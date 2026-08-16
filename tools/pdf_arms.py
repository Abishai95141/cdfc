#!/usr/bin/env python
"""S1 — the PDF extraction arms for a STATUTE instrument. **Build-time only.**

This module is deliberately NOT under `src/`. The pinned `<instrument>.text.json` is what the
system reads; the PDF libraries are needed to *produce* it and never to *use* it. Putting them in
`src/` would add three parsers to the runtime closure of a package whose whole claim is that its
verdict path is small and auditable.

## Why two parties and not three, when three were measured

`textsource.build()` implements **unanimity** — `len(distinct) == 1` or the unit is `DISPUTED`.
There is no majority rule and this build did not add one: weakening *"every competent party
agrees"* to *"most agree"* across the whole system, including the nine TEMPLATE instruments whose
numbers are already published, to rescue one instrument is the wrong trade.

**Four** arms were run and **all four are published** in
`docs/measurements/S1-instrument-agreement.md`. The shipped parties are **pdfplumber**
(pdfminer.six, pure Python) and **pypdfium2** (PDFium, Google's C++ engine — the one in Chrome).
Two are measured and are not parties, for two different reasons:

**`pymupdf` — excluded on its LICENCE, and it is the arm that scored best.** It agreed with
pdfplumber on 1,217 of 1,219 units, against the shipped pair's 1,189 of 1,218, so dropping it cost
27 units of real accuracy. It is `Dual Licensed - GNU AFFERO GPL 3.0 or Artifex commercial`, and
`AGPL-3.0` is on this repository's own denylist in `ci/licence-denylist.sh` — a gate that resolves
the RUNTIME set and therefore never sees a build-time tool. **A denylisted licence entering through
a door the gate does not watch** is this project's subject matter happening to this project. The
arm was dropped, `ci/no-denied-build-tool.sh` was written, and the cost is published rather than
absorbed.

**`pypdf` — excluded on a ground taken from the artifact rather than from the score:**

* The instrument's fonts carry **zero `/ToUnicode` CMaps** (measured on the bytes). `pypdf`'s
  `extract_text()` reconstructs word boundaries from glyph advance widths, and without a
  `/ToUnicode` map it has no text-level check on that reconstruction.
* The realised consequence is spurious **intra-word** spaces, 2–7 per page — which whitespace
  collapsing cannot repair, because the space is inside the word rather than between words.
* The corroborating evidence that this is `pypdf`'s defect rather than a genuine ambiguity in the
  text is the SHAPE of the disagreement: the three other arms agree with each other and `pypdf`
  disagrees with all of them, at roughly 1,060 of 1,219 against each. Three independent readings of
  an ambiguous text scatter three ways; these went three against one.

A configuration is not made true by being measured second, and not made false by being excluded.

## Both parties are EXTERNAL, which is stronger than the template arm

For the nine workbooks one party was `openpyxl` and the other was ours. Here neither party was
written in this repository, so `agreement_external` covers every unit and `agreement_same_author`
is empty. That is the one respect in which this instrument rests on better evidence than the
templates do.

## The running header, and why it is not a threshold

The Gazette prints a running header whose language alternates with page parity, independently of
the language of the content: even pages carry `142 THE GAZETTE OF INDIA : EXTRAORDINARY
[PART III—SEC.4]` and odd pages the Devanagari form. So page 142 is Hindi content under an English
header, and page 143 is English content under a Devanagari one.

The first version of this rule classified pages by the *fraction* of Devanagari characters and set
the boundary where that fraction fell below 1 in 100. It returned page **184** instead of 143,
because page 183 carries the 27-character header against 2,636 Latin characters — 27 of 2,663, a
hair over
the line — and one page moved the boundary by forty. A threshold over a ratio whose numerator is a
constant is a threshold over the denominator, which here is just how much text happened to fit on
the page.

So: **strip the header, then classify on a zero.** A page is English when its remaining Devanagari
count is exactly 0 and it has Latin characters. No fraction, nothing to tune.

## The Hindi region is EXCLUDED and COUNTED

Pages 1–142 are the Hindi text of the same instrument. They are not units: `enumerate_shall` would
find no `shall` in them and the pool would have been built from the English pages alone **by
accident**, with nothing recording that a decision had been taken. The exclusion is declared here,
its page count and character count are published, and `S1_EXCLUSION` is what the pre-registration
lock's `exclusion_rule_sha256` covers.
"""

from __future__ import annotations

import hashlib
import pathlib
import sys
import unicodedata
from dataclasses import dataclass
from typing import Final

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.enumerate_shall import sentences  # noqa: E402
from cdfc.qualify.textsource import Extraction, Unit, normalise  # noqa: E402

