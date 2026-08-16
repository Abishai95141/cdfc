"""P14-B4 — settled fraction over time. **The chart must be able to step down.**

A coverage number that can only rise is a marketing chart. When a template's hash bumps, affected
predicates go `PROVISIONAL`, leave the settled numerator, and the fraction FALLS — and if the
chart smooths, clamps or drops that, the fall is not a system property, it is a thing that
happened to a number nobody plotted.

**The step-downs are the most credible thing on this chart.** They are the evidence that the
number is measured rather than accumulated, so a decrease renders with the cause that produced it,
and a decrease without a cause does not render at all.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

HISTORY_PATH: Final[Path] = Path("reports/settled-history.jsonl")


class UnlabelledStepDown(ValueError):
    """The series decreased and the point carries no cause. It does not render."""


@dataclass(frozen=True, slots=True)
class HistoryPoint:
    at: str                 # ISO-8601, supplied; this module reads no clock
    settled: int
    field_surface: int
    admission: str
    cause: str | None = None

    def __post_init__(self) -> None:
        if self.settled > self.field_surface:
            raise ValueError(
                f"settled={self.settled} exceeds the field surface {self.field_surface}: a "
                "numerator larger than its denominator"
            )


def history_points(points: tuple[HistoryPoint, ...]) -> tuple[HistoryPoint, ...]:
    """Validate a series. **Nothing here sorts, clamps, smooths or takes a running maximum.**

    The absence of those four operations is the feature. `running_max` is one call and it would
    make every decrease invisible while the chart still looked like data.
    """
    for prev, cur in zip(points, points[1:], strict=False):
        if cur.settled < prev.settled and not (cur.cause or "").strip():
            raise UnlabelledStepDown(
                f"{cur.at}: settled fell from {prev.settled} to {cur.settled} with no cause. A "
                "step-down is the most credible point on this chart and an unexplained one is "
                "indistinguishable from a bug in the pipeline that produced it."
            )
    return points


def render_series(points: tuple[HistoryPoint, ...]) -> str:
    """One line per point, and every decrease carries its cause inline."""
    out: list[str] = []
    prev: HistoryPoint | None = None
    for p in points:
        line = f"{p.at}: {p.settled} of {p.field_surface} · {p.admission}"
        if prev is not None and p.settled < prev.settled:
            line += f" ▼ {p.cause}"
        out.append(line)
        prev = p
    return "\n".join(out)
