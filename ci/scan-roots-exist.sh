#!/usr/bin/env bash
# Registry row 3. Every declared scan root must exist before any grep gate runs.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || exit 1
assert_roots_exist cdfc_surface_roots || exit 1
echo "scan-roots-exist: OK"
