# 02 — THE FOUNDATION PHASES
## P0, P1, P2 and P3 in full · build plan, part 2 · compiled 11 August 2026

**This document specifies P0, P1, P2 and P3 and nothing else.** It uses the phase IDs, the build
numbering, the ordering, the gates, the numbers and the effort figures of `plan/00-decomposition.md`, and
it is written against `plan/01-validation-methodology.md` — whose test taxonomy (§1), negative-control
catalogue (§2), mutation regime (§3), Definition of Done (§4), CI pipeline (§5), fixture strategy (§6) and
declared residue (§7) are referenced **by id** here and never restated. Where this document adds a
catalogue entry it gives the entry's full YAML shape and says it is new. Where it relies on an existing
entry it names the id and stops.

**What these four phases are.** They are the layer under every number the product will ever print. P0
makes the honesty commitments mechanical *before there is code to violate them*. P1 reads the artifact. P2
computes the denominator. P3 builds the two substrates every predicate reads and every kill rate depends
on. Nothing above them can be more trustworthy than they are, and the project's five documented silent
false negatives all live in exactly this band.

**Why this document opens with measurement rather than with a plan.** Under the rule that generates this
whole methodology — *a test that has never been observed to fail is not evidence* — a phase specification
written from a summary of an artifact is a plan that has never been observed to touch the artifact. Every
figure the four phases pin was therefore re-run against the nine workbooks on disk before a single build
was written. Ten figures reproduced exactly. Eight measurements are new. **Four of the eight change a gate
that `plan/00-decomposition.md` had already pre-registered**, and one of those four shows that the phase
gate guarding every kill rate in the programme, as written, cannot fail. Those are §0.

---

# §0 — WHAT WAS MEASURED BEFORE ANYTHING WAS DECIDED

**Script.** `/Users/abishaikc/Gift/research/scripts/foundation_probe.py` — **on disk, runnable now**:

```
$ /Users/abishaikc/Gift/.venv/bin/python research/scripts/foundation_probe.py
```

It moves to `tools/measure/foundation_probe.py` at P0-B2 and becomes `make measure-foundation`, whose
output is diffed against the committed `docs/measurements/P0-foundation-probe.md`. Interpreter
`/Users/abishaikc/Gift/.venv/bin/python`
(`lxml`, `openpyxl` 3.1.5). Date 11 August 2026. Artifact
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx`, nine files, unmodified.

## §0.1 — What reproduced exactly

Every one of these is a figure the spec or the methodology already carries. All reproduce. They are
restated here only to establish that the instrument used for §0.2 is the same instrument that agrees with
the corpus everywhere else.

| Quantity (FME `7d9a1960…`) | Value | Where it is already pinned |
|---|---|---|
| formula-bearing cells / authored / shared dependents | **505 / 294 / 211** | `test_schema_constants` |
| data validations, main + `x14` | **35 + 19 = 54** | `test_schema_constants` |
| `'7. AML-CFT'` validations, main + `x14` | **0 + 5** | NC-P01 |
| list-type validations | **22** | `test_schema_constants` |
| merged ranges | **252** | `test_schema_constants` |
| defined names, of which `#REF!` | **12, of which 4** — `ExternalData_1/_2/_3/_17` | spec §II.1.3 |
| sheets, hidden, protected | **10, 1 (`Dropdown`), 9** — `Dropdown` alone unprotected **and** hidden | spec §II.1.3 |
| unlocked style ids | **105** | spec §IV.4.3 |
| **field surface (unlocked ∧ non-formula)** | **3,747** — Portfolio 1,698 · Investors 897 · PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22 | `test_schema_constants`, the denominator |
| all unlocked cells in used ranges (the other definition) | **3,755** | spec §II.1.3 |
| cached values present on formula cells | **505 of 505** | spec §II.1.9, gate G-EVAL |
| field surface, other eight workbooks | **2,255 · 1,599 · 3,537 · 0 · 459 · 481 · 162 · 8** | methodology §0.3 |

The last row is reproduced by the same code path that produces 3,747, which is why it belongs in §0.1 and
not in §0.2 — it is a re-measurement, not a discovery. **It is not P2's number.** P2's number is the same
quantity computed *twice, by two independent code paths*, and nothing here has done that.

## §0.2 — Eight new measurements. Four of them change a gate

### N1 — **The blank template's 505 cached values are 301 numeric zeros and 204 copies of the string `"NA"`. There is not one non-zero numeric value among them.** · MEASURED · changes G-EVAL

```
by cell type : {'n': 301, 'str': 204}
distribution : {'num:0': 301, 'str:NA': 204}
non-zero numeric cached values: 0
```

`plan/00-decomposition.md` P3 makes this the phase and gate **G-EVAL**, barrier 2 of five: *"recalculate
the blank template and compare against the cached values present on 505 of 505 formula cells"*, and
`plan/01-validation-methodology.md` §1.4 D3 makes the same comparison a blocking differential. Spec §7
lists it first among *"measurements before any number is quoted"* and states that **no kill rate may render
before it passes.**

**As written, it cannot fail.** An evaluator that returns integer `0` for every numeric formula and the
string `"NA"` for every `IFERROR`-wrapped formula reproduces 505 of 505 exactly. So does an evaluator that
treats every function it does not implement as an error — because 204 of the 505 are `IFERROR(…, "NA")`
and the error path *is* the expected answer. So does the specific negative control the decomposition
proposes for this phase: *"an evaluator variant that treats `AGGREGATE(15,6,…)` as plain `SUM`"* returns
`SUM` over an array containing `#DIV/0!`, which is an error, which `IFERROR` catches, which yields `"NA"`
— **the correct cached value.** The named negative control for the programme's second barrier is
inert against the artifact it names.

This is not a drafting slip. It is the project's own failure mode, arriving inside the instrument built to
detect it: a clean, confident, well-formed positive control with no information in it. The corpus already
contains five of these; this would have been the sixth, and it would have sat under every kill rate the
product ever published.

**The consequence, and it is P3's largest single change.** G-EVAL splits into two arms with two
denominators, and the split is recorded in `docs/GATE-CHANGES.md` as an *addition*, never as a lowering —
a threshold may be lowered only by an argument that the old one was wrong (methodology §3.5), and this
argument is that the old one was **weaker than it appeared**, which licenses adding an arm and forbids
removing one. Specified in full at **P3-B4**.

### N2 — **Iterating visible sheets only does not move the FME field surface. It stays 3,747.** · MEASURED · changes P2's golden

`Dropdown` is hidden, unprotected, and holds all 15 vocabularies — and it contributes **zero** cells to the
field surface, because none of its cells carries an unlocked style id. `'9. Compliance Report'` is visible
and also contributes zero. The eight sheets in the per-sheet split are the whole of the denominator.

So NC-D01's break — *"iterate visible sheets only"*, the scope truncation that produces the empty
vocabulary set and the vacuous membership pass — **is invisible in the denominator.** A golden test
asserting `field_surface == 3747` passes against the broken inducer. This is rule **R-GOLD-2**
(methodology §0.2) reaching the denominator: *a golden test asserts values, not only counts.* NC-D01a
already asserts the presence of `Dropdown` and 15 non-empty vocabularies, which is the value assertion that
does the work; what changes is that **the count assertion must never be cited as the guard**, and P2's
gate says so in those words.

### N3 — **On the FME workbook, with no injection at all, readers A and B disagree on 4 of the 8 agreement fields — and 3 of the 4 disagreements are definitional, not instrumental.** · MEASURED · changes P1's design

| field | A (`lxml`, `<c>`/`<f>`/`dataValidation` element walk) | B (`openpyxl` 3.1.5) | agree | what the disagreement is |
|---|---:|---:|:--:|---|
| `n_sheets` | 10 | 10 | ✅ | — |
| `sheet_names` | 10 names | same | ✅ | — |
| `hidden_sheets` | `['Dropdown']` | `['Dropdown']` | ✅ | — |
| `n_cells` | **6,757** | **3,740** | ❌ | **definitional** — A counts `<c>` elements, B counts non-`None` values |
| `n_formula_cells` | **505** | **504** | ❌ | **definitional** — B's naive rule `isinstance(v,str) and v.startswith("=")` loses the one array formula, which openpyxl returns as an `ArrayFormula` object |
| `n_validations` | **54** | **35** | ❌ | **instrumental** — namespace blindness, `UserWarning: Data Validation extension is not supported and will be removed` |
| `n_defined_names` | **12** | **4** | ❌ | **definitional** — B's `wb.defined_names` holds only workbook-global names; the 4 `_xlnm.Print_Area` and the 4 `ExternalData_*` `#REF!` names are sheet-scoped |
| `merged_ranges` | 252 | 252 | ✅ | — |

**A disagreement check that fires on half its fields on day one, on the flagship artifact, for reasons that
are mostly not defects, is a check that will be switched off within a week.** That is how a gate dies: not
by being wrong, by being noisy. And the specified escalation makes it worse than noisy. Spec §III.3.1 F2
and methodology §1.4 D1 both say a non-structural disagreement marks the field and makes every predicate
reading it return `NOT_RUN(not_run.extractor_disagreement)`. **2,329 of the FME workbook's 2,373 settled
cells (98.1%) come from the 53 validation predicates** (spec §III.4.3). Ship the check as literally
specified and the flagship workbook's settled count falls from 2,373 to roughly 44 — permanently, on day
one, because `openpyxl` will always report 35.

> **N3a — the `53` does not reconcile with the harvest, and this document does not resolve it.** · **UNRECONCILED**
>
> Spec §III.4.3's *"53 validation predicates"* is quoted above because it is the corpus's own figure and
> the escalation argument needs its **order of magnitude**, not its exact value. It does not reconcile with
> anything this project will build: FME carries 54 validations, 22 list-type, of which **20 resolve**
> (§0.2 N7), and `plan/03` §0.4's frozen v0 harvest emits **20** membership predicates — not 53. Either
> `2,373` was computed from an enumeration P4-B4 will not ship, or `53` is wrong, and **no document in the
> corpus reconciles them.**
>
> **Ruling.** `2,373` is **not** a measurement of this system until P4-B4 computes it. Until then it is
> `DERIVED-FROM-SPEC`, it may not be pinned as a literal in any golden test, and any surface quoting it
> carries that warrant. The reconciliation is a P4-B4 deliverable
> (`docs/measurements/P4-harvest-distribution.md`, obligation **Y10**), the arithmetic is
> `len(HarvestResult.cells_reachable)` for `7d9a1960`, and **a divergence from 2,373 is a finding to be
> published, not a number to be corrected quietly.** The escalation argument above survives either way: at
> 20 membership predicates the flagship's settled count still collapses under a naive escalation, which is
> all this measurement is used for.
>
> Mechanised by **`ci/golden-literals-are-traceable.sh`** (registry row 17, R5): every integer literal
> compared inside `tests/golden/` must appear either in `plan/01` §0.3's table or in a
> `reports/validation-ledger.jsonl` row. `2,373` appears in neither today, so a golden pinning it fails the
> build. `plan/07` §6 called this *"the fourth impossible control"*; **it is a grep over a ledger.**

The resolution is not to relax the check. It is **P1-B3's competence matrix**: a field is compared only
between instruments *declared competent for that field under a written definition*, a declared-incompetent
instrument's reading is retained as a **pinned positive control** rather than as an escalation, and the
second party for a field no third-party library can read is a **second implementation of ours**. Specified
in full at P1-B3, with the anti-abuse mechanism — because "declare it incompetent" is otherwise a way to
make any inconvenient disagreement disappear.

### N4 — **322 of the FME workbook's 434 `cellXfs` carry no `<protection>` child at all** · MEASURED · sizes NC-D02's blast radius

105 style ids declare `locked="0"`. **7** declare `locked="1"` explicitly. **322 declare nothing** and
inherit the OOXML default `locked="1"` from `cellStyleXfs`, of which there is exactly one, itself carrying
no unlocked protection. 112 `cellXfs` carry `applyProtection="1"`.

An implementation that reads `protection/@locked` and treats **absence as unlocked** adds **2,502**
non-formula cells and returns a field surface of **6,249** instead of 3,747. An implementation that
requires `applyProtection="1"` before honouring `locked="0"` returns a *smaller* number. Both are plausible
readings of the same XML by two competent engineers, which is precisely §7.5's residue — *two independent
implementations sharing a misconception* — arriving at the one quantity the whole product is a fraction of.
P2-B2 therefore fixes the resolution order in `docs/PROTECTION-RESOLUTION.md`, both paths implement it, and
NC-D02d's mutation test is what proves they are two implementations rather than one called twice.

### N5 — **There is a ninth function, and the spec's vocabulary is eight** · MEASURED · changes P3-B4's scope

Function call sites across the 294 authored expressions:

```
ROW 60 · IFERROR 50 · SUM 35 · INDEX 30 · _xlfn.AGGREGATE 30 · ROWS 30 · IF 14 · COUNTIF 5 · _xlfn.SINGLE 1
```

`_xlfn.SINGLE` — the implicit-intersection operator, Excel's `@` — appears once, at
`'1. Introduction'!D92`, which is also **the workbook's only array-encoded formula**
(`<f t="array" ref="D92">`). The encoding census is exact and sums:

```
normal/text 261 + shared/master-text 32 + array/text 1 = 294 authored
shared/empty-text 211                                  = 211 dependents      total 505
32 distinct shared groups, 32 masters, e.g. '3. Portfolio'!O3 = SUM(C3:N3) over ref O3:O12
```

Under the spec's own rule — *"a function outside the vocabulary makes its cells
`NOT_RUN(not_run.source_unreadable)`, and a human decides"* — the vocabulary decision is now a real
decision with a name attached to it rather than a hypothetical. P3-B4 takes it.

### N6 — **`COUNTIF` requires wildcard semantics, and the `D17` defect is located exactly** · MEASURED

```
'1. Introduction'!D17 = SUM(D18:D20)
'1. Introduction'!D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")
'1. Introduction'!D19 = COUNTIF(G54:G63, "*Restricted*")
'1. Introduction'!D20 = COUNTIF(G54:G63,"*Retail*")+COUNTIF(G54:G63,"*Exchange Traded Fund*")
```

Five `COUNTIF` call sites in three cells, five substring patterns, against a scheme-type vocabulary of
**nine** values at `Dropdown!$F$3:$F$11`. That is the regulator's own scheme total missing two of its own
nine legal values (NC-N04) — now with cell references, so it is a fixture rather than an anecdote. It also
means `COUNTIF` must implement Excel wildcard matching (`*`, `?`, `~` escape), which the eight-function
list does not mention, and which is invisible on the blank template because every count is `0` either way
— N1 again, in a second place.

### N7 — **The `22 list-type / 20 resolving` figure reconciles, and the rule that produces it is now written down** · MEASURED · closes a spec open item

Spec §7 lists *"the vocabulary→validation mapping — two lanes imply different counts and neither figure may
be quoted until the build computes it"* as an open measurement. It computes as follows.

| kind | n | `formula1` |
|---|---:|---|
| `x14` list validations pointing at a literal range | **19** | `Dropdown!$D$3:$D$6`, `…$E$3:$E$6`, `…$M$3:$M$14`, … |
| main-ns list validation pointing at a **defined name** | **1** | `Choicelist` → `Dropdown!$H$3:$H$5`, at `'1. Introduction'!N54:N63` |
| main-ns list validations pointing at a **filing-conditional expression** | **2** | `IF(C5="No",Choicelist,YesNolist)`, at `'8. Compliance Status'!C10` and `!C11` |
| | **22** | |

> **The resolution rule, normative from here.** A list validation *resolves* iff its `formula1` reduces,
> **without reading any cell of the filing**, to a single contiguous range on the pinned blank. 19 + 1 =
> **20**. The two `IF(C5=…)` validations do **not** resolve; their vocabulary depends on
> `'8. Compliance Status'!C5`, so the predicates over them are `applicable`-gated on that cell and their
> unmet branch is `OUT_OF_SCOPE(out_of_scope.not_applicable)` with a pointer to `C5` — never a silent
> membership pass against whichever list happened to be picked.

This is exactly the shape the vacuous pass takes: a vocabulary that is *sometimes* the right one. It is
recorded as new catalogue entry **NC-D06**.

### N8 — **2 of the 15 `Dropdown` vocabularies are wired to no validation** · MEASURED

Columns used on `Dropdown`: `D E F G H I J K L M N O P Q R` = 15. Columns referenced by any of the 22 list
validations or by the four defined names: `D E F G H I J K M N O P Q` = 13. **`L` and `R` are shipped
vocabularies that nothing enforces.** The data model already has the field —
`vocabulary(..., wired_by_validation)` — and this is its first measured value: `13 wired, 2 unwired`. An
unwired vocabulary is a candidate obligation with no enforcement point, and it belongs in the Unchecked
panel, not in the harvest.

## §0.3 — Container-guard limits, derived from the corpus rather than invented

| | observed max across the nine | limit set in `GuardLimits` | headroom |
|---|---:|---:|---:|
| zip entries | **85** (`Updated___Quarterly…`) | 1,024 | 12× |
| total uncompressed bytes | **4,495,901** | 67,108,864 (64 MiB) | 14.9× |
| single-entry uncompressed bytes | **3,551,232** (`xl/model/item.data`, present in the two large workbooks) | 16,777,216 (16 MiB) | 4.7× |
| total compression ratio | **6.2** (`AL_monthly_report`; the two large files are 1.2) | 100.0 | 16× |

Every limit is a constant in one place with the observed maximum in a comment beside it, and the
**admission-side positive control is that all nine prescribed workbooks pass the guard** — without it the
guard is a reject-everything baseline that would score perfectly on its five hostile fixtures.

---

# §1 — THE ELEVEN RULINGS THIS DOCUMENT TAKES BEFORE A BUILD STARTS

Each is a place where the two binding documents under-determine or disagree. Each is decided here with its
reason and its runner-up, so no build begins on an ambiguity. Rulings 1–3 are naming; 4–9 are structural;
10–11 record what is deliberately left open.

### R1 — Where the two binding documents name the same file differently, `01-validation-methodology.md` §0.4 wins for **file** names and `00-decomposition.md` §5 wins for **package** names

*Reason.* The negative-control catalogue references file paths *inside test names and injector targets* —
`schema/styles_mask.py::field_surface()` in NC-D02a, `styles_mask.py` vs `styles_mask_b.py` in NC-D02c,
`evaluate/preflight.py` in §3.3. The catalogue is the instrument that must not drift, and renaming its
referents to satisfy a prose bullet is how a catalogue silently stops covering the code. Package names, by
contrast, appear in the decomposition's import-closure assertions (`cdfc.{ingest,schema,facts,evaluate,…}`)
and in the P0 fixture path `src/cdfc/surface/templates/report.html.j2`.

| decomposition §5 | methodology §0.4 | **decided** |
|---|---|---|
| `ingest/guard.py` | `ingest/container_guard.py` | **`ingest/container_guard.py`** |
| `schema/mask.py` (one file, "two implementations") | `schema/styles_mask.py` + `schema/styles_mask_b.py` | **two files, as §0.4** — one file with two functions cannot satisfy NC-D02c |
| `schema/keys.py` | `schema/stable_keys.py` | **`schema/stable_keys.py`** |
| `facts/table.py` | `facts/fact_table.py` | **`facts/fact_table.py`** |
| `schema/fingerprint.py` | — | **`schema/fingerprint.py`** (additive, no conflict) |
| `facts/anchors.py` | — | **`facts/anchors.py`** (additive) |
| `src/cdfc/calc/` | — | **`src/cdfc/calc/`** (additive; see R4) |
| `report/` (§0.4) | `surface/` (decomposition §5 P0 and P14) | **`src/cdfc/surface/`**, following the ruling already taken and argued in `plan/07-phases-surface-and-transfer.md` §0.1 |

### R2 — There are **two** manifests, not one, and they are different objects

The decomposition puts `manifest.py` under `ingest/` (P1-B4); the methodology puts it under `schema/`.
Both are right, about different things.

- **`ingest/manifest.py` → `ExtractionManifest`** — *per artifact, per reader*: parts read, parts skipped,
  namespaces seen, constructs not understood, and the agreement vector. It populates
  `extraction_manifest(run_id, reader, …)`, whose primary key already carries `reader`, which is the
  schema's own evidence that this object is per-reader.
- **`schema/manifest.py` → `InductionManifest`** — *per template digest*: which of the induction's
  constructs were understood, which fields were excluded from `in_scope` **with a stated reason**, the
  resolution state of every stable key, and the vocabulary wiring census (N8). It is content-addressed with
  the `TemplateSchema` and is an input to `verify`.

`tests/contract/test_contract__two_manifests_are_distinct` asserts neither type is assignable to the other
and that `InductionManifest` carries no `run_id`.

### R3 — The clock is a parameter, everywhere, from the first function written

No function in `src/cdfc/` below the CLI calls `datetime.now()`, `time.time()` or reads `TZ`. `received_at`
is an argument to `receive()`; `retrieved_at` is a field of the blob record; both are recorded in the run
manifest as *inputs*. Enforced by `ci/no-clock-in-core.sh` (a ninth grep, added to `ci/GATES.md` — see R5)
scanning `src/cdfc/` excluding `cli.py`, with injector `injectors/now_in_renderer.py` already in the
methodology's determinism table. *Reason:* determinism is cheaper to keep than to recover, and P11's
byte-identity gate is nine phases away — by then a `now()` in a foundation module is thirty call sites deep.

**And the pattern set is `perf_counter`, `monotonic`, `process_time` as well as `now()`, `time.time()` and
`TZ` — because a *duration we measured ourselves* is a clock.** The wall-clock sources everyone enumerates
are the ones that produce a timestamp; the one that broke `05`'s `CanaryRow` is the one that produces an
`elapsed_us`, and `01` §1.5's enumeration of non-determinism sources does not contain it. `ci/no-clock-in-core.sh`
therefore greps for `datetime\.now|time\.time|perf_counter|monotonic|process_time|\bTZ\b`, and its scan set
excludes exactly one directory, `src/cdfc/measure/perf/`, which writes timings to
`reports/perf/<run_id>.jsonl` — **outside every hashed payload**. Catalogue entry **NC-CI07** (§X); the
companion structural test over hashed dataclasses (`test_contract__no_duration_field_in_a_hashed_object`)
belongs to P10/P11 and is recorded as obligation **Y13**.

### R4 — `src/cdfc/calc/` enters `ci/no-float-money.sh`'s scan set, with one clause disapplied and the boundary named

The evaluator computes in `Decimal` under a pinned context; the fact table stores `int64
MILLI_USD_MILLION`. The grep's `float(` and `import math` clauses apply to `calc/` in full. Its
*"`/` applied to a money-typed symbol"* clause does **not**, because Excel semantics include division and
`'1. Introduction'!C92`'s formula divides on purpose. In exchange, `calc/` carries a stricter structural
test: `tests/unit/test_calc_no_float.py::test_calc__never_produces_a_float` asserts every value the
evaluator returns is `Decimal | str | ExcelError | bool`, never `float`, over all 505 FME cells; and
exactly one function crosses the boundary, `facts/units.py::to_milli_usd_million(Decimal) -> int`.

*Why the scan set is extended at all, rather than left as the methodology wrote it:* NC-A02b's lesson is
that **a gate which stopped scanning the right directory is the same defect as NC-D01, one level up.**
`calc/` is a directory full of arithmetic that did not exist when the scan set was written.
`tests/negative/test_nc_ci.py::test_nc__E07c_float_scan_set_covers_every_arithmetic_package` enumerates
packages containing arithmetic and asserts each lies inside the scan set — the same shape as NC-A02b.

### R5 — `ci/GATES.md` is the gate registry, its rows are the denominator of P0's number, and the enumeration is fixed here

`plan/00-decomposition.md` P0 **originally** gave the denominator as *"the 16 build gates enumerated in
spec §III.6"* (it now cites this section's 18; arbitration **C4**).
Spec §III.6 is **THE INTERFACES** and contains no gate list; the enumerable neighbours are spec §IV.4.2's
fifteen acceptance criteria A1–A15 and methodology §5.4's eleven mechanised gates. **Ruling: the
denominator is `|rows in ci/GATES.md|`, the registry is created in P0-B3, and it is enumerated at 18 as
follows** — the decomposition's pre-registered 16, plus rows 17 and 18, each added here **with its reason
recorded in `ci/GATES.md`'s append-only log at the moment of addition** (row 17 closes the untraceable
golden literal that `02` §0.2 N3a and `07` §6 both name; row 18 closes the colliding negative-control ids
that four documents allocated independently). If a later phase adds or removes a row, the count moves the
same way, exactly as `docs/HARVEST-DELTA.md` governs `test_harvest_count`. A count that may not move is a
count that gets quietly worked around — **and a count that may move without a diff is worse.**

| # | Gate | Kind | Subject exists | Demonstrable red at | Named broken build |
|---:|---|---|---|---|---|
| 1 | `ci/no-green-tick.sh` | grep | P0 | **P0** | `injectors/plant_glyph.py` |
| 2 | `ci/licence-gate.sh` | resolver | P0 | **P0** | the live research venv: `formulas` 1.3.4 (EUPL 1.1+), `pycel` 1.0b30 (GPL-3.0) |
| 3 | `ci/no-regex-over-xml.sh` | grep | P0 | **P0** | `injectors/formula_regex.py` |
| 4 | `ci/no-bare-except.sh` | grep | P0 | **P0** | `injectors/evaluate_swallow.py` |
| 5 | `ci/no-float-money.sh` | grep | P0 | **P0** | `injectors/float_money.py` |
| 6 | `ci/no-bare-absence.sh` | grep | P0 | **P0** | a `docs/` line asserting an absence with no positive control |
| 7 | `ci/no-libreoffice-online.sh` | grep | P0 | **P0** | `injectors/soffice_online.py` |
| 8 | `ci/golden-asserts-values.sh` | AST scan | P0 | **P0** | a count-only golden |
| 9 | `ci/no-clock-in-core.sh` (**new, R3**) | grep | P0 | **P0** | `injectors/now_in_renderer.py` |
| 10 | `test_nc_meta__every_injector_flips_its_guard` | the sweep, as a test | P0 | **P0** | a catalogue entry whose injector is a no-op |
| 11 | `tests/test_validation_ledger.py` | ledger growth | P0 | **P0** | a phase tag with no new ledger row |
| 12 | `tests/test_suite_census.py` | collection count | P0 | **P0** | delete a test file with no census entry |
| 13 | `tests/golden/test_fixture_integrity.py` | corpus hashes | P0-B2 | **P0** | flip one byte of a vendored workbook |
| 14 | `test_nc__D02d_mutating_path_A_moves_only_path_A` | mutation of a shared reader | P2 | P2 | `injectors/denominator_single_path.py` |
| 15 | `test_attestation_has_no_status_field` | recursive schema walk | P11 | P11 | `injectors/schema_status_deep.py` |
| 16 | `test_no_model_in_verdict_path` | import closure + blocked socket | P5 | P13-B0 | `injectors/import_model_client.py` |
| 17 | `ci/golden-literals-are-traceable.sh` (**new, §0.2 N3a**) | AST scan over `tests/golden/` | P0 | **P0** | a golden comparing an integer literal that appears in neither `01` §0.3's table nor `reports/validation-ledger.jsonl` |
| 18 | `ci/catalogue-ids.sh` (**new, R5a**) | grep over `plan/*.md` + `catalogue.yaml` | P0 | **P0** | one `NC-` id *defined* in two documents |

**And the rule that makes rows 3–9 demonstrable at P0 even though their scan roots are nearly empty:
every grep gate exits non-zero if its scan root does not exist.** A grep over a missing directory that
returns success is scope truncation applied to our own CI. P0-B1 therefore creates every scan root as a
package with an `__init__.py`, and `test_nc__CI01_missing_scan_root_fails` (new, NC-CI01) asserts it.

