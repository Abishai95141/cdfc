"""P5 — the exit gate's criteria, on the real workbook.

Criterion 1 is asserted on the **INDEPENDENTLY-COMPUTED** filing and never on the TEMPLATE-COMPUTED
one. That is the whole of finding F2: `calc/` wrote the second filing's derived cells, and the
arithmetic predicates assert exactly the identities `calc/` enforced when it did — so a zero there
is `x == x`, green on a correct implementation and green on one with a thousand-fold tolerance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema.anchor import Anchor
from cdfc.measure.p5_run import (  # noqa: E402
    INDEPENDENT,
    INDEPENDENT_LABEL,
    SEEDED,
    SMOKE_LABEL,
    TEMPLATE_COMPUTED,
    failing_predicate_ids,
    fme_harvest,
    fme_surface,
    predicates_reading,
    promote,
    run_filing,
)
from cdfc.verdict import InvalidCause, ItemState, ReasonCode  # noqa: E402
from cdfc.verdict.settled_fraction import assert_fraction_did_not_rise  # noqa: E402

SEED_CELL = "1. Introduction!C54"


@pytest.fixture(scope="module")
def clean():
    return run_filing(INDEPENDENT)


@pytest.fixture(scope="module")
def seeded():
    return run_filing(SEEDED)


def test_golden__closure__fme_clean_independently_computed(clean) -> None:
    """EXIT CRITERION 1 — 0 FAIL on a filing this product did not compute."""
    assert clean.run_state == "VALID", clean.invalid_causes
    assert clean.fraction is not None
    assert clean.fraction.settled.failed == 0, (
        f"a predicate fired on a filing LibreOffice computed: {failing_predicate_ids(clean)}. "
        "That is a genuine false failure and must be investigated before this gate can pass."
    )
    # R-GOLD-2: value assertions beside the pinned counts.
    n, _cells, _state = fme_surface()
    p = clean.partition
    assert p.cellsTotal == n == 3747
    assert p.total == p.cellsTotal, "the seven terms sum to the field surface"
    assert p.settled == 2320 and p.settledPass == 2320 and p.settledFail == 0
    assert p.noPredicate == 1427 and p.error == 0 and p.notRun == 0
    assert p.inScope == 3747
    assert str(clean.fraction.fraction) == "0.6192"


def test_golden__the_independent_filing_carries_its_label() -> None:
    """It is NOT the plan's HAND-COMPUTED filing and never claims to be."""
    assert "LibreOffice" in INDEPENDENT_LABEL
    assert "NOT by a person" in INDEPENDENT_LABEL and "NOT by Excel" in INDEPENDENT_LABEL
    assert "HAND-COMPUTED" not in INDEPENDENT.name


def test_golden__closure__fme_seeded(seeded) -> None:
    """EXIT CRITERION 2 — exactly the predicates reading that cell FAIL, asserted BY ID."""
    expected = predicates_reading(SEED_CELL)
    assert expected, "the seed cell is read by no predicate; the case would be vacuous"
    assert failing_predicate_ids(seeded) == expected
    assert seeded.run_state == "VALID"


def test_golden__the_seeded_run_does_not_raise_the_fraction(clean, seeded) -> None:
    assert_fraction_did_not_rise(clean.fraction, seeded.fraction, note="one seeded F11")


def test_golden__closure__fme_template_computed_is_smoke_only() -> None:
    """1a — SMOKE CHECK, NON-GATING. Its result does not enter the exit gate.

    A red here is a defect report, never a gate failure — so this test records what it found and
    asserts only that the plumbing ran, plus the second assertion the plan requires: every
    arithmetic predicate reads a cell `calc/` computed, which is why a zero here would be `x == x`.
    """
    res = run_filing(TEMPLATE_COMPUTED)
    assert res.checks, "the plumbing did not run at all"
    assert "SMOKE ONLY" in SMOKE_LABEL and "NON-GATING" in SMOKE_LABEL

    from cdfc.predicates.ast_walker import bound_cells
    from cdfc.predicates.harvest import _load_context

    from cdfc.measure.p5_run import FME

    h = fme_harvest()
    ctx = _load_context(FME)
    computed = {Anchor.cell(s, f.ref).render() for s, fs in ctx.formulas_by_sheet.items() for f in fs}
    arithmetic = [
        c for c in h.candidates
        if "carried across sheets" in c.rationale or "arithmetic identity" in c.rationale
        or "tally counts rows" in c.rationale
    ]
    assert arithmetic, "no arithmetic predicate was harvested; the limit statement is vacuous"
    for c in arithmetic:
        assert bound_cells(c, h.schema) & computed, (
            f"{c.id} reads no cell calc/ computed, so the smoke filing would be discriminating "
            "for it — which would change what this test may claim"
        )


def test_golden__cells_bound_zero_is_error_and_invalidates_the_run() -> None:
    """EXIT CRITERION 3 — with the run-level cause carried AS WELL AS the item-level code."""
    import dataclasses

    h = fme_harvest()
    orphan = dataclasses.replace(
        promote(h.candidates[0]),
        id="P-ORPHAN",
        schema_keys=("filing.nowhere.at.all.v", "filing.nowhere.at.all.__cell__"),
        applicable="has(filing.nowhere.at.all.v)",
        expr="filing.nowhere.at.all.v >= 0",
        witness="[filing.nowhere.at.all.__cell__]",
    )
    from cdfc.evaluate.celrt import CelRuntime
    from cdfc.evaluate.runner import evaluate_one
    from cdfc.facts.view import FactSet
    from cdfc.predicates.host_fns import default_registry

    facts = FactSet({"nowhere": {"at": {"all": {"v": 1, "__cell__": "S!A1"}}}}, {})
    chk = evaluate_one(orphan, facts=facts, schema=h.schema,
                       rt=CelRuntime(profile_version="P5", host_fns=default_registry()))
    assert chk.state is ItemState.ERROR
    assert chk.reason is ReasonCode.ERR_CELLS_BOUND_ZERO
    assert chk.invalid_cause is InvalidCause.CELLS_BOUND_ZERO
    assert chk.order == 4, "before pre-flight and before expr — D-P5-01"


def test_golden__unbound_sets_both_vocabularies() -> None:
    """Audit V.7.3: `invalid.template_unbound` AND `not_run.template_unbound`, not one."""
    res = run_filing(REPO / "fixtures" / "synthetic" / "row-inserted__portfolio-r7.xlsx")
    assert res.run_state == "INVALID"
    assert InvalidCause.TEMPLATE_UNBOUND in res.invalid_causes
    assert res.checks and all(c.reason is ReasonCode.NR_TEMPLATE_UNBOUND for c in res.checks)
    assert res.fraction is None


def test_golden__binding__formula_content_is_not_in_the_fingerprint() -> None:
    """A filer who overwrote a formula with a literal must fail a PREDICATE, not the BINDING."""
    from cdfc.evaluate.binding import Bound, bind_template
    from cdfc.measure.p5_run import catalogue

    overwritten = REPO / "fixtures" / "synthetic" / "formula-overwritten__portfolio-O7.xlsx"
    assert isinstance(bind_template(overwritten, catalogue()), Bound)
