# L14 — BUILD PATH AND APPLICATION STACK

**Lane:** the build plan and the application-layer technology decisions.
**Compiled:** 10 August 2026. **Operator scripts:** `/Users/abishaikc/Gift/research/scripts/`.

**Warrant key used throughout:**
`VERIFIED-AT-SOURCE` = I opened the primary source or ran the code myself ·
`SECONDARY` = a credible source describes it, I did not re-derive it ·
`UNVERIFIED` = could not check.

**Coverage denominator for the live-web half of this lane:** the session's WebSearch budget
(200/200) was exhausted before this lane began. Every live check below was therefore done with
**WebFetch against a named primary URL**. That means I could verify things I could *name*
(PyPI JSON endpoints, the Anthropic pricing page, Fly.io's pricing page) and could **not** do
discovery (e.g. "what is the best current open-weight coding model"). Where discovery was
required, the answer below is `NOT-VERIFIED` and a decision *procedure* is given instead of a
recommendation. This is called out again in §6.3 and in Open Questions.

---

## PART 0 — THE SHORT VERSION

1. **The two-day demo is already built, and it is not a mock.** L1→L5 runs end-to-end on the real
   published IFSCA FME workbook in **~30 milliseconds**, deriving **227 executable arithmetic
   predicates** and **53 validation predicates** with **zero model involvement**. Across all nine
   prescribed workbooks: **515 executable predicates**. Scripts are in this repo and reproduce.
2. **The coverage number is real and it is 63.3%**, measured against an honest denominator
   (3,747 filer-editable cells). 36.7% is declared UNCHECKED. Neither number is asserted.
3. **Three of the brief's §4.3 numbers need correcting**, and two of them fail *in exactly the way
   §4.4 documents* — a namespace-blind regex. One of the corrections is the most valuable finding
   in this lane (§1.6): **openpyxl, the standard Python xlsx library, has the identical blind
   spot** and reports the AML-CFT sheet as having zero data validations when it has five.
4. **No queue. No Postgres. No React.** The deterministic path is 30 ms; the durable state is a
   few hundred rows; the deliverable is a file, not an app. Each of those is argued against its
   runner-up in §5, not asserted.
5. **Model cost is not a constraint and is the wrong thing to optimise.** L3 runs *once per
   template version*, not per filing. Marginal model cost per filing on the workbook path is
   **$0.00**. Annual model spend to cover all ~868 filings is **under $200** (§6.4).
6. **The 16 August artifact should be a public GitHub repo whose README is the pitch** (§2).

---

## PART 1 — GROUND TRUTH FROM THE REAL ARTIFACTS

Everything in this part was produced by running code against the nine workbooks in
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/`. Warrant: **VERIFIED-AT-SOURCE**
(I wrote and ran the scripts; they are on disk and re-runnable).

### 1.1 Method, and why it is not the operator's method

`/Users/abishaikc/Gift/research/scripts/wb_probe.py`

The brief's §4.4 records that a formula regex `<f[ >][^>]*>` silently missed every
`<f>SUM(...)</f>`, producing "clean, confident, well-formed output that was wrong." I therefore
made a deliberate methodological choice and wrote it into the script header:

> Parse OOXML with lxml, never with a regex over the XML text. Count `<f>` **elements**, not
> `<f>text</f>` matches — a shared-formula dependent cell is `<f t="shared" si="N"/>` with no text
> node, and a regex requiring a closing tag with a text body silently drops every one of them.

This choice is what surfaced corrections §1.4 and §1.6. It cost nothing and it is the only reason
this lane is not a fourth instance of the same error.

### 1.2 Structural probe — all nine workbooks

`f(all)` = every `<f>` element. `f(body)` = elements carrying a formula body (**this is the number
the brief reports**). `shDep` = shared-formula dependents, which carry no body and which every
regex-based pass in this corpus has missed.

| workbook | sheets | cells | f(all) | f(body) | shDep | x-sheet | merged | dataVal | protected | labels (inst/distinct) | definedNames |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `Reporting_Format_for_Fund_Management_Entities_02012026` | 10 | 6,757 | **505** | **294** | 211 | 195 | 252 | **54** | 9/10 | 1,249 / 458 | 12 |
| `Updated___Quarterly_..._Capital_Market_Intermediaries_20260409` | 18 | 7,810 | 33 | 33 | 0 | 8 | 53 | 142 | 17/18 | 1,337 / 608 | 0 |
| `ALR_V2_3_20250808` | 9 | 2,889 | 645 | 246 | 399 | 35 | 77 | 7 | 9/9 | 314 / 264 | 0 |
| `AL_monthly_report_updated_final_20260717` | 4 | 4,215 | 161 | 49 | 112 | 6 | 36 | 10 | 3/4 | 782 / 118 | 1 |
| `Draft_ACAC_Format_20260605` | 13 | 3,793 | 112 | 9 | 103 | 0 | 111 | 0 | 0/13 | 843 / 632 | 0 |
| `IBU_Operations_Report_V2_3_20250808` | 8 | 961 | 7 | 7 | 0 | 7 | 36 | 4 | 8/8 | 216 / 159 | 0 |
| `ITFS_Monthly_report201220241626` | 2 | 732 | 32 | 32 | 0 | 11 | 82 | 16 | 1/2 | 108 / 92 | 0 |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808` | 3 | 397 | **0** | 0 | 0 | 0 | 2 | 1 | 3/3 | 147 / 143 | 0 |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved` | 9 | 1,708 | **0** | 0 | 0 | 0 | 95 | **0** | 0/9 | 295 / 268 | 0 |

Two workbooks (`EDR_1`, `IFSCA_Annual_Reporting_Format`) contain **zero formulas and, in the
latter case, zero data validations**. They are typed forms with no internal consistency structure
at all. Any coverage claim must be made per-template, never across the corpus — a point the
architecture does not currently make.

### 1.3 Formula classification — the brief's table reproduces exactly

FME workbook, of the 294 body-carrying formulas:

| class | count | % of 294 | brief §4.3 asserts | verdict |
|---|---:|---:|---:|---|
| pure cross-sheet carry-forward | **181** | 61.6% | 181 (62%) | **CONFIRMED** |
| IFERROR wrapper | **50** | 17.0% | 50 (17%) | **CONFIRMED** |
| SUM row/column total | **35** | 11.9% | 35 (12%) | **CONFIRMED** |
| IF conditional carry | **14** | 4.8% | 14 (5%) | **CONFIRMED** |
| other/ref (same-sheet cell refs) | **11** | 3.7% | 11 (4%) | **CONFIRMED** |
| COUNTIF scheme-type tally | **3** | 1.0% | 3 (1%) | **CONFIRMED** |
| **sum** | **294** | 100% | 294 | **CONFIRMED** |

The classification is exactly right. So is the interpretive claim built on it — *38 of 294 (13%)
express a checkable relationship; 181 (62%) copy a value.* Both survive.

The cross-workbook line in §4.3 also reproduces exactly, once you read it as *body-carrying*
formulas: FME 294/195 cross-sheet (66%) ✓; ALR 246/35 ✓; AL monthly 49/6 ✓; CMI quarterly 33/8 ✓;
ITFS 32/11 ✓; Draft ACAC 9/0 ✓; **IBU Operations Report 7 formulas across 961 cells** ✓ (exact).

### 1.4 CORRECTION 1 — "294 formulas" is 294 formula *bodies*; there are 505 formula *cells*

`verify_brief_43.py` output:

```
  formula ELEMENTS (all <f>)   : 505
    with a formula body        : 294   <- this is the brief's '294'
    shared-formula dependents  : 211   <- NOT counted by the brief
```

A shared formula is written once with `<f t="shared" ref="B7:B93" si="0">…</f>` and its dependents
are `<f t="shared" si="0"/>` — same computation, different cells, **no text node**. The brief's
294 is the count of distinct formula *expressions*; the count of *cells that compute something* is
505. Both are true statements about different quantities.

**Why it matters for the build, and it is not cosmetic:** the field graph has 505 derived cells,
not 294. A checker built to the 294 figure leaves 211 computed cells unmodelled — it would treat
them as free inputs and never notice when they disagree with their master. The same undercount
applies elsewhere and is larger in relative terms: ALR **645 vs 246** (399 dependents, 62% of the
sheet's computation missed), AL monthly **161 vs 49**, Draft ACAC **112 vs 9** (92% missed).

**Recommended restatement:** *"294 distinct formula expressions across 505 formula-bearing cells;
of the 294, 181 (62%) are pure cross-sheet carries and 38 (13%) express a checkable relationship."*

### 1.5 CORRECTION 2 — "35 data validations" is the main-namespace count; there are 54

```
  dataValidation split : main-namespace=35  x14-extension=19  total=54
  dataValidation by type: {'list': 22, 'decimal': 13, 'whole': 11, 'date': 6, None: 2}
```

I then proved the mechanism rather than inferring it:

```
REGEX PROOF for the 35-vs-54 gap:
  operator regex  r'<dataValidation[ >]'      -> 35   (misses the namespace prefix)
  x14-prefixed    r'<x14:dataValidation[ >]'  -> 19
  namespace-aware lxml total                  -> 54
```

Excel writes validations that use newer features (list sources on another sheet, some custom
formulas) into the `x14` extension block as `<x14:dataValidation>`. The pattern `<dataValidation`
cannot match `<x14:dataValidation`. **This is the same failure as §4.4, third instance, and it is
the second one caused by a namespace-blind regex.**

### 1.6 CORRECTION 3 — the finding that should change the build: **openpyxl shares the blind spot**

This is the most important result in the lane. I ran openpyxl 3.1.5 against the same file and
compared per sheet with the namespace-aware lxml count:

| sheet | openpyxl sees | lxml main | lxml x14 | **lost** |
|---|---:|---:|---:|---:|
| 1. Introduction | 8 | 8 | 9 | **9** |
| 2. Summary | 3 | 3 | 0 | 0 |
| 3. Portfolio | 11 | 11 | 2 | **2** |
| 4. Investors | 3 | 3 | 0 | 0 |
| 5. PMS | 6 | 6 | 0 | 0 |
| 6. Complaints | 1 | 1 | 1 | **1** |
| **7. AML-CFT** | **0** | **0** | **5** | **5** |
| 8. Compliance Status | 2 | 2 | 2 | **2** |
| 9. Compliance Report | 0 | 0 | 0 | 0 |
| Dropdown | 1 | 1 | 0 | 0 |
| **TOTAL** | **35** | **35** | **19** | **19** |

> openpyxl sees 35 of 54 data validations.
> It silently drops all 19 x14-extension validations (35% of the total).

**openpyxl arrives at exactly the operator's 35.** Two independent tools — a hand-written regex and
the most widely used Python spreadsheet library — produce the identical wrong number by the
identical mechanism, with no error, no warning, and no way to tell from the output that anything
was missed.

And the worst cell in that table is the one that matters most: **openpyxl reports the AML-CFT sheet
as having no data validations at all.** It has five. A compliance tool built on openpyxl would
report full validation coverage of the anti-money-laundering section while checking none of it.

**Build consequence, and it is a hard rule:** *L1 schema induction must read raw OOXML through
lxml. openpyxl may be used for convenience reads and for writing mutants, never for deriving the
schema.* This is now encoded in `wb_probe.py` and `predicate_harvest.py`.

**Pitch consequence:** the brief asks for evidence that "the system found nothing" is not
information. §4.4 offers two operator-authored bugs. This is strictly better evidence, because the
tool is not ours, it is the ecosystem default, it is used by a very large number of people, and
the failure lands on the AML sheet. It needs no explanation of the operator's own code.

### 1.7 CORRECTION 4 — "854 label instances" is right, with a denominator the brief omits

```
all shared-string cells   : 1249
  ... with len(text) > 3  :  854   <- brief's 854
  ... distinct            :  486
  ... distinct with len>3 :  458
```

854 is **CONFIRMED** as *shared-string cells whose text exceeds three characters* — the filter is
in the operator's own `cls.py` (`if i < len(ss) and len(ss[i])>3`). The unfiltered count is 1,249.
"494 distinct strings" is **CONFIRMED** exactly (the `sharedStrings.xml` `<si>` count); note that
486 are distinct after whitespace normalisation, so eight are duplicates differing only in spacing.

Field shape, on distinct labels: **"Whether…" yes/no = 16, CONFIRMED exactly.** Labels containing
"date" = 19 against an asserted 15 — **QUALIFIED**, my substring test is looser than whatever the
operator used. I could not reproduce the "84 numeric/amount" figure with any defensible
heuristic (my nearest attempt returns 268 label instances / a different distinct count) —
**UNVERIFIED**, and it should not be quoted until the counting rule is written down.

### 1.8 CONFIRMED without qualification

| brief §4.3 claim | measured | verdict |
|---|---|---|
| 10 sheets | 10 | **CONFIRMED** |
| 6,757 cells | 6,757 | **CONFIRMED** (exact) |
| 494 distinct strings | 494 | **CONFIRMED** (exact) |
| 9 of 10 sheets protected | 9 | **CONFIRMED** |
| 294 formulas | 294 bodies | **CONFIRMED** as bodies (see §1.4) |
| formula classification, all six rows | all six | **CONFIRMED** (exact) |
| cross-workbook formula/cross-sheet counts, all seven | all seven | **CONFIRMED** (exact) |
| IBU Operations Report: 7 formulas across 961 cells | 7 / 961 | **CONFIRMED** (exact) |
| ITFS and AL ship a validation sheet, and it is the only unprotected sheet | ITFS 1/2 protected, `Validation Sheet` unprotected; AL 3/4, `0 Validation` unprotected | **CONFIRMED** |

**New fact not in the brief:** all nine protected sheets carry a real password hash,
`algorithmName="SHA-512"`. Protection is *not* encryption — every byte is readable without the
password. Reading is unimpeded; only writing through Excel's UI is gated. Confirmed by round-trip:
openpyxl loads, mutates and saves the file with protection intact and formulas preserved.

### 1.9 What a demo can compute TODAY, with zero model involvement

`/Users/abishaikc/Gift/research/scripts/predicate_harvest.py`

Every predicate below is *mechanically derived from the blank template's own OOXML*. No model, no
prompt, no API key. Each is directly executable.

| predicate class | derived from | FME | all 9 workbooks |
|---|---|---:|---:|
| `cross_sheet_equality` | pure cross-sheet carry formula | 181 | **196** |
| `membership` | `list` validation, vocabulary resolved | 20 | **95** |
| `sum_identity` | `SUM(range)` formula | 35 | **78** |
| `numeric_bound` | `decimal` validation | 13 | **48** |
| `integer_bound` | `whole` validation | 11 | **45** |
| `date_bound` | `date` validation | 6 | **24** |
| `same_sheet_equality` | same-sheet cell ref | 11 | **14** |
| `conditional_required` | `custom` validation (an `IF(...)` condition) | 0 | **12** |
| `tally_identity` | `COUNTIF` formula | 3 | **3** |
| **TOTAL** | | **280** | **515** |

**515 executable predicates across nine real regulated workbooks, zero model involvement.**
The FME workbook alone yields 280.

**The 20 membership predicates matter more than their count suggests**, and they correct a
pessimistic reading in the brief. §4.3 says "only 3 list-type with a named vocabulary." Measured:
of 22 list validations, **20 resolve to a real enumerable vocabulary** — the resolver follows
defined names (`Choicelist`, `YesNolist`, `YesNoNA`) and cross-sheet ranges into the `Dropdown`
sheet and reads the actual strings. Only 2 fail to resolve. Resolved examples, read off the file:

```
[1. Introduction] D10   |V|=3  ['Registered FME (Retail)', 'Registered FME (Non-Retail)', 'Authorised FME']
[1. Introduction] G54:G63 |V|=9 ['Venture Capital Scheme', 'Angel Scheme', 'Restricted Scheme (Category I)', …]
[3. Portfolio]  W88:W97… |V|=12 ['Equity shares listed or to be listed on Stock Exchange', 'Unlisted equity sh…']
[3. Portfolio]  I116:I126 M116:M126  n=210 cells  |V|=2  ['Yes','No']
[7. AML-CFT]    C13     |V|=3  ['Completed', 'In-progress', 'Not initiated']
```

The `3. Portfolio` row is the one to show a judge: **one derived predicate covers 210 cells** with
a two-value vocabulary. That is the whole thesis in one line — the check was already latent in the
artifact; nobody had extracted it.

**Recommended restatement of the §4.3 sentence:** *"35 data validations"* → *"54 data validations
(35 main-namespace, 19 in the x14 extension that regex- and openpyxl-based passes both miss), of
which 22 are list-type and **20 resolve to a real enumerable vocabulary**."*

### 1.10 Timing — this is why there is no queue

Measured on the operator's machine, cold, single process:

| step | time |
|---|---|
| L1 field-graph build from the blank FME template (lxml) | **28–44 ms** |
| clean-filing synthesis (511 cells, dependency-ordered) | **1 ms** |
| L5 evaluation of 227 arithmetic predicates | **sub-millisecond** |
| full structural probe, all 9 workbooks | well under 1 s |
| L4 mutation run: 19,782 mutants | **2.5 s (7,946 mutants/sec)** |
| openpyxl load (convenience path only) | 202 ms |
| openpyxl mutate + save a mutant workbook | 80 ms |

**The entire deterministic pipeline for one filing is ~30 milliseconds.** §5.2 draws the
architectural conclusion.

### 1.11 L4 test 1, run for real — and two bugs of my own, kept in the record

`/Users/abishaikc/Gift/research/scripts/l4_mutation_harness.py`

**First, a correction to the architecture.** L4 test 1 names *"mutmut, PIT, Stryker."* That is a
category error. I verified mutmut at source (PyPI JSON: **3.7.0, released 31 July 2026,
BSD-3-Clause, Python ≥3.10, requires `fork` so no native Windows** — VERIFIED-AT-SOURCE). What it
does: mutates **your Python source** and asks whether **your tests** fail.

| mutation-testing concept | classic (mutmut) | what L4 actually needs |
|---|---|---|
| program under test | your `.py` source | **the filed workbook (data)** |
| test suite | your pytest suite | **the admitted predicate set** |
| a mutant | source with one edit | **a filing with one cell perturbed** |
| "killed" | a test fails | **a predicate FAILs** |

L4's mutants are *data*, not code. So the L4 harness is ~200 lines of our own code over the cell
graph — which makes the two-day build **easier**, not harder, and removes a dependency. mutmut is
still worth having, one level up: mutate the *predicate implementations* to test the harness. It
is not the L4-test-1 tool.

**Second, my own two bugs, and I am keeping them in the file on purpose.** Version 1 of the harness
printed this:

```
  TOTAL                3574     3574       3     100.0%
  MUTATION SCORE  MS = killed / (mutants - equivalent) = 3574 / (3574 - 3) = 100.1%
```

A 100.0% kill rate and a mutation score of **100.1%** — arithmetically impossible, and it printed
cleanly, confidently and well-formed. Two independent defects:

- **Bug A (denominator).** Equivalent mutants were `continue`d before the `mutants` counter
  incremented, so they were in neither numerator nor denominator, and `killed/(mutants−equivalent)`
  exceeded 1.
- **Bug B, the serious one (degenerate baseline).** I sampled mutation sites *only from cells the
  predicates already read*. Perturbing only the cells a check reads cannot do anything but pass.
  **That is L4 test 2 — the degenerate-baseline failure — committed by the very harness meant to
  detect it.** The honest site set is every cell a filer can populate, so the run can measure the
  cells no predicate touches. Both fixes are commented in place in the script.

After the fix, the honest result:

```
  MUTATION RUN: 2826 sites x 7 operators in 2.5s  (7,946 mutants/sec)
  operator          mutants   killed   equiv  kill rate
  sign_flip            2826      511       0      18.1%
  scale_x10            2826      511       0      18.1%
  scale_div10          2826      511       0      18.1%
  off_by_one           2826      511       0      18.1%
  digit_transpose      2826      511       0      18.1%
  zero_out             2826      511       0      18.1%
  round_to_int         2826      508      22      18.0%
  TOTAL               19782     3574      22      18.1%
  MUTATION SCORE  MS = 3574 / (19782 - 22) = 18.1%
```

Every arithmetic operator kills at exactly the same rate, and that rate equals the fraction of
sites inside the field graph. That is the correct and expected behaviour for equality and sum
identities: *any* perturbation of a cell an identity reads breaks the identity, and no perturbation
of a cell it does not read can. Kill rate ≡ coverage, for this predicate class. The mutation score
is therefore not measuring predicate *quality* here — it is measuring predicate *reach*. That
distinction needs to be in the product's own vocabulary; it is not in the architecture today.

**This is a third self-demonstration, and unlike the first two it is not the operator's.** §4.4 has
two. §1.6 adds openpyxl's. This adds mine, in the tool built to prevent exactly this. Four
instances, three mechanisms, all producing clean confident wrong output from deterministic
programs. That is the pitch, and it now has a sample size.

### 1.12 The honest coverage fraction — 63.3%

`/Users/abishaikc/Gift/research/scripts/true_coverage.py`

My first coverage figure was **99.2%**, and it was circular: I had defined the denominator as
"cells in the predicate graph ∪ cells carrying a validation" — cells that already have a check.
A denominator built from the numerator cannot come out low. Third instance of the same
degenerate-baseline trap in one afternoon.

The honest denominator is **the field surface**: every cell the filer can actually type into. In a
protected sheet that is exactly the **unlocked** cells, recoverable from `styles.xml`
(`cellXfs → <protection locked="0"/>`), because Excel locks every cell by default and the template
author unlocks precisely the input cells. Measured:

```
  unlocked style ids in styles.xml         : 105
  protected sheets                         : 9 of 10
  cells present in the workbook            : 6757
  formula cells (not filer-editable)       : 505
  THE FIELD SURFACE (unlocked, non-formula): 3747 cells   <- the denominator

     arithmetic predicates (227)   :   271   ( 7.2% of field surface)
     validation predicates (53)    :  2329   (62.2%)
     UNION (280 predicates)        :  2373   (63.3%)
     UNCHECKED residue             :  1374   (36.7%)
```

Per sheet, the field surface is: Portfolio 1,698 · Investors 897 · PMS 480 · Introduction 371 ·
Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22.

**The demo headline: `63.3% of 3,747 fields settled — 1,374 declared unchecked`.** Computed, not
asserted, in 30 ms, with no model. And it sits strikingly close to the brief's independent
predicate-level 17/24 = 71%, arrived at by a different method on a different denominator.

**One caveat that must ship with the number, and it is an L4-test-2 finding.** The 62.2% carried by
validation predicates is *weaker per cell* than the 7.2% carried by arithmetic ones. Bound
predicates vary enormously in strength, and some are near-vacuous:

| workbook | bound predicates | near-vacuous (\|bound\| ≥ 1e12, i.e. "is a number") | substantive (e.g. `≥ 0`) |
|---|---:|---:|---:|
| FME | 24 | 2 (60 cells) | 22 (2,068 cells) |
| CMI quarterly | 61 | 18 (380 cells) | 43 (516 cells) |
| ALR | 6 | **5 (1,428 cells)** | 1 (54 cells) |
| ITFS | 2 | 0 | 2 (27 cells) |

The FME workbook is in good shape — 19 of its 24 bounds are a real `≥ 0` non-negativity
constraint. **ALR is not**: five of six bounds are `-100000000000000000`, which asserts only "this
is a number" over 1,428 cells. L4 test 2 must reject those at admission, and the coverage meter
must not count them. This is a per-template property, and it is the first concrete demonstration
that the qualification gate does real work rather than rubber-stamping.

### 1.13 Summary of corrections to brief §4.3

| # | claim | status | correct statement |
|---|---|---|---|
| 1 | "294 formulas" | **QUALIFIED** | 294 formula *bodies*; **505** formula-bearing cells (211 shared dependents) |
| 2 | "35 data validations" | **REFUTED** | **54** (35 main-namespace + 19 x14); the regex is namespace-blind |
| 3 | "only 3 list-type with a named vocabulary" | **REFUTED** | 22 list-type, **20 resolve to a real vocabulary** |
| 4 | "854 label instances" | **CONFIRMED** | with denominator: 854 of 1,249 shared-string cells, filtered `len>3` |
| 5 | "494 distinct strings" | **CONFIRMED** | exact; 486 distinct after whitespace normalisation |
| 6 | "10 sheets / 6,757 cells / 9 of 10 protected" | **CONFIRMED** | exact |
| 7 | formula classification (all six rows) | **CONFIRMED** | exact |
| 8 | cross-workbook counts (all seven) | **CONFIRMED** | exact |
| 9 | "16 Whether… yes/no" | **CONFIRMED** | exact, on distinct labels |
| 10 | "15 dates" | **QUALIFIED** | 19 distinct labels contain "date"; counting rule undocumented |
| 11 | "84 numeric/amount" | **UNVERIFIED** | not reproducible without the counting rule |
| 12 | L4 test 1 tools "mutmut, PIT, Stryker" | **REFUTED** | those mutate code; L4 mutates data — write ~200 lines |

---

## PART 2 — THE 16 AUGUST DELIVERABLE

The form takes **one URL**, choice of: demo video / prototype / Figma / GitHub / website / deck.
Judging is on *problem relevance, innovation and creativity, solution feasibility, team capability,
presentation and pitch quality*.

### Recommendation: a public **GitHub repository whose README is the pitch**

One URL, and it is the only option that discharges four of the five criteria simultaneously:

| criterion | how the repo carries it |
|---|---|
| solution feasibility | the code runs; `make demo` reproduces 63.3% coverage on the real published workbook |
| team capability | the commit history and the code are the evidence; nothing else on the list is inspectable |
| problem relevance | the README leads with the four silent-failure instances (§1.6, §1.11, §4.4 ×2) |
| innovation and creativity | the Unchecked panel and the computed coverage fraction, both visible in the output |
| presentation and pitch quality | GitHub renders README.md as a formatted page with images and tables — a deck that happens to be executable |

**Against each runner-up, on its merits:**

- **Demo video.** Best on pitch quality alone, worst on feasibility and capability — a judge cannot
  tell a real pipeline from a screen recording of a mock, and that is precisely the distinction
  this project exists to make. Losing it in the artifact would be self-refuting. *Put a 60-second
  screen capture in the README instead;* it is strictly additive and costs one URL less.
- **Deck.** Every applicant sends a deck. It is the weakest possible evidence of capability, and it
  cannot demonstrate that the numbers are computed rather than authored.
- **Figma.** Signals a design exercise. The differentiator here is measurement, not layout.
- **Website.** Another deploy target, another thing to be down at 09:00 on the 16th, and it
  reveals less than the repo.
- **Working MVP behind a login.** Judges will not create accounts.

**Set the two adjacent form fields to match the evidence, not to flatter it:** Current Stage =
**Prototype**; Have you built anything = **Prototype**. Both are defensible — L1→L5 runs
end-to-end on the real artifact — and neither overclaims, which matters because the repo is
inspectable.

### The README, in order

1. **One sentence:** *A regulated filing checker that reports what it did **not** check.*
2. **The four silent failures**, in a table — two operator bugs, openpyxl's AML-CFT blind spot, and
   my own degenerate-baseline harness bug. Lead with openpyxl: it is not our code.
3. **The measured result**, as a fenced block of real program output: 280 predicates, 63.3%
   coverage of 3,747 fields, 1,374 unchecked, 30 ms, zero model calls.
4. **A screenshot of the report** showing the coverage meter and the Unchecked panel. **No green
   tick anywhere** — the one design commitment, visible in the artifact itself.
5. **`make demo`** — clone, run, reproduce, against the workbook as published on `ifsca.gov.in`.
6. **What is not built yet**, named plainly (§7). A do-not-build list in the README is itself
   evidence of the discipline being pitched.
7. **The 60-second capture** (asciinema or GIF).

### Hard constraints on the repo before 16 August

- **Public**, MIT or Apache-2.0, no credentials in history.
- **Ships the nine IFSCA workbooks or a fetch script** — the demo must reproduce on a judge's
  laptop. Prefer the fetch script plus recorded sha256 for each file, so provenance is checkable
  and the repo stays small.
- **No model call anywhere on the demo path.** The 16 August artifact should be the deterministic
  half only. It is the stronger claim, and it cannot fail live.
- **Pin the record straight:** cite the corrected numbers from §1.13, not the brief's originals.

---

## PART 3 — THE 21–22 AUGUST TWO-DAY BUILD

**Scope thesis:** L0 + L1 + L5 + a hand-authored predicate set + the report UI, end-to-end on a
real published artifact with zero model involvement. Per Part 1, most of this is already done, so
the two days should be spent on **the surfaces and the honesty machinery**, not the parser.

Dependency-ordered. Each task lists its acceptance test. **The hard cut line is between T9 and
T10.** Everything above the line is the demo; everything below is optional polish that must be
abandoned without hesitation if the line is reached.

### Day 1 — the pipeline and the artifact

| # | task | depends on | acceptance test |
|---|---|---|---|
| T1 | **L0 ingest.** Fetch the nine workbooks from `ifsca.gov.in/Download`, content-address each by sha256, write `templates/<sha256>.xlsx` + a manifest row. | — | `ingest.py` run twice produces byte-identical manifests; every sha256 matches the recorded value |
| T2 | **L1 schema induction** (lxml only — see §1.6). Emit `TemplateSchema{cells, merges, formulas, validations, protection, unlocked_mask, version_hash}`. | T1 | On the FME sha, emits exactly 505 formula cells, 54 validations, 3,747 field-surface cells. **Assert these constants in a test** so a regression is loud |
| T3 | **Predicate harvest.** `TemplateSchema → 280 executable predicates` (nine classes, §1.9). | T2 | 280 for FME, 515 across all nine; each predicate serialises to JSON and round-trips |
| T4 | **L5 execution engine.** `(filing, predicate_set) → per-predicate PASS / FAIL / UNCHECKED(reason)`, closed reason vocabulary, weakest-input provenance. | T3 | Synthetic clean filing → 0 FAIL; single seeded fault → exactly the predicates reading that cell FAIL |
| T5 | **Coverage computation** against the *field surface* denominator (§1.12), never the graph. | T2, T4 | Prints `63.3% of 3,747`; a unit test asserts the denominator is derived from `styles.xml` unlocked mask, **not** from the predicate set |
| T6 | **Run manifest + content addressing.** Every run emits `{template_sha, filing_sha, predicate_set_root, code_git_sha, python_version, tool_versions}`. | T4 | `verify` re-derives the report from the manifest and byte-matches |
| T7 | **Self-contained HTML report** (§5.4): one file, inline CSS/JS, no external requests. Coverage meter, failures expanding to cells + clause, **Unchecked panel**, run manifest in a `<details>` footer. | T4, T5, T6 | Opens from `file://` with networking off; renders on a phone; contains **no green tick** — grep the output for `✓`/`check` and fail the build if present |

### Day 2 — the honesty machinery and the surfaces

| # | task | depends on | acceptance test |
|---|---|---|---|
| T8 | **L4 mutation harness** (data mutants, not code — §1.11). Per-predicate kill rate, MS with the equivalent-mutant term, and the surviving-mutant residue. | T4 | Reproduces MS = 18.1% on 19,782 mutants; the site set is the field surface, and a test asserts it is **not** the predicate graph |
| T9 | **L4 test 2, the degenerate-baseline gate.** Reject near-vacuous bounds (§1.12). Every admitted predicate carries `mutation_score` + `admitted_at`. | T8 | ALR's five `-1e17` bounds are **rejected**; FME's 19 `≥ 0` bounds are **admitted**; coverage recomputes downward for ALR |
| — | **=========== HARD CUT LINE — the demo is complete above this ===========** | | |
| T10 | **Drop screen** — one control, POST a workbook, render the report. | T7 | Works from a phone browser on the venue wifi |
| T11 | **Predicate library screen** — clause, code, mutation score, admission date, filterable. | T9 | 280 rows render in <200 ms; no virtualisation library |
| T12 | **Coverage-over-time** — replay predicate admission in order, animate the meter, annotate each step. | T9 | Renders from a static JSON log; no live backend |
| T13 | **L7 attestation stub** — sign the manifest, `verify` checks the signature. | T6 | Tampering with one cell changes the report sha and `verify` fails |
| T14 | **L6 metamorphic probes** — 3 relations only (row reorder, zero-row insert, duplicate consolidation). | T4 | Each relation holds on the clean filing and is violated by a targeted mutant |

**Cut-line discipline.** T1–T9 is the whole demo: the pipeline runs, the report renders, the
coverage is computed, and the qualification gate visibly rejects bad predicates. T10–T14 make it
prettier and broader. If Day 2 morning is lost to a venue problem, **ship T1–T9 and present from
the HTML file and the terminal.** T14 (L6) is the most novel work in the programme (§9.3 of the
brief) and is deliberately *below* the line for the hackathon — two days is not enough to author
metamorphic relations honestly, and doing it badly would poison the most publishable component.

**What is explicitly NOT in the two days:** any model call, any database, any auth, any deploy
pipeline, any queue. See §7.

---

## PART 4 — THE RESIDENCY, 1 SEPTEMBER – 30 OCTOBER 2026

Eight and a half weeks, up to ₹1,00,000 milestone-linked. Five milestones, each with a
**measurable acceptance test that can fail**. Milestone 1 is deliberately the settling experiment,
because the brief's Part 11 is explicit that the standing bias is to elaborate rather than to find
out whether the thing is over.

### M1 — Weeks 1–2 (1–14 Sep): run experiment 9.1 and let it decide L3

The brief pre-registers the threshold: *take 10 obligations from the FM Regulations, ask a model
for executable checks, score by L4's three tests; **if fewer than 3 of 10 survive, L3 is deleted
and predicates are hand-authored.*** That is the first thing the residency does, before anything is
elaborated on top of it.

- **Acceptance test:** 10 obligations scored by L4's three gates, results published with the
  per-candidate mutation score and false-failure rate, **and the go/no-go decision recorded in the
  repo on the date it was taken**, whichever way it goes.
- **Failure is a valid, funded outcome.** If fewer than 3 survive, M1 ships "L3 deleted, predicates
  hand-authored" and M3 changes shape. Say this to the mentors in week 1, so the result cannot be
  renegotiated in week 6.
- **Deliverable:** `experiments/9.1/` — inputs, raw model outputs, scores, decision, all
  content-addressed.

### M2 — Weeks 2–4 (8–28 Sep): the corpus, and its declared weakness

The brief calls this the design's largest structural weakness: filed returns are not public.

- Build the **clean corpus**: ≥30 correctly-filled FME workbooks constructed by the team, each
  passing all 280 predicates by construction.
- Build the **dirty corpus** by mutation, which is free (§1.11) — target ≥20,000 labelled mutants.
- Extend the field-surface computation to all nine templates; publish a per-template coverage
  table (this will be embarrassing for `EDR_1` and `IFSCA_Annual_Reporting_Format`, which have zero
  formulas and, in the latter case, zero validations — publish it anyway).
- **Acceptance test:** every false-failure rate the system reports carries the string
  *"measured on a synthetic clean corpus of N filings; not a measurement of real filings"* —
  **enforced by a unit test that fails the build if an FFR is rendered without its provenance
  string.** Discipline that is not mechanised does not survive week 6.

### M3 — Weeks 4–6 (22 Sep–12 Oct): L4 as a product, and L3 only if M1 permitted it

- Harden L4 into the admission gate: all three tests, per-predicate `mutation_score`, `ffr`,
  `admitted_at`, and FFR interaction across admitted predicates (SPADE's contribution).
- Predicate registry versioned as a Merkle root over admitted rows; a report names its registry
  root and re-derives exactly.
- **If and only if M1 passed:** L3 synthesis behind the gate, Batch API, offline.
- **Acceptance test:** a predicate whose error rate is unknown **cannot** be admitted — attempt it
  in a test and assert the rejection. This is what makes the coverage claim true by construction
  rather than by discipline, and it should be provable in one test.

### M4 — Weeks 6–8 (6–24 Oct): L6 metamorphic probes — the publishable component

The brief's §9.3: *the most novel component and the most likely to produce a publishable result.*
Author ~10 relations for a fund return: row reorder ⇒ NAV unchanged; zero-value holding inserted
⇒ NAV unchanged; identical positions consolidated ⇒ NAV unchanged; reporting unit scaled ⇒ every
derived total scales proportionally; currency round-trip within tolerance.

- **Acceptance test, and it is the number the residency is judged on:** *how far does L6 move the
  63.3% coverage fraction, and how many of the brief's 7 "not decidable" predicates become
  relation-checkable?* Publish the before/after with the relation that moved each one. A relation
  that moves nothing is reported as moving nothing.

### M5 — Weeks 8–8.5 (20–30 Oct): attestation, reproduction, and the demo day artifact

- L7: sign template hash + filing hash + registry root + per-predicate mutation score and FFR.
- **Acceptance test:** a third party clones the repo, runs `verify <report.html>`, and gets a
  byte-identical re-derivation on a different machine. If it does not reproduce, it does not ship.
- Freeze the demo-day artifact as a single signed HTML file that opens with no network.

**Milestone-to-funding mapping** (each is objectively checkable, so the tranche cannot be argued):
M1 = experiment run and decision recorded · M2 = corpus published with enforced provenance strings
· M3 = admission gate provably rejects unmeasured predicates · M4 = before/after coverage delta
published · M5 = third-party reproduction succeeds.

---

## PART 5 — APPLICATION STACK

Every choice is argued against its runner-up. Where a measurement decided it, the measurement is
cited.

### 5.1 Backend language — **Python**. Confirmed, but for a corrected reason.

The lane brief guessed Python is "near-forced (openpyxl, pandera, conformal libraries, mutation
tooling)". **Confirmed as the right answer, and two of those four reasons are wrong.**

- **openpyxl is a reason to be careful, not a reason to choose Python** — §1.6 shows it silently
  drops 35% of the validations and blanks the AML-CFT sheet. The real dependency is **lxml**, which
  is excellent, C-backed, and gave a full parse in **28 ms**.
- **mutation tooling does not transfer** — mutmut mutates code, L4 mutates data (§1.11). We write
  those ~200 lines ourselves in any language.
- **pandera** (0.32.1, MIT — version VERIFIED-AT-SOURCE via the PyPI JSON API; the release date the
  fetch returned was inconsistent with the current version line and I did not re-verify it, so
  treat **the date as UNVERIFIED**) is a genuine reason but a weak one: it validates dataframes,
  and our unit is a cell graph, not a dataframe.
- **The conformal-prediction ecosystem is the real forcing reason**, and it is L2-only.

The decisive argument is simpler and it is measured: **the entire deterministic core is 30 ms of
lxml and dictionary arithmetic.** Python is fast enough by three orders of magnitude, and the
scientific/statistical ecosystem is where the L2/L4 work will actually live.

**Runner-up: TypeScript with SheetJS/ExcelJS.** Rejected on a specific risk, not on taste — the
x14 namespace trap in §1.6 is a *library* failure, not a Python failure, and I have no evidence
about which JS libraries share it. Migrating would mean re-deriving §1.6 from scratch for a new
library, on a deadline, with the AML sheet as the failure mode. Not worth it.

**Python core with a thin TypeScript edge: not needed, and the reason is §5.4** — the deliverable
is a file, not an app, so there is no rich client to write. If a framework becomes necessary
post-residency, add SvelteKit at the edge and keep the Python core untouched.

### 5.2 API framework and job execution

**Framework: FastAPI.** Versions checked live at the PyPI JSON API today (VERIFIED-AT-SOURCE):

| | version | released | licence | Python |
|---|---|---|---|---|
| **FastAPI** | **0.141.1** | (date not exposed in fetch) | MIT | ≥3.10 |
| **Litestar** | **2.24.0** | 11 June 2026 | MIT | ≥3.8, <4.0 |

**Why FastAPI over Litestar — and note this is not a performance argument.** Litestar is genuinely
the better-engineered framework for a large application: msgspec serialisation, layered DI,
class-based controllers, OpenAPI 3.1. Every one of those advantages pays off at a scale this
project will not reach inside 60 days. Against that: the job is ~5 endpoints over a 30 ms
computation, so framework throughput is *irrelevant by three orders of magnitude*; and the binding
constraint on a hackathon-to-residency codebase is **how quickly a mentor, a teammate, or a judge
can read it**. FastAPI wins that by a wide margin, and `StaticFiles`, `StreamingResponse` for SSE,
and generated OpenAPI are each one line. Choose Litestar if the team already knows it — the
switching cost is the only real cost either way.

**Django-ninja: rejected.** It brings the ORM, settings, migrations and app registry for a system
whose durable state is a directory of content-addressed blobs plus one registry table. The Django
apparatus is a liability here, not an asset — it would put a migration between us and a
reproducible report.

**Job execution: no queue. Synchronous, and it is not close.** Measured (§1.10): L1 28 ms +
synthesis 1 ms + L5 sub-ms ≈ **30 ms**; the whole 19,782-mutant L4 run is 2.5 s. The lane brief
asks whether a queue is needed for a sub-60-second job; the real job is **sub-100-millisecond**, so
the question does not arise. Plain request/response.

- **SSE:** only where there is genuinely something to stream — the coverage-over-time replay
  (T12) — and even that can render from a static JSON log. Not needed for the check itself.
- **When a queue *would* be justified:** the L3 synthesis sweep and large L4 campaigns. Both are
  **offline, batch, and not in the request path**, so the answer there is the Anthropic **Batch
  API** (§6.4) plus a `Makefile`, not Celery. If in-process queuing is ever truly needed, use a
  Postgres- or SQLite-backed job table before adding Redis — do not add a broker to a system whose
  unit of work is 30 ms.

### 5.3 Storage, versioning, and exact re-derivation

**SQLite, not Postgres.** Single writer, single node, entire dataset well under 10 MB, no
concurrent-write story to tell. Postgres wins on concurrency this project does not have and costs a
service to run, back up and reproduce. Decisive extra reason: **SQLite is a file, so it can be
hashed and named in the run manifest** — which is exactly what L7 needs. A Postgres cluster cannot
be content-addressed.

- **Blob store:** a directory of `sha256`-named files. Already in use — every workbook in Part 1
  carries its sha256 (FME = `7d9a1960085785ee…`). No S3, no minio.
- **Predicate registry:** one row per predicate —
  `(id, template_sha256, clause_ref, code, code_sha256, kind, mutation_score, ffr, ffr_corpus_n, ffr_corpus_kind, admitted_at, admitted_by)`.
  Append-only; supersession by a new row, never an update. `ffr_corpus_kind` exists so the
  synthetic-corpus caveat (§M2) is a **column**, not a habit.
- **Registry version** = Merkle root over the sorted `code_sha256` of admitted predicates. A report
  names one root; the root pins the exact check set.
- **Exact re-derivation.** Every report embeds a run manifest:
  `{template_sha256, filing_sha256, registry_root, code_git_sha, python_version, lxml_version, tool_versions}`.
  `verify <report.html>` re-runs from the manifest and asserts a byte-identical report. That single
  command is the strongest thing to hand a supervisor, and it is T6 on Day 1.

### 5.4 Frontend — the correct answer is that the deliverable is a **file**, not an app

The five screens are Drop, Report, Unchecked panel, Predicate library, Coverage-over-time.

**Primary recommendation: the report is a single self-contained HTML file** — inline CSS and JS,
no external requests — generated by the backend. This is not a way of dodging the framework
question; it is a better answer to it, on four grounds the frameworks cannot match:

1. **It survives the venue.** Opens from `file://` with the wifi down. On demo day that is not a
   nice-to-have.
2. **It is phone-safe by construction.** The lane brief flags that judges may open it on a phone.
   One HTML file with a responsive stylesheet has no build target, no hydration, no bundle.
3. **It is the attestation artifact.** L7 signs a hash of *something*. A file has a hash. A
   single-page app does not.
4. **It is emailable**, which is how a compliance officer will actually share a report with a
   supervisor.

**For the interactive shell** (Drop, Predicate library, Coverage-over-time) during the two-day
build: **Jinja2 templates from FastAPI + Tailwind compiled to a static stylesheet + ~50 lines of
vanilla JS.** No SPA.

**Runners-up, each rejected on a specific ground:**

- **Next.js + shadcn/ui:** shadcn/ui requires React, and React requires a build, a second deploy
  target and an API boundary that a server already rendering HTML does not need. It would become
  the project — the exact failure the lane brief warns about.
- **SvelteKit:** the right choice *if* a framework is required — single build artifact, no RSC
  complexity, `adapter-static` can even emit the self-contained report. Still not required for five
  screens. **This is the one to adopt post-residency.**
- **Remix:** no advantage here over SvelteKit, and its data-loading model assumes a server round
  trip per route, which fights the offline-file requirement.
- **Streamlit:** cannot render a test-run-shaped report without fighting it, and the rerun model
  makes the coverage-over-time animation awkward. Also cannot produce an offline artifact.
- **Reflex / NiceGUI:** both bind the UI to a live WebSocket session. That is precisely wrong for
  an artifact that must survive being emailed, hashed and signed.
- **TanStack Table:** overkill. The predicate library is ≤515 rows; a plain `<table>` with a filter
  input renders in under 200 ms. Revisit only if the registry passes ~5,000 rows.
- **A diff or DAG view of the field graph:** genuinely valuable — 196 cross-sheet edges is a real
  graph — but it is a *residency* task (M4-adjacent), not a two-day task. If it happens, render
  static SVG server-side; do not add D3 or Cytoscape to the two-day build.

**The one non-negotiable UI rule, mechanised:** no green tick anywhere. Make it a build-time grep
(T7) rather than a code-review convention, because a convention will not survive week 6.

### 5.5 Deployment — a single container, and a laptop that does not need it

**Recommendation: one Docker container, deployed to Fly.io, with the laptop as the real
fallback.** Fly.io pricing checked live today (VERIFIED-AT-SOURCE, fly.io/docs/about/pricing):
`shared-cpu-1x` **256 MB ≈ $2.02/mo**, **512 MB ≈ $3.32/mo**, **1 GB ≈ $5.92/mo`, region-dependent;
**new accounts get no free allowance** — the legacy free tier is closed to organisations created
after 7 October 2024. Budget **512 MB ≈ $3.32/month ≈ ₹290/month**, which is noise against
₹1,00,000.

**Why single-container over the alternatives:**

- **Vercel + Railway: rejected.** Two deploy targets, two failure modes, two dashboards, and
  Vercel's serverless model actively fights a long-lived predicate registry file and a
  content-addressed blob directory. Splitting a 30 ms computation across a network boundary buys
  nothing.
- **Nothing-but-a-laptop: rejected as the *primary*, mandatory as the *fallback*.** A URL in the
  application form must resolve for a judge who is not in the room. But the demo itself must never
  depend on the network — which the self-contained HTML report (§5.4) already guarantees.
- **Kubernetes, or anything with a control plane: not a serious option** at this scale and would
  itself be evidence against the feasibility criterion.

**Demo-day protocol, and it is the reason for the whole §5.4 design:** open the signed HTML report
from disk. The deployed URL is for the judges who read the application, not for the stage.

### 5.6 Observability and reproducibility

Deliberately minimal — the system is 30 ms and single-node, so distributed tracing would be
theatre.

- **Run manifest** on every report (§5.3), rendered in the report footer where a human can read it.
- **Content addressing** end to end: template, filing, predicate code, report.
- **`verify` command** — re-derive and byte-compare. This *is* the observability story: the
  question a supervisor asks is not "what was the p99 latency" but "can I get this same answer
  again," and `verify` answers it.
- **Structured JSONL run log**, one line per predicate evaluation: `{predicate_id, verdict, reason,
  cells_read, elapsed_us}`. Feeds the coverage-over-time screen and costs nothing.
- **What not to add:** OpenTelemetry, Sentry, Prometheus, a metrics backend. Add the first of these
  only when a real user is on the system, which will not happen before 30 October.

---

## PART 6 — MODEL CHOICE

### 6.1 Current line-up and pricing — checked live today

**VERIFIED-AT-SOURCE**, `https://platform.claude.com/docs/en/about-claude/pricing`, fetched
10 August 2026. Prices per million tokens (MTok), USD.

| model | model ID | base input | 5m cache write | 1h cache write | cache hit | output |
|---|---|---:|---:|---:|---:|---:|
| Claude Fable 5 | `claude-fable-5` | $10 | $12.50 | $20 | $1 | $50 |
| **Claude Opus 5** | `claude-opus-5` | **$5** | $6.25 | $10 | **$0.50** | **$25** |
| Claude Opus 4.8 | `claude-opus-4-8` | $5 | $6.25 | $10 | $0.50 | $25 |
| **Claude Sonnet 5** *(through 31 Aug 2026)* | `claude-sonnet-5` | **$2** | $2.50 | $4 | **$0.20** | **$10** |
| Claude Sonnet 5 *(from 1 Sep 2026)* | `claude-sonnet-5` | $3 | $3.75 | $6 | $0.30 | $15 |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | $3 | $3.75 | $6 | $0.30 | $15 |
| **Claude Haiku 4.5** | `claude-haiku-4-5` | **$1** | $1.25 | $2 | **$0.10** | **$5** |

> Verbatim: *"Introductory pricing of $2/$10 per million input/output tokens is in effect through
> August 31, 2026, after which the standard pricing of $3/$15 per million input/output tokens will
> take effect."*

**Directly relevant to this residency: Sonnet 5's introductory price expires on 31 August 2026 —
the day before the residency starts.** Any L2 cost modelled on $2/$10 must be re-modelled at $3/$15
for September onward. Budget at the standard rate.

**Batch API: 50% off both input and output** — verbatim: *"asynchronous processing of large volumes
of requests with a 50% discount on both input and output tokens."* Opus 5 batch = **$2.50 / $12.50**;
Sonnet 5 batch = $1/$5 intro, $1.50/$7.50 standard; Haiku 4.5 batch = $0.50/$2.50.

**Prompt caching multipliers** (verbatim): 5-minute write **1.25×** base input, 1-hour write **2×**,
cache read **0.1×**. *"These multipliers stack with other pricing modifiers, including the Batch API
discount."* Both discounts compose — which matters for L3 (§6.4).

**Long context:** *"Claude 4.6 and later models … include the full 1M token context window at
standard pricing."* No long-context premium. Context windows are **SECONDARY** (from the bundled
`claude-api` reference, cached 2026-06-24, not re-derived): 1M for Fable 5 / Opus 5 / Opus 4.8 /
Sonnet 5 / Sonnet 4.6; 200K for Haiku 4.5. The 1M figure is corroborated at source by the
long-context pricing paragraph above.

