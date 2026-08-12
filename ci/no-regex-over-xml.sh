#!/usr/bin/env bash
# Registry row 28. No regular expression is used to read or rewrite OOXML.
#
# WHY IT EXISTS, and it is not a hypothesis. This gate was named in `ci/no-regex-over-cel.sh`'s own
# docstring as "the sibling" and DID NOT EXIST. At P5 the filing generator rewrote `<c>` elements
# with a pattern, produced `Opening and ending tag mismatch: row ... and c`, and LibreOffice
# "repaired" the result by dropping 424 of the workbook's 505 formulas. The count of formula cells
# then read 81 and every relation they encode was gone.
#
# One level down, `<f[ >][^>]*>` over the same format returned a CORRECT COUNT with TRUNCATED
# BODIES. Same shape, three times now.
#
# The rule: anything that reads or writes a worksheet part goes through `cdfc.ingest.xmlsafe` —
# the one parser factory — and edits elements, never bytes.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }

SCAN="src/cdfc tools/fixtures tools/measure"
for f in $SCAN; do
  [ -e "$f" ] || { echo "GATE FAIL: $f does not exist; a grep over it would report success" >&2; exit 1; }
done

# A regex whose pattern mentions an OOXML tag, an OOXML attribute, or the main namespace.
hits=$(grep -rnE "(findall|finditer|sub|search|match|compile)\s*\(\s*(rb?)?[\"'][^\"']*(<[a-zA-Z]+|</|spreadsheetml|sharedStrings|<c |<f |<v>|<row|sqref|dataValidation)" \
       --include='*.py' $SCAN 2>/dev/null | grep -v 'no-regex-over-xml' || true)

if [ -n "$hits" ]; then
  echo "GATE FAIL: a regular expression is being applied to OOXML:" >&2
  echo "$hits" >&2
  echo "  Worksheet parts are PARSED (cdfc.ingest.xmlsafe) and edited as elements. A pattern over" >&2
  echo "  this format returns a correct count with wrong contents, and has three times." >&2
  exit 1
fi
echo "no-regex-over-xml: OK"
