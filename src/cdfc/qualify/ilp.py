"""P7-B4 — SPADE's ILP, reimplemented. **Subsumption only at P7, and that is a declared state.**

The set-FFR constraint `max(FFR(S),FFR(f)) <= FFR(S∪{f}) <= FFR(S)+FFR(f)` needs an FFR, and no
false-failure rate has been measured for any predicate in this system — the blind-fill corpus
arrives at P8. So:

    ilp.select(candidates, constraints=[SUBSUMPTION])              at P7
    ilp.select(candidates, constraints=[SUBSUMPTION, SET_FFR])     at P8-B3

`test_ilp__ffr_constraint_absent_at_p7` asserts the P7 configuration AND its reason string, so the
omission is a declared state rather than a gap somebody has to notice.

**Reuse the algorithm, not the repository.** The SPADE repository is 17 stars, one fork, **no
licence field**, last pushed 2024-04-07. With the subsumption constraint alone the problem is a
maximum independent set over a PARTIAL ORDER, which is solved exactly by keeping every maximal
element — no solver, no dependency, and provably optimal rather than approximately so. Adding
PuLP/CBC for a constraint set this shape would be a 30 MB binary dependency doing arithmetic that
fits in this file.

**EVERY REMOVAL IS RECORDED.** NC-Q36: a subsumed predicate that vanishes without a `rejection` row
moves the settled fraction with no cause on the chart.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final


class Constraint(StrEnum):
    SUBSUMPTION = "subsumption"
    SET_FFR = "set_ffr"  # P8-B3. Not available at P7.


P7_CONSTRAINTS: Final[tuple[Constraint, ...]] = (Constraint.SUBSUMPTION,)

FFR_ABSENT_REASON: Final[str] = (
    "the set-FFR constraint requires a false-failure rate, and no FFR has been measured for any "
    "predicate in this system: the blind-fill corpus arrives at P8. Configured at P7 as "
    "constraints=[SUBSUMPTION]; at P8-B3 as [SUBSUMPTION, SET_FFR]."
)


class UnavailableConstraint(ValueError):
    """A constraint whose input does not exist yet. Never silently dropped."""


@dataclass(frozen=True, slots=True)
class Removal:
    removed: str
    subsumed_by: str
    cells_would_have_covered: int


@dataclass(frozen=True, slots=True)
class Selection:
    kept: tuple[str, ...]
    removals: tuple[Removal, ...]

    def __post_init__(self) -> None:
        overlap = set(self.kept) & {r.removed for r in self.removals}
        if overlap:
            raise ValueError(f"a predicate is both kept and removed: {sorted(overlap)}")


def select(
    candidates: Sequence[Any],
    *,
    constraints: Sequence[Constraint] = P7_CONSTRAINTS,
    subsumes: Callable[[Any, Any], bool | None],
    cells_of: Mapping[str, int],
) -> Selection:
    """Keep every maximal element of the subsumption order; record every removal.

    `subsumes(a, b)` returns True when `a` implies `b`, False when it does not, and **None when it
    could not be decided** — and None is treated as "does not subsume". An undecided implication
    must never remove a predicate: the ILP would then be dropping checks on the strength of a proof
    nobody has, which is `UNKNOWN` read as a verdict one level up.
    """
    if Constraint.SET_FFR in constraints:
        raise UnavailableConstraint(FFR_ABSENT_REASON)
    if Constraint.SUBSUMPTION not in constraints:
        return Selection(tuple(c.id for c in candidates), ())

    removed: dict[str, str] = {}
    for a in candidates:
        for b in candidates:
            if a.id == b.id or b.id in removed or a.id in removed:
                continue
            if subsumes(a, b) is True and subsumes(b, a) is not True:
                removed[b.id] = a.id
    kept = tuple(c.id for c in candidates if c.id not in removed)
    return Selection(
        kept=kept,
        removals=tuple(
            Removal(removed=k, subsumed_by=v, cells_would_have_covered=cells_of.get(k, 0))
            for k, v in sorted(removed.items())
        ),
    )
