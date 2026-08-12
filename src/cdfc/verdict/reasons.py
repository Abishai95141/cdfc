"""P5-B3 — the thirty item-level reason codes, in five families.

**Exactly thirty, and the count is pinned in four other documents.** Adding a thirty-first is a
four-place change and needs a decision record; arbitration C3 already refused one
(`out_of_scope.precondition_degenerate`) because a *field* on an existing code carried the same
distinction without moving any count. See `cdfc.probes.relations.ScopeKind`.

**The discipline rule.** A reason is required exactly when the state is not `PASS`, `FAIL` or
`INFORMATIONAL` (D-P5-02). `PASS` and `FAIL` are the two settled states and their reason is the
predicate that produced them. `INFORMATIONAL` is the third: it carries a mandatory
`informational_note` and the producing relation's flag instead, because *an informational item
implies no remedy*, and the spec's own admission test for a distinct reason is that two reasons
are distinct iff they imply different remedies.

**These are ITEM-level codes.** The run-level `invalid.*` causes are a separate closed vocabulary
in `cdfc.verdict.invalid`, and no string is shared between them — a container guard trip, a reader
disagreement about sheet structure and an unbound template are not properties of any cell, and
forcing them into a per-cell code was the category error the audit caught.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class ReasonDisciplineError(ValueError):
    """A (state, reason, note) triple that the vocabulary does not admit. Never defaulted."""


class ReasonCode(StrEnum):
    # --- no_predicate.* (8) — a gap in US, and it stays in the denominator ------------------
    NP_UNDECIDABLE_BY_CONSTRUCTION = "no_predicate.undecidable_by_construction"
    NP_REQUIRES_JUDGMENT = "no_predicate.requires_judgment"
    NP_NOT_YET_SYNTHESISED = "no_predicate.not_yet_synthesised"
    NP_FAILED_QUALIFICATION = "no_predicate.failed_qualification"
    NP_RULE_AMBIGUOUS = "no_predicate.rule_ambiguous"
    NP_NO_OBLIGATION_SPECIFIED = "no_predicate.no_obligation_specified"
    NP_RULE_WITHDRAWN = "no_predicate.rule_withdrawn"
    NP_NOT_YET_REQUALIFIED = "no_predicate.not_yet_requalified"

    # --- not_run.* (10) — a check that did not happen, and it is never absorbed -------------
    NR_INPUT_UNAVAILABLE_COUNTERPARTY = "not_run.input_unavailable.counterparty"
    NR_INPUT_UNAVAILABLE_REGISTER = "not_run.input_unavailable.register"
    NR_INPUT_UNAVAILABLE_PRIOR_PERIOD = "not_run.input_unavailable.prior_period"
    NR_SOURCE_UNREADABLE = "not_run.source_unreadable"
    NR_TEMPLATE_UNBOUND = "not_run.template_unbound"
    NR_DEACTIVATED = "not_run.deactivated"
    NR_BUDGET_EXHAUSTED = "not_run.budget_exhausted"
    NR_EXTERNAL_SOURCE_LACKS_FIELD = "not_run.external_source_lacks_field"
    NR_EXTERNAL_SOURCE_UNAVAILABLE = "not_run.external_source_unavailable"
    NR_EXTRACTOR_DISAGREEMENT = "not_run.extractor_disagreement"

    # --- indeterminate.* (4) — we ran and cannot say -----------------------------------------
    IND_EXTRACTION_ABSTAINED = "indeterminate.extraction_abstained"
    IND_TOLERANCE_STRADDLE = "indeterminate.tolerance_straddle"
    IND_CONFLICTING_SOURCES = "indeterminate.conflicting_sources"
    IND_ENGINE_DISAGREEMENT = "indeterminate.engine_disagreement"

    # --- out_of_scope.* (3) — C3: there is NO out_of_scope.precondition_degenerate ------------
    OOS_NOT_APPLICABLE = "out_of_scope.not_applicable"  # carries scope_kind
    OOS_NOT_SELECTED = "out_of_scope.not_selected"
    OOS_WITHHELD = "out_of_scope.withheld"

    # --- error.* (5) — the apparatus failed, and the run is INVALID ---------------------------
    ERR_PREDICATE_RAISED = "error.predicate_raised"
    ERR_CELLS_BOUND_ZERO = "error.cells_bound_zero"
    ERR_CANARY_SILENT = "error.canary_silent"
    ERR_CLOSURE_VIOLATED = "error.closure_violated"
    ERR_PARSER_DISAGREEMENT_STRUCTURAL = "error.parser_disagreement_structural"


REASON_COUNT: Final[int] = 30

FAMILIES: Final[tuple[str, ...]] = (
    "no_predicate", "not_run", "indeterminate", "out_of_scope", "error"
)


def family_of(reason: ReasonCode) -> str:
    return reason.value.split(".", 1)[0]


def by_family() -> dict[str, tuple[ReasonCode, ...]]:
    return {f: tuple(c for c in ReasonCode if family_of(c) == f) for f in FAMILIES}


# NOTE ON FILE LAYOUT, and it is a deliberate deviation recorded rather than glossed.
#
# The plan puts `FAMILY`, `reason_required` and `validate_pair` in this file. They join the two
# vocabularies, so wherever they live that file must import both — and `states.py` must import
# `ReasonCode` for `REMOVAL_BASIS`'s keys. Written as specified the two modules import each other.
#
# The dependency therefore runs ONE WAY: this file is the enum and nothing else, and everything
# that joins a reason to a state lives in `states.py`. `cdfc.verdict.__init__` re-exports the
# public names so a caller sees the interface the plan specifies from one place.
