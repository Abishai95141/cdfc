## What I ran, and what it shows

All commands below are from `/Users/abishaikc/Gift` with `PYTHONPATH=src` and `.venv/bin/python`. Tree state on exit: only `src/cdfc/qualify/g4_ffr.py` is modified, and it was already modified by a parallel session before I started — I touched nothing tracked.

---

# PART 1 — DEFECTS FOUND

### [major] `_write_template_computed` silently drops 292 of the 475 cells its evaluator computes, and the fixture that carries its name is 322/505 not template-computed

`tools/fixtures/synthesise_filing.py:424`:

```python
computed = {
    k: v for k, v in grid.values.items()
    if k in formulas and isinstance(v, (int, float)) and not isinstance(v, bool)
}
```

The evaluator is `Decimal`-native by R4 (`ci/no-float-money.sh` is a live gate precisely because a `float` in a filing is "a value nobody can re-derive"). So this filter — written as `int|float`, which excludes `Decimal` — keeps only the subset of results that happen to land on `int`. Measured, with the real planned inputs:

```
types with REAL inputs: Counter({'Decimal': 258, 'int': 183, 'str': 34})
kept by the isinstance filter: 183 of 475
DROPPED (Decimal/str/None): 292
```

The 322 formula cells that receive nothing keep **the pinned blank's cached zeros and `"NA"` strings**. The consequence is measurable on the committed artifact:

```
$ python scratch/corrector_probe.py fixtures/synthetic/clean__template-computed__fme-q1.xlsx
states: {'NO_PREDICATE': 1, 'FAIL': 285, 'PASS': 189, 'NOT_RUN': 30}
    1. Introduction!D18 filed= 0 should be= 1E+1
    1. Introduction!E75 filed= 0 should be= Trust
```

`TEMPLATE_DIFF` fires on **285 of 475** cells of the filing whose own sidecar reads *"TEMPLATE-COMPUTED by this project's own evaluator. Uninformative for any arithmetic predicate: **the oracle and the system under test are the same function**."* If that sentence were true the number would be 0. It is 285, and the reason is that 322 of the cells were never written by the evaluator at all.

The generator *is* deterministic — I regenerated into scratch and got `aeedbfe18c803061` byte-identical to the committed fixture — so this is not a reproducibility failure. It is a **false provenance sentence on a committed artifact**, and it is load-bearing beyond P9: `docs/measurements/P5-runtime-closure.md:73` publishes *"`clean__template-computed__fme-q1.xlsx` — run state `INVALID`, 349 checks"* against this filing. P9's own tests are honest about it (`test_rel__td_runs_on_a_template_computed_filing_SMOKE_ONLY` asserts only `len(out) == 505`, and `test_nc__R08c` refuses the provenance for the zero-fire claim) — the defect is in the fixture's sidecar and in the generator, not in P9's use of it.

**Repro:**
```
python - <<'EOF'
import sys; sys.path.insert(0,"src"); sys.path.insert(0,"tools/fixtures")
from collections import Counter; from pathlib import Path
import synthesise_filing as sf
from cdfc.calc.evaluate import recalculate; from cdfc.calc.shift import materialise
FME=Path("fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
ctx=sf._load_context(FME); values=sf.plan_inputs(ctx)
formulas={};deferred={}
for sheet,recs in ctx.formulas_by_sheet.items():
    masters={f.si:f for f in recs if f.encoding=="SHARED_MASTER"}
    for f in recs:
        if f.text: formulas[(sheet,f.ref)]=f.text
        elif f.encoding=="SHARED_DEPENDENT":
            mm=masters.get(f.si)
            if mm and mm.text: formulas[(sheet,f.ref)]=materialise(mm.ref,mm.text,f.ref)
            else: deferred[(sheet,f.ref)]="x"
g=recalculate(formulas=formulas,literals=dict(values),formula_source="TEMPLATE",deferred=deferred)
v=[x for k,x in g.values.items() if k in formulas]
print(Counter(type(x).__name__ for x in v))
print("kept:",sum(1 for x in v if isinstance(x,(int,float)) and not isinstance(x,bool)),"of",len(v))
EOF
```

**Fix:** `isinstance(v, (int, float, Decimal))` — the very next function, `_int`, already does `float(str(v))`, which is what the author meant.

