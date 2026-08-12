#!/usr/bin/env bash
# Registry row 19. No source, test or tool may reference an absolute path outside the
# repository.
#
# WHY IT EXISTS, dated 11 Aug 2026. P0-B2 vendored the nine workbooks so that every
# reading is validated against pinned, hash-verified bytes. A negative control in
# tests/negative/test_nc_ci.py went on pointing at the ORIGINAL external directory, so
# it was validated against a fixture that could drift — and P1's own entry criterion says
# a reader validated against a drifting fixture validates nothing. It also made the
# repository non-portable: a fresh clone on any other machine failed.
#
# The gate is broader than that one path on purpose: /Users/, /home/ and /tmp/ are all
# machine-local, and any of them silently couples the build to one laptop.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }

# The gate's own documentation necessarily contains the pattern; exempt exactly this file.
hits=$(grep -rnE '"/(Users|home|tmp)/|'"'"'/(Users|home|tmp)/' \
        --include='*.py' --include='*.sh' --include='*.yaml' --include='*.yml' \
        src tests tools ci 2>/dev/null | grep -v '^ci/no-external-paths.sh' || true)
if [ -n "$hits" ]; then
  echo "GATE FAIL: a machine-local absolute path is referenced from the build:" >&2
  echo "$hits" | sed 's/^/  /' >&2
  echo "  vendored fixtures live in fixtures/; resolve paths from REPO root instead." >&2
  exit 1
fi
echo "no-external-paths: OK"
