# L09 — EXECUTION SUBSTRATE
### Where predicates run, what language they are written in, how we sandbox them, and how we seed faults to qualify them.

**Compiled 10 Aug 2026.** Lane brief: *"Where do the predicates actually RUN, in what language are they
written, and how do we mutate and qualify them?"*

**Warrant key used throughout:**
`VERIFIED-AT-SOURCE` = I opened the primary artifact (paper PDF, repo page, licence file, spec file, or
ran the code myself) · `SECONDARY` = a credible source describes it and I did not open the primary ·
`UNVERIFIED` = plausible, unchecked · `NOT-FOUND` = I looked and could not confirm.
`MEASURED-BY-ME` = computed today on the real artifact at
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/` with
`/Users/abishaikc/Gift/.venv/bin/python` (openpyxl) and `unzip`+`grep` on the raw OOXML.

**Coverage declaration for this lane.** ~40 web searches/fetches; 6 primary PDFs opened (2 fully read
page-by-page); 8 GitHub repo pages opened; 2 licence files read verbatim; 7 executions against the real
IFSCA FME workbook. **Not checked:** cel-cpp internals, Drools' current licence file, Nools' repo,
SpEL's current CVE history, VTL 2.2 reference manual body text, NVD's own record for CVE-2026-5752 (the
NVD page returned HTTP 502 twice — I fell back to a vendor vulnerability database and say so at the point
of use).

---

# PART 0 — THE RECOMMENDATION IN ONE PAGE

**Primary predicate language: CEL (Common Expression Language), evaluated by a Python host process,
over a flat typed `Cell`/`Field` fact table derived by L1 — with a mandatory three-slot predicate
envelope (`applicable` / `expr` / `witness`) that makes UNCHECKED a first-class evaluation outcome
rather than an exception.**

Why CEL and not the runners-up, compressed:

| Requirement from the brief | CEL | Python+GX/pandera | Rego | Z3 | Drools/ZEN |
|---|---|---|---|---|---|
| Guaranteed to terminate on model-written input | **yes, by language design** | no | yes | no (decidable fragments only) | engine-dependent |
| Safe to evaluate model-generated text without a container | **yes** | **no** | yes | no | no |
| Predicate is one auditable line a lawyer can read | **yes** | no (a function body) | partly | no | no (a graph/DRL) |
| Serialisable, content-addressable, diffable | **yes (it is a string)** | no (code) | yes | yes | yes |
| Mechanically mutable (we can perturb the AST) | **yes, small grammar** | yes but huge grammar | yes | yes | awkward |
| Coverage over the rule set is computable | **yes — field refs are extractable statically** | no (needs taint analysis) | partly | yes | partly |
| Can express all 17 decidable predicates | **13 of 17 natively; 4 need a host function** | 17 | 15 | 6 | 10 |

**Escape hatch (§A.8):** four of the 17 predicates need something CEL cannot do (live register lookup,
GSTIN check-digit, template-hash comparison, regulation-date arithmetic). These become **host functions**
— named, deterministic, individually versioned Python functions registered into the CEL environment,
each with its own test suite and its own mutation score. The predicate stays one readable CEL line;
the impurity is quarantined into a small, enumerable, separately-qualified set. **No predicate ever
contains model-generated Python.**

**Sandbox (Part B):** because of the above, **no generated Python survives**, and the sandbox question
mostly dissolves. What remains — the L1 parser eating a filer-supplied `.xlsx`, and the host-function
set — runs in a **gVisor-sandboxed container with no network, read-only rootfs, a `seccomp` profile and
a wall-clock kill**. Firecracker is over-engineered for a confused-model threat model and buys nothing
against the actual adversary, which is a malformed workbook, not an attacker.

**Fault seeding (Part C):** the brief's L4 test 1 is **mis-specified**. It says "mutation testing" and
cites mutmut/PIT/Stryker, which mutate *code*. What the brief needs is **fault seeding into the
artifact** — the data — and there is a directly-applicable primary literature the brief does not cite:
**Abraham & Erwig's spreadsheet mutation operators (IEEE TSE 35(1):94–108, 2009)**, whose 17 operators
are *exactly* a fault taxonomy for a financial reporting workbook, and whose measured result —
**3,512 of 7,500 mutants (46.8%) were "irreversible", i.e. produced no observable change** — is the
single most important number for how we compute kill rate.

---

# PART A — THE PREDICATE LANGUAGE

## A.0 — What the 17 decidable predicates actually demand

Before comparing languages, here is what the brief's §4.3 list requires, sorted by the capability it
needs. This is the requirements spec the language must meet, derived by reading each of the 17 against
the real workbook (MEASURED-BY-ME: cell references below are real and were read off the file today).

| # | Predicate (brief §4.3) | Capability class | Concrete anchor in the FME workbook |
|---|---|---|---|
| 1 | scheme-count identity | arithmetic over a range + string classification | `'1. Introduction'!D17 = SUM(D18:D20)`, `D18:D20` are COUNTIFs over `G54:G63` |
| 2 | investor row totals | row-wise sum identity | `'4. Investors'!N5 = SUM(C5:M5)`; `AA21 = SUM(C21,E21,…,Y21)` |
| 3 | portfolio row totals | row-wise sum identity | `'3. Portfolio'!O3 = SUM(C3:N3)` |
| 4 | every cross-sheet carry matches source | equality across two named fields | 195 formula strings carry a `!` reference (MEASURED-BY-ME) |
| 5 | Table 1.5 rows = declared count | count of non-empty rows vs a scalar | `B54:N63` vs `D17` |
| 6 | fee arithmetic | arithmetic with tolerance | Table 1.4, `D42:D44` |
| 7 | scheme auth date ≤ period end | date comparison | `E54:E63` vs `'1. Introduction'!D2/D3` |
| 8 | FME reg date ≤ scheme auth date | date comparison | `D11` vs `E54:E63` |
| 9 | registration number resolves in live register | **external lookup** | `D8` |
| 10 | scheme number resolves | **external lookup** | `C54:C63` |
| 11 | GSTIN check digit | **string algorithm (mod-36 Luhn variant)** | `D14`, carried to `D46` |
| 12 | percentages sum to 100 | arithmetic with tolerance | portfolio/investor share tables |
| 13 | dropdown ∈ vocabulary | set membership | see A.0.1 — **only 3 of 35 validations are list-type** |
| 14 | email / phone format | regex | `D27,D30,D33` / `D28,D31,D34` |
| 15 | **Principal Officer ≠ Compliance Officer** | string inequality | `D26 ≠ D29` |
| 16 | template version = current published | **content-hash comparison against L0** | workbook hash |
| 17 | latest valuation date vs NAV frequency owed under regs 27(1)/39(1)/51(1) | **date arithmetic conditioned on a regulation-derived interval, with provisos** | Table 1.5 `H`/`I` + scheme type |

**Classes:** arithmetic/comparison (1,2,3,4,5,6,7,8,12,15) = 10; regex (14) = 1; set membership (13) = 1;
external lookup (9,10) = 2; string algorithm (11) = 1; hash comparison (16) = 1; regulation-conditioned
date arithmetic (17) = 1. **13 of 17 are pure expression evaluation over a fact table.** Four are not.

### A.0.1 — Two measurements I ran today that change what a predicate must do

**(a) The published template's own scheme-count formula is defective, and it will produce a false
failure on a correctly-filled workbook.** (MEASURED-BY-ME, reproducible.)

`'1. Introduction'!D17`, labelled *"Total No. of Schemes of the FME authorised by IFSCA"*, is
`=SUM(D18:D20)`, and:

```
D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")
D19 = COUNTIF(G54:G63, "*Restricted*")
D20 = COUNTIF(G54:G63,"*Retail*") + COUNTIF(G54:G63,"*Exchange Traded Fund*")
```

The controlled vocabulary that column `G` draws from is `Dropdown!F3:F11`, and it has **9** terms. I
applied the three COUNTIF patterns to all 9:

```
Venture Capital Scheme            -> D18
Angel Scheme                      -> D18
Restricted Scheme (Category I)    -> D19
Restricted Scheme (Category II)   -> D19
Restricted Scheme (Category III)  -> D19
Retail Scheme                     -> D20
Exchange Traded Fund              -> D20
Special Situation Fund            -> NOT COUNTED BY ANY COUNTIF
Family Investment Fund            -> NOT COUNTED BY ANY COUNTIF
```

**7 of 9 vocabulary terms are counted; 2 are not.** So for any FME running a Special Situation Fund or a
Family Investment Fund, `D17` **undercounts the total number of authorised schemes**, and predicate #5
("Table 1.5 rows = declared count") fires on a correct filing. This is not hypothetical: the workbook's
own guidance note `B114` says *"For Family Investment Funds, information may be submitted in a single row
under each table"* — FIFs are expected filers.

**Why this matters more than the bug itself:** the brief's L3 novelty claim is that *"statutory text plus
the template's own 294 native formulas"* is **"an authoritative criterion source rather than an inferred
one"** (ARCHITECTURE.md, L3). That claim is now **QUALIFIED at source**: the template's native formulas
are an *available* criterion source, not an *authoritative* one. A predicate mined from `D17` inherits
`D17`'s defect. The L4 gate is not an optimisation — it is the only thing standing between the template's
bugs and our verdict.

**(b) The workbook ships 15 controlled vocabularies and enforces 1, and the vocabulary sheet is the only
unprotected sheet.** (MEASURED-BY-ME.)

- Sheet protection: `1. Introduction, 2. Summary, 3. Portfolio, 4. Investors, 5. PMS, 6. Complaints,
  7. AML-CFT, 8. Compliance Status, 9. Compliance Report` → `protection.sheet = True`. **`Dropdown` →
  `False`.**
- 35 data validations total. **3 are list-type**: `'1. Introduction'!N54:N63` (`=Choicelist`) and
  `'8. Compliance Status'!C10` and `C11` (`=IF(C5="No",Choicelist,YesNolist)`). This independently
  reproduces the brief's "35 data validations, only 3 list-type" — CONFIRMED.
- Defined names: `Choicelist = Dropdown!$H$3:$H$5`, `YesNolist = Dropdown!$H$3:$H$4`,
  `YesNoNA = Dropdown!$H$3:$H$5`, `NA = Dropdown!$H$5`. **All four point at column H only** — the
  Yes/No/Not-Applicable list.
- The `Dropdown` sheet actually carries **15 vocabularies** in columns `D`–`R`: reporting quarter (4
  terms), financial year (4), scheme type (9), legal structure of FME (5), Yes/No/NA (3), open/close (2),
  FME category (3), legal structure of scheme (4), PMS type (3), instrument class (13), status (3),
  manual/automated (2), system/manual (2), complaint bands (4), registration status (3).

**Consequence for the language choice: 14 of the 15 vocabularies exist in the file but are enforced by
nothing, and the file that defines them is the one sheet a filer may edit.** So predicate #13 (`dropdown ∈
vocabulary`) cannot be evaluated against the *submitted* workbook's Dropdown sheet — it must be evaluated
against the **L0-pinned blank template's** Dropdown sheet, content-addressed. That is a hard requirement
on the fact model, not on the language: **every predicate must be able to reference two documents — the
filing and the pinned template — and the language must make it syntactically obvious which one it is
reading.**

### A.0.2 — A correction to the brief's formula census

The brief states **"294 formulas"** in the FME workbook, of which **"181 (62%) pure cross-sheet
carry-forward"** and **"38 of 294 (13%) express a checkable relationship."**

I re-ran this today. (MEASURED-BY-ME; commands below are exact.)

```
$ unzip -q Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx
$ cat xl/worksheets/*.xml | grep -o '<f[ >/]' | wc -l          # 505
$ cat xl/worksheets/*.xml | grep -o '<f[^>]*/>' | wc -l        # 211
```

- **505** `<f>` elements exist across the 10 worksheets → **505 cells contain a formula**.
- **211** of them are *shared-formula followers*, stored in OOXML as `<f t="shared" si="N"/>` — an
  element with **no text**. They are real formula cells; Excel materialises them from the group master.
- **505 − 211 = 294.** The brief's 294 is exactly the count of formula elements that carry **text**.

**The brief's 294 is the number of distinct formula *strings*. The number of formula-bearing *cells* is
505.** The undercount is **211 / 505 = 41.8%**.

This is the same failure family as the brief's own §4.4 item 2 (`<f[ >][^>]*>` could not match
`<f>SUM(...)</f>`): a confident, well-formed number produced by a deterministic program from a wrong
assumption about XML shape. **It is a third silent false negative, and it is the operator's own.** I hit
the same class of bug myself mid-analysis (a regex whose `||` alternation swallowed the self-closing
stubs and, by coincidence, returned exactly 294) — which is itself the point.

Class census over all **505** formula cells, classifier stated (openpyxl expands shared formulas):

| Class | Cells | % of 505 | Checks anything? |
|---|---:|---:|---|
| Pure carry — `=X12` or `='Sheet'!X12` | 223 | 44.2% | **No — copies a value** |
| `SUM(...)` row/column identity | 135 | 26.7% | **Yes** |
| `IFERROR(...)` wrapper | 129 | 25.5% | No |
| `IF(...)` conditional carry | 14 | 2.8% | Partly |
| `COUNTIF(...)` tally | 3 | 0.6% | **Yes** |
| array formula | 1 | 0.2% | No |

**Checkable relations: 138 of 505 = 27.3%** (not 38 of 294 = 13%). Cross-sheet formula strings: **195 of
294 = 66.3%** — this figure in the brief is **CONFIRMED exactly.**

The correction runs *in the design's favour*: the harvestable relation set is 3.6× larger than the brief
claims. But the rhetorical line "*the workbook moves numbers between sheets and that motion is counted as
validation*" survives intact — 44.2% still copy a value.

---

## A.1 — Plain Python plus a data-validation framework

| Project | Licence | Activity / scale | Declarative & serialisable? | Per-check result rich enough for PASS/FAIL/**UNCHECKED(reason)**? |
|---|---|---|---|---|
| **Great Expectations (GX Core)** | Apache-2.0 (SECONDARY) | dominant OSS DQ framework | Expectation Suites are JSON-serialisable | **No — and it fails in the exact direction that kills us.** See below. |
| **pandera** | **MIT** (VERIFIED-AT-SOURCE: github.com/unionai-oss/pandera, 4.4k★, 430 forks) | Union.ai project | `DataFrameSchema` / `DataFrameModel`; README does *not* document YAML/JSON round-trip (the repo page I opened does not mention it) | Lazy validation returns a `SchemaErrors` with a `failure_cases` frame — rich on failures, silent on non-evaluation |
| **Soda Core (SodaCL)** | **Elastic License 2.0** (VERIFIED-AT-SOURCE — I read `LICENSE` on `main`) | active, commercial | SodaCL is YAML — genuinely declarative and the nicest syntax in this table | **DISQUALIFIED ON LICENCE.** See below. |
| **dbt tests** | Apache-2.0 (SECONDARY) | very large | a test is a `.sql` file; generic tests are Jinja macros | **No.** A dbt test is "a SELECT that returns failing rows; zero rows = pass" (SECONDARY, docs.getdbt.com). Two-valued by construction; also requires a warehouse |
| **Deequ / PyDeequ** | **Apache-2.0** (SECONDARY) | AWS Labs; VLDB 2018 lineage | `VerificationSuite` + `Check` objects; constraint *suggestion* is a real differentiator | `VerificationResult` carries per-constraint status — the richest status model in this row, but Spark-shaped |
| **Frictionless (frictionless-py)** | **MIT** (SECONDARY) | Open Knowledge | Table Schema is a JSON standard — best serialisation story here | Report has per-error `type`/`note`; no unchecked state |
| **Cerberus** | **ISC** (SECONDARY) | small, stable | schema is a plain dict | dict-of-errors; no unchecked state |
| **Pointblank (Python)** | MIT, Posit (SECONDARY) | ~50 releases in ~1 yr (SECONDARY) | Python fluent API | **Closest in the ecosystem.** Its report has PASS/FAIL counts, WARNING/ERROR/CRITICAL thresholds, **and an `EVAL` column** flagging whether the step evaluated at all (VERIFIED-AT-SOURCE: I read the user guide's rendered report description) |

### The Great Expectations disqualifier — and it is the most important negative result in this lane

GX's `ExpectationValidationResult` carries `exception_info`, a dict with `raised_exception`,
`exception_traceback`, `exception_message` (SECONDARY, docs.greatexpectations.io 0.18 reference). Every
Expectation takes `catch_exceptions`; the docs state that when it is true, *"execution will not fail if
the Expectation encounters an error. Instead, it will return `success = False`"* (SECONDARY, same source).

**A GX expectation that could not be evaluated returns `success = False` — the same value it returns when
it evaluated and the data was wrong.** For an ordinary data-quality tool that is a defensible
conservative default. For *this* product it is fatal: the entire headline output is a **coverage
fraction**, and coverage is `checked / in-scope`. A framework that folds *could-not-check* into *failed*
destroys the denominator. It also violates the brief's own weakest-input provenance rule (ARCHITECTURE.md
L5) at the substrate level.

And at the verbosity levels GX documents (BOOLEAN_ONLY / BASIC / SUMMARY / COMPLETE — VERIFIED-AT-SOURCE,
I read the `result_format` reference), the result fields are `element_count`, `unexpected_count`,
`unexpected_percent`, `unexpected_percent_nonmissing`, `missing_count`, `missing_percent`,
`partial_unexpected_list`, `partial_unexpected_counts`, `partial_unexpected_index_list`,
`unexpected_list`, `unexpected_index_list`, `unexpected_index_query`, `observed_value`. **There is no
field for "not applicable", "out of scope", or "no oracle exists."** The vocabulary the brief's L5
requires — *no oracle exists · requires counterparty data · requires judgment · source unreadable · rule
ambiguous · predicate not yet synthesised* — has no home in any of these frameworks.

> **Where this fits (L0–L7):** none of these frameworks can be L5. They can be *called from* L5 as
> host functions for bulk column-shaped checks (pandera is the best fit: MIT, dataframe-native,
> `failure_cases` gives row-level provenance for free).
> **Where it stops:** the moment a verdict needs a third value. The brief's line *"Great Expectations /
> pandera / Soda Core / dbt tests / Deequ — L5 substrate — do not rebuild"* (§6.2) should be **revised**:
> do not rebuild the *check library*; **you must build the verdict model**, because none of them has one.

### The Soda Core disqualifier

I read `https://raw.githubusercontent.com/sodadata/soda-core/main/LICENSE`. It is the **Elastic License
2.0**, and it contains verbatim:

