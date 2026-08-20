#!/usr/bin/env bash
# A document describing the CURRENT tree may not carry a claim the tree has falsified.
#
# Every pattern below was TRUE of this repository once and is false now. They are not hypothetical
# and they are not phrasing preferences: each was found being asserted after the code had moved,
# and two of them were RENDERED INTO THE PRODUCT by `cdfc.surface.openitems`, which reads
# docs/OPEN-ITEMS.md and shows every `- [OPEN]` line to a user.
#
# The rule is not "never write these words". It is that a line carrying one must ALSO carry a
# closure marker saying it is history:
#
#     [CLOSED   [SUPERSEDED   [CORRECTED   [HISTORICAL   NOT:   was:
#
# so a dated record can quote what it corrects. A document with no marker is claiming it of the
# tree as it stands, and the tree disagrees.
#
# `docs/audit/` and `docs/measurements/` are exempt as a DIRECTORY, because they are dated records
# by construction -- an assessment of what was true on a date is not a claim about today. That
# exemption is the hole to watch: it is why `AUDIT-TRAIL.md` records corrections separately and
# why `tools/audit_trail.py` checks every citation in it resolves.
set -euo pipefail
cd "$(dirname "$0")/.."

# Patterns are built from fragments so this file does not match itself -- a gate defeated by the
# prose explaining it is a shape this repository has hit more than a dozen times.
P1="refuses every filing"
P2="takes no template"$' parameter'
P3="raised by no"$' code'
P4="702 of 724"
P5="481 of 498"
P6="Every figure in it"$'\n'
# A line is HISTORY if it says so. Broad on purpose: the cost of a missed marker is a false red
# on a correction someone already wrote, and the first run of this gate produced six of exactly
# that -- it flagged its own author's correction notices.
MARK='\[CLOSED|\[SUPERSEDED|\[CORRECTED|\[HISTORICAL|CORRECTED|SUPERSEDED|CORRECTION|was true|no longer|must not be quoted|used to|previously|does not reproduce|not reproducible|first run|earlier'

# A DOCUMENT is history if its own header says so. Both dated plan documents carry a supersession
# pointer in their first lines, and a pre-registration whose criteria may never be edited cannot
# be asked to annotate the claim each criterion was written against.
DOC_MARK='SUPERSEDED IN PART|NEVER EDITED|dated decision record|dated record|PRE-REGISTERED CRITERIA'

fail=0
scan() {
  local pat="$1" label="$2"
  # -F fixed-string: a pattern is a literal claim, never a regex somebody has to escape.
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    local file="${hit%%:*}"
    case "$file" in docs/audit/*|docs/measurements/*|ci/no-stale-claim.sh) continue;; esac
    # A document that declares itself a dated record in its own header is exempt as a whole.
    if head -40 "$file" 2>/dev/null | grep -Eq "$DOC_MARK"; then continue; fi
    if ! printf '%s' "$hit" | grep -Eq "$MARK"; then
      echo "  $hit" >&2
      fail=1
    fi
  done < <(grep -rnF "$pat" README.md docs PROGRESS.md 2>/dev/null || true)
}
scan "$P1" "endpoint"
scan "$P2" "runner"
scan "$P3" "denominator_disagreement"
scan "$P4" "attestation split"
scan "$P5" "attestation split"

if [ "$fail" -ne 0 ]; then
  echo "GATE FAIL: a document describing the current tree carries a claim the tree falsified." >&2
  echo "  Each line above states something that was true once. If it is HISTORY, mark it:" >&2
  echo "  [CLOSED ...] / [SUPERSEDED ...] / CORRECTED <date> / 'previously' / 'used to'." >&2
  echo "  If it is not history, the document is wrong and the fix is the document." >&2
  exit 1
fi
echo "no-stale-claim: OK"
