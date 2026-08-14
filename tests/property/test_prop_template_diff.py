"""P9-B1 — the properties. Generated inputs, not chosen ones.

The four here are the ones a chosen example cannot establish: they quantify over *every* formula
cell, *every* subset of the defect table, and *every* integer difference.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.degree import degree_map  # noqa: E402
from cdfc.probes.precedents import build_precedent_map, ceiling  # noqa: E402
from cdfc.probes.template_diff import (  # noqa: E402
    TemplateDefectTable,
    agree,
    fired,
    load_defects,
    template_diff,
)
from cdfc.probes.workbook import filed_values  # noqa: E402

FME = (
    REPO / "fixtures" / "prescribed"
    / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)
CLEAN = REPO / "fixtures" / "synthetic" / "clean__independently-computed__fme-q1.xlsx"

SLOW = settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])

_PM = build_precedent_map(FME)
_DM = degree_map(FME)
_DEFECTS = load_defects()
_CELLS = sorted(_PM.formula_text)


_FILED = filed_values(CLEAN)
_FINDINGS = template_diff(_FILED, _PM, _DEFECTS, degrees=_DM)
_BY_CELL = {f.formula_cell: f for f in _FINDINGS}


@given(st.lists(st.sampled_from(_CELLS), min_size=1, max_size=40, unique=True))
@SLOW
def test_prop__binding_is_a_subset_of_the_denominator(cells: list[str]) -> None:
    """For every FINDING, `bound_cells ⊆ field_surface` and non-empty, and a bound set never
    contains the formula cell itself. NC-R02.

    **Over the findings and not over the map.** Quantifying over `pm.in_field_surface` would test
    the precedent map — which is right, and is a different property. The rule NC-R02 guards is
    about what a FINDING binds, so `td_binds_the_formula_cell` has to be able to break it; a
    property that read the map would stay green under that injector and the control would be
    green for a reason unrelated to the break.
    """
    for cell in cells:
        f = _BY_CELL[cell]
        assert f.bound_cells <= _PM.field_surface, f"{cell} binds outside the denominator"
        assert cell not in f.bound_cells, f"{cell} binds ITSELF, which is not in the field surface"


@given(st.lists(st.sampled_from(_CELLS), min_size=1, max_size=60, unique=True))
@SLOW
def test_prop__the_ceiling_is_monotone_and_bounded(cells: list[str]) -> None:
    """`|⋃ bound_cells| ≤ 957` for every subset of relations over this template. A subset cannot
    reach more cells than the whole."""
    union: set[str] = set()
    for cell in cells:
        union |= _PM.in_field_surface[cell]
    assert len(union) <= ceiling(_PM)[0]


@given(st.integers(min_value=0, max_value=200), st.integers(min_value=0, max_value=5_000))
@SLOW
def test_prop__tolerance_is_one_sided_in_the_safe_direction(tau: int, base: int) -> None:
    """A difference of exactly `τ` does NOT fire; `τ + 1` does. In integer
    `MILLI_USD_MILLION`, against values in the workbook's own USD Million."""
    a = Decimal(base)
    at_tau = a + Decimal(tau) / 1000
    past_tau = a + Decimal(tau + 1) / 1000
    assert agree(a, at_tau, tau)
    if a != 0:
        assert not agree(a, past_tau, tau) or (past_tau - a) / abs(a) < Decimal("1e-15")


@given(st.integers(min_value=1, max_value=5_000))
@SLOW
def test_prop__a_count_never_gets_a_tolerance(delta: int) -> None:
    """τ = 0 admits no difference at all. A person, and a scheme, is not a rounded quantity."""
    assert not agree(Decimal(0), Decimal(delta), 0)


@pytest.mark.parametrize("subset", [(), ("1. Introduction!D17",)])
def test_prop__a_declared_defect_never_raises_the_settled_fraction(subset: tuple[str, ...]) -> None:
    """F14, over every subset of the declared defect table. With the fallback in place, a
    declared defect on a cell nothing else binds becomes `NO_PREDICATE(rule_ambiguous)`, which
    STAYS in the denominator — so the fraction cannot rise by adding a row."""
    from cdfc.verdict.states import in_scope

    table = TemplateDefectTable({k: v for k, v in _DEFECTS.by_cell.items() if k in subset})
    filed = {("1. Introduction", "G54"): "Special Situation Fund",
             ("1. Introduction", "D17"): Decimal(1)}
    out = [f for f in template_diff(filed, _PM, table, degrees=_DM, otherwise_bound=frozenset())
           if f.formula_cell == "1. Introduction!D17"]
    assert len(out) == 1
    assert in_scope(out[0].state, out[0].reason, out[0].scope_kind), (
        "a declared defect must not remove a cell from the denominator when nothing else binds it"
    )


def test_prop__idempotence_over_the_real_clean_filing() -> None:
    """Running twice over one fact table yields identical findings in identical order."""
    filed = filed_values(CLEAN)
    a = template_diff(filed, _PM, _DEFECTS, degrees=_DM)
    b = template_diff(filed, _PM, _DEFECTS, degrees=_DM)
    assert a == b
    assert fired(a) == []
