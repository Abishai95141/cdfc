"""P6 — "killed" means a predicate returned `FAIL` under the P5 verdict model.

The fact tree is built ONCE from the clean filing and PATCHED per mutant: the edited cells take
the mutant's literal and every cell in the edit's transitive downstream cone takes the mutant's
recalculated value. A cell outside the cone cannot change, so the patch is exact rather than an
approximation — and re-parsing the workbook per mutant would cost hours.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from cdfc.evaluate.celrt import CelRuntime
from cdfc.evaluate.runner import evaluate_one
from cdfc.facts.build import _coerce, filing_tree, template_tree
from cdfc.facts.view import FactSet
from cdfc.measure.p5_run import FME, INDEPENDENT
from cdfc.predicates.host_fns import default_registry
from cdfc.verdict import ItemState


def killer(predicates: Sequence[Any], schema: Any, *, restrict: bool = True) -> Any:
    """`restrict` evaluates only the predicates whose BOUND CELLS intersect what changed.

    Exact, not an approximation: a predicate binds exactly the cells its declared keys resolve to —
    P4-B2 machine-checked that in both directions — so one binding no changed cell reads the same
    facts it read on the clean filing and returns the same verdict. The clean filing has zero
    FAILs, so an unchanged verdict is not a kill.

    `tests/differential/test_diff__restricted_kill_equals_full.py` runs both on a sample and
    asserts they agree, because "exact by argument" is how a wrong optimisation gets shipped.
    """
    from cdfc.predicates.harvest import _load_context

    ctx = _load_context(FME)
    base_tree = filing_tree(INDEPENDENT, ctx=ctx)
    template = template_tree(FME, ctx=ctx)
    rt = CelRuntime(profile_version="P6", host_fns=default_registry())
    from cdfc.predicates.harvest import cel_path, range_path

    # A cell -> range-node index, built ONCE. The first version scanned every data validation
    # and expanded every sqref for EVERY patched cell — and a mutant patches its whole downstream
    # cone, so the cost was quadratic and the campaign made no visible progress in two minutes.
    from cdfc.predicates.harvest import expand

    range_of: dict[tuple[str, str], list[str]] = {}
    for _sheet, _dvs in ctx.validations_by_sheet.items():
        for _dv in _dvs:
            if not _dv.sqref.split():
                continue
            _path = range_path(_sheet, _dv.sqref)
            for _part in _dv.sqref.split():
                for _ref in expand(_part.replace("$", "")):
                    range_of.setdefault((_sheet, _ref), []).append(_path)

    def _node(tree: dict, dotted: str) -> Any:
        node: Any = tree
        for seg in dotted.split("."):
            if not isinstance(node, dict):
                return None
            node = node.setdefault(seg, {})
        return node

    def _patch(tree: dict, sheet: str, ref: str, raw: Any) -> None:
        # THE SAME COERCION the clean tree was built with. A patched value that took a different
        # path into the fact model would make the mutant differ from the clean filing in the
        # coercion as well as in the fault, and the campaign would be measuring both.
        value = _coerce(raw)
        leaf = _node(tree, cel_path(sheet, ref))
        if isinstance(leaf, dict):
            leaf["v"] = value
        for dotted in range_of.get((sheet, ref), ()):
            n = _node(tree, dotted)
            if not isinstance(n, dict):
                continue
            for cell in n.get("cells", ()):
                if cell.get("__cell__") == f"{sheet}!{ref}":
                    cell["v"] = value

    from cdfc.predicates.ast_walker import bound_cells

    cells_of = {p.id: bound_cells(p, schema) for p in predicates}

    def run(mutant: Path, mutant_grid: Any, edited: Sequence[tuple[str, str]]) -> tuple[str, ...]:
        from cdfc.qualify.observability import extract

        tree = copy.deepcopy(base_tree)
        literals = extract(mutant).literals
        for sheet, ref in edited:
            _patch(tree, sheet, ref, literals.get((sheet, ref), ""))
        for (sheet, ref), value in mutant_grid.values.items():
            _patch(tree, sheet, ref, value)
        facts = FactSet(tree, template)
        changed = {f"{s}!{r}" for s, r in edited} | {
            f"{s}!{r}" for (s, r) in mutant_grid.values
        }
        candidates = (
            [p for p in predicates if cells_of[p.id] & changed] if restrict else list(predicates)
        )
        failed = []
        for p in candidates:
            chk = evaluate_one(p, facts=facts, schema=schema, rt=rt)
            if chk.state is ItemState.FAIL:
                failed.append(p.id)
        return tuple(failed)

    return run
