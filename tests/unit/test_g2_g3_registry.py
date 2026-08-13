"""P7-B3/B4 — G2's two bars, G3's two arms, the ILP, and the registry."""

from __future__ import annotations

import dataclasses
import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.registry import (  # noqa: E402
    INTERNAL_PREFIX,
    LEAF_PREFIX,
    UNSIGNED,
    UNSIGNED_BADGE,
    Registry,
    UnqualifiedPredicate,
    registry_root,
)
from cdfc.qualify import g2_kill, g3_degeneracy, ilp  # noqa: E402
from cdfc.qualify.baselines import b1_invariants, b2_degenerate  # noqa: E402
from cdfc.qualify.campaign_store import load as load_campaign  # noqa: E402
from cdfc.qualify.cel_smt import translate  # noqa: E402
from cdfc.qualify.domain import load as load_domain  # noqa: E402
from cdfc.qualify.errors import (  # noqa: E402
    ApparatusError,
    UnexercisedClaimError,
    UnsignedAdmissionError,
)
from cdfc.qualify.random_flagger import DegenerateBaseline, adjusted_precision, f1  # noqa: E402

FME = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
CAMPAIGN = "fme-v3-seed20260810"


@pytest.fixture(scope="module")
def world():
    r = harvest(FME)
    stored = load_campaign(CAMPAIGN, REPO / "reports/campaigns")
    return r, stored


def _cand(r, pid):
    return next(c for c in r.candidates if c.id == pid)


# --- G2 ------------------------------------------------------------------------------------


def test_g2__both_ratios_render_together(world):
    """Every render path emitting `kr_claimed` emits `kr_all_classes` in the same string."""
    r, stored = world
    bl = g2_kill.BaselineResult(per_baseline={"B0": frozenset()})
    killer = next(c for c in r.candidates if stored.mutants(c.id))
    out = g2_kill.check(killer, stored, bl, bar=g2_kill.KillBar.EXPERIMENT, repo=REPO)
    assert "kr_claimed" in out.measured and "kr_all_classes" in out.measured
    line = g2_kill.render(out.measured)
    assert "kr_claimed" in line and "kr_all_classes" in line
    assert "/" in out.measured["kr_claimed"], "a ratio is TWO INTEGERS, never a rounded float"


def test_g2__the_registry_bar_ignores_the_witness_set(world):
    """F1. The denominator is the DECLARED set, never the classes that happened to kill.

    Asserted on the CALL GRAPH as well as on the number: `g2_kill` must never read a witness's
    fault class to build a denominator.
    """
    import ast

    r, stored = world
    src = (REPO / "src/cdfc/qualify/g2_kill.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "fault_class" not in attrs, (
        "g2_kill reads FaultWitness.fault_class — the numerator choosing its denominator, at the "
        "gate built to catch exactly that"
    )
    killer = next(c for c in r.candidates if stored.mutants(c.id))
    bl = g2_kill.BaselineResult(per_baseline={"B0": frozenset()})
    out = g2_kill.check(killer, stored, bl, bar=g2_kill.KillBar.EXPERIMENT, repo=REPO)
    k, o = out.measured["kr_claimed"].split("/")
    declared = set(killer.claims_fault_classes)
    assert int(o) == sum(stored.observable(c) for c in declared)


def test_g2__an_unexercised_claim_raises(world):
    """A claimed class with `O == 0` on this campaign. Claiming F11 while the observability filter
    reports zero IS the F19 failure."""
    from cdfc.qualify.campaign import Campaign, ClassTally
    from cdfc.qualify.campaign_store import StoredCampaign

    r, stored = world
    # EVERY class in the real campaign was exercised, so the zero is CONSTRUCTED rather than
    # skipped. A guard that skips when the corpus does not happen to contain its subject is a
    # guard with no information in it, which this project counts as evidence of nothing.
    blinded = StoredCampaign(
        campaign=Campaign(
            campaign_id="constructed-F11-unobservable",
            by_fault_class={**{k: v for k, v in stored.campaign.by_fault_class.items()},
                            "F11": ClassTally(G=8, U=8, I=0, O=0, R=0, K=0)},
        ),
        kills_by_predicate=stored.kills_by_predicate,
        mutants_by_predicate=stored.mutants_by_predicate,
        class_of_mutant=stored.class_of_mutant,
        commit=stored.commit, n_killed_rows=stored.n_killed_rows,
    )
    assert blinded.observable("F11") == 0
    victim = dataclasses.replace(_cand(r, "P-0001"), claims_fault_classes=("F11",))
    bl = g2_kill.BaselineResult(per_baseline={"B0": frozenset()})
    with pytest.raises(UnexercisedClaimError, match="F19"):
        g2_kill.check(victim, blinded, bl, bar=g2_kill.KillBar.EXPERIMENT, repo=REPO)


