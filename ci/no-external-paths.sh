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

# WIDENED 14 Aug 2026, and the widening is the finding rather than housekeeping.
#
# The pattern required a QUOTE CHARACTER IMMEDIATELY BEFORE the path. Every machine-local path
# actually in this build was written as a shell default or a make variable —
#   PY="${CDFC_PY:-/Users/…}"      and      PY ?= /Users/…
# — where the character before the slash is `:` or a space. So the gate was observed red on
# exactly the shape its own injector plants (`EXTERNAL = "/Users/somebody/corpus/f.xlsx"`) and
# green on the four instances the repository contained, one of which was inside `ci/_roots.sh`
# and silently disabled every root-derived gate on any other machine.
#
# The pattern is now anchored on the PATH, not on what precedes it, and the Makefile — which was
# not in the scan set at all, and which carried the fourth instance — is included.
#
# `_here` and `$(dirname "$0")` style repo-relative resolution is what a path here should be, and
# it contains no leading slash, so it cannot match.
# `-` IS NOT IN THE EXCLUSION CLASS, and leaving it there was this gate's defect a second time:
# the shape the repository actually contained was `${CDFC_PY:-/Users/…}`, where the character
# before the slash is the `-` of the shell default operator. A class of `[^A-Za-z0-9_.-]` excludes
# it and the gate reads straight past the only instances that mattered.
PAT='(^|[^A-Za-z0-9_.])/(Users|home)/'
hits=$(grep -rnE "$PAT" \
        --include='*.py' --include='*.sh' --include='*.yaml' --include='*.yml' \
        src tests tools ci 2>/dev/null | grep -v '^ci/no-external-paths.sh' || true)
# The Makefile is scanned SEPARATELY, and that is not tidiness. `--include` filters apply to
# explicitly-named files too, so naming `Makefile` alongside `--include='*.py'` excludes it — the
# gate reads the argument, reports OK, and has scanned nothing of it. That is the same shape as the
# empty-root-list defect this build just repaired one file over, arriving through a grep flag.
mk=$(grep -nE "$PAT" Makefile 2>/dev/null | sed 's/^/Makefile:/' || true)
hits="${hits}${hits:+$'\n'}${mk}"
hits="${hits#"${hits%%[![:space:]]*}"}"
if [ -n "$hits" ]; then
  echo "GATE FAIL: a machine-local absolute path is referenced from the build:" >&2
  echo "$hits" | sed 's/^/  /' >&2
  echo "  vendored fixtures live in fixtures/; resolve paths from REPO root instead." >&2
  exit 1
fi
echo "no-external-paths: OK"
