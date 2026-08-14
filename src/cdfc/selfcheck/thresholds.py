"""P10-B1 — the pre-registered thresholds of the liveness layer.

**Pre-registered means: written down before the number it judges was measured, with a document
row that has to move for the constant to move.** A ceiling chosen after seeing the
inapplicability rate is not a ceiling, it is a description of the rate.

`docs/SELFCHECK-THRESHOLDS.md` carries one row per constant here, and
`tests/unit/test_thresholds.py::test_th__ceiling_is_pre_registered` fails the build when a
constant moves without its row moving with it. The mechanism is the same one `perf/BUDGET-CHANGES.md`
and `docs/GATE-CHANGES.md` use, and it exists for the same reason: a number in code with no dated
argument beside it is a number whoever is inconvenienced by it will change.

**`MAX_WITNESSES` is `PROVISIONAL` until the calibration curve closes it (§5.1, adversary F44).**
`plan/05` §5.1 is explicit that *nothing in the corpus argues for 3*, so the constant renders with
its status attached and `docs/measurements/P10-canary-cost.md` publishes inapplicability at
`{1, 3, 5}`. A constant nobody can defend is allowed to ship — labelled — and is not allowed to
ship quietly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Final

# The fraction of canary attempts that may be inapplicable OR indeterminate before the run is
# INVALID. **`Decimal`, not float**: this number is compared against a ratio that decides whether
# a regulated filing gets a verdict, and a comparison that can turn on the last binary place is a
# threshold nobody can re-derive. R4.
CANARY_INAPPLICABLE_CEILING: Final[Decimal] = Decimal("0.25")

# The number of stored kill cases the loop will try before declaring a predicate inapplicable.
# **PROVISIONAL.** See the module docstring and §5.1.
MAX_WITNESSES: Final[int] = 3
MAX_WITNESSES_STATUS: Final[str] = "PROVISIONAL — see docs/measurements/P10-canary-cost.md"

# The settings the calibration curve is measured at. In the code rather than in the tool, so the
# curve's x-axis and the constant it is meant to close are the same list.
CALIBRATION_SETTINGS: Final[tuple[int, ...]] = (1, 3, 5)

# Every constant this module pre-registers, and the row of `docs/SELFCHECK-THRESHOLDS.md` that
# must carry it. The test reads THIS map rather than a second list in the test file.
PRE_REGISTERED: Final[dict[str, object]] = {
    "CANARY_INAPPLICABLE_CEILING": CANARY_INAPPLICABLE_CEILING,
    "MAX_WITNESSES": MAX_WITNESSES,
}


def ceiling_exceeded(inapplicable: int, indeterminate: int, rows: int) -> bool:
    """`(inapplicable + indeterminate) / rows > CEILING`, in exact arithmetic.

    **The numerator is both, and adversary F18 is why.** Pooling only `inapplicable` reports our
    evaluator's coverage as the fault's invisibility: an INDETERMINATE canary is one where we
    cannot say whether the predicate would have caught the fault, and a run in which we cannot say
    that for a third of the checks has not demonstrated liveness either. They are counted together
    HERE and reported apart everywhere else, which is the only combination that is honest in both
    directions.

    **`rows == 0` is not a pass.** A loop that attempted nothing has an undefined rate, and
    returning `False` — "the ceiling was not exceeded" — would let a build with no canary layer at
    all sail through the disposition. It is exceeded, and `disposition` names why.
    """
    if rows <= 0:
        return True
    return Decimal(inapplicable + indeterminate) / Decimal(rows) > CANARY_INAPPLICABLE_CEILING