> "You may not provide the software to third parties as a hosted or managed service, where the service
> provides users with access to any substantial set of the features or functionality of the software."

Our product *is* a hosted service whose substantial functionality is data validation. **Soda Core is
unusable as our engine**, regardless of its merits, and the brief's §6.2 row listing it alongside Apache-2
projects should be corrected. (SodaCL's YAML syntax remains worth reading as a design reference — reading
a licence-incompatible project for ideas is fine; linking it is not.)

---

## A.2 — Restricted, non-Turing-complete expression languages

### CEL — Common Expression Language

**Primary sources opened:** `github.com/google/cel-spec/blob/master/doc/langdef.md` (and the raw file),
`github.com/google/cel-go`, `cel.dev`.

VERIFIED-AT-SOURCE, quoted from the language definition:

> **"terminating: CEL programs cannot loop forever"**
> **"side-effect-free: a CEL program only computes an output from its inputs"**

Types: `int, uint, double, bool, string, bytes, list, map, null_type`, protobuf message types, and
`type`. **No user-defined functions. No loops.** The reserved-keyword list explicitly includes `for`,
`function`, `loop`, `while`, `break`, `continue` — they are reserved *and unavailable*.

Six macros: `has()`, `all()`, `exists()`, `exists_one()`, `map()`, `filter()`. The spec states:

> "The macros other than `has()` are the only avenue for exponential behavior. This can be curtailed by
> the implementation allowing applications to set limits on the recursion or chaining of macros."

cel-go (VERIFIED-AT-SOURCE, repo page): **Apache-2.0, 3.1k★, 307 forks**; the repo banner states *"On
June 16, 2026, this repository will move to github.com/cel-expr/cel-go"* — the canonical org is now
`cel-expr`, not `google`. Its README: *"a non-Turing complete language designed for simplicity, speed,
safety, and portability"* and *"CEL evaluates linearly with respect to the size of the expression and the
input being evaluated when macros are disabled."*

**Python implementations — and there is a naming trap.** Two different projects both live at a path
called `cel-python`:

| | `cloud-custodian/cel-python` | `cel-expr/cel-python` |
|---|---|---|
| PyPI name | `cel-python` (module `celpy`) | `cel-expr-python` |
| Implementation | **pure Python** | **wrapper over the official CEL C++** |
| Licence | **Apache-2.0** (VERIFIED-AT-SOURCE) | **Apache-2.0** (VERIFIED-AT-SOURCE) |
| Stars / forks | **171 / 40** (VERIFIED-AT-SOURCE) | **76 / 6, 81 commits** (VERIFIED-AT-SOURCE) |
| Released | long-standing, Cloud Custodian project | **announced 3 Mar 2026** by Google Open Source (VERIFIED-AT-SOURCE: opensource.googleblog.com); repo launched **read-only**, contributions planned later |
| Conformance claim | none stated on the repo page I opened (NOT-FOUND) | Google states they wrapped C++ *"to ensure maximum consistency with CEL semantics"*, and *"new features and optimizations implemented in CEL C++ will automatically and immediately become available"* |

**The precedent that settles the "is this a real engineering choice" question: Kubernetes.**
ValidatingAdmissionPolicy was **alpha in v1.26, beta in v1.28, and GA in v1.30** (SECONDARY,
kubernetes.io blog "Kubernetes 1.30: Validating Admission Policy Is Generally Available", 24 Apr 2024).
It is *"a declarative, in-process alternative to validating admission webhooks"* using CEL. That is
precisely our shape: **model-free policy over structured data, evaluated in-process, no container per
check.**

Kubernetes also demonstrates the two resource controls we will need. VERIFIED-AT-SOURCE from the
Kubernetes website source markdown:

> "All CEL expressions evaluated by Kubernetes are constrained by a runtime cost budget. The runtime cost
> budget is an estimate of actual CPU utilization computed by incrementing a cost unit counter while
> interpreting a CEL expression." … "If the sum total of the cost of expressions exceed the budget,
> execution of the expressions will be halted, and an error will result."

and, for the static gate:

> "the API server may also check if worst case estimated running time of CEL expressions would be
> prohibitively expensive to execute" … "the API server prevent the CEL expression from being written to
> API resources by rejecting create or update operations."

**The specific numeric constants (the widely-repeated `10,000,000` cost budget) are NOT-FOUND in the
Kubernetes documentation page** — the docs describe the mechanism, not the number. The constants live in
the Kubernetes source, which I did not open. Do not quote a figure.

**The one CEL hazard that must be designed around — and it is serious for us.** VERIFIED-AT-SOURCE,
from the language definition's runtime-error section:

> "In general, when a runtime error is produced, expression evaluation is terminated; exceptions to this
> rule are discussed in Logical Operators and Macros."

> "if any of their operands uniquely determines the result (false for `&&` and true for `||`) the other
> operand may or may not be evaluated, and if that evaluation produces a runtime error, **it will be
> ignored**."

So `true || <error>` evaluates to `true`. **A predicate written as `a || b` can return PASS while
silently swallowing an operand that could not be evaluated at all.** In a system whose product is "we
declare what we did not check", that is the exact defect we exist to prevent — CEL will manufacture a
clean verdict from an unreadable input. Mitigation is in §A.6.4 and it is mandatory, not optional.

### Rego / OPA

Apache-2.0 core; **CNCF graduated project** (SECONDARY — devops.com / openpolicyagent.org via search).
Rego is Datalog-inspired and *"isn't a Turing-complete language"* (SECONDARY — Aserto/OPA docs via
search; I did **not** open the OPA language-reference page and therefore do not claim this
VERIFIED-AT-SOURCE).

**Verdict: strong runner-up, rejected on readability and on host-language fit.** Rego's partial-evaluation
and "undefined" semantics are actually *closer* to what we want than CEL's booleans — an undefined rule
body simply produces no result, which is nearly UNCHECKED for free. But (a) Rego's default-deny/undefined
model is famously confusing to read, and the brief's UX commitment is a **predicate library an auditor
inspects** (ARCHITECTURE.md Screen 3) — a rule an auditor cannot read has negative value here; (b) the
mature implementation is Go, and our stack is Python (openpyxl/lxml); embedding OPA means a subprocess or
a WASM bundle per evaluation. Reconsider if the system ever moves to Go.

### Starlark

Deterministic and hermetic; **no recursion; loops iterate only over finite sequences and are therefore
guaranteed to terminate**; no file, network or clock access (SECONDARY — bazel.build "Starlark Language"
docs and `bazelbuild/starlark` spec via search; I did not open `spec.md` itself).

