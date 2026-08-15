"""P12-B4 — `decide()`: the rule, and the signature that has no door in it.

The four inadmissible arguments are not refused at runtime; they are **unrepresentable**. That is a
claim about the function's shape rather than about its body, so it is asserted by introspection —
a body that rejected an override could be edited to accept one in a line, and the review that let
it through would be looking at a diff to a validation branch rather than to a signature.
"""

from __future__ import annotations

import inspect
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.decide import (  # noqa: E402
    INADMISSIBLE_ARGUMENTS,
    CriterionExhausted,
    SettlingResult,
    decide,
)
from cdfc.experiment.marginal import (  # noqa: E402
    BASELINE_IDS,
    MARGINAL_FLOOR_DEN,
    MARGINAL_FLOOR_NUM,
    UNION_ID,
    MarginalKill,
    beats_baselines,
)
from cdfc.experiment.power import DELETE1, N1, N2, RETAIN1, RETAIN2  # noqa: E402
from cdfc.experiment.prereg import Lock  # noqa: E402

LOCK = Lock(fields={"h0": "d0babf29" + "1" * 56, "committed_at": "2026-08-15"})

VERDICTS = frozenset({"RETAIN", "DELETE", "EXTEND"})


def _row(baseline_id: str, observable: int, marginal: int, comparable: bool) -> MarginalKill:
    """One row with `killed_by_candidate_only == marginal`, and every other field made legal.

    `killed_by_candidate` is pinned at `observable` so the set-difference invariant never binds:
    this helper exists to sweep the two fields `beats_baselines` actually reads, and a helper that
    also constrained them would be sweeping a subspace while claiming to sweep the space.
    """
    return MarginalKill(
        baseline_id=baseline_id,
        observable=observable,
        killed_by_baseline=0,
        killed_by_candidate=observable,
        killed_by_candidate_only=marginal,
        comparable=comparable,
        incomparable_reason=None if comparable else "candidate FFR upper bound exceeds baseline",
    )


def _rows(*, marginal: int = 4, observable: int = 10, comparable: bool = True) -> tuple[
    MarginalKill, ...
]:
    return tuple(_row(b, observable, marginal, comparable) for b in BASELINE_IDS)


def _result(k_a: int, *, stage: int = 1, beats: bool = True,
            k_b: int = 0, n_b: int = 0) -> SettlingResult:
    return SettlingResult(
        k_a=k_a,
        n_a=N1 if stage == 1 else N2,
        k_b=k_b,
        n_b=n_b,
        beats_baselines=beats,
        per_baseline=_rows(),
        stage=stage,  # type: ignore[arg-type]
    )


# --- the signature -----------------------------------------------------------------------------


def test_decide__is_a_pure_function() -> None:
    """**The four inadmissible arguments must be UNREPRESENTABLE, not merely disallowed.**

    A `decide(result, lock, override=...)` that raises on `override` is one commit away from a
    `decide` that honours it, and the commit would read as a small relaxation rather than as the
    abandonment of the pre-registration. So the parameter list is asserted to be exactly
    `(result, lock)` with no `*args` and no `**kwargs`: there is no name an argument could arrive
    under at 6pm on a Friday. Purity is asserted alongside it because a function that consulted
    anything outside its arguments would have a door that the signature could not show.
    """
    params = inspect.signature(decide).parameters
    assert list(params) == ["result", "lock"], (
        f"decide takes {list(params)}. Anything beyond (result, lock) is a channel by which a "
        f"reason could enter the decision: {list(INADMISSIBLE_ARGUMENTS)}"
    )
    kinds = {p.kind for p in params.values()}
    assert inspect.Parameter.VAR_KEYWORD not in kinds, "**kwargs accepts every override at once"
    assert inspect.Parameter.VAR_POSITIONAL not in kinds, "*args accepts them positionally"
    assert not ({"override", "rationale", "notes", "reason", "exception"} & set(params))

    first = decide(_result(6, beats=True), lock=LOCK)
    second = decide(_result(6, beats=True), lock=LOCK)
    assert first == second, "two calls on equal inputs disagreed; decide is not a function"
    assert first.as_obj() == second.as_obj()


