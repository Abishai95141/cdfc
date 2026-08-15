"""P12-B4 — the five-gate attrition funnel. **Nothing is filtered before stage 0.**

**A 20:1 attrition displayed honestly is a stronger demonstration than a settled-fraction bar,
because no competitor will show it — and a 600:0 attrition displayed honestly is stronger still.**
The funnel is the deliverable and it is *more* informative when nothing survives, because it says
**where** the candidates died.

## Stage 0 is the PLANNED count, and the discard pile is inside it

`stages[0].entered == |obligations| × |regimes| × k`. A malformed candidate is a **row**, not an
absence: it enters at `generated` and dies at `parsed`. Starting the funnel at
`600 − discards` would report a curated denominator and make the parse stage invisible — which is
NC-M11, and it is the same defect as every other truncated denominator in this project, wearing
the clothes of a data-cleaning step.

## Every rejection carries its measured number

A `RejectionRow` with a null measured number **fails to construct**. *"Rejected at G2"* is not a
finding; *"rejected at G2 with `K/O = 0.05` against a bar of 0.80"* is. The difference is what
makes the funnel readable by someone who did not run it, and it is the difference between a table
and a log.

## The two attrition numbers are DIFFERENT TESTS and both are printed

| Test | Threshold | Question |
|---|---|---|
| the settling experiment (G-SETTLE) | `K/O > 0` **and** marginal kill over `B0 ∪ B1 ∪ B2` at §0.6 | *can a model-proposed candidate fire at all, and does it beat free work?* |
| registry admission | `K/O ≥ 0.80` on the classes the predicate **claims** | *is this check good enough to be applied to a regulated filing?* |

**A predicate at `K/O = 0.05` survives the experiment and fails the registry.** A document quoting
one of these has quoted the wrong one, so `funnel.json` carries both counts and `DECISION.md`
prints them in the same paragraph.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Literal

StageName = Literal[
    "generated", "parsed", "G0", "G1", "G3_proof", "G2", "G3_empirical", "G4"
]

# THE FIXED GATE ORDER. Cheap gates first, so few candidates reach G2 — and a build in which G2 ran
# before G0 would show up as a tenfold blow-out in PERF-E6-GATE rather than as a quiet cost.
STAGE_ORDER: Final[tuple[StageName, ...]] = (
    "generated", "parsed", "G0", "G1", "G3_proof", "G2", "G3_empirical", "G4",
)

# The registry's bar, quoted here so the two-attrition-numbers table reads one constant.
REGISTRY_KILL_BAR: Final[str] = "0.80"


class FunnelInvariantViolated(ValueError):
    """A stage count that cannot be true of a funnel."""


@dataclass(frozen=True, slots=True)
class RejectionRow:
    """One candidate's death: the gate, the reason, **and the number that decided it.**"""

    candidate_sha256: str
    gate: StageName
    reason: str
    measured: str                    # the number, as a string, never absent
    cells_it_would_have_covered: int

    def __post_init__(self) -> None:
        if not self.reason:
            raise FunnelInvariantViolated("a rejection with no reason cannot be acted on")
        if not self.measured:
            raise FunnelInvariantViolated(
                f"candidate {self.candidate_sha256[:12]} was rejected at {self.gate} with no "
                "measured number. 'Rejected at G2' is not a finding; 'rejected at G2 with K/O = "
                "0.05 against a bar of 0.80' is. A rejection table without numbers is a log."
            )

    def as_obj(self) -> dict[str, Any]:
        return {
            "candidate_sha256": self.candidate_sha256, "gate": self.gate, "reason": self.reason,
            "measured": self.measured,
            "cells_it_would_have_covered": self.cells_it_would_have_covered,
        }


