"""P11-B1 — DSSE, and the two things that must never merge.

The envelope is DSSE v1: `{payload, payloadType, signatures:[{keyid, sig}]}`, the signature taken
over **PAE** (Pre-Authentication Encoding) rather than over the raw payload. PAE is length-prefixed,
so `payloadType || payload` cannot be re-split a second way — the shape a signature scheme is
supposed to have and the shape a naive concatenation does not.

## THE FILER SIGNS. THE VENDOR SIGNS NOTHING.

The vendor appears only as `assessor.id` with `thirdParty: false`. A vendor signature over a
customer's compliance statement would be an assurance opinion we are not licensed to give and did
not perform, and it would read as one whatever the surrounding words said.

## KEYLESS IS UNREACHABLE, AND THAT IS A PRIVACY DECISION

`--tlog-upload=false` is not a default here; there is **no keyless code path at all**, and
`test_no_tlog` asserts it by import closure. A keyless (Fulcio/Rekor) signature puts *the fact and
the timing of a named fund management entity running a pre-submission compliance check* into a
permanent, public, append-only transparency log. That is a disclosure about the filer that the
filer did not ask for and cannot retract, and it is made by the tool they ran to be careful.

## `verify` NEVER RE-SIGNS

A tool that re-signed to compare signatures would report a mismatch whenever the key differed and a
match whenever it did not — and neither answer is about the report. So the envelope carries the
public key, `verify` checks the stored signature against it, and **`reproduced` and
`signature_valid` are two separate facts** that a caller reads separately.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from cdfc.attest import ed25519

PAYLOAD_TYPE: Final[str] = "application/vnd.in-toto+json"


class SigningRefused(ValueError):
    """A signature this module must not produce."""


def pae(payload_type: str, payload: bytes) -> bytes:
    """DSSE Pre-Authentication Encoding.

        "DSSEv1" SP LEN(type) SP type SP LEN(payload) SP payload

    **Length-prefixed, and that is the whole point.** Signing `type || payload` directly lets two
    different `(type, payload)` pairs produce identical signed bytes, so one signature would attest
    to two different statements. The lengths make the split unambiguous.
    """
    t = payload_type.encode("utf-8")
    return b"DSSEv1 %d %s %d %s" % (len(t), t, len(payload), payload)


@dataclass(frozen=True, slots=True)
class Envelope:
    payload: bytes
    payload_type: str
    keyid: str
    sig: bytes
    public_key: bytes
    implementation_label: str = ed25519.IMPLEMENTATION_LABEL

    def as_obj(self) -> dict[str, Any]:
        import base64

        return {
            "payload": base64.b64encode(self.payload).decode("ascii"),
            "payloadType": self.payload_type,
            "signatures": [
                {
                    "keyid": self.keyid,
                    "sig": base64.b64encode(self.sig).decode("ascii"),
                    # The public key travels IN the envelope, because a third party has no other
                    # way to check the signature and a signature nobody can check is decoration.
                    "publicKey": base64.b64encode(self.public_key).decode("ascii"),
                    # And the label travels with it, because what a signature is worth depends on
                    # what produced it.
                    "implementation": self.implementation_label,
                }
            ],
        }


def sign(payload: bytes, *, secret: bytes = ed25519.DEMO_SECRET,
         keyid: str = ed25519.DEMO_KEY_ID) -> Envelope:
    """Sign over PAE. **Deterministic** — RFC 8032 derives the nonce from the key and the message,
    so the same payload and key produce the same 64 bytes, which is what lets a signature be part
    of a byte-identity claim rather than an exception to it."""
    if not payload:
        raise SigningRefused("refusing to sign an empty payload")
    return Envelope(
        payload=payload,
        payload_type=PAYLOAD_TYPE,
        keyid=keyid,
        sig=ed25519.sign(secret, pae(PAYLOAD_TYPE, payload)),
        public_key=ed25519.public_key(secret),
    )


def verify(envelope_obj: dict[str, Any]) -> bool | None:
    """`True` / `False` / **`None` when the envelope carries no public key**.

    `None` is not `False`. *We checked and it does not match* and *there is nothing here to check
    against* are different facts about the world, and reporting the first for the second is the
    collapse this project is named for.
    """
    import base64

    sigs = envelope_obj.get("signatures") or []
    if not sigs:
        return None
    entry = sigs[0]
    raw_key = entry.get("publicKey")
    if not raw_key:
        return None
    payload = base64.b64decode(envelope_obj["payload"])
    return ed25519.verify(
        base64.b64decode(raw_key),
        pae(str(envelope_obj.get("payloadType", PAYLOAD_TYPE)), payload),
        base64.b64decode(entry["sig"]),
    )
