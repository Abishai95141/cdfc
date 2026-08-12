#!/usr/bin/env bash
# Registry row 20. No float anywhere in the deterministic numeric core.
#
# R4 puts calc/ in this scan set so the evaluator is Decimal FROM ITS FIRST LINE rather
# than converted later. A float that enters a money path does not announce itself: it
# produces a well-formed number that differs in the last places, and a tolerance wide
# enough to absorb it is wide enough to absorb a real defect.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }
hits=$(grep -rnE '\bfloat\(|: *float\b|-> *float\b' --include='*.py' src/cdfc/calc src/cdfc/facts 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "GATE FAIL: a float reached the deterministic numeric core:" >&2
  echo "$hits" | sed 's/^/  /' >&2
  exit 1
fi
echo "no-float-money: OK"
