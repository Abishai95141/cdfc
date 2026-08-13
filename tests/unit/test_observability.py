"""P6-B3 — the three-way observability filter. F18 and F19, as tests."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.calc.evaluate import ValueGrid  # noqa: E402
from cdfc.qualify.observability import (  # noqa: E402
    Observability,
    classify,
    classify_files,
    cone_for,
    grid_of,
)
from cdfc.qualify.surgery import plan_edit, seed_mutant  # noqa: E402

CLEAN = REPO / "fixtures" / "synthetic" / "clean__independently-computed__fme-q1.xlsx"
PORTFOLIO_O7 = ("3. Portfolio", "O7")


def _grid(values, not_run=None) -> ValueGrid:
    return ValueGrid(
        values=values, not_run=not_run or {}, computed_cells=frozenset(values),
        formula_source="FILING",
    )


def test_classify__a_difference_is_observable() -> None:
    obs, cells = classify(_grid({("S", "A1"): 1}), _grid({("S", "A1"): 2}))
    assert obs is Observability.OBSERVABLE and cells == {("S", "A1")}


def test_classify__identical_and_fully_evaluated_is_unobservable() -> None:
    obs, cells = classify(_grid({("S", "A1"): 1}), _grid({("S", "A1"): 1}))
    assert obs is Observability.UNOBSERVABLE and cells == frozenset()


def test_indeterminate_is_not_unobservable() -> None:
    """F18. A cell in `not_run` is identical in both grids BY CONSTRUCTION.

    Folding this into UNOBSERVABLE removes the mutant from `O`, and because `O = G − U − I` it
    RAISES `K/O` — the measurement error correlated with the quantity being measured, in the
    direction that flatters us.
    """
    obs, cells = classify(
        _grid({("S", "A1"): 1}, {("S", "B1"): "unimplemented: AGGREGATE"}),
        _grid({("S", "A1"): 1}, {("S", "B1"): "unimplemented: AGGREGATE"}),
    )
    assert obs is Observability.INDETERMINATE_OBSERVABILITY
    assert ("S", "B1") in cells, "the offending cell is NAMED, not merely counted"


def test_f11_mutant_is_observable(tmp_path: Path) -> None:
    """F19, and it is the test the plan most needed and did not have.

    Recalculating an F11 mutant through the TEMPLATE's formula graph overwrites the literal with
    the formula's value, the grids match, the flagship class classifies UNOBSERVABLE with `O = 0`,
    and `TEMPLATE_DIFF` can never clear G2 — with nothing red for twelve weeks.
    """
    out = tmp_path / "f11.xlsx"
    edit = plan_edit(CLEAN, *PORTFOLIO_O7, 999999, "F11.a")
    seed_mutant(CLEAN, [edit], out, fault_class="F11", operator_id="F11.a", seed=20260810)
    # `or True` made an earlier version of this pass on every build — in the test the plan calls
    # the one it most needed and did not have. The assertions below are unconditional.
    obs, cells = classify_files(CLEAN, out, edited=[PORTFOLIO_O7])
    assert obs is Observability.OBSERVABLE, (
        f"the F11 override classified {obs}: observability is recalculating through the "
        "TEMPLATE's formula graph, which overwrites the literal with the formula's value"
    )
    assert PORTFOLIO_O7 in cells, (
        "the overridden cell itself is not in the distinguishing set"
    )
    full = grid_of(CLEAN)
    cone = cone_for(CLEAN, [PORTFOLIO_O7])
    clean_grid = grid_of(CLEAN, cone=cone, baseline=full)
    mutant_grid = grid_of(out, cone=cone, baseline=full)
    assert clean_grid.values.get(PORTFOLIO_O7) != mutant_grid.values.get(PORTFOLIO_O7), (
        "the override did not change the recalculated value — observability is reading the "
        "TEMPLATE's formulas"
    )


def test_observability_recalculates_with_filing_formulas() -> None:
    """Asserted on the CALL GRAPH, not on a comment."""
    source = (REPO / "src" / "cdfc" / "qualify" / "observability.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    sources = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "recalculate":
            for kw in node.keywords:
                if kw.arg == "formula_source":
                    sources.append(ast.literal_eval(kw.value))
    assert sources and set(sources) == {"FILING"}, (
        f"observability recalculates with {sorted(set(sources))}; F19 requires FILING and nothing "
        "else. There are two call sites — the full grid and the cone-restricted one — and both "
        "must be FILING; a TEMPLATE on either makes the flagship class unobservable."
    )


def test_cone_is_exact_not_an_approximation() -> None:
    """A cell outside the transitive downstream cone cannot change, so the restriction is exact."""
    cone = cone_for(CLEAN, [PORTFOLIO_O7])
    full = grid_of(CLEAN)
    partial = grid_of(CLEAN, cone=cone, baseline=full)
    for key in partial.values:
        if key in full.values:
            assert str(partial.values[key]) == str(full.values[key]), key


def test_grid_of__the_clean_filing_has_indeterminate_cells() -> None:
    """The campaign's `I` is non-zero because of these, and they are MEASURED not contrived.

    29 cells use `AGGREGATE(15, 6, ...)` — option 6 means IGNORE ERROR VALUES, which this build
    does not implement. It refuses rather than computing over the wrong operand set.
    """
    g = grid_of(CLEAN)
    assert g.not_run, "no not_run cells: I would be 0 and F18's control would be vacuous"
    assert any("AGGREGATE" in r for r in g.not_run.values())
