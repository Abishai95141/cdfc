"""P4-B4 — the nine harvest classes, and the fault classes each of them CLAIMS.

**Each class declares `CLAIMS_FAULT_CLASSES` once, as a module-level constant.** The harvest cannot
invent a claim per predicate, and that is the point: a claim tuned per predicate after a campaign
is exactly what D-P4-06 exists to prevent, and a per-class constant makes
`test_harvest__claims_are_a_pure_function_of_the_class` mechanical rather than aspirational.

**Over-claiming is self-punishing and under-claiming is caught.** A wider claim is a HARDER G2 bar
(more classes in the denominator), and any claimed class with `O == 0` raises at G2 — an unexercised
claim is not a claim. The incentive runs the right way in both directions.

The table below is `docs/FAULT-CLAIMS.md`, committed in this phase — four phases before the first
campaign — so the git-ancestor test in `test_g2_denominator_is_declared_before_the_campaign` is
satisfied by construction rather than by discipline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cdfc.predicates.envelope import Candidate, ClauseAbsentReason, Tolerance


@dataclass(frozen=True, slots=True)
class Draft:
    """One candidate before an id is assigned. Ids come from the canonical emission order."""

    harvest_class: str
    obligation_id: str
    clause_absent_reason: ClauseAbsentReason
    claims_fault_classes: tuple[str, ...]
    schema_keys: tuple[str, ...]
    applicable: str
    expr: str
    witness: str
    reason_if_inapplicable: str
    rationale: str
    key_cells: dict[str, set[str]] = field(default_factory=dict)
    tolerance: Tolerance | None = None
    host_fns: tuple[str, ...] = ()

    def build(self, pid: str, template_sha256: str) -> Candidate:
        return Candidate(
            id=pid,
            version=1,
            kind="harvested",
            template=template_sha256,
            schema_keys=self.schema_keys,
            host_fns=self.host_fns,
            obligation_id=self.obligation_id,
            obligation_source="TEMPLATE",
            clause=None,
            rationale=self.rationale,
            clause_absent_reason=self.clause_absent_reason,
            claims_fault_classes=self.claims_fault_classes,
            applicable=self.applicable,
            expr=self.expr,
            witness=self.witness,
            reason_if_inapplicable=self.reason_if_inapplicable,
            tolerance=self.tolerance,
            external_deps=(),
        )


def obligation_id(sheet: str, ref: str) -> str:
    """`OBL-TEMPLATE-<sheet>-<ref>` (C2). Every harvested candidate carries one."""
    return f"OBL-TEMPLATE-{sheet.strip().replace(' ', '_')}-{ref.replace('$', '')}"


from cdfc.predicates.harvest_classes import (  # noqa: E402
    conditional_required,
    cross_sheet_equality,
    date_bound,
    integer_bound,
    membership,
    numeric_bound,
    same_sheet_equality,
    sum_identity,
    tally_identity,
)

# Emission order across classes does not matter: `harvest()` sorts by the canonical
# `(sheet index, row, column, class)` key before assigning ids.
ALL_CLASSES: tuple[Any, ...] = (
    cross_sheet_equality,
    same_sheet_equality,
    sum_identity,
    tally_identity,
    membership,
    numeric_bound,
    integer_bound,
    date_bound,
    conditional_required,
)

CLAIMS: dict[str, tuple[str, ...]] = {m.NAME: m.CLAIMS_FAULT_CLASSES for m in ALL_CLASSES}
