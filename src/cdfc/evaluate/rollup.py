"""P5-B4 — roll-up: from evaluations to cells, and the table is built from the DENOMINATOR.

**`materialise` builds a row for every field-surface cell BEFORE evaluation.** That is the
structural reason closure cannot have a hole: the table is the denominator, and evaluations
overwrite rows rather than creating them. A table accumulated from the evaluations has exactly as
many rows as things that happened, and the cells nothing happened to are the ones that matter.

**A cell is clean only if every predicate binding it passed.** `roll_up` takes the max under
`PRECEDENCE`, and `NOT_RUN` beats `PASS` — the audit's resolution, because *the settled fraction
falls, it does not silently succeed.*

**Two exceptions, both of them repairs to a way the fraction could rise:**

- An **empty** evaluation set is `NO_PREDICATE(no_predicate.not_yet_synthesised)`, which stays in
  the denominator. A gap in us is not a smaller job.
- An **INFORMATIONAL-only** cell rolls up to `NO_PREDICATE(no_predicate.rule_ambiguous)`, never to
  `INFORMATIONAL`. `INFORMATIONAL` leaves `inScope`, so without this rule adding a row to
  `template_defects.yaml` would raise the headline fraction. **A cell we have no verdict on is a
  gap in US** — the repair sits at the roll-up because the defect table belongs to another phase.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any

from cdfc.verdict import ItemState, ReasonCode, in_scope, requalification_flag, worst


@dataclass(frozen=True, slots=True)
class Evaluation:
    predicate_id: str
    version: int
    state: ItemState
    reason: ReasonCode | None
    witness: tuple[str, ...] = ()
    settles: bool = True
    scope_kind: str | None = None
    informational_note: str | None = None


@dataclass(frozen=True, slots=True)
class RunCell:
    stable_key: str
    state: ItemState
    reason: ReasonCode | None
    settled_by: str | None
    evaluations: tuple[Evaluation, ...] = ()
    scope_kind: str | None = None

    @property
    def in_scope(self) -> bool:
        return in_scope(self.state, self.reason, self.scope_kind)

    @property
    def requalify(self) -> bool:
        return requalification_flag(self.scope_kind)

    @property
    def lowered_by_rollup(self) -> bool:
        """At least one PASS and at least one non-PASS. The audit resolution's effect size."""
        states = {e.state for e in self.evaluations}
        return ItemState.PASS in states and bool(states - {ItemState.PASS})


def roll_up(
    evals: Sequence[Evaluation],
) -> tuple[ItemState, ReasonCode | None, str | None, str | None]:
    """`(state, reason, settled_by, scope_kind)`."""
    if not evals:
        return ItemState.NO_PREDICATE, ReasonCode.NP_NOT_YET_SYNTHESISED, None, None

    # D-P5-05 / F14. An INFORMATIONAL-only cell is a cell we have no verdict on.
    if all(e.state is ItemState.INFORMATIONAL for e in evals):
        return ItemState.NO_PREDICATE, ReasonCode.NP_RULE_AMBIGUOUS, None, None

    top = worst(tuple(e.state for e in evals))
    winners = [e for e in evals if e.state is top]
    # Ties are broken by predicate id so the rolled-up reason cannot depend on evaluation order.
    winner = sorted(winners, key=lambda e: (e.predicate_id, e.version))[0]
    settled_by = winner.predicate_id if (top in (ItemState.PASS, ItemState.FAIL) and winner.settles) else None
    return top, winner.reason, settled_by, winner.scope_kind


def materialise(
    cells: Sequence[str],
    *,
    reasons: Mapping[str, ReasonCode] | None = None,
) -> dict[str, RunCell]:
    """Every field-surface cell, before evaluation, defaulting to `NO_PREDICATE`.

    **`not_yet_synthesised` is the default and it was the ONLY value, which made it a lie for 735
    cells.** That code says *nobody has written a check for this cell*. For a cell that a harvested
    candidate binds — and which is unchecked because the kill gate REFUSED that candidate — the
    true statement is `no_predicate.failed_qualification`, and the vocabulary has carried it since
    P4 precisely for this case: `qualify/pipeline.py` records `cells_would_have_covered` on every
    rejection expressly so the count can be attributed here.

    The difference is not cosmetic. *Nobody wrote a check* is a gap in our authoring backlog. *A
    check was written and refused for never catching anything* is a gap in the evidence — and it is
    the one a reader of a coverage report needs, because it tells them the cell is unchecked for a
    reason somebody already investigated.

    `reasons` supplies the per-cell override. It changes NO state and NO count: every cell here is
    `NO_PREDICATE` either way and the settled fraction is untouched.
    """
    override = dict(reasons or {})
    return {
        key: RunCell(
            stable_key=key,
            state=ItemState.NO_PREDICATE,
            reason=override.get(key, ReasonCode.NP_NOT_YET_SYNTHESISED),
            settled_by=None,
            evaluations=(),
        )
        for key in sorted(set(cells))
    }


def roll_up_run(
    cells: Mapping[str, RunCell],
    checks: Sequence[Any],
    *,
    cells_of: Any = None,
) -> tuple[RunCell, ...]:
    """Attach each check to the cells it bound, then roll each cell up.

    `cells_of(check) -> Sequence[str]` defaults to the check's own `cells_bound`. A check whose
    cells are not in the materialised table is DROPPED from the roll-up and that is deliberate:
    the denominator is the field surface, and a predicate binding a cell outside it would add a
    row the closure sum does not know about.
    """
    by_cell: dict[str, list[Evaluation]] = {k: [] for k in cells}
    for chk in checks:
        for cell in (cells_of(chk) if cells_of else getattr(chk, "cells_bound", ())):
            if cell in by_cell:
                by_cell[cell].append(
                    Evaluation(
                        predicate_id=chk.predicate_id,
                        version=chk.version,
                        state=chk.state,
                        reason=chk.reason,
                        witness=tuple(getattr(chk, "witness", ())),
                        settles=bool(getattr(chk, "settles", True)),
                        scope_kind=getattr(chk, "scope_kind", None),
                        informational_note=getattr(chk, "informational_note", None),
                    )
                )
    out: list[RunCell] = []
    for key in sorted(cells):
        evs = tuple(by_cell[key])
        state, reason, settled_by, scope_kind = roll_up(evs)
        # THE MATERIALISED REASON SURVIVES AN EMPTY EVALUATION SET.
        #
        # `roll_up(())` returns the hard-coded `not_yet_synthesised`, which is the right default
        # and the wrong answer when the caller already knows better — and it silently overwrote the
        # reason `materialise` had just set, so supplying one had no effect at all. That is the
        # shape this project keeps finding: a value computed upstream, discarded downstream, and
        # nothing in between to notice.
        #
        # It is scoped tightly: ONLY when no predicate evaluated the cell, and ONLY over the reason.
        # The state stays `NO_PREDICATE` and no count moves.
        if not evs and cells[key].reason is not None:
            reason = cells[key].reason
        out.append(
            replace(
                cells[key],
                state=state, reason=reason, settled_by=settled_by,
                evaluations=evs, scope_kind=scope_kind,
            )
        )
    return tuple(out)
