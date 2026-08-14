"""P6 — the campaign runner: generate, classify, and ask the P5 verdict model what died.

**"Killed" means a predicate returned `FAIL`** under the eight-state verdict model. That term did
not exist until P5 shipped; the v0 harness approximated it with a print statement, and the
difference is the whole reason this phase exists.

**The fact tree is built ONCE from the clean filing and patched per mutant.** Re-parsing the
workbook for each of thousands of mutants would cost hours, and the patch is exact rather than an
approximation: the edited cells take the mutant's literal, and every cell in the edit's transitive
downstream cone takes the mutant's recalculated value. A cell outside the cone cannot change.
"""

from __future__ import annotations

import json
import copy
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cdfc.qualify.campaign import Campaign, ClassTally, tally
from cdfc.qualify.fault_model import (
    FAULT_CLASSES,
    FAULT_MODEL_VERSION,
    REMOVE,
    Dtype,
    FaultOperator,
    Site,
    model_digest,
)
from cdfc.qualify.observability import Observability, classify, cone_for, grid_of
from cdfc.qualify.surgery import CellEdit, MutantRecord, plan_edit, seed_mutant

CellRef = tuple[str, str]


@dataclass(frozen=True, slots=True)
class MutantOutcome:
    record: MutantRecord
    observability: Observability
    distinguishing: tuple[str, ...]
    reachable: bool
    killed_by: tuple[str, ...]
    # The cells the evaluator COULD NOT COMPUTE while classifying this mutant. Kept apart from
    # `distinguishing` because they are the opposite kind of fact: a distinguishing cell is one
    # where the mutant and the base DIFFER, a blocked cell is one where we cannot say. Recording
    # the second as the first is what made `I` unreachable.
    blocked: tuple[str, ...] = ()
    # Predicates that FIRED on this mutant while it was outside their read set. The control arm:
    # a fire here is an apparatus failure, not a kill, so it never enters `killed_by` or `K`.
    spurious_fires: tuple[str, ...] = ()

    @property
    def killed(self) -> bool:
        return bool(self.killed_by)

    def as_row(self) -> dict[str, Any]:
        return self.record.as_row() | {
            "observability": str(self.observability),
            "distinguishing": list(self.distinguishing[:32]),
            "n_distinguishing": len(self.distinguishing),
            "reachable": self.reachable,
            "killed_by": list(self.killed_by),
            "blocked": list(self.blocked[:32]),
            "n_blocked": len(self.blocked),
            "spurious_fires": list(self.spurious_fires),
            "n_spurious_fires": len(self.spurious_fires),
        }


def plan_mutants(
    sites: Sequence[Site],
    *,
    rng: Any,
    values: Mapping[CellRef, Any],
    partner_ctx: Any = None,
) -> list[tuple[str, FaultOperator, Site, list[tuple[Site, Any]]]]:
    """Every `(class, operator, site, edits)` the model produces over these sites.

    An operator that does not apply at a site yields NOTHING — no mutant, not a no-op mutant. A
    no-op mutant is unobservable by construction and would inflate `U` with the operator's
    inapplicability rather than with the fault model's invisibility.
    """
    out = []
    for cls in FAULT_CLASSES:
        for op in cls.operators:
            for site in sites:
                if site.dtype not in cls.applies_to:
                    continue
                current = values.get((site.sheet, site.ref))
                new = op.mutate(current, site, rng)
                if new is None:
                    continue
                edits = [(site, new)]
                if op.partner is not None and partner_ctx is not None:
                    pair = op.partner(site, partner_ctx)
                    if pair is None:
                        continue          # a pair operator with no partner is not a pair mutant
                    edits.append(pair)
                out.append((cls.id, op, site, edits))
    return out