**One caution that bears on token budgeting** (verbatim from the pricing page): *"Claude 4.7 and
later models … use a newer tokenizer … This tokenizer produces approximately 30% more tokens for
the same text."* Opus 5 is in that family. Any token estimate carried over from a Sonnet 4.6-era
measurement must be re-baselined with `count_tokens`, not multiplied by a guess.

### 6.2 Recommendation per model-bearing step

**Only L2 and L3 contain a model.** Everything in Part 1 — all 515 predicates, the coverage
fraction, the mutation harness — runs with none.

**L3 predicate synthesis → `claude-opus-5`, via the Batch API.**

The architecture's own thesis decides this: *put the model only where generation is hard and
verification is cheap.* L3 generates many candidate predicates; L4 adjudicates every one of them
deterministically against mutation kill, the degenerate baseline, and FFR. That is the ideal place
to spend on the strongest model, because a bad candidate costs a rejection, not an error. Three
supporting reasons: L3 is **offline and per-template-version**, so latency is irrelevant and Batch
applies; the template schema is a large stable prefix, so prompt caching applies; and the failure
mode being defended against is a *plausible-but-wrong* check, which is exactly what capability buys
down.

*Runner-up, Sonnet 5:* the honest position is that **M1 (experiment 9.1) should settle this
empirically** by measuring admitted-candidates-per-rupee for both. Cost is so low either way
(§6.4) that capability should decide until measurement says otherwise.

