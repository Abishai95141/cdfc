"""§P10·L.2.2 — the admission-side positive controls.

**Without these, all six deaths of §P10·L.1 are satisfied by a layer that returns `INVALID`
unconditionally.** That is the whole reason this file exists: the six deaths prove the layer can
say no, and only these prove it can say yes — and say yes for the right reasons, on the right
artifacts, with digits.

The middle one is the load-bearing one. **A layer that cannot tell a broken instrument from a
broken filing has destroyed the distinction the whole product sells.**
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.p10_run import population, run_filing  # noqa: E402
from cdfc.measure.p5_run import INDEPENDENT, SEEDED, TEMPLATE_COMPUTED  # noqa: E402
from cdfc.selfcheck.thresholds import CANARY_INAPPLICABLE_CEILING  # noqa: E402
from cdfc.verdict import ItemState  # noqa: E402

SPARSE = REPO / "fixtures" / "synthetic" / "formula-overwritten__portfolio-O7.xlsx"


def test_canary__healthy_run_is_VALID() -> None:
    """The FME reference fill against the real population yields `VALID` **with digits**.

    Every clause matters. `canariesPassed == canariesRun` says every check demonstrated itself;
    `antiCanariesPassed == antiCanariesRun` says none of them flags a filing known to be correct;
    `canariesInapplicable == 0` says this filing could exercise all of them; `selfTestSilent` says
    the loop is running. And the settled fraction renders as a number rather than as `null`.
    """
    result = run_filing(TEMPLATE_COMPUTED)
    proof = result.liveness.as_liveness_proof()

    assert result.run_state == "VALID", [c.value for c in result.invalid_causes]
    assert proof["canariesRun"] == len(population()) == proof["canariesPassed"]
    assert proof["antiCanariesRun"] == proof["antiCanariesPassed"] == len(population())
    assert proof["canariesInapplicable"] == 0
    assert proof["canariesIndeterminate"] == 0
    assert proof["selfTestSilent"] is True
    assert result.liveness_disposition.valid

    # A RENDERED SETTLED FRACTION WITH DIGITS. `null` here would mean the run declared no
    # coverage, and a positive control that accepts `null` accepts the failure it is guarding.
    assert result.fraction is not None
    assert result.fraction.fraction is not None
    assert result.partition.settled > 0 and result.partition.inScope > 0


def test_canary__a_real_fault_still_FAILs_and_the_run_stays_VALID() -> None:
    """**The distinction the whole product sells.**

    A filing with one seeded fault must produce a `FAIL` on the predicate reading that cell — and
    the run must stay `VALID`, because the instrument is fine and the *filing* is not. A liveness
    layer that turned this run `INVALID` would be reporting a broken filing as a broken instrument,
    and the report would say nothing about the filer's document at all.
    """
    result = run_filing(SEEDED)
    fails = sorted(c.predicate_id for c in result.checks if c.state is ItemState.FAIL)

    assert result.run_state == "VALID", [c.value for c in result.invalid_causes]
    assert fails, "the seeded fault produced no FAIL, so this control proves nothing about VALID"
    proof = result.liveness.as_liveness_proof()
    assert proof["canariesPassed"] == proof["canariesRun"]
    assert proof["antiCanariesPassed"] == proof["antiCanariesRun"]
    assert result.fraction is not None, "the fraction is a number: the instrument was demonstrated"

    # And the FAIL lands on a predicate that READS the seeded cell — not on an unrelated one.
    #
    # The seeded cell is COMPUTED from the fixture rather than taken from its filename, and that is
    # not pedantry: `mutant__f11-formula-override__portfolio-O7.xlsx` seeds
    # `'1. Introduction'!C54`, not `'3. Portfolio'!O7`. Its provenance file says only *"the P6
    # fault-model instance of F11"*, so the filename is the only place the cell is named and the
    # filename is wrong. A test that trusted it would assert against a cell nothing touched.
    from cdfc.measure.p5_run import predicates_reading
    from cdfc.qualify.observability import literal_differences

    seeded = sorted(f"{s}!{r}" for s, r in literal_differences(TEMPLATE_COMPUTED, SEEDED))
    assert seeded == ["1. Introduction!C54"], f"the fixture moved: it now seeds {seeded}"
    readers = set().union(*(set(predicates_reading(c)) for c in seeded))
    assert set(fails) <= readers, (
        f"{sorted(set(fails) - readers)} FAILed without reading any cell this filing changed"
    )


def test_canary__inapplicable_below_the_ceiling_stays_VALID() -> None:
    """A sparsely-filled but lawful filing returns `VALID` with a **lower** settled fraction.

    This is the row of the disposition table that is easiest to get wrong in the flattering
    direction: inapplicability must cost coverage, not invalidate the run, and the cost must show
    up in the number rather than in a footnote. Those predicates are `NOT_RUN(not_run.deactivated)`
    and their cells stop being settled.
    """
    dense = run_filing(TEMPLATE_COMPUTED)
    sparse = run_filing(SPARSE)
    proof = sparse.liveness.as_liveness_proof()

    inapplicable = proof["canariesInapplicable"] + proof["canariesIndeterminate"]
    assert inapplicable > 0, "this fixture exercises every canary, so it tests the wrong row"
    ratio = inapplicable / proof["canariesRun"]
    assert ratio <= float(CANARY_INAPPLICABLE_CEILING), (
        f"{inapplicable}/{proof['canariesRun']} is above the ceiling, so this fixture belongs to "
        "the WHOLESALE_INAPPLICABILITY row and not to this one"
    )

    assert sparse.run_state == "VALID", [c.value for c in sparse.invalid_causes]
    assert sparse.liveness_disposition.deactivated, "nothing was deactivated, so nothing can fall"
    assert sparse.fraction is not None
    assert sparse.fraction.fraction < dense.fraction.fraction, (
        f"the settled fraction did not fall: {sparse.fraction.fraction} vs {dense.fraction.fraction}. "
        "A predicate whose liveness could not be demonstrated here settles nothing here."
    )


def test_canary__the_whole_harvest_cannot_demonstrate_itself_and_says_so() -> None:
    """The number that does NOT flatter us, published beside the three above.

    Over all 348 harvested candidates the run is `INVALID(WHOLESALE_INAPPLICABILITY)`: 315 of them
    carry no stored kill case at all, so their liveness cannot be demonstrated on any filing. That
    is the same 315 the P7 funnel rejects with `g2.no_kill` — two layers, built independently,
    reaching the same set. Reporting only the restricted population would be choosing it after
    seeing the result.
    """
    from cdfc.measure.p10_run import all_predicates

    result = run_filing(TEMPLATE_COMPUTED, predicates=all_predicates())
    assert result.run_state == "INVALID"
    assert result.liveness_disposition.failure_kind == "WHOLESALE_INAPPLICABILITY"
    assert result.fraction is None, "not zero — null. This is a finding about us, not about the filing"
    proof = result.liveness.as_liveness_proof()
    assert proof["canariesInapplicable"] == len(all_predicates()) - len(population())
