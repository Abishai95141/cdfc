## II.0 — How to read this part

Every number carries a **warrant** and a **denominator**: `MEASURED` (we ran it on the artifact),
`VERIFIED-AT-SOURCE` (a primary source was opened and quoted), `SECONDARY` (reported by a source we did
not re-open), `DERIVED` (arithmetic over other numbers), `UNVERIFIED` (asserted nowhere we checked). A
derived number never claims a stronger warrant than its weakest input. Every decision below is written as
**DECIDED**, with the alternative it beat and the reason, or as **OPEN — USER DECISION** with the exact
question. There are no implicit choices in this part.

Three global renames are normative from here and are not repeated at every occurrence:

| Was | Is | Why |
|---|---|---|
| `coverage`, `coverageFraction`, `GET /v1/coverage/history` | **`settledFraction`**, `GET /v1/settled-fraction/history` | "coverage" is the conformal guarantee's word and it appears three pages away in that sense |
| `micro_units`, "integer micro-units" | **`MILLI_USD_MILLION`** — an `int64` count of 10⁻³ USD Million, 1 unit = USD 1,000, `12.34 → 12340`, half-ulp = 5 units, `τ(n) = 5n` | Two definitions differing by 10³ were live, and every tolerance in the design is expressed in units. **DECIDED** in favour of the definition that derives from guidance C111's two-decimal USD Million quantum. Alternative it beat: "micro-units", which had no derivation |
| `METAMORPHIC` (as a `method` value) | **`DIFFERENTIAL`** | Metamorphic testing requires a re-executable system under test; a filed workbook is a record. A correct small claim beats a large unbuildable one |

---

## II.1 — THE LAYERS, REVISED

### 1.0 What is actually built — the ruling, verbatim

> **"Schema induction, predicate harvest, arithmetic evaluation and the coverage denominator are built and
> reproduce in ~30 ms. Template binding, pre-flight, closure, canaries, attestation and `verify` are
> specified and not built."**

("Coverage denominator" in that ruling is the settled-fraction denominator; the rename above applies.) Any
sentence of the form *"L1→L5 runs end-to-end"* overstates it and must not be used. The honest form is:
*schema induction, predicate harvest and arithmetic evaluation run end-to-end in ~30 ms (MEASURED, single
run, cold, single process, one workbook); the verdict model, closure, canaries and attestation are
specified and unbuilt.*

Likewise: **the verdict path is specified to make zero model calls, and the assertion is listed as a build
gate; the gate is not yet written.** It is not yet a property of a running system.

### 1.1 The layer table

| Layer | Exact input | Exact output | Model? | Status |
|---|---|---|:--:|---|
| **L0 INGEST** | `bytes` (filing, blank template, instrument PDFs) + `HTTP GET spec` (register) | `ContentAddressedBlob{sha256_original, media_type, retrieved_at, origin_uri, parse_a, parse_b, agreement{field→bool}}`, `RegisterSnapshot{sha256, fetched_at, endpoint, records[]}`, `ExtractionManifest` | **No. Never.** | **PARTIALLY BUILT** — readers A and B built; container guard and the agreement check specified |
| **L1 SCHEMA INDUCTION** | the **blank template** blob, pinned by hash — never the filing | `TemplateSchema{template_sha256, fields{stable_key→Field}, vocabularies, carry_edges, field_surface[], manifest}` | No | **BUILT** — 28–44 ms (MEASURED) |
| **L1b CLAUSE GRAPH** | instrument PDFs | `Instrument{frbr_uri, as_at, pdf_sha256}` + `Clause{eId, text, charspan, bbox, provisos[], xrefs[]}` + `Amendment{src, tgt, effective_date, resolved}` | No (Docling is a parser, not a judge) | **SPECIFIED — nothing of L1b is built** |
| **L2a STRUCTURAL EXTRACTION** | filing blob + `TemplateSchema` + `RegisterSnapshot` | `Fact{key, value, unit, provenance_anchor, warrant=DETERMINISTIC}` | No | **BUILT** (fact-table construction) |
| **L2b DOCUMENT EXTRACTION** | unstructured attachment bytes + `TemplateSchema.stable_keys()` | `Fact{…, warrant=MODEL_EXTRACTED}` or an abstention | **Yes — contingency only** | **SPECIFIED / GATED** (see the pre-flight gate below) |
| **L3 CANDIDATE PROPOSAL** | `TemplateSchema` + `ClauseGraph` + the 505-cell native formula graph | `CandidatePredicate[]` — the §II.4 envelope, containing **CEL**, not Python | **Yes — the only model in the system, build time only** | **SPECIFIED** (the settling experiment is unrun) |
| **L4 QUALIFICATION** | `CandidatePredicate` + `TemplateSchema` + `CleanCorpus{provenance, n}` + `FaultModel{version}` | `AdmittedPredicate` with a **required** `qualification` block, **or** a typed `rejection` row | No | **PARTIALLY BUILT** — see the gate-by-gate status in §II.4.3 |
| **L5 EXECUTION AND VERDICT** | `AdmittedPredicate[]` pinned by registry root + `Facts` + `TemplateSchema` | one `Item` per **cell** (§II.3) + the computed scope object | **No. Zero model calls.** | **PARTIALLY BUILT** — arithmetic evaluation built; pre-flight and closure specified |
| **L6 DIFFERENTIAL & INVARIANT PROBES** | the fact table + admitted relations + the pinned blank | per relation: `PASS / FAIL / INFORMATIONAL(advisory) / OUT_OF_SCOPE(precondition unmet)` | No | **SPECIFIED** |
| **L6.5 SELF-CHECK AND RESIDUE** | the filing, the admitted set with its stored witnesses, the L5 result | `{canaries_run, canaries_passed, dead_predicates[], residue: ResidueSet, run_state: VALID\|INVALID}` | No | **SPECIFIED** |
| **L7 ATTESTATION** | the L5 scope object + L6 results + L6.5 proof + every content hash + the registry root | DSSE envelope over an in-toto Statement v1, one self-contained `report.html`, `run.jsonl`, declared-lossy OSCAL projections, an RO-Crate evidence crate | No | **PARTIALLY BUILT** — report render partial; attestation and `verify` specified |

**L6 is a loop over L0–L5 on transformed inputs, not a box after L5**, and its relations pass the same L4
gate as any other predicate. Drawn as a downstream stage it teaches the wrong mental model and implies
relations are self-validating. They are not: a violated relation means *the artifact is wrong* **or** *our
relation is wrong*.

### 1.2 L0 — INGEST

**Kills it, all observed on this artifact.** *Namespace blindness* — a reader that cannot see
`<x14:dataValidation>` reports **35** validations where there are **54** (35 main + 19 `x14`) and reports
the AML-CFT sheet as having zero where it has five; MEASURED on both a hand-written regex and openpyxl
3.1.5, **two independent instruments producing the identical wrong number by the identical mechanism, with
no error reaching a log**. *Shared-formula invisibility* — 211 of 505 formula cells are
`<f t="shared" si="N"/>`, an element with no text, so a text-matching pass loses 41.8% here and
**825 of 1,495 = 55.2%** across the nine workbooks (MEASURED); the loss concentrates on row and column
totals, so **the measurement error is correlated with the quantity being measured, in the direction that
supports the thesis** — the most dangerous shape an instrument error can take. *Destructive round-trip* —
an openpyxl load-and-save with nothing edited takes the workbook from 3,663,391 to 65,877 bytes and deletes
all 19 `x14` validations (MEASURED). *Register mutability* — the register is live and undated.
*Reading the wrong field* — `EncryptDId` is null in 2,005 of 2,005 records while `EncryptedId` is populated
in 2,005 of 2,005; keying on the first returns HTTP 302 on every record forever and yields an
honest-looking absence. **The corrected finding: the list endpoint returns `RegistrationNumber = null` on
650 of 650 fund rows, while the detail endpoint returns it on 228 of 228 live FMEs (VERIFIED-AT-SOURCE).**
*Zip and XML bombs* — an `.xlsx` is a zip of XML supplied by an adversarial-capable party, so entry count,
per-entry uncompressed size and total ratio are checked **before** parse, and `lxml` runs with
`resolve_entities=False`, no DTD and no network.

**Self-check.** Dual-parser agreement over `{n_sheets, sheet_names, hidden_sheets, n_cells,
n_formula_cells, n_validations, n_defined_names, merged_ranges}`. Disagreement on the first three makes the
run **`INVALID`** — the scope is not established, so nothing computed on top of it means anything.
Disagreement elsewhere marks those fields and every predicate reading them returns
`NOT_RUN(not_run.extractor_disagreement)`: the settled fraction falls, it does not silently succeed. The
extraction manifest (parts read, parts skipped, namespaces seen, constructs not understood) is a
first-class output, not a log. **No absence is reported without a declared positive control.** Evidence
this step earns its thirty lines: three implementations of this parse returned **244, 294 and 505** on the
same file on the same day, two of them in the same directory, and the divergence went undetected inside
the authoritative document.

