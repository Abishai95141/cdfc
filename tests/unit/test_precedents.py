"""P9-B1 — the precedent map. Admission side and rejection side in one file, deliberately.

A map that resolves everything and a map that resolves nothing both pass one of them.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.precedents import (  # noqa: E402
    READINGS,
    IncompletePrecedents,
    PrecedentError,
    build_precedent_map,
    ceiling,
    materialised_formulas,
)

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
ALR = FIX / "ALR_V2_3_20250808_1024.xlsx"
ACAC = FIX / "Draft_ACAC_Format_20260605_0631.xlsx"


@pytest.fixture(scope="module")
def pm():
    return build_precedent_map(FME)


def test_precedents__shared_dependents_are_row_shifted(pm) -> None:
    """`'3. Portfolio'!O4 → SUM(C4:N4)` — the positive control the specification names.

    PAIRED VALUE ASSERTION (R-GOLD-2): the count AND the body. A dependent resolved from its
    master's UNSHIFTED text yields a well-formed formula for the wrong row, so a test that
    checked only *"505 formulas materialised"* would be green on 211 confidently wrong ones.
    """
    text, deferred = materialised_formulas(FME)
    assert len(text) == 505
    assert deferred == {}
    assert text["3. Portfolio!O4"] == "SUM(C4:N4)"
    assert text["3. Portfolio!O7"] == "SUM(C7:N7)"
    # And the master itself is unshifted, which is the other way to get this wrong.
    assert pm.in_field_surface["3. Portfolio!O4"] < pm.field_surface


def test_precedents__a_dependent_resolved_from_unshifted_master_text_is_wrong(pm) -> None:
    """The rejection side of the same rule, stated as an inequality rather than a hope."""
    assert pm.in_field_surface["3. Portfolio!O4"] != pm.in_field_surface["3. Portfolio!O7"]
    assert "3. Portfolio!C4" in pm.in_field_surface["3. Portfolio!O4"]
    assert "3. Portfolio!C4" not in pm.in_field_surface["3. Portfolio!O7"]


def test_precedents__cross_sheet_references_resolve_to_the_named_sheet(pm) -> None:
    """`'2. Summary'` formulas referencing `'1. Introduction'!C54` bind on `1. Introduction`."""
    assert pm.formula_text["2. Summary!B5"] == "'1. Introduction'!C54"
    assert pm.by_formula_cell["2. Summary!B5"] == frozenset({"1. Introduction!C54"})
    assert all(
        not c.startswith("2. Summary!") for c in pm.by_formula_cell["2. Summary!B5"]
    ), "a cross-sheet reference resolved against the REFERRING sheet is silently wrong"


def test_precedents__unreachable_formula_binds_zero() -> None:
    """A formula whose precedents miss the field surface entirely returns `∅` and is LISTED.

    `Draft_ACAC` ships no protection mask at all, so its field surface is empty and all 112 of
    its formula cells are unreachable. They are refused at G1 with `cells_bound = 0`; they are
    never raised at run time and never silently dropped.
    """
    acac = build_precedent_map(ACAC)
    assert len(acac.field_surface) == 0
    assert len(acac.formula_text) == 112
    assert len(acac.unreachable) == 112
    assert all(acac.in_field_surface[c] == frozenset() for c in acac.unreachable)
    assert ceiling(acac) == (0, 0)


def test_precedents__the_three_readings_agree_on_the_ceiling_and_not_on_the_binding() -> None:
    """The measurement that makes the published number trustworthy AND stops it being read as
    proof that the reading did not matter."""
    maps = {r: build_precedent_map(FME, reading=r) for r in READINGS}
    assert {ceiling(m)[0] for m in maps.values()} == {957}
    assert len(maps["transitive"].unreachable) == 0
    assert len(maps["value"].unreachable) == 115
    assert len(maps["lexical"].unreachable) == 115


def test_precedents__transitive_follows_through_intermediate_formula_cells(pm) -> None:
    """`D17 = SUM(D18:D20)` over three COUNTIFs reaching `G54:G63`. The direct precedents are
    three FORMULA cells, which no filer may write; the answer depends on ten cells they can."""
    direct = build_precedent_map(FME, reading="value")
    assert direct.in_field_surface["1. Introduction!D17"] == frozenset()
    assert direct.by_formula_cell["1. Introduction!D17"] == frozenset(
        {"1. Introduction!D18", "1. Introduction!D19", "1. Introduction!D20"}
    )
    bound = pm.in_field_surface["1. Introduction!D17"]
    assert bound == frozenset(f"1. Introduction!G{r}" for r in range(54, 64))


def test_precedents__the_ceiling_is_957_of_3747(pm) -> None:
    assert ceiling(pm) == (957, 3747)
    assert pm.per_sheet() == {
        "1. Introduction": 64, "2. Summary": 20, "3. Portfolio": 400,
        "4. Investors": 368, "5. PMS": 104, "8. Compliance Status": 1,
    }


def test_precedents__binding_is_a_subset_of_the_denominator(pm) -> None:
    """NC-R02: a finding that binds outside the field surface has widened the denominator."""
    for cell, bound in pm.in_field_surface.items():
        assert bound <= pm.field_surface, f"{cell} binds outside the field surface"
        assert cell not in bound, f"{cell} binds ITSELF — a formula cell is never in the surface"


def test_precedents__an_incomplete_closure_refuses_rather_than_under_reporting(pm) -> None:
    """A precedent set passing through an unmaterialised formula is a LOWER BOUND and says so.

    FME has no such cell, so the mechanism is exercised against a constructed map: a silent
    lower bound is a `cells_bound` nobody can check, and a small enough one is a G1 refusal
    for a reason that is ours rather than the template's.
    """
    import dataclasses

    holed = dataclasses.replace(pm, incomplete=frozenset({"3. Portfolio!O7"}))
    with pytest.raises(IncompletePrecedents, match="LOWER BOUND"):
        holed.assert_complete("3. Portfolio!O7")
    pm.assert_complete("3. Portfolio!O7")   # the real map is complete


def test_precedents__an_unknown_reading_is_refused() -> None:
    with pytest.raises(PrecedentError, match="unknown reading"):
        build_precedent_map(FME, reading="whatever")  # type: ignore[arg-type]


def test_precedents__alr_is_the_shared_dependent_stress_case() -> None:
    """ALR is where a map built from formula TEXT fails first and hardest: most of its formula
    cells are shared dependents, so a materialiser that skipped the row shift would produce a
    map that is wrong for the majority of the sheet and well-formed throughout."""
    text, deferred = materialised_formulas(ALR)
    assert len(text) == 645
    assert deferred == {}
    alr = build_precedent_map(ALR)
    assert ceiling(alr) == (914, 1599)
    assert len(alr.unreachable) == 2
