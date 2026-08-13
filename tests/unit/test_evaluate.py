"""P3 — the formula evaluator.

The tests that matter here are the three contracts, each of which exists because breaking
it produces a clean confident wrong answer, and two of which this evaluator was CAUGHT
breaking on its own first run.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.calc.errors import DIV0, NA, ExcelError, is_error  # noqa: E402
from cdfc.calc.evaluate import ParseError, expand, parse_formula, recalculate  # noqa: E402
from cdfc.calc.functions import IFERROR, ROUND, SUM, Unimplemented  # noqa: E402


def _grid(formulas, literals=None, **kw):
    return recalculate(formulas, literals or {}, formula_source="TEMPLATE", **kw)


# --------------------------------------------------------------- the cascade rule
def test_eval__a_cell_reading_a_NOT_RUN_cell_does_not_run() -> None:
    """THE DEFECT THIS EVALUATOR WAS CAUGHT COMMITTING.

    `A13 = A11+1` where A11 did not run returned a clean 1 where the answer was 9,
    because the missing precursor read as 0. A number computed from an input that did not
    run is exactly the failure this system exists to refuse.
    """
    g = _grid({("S", "A2"): "TODAY()", ("S", "A3"): "A2+1"})
    assert ("S", "A2") in g.not_run
    assert ("S", "A3") in g.not_run, "a cell reading a NOT_RUN cell returned a value"
    assert "A2" in g.not_run[("S", "A3")], "the block does not name the input"
    assert ("S", "A3") not in g.values


def test_eval__a_declared_deferral_also_blocks() -> None:
    """A cell the CALLER could not materialise must be DECLARED, not dropped.

    Dropping it silently makes it invisible to the cascade rule, so anything reading it
    computes with a zero — the same defect, one level up, committed by the caller. Found
    in this evaluator's own arm-1 run.
    """
    g = _grid({("S", "B2"): "B1+1"}, deferred={("S", "B1"): "deferred: shared dependent"})
    assert ("S", "B2") in g.not_run and ("S", "B2") not in g.values


def test_eval__the_cascade_rule_is_not_over_broad() -> None:
    """Admission-side twin: a cell whose inputs all ran DOES run."""
    g = _grid({("S", "C3"): "C1+C2"}, {("S", "C1"): Decimal(2), ("S", "C2"): Decimal(3)})
    assert g.values[("S", "C3")] == Decimal(5)


# --------------------------------------------------------------- cycles
def test_eval__a_cycle_is_not_run_never_a_value() -> None:
    g = _grid({("S", "A1"): "A2+1", ("S", "A2"): "A1+1"})
    assert ("S", "A1") in g.not_run and ("S", "A2") in g.not_run
    assert "cycle" in g.not_run[("S", "A1")]
    assert ("S", "A1") not in g.values


# --------------------------------------------------------------- unimplemented
def test_eval__an_unimplemented_function_is_not_run_not_zero() -> None:
    g = _grid({("S", "A1"): "TODAY()"})
    assert "unimplemented" in g.not_run[("S", "A1")]
    assert ("S", "A1") not in g.values


def test_eval__IFERROR_does_not_swallow_unimplemented() -> None:
    """IFERROR catches EXCEL ERRORS. 'we did not implement this' is not one, and letting
    IFERROR convert it into a fallback turns a gap into a clean number."""
    g = _grid({("S", "A1"): "IFERROR(TODAY(),0)"})
    assert ("S", "A1") in g.not_run, "IFERROR swallowed an unimplemented function"
    # and it DOES catch a real Excel error
    assert IFERROR(DIV0, Decimal(7)) == Decimal(7)


# --------------------------------------------------------------- formula_source
def test_eval__formula_source_has_no_default() -> None:
    """The defect it prevents: checking a filing against formulas the filing supplied,
    under which a filer who rewrote a formula passes their own rewritten check."""
    with pytest.raises(TypeError):
        recalculate({}, {})  # type: ignore[call-arg]
    assert _grid({}).formula_source == "TEMPLATE"


# --------------------------------------------------------------- numerics
def test_eval__is_decimal_never_float() -> None:
    g = _grid({("S", "A1"): "0.1+0.2"})
    v = g.values[("S", "A1")]
    assert isinstance(v, Decimal) and v == Decimal("0.3"), f"float contamination: {v!r}"


def test_eval__round_is_half_away_from_zero_like_excel() -> None:
    """Python's default is half-to-even; Excel rounds half away from zero, and the
    difference lands on exactly the .5 cases a filer's totals produce."""
    assert ROUND(Decimal("2.5")) == Decimal(3)
    assert ROUND(Decimal("0.125"), Decimal(2)) == Decimal("0.13")


