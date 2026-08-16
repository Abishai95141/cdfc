"""P10 — the reference run WITH its liveness proof. One assembler, so nothing builds it twice.

`p5_run.run_filing` measures the P5 layer and keeps doing exactly that. This module is the
production path: **`cdfc run` calls it, and there is no flag to turn the canary loop off.** A
self-test that runs only when a flag is set is a self-test that is off in production, which is the
failure this layer exists to catch one level up (NC-C09) — and the same argument applies to the
loop that carries it.

## The canary population, and the selector is the design's rather than this file's

`plan/05` says the loop runs over *"each ACTIVE or PROVISIONAL predicate"*. **No predicate in this
repository is ACTIVE**: the P7 funnel admitted none of 348, so a loop over the admitted set would
run over the empty set and report `VALID` having demonstrated nothing.

So the reference run uses the PRE-GATE fixture set, `p5_run.promote`-labelled like every other
number here, restricted to the predicates that cleared **G2's kill stage** — the ones the committed
campaign records at least one kill for. That restriction is not chosen to make a number look good:
a predicate with no kill is rejected by G2 with `g2.no_kill` and never reaches the registry, so it
is out of the canary population for the same reason it is out of the admitted set. On the committed
campaign it selects 125 of 348, and the other 223 are exactly the funnel's `no_kill` column — two
layers, built independently, selecting the same set.

**Both numbers are published.** `docs/measurements/P10-canary-cost.md` carries the run over all 348
as well, which is `INVALID(WHOLESALE_INAPPLICABILITY)` — because 223 checks that have never been
shown to catch anything are 223 checks whose liveness this filing cannot demonstrate, and that is
the honest headline. Reporting only the restricted run would be choosing the population after
seeing the result.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

from cdfc.evaluate.celrt import CelRuntime
from cdfc.evaluate.liveness import LivenessInputs, inputs_for
from cdfc.evaluate.run import RunResult, execute
from cdfc.evaluate.selection import RunProfile
from cdfc.facts.build import fact_set_for
from cdfc.measure.p5_run import (
    FME,
    REGISTRY_ROOT,
    TEMPLATE_COMPUTED,
    catalogue,
    denominator,
    fme_harvest,
    fme_surface,
    promote,
)
from cdfc.predicates.host_fns import default_registry
from cdfc.qualify.campaign_store import CAMPAIGNS
from cdfc.selfcheck.thresholds import MAX_WITNESSES

CAMPAIGN_ID = "fme-v3-seed20260810"

# What the surface must say when the loop did not run. Absence is rendered in words, never as
# zeros: `canariesRun: 0` and `livenessProof: null` are different claims, and only the second one
# is true of a run that never asked.
NO_LIVENESS = (
    "LIVENESS NOT DEMONSTRATED: the canary loop did not run on this filing, so nothing here "
    "states that the checks were working when they were applied to it."
)


class CampaignAbsent(FileNotFoundError):
    """No stored campaign, therefore no stored kill cases, therefore nothing to replay."""


@lru_cache(maxsize=2)
def killed_rows(campaign_id: str = CAMPAIGN_ID) -> tuple[dict[str, Any], ...]:
    path = CAMPAIGNS / campaign_id / "killed.jsonl"
    if not path.is_file():
        raise CampaignAbsent(
            f"{path} does not exist. Liveness witnesses are PROJECTED from the stored campaign — "
            "the same rows G2 scored — so a build with no campaign has no kill case to replay and "
            "must say so rather than reporting a loop that ran over nothing. Run `make campaign`."
        )
    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )


@lru_cache(maxsize=2)
def kill_stage_ids(campaign_id: str = CAMPAIGN_ID) -> frozenset[str]:
    """Predicate ids the campaign records at least one kill for — G2's kill stage, not a filter."""
    out: set[str] = set()
    for row in killed_rows(campaign_id):
        out.update(str(p) for p in (row.get("killed_by") or ()))
    return frozenset(out)


