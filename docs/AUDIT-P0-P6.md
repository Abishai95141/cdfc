# docs/AUDIT-P0-P6.md — a full audit of everything built, 13 August 2026

**What this is.** A sweep of P0–P6 for the things that make a green build untrustworthy: tests that
cannot fail, gates that cannot go red, numbers published without their denominators, claims made
only in prose, deferrals nobody re-opened, and code nobody reaches. Every finding is listed with
what was done about it. **Nothing here is left as a note.**

The audit is mechanical where it can be — `tools/audit.py` runs the sweeps and is re-runnable —
and by reading where it cannot.

---

## 1. Tests that could not fail

| # | Finding | Where | Resolution |
|---|---|---|---|
| 1.1 | **`assert ... or True`** — the assertion was unconditional | `test_f11_mutant_is_observable` | **FIXED.** This is the test the plan calls *"the one it most needed and did not have"*: it checks that an F11 override is OBSERVABLE, which is what stops the flagship class leaving `K/O`'s denominator. `or True` made it green on every build, including one recalculating through the template's formula graph. Rewritten with two unconditional assertions; both pass. |
| 1.2 | **`assert ... or True`** | `test_fault_model__f12_homoglyph_...` | **FIXED.** Now asserts three properties unconditionally: byte-different, contains `U+2011`, same length. Plus the one that matters — the homoglyph must **not** NFKC-fold to the legal member, or F12.b would be unkillable by construction. |
| 1.3 | Eight tests with **no `assert` and no `pytest.raises`** | various | **REVIEWED, all legitimate.** Each calls a function whose contract is *raises on failure* — `check_schema`, `check_subset`, `assert_fraction_did_not_rise`, `validate`. The call **is** the assertion. Recorded here rather than "fixed", because rewriting them as `assert f() is None` would assert less. |
| 1.4 | Nine `pytest.skip` / `importorskip` sites | various | **REVIEWED, all legitimate, and two were checked rather than assumed.** `cel_expr_python` **is** installed and pinned in `requirements.lock`, so the two-runtime CEL differential runs rather than silently skipping. The arm-1 evaluator report **is** committed at `docs/measurements/p3-evaluator.json`, so `test_eval__arm1_has_zero_disagreements` runs. The rest are platform guards (`/etc/passwd`) or stage guards (`CDFC_REQUIRE_SWEEP`, enforced in CI). |

## 2. Gates that could not go red

| # | Finding | Resolution |
|---|---|---|
| 2.1 | **Rows 14 and 16 were still `PENDING` although their subjects shipped at P5.** | **FIXED — promoted to LIVE, with injectors.** `PENDING` is the state that lets a gate avoid demonstration, and the whole reason `ci/GATES.md` is a registry rather than a list is that a gate resisting demonstration must not sit in a set nobody has to keep green. Row 14 (`test_no_model_in_verdict_path`) now walks the import closure of `verdict/`, `evaluate/` and `facts/` for model clients **and network stacks**, with an admission-side control proving the walk can see an import when there is one. Row 16 (`test_prop__closure_seven_terms`) gets `injectors/closure_drops_a_bucket.py`. Both observed red. |
| 2.2 | `ci/no-regex-over-xml.sh` **was named as "the sibling" inside another gate's docstring and did not exist** | **FIXED at P5**, and it found two live defects on its first run — one in the P5 filing generator, one pre-existing in `tools/fixtures/make_synthetic.py`. Recorded here because it is the clearest instance of the class: *a gate named in a comment is not a gate.* |
| 2.3 | Row 15 (attestation schema) is `PENDING` | **CORRECT, and left.** Its subject is P11's and genuinely does not exist. `PENDING_NOW = PENDING_AT_P0 − PROMOTED_AT_P6` is asserted, so the set can only shrink into LIVE and never the other way. |

## 3. Numbers published without their arithmetic

