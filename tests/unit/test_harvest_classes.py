"""P4-B4 — one test per harvest class, plus the rules the harvest as a whole obeys."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.facts.units import HALF_ULP  # noqa: E402
from cdfc.measure.harvest_report import claimed_classes, unclaimed_classes  # noqa: E402
from cdfc.predicates.ast_walker import check_declared_keys  # noqa: E402
from cdfc.predicates.canonical import code_sha256  # noqa: E402
from cdfc.predicates.cel_profile import check_subset  # noqa: E402
from cdfc.predicates.envelope import Tolerance  # noqa: E402
from cdfc.predicates.fault_model import known_ids  # noqa: E402
from cdfc.predicates.harvest import (  # noqa: E402
    SkipRecord,
    harvest,
    single_call,
)
from cdfc.predicates.harvest_classes import CLAIMS  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
ITFS = FIX / "ITFS_Monthly_report201220241626.xlsx"
EDR = FIX / "EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx"


@pytest.fixture(scope="module")
def fme():
    return harvest(FME)


def _of_class(res, name: str):
    return [c for c in res.candidates if name in c.rationale or True and _cls(c) == name]


def _cls(c) -> str:
    """The harvest class a candidate came from, read back off its claim + shape."""
    for name, claims in CLAIMS.items():
        if tuple(c.claims_fault_classes) == tuple(claims):
            if name in ("numeric_bound", "integer_bound") and "whole" in c.rationale:
                return "integer_bound"
            return name
    return "?"


# --- one test per class -------------------------------------------------------------------


def test_cross_sheet_equality__emits_an_equality_over_two_documents_cells(fme) -> None:
    c = next(x for x in fme.candidates if _cls(x) == "cross_sheet_equality")
    assert c.expr.count("==") == 1 and c.tolerance is None
    assert c.witness.startswith("[") and c.witness.count("__cell__") == 2, (
        "both ends of a carry are named, because a reader has to open both to see which moved"
    )
    assert set(c.claims_fault_classes) >= {"F13"}


def test_same_sheet_equality__does_not_claim_the_carry_class(fme) -> None:
    c = next(x for x in fme.candidates if _cls(x) == "same_sheet_equality")
    assert "F13" not in c.claims_fault_classes, (
        "there is no cross-sheet carry to desynchronise when both ends are on one sheet"
    )


def test_sum_identity__emits_a_tolerance_bearing_equality(fme) -> None:
    """A money row gets `tau(n) = 5n` units; a COUNT gets zero tolerance."""
    s = next(x for x in fme.candidates if _cls(x) == "sum_identity")
    assert s.tolerance == Tolerance(tau_units_per_summand=HALF_ULP)
    assert "<=" in s.expr, "the tolerance is in the expression as an integer band, not implied"
    assert "sum(" not in s.expr, "the band is written out; a host call would hide the summands"

    t = next(x for x in fme.candidates if _cls(x) == "tally_identity")
    assert t.tolerance is None, "a person is not a rounded quantity — NC-E08"


def test_tally_identity__claims_only_the_row_classes(fme) -> None:
    t = next(x for x in fme.candidates if _cls(x) == "tally_identity")
    assert set(t.claims_fault_classes) == {"F05", "F07", "F08"}
    assert not {"F01", "F02"} & set(t.claims_fault_classes), (
        "a tally sees rows appearing and disappearing and nothing about value magnitude"
    )


def test_membership__claims_F12_and_not_F10(fme) -> None:
    m = next(x for x in fme.candidates if _cls(x) == "membership")
    assert m.claims_fault_classes == ("F12",)
    assert "F10" not in m.claims_fault_classes, (
        "a LEGAL enum substituted for another legal enum passes a membership test by "
        "construction; claiming F10 would be the exact lie the field exists to prevent"
    )
    assert "template.vocab." in m.expr, "the vocabulary resolves from the TEMPLATE — NC-D01c"
    assert "filing.vocab" not in m.expr


def test_membership__admits_a_blank(fme) -> None:
    """A list validation constrains what MAY be entered, not that something must be."""
    m = next(x for x in fme.candidates if _cls(x) == "membership")
    assert 'c.v == ""' in m.expr, (
        "without the blank arm, an empty column fails a requirement nobody wrote — and "
        "`conditional_required` is the class for requirements"
    )


def test_numeric_bound__does_not_claim_the_scale_class(fme) -> None:
    n = next(x for x in fme.candidates if _cls(x) == "numeric_bound")
    assert set(n.claims_fault_classes) == {"F01", "F03"}
    assert "F02" not in n.claims_fault_classes, "a x10 on a positive value stays above `>= 0`"


def test_integer_bound__claims_the_rounding_class(fme) -> None:
    i = next(x for x in fme.candidates if _cls(x) == "integer_bound")
    assert set(i.claims_fault_classes) == {"F01", "F03", "F06"}


def test_date_bound__claims_only_the_date_class(fme) -> None:
    d = next(x for x in fme.candidates if _cls(x) == "date_bound")
    assert d.claims_fault_classes == ("F09",)


def test_conditional_required__does_not_translate_the_custom_condition() -> None:
    res = harvest(ITFS)
    c = next(x for x in res.candidates if _cls(x) == "conditional_required")
    assert c.claims_fault_classes == ("F05",)
    assert "NOT translate" in c.rationale, (
        "translating an arbitrary Excel condition into CEL would be a re-interpretation nobody "
        "qualified, and it would be invisible in the envelope"
    )


# --- the rules the harvest obeys ------------------------------------------------------------


def test_harvest__claims_are_a_pure_function_of_the_class(fme) -> None:
    twin = harvest(FME)
    a = {c.id: c.claims_fault_classes for c in fme.candidates}
    b = {c.id: c.claims_fault_classes for c in twin.candidates}
    assert a == b
    for c in fme.candidates:
        assert tuple(c.claims_fault_classes) in {tuple(v) for v in CLAIMS.values()}


def test_harvest__every_candidate_is_inside_the_admitted_subset_and_agrees_both_ways(fme) -> None:
    for c in fme.candidates:
        for slot in ("applicable", "expr", "witness"):
            check_subset(getattr(c, slot), slot=slot)
        check_declared_keys(c)


def test_harvest__every_candidate_carries_an_obligation_and_declares_why_it_cites_no_statute(fme) -> None:
    for c in fme.candidates:
        assert c.obligation_source == "TEMPLATE"
        assert c.obligation_id.startswith("OBL-TEMPLATE-")
        assert c.clause is None
        assert c.clause_absent_reason


def test_harvest__the_weak_pile_is_typed_and_counted(fme) -> None:
    assert fme.skipped, "FME has constructs outside the class set; a zero here would be suspicious"
    for s in fme.skipped:
        assert s.kind and s.sheet and s.ref and s.detail
    assert sum(fme.skips_by_kind.values()) == len(fme.skipped)


def test_skip_record__refuses_an_anonymous_skip() -> None:
    with pytest.raises(ValueError, match="coverage lie"):
        SkipRecord(kind="other_formula", sheet="S", ref="A1", detail="")


def test_harvest__cannot_fail_only_under_produce() -> None:
    """Every workbook in the pinned corpus harvests without raising, including the two zeroes."""
    for p in sorted(FIX.glob("*.xlsx")):
        res = harvest(p)
        assert res.template_sha256 and isinstance(res.candidates, tuple)


def test_harvest__a_template_with_no_formulas_still_publishes() -> None:
    res = harvest(EDR)
    assert len(res.candidates) == 1 and _cls(res.candidates[0]) == "membership"
    assert len(res.cells_reachable) == 1


def test_single_call__will_not_match_two_calls_and_a_plus() -> None:
    """The defect this replaced: a greedy `^NAME\\((.+)\\)$` matched a compound expression, and the
    harvest emitted an argument list that was really two calls."""
    assert single_call("SUM(A1:A5)", "SUM") == "A1:A5"
    assert single_call("SUM(A1:A5)+SUM(B1:B5)", "SUM") is None
    assert single_call('COUNTIF(G54:G63,"*Angel*") + COUNTIF(H1:H2,"x")', "COUNTIF") is None
    assert single_call('COUNTIF(G54:G63,"*Angel*")', "COUNTIF") == 'G54:G63,"*Angel*"'


def test_harvest__ids_and_bytes_are_a_pure_function_of_the_template(tmp_path) -> None:
    from cdfc.predicates.harvest import emit_envelopes

    a, b = harvest(ITFS), harvest(ITFS)
    assert [c.id for c in a.candidates] == [c.id for c in b.candidates]
    assert [code_sha256(c) for c in a.candidates] == [code_sha256(c) for c in b.candidates]
    pa = emit_envelopes(a, tmp_path / "one")
    pb = emit_envelopes(b, tmp_path / "two")
    assert [p.name for p in pa] == [p.name for p in pb]
    assert [p.read_bytes() for p in pa] == [p.read_bytes() for p in pb]


def test_harvest__the_claims_table_and_the_modules_agree() -> None:
    doc = (REPO / "docs" / "FAULT-CLAIMS.md").read_text(encoding="utf-8")
    for name, classes in CLAIMS.items():
        assert f"`{name}`" in doc, f"{name} is not in docs/FAULT-CLAIMS.md"
        assert f"`{' '.join(classes)}`" in doc, f"{name}'s claim in the doc differs from the module"


def test_harvest__unclaimed_classes_are_computed_not_asserted() -> None:
    claimed = {c for v in claimed_classes().values() for c in v}
    assert unclaimed_classes() == tuple(sorted(known_ids() - claimed))
    assert set(unclaimed_classes()) == {"F10", "F11", "F14"}
