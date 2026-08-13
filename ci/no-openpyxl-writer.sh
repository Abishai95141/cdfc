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

# NARROWED AT P7, dated 13 Aug 2026, and the narrowing is recorded in docs/GATE-CHANGES.md.
#
# `template_instrument.py` needs a READ-ONLY openpyxl handle: it is the external party of the
# dual-extraction harness, and the whole value of that party is that nobody here wrote it. So
# `load_workbook` is admitted in that ONE file, by name, and every WRITE construct stays banned
# there and everywhere — including in the exempt file, which is checked separately below rather
# than exempted wholesale. A blanket exemption would have re-opened the round-trip this gate
# exists to prevent, in the file the exemption was granted to.
READER_EXEMPT='^src/cdfc/qualify/template_instrument\.py:'

hits=$(grep -rnE '\.save\s*\(|load_workbook|Workbook\s*\(' --include='*.py' "$SCAN" 2>/dev/null \
       | grep -vE "${READER_EXEMPT}[0-9]+: *(#.*)?(with warnings|wb = openpyxl\.load_workbook)" || true)
# The exempt file may READ. It may not write, by any of the three routes.
exempt_writes=$(grep -rnE '\.save\s*\(|Workbook\s*\(\s*\)|ZipFile\s*\([^)]*["'"'"']w["'"'"']' \
                --include='*.py' "$SCAN" 2>/dev/null | grep -E "$READER_EXEMPT" || true)
# WIDENED AT P8, dated 13 Aug 2026: `corpus/_writer.py` joins `surgery.py` as a declared raw-zip
# writer. It writes the CLEAN CORPUS by the same technique and for the same measured reason — an
# openpyxl round-trip drops 24 parts and all 19 x14 validations — and it imports no openpyxl at
# all, which the `hits` scan above still enforces over every file including this one. The list is
# EXPLICIT so that widening it stays a visible diff rather than a quiet edit.
writers=$(grep -rnE 'ZipFile\s*\([^)]*["'"'"']w["'"'"']' --include='*.py' "$SCAN" 2>/dev/null \
          | grep -v '^src/cdfc/qualify/surgery.py:' \
          | grep -v '^src/cdfc/qualify/corpus/_writer.py:' || true)

if [ -n "$hits$writers$exempt_writes" ]; then
  echo "GATE FAIL: a workbook writer outside surgery.py:" >&2
  echo "$hits" >&2
  echo "$writers" >&2
  [ -n "$exempt_writes" ] && echo "  (in the READ-ONLY exempt file, which may not write)" >&2
  echo "$exempt_writes" >&2
  echo "  Mutants are written by raw-zip surgery ONLY. An openpyxl round-trip loses 19 x14" >&2
  echo "  validations and 24 parts, and the observability diff then measures the writer." >&2
  exit 1
fi
echo "no-openpyxl-writer: OK"
