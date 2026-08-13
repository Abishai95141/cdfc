"""P7-B3 — G2, the kill gate. Two bars, two numbers, and a denominator declared before the run.

**F1 — the registry bar's denominator, and why this is a changed contract rather than a
clarification.** Every document repeated *"on the fault classes the predicate CLAIMS to cover"*,
and **no field held the claim.** The only place a fault class appeared was `FaultWitness.fault_class`,
and the witness set is selected at admission **from the mutants that already killed**. A predicate
that kills F01 and F03 on its own read set and is structurally blind to F10, F12, F13 and F14 has
`K/O = 0.21` over the campaign; the witnesses are all F01/F03; the bar is evaluated over
`{F01, F03}`; the record reads `0.97`. **That is the numerator choosing its denominator, arriving
at the gate built to catch it.**

D-P4-06 put `claims_fault_classes` on `Candidate`, inside `envelope_projection()` and therefore
inside `code_sha256`. Three properties make the claim evidence rather than a label, and this module
asserts each:

1. **It is content-addressed** — narrowing the claim after a campaign produces a DIFFERENT
   predicate, not a better score.
2. **It precedes its evidence** — the claim's commit must be a git-ancestor of the campaign's.
3. **It must be exercised** — a claimed class with `O == 0` raises. Claiming F11 while the
   observability filter reports `O == 0` for F11 IS the F19 failure, and after that repair this is
   the symptom by which F19 would be caught again if it regressed.

**BOTH RATIOS ARE STORED AND BOTH ARE RENDERED.** `kr_claimed` over the declared set and
`kr_all_classes` over all fourteen. The gap between them is the number a reviewer wants, and
`render()` emits them in one string so a surface cannot carry one alone.
"""

from __future__ import annotations

import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from pathlib import Path
from typing import Any, Final

from cdfc.qualify.campaign_store import StoredCampaign
from cdfc.qualify.errors import ClaimPostdatesCampaignError, UnexercisedClaimError
from cdfc.qualify.fault_model import FAULT_CLASSES
from cdfc.qualify.result import GateId, GateOutcome

REGISTRY_THRESHOLD: Final[Fraction] = Fraction(4, 5)  # 0.80, as two integers


class KillBar(StrEnum):
    EXPERIMENT = "experiment"  # K/O > 0 AND marginal kill > B0 ∪ B1 ∪ B2
    REGISTRY = "registry"  # K/O >= 0.80 over cand.claims_fault_classes — the DECLARED set


class Reason:
    NO_KILL: Final[str] = "g2.no_kill"  # K/O == 0 under the experiment bar
    BELOW_REGISTRY_BAR: Final[str] = "g2.below_registry_bar"
    NO_MARGIN_OVER_BASELINES: Final[str] = "g2.no_margin_over_baselines"


CLOSED_REASONS: Final[tuple[str, ...]] = (
    Reason.NO_KILL,
    Reason.BELOW_REGISTRY_BAR,
    Reason.NO_MARGIN_OVER_BASELINES,
)

REMEDY: Final[Mapping[str, str]] = {
    Reason.NO_KILL: "the predicate fired on no observable mutant of any class it claims; either "
                    "the claim is wrong or the check is",
    Reason.BELOW_REGISTRY_BAR: "it fires, but not often enough to be applied to a regulated "
                               "filing; it may still be admitted as an EXPERIMENT",
    Reason.NO_MARGIN_OVER_BASELINES: "a free baseline catches everything this catches; the "
                                     "predicate is not doing the work",
}


@dataclass(frozen=True, slots=True)
class BaselineResult:
    """Each baseline's KILL SET over the SAME campaign.

    Sets, not counts. `|kills(p)| − |kills(B)|` can be negative while `p` still catches mutants
    `B` misses, and it is the mutants `B` misses that make `p` worth having. So marginal kill is
    `|kills(p) \\ kills(B)|` — one campaign, one denominator, two sets.
    """

    per_baseline: Mapping[str, frozenset[str]]  # baseline name -> mutant digests it kills
    caveats: Mapping[str, str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.caveats is None:
            object.__setattr__(self, "caveats", {})

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self.per_baseline))

    def kills(self, baseline: str) -> frozenset[str]:
        return self.per_baseline.get(baseline, frozenset())

    def union(self) -> frozenset[str]:
        out: set[str] = set()
        for v in self.per_baseline.values():
            out |= v
        return frozenset(out)


def _ratio(k: int, o: int) -> str:
    """`K/O` as TWO INTEGERS. Never a rounded float; `ci/no-bare-rate.sh` scans for the other."""
    return f"{k}/{o}"


