### [FATAL] p0-p2-foundation — Every root-derived grep gate reports OK having scanned nothing when the hardcoded interpreter path is absent — NC-CI01's own defect, live inside the gate that prevents it

**file** `ci/_roots.sh`:5  ·  **kind** shallow-proxy

**claim** `ci/_roots.sh` defaults `PY` to the machine-local absolute path `/Users/abishaikc/Gift/.venv/bin/python`; on any machine where that path does not exist (i.e. every fresh clone that does not set `CDFC_PY`) `cdfc_roots` emits nothing, `assert_roots_exist` iterates zero roots and returns 0, and `ci/no-bare-except.sh` and `ci/scan-roots-exist.sh` print `OK` and exit 0 having greped no files at all.

**evidence** With a bare `except:` planted in `src/cdfc/evaluate/__init__.py`:
  `bash ci/no-bare-except.sh` -> prints `GATE FAIL: bare except found`, rc=1 (correct)
  `CDFC_PY=/nonexistent/python bash ci/no-bare-except.sh` -> prints `ci/_roots.sh: line 6: /nonexistent/python: No such file or directory` twice, then `no-bare-except: OK`, rc=0.
Same shape for `ci/scan-roots-exist.sh` (rc=0 with a missing interpreter). This is verbatim the break NC-CI01 registers — "a grep gate whose scan root does not exist reports success" — and the guard test `test_nc__CI01_missing_scan_root_fails` cannot see it because it only injects `RemoveScanRoot` while the interpreter is present. `set -euo pipefail` does not catch it: the failure is inside a process substitution `< <("$@")`, whose exit status is discarded.

**reproduce** `cd /Users/abishaikc/Gift && printf '\ntry:\n    pass\nexcept:\n    pass\n' >> src/cdfc/evaluate/__init__.py && bash ci/no-bare-except.sh; echo "real=$?"; CDFC_PY=/nonexistent/python bash ci/no-bare-except.sh; echo "missing=$?"; git checkout -- src/cdfc/evaluate/__init__.py`

---

### [FATAL] p6-campaign — INDETERMINATE_OBSERVABILITY is unreachable in the campaign: run_one overwrites every one of them with OBSERVABLE, so the published I=0 is a construction, not a measurement

**file** `src/cdfc/qualify/runner.py`:131  ·  **kind** shallow-proxy

**claim** `classify()` is genuinely three-way, but `CampaignRunner.run_one` promotes every INDETERMINATE verdict to OBSERVABLE before it is counted — because `classify` returns the *blocked* (not_run) cells as its second value and run_one treats any non-empty second value as proof of observability — so `I` can never be non-zero in any campaign, and the 22 mutants that were INDETERMINATE on the committed campaign were banked into `O` with the cells the evaluator COULD NOT COMPUTE recorded as their `distinguishing` set.

**evidence** runner.py:123 `obs, cells = classify(...)`; :130 `cells = frozenset(cells) | moved`; :131 `if cells and obs is not Observability.OBSERVABLE: obs = Observability.OBSERVABLE`. classify() returns `(INDETERMINATE_OBSERVABILITY, blocked)` with `blocked` non-empty by construction (observability.py:253-255), so the promotion always fires.

Ran the real campaign out-of-tree with `classify` wrapped to record its verdict:
  raw classify() verdicts over all 773 mutants: OBSERVABLE 739, UNOBSERVABLE 12, INDETERMINATE_OBSERVABILITY 22
  mutants whose classify() verdict was OVERWRITTEN by run_one: 22 (F12.c x20, F05.b x1, F07.a x1)
Published manifest: I=0 for every class, O=761. Correctly classified it would be O=739.

Isolated single mutant (F12.c, trailing whitespace, at a sampled site):
  ('1. Introduction','C54') val=1 classify=INDETERMINATE_OBSERVABILITY moved=0 -> runner=OBSERVABLE distinguishing=['1. Introduction!C100','1. Introduction!C101','1. Introduction!C92','1. Introduction!C93']  — all four are `not_run` cells (AGGREGATE options=6 unimplemented).
The committed campaign records exactly that: `grep 'Introduction!C54' reports/campaigns/fme-v3-seed20260810/unreachable.jsonl` -> `F12.c OBSERVABLE n_distinguishing=10 distinguishing=['1. Introduction!C100','1. Introduction!C101','1. Introduction!C92']`.

The measurement doc's stated reason for I=0 is therefore false: docs/measurements/P6-fault-model-v3.md:50-55 says "every operator in this model edits a cell whose own value moves ... INDETERMINATE needs a mutant that is invisible at its own site. This model has none." The F12.c mutant above IS invisible at its own site (`literal_differences` = 0, grids equal) and classify says INDETERMINATE; it is only the runner's override that hides it.

Nothing tests this path: `grep -rn 'CampaignRunner\|run_one' tests/` returns nothing. NC-Q60's three guards all call `classify()` directly, so the control observed red is a control over a function whose verdict the campaign discards.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python - <<'EOF'
from pathlib import Path
from cdfc.measure.p5_run import INDEPENDENT
from cdfc.qualify.observability import grid_of, cone_for, classify, literal_differences, Observability
from cdfc.qualify.surgery import plan_edit, seed_mutant
site=("1. Introduction","C54"); tgt=Path("/tmp/m_c54.xlsx")
e=plan_edit(INDEPENDENT,*site,"1 ","F12.c")
seed_mutant(INDEPENDENT,[e],tgt,fault_class="F12",operator_id="F12.c",seed=1)
full=grid_of(INDEPENDENT); cone=cone_for(INDEPENDENT,[site])
obs,cells=classify(grid_of(INDEPENDENT,cone=cone,baseline=full), grid_of(tgt,cone=cone,baseline=full))
moved=literal_differences(INDEPENDENT,tgt)
cells2=frozenset(cells)|moved
print("classify() says:",obs," literal diffs:",len(moved))
print("runner.run_one records:", Observability.OBSERVABLE if (cells2 and obs is not Observability.OBSERVABLE) else obs)
EOF
# and: grep -c . reports/campaigns/fme-v3-seed20260810/indeterminate.jsonl   -> 0`

---

### [FATAL] p6-campaign — The committed campaign credits kills to predicate ids that no longer denote those predicates: 125 of the 126 credited ids carry a different `expr` at HEAD, and nothing checks it

**file** `src/cdfc/qualify/campaign_store.py`:83  ·  **kind** correctness

**claim** `killed.jsonl` records `killed_by: [<predicate id>]`, and `campaign_store.load()` joins those ids to the *current* candidate set for every per-predicate kill vector G2 scores (`stored.kills(cand.id, cls)`), but the harvest re-assigned predicate ids after the campaign was recorded — so G2's numerator for each of the 348 candidates is evidence about a different predicate, and the only guard on the join is a fault-model-version string.

**evidence** Campaign committed at 0605a9c; `predicates/harvested/7d9a1960/*.yaml` rewritten at 37c9dc6 ("P7-B1 ... an id that was not injective") and 37ab113 (P8-B1). Comparing the 126 predicate ids credited in the committed killed.jsonl between 0605a9c and HEAD:
  distinct predicate ids credited in killed.jsonl: 126
  expr identical: 1   expr DIFFERENT: 125
Examples:
  P-0009 was `filing.n_1_introduction.r19.cd.v == (…"*Restricted*" ? 1 : 0)+…` (a COUNTIF tally over G54:G63); at HEAD it is `filing.n_1_introduction.dv_d21.cells.all(c, c.v == "" || c.v in template.vocab.n_1_introduction_d21)` (a vocabulary membership check on a different range).
  P-0013 was `r40.cd.v == r11.cd.v`; at HEAD it is a date-range check on dv_d41.
campaign_store.load() (campaign_store.py:83) validates only `fault_model_version`; there is no harvest digest, no `code_sha256`, no predicate-set digest in `manifest.json` (`grep -n 'digest' reports/campaigns/fme-v3-seed20260810/manifest.json` -> fault_model_digest, site_set_digest only). g2_kill.py:135 `k_claimed = sum(stored.kills(cand.id, c) for c in claimed)` is the join. G2 rejected 302 of 348 and admitted 46 on that basis (docs/measurements/P7-attrition.md:15-19).
The ancestry check (g2_kill.py:196) does not catch this: it compares docs/FAULT-CLAIMS.md's commit against the campaign's, not the predicate bodies'.

**reproduce** `cd /Users/abishaikc/Gift && python3 - <<'EOF'
import json, subprocess
ids=set()
for l in open('reports/campaigns/fme-v3-seed20260810/killed.jsonl'):
    ids |= set(json.loads(l)['killed_by'])
def expr(rev,pid):
    r=subprocess.run(["git","show",f"{rev}:predicates/harvested/7d9a1960/{pid}__harvested.yaml"],capture_output=True,text=True)
    return next((x for x in r.stdout.splitlines() if x.startswith("expr:")), None)
same=sum(1 for p in ids if expr("0605a9c",p)==expr("HEAD",p))
print("credited ids:",len(ids)," expr identical at HEAD:",same," DIFFERENT:",len(ids)-same)
EOF`

---

### [FATAL] p7-gates — G2's "marginal kill over B0/B1/B2" is arithmetically independent of the baselines: replacing all three with the empty set, or with the set of every mutant, leaves the funnel byte-identical

**file** `src/cdfc/qualify/g2_kill.py`:152  ·  **kind** shallow-proxy

**claim** `g2_kill.check` subtracts the candidate's ENTIRE kill set from every baseline before the set difference, so `mine - others[b] == mine` identically; `marginal_kill[B0/B1/B2]` is three copies of the candidate's own claimed-class kill count and no baseline can ever affect a G2 decision.

**evidence** src/cdfc/qualify/g2_kill.py:152 computes `others = {b: baselines.kills(b) - stored.mutants(cand.id)}` and line 146 sets `mine = stored.mutants_in(stored.mutants(cand.id), claimed)`, so `mine ⊆ stored.mutants(cand.id)` and `mine ∩ others[b] = ∅` for every b by construction. Observed, over all 348 harvested candidates:
  real       {'PASS': 46, 'g2.no_kill': 231, 'g2.no_margin_over_baselines': 71}
  empty      {'PASS': 46, 'g2.no_kill': 231, 'g2.no_margin_over_baselines': 71}
  omniscient {'PASS': 46, 'g2.no_kill': 231, 'g2.no_margin_over_baselines': 71}
