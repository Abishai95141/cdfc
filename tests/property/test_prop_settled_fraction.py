"""P5-B4 — the properties the headline number rests on.

`test_prop__fraction_does_not_rise_as_the_filing_empties` is the phase's second no-fallback
criterion. **A settled fraction that rises when a filer fills in less is not a smaller product; it
is a product whose headline number rewards the behaviour it exists to detect.**

The property is stated over the ARITHMETIC, exhaustively and cheaply, because that is where the
hole was: `inScope = cellsTotal - outOfScope - informational` with both subtrahends reachable by
deleting values. The REAL pipeline is exercised on the same claim in
`tests/golden/test_p5_runtime.py`, where a run takes tens of seconds and three cases are affordable.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.rollup import Evaluation, RunCell, roll_up  # noqa: E402
from cdfc.verdict import PRECEDENCE, ItemState, ReasonCode, rank, worst  # noqa: E402
from cdfc.verdict.closure import TERMS, assert_closed, partition  # noqa: E402
from cdfc.verdict.settled_fraction import (  # noqa: E402
    Denominator,
    assert_fraction_did_not_rise,
    compute,
    fraction_of,
)

S = ItemState
R = ReasonCode
SLOW = settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])

REASON_FOR = {
    S.INDETERMINATE: R.IND_TOLERANCE_STRADDLE,
    S.NOT_RUN: R.NR_SOURCE_UNREADABLE,
    S.NO_PREDICATE: R.NP_NOT_YET_SYNTHESISED,
    S.ERROR: R.ERR_PREDICATE_RAISED,
    S.OUT_OF_SCOPE: R.OOS_NOT_SELECTED,
}

# The states a VALUE DELETION can produce, and the reason each is reachable.
#
#   PASS/FAIL -> NOT_RUN            pre-flight finds a declared key absent
#   PASS/FAIL -> OUT_OF_SCOPE       `applicable` becomes false — a statement about the PREDICATE,
#                                   so scope_kind is PREDICATE_PRECONDITION and the cell is RETAINED
#   PASS/FAIL -> NO_PREDICATE       every binding evaluation went away
#
# A deletion can never produce `DECLARED_CHARACTERISTIC`: that basis is a fact about the filer or
# the template, and no cell value participates in it. **That is the whole of the ruling.**
DELETION_TARGETS = (S.NOT_RUN, S.OUT_OF_SCOPE, S.NO_PREDICATE)


def _cell(i: int, state: ItemState, scope_kind: str | None = None) -> RunCell:
    return RunCell(
        stable_key=f"S!A{i}", state=state, reason=REASON_FOR.get(state),
        settled_by=None, evaluations=(), scope_kind=scope_kind,
    )


def _delete(c: RunCell, target: ItemState) -> RunCell:
    scope = "PREDICATE_PRECONDITION" if target is S.OUT_OF_SCOPE else None
    reason = R.OOS_NOT_APPLICABLE if target is S.OUT_OF_SCOPE else REASON_FOR.get(target)
    return RunCell(stable_key=c.stable_key, state=target, reason=reason,
                   settled_by=None, evaluations=(), scope_kind=scope)


def _den(n: int) -> Denominator:
    return Denominator("mask", "v3", n, True, "PROVISIONAL-UNVALIDATED")


class _Sel:
    active = ()
    provisional = ()


ANY_STATE = st.sampled_from([s for s in ItemState if s is not S.INFORMATIONAL])


@SLOW
@given(
    states=st.lists(ANY_STATE, min_size=1, max_size=60),
    which=st.lists(st.integers(0, 59), max_size=20),
    target=st.sampled_from(DELETION_TARGETS),
)
def test_prop__fraction_does_not_rise_as_the_filing_empties(
    states: list[ItemState], which: list[int], target: ItemState
) -> None:
    cells = [_cell(i, s) for i, s in enumerate(states)]
    before = compute(partition(cells, len(cells)), _Sel(), _den(len(cells)), "VALID")
    after_cells = [
        _delete(c, target) if i in set(which) and c.state in (S.PASS, S.FAIL) else c
        for i, c in enumerate(cells)
    ]
    after = compute(partition(after_cells, len(cells)), _Sel(), _den(len(cells)), "VALID")
    assert_fraction_did_not_rise(before, after, note=f"deleting {len(set(which))} value(s)")


@SLOW
@given(states=st.lists(ANY_STATE, min_size=1, max_size=60), which=st.lists(st.integers(0, 59), max_size=20))
def test_prop__deleting_a_value_never_moves_a_cell_out_of_inScope(
    states: list[ItemState], which: list[int]
) -> None:
    """The narrower invariant that localises a failure of the above."""
    cells = [_cell(i, s) for i, s in enumerate(states)]
    for target in DELETION_TARGETS:
        after = [
            _delete(c, target) if i in set(which) and c.state in (S.PASS, S.FAIL) else c
            for i, c in enumerate(cells)
        ]
        moved = [
            c.stable_key for c, a in zip(cells, after, strict=True)
            if c.in_scope and not a.in_scope
        ]
        assert moved == [], (
            f"deleting a value moved {moved} out of inScope via {target}. A counterexample names "
            "the (state, reason) pair, which is the line of states.py to change."
        )


@SLOW
@given(states=st.lists(ANY_STATE, min_size=1, max_size=200))
def test_prop__closure_seven_terms(states: list[ItemState]) -> None:
    cells = [_cell(i, s) for i, s in enumerate(states)]
    p = partition(cells, len(cells))
    assert sum(getattr(p, t) for t in TERMS) == p.cellsTotal == len(cells)
    assert_closed(p)


@SLOW
@given(states=st.lists(st.sampled_from(PRECEDENCE), min_size=1, max_size=12))
def test_prop__rollup_precedence_is_a_total_order(states: list[ItemState]) -> None:
    """A partial order would make the rolled-up state depend on evaluation order, and evaluation
    order is not part of the verdict."""
    forward = worst(tuple(states))
    assert forward is worst(tuple(reversed(states)))
    assert forward is min(states, key=rank)
    if len(states) >= 3:
        a, b, c = states[0], states[1], states[2]
        assert worst((worst((a, b)), c)) is worst((a, worst((b, c))))


@SLOW
@given(
    n_preds=st.integers(1, 12),
    n_cells=st.integers(1, 40),
    flip=st.integers(0, 11),
    seed=st.integers(0, 2**16),
)
def test_prop__settled_is_monotone_non_increasing_in_not_run(
    n_preds: int, n_cells: int, flip: int, seed: int
) -> None:
    """Turning any single evaluation from PASS into NOT_RUN never increases `settled`."""
    import random

    rnd = random.Random(seed)
    assume(flip < n_preds)
    per_cell = [
        [Evaluation(f"P-{p}", 1, S.PASS if rnd.random() < 0.7 else S.FAIL, None)
         for p in range(n_preds)]
        for _ in range(n_cells)
    ]
    def settled(vectors):
        cells = []
        for i, evs in enumerate(vectors):
            state, reason, sb, sk = roll_up(evs)
            cells.append(RunCell(f"S!A{i}", state, reason, sb, tuple(evs), sk))
        return partition(cells, n_cells).settled

    before = settled(per_cell)
    after_vectors = [
        [Evaluation(e.predicate_id, 1, S.NOT_RUN, R.NR_EXTRACTOR_DISAGREEMENT)
         if j == flip else e for j, e in enumerate(evs)]
        for evs in per_cell
    ]
    assert settled(after_vectors) <= before


def test_prop__the_generator_reaches_both_directions() -> None:
    """The admission-side control. A generator that never settles anything satisfies every
    property above by making every fraction zero."""
    passing = [_cell(i, S.PASS) for i in range(4)]
    assert fraction_of(partition(passing, 4)) == 1
    assert fraction_of(partition([_cell(0, S.NOT_RUN)], 1)) == 0
