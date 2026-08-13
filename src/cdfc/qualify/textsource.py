"""P7-B0 — the instrument text source: an addressable text with stable offsets.

**Why this exists and why it moved here.** G0's entire mechanism is `source_text.find(quote)` at an
exact character span. That requires an authoritative normalised text with stable offsets, and the
plan specified one five phases downstream of its only consumer (F35). **A span nobody can re-derive
is not evidence**, so the text a span points into is produced here, by a dual-extraction agreement
harness with a disputed-region exclusion rule — the D5 differential.

**The rule.** Two or more INDEPENDENT extractions of one artifact; normalise both with a recorded
transformation list; align them unit-wise on a key neither party chooses; **a unit the competent
parties disagree on is EXCLUDED from the addressable text** and published with its location. A
quote landing in an excluded region is `g0.quote_in_disputed_region` — a closed, named G0 reason,
never a silent failure to locate.

**D-P7-02 — three corroboration states, not two, and the reason is P1's competence matrix.**
The plan wrote the rule as *agree or disputed*. On a real artifact there is a third case and
collapsing it is lossy in both directions. `reader_openpyxl` is **namespace-blind to the `x14`
data-validation extension** and returns an object rather than a string for an array formula — both
exclusions measured on all nine workbooks at P1, not asserted. If a unit only one competent party
produced were treated as agreed, an uncorroborated reading would be indistinguishable from a
corroborated one; if it were treated as disputed, 19 `x14` validations would leave the addressable
text and take their predicates with them, **for a disagreement nobody observed.** So every unit
carries `AGREED | SINGLE_PARTY | DISPUTED`, all three counts are published, and a G0 outcome
records the corroboration of the unit it located in. Nothing is silently upgraded and nothing is
silently lost.

**Independence is a label on the number, never an assumption inside it.** `ingest/agreement.py`
already refuses to average an external check with a same-author one, and the same rule holds here:
`InstrumentText.agreement()` returns TWO vectors — one over units where a party nobody here wrote
was competent, one over units checked only by two implementations from this repository — and
`n/d` renders with its `EXTERNAL` or `SAME-AUTHOR` label on every surface.

**U+FFFD is an extraction failure, not a character.** A replacement character in a party's output
means that party already lost information at the byte level. It raises rather than becoming
addressable text, and the sentinel this module writes over a disputed region is the only U+FFFD in
an `InstrumentText`.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from cdfc.canon import digest

# The one character a disputed region is rendered as. It occupies a span, so any quote span
# intersecting it can be refused with a reason rather than silently sliced.
DISPUTED_SENTINEL: Final[str] = "�"

# The join between units. A single LF, always: a text whose offsets move with the platform is not
# an addressable text.
UNIT_SEP: Final[str] = "\n"


class TextSourceError(RuntimeError):
    """The text source cannot be built. Never repaired, never defaulted."""


class SpanOutOfRangeError(LookupError):
    """The span is not inside this instrument. A different failure from a disputed region, and
    they are kept apart because the remedies differ: one is a wrong offset, the other is a text
    that has no authoritative reading there."""


class DisputedRegionError(LookupError):
    """A span intersects a region the competent parties disagree on.

    G0 turns this into `g0.quote_in_disputed_region`. It is raised rather than returned so that a
    caller cannot reach the text by ignoring a return value.
    """

    def __init__(self, span: tuple[int, int], regions: Sequence[DisputedRegion]) -> None:
        keys = ", ".join(r.key for r in regions)
        super().__init__(
            f"span {span} intersects {len(regions)} disputed region(s) [{keys}]. The extractions "
            "of this instrument disagree there, so no party's reading is authoritative and the "
            "text is not addressable. Re-quote from an agreed region, or record that this "
            "obligation is not addressable."
        )
        self.span = span
        self.regions = tuple(regions)


class Corroboration(StrEnum):
    AGREED = "AGREED"  # two or more competent parties produced the same text
    SINGLE_PARTY = "SINGLE_PARTY"  # exactly one competent party; addressable, and labelled
    DISPUTED = "DISPUTED"  # competent parties differ; NOT addressable


class Independence(StrEnum):
    EXTERNAL = "EXTERNAL"  # a party nobody in this repository wrote was competent here
    SAME_AUTHOR = "SAME_AUTHOR"  # every competent party was written in this repository
    NONE = "NONE"  # one competent party; nothing was corroborated


# --- normalisation ---------------------------------------------------------------------
#
# The list is ORDERED, NAMED, and inside the instrument digest. A build that changes how text is
# normalised changes the instrument's identity, which is what stops a span silently re-pointing.
#
# What is deliberately NOT done is recorded beside what is, because a normalisation that quietly
# unified dashes would make `test_g0__verbatim_quote_required` unfailable: the homoglyph it plants
# is exactly a hyphen-minus swapped for a non-breaking hyphen.

TRANSFORMATIONS: Final[tuple[tuple[str, str], ...]] = (
    ("strip_soft_hyphen", "U+00AD is a line-break hint inserted by a typesetter, never a character "
                          "of the instrument; leaving it in makes a quote fail to locate for a "
                          "reason no reader can see"),
    ("nfkc", "Unicode NFKC. Expands the ligatures a PDF text layer emits (U+FB01 -> 'fi') and "
             "folds compatibility forms, so two extractions that differ only in encoding agree"),
    ("collapse_whitespace", "every run of Unicode whitespace becomes one U+0020 and the ends are "
                            "stripped; column and line geometry is a property of the rendering, "
                            "not of the text"),
)

REFUSED_TRANSFORMATIONS: Final[tuple[tuple[str, str], ...]] = (
    ("unify_dashes", "U+2010, U+2011, U+2013 and U+002D stay distinct. Folding them would make a "
                     "homoglyph substitution unlocatable BY THE GATE THAT EXISTS TO CATCH IT"),
    ("case_fold", "an identifier's case is part of it; folding would make two different cell "
                  "references one unit"),
    ("unify_quotes", "U+2018/U+2019 and U+201C/U+201D stay distinct from U+0027 and U+0022 for "
                     "the same reason as the dashes"),
)


def normalise(text: str) -> str:
    """Apply `TRANSFORMATIONS`, in order. Pure, and the only normaliser in the system."""
    if DISPUTED_SENTINEL in text:
        raise TextSourceError(
            "the text carries U+FFFD, which means the extraction already lost information at the "
            "byte level. A replacement character is an extraction failure, not a character, and "
            "it is also the sentinel this module writes over a disputed region — admitting it "
            "would make a real loss indistinguishable from a declared one."
        )
    text = text.replace("­", "")
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())


# --- the parties -----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Unit:
    """One comparable region of an instrument, with the identity the parties are aligned on.

    `key` is chosen by the extraction so that **lexicographic order is document order**. The
    addressable text is assembled in `sorted(key)` order and therefore does not depend on which
    party is passed first — a text whose byte layout moved with argument order would make every
    span a function of the caller.
    """

    key: str
    text: str
    page: int

    def __post_init__(self) -> None:
        if not self.key:
            raise TextSourceError("a unit with no key cannot be aligned against another party")
        if isinstance(self.page, bool) or not isinstance(self.page, int) or self.page < 1:
            raise TextSourceError(f"{self.key!r}: page is a 1-based ordinal, got {self.page!r}")


@dataclass(frozen=True, slots=True)
class Extraction:
    """One party's reading of one artifact.

    **`blind_to` is the whole discipline of this class.** A party that produced no unit at some key
    is in one of two states, and they are not the same fact: *"I cannot see this construct, and
    here is the mechanism"* is an exclusion; *"I saw nothing"* with no mechanism is a MISS. P1's
    competence matrix made that distinction for counts and required every exclusion to be
    `measured_on` a named workbook rather than believed. `build()` enforces the same thing here,
    and harder: **every absence must be covered by a named mechanism, and a mechanism may not be
    claimed for a key the party did produce.** An unexplained absence fails the build, because an
    absence read as agreement is this project's own subject matter.
    """

    extractor: str
    version: str
    external: bool
    units: tuple[Unit, ...]
    blind_to: Mapping[str, str]  # key -> the mechanism, in prose

    def __post_init__(self) -> None:
        if not self.extractor or not self.version:
            raise TextSourceError("an extraction names its extractor and its version")
        keys = [u.key for u in self.units]
        if len(set(keys)) != len(keys):
            dupes = sorted({k for k in keys if keys.count(k) > 1})
            raise TextSourceError(f"{self.extractor}: duplicate unit key(s) {dupes}")
        claimed = sorted(set(self.blind_to) & set(keys))
        if claimed:
            raise TextSourceError(
                f"{self.extractor}: claims blindness at {len(claimed)} key(s) it produced a "
                f"reading for, e.g. {claimed[:3]}. A party cannot both read a construct and "
                "excuse itself from being compared on it."
            )
        blank = sorted(k for k, why in self.blind_to.items() if not (why or "").strip())
        if blank:
            raise TextSourceError(
                f"{self.extractor}: {len(blank)} blindness declaration(s) carry no mechanism, "
                f"e.g. {blank[:3]}. An exclusion nobody can read is an exclusion nobody can check."
            )

    def by_key(self) -> Mapping[str, Unit]:
        return {u.key: u for u in self.units}

    def mechanisms(self) -> tuple[str, ...]:
        return tuple(sorted(set(self.blind_to.values())))


@dataclass(frozen=True, slots=True)
class ExtractionManifest:
    extractor: str
    version: str
    external: bool
    sha256: str
    n_units: int
    n_disputed: int
    n_blind: int
    exclusion_mechanisms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DisputedRegion:
    key: str
    page: int
    span: tuple[int, int]
    readings: Mapping[str, str]

    def render(self) -> str:
        parts = " | ".join(f"{p}: {t[:60]!r}" for p, t in sorted(self.readings.items()))
        return f"{self.key} (page {self.page}) -> {parts}"


@dataclass(frozen=True, slots=True)
class ResolvedUnit:
    key: str
    page: int
    span: tuple[int, int]
    corroboration: Corroboration
    parties: tuple[str, ...]  # the COMPETENT parties, whether or not they agreed
    external_party: bool  # was one of them written outside this repository?


@dataclass(frozen=True, slots=True)
class InstrumentText:
    """A normalised text, its offsets, and everything a reader needs to distrust it correctly."""

    instrument_id: str
    text: str
    units: tuple[ResolvedUnit, ...]
    disputed: tuple[DisputedRegion, ...]
    manifests: tuple[ExtractionManifest, ...]
    transformations: tuple[tuple[str, str], ...]
    refused_transformations: tuple[tuple[str, str], ...]
    sha256: str

    # --- addressing ---------------------------------------------------------------------

    def slice(self, span: tuple[int, int]) -> str:
        """The text at `span`, or `DisputedRegionError`. The ONLY way to read by offset."""
        lo, hi = span
        if not (0 <= lo <= hi <= len(self.text)):
            raise SpanOutOfRangeError(
                f"span {span} is outside the instrument's {len(self.text)} characters"
            )
        hit = [r for r in self.disputed if r.span[0] < hi and lo < r.span[1]]
        if hit:
            raise DisputedRegionError(span, hit)
        return self.text[lo:hi]

    def find_all(self, quote: str) -> tuple[tuple[int, int], ...]:
        """Every occurrence of `quote`, disputed regions included.

        Disputed occurrences are returned rather than filtered: G0 needs to distinguish *"the
        quote is nowhere"* from *"the quote is in a region we excluded"*, and a filter here would
        collapse two reasons with two different remedies into one.
        """
        out: list[tuple[int, int]] = []
        if not quote:
            return ()
        start = 0
        while (i := self.text.find(quote, start)) != -1:
            out.append((i, i + len(quote)))
            start = i + 1
        return tuple(out)

    def is_disputed(self, span: tuple[int, int]) -> bool:
        lo, hi = span
        return any(r.span[0] < hi and lo < r.span[1] for r in self.disputed)

    def unit_at(self, span: tuple[int, int]) -> ResolvedUnit | None:
        lo, hi = span
        for u in self.units:
            if u.span[0] <= lo and hi <= u.span[1]:
                return u
        return None

    # --- what a reader must be told ------------------------------------------------------

    def counts(self) -> Mapping[str, int]:
        """All four integers. `agreed` alone is a number with its denominator removed."""
        c = {k.value: 0 for k in Corroboration}
        for u in self.units:
            c[u.corroboration.value] += 1
        c["units_total"] = len(self.units)
        return c

    def agreement(self) -> Mapping[str, tuple[int, int]]:
        """TWO vectors, never one — `ingest/agreement.py`'s rule, applied to this instrument.

        A single figure would average a check against a library nobody here wrote with a check of
        two implementations by one author, and report the result as one instrument.
        """
        ext = [u for u in self.units if u.external_party and len(u.parties) > 1]
        same = [u for u in self.units if not u.external_party and len(u.parties) > 1]
        return {
            Independence.EXTERNAL.value: (
                sum(1 for u in ext if u.corroboration is Corroboration.AGREED), len(ext)
            ),
            Independence.SAME_AUTHOR.value: (
                sum(1 for u in same if u.corroboration is Corroboration.AGREED), len(same)
            ),
        }

    def addressable_fraction(self) -> tuple[int, int]:
        """(addressable units, total units). Ships beside every G0 figure — the plan's own risk."""
        return (
            sum(1 for u in self.units if u.corroboration is not Corroboration.DISPUTED),
            len(self.units),
        )


