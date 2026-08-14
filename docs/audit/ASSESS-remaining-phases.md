The user's repo carries no edit of mine (`src/cdfc/qualify/g4_ffr.py` is the concurrent audit's; my work ran in a pristine clone at `/private/tmp/.../scratchpad/clone`, left clean).

---

# THE ROAD FROM HERE — P10 to P14, assessed against what is actually in the tree

## 0. The board, verified by running

| fact | value | how |
|---|---|---|
| admitted predicates | **46 of 348** | `PYTHONPATH=src .venv/bin/python /private/tmp/claude-501/-Users-abishaikc-Gift/894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad/p10_witness_inventory.py` |
| admitted relations | **0** | `docs/measurements/P9-relation-attrition.md` |
| G-CORPUS | **RESTRICTED**, n=40, `n_non_synthetic: 0`, `derived_by: FOREIGN_ENGINE` | `fixtures/corpus_manifest.json` |
| campaign | G 773 · U 12 · **I 0** · O 761 · K 258 | `docs/measurements/P6-fault-model-v3.md` |
| suite | 2 failures in a fresh clone (`test_nc__Q64`, `test_nc__CI13`), 3 skips (nc-sweep) | `pytest -q --tb=no` in the clone |
| `src/cdfc/selfcheck/` | one line: `"""cdfc.selfcheck — CI scan root (R5). Must exist from P0."""` | `cat` |
| `src/cdfc/attest/` | same | `cat` |
| `src/cdfc/experiment/`, `model/`, `clause/`, `watch/`, `churn/`, `ops/`, `transfer/` | do not exist | `ls src/cdfc/` |

---

## 1. P10 — CANARIES AND RESIDUE. What is actually in the way.

### 1.1 The canary loop has no witnesses to replay, and the campaign cannot supply them

Plan/05 §P10 entry: *"P7's `admit.py` must already write `FaultWitness` records."* It does not. Admission is two fields:

```python
# src/cdfc/qualify/pipeline.py:55
@dataclass(frozen=True, slots=True)
class Admission:
    candidate_sha256: str
    record: QualificationRecord
```

and `QualificationRecord` (`src/cdfc/qualify/result.py:126`) is `(candidate_sha256, obligation_id, outcomes, qualified_at, qualified_against)`. No `liveness`, no `kill_cases`, no `pass_case`. There is **no persisted registry at all** — `Registry` (`src/cdfc/predicates/registry.py:71`) is in-memory and `registry_root()` is a hash over rows built at run time, so `n_admitted_predicates` and `registry_root` — two of the five fields P10-B2's renderer refuses to print without — require re-running the whole qualification.

Worse, the campaign cannot be mined for witnesses, because **it never records a stable key**:

```
$ .venv/bin/python -c "import json; rows=[json.loads(l) for l in open('reports/campaigns/fme-v3-seed20260810/killed.jsonl')]; \
  print(sorted(rows[0].keys())); print(sorted(rows[0]['edits'][0].keys())); \
  print('stable_key anywhere:', any('stable_key' in json.dumps(r) for r in rows))"
['base_sha256','distinguishing','edits','fault_class','fault_model_version','harness_version','killed_by',
 'mutant_sha256','n_distinguishing','observability','operator_id','parts_changed','reachable','reason','seed','sites']
['new_xml','old_xml','operator_id','ref','sheet_name']
stable_key anywhere: False
```

Every mutant is `sheet!ref` plus raw XML. `FaultWitness.target: StableKey` — *"a key in the induced schema — NEVER a coordinate"* — has no source in the build. The **good news** is that `FaultOperator.mutate(value, site, rng)` (`src/cdfc/qualify/fault_model.py:97`) is already a value transformation, not an XML one, so the operator half replays in memory as designed. Two things must be built that the 4.5-day B1 estimate does not contain: a coordinate→stable-key inverse (`facts/build.py::cell_of` is the forward direction, at line 162), and an `rng` capture — `_enum_other`, `_homoglyph`, `_vocab_outside` draw from an RNG and produce **strings**, which `params: Mapping[str, int]` ("integer only") cannot hold.

