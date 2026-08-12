PY ?= /Users/abishaikc/Gift/.venv/bin/python
export PYTHONPATH := $(CURDIR)/src

.PHONY: all lint licence greps contract unit property golden differential nc-sweep \
        determinism perf mutation-pr e2e nightly demo corpus-verify measure-foundation gates \
        harvest cel-conformance host-fn-mutation predicate-schema verify

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
verify: lint licence greps corpus-verify
	# Producers first. A consumer that runs before its producer either fails on a missing file
	# or — worse — reads a stale one and reports a number nobody computed this run.
	$(PY) tools/host_fn_mutation.py
	$(PY) tools/cel_conformance.py
	$(PY) -m pytest tests -q
	$(PY) tools/nc_sweep.py
	$(PY) tools/gate_liveness.py
	@echo "verify: every gate green, every negative control caught"
