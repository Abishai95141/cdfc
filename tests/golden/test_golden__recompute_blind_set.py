"""P10-B4 — the recompute-blind set, pinned. **E2's landing ground, and it is a measurement.**

E1 (the coordinated misstatement) is a construction: an argument that scaling one connected
component of the carry graph leaves every identity satisfied. **E2 is a fact about the regulator's
own artifact** — these cells feed no template formula at all, so no recompute, no cross-sheet carry
and no SUM identity can reach them, whatever a checker does. A categorical swap that lands here is
unreachable by arithmetic and legal by the regulator's own data validation at the same time.

That is why the number is pinned with a **paired value assertion**: a count alone agrees with a
pin whether or not it is about the right cells, and this project has now found that defect shape
seven times.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.p5_run import FME  # noqa: E402
from cdfc.probes.precedents import build_precedent_map  # noqa: E402
from cdfc.schema.styles_mask import Rule, build  # noqa: E402
from cdfc.selfcheck.exhibit import recompute_blind  # noqa: E402

FIELD_SURFACE = 3747
REACHABLE = 957
BLIND = 2790

# MEASURED 14 August 2026 from `probes/precedents.py`'s `transitive` reading, which is the reading
# that BINDS: it follows a formula's references through intermediate formula cells to the
# field-surface inputs that actually determine the answer.
PER_SHEET = {
    "1. Introduction": 307,
    "2. Summary": 211,
    "3. Portfolio": 1298,
    "4. Investors": 529,
    "5. PMS": 376,
    "6. Complaints": 25,
    "7. AML-CFT": 22,
    "8. Compliance Status": 22,
}

# THE PAIRED VALUE ASSERTION. One cell inside the set and one outside, both named.
#
# `'3. Portfolio'!C7` is a column of the row whose total `O7` computes, so overwriting it moves a
# formula and every recompute predicate over that row can see it. `'6. Complaints'!C10` carries no
# formula anywhere downstream of it, so nothing arithmetic in the workbook can contradict what it
# says. A count that agreed with 2,790 while these two swapped sides would be a count about the
# wrong cells.
INSIDE = "6. Complaints!C10"
OUTSIDE = "3. Portfolio!C7"


def _sets() -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    fs = build(FME, Rule.V3)
    surface = frozenset(f"{s}!{r}" for s, r in fs.cells)
    pm = build_precedent_map(FME, reading="transitive")
    return surface, pm.reachable, recompute_blind(pm, surface)


def test_golden__2790_cells_feed_no_formula() -> None:
    surface, reachable, blind = _sets()
    assert len(surface) == FIELD_SURFACE
    assert len(reachable) == REACHABLE
    assert len(blind) == BLIND
    assert len(reachable) + len(blind) == len(surface), (
        "reachable and blind must PARTITION the field surface: a cell that is in neither, or in "
        "both, means the ceiling and its complement were computed against different surfaces"
    )


def test_golden__the_per_sheet_split_is_pinned() -> None:
    """A total agrees with a pin whether or not it is about the right cells."""
    _surface, _reachable, blind = _sets()
    actual: dict[str, int] = {}
    for cell in blind:
        actual[cell.split("!")[0]] = actual.get(cell.split("!")[0], 0) + 1
    assert actual == PER_SHEET
    assert sum(PER_SHEET.values()) == BLIND


def test_golden__the_paired_value_assertion() -> None:
    """One named cell in the set, one named cell outside it. Both, or the count means nothing."""
    surface, reachable, blind = _sets()
    assert INSIDE in surface and OUTSIDE in surface, "both pins must be on the field surface"
    assert INSIDE in blind and INSIDE not in reachable, (
        f"{INSIDE} was expected to feed no template formula; if the template changed, the exhibit "
        "family E2 needs a new landing cell and this pin needs a new argument"
    )
    assert OUTSIDE in reachable and OUTSIDE not in blind, (
        f"{OUTSIDE} feeds the row total the recompute predicates check; if it has left the "
        "reachable set the precedent map is under-reporting and the ceiling is too small"
    )


def test_golden__the_blind_set_is_what_e2_lands_in() -> None:
    """The two facts that make E2 unkillable, asserted together rather than assumed.

    A categorical swap is unkillable when BOTH hold: the new value is legal by the regulator's own
    validation (so membership passes), and the cell feeds no formula (so no recompute reaches it).
    Either alone is not enough — a legal swap in a *reachable* cell can still break a sum.
    """
    from cdfc.predicates.harvest import _load_context

    _surface, _reachable, blind = _sets()
    ctx = _load_context(FME)
    enum_cells = {
        f"{sheet}!{ref}"
        for sheet, dvs in ctx.validations_by_sheet.items()
        for dv in dvs
        if dv.type == "list"
        for part in dv.sqref.split()
        for ref in __import__(
            "cdfc.predicates.harvest", fromlist=["expand"]
        ).expand(part.replace("$", ""))
    }
    landing = enum_cells & blind
    assert landing, (
        "no cell carries a controlled vocabulary AND feeds no formula, so exhibit family E2 has "
        "nowhere to land on this template and the residue argument loses its measured half"
    )
    assert len(landing) >= 100, f"only {len(landing)} candidate landing cells; expected many"
