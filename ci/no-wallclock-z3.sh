#!/usr/bin/env bash
# Registry row 48. Z3 is bounded by `rlimit`, NEVER by a wall clock.
#
# WHY IT EXISTS. `set("timeout", ms)` makes a proof verdict a function of what else the machine was
# doing: the same candidate is `unknown` on a loaded runner and `trivially_true` on an idle one, so
# `test_det__z3_unknown_is_reproducible` becomes a coin toss and a predicate's ADMISSION becomes a
# property of the CI queue. `rlimit` counts solver work and is identical on every machine.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }

SCAN="src/cdfc/qualify"
[ -d "$SCAN" ] || { echo "GATE FAIL: $SCAN does not exist; a grep over it would report success" >&2; exit 1; }

# Any wall-clock bound handed to a solver, by either spelling — over CODE, not prose.
#
# The comment-stripping is not hygiene: on this gate's first run it matched the sentence in
# `g3_degeneracy.py` that EXPLAINS why a timeout is banned. A gate that fires on its own rationale
# gets "fixed" by deleting the rationale, which is the worst available outcome for a rule whose
# whole value is that the next reader knows why it exists.
CODE=$(mktemp)
grep -rn --include='*.py' '' "$SCAN" | sed 's/[[:space:]]#.*$//' > "$CODE"
hits=$(grep -nE 'set\s*\(\s*["'"'"']timeout["'"'"']|set_param\s*\([^)]*timeout|SolverFor\([^)]*timeout' \
       "$CODE" 2>/dev/null | sed 's/^[0-9]*://' || true)
rm -f "$CODE"

# And the positive half: a module that drives z3 must SET an rlimit. A solver with no budget at
# all is worse than one with a wall clock — it can hang the admission run for ever.
drivers=$(grep -rln 'z3\.Solver()' --include='*.py' "$SCAN" 2>/dev/null || true)
missing=""
for f in $drivers; do
  grep -q 'set("rlimit"' "$f" || missing="$missing $f"
done

if [ -n "$hits" ] || [ -n "$missing" ]; then
  echo "GATE FAIL: Z3 is bounded by rlimit, never by a wall clock:" >&2
  [ -n "$hits" ] && echo "$hits" >&2
  [ -n "$missing" ] && echo "  a z3.Solver() with no rlimit:$missing" >&2
  echo "  A wall clock makes a proof verdict a function of machine load, so the same" >&2
  echo "  candidate is 'unknown' on one runner and 'trivially_true' on another." >&2
  exit 1
fi
echo "no-wallclock-z3: OK"
