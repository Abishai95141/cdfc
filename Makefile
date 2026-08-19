# THE INTERPRETER IS DISCOVERED, NOT DEFAULTED TO ONE LAPTOP.
#
# This was a `?=` default naming one developer's home directory. Together with the same literal
# inside `ci/_roots.sh` it is why a fresh clone had to be handed BOTH `PY` and `CDFC_PY` before
# `make verify` would work — and the clone-verify step at P7, P8 and P9 all did exactly that,
# which is the build telling us about the defect three times while we wrote the workaround down
# as a procedure. `ci/no-external-paths.sh` could not see it: its pattern required a quote
# immediately before the path, and its `--include` filters excluded the Makefile even when named.
PY := $(firstword $(wildcard $(CDFC_PY)) $(wildcard $(CURDIR)/.venv/bin/python) $(shell command -v python3))
export CDFC_PY := $(PY)
export PYTHONPATH := $(CURDIR)/src

.PHONY: all lint licence greps contract unit property golden differential nc-sweep \
        determinism perf mutation-pr e2e nightly demo corpus-verify measure-foundation gates \
        harvest cel-conformance host-fn-mutation predicate-schema verify \
        gen-contract instruments evaluator-arm1 p3-reproduction ceiling runnability relation-attrition \
        fixture-fy2029 history serve demo-verify demo-video

all: lint licence greps corpus-verify contract unit golden determinism negative gates

lint:
	$(PY) -m ruff check src tests injectors 2>/dev/null || echo "ruff not installed — advisory at P0"

licence:
	bash ci/licence-denylist.sh

greps:
	bash ci/scan-roots-exist.sh
	bash ci/no-bare-except.sh
	bash ci/no-green-tick.sh
	bash ci/no-clock-in-core.sh
	bash ci/no-timing-in-hashed-payload.sh
	bash ci/no-bare-absence.sh
	bash ci/catalogue-ids.sh
	bash ci/no-external-paths.sh
	bash ci/no-float-money.sh
	bash ci/no-regex-over-cel.sh
	bash ci/no-regex-over-xml.sh
	bash ci/no-bare-rate.sh
	bash ci/no-openpyxl-writer.sh
	bash ci/no-wallclock-z3.sh
	bash ci/no-imported-prior.sh
	bash ci/no-left-split-on-cell.sh
	$(PY) tools/audit_trail.py

contract:
	$(PY) -m pytest tests/contract -q

unit:
	$(PY) -m pytest tests/unit -q

negative:
	$(PY) -m pytest tests/negative -q

determinism:
	$(PY) -m pytest tests/determinism -q

golden:
	$(PY) -m pytest tests/golden -q

corpus-verify:
	$(PY) tools/measure/corpus_verify.py

fixtures:
	$(PY) tools/fixtures/make_adversarial.py
	$(PY) tools/fixtures/make_synthetic.py

agreement:
	$(PY) tools/measure/agreement_matrix.py

field-surface:
	$(PY) tools/measure/field_surface.py

property:
	$(PY) -m pytest tests/property -q

differential:
	$(PY) -m pytest tests/differential -q

nc-sweep:
	$(PY) tools/nc_sweep.py
	CDFC_REQUIRE_SWEEP=1 $(PY) -m pytest tests/negative/test_nc_sweep.py -q

e2e demo:
	@echo "$@: subject does not exist at P0"; exit 0

perf:
	@echo "PERF budgets are recorded, not enforced, until their subject exists"

mutation-pr:
	@echo "mutation testing arrives with the code it measures (P2)"

gates: nc-sweep
	$(PY) tools/gate_liveness.py

measure-foundation: gates agreement field-surface
	@echo "wrote docs/measurements/p0-gate-liveness.json"

nightly: all

# --- P4 ------------------------------------------------------------------------------
predicate-schema:
	$(PY) tools/gen_predicate_schema.py

audit:
	$(PY) tools/audit_trail.py
	$(PY) tools/audit_trail.py --selftest

progress:
	$(PY) tools/progress.py

