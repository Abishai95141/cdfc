"""P9-B1 — `TEMPLATE_DIFF`, the flagship relation.

**The admission side is load-bearing here.** A relation that emits nothing scores perfectly on
every negative control in the phase: it never fires on a clean filing, never binds outside the
denominator, never reports a template defect as a failure. So the file opens with the three tests
that stop it — the F11 pair IS detected, an undeclared mismatch DOES fail, and the relation DOES
bind cells — and only then checks the ways it must not fire.
"""

from __future__ import annotations

import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.degree import degree_map  # noqa: E402
from cdfc.probes.precedents import build_precedent_map  # noqa: E402
from cdfc.probes.template_diff import (  # noqa: E402
    METHOD,
    PROVENANCE,
    WARRANT,
    DiffFinding,
    TemplateDefectTable,
    TemplateDiffError,
    agree,
    applicable,
    fired,
    load_defects,
    template_diff,
)
from cdfc.probes.workbook import filed_values  # noqa: E402
from cdfc.verdict.reasons import ReasonCode  # noqa: E402
from cdfc.verdict.states import ItemState  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
SYN = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"

G_RANGE = [f"1. Introduction!G{r}" for r in range(54, 64)]


@pytest.fixture(scope="module")
def pm():
    return build_precedent_map(FME)


@pytest.fixture(scope="module")
def dm():
    return degree_map(FME)


@pytest.fixture(scope="module")
def defects():
    return load_defects()


def _run(name: str, pm, dm, defects, **kw) -> list[DiffFinding]:
    return template_diff(filed_values(SYN / name), pm, defects, degrees=dm, **kw)


# --------------------------------------------------------------------------------
# ADMISSION SIDE — the three tests that stop a relation which emits nothing
# --------------------------------------------------------------------------------


def test_td__fires_on_the_overwritten_formula(pm, dm, defects) -> None:
    f = _run("formula-overwritten__portfolio-O7.xlsx", pm, dm, defects)
    fails = fired(f)
    assert [x.formula_cell for x in fails] == ["3. Portfolio!O7"]
    got = fails[0]
    assert got.filed_value == "999999"
    assert got.recomputed == "0"
    assert got.witness == ("3. Portfolio!O7",)
    assert got.bound_cells == pm.in_field_surface["3. Portfolio!O7"]
    assert got.bound_cells <= pm.field_surface and got.bound_cells
    assert (got.method, got.warrant, got.provenance) == (METHOD, WARRANT, PROVENANCE)


def test_td__fires_on_the_coordinated_pair(pm, dm, defects) -> None:
    """The F11 PAIR — `'3. Portfolio'!O7` and its own carry `C182 = O7`, both overwritten with
    the same literal. Every carry identity in the workbook still holds. If `TEMPLATE_DIFF`
    could not detect this it would detect only careless overrides."""
    fails = fired(_run("formula-overwritten__pair-portfolio-O7-C182.xlsx", pm, dm, defects))
    assert [x.formula_cell for x in fails] == ["3. Portfolio!O7", "3. Portfolio!C182"]
    assert {x.filed_value for x in fails} == {"999999"}
    assert all(x.bound_cells for x in fails)


def test_td__fires_on_stale_carries_a_structural_detector_cannot_see(pm, dm, defects) -> None:
    """`values-written__50-cells.xlsx` writes fifty inputs and leaves the derived cells at the
    blank's cached zeros. **No formula was deleted**, so a detector that looks for missing `<f>`
    elements reports zero findings — which is what the P5 demo's admission-side control does.
    The value comparison is strictly stronger and these twenty are true positives."""
    fails = fired(_run("values-written__50-cells.xlsx", pm, dm, defects))
    assert len(fails) == 20
    # Ten row totals `O3:O12`, and the ten cells of Table 3.8 that CARRY those totals. The carry
    # is stale in exactly the same way and for the same reason, which is what makes twenty rather
    # than ten the honest count.
    assert [f.formula_cell for f in fails] == (
        [f"3. Portfolio!O{r}" for r in range(3, 13)]
        + [f"3. Portfolio!C{r}" for r in range(178, 188)]
    )
    assert {f.recomputed for f in fails} == {"2"}
    assert {f.filed_value for f in fails} == {"0"}


# --------------------------------------------------------------------------------
# REJECTION SIDE
# --------------------------------------------------------------------------------


def test_td__fires_on_zero_cells_of_a_filing_the_product_did_not_compute(pm, dm, defects) -> None:
    """The zero-fire arm, on a corpus **whose derived cells our evaluator did not write**.

    `clean__independently-computed__fme-q1.xlsx` was derived by LibreOffice. A zero-fire result
    on a `TEMPLATE-COMPUTED` filing would be `x == x` — green on a relation that always returns
    `[]` and green on one whose tolerance is 1,000×.
    """
    f = _run("clean__independently-computed__fme-q1.xlsx", pm, dm, defects)
    assert fired(f) == []
    states = Counter(str(x.state) for x in f)
    assert states["PASS"] == 475
    assert states["NOT_RUN"] == 30
    assert sum(states.values()) == 505


