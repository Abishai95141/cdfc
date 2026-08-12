"""P5-B4 — the seven-term closure invariant, and it ABORTS the report on a hole.

**There is no degraded report.** If the seven terms do not sum to the field surface, some cell of
the denominator is in no bucket, and every fraction over that denominator is a fraction of
something nobody enumerated. The in-toto specification names the hazard in its own text: an
implicit open world *"could allow artifacts to sneak into the step or inspection undetected."*
`assert_closed` raises, the run is `INVALID(invalid.closure_violated)`, and report generation
stops. The failure branch is to narrow the field surface to the sheets where closure holds and
publish the excluded sheets **by name** — a smaller denominator honestly stated beats a full one
that does not balance.

**`inScope` is not `cellsTotal - outOfScope - informational`, and D-P5-05 states the change.**
Both subtrahends are reachable by making the filing worse, so under the spec's formula a filer who
fills in less can get a better settled fraction. The two `*Retained` sub-counts carry the cells
that stay, the seven-term sum over `cellsTotal` is untouched, and **`in_scope()` is the only
function consulted** — a second removal path anywhere in this file is a defect no test of the
table can see.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from cdfc.verdict.reasons import ReasonCode
from cdfc.verdict.states import ItemState, in_scope

# The seven buckets, and every item state maps to exactly one. `NO_PREDICATE` has its own bucket
# because it is a gap in US and stays in the denominator; folding it into `notRun` would let the
# fraction rise by doing nothing.
BUCKET_OF: Final[Mapping[ItemState, str]] = {
    ItemState.OUT_OF_SCOPE: "outOfScope",
    ItemState.INFORMATIONAL: "informational",
    ItemState.PASS: "settled",
    ItemState.FAIL: "settled",
    ItemState.INDETERMINATE: "indeterminate",
    ItemState.NOT_RUN: "notRun",
    ItemState.NO_PREDICATE: "noPredicate",
    ItemState.ERROR: "error",
}

TERMS: Final[tuple[str, ...]] = (
    "outOfScope", "informational", "settled", "indeterminate", "notRun", "noPredicate", "error"
)


class ClosureViolation(Exception):
    """A cell of the denominator is in no bucket. Report generation stops here."""

    def __init__(self, missing: tuple[str, ...], sums: Mapping[str, int], field_surface: int) -> None:
        self.missing = missing
        self.sums = dict(sums)
        self.field_surface = field_surface
        total = sum(sums[t] for t in TERMS)
        super().__init__(
            f"the seven terms sum to {total}, not to the {field_surface}-cell field surface. "
            f"Unbucketed: {list(missing[:8])}"
            + (f" (+{len(missing) - 8} more)" if len(missing) > 8 else "")
            + ". There is no degraded report: every fraction over this denominator would be a "
            "fraction of something nobody enumerated."
        )


@dataclass(frozen=True, slots=True)
class ClosurePartition:
    outOfScope: int
    informational: int
    settled: int
    indeterminate: int
    notRun: int
    noPredicate: int
    error: int
    cellsTotal: int
    outOfScopeRetained: int
    informationalRetained: int
    settledPass: int = 0
    settledFail: int = 0
    requalify: int = 0
    loweredByRollup: int = 0

    @property
    def total(self) -> int:
        """The SEVEN terms. Unchanged by D-P5-05 — the sub-counts do not enter it."""
        return (
            self.outOfScope + self.informational + self.settled + self.indeterminate
            + self.notRun + self.noPredicate + self.error
        )

    @property
    def inScope(self) -> int:
        return (
            self.cellsTotal
            - (self.outOfScope - self.outOfScopeRetained)
            - (self.informational - self.informationalRetained)
        )

    def as_row(self) -> dict[str, int]:
        return {t: getattr(self, t) for t in TERMS} | {
            "cellsTotal": self.cellsTotal,
            "inScope": self.inScope,
            "outOfScopeRetained": self.outOfScopeRetained,
            "informationalRetained": self.informationalRetained,
        }


def partition(cells: Sequence[Any], field_surface: int) -> ClosurePartition:
    """Bucket every cell. `in_scope()` decides removal, and nothing else in this file does."""
    counts = dict.fromkeys(TERMS, 0)
    retained_oos = retained_info = 0
    passes = fails = requalify = lowered = 0
    unbucketed: list[str] = []

    for cell in cells:
        bucket = BUCKET_OF.get(cell.state)
        if bucket is None:
            unbucketed.append(cell.stable_key)
            continue
        counts[bucket] += 1
        if cell.state is ItemState.PASS:
            passes += 1
        elif cell.state is ItemState.FAIL:
            fails += 1
        # THE ONLY REMOVAL DECISION. `in_scope` reads scope_kind; a build that subtracted all
        # OUT_OF_SCOPE would never call it and would fail the fraction-does-not-rise property.
        if in_scope(cell.state, cell.reason, getattr(cell, "scope_kind", None)):
            if cell.state is ItemState.OUT_OF_SCOPE:
                retained_oos += 1
            elif cell.state is ItemState.INFORMATIONAL:
                retained_info += 1
        if getattr(cell, "requalify", False):
            requalify += 1
        if getattr(cell, "lowered_by_rollup", False):
            lowered += 1

    part = ClosurePartition(
        **counts,
        cellsTotal=field_surface,
        outOfScopeRetained=retained_oos,
        informationalRetained=retained_info,
        settledPass=passes,
        settledFail=fails,
        requalify=requalify,
        loweredByRollup=lowered,
    )
    if unbucketed:
        raise ClosureViolation(tuple(sorted(unbucketed)), counts, field_surface)
    return part


def assert_closed(p: ClosurePartition) -> None:
    """The seven terms sum to `cellsTotal`, or report generation aborts."""
    if p.total != p.cellsTotal:
        raise ClosureViolation((), p.as_row(), p.cellsTotal)


CLOSURE_SQL: Final[str] = """
SELECT
  SUM(state = 'OUT_OF_SCOPE')   AS outOfScope,
  SUM(state = 'INFORMATIONAL')  AS informational,
  SUM(state IN ('PASS','FAIL')) AS settled,
  SUM(state = 'INDETERMINATE')  AS indeterminate,
  SUM(state = 'NOT_RUN')        AS notRun,
  SUM(state = 'NO_PREDICATE')   AS noPredicate,
  SUM(state = 'ERROR')          AS error,
  SUM(in_scope AND state = 'OUT_OF_SCOPE')  AS outOfScopeRetained,
  SUM(in_scope AND state = 'INFORMATIONAL') AS informationalRetained,
  COUNT(*)                      AS cellsTotal
FROM run_cell WHERE run_id = ?
"""


def explain(p: ClosurePartition) -> str:
    """The seven terms, for `cdfc closure explain`. Rendered with `inScope` beside `cellsTotal`."""
    lines = [f"  {t:>15s}  {getattr(p, t):6d}" for t in TERMS]
    lines.append(f"  {'':>15s}  {'-' * 6}")
    lines.append(f"  {'sum':>15s}  {p.total:6d}   cellsTotal {p.cellsTotal}")
    lines.append(
        f"  of which retained: outOfScope {p.outOfScopeRetained}  "
        f"informational {p.informationalRetained}"
    )
    lines.append(f"  {'inScope':>15s}  {p.inScope:6d}")
    if p.requalify:
        lines.append(
            f"  {p.requalify} cell(s) retained for a degenerate precondition are flagged for "
            "G3 re-qualification"
        )
    return "\n".join(lines)
