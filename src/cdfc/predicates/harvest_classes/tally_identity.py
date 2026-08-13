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

        # **A WILDCARD CRITERION IS NOT A STRING EQUALITY, AND P8's FALSE-FAILURE RATE IS WHAT
        # FOUND THAT.** In Excel and in LibreOffice, `*` and `?` in a COUNTIF criterion are
        # wildcards: `"*Restricted*"` counts every cell CONTAINING "Restricted". This class emits
        # `c.v == "*Restricted*"`, which counts cells whose text is literally `*Restricted*` — a
        # different relation, and always zero on a real filing.
        #
        # It survived P4, G0, G1, G2 and G3, and it survived P5's clean filing because that filing
        # put ONE value in every cell and the value happened not to contain "Restricted". A corpus
        # with varied inputs and an INDEPENDENT oracle fired it on 18 of 40 clean filings — a
        # predicate that would have told a correct filer their return was wrong. That is what an
        # FFR is for, and it is the first one this project has measured.
        #
        # The fix is a TYPED SKIP rather than wildcard semantics: this step cannot fail, only
        # under-produce, and an undeclared suppression is a coverage lie. Implementing Excel's
        # wildcard matching is real work with its own escaping rules (`~*` is a literal asterisk)
        # and it belongs to whoever needs the class, not to a repair.
        if "*" in crit or "?" in crit:
            ctx.skip("function_outside_vocabulary", sheet, ref,
                     f"COUNTIF criterion {criterion.strip()[:48]!r} contains an Excel WILDCARD; "
                     "translating it as a string equality states a relation the template does not "
                     "encode (found by P8's false-failure rate at 18 fires on 40 clean filings)")
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
            obligation_id=obligation_id("F", sheet, ref),
            construct_kind="formula",
            construct_parts=(body,),
            construct_at=(sheet, ref),
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