**Verdict: rejected.** Starlark is a *configuration* language with statements, assignment and functions.
It is strictly more powerful than we need, its programs are multi-line and therefore harder to mutate
mechanically and harder to render in a predicate library, and — decisively — a Starlark predicate has
*local state*, which means "which fields does this predicate read?" stops being a static question. We
need that question to stay static, because **coverage over the rule set is computed from it** (§A.6.5).

### JSONLogic

*"We never eval(). Rules only have read access to data you provide, and no write access to anything."*
(SECONDARY — jsonlogic.com via search.) Rules are JSON, so serialisation and mutation are trivial.

**Verdict: rejected on expressiveness and ecosystem.** No type system, no date arithmetic, no regex in the
core spec, and the reference implementation is JS. It cannot express predicate #7, #8 or #17 without
extension. Its *shape* — a rule is a JSON tree — is worth stealing for the envelope, and we do (§A.6.1).

### JMESPath

A **query** language for extracting from JSON, not a predicate language: it has no boolean operators of
the kind we need and no arithmetic. **Verdict: rejected as the predicate language; adopt as the
*provenance-pointer* language** — a JMESPath expression is a clean, portable way to name the exact fact a
predicate read, which L5 needs for the "expands to both cells" UX.

### SpEL (Spring Expression Language)

**Verdict: rejected outright, on security.** SpEL evaluates against a full JVM object graph and supports
type references and constructor/method invocation (`T(java.lang.Runtime)`); SpEL injection is a
well-known RCE class. It is the opposite of a restricted language: it is a *scripting hook* into a
runtime. Also JVM-only. (I did not enumerate current CVEs — UNVERIFIED on specifics, but the design
property alone disqualifies it.)

---

## A.3 — Formal: SMT and Datalog

### Z3 / SMT — **adopt, but for L4, not L5**

**Licence: MIT** (SECONDARY — `Z3Prover/z3`; consistent across sources).

Z3 is the wrong tool for *evaluating* a predicate against a filing (that is a one-shot arithmetic
evaluation; an SMT solver is absurd overkill and introduces a non-terminating tool into a terminating
pipeline). It is the **right tool for L4 test 2**, "can a degenerate artifact satisfy it?", which is
*literally a satisfiability question*:

- **Trivially-true detection:** the predicate is degenerate iff `¬P` is UNSAT over the field domains.
  If Z3 cannot find *any* assignment of the referenced fields that makes the predicate false, the
  predicate never fires and must be rejected.
- **Always-flag detection:** symmetric — `P` UNSAT ⇒ the predicate always fails ⇒ it is the
  flag-everything baseline in disguise, which is precisely the failure the brief's contract-discrepancy
  result exhibits (§3.1: best model F1 65.4 vs a flag-everything ≈66.2).
- **Non-degeneracy witness:** Z3 returns a *model* — a concrete counterexample workbook. That witness is
  a directly usable seeded fault (Part C), and it goes in the predicate library entry as evidence.
- **Redundancy / subsumption:** `P₁ ∧ ¬P₂` UNSAT ⇒ P₁ implies P₂ ⇒ P₂ adds no coverage. This is how we
  keep the registry minimal without SPADE's LLM loop.

CEL's arithmetic-comparison fragment translates to SMT-LIB almost one-to-one (linear integer/real
arithmetic + booleans + a string theory Z3 supports), so this is cheap.

> **Where this fits:** L4 tests 2 and 3, plus registry hygiene.
> **Where it stops:** the moment a predicate calls a host function (register lookup, GSTIN check digit).
> Those are uninterpreted functions to Z3, so degeneracy for them must be established empirically by
> fault seeding, not proof. Also: string constraints in Z3 are decidable only for fragments; **assume
> `unknown` is a possible answer and treat it as UNCHECKED, never as "non-degenerate."**

### Soufflé / Datalog

**Licence: Universal Permissive License (UPL) 1.0** (SECONDARY — `souffle-lang/souffle` LICENSE).
Terminating by construction on finite domains, and excellent for the *relational* half of the problem
(does this registration number resolve? which schemes appear in table X but not table Y?).

**Verdict: not the primary language, but keep it in view for L6.** Metamorphic relations over a filing —
"the set of schemes in Table 1.5 equals the set in Table 2.1 equals the set in Table 3.1" — are naturally
Datalog. Today that is a `SUM`/set-equality one-liner in CEL. Revisit if cross-table relations multiply.
**Where it stops:** compiled Soufflé is a C++ binary; that is a second toolchain and a second sandbox for
a problem we can currently express in one line.

---

## A.4 — Rule engines

| Engine | Licence | Shape | Verdict |
|---|---|---|---|
| **Drools** | Apache-2.0 (SECONDARY, not verified at the LICENSE file) | DRL + RETE, JVM | **Reject.** RETE's whole value is efficient incremental matching over a large, changing working memory. Our working memory is ~6,757 cells and is evaluated once. We would pay a JVM, a DSL, and a forward-chaining semantics (rules that fire rules) that destroys the "each predicate is independently qualified and independently scored" property the L4 gate depends on. |
| **GoRules ZEN** | **MIT** (SECONDARY) | Rust core, JSON Decision Model (JDM) graphs, bindings for Node/Python/Go/Java/C#/Kotlin/Swift | **Reject as the language; note as a UI precedent.** JDM's decision *tables* are a genuinely good rendering of a rule set for non-programmers, which is relevant to the brief's Screen 3. But a JDM graph is a decision *pipeline*, not an assertion, and its expression layer is another embedded expression language — so we would inherit a dependency to get a worse CEL. |
| **json-rules-engine** | (NOT-FOUND — did not open the repo) | JS, JSON conditions | **Reject.** Node-only, and it is JSONLogic with more ceremony. |
| **Nools** | (NOT-FOUND — did not open the repo) | JS RETE | **Reject.** Same objection as Drools without the maturity. I found no evidence of current maintenance and did not look hard; treat as UNVERIFIED. |

**The general objection to all four:** a rule engine's core competence is *conflict resolution and
chaining* — deciding which of many applicable rules to fire, and letting rules produce facts that trigger
other rules. Our architecture forbids exactly that. Every predicate must be independently scored (mutation
score, FFR) and independently attributable in the report; chaining makes both incoherent. **We do not have
a rules-engine problem. We have an assertion-evaluation problem.**

---

## A.5 — VTL (Validation and Transformation Language)

**Status: real, standardised, and the wrong altitude for us.** (SECONDARY throughout — I read the SDMX
landing pages and repo descriptions, not the reference manual body.)

- VTL is maintained by the **SDMX Technical Working Group's VTL Task Force**; **VTL 2.2 documentation was
  published in mark-up form (Dec 2024) at `sdmx-twg.github.io/vtl/2.2`**; the spec repo is
  `github.com/sdmx-twg/vtl`.
- Implementations: `statisticsnorway/java-vtl` and `hadrienk/java-vtl` (both **VTL 1.1 draft**, not 2.x);
  the **ESCB VTL Engine and Editor** was published as open source **under the EUPL**, a Java library
  wrapped by an R package.

**Verdict for L09: REJECT as the predicate language, KEEP as a vocabulary source.** VTL is designed for
*statistical dataset* algebra — datasets with identifier/measure/attribute components, joins, aggregations
across dimensions. Our artifact is a 10-sheet workbook with merged headers and 505 formula cells, not a
tidy multidimensional cube; getting it into VTL's data model *is* the hard part, and VTL does not help
with it. The live Java implementations are still on the **1.1 draft**, five-plus years behind the
published spec, which is a maintenance signal.

**But its `check_datapoint` / `check_hierarchy` operator vocabulary is worth mining** — European
statistical authorities have already enumerated the shapes of "a validation rule over a regulatory
return", and reinventing that taxonomy would be waste. **Where it stops:** no Python engine of any
maturity that I found; adopting VTL means adopting the JVM. (Cross-reference: whatever lane L04 concluded
about VTL's reality — this lane's independent finding is *the standard is real, the tooling is
JVM-and-behind*.)

---

## A.6 — THE RECOMMENDED DESIGN

### A.6.1 The predicate envelope

A predicate is **not** a CEL expression. It is a small, signed, content-addressed record **containing**
CEL expressions. The envelope is what makes UNCHECKED a first-class outcome, and it is where all the
qualification metadata lives.

```yaml
# predicate/P-0041.yaml   — content-addressed by sha256 of the canonical serialisation
id:            P-0041
version:       3
template:      sha256:8f2a…            # the pinned blank template this predicate is bound to
schema_keys:   ["intro.tbl15.row[*].scheme_type", "vocab.scheme_type"]   # DECLARED, and machine-checked
                                                                        # against the CEL AST at admission
clause:                                # what it claims to implement
  instrument:  "IFSCA (Fund Management) Regulations, 2025 (as amended to 30 Jan 2026)"
  locator:     "Reporting Format FME v02012026, Table 1.5 col G"
  quote:       "Type of Scheme"
rationale:     "Every declared scheme type must be a term the published template offers."

applicable: >                          # CEL -> bool.  false  => UNCHECKED(reason_if_inapplicable)
  size(filing.intro.tbl15.rows) > 0
expr: >                                # CEL -> bool.  true => PASS, false => FAIL
  filing.intro.tbl15.rows.all(r,
    r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)
witness: >                             # CEL -> list.  what to show the user on FAIL
  filing.intro.tbl15.rows.filter(r,
    r.scheme_type != "" && !(r.scheme_type in template.vocab.scheme_type))
             .map(r, r.__cell__)

reason_if_inapplicable: "predicate not applicable: no schemes declared"
severity_hint: "vocabulary"            # advisory only; never affects PASS/FAIL

qualification:                         # written by L4. NOT hand-editable. Absent => not admitted.
  admitted:            "2026-08-14"
  kill_rate:           {killed: 41, observable_mutants: 44, rate: 0.932}
  degeneracy:          {method: "z3", verdict: "non-degenerate", witness: "w/P-0041-neg.json"}
  ffr:                 {fired: 2, clean_corpus_n: 96, rate: 0.021, corpus: "SYNTHETIC-TEAM-FILLED"}
  interaction:         {conditioned_on: ["P-0007"], marginal_ffr: 0.010}
```

Three properties this buys, none of which any framework in §A.1 has:

1. **UNCHECKED is produced by evaluation, not by exception.** `applicable` is a *predicate about
   applicability*, evaluated first, with its own semantics. A predicate that does not apply is not a
   failure and is not a pass — it is removed from the coverage denominator with a stated reason.
2. **`schema_keys` is declared and then machine-checked.** At admission, the harness walks the CEL AST,
   extracts every field selection, and **rejects the predicate if the AST reads a key not declared, or
   declares a key it does not read.** This is what makes coverage computable (§A.6.5) — and it is a
   static check only because the language has no variables and no loops.
3. **`qualification` is a required block.** A predicate without it does not load. The brief's *"a check
   whose error rate is unknown is not admitted"* becomes a schema constraint, not a discipline.

### A.6.2 The fact model the CEL environment sees

L1 emits two content-addressed documents; CEL binds exactly two top-level names, `filing` and `template`.
Nothing else is in scope — no clock, no network, no filesystem.

```
filing.<sheet_key>.<table_key>.rows[i].<field_key>   -> typed scalar
filing.<sheet_key>.<field_key>                       -> typed scalar
filing.<...>.__cell__                                -> "3. Portfolio!O7"   (provenance pointer)
filing.__hash__                                      -> sha256 of the submitted workbook
template.vocab.<vocab_key>                           -> list<string>        (from the PINNED blank)
template.__hash__                                    -> sha256 of the pinned blank template
template.formula.<cell>                              -> string              (the native formula text)
```

Two rules that follow from §A.0.1(b) and are non-negotiable:

- **Vocabularies always resolve against `template`, never `filing`.** The `Dropdown` sheet is the only
  unprotected sheet in the workbook; reading the vocabulary from the submission would let a filer define
  their own legality.
- **Every leaf carries `__cell__`.** The report must expand a failure to the actual cells (Screen 2), and
  the weakest-input provenance rule needs a pointer per input, not per predicate.

### A.6.3 Grammar sketch — the admitted CEL subset

We do not admit all of CEL. The admitted grammar is a profile, enforced by an AST walker at admission
time. This is what makes both mutation and coverage tractable.