### 1.2 The canary loop's in-memory path does not exist, and the type it is specified over is dead code

`apply(w, facts: FactTable) -> FactTable` and `compute_residue(filing: FactTable, …)` name a type nothing in the runtime uses:

```
$ PYTHONPATH=src .venv/bin/python -c "from cdfc.importgraph import import_closure; \
  c=set(import_closure('cdfc.evaluate.runner')); print('fact_table in runner closure:', 'cdfc.facts.fact_table' in c)"
fact_table in runner closure: False
```

`cdfc.facts.fact_table` — the two-document model with `Leaf`, `Anchor`, `Warrant`, `derive()` weakest-input composition and the `to_units` money scaling — is imported by exactly one file in the repository: `tests/unit/test_fact_table.py`. Every real path (`measure/p5_run.py`, `tools/measure/p7_attrition.py`, `tools/measure/p8_ffr.py`, `probes/qualify.py`) uses `facts.build.fact_set_for` → `FactSet` over nested dicts. **This is the root of open item (c)** — the 1000× tolerance is not a typo, it is that the only scaling site in the system sits on a dead path.

And `observability()` today is file-based: `grid_of(blob: Path)`, `extract(blob: Path)`, `classify_files(clean: Path, mutant: Path)`. The canary loop is required to never open an artifact (`test_nc__C05c_no_artifact_is_opened_during_the_canary_loop`). Measured cost of the file path, so the trade is priced:

```
$ PYTHONPATH=src .venv/bin/python -c "...grid_of('clean__independently-computed__fme-q1.xlsx')..."
grid_of cold 45.9 ms, warm 10.2 ms; 5273 values, 30 not_run
fact_set_for 134.5 ms
```

46 predicates × one witness × one recalculation ≈ **470 ms warm** against a "~30 ms core". So the in-memory path is not an optimisation, it is the phase. Build it as: patch the `Extraction.literals` map at the witness's cell, reuse `cone_for` + `recalculate(..., formula_source="FILING")`. That machinery all exists; the entry point does not.

### 1.3 `src/cdfc/selfcheck/timings.py` — the file the plan names — cannot exist. Demonstrated.

```
$ printf 'from time import perf_counter\ndef t() -> float:\n    return perf_counter()\n' > src/cdfc/selfcheck/timings.py
$ bash ci/no-clock-in-core.sh
GATE FAIL: a monotonic clock is reachable from the deterministic core:
src/cdfc/selfcheck/timings.py:3:    return perf_counter()
  timings belong in src/cdfc/measure/perf/ or reports/perf/
rc=1
```

(file removed; tree clean). This is a case where the **built gate is stricter and better than the plan** — P0 did widen the pattern set to `perf_counter|monotonic|process_time` exactly as plan/05 F23 demanded. P10-B1 must put the timer in `src/cdfc/measure/perf/canary_timings.py` and record the relocation. It must **not** widen the exemption: widening `no-clock-in-core.sh` for the one module P11's whole determinism argument turns on is the "exemption swallows the subject" pattern this audit keeps finding elsewhere.

### 1.4 The canary loop is outside the scan set of the gate that exists to guard verdicts. Demonstrated.

```python
# tests/contract/test_contract_verdict_path.py:22
VERDICT_PATH = ("cdfc/verdict", "cdfc/evaluate", "cdfc/facts")
```

`cdfc/selfcheck`, `cdfc/probes`, `cdfc/attest`, `cdfc/surface` are not in it. P10 puts `selfcheck/canary.py` in the position of deciding whether a run is VALID **at all**. Reproduction (run in the clone, restored):