---

### [minor] `_writer._set_value` writes an invalid cached string onto formula cells; 64 of 505 derived cells per corpus filing are unreadable by the module's own reader

`src/cdfc/qualify/corpus/_writer.py:31-35` sets `t="inlineStr"` and appends `<is><t>` for **any** string value, including onto a cell that carries `<f>`. What lands on disk after the sanctioned corpus write path:

```xml
<c r="E75" s="48" t="inlineStr"><f t="shared" ref="E75:E84" si="0">F54</f><is><t>Trust</t></is></c>
```

Per ECMA-376 a formula cell's cached string result is `t="str"` with `<v>`; `<is>` is not admissible beside `<f>`. `formula_values()` — 20 lines below in the same file, and the FOREIGN_ENGINE oracle's only reader — looks for `<v>` and returns nothing for these. Measured on `fill_001` through the exact production path (`strip_and_write` → `value_table(SOFFICE, …)` → `write_values`):

```
LibreOffice string-valued derived cells: 64
lost on read-back: 64
all lost are strings: True
```

`write_values ∘ formula_values` is therefore not the identity: 64 of 505 derived cells silently disappear on read-back, every filing, every run. The same asymmetry is in `tools/fixtures/synthesise_filing.py:290` (`_formula_values`), which is why `clean__independently-computed__fme-q1.xlsx` — the corpus the zero-fire claim is founded on — carries LibreOffice's answer for 441 of 505 derived cells and the pinned blank's for the other 64.

Containment, measured: `cdfc.probes.workbook.filed_values` **does** read the `<is>` form (`filed_values(t)[('1. Introduction','E75')] == 'Trust'`), and LibreOffice round-trips it (second pass returns 505 values with `E75='Trust'`), so no predicate evaluation is currently wrong because of it. The exposure is that the writer emits a shape the codebase's own oracle-side reader rejects, and the `_typed` docstring in the same file names *exactly this bug class* ("`formula_values` returned `v.text` … `_set_value` writes a `str` as an inline STRING") as the root cause of the 6 GB hang — the repair went into `_typed` (numbers) and never into `_set_value` (text).

**Repro:** the script under "Part 2 / the fill pipeline" below; the diagnostic line is `lost on read-back: 64`.

---

### [minor] `corpus/blind-fill/fills/README.md` publishes an absence claim its own generator falsifies, and `make blind-probe` does not exist

README line 34-37: *"`tools/corpus/blind_fill_probe.py` consumes them. **It has not yet produced a measurement**: the run exits without output and without a traceback, and the cause was not diagnosed. Treat `docs/measurements/P8-blind-probe.md` as ABSENT, not as zero."*

The probe runs, and its output is byte-identical to what is committed:

```
$ PYTHONPATH=src .venv/bin/python tools/corpus/blind_fill_probe.py
  fill_001: 3754 cells filled, 1 predicate(s) fired
  ... (×5)
wrote docs/measurements/P8-blind-probe.md
$ git status --short docs/measurements/P8-blind-probe.md   # (empty)
```

`tests/relational/test_rel_p9.py::test_rel__the_blind_filled_corpus_fires_on_zero_template_cells` already reads that file and pins `P-0185`. The README's ABSENT declaration is stale in the direction the project cares most about — a false absence claim.

Separately, the probe's own docstring line 5 says `make blind-probe`. `grep -n "blind" Makefile` returns nothing. The tool that runs the only real fill pipeline in the repository has no make target and is in no `make all` path.

---

### [context, not a defect] `ci/no-openpyxl-writer.sh` scans one directory, and any future writer outside it is unguarded

```
$ printf 'import openpyxl\nwb = openpyxl.Workbook()\nwb.save("x.xlsx")\n' > src/cdfc/probes/_audit_tmp_writer.py
$ CDFC_PY=… bash ci/no-openpyxl-writer.sh
no-openpyxl-writer: OK
exit=0
```
(file removed; tree clean)

Registry row 38 is honestly worded — *"nothing under `qualify/` writes a workbook except `surgery.py`"* — so this is not a mis-claim today. It is a fact a filling harness must plan around: **`SCAN="src/cdfc/qualify"` is the whole guard.** A writer at `src/cdfc/repair/` inherits none of the protection that the 3.55 MB data-model part and the 19 `x14` validations currently enjoy.

