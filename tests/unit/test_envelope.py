"""P4-B1 — the predicate envelope, its digest, and the loader invariant."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.canonical import code_sha256, envelope_projection, jcs  # noqa: E402
from cdfc.predicates.envelope import (  # noqa: E402
    PREDICATE_STATES,
    Candidate,
    Clause,
    EnvelopeSchemaError,
    Predicate,
    Proviso,
    Tolerance,
)
from cdfc.predicates.fault_model import EXPECTED_CLASSES, fault_classes, known_ids  # noqa: E402
from cdfc.predicates.loader import (  # noqa: E402
    UnqualifiedPredicateError,
    dump,
    load_candidate,
    load_predicate,
)

GOOD = REPO / "fixtures" / "predicates" / "good"
BROKEN = REPO / "fixtures" / "predicates" / "broken"
P0041 = GOOD / "P-0041__scheme-type-membership.yaml"
P0007 = GOOD / "P-0007__intro-D17-integer-bound.yaml"


def _raw(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# --- the loader invariant ---------------------------------------------------------------


def test_load_predicate__missing_qualification_raises() -> None:
    with pytest.raises(UnqualifiedPredicateError) as e:
        load_predicate(BROKEN / "P-NC02__no-qualification.yaml")
    msg = str(e.value)
    assert "P-NC02__no-qualification.yaml" in msg, "the error must name the file it read"
    assert "qualification" in msg, "the error must name the missing key"


def test_load_candidate__missing_qualification_is_fine() -> None:
    """The positive control. Without it the loader is a reject-everything baseline."""
    c = load_candidate(P0041)
    assert isinstance(c, Candidate) and not isinstance(c, Predicate)
    assert c.id == "P-0041"


def test_load_predicate__a_qualified_envelope_loads() -> None:
    """The other admission side: a predicate that DOES load. NC-Q02's twin, live from P4."""
    p = load_predicate(P0007)
    assert isinstance(p, Predicate)
    assert p.qualification is not None and p.qualified_against is not None
    assert p.state in PREDICATE_STATES


def test_load_candidate__refuses_an_already_qualified_envelope() -> None:
    with pytest.raises(EnvelopeSchemaError, match="skipped the gates"):
        load_candidate(P0007)


def test_load_predicate__unknown_field_rejected() -> None:
    raw = _raw(P0007)
    raw["confidence"] = "high"
    with pytest.raises(EnvelopeSchemaError, match="unknown field"):
        load_predicate(raw)


def test_load_predicate__unknown_field_rejected_at_every_depth() -> None:
    """additionalProperties:false inside clause.provisos[] — the depth a hand-written schema forgets."""
    raw = _raw(P0007)
    raw["obligation_source"] = "STATUTE"
    raw["clause_absent_reason"] = None
    raw["clause"] = {
        "instrument": "IFSCA (Fund Management) Regulations, 2025",
        "eId": "reg-51-1",
        "span": [0, 10],
        "quote": "in such manner as specified",
        "provisos": [
            {"text": "unless the Authority specifies", "disposal": "DECLARED",
             "emits": "no_predicate.no_obligation_specified", "span": [0, 4], "certainty": "high"}
        ],
    }
    with pytest.raises(EnvelopeSchemaError, match="unknown field"):
        load_predicate(raw)


def test_load_predicate__severity_tier_cannot_be_hand_set_on_a_candidate() -> None:
    """A Candidate has no such attribute at all: an AttributeError, not a validation error."""
    c = load_candidate(P0041)
    assert not hasattr(c, "severity_tier")
    # A frozen `slots=True` dataclass refuses the assignment from its generated __setattr__;
    # CPython surfaces that as TypeError rather than FrozenInstanceError. Either way the tier
    # cannot be attached to an unqualified envelope, which is the property under test.
    with pytest.raises((AttributeError, TypeError)):
        c.severity_tier = "BLOCKING"  # type: ignore[attr-defined]
    assert not hasattr(c, "severity_tier")