# Devanagari, as a closed range. `unicodedata.name` would also work and would be slower and no
# clearer; the block boundaries are stable and this is checked by test_pdf_arms__devanagari_range.
DEVANAGARI: Final[tuple[str, str]] = ("ऀ", "ॿ")

# The two forms of the running header. Matched on the Gazette's own invariant words rather than on
# the whole line, because the line carries the page number and therefore differs on every page.
HEADER_MARKERS_LATIN: Final[tuple[str, ...]] = ("THE GAZETTE OF INDIA", "EXTRAORDINARY")
DEVANAGARI_HEADER_OPENER: Final[str] = "[भाग"
DEVANAGARI_HEADER_TAIL: Final[str] = "असाधारण"

S1_EXCLUSION: Final[str] = (
    "Pages 1-142 are the Hindi text of the same instrument and are excluded from the unit set. "
    "They are counted, never dropped: the English half alone would have produced an identical "
    "pool with nothing recording that a choice had been made. A page is English when, after the "
    "running header is removed, it carries zero Devanagari characters and at least one Latin "
    "letter -- a zero, not a fraction, because the header is a constant numerator and a ratio "
    "over it is a ratio over how much text fitted on the page."
)


def is_devanagari(ch: str) -> bool:
    return DEVANAGARI[0] <= ch <= DEVANAGARI[1]


def page_body(page_text: str, page: int) -> str:
    """The page's content, normalised, with the running header removed. **Arm-independent.**

    The header is stripped from the NORMALISED text as a prefix, never by line index. The first
    version dropped line 0 and it was wrong in a way only a second reader could show: `pdfplumber`
    emits the header as one line, `pymupdf` splits it across two, so line-0 removal left half the
    header behind on every odd page and 27 of the 54 English pages classified as Devanagari. The
    guard in `pin_statute.py` — *the parties must agree on which pages are English* — caught it
    before a single unit was written.

    `normalise()` collapses exactly the line structure the two parties disagree about, so after it
    the header is a prefix in both readings and the strip is a property of the text rather than of
    the reader.

    **The page's own ordinal is required to match.** The header carries it, and demanding it means
    a body sentence quoting the instrument's own publication details cannot be mistaken for
    furniture — the failure the line-index version was trying to avoid, kept.
    """
    t = normalise(page_text)

    # Devanagari form: `[भाग III—खण्ड 4] भारत<ZWJ>का<ZWJ>राजपत्र<ZWJ>:<ZWJ>असाधारण <page>`.
    # The words are joined by U+200D, which NFKC does not remove, so the search is on the one
    # token that survives contiguously rather than on the phrase.
    if t.startswith(DEVANAGARI_HEADER_OPENER):
        i = t.find(DEVANAGARI_HEADER_TAIL)
        if i != -1:
            j = t.find(str(page), i)
            if j != -1:
                return t[j + len(str(page)):].lstrip()

    # Latin form: `<page> THE GAZETTE OF INDIA : EXTRAORDINARY [PART III—SEC.4]`.
    if t.startswith(f"{page} ") and all(m in t[:120] for m in HEADER_MARKERS_LATIN):
        k = t.find("]", 0, 200)
        if k != -1:
            return t[k + 1:].lstrip()

    return t


def classify_page(page_text: str, page: int) -> str:
    """`ENGLISH` | `DEVANAGARI` | `EMPTY`. Computed on a zero, with the header already gone."""
    body = page_body(page_text, page)
    dev = sum(1 for c in body if is_devanagari(c))
    lat = sum(1 for c in body if c.isascii() and c.isalpha())
    if dev == 0 and lat > 0:
        return "ENGLISH"
    if dev > 0:
        return "DEVANAGARI"
    return "EMPTY"


@dataclass(frozen=True, slots=True)
class PageRead:
    """One party's reading of one page, before segmentation."""

    page: int  # 1-based
    text: str


def english_pages(pages: list[str]) -> tuple[int, ...]:
    """The 1-based ordinals of the English pages. **Computed, never a constant.**"""
    return tuple(i + 1 for i, t in enumerate(pages) if classify_page(t, i + 1) == "ENGLISH")


def units_of(pages: list[str], english: tuple[int, ...]) -> tuple[Unit, ...]:
    """Segment each English page into sentence units with `p{page}.s{ordinal}` keys.

    The key sorts lexicographically into document order, which is `Unit`'s contract, and the
    ordinal is zero-padded to four digits so page 10 does not sort before page 9.

    **The segmenter is `cdfc.experiment.enumerate_shall.sentences`, imported rather than
    reimplemented.** There is one sentence rule in this system. If the build used a second one,
    a unit boundary and an obligation boundary could disagree and a `shall` could straddle two
    units -- an obligation the pool contains and no span can address.
    """
    out: list[Unit] = []
    for page in english:
        body = page_body(pages[page - 1], page)
        for ordinal, (lo, hi) in enumerate(sentences(body)):
            text = body[lo:hi]
            if text:
                out.append(Unit(key=f"p{page:04d}.s{ordinal:04d}", text=text, page=page))
    return tuple(out)


