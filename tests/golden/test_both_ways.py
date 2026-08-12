"""P4-B2/B4 — the both-ways agreement over the harvested candidates.

**Authored in B2 and first runnable in B4**, because B4 is what produces envelopes to run it
against. FME is the workbook because it carries the most harvest classes and 181 cross-sheet
carries — the class most likely to read a key it did not declare.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.ast_walker import declared_vs_read  # noqa: E402
from cdfc.predicates.cel_profile import check_subset  # noqa: E402
from cdfc.predicates.errors import CelLayerError  # noqa: E402
from cdfc.predicates.harvest import harvest, harvest_all  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
DOC = REPO / "docs" / "measurements" / "P4-both-ways.md"


def _agreement(candidates) -> tuple[int, list[tuple[str, tuple, tuple]]]:
    agree, short = 0, []
    for c in candidates:
        try:
            for slot in ("applicable", "expr", "witness"):
                check_subset(getattr(c, slot), slot=slot)
            undeclared, unread = declared_vs_read(c)
        except CelLayerError as e:
            short.append((c.id, ("<outside the admitted subset>",), (str(e)[:70],)))
            continue
        if undeclared or unread:
            short.append((c.id, undeclared, unread))
        else:
            agree += 1
    return agree, short


def test_golden__both_ways__fme() -> None:
    res = harvest(FME)
    agree, short = _agreement(res.candidates)
    assert short == [], f"shortfalls on FME: {short[:5]}"
    assert agree == len(res.candidates) > 0


@pytest.fixture(scope="module")
def results():
    return harvest_all(FIX)


def test_golden__both_ways__all_nine(results) -> None:
    total = agree_total = 0
    per_workbook = []
    for res in results:
        agree, short = _agreement(res.candidates)
        agree_total += agree
        total += len(res.candidates)
        per_workbook.append((res.workbook, agree, len(res.candidates), short))
    bad = [(w, s) for w, _a, _n, s in per_workbook if s]
    assert bad == [], f"shortfalls: {bad[:3]}"
    assert agree_total == total > 0


def test_golden__the_both_ways_measurement_is_published(results) -> None:
    """A headline number a reviewer cannot open is a screenshot."""
    doc = DOC.read_text(encoding="utf-8")
    total = sum(len(r.candidates) for r in results)
    assert f"**{total} of {total}**" in doc, "the measurement file does not carry the number"
    assert "UndeclaredKeyRead" in doc and "DeclaredKeyUnread" in doc, (
        "the two directions must be named separately; they have different remedies"
    )
    assert "NC-N01" in doc, (
        "the file must state what the number does NOT license: that any predicate encodes its "
        "clause. A negative control for that is impossible."
    )
    m = re.search(r"\*\*(\d+) of (\d+)\*\*", doc)
    assert m and int(m.group(1)) == int(m.group(2)) == total


def test_golden__the_measurement_is_reproducible_from_the_code(results) -> None:
    from cdfc.measure.harvest_report import render_both_ways

    assert render_both_ways(results) == DOC.read_text(encoding="utf-8"), (
        "the published measurement is not what the code renders today. Re-run `make harvest` — "
        "and if you did not change the harvest, ask why the file moved."
    )
