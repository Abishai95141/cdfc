"""P3-B2 — units and tolerance. Money is an integer, once, here.

**`MILLI_USD_MILLION`: an `int64` count of 10⁻³ USD Million. One unit = USD 1,000.**
`12.34` USD Million becomes `12340`. The name is deliberately explicit because the
specification carried two definitions differing by 10³ — "integer micro-units" against
this one — and every tolerance in the design is expressed in units, so picking wrong puts
every arithmetic predicate's tolerance out by a factor of a thousand.

**Tolerance is `τ(n) = 5n` units for an n-summand sum**: half an ulp per summand, since a
value rounded to the unit can be off by half a unit in either direction and n of them
accumulate. It is an INTEGER count, not a percentage — a relative tolerance on a total of
zero admits everything, and totals of zero are the modal case in this corpus.

Scaling happens exactly once, at the fact-model boundary. A second scaling is silent and
produces a well-formed number three orders of magnitude wrong.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from enum import StrEnum
from typing import Final

PRECISION: Final[int] = 34
UNITS_PER_USD_MILLION: Final[int] = 1_000
HALF_ULP: Final[int] = 5


class Unit(StrEnum):
    MILLI_USD_MILLION = "MILLI_USD_MILLION"
    COUNT = "COUNT"
    DATE = "DATE"
    TEXT = "TEXT"
    ENUM = "ENUM"


class UnitError(ValueError):
    """A value that cannot be represented in its declared unit. Never coerced silently."""


def to_units(value: Decimal | int | str | None) -> int | None:
    """USD Million → an int64 count of 10⁻³ USD Million. The ONLY scaling site."""
    if value is None or value == "":
        return None
    try:
        d = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as e:
        raise UnitError(f"{value!r} is not a decimal amount") from e
    with localcontext() as ctx:
        ctx.prec = PRECISION
        scaled = d * UNITS_PER_USD_MILLION
    if scaled != scaled.to_integral_value():
        # More precision than the unit can hold. Rounding here would be a silent loss at
        # the boundary where money enters the system, so it is refused instead.
        raise UnitError(
            f"{value!r} carries more precision than MILLI_USD_MILLION can represent "
            f"(1 unit = USD 1,000); scaled to {scaled}"
        )
    n = int(scaled)
    if not (-(2**63) <= n < 2**63):
        raise UnitError(f"{value!r} overflows int64 in MILLI_USD_MILLION")
    return n


def from_units(units: int | None) -> Decimal | None:
    """Back to USD Million, for rendering only. Never for arithmetic."""
    if units is None:
        return None
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return Decimal(units) / UNITS_PER_USD_MILLION


def tau(n_summands: int) -> int:
    """τ(n) = 5n units. An INTEGER count, never a percentage."""
    if n_summands < 0:
        raise UnitError("a sum cannot have a negative number of summands")
    return HALF_ULP * n_summands


def within_tolerance(a: int, b: int, n_summands: int) -> bool:
    return abs(a - b) <= tau(n_summands)
