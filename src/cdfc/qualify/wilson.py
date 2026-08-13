"""P8-B3 — the Wilson score interval. **`Decimal` throughout, and `math` is not importable here.**

**Why the interval and not the point estimate.** `0 fires / 4 filings` has a point estimate of
`0.000` and an interval of `[0.000, 0.490]`. A rule keyed on the point estimate would let a sample
of four buy `BLOCKING`. **The upper bound makes the tier a statement about EVIDENCE rather than
about LUCK.**

The two intervals that must never be allowed to look alike:

    0/340  ->  [0.000000, 0.011172]
    0/4    ->  [0.000000, 0.489891]

**Why `Decimal` and never `math.sqrt`.** This value lands in a byte-identical attestation (P11 /
G-REPRO). A binary float's 6-dp string can differ between builds of the same interpreter, and then
two machines produce two attestations for one run. NC-Q56 is the injected break, and its guard
asserts `math` is absent from this module's import closure — not that the numbers happen to match.
"""

from __future__ import annotations

from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from typing import Final

# The two-sided 95% normal quantile (rate-ok: a confidence LEVEL naming an interval, not a
# measured rate), to 15 dp. A MODULE CONSTANT WITH A TEST: a different `z` is a
# different gate, and a gate whose threshold moved without a diff is not a gate.
WILSON_Z: Final[Decimal] = Decimal("1.959963984540054")

WILSON_CTX: Final[Context] = Context(prec=28, rounding=ROUND_HALF_EVEN)

QUANTUM: Final[Decimal] = Decimal("0.000001")  # 6 dp, everywhere


class ZeroSampleError(ZeroDivisionError):
    """`n == 0`. **A rate over no filings is not a small rate** — it is not a rate."""


def wilson(k: int, n: int, z: Decimal = WILSON_Z) -> tuple[Decimal, Decimal, Decimal]:
    """`(point, lo, hi)`, each quantised to 6 dp, with `lo` and `hi` CLAMPED to `[0, 1]`.

    The clamp is not cosmetic: the unclamped lower bound of `0/340` is `-0.000000`, and a NEGATIVE
    RATE must never reach a surface. A reader who sees one stops believing the column.
    """
    if isinstance(k, bool) or isinstance(n, bool) or not isinstance(k, int) or not isinstance(n, int):
        raise TypeError("k and n are integer counts of FILINGS")
    if n == 0:
        raise ZeroSampleError(
            "n == 0: a false-failure rate over no filings is not a small rate, it is not a rate. "
            "Returning 0.0 here would print the shape of evidence over no evidence."
        )
    if n < 0 or k < 0 or k > n:
        raise ValueError(f"k={k}, n={n}: a count of fires cannot exceed the filings it ran over")

    with localcontext(WILSON_CTX):
        N = Decimal(n)
        K = Decimal(k)
        p = K / N
        z2 = z * z
        denom = Decimal(1) + z2 / N
        centre = (p + z2 / (2 * N)) / denom
        # Decimal.sqrt, never math.sqrt.
        radicand = (p * (Decimal(1) - p) / N) + (z2 / (4 * N * N))
        half = (z * radicand.sqrt()) / denom
        lo = centre - half
        hi = centre + half
        return (
            _q(p),
            _q(max(Decimal(0), min(Decimal(1), lo))),
            _q(max(Decimal(0), min(Decimal(1), hi))),
        )


def _q(x: Decimal) -> Decimal:
    with localcontext(WILSON_CTX):
        out = x.quantize(QUANTUM)
        # `-0.000000` is not a number a reader should ever see.
        return Decimal("0.000000") if out == 0 else out


def render(k: int, n: int) -> str:
    """`k/n` AND the interval, in one string. A rate never renders without both integers of its
    fraction (`ci/no-bare-rate.sh`) and never without its interval (P8 exit criterion 4)."""
    point, lo, hi = wilson(k, n)
    return f"{k}/{n} (point {point}, Wilson interval [{lo}, {hi}])"


def n_for_upper_bound(bound: Decimal, k: int = 0) -> int:
    """The smallest `n` at which `hi(k, n) <= bound`. **DERIVED, not quoted.**

    The specification says *"roughly n >= 185"* for `hi(0, n) <= 0.02`. It is **189**, and this
    function computes it rather than repeating the number: a threshold nobody re-derived is a
    threshold that drifts into a document and then into a gate.
    """
    n = max(1, k)
    while n < 10_000_000:
        if wilson(k, n)[2] <= bound:
            return n
        n += 1
    raise ValueError(f"no n below 10^7 reaches hi({k}, n) <= {bound}")