```
$ printf 'import anthropic\nimport requests\n' >> src/cdfc/selfcheck/__init__.py
$ printf '\nimport openai  # noqa\n' >> src/cdfc/probes/driver.py
$ PYTHONPATH=src pytest tests/contract/test_contract_verdict_path.py -q
...                                                                      [100%]
```

Three tests green with a model client and a network stack in the module that gates the verdict. `VERDICT_PATH` must gain `cdfc/selfcheck` and `cdfc/probes` **in P10-B1, before the canary code lands**, not in P13-B0 where the plan files it — because P13-B0 is nine months later and its stated principle is *"the guard must precede the thing it guards"*.

### 1.5 P10-B2: the residue set is 503 mutants, and 425 of them are written to no file

```
$ wc -l reports/campaigns/fme-v3-seed20260810/*.jsonl
       0 indeterminate.jsonl
     258 killed.jsonl
      12 unobservable.jsonl
      78 unreachable.jsonl
```

`773 − 258 − 12 − 78 = 425`. Add the 78 unreachable (a mutant no predicate reads is a survivor by definition) and the residue base is **503 = 761 − 258**, of which **425 have no persisted identity**. P6's campaign has no survivor writer. B2 must add one, and the human adjudication step — 3–5 person-days — is over 503 mutants, i.e. ~3 minutes each with an *argument* per row that the loader refuses without.

### 1.6 `INDETERMINATE_OBSERVABILITY` is unreachable, and P10-B2's denominator inherits it

`I = 0` in the published campaign is a construction. `src/cdfc/qualify/runner.py:130`:

```python
if cells and obs is not Observability.OBSERVABLE:
    obs = Observability.OBSERVABLE
```

`classify` returns `(INDETERMINATE_OBSERVABILITY, blocked)` with `blocked` **always non-empty** — that is what makes it indeterminate. Reproduction:

```
$ PYTHONPATH=src .venv/bin/python -c "
from cdfc.qualify.observability import classify, Observability
from cdfc.calc.evaluate import ValueGrid
kw=dict(values={('S','A1'):1}, not_run={('S','B1'):'deferred'}, formula_source='FILING', computed_cells=1)
obs,cells=classify(ValueGrid(**kw),ValueGrid(**kw)); print('classify ->',obs.value)
if cells and obs is not Observability.OBSERVABLE: obs=Observability.OBSERVABLE
print('after the runner.run_one promotion line ->',obs.value)"
classify -> INDETERMINATE_OBSERVABILITY
after the runner.run_one promotion line -> OBSERVABLE
```

For P10-B2 this is not a cosmetic count. Every mutant our evaluator **cannot see** is currently banked into `O`, evaluated, not killed, and lands in RESIDUE — where the headline reads *"a falsehood no check catches"* and the truth is *"a falsehood we cannot compute"*. That is the F18 confusion arriving inside the number the phase exists to produce. It also breaks P12's G-SETTLE criterion 7 (`I` published beside `U/G`), so one repair pays for two phases.

### 1.7 The witness inventory, measured: liveness can only be demonstrated for 1–2 of the 5–7 classes each predicate claims

```
--- witness inventory over the 46 admitted ---
admitted with ZERO stored kill in any CLAIMED class: 0
admitted with fewer than min(3,|claimed|) distinct claimed classes killed: 36
distribution (claimed, killed-claimed): Counter({(7,2):19, (6,1):7, (7,1):5, (1,1):4, (5,3):2,
                                                (2,1):2, (6,4):2, (6,6):2, (5,1):1, (6,2):1, (3,1):1})
```

Every one of the 46 can get *a* witness — good, the loop is buildable. But **36 of 46 cannot get three diverse-by-class witnesses**: nineteen predicates claim seven classes and killed two. So `livenessProof` would attest *"this check just demonstrated it can catch the fault it was admitted for"* while the demonstration covers 2 of 7 declared faults. That is D-P4-06's defect — a denominator chosen after the result — reappearing on the canary side. **The fix is cheap and must be pre-registered before B1**: `CanaryRow` gains `classes_demonstrated` and `classes_claimed`, and `livenessProof` renders **both integers**, exactly as the obligation-coverage pair and the two kill rates already do. Do not let it render one.

