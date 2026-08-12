"""P5-B3 — the eight item states, the precedence order, and the whole of the removal policy.

**`PRECEDENCE` is binding and it is the audit's resolution.** The withdrawn `PASS ≻ NOT_RUN`
ordering made this sentence false in exactly the case it was written for: *on reader disagreement
every predicate reading the field returns `NOT_RUN(extractor_disagreement)` and the settled
fraction falls, it does not silently succeed.* Under the withdrawn order a cell read by one
passing and one not-run predicate rolled up to `PASS`. **A check that did not run must never be
absorbed by one that did.**

**`NO_PREDICATE` is deliberately not in `PRECEDENCE`.** It is not a verdict competing with others;
it is the state of a cell whose evaluation set is *empty*. Putting it in the order would let it be
beaten by a verdict that does not exist.

**Denominator membership is a function of `(state, reason, scope_kind)`, never of state alone.**
`REMOVAL_BASIS` plus the retention rule below is the *whole* removal policy, and `in_scope()` is
the only function that implements it — a second place that removes a cell from the denominator is
a defect no test of this table can see, which is why `partition()` consults `in_scope()` and
nothing else.

**The retention rule, which is the whole of the D-P5-05 repair:**

> Only `scope_kind == DECLARED_CHARACTERISTIC` leaves the in-scope denominator.
> `scope_kind == PREDICATE_PRECONDITION` **stays**, and is flagged for G3 re-qualification.

A predicate whose `applicable` is degenerate is not telling you something about the filing. It is
telling you something about **the predicate** — and letting it remove a cell from the denominator
lets a bad predicate shrink the thing it is measured against. Under this rule nothing a predicate
does to itself can make the settled fraction rise.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Final

from cdfc.probes.relations import LEAVES_IN_SCOPE, ScopeKind
from cdfc.verdict.reasons import FAMILIES, ReasonCode, ReasonDisciplineError, family_of


class ItemState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INDETERMINATE = "INDETERMINATE"
    NOT_RUN = "NOT_RUN"
    NO_PREDICATE = "NO_PREDICATE"
    ERROR = "ERROR"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    INFORMATIONAL = "INFORMATIONAL"


ITEM_STATE_COUNT: Final[int] = 8

# Highest first. `roll_up` takes the max under this order, so a cell is clean only if EVERY
# predicate binding it passed.
PRECEDENCE: Final[tuple[ItemState, ...]] = (
    ItemState.ERROR,
    ItemState.FAIL,
    ItemState.INDETERMINATE,
    ItemState.NOT_RUN,
    ItemState.PASS,
    ItemState.INFORMATIONAL,
    ItemState.OUT_OF_SCOPE,
)

_RANK: Final[Mapping[ItemState, int]] = {s: i for i, s in enumerate(PRECEDENCE)}

SETTLED: Final[frozenset[ItemState]] = frozenset({ItemState.PASS, ItemState.FAIL})
ERROR_STATES: Final[frozenset[ItemState]] = frozenset({ItemState.ERROR})


class MissingScopeKindError(ValueError):
    """`OUT_OF_SCOPE(not_applicable)` with no `scope_kind`. Fails closed; never guesses.

    Defaulting either way is a decision about the denominator taken by whoever forgot the field.
    """

    def __init__(self, state: ItemState, reason: ReasonCode | None) -> None:
        self.state = state
        self.reason = reason
        super().__init__(
            f"{state} / {reason} carries no scope_kind. Whether this cell leaves the in-scope "
            "denominator depends on it, and a default would be a denominator decision nobody made."
        )


class RemovalBasis(StrEnum):
    TEMPLATE = "TEMPLATE"
    SELECTION = "SELECTION"
    DECLARED_CHARACTERISTIC = "DECLARED_CHARACTERISTIC"


# A pair ABSENT from this table stays in `inScope`. **The default is to count, never to remove.**
REMOVAL_BASIS: Final[Mapping[tuple[ItemState, ReasonCode | None], RemovalBasis]] = {
    (ItemState.OUT_OF_SCOPE, ReasonCode.OOS_NOT_APPLICABLE): RemovalBasis.DECLARED_CHARACTERISTIC,
    (ItemState.OUT_OF_SCOPE, ReasonCode.OOS_NOT_SELECTED): RemovalBasis.SELECTION,
    (ItemState.OUT_OF_SCOPE, ReasonCode.OOS_WITHHELD): RemovalBasis.SELECTION,
    (ItemState.INFORMATIONAL, None): RemovalBasis.TEMPLATE,
}


def rank(state: ItemState) -> int:
    """Position in `PRECEDENCE`. `NO_PREDICATE` is not in it, and asking raises."""
    if state not in _RANK:
        raise KeyError(
            f"{state} is not in PRECEDENCE. NO_PREDICATE is the state of a cell whose evaluation "
            "set is EMPTY; it does not compete with verdicts and must not be ordered against them."
        )
    return _RANK[state]


def worst(states: tuple[ItemState, ...]) -> ItemState:
    """Max under `PRECEDENCE`. Total, so the result cannot depend on evaluation order."""
    if not states:
        raise ValueError("an empty evaluation set has no maximum; it is NO_PREDICATE")
    return min(states, key=rank)


def in_scope(
    state: ItemState,
    reason: ReasonCode | None,
    scope_kind: ScopeKind | None = None,
) -> bool:
    """THE only removal decision in the system. `closure.partition()` consults this and nothing else."""
    if (state, reason) not in REMOVAL_BASIS:
        return True
    if (state, reason) == (ItemState.OUT_OF_SCOPE, ReasonCode.OOS_NOT_APPLICABLE):
        if scope_kind is None:
            raise MissingScopeKindError(state, reason)
        # PREDICATE_PRECONDITION is RETAINED. See this module's docstring for why.
        return scope_kind != LEAVES_IN_SCOPE
    return False


def requalification_flag(scope_kind: ScopeKind | None) -> bool:
    """A cell retained for a degenerate precondition does not merely stay counted — it accuses
    its own predicate. Being counted is not the punishment; being re-qualified is."""
    return scope_kind == "PREDICATE_PRECONDITION"


# --- the join between the two vocabularies ------------------------------------------------
#
# It lives here rather than in `reasons.py` because `REMOVAL_BASIS` needs `ReasonCode` for its
# keys, so the dependency has to run one way. See the note at the foot of `reasons.py`.

_STATE_OF_FAMILY: Final[Mapping[str, ItemState]] = {
    "no_predicate": ItemState.NO_PREDICATE,
    "not_run": ItemState.NOT_RUN,
    "indeterminate": ItemState.INDETERMINATE,
    "out_of_scope": ItemState.OUT_OF_SCOPE,
    "error": ItemState.ERROR,
}

# The family IS the state. Derived from the code strings rather than written out a second time:
# a hand-written table beside the enum is a second list, and the one that drifts is the one
# nobody is reading.
FAMILY: Final[Mapping[ReasonCode, ItemState]] = {
    c: _STATE_OF_FAMILY[family_of(c)] for c in ReasonCode
}

# D-P5-02. `INFORMATIONAL` is the third state that carries no reason: it implies no remedy, and
# the spec's own admission test for a distinct reason is a distinct remedy. It carries a mandatory
# `informational_note` instead.
NO_REASON_STATES: Final[frozenset[ItemState]] = frozenset(
    {ItemState.PASS, ItemState.FAIL, ItemState.INFORMATIONAL}
)


def reason_required(state: ItemState) -> bool:
    return state not in NO_REASON_STATES


def validate_pair(
    state: ItemState, reason: ReasonCode | None, note: str | None = None
) -> None:
    """Accept or raise. There is no third outcome and no pair silently tolerated.

    `note` is the `informational_note`, required exactly when the state is `INFORMATIONAL`.
    """
    if reason_required(state):
        if reason is None:
            raise ReasonDisciplineError(
                f"{state} requires a reason code. A state that is neither settled nor "
                "informational and cannot say why is a silent skip."
            )
        expected = FAMILY[reason]
        if expected is not state:
            raise ReasonDisciplineError(
                f"{reason.value!r} belongs to {expected}, not to {state}. The family IS the "
                "state; a cross-family pair would let a report show a not-run reason on a cell "
                "that ran."
            )
        if note is not None:
            raise ReasonDisciplineError(f"{state} carries a reason code, not an informational note")
        return

    if reason is not None:
        raise ReasonDisciplineError(
            f"{state} carries no reason code; got {reason.value!r}. For PASS and FAIL the "
            "predicate IS the reason, and attaching one here would let two different things be "
            "read off one field."
        )
    if state is ItemState.INFORMATIONAL:
        if not note:
            raise ReasonDisciplineError(
                "INFORMATIONAL requires an informational_note (D-P5-02). Without it the state "
                "says a template defect exists and nothing about which one."
            )
        return
    if note is not None:
        raise ReasonDisciplineError(f"{state} carries no informational_note")


assert set(_STATE_OF_FAMILY) == set(FAMILIES), "the five families and their states have diverged"
