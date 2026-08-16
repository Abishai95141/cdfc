"""V7 — withdrawal is DATED and REASONED, and it is a new row rather than a deletion.

A withdrawn predicate does not disappear. Runs that already cited it must stay explicable, and an
attestation covering a run that used a predicate nobody can look up is an attestation covering
nothing. So withdrawal writes `withdrawn_on` and `withdrawn_reason` onto a superseding row and
leaves the original in place.

**`withdrawn_reason` is drawn from a closed set.** Free text here becomes a field that says
"deprecated" 400 times, and a reason that carries no information is the same defect as a generic
remedy string on the Unchecked panel: it looks exactly like a surface that thought about each case.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# The closed set. Each is a DIFFERENT thing to have happened, and a reader who sees one knows what
# to do next; that is the test for whether a code earns its place.
WITHDRAWN_REASONS: Final[dict[str, str]] = {
    "superseded": "a later version of this predicate is admitted; this row is kept for runs that cited it",
    "obligation_removed": "the obligation it implements no longer exists in the instrument",
    "template_construct_gone": "the construct it binds to is absent from the current template",
    "false_failure_measured": "a measured false-failure rate above its tier's bound",
    "unsound": "the check was wrong about a filing that was correct, and the error is in the predicate",
    "unreplayable_kill_case": "quarantined and not cleared; the stored kill case never replayed again",
}


class WithdrawalReasonNotInVocabulary(ValueError):
    """Free text where a reason code belongs."""


class WithdrawalUndated(ValueError):
    """A withdrawal with no date cannot be placed in a supersession chain."""


@dataclass(frozen=True, slots=True)
class Withdrawal:
    predicate_id: str
    version: int
    withdrawn_on: str          # ISO date, an ARGUMENT; nothing here reads a clock
    withdrawn_reason: str
    superseded_by: str | None = None

    def __post_init__(self) -> None:
        if not self.withdrawn_on.strip():
            raise WithdrawalUndated(
                f"{self.predicate_id}: no withdrawal date. Supersession is an ORDER, and a row "
                "with no date cannot be placed in one."
            )
        if self.withdrawn_reason not in WITHDRAWN_REASONS:
            raise WithdrawalReasonNotInVocabulary(
                f"{self.withdrawn_reason!r} is not one of {sorted(WITHDRAWN_REASONS)}. A free-text "
                "reason becomes a column that says 'deprecated' every time, which tells a reader "
                "nothing about what to do next."
            )
        if self.withdrawn_reason == "superseded" and not self.superseded_by:
            raise ValueError(
                f"{self.predicate_id}: reason 'superseded' with no superseding row. The whole "
                "content of that reason is the thing that replaced it."
            )

    def render(self) -> str:
        tail = f" → {self.superseded_by}" if self.superseded_by else ""
        return (f"{self.predicate_id} v{self.version} withdrawn {self.withdrawn_on}: "
                f"{WITHDRAWN_REASONS[self.withdrawn_reason]}{tail}")


def withdraw(predicate_id: str, version: int, *, on: str, reason: str,
             superseded_by: str | None = None) -> Withdrawal:
    return Withdrawal(predicate_id=predicate_id, version=version, withdrawn_on=on,
                      withdrawn_reason=reason, superseded_by=superseded_by)
