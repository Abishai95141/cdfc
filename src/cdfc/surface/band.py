"""P14-B1 — the stacked band, and the invariant that it **never fills**.

The band is the one graphic on the report. It shows the field surface split by item state, and its
governing property is structural rather than stylistic:

> **`sum(settled widths) < total width`, strictly, for every possible input.**

The last two segments are always `NOT_SETTLEABLE_FROM_ARTIFACT` and `RESIDUE`, both hatched, both
with a non-zero rendered width **whether or not their counts are known**. There is no run — not a
perfect one, not a hypothetical one — that produces a full bar. A reader cannot see one because the
geometry cannot draw one.

**Why that is not a trick.** Those two segments are real and permanently non-empty:

- `NOT_SETTLEABLE_FROM_ARTIFACT` — obligations that cannot be decided from the filing at all,
  because the fact they turn on is not in it. Cross-document binding is the standing example and it
  is `DO_NOT_BUILD` on its own gate.
- `RESIDUE` — the measured count of constructed falsehoods no admitted check rejects. It is a
  **lower bound** on what the instrument cannot see, and it is a theorem about the check set rather
  than a gap in it.

A bar that filled would be claiming both were zero, and neither can be.

## `count is None` renders as *not yet measured*, never as zero

The residue is `None` until P10's procedure has run against this predicate set. **Zero and unknown
are different facts** — zero is a finding about the check set, `None` is a finding about us — and
the segment renders its width either way so the absence is visible rather than silent.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Final, Literal

Pattern = Literal["SOLID", "HATCH"]

SegmentKind = Literal[
    "SETTLED_PASS", "SETTLED_FAIL", "INDETERMINATE", "NOT_RUN", "NO_PREDICATE",
    "ERROR", "NOT_SETTLEABLE_FROM_ARTIFACT", "RESIDUE",
]

# The two that always close the band. Named as data so the invariant test reads the same tuple the
# builder does, rather than a second copy that could drift.
ALWAYS_LAST: Final[tuple[SegmentKind, SegmentKind]] = (
    "NOT_SETTLEABLE_FROM_ARTIFACT", "RESIDUE",
)

# The minimum rendered width, in per-mille of the band, for a segment whose count is zero or
# unknown. Per-mille and not a percentage: `ci/no-bare-rate.sh` polices percentages, and this is a
# GEOMETRY, not a measurement of anything.
MIN_WIDTH_PERMILLE: Final[int] = 12

HUMAN: Final[dict[str, str]] = {
    "SETTLED_PASS": "settled — a check ran and did not fire",
    "SETTLED_FAIL": "settled — a check ran and fired",
    "INDETERMINATE": "not settled — the check could not decide",
    "NOT_RUN": "not settled — the check did not run",
    "NO_PREDICATE": "not checked — no predicate exists for this cell",
    "ERROR": "not settled — the check errored",
    "NOT_SETTLEABLE_FROM_ARTIFACT": "not settleable from this filing at all",
    "RESIDUE": "constructed falsehoods no admitted check rejects (lower bound)",
}


class BandInvariantViolated(ValueError):
    """A band that could fill. Never a warning."""


@dataclass(frozen=True, slots=True)
class Segment:
    kind: SegmentKind
    count: int | None            # None == "not yet measured" — rendered as such, never as 0
    pattern: Pattern
    label: str                   # an ABSOLUTE COUNT. Never a percentage.
    width_permille: int

    def __post_init__(self) -> None:
        if self.count is not None and self.count < 0:
            raise BandInvariantViolated(f"{self.kind}: a count cannot be negative")
        if self.width_permille <= 0:
            raise BandInvariantViolated(
                f"{self.kind}: a segment with no width is a segment a reader cannot see, which is "
                "the same as one that is not there"
            )
        if "%" in self.label:
            raise BandInvariantViolated(
                f"{self.kind}: the label is {self.label!r}. Band labels are ABSOLUTE COUNTS. A "
                "percentage in a band carries no evidence of its own denominator, and the "
                "denominator is the whole argument of this report."
            )


def band_segments(sf: Any, residue: Any | None = None) -> tuple[Segment, ...]:
    """The band, from a `SettledFraction` and an optional residue.

    **The returned tuple always ends with `ALWAYS_LAST`, both hatched, both non-zero width.**
    """
    settled = sf.settled
    unsettled = sf.unsettled
    counts: list[tuple[SegmentKind, int | None, Pattern]] = [
        ("SETTLED_PASS", int(settled.passed), "SOLID"),
        ("SETTLED_FAIL", int(settled.failed), "SOLID"),
        ("INDETERMINATE", int(unsettled.indeterminate), "SOLID"),
        ("NOT_RUN", int(unsettled.notRun), "SOLID"),
        ("NO_PREDICATE", int(unsettled.noPredicate), "SOLID"),
        ("ERROR", int(unsettled.error), "SOLID"),
        # NOT SETTLEABLE FROM THE ARTIFACT. `None` until it is measured per template; it is not
        # zero, and rendering it as zero would claim every obligation is decidable from the filing.
        ("NOT_SETTLEABLE_FROM_ARTIFACT", _not_settleable(sf), "HATCH"),
        ("RESIDUE", _residue_count(residue), "HATCH"),
    ]

    total = int(sf.cellsTotal) or 1
    out: list[Segment] = []
    for kind, count, pattern in counts:
        if count is None:
            width = MIN_WIDTH_PERMILLE
        else:
            width = max(MIN_WIDTH_PERMILLE if pattern == "HATCH" else 1,
                        (count * 1000) // total)
        out.append(Segment(
            kind=kind, count=count, pattern=pattern,
            label=f"{count:,} {HUMAN[kind]}" if count is not None
            else f"not yet measured — {HUMAN[kind]}",
            width_permille=width,
        ))

    assert_never_fills(tuple(out))
    return tuple(out)


def _not_settleable(sf: Any) -> int | None:
    """`declaredGaps` if the run declares any, else `None` — **never 0**."""
    gaps = getattr(sf, "declaredGaps", ()) or ()
    return len(gaps) if gaps else None


def _residue_count(residue: Any | None) -> int | None:
    if residue is None:
        return None
    for attr in ("size", "count", "total"):
        v = getattr(residue, attr, None)
        if isinstance(v, int):
            return v
    return None


def assert_never_fills(segments: tuple[Segment, ...]) -> None:
    """The invariant, as a function, so the test and the builder assert the same thing."""
    if len(segments) < 2 or tuple(s.kind for s in segments[-2:]) != ALWAYS_LAST:
        raise BandInvariantViolated(
            f"the band ends with {tuple(s.kind for s in segments[-2:])} and must end with "
            f"{ALWAYS_LAST}. Those two are what make a full bar undrawable, and a bar that filled "
            "would claim that nothing is undecidable from the filing and that no constructed "
            "falsehood survives the check set. Neither can be true."
        )
    for s in segments[-2:]:
        if s.pattern != "HATCH":
            raise BandInvariantViolated(f"{s.kind} must be HATCH; it is not a settled quantity")
        if s.width_permille < MIN_WIDTH_PERMILLE:
            raise BandInvariantViolated(
                f"{s.kind} renders at {s.width_permille}‰, below the {MIN_WIDTH_PERMILLE}‰ floor. "
                "A segment too narrow to see is a segment that is not there."
            )

    settled_width = sum(s.width_permille for s in segments if s.pattern == "SOLID")
    total_width = sum(s.width_permille for s in segments)
    if settled_width >= total_width:
        raise BandInvariantViolated(
            f"the solid segments occupy {settled_width}‰ of {total_width}‰. The band must never "
            "fill: a reader who sees a full bar has been told the filing is completely covered, "
            "which no run can establish."
        )


def settled_fraction_text(sf: Any) -> str:
    """`1,898 of 3,747` — **both integers, never a bare rate** (`ci/no-bare-rate.sh`)."""
    return f"{int(sf.settled.total):,} of {int(sf.inScope):,}"


def subordinate_fraction(sf: Any) -> Decimal:
    """The decimal. **Strapline only — it may never appear in the hero** (`plan/07`).

    The hero carries two counts in one ink. A fraction there would be a single number a reader
    could take away, and the number they would take away is the flattering one.
    """
    return Decimal(sf.fraction)
