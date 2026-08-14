# The Report, Assessed Forward

Working tree left as found. One file, `src/cdfc/qualify/g4_ffr.py:254`, carries a live `# INJECTED` edit from the audit running alongside me — not mine, not reverted.

---

## 1. What the report contains TODAY

**There is no report.** `src/cdfc/surface/` is 164 lines across four files. `render.py`, `band.py`, `inline.py`, `admission.py`, `openitems.py`, `report.css`, `report.js` — every file P14-B1 names — do not exist. `report.html.j2` is nine lines, and **jinja2 is not a declared dependency and is not installed**:

```
$ .venv/bin/python -c "import jinja2"
ModuleNotFoundError: No module named 'jinja2'
```

`cdfc run` exits 2. `cdfc attest`/`verify` exit 2. `src/cdfc/attest/` is one docstring line.

So today the report a user receives is **stdout from two demo scripts**, and that is the whole product surface:

```
$ PYTHONPATH=src .venv/bin/python tools/demo_template_diff.py
  1 formula cell(s) overwritten with a literal
    FAIL  3. Portfolio!O7
          the template computes  = SUM(C7:N7)  …  the filing instead holds the literal 999999
          method TEMPLATE_DIFF · warrant DETERMINISTIC
  475 of 505 derived cells checked
  30 NOT CHECKED, each with a declared reason:
       30  unimplemented
  Both counts carry equal weight. …It does not state that the filing is correct.

$ PYTHONPATH=src .venv/bin/python tools/demo_predicate_run.py
CONTROL — the filing untouched
  ran 160   passed 160   findings 0   did not run 21   errored 0
SEEDED — one carry target changed by one unit
  ran 160   passed 159   findings 1   did not run 21   errored 0
    P-0055  2. Summary!H5 4. Investors!AB21
```

Neither renders an admission state, a denominator rule, a settled fraction, a template digest with its validation state, or a Wilson interval. The `SettledFraction` object — the one carefully-built thing — reaches a human only through `docs/measurements/P5-runtime-closure.md`, which is a documentation page, not the report.

**After P11 and P14** it becomes: one self-contained `report.html` (hero pair, stacked band, failure items, unchecked panel with remedies, residue exhibit, open-items with ages, FFR columns), plus `attestation.json` (in-toto/DSSE, Ed25519, integers only) and `run.jsonl`, all three byte-identical on a second machine, plus declared-lossy OSCAL and RO-Crate projections. That is 22 engineer-days of specified-but-unwritten work, and every P14-B1 gate (SG1–SG4) that would make it honest is unwritten too.

---

## 2. Is the coverage declaration structurally incapable of an all-clear? **No — and the gate that claims otherwise is proven on an artifact nobody renders.**

`ci/no-green-tick.sh` scans **exactly four files**:

```
$ PYTHONPATH=src .venv/bin/python -c "…rglob over SURFACE_ROOTS…"
no-green-tick scans 4 files: ['src/cdfc/surface/labels.py', 'src/cdfc/surface/design.py',
 'src/cdfc/surface/__init__.py', 'src/cdfc/surface/templates/report.html.j2']
```

`ci/GATES.md:28` registers row 1's subject as *"no all-clear glyph or phrase **on a user surface**"*, and its `broken_build` as *"`injectors/green_tick.py` writes a check mark into `report.html.j2`"*. `injectors/__init__.py:149` confirms: `GreenTick.apply()` appends `<p class="ok">All clear ✅</p>` to a Jinja template with no renderer, no engine installed, and no reader. NC-CI03 is `flips: true`, `status: active` on that evidence.

The gate's registered claim is about user surfaces. What was measured is that a grep sees a string in a 9-line file.

**Reproduction — an explicit all-clear on the live surface, every gate green:**

