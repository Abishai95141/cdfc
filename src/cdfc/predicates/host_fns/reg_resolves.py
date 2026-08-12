"""`reg_resolves(string) -> string` — tri-state, snapshot-bound, and it cannot resolve live.

**Three values, not two.** `"TRUE"`, `"FALSE"`, `"UNDERSPECIFIED"`. The third is what the function
returns when the bound snapshot has nothing to say about a registration number — which is a
different fact from "this entity is not registered", and reporting them as one would turn a gap in
our snapshot into a finding against a filer.

**There is no HTTP client in this module's import closure**, and that is asserted by an AST walk
rather than left to code review. A verdict that depends on what a remote endpoint said at run time
cannot be re-derived from the filing's bytes, so calling with no snapshot bound RAISES; the
evaluator maps that to `NOT_RUN(not_run.input_unavailable.register)`.
"""

from __future__ import annotations

from typing import Any

from celpy import celtypes

from cdfc.predicates.host_fns import UNDERSPECIFIED, HostFn, vector_digest

NAME = "reg_resolves"
VERSION = "1"
SIGNATURE = "reg_resolves(string) -> string"

_REGISTRY: Any = None


def bind_registry(reg: Any) -> None:
    """The registry that owns the snapshot. Set by `register_into`; there is no other source."""
    global _REGISTRY
    _REGISTRY = reg


def reg_resolves(value: Any) -> Any:
    if _REGISTRY is None:
        raise LookupError(
            "reg_resolves was called with no registry bound. It never falls back to a live "
            "lookup: NOT_RUN(not_run.input_unavailable.register) is the honest outcome."
        )
    key = str(value).strip()
    if not key:
        return celtypes.StringType(UNDERSPECIFIED)
    record = _REGISTRY.lookup(key)   # raises SnapshotMissing when nothing is bound
    if record is None:
        # MEASURED, and it is why this is tri-state: one live regulated entity's registration
        # number carries U+2011 NON-BREAKING HYPHEN — visually identical to a hyphen, byte-wise
        # different, and absent from any snapshot keyed on the ASCII form. "Not in our snapshot"
        # is not "not registered".
        return celtypes.StringType(UNDERSPECIFIED)
    return celtypes.StringType("TRUE" if record else "FALSE")


def register_into(reg: Any) -> None:
    bind_registry(reg)
    reg.register(HostFn(
        name=NAME, version=VERSION, signature=SIGNATURE, returns_tristate=True,
        fn=reg_resolves, test_vector_sha256=vector_digest(NAME),
        mutation_score_json=f"reports/host_fns/{NAME}.mutation.json",
        authored_by="cdfc P4-B3",
    ))
