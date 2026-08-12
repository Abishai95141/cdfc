"""Helpers every formula-derived class needs. One implementation, so the classes agree."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from cdfc.schema.stable_keys import col_to_index, split_ref


def order_key(ctx: Any, sheet: str, ref: str, cls: str) -> tuple[int, int, int, str]:
    """The canonical emission order: `(sheet index, row, column, class)`. Nothing else.

    Ids are assigned from this, so two harvests of one template emit byte-identical files. A
    harvest keyed on set iteration order produces a different registry root every run.
    """
    try:
        col, row = split_ref(ref.replace("$", "").split(":")[0])
        return (ctx.sheet_index.get(sheet, 10**6), row, col_to_index(col), cls)
    except ValueError:
        return (ctx.sheet_index.get(sheet, 10**6), 10**6, 10**6, cls)


def cell_node(ctx: Any, sheet: str, ref: str) -> tuple[str, dict[str, set[str]]] | None:
    """`(path, key_cells)` for one cell, or None when the cell has no resolved stable key.

    A cell with no stable key is DROPPED and the drop is RECORDED: a key nobody induced is a key
    no predicate can name, and a predicate over an unnameable cell could never be re-opened.
    """
    from cdfc.predicates.harvest import cel_path

    ref = ref.replace("$", "")
    if (sheet, ref) not in ctx.key_of:
        ctx.skip("key_unresolved", sheet, ref, f"no stable key was induced for {sheet}!{ref}")
        return None
    path = f"filing.{cel_path(sheet, ref)}"
    return path, {
        f"{path}.v": {f"{sheet}!{ref}"},
        f"{path}.__cell__": {f"{sheet}!{ref}"},
    }


def parse_ref(text: str, default_sheet: str) -> tuple[str, str] | None:
    """`Sheet!C25` or `C25` -> `(sheet, ref)`. `$` is dropped; it is an authoring artefact."""
    t = text.strip().replace("$", "")
    if "!" in t:
        sheet, ref = t.rsplit("!", 1)
        return sheet.strip().strip("'"), ref.strip()
    return (default_sheet, t) if t else None


def iter_formulas(ctx: Any) -> Iterator[tuple[str, str, str]]:
    """`(sheet, ref, body)` for every formula cell, with SHARED DEPENDENTS MATERIALISED.

    The v0 research harvest read `<f>` text directly and so saw nothing for a shared dependent —
    `<f t="shared" si="0"/>` carries no text. On FME that is **211 of 505 formula cells, 42%**, and
    every relation they encode was invisible to it.

    Materialisation happens HERE rather than in the reader: `FormulaRecord.materialised` is a field
    the reader leaves `None`, because shifting a master's expression to a dependent's cell is an
    interpretation, and the reader's job is to report bytes. A dependent whose master cannot be
    seen is DECLARED as a skip, never dropped — evaluating the master's text UNSHIFTED would return
    a well-formed relation about the wrong row, which is the defect this project is about.
    """
    from cdfc.calc.shift import materialise

    for sheet, records in ctx.formulas_by_sheet.items():
        masters = {f.si: f for f in records if f.encoding == "SHARED_MASTER"}
        for f in records:
            if f.text:
                body = f.text.strip()
            elif f.encoding == "SHARED_DEPENDENT":
                m = masters.get(f.si)
                if m is None or not m.text:
                    ctx.skip(
                        "other_formula", sheet, f.ref,
                        f"shared dependent si={f.si} whose master is not visible on this sheet; "
                        "its expression cannot be shifted, and using the master's text unshifted "
                        "would state a relation about the wrong row",
                    )
                    continue
                body = materialise(m.ref, m.text, f.ref).strip()
            else:
                body = (f.materialised or "").strip()
            if body:
                yield sheet, f.ref, body
