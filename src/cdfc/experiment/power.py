"""P12-B1 — the power arithmetic. **Exact rational binomial. There is no float on this path.**

This module produces every figure `experiments/E6/PREREGISTRATION.md` carries, and
`tests/contract/test_contract__e6_power.py` asserts the committed markdown equals this function's
output. A pre-registration whose numbers nobody can re-derive is a pre-registration nobody can
check.

## Why `Fraction` and not `float`

`research/scripts/e6_power.py` — this module's superseded ancestor — computes the same table in
binary floating point. It agrees to three decimal places, which is all the table prints, and that
is exactly the problem: **at three decimal places a float and an exact rational agree until they
do not**, and the one figure where it matters is the one the plan corrects. `P(X ≤ 2 | n=20,
p=0.30)` is `0.035483…`; the specification printed `0.036`. Recomputing it in the same arithmetic
that produced the error is not a check. So the binomial here is
`C(n,k) · p^k · (1−p)^(n−k)` over `Fraction`, with `p` a `Fraction` and never a decimal literal —
`Fraction(3,10)`, not `Fraction(0.3)`, which is 5404319552844595/18014398509481984.

## Wilson is IMPORTED, not re-implemented

`cdfc.qualify.wilson` already computes the Wilson score interval in `Decimal` with `math` banned
from its import closure, because the value lands in a byte-identical attestation. Writing a second
one here would mean this module's intervals and G4's intervals could disagree, and then the
experiment's `k/n` and the registry's FFR would be two different statistics wearing one name.
**The plan's `-> tuple[float, float]` signature is superseded by the module that exists**, and the
reason is recorded in `docs/decisions/D-P12-01-power-is-exact.md`.

## What the tables mean, since three of them are easy to misread

- The celebrated `0.933` at `p = 0.15` is **`P(X ≤ 5)`** — the probability the *retain* threshold
  is not met. Outright deletion at stage 1 is `P(X ≤ 2) = 0.405`.
- **The extension is the modal path** at `p = 0.15–0.25`, firing 0.528, 0.598 and 0.526 of the
  time. It is the expected case, not a contingency, and it is budgeted as one.
- **"The extension is sharper" is not "the extension is harder."** Pooled `≥ 12 of 40` retains
  *less* often at low `p` (0.012 vs 0.067 at `p = 0.15`) and *more* often at high `p` (0.795 vs
  0.755 at `p = 0.35`). It discriminates better in both directions; saying it is uniformly harder
  would be wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from math import comb
from typing import Final

from cdfc.qualify.wilson import wilson as _wilson_decimal

# The decision rule, as integers. A threshold that moves must move here, in a diff.
N1: Final[int] = 20
RETAIN1: Final[int] = 6
DELETE1: Final[int] = 2
N2: Final[int] = 40
RETAIN2: Final[int] = 12

# The true per-obligation survival rates the operating characteristic is evaluated at. Exact
# rationals: `Fraction(3, 20)`, never `Fraction(0.15)`.
P_GRID: Final[tuple[Fraction, ...]] = (
    Fraction(3, 20), Fraction(1, 5), Fraction(1, 4), Fraction(3, 10), Fraction(7, 20),
)

# The four `(k, n)` pairs whose intervals are reportable, with the note each carries.
REPORTABLE: Final[tuple[tuple[int, int, str], ...]] = (
    (0, 20, "**`k = 0` is a publishable result, and this is its interval**"),
    (2, 20, "the delete boundary"),
    (6, 20, "the retain boundary"),
    (12, 40, "the extension's retain boundary — half the width at the same rate"),
)


class ExtensionNotAvailable(ValueError):
    """A stage-2 quantity was asked for at a stage-1 outcome that does not extend."""


def pmf(k: int, n: int, p: Fraction) -> Fraction:
    """`P(X = k)` for `X ~ Binomial(n, p)`. Exact."""
    if not 0 <= k <= n:
        return Fraction(0)
    return Fraction(comb(n, k)) * p**k * (1 - p) ** (n - k)


def cdf(k: int, n: int, p: Fraction) -> Fraction:
    """`P(X ≤ k)`. Exact — `cdf(n, n, p)` is `Fraction(1)`, not `1.0 - 1e-16`."""
    if k < 0:
        return Fraction(0)
    if k >= n:
        return Fraction(1)
    return sum((pmf(i, n, p) for i in range(0, k + 1)), Fraction(0))


def sf(k: int, n: int, p: Fraction) -> Fraction:
    """`P(X ≥ k)`. The survival function at `k`, **inclusive** — `sf(0, n, p) == 1`."""
    return Fraction(1) - cdf(k - 1, n, p)


def extension_fires(k: int) -> bool:
    """Stage 1 leaves `{3, 4, 5}` unresolved, and only those. `≤ 2` deletes, `≥ 6` retains."""
    return DELETE1 < k < RETAIN1


def extension_retain_probability(k: int, p: Fraction) -> Fraction:
    """Given stage-1 `X = k`, the probability the pooled 40 reaches `≥ 12`.

    **Interpretation A (§0.3): the extension draws 20 MORE and the threshold is evaluated over the
    pooled 40.** The alternative — a fresh independent 40 — reproduces neither of the two figures
    the specification publishes, and `retain_probability` below is where that is settled by
    arithmetic rather than by preference.
    """
    if not extension_fires(k):
        raise ExtensionNotAvailable(
            f"stage 1 X = {k} does not extend: {DELETE1} < X < {RETAIN1} is the extension band, and "
            f"X = {k} is already {'a DELETE' if k <= DELETE1 else 'a RETAIN'} at stage 1. Asking for "
            "the extension's probability here would price a branch the rule does not take."
        )
    return sf(RETAIN2 - k, N1, p)


def retain_probability(p: Fraction) -> Fraction:
    """The two-stage operating characteristic under **interpretation A**. Exact.

    Retain at stage 1 (`X ≥ 6`), or extend (`3 ≤ X ≤ 5`) and reach `X + Y ≥ 12` over the pooled 40.
    """
    total = Fraction(0)
    for x in range(0, N1 + 1):
        px = pmf(x, N1, p)
        if x >= RETAIN1:
            total += px
        elif extension_fires(x):
            total += px * extension_retain_probability(x, p)
    return total


def retain_probability_fresh40(p: Fraction) -> Fraction:
    """**Interpretation B, kept because it is what settles §0.3 — and it is never used elsewhere.**

    A fresh independent `n = 40` sample at `≥ 12`. It reproduces neither published figure —
    **and the published figures are P(DELETE), so they are the complements of what this function
    returns.** At `p = 0.15` interpretation A deletes 0.929 of the time and B deletes 0.926; at
    `p = 0.35` A deletes 0.134 and B deletes 0.060. A reproduces both exactly and B reproduces
    neither, which is the whole argument for interpretation A. Saying "0.926 vs 0.929" without
    naming the direction invites a reader to compare a retain probability with a delete one. It exists so that `test_power__pooled_interpretation_reproduces_the_spec` can
    assert the losing interpretation **loses**, rather than asserting only that the winner wins —
    a test that checks one arm of a two-arm decision has checked half of it.
    """
    return sf(RETAIN1, N1, p) + (cdf(RETAIN1 - 1, N1, p) - cdf(DELETE1, N1, p)) * sf(RETAIN2, N2, p)


def wilson_interval(k: int, n: int) -> tuple[Decimal, Decimal]:
    """`(lo, hi)`, 6 dp, clamped — **delegated to `cdfc.qualify.wilson`, never recomputed here.**

    Two Wilson implementations in one repository is two statistics wearing one name, and the one
    that would drift is the one nobody is looking at.
    """
    _point, lo, hi = _wilson_decimal(k, n)
    return lo, hi


def inverse_sampling_estimate(a: int, n: int) -> tuple[Fraction, Fraction]:
    """`(naive, unbiased)` for `|A| / |drawn|` under **inverse (negative-binomial) sampling** (§0.4).

    The draw continues until a fixed number of *successes* (`|A| = 20`), not for a fixed number of
    trials. Under that stopping rule `a/n` is **biased upward** and the unbiased estimator is
    `(a − 1)/(n − 1)`. Both are returned because both are published, each labelled; and any
    binomial interval computed on them carries `INVERSE_SAMPLING_LABEL`, because a Wilson interval
    is **not exact** here and printing it bare would borrow a guarantee this design does not have.
    """
    if n <= 0 or a <= 0:
        raise ValueError(
            f"a={a}, n={n}: the decidable fraction is undefined before the draw completes. A draw "
            "that returned short would be a truncated denominator, which is NC-M03."
        )
    if a > n:
        raise ValueError(f"a={a} > n={n}: Stratum A cannot exceed the drawn set that contains it")
    if n == 1:
        raise ValueError(
            "n == 1: the unbiased inverse-sampling estimator (a−1)/(n−1) is undefined at one trial, "
            "and returning the naive ratio in its place would silently publish the biased number "
            "under the unbiased label"
        )
    return Fraction(a, n), Fraction(a - 1, n - 1)


INVERSE_SAMPLING_LABEL: Final[str] = "APPROXIMATE — inverse sampling, interval not exact"


@dataclass(frozen=True, slots=True)
class PowerTable:
    """The exact object rendered into `PREREGISTRATION.md`. Every cell is a `Fraction`."""

    stage1: tuple[tuple[Fraction, Fraction, Fraction, Fraction, Fraction], ...]
    extension: tuple[tuple[Fraction, Fraction, Fraction, Fraction], ...]
    operating: tuple[tuple[Fraction, Fraction, Fraction], ...]
    reportable: tuple[tuple[int, int, Decimal, Decimal, str], ...]

    def as_markdown(self) -> str:
        """The four tables, exactly as `PREREGISTRATION.md` carries them.

        **One renderer, so the document and the generator cannot drift.** The contract test parses
        the committed markdown back out and compares set-equal to this function's output; a table
        edited by hand fails the build rather than the review.
        """
        out: list[str] = []
        out.append(
            "**Stage 1, `n = 20`, retain at `≥ 6`, delete at `≤ 2`:**\n\n"
            "| True per-obligation survival rate `p` | `P(X ≤ 5)` retain threshold not met "
            "| `P(X ≤ 2)` outright delete | `P(3 ≤ X ≤ 5)` extension fires | `P(X ≥ 6)` retain |\n"
            "|---:|---:|---:|---:|---:|"
        )
        for p, le5, le2, band, ge6 in self.stage1:
            out.append(f"| {_p(p)} | {_r3(le5)} | {_r3(le2)} | {_r3(band)} | {_r3(ge6)} |")
        out.append(
            "\n**The extension branch — given stage-1 `X ∈ {3,4,5}`, draw 20 more and retain iff "
            "`X + Y ≥ 12`:**\n\n| `p` | `X = 3` | `X = 4` | `X = 5` |\n|---:|---:|---:|---:|"
        )
        for p, x3, x4, x5 in self.extension:
            out.append(f"| {_p(p)} | {_r3(x3)} | {_r3(x4)} | {_r3(x5)} |")
        out.append(
            "\n**The two-stage operating characteristic (interpretation A):**\n\n"
            "| `p` | `P(retain L3)` | `P(delete L3)` |\n|---:|---:|---:|"
        )
        for p, keep, drop in self.operating:
            out.append(f"| {_p(p)} | {_r3(keep)} | {_r3(drop)} |")
        out.append(
            "\n**Wilson intervals for the results that can actually be reported.** The interval "
            "goes on the slide; the point estimate never.\n\n"
            "| Result | 95% Wilson | Note |\n|---|---|---|"
        )
        for k, n, lo, hi, note in self.reportable:
            out.append(f"| `{k}/{n}` | `[{lo:.3f}, {hi:.3f}]` | {note} |")
        return "\n".join(out) + "\n"


def power_table() -> PowerTable:
    """Every figure the pre-registration carries, computed exactly, in one object."""
    stage1 = tuple(
        (p, cdf(RETAIN1 - 1, N1, p), cdf(DELETE1, N1, p),
         cdf(RETAIN1 - 1, N1, p) - cdf(DELETE1, N1, p), sf(RETAIN1, N1, p))
        for p in P_GRID
    )
    extension = tuple(
        (p, *(extension_retain_probability(x, p) for x in (3, 4, 5))) for p in P_GRID
    )
    operating = tuple(
        (p, retain_probability(p), Fraction(1) - retain_probability(p)) for p in P_GRID
    )
    reportable = tuple(
        (k, n, *wilson_interval(k, n), note) for k, n, note in REPORTABLE
    )
    return PowerTable(stage1=stage1, extension=extension, operating=operating, reportable=reportable)


def _r3(f: Fraction) -> str:
    """Three decimal places, half-up on the exact rational — **never through a float**.

    `round(float(x), 3)` is round-half-even over a value that is already the wrong value. This
    multiplies the exact rational by 1000, rounds the integer quotient half-up, and formats. The
    difference shows up at exactly the figure this plan corrects.
    """
    scaled = f * 1000
    whole = scaled.numerator // scaled.denominator
    if 2 * (scaled - whole) >= 1:
        whole += 1
    return f"{whole // 1000}.{whole % 1000:03d}"


def _p(p: Fraction) -> str:
    """`Fraction(3, 20)` renders as `0.15`. Exact by construction: every grid point is /100."""
    hundredths = p * 100
    if hundredths.denominator != 1:
        raise ValueError(f"grid point {p} is not an exact number of hundredths")
    return f"0.{int(hundredths):02d}"
