"""P7-B0 — the instrument text source, unit by unit."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify import template_instrument as TI  # noqa: E402
from cdfc.qualify.instruments import deserialise, serialise  # noqa: E402
from cdfc.qualify.textsource import (  # noqa: E402
    REFUSED_TRANSFORMATIONS,
    TRANSFORMATIONS,
    Corroboration,
    DisputedRegionError,
    Extraction,
    SpanOutOfRangeError,
    TextSourceError,
    Unit,
    build,
    normalise,
)

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


def _party(name: str, units: dict[str, str], *, external: bool = False, blind=None) -> Extraction:
    return Extraction(
        extractor=name,
        version="test",
        external=external,
        units=tuple(Unit(key=k, text=v, page=1) for k, v in sorted(units.items())),
        blind_to=dict(blind or {}),
    )


# --- normalisation ---------------------------------------------------------------------


def test_textsource__normalisation_is_the_declared_list():
    assert [n for n, _ in TRANSFORMATIONS] == ["strip_soft_hyphen", "nfkc", "collapse_whitespace"]
    assert normalise("a­b") == "ab"
    assert normalise("ﬁne") == "fine"  # NFKC expands the ligature a PDF text layer emits
    assert normalise("  a \t\n b  ") == "a b"


def test_textsource__refused_transformations_are_refused():
    """The homoglyph must SURVIVE normalisation, because `test_g0__verbatim_quote_required` plants
    exactly one — a hyphen-minus swapped for a non-breaking hyphen. A normaliser that folded them
    would make that gate unfailable."""
    assert {n for n, _ in REFUSED_TRANSFORMATIONS} == {"unify_dashes", "case_fold", "unify_quotes"}
    assert normalise("A-1") != normalise("A‑1")
    assert normalise("Abc") != normalise("abc")
    assert normalise("'x'") != normalise("‘x’")


def test_textsource__replacement_character_is_an_extraction_failure():
    with pytest.raises(TextSourceError, match="U\\+FFFD"):
        normalise("reg 51�1")


# --- the parties -----------------------------------------------------------------------


def test_textsource__one_extraction_is_refused():
    with pytest.raises(TextSourceError, match="NC-Q47"):
        build("x", [_party("a", {"k": "t"})])


def test_textsource__an_unexplained_absence_fails_the_build():
    """The rule that separates a MISS from an exclusion. `b` read nothing at `k2` and named no
    mechanism, so the build refuses rather than labelling the unit merely uncorroborated."""
    with pytest.raises(TextSourceError, match="MISS, not an exclusion"):
        build("x", [_party("a", {"k1": "t", "k2": "u"}), _party("b", {"k1": "t"})])


def test_textsource__a_declared_absence_is_single_party():
    it = build("x", [
        _party("a", {"k1": "t", "k2": "u"}),
        _party("b", {"k1": "t"}, blind={"k2": "b cannot see this construct"}),
    ])
    states = {u.key: u.corroboration for u in it.units}
    assert states == {"k1": Corroboration.AGREED, "k2": Corroboration.SINGLE_PARTY}
    assert it.counts() == {"AGREED": 1, "SINGLE_PARTY": 1, "DISPUTED": 0, "units_total": 2}


def test_textsource__a_party_may_not_excuse_itself_from_a_unit_it_read():
    with pytest.raises(TextSourceError, match="both read a construct and excuse itself"):
        _party("b", {"k1": "t"}, blind={"k1": "a mechanism"})


def test_textsource__a_blindness_without_a_mechanism_is_refused():
    with pytest.raises(TextSourceError, match="no mechanism"):
        _party("b", {"k1": "t"}, blind={"k2": "   "})


# --- disputed regions ------------------------------------------------------------------


def test_textsource__disputed_region_is_not_addressable():
    it = build("x", [_party("a", {"k1": "same", "k2": "left"}),
                     _party("b", {"k1": "same", "k2": "right"})])
    d = it.disputed[0]
    assert d.key == "k2"
    assert it.is_disputed(d.span)
    with pytest.raises(DisputedRegionError, match="disputed region"):
        it.slice(d.span)
    # and the agreed unit next to it is still readable
    agreed = next(u for u in it.units if u.corroboration is Corroboration.AGREED)
    assert it.slice(agreed.span) == "same"


def test_textsource__a_span_straddling_a_dispute_is_refused():
    it = build("x", [_party("a", {"k1": "same", "k2": "left"}),
                     _party("b", {"k1": "same", "k2": "right"})])
    with pytest.raises(DisputedRegionError):
        it.slice((0, len(it.text)))


def test_textsource__an_out_of_range_span_is_a_different_failure():
    """Two failures, two remedies: a wrong offset is fixed by fixing the offset; a disputed region
    is fixed by re-quoting or by recording that the obligation is not addressable."""
    it = build("x", [_party("a", {"k": "t"}), _party("b", {"k": "t"})])
    with pytest.raises(SpanOutOfRangeError):
        it.slice((0, 9999))
    assert not issubclass(SpanOutOfRangeError, DisputedRegionError)


def test_textsource__find_all_returns_disputed_occurrences_too():
    """G0 must tell `the quote is nowhere` from `the quote is where we excluded`. Filtering here
    would collapse two reasons that have different remedies."""
    it = build("x", [_party("a", {"k1": "aa", "k2": "bb"}), _party("b", {"k1": "aa", "k2": "cc"})])
    assert it.find_all("aa") == ((0, 2),)
    assert it.find_all("bb") == ()
    assert it.find_all("�")  # the sentinel occupies the disputed span


# --- layout ----------------------------------------------------------------------------


def test_textsource__layout_does_not_depend_on_party_order():
    a = _party("a", {"k2": "two", "k1": "one"})
    b = _party("b", {"k1": "one", "k2": "two"})
    assert build("x", [a, b]).sha256 == build("x", [b, a]).sha256


def test_textsource__spans_partition_the_text():
    it = TI.emit(FME)
    for u in it.units:
        assert 0 <= u.span[0] <= u.span[1] <= len(it.text)
    for prev, nxt in zip(it.units, it.units[1:]):
        assert prev.span[1] < nxt.span[0], "units must not overlap"
        assert it.text[prev.span[1] : nxt.span[0]] == "\n", "units are joined by exactly one LF"


def test_textsource__offsets_are_stable_under_regeneration():
    """Regenerating from the same bytes reproduces byte-identical offsets. A span recorded against
    an instrument that re-lays-out on every build is not a span."""
    a, b = TI.emit(FME), TI.emit(FME)
    assert a.sha256 == b.sha256
    assert a.text == b.text
    assert [u.span for u in a.units] == [u.span for u in b.units]


def test_textsource__a_stored_instrument_reproduces_and_a_tampered_one_does_not():
    it = TI.emit(FME)
    blob = serialise(it, kind="TEMPLATE", source_name="fme", source_sha256="00" * 32)
    back, kind, name, sha = deserialise(blob)
    assert (kind, name, sha) == ("TEMPLATE", "fme", "00" * 32)
    assert back.sha256 == it.sha256 and back.text == it.text
    tampered = blob.replace(b'"text":"', b'"text":"X', 1)
    with pytest.raises(TextSourceError, match="points somewhere else"):
        deserialise(tampered)


def test_textsource__the_addressable_fraction_is_two_integers():
    it = TI.emit(FME)
    ok, total = it.addressable_fraction()
    assert total == it.counts()["units_total"]
    assert ok == total - it.counts()[Corroboration.DISPUTED.value]


def test_textsource__sqref_range_order_is_not_a_disagreement():
    """The defect this build found on its first run: two parties serialise the SET of ranges in a
    `sqref` in different orders, so eleven validations looked like disagreements and — worse —
    landed on different keys and were never compared at all."""
    assert TI._norm_ref("L132 K2 H132") == TI._norm_ref("K2 H132 L132")
    assert TI._anchor("L132 K2 H132") == TI._anchor("H132 L132 K2")
    # a GENUINE difference in the set still shows
    assert TI._norm_ref("K2 L132") != TI._norm_ref("K2 L133")
