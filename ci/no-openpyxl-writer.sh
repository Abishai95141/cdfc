#!/usr/bin/env bash
# Registry row 38. Nothing under src/cdfc/qualify/ writes a workbook except surgery.py.
#
# WHY IT EXISTS. An openpyxl round-trip of the FME workbook drops 24 parts and all 19 `x14` data
# validations, and shrinks 3.66 MB to 66 kB. A mutant written that way differs from its base in
# hundreds of ways that have nothing to do with the seeded fault — so the observability diff would
# be a diff of THE WRITER, `U/G` would collapse to zero, and every `K/O` computed through it would
# be wrong in the direction that flatters us. NC-Q30.
#
# `surgery.py`'s raw `zipfile.ZipFile(..., "w")` is the ONE declared exception, named here so that
# widening it is a visible diff rather than a quiet edit.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }

SCAN="src/cdfc/qualify"
[ -d "$SCAN" ] || { echo "GATE FAIL: $SCAN does not exist; a grep over it would report success" >&2; exit 1; }

hits=$(grep -rnE '\.save\s*\(|load_workbook|Workbook\s*\(' --include='*.py' "$SCAN" 2>/dev/null || true)
writers=$(grep -rnE 'ZipFile\s*\([^)]*["'"'"']w["'"'"']' --include='*.py' "$SCAN" 2>/dev/null \
          | grep -v '^src/cdfc/qualify/surgery.py:' || true)

if [ -n "$hits$writers" ]; then
  echo "GATE FAIL: a workbook writer outside surgery.py:" >&2
  echo "$hits" >&2
  echo "$writers" >&2
  echo "  Mutants are written by raw-zip surgery ONLY. An openpyxl round-trip loses 19 x14" >&2
  echo "  validations and 24 parts, and the observability diff then measures the writer." >&2
  exit 1
fi
echo "no-openpyxl-writer: OK"