**Components.** Authoritative parse: **raw `zipfile` + `lxml`** (stdlib / BSD), beating **openpyxl as the
schema authority**, which drops all 19 `x14` validations behind a `UserWarning` nobody reads; openpyxl is
retained only for row-shifting shared formulas (verified: `O4 → '=SUM(C4:N4)'`) and for writing mutants.
Register access: **one `GET DirectoryGetList` + one `GET DirectoryDetailGet?EncryptedId=…` per entity**,
snapshot content-addressed; state the plan as *1 list request + N detail requests, N = |records|*, and
report the actual request count of the run that produced the snapshot hash. **A figure of 2,235 requests
was carried in the drafts and is withdrawn to UNRECONCILED:** it matches neither `1 + 650 = 651` (the fund
population) nor `1 + 2,005 = 2,006` (the whole register), no document states the `N` it belongs to, and the
run cannot be re-executed from the artifacts on disk. Re-fetch under the stated plan, record the count in
the manifest, and quote that. Until then the fetch plan is quoted in its **form** — `1 list request + N
detail requests` — and never as an integer, which is the same rule this system applies to a filer. It beat **scraping the rendered page**, which is client-rendered with zero data
rows in the HTML. Parser sandbox: **gVisor (`runsc`) + `seccomp` + `--network=none` + read-only rootfs +
RLIMIT + wall-clock kill**, beating **Firecracker** (hypervisor isolation against an adversary we do not
have, at a VM per filing), **E2B** (the filing leaves our boundary — a data-residency conversation about
regulated filings we should not have to have) and **Pyodide/WASM** (the Grist "Cellbreak" escape,
`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, escaped a Pyodide sandbox by three independent routes and was fixed by
putting Deno's permission system underneath it — **WASM-of-CPython is a resource boundary, not a security
boundary**).

**LibreOffice — DECIDED: excluded from the verdict path entirely.** It sees the truth (it expands all 505
formulas to text and migrates the `x14` validations into the main namespace) but **writes 53 where
35 + 19 = 54: one validation lost, unexplained, in the very step being recommended.** It therefore runs
offline only — template admission and diagnosis — pinned by container digest. A verdict run never invokes
it; a run that would need it either terminates `INVALID` or marks the affected fields
`NOT_RUN(extractor_disagreement)`. *Alternative it beat:* pinning it by digest and keeping it inline —
rejected because an uncharacterised one-validation loss would then sit inside the programme's own
byte-identity acceptance test (§II.5.4).

### 1.3 L1 — SCHEMA INDUCTION

**What the induction recovers**, MEASURED on `sha256 7d9a…` and reproduced independently by four lanes and
one adversarial pass: 10 sheets (9 visible + `Dropdown`, `state="hidden"`) · 6,757 `<c>` elements · **505**
formula-bearing cells = 294 authored expressions + 211 shared dependents · 138 of 505 (27.3%) expressing a
checkable relationship, 223 (44.2%) pure carries · 195 of 294 (66.3%) cross-sheet · **54** data validations
(35 main + 19 `x14`), 22 list-type, 20 resolving to a real enumerable vocabulary · 15 vocabularies on the
hidden `Dropdown` sheet · 252 merged ranges · 12 defined names of which **4 point at `#REF!` in the
regulator's own published blank** · 9 of 10 sheets protected, **`Dropdown` alone unprotected *and*
hidden** · **field surface (unlocked ∧ non-formula) = 3,747 cells**, per sheet Portfolio 1,698 ·
Investors 897 · PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 ·
AML-CFT 22 · build time 28–44 ms cold. A separate pass counting *all* unlocked cells in used ranges returns
3,755; both are right under their own definitions and **3,747 is the denominator**.

**Kills it.** Scope truncation (iterating visible sheets drops `Dropdown`, the vocabulary set is empty, and
`all(v in vocab …)` passes vacuously). Vacuity by empty set. Coordinate-anchored keys silently rebinding on
a row insertion. **Vocabulary read from the wrong document** — `Dropdown` is the only unprotected sheet, so
a predicate resolving the vocabulary from the *filed* workbook validates the filer's data against a list
the filer can edit. Broken references shipped in the authoritative artifact. Scheduled obsolescence:
`Dropdown!$E$3:$E$6` runs out at `2028-29`, so the workbook cannot express FY2029-30.

**Self-check.** Three-way agreement on the induced schema; disagreeing fields become
`NOT_RUN(extractor_disagreement)` by construction. **The denominator is computed twice by independent code
paths**, because when numerator and denominator come from the same wrong parser the ratio stays plausible
and the error is invisible by construction. A named invariant guards the flattering direction: *the
denominator derives from the unlocked mask, never from the predicate set* — that mistake was made twice in
one afternoon by the person who knew about it, once by sampling mutation sites only from cells the
predicates already read and once by computing 99.2% settled from a denominator built out of the numerator.
Parse round-trip must reproduce all 505 formula cells, all 54 validations, all 252 merged ranges, the
hidden sheet and its 15 vocabularies.

**Constants tests — G8, DECIDED, split in two**, because a regression test that fails on correct behaviour
gets deleted: `test_schema_constants` asserts **505 / 294 / 211 / 54 / 22 / 20 / 252 / 3747**, properties
of the published file that must never move; `test_harvest_count` asserts **280 / 515**, properties of our
code that are **allowed to move with a recorded reason** — they will move the first time G3 rejects a
harvested predicate.

**Components.** Schema authority: **raw OOXML via `lxml`**, beating **openpyxl** (above) and **pandas
`read_excel`**, which collapses merged headers and returns cached values, i.e. exactly the numbers under
test. Key identity: **label-anchored `(sheet, merged_header_path, row_label)` with coordinates as a
resolved attribute**, beating **coordinate-anchored keys** because a version bump becomes a re-resolution
instead of a rewrite; measured support — under a naive `(sheet, label-above, label-left)` key **1,749 of
1,953 cells are ambiguous (89.6%)** because 100-row tables repeat the label pair, and the row ordinal
disambiguates completely and is arithmetic, not a prediction.

### 1.4 L1b — CLAUSE GRAPH

Clause identity is **Akoma Ntoso / OASIS LegalDocML** — `eId` per clause, FRBR URI per instrument, promoted
deterministically from `DoclingDocument` — beating **inventing a clause-key scheme**, because without
`eId` a predicate's "the clause it implements" is an unresolvable free-text string and L5 cannot cite; and
the amendment graph is machine-followable, **76 of 82 amending circulars citing a resolvable target
(92.7%, MEASURED)**, with the remaining 6 declared. **10 of 399 circulars are scanned images** — a
permanent declared coverage gap carried on every predicate whose correctness rests on a negative search
result, until they are OCR'd once, offline, and frozen. **FRBR URI handling — DECIDED: implement the
grammar ourselves, ~100 lines.** *Alternative it beat:* depending on `laws-africa/cobalt` — GitHub reports
**NOASSERTION** for `indigo` and `cobalt` and **no lane opened their LICENSE files**; adopt `cobalt` only
if someone opens its LICENSE and it is permissive. The sibling `bluebell` is **GPL-3.0 (verified)** and
must never be linked.

### 1.5 L2a / L2b — EXTRACTION, and why the split is the correction

**L2a needs no model.** For a native `.xlsx`, key-binding is a lookup against L1: **0 of 3,755 unlocked
cells are ambiguous under the address key**, and 154 (4.10%) under a header-anchored key that generalises
across row counts (MEASURED). Running a model to predict what L1 already computes, then conformalising it,
then abstaining, would be an elaborate way to reintroduce uncertainty the artifact does not contain.

**L2b applies to exactly four populations and only these:** P1 cross-document binding (a value in an
attached PDF that must bind to a template key — the real target); P2 template-version drift (23.1% of
circulars amend an earlier instrument, so drift is the normal case); P3 filer deviation (share
**UNMEASURED** — needs real filings); P4 free text, where there may be no key at all.

**Kills it.** *Shape is not truth* — constrained decoding guarantees the key is **a** valid key, never that
it is **the right** key. *The confidently-wrong regime* — structured extraction into a fixed template is
precisely the low-entropy regime where entropy-based abstention was measured to fail. *Void guarantees* —
split conformal requires exchangeability, and a team-authored calibration set against real filings is a
known distribution shift, so the coverage guarantee is **void, not degraded**; quoting a distribution-free
finite-sample guarantee under a known-violated assumption is a stronger error than a loose FFR, because it
borrows a theorem. *The wrong exchangeable unit* — **the exchangeable unit is the FILING; report `n = F`,
never `n = 3,755·F`.** *The forced-abstention floor* — where base error μ exceeds target risk α, any
distribution-free method must abstain on at least `(μ − α)/(1 − α)` of items. *Silent retry* manufactures
exactly the clean verdict this product refuses to give.

**Self-check.** The key is an enum over exactly L1's induced key set, so an off-schema key is outside the
reachable token space at generation time **and** is deterministically rejected afterwards — both kept,
because the post-hoc guard is the one you can prove to a reviewer. **Gate before the layer is built at
all:** measure key-binding accuracy μ on P1; **μ > 0.30 ⇒ do not build the conformal layer**, because at
α = 0.05 the forced-abstention floor already exceeds 26.3% and the honest product is *"cross-document
binding is unchecked"*. `MODEL_EXTRACT` may never be the sole `method` on a `PASS` — a schema constraint,
not a coding convention. Retry is banned; if ever enabled, a Fact produced on attempt *k > 1* carries that
in its provenance.

**Structured output — DECIDED: provider-native structured output with `key` typed as `Literal[*L1_KEYS]`,
plus the post-hoc deterministic key check.** *Alternative it beat:* `outlines` / `XGrammar` (both
Apache-2.0), which mask logits and are strictly better **but require a local model, and no local model is
in this stack**; they become primary the day an open-weight model enters the L2b path. **Whether
provider-native constraint is guaranteed or best-effort is UNVERIFIED — which is exactly why the post-hoc
guard is not optional.** Abstention library: **crepes (BSD-3) / MAPIE (BSD-3)**, beating **TorchCP
(LGPL-3.0)** on licence and **entropy thresholding** on measurement.

### 1.6 L3 — CANDIDATE PREDICATE PROPOSAL (build time only)

**Renamed from "synthesis" deliberately.** Every measured system in this literature that works, works
because a rejector exists; every one that fails, failed because the rejector was absent or fake. **L4 is
the rejector, and L4 is the product. L3 proposes.**

**Kills it, each measured.** The degenerate operating point is documented inside the paper we reuse:
selecting **all** generated candidates yields **100% coverage and 100% FFR** (VERIFIED-AT-SOURCE).
**44.4%** of raw candidates individually blow a 25% FFR budget, and in two of nine pipelines sets whose
every member individually met the constraint reached composite FFR of **88%** and **53%** — FFR is monotone
non-decreasing under union, so **a registry that admits checks one at a time, each individually
acceptable, drifts silently to a flag-everything product.** The modal output is the weakest output (Type
Check at 47.4% prevalence and 0.14 bug-completeness against Arithmetic Equality at 0.82 — a 6× gap). The
correctness prompt is not the completeness prompt (p = 0.008, Cohen's d = 1.73), so **two prompt regimes
run and L4 arbitrates**. And **Silent Scope Omission** is the failure the empirical gates cannot see:
frontier models ground the right clause spans (SpanFaith **0.77–0.79**) and wire the exception structure
wrong (Edge-F1 **0.215–0.246** over 2,290 provisions), while our instrument is full of defeaters — which is
why G0 exists.

**The criterion source, restored to its full and true claim.** SPADE infers what correctness meant from the
traces of a developer changing their mind. We do not have to infer it: **the criterion is a published
instrument with a version, an amendment chain that is machine-followable in 76 of 82 cases, and a blank
template with a content hash. The criterion source is not more *authoritative* than SPADE's — the
regulator's own template computes a scheme total that misses two of its own nine legal values — it is
*citable, versionable and watchable*, which is what lets a predicate be tied to a clause, re-qualified when
the clause moves, and quarantined the day a circular changes the rule.** That is exactly what the
instrument-stream watcher implements, and it is a novelty no earlier version of this document stated.

**Self-check.** A **verbatim-quote provenance guard** — `source_text.find(quote)` must succeed or the
candidate is rejected at the boundary, at zero extra model cost. **`schema_keys` machine-checked against
the CEL AST both ways**, possible only because the language has no variables and no loops, and the reason
the settled fraction is a *derived* quantity rather than an estimate. **Three mandatory free baselines, run
before the model:** B0 the template's own 138 checkable relations; B1 **Daikon** over the clean corpus at
`--conf_limit 0.99`, whose trivia output doubles as the degeneracy list; B2 the degenerate arm — "no cell
is blank and no cell errors" — the analogue of the `NoException` baseline that found **68.9%** of a
published neural oracle's bugs at **twice** its precision. **If L3 does not beat B0 ∪ B1 ∪ B2 on marginal
kill at equal FFR, it has produced nothing**, however many predicates survive.

**Components.** Selection: **reimplement SPADE's ILP** (~40 lines of PuLP/CBC; measured runtimes
0.104–1.197 s on thousands of variables), beating **depending on the SPADE repository** — 17★, 1 fork,
**no licence field**, last push 2024-04-07: reuse the algorithm, not the repository. Prompt construction:
feeding L1's induced schema in as an explicit I/O constraint is the dominant lever on **structural
similarity (+37–54 percentage points)** in the only published study of statute→executable-model generation
(arXiv:2604.17153, VERIFIED-AT-SOURCE); **that study's *outcome* equivalence tops out at 51–53%**, and its
own caveat is that structural similarity does not guarantee outcome equivalence, or vice versa. Framing:
**the output is a number — `k` of `n` model-proposed checks survived a gate specified before the model
ran**, beating *"L3 works"*, which is unfalsifiable. **`k = 0` is a publishable result.**

### 1.7 L4 — QUALIFICATION

Specified in full in §II.4.3, because the gates are a property of the predicate model rather than of the
pipeline. Two things belong here. **The ceiling, stated permanently:** `KR = 0.82` licenses exactly one
sentence — *"rejects 82% of the 340 defects I seeded, under fault model v3"* — and does **not** license
*"detects 82% of real filing errors"*. In code mutation testing the bridge is the coupling effect; there is
**no coupling study for financial filing data**, so the bridge does not exist and must not be walked
across. **And the honest statement of what the gate has demonstrated:** *the gate has one demonstrated
rejection — five of ALR's six bound predicates assert only `≥ −1e17` over 1,428 cells and are refused.
Whether it rejects anything on the FME workbook is unmeasured: 19 of 24 FME bounds are a real `≥ 0`.*

### 1.8 L5 — EXECUTION AND VERDICT

Specified in full in §II.3. The failure modes, enumerated as code because that is how they will arrive:

```python
# 1. VACUOUS PASS — the classic, and the most likely to ship
def check_all_percentages_sum_to_100(cells):
    return all(abs(sum(g) - 100) < 1e-9 for g in group(cells))
# group() returns [] because the selector missed a renamed sheet. all([]) is True.
# Returns PASS. Nothing checked. Nothing logged.

# 2. EMPTY-SET ARITHMETIC     sum([]) == 0 ;  len(rows) == declared  passes as 0 == 0
# 3. SELECTOR DRIFT — a regex over OOXML that cannot see <x14:dataValidation>. Reports 3.
#    Truth is 22. Confident, well-formed, wrong.
# 4. SCOPE TRUNCATION — 'Dropdown' is state="hidden"; its fields never enter the DENOMINATOR.
# 5. SHARED-DENOMINATOR ERROR — numerator and denominator from the same wrong parser. Ratio 1.0.
# 6. SWALLOWED EXCEPTION      except: result = UNCHECKED   # a crash that looks like a limit
```

`cells_bound == 0 ⇒ ERROR` kills modes 1–4 at once; the twice-computed denominator kills mode 5; the
eight-state vocabulary kills mode 6.

**Components.** Verdict model: **build it — nothing in the ecosystem has a third value.** *Alternative it
beat:* **Great Expectations**, disqualifying and in the exact direction that kills us — with
`catch_exceptions=True`, an expectation that *could not be evaluated* returns `success = False`, **the same
value it returns when it evaluated and the data was wrong**, and its documented result fields contain no
field for "not applicable", "out of scope" or "no oracle exists". **Soda Core** is disqualified on licence
— Elastic License 2.0 forbids providing the software to third parties as a hosted service, which is what we
are. **pandera** (MIT) is adopted **only** as a host-function implementation for bulk column checks, never
as the predicate language. The corrected guidance line: *do not rebuild the check **library**; you **must**
build the **verdict model**, because none of them has one.*

### 1.9 L6 — DIFFERENTIAL AND INVARIANT PROBES

**SUT — DECIDED: the workbook-as-program.** *Alternative it beat:* the filer's valuation engine, which
would require the FME to run our transformations through their own system — a different and more
interesting product, but not this one. The workbook is genuinely re-executable: **all 505 formula cells
carry cached computed values**, so a baseline exists. The relation set is **25, none requiring ground
truth**: 15 need the filing alone, 4 the filing plus the pinned blank, 3 two consecutive filings, 1
multiple instances, and 2 are checker self-tests never reported to the filer.

The relation that pays for the layer is the **formula-override differential**: for every cell the blank
template declares to be a formula, compare the filed value against the value obtained by evaluating the
template's formula over the filed inputs. **This is the only thing in the design that detects a filer
overwriting a formula cell with a literal** — a defect that leaves the filing perfectly self-consistent,
because the inconsistency was deleted along with the formula. Its oracle is the published blank, so it
needs no corpus. **It is predicate #1**, and its `method` value is `TEMPLATE_DIFF` — which is why dropping
`TEMPLATE_DIFF` from the schema would make the design's own flagship undescribable. Sheet protection does
not help: nine sheets carry SHA-512 `sheetProtection` hashes and stripping them is a zip edit, so **assume
the filed artifact is fully mutable and build no predicate whose validity depends on a range being
protected.**

**Kills it.** Relations are not self-validating — a violated relation means *the artifact is wrong* **or**
*our relation is wrong*, so every relation passes L4 like any other predicate. Null tests inflate the
settled fraction and are rejected automatically by G3. **Degenerate satisfaction** — an all-zero filing
satisfies every partition identity trivially, so every partition relation carries a **non-degeneracy
precondition** and returns `OUT_OF_SCOPE`, never `PASS`; without it an empty filing scores 100% through the
L6 door. **Cross-basis contamination** — Portfolio note 7 puts Tables 3.1/3.2 on a direct-investment basis
while the PMS note puts Table 5.6 on a look-through basis, so any relation adding a 3.x quantity to a 5.6
quantity is invalid by the artifact's own notes.

**Tolerance.** `τ(n) = 5n` units of `MILLI_USD_MILLION` (= `n × 0.005` USD Million), from guidance C111.
Integer arithmetic throughout; **counts get zero tolerance — a person is not a rounded quantity, and slack
there is how a missing investor hides.** A fixed epsilon is the single most likely source of spurious
failures.

**Components.** Execution vehicle: **Hypothesis** — reported **MPL-2.0, LICENSE not opened (SECONDARY)** —
with `@invariant` for necessary relations and in-rule assertions for expected ones, so the FAIL/ADVISORY
split is implemented by the library rather than by convention, plus shrinking and `@example` regression
pinning; it beat a bespoke loop, which loses both. Search budget **`max_examples = 50`**, beating
Hypothesis's default 100 and fuzzer scale because **55% of mutations are found with a single input and 76%
within the first 20**, and this input space is small and fixed. Relation authorship: **human, read off the
artifact's own formula graph and guidance notes, no model** — measured, model-generated metamorphic
relations score "markedly low" on novelty and recapitulate the textbook classes, which is exactly how an
earlier version of this design arrived at five relations of which four false-alarm on a *correct* filing
and the fifth is vacuous. Formula evaluator: **reimplement the eight-function vocabulary** (`SUM`,
`COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)`) over a topological sort of 505
cells, beating **`formulas` (EUPL 1.1+)** and **`pycel` (GPL-3.0)** on licence for a hosted product and on
method — importing someone else's evaluator imports an unmeasured error rate our own admission rules would
have to reject — **and the reimplementation *is* the differential arm.**

### 1.10 L6.5 and L7

Specified in §II.6 and §II.5 respectively.

---

## II.2 — THE CORRECTED DATA FLOW

```
 BUILD TIME — offline, batched, human-reviewed, amortised over every future filing
 ─────────────────────────────────────────────────────────────────────────────────────────────────
  regulation PDF ──┐
  399 circulars ───┼──►  L1b CLAUSE GRAPH            [deterministic · SPECIFIED, nothing built]
                   │      Docling → Akoma Ntoso · eId per clause · FRBR URI per instrument
                   │      76/82 amending circulars resolve · 10/399 scanned → declared gap
                   ▼
   ╔══════════════════════════════╗            ╔═══════════════════════════════════════════════╗
   ║  L3  CANDIDATE PROPOSAL      ║    CEL     ║  L4  QUALIFICATION — FIVE GATES, THIS ORDER   ║
   ║  ★ THE ONLY MODEL IN THE     ║  envelopes ║   G0  scope faithfulness            free      ║
   ║    ENTIRE SYSTEM ★           ║ ─────────► ║   G1  executes and binds            free      ║
   ║  ~600 calls per template     ║            ║   G3ᵖ non-degeneracy · proof arm    cheap     ║
   ║  version  (DERIVED: ~30      ║            ║   G2  seeded-defect kill            expensive ║
   ║  obligations × 10 candidates ║            ║   G3ᵉ non-degeneracy · control arm            ║
   ║  × 2 prompt regimes)         ║            ║   G4  false-failure rate + provenance         ║
   ╚══════════════════════════════╝            ║   emits kill_case + pass_case (liveness)      ║
             ▲                                 ║   ADMIT ⇒ append-only REGISTRY (Merkle root)  ║
   hand-authored predicates ────────────────► ║   REJECT ⇒ rejection row → counterEvidence[]  ║
   L6 relations ────────────────────────────► ╚═══════════════════════════════════════════════╝
                                                              │ registry_root
 ══════════════════════ THE DETERMINISTIC BOUNDARY ═══════════╪═══════════════════════════════════
  Every model output crosses this line as DATA that a program has already adjudicated.
  Nothing below opens a socket to a model endpoint.  (Specified; the CI gate is not yet written.)
                                                              │
 RUN TIME — per filing                                        │
 ─────────────────────────────────────────────────────────────┼───────────────────────────────────
  blank template ─┐                                           │
  filing .xlsx ───┼─► L0 INGEST  sha256 ORIGINAL BYTES ← what L7 signs
  register JSON ──┘   container guard · DUAL PARSER · agreement vector
        ▲             disagree on {sheets, names, hidden} ⇒ INVALID; else NOT_RUN(those fields)
        │                                  │
  [+] INSTRUMENT WATCHER                   ▼
  daily hash of circular +   ┌──────────────────────────────────────────┐
  Authority-meeting pages;   │ L1 SCHEMA INDUCTION  (from the BLANK)     │
  a new instrument citing a  │  all sheets incl. hidden · extLst/x14     ├── TemplateSchema (pinned)
  regulation a predicate     │  shared formulas materialised · degree map│        │
  claims ⇒ PROVISIONAL,      │  MILLI_USD_MILLION · label-anchored keys  │        │
  automatic and pessimistic  │  UNLOCKED-CELL MASK = THE DENOMINATOR     │        │
        └──────────────────  │  + EXTRACTION MANIFEST                    │        │
                             └──────────────────┬───────────────────────┘        │
                    ┌───────────────────────────┴──────────────┐                 │
                    ▼                                          ▼                 │
        L2a STRUCTURAL EXTRACTION           L2b DOCUMENT EXTRACTION               │
        deterministic · NO MODEL            ✦ MODEL · CONTINGENCY ONLY ✦          │
        lookup against L1                   unstructured attachments only;        │
        0 of 3,755 cells ambiguous          SKIPPED ENTIRELY when there are       │
        under the address key               none — the normal case, $0.00         │
                    │                                          │                 │
                    └──────────────────┬───────────────────────┘                 │
                                       ▼  Facts{key,value,unit,anchor,warrant}    │
        ┌────────────────────────────────────────────────────────────────┐        │
        │ L5  PRE-FLIGHT + EVALUATION + VERDICT       (deterministic)     │◄───────┘
        │  CEL over exactly two bound names: `filing`, `template`.        │  admitted predicates only
        │  No clock, no network, no filesystem. Terminating by design.    │
        │  8 states × 30 namespaced reasons × severity {BLOCKING|ADVISORY}│
        │  cells_bound per predicate; 0 ⇒ ERROR ⇒ run INVALID             │
        │  denominator computed TWICE by independent code paths           │
        └───────────────────────────┬────────────────────────────────────┘
        ┌───────────────────────────┴──── L6 IS A LOOP OVER L0–L5 ─────────────────┐
        │  transform the input → re-run → compare. 25 relations, all L4-qualified. │
        │  ★ TEMPLATE_DIFF: template says formula, filing carries a literal ★      │
        └───────────────────────────┬─────────────────────────────────────────────┘
                                    ▼
        ┌────────────────────────────────────────────────────────────────┐
        │ L6.5 SELF-CHECK AND RESIDUE                                     │
        │  replay each predicate's stored kill_case against THIS filing.  │
        │  any survivor ⇒ run state INVALID, and no settled fraction is   │
        │  emitted at all.  RESIDUE := WRONG mutants nothing rejects.     │
        └───────────────────────────┬────────────────────────────────────┘
                                    ▼
        ┌────────────────────────────────────────────────────────────────┐
        │ L7 ATTESTATION  DSSE + in-toto Statement v1                     │
        │  subject[] = filing ⊕ template.  ★ NO `result`. NO `status`. ★   │
        │  top level is `scope`.  → self-contained HTML → lossy OSCAL      │
        └────────────────────────────────────────────────────────────────┘
```

**How many model calls an honest implementation needs.** Not two. **Zero on the verdict path per filing**
(specified, gate unwritten). **~600 per template version at build time**, DERIVED from the pre-registered
design — ≈30 obligations drawn, 10 candidates per obligation per prompt regime, two regimes — plus the L3
baselines, which use no model at all. **O(1) per unstructured attachment on the L2b path**, which is
skipped entirely when a filing has no attachment, which is the normal case; if the conformal layer passes
its μ ≤ 0.30 gate it adds O(calibration set) calls, once, offline. A property you can assert in CI beats a
property you assert in prose, which is why the claim is *zero on the verdict path* and not a count.

---

## II.3 — THE VERDICT MODEL

This is the product's core object. Everything below is normative and replaces every earlier version.

### 3.1 The denominator's unit — G1, DECIDED

**DECIDED: the unit of the denominator is the CELL.** The report's primary key is `cell_id = stable_key`.
The obligation becomes an **attribute of the predicate**, never a factor of the denominator.

*Alternative it beat:* the `(field × obligation)` pair. It lost because **no derivation of it exists
anywhere in the corpus.** Three incompatible pair counts were in circulation, two of them lifted from an
*illustrative* JSON block that never claimed to be a measurement, and none reconcilable with the one
quantity that was actually measured. `obligationsTotal` and `pairsTotal` are therefore **deleted from the
schema** and must not appear in an example until a published enumeration rule exists. The measured
denominator is the **3,747-cell field surface**; 2,373 cells are settled by 280 harvested predicates and
1,374 are declared unchecked.

**Consequences, all of which are now normative:**

1. `run_item.pair_id` becomes `run_item.cell_id`; `scope.denominator.pairsTotal` becomes
   `scope.denominator.cellsTotal`, whose value **is** `fieldSurface`.
2. **Obligation binding — G6, DECIDED.** `obligation_id` comes from a **hand-maintained `obligations.yaml`**
   (`OBL-nnn` → `{frbr_uri, eId, verbatim_quote, char_span}`), because **L1b is entirely unbuilt** and a
   day-one answer that depends on an unbuilt layer is not an answer. When L1b ships, `obligations.yaml`
   becomes generated and the ids are preserved. Obligation is a grouping *view* over items; it is never a
   denominator.
3. **Many predicates may bind one cell.** A cell's item state is the maximum of its evaluations under the
   precedence order
   `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`.
   A cell is clean only if **every** predicate binding it passed. `NO_PREDICATE` is not in the order: it is
   the state of a cell with an empty evaluation set. Every item carries `evaluations[]` — the full
   per-predicate vector — so nothing is lost by taking a maximum.

### 3.2 The eight closed item states

| State | The rule that produces it | Settled denominator? | Precedent |
|---|---|:--:|---|
| `PASS` | `applicable` true, pre-flight clean, `expr` evaluated to true, `cells_bound > 0` | ✅ settled | XCCDF `pass` |
| `FAIL` | as above, `expr` evaluated to false; `witness` is evaluated for the cell list | ✅ settled | XCCDF `fail` |
| `INDETERMINATE` | the predicate ran to completion and the result is not decidable (abstention, tolerance straddle, source conflict, engine disagreement) | ✅ kept | XCCDF `unknown` |
| `NOT_RUN` | the predicate is admitted and in scope but did not execute (input unavailable, unreadable source, budget, deactivation, extractor disagreement) | ✅ kept | XCCDF `error`; C2PA `inaccessible` / `skipped` |
| `NO_PREDICATE` | the cell is in scope and **no admitted, qualified predicate binds it** | ✅ **kept — the deliberate divergence** | XCCDF `notchecked` |
| `ERROR` | the apparatus failed here: a predicate raised, `cells_bound == 0`, a canary was silent, closure was violated, the readers disagreed structurally | ✅ kept, **and the run becomes `INVALID`** | — |
| `OUT_OF_SCOPE` | `applicable` evaluated false, or the run profile excluded it, or the operator withheld it | ❌ removed | XCCDF `notapplicable` / `notselected` |
| `INFORMATIONAL` | the predicate ran and its output is a value for the reader, not a verdict (including a lawfully-failing *expected* relation) | ❌ removed | XCCDF `informational` |

**The divergence, and it is the single most important scoring decision in the design.** XCCDF removes
`notchecked` from its denominator because its denominator is a benchmark a human authored, so "no check
exists" means the author chose not to have one. **Ours is induced from the regulator's own published
template, which is authoritative and complete — so "no predicate exists" is a gap in *us*, not in the
specification.** Removing it would let the settled fraction rise by doing nothing. It ships with this
justification attached.

**Severity and override are orthogonal axes, not extra states.** `severity ∈ {BLOCKING, ADVISORY}` is set
by the measured FFR (§3.6). `override = {oldState, newState, remark, actor, time}` retains both states
inside the signed payload; an overridden item counts under its **new** state and the override count is
reported separately — a downstream reviewer will want it.

**Run states:** `VALID` (the pipeline ran, the checker demonstrated liveness on this artifact, closure
holds) · `INVALID` (the system could not demonstrate it was working here) · `REJECTED` (the submission
never became a run: size or media-type refusal, no run row created). **An `INVALID` run renders a report
that states why and carries no settled fraction at all, and its aggregate verdict is `null`, not
`SETTLEMENT_INSUFFICIENT` — the latter is a finding about the filing and this is a finding about us.**

### 3.3 The closure invariant — seven terms

```
outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == cellsTotal
                                   ( settled == pass + fail )
```

Checked at report-generation time. **A cell that lands in no bucket aborts the report.** This is the
terminal `DISALLOW *`: the in-toto specification names the hazard in its own text — an implicit open world
*"could allow artifacts to sneak into the step or inspection undetected."* The seven-term form is the only
one under which each of the eight states lands in exactly one bucket; the five-term version that was in
circulation had no bucket for `INFORMATIONAL` or `ERROR`, so under it every informational item aborted the
report. `inScope = cellsTotal − outOfScope − informational` is the settled fraction's denominator.

### 3.4 The evaluation contract — five rules

**G5, DECIDED: this subsection is the evaluation contract.** `EVALUATION-CONTRACT.md` is *generated* from
it by a build step, and a CI test asserts that the evaluator's transition table equals this table. It
appears in exactly one place because three different versions of it were live at once.

```
1.  Evaluate P.applicable
      error  -> NOT_RUN(not_run.source_unreadable)            [never FAIL]
      false  -> OUT_OF_SCOPE(P.reason_if_inapplicable ∈ out_of_scope.*)   [never PASS]
      true   -> continue

2.  PRE-FLIGHT. For every key k in P.schema_keys, test presence and type against the fact model
    BEFORE evaluating P.expr. Any k absent or mistyped -> NOT_RUN(not_run.source_unreadable: <k>).
      Why this is structural and not optional: the CEL specification states that for || and &&,
      if an operand's evaluation "produces a runtime error, it will be ignored." So
      `true || <error>` evaluates to TRUE, and an unguarded predicate can return PASS while
      silently swallowing an operand that could not be evaluated at all — the exact defect this
      product exists to prevent, manufactured by the language. Because schema_keys is
      machine-checked against the AST, the pre-flight set is EXACT, not an estimate.

3.  Evaluate P.expr under a step-count budget and a wall-clock kill
      budget exceeded -> NOT_RUN(not_run.budget_exhausted)     [never FAIL]
      runtime error   -> ERROR(error.predicate_raised), run_state = INVALID
      false           -> FAIL, then evaluate P.witness for the cell list
      true            -> PASS

4.  Warrant composes by WEAKEST INPUT: warrant = min over every fact the AST read, under
    DETERMINISTIC > MODEL_EXTRACTED > DERIVED; retrieved_at = max over inputs. A verdict is never
    fresher than its stalest input and never stronger than its weakest.

5.  Every predicate reports cells_bound. cells_bound == 0 -> ERROR(error.cells_bound_zero),
    run_state = INVALID. Binding to nothing is never a PASS.
```

The five rulings the drafts disagreed about, each stated once and finally:

| Situation | State | Reason code | Run state | Why not the alternative |
|---|---|---|---|---|
| `applicable` evaluates **false** | `OUT_OF_SCOPE` | `out_of_scope.*` | unchanged | The word `UNCHECKED` was retired when the state axis was opened up; an evaluation contract written in a retired vocabulary is not a contract |
| `expr` **raises** | `ERROR` | `error.predicate_raised` | **`INVALID`** | A predicate that raised is an **apparatus failure**, not an unreadable source. `not_run.source_unreadable` is reserved for inputs that could not be read, and the two have opposite remedies — fix the code versus retry |
| **budget exceeded** | `NOT_RUN` | `not_run.budget_exhausted` | unchanged | Never FAIL. A check that ran out of time has told us nothing about the filing |
| **`cells_bound == 0`** | `ERROR` | `error.cells_bound_zero` | **`INVALID`** | This is the vacuous-pass failure mode the whole design exists to catch. Demoting it to `NOT_RUN` puts it in the same bucket as a rate-limited register |
| a proviso is **declared but unimplemented** | `NO_PREDICATE` record | `no_predicate.not_yet_synthesised` | unchanged | It is not an ambiguous rule — the rule is clear and we have not implemented it. The record carries the proviso's **verbatim text and character span**, and the predicate's scope record carries `provisos_declared` |

**How a declared proviso interacts with the cell denominator — DECIDED.** Closure holds over cells, and a
proviso is not a cell. So: a predicate with `provisos_declared > 0` (a) is admitted at **`ADVISORY` at
most**, (b) stamps every item it settles with `scopeIncomplete: [{eId, char_span, quote}]`, and (c) causes
the report to emit one `NO_PREDICATE(no_predicate.not_yet_synthesised)` record per declared proviso into
`scopeCaveats[]`, counted and rendered in the unchecked panel. *Alternative it beat:* charging the proviso
against specific cells in the denominator — rejected because the cells a proviso governs are exactly the
ones we cannot identify (that is what "unimplemented" means), so any cell-level attribution would be
invented. A predicate that neither implements **nor** declares a proviso is rejected at G0; that is the
real gate.

### 3.5 The thirty reason codes

Closed, namespaced, five families. **Admission test, written into the spec: two reasons are distinct if and
only if they imply different remedies. If the operator's next action is the same, the codes merge.** That
test is why the vocabulary is 30 and also why it is not 60. A reason code is **required whenever the state
is not `PASS` or `FAIL`**, and forbidden when it is.

**`no_predicate.*` — 8. We have no qualified check. The honest core, and the backlog.**

| Code | Meaning | Remedy |
|---|---|---|
| `.undecidable_by_construction` | "correct" is not defined for this obligation — valuation appropriateness; whether a scheme is properly classified | **None. The permanent floor; report it forever** |
| `.requires_judgment` | a competent human can decide; no program can | Route to a human; never auto-close |
| `.not_yet_synthesised` | decidable in principle; nobody has written it. **Also the emission for a declared-but-unimplemented proviso** | The growable set — this is the settled-fraction-over-time story |
| `.failed_qualification` | a predicate **was** written and a gate rejected it; carries the rejecting gate and the measured number | Improve the predicate, or accept the gap knowingly |
| `.rule_ambiguous` | the obligation text does not determine a testable condition — reg 51(1)'s open delegation | Ask the regulator |
| `.no_obligation_specified` | **the instrument is clear and simply says nothing.** Two of nine legal Type-of-Scheme values have no NAV-frequency rule at all | Distinct from `.rule_ambiguous` (a rule exists and is unclear) and from `.not_yet_synthesised` (our gap). **Conflating "the regulator did not legislate this" with "we haven't got round to it" would be the most misleading thing this report could do** |
| `.rule_withdrawn` | previously admitted; its FFR later exceeded threshold, or its clause was amended | Re-qualify or retire |
| `.not_yet_requalified` | `PROVISIONAL`: an element of `qualified_against` changed. **It still runs, so detection is not lost, but it does not count in the settled numerator** | Human clears it |

**`not_run.*` — 10. We have a check; it did not run. Every one is an ops or data problem.**

`.input_unavailable.counterparty` (needs data held by a party who is not the filer) ·
`.input_unavailable.register` (live register unreachable, rate-limited or ambiguous at run time) ·
`.input_unavailable.prior_period` (needs a filing we do not hold) ·
`.source_unreadable` (the artifact or a region of it could not be parsed) ·
`.template_unbound` (L1 could not bind the filing to a published template hash — **this escalates: the
whole run is suspect**) ·
`.deactivated` (an admitted predicate deliberately switched off for this run, with a pointer to the
decision record — skipping is sometimes legitimate, and the moment it is legitimate the report must be able
to say so, or the skip becomes silent) ·
`.budget_exhausted` ·
`.external_source_lacks_field` — **the external source structurally does not carry the field. Our own
near-miss is the canonical illustration and not an instance: the register's *list* endpoint returns
`RegistrationNumber = null` on 650 of 650 rows while its *detail* endpoint returns it on 228 of 228.** ·
`.external_source_unavailable` (the source was down at filing time) ·
`.extractor_disagreement` (the readers disagreed on this field — added because a schema extractor that
silently returns 35 of 54 validations is the failure this product exists to prevent, occurring inside the
product).

**`indeterminate.*` — 4.** `.extraction_abstained` (the L2b conformal set was not a singleton — the
designed abstention) · `.tolerance_straddle` (the result sits inside the rounding band where both answers
are admissible; the rounding trade-off now has a name instead of being absorbed into a threshold) ·
`.conflicting_sources` (two admitted sources disagree and no tie-break rule is published) ·
`.engine_disagreement` (the two recalculation engines disagree on this cell — never `PASS`, never `FAIL`).

**`out_of_scope.*` — 3. Removed from the denominator, therefore the most abusable; each requires a
machine-checkable justification.** `.not_applicable` (a pointer to the schema condition that makes it
inapplicable) · `.not_selected` (a pointer to the named run profile and its digest) · `.withheld` (an actor
plus a rationale; **counted and displayed separately, never folded into `.not_applicable`**).

**`error.*` — 5. The apparatus failed. Any one sets `run_state = INVALID`.**
`.predicate_raised` · `.cells_bound_zero` · `.canary_silent` · `.closure_violated` ·
`.parser_disagreement_structural`.

**Why the distinctions are load-bearing, in one citation.** SPDX names three distinct causes of
non-assertion — the creator *"cannot reach a reasonable objective determination"*, *"has made no attempt"*,
and *"has intentionally provided no information"* — and then deliberately collapses all three into one
token, `NOASSERTION`. That is a documented decision, not an oversight, and it is precisely the collapse
this product exists to refuse.

### 3.6 The four enums that were in dispute

```
method      = RECOMPUTE | TIE_OUT | SCHEMA_BIND | TEMPLATE_DIFF | REGISTER_LOOKUP
            | CLAUSE_TEST | DIFFERENTIAL | MODEL_EXTRACT | UNKNOWN          -- NINE values
warrant     = DETERMINISTIC | MODEL_EXTRACTED | DERIVED                     -- composes by weakest input
provenance  = COMPUTED | DECLARED                                           -- by us | by the filer
corpus_provenance = SELF-AUTHORED | BLIND-FILLED | TEMPLATE-COMPUTED
                  | REGISTER-DERIVED | REAL-PARTNER | PUBLIC                -- SIX values
```

`TEMPLATE_DIFF` is the method of the formula-override detector, which both the design's own text and its
demo call predicate #1; a schema without it cannot describe the design's flagship. `DIFFERENTIAL` replaces
`METAMORPHIC` because the technique's own definition requires a re-executable system under test.

**`warrant` is the runtime provenance lattice and nothing else.** The four-value column
`MEASURED | MODELED | ASSERTED | UNCHECKED` that appeared in one draft is **deleted**: it confused the
corpus's documentation-warrant labels with the runtime lattice, and no rule composes `MEASURED` with
`ASSERTED`. The lattice composes: a derived fact takes `warrant = min(inputs)` and
`retrieved_at = max(inputs)`. It is **exact and not an estimate**, because `schema_keys` is machine-checked
against the AST.

**`provenance` is `COMPUTED | DECLARED`.** `GATHERED` is C2PA's word for a different distinction
(created versus gathered assertions) and importing it here would blur ours.

**`corpus_provenance` has six values and the register value is spelled `REGISTER-DERIVED`.** The five-value
version could not express the one false-failure rate this project can measure today, and a third spelling
(`REAL-REGISTER`) existed in a third document. **`SELF-AUTHORED` renders as `—` and the word
*uninformative*. It is not a number and the schema forbids one**, because an FFR measured on a corpus its
authors also wrote has expected value zero regardless of predicate quality — printing *"0.0% false failures
across 340 clean filings"* is worse than printing nothing, because it has the shape of evidence.

**Severity thresholds — G2, DECIDED and pre-registered before the first run:**

```
FFR Wilson UPPER bound  ≤ 0.02   ⇒  BLOCKING
                 0.02 <  ≤ 0.10  ⇒  ADVISORY
                        >  0.10  ⇒  NOT ADMITTED  (this is gate G4)
```

The threshold applies to the **Wilson upper bound**, not the point estimate. *Alternative it beat:* the
point estimate — rejected because `0 fires / 4 filings` has a point estimate of 0.000 and an interval of
`[0.000, 0.490]`, and a rule keyed on the point estimate would let a sample of four buy `BLOCKING`.
**Consequence, stated so nobody is surprised on stage: on day one almost nothing is `BLOCKING`.** A
predicate needs roughly `n ≥ 185` clean, non-self-authored filings with zero fires to clear 0.02 on the
upper bound. Everything enters as `ADVISORY` with its interval printed beside it. That is the EBA's
warnings-first convention with the measurement put back in, and it is defensible to a downstream reviewer
on day one because they already run the unmeasured version.

### 3.7 Aggregation, and the state name that replaces the green tick

```
residueIsConfined := (unsettled cells touch ≤ K distinct sheets)
                 AND (no unsettled cell is flagged material-by-policy)
                 AND (unsettled / inScope ≤ T)
```

| | residue confined | residue pervasive |
|---|---|---|
| **failures present** (`settled.fail > 0`) | `EXCEPTIONS_NOTED` | `ADVERSE` |
| **no failures, unsettled residue** | **`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`** | `SETTLEMENT_INSUFFICIENT` |
| **self-check failed** | `INVALID` (verdict field is `null`) | `INVALID` |

**There is no state whose name means "clean."** The best available verdict is literally
`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`, which cannot be quoted out of context without carrying its
own qualifier. This delivers the no-green-tick commitment **by naming**, which is far more robust than by
iconography: an icon can be screenshotted; a name travels with the claim. The report's own title string is
a function of the verdict state. When `SETTLEMENT_INSUFFICIENT`, the wording flips from *"this filing was
checked against N predicates"* to *"this filing was **submitted for** checking against N predicates;
coverage was insufficient to report."*

Say what we are doing and what we are not: "material" and "pervasive" are matters of professional judgment
in the standard we borrow the shape from. **We cannot compute them.** We can declare a published, versioned
policy and apply it deterministically, which is strictly more inspectable than judgment. **Do not claim to
have implemented ISA 705. Claim a declared policy in its shape.**

**`K` and `T` — OPEN — USER DECISION.** Two different parameter sets shipped in two drafts (`K = 3, T = 0.35,
v2` and `K = 3, T = 0.45, v1.1`), and **neither has a basis anywhere in the corpus**. There will be exactly
one file, `pervasiveness-policy-v1.json`, versioned inside the attestation. Until an argument for the
numbers exists, both are rendered as the literal string `PLACEHOLDER` in every example and every screen.
**The exact question: what is the maximum number of distinct sheets `K` an unsettled residue may touch, and
the maximum unsettled/inScope ratio `T`, before a report with no failures must be downgraded from
`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` to `SETTLEMENT_INSUFFICIENT` — and on what argument?**

---

## II.4 — THE PREDICATE MODEL

### 4.1 What a predicate IS

**A predicate is not an expression. It is a small, signed, content-addressed record that *contains*
expressions.** The envelope is what makes non-settlement a first-class evaluation outcome rather than an
exception, and it is where all qualification metadata lives. Content address = `sha256` of the RFC 8785
canonical serialisation (stated explicitly, because *"the sha256 of the JSON"* is not a definition and two
implementations disagreeing on key order produce two registry roots).

```yaml
# predicate/P-0041.yaml
id:            P-0041
version:       3
kind:          harvested            # harvested | proposed | hand_authored | relation
template:      sha256:7d9a…         # the PINNED blank this predicate binds to
schema_keys:   ["intro.tbl15.row[*].scheme_type", "vocab.scheme_type"]
                                    # DECLARED, machine-checked BOTH WAYS against the CEL AST.
                                    # Reads an undeclared key -> REJECT. Declares an unread key -> REJECT.
host_fns:      []                   # closed, versioned set; unregistered -> REJECT
obligation_id: OBL-014              # attribute, NOT a denominator factor  (§II.3.1)
clause:
  instrument:  "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30"
  eId:         "reg_27__para_1"
  span:        [10422, 10597]       # exact character span — G0 requires it
  quote:       "Type of Scheme"     # VERBATIM. source.find(quote) must succeed or REJECT.
  provisos:
    - text:    "Provided that this requirement shall not apply in case of a fund of funds scheme…"
      disposal: DECLARED            # IMPLEMENTED | DECLARED
      emits:    NO_PREDICATE(no_predicate.not_yet_synthesised)
rationale:     "Every declared scheme type must be a term the published template offers."

applicable: >                       # CEL -> bool. false => OUT_OF_SCOPE(reason_if_inapplicable)
  size(filing.intro.tbl15.rows) > 0
expr: >                             # CEL -> bool. true => PASS, false => FAIL
  filing.intro.tbl15.rows.all(r,
    r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)
witness: >                          # CEL -> list. what to show on FAIL
  filing.intro.tbl15.rows.filter(r,
    r.scheme_type != "" && !(r.scheme_type in template.vocab.scheme_type)).map(r, r.__cell__)

reason_if_inapplicable: "out_of_scope.not_applicable: no schemes declared"
tolerance:      null                # arithmetic predicates: {"tau_units_per_summand": 5}  (MILLI_USD_MILLION)
severity_tier:  ADVISORY            # SET BY THE MEASURED FFR (§II.3.6), never by hand

external_deps:                      # declared, so a schema change at the source degrades LOUDLY
  - endpoint: "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet"
    field:    "RegistrationNumber"
    snapshot: sha256:…              # content-addressed; the register is mutable and undated
    on_missing: NOT_RUN(not_run.input_unavailable.register)

qualification:                      # WRITTEN BY L4. NOT HAND-EDITABLE. ABSENT => DOES NOT LOAD.
  g0: {provisos_total: 1, provisos_implemented: 0, provisos_declared: 1}   # must sum or REJECT
  g1: {executes: true, keys_resolve: true, cells_bound: 10}
  g2: {generated: 61, unobservable: 17, observable: 44, unreachable: 3, killed: 41,
       kill_rate: 0.932, by_fault_class: {F2: 1.00, F5: 0.00, F12: 0.93},
       marginal_kill_over_baselines: 0.11, fault_model: "v3", harness: "1.2.0"}
  g3: {method: "z3+empirical", verdict: "non_degenerate", witness: "sha256:…",
       control_arm: {seeded_outside_read_set: 41, spurious_fires: 0}}
  g4: {fired: 2, n: 96, rate: 0.021, wilson: [0.006, 0.074],
       corpus_id: "blind-fill-v2", corpus_provenance: "BLIND-FILLED",
       clean_corpus_independent_of_predicate: true,
       heldout: {fired: 1, n: 22, wilson: [0.001, 0.216], slice: "close-ended restricted schemes"},
       marginal_ffr: 0.010, conditioned_on: ["P-0007"]}
  liveness: {kill_case: "mutants/P-0041-kill.xlsx", pass_case: "clean/blind_fill_017.xlsx"}
  qualified_against:
    template_sha256: "7d9a…"        # every element here is part of the predicate's IDENTITY
    template_label: "FME_02012026"
    regulation_version: "2026-01-30"
    circular_corpus_snapshot: "2026-08-10T00:00Z"
    circulars_unreadable: 10        # of 399 — a permanent declared gap this predicate inherits
    evaluator_version: "0.4.1"
    proposer: null                  # kind=proposed: {model_id, date, prompt_sha256}
state:          ACTIVE              # ACTIVE | PROVISIONAL | QUARANTINED | WITHDRAWN
withdrawn_reason: null              # {rule_amended, ffr_exceeded_threshold, superseded_by, source_schema_changed}
```

### 4.2 The language — DECIDED: CEL, admitted subset only, in the three-slot envelope

*Alternative it beat, and it is the execution-substrate lane's own recommendation:* **plain Python plus a
data-validation framework**, which wins on expressiveness and developer speed and loses on four
independently decisive grounds. (i) **The settled fraction stops being computable** — you cannot statically
determine which fields a Python function reads, so the product's headline becomes an *estimate*, and this
corpus is a monument to what happens when a coverage claim is inferred rather than derived. (ii) Executing
model-written Python **requires a sandbox**, and the sandbox layer is where the 2026 CVEs are. (iii) The
predicate stops being auditable — the library screen shows a function body, not a rule. (iv) Mutating
arbitrary Python has a high, unbounded equivalent-mutant rate, versus a ~20-production grammar with
enumerable operators. The language definition states verbatim that CEL programs are **"terminating: CEL
programs cannot loop forever"** and **"side-effect-free"**, and the precedent that settles whether this is
a real engineering choice is **Kubernetes ValidatingAdmissionPolicy, GA in v1.30** — model-free CEL policy
over structured data, evaluated in-process, no container per check.

Runners-up, each with its specific loss: **Rego/OPA** on readability and host language (reconsider only if
the stack moves to Go); **Starlark** decisively, because a Starlark predicate has local state, so *"which
fields does this predicate read?"* stops being a static question; **JSONLogic** on types, dates and regex
(its *shape* — a rule is a tree — was stolen for the envelope); **SpEL** outright on security; **Z3** as a
category error (it answers *"is this predicate ever falsifiable"*, not *"is this filing correct"*, and is
adopted for G3 instead); **Drools / ZEN / json-rules-engine** because a rule engine's core competence is
conflict resolution and chaining, and **our architecture forbids exactly that** — every predicate must be
independently scored and independently attributable, and chaining makes both incoherent.

**Runtime: `celpy` (`cloud-custodian/cel-python`, Apache-2.0), pinned by PyPI name and wheel hash** — two
different projects live at a path called `cel-python`, which is a real footgun — with `cel-expr-python`
(Apache-2.0, a wrapper over the official CEL C++) as the drop-in when conformance exactness matters more
than deployment simplicity. **Whether `celpy` passes the CEL conformance suite is NOT-FOUND on its
repository page; both must be run against the suite before commitment**, because if they diverge *on error
semantics specifically*, the rule-2 guard behaves differently between them.

**The sandbox question mostly dissolves, and that is the point.** With a restricted language there is no
model-generated Python to contain: CEL *is* the sandbox — terminating, side-effect-free, no I/O, exactly
two bound names, plus a step-count budget and a wall-clock kill. Choosing the restricted language deletes
the hardest sandboxing problem instead of solving it. What remains is the parser tier, an ordinary
container-hardening exercise.

**The predicate population, stated correctly.** There are **24 candidate correctness predicates, of which
15 are exactly settleable, 2 are settleable only after a declared normalisation (NFKC, `U+2011 → U+002D`,
strip, case-fold) that carries its own measured false-failure rate, and 7 are not settleable from the
artifact at all.** Four of the settleable ones need capabilities the admitted grammar lacks and become
**host functions** — named, deterministic, individually versioned Python with their own test suites and
their own kill rates: `reg_resolves(kind, number)` (tri-state; **never resolves live at verdict time,
always against a content-addressed snapshot**), `gstin_valid(s)`, `template_current(hash)`, and
`nav_interval(scheme_type, open_closed, tenure)` — which **must be able to return `UNDERSPECIFIED`**,
because reg 51(1) ends *"in such manner as specified by the Authority"* and a system that resolves that
delegation into a concrete interval is asserting something the regulation does not say. **A host function
may be added only by a human, is never generated by a model, and must return a third value wherever its
answer can be unknown.** The set is closed at evaluation time.

### 4.3 The five gates — C16, DECIDED, in this order

```
G0  SCOPE FAITHFULNESS   verbatim clause quote locates deterministically; every proviso, exception
                         and cross-reference in the span is either implemented as a branch or
                         declared as a NO_PREDICATE(not_yet_synthesised) emission. Neither ⇒ REJECT.
                                                                                  [structural · free]
G1  EXECUTES AND BINDS   runs on the corpus without error; every key it reads exists in the induced
                         schema; cells_bound > 0.                                 [mechanical · free]
G3ᵖ NON-DEGENERACY,      Z3: trivially-true iff ¬P is UNSAT; always-flag iff P is UNSAT; redundant
    PROOF ARM            iff P₁ ∧ ¬P₂ is UNSAT. `unknown` ⇒ unproven, never "non-degenerate".
                                                                                        [proof · cheap]
G2  SEEDED-DEFECT KILL   KR = K/O over mutants verified OBSERVABLE by recalculation, under a declared
                         versioned fault model, reported as a per-fault-class VECTOR plus U/G, plus
                         marginal kill over B0 ∪ B1 ∪ B2.                         [empirical · expensive]
G3ᵉ NON-DEGENERACY,      seed a 10% control sample into fields the predicate does NOT read; count
    CONTROL ARM          spurious fires; hypergeometric random-flagger adjusted precision.
G4  FALSE-FAILURE RATE   FFR on a corpus whose provenance ≠ SELF-AUTHORED, with n, a Wilson interval,
                         clean_corpus_independent_of_predicate, a structurally-distinct held-out
                         slice reported separately, and the MARGINAL FFR conditioned on the
                         already-admitted set.                                        [empirical]
```

**Why five and not four.** G1 — *executes without error, every key exists in the induced schema,
`cells_bound > 0`* — is a separately testable admission condition that the four-gate versions folded
silently into the kill-rate gate, and **it is precisely the condition whose absence produces the vacuous
pass.** It is nearly free and proves nothing on its own; it is a gate so that its absence is impossible
rather than merely unlikely.

**Why this order — G7, DECIDED.** G0 and G1 are free and reject the failure classes the expensive gates
cannot see, so they run first. G3's proof arm runs before G2 because a predicate Z3 proves unfalsifiable
should never consume a mutation budget. G2 is the expensive step. G3's empirical arm needs G2's harness
already warm. G4 runs last because it needs the corpus and the already-admitted set.

**Two different thresholds for the same gate, and they are different tests — C17, DECIDED. State both,
report both attrition numbers separately.**

| Test | Threshold | Question it answers |
|---|---|---|
| **The settling experiment (E6)** | `K/O > 0` **and** marginal kill strictly greater than `B0 ∪ B1 ∪ B2` | *Can a model-proposed candidate fire at all, and does it beat the free baselines?* |
| **Registry admission** | `K/O ≥ 0.80` on the fault classes the predicate **claims** to cover | *Is this check good enough to be applied to a regulated filing?* |

A predicate at `K/O = 0.05` survives the experiment and fails the registry. Both numbers are published; a
document that quotes one attrition figure has quoted the wrong one.

**The scoring, and why it is strictly better than the formula it replaces.**

```
GENERATED G · UNOBSERVABLE U (recalculated grid identical to clean) · OBSERVABLE O = G − U
UNREACHABLE R (observable, but touching no field any admitted predicate reads) · KILLED K
KILL RATE  KR = K/O   ← the headline. NEVER K/G.
REACHABLE  RKR = K/(O − R)          UNOBSERVABLE RATE  UR = U/G   ← a property of the OPERATOR MIX
```

`MS = |killed| / (|mutants| − |equivalent|)` requires `|equivalent|`, which is undecidable in general.
`K/O` needs no such term, **because our mutants are data: "observable" is a *diff*, measured by
recalculation, whereas "equivalent" is a *theorem*.** The filter is not optional — **3,512 of 7,500
(46.8%)** of naively generated spreadsheet mutants in the canonical study produced no observable change.
One measured caution the vocabulary must carry: in the first real run — **19,782 mutants in 2.5 s
(7,946 mutants/second, MEASURED)** — every arithmetic operator killed at exactly **18.1%**, identical to
the fraction of sites inside the field graph. For identity predicates, **kill rate measures predicate
*reach*, not predicate *quality*, and the report must say which it is showing.** Every suppression is
logged with its reason; an undeclared suppression is a coverage lie.

**Gate status, mapped, because the four-gate numbering is still in circulation and does not line up:**

| Five-gate name | Old name | Status |
|---|---|---|
| G0 scope faithfulness | GATE 0 | SPECIFIED |
| G1 executes and binds | folded into GATE 1 | PARTIALLY BUILT (evaluation built; the AST both-ways check specified) |
| G2 seeded-defect kill | **GATE 1** | **BUILT** — 19,782 mutants, 2.5 s, `KR` reported with its observability term |
| G3 non-degeneracy | **GATE 2** | PARTIALLY BUILT — the vacuous-bound rejection is built; Z3 is specified |
| G4 false-failure rate | GATE 3 | SPECIFIED |

**And the sentence that survives from the brief's sharpest claim, in its corrected form:** *where a
programmatic oracle exists we do not need a model; where it does not, we manufacture labels by seeding
faults rather than by asking one.*

### 4.4 What a predicate carries permanently

Everything in `qualification`, `qualified_against`, `liveness_witness` and `external_deps` is part of the
predicate's **identity**, not metadata about it, and all of it is visible on the predicate-library screen:
the clause with FRBR URI, `eId` and the verbatim quote that located it; the code and its `sha256`; the kill
rate **with its denominator and its per-fault-class vector**, the fault-model version and the unobservable
rate; the degeneracy verdict, the Z3 counterexample and the random-flagger adjusted precision; the FFR as
`(rate, corpus_id, corpus_provenance, n)` **plus a two-sided Wilson interval**, with
`clean_corpus_independent_of_predicate` and the held-out slice beside it; the marginal FFR conditioned on
the admitted set; for model-proposed predicates the model id, date and prompt hash — so a re-synthesis
under a drifted model is a **diff, not a mystery**; the admission date and admitter; and the coverage gap
it inherits (`circulars_unreadable: 10/399`). **Two things the record must never contain: a bare percentage
anywhere, and a `SELF-AUTHORED` FFR rendered as a number.** Rejections are kept, not discarded: a candidate
failing any gate becomes a `rejection` row carrying the rejecting gate, the measured number, the cells it
would have covered and the obligation it claimed — that row *is* `no_predicate.failed_qualification` and
the report's `counterEvidence[]`.

### 4.5 Versioning against a changing template

**Version churn is not a risk. It is scheduled, and it has already happened.** The template's own
financial-year vocabulary runs out at 2028-29; **23.1% of circulars amend an earlier instrument**; and the
**29th IFSCA Authority Meeting of 24 July 2026** (VERIFIED-AT-SOURCE, dated 17 days before this
specification) decided that NAV periodicity for close-ended Restricted Schemes *"may be enhanced by the FME
from semi-annual to annual, subject to prior approval of at least 75% of the investors in the scheme by
value of their investments"* — which lands directly on the most sophisticated predicate in the set, and
**the owed frequency now depends on a fact the workbook does not collect.**

The failure this policy exists to prevent, concretely: that predicate **does not error, does not abstain,
and keeps computing a date difference against a rule that no longer exists.** A filer who lawfully moved to
annual NAV gets a false failure; a filer who moved without approval gets a silent pass. Both outputs are
clean, confident and well-formed.

| Rule | Statement |
|---|---|
| **V1** | Keys are label-anchored, never coordinate-anchored. A version bump is a **re-resolution**, not a rewrite. Unresolvable keys enter an explicit `UNRESOLVED` state that **blocks** the predicate; they never silently rebind |
| **V2** | Every element of `qualified_against` is part of the predicate's identity |
| **V3** | Any change to any element of `qualified_against` moves the predicate to `PROVISIONAL`. **It still runs**, so detection is not lost, but its measured numbers are hidden and replaced by *"not re-qualified for this template version"*, and **it does not count in the settled numerator** (`no_predicate.not_yet_requalified`) |
| **V4** | **Therefore the settled fraction falls when the template changes.** That is correct. A system whose coverage silently persists across a version boundary is lying — and the step-downs are the most credible thing on the chart, because they are the only evidence the system notices when the world moves |
| **V5** | Liveness witnesses are replayed, and a predicate whose `kill_case` stops dying is **quarantined automatically**. Its limit, stated honestly: applied to the NAV-frequency predicate, the `kill_case` was built against the semi-annual rule and would still die, because the mutant and the predicate moved together. **V5 alone does not catch a rule change. That needs V6** |
| **V6** | Watch the **instrument stream**, not just the instrument. Reg 51(1)'s delegation means the rule can change by circular without the regulation changing. A daily content hash of the circular and Authority-meeting pages; any new instrument citing a regulation a predicate claims to implement moves it to `PROVISIONAL` **automatically and pessimistically**; a human clears it. This is a diff-and-flag job, not an NLP problem, and it is the only mechanism that would have caught 24 July 2026 |
| **V7** | `withdrawn_on` / `withdrawn_reason` exist on every predicate, drawn from `{rule_amended, ffr_exceeded_threshold, superseded_by, source_schema_changed}`. A registry without a withdrawal state silently carries dead checks — which is exactly what a regulator's quarterly deactivation list is a public admission of |

**What happens when a predicate silently becomes untestable** is therefore covered twice and neither
mechanism is sufficient alone: V5 catches *the artifact moved under us* (parser drift, renamed sheet,
selector miss), V6 catches *the rule moved under us*. The residual class — the rule moved **and** the
witness moved with it — is caught by neither, is named here, and is the reason the instrument watcher is
pessimistic rather than clever.

---

## II.5 — THE REPORT

### 5.1 The envelope and the body

```jsonc
// DSSE envelope · payloadType "application/vnd.in-toto+json"
{ "_type": "https://in-toto.io/Statement/v1",
  "subject": [ { "name": "filing",   "digest": { "sha256": "<hash of the workbook AS RECEIVED>" } },
               { "name": "template", "digest": { "sha256": "7d9a1960085785ee…" } } ],
  "predicateType": "https://<ns>/filing-settlement-attestation/v1",
  "predicate": {
    "assessor": { "id": "https://<ns>/verifier/0.4.1", "thirdParty": false,
                  "components": { "registryRoot": "sha256:…", "schemaInducerVersion": "1.4.0",
                                  "faultModelVersion": "v3", "extractorModel": null } },
    "timeVerified": "2026-08-14T09:12:44Z",
    "expires":      "2026-11-14T00:00:00Z",
    "runState":     "VALID",
    "livenessProof": { "canariesRun": 280, "canariesPassed": 280 },

    "scope": {
      "denominator": { "source": "induced-from-template-unlocked-mask",
                       "generatorRule": "v3",
                       "unit": "CELL",
                       "fieldSurface": 3747,          // MEASURED
                       "cellsTotal":   3747,          // == fieldSurface; DISALLOW * applies to it
                       "computedTwiceAgreed": true },
      "plannedSelection": { "includeAll": true, "exclude": [] },
      "actualSelection":  { "includeAll": true, "exclude": [] },
      "selectionDelta":   []
    },

    "settledFraction": {
      "cellsTotal":  3747,                            // MEASURED
      "outOfScope":  0, "informational": 0,
      "inScope":     3747,                            // = cellsTotal − outOfScope − informational
      "settled":     { "pass": 2361, "fail": 12, "total": 2373 },   // total MEASURED (harvest), see
                                                                    // caveat; the pass/fail split is
                                                                    // illustrative, not a measurement
      "unsettled":   { "indeterminate": 0, "notRun": 0, "noPredicate": 1374, "error": 0 },
      "fraction":    0.6333,                          // DERIVED; meaningless without the counts above
      "aggregate":   "incomplete",
      "admissibilityCaveat":
        "None of the 280 predicates producing this number is admitted under gate G4: no false-failure
         rate has been measured for any of them on a corpus we did not write. Under this
         specification's own admission rule the currently admissible predicate set is empty and the
         currently defensible settled fraction is 0%.",
      "denominatorWarning":
        "Out-of-scope determinations are filing-specific, so the denominator varies between filings.
         Settled fractions are not directly comparable across filings."
    },

    "items": [
      { "id": "portfolio.tbl31.row[7].total_value", "pointer": "/predicate/items/0",
        "cell": "3. Portfolio!O7",
        "obligation": { "id": "OBL-014", "frbrUri": "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30",
                        "eId": "reg_27__para_1", "sourceDigest": { "sha256": "…" } },
        "state": "FAIL", "reason": null, "severity": "ADVISORY",
        "method": "TEMPLATE_DIFF", "warrant": "DETERMINISTIC", "provenance": "COMPUTED",
        "cellsBound": 12, "scopeIncomplete": [],
        "evaluations": [ { "predicate": { "id": "P-0041", "version": 3, "digest": { "sha256": "…" } },
                           "state": "FAIL", "elapsedUs": 41,
                           "witness": ["3. Portfolio!O7"],
                           "ffr": { "rate": 0.021, "n": 96, "wilson": [0.006, 0.074],
                                    "corpusId": "blind-fill-v2",
                                    "corpusProvenance": "BLIND-FILLED" } } ],
        "anchors": [ /* §5.2 */ ], "override": null } ],

    "counterEvidence": [
      { "kind": "rejected-predicate", "obligation": "OBL-031", "candidate": "sha256:…",
        "rejectedBy": "G4", "measured": { "ffr": 0.382, "n": 228, "corpusProvenance": "REGISTER-DERIVED" },
        "note": "registration-number format regex; 87 of 228 live FMEs fire. Would have covered 41 cells." } ],

    "scopeCaveats": [
      { "reason": "no_predicate.not_yet_synthesised", "kind": "declared-proviso",
        "predicate": "P-0041", "eId": "reg_26__para_2", "charSpan": [10422, 10597],
        "quote": "Provided that this requirement shall not apply in case of a fund of funds scheme…" } ],

    "verdict": { "state": "EXCEPTIONS_NOTED",
                 "policy": { "file": "pervasiveness-policy-v1.json", "version": "v1",
                             "K": "PLACEHOLDER", "T": "PLACEHOLDER",
                             "status": "PLACEHOLDER — K and T have no argued basis yet" } },

    "residue": { "survivors": 12, "faultModel": "v3",
                 "adjudicationRecord": "sha256:…", "manifest": "sha256:…" },
    "declaredGaps": [ { "kind": "unread-sources", "detail": "10 of 399 circulars are scanned images" } ],
    "boundedSilenceStatement": "Had additional predicates been executed, other matters might have been
      reported. This report states only the results of the predicates listed, and makes no representation
      that the predicate set is sufficient for any purpose.",
    "purposeStatement": "This report relates only to the cells enumerated in scope.denominator and does
      not extend to the filing taken as a whole.",
    "deceptionStatement": "This system detects error, not deception. Every check here is a consistency
      check over a self-reported document. A coherent liar passes all of them.",
    "summaryIsNotSubstitute": true
  } }
```

**The field that is absent by design: there is no `result` and no `status`, and there never will be.** The
top-level object of the predicate is `scope`. **There is nowhere in the schema to write "pass", so no
downstream consumer can render one.** Schema-level prohibition beats copy discipline because it survives
the screenshot, the API integration and the intern — and it is backed by a build gate that greps every
user-facing surface for tick glyphs and all-clear language. The four statement fields are **required by
schema**: making a disclaimer a mandatory field rather than a template string is the cheapest possible way
to guarantee it survives contact with a marketing page. And `NONE ≠ NOASSERTION ≠ absent` is enforced by
the JSON Schema: `[]` means *we determined there are none*, `null` means *we make no claim*, and an omitted
field is a schema violation the validator rejects.

**On the headline.** The hero is `<F> failures across <S> checks` and `<U> fields were not checked`, in
equal type, populated from the measured triple **2,373 / 1,374 / 3,747**. It is never populated from a
predicate-enumeration count. The reason the fraction had to go is that the decidable set is unbounded and
mechanically expandable — one predicate per formula-evaluating cell, per data validation, per shipped
vocabulary is `505 + 54 + 15 = 574`, taking a hand-classified 24-predicate ratio to `574 / 581 = 98.8%`
without writing a single interesting check. **That figure is DERIVED — an enumeration argument, not a
run** — and it exists in this specification only to demonstrate that the fraction is manipulable.

**And the corrected sentence about what the 63.3% means, which is stronger than the version it replaces:**

> *"280 predicates are mechanically derivable from the regulator's blank template with no model, and they
> touch 2,373 of 3,747 filer-editable cells. **None of them is admitted yet**, because no one has measured
> a false-failure rate for them on a corpus we did not write. That is the point: the number you are looking
> at is what every compliance product ships, and it is the number our own gate is designed to refuse. Watch
> what happens to it after qualification — that delta is the product."*

Two composition facts travel with it or it is not quoted: **2,329 of the 2,373 settled cells (98.1%) come
from the 53 validation predicates, not the 227 arithmetic ones**, and the validation-carried share is
weaker per cell — which is exactly what G3 exists to reject. And the cross-workbook figure **515** is
always published with its per-workbook distribution attached, never alone, because two of the nine
workbooks have zero formulas and one has zero validations too.

### 5.2 The provenance anchor

Docling's `ProvenanceItem` is adopted **verbatim** for the PDF class (`page_no`, `bbox{l,t,r,b,coord_origin}`,
`charspan`, optional `table_cell` offsets), which removes a translation layer and a coordinate-origin
guess, and the union is extended with two locator kinds document AI does not model: **`xlsx_cell`**
(carrying `formula.encoding ∈ {TEXT, SHARED_MASTER, SHARED_DEPENDENT, ARRAY, NONE}` — not decoration:
recording the encoding is what makes the 294-versus-505 undercount impossible to repeat silently) and
**`register_record`**. The register anchor carries **both `raw_value` and `normalised_value`, plus the
transformation list** — mandatory, because one live regulated entity's registration number contains
`U+2011 NON-BREAKING HYPHEN` rather than `U+002D`: visually identical, byte-wise different, invisible in
any log or screenshot. **A system that stores only the normalised form has destroyed the evidence that its
own normalisation was load-bearing.**