# --- the rule, point by point ------------------------------------------------------------------


def test_decide__k6_not_beating_baselines_is_delete() -> None:
    """§0.5, ruled at P12-B1 and pinned here so it cannot be re-read after the draw.

    The source rule is silent on `k ≥ 6` without beating the free baselines, and silence is where a
    result gets re-litigated. Extending would be re-rolling a criterion already satisfied on the
    axis the extension addresses — the extension resolves a *sample-size* ambiguity, and this is
    not one. The headline it produces is stronger than "inconclusive", and the reason string is
    asserted because that sentence is the deliverable.
    """
    for k in range(RETAIN1, N1 + 1):
        out = decide(_result(k, beats=False), lock=LOCK)
        assert out.verdict == "DELETE", f"k = {k} with beats_baselines False must DELETE"
        assert "does NOT beat" in out.reason
        assert "none that the free baselines did not already produce" in out.reason
        assert decide(_result(k, beats=True), lock=LOCK).verdict == "RETAIN"


def test_decide__three_to_five_extends() -> None:
    """The extension band is `{3, 4, 5}` and nothing else, whatever the baselines did.

    `beats_baselines` is irrelevant inside the band: the band means *we do not yet have enough
    obligations to tell*, and evaluating criterion 4 on a sample the rule has already declared
    inconclusive would let the free-work comparison decide a case the sample size does not.
    """
    for k in range(DELETE1 + 1, RETAIN1):
        for beats in (True, False):
            out = decide(_result(k, beats=beats), lock=LOCK)
            assert out.verdict == "EXTEND", f"k = {k}, beats = {beats}"
            assert f"pooled n = {N2}" in out.reason and str(RETAIN2) in out.reason
    assert decide(_result(DELETE1, beats=True), lock=LOCK).verdict == "DELETE"
    assert decide(_result(RETAIN1, beats=True), lock=LOCK).verdict == "RETAIN"


def test_decide__stage_three_raises() -> None:
    """There is exactly one extension. A third stage is re-rolling an evaluated criterion.

    This is the failure mode a pre-registration exists to make impossible rather than improper, so
    it raises instead of returning a verdict: a third stage that returned DELETE would still have
    been a third stage, and the run would carry no trace of the re-roll.
    """
    with pytest.raises(CriterionExhausted) as e:
        decide(_result(11, stage=3), lock=LOCK)
    assert "there is no third stage" in str(e.value)


def test_decide__k_zero_is_delete_and_returns_an_interval() -> None:
    """**`k = 0` is a result, not a failed run**, and the interval is what makes it publishable.

    A DELETE reported as a bare zero reads as an experiment that did not work. `[0.000, 0.161]` is
    the first measurement anyone has of whether a frontier model can write a regulator-grade
    executable check, and the bound is the claim — 3 dp because that is what the pre-registration's
    reportable table prints.
    """
    out = decide(_result(0, beats=False), lock=LOCK)
    assert out.verdict == "DELETE"
    assert (f"{out.wilson_a[0]:.3f}", f"{out.wilson_a[1]:.3f}") == ("0.000", "0.161")
    assert "publishable result" in out.reason
    assert out.lock_h0 == LOCK.h0, "the decision must carry the lock it was taken under"
    assert decide(_result(0, beats=True), lock=LOCK).verdict == "DELETE", (
        "beating the baselines on zero survivors cannot rescue a k below the delete threshold"
    )


# --- criterion 4, as arithmetic ----------------------------------------------------------------