where `empty` sets B0=B1=B2=∅ and `omniscient` sets B0=B1=B2 = every mutant digest in the campaign (a baseline that catches everything). I also confirmed 0 of 348 candidates have any marginal value differing from `len(mine)`, and 0 candidates have three marginals that differ from each other — which is visible in the published table itself: every row of docs/measurements/P7-attrition.md:67ff renders the same integer three times (`3 / 3 / 3`, `2 / 2 / 2`, `0 / 0 / 0`). The three baseline kill counts B0=143, B1=102, B2=108 and the union=210 are computed, published with careful caveats, and consumed by nothing. The one guard that touches this number, tests/unit/test_g2_g3_registry.py:140 `test_g2__a_baseline_never_competes_with_the_candidate`, asserts only that SOME subtraction happens; there is no control anywhere asserting that a baseline is load-bearing. Note also that `b0_template.kill_set(..., exclude=...)` — the parameter written for the correct fix (drop the candidate's own predicate id from B0's members) — is never passed by tools/measure/p7_attrition.py:60 or by baselines/build.py, so the intended mechanism is dead code while the substitute nullifies the gate.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python -c "
import sys,pathlib; sys.path[:0]=['src','tools/measure']
import p7_attrition as P
from cdfc.predicates.harvest import harvest
from cdfc.qualify import g2_kill
from cdfc.qualify.campaign_store import load
from cdfc.qualify.baselines.build import build
from collections import Counter
R=pathlib.Path('.'); r=harvest(P.FME); st=load('fme-v3-seed20260810',R/'reports/campaigns')
bl,_=build(st,campaign_id='fme-v3-seed20260810',class_of_predicate=r.class_of,clean_cells=P._clean_values(P.CLEAN),root=R/'reports/campaigns')
def funnel(b):
    c=Counter()
    for x in r.candidates:
        o=g2_kill.check(x,st,b,bar=g2_kill.KillBar.EXPERIMENT,repo=R); c['PASS' if o.passed else o.reason]+=1
    return c
E=g2_kill.BaselineResult(per_baseline={n:frozenset() for n in bl.names()})
U=g2_kill.BaselineResult(per_baseline={n:frozenset(st.class_of_mutant) for n in bl.names()})
print('real      ',dict(funnel(bl))); print('empty     ',dict(funnel(E))); print('omniscient',dict(funnel(U)))
"`

---

### [MAJOR] end-to-end — docs/measurements/P5-runtime-closure.md publishes four numbers `make run-fme` no longer produces

**file** `docs/measurements/p5-verdict-closure.json`:25  ·  **kind** claim-unbacked

**claim** The P5 closure measurement page and its JSON header themselves as "Warrant: MEASURED. Produced by `make run-fme`", but re-running that exact committed command in a pristine checkout of HEAD produces different numbers — the published page is a memory, not a measurement.

**evidence** In a pristine `git archive HEAD` copy (no sibling-agent contamination), running the committed producer and diffing against the committed artefact:

    $ diff /tmp/committed_p5.json $D/docs/measurements/p5-verdict-closure.json
    25,26c25,26
    <   "keys_preflighted": 1725,
    <   "keys_type_checked": 77,
    ---
    >   "keys_preflighted": 1713,
    >   "keys_type_checked": 66,
    31,32c31,32
    <       "P-0021",
    <       "P-0051"
    ---
    >       "P-0020",
    >       "P-0050"
    40c40
    <     "checks": 349,
    ---
    >     "checks": 348,
    DIFF_RC=1

The .md carries the same stale figures in prose: `| keys pre-flighted | 1725 |`, `| keys **type**-checked | 77 |`, `| predicates reading that cell | `P-0021`, `P-0051` |`, and "run state `INVALID`, 349 checks". The upstream cause (P8 dropping the wildcard COUNTIF, 349->348) IS recorded in docs/HARVEST-DELTA.md, and every other generator I re-ran (p9_ceiling, p9_runnability, p9_attrition, evaluator_arm1, p3_reproduction, field_surface, gen_contract, p7_attrition, build_instruments, gen_fault_model_doc, gen_proviso_markers_doc, cel_conformance, agreement_matrix) reproduces byte-identically — so this is one stale page, not systemic drift. Nothing regenerates it: `run-fme` appears in no aggregate target (`grep -n run-fme Makefile` -> only its own rule at line 131), and `make verify` does not call it. This is precisely the defect the Makefile's own `evaluator-arm1` comment says P9 repaired: "A measurement with no way to re-run it is a memory."

**reproduce** `D=/tmp/p5audit; rm -rf $D; mkdir -p $D; cd /Users/abishaikc/Gift && git archive HEAD | tar -x -C $D
cd $D && PYTHONPATH=$D/src /Users/abishaikc/Gift/.venv/bin/python tools/measure/p5_runtime_closure.py
cd /Users/abishaikc/Gift && git show HEAD:docs/measurements/p5-verdict-closure.json > /tmp/committed_p5.json
diff /tmp/committed_p5.json $D/docs/measurements/p5-verdict-closure.json`

---

### [MAJOR] end-to-end — ci/no-external-paths.sh is blind to the exact shape of the four machine-local paths that actually exist in the build

**file** `ci/no-external-paths.sh`:20  ·  **kind** shallow-proxy

**claim** The gate whose stated purpose is "a fresh clone on any other machine failed" requires a quote character immediately before the path, so it does not see `${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}` — the form used in ci/_roots.sh, ci/no-green-tick.sh, ci/no-bare-absence.sh and Makefile:1. It reports OK over all four.

**evidence** The four live instances, and the gate passing over them:

    $ grep -rn "/Users/" ci/ Makefile | grep -v '^ci/no-external-paths.sh'
    ci/_roots.sh:5:PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
    ci/no-bare-absence.sh:10:PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
    ci/no-green-tick.sh:8:PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
    Makefile:1:PY ?= /Users/abishaikc/Gift/.venv/bin/python
    $ bash ci/no-external-paths.sh
    no-external-paths: OK

Discriminating demonstration (in a scratchpad copy of HEAD, both probes appended to ci/no-bare-rate.sh and then restored):

    --- with QUOTED absolute path:
    GATE FAIL: a machine-local absolute path is referenced from the build:
      ci/no-bare-rate.sh:62:QUOTED="/Users/nobody/x"
    exit=1
    --- with UNQUOTED absolute path (same shape as ci/_roots.sh):
    no-external-paths: OK
    exit=0

The harm the gate names is live. With the hard-coded interpreter absent (i.e. any other machine):

    $ CDFC_PY=/nonexistent/python bash ci/no-green-tick.sh
    ci/_roots.sh: line 7: /nonexistent/python: No such file or directory
    exit=1

And the whole suite run in a fresh checkout that lacks a sibling `.venv` does not merely fail — two negative controls fail on their PRECONDITION, i.e. they stop being observable:

    FAILED tests/negative/test_nc_campaign.py::test_nc__Q64_no_bare_rate_reaches_a_surface
    FAILED tests/negative/test_nc_ci.py::test_nc__CI13_denylisted_runtime_licence_is_rejected
      AssertionError: precondition: green on the real set

Symlinking the venv into that same checkout makes both pass, confirming the cause is the interpreter path, not the code.

**reproduce** `cd /Users/abishaikc/Gift
grep -rn "/Users/" ci/ Makefile | grep -v '^ci/no-external-paths.sh'
bash ci/no-external-paths.sh; echo "gate rc=$?"
CDFC_PY=/nonexistent/python bash ci/no-green-tick.sh; echo "rc=$?"
# discriminating probe (restore afterwards):
D=/tmp/p5audit; cp $D/ci/no-bare-rate.sh /tmp/nbr.bak
cd $D; printf '\nQUOTED="/Users/nobody/x"\n' >> ci/no-bare-rate.sh; bash ci/no-external-paths.sh; echo rc=$?
cp /tmp/nbr.bak ci/no-bare-rate.sh; printf '\nUNQUOTED=${FOO:-/Users/nobody/x}\n' >> ci/no-bare-rate.sh; bash ci/no-external-paths.sh; echo rc=$?
cp /tmp/nbr.bak ci/no-bare-rate.sh`

---

### [MAJOR] end-to-end — ci/no-bare-rate.sh does not scan tools/ — the only place a coverage number reaches a reader today

**file** `ci/no-bare-rate.sh`:22  ·  **kind** shallow-proxy