### 5.3 Exact relationship to the four standards

| Standard | What we take | What it cannot do — exactly |
|---|---|---|
| **OSCAL** (CC0 1.0 — no licence obstacle to profiling, forking or embedding) | `reviewed-controls` (planned versus actual scope with the delta visible); `observation.methods` and `origin-actor.type ∈ {tool, assessment-platform, party}`, so it can say *a machine asserted this*; `assessment-assets` for the registry version; `observation.expires`; and the **POA&M model as the unchecked panel's interchange format** — reason plus what would make it checkable is exactly a `poam-item` plus a `risk.response.lifecycle`. Tooling: `compliance-trestle`, Apache-2.0, ships pydantic models plus detached JSON signing | `finding-target.status.state` is a **closed two-value enum `{satisfied, not-satisfied}`** — the one field this product exists to add states to. Non-coverage is expressed by omission plus free-text scope, and `findings` was made optional in 2021, so **an OSCAL AR with zero findings is schema-valid and means nothing in particular.** Its ontology is security-control-shaped and **has no cell.** *The useful negative result:* OSCAL was asked for exactly this vocabulary in 2021, citing XCCDF's result states, and resolved it by adding an **open `reason` token** rather than states. Encoding our third state there would get OSCAL's syntax without OSCAL's validation — a validator would accept `{"state":"satisfied","reason":"actually-we-never-checked"}`, which is the worst of both |
| **ISRS 4400 (Revised)** — agreed-upon procedures | ¶30(j)'s **bounded-silence sentence as a required schema field**; ¶30(h)'s disclaimer of procedure appropriateness; ¶13(f)'s finding-is-objectively-verifiable definition; ¶32(b)'s "reading the summary is not a substitute"; and Appendix 2 Illustration 2's stated circumstances — **the regulator is the intended user and the entity it oversees is the engaging party**, which is our exact two-party model, already contemplated, with a report template supplied | The report is **human prose in a two-column Procedures/Findings table**: no schema, no closed vocabulary, no machine-readable form, no fraction, **no per-procedure error rate.** ¶A56's not-performed declaration is a *may*, not a *shall*, and it is free text. And **every procedure is agreed with the engaging party in advance, with its adequacy expressly disclaimed** — the denominator is negotiated, where ours is induced |
| **in-toto / DSSE** — **Apache-2.0, VERIFIED-AT-SOURCE** (the LICENSE file was opened and quoted) | The envelope; `subject[]` carrying **both** hashes, because a verdict against template v3 is meaningless if the entity filed on v4; and the deepest borrowing, the **`DISALLOW *` closed-world principle** — our L1-induced schema **is** the layout, which is why the closure is possible for us | Its subject is a build pipeline; steps are commands and artifacts are files. No notion of a partially-verified artifact, no reason codes, no coverage semantics in the envelope. Its standard `test-result` predicate has `passedTests[]`, `warnedTests[]`, `failedTests[]` and **no `skippedTests[]` — the standard test attestation cannot express a test that did not run** |
| **CycloneDX** | Three things, none of them the one usually cited. **(a)** `compositions.aggregate` demoted to one roll-up header field (six states in 1.3, ten in 1.5 — not ten in 1.2). **(b)** `declarations` (CDXA, 1.6): `assessors[].thirdParty` — *"a value of false indicates a self assessor"* — `attestations[].map[].{claims, counterClaims, conformance}`, and `standard.requirements[]` with regulations explicitly in scope. **(c)** 1.7's `citation` with **RFC 6901 JSON Pointers**, the right idiom for addressing a verdict to an exact location | `aggregate` is aggregate, not per-item: it says the *set* is incomplete and cannot say *which* component was not examined or why. CDXA's `conformance` is a **continuous score in [0,1] with free-text rationale — there is no discrete "not assessed" state, and a score of 0 is indistinguishable from "we never looked."** A float plus prose is exactly the interface we are arguing against |

