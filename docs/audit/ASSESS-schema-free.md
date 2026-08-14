Tree check before I report: `git status --short` shows only ` M src/cdfc/qualify/g4_ffr.py`, which is the *concurrent* audit's live injector (`recomputed = record['clean_corpus_independent_of_predicate']  # INJECTED`), not mine. I modified no file in the repo; all my probes were read-only scripts in the scratchpad.

---

# PART 1 — DEFECTS

## D1 [major] The harvest's central anti-coverage-lie rule is false for 1,060 of the corpus's 1,495 formula cells, and the two skip kinds written for the dominant case were never wired

`src/cdfc/predicates/harvest.py:22` states rule 2 of the module contract:

> **Every formula the class set cannot express becomes a typed `SkipRecord`**, with the sheet, the cell and the detail. Never a silent omission: an undeclared suppression is a coverage lie.

`docs/measurements/P4-harvest-distribution.md` repeats it verbatim as the header of the published skip table ("An undeclared suppression is a coverage lie. Every construct the class set cannot express is a typed `SkipRecord`…") and publishes **302** skips across the nine workbooks.

Measured:

```
PYTHONPATH=src .venv/bin/python -c "
from pathlib import Path
from cdfc.predicates.harvest import harvest, _load_context
from cdfc.predicates.harvest_classes._shared import iter_formulas
t=s=0
for f in sorted(Path('fixtures/prescribed').glob('*.xlsx')):
    ctx=_load_context(f); r=harvest(f)
    cells={(a,b) for a,b,_ in iter_formulas(ctx)}
    acct={(v[2],v[3]) for v in r.constructs.values()} | {(k.sheet,k.ref) for k in r.skipped}
    t+=len(cells); s+=len(cells-acct)
print('corpus formula cells:',t,' neither obligation nor SkipRecord:',s)"
```
```
corpus formula cells: 1495  neither obligation nor SkipRecord: 1060
```

Per workbook (formula cells / carrying an obligation / carrying a SkipRecord / **carrying neither**):

| workbook | formula cells | obligation | SkipRecord | **SILENT** | what the silent ones are |
|---|---:|---:|---:|---:|---|
| ALR | 645 | 25 | 0 | **620** | `ROUND(...)` ×558, `+B13-B22`, `IF` ×9 |
| AL monthly | 161 | 6 | 0 | **155** | `+D9+1` chains |
| **Draft ACAC** | 112 | 0 | 0 | **112** | `A9+1` chains |
| EDR 1 | 0 | 0 | 0 | 0 | — |
| IBU | 7 | 6 | 0 | **1** | external-workbook carry `'[1]General Information'!B3` |
| Annual Reporting | 0 | 0 | 0 | 0 | — |
| ITFS | 32 | 14 | 2 | **18** | `E43-E48` |
| **FME** | 505 | 302 | 59 | **144** | `IFERROR` ×130, `IF` ×14 |
| CMI | 33 | 23 | 0 | **10** | `IF(COUNTIF(...))` |

The mechanism is a bare `continue` at the head of every formula class — e.g. `src/cdfc/predicates/harvest_classes/sum_identity.py:26` `if not SUM_CALL.match(body): continue`, plus `if src is None or ":" not in inner: continue` at line 38. A body the class cannot match is dropped by all nine classes in turn and nothing records it.

**The self-evidencing part.** `SkipKind` at `src/cdfc/predicates/harvest.py:44-52` declares seven kinds. Two of them — `iferror_wrapper` and `if_conditional_carry` — appear **nowhere else in the repository**:

```
$ grep -rn "iferror_wrapper\|if_conditional_carry" src/ tools/ tests/
src/cdfc/predicates/harvest.py:48:    "iferror_wrapper",
src/cdfc/predicates/harvest.py:49:    "if_conditional_carry",
```

Those two names are exactly FME's silent pile: 130 `IFERROR` + 14 `IF` = 144. The vocabulary for declaring them was written and never connected.

