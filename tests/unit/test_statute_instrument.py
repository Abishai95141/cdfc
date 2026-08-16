"""S1 — the first `kind: STATUTE` instrument, asserted against the PINNED artifact.

These tests read `corpus/instruments/statute-fm-regulations-2025.text.json` and **import no PDF
library**. That is the design, not a convenience: the extractors are build-time tools, the pinned
JSON is what the system reads, and a test that re-extracted would be testing the tool rather than
the artifact every span in this repository points into.
"""

from __future__ import annotations

import pytest

from cdfc.qualify.instruments import InstrumentStore
from cdfc.qualify.textsource import Corroboration, DisputedRegionError

INSTRUMENT_ID = "statute-fm-regulations-2025"

# Pinned from `docs/measurements/S1-instrument-agreement.md`, which `tools/pin_statute.py` writes.
# A change to any of these is a change to what every recorded span means.
UNITS_TOTAL = 1218
AGREED = 1189
SINGLE_PARTY = 1
DISPUTED = 28
SOURCE_SHA256 = "f136c7bec0c1be16eef951ea29650692c1c5383f61725b63f04ce1f754ee153b"


@pytest.fixture(scope="module")
def store() -> InstrumentStore:
    return InstrumentStore()


def test_statute__the_corpus_is_no_longer_empty(store: InstrumentStore) -> None:
    """D-P7-01's headline number. `statute_instruments: []` was the reason P13 had no input."""
    assert store.statute_ids() == (INSTRUMENT_ID,)


def test_statute__counts_are_the_published_ones(store: InstrumentStore) -> None:
    c = store.get(INSTRUMENT_ID).counts()
    assert c["units_total"] == UNITS_TOTAL
    assert c["AGREED"] == AGREED
    assert c["SINGLE_PARTY"] == SINGLE_PARTY
    assert c["DISPUTED"] == DISPUTED
    # The partition closes. A census whose parts do not sum to its total is the defect this
    # project is named for, and it is asserted rather than assumed at every level.
    assert c["AGREED"] + c["SINGLE_PARTY"] + c["DISPUTED"] == c["units_total"]


def test_statute__both_parties_are_external(store: InstrumentStore) -> None:
    """Neither reader was written here — stronger evidence than the nine TEMPLATE instruments.

    For a workbook one party is `openpyxl` and the other is ours, so `SAME_AUTHOR` carries real
    units. Here it must be empty: a same-author unit would mean an arm crept in from `src/`.
    """
    ag = store.get(INSTRUMENT_ID).agreement()
    assert ag["SAME_AUTHOR"] == (0, 0)
    assert ag["EXTERNAL"][1] > 0
    assert ag["EXTERNAL"] == (AGREED, AGREED + DISPUTED)


def test_statute__a_disputed_span_is_not_addressable(store: InstrumentStore) -> None:
    """`slice()` RAISES on a disputed region. The whole point of declaring one.

    28 units are disputed. If `slice` returned the sentinel, or one party's reading, a quote into
    a region the parties could not agree on would look exactly like a quote into one they did.
    """
    it = store.get(INSTRUMENT_ID)
    assert it.disputed, "the instrument declares disputed regions; this test needs one"
    with pytest.raises(DisputedRegionError):
        it.slice(it.disputed[0].span)


def test_statute__find_all_still_returns_disputed_occurrences(store: InstrumentStore) -> None:
    """G0 must tell *the quote is nowhere* from *the quote is in a region we excluded*.

    Filtering here would collapse two findings with two different remedies into one.
    """
    it = store.get(INSTRUMENT_ID)
    region = it.disputed[0]
    # The sentinel occupies a disputed unit's span, so searching for it finds every disputed one.
    hits = it.find_all(it.text[region.span[0]:region.span[1]])
    assert hits, "a disputed region's own text is not findable — find_all is filtering"
    assert any(it.is_disputed(h) for h in hits)


def test_statute__an_agreed_span_reads_back_as_clause_text(store: InstrumentStore) -> None:
    """The end-to-end property every G0 figure rests on: a span resolves to quotable text."""
    it = store.get(INSTRUMENT_ID)
    agreed = [u for u in it.units if u.corroboration is Corroboration.AGREED]
    assert len(agreed) == AGREED
    body = it.slice(agreed[40].span)
    assert body and body == body.strip()
    # Whitespace is collapsed by `normalise`, so no unit carries newlines or runs of spaces --
    # column geometry is a property of the rendering, never of the instrument.
    assert "\n" not in body and "  " not in body


def test_statute__the_source_digest_is_the_pinned_one(store: InstrumentStore) -> None:
    """The bytes this text was derived from, asserted against `docs/CORPUS-PROVENANCE.md`."""
    import json
    from pathlib import Path

    blob = json.loads(
        Path(f"corpus/instruments/{INSTRUMENT_ID}.text.json").read_bytes().decode("utf-8")
    )
    assert blob["kind"] == "STATUTE"
    assert blob["source_sha256"] == SOURCE_SHA256
    assert blob["source_name"] == "fm-regulations-2025.pdf"


def test_statute__no_unit_carries_a_devanagari_character(store: InstrumentStore) -> None:
    """The Hindi half is EXCLUDED, and the exclusion actually held.

    Pages 1–142 are the same instrument in Hindi. They are declared out rather than dropped, and
    this asserts the declaration did what it says: a Devanagari character reaching a unit would
    mean the running-header rule leaked and the boundary is not where the measurement claims.
    """
    it = store.get(INSTRUMENT_ID)
    assert not [c for c in it.text if "ऀ" <= c <= "ॿ"]


def test_statute__unit_keys_sort_into_document_order(store: InstrumentStore) -> None:
    """`Unit.key`'s contract, asserted on the real artifact rather than on a fixture.

    Lexicographic order must be document order, or the assembled text is laid out in an order that
    depends on nothing in particular and every span moves the next time it is built.
    """
    it = store.get(INSTRUMENT_ID)
    keys = [u.key for u in it.units]
    assert keys == sorted(keys)
    pages = [u.page for u in it.units]
    assert pages == sorted(pages)
    # And the spans march forward without overlapping.
    spans = [u.span for u in it.units]
    assert all(a[1] <= b[0] for a, b in zip(spans, spans[1:], strict=False))


def test_statute__obligations_can_now_resolve_against_a_statute(store: InstrumentStore) -> None:
    """The number D-P7-01 said this build changes.

    `predicates_with_a_STATUTE_obligation / N` read `0 / N` because **no statute was pinned at
    all**, not because no predicate cited one. That is no longer the reason, and the funnel's
    obligation-coverage pair must stop being a structural zero and start being a measurable one.
    """
    assert store.kind_of(INSTRUMENT_ID) == "STATUTE"
    it = store.get(INSTRUMENT_ID)
    # 682 `shall` occurrences across the addressable text: a real pool, not an empty one.
    assert len(it.find_all("shall")) > 100
