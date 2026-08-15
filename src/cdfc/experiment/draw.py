"""P12-B1 — the pool, the draw, and the two integers that must never be folded together.

## The draw is a KEYED SORT, not a Mersenne Twister — DECIDED, and it is a deviation

`plan/06` §"What `PREREGISTRATION.md` contains" item 1 asks for *"the PRNG algorithm and the seed
as a literal integer"*. The obvious reading is `random.Random(seed).shuffle(pool)`. **This module
uses a keyed sort instead: the permutation is `sorted(pool, key=sha256(seed ‖ ordinal))`.**

*Reason:* the draw is the object the whole experiment's credibility rests on, and a reader who
doubts us must be able to **recompute it**. `random.shuffle`'s output is a property of CPython's
implementation of the Mersenne Twister and of the specific Fisher–Yates loop in `random.py`; it is
stable in practice, documented nowhere as a format, and not reproducible in another language
without porting CPython. A sha256-keyed sort is reproducible by anyone with a hash function, in
any language, forever. *Alternative it beat:* `random.Random(seed)`, rejected because "trust our
interpreter version" is a weaker guarantee than "here is the hash", and this is the one artifact
where the guarantee is the product. The algorithm is written into `PREREGISTRATION.md` in the form
that lets a reader re-derive it.

**A consequence, and it is the one that matters:** `extend()` continuing "the SAME permutation
without replacement" is then not a promise about mutable PRNG state — it is a **total order over
the pool**, so stage 2 is literally the next prefix and cannot silently be a different sequence.

## §0.4 — the Stratum-B cap is a cap on GENERATION, never on the denominator

*"Draw until `|A| = 20`; cap Stratum B at 10"* and *"`|A| / |drawn|` is the measured decidable
fraction"* are in tension: a cap that stops the draw truncates the denominator of the fraction
being measured. **The draw continues until `|A| == target_a` regardless of how many Bs it turns
up.** Every drawn obligation enters `stratum_b_all` and therefore `|drawn|`; the cap applies only
to `stratum_b_generated`, which is what is carried into candidate generation.

This is NC-D01's mechanism — scope truncation — applied to our own headline, and it moves the
number in the flattering direction. It gets its own control, **NC-M03**, and the property test
`len(drawn) == len(stratum_a) + len(stratum_b_all)` is the assertion that closes it.

## The pool is what is left AFTER exclusion, and the excluded count travels with it

An obligation whose span intersects a region the extractions disagree on has **no authoritative
reading**, so it is excluded — with its reason and its location — and counted. `|drawn|` is the
post-exclusion draw; `excluded` is a **third integer**, never folded in and never dropped, because
it is the size of *our curation of the instrument* and a reader is entitled to it beside the
fraction (NC-M34).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal, Protocol

from cdfc.canon import canonical_json, digest

# The word the pool is enumerated over. A single lower-cased token, matched on word boundaries
# after normalisation — `shall` inside `marshalling` is not an obligation.
OBLIGATION_TOKEN: Final[str] = "shall"

Stratum = Literal["A", "B"]


class PoolExhausted(RuntimeError):
    """The pool ran out before `|A| == target_a`.

    **It never returns short.** A 19-obligation "draw" reported as a draw would make `k of 19` a
    number computed against a rule written for 20, and the shortfall would be invisible in the
    published fraction. `plan/06` names this as a legitimate published outcome — *"`|A| < 20` with
    the disputed-region count and its page numbers"* — which is a measurement of the **instrument**,
    and it is reported by catching this exception, never by returning a smaller `Draw`.
    """


class ExtensionAlreadyTaken(RuntimeError):
    """A second extension. There is no third stage, ever (§0.5, NC-M14)."""


class ChapterNotFound(LookupError):
    """A named chapter did not match exactly.

    **There is no fuzzy chapter match.** A silently-missed chapter is a silently-shrunk
    denominator, and this project has committed that defect four times in other places. The
    enumeration raises rather than returning the obligations it did find.
    """


class StratumOracle(Protocol):
    """The human stratum assignment, read from `experiments/E6/strata.csv`.

    It is a `Protocol` and not a function so that the object carrying the assignment also carries
    *who made it and when* — `NC-M05` asserts `assigned_by` is a person, and an oracle that was
    only `Callable[[int], str]` would have nowhere to keep that.
    """

    def stratum_of(self, ordinal: int) -> Stratum: ...
    def assigned_by(self, ordinal: int) -> str: ...


@dataclass(frozen=True, slots=True)
class Obligation:
    """One `shall` sentence, addressed into the pinned instrument text."""

    ordinal: int                          # position in the canonical ordering, 0-based
    reg_no: int
    sub_clause: tuple[int | str, ...]     # ("1", "a") — PARSED, so ordering is arithmetic
    quote: str                            # the verbatim sentence containing the `shall`
    char_span: tuple[int, int]            # into the pinned text blob
    source_sha256: str                    # the text blob this span indexes into

    def __post_init__(self) -> None:
        lo, hi = self.char_span
        if lo < 0 or hi <= lo:
            raise ValueError(f"span {self.char_span} does not address anything")
        if not self.quote:
            raise ValueError("an obligation with no quote cannot be located, and G0 is a `find`")

    def as_obj(self) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal, "reg_no": self.reg_no,
            "sub_clause": [str(s) for s in self.sub_clause],
            "quote": self.quote, "char_span": list(self.char_span),
            "source_sha256": self.source_sha256,
        }


@dataclass(frozen=True, slots=True)
class ExcludedObligation:
    """An obligation the pool does NOT contain, with the reason and the location.

    **Never a silent drop.** The count and the page numbers are published in the
    pre-registration — before the result — so a reader sizes our curation of the instrument before
    seeing the finding (NC-M34).
    """

    quote: str
    char_span: tuple[int, int]
    page: int
    reason: str

    def as_obj(self) -> dict[str, Any]:
        return {"quote": self.quote, "char_span": list(self.char_span),
                "page": self.page, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class Pool:
    """The enumerated obligations, the exclusions, and the hash of the text they address into."""

    obligations: tuple[Obligation, ...]
    excluded: tuple[ExcludedObligation, ...]
    source_sha256: str
    chapters: tuple[str, ...]

    @property
    def sha256(self) -> str:
        return digest({
            "obligations": [o.as_obj() for o in self.obligations],
            "excluded": [e.as_obj() for e in self.excluded],
            "source_sha256": self.source_sha256,
            "chapters": list(self.chapters),
        })

    def excluded_pages(self) -> tuple[int, ...]:
        return tuple(sorted({e.page for e in self.excluded}))


@dataclass(frozen=True, slots=True)
class Draw:
    """The realised draw. `order` is recorded WHOLE, not just the prefix consumed."""

    pool_sha256: str
    seed: int
    order: tuple[int, ...]                # the full permutation
    drawn: tuple[int, ...]                # the prefix consumed, in order
    stratum_a: tuple[int, ...]
    stratum_b_all: tuple[int, ...]        # EVERY B drawn — the denominator (§0.4)
    stratum_b_generated: tuple[int, ...]  # the first `generate_cap_b` of them
    excluded_count: int                   # the third integer (NC-M34)
    stage: Literal[1, 2]

    def __post_init__(self) -> None:
        # THE INVARIANT §0.4 EXISTS TO PROTECT, asserted at construction rather than in a test
        # alone: a Draw whose drawn set is not exactly its two strata cannot be built at all.
        if len(self.drawn) != len(self.stratum_a) + len(self.stratum_b_all):
            raise ValueError(
                f"|drawn| = {len(self.drawn)} but |A| + |B_all| = "
                f"{len(self.stratum_a)} + {len(self.stratum_b_all)}. The generation cap is a cap "
                "on what is PROCESSED and never on what is COUNTED — a Draw in which they differ "
                "would publish a decidable fraction over a truncated denominator, which is NC-M03."
            )
        if set(self.drawn) != set(self.stratum_a) | set(self.stratum_b_all):
            raise ValueError("the drawn set is not the union of its strata")
        if len(self.stratum_b_generated) > len(self.stratum_b_all):
            raise ValueError("more Stratum-B obligations generated than were drawn")
        if tuple(self.stratum_b_generated) != tuple(self.stratum_b_all[:len(self.stratum_b_generated)]):
            raise ValueError("the generated Stratum-B set is not a prefix of the drawn one")

    @property
    def sha256(self) -> str:
        return digest(self.as_obj())

    def as_obj(self) -> dict[str, Any]:
        return {
            "pool_sha256": self.pool_sha256, "seed": self.seed,
            "order": list(self.order), "drawn": list(self.drawn),
            "stratum_a": list(self.stratum_a),
            "stratum_b_all": list(self.stratum_b_all),
            "stratum_b_generated": list(self.stratum_b_generated),
            "excluded_count": self.excluded_count, "stage": self.stage,
        }

    def as_json(self) -> bytes:
        """`draw.json`'s bytes. Canonical, so the file is byte-identical across environments."""
        return canonical_json(self.as_obj())

    def decidable_fraction(self) -> tuple[int, int, int]:
        """`(|A|, |drawn|, excluded)` — **three integers, published in this order.**

        The fraction is never returned as a single number here, and that is deliberate: a caller
        that wanted one would have to divide, which is where the label
        `power.INVERSE_SAMPLING_LABEL` and both estimators attach.
        """
        return len(self.stratum_a), len(self.drawn), self.excluded_count