# --- D-P4-06: claims_fault_classes ------------------------------------------------------


def test_envelope__claims_fault_classes_is_required_and_non_empty() -> None:
    raw = _raw(P0041)
    raw["claims_fault_classes"] = []
    with pytest.raises(EnvelopeSchemaError) as e:
        load_candidate(raw)
    assert "claims_fault_classes" in str(e.value)


def test_envelope__narrowing_a_claim_changes_the_digest() -> None:
    """Narrowing after a campaign produces a DIFFERENT predicate, not a softer bar."""
    raw = _raw(P0007)
    for k in ("qualification", "qualified_against", "severity_tier", "state", "withdrawn_reason"):
        del raw[k]
    wide = load_candidate(raw)
    narrow = load_candidate({**raw, "claims_fault_classes": ["F01"]})
    assert set(narrow.claims_fault_classes) < set(wide.claims_fault_classes)
    assert code_sha256(narrow) != code_sha256(wide)


def test_envelope__claims_are_drawn_from_the_pinned_fault_model() -> None:
    raw = _raw(P0041)
    raw["claims_fault_classes"] = ["F99"]
    with pytest.raises(EnvelopeSchemaError, match="pinned fault model"):
        load_candidate(raw)


def test_fault_model__parses_the_pinned_document() -> None:
    classes = fault_classes()
    assert len(classes) == EXPECTED_CLASSES
    assert classes["F11"].name == "formula override", (
        "F11 is named by id in P9's exit gate and may not be renumbered"
    )
    assert known_ids() >= {"F01", "F10", "F12", "F13", "F14"}


# --- D-P4-07 / C2: clause_absent_reason -------------------------------------------------


def test_envelope__clauseless_candidate_declares_why() -> None:
    raw = _raw(P0041)
    raw["clause_absent_reason"] = None
    with pytest.raises(EnvelopeSchemaError, match="declare why it cites no statute"):
        load_candidate(raw)


def test_envelope__a_cited_clause_may_not_also_carry_an_absence_reason() -> None:
    """The field is an EXPLANATION OF AN ABSENCE, not an annotation.

    Annotating a candidate that does cite a clause would make the field's count meaningless,
    and the count is half of the published obligation-coverage pair.
    """
    raw = _raw(P0041)
    raw["obligation_source"] = "STATUTE"
    raw["clause"] = {"instrument": "X", "eId": "e", "span": [0, 1], "quote": "q", "provisos": []}
    with pytest.raises(EnvelopeSchemaError, match="explains an ABSENCE"):
        load_candidate(raw)


def test_envelope__a_template_obligation_may_not_carry_a_clause() -> None:
    raw = _raw(P0041)
    raw["clause"] = {"instrument": "X", "eId": "e", "span": [0, 1], "quote": "q", "provisos": []}
    with pytest.raises(EnvelopeSchemaError, match="cites no statutory clause"):
        load_candidate(raw)


def test_envelope__a_statute_obligation_must_carry_its_clause() -> None:
    raw = _raw(P0041)
    raw["obligation_source"] = "STATUTE"
    raw["clause_absent_reason"] = None
    with pytest.raises(EnvelopeSchemaError, match="must carry the Clause"):
        load_candidate(raw)


def test_envelope__obligation_id_is_required_for_every_candidate() -> None:
    raw = _raw(P0041)
    raw["obligation_id"] = ""
    with pytest.raises(EnvelopeSchemaError, match="obligation_id"):
        load_candidate(raw)


# --- the digest ---------------------------------------------------------------------------


def test_code_sha256__is_key_order_invariant() -> None:
    raw = _raw(P0041)
    shuffled = dict(reversed(list(raw.items())))
    assert list(shuffled) != list(raw)
    assert code_sha256(load_candidate(shuffled)) == code_sha256(load_candidate(raw))


def test_dump__roundtrips_byte_identical() -> None:
    c = load_candidate(P0041)
    assert jcs(dump(c)) == jcs(dump(load_candidate(dump(c))))


