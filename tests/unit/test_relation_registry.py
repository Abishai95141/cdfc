"""P9-B2 — the relation registry, its loader's refusals, and the authoring protocol as tests.

**Each refusal below corresponds to a step of the protocol, and each is the LOADER's.** A protocol
enforced by a reviewer's memory is a protocol that will be followed until the week somebody is
busy.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.relations.basis import BasisContamination, assert_single_basis, bases_of  # noqa: E402
from cdfc.probes.relations.registry import (  # noqa: E402
    CATALOGUE_SIZE,
    COMPLETED_PHASES,
    WEAKER_REVIEW,
    RelationError,
    catalogue_size,
    load,
    parse_row,
    resolve_builder,
    runnability,
)
from cdfc.verdict.reasons import ReasonCode  # noqa: E402
from cdfc.verdict.states import ItemState  # noqa: E402

REVIEW = REPO / "docs" / "RELATION-REVIEW.md"


def _row(**over) -> dict:
    base = {
        "id": "R-99", "title": "a relation", "necessity": "NECESSARY", "inputs": "FILING_ONLY",
        "bases": ["INVESTOR_SIDE"], "precondition": "has(filing.a.v)", "expr": "filing.a.v == 1",
        "witness": "[filing.a.__cell__]", "evidence": "a cell range in the pinned blank",
        "claims_fault_classes": ["F01"], "reviewed_by": ["someone"],
        "reviewed_at": "2026-08-14", "review_label": WEAKER_REVIEW,
    }
    base.update(over)
    return base


# --------------------------------------------------------------------------------
# the catalogue itself
# --------------------------------------------------------------------------------


def test_reg__the_catalogue_loads_and_its_size_is_a_measurement() -> None:
    specs = load()
    assert CATALOGUE_SIZE == catalogue_size() == len(specs)
    assert {s.id for s in specs} == {"R-01", "R-02", "R-03", "R-05", "R-06", "R-07"}


def test_reg__necessity_drives_the_state_and_there_is_no_third_path() -> None:
    by_id = {s.id: s for s in load()}
    assert by_id["R-02"].state_on_violation() is ItemState.FAIL
    assert by_id["R-03"].state_on_violation() is ItemState.INFORMATIONAL
    for s in load():
        assert s.state_on_violation() in (ItemState.FAIL, ItemState.INFORMATIONAL)


def test_reg__self_tests_are_never_reported_to_the_filer() -> None:
    for s in load():
        assert (s.inputs == "SELF_TEST") == (not s.reported_to_filer)


def test_reg__every_relation_carries_the_weaker_review_label() -> None:
    """There is no second person on this project. The rule for that case is followed exactly:
    one signature, the literal label, and the label rendered where the numbers are."""
    for s in load():
        assert s.single_signer
        assert s.review_label == WEAKER_REVIEW


def test_reg__the_weaker_label_travels_with_every_relation_derived_number() -> None:
    for page in ("P9-relation-runnability.md",):
        text = (REPO / "docs" / "measurements" / page).read_text(encoding="utf-8")
        assert WEAKER_REVIEW in text, f"{page} quotes relation-derived numbers without the label"
    assert WEAKER_REVIEW in REVIEW.read_text(encoding="utf-8")


def test_reg__unrunnable_relations_report_a_reason_and_are_not_omitted() -> None:
    """**Absence and `NOT_RUN` are different claims.** Only the second is a coverage
    declaration."""
    by_id = {s.id: s for s in load()}
    assert by_id["R-07"].unrunnable_reason() is ReasonCode.NR_INPUT_UNAVAILABLE_PRIOR_PERIOD
    assert by_id["R-06"].unrunnable_reason() is ReasonCode.NR_DEACTIVATED
    assert by_id["R-02"].unrunnable_reason() is None
    r = runnability()
    assert (r["total"], r["runnable"], r["unrunnable"]) == (6, 4, 2)


def test_reg__no_relation_is_permanently_pending() -> None:
    """The escape hatch a `subject_exists_at` field opens if nobody bounds it — the same one
    `ci/GATES.md` closes with a never-empty `demonstrable_red_at`."""
    for s in load():
        assert s.subject_exists_at, f"{s.id} names no phase"
    with pytest.raises(RelationError, match="permanently pending"):
        parse_row(_row(subject_exists_at="P99"))


def test_reg__relations_are_returned_in_catalogue_order() -> None:
    """Never in sorted or glob order: a relation set enumerated by `Path.glob` is ordered by the
    filesystem, which differs between CI runner images and would break `verify` for a reason
    nobody would look for."""
    assert [s.id for s in load()] == ["R-01", "R-02", "R-03", "R-05", "R-06", "R-07"]


# --------------------------------------------------------------------------------
# the loader's refusals, one per protocol step
# --------------------------------------------------------------------------------


def test_reg__step1_a_relation_without_evidence_does_not_load() -> None:
    with pytest.raises(RelationError, match="name the cell range"):
        parse_row(_row(evidence=""))


def test_reg__step2_an_expected_relation_must_name_its_note() -> None:
    with pytest.raises(RelationError, match="it is unfinished"):
        parse_row(_row(necessity="EXPECTED"))
    parse_row(_row(necessity="EXPECTED", guidance_note="the note"))


def test_reg__step3_every_relation_has_a_precondition() -> None:
    with pytest.raises(RelationError, match="written to make the relation pass"):
        parse_row(_row(precondition=""))


def test_reg__step4_bases_must_be_a_singleton() -> None:
    with pytest.raises(RelationError, match="SINGLETON"):
        parse_row(_row(bases=["LOOK_THROUGH", "NON_LOOK_THROUGH"]))
    with pytest.raises(RelationError, match="SINGLETON"):
        parse_row(_row(bases=[]))


def test_reg__step5_claims_fault_classes_is_declared_before_any_campaign() -> None:
    with pytest.raises(RelationError, match="not a denominator"):
        parse_row(_row(claims_fault_classes=[]))


def test_reg__step7_two_signatures_or_the_weaker_label() -> None:
    with pytest.raises(RelationError, match="one signer"):
        parse_row(_row(review_label=""))
    parse_row(_row(reviewed_by=["a", "b"], review_label=""))


def test_reg__a_self_test_reported_to_the_filer_does_not_load() -> None:
    with pytest.raises(RelationError, match="never reported to the filer"):
        parse_row(_row(inputs="SELF_TEST", reported_to_filer=True))


def test_reg__duplicate_ids_do_not_load(tmp_path) -> None:
    import yaml

    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump({"relations": [_row(), _row()]}), encoding="utf-8")
    with pytest.raises(RelationError, match="duplicate relation ids"):
        load(p)


def test_reg__a_builder_outside_the_package_is_refused() -> None:
    with pytest.raises(RelationError, match="outside `cdfc.probes.relations`"):
        resolve_builder("os.path:join")
    with pytest.raises(RelationError, match="module:function"):
        resolve_builder("nonsense")


# --------------------------------------------------------------------------------
# step 6 — the redundancy refusal, and it is the interesting one
# --------------------------------------------------------------------------------


def test_reg__R04_is_refused_because_the_harvest_already_asserts_it() -> None:
    """R-04 was drafted as *vocabulary closure resolved from the blank*. `P-0017` already asserts
    it, from the blank, so admitting R-04 would have inflated the before/after delta with a
    rename — NC-R07's mechanism committed by the author of the relation set.

    **This test fails if `P-0017` stops existing**, because the refusal would then have removed a
    real relation and left nothing in its place.
    """
    from cdfc.predicates.harvest import harvest

    fme = (
        REPO / "fixtures" / "prescribed"
        / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
    )
    res = harvest(fme)
    membership = [c for c in res.candidates if res.class_of[c.id] == "membership"]
    assert len(membership) == 20
    scheme_type = [c for c in membership if "dv_g54" in c.expr]
    assert len(scheme_type) == 1
    assert "template.vocab.n_1_introduction_g54" in scheme_type[0].expr
    assert "R-04" not in {s.id for s in load()}
    assert "R-04" in REVIEW.read_text(encoding="utf-8")


def test_reg__the_review_log_records_both_refusals() -> None:
    """The refusals are the evidence the protocol did anything."""
    text = REVIEW.read_text(encoding="utf-8")
    assert text.count("\n### ") >= 2
    assert "REFUSED at step 6" in text
    assert "inexpressible in the admitted subset" in text


# --------------------------------------------------------------------------------
# the basis guard
# --------------------------------------------------------------------------------


def test_rel__cross_basis_relation_is_refused() -> None:
    """A relation summing a Table 3.5 quantity and a Table 3.6 quantity is refused AT AUTHORING
    REVIEW by a named test, not caught in production."""
    with pytest.raises(BasisContamination, match="LOOK_THROUGH"):
        assert_single_basis("R-XX", ["3. Portfolio!C80", "3. Portfolio!C110"])


def test_rel__single_basis_relation_is_admitted() -> None:
    """The admission-side control. A guard that refused everything would pass the test above."""
    assert assert_single_basis("R-YY", ["3. Portfolio!C80", "3. Portfolio!C90"]) == frozenset(
        {"NON_LOOK_THROUGH"}
    )
    assert bases_of(["4. Investors!AA21", "4. Investors!G42"]) == frozenset({"INVESTOR_SIDE"})


def test_rel__every_admitted_relation_passes_the_basis_guard() -> None:
    for s in load():
        assert len(s.bases) == 1


# --------------------------------------------------------------------------------
# the builders
# --------------------------------------------------------------------------------


def test_partition__the_precondition_is_written_before_expr_and_refuses_an_empty_filing() -> None:
    """Non-degeneracy has two clauses and both are needed: present on every side, and at least
    one non-zero. An all-zero filing satisfies every partition identity by construction."""
    from cdfc.probes.relations import partition

    pre = partition.precondition()
    assert "has(" in pre
    assert "!= 0" in pre
    assert pre.count("has(") == 40, "ten schemes × four cells"


def test_partition__the_expression_compares_both_totals_of_every_scheme() -> None:
    from cdfc.probes.relations import partition

    e = partition.expr()
    assert e.count("==") == 20, "ten schemes × (amount, count)"
    assert "filing.n_4_investors.r21.caa.v == filing.n_4_investors.r42.cg.v" in e
    assert "filing.n_4_investors.r30.cab.v == filing.n_4_investors.r51.ch.v" in e


def test_partition__carries_no_tolerance_literal_at_all() -> None:
    """`_coerce` returns a non-integral value as TEXT, which is `NOT_RUN` at pre-flight, so every
    value this relation can see is a whole USD Million. **A relation with no tolerance literal
    cannot inherit the harvest's 1,000× unit defect.**"""
    from cdfc.probes.relations import partition

    for token in partition.expr().replace("(", " ").replace(")", " ").split():
        assert not token.isdigit(), f"{token} is a bare tolerance literal"