This also collapses B1's extra 0.5 day: the `MAX_WITNESSES ∈ {1,3,5}` curve is capped at 2 for 31 of 46 predicates by class coverage alone, computable from the committed `killed.jsonl` in twenty minutes, before any campaign runs.

### 1.8 Open item (c) hits P10 hardest, and it flips sign here

24 of the 46 admitted predicates carry a tolerance literal that is 1,000× too wide (same script). In P6/P7 that *depressed* K/O — a lower bound, benign. In P10 it inverts: a canary witness whose perturbation is smaller than a 60-USD-Million tolerance does **not fire** → `silent` → `invalid.canary_silent` → `settledFraction is null`. The over-wide tolerance turns from a conservative bias into **a run that refuses to issue a verdict**, on 52% of the canary population. The worked instance is already published: `P-0114` over `'3. Portfolio'!O7` passes for any total between −48 and 72 on a row whose true total is 12.

### 1.9 P10-B4 is the one piece that is ready

Exhibit E2's measured basis exists: `docs/measurements/P9-template-diff-ceiling.md:15` publishes **2790 field-surface cells feed no template formula at all**. What is missing is the golden pin the exit gate names (`test_golden__2790_cells_feed_no_formula`, per-sheet split, paired in/out value assertion). One day, as budgeted.

### 1.10 P10 catalogue delta

`NC-C01…C07` do not exist:

```
$ .venv/bin/python -c "import yaml; d=yaml.safe_load(open('tests/negative/catalogue.yaml')); \
  print([e['id'] for e in d['entries'] if e['id'].startswith('NC-C')])"
['NC-CI01', … 'NC-CI17']
```

99 entries today, all `NC-CI*` on the C prefix. P10 adds seven-plus new entries and `tests/negative/test_nc_selfcheck.py`, which does not exist.

---

## 2. P11 — ATTESTATION AND `verify`

**Hard-blocked on P10 by design** (nothing to sign until canaries run), and separately blocked by a P5 gap.