def test_td__a_cell_the_evaluator_could_not_compute_is_NOT_RUN_never_FAIL(pm, dm, defects) -> None:
    """`error.predicate_raised` and `not_run.source_unreadable` have opposite remedies. Comparing
    the filed value against an absent recomputation turns *our apparatus said nothing* into
    *your filing is wrong*."""
    f = _run("clean__independently-computed__fme-q1.xlsx", pm, dm, defects)
    nr = [x for x in f if x.state is ItemState.NOT_RUN]
    assert len(nr) == 30
    assert {x.reason for x in nr} == {ReasonCode.NR_SOURCE_UNREADABLE}
    assert all(x.recomputed is None and x.detail for x in nr)


def test_td__applicability_is_a_scope_kind_and_never_a_bool(pm) -> None:
    """An empty filing must return `OUT_OF_SCOPE`, never `PASS` (NC-R01). The blank's own cached
    grid is essentially zeros and `"NA"` strings, so without the precondition an unfilled filing
    sweeps the flagship's door."""
    assert applicable({}, "3. Portfolio!O7", pm) == "PREDICATE_PRECONDITION"
    assert applicable({("3. Portfolio", "C7"): Decimal(1)}, "3. Portfolio!O7", pm) == "IN_SCOPE"


def test_td__scope_kind_distinguishes_declared_from_precondition(pm) -> None:
    """The two are NOT the same claim, and only one of them leaves the denominator (C3).

    `DECLARED_CHARACTERISTIC` — no field-surface precedent could ever exist: a fact about the
    INSTRUMENT. `PREDICATE_PRECONDITION` — precedents exist and THIS filing left them empty: a
    fact about the PREDICATE, which stays counted and accuses its own predicate.
    """
    from cdfc.probes.precedents import build_precedent_map as build

    acac = build(FIX / "Draft_ACAC_Format_20260605_0631.xlsx")
    cell = sorted(acac.unreachable)[0]
    assert applicable({}, cell, acac) == "DECLARED_CHARACTERISTIC"
    assert applicable({}, "3. Portfolio!O7", pm) == "PREDICATE_PRECONDITION"


def test_td__an_out_of_scope_finding_without_a_scope_kind_cannot_be_constructed() -> None:
    """`in_scope()` fails closed rather than guessing, so the field is required at the source."""
    with pytest.raises(TemplateDiffError, match="no scope_kind"):
        DiffFinding(
            formula_cell="S!A1", state=ItemState.OUT_OF_SCOPE,
            reason=ReasonCode.OOS_NOT_APPLICABLE, scope_kind=None,
            filed_value=None, recomputed=None, tau=0, degree=0,
            bound_cells=frozenset(), witness=("S!A1",),
        )


def test_td__a_fail_bound_to_nothing_cannot_be_constructed() -> None:
    """`cells_bound == 0` is a G1 refusal; it must never be reachable at run time."""
    with pytest.raises(TemplateDiffError, match="bound to no cell"):
        DiffFinding(
            formula_cell="S!A1", state=ItemState.FAIL, reason=None, scope_kind="IN_SCOPE",
            filed_value="1", recomputed="2", tau=0, degree=0,
            bound_cells=frozenset(), witness=("S!A1",),
        )


# --------------------------------------------------------------------------------
# tolerance
# --------------------------------------------------------------------------------


def test_td__tolerance_is_one_sided_in_the_safe_direction() -> None:
    """A difference of exactly `τ` does NOT fire; `τ + 1` does. Both in integer
    `MILLI_USD_MILLION`, where the workbook's own scale is USD Million."""
    tau = 60
    assert agree(Decimal("100"), Decimal("100.060"), tau)
    assert not agree(Decimal("100"), Decimal("100.061"), tau)


def test_td__a_count_gets_no_tolerance_at_all() -> None:
    assert agree(Decimal("3"), Decimal("3"), 0)
    assert not agree(Decimal("3"), Decimal("4"), 0)
    assert not agree(Decimal("3"), Decimal("3.0001"), 0)


def test_td__the_representation_epsilon_is_not_a_tolerance() -> None:
    """It absorbs a difference at the sixteenth significant digit, which is a statement about
    float serialisation. It never grows with the summand count and never hides a whole unit."""
    assert agree(Decimal("1") / 12, Decimal("0.0833333333333333333"), 0)
    assert not agree(Decimal("1000000"), Decimal("1000001"), 0)


def test_td__non_numeric_values_compare_as_strings() -> None:
    assert agree("NA", "na", 0)
    assert not agree("NA", Decimal("12"), 0)
    assert agree(None, None, 0)


