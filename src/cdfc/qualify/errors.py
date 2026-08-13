"""P7-B1 — the closed error hierarchy of the qualification pipeline.

**Closed, and each type is a different remedy.** A single `QualificationError` would let a caller
write one `except` and treat *"this candidate is bad"* the same as *"our apparatus is broken"* —
and those two have opposite responses: the first rejects a predicate, the second **blocks the whole
admission batch**. That distinction is load-bearing at G3's control arm, where a non-zero spurious
fire is an apparatus defect and softening it into a per-predicate rejection is how the
flag-everything predicate gets admitted.

    QualifyError
      ├── UnsourcedObligationError      the candidate cannot be gated at all
      ├── GateOrderError                the pipeline ran out of order — a COST control, not a verdict
      ├── ApparatusError                OUR instrument is wrong; the batch is blocked
      │     ├── UnexercisedClaimError   a claimed fault class has O == 0 on this campaign
      │     └── ClaimPostdatesCampaignError   the claim was written after its own evidence
      └── AdmissionError                the registry refuses
            ├── UnqualifiedPredicateError
            └── UnsignedAdmissionError

There is no error for *"the candidate failed a gate"*. **A rejection is a value, not an
exception** — a `RejectionRow` carrying the gate, the measured number and
`cells_would_have_covered` — because a rejection is evidence the report has to publish and an
exception is a thing a caller can swallow.
"""

from __future__ import annotations


class QualifyError(RuntimeError):
    """Root of the qualification hierarchy. Never raised directly."""


class UnsourcedObligationError(QualifyError):
    """The candidate's obligation is missing, or its `source` is unset.

    Raised by `g0_scope.check` so that a future predicate kind cannot enter the funnel by
    defaulting into a pass. There is no seventh G0 outcome and no skip.
    """


class GateOrderError(QualifyError):
    """A gate ran before a cheaper gate that precedes it in `GATE_ORDER`.

    NC-Q34. The outcome of an out-of-order run is usually the same; the COST is not. A candidate
    that fails G0's free structural check must never consume a mutation campaign, and a candidate
    Z3 would have proved degenerate must never be admitted on an expensive number instead.
    """


class ApparatusError(QualifyError):
    """OUR instrument is wrong. Blocks the batch; never softened into a per-predicate rejection.

    G3's control-arm threshold is exactly zero, and that is derived rather than chosen: a control
    site lies outside `upstream_closure(read_set(p))`, so a fire there means either an undeclared
    key read (impossible — P4's both-ways AST check rejects it at admission) or a leak in the fact
    table. Both are defects here, not findings about a predicate.
    """


class UnexercisedClaimError(ApparatusError):
    """A predicate claims a fault class the campaign never observed (`O == 0`).

    F1. Claiming F11 while the observability filter reports `O == 0` for F11 IS the F19 failure,
    and after that repair this is the symptom by which F19 would be caught again if it regressed.
    An unexercised claim is not a claim.
    """


class ClaimPostdatesCampaignError(ApparatusError):
    """`claims_fault_classes` was written after the campaign that scores it.

    The same instrument, in the same shape, as the fill brief's commit-order test. A claim
    narrowed after seeing the kill vector is a denominator built out of its own numerator.
    """


class AdmissionError(QualifyError):
    """The registry refuses to admit."""


class UnqualifiedPredicateError(AdmissionError):
    """No qualification row exists. BARRIER 3, and it is a runtime invariant, not a lint."""


class UnsignedAdmissionError(AdmissionError):
    """No valid detached signature over the batch manifest (R7).

    The gate is mechanical; shipping a check that will be applied to a regulated filing is not.
    """


class SuspiciousUniformityError(ApparatusError):
    """A gate reported the same measurement for every candidate in a population where that is
    not credible.

    NC-Q35: `provisos_total == 0` across every `source == STATUTE` candidate means the marker list
    is empty, not that the instrument has no provisos. **Scoped to STATUTE**, because under F9
    every harvested candidate is `source: TEMPLATE` with a legitimate zero, and an unscoped guard
    would fire on a correct build — and would then be "fixed" by deleting it.
    """