- `runs/<run_id>/{run.jsonl, run.db, manifest.json}` is never produced. `src/cdfc/evaluate/run.py:180 write()` has **no caller** (`grep -rn "import write\|run\.write\|\bwrite(" --include="*.py" src tests tools` returns only `measure/absence.py`'s `fh.write` and a `sys.stdout.write`). `cdfc run` exits 2: *"`run` is not implemented at phase P0; it is built in P5."*
- P11-B2 re-runs the pipeline from **the manifest's eight pins** — `{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha, evaluator_version, fault_model_version, tool_versions{…}}` plus `probe_seed` and `timeVerified`. `RunResult.as_manifest()` carries none of `registry_root`, `register_snapshot_sha256`, `code_git_sha`, `evaluator_version`, `fault_model_version`, `tool_versions`, `probe_seed`. Roughly three of ten pins exist.
- The four acceptance flows (`E2E-VERIFY`, `E2E-TAMPER`, `E2E-INVALID`, `E2E-TAMPER-ATTEST`) have no home: `tests/e2e/` does not exist and `make e2e` prints **`e2e: subject does not exist at P0`** — a stale echo stub nine phases late, same family as `make perf` and `make mutation-pr`.

**What P11 already has, and it is more than expected.** `ci/no-clock-in-core.sh` covers all three monotonic-clock names. `tests/determinism/test_det_probes.py::test_det__probe_results_are_seed_stable` and `::test_det__the_seed_is_recorded_in_the_manifest` are green — the fifth non-determinism source P9 added is closed. Money is integer; there is no float on the verdict path. The determinism spine is in good shape; it is the **artifact** that is missing, not the discipline.

---

## 3. P12 — THE SETTLING EXPERIMENT (G-SETTLE)

Nothing of `src/cdfc/experiment/` exists. Three specific hazards, all inherited:

**(i) G-SETTLE criterion 4 is at risk of being a tautology.** `beats_baselines` is specified as *"THE ARITHMETIC OF G-SETTLE CRITERION 4, as a pure function of the four rows"*. The shipped analogue at `src/cdfc/qualify/g2_kill.py:152`:

```python
others = {b: baselines.kills(b) - stored.mutants(cand.id) for b in baselines.names()}
marginal = {b: len(mine - others[b]) for b in baselines.names()}
```

`mine ⊆ stored.mutants(cand.id)` and `others[b] ∩ stored.mutants(cand.id) = ∅`, so `mine − others[b] ≡ mine`. Verified on real data against a baseline that kills **every one of the 210** observable digests:

```
$ PYTHONPATH=src .venv/bin/python -c "
import json; from cdfc.qualify import campaign_store
st=campaign_store.load('fme-v3-seed20260810')
rows=[json.loads(l) for l in open('reports/campaigns/fme-v3-seed20260810/killed.jsonl')]
mine=set(st.mutants('P-0001')); allm={r['mutant_sha256'] for r in rows}
print('|mine|=%d |allm|=%d'%(len(mine),len(allm)), 'mine-others==mine ?', (mine-(allm-mine))==mine)"
|mine|=3 |allm|=210 mine-others==mine ? True
```

If P12-B2's `marginal_kill` reuses that subtraction, the gate that decides **whether the model layer is built at all** passes by construction. The correction is one line — remove the candidate from the baseline *after* the difference, or not at all, and handle the "candidate is in B0" problem by excluding the candidate's own harvest class from B0 rather than its kill set.

**(ii) The B1 the plan forbids is the B1 that exists.** `src/cdfc/qualify/baselines/b1_invariants.py` opens *"THIS IS NOT DAIKON, AND IT SAYS SO"* and the deviation is recorded honestly in its own docstring (four single-variable templates at confidence 1.0, no inter-variable relations, *"marginal kill over it OVERSTATES marginal kill over Daikon"*). That is fine for P7. It is **exactly** what plan/06 §P12-B2 prohibits: *"It does not fall back to a hand-written weaker detector, because a weaker baseline makes L3 easier to beat."* P12 must either run Daikon under a digest-pinned container or declare B1 not-run and evaluate its term `False` — it must not point at `qualify/baselines/b1_invariants.py`.

**(iii) Criterion 7 requires `I` published beside `U/G`.** `I` is structurally 0 (§1.6). Publishing it as-is is publishing a constant into the exit gate that F18 wrote specifically against.

**What is ready:** `src/cdfc/qualify/textsource.py` and `docs/measurements/P7-textsource.md` exist — the plan/06 §0.2 relocation of `textsource` to P7-B0 was executed. The three baselines exist as objects. The `k=0` branch already has its answer: with `experiments/E6/` absent and 46 EXPERIMENT-grade predicates, P12 is genuinely optional to the product and mandatory to the paper.

---

## 4. P13 — MODEL AND CLAUSE LAYERS

**B0 is already delivered, early and well.** `tests/contract/test_contract_verdict_path.py` has `test_no_model_in_verdict_path`, `test_no_network_stack_in_verdict_path`, **and** `test_the_walk_can_see_an_import_when_there_is_one` — the admission-side positive control the plan asks for, with the right docstring: *"a walk that matches nothing is not a guard."* Its two defects are the scan set (§1.4) and that **`ci/barrier5.sh` does not exist** (`ls ci/` shows seventeen scripts, no barrier5) — the file-existence half of the guard, a P0 deliverable per P13's own entry table.

B1 is gated on `experiments/E6/DECISION.md` with verdict `RETAIN` — so P12 fully blocks it. **B2 (the clause graph, 6 days) is explicitly not gated on G-SETTLE** and its dependencies (P1 dual-reader, P2 extraction manifest) are complete. B2 is the largest piece of P13 that can be built at any time, and its value does not depend on the experiment's outcome.

One standing fact that P13-B2 will confront: `docs/decisions/D-P7-01-no-statutory-instrument.md` and `docs/measurements/P7-attrition.md` — **`predicates_with_a_STATUTE_obligation = 0 / 348`**, and *"no statute is pinned in this repository at all."* The clause graph's 399 PDFs are the artifact that changes that number, and until it does, `g0_marker_recall` stays `NOT MEASURED (0/0 labelled spans)`.

---

## 5. P14 — THE SURFACES

P14's entry table is explicit that B1–B3 need only P5 and P0: *"B1–B3 render from `run.jsonl` and nothing else. Not required, deliberately: P6, P9, P11, P12, P13."* Which makes the position sharp: **P14-B1/B2/B3 — nine days, the earliest-finishing off-path work in the whole schedule — is blocked on one unwired P5 function.** `write()` exists, is correct, and is called by nothing. `cdfc run` exits 2.

Other concrete state:

- `src/cdfc/surface/labels.py` is **not** the P14 label registry. It holds `SCAN_ROOTS` and the banned-glyph list — precisely the P0 stub plan/07's §"three scan sets" ruling specifies, correctly built. `SURFACES`, `REQUIRED_NUMBERS` and the hero string are absent, which is right: P14-B1 extends it.
- `src/cdfc/surface/design.py` exists and its docstring is a genuine deliverable, not a claim: *"There is no `SUCCESS` colour and no affirmative badge token… `ci/no-green-tick.sh` fails the build if either name appears."*
- `src/cdfc/surface/templates/report.html.j2` is 9 lines with three `{{ }}` slots and no renderer. **jinja2 is not installed** (`ModuleNotFoundError: No module named 'jinja2'`) — a new runtime dependency, so it lands in `docs/LICENCES.md` and `ci/licence-denylist.sh` (which already fails in a fresh clone).
- **B4 is not blocked.** G-CORPUS = RESTRICTED is one of its three admissible branches; B4 ships digits only for classes the corpus licenses with the literal `G-CORPUS: RESTRICTED` in the header. The instruction *"B4 must never treat RESTRICTED as PASS"* is the whole test.
- P14 exit criterion 9 pins `predicates_with_a_TEMPLATE_obligation / 280 = 280 / 280`. The build says **348 / 348** (recorded in `docs/HARVEST-DELTA.md`), the P4 markdown says **571 / 571**, and `docs/measurements/p4-harvest-distribution.json` says **592**. Three numbers for one metric. Whichever the surface renders, the other two must be reconciled or retired first, because criterion 9's own rule is that both obligation counts render together or neither does.

---

## 6. THE P9 OPEN ITEMS: which blocks what

| item | blocks | verdict |
|---|---|---|
| **(a) TEMPLATE_DIFF needs a new `ADMITTED_HOST_FNS` member** | **P10-B2 (soft), P14-B2 (soft)** | **RIDES.** Nothing structurally requires it. Its cost is that `|RESIDUE|` is computed against `n_admitted_relations = 0` — which the plan already anticipates (*"on G-CORPUS's FAIL branch the admitted set is empty… That is still a result and it is a ceiling"*) and NC-C07's guard already enforces. Fix it when the residue's headline is worth strengthening, not before. |
| **(b) A relation has no obligation; G0 RAISES** | **P10-B2 (soft), P14-B4 (soft)** | **RIDES**, but must be *decided* before P10-B2 publishes, because `n_admitted_relations` is one of the five fields the renderer refuses without. Deciding it is arbitration, not engineering: minting `OBL-TEMPLATE-R-*` moves `coverage_pair()`'s published TEMPLATE count, which lands on P14's criterion 9. Cheapest honest route: publish `n_admitted_relations = 0` and label `|RESIDUE|` a ceiling. |
| **(c) Every harvested tolerance is 1000× too wide** | **P10-B1 — HARD** | **BLOCKS P10-B1.** In P6/P7 it depressed K/O and was benign. In P10 it makes 24 of 46 canaries silent, and a silent canary is `invalid.canary_silent` with `settledFraction: null`. It is also the only one of the five whose repair is fully specified and mechanical: give `fact_set_for` a `money_keys` argument and route it through `facts/fact_table.build`, i.e. **retire the dead `FactTable` by putting it on the runtime path** — which is separately required by `apply(w, facts: FactTable)`. Two problems, one repair. `test_nc__R12a_the_tolerance_unit_mismatch_is_still_open` will go red the day one half moves without the other; that is the guard working, and it is the signal to do both. |
| **(d) Fingerprint does not exclude formula PRESENCE; 8 cells unbind** | **P10-B1 (narrow), P11 (narrow)** | **RIDES.** Its consequence is already published as a second ceiling (869 of 3747) and guarded by NC-R11. It matters at P10 only if a canary witness targets one of the eight — trivially excluded by refusing those cells as witness targets, which is one predicate in the witness selector plus a test. The real repair (style-only mask) moves every template binding digest and belongs to P5's binder in a phase of its own. |
| **(e) 29 of 79 tolerance-bearing predicates apply τ to a count** | **P10-B1 (partial)** | **RIDES, but is fixed by the same commit as (c).** `probes/degree.py` already computes the degree map that decides who gets τ; wiring `sum_identity.py` to consult it is the same PR as the units repair, and both change `code_sha256` for the same predicates — so doing them separately costs two registry-root moves and two funnel regenerations. |

**One item blocks: (c). It blocks P10-B1, the next thing to be built.**

Two items from the parallel audit block alongside it and are not on the P9 open list:
- `INDETERMINATE` unreachable — blocks P10-B2's denominator and P12's G-SETTLE criterion 7.
- The `killed.jsonl` → predicate-id join (125 of 126 credited ids carry a different `expr` at HEAD) — blocks P10-B1 outright. **Every witness the canary loop would store is attributed to a predicate that no longer exists.** A canary loop built on that join attests liveness for the wrong check.

---

## 7. THE ORDER I WOULD BUILD IN

**P9.5 — a repair phase, 5–7 days, before any P10 code.** Not in the plan, and it should be, because four of its five items are prerequisites of P10-B1 rather than improvements to P9.

1. **Bind the campaign to predicate identity.** Store `code_sha256` beside `killed_by` in `killed.jsonl`, and make `campaign_store.load` refuse a join whose digest does not match the current candidate. *Reason: it is the cheapest, and until it holds, every downstream number — G2's per-predicate kill vector, the 46-predicate admitted set, every witness P10 would store — is evidence about a different predicate. Nothing built after it survives fixing it later.*
2. **Delete the `INDETERMINATE → OBSERVABLE` promotion at `runner.py:130`** and re-derive P6. *Reason: it is one line; it pays for P10-B2's denominator and P12's criterion 7 at once; and the 22 mutants it moves change published integers, so it must precede anything that pins them.*
3. **Put `FactTable` on the runtime path** — `fact_set_for(filing, template, money_keys=...)` — and route `sum_identity`'s τ through `probes/degree.py`. *Reason: repairs (c) and (e) in one registry-root move; supplies the in-memory typed fact table that `apply()` and `compute_residue()` are specified over; and retires 200 lines of unit-tested dead code. Regenerate P4/P6/P7/P8/P9 in the same commit and publish the deltas — this is the one moment where moving four phases' published numbers is honest, because the commit says why.*
4. **Add a survivor writer to the campaign** (`survivors.jsonl`, 425 rows). *Reason: P10-B2's human step cannot be scheduled over a set that does not exist, and 3–5 person-days of a second person's calendar is the longest-latency item in the phase — start it the day the file lands.*
5. **Extend `VERDICT_PATH` to `cdfc/selfcheck` and `cdfc/probes`, and write `ci/barrier5.sh`.** *Reason: the guard precedes the thing it guards. Both are hours, and after P10-B1 lands the extension becomes a change to a passing gate rather than a gate that was always right.*

**Then P10, in the plan's order, with three amendments.** B1 puts timings in `src/cdfc/measure/perf/` (the gate already says so). `CanaryRow` carries `classes_demonstrated` **and** `classes_claimed`, rendered as a pair. The `MAX_WITNESSES` curve is computed from the committed campaign before B1 opens, not by three fresh campaigns — the class-coverage ceiling of 2 for 31 of 46 predicates makes the {3,5} arms nearly flat, and measuring that first may return the 0.5 day F44 bought.

**In parallel with P10, off the critical path: wire P5-B4.** Call `write()`, add the missing manifest pins, create `tests/e2e/`, replace the `make e2e` echo. It is two days, it unblocks nine days of P14-B1/B2/B3 that need nothing else, and it is a prerequisite of P11-B2 regardless. *Reason it goes here and not later: it is the only item in the remaining plan that blocks a full phase while costing two days, and it is currently invisible because `execute()` returns a `RunResult` that no test asks to be written down.*

**Then P11**, which is genuinely gated on P10 and on nothing else once the manifest pins exist.

**P14-B1/B2/B3 whenever an engineer is free after `run.jsonl` lands**; **P14-B4 after P8's numbers are reconciled** (the 280/348/571/592 problem is criterion 9's, not B4's, but B4 is where it surfaces).

**P12 last of the pre-P13 work**, and only after the `marginal_kill` arithmetic is rebuilt rather than reused. *Reason: it is the one phase whose failure branch is already the plan's default (`k = 0`), the product is unaffected either way, and building it on an inherited tautology would produce a RETAIN that means nothing.* **P13-B2** — the clause graph — is not gated on it and is the best use of a second engineer today.

---

## 8. WHERE I AM UNCERTAIN, AND THE MEASUREMENT THAT SETTLES IT

- **How many of the 761 O-mutants are truly INDETERMINATE.** I proved the promotion line makes I unreachable; I did not re-run the campaign with it removed. Settles it: delete `runner.py:130`, run `make campaign`, read `wc -l indeterminate.jsonl`. ~15 minutes of wall clock. The parallel audit's figure of 22 is the number to check against.
- **Whether the in-memory canary hits `PERF-CANARY`.** I measured the file path at 10.2 ms warm per recalculation. The in-memory cone-restricted path has never been built, so its cost is a guess. Settles it: a 30-line spike that patches one `Extraction.literals` entry, calls `cone_for` + `recalculate`, and times 46 iterations. Half a day, and it decides whether B1 is 4.5 days or 8.
- **Whether the 46-predicate admitted set survives repair (1).** With the id join fixed, some of the 126 credited ids will no longer match and some of the 46 admissions will vanish. If the admitted set drops below ~20, the canary loop's inapplicability ceiling of 0.25 becomes a coarse threshold over a small denominator and `CANARY_INAPPLICABLE_CEILING` needs re-pre-registering before B1, not after. Settles it: repair (1), re-run `make attrition`, read the admitted count.
- **Whether `qualify/baselines/b1_invariants.py` was ever intended as P12's B1.** Its docstring records the P7 deviation honestly and says nothing about P12. I found no `docs/decisions/` file, no `docs/GATE-CHANGES.md` entry, and no commit message on the question. If the intent was to reuse it, that is an unrecorded deviation from a P12 prohibition; if not, P12's B1 is unbuilt and its 1-day estimate is wrong. Settles it: one line in a decision record, written now while the answer is still known.