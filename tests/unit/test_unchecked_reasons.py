"""The 319 predicates that never ran, and the reason code that said they did not exist.

## What was measured, and what it turned out to be

The reference run loads 348 harvested predicates and only 29 distinct ids appear in `run.jsonl`.
`1. Introduction!D3` is in the field-surface mask, `P-0002` binds exactly that cell, and the fact
tree carries `dv_d3 = "2025-26"` — yet the cell sat in the 1,849 counted under
`no_predicate.not_yet_synthesised`, which says **nobody has written a check for this cell**.

The drop is in `measure/p10_run.population()`, which restricts the run to `kill_stage_ids()` — the
predicates that killed at least one mutant in the pinned campaign. **That restriction is correct.**
It is exactly the set G2 admits at the kill stage; the other 315 are the ones G2 refused as
`g2.no_kill`, and running only predicates that have demonstrated they can catch something is the
rule this product is built on. It is also what lets the liveness loop replay a stored kill case for
every predicate in the run.

**So the answer is (b): they are correctly excluded, and the reason code was wrong.** The
vocabulary has carried the right one since P4 — `no_predicate.failed_qualification` — and
`qualify/pipeline.py` records `cells_would_have_covered` on every rejection expressly so the count
can be attributed to it.

## Two places had to change, and the second is the one that made the first a no-op

1. `rollup.materialise` took no per-cell reason at all.
2. `rollup.roll_up_run` then **overwrote** whatever `materialise` had set, because `roll_up(())`
   returns the hard-coded default for an empty evaluation set. Supplying a reason had no effect
   until that was scoped to *only when no predicate evaluated the cell*.

## The measurement, and the constraint it had to respect

`settled` is **1,898 before and after**. Nothing runs that did not run before; no state changes;
only the reason on cells that were already `NO_PREDICATE`. The 1,849 now splits **422 / 1,427**,
and the first number is the one a reader wants: *a check exists for these cells and the kill gate
refused it.*
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cdfc.evaluate.rollup import materialise, roll_up_run
from cdfc.verdict import ItemState, ReasonCode

RUNS = Path("reports/runs")
_RUN = next((d for d in sorted(RUNS.iterdir()) if (d / "manifest.json").is_file()), None) \
    if RUNS.is_dir() else None


def test_reasons__the_run_exists_when_the_pipeline_requires_one() -> None:
    import os

    if os.environ.get("CDFC_REQUIRE_RUN") and _RUN is None:
        raise AssertionError("CDFC_REQUIRE_RUN=1 and reports/runs is empty")


# --- the mechanism, in isolation ----------------------------------------------------------


def test_reasons__materialise_takes_a_per_cell_reason() -> None:
    table = materialise(
        ["S!A1", "S!A2"], reasons={"S!A1": ReasonCode.NP_FAILED_QUALIFICATION},
    )
    assert table["S!A1"].reason is ReasonCode.NP_FAILED_QUALIFICATION
    assert table["S!A2"].reason is ReasonCode.NP_NOT_YET_SYNTHESISED
    # The STATE is identical either way. This changes attribution, not the closure.
    assert {c.state for c in table.values()} == {ItemState.NO_PREDICATE}


def test_reasons__the_rollup_no_longer_discards_the_materialised_reason() -> None:
    """**This is the change that made supplying a reason do anything at all.**

    `roll_up(())` returns the hard-coded `not_yet_synthesised`, and `roll_up_run` wrote it over the
    materialised value — so the first version of this repair was a silent no-op, which is the
    defect shape it was written to fix, occurring inside the fix.
    """
    table = materialise(["S!A1"], reasons={"S!A1": ReasonCode.NP_FAILED_QUALIFICATION})
    rolled = roll_up_run(table, [])
    assert rolled[0].reason is ReasonCode.NP_FAILED_QUALIFICATION
    assert rolled[0].state is ItemState.NO_PREDICATE


def test_reasons__an_evaluated_cell_keeps_the_rolled_up_reason_not_the_default() -> None:
    """The override is scoped to cells NOTHING evaluated. A cell a predicate decided must carry
    the decision, never the materialised placeholder."""
    class _Chk:
        predicate_id, version, state = "P-0001", 1, ItemState.PASS
        reason, settles, witness, scope_kind = None, True, (), None
        cells_bound = ("S!A1",)

    table = materialise(["S!A1"], reasons={"S!A1": ReasonCode.NP_FAILED_QUALIFICATION})
    rolled = roll_up_run(table, [_Chk()])
    assert rolled[0].state is ItemState.PASS
    assert rolled[0].reason is None
    assert rolled[0].settled_by == "P-0001"


# --- the population, and why the restriction is right --------------------------------------


def test_reasons__the_run_population_is_the_kill_stage_and_nothing_else() -> None:
    """The 315 excluded predicates are exactly those the campaign records no kill for — which is
    the set G2 refused. The restriction is not arbitrary and it is not a bug."""
    from cdfc.measure.p10_run import all_predicates, kill_stage_ids, population

    every, running = all_predicates(), population()
    assert len(running) < len(every)
    assert {p.id for p in running} == {p.id for p in every} & kill_stage_ids()


def test_reasons__every_excluded_predicate_was_refused_at_G2() -> None:
    """Cross-checked against the qualification artifact rather than assumed.

    If an excluded predicate were NOT among the refusals, the exclusion would be unexplained and
    `failed_qualification` would be the wrong code for its cells.
    """
    from cdfc.qualify import artifact

    if not artifact.ARTIFACT_PATH.is_file():
        pytest.skip("run `make attrition`")
    art = artifact.load()
    refused = {r.candidate_id for r in art.rejections}
    from cdfc.measure.p10_run import all_predicates, population

    excluded = {p.id for p in all_predicates()} - {p.id for p in population()}
    assert excluded, "nothing is excluded, so this test asserts nothing"
    assert excluded <= refused, f"{sorted(excluded - refused)[:5]} were excluded but not refused"


def test_reasons__the_named_cell_is_attributed_to_the_refusal() -> None:
    """`1. Introduction!D3` — the cell the investigation started from."""
    from cdfc.measure.p10_run import fme_harvest, fme_surface, population, unchecked_reasons

    res = fme_harvest()
    _n, cells, _s = fme_surface()
    mapping = unchecked_reasons(population(), res.schema, list(cells))
    assert mapping.get("1. Introduction!D3") is ReasonCode.NP_FAILED_QUALIFICATION


# --- the run on disk -----------------------------------------------------------------------


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_reasons__the_settled_fraction_is_unchanged() -> None:
    """**THE CONSTRAINT.** A reason-code repair that moved the coverage number would be a repair
    that changed what the product claims, and no measurement here justifies that."""
    m = json.loads((_RUN / "manifest.json").read_text(encoding="utf-8"))
    c = m["closure"]
    assert c["settled"] == 1898
    assert c["noPredicate"] == 1849
    assert c["cellsTotal"] == c["inScope"] == 3747
    assert c["notRun"] == c["indeterminate"] == c["error"] == 0


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_reasons__the_manifest_carries_a_breakdown_that_sums_to_its_total() -> None:
    """A breakdown that does not sum to its own total is worse than none: it looks complete."""
    m = json.loads((_RUN / "manifest.json").read_text(encoding="utf-8"))
    breakdown = m["uncheckedByReason"]
    c = m["closure"]
    unchecked = c["noPredicate"] + c["indeterminate"] + c["notRun"] + c["error"]
    assert sum(breakdown.values()) == unchecked == 1849


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_reasons__the_split_is_422_and_1427_and_neither_is_zero() -> None:
    """Both halves must be non-empty or the split is decoration.

    A zero on the left would mean no refused candidate covers any surface cell — which would make
    the whole repair unobservable, and a test that passed either way.
    """
    m = json.loads((_RUN / "manifest.json").read_text(encoding="utf-8"))
    b = m["uncheckedByReason"]
    assert b["no_predicate.failed_qualification"] == 422
    assert b["no_predicate.not_yet_synthesised"] == 1427


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_reasons__every_code_in_the_breakdown_is_in_the_closed_vocabulary() -> None:
    """An invented code beside real ones is indistinguishable from a real one."""
    m = json.loads((_RUN / "manifest.json").read_text(encoding="utf-8"))
    known = {str(getattr(r, "value", r)) for r in ReasonCode}
    for code in m["uncheckedByReason"]:
        assert code in known, f"{code!r} is not one of the {len(known)} reason codes"


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_reasons__the_unchecked_panel_now_serves_the_breakdown() -> None:
    """It used to raise `BreakdownNotInArtifact` and serve `groups: null`. The gap is closed
    because the run MEASURES the breakdown, not because the API learned to derive one."""
    from cdfc.api.app import Request, dispatch

    body = dispatch(Request("GET", f"/v1/runs/{_RUN.name}/unchecked")).json()
    assert body["breakdownUnavailable"] is None
    assert body["groups"] is not None
    assert sum(g["count"] for g in body["groups"]) == body["total"] == 1849
    # NO FALLBACK REMEDY. Each group carries its own, and they differ.
    remedies = {g["remedy"] for g in body["groups"]}
    assert len(remedies) == len(body["groups"])
    for g in body["groups"]:
        assert g["remedy"].strip()
