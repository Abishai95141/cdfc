"""N1 — the division map, pinned BY VALUE, and every pin is a defect this build actually shipped.

`R-GOLD-2`: a count that matches a pinned count is evidence about the count. So these pin CONTENTS
— the eId, the heading, the shape that recovered it, and the refusal reason — for the five things
that went wrong while the module was being written. Each one was observed red here first:

    div2_0003          THIRD SCHEDULE was declared "not recovered" while sitting mid-unit, 175
                       characters inside the second. The scan was anchored at unit starts.
    div1_0008 heading  read `'8'`, not `'Net worth requirements 8'` — the division was anchored at
                       the margin number instead of at the line carrying it.
    div1_0148          carried 181 units, the whole schedule set, because no run bounded it.
    div1_0002__sub_*   `(aa) (bb) (cc)` decoded as 27, 54, 81 under a base-26 reading, so the map
                       published 336 rows claiming ordinals had been skipped that no document ever
                       numbered.
    run 3              returned the sixth schedule's own lettered list as a third top-level
                       sequence, duplicating divisions already addressed as subdivisions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.instruments import CORPUS, deserialise  # noqa: E402
from cdfc.qualify.provisions import (  # noqa: E402
    MARKER_SHAPES,
    DivisionRefusal,
    _letter,
    _roman,
    _stable_chain,
    recover,
)

STATUTE = "statute-fm-regulations-2025"

TOP_LEVEL_DIVISIONS = 153      # 147 regulations + 6 schedules
REGULATIONS = 147
SCHEDULES = 6
SUBDIVISIONS = 464
REFUSED = 58
UNITS_OUTSIDE = 3              # the two-unit preamble, and the notification line


@pytest.fixture(scope="module")
def statute():
    blob = (CORPUS / f"{STATUTE}.text.json").read_bytes()
    it, _kind, _name, _sha = deserialise(blob)
    return it


def test_golden__division_counts(statute):
    m = statute.divisions
    assert len(m.top_level()) == TOP_LEVEL_DIVISIONS
    assert sum(1 for d in m.top_level() if d.run == 1) == REGULATIONS
    assert sum(1 for d in m.top_level() if d.run == 2) == SCHEDULES
    assert sum(1 for d in m.divisions if d.depth == 1) == SUBDIVISIONS
    assert len(m.refused) == REFUSED
    assert m.units_outside_any_division == UNITS_OUTSIDE


def test_golden__the_map_is_re_derived_not_trusted(statute):
    """`deserialise` recomputes the map from the text. The stored block is for reading only."""
    stored = json.loads((CORPUS / f"{STATUTE}.text.json").read_bytes())
    assert len(stored["divisions"]) == len(statute.divisions.divisions)
    fresh = recover(
        [(u.key, u.page, u.span, u.corroboration.value) for u in statute.units], statute.text
    )
    assert [d.eid for d in fresh.divisions] == [d.eid for d in statute.divisions.divisions]
    assert [d.span for d in fresh.divisions] == [d.span for d in statute.divisions.divisions]


def test_golden__regulation_8_carries_its_heading_not_just_its_number(statute):
    """The `heading='44'` defect: a trailing-marker division starts at the LINE, not the number."""
    d = statute.division("div1_0008")
    assert d is not None
    assert d.heading == "Net worth requirements 8"
    assert d.recovered_by == "DECIMAL_TRAILING"
    assert statute.text[d.span[0]:d.span[1]].startswith("Net worth requirements 8\n(1) An entity")
    sub = statute.division("div1_0008__sub_0001")
    assert sub is not None and sub.recovered_by == "PAREN_DECIMAL"
    assert "net worth requirements as specified in Second Schedule" in \
        statute.text[sub.span[0]:sub.span[1]]


def test_golden__third_schedule_is_recovered_mid_unit(statute):
    """It is 175 characters inside another unit. A unit-anchored scan reported it absent."""
    d = statute.division("div2_0003")
    assert d is not None, "THIRD SCHEDULE was declared not-recovered while present in the text"
    assert d.heading.startswith("THIRD SCHEDULE CODE OF CONDUCT")
    assert d.recovered_by == "ORDINAL_WORD"
    assert [x.ordinal for x in statute.divisions.top_level() if x.run == 2] == [1, 2, 3, 4, 5, 6]


def test_golden__the_last_regulation_does_not_swallow_the_schedules(statute):
    """`div1_0148` carried 181 units — every schedule — until a second run bounded it."""
    d = statute.division("div1_0148")
    assert d is not None and d.heading == "Repeal and Savings 148"
    assert len(d.unit_keys) == 12
    first_schedule = statute.division("div2_0001")
    assert d.span[1] <= first_schedule.span[0]


def test_golden__doubled_letters_are_a_sequence_not_a_base_26_numeral():
    """`(aa) (bb) (cc)` is 27, 28, 29 in legal drafting. Base-26 read them as 27, 54, 81."""
    assert [_letter(x) for x in ("a", "z", "aa", "bb", "cc", "dd")] == [1, 26, 27, 28, 29, 30]
    # A two-letter word in parentheses is not an ordinal in either convention.
    assert [_letter(x) for x in ("is", "if", "ab")] == [None, None, None]
    assert [_roman(x) for x in ("i", "iv", "ix", "x")] == [1, 4, 9, 10]


def test_golden__regulation_2_definitions_number_past_z(statute):
    """The doubled-letter defect published 336 false 'ordinal skipped' rows in this division."""
    d = statute.division("div1_0002__sub_0027")
    assert d is not None
    assert statute.text[d.span[0]:d.span[1]].startswith("(aa) ")
    skipped = [r for r in statute.divisions.refused
               if r[1] == DivisionRefusal.ORDINAL_SKIPPED.value and "div1_0002" in r[0]]
    assert skipped == [], f"{len(skipped)} ordinals reported skipped inside regulation 2"


def test_golden__regulation_100_is_refused_as_disputed_not_missed(statute):
    """Its heading is inside the disputed region on page 177. The remedy is a third party."""
    assert 100 not in {d.ordinal for d in statute.divisions.top_level() if d.run == 1}
    rows = [r for r in statute.divisions.refused
            if r[1] == DivisionRefusal.ANCHOR_DISPUTED.value and r[0].startswith("100@")]
    assert len(rows) == 1
    assert "div1_0099" in rows[0][2] and "disputed unit" in rows[0][2]


def test_golden__every_refusal_takes_a_reason_from_the_closed_vocabulary(statute):
    vocab = {r.value for r in DivisionRefusal}
    assert {r[1] for r in statute.divisions.refused} <= vocab
    assert all(r[2].strip() for r in statute.divisions.refused), \
        "a refusal with no text is a refusal nobody can check"


def test_golden__the_top_level_shape_is_discovered_by_a_wide_margin(statute):
    """Nothing declares the margin number is the top level. It wins on a measured criterion."""
    depth0 = [s for s in statute.divisions.selections if s.depth == 0]
    run1 = next(s for s in depth0 if s.run == 1)
    assert set(run1.shapes) == {"DECIMAL_TRAILING", "DECIMAL_LEADING"}
    assert run1.chain_length == 147
    assert run1.margin > 0.4, "the top level was nearly a coin-toss"
    run2 = next(s for s in depth0 if s.run == 2)
    assert run2.shapes == ("ORDINAL_WORD",)
    assert run2.margin > 0.7


def test_golden__no_third_run_of_subdivisions(statute):
    """Run 3 returned the sixth schedule's lettered list as a top-level sequence, opening at 2."""
    assert {d.run for d in statute.divisions.top_level()} == {1, 2}


