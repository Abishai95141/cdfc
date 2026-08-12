"""A cell whose formula is a bare reference to another SHEET. The carry, and its identity."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, iter_formulas, order_key, parse_ref

NAME = "cross_sheet_equality"

# 181 of these on FME. F13 (carry desync) is the class they exist for, and any single-sided
# perturbation of either end breaks the equality: F01 sign flip, F02 scale, F03 off-by-one,
# F04 transposition, F05 zero-out.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F01", "F02", "F03", "F04", "F05", "F13")


def emit(ctx: Any) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import PURE_CARRY

    for sheet, ref, body in iter_formulas(ctx):
        if not PURE_CARRY.match(body):
            continue
        src = parse_ref(body, sheet)
        if src is None or src[0] == sheet:
            continue
        if not ctx.sheet_exists(src[0]):
            ctx.skip("other_formula", sheet, ref, f"carry names sheet {src[0]!r}, which is absent")
            continue
        tgt_node, tgt_keys = cell_node(ctx, sheet, ref) or (None, None)
        src_node, src_keys = cell_node(ctx, src[0], src[1]) or (None, None)
        if tgt_node is None or src_node is None:
            continue
        keys = {**tgt_keys, **src_keys}  # type: ignore[dict-item]
        yield order_key(ctx, sheet, ref, NAME), Draft(
            harvest_class=NAME,
            obligation_id=obligation_id(sheet, ref),
            clause_absent_reason="derived_from_template_formula",
            claims_fault_classes=CLAIMS_FAULT_CLASSES,
            schema_keys=tuple(sorted(keys)),
            applicable=f"has({tgt_node}.v) && has({src_node}.v)",
            expr=f"{tgt_node}.v == {src_node}.v",
            witness=f"[{tgt_node}.__cell__, {src_node}.__cell__]",
            reason_if_inapplicable=(
                f"one end of the carry is absent from this filing: {sheet}!{ref} or "
                f"{src[0]}!{src[1]}"
            ),
            rationale=(
                f"The pinned blank declares {sheet}!{ref} as `={body}` — the two cells are one "
                "number carried across sheets. A filing where they differ has been edited on one "
                "side, and the formula that would have kept them equal is gone."
            ),
            key_cells=keys,
        )
