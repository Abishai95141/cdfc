"""P5 — the reference run harness. One place that assembles a run, so tests and the measurement
tool cannot assemble it two different ways.

**The promotion of harvested candidates to `Predicate` happens HERE and is labelled.** No candidate
in this repository has been through the gates; promoting one to run it is a *fixture* operation,
and every number it produces is `PRE-GATE`. `qualification.campaign_id` is
`CAMPAIGN-PRE-GATE-FIXTURE` so `admission_state()` computes `PRE-GATE` from the data rather than
being told.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

from cdfc.evaluate.binding import TemplateCatalogue
from cdfc.evaluate.celrt import CelRuntime
from cdfc.evaluate.run import RunResult, execute
from cdfc.evaluate.selection import RunProfile
from cdfc.facts.build import fact_set_for
from cdfc.predicates.envelope import Candidate, Predicate, Qualification, QualifiedAgainst
from cdfc.predicates.harvest import HarvestResult, harvest
from cdfc.predicates.host_fns import default_registry
from cdfc.schema.styles_mask import Rule, build
from cdfc.verdict.settled_fraction import Denominator

REPO = Path(__file__).resolve().parents[3]
PRESCRIBED = REPO / "fixtures" / "prescribed"
SYNTHETIC = REPO / "fixtures" / "synthetic"
FME = PRESCRIBED / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"

INDEPENDENT = SYNTHETIC / "clean__independently-computed__fme-q1.xlsx"
TEMPLATE_COMPUTED = SYNTHETIC / "clean__template-computed__fme-q1.xlsx"
SEEDED = SYNTHETIC / "mutant__f11-formula-override__portfolio-O7.xlsx"

REGISTRY_ROOT = "root-p5-pre-gate-fixture"

# Carried on every surface that quotes a number from the independently-computed filing.
INDEPENDENT_LABEL = (
    "INDEPENDENTLY-COMPUTED (LibreOffice). Its derived cells were computed by an implementation "
    "this project did not write — NOT by a person, and NOT by Excel. It is the plan's E6 substitute "
    "and it is weaker than E6 in two named ways: LibreOffice is not Excel, so a disagreement is a "
    "third answer rather than a verdict against us; and it is a spreadsheet engine, not a reader "
    "of the regulation, so it cannot notice that a formula is wrong."
)

SMOKE_LABEL = (
    "SMOKE ONLY — NON-GATING — NON-DISCRIMINATING (arithmetic). src/cdfc/calc/ wrote this filing's "
    "derived cells, and the arithmetic predicates assert exactly the identities calc/ enforced when "
    "it did. The oracle and the system under test are the same function, so a zero here is x == x. "
    "It may not be cited in a gate, in a severity tier, or in any published rate."
)


def promote(c: Candidate) -> Predicate:
    """A harvested candidate, run as a fixture. Every number it produces is PRE-GATE."""
    return Predicate(
        **{f.name: getattr(c, f.name) for f in dataclasses.fields(c)},
        qualification=Qualification(
            campaign_id="CAMPAIGN-PRE-GATE-FIXTURE",
            kill_rate_claimed="0/0",
            kill_rate_all_classes="0/0",
            false_failure_rate="0/0",
            qualified_at="2026-08-12",
        ),
        qualified_against=QualifiedAgainst(
            evaluator_version="celpy-0.5.0", fault_model_version="v3",
            corpus_sha256="0" * 64, template_sha256=c.template,
        ),
        severity_tier="ADVISORY",
        state="ACTIVE",
        withdrawn_reason=None,
    )


@lru_cache(maxsize=4)
def fme_harvest() -> HarvestResult:
    return harvest(FME)


@lru_cache(maxsize=1)
def fme_surface() -> tuple[int, tuple[str, ...], str]:
    fs = build(FME, Rule.V3)
    return fs.n_cells, tuple(sorted(f"{s}!{r}" for s, r in fs.cells)), fs.validation_state


@lru_cache(maxsize=1)
def catalogue() -> TemplateCatalogue:
    return TemplateCatalogue.from_corpus(PRESCRIBED)


def denominator() -> Denominator:
    n, _cells, state = fme_surface()
    return Denominator(
        source="styles.xml unlocked mask, computed twice and agreed (P2)",
        generatorRule="v3",
        fieldSurface=n,
        computedTwiceAgreed=True,
        validationState=state,
    )


def run_filing(
    filing: Path,
    *,
    predicates: Sequence[Predicate] | None = None,
    profile: RunProfile | None = None,
    surface_cells: Sequence[str] | None = None,
    field_surface: int | None = None,
    schema: Any = None,
) -> RunResult:
    res = fme_harvest()
    n, cells, _state = fme_surface()
    return execute(
        filing,
        catalogue=catalogue(),
        predicates=list(predicates if predicates is not None else [promote(c) for c in res.candidates]),
        schema=schema if schema is not None else res.schema,
        field_surface=n if field_surface is None else field_surface,
        denominator=denominator(),
        registry_root=REGISTRY_ROOT,
        profile=profile or RunProfile(name="default", digest="p5"),
        facts=fact_set_for(filing, FME),
        surface_cells=list(surface_cells if surface_cells is not None else cells),
        rt=CelRuntime(profile_version="P5", host_fns=default_registry()),
    )


def failing_predicate_ids(result: RunResult) -> tuple[str, ...]:
    from cdfc.verdict import ItemState

    return tuple(sorted(c.predicate_id for c in result.checks if c.state is ItemState.FAIL))


def predicates_reading(cell: str) -> tuple[str, ...]:
    """Every harvested predicate whose bound cells include `cell`. Named, not counted."""
    from cdfc.predicates.ast_walker import bound_cells

    res = fme_harvest()
    return tuple(sorted(c.id for c in res.candidates if cell in bound_cells(c, res.schema)))
