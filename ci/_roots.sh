#!/usr/bin/env bash
# Read SCAN_ROOTS from labels.py — the ONE list (R5). Two lists drift; the one that
# drifts is the one nobody is reading.
set -euo pipefail
PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
cdfc_roots() { "$PY" -c 'import sys; sys.path.insert(0,"src"); from cdfc.surface.labels import SCAN_ROOTS; print("\n".join(SCAN_ROOTS))'; }
cdfc_surface_roots() { "$PY" -c 'import sys; sys.path.insert(0,"src"); from cdfc.surface.labels import SURFACE_ROOTS; print("\n".join(SURFACE_ROOTS))'; }
# A grep over a MISSING directory exits 0 and reports success. Every gate that greps
# must assert existence FIRST or it passes trivially — NC-CI01.
assert_roots_exist() {
  local rc=0
  while IFS= read -r r; do
    [ -z "$r" ] && continue
    if [ ! -d "$r" ]; then echo "GATE FAIL: scan root '$r' does not exist (a grep over it would pass trivially)" >&2; rc=1; fi
  done < <("$@")
  return $rc
}