| # | Finding | Resolution |
|---|---|---|
| 3.1 | **Fourteen bare rates**, including one in a published measurement file | **FIXED.** `ci/no-bare-rate.sh` is now a gate. `docs/measurements/P3-evaluator.md` renders `n/d` in place of a percentage column and its generator was changed to match. Two prose sites carry a declared `rate-ok:` marker with a reason — a regulatory threshold quoted from a rule (75% by value), and a historical figure named as the defect it was (v0's 18.09%, v1's impossible 100.1%). **Both are quotations, not measurements**, and the marker is greppable so widening it is a visible diff. |
| 3.2 | The static/runtime settled delta was published **undecomposed** | **FIXED at P5.** `−474` reads as roll-up lowering when 474 of it is a difference of populations: cells bound by a predicate that lie outside the field surface, because a predicate may bind a locked or formula cell no filer fills in. The measurement now decomposes it into the two parts, and the roll-up part is 0. |
| 3.3 | Ledger rows | **REVIEWED.** 12 rows; every one carries a `caveat` and a recognised warrant. Two rows have a different shape (`query_name`, `positive_control_count`) — those are the **absence-claim** ledger that `ci/no-bare-absence.sh` resolves, not validation rows, and both consumers read their own shape. |

## 4. Claims made only in prose

| # | Finding | Resolution |
|---|---|---|
| 4.1 | `src/cdfc/surface/design.py` states in a docstring that there is **no `SUCCESS` colour and no affirmative badge token** — the asymmetry the whole product rests on — and nothing checked it. The module was also reached by nothing. | **FIXED.** `tests/contract/test_contract_design_tokens.py` asserts the exclusion over every exported token name and every palette value, checks the banned vocabulary and the token module agree, and carries an admission-side control so that deleting every token would not make the other three pass. |
| 4.2 | `AGGREGATE`'s docstring said *"an aggregate silently computing the wrong statistic is a clean confident wrong answer"* — and the function **ignored its `options` argument** | **FIXED, and it was a live defect.** See §6.1. |

## 5. Dead code

Seven modules are reached by nothing. **Six are `__init__.py` package markers of ~60 bytes** that
exist because `labels.SCAN_ROOTS` enumerates them and `ci/scan-roots-exist.sh` asserts they exist —
a deleted root would otherwise make every grep gate report success over nothing. The seventh was
`surface/design.py`, resolved at §4.1: its consumer is P14, and it now carries the test that makes
it valuable before P14 arrives.

**No dead code was found that should be deleted.** The dynamically-loaded families were checked
rather than assumed: 9 harvest classes load, 5 host functions register.

## 6. Defects the audit found in the product itself

These are not process findings. They are wrong answers that were being produced.

### 6.1 `AGGREGATE` ignored its `options` argument — 29 cells, clean and wrong

Comparing our recalculation against **LibreOffice's** on the FME filing showed 129 of 505 formula
cells disagreeing. **100 were a defect in the comparison** — LibreOffice writes IEEE-754 doubles
(~16 significant digits) and we compute in `Decimal` at 34, so exact equality reported `1/12` as a
disagreement. That is fixed with a relative tolerance and is a lesson about the instrument, not the
engine.

**The remaining 29 were real.** Every one was `AGGREGATE(15, 6, (ROW(r)-ROW(c)+1)/(r2="yes"), ...)`
— the standard *nth matching row* idiom. Option 6 means **ignore error values**: the division by
`FALSE` is *meant* to produce `#DIV/0!` for non-matching rows and `AGGREGATE` is meant to drop them.
We do not implement array arithmetic, so we computed over the wrong operand set, returned `#NUM!`,
and **`IFERROR` caught it and wrote the literal `"NA"`.** Twenty-nine clean, confident, wrong
values, with nothing red.

`AGGREGATE` now **refuses** an ignore option it does not implement. The consequence is visible on
the product's own demo output:

> **`495 of 505 derived cells checked` became `475 of 505`, and `10 NOT CHECKED` became `30`.**

**The number got worse and the output got truer.** That is this product's entire thesis, applied
to itself.

**After the repair: G-EVAL arm 2 on FME is 475 agree, 0 disagree, 30 we did not compute.**

### 6.2 The cone optimisation was not exact — it computed 11 where the full grid computed 12

