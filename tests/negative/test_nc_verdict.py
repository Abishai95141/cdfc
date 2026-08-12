"""P5 — the negative controls for run assembly, the verdict model and closure.

Every entry ships with its admission-side twin. A guard that goes red under injection because it
goes red under everything is not a control.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import CelRuntime  # noqa: E402
from cdfc.evaluate.rollup import Evaluation, RunCell, materialise, roll_up  # noqa: E402
from cdfc.evaluate.runner import evaluate_one  # noqa: E402
from cdfc.facts.view import FactSet  # noqa: E402
from cdfc.measure.p5_run import fme_harvest, fme_surface, promote  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402
from cdfc.verdict import InvalidCause, ItemState, ReasonCode  # noqa: E402
from cdfc.verdict.closure import partition  # noqa: E402
from cdfc.verdict.settled_fraction import serialise  # noqa: E402

S, R = ItemState, ReasonCode


def _orphan():
    import dataclasses

    h = fme_harvest()
    return dataclasses.replace(
        promote(h.candidates[0]), id="P-ORPHAN",
        schema_keys=("filing.nowhere.at.all.v", "filing.nowhere.at.all.__cell__"),
        applicable="has(filing.nowhere.at.all.v)",
        expr="filing.nowhere.at.all.v >= 0",
        witness="[filing.nowhere.at.all.__cell__]",
    )


def _facts():
    return FactSet({"nowhere": {"at": {"all": {"v": 1, "__cell__": "S!A1"}}}}, {})


def _cell(key, state, reason=None, scope_kind=None):
    return RunCell(key, state, reason, None, (), scope_kind)


# --- NC-E20: the vacuous pass must be UNREACHABLE, not repaired ----------------------------


def test_nc__E20_cells_bound_zero_is_error_before_expr_runs() -> None:
    h = fme_harvest()
    chk = evaluate_one(_orphan(), facts=_facts(), schema=h.schema,
                       rt=CelRuntime(profile_version="P5", host_fns=default_registry()))
    assert chk.state is S.ERROR and chk.order == 4
    assert chk.reason is R.ERR_CELLS_BOUND_ZERO
    assert chk.invalid_cause is InvalidCause.CELLS_BOUND_ZERO


def test_nc__E20b_a_predicate_that_binds_cells_still_runs() -> None:
    """The admission side: order 4 does not swallow everything."""
    import dataclasses

    h = fme_harvest()
    real = promote(h.candidates[0])
    facts = FactSet({}, {})
    chk = evaluate_one(real, facts=facts, schema=h.schema,
                       rt=CelRuntime(profile_version="P5", host_fns=default_registry()))
    assert chk.state is not S.ERROR
    assert dataclasses.is_dataclass(chk)


# --- NC-E21: the cell table is the DENOMINATOR ----------------------------------------------


def test_nc__E21_run_cell_is_materialised_from_the_field_surface() -> None:
    n, cells, _ = fme_surface()
    assert len(materialise(cells)) == n == 3747


def test_nc__E21b_an_empty_evaluation_set_still_has_a_row() -> None:
    """The admission side: a cell nothing happened to is present, NO_PREDICATE, and IN SCOPE.

    One cell, deliberately. A control that asserted a COUNT would go red under any injector that
    truncates the table — including the one this entry declares — and a positive control that
    flips with the guard is not a control.
    """
    table = materialise(["S!A1"])
    assert set(table) == {"S!A1"}
    assert all(c.state is S.NO_PREDICATE and c.in_scope for c in table.values())


# --- NC-E22: null is not zero and not omitted ------------------------------------------------


def test_nc__E22_invalid_carries_a_present_null() -> None:
    body = serialise(None)
    assert "settledFraction" in body and body["settledFraction"] is None
    assert '"settledFraction": null' in json.dumps(body)


def test_nc__E22b_a_valid_run_carries_the_object() -> None:
    """The admission side: it is not `null` for everything."""
    from cdfc.evaluate.selection import RunProfile, Selection
    from cdfc.verdict.settled_fraction import Denominator, compute

    p = partition([_cell("S!A1", S.PASS)], 1)
    sel = Selection((), (), (), (), "r", RunProfile("default", "d"))
    sf = compute(p, sel, Denominator("m", "v3", 1, True, "PROVISIONAL-UNVALIDATED"), "VALID")
    assert serialise(sf)["settledFraction"] is not None


# --- NC-E23: the two vocabularies stay disjoint ------------------------------------------------


def test_nc__E23_no_run_level_cause_appears_in_the_item_vocabulary() -> None:
    item = {c.value for c in ReasonCode}
    run = {c.value for c in InvalidCause}
    assert item & run == set()
    assert not any(v.startswith("invalid.") for v in item)


def test_nc__E23b_a_guard_trip_produces_one_run_cause_and_zero_item_reasons() -> None:
    """The admission side, and the shape the split exists for."""
    from cdfc.evaluate.run import RunResult

    r = RunResult(run_id="x", filing_sha256="y", template_sha256=None, run_state="INVALID",
                  invalid_causes=(InvalidCause.CONTAINER_GUARD_TRIPPED,), checks=(), cells=(),
                  partition=None, fraction=None)
    assert len(r.invalid_causes) == 1 and r.checks == ()


# --- NC-E24: nothing derived from the filing's VALUES may remove a cell -------------------------


def test_nc__E24_a_degenerate_precondition_does_not_leave_the_denominator() -> None:
    retained = _cell("S!A1", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "PREDICATE_PRECONDITION")
    p = partition([retained, _cell("S!A2", S.PASS)], 2)
    assert p.outOfScopeRetained == 1 and p.inScope == 2, (
        "a predicate whose applicable went degenerate shrank the denominator it is measured against"
    )


def test_nc__E24b_a_declared_characteristic_does_leave() -> None:
    """The admission side: the removal path is not simply disabled."""
    leaves = _cell("S!A1", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "DECLARED_CHARACTERISTIC")
    p = partition([leaves, _cell("S!A2", S.PASS)], 2)
    assert p.outOfScopeRetained == 0 and p.inScope == 1


# --- NC-E25: an INFORMATIONAL-only cell stays counted --------------------------------------------


def test_nc__E25_an_informational_only_cell_is_no_predicate() -> None:
    state, reason, _sb, _sk = roll_up([
        Evaluation("P-a", 1, S.INFORMATIONAL, None),
        Evaluation("P-b", 1, S.INFORMATIONAL, None),
    ])
    assert (state, reason) == (S.NO_PREDICATE, R.NP_RULE_AMBIGUOUS)
    assert partition([_cell("S!A1", state, reason)], 1).inScope == 1


def test_nc__E25b_a_genuine_informational_cell_still_leaves() -> None:
    """The admission side: INFORMATIONAL has not stopped removing cells altogether."""
    p = partition([_cell("S!A1", S.INFORMATIONAL), _cell("S!A2", S.PASS)], 2)
    assert p.informational == 1 and p.informationalRetained == 0 and p.inScope == 1


# --- NC-E03: the contract is generated, not edited -------------------------------------------


def test_nc__E03b_contract_is_generated_not_edited() -> None:
    """Compared IN PROCESS, never by regenerating.

    The first version ran `tools/gen_contract.py`, which REWRITES the file — so it healed the
    hand edit for every guard that ran after it in the same pytest process, and the sweep saw a
    smaller flipped set than the entry declared. A guard that repairs the break is not a guard.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import gen_contract

    assert (REPO / "EVALUATION-CONTRACT.md").read_text(encoding="utf-8") == gen_contract.render()


