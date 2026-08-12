"""RFC 8785 JSON Canonicalization Scheme — the ONE serialiser for any hashed object.

Why one implementation and not "just use json.dumps(sort_keys=True)": RFC 8785 sorts
object keys by their **UTF-16 code units**, not by Python's code-point order. The two
orders differ for any key outside the BMP, and for a registry whose root is a Merkle hash
over sorted entries that means two implementations produce two roots for one registry.
The project's own corpus already contains a `U+2011` homoglyph in a live registration
number, so non-ASCII keys are not hypothetical here.

Numbers: RFC 8785 mandates ECMAScript `Number::toString`. We sidestep the hard part by
REFUSING floats outright — every quantity in this system is an integer (money is an
`int64` count of 10^-3 USD Million) and a float in a hashed payload is a
reproducibility bug wearing a value's clothes.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class NonCanonicalisable(TypeError):
    """The object cannot be canonicalised. Never silently coerced."""


_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
    0x22: '\\"',
    0x5C: "\\\\",
}


def _escape(s: str) -> str:
    out = []
    for ch in s:
        cp = ord(ch)
        if cp in _ESCAPES:
            out.append(_ESCAPES[cp])
        elif cp < 0x20:
            out.append(f"\\u{cp:04x}")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _utf16_key(k: str) -> tuple[int, ...]:
    """The sort key RFC 8785 actually specifies: UTF-16 code units."""
    return tuple(k.encode("utf-16-be"))


def _ser(obj: Any) -> str:
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, float):
        raise NonCanonicalisable(
            "a float reached the canonical serialiser. Every hashed quantity in this "
            "system is an integer; money is an int64 count of 10^-3 USD Million. A float "
            "here is a reproducibility bug, not a value."
        )
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, str):
        return _escape(obj)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_ser(x) for x in obj) + "]"
    if isinstance(obj, dict):
        keys = sorted(obj, key=_utf16_key)
        for k in keys:
            if not isinstance(k, str):
                raise NonCanonicalisable(f"object key {k!r} is not a string")
        return "{" + ",".join(_escape(k) + ":" + _ser(obj[k]) for k in keys) + "}"
    raise NonCanonicalisable(f"cannot canonicalise {type(obj).__name__}")


def canonical_json(obj: Any) -> bytes:
    """RFC 8785 canonical form, UTF-8 encoded. The only serialiser for a hashed object."""
    return _ser(obj).encode("utf-8")


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def digest(obj: Any) -> str:
    """sha256 of the canonical form. Use this, never sha256(json.dumps(...))."""
    return sha256_hex(canonical_json(obj))


def loads(b: bytes | str) -> Any:
    """Parse, for round-trip tests. Not part of the hashing path."""
    return json.loads(b)


_FLOATY = re.compile(rb"\d\.\d")


def assert_no_float(b: bytes) -> None:
    if _FLOATY.search(b):
        raise NonCanonicalisable("canonical output contains a decimal number")
