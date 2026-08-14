"""P9 — the NC-R family. Every guard here is observed RED under its injector by `make nc-sweep`.

**The admission-side controls are in this file too, and they are what stop the whole layer being
satisfied by a relation that emits nothing.** A `template_diff` that always returned `[]` never
fires on a clean filing, never binds outside the denominator, and never reports a template defect
as a failure — perfect on four negative controls and worth nothing.
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.degree import degree_map  # noqa: E402
from cdfc.probes.precedents import build_precedent_map, ceiling  # noqa: E402
from cdfc.probes.qualify import RelationEnvelopeError, to_envelope  # noqa: E402
from cdfc.probes.relations.registry import RelationError, load, parse_row  # noqa: E402
from cdfc.probes.template_diff import fired, load_defects, template_diff  # noqa: E402
from cdfc.probes.workbook import filed_values  # noqa: E402
from cdfc.verdict.reasons import ReasonCode  # noqa: E402
from cdfc.verdict.states import ItemState  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
SYN = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
MEASUREMENTS = REPO / "docs" / "measurements"
G_RANGE = frozenset(f"1. Introduction!G{r}" for r in range(54, 64))


@pytest.fixture(scope="module")
def kit():
    return build_precedent_map(FME), degree_map(FME), load_defects()


def _defective_filing():
    return {("1. Introduction", "G54"): "Special Situation Fund",
            ("1. Introduction", "D17"): Decimal(1)}


# --- NC-R01 — a relation must not PASS an empty filing ------------------------------------


def test_nc__R01a_all_zero_filing_is_OUT_OF_SCOPE(kit) -> None:
    pm, dm, defects = kit
    out = template_diff({}, pm, defects, degrees=dm)
    assert out
    assert all(f.state is ItemState.OUT_OF_SCOPE for f in out)
    assert not any(f.state is ItemState.PASS for f in out)


def test_rel__td_precondition_holds(kit) -> None:
    """The same rule stated as the precondition's own property: a filing with inputs is IN_SCOPE,
    a filing without is not. A precondition that is always unmet refuses everything."""
    pm, dm, defects = kit
    live = template_diff(
        filed_values(SYN / "clean__independently-computed__fme-q1.xlsx"), pm, defects, degrees=dm
    )
    assert not any(f.state is ItemState.OUT_OF_SCOPE for f in live)


# --- NC-R02 — binding must stay inside the denominator ------------------------------------


def test_nc__R02a_binding_outside_the_denominator_aborts_closure(kit) -> None:
    pm, dm, defects = kit
    out = template_diff(
        filed_values(SYN / "formula-overwritten__portfolio-O7.xlsx"), pm, defects, degrees=dm
    )
    for f in out:
        assert f.bound_cells <= pm.field_surface
        assert f.formula_cell not in f.bound_cells


# --- NC-R03 — an unqualified relation settles nothing --------------------------------------


def test_unqualified_relation_cannot_settle_a_cell() -> None:
    by_id = {s.id: s for s in load()}
    with pytest.raises(RelationEnvelopeError):
        to_envelope(by_id["R-01"], "0" * 64)


def test_nc__R03b_qualified_relation_does_settle() -> None:
    """The admission-side control. A converter that refused EVERYTHING would pass the test
    above."""
    by_id = {s.id: s for s in load()}
    c = to_envelope(by_id["R-02"], "0" * 64)
    assert c.schema_keys and c.expr


# --- NC-R04 — a defective oracle is not the filer's failure ---------------------------------


def test_nc__R04a_declared_defect_is_INFORMATIONAL_not_FAIL(kit) -> None:
    pm, dm, defects = kit
    out = [
        f for f in template_diff(_defective_filing(), pm, defects, degrees=dm,
                                 otherwise_bound=G_RANGE)
        if f.formula_cell == "1. Introduction!D17"
    ]
    assert len(out) == 1
    assert out[0].state is ItemState.INFORMATIONAL
    assert out[0].state is not ItemState.FAIL


def test_nc__R04b_an_undeclared_cell_still_FAILs(kit) -> None:
    """The positive control: a defect table that swallowed every mismatch would pass R04a."""
    pm, dm, defects = kit
    fails = fired(
        template_diff(filed_values(SYN / "formula-overwritten__portfolio-O7.xlsx"), pm,
                      defects, degrees=dm)
    )
    assert [f.formula_cell for f in fails] == ["3. Portfolio!O7"]


# --- NC-R05 — the basis guard ---------------------------------------------------------------


def test_nc__R05a_a_cross_basis_relation_does_not_load() -> None:
    row = {
        "id": "R-XX", "title": "t", "necessity": "NECESSARY", "inputs": "FILING_ONLY",
        "bases": ["LOOK_THROUGH", "NON_LOOK_THROUGH"], "precondition": "has(filing.a.v)",
        "expr": "filing.a.v == 1", "witness": "[filing.a.__cell__]", "evidence": "e",
        "claims_fault_classes": ["F01"], "reviewed_by": ["x"], "reviewed_at": "2026-08-14",
        "review_label": "SINGLE-SIGNER — a weaker review",
    }
    with pytest.raises(RelationError, match="SINGLETON"):
        parse_row(row)


# --- NC-R06 — the probe seed is an input ----------------------------------------------------


def test_nc__R06a_the_probe_seed_is_a_pinned_constant() -> None:
    import ast

    src = (REPO / "src" / "cdfc" / "probes" / "driver.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "DEFAULT_SEED":
            assert isinstance(node.value, ast.Constant), (
                "the probe seed is an INPUT recorded in the manifest, not a draw from entropy"
            )
            return
    raise AssertionError("DEFAULT_SEED is not declared in driver.py")


# --- NC-R07 — redundancy against the harvested set ------------------------------------------


def test_nc__R07a_redundant_relation_is_removed_and_the_removal_is_recorded() -> None:
    assert "R-04" not in {s.id for s in load()}
    review = (REPO / "docs" / "RELATION-REVIEW.md").read_text(encoding="utf-8")
    assert "R-04" in review and "REFUSED at step 6" in review


def test_nc__R07b_a_genuinely_new_relation_moves_the_count() -> None:
    """The positive control: a review that refused everything would pass R07a."""
    assert {s.id for s in load()} >= {"R-02", "R-03"}


# --- NC-R09 — the fraction must not rise as the filing empties -------------------------------


def test_nc__R09a_a_degenerate_precondition_stays_in_the_denominator(kit) -> None:
    from cdfc.verdict.states import in_scope

    pm, dm, defects = kit
    out = template_diff({}, pm, defects, degrees=dm)
    assert {f.scope_kind for f in out} == {"PREDICATE_PRECONDITION"}
    for f in out[:20]:
        assert in_scope(f.state, f.reason, f.scope_kind), (
            "a cell out of scope because THIS FILER left its inputs empty is a statement about "
            "the PREDICATE and must stay counted"
        )


def test_nc__R09b_a_structurally_unreachable_cell_does_leave_the_denominator() -> None:
    """The positive control, and it is the half that makes R09a mean anything: a cell no relation
    over this template could ever reach IS a statement about the instrument, and that one
    legitimately leaves."""
    from cdfc.probes.template_diff import applicable
    from cdfc.verdict.states import in_scope

    acac = build_precedent_map(FIX / "Draft_ACAC_Format_20260605_0631.xlsx")
    cell = sorted(acac.unreachable)[0]
    assert applicable({}, cell, acac) == "DECLARED_CHARACTERISTIC"
    assert not in_scope(
        ItemState.OUT_OF_SCOPE, ReasonCode.OOS_NOT_APPLICABLE, "DECLARED_CHARACTERISTIC"
    )


# --- NC-R10 — a defect row must not raise the settled fraction --------------------------------


def test_defect_table_cannot_raise_the_settled_fraction(kit) -> None:
    """F14, and the fallback is in CODE rather than in the declarer's judgement."""
    pm, dm, defects = kit
    out = [
        f for f in template_diff(_defective_filing(), pm, defects, degrees=dm,
                                 otherwise_bound=frozenset())
        if f.formula_cell == "1. Introduction!D17"
    ]
    assert len(out) == 1
    assert out[0].state is ItemState.NO_PREDICATE
    assert out[0].reason is ReasonCode.NP_RULE_AMBIGUOUS


