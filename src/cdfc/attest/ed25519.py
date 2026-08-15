"""RFC 8032 Ed25519, from the RFC's own reference implementation — and **labelled**.

**WHY THIS EXISTS RATHER THAN A DEPENDENCY.** `cryptography` and `PyNaCl` are the right answers and
neither is in this project's lockfile, which is hash-pinned and cannot be extended from this
environment. The alternative to implementing RFC 8032 was shipping P11 with **no signature at all**,
which loses exit criterion 3 — `E2E-TAMPER-ATTEST` reporting `signature_valid` and `reproduced` as
two separate facts — and with it the only mechanism by which a reader can tell a changed report from
a changed key.

## THE LABEL, AND IT TRAVELS

```
PURE-PYTHON ED25519 — NOT CONSTANT-TIME. NOT FOR A PRODUCTION SIGNING KEY.
```

`IMPLEMENTATION_LABEL` is carried on every envelope this module signs and rendered on every surface
that quotes one, the same way `SINGLE-SIGNER — a weaker review`, `SAME-AUTHOR — a weaker instrument`
and `RULE-BASED-v1 — a weaker adjudication` are. It ships weaker, visibly; it does not ship silently.

**What the label is and is not about.** `point_mul` is a double-and-add over a secret scalar: its
timing depends on the bits of the private key, so a local attacker who can measure it can recover
that key. That is a real defect and it bounds what this may be used for:

| path | secret involved | admissible here |
|---|---|---|
| **`verify`** — what a third party runs, and what G-REPRO is about | **none** | **yes, without qualification.** There is no secret to leak, so the side channel does not exist on this path |
| **`sign`** with the demo key over a synthetic filing | a key we published | **yes.** `plan/05` P11-B1 specifies exactly this: *"the demo signs a synthetic filing with a demo key and the report says so on its face"* |
| **`sign`** with a filer's real key | the filer's | **NO.** `assert_not_production_key()` refuses, and it is not a convention — it raises |

## CORRECTNESS IS CHECKED AGAINST THE STANDARD, NOT AGAINST ITSELF

`tests/unit/test_ed25519.py` runs **RFC 8032 §7.1's own published test vectors** — the secret, the
public key, the message and the 64 signature bytes, all four fixed by the standard. A crypto
implementation validated only against its own output is a self-check, which is the defect shape this
whole project is about; a test vector authored by the IETF is an oracle nobody here wrote.

The code below is the RFC's Appendix A reference implementation, restructured but not re-derived.
"""

from __future__ import annotations

import hashlib
from typing import Final

# The label, and it is a module constant so nothing can quote a signature without it.
IMPLEMENTATION_LABEL: Final[str] = (
    "PURE-PYTHON ED25519 (RFC 8032 reference) — NOT CONSTANT-TIME. NOT FOR A PRODUCTION SIGNING KEY."
)

# The demo key `plan/05` P11-B1 sanctions, and the ONLY key this module will sign with. It is
# published here on purpose: a key in source control is not a secret, and saying so is the point.
DEMO_SECRET: Final[bytes] = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
DEMO_KEY_ID: Final[str] = "cdfc-demo-key-do-not-trust"

_p: Final[int] = 2**255 - 19
_q: Final[int] = 2**252 + 27742317777372353535851937790883648493
_d: Final[int] = -121665 * pow(121666, _p - 2, _p) % _p
_SQRT_M1: Final[int] = pow(2, (_p - 1) // 4, _p)


class KeyRefused(ValueError):
    """A signing key this implementation must not touch."""


def assert_not_production_key(secret: bytes) -> None:
    """**Refuse to sign with anything but the published demo key.**

    Not a convention and not a warning. `point_mul` is a double-and-add over the secret scalar, so
    its timing carries the key's bits; an implementation that is honest about that must also be
    unable to be pointed at a key where it matters. The check is on the KEY, not on a flag,
    because a flag is what somebody sets.
    """
    if secret != DEMO_SECRET:
        raise KeyRefused(
            f"{IMPLEMENTATION_LABEL} This module signs with the published demo key and nothing "
            "else. Signing a filer's key with a non-constant-time scalar multiply leaks that key "
            "to anyone who can time the process. Install `cryptography` or `PyNaCl` and route "
            "production signing through it — the DSSE envelope, the PAE encoding and `verify` are "
            "unaffected and need no change."
        )


def _sha512(b: bytes) -> bytes:
    return hashlib.sha512(b).digest()


def _sha512_modq(b: bytes) -> int:
    return int.from_bytes(_sha512(b), "little") % _q


# Extended homogeneous coordinates (X, Y, Z, T), per RFC 8032 Appendix A.
_Point = tuple[int, int, int, int]


def _point_add(P: _Point, Q: _Point) -> _Point:
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % _p
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % _p
    C = 2 * P[3] * Q[3] * _d % _p
    D = 2 * P[2] * Q[2] % _p
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _p, G * H % _p, F * G % _p, E * H % _p)


