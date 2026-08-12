"""`gstin_valid(string) -> bool` — the GSTIN check digit, computed rather than pattern-matched.

This is D-P4-03's example made concrete. The obvious `matches()` pattern accepts any 15 characters
of the right shape; it cannot see a transposed digit, which is the modal keying error. The check
digit can, and it lives here because here is where a check can carry test vectors and a mutation
score.

The algorithm: 36-character alphabet `0-9A-Z`; each of the first 14 positions is weighted 1, 2,
1, 2 ...; each product is folded by `quotient + remainder` on 36; the sum's complement to the next
multiple of 36 is the check character.
"""

from __future__ import annotations

from typing import Any

from celpy import celtypes

from cdfc.predicates.host_fns import HostFn, vector_digest

NAME = "gstin_valid"
VERSION = "1"
SIGNATURE = "gstin_valid(string) -> bool"

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gstin_valid(value: Any) -> Any:
    s = str(value)
    if len(s) != 15 or any(ch not in ALPHABET for ch in s):
        return celtypes.BoolType(False)
    total = 0
    for i, ch in enumerate(s[:14]):
        product = ALPHABET.index(ch) * (2 if i % 2 else 1)
        total += product // 36 + product % 36
    check = ALPHABET[(36 - total % 36) % 36]
    return celtypes.BoolType(check == s[14])


def register_into(reg: Any) -> None:
    reg.register(HostFn(
        name=NAME, version=VERSION, signature=SIGNATURE, returns_tristate=False,
        fn=gstin_valid, test_vector_sha256=vector_digest(NAME),
        mutation_score_json=f"reports/host_fns/{NAME}.mutation.json",
        authored_by="cdfc P4-B3",
    ))