@dataclass
class CampaignRunner:
    base: Path                 # the pinned blank, for the template side
    clean: Path                # the clean filing every mutant is a perturbation of
    out_dir: Path
    evaluate: Any              # (patched_tree) -> tuple[str, ...] of predicate ids that FAILed
    read_cells: frozenset[str] = field(default_factory=frozenset)
    _clean_grid: Any = None
    _clean_literals: Any = None

    def clean_grid(self) -> Any:
        if self._clean_grid is None:
            self._clean_grid = grid_of(self.clean)
        return self._clean_grid

    def run_one(
        self, class_id: str, op: FaultOperator, edits: Sequence[tuple[Site, Any]], seed: int
    ) -> MutantOutcome:
        cell_edits = [
            plan_edit(self.clean, s.sheet, s.ref, v, op.id) for s, v in edits
        ]
        target = self.out_dir / "mutants" / f"{op.id}__{edits[0][0].sheet}__{edits[0][0].ref}.xlsx"
        record = seed_mutant(
            self.clean, cell_edits, target, fault_class=class_id, operator_id=op.id, seed=seed
        )
        edited: list[CellRef] = [(s.sheet, s.ref) for s, _v in edits]
        cone = cone_for(self.clean, edited)
        full = self.clean_grid()
        clean_grid = grid_of(self.clean, cone=cone, baseline=full)
        mutant_grid = grid_of(target, cone=cone, baseline=full)
        obs, cells = classify(clean_grid, mutant_grid)

        # A literal edit moves no key of the recalculated grid — `recalculate` returns values for
        # FORMULA cells only. Comparing the literals is part of observability, not a patch on it.
        from cdfc.qualify.observability import literal_differences

        moved = literal_differences(self.clean, target)

        # --- THE PROMOTION, AND WHY IT IS DRIVEN BY `moved` ALONE ---------------------------
        #
        # This block read `cells = frozenset(cells) | moved` and then promoted on `if cells`.
        # That is correct for an UNOBSERVABLE verdict, whose second return value is EMPTY — so
        # `cells == moved` and the promotion fires exactly when a literal moved.
        #
        # It is wrong for INDETERMINATE, whose second return value is the **blocked** set: the
        # cells the evaluator COULD NOT COMPUTE, non-empty by construction. So every
        # INDETERMINATE verdict was promoted to OBSERVABLE and the blocked cells were recorded
        # as its `distinguishing` set. Measured on the committed campaign: `classify` says
        # OBSERVABLE 739 / UNOBSERVABLE 12 / INDETERMINATE 22, and all 22 were banked into `O`.
        # Published `I` was 0 for every fault class — a construction, not a measurement, and the
        # measurement file's stated reason for it ("this model has none") was false.
        #
        # `I` is excluded from `O` deliberately: it is the population where we cannot tell
        # whether the fault is invisible or whether WE are, and folding it into either direction
        # moves `K/O`. Promoting it into `O` moves it in the direction that flatters us.
        blocked = frozenset() if obs is Observability.OBSERVABLE else frozenset(cells)
        seen = (frozenset(cells) if obs is Observability.OBSERVABLE else frozenset()) | moved
        if moved and obs is not Observability.OBSERVABLE:
            obs = Observability.OBSERVABLE
            blocked = frozenset()
        cells = seen
        distinguishing = tuple(sorted(f"{s}!{r}" for s, r in cells))
        blocked_cells = tuple(sorted(f"{s}!{r}" for s, r in blocked))

        reachable = bool(set(distinguishing) & self.read_cells) if self.read_cells else True
        # --- THE CONTROL ARM, AND WHY IT IS EVALUATED AT ALL --------------------------------
        #
        # This read `if obs is OBSERVABLE and reachable:` — so a mutant OUTSIDE every predicate's
        # read set was never evaluated, `killed_by` was empty for all of them by construction, and
        # the funnel's published *"control-arm spurious fires: 0 — the threshold is exactly zero"*
        # was a constant. It would read 0 for a predicate that fired on EVERY mutant, which is
        # precisely the flag-everything baseline the control arm exists to reject.
        #
        # Unreachable mutants are now evaluated, and their fires are recorded SEPARATELY. They do
        # NOT enter `killed_by`, because a fire on a cell the predicate does not read is an
        # apparatus failure rather than a kill, and letting it into `K` would inflate the rate with
        # exactly the behaviour being policed. 56 of 773 mutants are unreachable, so the arm costs
        # a fourteenth of the campaign.
        killed: tuple[str, ...] = ()
        spurious: tuple[str, ...] = ()
        if obs is Observability.OBSERVABLE:
            fired = tuple(self.evaluate(target, mutant_grid, edited))
            if reachable:
                killed = fired
            else:
                spurious = fired
        target.unlink(missing_ok=True)     # the bytes are re-derivable from the record and the seed
        return MutantOutcome(record, obs, distinguishing, reachable, killed, blocked_cells, spurious)

    def literal(self, sheet: str, ref: str) -> Any:
        from cdfc.qualify.observability import extract

        if self._clean_literals is None:
            self._clean_literals = dict(extract(self.clean).literals)
        return self._clean_literals.get((sheet, ref))