**claim** The gate's ROOTS are `src/cdfc`, `docs/measurements`, `reports`. The CLI's `run` subcommand exits 2 and the report template has no renderer, so today the ONLY programs that print a coverage declaration to a human are tools/demo_template_diff.py, tools/demo_predicate_run.py and tools/measure/*.py — none of which the gate reads.

**evidence** Discriminating demonstration in a scratchpad copy of HEAD (both edits restored):

    --- baseline:
    no-bare-rate: OK
    --- bare rate PRINTED by the user-facing tool (appended to tools/demo_template_diff.py):
    no-bare-rate: OK
    exit=0
    --- same text as a COMMENT in src/cdfc (appended to src/cdfc/verdict/closure.py):
    GATE FAIL: a rate rendered without both integers of its fraction:
      src/cdfc/verdict/closure.py:190: # coverage 61.92%
    exit=1

So the gate fires on a dead comment inside the scanned root and stays silent on a `print()` that actually reaches the reader. The gate's own header states its subject as the surfaces "a rate can reach a reader from"; ROOTS names the one set that today reaches nobody and omits the one that does. No live offender exists in tools/ right now (I checked: the only two `%` hits in tools/*.py are prose and one already carries `3,512 of 7,500`), so this is an unguarded surface rather than a shipped bad number.

**reproduce** `D=/tmp/p5audit; cd $D; export CDFC_PY=/Users/abishaikc/Gift/.venv/bin/python
cp tools/demo_template_diff.py /tmp/dtd.bak; cp src/cdfc/verdict/closure.py /tmp/clo.bak
bash ci/no-bare-rate.sh
printf '\nprint("coverage 61.92%%")\n' >> tools/demo_template_diff.py; bash ci/no-bare-rate.sh; echo rc=$?
cp /tmp/dtd.bak tools/demo_template_diff.py
printf '\n# coverage 61.92%%\n' >> src/cdfc/verdict/closure.py; bash ci/no-bare-rate.sh; echo rc=$?
cp /tmp/clo.bak src/cdfc/verdict/closure.py`

---

### [MAJOR] end-to-end — The P5 CLI (`cdfc run`, `cdfc closure explain`) was never built, cli.py still says PHASE = "P0", and a unit test pins the gap

**file** `src/cdfc/cli.py`:19  ·  **kind** unrecorded-deviation

**claim** plan/03-phases-verdict.md §"CLI and outputs" specifies `cdfc run <filing> --template … --out runs/` and `cdfc closure explain <run_id>` as P5 deliverables. Neither exists; `cdfc run` exits 2 saying "not implemented at phase P0; it is built in P5" four phases after P5 shipped, and no docstring, docs/GATE-CHANGES.md entry, docs/decisions/ file or commit message records the deviation.

**evidence** Every subcommand, observed:

    $ for c in --version "" init ingest induce run qualify attest verify; do python -m cdfc.cli $c; echo EXIT=$?; done
    cdfc 0.0.1 (schema 14ef18f3, gates 75)            EXIT=0
    cdfc: no command given. Try `cdfc --version`. Phase P0.   EXIT=2
    cdfc: `init` is not implemented at phase P0; it is built in P1.     EXIT=2
    cdfc: `ingest` … P1.  `induce` … P2.  `run` … P5.  `qualify` … P7.  `attest`/`verify` … P11.   all EXIT=2

(`harvest`, added at P4, does work.) The machinery the plan asked for exists and is unreachable from the CLI: src/cdfc/evaluate/run.py:182 `write()` produces exactly `runs/<run_id>/{run.jsonl, run.db, manifest.json}`; I drove it directly and it emitted all three files with a well-formed manifest. Two consequences:

1. tests/unit/test_cli.py:14 asserts `main(["run"]) == 2` AND that the message contains "p5" — so the test now enforces that the P5 deliverable stays absent and will go red when it is built.
2. `src/cdfc/verdict/closure.py:173 explain()`, docstring "The seven terms, for `cdfc closure explain`", has zero callers and zero tests (`grep -rn "closure.explain\|explain(" src tools tests` finds only its own definition and an unrelated `Unbound.explain`); tools/measure/p5_runtime_closure.py:100-118 re-implements the same seven-term rendering by hand.

Searching for a record found none: `grep -rniE "cdfc run|cli\.py|subcommand" docs/*.md docs/decisions/` returns only a GATE-LIVENESS row, and the P5 commit c025320's message (which does record five other deviations in detail, including the E6 substitute) does not mention the CLI.

**reproduce** `cd /Users/abishaikc/Gift && export PYTHONPATH=src
for c in "--version" "" init ingest induce run qualify attest verify; do echo "=== cdfc $c"; .venv/bin/python -m cdfc.cli $c; echo "EXIT=$?"; done
grep -n 'PHASE = ' src/cdfc/cli.py
sed -n '1610,1622p' plan/03-phases-verdict.md
grep -rn "closure.explain\|explain(" src tools tests --include='*.py' | grep -v __pycache__
grep -rniE "cdfc run|cli\.py|subcommand" docs/ --include='*.md'`

---

### [MAJOR] measurements-and-docs — P5-runtime-closure.md and p5-verdict-closure.json do not reproduce: `make run-fme` today gives different numbers, and one of them is a published ledger row

**file** `docs/measurements/P5-runtime-closure.md`:29  ·  **kind** does-not-run

**claim** The committed P5 measurement publishes keys_preflighted=1725 / keys_type_checked=77, seeded-fault predicates P-0021 and P-0051, and 349 smoke checks; regenerating it from a pristine HEAD tree with its own committed command produces 1713 / 66, P-0020 and P-0050, and 348. The stale pair is cited by reports/validation-ledger.jsonl as metric `preflight.keys_type_checked` = 77/1725 with `command: make run-fme`, so a published number does not survive the command that claims to derive it.

**evidence** Exported HEAD with `git archive` (the working tree is being concurrently mutated by another process, so all verification was done in isolated exports). Ran tools/measure/p5_runtime_closure.py -- exit 0, printed `fraction 0.6192  settled 2320/3747  static 2794  runtime 2320 (delta -474)`. Diff of the regenerated file against `git show HEAD:docs/measurements/P5-runtime-closure.md`:

29,30c29,30
< | keys pre-flighted | 1725 |
< | keys **type**-checked | 77 |
---
> | keys pre-flighted | 1713 |
> | keys **type**-checked | 66 |
65,66c65,66
< | predicates reading that cell | `P-0021`, `P-0051` |
---
> | predicates reading that cell | `P-0020`, `P-0050` |
73c73
< ... run state `INVALID`, 349 checks.
---
> ... run state `INVALID`, 348 checks.

p5-verdict-closure.json moves identically (keys_preflighted 1725->1713, keys_type_checked 77->66, checks 349->348, seeded ids shifted). Re-running the generator a second time in the same export reproduced the NEW file byte-for-byte, so 1713/66 is the deterministic current answer and 1725/77 is a memory. The id shift P-0021->P-0020 / P-0051->P-0050 is consistent with P8's recorded 572->571 harvest change (docs/HARVEST-DELTA.md, the wildcard-COUNTIF declared skip) never having been followed by a P5 re-render. static_settled_cells 2794 and runtime 2320 are unchanged, so ledger rows 9 and 10 still hold; only row 11 is dead.

Nothing catches it: the full suite on a pristine HEAD export is GREEN (`pytest tests -q`, 0 failures with .venv symlinked), and `make verify` does not invoke `run-fme` -- verify runs lint/licence/greps/corpus-verify, host_fn_mutation.py, cel_conformance.py, pytest, nc_sweep.py, gate_liveness.py, and nothing else. No test regenerates this measurement and compares, unlike tests/unit/test_fault_model.py which does exactly that for docs/FAULT-MODEL-v3.md.

The deviation is not recorded: grep for P5-runtime-closure / keys_preflighted across docs/ and tests/ returns only plan/ references; docs/GATE-CHANGES.md, docs/HARVEST-DELTA.md and docs/decisions/ carry no note that the P5 page predates the P8 harvest change.

**reproduce** `rm -rf /tmp/cdfc-audit && mkdir -p /tmp/cdfc-audit && git -C /Users/abishaikc/Gift archive HEAD | tar -x -C /tmp/cdfc-audit && cd /tmp/cdfc-audit && PYTHONPATH=$PWD/src /Users/abishaikc/Gift/.venv/bin/python tools/measure/p5_runtime_closure.py && git -C /Users/abishaikc/Gift show HEAD:docs/measurements/P5-runtime-closure.md | diff - docs/measurements/P5-runtime-closure.md ; git -C /Users/abishaikc/Gift show HEAD:docs/measurements/p5-verdict-closure.json | diff - docs/measurements/p5-verdict-closure.json`

---

### [MAJOR] measurements-and-docs — docs/measurements/p4-harvest-distribution.json has no generator, no reader, and contradicts the .md beside it by 21 predicates

**file** `docs/measurements/p4-harvest-distribution.json`:9  ·  **kind** claim-unbacked

**claim** The committed JSON publishes `predicates_with_a_TEMPLATE_obligation: 592` and rows summing to 592, while the markdown it is named after publishes **571 / 571** for the same metric. Nothing in the repository writes the JSON, and the one test that names it asserts only its filename and never opens it -- so the disagreement is invisible to a green build and neither number in the JSON is re-derivable.

**evidence** Numbers read from HEAD so the concurrent mutator cannot affect them:

$ git show HEAD:docs/measurements/p4-harvest-distribution.json | python -c "..."
non_empty_workbooks 7
TEMPLATE_obl 592
sum of n over rows 592
rows 9

$ git show HEAD:docs/measurements/P4-harvest-distribution.md | grep -n 'TEMPLATE_obligation'
78:| `predicates_with_a_TEMPLATE_obligation / 571` | **571 / 571** | ...
(line 24: `| **total** | - | **571** | ...`; line 26: `Concentration: 487 of 571 ...`)

Who writes it: nobody. `make harvest` runs `cdfc harvest --all --out predicates/harvested --report docs/measurements/P4-harvest-distribution.md` plus an inline render of P4-both-ways.md. I ran both in a pristine export; the .md and the .json both compared byte-identical to HEAD -- i.e. the harvest left the JSON untouched, it did not confirm it.

Who reads it: only the filename.
$ grep -rn 'p4-harvest-distribution' --include='*.py' --include='*.sh' --include='Makefile' .
tests/golden/test_harvest_count.py:128:    assert P4_HARVEST_DISTRIBUTION.name == "p4-harvest-distribution.json"
src/cdfc/measure/paths.py:24:P4_HARVEST_DISTRIBUTION: Path = MEASUREMENTS_DIR / "p4-harvest-distribution.json"
That test's docstring calls itself "the transfer note lives in one file and names the number", but it asserts a string equality against a hard-coded literal -- a constant dressed as a check. It would pass if the JSON were deleted.

No glob consumer exists either: `grep -rn 'measurements' src tests tools ci --include='*.py' | grep -i 'glob|iterdir|rglob'` returns nothing.

**reproduce** `cd /Users/abishaikc/Gift && git show HEAD:docs/measurements/p4-harvest-distribution.json | /Users/abishaikc/Gift/.venv/bin/python -c "import json,sys; d=json.load(sys.stdin); print('TEMPLATE_obl', d['predicates_with_a_TEMPLATE_obligation'], '| sum rows', sum(r['n'] for r in d['rows']))" && git show HEAD:docs/measurements/P4-harvest-distribution.md | grep -n 'TEMPLATE_obligation' && grep -rn 'p4-harvest-distribution' --include='*.py' --include='*.sh' --include='Makefile' .`

---

### [MAJOR] negative-control-system — Gate 12 (`ci/catalogue-ids.sh`) swallows the failure of the subject it is registered to guard, and that subject is red right now

**file** `ci/catalogue-ids.sh`:8  ·  **kind** shallow-proxy

**claim** `ci/catalogue-ids.sh` is registered LIVE in ci/GATES.md as "`NC-` ids unique, defined, non-dangling, UTF-8" with `broken_build` = "duplicate an id in the registry", but the id half runs as `python3 plan/scripts/nc_audit.py plan >/dev/null 2>&1 || { echo "...advisory at P0"; }` — output discarded, exit code swallowed — so the gate's own registered broken_build cannot make it red, and the id audit is failing today with the gate green.

**evidence** $ python3 plan/scripts/nc_audit.py plan
  COUNTS
    DUPLICATE definitions     : 0        (must be 0)
    ORPHANS (def, never ref)  : 17        (must be 0)
    DANGLING (ref, never def) : 56        (must be 0)
  VERDICT: NOT CLEAN
  nc_audit exit=1
$ bash ci/catalogue-ids.sh
  catalogue-ids: audit reports issues (advisory at P0)
  catalogue-ids: OK (encoding clean)
  gate exit=0

Only the UTF-8/NUL half of the gate can fail, and that is the half the negative-control system exercises: tools/gate_liveness.py:48 binds gate 12 to NC-CI14, whose injector is `NulByteInPlanDoc`. So docs/measurements/P0-gate-liveness.json records gate 12 as "NC-CI14: OBSERVED RED" while three of the four properties named in its registry row are advisory and currently failing.

The exemption is unrecorded. `grep -rn "advisory at P0" docs/ ci/ plan/*.md` returns only the line inside the script itself; there is no entry in docs/GATE-CHANGES.md, docs/decisions/, or ci/GATES.md. The project's own rule at plan/01-validation-methodology.md:1936 reads "**Advisory is temporary and dated.** Every advisory gate carries the phase at which it becomes blocking" — this one carries a phase label (P0) that the build passed nine phases ago, with no dated argument.

**reproduce** `cd /Users/abishaikc/Gift
python3 plan/scripts/nc_audit.py plan; echo "nc_audit exit=$?"
bash ci/catalogue-ids.sh;              echo "gate exit=$?"
grep -rn 'advisory at P0' docs/ ci/ plan/*.md
git checkout -- plan/scripts/nc_audit_result.json   # nc_audit.py rewrites this`

---

### [MAJOR] p0-p2-foundation — ci/no-external-paths.sh misses the four machine-local absolute paths that are actually in the build, because its pattern requires a quote character immediately before the path

**file** `ci/no-external-paths.sh`:20  ·  **kind** shallow-proxy

**claim** Registry row 19 says "no machine-local absolute path in the build" and its recorded reason is that such a path "made the repository non-portable: a fresh clone on any other machine failed". The gate greps for `"/(Users|home|tmp)/` or `'/(Users|home|tmp)/` — a quote must be adjacent — so the four live instances, all of the form `PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"` and `PY ?= /Users/abishaikc/Gift/.venv/bin/python`, are invisible. The Makefile is not in the scan set at all.

**evidence** `grep -rn '/Users/' ci/_roots.sh ci/no-green-tick.sh ci/no-bare-absence.sh Makefile` returns 4 hits:
  ci/_roots.sh:5, ci/no-green-tick.sh:8, ci/no-bare-absence.sh:10, Makefile:1
and `bash ci/no-external-paths.sh` prints `no-external-paths: OK`, rc=0. The negative control NC-CI17's injector `ExternalFixturePath` appends `EXTERNAL = "/Users/somebody/corpus/f.xlsx"` — the quoted form only — so the gate is observed red on exactly the shape its pattern can see, and green on the shape the repository actually contains. NC-CI17's declared positive control is "the repository clones and runs on another machine", which finding #1 shows is false.

**reproduce** `cd /Users/abishaikc/Gift && grep -rn '/Users/' ci/_roots.sh ci/no-green-tick.sh ci/no-bare-absence.sh Makefile; bash ci/no-external-paths.sh; echo rc=$?`

---

### [MAJOR] p0-p2-foundation — Gates 28 and 48 are published as OBSERVED RED on evidence from injectors that leave them green

**file** `tools/gate_liveness.py`:76  ·  **kind** claim-unbacked

**claim** `docs/measurements/p0-gate-liveness.json` publishes `gates_with_an_observed_red: 74` of `74` live gates. For row 28 (`ci/no-regex-over-xml.sh`) the evidence is NC-E36, whose injector hand-edits `EVALUATION-CONTRACT.md`; for row 48 (`ci/no-wallclock-z3.sh`) it is NC-Q07, whose injector makes Z3's `unknown` read as ok. Neither injector touches either gate's subject, neither gate goes red under it, and no test in the repository ever executes either script.

**evidence** Under the bound injectors: `ContractTableEdit` -> `ci/no-regex-over-xml.sh` rc=0; `Z3UnknownIsOk` -> `ci/no-wallclock-z3.sh` rc=0. Both gates ARE functional — planting `re.findall(r"<c r=...")` in `src/cdfc/schema/styles_mask.py` gives rc=1, and planting `s.set("timeout", 5000)` in `src/cdfc/qualify/g3_degeneracy.py` gives rc=1 — so this is a wrong evidence binding, not a dead gate. `grep -rn 'no-regex-over-xml\|no-wallclock-z3' tests/` returns no test that runs either script, and neither `broken_build` cell in ci/GATES.md names a committed injector (both are prose conditions), so neither row's red observation is re-derivable by a committed command. tools/gate_liveness.py's docstring argues that a hand-maintained `OBSERVED_BY` list drifts and was therefore removed — its `EVIDENCE` dict is exactly such a hand-maintained list, and it is the thing that drifted.

**reproduce** `cd /Users/abishaikc/Gift && .venv/bin/python -c "import sys; sys.path.insert(0,'.')
from injectors import inject, run_gate, ContractTableEdit, Z3UnknownIsOk
with inject(ContractTableEdit()): print('gate28 rc=', run_gate('ci/no-regex-over-xml.sh'))
with inject(Z3UnknownIsOk()):    print('gate48 rc=', run_gate('ci/no-wallclock-z3.sh'))"`

---

### [MAJOR] p0-p2-foundation — xmlsafe.py claims the single-parser-factory control "walks the AST"; it is a two-string substring check, and a second unhardened parser passes it

**file** `src/cdfc/ingest/xmlsafe.py`:5  ·  **kind** claim-unbacked

**claim** `src/cdfc/ingest/xmlsafe.py`'s docstring states that "a second `etree.fromstring` call site anywhere in `src/cdfc/` defeats the control silently, so `test_nc__P08_only_one_parser_factory` walks the AST and fails the build if one appears". The test does `if needle in src` for the two literal strings `etree.XMLParser(` and `etree.fromstring(`. Importing lxml under any other name installs a second, unhardened door with the guard green — including `recover=True`, the setting the same docstring calls the one that "matters most".

**evidence** Appending to `src/cdfc/schema/styles_mask.py`:
  from lxml import etree as ET
  def _second_parse(b): return ET.fromstring(b, parser=ET.XMLParser(resolve_entities=True, recover=True))
`pytest tests/negative/test_nc_ingest.py::test_nc__P08_only_one_parser_factory` -> 1 passed (baseline: 1 passed; after restore: 1 passed). The committed injector `SecondParserFactory` plants `from lxml import etree` + `etree.fromstring(b)` — precisely the literal spelling the substring check matches — so the control is observed red only on the shape of the check.

**reproduce** `cd /Users/abishaikc/Gift && cp src/cdfc/schema/styles_mask.py /tmp/sm.bak && printf '\nfrom lxml import etree as ET\ndef _second_parse(b):\n    return ET.fromstring(b, parser=ET.XMLParser(resolve_entities=True, recover=True))\n' >> src/cdfc/schema/styles_mask.py && PYTHONPATH=src .venv/bin/python -m pytest tests/negative/test_nc_ingest.py::test_nc__P08_only_one_parser_factory -q; cp /tmp/sm.bak src/cdfc/schema/styles_mask.py`

---

### [MAJOR] p0-p2-foundation — ci/catalogue-ids.sh swallows its own primary subject as "advisory" — and that subject is currently failing

**file** `ci/catalogue-ids.sh`:8  ·  **kind** shallow-proxy

**claim** Registry row 12 reads "`ci/catalogue-ids.sh` — `NC-` ids unique, defined, non-dangling, UTF-8", LIVE. Three of those four subjects run through `plan/scripts/nc_audit.py` whose exit status is discarded by `|| { echo "catalogue-ids: audit reports issues (advisory at P0)"; }`. Only the UTF-8/NUL half can fail the gate, and the gate's evidence entry NC-CI14 exercises only that half. The audit is red right now: 17 orphan ids, 56 dangling ids, VERDICT NOT CLEAN.

**evidence** `bash ci/catalogue-ids.sh` prints `catalogue-ids: audit reports issues (advisory at P0)` followed by `catalogue-ids: OK (encoding clean)` and exits 0. `python3 plan/scripts/nc_audit.py plan` prints `DUPLICATE definitions: 0`, `ORPHANS (def, never ref): 17 (must be 0)`, `DANGLING (ref, never def): 56 (must be 0)`, `VERDICT: NOT CLEAN`, rc=1. plan/02-phases-foundation.md:1111 makes this a P0 EXIT criterion ("every `NC-` id in `plan/*.md` is defined in exactly one document and ... no dangling reference") and plan/01 names four meta-tests required before the first entry; only two of them exist (`test_nc_meta__ids_are_unique`, `test_nc_meta__no_orphan_guard`, both over `catalogue.yaml` alone). `test_nc_meta__ids_are_defined_in_the_registry` and `test_nc_meta__no_dangling_reference` do not exist anywhere, and the deviation appears in none of docs/GATE-CHANGES.md, docs/CATALOGUE-CORRECTIONS.md (absent), docs/decisions/ or any measurement file.

**reproduce** `cd /Users/abishaikc/Gift && bash ci/catalogue-ids.sh; echo rc=$?; python3 plan/scripts/nc_audit.py plan; echo rc=$?; git checkout -- plan/scripts/nc_audit_result.json; grep -rn 'no_dangling_reference\|ids_are_defined_in_the_registry' tests/ || echo 'meta-tests absent'`

---

### [MAJOR] p3-evaluator — "reproduced, equal to the regulator's cached value | 475" never compares anything to the cached value

**file** `tools/measure/p3_reproduction.py`:100  ·  **kind** shallow-proxy

**claim** tools/measure/p3_reproduction.py:100 computes `agree = sum(1 for k in cached if k in grid.values and k not in grid.not_run)` — the count of formula cells for which the evaluator produced ANY value — and renders it under the label "reproduced, equal to the regulator's cached value". The variable `want`/the cached string is never read. The number is identical when every value is wrong.

**evidence** I replaced `SUM` in src/cdfc/calc/functions.py with `return Decimal(999999)`. The live arm-1 comparison then reports 155 of 505 FME cells DISAGREEING (`make evaluator-arm1`: `Reporting_Format_for_Fund_Management_E  505  320 agree  155 dis  30 n/run`). With that same mutant in place, `make p3-reproduction` regenerated docs/measurements/P3-cached-value-reproduction.md still reading `| reproduced, equal to the regulator's cached value | 475 |`. The row is unchanged by an evaluator that is wrong on a third of the workbook. Source restored (`cp` backup) and both docs restored via `git checkout -- docs/measurements/ reports/validation-ledger.jsonl`.

**reproduce** `cd /Users/abishaikc/Gift && cp src/cdfc/calc/functions.py /tmp/fn.bak && .venv/bin/python -c "
from pathlib import Path;p=Path('src/cdfc/calc/functions.py');s=p.read_text()
p.write_text(s.replace('def SUM(*args: Any) -> Any:','def SUM(*args: Any) -> Any:\n    return Decimal(999999)',1))"
make evaluator-arm1 | grep Reporting        # 320 agree / 155 disagree -> the evaluator IS wrong
make p3-reproduction >/dev/null; grep 'equal to the regulator' docs/measurements/P3-cached-value-reproduction.md   # still 475
cp /tmp/fn.bak src/cdfc/calc/functions.py && git checkout -- docs/measurements/ reports/validation-ledger.jsonl`

---

### [MAJOR] p3-evaluator — test_eval__arm1_has_zero_disagreements_on_the_corpus reads a committed JSON that no CI target regenerates

**file** `tests/unit/test_evaluate.py`:161  ·  **kind** shallow-proxy

**claim** The test the catalogue treats as "the gate, run as a test" does not run arm 1. It json.loads docs/measurements/p3-evaluator.json and asserts `disagree == 0` on whatever was last committed. `make all` and `make verify` never invoke `tools/measure/evaluator_arm1.py`, so in CI the test is an assertion about a file, not about the evaluator.

**evidence** With `SUM` mutated to `return Decimal(999999)` — an evaluator wrong on 155 of 505 FME cells and 464 corpus cells — `pytest tests/unit/test_evaluate.py::test_eval__arm1_has_zero_disagreements_on_the_corpus` passed (`.  [100%]`). Only after I additionally ran `make evaluator-arm1` to refresh the JSON did it go red. Makefile:9 `all: lint licence greps corpus-verify contract unit golden determinism negative gates` and Makefile:108-115 `verify:` (which explicitly comments "Producers first. A consumer that runs before its producer either ... reads a stale one and reports a number nobody computed this run" and then runs only tools/host_fn_mutation.py and tools/cel_conformance.py as producers) contain neither `evaluator-arm1` nor `p3-reproduction`. This is the identical failure already recorded at Makefile:162-165 for the same file; a make target was added but never wired into a target CI runs. tools/measure/cached_values.py is in the same position (no make target, not in all/verify) — it does still reproduce byte-identically today.

**reproduce** `cd /Users/abishaikc/Gift && cp src/cdfc/calc/functions.py /tmp/fn.bak && .venv/bin/python -c "
from pathlib import Path;p=Path('src/cdfc/calc/functions.py');s=p.read_text()
p.write_text(s.replace('def SUM(*args: Any) -> Any:','def SUM(*args: Any) -> Any:\n    return Decimal(999999)',1))"
PYTHONPATH=src .venv/bin/python -m pytest 'tests/unit/test_evaluate.py::test_eval__arm1_has_zero_disagreements_on_the_corpus' -q   # PASSES
cp /tmp/fn.bak src/cdfc/calc/functions.py
grep -n '^all:' -A1 Makefile; sed -n '108,116p' Makefile      # neither producer is in all/ verify`

---

### [MAJOR] p3-evaluator — Gate row 65 (G-EVAL) is counted "OBSERVED RED" on an injector that edits facts/units.py and leaves its guard green

**file** `tools/gate_liveness.py`:110  ·  **kind** shallow-proxy

**claim** tools/gate_liveness.py:110 binds registry row 65 — G-EVAL's independence label — to catalogue entry NC-R12, whose injector `ToleranceUnitsSilentlyReconciled` rewrites `HALF_ULP` in src/cdfc/facts/units.py. That injector cannot make row 65's named guard fail, yet gate_liveness.py reports "OBSERVED RED: 74 of 74 live gates" and writes gates_with_an_observed_red=74 into docs/measurements/p0-gate-liveness.json. ci/GATES.md:92 names row 65's broken_build as "set `ARM2.oracle_author` to `cdfc`" — no injector in injectors/__init__.py does that.

**evidence** I applied NC-R12's injector via the project's own `inject()` context manager and ran row 65's guard: `row-65 guard under NC-R12's injector -> returncode 0` (`.  [100%]`). The guard stays green under the injector that is its liveness evidence. `PYTHONPATH=src .venv/bin/python tools/gate_liveness.py` nonetheless prints `OBSERVED RED         : 74 of 74 live gates` with 65 in the live list. Row 65's own test file does contain a genuine positive control (`test_geval__the_label_appears_when_the_author_is_ours`, which dataclasses.replace's the author and asserts the label returns) — so the label mechanism is guarded; what is not backed is the liveness ledger's count.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python -c "
import subprocess,sys;sys.path.insert(0,'.')
from injectors import BY_NAME, inject
with inject(BY_NAME['ToleranceUnitsSilentlyReconciled']()):
    r=subprocess.run(['.venv/bin/python','-m','pytest','tests/contract/test_contract_geval.py::test_arm_two_author_is_not_the_evaluator_author','-q','--no-header'],capture_output=True,text=True,env={'PYTHONPATH':'src','PATH':'/usr/bin:/bin'})
    print('returncode',r.returncode)"
PYTHONPATH=src .venv/bin/python tools/gate_liveness.py | grep 'OBSERVED RED'
git checkout -- docs/measurements/p0-gate-liveness.json`

---

### [MAJOR] p4-predicates — Static key extraction is unsound for a parenthesised member access: `(filing.a).b` reports `filing.a`, the runtime reads `filing.a.b`, and the predicate returns PASS over a key pre-flight never checked

**file** `src/cdfc/predicates/ast_walker.py`:141  ·  **kind** correctness

**claim** `_Walker.resolve` returns None for a member access whose base is a parenthesised expression, so `walk` falls through and records only the inner path; `check_subset` admits the construct, `check_declared_keys` therefore agrees BOTH ways on a predicate whose runtime read set is strictly larger than its declared set, and `preflight` -- which guards `p.schema_keys` only -- lets `evaluate_one` reach order 9 PASS over an unguarded key. This is exactly the defect `UndeclaredKeyRead` and preflight.py's "the declared set IS the read set" claim exist to make impossible.

**evidence** Static vs dynamic, measured against the project's own instrumented runtime:

    (filing.a).b == 1
      static  : ['filing.a']
      observed: ['filing.a.b']
      ESCAPED : ['filing.a.b']
    (filing.flag ? filing.p : filing.q).z == 2
      static  : ['filing.flag', 'filing.p', 'filing.q']
      observed: ['filing.flag', 'filing.p.z']
      ESCAPED : ['filing.p.z']

Discriminating pair -- one pair of parentheses is the whole difference:

    REFUSED UndeclaredKeyRead : filing.zz.a.b == 1 || filing.zz.ok
    PASSES both-ways          : (filing.zz.a).b == 1 || filing.zz.ok

End to end through the real run path, with `filing.zz.a.b` ABSENT from the fact set:

    check_subset: ADMITTED all three slots
    check_declared_keys: PASSES BOTH WAYS. static read set = ['filing.zz.a', 'filing.zz.ok']
    preflight: PreflightResult(proceed=True, missing=(), mistyped=(), keys_checked=2, keys_type_checked=0)
    VERDICT: PASS order 9 keys_checked 2

The two controls that exist for this cannot see it. tests/differential/test_diff__static_keys_cover_dynamic_reads.py runs a hand-written 10-element CASES list with no parenthesised expression in it; tests/property/test_prop_ast_walker.py's `_comprehension()` generator emits no parentheses either. Full suite is green (976 tests, exit 0) with the escape present.

SCOPE, measured: the published 571/571 both-ways number is NOT affected. I scanned all 1,713 slots of the 571 harvested candidates for the shape; the 195 hits on `\)\s*\.` are all `.filter(...).map(...)` macro chains, which `resolve` handles correctly via `_macro_of`. The hole bites hand-authored and relation envelopes, and it falsifies the general claim rather than the current number.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=/Users/abishaikc/Gift/src .venv/bin/python -c "
import dataclasses
from cdfc.predicates.ast_walker import check_declared_keys, TemplateSchema
from cdfc.predicates.cel_profile import check_subset
from cdfc.evaluate.celrt import CelRuntime
from cdfc.evaluate.runner import evaluate_one
from cdfc.facts.view import FactSet
from cdfc.predicates.host_fns import default_registry
from cdfc.measure.p5_run import fme_harvest, promote
p = dataclasses.replace(promote(fme_harvest().candidates[0]), id='P-ESCAPE',
    schema_keys=('filing.zz.a','filing.zz.ok'), applicable='has(filing.zz.a)',
    expr='(filing.zz.a).b == 1 || filing.zz.ok', witness='[filing.zz.a]')
[check_subset(getattr(p,s), slot=s) for s in ('applicable','expr','witness')]
check_declared_keys(p)
chk = evaluate_one(p, facts=FactSet({'zz':{'a':{'c':5},'ok':True}},{}),
    schema=TemplateSchema({'filing.zz.a':frozenset({'S!A1'}),'filing.zz.ok':frozenset({'S!A2'})},'t'),
    rt=CelRuntime(profile_version='P5', host_fns=default_registry()))
print(chk.state, chk.order, 'keys_checked', chk.keys_checked)
"
# prints: PASS 9 keys_checked 2   -- a PASS over filing.zz.a.b, which pre-flight never checked

cd /Users/abishaikc/Gift && PYTHONPATH=/Users/abishaikc/Gift/src .venv/bin/python -c "
from cdfc.evaluate.celrt import CelRuntime
from cdfc.facts.view import FactView
from cdfc.predicates.ast_walker import read_keys
from cdfc.predicates.host_fns import default_registry
rt = CelRuntime(profile_version='P4', host_fns=default_registry())
src='(filing.a).b == 1'
print('static  :', sorted(read_keys(src, slot='expr')))
print('observed:', sorted(rt.observed_keys(rt.compile(src, slot='expr'), filing=FactView({'a':{'b':1}}, root='filing'), template=FactView({}, root='template'))))
"`

---

### [MAJOR] p5-evaluate-verdict — docs/measurements/P5-runtime-closure.md is not re-derivable by its own committed command

**file** `docs/measurements/P5-runtime-closure.md`:29  ·  **kind** claim-unbacked

**claim** The file declares "Warrant: MEASURED. Produced by `make run-fme`", but re-running `make run-fme` changes four published values — the measurement was not regenerated after a later phase moved the harvest.

**evidence** Verified twice: once in the working tree and once in a pristine `git archive HEAD` export (so a concurrent agent's in-flight mutation cannot explain it). Diff of the regenerated file against the committed one:

  | keys pre-flighted |   1725 -> 1713
  | keys type-checked |     77 -> 66
  | predicates reading/FAILING `1. Introduction!C54` | P-0021, P-0051 -> P-0020, P-0050
  | smoke filing checks | 349 -> 348

The same four move in `docs/measurements/p5-verdict-closure.json` (`keys_preflighted`, `keys_type_checked`, `seeded.expected_failures`, `seeded.observed_failures`, `smoke.checks`). Nothing checks this file: `grep -rn 'p5-verdict-closure' tests/ ci/ Makefile` matches only the generator itself. The golden test computes the seeded predicate ids live via `predicates_reading(SEED_CELL)`, so it stays green while the published ids are wrong. (I restored both files with `git checkout --` afterwards.)

**reproduce** `cd /Users/abishaikc/Gift && cp docs/measurements/P5-runtime-closure.md /tmp/P5-orig.md && make run-fme && git diff docs/measurements/P5-runtime-closure.md docs/measurements/p5-verdict-closure.json && git checkout -- docs/measurements/P5-runtime-closure.md docs/measurements/p5-verdict-closure.json`

---

### [MAJOR] p6-campaign — The headline K/O = 258/761 does not re-derive: `make campaign` on HEAD produces 257/761

**file** `docs/measurements/P6-fault-model-v3.md`:37  ·  **kind** claim-unbacked

**claim** docs/measurements/P6-fault-model-v3.md publishes `K/O = 258/761` as MEASURED and re-derivable by `make campaign`; re-running the campaign at HEAD produces 257/761 — the single F10 kill is gone, because the predicate that produced it (P-0009) is a different predicate at HEAD.

**evidence** Re-ran tools/measure/p6_campaign.py with OUT/DOC redirected outside the repo (no other change). Result table identical to the committed one for every class except F10:
  committed manifest F10: {G:32, U:0, I:0, O:32, R:0, K:1}, TOTAL K=258, K/O = 258/761
  re-run          F10: {G:32, U:0, I:0, O:32, R:0, K:0}, TOTAL K=257, K/O = 257/761
Set difference of (operator_id, sites) over killed.jsonl: in old not new = [('F10.a', ('1. Introduction!G55',))]; in new not old = [].
Isolated: re-seeding that exact mutant from its recorded `edits` and evaluating with the current harvest gives
  committed row: F10.a ['1. Introduction!G55'] killed_by ['P-0009']
  predicates that FAIL at HEAD: ()
The environment matches the published state otherwise (348 candidates, same as the P7 funnel's `entered 348`; site universe 4252 and the sampling-rule string reproduce byte-for-byte).

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python - <<'EOF'
import json
from pathlib import Path
from cdfc.measure.p5_run import INDEPENDENT, fme_harvest, promote
from cdfc.measure.p6_kill import killer
from cdfc.qualify.observability import grid_of, cone_for
from cdfc.qualify.surgery import CellEdit, seed_mutant
row=next(json.loads(l) for l in open('reports/campaigns/fme-v3-seed20260810/killed.jsonl') if json.loads(l)['fault_class']=='F10')
print('committed:',row['operator_id'],row['sites'],'killed_by',row['killed_by'])
h=fme_harvest(); run=killer([promote(c) for c in h.candidates], h.schema)
ce=[CellEdit(e['sheet_name'],e['ref'],e['old_xml'],e['new_xml'],e['operator_id']) for e in row['edits']]
tgt=Path('/tmp/f10.xlsx'); seed_mutant(INDEPENDENT,ce,tgt,fault_class='F10',operator_id=row['operator_id'],seed=1)
ed=[(e['sheet_name'],e['ref']) for e in row['edits']]
print('FAILs at HEAD:', run(tgt, grid_of(tgt,cone=cone_for(INDEPENDENT,ed),baseline=grid_of(INDEPENDENT)), ed))
EOF
# full re-derivation (~25 min): make campaign   [overwrites reports/campaigns and the measurement doc — git checkout afterwards]`

---

### [MAJOR] p6-campaign — "Control-arm spurious fires: 0" is a constant, not a measurement — the runner never evaluates a predicate on an unreachable mutant, so the count it is read from cannot be non-zero

**file** `src/cdfc/qualify/runner.py`:137  ·  **kind** shallow-proxy

**claim** P7's funnel publishes `control-arm spurious fires: 0 — the threshold is exactly zero` as MEASURED, computed as the number of rows in killed.jsonl with `reachable == false`; but `run_one` only calls `self.evaluate(...)` when `reachable` is True, so `killed_by` is empty for every unreachable mutant and the count is 0 for any predicate set whatsoever — including a predicate that fires on every mutant, which is exactly the flag-everything baseline the control arm exists to reject (plan NC-Q06c).

**evidence** runner.py:137 `if obs is Observability.OBSERVABLE and reachable: killed = tuple(self.evaluate(...))`; write_reports puts a row in killed.jsonl only `if o.killed`. tools/measure/p7_attrition.py:61-64: `spurious = sum(1 for row in killed_rows if row.get('reachable') is False)` — over killed.jsonl only.
On the committed campaign: killed rows 258, killed with reachable==False: 0, unreachable.jsonl rows with non-empty killed_by: 0.
Demonstrated with an evaluator that FAILS on every mutant, run on a site the committed campaign marked unreachable:
  site ['1. Introduction!C100'] operator F05.a campaign said reachable = False
  observability: OBSERVABLE reachable: False killed_by: ()
  killed.jsonl rows: 0   control-arm spurious fires as p7_attrition counts them: 0
Separately, the plan's actual control arm — `sites.partition()`, which excludes `upstream_closure(read_set(p))` per predicate — is called by no production code: `grep -rn 'partition(' src tools` finds it only in sites.py's own error string; every caller is in tests/unit/test_sites.py. What the campaign computes instead is `distinguishing ∩ (union of every predicate's read set)`, which is not the per-predicate quantity the zero threshold was derived for.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python - <<'EOF'
import json
from pathlib import Path
from cdfc.measure.p5_run import FME, INDEPENDENT, fme_harvest, promote
from cdfc.predicates.ast_walker import bound_cells
from cdfc.qualify.runner import CampaignRunner, summarise, write_reports
from cdfc.qualify.fault_model import Site, Dtype, by_id
h=fme_harvest(); preds=[promote(c) for c in h.candidates]
read=frozenset().union(*(bound_cells(p,h.schema) for p in preds))
row=json.loads(open('reports/campaigns/fme-v3-seed20260810/unreachable.jsonl').readline())
sh,rf=row['edits'][0]['sheet_name'],row['edits'][0]['ref']
out=Path('/tmp/flagall')
r=CampaignRunner(base=FME, clean=INDEPENDENT, out_dir=out,
                 evaluate=lambda *a,**k:("P-FLAG-EVERYTHING",), read_cells=read)
op=[o for o in by_id('F05').operators if o.id=='F05.a'][0]
o=r.run_one('F05',op,[(Site(sh,rf,Dtype.MILLI_USD_MILLION),424242)],1)
print('reachable:',o.reachable,'killed_by:',o.killed_by)
c=summarise([o],campaign_id='t',site_set_digest='',evaluator_version='',base_sha256='',sampling_rule='')
t=write_reports(c,[o],out)
killed=[x for x in (t/'killed.jsonl').read_text().splitlines() if x.strip()]
print('spurious fires as p7_attrition counts them:', sum(1 for x in killed if json.loads(x)['reachable'] is False))
EOF
# and: python3 -c "import json;rows=[json.loads(l) for l in open('reports/campaigns/fme-v3-seed20260810/killed.jsonl')];print(sum(1 for r in rows if r['reachable'] is False))"`

---

### [MAJOR] p7-gates — All 71 `g2.no_margin_over_baselines` rejections — 23.5% of the funnel's attrition — are caused by a last-write-wins collapse in `class_of_mutant`, and the published remedy text for them is false

**file** `src/cdfc/qualify/campaign_store.py`:115  ·  **kind** correctness

**claim** `campaign_store.load` stores one fault class per mutant digest, but 48 of the 210 observable mutant digests appear in `killed.jsonl` under TWO fault classes; the later row overwrites the earlier, so `mutants_in(mutants(p), claimed)` returns ∅ for predicates whose only claimed-class kills landed on an overwritten digest — even though `kills(p, claimed_class) > 0`.

**evidence** src/cdfc/qualify/campaign_store.py:115 does `class_of[row["mutant_sha256"]] = row["fault_class"]`. Measured in reports/campaigns/fme-v3-seed20260810/killed.jsonl: 258 rows, 210 distinct digests, 48 digests carrying >1 fault class. Example: digest 4edad3ff78a0 is recorded once as F05 and once as F07, both crediting P-0022; `class_of` keeps F07, P-0022 claims F01..F05, so `mine` is empty while `kr_claimed` reads `1/388` — and it is rejected with `g2.no_margin_over_baselines`. Rebuilding the digest→class map as a SET and re-testing every no-margin rejection: 71 of 71 would have a non-empty claimed-class kill set under the correct map, 0 are genuine. So docs/measurements/P7-attrition.md publishes 71 rejections under the remedy "a free baseline catches everything this catches; the predicate is not doing the work" (g2_kill.py:68) when no baseline was involved in any of them. This also inflates `kr_all_classes`: those 48 mutants are counted twice in the numerator (P-0022 reads `2/761` for one workbook).

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python -c "
import json,pathlib,sys,collections; sys.path[:0]=['src','tools/measure']
import p7_attrition as P
from cdfc.predicates.harvest import harvest
from cdfc.qualify.campaign_store import load
r=harvest(P.FME); st=load('fme-v3-seed20260810', pathlib.Path('reports/campaigns'))
rows=[json.loads(l) for l in open('reports/campaigns/fme-v3-seed20260810/killed.jsonl') if l.strip()]
true_cls=collections.defaultdict(set)
for row in rows:
    if row.get('observability')=='OBSERVABLE': true_cls[row['mutant_sha256']].add(row['fault_class'])
print('digests with >1 class:', sum(1 for v in true_cls.values() if len(v)>1), 'of', len(true_cls))
ov=gen=0
for c in r.candidates:
    cl=tuple(c.claims_fault_classes)
    if sum(st.kills(c.id,x) for x in cl)==0: continue
    if st.mutants_in(st.mutants(c.id),cl): continue
    (ov:=ov) ; 
    if {d for d in st.mutants(c.id) if true_cls[d]&set(cl)}: ov+=1
    else: gen+=1
print('no_margin rejections: overwrite-caused=',ov,' genuine=',gen)
"`

---

### [MAJOR] p8-corpus-ffr — The corpus firewall's RULE 1 test exempts the very corpus it guards, so it cannot fail

**file** `tests/test_corpus_firewall.py`:61  ·  **kind** shallow-proxy

**claim** tests/test_corpus_firewall.py::test_corpus_is_not_importable claims "Nothing under src/ or tests/ reads the corpus except through fixtures/corpus_manifest.json", but its predicate carries an undocumented `"corpus/blind-fill" not in v` exemption covering the entire blind-fill corpus tree — the only corpus the firewall exists for — so no reference to it can ever be reported as an offender.

**evidence** corpus/ contains exactly two subdirectories, blind-fill and instruments, and BOTH are exempted (lines 61-62), so the offenders list is empty by exemption rather than by the rule holding. Re-running the same AST predicate with the exemptions varied: as-shipped -> 0 offenders; without the blind-fill exemption -> 1 offender (`tools/corpus/blind_fill_probe.py: 'corpus/blind-fill/fills'`, a scanned root already reading the corpus directly); with no exemptions -> 6. Decisive demonstration: I appended `CONTAMINATION = "corpus/blind-fill/fills/fill_001.json"` to src/cdfc/qualify/wilson.py — a src module reading the corpus directly, exactly what RULE 1 forbids — and the test PASSED (`.  [100%]`, 1 passed). File restored; git status clean. The two path exemptions carry no comment; the only comment above them explains the unrelated per-filename skips. Nothing in docs/GATE-CHANGES.md, docs/decisions/D-P8-01, or the module docstring records them. NC-N03 is the only catalogue entry naming this file and it guards a different test; there is no injector and no negative control for RULE 1 at all.

**reproduce** `cd /Users/abishaikc/Gift && printf '\nCONTAMINATION = "corpus/blind-fill/fills/fill_001.json"\n' >> src/cdfc/qualify/wilson.py && PYTHONPATH=src .venv/bin/python -m pytest tests/test_corpus_firewall.py::test_corpus_is_not_importable -q ; git checkout -- src/cdfc/qualify/wilson.py`

---

### [MAJOR] p8-corpus-ffr — docs/measurements/P8-ffr.md publishes an absence claim its own superseding decision falsified

**file** `tools/measure/p8_ffr.py`:285  ·  **kind** claim-unbacked

**claim** The published P8 measurement states "`REGISTER-DERIVED` is not built. It needs the IFSCA register, whose terms of use have not been read, so the 87-of-228 regex exhibit is unmeasured here (D-P8-02)" — but D-P8-02 is titled "SUPERSEDED 13 Aug 2026: `REGISTER-DERIVED` is built", the snapshot is committed, and the exhibit measures 87 of 229 first-hand. The false sentence is hardcoded in the generator, so `make ffr` reproduces it.

**evidence** docs/measurements/P8-ffr.md:110-111 carries the claim verbatim; tools/measure/p8_ffr.py:285-286 is the hardcoded source string. Against it: docs/decisions/D-P8-02-no-register-derived.md line 1 reads `# D-P8-02 — SUPERSEDED 13 Aug 2026: REGISTER-DERIVED is built`, and states the terms WERE looked for (robots.txt 404, no clause) and that the spec's `87 of 228` came from a lane that lost one record. fixtures/register/fme-register__54f0dbdc.json is committed; src/cdfc/qualify/corpus/register_derived.py is 146 lines of live code. Re-derived first-hand this session: `n= 229 resolving= 229 regex fires= 87 membership fires= 0 stragglers= 3`. So the published surface asserts (a) not built — false, (b) terms unread — false per D-P8-02, (c) unmeasured — false, and (d) the wrong denominator 228 instead of the measured 229. Commit 043572e is titled "P8-B2: REGISTER-DERIVED, built — 87 of 229 measured first-hand"; the generator string was never updated with it.

**reproduce** `cd /Users/abishaikc/Gift && grep -n 'REGISTER-DERIVED. is not built' docs/measurements/P8-ffr.md tools/measure/p8_ffr.py ; head -1 docs/decisions/D-P8-02-no-register-derived.md ; PYTHONPATH=src .venv/bin/python -c "from cdfc.qualify.corpus import register_derived as rd; s=rd.load(); print('n',s.n,'regex fires',len(rd.format_regex_fires(s)))"`

---

### [MAJOR] p9-probes — The degree map assigns MONEY (τ=5n) to 130 name/type/authorisation-number cells, licensed by a different column's header

**file** `src/cdfc/probes/degree.py`:256  ·  **kind** correctness

**claim** `degree.py` claims "the tolerance is zero unless the cell is *positively established* as money", "**Nearest marker wins**", and "Every assignment names the regulator's own words and the cell they are in". Level 3 of `assign()` searches for a parenthesised unit *anywhere in the table*, so a column with no unit of its own inherits an unrelated column's. 130 of the 223 published `MONEY_MARKER` cells are on text columns — `Type of Scheme`, `Open-Ended / Close-Ended`, `Name of Scheme`, `IFSCA Authorisation Number of Scheme` — each licensed by `'2. Summary'!G4` = "Stated Target Corpus … (USD Million)", a column seven positions away. The published table `MONEY_MARKER | 223 | 1` in `docs/measurements/P9-template-diff-ceiling.md` is therefore not a count of money cells.

**evidence** `'2. Summary'!D8` has formula `='1. Introduction'!G57` (Type of Scheme, a dropdown string) and is assigned `degree=1 MONEY_MARKER` on the authority of `'2. Summary'!G4`:
```
2. Summary!D8 -> 1 MONEY_MARKER 2. Summary!G4 'Stated Target Corpus (Only for Close-Ended Schemes)\n(USD Million)'
2. Summary col D (Type of Scheme):               10 cells at degree 1 MONEY
2. Summary col E (Open-Ended / Close-Ended):     10 cells at degree 1 MONEY
2. Summary col C (Name of Scheme):               10 cells at degree 1 MONEY
2. Summary col B (IFSCA Authorisation Number):    9 cells at degree 1 MONEY
name/type/authnum-column cells assigned MONEY: 130   (of 223)
money assignments whose evidence is in another column: 171 (of 223)
```
The mechanism has two halves: level 2 (`degree.py:248-254`) breaks on the first non-empty cell above, and in `2. Summary` / `3. Portfolio` / `4. Investors` the blank's own `'NA'` placeholder rows sit directly above, masking the real header; level 3 then grabs the nearest parenthesised unit in the table regardless of column.

The guard is a count, not a content check. `tests/unit/test_degree.py:75` pins `bases["MONEY_MARKER"] == 223` and `test_degree__every_money_cell_names_its_evidence` (line 80) asserts only that `evidence_cell`/`evidence_text` are non-empty — never that the string names *that cell's* unit. That is exactly the count-agrees-with-a-pin shape.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python -c "
from pathlib import Path
from cdfc.probes.degree import degree_map, HEADER_REACH
from cdfc.probes.workbook import cell_text
from cdfc.schema.stable_keys import split_ref
FME=Path('fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx')
dm=degree_map(FME); t=cell_text(FME)
a=dm['2. Summary!D8']; print('2. Summary!D8 ->',a.degree,a.basis,a.evidence_cell,repr(a.evidence_text))
print('D4 header text:', repr(t['2. Summary']['D4']))
bad=[k for k,x in dm.items() if x.degree==1 and split_ref(k.split('!',1)[1])[0] in ('B','C','D','E') and k.split('!',1)[0] in ('2. Summary','3. Portfolio','4. Investors')]
print('name/type/authnum cells assigned MONEY:', len(bad), 'of', sum(1 for x in dm.values() if x.degree==1))
"`

---

### [MINOR] measurements-and-docs — src/cdfc/measure/paths.py: 4 of 9 measurement-path constants name files that do not exist, and one misspells the file it exists to canonicalise

**file** `src/cdfc/measure/paths.py`:21  ·  **kind** claim-unbacked

**claim** The module docstring says other modules import these constants "instead of re-typing a filename" because "a measurement written to a path one module spells differently from another is a measurement nobody reads." In fact seven of the nine constants are imported by nothing, four name files that were never produced, and P1_READER_AGREEMENT spells the P1 file `p1-reader-agreement.json` while the file that exists and is produced by tools/measure/agreement_matrix.py is `p1-agreement.json` -- the exact defect the docstring claims the module prevents.

**evidence** $ existence check over the nine declared paths
p0-gate-liveness.json          EXISTS
p1-reader-agreement.json       MISSING   <-- actual file is p1-agreement.json
p2-field-surface.json          EXISTS
p3-evaluator.json              EXISTS
p4-harvest-distribution.json   EXISTS
p5-verdict-closure.json        EXISTS
p6-fault-campaign.json         MISSING
p7-attrition-funnel.json       MISSING
p8-ffr.json                    MISSING

$ usage count outside paths.py
P0_GATE_LIVENESS: 4
P1_READER_AGREEMENT: 0
P2_FIELD_SURFACE: 0
P3_EVALUATOR: 0
P4_HARVEST_DISTRIBUTION: 2   (both are the filename-only assertion in the previous finding)
P5_VERDICT_CLOSURE: 0
P6_FAULT_CAMPAIGN: 0
P7_ATTRITION_FUNNEL: 0
P8_FFR: 0

Only two importers exist repo-wide: tools/gate_liveness.py (P0) and tests/golden/test_harvest_count.py (P4). tools/measure/p5_runtime_closure.py, tools/measure/agreement_matrix.py, tools/measure/p7_attrition.py and tools/measure/p8_ffr.py each re-type their own output filenames instead. No test asserts that these constants resolve to existing files.

**reproduce** `cd /Users/abishaikc/Gift && for f in p0-gate-liveness p1-reader-agreement p2-field-surface p3-evaluator p4-harvest-distribution p5-verdict-closure p6-fault-campaign p7-attrition-funnel p8-ffr; do printf '%-32s %s\n' "$f.json" "$( [ -f docs/measurements/$f.json ] && echo EXISTS || echo MISSING)"; done; for c in P0_GATE_LIVENESS P1_READER_AGREEMENT P2_FIELD_SURFACE P3_EVALUATOR P4_HARVEST_DISTRIBUTION P5_VERDICT_CLOSURE P6_FAULT_CAMPAIGN P7_ATTRITION_FUNNEL P8_FFR; do echo "$c: $(grep -rn "$c" src tests tools --include='*.py' | grep -v 'paths.py' | wc -l)"; done`

---

### [MINOR] negative-control-system — `test_sweep__records_the_failing_assertion_text` is satisfied by a constant the sweep writes itself

**file** `tools/nc_sweep.py`:130  ·  **kind** shallow-proxy

**claim** The test asserts `g["assertion_text"]` is non-empty for every flipped guard and claims this makes the artifact reviewable rather than a paste, but tools/nc_sweep.py:130 supplies the literal `"reported failed"` whenever no text was captured, so the assertion can never fail — and 13 of the 160 flipped guards in the committed report carry that literal instead of a captured assertion.

**evidence** $ grep -n '"reported failed"' tools/nc_sweep.py
  130:            text = next((v for k, v in tb.items() if k.endswith(f) or f.endswith(k)), "reported failed")
$ .venv/bin/python -c "..." reports/negative-control-sweep.json
  13 of 160 red guards carry the literal placeholder, not a captured assertion
$ CDFC_REQUIRE_SWEEP=1 pytest tests/negative/test_nc_sweep.py -q  ->  4 passed

The text exists and is simply not captured. Running NC-CI06's guard under its injector, pytest emits:
  '/Users/abishaikc/Gift/src/cdfc/gates.py:71: cdfc.gates.RegistryError: /Users/abishaikc/Gift/ci/GATES.md:45: duplicate gate id 17'
  'FAILED tests/contract/test_contract_gates.py::test_contract__gates_registry_schema'
The `--tb=line` line is keyed on `src/cdfc/gates.py`, while the lookup at tools/nc_sweep.py:130 matches only against the guard's own file, so it misses and falls back to the placeholder. Re-running the sweep on a one-entry catalogue reproduces `red= True text= 'reported failed'`. The docstring's claim — "Every flipped guard carries the captured assertion ... so a reviewer opens a file rather than trusting a plausible-looking quotation" — is false for those 13, and the test that is supposed to enforce it cannot detect the difference.

**reproduce** `cd /Users/abishaikc/Gift
grep -n '"reported failed"' tools/nc_sweep.py
.venv/bin/python -c "import json; r=json.load(open('reports/negative-control-sweep.json')); print(sum(1 for x in r['rows'] for g in x['guards'] if g['observed_red'] and g['assertion_text']=='reported failed'), 'of', sum(1 for x in r['rows'] for g in x['guards'] if g['observed_red']))"
PYTHONPATH=/Users/abishaikc/Gift/src CDFC_REQUIRE_SWEEP=1 .venv/bin/python -m pytest tests/negative/test_nc_sweep.py -q --no-header`

---

### [MINOR] negative-control-system — The gate registry publishes a row count its own rows refute

**file** `ci/GATES.md`:110  ·  **kind** claim-unbacked

**claim** ci/GATES.md:110 states "**LIVE = {1,…,14,16,…,63} (62 rows). PENDING = {15} (1 row). Total 63.**" while the same file now carries 75 rows with 74 LIVE, and nothing in the build reads that line.

**evidence** $ grep -n 'LIVE = ' ci/GATES.md
  110:**LIVE = {1,…,14,16,…,63} (62 rows). PENDING = {15} (1 row). Total 63.**
$ PYTHONPATH=src .venv/bin/python tools/gate_liveness.py
  gates total          : 75
    LIVE               : 74
    PENDING            : 1   [15]
$ grep -rn '62 rows|Total 63|LIVE = {' tests/ src/ tools/
  (no matches — the literal is prose no test reads)
The frozen literal sets that `test_contract__live_set_is_pre_registered` enforces live in the test file, so the registry's own published summary drifted twelve rows without any gate noticing. This is the same shared-denominator shape the registry's row 18 exists to catch, in the registry itself.

**reproduce** `cd /Users/abishaikc/Gift
grep -n 'LIVE = ' ci/GATES.md
PYTHONPATH=/Users/abishaikc/Gift/src .venv/bin/python tools/gate_liveness.py | head -4
grep -rn '62 rows\|Total 63\|LIVE = {' tests/ src/ tools/ || echo 'no test reads it'`

---

### [MINOR] p0-p2-foundation — Two shell gates run in `make greps` with no row in the registry, and the registry's own published totals are stale by 12 rows

**file** `ci/GATES.md`:97  ·  **kind** unrecorded-deviation

**claim** `ci/no-clock-in-core.sh` and `ci/no-bare-absence.sh` are executed by `make greps` and have guard tests, but neither has a row in ci/GATES.md — so `gates_total: 75` in the published liveness measurement is not the set of gates that run. `ci/no-clock-in-core.sh`'s own header claims "Registry row 17 (R3)", which is `ci/no-timing-in-hashed-payload.sh`'s row. Separately, ci/GATES.md still states in present tense "**LIVE = {1,…,14,16,…,63} (62 rows). PENDING = {15} (1 row). Total 63.**" while the file now holds 75 rows (74 LIVE, 1 PENDING).

**evidence** `grep -n 'no-clock-in-core\|no-bare-absence' ci/GATES.md` -> no output; both appear in Makefile lines 21 and 23. `head -1 ci/no-clock-in-core.sh` region reads `# Registry row 17 (R3)` while ci/GATES.md:44 assigns row 17 to `ci/no-timing-in-hashed-payload.sh`. `.venv/bin/python -c "...cdfc.gates.parse()..."` yields 75 rows against the file's stated 63.

**reproduce** `cd /Users/abishaikc/Gift && grep -n 'no-clock-in-core\|no-bare-absence' ci/GATES.md; grep -n 'bash ci/' Makefile; grep -n 'Registry row' ci/no-clock-in-core.sh ci/no-timing-in-hashed-payload.sh; PYTHONPATH=src .venv/bin/python -c "from cdfc.gates import parse; g=parse(); print('rows',len(g))"; grep -n 'Total 63' ci/GATES.md`

---

### [MINOR] p0-p2-foundation — Seven of the nine published denominators are pinned by no test; the plan-named golden test for them does not exist and the omission is unrecorded

**file** `tools/measure/field_surface.py`:26  ·  **kind** unrecorded-deviation

**claim** plan/02-phases-foundation.md:2096 names `::test_golden__field_surface__all_nine` pinning `{FME: 3747, CMI: 2255, ALR: 1599, AL_monthly: 3537, IBU 459, ITFS 481, EDR_1 162}`. No such test exists, no test reads `docs/measurements/p2-field-surface.json`, and only FME's 3747 is asserted (in tests/negative/test_nc_schema.py). A change to the shared v3 rule that moved both paths consistently would silently move six of the seven published denominators: G-DENOM stays 9/9, the whole suite stays green, and the measurement file simply regenerates.

**evidence** `grep -rn 'field_surface__all_nine\|test_golden__field_surface' docs/ tests/ src/ tools/` -> no output (the name occurs only in plan/). `grep -rn 'p2-field-surface' tests/` -> no output; the only readers of that path are `src/cdfc/measure/paths.py` (a constant) and the generator itself. `grep -rn '2255\|3537' tests/ --include='*.py'` -> no hits for the denominators (1599 appears only as the P9 ceiling's ALR total). No recording of the substitution in docs/GATE-CHANGES.md, docs/HARVEST-DELTA.md, docs/decisions/ or docs/AUDIT-P0-P6.md.

**reproduce** `cd /Users/abishaikc/Gift && grep -rn 'field_surface__all_nine' plan/ docs/ tests/ tools/ src/; grep -rn 'p2-field-surface' tests/ || echo 'no test reads the published denominators'; grep -rn '2255\|3537' tests/ --include='*.py' || echo 'no per-workbook denominator pinned'`

---

### [MINOR] p5-evaluate-verdict — The run artifacts and the closure SQL never run: write(), run_jsonl(), explain() and CLOSURE_SQL are dead, and the determinism test the plan makes P5's down payment on G-REPRO does not exist

**file** `src/cdfc/evaluate/run.py`:154  ·  **kind** does-not-run

**claim** P5-B4's `runs/<run_id>/{run.jsonl, run.db, manifest.json}` output, `cdfc run`, `cdfc closure explain` and `tests/determinism/test_det__run_jsonl_byte_identical` were never wired; `CLOSURE_SQL` — specified as *the* definition of closure, "one GROUP BY over run_cell" — is only ever compared against a hand-built 5-row in-memory table.

**evidence** `grep -rn 'run\.write|run_jsonl|closure.explain|CLOSURE_SQL' tests tools src Makefile` shows: `run_jsonl` and `write` referenced only inside `run.py` itself; `explain` referenced only in its own docstring; `CLOSURE_SQL` only in `tests/unit/test_rollup_closure.py:155`, which builds `CREATE TABLE run_cell(...)` and inserts 5 synthetic rows. `ls tests/determinism/` contains celrt, envelope, harvest, lockfile, p8_corpus, probes, receipt, template_instrument — nothing for the run. `cdfc run` exits 2 with `PHASE = "P0"` hardcoded in `src/cdfc/cli.py:19` and the message "not implemented at phase P0; it is built in P5", though P5 is closed. The code is dead but functional — I called `write()` on a real run in a pristine export and it produced all three files, and `CLOSURE_SQL` over the resulting `run.db` agreed with the Python partition (0,0,2320,0,0,1427,0,0,0,3747).

**reproduce** `cd /Users/abishaikc/Gift && grep -rn "run\.write\|run_jsonl\|closure\.explain\|CLOSURE_SQL" tests tools src Makefile | grep -v __pycache__ ; ls tests/determinism/ ; PYTHONPATH=src .venv/bin/python -m cdfc.cli run 2>&1`

---

### [MINOR] p6-campaign — P6 exit criteria 3 and 5 (PERF-MUT-SEED / PERF-MUT-OBS, and `make mutation-pr` K/V >= 0.90 for observability.py and sites.py) are unimplemented stubs whose printed reasons are stale

**file** `Makefile`:77  ·  **kind** does-not-run

**claim** The P6 exit gate requires a recorded PERF-MUT-SEED/PERF-MUT-OBS baseline and `make mutation-pr` reporting K/V >= 0.90 for qualify/observability.py and qualify/sites.py; both make targets are echo-only, `perf/baseline.ci.json` has an empty `budgets` map, docs/MUTATION-THRESHOLDS.md says "Not yet written", and both stubs give reasons that are no longer true ("until their subject exists" — the mutant seeder exists since P6; "arrives with the code it measures (P2)" — P2 is five phases past).

**evidence** $ make mutation-pr -> `mutation testing arrives with the code it measures (P2)`
$ make perf -> `PERF budgets are recorded, not enforced, until their subject exists`
$ cat perf/baseline.ci.json -> {"machine": {..."populated by the first PERF run; budgets are recorded, not enforced, until their subject exists"}, "budgets": {}}
$ head -4 docs/MUTATION-THRESHOLDS.md -> "**Not yet written.** Its subject does not exist at P0; it is created by the phase that first needs it."
plan/04-phases-qualification.md "P6 EXITS iff ALL of" items 3 and 5. No record of the deferral in docs/GATE-CHANGES.md, docs/decisions/, or docs/AUDIT-P0-P6.md (which reports 0 open findings for P0–P6).

**reproduce** `cd /Users/abishaikc/Gift && make mutation-pr && make perf && cat perf/baseline.ci.json && head -4 docs/MUTATION-THRESHOLDS.md && grep -rn 'mutation-pr\|PERF-MUT' docs/ | head`

---

### [MINOR] p8-corpus-ffr — P8 exit criterion 1: the G-CORPUS trichotomy has no test and is not recorded in ci/GATES.md

**file** `tools/measure/p8_ffr.py`:292  ·  **kind** unrecorded-deviation

**claim** plan/04 P8 exit criterion 1 requires the G-CORPUS outcome to be "recorded in ci/GATES.md" and requires `test_gcorpus__outcome_is_one_of_three_and_is_rendered` to assert the trichotomy and that the outcome string reaches the surface. Neither exists: the test is absent from the whole repository, ci/GATES.md contains no G-CORPUS row, and `_gcorpus()` — which decides PASS/RESTRICTED/FAIL — has no test coverage at all, so two of its three branches have never executed.

**evidence** `grep -rn 'test_gcorpus' .` (excluding __pycache__) -> NOT FOUND anywhere. `grep -in 'g-corpus\|restricted' ci/GATES.md` -> no matches; ci/GATES.md's P8 block is rows 57-63, all pytest negative controls, none about G-CORPUS. `grep -rn '_gcorpus' tests/ tools/ src/` -> only tools/measure/p8_ffr.py:158, :164, :166, :292 — the definition and its single call site inside the report renderer; no test imports it. The outcome (RESTRICTED) IS recorded in docs/decisions/D-P8-01-no-blind-fill-corpus.md:36 and rendered at docs/measurements/P8-ffr.md:5, so the outcome itself is honest; what is unrecorded is the deviation from the criterion's two mechanisms. docs/GATE-CHANGES.md's P8 entry (lines 127-155) covers rows 57-62 and the row-38 widening and says nothing about G-CORPUS.

**reproduce** `cd /Users/abishaikc/Gift && grep -rn 'test_gcorpus' --include='*.py' . | grep -v __pycache__ ; echo '(none)' ; grep -in 'g-corpus' ci/GATES.md ; echo '(none)' ; grep -rn '_gcorpus' tests tools src --include='*.py' | grep -v __pycache__`

---

### [MINOR] p9-probes — `expr_language` misclassifies whitespace-free CEL containing a ternary or map literal as PYTHON

**file** `src/cdfc/probes/relations/registry.py`:107  ·  **kind** correctness

**claim** `RelationSpec.expr_language` claims "A relation whose expression is `module:function` is Python; anything else is CEL." The implementation is `"PYTHON" if (':' in body and ' ' not in body and '.' in body) else 'CEL'`, which classifies any space-free CEL expression containing a `:` — a ternary or a map literal — as PYTHON. `to_envelope` then raises `RelationEnvelopeError("its expression is PYTHON, not CEL")`, so the relation would appear in `docs/measurements/P9-relation-attrition.md`'s refusals with a reason that is untrue. It also runs the other way: a dotted Python callable with any trailing space or comment is classified CEL and routed at the CEL subset check. R-03's builder emits ternaries today and is only saved by emitting spaces around them.

**evidence** ```
'filing.a.v>0?1:0'                      -> PYTHON
'has(filing.a.v)?filing.a.v:0'          -> PYTHON
'{"k":filing.a.v}'                      -> PYTHON
'cdfc.mod:fn # note'                    -> CEL
'cdfc.probes.template_diff:template_diff' -> PYTHON   (correct)
'filing.a.v==1'                         -> CEL        (correct)
```
The only guard, `test_reg__self_test_expressions_are_python_and_the_rest_are_cel`, checks the six rows currently in `catalogue.yaml`; none of them exercises a space-free ternary, so the heuristic's failure mode is not covered.

**reproduce** `cd /Users/abishaikc/Gift && PYTHONPATH=src .venv/bin/python -c "
from cdfc.probes.relations.registry import RelationSpec
def L(e):
    return RelationSpec(id='x',title='t',necessity='NECESSARY',inputs='FILING_ONLY',precondition='p',expr=e,witness='w',bases=frozenset({'A'}),evidence='e',reviewed_by=('a',),reviewed_at='d',claims_fault_classes=('F01',)).expr_language
for e in ['filing.a.v>0?1:0','has(filing.a.v)?filing.a.v:0','{\"k\":filing.a.v}','cdfc.mod:fn # note','cdfc.probes.template_diff:template_diff','filing.a.v==1']:
    print(repr(e),'->',L(e))"`

---
