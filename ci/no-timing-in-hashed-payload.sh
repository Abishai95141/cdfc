#!/usr/bin/env bash
# Registry row 17, dated 11 Aug 2026. A duration field inside a canonicalised payload
# makes byte-identical re-derivation impossible. The gate exists before the payload does.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || exit 1
# **THE SCOPE, and it must match `tests/contract/test_contract_timing.py`'s.** That test is this
# gate's AST twin: two instruments, one rule. It exempts `src/cdfc/measure/perf/` because
# `ci/no-clock-in-core.sh` already carves that directory out as the declared home for timings —
# and this gate did not, so `measure/perf/canary_timings.py`'s `elapsed_ms` field made it red the
# moment P10 wrote the module the F23 ruling asked for. A gate and its twin that disagree about
# scope are TWO rules, and the stricter one wins by accident rather than by argument.
if grep -rnE '(elapsed_us|elapsed_ms|duration_ms|took_ms|_seconds)\s*[:=]' --include='*.py' src/cdfc \
   | grep -vE '^src/cdfc/measure/paths\.py' \
   | grep -vE '^src/cdfc/measure/perf/' | grep -vE 'reports/perf'; then
  echo "GATE FAIL: a timing field appears in a hashed-payload scan root. Timings live in reports/perf/." >&2
  exit 1
fi
echo "no-timing-in-hashed-payload: OK"
