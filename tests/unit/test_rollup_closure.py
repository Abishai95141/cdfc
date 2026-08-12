"""P5-B4 — roll-up, closure, and the settled-fraction object."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.rollup import Evaluation, RunCell, materialise, roll_up  # noqa: E402
from cdfc.evaluate.selection import RunProfile, Selection, admission_state  # noqa: E402
from cdfc.verdict import ItemState, MissingScopeKindError, ReasonCode  # noqa: E402
from cdfc.verdict.closure import (  # noqa: E402
    TERMS,
    ClosureViolation,
    assert_closed,
    partition,
)
from cdfc.verdict.settled_fraction import (  # noqa: E402
    Denominator,
    FractionRoseError,
    assert_fraction_did_not_rise,
    compute,
    fraction_of,
    serialise,
)

R = ReasonCode
S = ItemState


def ev(state, reason=None, pid="P-0001", settles=True, scope_kind=None):
    return Evaluation(predicate_id=pid, version=1, state=state, reason=reason,
                      settles=settles, scope_kind=scope_kind)


def cell(key, state, reason=None, scope_kind=None, evals=()):
    return RunCell(stable_key=key, state=state, reason=reason, settled_by=None,
                   evaluations=evals, scope_kind=scope_kind)


# --- roll-up -----------------------------------------------------------------------------


def test_roll_up__empty_evaluation_set_is_NO_PREDICATE() -> None:
    from cdfc.verdict import PRECEDENCE

    state, reason, settled_by, _sk = roll_up([])
    assert (state, reason, settled_by) == (S.NO_PREDICATE, R.NP_NOT_YET_SYNTHESISED, None)
    assert S.NO_PREDICATE not in PRECEDENCE


def test_roll_up__one_pass_and_one_not_run_is_unsettled() -> None:
    """The audit's resolution, as one line. Under the withdrawn order this rolled up to PASS."""
    state, _r, settled_by, _sk = roll_up(
        [ev(S.PASS, pid="P-a"), ev(S.NOT_RUN, R.NR_EXTRACTOR_DISAGREEMENT, pid="P-b")]
    )
    assert state is S.NOT_RUN and settled_by is None


def test_roll_up__error_beats_everything_and_out_of_scope_loses_to_everything() -> None:
    every = [ev(s, None if s in (S.PASS, S.FAIL) else _reason(s), pid=f"P-{i}")
             for i, s in enumerate(
                 (S.PASS, S.FAIL, S.INDETERMINATE, S.NOT_RUN, S.OUT_OF_SCOPE, S.ERROR))]
    assert roll_up(every)[0] is S.ERROR
    assert roll_up([ev(S.OUT_OF_SCOPE, R.OOS_NOT_SELECTED), ev(S.PASS, pid="P-z")])[0] is S.PASS


def _reason(s):
    return {
        S.INDETERMINATE: R.IND_TOLERANCE_STRADDLE, S.NOT_RUN: R.NR_SOURCE_UNREADABLE,
        S.OUT_OF_SCOPE: R.OOS_NOT_SELECTED, S.ERROR: R.ERR_PREDICATE_RAISED,
        S.NO_PREDICATE: R.NP_NOT_YET_SYNTHESISED,
    }[s]


def test_roll_up__informational_only_cell_is_no_predicate() -> None:
    """D-P5-05 / F14. INFORMATIONAL leaves inScope; without this a defect-table row raises the
    headline. A cell we have no verdict on is a gap in US."""
    state, reason, _sb, _sk = roll_up([ev(S.INFORMATIONAL), ev(S.INFORMATIONAL, pid="P-b")])
    assert (state, reason) == (S.NO_PREDICATE, R.NP_RULE_AMBIGUOUS)
    # one PASS beside it still rolls up to PASS
    assert roll_up([ev(S.INFORMATIONAL), ev(S.PASS, pid="P-b")])[0] is S.PASS


def test_roll_up__degenerate_precondition_stays_in_scope() -> None:
    """Three rows, one test, no default."""
    retained = cell("S!A1", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "PREDICATE_PRECONDITION")
    leaves = cell("S!A2", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "DECLARED_CHARACTERISTIC")
    naked = cell("S!A3", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, None)
    assert retained.in_scope is True and retained.requalify is True
    assert leaves.in_scope is False and leaves.requalify is False
    with pytest.raises(MissingScopeKindError):
        _ = naked.in_scope


def test_materialise__count_equals_field_surface() -> None:
    from cdfc.measure.p5_run import fme_surface

    n, cells, _ = fme_surface()
    table = materialise(cells)
    assert len(table) == n == 3747
    assert all(c.state is S.NO_PREDICATE for c in table.values())


# --- closure ------------------------------------------------------------------------------


def test_partition__seven_terms_sum_to_field_surface() -> None:
    cells = [cell(f"S!A{i}", S.PASS) for i in range(10)] + [
        cell("S!B1", S.NOT_RUN, R.NR_SOURCE_UNREADABLE),
        cell("S!B2", S.NO_PREDICATE, R.NP_NOT_YET_SYNTHESISED),
    ]
    p = partition(cells, len(cells))
    assert p.total == p.cellsTotal == 12
    assert set(TERMS) == {"outOfScope", "informational", "settled", "indeterminate",
                          "notRun", "noPredicate", "error"}
    assert_closed(p)


def test_partition__inscope_uses_removal_basis_only() -> None:
    cells = [
        cell("S!A1", S.PASS),
        cell("S!A2", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "PREDICATE_PRECONDITION"),
        cell("S!A3", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "DECLARED_CHARACTERISTIC"),
        cell("S!A4", S.OUT_OF_SCOPE, R.OOS_NOT_SELECTED),
    ]
    p = partition(cells, 4)
    assert p.outOfScope == 3 and p.outOfScopeRetained == 1
    assert p.inScope == 4 - (3 - 1) == 2
    assert p.requalify == 1