def permutation(pool_sha256: str, n: int, *, seed: int) -> tuple[int, ...]:
    """The draw order: indices `0..n-1` sorted by `sha256(pool ‖ seed ‖ index)`.

    Ties break on the index itself, so the permutation is total and the function is pure. The pool
    hash is inside the key so that the same seed over a **different pool** is a different order —
    otherwise a pool edited after the draw would keep its ordering and the edit would be invisible
    in `draw.json`.
    """
    if n < 0:
        raise ValueError("a pool cannot have negative size")

    def key(i: int) -> tuple[bytes, int]:
        material = f"{pool_sha256}:{seed}:{i}".encode("utf-8")
        return hashlib.sha256(material).digest(), i

    return tuple(sorted(range(n), key=key))


def draw(
    pool: Pool,
    *,
    seed: int,
    strata: StratumOracle,
    target_a: int = 20,
    generate_cap_b: int = 10,
    stage: Literal[1, 2] = 1,
) -> Draw:
    """Consume the permutation in order until `|A| == target_a`. **The B cap never stops it.**"""
    order = permutation(pool.sha256, len(pool.obligations), seed=seed)
    return _consume(pool, order, strata, target_a=target_a, generate_cap_b=generate_cap_b,
                    seed=seed, stage=stage, start_at=0, carry_a=(), carry_b=())