Reproduction naming a specific cell:
```
PYTHONPATH=src .venv/bin/python -c "
from pathlib import Path; from cdfc.predicates.harvest import harvest
r=harvest(Path('fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx'))
print([s for s in r.skipped if s.ref=='C100'], [k for k,v in r.constructs.items() if v[3]=='C100'])"
# [] []
```
`'1. Introduction'!C100 = IFERROR(INDEX($C$54:$C$63, _xlfn.AGGREGATE(15,6,…)))` produces neither.

**Why this is the product's own failure mode.** These cells are formula cells, so they are *excluded from the field surface by construction* (`styles_mask.build`, rule 5: `if has_formula … continue`). They therefore appear in no `noPredicate` count, no `settled_fraction` residue, and no run-time coverage declaration either. The harvest skip table is the only place a reader could ever learn they exist, and 1,060 of them are not in it. For a checker whose differentiator is *reporting what it did not check*, this is a 3.5× understatement of the declared weak pile.

## D2 [minor] NC-Q46's guard — "the weak pile is dropped instead of counted" — is satisfied by any non-empty skip list, so it cannot see D1

`tests/negative/catalogue.yaml:643-657` registers NC-Q46 with `measured_instance: "58 formulas on FME are outside the class set"`. Its `flips: true` guard is:

```python
# tests/negative/test_nc_predicate.py:167
def test_nc__Q46_a_construct_outside_the_class_set_is_recorded() -> None:
    res = harvest(FME)
    assert res.skipped, "FME carries constructs the class set cannot express; none was recorded"
    assert res.skips_by_kind.get("function_outside_vocabulary", 0) > 0
    for s in res.skipped: assert s.sheet and s.ref and s.detail
```

It asserts the skip list is non-empty and that at least one `function_outside_vocabulary` exists. It never compares the skip set against the formula set, so 144 undeclared FME drops (and 620 on ALR, where the skip list has **2** entries and would still be non-empty at 1) are invisible to it. The second `flips: true` guard, `test_harvest__the_weak_pile_is_typed_and_counted` (`tests/unit/test_harvest_classes.py:80-104`), asserts only that *the wildcard COUNTIF* is a declared skip. The `flips: false` positive control (`test_nc__Q46b`) uses EDR-1, which has **zero formulas** — so it discriminates nothing about formula handling.

Reproduction: `PYTHONPATH=src .venv/bin/python -m pytest tests/negative/test_nc_predicate.py::test_nc__Q46_a_construct_outside_the_class_set_is_recorded -q` passes on HEAD, where the defect it names is live at 144 instances.

Related, and unrecorded: `docs/HARVEST-DELTA.md` entry #1 publishes a per-workbook table with a `v0 weak` column — ALR **234**, FME **68** — against `P4-B4 skips` of **2** and **178**. The entry's "Why it moved" section explains the FME *increase* and says nothing about ALR's declared weakness collapsing from 234 to 2 while its candidate count rose 19→32. That movement is the silent-drop regression, and it moved in the flattering direction with no recorded reason, in the file whose own header says "a number that moves with no recorded reason does not get past this file."

## D3 [minor] `resolve_builder`'s "deterministic in the template" is false — the relation builders take no template and open no workbook

`src/cdfc/probes/relations/registry.py:91`:
```python
builder: str = ""     # a dotted callable that renders `expr` per template
```
and `resolve_builder`'s docstring (line 130-138): *"Long CEL is GENERATED from the pinned blank, never typed into YAML… The builder is deterministic in the template, so `catalogue.yaml` stays readable."*

The call site is `out = fn()` — zero arguments (line 148). `partition.build()`, `schemes.build()` and `prior_period.build()` all have signature `() -> dict[str, str]` and read no file. Every coordinate is a module-level literal transcribed by hand from FME: `partition.py:42-52` fixes `SHEET = "4. Investors"`, `CATEGORY_FIRST_ROW = 21`, `ACCREDITATION_FIRST_ROW = 42`, `SCHEMES = 10`, `CATEGORY_AMOUNT_COL = "AA"`. The expression is generated *instead of hand-typed*, which is a real benefit; it is not generated *from* anything.

