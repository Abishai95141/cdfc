"""A list-type data validation — the value is drawn from the TEMPLATE's own vocabulary."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.schema.anchor import Anchor
from cdfc.predicates.harvest_classes import Draft, obligation_id
from cdfc.predicates.harvest_classes._shared import cell_node, order_key

NAME = "membership"

# F12 (vocabulary drift, including the homoglyph and whitespace forms) and NOTHING ELSE.
#
# NOT F10. A LEGAL enum substituted for another legal enum is invisible to a membership test BY
# CONSTRUCTION — the substituted value is in the vocabulary, so the test passes. Claiming F10 here
# would be the exact lie D-P4-06 exists to prevent, and it would make F10's designed miss
# invisible in the residue.
CLAIMS_FAULT_CLASSES: tuple[str, ...] = ("F12",)


def emit(ctx: Any) -> Iterator[tuple[tuple, Draft]]:
    from cdfc.predicates.harvest import cel_segment, expand, range_path, resolve_vocabulary

    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if dv.type != "list":
                continue
            if not dv.sqref.split():
                ctx.skip("dv_no_type", sheet, "<no sqref>",
                         "a data validation that names no cells constrains nothing")
                continue
            first = dv.sqref.split()[0].split(":")[0].replace("$", "")
            vocab, how = resolve_vocabulary(ctx, sheet, dv.formula1)
            if not vocab:
                ctx.skip("list_unresolved", sheet, dv.sqref,
                         f"formula1 {(dv.formula1 or '')[:48]!r} did not resolve to a vocabulary: {how}")
                continue
            cells = [c for part in dv.sqref.split() for c in expand(part.replace("$", ""))]
            nodes = [n for n in (cell_node(ctx, sheet, c) for c in cells) if n is not None]
            if not nodes:
                ctx.skip("key_unresolved", sheet, dv.sqref,
                         f"no cell of {dv.sqref} has a stable key")
                continue
            base = f"filing.{range_path(sheet, dv.sqref)}"
            vocab_key = f"template.vocab.{cel_segment(sheet)}_{cel_segment(first)}"
            keys: dict[str, set[str]] = {
                f"{base}.cells": {Anchor.cell(sheet, c).render() for c in cells},
                f"{base}.cells[*].v": {Anchor.cell(sheet, c).render() for c in cells},
                f"{base}.cells[*].__cell__": {Anchor.cell(sheet, c).render() for c in cells},
                vocab_key: set(),
            }
            yield order_key(ctx, sheet, first, NAME), Draft(
                harvest_class=NAME,
                obligation_id=obligation_id("V", sheet, dv.sqref),
                construct_kind="validation",
                construct_parts=(dv.type, dv.operator, dv.formula1 or ""),
                construct_at=(sheet, dv.sqref),
                clause_absent_reason="derived_from_data_validation",
                claims_fault_classes=CLAIMS_FAULT_CLASSES,
                schema_keys=tuple(sorted(keys)),
                applicable=f"has({base}.cells)",
                # A blank is admitted: the validation constrains what MAY be entered, not that
                # something must be. `conditional_required` is the class for that, and conflating
                # them would make an empty column pass a requirement nobody wrote.
                expr=f'{base}.cells.all(c, c.v == "" || c.v in {vocab_key})',
                witness=f'{base}.cells.filter(c, c.v != "" && !(c.v in {vocab_key})).map(c, c.__cell__)',
                reason_if_inapplicable=f"the validated range {sheet}!{dv.sqref} is absent from this filing",
                rationale=(
                    f"The pinned blank attaches a list validation to {sheet}!{dv.sqref} whose "
                    f"{len(vocab)} members come from the blank itself ({how}). A value outside it "
                    "is outside the vocabulary the regulator's own artifact declares. It says "
                    "nothing about whether the value is correct."
                ),
                key_cells=keys,
            )
