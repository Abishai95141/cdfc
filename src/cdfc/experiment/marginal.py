"""P12-B2 — marginal kill, and **`beats_baselines` as arithmetic rather than prose** (F30).

## The bar exists before the candidates, and it is not a straw man

Two of the three demolitions in this literature are demolitions by baseline: a synthesis result
that looked strong until somebody ran the free work. So `B0 ∪ B1 ∪ B2` is computed, frozen and
content-addressed **before the first API call**, and its hash goes into the lock.

- **B0 is a subset of what the product already ships** — the template's own formula-derived
  identities, `sum_identity`, `tally_identity`, `cross_sheet_equality`, `same_sheet_equality`,
  which the harvest emits for nothing. A baseline the product already contains cannot be accused
  of being built to lose, and `test_b0__is_a_subset_of_the_harvest` is that argument as a test.
- **B1 is NOT Daikon and says so.** `cdfc.qualify.baselines.b1_invariants.NOT_DAIKON` is the
  sentence that travels with every B1 figure. It is a weaker miner than the plan specified, so a
  candidate's marginal kill over B1 **overstates** its marginal kill over Daikon — the direction
  that flatters us, stated wherever the number is printed.
- **B2 is in the set BECAUSE it is embarrassing.** *"No cell is blank; no cell errors."* Its
  published analogue found 68.9% of a neural oracle's bugs at twice its precision. Dropping it, or
  footnoting a high kill count, is NC-M08.

## §0.6 — the two preconditions, both fail-closed

`comparable` is `False`, and `beats_baselines` therefore `False`, when either holds:

1. **`candidate FFR upper bound exceeds baseline`.** A candidate that kills more *because it flags
   more* has not beaten a baseline; it has moved along the same trade-off. Predicates here are
   boolean and carry no threshold, so there is no knob with which to equalise two false-failure
   rates — which is exactly why this is a **precondition** and not a tuning step.
2. **`FFR CORPUS UNINFORMATIVE FOR BOTH ARMS`** (adversary F2). On a `TEMPLATE-COMPUTED` corpus —
   one our own `calc/` generated — an arithmetic candidate and an arithmetic baseline both fire
   **zero** times regardless of quality. The comparability precondition then passes and tells you
   nothing. The intersection that detects it is **imported from `g4_ffr`**, never re-implemented:
   two implementations of one predicate is a differential nobody is running.

## Why the union floor is `1/10` and not `> 0`

Against the *union* of three free baselines, a single marginal kill is indistinguishable from noise
in a campaign of thousands of mutants, and a RETAIN resting on it would be a RETAIN resting on one
mutant. `union.killed_by_candidate_only > 0` — the reading the prose most naturally supports — makes
G-SETTLE's criterion 4 satisfiable by any candidate that kills one mutant the free work missed.
That is not *"beats free work"*; it is *"is not identical to free work"*.

*Second alternative it beat:* a floor expressed as a fraction of `killed_by_baseline(union)` —
rejected because it is **undefined when the union kills nothing**, which is exactly the `EDR_1`
case (a workbook with zero formula cells, where B0 is empty) that the goldens already pin.

**Integer arithmetic throughout.** `union.killed_by_candidate_only * 10 >= 1 * union.observable`
rather than a division, because a float on a gate path is a gate whose value depends on rounding.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal

# THE LOCKED THRESHOLDS. `cdfc.experiment.criterion` asserts the pre-registration declares each of
# these and that the two agree — in both directions, so a constant here that the document does not
# carry is a threshold outside the lock.
MARGINAL_FLOOR_NUM: Final[int] = 1
MARGINAL_FLOOR_DEN: Final[int] = 10          # 10% of the union's observable set
TARGET_A: Final[int] = 20
GENERATE_CAP_B: Final[int] = 10
CANDIDATES_PER_OBLIGATION_PER_REGIME: Final[int] = 10

BaselineId = Literal["B0", "B1", "B2", "B0|B1|B2"]
UNION_ID: Final[str] = "B0|B1|B2"
BASELINE_IDS: Final[tuple[str, ...]] = ("B0", "B1", "B2", UNION_ID)

# The two incomparability reasons, as constants, because `DECISION.md` renders the literal string
# where a number would otherwise go and a typo would render as a different reason.
FFR_UPPER_BOUND_EXCEEDED: Final[str] = "candidate FFR upper bound exceeds baseline"
CORPUS_UNINFORMATIVE: Final[str] = "FFR CORPUS UNINFORMATIVE FOR BOTH ARMS"


class NotComparable(ValueError):
    """A number was asked for from a row that does not carry one."""


@dataclass(frozen=True, slots=True)
class MarginalKill:
    """One row. **Four are always produced** — three baselines and the union (NC-M07).

    Reporting only the union hides that one baseline already killed everything, which is the exact
    shape of the demolitions this build exists to pre-empt.
    """

    baseline_id: str
    observable: int                    # the SHARED denominator O
    killed_by_baseline: int
    killed_by_candidate: int
    killed_by_candidate_only: int      # |K_c \ K_b| — THE marginal number
    comparable: bool
    incomparable_reason: str | None = None

    def __post_init__(self) -> None:
        if self.baseline_id not in BASELINE_IDS:
            raise ValueError(f"{self.baseline_id!r} is not one of {BASELINE_IDS}")
        for name in ("observable", "killed_by_baseline", "killed_by_candidate",
                     "killed_by_candidate_only"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} is a count and cannot be negative")
        if self.killed_by_candidate > self.observable:
            raise ValueError("a candidate cannot kill more mutants than are observable")
        if self.killed_by_baseline > self.observable:
            raise ValueError("a baseline cannot kill more mutants than are observable")
        if self.killed_by_candidate_only > self.killed_by_candidate:
            raise ValueError(
                "the marginal kill is a SET DIFFERENCE |K_c \\ K_b| and cannot exceed |K_c|"
            )
        if self.comparable and self.incomparable_reason is not None:
            raise ValueError("a comparable row carries no incomparable_reason")
        if not self.comparable and not self.incomparable_reason:
            raise ValueError(
                "an incomparable row with no reason renders as a blank where a number was "
                "expected, and a reader fills a blank in with the flattering value"
            )

    def render(self) -> str:
        """**The literal string, not a number, when the comparison is inadmissible.**

        A number rendered under an inadmissible comparison is read as a result. The string is
        longer than the number and that is the point: it does not fit in a column somebody would
        skim.
        """
        if not self.comparable:
            return f"NOT COMPARABLE — {self.incomparable_reason}"
        return f"{self.killed_by_candidate_only}/{self.observable}"

    def as_obj(self) -> dict[str, Any]:
        return {
            "baseline_id": self.baseline_id, "observable": self.observable,
            "killed_by_baseline": self.killed_by_baseline,
            "killed_by_candidate": self.killed_by_candidate,
            "killed_by_candidate_only": (
                self.killed_by_candidate_only if self.comparable else None
            ),
            "comparable": self.comparable,
            "incomparable_reason": self.incomparable_reason,
            "rendered": self.render(),
        }


def corpus_is_uninformative(corpus: Any, read_keys: frozenset[str]) -> bool:
    """F2. A `TEMPLATE-COMPUTED` corpus whose `computed_cells` meet either arm's read set.

    The intersection is `read_keys & corpus.computed_cells` — **the same one `g4_ffr.independent`
    computes**, and `computed_cells` is read off the corpus object rather than recomputed here.
    """
    label = str(getattr(corpus, "provenance", "")).upper()
    if "TEMPLATE" not in label or "COMPUTED" not in label:
        return False
    computed = frozenset(getattr(corpus, "computed_cells", frozenset()))
    return bool(read_keys & computed)


def marginal_kill(
    *,
    observable: frozenset[str],
    candidate_kills: frozenset[str],
    baseline_kills: dict[str, frozenset[str]],
    incomparable_reason: str | None = None,
) -> tuple[MarginalKill, ...]:
    """FOUR rows: one per baseline **and** the union. Never three, never one.

    `observable` is the shared denominator `O` — mutants verified observable by recalculation of
    the workbook-as-program. Every kill set is intersected with it first, so a baseline that
    "killed" an unobservable mutant does not score for it.
    """
    missing = sorted({"B0", "B1", "B2"} - set(baseline_kills))
    if missing:
        raise ValueError(
            f"baselines {missing} are absent. All three rows are produced even when a baseline did "
            "not run — B1 not running contributes a row with killed_by_baseline = 0, which is the "
            "honest reading of 'declared not-run'. Dropping the row would silently strengthen the "
            "candidate by removing a comparison it never beat."
        )

    o = observable
    kc = candidate_kills & o
    per: dict[str, frozenset[str]] = {b: (baseline_kills[b] & o) for b in ("B0", "B1", "B2")}
    per[UNION_ID] = per["B0"] | per["B1"] | per["B2"]

    comparable = incomparable_reason is None
    return tuple(
        MarginalKill(
            baseline_id=b,
            observable=len(o),
            killed_by_baseline=len(per[b]),
            killed_by_candidate=len(kc),
            killed_by_candidate_only=len(kc - per[b]),
            comparable=comparable,
            incomparable_reason=incomparable_reason,
        )
        for b in BASELINE_IDS
    )


def beats_baselines(rows: Sequence[MarginalKill]) -> bool:
    """**G-SETTLE criterion 4, as a pure function of the four rows and nothing else.**

    Verbatim in `PREREGISTRATION.md`. `decide()` takes this function's *value*, never the rows, so
    no argument, rationale or override can enter through this door.

        every row comparable                                          (§0.6, fail-closed)
      ∧ killed_by_candidate_only > 0 against B0, B1 and B2 separately
      ∧ union.killed_by_candidate_only · 10 ≥ 1 · union.observable    (the 10% floor)

    **A prose reading of this is a build failure, not an interpretation.**
    """
    rows = tuple(rows)
    if len(rows) != len(BASELINE_IDS) or {r.baseline_id for r in rows} != set(BASELINE_IDS):
        raise ValueError(
            f"expected exactly the four rows {BASELINE_IDS}; got "
            f"{sorted(r.baseline_id for r in rows)}. Evaluating the criterion over a partial row "
            "set is evaluating a different criterion."
        )

    per_baseline = tuple(r for r in rows if r.baseline_id != UNION_ID)
    union = next(r for r in rows if r.baseline_id == UNION_ID)

    if not all(r.comparable for r in rows):
        return False
    if not all(r.killed_by_candidate_only > 0 for r in per_baseline):
        return False
    return (union.killed_by_candidate_only * MARGINAL_FLOOR_DEN
            >= MARGINAL_FLOOR_NUM * union.observable)


def evaluate_term_by_term(rows: Sequence[MarginalKill]) -> tuple[tuple[str, bool, str], ...]:
    """`(term, value, working)` — so a reader can **recompute the boolean**, not just read it.

    `DECISION.md` prints this table. A published boolean nobody can re-derive is a claim; a
    published boolean beside its three terms and their arithmetic is evidence.
    """
    rows = tuple(rows)
    per_baseline = tuple(r for r in rows if r.baseline_id != UNION_ID)
    union = next(r for r in rows if r.baseline_id == UNION_ID)

    all_comparable = all(r.comparable for r in rows)
    reasons = sorted({r.incomparable_reason for r in rows if r.incomparable_reason})
    each_positive = all(r.killed_by_candidate_only > 0 for r in per_baseline)
    floor_met = (union.killed_by_candidate_only * MARGINAL_FLOOR_DEN
                 >= MARGINAL_FLOOR_NUM * union.observable)

    return (
        (
            "every row comparable (§0.6)",
            all_comparable,
            "all four rows comparable" if all_comparable else "; ".join(reasons),
        ),
        (
            "marginal > 0 against each of B0, B1, B2",
            each_positive,
            ", ".join(f"{r.baseline_id}={r.killed_by_candidate_only}" for r in per_baseline),
        ),
        (
            f"union marginal ≥ {MARGINAL_FLOOR_NUM}/{MARGINAL_FLOOR_DEN} of observable",
            floor_met,
            f"{union.killed_by_candidate_only} × {MARGINAL_FLOOR_DEN} = "
            f"{union.killed_by_candidate_only * MARGINAL_FLOOR_DEN} "
            f"{'≥' if floor_met else '<'} {MARGINAL_FLOOR_NUM} × {union.observable} = "
            f"{MARGINAL_FLOOR_NUM * union.observable}",
        ),
    )
