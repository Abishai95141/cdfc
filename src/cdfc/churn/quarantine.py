"""V5 — liveness-witness replay. **A kill case that stops dying quarantines its predicate.**

Every admitted predicate carries a stored `kill_case`: a mutant it demonstrably caught during the
qualification campaign. That artifact is the only standing evidence the predicate detects anything,
and it is evidence *about a workbook*. When the template moves, the mutant may no longer be
constructible, or may no longer be caught — and a predicate whose only proof of detection no longer
reproduces is a predicate nobody can say is working.

**Quarantine is not rejection.** A QUARANTINED predicate has not been shown to be wrong; it has
stopped being shown to be right. The distinction is why it is a fourth state rather than a
withdrawal, and why nothing here clears it.

## Nothing re-admits automatically, and that is checked structurally

There is no code path in this package that assigns `ACTIVE`.
`tests/unit/test_quarantine.py::test_quarantine__nothing_re_admits_automatically` walks the AST of
every module under `cdfc/churn/` looking for the literal in an assignment or a return. A comment
promising the absence would be a promise; the walk is a measurement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

QUARANTINED: Final[str] = "QUARANTINED"

NO_KILL_CASE: Final[str] = (
    "no stored kill case — the predicate has never demonstrated a catch against this template"
)


@dataclass(frozen=True, slots=True)
class QuarantineReport:
    quarantined: tuple[str, ...]
    reasons: dict[str, str]
    replayed: int
    still_dying: tuple[str, ...]
    not_replayable: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.replayed != len(self.quarantined) + len(self.still_dying) + len(
            self.not_replayable
        ):
            raise ValueError(
                f"replayed={self.replayed} but the dispositions sum to "
                f"{len(self.quarantined) + len(self.still_dying) + len(self.not_replayable)}. "
                "A replay whose census does not close has lost a predicate somewhere."
            )

    @property
    def clears_nothing(self) -> bool:
        """**True, always.** Stated as a property so a caller can assert it rather than trust it."""
        return True


def replay_liveness(
    kill_cases: dict[str, Any],
    *,
    replay: Any,
) -> QuarantineReport:
    """Replay each stored kill case. `replay(predicate_id, case) -> bool | None`.

    * `True`  — the mutant still dies. The predicate keeps its state.
    * `False` — the mutant survives. **QUARANTINED.**
    * `None`  — the case could not be constructed against this template. Also **QUARANTINED**, and
      with a different reason: an unreplayable case is not evidence of detection either, and
      treating "could not check" as "checked and fine" is the swallowed-exception failure wearing a
      version bump's clothes.
    """
    quarantined: list[str] = []
    still: list[str] = []
    unreplayable: list[str] = []
    reasons: dict[str, str] = {}
    for pid in sorted(kill_cases):
        case = kill_cases[pid]
        if case is None:
            quarantined.append(pid)
            reasons[pid] = NO_KILL_CASE
            continue
        verdict = replay(pid, case)
        if verdict is True:
            still.append(pid)
        elif verdict is False:
            quarantined.append(pid)
            reasons[pid] = (
                "the stored kill case no longer dies against this template: the one mutant this "
                "predicate demonstrably caught now survives it"
            )
        else:
            quarantined.append(pid)
            unreplayable.append(pid)
            reasons[pid] = (
                "the stored kill case could not be constructed against this template. Not a "
                "failure to detect — a failure to ASK, which is not evidence of detection either"
            )
    quarantined = sorted(set(quarantined) - set(unreplayable))
    return QuarantineReport(
        quarantined=tuple(quarantined), reasons=reasons, replayed=len(kill_cases),
        still_dying=tuple(still), not_replayable=tuple(sorted(unreplayable)),
    )
