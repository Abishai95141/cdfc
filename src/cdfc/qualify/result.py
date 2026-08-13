"""P7-B1 — what a gate returns, what a rejection records, and the order the gates run in.

**`GATE_ORDER` is a tuple, not a comment.** Free before cheap before expensive, and the pipeline
reads the tuple rather than hard-coding a sequence, so NC-Q34's injector can reverse it and the spy
assertion can watch zero mutants be generated for a candidate that fails G0.

**A rejection is a VALUE.** `RejectionRow` carries the rejecting gate, the measured numbers and
`cells_would_have_covered` — the last of which is not cosmetic: it is what turns a rejection into
`no_predicate.failed_qualification` and into the report's `counterEvidence[]`. Discarding it would
throw away exactly the information an audit-documentation standard makes mandatory.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final


class GateId(StrEnum):
    G0 = "G0"  # scope faithfulness — free, structural
    G1 = "G1"  # executes and binds — cheap, one run
    G3P = "G3p"  # degeneracy, proof arm — SMT, bounded by rlimit
    G2 = "G2"  # the kill gate — a whole mutation campaign
    G3E = "G3e"  # degeneracy, empirical arm — needs a corpus
    G4 = "G4"  # the false-failure rate — P8; NOT run at P7


GATE_ORDER: Final[tuple[GateId, ...]] = (
    GateId.G0,
    GateId.G1,
    GateId.G3P,
    GateId.G2,
    GateId.G3E,
    GateId.G4,
)

# What each stage costs, in the only unit that matters for ordering: whether it needs a campaign.
GATE_COST: Final[Mapping[GateId, str]] = {
    GateId.G0: "free — string operations over a pinned text",
    GateId.G1: "cheap — one evaluation against one filing",
    GateId.G3P: "bounded — an SMT query under an rlimit, never a wall clock",
    GateId.G2: "EXPENSIVE — a mutation campaign, minutes per template",
    GateId.G3E: "expensive — a clean corpus plus the campaign's site set",
    GateId.G4: "expensive — the blind-fill corpus, which does not exist before P8",
}


class GateSkipReason(StrEnum):
    """Why a gate did not run. There is exactly one member, and it is not a pass.

    A `SKIPPED` outcome is never counted as a survivor. The column exists so that a future
    predicate source cannot enter the funnel silently — under F9's ruling its value is `0`.
    """

    SUBJECT_NOT_BUILT = "subject_not_built"  # G4 at P7: the blind-fill corpus arrives at P8


@dataclass(frozen=True, slots=True)
class GateOutcome:
    gate: GateId
    passed: bool
    measured: Mapping[str, object]  # written verbatim into qualification.g<n>
    reason: str | None = None  # required iff not passed; from that gate's closed reason set
    evidence_sha256: str | None = None  # a Z3 witness, a campaign id, a corpus id
    skipped: GateSkipReason | None = None

    def __post_init__(self) -> None:
        if self.passed and self.reason is not None:
            raise ValueError(
                f"{self.gate}: a passing outcome carries a rejection reason ({self.reason!r}). "
                "A reason on a pass is a finding nobody acted on."
            )
        if not self.passed and not self.reason:
            raise ValueError(
                f"{self.gate}: a rejection with no reason. Every reason in the closed set implies "
                "a different remedy, which is the admission test for a reason code — a rejection "
                "nobody can act on is a rejection nobody will believe."
            )
        if self.skipped is not None and not self.passed:
            raise ValueError(f"{self.gate}: a skipped gate cannot also reject")
        if self.measured is None:
            raise ValueError(f"{self.gate}: `measured` is required, even when empty")


@dataclass(frozen=True, slots=True)
class RejectionRow:
    """One rejection, keyed by the CANDIDATE digest.

    `predicate_id` is `None` and stays `None`: D-P4-01 says there is no `REJECTED` predicate state,
    so a rejected candidate never acquires an id. E7.3 asserted rather than believed, in
    `tests/contract/test_contract__no_rejected_predicate_state`.
    """

    candidate_sha256: str
    predicate_id: None
    obligation_id: str
    rejecting_gate: GateId
    measured: Mapping[str, object]
    cells_would_have_covered: int
    rejected_at: str  # ISO date, an ARGUMENT to the pipeline, never a clock read here

    def __post_init__(self) -> None:
        if self.predicate_id is not None:
            raise ValueError(
                "a rejected candidate never acquires a predicate_id (D-P4-01: four states, and "
                "REJECTED is not one of them)"
            )
        if isinstance(self.cells_would_have_covered, bool) or not isinstance(
            self.cells_would_have_covered, int
        ):
            raise ValueError(
                f"{self.candidate_sha256[:8]}: cells_would_have_covered is required and is an "
                "integer. It is what turns this rejection into no_predicate.failed_qualification "
                "and into the report's counterEvidence[] — discarding it throws away exactly the "
                "information an audit-documentation standard makes mandatory."
            )
        if self.cells_would_have_covered < 0:
            raise ValueError("cells_would_have_covered cannot be negative")
        if not self.rejected_at:
            raise ValueError("a rejection with no date cannot be placed in a supersession chain")


@dataclass(frozen=True, slots=True)
class QualificationRecord:
    """Every gate outcome for one candidate, in the order they ran."""

    candidate_sha256: str
    obligation_id: str
    outcomes: tuple[GateOutcome, ...]
    qualified_at: str
    qualified_against: Mapping[str, str] = field(default_factory=dict)

    @property
    def rejecting(self) -> GateOutcome | None:
        """The ONE gate that rejected, or None. The pipeline stops at the first failure, so a
        record carrying two rejections is an apparatus defect rather than a worse predicate."""
        failed = [o for o in self.outcomes if not o.passed]
        if len(failed) > 1:
            raise ValueError(
                f"{self.candidate_sha256[:8]}: {len(failed)} rejections in one record. The "
                "pipeline stops at the first failure — the stop is the cost control AND the "
                "evidence, because a rejection carries exactly one gate."
            )
        return failed[0] if failed else None

    @property
    def passed(self) -> bool:
        return self.rejecting is None

    def by_gate(self) -> Mapping[str, GateOutcome]:
        return {o.gate.value: o for o in self.outcomes}

    def ran_in_order(self) -> bool:
        seen = [o.gate for o in self.outcomes]
        return seen == [g for g in GATE_ORDER if g in set(seen)]