def summarise(
    outcomes: Iterable[MutantOutcome],
    *,
    campaign_id: str,
    site_set_digest: str,
    evaluator_version: str,
    base_sha256: str,
    sampling_rule: str,
    predicate_set_digest: str = "",
) -> Campaign:
    counts: dict[str, dict[str, int]] = {}
    indeterminate_cells: dict[str, list[str]] = {}
    for o in outcomes:
        c = counts.setdefault(
            o.record.fault_class, {"G": 0, "U": 0, "I": 0, "R": 0, "K": 0}
        )
        c["G"] += 1
        if o.observability is Observability.UNOBSERVABLE:
            c["U"] += 1
        elif o.observability is Observability.INDETERMINATE_OBSERVABILITY:
            c["I"] += 1
            indeterminate_cells.setdefault(o.record.fault_class, []).extend(o.distinguishing[:4])
        else:
            if not o.reachable:
                c["R"] += 1
            if o.killed:
                c["K"] += 1
    return Campaign(
        campaign_id=campaign_id,
        by_fault_class={
            k: tally(G=v["G"], U=v["U"], I=v["I"], R=v["R"], K=v["K"]) for k, v in counts.items()
        },
        fault_model_digest=model_digest(),
        site_set_digest=site_set_digest,
        evaluator_version=evaluator_version,
        base_sha256=base_sha256,
        sampling_rule=sampling_rule,
        predicate_set_digest=predicate_set_digest,
        indeterminate_cells={k: tuple(sorted(set(v))) for k, v in indeterminate_cells.items()},
    )


def write_reports(campaign: Campaign, outcomes: Sequence[MutantOutcome], out_dir: Path) -> Path:
    """`manifest.json` · `killed.jsonl` · `unobservable.jsonl` · `indeterminate.jsonl` ·
    `unreachable.jsonl`.

    **An unobservable mutant is RETAINED with its reason, never destroyed** (§0.7). Destroying it
    makes `U/G` unauditable and takes P10's residue feedstock with it. NC-Q37.
    """
    target = out_dir / campaign.campaign_id
    target.mkdir(parents=True, exist_ok=True)
    (target / "manifest.json").write_text(
        json.dumps(campaign.as_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    buckets = {
        "killed.jsonl": [o for o in outcomes if o.killed],
        "unobservable.jsonl": [o for o in outcomes if o.observability is Observability.UNOBSERVABLE],
        "indeterminate.jsonl": [
            o for o in outcomes if o.observability is Observability.INDETERMINATE_OBSERVABILITY
        ],
        "unreachable.jsonl": [
            o for o in outcomes
            if o.observability is Observability.OBSERVABLE and not o.reachable
        ],
    }
    for name, rows in buckets.items():
        (target / name).write_text(
            "".join(json.dumps(_row_with_reason(o, name), sort_keys=True) + "\n" for o in rows),
            encoding="utf-8",
        )
    return target


def _row_with_reason(o: MutantOutcome, bucket: str) -> dict[str, Any]:
    reasons = {
        "unobservable.jsonl": "every recalculated cell value is equal and no not_run cell was traversed",
        "indeterminate.jsonl": "the grids are equal but the recalculation traversed a cell this "
                               "evaluator could not compute; the cells are named below",
        "unreachable.jsonl": "observable, but no distinguishing cell lies in any predicate's read set",
        "killed.jsonl": "at least one predicate returned FAIL under the P5 verdict model",
    }
    return o.as_row() | {"reason": reasons[bucket]}
