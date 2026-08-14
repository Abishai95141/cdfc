"""P9-B1 — the degree map. **Money is degree 1; a person is not a rounded quantity.**

The tests are written so that a degree map returning `0` for everything fails, and so does one
returning `1` for everything. Either would satisfy a suite that only checked the safe direction.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.facts.units import HALF_ULP  # noqa: E402
from cdfc.probes.degree import (  # noqa: E402
    Assignment,
    _classify,
    _parenthesised,
    _tokens,
    assign,
    degree_map,
    tau_for,
)

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


@pytest.fixture(scope="module")
def dm():
    return degree_map(FME)


def test_degree__counts_get_zero_tolerance(dm) -> None:
    """`'1. Introduction'!D17` is `SUM(D18:D20)` over three COUNTIF rows. Under a blanket
    `τ(n) = 5n` a filing could be wrong by fifteen schemes and pass."""
    a = dm["1. Introduction!D17"]
    assert a.degree == 0
    assert a.basis == "COUNT_MARKER"
    assert tau_for(a, n_summands=3) == 0
    assert tau_for(a, n_summands=1000) == 0


def test_degree__money_cells_get_tau_5n(dm) -> None:
    """`'3. Portfolio'!O7` is `SUM(C7:N7)` under `Table 3.1 … (USD Million)`."""
    a = dm["3. Portfolio!O7"]
    assert a.degree == 1
    assert a.basis == "MONEY_MARKER"
    assert tau_for(a, n_summands=12) == 12 * HALF_ULP == 60


def test_degree__categoricals_and_ratios_are_degree_zero(dm) -> None:
    """A `%` column inside a `(USD Million)` table is a ratio: the NEARER marker wins."""
    a = dm["3. Portfolio!Y75"]                       # IFERROR(X75/$O$7,0) — a share of the total
    assert (a.degree, a.basis) == (0, "RATIO_MARKER")
    assert "%" in (a.evidence_text or "")
    assert tau_for(a, n_summands=12) == 0


def test_degree__dates_are_degree_zero(dm) -> None:
    a = dm["1. Introduction!D40"]
    assert (a.degree, a.basis) == (0, "DATE_MARKER")
    assert "Date" in (a.evidence_text or "")


def test_degree__both_degrees_are_actually_used(dm) -> None:
    """The admission-side control against a map that answers the same thing everywhere. A
    constant-0 map passes every count assertion; a constant-1 map passes every money one."""
    bases = Counter(a.basis for a in dm.values())
    assert len(dm) == 505
    assert bases["MONEY_MARKER"] == 223
    assert sum(v for k, v in bases.items() if k != "MONEY_MARKER") == 282
    assert bases["AMBIGUOUS"] == 0, "an unresolved tie means the marker lists are colliding"


def test_degree__every_money_cell_names_its_evidence(dm) -> None:
    """Money is the degree that buys a tolerance, so it is the one that must cite the
    regulator's own words. A degree with no evidence is an opinion."""
    for a in dm.values():
        if a.degree == 1:
            assert a.evidence_cell and a.evidence_text, f"{a.cell} claims money without evidence"


def test_degree__an_assignment_of_money_without_evidence_cannot_be_constructed() -> None:
    """The rule above, enforced by the record rather than by the test that checks it."""
    with pytest.raises(ValueError, match="no evidence"):
        Assignment(cell="S!A1", degree=1, basis="MONEY_MARKER",
                   evidence_cell=None, evidence_text=None)
    Assignment(cell="S!A1", degree=0, basis="NO_MARKER", evidence_cell=None, evidence_text=None)


def test_degree__a_table_title_is_prose_and_only_its_parentheses_declare_a_unit() -> None:
    """`Table 3.6: … in which 30% or more of the Total Portfolio Value` contains `%`, and
    `Table 3.1: … as at the end of quarter (USD Million)` contains a temporal phrase. Reading
    whole titles as unit declarations made 46 of 505 cells AMBIGUOUS."""
    assert _parenthesised("Table 3.1: Portfolio Details (USD Million)") == "USD Million"
    assert _parenthesised("scheme(s) in which 30% or more") == "s"
    assert _classify("USD Million") == "MONEY_MARKER"
    assert _classify("as at the end of quarter") is None


def test_degree__markers_are_tokens_and_not_substrings() -> None:
    """`ratio` is a substring of `Registration`. A degree decided by substring is a degree
    decided by whatever the marker list accidentally spells."""
    assert _tokens("Date of Registration of FME") == (
        "date", "of", "registration", "of", "fme"
    )
    assert _classify("Date of Registration of FME") == "DATE_MARKER"
    assert _classify("Amount Invested in US as % of Total") == "RATIO_MARKER"


def test_degree__a_conflicting_level_refuses_rather_than_choosing_money() -> None:
    """A tie broken towards money is the one silent path back to a tolerance on a count."""
    assert _classify("No. of Investors (USD Million)") == "AMBIGUOUS"
    a = assign("S", "B2", {"A2": "No. of Investors (USD Million)"})
    assert (a.degree, a.basis) == (0, "AMBIGUOUS")


def test_degree__a_cell_with_no_marker_anywhere_is_degree_zero() -> None:
    """The default direction is the whole design: a tolerance wrongly applied hides a fault and
    nothing goes red; a tolerance wrongly withheld produces a visible, arguable false alarm."""
    a = assign("S", "B2", {})
    assert (a.degree, a.basis, a.evidence_text) == (0, "NO_MARKER", None)


def test_degree__the_table_boundary_stops_a_unit_leaking_from_the_table_above() -> None:
    """Without the bound, a table that declares no unit inherits the previous table's — which is
    how a count acquires a tolerance from a sentence about a different table three screens up."""
    text = {"A1": "Table 1: Amounts (USD Million)", "A9": "Table 2: Headcount", "B10": "x"}
    assert assign("S", "C10", text).basis == "NO_MARKER"
    assert assign("S", "C5", text).basis == "MONEY_MARKER"
