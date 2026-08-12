"""`=COUNTIF(range, criterion)` — a count against a table body."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, iter_formulas, order_key, parse_ref

NAME = "tally_identity"

# It sees rows appearing and disappearing (F07, F08) and the blank-and-zero pair (F05), and
# NOTHING about value magnitude. Claiming a scale or sign class here would be claiming a class the
# predicate is structurally blind to.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F05", "F07", "F08")


def emit(ctx: Any) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import COUNT_CALL, expand, single_call

    for sheet, ref, body in iter_formulas(ctx):
        if not COUNT_CALL.match(body):
            continue
        args = single_call(body, "COUNTIF") or single_call(body, "COUNTIFS")
        if args is None:
            ctx.skip("function_outside_vocabulary", sheet, ref,
                     f"the body is not a single COUNTIF call: {body[:60]}")
            continue
        rng_text, _, criterion = args.partition(",")
        src = parse_ref(rng_text, sheet)
        if src is None or ":" not in rng_text:
            ctx.skip("function_outside_vocabulary", sheet, ref, f"COUNTIF over {rng_text[:40]!r}")
            continue
        src_sheet, rng = src
        crit = criterion.strip().strip('"')
        if not crit or not ctx.sheet_exists(src_sheet):
            ctx.skip("function_outside_vocabulary", sheet, ref,
                     f"COUNTIF criterion {criterion[:40]!r} is not a literal, or its sheet is absent")
            continue
        cells = [c for c in expand(rng)]
        total = cell_node(ctx, sheet, ref)
        parts = [cell_node(ctx, src_sheet, c) for c in cells]
        parts = [p for p in parts if p is not None]
        if total is None or not parts:
            continue
        # DECLARE WHAT IS READ, and nothing else. The witness names the total's cell only, so
        # declaring every summand's `__cell__` would be a declared-but-unread key — and a declared
        # footprint wider than the read one inflates the settled numerator.
        keys = dict(total[1])
        for p in parts:
            keys.update({k: v for k, v in p[1].items() if k.endswith(".v")})
        terms = " + ".join(f"({p[0]}.v == \"{crit}\" ? 1 : 0)" for p in parts)
        yield order_key(ctx, sheet, ref, NAME), Draft(
            harvest_class=NAME,
            obligation_id=obligation_id(sheet, ref),
            clause_absent_reason="derived_from_template_formula",
            claims_fault_classes=CLAIMS_FAULT_CLASSES,
            schema_keys=tuple(sorted(keys)),
            applicable=f"has({total[0]}.v)",
            # A COUNT gets ZERO tolerance. A person is not a rounded quantity.
            expr=f"{total[0]}.v == {terms}",
            witness=f"[{total[0]}.__cell__]",
            reason_if_inapplicable=f"the tally cell {sheet}!{ref} is absent from this filing",
            rationale=(
                f"The pinned blank declares {sheet}!{ref} as `={body}`. The tally counts rows "
                f"matching {crit!r}; it is exact, with no tolerance, because a count of things is "
                "not a rounded quantity."
            ),
            key_cells=keys,
            tolerance=None,
        )
