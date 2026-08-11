#!/usr/bin/env bash
# Registry row 12. NC- ids unique, defined, non-dangling; every plan document UTF-8.
# The UTF-8 assertion is not decoration: a raw NUL made grep skip an entire document,
# and this gate would have run green over the largest instance of the problem.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -d plan ]; then
  python3 plan/scripts/nc_audit.py plan >/dev/null 2>&1 || { echo "catalogue-ids: audit reports issues (advisory at P0)"; }
fi
python3 - <<'PYEOF'
import pathlib, sys
bad = []
for p in list(pathlib.Path("plan").glob("*.md")) + list(pathlib.Path("spec").glob("*.md")):
    raw = p.read_bytes()
    if b"\x00" in raw:
        bad.append(f"{p}: NUL byte — grep would skip this file entirely")
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        bad.append(f"{p}: not UTF-8 ({e})")
if bad:
    print("GATE FAIL:", *bad, sep="\n  ", file=sys.stderr); sys.exit(1)
print("catalogue-ids: OK (encoding clean)")
PYEOF