def test_nc__E03c_the_generator_still_writes_the_table() -> None:
    """The admission side: `unchanged` is not printed by a generator that writes nothing."""
    text = (REPO / "EVALUATION-CONTRACT.md").read_text(encoding="utf-8")
    assert "| 4 | 5 | cells_bound == 0 |" in text


# --- NC-E02: pre-flight is what makes `true || <error>` impossible ------------------------------


def test_nc__E02b_preflight_blocks_expr_when_a_declared_key_is_absent() -> None:
    """`01`'s NAMED EXEMPLAR: under `preflight_disabled` the same predicate returns PASS.

    The expression is `<true> || <reads an absent key>`. The CEL specification says an operand
    error in `||` *"will be ignored"* when the other operand determines the result — so with
    pre-flight off this returns PASS while silently swallowing an operand that could not be
    evaluated at all. **The defect this product exists to prevent, manufactured by the language.**
    """
    import dataclasses

    h = fme_harvest()
    probe = dataclasses.replace(
        promote(h.candidates[0]), id="P-EXEMPLAR",
        schema_keys=("filing.here.v", "filing.here.__cell__", "filing.absent.v"),
        applicable="has(filing.here.v)",
        expr="filing.here.v == 1 || filing.absent.v == 1",
        witness="[filing.here.__cell__]",
    )
    facts = FactSet({"here": {"v": 1, "__cell__": "S!A1"}}, {})

    class _Schema:
        template_sha256 = "t"

        def cells_for(self, key: str) -> frozenset[str]:
            return frozenset({"S!A1"}) if key.startswith("filing.") else frozenset()

        def keys(self) -> frozenset[str]:
            return frozenset()

    chk = evaluate_one(probe, facts=facts, schema=_Schema(),
                       rt=CelRuntime(profile_version="P5", host_fns=default_registry()))
    assert chk.state is S.NOT_RUN and chk.order == 5, (
        "pre-flight did not block `expr`; an unguarded predicate returns PASS over a key nobody "
        "checked was present"
    )
    assert chk.reason is R.NR_SOURCE_UNREADABLE


def test_nc__E02c_a_complete_fact_set_proceeds_to_expr() -> None:
    """The admission side."""
    from cdfc.measure.p5_run import INDEPENDENT, run_filing

    res = run_filing(INDEPENDENT)
    assert any(c.order in (8, 9) for c in res.checks), "no predicate reached `expr` at all"
