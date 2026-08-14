#!/usr/bin/env bash
# Read SCAN_ROOTS from labels.py — the ONE list (R5). Two lists drift; the one that
# drifts is the one nobody is reading.
set -euo pipefail

# --- THE INTERPRETER, AND WHY IT IS DISCOVERED RATHER THAN DEFAULTED -----------------------
#
# This line used to default `PY` to an absolute path in one developer's home directory, and it was
# NC-CI01's own defect living inside the machinery that prevents it. On any machine where that
# absolute path does not exist — i.e. every fresh clone that does not pass `CDFC_PY` by hand —
# `cdfc_roots` produced nothing, `assert_roots_exist` iterated ZERO roots, and every gate built on
# it printed OK and exited 0 having grepped no files at all. Demonstrated with a bare `except:`
# planted in the tree: the real run failed correctly; `CDFC_PY=/nonexistent` passed.
#
# `set -euo pipefail` does not catch it, and that is the part worth remembering: the failure was
# inside a process substitution `< <("$@")`, whose exit status bash discards. A gate cannot rely on
# the shell to notice that its input was empty.
#
# So: discover, in order, and REFUSE if nothing works. A gate with no interpreter must be red, not
# quiet — that is the whole rule this file exists to enforce, applied to itself.
# **THE PROBE HAS TO BE THE WHOLE JOB, NOT A HANDSHAKE.** It used to be `import cdfc` — and
# `src/cdfc/__init__.py` imports nothing, so a bare system interpreter with none of the project's
# dependencies installed passes it. On a fresh clone with no `.venv`, `_pick_python` therefore
# selected that interpreter, announced nothing, and the gates built on it failed one by one with
# `ModuleNotFoundError: No module named 'yaml'` — a diagnosis about the wrong thing, three layers
# from the cause.
#
# The whole point of this discovery is to REFUSE rather than half-work. So it probes for what the
# gates actually use — `yaml` (`catalogue-ids`), `lxml` (the ingest path) — as well as for `cdfc`
# itself. An interpreter that can import an empty package and nothing else is not an interpreter
# that can run this build, and saying so once here is worth more than a stack trace per gate.
#
# **Found by a fresh clone, which is the only place it could be found**: every developer machine
# has a `.venv`, and the first candidate that works masks the probe's weakness completely.
_here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
_PROBE='import sys; sys.path.insert(0,"'"$_here"'/src"); import cdfc, yaml, lxml.etree'
_pick_python() {
  local c
  for c in "${CDFC_PY:-}" "$_here/.venv/bin/python" "$(command -v python3 || true)"; do
    [ -n "$c" ] && [ -x "$c" ] || continue
    if "$c" -c "$_PROBE" >/dev/null 2>&1; then
      printf '%s' "$c"
      return 0
    fi
  done
  return 1
}
if ! PY="$(_pick_python)"; then
  echo "GATE FAIL: no interpreter can run this build. Tried \$CDFC_PY, .venv/bin/python, python3." >&2
  echo "  The probe is 'import cdfc, yaml, lxml.etree' and not merely 'import cdfc': cdfc's" >&2
  echo "  __init__ imports nothing, so a bare interpreter passes that and then fails inside" >&2
  echo "  every gate with a ModuleNotFoundError about something else." >&2
  echo "  Install the lockfile (pip install -r requirements.lock) or set CDFC_PY." >&2
  echo "  A gate that cannot read its own scan roots must be RED, never quiet: a grep over" >&2
  echo "  nothing reports success, which is NC-CI01." >&2
  exit 1
fi
export PY

cdfc_roots() { "$PY" -c 'import sys; sys.path.insert(0,"src"); from cdfc.surface.labels import SCAN_ROOTS; print("\n".join(SCAN_ROOTS))'; }
cdfc_surface_roots() { "$PY" -c 'import sys; sys.path.insert(0,"src"); from cdfc.surface.labels import SURFACE_ROOTS; print("\n".join(SURFACE_ROOTS))'; }

# A grep over a MISSING directory exits 0 and reports success. Every gate that greps
# must assert existence FIRST or it passes trivially — NC-CI01.
#
# THREE ways this can fail and all three are now checked, because only the third was:
#   1. the command that produces the list FAILS      -> its status is captured, not discarded
#   2. the list is EMPTY                             -> zero roots is not zero problems
#   3. a named root does not exist                   -> the original check
assert_roots_exist() {
  local out rc=0
  if ! out="$("$@" 2>/dev/null)"; then
    echo "GATE FAIL: the scan-root command failed; a gate cannot grep a list it could not read" >&2
    return 1
  fi
  if [ -z "${out//[[:space:]]/}" ]; then
    echo "GATE FAIL: the scan-root list is EMPTY. A grep over no roots reports success — NC-CI01." >&2
    return 1
  fi
  while IFS= read -r r; do
    [ -z "$r" ] && continue
    if [ ! -d "$r" ]; then echo "GATE FAIL: scan root '$r' does not exist (a grep over it would pass trivially)" >&2; rc=1; fi
  done <<< "$out"
  return $rc
}
