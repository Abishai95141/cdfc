#!/usr/bin/env bash
# Registry row 1. There is no green tick anywhere in this product. The commitment is a
# system property rather than a preference only because this grep is a build gate.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_surface_roots || { echo "GATE FAIL: refusing to report success over a missing surface root" >&2; exit 1; }
PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
"$PY" - <<'PYEOF'
import sys, pathlib
sys.path.insert(0, "src")
from cdfc.surface.labels import SURFACE_ROOTS, banned_tokens

# The vocabulary's DEFINITION SITE is the one file that must contain the banned tokens.
# Excluding a file from a gate is how gates get defeated, so the exemption is exactly
# one path, asserted by tests/contract/test_contract__green_tick_exemption_is_one_file.
EXEMPT = {"src/cdfc/surface/labels.py"}
bad = []
for root in SURFACE_ROOTS:
    for p in pathlib.Path(root).rglob("*"):
        if not p.is_file() or p.suffix in {".pyc"}:
            continue
        if p.as_posix() in EXEMPT:
            continue
        text = p.read_text(encoding="utf-8", errors="replace").lower()
        for tok in banned_tokens():
            if tok.lower() in text:
                bad.append(f"{p}: contains banned surface token {tok!r}")
if bad:
    print("GATE FAIL: an all-clear reached a user surface", file=sys.stderr)
    print("\n".join(bad), file=sys.stderr)
    sys.exit(1)
print("no-green-tick: OK")
PYEOF