```ebnf
predicate   ::= disjunction
disjunction ::= conjunction ( "||" conjunction )*
conjunction ::= negation    ( "&&" negation    )*
negation    ::= [ "!" ] atom
atom        ::= comparison | membership | quantifier | call | "(" disjunction ")"

comparison  ::= arith relop arith
relop       ::= "==" | "!=" | "<" | "<=" | ">" | ">="
arith       ::= term ( ("+"|"-") term )*
term        ::= factor ( ("*"|"/") factor )*
factor      ::= number | string | selector | agg | call | "(" arith ")"

membership  ::= arith "in" ( selector | listlit )
quantifier  ::= selector "." ( "all" | "exists" | "exists_one" ) "(" ident "," disjunction ")"
agg         ::= "sum" "(" selector "." "map" "(" ident "," arith ")" ")"
              | "size" "(" selector ")"
selector    ::= root ( "." ident | "[" int "]" )+
root        ::= "filing" | "template"
call        ::= hostfn "(" arith { "," arith } ")"        (* §A.8 — closed, versioned set *)
hostfn      ::= "reg_resolves" | "gstin_valid" | "matches" | "date" | "months_between"
              | "abs" | "round"
```

**Deliberately excluded from the profile:** `map()` used for anything but the argument of `sum()`,
nested comprehensions, `filter()` outside `witness`, protobuf messages, `bytes`, `uint`, `type()`,
`dyn()`. Nested comprehensions are the *only* route to exponential blow-up the CEL spec names, and
excluding them turns the spec's "can be curtailed by the implementation" from a promise into a fact.

### A.6.4 The evaluation contract — five rules, and rule 3 exists only because of CEL's error absorption

For each predicate `P` and each filing `F`:

```
1.  Evaluate P.applicable.
      error            -> UNCHECKED("source unreadable")            [not FAIL]
      false            -> UNCHECKED(P.reason_if_inapplicable)       [not PASS]
      true             -> continue

2.  PRE-FLIGHT: for every key k in P.schema_keys, test presence and type against the fact model
    BEFORE evaluating P.expr.  Any k absent or mistyped -> UNCHECKED("source unreadable: <k>").
    This is the mitigation for CEL's documented error absorption:
      the spec states that for || and && "if that evaluation produces a runtime error, it will be
      ignored."  Left unguarded, `true || <error>` yields PASS from an unreadable input.
      Pre-flight makes the guard structural rather than dependent on how the predicate was written.

3.  Evaluate P.expr under a cost budget and a wall-clock kill.
      budget exceeded  -> UNCHECKED("predicate exceeded evaluation budget")   [never FAIL]
      runtime error    -> UNCHECKED("source unreadable")                      [never FAIL]
      false            -> FAIL, and evaluate P.witness for the cell list
      true             -> PASS

4.  Provenance composes by weakest input: the verdict's warrant is min() over the warrants of every
    fact the AST read.  Because schema_keys is machine-checked against the AST (§A.6.1), this set is
    exact and not an estimate.

5.  A predicate whose qualification block is absent, or whose `template` hash does not equal the
    pinned template hash for this filing, is NOT EVALUATED and reports
    UNCHECKED("predicate not yet synthesised" | "template version mismatch").
```

**Rule 3 is the whole product in four lines.** Everywhere a conventional validation framework would
convert doubt into a failure (GX: `success = False`) or into silence, this converts it into a *counted,
reasoned, reported* UNCHECKED.

### A.6.5 Coverage over the rule set — computable, and this is why the language had to be restricted

Because CEL has no assignment, no loops and no user-defined functions, the set of fields a predicate
reads is **statically extractable from its AST**. Therefore:

```
in_scope(F)   = { field keys L1 induced from the pinned template that F populates or is required to }
covered(F)    = ⋃ { P.schema_keys : P admitted, P evaluated to PASS or FAIL on F }
coverage(F)   = |covered(F) ∩ in_scope(F)| / |in_scope(F)|
unchecked(F)  = in_scope(F) \ covered(F),  each carrying a reason from the closed vocabulary
```

This is the number on Screen 2. **It cannot be computed if the predicate language has variables**, which
is the strongest single argument against Python, Starlark and Drools and the reason this lane's answer is
"restricted language" rather than "sandboxed Python". The brief's coverage meter is not a UI feature; it
is a *language requirement* that propagates all the way down.

### A.6.6 Worked encodings — 6 of the 17 decidable predicates

All cell references below were read off the real workbook today (MEASURED-BY-ME).

---

