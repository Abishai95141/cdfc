"""P12-B1 — the power arithmetic, and the one figure it corrects.

`src/cdfc/experiment/power.py` recomputes every number `experiments/E6/PREREGISTRATION.md`
publishes, in exact rationals, because its superseded ancestor computed them in binary floats and
agreed to three decimal places everywhere except at `P(X ≤ 2 | n = 20, p = 0.30)` — the one figure
the plan corrects. These tests exist to hold that correction, the two-arm interpretation decision
behind the operating characteristic, and the absence of `float` on the path that renders the
committed markdown. A number nobody can re-derive is a pre-registration nobody can check.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.power import (  # noqa: E402
    DELETE1,
    N1,
    N2,
    RETAIN1,
    RETAIN2,
    ExtensionNotAvailable,
    _r3,
    cdf,
    extension_fires,
    extension_retain_probability,
    inverse_sampling_estimate,
    pmf,
    power_table,
    retain_probability,
    retain_probability_fresh40,
    sf,
    wilson_interval,
)


# --- exactness -------------------------------------------------------------------------------


def test_power__cdf_at_n_is_exactly_one() -> None:
    """`P(X ≤ n)` is **`Fraction(1)`, not `0.9999999999999998`**.

    This is the property the whole module is written in `Fraction` to obtain. Summed in binary
    floating point the twenty-one binomial terms do not close on one, and every quantity derived by
    complement — `sf`, the delete column, `1 − retain_probability` — inherits the residue. Asserting
    against `1.0` would pass under a float implementation and check nothing.
    """
    for p in (Fraction(3, 20), Fraction(1, 3), Fraction(7, 20), Fraction(99, 100)):
        got = cdf(N1, N1, p)
        assert got == Fraction(1)
        assert isinstance(got, Fraction) and not isinstance(got, float)
        # Summing the terms is the path that would carry the residue; it must close too.
        assert sum((pmf(i, N1, p) for i in range(N1 + 1)), Fraction(0)) == Fraction(1)
    assert cdf(N2, N2, Fraction(3, 20)) == Fraction(1)
    assert sf(0, N1, Fraction(3, 20)) == Fraction(1)


def test_power__delete_boundary_at_p030_is_0035() -> None:
    """**The §0.2 correction.** `spec/04-path.md` printed `0.036`; the exact value is `0.035483…`.

    Every other figure in that table reproduces, which is why this one is dangerous: a float
    recomputation agrees to three decimal places everywhere it is checked and disagrees exactly
    where nobody looks. Both halves are asserted — the rendered string a reader sees, and the strict
    inequality against `36/1000` that says the spec's figure is *wrong* rather than merely rounded
    differently. Asserting only the string would pass on a value of `0.0354999` that had been
    rounded into place.
    """
    exact = cdf(DELETE1, N1, Fraction(3, 10))
    assert _r3(exact) == "0.035"
    assert exact < Fraction(36, 1000), f"the spec's 0.036 is not merely a rounding of {exact}"
    assert Fraction(354, 10_000) < exact < Fraction(355, 10_000)
    # And the correction survives the renderer: the committed table carries 0.035 in this cell.
    row = next(r for r in power_table().stage1 if r[0] == Fraction(3, 10))
    assert _r3(row[2]) == "0.035"


# --- the two-arm interpretation decision -------------------------------------------------------


def test_power__pooled_interpretation_reproduces_the_spec() -> None:
    """§0.3 was settled by arithmetic, and **the losing arm must be shown to lose.**

    Two readings of "draw 20 more" were available: pool them into 40 (A), or take a fresh
    independent 40 (B). A publishes `0.929` and `0.134` for the delete column at `p = 0.15` and
    `p = 0.35`; B publishes `0.926` and `0.060` and so reproduces neither. Asserting only that A
    reproduces the spec checks one arm of a two-arm decision — it would pass in a world where B also
    reproduced it, and the choice recorded in the pre-registration would then be unforced.
    """
    assert _r3(Fraction(1) - retain_probability(Fraction(3, 20))) == "0.929"
    assert _r3(Fraction(1) - retain_probability(Fraction(7, 20))) == "0.134"

    fresh_low = _r3(Fraction(1) - retain_probability_fresh40(Fraction(3, 20)))
    fresh_high = _r3(Fraction(1) - retain_probability_fresh40(Fraction(7, 20)))
    assert fresh_low == "0.926" and fresh_high == "0.060"
    assert fresh_low != "0.929" and fresh_high != "0.134", "interpretation B must NOT reproduce"
    assert retain_probability(Fraction(7, 20)) != retain_probability_fresh40(Fraction(7, 20))


def test_power__extension_band_is_exactly_three_four_five() -> None:
    """`≤ 2` deletes, `≥ 6` retains, and **only `{3, 4, 5}` is unresolved**.

    An off-by-one at either end is silent: it does not change a table's shape, it prices a branch
    the decision rule never takes and folds that price into the operating characteristic. The
    refusal outside the band is asserted too, because a function that answered anyway would let the
    error through arithmetic instead of through an exception.
    """
    assert {k for k in range(0, N1 + 1) if extension_fires(k)} == {3, 4, 5}
    assert (DELETE1, RETAIN1) == (2, 6)

    for k in (3, 4, 5):
        assert isinstance(extension_retain_probability(k, Fraction(1, 4)), Fraction)
    for k in set(range(0, N1 + 1)) - {3, 4, 5}:
        with pytest.raises(ExtensionNotAvailable):
            extension_retain_probability(k, Fraction(1, 4))
    # The refusal names which side of the band it fell on, so the caller learns the branch it
    # asked to price and not merely that it asked for something.
    with pytest.raises(ExtensionNotAvailable) as low:
        extension_retain_probability(0, Fraction(1, 4))
    assert "DELETE" in str(low.value)
    with pytest.raises(ExtensionNotAvailable) as high:
        extension_retain_probability(RETAIN1, Fraction(1, 4))
    assert "RETAIN" in str(high.value)


def test_power__the_extension_is_sharper_in_both_directions() -> None:
    """**"Sharper" is not "harder", and only a two-directional assertion can tell them apart.**

    Pooled `≥ 12 of 40` retains *less* often than `≥ 6 of 20` at a low true rate and *more* often at
    a high one — it discriminates better on both sides. A rule that had merely been made uniformly
    harder would pass a test that checked the low-`p` direction alone, and the pre-registration's
    claim about the extension would be false while its test stayed green.
    """
    low, high = Fraction(3, 20), Fraction(7, 20)
    assert sf(RETAIN2, N2, low) < sf(RETAIN1, N1, low), "must be harder to retain at low p"
    assert sf(RETAIN2, N2, high) > sf(RETAIN1, N1, high), "must be EASIER to retain at high p"
    assert (_r3(sf(RETAIN2, N2, low)), _r3(sf(RETAIN1, N1, low))) == ("0.012", "0.067")
    assert (_r3(sf(RETAIN2, N2, high)), _r3(sf(RETAIN1, N1, high))) == ("0.795", "0.755")


# --- the estimators and the intervals ----------------------------------------------------------


def test_power__inverse_sampling_estimator_is_a_minus_one_over_n_minus_one() -> None:
    """Under inverse sampling `a/n` is **biased upward**, and the direction is the reason to publish
    both. The draw stops at a fixed number of successes, not a fixed number of trials, so the last
    trial is a success by construction and the naive ratio counts it. A test that checked only the
    formula would pass on `(a+1)/(n+1)`, which is also "not `a/n`" and corrects the bias the wrong
    way. `n == 1` is refused rather than falling back to the naive ratio, because the fallback would
    publish the biased number under the unbiased label.
    """
    naive, unbiased = inverse_sampling_estimate(20, 101)
    assert naive == Fraction(20, 101) and unbiased == Fraction(19, 100)
    assert unbiased < naive, "the unbiased estimator must correct DOWNWARD"
    assert isinstance(naive, Fraction) and isinstance(unbiased, Fraction)

    with pytest.raises(ValueError, match="unbiased"):
        inverse_sampling_estimate(1, 1)
    with pytest.raises(ValueError):
        inverse_sampling_estimate(0, 10)
    with pytest.raises(ValueError):
        inverse_sampling_estimate(11, 10)


def test_power__wilson_reproduces_the_four_reportable_intervals() -> None:
    """The four intervals that go on a slide, to the three places they are printed at.

    `0/20` is the one that matters most: it is a **publishable result**, and its interval is what
    stops a reader treating a point estimate of zero as evidence of zero. `12/40` against `6/20` is
    the extension's payoff — a narrower interval at the same observed rate — and pinning both here
    means a change to `cdfc.qualify.wilson`, which this module delegates to rather than
    re-implementing, cannot silently move the experiment's published numbers.
    """
    expected = {
        (0, 20): ("0.000", "0.161"),
        (2, 20): ("0.028", "0.301"),
        (6, 20): ("0.145", "0.519"),
        (12, 40): ("0.181", "0.454"),
    }
    for (k, n), (lo_s, hi_s) in expected.items():
        lo, hi = wilson_interval(k, n)
        assert (f"{lo:.3f}", f"{hi:.3f}") == (lo_s, hi_s), f"{k}/{n} moved"
    assert wilson_interval(12, 40)[1] - wilson_interval(12, 40)[0] < (
        wilson_interval(6, 20)[1] - wilson_interval(6, 20)[0]
    ), "the extension's interval must be narrower at the same observed rate"


def test_power__there_is_no_float_on_the_table_path() -> None:
    """**No `float` reaches the object the pre-registration is rendered from.** A single one is
    enough: it would be summed with exact rationals, silently widen to binary, and the table would
    then reproduce on the machine that generated it and nowhere else. The probability cells are
    `Fraction`, the intervals are `Decimal` (borrowed from `cdfc.qualify.wilson`, which bans `math`
    for the same reason), and nothing anywhere in the structure is a `float`.
    """
    table = power_table()

    for row in table.stage1:
        assert len(row) == 5
        assert all(isinstance(cell, Fraction) for cell in row), row
    for row in table.extension:
        assert len(row) == 4
        assert all(isinstance(cell, Fraction) for cell in row), row
    for row in table.operating:
        assert len(row) == 3
        assert all(isinstance(cell, Fraction) for cell in row), row
    for k, n, lo, hi, note in table.reportable:
        assert isinstance(k, int) and isinstance(n, int)
        assert isinstance(lo, Decimal) and isinstance(hi, Decimal), (lo, hi)
        assert isinstance(note, str)

    def walk(node: object) -> None:
        assert not isinstance(node, float), f"a float reached the table path: {node!r}"
        if isinstance(node, (tuple, list)):
            for child in node:
                walk(child)

    walk((table.stage1, table.extension, table.operating, table.reportable))

    # And the renderer does not reintroduce one: a decimal cell is `0.15` (a grid point) or `0.ddd`
    # (a probability), never a float repr such as `0.03548313229846868`.
    for line in table.as_markdown().splitlines():
        for cell in (c.strip().strip("`") for c in line.split("|")):
            if cell[:2] == "0." and cell.replace(".", "").isdigit():
                assert len(cell) <= 5, f"a float-shaped probability was rendered: {cell!r}"
