"""The eight RUN-LEVEL invalid causes.

These are NOT the item-level 8x30 vocabulary. A container guard trip, a reader
disagreement on sheet structure, an unbound template and a closure violation are not
properties of any cell — forcing them into a per-cell reason code was a category error
the plan's audit caught (§V.7.3). Run-level causes therefore have their own closed
vocabulary, and the item-level count stays pinned.

P1 owns CONTAINER_GUARD_TRIPPED and READER_STRUCTURAL_DISAGREEMENT. P5 owns the rest of
the verdict model; the enum is complete here so nothing invents a ninth cause later.
"""

from __future__ import annotations

from enum import StrEnum


class InvalidCause(StrEnum):
    CONTAINER_GUARD_TRIPPED = "invalid.container_guard_tripped"
    READER_STRUCTURAL_DISAGREEMENT = "invalid.reader_structural_disagreement"
    TEMPLATE_UNBOUND = "invalid.template_unbound"
    CELLS_BOUND_ZERO = "invalid.cells_bound_zero"
    PREDICATE_RAISED = "invalid.predicate_raised"
    CANARY_SILENT = "invalid.canary_silent"
    CLOSURE_VIOLATED = "invalid.closure_violated"
    DENOMINATOR_DISAGREEMENT = "invalid.denominator_disagreement"
