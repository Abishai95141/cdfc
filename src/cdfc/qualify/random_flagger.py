"""P7-B3 — the hypergeometric baseline. **A random flagger scores exactly 0.**

    adjusted_precision = (observed_precision - d/n) / (1 - d/n)

where `d` is the number of genuinely defective items and `n` the population. A checker that flags
at random has `observed_precision = d/n` by construction, so its adjusted precision is `0`; a
checker that flags EVERYTHING also has `observed_precision = d/n`, so it scores `0` too.

**THE EXHIBIT THIS EXISTS FOR.** CLAUSE's best F1 over an 80-cell table is **65.4** on a
~49.5%-positive split (rate-ok: the published split, quoted) where a constant always-flag
classifier scores **66.2** — *the published
system is beaten by a classifier that says yes to everything*. A degeneracy module that cannot
reproduce the published exhibit of the failure it exists to catch is not a degeneracy module, so
`test_random_flagger__clause_exhibit` reproduces both numbers from this module.

`Decimal` with the pinned context; no float. A precision computed in binary floating point is a
number nobody can re-derive.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Final

PRECISION: Final[int] = 28


class DegenerateBaseline(ZeroDivisionError):
    """`d == n`: every item is defective, so no checker can be distinguished from any other."""


def adjusted_precision(flagged: int, true_defective: int, n: int, *, correct: int | None = None) -> Decimal:
    """`(observed_precision − d/n) / (1 − d/n)`.

    `correct` is how many of the flagged items were genuinely defective; when omitted it is
    assumed the flagger is unbiased over the population — the RANDOM case — which is what makes
    the random flagger's score exactly `0` rather than approximately so.
    """
    if n <= 0:
        raise DegenerateBaseline("an empty population has no precision")
    if not (0 <= true_defective <= n):
        raise ValueError(f"true_defective={true_defective} outside [0, {n}]")
    if true_defective == n:
        raise DegenerateBaseline(
            "every item is defective, so `1 - d/n` is zero and no checker is distinguishable "
            "from any other. This is a property of the population, not a score."
        )
    with localcontext() as ctx:
        ctx.prec = PRECISION
        base = Decimal(true_defective) / Decimal(n)
        if flagged == 0:
            observed = base  # flags nothing: indistinguishable from the base rate
        else:
            hits = Decimal(true_defective) * Decimal(flagged) / Decimal(n) if correct is None \
                else Decimal(correct)
            observed = hits / Decimal(flagged)
        return (observed - base) / (Decimal(1) - base)


def f1(tp: int, fp: int, fn: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        if tp == 0:
            return Decimal(0)
        p = Decimal(tp) / Decimal(tp + fp)
        r = Decimal(tp) / Decimal(tp + fn)
        return (2 * p * r) / (p + r)


def always_flag_f1(n: int, positives: int) -> Decimal:
    """The constant classifier's F1: it flags everything, so `tp = positives`, `fp = n - positives`,
    `fn = 0`. This is the number that beat CLAUSE."""
    return f1(tp=positives, fp=n - positives, fn=0)