Reproduction:
```
PYTHONPATH=src .venv/bin/python -c "
import inspect; from cdfc.probes.relations import partition
print(inspect.signature(partition.build))   # ()
print(partition.build()['expr'][:80])"
```

## D4 [minor] `tools/fixtures/value_deletion.py` — "Built here, imported by P9-B2" — is imported by nothing, and no value-deletion transform is ever applied to a real filing

`tools/fixtures/value_deletion.py:2`: *"P5-B4 — the value-deletion transform generator. **Built here, imported by P9-B2.**"* `src/cdfc/probes/driver.py:17`: *"`tools/fixtures/value_deletion.py` already generates those transforms for P5, so the generator costs nothing new."* `plan/03-phases-verdict.md` X7 makes it a cross-phase requirement.

```
$ grep -rn "value_deletion" . | grep -v '^\./\.git/' | grep -v pyc
plan/10-repair-verification.md:231 …
plan/03-phases-verdict.md:1401,1542,1550,1668,1837,1891,1990,2015 …
src/cdfc/probes/driver.py:17 …
```
No Python file imports it. `tests/property/test_prop_settled_fraction.py` builds its own synthetic `RunCell` lists and openly records the deviation ("The property is stated over the ARITHMETIC… because that is where the hole was") — that half is recorded and fine. But the same docstring then says *"The REAL pipeline is exercised on the same claim in `tests/golden/test_p5_runtime.py`, where a run takes tens of seconds and three cases are affordable."* There is **one** such test, `test_golden__the_seeded_run_does_not_raise_the_fraction`, and it compares the clean filing against the **F11 formula-override** mutant — a filing that is not emptier in any cell. No test anywhere applies a value deletion to a real workbook and re-runs the pipeline. The anti-gaming property that D-P5-05 calls a no-fallback exit criterion has never been evaluated end-to-end against the transform it was specified over.

Reproduction: `grep -n "def test" tests/golden/test_p5_runtime.py` → 8 tests, none deleting a value; `sed -n 82,84p tests/golden/test_p5_runtime.py`.

## D5 [minor] The P9 execution vehicle has never evaluated a relation against a fact tree

`ProbeMachine` / `run_probes` (`src/cdfc/probes/driver.py:96-196`) take `evaluate` as a caller-supplied callable. Every call site in the repository supplies a stub and `state=None`:

```
$ grep -rn "run_probes\|ProbeMachine(" tools/ src/ tests/ | grep -v pyc
tests/unit/test_probe_driver.py:50,57,74,93,110,115   evaluate=_broken / _held, state=None
tests/determinism/test_det_probes.py:42,43,57         evaluate=lambda _r,_s:(True,("S!A1",),"")
src/cdfc/probes/driver.py:96,182                      (definition)
```

Nothing in `src/` or `tools/` constructs a `ProbeMachine`. This is *partly* recorded — `docs/measurements/P9-relation-attrition.md` publishes that `qualify()` raises before G0 for every relation and that no relation is admitted. But `docs/measurements/P9-relation-runnability.md` publishes a table asserting `FILING_AND_BLANK | 1 | runnable` and `FILING_ONLY | 2 | runnable`, which reads as an execution claim and is backed by no execution. The measurement that would settle it: a single call of `run_probes` with a real `evaluate` bound to `CelRuntime` over `fact_set_for(clean_filing, FME)` — which would also, incidentally, be the first test of whether R-02's 80-key precondition holds on the reference filing.

Also stale: `obligations.yaml:5` says "572 of them today" against the published 571.

---

# PART 2 — IS IT SCHEMA-FREE? **Measured: yes at the induction layer, FME-wired only in the harness.**

This is the strongest part of the build, and it is stronger than I expected. I ran every stage over all nine workbooks.