**And the rule that stops the scan set itself from being the defect.** `01` §5.4 writes
`ci/no-green-tick.sh`'s roots as `src/ templates/ locales/ static/`. **Three of those four do not exist in
the tree P0-B1 creates** — there is no top-level `templates/`, `locales/` or `static/`; the only Jinja
target is `src/cdfc/surface/templates/report.html.j2`. Under the missing-scan-root rule the gate exits
non-zero from the first commit, and the obvious repair is to narrow the scan set to `src/`, which is
**NC-D01's mechanism applied to the honesty gate itself, on day one, in the phase that exists to prevent
it.** `07` P14 SG1 then derives a *third* scan set from `render.TEMPLATE_DIR`, which does not exist until
P14.

> **Ruling (DECIDED).** There is **one** scan-root list and it is a module constant:
> `src/cdfc/surface/labels.py::SCAN_ROOTS`, created at P0-B1 as `("src/cdfc",)` and **extended, never
> replaced**, by P14. `ci/no-green-tick.sh` reads it (`python -c 'from cdfc.surface.labels import
> SCAN_ROOTS; print("\n".join(SCAN_ROOTS))'`) and contains **no directory literal**;
> `test_nc__CI01c_scan_root_list_is_not_a_literal` greps the script for `src/`, `templates/`, `locales/`
> and `static/` and fails if any appears. The narrowing from `01` §5.4's four names to the real tree is
> recorded in `ci/GATES.md` with its reason and date. **A scan set that shrinks silently is the defect; a
> scan set that shrinks with a diff is housekeeping.** `SCAN_ROOTS` is additionally append-only:
> `test_nc__CI01d_scan_roots_are_append_only` fails a removal without a dated row.

### R5a — negative-control ids are allocated by document band, and one gate checks it

`tests/negative/catalogue.yaml` is keyed by `id`, is append-only, and its meta-tests assume uniqueness.
**Four documents allocated ids independently against `01` §2 and they collide.** Within the two documents
this one owns, `02` allocates `NC-E10`–`E13` (facts and `calc/`) and `03` allocated the ids then called
`NC-E09`–`E12` (predicates and verdict) — so `E10`, `E11` and `E12` were each claimed twice. *(`03`'s four
are now `NC-E20`–`NC-E23`; `NC-E09` is **RETIRED** and the numbers below are quoted as history.)* `03` §6 states *"`NC-Q11` and
`NC-E08` are the current maxima"* (false) and `04` §0.8(e) states *"the Q family is free from `NC-Q12`"*
(also false; `NC-Q12` is now **RETIRED** and both sentences are deleted in their own documents). **If the catalogue loads into a dict keyed by id, the later entry silently replaces the
earlier one** — and the earlier one here is `02`'s `NC-E11`, the row that permanently encodes the discovery
that G-EVAL arm 1 is inert. It would be replaced, the sweep would still report `caught == active`, and
`test_nc_meta__no_orphan_guard` would still be satisfied because *an* entry names the guard.

> **THE BAND TABLE THAT STOOD HERE IS DELETED. Arbitration C9.**
>
> This section declared its band table *normative*; `01`, `04`, `05` and `07` each then wrote a different
> one, and no two agreed. **Four competing normative tables is not a stricter regime than none — it is the
> same defect with more authority attached.** The single allocation now lives in
> **`plan/01-validation-methodology.md` §2, THE CANONICAL NC- REGISTRY**, which is the sole place an `NC-`
> id may be *defined*; every other document, this one included, only *references* ids.
>
> **What this document keeps:** `02` still owns its ids — `NC-CI01–CI08`, `NC-F01`, `NC-P07–P11`,
> `NC-D05–D08`, `NC-E10–E14`, `NC-N16` — and their detail lives in this document's §X catalogue tables.
> **What it no longer does is allocate.** New ids come from `01`'s reserved range for `02`, and a new id
> written here without a registry row fails `test_nc_meta__ids_are_defined_in_the_registry`.
>
> **Renumbering this document took, in the same pass:** `NC-N07` → **`NC-N16`**. The former `NC-N07` was
> defined *here* and *also* in `07` §3 with different content; under C9 **both got new ids and `NC-N07` is
> RETIRED permanently, never reassigned** — `07`'s became `NC-N40`. A retired id that later resolves to
> something is how a stale reference becomes a silent wrong reference.

Enforcement is unchanged in shape and stronger in content: **`ci/catalogue-ids.sh`** (registry row 18) —
asserting that each `NC-` id appears as a *definition* in **`plan/01` only**, that every id referenced
anywhere resolves to a registry row, and that no reference names a RETIRED id — together with
`test_nc_meta__ids_are_unique`, `test_nc_meta__ids_are_defined_in_the_registry`,
`test_nc_meta__no_orphan_guard` and `test_nc_meta__no_dangling_reference`, all of which must exist
**before the first entry is written**, at P0-B3. `ci/catalogue-ids.sh` must additionally assert
`file --mime-encoding` is `utf-8` for every scanned path, or use `grep -a`: a scan set that silently drops
a file is the same defect as a scan set that shrinks.

The predicate-loader gate (*a row with no `qualification` block does not load*) is **not** a row here: it
is a property of `predicates/registry.py`, it is NC-Q02, and it belongs to P4. The decomposition's P0
negative-control list mentions a *loader stub* refusing an unqualified YAML; P0-B3 ships that stub as
`src/cdfc/predicates/registry.py::load_or_refuse()` raising `UnqualifiedPredicate` unconditionally, with
`test_nc__Q02_unqualified_predicate_does_not_load` written and green at P0. **A stub that refuses
everything is admissible only because its admission-side twin is impossible until P4** — and that is
recorded, in those words, in the DoD's line C5.

### R6 — SQLite, one `db/schema.sql`, no migration framework, schema digest in the run manifest

The do-not-build list forbids *"Postgres, an ORM, migrations"*. Consequence, stated so nobody invents one
under pressure: during the build, a schema change is a **re-initialisation of a development database**, not
a migration. `db/schema.sql` is applied by `cdfc init`, its `sha256` is written to a one-row `meta` table
and into the run manifest, and `cdfc verify` fails on a schema-digest mismatch rather than attempting to
adapt. P1 creates `blob` and `run`; P2 creates `template`, `template_sheet`, `field`, `vocabulary`,
`validation`, `carry_edge`; P3 creates nothing (the fact table is in-memory by construction, spec §III.3.1
F4). Portable SQL only — no `WITHOUT ROWID`, no JSON1 dependency, no SQLite-only types — because §III.5.3's
named trigger for Postgres is a second concurrent writer, not a row count.

### R7 — gVisor is Linux-only, the developer machine is macOS, and the sandbox gate is a **deselect**, never a skip

`runsc` does not run on Darwin. Methodology §1.0: *a skipped test is a failed test.* Ruling: the guard's
**checks** are pure Python and run on every platform; the guard's **confinement profile** (gVisor `runsc`,
`seccomp`, `--network=none`, read-only rootfs, RLIMITs, wall-clock kill, non-root uid,
`no-new-privileges`) is asserted by `tests/e2e/test_e2e__sandbox_profile.py`, which is **collected only in
the Linux CI image** via a collection filter, not a `@pytest.mark.skip`. `tests/test_suite_census.py`
records **two** expected collection counts, one per platform, so a suite that silently shrinks on either is
still caught. `docs/GATE-LIVENESS.md` records the sandbox row as `LIVE (linux-ci) / NOT-EVALUABLE (darwin)`
and never as a pass.

**And the licence.** gVisor's licence is **NOT-FOUND** and methodology §5.2 fails the build on a
`NOT-FOUND` runtime dependency. gVisor is a runtime dependency of the parser tier. **P0-B3 must therefore
either open gVisor's LICENSE and record `opened_by`/`opened_at`, or record the fallback in
`docs/LICENCES.md` — plain `seccomp` + namespaces, a weaker boundary — and print that weakness on the
deployment surface.** It is the one licence item that can block P1.

### R8 — The research venv is a **fixture**. Do not clean it

`/Users/abishaikc/Gift/.venv` contains `formulas` 1.3.4 (EUPL 1.1+) and `pycel` 1.0b30 (GPL-3.0), both on
the hard denylist. It is the licence gate's live negative control and requires no injection
(methodology §5.2). P0-B1 creates a **separate** clean environment for `src/cdfc/` and leaves the research
venv untouched; P0-B3 additionally commits
`fixtures/licences/research-venv-sitepackages__20260811.txt` so the control survives the day someone
tidies up. `tests/negative/test_nc_licence.py::test_nc__L01_gate_fails_against_the_research_venv` runs
against the live interpreter when it exists and against the committed listing when it does not.

### R9 — The reader-competence matrix is code, and widening it requires a recorded reason

The mechanism that resolves N3 is also the mechanism that could be abused to make any disagreement
disappear. `ingest/competence.py` holds `COMPETENCE: dict[str, frozenset[Instrument]]` — one entry per
agreement field — and `docs/READER-COMPETENCE.md` carries one row per entry with the *written definition*
of the field and the reason each instrument is or is not a party.

**And the reason must name the workbooks it was measured on, because the matrix is being written from
`n = 1`.** §0.2 N3 measures eight fields on **FME alone**, and `COMPETENCE` then classifies all 72 cells of
P1's 8 × 9 matrix. A competence judgment taken on one workbook becomes the classifier for nine — and the
four fields it excludes `B` from are precisely the four where the project's founding external disagreement
lives (openpyxl, 35 of 54). *An exclusion measured once and applied nine times is an assumption wearing a
measurement's label.* Therefore every `COMPETENCE` entry carries a third element, `measured_on:
frozenset[str]` (workbook sha8s), and
`tests/contract/test_contract__incompetence_is_measured_on_every_workbook_it_classifies` **fails the build
when a field's exclusion is applied to a workbook on which it was never measured** — the reading is
`NOT_COMPARABLE(competence_unmeasured)` on that cell of the matrix, never a silent `AGREE`.
`tests/contract/test_contract__competence_is_pinned` asserts the matrix equals the document, and
`tests/negative/test_nc_ingest.py::test_nc__P07_narrowing_competence_requires_a_reason` asserts that
removing an instrument from a field's competent set without an appended dated row in
`docs/READER-COMPETENCE.md` fails the build. Same shape as `HARVEST-DELTA.md`, same reason: **the escape
hatch must leave a diff.**

### R10 — Deliberately left open, with the decision rule rather than an answer

| Open | Why it is not decided here | The decision rule |
|---|---|---|
| Whether `_xlfn.SINGLE` is implemented or its cells are `NOT_RUN` | It is a human decision the spec explicitly reserves (§III.3.2 T5) and it costs one cell | **P3-B4 implements it iff the implementation is ≤ 20 lines and its own unit vector passes; otherwise `'1. Introduction'!D92` and its materialised siblings are `NOT_RUN(not_run.source_unreadable)` and the count is published.** Either way the number `1` appears in `docs/measurements/P3-evaluator.md` |
| The `REJECTED` predicate state (audit §V.7.5) | It is a P4 schema question and this document does not write that schema | Recorded as a live cross-document obligation in §Y. P4-B1 confirms it before the predicate schema is written |
| `K` and `T` in `pervasiveness-policy-v1.json` | No argued basis exists anywhere in the corpus | They render the literal string `PLACEHOLDER`. No foundation phase touches them |
| Whether the two workbooks with no protection mask should be excluded from the corpus | It is P2's measurement, not a prior | `field_surface = null`, `denominator.source = "not derivable — template ships no protection mask"`, and they stay in the corpus. Excluding them would hide the one case (`IFSCA_Annual_Reporting_Format`, a plausible-looking 8) that NC-D03 exists for |

### R11 — Effort assumption, stated once for all four phases — **re-estimated, and the second author is now a line item**

**One competent engineer**: fluent in Python, comfortable reading raw OOXML against the ECMA-376 text,
comfortable with `Decimal` semantics and with pytest fixtures; working from this document and the two it
binds to; **~6 productive hours a day; no context switching.** Human-latency items belong to other phases
and are never added to this total.

**The figures, revised.** `plan/00-decomposition.md` §7 pre-registered **P0 4 · P1 8 · P2 10 · P3 12 = 34**.
Two of those four do not survive contact with their own build lists, and the direction of the error is the
load-bearing part:

| Phase | `00` §7 | **This document, revised** | Why |
|---|---:|---:|---|
| P0 | 4 | **8** (B1 1.5 · B2 0.5 · B3 5.0 · B4 1.0) | Four days is 24 productive hours for: a hash-pinned lockfile, a 13-stage pipeline, **eleven** shell/AST gates, the catalogue schema and its `flips` contract, the `Injector` protocol, nine injectors, the sweep, **six** meta-tests, an AST import-closure walker three later phases reuse, a two-platform census, the ledger, a licence resolver, the vendored corpus with value assertions, the foundation probe, **and fifteen gates observed red with their assertions captured.** P0 is where every later phase's evidence machinery comes from; an underestimated P0 is the phase that gets compressed, and compressing it turns the sweep into a shell script and the catalogue into a list |
| P1 | 8 | **8** | unchanged |
| P2 | 10 | **10** | unchanged |
| P3 | 12 | **17** (B1 2.0 · B2 1.5 · B3 1.5 · **B4 12.0**) | B4 at 7 days delivers nine Excel functions including `AGGREGATE(15,6,…)` over an array, `COUNTIF` wildcard semantics, array forms, `_xlfn.SINGLE`, element-wise `#DIV/0!`, six error types with `IFERROR` interaction, `Decimal` under a pinned context, a seeded discriminating-fixture generator, a human-authored expectation file **and** a digest-pinned offline LibreOffice differential. Any one of the last three is a day; the array semantics alone are two |
| **total** | **34** | **43 engineer-days** | |

**Range, stated as a range because it is judgment and not measurement:** P0 8–10, P3 15–20. The planning
figures above take the low end of each. *The alternative this beat:* holding 34 and absorbing the
difference inside the phases — rejected because the cheapest way to make a 7-day P3-B4 estimate come true
is to skip arm 2 (§P3-B4), which is the one thing in P3 that carries information.

**The 9-day delta is a cross-document obligation on `00` §7 (Y14), not a licence to compress.** `00` §7's
critical-path arithmetic and its *"requires ~2–3 engineers to realise"* line were recomputed against 43;
**`00` §7 now publishes ~118 working days and is the arithmetic of record** (arbitration **C6** — the
pre-revision `~114` is retired and must not be re-quoted from this document or any other).

**And the staffing model, stated once, because three of this document's evidence claims depend on it.**
Every per-phase table here says *one competent engineer*. **Three artifacts in these four phases are
evidence only if a *second author* writes them**, and none of them is budgeted anywhere in the corpus:

| Artifact | Build | Second-author cost | What it buys |
|---|---|---:|---|
| `ingest/reader_lxml_b.py` (reader A′) | P1-B3 | 2.0 person-days | The A-vs-A′ differential on the four fields no third-party library can read |
| `schema/styles_mask_b.py` (mask path B) | P2-B2 | 1.5 person-days | `computedTwiceAgreed` on the denominator |
| `tests/golden/expected/*.expected.json` (G-EVAL arm 2 oracle (a)) | P3-B4 | 1.5 person-days | The only discriminating oracle over the evaluator |

These **5.0 person-days are a different person's days and are not added to the 43**, exactly as every other
second-person cost in the plan is enumerated separately (corpus 15–25, adjudication 3–5, κ re-rate 1,
strata 2+1, proviso labeller 0.5, admission signer 0.25, transfer operator 4–6 h).

> **Ruling (DECIDED), and it is mechanised, not promised.** If the second person does not exist, each of
> the three artifacts is written by the same engineer and **the differential it feeds is labelled
> `SAME-AUTHOR — a weaker instrument`**, in those exact words, in `docs/measurements/P1-agreement.md`,
> `docs/measurements/P2-field-surface.md` and `docs/measurements/P3-evaluator.md`, in `ci/GATES.md`
> (G-READERS / G-DENOM / G-EVAL recorded `PASSED — NOT INDEPENDENT`), and **on every surface that quotes a
> number derived from them.** `tests/contract/test_contract__same_author_label.py::test_same_author_label_is_present_when_authors_match`
> reads a declared `authored_by` field from each artifact, cross-checks it against `git blame`'s dominant
> author for the counterpart module, and — when they are equal — asserts the literal string is present in
> all four places. **There is no third option and no silent one.** NC-D02d and NC-P09 prove *two code
> paths*; `01` §7.5 already admits they cannot prove *two minds*, and this ruling is what stops that
> admission from living only in a residue section.
>
> *OPEN — USER DECISION.* **Is a second author funded for these 5.0 person-days?** It blocks nothing — the
> build proceeds either way — but it decides whether P1, P2 and P3 each ship a differential or a label. Ask
> before P1-B3 starts (day ~9 on the revised schedule).

---

# P0 — REPOSITORY, CI, AND THE COMMITMENT GATES

