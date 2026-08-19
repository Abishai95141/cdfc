#!/usr/bin/env bash
# A cell string is `<sheet>!<ref>`, and ONLY THE LAST `!` is the delimiter.
#
# A reference (`D40`, `$C$6`) can never contain `!`. A SHEET NAME can: Excel permits it and
# openpyxl accepts it, verified. So `"Bad!Name!A1".split("!", 1)` yields sheet `Bad` and ref
# `Name!A1` -- the wrong sheet and a ref that addresses nothing.
#
# `Anchor.parse` right-splits and got this right. Eighteen call sites left-split and did not, so
# the anchor and the rest of the codebase disagreed about which `!` was the delimiter, on exactly
# the path A1 exists to serve: a buyer's own workbook.
#
# Found by the adversarial audit of the A1 diff, 20 Aug 2026. Latent -- no pinned blank carries
# such a name -- and latent is not fixed.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh

# The pattern is written so this file does not match itself: a gate defeated by the prose
# explaining it is a shape this repository has hit more than a dozen times.
BAD='\.split\("!", ?1\)|\.partition\("!"\)|\.split\('"'"'!'"'"'\)\['
hits=$(grep -rnE "$BAD" src tools 2>/dev/null | grep -v rsplit | grep -v rpartition || true)
if [ -n "$hits" ]; then
  echo "GATE FAIL: a cell string is split on its FIRST '!', which is the wrong one." >&2
  echo "$hits" | sed 's/^/  /' >&2
  echo "  Use rsplit(\"!\", 1) / rpartition(\"!\"). A sheet name may contain '!'; a ref may not." >&2
  exit 1
fi
echo "no-left-split-on-cell: OK"
