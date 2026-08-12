"""P5-B2 — the evaluation contract: code → doc by byte identity, code → spec by set equality."""

from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.contract import (  # noqa: E402
    TRANSITION_COUNT,
    TRANSITIONS,
    ContractViolation,
    EmptyReadSetError,
    RunStateEffect,
    assert_permitted,
    compose_retrieved_at,
    compose_warrant,
    transition,
)
from cdfc.facts.anchor import Warrant  # noqa: E402
from cdfc.verdict import ItemState, ReasonCode  # noqa: E402

DOC = REPO / "EVALUATION-CONTRACT.md"
PINNED = REPO / "tests" / "contract" / "expected" / "spec_II_3_4_transitions.json"


def test_contract__transitions_has_exactly_nine_rows() -> None:
    assert len(TRANSITIONS) == TRANSITION_COUNT == 9
    assert [t.order for t in TRANSITIONS] == list(range(1, 10)), "orders are dense and sorted"
    assert {t.rule for t in TRANSITIONS} == {1, 2, 3, 5}, (
        "rule 4 is composition, not a transition — compose_warrant / compose_retrieved_at"
    )


def test_contract__evaluation_contract_matches_evaluator() -> None:
    """Set equality against the spec's table, extracted once and pinned."""
    pinned = json.loads(PINNED.read_text(encoding="utf-8"))["transitions"]
    ours = [t.as_row() for t in TRANSITIONS]
    key = lambda r: r["order"]  # noqa: E731
    assert sorted(ours, key=key) == sorted(pinned, key=key), (
        "the evaluator's transition table has drifted from the pinned extraction of the "
        "specification's five rules. The extraction moves only with a decision record."
    )


def test_contract__the_pinned_extraction_is_not_generated_from_the_code() -> None:
    """A pinned extraction generated from the thing it checks is `x == x`."""
    doc = json.loads(PINNED.read_text(encoding="utf-8"))
    assert "spec" in doc["source"].lower()
    assert "x == x" in doc["note"], "the file must record why it is hand-extracted"


def test_contract__generated_doc_is_byte_identical() -> None:
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "gen_contract.py")],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "unchanged" in r.stdout, (
        f"EVALUATION-CONTRACT.md is not what the generator produces: {r.stdout!r}. It is "
        "generated, never hand-edited."
    )


def test_contract__the_doc_carries_every_row() -> None:
    text = DOC.read_text(encoding="utf-8")
    for t in TRANSITIONS:
        assert f"| {t.order} | {t.rule} | {t.trigger} |" in text


def test_contract__every_transition_declares_its_never_set() -> None:
    """A row with no `never` must be one that genuinely forbids nothing, not one that forgot."""
    forbidding = [t for t in TRANSITIONS if t.never]
    assert len(forbidding) == 6
    for t in TRANSITIONS:
        assert t.state not in t.never, f"order {t.order} forbids the state it produces"
        if t.state is None:
            assert t.never == (), "a continue row realises no state, so it forbids none"


def test_contract__never_sets_are_enforced_at_runtime() -> None:
    """The spec's bracketed comments as an executable guarantee, fuzzed over every pair."""
    checked = violations = 0
    for t in TRANSITIONS:
        for state in ItemState:
            checked += 1
            if state in t.never:
                with pytest.raises(ContractViolation):
                    assert_permitted(t.order, state)
                violations += 1
            else:
                assert_permitted(t.order, state)
    assert checked == 9 * 8
    assert violations == sum(len(t.never) for t in TRANSITIONS) == 11


def test_contract__cells_bound_zero_is_evaluated_before_preflight_and_expr() -> None:
    """D-P5-01. `all([])` is True; the vacuous pass must be unreachable, not repaired."""
    zero = transition(4)
    assert zero.trigger == "cells_bound == 0"
    assert zero.state is ItemState.ERROR and zero.reason is ReasonCode.ERR_CELLS_BOUND_ZERO
    assert zero.run_state_effect is RunStateEffect.INVALID
    preflight = next(t for t in TRANSITIONS if "declared key" in t.trigger)
    exprs = [t for t in TRANSITIONS if t.trigger.startswith("expr")]
    assert zero.order < preflight.order
    assert all(zero.order < t.order for t in exprs)
    assert ItemState.PASS in zero.never


def test_contract__raised_and_unreadable_have_different_reasons_and_effects() -> None:
    """NC-E01: opposite remedies. Fix the code, or retry the source."""
    raised = transition(7)
    unreadable = transition(5)
    assert raised.reason is ReasonCode.ERR_PREDICATE_RAISED
    assert unreadable.reason is ReasonCode.NR_SOURCE_UNREADABLE
    assert raised.state is not unreadable.state
    assert raised.run_state_effect is RunStateEffect.INVALID
    assert unreadable.run_state_effect is RunStateEffect.UNCHANGED


def test_contract__only_the_two_error_rows_invalidate_the_run() -> None:
    invalidating = [t.order for t in TRANSITIONS if t.run_state_effect is RunStateEffect.INVALID]
    assert invalidating == [4, 7]
    for t in TRANSITIONS:
        expected = t.state is ItemState.ERROR
        assert (t.run_state_effect is RunStateEffect.INVALID) is expected


# --- rule 4: composition ---------------------------------------------------------------------


def test_compose_warrant__is_the_weakest_input() -> None:
    assert compose_warrant([Warrant.DETERMINISTIC, Warrant.DETERMINISTIC]) is Warrant.DETERMINISTIC
    assert compose_warrant([Warrant.DETERMINISTIC, Warrant.MODEL_EXTRACTED]) is Warrant.MODEL_EXTRACTED
    assert compose_warrant([Warrant.MODEL_EXTRACTED, Warrant.DERIVED]) is Warrant.DERIVED


def test_compose_warrant__the_empty_set_raises() -> None:
    """Returning DETERMINISTIC here is how a constant acquires a provenance."""
    with pytest.raises(EmptyReadSetError, match="derived from nothing"):
        compose_warrant([])


def test_compose_retrieved_at__is_the_stalest_input_not_the_freshest() -> None:
    """The plan annotates this `# max`, two lines below its own rule. `min` is the reading that
    makes the rule true; under `max` a nine-month-old snapshot reports as today."""
    old = _dt.datetime(2026, 1, 31, 12, 0, tzinfo=_dt.UTC)
    new = _dt.datetime(2026, 8, 12, 9, 0, tzinfo=_dt.UTC)
    assert compose_retrieved_at([new, old]) == old
    assert compose_retrieved_at([old]) == old
    with pytest.raises(EmptyReadSetError):
        compose_retrieved_at([])
