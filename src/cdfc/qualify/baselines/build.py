"""P7-B3 — assemble the three baselines' kill sets from committed campaign evidence.

Nothing is re-run here. `killed.jsonl` records every observable mutant's edit and which predicates
killed it; each baseline is a RULE applied to that record. One campaign, one denominator, three
sets, and each set's caveat travels with it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cdfc.qualify.baselines import b0_template, b1_invariants, b2_degenerate
from cdfc.qualify.baselines.b1_invariants import NOT_DAIKON
from cdfc.qualify.g2_kill import BaselineResult

B0_CAVEAT = (
    "B0 is drawn from this repository's own formula-derived harvest classes, and the candidate "
    "under test is excluded from it so the comparison is never with itself."
)
B2_CAVEAT = (
    "B2 is evaluated against each mutant's RECORDED EDIT rather than against a recalculated "
    "filing, so it sees a blank or an error the edit wrote directly and not one produced "
    "downstream by recalculation. That UNDER-counts B2, which flatters the candidate."
)


def killed_rows(campaign_id: str, root: Path = Path("reports/campaigns")) -> list[Mapping]:
    p = root / campaign_id / "killed.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def clean_observations(filing_cells: Mapping[str, object]) -> list[Mapping[str, Decimal]]:
    """One observation per clean filing. ONE is not a corpus, and B1 says so."""
    obs: dict[str, Decimal] = {}
    for cell, v in filing_cells.items():
        try:
            obs[cell] = Decimal(str(v))
        except (InvalidOperation, ValueError, TypeError):
            continue
    return [obs] if obs else []


def build(
    stored,
    *,
    campaign_id: str,
    class_of_predicate: Mapping[str, str],
    clean_cells: Mapping[str, object],
    exclude: Sequence[str] = (),
    root: Path = Path("reports/campaigns"),
) -> tuple[BaselineResult, tuple[b1_invariants.Invariant, ...]]:
    rows = killed_rows(campaign_id, root)
    invariants = b1_invariants.mine(clean_observations(clean_cells))
    # B0's MEMBERSHIP is retained, not just its union, so `g2_kill` can ask what B0 kills WITHOUT
    # the candidate as one of its members. Only B0 has members — B1 and B2 are rules applied to the
    # campaign record, and the candidate is not in either of them, so excluding it from those is
    # not a correction but a hole. Before this, `g2_kill` subtracted the candidate's entire kill set
    # from all three, which made every marginal equal `|mine|` and no baseline able to affect any
    # decision.
    b0_members = {
        pid: frozenset(stored.mutants(pid))
        for pid in sorted(b0_template.members(class_of_predicate) - set(exclude))
    }
    return (
        BaselineResult(
            per_baseline={
                "B0": b0_template.kill_set(stored, class_of_predicate, exclude=exclude),
                "B1": b1_invariants.kill_set(stored, rows, invariants),
                "B2": b2_degenerate.kill_set(rows),
            },
            caveats={"B0": B0_CAVEAT, "B1": NOT_DAIKON, "B2": B2_CAVEAT},
            members={"B0": b0_members},
        ),
        invariants,
    )
