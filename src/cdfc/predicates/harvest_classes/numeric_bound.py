"""A `decimal` data validation — a numeric range the pinned blank declares."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.predicates.harvest_classes._shared import order_key  # noqa: F401  (re-exported shape)

NAME = "numeric_bound"

# A sign flip crosses a `>= 0` bound; an off-by-one crosses a boundary.
# NOT F02: a x10 on a positive value stays above a `>= 0` bound, so the scale class is one this
# predicate is structurally blind to and claiming it would widen the denominator dishonestly.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F01", "F03")


def emit(ctx: Any) -> Iterator[tuple[tuple, Any]]:
    from cdfc.predicates.harvest_classes._bounds import emit_bounds

    yield from emit_bounds(
        ctx, dv_type="decimal", name=NAME, claims=CLAIMS_FAULT_CLASSES,
        reason="A value outside it is outside the range the regulator's own artifact admits.",
        dtype="MILLI_USD_MILLION",
    )
