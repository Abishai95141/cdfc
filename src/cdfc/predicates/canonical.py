"""P4-B1 — the canonical serialisation an envelope's identity is computed over.

`jcs` is `cdfc.canon.canonical_json` re-exported, not re-implemented. RFC 8785 sorts object
keys by UTF-16 code units rather than by code point, and two implementations of that rule
produce two registry roots for one registry.

**`envelope_projection` is checked against `dataclasses.fields()` at runtime**, so a field added
to the record without being added here fails `test_prop__every_envelope_field_is_covered_by_the_digest`
instead of silently leaving the identity. That property is the reason `claims_fault_classes` and
`clause_absent_reason` became part of the identity for free the moment they were added — and it is
the control behind NC-Q70.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from cdfc.canon import canonical_json, sha256_hex
from cdfc.predicates.envelope import Candidate, Predicate

__all__ = ["jcs", "envelope_projection", "code_sha256", "ProjectionCoverageError"]


class ProjectionCoverageError(AssertionError):
    """A field of the record is not in the projection, so it is not in the identity."""


def jcs(obj: Any) -> bytes:
    """RFC 8785 canonical JSON. One implementation, shared with every other hashed object."""
    return canonical_json(obj)


def _plain(value: Any) -> Any:
    """Dataclasses to mappings, tuples to lists, everything else verbatim.

    Deliberately *not* `dataclasses.asdict`: that would silently include any nested field the
    projection never looked at, which is the opposite of the guarantee this module makes.
    """
    if value is None or isinstance(value, (str, int)) and not isinstance(value, bool):
        return value
    if isinstance(value, bool):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    raise TypeError(f"cannot project {type(value).__name__} into a canonical envelope")


def envelope_projection(c: Candidate | Predicate) -> dict[str, Any]:
    """THE serialisation the digest covers. Every field of the record, none omitted.

    The projection is generated from `dataclasses.fields()` rather than written out by hand.
    A hand-written projection is exactly how a field leaves an identity without anyone noticing,
    and the digest of a predicate is what a registry admission is keyed on.
    """
    out = {f.name: _plain(getattr(c, f.name)) for f in fields(c)}
    missing = {f.name for f in fields(c)} - set(out)
    if missing:  # unreachable by construction; asserted because the cost of being wrong is a
        raise ProjectionCoverageError(  # registry root that does not cover what it claims to
            f"fields absent from the canonical projection: {sorted(missing)}"
        )
    # The type is part of the identity: a Candidate and a Predicate with identical common
    # fields are different things, and a digest that could not tell them apart would let an
    # unqualified envelope inherit a qualified one's admission record.
    out["__envelope_type__"] = type(c).__name__
    return out


def code_sha256(c: Candidate | Predicate) -> str:
    """sha256 over the canonical projection, lowercase hex. The predicate's identity."""
    return sha256_hex(jcs(envelope_projection(c)))