def test_golden__eids_sort_into_document_order(statute):
    top = statute.divisions.top_level()
    assert [d.eid for d in top] == sorted(d.eid for d in top)
    assert [d.span[0] for d in top] == sorted(d.span[0] for d in top)


def test_golden__a_tie_is_refused_rather_than_resolved():
    """Two ascending chains of equal length share a depth, so neither element is stable."""
    # 1, 5, 2, 6 -> two maximum chains (1,5,6) and (1,2,6). 5 and 2 share depth 2 and are unstable.
    cand = [(0, 1, "S"), (10, 5, "S"), (20, 2, "S"), (30, 6, "S")]
    length, stable = _stable_chain(cand)
    assert length == 3
    assert [cand[j][1] for j in stable] == [1, 6]


def test_golden__a_shape_captures_exactly_one_group():
    for s in MARKER_SHAPES:
        assert s.pattern.groups == 1, f"{s.name} captures {s.pattern.groups}"
        assert s.note.strip(), f"{s.name} carries no note"


def test_golden__a_corpus_matching_no_shape_recovers_nothing_and_says_so():
    """The honest degrade. All nine pinned workbooks land here — a spreadsheet has no numbering."""
    units = [("k0", 1, (0, 12), "AGREED"), ("k1", 1, (13, 25), "AGREED")]
    m = recover(units, "no markers\nnone either")
    assert m.divisions == ()
    assert m.units_outside_any_division == 2
    for blob in sorted(CORPUS.glob("template-*.text.json")):
        it, _k, _n, _s = deserialise(blob.read_bytes())
        assert it.divisions.divisions == (), f"{blob.name} recovered divisions from a workbook"