def test_g2__two_bars_are_two_numbers(world):
    """The same campaign, the same predicate, two different questions and two different answers."""
    r, stored = world
    killer = next(c for c in r.candidates if stored.mutants(c.id))
    bl = g2_kill.BaselineResult(per_baseline={"B0": frozenset()})
    exp = g2_kill.check(killer, stored, bl, bar=g2_kill.KillBar.EXPERIMENT, repo=REPO)
    reg = g2_kill.check(killer, stored, bl, bar=g2_kill.KillBar.REGISTRY, repo=REPO)
    assert exp.passed, "it fires, so it clears the experiment bar"
    assert not reg.passed and reg.reason == g2_kill.Reason.BELOW_REGISTRY_BAR
    assert exp.measured["kr_claimed"] == reg.measured["kr_claimed"], "one measurement, two bars"


def test_g2__a_baseline_never_competes_with_the_candidate(world):
    """The defect the funnel found on its first run: B0 is drawn from this repository's own
    formula-derived classes, so a `sum_identity` candidate is IN B0 and scored a marginal kill of
    zero against itself."""
    r, stored = world
    killer = next(c for c in r.candidates
                  if stored.mutants(c.id) and r.class_of[c.id] == "sum_identity")
    self_including = g2_kill.BaselineResult(per_baseline={"B0": stored.mutants(killer.id)})
    out = g2_kill.check(killer, stored, self_including, bar=g2_kill.KillBar.EXPERIMENT, repo=REPO)
    assert out.measured["marginal_kill"]["B0"] > 0, (
        "the candidate must be removed from the baseline before the difference is taken"
    )


# --- G3, the proof arm ---------------------------------------------------------------------


def test_g3__trivially_true_and_always_flag_rejected(world):
    r, _stored = world
    dom = load_domain(REPO / "domain-policy-v1.json")
    base = _cand(r, "P-0041")
    t = g3_degeneracy.proof_arm(dataclasses.replace(base, expr="true"), dom,
                                harvest_class="sum_identity")
    assert not t.passed and t.measured["verdict"] == "trivially_true"
    f = g3_degeneracy.proof_arm(dataclasses.replace(base, expr="false"), dom,
                                harvest_class="sum_identity")
    assert not f.passed and f.measured["verdict"] == "always_flag"


def test_g3__unknown_is_unproven_and_does_not_earn_non_degenerate(world):
    """`unknown` never becomes `non_degenerate`, and it does NOT reject either: the empirical arm
    must then decide. Rejecting here would reject 47 of 349 predicates for a limitation of our own
    translator."""
    r, _stored = world
    dom = load_domain(REPO / "domain-policy-v1.json")
    membership = next(c for c in r.candidates if r.class_of[c.id] == "membership")
    o = g3_degeneracy.proof_arm(membership, dom, harvest_class="membership")
    assert o.measured["verdict"] == "unknown"
    assert o.measured["proved"] is False
    assert o.passed, "unproven is not rejected; the empirical arm decides"


def test_g3__a_pure_bound_is_unproven_while_the_policy_is_placeholder(world):
    r, _stored = world
    dom = load_domain(REPO / "domain-policy-v1.json")
    assert dom.is_placeholder
    bound = next(c for c in r.candidates if r.class_of[c.id] == "numeric_bound")
    o = g3_degeneracy.proof_arm(bound, dom, harvest_class="numeric_bound")
    assert o.measured["verdict"] == "unknown" and o.measured["proved"] is False
    assert "PLACEHOLDER" in str(o.measured["why"])