## The field surface — genuinely induced, 7/9, and the two failures are honest

`build(blob, Rule.V3)` on each of the nine:

| workbook | `n_cells` | sheets | source |
|---|---:|---:|---|
| ALR | 1599 | 9 | styles.xml cellXfs path A |
| AL monthly | 3537 | 4 | " |
| **Draft ACAC** | **None** | 13 | *not derivable — template ships no protection mask* |
| EDR 1 | 162 | 3 | " |
| IBU | 459 | 8 | " |
| **Annual Reporting** | **None** | 9 | *not derivable — template ships no protection mask* |
| ITFS | 481 | 2 | " |
| FME | 3747 | 10 | " |
| CMI | 2255 | 18 | " |

Rule 6 fires *before* rule 5 (`styles_mask.py:151`) so a stray unlocked style id cannot manufacture a small answer from a maskless workbook, and `n_cells=None` propagates to `compute() -> None` (`settled_fraction.py:142`) — the fraction is `null`, never `0`. `docs/measurements/p2-field-surface.json` publishes `derivable: 7, not_derivable: 2`. Nothing here is FME-shaped.

## The harvest — induced, runs on all nine, distribution recomputes exactly

`harvest(blob)` yields, at HEAD: ALR 32, AL 16, ACAC 0, EDR 1, IBU 10, Annual 0, ITFS 25, FME 348, CMI 139 = **571**, matching `docs/measurements/P4-harvest-distribution.md` row for row. Vocabularies resolve from each blank's own dropdown ranges (`resolve_vocabulary`, `harvest.py:308`); keys come from `cel_path(sheet, ref)` (`harvest.py:120`), which is a pure function of coordinates and carries no per-form knowledge. `cel_segment` even handles the `1. …` sheet-name family generically. The two zero-yield workbooks are published, with a row, not omitted.

## The precedent map and ceiling — runs on all nine

`build_precedent_map(blob, reading=...)` at all three readings, all nine, no exceptions, deferred=0 and incomplete=0 everywhere:

| workbook | ceiling (transitive) | field surface | unreachable formula cells (lexical→transitive) |
|---|---:|---:|---|
| ALR | 914 | 1599 | 155 → 2 |
| AL monthly | 1072 | 3537 | 56 → 44 |
| Draft ACAC | 0 | 0 | 112 → 112 |
| EDR 1 | 0 | 162 | 0 |
| IBU | 1 | 459 | 1 |
| Annual | 0 | 0 | 0 |
| ITFS | 40 | 481 | 8 → 5 |
| **FME** | **957** | **3747** | 115 → 0 |
| CMI | 167 | 2255 | 0 |

FME's 957/3747 reproduces the published number exactly. Worth noting for honesty's sake: the `value` reading differs from `lexical` on **FME only** (30 cells); on the other eight they are byte-identical. The published page already says all three readings agree on the ceiling and calls that out — so this is a recorded property, not a finding, but it does mean the shape-only-argument distinction (`ROW(D54)`) has instances in exactly one workbook.

## A full run — executes on all nine, and only the harness is FME-wired

`src/cdfc/measure/p5_run.py` is hard-wired: `FME` at line 33, `fme_harvest()`, `fme_surface()`, and `run_filing(filing)` calls `facts=fact_set_for(filing, FME)` at line 126 — the `filing` argument is a parameter, the **template is a constant**. `make run-fme` is the only run target; `cdfc run` still exits 2 (already in the confirmed list).

But the wiring is the *only* obstacle. Re-assembling `execute(...)` with a per-template harvest/surface/facts — a 30-line script, no changes to `src/` — runs all nine end to end:

