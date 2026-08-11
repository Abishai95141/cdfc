#!/usr/bin/env bash
# Registry row 2. A bare `except:` swallows a crash into a clean state — the sixth
# silent-false-negative mechanism in the catalogue.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }
hits=0
while IFS= read -r r; do
  [ -z "$r" ] && continue
  if grep -rnE '^\s*except\s*:' --include='*.py' "$r"; then hits=1; fi
done < <(cdfc_roots)
if [ "$hits" -ne 0 ]; then echo "GATE FAIL: bare except found" >&2; exit 1; fi
echo "no-bare-except: OK"