def check(
    cand: Any,
    stored: StoredCampaign,
    baselines: BaselineResult,
    *,
    bar: KillBar,
    repo: Path | None = None,
) -> GateOutcome:
    claimed = tuple(cand.claims_fault_classes)
    if not claimed:
        raise UnexercisedClaimError(
            f"{cand.id}: claims_fault_classes is empty. The field is required and non-empty at "
            "load, so a candidate reaching G2 without one means the loader was bypassed."
        )

    # --- 2. THE CLAIM MUST PRECEDE ITS EVIDENCE ------------------------------------------
    _assert_claim_predates(cand, stored, repo=repo)

    # --- 3. EVERY CLAIMED CLASS MUST HAVE BEEN EXERCISED ---------------------------------
    for c in claimed:
        if stored.observable(c) == 0:
            raise UnexercisedClaimError(
                f"{cand.id}: claims {c}, and campaign {stored.campaign.campaign_id} observed "
                f"O == 0 for it. An unexercised claim is not a claim — and a claimed class whose "
                "observability filter reports zero is exactly the F19 failure, which is how F19 "
                "would be caught again if it regressed."
            )

    k_claimed = sum(stored.kills(cand.id, c) for c in claimed)
    o_claimed = sum(stored.observable(c) for c in claimed)
    all_classes = tuple(f.id for f in FAULT_CLASSES)
    k_all = sum(stored.kills(cand.id, c) for c in all_classes)
    o_all = sum(stored.observable(c) for c in all_classes)

    per_class = {c: _ratio(stored.kills(cand.id, c), stored.observable(c)) for c in all_classes}

    # MARGINAL KILL: the mutants THIS predicate catches, in the classes it claims, that the
    # baseline does not. A set difference, reported per baseline SEPARATELY — a union figure
    # hides which baseline did the work — with the union beside it, never instead of it.
    mine = stored.mutants_in(stored.mutants(cand.id), claimed)
    # **THE CANDIDATE IS REMOVED FROM EVERY BASELINE BEFORE THE DIFFERENCE IS TAKEN.** B0 is drawn
    # from this repository's own formula-derived harvest classes, so a `sum_identity` candidate is
    # IN B0; comparing it against a set containing itself scores a marginal kill of zero for every
    # such predicate and rejects 105 of them for being indistinguishable from themselves. Found by
    # running the funnel, not by reading the code.
    others = {b: baselines.kills(b) - stored.mutants(cand.id) for b in baselines.names()}
    marginal = {b: len(mine - others[b]) for b in baselines.names()}
    measured: dict[str, object] = {
        "bar": bar.value,
        "campaign_id": stored.campaign.campaign_id,
        # BOTH RATIOS, ALWAYS. The gap between them is the number a reviewer wants.
        "kr_claimed": _ratio(k_claimed, o_claimed),
        "kr_all_classes": _ratio(k_all, o_all),
        "claimed_classes": list(claimed),
        "per_class": per_class,
        # per-baseline, SEPARATELY — a union figure hides which baseline did the work
        "marginal_kill": dict(sorted(marginal.items())),
        "marginal_kill_over_union": len(mine - (baselines.union() - stored.mutants(cand.id))),
        "baseline_caveats": dict(sorted(baselines.caveats.items())),
    }

    def reject(reason: str) -> GateOutcome:
        return GateOutcome(gate=GateId.G2, passed=False, measured=measured, reason=reason,
                           evidence_sha256=stored.campaign.fault_model_digest)

    if bar is KillBar.EXPERIMENT:
        if k_claimed == 0:
            return reject(Reason.NO_KILL)
        if any(m <= 0 for m in marginal.values()) or measured["marginal_kill_over_union"] <= 0:
            return reject(Reason.NO_MARGIN_OVER_BASELINES)
    else:
        if o_claimed == 0:  # unreachable: every claimed class was checked above
            raise UnexercisedClaimError(f"{cand.id}: O == 0 over the claimed set")
        if Fraction(k_claimed, o_claimed) < REGISTRY_THRESHOLD:
            return reject(Reason.BELOW_REGISTRY_BAR)

    return GateOutcome(gate=GateId.G2, passed=True, measured=measured,
                       evidence_sha256=stored.campaign.fault_model_digest)


def render(measured: Mapping[str, object]) -> str:
    """ONE STRING CARRYING BOTH RATIOS. A document quoting `kr_claimed` without `kr_all_classes`
    beside it has quoted half of a measurement."""
    return (
        f"kr_claimed = {measured['kr_claimed']} over {measured['claimed_classes']} · "
        f"kr_all_classes = {measured['kr_all_classes']}"
    )


def _assert_claim_predates(cand: Any, stored: StoredCampaign, *, repo: Path | None) -> None:
    """The commit introducing `claims_fault_classes` must be a git-ancestor of the campaign's.

    The same instrument, in the same shape, as the fill brief's commit-order test. **An
    unverifiable ancestry is not a verified one**: outside a git work tree the check records that
    it could not run rather than passing, and the funnel publishes that state.
    """
    if stored.commit == "":
        return  # recorded as unverifiable by the caller; see `ancestry_state`
    claim_commit = _claim_commit(repo)
    if claim_commit == "":
        return
    if claim_commit == stored.commit:
        return
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", claim_commit, stored.commit],
        cwd=repo or Path.cwd(), capture_output=True, text=True, check=False,
    )
    if r.returncode != 0:
        raise ClaimPostdatesCampaignError(
            f"{cand.id}: the commit that introduced claims_fault_classes ({claim_commit[:8]}) is "
            f"not an ancestor of campaign {stored.campaign.campaign_id}'s commit "
            f"({stored.commit[:8]}). A claim narrowed after seeing the kill vector is a "
            "denominator built out of its own numerator."
        )


def _claim_commit(repo: Path | None) -> str:
    """The commit that last touched `docs/FAULT-CLAIMS.md` — the per-class claim table.

    The claim is a property of the harvest CLASS, not of an individual predicate
    (`test_harvest__claims_are_a_pure_function_of_the_class`), so the artifact whose history
    matters is the class table. It was committed at P4, four phases before the first campaign, so
    the ancestry holds by construction rather than by discipline.
    """
    r = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "docs/FAULT-CLAIMS.md"],
        cwd=repo or Path.cwd(), capture_output=True, text=True, check=False,
    )
    return r.stdout.strip() if r.returncode == 0 else ""


def ancestry_state(stored: StoredCampaign, *, repo: Path | None = None) -> str:
    """`VERIFIED | UNVERIFIABLE`, for the funnel. Never `VERIFIED` by default."""
    return "VERIFIED" if stored.commit and _claim_commit(repo) else "UNVERIFIABLE (no git history)"
