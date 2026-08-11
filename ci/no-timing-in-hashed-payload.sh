#!/usr/bin/env bash
# Registry row 17, dated 11 Aug 2026. A duration field inside a canonicalised payload
# makes byte-identical re-derivation impossible. The gate exists before the payload does.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || exit 1
if grep -rnE '(elapsed_us|elapsed_ms|duration_ms|took_ms|_seconds)\s*[:=]' --include='*.py' src/cdfc \
   | grep -vE '^src/cdfc/measure/paths\.py' | grep -vE 'reports/perf'; then
  echo "GATE FAIL: a timing field appears in a hashed-payload scan root. Timings live in reports/perf/." >&2
  exit 1
fi
echo "no-timing-in-hashed-payload: OK"
