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
    # THE CONSTRUCT THE HARVESTER READ, kept in the pieces the artifact carries rather than as
    # rendered text. P7-B1 turns it into the TEMPLATE obligation's verbatim quote, and its offset
    # into `template_instrument.emit()` is that obligation's span (F9). Recording it here rather
    # than re-deriving it later is the point: a quote re-read from the workbook by a second code
    # path is a second extraction, and two extractions that disagree is exactly what G0 exists to
    # find — it must not be something the obligation generator can quietly launder.
    #
    # It is NOT on `Candidate` and therefore NOT inside `code_sha256`: adding a field to the
    # envelope would re-key all 572 admitted digests, and the construct is a property of the
    # OBLIGATION, not of the predicate that implements it.
    construct_kind: str  # "formula" | "validation"
    construct_parts: tuple[str, ...]  # (body,) | (type, operator, formula1)
    construct_at: tuple[str, str]  # (sheet, ref-or-sqref), verbatim as the artifact writes it
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


def obligation_id(kind: str, sheet: str, ref: str) -> str:
    """`OBL-TEMPLATE-<F|V>-<sheet>-<ref>` (C2). Every harvested candidate carries one.

    **THE KIND DISCRIMINATOR WAS ADDED AT P7-B1 AND IT IS NOT COSMETIC.** Without it the id was
    `(sheet, ref)` only, and `1. Introduction!D17` on the FME blank carries BOTH a formula
    (`=SUM(D18:D20)`) and a `whole >= 0` data validation. Those are two different obligations —
    *the total equals its parts* and *this cell is a non-negative whole number* — and they shared
    one id, so the obligation's verbatim quote would have been **whichever harvest class ran
    last** and one of the two predicates would have been checked at G0 against a construct it was
    not derived from.

    One instance across all nine workbooks, found by an equality assertion in `harvest()` rather
    than by inspection. An id that is not injective over the thing it names is a foreign key that
    silently points at the wrong row.
    """
    if kind not in ("F", "V"):
        raise ValueError(f"construct kind must be 'F' or 'V', got {kind!r}")
    return f"OBL-TEMPLATE-{kind}-{sheet.strip().replace(' ', '_')}-{ref.replace('$', '')}"


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