```bash
# insert into tools/demo_predicate_run.py before print("\n---"):
#   print("\n  ✅ ALL CLEAR — no issues found. Verified clean, fully compliant.")
$ CDFC_PY=$PWD/.venv/bin/python PY=$PWD/.venv/bin/python make greps
no-green-tick: OK          no-bare-absence: OK        no-bare-rate: OK      … (14/14 OK, rc=0)
$ PYTHONPATH=src .venv/bin/python -m pytest tests/golden tests/contract tests/negative/test_nc_ci.py -q
159 passed
$ PYTHONPATH=src .venv/bin/python tools/demo_predicate_run.py | tail -4
  ✅ ALL CLEAR — no issues found. Verified clean, fully compliant.
```

The same injection into `src/cdfc/verdict/reasons.py` (a declared `SCAN_ROOT`, but not a `SURFACE_ROOT`) is likewise invisible.

Credit where earned: `tests/golden/test_template_diff.py:57::test_golden__the_output_contains_no_banned_surface_token` **does** scan `demo_template_diff.py`'s real stdout against `banned_tokens()`, and it went red under my injection. That is a genuine, discriminating control. It covers **one** of the two live surfaces. `tools/demo_predicate_run.py` has no equivalent — `tests/golden/test_predicate_run.py` asserts only `"control findings 0"` and `"seeded findings 1"`. And `NC-E16` honestly records the hazard (`why_provisional: "the injector edits a template the demo does not render; no guard flips"`) while `NC-CI03` makes the identical move and is not marked provisional.

**Separately, and worse: the vocabulary gate is the wrong instrument for the failure it names.** The template as committed renders

```
{{ failures }} failures across {{ checks }} checks
{{ unchecked }} fields were not checked
```

With `failures=0, unchecked=0` that is a complete all-clear containing none of the 20 banned tokens. The mechanism P14 specifies against it — `band.py`'s *"the band never fills"* invariant, with terminal `NOT_SETTLEABLE_FROM_ARTIFACT` and `RESIDUE` hatched segments of non-zero width for every input — **does not exist**. Today the structural refusal rests on one hand-typed sentence in a demo script: *"It does not state that the filing is correct."*

---

## 3. Is the settled fraction always rendered with `cellsTotal` AND `inScope`? **In the object, yes. In the only thing that renders it, no — and nothing checks.**

The object is well built. `SettledFraction.__post_init__` refuses a `PRE-GATE` fraction with an empty caveat and refuses a `float`; `as_row()` is the single serialisation and `asdict` carries `cellsTotal`, `inScope`, all seven closure terms, `denominatorWarning` and `admissionState` with it; `compute()` returns `None` (never `0`) on `INVALID` / no-mask / silent-canary. `tests/property/test_prop_settled_fraction.py` exists.

But the docstring's rule 1 — *"It is a field of this object and **this object is the only serialisation**"* — is false. `tools/measure/p5_runtime_closure.py:74` writes a top-level `"fraction": "0.6192"` key into `docs/measurements/p5-verdict-closure.json` as a sibling of `closure`, not as a field of a serialised `SettledFraction`. And the markdown's own guarantee is prose in an f-string:

```
tools/measure/p5_runtime_closure.py:120
`fraction` never renders without `cellsTotal` and `inScope` beside it.
```

**Reproduction — delete the counts, keep the sentence, everything stays green:**

```bash
# in tools/measure/p5_runtime_closure.py, remove "(cellsTotal {p.cellsTotal})" and the
# "inScope {p.inScope} / fraction … = settled {p.settled} / inScope {p.inScope}" lines
$ PY=$PWD/.venv/bin/python make run-fme
$ sed -n '14,22p' docs/measurements/P5-runtime-closure.md
      ==  3747
    settled fraction   0.6192
`fraction` never renders without `cellsTotal` and `inScope` beside it.   ← the claim survives its own falsification
$ PYTHONPATH=src .venv/bin/python -m pytest tests/ -q -k "settled or fraction or closure or p5 or surface or ledger"
60 passed
$ CDFC_PY=$PWD/.venv/bin/python bash ci/no-bare-rate.sh   →  no-bare-rate: OK
```