def _reference(observable: int, marginals: tuple[int, int, int, int],
               comparables: tuple[bool, bool, bool, bool]) -> bool:
    """G-SETTLE criterion 4, written a second time and deliberately differently.

    The floor is expressed as a rational comparison `m ≥ (1/10)·O` rather than as the source's
    integer cross-multiplication `m·10 ≥ 1·O`. A reference that restated the implementation would
    agree with it by construction, including where both are wrong.
    """
    if not all(comparables):
        return False
    if not all(m > 0 for m in marginals[:3]):
        return False
    return Fraction(marginals[3]) >= Fraction(MARGINAL_FLOOR_NUM, MARGINAL_FLOOR_DEN) * observable


def test_decide__beats_baselines_is_arithmetic_not_prose() -> None:
    """EXHAUSTIVE over the row space `decide()` reads, because prose is where this criterion dies.

    F30: a criterion a reader can *interpret* is a criterion that gets interpreted in the direction
    of the result. `union.killed_by_candidate_only > 0` — the reading the prose most naturally
    supports — makes criterion 4 satisfiable by any candidate that kills one mutant the free work
    missed, which is *"is not identical to free work"*, not *"beats free work"*. So every point of
    the small space is checked against an independently written reference, including the exact
    union floor where `10·m == O` must be MET (`≥`, not `>`) and the point one below it must not.
    """
    boundary_seen = False
    for observable in range(0, 13):
        cache = {
            (b, m, c): _row(b, observable, m, c)
            for b in BASELINE_IDS
            for m in range(observable + 1)
            for c in (True, False)
        }
        for m0, m1, m2, mu in product(range(observable + 1), repeat=4):
            for c0, c1, c2, cu in product((True, False), repeat=4):
                rows = (
                    cache[("B0", m0, c0)], cache[("B1", m1, c1)],
                    cache[("B2", m2, c2)], cache[(UNION_ID, mu, cu)],
                )
                got = beats_baselines(rows)
                want = _reference(observable, (m0, m1, m2, mu), (c0, c1, c2, cu))
                assert got is want, (
                    f"O={observable} marginals={(m0, m1, m2, mu)} "
                    f"comparable={(c0, c1, c2, cu)}: got {got}, reference says {want}"
                )
                if mu * MARGINAL_FLOOR_DEN == observable and observable > 0:
                    boundary_seen = True
    assert boundary_seen, "the union floor's exact boundary was never reached by the sweep"

    exact = (_row("B0", 10, 1, True), _row("B1", 10, 1, True),
             _row("B2", 10, 1, True), _row(UNION_ID, 10, 1, True))
    assert beats_baselines(exact) is True, (
        "10 × 1 >= 1 × 10 is the floor MET. A `>` here would reject the boundary case the "
        "pre-registration declares sufficient, and the criterion would be a different criterion."
    )
    below = exact[:3] + (_row(UNION_ID, 11, 1, True),)
    assert beats_baselines(below) is False, "one observable more and the floor is not met"


# --- what is published either way ---------------------------------------------------------------


def test_decide__stratification_discriminative_value_is_published_either_way() -> None:
    """`None` when Stratum B was never generated; a bool when it was — never a quiet `False`.

    If B survives at A's rate, the human stratification carried no information. That is a finding
    about the human step and it costs nothing to check, so the value is published whatever `k_A`
    was. Collapsing "not generated" into `False` would report the absence of a stratum as evidence
    that stratification did not discriminate, which is the absence-as-silence defect this project
    is named for.
    """
    assert _result(6, n_b=0, k_b=0).stratification_discriminated is None

    assert _result(6, k_b=1, n_b=10).stratification_discriminated is True   # 6/20 > 1/10
    assert _result(6, k_b=3, n_b=10).stratification_discriminated is False  # 6/20 == 3/10
    assert _result(6, k_b=9, n_b=10).stratification_discriminated is False
    assert _result(0, k_b=0, n_b=10).stratification_discriminated is False

    for k_a, k_b in ((0, 0), (6, 1), (6, 3), (20, 10)):
        value = _result(k_a, k_b=k_b, n_b=10).stratification_discriminated
        assert isinstance(value, bool), f"k_a={k_a}, k_b={k_b} published {value!r}, not a bool"
