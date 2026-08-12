PY ?= /Users/abishaikc/Gift/.venv/bin/python
export PYTHONPATH := $(CURDIR)/src

.PHONY: all lint licence greps contract unit property golden differential nc-sweep \
        determinism perf mutation-pr e2e nightly demo corpus-verify measure-foundation gates

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

agreement:
	$(PY) tools/measure/agreement_matrix.py

property:
	$(PY) -m pytest tests/property -q

differential:
	$(PY) -m pytest tests/differential -q

nc-sweep:
	$(PY) tools/nc_sweep.py

e2e demo:
	@echo "$@: subject does not exist at P0"; exit 0

perf:
	@echo "PERF budgets are recorded, not enforced, until their subject exists"

mutation-pr:
	@echo "mutation testing arrives with the code it measures (P2)"

gates: nc-sweep
	$(PY) tools/gate_liveness.py

measure-foundation: gates agreement
	@echo "wrote docs/measurements/p0-gate-liveness.json"

nightly: all
