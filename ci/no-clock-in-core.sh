#!/usr/bin/env bash
# Registry row 17 (R3). A duration WE measured must not enter the deterministic core.
# A timing inside a hashed payload makes byte-identical re-derivation impossible, and the
# obvious repair — deleting the field — silently destroys the evidence the loop ran. So
# timings live in src/cdfc/measure/perf/ and reports/perf/, and nowhere else.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }
hits=$(grep -rnE '\b(perf_counter|monotonic|process_time)\s*\(' --include='*.py' src/cdfc \
       | grep -v '^src/cdfc/measure/perf/' || true)
if [ -n "$hits" ]; then
  echo "GATE FAIL: a monotonic clock is reachable from the deterministic core:" >&2
  echo "$hits" >&2
  echo "  timings belong in src/cdfc/measure/perf/ or reports/perf/" >&2
  exit 1
fi
echo "no-clock-in-core: OK"
