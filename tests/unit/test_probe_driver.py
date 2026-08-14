"""P9-B3 — the driver. The `FAIL` / `INFORMATIONAL` split, the budget, and the witness rule."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.driver import (  # noqa: E402
    DEFAULT_MAX_EXAMPLES,
    Budget,
    ProbeError,
    ProbeMachine,
    ProbeResult,
    manifest_entry,
    run_probes,
    shrink,
)
from cdfc.probes.examples import PIN_IDS, PINS  # noqa: E402
from cdfc.probes.relations.registry import load, parse_row  # noqa: E402
from cdfc.verdict.reasons import ReasonCode  # noqa: E402
from cdfc.verdict.states import ItemState  # noqa: E402


def _spec(**over):
    base = {
        "id": "R-99", "title": "t", "necessity": "NECESSARY", "inputs": "FILING_ONLY",
        "bases": ["INVESTOR_SIDE"], "precondition": "has(filing.a.v)", "expr": "filing.a.v == 1",
        "witness": "[filing.a.__cell__]", "evidence": "e", "claims_fault_classes": ["F01"],
        "reviewed_by": ["x"], "reviewed_at": "2026-08-14",
        "review_label": "SINGLE-SIGNER — a weaker review",
    }
    base.update(over)
    return parse_row(base)


def _held(_r, _s):
    return True, ("S!A1",), "held"


def _broken(_r, _s):
    return False, ("S!A1",), "did not hold"


def test_driver__invariant_maps_to_FAIL() -> None:
    r = run_probes([_spec()], state=None, evaluate=_broken)[0]
    assert r.state is ItemState.FAIL
    assert r.witness == ("S!A1",)


def test_driver__in_rule_assertion_maps_to_INFORMATIONAL_and_never_to_FAIL() -> None:
    spec = _spec(necessity="EXPECTED", guidance_note="the note that makes it lawful")
    m = ProbeMachine(relations=[spec], evaluate=_broken)
    r = m.check(spec, None)
    assert r.state is ItemState.INFORMATIONAL
    assert r.state is not ItemState.FAIL
    assert m.observations == [("R-99", "did not hold")]
    assert "lawful" in r.detail


def test_driver__the_split_is_the_specs_and_has_no_third_branch() -> None:
    for necessity, state in (("NECESSARY", ItemState.FAIL), ("EXPECTED", ItemState.INFORMATIONAL)):
        s = _spec(necessity=necessity, guidance_note="n")
        assert s.state_on_violation() is state


def test_driver__budget_exhaustion_is_NOT_RUN_never_FAIL() -> None:
    """A probe that ran out of time has told us nothing about the filing."""
    specs = [_spec(id=f"R-{i:02d}") for i in range(3)]
    m = ProbeMachine(relations=specs, evaluate=_broken, budget=Budget(1))
    first, second = m.check(specs[0], None), m.check(specs[1], None)
    assert first.state is ItemState.FAIL
    assert second.state is ItemState.NOT_RUN
    assert second.reason is ReasonCode.NR_BUDGET_EXHAUSTED
    assert second.state is not ItemState.FAIL


def test_driver__the_budget_is_checked_before_the_example_not_after() -> None:
    """Checked after, the last example overruns the budget it was admitted under — the shape
    that made `Budget(steps=2000)` unable to stop the 6 GB evaluation at P8."""
    b = Budget(2)
    assert b.take() and b.take()
    assert not b.take()
    assert b.used == 2


def test_driver__an_unrunnable_relation_reports_its_reason_and_spends_no_budget() -> None:
    by_id = {s.id: s for s in load()}
    m = ProbeMachine(relations=[by_id["R-07"]], evaluate=_broken)
    r = m.check(by_id["R-07"], None)
    assert r.state is ItemState.NOT_RUN
    assert r.reason is ReasonCode.NR_INPUT_UNAVAILABLE_PRIOR_PERIOD
    assert m.budget.used == 0, "an un-runnable relation must not consume an example"


def test_driver__a_fail_with_no_witness_cannot_be_constructed() -> None:
    with pytest.raises(ProbeError, match="no witness"):
        ProbeResult(
            relation_id="R-99", state=ItemState.FAIL, reason=None, scope_kind=None,
            witness=(), detail="", examples_run=1, seed=0,
        )


def test_driver__results_are_in_catalogue_order() -> None:
    specs = load()
    out = run_probes(specs, state=None, evaluate=_held)
    assert [r.relation_id for r in out] == [s.id for s in specs]


def test_driver__the_seed_is_recorded_on_every_result_and_in_the_manifest() -> None:
    out = run_probes([_spec()], state=None, evaluate=_held, seed=1234)
    assert all(r.seed == 1234 for r in out)
    assert manifest_entry(out)["probe_seed"] == 1234


def test_driver__shrink_reduces_a_counterexample_to_its_smallest_form() -> None:
    """An un-shrunk counterexample over two hundred deleted cells names the whole filing and
    points at nothing."""
    cells = [f"S!A{i}" for i in range(1, 11)]

    def still_fails(trial):
        return "S!A7" in trial

    assert shrink(cells, still_fails, Budget(500)) == ("S!A7",)


def test_driver__shrink_stops_when_the_budget_is_spent() -> None:
    cells = [f"S!A{i}" for i in range(1, 51)]
    b = Budget(3)
    out = shrink(cells, lambda t: "S!A50" in t, b)
    assert b.exhausted
    assert len(out) > 1, "a bounded shrink returns a larger witness rather than running forever"


def test_examples__every_real_defect_is_pinned() -> None:
    """APPEND-ONLY. A removed entry fails the build."""
    assert len(PINS) >= 5
    assert PIN_IDS >= {"EX-01", "EX-02", "EX-03", "EX-04", "EX-05"}
    for p in PINS:
        assert p.defect and p.example and p.guard and p.dated
        assert p.guard.startswith("tests/") or p.guard.startswith("make ")


def test_examples__ids_are_unique_and_sequential() -> None:
    ids = [p.id for p in PINS]
    assert ids == sorted(ids)
    assert len(set(ids)) == len(ids)


def test_driver__the_default_budget_is_the_specs_decided_one() -> None:
    assert DEFAULT_MAX_EXAMPLES == 50
