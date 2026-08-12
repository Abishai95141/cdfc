#!/usr/bin/env bash
# Registry row 21. No regular expression is used to extract keys or constructs from CEL source.
#
# WHY IT EXISTS, and it is not hypothetical here. One level up, `<f[ >][^>]*>` over OOXML
# returned a CORRECT COUNT with WRONG BODIES — the count agreed with every cross-check and the
# extracted formulas were silently truncated. The same defect class over CEL is worse, because
# the thing extracted is the key set, and the key set is the settled fraction's denominator.
#
# Concretely, a regex over
#     filing.rows.all(r, r.x in template.v)
# reports `r.x` as a root — a document that does not exist — and misses the `[*]` that says the
# key is a column rather than a cell. `read_keys` walks celpy's parse tree, resolves the
# comprehension binding, and never sees `r` as a root.
#
# The sibling gate is ci/no-regex-over-xml.sh's argument applied to the layer above it.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }

# The scan is over the CEL layer only. `re` is lawful elsewhere (the fault taxonomy parser reads
# a markdown table with one), and a repo-wide ban would be a gate nobody could keep green.
CEL_FILES="src/cdfc/predicates/ast_walker.py src/cdfc/predicates/cel_profile.py src/cdfc/evaluate"
for f in $CEL_FILES; do
  [ -e "$f" ] || { echo "GATE FAIL: $f does not exist; a grep over it would report success" >&2; exit 1; }
done

# Any regex applied to something that looks like CEL source, and any import of `re` in these
# modules at all. The second is the one that actually holds: a module with no `re` cannot use it.
hits=$(grep -rnE "(findall|finditer|re\.(search|match|sub|split|compile))\s*\(\s*r?[\"'][^\"']*(filing|template|\\\\.all|\\\\.exists|\\\\.map|\\\\.filter)" \
       --include='*.py' $CEL_FILES 2>/dev/null || true)
imports=$(grep -rnE '^\s*(import re|from re import)\b' --include='*.py' $CEL_FILES 2>/dev/null \
          | grep -v 'ast_walker.py.*import re$' || true)

# ast_walker imports `re` for ONE thing: validating that a declared key SEGMENT is an identifier.
# That is a check on a name we already parsed, not an extraction from CEL source. It is allowed
# by name, and the allowance is narrow enough that a second use would have to be argued for here.
seg=$(grep -c '_SEGMENT' src/cdfc/predicates/ast_walker.py || true)
uses=$(grep -cE '\bre\.' src/cdfc/predicates/ast_walker.py || true)
if [ "$uses" -gt 1 ]; then
  echo "GATE FAIL: src/cdfc/predicates/ast_walker.py uses \`re\` $uses times." >&2
  echo "  Exactly one use is allowed — the identifier check behind _SEGMENT ($seg reference(s))." >&2
  grep -nE '\bre\.' src/cdfc/predicates/ast_walker.py >&2
  exit 1
fi

if [ -n "$hits$imports" ]; then
  echo "GATE FAIL: a regular expression is being applied to CEL source:" >&2
  echo "$hits" >&2
  echo "$imports" >&2
  echo "  Key extraction walks celpy's parse tree. A lexical pass reports the comprehension" >&2
  echo "  variable as a document root and misses [*]." >&2
  exit 1
fi
echo "no-regex-over-cel: OK"
