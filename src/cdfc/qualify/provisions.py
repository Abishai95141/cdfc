"""N1 — DURABLE DIVISION ADDRESSING: an eId taken from the instrument's own numbering.

## What this exists to fix

`docs/measurements/N1-repin-blast-radius.md` measured the cost of re-pinning the statutory
instrument. **Moving the bytes costs nothing; moving the SEGMENTATION costs everything.** A unit key
is `p0143.s0008` — a page/sentence COORDINATE — so a shift of the whole text leaves all 11 provision
citations resolving, while a resegmentation leaves **0 of 11** resolving and loses every admission.

This adds a SECOND addressing layer. It does not replace the first and does not move a single span:

    COORDINATE   p0148.s0007       physical. Survives a byte shift; dies on a resegmentation.
    DIVISION     div1_0008         the instrument's own numbering. Survives both.

## F4 IS FALSE, AND THE COUNT THAT ESTABLISHED IT WAS NEVER OPENED

`docs/PLAN.md §8 F4` said a layout-preserving re-extraction was the only way to recover provision
numbers: *"the numbers are absent from our pinned corpus entirely. A line-anchored pattern finds 3
regulation numbers in 197,767 characters."*

They are not absent. The Gazette prints them in a margin column beside the heading, and both
extractors emit them at the END of the heading:

    p0148.s0007   'Net worth requirements 8'
    p0158.s0000   'Minimum number of Investors 44'

A pattern anchored on `^\\d{1,3}\\.` cannot see any of those. The 3 it found are the three the
Gazette sets inline instead — so the number was a true count of one construct read as a total over
two. **The re-pin therefore needs no re-extraction**, and the boundaries come from text the two
parties already corroborated, which is better evidence than a third reader's opinion.

## THE MACHINE IS CORPUS-FREE; THE SHAPES ARE FITTED TO ONE GAZETTE, AND THAT IS MEASURED

**`docs/measurements/N6-corpus-independence.md` tested this module against eleven corpora and it
ranks the correct division axis first on ONE of them — this one.** The shapes below match an EU
regulation, a US bill, the CFR, three RFCs, a W3C specification, an Indian constitution and a
Victorian novel essentially not at all. What survives the test is the MACHINE: the ascending chain,
the stability rule and the integer scoring are reused unchanged by N6's prototype, which reaches
rank-1 on 3 of 11 and proposes the correct axis somewhere for 9 of 11.

This module is what SHIPS because it is measured, gated by four negative controls and inside the
instrument digest; the better-scoring prototype is none of those things yet. Replacing a measured
component with an unmeasured one is the trade this repository exists to refuse. The replacement
belongs in `A4`, with its own controls.


The failure mode this module was one revision away from shipping was a set of patterns tuned to one
Gazette — an `ORDINALS = {FIRST…TENTH}` map that recovers nothing from an instrument numbering its
schedules `SCHEDULE 3`, and a scan anchored at unit starts that had already published *"no unit
carries a THIRD SCHEDULE heading"* about a heading sitting mid-unit, 175 characters into `sch_0002`.
Both are the shape of defect this repository keeps finding: **a pattern's blind spot published as a
fact about the document.**

So the two halves are separated and only one of them knows anything about a corpus:

**`MARKER_SHAPES` is DATA** — a name, a regex, an ordinal decoder. Six are declared. A corpus whose
markers match none of them recovers nothing and says so; a corpus needing a seventh gets a row here,
not a branch somewhere.

**`stable_chain` is the machine, and it knows nothing about statutes.** Its only premise is that a
DIVISION'S NUMBERING ASCENDS — true of the CFR, of EU regulations, of EBA rule tables, of any
numbered document — while a SUBDIVISION'S RESTARTS at every parent. That one asymmetry is enough to
tell the levels apart by measurement:

    DECIMAL_TRAILING   candidates 147   longest ascending chain 144
    PAREN_LETTER       candidates 365   longest ascending chain  40
    PAREN_DECIMAL      candidates 335   longest ascending chain   9

**Nothing declares that the margin number is the top level.** It wins by 3.6x on a criterion that is
a property of numbering, and the margin is published so the reader can see how near the decision was.

A level may use more than one shape — this instrument sets three of its 148 provisions inline — so
shapes are added greedily and an addition is kept only if it **lengthens the chain AND leaves every
element stable**. `+DECIMAL_LEADING` takes 144 to 147 with all 147 stable and is accepted; every
other shape is rejected. There is no threshold anywhere in that rule.

## STABILITY, AND WHY A TIE IS NOT A COIN-TOSS

An element is STABLE when it appears in *every* longest ascending chain. An unstable one is a
position where two equally good readings of the document disagree, and it is refused by name rather
than resolved by which one the algorithm happened to build — the rule `cdfc.correspond` applies when
two alignments score alike, for the same reason.

## WHAT A DISPUTED REGION DOES

A marker inside one cannot anchor a division: the parties disagree there and the text is the
sentinel. Regulation **100** is lost that way and the refusal says so. The remedy is a third
competent party, not a better pattern.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Sequence
from functools import cmp_to_key
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

MAX_HEADING_CHARS: Final[int] = 240

# Cheap guards on the O(n^2) stability pass. Neither has ever bound on a real instrument — the
# largest shape here yields 365 candidates — and they exist so a pathological input degrades into a
# declared refusal instead of a hang.
MAX_CANDIDATES: Final[int] = 20_000
MAX_RUNS: Final[int] = 4

# HOW DEEP TO ADDRESS, and this is a declared scope rather than a limit of the machine. Depth 0 is
# the division (`regulation 8`), depth 1 the subdivision (`8(1)`) — which is what `A4` cites and
# what the plan writes as `reg_8__subreg_1`. Running deeper recovers lettered and roman lists too;
# it was measured at depth 4 and produced 1,176 further divisions whose numbering restarts inside
# every sentence, so the level selection there is choosing between shapes on chains of length 1.
# Nothing needs those addresses yet, and an address nothing cites is an address nobody checks.
DEFAULT_DEPTH: Final[int] = 2

# A LEVEL NEEDS AT LEAST TWO DIVISIONS. One marker is not a numbering, and a "level" recovered from
# it puts a single arbitrary boundary into the address space. This is a definition, not a threshold.
MIN_CHAIN: Final[int] = 2


def _ratio(score: tuple[int, int, int, int]) -> float:
    """`(chain/candidates) * (span/region)`, FOR DISPLAY. Never hashed, never compared."""
    chain, cand, span, region = score
    return (chain / cand) * (span / region) if cand and region else 0.0


class ShapeError(RuntimeError):
    """A declared marker shape is malformed. Never defaulted, never skipped."""


def _roman(s: str) -> int | None:
    vals = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
    total = 0
    prev = 0
    for ch in reversed(s.lower()):
        v = vals.get(ch)
        if v is None:
            return None
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total or None


def _letter(s: str) -> int | None:
    """`a`→1 … `z`→26, then the DOUBLED form `aa`→27, `bb`→28, `cc`→29.

    **Not the spreadsheet convention, and using it was a defect.** Legal drafting continues past
    `(z)` with `(aa) (bb) (cc) (dd)` — the letter repeated, not a base-26 numeral. Under base-26
    those decode to 27, 54, 81 and 108, so regulation 2's definitions appeared to skip 80 ordinals
    and the map published 336 rows claiming ordinals had been skipped that the document never
    numbered. Which convention a document uses is visible in the sequence it produces; this one is
    the convention that produces a sequence at all.

    A mixed pair like `(is)` is not an ordinal in either convention and returns None, which also
    stops ordinary two-letter words inside parentheses from entering the candidate pool.
    """
    t = s.lower()
    if not t or not all("a" <= ch <= "z" for ch in t):
        return None
    if len(t) == 1:
        return ord(t) - 96
    if len(set(t)) == 1:
        return 26 * (len(t) - 1) + (ord(t[0]) - 96)
    return None


# The ENGLISH ordinal words. Declared here as one shape among six rather than as a special case in
# the recovery, so that an instrument using them gets them and one that does not loses nothing else.
_ORDINAL_WORDS: Final[dict[str, int]] = {
    w: i + 1 for i, w in enumerate(
        ("FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH",
         "TENTH", "ELEVENTH", "TWELFTH")
    )
}


@dataclass(frozen=True, slots=True)
class MarkerShape:
    """One way a document can write an ordinal. Data, not control flow.

    `pattern` must expose exactly one capturing group — the ordinal — and is matched against the
    WHOLE instrument text at character offsets, never against a unit. Anchoring to a unit boundary
    is what hid `THIRD SCHEDULE` 175 characters inside another unit.
    """

    name: str
    pattern: re.Pattern[str]
    decode: Callable[[str], int | None]
    note: str
    # WHERE THE DIVISION BEGINS relative to the match, and it is not always the match.
    # `DECIMAL_TRAILING` matches the margin number at the END of `'Net worth requirements 8'`, so a
    # division anchored at the match would start at `'8'` and drop its own heading — which the
    # first run of this module did, publishing `heading='44'`.
    starts_at_line: bool = False

    def __post_init__(self) -> None:
        if self.pattern.groups != 1:
            raise ShapeError(
                f"{self.name}: a shape captures exactly one group, the ordinal; this one captures "
                f"{self.pattern.groups}. A shape that captures two has no unambiguous number."
            )


MARKER_SHAPES: Final[tuple[MarkerShape, ...]] = (
    MarkerShape(
        "DECIMAL_LEADING", re.compile(r"(?m)^(\d{1,3})\.\s"), int,
        "'75. (1) A FME shall…' — the number set inline at the head of the division",
    ),
    MarkerShape(
        "DECIMAL_TRAILING", re.compile(r"(?m)\s(\d{1,3})$"), int,
        "'Net worth requirements 8' — a margin column the extractor emits at the line's end. "
        "This is the shape F4 asserted did not exist.",
        starts_at_line=True,
    ),
    MarkerShape(
        "PAREN_DECIMAL", re.compile(r"(?m)^\((\d{1,2})\)\s"), int,
        "'(1) An entity seeking registration…' — the sub-division form",
    ),
    MarkerShape(
        "PAREN_ROMAN", re.compile(r"(?m)^\((x{0,3}(?:ix|iv|v?i{0,3}))\)\s"), _roman,
        "'(iv) who have disclosed all the defaults…' — a third-level list",
    ),
    MarkerShape(
        "PAREN_LETTER", re.compile(r"(?m)^\(([a-z]{1,2})\)\s"), _letter,
        "'(b) Unlisted securities' — a lettered list",
    ),
    MarkerShape(
        "ORDINAL_WORD",
        re.compile(r"\b(" + "|".join(_ORDINAL_WORDS) + r")\s+[A-Z]{3,}"),
        _ORDINAL_WORDS.get,
        "'SECOND SCHEDULE NET WORTH REQUIREMENTS' — ENGLISH ordinal words, and the one shape here "
        "that is language-bound. An instrument writing 'SCHEDULE 3' matches DECIMAL shapes instead; "
        "one writing neither recovers no divisions at that level and declares it.",
    ),
)


class DivisionRefusal(StrEnum):
    """Why a candidate did not become a division. CLOSED, and every refusal takes one.

    `absent != empty != zero`: a marker no shape matched is a different fact from one the parties
    disagreed on, and from one that two equally good readings placed differently.
    """

    NOT_ON_ASCENDING_CHAIN = "not_on_ascending_chain"
    UNSTABLE_POSITION = "unstable_position"
    ANCHOR_DISPUTED = "anchor_disputed"
    ORDINAL_SKIPPED = "ordinal_skipped"
    NOT_A_NEW_SEQUENCE = "not_a_new_sequence"
    TOO_MANY_CANDIDATES = "too_many_candidates"


@dataclass(frozen=True, slots=True)
class Division:
    """One numbered region, named by the instrument's own numbering.

    `eid` carries the run and a four-digit ordinal so that **lexicographic order is document
    order** — the contract `Unit.key` also carries. `div1_8` and `div1_10` sort the wrong way
    round; `div1_0008` and `div1_0010` do not.

    **The eId says NOTHING about what the document calls this division**, because the recovery
    cannot know. `label` is set at pin time from the instrument's own front matter and is for
    rendering only: changing it must never change an address.
    """

    eid: str
    run: int
    ordinal: int
    heading: str
    span: tuple[int, int]
    unit_keys: tuple[str, ...]
    recovered_by: str
    depth: int
    n_agreed: int
    n_single_party: int
    n_disputed: int

    def is_wholly_corroborated(self) -> bool:
        return self.n_disputed == 0 and self.n_single_party == 0


@dataclass(frozen=True, slots=True)
class LevelSelection:
    """Which shapes won a level, and by how much. Published so the choice is checkable.

    `margin` is the winning score over the best REJECTED shape's. A margin near zero on a real
    instrument means the level was nearly a coin-toss and the reader should know.

    `score` is FOUR INTEGERS — `(chain, candidates, span chars, region chars)` — so both ratios
    ship with both of their integers and nothing hashed here is a float.
    """

    run: int
    depth: int
    shapes: tuple[str, ...]
    chain_length: int
    score: tuple[int, int, int, int]           # (chain, candidates, span chars, region chars)
    runner_up: str
    runner_up_score: tuple[int, int, int, int]

    @property
    def margin(self) -> float:
        """The winning score less the runner-up's, as a float FOR DISPLAY ONLY.

        Never hashed and never compared — `_better` does the comparing in integers. This exists so
        a measurement table can print how near a level was to going the other way.
        """
        return _ratio(self.score) - _ratio(self.runner_up_score)


@dataclass(frozen=True, slots=True)
class DivisionMap:
    """The recovered divisions, every candidate refused, and how each level was chosen.

    A map carrying only what it admitted would report a recovery rate with the denominator removed.
    """

    divisions: tuple[Division, ...]
    refused: tuple[tuple[str, str, str], ...]     # (eid-or-ordinal, reason, what was read)
    selections: tuple[LevelSelection, ...]
    units_outside_any_division: int

    def by_eid(self) -> dict[str, Division]:
        return {d.eid: d for d in self.divisions}

    def top_level(self) -> tuple[Division, ...]:
        return tuple(d for d in self.divisions if d.depth == 0)

    def counts(self) -> dict[str, int]:
        c = Counter(d.depth for d in self.divisions)
        return {f"depth_{k}": v for k, v in sorted(c.items())} | {
            "divisions_total": len(self.divisions),
            "refused_total": len(self.refused),
        }


# --- the machine. Nothing below knows what a statute is. ---------------------------------


def _candidates(text: str, lo: int, hi: int, shape: MarkerShape) -> list[tuple[int, int, str]]:
    """(offset, ordinal, shape name) for one shape inside `text[lo:hi]`, at ABSOLUTE offsets."""
    out: list[tuple[int, int, str]] = []
    for m in shape.pattern.finditer(text, lo, hi):
        v = shape.decode(m.group(1))
        if v is None:
            continue
        start = m.start()
        if shape.starts_at_line:
            start = max(lo, text.rfind("\n", lo, start) + 1)
        out.append((start, v, shape.name))
    return out


def _stable_chain(cand: Sequence[tuple[int, int, str]]) -> tuple[int, list[int]]:
    """`(longest ascending chain length, indices STABLE across every such chain)`.

    An element is stable when it lies on some longest chain AND is the only such element at its
    depth in that chain. Two elements sharing a depth are two readings of one position, and a
    position two optimal readings disagree about is refused rather than picked.
    """
    n = len(cand)
    if n == 0:
        return 0, []
    v = [c[1] for c in cand]
    ending = [1] * n      # longest ascending chain ENDING at j
    starting = [1] * n    # longest ascending chain STARTING at j
    for j in range(n):
        for i in range(j):
            if v[i] < v[j] and ending[i] + 1 > ending[j]:
                ending[j] = ending[i] + 1
    for j in range(n - 1, -1, -1):
        for k in range(j + 1, n):
            if v[j] < v[k] and starting[k] + 1 > starting[j]:
                starting[j] = starting[k] + 1
    longest = max(ending)
    on_some = [j for j in range(n) if ending[j] + starting[j] - 1 == longest]
    at_depth = Counter(ending[j] for j in on_some)
    return longest, [j for j in on_some if at_depth[ending[j]] == 1]


def _score(
    cand: Sequence[tuple[int, int, str]], lo: int, hi: int
) -> tuple[tuple[int, int, int, int], int, list[int]]:
    """`(score, chain length, stable indices)` for one candidate pool. THE LEVEL CRITERION.

    **Chain length alone is the wrong criterion and choosing it was a real defect.** In the schedule
    region of this instrument the lettered lists inside the schedules give an ascending chain of 19
    while the six schedule headings give 6, so length picked the SUBDIVISION as the top level and
    the schedules were never recovered.

    Two properties separate a top-level numbering from a subdivision's, and both are properties of
    what a top-level numbering IS rather than constants anybody chose:

        PURITY     chain / candidates. A divider's numbering ascends throughout; a subdivision's
                   RESTARTS at every parent, so most of its markers cannot be on one chain.
                   DECIMAL_TRAILING 144/147 = 0.98; PAREN_DECIMAL 9/335 = 0.03.

        COVERAGE   how much of the region the chain spans. ORDINAL_WORD is perfectly monotone here
                   — 6 of 6 — but every one of its markers is in the last sixth of the document, so
                   it is not what divides the document; it is what divides its tail.

    Their product picks DECIMAL_TRAILING over the whole instrument (0.81 against 0.37) and
    ORDINAL_WORD over the schedule tail (0.91 against 0.03), with no threshold in either.

    **THE SCORE IS FOUR INTEGERS, NEVER A FLOAT.** `cdfc.canon` refuses a float outright — *"a float
    here is a reproducibility bug, not a value"* — and it caught this on the first write. Returning
    `(chain, candidates, span_chars, region_chars)` also satisfies `ci/no-bare-rate.sh`: the two
    ratios ship with both of their integers, and `_better` compares by exact cross-multiplication,
    so the choice between two shapes is decided in integer arithmetic and is bit-reproducible.
    """
    if not cand or hi <= lo:
        return (0, 1, 0, 1), 0, []
    length, stable = _stable_chain(cand)
    if not stable:
        return (0, 1, 0, 1), length, []
    anchors = [cand[j][0] for j in stable]
    return (length, len(cand), anchors[-1] - anchors[0], hi - lo), length, stable


def _better(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    """Is `a` a strictly better level score than `b`? `(chain/cand)*(span/region)`, in integers."""
    return a[0] * a[2] * b[1] * b[3] > b[0] * b[2] * a[1] * a[3]


def _select(
    text: str, lo: int, hi: int, shapes: Sequence[MarkerShape]
) -> tuple[list[tuple[int, int, str]], list[int], tuple[str, ...], int, str, float, float]:
    """Choose the shape set for one level BY MEASUREMENT, then return its stable chain.

    Greedy: take the best-scoring shape, then keep adding any shape that both RAISES THE SCORE and
    leaves every element of the chain stable. A shape that lengthens the chain by destabilising it
    has traded a boundary the document states for one two readings disagree about. The runner-up
    and both scores are returned so the margin can be published — a level decided by 0.01 is a
    level the reader should be told about.
    """
    ZERO = (0, 1, 0, 1)
    scored: list[tuple[tuple[int, int, int, int], str, MarkerShape]] = []
    for shape in shapes:
        c = sorted(_candidates(text, lo, hi, shape))
        if len(c) > MAX_CANDIDATES:
            continue
        sc, _length, _stable = _score(c, lo, hi)
        if _better(sc, ZERO):
            scored.append((sc, shape.name, shape))
    if not scored:
        return [], [], (), 0, "", ZERO, ZERO
    # Ordered by `_better` and NOTHING ELSE, then by NAME so a tie resolves the same way on every
    # machine. **The comparison used to be written twice** — once here as a sort key and once in
    # `_better` — and the two are not the same code even when they agree. A negative control that
    # replaced `_better` with raw chain length flipped NO guard, because the choice was being made
    # by this line and `_better` only filtered zeroes. A control that breaks a rule the system does
    # not consult proves nothing, and the second copy is why it could happen.
    scored.sort(key=cmp_to_key(
        lambda x, y: -1 if _better(x[0], y[0]) else (1 if _better(y[0], x[0]) else
                                                    (-1 if x[1] < y[1] else 1))))
    best = scored[0][2]
    runner_up, runner_score = (scored[1][1], scored[1][0]) if len(scored) > 1 else ("", ZERO)

    chosen = [best]
    pool = sorted(_candidates(text, lo, hi, best))
    score, length, stable = _score(pool, lo, hi)
    for _s, _name, shape in scored[1:]:
        trial = sorted(pool + _candidates(text, lo, hi, shape))
        if len(trial) > MAX_CANDIDATES:
            continue
        t_score, t_len, t_stable = _score(trial, lo, hi)
        if _better(t_score, score) and len(t_stable) == t_len:
            pool, score, length, stable = trial, t_score, t_len, t_stable
            chosen.append(shape)
    return pool, stable, tuple(s.name for s in chosen), length, runner_up, score, runner_score


def recover(
    units: Sequence[tuple[str, int, tuple[int, int], str]],
    text: str,
    *,
    shapes: Sequence[MarkerShape] = MARKER_SHAPES,
    max_depth: int = DEFAULT_DEPTH,
) -> DivisionMap:
    """Recover the division map from the CORROBORATED text. Deterministic; no model, no network.

    `units` is `(key, page, span, corroboration)` in document order — plain tuples rather than
    `ResolvedUnit` so `textsource` can import this module and not the other way round.
    """
    disputed = tuple((u[2][0], u[2][1]) for u in units if u[3] == "DISPUTED")
    divisions: list[Division] = []
    refused: list[tuple[str, str, str]] = []
    selections: list[LevelSelection] = []

    # SUCCESSIVE RUNS, because a document may hold more than one top-level sequence. This instrument
    # holds regulations 1–148 and then schedules 1–6, and the schedules' numbering RESTARTS — so a
    # single ascending chain cannot contain both, and the second sequence would be swallowed by the
    # last division of the first. (It was: `div1_0148` carried 181 units, the whole schedule set,
    # and a citation to "Repeal and Savings" returned the net-worth table.)
    #
    # Nothing here names a schedule. The machine re-runs on the text the previous run's numbering
    # did not reach, and a document with one sequence produces one run and a second that finds
    # nothing. When a later run does find a sequence, the previous run's last division is CLIPPED
    # to where it begins — which is the only way to learn that boundary, since neither sequence
    # announces its own end.
    run = 0
    cursor = 0
    while cursor < len(text) and run < MAX_RUNS:
        run += 1
        found = _descend(text, cursor, len(text), units, disputed, shapes, run, 0, max_depth,
                         divisions, refused, selections)
        if not found:
            break
        # A LATER RUN MUST OPEN A NEW NUMBERING, and the test is that it starts at 1. Without it
        # the loop kept going into the last division's own body and returned its lettered list —
        # ordinals 2..7 — as a third top-level sequence, duplicating divisions the depth recursion
        # had already recovered as subdivisions. Run 1 is exempt: a document whose first division
        # is numbered 2 has lost a page, which is a different finding from having no numbering.
        if run > 1 and min(d.ordinal for d in found) != 1:
            for d in found:
                refused.append((d.eid, DivisionRefusal.NOT_A_NEW_SEQUENCE.value,
                                f"run {run} opens at ordinal {min(x.ordinal for x in found)}, not 1; "
                                f"these are subdivisions of run {run - 1}, already addressed"))
            for d in list(divisions):
                if d.run == run:
                    divisions.remove(d)
            selections[:] = [x for x in selections if x.run != run]
            break
        if run > 1:
            _clip_previous_run(divisions, units, run, found[0].span[0])
        cursor = found[-1].span[0] + 1

    covered = {k for d in divisions for k in d.unit_keys}
    return DivisionMap(
        divisions=tuple(sorted(divisions, key=lambda d: (d.span[0], d.depth))),
        refused=tuple(sorted(set(refused))),
        selections=tuple(selections),
        units_outside_any_division=sum(1 for u in units if u[0] not in covered),
    )


def _clip_previous_run(
    divisions: list[Division],
    units: Sequence[tuple[str, int, tuple[int, int], str]],
    run: int,
    boundary: int,
) -> None:
    """Truncate the divisions of run `run - 1` that overrun the next run's first anchor.

    Mutates in place because the alternative — carrying an open-ended span until the whole document
    is read — would let a caller address a division whose extent is not yet known.
    """
    for i, d in enumerate(divisions):
        if d.run != run - 1 or d.span[1] <= boundary:
            continue
        block = [u for u in units if u[2][0] >= d.span[0] and u[2][1] <= boundary]
        divisions[i] = Division(
            eid=d.eid, run=d.run, ordinal=d.ordinal, heading=d.heading,
            span=(d.span[0], boundary), unit_keys=tuple(u[0] for u in block),
            recovered_by=d.recovered_by, depth=d.depth,
            n_agreed=sum(1 for u in block if u[3] == "AGREED"),
            n_single_party=sum(1 for u in block if u[3] == "SINGLE_PARTY"),
            n_disputed=sum(1 for u in block if u[3] == "DISPUTED"),
        )


def _descend(
    text: str, lo: int, hi: int,
    units: Sequence[tuple[str, int, tuple[int, int], str]],
    disputed: Sequence[tuple[int, int]],
    shapes: Sequence[MarkerShape],
    run: int, depth: int, max_depth: int,
    divisions: list[Division], refused: list[tuple[str, str, str]],
    selections: list[LevelSelection],
    parent_eid: str = "",
) -> list[Division]:
    """One level inside `[lo, hi)`, then the same again inside each division it found."""
    if depth >= max_depth or lo >= hi:
        return []
    pool, stable, chosen, length, runner_up, score, runner_score = _select(text, lo, hi, shapes)
    if len(stable) < MIN_CHAIN:
        return []
    selections.append(LevelSelection(run=run, depth=depth, shapes=chosen, chain_length=length,
                                     score=score, runner_up=runner_up,
                                     runner_up_score=runner_score))

    keep = set(stable)
    stable_ordinals = {pool[k][1] for k in stable}
    for j, (off, ordinal, shape_name) in enumerate(pool):
        if j in keep:
            continue
        why = (DivisionRefusal.UNSTABLE_POSITION if ordinal in stable_ordinals
               else DivisionRefusal.NOT_ON_ASCENDING_CHAIN)
        refused.append((f"{ordinal}@{off}", why.value, f"{shape_name}: {text[off:off + 90]!r}"))

    anchors = [pool[j] for j in stable]
    out: list[Division] = []
    for a, (off, ordinal, shape_name) in enumerate(anchors):
        end = anchors[a + 1][0] if a + 1 < len(anchors) else hi
        # A marker inside a disputed region cannot anchor: the parties disagree there and the text
        # is the sentinel, so nobody can read what the heading said.
        if any(d0 <= off < d1 for d0, d1 in disputed):
            refused.append((f"{ordinal}@{off}", DivisionRefusal.ANCHOR_DISPUTED.value,
                            f"{shape_name}: the anchor is inside a region the parties disagree on"))
            continue
        block = [u for u in units if u[2][0] >= off and u[2][1] <= end]
        eid = f"{parent_eid}__sub_{ordinal:04d}" if parent_eid else f"div{run}_{ordinal:04d}"
        d = Division(
            eid=eid, run=run, ordinal=ordinal, heading=_heading(text, off, end),
            span=(off, end), unit_keys=tuple(u[0] for u in block),
            recovered_by=shape_name, depth=depth,
            n_agreed=sum(1 for u in block if u[3] == "AGREED"),
            n_single_party=sum(1 for u in block if u[3] == "SINGLE_PARTY"),
            n_disputed=sum(1 for u in block if u[3] == "DISPUTED"),
        )
        divisions.append(d)
        out.append(d)
        _descend(text, off, end, units, disputed, shapes, run, depth + 1, max_depth,
                 divisions, refused, selections, parent_eid=eid)

    _declare_gaps(out, run, parent_eid, refused)
    return out


def _declare_gaps(
    out: Sequence[Division], run: int, parent_eid: str, refused: list[tuple[str, str, str]]
) -> None:
    """An ordinal between two admitted neighbours that nothing anchored, with its reason.

    **Only between CONSECUTIVE admitted ordinals.** Enumerating `min..max` instead reports a gap
    for every integer a single outlier reaches past — the first version of this did exactly that
    and produced 10,494 refusal rows claiming "ordinal 100 skipped" at every depth, because one
    two-letter list marker decoded to 243.

    A gap run longer than the sequence that contains it is not a gap: two ordinals that far apart
    are not neighbours in one numbering, and saying they are would invent a hundred missing
    divisions from one false positive.
    """
    if len(out) < MIN_CHAIN:
        return
    for prior, nxt in zip(out, out[1:]):
        run_len = nxt.ordinal - prior.ordinal - 1
        if not 0 < run_len <= len(out):
            continue
        why = (DivisionRefusal.ANCHOR_DISPUTED if prior.n_disputed
               else DivisionRefusal.ORDINAL_SKIPPED)
        for gap in range(prior.ordinal + 1, nxt.ordinal):
            refused.append((
                f"{gap}@{parent_eid or f'run{run}'}", why.value,
                f"no admitted marker carries ordinal {gap} between {prior.eid} and {nxt.eid}"
                + (f"; {prior.eid} carries {prior.n_disputed} disputed unit(s) of "
                   f"{len(prior.unit_keys)}" if why is DivisionRefusal.ANCHOR_DISPUTED else ""),
            ))


def _heading(text: str, off: int, end: int) -> str:
    """The division's opening text, to the first line break. For rendering, never for addressing."""
    line = text[off:min(end, off + MAX_HEADING_CHARS)]
    return line.split("\n", 1)[0].strip()
