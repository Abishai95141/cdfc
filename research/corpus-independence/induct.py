"""Division recovery by TEMPLATE INDUCTION. Prototype for the corpus-independence measurement.

## What was wrong with the version this replaces

`src/cdfc/qualify/provisions.py` enumerated six MARKER SHAPES as regexes — `DECIMAL_TRAILING`,
`PAREN_LETTER`, `ORDINAL_WORD` and so on — chosen by looking at one Gazette. Three separate
problems follow from that and none of them is fixable by adding a seventh regex:

  * an instrument writing `Article 5`, `§ 275.1`, `SEC. 11101.` or `Chapter IV` matches none of
    them, so it recovers nothing;
  * `ORDINAL_WORD` hard-codes twelve English words, so schedules are recoverable in English and
    nowhere else;
  * `(aa) (bb) (cc)` needed a hand-picked decoding convention, and the other convention — the
    spreadsheet one — is equally real and is right for other documents.

## The decomposition

    LAYER 1  NUMERAL SYSTEMS      DECLARED, and universal. How notation denotes an ordinal:
                                  arabic, roman, alphabetic, English ordinal words. These are
                                  properties of writing systems, not of any document.

    LAYER 2  TEMPLATE INDUCTION   OBSERVED. What surrounds a numeral in THIS document — the
                                  punctuation, the preceding word, whether it sits at a line's
                                  start or end. Nothing here is enumerated in code: the templates
                                  come out of the text.

    LAYER 3  THE CHAIN MACHINE    Unchanged and corpus-free. A division's numbering ascends across
                                  its region; a subdivision's restarts. Score each induced
                                  template by purity x coverage and let the document choose.

**Ambiguity is resolved by generate-and-score, never by a threshold.** Where the old code decided
that `(aa)` means 27 rather than 53, both decodings are now emitted as separate numeral systems and
the chain machine picks whichever actually forms a sequence in the document at hand. Where the old
code decided that a margin number is the top level, several candidate groupings of the same
occurrences are generated and scored. Nothing is chosen by a constant.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Callable, Final, Iterable

MAX_ORDINAL: Final[int] = 999_999_999
CONTEXT: Final[int] = 24          # chars of left context inspected around a numeral
MIN_CHAIN: Final[int] = 3         # a sequence needs three members; two is a coincidence
MAX_OCCURRENCES: Final[int] = 400_000


# --------------------------------------------------------------------------------------
# LAYER 1 — NUMERAL SYSTEMS. Declared, universal, and small.
# --------------------------------------------------------------------------------------

_ORDINAL_WORDS: Final[dict[str, int]] = {
    w: i + 1 for i, w in enumerate((
        "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth",
        "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth",
        "seventeenth", "eighteenth", "nineteenth", "twentieth",
    ))
}

_ROMAN_VALUES: Final[dict[str, int]] = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500,
                                        "m": 1000}


def _roman(tok: str) -> int | None:
    t = tok.lower()
    if not t or any(ch not in _ROMAN_VALUES for ch in t):
        return None
    total = prev = 0
    for ch in reversed(t):
        v = _ROMAN_VALUES[ch]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total if 0 < total <= MAX_ORDINAL else None


def _alpha_sequence(tok: str) -> int | None:
    """`a`..`z`, then the DOUBLED form `aa`=27, `bb`=28 — the legal-drafting continuation."""
    t = tok.lower()
    if not t or not all("a" <= c <= "z" for c in t):
        return None
    if len(t) == 1:
        return ord(t) - 96
    if len(set(t)) == 1:
        return 26 * (len(t) - 1) + (ord(t[0]) - 96)
    return None


def _alpha_base26(tok: str) -> int | None:
    """`a`..`z`, then `aa`=27, `ab`=28 — the spreadsheet-column continuation.

    BOTH conventions are real and each is right for some documents. The old code picked one by
    hand. Emitting both and letting the chain machine see which forms a sequence is the same
    generate-and-score discipline used everywhere else here.
    """
    t = tok.lower()
    if not t or not all("a" <= c <= "z" for c in t):
        return None
    n = 0
    for ch in t:
        n = n * 26 + (ord(ch) - 96)
    return n if n <= MAX_ORDINAL else None


@dataclass(frozen=True)
class NumeralSystem:
    name: str
    pattern: re.Pattern[str]
    decode: Callable[[str], int | None]
    note: str


def _multi_index(tok: str) -> int | None:
    """`1.1`, `2.10.3`, `275.206` -> a single ordinal that sorts like the tuple it denotes.

    DOTTED OUTLINE NUMBERING IS A NOTATION, NOT A CORPUS CONVENTION. RFCs, the CFR, ISO standards,
    W3C specifications and most technical prose use it, and a tokenizer that reads `1.1` as the
    two numerals `1` and `1` cannot see it at all — which is why the first measurement across ten
    corpora found the RFC section structure nowhere near the top on any of them.

    The components are packed base-10000 so that lexicographic order on the tuple is numeric order
    on the result, which is what the ascending-chain machine needs. Depth is capped at three
    because the packing must stay inside the ordinal domain.
    """
    parts = tok.split(".")
    if not 2 <= len(parts) <= 3 or not all(p.isdigit() and len(p) <= 3 for p in parts):
        return None
    n = 0
    for p in parts + ["0"] * (3 - len(parts)):
        n = n * 1000 + int(p)
    return n or None


NUMERAL_SYSTEMS: Final[tuple[NumeralSystem, ...]] = (
    NumeralSystem("MULTI_INDEX", re.compile(r"(?<![\d.])\d{1,3}(?:\.\d{1,3}){1,2}(?![\d.])"),
                  _multi_index,
                  "1.1, 2.10.3, 275.206 — dotted outline numbering, the notation every technical "
                  "standard and code of regulations uses"),
    NumeralSystem("ARABIC", re.compile(r"(?<![\d.])\d{1,4}(?![\d.])"),
                  lambda t: int(t) if int(t) else None,
                  "1, 2, 147 — every numbering system in the corpora uses it somewhere"),
    NumeralSystem("ROMAN_LOWER", re.compile(r"(?<![a-z])[ivxlcdm]{1,9}(?![a-z])"), _roman,
                  "i, iv, ix — sub-lists in statutes, and front matter in books"),
    NumeralSystem("ROMAN_UPPER", re.compile(r"(?<![A-Z])[IVXLCDM]{1,9}(?![A-Z])"), _roman,
                  "I, IV, IX — chapter and part numbering"),
    NumeralSystem("ALPHA_LOWER_SEQ", re.compile(r"(?<![a-z])[a-z]{1,3}(?![a-z])"), _alpha_sequence,
                  "a..z then aa=27 — the drafting continuation"),
    NumeralSystem("ALPHA_LOWER_B26", re.compile(r"(?<![a-z])[a-z]{1,3}(?![a-z])"), _alpha_base26,
                  "a..z then aa=27, ab=28 — the spreadsheet continuation"),
    NumeralSystem("ALPHA_UPPER_SEQ", re.compile(r"(?<![A-Z])[A-Z]{1,3}(?![A-Z])"), _alpha_sequence,
                  "A..Z then AA — the same, upper case"),
    NumeralSystem("ORDINAL_WORD_EN", re.compile(r"(?i)(?<![a-z])(?:" + "|".join(_ORDINAL_WORDS) +
                                                r")(?![a-z])"), lambda t: _ORDINAL_WORDS[t.lower()],
                  "First, SECOND — ENGLISH ONLY, and one system among several rather than a "
                  "special case in the recovery. A document not in English loses this and keeps "
                  "the rest."),
)


# --------------------------------------------------------------------------------------
# LAYER 2 — TEMPLATE INDUCTION. Observed from the document.
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Occurrence:
    offset: int          # where the DIVISION starts, not where the numeral is
    numeral_at: int
    token_len: int       # the TOKEN's length, which is not len(str(ordinal)) outside arabic
    ordinal: int
    system: str
    punct_before: str
    word_before: str
    punct_after: str
    word_after: str
    at_line_start: bool
    at_line_end: bool


_WORD_TAIL = re.compile(r"([A-Za-z][A-Za-z.'-]*)[^A-Za-z0-9]*$")
_WORD_HEAD = re.compile(r"^[^A-Za-z0-9]*([A-Za-z][A-Za-z.'-]*)")
_PUNCT_TAIL = re.compile(r"([^A-Za-z0-9]*)$")
_PUNCT_HEAD = re.compile(r"^([^A-Za-z0-9]*)")


def occurrences(text: str, systems: Iterable[NumeralSystem] = NUMERAL_SYSTEMS) -> list[Occurrence]:
    """Every numeral in the text, with the context a template is induced from.

    The context is deliberately shallow — the punctuation touching the numeral, and the one word
    before and after it. A deeper window would start memorising sentences.
    """
    out: list[Occurrence] = []
    line_start_at = _line_starts(text)
    for sysm in systems:
        for m in sysm.pattern.finditer(text):
            val = sysm.decode(m.group(0))
            if val is None or not (0 < val <= MAX_ORDINAL):
                continue
            ls = line_start_at(m.start())
            le = text.find("\n", m.end())
            le = len(text) if le == -1 else le
            left = text[max(ls, m.start() - CONTEXT):m.start()]
            right = text[m.end():min(le, m.end() + CONTEXT)]
            pb = _PUNCT_TAIL.search(left).group(1)
            pa = _PUNCT_HEAD.match(right).group(1)
            wb = (_WORD_TAIL.search(left).group(1) if _WORD_TAIL.search(left) else "")
            wa = (_WORD_HEAD.match(right).group(1) if _WORD_HEAD.match(right) else "")
            at_start = (m.start() - len(pb)) <= ls
            at_end = m.end() + len(pa) >= le
            out.append(Occurrence(
                offset=ls if at_end else max(ls, m.start() - len(pb)),
                numeral_at=m.start(), token_len=len(m.group(0)), ordinal=val, system=sysm.name,
                punct_before=pb[-3:], word_before=wb[:24], punct_after=pa[:3], word_after=wa[:24],
                at_line_start=at_start, at_line_end=at_end,
            ))
            if len(out) > MAX_OCCURRENCES:
                return out
    return out


def _line_starts(text: str):
    starts = [0] + [i + 1 for i, ch in enumerate(text) if ch == "\n"]
    import bisect

    def at(pos: int) -> int:
        return starts[bisect.bisect_right(starts, pos) - 1]

    return at


# The candidate GROUPINGS. Several views of the same occurrences; the chain machine picks.
# Each is a function from an Occurrence to a hashable key, or None to exclude it from that view.

def _g_line_start(o: Occurrence):
    return (o.system, "LS", o.punct_before, o.punct_after) if o.at_line_start else None


def _g_line_start_word(o: Occurrence):
    if not o.at_line_start or not o.word_before:
        return None
    return (o.system, "LSW", o.word_before.lower(), o.punct_before, o.punct_after)


def _g_line_end(o: Occurrence):
    return (o.system, "LE", o.punct_before) if o.at_line_end else None


def _g_word_after(o: Occurrence):
    return (o.system, "WA", o.word_after.lower(), o.punct_before) if o.word_after else None


def _g_word_before_anywhere(o: Occurrence):
    return (o.system, "WB", o.word_before.lower()) if o.word_before else None


GROUPINGS: Final[tuple[tuple[str, Callable[[Occurrence], object]], ...]] = (
    ("line_start", _g_line_start),
    ("line_start_word", _g_line_start_word),
    ("line_end", _g_line_end),
    ("word_after", _g_word_after),
    ("word_before", _g_word_before_anywhere),
)


def templates(occs: list[Occurrence]) -> dict[object, list[Occurrence]]:
    """Group occurrences under every candidate view. A template with too few members is dropped."""
    groups: dict[object, list[Occurrence]] = defaultdict(list)
    for name, key in GROUPINGS:
        for o in occs:
            k = key(o)
            if k is not None:
                groups[(name, k)].append(o)
    return {k: sorted(v, key=lambda o: o.numeral_at)
            for k, v in groups.items() if len(v) >= MIN_CHAIN}


# --------------------------------------------------------------------------------------
# LAYER 3 — THE CHAIN MACHINE. Corpus-free; unchanged in substance, O(n log n) in form.
# --------------------------------------------------------------------------------------

class _MaxTree:
    """Fenwick tree of prefix maxima over the ordinal domain. Values are bounded by MAX_ORDINAL."""

    __slots__ = ("n", "t")

    def __init__(self, n: int) -> None:
        self.n = n
        self.t = [0] * (n + 1)

    def update(self, i: int, v: int) -> None:
        while i <= self.n:
            if self.t[i] < v:
                self.t[i] = v
            i += i & -i

    def query(self, i: int) -> int:
        best = 0
        while i > 0:
            if self.t[i] > best:
                best = self.t[i]
            i -= i & -i
        return best


def stable_chain(values: list[int]) -> tuple[int, list[int]]:
    """`(longest strictly-ascending chain, indices STABLE across every such chain)`.

    An element is stable when it lies on some longest chain AND is the only such element at its
    depth. Two elements sharing a depth are two readings of one position, and a position two
    optimal readings disagree about is refused rather than picked.

    **O(n log n), where the version this replaces was O(n^2).** That was affordable on 150
    candidates and is not on the 200,000 a 2.7-million-character bill produces — the algorithm
    that could only run on the small corpus was itself a way of only ever seeing the small corpus.
    """
    n = len(values)
    if n == 0:
        return 0, []
    # Coordinate-compress: the ordinal domain is now large enough (dotted indices pack to nine
    # digits) that a Fenwick tree over raw values would allocate a billion cells.
    order = {v: i + 1 for i, v in enumerate(sorted(set(values)))}
    m = len(order)
    ending = [1] * n
    tree = _MaxTree(m + 2)
    for j, v in enumerate(values):
        r = order[v]
        ending[j] = tree.query(r - 1) + 1        # strictly less than v
        tree.update(r, ending[j])
    starting = [1] * n
    tree2 = _MaxTree(m + 2)
    for j in range(n - 1, -1, -1):
        r = m + 1 - order[values[j]]
        starting[j] = tree2.query(r - 1) + 1     # strictly greater than v
        tree2.update(r, starting[j])
    longest = max(ending)
    on_some = [j for j in range(n) if ending[j] + starting[j] - 1 == longest]
    at_depth = Counter(ending[j] for j in on_some)
    return longest, [j for j in on_some if at_depth[ending[j]] == 1]


@dataclass(frozen=True)
class Score:
    chain: int
    candidates: int
    span: int
    region: int

    def better_than(self, other: "Score") -> bool:
        """(chain/candidates) * (span/region), in exact integers. No float is compared or hashed."""
        return (self.chain * self.span * other.candidates * other.region >
                other.chain * other.span * self.candidates * self.region)

    def ratio(self) -> float:
        if not self.candidates or not self.region:
            return 0.0
        return (self.chain / self.candidates) * (self.span / self.region)


ZERO = Score(0, 1, 0, 1)


def score_template(occs: list[Occurrence], lo: int, hi: int) -> tuple[Score, list[int]]:
    if not occs or hi <= lo:
        return ZERO, []
    length, stable = stable_chain([o.ordinal for o in occs])
    if len(stable) < MIN_CHAIN:
        return ZERO, []
    anchors = [occs[j].numeral_at for j in stable]
    return Score(length, len(occs), anchors[-1] - anchors[0], hi - lo), stable