**P-01 — scheme-count identity** (brief predicate #1). *And note what the encoding forces us to admit.*

```cel
applicable: has(filing.intro.tbl12.total_schemes)
expr:       filing.intro.tbl12.total_schemes == size(filing.intro.tbl15.rows.filter(r, r.auth_no != "NA" && r.auth_no != ""))
witness:    ["1. Introduction!D17"]
```

Note what this deliberately does **not** do: it does not reproduce the template's
`SUM(COUNTIF(...)+COUNTIF(...))`. If we mined the predicate from the native formula — the brief's L3
plan — we would encode the template's bug (§A.0.1(a)) and the predicate would pass on a workbook that is
wrong, and fail on a workbook that is right. **The correct predicate contradicts the template's own
formula, and a second predicate must record that contradiction:**

```cel
# P-02  — template-defect detector, admitted as a permanent FAIL against the template, not the filer
applicable: true
expr:       template.vocab.scheme_type.all(v,
              v.matches("(?i).*(angel|venture|restricted|retail|exchange traded fund).*"))
            # evaluates FALSE on the published v02012026 template:
            # "Special Situation Fund" and "Family Investment Fund" match nothing.
```

This is the single best demo artifact in the whole build: **a predicate that fails the regulator's own
published template, deterministically, in one line, with the two offending vocabulary terms as the
witness.**

---

**P-03 — portfolio row totals** (brief predicate #3). Real cells: `'3. Portfolio'!O3 = SUM(C3:N3)`.

```cel
applicable: size(filing.portfolio.tbl31.rows) > 0
expr:       filing.portfolio.tbl31.rows.all(r,
              abs(r.total_portfolio_value
                  - (r.equity_listed + r.equity_unlisted + r.debt_listed + r.debt_unlisted
                     + r.schemes_ifsc + r.schemes_india + r.schemes_foreign + r.llp_interest
                     + r.physical_assets + r.cash_equivalents + r.derivatives_paid + r.other))
              <= 0.005)                       # USD Million reported to 2dp -> half-ulp tolerance
witness:    filing.portfolio.tbl31.rows.filter(r, abs(...) > 0.005).map(r, r.__cell__)
```

The tolerance is **declared in the predicate and versioned with it**, which is what makes the brief's
§3.2 finding operational: *"Allow rounding tolerance → 21-point recall loss is exactly the price of the FP
suppression."* The tolerance is now a measured parameter with its own FFR, not a hidden constant. Two
predicates differing only in tolerance are two registry entries with two error rates, and the library
shows both.

---

**P-04 — cross-sheet carry integrity** (brief predicate #4). This is the highest-volume predicate class:
**223 of 505 formula cells are pure carries** and **195 formula strings reference another sheet**
(MEASURED-BY-ME). Rather than one predicate per carry, L1 emits a *carry table* from the pinned template
and one parameterised predicate family is instantiated over it:

```cel
# instantiated per carry edge (src_cell -> dst_cell) discovered in the PINNED template
applicable: has(filing.at[src]) && has(filing.at[dst])
expr:       filing.at[dst] == filing.at[src]
witness:    [src, dst]
```

Concrete instance from the file: `'2. Summary'!B5 = '1. Introduction'!C54`; `'3. Portfolio'!B3 =
'1. Introduction'!D54`; `'1. Introduction'!D40 = D11`; `'1. Introduction'!D46 = D14`.

> **Where this stops, and it is important:** a carry predicate is *near-degenerate by construction*.
> When the filer uses the shipped workbook, Excel computes the destination, so the equality holds
> trivially and the predicate can never fail. It only earns admission for filings submitted as
> values-only workbooks or re-keyed exports. **L4 test 2 will and should reject most of the 223 carry
> predicates on a formula-bearing submission** — and *that rejection is itself the finding*: 44.2% of the
> workbook's formula mass is unfalsifiable motion. The registry must record them as
> `UNCHECKED("no oracle exists: destination is computed from source")` rather than silently counting them
> as passes. This is the sharpest concrete instance of the brief's §4.3 thesis.

---

**P-05 — Principal Officer ≠ Compliance Officer** (brief predicate #15). Real cells: `D26` vs `D29`.

```cel
applicable: filing.intro.tbl13.principal_officer_name != "" &&
            filing.intro.tbl13.compliance_officer_name != ""
expr:       normalize(filing.intro.tbl13.principal_officer_name)
              != normalize(filing.intro.tbl13.compliance_officer_name)
witness:    ["1. Introduction!D26", "1. Introduction!D29"]
```

`normalize` is a host function (case-fold, collapse whitespace, strip honorifics from a versioned list).
**It is a host function precisely so that its behaviour is separately versioned and separately mutation-
tested** — "Mr. Rajesh Kumar" vs "Rajesh  Kumar" is the entire difficulty of this predicate, and burying
it in the expression would make the predicate's FFR depend on an invisible string-handling decision.

---

**P-06 — scheme authorisation date ≤ period end, and FME registration ≤ scheme authorisation**
(brief predicates #7 and #8). Real cells: `D11` (FME reg date), `E54:E63` (scheme auth dates),
`D2`/`D3` (quarter, FY).

```cel
applicable: has(filing.intro.tbl11.quarter) && has(filing.intro.tbl11.financial_year)
            && size(filing.intro.tbl15.rows) > 0
expr:       filing.intro.tbl15.rows.all(r,
              r.auth_date == null ||
              (date(r.auth_date) <= period_end(filing.intro.tbl11.quarter,
                                               filing.intro.tbl11.financial_year)
               && date(filing.intro.tbl12.fme_reg_date) <= date(r.auth_date)))
witness:    filing.intro.tbl15.rows.filter(r, /* same, negated */).map(r, r.__cell__)
```

`date()` and `period_end()` are host functions; `period_end` maps the two dropdown vocabularies
(`Dropdown!D3:D6` = April–June / July–September / October–December / January–March, and
`Dropdown!E3:E6` = 2025-26 … 2028-29) to a concrete date. **That mapping is regulation-derived and is
therefore itself a versioned artifact with a clause citation**, not a helper.

---

**P-07 — dropdown ∈ vocabulary**, generalised (brief predicate #13). Given §A.0.1(b) — 15 vocabularies
shipped, 1 enforced — this is not one predicate but **15**, of which the template enforces one. The
family is:

```cel
applicable: size(filing.at_range[range_key]) > 0
expr:       filing.at_range[range_key].all(v, v == "" || v in template.vocab[vocab_key])
```

instantiated over the 15 `(range_key, vocab_key)` pairs L1 derives from `Dropdown!D3:R14`. **This single
family takes the workbook from 3 enforced vocabularies to 15 — a 5× increase in enforced controlled
vocabulary, achieved with zero model involvement, entirely from L1's induced schema.** It is the cheapest
coverage increment in the system and it should be in the two-day build.

---

## A.7 — Explicit justification against the runners-up

**vs. plain Python + pandera (the obvious choice, and the one to beat).** Python wins on expressiveness
and on developer speed. It loses on four things that are each independently decisive here:
(i) *coverage is not computable* — you cannot statically determine which fields a Python function reads,
so the brief's headline number becomes an estimate, and the brief's own §4.4 is a monument to what
happens when a deterministic program's coverage claim is inferred rather than derived;
(ii) *executing model-written Python requires a sandbox*, and Part B shows the sandbox layer is where the
2026 CVEs actually are;
(iii) *the predicate stops being auditable* — Screen 3 shows a function body, not a rule, and the
regulator-facing artifact degrades;
(iv) *mutation of the predicate itself* (needed for registry hygiene) means mutating arbitrary Python,
where the equivalent-mutant rate is high and unbounded, versus a 20-production grammar where the mutation
operators are enumerable.
**Adopt pandera anyway — as a *host-function* implementation detail for bulk column checks, never as the
predicate language.**

**vs. Rego.** The better semantics (undefined ≈ unchecked), the worse readability and the wrong host
language. Genuinely close. If the team were writing Go, this ordering could flip.

**vs. Z3 as primary.** Category error: Z3 answers "is this predicate ever falsifiable", not "is this
filing correct". Adopted for L4, rejected for L5.

**vs. Drools / ZEN.** We do not want rule chaining; we want independently-scored assertions. Chaining
makes both mutation score and FFR non-attributable.

**vs. VTL.** Right domain, wrong data model, JVM-only, implementations stuck on the 1.1 draft.

**vs. Starlark / JSONLogic / JMESPath / SpEL.** Too powerful and stateful; too weak; a query language not
a predicate language; and an RCE vector, respectively.

**The honest cost of choosing CEL.** (a) Two competing Python packages both called "cel-python"
(§A.2) — a real footgun; pin by PyPI name and hash. (b) `cel-expr-python` is 5 months old, 76 stars, and
launched read-only; `celpy` is pure-Python and slower but has years of use inside Cloud Custodian. **Start
on `celpy`** (Apache-2.0, no build toolchain, no C++ dependency, trivially auditable) and keep
`cel-expr-python` as the drop-in for when conformance-exactness matters more than deployment simplicity.
(c) The error-absorption hazard (§A.6.4 rule 2) is a genuine sharp edge that must be structurally guarded,
not documented. (d) CEL has no decimal type — `double` only. **For a filing denominated in USD Million to
two decimal places, we must scale to integer micro-units at L1 and compare integers**, or every arithmetic
predicate inherits a floating-point FFR we did not choose. This is a real requirement, not a nicety.

---

## A.8 — The escape hatch

Four of the 17 decidable predicates cannot be expressed in the restricted grammar. Each becomes a **host
function**: a named, deterministic, individually-versioned Python function registered into the CEL
environment. The predicate stays one readable line; the impurity is quarantined and enumerable.

| Host function | Serves predicate | What it does | Why it cannot be CEL | Its own qualification |
|---|---|---|---|---|
| `reg_resolves(kind, number)` | #9, #10 | look up an FME/scheme number in the L0-snapshotted register | needs external state | **must return a tri-state** `TRUE / FALSE / UNKNOWN(snapshot stale)`; UNKNOWN ⇒ UNCHECKED("requires counterparty data"). Never resolves live at verdict time — always against a content-addressed snapshot, or the report is not reproducible |
| `gstin_valid(s)` | #11 | 15-char GSTIN structure + mod-36 check digit | string algorithm with arithmetic over a 36-char alphabet | pure function; unit tests + its own mutation score; deterministic, so it belongs to the *deterministic* half of the coverage claim |
| `template_current(hash)` | #16 | compare against L0's registry of published template hashes | needs the corpus | tri-state: `CURRENT / SUPERSEDED / UNKNOWN` |
| `nav_interval(scheme_type, open_closed, tenure)` | #17 | the NAV frequency owed under regs 27(1)/39(1)/51(1) | encodes regulation, including 39(1)'s half-yearly proviso for close-ended restricted schemes and 51(1)'s *"in such manner as specified by the Authority"* delegation | **the delegation hook means this function must be able to return `UNDERSPECIFIED`** ⇒ UNCHECKED("rule ambiguous"). A regulation that delegates is not a rule we may silently resolve |
| `matches(s, re)` `date(s)` `months_between(a,b)` `abs` `round` `normalize` | #14, #7, #8, #6, #12, #15 | pure utility | CEL has `matches` natively; the rest are pure | pure; versioned with the profile |

**The rule that keeps the escape hatch from eating the design:** a host function may be **added only by a
human**, is **never generated by a model**, has its **own test suite and its own mutation score**, and
**must be able to return a third value** wherever its answer can be unknown. The set is closed at
evaluation time; a predicate calling an unregistered function is rejected at admission.

**The `nav_interval` row is the most important one in this table.** Predicate #17 is the only one of the
17 that encodes a *regulatory* rather than an *arithmetic* obligation, and reg 51(1) ends *"in such manner
as specified by the Authority"* (RND-BRIEF §6.3). A system that resolves that delegation into a concrete
interval is asserting something the regulation does not say. **It must return UNDERSPECIFIED.** That
single design decision is the architecture's thesis executed at the level of a function signature.

---

# PART B — SANDBOXING

## B.1 The threat model, stated

**The adversary is a confused model and a malformed file. It is not a hostile attacker.** What that
changes:

| | Hostile attacker | Confused model (ours) |
|---|---|---|
| Goal of the sandbox | prevent escape by an adversary actively probing for one | prevent *unintended effect* and *unbounded resource use*; contain a parser crash |
| Cost of a rare escape | catastrophic | contained — nothing valuable is in the process |
| Acceptable overhead | high (Firecracker, per-tenant VMs) | low; the sandbox must not dominate a 6,757-cell workbook |
| The real risk | RCE, data exfiltration | **a wrong verdict** |

**But two adversaries are hostile and must not be waved away.** (1) **The filer.** They supply the
`.xlsx`. An `.xlsx` is a zip of XML: zip bombs, XXE, billion-laughs, quadratic blowup, and formula/DDE
payloads are all in scope for L0/L1's parser, and `lxml` has a documented history here. **The parser, not
the predicate, is the exposed surface.** (2) **If L3 ever emits Python** (which this lane recommends it
must not), a model that has read the filing is an *injection-carrying* component: text in the workbook
becomes text in the prompt becomes text in the generated code.

## B.2 What the 2026 evidence says about the popular answer

The default 2026 recommendation is "run it in Pyodide/WASM". **The evidence says WASM alone is not a
security boundary for Python**, and there is a concrete, recent, well-documented escape.

**Grist / "Cellbreak"** (SECONDARY — Cyera Research Labs writeup, which I read in full): advisory
`GHSA-7xvx-8pf2-pv5g`, **CVSS 9.1**, opened **30 Dec 2025**, patched in **Grist 1.7.9 on 20 Jan 2026**,
public **21 Jan 2026**. A *spreadsheet formula* escaped the Pyodide WASM sandbox by **three independent
routes**:

1. `object.__subclasses__()` → `warnings.catch_warnings` → full `__builtins__` → `os.system()`
2. `ctypes.CDLL(None).system()` — libc directly, inside Emscripten
3. `emscripten_run_script_string()` → JS in the host → `require('child_process')`, `process.env`

The fix was **not** to harden Pyodide; it was to run Pyodide **under Deno's permission system**. The
writeup's conclusion: *"sandboxing needs to be capability-based and defense-in-depth, not a fragile
blocklist"*, and it notes Grist's own team pointing at **gVisor** as providing *"stronger isolation
guarantees"*. The escape hatch `GRIST_PYODIDE_SKIP_DENO=1` reinstates the original risk.

**A correction to a claim now circulating, which this lane should stop from entering the brief.**
Several 2026 write-ups (and a Hacker News post) state that **CVE-2026-5752 is a Pyodide vulnerability and
that "the project is unmaintained, so the issue remains UNPATCHED."** Checking:

- The SentinelOne vulnerability database entry for **CVE-2026-5752** (SECONDARY; NVD returned HTTP 502
  on two attempts, so this is the best source I reached) records the product as **Cohere Terrarium**,
  CVSS **9.3**, vector `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`, published **17 Apr 2026**,
  description *"sandbox escape vulnerability in Terrarium enabling arbitrary code execution with root
  privileges via JavaScript prototype chain traversal"*, remediation *"Consider temporarily disabling
  Terrarium sandbox functionality until patches are available."* **The SentinelOne page identifies no
  project as unmaintained.**
- The **Pyodide** repository (VERIFIED-AT-SOURCE, github.com/pyodide/pyodide) is **MPL-2.0, 14.8k★, 1.0k
  forks**, and describes itself as *"an independent and community-driven open-source project"* with
  active governance. **No unmaintained notice.**

**Conclusion: the CVE is against Cohere's Terrarium, not Pyodide; "Pyodide is unmaintained" is a
conflation and must not be repeated.** The *substantive* lesson survives entirely: **Pyodide's Python
surface (ctypes, `__subclasses__`, Emscripten hooks) is reachable from user code, so WASM-of-CPython is a
resource boundary and a portability layer, not a security boundary.**

## B.3 Options, and the recommendation

| Option | Licence / status | Isolation | Determinism | Verdict for us |
|---|---|---|---|---|
| **RestrictedPython** | zopefoundation; releases 8.3 (16 Jun 2026), 8.4 (10 Jul 2026) (SECONDARY, libraries.io) | AST filtering + attribute wrappers | n/a | **Reject as a boundary.** Its own docs say it *"is not a sandbox system or a secured environment"* (VERIFIED via docs quote in search result). CVE-2023-37271: stack-frame walking out of generators escaped it before 6.1/5.3. Useful only as *defence in depth inside* a real boundary |
| **Pyodide / WASM-CPython** | MPL-2.0, 14.8k★ (VERIFIED-AT-SOURCE) | see §B.2 | good | **Reject as the boundary**; keep as a portability option if predicates must ever run client-side |
| **wasmtime** | Bytecode Alliance (licence NOT-FOUND — I did not open the LICENSE file) | true WASM sandbox for *WASM-native* code | **best in class**: fuel metering is *"completely deterministic: the same program run with the same amount of fuel will always be interrupted at the same location"*; epoch interruption is faster but non-deterministic (SECONDARY, docs.wasmtime.dev) | **Adopt if and only if we ever compile the predicate evaluator itself to WASM.** Deterministic fuel is exactly the right shape for a reproducible cost budget. Not needed for a CEL host |
| **gVisor** | (licence NOT-FOUND) | user-space kernel intercepting syscalls; shrinks host-kernel attack surface; Sentry runs on the host (SECONDARY) | good | **ADOPT.** Right point on the curve for a confused-model + malicious-file model; container-native, no nested virtualisation, no guest OS to manage. Independently endorsed by Grist's team for this exact problem class |
| **Firecracker** | (licence NOT-FOUND) | KVM microVM, own guest kernel; ~125 ms boot, ~5 MB overhead (SECONDARY) | good | **Reject for now.** Buys hypervisor-grade isolation against an adversary we do not have, and costs a VM per filing. Revisit only for multi-tenant SaaS with untrusted tenants |
| **E2B** | managed, Firecracker-backed (SECONDARY) | strong | good | **Reject.** A managed remote execution service means the filing leaves our boundary. For IFSCA-regulated filings that is a data-residency conversation we should not have to have |
| **Docker + seccomp** | ubiquitous | shared host kernel + syscall filter | good | **Adopt as the baseline layer under gVisor**, not instead of it |

### B.4 The recommended configuration

```
L1 PARSER TIER  (untrusted input: the filer's .xlsx)
  runsc (gVisor)  +  seccomp  +  --network=none  +  read-only rootfs
  + tmpfs work dir, size-capped        + uid/gid non-root, no-new-privileges
  + RLIMIT_AS, RLIMIT_CPU              + wall-clock kill
  + zip guards BEFORE parse: entry count, per-entry uncompressed size, total ratio
  + XML: lxml with resolve_entities=False, no network, no DTD
  -> emits ONLY the typed fact JSON. Nothing else crosses the boundary.

L5 EVALUATOR TIER  (trusted code, restricted data)
  ordinary process. CEL is terminating, side-effect-free, has no I/O, and binds exactly two
  names. There is nothing to sandbox: the language IS the sandbox.
  + per-predicate cost budget (celpy step counter) and wall-clock kill  [§A.6.4 rule 3]
  + host-function registry is closed, hand-written, individually tested
```

**The whole argument of Part B in one sentence: choosing a restricted predicate language in Part A
deletes the hardest sandboxing problem instead of solving it**, and leaves behind only the parser problem,
which is an ordinary, well-understood container-hardening exercise.

> **Where this fits:** L0/L1 (parser tier), L5 (evaluator tier).
> **Where it stops:** gVisor does not protect against a *wrong verdict*, which is our actual risk. No
> sandbox in this table addresses the brief's problem; they address a different one that we would have
> acquired by choosing Python.

---

# PART C — FAULT SEEDING

## C.1 The methodological error in the brief, stated precisely

ARCHITECTURE.md L4 test 1 reads:

> **"Can it fire?"** — **mutation testing.** Seed artificial faults into clean artifacts and measure the
> fraction the predicate kills. *Mutation score* = `|killed| / (|mutants| − |equivalent|)` … tooling
> exists (mutmut for Python, PIT for JVM, Stryker for JS).

**The prose is right and the tooling is wrong.** "Seed artificial faults into clean *artifacts*" is
**data** fault seeding. mutmut, PIT and Stryker mutate **source code** and re-run a **test suite**. Their
subject is the test suite; ours is the *rule set*; their mutants are program variants; ours must be
*filing variants*. Wiring mutmut to this problem would mutate our own predicate implementations — a real
but *different* activity (§C.6).

**The correct framing, and it is a clean inversion of classical mutation analysis:**

| Mutation testing (classical) | Fault seeding (what L4 needs) |
|---|---|
| Subject under evaluation: a **test suite** | Subject under evaluation: the **predicate set** |
| Mutants are variants of the **program** | Mutants are variants of the **filing** |
| A mutant is *killed* if some test fails | A mutant is *killed* if some predicate FAILs |
| Equivalent mutant = semantically identical program | **Unobservable mutant** = a filing variant no predicate *could* distinguish |
| Mutation score = suite adequacy | **Kill rate = rule-set adequacy** = a lower bound on coverage that is *earned*, not asserted |

The theory transfers exactly; only the artifact class changes. And critically, **the analogue of the
equivalent-mutant problem transfers too, and it is much worse here** — see §C.3.

## C.2 The literature the brief should be citing

### The one that matters most: spreadsheet mutation operators

**Abraham, R. & Erwig, M., "Mutation Operators for Spreadsheets", IEEE Transactions on Software
Engineering 35(1):94–108, 2009.** VERIFIED-AT-SOURCE — I opened the PDF at
`https://web.engr.oregonstate.edu/~erwig/papers/MutationOps_TSE09.pdf` and read pages 5–12 including
Tables 1–9.

Their **Table 3, "Mutation Operators for Spreadsheets"**, is 17 operators and it is, verbatim, a fault
taxonomy for exactly our artifact class:

| Op | Name | Direct mapping to a financial-workbook fault |
|---|---|---|
| ABS | Absolute value insertion | **sign flip** |
| AOR | Arithmetic Operator Replacement | `+`↔`-`, `*`↔`/` in a subtotal |
| CRP | Constants RePlacement | keyed value wrong |
| CRR | Constants for Reference Replacement | a carried value hard-typed |
| LCR | Logical Connector Replacement | AND/OR in an eligibility test |
| ROR | Relational Operator Replacement | `<=` vs `<` on a threshold/date |
| RCR | **Reference for Constant Replacement** | a constant replaced by a cell reference |
| FDL | Formula DeLetion | a total simply removed |
| **FRC** | **Formula Replacement with Constant** | **"formula overwritten by a constant" — the brief's own listed fault, named and studied here** |
| RFR | ReFerence Replacement | **off-by-one row shift** (they explicitly use the *eight spatial neighbours* as candidates) |
| UOI | Unary Operator Insertion | sign flip |
| CRS / NRS | Contiguous / Non-contiguous Range Shrinking | **dropped row** from a SUM |
| CRE / NRE | Contiguous / Non-contiguous Range Expansion | **duplicated / extra row** in a SUM |
| RRR | Range Reference Replace | wrong member in a non-contiguous range |
| FFR | Formula Function Replacement | **SUM↔AVERAGE, SUM↔COUNT** — unit/aggregate confusion |

The paper's own justification for FRC is precisely our case:

> "It has been observed in empirical studies that when the spreadsheet specifications are not well
> understood, users sometime overwrite formula cells with constant values as a 'quick fix' to get the
> output they expect."

Scale of their evaluation (Table 4): **15 spreadsheets, 211 formula cells, 542 total cells, 7,500 mutants
generated.**

### The number that changes our harness design

**Table 7** classifies all 7,500 mutants as *irreversible* or *reversible*, and defines irreversible as:

> "Irreversible mutants are the mutated formulas that evaluate to the same value as the original formula,
> given the input values in the original spreadsheet, and thus cannot produce failures that could be
> identified by the user."

**Result: 3,512 irreversible / 3,988 reversible / 7,500 total. 46.8% of naively-generated spreadsheet
mutants produce no observable change on the artifact they were seeded into.**

(Note the paper's footnote 4 on p.9: *"All the generated mutants were nonequivalent to the original
spreadsheets"* — i.e. these are not *equivalent* in the classical, all-inputs sense. They are
unobservable **on this input**. Since a filing *is* a single input, that is precisely the denominator
problem we face, and it is worse than classical equivalence, not better.)

**Design consequence, and it is the most important sentence in Part C: a kill rate computed over
generated mutants is uninterpretable. It must be computed over *observably-faulty* mutants — mutants
verified, by recalculation, to change at least one reported value.** Otherwise ~47% of the denominator is
un-killable by anyone, and every predicate looks worse than it is by a factor that varies with the
operator mix.

### The number that kills the naive mutation score

**Petrović, Ivanković, Fraser & Just, "Practical Mutation Testing at Scale: A view from Google", IEEE TSE
(DOI 10.1109/TSE.2021.3107634); arXiv:2102.11378.** VERIFIED-AT-SOURCE — I read pp. 1–4 of the TSE PDF.

> "developers at Google initially classified 85% of reported mutants as unproductive."
> "An *unproductive* mutant is either trivially equivalent to the original program or it is detectable,
> but adding a test for it would not improve the test suite."
> "The feedback from more than 20,000 developers on thousands of mutants over six years enabled us to
> develop heuristics for mutant suppression that reduce the ratio of unproductive mutants **from 85% to
> 11%**."
> "Our evaluation of the proposed approach involved **760,000 code changes and 2 million mutants reported
> during code review, out of a total of almost 17 million generated mutants**."
> Scale: *"more than 24,000 developers on more than 1,000 projects."*

Also load-bearing for our operator selection: they implement five operators (**AOR, LCR, ROR, UOI, SBR**)
across **10 languages including SQL**, generate **at most one mutant per line**, and **dropped ABS**
because it *"predominantly created unproductive mutants."*

**Denominator discipline:** 85% → 11% is *Google's* rate on *code* mutants judged by *developers*. It does
not transfer numerically. What transfers is the **structure**: *the majority of naively generated mutants
are worthless, and the productive fraction is achieved by suppression heuristics learned from feedback,
not by generating more.*

**Madeyski, Orzeszyna, Torkar & Józala, "Overcoming the Equivalent Mutant Problem: A Systematic Literature
Review and a Comparative Experiment of Second Order Mutation", IEEE TSE 40(1):23–42, 2014** (SECONDARY):
17 techniques across 22 articles, in three families — **detecting (DEM), suggesting (SEM), and avoiding
equivalent mutant generation (AEMG)**. **AEMG is the family we want**: do not generate the unobservable
mutant in the first place (§C.4 step 3).

### Data-error generation, from the database community

- **BART — "Messing Up with BART: Error Generation for Evaluating Data-Cleaning Algorithms", Arocena,
  Glavic, Mecca, Miller, Papotti & Santoro, PVLDB 9(2):36–47, 2015** (SECONDARY; I fetched the PDF but the
  text layer would not yield exact quotes). The relevant contributions: a principled split between
  **detectable** and **non-detectable** errors (errors that violate a declared constraint vs errors that
  satisfy every constraint), a **degree of detectability** control, and the result that **the
  error-generation problem is NP-complete**, handled by a greedy algorithm. *This is the closest existing
  system to what we need to build*, and its detectable/non-detectable split maps directly onto our
  killed/unobservable split.
- **JENGA — Schelter, Rukat & Biessmann, EDBT 2021** (SECONDARY): three abstractions — *tasks*, *data
  corruptions* (missing values, outliers, typos, noisy measurements), *evaluators*. Our harness is the
  same shape with "model" replaced by "predicate set". Worth reading for the corruption API design.
- **SQL mutation.** *SQLMutation* (Tuya, Suárez-Cabal & de la Riva, Mutation 2006) defines four operator
  families — **SC** (SQL clause), **OR** (operator replacement), **NL** (NULL handling), **IR**
  (identifier replacement) — tested against the NIST SQL Conformance Test Suite (SECONDARY). *Mutant
  Swarm* (Expedia) is a Hive-SQL mutation tool (SECONDARY).
- **MutaSQL — "Testing Query Execution Engines with Mutations", DBTest 2020** (SECONDARY): **8 seed
  queries, 23 mutation rules, reproduced 34 bugs and found 1 new one in SQLite.** **But read it
  correctly:** MutaSQL mutates a query `Q` into `Q'` that *should evaluate to the same result*, then
  compares. **That is metamorphic testing, not fault seeding** — it belongs in the brief's **L6**, not
  L4. If the brief cites MutaSQL it must cite it there.

### Prior art nobody in the brief has noticed: XBRL US Data Quality Committee

This is the closest existing thing to the brief's "predicate registry as the durable asset", **for
regulated financial filings**, and it exists.

- Rules live at `github.com/DataQualityCommittee/dqc_us_rules` (VERIFIED-AT-SOURCE: **31★, 39 forks**;
  licence stated as *"See https://xbrl.us/dqc-license"* — **I did not open that licence, so its terms are
  NOT-FOUND**).
- Rules are written in **Xule**, an XBRL rule syntax executed as an **Arelle** plugin
  (`github.com/xbrlus/xule`). The README: *"The DQC rules are run using an Arelle plugin written in an
  XBRL rule syntax called Xule."*
- **Their qualification process is our L4 test 3, already operating in production, on a financial filing
  corpus.** VERIFIED-AT-SOURCE from `xbrl.us/home/priorities/data-quality/rules-guidance/rules-process/`:

  > "The DQC researches every rule for false positives using SQL queries against the XBRL US Database of
  > Public Filings – a copy of all XBRL SEC filings that also includes historic data quality issue
  > records."
  > "Every draft rule is tested by running it against historical corporate filings. Reported values that
  > trigger the draft rule are analyzed in detail to make sure that they are flagging errors appropriately
  > and not generating false positives."
  > "This is because the risk is too high that a filer will be led astray and waste time attempting to
  > correct something that was right in the first place."

  Their published 10-step process: create draft rules → consider potential problems → write clear
  messages → test the rules → public review → incorporate feedback → set effective dates → DQC approval
  and publication → FASB taxonomy team incorporates into DQCRT → SEC adopts DQCRT.

**What this does to the brief's positioning.** It **QUALIFIES**, hard, the claim that no analogue exists
for declaring what you could not check. The DQC has been running a versioned, publicly-reviewed,
false-positive-gated rule registry over regulated financial filings for a decade. **The differentiator
survives, but it must be restated precisely:** the DQC gates *for* false positives before publication and
then publishes a rule; it does **not** publish a per-rule measured false-failure rate alongside each
finding, and it does **not** publish a coverage denominator saying what fraction of the filing its rules
touch. **Our novelty is the *quantified* and *declared* version of a discipline the DQC already practises
qualitatively.** That is a smaller claim and a far more defensible one — and it comes with a named,
credible precedent, which strengthens rather than weakens the pitch.

> **Where this fits:** L4 (process design — copy it), L7 (registry versioning and effective dates).
> **Where it stops:** XBRL-only, US-GAAP-taxonomy-only, Xule/Arelle-only, and there is **no equivalent for
> IFSCA workbooks** (the brief's §4.1 grep over 399 circulars is the evidence for that absence).

## C.3 The fault taxonomy for a financial reporting workbook

The brief lists eleven fault classes. Below, each is given a **generator**, an **observability
condition**, and its **provenance** — whether it comes from Abraham & Erwig's operator suite, from the
Panko–Halverson human-error taxonomy, or from the artifact itself.

*Panko–Halverson framing* (SECONDARY — via Powell/Baker/Lawson's critical review and EuSpRIG papers; I
could not extract clean text from the primary PDF): quantitative spreadsheet errors divide into
**mechanical** (typing/pointing), **logic** (wrong function or formula), and **omission**
(misinterpretation of the situation). In one Panko & Halverson experiment the split was **45% logic / 23%
mechanical / 31% omission**, with detection rates *highest for mechanical and lowest for omission*.
**That ordering is the brief's problem restated in 1996 vocabulary:** the errors machines catch are the
ones humans also catch, and the ones nobody catches are the omissions.

| # | Fault | Class | Generator | Observable iff | Provenance |
|---|---|---|---|---|---|
| F1 | **Transposition** | mechanical | swap two adjacent digits in a numeric cell (`1234.56 → 1243.56`); reject if value unchanged | the cell feeds a total or a cross-sheet carry | Panko mechanical; CRP |
| F2 | **Sign flip** | mechanical | negate a numeric cell | a downstream identity or a `>= 0` validation exists (**35 validations, many `decimal ≥ 0`** — MEASURED-BY-ME) | ABS / UOI |
| F3 | **Off-by-one row shift** | mechanical | shift a whole row's values up/down one row within its table | the row is keyed (scheme name/auth no.) so the key/value binding breaks | **RFR**, with A&E's 8-neighbour candidate rule |
| F4 | **Unit confusion (lakh/crore/USD-mn)** | logic | multiply a declared-unit column by 1e5, 1e7, 1e6 or 1e-6 | a cross-table relation in a different unit exists, or a plausibility band | Panko logic; the workbook labels units in headers ("USD Million") but **enforces none of them** |
| F5 | **Stale carry-forward** | omission | replace a period-end value with the prior period's | a prior filing is available, or an internal opening/closing identity exists (`'3. Portfolio'!C16:F16` borrowing open/close) | Panko omission |
| F6 | **Duplicated row** | logic | copy a table row into a free row | a count, a total, or an identity across tables | **CRE / NRE** |
| F7 | **Dropped row** | omission | blank a populated table row | same | **CRS / NRS** |
| F8 | **Date off-by-period** | mechanical | shift a date by ±1 quarter / ±1 year | a date ordering predicate exists (#7, #8, #17) | ROR/CRP |
| F9 | **Currency mislabel** | logic | change a currency label without rescaling values | a magnitude relation or a declared-unit predicate exists | Panko logic |
| F10 | **Rounding drift** | mechanical | perturb components by ±0.005 so a total no longer reconciles at 2dp | the tolerance in the identity predicate is tighter than the drift — **this is the fault that *calibrates the tolerance*** | CRP |
| F11 | **Formula overwritten by a constant** | logic | replace a formula cell with its computed value, **then perturb an input it depended on** | the perturbation would have changed the formula's value | **FRC**, named and studied in A&E |
| F12 | **Vocabulary drift** *(added by this lane)* | logic | write a scheme type not in `Dropdown!F3:F11`, or edit the `Dropdown` sheet itself | predicate #13 evaluated against the **pinned template** | MEASURED-BY-ME §A.0.1(b) — the Dropdown sheet is unprotected |
| F13 | **Carry desynchronisation** *(added)* | mechanical | change a destination cell of one of the 195 cross-sheet carries without changing its source | predicate family P-04 | MEASURED-BY-ME |
| F14 | **Vocabulary-gap exploitation** *(added)* | omission | declare every scheme as `Special Situation Fund` | **only if the predicate does NOT reproduce the template's COUNTIF** | MEASURED-BY-ME §A.0.1(a) — this fault is *invisible to the template's own formula* |

**F11 needs its two-step generator understood, because it is the most instructive fault in the list.**
Overwriting `=SUM(C3:N3)` with its current value `0` changes nothing observable — it is an *irreversible*
mutant in Abraham & Erwig's sense and contributes only to the 46.8%. It becomes observable only when a
component is subsequently perturbed and the frozen total fails to move. **So F11 must be generated as a
pair, and any harness that generates it as a single edit will report a spuriously low kill rate.**

**F14 is the taxonomy's payoff.** It is a fault that the *template's own validation logic cannot see*, and
it exists because of a defect I measured today. A rule set mined from the template is *blind by
construction* to a fault class the template creates.

## C.4 The fault-seeding harness — specification

```
┌── INPUTS ─────────────────────────────────────────────────────────────────────┐
│ T   pinned blank template, content-addressed          (from L0)               │
│ S   induced schema: fields, types, ranges, formulas, vocabularies (from L1)   │
│ C   clean corpus: N correctly-filled workbooks                                │
│     ** LABEL REQUIRED: SYNTHETIC-TEAM-FILLED | REAL-FILED **                  │
│ P   the candidate predicate (or the admitted set, for interaction runs)       │
└───────────────────────────────────────────────────────────────────────────────┘

STEP 1  TARGET SELECTION
  Seed only into fields P.schema_keys actually reads (extracted from the CEL AST) PLUS
  a 10% control sample of fields it does NOT read.
  Rationale: the first measures kill rate; the CONTROL SAMPLE MEASURES SPURIOUS FIRING, and
  without it a predicate that flags everything scores a perfect kill rate. This is L4 test 2
  implemented empirically alongside the Z3 proof.

STEP 2  GENERATION
  For each (clean workbook c in C) x (target field f) x (fault class F1..F14):
    emit a candidate mutant m = apply(F, c, f), with a manifest:
      {clean_hash, fault_class, target_cell, param, seed}
  Bound the cross-product: at most ONE mutant per (field, fault class) per clean workbook
  — Google's "at most one mutant per line", transposed. (VERIFIED-AT-SOURCE, §C.2.)

STEP 3  OBSERVABILITY FILTER  ** the step the brief does not have, and the one that decides
        whether the kill rate means anything **
  Recalculate m (LibreOffice headless or formulas.py) and diff the RESULTING VALUE GRID
  against the recalculated clean workbook.
    - no cell value differs                    -> DISCARD as UNOBSERVABLE, count separately
    - a value differs but only in a cell no predicate in the registry can reach
                                               -> retain, tag UNREACHABLE
    - otherwise                                -> admit to the denominator
  Expected discard rate: HIGH. Abraham & Erwig measured 3,512/7,500 = 46.8% irreversible on
  a comparable operator suite. Report our own figure every run; it is a property of the
  operator mix and must not be assumed.

STEP 4  EXECUTION
  Run P (and, for interaction, the admitted set) over every admitted mutant and over every
  clean workbook.

STEP 5  SCORING  (§C.5)

STEP 6  PROVENANCE
  Every mutant is content-addressed; every kill records (mutant_hash, predicate_id,
  predicate_version, template_hash, harness_version, corpus_label). The L7 attestation signs
  over these, so a quoted kill rate is reproducible or it is not quoted.
```

**Implementation notes.** Generate mutants by editing the OOXML directly (the workbook is a zip of XML;
9 of 10 sheets are protected but sheet protection is a UI affordance, not a lock — `openpyxl` writes
through it). Recalculation is the one genuinely awkward dependency: `openpyxl` does not evaluate formulas.
Use LibreOffice headless (`--convert-to xlsx` forces recalc) in the gVisor tier, or a pure-Python
formula evaluator if the formula surface stays inside `SUM/COUNTIF/IF/IFERROR` — which, per my census
(§A.0.2), it does for **281 of 505 formula cells (55.6%)**; the `IFERROR(INDEX(AGGREGATE(...)))` block on
`'1. Introduction'!C92:E101` is the awkward remainder.

## C.5 How kill rate is computed and reported

Three numbers, never one, and each with its denominator visible:

```
GENERATED        G  = |mutants generated|
UNOBSERVABLE     U  = |mutants whose recalculated value grid is identical to clean|
OBSERVABLE       O  = G - U
UNREACHABLE      R  = |observable mutants touching no field any admitted predicate reads|
KILLED           K  = |observable mutants for which at least one predicate returned FAIL|

KILL RATE            KR   = K / O                       <- the headline; NEVER K/G
REACHABLE KILL RATE  RKR  = K / (O - R)                 <- adequacy of the rules we HAVE
UNOBSERVABLE RATE    UR   = U / G                       <- a property of the OPERATORS, reported
                                                            so the operator mix is auditable
```

**Reporting rules — these are the brief's own instrument discipline made mechanical:**

1. **Never quote a bare "mutation score."** Quote `K/O` with both integers, plus `UR`. A kill rate whose
   denominator is not stated is exactly the class of number the brief's Part 8 exists to withdraw.
2. **Report per fault class, not only in aggregate.** A predicate that kills 100% of F2 (sign flip) and
   0% of F5 (stale carry-forward) has a headline kill rate near 50% and two completely different
   properties. The predicate library entry carries the **vector**.
3. **`R` is a coverage statement, not a failure.** Observable mutants nothing reads are exactly the
   UNCHECKED region, arrived at empirically. `R/O` rising over time is the *inverse* of the Screen-4
   coverage curve and should be plotted next to it.
4. **The clean-corpus label propagates.** Every FFR and every kill rate carries
   `SYNTHETIC-TEAM-FILLED` or `REAL-FILED`. The brief already flags this as the design's largest
   structural weakness (§9.2); the harness must make the caveat un-droppable by putting it in the record,
   not in a footnote.
5. **Admission thresholds, pre-registered before the first run** (this lane's proposal, to be argued
   before it is used): admit iff `K/O ≥ 0.80` on the fault classes the predicate *claims* to cover, AND
   Z3 returns non-degenerate (or an empirical falsifying witness exists), AND `FFR ≤ 0.05` on the clean
   corpus with `n` stated, AND marginal FFR conditioned on the already-admitted set is reported.
6. **Suppression heuristics are learned and logged, never silent.** Following Google (85%→11% via
   feedback-derived suppression, VERIFIED-AT-SOURCE), any operator/target combination we stop generating
   is recorded with its reason in the harness manifest. **An undeclared suppression is a coverage lie.**

## C.6 Where we *do* mutate code, and how

Three places, all of them our own code, none of them model-generated:

1. **The host functions** (§A.8: `gstin_valid`, `normalize`, `date`, `period_end`, `nav_interval`,
   `reg_resolves`). Real Python, real logic, real bugs. **Use `mutmut`** — **BSD-3-Clause, 1.4k★, 165
   forks** (VERIFIED-AT-SOURCE), with `# pragma: no mutate` for the suppression that Google's paper shows
   is unavoidable. **`cosmic-ray`** (MIT, `sixty-north/cosmic-ray`) is described as the more actively
   maintained option with a broader operator set (SECONDARY — a 2024/2025 comparative study of Python
   mutation tools; I did not open the study, so treat the "most maintained" claim as UNVERIFIED). Either
   is fine; the host-function set is small.
2. **The L1 schema inducer.** This is where the brief's §4.4 bugs lived and where my §A.0.2 bug lived.
   The highest-value code mutation target in the system, precisely because its failures are silent.
3. **The predicate profile checker** (the AST walker that enforces §A.6.3 and verifies `schema_keys`).
   If this is wrong, coverage is wrong, and coverage is the product.

**On the equivalent-mutant problem, practically.** Do not attempt to detect equivalent mutants — the
literature (Madeyski et al., 17 techniques, 22 articles) says detection is hard and partial. Do three
cheap things instead: (a) **prefer avoidance (AEMG)** — the observability filter (§C.4 step 3) *is* AEMG
for data mutants and removes the problem at its source; (b) **suppress operators empirically** — Google
dropped ABS because it *"predominantly created unproductive mutants"*; when a fault class shows a >70%
unobservable rate over several runs, demote it and log the demotion; (c) **never put the equivalent count
in the denominator as an estimate.** The brief's formula `MS = |killed| / (|mutants| − |equivalent|)`
requires knowing `|equivalent|`, which is undecidable in general. **Our `K/O` needs no such term** —
observability is *measured by recalculation*, not estimated. That substitution is the single biggest
practical improvement available to L4, and it is available only because our mutants are data, where
"observable" is a diff, rather than code, where "equivalent" is a theorem.

---

# PART D — ASSET LEDGER

| Asset | Licence | Verdict | Fits at | Stops at |
|---|---|---|---|---|
| **CEL spec + `celpy`** (`cloud-custodian/cel-python`) | Apache-2.0 ✔ | **ADOPT — primary predicate language** | L3 output format, L4 mutation target, L5 evaluator | no decimals (scale to integers at L1); error absorption in `\|\|`/`&&` must be structurally guarded |
| **`cel-expr-python`** (`cel-expr/cel-python`) | Apache-2.0 ✔ | **EVALUATE** — official, C++-backed, 5 months old, 76★, read-only repo | drop-in for `celpy` when conformance exactness matters | immature; a C++ build dependency |
| **cel-go** | Apache-2.0 ✔, 3.1k★ | REJECT (wrong host language) — but it is the reference implementation to read | — | Go |
| **Kubernetes ValidatingAdmissionPolicy** | — | **ADOPT AS PRECEDENT.** GA in v1.30. Model-free CEL policy over structured data, in-process | the whole L5 argument | its cost constants are in source, not docs (NOT-FOUND) |
| **pandera** | MIT ✔, 4.4k★ | **ADOPT as a host-function implementation** | L5 bulk column checks | not the predicate language; no UNCHECKED |
| **Great Expectations (GX Core)** | Apache-2.0 | **REJECT as verdict substrate** | expectation *catalogue* as a design reference | `catch_exceptions=True → success=False` collapses UNCHECKED into FAIL |
| **Soda Core / SodaCL** | **Elastic License 2.0** ✔ (read verbatim) | **REJECT — licence** | SodaCL YAML as a syntax reference only | "may not provide the software to third parties as a hosted or managed service" |
| **Deequ / PyDeequ** | Apache-2.0 | EVALUATE | constraint *suggestion* is a genuine L3 alternative with no model | Spark |
| **Frictionless / Cerberus / Pointblank** | MIT / ISC / MIT | EVALUATE (Pointblank first) | Pointblank's `EVAL` column is the nearest existing UNCHECKED | none carry a reason vocabulary |
| **Z3** | MIT | **ADOPT for L4** | degeneracy proof, subsumption, counterexample witnesses | `unknown` on string fragments ⇒ treat as UNCHECKED; host functions are uninterpreted |
| **Soufflé** | UPL-1.0 | EVALUATE | L6 cross-table set relations | second toolchain |
| **OPA / Rego** | Apache-2.0, CNCF graduated | REJECT (readability + Go) | — | revisit only if the stack moves to Go |
| **Starlark / JSONLogic / JMESPath / SpEL** | — | REJECT / REJECT / **ADOPT for provenance pointers** / REJECT (RCE) | JMESPath names the cell a predicate read | — |
| **Drools / GoRules ZEN / json-rules-engine / Nools** | Apache-2.0 / MIT / NOT-FOUND / NOT-FOUND | REJECT all | ZEN's JDM tables are a Screen-3 UI reference | chaining destroys per-predicate attribution |
| **VTL 2.2 (SDMX)** | spec; ESCB engine EUPL | REJECT as language, **ADOPT its operator vocabulary** | naming the shapes of a regulatory validation rule | JVM; implementations on the 1.1 draft |
| **Abraham & Erwig 2009, TSE 35(1):94–108** | paper | **ADOPT — the fault taxonomy** | L4 fault seeding: 17 operators, and 46.8% irreversible | 15 sheets / 542 cells, small and 2009 |
| **Petrović et al., TSE 2021 / arXiv:2102.11378** | paper (CC-BY) | **ADOPT — the suppression discipline** | L4 scoring and reporting | code mutants, Google's corpus; 85%→11% does not transfer numerically |
| **Madeyski et al., TSE 40(1):23–42** | paper | ADOPT — use the AEMG family | L4 equivalent-mutant handling | 2014 |
| **BART, PVLDB 9(2):36–47** | paper | **EVALUATE — closest existing system** | L4 generator design; detectable/non-detectable split | relational data with declared constraints, not workbooks |
| **JENGA (EDBT 2021)** | OSS | EVALUATE | corruption-API shape | ML-serving oriented |
| **SQLMutation / Mutant Swarm** | papers/OSS | EVALUATE | if predicates ever compile to SQL | SQL-only |
| **MutaSQL (DBTest 2020)** | paper | **ADOPT — but for L6, not L4** | metamorphic relation design | it mutates queries, not data |
| **XBRL US DQC + Xule/Arelle** | licence NOT-FOUND | **ADOPT the process; EVALUATE the tooling** | L4 test 3 (their FP research), L7 (versioning, effective dates) | XBRL/US-GAAP only; no IFSCA analogue |
| **gVisor + seccomp** | NOT-FOUND | **ADOPT** | L0/L1 parser tier | does not prevent a wrong verdict |
| **Pyodide / RestrictedPython / Firecracker / E2B / wasmtime** | MPL-2.0 / — / — / — / NOT-FOUND | REJECT / REJECT / REJECT-for-now / REJECT (data residency) / EVALUATE | wasmtime's deterministic fuel if we ever compile the evaluator | see Part B |
| **mutmut / cosmic-ray** | BSD-3-Clause, 1.4k★ / MIT | **ADOPT — for OUR code only** | host functions, L1 inducer, profile checker | they mutate code; they are not L4 test 1 |

---

# PART E — WHAT THIS CHANGES ABOUT THE DESIGN

**1. L5 gets a language, and the language choice is what makes the coverage number real.**
Adopt **CEL over a two-document fact model, in a three-slot envelope (`applicable`/`expr`/`witness`),
with a mandatory pre-flight key check.** Coverage is computable *only because* the language has no
variables — this is not a preference, it is the constraint that makes the brief's headline metric a
derived quantity rather than an assertion. Every alternative that is more expressive makes the product's
central number an estimate.

**2. Delete "Great Expectations / pandera / Soda Core / dbt / Deequ — L5 substrate — do not rebuild" and
replace it.** None of them has a third verdict value. GX actively converts *could-not-check* into
*failed*. **The check library need not be rebuilt; the verdict model must be built, because it does not
exist anywhere in the ecosystem.** And **Soda Core is Elastic License 2.0** and cannot be embedded in a
hosted product at all — a licence error in the brief's §6.2 table.

**3. The sandbox problem largely disappears, and what remains moves upstream.** With a restricted
language there is no model-generated Python to contain. The exposed surface is **L0/L1's `.xlsx` parser**,
not L5. Harden the parser tier with gVisor + seccomp + no network + zip/XML bomb guards; leave the
evaluator as an ordinary process, because CEL *is* the sandbox. Also: stop repeating that "Pyodide is
unmaintained" — **CVE-2026-5752 is against Cohere Terrarium**, and Pyodide is a 14.8k★ MPL-2.0 project
with active governance. The real lesson (Grist, GHSA-7xvx-8pf2-pv5g, CVSS 9.1, patched 20 Jan 2026) is
that **WASM-of-CPython is not a security boundary**, which is a stronger and more useful claim.

**4. L4 test 1 must be respecified: it is data fault seeding, not code mutation testing.** mutmut/PIT/
Stryker belong in a different paragraph (mutating *our* host functions and *our* schema inducer). The
right citation is **Abraham & Erwig, IEEE TSE 35(1):94–108, 2009**, whose **17 spreadsheet mutation
operators are the fault taxonomy the brief was writing from scratch** — including **FRC**, which is
literally "formula overwritten by a constant."

**5. The mutation-score formula must change, and the replacement is strictly better.**
`MS = |killed| / (|mutants| − |equivalent|)` requires an undecidable term. Replace it with
**`KR = K/O`**, where `O` is the count of mutants *measured by recalculation* to change at least one
reported value. **This is only possible because our mutants are data**: "observable" is a diff, whereas
"equivalent" is a theorem. Abraham & Erwig measured **3,512 of 7,500 (46.8%)** of comparable mutants as
producing no observable change — so a kill rate over generated mutants understates every predicate by
roughly half, variably by operator mix. Report `K/O`, the per-fault-class vector, and the unobservable
rate `U/G`, always with integers.

**6. L4 needs a control arm, and it does not have one.** Seeding faults only into fields a predicate
reads gives a flag-everything predicate a perfect kill rate. **Seed a 10% control sample into fields the
predicate does not read and count spurious firings.** This is L4 test 2 done empirically, and it directly
addresses the brief's own §3.1 finding (best model F1 65.4 vs a flag-everything baseline ≈66.2, with no
constant baseline reported in the paper).

**7. The brief's formula census is wrong in the design's favour, and how it is wrong is a third
self-demonstration.** The workbook has **505 formula-bearing cells, not 294**; 294 is the count of
formula *strings*, because **211 shared-formula followers are stored as `<f t="shared" si="N"/>` with no
text**. Checkable relations are **138/505 = 27.3%**, not 38/294 = 13%. Pure carries are **223/505 =
44.2%**. Cross-sheet at **195/294 = 66.3%** is confirmed exactly. **This is a third silent false negative
from a deterministic program, from the same XML-shape assumption family as §4.4's — and it is worth more
to the pitch than the corrected number is.**

**8. L3's "authoritative criterion source" claim must be downgraded to "available criterion source", and
here is the proof.** `'1. Introduction'!D17` — *"Total No. of Schemes of the FME authorised by IFSCA"* —
is `SUM(D18:D20)`, and those three COUNTIFs pattern-match only 7 of the 9 terms in the template's own
scheme-type vocabulary. **"Special Situation Fund" and "Family Investment Fund" are counted by nothing.**
A predicate mined from that formula would pass a wrong filing and fail a right one. **The regulator's
template contains a defect that our system catches in one line** — which is simultaneously the best demo
in the build and the reason the L4 gate is load-bearing rather than decorative.

**9. There is a cheap, model-free, 5× coverage increment sitting in the file.** The workbook ships **15
controlled vocabularies** on the `Dropdown` sheet and enforces **3** list-type data validations, all four
defined names pointing only at the Yes/No/NA column. One parameterised predicate family takes enforcement
from 3 to 15. **And the `Dropdown` sheet is the only unprotected sheet in the workbook** — so vocabularies
must always resolve against the *pinned blank template*, never against the submission. Put this in the
two-day build.

**10. The "no analogue exists" claim needs qualifying, and qualifying it makes the pitch better.** The
**XBRL US Data Quality Committee** has run a versioned, publicly-reviewed, false-positive-gated rule
registry over regulated financial filings for about a decade, in Xule on Arelle, and states verbatim that
*"Every draft rule is tested by running it against historical corporate filings … to make sure that they
are flagging errors appropriately and not generating false positives"* because *"the risk is too high
that a filer will be led astray."* **They gate for false positives; they do not publish a per-rule
measured false-failure rate next to each finding, and they publish no coverage denominator.** Our claim
becomes: *the quantified, per-rule, coverage-declaring version of a discipline a US financial-reporting
body already practises qualitatively.* Smaller, defensible, and it now has a named precedent to point at.

**11. One concrete numeric requirement that falls out of the language choice.** CEL has no decimal type.
The filing is denominated in **USD Million to two decimal places**. **L1 must scale monetary values to
integer micro-units** before they enter the fact model, or every arithmetic predicate acquires a
floating-point false-failure rate we did not choose and cannot attribute. This is a schema requirement,
and it is cheap only if done at the start.

---

# PART F — OPEN QUESTIONS

1. **Can a model write CEL as well as it writes Python?** The brief's settling experiment (9.1) is
   specified for "executable checks". This lane changes the target language, which changes the
   experiment's difficulty in an unknown direction. **Argument for easier:** a 20-production grammar over
   a declared key set, with the schema in the prompt, is a far smaller output space than arbitrary Python,
   and constrained decoding over the grammar is straightforward (the brief's L2 already plans
   outlines/XGrammar). **Argument for harder:** CEL is far rarer in pretraining corpora than Python.
   **Run 9.1 with both targets and report the two rates separately.** This is a one-line change to the
   experiment that doubles what it settles.
2. **Does recalculation of a mutated `.xlsx` reproduce Excel's values exactly?** LibreOffice headless is
   the plan, and `_xlfn.AGGREGATE` appears in `'1. Introduction'!C92:E101`. If LibreOffice and Excel
   disagree on any cell, the observability filter is measuring the wrong thing. **Positive control
   required before any kill rate is quoted.**
3. **What is the actual licence at `xbrl.us/dqc-license`?** NOT-FOUND. If it is permissive, the DQC rule
   corpus is a ready-made training and evaluation set for L3 on a *financial filing* domain — the only
   one I found anywhere.
4. **Are there filed IFSCA workbooks anywhere?** Unchanged from the brief (§9.2) and still the largest
   structural weakness. Everything in Part C's scoring carries the `SYNTHETIC-TEAM-FILLED` label until
   this changes.
5. **Does `celpy` pass the CEL conformance test suite?** NOT-FOUND on its repo page. `cel-expr-python`
   wraps the official C++ and therefore inherits conformance by construction. If `celpy` diverges on
   error semantics specifically, our error-absorption guard (§A.6.4) may behave differently between the
   two implementations. **Run the conformance suite against both before committing.**
6. **Is the `D17` COUNTIF defect present in the other 6 prescribed workbooks?** I checked only the FME
   format. Same method, ~20 minutes, and it would turn one finding into a pattern.
7. **What are Kubernetes' actual CEL cost constants?** NOT-FOUND in documentation; they are in source. We
   need our own budget, calibrated on our own workbook, not theirs — but theirs is a sanity reference.
8. **Does the equivalent/unobservable rate on *our* fault taxonomy resemble Abraham & Erwig's 46.8%?**
   Their operator mix and ours differ (we add F12–F14 and drop several formula-structure operators).
   **Measure it; do not assume it.**

---

# PART G — WHAT I COULD NOT CHECK

- **NVD's own record for CVE-2026-5752** — HTTP 502 twice. Used a vendor vulnerability database instead
  and labelled it SECONDARY at the point of use.
- **Licence files** for wasmtime, gVisor, Firecracker, Drools, json-rules-engine, Nools, and
  `xbrl.us/dqc-license` — all NOT-FOUND rather than assumed.
- **The `celpy` conformance claim** — no statement found on the repo page.
- **The exact Kubernetes CEL cost constants** — described in docs, not numbered there.
- **Powell/Baker/Lawson's spreadsheet-error field-audit numbers** — the primary PDF's text layer would not
  yield clean quotes, so the Panko–Halverson figures in §C.3 are SECONDARY and carry no denominators I
  could verify. Do not put them on a slide as measured.
- **BART's exact detectability definitions** — same problem; the PDF text layer was unusable.
- **VTL 2.2's reference-manual body** — read the landing pages and repo descriptions only.
- **Whether any of the 7 other prescribed workbooks shares the `D17` defect** — not attempted.
