"""P11-B1 — the statement, the policy constant, and the DSSE envelope."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest import dsse, ed25519  # noqa: E402
from cdfc.attest.policy import POLICY_VALIDITY_DAYS, TimeNotAnInput, expires_for  # noqa: E402
from cdfc.attest.statement import STATEMENTS, StatementError, Subject  # noqa: E402
from tools.attest_validate import validate  # noqa: E402
from tests.contract.attest_fixtures import sample_statement  # noqa: E402


# --- the policy constant ---------------------------------------------------------------------


def test_stmt__expires_is_92_days_after_time_verified() -> None:
    """**The specification's own worked example**, and it is what fixes the constant at 92.

    `plan/05` gives `2026-08-14 → 2026-11-14` without naming the number of days. A constant
    reverse-engineered from a published example is a constant somebody can check; a constant
    chosen and then illustrated is not.
    """
    assert expires_for("2026-08-14T00:00:00Z") == "2026-11-14T00:00:00Z"
    assert POLICY_VALIDITY_DAYS == 92


def test_stmt__expires_reads_no_clock() -> None:
    """A pure function of its argument. A single `now()` here makes every attestation differ from
    its own re-derivation and fails E2E-VERIFY for a reason that reads like clock skew."""
    import ast

    from cdfc.attest import policy

    src = Path(policy.__file__).read_text(encoding="utf-8")
    calls = {
        getattr(n.func, "attr", "")
        for n in ast.walk(ast.parse(src))
        if isinstance(n, ast.Call)
    }
    assert not (calls & {"now", "utcnow", "today", "time", "monotonic", "perf_counter"}), (
        f"a clock is read in the module that derives `expires`: {sorted(calls)}"
    )
    a = expires_for("2026-01-01T00:00:00Z")
    assert a == expires_for("2026-01-01T00:00:00Z")


def test_stmt__an_empty_time_verified_is_refused_not_defaulted() -> None:
    with pytest.raises(TimeNotAnInput) as e:
        expires_for("")
    assert "INPUT recorded in the manifest" in str(e.value)
    with pytest.raises(TimeNotAnInput):
        expires_for("not-a-date")


# --- the statement ----------------------------------------------------------------------------


def test_stmt__the_subject_is_both_documents() -> None:
    """A verdict against template v3 is meaningless if the entity filed on v4."""
    st = sample_statement()
    assert len(st.subjects) == 2
    names = {s.name for s in st.subjects}
    assert "filing.xlsx" in names and "template.xlsx" in names
    with pytest.raises(StatementError) as e:
        object.__setattr__(st, "subjects", (st.subjects[0],))
        type(st).__post_init__(st)
    assert "template v3" in str(e.value)


def test_stmt__an_invalid_run_carries_null_and_a_cause() -> None:
    st = sample_statement(invalid=True)
    pred = st.as_predicate()
    assert pred["settledFraction"] is None and pred["verdict"] is None
    assert pred["invalidCauses"] == ["invalid.canary_silent"]
    assert "settledFraction" in pred and "verdict" in pred, "PRESENT and null — not omitted"


def test_stmt__a_number_on_an_invalid_run_is_refused() -> None:
    """The builder refuses what the schema forbids, so the two cannot disagree."""
    good = sample_statement()
    with pytest.raises(StatementError) as e:
        type(good)(
            **{
                **{f: getattr(good, f) for f in good.__slots__ if not f.startswith("_")},
                "run_state": "INVALID",
                "invalid_causes": ("invalid.canary_silent",),
            }
        )
    assert "we make no claim" in str(e.value)


def test_stmt__a_valid_run_carries_no_invalid_cause() -> None:
    good = sample_statement()
    with pytest.raises(StatementError):
        type(good)(
            **{
                **{f: getattr(good, f) for f in good.__slots__ if not f.startswith("_")},
                "invalid_causes": ("invalid.canary_silent",),
            }
        )


def test_stmt__the_four_statements_are_in_every_predicate() -> None:
    """They are fields, not template strings — so they are here whatever a renderer does."""
    pred = sample_statement().as_predicate()
    assert set(pred["statements"]) == set(STATEMENTS)
    assert "does not state that the filing is correct" in pred["statements"]["purpose"]
    assert "BOUNDED" in pred["statements"]["boundedSilence"]
    assert "LOSSY" in pred["statements"]["summaryIsNotSubstitute"]
    assert "lower bound" in pred["statements"]["detectionBoundary"]


def test_stmt__ffr_is_null_with_a_self_authored_corpus() -> None:
    """G-CORPUS's FAIL branch, as a SCHEMA requirement rather than a rendering one. A rate of zero
    would be a claim; null is the absence of one."""
    pred = sample_statement().as_predicate()
    assert pred["falseFailureRate"] is None
    assert pred["corpusProvenance"] == "SELF-AUTHORED"


def test_stmt__the_vendor_signs_nothing() -> None:
    assert sample_statement().as_predicate()["assessor"]["thirdParty"] is False


def test_stmt__both_shapes_validate_against_the_schema() -> None:
    validate(sample_statement())
    validate(sample_statement(invalid=True))


def test_stmt__an_omitted_field_fails_validation() -> None:
    """The third leg of F24's ruling: `null` is a claim, and **absence is a bug**."""
    import jsonschema

    st = sample_statement(invalid=True)
    obj = st.as_obj()
    del obj["predicate"]["settledFraction"]
    schema = __import__("json").loads(
        (REPO / "src" / "cdfc" / "attest" / "schema" / "attestation.schema.json")
        .read_text(encoding="utf-8")
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=obj, schema=schema)