---

# PART 2 — THE FORWARD-LOOKING ASSESSMENT

## The foundation, inventoried and measured

**The field surface and what constrains it (FME, `make ceiling` numbers re-derived):**

| | |
|---|---:|
| field-surface cells (`unlocked ∧ non-formula`, v3) | **3,747** |
| formula cells in the pinned blank | **505** |
| field-surface cells `TEMPLATE_DIFF` can reach at all (`ceiling`) | **957** (25.5%) |
| field-surface cells bound by ≥1 harvested predicate | **2,320** (61.9%) |
| field-surface cells carrying a *value* constraint — vocabulary, numeric/integer/date bound, or requiredness | **2,244** (59.9%) |

Harvested predicates, all nine prescribed workbooks: **671** — `membership 90 · cross_sheet_equality 196 · sum_identity 129 · same_sheet_equality 51 · integer_bound 45 · numeric_bound 26 · date_bound 22 · conditional_required 12`. FME alone carries 348.

**The write path is real and it is sound.** I ran the full blind-fill pipeline on `fill_001` and instrumented it:

```
inputs: 3754
zip parts base/written: 42 42   missing: []
formula ELEMENTS surviving in the written filing: 505   (blank: 505)
formula values LibreOffice returned: 505
```

Every one of the 42 zip parts and all 505 `<f>` elements survive `strip_and_write` → LibreOffice → `write_values`. The 3.55 MB data-model part and the `x14` validations are preserved by construction (raw-zip copy). This is a working, deterministic, byte-reproducible form-filler already.

## What a FILLING harness could do TODAY with zero new machinery

Concretely: `tools/corpus/blind_fill_probe.py` **is** a filling harness with the output deleted. Line 166 is `target.unlink()`. Remove that line and you have a program that:

1. reads `filler_task.json` — 454 field decisions, each carrying the regulator's own label, declared kind (`list/decimal/whole/date`), operator, bounds, and permitted vocabulary lifted from the workbook's own data validations;
2. expands them mechanically across 2,323 cells via `fill_groups.json` (keyed on `uid`, after the `sheet|column` collapse was caught);
3. defaults the remaining 1,441 cells (`_remainder`, at the declared default);
4. writes them into the pinned blank by raw-zip surgery with every cached formula value stripped;
5. hands the file to LibreOffice to derive all 505 formula cells;
6. writes the derived values back;
7. evaluates all 348 harvested predicates against the result and reports which fired.

Today that produces `1 predicate fired / 348` on all five fills. I checked whether that low number is a construction: it is not — the 1,441 defaulted-to-`1` remainder cells overlap **zero** membership-constrained cells (`membership predicates with >=1 cell filled by the literal 1: 0`), so the single `P-0185` fire is a genuine finding and not an artefact of the default.

So the honest statement of today's fill capability: **a harness can fill an FME return with values that satisfy the form's own declared validations on 2,244 of 3,747 cells (59.9%), derive all 505 formula cells with a foreign engine, and self-check the result against 348 predicates plus `TEMPLATE_DIFF` — and it can prove byte-reproducibility of the whole thing.** The 40% it cannot constrain is where a filler's judgement actually lives (names, addresses, free text), and the system already knows exactly which cells those are.

## What a CORRECTING harness could do today — and what stops `template_diff` proposing the fix

`template_diff` returns a `DiffFinding` carrying `recomputed` for every in-scope evaluable formula cell. Measured across the synthetic corpus:

| filing | findings carrying `recomputed` | FAIL |
|---|---:|---:|
| `clean__independently-computed` | 475 | 0 |
| `formula-overwritten__portfolio-O7` | 426 | 1 |
| `formula-overwritten__pair-portfolio-O7-C182` | 426 | 2 |
| `values-written__50-cells` | 426 | 20 |
| `row-inserted__portfolio-r7` | 426 | 60 |

So it already computes a candidate right-hand side for 426–475 cells per filing. Nothing in the code stops it *emitting* one — `DiffFinding.recomputed` is a public field. **Four things stop it being a correction:**

