"""A `custom` data validation — the formula IS the condition, and it is recorded, not executed."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, order_key

NAME = "conditional_required"

# It detects the blank-and-zero pair and nothing else.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F05",)


def emit(ctx: Any) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import expand, range_path

    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if dv.type != "custom":
                continue
            if not dv.sqref.split():
                ctx.skip("dv_no_type", sheet, "<no sqref>",
                         "a data validation that names no cells constrains nothing")
                continue
            cells = [c for part in dv.sqref.split() for c in expand(part.replace("$", ""))]
            nodes = [n for n in (cell_node(ctx, sheet, c) for c in cells) if n is not None]
            if not nodes:
                ctx.skip("key_unresolved", sheet, dv.sqref, f"no cell of {dv.sqref} has a stable key")
                continue
            base = f"filing.{range_path(sheet, dv.sqref)}"
            keys: dict[str, set[str]] = {
                f"{base}.cells": {f"{sheet}!{c}" for c in cells},
                f"{base}.cells[*].v": {f"{sheet}!{c}" for c in cells},
                f"{base}.cells[*].__cell__": {f"{sheet}!{c}" for c in cells},
            }
            first = dv.sqref.split()[0].split(":")[0].replace("$", "")
            yield order_key(ctx, sheet, first, NAME), Draft(
                harvest_class=NAME,
                obligation_id=obligation_id(sheet, dv.sqref),
                clause_absent_reason="derived_from_data_validation",
                claims_fault_classes=CLAIMS_FAULT_CLASSES,
                schema_keys=tuple(sorted(keys)),
                applicable=f"has({base}.cells)",
                # The custom formula is NOT translated. What is checked is the weaker, honest
                # thing the class can express: a cell the template marks as conditionally required
                # is present. Translating an arbitrary Excel condition into CEL would be a
                # re-interpretation nobody qualified, and it would be invisible in the envelope.
                expr=f'{base}.cells.exists(c, c.v != "")',
                witness=f'{base}.cells.filter(c, c.v == "").map(c, c.__cell__)',
                reason_if_inapplicable=f"the validated range {sheet}!{dv.sqref} is absent from this filing",
                rationale=(
                    f"The pinned blank attaches a custom validation to {sheet}!{dv.sqref}: "
                    f"`{(dv.formula1 or '')[:80]}`. This predicate does NOT translate that "
                    "condition — it checks the weaker thing the class can express honestly, that "
                    "the conditionally-required range is not wholly blank. The untranslated "
                    "condition is why this class claims only F05."
                ),
                key_cells=keys,
            )