def _point_mul(s: int, P: _Point) -> _Point:
    Q: _Point = (0, 1, 1, 0)          # the neutral element
    while s > 0:
        if s & 1:
            Q = _point_add(Q, P)
        P = _point_add(P, P)
        s >>= 1
    return Q


def _point_equal(P: _Point, Q: _Point) -> bool:
    if (P[0] * Q[2] - Q[0] * P[2]) % _p != 0:
        return False
    return (P[1] * Q[2] - Q[1] * P[2]) % _p == 0


def _recover_x(y: int, sign: int) -> int | None:
    if y >= _p:
        return None
    x2 = (y * y - 1) * pow(_d * y * y + 1, _p - 2, _p) % _p
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_p + 3) // 8, _p)
    if (x * x - x2) % _p != 0:
        x = x * _SQRT_M1 % _p
    if (x * x - x2) % _p != 0:
        return None
    if (x & 1) != sign:
        x = _p - x
    return x


_G_Y: Final[int] = 4 * pow(5, _p - 2, _p) % _p
_G_X: Final[int] = _recover_x(_G_Y, 0)  # type: ignore[assignment]
_G: Final[_Point] = (_G_X, _G_Y, 1, _G_X * _G_Y % _p)


def _compress(P: _Point) -> bytes:
    zinv = pow(P[2], _p - 2, _p)
    x, y = P[0] * zinv % _p, P[1] * zinv % _p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _decompress(s: bytes) -> _Point | None:
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % _p)


def _expand(secret: bytes) -> tuple[int, bytes]:
    if len(secret) != 32:
        raise KeyRefused(f"an Ed25519 secret is 32 bytes; got {len(secret)}")
    h = _sha512(secret)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def public_key(secret: bytes) -> bytes:
    a, _prefix = _expand(secret)
    return _compress(_point_mul(a, _G))


def sign(secret: bytes, msg: bytes) -> bytes:
    """64 signature bytes. **Deterministic**: RFC 8032 derives the nonce from the key and message,
    so the same payload and key produce the same bytes on every machine — which is what makes an
    attestation's signature part of a byte-identity claim rather than an exception to it."""
    assert_not_production_key(secret)
    a, prefix = _expand(secret)
    A = _compress(_point_mul(a, _G))
    r = _sha512_modq(prefix + msg)
    Rs = _compress(_point_mul(r, _G))
    h = _sha512_modq(Rs + A + msg)
    return Rs + int.to_bytes((r + h * a) % _q, 32, "little")


def verify(public: bytes, msg: bytes, signature: bytes) -> bool:
    """**No secret is involved on this path**, so the timing caveat in the module docstring does
    not apply to it. This is what a third party runs, and it is what G-REPRO is about."""
    if len(public) != 32 or len(signature) != 64:
        return False
    A = _decompress(public)
    if A is None:
        return False
    Rs = signature[:32]
    R = _decompress(Rs)
    if R is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= _q:
        return False        # a non-canonical scalar; RFC 8032 §5.1.7 rejects it
    h = _sha512_modq(Rs + public + msg)
    return _point_equal(_point_mul(s, _G), _point_add(R, _point_mul(h, A)))
