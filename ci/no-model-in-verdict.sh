#!/usr/bin/env bash
# The cheap companion to test_nc__A04a. Stage 2, so it fails in seconds rather than in the suite.
#
# THIS GATE IS NOT THE GUARD. The AST closure is. A grep sees `import httpx` and does not see
# `from x import y` where y transitively reaches it, so a green here proves nothing on its own —
# which is why it runs BESIDE the closure walk and never instead of it. It exists because a
# thirty-second failure gets fixed and a twenty-minute one gets skipped.
set -euo pipefail
cd "$(dirname "$0")/.."

ROOTS="src/cdfc/evaluate src/cdfc/verdict src/cdfc/probes src/cdfc/selfcheck src/cdfc/attest src/cdfc/qualify src/cdfc/surface"
for r in $ROOTS; do
  [ -d "$r" ] || { echo "GATE FAIL: $r does not exist; a scan over it would report success" >&2; exit 1; }
done

# `cdfc.api` is deliberately NOT scanned: an API binds a socket by definition. The rule says where
# it applies rather than being weakened everywhere.
PATTERN='^[[:space:]]*(import|from)[[:space:]]+(anthropic|openai|google|genai|cohere|mistralai|httpx|requests|aiohttp|urllib3|socket|http\.client|cdfc\.model)\b'

if hits=$(grep -rnE "$PATTERN" $ROOTS --include='*.py' 2>/dev/null); then
  echo "GATE FAIL: a model client or network module is imported in a verdict root:" >&2
  echo "$hits" >&2
  exit 1
fi
echo "ok: no model client or network import in any verdict root (grep arm; the closure walk is the guard)"