def test_eval__division_by_zero_is_an_error_value_not_an_exception() -> None:
    g = _grid({("S", "A1"): "1/0"})
    assert is_error(g.values[("S", "A1")])
    assert str(g.values[("S", "A1")]) == "#DIV/0!"


def test_eval__an_error_propagates_through_sum() -> None:
    assert is_error(SUM([Decimal(1), DIV0, Decimal(2)]))


def test_eval__an_error_is_never_truthy() -> None:
    assert not bool(NA), "an error must not satisfy a predicate's condition"


def test_eval__text_is_skipped_by_sum_not_zeroed() -> None:
    assert SUM([Decimal(1), "abc", Decimal(2)]) == Decimal(3)


# --------------------------------------------------------------- parsing
@pytest.mark.parametrize(
    ("src", "want"),
    [
        ("1+2*3", Decimal(7)),
        ("(1+2)*3", Decimal(9)),
        ("2^3^2", Decimal(512)),      # right-associative, as Excel
        ("-2^2", Decimal(4)),         # unary minus binds tighter, as Excel
        ('"a"&"b"', "ab"),
        ("10%", Decimal("0.1")),
        ("1<2", True),
        ("1<>1", False),
    ],
)
def test_eval__parser_precedence(src: str, want: object) -> None:
    g = _grid({("S", "A1"): src})
    assert g.values[("S", "A1")] == want, f"{src} -> {g.values.get(('S','A1'))!r} / {g.not_run}"


def test_eval__a_malformed_formula_is_not_run_not_zero() -> None:
    g = _grid({("S", "A1"): "SUM("})
    assert ("S", "A1") in g.not_run and ("S", "A1") not in g.values


def test_expand__ranges_and_sheet_qualification() -> None:
    assert expand("A1:B2", "S") == [("S", "A1"), ("S", "B1"), ("S", "A2"), ("S", "B2")]
    assert expand("'3. Portfolio'!C3", "S") == [("3. Portfolio", "C3")]
    assert expand("$C$3", "S") == [("S", "C3")]


def test_parse__rejects_rubbish() -> None:
    with pytest.raises(ParseError):
        parse_formula("=1 2 3 )")


# --------------------------------------------------------------- arm 1, as a test
def test_eval__arm1_has_zero_disagreements_on_the_corpus() -> None:
    """The gate, run as a test. Every cell we compute, we compute correctly; every cell we
    cannot, we say so. Reported per workbook — a corpus figure would average a control
    that discriminates against six that do not."""
    import json

    rep = REPO / "docs" / "measurements" / "p3-evaluator.json"
    if not rep.exists():
        pytest.skip("run tools/measure/evaluator_arm1.py first")
    rows = json.loads(rep.read_text())["rows"]
    bad = [(r["workbook"], r["disagree"], r["samples"]) for r in rows if r["disagree"]]
    assert not bad, f"arm 1 disagreements: {bad}"
    discriminating = [r for r in rows if r["trivial_share_pct"] < 10]
    assert discriminating, "no workbook in the corpus discriminates; arm 1 proves nothing"
    assert discriminating[0]["compared"] > 0


def test_eval__shape_only_references_are_not_value_dependencies() -> None:
    """NC-E15's direct guard, and it exists because the indirect one stopped being sensitive.

    `ROWS($C$92:C92)` asks HOW MANY ROWS a range spans. It does not read their values, so it is
    not a dependency edge. Treating it as one invented **thirty circular references** in the FME
    workbook that do not exist — and reported them as a finding about the regulator's template
    rather than as a defect in our own dependency analyser.

    The guard used to be the demo's NOT-CHECKED count. At P6 the `AGGREGATE` repair moved those
    same thirty cells into `not_run` for a different and correct reason, so the phantom cycles
    landed on cells that were already excluded and **the count stopped moving**. An indirect guard
    can be absorbed by an unrelated repair; a direct one cannot.
    """
    from cdfc.calc.evaluate import SHAPE_ONLY_FUNCTIONS, parse_formula, refs_of

    assert SHAPE_ONLY_FUNCTIONS, "the shape-only set is empty: every ROWS() is a dependency edge"
    assert {"ROW", "ROWS", "COLUMN", "COLUMNS"} <= SHAPE_ONLY_FUNCTIONS

    ast_ = parse_formula("ROWS($C$92:C92)+SUM($D$1:$D$3)")
    values = set(refs_of(ast_, values_only=True))
    all_refs = set(refs_of(ast_))
    assert "$D$1:$D$3" in all_refs
    assert not any("C92" in r for r in values), (
        f"a shape-only reference is being counted as a value dependency: {sorted(values)}"
    )
    assert values, "the positive control: a genuine value reference IS reported"
