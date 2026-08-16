"""The FME reference run's Unchecked panel, pinned — with a correction to `plan/07`.

**`plan/07` P14-B2's golden says "counts summing to 1,374". The measured value is 1,849.** That
figure predates P8's harvest delta and the R2 repair of the 1,060 silent formula cells; it is
recorded here as the prior with its provenance rather than quietly replaced, because under this
project's own rule a recount that disagrees with a published count is the event to investigate, not
the one to align.

**R-GOLD-2: the paired value assertion.** A count golden that pins only a number passes over a
panel that grouped everything under the wrong code. So the group's reason code, its remedy id and
the verbatim CSSF citation are pinned beside the integer.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.unchecked import build_unchecked_panel  # noqa: E402

# The prior, with its provenance. Not deleted.
PLAN_07_PRIOR = 1374
MEASURED = 1849


def _run():
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED

    return run_filing(TEMPLATE_COMPUTED)


def test_golden__unchecked_groups__fme() -> None:
    panel = build_unchecked_panel(_run())

    assert panel.total == MEASURED, (
        f"the panel totals {panel.total}, pinned at {MEASURED}. plan/07 carries {PLAN_07_PRIOR}, "
        "which predates P8's harvest delta and the R2 repair; a movement here is a regression in "
        "coverage accounting, not a documentation drift."
    )
    # **TWO GROUPS, PINNED 422 / 1,427 — and the movement from one is a repair, not a drift.**
    #
    # This assertion read `== ["no_predicate.not_yet_synthesised"]` and said *more than one would
    # mean the run changed*. The run did change, and the golden caught it, which is the whole job.
    #
    # The single code was WRONG for 422 of these cells. `not_yet_synthesised` says *nobody has
    # written a check for this cell*; for a cell a harvested candidate binds — and which is
    # unchecked because G2 REFUSED that candidate — the true code is `failed_qualification`, and
    # `qualify/pipeline.py` has recorded `cells_would_have_covered` on every rejection since P4
    # expressly so the count could be attributed here.
    #
    # **The total is unmoved and so is the settled fraction.** Every cell in both groups is
    # `NO_PREDICATE` before and after; only the attribution changed.
    assert [g.reason_code for g in panel.groups] == [
        "no_predicate.failed_qualification",
        "no_predicate.not_yet_synthesised",
    ], (
        "the reference run groups under exactly two reason codes, in this order. A third would "
        "mean the run changed; a different one would mean the grouping did."
    )
    counts = {g.reason_code: g.count for g in panel.groups}
    assert counts == {
        "no_predicate.failed_qualification": 422,
        "no_predicate.not_yet_synthesised": 1427,
    }
    assert sum(counts.values()) == MEASURED
    for g in panel.groups:
        assert g.count == len(g.entries)
    by_code = {g.reason_code: g for g in panel.groups}
    assert by_code["no_predicate.not_yet_synthesised"].remedy.id == "R-NP-NOT-YET-SYNTHESISED"
    assert "five gates" in by_code["no_predicate.not_yet_synthesised"].remedy.text
    # The two remedies must DIFFER. Identical text would make the split cosmetic.
    assert len({g.remedy.text for g in panel.groups}) == 2

    # The residue has not been measured against this predicate set. `None`, never `()`.
    assert panel.exhibits is None
    assert "not yet measured" in panel.residue_state


def test_golden__the_cssf_remedy_is_verbatim() -> None:
    """R-GOLD-2's paired value assertion, on the canonical judgment-bearing entry.

    This is the remedy `ci/no-imported-prior.sh` must NOT fire on: it cites the kind of instrument
    that would make a valuation judgment checkable, quoting CSSF's own published bands. Citing an
    instrument is lawful; adopting somebody else's number as our threshold is not.
    """
    from cdfc.surface.unchecked import load_remedies

    remedies, _ = load_remedies()
    r = remedies["no_predicate.requires_judgment"]
    assert r.source == "CSSF Circular 24/856, Tables 1-5"
    for fragment in ("materiality threshold by scheme class", "Tables 1-3",
                     "0.20% money-market", "0.50% bond and mixed", "1.00% equity and other",
                     "compensation-direction rule", "Tables 4-5"):
        assert fragment in r.text, f"the CSSF remedy lost {fragment!r}"
    assert "1.72" not in r.text, "the Luxembourg prior reached the canonical remedy"
