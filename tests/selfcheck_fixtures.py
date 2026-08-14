"""Shared assembly for the P10 liveness suite — imported, never re-derived per test file.

Building the filing image, harvesting the predicates and projecting the witnesses costs about a
second each; doing it once per test module is fine and doing it once per test is not. Everything
here is `lru_cache`d on the module, and every object it returns is treated as read-only by the
tests that take it.

**The population is the predicates that cleared G2's KILL stage, and that selector is the
design's, not this file's.** A predicate the campaign records no kill for is rejected by G2 with
`g2.no_kill` and never reaches the registry, so it is not in the canary population for the same
reason it is not in the admitted set. On the committed campaign that is 125 of 348, and the other
223 are precisely the funnel's `no_kill` column — the two layers were built independently and they
select the same set.

Everything these fixtures produce is **PRE-GATE**: no candidate in this repository has been through
the gates, `p5_run.promote` labels the promotion, and every number derived here inherits that label.
"""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import CelRuntime  # noqa: E402
from cdfc.evaluate.liveness import LivenessInputs, inputs_for  # noqa: E402
from cdfc.measure.p5_run import (  # noqa: E402
    FME,
    INDEPENDENT,
    TEMPLATE_COMPUTED,
    fme_harvest,
    promote,
)
from cdfc.predicates.host_fns import default_registry  # noqa: E402
from cdfc.qualify.campaign_store import CAMPAIGNS  # noqa: E402

CAMPAIGN_ID = "fme-v3-seed20260810"
ROW_INSERTED = REPO / "fixtures" / "synthetic" / "row-inserted__portfolio-r7.xlsx"
SEEDED = REPO / "fixtures" / "synthetic" / "formula-overwritten__portfolio-O7.xlsx"


@lru_cache(maxsize=1)
def killed_rows() -> tuple[dict[str, Any], ...]:
    path = REPO / CAMPAIGNS / CAMPAIGN_ID / "killed.jsonl"
    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )


@lru_cache(maxsize=1)
def killers() -> frozenset[str]:
    """Predicate ids the committed campaign records at least one kill for — G2's kill stage."""
    out: set[str] = set()
    for row in killed_rows():
        out.update(str(p) for p in (row.get("killed_by") or ()))
    return frozenset(out)


@lru_cache(maxsize=1)
def all_predicates() -> tuple[Any, ...]:
    return tuple(promote(c) for c in fme_harvest().candidates)


@lru_cache(maxsize=1)
def population() -> tuple[Any, ...]:
    ids = killers()
    return tuple(p for p in all_predicates() if p.id in ids)


@lru_cache(maxsize=1)
def runtime() -> CelRuntime:
    return CelRuntime(profile_version="P10", host_fns=default_registry())


@lru_cache(maxsize=8)
def liveness_inputs(filing: Path = INDEPENDENT, max_witnesses: int = 3) -> LivenessInputs:
    return inputs_for(
        filing,
        FME,
        predicates=list(population()),
        schema=fme_harvest().schema,
        rt=runtime(),
        passcase=TEMPLATE_COMPUTED,
        killed_rows=list(killed_rows()),
        max_witnesses=max_witnesses,
    )


@lru_cache(maxsize=1)
def image() -> Any:
    return liveness_inputs().image


@lru_cache(maxsize=1)
def witnesses() -> dict[str, tuple[Any, ...]]:
    return dict(liveness_inputs().witnesses)


def a_witness(pid: str | None = None) -> Any:
    """One witness, deterministically chosen. `pid` picks a predicate; otherwise the first."""
    ws = witnesses()
    key = pid if pid is not None else sorted(k for k, v in ws.items() if v)[0]
    return ws[key][0]
