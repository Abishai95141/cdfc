"""P4 — the negative controls for the predicate envelope, the CEL substrate and the harvest.

Every entry here ships with its admission-side twin. Without one, a check that rejects everything
scores perfectly: the guard goes red under injection because it goes red under everything.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.harvest_report import render_report  # noqa: E402
from cdfc.predicates.ast_walker import check_declared_keys, read_keys  # noqa: E402
from cdfc.predicates.canonical import code_sha256, envelope_projection  # noqa: E402
from cdfc.predicates.cel_profile import check_subset  # noqa: E402
from cdfc.predicates.envelope import EnvelopeSchemaError  # noqa: E402
from cdfc.predicates.errors import (  # noqa: E402
    DeclaredKeyUnread,
    SubsetViolation,
    UndeclaredKeyRead,
)
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.harvest_classes import CLAIMS  # noqa: E402
from cdfc.predicates.loader import (  # noqa: E402
    UnqualifiedPredicateError,
    load_candidate,
    load_predicate,
)

GOOD = REPO / "fixtures" / "predicates" / "good"
BROKEN = REPO / "fixtures" / "predicates" / "broken"
FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
ITFS = FIX / "ITFS_Monthly_report201220241626.xlsx"
P0041 = GOOD / "P-0041__scheme-type-membership.yaml"
P0007 = GOOD / "P-0007__intro-D17-integer-bound.yaml"


# --- NC-Q02 — the loader invariant, LIVE from P4 ------------------------------------------


def test_nc__Q02b_the_predicate_loader_refuses_an_unqualified_envelope() -> None:
    with pytest.raises(UnqualifiedPredicateError):
        load_predicate(BROKEN / "P-NC02__no-qualification.yaml")


def test_nc__Q02c_a_qualified_predicate_does_load() -> None:
    """THE ADMISSION-SIDE TWIN, impossible before P4 because the schema did not exist."""
    p = load_predicate(P0007)
    assert p.qualification is not None and p.state


# --- NC-Q41 — a field leaves the canonical serialisation ------------------------------------


def test_nc__Q41_every_record_field_is_inside_the_digest() -> None:
    for env in (load_candidate(P0041), load_predicate(P0007)):
        import dataclasses

        projected = set(envelope_projection(env))
        for f in dataclasses.fields(env):
            assert f.name in projected, (
                f"{f.name} is not in the canonical projection, so it is not in the identity: a "
                "predicate could be re-issued with it changed under the same code_sha256"
            )


def test_nc__Q41b_two_envelopes_differing_only_in_a_claim_have_different_digests() -> None:
    """The admission side: the digest does distinguish envelopes it should distinguish."""
    import yaml

    raw = yaml.safe_load(P0041.read_text(encoding="utf-8"))
    a = load_candidate(raw)
    b = load_candidate({**raw, "claims_fault_classes": ["F12", "F05"]})
    assert code_sha256(a) != code_sha256(b)


# --- NC-Q42 — the two directions of the both-ways check are distinguishable ------------------


def test_nc__Q42_the_two_key_mismatches_raise_different_types() -> None:
    with pytest.raises(UndeclaredKeyRead):
        check_declared_keys(load_candidate(BROKEN / "P-NC04a__reads-undeclared.yaml"))
    with pytest.raises(DeclaredKeyUnread):
        check_declared_keys(load_candidate(BROKEN / "P-NC04b__declares-unread.yaml"))


def test_nc__Q42b_a_correct_envelope_raises_neither() -> None:
    """The admission side. A check that always raises satisfies the test above."""
    check_declared_keys(load_candidate(P0041))
    check_declared_keys(load_predicate(P0007))


# --- NC-Q43 — the subset walker actually walks ----------------------------------------------


BANNED_FORMS = (
    "filing.rows.all(r, r.sub.all(s, s.x > 0))",
    'filing.a.matches("^x")',
    "dyn(filing.a) == 1",
    "filing.a == 1.5",
    "other.a == 1",
)


def test_nc__Q43_a_banned_construct_is_refused() -> None:
    """Deliberately a loop rather than a `parametrize`.

    The sweep maps guard results BY NODE ID, and a parametrised test's node ids carry a `[case]`
    suffix — so the catalogue would have to name each case, and adding a banned form would
    silently leave the new case outside the declared exact set.
    """
    for src in BANNED_FORMS:
        with pytest.raises(SubsetViolation):
            check_subset(src, slot="expr")


def test_nc__Q43d_a_flat_comprehension_is_admitted() -> None:
    """The admission-side twin: the walker is not simply rejecting everything."""
    check_subset("filing.rows.all(r, r.x > 0)", slot="expr")
    check_subset("filing.rows.filter(r, r.x == 0).map(r, r.__cell__)", slot="witness")


# --- NC-Q44 — key extraction is structural, not lexical --------------------------------------


def test_nc__Q44_the_comprehension_binding_is_never_a_document_root() -> None:
    keys = read_keys("filing.rows.all(r, r.x in template.v.k)", slot="expr")
    assert "r.x" not in keys, "a lexical pass reports the binding as a root"
    assert "filing.rows[*].x" in keys, "and loses the [*] that says the key is a column"


def test_nc__Q44c_both_roots_are_reported() -> None:
    """The admission-side twin: the walker reads BOTH documents, not just the filing."""
    keys = read_keys("filing.rows.all(r, r.x in template.v.k)", slot="expr")
    assert {"filing.rows[*].x", "template.v.k"} == set(keys)


# --- NC-Q45 — the total never renders without its distribution --------------------------------


def test_nc__Q45_the_distribution_renders_beside_the_total() -> None:
    results = [harvest(ITFS), harvest(FME)]
    doc = render_report(results)
    for r in results:
        assert f"`{r.template_sha256[:8]}`" in doc, (
            "a workbook is missing from the rendered distribution; the total alone reads as "
            "breadth when the distribution is concentrated"
        )
    assert "Concentration:" in doc


def test_nc__Q45b_the_total_itself_still_renders() -> None:
    """The admission side: the fix is not to delete the total."""
    doc = render_report([harvest(ITFS)])
    assert "| **total** |" in doc


# --- NC-Q46 — the weak pile is counted, not dropped --------------------------------------------


def test_nc__Q46_a_construct_outside_the_class_set_is_recorded() -> None:
    res = harvest(FME)
    assert res.skipped, "FME carries constructs the class set cannot express; none was recorded"
    assert res.skips_by_kind.get("function_outside_vocabulary", 0) > 0
    for s in res.skipped:
        assert s.sheet and s.ref and s.detail


def test_nc__Q46b_a_workbook_with_nothing_to_skip_records_nothing() -> None:
    """The admission side: the counter is not simply always non-zero."""
    res = harvest(FIX / "EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx")
    assert res.skipped == ()


# --- NC-Q47 — a clause-less candidate declares why ----------------------------------------------


def test_nc__Q47_a_template_obligation_must_declare_why_it_cites_no_statute() -> None:
    import yaml

    raw = yaml.safe_load(P0041.read_text(encoding="utf-8"))
    with pytest.raises(EnvelopeSchemaError, match="declare why"):
        load_candidate({**raw, "clause_absent_reason": None})


def test_nc__Q47b_every_harvested_candidate_declares_why() -> None:
    """280-style instance count: the guard fires on every harvested candidate, not zero."""
    res = harvest(FME)
    assert res.candidates
    for c in res.candidates:
        assert c.obligation_source == "TEMPLATE" and c.clause_absent_reason


# --- NC-Q48 — the claim is a pure function of the class ------------------------------------------


def test_nc__Q48_claims_precede_the_campaign_and_do_not_vary_per_predicate() -> None:
    res = harvest(FME)
    by_class: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
    for c in res.candidates:
        by_class.setdefault(tuple(c.claims_fault_classes), set()).add(tuple(c.claims_fault_classes))
    declared = {tuple(v) for v in CLAIMS.values()}
    for claim in by_class:
        assert claim in declared, (
            f"{claim} is not any harvest class's declared constant, so it was derived per "
            "predicate — which is the kill vector choosing the denominator"
        )


def test_nc__Q48b_the_declared_claims_are_non_empty_and_resolve() -> None:
    """The admission side: the classes do declare claims, and every member resolves."""
    from cdfc.predicates.fault_model import known_ids

    assert CLAIMS
    for name, classes in CLAIMS.items():
        assert classes, f"{name} claims nothing"
        assert set(classes) <= known_ids()


# --- NC-Q49 — the host functions -------------------------------------------------------------------


def test_nc__Q49_reg_resolves_never_answers_without_a_snapshot() -> None:
    from cdfc.predicates.host_fns import HostFnRegistry, SnapshotMissing
    from cdfc.predicates.host_fns import reg_resolves as mod

    reg = HostFnRegistry()
    mod.bind_registry(reg)
    with pytest.raises(SnapshotMissing):
        mod.reg_resolves("IFSCA-FME-001")


def test_nc__Q49b_with_a_snapshot_bound_it_answers() -> None:
    """The admission side."""
    from cdfc.predicates.host_fns import HostFnRegistry
    from cdfc.predicates.host_fns import reg_resolves as mod

    reg = HostFnRegistry()
    reg.bind_snapshot("deadbeef", {"IFSCA-FME-001": True})
    mod.bind_registry(reg)
    assert str(mod.reg_resolves("IFSCA-FME-001")) == "TRUE"


def test_nc__Q49c_nav_interval_keeps_its_third_value() -> None:
    from cdfc.predicates.host_fns import UNDERSPECIFIED
    from cdfc.predicates.host_fns.nav_interval import nav_interval

    assert str(nav_interval("Restricted", "Close-ended", "NA")) == UNDERSPECIFIED, (
        "a two-valued nav_interval has to pick a frequency where the regulator gave none, and "
        "the report then presents our guess as the rule"
    )


def test_nc__Q49d_nav_interval_still_answers_where_the_regulation_determines_it() -> None:
    """The admission side: it has not become UNDERSPECIFIED for everything."""
    from cdfc.predicates.host_fns.nav_interval import nav_interval

    assert str(nav_interval("Retail", "Open-ended", "NA")) == "P1M"