harvest:
	$(PY) -m cdfc.cli harvest --all --out predicates/harvested \
		--report docs/measurements/P4-harvest-distribution.md
	$(PY) -c "import sys; sys.path.insert(0,'src'); from pathlib import Path; \
		from cdfc.predicates.harvest import harvest_all; \
		from cdfc.measure.harvest_report import render_both_ways; \
		Path('docs/measurements/P4-both-ways.md').write_text(render_both_ways(harvest_all(Path('fixtures/prescribed'))), encoding='utf-8')"

cel-conformance:
	$(PY) tools/cel_conformance.py

host-fn-mutation:
	$(PY) tools/host_fn_mutation.py

# THE PHASE-CLOSING RITUAL, in one target. A phase is not closed until this is green in a
# FRESH CLONE — the working tree silently supplies things a clone does not.
verify: lint licence build-tool-licence barrier5 greps corpus-verify
	# Producers first. A consumer that runs before its producer either fails on a missing file
	# or — worse — reads a stale one and reports a number nobody computed this run.
	$(PY) tools/host_fn_mutation.py
	$(PY) tools/cel_conformance.py
	$(PY) -m cdfc.cli run fixtures/synthetic/clean__independently-computed__fme-q1.xlsx --out reports/runs
	# The churn artifacts, for the same reason: `reports/settled-history.jsonl` and
	# `reports/churn/*.json` back three screens, and a fresh clone that lacks them would SKIP
	# their tests rather than fail — which is a green suite reporting that a chart can step down
	# without once asking it to.
	$(MAKE) history
	CDFC_REQUIRE_RUN=1 $(PY) -m pytest tests -q
	$(PY) tools/nc_sweep.py
	$(PY) tools/gate_liveness.py
	@echo "verify: every gate green, every negative control caught"

# --- P5 ------------------------------------------------------------------------------
# RENAMED AT P7, dated 13 Aug 2026. It was `contract:`, which is also the name of the P0 target
# that RUNS the contract tests — and make silently keeps the LAST definition. So since P5
# `make contract` regenerated EVALUATION-CONTRACT.md and `make all` never ran tests/contract at
# all, while printing a target name that said it had. `make verify` was unaffected (it runs
# `pytest tests`), which is why nothing went red. A duplicate target is a silent pass with a
# warning nobody reads.
.PHONY: barrier5
barrier5:
	./ci/barrier5.sh
	./ci/no-model-in-verdict.sh

.PHONY: build-tool-licence
build-tool-licence:
	./ci/no-denied-build-tool.sh

gen-contract:
	$(PY) tools/gen_contract.py

filings:
	$(PY) tools/fixtures/synthesise_filing.py

run-fme:
	$(PY) tools/measure/p5_runtime_closure.py

# --- P6 ------------------------------------------------------------------------------
fault-model:
	$(PY) tools/gen_fault_model_doc.py

campaign:
	$(PY) tools/measure/p6_campaign.py

audit:
	$(PY) tools/audit.py

# --- P7 ------------------------------------------------------------------------------
instruments:
	$(PY) tools/build_instruments.py

proviso-markers:
	$(PY) tools/gen_proviso_markers_doc.py

attrition:
	$(PY) tools/measure/p7_attrition.py

# --- P15-B2 --------------------------------------------------------------------------
# The churn fixture, and the demonstration that the settled fraction CAN FALL (criterion A8).
# `history` needs a run on disk and the fixture; it produces `reports/settled-history.jsonl`
# and `reports/churn/fy2029-30.json`, which are what `/v1/settled-fraction/history` and
# `/v1/churn` serve. Neither endpoint recomputes: an API that re-derives a verdict is an API
# that can disagree with the artifact the attestation covers.
# The product, running. Loopback by default: a coverage tool that listens on 0.0.0.0 the first
# time somebody runs it is a coverage tool that ends up on a network nobody meant to put it on.
serve:
	$(PY) -m cdfc.cli serve

# --- the walkthrough -----------------------------------------------------------------
# Records the product by DRIVING IT, not by capturing a desktop. `demo-verify` runs first
# and fails the build when a caption quotes a figure the live API no longer produces — a
# walkthrough is the one artifact nobody re-derives, so its numbers are checked here or
# they are never checked again. Needs `make serve` running in another shell.
.PHONY: demo-verify demo-video
demo-verify:
	node tools/demo/verify.mjs