def extend(stage1: Draw, pool: Pool, *, strata: StratumOracle, target_a: int = 20,
           generate_cap_b: int = 10) -> Draw:
    """Continue the SAME permutation from where stage 1 stopped, for a further `target_a` As.

    **One draw with a stopping rule, not two experiments** (§0.3, interpretation A). The pooled
    result is what the `≥ 12 of 40` threshold is evaluated over, and the stage-2 indices are the
    next prefix of the same total order — provably, because the order is a keyed sort rather than
    PRNG state somebody has to have kept.
    """
    if stage1.stage != 1:
        raise ExtensionAlreadyTaken(
            f"the draw handed in is already at stage {stage1.stage}. There is exactly one "
            "extension and there is no third stage — §0.5, NC-M14. A second extension would be "
            "re-rolling a criterion that has already been evaluated twice."
        )
    if stage1.pool_sha256 != pool.sha256:
        raise ValueError(
            "the extension is being drawn from a different pool than stage 1. Continuing 'the same "
            "permutation' over a re-curated pool is the defect NC-M34 exists to catch."
        )
    consumed = len(stage1.drawn)
    # THE CAP IS THE EXPERIMENT'S, NOT STAGE 1'S REALISED COUNT. The first version passed
    # `len(stage1.stratum_b_generated)`, which reads plausibly and is wrong in exactly one place:
    # when stage 1 turned up FEWER than ten Stratum-B obligations, the cap froze at whatever it
    # happened to get, and the pooled experiment could never reach ten however many stage 2 drew.
    # The extension is ONE draw with a stopping rule (§0.3, interpretation A), so it is one cap
    # over the pooled set. `|drawn|` was never affected, so §0.4's invariant held throughout and
    # the defect was invisible to NC-M03 — it only ever shrank the Stratum-B arm, which is the
    # arm whose whole job is to tell us whether the human stratification carried information.
    return _consume(
        pool, stage1.order, strata, target_a=target_a, generate_cap_b=generate_cap_b,
        seed=stage1.seed, stage=2, start_at=consumed,
        carry_a=stage1.stratum_a, carry_b=stage1.stratum_b_all,
    )