No test opens the rendered page. `ci/no-bare-rate.sh` cannot help: `0.6192` is not a `%`, so the decimal form of the settled fraction is outside its regex entirely.

**And the two live surfaces render no settled count at all** — so P14 exit criterion 9 (*"no settled count renders without its denominator's generating rule in the same block"*) and SG3 (*"admission state and count share an ancestor within 2 levels"*) have no subject yet. When they get one, the enforcement will be a Jinja template and a Playwright assertion; today the analogous enforcement is a comment.

---

## 4. Does the attestation design avoid floats? **The ruling is enforced structurally, and it is the strongest thing in this area.**

`src/cdfc/canon.py::_ser` is the only hashing serialiser and it is int-only by construction — `Decimal` is not special-cased and therefore falls through to the terminal raise:

```
$ PYTHONPATH=src .venv/bin/python -c "…canonical_json({'x': v})…"
Decimal RAISED NonCanonicalisable  cannot canonicalise Decimal
float   RAISED NonCanonicalisable  a float reached the canonical serialiser…
int     b'{"x":3}'
bool    b'{"x":true}'
```

`src/cdfc/qualify/wilson.py` is `Decimal` throughout with an explicit ban on `math.sqrt` in its import closure, `WILSON_Z` pinned to 15 dp, `-0.000000` normalised away, `ZeroSampleError` on `n == 0`. The `ppm`-plus-`display`-string carrier that P11 §0.7 rules for is not yet built, but nothing in the tree can currently defeat it.

**One live hazard for the P11 test as specified.** `test_contract__no_json_float_in_the_payload` must assert *"no `.`, `e` or `E` inside any JSON **number token**"*. The payload already carries strings that would trip a byte-level scan — today's `"fraction": "0.6192"`, and P11's own worked example `"display": "2 of 96 · 2.1% · [0.6%–7.4%]"`. Written as `b"." not in canonical` it fails on the correct payload; written as `"no float type reached canon"` it duplicates what `canon.py` already raises and adds nothing. It has to tokenise. That is the one place this control can be built shallow, and it is worth pre-registering the tokeniser test with a positive control (`{"a": 1.5}` must fail; `{"a": "1.5"}` must pass).

---

## 5. What a regulator or auditor would find missing

1. **The denominator that matters is absent from the report and the flattering one is present.** The declaration says `475 of 505 derived cells checked` — 94%. `docs/measurements/P9-template-diff-ceiling.md:44` states the honest ceiling: *"**869 of 3747** … the flagship's real domain."* The 505 derived cells are LOCKED formula cells; the 3,747 field-surface cells are what the entity typed in. A regulator asks *"how much of what they filed did you check?"* and the report answers with a ratio over a different population. The 61.92% answer exists (`settled 2320 / inScope 3747`) and lives in a docs page.

2. **"Checked" is defined as "our evaluator did not decline to compute it".** `tools/demo_template_diff.py:99` — `checked = len(template_formula_cells) - len(grid.not_run)`. The comparison the demo actually performs is `template_formula_cells - filing_formula_cells`: **formula presence only**. A cell whose value is stale but whose `<f>` survives is counted as checked and nothing about it is compared. `_f_cached` is loaded on line 73 and never read.

   ```bash
   $ PYTHONPATH=src .venv/bin/python -c "import sys;sys.path.insert(0,'tools');import demo_template_diff as d;d.run(d.SYN/'values-written__50-cells.xlsx')"
     0 formula cell(s) overwritten with a literal
     475 of 505 derived cells checked
   $ PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_probe_template_diff.py -q -k stale
   1 passed   # test_td__fires_on_stale_carries_a_structural_detector_cannot_see  →  assert len(fails) == 20
   ```

   Twenty true positives, invisible to the report, with their twenty cells counted inside the 475. The real probe `src/cdfc/probes/template_diff.py` finds all twenty. **The report does not run the probe.** The deviation is recorded — in the demo's module docstring, which no reader of the report sees.

