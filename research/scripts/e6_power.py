#!/usr/bin/env python3
"""
E6 settling-experiment power arithmetic — exact binomial, no approximation, no RNG.

Produces every figure the P12 pre-registration must carry, and settles by arithmetic
the one thing spec/04-path.md §1.1 leaves ambiguous: what the "extension to n = 40"
actually draws.

    /Users/abishaikc/Gift/.venv/bin/python research/scripts/e6_power.py

This script is the interim producer of the DERIVED figures in plan/06-phases-model-and-clause.md.
It is superseded by src/cdfc/experiment/power.py at P12-B4, at which point
test_e6__power_table_matches_preregistration asserts the two agree.

Decision rule under test (spec/04-path.md DECISION E6.1):
    n = 20 Stratum-A obligations.
    k >= 6   -> RETAIN L3   (and the surviving set must also beat B0 u B1 u B2)
    k <= 2   -> DELETE L3
    3<=k<=5  -> exactly ONE extension to n = 40 at a threshold of >= 12, never again.
"""

from math import comb, sqrt

N1, RETAIN1, DELETE1 = 20, 6, 2
N2, RETAIN2 = 40, 12
P_GRID = (0.15, 0.20, 0.25, 0.30, 0.35)


def pmf(k: int, n: int, p: float) -> float:
    return comb(n, k) * p**k * (1.0 - p) ** (n - k)


def cdf(k: int, n: int, p: float) -> float:
    """P(X <= k)."""
    return sum(pmf(i, n, p) for i in range(0, k + 1))


def sf(k: int, n: int, p: float) -> float:
    """P(X >= k)."""
    return 1.0 - cdf(k - 1, n, p)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Two-sided Wilson score interval. The interval goes on the slide; the point estimate never."""
    ph = k / n
    d = 1.0 + z * z / n
    centre = (ph + z * z / (2 * n)) / d
    half = z * sqrt(ph * (1.0 - ph) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def retain_pooled(p: float) -> float:
    """
    INTERPRETATION A — the extension draws 20 MORE Stratum-A obligations and the
    >= 12 threshold is evaluated over the POOLED 40.
    """
    total = 0.0
    for x in range(0, N1 + 1):
        px = pmf(x, N1, p)
        if x >= RETAIN1:
            total += px
        elif x > DELETE1:
            total += px * sf(RETAIN2 - x, N1, p)
    return total


def retain_fresh40(p: float) -> float:
    """INTERPRETATION B — the extension is a fresh independent n = 40 sample."""
    return sf(RETAIN1, N1, p) + (cdf(RETAIN1 - 1, N1, p) - cdf(DELETE1, N1, p)) * sf(RETAIN2, N2, p)


def main() -> None:
    print("== Stage 1, n = 20 — the table in spec/04-path.md §1.1 ==")
    print(f"{'p':>6}{'P(X<=5)':>10}{'P(X<=2)':>10}{'P(3<=X<=5)':>13}{'P(X>=6)':>10}")
    for p in P_GRID:
        a, b = cdf(RETAIN1 - 1, N1, p), cdf(DELETE1, N1, p)
        print(f"{p:>6.2f}{a:>10.3f}{b:>10.3f}{a - b:>13.3f}{1 - a:>10.3f}")
    print(f"\n  NOTE: P(X<=2 | p=0.30) = {cdf(2, 20, 0.30):.6f} -> 0.035 to 3dp.")
    print("  spec/04-path.md §1.1 prints 0.036. Corrected in plan/06 §0.3 item 2.\n")

    print("== The extension branch: given stage-1 X, draw 20 more, retain iff X+Y >= 12 ==")
    print(f"{'p':>6}" + "".join(f"{'X=' + str(x):>10}" for x in (3, 4, 5)))
    for p in P_GRID:
        print(f"{p:>6.2f}" + "".join(f"{sf(RETAIN2 - x, N1, p):>10.3f}" for x in (3, 4, 5)))

    print("\n== Which interpretation of 'extension to n = 40' does the spec mean? ==")
    print("  spec/04-path.md §1.1 states: deletes 92.9% at p=0.15, wrongly deletes 13.4% at p=0.35.")
    print(f"{'p':>6}{'A: pooled 40':>15}{'B: fresh 40':>15}")
    for p in (0.15, 0.35):
        print(f"{p:>6.2f}{1 - retain_pooled(p):>15.3f}{1 - retain_fresh40(p):>15.3f}")
    print("  A reproduces both figures exactly. B does not. The extension therefore draws")
    print("  20 MORE Stratum-A obligations and >= 12 is evaluated over the pooled 40.\n")

    print("== Overall two-stage operating characteristic (interpretation A) ==")
    print(f"{'p':>6}{'P(retain)':>12}{'P(delete)':>12}")
    for p in P_GRID:
        r = retain_pooled(p)
        print(f"{p:>6.2f}{r:>12.3f}{1 - r:>12.3f}")

    print("\n== Stage-2 is sharper, not laxer: same 0.30 rate, half the interval width ==")
    print(f"{'p':>6}{'P(X>=6|20)':>13}{'P(X>=12|40)':>14}")
    for p in P_GRID:
        print(f"{p:>6.2f}{sf(RETAIN1, N1, p):>13.3f}{sf(RETAIN2, N2, p):>14.3f}")

    print("\n== Wilson 95% intervals for the results that can actually be reported ==")
    for k, n, note in (
        (0, 20, "k = 0 — a publishable result, and this is its interval"),
        (2, 20, "the delete boundary"),
        (6, 20, "the retain boundary"),
        (12, 40, "the extension's retain boundary"),
    ):
        lo, hi = wilson(k, n)
        print(f"  {k:>3}/{n:<3} [{lo:.3f}, {hi:.3f}]   {note}")

    print("\n== Forced-abstention floor r >= (mu - alpha)/(1 - alpha), alpha = 0.05 ==")
    print("  mu is a BASE ERROR RATE, not an accuracy — the formula only closes that way.")
    for mu in (0.05, 0.10, 0.20, 0.30, 0.40):
        print(f"  mu={mu:.2f}  ->  r >= {max(0.0, (mu - 0.05) / 0.95):.4f}")


if __name__ == "__main__":
    main()