def test_stmt__an_unknown_property_fails_validation() -> None:
    import jsonschema

    obj = sample_statement().as_obj()
    obj["predicate"]["overallStatus"] = "fine"
    schema = __import__("json").loads(
        (REPO / "src" / "cdfc" / "attest" / "schema" / "attestation.schema.json")
        .read_text(encoding="utf-8")
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=obj, schema=schema)


def test_stmt__the_open_items_carry_their_age_and_it_is_derived() -> None:
    """*"Rendered from `surface/openitems.py`, with its age, not as silence."* The age is computed
    from `timeVerified`, so it grows on its own — an item whose age is maintained by hand reads as
    three days old for ever."""
    from cdfc.measure.p11_attest import open_items

    early = {i["id"]: i["ageDays"] for i in open_items("2026-08-14T00:00:00Z")}
    later = {i["id"]: i["ageDays"] for i in open_items("2026-12-14T00:00:00Z")}
    assert early["C21"] == 3
    assert all(later[k] > early[k] for k in early), "the ages did not move with timeVerified"


# --- DSSE ---------------------------------------------------------------------------------------


def test_dsse__pae_is_length_prefixed() -> None:
    """Signing `type || payload` directly lets two different pairs produce identical signed bytes,
    so one signature would attest to two different statements."""
    assert dsse.pae("ab", b"cd") == b"DSSEv1 2 ab 2 cd"
    assert dsse.pae("a", b"bcd") != dsse.pae("ab", b"cd")


def test_dsse__the_envelope_verifies_and_a_tampered_one_does_not() -> None:
    env = dsse.sign(b'{"a":1}').as_obj()
    assert dsse.verify(env) is True
    bad = copy.deepcopy(env)
    bad["payload"] = bad["payload"][:-4] + "AAAA"
    assert dsse.verify(bad) is False


def test_dsse__no_public_key_is_None_and_not_False() -> None:
    """*We checked and it does not match* and *there is nothing here to check against* are
    different facts about the world."""
    env = dsse.sign(b'{"a":1}').as_obj()
    env["signatures"][0].pop("publicKey")
    assert dsse.verify(env) is None
    env["signatures"] = []
    assert dsse.verify(env) is None


def test_dsse__the_implementation_label_travels_with_the_signature() -> None:
    env = dsse.sign(b'{"a":1}').as_obj()
    label = env["signatures"][0]["implementation"]
    assert "NOT CONSTANT-TIME" in label and "NOT FOR A PRODUCTION SIGNING KEY" in label
    assert label == ed25519.IMPLEMENTATION_LABEL


def test_dsse__signing_is_deterministic_over_the_same_payload() -> None:
    """What lets a signature be part of a byte-identity claim rather than an exception to it."""
    a, b = dsse.sign(b'{"a":1}'), dsse.sign(b'{"a":1}')
    assert a.sig == b.sig
    assert dsse.sign(b'{"a":2}').sig != a.sig


def test_dsse__an_empty_payload_is_refused() -> None:
    with pytest.raises(dsse.SigningRefused):
        dsse.sign(b"")