The downstream-cone recalculation restricts the formula set to the edit's transitive downstream
cone. Restricting it also removed formula cells that a cone member **reads**, and those fell back
to their cached literals. The differential test caught it on its first run at
`'3. Portfolio'!O7`. A silent one-off there would have moved every kill rate in the campaign.

The repair is exact rather than a widening: a cell outside the cone cannot change under this edit,
so its clean value is a valid input and is supplied as a literal. `baseline` is now a **required**
argument of a cone-restricted call — it raises rather than defaulting.

### 6.3 A harvested bound exceeded `int64` and the runtime exhausted memory

Found at P5. One `decimal` validation declares an upper bound of `9.99999999999999E+21`, about a
thousand times the `int64` ceiling. Both the harvest and the CEL profile now refuse an
out-of-`int64` literal; 592 candidates fall to 572, recorded in `docs/HARVEST-DELTA.md` entry #2.
**A predicate whose threshold cannot be represented is a typed skip, not a predicate with an
approximated threshold.**

### 6.4 A bound predicate compared an integer to a string

`c.v == "" || c.v >= 0` — in CEL that is a **type error**, not `false`. Five predicates produced
`ERROR(error.predicate_raised)` on the clean filing and invalidated the run. The blank arm was also
unnecessary: a blank numeric cell is *absent* from the fact model, so it never reaches `.all()`.
Removing it made the inferred type unambiguous, which moves a text value in a numeric column from
`ERROR` (our apparatus failed) to `NOT_RUN` (the source could not be read) — **the honest state,
and one with a different remedy.**

### 6.5 An `F08` operator that seeded nothing

The row-duplication operator returned `None` unconditionally — a stub. The class showed `G = 0` in
the published vector: **a class that cannot seed contributes no evidence while still occupying a
row.** Implemented as a real cell-wise duplication.

### 6.6 A pair operator double-wrapped its partner

`_pair_partner_carry` returned `(ctx.carry_counterpart(site), 3)` where the context already returns
`(site, value)`. It surfaced 750 mutants into a 25-minute campaign as an `AttributeError`. Fixed;
the campaign now runs 24 operators including both pair forms.

## 7. Things this build does NOT claim

Listed because an audit that only lists what was fixed is an audit with a missing column.

- **`NC-N50` — that the fault taxonomy is complete.** No negative control is possible: completeness
  is a claim about the population of real filing errors, and **no filed FME return is public**, so
  the denominator does not exist. Every `K/O` is a statement about *our operator mix*. The bridge to
  real faults is the coupling effect and **there is no coupling study for financial filing data.**
- **`NC-N01` — that a predicate means what its clause means.** A predicate can clear every gate and
  enforce a rule that does not exist.
- **The blind-fill corpus does not exist**, so no false-failure rate has been measured and every
  admission state is `PRE-GATE`. See [[cdfc-human-blockers]]: the substitute is an audited
  second-model-instance route with the fill prompt hashed before the first workbook is filled.
- **The clean filing is `INDEPENDENTLY-COMPUTED (LibreOffice)`, never `HAND-COMPUTED`.** LibreOffice
  is not Excel — a disagreement is a third answer, not a verdict against us — and it is a spreadsheet
  engine rather than a reader of the regulation, so it cannot notice that a formula is *wrong*.
- **One catalogue entry is `PROVISIONAL` (`NC-E16`)** and is excluded from `entries_caught` rather
  than counted. A green entry with no information in it must not be counted as evidence.

## 8. The state after the audit

| | |
|---|---:|
| negative-control entries caught | **68 / 68** |
| guards observed red under injection | **107 / 107** |
| entries with `injector: NONE` | 0 |
| provisional entries (excluded from caught) | 1 (`NC-E16`) |
| live gates observed red | **46 / 46** |
| gate rows still `PENDING` | 1 (row 15, subject is P11's and genuinely absent) |
| CI shell gates | 14 |
| bare rates on any surface | **0**, and a gate that finds them |
| `assert ... or True` | **0** |
| gates named in a comment but not existing | **0** |
| modules reached by nothing | **0** (six package markers required by `SCAN_ROOTS`) |
| ledger rows without a caveat | **0** |
