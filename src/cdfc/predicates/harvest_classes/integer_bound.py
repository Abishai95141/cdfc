"""A `whole` data validation — an integrality bound the pinned blank declares."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

NAME = "integer_bound"

# As numeric_bound, plus F06 (round to integer), because an integrality bound is exactly what the
# rounding class perturbs.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F01", "F03", "F06")


def emit(ctx: Any) -> Iterator[tuple[tuple, Any]]:
    from cdfc.predicates.harvest_classes._bounds import emit_bounds

    yield from emit_bounds(
        ctx, dv_type="whole", name=NAME, claims=CLAIMS_FAULT_CLASSES,
        reason="The value must be a whole number inside that range; counts get zero tolerance.",
        dtype="COUNT",
    )