def _consume(
    pool: Pool, order: Sequence[int], strata: StratumOracle, *,
    target_a: int, generate_cap_b: int, seed: int, stage: Literal[1, 2],
    start_at: int, carry_a: Sequence[int], carry_b: Sequence[int],
) -> Draw:
    stratum_a: list[int] = []
    stratum_b: list[int] = []
    drawn: list[int] = []
    fresh_a = 0
    for idx in order[start_at:]:
        drawn.append(idx)
        if strata.stratum_of(pool.obligations[idx].ordinal) == "A":
            stratum_a.append(idx)
            fresh_a += 1
            if fresh_a == target_a:
                break
        else:
            # THE CAP DOES NOT APPEAR HERE. Every B drawn is appended, and the cap is applied once,
            # below, to the GENERATED slice only.
            stratum_b.append(idx)
    else:
        raise PoolExhausted(
            f"the pool of {len(pool.obligations)} obligations yielded {fresh_a} Stratum-A of the "
            f"{target_a} the decision rule is written over"
            + (f", after excluding {len(pool.excluded)} in extractor-disputed regions"
               if pool.excluded else "")
            + ". This returns nothing rather than a shorter draw: `k of "
            f"{fresh_a}` evaluated against a rule written for {target_a} is a threshold applied to "
            "a denominator it was not chosen for. Publish |A| < 20 with the disputed-region count "
            "and its page numbers — that is a measurement of the INSTRUMENT, and it is a result."
        )

    all_a = tuple(carry_a) + tuple(stratum_a)
    all_b = tuple(carry_b) + tuple(stratum_b)
    all_drawn = tuple(order[:start_at]) + tuple(drawn)
    return Draw(
        pool_sha256=pool.sha256, seed=seed, order=tuple(order), drawn=all_drawn,
        stratum_a=all_a, stratum_b_all=all_b,
        stratum_b_generated=all_b[:generate_cap_b],
        excluded_count=len(pool.excluded), stage=stage,
    )


@dataclass(frozen=True, slots=True)
class TableOracle:
    """A `StratumOracle` backed by the committed `strata.csv` rows.

    `assigned_by` is carried per row rather than per table because two named humans appear in the
    protocol — the assigner and the second assigner who re-does a random 20% for κ — and a single
    table-level author would make the second one unrepresentable.
    """

    assignment: Mapping[int, Stratum]
    assigner: Mapping[int, str]

    def stratum_of(self, ordinal: int) -> Stratum:
        try:
            return self.assignment[ordinal]
        except KeyError:
            raise LookupError(
                f"obligation {ordinal} has no stratum. An unassigned obligation cannot be drawn: "
                "defaulting it to either stratum would make a human judgment into a fallback, and "
                "the stratum assignment is the one human judgment the whole n = 20 rests on."
            ) from None

    def assigned_by(self, ordinal: int) -> str:
        return self.assigner[ordinal]