# --- the build -------------------------------------------------------------------------


def build(instrument_id: str, extractions: Sequence[Extraction]) -> InstrumentText:
    """Align, compare, exclude, and lay out. The one constructor of an `InstrumentText`."""
    if len(extractions) < 2:
        raise TextSourceError(
            f"{instrument_id}: {len(extractions)} extraction(s). An instrument built from one "
            "reading is that reading's opinion, and a span into it is unfalsifiable. This is "
            "NC-Q47's mechanism."
        )
    names = [e.extractor for e in extractions]
    if len(set(names)) != len(names):
        raise TextSourceError(f"{instrument_id}: two extractions share a name: {sorted(names)}")

    tables = {e.extractor: e.by_key() for e in extractions}
    # Order is `sorted(key)` and nothing else, so the layout does not depend on argument order.
    all_keys = sorted({k for t in tables.values() for k in t})
    universe = set(all_keys)

    # EVERY ABSENCE IS EXPLAINED OR THE BUILD FAILS. Without this the party that quietly dropped a
    # construct is indistinguishable from the party that declared it cannot see one — and the unit
    # would be labelled SINGLE_PARTY, which reads as "uncorroborated" rather than as "one reader
    # lost it". Those are different findings with different remedies.
    for e in extractions:
        missing = universe - set(tables[e.extractor])
        unexplained = sorted(missing - set(e.blind_to))
        if unexplained:
            raise TextSourceError(
                f"{e.extractor}: {len(unexplained)} key(s) another party read and this one "
                f"produced nothing for, with no declared mechanism, e.g. {unexplained[:3]}. "
                "An unexplained absence is a MISS, not an exclusion, and treating it as one "
                "would let a reader that silently dropped a construct look merely uncorroborated."
            )

    resolved: list[ResolvedUnit] = []
    disputed: list[DisputedRegion] = []
    rendered: list[str] = []
    disputed_per_party: dict[str, int] = {e.extractor: 0 for e in extractions}
    cursor = 0

    for key in all_keys:
        present = [e for e in extractions if key in tables[e.extractor]]
        readings = {e.extractor: tables[e.extractor][key].text for e in present}
        pages = {tables[e.extractor][key].page for e in present}
        page = min(pages)
        distinct = set(readings.values())

        if len(present) == 1:
            corro = Corroboration.SINGLE_PARTY
            body = next(iter(readings.values()))
        elif len(distinct) == 1:
            corro = Corroboration.AGREED
            body = next(iter(distinct))
        else:
            corro = Corroboration.DISPUTED
            body = DISPUTED_SENTINEL

        span = (cursor, cursor + len(body))
        rendered.append(body)
        cursor += len(body) + len(UNIT_SEP)
        resolved.append(
            ResolvedUnit(
                key=key,
                page=page,
                span=span,
                corroboration=corro,
                parties=tuple(sorted(readings)),
                external_party=any(e.external for e in present),
            )
        )
        if corro is Corroboration.DISPUTED:
            disputed.append(DisputedRegion(key=key, page=page, span=span, readings=dict(readings)))
            for name in readings:
                disputed_per_party[name] += 1

    text = UNIT_SEP.join(rendered)
    manifests = tuple(
        ExtractionManifest(
            extractor=e.extractor,
            version=e.version,
            external=e.external,
            sha256=digest([[u.key, u.page, u.text] for u in sorted(e.units, key=lambda u: u.key)]),
            n_units=len(e.units),
            n_disputed=disputed_per_party[e.extractor],
            n_blind=len(set(e.blind_to) & universe),
            exclusion_mechanisms=e.mechanisms(),
        )
        for e in sorted(extractions, key=lambda e: e.extractor)
    )
    payload = {
        "instrument_id": instrument_id,
        "transformations": [list(t) for t in TRANSFORMATIONS],
        "refused_transformations": [list(t) for t in REFUSED_TRANSFORMATIONS],
        "units": [
            [u.key, u.page, u.corroboration.value, list(u.parties), u.external_party, *u.span]
            for u in resolved
        ],
        "text": text,
        "manifests": [
            [m.extractor, m.version, m.external, m.sha256, m.n_units, m.n_disputed, m.n_blind,
             list(m.exclusion_mechanisms)]
            for m in manifests
        ],
    }
    return InstrumentText(
        instrument_id=instrument_id,
        text=text,
        units=tuple(resolved),
        disputed=tuple(disputed),
        manifests=manifests,
        transformations=TRANSFORMATIONS,
        refused_transformations=REFUSED_TRANSFORMATIONS,
        sha256=digest(payload),
    )
