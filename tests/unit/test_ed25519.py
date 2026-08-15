"""RFC 8032 §7.1's own test vectors — an oracle nobody on this project wrote.

**A crypto implementation validated only against its own output is a self-check**, which is the
defect shape this entire project is about. The secret, the public key, the message and the 64
signature bytes below are all four fixed by the IETF standard; if this implementation disagrees
with any of them it is wrong, and no amount of internal consistency changes that.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest import ed25519  # noqa: E402

# RFC 8032 §7.1 — Test Vectors for Ed25519. Verbatim.
VECTORS = [
    (
        "TEST 1 (empty message)",
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "",
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc"
        "61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b",
    ),
    (
        "TEST 2 (one byte)",
        "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
        "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "72",
        "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e"
        "458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00",
    ),
    (
        "TEST 3 (two bytes)",
        "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
        "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
        "af82",
        "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290"
        "ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a",
    ),
]


@pytest.mark.parametrize("name,secret,public,msg,sig", VECTORS, ids=[v[0] for v in VECTORS])
def test_ed25519__rfc_8032_public_key(name: str, secret: str, public: str, msg: str, sig: str) -> None:
    assert ed25519.public_key(bytes.fromhex(secret)).hex() == public


@pytest.mark.parametrize("name,secret,public,msg,sig", VECTORS, ids=[v[0] for v in VECTORS])
def test_ed25519__rfc_8032_signature(name: str, secret: str, public: str, msg: str, sig: str) -> None:
    """The signature bytes are fixed by the standard, so this is a real oracle."""
    secret_b = bytes.fromhex(secret)
    if secret_b != ed25519.DEMO_SECRET:
        # `sign` refuses any key but the demo key BY DESIGN, and that refusal is load-bearing.
        # The vector is still checked, through `verify`, which is the path with no secret in it.
        assert ed25519.verify(bytes.fromhex(public), bytes.fromhex(msg), bytes.fromhex(sig))
        return
    assert ed25519.sign(secret_b, bytes.fromhex(msg)).hex() == sig


@pytest.mark.parametrize("name,secret,public,msg,sig", VECTORS, ids=[v[0] for v in VECTORS])
def test_ed25519__rfc_8032_verify(name: str, secret: str, public: str, msg: str, sig: str) -> None:
    assert ed25519.verify(bytes.fromhex(public), bytes.fromhex(msg), bytes.fromhex(sig))


def test_ed25519__a_flipped_signature_byte_does_not_verify() -> None:
    """The admission-side twin. Without it, `verify` returning True for everything passes above."""
    _n, secret, public, msg, sig = VECTORS[1]
    raw = bytearray(bytes.fromhex(sig))
    for i in (0, 31, 32, 63):
        bad = bytearray(raw)
        bad[i] ^= 0x01
        assert not ed25519.verify(bytes.fromhex(public), bytes.fromhex(msg), bytes(bad)), (
            f"a signature with byte {i} flipped verified — `verify` is not checking anything"
        )


def test_ed25519__a_flipped_message_byte_does_not_verify() -> None:
    _n, _s, public, msg, sig = VECTORS[2]
    bad = bytearray(bytes.fromhex(msg))
    bad[0] ^= 0x01
    assert not ed25519.verify(bytes.fromhex(public), bytes(bad), bytes.fromhex(sig))


def test_ed25519__a_wrong_public_key_does_not_verify() -> None:
    _n, _s, _pub, msg, sig = VECTORS[1]
    other = VECTORS[2][2]
    assert not ed25519.verify(bytes.fromhex(other), bytes.fromhex(msg), bytes.fromhex(sig))


def test_ed25519__a_non_canonical_scalar_is_rejected() -> None:
    """RFC 8032 §5.1.7: `s` must be reduced. An implementation that skips the check accepts
    malleable signatures, and a malleable signature over an attestation is a second valid
    signature for one payload."""
    _n, _s, public, msg, sig = VECTORS[1]
    raw = bytearray(bytes.fromhex(sig))
    raw[32:] = int.to_bytes(2**252 + 27742317777372353535851937790883648493, 32, "little")
    assert not ed25519.verify(bytes.fromhex(public), bytes.fromhex(msg), bytes(raw))


def test_ed25519__signing_is_deterministic() -> None:
    """The same payload and key produce the same 64 bytes. This is what lets a signature be part
    of a byte-identity claim rather than an exception to it."""
    msg = b"the same payload twice"
    a = ed25519.sign(ed25519.DEMO_SECRET, msg)
    b = ed25519.sign(ed25519.DEMO_SECRET, msg)
    assert a == b and len(a) == 64
    assert ed25519.verify(ed25519.public_key(ed25519.DEMO_SECRET), msg, a)


def test_ed25519__it_refuses_any_key_but_the_published_demo_key() -> None:
    """**Not a flag and not a warning.** `point_mul` is a double-and-add over the secret scalar, so
    its timing carries the key's bits. An implementation honest about that must also be unable to
    be pointed at a key where it matters — and the check is on the KEY, because a flag is what
    somebody sets.
    """
    other = bytes.fromhex(VECTORS[1][1])
    with pytest.raises(ed25519.KeyRefused) as e:
        ed25519.sign(other, b"anything")
    assert "NOT CONSTANT-TIME" in str(e.value)
    assert "cryptography" in str(e.value), "the refusal must name the way out, not just refuse"
    ed25519.sign(ed25519.DEMO_SECRET, b"anything")     # the admission-side twin


def test_ed25519__the_label_is_a_constant_and_says_what_is_weak() -> None:
    label = ed25519.IMPLEMENTATION_LABEL
    assert "NOT CONSTANT-TIME" in label and "NOT FOR A PRODUCTION SIGNING KEY" in label
    assert "RFC 8032" in label