**Projection rule, so the loss is explicit and auditable.** `PASS → satisfied`; `FAIL → not-satisfied`;
`INDETERMINATE / NOT_RUN / NO_PREDICATE →` an `observation` with our reason as a `prop`, **no finding**, and
a matching `exclude-controls[]` entry; `OUT_OF_SCOPE →` an `exclude-controls[]` entry only;
**`INVALID` → not representable at all.** Any party reading only the projection sees a smaller, cleaner
report than the truth, so the projection carries a **mandatory `metadata.prop` flagging it as lossy and
naming the URI of the normative artifact — in the file, not in a README.**

### 5.4 Signing

**DECIDED: the filer signs, with a detached key, over the report JSON. The vendor signs nothing about the
filing; the vendor appears only as `assessor.id` with `thirdParty: false`.** *Alternatives it beat:* **the
vendor signs** — the vendor would be attesting to a regulated filing it did not prepare, and **if an FME
shows an inspector a signed attestation over a filing that was wrong, the signature is the first exhibit**;
**Sigstore keyless** — keyless signing binds an identity into a public certificate published permanently,
so the fact and timing of a named entity running a pre-submission compliance check becomes world-readable
and correlatable (if a log is wanted, run a **private instance operated by the supervisor**, publishing
only salted hashes of filing identifiers); **no signature at all** — then the coverage claim is marketing
and the boundary can be restated later. Envelope: **DSSE + in-toto Statement v1** over **JWS/JSF**, because
it is Apache-2.0 (VERIFIED-AT-SOURCE), it is what the attestation ecosystem already speaks, and `subject[]`
naturally carries the two hashes. `--tlog-upload=false` is asserted in a test.

