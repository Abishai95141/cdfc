"""P5-B1 — F6: which predicates run, against the pinned registry root.

**A `PROVISIONAL` predicate STILL RUNS.** Its result appears in `run_check` with its state, and
its cells do **not** enter the settled numerator. Not running it would hide a finding; counting it
would claim coverage nobody qualified. Running it and withholding the number is the only option
that does neither.

**A predicate bound to a different template is not evaluated**, and its cells land in
`NO_PREDICATE(no_predicate.not_yet_requalified)` rather than silently vanishing — the gap is a gap
in us, and it stays in the denominator.

**An empty active set is not an error.** It is an honest report with `settled.total == 0` and run
state `VALID`. Without that branch the selector is a reject-everything baseline whose zero looks
like a measurement.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from cdfc.predicates.envelope import Predicate


@dataclass(frozen=True, slots=True)
class RunProfile:
    name: str
    digest: str
    exclude: tuple[str, ...] = ()
    # P9-B1's non-admitted TEMPLATE_DIFF demonstration runs under this flag. A spike run may not
    # write `settled` for any cell — the demonstration is allowed, the coverage claim is not.
    spike: bool = False


@dataclass(frozen=True, slots=True)
class Selection:
    active: tuple[Predicate, ...]
    provisional: tuple[Predicate, ...]
    not_requalified: tuple[str, ...]
    deactivated: tuple[tuple[str, str], ...]
    registry_root: str
    profile: RunProfile = field(default=RunProfile(name="default", digest=""))

    @property
    def runnable(self) -> tuple[Predicate, ...]:
        """Everything that RUNS. Provisional predicates run; they just do not settle."""
        return (*self.active, *self.provisional)

    @property
    def settles(self) -> frozenset[str]:
        """The predicate ids whose results may enter the settled numerator."""
        return frozenset() if self.profile.spike else frozenset(p.id for p in self.active)


class SelectionError(ValueError):
    pass


def select(
    registry_root: str,
    template_sha256: str,
    profile: RunProfile,
    *,
    predicates: Sequence[Predicate],
    deactivated: Sequence[tuple[str, str]] = (),
) -> Selection:
    """Partition the registry into what runs, what settles, and what is missing."""
    if not registry_root:
        raise SelectionError(
            "a selection with no registry root cannot be re-derived: the report would name a "
            "predicate set nobody can reconstruct"
        )
    dead = {pid for pid, _uri in deactivated}
    active: list[Predicate] = []
    provisional: list[Predicate] = []
    foreign: list[str] = []
    for p in predicates:
        if p.id in dead or p.id in profile.exclude:
            continue
        if p.template != template_sha256:
            foreign.append(p.id)
            continue
        if p.state == "ACTIVE":
            active.append(p)
        elif p.state == "PROVISIONAL":
            provisional.append(p)
        # QUARANTINED and WITHDRAWN do not run at all; their cells fall to the materialised
        # default, which is NO_PREDICATE — a gap in us, counted.
    return Selection(
        active=tuple(sorted(active, key=lambda p: p.id)),
        provisional=tuple(sorted(provisional, key=lambda p: p.id)),
        not_requalified=tuple(sorted(foreign)),
        deactivated=tuple(sorted(deactivated)),
        registry_root=registry_root,
        profile=profile,
    )


def admission_state(sel: Selection) -> str:
    """`PRE-GATE` until every active predicate carries a G4 record. Computed, never hand-set."""
    if not sel.active:
        return "PRE-GATE"
    qualified = all(
        getattr(p.qualification, "campaign_id", "").startswith("G4-") for p in sel.active
    )
    return "POST-GATE" if qualified else "PRE-GATE"