@lru_cache(maxsize=1)
def all_predicates() -> tuple[Any, ...]:
    return tuple(promote(c) for c in fme_harvest().candidates)


def population(*, restrict_to_kill_stage: bool = True) -> tuple[Any, ...]:
    """The predicates a run evaluates. **33 of 348, and the restriction is the KILL STAGE.**

    A predicate outside `kill_stage_ids()` never killed a mutant in the pinned campaign — it is
    exactly the set G2 refused as `g2.no_kill`. Running only predicates that have demonstrated
    they can catch something is the right rule, and it is why the liveness loop can replay a
    stored kill case for every predicate in the run.

    **What was wrong was not the restriction. It was the silence.** The 315 excluded predicates
    bind 735 field-surface cells, and those cells were reported as
    `no_predicate.not_yet_synthesised` — *nobody has written a check for this cell* — when a check
    exists and was refused. `unchecked_reasons()` below supplies the true code.
    """
    if not restrict_to_kill_stage:
        return all_predicates()
    ids = kill_stage_ids()
    return tuple(p for p in all_predicates() if p.id in ids)


def unchecked_reasons(
    predicates: Sequence[Any], schema: Any, cells: Sequence[str]
) -> dict[str, Any]:
    """cell -> `no_predicate.failed_qualification`, for cells a REFUSED candidate binds.

    The map covers only cells bound by a harvested candidate that is not in the run population.
    Every other unchecked cell keeps `not_yet_synthesised`, which for it is true: no candidate
    binds it at all, because the workbook declares no constraint there that the harvest could read.

    **This changes no state and no count.** Every cell here is `NO_PREDICATE` before and after, and
    the settled fraction is identical — asserted by
    `tests/unit/test_unchecked_reasons.py::test_reasons__the_settled_fraction_is_unchanged`.
    """
    from cdfc.predicates.ast_walker import bound_cells
    from cdfc.verdict import ReasonCode

    running = {p.id for p in predicates}
    surface = set(cells)
    out: dict[str, Any] = {}
    for cand in fme_harvest().candidates:
        if cand.id in running:
            continue
        try:
            bound = bound_cells(cand, schema)
        except (AttributeError, TypeError, ValueError):
            continue
        for cell in bound:
            if cell in surface:
                out[cell] = ReasonCode.NP_FAILED_QUALIFICATION
    return out


@lru_cache(maxsize=1)
def runtime() -> CelRuntime:
    return CelRuntime(profile_version="P10", host_fns=default_registry())


def liveness_for(
    filing: Path,
    *,
    predicates: Sequence[Any] | None = None,
    max_witnesses: int = MAX_WITNESSES,
    passcase: Path = TEMPLATE_COMPUTED,
) -> LivenessInputs:
    return inputs_for(
        filing,
        FME,
        predicates=list(predicates if predicates is not None else population()),
        schema=fme_harvest().schema,
        rt=runtime(),
        passcase=passcase,
        killed_rows=list(killed_rows()),
        max_witnesses=max_witnesses,
    )


def run_filing(
    filing: Path,
    *,
    predicates: Sequence[Any] | None = None,
    max_witnesses: int = MAX_WITNESSES,
) -> RunResult:
    """One filing, checked, with its liveness proof taken on the same execution."""
    preds = list(predicates if predicates is not None else population())
    res = fme_harvest()
    n, cells, _state = fme_surface()
    rt = runtime()
    return execute(
        filing,
        catalogue=catalogue(),
        predicates=preds,
        schema=res.schema,
        field_surface=n,
        denominator=denominator(),
        registry_root=REGISTRY_ROOT,
        profile=RunProfile(name="default", digest="p10"),
        facts=fact_set_for(filing, FME),
        surface_cells=list(cells),
        rt=rt,
        liveness=liveness_for(filing, predicates=preds, max_witnesses=max_witnesses),
        unchecked_reasons=unchecked_reasons(preds, res.schema, list(cells)),
    )
