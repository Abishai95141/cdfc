"""A `date` data validation. Dates are compared as ISO strings; CEL binds no clock."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

NAME = "date_bound"

# Nothing else in the taxonomy moves a date.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F09",)


def emit(ctx: Any) -> Iterator[tuple[tuple, Any]]:
    from cdfc.predicates.harvest_classes._bounds import emit_bounds

    yield from emit_bounds(
        ctx, dv_type="date", name=NAME, claims=CLAIMS_FAULT_CLASSES,
        reason=(
            "The bound is an Excel serial day number in the pinned blank, and it is compared as "
            "an integer: CEL binds no clock, so no date arithmetic happens at run time."
        ),
        dtype="DATE",
    )