# --- the parties ------------------------------------------------------------------------


def read_pdfplumber(path: pathlib.Path) -> tuple[list[str], str]:
    import pdfplumber

    with pdfplumber.open(path) as doc:
        return [p.extract_text() or "" for p in doc.pages], _version("pdfplumber")


def read_pypdfium2(path: pathlib.Path) -> tuple[list[str], str]:
    """PDFium — Google's PDF engine, the one in Chrome. BSD-3-Clause / Apache-2.0.

    Independent of `pdfminer.six` in every sense that matters: a different language, a different
    organisation, and a rendering-derived text model rather than a content-stream one.
    """
    import pypdfium2

    doc = pypdfium2.PdfDocument(str(path))
    try:
        return [doc[i].get_textpage().get_text_bounded() or "" for i in range(len(doc))], _version(
            "pypdfium2"
        )
    finally:
        doc.close()


def read_pymupdf(path: pathlib.Path) -> tuple[list[str], str]:
    """MEASURED, NOT A PARTY — **licence, not score.**

    PyMuPDF is `Dual Licensed - GNU AFFERO GPL 3.0 or Artifex commercial`, and `AGPL-3.0` is on
    this repository's own denylist in `ci/licence-denylist.sh`. That gate scopes to the RUNTIME
    set, so it would not have fired on a build-time tool — **a denylisted licence entering through
    a door the gate does not watch**, which is this project's own subject matter happening to it.
    The gate is extended rather than the exception taken.

    It is read here so its numbers stay reproducible and its exclusion stays falsifiable. Reading
    an AGPL tool to produce a measurement distributes nothing; depending on it would.
    """
    import pymupdf

    with pymupdf.open(path) as doc:
        return [p.get_text() or "" for p in doc], _version("pymupdf")


def read_pypdf(path: pathlib.Path) -> tuple[list[str], str]:
    """MEASURED, NOT A PARTY. Kept so the exclusion argument stays reproducible."""
    import pypdf

    return [p.extract_text() or "" for p in pypdf.PdfReader(str(path)).pages], _version("pypdf")


def _version(dist: str) -> str:
    from importlib.metadata import version

    return version(dist)


def extraction_of(name: str, path: pathlib.Path) -> tuple[Extraction, tuple[int, ...], list[str]]:
    """One party's `Extraction`, its English page ordinals, and its raw page reads."""
    reader = {
        "pdfplumber": read_pdfplumber,
        "pypdfium2": read_pypdfium2,
        "pymupdf": read_pymupdf,
        "pypdf": read_pypdf,
    }[name]
    pages, ver = reader(path)
    english = english_pages(pages)
    units = units_of(pages, english)
    return (
        Extraction(
            extractor=name,
            version=ver,
            # Neither party was written in this repository. Unlike the template arm, where one
            # side was ours, every unit here is corroborated by two outside readers.
            external=True,
            units=units,
            blind_to={},
        ),
        english,
        pages,
    )


def declare_asymmetry(extractions: list[Extraction]) -> list[Extraction]:
    """Fill each party's `blind_to` for keys another party produced and it did not.

    **This is not an excuse and it does not launder anything.** `build()` refuses an unexplained
    absence, because a party that silently dropped a construct must not be indistinguishable from
    one that declared it cannot see the construct. The absences here are real and have one cause:
    the two parties read the same page into a different number of sentences under the shared
    segmenter, so the higher ordinals exist in one reading only.

    The unit that results is `SINGLE_PARTY` — **addressable and labelled**, strictly weaker than
    `AGREED`, and counted separately in `counts()`. Nothing is promoted. The alternative was a
    build that fails outright, which would leave no instrument at all rather than an instrument
    that says which of its sentences only one reader saw.
    """
    tables = {e.extractor: e.by_key() for e in extractions}
    universe = {k for t in tables.values() for k in t}
    out: list[Extraction] = []
    for e in extractions:
        mine = set(tables[e.extractor])
        blind = {}
        for key in sorted(universe - mine):
            page = int(key.split(".")[0][1:])
            others = sorted(n for n, t in tables.items() if key in t and n != e.extractor)
            blind[key] = (
                f"{e.extractor} reads page {page} into {sum(1 for k in mine if k.startswith(key.split('.')[0]))} "
                f"sentence unit(s) under the shared segmenter; this ordinal exists only in the "
                f"reading(s) of {', '.join(others)}. The unit is SINGLE_PARTY and uncorroborated."
            )
        out.append(
            Extraction(
                extractor=e.extractor, version=e.version, external=e.external,
                units=e.units, blind_to=blind,
            )
        )
    return out


def sha256_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
