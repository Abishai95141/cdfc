"""P14-B4 — the five-gate attrition funnel. **Three integers per stage, never two.**

## `skipped` is new, and without it stage one is either a constant or a lie

G0 is a verbatim-quote guard: its six closed rejection reasons all presuppose a clause. The 280
harvested FME candidates are derived from the workbook's own formulas and data validations — they
cite no regulation and carry `clause: None`.

Both branches are bad. If G0 REJECTS them, all 280 die at stage one and D-REJECT — the flagship
demonstration that the gate is not decorative — becomes unreachable. If G0 silently SKIPS them,
stage one reads `280 -> 280`, the first column is a constant, and **a gate that does not apply to
the population it is run over is reporting a pass it did not compute.**

`03`/`04` own the disposition. This surface owns making it COUNTABLE:

1. three integers at every stage, and `entered == skipped + survived + len(rejections)`;
2. a stage whose `skipped == entered` renders `NOT APPLICABLE — 0 evaluated`, not a full-width bar;
3. the obligation-coverage PAIR, published together or not at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# THE ORDER IS THE GATE ORDER. It is not a display preference, and it is asserted against the
# qualification pipeline rather than pinned as a literal here.
FUNNEL_STAGES: Final[tuple[str, ...]] = (
    "generated", "G0.scope", "G1.binds", "G3.proof", "G2.kill", "G3.empirical", "G4.ffr",
)

NOT_APPLICABLE: Final[str] = "NOT APPLICABLE — 0 evaluated"

# The sentence that renders VERBATIM beside the obligation pair. Publishing a zero is the honest
# case and must not be special-cased into an empty state.
NO_STATUTORY_PREDICATE_YET: Final[str] = (
    "no harvested predicate yet implements a statutory clause"
)


class StageArithmeticDoesNotClose(ValueError):
    """`entered != skipped + survived + rejections`. A skip laundered into a survival."""


class UnpairedObligationCount(ValueError):
    """One obligation-coverage number rendered without the other (arbitration C2)."""


@dataclass(frozen=True, slots=True)
class RejectionRow:
    candidate_id: str
    gate: str
    measured: str                 # the NUMBER that decided it; empty does not render
    cells_it_would_have_covered: int

    def __post_init__(self) -> None:
        if not self.measured.strip():
            raise ValueError(
                f"{self.candidate_id}: rejected by {self.gate} with no measured number. A "
                "rejection without the number that decided it is an opinion with a gate's name on "
                "it, and the Rejected tab is the one place this product proves its gate is real."
            )


@dataclass(frozen=True, slots=True)
class FunnelStage:
    name: str
    entered: int
    skipped: int                  # the gate DOES NOT APPLY. Never counted as a survivor.
    survived: int
    rejections: tuple[RejectionRow, ...]

    def __post_init__(self) -> None:
        total = self.skipped + self.survived + len(self.rejections)
        if self.entered != total:
            raise StageArithmeticDoesNotClose(
                f"{self.name}: entered={self.entered} but skipped+survived+rejections={total}. A "
                "skip cannot be laundered into a survival by omission -- which is exactly how a "
                "`280 -> 280` first row gets printed and read as attrition."
            )

    @property
    def wholly_skipped(self) -> bool:
        return self.entered > 0 and self.skipped == self.entered

    def render(self) -> str:
        if self.wholly_skipped:
            return f"{self.name}: {NOT_APPLICABLE}"
        return (f"{self.name}: entered {self.entered} · skipped {self.skipped} · "
                f"survived {self.survived} · rejected {len(self.rejections)}")


@dataclass(frozen=True, slots=True)
class ObligationCoverage:
    """TWO numbers, never one (arbitration C2). They render together or not at all.

    The earlier form published a single, unqualified `harvested_predicates_with_an_obligation/280`
    reading `0 / 280` — which under the arbitrated mechanism is **wrong by 280**. An unqualified
    obligation count is the defect, in EITHER direction.
    """

    with_statute_obligation: int | None
    with_template_obligation: int | None
    total: int

    def __post_init__(self) -> None:
        if (self.with_statute_obligation is None) != (self.with_template_obligation is None):
            raise UnpairedObligationCount(
                "one obligation-coverage number is present and the other is not. A STATUTE count "
                "alone reads as 'nothing is covered'; a TEMPLATE count alone reads as 'everything "
                "is'. Both are wrong and each is wrong by the other's value."
            )

    def render(self) -> str:
        if self.with_statute_obligation is None:
            return "obligation coverage: not measured"
        return (
            f"predicates_with_a_STATUTE_obligation: {self.with_statute_obligation} / {self.total} · "
            f"predicates_with_a_TEMPLATE_obligation: {self.with_template_obligation} / {self.total}"
            f" — {NO_STATUTORY_PREDICATE_YET}"
            if self.with_statute_obligation == 0
            else
            f"predicates_with_a_STATUTE_obligation: {self.with_statute_obligation} / {self.total} · "
            f"predicates_with_a_TEMPLATE_obligation: {self.with_template_obligation} / {self.total}"
        )


def attrition_funnel(stages: tuple[FunnelStage, ...]) -> tuple[FunnelStage, ...]:
    """Validated in stage order. The order is read from `FUNNEL_STAGES`, not from the caller."""
    names = [s.name for s in stages]
    expected = [n for n in FUNNEL_STAGES if n in set(names)]
    if names != expected:
        raise ValueError(
            f"stages arrived as {names} and the gate order is {expected}. A funnel rendered out of "
            "gate order tells a story about attrition that did not happen."
        )
    return stages
