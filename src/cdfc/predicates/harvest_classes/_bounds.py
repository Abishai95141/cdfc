"""The three bound classes differ only in their claimed fault set and their operator vocabulary."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.schema.anchor import Anchor
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
    if f != int(f):
        return None
    # A BOUND OUTSIDE int64 IS NOT A BOUND THIS SYSTEM CAN EXPRESS. One `decimal` validation on
    # FME declares 9.99999999999999E+21, which is ~1,000x the int64 ceiling; emitting it as a CEL
    # integer literal made the runtime exhaust memory on that one predicate and the run was killed.
    # Money is an int64 count of 10^-3 USD Million, so a threshold this large is outside the
    # model — and a predicate whose threshold cannot be represented is a typed skip, not a
    # predicate with an approximated threshold.
    if not (-(2**63) <= int(f) < 2**63):
        return None
    return str(int(f))


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
                         f"{dv_type} validation whose bound {(dv.formula1 or '')[:40]!r} is not an "
                         "int64 literal in the pinned blank: either the filing supplies the "
                         "threshold (a threshold the filer sets), or it is outside the range "
                         "MILLI_USD_MILLION can represent")
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
                f"{base}.cells": {Anchor.cell(sheet, c).render() for c in cells},
                f"{base}.cells[*].v": {Anchor.cell(sheet, c).render() for c in cells},
                f"{base}.cells[*].__cell__": {Anchor.cell(sheet, c).render() for c in cells},
            }
            # NO BLANK ARM. A bound is over NUMBERS, and `c.v == ""` compares an integer to a
            # string — which CEL treats as a type error, not as false, so five predicates on the
            # clean filing produced ERROR(error.predicate_raised) and invalidated the run.
            #
            # The blank arm was also unnecessary: a blank NUMERIC cell is ABSENT from the fact
            # model (F05 — blank is not zero), so it never reaches `.all()` at all. Removing it
            # makes the inferred type unambiguous, which moves a text value in a numeric column
            # from ERROR (our apparatus failed) to NOT_RUN (the source could not be read) at
            # pre-flight — the honest state, and one with a different remedy.
            if hi is not None and op is None:
                test = f"c.v >= {lo} && c.v <= {hi}"
                bad = f"c.v < {lo} || c.v > {hi}"
                shown = f"between {lo} and {hi}"
            else:
                o = op or ">="
                inverse = {">": "<=", ">=": "<", "<": ">=", "<=": ">", "==": "!=", "!=": "=="}[o]
                test = f"c.v {o} {lo}"
                bad = f"c.v {inverse} {lo}"
                shown = f"{o} {lo}"
            first = dv.sqref.split()[0].split(":")[0].replace("$", "")
            yield order_key(ctx, sheet, first, name), Draft(
                harvest_class=name,
                obligation_id=obligation_id("V", sheet, dv.sqref),
                construct_kind="validation",
                construct_parts=(dv.type, dv.operator, dv.formula1 or ""),
                construct_at=(sheet, dv.sqref),
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
