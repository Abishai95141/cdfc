"""`=SUM(range)` — the total and its summands, with an INTEGER tolerance."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.facts.units import HALF_ULP
from cdfc.predicates.envelope import Tolerance
from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, iter_formulas, order_key, parse_ref

NAME = "sum_identity"

# A row omission or duplication moves the sum (F07, F08); a transposition, scale slip, sign flip,
# off-by-one or zero-out in any summand does too.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F01", "F02", "F03", "F04", "F05", "F07", "F08")


def emit(ctx: Any) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import SUM_CALL, expand, single_call

    for sheet, ref, body in iter_formulas(ctx):
        if not SUM_CALL.match(body):
            continue
        raw_args = single_call(body, "SUM")
        if raw_args is None:
            ctx.skip("function_outside_vocabulary", sheet, ref,
                     f"the body is not a single SUM call: {body[:60]}")
            continue
        inner = raw_args.strip()
        if "," in inner or "(" in inner:
            ctx.skip("function_outside_vocabulary", sheet, ref,
                     f"SUM over more than one range is outside the class set: {body[:60]}")
            continue
        src = parse_ref(inner, sheet)
        if src is None or ":" not in inner:
            continue
        src_sheet, rng = src
        if not ctx.sheet_exists(src_sheet):
            ctx.skip("other_formula", sheet, ref, f"SUM names sheet {src_sheet!r}, which is absent")
            continue
        cells = expand(rng)
        if not cells:
            ctx.skip("other_formula", sheet, ref, f"unparseable SUM range {rng!r}")
            continue
        total = cell_node(ctx, sheet, ref)
        if total is None:
            continue
        parts = [cell_node(ctx, src_sheet, c) for c in cells]
        parts = [p for p in parts if p is not None]
        if not parts:
            ctx.skip("key_unresolved", sheet, ref, f"no summand of {rng} has a stable key")
            continue
        # DECLARE WHAT IS READ. The witness names the total's cell; the summands are read as
        # values only, so their anchors are not declared.
        keys = dict(total[1])
        for p in parts:
            keys.update({k: v for k, v in p[1].items() if k.endswith(".v")})
        summands = " + ".join(f"{p[0]}.v" for p in parts)
        n = len(parts)
        yield order_key(ctx, sheet, ref, NAME), Draft(
            harvest_class=NAME,
            obligation_id=obligation_id("F", sheet, ref),
            construct_kind="formula",
            construct_parts=(body,),
            construct_at=(sheet, ref),
            clause_absent_reason="derived_from_template_formula",
            claims_fault_classes=CLAIMS_FAULT_CLASSES,
            schema_keys=tuple(sorted(keys)),
            applicable=f"has({total[0]}.v)",
            # tau(n) = 5n units, an INTEGER count. A relative tolerance on a total of zero admits
            # everything, and totals of zero are the modal case in this corpus.
            expr=(
                f"{total[0]}.v - ({summands}) <= {HALF_ULP * n} && "
                f"({summands}) - {total[0]}.v <= {HALF_ULP * n}"
            ),
            witness=f"[{total[0]}.__cell__]",
            reason_if_inapplicable=f"the total cell {sheet}!{ref} is absent from this filing",
            rationale=(
                f"The pinned blank declares {sheet}!{ref} as `={body}`. The total and its {n} "
                f"summands are one arithmetic identity, admitted within tau({n}) = {HALF_ULP * n} "
                "MILLI_USD_MILLION units — half an ulp per summand, as an integer count."
            ),
            key_cells=keys,
            tolerance=Tolerance(tau_units_per_summand=HALF_ULP),
        )