**The residual item is legal review of that decision, not the decision itself. OPEN — USER DECISION:
is a real FME prepared to sign, and does your legal review accept filer-side self-attestation as the signing
model?** Until it is answered, the demo signs a synthetic filing with a demo key and the demo script says
so out loud.

**Byte-identity — G12, DECIDED.** `verify` re-runs the pipeline pinned to
`{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha, evaluator_version,
fault_model_version, tool_versions{python, lxml, openpyxl, celpy, z3}}` and asserts a byte-identical
report. **LibreOffice is not in that list and is not on the verdict path** (§II.1.2). The four sources of
non-determinism are removed rather than tolerated: the mutable register is pinned by snapshot hash and the
host function never resolves live at verdict time; wall-clock time is an input recorded in the manifest and
CEL binds no clock; iteration order is fixed by RFC 8785 canonicalisation and explicit sort keys; and there
is no floating point, because money is `int64 MILLI_USD_MILLION` and tolerances are integers. **A model
call is never on the re-derivation path**: if a filing had attachments, the *facts* L2b produced are
content-addressed and pinned, and `verify` replays those facts rather than re-calling the model. That is
the only honest treatment — a model output is an input to the verdict, not a step of it.

---

## II.6 — THE SELF-CHECK LAYER

### 6.1 The claim, restored

