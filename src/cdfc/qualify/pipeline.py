"""P7-B4 — the pipeline: `GATE_ORDER`, in order, stopping at the first failure.

**The stop is the cost control AND the evidence.** A rejection carries exactly one gate, so the
funnel's per-stage integers are a partition rather than an overlapping tally — and a candidate that
fails G0's free structural check never consumes a mutation campaign.

**Order is read from `GATE_ORDER`, not written into this function.** That is what makes NC-Q34
possible: the injector reverses the tuple, and the guard asserts on a SPY over `surgery.seed_mutant`
rather than on the outcome. *The outcome is the same either way; the cost is the thing being gated.*
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from cdfc.qualify.errors import GateOrderError
from cdfc.qualify.result import (
    GATE_ORDER,
    GateId,
    GateOutcome,
    GateSkipReason,
    QualificationRecord,
    RejectionRow,
)


@dataclass(frozen=True, slots=True)
class QualificationContext:
    """Everything the five gates need, assembled once."""

    obligations: Any
    store: Any
    schema: Any
    facts: Any
    runtime: Any
    hostfns: Any
    campaign: Any | None = None
    baselines: Any | None = None
    domain: Any | None = None
    clean: Any | None = None
    degeneracy_list: Sequence[Any] = ()
    class_of: Mapping[str, str] = field(default_factory=dict)
    kill_bar: Any = None
    qualified_at: str = ""
    admitted: Sequence[Any] = ()
    n_sites: int = 0
    true_defective: int = 0
    flagged_by: Mapping[str, int] = field(default_factory=dict)
    correct_by: Mapping[str, int] = field(default_factory=dict)
    repo: Any = None


@dataclass(frozen=True, slots=True)
class Admission:
    candidate_sha256: str
    record: QualificationRecord


@dataclass(frozen=True, slots=True)
class Rejection:
    row: RejectionRow
    record: QualificationRecord


def qualify(
    cand: Any,
    ctx: QualificationContext,
    *,
    through: GateId = GateId.G4,
    spy: Callable[[GateId], None] | None = None,
) -> Admission | Rejection:
    """Run the gates in `GATE_ORDER` and STOP AT THE FIRST FAILURE."""
    from cdfc.predicates.canonical import code_sha256

    digest = code_sha256(cand)
    outcomes: list[GateOutcome] = []
    stop_at = GATE_ORDER.index(through)

    for gate in GATE_ORDER[: stop_at + 1]:
        if spy is not None:
            spy(gate)
        out = _run_gate(gate, cand, ctx)
        if out is None:
            continue
        outcomes.append(out)
        if not out.passed:
            record = QualificationRecord(
                candidate_sha256=digest, obligation_id=cand.obligation_id,
                outcomes=tuple(outcomes), qualified_at=ctx.qualified_at,
            )
            if not record.ran_in_order():
                raise GateOrderError(
                    f"{cand.id}: gates ran as {[o.gate.value for o in outcomes]}, which is not the "
                    f"order of {[g.value for g in GATE_ORDER]}. A candidate that fails a FREE gate "
                    "must never consume an expensive one."
                )
            return Rejection(
                row=RejectionRow(
                    candidate_sha256=digest, predicate_id=None,
                    obligation_id=cand.obligation_id, rejecting_gate=gate,
                    measured=out.measured,
                    cells_would_have_covered=_cells(cand, ctx),
                    rejected_at=ctx.qualified_at,
                ),
                record=record,
            )

    record = QualificationRecord(
        candidate_sha256=digest, obligation_id=cand.obligation_id,
        outcomes=tuple(outcomes), qualified_at=ctx.qualified_at,
    )
    if not record.ran_in_order():
        raise GateOrderError(
            f"{cand.id}: gates ran as {[o.gate.value for o in outcomes]}, out of GATE_ORDER"
        )
    return Admission(candidate_sha256=digest, record=record)


def _run_gate(gate: GateId, cand: Any, ctx: QualificationContext) -> GateOutcome | None:
    from cdfc.qualify import g0_scope, g1_binds, g2_kill, g3_degeneracy

    if gate is GateId.G0:
        return g0_scope.check(cand, ctx.obligations, ctx.store)
    if gate is GateId.G1:
        return g1_binds.check(cand, ctx.schema, ctx.facts, ctx.runtime, ctx.hostfns)
    if gate is GateId.G3P:
        return g3_degeneracy.proof_arm(
            cand, ctx.domain, harvest_class=ctx.class_of.get(cand.id, ""), admitted=ctx.admitted
        )
    if gate is GateId.G2:
        return g2_kill.check(cand, ctx.campaign, ctx.baselines, bar=ctx.kill_bar, repo=ctx.repo)
    if gate is GateId.G3E:
        return g3_degeneracy.empirical_arm(
            cand, ctx.clean, ctx.degeneracy_list,
            n_sites=ctx.n_sites, true_defective=ctx.true_defective,
            flagged=ctx.flagged_by.get(cand.id, 0),
            # EVERY MUTANT A PREDICATE FLAGGED IS DEFECTIVE BY CONSTRUCTION — a mutant is a
            # seeded fault. `correct` defaults to `flagged` for that reason and is overridable
            # the moment a corpus exists that a predicate can be WRONG about, which is P8's.
            correct=ctx.correct_by.get(cand.id, ctx.flagged_by.get(cand.id, 0)),
        )
    if gate is GateId.G4:
        # THE SKIP IS A DECLARED STATE, NOT A PASS. The blind-fill corpus arrives at P8, and
        # `skipped` is never counted as a survivor whatever its value.
        return GateOutcome(gate=GateId.G4, passed=True, measured={
            "false_failure_rate": None,
            "why": "the blind-fill corpus does not exist before P8; no FFR has been measured for "
                   "any predicate in this system",
        }, skipped=GateSkipReason.SUBJECT_NOT_BUILT)
    return None


def _cells(cand: Any, ctx: QualificationContext) -> int:
    """`cells_would_have_covered`. Not optional and not cosmetic: it is what turns a rejection
    into `no_predicate.failed_qualification` and into the report's `counterEvidence[]`."""
    from cdfc.predicates.ast_walker import bound_cells

    try:
        return len(bound_cells(cand, ctx.schema))
    except (AttributeError, TypeError, ValueError):
        return 0