def test_envelope_projection__distinguishes_a_candidate_from_a_predicate() -> None:
    """Otherwise an unqualified envelope could inherit a qualified one's admission record."""
    p = load_predicate(P0007)
    raw = _raw(P0007)
    for k in ("qualification", "qualified_against", "severity_tier", "state", "withdrawn_reason"):
        del raw[k]
    c = load_candidate(raw)
    assert envelope_projection(c)["__envelope_type__"] == "Candidate"
    assert envelope_projection(p)["__envelope_type__"] == "Predicate"
    assert code_sha256(c) != code_sha256(p)


# --- D-P4-01 -------------------------------------------------------------------------------


def test_predicate_state__has_exactly_four_members() -> None:
    assert PREDICATE_STATES == ("ACTIVE", "PROVISIONAL", "QUARANTINED", "WITHDRAWN")
    assert "REJECTED" not in PREDICATE_STATES, (
        "D-P4-01: a rejected candidate never acquires a predicate_id; it becomes a rejection "
        "row keyed by candidate_sha256"
    )


def test_predicate__withdrawn_requires_a_reason_and_the_reverse() -> None:
    raw = _raw(P0007)
    raw["state"] = "WITHDRAWN"
    with pytest.raises(EnvelopeSchemaError, match="WITHDRAWN with no reason"):
        load_predicate(raw)
    raw["state"] = "ACTIVE"
    raw["withdrawn_reason"] = "rule_amended"
    with pytest.raises(EnvelopeSchemaError, match="withdrawn_reason but is ACTIVE"):
        load_predicate(raw)


# --- the record's other refusals ------------------------------------------------------------


def test_envelope__empty_schema_keys_is_refused() -> None:
    """A predicate declaring no footprint settles no cells; the fraction would count it free."""
    raw = _raw(P0041)
    raw["schema_keys"] = []
    with pytest.raises(EnvelopeSchemaError, match="settles"):
        load_candidate(raw)


def test_envelope__an_empty_slot_is_refused() -> None:
    for slot in ("applicable", "expr", "witness", "reason_if_inapplicable"):
        raw = _raw(P0041)
        raw[slot] = ""
        with pytest.raises(EnvelopeSchemaError):
            load_candidate(raw)


def test_tolerance__is_an_integer_count_never_a_float() -> None:
    with pytest.raises(EnvelopeSchemaError, match="integer count"):
        Tolerance(tau_units_per_summand=5.0)  # type: ignore[arg-type]
    assert Tolerance(tau_units_per_summand=5).tau_units_per_summand == 5


def test_proviso__declared_must_name_its_emission() -> None:
    raw = _raw(P0041)
    raw["obligation_source"] = "STATUTE"
    raw["clause_absent_reason"] = None
    raw["clause"] = {
        "instrument": "X", "eId": "e", "span": [0, 1], "quote": "q",
        "provisos": [{"text": "t", "disposal": "DECLARED", "emits": None, "span": [0, 1]}],
    }
    with pytest.raises(EnvelopeSchemaError, match="must name what it emits"):
        load_candidate(raw)


def test_clause_and_proviso_construct_directly() -> None:
    """A value assertion beside the refusals: the lawful shape does build."""
    cl = Clause(
        instrument="IFSCA (Fund Management) Regulations, 2025",
        eId="reg-51-1",
        span=(120, 260),
        quote="in such manner as specified by the Authority",
        provisos=(Proviso(text="p", disposal="IMPLEMENTED", emits=None, span=(0, 1)),),
    )
    assert cl.provisos[0].disposal == "IMPLEMENTED"


def test_projection_is_deep_copy_safe() -> None:
    c = load_candidate(P0041)
    before = copy.deepcopy(envelope_projection(c))
    envelope_projection(c)["schema_keys"].append("filing.injected")
    assert envelope_projection(c) == before, "the projection must not alias the record"
