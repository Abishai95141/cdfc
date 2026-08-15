"""P12-B4 — `decide()` partitions its outcome space, checked at every point of it.

**Exhaustive rather than sampled, and deliberately.** The space is `k ∈ [0, 40] × stage ∈ {1, 2} ×
beats ∈ {T, F}` — 164 points, of which 124 are constructible. A property test that could have been
exhaustive and was not is weaker than it needed to be: sampling buys nothing here except the
possibility that the one unvisited point is the boundary, and every boundary in this rule (`≤ 2`,
`< 6`, `≥ 6`, `< 12`, `≥ 12`, `k = n`) is an integer comparison somebody could have written with the
wrong inequality. Hypothesis is the right tool for spaces too large to walk; this one is not.

The three refusals are part of the partition and are asserted as such: a point outside the valid
space must RAISE, never fall through to a verdict. A rule with a default branch is a rule with an
answer for a question it was never asked.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.decide import (  # noqa: E402
    CriterionExhausted,
    SettlingResult,
    decide,
)
from cdfc.experiment.marginal import BASELINE_IDS, MarginalKill  # noqa: E402
from cdfc.experiment.power import DELETE1, N1, N2, RETAIN1, RETAIN2  # noqa: E402
from cdfc.experiment.prereg import Lock  # noqa: E402

LOCK = Lock(fields={"h0": "d0babf29" + "2" * 56, "committed_at": "2026-08-15"})

VERDICTS = ("RETAIN", "DELETE", "EXTEND")

ROWS = tuple(
    MarginalKill(baseline_id=b, observable=10, killed_by_baseline=1, killed_by_candidate=5,
                 killed_by_candidate_only=2, comparable=True)
    for b in BASELINE_IDS
)

N_FOR_STAGE = {1: N1, 2: N2}


def _result(k: int, stage: int, beats: bool, *, n_a: int | None = None) -> SettlingResult:
    return SettlingResult(
        k_a=k, n_a=N_FOR_STAGE.get(stage, N2) if n_a is None else n_a,
        k_b=0, n_b=0, beats_baselines=beats, per_baseline=ROWS,
        stage=stage,  # type: ignore[arg-type]
    )


def test_prop__decide_partitions_the_outcome_space() -> None:
    """Every constructible point lands in exactly one verdict, and the three preimages cover it.

    "Exactly one" is not tautological here even though a function returns one value: the assertion
    is that the *rule* has no point it cannot classify and no point it classifies by falling off
    the end of a chain of `if`s. The preimages are collected and their union compared to the whole
    space, so a branch that quietly returned `None`, raised, or was unreachable shows up as a hole
    rather than as a test that happened not to visit it.
    """
    space = [(k, stage, beats)
             for stage in (1, 2) for k in range(0, N2 + 1) for beats in (True, False)]
    assert len(space) == 164

    preimage: dict[str, set[tuple[int, int, bool]]] = {v: set() for v in VERDICTS}
    unconstructible: set[tuple[int, int, bool]] = set()

    for k, stage, beats in space:
        n_a = N_FOR_STAGE[stage]
        if k > n_a:
            with pytest.raises(ValueError) as e:
                _result(k, stage, beats)
            assert "more obligations survived than were drawn" in str(e.value)
            unconstructible.add((k, stage, beats))
            continue
        out = decide(_result(k, stage, beats), lock=LOCK)
        assert out.verdict in VERDICTS, f"k={k} stage={stage} beats={beats} -> {out.verdict!r}"
        preimage[out.verdict].add((k, stage, beats))
        assert out.k_a == k and out.n_a == n_a and out.stage == stage
        assert out.reason, "a verdict with no reason is a number nobody can check"

    covered = preimage["RETAIN"] | preimage["DELETE"] | preimage["EXTEND"]
    assert covered | unconstructible == set(space), "points the rule classified nowhere"
    assert len(covered) + len(unconstructible) == len(space), "a point landed in two preimages"
    assert len(covered) == 124
    assert all(preimage[v] for v in VERDICTS), "a verdict the rule can never reach is dead code"


def test_prop__the_extension_exists_once_and_only_at_stage_one() -> None:
    """EXTEND is reachable at stage 1 and nowhere else — and stage 3 raises rather than deciding.

    Two guards, one rule. Inside the space, stage 2 must never return EXTEND: an extension reached
    from an extension is the re-roll the pre-registration exists to prevent, and it would look like
    a verdict rather than like a violation. Outside the space, a third stage raises — because a
    third stage that returned DELETE would still have been a third stage and the published record
    would carry no trace of it.
    """
    for k in range(0, N1 + 1):
        for beats in (True, False):
            got = decide(_result(k, 1, beats), lock=LOCK).verdict
            assert (got == "EXTEND") is (DELETE1 < k < RETAIN1), f"k={k} beats={beats} -> {got}"

    for k in range(0, N2 + 1):
        for beats in (True, False):
            got = decide(_result(k, 2, beats), lock=LOCK).verdict
            assert got != "EXTEND", f"stage 2 extended at k={k}: there is no second extension"
            assert got == ("RETAIN" if (k >= RETAIN2 and beats) else "DELETE")

    for stage in (3, 4, 99):
        with pytest.raises(CriterionExhausted):
            decide(_result(11, stage, True), lock=LOCK)


def test_prop__a_stage_and_a_denominator_that_disagree_are_refused() -> None:
    """`n_a` is 20 at stage 1 and the POOLED 40 at stage 2 — never a fresh independent 40 (§0.3).

    Interpretation B reproduces neither published figure, so a stage-2 result carrying a fresh
    `n = 40` would be evaluated against a threshold computed for a different sampling design. It is
    refused at construction, which is the only place it can be caught: by the time `decide()` sees
    `k_a` and `stage`, a pooled 40 and a fresh 40 are the same two integers.
    """
    with pytest.raises(ValueError) as e:
        _result(6, 1, True, n_a=N2)
    assert f"stage 1 is n = {N1}" in str(e.value)

    with pytest.raises(ValueError) as e:
        _result(6, 2, True, n_a=N1)
    assert "POOLED" in str(e.value) and "fresh independent 40" in str(e.value)


def test_prop__retain_is_upward_closed_in_k_when_the_baselines_are_beaten() -> None:
    """Once a candidate set beats free work, more survivors can never turn a RETAIN into a DELETE.

    The one monotonicity this rule actually has, and the one an off-by-one would break: with the
    `k ≥ 6` and `k ≥ 12` comparisons written as `>` by mistake, the threshold point flips and the
    retain set stops being upward-closed at exactly one value of `k` — which is the value a
    sampled property test is most likely to miss and the one the whole experiment turns on.
    """
    for stage, threshold in ((1, RETAIN1), (2, RETAIN2)):
        verdicts = [decide(_result(k, stage, True), lock=LOCK).verdict
                    for k in range(0, N_FOR_STAGE[stage] + 1)]
        retain = [k for k, v in enumerate(verdicts) if v == "RETAIN"]
        assert retain == list(range(threshold, N_FOR_STAGE[stage] + 1))
        assert verdicts[threshold] == "RETAIN" and verdicts[threshold - 1] != "RETAIN"