3. **`475` is the same arithmetic published under a third name.** `reports/validation-ledger.jsonl` carries `P6 eval.arm2_agreement.fme_libreoffice 475 / 505 MEASURED`, and `tools/measure/p3_reproduction.py:100` computes it as "cells for which the evaluator produced any value" (already confirmed by the p3-evaluator audit as not comparing to the cached value). One quantity — *cells our evaluator did not refuse* — is published as **evaluator agreement**, as **cached-value reproduction**, and as **check coverage**. Only the first is close to true.

4. **The "not checked" half loses its content in the render.** The objects carry good reasons; `why.split(":")[0]` throws them away:
   ```
   $ …recalculate(… formula_source='TEMPLATE') …Counter(g.not_run.values())
   20 | unimplemented: AGGREGATE options=6 — this build implements no ignore behaviour, and an
        aggregate computing over the wrong operand set is a clean wrong answer
   10 | unimplemented: ROW() without an explicit reference
   ```
   The user is told `30 unimplemented`. The differentiator is machine-readable and lossily rendered.

5. **No verdict, no attestation, no signature, no run id, no manifest, no template validation state on the surface.** The report never says the denominator is `PROVISIONAL-UNVALIDATED`, never says `admissionState: PRE-GATE`, never carries `ADMISSIBILITY_CAVEAT` — the sentence *"none of the predicates producing this number is admitted under G4"* — even though the object requires it be non-empty. It is constructed and discarded.

6. **`reports/validation-ledger.jsonl` stops at P6.** Seventeen rows, none from P7, P8 or P9. Two of the P5 rows are stale against their own command (`preflight.keys_type_checked 77 / 1725` vs `1713`/`66` on regeneration), and `P4 harvest.static_settled_cells.fme 2854 / 3747` disagrees with the `2794` the same command produces. The ledger is the thing an auditor would ask for first.

---

## 6. The weakest link between "we checked X" and "the report says we checked X"

**The report is not downstream of the checks. It is a parallel reimplementation of them.**

`src/cdfc/probes/template_diff.py` performs the value comparison, applies `REPRESENTATION_EPS` then `τ(n)=5n` separately, consults `template_defects.yaml`, and returns `DiffFinding` objects carrying `ItemState`/`ReasonCode`. `src/cdfc/evaluate/run.py::execute` builds `RunResult` with a closed seven-term partition and a `SettledFraction`. **Neither is on the path from a filing to a printed page.** `tools/demo_template_diff.py` re-derives its own weaker detector and its own coverage arithmetic from `recalculate` directly; `tools/demo_predicate_run.py` re-derives its own pass/fail loop. The coverage numbers that reach a human are computed by code with no gate on it, in a directory (`tools/`) that `ci/no-green-tick.sh`, `ci/no-bare-rate.sh` (`ROOTS = ["src/cdfc", "docs/measurements", "reports"]`) and `ci/no-bare-absence.sh` (`ROOTS = ["src", "tests", "docs"]`) all fail to scan.

Every honesty invariant this system owns — the seven-term closure, `assert_fraction_did_not_rise`, the `PRE-GATE` caveat, the `null`-not-zero rule, the `DECLARED_CHARACTERISTIC`/`PREDICATE_PRECONDITION` split that stops a defect declaration from raising the headline — lives on the side of the wall the report is not on.

**The single highest-value repair before P14 starts:** delete `run()` from both demos and make them call `cdfc.evaluate.run.execute` and `cdfc.probes.template_diff.template_diff`, then add `tools/` to `SURFACE_ROOTS`. That converts three of the findings above into one code path, brings the live surface inside the honesty gate, and makes the P14 renderer a formatting problem rather than a third implementation.

**Two things that would settle what I could not:** (a) a test that renders the actual declaration text and asserts the `SettledFraction` field-set appears in it — that is the only way rule 1 stops being prose; (b) a positive control on the P11 float test built *before* the payload exists — `{"a": 1.5}` red, `{"a": "1.5"}` green — because that test is one line away from being either vacuous or wrong, and it is the phase's named exit criterion 5.