"""P4-B2 — the exception types the CEL layer raises, kept apart on purpose.

`UndeclaredKeyRead` and `DeclaredKeyUnread` are **different types because they have different
remedies**, and NC-Q04 requires the two rejections to be distinguishable. A single `KeysMismatch`
would fail that control:

- a key **read but not declared** means the pre-flight set is too small and P5 rule 2 is guarding
  the wrong keys — the run can produce a `PASS` on a key nobody checked was present;
- a key **declared but not read** means the predicate's declared footprint overstates what it
  settles, which inflates the settled **numerator** — the report claims coverage it does not have.

One is a hole in the guard; the other is a lie in the headline number. Collapsing them into one
message is how a repair gets applied to the wrong side.
"""

from __future__ import annotations

__all__ = [
    "CelLayerError",
    "SubsetViolation",
    "UndeclaredKeyRead",
    "DeclaredKeyUnread",
    "KeyGrammarError",
    "UnregisteredHostFn",
    "RegistryNotFrozen",
]


class CelLayerError(Exception):
    """Base for everything this layer refuses. Never caught broadly inside the layer."""


class SubsetViolation(CelLayerError):
    """A construct outside the admitted subset. Carries where and why, so an author can fix it."""

    def __init__(self, construct: str, *, slot: str, reason: str, offset: int) -> None:
        self.construct = construct
        self.slot = slot
        self.reason = reason
        self.offset = offset
        super().__init__(f"{slot} slot, offset {offset}: {construct} — {reason}")


class UnresolvableMemberBase(SubsetViolation):
    """A member access whose base is not a statically resolvable path.

    `(filing.a).b` used to record only `filing.a`, so the static read set was strictly smaller
    than the runtime's — and because the DECLARED set matched the truncated static set,
    `check_declared_keys` agreed both ways, pre-flight guarded a key nobody read, and the
    predicate reached `PASS` over a key that was never checked for presence. One pair of
    parentheses separated `UndeclaredKeyRead` from a clean pass.

    It is a `SubsetViolation` and not a new family: the admitted subset exists precisely so the
    read set is statically decidable, and this is a construct that defeats that.
    """

    def __init__(self, reason: str) -> None:
        super().__init__("member access on a non-path base", slot="expr", reason=reason, offset=0)


class UndeclaredKeyRead(CelLayerError):
    """The program reads a key `schema_keys` does not declare. The pre-flight set is too small."""

    def __init__(self, predicate_id: str, keys: tuple[str, ...]) -> None:
        self.predicate_id = predicate_id
        self.keys = keys
        super().__init__(
            f"{predicate_id}: reads {list(keys)} without declaring them. Pre-flight guards the "
            "declared set, so an undeclared key is a key nobody checked was present — and a "
            "predicate can return PASS over one."
        )


class DeclaredKeyUnread(CelLayerError):
    """`schema_keys` declares a key no slot reads. The settled numerator is overstated."""

    def __init__(self, predicate_id: str, keys: tuple[str, ...]) -> None:
        self.predicate_id = predicate_id
        self.keys = keys
        super().__init__(
            f"{predicate_id}: declares {list(keys)} but reads none of them. The declared "
            "footprint overstates what this predicate settles, which inflates the settled "
            "fraction's numerator."
        )


class KeyGrammarError(CelLayerError):
    """A key that is not writable in D-P4-02's grammar."""


class UnregisteredHostFn(CelLayerError):
    """A call to a host function the registry does not carry."""


class RegistryNotFrozen(CelLayerError):
    """The host-function set must be CLOSED before anything is evaluated."""