**L2 fact extraction → `claude-haiku-4-5` for the bulk pass, escalating to `claude-sonnet-5` when
the conformal prediction set is not a singleton.**

L2's job is `→ Fact{key, value, unit, provenance, confidence}`, and L1 already rejects any key not
in the induced schema deterministically. That hard guard means L2's failure modes are cheap:
a wrong key is *caught*, and a non-singleton prediction set *abstains*. The economically right
shape is therefore a cheap high-volume pass with a capable escalation path. Use **structured
outputs** (`output_config.format`) to guarantee shape — supported on Haiku 4.5, Sonnet 5 and
Opus 5 — and remember it guarantees shape, never truth.

**Crucially, L2 is not on the critical path for the workbook itself.** Extraction from a `.xlsx` is
deterministic — we read the cells. L2 is needed only for unstructured attachments (PDFs). For a
filing with no attachments, **the marginal model cost is exactly zero.**

### 6.3 Open-weight comparison — NOT-VERIFIED, and here is the decision rule instead

I **could not** check current open-weight options. WebSearch was exhausted at 200/200 before this
lane began, and WebFetch requires a URL I can name — which makes discovery ("what is the strongest
current open-weight model for code generation") impossible without guessing URLs, and a guessed URL
is exactly the fabrication this brief forbids. **Recording this as NOT-VERIFIED rather than
producing a plausible answer from training memory, which for an August 2026 model line-up would
almost certainly be stale.**

What can be said without checking anything, because it follows from the architecture:

> **L4 adjudicates every candidate deterministically. Therefore L3 model choice cannot affect
> correctness — only yield.** A weaker model proposes more rejects; it cannot smuggle an
> unqualified predicate past the gate, because admission requires a measured mutation score and
> FFR.

That converts an unanswerable question into a measurable one, and the measurement is cheap:

1. Fix the L4 gate and the 10 obligations from M1.
2. Run each candidate model over the identical prompt set.
3. Report **admitted predicates per unit cost** and **admitted per 100 candidates**.
4. Adopt whichever wins; re-run when the line-up changes.

Do this **inside M1**, where the harness already exists. Note the one structural advantage
open-weight would bring: many-candidate generation is embarrassingly parallel and locally
reproducible, which suits an attestation story. That is a reason to *run the measurement*, not a
reason to assume the outcome.

### 6.4 Cost per filing — the number is smaller than the framing suggests

Assumptions stated so the arithmetic is auditable, and flagged as MODELED, not measured. Token
counts are **estimates**, not `count_tokens` measurements; the §6.1 tokenizer caution applies.

**L3, per template version — one-time, not per filing.** 24 obligations; ~6,000-token cached
schema prefix; ~600 fresh tokens of clause text; ~1,500 output tokens per obligation.

| path | per obligation | × 24 obligations |
|---|---:|---:|
| Opus 5, no caching, no batch | $0.0705 | **$1.69** |
| Opus 5, cached prefix | $0.0435 | **$1.04** |
| **Opus 5, cached + Batch (50%)** | **$0.0218** | ****$0.52**** |

Add a one-time 5-minute cache write of 6,000 tokens at $6.25/MTok = **$0.0375**. **Round figure:
about $0.55 per template version, and there are nine templates.** The entire predicate-synthesis
bill for the whole IFSCA prescribed-format corpus is **under $6**, and it is paid once per template
revision — not per filing.

**L2, per filing — only when there are unstructured attachments.** A 20-page PDF ≈ 25,000 input
tokens, ~3,000 output tokens:

| model | per filing | × 868 filings/year |
|---|---:|---:|
| Haiku 4.5 | $0.040 | **$35** |
| Sonnet 5 (standard $3/$15, i.e. from 1 Sep 2026) | $0.120 | **$104** |
| Opus 5 | $0.200 | **$174** |
| Sonnet 5 via Batch | $0.060 | **$52** |

**The headline, and it should be said plainly on stage:**

- **Marginal model cost per filing on the workbook path: $0.00.** The 280 predicates, the coverage
  fraction and the verdict involve no model at all.
- **Annual model spend to process the entire measured population of ~868 filings: under $200**,
  even routing every attachment through Opus 5.
- **The cost that matters is not inference. It is the L4 qualification corpus** — the ≥30
  correctly-filled workbooks in M2, which is human time, and which no amount of model spend
  substitutes for.

---

## PART 7 — DO NOT BUILD

Ranked by how likely each is to be built anyway.

1. **No agent loop, no cross-step memory, no retry-until-it-passes.** The brief's own evidence:
   adding memory made all 10 models worse at long horizons; reasoning fine-tuning makes abstention
   24% worse; `pass^k` collapses ~60%→~25% over 8 attempts. Two short stateless model calls, both
   adjudicated by programs. If a demo needs an agent to be impressive, the demo is wrong.
2. **No green tick, no "all clear", no PASS summary badge.** The single design commitment.
   Mechanise it as a build-time grep (T7), not a convention.
3. **No queue, no Redis, no Celery, no worker pool.** The job is 30 ms (§1.10).
4. **No Postgres, no ORM, no migrations** before there is a second writer.
5. **No React, no Next.js, no shadcn/ui, no component library** in the two-day build. It becomes
   the project.
6. **No auth, no multi-tenancy, no user accounts** before 30 October. Judges will not sign up.
7. **No openpyxl in the L1 path — ever.** §1.6. Convenience reads and mutant writing only.
8. **No rebuilding Great Expectations / pandera / Soda Core.** They are the L5 substrate if we
   need one; their gap is that assertions are hand-authored and there is no coverage declaration,
   and *that gap is our product* — do not re-implement the part they already do.
9. **No mutmut/PIT/Stryker for L4 test 1.** Wrong tool class (§1.11). ~200 lines of our own.
10. **No LLM-as-judge anywhere in the verdict path.** LLM judges detect false success at
    AUROC ≤0.65. A model may never be the final adjudicator.
11. **No rules-as-code framework** (Catala, OpenFisca, Blawx). Killed in the brief: zero financial
    regulations encoded anywhere, 16★, no commit since June 2024.
12. **No metamorphic relations in the two days.** Below the cut line deliberately (T14) — it is the
    most publishable component and rushing it would poison it.
13. **No coverage number computed against a denominator derived from the predicate set.** I made
    this mistake twice in one afternoon (§1.11 Bug B, §1.12). Assert the denominator's provenance
    in a test.
14. **No FFR quoted without its corpus provenance string.** Enforced by a failing test (M2), not by
    remembering.

---

## PART 8 — WHAT THE PROTOTYPE MUST DO ON STAGE, UNAMBIGUOUSLY

On stage, on a laptop with the wifi switched off, the presenter drops the real
`Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` — the file as published
on `ifsca.gov.in`, sha256 `7d9a1960085785ee…`, filled with one deliberately corrupted cell — onto a
single control, and within one second the screen shows a report shaped like a test run whose
headline is a coverage fraction and never a tick: **"63.3% of 3,747 fields settled · 1,374
unchecked"**; the failure expands to show both the corrupted cell and the cell it disagrees with,
the clause the check implements, and that check's own measured false-failure rate carrying the
words *"on a synthetic clean corpus of N filings, not a measurement of real filings"*; the presenter
then opens the Unchecked panel and reads out that 1,374 fields were **not** checked and *why* —
no oracle exists, requires counterparty data, requires judgment — because that panel, not the
failure, is the product; then opens the Predicate library to show all 280 checks with their
mutation scores and admission dates, and points at the five ALR bounds the qualification gate
**rejected** for being satisfiable by any number at all; and finally runs `verify` on the report,
which re-derives it byte-for-byte from its embedded run manifest, and states the two facts that
make the whole thing land — that **not one model was called** at any point in what was just shown,
and that the same regulator-published workbook silently reports zero data validations on its
anti-money-laundering sheet when read with the standard Python spreadsheet library, which is
exactly the class of confident, well-formed, wrong answer this system exists to make impossible to
give.

---

## PART 9 — WHERE EACH ASSET FITS IN L0–L7, AND WHERE IT STOPS

| asset | licence / version | fits at | where it stops |
|---|---|---|---|
| **lxml** | BSD, 6.1.1 (installed) | **L0, L1** — the only safe OOXML reader (§1.6) | No spreadsheet semantics: no formula evaluation, no style resolution. We wrote the cell-graph layer ourselves |
| **openpyxl** | MIT, 3.1.5 (installed) | **L0 convenience reads; L4 mutant writing** | **Silently drops all 19 x14 validations, 35% of the total, and blanks the AML-CFT sheet.** Must never derive the schema. Round-trip also shrinks the file 3.66 MB → 66 KB, discarding embedded objects |
| **`wb_probe.py`** (ours) | ours | **L1** — structural induction | Reports structure, asserts nothing about a filing |
| **`predicate_harvest.py`** (ours) | ours | **L1→L3 boundary** — 515 predicates with no model | Only harvests what the template already encodes. Any check the template does not encode needs L3 or a human |
| **`l4_mutation_harness.py`** (ours) | ours | **L4 test 1** | Numeric mutation operators only; no string/date/structural mutants yet. Measures *reach* for identity predicates, not quality (§1.11) |
| **`true_coverage.py`** (ours) | ours | **L5** — the coverage fraction | Denominator is the unlocked-cell mask, which assumes the author locked correctly. Unprotected templates (ACAC, Annual Report) have no mask and need a different denominator |
| **FastAPI** | MIT, 0.141.1 ✓ | the L5→UI seam | Not a job system. Anything beyond a request/response goes to a Makefile, not a broker |
| **Litestar** | MIT, 2.24.0 ✓ | same seam, runner-up | Better engineering, no benefit at this scale (§5.2) |
| **SQLite** | public domain | predicate registry + run manifests | Single writer. Revisit only with a second concurrent writer |
| **pandera** | MIT, 0.32.1 (version ✓, **date UNVERIFIED**) | possible **L5** substrate | Validates dataframes; our unit is a cell graph. Assertions hand-authored, no coverage declaration |
| **mutmut** | BSD-3-Clause, 3.7.0, 31 Jul 2026 ✓ | **meta-L4 only** — mutating our predicate implementations | **Not the L4-test-1 tool** — mutates code, not data (§1.11). Needs `fork`, so no native Windows |
| **Claude Opus 5** | `claude-opus-5`, $5/$25 ✓ | **L3** synthesis, offline + Batch | One-time per template version. Never in the verdict path |
| **Claude Haiku 4.5 / Sonnet 5** | $1/$5 · $3/$15 from 1 Sep ✓ | **L2** extraction from attachments | Not needed for the `.xlsx` path at all — that extraction is deterministic |
| **Anthropic Batch API** | 50% off ✓ | **L3** | Not for interactive work; not available with fast mode |
| **Fly.io** | 512 MB ≈ $3.32/mo ✓ | deployment | No free allowance for post-Oct-2024 orgs. Demo must not depend on it |
| **Self-contained HTML report** (ours) | ours | **L5 output + L7 attestation target** | A file, so it can be hashed and signed — which no SPA can be (§5.4) |
| **in-toto / Sigstore** | Apache-2.0 | **L7** | **UNVERIFIED** — not re-checked live this session. Mature but nothing financial-specific |
| **CycloneDX `compositions.aggregate`** | ECMA-424 | **L7** prior art for the coverage declaration | Software/crypto assets only; no financial analogue — the gap being filled |
| **QuantMind** | MIT (per brief) | proposed **L0** | **UNVERIFIED this session.** Brief §9.7 asks whether its shapes handle a protected xlsx with merged headers. **This lane makes that question moot for the two-day build** — L0/L1 are ~200 lines of lxml, already written and measured at 28 ms. Do not adopt a 2.3k-star dependency to save 200 lines |

---

## PART 10 — WHAT THIS CHANGES ABOUT THE DESIGN

**1. The two-day build is not a build; it is an assembly.** L1→L5 already runs end-to-end on the
real artifact in 30 ms with 280 predicates and a 63.3% coverage fraction. Both days should go to
the *surfaces* and the *honesty machinery* — the Unchecked panel, the qualification gate visibly
rejecting bad predicates, and `verify` — not to the parser. This is a straight reallocation of the
scarcest resource in the programme.

**2. L4's tool list is wrong, and fixing it removes a dependency.** mutmut/PIT/Stryker mutate
*code*; L4 mutates *data*. The harness is ours, it is ~200 lines, it runs at 7,946 mutants/second,
and it exists now. ARCHITECTURE.md §L4 test 1 should be amended.

**3. Mutation score measures predicate *reach*, not predicate *quality*, for identity predicates.**
Every arithmetic operator killed at exactly 18.1%, identical to the field-graph coverage fraction —
because any perturbation of a cell an identity reads breaks it, and no perturbation of a cell it
does not read can. The architecture treats mutation score as a quality signal. For this predicate
class it is a coverage signal, and the product's vocabulary needs to say which.

**4. The coverage denominator is a first-class design decision, and it is easy to get wrong in the
flattering direction.** I got it wrong twice in one afternoon — once in the mutation harness (Bug
B) and once in the coverage calculation (99.2%) — both times by deriving the denominator from the
predicate set. The honest denominator is the *unlocked-cell field surface* from `styles.xml`.
This should be a named, tested invariant, because it is the number the whole product rests on.

**5. The strongest evidence for the pitch is not ours.** §4.4 offers two operator-authored bugs,
which invite the reply "then write better code." **openpyxl** — the ecosystem default, not our code
— has the identical namespace blind spot, arrives at the identical wrong number of 35, and reports
the **AML-CFT sheet as having zero data validations when it has five**. Lead with that. It needs no
defence and no explanation of our own code.

**6. Four instances now, three mechanisms.** Two operator bugs (§4.4), openpyxl's blind spot
(§1.6), and my own degenerate-baseline harness (§1.11) — all deterministic programs, all producing
clean, confident, well-formed wrong output. The claim "the system found nothing is not information"
has moved from anecdote to a pattern with a sample size and a taxonomy.

**7. Per-filing model cost is $0.00, and this reframes the pitch away from AI economics.** L3 is
per-template-version, not per-filing (~$0.55 per template with caching + Batch). The entire annual
inference bill for all ~868 filings is under $200. The expensive input is the human-built clean
corpus. Do not pitch cost savings on inference; pitch the boundary.

**8. Coverage is a per-template property and must never be averaged.** `EDR_1` has zero formulas;
`IFSCA_Annual_Reporting_Format` has zero formulas *and* zero validations, so its mechanically
derivable coverage is 0%. `ALR` looks well covered until L4 test 2 rejects five of its six bounds
for being satisfiable by any number at all. A single corpus-wide coverage number would be
meaningless — and would be exactly the kind of silent all-clear the product exists to prevent.

**9. Sonnet 5's introductory pricing ends 31 August 2026 — the day before the residency starts.**
Any L2 budget modelled at $2/$10 must be re-modelled at $3/$15. Small in absolute terms, but it is
the kind of dated fact that survives into a slide unchallenged.

**10. The frontend question dissolves.** The right deliverable is a single self-contained HTML file
— it survives the venue, renders on a phone, can be emailed, and is the only form of the report
that can be *hashed and signed*, which L7 requires. A single-page app cannot be content-addressed.
That is an architectural argument, not a preference, and it deletes an entire category of two-day
work.

---

## PART 11 — OPEN QUESTIONS

1. **Open-weight models for L3 are NOT-VERIFIED** (WebSearch exhausted at 200/200; WebFetch cannot
   do discovery). Resolve inside M1 by measuring admitted-predicates-per-rupee against Opus 5 —
   §6.3 gives the procedure.
2. **The GIFT IFIH portal could not be confirmed live.** `giftifih.getkruu.com/apply` returned
   **HTTP 404** to WebFetch, and the root served only an SPA shell titled *"KYF Programme - Kruu
   Youth Fellowship"* with no application content — consistent with the brief's note that the page
   renders client-side. **This does not establish that applications have closed**, but it is six
   days from the stated deadline and the operator should open the form in a real browser today.
3. **"84 numeric/amount fields" (§4.3) is not reproducible** without the counting rule. Either
   document the rule or withdraw the number.
4. **What is the field-surface denominator for an *unprotected* template?** `Draft_ACAC` (0/13
   protected) and `IFSCA_Annual_Reporting_Format` (0/9) have no unlocked-cell mask, so §1.12's
   method does not apply. Needed before any cross-template coverage claim.
5. **Do the 19 x14 validations differ in kind from the 35 main-namespace ones**, or is the split
   purely an Excel serialisation artifact? Affects whether the blind spot is systematically biased
   toward a particular check class — the AML-CFT result hints that it might be.
6. **Are there filled FME workbooks anywhere public?** The whole FFR story depends on this and the
   answer is currently no (brief §9.2). Worth one direct ask alongside the §9.6 email to IFSCA's
   Division of Investment Funds.
7. **in-toto / Sigstore not re-verified this session** — confirm current versions and licences
   before M5 commits to a signing format.
8. **`pandera` release date UNVERIFIED** (§5.1) — the version is right, the date the fetch returned
   is not consistent with it. Re-check before depending on it.