def test_smt__single_row_abstraction_is_not_used_for_subsumption(world):
    """Sound for triviality; NOT sound for subsumption, because it can couple rows across
    predicates. Asserted on the code path, not on an outcome."""
    r, _stored = world
    a = next(c for c in r.candidates if ".all(" in c.expr)
    b = next(c for c in r.candidates if ".all(" in c.expr and c.id != a.id)
    assert g3_degeneracy.subsumes(a, b) is None, (
        "a comprehension must not be decided by subsumption under the single-row abstraction"
    )


def test_smt__the_admitted_subset_is_measured_not_assumed(world):
    r, _stored = world
    translated = sum(1 for c in r.candidates if translate(c.expr) is not None)
    assert translated == 328, "the CEL->SMT coverage moved"
    assert len(r.candidates) - translated == 20


def test_smt__a_string_expression_is_untranslatable():
    assert translate('filing.a.v == "x"') is None
    assert translate("filing.a.v >= 0") is not None


# --- G3, the empirical arm ------------------------------------------------------------------


def test_g3e__a_control_fire_blocks_the_batch(world):
    """Exactly zero, and DERIVED rather than chosen. A control fire is an apparatus failure, so it
    raises rather than rejecting one predicate."""
    r, _stored = world
    clean = g3_degeneracy.CleanCorpusResult(n_filings=1, n_fired=0, control_spurious_fires=1,
                                            corpus_label="TEST")
    with pytest.raises(ApparatusError, match="blocks the whole admission batch"):
        g3_degeneracy.empirical_arm(_cand(r, "P-0041"), clean, (), n_sites=10,
                                    true_defective=5, flagged=3)


def test_g3e__firing_on_most_of_a_clean_corpus_is_rejected(world):
    r, _stored = world
    clean = g3_degeneracy.CleanCorpusResult(n_filings=10, n_fired=9, control_spurious_fires=0,
                                            corpus_label="TEST")
    out = g3_degeneracy.empirical_arm(_cand(r, "P-0041"), clean, (), n_sites=10,
                                      true_defective=5, flagged=3, correct=3)
    assert not out.passed and out.reason == g3_degeneracy.Reason.FIRES_ON_CLEAN


def test_random_flagger__clause_exhibit():
    """The published exhibit of the failure this module exists to catch: CLAUSE's best F1 over an
    80-cell table is 65.4 where a constant always-flag classifier scores 66.2.

    The split is computed from the published RATE, not from an integer count: 49.5% of 80 cells is
    39.6, so the published number is not realisable over 80 integer cells — which is itself worth
    saying rather than rounding away.
    """
    p = Decimal("0.495")
    always = (2 * p) / (1 + p)
    assert round(always * 100, 1) == Decimal("66.2")
    assert Decimal("65.4") < always * 100, "the constant classifier beats the published system"
    # and it scores exactly zero on adjusted precision
    assert adjusted_precision(flagged=80, true_defective=40, n=80, correct=40) == 0
    assert adjusted_precision(flagged=20, true_defective=40, n=80) == 0, "a random flagger scores 0"
    assert adjusted_precision(flagged=10, true_defective=40, n=80, correct=10) > 0
    assert f1(tp=1, fp=0, fn=0) == 1


def test_random_flagger__a_fully_defective_population_has_no_score():
    with pytest.raises(DegenerateBaseline):
        adjusted_precision(flagged=5, true_defective=10, n=10)


# --- the baselines ---------------------------------------------------------------------------


def test_b1__is_not_daikon_and_says_so():
    assert "NOT Daikon" in b1_invariants.NOT_DAIKON
    doc = b1_invariants.__doc__ or ""
    assert "THIS IS NOT DAIKON" in doc
    assert "OVERSTATEMENT" in doc or "OVERSTATES" in b1_invariants.NOT_DAIKON


def test_b1__mines_only_what_holds_on_every_observation():
    obs = [{"S!A1": Decimal(3)}, {"S!A1": Decimal(5)}]
    inv = {i.template for i in b1_invariants.mine(obs)}
    assert "nonneg" in inv and "integral" in inv
    assert "constant" not in inv, "3 and 5 are not one constant"
    assert "nonpos" not in inv


def test_b2__kills_a_blank_and_an_error_and_not_a_number():
    assert b2_degenerate.kills_edit("<c r='A1'/>")
    assert b2_degenerate.kills_edit("<c r='A1'><v></v></c>")
    assert b2_degenerate.kills_edit("<c r='A1'><v>#DIV/0!</v></c>")
    assert not b2_degenerate.kills_edit("<c r='A1'><v>42</v></c>")