1. **No writer can restore a formula.** `grep -rn 'SubElement' src/cdfc tools` returns exactly five tags across the whole repository: `is`, `t`, `v`, `row`, `c`. **No code path anywhere creates an `<f>` element.** The dominant fault the flagship detects is F11 — a formula replaced by a literal — and the correct repair is *put the formula back*, which no sanctioned writer can do.
2. **The only writer that could write the value destroys the formula while doing it.** `surgery.py:_mutate_element` removes every child of `<c>` before writing (`for child in list(el): el.remove(child)`), with the comment *"A formula cell being overridden loses its `<f>`: that IS the F11 fault."* Using the "only sanctioned writer" to apply a correction **manufactures the fault the correction was for.** Only `_writer._rewrite`'s `strip_cached=False` branch preserves `<f>` while replacing `<v>` — and that module lives inside G4's independence closure (below).
3. **The recomputed value is only right if the inputs are right, and `template_diff` cannot tell which end is wrong.** `precedents.py` is explicit that a finding at `O7` is *"a statement about the inputs `C7:N7`"*. The evidence that this is not academic: on `row-inserted__portfolio-r7.xlsx` the relation emits 60 FAILs whose proposals are `3. Portfolio!B7 → "NA"`, `L7 → 0`, `O7 → 0`, `G41 → 0`. A corrector acting on those would **blank a filing** in response to a structural shift the relation correctly detected but misattributed. `template_diff` is a corrector for exactly one class — a derived cell that disagrees with its own inputs (F11, and stale carries, `values-written`'s 20) — and it is silent about, and actively misleading on, everything upstream of that.
4. **`degree.py`'s money map is not safe to write against.** The parallel audit confirmed 130 of 223 published `MONEY_MARKER` cells are text columns (`Name of Scheme`, `IFSCA Authorisation Number of Scheme`) licensed by a `(USD Million)` header seven columns away. A corrector that used `tau_for()` to decide "close enough, leave it" would be applying a ±5·n USD-million tolerance to authorisation numbers.

## What is genuinely missing, hardest last

1. **A formula writer.** Create `<f>` (and the shared-formula `si`/`ref` bookkeeping) inside the one-parser-factory rule. `materialise()` already exists to shift a master to a dependent, so the text is derivable; only the serialiser is absent. *Small.*
2. **A `Proposal` type distinct from a `DiffFinding`.** Today a finding says "your filing holds X, the template computes Y". A proposal must additionally carry: which cell it would write, what it would write, whether the write is `value` or `formula`, and — the load-bearing field — **what it assumes** (that the precedents are correct). *Small, but it is the whole honesty surface.*
3. **A provenance stamp for a written filing.** `CorpusProvenance` has six values and none of them means *"partially written by cdfc"*. A filing this system corrected and then evaluated is `SELF_AUTHORED` in every sense the FFR machinery cares about. Needs a seventh value and an entry in `NON_SYNTHETIC`'s complement. *Small, high leverage.*
4. **Discrimination between "the derived cell is wrong" and "an input is wrong".** This is the `row-inserted` problem. Nothing in the design does it; the precedent map gives you the candidate input set (`in_field_surface`, 957 cells) but not a ranking within it. *Medium — this is real research, and the ILP/attrition machinery from P7 is the nearest analogue.*
5. **A corrector-side mutation campaign.** P6 measures *does a predicate detect a seeded fault*. A corrector needs the dual: *does the proposal restore the mutant to the base*. `surgery.py` gives you `differing_parts(a, b)` and a `base_sha256` on every `MutantRecord` — the oracle for "did the correction land" is one function call. This is the highest-value missing measurement and it is cheaper than it looks. *Medium.*
6. **Anything that fills the 40% the harvest cannot constrain.** 1,503 of 3,747 cells carry no harvested predicate at all. Filling those requires the regulation, which is not on disk (D-P7-01) and whose terms of use have not been read. *Hard, and it is a licensing problem before it is an engineering one.*

## The safety constraints this codebase's own design imposes on a writer

- **`plan/05-phases-probes-attestation.md:447`, §0.8: "no repair of any artifact."** Scoped to P9–P11 only, so it is a scope boundary rather than a prohibition — but it is the only ruling on the subject that exists, and there is nothing to override. `grep -rniE "remediat|auto-fix|propose a fix|corrective"` over `plan/`, `spec/`, `docs/`, `SPEC.md`, `DESIGN.md`, `BUILD-PLAN.md` returns **two hits, both quotations of CSSF 24/856 about Luxembourg fund managers**. No phase P0–P15 covers writing.
- **The corpus writer is inside G4's independence proof.** `_writer.py`'s docstring — *"This module imports nothing from `cdfc.calc`, and that is load-bearing"* — is enforced by `g4_ffr.independent()`, whose second conjunct is `generator_import_closure & evaluation_import_closure(cand) == ∅` (`src/cdfc/qualify/g4_ffr.py:165`). A corrector that made `_writer.py` import `cdfc.calc` would make every FOREIGN_ENGINE independence claim false, silently, in the flattering direction. **A corrector must not be built on top of the corpus writer; it must be a sibling that shares the raw-zip primitives and not the module.**
- **`formula_source` has no default** (`EVALUATION-CONTRACT.md:57`, `TypeError` on omission). Any correction derived from the template's formulas must carry `TEMPLATE`; a correction derived from `FILING` is a filer passing their own rewritten check.
- **A written correction is byte-identical in kind to a seeded mutant.** `surgery.py` is the fault injector. The design's whole `K/O` measurement rests on being able to say "this workbook differs from its base in exactly the parts the edits name". Corrections must produce the same record (`MutantRecord`-shaped: base digest, edits with `old_xml` verbatim, `parts_changed` checked against the named set), or the campaign machinery loses its ability to distinguish a repair from a fault.
- **`ItemState` has no state for "corrected".** Eight states, `ITEM_STATE_COUNT = 8`, and `PRECEDENCE` is binding with the rule *"a check that did not run must never be absorbed by one that did."* The analogous corrector rule writes itself: **a cell that was corrected must never roll up as a cell that passed.**
- **The absence discipline applies to the writer too.** The one thing the product sells is that it reports what it did not check. A corrector must report **what it did not propose** — and today the number is knowable exactly: 30 `NOT_RUN` formula cells per FME filing, 2,790 field-surface cells outside `TEMPLATE_DIFF`'s 957-cell reach, and 1,503 cells with no harvested constraint of any kind.

## The smallest honest first step

**`cdfc propose` — a dry-run corrector that writes nothing, on the one fault class the design can actually settle.**

- Emit a `Proposal` for exactly the `DiffFinding`s where `state is FAIL` **and** the filed cell has lost its `<f>` element (the structural F11 test the P5 demo already implements) — i.e. the case where the template's own formula is the authority and no judgement about inputs is required. On `formula-overwritten__portfolio-O7.xlsx` that is 1 proposal; on the pair fixture, 2. On `row-inserted__portfolio-r7.xlsx` it is **0**, which is the correct and honest answer and is why the filter is the deliverable rather than an optimisation.
- Every proposal renders `filed_value`, `recomputed`, `tau`, `degree`, the `evidence_text` `degree.py` used, and the full `bound_cells` set it *assumes* to be correct — because that assumption is the proposal's entire warrant.
- Render beside it, in equal weight and in the same run: proposals emitted, findings deliberately **not** proposed on and why (`inputs may be the error`, `NOT_RUN`, `template defect declared`), and cells outside the 957 ceiling.
- The negative controls, which are the actual point:
  - `test_nc__propose__emits_nothing_on_a_filing_the_product_did_not_compute` — 0 proposals on `clean__independently-computed__fme-q1.xlsx` (475 PASS, 0 FAIL, verified above).
  - `test_nc__propose__emits_nothing_on_row_inserted` — the positive control for the misattribution hazard; it must go **red** if the F11 structural filter is removed, and it will, because the unfiltered relation emits 60.
  - `test_nc__propose__writes_no_bytes` — assert the input workbook's sha256 is unchanged after a full `propose` run.
- No writer. No `<f>` serialiser. No new provenance value. Nothing in `plan/05` §0.8's blast radius, because no artifact is repaired.

That step is worth taking because it is the only one whose oracle already exists and is already measured, and because it forces the two questions that decide whether the corrector is a product or a liability — *which cell is actually wrong*, and *what does the system refuse to propose* — to be answered in code before a single byte is written.