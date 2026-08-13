"""P8-B2 — the CALC derivation. **This module imports `cdfc.calc`, and that is the point.**

It is the POSITIVE CONTROL for `test_tc__foreign_engine_closure_excludes_calc`: a check that cannot
detect the case it exists for is not a check. A corpus derived here licenses an FFR **only** for
predicates whose read set is disjoint from `computed_cells` — never for an arithmetic predicate,
which would be re-checking our answer against our answer.
"""

from __future__ import annotations

from pathlib import Path

from cdfc.calc.evaluate import ValueGrid  # noqa: F401 - the dependency this module DECLARES
from cdfc.qualify.observability import grid_of

MODULE = "cdfc.qualify.corpus._derive_calc"


def value_table(path: Path) -> dict[tuple[str, str], object]:
    grid = grid_of(path)
    return {k: v for k, v in grid.values.items() if k in grid.computed_cells}
