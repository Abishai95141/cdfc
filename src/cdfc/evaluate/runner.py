"""P5-B1 — F8: the evaluation loop, walking `contract.TRANSITIONS` in evaluation order.

**`evaluate_one` accepts `Predicate` and nothing else.** A `Candidate` is a type error at the call
site — barrier 3 in the type system — and `evaluate_one` also refuses one at runtime. Both are
kept, because the runtime one is the one you can prove to a reviewer.

**The order is the contract's, not a convenient one.** `cells_bound == 0` is checked at order 4,
before pre-flight and before `expr`, because `all([])` is `True` and a design that produces the
vacuous pass and then corrects it is trusting itself to overwrite a `PASS`.

Every state this module realises is passed through `assert_permitted`, so the specification's
bracketed `[never FAIL]` annotations are enforced rather than commented.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from cdfc.evaluate.celrt import CelResult, CelRuntime, Outcome
from cdfc.evaluate.contract import RunStateEffect, assert_permitted, transition
from cdfc.evaluate.preflight import PreflightResult, preflight
from cdfc.evaluate.selection import Selection
from cdfc.predicates.ast_walker import KeyRef
from cdfc.predicates.envelope import Candidate, Predicate
from cdfc.verdict import InvalidCause, ItemState, ReasonCode, validate_pair


class NotAPredicateError(TypeError):
    """A `Candidate` reached the run path. Barrier 3, at runtime as well as in the type system."""


@dataclass(frozen=True, slots=True)
class RunCheck:
    predicate_id: str
    version: int
    state: ItemState
    reason: ReasonCode | None
    witness: tuple[str, ...]
    cells_bound: tuple[str, ...]
    order: int                       # which transition produced it — the audit trail, not a label
    settles: bool                    # PROVISIONAL predicates run and do not settle
    scope_kind: str | None = None
    informational_note: str | None = None
    keys_checked: int = 0
    keys_type_checked: int = 0
    detail: str = ""
    run_state_effect: RunStateEffect = RunStateEffect.UNCHANGED
    invalid_cause: InvalidCause | None = None

    def __post_init__(self) -> None:
        validate_pair(self.state, self.reason, self.informational_note)
        assert_permitted(self.order, self.state)


@dataclass(frozen=True, slots=True)
class RunOutcome:
    checks: tuple[RunCheck, ...]
    invalid_causes: tuple[InvalidCause, ...] = ()
    keys_checked: int = 0
    keys_type_checked: int = 0

    @property
    def run_state(self) -> str:
        return "INVALID" if self.invalid_causes else "VALID"


def bind_count(p: Predicate | Candidate, schema: Any) -> tuple[str, ...]:
    """The cells this predicate binds. Computed BEFORE `expr` — D-P5-01."""
    from cdfc.predicates.ast_walker import bound_cells

    return tuple(sorted(bound_cells(p, schema)))


def _check(order: int, **kw: Any) -> RunCheck:
    t = transition(order)
    assert t.state is not None, f"order {order} is a continue row and realises no state"
    return RunCheck(
        state=t.state,
        reason=t.reason,
        order=order,
        run_state_effect=t.run_state_effect,
        **kw,
    )


def evaluate_one(
    p: Predicate,
    *,
    facts: Any,
    schema: Any,
    rt: CelRuntime,
    settles: bool = True,
    scope_kind: str | None = None,
) -> RunCheck:
    """One predicate, one filing, one `RunCheck`. Never raises for a program-level failure."""
    if not isinstance(p, Predicate):
        raise NotAPredicateError(
            f"{getattr(p, 'id', p)!r} is a {type(p).__name__}, not a Predicate. A candidate has "
            "not been through the gates, and the settled-fraction claim rests on that being "
            "impossible rather than merely discouraged."
        )
    filing, template = facts.view("filing"), facts.view("template")
    common = {"predicate_id": p.id, "version": p.version, "settles": settles}

    # --- orders 1-3: applicable ------------------------------------------------------------
    applicable = _run(rt, p.applicable, "applicable", filing, template)
    if applicable.outcome is not Outcome.OK:
        return _check(
            1, witness=(), cells_bound=(), detail=applicable.error or "", **common
        )
    if applicable.value is not True:
        # Order 2 carries `out_of_scope.not_applicable`, which REQUIRES a scope_kind. The runner
        # cannot invent one: `applicable` returning false because a table is absent is a statement
        # about the PREDICATE's precondition, and that is the retained kind. A caller with better
        # information passes its own.
        return _check(
            2, witness=(), cells_bound=(),
            scope_kind=scope_kind or "PREDICATE_PRECONDITION",
            detail=p.reason_if_inapplicable, **common,
        )

    # --- order 4: cells_bound == 0, BEFORE pre-flight and BEFORE expr (D-P5-01) -------------
    bound = bind_count(p, schema)
    if not bound:
        return _check(
            4, witness=(), cells_bound=(),
            detail=(
                "this predicate binds no cell of the pinned template. `all([])` is True, so a "
                "design that evaluated it and then corrected the PASS would be trusting itself "
                "to overwrite one."
            ),
            invalid_cause=InvalidCause.CELLS_BOUND_ZERO, **common,
        )

    # --- order 5: pre-flight ----------------------------------------------------------------
    pf: PreflightResult = preflight(p, facts)
    if not pf.proceed:
        return _check(
            5, witness=(), cells_bound=bound,
            keys_checked=pf.keys_checked, keys_type_checked=pf.keys_type_checked,
            detail=_preflight_detail(pf), **common,
        )

    # --- orders 6-9: expr --------------------------------------------------------------------
    result = _run(rt, p.expr, "expr", filing, template)
    if result.outcome is Outcome.BUDGET_EXCEEDED:
        return _check(
            6, witness=(), cells_bound=bound,
            keys_checked=pf.keys_checked, keys_type_checked=pf.keys_type_checked,
            detail=result.error or "", **common,
        )
    if result.outcome is not Outcome.OK:
        return _check(
            7, witness=(), cells_bound=bound,
            keys_checked=pf.keys_checked, keys_type_checked=pf.keys_type_checked,
            detail=result.error or "", invalid_cause=InvalidCause.PREDICATE_RAISED, **common,
        )
    if result.value is True:
        return _check(
            9, witness=(), cells_bound=bound,
            keys_checked=pf.keys_checked, keys_type_checked=pf.keys_type_checked, **common,
        )

    witness = _run(rt, p.witness, "witness", filing, template)
    return _check(
        8,
        witness=tuple(witness.value or ()) if witness.outcome is Outcome.OK else (),
        cells_bound=bound,
        keys_checked=pf.keys_checked, keys_type_checked=pf.keys_type_checked,
        detail="" if witness.outcome is Outcome.OK else f"witness: {witness.error}",
        **common,
    )


def _preflight_detail(pf: PreflightResult) -> str:
    if pf.missing:
        return f"declared key absent: {pf.missing[0]}"
    key, expected, actual = pf.mistyped[0]
    return f"declared key mistyped: {key} expected {expected}, found {actual}"


def _run(rt: CelRuntime, source: str, slot: str, filing: Any, template: Any) -> CelResult:
    try:
        prog = rt.compile(source, slot=slot)  # type: ignore[arg-type]
    except Exception as e:  # noqa: BLE001 — a compile failure IS a program-level failure
        return CelResult(outcome=Outcome.ERROR, value=None, error=f"compile: {e}", steps=0)
    return rt.evaluate(prog, filing=filing, template=template)


def evaluate_all(sel: Selection, *, facts: Any, schema: Any, rt: CelRuntime) -> RunOutcome:
    checks: list[RunCheck] = []
    settling = sel.settles
    for p in sel.runnable:
        checks.append(
            evaluate_one(p, facts=facts, schema=schema, rt=rt, settles=p.id in settling)
        )
    causes = tuple(
        sorted({c.invalid_cause for c in checks if c.invalid_cause is not None}, key=str)
    )
    return RunOutcome(
        checks=tuple(checks),
        invalid_causes=causes,
        keys_checked=sum(c.keys_checked for c in checks),
        keys_type_checked=sum(c.keys_type_checked for c in checks),
    )


def unbound_checks(predicate_ids: Sequence[str]) -> tuple[RunCheck, ...]:
    """Every item on an UNBOUND run carries `not_run.template_unbound`.

    The run-level `invalid.template_unbound` is carried beside it, not instead of it — audit
    §V.7.3. They are not alternatives, and a report with one and not the other has lost either the
    location or the run-level consequence.
    """
    return tuple(
        RunCheck(
            predicate_id=pid, version=0, state=ItemState.NOT_RUN,
            reason=ReasonCode.NR_TEMPLATE_UNBOUND, witness=(), cells_bound=(),
            order=5, settles=False,
            detail="the filing did not bind to any pinned template",
        )
        for pid in sorted(predicate_ids)
    )


def key_grammar_ok(p: Predicate) -> bool:
    """Every declared key is writable in D-P4-02's grammar. Cheap, and it fails loudly."""
    for k in p.schema_keys:
        KeyRef.parse(k)
    return True