> **No assurance artifact in existence carries evidence that the instrument that produced it was working on
> the specific document it examined. A clean audit opinion does not. An SBOM does not. A validation report
> does not. Ours refuses to issue a verdict unless every check has just demonstrated, on your file, that it
> can still catch the fault it was admitted for.**

That sentence is falsifiable, it is not a novelty claim about a mechanism, and it needs no citation — the
mechanism is two extra executions per predicate. The hedged version ("we self-test") buried the actual
claim, which is that **the verdict is conditioned on a proof obtained from the artifact under test, in the
same execution, and is withheld when that proof fails.** The nearest named prior art is SRE synthetic
monitoring and hardware built-in self-test, not anything in the testing literature. *A formal-methods
citation for vacuity detection is **UNVERIFIED** and must not be asserted.*

### 6.2 The mechanism

```python
def verdict_with_self_check(filing, predicates):
    result = run_all(filing, predicates)
    silent = []
    for p in predicates:
        # instantiate THIS predicate's stored kill_case against THIS filing's cells,
        # in the in-memory fact table — never against the file, never re-serialising it
        mutant = p.liveness.kill_case.apply(filing.facts)
        if not run_one(mutant, p).state == "FAIL":
            silent.append(p.id)
    if silent:
        return Report(run_state="INVALID", reason="error.canary_silent",
                      dead_predicates=silent,
                      settled_fraction=None,      # not zero. Not omitted. NULL.
                      verdict=None)               # a finding about us, not about the filing
    return result.with_liveness_proof(run=len(predicates), passed=len(predicates))
```