demo-video: demo-verify
	cd tools/demo && npm i --silent --no-audit --no-fund
	node tools/demo/record.mjs
	ffmpeg -y -i reports/demo/walkthrough.webm -c:v libx264 -preset slow -crf 20 \
		-pix_fmt yuv420p -movflags +faststart -r 30 reports/demo/cdfc-walkthrough.mp4 -loglevel error
	rm -f reports/demo/walkthrough.webm
	@echo "wrote reports/demo/cdfc-walkthrough.mp4 (+ .srt)"

fixture-fy2029:
	$(PY) tools/fixtures/build_fy2029.py

history: fixture-fy2029
	$(PY) tools/measure/settled_history.py

# --- P8 ------------------------------------------------------------------------------
ffr:
	$(PY) tools/measure/p8_ffr.py

mask-check:
	$(PY) tools/corpus/mask_vs_filler.py

# --- P9 ------------------------------------------------------------------------------
# `evaluator-arm1` had NO make target until P9, and its script had been raising
# `KeyError: 'cells'` since a rename — so `docs/measurements/P3-evaluator.md` was an artifact
# of a version that no longer ran, and it published FME as 495/10 when the truth after P6's
# AGGREGATE repair was 475/30. A measurement with no way to re-run it is a memory.
evaluator-arm1:
	$(PY) tools/measure/evaluator_arm1.py

p3-reproduction:
	$(PY) tools/measure/p3_reproduction.py

ceiling:
	$(PY) tools/measure/p9_ceiling.py

runnability:
	$(PY) tools/measure/p9_runnability.py

relation-attrition:
	$(PY) tools/measure/p9_attrition.py

# --- P10 -----------------------------------------------------------------------------
# The adjudication record, |RESIDUE| against BOTH rejector sets, and the two exhibits.
# Re-runs from the committed campaign; it opens no artifact and reads no clock.
residue:
	$(PY) tools/measure/p10_residue.py

canary-cost:
	$(PY) tools/measure/p10_canary_cost.py

# --- P11 -----------------------------------------------------------------------------
# The programme's primary number: bytes differing / bytes in the artifacts, target 0,
# under four environment variations. It exits NON-ZERO when anything differs.
byte-identity:
	$(PY) tools/measure/p11_byte_identity.py

# --- P12 -----------------------------------------------------------------------------
# The settling experiment. `preregister` generates the criterion and LOCKS it; `pool` reports
# the instrument's absence and exits 2; `e6-status` prints the lock's state and whether the run
# may proceed. None of the three makes a model call, and `pool` exiting non-zero is the finding.
preregister:
	PYTHONPATH=$(CURDIR):$(CURDIR)/src $(PY) tools/e6/preregister.py

pool:
	PYTHONPATH=$(CURDIR):$(CURDIR)/src $(PY) tools/e6/enumerate_shall.py

e6-status:
	PYTHONPATH=$(CURDIR)/src $(PY) -c "import json, sys; \
		sys.path.insert(0, 'src'); \
		from cdfc.experiment import prereg; \
		print(json.dumps(prereg.lock_summary(), indent=1)); \
		print('ancestry:', prereg.ancestry_state())"

# --- P14 -----------------------------------------------------------------------------
# The four surface gates, run over a RENDERED artifact. SG1's DOM arm and SG4's computed-style
# arm need a headless browser that is not in the lockfile; they are recorded NOT RUN in
# docs/measurements/P14-surface-audit.md rather than reported as passed.
surface-audit:
	PYTHONPATH=$(CURDIR)/src $(PY) ci/surface_audit.py

report:
	PYTHONPATH=$(CURDIR)/src $(PY) -c "import sys; sys.path.insert(0,'src'); \
		from pathlib import Path; from cdfc.surface.render import render_report; \
		from cdfc.measure.p10_run import run_filing; from cdfc.measure.p5_run import TEMPLATE_COMPUTED; \
		a = render_report(run_filing(TEMPLATE_COMPUTED)); \
		print(f'  {a.path}  {a.n_bytes:,} bytes  sha256 {a.sha256[:16]}')"

.PHONY: statute
statute:  ## rebuild the STATUTE instrument from the pinned PDF (needs .[pdf])
	./ci/no-denied-build-tool.sh
	$(PY) tools/pin_statute.py
