"""P5-B2 — THE evaluation contract. This module is the source of truth; the markdown is generated.

**Why not "generated from the five rules of spec §II.3.4" literally.** Taken literally that means
parsing prose in CI, and a gate that goes red because a paragraph reflowed is a gate that gets
disabled. The arrangement is three-way, and each edge is checked a different way:

    contract.py::TRANSITIONS  --(byte identity)-->  EVALUATION-CONTRACT.md
             |
             +--(set equality)--> tests/contract/expected/spec_II_3_4_transitions.json
                                  the spec's table, extracted ONCE and pinned

The extraction moves only with a decision record — which is how the spec's own five rules should
move, since **three different versions of them were live at once and a build cannot satisfy two
fives.**

**`order` is not `rule`.** `rule` is the spec's conceptual numbering; `order` is the order the
evaluator actually applies them, and D-P5-01 puts `cells_bound == 0` at order 4 — *before*
pre-flight and *before* `expr`. `all([])` is `True`, so a design that lets the vacuous pass be
produced and then corrected is trusting itself to overwrite a `PASS`. **The vacuous pass must be
unreachable, not repaired.**

**Rows 4 and 7 against each other.** A predicate that *raised* is an apparatus failure — fix the
code. A source that could not be read is `not_run.source_unreadable` — retry. **They have opposite
remedies**, and collapsing them is NC-E01.

**Rule 4 of the spec is not a transition.** It is `compose_warrant` / `compose_retrieved_at`:
*a verdict is never fresher than its stalest input and never stronger than its weakest.*
"""

from __future__ import annotations

import datetime as _dt
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final

from cdfc.facts.anchor import Warrant
from cdfc.verdict import ItemState, ReasonCode


class RunStateEffect(StrEnum):
    UNCHANGED = "UNCHANGED"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class Transition:
    order: int
    rule: int
    trigger: str
    state: ItemState | None  # None == "continue to the next order"
    reason: ReasonCode | None
    run_state_effect: RunStateEffect
    never: tuple[ItemState, ...]  # the spec's "[never FAIL]" annotations, as assertions

    def as_row(self) -> dict[str, Any]:
        return {
            "order": self.order,
            "rule": self.rule,
            "trigger": self.trigger,
            "state": None if self.state is None else self.state.value,
            "reason": None if self.reason is None else self.reason.value,
            "run_state_effect": self.run_state_effect.value,
            "never": [s.value for s in self.never],
        }


_S = ItemState
_R = ReasonCode
_U = RunStateEffect.UNCHANGED
_I = RunStateEffect.INVALID

TRANSITIONS: Final[tuple[Transition, ...]] = (
    Transition(1, 1, "applicable errors", _S.NOT_RUN, _R.NR_SOURCE_UNREADABLE, _U, (_S.FAIL,)),
    Transition(
        2, 1, "applicable false", _S.OUT_OF_SCOPE, _R.OOS_NOT_APPLICABLE, _U, (_S.PASS, _S.FAIL)
    ),
    Transition(3, 1, "applicable true", None, None, _U, ()),
    # D-P5-01: BEFORE pre-flight and BEFORE expr. `all([])` is True.
    Transition(
        4, 5, "cells_bound == 0", _S.ERROR, _R.ERR_CELLS_BOUND_ZERO, _I, (_S.PASS, _S.NOT_RUN)
    ),
    Transition(
        5, 2, "declared key absent or mistyped", _S.NOT_RUN, _R.NR_SOURCE_UNREADABLE, _U,
        (_S.PASS, _S.FAIL),
    ),
    Transition(6, 3, "expr budget exceeded", _S.NOT_RUN, _R.NR_BUDGET_EXHAUSTED, _U, (_S.FAIL,)),
    Transition(
        7, 3, "expr runtime error", _S.ERROR, _R.ERR_PREDICATE_RAISED, _I,
        (_S.NOT_RUN, _S.PASS, _S.FAIL),
    ),
    Transition(8, 3, "expr false", _S.FAIL, None, _U, ()),
    Transition(9, 3, "expr true", _S.PASS, None, _U, ()),
)

TRANSITION_COUNT: Final[int] = 9


def transition(order: int) -> Transition:
    for t in TRANSITIONS:
        if t.order == order:
            return t
    raise KeyError(f"no transition at evaluation order {order}")


def never_set(order: int) -> frozenset[ItemState]:
    return frozenset(transition(order).never)


class ContractViolation(AssertionError):
    """A realised state that the transition's own `never` set forbids."""


def assert_permitted(order: int, state: ItemState) -> None:
    """Turn the spec's bracketed `[never FAIL]` comments into an executable guarantee."""
    forbidden = never_set(order)
    if state in forbidden:
        raise ContractViolation(
            f"order {order} ({transition(order).trigger}) produced {state}, which its own "
            f"never-set forbids: {sorted(s.value for s in forbidden)}"
        )


# --- rule 4: composition, which is not a transition -----------------------------------------


class EmptyReadSetError(ValueError):
    """`compose_warrant` over no inputs. `cells_bound == 0` already owns this at order 4."""


def compose_warrant(warrants: Iterable[Warrant]) -> Warrant:
    """The minimum under `DETERMINISTIC > MODEL_EXTRACTED > DERIVED`. Never stronger than its
    weakest input: a sum of three deterministic reads and one extracted value is MODEL_EXTRACTED.

    The empty set RAISES rather than returning `DETERMINISTIC`. An empty read set means
    `cells_bound == 0`, and order 4 already owns that — returning the strongest warrant for a
    value derived from nothing is how a constant acquires a provenance.
    """
    ws = list(warrants)
    if not ws:
        raise EmptyReadSetError(
            "compose_warrant over an empty read set. A value derived from nothing is not "
            "deterministic; cells_bound == 0 is ERROR(error.cells_bound_zero) at order 4."
        )
    return min(ws)


def compose_retrieved_at(stamps: Iterable[_dt.datetime]) -> _dt.datetime:
    """The MINIMUM — the OLDEST retrieval. **This contradicts the plan's annotation, and the
    correction is recorded rather than glossed.**

    The plan's interface block writes `def compose_retrieved_at(facts) -> datetime  # max`, two
    lines below its own statement of the rule: *a verdict is never fresher than its stalest input
    and never stronger than its weakest.* The two cannot both hold. The stalest input is the one
    retrieved LONGEST AGO, i.e. the smallest datetime, so the bound on the composite's freshness
    is the minimum.

    Under `max`, a verdict composed from a register snapshot taken in January and a filing read
    today would report today — and a reader would take the whole verdict to be that fresh when
    part of it is nine months old. That is the overstatement this product exists to prevent,
    produced by the composition function written to prevent it. `min` is the reading that makes
    the plan's own sentence true, and it is the one implemented.

    No clock is read here: every stamp is an argument recorded in the manifest.
    """
    ss = list(stamps)
    if not ss:
        raise EmptyReadSetError("compose_retrieved_at over an empty input set")
    return min(ss)
