"""P7-B2 — G1, executes and binds. The cheap gate: one evaluation, against one filing.

**`g1.cells_bound_zero` is the condition whose absence produces the vacuous pass**, and it is
checked BEFORE `expr` runs, for the same reason D-P5-01 checks it at evaluation order 4: `all([])`
is `True`, so a predicate that binds nothing returns a clean pass over nothing at all. At the run
path that produces `ERROR`; here it produces a rejection, and the candidate never reaches a run.

**`g1.raised` is DISTINCT from the run-time `ERROR(error.predicate_raised)`, and the distinction is
not pedantic.** A candidate that raises is never admitted; a *predicate* that raises at run time is
an apparatus failure on an admitted check. Same symptom, two different findings, two different
remedies — so two reason codes.

**Six closed reasons.** As at G0 there is no seventh and no skip.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from cdfc.evaluate.celrt import Outcome
from cdfc.qualify.result import GateId, GateOutcome


class Reason:
    KEY_NOT_IN_SCHEMA: Final[str] = "g1.key_not_in_schema"
    KEY_UNRESOLVED: Final[str] = "g1.key_unresolved"
    HOST_FN_UNREGISTERED: Final[str] = "g1.host_fn_unregistered"
    RAISED: Final[str] = "g1.raised"
    BUDGET_EXHAUSTED: Final[str] = "g1.budget_exhausted"
    CELLS_BOUND_ZERO: Final[str] = "g1.cells_bound_zero"


CLOSED_REASONS: Final[tuple[str, ...]] = (
    Reason.KEY_NOT_IN_SCHEMA,
    Reason.KEY_UNRESOLVED,
    Reason.HOST_FN_UNREGISTERED,
    Reason.RAISED,
    Reason.BUDGET_EXHAUSTED,
    Reason.CELLS_BOUND_ZERO,
)

REMEDY: Final[Mapping[str, str]] = {
    Reason.KEY_NOT_IN_SCHEMA: "the predicate names a key this template does not have; re-harvest "
                              "or fix the key",
    Reason.KEY_UNRESOLVED: "induce the key, or withdraw the predicate. It BLOCKS; it never "
                           "degrades to a guess",
    Reason.HOST_FN_UNREGISTERED: "register the host function (admission rule R2) or remove the call",
    Reason.RAISED: "the expression is not evaluable against a clean filing; fix it before it is "
                   "ever applied to a real one",
    Reason.BUDGET_EXHAUSTED: "the expression does not terminate inside the admission budget",
    Reason.CELLS_BOUND_ZERO: "the predicate settles nothing. `all([])` is True, so it would "
                             "return a clean pass over no cells at all",
}


def check(
    cand: Any,
    schema: Any,
    facts: Any,
    rt: Any,
    hostfns: Any,
) -> GateOutcome:
    """One candidate against one reference filing. Never raises for a candidate-level failure."""
    from cdfc.predicates.ast_walker import bound_cells

    measured: dict[str, object] = {
        "declared_keys": len(cand.schema_keys),
        "host_fns": list(cand.host_fns),
    }

    def reject(reason: str, **over: object) -> GateOutcome:
        return GateOutcome(gate=GateId.G1, passed=False, measured={**measured, **over}, reason=reason)

    # --- 1. every declared key must exist in this template's schema -------------------------
    known = set(schema.keys())
    missing = sorted(k for k in cand.schema_keys if k not in known)
    if missing:
        return reject(Reason.KEY_NOT_IN_SCHEMA, missing_keys=missing[:8], n_missing=len(missing))

    # --- 2. an UNRESOLVED key blocks; it never degrades to a guess --------------------------
    unresolved = sorted(k for k in cand.schema_keys if _is_unresolved(schema, k))
    if unresolved:
        return reject(Reason.KEY_UNRESOLVED, unresolved_keys=unresolved[:8], n_unresolved=len(unresolved))

    # --- 3. admission rule R2: the host-function registry is CLOSED ------------------------
    registered = set(_registered(hostfns))
    unregistered = sorted(set(cand.host_fns) - registered)
    if unregistered:
        return reject(Reason.HOST_FN_UNREGISTERED, unregistered=unregistered)

    # --- 4. BINDING, BEFORE `expr` (D-P5-01) ------------------------------------------------
    # `all([])` is True. A predicate that binds nothing must never get as far as evaluating an
    # expression that would return a clean pass over no cells.
    cells = tuple(sorted(bound_cells(cand, schema)))
    measured["cells_bound"] = len(cells)
    if not cells:
        return reject(Reason.CELLS_BOUND_ZERO, cells_bound=0)

    # --- 5. it must EXECUTE ------------------------------------------------------------------
    filing, template = facts.view("filing"), facts.view("template")
    for slot in ("applicable", "expr"):
        res = rt.evaluate(rt.compile(getattr(cand, slot), slot=slot), filing=filing, template=template)
        measured[f"{slot}_outcome"] = res.outcome.value
        measured[f"{slot}_steps"] = res.steps
        if res.outcome is Outcome.BUDGET_EXCEEDED:
            return reject(Reason.BUDGET_EXHAUSTED, slot=slot, budget=res.budget)
        if res.outcome is Outcome.ERROR:
            return reject(Reason.RAISED, slot=slot, error=res.error)
        # INPUT_UNAVAILABLE is not a G1 rejection: a host function with no bound snapshot is a
        # property of THIS admission run, not of the candidate. It is recorded and the gate
        # continues, because rejecting here would make admission depend on what happened to be
        # loaded rather than on the predicate.
        if res.outcome is Outcome.INPUT_UNAVAILABLE:
            measured[f"{slot}_input_unavailable"] = res.error or "no snapshot bound"

    return GateOutcome(gate=GateId.G1, passed=True, measured=measured)


def _is_unresolved(schema: Any, key: str) -> bool:
    """A key whose resolution state is UNRESOLVED. It BLOCKS.

    The schema's field map is `{key: frozenset(cells)}`; a key that resolved to no cell at all is
    the unresolved case, and admitting it would let a version bump silently rebind the predicate to
    a different row of the same table (NC-D04a's mechanism, caught here at admission as well as at
    induction).
    """
    if key not in schema.keys():
        return False  # reported as KEY_NOT_IN_SCHEMA, which is a different remedy
    # A `template.vocab.*` key legitimately binds no filing cell: it names a vocabulary in the
    # PINNED BLANK. Treating it as unresolved would reject every membership predicate.
    if key.startswith("template."):
        return False
    return not schema.cells_for(key)


def _registered(hostfns: Any) -> Sequence[str]:
    for attr in ("names", "registered", "keys"):
        fn = getattr(hostfns, attr, None)
        if callable(fn):
            return list(fn())
    return list(getattr(hostfns, "_fns", {}) or {})
