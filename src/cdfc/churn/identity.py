"""V2 — `qualified_against` is part of the predicate's identity. **There is no in-place edit.**

A predicate qualified against evaluator `v1`, fault model `v3`, corpus `c` and template `t` is not
the same predicate when any of the four moves. The conventional way to say that is a docstring; the
mechanical way is to put all four inside the digest, so a predicate cannot be edited into a
different qualification while keeping its name. Supersession is a NEW ROW (registry rule R5).

`code_sha256` already digests the envelope — the expression, the keys, the tolerance. This adds the
second half. They are kept separate rather than merged into one function because they answer
different questions: `code_sha256` asks *is this the same check*, and `predicate_identity` asks *is
this the same check, established the same way*. Two predicates can share the first and differ in the
second, and that pair is exactly what a churn sweep has to be able to tell apart.
"""

from __future__ import annotations

import dataclasses
from typing import Any

from cdfc.canon import canonical_json, sha256_hex
from cdfc.predicates.canonical import envelope_projection


class IdentityInputsMissing(ValueError):
    """A predicate with no `qualified_against` has no identity under V2.

    **Not defaulted to the envelope digest alone.** That would silently give an unqualified
    candidate the identity of a qualified predicate, which is the substitution the rule exists to
    prevent.
    """


def qualified_against_projection(p: Any) -> dict[str, str]:
    qa = getattr(p, "qualified_against", None)
    if qa is None:
        raise IdentityInputsMissing(
            f"{getattr(p, 'id', '?')}: no qualified_against. The evaluator, the fault model, the "
            "corpus and the template are part of the identity, and a predicate that does not say "
            "what it was qualified against cannot be placed in a supersession chain."
        )
    if dataclasses.is_dataclass(qa):
        return {k: str(v) for k, v in sorted(dataclasses.asdict(qa).items())}
    return {k: str(v) for k, v in sorted(dict(qa).items())}


def predicate_identity(p: Any) -> str:
    """`sha256` over the RFC 8785 canonicalisation of `(envelope, qualified_against)`.

    Changing any element of `qualified_against` changes this digest. That is the whole rule.
    """
    return sha256_hex(canonical_json({
        "envelope": envelope_projection(p),
        "qualified_against": qualified_against_projection(p),
    }))
