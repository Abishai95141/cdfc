"""P11-B1 — the four properties of the attestation layer.

`tests/property/test_prop_canon.py` already covers RFC 8785 order-invariance and the float refusal
over arbitrary trees. These are the properties that are about the STATEMENT: that its canonical
bytes distinguish statements that differ, that its signature is deterministic, and that `expires`
is a function of an input rather than of the day it was computed.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest import dsse, ed25519  # noqa: E402
from cdfc.attest.policy import POLICY_VALIDITY_DAYS, expires_for  # noqa: E402
from cdfc.canon import canonical_json  # noqa: E402
from tests.contract.attest_fixtures import sample_statement  # noqa: E402

PROFILE = settings(
    max_examples=200, deadline=None, derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)

INSTANTS = st.datetimes(
    min_value=_dt.datetime(2000, 1, 1), max_value=_dt.datetime(2100, 1, 1)
).map(lambda d: d.replace(microsecond=0).isoformat() + "Z")


@PROFILE
@given(INSTANTS)
def test_prop__expires_is_a_function_of_time_verified(stamp: str) -> None:
    """**`expires == timeVerified + POLICY_VALIDITY`, and no clock is read.**

    Easy to under-rate and a real byte-identity hazard: `timeVerified` is an input recorded in the
    manifest, so `expires` must be derived from it. Derived from `now()` instead, every attestation
    differs from its own re-derivation on the following day and `E2E-VERIFY` fails permanently for
    a reason that reads like clock skew rather than like a bug.
    """
    out = expires_for(stamp)
    assert out == expires_for(stamp), "not a function: two calls disagreed"
    base = _dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    got = _dt.datetime.fromisoformat(out.replace("Z", "+00:00"))
    assert (got - base).days == POLICY_VALIDITY_DAYS
    assert got > base, "expires must be after the instant it was derived from"


@PROFILE
@given(st.integers(min_value=0, max_value=9_999_999), st.integers(min_value=0, max_value=3_747))
def test_prop__canonicalisation_is_injective_on_our_payload_set(settled: int, in_scope: int) -> None:
    """Two structurally different statements never canonicalise to the same bytes.

    The canonicaliser is the one module where a wrong answer is **silent by construction**, because
    both sides of the comparison are hashes. If two different statements collapsed to one digest, a
    tampered report would verify against the original's signature.
    """
    base = sample_statement()
    a = base.as_obj()
    b = base.as_obj()
    b["predicate"]["settledFraction"]["settled"] = settled
    b["predicate"]["settledFraction"]["inScope"] = in_scope
    same = (
        a["predicate"]["settledFraction"]["settled"] == settled
        and a["predicate"]["settledFraction"]["inScope"] == in_scope
    )
    assert (canonical_json(a) == canonical_json(b)) is same


@PROFILE
@given(st.binary(min_size=1, max_size=512))
def test_prop__ed25519_is_deterministic(payload: bytes) -> None:
    """The same payload and key produce the same 64 signature bytes — on every machine, for ever.

    RFC 8032 derives the nonce from the key and the message rather than from randomness, which is
    what lets a signature be part of a byte-identity claim rather than an exception to it.
    """
    a = ed25519.sign(ed25519.DEMO_SECRET, payload)
    b = ed25519.sign(ed25519.DEMO_SECRET, payload)
    assert a == b and len(a) == 64
    assert ed25519.verify(ed25519.public_key(ed25519.DEMO_SECRET), payload, a)


@PROFILE
@given(st.binary(min_size=1, max_size=256), st.binary(min_size=1, max_size=256))
def test_prop__the_envelope_binds_its_payload(one: bytes, two: bytes) -> None:
    """A signature over PAE cannot be moved to a different payload.

    PAE is length-prefixed precisely so `payloadType || payload` cannot be re-split a second way;
    without it, two different `(type, payload)` pairs could produce identical signed bytes and one
    signature would attest to two different statements.
    """
    env = dsse.sign(one).as_obj()
    assert dsse.verify(env) is True
    if one == two:
        return
    import base64

    moved = dict(env)
    moved["payload"] = base64.b64encode(two).decode("ascii")
    assert dsse.verify(moved) is False