# --- the ILP ---------------------------------------------------------------------------------


def test_ilp__ffr_constraint_absent_at_p7():
    assert ilp.P7_CONSTRAINTS == (ilp.Constraint.SUBSUMPTION,)
    with pytest.raises(ilp.UnavailableConstraint, match="blind-fill corpus arrives at P8"):
        ilp.select([], constraints=[ilp.Constraint.SUBSUMPTION, ilp.Constraint.SET_FFR],
                   subsumes=lambda a, b: False, cells_of={})


def test_ilp__an_undecided_implication_never_removes_a_predicate():
    class C:
        def __init__(self, i):
            self.id = i

    sel = ilp.select([C("a"), C("b")], subsumes=lambda a, b: None, cells_of={})
    assert sel.kept == ("a", "b") and not sel.removals


def test_ilp__every_removal_is_recorded():
    class C:
        def __init__(self, i):
            self.id = i

    sel = ilp.select([C("a"), C("b")], subsumes=lambda a, b: a.id == "a" and b.id == "b",
                     cells_of={"b": 12})
    assert sel.kept == ("a",)
    assert sel.removals[0].removed == "b" and sel.removals[0].subsumed_by == "a"
    assert sel.removals[0].cells_would_have_covered == 12


# --- the registry -----------------------------------------------------------------------------


def test_registry__merkle_domain_separation():
    import hashlib

    a, b = "aa" * 32, "bb" * 32
    root = registry_root([a, b])
    naive = hashlib.sha256(bytes.fromhex(a) + bytes.fromhex(b)).hexdigest()
    assert root != naive, "domain separation is not decoration"
    assert LEAF_PREFIX != INTERNAL_PREFIX


def test_registry__odd_node_promoted():
    five = [f"{i:02x}" * 32 for i in range(5)]
    assert len(registry_root(five)) == 64
    # promotion, not duplication: duplicating an odd node is the CVE-2012-2459 construction
    assert registry_root(five) != registry_root(five + [five[-1]])


def test_registry__root_is_order_invariant():
    import random

    hs = [f"{i:02x}" * 32 for i in range(9)]
    shuffled = hs[:]
    random.Random(7).shuffle(shuffled)
    assert registry_root(hs) == registry_root(shuffled)


def test_registry__append_only_and_load_requires_a_qualification(world):
    r, _stored = world
    reg = Registry()
    c = _cand(r, "P-0041")
    with pytest.raises(UnqualifiedPredicate):
        reg.load("P-0041", 1)
    row = reg.admit(c, {"g0": {}}, signer=UNSIGNED, signature=b"",
                    batch_manifest_sha256="m", admitted_at="2026-08-13")
    assert reg.load("P-0041", 1).code_sha256 == row.code_sha256
    before = reg.rows()[0]
    reg.admit(dataclasses.replace(c, version=2), {"g0": {}}, signer=UNSIGNED, signature=b"",
              batch_manifest_sha256="m", admitted_at="2026-08-14")
    assert reg.rows()[0] == before, "supersession is a NEW ROW; the old one is byte-unchanged"
    assert len(reg.rows()) == 2


def test_admission_requires_a_signature_or_the_literal_unsigned(world):
    r, _stored = world
    reg = Registry()
    c = _cand(r, "P-0041")
    with pytest.raises(UnsignedAdmissionError, match="no detached signature"):
        reg.admit(c, {}, signer="A. Human", signature=b"",
                  batch_manifest_sha256="m", admitted_at="2026-08-13")
    with pytest.raises(UnsignedAdmissionError, match="not a place to hide a signature"):
        reg.admit(c, {}, signer=UNSIGNED, signature=b"sig",
                  batch_manifest_sha256="m", admitted_at="2026-08-13")
    row = reg.admit(c, {}, signer=UNSIGNED, signature=b"",
                    batch_manifest_sha256="m", admitted_at="2026-08-13")
    assert not row.signed and row.badge() == UNSIGNED_BADGE
    signed = reg.admit(dataclasses.replace(c, version=2), {}, signer="A. Human", signature=b"sig",
                       batch_manifest_sha256="m", admitted_at="2026-08-13")
    assert signed.signed and signed.badge() == ""
