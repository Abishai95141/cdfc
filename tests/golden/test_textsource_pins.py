"""P7-B0 — the instrument text, pinned BY VALUE (R-GOLD-2).

A count that matches a pinned count is evidence about the count. These pin the CONTENTS: the first,
median and last unit's key, span and rendered text, plus the digest of the whole instrument. This
repository has now found the count-agreeing-with-a-pin defect five times, and every one of them was
in an instrument that counted correctly and reported the wrong thing.

Moving any number here means the addressable text moved, and **every span recorded against this
instrument now points at different characters**. That is a regression until an entry in
`docs/HARVEST-DELTA.md` says otherwise.

**THE INSTRUMENT DIGEST AND THE ADDRESSABLE TEXT ARE PINNED SEPARATELY, and they used to be one.**
`N1`'s re-pin added a derived DIVISION MAP to the digest payload without touching a single unit or
span, so `sha256` moved while the addressable text was byte-identical — and a single pin cannot
tell those apart. It reads as *"every span is stale"* when nothing is. `ADDRESSABLE_SHA256` covers
the text and the units and NOTHING derived from them: it is the one that must never move, and it
did not.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.instruments import CORPUS, InstrumentStore  # noqa: E402
from cdfc.qualify.template_instrument import emit  # noqa: E402
from cdfc.qualify.textsource import Corroboration  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"

# The whole-instrument digest, which covers derived layers too. It MOVED at the N1 re-pin
# (`01b3962c7eef…` -> `dacd124a712e…`) because `textsource.build()` now derives a division map into
# the payload. `docs/HARVEST-DELTA.md` carries the entry; `tools/repin_divisions.py` asserts the
# text and every unit were unchanged, and `ADDRESSABLE_SHA256` below is the pin that proves it.
FME_SHA256 = "dacd124a712eb87ae73e7ddd96d7e53aabcb81cbe6f0eaeb8e4ecd7fdb06f957"
FME_CHARS = 27633
FME_COUNTS = {"AGREED": 539, "SINGLE_PARTY": 20, "DISPUTED": 0, "units_total": 559}

# (index, key, span, rendered text, corroboration)
FME_PINS = (
    (0, "0000|000002|00004|V|1. Introduction!D2", (0, 50),
     "1. Introduction!D2 :: list - :: Dropdown!$D$3:$D$6", "SINGLE_PARTY"),
    (279, "0002|000084|00025|F|3. Portfolio!Y84", (15363, 15402),
     "3. Portfolio!Y84 :: IFERROR(X84/$O$7,0)", "AGREED"),
    (558, "0009|000011|00013|V|Dropdown!M11", (27605, 27633),
     "Dropdown!M11 :: whole - :: 0", "AGREED"),
)

# The whole corpus, so a change on any of the nine is visible here.
CORPUS_UNITS = 1729
CORPUS_AGREED = 1691
CORPUS_SINGLE = 38
CORPUS_DISPUTED = 0


# THE ADDRESSABLE TEXT, pinned on its own. Text plus every unit's identity, page, offsets and
# corroboration — and nothing derived. A change here means a span into this instrument now points
# at different characters, which is the regression the module docstring describes. A change to
# `FME_SHA256` alone does not.
ADDRESSABLE_SHA256 = "bf962b633585ce0420ed962f13b419eb20a002ee01b02ce8b39775bf77e22b2c"


def _addressable_digest(it) -> str:
    from cdfc.canon import digest

    return digest({
        "text": it.text,
        "units": [
            [u.key, u.page, u.corroboration.value, list(u.parties), u.external_party, *u.span]
            for u in it.units
        ],
    })


@pytest.fixture(scope="module")
def fme():
    return emit(FME)


def test_golden__fme_instrument_digest_and_size(fme):
    assert fme.instrument_id == "template-7d9a1960"
    assert len(fme.text) == FME_CHARS
    assert fme.sha256 == FME_SHA256


def test_golden__fme_addressable_text_did_not_move(fme):
    """The pin that must never move. Separate from `FME_SHA256` since the N1 re-pin — see above."""
    assert _addressable_digest(fme) == ADDRESSABLE_SHA256


def test_golden__fme_first_median_last_unit_pinned_by_value(fme):
    assert len(fme.units) == FME_COUNTS["units_total"]
    for idx, key, span, text, corro in FME_PINS:
        u = fme.units[idx]
        assert u.key == key, f"unit {idx}'s identity moved"
        assert u.span == tuple(span), f"unit {idx}'s offsets moved; every span into it is stale"
        assert fme.text[u.span[0] : u.span[1]] == text, f"unit {idx}'s CONTENTS moved"
        assert u.corroboration.value == corro


def test_golden__fme_corroboration_counts(fme):
    assert dict(fme.counts()) == FME_COUNTS
    # The 20 uncorroborated units are the 19 x14 validations plus the single array formula, and
    # each is a NAMED, checkable blindness rather than a judgement.
    blind = {m.extractor: m.n_blind for m in fme.manifests}
    assert blind == {"openpyxl": 20, "reader_lxml+calc.shift": 0}


def test_golden__corpus_wide_counts():
    totals = {"units_total": 0, "AGREED": 0, "SINGLE_PARTY": 0, "DISPUTED": 0}
    for p in sorted(FIX.glob("*.xlsx")):
        for k, v in emit(p).counts().items():
            totals[k] += v
    assert totals["units_total"] == CORPUS_UNITS
    assert totals[Corroboration.AGREED.value] == CORPUS_AGREED
    assert totals[Corroboration.SINGLE_PARTY.value] == CORPUS_SINGLE
    assert totals[Corroboration.DISPUTED.value] == CORPUS_DISPUTED


def test_golden__the_committed_corpus_matches_a_fresh_build(fme):
    """`corpus/instruments/` is committed evidence, so a stale file is a build that ships a text
    nobody regenerated. This is the same rule the campaign reports live under."""
    store = InstrumentStore(REPO / CORPUS)
    stored = store.get("template-7d9a1960")
    assert stored.sha256 == fme.sha256, "run `make instruments`; the committed text is stale"
    assert stored.text == fme.text


def test_golden__the_manifest_declares_the_statutory_corpus():
    """S1, 16 Aug 2026. **This assertion was inverted, and the inversion is the point.**

    Until S1 this read `statute_instruments == []` and pinned `statute_absent_reason`, because
    D-P7-01 recorded that no statutory instrument existed and that the absence had to be a field
    with a value rather than a section nobody wrote. The instrument is now pinned, so the same
    discipline applies in the other direction: the presence is asserted, its count is asserted,
    and `statute_absent_reason` must now be EMPTY. A stale absence reason beside a present statute
    would let a reader conclude the corpus is still empty from a field nobody updated.
    """
    m = json.loads((REPO / CORPUS / "MANIFEST.json").read_text(encoding="utf-8"))
    assert m["statute_instruments"] == ["statute-fm-regulations-2025"]
    assert m["statute_absent_reason"] == ""
    # B3, 20 Aug 2026: a third KIND appears. `source-fincen-boir-instructions` is the first PDF
    # pinned as a SOURCE -- an uploaded document that evidence is read FROM, as against a STATUTE
    # whose rules are read from it or a TEMPLATE whose fields are read from it.
    #
    # The pin is EXTENDED, not loosened. Each kind carries its own count, so a fourth kind
    # appearing, or a template quietly becoming a source, still goes red -- a set membership
    # assertion alone would admit nine templates turning into nine sources without a word.
    kinds = {i["kind"] for i in m["instruments"]}
    assert kinds == {"TEMPLATE", "STATUTE", "SOURCE"}, (
        f"the corpus holds kinds {sorted(kinds)}. A new kind is a corpus decision and belongs in "
        f"docs/AUDIT-TRAIL.md before it belongs here."
    )
    assert len(m["instruments"]) == 11
    assert sum(1 for i in m["instruments"] if i["kind"] == "TEMPLATE") == 9
    assert sum(1 for i in m["instruments"] if i["kind"] == "STATUTE") == 1
    assert sum(1 for i in m["instruments"] if i["kind"] == "SOURCE") == 1
