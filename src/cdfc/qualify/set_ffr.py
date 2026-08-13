"""P8-B3 — the SET-level false-failure rate. **At least one member fires, never the mean.**

**THE DEFINITION, stated because an implementation as a MEAN was the injected break.** `FFR(S)` is
the fraction of clean filings on which **AT LEAST ONE** member of `S` fires. That is what makes the
rate monotone non-decreasing under union and what satisfies

    max(FFR(S), FFR(f))  <=  FFR(S ∪ {f})  <=  FFR(S) + FFR(f)

A mean violates the lower bound the moment two predicates fire on disjoint filings: each has
`FFR = 1/n`, the mean is `1/n`, and the truth is `2/n`. **In two of SPADE's nine pipelines, sets
whose every member individually met the constraint reached composite FFR of 88% and 53%**  <!-- rate-ok: published figures, quoted -->
(rate-ok: published figures, quoted) — the registry drifting to flag-everything one admission at a
time, which is what this module exists to make visible.

`marginal_ffr` is what a candidate ADDS to the set that already exists, and `conditioned_on[]` is
that set — **a marginal number with no record of what it was marginal to is not a number.**
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction


class EmptyCorpusError(ZeroDivisionError):
    """A set FFR over no filings. Not a small rate; not a rate."""


@dataclass(frozen=True, slots=True)
class FireMatrix:
    """`predicate_id -> the filings it fired on`. Filings are identified, never counted, so a
    union is a set operation rather than an arithmetic guess."""

    filings: tuple[str, ...]
    fires: Mapping[str, frozenset[str]]

    def __post_init__(self) -> None:
        unknown = {f for v in self.fires.values() for f in v} - set(self.filings)
        if unknown:
            raise ValueError(
                f"the matrix records fires on {len(unknown)} filing(s) absent from its own "
                f"denominator, e.g. {sorted(unknown)[:3]}. A numerator over a filing nobody "
                "counted is the shared-denominator error."
            )

    def of(self, pid: str) -> frozenset[str]:
        return self.fires.get(pid, frozenset())

    @property
    def n(self) -> int:
        return len(self.filings)


def ffr(pid: str, fires: FireMatrix) -> Fraction:
    """One predicate's FFR. `Fraction`, so the two integers survive into every render."""
    if fires.n == 0:
        raise EmptyCorpusError("a false-failure rate over no filings is not a rate")
    return Fraction(len(fires.of(pid)), fires.n)


def set_ffr(members: Sequence[str], fires: FireMatrix) -> Fraction:
    """The fraction of clean filings on which AT LEAST ONE member fires."""
    if fires.n == 0:
        raise EmptyCorpusError("a set false-failure rate over no filings is not a rate")
    union: set[str] = set()
    for m in members:
        union |= fires.of(m)
    return Fraction(len(union), fires.n)


def marginal_ffr(
    existing: Sequence[str], f: str, fires: FireMatrix
) -> tuple[Fraction, tuple[str, ...]]:
    """`(FFR(S ∪ {f}) − FFR(S), sorted(S))` — the number AND what it was marginal to."""
    s = sorted(set(existing))
    before = set_ffr(s, fires)
    after = set_ffr([*s, f], fires)
    return after - before, tuple(s)


def render(value: Fraction) -> str:
    """`k/n`, as two integers. Never a rounded float — `ci/no-bare-rate.sh` scans for the other."""
    return f"{value.numerator}/{value.denominator}"