**Why it is the answer and not a nicety.** It runs **on the artifact under test, not on a training
corpus**, so it catches parser drift, selector misses, renamed sheets, hidden-sheet truncation, encoding
changes and empty-set vacuity **for this file** — the failure class that produced five documented instances
inside this project's own research, three mechanisms, all under-counting in the same direction. L4
qualifies predicates **at admission, against the corpus of that moment**; nothing else re-checks at run
time that the predicates still bind to anything.

**Cost.** Canaries operate on the in-memory fact table, not the file. At the measured harness throughput of
**7,946 mutants/second (MEASURED)**, 280 canaries ≈ **35 ms** (DERIVED from a measured rate; the canary
loop itself is not yet built) against a ~30 ms baseline pipeline. **There is no reason not to.**

**What makes a run `INVALID`** — the complete list, and each is an engineering incident rather than a
filing outcome: a container guard trip · structural disagreement between the readers on
`{n_sheets, sheet_names, hidden_sheets}` · an unbound template · `cells_bound == 0` on any predicate · a
predicate raising inside `expr` · **a silent canary** · a closure violation · the two denominator
computations disagreeing. An `INVALID` run renders a report that states which of these fired, carries
**no settled fraction at all**, and sets the aggregate verdict to `null`.

### 6.3 The residue set, and the class that is the product

