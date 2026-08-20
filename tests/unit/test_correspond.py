"""A1c — the correspondence, and the case that made it necessary.

Graded binding was built, measured unsafe and reverted because a row insertion renumbers every
cell below it: 3,544 addresses common to both files, **1,451 of them holding a different field**.
A name-based align is silently wrong on 41% of what it matches. These tests are that case.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cdfc.correspond.align import Unaligned, correspond

BLANK = Path("fixtures/prescribed/"
             "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
INSERTED = Path("fixtures/synthetic/row-inserted__portfolio-r7.xlsx")
CLEAN = Path("fixtures/synthetic/clean__independently-computed__fme-q1.xlsx")


def _rc(ref: str) -> tuple[str, str, int]:
    sheet, cell = ref.rsplit("!", 1)
    return sheet, "".join(c for c in cell if c.isalpha()), int("".join(c for c in cell if c.isdigit()))


@pytest.fixture(scope="module")
def inserted():
    return correspond(BLANK, INSERTED)


def test_a1c__every_alignment_is_correct_against_the_known_transformation(inserted) -> None:
    """`tools/fixtures/make_synthetic.py` shifts '3. Portfolio' rows >= 7 down by one and touches
    nothing else. That is the ground truth, and it is a construction rather than a judgement."""
    assert inserted.pairs, "no alignments would make this vacuous"
    wrong = []
    for a, b in inserted.pairs:
        sa, la, na = _rc(a)
        sb, lb, nb = _rc(b)
        want = na + 1 if (sa == "3. Portfolio" and na >= 7) else na
        if not (sa == sb and la == lb and nb == want):
            wrong.append((a, b))
    assert not wrong, f"{len(wrong)} of {len(inserted.pairs)} aligned to the wrong field: {wrong[:5]}"


def test_a1c__it_beats_the_name_based_align_it_replaces(inserted) -> None:
    """The measurement that justified A1c: matching by ADDRESS is wrong on 1,451 of 3,544."""
    from cdfc.measure.p5_run import surface_for

    common = set(surface_for(BLANK)[1]) & set(surface_for(INSERTED)[1])
    by_name_wrong = sum(1 for r in common
                        if r.startswith("3. Portfolio!") and _rc(r)[2] >= 7)
    assert by_name_wrong > 1000, "the premise moved; re-measure before trusting this test"
    # The structural align makes NONE of those errors, because it never matches by address.
    assert all(_rc(a)[2] + 1 == _rc(b)[2]
               for a, b in inserted.pairs
               if _rc(a)[0] == "3. Portfolio" and _rc(a)[2] >= 7)


def test_a1c__both_sides_are_declared(inserted) -> None:
    """Coverage over a correspondence must name what the BLANK lost and what the FILING added.
    Reporting only one side is how a partial alignment reads as a complete one."""
    # The invariant is that the arithmetic CLOSES on both sides, not that anything failed to
    # align. On this pair everything does align, and an earlier version of this test asserted
    # otherwise because it was written against a bug: rows carrying no text had no signature, so
    # they never entered the alignment and were reported unmatched.
    from_blank = len([u for u in inserted.unaligned if u[1] is not Unaligned.ADDED_BY_FILER])
    added = len([u for u in inserted.unaligned if u[1] is Unaligned.ADDED_BY_FILER])
    assert inserted.aligned + from_blank == inserted.blank_total
    assert inserted.aligned + added == inserted.filing_total
    assert {w for _r, w in inserted.unaligned} <= set(Unaligned), "closed vocabulary"


def test_a1c__an_ambiguous_alignment_is_refused(inserted) -> None:
    """Two candidate alignments of similar quality is the same hazard as two pinned blanks sharing
    a sheet set. It must stay a refusal rather than become a coin toss."""
    assert inserted.ambiguous
    assert inserted.detail, "a refusal that cannot say WHY sends the reader to guess"


def test_a1c__an_identical_pair_aligns_completely() -> None:
    """The positive control. If a file does not align to ITSELF, nothing below it means anything."""
    c = correspond(BLANK, BLANK)
    assert c.aligned == c.blank_total == c.filing_total
    assert all(a == b for a, b in c.pairs)


def test_a1c__a_filled_filing_still_aligns_to_its_blank() -> None:
    """A filer changes VALUES, and the alignment must not move: the signature is text, not value."""
    c = correspond(BLANK, CLEAN)
    assert c.aligned > c.blank_total * 0.9, (
        f"only {c.aligned} of {c.blank_total} aligned; filling a form must not break its identity"
    )
