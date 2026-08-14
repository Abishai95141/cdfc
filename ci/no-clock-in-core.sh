#!/usr/bin/env bash
# Registry row 17 (R3). A duration WE measured must not enter the deterministic core.
# A timing inside a hashed payload makes byte-identical re-derivation impossible, and the
# obvious repair — deleting the field — silently destroys the evidence the loop ran. So
# timings live in src/cdfc/measure/perf/ and reports/perf/, and nowhere else.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }
# **THE PATTERN MISSED `time.time()`** — the most obvious clock of all — along with
# `datetime.now()`, `datetime.utcnow()` and `date.today()`. It listed only the MONOTONIC clocks,
# which are what a person reaches for when timing something; a WALL clock is what a person reaches
# for when stamping something, and a timestamp inside a hashed payload is exactly what makes
# byte-identical re-derivation impossible. A `time.time()` planted in `src/cdfc/verdict/closure.py`
# — the deterministic core — left this gate green.
#
# Scope is `src/cdfc` only, which IS the deterministic core; `measure/perf/` is the declared home
# for timings and stays exempt. Nothing in the core uses a wall clock today, so this widening
# costs nothing and closes the shape.
hits=$(grep -rnE '\b(perf_counter|monotonic|process_time|time\.time|datetime\.(now|utcnow)|date\.today)\s*\(' \
       --include='*.py' src/cdfc \
       | grep -v '^src/cdfc/measure/perf/' || true)
if [ -n "$hits" ]; then
  echo "GATE FAIL: a monotonic clock is reachable from the deterministic core:" >&2
  echo "$hits" >&2
  echo "  timings belong in src/cdfc/measure/perf/ or reports/perf/" >&2
  exit 1
fi
echo "no-clock-in-core: OK"
