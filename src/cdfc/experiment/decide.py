"""P12-B4 — `decide()`. **A pure function, with no parameter an argument can enter through.**

The four inadmissible arguments are hashed into `PREREGISTRATION.md`:

> *"we should have sampled better obligations"* — the rule is pre-registered.
> *"the clean corpus was synthetic"* — known in advance and symmetric with the baselines.
> *"Stratum B was always going to fail"* — hence a separate stratum with a pre-registered
> expectation of 0–1 of 10.
> *"the language was wrong"* — the Python arm is exploratory, is never executed, and may not
> change the CEL decision.

**The signature makes them unrepresentable rather than merely disallowed**, and that is the whole
design of this module. There is no `override`, no `rationale`, no `notes`, no `**kwargs`. A
function that accepted one would be a function somebody could pass one to at 6pm on a Friday, and
the pre-registration would then be a document about a decision that was taken elsewhere.

## §0.5 — `k ≥ 6` without beating the baselines is DELETE, and it was decided before the run

Nothing in the source rule states the outcome when `k ≥ 6` and the free work was not beaten. The
extension exists to resolve a **sample-size** ambiguity in the 3–5 band; a `k ≥ 6` result that does
not beat free work is not a sample-size problem — it is a measurement that the model reproduced
work the template and a mined-invariant baseline already do for nothing. Extending would be
re-rolling a criterion that was already satisfied on the axis the extension addresses.

And the headline it produces is **stronger** than "inconclusive":

> *"the model produced `k` checks that survive the gate and none that the free baselines did not
> already produce."*

## `k = 0` is a result, and this function returns it as one

`DELETE` with `wilson_a == [0.000, 0.161]`. It would be the first measurement anyone has of
whether a frontier model can write a regulator-grade executable check, and the interval is what
makes it publishable rather than anecdotal.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Final, Literal

from cdfc.experiment.marginal import (
    MARGINAL_FLOOR_DEN,
    MARGINAL_FLOOR_NUM,
    MarginalKill,
    evaluate_term_by_term,
)
from cdfc.experiment.power import DELETE1, N1, N2, RETAIN1, RETAIN2, wilson_interval
from cdfc.experiment.prereg import Lock

Verdict = Literal["RETAIN", "DELETE", "EXTEND"]

# The four arguments the pre-registration refuses in advance, as data so a test can assert the
# signature admits none of them and `DECISION.md` can print them.
INADMISSIBLE_ARGUMENTS: Final[tuple[str, ...]] = (
    "we should have sampled better obligations",
    "the clean corpus was synthetic",
    "Stratum B was always going to fail",
    "the language was wrong",
)


class CriterionExhausted(RuntimeError):
    """A third stage. There is no third extension, ever (NC-M14)."""


@dataclass(frozen=True, slots=True)
class SettlingResult:
    """The realised outcome. `n_a` is 20 at stage 1 and **40 POOLED** at stage 2 (§0.3)."""

    k_a: int
    n_a: int
    k_b: int
    n_b: int
    beats_baselines: bool
    per_baseline: tuple[MarginalKill, ...]
    stage: Literal[1, 2]

    def __post_init__(self) -> None:
        if self.k_a < 0 or self.k_b < 0:
            raise ValueError("a survivor count cannot be negative")
        if self.k_a > self.n_a or self.k_b > self.n_b:
            raise ValueError("more obligations survived than were drawn")
        if self.stage == 1 and self.n_a != N1:
            raise ValueError(f"stage 1 is n = {N1}; got {self.n_a}")
        if self.stage == 2 and self.n_a != N2:
            raise ValueError(
                f"stage 2 is the POOLED n = {N2} (§0.3, interpretation A), not a fresh sample; "
                f"got {self.n_a}. A fresh independent 40 reproduces neither published figure."
            )

    @property
    def wilson_a(self) -> tuple[Decimal, Decimal]:
        return wilson_interval(self.k_a, self.n_a)

    @property
    def stratification_discriminated(self) -> bool | None:
        """`k_A/n_A` materially above `k_B/n_B`, or `None` when Stratum B was not generated.

        **Published whatever `k_A` was.** If Stratum B survives at the same rate as Stratum A, the
        human stratification carried no information — which is a finding about the human step, and
        it costs nothing to check.
        """
        if self.n_b == 0:
            return None
        return self.k_a * self.n_b > self.k_b * self.n_a


@dataclass(frozen=True, slots=True)
class Decision:
    """The verdict, and everything needed to recompute it."""

    verdict: Verdict
    k_a: int
    n_a: int
    stage: Literal[1, 2]
    beats_baselines: bool
    wilson_a: tuple[Decimal, Decimal]
    lock_h0: str
    reason: str

    def as_obj(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict, "k_a": self.k_a, "n_a": self.n_a, "stage": self.stage,
            "beats_baselines": self.beats_baselines,
            "wilson_a": [str(self.wilson_a[0]), str(self.wilson_a[1])],
            "lock_h0": self.lock_h0, "reason": self.reason,
        }


def decide(result: SettlingResult, *, lock: Lock) -> Decision:
    """A PURE FUNCTION of `(k_a, stage, beats_baselines)` and the thresholds inside `lock`.

    ```
    stage 1: k_a >= 6 and beats_baselines -> RETAIN
             k_a >= 6 and not beats       -> DELETE      (§0.5, locked at B1)
             3 <= k_a <= 5                -> EXTEND
             k_a <= 2                     -> DELETE
    stage 2: k_a >= 12 and beats_baselines -> RETAIN ; otherwise DELETE
    ```
    """
    if result.stage not in (1, 2):
        raise CriterionExhausted(
            f"stage {result.stage}. There is exactly one extension and there is no third stage. A "
            "third would be re-rolling a criterion that has already been evaluated twice, which is "
            "the thing a pre-registration exists to make impossible rather than merely improper."
        )

    if result.stage == 1:
        if result.k_a <= DELETE1:
            return _decision(
                "DELETE", result, lock,
                f"k = {result.k_a} of {result.n_a} is at or below the pre-registered delete "
                f"threshold of {DELETE1}. This is a publishable result: its interval is "
                f"[{result.wilson_a[0]:.3f}, {result.wilson_a[1]:.3f}].",
            )
        if result.k_a < RETAIN1:
            return _decision(
                "EXTEND", result, lock,
                f"k = {result.k_a} of {result.n_a} falls in the pre-registered extension band "
                f"({DELETE1 + 1}–{RETAIN1 - 1}). Exactly one extension is taken, to a pooled "
                f"n = {N2} at a threshold of {RETAIN2}, and never again.",
            )
        return _retain_or_delete(result, lock, threshold=RETAIN1)

    if result.k_a < RETAIN2:
        return _decision(
            "DELETE", result, lock,
            f"pooled k = {result.k_a} of {result.n_a} is below the pre-registered stage-2 "
            f"threshold of {RETAIN2}.",
        )
    return _retain_or_delete(result, lock, threshold=RETAIN2)


def _retain_or_delete(result: SettlingResult, lock: Lock, *, threshold: int) -> Decision:
    if result.beats_baselines:
        return _decision(
            "RETAIN", result, lock,
            f"k = {result.k_a} of {result.n_a} meets the pre-registered threshold of {threshold} "
            "AND the surviving set beats B0 ∪ B1 ∪ B2 under §0.6's preconditions and the "
            f"{MARGINAL_FLOOR_NUM}/{MARGINAL_FLOOR_DEN} union floor.",
        )
    # §0.5. The sentence is the headline, and it is stronger than "inconclusive".
    return _decision(
        "DELETE", result, lock,
        f"k = {result.k_a} of {result.n_a} meets the threshold of {threshold} and does NOT beat "
        "the free baselines: the model produced checks that survive the gate and none that the "
        "free baselines did not already produce. Ruled DELETE at P12-B1, before the draw — the "
        "extension resolves a sample-size ambiguity, and this is not one.",
    )


def _decision(verdict: Verdict, result: SettlingResult, lock: Lock, reason: str) -> Decision:
    return Decision(
        verdict=verdict, k_a=result.k_a, n_a=result.n_a, stage=result.stage,
        beats_baselines=result.beats_baselines, wilson_a=result.wilson_a,
        lock_h0=lock.h0, reason=reason,
    )


def working(result: SettlingResult) -> tuple[tuple[str, bool, str], ...]:
    """`beats_baselines`' three terms with their arithmetic, for `DECISION.md`."""
    return evaluate_term_by_term(result.per_baseline)
