#!/usr/bin/env bash
# BARRIER 5. `src/cdfc/model/propose.py` may not exist without a RETAIN decision record.
#
# `plan/06` names this file as an entry criterion for P12 AND P13 and no build created it — the
# same class as `docs/measurements/P4-transfer-mechanical.md`, an entry criterion naming a file
# nobody writes, which nobody discovers until the phase cannot start. P13-B0 creates it.
#
# The rule has TWO directions and the second is the one that gets forgotten:
#   * propose.py without experiments/E6/DECISION.md  -> a proposer that shipped before the
#     experiment that licenses it;
#   * propose.py WITH a DECISION.md whose verdict is DELETE or PENDING -> a proposer that shipped
#     against its own experiment's answer, which is worse, because a record exists and says no.
set -euo pipefail
cd "$(dirname "$0")/.."

PROPOSE="src/cdfc/model/propose.py"
DECISION="experiments/E6/DECISION.md"

if [ ! -e "$PROPOSE" ]; then
  echo "ok: $PROPOSE is absent; barrier 5 has nothing to admit"
  exit 0
fi

if [ ! -f "$DECISION" ]; then
  echo "GATE FAIL: $PROPOSE exists and $DECISION does not." >&2
  echo "  A proposer may not ship before the experiment that licenses it has a record." >&2
  exit 1
fi

# The verdict line. `status: RETAIN` and nothing else admits.
if grep -qiE '^\*\*status:[[:space:]]*RETAIN' "$DECISION"; then
  echo "ok: $PROPOSE is admitted by a RETAIN decision in $DECISION"
  exit 0
fi

VERDICT="$(grep -iE '^\*\*status:' "$DECISION" | head -1 || echo '(no status line)')"
echo "GATE FAIL: $PROPOSE exists and $DECISION does not record a RETAIN." >&2
echo "  found: $VERDICT" >&2
echo "  A proposer shipping against its own experiment's answer is worse than one shipping" >&2
echo "  before the experiment: a record exists, and it says no." >&2
exit 1
