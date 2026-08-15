"""P12-B1 — the three properties of the power arithmetic that no table of pinned figures can hold.

`tests/unit/test_experiment_power.py` pins the numbers `experiments/E6/PREREGISTRATION.md`
publishes. Pinned numbers catch a value that moved; they do not catch a distribution that is not a
distribution, an operating characteristic that rewards a worse world, or an interval that fails to
narrow with evidence. Those are the shape of the arithmetic rather than any point in it, and they
are what is asserted here — over arbitrary exact rational `p`, because `p` is a `Fraction` on this
path by design and a property test that fed it floats would be testing a different module.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.power import cdf, retain_probability, sf, wilson_interval  # noqa: E402

PROFILE = settings(
    max_examples=50, deadline=None, derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)

# `p` as an exact rational in the open interval (0, 1). Never `Fraction(0.3)`, which is
# 5404319552844595/18014398509481984 and is not the number anybody wrote down.
PROBS = st.fractions(
    min_value=Fraction(1, 1000), max_value=Fraction(999, 1000), max_denominator=1000
)

SIZES = st.integers(min_value=1, max_value=60)


@PROFILE
@given(SIZES, PROBS)
@example(20, Fraction(3, 10))  # the §0.2 correction's own cell
def test_prop__cdf_and_sf_are_exact_complements(n: int, p: Fraction) -> None:
    """**`cdf(k) + sf(k+1) == 1` EXACTLY**, `cdf` non-decreasing, `sf` non-increasing.

    In binary floating point the complement holds only to within a few ULP, and the delete column
    of the operating characteristic is computed *as* a complement — so a residue there is a residue
    in a published figure. The monotonicity is the other half: a `cdf` that dipped, or an `sf` that
    rose, would mean the terms are not a probability mass function at all, and every threshold
    downstream would be reading a number that is not a probability.
    """
    for k in range(0, n):
        assert cdf(k, n, p) + sf(k + 1, n, p) == Fraction(1), f"complement failed at k={k}"

    prev_cdf = cdf(-1, n, p)
    prev_sf = sf(0, n, p)
    assert prev_cdf == Fraction(0) and prev_sf == Fraction(1)
    for i in range(0, n + 1):
        cur_cdf, cur_sf = cdf(i, n, p), sf(i, n, p)
        assert cur_cdf >= prev_cdf, f"cdf fell between {i - 1} and {i}"
        assert cur_sf <= prev_sf, f"sf rose between {i - 1} and {i}"
        assert Fraction(0) <= cur_cdf <= Fraction(1)
        prev_cdf, prev_sf = cur_cdf, cur_sf
    assert cdf(n, n, p) == Fraction(1)


@PROFILE
@given(PROBS, PROBS)
@example(Fraction(3, 20), Fraction(7, 20))  # the two rates the pre-registration publishes
def test_prop__retain_probability_is_non_decreasing_in_p(a: Fraction, b: Fraction) -> None:
    """**A better world must not be retained less often.**

    `p` is the true per-obligation survival rate, so `retain_probability` is the two-stage rule's
    power curve; if it ever fell as `p` rose, the rule would punish the very evidence it exists to
    detect and the published operating characteristic would be uninterpretable. This is the one
    property that catches a swapped inequality inside the extension branch — an error that leaves
    every individual cell a valid probability and only shows up as the curve bending the wrong way.
    """
    assume(a != b)
    low, high = (a, b) if a < b else (b, a)
    assert retain_probability(low) <= retain_probability(high), (
        f"retaining fell from p={low} to p={high}: a higher true survival rate retained LESS often"
    )
    assert Fraction(0) <= retain_probability(low) <= Fraction(1)


@PROFILE
@given(st.integers(min_value=1, max_value=59), st.integers(min_value=2, max_value=60))
@example(6, 20)  # 6/20 -> 12/40: the extension's whole justification
def test_prop__doubling_the_sample_narrows_the_wilson_interval(k: int, n: int) -> None:
    """**Twice the evidence at the same observed rate is a strictly narrower interval.**

    This is the entire argument for the extension: `12/40` and `6/20` are the same point estimate,
    and only the width distinguishes them. If widening were possible anywhere in the range the
    experiment can reach, "the extension is sharper" would be a claim about two particular numbers
    rather than about drawing more, and the pre-registration's budget for stage 2 would be buying
    nothing.
    """
    assume(0 < k < n)
    lo1, hi1 = wilson_interval(k, n)
    lo2, hi2 = wilson_interval(2 * k, 2 * n)
    assert (hi2 - lo2) < (hi1 - lo1), f"{2 * k}/{2 * n} is not narrower than {k}/{n}"
    # Narrower is not enough on its own — an interval that slid sideways could also be narrower
    # while excluding rates the smaller sample admitted. It must shrink INWARD, from both ends.
    assert lo1 <= lo2 and hi2 <= hi1, f"{2 * k}/{2 * n} is not contained in {k}/{n}"