| template (filed against itself) | run_state | checks | states | run cells |
|---|---|---:|---|---:|
| ALR | VALID | 32 | PASS 16 · OOS 8 · NOT_RUN 8 | 1599 |
| AL monthly | VALID | 16 | PASS 9 · **FAIL 1** · NOT_RUN 6 | 3537 |
| Draft ACAC | VALID | 0 | — | 0 |
| EDR 1 | VALID | 1 | PASS 1 | 162 |
| IBU | VALID | 10 | PASS 4 · OOS 6 | 459 |
| Annual | VALID | 0 | — | 0 |
| ITFS | VALID | 25 | PASS 11 · **FAIL 1** · NOT_RUN 13 | 481 |
| FME | VALID | 348 | PASS 291 · OOS 33 · NOT_RUN 24 | 3747 |
| CMI | VALID | 139 | PASS 106 · **FAIL 10** · NOT_RUN 23 | 2255 |

Script at `/private/tmp/claude-501/-Users-abishaikc-Gift/894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad/genrun.py`. Binding, pre-flight, selection, roll-up and closure all completed on eight non-FME templates with no per-form input.

## Every FME-specific literal in `src/`, classified

I grepped `src/` for literal sheet names, cell refs and counts.

**Executable and FME-specific (3 places):**
1. `src/cdfc/measure/p5_run.py:33` — `FME` constant; lines 81/86/126 make the whole harness single-template. This is the one that matters.
2. `src/cdfc/measure/p6_kill.py:20,38,40` — imports `FME` from p5_run; the kill measurement is FME-only.
3. `src/cdfc/probes/relations/{partition,schemes,prior_period,basis}.py` — hand-authored P9 relations with literal sheets, columns and row bands (`SHEET = "4. Investors"`, `CATEGORY_FIRST_ROW = 21`, `basis.py:37-41`'s `("3. Portfolio", 72, 99)` bands). `RelationSpec` has **no template-scope field**, so nothing in the type system stops R-02 being applied to ALR.

**Curated-from-FME vocabularies that are generic in form but were tuned on one workbook:**
- `src/cdfc/probes/degree.py:50-72` — `MONEY_MARKERS`/`COUNT_MARKERS`/`RATIO_MARKERS`/`DATE_MARKERS`, with the comment "Every string below appears verbatim in the FME workbook." These are IFSCA-idiom strings, not FME coordinates, but their coverage on the other eight is unmeasured and unpublished.
- `src/cdfc/ingest/competence.py:56-66` — nine template sha8s. A corpus pin, correctly generalised from n=1 to nine by `agreement_matrix.py`, documented at line 80.

**Not found:** zero literal counts in executable code paths. `3747`, `957`, `505`, `348` appear only in docstrings and prose. `registry.CATALOGUE_SIZE` is read from the file. `obligations.yaml` is empty by design. There is no per-form field list, no per-form sheet map, no hand-written schema file anywhere in the repository.

## The honest one-line answer

**Induced in fact, not merely in principle — for the field surface, the fact-model keys, the vocabularies, the predicates and the precedent map, all five demonstrated on eight workbooks the system was not tuned on.** FME-wiring is confined to (a) the P5/P6 measurement harness, which pins the template as a constant, and (b) the P9 relation layer, which is hand-authored per-form by design and is currently admitted for zero relations anyway.

**What it would take to make it general:** change `run_filing(filing, *, template=FME)` in `src/cdfc/measure/p5_run.py` to take the template as a parameter and replace the three `lru_cache`d FME globals with `lru_cache`s keyed on the template path — roughly 20 lines, no change to any induction module. Then add a `templates: [sha256]` field to `RelationSpec` so a hand-authored relation declares which blank it is about, and have `to_envelope` refuse a mismatch rather than relying on `has()` returning false. The rest already works.

**The caveat that limits the claim, and it is D1.** "Schema-free" here means *no hand-written schema*, and that is true. It does not yet mean *complete over the blank*: on the eight non-FME workbooks the harvest converts 435 of 1,495 formula cells into obligations or declared skips and drops the other 1,060 without a record. On ALR the system induces a 1,599-cell surface and 32 predicates from a workbook containing 645 formulas, and its published weak pile is **2**. Generality across forms is real; per-form depth is not what the skip table currently says it is.