def test_schemes__counts_the_full_nine_member_vocabulary() -> None:
    from cdfc.probes.relations import schemes

    e = schemes.expr()
    assert e.count("? 1 : 0") == 10, "G54:G63"
    assert "template.vocab.n_1_introduction_g54" in e
    assert "filing.n_1_introduction.r17.cd.v ==" in e


def test_prior_period__uses_a_root_the_subset_refuses() -> None:
    """The stronger half of R-07's un-runnability: it is not expressible at all."""
    from cdfc.predicates.cel_profile import BOUND_ROOTS
    from cdfc.probes.relations import prior_period

    assert "prior." in prior_period.expr()
    assert "prior" not in BOUND_ROOTS


def test_selftest__the_denominator_relation_holds_on_every_prescribed_workbook() -> None:
    from cdfc.probes.relations.selftest import denominator_agrees

    fix = REPO / "fixtures" / "prescribed"
    for p in sorted(fix.glob("*.xlsx")):
        held, detail = denominator_agrees(p)
        assert held, f"{p.name}: {detail}"


def test_selftest__the_canary_relation_refuses_rather_than_passing_vacuously() -> None:
    """A self-test that passes by having nothing to check is the vacuous pass this layer exists
    to refuse, committed by the catcher."""
    from cdfc.probes.relations.selftest import SelfTestUnavailable, canary_population_agrees

    with pytest.raises(SelfTestUnavailable, match="P10-B1"):
        canary_population_agrees(None)


def test_reg__the_completed_phase_set_does_not_include_the_future() -> None:
    assert "P10" not in COMPLETED_PHASES
    assert "P9" in COMPLETED_PHASES