# --- NC-R11 — the eight blind cells, and the layer that actually catches them -------------------


def test_nc__R11a_an_unlocked_overwrite_is_not_credited_to_the_relation() -> None:
    """§0.5's mechanism, in P9's own headline fixture. Overwriting one of the eight unlocked
    formula cells moves the field surface, moves the fingerprint, and ends the run at F3 with
    `invalid.template_unbound` — **five steps before the relation executes.** The binder catches
    it, and `TEMPLATE_DIFF` must not be credited for the catch."""
    from cdfc.schema.fingerprint import structural_fingerprint

    base = structural_fingerprint(FME)
    assert structural_fingerprint(SYN / "formula-overwritten__investors-N5.xlsx") != base
    assert structural_fingerprint(SYN / "formula-overwritten__portfolio-O7.xlsx") == base

    d = json.loads((MEASUREMENTS / "p9-template-diff-ceiling.json").read_text(encoding="utf-8"))
    assert len(d["unlocked_formula_cells"]) == 8
    assert d["ceiling_binding_formula_cells"] < d["ceiling_all_formula_cells"]


def test_nc__R11b_the_ceiling_publishes_both_numbers() -> None:
    """The positive control: publishing only 957 would hide the blind spot, and publishing only
    869 would hide the ceiling the plan measured."""
    text = (MEASUREMENTS / "P9-template-diff-ceiling.md").read_text(encoding="utf-8")
    assert "957" in text and "869" in text


