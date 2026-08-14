"""P4-B4 — the pinned harvest counts.

Per `01` §1.3 these are **properties of our code**, allowed to move with a recorded reason. The
expected values are read from `docs/HARVEST-DELTA.md`'s last entry, so **moving a number without
appending an entry fails the build.** The first thing P7's G3 will do is reject predicates and this
number will fall — which is correct behaviour, and a regression test that fails on correct
behaviour gets deleted rather than argued with.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.harvest_report import SPEC_STATIC_SETTLED_CELLS  # noqa: E402
from cdfc.measure.paths import P4_HARVEST_DISTRIBUTION  # noqa: E402
from cdfc.predicates.harvest import distribution, harvest, harvest_all  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
EDR = FIX / "EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx"
DELTA = REPO / "docs" / "HARVEST-DELTA.md"
DIST = REPO / "docs" / "measurements" / "P4-harvest-distribution.md"


def _pinned(name: str) -> int:
    """The expected value, read from the LAST entry of the append-only delta ledger."""
    entries = DELTA.read_text(encoding="utf-8").split("\n## ")
    last = entries[-1]
    m = re.search(rf"`{re.escape(name)}` -> \*\*(\d+)\*\*", last)
    assert m, f"{name} is not pinned in the last entry of docs/HARVEST-DELTA.md"
    return int(m.group(1))


@pytest.fixture(scope="module")
def results():
    return harvest_all(FIX)


def test_golden__harvest_count__fme() -> None:
    res = harvest(FME)
    assert len(res.candidates) == _pinned("test_golden__harvest_count__fme")
    # The class vector beside the count, per R-GOLD-2: a total alone says something did not change,
    # not that it is right.
    assert res.by_class == {
        "cross_sheet_equality": 181,
        "date_bound": 5,
        "integer_bound": 11,
        "membership": 20,
        "numeric_bound": 10,
        "same_sheet_equality": 42,
        "sum_identity": 79,
        # `tally_identity` IS ABSENT, and its absence is the value assertion. The corpus contains
        # exactly one COUNTIF and its criterion is an Excel wildcard, which the class refuses as a
        # typed skip since P8 — see docs/HARVEST-DELTA.md, 13 Aug 2026. A key that reappeared here
        # would mean a non-wildcard COUNTIF entered the corpus, or that the refusal regressed.
    }
    # The pinned `22 list-type / 20 resolving` split, reconciled: 20 membership predicates and
    # exactly 2 `list_unresolved` skips. It will silently fall to 15 if the x14 validations did
    # not survive ingest, which is what makes this an upstream positive control.
    assert res.by_class["membership"] == 20
    assert res.skips_by_kind.get("list_unresolved") == 2


def test_golden__cross_workbook_harvest_distribution(results) -> None:
    rows = distribution(results)
    total = sum(r.n for r in rows)
    assert total == _pinned("test_golden__cross_workbook_harvest_distribution")
    assert len(rows) == 9, "all nine rows, including the two zeroes"

    # Publishing the total alone is banned (NC-Q73). The distribution is concentrated, so the
    # per-workbook table travels with it.
    top2 = sorted((r.n for r in rows), reverse=True)[:2]
    assert sum(top2) > total * 0.6, "the distribution is concentrated; the table is not optional"

    doc = DIST.read_text(encoding="utf-8")
    for r in rows:
        assert f"`{r.sha8}`" in doc, f"{r.workbook} is missing from the published distribution"
        assert f"| **{r.n}** |" in doc
    assert sum(1 for r in rows if r.n == 0) == 2, "the two zeroes are published, not omitted"


def test_golden__zero_formula_template__edr1() -> None:
    """`EDR_1` yields one membership predicate and a settled fraction of 0%. Publish it anyway."""
    res = harvest(EDR)
    assert len(res.candidates) == _pinned("test_golden__zero_formula_template__edr1")
    assert res.by_class == {"membership": 1}
    assert res.candidates[0].claims_fault_classes == ("F12",)


def test_golden__static_settled_cells_reconcile() -> None:
    """Both integers and the delta, in writing. A divergence is a finding, not a correction."""
    res = harvest(FME)
    computed = len(res.cells_reachable)
    doc = DIST.read_text(encoding="utf-8")
    assert f"**{computed}**" in doc, "the computed figure is not published"
    assert str(SPEC_STATIC_SETTLED_CELLS) in doc, "the spec's figure is not published beside it"
    delta = computed - SPEC_STATIC_SETTLED_CELLS
    assert f"**{delta:+d}**" in doc, "the delta is not stated"
    assert "is a finding" in doc and "not reconciled by adjusting the" in doc


def test_golden__the_obligation_coverage_pair_renders_together(results) -> None:
    """`test_harvest__obligation_coverage_is_published`. Either both, or the criterion fails."""
    total = sum(len(r.candidates) for r in results)
    doc = DIST.read_text(encoding="utf-8")
    assert f"**0 / {total}**" in doc, "the STATUTE count is not published"
    assert f"**{total} / {total}**" in doc, "the TEMPLATE count is not published"
    assert "never added together" in doc
    assert "clause_absent_reason" in doc, "the distribution beside the pair is missing"


def test_golden__unclaimed_fault_classes_are_published() -> None:
    doc = DIST.read_text(encoding="utf-8")
    assert "fault_classes_claimed_by_no_harvested_candidate" in doc
    for f in ("F10", "F11", "F14"):
        assert f"**{f}**" in doc, f"{f} is unclaimed and is not named with its reason"


def test_golden__the_transfer_note_lives_in_one_file_and_names_the_number(results) -> None:
    """`07` imports the path constant rather than re-typing a filename — obligation X6."""
    assert P4_HARVEST_DISTRIBUTION.name == "p4-harvest-distribution.json"
    non_empty = sum(1 for r in results if r.candidates)
    doc = DIST.read_text(encoding="utf-8")
    assert f"Non-empty on {non_empty} of 9" in doc
    assert ">= 5 of 9" in doc, "G-TRANSFER (mech)'s pre-registered threshold is not stated"
    assert "P15" in doc and "human cost" in doc, (
        "the note must say what it does NOT claim: the per-predicate human cost is P15's arm"
    )


def test_golden__the_distribution_json_and_markdown_agree() -> None:
    """**The JSON published 592 while the markdown beside it published 571.**

    It was a committed snapshot from before the repairs in `docs/HARVEST-DELTA.md`, with no
    generator and no reader — and the one test that named it asserted its FILENAME and never
    opened it, so it would have passed had the file been deleted. Both now come out of the same
    call in `cdfc harvest --report`, and this test reads the numbers rather than the name.
    """
    import json
    import re

    d = json.loads(P4_HARVEST_DISTRIBUTION.read_text(encoding="utf-8"))
    md = (P4_HARVEST_DISTRIBUTION.parent / "P4-harvest-distribution.md").read_text(encoding="utf-8")

    total = d["predicates_with_a_TEMPLATE_obligation"]
    assert total == sum(r["n"] for r in d["rows"]), "the JSON does not add up to its own rows"
    assert d["predicates_with_a_STATUTE_obligation"] == 0
    assert f"**{total}**" in md, (
        f"the JSON says {total} and the markdown beside it does not carry that number"
    )
    # Every workbook of the corpus appears, zeroes included — publishing the total alone is banned.
    assert len(d["rows"]) == 9
    assert sum(1 for r in d["rows"] if r["n"] == 0) == 2, "the two zero-yield workbooks are rows"

    # The skip pile is the coverage declaration's other half and must be non-trivial: before the
    # completeness sweep, 1,060 of 1,495 formula cells were neither an obligation nor a skip.
    assert sum(r["skips"] for r in d["rows"]) > total, (
        "the declared weak pile is smaller than the predicate count; the sweep is not running"
    )
    assert re.search(r"\b571\b", md), "the corpus total must be on the page"