def test_closure__a_hole_aborts_rather_than_degrading() -> None:
    """There is no degraded report. The count is short and the run is INVALID."""
    p = partition([cell("S!A1", S.PASS)], field_surface=5)
    with pytest.raises(ClosureViolation) as e:
        assert_closed(p)
    assert "no degraded report" in str(e.value)


def test_closure_sql_matches_python() -> None:
    """NOT an independent implementation, and the docstring says so.

    Both read the same `run_cell` rows, so this catches a TRANSCRIPTION error and nothing more —
    the distinction NC-D02d draws between two implementations and one implementation called twice,
    applied honestly to our own cheap check.
    """
    import sqlite3

    from cdfc.verdict.closure import CLOSURE_SQL

    cells = [
        cell("S!A1", S.PASS), cell("S!A2", S.FAIL), cell("S!A3", S.NOT_RUN, R.NR_DEACTIVATED),
        cell("S!A4", S.OUT_OF_SCOPE, R.OOS_NOT_APPLICABLE, "PREDICATE_PRECONDITION"),
        cell("S!A5", S.NO_PREDICATE, R.NP_NOT_YET_SYNTHESISED),
    ]
    py = partition(cells, len(cells))
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE run_cell (run_id TEXT, stable_key TEXT, state TEXT, in_scope INT)")
    conn.executemany(
        "INSERT INTO run_cell VALUES ('r', ?, ?, ?)",
        [(c.stable_key, str(c.state), int(c.in_scope)) for c in cells],
    )
    row = dict(zip(
        [d[0] for d in conn.execute(CLOSURE_SQL, ("r",)).description],
        conn.execute(CLOSURE_SQL, ("r",)).fetchone(), strict=True))
    for term in TERMS:
        assert row[term] == getattr(py, term), term
    assert row["outOfScopeRetained"] == py.outOfScopeRetained


# --- the settled fraction --------------------------------------------------------------------


def _den(n=100):
    return Denominator("mask", "v3", n, True, "PROVISIONAL-UNVALIDATED")


def _sel(active=()):
    return Selection(active=tuple(active), provisional=(), not_requalified=(), deactivated=(),
                     registry_root="r", profile=RunProfile("default", "d"))


def test_compute__invalid_run_returns_None_not_zero() -> None:
    p = partition([cell("S!A1", S.PASS)], 1)
    assert compute(p, _sel(), _den(1), "INVALID") is None


def test_compute__no_mask_template_returns_None_and_the_source_string() -> None:
    from cdfc.verdict.settled_fraction import NO_MASK_SOURCE

    p = partition([cell("S!A1", S.PASS)], 1)
    assert compute(p, _sel(), Denominator("none", "v3", None, False, "N/A"), "VALID") is None
    assert "looks like a small answer rather than like no answer" in NO_MASK_SOURCE


def test_contract__invalid_carries_a_null_not_an_absence() -> None:
    """D-P5-06. `null`, `forbidden` and `omitted` are three different things."""
    import json

    body = serialise(None)
    assert "settledFraction" in body and body["settledFraction"] is None
    text = json.dumps(body)
    assert '"settledFraction": null' in text
    assert json.loads(text)["settledFraction"] is None
    assert "settledFraction" in json.loads(text)


def test_compute__fraction_is_decimal_not_float() -> None:
    p = partition([cell(f"S!A{i}", S.PASS) for i in range(3)] +
                  [cell("S!B1", S.NOT_RUN, R.NR_DEACTIVATED)], 4)
    sf = compute(p, _sel(), _den(4), "VALID")
    assert isinstance(sf.fraction, Decimal) and not isinstance(sf.fraction, float)
    assert sf.fraction == Decimal("0.7500")


def test_fraction__renders_inscope_and_cellstotal_together() -> None:
    p = partition([cell("S!A1", S.PASS)], 1)
    row = compute(p, _sel(), _den(1), "VALID").as_row()
    assert "inScope" in row and "cellsTotal" in row
    assert "fraction" in row and isinstance(row["fraction"], str)


def test_fraction__pre_gate_requires_its_caveat() -> None:
    p = partition([cell("S!A1", S.PASS)], 1)
    sf = compute(p, _sel(), _den(1), "VALID")
    assert sf.admissionState == "PRE-GATE" and sf.admissibilityCaveat
    assert admission_state(_sel()) == "PRE-GATE"


def test_assert_fraction_did_not_rise__raises_only_when_it_rose() -> None:
    lo = compute(partition([cell("S!A1", S.PASS), cell("S!A2", S.NOT_RUN, R.NR_DEACTIVATED)], 2),
                 _sel(), _den(2), "VALID")
    hi = compute(partition([cell("S!A1", S.PASS), cell("S!A2", S.PASS)], 2), _sel(), _den(2), "VALID")
    assert_fraction_did_not_rise(hi, lo)
    with pytest.raises(FractionRoseError, match="rewards the behaviour"):
        assert_fraction_did_not_rise(lo, hi)


def test_settled_fraction_falls_on_not_run() -> None:
    """EXIT CRITERION 5, as a single case. The invariant is in the property tests."""
    passing = [cell(f"S!A{i}", S.PASS) for i in range(4)]
    before = compute(partition(passing, 4), _sel(), _den(4), "VALID")
    after_cells = [*passing[:3], cell("S!A3", S.NOT_RUN, R.NR_EXTRACTOR_DISAGREEMENT)]
    after = compute(partition(after_cells, 4), _sel(), _den(4), "VALID")
    assert after.fraction < before.fraction
    assert fraction_of(partition(after_cells, 4)) == Decimal("0.7500")