# --- NC-R12 — the tolerance unit mismatch is open, and half a repair is the same defect ---------


def test_nc__R12a_the_tolerance_unit_mismatch_is_still_open() -> None:
    """**Both sides, or neither.** `HALF_ULP` is half a unit of `MILLI_USD_MILLION`; the tree the
    runner evaluates carries the workbook's own numbers unscaled. Scaling one side alone is the
    same defect with the sign flipped, so this guard pins BOTH halves and fails on either move.
    """
    from cdfc.facts.units import HALF_ULP, UNITS_PER_USD_MILLION

    assert (HALF_ULP, UNITS_PER_USD_MILLION) == (5, 1_000)

    src = (REPO / "src" / "cdfc" / "facts" / "build.py").read_text(encoding="utf-8")
    assert "to_units" not in src, (
        "facts/build.py has started scaling. If the tree is now in MILLI_USD_MILLION, the "
        "harvested tolerance literals must move with it in the same commit."
    )
    d = json.loads((MEASUREMENTS / "p9-template-diff-ceiling.json").read_text(encoding="utf-8"))
    assert d["harvested_tolerance"]["with_tolerance"] > 0
    assert d["harvested_tolerance"]["max_tau_literal"] >= 5


def test_nc__R12b_a_new_relation_carries_no_tolerance_literal() -> None:
    """The positive control: the defect is in the harvest, and the relation layer does not
    inherit it. A relation with no tolerance literal cannot be 1,000× anything."""
    from cdfc.probes.relations import partition

    for token in partition.expr().replace("(", " ").replace(")", " ").split():
        assert not token.isdigit()


# --- the flagship's ceiling, as a control over the relation emitting nothing ---------------------


def test_nc__R_the_relation_does_bind_cells(kit) -> None:
    pm, _dm, _defects = kit
    assert ceiling(pm) == (957, 3747)
    assert pm.reachable