@dataclass(frozen=True, slots=True)
class FunnelStage:
    name: StageName
    entered: int
    survived: int
    rejections: tuple[RejectionRow, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.survived > self.entered:
            raise FunnelInvariantViolated(
                f"{self.name}: {self.survived} survived of {self.entered} entered"
            )
        if self.entered - self.survived != len(self.rejections):
            raise FunnelInvariantViolated(
                f"{self.name}: {self.entered - self.survived} candidates died but "
                f"{len(self.rejections)} rejection rows exist. A death with no row is a candidate "
                "that left the funnel without a reason, which is the absence this whole project "
                "refuses to render as silence."
            )

    def as_obj(self) -> dict[str, Any]:
        return {
            "name": self.name, "entered": self.entered, "survived": self.survived,
            "rejections": [r.as_obj() for r in self.rejections],
        }


@dataclass(frozen=True, slots=True)
class Funnel:
    stages: tuple[FunnelStage, ...]
    planned: int
    by_stratum: dict[str, int]
    by_regime: dict[str, int]
    registry_bar_survivors: int

    def __post_init__(self) -> None:
        if not self.stages:
            raise FunnelInvariantViolated("a funnel with no stages reports nothing")
        if self.stages[0].name != "generated":
            raise FunnelInvariantViolated(
                f"stage 0 is {self.stages[0].name!r}, not 'generated'. Discards enter at generated "
                "and die at parsed; a funnel starting anywhere else has filtered before counting."
            )
        if self.stages[0].entered != self.planned:
            raise FunnelInvariantViolated(
                f"stage 0 entered {self.stages[0].entered} against a planned "
                f"{self.planned}. Stage 0 is |obligations| × |regimes| × k, DISCARDS INCLUDED. A "
                "funnel that starts at 'planned minus discards' has reported a curated "
                "denominator and made the parse stage invisible — NC-M11."
            )
        for a, b in zip(self.stages, self.stages[1:]):
            if a.survived != b.entered:
                raise FunnelInvariantViolated(
                    f"{a.name} passed {a.survived} to {b.name}, which received {b.entered}. The "
                    "funnel is monotone and the hand-off is an EQUALITY: a gap between two stages "
                    "is a population that left the measurement without being counted anywhere."
                )
        if self.registry_bar_survivors > self.stages[-1].survived:
            raise FunnelInvariantViolated(
                "more candidates cleared the registry's bar than cleared the experiment's. The "
                f"registry bar is K/O ≥ {REGISTRY_KILL_BAR} and the experiment's is K/O > 0, so "
                "the registry's survivors are a SUBSET — a count that inverts them has confused "
                "the two tests, which is precisely what printing both is for."
            )

    @property
    def survived(self) -> int:
        return self.stages[-1].survived

    def as_obj(self) -> dict[str, Any]:
        return {
            "planned": self.planned,
            "stages": [s.as_obj() for s in self.stages],
            "survived_experiment_bar": self.survived,
            "survived_registry_bar": self.registry_bar_survivors,
            "registry_bar": f"K/O >= {REGISTRY_KILL_BAR}",
            "experiment_bar": "K/O > 0 and marginal kill over B0|B1|B2 at the §0.6 preconditions",
            "by_stratum": dict(self.by_stratum),
            "by_regime": dict(self.by_regime),
        }


def planned_count(*, obligations: int, regimes: int, k: int) -> int:
    """`|obligations| × |regimes| × k`. **The funnel's stage 0, and the run's call count.**"""
    if min(obligations, regimes, k) < 0:
        raise ValueError("a planned count is a product of non-negative integers")
    return obligations * regimes * k


def funnel(
    records: Sequence[Any],
    rejections: Sequence[RejectionRow],
    *,
    obligations: int,
    regimes: int,
    k: int,
    registry_bar_survivors: int = 0,
    by_stratum: dict[str, int] | None = None,
    by_regime: dict[str, int] | None = None,
) -> Funnel:
    """Build the funnel from the candidate records and every rejection row.

    **The invariant is asserted, not assumed:** `stages[0].entered == len(records) ==
    |obligations| × |regimes| × k`. A `records` sequence that has already had its discards removed
    fails here rather than producing a funnel that looks tidier than the run was.
    """
    planned = planned_count(obligations=obligations, regimes=regimes, k=k)
    if len(records) != planned:
        raise FunnelInvariantViolated(
            f"{len(records)} candidate records against a planned {planned}. Every call made is a "
            "row, including the malformed ones: the discard pile is data, and a funnel built from "
            "the survivors of a filter nobody counted is a funnel about a different experiment."
        )

    by_gate: dict[StageName, list[RejectionRow]] = {s: [] for s in STAGE_ORDER}
    for r in rejections:
        by_gate[r.gate].append(r)

    stages: list[FunnelStage] = []
    alive = planned
    for name in STAGE_ORDER:
        dead = by_gate[name]
        entered = alive
        alive = entered - len(dead)
        if alive < 0:
            raise FunnelInvariantViolated(
                f"{name} rejected {len(dead)} of the {entered} that entered it"
            )
        stages.append(FunnelStage(name=name, entered=entered, survived=alive,
                                  rejections=tuple(dead)))
    return Funnel(
        stages=tuple(stages), planned=planned,
        by_stratum=by_stratum or {}, by_regime=by_regime or {},
        registry_bar_survivors=registry_bar_survivors,
    )
