"""P12-B1 — the pool enumerator: what the model is asked about, and what it is never asked about.

Every refusal here shrinks or moves the denominator of `k of 20`. A chapter missed silently is a
smaller pool; a heading unrecognised is a larger one; a `shall` inside `marshalling` is a pool of
words rather than obligations. So the admission side is tested beside the refusals — a module that
raised on everything would satisfy every negative test in this file.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.draw import ChapterNotFound, Pool  # noqa: E402
from cdfc.experiment.enumerate_shall import (  # noqa: E402
    NotAStatute,
    UndeclaredHeading,
    _sub_clause_key,
    enumerate_shall,
    is_obligation_token_at,
    parse_citation,
    sentences,
)
from cdfc.qualify.textsource import Extraction, Unit, build  # noqa: E402

# --- the synthetic statute ---------------------------------------------------------------------
#
# No statutory instrument is pinned in this repository (D-P7-01), so the fixture is built here and
# every property it carries is deliberate:
#
#   u060  two sentences in ONE unit, the second preceded by a run of spaces — the span-trim case
#   u070  sub-clause (10) BEFORE (9) in document order — arithmetic ordering, not lexical
#   u090  `marshalling`, a real word from financial regulation that contains the token
#   u050  regulation 9 against regulation 51 — 9 sorts first arithmetically, last lexically
#
# Keys sort in document order because the addressable text is laid out in `sorted(key)` order.

_UNITS: tuple[tuple[str, str, int], ...] = (
    ("u010", "Chapter I - Preliminary", 1),
    ("u020", "1. (1) These regulations may be cited as the Reporting Regulations 2026.", 1),
    ("u030", "2. (1) The Authority shall publish the forms.", 1),
    ("u040", "Chapter II - Reporting", 2),
    ("u050", "9. (1) The FME shall file the return.", 2),
    ("u060", "51. (1) The FME shall retain the records for six years.   "
             "51. (2) The FME shall index them.", 3),
    ("u070", "51. (10) The FME shall notify the Authority.", 3),
    ("u080", "51. (9) The FME shall reconcile the balances.", 3),
    ("u090", "72. (1) The marshalling of collateral is described in the Schedule.", 4),
    ("u100", "Chapter III - Netting", 5),
    ("u110", "80. (1) The FME shall net the exposures.", 5),
    ("u120", "Chapter IV - Citation", 6),
    ("u130", "90. (1) These regulations come into force on 1 April 2026.", 6),
)

ALL_HEADINGS = frozenset({
    "Chapter I - Preliminary", "Chapter II - Reporting",
    "Chapter III - Netting", "Chapter IV - Citation",
})
CH2 = frozenset({"Chapter II - Reporting"})

# Every `shall` sentence in the WHOLE instrument, counted by hand from `_UNITS`: u030, u050,
# both sentences of u060, u070, u080, u110. `marshalling` in u090 is not one of them.
WHOLE_DOCUMENT_SHALL_SENTENCES = 7


def _party(name: str, *, external: bool = False, overrides: dict[str, str] | None = None):
    o = overrides or {}
    return Extraction(
        extractor=name, version="test", external=external,
        units=tuple(Unit(key=k, text=o.get(k, t), page=p) for k, t, p in _UNITS),
        blind_to={},
    )


def _statute(**overrides: str):
    """The instrument as two independent extractions that AGREE. `build` requires two."""
    return build("syn-statute", [
        _party("reader_ext", external=True, overrides=overrides),
        _party("reader_own", overrides=overrides),
    ])


# --- the boundary rule -------------------------------------------------------------------------


def test_enumerate__shall_inside_a_longer_word_is_not_an_obligation() -> None:
    """`marshalling` is the fixture because it appears in financial regulation and an invented one
    would not have caught it.

    A substring match here inflates the pool with sentences that carry no obligation at all, and
    the inflation is invisible downstream: `k of 20` is then computed over clauses the model was
    right to say nothing about.
    """
    assert not any(is_obligation_token_at("marshalling", i) for i in range(len("marshalling")))
    assert not any(is_obligation_token_at("shallow", i) for i in range(len("shallow")))
    assert not any(is_obligation_token_at("marshall", i) for i in range(len("marshall")))
    # The admission side of the same rule: a bare token IS one, or the check above is satisfied by
    # a function that always returns False.
    assert is_obligation_token_at("the fme shall file", 8)

    src = _statute()
    assert "marshalling" in src.text  # the word really is inside the sampled chapter
    pool = enumerate_shall(src, chapters=CH2, all_headings=ALL_HEADINGS)
    assert all("marshalling" not in o.quote for o in pool.obligations)


# --- the two refusals that move the denominator --------------------------------------------------


def test_enumerate__a_chapter_title_that_does_not_match_exactly_raises() -> None:
    """An em dash where the pre-registration typed a hyphen — the near-miss that actually happens
    when a chapter list is retyped out of a PDF.

    Both spellings are declared as headings here, so nothing reads as undeclared and the only thing
    left to test is the match itself: the sampled hyphen title does NOT fall back onto its em-dash
    sibling. A fuzzy match would silently sample a chapter nobody registered; no match at all, if it
    returned the obligations it did find, would silently shrink the denominator.
    """
    em = "Chapter II — Reporting"      # U+2014 in the instrument
    hyphen = "Chapter II - Reporting"       # U+002D in the pre-registered chapter list
    src = _statute(u040=em)

    with pytest.raises(ChapterNotFound) as e:
        enumerate_shall(
            src,
            chapters=frozenset({hyphen}),
            all_headings=ALL_HEADINGS | {em},
        )
    assert hyphen in str(e.value)
    assert "no fuzzy chapter match" in str(e.value)

    # And the em-dash spelling, sampled as written, does enumerate — so the refusal above is about
    # the comparison and not about a chapter that vanished from the instrument.
    assert enumerate_shall(src, chapters=frozenset({em}),
                           all_headings=ALL_HEADINGS | {em}).obligations


def test_enumerate__an_undeclared_heading_is_refused_not_absorbed() -> None:
    """A named chapter runs to the NEXT HEADING, so a heading nobody declared is absorbed into the
    chapter above it and every obligation below it enters the pool.

    That is denominator INFLATION — the mirror of the truncation NC-M03 guards — and it is the
    direction nobody questions, because a pool that grew looks like an instrument that had more in
    it. The enumerator names the heading instead of guessing.
    """
    src = _statute()
    with pytest.raises(UndeclaredHeading) as e:
        enumerate_shall(
            src, chapters=CH2,
            all_headings=frozenset({"Chapter I - Preliminary", "Chapter II - Reporting"}),
        )
    assert "Chapter III - Netting" in str(e.value)

    # Declared, the boundary holds: Chapter II stops at Chapter III and the pool is a PROPER subset
    # of the instrument's `shall` sentences. Equality here would mean the whole document was
    # absorbed into one chapter.
    pool = enumerate_shall(src, chapters=CH2, all_headings=ALL_HEADINGS)
    assert 0 < len(pool.obligations) < WHOLE_DOCUMENT_SHALL_SENTENCES
    assert all("net the exposures" not in o.quote for o in pool.obligations)


# --- the admission side ------------------------------------------------------------------------


def test_enumerate__the_admission_side_a_correctly_declared_instrument_enumerates() -> None:
    """The positive control. Without it, every refusal in this file is satisfied by a function that
    always raises — and the ordering assertion is the one that has to be here, because the
    permutation is keyed on the ordinal and a wrong order is a DIFFERENT DRAW wearing the same seed.

    Lexical ordering would put 51 before 9 and (10) before (9); this is the arithmetic one.
    """
    src = _statute()
    pool = enumerate_shall(src, chapters=CH2, all_headings=ALL_HEADINGS)

    assert isinstance(pool, Pool)
    assert [(o.reg_no, o.sub_clause) for o in pool.obligations] == [
        (9, ("1",)), (51, ("1",)), (51, ("2",)), (51, ("9",)), (51, ("10",)),
    ]
    # (9) precedes (10) in the pool but FOLLOWS it in the document, so the order is the parsed
    # citation and not insertion order.
    nine = next(o for o in pool.obligations if o.sub_clause == ("9",))
    ten = next(o for o in pool.obligations if o.sub_clause == ("10",))
    assert nine.ordinal < ten.ordinal and nine.char_span[0] > ten.char_span[0]

    assert [o.ordinal for o in pool.obligations] == list(range(len(pool.obligations)))
    assert all("shall" in o.quote for o in pool.obligations)
    assert all(o.source_sha256 == src.sha256 for o in pool.obligations)
    assert pool.source_sha256 == src.sha256
    assert pool.chapters == ("Chapter II - Reporting",)
    assert pool.excluded == ()


# --- sentence splitting ------------------------------------------------------------------------


def test_enumerate__a_clause_numeral_does_not_end_a_sentence() -> None:
    """`51. (1) The FME shall …` split at the clause number in the first version, so every quote
    parsed to `reg_no = 0` and the canonical ordering — which is keyed on the ordinal — silently
    became insertion order. A draw over that pool is a different draw with the same seed.

    The rule is narrow ON PURPOSE, and the second half of this test is what holds it narrow: a
    trailing year still ends a sentence, because a splitter that swallowed every full stop after a
    digit would glue whole regulations into one quote and shrink the pool.
    """
    one = "51. (1) The FME shall x."
    assert sentences(one) == ((0, len(one) - 1),)
    assert parse_citation(one) == (51, ("1",))

    two = "53. (1) The report shall be audited in 2025. The FME shall publish it."
    assert [two[a:b] for a, b in sentences(two)] == [
        "53. (1) The report shall be audited in 2025",
        "The FME shall publish it",
    ]
    assert parse_citation(two[slice(*sentences(two)[1])]) == (0, ())

    # End to end: the clause numeral survives enumeration, not just `sentences`.
    pool = enumerate_shall(_statute(), chapters=CH2, all_headings=ALL_HEADINGS)
    assert 0 not in {o.reg_no for o in pool.obligations}


def test_enumerate__sub_clauses_parse_into_components() -> None:
    """`52. (2)(a)` parsed into `("2", "a")`, not consumed and dropped.

    The first version returned `(52, ())` for every sub-clause, so `51.(10)` and `51.(9)` compared
    EQUAL and the canonical ordering degenerated to span order inside a regulation — a pool that
    looks correctly ordered and is not.
    """
    assert parse_citation("52. (2)(a) x") == (52, ("2", "a"))
    assert parse_citation("51.(1)(a)(i)") == (51, ("1", "a", "i"))
    assert parse_citation("The FME shall publish it") == (0, ())

    # The components are then ordered ARITHMETICALLY. Lexically `("9",) > ("10",)`, which is the
    # comparison this key exists to replace.
    assert _sub_clause_key(("9",)) < _sub_clause_key(("10",))
    assert ("9",) > ("10",)
    assert _sub_clause_key(("2",)) < _sub_clause_key(("a",))  # a numeral before a letter


def test_enumerate__spans_are_exact_and_trimmed() -> None:
    """`source.text[span] == quote`, and the quote carries no leading space.

    A span that included the space before its sentence still LOCATES under `find`, so G0 would pass
    on it and the only symptom would be a verbatim quote nobody could paste back — the shape of
    every off-by-one that survives review. `u060` puts three spaces before its second sentence so
    the trim is measured rather than assumed.
    """
    src = _statute()
    pool = enumerate_shall(src, chapters=ALL_HEADINGS, all_headings=ALL_HEADINGS)
    assert len(pool.obligations) == WHOLE_DOCUMENT_SHALL_SENTENCES

    for o in pool.obligations:
        lo, hi = o.char_span
        assert src.text[lo:hi] == o.quote
        assert o.quote == o.quote.strip()
        assert o.char_span in src.find_all(o.quote)

    indexed = next(o for o in pool.obligations if o.quote.endswith("index them"))
    assert indexed.quote.startswith("51. (2)")
    assert src.text[indexed.char_span[0] - 1] == " "  # the run of spaces is OUTSIDE the span


@settings(max_examples=300, deadline=None)
@given(st.text(alphabet=".;\n \t5aZ", max_size=60))
@example("51. (1) The FME shall retain them.   51. (2) The FME shall index them.")
@example("53. (1) audited in 2025. The FME shall publish it.")
@example("   ")
def test_enumerate__every_sentence_span_is_non_empty_and_stripped(text: str) -> None:
    """The same trim invariant, over generated text rather than the fixture.

    The two `@example`s are the defects the module's own comments record: the clause numeral that
    split a citation off its sentence, and the leading whitespace that stayed inside the span.
    """
    for a, b in sentences(text):
        assert b > a
        assert text[a:b] == text[a:b].strip()


# --- exclusion ---------------------------------------------------------------------------------


def test_enumerate__a_disputed_region_excludes_and_counts() -> None:
    """An obligation the extractions disagree over leaves the pool WITH its reason and its page.

    Never a silent drop: `excluded` is the third integer NC-M34 publishes beside `|A| / |drawn|`,
    because it is the size of OUR curation of the instrument. An obligation that merely disappeared
    would shrink the pool and report the shrinkage as nothing at all.
    """
    disputed_reg_no, disputed_page = 9, 2  # `u050`, and its chapter heading, are both on page 2

    src = _statute()
    baseline = enumerate_shall(src, chapters=CH2, all_headings=ALL_HEADINGS)
    target = next(o for o in baseline.obligations if o.reg_no == disputed_reg_no)

    # The disagreement is real: two extractions read `u050` differently and `build` derives the
    # region from that. `build` renders a disputed unit as a single U+FFFD sentinel, so the region
    # it returns spans the sentinel rather than the sentence it stands for; it is re-pointed at
    # that sentence here so the enumerator is asked the question the region was raised about.
    disagreeing = build("syn-statute", [
        _party("reader_ext", external=True),
        _party("reader_own", overrides={"u050": "9. (1) The FME shall file the returns."}),
    ])
    (region,) = disagreeing.disputed
    assert region.key == "u050" and set(region.readings) == {"reader_ext", "reader_own"}
    assert len(set(region.readings.values())) == len(region.readings)  # they really do differ

    source = replace(src, disputed=(replace(region, span=target.char_span),))
    pool = enumerate_shall(source, chapters=CH2, all_headings=ALL_HEADINGS)

    assert all(o.quote != target.quote for o in pool.obligations)
    assert len(pool.obligations) == len(baseline.obligations) - 1

    (excluded,) = pool.excluded
    assert excluded.quote == target.quote
    assert excluded.char_span == target.char_span
    assert "disagree" in excluded.reason
    assert excluded.page == disputed_page
    assert pool.excluded_pages() == (disputed_page,)


# --- what is not a statute ---------------------------------------------------------------------


def test_enumerate__a_template_instrument_is_refused() -> None:
    """A TEMPLATE workbook enumerated for `shall` yields a pool of spreadsheet labels called a
    regulation, and an empty pool would be indistinguishable from a statute with no obligations.

    Two different facts, two different remedies — collapsing them is this project's own subject
    matter, so the refusal names which one it is.
    """

    class _Template:
        kind = "TEMPLATE"
        text = "Total assets shall be reported in thousands."
        units = ()
        disputed = ()
        sha256 = "0" * 64

        def is_disputed(self, span: tuple[int, int]) -> bool:
            return False

    with pytest.raises(NotAStatute) as e:
        enumerate_shall(_Template(), chapters=frozenset())
    assert "not STATUTE" in str(e.value)

    class _NotAnInstrument:
        pass

    with pytest.raises(NotAStatute) as e:
        enumerate_shall(_NotAnInstrument(), chapters=frozenset())
    assert "is not an InstrumentText" in str(e.value)


# --- the pool hash -----------------------------------------------------------------------------


def test_enumerate__the_pool_hash_changes_when_the_chapter_set_changes() -> None:
    """`Pool.sha256` covers the chapters, so a re-curated chapter list is a DIFFERENT POOL and
    cannot silently reuse a draw taken over the old one.

    The chapter added here carries no obligation, so the two pools are identical in every other
    field. That is the sharp case: if the chapters were outside the digest, a curation change that
    happened to add nothing would keep the hash, `extend()`'s pool check would pass, and the
    permutation — which is keyed on the pool hash — would go on addressing the old scope.
    """
    src = _statute()
    narrow = enumerate_shall(src, chapters=CH2, all_headings=ALL_HEADINGS)
    wider = enumerate_shall(
        src, chapters=CH2 | {"Chapter IV - Citation"}, all_headings=ALL_HEADINGS,
    )

    assert wider.obligations == narrow.obligations
    assert wider.excluded == narrow.excluded
    assert wider.source_sha256 == narrow.source_sha256
    assert wider.chapters != narrow.chapters
    assert wider.sha256 != narrow.sha256
