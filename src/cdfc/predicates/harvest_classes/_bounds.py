"""The three bound classes differ only in their claimed fault set and their operator vocabulary."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, order_key

_OPS = {
    "greaterThan": ">", "greaterThanOrEqual": ">=",
    "lessThan": "<", "lessThanOrEqual": "<=",
    "equal": "==", "notEqual": "!=",
}


def _literal(text: str | None) -> str | None:
    """A bound is admitted only when it is a LITERAL in the pinned blank.

    A bound that is itself a formula depends on the filing's own values, and a check whose
    threshold the filer supplies is a check the filer sets. Those become skips, not predicates.
    """
    t = (text or "").strip().lstrip("=")
    if not t:
        return None
    try:
        f = float(t)
    except ValueError:
        return None
    return str(int(f)) if f == int(f) else None


def emit_bounds(
    ctx: Any, *, dv_type: str, name: str, claims: tuple[str, ...], reason: str, dtype: str
) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import expand, range_path

    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if dv.type != dv_type:
                continue
            op = _OPS.get(dv.operator or "")
            lo = _literal(dv.formula1)
            hi = _literal(dv.formula2)
            if lo is None:
                ctx.skip("dv_no_type", sheet, dv.sqref,
                         f"{dv_type} validation whose bound {(dv.formula1 or '')[:40]!r} is not a "
                         "literal in the pinned blank; a threshold the filing supplies is a "
                         "threshold the filer sets")
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
            if hi is not None and op is None:
                test = f'c.v == "" || (c.v >= {lo} && c.v <= {hi})'
                bad = f'c.v != "" && (c.v < {lo} || c.v > {hi})'
                shown = f"between {lo} and {hi}"
            else:
                o = op or ">="
                inverse = {">": "<=", ">=": "<", "<": ">=", "<=": ">", "==": "!=", "!=": "=="}[o]
                test = f'c.v == "" || c.v {o} {lo}'
                bad = f'c.v != "" && c.v {inverse} {lo}'
                shown = f"{o} {lo}"
            first = dv.sqref.split()[0].split(":")[0].replace("$", "")
            yield order_key(ctx, sheet, first, name), Draft(
                harvest_class=name,
                obligation_id=obligation_id(sheet, dv.sqref),
                clause_absent_reason="derived_from_data_validation",
                claims_fault_classes=claims,
                schema_keys=tuple(sorted(keys)),
                applicable=f"has({base}.cells)",
                expr=f"{base}.cells.all(c, {test})",
                witness=f"{base}.cells.filter(c, {bad}).map(c, c.__cell__)",
                reason_if_inapplicable=f"the validated range {sheet}!{dv.sqref} is absent from this filing",
                rationale=(
                    f"The pinned blank attaches a {dv_type} validation to {sheet}!{dv.sqref} "
                    f"requiring {shown}. {reason} The dtype is {dtype}."
                ),
                key_cells=keys,
            )