```
1. Take the filing under test, F.
2. Generate mutants of F under a declared, versioned fault model.
3. Adjudicate each: INNOCUOUS (still correct) / WRONG (materially false).   <- the only human step
4. Run the full admitted predicate set + every admitted relation on every WRONG mutant.
5. RESIDUE := { WRONG mutants that no predicate and no relation rejects }
6. Report |RESIDUE| and, for each survivor, the class of falsehood it represents.
```

**It cannot be inflated by boring checks**, because the residue is populated by falsehoods consistent with
every arithmetic relation in the file — which is exactly the property the fraction lacks. **It converts a
hand classification into a measurement**, and it is **reproducible given the published fault model *and the
published adjudication record*, both content-addressed** — step 3 is a human INNOCUOUS/WRONG judgment,
it is one-time per fault-model version, and it is auditable per mutant by content hash. Saying "a third
party can re-run it" without naming the adjudication record would repeat the error this whole document
exists to correct.

**Three mutant classes, and the third one is the product.** Code mutation testing has one nuisance class,
the equivalent mutant. Data fault seeding has two, and they point in opposite directions. **INNOCUOUS** —
a data edit that leaves the filing correct (reordering rows where order carries no meaning, reformatting a
number, rewording a rationale); like equivalent mutants these cannot be killed and **must leave the
denominator**, or the score is understated. **WRONG-AND-KILLABLE** — the ordinary case. And:

> **A prescribed return is a closed arithmetic system. We can construct, and exhibit, a family of filings
> that are internally perfect under every relation the regulator's own template encodes and every relation
> we have added — and materially false. That family is non-empty by construction, its size is measurable,
> and measuring it is the first quantitative statement anyone has made about the limit of document-level
> verification for a regulated filing.**

In code mutation testing a mutant that changes behaviour is in principle killable by *some* test. Here, a
mutant can change the **truth** of the artifact and be **provably unkillable by any predicate over the
artifact alone.** That is not a coverage gap; it is a theorem about the artifact class, and it is the
reason the risk *"the residue set comes back empty"* is graded **Low → structurally impossible** rather
than merely unlikely. It is also the honest content of the unchecked panel: that panel should not list
reasons, it should list **demonstrated survivors** — a coordinated misstatement propagated through all 181
cross-sheet carries and all 35 SUM identities, exhibited, with its content hash.

**And the sentence that stays permanently on the report surface, because it is the boundary the residue set
measures from the other side:** *this system detects error, not deception. Every check here is a
consistency check over a self-reported document. A coherent liar passes all of them.*
