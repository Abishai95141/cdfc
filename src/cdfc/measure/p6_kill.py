"""P6 — "killed" means a predicate returned `FAIL` under the P5 verdict model.

The fact tree is built ONCE from the clean filing and PATCHED per mutant: the edited cells take
the mutant's literal and every cell in the edit's transitive downstream cone takes the mutant's
recalculated value. A cell outside the cone cannot change, so the patch is exact rather than an
approximation — and re-parsing the workbook per mutant would cost hours.

**The patch is `facts/patch.py`'s, and it is shared with P10's canary loop deliberately.** The
canary replays a stored kill to prove the predicate still catches it; if the two patchers differed,
the canary would be testing whether two implementations of one idea agree rather than whether the
check works. Routing both through one module is also what surfaced the `"None"` coercion defect
that module documents — the campaign's own kills were being read back and 81 of 125 predicates did
not reproduce them.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from cdfc.schema.anchor import Anchor
from cdfc.evaluate.celrt import CelRuntime
from cdfc.evaluate.runner import evaluate_one
from cdfc.facts.build import filing_tree, template_tree
from cdfc.facts.patch import ABSENT, CellIndex, patch, value_for
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
    cell_index = CellIndex.of(ctx)

    from cdfc.predicates.ast_walker import bound_cells

    cells_of = {p.id: bound_cells(p, schema) for p in predicates}

    def run(mutant: Path, mutant_grid: Any, edited: Sequence[tuple[str, str]]) -> tuple[str, ...]:
        from cdfc.qualify.observability import extract

        literals = extract(mutant).literals
        # THE SAME COERCION the clean tree was built with, and the same ABSENCE rule. A patched
        # value that took a different path into the fact model would make the mutant differ from
        # the clean filing in the coercion as well as in the fault, and the campaign would be
        # measuring both — which is exactly what `"None"` was.
        patches = {
            Anchor.cell(s, r).render(): value_for(v) for (s, r), v in mutant_grid.values.items()
        }
        for sheet, ref in edited:
            patches[Anchor.cell(sheet, ref).render()] = value_for(literals.get((sheet, ref), ABSENT))
        facts = FactSet(patch(base_tree, patches, index=cell_index), template)
        changed = {Anchor.cell(s, r).render() for s, r in edited} | {
            Anchor.cell(s, r).render() for (s, r) in mutant_grid.values
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
