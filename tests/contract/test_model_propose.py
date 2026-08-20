"""LAYER 2 — the proposer's contract. NO NETWORK: every test supplies a transport.

The point of these is not that the model is good. It is that a proposal is DATA, that a proposal
about something the model was not shown is discarded loudly, and that a transport failure never
looks like a clean negative result.
"""

from __future__ import annotations

import json

import pytest

from cdfc.model.propose import ProposalSet, ProposerError, parse, propose

PROV = [("reg_0008", "An entity shall at all times comply with the net worth requirements.")]
FIELDS = [("8. Compliance Status!C6", "The Net worth requirement has been complied with")]


def _reply(obj) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(obj)}]}


def test_propose__returns_candidates_as_DATA_with_no_verdict():
    got = propose(PROV, FIELDS, transport=lambda _p: _reply({"proposals": [
        {"provision_eid": "reg_0008", "field_ref": "8. Compliance Status!C6",
         "quote": "shall at all times comply with the net worth requirements",
         "reason": "the field certifies the obligation this provision creates", "kind": "disclosure"}]}))
    assert isinstance(got, ProposalSet)
    p = got.proposals[0]
    assert p.provision_eid == "reg_0008"
    # a proposal carries NO verdict and NO admitted flag
    assert not hasattr(p, "admitted") and not hasattr(p, "score")
    assert got.counts()["provisions_offered"] == 1     # the denominator travels with it


def test_propose__discards_a_proposal_about_something_it_was_never_shown():
    """A hallucinated eId cannot be adjudicated, only discarded — and never silently."""
    got = propose(PROV, FIELDS, transport=lambda _p: _reply({"proposals": [
        {"provision_eid": "reg_9999", "field_ref": "8. Compliance Status!C6",
         "quote": "x", "reason": "r", "kind": "disclosure"},
        {"provision_eid": "reg_0008", "field_ref": "Sheet!ZZ99", "quote": "x", "reason": "r", "kind": "disclosure"},
        {"provision_eid": "reg_0008", "field_ref": "8. Compliance Status!C6",
         "quote": "   ", "reason": "r", "kind": "disclosure"}]}))
    assert got.proposals == ()
    assert got.raw_blocks == 3 and len(got.malformed) == 3
    assert "was not offered" in got.malformed[0]
    assert "G-QUOTE has nothing to locate" in got.malformed[2]


def test_propose__a_transport_failure_is_NOT_an_empty_proposal_set():
    def boom(_p):
        raise OSError("connection refused")
    with pytest.raises(ProposerError, match="NOT an empty result"):
        propose(PROV, FIELDS, transport=lambda p: (_ for _ in ()).throw(OSError("refused")))


def test_propose__unparseable_json_raises_rather_than_returning_zero():
    with pytest.raises(ProposerError, match="not JSON"):
        parse("I think regulation 8 binds to C6.", model="m", provisions=PROV, fields=FIELDS)


def test_propose__refuses_an_empty_offer():
    with pytest.raises(ProposerError, match="was shown nothing"):
        propose([], FIELDS, transport=lambda _p: _reply({"proposals": []}))


def test_propose__refuses_to_run_with_no_key_and_no_transport():
    import os
    old = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        with pytest.raises(ProposerError, match="no API key"):
            propose(PROV, FIELDS)
    finally:
        if old is not None:
            os.environ["ANTHROPIC_API_KEY"] = old


def test_propose__never_puts_a_credential_in_a_proposal_or_an_error():
    seen = {}
    def t(p):
        seen["payload"] = p
        return _reply({"proposals": []})
    got = propose(PROV, FIELDS, api_key="sk-secret-do-not-leak", transport=t)
    assert "sk-secret" not in json.dumps(seen["payload"])
    assert "sk-secret" not in json.dumps([p.as_canonical_obj() for p in got.proposals])


def test_propose__the_model_may_propose_nothing_and_that_is_a_valid_answer():
    got = propose(PROV, FIELDS, transport=lambda _p: _reply({"proposals": []}))
    assert got.proposals == () and got.raw_blocks == 0 and got.malformed == ()


def test_propose__is_banned_from_the_verdict_closure():
    """`cdfc.model` is BANNED_IN_VERDICT as a PACKAGE. This asserts the ban is still declared;
    `test_nc__A04a` walks the actual import graph."""
    from tests.negative.importgraph import BANNED_IN_VERDICT, VERDICT_ROOTS

    assert "cdfc.model" in BANNED_IN_VERDICT
    assert not any(r.startswith("cdfc.model") for r in VERDICT_ROOTS)


# --- C3: the shape LAYER 3 consumes. Added 20 Aug 2026 ----------------------------------------
#
# `cdfc.model` was ORPHANED -- nothing under src/ imported it -- and the reason was structural,
# not an oversight. `evidence.proposal.Proposal` REQUIRES a `kind` from a closed vocabulary and
# uses `terms` for G-VOCAB and `refers_to` for G-XREF. A BindingProposal carrying none of them
# could not be loaded by the driver, so LAYER 2 emitted something LAYER 3 could not eat.


def test_propose__a_kind_outside_the_closed_vocabulary_is_DISCARDED_not_coerced() -> None:
    """Coercing to a default would adjudicate a claim the model never made."""
    got = propose(PROV, FIELDS, transport=lambda _p: _reply({"proposals": [
        {"provision_eid": "reg_0008", "field_ref": "8. Compliance Status!C6",
         "quote": "shall at all times comply with the net worth requirements",
         "reason": "r", "kind": "vibes"}]}))
    assert not got.proposals, "a proposal with an unlisted kind must not survive"
    assert got.malformed, "and the discard must be COUNTED, not silent"
    assert "vibes" in got.malformed[0] and "closed vocabulary" in got.malformed[0]


def test_propose__a_missing_kind_is_refused_because_absent_is_not_a_default() -> None:
    got = propose(PROV, FIELDS, transport=lambda _p: _reply({"proposals": [
        {"provision_eid": "reg_0008", "field_ref": "8. Compliance Status!C6",
         "quote": "shall at all times comply with the net worth requirements",
         "reason": "r"}]}))
    assert not got.proposals
    assert got.malformed and "kind" in got.malformed[0]


def test_propose__evidence_rows_are_exactly_what_the_driver_loads() -> None:
    """The round trip that was missing: LAYER 2 output -> `evidence.proposal.parse` -> Proposal."""
    from cdfc.evidence.proposal import parse as evidence_parse

    got = propose(PROV, FIELDS, transport=lambda _p: _reply({"proposals": [
        {"provision_eid": "reg_0008", "field_ref": "8. Compliance Status!C6",
         "quote": "shall at all times comply with the net worth requirements",
         "reason": "r", "kind": "enumeration", "terms": ["Yes", "No"],
         "refers_to": ["reg_0009"]}]}))
    assert len(got.proposals) == 1
    rows = got.as_evidence_rows()
    ps = evidence_parse(rows, source="<test>")
    assert len(ps.proposals) == 1
    p = ps.proposals[0]
    assert p.eid == "reg_0008"
    assert p.field_ref == "8. Compliance Status!C6"
    assert p.terms == ("Yes", "No"), "G-VOCAB must receive the terms the model proposed"
    assert p.refers_to == ("reg_0009",), "G-XREF must receive the cross-references"
    assert p.note == "r", "the model's words are retained as note, which never reaches a verdict"
