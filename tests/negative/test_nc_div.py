"""NC-DIV — the guards for the N1 division map, written to fail on the DEFECT rather than on a digest.

**Why these do not go through `deserialise`.** Any edit to `qualify/provisions.py` changes the map
the instrument digest covers, so a pinned instrument refuses to load at all — which is a real and
useful property, and a useless GUARD: every injector would flip every corpus-reading test with one
identical `TextSourceError`, and the sweep would record four controls as caught while distinguishing
nothing. A control that cannot tell which break happened is a control that has not measured one.

So each guard reads the instrument's raw text and calls `recover()` directly, and asserts the
specific thing that specific defect destroys.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.provisions import DivisionRefusal, _letter, _stable_chain, recover  # noqa: E402

STATUTE = REPO / "corpus/instruments/statute-fm-regulations-2025.text.json"


@pytest.fixture(scope="module")
def raw():
    obj = json.loads(STATUTE.read_bytes().decode("utf-8"))
    units = [(u["key"], u["page"], (u["span"][0], u["span"][1]), u["corroboration"])
             for u in obj["units"]]
    return recover(units, obj["text"])


def test_nc__DIV01_all_six_schedules_recover(raw):
    """`LevelByChainLength`: raw chain length picks the schedules' lettered lists over the
    schedules, so the whole second run vanishes and the last regulation absorbs 181 units."""
    run2 = [d.ordinal for d in raw.top_level() if d.run == 2]
    assert run2 == [1, 2, 3, 4, 5, 6], f"the schedule run came out as {run2}"
    last = raw.by_eid()["div1_0148"]
    assert len(last.unit_keys) == 12, (
        f"div1_0148 carries {len(last.unit_keys)} units; it swallowed the schedules"
    )


def test_nc__DIV02_a_trailing_marker_division_carries_its_heading(raw):
    """`AnchorAtMarkerNotLine`: the division starts at the number, so it drops its own heading
    and the total stays a plausible 153."""
    d = raw.by_eid()["div1_0008"]
    assert d.heading == "Net worth requirements 8", f"heading came out as {d.heading!r}"


def test_nc__DIV03_an_unstable_position_is_refused_not_picked():
    """`AcceptUnstableChain`: a tie between two equally good readings becomes a coin-toss."""
    cand = [(0, 1, "S"), (10, 5, "S"), (20, 2, "S"), (30, 6, "S")]
    length, stable = _stable_chain(cand)
    assert length == 3
    assert [cand[j][1] for j in stable] == [1, 6], "an unstable position was admitted"


def test_nc__DIV04_doubled_letters_are_drafting_not_base_26(raw):
    """`DoubledLetterAsBase26`: `(bb)` reads as 54, regulation 2 appears to skip eighty ordinals,
    and the map publishes hundreds of rows for numbers nothing wrote."""
    assert [_letter(x) for x in ("aa", "bb", "cc", "dd")] == [27, 28, 29, 30]
    skipped = [r for r in raw.refused
               if r[1] == DivisionRefusal.ORDINAL_SKIPPED.value and "div1_0002" in r[0]]
    assert skipped == [], f"{len(skipped)} ordinals reported skipped inside regulation 2"


def test_nc__DIV05_positive_control_the_map_still_recovers_the_body(raw):
    """POSITIVE CONTROL. It must stay GREEN under every injector above.

    Without it a recovery that returned nothing at all would score perfectly on the four guards —
    each of which is an assertion about what a WRONG map contains.
    """
    assert len([d for d in raw.top_level() if d.run == 1]) == 147
    assert raw.by_eid()["div1_0008"].recovered_by == "DECIMAL_TRAILING"