**Effort: 8 engineer-days** (revised from `00` §7's 4 — see R11) · B1 1.5 · B2 0.5 · B3 5.0 · B4 1.0

## P0 · What it settles

**Whether this project's own honesty commitments can be enforced by a machine before there is any code to
violate them — and what the two field observations say.**

Every commitment in the specification is today a sentence in a document. A sentence is a preference. The
question no later phase can answer is whether these particular commitments are the kind that *can* be
mechanised at all, because the ones that cannot must be downgraded to documented preferences **in writing,
with a published count**, and that downgrade is much cheaper to accept at day zero than at day ninety.

Three sub-questions:

1. **Can a gate be observed red before its subject exists?** Ten of the eighteen registry rows are greps or
   AST scans, and most of their scan roots will be nearly empty at P0. A grep over an empty directory
   passes trivially, and a grep over a *missing* one passes trivially too — which is NC-D01's mechanism
   applied to CI. R5's missing-scan-root rule and R5's `SCAN_ROOTS` ruling are the answer, and P0 is where
   they are tested rather than asserted.
2. **Does the licence gate reject a real denylisted package on a real interpreter?** It does not need an
   injector: two are installed right now.
3. **Do the two field observations get asked, dated, and — if unanswered — carried as a visible standing
   absence rather than dropped?** The failure mode here is not a wrong answer. It is a question quietly
   dropped because nothing depended on it.

## P0 · Entry criteria

**None. This is the root.** The only preconditions are facts about the machine: a Python 3.12 toolchain, a
git repository at `/Users/abishaikc/Gift` with no commits, and the nine workbooks readable at
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/`.

## P0 · Builds

---

### BUILD P0-B1 — REPOSITORY SKELETON, LICENCE, PINNED TOOLCHAIN · 1.0 day

**What it produces.** A repository in which every command named in methodology §5 exists as a `make`
target, every CI scan root exists as a package, and every dependency is pinned by name **and wheel hash**.

#### Files created

```
LICENSE                          Apache-2.0, verbatim. THE FIRST FILE COMMITTED (spec G9)
NOTICE                           attribution stub
pyproject.toml                   deps, pytest config, ruff, mypy --strict, mutmut config
requirements.lock                fully resolved, --require-hashes, generated by `uv pip compile --generate-hashes`
Makefile                         lint licence greps contract unit property golden differential
                                 nc-sweep determinism perf mutation-pr e2e nightly demo
                                 corpus-verify measure-foundation
.github/workflows/ci.yml         the thirteen stages of methodology §5.3, in that order
.gitignore                       .venv-cdfc/ reports/ blobs/ *.db  — never fixtures/
src/cdfc/__init__.py             __version__ = "0.0.1"
src/cdfc/cli.py                  typer/argparse entry point; every unimplemented subcommand EXITS 2
src/cdfc/{ingest,schema,facts,calc,predicates,evaluate,verdict,probes,selfcheck,
          attest,surface,qualify,measure}/__init__.py          -- the CI scan roots (R5)
src/cdfc/surface/templates/report.html.j2                       -- the NC-A02 injector target
src/cdfc/surface/labels.py       SCAN_ROOTS = ("src/cdfc",) -- THE one scan-root list (R5), extended
                                 by P14, never replaced; read by ci/no-green-tick.sh
src/cdfc/measure/paths.py        the measurement-file path constants other documents import instead of
                                 re-typing a filename (P4_HARVEST_DISTRIBUTION, P3_EVALUATOR, ...)
docs/LICENCES.md  docs/ABSENCE-SCOPE.md  docs/GATE-LIVENESS.md  docs/DOD-TEMPLATE.md
docs/HARVEST-DELTA.md  docs/EQUIVALENT-MUTANTS.md  docs/MUTATION-THRESHOLDS.md
docs/READER-COMPETENCE.md  docs/PROTECTION-RESOLUTION.md  docs/GATE-CHANGES.md
docs/measurements/.gitkeep      reports/.gitkeep      perf/baseline.json  perf/baseline.ci.json
reports/perf/.gitkeep            timings live HERE, outside every hashed payload (R3)
ci/GATES.md                      the eighteen rows of R5, append-only, with rows 17-18's reasons dated
tools/mutation/{run.py,exclude.toml}
```

**Pinned toolchain**, by name and wheel hash, in `requirements.lock`:
`python 3.12.x` · `lxml 6.1.1` · `openpyxl 3.1.5` · `celpy` (pinned by PyPI name **and** wheel hash — two
different projects live at a path called `cel-python`) · `z3-solver` · `pytest 8.x` · `hypothesis` ·
`jsonschema` · `pulp` · `cryptography` · `pandera` · `fastapi` · `jinja2` · dev-only `mutmut 3.7.0`,
`ruff`, `mypy`, `pytest-benchmark`, `coverage`.

**`pyproject.toml`, the non-negotiable block** (methodology §1.0):

```toml
[tool.pytest.ini_options]
addopts = "--strict-markers --strict-config -q"
xfail_strict = true
filterwarnings = ["error"]     # openpyxl's "Data Validation extension is not supported and will be
                               # removed" is EXACTLY the signal this project exists to stop discarding
markers = ["linux_only: collected only in the Linux CI image (R7)"]
```

#### Public interface

```
$ cdfc --version                       -> "cdfc 0.0.1 (schema <sha8>, gates 18)"
$ cdfc init [--db PATH]                -> applies db/schema.sql (P1), writes meta.schema_sha256
$ cdfc <anything else>                 -> exit 2, "not implemented at phase P0"
$ make lint licence greps              -> the first three CI stages, under 40 s total
```

#### Data produced

`ci/GATES.md` (18 rows, each carrying `id, kind, subject_exists_at, demonstrable_red_at, broken_build,
liveness ∈ {LIVE, PENDING}`) · `docs/LICENCES.md` (one row per resolved dependency:
`{name, version, licence, warrant, opened_by, opened_at}`) · `perf/baseline.json` (empty, machine block
populated).

#### Functionality validation

**Unit.**
`tests/unit/test_cli.py::test_cli__unimplemented_subcommand_exits_nonzero` — asserts exit code 2 and that
stdout contains no member of the banned string set. *A stub that exits 0 is an all-clear.*
`tests/unit/test_cli.py::test_cli__version_reports_gate_count` — the printed gate count equals
`len(parse(ci/GATES.md))`, so a row added without a version bump is visible.

**Contract.**
`tests/contract/test_contract__gates_registry_schema` — every row has `id, kind, subject_exists_at,
demonstrable_red_at, broken_build, liveness`; ids are unique; `demonstrable_red_at ∈ {P0…P15}`.
`tests/contract/test_contract__pending_rows_name_a_phase` — a row whose `demonstrable_red_at` is empty
fails. **There is no permanently-pending gate.**
**`tests/contract/test_contract__live_set_is_pre_registered`** — the set of rows whose `liveness` is `LIVE`
at P0 is **exactly** `{1,…,13,17,18}` and the `PENDING` set is **exactly** `{14,15,16}`, both as literals in
the test. Moving a row between the sets fails the build unless `ci/GATES.md` carries an appended, dated
argument naming the row — the same discipline `docs/HARVEST-DELTA.md` applies to `test_harvest_count`.
*Why this test and not a count:* P0's exit gate was `gates_live == gates_written`, and `gates_written` was
defined as "the gates whose subject exists", decided by the same person deciding whether a gate can be
demonstrated. **Any gate that resisted demonstration could be moved to `PENDING` and the ratio would become
`n/n`. The gate could not fail.** Pre-registering the *set* is what makes it able to.

**Property.** None exists for this build. *Stated because the DoD requires it to be stated:* a repository
skeleton has no invariant over a generated input space; asserting one would be decoration.

**Golden.** None at B1; the corpus arrives at B2.

**Negative controls.**
- **NC-CI01 (new)** — *a grep gate whose scan root does not exist returns success.*
  Injector `injectors/remove_scan_root.py` deletes `src/cdfc/evaluate/`;
  `tests/negative/test_nc_ci.py::test_nc__CI01_missing_scan_root_fails` asserts
  `ci/no-bare-except.sh` exits non-zero. **Admission-side twin:**
  `test_nc__CI01b_present_empty_scan_root_passes` — an existing but empty `evaluate/` passes, so the rule
  is "root must exist", not "root must be non-empty".
- **NC-CI02 (new)** — *`filterwarnings = ["error"]` is removed.* Injector
  `injectors/warnings_tolerated.py`; the guard is
  `tests/negative/test_nc_ci.py::test_nc__CI02_openpyxl_warning_is_an_error`, which loads the FME workbook
  through `openpyxl` and asserts the `UserWarning` **raises**. This is the one line of configuration
  standing between the project and the exact signal that produced its flagship finding.

**Determinism.** `tests/determinism/test_det__lockfile_is_hash_pinned` — every line of
`requirements.lock` carries at least one `--hash=sha256:`; a dependency without one fails.

**Performance.** `PERF` budgets are recorded, not enforced, until their subject exists. `make lint licence
greps` under 40 s is asserted as a soft ceiling in CI logs only.

**Effort: 1.5 days** (R11; the extra half-day is `labels.py::SCAN_ROOTS`, `measure/paths.py`, and rows
17–18's two scripts existing as failing stubs from the first commit).

---

### BUILD P0-B2 — THE NINE REAL ARTIFACTS, VENDORED AND CONTENT-ADDRESSED · 0.5 day

**What it produces.** The corpus, byte-identical, inside the repository, with a manifest that fails on
drift — and the measurement script that produced §0.

#### Files created

```
fixtures/prescribed/<nine files, byte-for-byte>
fixtures/prescribed/MANIFEST.json      {filename, sha256, bytes, origin_uri, retrieved_at}
fixtures/licences/research-venv-sitepackages__20260811.txt          (R8)
tools/measure/foundation_probe.py      the §0 script, one function per measurement
tests/golden/test_fixture_integrity.py
docs/measurements/P0-foundation-probe.md   the §0 tables, regenerated by `make measure-foundation`
```

#### Public interface

```python
# tools/measure/foundation_probe.py
def probe_all(paths: Sequence[Path]) -> dict[str, Any]   # one key per §0 measurement id (N1..N8)
```
```
$ make corpus-verify      -> re-hashes all nine against MANIFEST.json; exit 1 on any drift
$ make measure-foundation -> rewrites docs/measurements/P0-foundation-probe.md; exit 1 if it differs
                             from the committed copy without a --update flag
```

#### Data produced

The nine `sha256` values of methodology §0.3, re-asserted; and `docs/measurements/P0-foundation-probe.md`
carrying N1–N8 with their commands.

#### Functionality validation

**Golden.** `tests/golden/test_fixture_integrity.py::test_golden__fixture_integrity__all_nine` — asserts
every `sha256` and every byte count of methodology §0.3, **and** (rule R-GOLD-2) at least one *value*
drawn from each file: for FME, `'3. Portfolio'!O3` materialises to `SUM(C3:N3)` with `ref="O3:O12"`;
for `ALR_V2_3`, one of the five `≥ −1e17` bound formulas verbatim. *Which workbook and why:* all nine,
because this is the integrity test and a partial one is a partial guarantee.

**Negative control.** **NC-F01 (new)** — *a vendored fixture drifts.* Injector
`injectors/flip_fixture_byte.py` writes one byte into a temp copy and repoints the manifest;
`tests/negative/test_nc_meta.py::test_nc__F01_fixture_drift_is_caught` asserts `make corpus-verify` exits
non-zero **and names the file**. A drift detector that does not name the file is a drift detector nobody
uses.

**Determinism.** `test_det__probe_is_reproducible` — `probe_all` run twice in different working
directories under different `PYTHONHASHSEED` produces byte-identical canonical JSON.

**Effort: 0.5 day.**

---

### BUILD P0-B3 — THE COMMITMENT GATES, WRITTEN FIRST AND DEMONSTRATED TO FAIL · 5.0 days

**What it produces.** The eighteen rows of R5, of which **fifteen are observed red at P0**, plus the
negative-control machinery every later phase plugs into.

#### Files created

```
ci/no-green-tick.sh  ci/licence-gate.sh  ci/no-regex-over-xml.sh  ci/no-bare-except.sh
ci/no-float-money.sh ci/no-bare-absence.sh ci/no-libreoffice-online.sh
ci/golden-asserts-values.sh  ci/no-clock-in-core.sh                       (R3, new)
ci/golden-literals-are-traceable.sh                                       (row 17, new)
ci/catalogue-ids.sh                                                       (row 18, new, R5a)
tests/negative/catalogue.yaml           THE machine-readable catalogue (methodology §2)
tests/negative/injectors/__init__.py    INJECTORS: dict[str, Injector]
tests/negative/injectors/{plant_glyph,formula_regex,evaluate_swallow,float_money,
                          soffice_online,now_in_renderer,remove_scan_root,
                          warnings_tolerated,flip_fixture_byte,
                          perf_counter_in_core,absence_cites_empty_control,
                          untraceable_golden_literal,duplicate_nc_id,
                          sweep_any_guard}.py
tests/negative/broken_builds/.gitkeep
tests/negative/{test_nc_meta.py,test_nc_ci.py,test_nc_licence.py}
tests/negative/importgraph.py           AST import-closure walker (used by P1, P11, P13)
tests/test_suite_census.py              two expected counts, one per platform (R7)
tests/test_validation_ledger.py
tools/nc_sweep.py                       -> reports/negative-control-sweep.json
src/cdfc/predicates/registry.py         load_or_refuse() — refuses unconditionally at P0 (R5)
src/cdfc/measure/absence.py             assert_absent(query, positive_control, corpus)
docs/GATE-LIVENESS.md                   one row per gate, with the CI log line that showed it red
```

#### Public interface

```python
# tests/negative/injectors/__init__.py
class Injector(Protocol):
    id: str
    def __enter__(self) -> None: ...      # monkeypatch a symbol, swap sys.modules for a broken twin,
    def __exit__(self, *exc) -> None: ... # or write a corrupted fixture to a temp path
INJECTORS: dict[str, Injector]

# tools/nc_sweep.py
def sweep(catalogue: Path) -> SweepReport
    # {entries_caught: int, entries_active: int, none_count: int, provisional_count: int,
    #  guards_flipped: int, guards_expected_to_flip: int, rows: [...]}
    # rows[i].guards[j] = {path, flips, observed, assertion_text, node_id}

# tests/negative/importgraph.py — PUBLIC, because three later phases and two gates read it
def import_closure(module: str, *, root: str = "cdfc") -> frozenset[str]
    """The transitive first-party import set, by AST, without importing the module.
       Used by: NC-D02a/c (denominator provenance), NC-P04 (round-trip), row 16
       (no model in the verdict path), and — from P8 — g4_ffr's COMPUTED corpus-independence
       (obligation Y11). It is one function, so there is no second implementation to forget."""

# src/cdfc/measure/absence.py
def assert_absent(query: Callable[[Corpus], int], *, positive_control: Callable[[Corpus], int],
                  corpus: Corpus, ledger: Path) -> AbsenceClaim
    """Refuses to return unless positive_control(corpus) > 0 through the SAME interface.
       Writes both counts to reports/validation-ledger.jsonl AND returns the ledger row id.
       The ONLY sanctioned way to record an absence anywhere in this project."""

# src/cdfc/predicates/registry.py
class UnqualifiedPredicate(Exception): ...
def load_or_refuse(envelope: Mapping) -> NoReturn   # P0: always raises. P4 gives it the other branch.
```

#### **The sweep's contract — CHANGED here, and it is the most important change in P0**

Methodology §2.0 step 3 reads: guards pass clean → apply the injector → *"re-run **only** the named guard
tests. Assert **at least one** fails, and record which."* **`at least one` is the defect.** Entries name
three to five guards apiece (NC-Q08 names five; NC-C01 three; NC-P01 two; NC-D02 four), `caught / active`
counts **entries**, not guards, and an entry is `caught` the moment its *weakest* guard goes red.

**The failure this permits, concretely.** `injectors/render_self_authored_ffr.py` is applied. The injected
renderer also drops `corpus_id`, so `test_nc__Q08c_no_ffr_without_provenance_and_n` goes red. The sweep
records NC-Q08 as `caught` and prints `caught = 47 of 47`. **`test_nc__Q08a_renders_uninformative` — the
assertion that no digit reaches the FFR element, the one the whole provenance story rests on — was never
exercised, and could have been deleted three commits earlier.** `test_nc_meta__no_orphan_guard` does not
see it: the test still exists and is still named. It is simply never observed red. This is the plan's own
thesis — *a guard that has never been observed to fail is not evidence* — applied to the plan's own
instrument, and the plan currently holds itself to the weaker version of the assertion it demands from
everyone else.

> **Ruling (DECIDED).** The catalogue's `guard_tests` gains a **per-guard expectation**, and the sweep
> asserts the **exact set**, never "at least one":
>
> ```yaml
> guard_tests:
>   - path: tests/negative/test_nc_predicate.py::test_nc__Q08a_renders_uninformative
>     flips: true
>   - path: tests/golden/test_golden__ffr_render.py::test_golden__blind_filled_renders_digits
>     flips: false        # a POSITIVE control: it must STAY GREEN under this injector
> ```
>
> The sweep runs every named guard and asserts: every `flips: true` guard is **red** under the injector,
> every `flips: false` guard is **green**, and the run fails if either set differs by one member. A guard
> with no `flips` key is a schema error; **`flips: false` on every guard of an entry is a schema error**
> (an entry that expects nothing to flip is not a negative control). Then: remove the injector → assert
> everything green again. A guard that stays red is a leaked injector, which is itself a defect.

#### Data produced

`reports/negative-control-sweep.json` — **five integers, never a percentage**:
`entries_caught / entries_active`, **`guards_flipped / guards_expected_to_flip`**, and `none_count`, plus a
sixth reported separately, `provisional_count`. *The second pair is the number DoD line C4 is really about,
and today nothing computes it.*

**And the sweep writes the evidence, so C4 stops being a paste.** For every guard it observed red, the row
carries `assertion_text` (the captured assertion line from pytest's report) and `node_id`. DoD line C4 then
reads *"the sweep report's row for `<NC-id>`, guard `<node_id>`, at commit `<sha>`"* — **an artifact path a
reviewer can open, not prose in a PR description**. `01` §4 calls C4 *"the load-bearing line"* and its own
standard for a DoD line is *"an artifact path or a command whose output a reviewer can read without having
done the work"*; a pasted assertion meets neither, because a reviewer cannot distinguish a real paste from
a plausible one. `test_sweep__records_the_failing_assertion_text` asserts the field is non-empty for every
flipped guard.

**`provisional_count`, the third column, and why it is not part of `caught`.** `registry.py::load_or_refuse()`
refuses **unconditionally** from P0 to P4 (R5), so `test_nc__Q02_unqualified_predicate_does_not_load` is
green for four phases while proving nothing: its admission-side twin is impossible until the predicate
schema exists. The plan already declares this in DoD line C5. **An entry whose admission-side twin does not
yet exist is reported as `PROVISIONAL — no admission-side twin yet`, in its own column, and is excluded
from `entries_caught`.** A green entry with no information in it must not be counted as evidence, which is
the same rule this document applies to G-EVAL arm 1.

`docs/GATE-LIVENESS.md` — for each gate, the date, the injector, the pasted failing assertion, **and its
`liveness` at P0** so the pre-registered LIVE/PENDING sets of `test_contract__live_set_is_pre_registered`
have a document to be checked against.

#### Functionality validation

**Unit.** `tests/unit/test_absence.py::test_assert_absent__raises_without_positive_control` ·
`::test_assert_absent__raises_when_control_returns_zero` — *a broken interface must not be reported as an
empty world*. `tests/unit/test_absence.py::test_assert_absent__writes_both_counts` — the ledger row carries
numerator and control.

**Contract.** `tests/contract/test_contract__catalogue_schema` — every entry has
`id, component, break, measured_instance, injector, why_impossible, guard_tests, positive_control, status`;
every member of `guard_tests` is a mapping with `path` **and `flips: bool`** (a bare string fails);
at least one guard carries `flips: true`; `injector: NONE` requires non-empty `why_impossible`.

**Negative controls — the meta-tests of methodology §2.0, now six, all live at P0.**
`test_nc_meta__every_entry_has_an_injector_or_a_reason` ·
`test_nc_meta__every_injector_flips_its_guard` (**the sweep, run as a test — registry row 10**) ·
`test_nc_meta__no_orphan_guard` · `test_nc_meta__catalogue_growth_is_logged` ·
**`test_nc_meta__every_expected_guard_flipped`** (new — row 10's real form: the exact-set assertion above,
asserting `guards_flipped == guards_expected_to_flip` **and** that the flipped set equals the declared set
member-for-member; a mismatch names the guards) ·
**`test_nc_meta__ids_are_unique`** (new, R5a — trivial, and it must exist *before* the first entry is
written, which is why it is here and not in the phase that first collides).
Plus, specific to this build:
- `tests/negative/test_nc_ci.py::test_nc__A02a_grep_catches_a_planted_glyph` — `injectors/plant_glyph.py`
  resolves its target from `cdfc.surface.render.TEMPLATE_DIR` when that symbol exists and from the P0 stub
  path otherwise; never a hard-coded literal (`plan/07-…` §0.1).
- `tests/negative/test_nc_licence.py::test_nc__L01_gate_fails_against_the_research_venv` — runs
  `ci/licence-gate.sh` against `/Users/abishaikc/Gift/.venv` and asserts non-zero exit **naming both
  `formulas` and `pycel`**. Falls back to the committed listing (R8).
- **NC-CI03 (new)** — *a `SECONDARY` runtime licence is silently tolerated forever.* The gate is advisory
  in P0–P1 and blocking from P2 (methodology §5.2); the injector sets the phase marker to P2 and the guard
  `test_nc__CI03_secondary_runtime_dep_blocks_from_p2` asserts the build fails while
  `docs/LICENCES.md` still shows `opened_by` blank for **gVisor, Z3, Hypothesis, cosign** (R7).
- **NC-CI04 (new)** — *`ci/no-bare-absence.sh` is defeated by writing the words "positive control" on the
  line.* `01` §5.4 implements *"names a positive control"* as a **lexical co-occurrence**: the gate greps
  `src/`, `tests/`, `docs/` for `does not occur`, `zero hits`, `not present in`, `no occurrences` *"on a
  line that does not also name a positive control"*. **Any author who has read the gate satisfies it in
  four words.**
  > **Ruling (DECIDED).** The gate requires a **resolvable reference**, not a phrase. A line asserting an
  > absence must cite a `reports/validation-ledger.jsonl` row id (`ledger:<row_id>`); the gate resolves the
  > id, reads the row, and **fails unless `positive_control_count > 0`**. `assert_absent` already writes
  > both counts and now returns the row id, so the grep reads numbers rather than prose. *Alternative it
  > beat:* a stricter word list — rejected, because it is the same lexical check with a longer regex.

  Injector `absence_cites_empty_control.py` plants a `docs/` line citing a ledger row whose control count
  is zero; guard `test_nc__CI04_absence_must_resolve_a_ledger_row` asserts non-zero exit **and** that a
  line carrying the literal phrase "positive control" with no ledger citation also fails. Admission-side
  twin: `test_nc__CI04b_absence_with_a_live_control_passes`.
- **NC-CI05 (new)** — *a golden test launders a warrant by pinning an integer literal nobody can trace.*
  Registry row 17. Injector `untraceable_golden_literal.py` adds `assert n == 2373` to a golden; guard
  `test_nc__CI05_golden_literals_are_traceable` asserts `ci/golden-literals-are-traceable.sh` exits
  non-zero and **names the file, the line and the literal**. Admission-side twin:
  `test_nc__CI05b_a_ledger_backed_literal_passes` — `3747` is in `01` §0.3's table and passes.
- **NC-CI06 (new)** — *two documents define the same `NC-` id and the later silently replaces the earlier.*
  Registry row 18, R5a. Injector `duplicate_nc_id.py`; guard
  `test_nc__CI06_duplicate_ids_fail_the_build` asserts `ci/catalogue-ids.sh` exits non-zero **naming both
  documents**, and `test_nc_meta__ids_are_unique` goes red. Admission-side twin: the real catalogue passes.
- **NC-CI07 (new)** — *a duration we measured ourselves enters the deterministic core.* (R3.) Injector
  `perf_counter_in_core.py` writes `time.perf_counter()` into a core module; guard
  `test_nc__CI07_monotonic_clock_is_rejected` asserts `ci/no-clock-in-core.sh` exits non-zero for each of
  `perf_counter`, `monotonic`, `process_time`. Admission-side twin: the same call inside
  `src/cdfc/measure/perf/` **passes**, because that is where timings are allowed to live.
- **NC-CI08 (new)** — *the sweep reverts to "at least one guard fails".* The negative control on the
  instrument that finds the others. Injector `sweep_any_guard.py` replaces the exact-set assertion with the
  `any()` form; guard `test_nc__CI08_sweep_requires_the_exact_guard_set` asserts
  `test_nc_meta__every_expected_guard_flipped` goes **red** on a catalogue entry whose second guard was
  silently deleted, and that the weaker sweep reports that entry as `caught`. **This is the entry that
  makes the sweep's own repair permanent.**

**Determinism.** `test_det__sweep_report_is_stable` — two sweeps produce byte-identical JSON. The captured
`assertion_text` is normalised (paths relativised, addresses stripped) before it enters the report, and
**no timing field enters it at all** (R3).

**Performance.** `PERF` — the sweep's 6-minute budget (methodology §5.3 stage 8) is recorded as the
baseline for later phases; at P0 the sweep runs in seconds and the budget is a ceiling, not a comparison.
Timings are written to `reports/perf/<run_id>.jsonl`, never into `negative-control-sweep.json`.

**Effort: 5.0 days** (R11). The exact-set sweep, the six meta-tests, fourteen injectors, the public
`import_closure`, and eleven gates each observed red with its assertion captured are not two days.

---

### BUILD P0-B4 — THE TWO FIELD OBSERVATIONS, AND THE ABSENCE-SCOPE RULE · 1.0 day

**What it produces.** Two questions asked by a named human on a recorded date, and the mechanism that makes
a *non-answer* visible rather than silent.

#### Files created

```
docs/FIELD-OBSERVATIONS.md   rows: {id, question_verbatim, sent_to, sent_by, sent_on,
                                    replied_on | standing_absence_since, reply_verbatim | null}
docs/ABSENCE-SCOPE.md        the written inclusion rule that closes risk R13
tests/unit/test_field_observations.py
```

**E1** — IFSCA, Division of Investment Funds: *are these checks run on receipt; how often is an FME return
sent back; are filed returns obtainable?* **E1b** — KFin / CAMS / Basiz: the written house NAV-tolerance
question, verbatim from spec §IV.1.2. Both are sent by a named person; **this document does not send
them.**

`docs/ABSENCE-SCOPE.md` is the precondition for every absence claim in the programme: **no absence claim
ships with a count until this file states the inclusion rule.** It is what `ci/no-bare-absence.sh` and
`measure/absence.py` enforce mechanically.

#### Functionality validation

**Unit.** `test_field_observations__every_row_resolves` — every row carries either `replied_on` or
`standing_absence_since`; a row with neither fails the build.
`test_field_observations__standing_absence_renders_its_duration` — the renderer formats a standing absence
as *"asked <date>, unanswered for N days"*, never as silence. This is the watcher's `gap_since` rule
(spec §II.4.5 V6) applied to a human channel: **an unobserved day is not a quiet day.**

**Negative control — impossible, and it is recorded as such.**
**NC-N16 (new, `injector: NONE`)** — *a question quietly dropped.* `why_impossible`: *"Dropping a question
leaves no artifact to inject into; the failure is the absence of a row, and a test cannot enumerate rows
that were never written."* **What it costs:** the mechanised half covers only questions that reached the
file. The substitute is procedural and stated in the DoD's §H — E1 and E1b are named in the risk register
(R7, R6) and in the P14 claim register, so a dropped question surfaces at two later gates rather than at
none. *(Id note, arbitration **C9**: this entry was `NC-N07`. `07` §3 defined a different entry under the same
number — an all-clear mark drawn as vector paths — and each document instructed the other to move.
**Neither keeps it.** This entry is now **`NC-N16`**, `07`'s is **`NC-N40`**, and **`NC-N07` is RETIRED
PERMANENTLY**, never reassigned. The row lives in `01` §2's canonical registry; this document references
it.)*

**Effort: 1.0 day.**

---

## P0 · The measurement this phase produces

> **`gates_live / gates_written = 15 / 15`, and the `LIVE` set is exactly rows `{1…13, 17, 18}` while the
> `PENDING` set is exactly rows `{14 → P2, 15 → P11, 16 → P13-B0}`.** Denominator: **18**, the rows of
> `ci/GATES.md` (R5). Warrant **MEASURED**.

**The arithmetic, corrected, because the previous form of this number could not be wrong.** The earlier
figure read `12 / 12` with *"4 of the 16 rows `PENDING`"*, counting the predicate-loader admission twin as
the fourth — but R5 rules explicitly that the loader is **not** a registry row (it is NC-Q02, and it
belongs to P4). Rows 1–13 are demonstrable red at P0 by R5's own table, rows 17–18 are added here and are
demonstrable at P0, and rows 14/15/16 are the only pending ones. **13 + 2 = 15 live, 3 pending, 18 written.**
*The alternative this beat:* promoting the loader gate to a seventeenth row — rejected because R5 already
argues, correctly, that a property of `predicates/registry.py` is not a CI gate, and because a row whose
admission-side twin is impossible for four phases would sit in `gates_live` carrying no information (which
is exactly what `provisional_count` exists to keep out).

This quantity does not exist anywhere today. The specification lists the gates; **not one of them has ever
been observed to fail.** The subordinate figure — `entries_caught / entries_active`,
`guards_flipped / guards_expected_to_flip`, `none_count` and `provisional_count`, from
`reports/negative-control-sweep.json` — is reported as five integers and never as a percentage.

Ledger rows:

```json
{"phase":"P0","build":"P0.3","metric":"ci.gates_demonstrated_red","numerator":15,"denominator":18,
 "denominator_source":"rows of ci/GATES.md, enumerated in plan/02 §1 R5","warrant":"MEASURED",
 "produced_by":"tools/nc_sweep.py","command":"make nc-sweep && cat docs/GATE-LIVENESS.md",
 "caveat":"3 rows are PENDING (14 -> P2, 15 -> P11, 16 -> P13-B0). The LIVE and PENDING sets are
           PRE-REGISTERED as literals in test_contract__live_set_is_pre_registered; moving a row between
           them fails the build without a dated argument in ci/GATES.md",
 "date":"20__-__-__"}
{"phase":"P0","build":"P0.3","metric":"nc.guards_flipped","numerator":null,"denominator":null,
 "denominator_source":"guards declared flips:true in tests/negative/catalogue.yaml","warrant":"MEASURED",
 "produced_by":"tools/nc_sweep.py","command":"make nc-sweep",
 "caveat":"entries_caught counts ENTRIES and is the weaker figure; this row counts GUARDS and is the one
           DoD line C4 is about",
 "date":"20__-__-__"}
```

## P0 · Exit gate

**TRUE iff all of:**

1. **The `LIVE` set is exactly `{1…13, 17, 18}` and the `PENDING` set is exactly `{14, 15, 16}`** —
   `test_contract__live_set_is_pre_registered` green. Every `LIVE` gate has been **observed red** against
   its named broken build, and the failing assertion is recorded in `docs/GATE-LIVENESS.md` **and** in
   `reports/negative-control-sweep.json`'s `assertion_text` field. *Moving any row out of `LIVE` fails this
   gate; it may be moved only with an appended, dated argument in `ci/GATES.md`, and the argument is part
   of the exit evidence.* **This criterion replaces `gates_live == gates_written`, which was `x == x`:
   `gates_written` was decided by the same person deciding whether a gate could be demonstrated, so any
   gate that resisted demonstration could be moved to `PENDING` and the ratio would still read `n/n`.**
2. Every `PENDING` row names a phase; no row is permanently pending.
2a. **`guards_flipped == guards_expected_to_flip`**, and `test_nc_meta__every_expected_guard_flipped` and
   `test_nc_meta__ids_are_unique` are both green. An entry whose weakest guard flipped while its
   load-bearing guard did not is **not** `caught`.
3. `ci/licence-gate.sh` exits non-zero against the research venv, naming `formulas` **and** `pycel`.
4. `make corpus-verify` green on all nine; one *value* assertion per workbook (R-GOLD-2).
5. `docs/ABSENCE-SCOPE.md` exists and is non-empty. **No absence claim may ship with a count before this.**
6. `docs/FIELD-OBSERVATIONS.md` carries E1 and E1b with a named sender and a date sent.
7. gVisor's licence is either opened and recorded, or the fallback boundary is recorded in
   `docs/LICENCES.md` **and** flagged for the deployment surface (R7).
8. **`ci/catalogue-ids.sh` green** — every `NC-` id in `plan/*.md` is defined in exactly one document and
   lies inside that document's R5a band. *This runs at P0, before the first entry is written, because four
   documents have already collided and the collisions are invisible to every other meta-test.*
9. **`ci/golden-literals-are-traceable.sh` green** — no golden compares an integer literal that appears in
   neither `01` §0.3's table nor a ledger row. `2,373` is in neither today (§0.2 N3a).

**Mutation score.** No Tier V module ships at P0. `tools/mutation/run.py` runs against
`src/cdfc/measure/absence.py` (Tier S, threshold `K/V ≥ 0.70`, blocking two phases after first ship) and
the result is recorded with its four census terms, not as a percentage.

## P0 · What it kills if it fails

**Nothing structural — and that is exactly why the failure is dangerous.** If a commitment cannot be
mechanised, it is downgraded to a documented preference **in writing**, and
`docs/GATE-LIVENESS.md` publishes the count of un-mechanised commitments, which then renders on the report
surface at P14. A project whose honesty machinery is aspirational is the category it is arguing against;
publishing the count is the only version of that admission that survives contact with a deadline.

The one branch that can block: **if gVisor cannot be licensed or run, P1's sandbox is `seccomp` +
namespaces**, a weaker boundary, disclosed on the deployment surface and named in the risk register. P1
proceeds either way — the guard's *checks* are not the guard's *confinement*.

---

# P1 — L0: RECEIPT, CONTAINER GUARD, DUAL-READER INGEST

**Effort: 8 engineer-days** · B1 1.5 · B2 2.0 · B3 3.5 · B4 1.0

## P1 · What it settles

**Whether the artifact can be read without the class of silent under-count this project has committed five
times — and what the two readers actually disagree about, on the real corpus, with the disagreements
classified rather than merely counted.**

Four of the five documented silent false negatives live in this phase's blast radius: namespace blindness
(35 of 54), shared-formula invisibility (211 of 505; 825 of 1,495 across the nine), the `<f[ >][^>]*>`
regex whose count was right and whose every extracted body was wrong, and the destructive round-trip
(3,663,391 → 65,877 bytes). §0.2 N3 adds a fifth question no earlier document asked: **what fraction of the
agreement check's firings are real?**

## P1 · Entry criteria

| Requires | Why the edge is real |
|---|---|
| **P0 complete.** The nine workbooks vendored and hashing stably; `make corpus-verify` green | The readers are validated against pinned bytes. A reader validated against a drifting fixture validates nothing |
| **P0-B3 complete.** `tests/negative/importgraph.py` exists and `make nc-sweep` runs | NC-P04's static tooth is an import-closure walk, and it must exist before the code it walks |
| **R7 resolved.** gVisor opened or the fallback recorded | The guard ships either way; the *confinement* claim does not |

## P1 · Builds

---

### BUILD P1-B1 — RECEIPT AND CONTENT ADDRESSING · 1.5 days

**What it produces.** A `sha256` over the exact received bytes, a per-part digest map, a blob on disk that
is never rewritten, and a refusal path that creates **no run row**.

#### Files created

```
src/cdfc/ingest/receipt.py
src/cdfc/canon.py                 RFC 8785 canonical JSON — one implementation, used everywhere
db/schema.sql                     blob(...), run(...), meta(schema_sha256)   (R6)
tests/unit/test_receipt.py  tests/property/test_prop_canon.py
tests/determinism/test_det__receipt_is_clock_free.py
```

#### Public interface

```python
@dataclass(frozen=True)
class Receipt:
    filing_sha256: str                    # lowercase hex, over EXACT received bytes
    n_bytes: int
    media_type: str
    received_at: str                      # RFC 3339 — AN ARGUMENT, never a clock read (R3)
    blob_path: Path                       # blobs/sha256/<aa>/<remaining-62>
    part_sha256: Mapping[str, str]        # every zip entry -> sha256, incl. every xl/worksheets/sheetN.xml

class RefusedAtReceipt(Exception):
    http_status: int                      # 413 over cap | 415 not a zip.  NO RUN ROW IS CREATED.
    reason: str

def receive(data: bytes, *, media_type: str, cap_bytes: int, blob_root: Path,
            received_at: str) -> Receipt: ...

# src/cdfc/canon.py
def canonical_json(obj: Any) -> bytes: ...        # RFC 8785, the ONLY serialiser for a hashed object
def sha256_hex(b: bytes) -> str: ...
```

**Why per-part digests are not decoration:** spec §III.4.1 requires that a re-derivation can say *which
sheet* changed. `part_sha256` is what makes that a lookup instead of a diff.

#### Data produced

`blobs/sha256/<aa>/<rest>` (mode `0444`) · one `blob` row · one `run` row **only on success**.

#### Functionality validation

**Unit.**
`test_receive__hash_is_over_exact_bytes` — a workbook whose bytes contain a trailing NUL hashes differently
from one without; no normalisation, no re-encoding.
`test_receive__over_cap_raises_413_and_writes_no_run_row` — asserts the `run` table row count is unchanged.
`test_receive__non_zip_raises_415` — `fixtures/adversarial/not-a-zip__renamed.xlsx`.
`test_receive__blob_is_written_read_only`.
`test_receive__part_digests_cover_every_entry` — on FME, exactly **42** entries digested (§0.3).

**Property.** *Invariant:* RFC 8785 canonicalisation is insertion-order invariant.
`tests/property/test_prop_canon.py::test_prop__canonicalisation_is_order_invariant` — generator: random
nested JSON trees over `{str, int, float-free, bool, null, list, dict}` with keys drawn from a Unicode
alphabet including `U+2011`; assert `canonical_json(shuffle(t)) == canonical_json(t)`. *Why this generator:*
two implementations disagreeing on key order produce two registry roots for one registry (spec §III.4.1).

**Golden.** `tests/golden/test_receipt_digests.py::test_golden__part_digests__fme` — the FME
`filing_sha256` equals `7d9a1960…` and the digest of `xl/worksheets/sheet10.xml` (the hidden `Dropdown`
sheet) is pinned. *Which workbook and why:* FME, because it is the only one carrying a hidden sheet **and**
the 3.55 MB `xl/model/item.data`, so the part map is exercised at both extremes.

**Determinism.** `test_det__receipt_is_clock_free` — `receive` called twice under `TZ=Pacific/Kiritimati`
and `TZ=UTC` with the same `received_at` argument produces identical `Receipt`s; and
`ci/no-clock-in-core.sh` covers `ingest/`.

**Negative controls.**
- **NC-P04** (existing) — *the artifact is re-serialised.* All three teeth are wired in this build because
  the blob is created here: **static** (`importgraph.py` asserts `Workbook.save`,
  `zipfile.ZipFile(...,'w')` and `open(...,'wb')` are unreachable from
  `cdfc.{ingest,schema,facts,calc,evaluate,verdict,probes,selfcheck,surface}`), **runtime**
  (`sha256(blob_path)` after a full run equals the receipt digest), **filesystem** (the blob directory is
  bind-mounted read-only and a write raises). Injector `injectors/openpyxl_save.py`.
- **NC-P04's golden twin** `tests/golden/test_roundtrip_destruction.py` — pins
  **3,663,391 → 65,877** and **19 → 0** `x14` validations, so the README's number has a script behind it.

**Performance.** `PERF-RECEIPT` (new budget) — `receive` on the 3.66 MB FME file: baseline to be recorded;
fail above 250 ms. Registered in `perf/baseline.ci.json` with `{machine, cpu, python, date}`.

**Effort: 1.5 days.**

---

### BUILD P1-B2 — THE CONTAINER GUARD · 2.0 days

**What it produces.** A refusal that happens **before any XML is parsed**, and a hardened parser
configuration that is the only one in the codebase.

#### Files created

```
src/cdfc/ingest/container_guard.py
src/cdfc/ingest/xmlsafe.py                the ONE lxml parser factory
src/cdfc/verdict/invalid.py               the eight run-level invalid.* causes  (stub enum at P1;
                                          P5 owns the rest of the vocabulary)
tools/fixtures/make_adversarial.py        deterministic from a seed
fixtures/adversarial/{zipbomb-entrycount__x100000.xlsx, zipbomb-ratio__x1000.xlsx,
                      zipbomb-entrysize__1gb.xlsx, xxe-entity__passwd.xlsx,
                      not-a-zip__renamed.xlsx, missing-part__no-workbook.xlsx,
                      oversized__over-cap.xlsx}
deploy/sandbox/runsc-profile.json  deploy/sandbox/seccomp.json                  (R7)
tests/negative/test_nc_ingest.py          NC-P05a/b/c
tests/e2e/test_e2e__sandbox_profile.py    linux_only, collected by filter not skip (R7)
```

#### Public interface

```python
@dataclass(frozen=True)
class GuardLimits:
    max_entries: int = 1024                        # observed max across the nine: 85
    max_entry_uncompressed_bytes: int = 16_777_216 # observed max: 3_551_232 (xl/model/item.data)
    max_total_uncompressed_bytes: int = 67_108_864 # observed max: 4_495_901
    max_total_ratio: float = 100.0                 # observed max: 6.2   (a ratio is not money)
    required_parts: tuple[str, ...] = ("[Content_Types].xml", "xl/workbook.xml",
                                       "xl/_rels/workbook.xml.rels")
    allowed_entry_suffixes: frozenset[str] = frozenset({".xml", ".rels", ".bin", ".data", ".png",
                                                        ".jpeg", ".jpg", ".emf", ".vml"})

class InvalidCause(StrEnum):                       # run-level, NOT the item-level 8x30 (audit V.7.3)
    CONTAINER_GUARD_TRIPPED = "invalid.container_guard_tripped"
    READER_STRUCTURAL_DISAGREEMENT = "invalid.reader_structural_disagreement"
    TEMPLATE_UNBOUND = "invalid.template_unbound"
    CELLS_BOUND_ZERO = "invalid.cells_bound_zero"
    PREDICATE_RAISED = "invalid.predicate_raised"
    CANARY_SILENT = "invalid.canary_silent"
    CLOSURE_VIOLATED = "invalid.closure_violated"
    DENOMINATOR_DISAGREEMENT = "invalid.denominator_disagreement"

class GuardTrip(Exception):
    cause: InvalidCause          # always CONTAINER_GUARD_TRIPPED
    detail: str                  # which limit, observed value, limit value

def guard(blob_path: Path, limits: GuardLimits = GuardLimits()) -> GuardReport: ...

# src/cdfc/ingest/xmlsafe.py
def safe_parser() -> etree.XMLParser:
    return etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False,
                           dtd_validation=False, huge_tree=False, recover=False)
def fromstring(b: bytes) -> etree._Element: ...   # the ONLY sanctioned entry point
```

**A guard trip is a run-level `invalid.*` cause, never a per-cell reason code and never a `FAIL`.** *A
filing we could not safely open is not a filing that failed a check* (audit §V.7.3).

#### Data produced

`GuardReport{entries, total_uncompressed, max_entry, ratio, missing_required, disallowed_suffixes}`,
recorded in the extraction manifest whether or not it tripped.

#### Functionality validation

**Unit.** One test per limit, table-driven over the seven adversarial fixtures, each asserting the
`GuardTrip.detail` names the limit, the observed value **and** the limit value. A guard that says only
"rejected" cannot be triaged.

**Golden — the admission-side positive control, and it is mandatory.**
`tests/golden/test_guard_admits_the_corpus.py::test_golden__all_nine_pass_the_guard` — every prescribed
workbook passes with its observed maxima recorded in `docs/measurements/P1-guard-headroom.md`. *Which
workbooks and why:* all nine, because the two large ones (85 entries, 3.55 MB single part) set the
headroom and the seven small ones prove the limits are not tuned to the large ones. **Without this the
guard is a reject-everything baseline that would score perfectly on the negative controls alone.**

**Negative controls.**
- **NC-P05a** (existing) — *the guard runs after the parser.* Injector `injectors/guard_after_parse.py`.
  Guard test asserts the outcome is `REJECTED` or `INVALID(invalid.container_guard_tripped)` **and that
  `cdfc.ingest.xmlsafe.fromstring` was never called**, via a spy installed in `conftest.py`. The spy is
  installed on *our* factory, which is why `xmlsafe.py` exists as a single entry point at all.
- **NC-P05b** (existing) — `fixtures/adversarial/xxe-entity__passwd.xlsx`; the parse raises and no file
  outside the fixture tree is opened.
- **NC-P05c** (existing) — the emitted cause comes from `InvalidCause`, not from a per-cell reason code.
- **NC-P08 (new)** — *`lxml` is constructed somewhere other than `xmlsafe.py`.* Injector
  `injectors/raw_lxml_parser.py` replaces one call site with `etree.fromstring`;
  `tests/negative/test_nc_ingest.py::test_nc__P08_only_one_parser_factory` walks the AST of
  `src/cdfc/` and asserts `etree.XMLParser(` and `etree.fromstring(` appear **only** in `xmlsafe.py`.
  A hardened parser that can be bypassed is a hardened parser that will be.

  ```yaml
  - id: NC-P08
    component: ingest
    break: "an lxml parser is constructed outside xmlsafe.py, without resolve_entities=False"
    measured_instance: "none yet — a structural control, added because xmlsafe.py is the only thing
                        standing between the pipeline and an XXE payload in a filer-supplied zip"
    injector: raw_lxml_parser
    why_impossible: null
    guard_tests:
      - tests/negative/test_nc_ingest.py::test_nc__P08_only_one_parser_factory
    positive_control: tests/unit/test_xmlsafe.py::test_safe_parser__parses_a_real_sheet
    status: ACTIVE
  ```

**Determinism.** The adversarial fixtures are generated deterministically from a seed;
`test_det__adversarial_fixtures_regenerate_identically`.

**Performance.** `PERF-GUARD` (new) — under 5 ms on FME (spec §III.3.1 F1 gives `<5 ms D`); fail above
20 ms. The guard reads the central directory, never the entries.

**Effort: 2.0 days.**

---

### BUILD P1-B3 — THE THREE READERS, THE COMPETENCE MATRIX, AND THE AGREEMENT VECTOR · 3.5 days

**What it produces.** The authoritative reading of the artifact, a second reading by a different
instrument, a third reading by a second implementation of ours for the fields no third-party library can
read, and an agreement vector whose every firing means something.

**This build is where §0.2 N3 lands. Read it before writing a line.**

#### Files created

```
src/cdfc/ingest/reader_lxml.py       READER A — authoritative: raw zipfile + lxml, namespace-aware,
                                     extLst/x14, styles.xml, sharedStrings.xml, workbook.xml
src/cdfc/ingest/reader_lxml_b.py     READER A' — a SECOND, independently written implementation for the
                                     fields B is not competent for. Different traversal: driven by
                                     [Content_Types].xml part enumeration and a qualified-name set,
                                     not by workbook.xml's rel graph
src/cdfc/ingest/reader_openpyxl.py   READER B — formula TEXT with shared-formula row-shifting, and
                                     data_only=True cached values. NEVER validations. NEVER a save.
src/cdfc/ingest/competence.py        FIELD_DEFINITIONS, COMPETENCE, and the escalation rule
src/cdfc/ingest/agreement.py         compare() -> Agreement
docs/READER-COMPETENCE.md            one row per field: the written definition + why each instrument is
                                     or is not a party. Append-only. (R9)
tests/differential/test_diff__lxml_vs_openpyxl.py           (D1)
tests/differential/test_diff__lxml_vs_lxml_b.py             (D1', new)
tests/golden/test_schema_constants.py                       (the ingest half; P2 owns the rest)
tests/golden/test_x14_blindness_positive_control.py
tests/negative/test_nc_ingest.py                            NC-P01, NC-P02, NC-P03, NC-P06, NC-P07
```

#### Public interface

```python
FormulaEncoding = Literal["TEXT", "SHARED_MASTER", "SHARED_DEPENDENT", "ARRAY", "NONE"]

@dataclass(frozen=True)
class FormulaRecord:
    sheet: str; ref: str
    encoding: FormulaEncoding
    text: str | None            # None iff encoding == SHARED_DEPENDENT
    si: int | None
    master_ref: str | None      # the SHARED_MASTER this dependent belongs to
    shared_ref_range: str | None
    materialised: str | None    # row/col-shifted text; filled by reader B, cross-checked by A'

@dataclass(frozen=True)
class ValidationRecord:
    sheet: str; namespace: Literal["main", "x14"]
    type: str; sqref: str
    formula1: str | None; formula2: str | None
    resolution: Literal["RANGE", "DEFINED_NAME", "FILING_CONDITIONAL", "UNRESOLVED"]   # §0.2 N7
    resolved_range: str | None

@dataclass(frozen=True)
class RawWorkbook:
    sheets: tuple[SheetRecord, ...]         # name, state, part, sheet_sha256, protected, dimension
    cells: Mapping[tuple[str, str], CellRecord]
    formulas: tuple[FormulaRecord, ...]
    validations: tuple[ValidationRecord, ...]
    defined_names: tuple[DefinedName, ...]  # scope: WORKBOOK | sheet name;  is_ref_error: bool
    merged_ranges: tuple[str, ...]
    styles: StyleTable
    shared_strings: tuple[str, ...]
    manifest: ExtractionManifest

def read(blob_path: Path) -> RawWorkbook                      # reader_lxml
def read_b(blob_path: Path) -> RawWorkbookB                   # reader_lxml_b, the same 8 fields only
def read_formula_text_and_cached(blob_path: Path) -> ReaderBView   # reader_openpyxl
```

```python
# src/cdfc/ingest/competence.py
AGREEMENT_FIELDS = ("n_sheets", "sheet_names", "hidden_sheets", "n_cells", "n_formula_cells",
                    "n_validations", "n_defined_names", "merged_ranges")
STRUCTURAL_FIELDS = ("n_sheets", "sheet_names", "hidden_sheets")

FIELD_DEFINITIONS: dict[str, str] = {
  "n_cells":          "count of <c> elements across every worksheet part named by workbook.xml's rels",
  "n_formula_cells":  "count of <c> elements containing an <f> child, ANY encoding",
  "n_validations":    "count of dataValidation elements in the main namespace PLUS the x14 namespace",
  "n_defined_names":  "count of definedName elements in workbook.xml, ANY scope, including _xlnm.*",
  ...
}

class Instrument(StrEnum): A = "reader_lxml"; A_PRIME = "reader_lxml_b"; B = "reader_openpyxl"

@dataclass(frozen=True)
class Competence:
    parties: frozenset[Instrument]
    measured_on: frozenset[str]      # workbook sha8s on which the EXCLUSION was measured (R9)

COMPETENCE: dict[str, Competence] = {
  "n_sheets":         Competence(frozenset({A, A_PRIME, B}), ALL_NINE),
  "sheet_names":      Competence(frozenset({A, A_PRIME, B}), ALL_NINE),
  "hidden_sheets":    Competence(frozenset({A, A_PRIME, B}), ALL_NINE),
  "merged_ranges":    Competence(frozenset({A, A_PRIME, B}), ALL_NINE),
  # The four below exclude B. At P1-B3 the exclusion is measured on FME ALONE (§0.2 N3, n = 1).
  # P1-B3 MUST widen measured_on to all nine before the matrix classifies all 72 cells.
  "n_cells":          Competence(frozenset({A, A_PRIME}), {"7d9a1960"}),  # B counts non-None VALUES
  "n_formula_cells":  Competence(frozenset({A, A_PRIME}), {"7d9a1960"}),  # B returns ArrayFormula objects
  "n_validations":    Competence(frozenset({A, A_PRIME}), {"7d9a1960"}),  # B namespace-blind: 35 of 54
  "n_defined_names":  Competence(frozenset({A, A_PRIME}), {"7d9a1960"}),  # B: workbook-scope only, 4 of 12
}

BLIND_CONTROLS: dict[str, dict[Instrument, dict[str, int]]] = {   # PINNED, not escalated
  "n_validations": {B: {"fme": 35, "al_monthly": 1, "itfs": 7}},   # THREE of nine at P1-B3's start;
}                                                                 # grown to nine before P1's exit gate
```

**Three things this shape forces, and each closes a way P1's number could be an artifact of P1.**

1. **`measured_on` is not decoration.** `test_contract__incompetence_is_measured_on_every_workbook_it_classifies`
   fails the build when a field whose `parties` exclude an instrument is compared on a workbook outside
   `measured_on`; that cell of the 72-cell matrix reads `NOT_COMPARABLE(competence_unmeasured)`, **never
   `AGREE`**. Widening `measured_on` requires the measurement, not an edit. Today the matrix would classify
   64 unmeasured cells from a judgment taken on one workbook.
2. **`BLIND_CONTROLS` must cover all nine before it is trusted.** It pins three. A pinned control that
   covers a third of the corpus tells us the ecosystem's blind spot is unchanged on a third of the corpus.
   P1-B3's deliverable is nine rows, and `test_golden__openpyxl_still_undercounts` asserts nine.
3. **The four `A`/`A′`-only fields are `SAME-AUTHOR` unless R11's second author exists**, and the vector
   over them renders with that label attached. Converting the project's one *external* disagreement into a
   `BLIND_CONTROLS` constant is defensible; converting it *silently* is how the only foreign instrument in
   the project stops being able to contradict us.

```python
CellVerdict = Literal["AGREE", "DISAGREE_ESCALATED", "DISAGREE_PINNED", "NOT_COMPARABLE"]

@dataclass(frozen=True)
class Agreement:
    per_field: Mapping[str, FieldAgreement]     # verdict, parties, values, definition
    structural_ok: bool
    escalations: tuple[str, ...]                # non-structural fields marked NOT_RUN downstream
def compare(a: RawWorkbook, a_prime: RawWorkbookB, b: ReaderBView) -> Agreement
```

**The escalation rule, normative:**

```
For each field f in AGREEMENT_FIELDS:
    parties := COMPETENCE[f]                      # always >= 2, asserted at import
    if all parties agree                      -> AGREE
    elif f in STRUCTURAL_FIELDS                -> INVALID(invalid.reader_structural_disagreement)
    else                                       -> DISAGREE_ESCALATED: mark f; every predicate reading a
                                                  fact derived from f returns
                                                  NOT_RUN(not_run.extractor_disagreement)
For each declared-blind instrument reading of f:
    compare against BLIND_CONTROLS[f]          -> DISAGREE_PINNED if equal   (a positive control)
                                               -> ESCALATE if NOT equal      (the library changed under us)
```

**The second half of that rule is the important half.** openpyxl reporting 35 is expected and pinned.
openpyxl reporting **54** would mean the ecosystem's blind spot was fixed, which is a finding we must
learn about rather than absorb — the same discipline methodology §2.1 applies to
`test_golden__openpyxl_still_undercounts`. *An absence claim about the ecosystem must be re-measured, not
remembered.*

#### Data produced

`docs/measurements/P1-agreement.md` — the **8 × 9 matrix**, every cell one of the four verdicts, every
non-`AGREE` cell carrying the two values and the named mechanism. This is P1's number.

#### Functionality validation

**Unit.**
`test_reader_lxml__hidden_sheet_is_read` — `Dropdown`, `state='hidden'`, part `xl/worksheets/sheet10.xml`.
`test_reader_lxml__x14_validations_are_seen` — 19, and `'7. AML-CFT'` has 5.
`test_reader_lxml__defined_names_include_sheet_scoped` — 12, of which 4 carry `#REF!`
(`ExternalData_1/_2/_3/_17`) and 4 are `_xlnm.Print_Area`.
`test_reader_lxml__encoding_is_recorded_for_every_formula` — every `FormulaRecord.encoding` is set;
census `{TEXT: 261, SHARED_MASTER: 32, SHARED_DEPENDENT: 211, ARRAY: 1}` (§0.2 N5).
`test_reader_openpyxl__materialises_a_shared_dependent` — `'3. Portfolio'!O4 == "=SUM(C4:N4)"` from master
`O3 = SUM(C3:N3)` over `ref="O3:O12"`. **The row-shift is the part that silently goes wrong**, which is why
openpyxl is retained for exactly this.
`test_competence__every_field_has_at_least_two_parties` — asserted at import time, so a field cannot be
compared against itself.

**Property.** *Invariant:* materialising a shared dependent then re-parsing its reference set yields the
same reference set the master's translation implies. Generator: every one of the **32 shared groups** on
FME × every member of its `ref` range (211 dependents), plus the 645-formula `ALR` workbook whose shared
share is the corpus's worst (399 of 645).
`tests/property/test_prop_reader.py::test_prop__shared_materialisation_is_a_pure_translation`.

**Golden.**
`tests/golden/test_schema_constants.py::test_golden__formula_cells__fme` — `505 == 261 + 32 + 1 + 211`,
**plus** the value assertion `'3. Portfolio'!O4 == "=SUM(C4:N4)"` (R-GOLD-2).
`::test_golden__validations__fme` — `54 == 35 + 19`, plus the per-sheet map
`{'1. Introduction': (8,9), '2. Summary': (3,0), '3. Portfolio': (11,2), '4. Investors': (3,0),
'5. PMS': (6,0), '6. Complaints': (1,1), '7. AML-CFT': (0,5), '8. Compliance Status': (2,2),
'9. Compliance Report': (0,0), 'Dropdown': (1,0)}`.
`tests/golden/test_x14_blindness_positive_control.py::test_golden__openpyxl_still_undercounts` — asserts
`{FME: 35, AL_monthly: 1, ITFS: 7}` **today**. *Which workbooks and why:* the three measured undercount
instances; `AL_monthly_report` is the extreme at 1 of 10.

**Differential.**
**D1** — A vs B, over the four fields where `B ∈ COMPETENCE`. Disagreement on a structural field ⇒
`INVALID`. `tests/differential/test_diff__lxml_vs_openpyxl.py`.
**D1′ (new)** — A vs A′, over the four fields where B is not a party.
`tests/differential/test_diff__lxml_vs_lxml_b.py`. **Structural independence is asserted the same way the
denominator's is:** `test_diff__readers_are_structurally_independent` — the import closures of
`reader_lxml.py` and `reader_lxml_b.py` share no module inside `cdfc` except `cdfc.ingest.xmlsafe`
(declared), and `test_nc__P09_mutating_A_moves_only_A` (new, the NC-D02d shape one layer up) mutates A's
validation walk and asserts A′'s count does not move.

**And D1′ is parametrised over all four fields, not over the validation walk alone.** `test_nc__P09` as
first written mutates one extraction path; the other three (`n_cells`, `n_formula_cells`,
`n_defined_names`) would then carry an *asserted* independence rather than a *demonstrated* one — and those
three are where the project's founding undercount actually lives.
`test_nc__P09_mutating_A_moves_only_A[field]` is therefore parametrised over
`{n_cells, n_formula_cells, n_validations, n_defined_names}`, mutating **that field's** extraction path in
A and asserting A′'s value for that field does not move. Four parametrisations, four observed reds, four
rows in `docs/GATE-LIVENESS.md`. *This is the only version of the dual-reader claim that carries
information for the fields the project exists because of.*

**Negative controls.**
- **NC-P01** (existing) — namespace blindness. Injector `injectors/reader_nsblind.py` swaps A's validation
  scan for `root.iter(M + "dataValidation")`. Guard: `test_golden__validations__fme` reads 35 and
  `'7. AML-CFT': 0`; and `test_nc__P01_namespace_blind_reader_rejected` asserts the D1′ check **escalates**
  (A vs A′ now disagree) rather than silently absorbing.
- **NC-P02** (existing) — shared-formula invisibility. Injector `injectors/reader_textonly.py`. Guards
  assert `505 == 294 + 211` **and** the materialised text of `O4`, and the corpus-wide `1,495 / 825` split.
  `test_nc__P02b_encoding_is_recorded` asserts every anchor carries its `FormulaEncoding`.
- **NC-P03** (existing) — a lexical matcher over XML. `ci/no-regex-over-xml.sh` is the standing structural
  rule; `test_nc__P03_element_encodings_table` is table-driven over the five legal encodings and asserts
  the **body**, not the count — because the measured refinement is that
  `re.findall(r"<f[ >][^>]*>")` returns the *right count on every sheet* while 50 of 50 matches on
  `'2. Summary'` swallow the closing tag.
- **NC-P06** (existing) — a partial agreement check. Injector `injectors/agreement_partial.py`.
  `test_nc__P06_hidden_state_disagreement_is_INVALID`.
- **NC-P07 (new)** — *competence is narrowed to make a disagreement disappear.* (R9.)

  ```yaml
  - id: NC-P07
    component: ingest
    break: "an instrument is removed from COMPETENCE[f] so a real disagreement stops escalating"
    measured_instance: "not yet realised — but on the FME workbook 4 of 8 fields disagree on day one
                        (plan/02 §0.2 N3), so the pressure to widen the blind set is immediate and real"
    injector: competence_narrow
    why_impossible: null
    guard_tests:
      - tests/negative/test_nc_ingest.py::test_nc__P07_narrowing_competence_requires_a_reason
      - tests/contract/test_contract__competence_is_pinned
    positive_control: tests/differential/test_diff__lxml_vs_lxml_b.py::test_diff__all_four_fields_agree_on_fme
    status: ACTIVE
  ```

  `test_nc__P07` removes `A_PRIME` from `COMPETENCE["n_validations"]` and asserts the build fails because
  (a) the field now has fewer than two parties and (b) `docs/READER-COMPETENCE.md` has no matching dated
  row.
- **NC-P09 (new)** — *the two "independent" readers are one reader called twice.* Injector
  `injectors/reader_b_calls_a.py` makes `read_b` delegate to `read`;
  `test_nc__P09_mutating_A_moves_only_A[field]` — **parametrised over all four `A`/`A′` fields** — is the
  only test that distinguishes two implementations from one, and it is the reason A′ exists as a file
  rather than as a second function.
- **NC-P11 (new)** — *a competence exclusion measured on one workbook classifies all nine.* (R9, §0.2 N3.)

  ```yaml
  - id: NC-P11
    component: ingest
    break: "COMPETENCE excludes an instrument from a field on the strength of a measurement taken on one
            workbook, and the exclusion then classifies that field on all nine"
    measured_instance: "MEASURED: plan/02 §0.2 N3 measures eight fields on FME ALONE (n = 1); the matrix
                        it produces classifies all 72 cells of the 8 x 9 agreement matrix (n = 9), and the
                        four fields it excludes openpyxl from are the four where the project's founding
                        external disagreement lives (35 of 54)"
    injector: competence_generalised
    why_impossible: null
    guard_tests:
      - path: tests/contract/test_contract__incompetence_is_measured_on_every_workbook_it_classifies
        flips: true
      - path: tests/golden/test_x14_blindness_positive_control.py::test_golden__openpyxl_still_undercounts
        flips: false
    positive_control: tests/differential/test_diff__lxml_vs_openpyxl.py::test_diff__three_party_fields_agree_on_all_nine
    status: ACTIVE
  ```

  The injector shrinks `measured_on` for `n_validations` to `{"7d9a1960"}` and asserts the build fails when
  the matrix is computed over all nine — the cell reads `NOT_COMPARABLE(competence_unmeasured)`, never
  `AGREE`. **Admission-side twin (`flips: false`):** the pinned blind-control golden must stay green, so the
  guard is not simply refusing to compare.

**Determinism.** `test_det__reader_output_is_order_stable` — `RawWorkbook`'s tuples are explicitly sorted
by `(sheet_index, row, column)`; two runs under different `PYTHONHASHSEED` canonicalise identically.

**Performance.** `PERF-L0A` — reader A on FME, cold: baseline **28 ms** (spec, MEASURED); fail above 90 ms.
`PERF-RB` — reader B: baseline **202 ms**; fail above 300 ms. Both against `perf/baseline.ci.json`.

**Effort: 3.5 days.**

---

### BUILD P1-B4 — THE EXTRACTION MANIFEST AS A FIRST-CLASS OUTPUT · 1.0 day

**What it produces.** The record of what was read, what was skipped, what namespaces were seen and **what
was not understood** — as an output, not a log.

#### Files created

```
src/cdfc/ingest/manifest.py           ExtractionManifest  (R2)
db/schema.sql                         + extraction_manifest(run_id, reader, ...)
tests/unit/test_extraction_manifest.py
tests/contract/test_contract__manifest_is_not_a_log.py
```

#### Public interface

```python
@dataclass(frozen=True)
class ExtractionManifest:
    reader: Instrument
    parts_read: tuple[str, ...]
    parts_skipped: tuple[tuple[str, str], ...]        # (part, WHY) — a skip with no reason is a defect
    namespaces_seen: tuple[str, ...]
    constructs_not_understood: tuple[Construct, ...]  # (part, xpath, qname, count, first_ref)
    guard_report: GuardReport
    agreement: Agreement | None                       # populated on the authoritative reader only
def build(...) -> ExtractionManifest
```

#### Functionality validation

**Unit.** `test_manifest__every_skipped_part_has_a_reason` — a `parts_skipped` entry with an empty reason
raises at construction. `test_manifest__unknown_qname_is_recorded` — inject a synthetic
`<foo:bar>` into a copied sheet part by raw-zip surgery and assert it appears in
`constructs_not_understood` with its count and first reference.

**Golden.** `tests/golden/test_manifest_namespaces.py::test_golden__namespaces_seen__fme` — asserts the
namespace set includes the main, `x14`, `x14ac`, `mc`, `xr` and `r` URIs, and that `parts_read` covers all
**42** entries or names each skip. *Which workbook and why:* FME, the only one carrying the `x14` extension
block and the `xl/model/` parts.

**Contract.** `test_contract__manifest_is_not_a_log` — `ExtractionManifest` is frozen, serialises through
`canonical_json`, and contains no free-text field other than the per-skip reason.
`test_contract__two_manifests_are_distinct` (R2).

**Negative control.** **NC-P10 (new)** — *a construct is skipped silently.* Injector
`injectors/manifest_swallow.py` drops the `constructs_not_understood` append;
`test_nc__P10_unknown_construct_must_surface` asserts the synthetic `<foo:bar>` fixture produces a
non-empty list. *And its declared limit, in the DoD's §H:* the list contains **only what we knew to look
for** (methodology §7.5, NC-N06). This build does not close that; it makes the residue visible.

**Effort: 1.0 day.**

---

## P1 · The measurement this phase produces

> **The reader-agreement matrix: 8 fields × 9 workbooks = 72 cells**, each labelled
> `AGREE | DISAGREE_ESCALATED | DISAGREE_PINNED | NOT_COMPARABLE`, with every non-`AGREE` cell carrying
> the two values and the **named mechanism**. Warrant **MEASURED**. Denominator **72**.
>
> **Published as TWO vectors, never as one number:**
> **(i) agreement over the four three-party fields — `/36`** — A, A′ and B all present, and this is the
> only vector containing an instrument nobody here wrote.
> **(ii) agreement over the four `A`/`A′`-only fields — `/36`, labelled `SAME-AUTHOR — see §7.5`**
> unless R11's second author exists.
> A single `/72` figure averages an external check with a self-check and reports the result as one
> instrument. It is banned on every surface; `test_contract__agreement_renders_as_two_vectors` asserts it.

Today exactly one cell of that matrix is known (`n_validations`, FME, 35 vs 54) and §0.2 N3 adds seven
more for FME alone. **The other 64 are unmeasured.** The matrix is published in
`docs/measurements/P1-agreement.md` together with the competence matrix that classifies it **and the
`measured_on` set for every exclusion** (R9), because a disagreement count without the competence
classification is the number that gets the check switched off — and a competence classification without its
`measured_on` set is a judgment from `n = 1` wearing a measurement's label.

Secondary, and new: the **openpyxl blind-control vector** `{FME: 35, AL_monthly: 1, ITFS: 7}` re-measured
rather than remembered.

## P1 · Exit gate

**TRUE iff all of:**

1. All nine workbooks ingest; no code path re-serialises a received filing (NC-P04, all three teeth).
2. `docs/measurements/P1-agreement.md` published, all 72 cells classified, **every non-`AGREE` cell
   naming its mechanism**, and every `NOT_COMPARABLE` cell naming its second party.
3. Gate **G-READERS**: readers agree on `{n_sheets, sheet_names, hidden_sheets}` for **9 of 9**. *A
   workbook that fails is excluded with a stated reason and its field surface is `null`; the corpus
   shrinks and the plan continues.*
   **G-READERS is a floor and it is very nearly certain to pass, so it is not evidence on its own.** Those
   three fields are exactly the ones where `COMPETENCE` admits all three instruments, and §0.2 N3 has
   already measured them agreeing on the flagship. The four fields where a disagreement is *known to exist*
   — `n_cells`, `n_formula_cells`, `n_validations`, `n_defined_names` — are the four from which `B` has
   been declared incompetent, so the gate's FAIL branch has no realistic path to firing. *A gate with a
   near-certain pass produces no information, and P1's exit gate was spending a criterion on it.*
3a. Gate **G-READERS-B (new, and this is the one that can fire)**: for **each** of the four `A`/`A′`-only
   fields, A and A′ agree on **9 of 9**, **and** `test_nc__P09_mutating_A_moves_only_A[field]` has been
   observed red for **that field's** extraction path — not for the validation walk alone. FAIL branch:
   the field is `DISAGREE_ESCALATED` on the workbooks where the two implementations differ, every
   predicate reading a fact derived from it returns `NOT_RUN(not_run.extractor_disagreement)`, and the
   settled fraction falls, which is the behaviour the whole escalation rule exists to produce.
4. The container guard trips on each of the five hostile fixture classes **and admits all nine prescribed
   workbooks**.
5. `docs/READER-COMPETENCE.md` carries a written definition for each of the eight fields **and the
   `measured_on` workbook set for every exclusion**;
   `test_contract__competence_is_pinned` and
   `test_contract__incompetence_is_measured_on_every_workbook_it_classifies` are both green;
   `BLIND_CONTROLS` covers **all nine** workbooks, not three.
6. NC-P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, **P11** all `ACTIVE` in the catalogue and all
   observed red under their injectors; `make nc-sweep` reports `entries_caught == entries_active`
   **and `guards_flipped == guards_expected_to_flip`** — including all four parametrisations of
   `test_nc__P09_mutating_A_moves_only_A[field]`.

**Mutation score, reported with the equivalent-mutant caveat in the same sentence.** `ingest/` is Tier I,
threshold `K/V ≥ 0.80`, blocking **one phase after first ship** — i.e. reported at P1 and blocking at P2.
Form: `ingest/: K/V = <k>/<v> (floor) · K/(V−E) = <k>/<v−e> with E = <e> adjudicated, arguments in
reports/mutation/ingest.ledger.jsonl · I = <i>, T = <t> (ids listed)`.

## P1 · What it kills if it fails

- **If the readers cannot be reconciled on a workbook:** that workbook is excluded with a stated reason,
  its field surface is `null`, and the corpus shrinks by one. The plan continues.
- **If they cannot be reconciled on the FME workbook specifically:** P2's denominator is unfounded and the
  whole plan halts at barrier 1 until one reader is proven right by a **third, offline, digest-pinned
  reader** — which is LibreOffice, offline only, and whose own measured defect (53 where 35 + 19 = 54)
  must be carried in the adjudication record.
- **If the competence matrix cannot be written honestly** — if every inconvenient disagreement ends up in
  the blind set — the agreement check is decorative and must be **published as decorative**: the
  extraction manifest still ships, `NOT_RUN(not_run.extractor_disagreement)` still exists as a state, and
  the product loses the claim that its ingest is cross-checked. That is a real loss and it is survivable.
  What is not survivable is keeping the claim without the check.

---

# P2 — L1: SCHEMA INDUCTION, THE FIELD SURFACE, STABLE KEYS

**Effort: 10 engineer-days** · B1 3.5 · B2 3.0 · B3 2.5 · B4 1.0

## P2 · What it settles

**The denominator every subsequent number is a fraction of — for all nine workbooks, computed twice by two
independent code paths, and for the two workbooks where it is not derivable, the `null` that says so.**

This is **barrier 1**: no fraction may be computed anywhere in the programme before this phase completes.
The failure this phase exists to prevent was committed twice in one afternoon by the person who knew about
it — once by sampling mutation sites only from cells the predicates already read, once by computing 99.2%
settled from a denominator built out of the numerator.

And, from §0.2 N2, a question no earlier document asked: **which of this phase's defects are visible in its
own headline number?** The answer is: not the most important one. Scope truncation by hidden sheet leaves
the FME field surface at exactly 3,747.

## P2 · Entry criteria

| Requires | Why the edge is real |
|---|---|
| **P1 complete**, agreement matrix published | The induction reads what the readers agreed on. Inducing from a single reader reintroduces the exact defect: 35 of 54, AML-CFT 0 where it is 5 |
| **P1-B3's `StyleTable`** exposing `cellXfs`, `cellStyleXfs`, `applyProtection` and `xfId` per style id | §0.2 N4: 322 of 434 FME styles carry no `<protection>` child; the resolution order is the whole ball game |
| **`docs/PROTECTION-RESOLUTION.md` written before either path is coded** | Two implementations of an unwritten rule are two guesses (methodology §7.5) |

## P2 · Builds

---

### BUILD P2-B1 — INDUCTION FROM THE BLANK TEMPLATE, PINNED BY HASH · 3.5 days

**What it produces.** `TemplateSchema` — every sheet including hidden, every validation including `x14`,
every shared formula materialised, every merged range, every defined name including the four `#REF!`, the
protection state per sheet, and the 15 vocabularies from the hidden `Dropdown` sheet.

#### Files created

```
src/cdfc/schema/induce.py            induce(RawWorkbook, RawWorkbookB) -> TemplateSchema
src/cdfc/schema/vocabularies.py      resolution of the 22 list validations  (§0.2 N7)
src/cdfc/schema/manifest.py          InductionManifest  (R2)
db/schema.sql                        + template, template_sheet, field, vocabulary, validation, carry_edge
tests/unit/test_induce.py  tests/unit/test_vocabularies.py
tests/golden/test_schema_constants.py     (extended)
tests/negative/test_nc_schema.py          NC-D01, NC-D06
```

#### Public interface

```python
@dataclass(frozen=True)
class Vocabulary:
    key: str                       # e.g. "vocab.scheme_type"
    source_ref: str                # "Dropdown!$F$3:$F$11" — ALWAYS on the pinned blank
    terms: tuple[str, ...]
    wired_by_validation: bool      # §0.2 N8: 13 of 15 wired on FME
    resolution: Literal["RANGE", "DEFINED_NAME", "FILING_CONDITIONAL"]
    condition_ref: str | None      # e.g. "'8. Compliance Status'!C5" for the two IF(...) validations

@dataclass(frozen=True)
class TemplateSchema:
    template_sha256: str
    label: str
    sheets: tuple[SheetSpec, ...]           # incl. state='hidden' and protected: bool
    fields: Mapping[str, Field]             # stable_key -> Field
    vocabularies: Mapping[str, Vocabulary]
    validations: tuple[ValidationRecord, ...]
    carry_edges: tuple[CarryEdge, ...]      # src_ref, dst_ref, formula_text, encoding
    field_surface: tuple[str, ...] | None   # None iff no protection mask  (P2-B2)
    defined_names: tuple[DefinedName, ...]
    manifest: InductionManifest

def induce(a: RawWorkbook, a_prime: RawWorkbookB) -> TemplateSchema: ...
```

**The rule that has its own test because it is the one an implementer will get wrong:**

```python
# vocabularies ALWAYS resolve against the pinned blank template, NEVER against a filed artifact.
# 'Dropdown' is hidden AND the only unprotected sheet, and sheetProtection is an application flag
# anyway: assume the filed artifact is fully mutable.
```

#### Data produced

One `template` row, ten `template_sheet` rows, the `vocabulary` rows with `wired_by_validation`, the
`validation` rows with `resolution`, and `carry_edge` rows (**195 cross-sheet of 294 authored**).

#### Functionality validation

**Unit.**
`test_induce__hidden_sheet_present` — `Dropdown`, `state='hidden'`, `protected=False`.
`test_induce__fifteen_vocabularies` — 15 keys, each non-empty; census `{wired: 13, unwired: 2}` with the
unwired named as `Dropdown!L` and `Dropdown!R` (§0.2 N8).
`test_vocabularies__resolution_rule` — table-driven over all 22 list validations, asserting
`{RANGE: 19, DEFINED_NAME: 1, FILING_CONDITIONAL: 2}` and `resolving == 20` under the N7 rule, with
`condition_ref == "'8. Compliance Status'!C5"` on both conditional ones.
`test_induce__defined_names_ref_errors` — 12 names, 4 with `is_ref_error=True`, named.
`test_induce__protection_state_per_sheet` — 9 protected, `Dropdown` alone unprotected.

**Property.** *Invariant:* every `carry_edge` destination is a formula cell and every source resolves to a
cell that exists in the induced schema. Generator: all 294 authored expressions across the nine workbooks
(1,495 formula cells total). `tests/property/test_prop_induce.py::test_prop__carry_edges_are_closed`.

**Golden.**
`tests/golden/test_schema_constants.py::test_golden__schema_constants__fme` pins
**505 / 294 / 211 / 54 / 22 / 20 / 252 / 3747** — properties of the published file, where a change is a
parser regression, full stop (spec G8). Paired **value** assertions (R-GOLD-2): `'3. Portfolio'!O4` text,
`Dropdown!$F$3:$F$11` term list, `'1. Introduction'!D18` verbatim.
`::test_golden__vocabulary_wiring__fme` — 13 wired, 2 unwired, named.
*Which workbook and why:* FME is the only one with all five features live at once — hidden sheet, `x14`
validations, shared formulas, protection mask, cross-sheet carries.

**Negative controls.**
- **NC-D01** (existing) — scope truncation drops the hidden sheet. Injector
  `injectors/induce_visible_only.py`. **And the guard must be the value assertion, not the count:**
  `test_nc__D01a_hidden_sheet_in_schema` asserts `Dropdown` present with 15 non-empty vocabularies;
  `test_nc__D01b_empty_vocabulary_is_never_a_pass` forces a vocabulary to `[]` and asserts the membership
  predicate binds zero cells ⇒ `ERROR(error.cells_bound_zero)` ⇒ run `INVALID`;
  `test_nc__D01c_vocabulary_resolves_from_the_blank` (injector `injectors/vocab_from_filing.py`).
  **New sub-assertion required by §0.2 N2:**
  `test_nc__D01d_the_denominator_does_not_detect_this` — under `induce_visible_only` the FME field
  surface is **still 3,747**, and the test asserts that fact, so that nobody later cites the denominator
  golden as this control's guard. *A test that documents a limit is worth more than a test that hides it.*
- **NC-D06 (new)** — *a filing-conditional vocabulary is treated as a static one.* (§0.2 N7.)

  ```yaml
  - id: NC-D06
    component: schema
    break: "a list validation whose formula1 is IF(C5=\"No\",Choicelist,YesNolist) is resolved to one of
            its branches and treated as a static vocabulary"
    measured_instance: "'8. Compliance Status'!C10 and !C11 on the FME workbook — 2 of the 22 list
                        validations (MEASURED, plan/02 §0.2 N7)"
    injector: vocab_take_first_branch
    why_impossible: null
    guard_tests:
      - tests/negative/test_nc_schema.py::test_nc__D06_conditional_vocab_is_not_static
      - tests/unit/test_vocabularies.py::test_vocabularies__resolution_rule
    positive_control: tests/unit/test_vocabularies.py::test_vocabularies__nineteen_ranges_resolve
    status: ACTIVE
  ```

  The guard asserts that a membership predicate over `C10` carries `applicable` gated on
  `'8. Compliance Status'!C5` and returns `OUT_OF_SCOPE(out_of_scope.not_applicable)` with a pointer to
  `C5` when the condition is unmet — **never a pass against whichever list was picked.**

**Performance.** `PERF-L1` — `induce` on FME, cold: baseline **28–44 ms**; warn above 60 ms, fail above
90 ms.

**Effort: 3.5 days.**

---

### BUILD P2-B2 — THE UNLOCKED-CELL MASK AND THE FIELD SURFACE, COMPUTED TWICE · 3.0 days

**What it produces.** The denominator. Twice. By two implementations that do not share a module.

#### Files created

```
docs/PROTECTION-RESOLUTION.md        WRITTEN FIRST. The resolution order, with the §0.2 N4 census
src/cdfc/schema/styles_mask.py       PATH A: styles.xml cellXfs -> protection@locked, xfId inheritance
src/cdfc/schema/styles_mask_b.py     PATH B: per-sheet <sheetProtection> + per-cell @s resolved by a
                                     SEPARATELY WRITTEN style resolver over reader A' 's StyleTable
tests/differential/test_diff__mask_a_vs_mask_b.py                      (D2)
tests/negative/test_nc_schema.py     NC-D02 (a,b,c,d), NC-D03 (a,b,c), NC-D05
tests/golden/test_field_surface.py
docs/measurements/P2-field-surface.md
```

**`docs/PROTECTION-RESOLUTION.md`, the rule both paths implement** (derived from ECMA-376 and from §0.2 N4,
and written before either path is coded so that the two are implementations of a rule rather than two
guesses):

```
1. A cell's style id s = <c @s>, defaulting to 0.
2. cellXfs[s] is the cell format.  If it carries <protection @locked>, that value wins.
3. If cellXfs[s] carries NO <protection> child, the locked bit is inherited from
   cellStyleXfs[cellXfs[s].@xfId], and if that also declares nothing, the OOXML default locked="1".
4. @applyProtection is a rendering hint. It is NOT a precondition for honouring an explicit
   locked="0".  (FME: 112 cellXfs carry applyProtection="1"; 105 carry locked="0"; the sets differ.)
5. A cell is IN THE FIELD SURFACE iff (locked resolves to false) AND (the cell has no <f> child).
6. If NO sheet in the workbook carries <sheetProtection>, the mask is NOT DERIVABLE:
   field_surface = None, denominator.source = "not derivable — template ships no protection mask".
   This is checked BEFORE step 5, so a stray unlocked style id cannot manufacture a small answer.
MEASURED on FME: 105 explicit-unlocked, 7 explicit-locked, 322 inheriting-locked style ids of 434.
An "absence means unlocked" reading adds 2,502 cells and returns 6,249.

7. THE THREE LAWFUL READINGS, and the field surface each returns on FME. This table is part of the
   document, and `generator_rule` names the row that produced the number:

   | rule id | Reading | FME field surface | Status |
   |---------|---------------------------------------------------------|-------|------------------|
   | v3      | rules 1-6 above (inheritance -> locked; formula cells out)| 3,747 | ADOPTED           |
   | v3-uw   | as v3 but WITHOUT excluding the 8 unlocked formula cells | 3,755 | lawful, not adopted|
   | v3-abs  | absence of <protection> read as UNLOCKED                 | 6,249 | lawful reading of the same XML, REJECTED by NC-D05 |

   All three are readings a competent engineer produces from ECMA-376. NOTHING IN P2 CAN FALSIFY THE
   CHOICE: the rule is written by us, both paths implement it, and NC-D02c/d prove only that the paths
   are two implementations rather than one called twice. The external falsifier is at P8 (see below).
```

**Every surface that prints a settled fraction prints `denominator.generator_rule` beside it**, resolving
to a row of that table — `test_contract__fraction_renders_its_generator_rule` (P5-B4 owns the field;
P14 owns the render). A denominator whose defining rule is not on the page is a denominator the reader
cannot check, and every fraction this product will ever print is a fraction of this one number.

> #### **The denominator ships at P2 as `PROVISIONAL-UNVALIDATED`, and P8-B1 is the phase that closes it**
>
> **This is a hidden dependency and it is named here rather than discovered later.** The 3,747 mask is
> built on day ~22 and **nothing in P2, P3, P4, P5, P6 or P7 can falsify it.** The first artifact that can
> arrives at P8-B1: **≥ 30 workbooks filled by a competent person who has never seen the predicate set**,
> whose `corpus/MANIFEST.json` already records `cells_left_blank[]` per workbook. *The set of cells Person A
> actually wrote into is a direct, cheap, independent measurement of "the cells a filer may fill" — which
> is exactly what the mask is a proxy for.* The plan buys this data and never uses it for this purpose.
>
> **`FieldSurface.validation_state: Literal["PROVISIONAL-UNVALIDATED", "EXTERNALLY-CHECKED"]`** is a field
> of the object from P2, initialised `PROVISIONAL-UNVALIDATED`, carried into
> `SettledFraction.denominator`, and **rendered on every surface that prints the fraction** until P8
> flips it. `test_contract__denominator_declares_its_validation_state` asserts the field is present and
> that no render path drops it.
>
> **The test that closes it, specified here because its subject is built here:**
> **`tests/e2e/test_mask_matches_what_a_competent_filler_filled`** — over the blind-fill corpus, for every
> workbook, compute the set of cells Person A wrote (from the filed artifact against the pinned blank, by
> raw-zip diff, **not** from `cells_left_blank[]`, which is the filler's own self-report and is the weaker
> instrument). Publish **two integers, both against denominator 3,747, warrant MEASURED**:
>
> - **`cells_written_outside_the_mask`** — the mask is **too small**. *This is the dangerous direction*: a
>   cell a filer may fill that is not in the denominator makes every settled fraction an **overstatement**
>   of coverage, and it is invisible to every other instrument in the plan.
> - **`mask_cells_no_filler_ever_wrote`** — the mask is **too large**: the fraction understates coverage.
>   Reported with `n` filers beside it, because a cell nobody happened to fill is not a cell nobody may
>   fill, and this integer decays as the corpus grows.
>
> **Pre-registered threshold, chosen now rather than after the result:** `cells_written_outside_the_mask == 0`
> flips `validation_state` to `EXTERNALLY-CHECKED`. **Any non-zero value is a finding**, published in
> `docs/measurements/P2-field-surface.md` with the cells named, the denominator restated as
> `3,747 + k (external)`, and `denominator.generator_rule` moved to a new row of the table above with its
> date — never a silent correction. *Alternative this beat:* a tolerance ("fewer than 10 cells is
> acceptable") — rejected, because the quantity being estimated is a **set**, and a tolerance on a set
> membership error is a licence to be wrong in the direction that flatters us.
>
> Catalogue entry **NC-D08** (§X). It costs one script over data the corpus lane already produces, and it
> is the only instrument in the entire plan that could falsify the number under every other number.

#### Public interface

```python
# src/cdfc/schema/styles_mask.py      -- PATH A
def field_surface(schema_input: MaskInputA) -> FieldSurface: ...
# src/cdfc/schema/styles_mask_b.py    -- PATH B, independently written
def field_surface_b(schema_input: MaskInputB) -> FieldSurface: ...

@dataclass(frozen=True)
class FieldSurface:
    cells: tuple[str, ...] | None       # None iff not derivable
    total: int | None
    per_sheet: Mapping[str, int]
    source: str                         # "induced-from-template-unlocked-mask"
                                        # | "not derivable — template ships no protection mask"
    generator_rule: str                 # "v3" -- resolves to a ROW of PROTECTION-RESOLUTION.md's table
    validation_state: Literal["PROVISIONAL-UNVALIDATED", "EXTERNALLY-CHECKED"]
                                        # PROVISIONAL from P2 until P8-B1's filler check flips it.
                                        # Rendered wherever the fraction renders. Never defaulted away.

def agree_or_invalid(a: FieldSurface, b: FieldSurface) -> FieldSurface:
    """Disagreement -> InvalidRun(InvalidCause.DENOMINATOR_DISAGREEMENT). Never a preference."""
```

**The named invariant, and it is guarded structurally:** *the denominator derives from the unlocked mask,
never from the predicate set.* `field_surface`'s import closure must not reach `cdfc.predicates` or
`cdfc.qualify`.

#### Data produced

`docs/measurements/P2-field-surface.md` — **all nine rows**, including the two `null` ones, with
`computedTwiceAgreed` per workbook. **This is P2's number.**

#### Functionality validation

**Unit.**
`test_styles_mask__inheritance_default_is_locked` — a synthetic style with no `<protection>` and an
`xfId` pointing at a `cellStyleXf` with none resolves to locked. **The single most important unit test in
this build**, because §0.2 N4 says 322 of 434 real style ids take this path.
`test_styles_mask__apply_protection_is_not_a_precondition` — an explicit `locked="0"` without
`applyProtection` is unlocked.
`test_styles_mask__formula_cells_are_excluded` — 3,755 unlocked in used ranges, 3,747 after excluding the
8 unlocked formula cells.
`test_styles_mask__no_protection_anywhere_yields_none` — `Draft_ACAC_Format` (0 of 13 protected, 0
unlocked ids) and `IFSCA_Annual_Reporting_Format` (0 of 9 protected, **1** unlocked id) both return
`None`, **not 0 and not 8**.

**Property.** *Invariant:* `field_surface(w) ⊆ unlocked(w)` and
`|field_surface(w)| + |unlocked ∧ formula| == |unlocked(w)|` for every workbook that has a mask.
Generator: the nine workbooks plus 200 synthetic style tables produced by
`tools/fixtures/make_style_table.py` varying `{explicit locked, explicit unlocked, absent, xfId depth,
applyProtection}`. `tests/property/test_prop_mask.py::test_prop__mask_partitions_the_unlocked_set`.

**Golden.** `tests/golden/test_field_surface.py::test_golden__field_surface__fme` — **3,747** with the
exact per-sheet split, **plus** the value assertion that `'3. Portfolio'!C4` is *in* the surface and
`'3. Portfolio'!O4` (a formula) is *not* (R-GOLD-2).
`::test_golden__field_surface__all_nine` — `{FME: 3747, CMI: 2255, ALR: 1599, AL_monthly: 3537,
Draft_ACAC: None, IBU: 459, ITFS: 481, EDR_1: 162, IFSCA_Annual: None}`.
`::test_golden__no_protection_mask_yields_null` on `IFSCA_Annual_Reporting_Format` and
`Draft_ACAC_Format` — *which workbooks and why:* the only two with no mask, and the former produces a
plausible **8**, which is the shape of a small answer rather than of no answer.

**Differential — D2.** `tests/differential/test_diff__mask_a_vs_mask_b.py` — the two paths agree on every
workbook that has a mask, and both return `None` on the two that do not. Disagreement ⇒
`invalid.denominator_disagreement`.

**Negative controls.**
- **NC-D02a** (existing) — `test_nc__D02a_denominator_provenance`: a structural assertion that
  `settledFraction.denominator` is produced by `schema/styles_mask.py::field_surface()` and that its
  import closure **does not reach `cdfc.predicates`**. Injector
  `injectors/denominator_from_predicates.py` — the 99.2% bug, verbatim.
- **NC-D02b** — `injectors/denominator_offbyone.py` ⇒ `INVALID(invalid.denominator_disagreement)`.
- **NC-D02c** — the import closures of the two paths share no `cdfc` module except
  `cdfc.ingest.reader_lxml` (declared), and the declaration is itself an assertion so widening it is a
  visible diff.
- **NC-D02d** — **registry row 14, and the strongest single test in the methodology.**
  `test_nc__D02d_mutating_path_A_moves_only_path_A`: mutate the shared reader's unlocked-mask extraction;
  assert path A's number changes and path B's does not. Structural independence can be satisfied by two
  copies of the same mistake; this cannot be satisfied by a shared dependency at all.
- **NC-D03a/b/c** (existing) — `settledFraction is None`, the source string exact, **no digit renders
  anywhere in the settled-fraction block** (regex over the rendered fragment), `null` is distinct from
  `0` in the API, and the admission-side twin on FME returns 3,747 so the guard is not simply refusing
  everything. Injector `injectors/mask_unconditional.py`.
- **NC-D05 (new)** — *absence of `<protection>` is read as unlocked.* (§0.2 N4.)

  ```yaml
  - id: NC-D05
    component: schema
    break: "a cellXf with no <protection> child is treated as unlocked instead of inheriting locked=1"
    measured_instance: "FME: 322 of 434 cellXfs carry no <protection> child; the misreading adds 2,502
                        non-formula cells and returns a field surface of 6,249 instead of 3,747
                        (MEASURED, plan/02 §0.2 N4)"
    injector: mask_absent_is_unlocked
    why_impossible: null
    guard_tests:
      - tests/negative/test_nc_schema.py::test_nc__D05_absent_protection_inherits_locked
      - tests/golden/test_field_surface.py::test_golden__field_surface__fme
    positive_control: tests/unit/test_styles_mask.py::test_styles_mask__explicit_unlocked_is_unlocked
    status: ACTIVE
  ```

  The guard asserts the injected path returns **6,249**, that D2 escalates to
  `invalid.denominator_disagreement`, and that the run does **not** publish a fraction.
- **NC-D08 (new)** — *the mask is never checked against anything outside this repository.*

  ```yaml
  - id: NC-D08
    component: schema
    break: "the unlocked-cell mask is validated only by two code paths agreeing on one rule WE wrote,
            and no artifact in the plan can falsify it, though the plan buys the artifact that could"
    measured_instance: "not yet realised — three lawful readings of the same styles.xml return 3,747 /
                        3,755 / 6,249 (MEASURED, plan/02 §0.2 N4), and every fraction the product prints
                        is a fraction of whichever one we picked"
    injector: mask_drops_a_sheet
    why_impossible: null
    guard_tests:
      - path: tests/e2e/test_mask_matches_what_a_competent_filler_filled.py::test_mask__no_filler_wrote_outside_the_mask
        flips: true
      - path: tests/golden/test_field_surface.py::test_golden__field_surface__fme
        flips: true
    positive_control: tests/e2e/test_mask_matches_what_a_competent_filler_filled.py::test_mask__the_real_mask_covers_every_written_cell
    status: PENDING_CORPUS        # ACTIVE from P8-B1; PROVISIONAL in the sweep until then
  ```

  `injectors/mask_drops_a_sheet.py` removes `'4. Investors'` (897 cells) from the mask; the guard asserts
  that Person A's writes on that sheet appear in `cells_written_outside_the_mask` and that the count is
  non-zero. **Until the corpus exists the entry is `PENDING_CORPUS` and the sweep counts it in
  `provisional_count`, never in `entries_caught`** — the same rule NC-Q02 gets, for the same reason.

**Determinism.** `test_det__field_surface_is_sorted` — `FieldSurface.cells` is sorted by
`(sheet_index, row, column)` explicitly, never by set iteration order.

**Effort: 3.0 days.**

---

### BUILD P2-B3 — STABLE KEYS AND THE RESOLUTION STATE · 2.5 days

**What it produces.** A key that survives a row insertion, or refuses to.

#### Files created

```
src/cdfc/schema/stable_keys.py
tools/fixtures/make_row_insertion.py     raw-zip surgery, never openpyxl
fixtures/synthetic/row-inserted__portfolio-r7.xlsx
tests/unit/test_stable_keys.py  tests/property/test_prop_stable_keys.py
tests/negative/test_nc_schema.py         NC-D04
```

#### Public interface

```python
@dataclass(frozen=True)
class StableKey:
    sheet_name: str
    merged_header_path: tuple[str, ...]     # from the 252 merged ranges
    row_label: str
    row_ordinal: int                        # THE disambiguator — arithmetic, not a prediction
    def __str__(self) -> str: ...           # "portfolio.tbl31.row[7].total_value"

@dataclass(frozen=True)
class Field:
    stable_key: str
    resolved_ref: str | None                # coordinates are a RESOLVED ATTRIBUTE, never the identity
    resolution_state: Literal["RESOLVED", "UNRESOLVED"]
    dtype: Literal["MILLI_USD_MILLION", "COUNT", "DATE", "TEXT", "ENUM"]
    is_unlocked: bool; is_formula: bool; in_field_surface: bool

def build_keys(schema: TemplateSchema) -> Mapping[str, Field]: ...
def resolve(key: StableKey, schema: TemplateSchema) -> Field:
    """UNRESOLVED BLOCKS its predicates. It never degrades to a guess."""
```

**The measured justification, restated so it is not lost:** under a naive
`(sheet, label-above, label-left)` key, **1,749 of 1,953 cells are ambiguous (89.6%)** because 100-row
tables repeat the label pair. The row ordinal disambiguates completely.

#### Functionality validation

**Unit.** `test_stable_keys__row_ordinal_disambiguates` — over `'3. Portfolio'`'s 100-row tables, 0
collisions with the ordinal and 1,749 without it.
`test_stable_keys__unresolved_blocks` — an `UNRESOLVED` key raises when a predicate attempts to bind it.

**Property.** *Invariant:* for any row insertion, every stable key resolves to the **correct** new
reference **or** to `UNRESOLVED` — never to a different label pair. Generator: row insertions at every row
of every FME table, produced by raw-zip surgery.
`tests/property/test_prop_stable_keys.py::test_prop__stable_key_resolution`.

**Golden.** `tests/golden/test_stable_keys.py::test_golden__key_set_is_stable__fme` — the sorted key set's
`sha256` is pinned, plus the value assertion that
`'3. Portfolio'!O7 → "portfolio.tbl31.row[7].total_value"`. *Which workbook and why:* FME, whose 252
merged ranges make the `merged_header_path` non-trivial.

**Negative control — NC-D04** (existing). Injector `injectors/keys_coordinate.py`.
`test_nc__D04a_row_insertion_does_not_rebind` on `fixtures/synthetic/row-inserted__portfolio-r7.xlsx`;
`test_nc__D04b_unresolved_blocks`. **Admission-side twin:**
`test_nc__D04c_unchanged_workbook_resolves_everything` — on the untouched FME blank, 0 keys are
`UNRESOLVED`, so the guard is not simply refusing to resolve.

**Effort: 2.5 days.**

---

### BUILD P2-B4 — THE STRUCTURAL FINGERPRINT · 1.0 day

**What it produces.** The value that binds a filing to a template version — and **deliberately excludes
formula content**.

#### Files created

```
src/cdfc/schema/fingerprint.py
tests/unit/test_fingerprint.py
tests/negative/test_nc_schema.py     NC-D07
fixtures/synthetic/formula-overwritten__portfolio-O7.xlsx    (built here, used by P9-B1)
```

#### Public interface

```python
def structural_fingerprint(schema: TemplateSchema) -> str:
    """sha256 over canonical_json of
       (sheet names + states, per-sheet dimension, merged-range set, defined-name list, unlocked mask).
       FORMULA CONTENT IS DELIBERATELY EXCLUDED."""
```

**Why the exclusion is load-bearing:** a filer who overwrote a formula cell with a literal must fail a
**predicate** (`TEMPLATE_DIFF`, predicate #1), not the **binding**. If formula content entered the
fingerprint, the flagship check's target would fail to bind and would be reported as
`invalid.template_unbound` — an apparatus failure — instead of as a finding about the filing.

#### Functionality validation

**Unit.** `test_fingerprint__is_stable_under_value_edits` — write values into 50 field-surface cells by
raw-zip surgery; the fingerprint is unchanged.
`test_fingerprint__moves_on_a_renamed_sheet`, `::on_an_added_merged_range`, `::on_a_changed_unlocked_mask`.

**Negative control — NC-D07 (new).**

```yaml
- id: NC-D07
  component: schema
  break: "formula content is included in the structural fingerprint"
  measured_instance: "not yet realised — but it would convert the design's flagship check
                      (TEMPLATE_DIFF, a formula cell overwritten with a literal) from a FINDING about
                      the filing into invalid.template_unbound, an apparatus failure about us"
  injector: fingerprint_includes_formulas
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_schema.py::test_nc__D07_overwritten_formula_still_binds
  positive_control: tests/unit/test_fingerprint.py::test_fingerprint__moves_on_a_renamed_sheet
  status: ACTIVE
```

The guard uses `fixtures/synthetic/formula-overwritten__portfolio-O7.xlsx` — the FME blank with `O7`'s
`<f>` removed and a literal `<v>` left behind, by raw-zip surgery — and asserts the fingerprint still
matches the template, so the run proceeds to the predicate that must catch it.

**Effort: 1.0 day.**

---

## P2 · The measurement this phase produces

> **The field surface for all nine workbooks, each computed twice by independent code paths, with
> `computedTwiceAgreed` per workbook and the count of templates for which no mask is derivable.**
> Denominator: **9 workbooks**. Warrant **MEASURED**.
>
> ```
> FME 3747 · CMI 2255 · ALR 1599 · AL_monthly 3537 · IBU 459 · ITFS 481 · EDR_1 162
> Draft_ACAC null · IFSCA_Annual null            -> 2 of 9 not derivable
> ```

Today exactly one of the nine is measured *and none is measured twice*. The spec asserts that two of the
nine ship no mask; **P2 converts that assertion into a measurement**, and the naive-count trap on
`IFSCA_Annual_Reporting_Format` — 1 unlocked style id, a plausible-looking field surface of **8** — is the
reason the assertion was not good enough.

Secondary and new: the **vocabulary wiring census** (13 wired, 2 unwired on FME) and the **validation
resolution census** (19 RANGE, 1 DEFINED_NAME, 2 FILING_CONDITIONAL — the reconciliation of the pinned
`20`).

## P2 · Exit gate — this is barrier 1 and gate G-DENOM

**TRUE iff all of:**

1. `test_schema_constants` green: **505 / 294 / 211 / 54 / 22 / 20 / 252 / 3747**, each count paired with
   at least one value assertion (R-GOLD-2, `ci/golden-asserts-values.sh`).
2. The field surface is computed twice and agrees on **every workbook that has a mask**; the two that do
   not return `None` from both paths.
3. The parse round-trip reproduces all 505 formula cells, all 54 validations, all 252 merged ranges, the
   hidden sheet and its 15 vocabularies.
4. `test_nc__D02a` green — the import closure of `field_surface` does not reach `cdfc.predicates`.
5. **`test_nc__D02d` observed red under `injectors/denominator_single_path.py`** — registry row 14 moves
   from `PENDING` to `LIVE` and `docs/GATE-LIVENESS.md` records the assertion line.
6. `test_nc__D01d` green — the phase states, in a test, that its own headline number does not detect
   NC-D01.
7. `docs/measurements/P2-field-surface.md` published with all nine rows **including the two `null` ones**,
   **and** `docs/PROTECTION-RESOLUTION.md` carrying the three-lawful-readings table (3,747 / 3,755 / 6,249)
   with the adopted row named.
8. **Every field surface carries `validation_state = "PROVISIONAL-UNVALIDATED"` and every surface that
   renders a fraction renders it**, plus `denominator.generator_rule`.
   `test_contract__denominator_declares_its_validation_state` and
   `test_contract__fraction_renders_its_generator_rule` green. **NC-D08 is in the catalogue as
   `PENDING_CORPUS` with the phase that activates it named (P8-B1).** *P2 does not claim the denominator is
   right; it claims two paths agree on a written rule, and it says so in the artifact.*

**Mutation score.** `schema/styles_mask*.py` is **Tier V** (`K/V ≥ 0.90`), blocking from this phase.
`schema/` (rest) is Tier I (`≥ 0.80`), blocking from P3. Reported with `I`, `T` (ids listed), `E` and its
published arguments.

## P2 · What it kills if it fails

- **If the mask is not recoverable for a workbook:** that workbook has **no settled fraction, ever** —
  `settledFraction: null`, `denominator.source` stating why, published as such. Two of the nine are already
  in this state and the product ships with them in it.
- **If it is not recoverable for the FME workbook:** the headline triple **2,373 / 1,374 / 3,747** is
  withdrawn and the product's primary claim becomes *a count of failures with no denominator* — strictly
  smaller, still honest, still shippable, and the settled fraction disappears from every surface rather
  than appearing with a guessed denominator.
- **If the two paths cannot be made independent** — if NC-D02d cannot be made to pass — then the
  denominator is computed once, `computedTwiceAgreed` is `false` on every row, and the report says so in
  the `scope.denominator` object. The claim that the denominator is cross-checked is withdrawn. **It is
  withdrawn in the artifact, not in a footnote**, because a withdrawn claim that only appears in a README
  is a claim that is still being made.

---

# P3 — THE TWO EVALUATION SUBSTRATES: FACT MODEL AND FORMULA EVALUATOR

**Effort: 17 engineer-days** (revised from `00` §7's 12 — see R11) · B1 2.0 · B2 1.5 · B3 1.5 · **B4 12.0**
· plus **1.5 person-days of a second author** for arm 2's expectation file, not added to this total

## P3 · What it settles

**Whether our recalculation reproduces the regulator's own cached values — and, after §0.2 N1, whether
that question as originally posed can be answered wrongly.**

This is experiment **E11** and **barrier 2**. Everything downstream depends on it: no observability filter
without the evaluator, therefore no `O`, therefore no `K/O`, therefore gate G2 measures *reach* rather than
*quality*; and `TEMPLATE_DIFF` — predicate #1, the only thing in the design that detects a formula cell
overwritten with a literal — is unbuildable without it.

**And the question this phase must now also settle, which no earlier document asked: how much information
is in the positive control?** §0.2 N1 measured the answer for the blank template: **none.** All 505 cached
values are 301 zeros and 204 copies of `"NA"`. The phase therefore produces two numbers with two
denominators, and it says which is which.

## P3 · Entry criteria

| Requires | Why the edge is real |
|---|---|
| **P2 complete**, field surface published, gate G-DENOM passed | The fact table's keys and the evaluator's cell graph are both projections of the induced schema |
| **P2-B3's `StableKey`** frozen for the FME template | A fact table keyed on coordinates silently rebinds on a row insertion |
| **P2-B1's `carry_edges`** — 195 cross-sheet of 294 authored | The topological sort is over that graph |
| **R4 decided** — `calc/` in the float scan set | The evaluator is written in `Decimal` from its first line, not converted later |

## P3 · Builds

---

### BUILD P3-B1 — THE TWO-DOCUMENT FACT MODEL · 2.0 days

**What it produces.** Exactly two bound names, `filing` and `template`, over which every predicate in the
system will be written.

#### Files created

```
src/cdfc/facts/fact_table.py
tests/unit/test_fact_table.py  tests/property/test_prop_fact_table.py
tests/negative/test_nc_evaluate.py      NC-E10 (new)
```

#### Public interface

```python
@dataclass(frozen=True)
class Leaf:
    value: int | str | date | bool | None
    unit: Literal["MILLI_USD_MILLION", "COUNT", "DATE", "TEXT", "ENUM"]
    cell: str                       # __cell__ — EVERY leaf carries it, no exceptions
    anchor: Anchor                  # P3-B3
    warrant: Literal["DETERMINISTIC", "MODEL_EXTRACTED", "DERIVED"]

@dataclass(frozen=True)
class FactTable:
    filing: Mapping[str, Any]       # nested, leaves are Leaf
    template: Mapping[str, Any]     # vocabularies and template constants — ALWAYS from the pinned blank
    def keys(self) -> frozenset[str]: ...          # exactly the induced stable-key set

def build(schema: TemplateSchema, filing: RawWorkbook, *, template_blob: Path) -> FactTable: ...
```

**Hard constraints, each with a test:** no clock, no network, no filesystem below `build`; `template` is
resolved from the pinned blank digest and never from the filing; every leaf carries `__cell__`; money is
scaled to `MILLI_USD_MILLION` here, **once**.

#### Functionality validation

**Unit.** `test_fact_table__two_names_only` — `set(ft.__dataclass_fields__) == {"filing","template"}`.
`test_fact_table__every_leaf_carries_a_cell` — over all 3,747 FME field-surface cells.
`test_fact_table__template_comes_from_the_blank` — build against a filing whose `Dropdown` sheet has been
edited by raw-zip surgery; assert `ft.template` is unchanged. **`Dropdown` is hidden *and* the only
unprotected sheet**, so a predicate resolving its vocabulary from the filing validates the filer's data
against a list the filer can edit.

**Property.** *Invariant:* `ft.keys() == schema.fields.keys()` for every workbook that has a mask.
Generator: the seven masked workbooks × 50 raw-zip value edits each.
`tests/property/test_prop_fact_table.py::test_prop__key_set_equals_the_schema`.

**Negative control — NC-E10 (new).**

```yaml
- id: NC-E10
  component: facts
  break: "a vocabulary or template constant is resolved from the FILED artifact instead of the pinned blank"
  measured_instance: "'Dropdown' is state=hidden AND the only unprotected sheet of the FME workbook
                      (MEASURED); sheetProtection is an application flag, so the filed artifact must be
                      assumed fully mutable"
  injector: template_from_filing
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_evaluate.py::test_nc__E10_template_never_reads_the_filing
    - tests/unit/test_fact_table.py::test_fact_table__template_comes_from_the_blank
  positive_control: tests/unit/test_fact_table.py::test_fact_table__filing_values_do_reach_filing
  status: ACTIVE
```

**Performance.** `PERF-FT` — fact-table build: baseline **1 ms**; warn 3 ms, fail 5 ms.

**Effort: 2.0 days.**

---

### BUILD P3-B2 — UNITS AND TOLERANCE · 1.5 days

**What it produces.** `MILLI_USD_MILLION`, and the rule that counts get none.

#### Files created

```
src/cdfc/facts/units.py
ci/no-float-money.sh                 (extended to calc/ per R4)
tests/unit/test_units.py  tests/property/test_prop_units.py
tests/negative/test_nc_evaluate.py   NC-E07, NC-E08
```

#### Public interface

```python
MILLI_USD_MILLION = "MILLI_USD_MILLION"     # int64 count of 1e-3 USD Million; 1 unit = USD 1,000
HALF_ULP_UNITS = 5                          # guidance C111 fixes 2 dp on USD Million

def to_milli_usd_million(d: Decimal) -> int:
    """12.34 -> 12340.  ROUND_HALF_UP.  The ONLY function that crosses the Decimal->int boundary."""
def tau(n_summands: int) -> int:
    """tau(n) = 5n units.  Raises TypeUnitError if applied to a COUNT-typed quantity."""
def within_tolerance(lhs: int, rhs: int, *, unit: str, n_summands: int) -> bool:
    """COUNT -> exact equality, zero tolerance. A person is not a rounded quantity."""
```

#### Functionality validation

**Unit.** `test_units__twelve_thirty_four` — `Decimal("12.34") -> 12340 -> Decimal("12.34")`.
`test_units__tau_raises_on_counts`. `test_units__round_half_up_not_bankers` — `Decimal("0.005")` rounds up.

**Property.** *Invariant:* the money round-trip is exact for every 2-dp value in the `int64` range.
Generator: `Decimal` with exactly 2 dp over `±(2**63-1)/1000`.
`tests/property/test_prop_units.py::test_prop__money_roundtrip_exact` — the float cast breaks it at
`12.34 → 12.339999999999999`.

**Negative controls.**
- **NC-E07** (existing) — floating-point money. Injector `injectors/float_money.py`;
  `ci/no-float-money.sh`; `test_nc__E07_no_float_in_fact_table` asserts every money-typed fact is
  `isinstance(v, int)`. **Plus NC-E07c (new, R4)** — the scan set covers every arithmetic package,
  enumerated rather than listed.
- **NC-E08** (existing) — tolerance applied to counts. Injector `injectors/tolerance_on_counts.py`; a
  mutant that changes an investor count by 1 must be **killed**. Admission-side twin
  `test_nc__E08b_money_gets_tau` — a mutant inside `τ(n)` on a money cell must **not** fire, so the guard
  is not zero-tolerance everywhere.

**Mutation note.** `facts/units.py` is **Tier V**. The comparison-boundary mutant `abs(d) <= τ → abs(d) < τ`
is high-value and must be killed by a straddle test; if it survives, the
`indeterminate.tolerance_straddle` path is untested (methodology §3.3).

**Effort: 1.5 days.**

---

### BUILD P3-B3 — THE PROVENANCE ANCHOR UNION · 1.5 days

**What it produces.** A locator that survives normalisation and records the encoding that made the
294-versus-505 undercount possible.

#### Files created

```
src/cdfc/facts/anchors.py
tests/unit/test_anchors.py
tests/negative/test_nc_external.py    NC-X03
```

#### Public interface

```python
@dataclass(frozen=True)
class PdfSpan:                      # Docling's ProvenanceItem, VERBATIM
    page_no: int; bbox: BBox; charspan: tuple[int, int]; table_cell: tuple[int, int] | None
@dataclass(frozen=True)
class XlsxCell:
    sheet: str; ref: str
    formula: FormulaEncodingRecord  # encoding in {TEXT, SHARED_MASTER, SHARED_DEPENDENT, ARRAY, NONE}
@dataclass(frozen=True)
class RegisterRecord:
    endpoint: str; snapshot_sha256: str
    raw_value: str                  # BOTH are mandatory
    normalised_value: str
    transformations: tuple[str, ...]  # ("NFKC", "U+2011 -> U+002D", "strip", "casefold") — ORDERED
Anchor = PdfSpan | XlsxCell | RegisterRecord
```

**Why `raw_value` is mandatory:** one live regulated entity's registration number contains
`U+2011 NON-BREAKING HYPHEN` rather than `U+002D` — visually identical, byte-wise different, invisible in
any log or screenshot. **A system that stores only the normalised form has destroyed the evidence that its
own normalisation was load-bearing.**

#### Functionality validation

**Unit.** `test_anchors__xlsx_cell_records_encoding` — over all 505 FME formula cells, the census
`{TEXT: 261, SHARED_MASTER: 32, SHARED_DEPENDENT: 211, ARRAY: 1}`.
`test_anchors__coord_origin_is_explicit` — the `BBox` carries Docling's `coord_origin` enum, not a guess.

**Negative control — NC-X03** (existing). Injector `injectors/store_normalised_only.py`;
`test_nc__X03_raw_and_normalised_both_stored` asserts a `U+2011` record is byte-distinguishable from a
`U+002D` record **after storage**.

**Effort: 1.5 days.**

---

### BUILD P3-B4 — THE FORMULA EVALUATOR, AND THE POSITIVE CONTROL THAT ACTUALLY DISCRIMINATES · 12.0 days

**What it produces.** A topological evaluator over the induced cell graph, and — after §0.2 N1 — a gate
with two arms instead of one.

#### Files created

```
src/cdfc/calc/graph.py         topological sort over carry_edges; cycle -> NOT_RUN, never a guess
src/cdfc/calc/functions.py     the function vocabulary, one function per module-level callable
src/cdfc/calc/operators.py     + - * / ^ & comparison, over Decimal under a pinned context
src/cdfc/calc/errors.py        ExcelError: #DIV/0! #N/A #VALUE! #REF! #NUM! #NAME?
src/cdfc/calc/evaluate.py      recalculate(schema, fact_table) -> ValueGrid
src/cdfc/calc/cached.py        the cached-value reader and the comparison
docs/PROTECTION-RESOLUTION.md  (no change; named here only because calc reads the same StyleTable)
docs/GATE-CHANGES.md           the G-EVAL two-arm entry, dated, with the §0.2 N1 argument
fixtures/synthetic/filled__template-computed__fme-discriminating__<seed>.xlsx
fixtures/synthetic/clean__hand-computed__fme-q1__<sha8>.xlsx   -- derived cells typed by a PERSON,
                                                                 never by calc/. P5's exit gate needs it
tools/fixtures/make_discriminating.py
tools/fixtures/materialise_expected.py
docs/EVALUATION-CONTRACT.md    TEMPLATE vs FILING is a GENERATED SECTION of this file, which is the one
                               place the rule is written (F19; C8b retired docs/RECALCULATION-SOURCE.md)
tests/differential/test_diff__evaluator_vs_cached.py            (D3, arm 1)
tests/differential/test_diff__evaluator_vs_expected.py          (D3', arm 2 — NEW)
tests/differential/test_diff__evaluator_vs_libreoffice.py       (D4, offline, nightly, advisory)
tests/negative/test_nc_evaluate.py     NC-E11, NC-E12 (new)
docs/measurements/P3-evaluator.md
```

#### Public interface

```python
Value = Decimal | str | bool | ExcelError | None
FormulaSource = Literal["TEMPLATE", "FILING"]

@dataclass(frozen=True)
class ValueGrid:
    values: Mapping[tuple[str, str], Value]     # (sheet, ref) -> value
    not_run: Mapping[tuple[str, str], str]      # (sheet, ref) -> reason, e.g. "unimplemented: FOO"
    computed_cells: frozenset[tuple[str, str]]  # cells THIS CALL wrote a value into. See below.
    formula_source: FormulaSource               # which <f> elements were used. Part of the object.

def recalculate(schema: TemplateSchema, facts: FactTable, *,
                formula_source: FormulaSource) -> ValueGrid: ...
    # NO DEFAULT. The caller must state which formulas it means, at every call site.

# calc/functions.py — the vocabulary, and it is NINE, not eight  (§0.2 N5)
SUM  COUNTIF  IF  IFERROR  INDEX  ROW  ROWS  AGGREGATE  SINGLE
#                                            ^ AGGREGATE(15,6,...) only: SMALL, ignore errors
#                                                       ^ _xlfn.SINGLE, implicit intersection (R10)
```

#### **`formula_source` is a required argument, and two phases currently disagree without knowing it**

`recalculate(schema, facts)` as first written takes the **schema**, and the schema is induced from the
**pinned blank**, whose formula content is fixed. Follow that through:

- **P6-B3's observability filter** calls `classify(clean, mutant)` over two recalculated grids and marks a
  mutant `UNOBSERVABLE` when they are identical.
- **An F11 mutant** is *"a cell the pinned blank declares a formula carries a literal"* — the flagship
  fault class, the one `TEMPLATE_DIFF` exists for, the one P9's exit gate names.
- Recalculating that mutant **through the template's formula graph overwrites the literal with the
  formula's value.** The clean grid and the mutant grid come out identical. **The entire F11 population is
  classified `UNOBSERVABLE`, drops out of `O`, and `Campaign.kill_rate()` raises `CampaignArithmeticError`
  on `O == 0` — so `TEMPLATE_DIFF`, predicate #1, cannot be admitted at G2 at all.** Meanwhile P9's exit
  gate is green, because `template_diff` compares the **filed** value against the recomputed one and never
  touches the observability filter. Two phases, two meanings of one verb, both green in isolation, and the
  integration is broken twelve weeks in.

> **Ruling (DECIDED), and it is fixed in one place so there is no second convention to remember.**
> `recalculate` takes `formula_source` **explicitly, with no default**:
> - `formula_source="FILING"` — evaluate the **filing's own `<f>` elements, materialised** (shared
>   dependents row/col-shifted per P1-B3); a cell the filing carries as a literal **stays a literal**.
>   **Observability recalculates with `FILING`.** This is what makes an F11 mutant observable.
> - `formula_source="TEMPLATE"` — evaluate the **pinned blank's** formula for each cell over the filed
>   inputs. **`TEMPLATE_DIFF` recalculates with `TEMPLATE`**, and the difference between the two grids at a
>   cell *is* the finding.
>
> The rule is published in **`docs/EVALUATION-CONTRACT.md`**, which is the **single home of the evaluation
> contract** and therefore the home of `formula_source`, because `formula_source` is a rule of that
> contract. The `formula_source` section is emitted by `EVALUATION-CONTRACT.md`'s **generator**, not
> hand-edited, so P5's byte-identity gate (P5.3 criterion 6) still holds.
>
> *(Arbitration **C8(b)**. This build previously created **`docs/RECALCULATION-SOURCE.md`** as a separate
> artifact with a generated cross-reference from `EVALUATION-CONTRACT.md`. **That file is deleted as a
> separate artifact and is not created by any build.** Two files, one generated from the other, is how the
> contract came to have two versions in the first place — and `00`, `04` and `05` had already written that
> the rule lives in `EVALUATION-CONTRACT.md`. The byte-identity concern that motivated the split is
> answered by generating the section rather than by splitting the file.)*

**The two tests that make the ruling real, and they live here because both grids are built here:**

- `tests/unit/test_calc_source.py::test_calc__filing_source_preserves_an_overwritten_literal` — over
  `fixtures/synthetic/formula-overwritten__portfolio-O7.xlsx` (built at P2-B4), assert
  `recalculate(..., formula_source="FILING").values[("3. Portfolio","O7")]` is the **literal**, and that
  `("3. Portfolio","O7") ∉ computed_cells`.
- `tests/unit/test_calc_source.py::test_calc__template_source_recomputes_it` — the same fixture with
  `formula_source="TEMPLATE"` returns the **formula's** value, and the two grids differ at exactly that
  cell. **Non-empty distinguishing set at the overwritten cell is the precondition for
  `test_f11_mutant_is_observable` at P6 (obligation Y9) and for `test_g2_admits_template_diff` at P7.**

Injector `injectors/observability_uses_template_formulas.py` (catalogue **NC-E14**, §X) flips the
observability call site back to `TEMPLATE` and both tests go red.

#### **`ValueGrid.not_run` is addressable, because `U/G` is otherwise a measurement of our own apparatus**

A cell in `not_run` (unimplemented function, cycle, engine-disagreement exclusion) **is identical in both
grids by construction.** A two-way `OBSERVABLE | UNOBSERVABLE` classification therefore marks every mutant
whose only propagation path runs through such a cell as `UNOBSERVABLE`, removes it from `O`, and — since
`O = G − U` — **raises `K/O`**. The published sentence *"`U/G` for our operator mix"* would then be a
property of **our evaluator's coverage**, not of the fault model, with the error correlated with the
quantity measured, in the direction that flatters us.

This build's obligation is to make the third case *detectable*: `ValueGrid` exposes

```python
def touched_not_run(self, cells: Iterable[tuple[str, str]]) -> frozenset[tuple[str, str]]
    """The subset of `cells` this grid could not compute. Non-empty => the comparison at those
       cells carries no information, and the caller MUST NOT read identity as unobservability."""
```

`tests/contract/test_contract__valuegrid_not_run_is_addressable` asserts the method exists, is total over
the grid's key set, and that `values` and `not_run` are **disjoint** — a cell may not be both computed and
not-run. The three-way classification itself (`OBSERVABLE · UNOBSERVABLE · INDETERMINATE_OBSERVABILITY`)
and the reporting of `I` beside `U/G` belong to P6-B3 and are recorded as obligation **Y9**.

**Semantics that must be implemented and that the blank template cannot exercise** — each is a line item
because each is invisible under §0.2 N1:

| Requirement | Why the blank does not exercise it |
|---|---|
| `COUNTIF` Excel **wildcards** `*`, `?`, `~` | `'1. Introduction'!D18:D20` count over an empty `G54:G63`; every answer is 0 either way (§0.2 N6) |
| Array division producing `#DIV/0!` element-wise, `(ROW(r)-ROW(first)+1)/(cond)` | On the blank, `N54:N63` is empty, every comparison is `FALSE`, every element is `#DIV/0!` |
| `AGGREGATE(15,6,array,k)` = k-th smallest **ignoring error values**; empty result ⇒ `#NUM!` | On the blank the result set is always empty, so only the `#NUM!` branch runs |
| `IFERROR` catching `#NUM!` and returning the string `"NA"` | This is the *only* branch the blank exercises for 204 of 505 cells |
| `_xlfn.SINGLE` implicit intersection at `'1. Introduction'!D92`, the workbook's only array formula | Its value on the blank is `"NA"`, like everything around it |
| Cycle detection over `carry_edges` | The blank has none |

#### **The gate, restructured. This is the build's most important paragraph.**

`plan/00-decomposition.md` pre-registers **G-EVAL** as *"reproduction is exact on 505 of 505 for the FME
workbook."* §0.2 N1 measures that this comparison is satisfied by an evaluator returning `0` and `"NA"`
unconditionally, and that the decomposition's own named negative control for it —
*"an evaluator variant that treats `AGGREGATE(15,6,…)` as plain `SUM`"* — **also produces `"NA"`**, because
`SUM` over an array of `#DIV/0!` is an error and `IFERROR` catches it. The control cannot fail.

**Ruling: G-EVAL gains a second arm. The first is retained unchanged and relabelled.** This is an
*addition*, recorded in `docs/GATE-CHANGES.md` with its argument and date; it is not a lowering, and
methodology §3.5's rule — *a threshold may be lowered only by an argument that the old one was wrong, never
by the discovery that it cannot be met* — is respected, because the discovery here is that the old
threshold was **weaker than it appeared**, which licenses adding and forbids removing.

```
G-EVAL, two arms, both required
───────────────────────────────
ARM 1  NON-DISCRIMINATING, NECESSARY.  505 of 505 exact against the blank's cached values.
       Reported ALWAYS with its census: "301 numeric zeros, 204 copies of the string 'NA',
       0 non-zero numeric values (MEASURED)". The gate report carries the literal label
       NON-DISCRIMINATING. Threshold unchanged: exact on 505 of 505, or every non-reproducing
       cell named, its cause identified, excluded from the observability site set and flagged
       INDETERMINATE(indeterminate.engine_disagreement) from a pinned per-template table.
       More than 25 (5%) -> G2 is downgraded to a REACH measurement reported as K/G and labelled.

ARM 2  DISCRIMINATING.  On >= 3 filled fixtures built by tools/fixtures/make_discriminating.py,
       every formula cell whose expected value is NON-TRIVIAL (not 0, not "NA") reproduces exactly
       against BOTH of:
         (a) a HUMAN-AUTHORED expectation file, tests/golden/expected/<fixture>.expected.json,
             written from the formula text by a person who did not write the evaluator, carrying a
             declared `authored_by` field; and
         (b) the digest-pinned OFFLINE LibreOffice engine (D4), whose per-cell disagreements are
             written to the engine_disagreement table rather than resolved by preference.
       Threshold against (a): 100%, on its own denominator |non-trivial cells|.
       Threshold against (b): DISAGREEMENT ON MORE THAN d NON-TRIVIAL CELLS DOWNGRADES G2 TO A REACH
       MEASUREMENT, on the same branch as arm 1's 25-cell rule, where
           d = 11        (A FROZEN INTEGER. Arbitration C1.)
       pre-registered in experiments/G-EVAL/PREREGISTRATION.md BEFORE the first fixture is built,
       together with the derivation max(3, ceil(0.05 * |non-trivial cells|)) that produced it, the
       content hash of the corpus it was evaluated against, and the date. d DOES NOT RECOMPUTE.
       Below 100% against (a): the same escalation as arm 1, on the discriminating denominator.
```

#### **Arm 2 had no failing condition against its only independent instrument, and no budget for its author**

`docs/GATE-CHANGES.md` records the two-arm split as the repair for §0.2 N1. **Two things were wrong with
the repair as first written, and both are fatal to the arm.**

**(i) There was no failing condition against (b).** LibreOffice is the only *independent* instrument in the
pair — the only one nobody in this project wrote. Its disagreements were *"published, never silently
resolved"*, which sounds like rigour and is a log line: **a build whose evaluator disagreed with
LibreOffice on every non-trivial cell passed arm 2, provided it agreed with the expectation file.** The
gate's independence contributed nothing to its pass/fail. The `d` threshold above is the repair, and the
form is deliberate: *a published disagreement that changes nothing is a log line, not a gate.*

> **`d` is DECIDED here, before any run: `d = 11`, an integer** (arbitration **C1**). *How the number was
> produced, retained as the derivation and not as the rule:* `max(3, ceil(0.05 × |non-trivial cells|))`
> evaluated against the **204 non-trivial cells** §0.2 N1 measured, which yields 11. *Reason for the 5%
> shape:* arm 1's escalation is 25 of 505, i.e. 5%, and a gate whose two arms escalate on different shapes
> of threshold invites the argument that the inconvenient one is the wrong shape. The floor of 3 exists
> because a pure percentage on a small denominator would round to zero and make the arm unfailable again.
> *Alternative it beat:* **keeping the formula as the rule** — rejected, because a threshold that recomputes
> from the corpus it is applied to *moves when the data moves*, which is F1's defect in another costume: the
> gate's strictness becomes a function of the thing being gated and nobody sees it change.
>
> **What is pre-registered is the number, not the generator.** `experiments/G-EVAL/PREREGISTRATION.md`
> carries, in one entry: (a) `d = 11`; (b) the formula `max(3, ceil(0.05 × |non-trivial cells|))` that
> produced it; (c) the **content hash of the corpus it was evaluated against**; (d) the date. It is written
> in the same commit as the `docs/GATE-CHANGES.md` two-arm entry — which records the *change*, while
> `PREREGISTRATION.md` holds the *constant* — and **before** `make_discriminating.py` runs;
> `test_gate__d_predates_the_first_fixture` asserts the `PREREGISTRATION.md` commit is a git-ancestor of
> the first fixture's, exactly as the corpus lane asserts the fill brief predates the first workbook.
>
> **If the corpus changes, `d` does not silently follow.** A new pre-registration is written, with a
> recorded reason, and the old one is kept. The criterion may change only by an argument that the old
> criterion was wrong.

**(ii) The expectation file's author was, by the plan's own resource model, the evaluator's author.** The
effort model is *one competent engineer*; every second-person cost in the programme is enumerated (corpus
15–25 person-days, adjudication 3–5, κ re-rate 1, strata 2+1, proviso labeller 0.5, admission signer 0.25,
transfer operator 4–6 h) — **and P3 had none.** So arm 2 resolved, silently, to §Y's second branch. The
failure scenario is one sentence long: the engineer implements `AGGREGATE(15,6,…)` with a subtly wrong
tie-break, writes the expectation file from the same mental model an hour later, both agree, LibreOffice
disagrees on 40 cells, those 40 are published in a table no gate reads, **G-EVAL is green, and every kill
rate in the programme rests on it.** That would be the sixth instance of this project's own failure mode,
committed inside the build that documented the fifth.

**R11 now budgets the author: 1.5 person-days of someone who has not read `calc/`**, in the same column as
every other second-person cost. And the degradation is mechanised rather than promised:

`tests/contract/test_arm_two_author_is_not_the_evaluator_author` — read `expected.json`'s declared `authored_by`
and `calc/`'s dominant author from `git blame`; **if they are equal**, assert that
`docs/measurements/P3-evaluator.md`, `ci/GATES.md` and **every surface that quotes a kill rate** carry the
literal string **`SAME-AUTHOR — a weaker instrument`**, and that `ci/GATES.md` records G-EVAL as
**`PASSED — NOT INDEPENDENT`**. §Y already writes the rule and says *"there is no third option and no
silent one"*; **this is the test that makes the third option unreachable.** Catalogue: the guard is bound
to NC-E11's entry as a third `flips: true` guard, so deleting it flips the sweep.

**How the filled fixtures are built without a corpus.** `make_discriminating.py` writes values into the
*field surface only*, by raw-zip surgery, from a seeded PRNG, choosing values that make each of the six
semantics above take a **non-trivial branch**: at least one `"yes"` in `'1. Introduction'!N54:N63` so the
`AGGREGATE` arm returns a row number and `INDEX` returns a real value; at least one scheme type matching
each of the five `COUNTIF` wildcards and **at least one matching none of them**, which is the `D17` defect
(NC-N04) made executable; non-zero money in the `'3. Portfolio'` carry graph so the 32 shared groups and
195 cross-sheet edges produce distinct sums. Each fixture carries
`CDFC_SYNTHETIC = true` and `CDFC_PROVENANCE = TEMPLATE-COMPUTED` in `/docProps/custom.xml`
(methodology §6.4), so no rate computed from it can be quoted as a measurement of real filings.

**And the honest limit, in the gate report:** arm 2's oracle (a) is a human, and a human authoring an
expectation from formula text can share the evaluator author's misconception. It is a *different*
instrument, not an independent one — and if R11's second author is unfunded it is not even that, which is
what `test_arm_two_author_is_not_the_evaluator_author` forces onto the surface. Oracle (b) is independent and
carries its own measured defect (LibreOffice writes 53 main-namespace validations where 35 + 19 = 54) —
which is a defect in its *validation writing*, not its *formula recalculation*, and the 91.9% recalc-exact
figure was ruled evidentially void, so **no floor is quoted, disagreement is measured per cell, per
template version, offline — and above `d` it now changes the gate.**

**The hand-computed filing that this build also produces, because P5's exit gate needs it and only this
build has the artifact.** Once `expected.json` exists, `tools/fixtures/materialise_expected.py` writes its
values into a copy of the fixture's cached `<v>` elements by raw-zip surgery, producing
`fixtures/synthetic/clean__hand-computed__fme-q1__<sha8>.xlsx`. **Its derived cells were typed by a person
from the formula text; `src/cdfc/calc/` never touched them.** It carries `CDFC_SYNTHETIC = true` and
`CDFC_PROVENANCE = HAND-COMPUTED` in `/docProps/custom.xml`. It is a **fixture, not a corpus**:
`CorpusProvenance` stays at exactly six members (so `04`'s `test_contract__six_corpus_provenances` is
untouched) and `qualify/corpus.py` **refuses to load a `HAND-COMPUTED` artifact as a corpus**, so no FFR
can ever be computed from one filing. `01` §6.5's provenance-token grammar must admit `hand-computed`
(obligation **Y12**). *Why it exists:* `03`'s P5 exit criterion 1 — *clean filing ⇒ 0 FAIL* — is otherwise
evaluated on a filing that `src/cdfc/calc/` computed, which makes it arithmetically impossible for the 227
arithmetic predicates to fire and turns the criterion into `x == x`. **One filing the product did not
compute is enough to make that gate non-vacuous; zero is what the plan had.**

#### Data produced

`docs/measurements/P3-evaluator.md` — the two rates with their two denominators, the blank's trivial-value
census, the list of every non-reproducing cell with its cause, the function-vocabulary census (§0.2 N5)
and the `_xlfn.SINGLE` decision (R10).

#### Functionality validation

**Unit.** One module per function with a published test vector, table-driven:
`test_functions__countif_wildcards` (`*Angel*`, `?`, `~*` escape, case-insensitivity) ·
`test_functions__aggregate_15_6_ignores_errors` · `::empty_result_is_num_error` ·
`test_functions__iferror_catches_every_excel_error` · `test_functions__index_out_of_range_is_ref` ·
`test_functions__single_on_a_single_cell_is_identity` ·
`test_operators__array_division_by_false_is_div0` ·
`test_graph__cycle_is_not_run` — a synthetic cycle yields `NOT_RUN`, never a fixed-point guess.

**Property.** *Invariant:* the evaluator is a pure function of `(schema, facts)` — no ordering,
environment or clock dependence. Generator: 200 random topological orderings of the 505-cell FME graph
(the sort is stable, but the *input* edge order is shuffled).
`tests/property/test_prop_calc.py::test_prop__evaluation_is_order_independent`.
*Second invariant:* `recalculate` never returns a `float`. Same generator.

**Golden.**
`tests/golden/test_cached_values.py::test_golden__blank_cached_census__fme` — pins **301 / 204 / 0** and
the label `NON-DISCRIMINATING`. *Which workbook and why:* FME, the only one with all 505 cells cached.
`tests/golden/test_cached_values.py::test_golden__aggregate_block__fme` — the 30 cells of
`'1. Introduction'!C92:E101` all reproduce as the string `"NA"` **and** the test asserts, in its docstring
and in an explicit second assertion, that this outcome is **also** produced by
`injectors/aggregate_as_sum` — recording the limit rather than hiding it.
`tests/golden/test_discriminating.py::test_golden__discriminating__filled_fme` — the non-trivial cells of
each filled fixture against `expected.json`.

**Differential.**
**D3 (arm 1)** — evaluator vs the blank's cached values, 505 of 505, blocking, labelled
`NON-DISCRIMINATING`.
**D3′ (arm 2, new)** — evaluator vs the human-authored expectation on the filled fixtures, blocking.
**D4** — evaluator vs digest-pinned offline LibreOffice; **advisory, nightly**; writes
`engine_disagreement(template_sha256, cell_ref, our_value, lo_value, lo_container_digest, measured_at)`.
LibreOffice is excluded from the verdict path (spec G12) and `ci/no-libreoffice-online.sh` enforces it.

**Negative controls.**
- **NC-E11 (new)** — *the positive control has no information in it.* This is the catalogue entry that
  encodes §0.2 N1 permanently.

  ```yaml
  - id: NC-E11
    component: calc
    break: "an evaluator that computes nothing passes G-EVAL, because the blank template's 505 cached
            values are 301 numeric zeros and 204 copies of the string 'NA'"
    measured_instance: "MEASURED on FME 7d9a1960 (plan/02 §0.2 N1): by-type {n:301, str:204};
                        distribution {num:0 -> 301, str:'NA' -> 204}; non-zero numeric values: 0.
                        The decomposition's own named control for this gate — AGGREGATE evaluated as
                        SUM — also yields 'NA', because SUM over an array of #DIV/0! is an error and
                        IFERROR catches it."
    injector: evaluator_returns_zero_and_na
    why_impossible: null
    guard_tests:
      - tests/negative/test_nc_evaluate.py::test_nc__E11a_null_evaluator_passes_arm_one
      - tests/negative/test_nc_evaluate.py::test_nc__E11b_null_evaluator_fails_arm_two
    positive_control: tests/golden/test_discriminating.py::test_golden__discriminating__filled_fme
    status: ACTIVE
  ```

  `test_nc__E11a` asserts the null evaluator **passes** arm 1 — a negative control that asserts a guard
  is *inert* — and `test_nc__E11b` asserts it **fails** arm 2. The pair is the point: without E11a,
  someone later deletes arm 2 as redundant.
- **NC-E12 (new)** — *a function outside the vocabulary is silently swallowed by `IFERROR`.*

  ```yaml
  - id: NC-E12
    component: calc
    break: "an unimplemented function raises an ExcelError that IFERROR catches, so the cell reproduces
            its cached value and the unimplemented function is never reported"
    measured_instance: "204 of 505 FME formula cells are IFERROR-wrapped (MEASURED); _xlfn.SINGLE is a
                        ninth function absent from the spec's eight-function vocabulary and occurs at
                        '1. Introduction'!D92 (MEASURED, plan/02 §0.2 N5)"
    injector: unimplemented_returns_error
    why_impossible: null
    guard_tests:
      - tests/negative/test_nc_evaluate.py::test_nc__E12_unimplemented_is_not_run_not_an_error
    positive_control: tests/unit/test_functions.py::test_functions__single_on_a_single_cell_is_identity
    status: ACTIVE
  ```

  The guard asserts that an unimplemented function makes its cells `NOT_RUN(not_run.source_unreadable)`
  and lands in `ValueGrid.not_run` **before** any `IFERROR` sees it — the unimplemented-function path and
  the Excel-error path are different objects and `IFERROR` catches only the second.
- **NC-E13 (new)** — *a fixed epsilon replaces `τ(n) = 5n`.* Injector `injectors/fixed_epsilon.py`; the
  guard asserts a false failure on a `TEMPLATE-COMPUTED` clean fixture. **A fixed epsilon is the single
  most likely source of spurious failures**, and it is invisible on the blank because every value is 0.

**Determinism.** `test_det__evaluator_is_reproducible` — the FME recalculation run twice under different
`TZ`, `PYTHONHASHSEED`, `LC_ALL` and working directory produces byte-identical canonical JSON of the
`ValueGrid`. `Decimal`'s context is pinned explicitly at module import, never inherited.

**Performance.** `PERF-EV` — evaluation over the 505-cell graph: baseline sub-ms; warn 5 ms, fail 10 ms.
`PERF-CORE` — the deterministic core end-to-end: baseline **~30 ms**; warn 45 ms, fail 60 ms.

**Mutation.** `calc/` is not in the methodology's tier table because it did not exist when the table was
written. **Ruling: `calc/` is Tier V** (`K/V ≥ 0.90`), blocking from this phase — it is the oracle under
every kill rate, which is the definition of verdict-critical. Recorded in `docs/MUTATION-THRESHOLDS.md`
with its date and argument.

**Effort: 12.0 days** (R11; realistic range 10–15). The nine functions with real array semantics are ~5,
the discriminating-fixture generator ~2, the LibreOffice differential with its `engine_disagreement` table
~2, `formula_source` and the two grids ~1, `materialise_expected.py` and the hand-computed filing ~1, the
rest ~1. **Plus 1.5 person-days of a second author for `expected.json`, which is a different person's time
and is not in the 12.** *The reason this estimate matters more than its size:* the cheapest way to make a
7-day estimate come true is to skip arm 2, and arm 2 is the only part of P3 that carries information.

---

## P3 · The measurement this phase produces

> **Two rates, two denominators, and the census that explains why there must be two.**
>
> **(a) The specified rate — arm 1.** Cells reproduced exactly / **505** (FME) and / **1,495** (all formula
> cells across the nine). Warrant **MEASURED**. **Published with the label `NON-DISCRIMINATING` and its
> census: 301 numeric zeros, 204 copies of `"NA"`, 0 non-zero numeric values.**
>
> **(b) The discriminating rate — arm 2, new.** Non-trivial cells reproduced exactly / **|non-trivial cells
> across the filled fixtures|**, against a human-authored expectation, with the per-cell LibreOffice
> disagreement set published beside it. Warrant **MEASURED**.
>
> Plus the function-vocabulary census — **nine functions, not eight** — and the `_xlfn.SINGLE` decision.

Neither number exists today. The spec lists (a) under *"measurements before any number is quoted"* and
states plainly that **no kill rate may render before it passes**; this document's contribution is the
measurement that (a) alone cannot carry that weight.

Ledger rows:

```json
{"phase":"P3","build":"P3.4","metric":"evaluator.cached_reproduction.blank.fme","numerator":505,
 "denominator":505,"denominator_source":"formula cells carrying a cached value on the pinned blank",
 "warrant":"MEASURED","produced_by":"src/cdfc/calc/cached.py","command":"cdfc eval --template 7d9a1960",
 "caveat":"NON-DISCRIMINATING: the 505 cached values are 301 numeric zeros and 204 copies of the string
           'NA'; an evaluator that computes nothing reproduces all of them",
 "date":"20__-__-__"}
{"phase":"P3","build":"P3.4","metric":"evaluator.discriminating_reproduction.filled.fme","numerator":null,
 "denominator":null,"denominator_source":"non-trivial expected values across >=3 TEMPLATE-COMPUTED filled
 fixtures","warrant":"MEASURED","produced_by":"src/cdfc/calc/cached.py",
 "command":"make eval-discriminating",
 "caveat":"oracle (a) is a human expectation file and is a DIFFERENT instrument, not an independent one",
 "date":"20__-__-__"}
```

## P3 · Exit gate — this is barrier 2 and gate G-EVAL

**TRUE iff all of:**

1. **Arm 1**: exact on **505 of 505** for FME, or every non-reproducing cell named, its cause identified,
   excluded from the observability site set and flagged `INDETERMINATE(indeterminate.engine_disagreement)`
   from a pinned per-template table. **More than 25 (5%) ⇒ G2 is downgraded to a reach measurement,
   reported as `K/G`, and labelled as such wherever it renders.**
2. **Arm 2**: 100% on the non-trivial cells of ≥ 3 filled fixtures against the human-authored expectation;
   the LibreOffice per-cell disagreement set published in `engine_disagreement` **and its cardinality
   `≤ d = 11`** (the frozen integer, C1), with `d` recorded in `experiments/G-EVAL/PREREGISTRATION.md` — with
   its derivation, the corpus content hash and the date — in a commit that is a git-ancestor of the first
   fixture's (`test_gate__d_predates_the_first_fixture`).
   **Above `d`, G2 is downgraded to a reach measurement and labelled wherever it renders** — the same
   branch as arm 1's 25-cell rule.
2a. **`test_arm_two_author_is_not_the_evaluator_author` green.** Either `expected.json`'s `authored_by` differs
   from `calc/`'s dominant `git blame` author, **or** `docs/measurements/P3-evaluator.md`, `ci/GATES.md`
   and every kill-rate surface carry the literal `SAME-AUTHOR — a weaker instrument` and G-EVAL is
   recorded `PASSED — NOT INDEPENDENT`. *A gate that is green on an oracle we wrote ourselves must say so
   on the surface, not in a residue section.*
2b. **`docs/EVALUATION-CONTRACT.md`'s generated `formula_source` section published** (C8b — there is no
   separate `docs/RECALCULATION-SOURCE.md`), `recalculate` has no default `formula_source`, and
   `test_calc__filing_source_preserves_an_overwritten_literal` and
   `test_calc__template_source_recomputes_it` are both green on
   `formula-overwritten__portfolio-O7.xlsx`. **Without these two, P6 classifies the entire F11 population
   `UNOBSERVABLE` and `TEMPLATE_DIFF` cannot be admitted at G2 — and nobody finds out until P9-B4.**
2c. **`clean__hand-computed__fme-q1__<sha8>.xlsx` exists**, its `CDFC_PROVENANCE` is `HAND-COMPUTED`, and
   `qualify/corpus.py` refuses to load it as a corpus. P5's exit criterion 1 depends on it.
3. `NC-E11a` **and** `NC-E11b` both green — the null evaluator passes arm 1 and fails arm 2, demonstrated,
   with both assertion lines captured in `reports/negative-control-sweep.json` and pasted into
   `docs/GATE-LIVENESS.md`.
4. `NC-E12` green — an unimplemented function is `NOT_RUN`, never an `IFERROR`-swallowed error;
   `NC-E14` green — the observability call site uses `FILING`, and flipping it to `TEMPLATE` goes red;
   `test_contract__valuegrid_not_run_is_addressable` green.
5. `test_no_float_in_money_path` and `test_calc__never_produces_a_float` green; `ci/no-float-money.sh`
   covers `calc/` (R4).
6. `docs/GATE-CHANGES.md` carries the dated two-arm entry with its argument.
7. `calc/` mutation score at **Tier V** threshold, reported as `K/V` first with `I`, `T` (ids listed), `E`
   and its published arguments.

## P3 · What it kills if it fails

- **Total failure of arm 1** kills the observability filter, hence `O`, hence `K/O`, hence gate G2's
  *quality* interpretation; and it kills `TEMPLATE_DIFF`. The system that survives is **harvest + verdict
  model + closure + canaries + FFR**, with kill rates reported as `K/G` and explicitly labelled *reach,
  not quality*. Smaller and still shippable.
- **Failure of arm 2 alone** is the more likely and more interesting outcome, and it kills something
  narrower: the claim that our evaluator is *correct*, as distinct from *non-crashing*. The response is
  not to delete the arm. It is to publish the discriminating rate as measured, exclude the disagreeing
  cells from the observability site set by name, and carry the exclusion on the report surface — the same
  treatment arm 1's 5% branch already specifies.
- **If `_xlfn.SINGLE` cannot be implemented in ≤ 20 lines** (R10), `'1. Introduction'!D92` and its
  materialised siblings are `NOT_RUN(not_run.source_unreadable)` and the count — 1 authored occurrence —
  is published. One cell is not a crisis; an unpublished exclusion is.
- **If the filled fixtures cannot be built without contaminating the corpus lane** — they cannot; they are
  `TEMPLATE-COMPUTED`, built by our own tooling from the blank, and they are labelled inside the artifact
  as synthetic. No FFR is ever computed from them. If that labelling cannot be made to survive
  (methodology §6.4's three layers), the fixtures do not ship and arm 2 falls back to oracle (b) alone,
  with the weaker warrant stated.

---

# §X — WHAT THIS DOCUMENT ADDS TO THE NEGATIVE-CONTROL CATALOGUE

Fourteen new entries, each with a full YAML row given at its build. Existing entries are referenced by id
and never restated.

| id | Component | The break, in one line | Injector | Real? |
|---|---|---|---|:--:|
| **NC-CI01** | ci | a grep gate whose scan root does not exist returns success | `remove_scan_root` | structural |
| **NC-CI02** | ci | `filterwarnings = ["error"]` is removed, and openpyxl's data-validation `UserWarning` scrolls past | `warnings_tolerated` | **REAL** |
| **NC-CI03** | ci | a `SECONDARY` runtime licence is tolerated past P2 | `licence_phase_marker` | **REAL** (gVisor `NOT-FOUND`) |
| **NC-F01** | fixtures | a vendored prescribed workbook drifts | `flip_fixture_byte` | structural |
| **NC-N16** | conduct | a field observation is quietly dropped | **NONE** | — |
| **NC-P07** | ingest | reader competence is narrowed to make a real disagreement disappear | `competence_narrow` | **REAL pressure** (4 of 8 fields disagree on day one) |
| **NC-P08** | ingest | an `lxml` parser is constructed outside `xmlsafe.py` | `raw_lxml_parser` | structural |
| **NC-P09** | ingest | the two "independent" readers are one reader called twice | `reader_b_calls_a` | structural |
| **NC-P10** | ingest | an unknown construct is skipped without reaching the manifest | `manifest_swallow` | structural |
| **NC-D05** | schema | absence of `<protection>` is read as unlocked | `mask_absent_is_unlocked` | **REAL** (322 of 434; 6,249 vs 3,747) |
| **NC-D06** | schema | a filing-conditional vocabulary is treated as static | `vocab_take_first_branch` | **REAL** (2 of 22 on FME) |
| **NC-D07** | schema | formula content enters the structural fingerprint | `fingerprint_includes_formulas` | structural |
| **NC-E10** | facts | a vocabulary is resolved from the filed artifact | `template_from_filing` | **REAL** (`Dropdown` is hidden *and* unprotected) |
| **NC-E11** | calc | **the positive control gating every kill rate has no information in it** | `evaluator_returns_zero_and_na` | **REAL** (301 / 204 / 0) |
| **NC-E12** | calc | an unimplemented function is swallowed by `IFERROR` | `unimplemented_returns_error` | **REAL** (204 of 505 wrapped) |
| **NC-E13** | calc | a fixed epsilon replaces `τ(n) = 5n` | `fixed_epsilon` | structural |
| **NC-CI04** | ci | an absence line satisfies `no-bare-absence.sh` by containing the words "positive control" | `absence_cites_empty_control` | **REAL** (the gate is a lexical co-occurrence) |
| **NC-CI05** | ci | a golden pins an integer literal that appears in no ledger row and no `01` §0.3 table row | `untraceable_golden_literal` | **REAL** (`2,373`, §0.2 N3a) |
| **NC-CI06** | ci | two documents define the same `NC-` id and the later silently replaces the earlier | `duplicate_nc_id` | **REAL** (`E10`/`E11`/`E12`, `Q12`–`Q16`, `N07`, `N11`/`N12`) |
| **NC-CI07** | ci | `perf_counter`/`monotonic`/`process_time` reaches the deterministic core | `perf_counter_in_core` | **REAL** (`05`'s `CanaryRow.elapsed_us`) |
| **NC-CI08** | ci | the sweep reverts to "at least one guard fails", so an entry is caught by its weakest guard | `sweep_any_guard` | **REAL** (the sweep as `01` §2.0 specifies it) |
| **NC-P11** | ingest | a competence exclusion measured on one workbook classifies all nine | `competence_generalised` | **REAL** (§0.2 N3 is `n = 1`; the matrix is `n = 9`) |
| **NC-D08** | schema | the mask is never checked against anything outside this repository | `mask_drops_a_sheet` | **REAL pressure** (3,747 / 3,755 / 6,249) — `PENDING_CORPUS` until P8-B1 |
| **NC-E14** | calc | observability recalculates with the **template's** formulas, so every F11 mutant is `UNOBSERVABLE` by construction | `observability_uses_template_formulas` | **REAL** (F11 is the flagship class) |

**Twenty-three entries, and the band is `CI01–CI09 · F01–F09 · P07–P19 · D05–D19 · E10–E19 · N07–N09`
(R5a).** `ci/catalogue-ids.sh` fails the build if any of them is also defined in another document.

**NC-E11 is the one to read first.** It is the only entry in the catalogue whose guard asserts that a
*specified gate is inert*, and it exists because the measurement was taken before the build was planned.
Had P3 been built to its written gate, the programme's second barrier would have been green from the first
commit and every kill rate downstream would have rested on it.

---

# §Y — CROSS-DOCUMENT OBLIGATIONS AND WHAT REMAINS OPEN

**Obligations this document creates for later documents.** None of these may be restated with different
numbers; each is named so the receiving document can reference rather than reinvent.

| # | Obligation | Owner |
|---|---|---|
| Y1 | **The `REJECTED` predicate state (audit §V.7.5) must be confirmed before the predicate schema is written.** This document does not write that schema | `plan/03-phases-verdict.md`, P4-B1 |
| Y2 | The **20-of-22 resolution rule** (§0.2 N7) governs how membership predicates over `'8. Compliance Status'!C10`/`!C11` are authored: `applicable`-gated on `C5`, `OUT_OF_SCOPE` when unmet | `plan/03`, P4-B4 harvest |
| Y3 | The **two unwired vocabularies** (`Dropdown!L`, `Dropdown!R`, §0.2 N8) are candidate obligations with no enforcement point. They belong in `scopeCaveats[]`, not in the harvest | `plan/03` (P5 closure), `plan/07` (P14-B2 Unchecked panel) |
| Y4 | **`calc/` is Tier V** for code mutation (`K/V ≥ 0.90`). The methodology's tier table predates the package | `plan/01` §3.5, by an appended row |
| Y5 | **G-EVAL has two arms.** Any later document quoting "505 of 505" without the `NON-DISCRIMINATING` label and the 301/204/0 census has quoted the wrong number | `plan/04-phases-qualification.md` (P6's `O`), `plan/05` (P9's `TEMPLATE_DIFF`) |
| Y6 | The **reader-competence matrix** classifies every cell of P1's 72-cell agreement matrix. A downstream document reporting "the readers disagree on N fields" without the classification has reported a number that will get the check switched off | `plan/04`, `plan/07` |
| Y7 | The **`D17` defect is now executable**: `'1. Introduction'!D17 = SUM(D18:D20)` over five wildcard `COUNTIF`s against a nine-term vocabulary. It is a fixture, not an anecdote, and it belongs in the residue exhibit set | `plan/05`, P10-B4 |
| Y8 | `PERF-RECEIPT` and `PERF-GUARD` are **new budget ids** and must be added to methodology §1.8's table with their measured baselines | `plan/01` §1.8 |
| **Y9** | **`recalculate` takes `formula_source` with no default** (P3-B4). **P6-B3's observability filter must pass `FILING`**, and its classification becomes three-way — `OBSERVABLE · UNOBSERVABLE · INDETERMINATE_OBSERVABILITY` (the recalculation touched a `not_run` cell) — with `I` excluded from `O`, **published as its own integer with the cells named**, and `Campaign.render()` printing `G · U · I · O · R · K`. Without this, the entire F11 population is `UNOBSERVABLE` by construction, `TEMPLATE_DIFF` cannot clear G2, and `U/G` measures our evaluator's coverage while being published as a property of the fault model | `plan/04`, P6-B3 and P7-B3 |
| **Y10** | **`2,373` is `DERIVED-FROM-SPEC`, not `MEASURED`, until P4-B4 computes `len(HarvestResult.cells_reachable)` for `7d9a1960` and reconciles it in writing** (§0.2 N3a). It may not be pinned as a literal in any golden until then; `ci/golden-literals-are-traceable.sh` (row 17) enforces it. Spec §III.4.3's *"53 validation predicates"* does not reconcile with the harvest's 20 membership predicates and **a divergence is a finding, not a correction** | `plan/03` P4-B4; `plan/07` P14-B1's hero |
| **Y11** | **`clean_corpus_independent_of_predicate` must be COMPUTED, not declared**: `independent = import_closure(corpus.generator) ∩ import_closure(predicate.evaluation) == ∅ and read_keys(cand) ∩ corpus.computed_cells == ∅ and corpus.provenance != SELF-AUTHORED`. `import_closure` is public from P0-B3 and `ValueGrid.computed_cells` is a field from P3-B4, so both operands exist; `g4_ffr.check()` raises `UninformativeCorpusError` when it is false — the same fail-closed shape as `SELF-AUTHORED`, in the same function | `plan/04`, P8-B3 |
| **Y12** | `01` §6.5's fixture-provenance token grammar must admit **`hand-computed`**. It is a *fixture* token, not a seventh `CorpusProvenance` member — `qualify/corpus.py` refuses to load a `HAND-COMPUTED` artifact as a corpus, so `04`'s `test_contract__six_corpus_provenances` is untouched | `plan/01` §6.5; `plan/04` P8-B3 |
| **Y13** | `ci/no-clock-in-core.sh` now greps `perf_counter\|monotonic\|process_time` (R3). The companion structural test — `test_contract__no_duration_field_in_a_hashed_object`, walking every dataclass that reaches `canonical_json` — belongs to the phase that owns `CanaryRow`. **`CanaryRow.elapsed_us` must move to `reports/perf/<run_id>.jsonl`, outside the hashed payload**, keeping `witness_digest`, `observable`, `intersects_read_set`, `fired` and `canariesRun == len(rows)` as the deterministic evidence of execution | `plan/05`, P10-B1 and P11 |
| **Y14** | **The revised effort figures are P0 8 · P1 8 · P2 10 · P3 17 = 43 engineer-days, not 34** (R11), plus 5.0 second-author person-days. `00` §7's critical path and its *"requires ~2–3 engineers to realise"* line must be recomputed against 43, and the staffing model stated once so both numbers derive from it. **DISCHARGED: `00` §7 publishes ~118 (C6); `~114` is retired** | `plan/00` §7 |
| **Y15** | **DISCHARGED AND SUPERSEDED BY ARBITRATION C9.** The band table this obligation was written against is deleted, along with the three others that disagreed with it; **`01` §2 is the sole registry and the sole allocator**, and no document — this one included — may define an id. `02`'s `NC-N07` became **`NC-N16`**, `07`'s became **`NC-N40`**, `NC-N07` is **RETIRED**; `04`'s `NC-N20`/`NC-N21` became `NC-N50`/`NC-N51` and `05`'s became `NC-N25`/`NC-N26`, with `NC-N20`/`NC-N21` **RETIRED**; `03`'s `NC-Q40`–`Q46` became `NC-Q70`–`Q75` (its `Q45` merging into `NC-Q57`) and `04`'s became `NC-Q55`–`Q61`, with `NC-Q40`–`Q46` **RETIRED**. `ci/catalogue-ids.sh` (row 18) fails the build on any remaining collision, and it runs from P0 | `plan/01` §2; `plan/05`, `06`, `07` |
| **Y16** | **The sweep asserts an exact per-guard set, not "at least one"** (P0-B3). `01` §2.0 step 3's contract, and every catalogue entry in every document, must carry `flips: true\|false` per guard. `reports/negative-control-sweep.json` publishes `guards_flipped / guards_expected_to_flip` beside `entries_caught / entries_active`, plus `provisional_count`, and DoD line C4 becomes a **path into that report**, not a paste | `plan/01` §2.0 and §4; every phase document's catalogue rows |

**What remains genuinely open in these four phases**, with the decision rule rather than an invented
answer — repeating R10 only for the items a later reader will look for here:

1. **gVisor's licence.** `NOT-FOUND`, and it is a runtime dependency. **Rule:** open it, or record the
   `seccomp`+namespaces fallback in `docs/LICENCES.md` and print the weaker boundary on the deployment
   surface. It is the one licence item that can block P1.
2. **`_xlfn.SINGLE`.** **Rule:** implement iff ≤ 20 lines with a passing unit vector; otherwise `NOT_RUN`,
   count published.
3. **Whether arm 2's human expectation author can be a different person from the evaluator's author.**
   **Rule:** if yes, the arm is a differential; if no, it is a self-check and `docs/measurements/P3-evaluator.md`
   says `SAME-AUTHOR — a weaker instrument` in those words. There is no third option and no silent one.
   **Now budgeted (R11: 1.5 person-days) and mechanised (`test_arm_two_author_is_not_the_evaluator_author`), so
   the branch is taken by a test rather than by whoever is under deadline pressure.** It is an
   *OPEN — USER DECISION* only in the sense that the money must be committed: see R11's question, which
   also covers reader A′ and mask path B and should be asked once, before P1-B3.
4. **The `1,495` corpus-wide denominator for arm 1** assumes every formula cell in all nine workbooks
   carries a cached value. **Rule:** P3-B4 measures it per workbook before quoting the ratio; a workbook
   with uncached formula cells contributes to the numerator's denominator only for the cells that have an
   oracle, and the shortfall is published.

---

# §Z — WHAT THESE FOUR PHASES DO NOT ESTABLISH

Written in the authors' own words, as the DoD's §H requires, because a build that cannot name its own
residue has not been understood by the person who built it.

1. **That the two "independent" readers do not share a misconception.** NC-P09 distinguishes two
   implementations from one called twice. It cannot distinguish two implementations from **two copies of
   the same misunderstanding of ECMA-376**, and both will be written by people reading the same
   specification. This is methodology §7.5 and NC-N06, and nothing in P1 closes it. The extraction
   manifest's `constructs_not_understood` list is the only mitigation and **it lists only what we knew to
   look for.**
2. **That 3,747 is the right denominator.** P2 establishes that two code paths agree on it and that the
   rule they implement is written down. It does not establish that the rule is the one the regulator
   intended by protecting nine sheets, and **there is no instrument in these four phases that could** —
   which is why the number now ships labelled `PROVISIONAL-UNVALIDATED`, why all three lawful readings
   (**3,747 / 3,755 / 6,249**) are tabled in `docs/PROTECTION-RESOLUTION.md`, and why
   `denominator.generator_rule` renders beside every fraction. **The external falsifier exists and is
   scheduled:** `test_mask_matches_what_a_competent_filler_filled` at P8-B1, over the blind-fill corpus
   (NC-D08). Until it runs, every fraction this product prints is a fraction of an unfalsified number, and
   the label is the only honest form of that sentence.
3. **That the evaluator is correct.** Arm 2 raises the bar from *non-crashing* to *agrees with a human and
   with one other engine on non-trivial values*. Agreement with two instruments is not correctness, and
   the one independent engine in the pair has a measured, uncharacterised defect of its own.
4. **That the fault surface of the container guard is covered.** Seven adversarial fixtures test seven
   mechanisms someone imagined. Methodology §7.6's self-referential denominator applies in full: the
   catalogue is written by the people who wrote the code, and the only available instrument is the
   catalogue's append-only growth log.
5. **Anything about a filing.** These four phases have never seen a filing. Every fixture is the
   regulator's blank, a synthetic edit of it, or an adversarial construction. No real filed FME return is
   public, and the first non-synthetic input to this system arrives in the corpus lane, not here.
6. **That the gates will stay live.** P0 measures that fifteen gates have been observed red **once**. A
   gate observed red once and never again is a gate whose subject may have moved out from under it — which
   is the version-churn failure (V5/V6) applied to CI. The rate at which catalogue entries are added late
   is the only signal, and it is reported rather than claimed to converge. **What the exact-set sweep adds
   is narrower and worth stating exactly:** it now tells us *which guards* have never been observed red,
   which the "at least one" form could not. It still cannot tell us which guards are red for the wrong
   reason.
7. **That the second author is a second mind.** R11 budgets one for reader A′, mask path B and arm 2's
   expectation file, and `test_same_author_label_is_present_when_authors_match` forces the label when
   there is not one. Neither establishes that two people reading the same ECMA-376 paragraph, or the same
   formula text, do not arrive at the same misconception. That is `01` §7.5 and NC-N06, and **funding the
   second author moves the residue from "one author, undeclared" to "two authors, possibly correlated" —
   an improvement, not a closure.**

---

*Ends. P4 and P5 are specified in `plan/03-phases-verdict.md`; P6–P8 in `plan/04-phases-qualification.md`;
P9–P11 in `plan/05-phases-probes-attestation.md`; P12–P13 in `plan/06-phases-model-and-clause.md`;
P14–P15 in `plan/07-phases-surface-and-transfer.md`.*

---

## REPAIRS APPLIED (adversary pass)

Against `plan/08-adversary.md`. One row per finding that touches P0–P3. **A repair here is a test, a
negative control, a changed gate threshold, a new required field, or a changed contract** — where a row
says "paragraph", it is a paragraph that *states a ruling a test then enforces*, and the test is named.

### FATAL

| id | The finding, in one line | What changed | Where |
|---|---|---|---|
| **F2** | The `TEMPLATE-COMPUTED` clean corpus is produced by the code the arithmetic predicates re-check, so P5's *"clean ⇒ 0 FAIL"* is `x == x` | P3-B4 now also produces **`clean__hand-computed__fme-q1__<sha8>.xlsx`** — derived cells typed by a person from formula text via `tools/fixtures/materialise_expected.py`, `calc/` never touches them. `HAND-COMPUTED` is a **fixture** token, not a seventh `CorpusProvenance` (so `04`'s six-provenance contract is untouched), and `qualify/corpus.py` refuses it as a corpus so no FFR can come from one filing. `ValueGrid.computed_cells` added so `g4_ffr` can compute independence (Y11) | P3-B4 files created; the arm-2 honest-limit block; P3 exit 2c; §Y Y11, Y12 |
| **F3** | G-EVAL arm 2 has no failing condition against LibreOffice and no budget for a second author | **`d = 11`, a frozen integer, pre-registered** in `experiments/G-EVAL/PREREGISTRATION.md` with its derivation `max(3, ceil(0.05 × non-trivial))`, the corpus content hash and the date (C1); above `d`, G2 downgrades to a reach measurement. `test_gate__d_predates_the_first_fixture` (git-ancestor). **1.5 person-days budgeted** in R11. `test_arm_two_author_is_not_the_evaluator_author` forces `SAME-AUTHOR — a weaker instrument` and `PASSED — NOT INDEPENDENT` when authors match, on four named surfaces | P3-B4 gate block + the two-arm box; R11; P3 exit 2 and 2a; §Y open item 3 |
| **F4** | The sweep asserts "at least one guard fails", so an entry is caught by its weakest guard | Catalogue `guard_tests` gains **`flips: true\|false` per guard**; the sweep asserts the **exact set**; `flips:false` on every guard is a schema error; report publishes **`guards_flipped / guards_expected_to_flip`**; new meta-test `test_nc_meta__every_expected_guard_flipped`; new **NC-CI08** whose injector reverts the sweep | P0-B3 sweep contract, data produced, meta-tests, NC-CI08; P0 exit 2a; §X; §Y Y16 |
| **F18** | `U/G` measures the evaluator's coverage, not the operator mix, because `not_run` cells are identical in both grids | `ValueGrid.touched_not_run()` added and `test_contract__valuegrid_not_run_is_addressable` (`values` and `not_run` disjoint, total over the key set). Three-way classification and publishing `I` recorded as an obligation on P6-B3 | P3-B4 `ValueGrid` block; P3 exit 4; §Y Y9 |
| **F19** | Two phases mean different things by "recalculate"; every F11 mutant is `UNOBSERVABLE` by construction and `TEMPLATE_DIFF` can never clear G2 | **`recalculate(..., *, formula_source: "TEMPLATE" \| "FILING")`, no default.** The rule lives in **`docs/EVALUATION-CONTRACT.md`** as a *generated* section, so P5's byte-identity gate survives (C8b: the separate `docs/RECALCULATION-SOURCE.md` is deleted — one contract, one file). Two tests on the F11 fixture; injector `observability_uses_template_formulas` as **NC-E14** | P3-B4 public interface + the `formula_source` block; P3 exit 2b; §X; §Y Y9 |
| **F23** | A wall-clock duration inside a hashed object; `ci/no-clock-in-core.sh` greps only for timestamps | Pattern set extended to **`perf_counter\|monotonic\|process_time`**; `reports/perf/` created at P0-B1 as the one place timings may live; **NC-CI07** with an admission-side twin (the same call inside `measure/perf/` passes). The hashed-dataclass walk is P10/P11's | R3; P0-B1 files; P0-B3 NC-CI07; §Y Y13 |

### SERIOUS

| id | The finding, in one line | What changed | Where |
|---|---|---|---|
| **F5** | `clean_corpus_independent_of_predicate` is a declared boolean nothing computes | `import_closure()` made **public** at P0-B3 with its consumers named, and `ValueGrid.computed_cells` added at P3-B4 — the two operands the computed form needs. The `g4_ffr.check()` raise is P8's | P0-B3 public interface; P3-B4; §Y Y11 |
| **F7** | `ci/no-bare-absence.sh` is defeated by writing "positive control" on the line | The gate now requires a **resolvable `ledger:<row_id>` citation** and asserts `positive_control_count > 0`; `assert_absent` returns the row id. **NC-CI04** with a planted zero-control row and an admission-side twin | R5 row 6 intent; P0-B3 NC-CI04 |
| **F8** | P0's exit gate is `x == x`: `gates_written` is decided by the person deciding demonstrability | The **set** is pre-registered: `LIVE = {1…13,17,18}`, `PENDING = {14,15,16}`, both literals in `test_contract__live_set_is_pre_registered`; movement requires a dated argument in `ci/GATES.md`. **The `12/12` figure was also arithmetically wrong** (it counted the predicate-loader twin, which R5 rules is not a row) → corrected to **15 / 15 of 18** | P0-B1 contract tests; P0 measurement; P0 exit 1; R5 |
| **F10** | G-READERS gates only the three fields every instrument already agrees on | **G-READERS-B added** as exit criterion 3a: A vs A′ agree 9 of 9 on each of the four `A`/`A′`-only fields, **and** `test_nc__P09_mutating_A_moves_only_A[field]` observed red **per field**, not for the validation walk alone | P1-B3 D1′; P1 exit 3a; NC-P09 |
| **F15** | Nothing can falsify the protection-resolution rule that produces 3,747 | `docs/PROTECTION-RESOLUTION.md` gains rule 7: **the three lawful readings tabled with their measured surfaces (3,747 / 3,755 / 6,249)**; `denominator.generator_rule` renders beside every fraction (`test_contract__fraction_renders_its_generator_rule`) | P2-B2 rule block; P2 exit 7–8 |
| **F20** | The competence matrix is fixed from one workbook and P1's number averages an external check with a self-check | `Competence` gains **`measured_on`** + `test_contract__incompetence_is_measured_on_every_workbook_it_classifies` (unmeasured ⇒ `NOT_COMPARABLE`, never `AGREE`); `BLIND_CONTROLS` grows to **all nine**; P1 publishes **two `/36` vectors**, the second labelled `SAME-AUTHOR`; **NC-P11** | R9; P1-B3 `competence.py` + NC-P11; P1 measurement; P1 exit 5 and 6 |
| **F22** | `2,373` and the harvest do not reconcile, and `2,373` is pinned as a MEASURED literal | New **§0.2 N3a**: `2,373` is `DERIVED-FROM-SPEC` until P4-B4 computes it; the *"53 validation predicates"* claim does not reconcile with 20 membership predicates; **`ci/golden-literals-are-traceable.sh` added as registry row 17** with **NC-CI05** | §0.2 N3a; R5 row 17; P0-B3; P0 exit 9; §Y Y10 |
| **F27** | Colliding `NC-` ids across four documents; the later entry silently replaces the earlier | **R5a's band table is DELETED by arbitration C9** — it was one of four that disagreed — and replaced by **`01` §2, THE CANONICAL NC- REGISTRY**, the sole place an id may be defined, + **`ci/catalogue-ids.sh` as registry row 18** + the four meta-tests (`ids_are_unique`, `ids_are_defined_in_the_registry`, `no_orphan_guard`, `no_dangling_reference`) at P0-B3 + **NC-CI06**. `02` keeps `E10–E13` and takes **`N16`** (its `N07` retired); `03` and `04` renumbered mechanically | R5a; P0-B1/B3; P0 exit 8; §X; §Y Y15 |
| **F28** | `ci/no-green-tick.sh`'s scan set names three directories P0 does not create, so R5 forces it to be narrowed on day one | One source of truth: **`src/cdfc/surface/labels.py::SCAN_ROOTS`**, `("src/cdfc",)` at P0, extended by P14; the script carries no directory literal (`test_nc__CI01c`), and `SCAN_ROOTS` is append-only (`test_nc__CI01d`). The narrowing is recorded in `ci/GATES.md` with its reason | R5's `SCAN_ROOTS` ruling; P0-B1 files |
| **F31** | DoD line C4 is a paste only its author can verify | The sweep writes **`assertion_text` and `node_id` per guard** into `reports/negative-control-sweep.json`; C4 becomes a path into that report; `test_sweep__records_the_failing_assertion_text` | P0-B3 data produced |
| **F36** | The denominator ships at day 22 and nothing validates it, though the plan buys the data that could | **`FieldSurface.validation_state = PROVISIONAL-UNVALIDATED`** from P2, rendered wherever the fraction renders, flipped only by **`test_mask_matches_what_a_competent_filler_filled`** at P8-B1, which publishes **two integers** against 3,747 with a **pre-registered zero threshold** on the dangerous direction. **NC-D08**, `PENDING_CORPUS` | P2-B2 boxed ruling + `FieldSurface`; NC-D08; P2 exit 8; §Z item 2 |
| **F38** | NC-Q02 is green for four phases while proving nothing | The sweep reports a **third column, `provisional_count`** — `PROVISIONAL — no admission-side twin yet` — excluded from `entries_caught`. Applied to NC-D08 as well | P0-B3 data produced |
| **F39** | P0 at 4 days | **P0 = 8 days** (B1 1.5 · B2 0.5 · B3 5.0 · B4 1.0), range 8–10, with the per-build reallocation and the reason compression is dangerous here | R11 table; P0 header; each build's effort line |
| **F40** | P3-B4 at 7 days, on the critical path | **P3-B4 = 12 days**, P3 = 17, range 15–20, itemised | R11 table; P3 header; P3-B4 effort |
| **F43** | The parallelised critical path (now **118** days, C6) assumes 2–3 engineers while every independence claim assumes one author | R11 now names the **three artifacts a second author buys evidence for** (A′, mask path B, arm-2 expectation) at **5.0 person-days**, states the `SAME-AUTHOR` degradation as a **ruling with a test** (`test_same_author_label_is_present_when_authors_match`), and marks the funding question **OPEN — USER DECISION**, blocking nothing but decidable before P1-B3 | R11 |

### Findings recorded but NOT repaired here, and why

- **F1, F9, F13, F14, F24** touch P4/P5 and are repaired in `plan/03-phases-verdict.md`.
- **F12, F16, F17, F37** are P8's; **F6, F21, F25, F32, F44** are P9/P10/P11's; **F11, F29, F35, F41** are
  P12/P14/P15's; **F26, F30** are P13/P12's; **F34** is `00` §3.1's dependency graph; **F33** needs no
  repair by the adversary's own statement. Where one of those repairs needs something from P0–P3, it is
  written above as an obligation (Y9–Y16) so the other owner can check their change against this document
  rather than re-deriving it.
- **F2's other half** — that `TEMPLATE-COMPUTED` must be inadmissible for any predicate reading a cell the
  generator computed, and that `g4_ffr.check()` must raise `UninformativeCorpusError` on a non-empty
  `read_keys ∩ computed_cells` — is P8-B3's. This document supplies `computed_cells` (Y11) and the
  hand-computed filing; it cannot supply the gate.

### One thing this pass could not repair

**F15's residue survives the repair.** Tabling the three lawful readings and rendering
`generator_rule` makes the choice *visible*; `test_mask_matches_what_a_competent_filler_filled` makes it
*falsifiable* — but only against what fillers happened to fill, on a corpus of thirty, and only from P8.
Between day 22 and day ~90 the denominator under every number this product prints is checked by nothing
except two implementations of a rule we wrote. The `PROVISIONAL-UNVALIDATED` label is not a fix; it is the
period being named.

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C1** — `d` is a frozen integer | the P3-B4 gate block, the DECIDED box, P3 exit criterion 2 and the F3 repair row all carry `d = 11`; the formula is retained **as the derivation** and `experiments/G-EVAL/PREREGISTRATION.md` becomes the constant's home | P3-B4 arm table · the two-arm box · P3 exit 2 · F3 row |
| **C4** — P0's gate set | R5a's quotation of `00`'s superseded "16 build gates" is marked historical; `00` now cites this document's 18 | R5a |
| **C6** — the `k = 0` critical path | the two instructions telling `00` to recompute against a `~114` line are discharged; `~114` is named as retired | §0 effort delta · §Y Y14 · F43 row |
| **C7** — arm-2 author test | `test_arm_two_oracle_is_a_different_author` renamed to `test_arm_two_author_is_not_the_evaluator_author`, **4 occurrences** | P3-B4 ×2 · P3 exit 2a · §Y |
| **C8(b)** — the `formula_source` doc | **`docs/RECALCULATION-SOURCE.md` is deleted as a separate artifact**; the rule is a *generated section* of `docs/EVALUATION-CONTRACT.md`, which preserves P5's byte-identity gate | P3-B4 file list · the DECIDED box · P3 exit 2b · F19 row |
| **C9** — the catalogue | **R5a's band table is deleted** — it declared itself normative and four documents wrote different ones. `NC-N07` → **`NC-N16`** (`07`'s → `NC-N40`; `NC-N07` **RETIRED**). Obligation **Y15** discharged and superseded | R5a · P0-B4 id note · §X catalogue · §Y Y15 · F27 row |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
