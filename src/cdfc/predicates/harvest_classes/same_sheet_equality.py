"""A cell whose formula is a bare reference to another cell on the SAME sheet."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, iter_formulas, order_key

NAME = "same_sheet_equality"

# As cross_sheet_equality minus the cross-sheet carry: no F13, because there is no carry to
# desynchronise when both ends are on one sheet.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F01", "F02", "F03", "F04", "F05")


def emit(ctx: Any) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import _CELL

    for sheet, ref, body in iter_formulas(ctx):
        plain = body.replace("$", "")
        if not _CELL.match(plain) or plain == ref.replace("$", ""):
            continue
        tgt = cell_node(ctx, sheet, ref)
        src = cell_node(ctx, sheet, plain)
        if tgt is None or src is None:
            continue
        keys = {**tgt[1], **src[1]}
        yield order_key(ctx, sheet, ref, NAME), Draft(
            harvest_class=NAME,
            obligation_id=obligation_id(sheet, ref),
            clause_absent_reason="derived_from_template_formula",
            claims_fault_classes=CLAIMS_FAULT_CLASSES,
            schema_keys=tuple(sorted(keys)),
            applicable=f"has({tgt[0]}.v) && has({src[0]}.v)",
            expr=f"{tgt[0]}.v == {src[0]}.v",
            witness=f"[{tgt[0]}.__cell__, {src[0]}.__cell__]",
            reason_if_inapplicable=f"one of {sheet}!{ref} and {sheet}!{plain} is absent",
            rationale=(
                f"The pinned blank declares {sheet}!{ref} as `={body}`. The two cells are one "
                "value under two labels."
            ),
            key_cells=keys,
        )