# --------------------------------------------------------------------------------
# the defective oracle
# --------------------------------------------------------------------------------


def _defective_filing() -> dict[tuple[str, str], object]:
    """A filing that declares a *Special Situation Fund* and counts it. The regulator's own
    COUNTIFs match seven of the nine scheme types, so our recomputation of `D17` says 0 and the
    correct filer says 1. **The filer who fills the return correctly is the one this cell
    disagrees with**, which is why the cell is declared."""
    return {("1. Introduction", "G54"): "Special Situation Fund",
            ("1. Introduction", "D17"): Decimal(1)}


def test_td__declared_defect_is_INFORMATIONAL_when_something_else_binds_the_cells(
    pm, dm, defects
) -> None:
    f = [
        x for x in template_diff(
            _defective_filing(), pm, defects, degrees=dm,
            otherwise_bound=frozenset(G_RANGE),
        ) if x.formula_cell == "1. Introduction!D17"
    ]
    assert len(f) == 1
    assert f[0].state is ItemState.INFORMATIONAL
    assert f[0].defect_id == "TD-01"
    assert f[0].filed_value == "1" and f[0].recomputed == "0"
    assert "seven" in f[0].detail.lower() or "SEVEN" in f[0].detail


def test_td__defect_that_would_raise_the_fraction_becomes_rule_ambiguous(pm, dm, defects) -> None:
    """F14, in code and not in the declarer's judgement.

    `INFORMATIONAL` leaves the denominator. For a bound cell nothing else reaches,
    `fraction = s/(i−1) > s/i` — so **adding a row to the defect table would raise the
    headline**. Append-only with an evidence command stops fabricated defects; it does nothing
    about convenient true ones, and those are the ones a person under deadline will find.
    """
    f = [
        x for x in template_diff(
            _defective_filing(), pm, defects, degrees=dm, otherwise_bound=frozenset()
        ) if x.formula_cell == "1. Introduction!D17"
    ]
    assert len(f) == 1
    assert f[0].state is ItemState.NO_PREDICATE
    assert f[0].reason is ReasonCode.NP_RULE_AMBIGUOUS
    assert f[0].defect_id == "TD-01"
    assert "raise the fraction" in f[0].detail


def test_td__an_undeclared_mismatch_still_FAILs(pm, dm, defects) -> None:
    """NC-R04's positive control. A defect table that swallowed every mismatch would pass every
    other test in this file."""
    fails = fired(_run("formula-overwritten__portfolio-O7.xlsx", pm, dm, defects))
    assert fails and fails[0].formula_cell not in defects.by_cell


def test_td__a_defect_declared_against_another_template_is_not_applied(pm, dm) -> None:
    """A defect is scoped to ONE `template_sha256`. Applied to a different digest it is an
    opinion about a different artifact."""
    from cdfc.probes.template_diff import TemplateDefect

    wrong = TemplateDefectTable({
        "3. Portfolio!O7": TemplateDefect(
            cell="3. Portfolio!O7", template_sha256="0" * 64, description="x",
            evidence_command="true", declared_by="x", declared_at="2026-01-01", id="TD-99",
        )
    })
    fails = fired(_run("formula-overwritten__portfolio-O7.xlsx", pm, dm, wrong))
    assert [x.formula_cell for x in fails] == ["3. Portfolio!O7"]


def test_td__a_defect_row_missing_a_field_refuses_to_load(tmp_path) -> None:
    p = tmp_path / "d.yaml"
    p.write_text("defects:\n  - cell: 'S!A1'\n    description: x\n", encoding="utf-8")
    with pytest.raises(TemplateDiffError, match="list of opinions"):
        load_defects(p)


# --------------------------------------------------------------------------------
# ordering and idempotence
# --------------------------------------------------------------------------------


def test_td__findings_are_ordered_by_sheet_row_column(pm, dm, defects) -> None:
    f = _run("formula-overwritten__portfolio-O7.xlsx", pm, dm, defects)
    from cdfc.probes.template_diff import _cell_order

    assert [x.formula_cell for x in f] == sorted((x.formula_cell for x in f), key=_cell_order)


def test_td__running_twice_yields_identical_findings(pm, dm, defects) -> None:
    a = _run("formula-overwritten__portfolio-O7.xlsx", pm, dm, defects)
    b = _run("formula-overwritten__portfolio-O7.xlsx", pm, dm, defects)
    assert a == b


def test_td__a_missing_degree_map_refuses_rather_than_defaulting(pm, defects) -> None:
    """Defaulting to 0 silently withholds `τ` from money; defaulting to 1 silently grants it to
    counts. Both are decisions nobody made."""
    with pytest.raises(TemplateDiffError, match="degree map"):
        template_diff({}, pm, defects)
