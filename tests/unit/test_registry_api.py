"""The registry-backed endpoints. **The three screens nothing else in this category has.**

Before this, `/v1/predicates`, `/v1/rejections`, `/v1/registry/roots` and the history all returned
`[]`. An empty list is not a neutral placeholder here — it is a claim, and it is the WRONG one:

* `200 []` from `/v1/predicates` says *the five gates ran and admitted nobody*. That is true today
  and is the most interesting single fact this product knows about itself.
* An absent artifact says *nobody ran the gates*.

The two are indistinguishable to a reader and mean opposite things, which is why every test below
that touches an absence checks the REFUSAL rather than the emptiness.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cdfc.api import registry_store
from cdfc.api.app import Request, dispatch
from cdfc.qualify import artifact

ART = artifact.ARTIFACT_PATH
_HAVE = ART.is_file()


def test_registry__the_artifact_exists_when_the_pipeline_requires_one() -> None:
    import os

    if os.environ.get("CDFC_REQUIRE_RUN") and not _HAVE:
        raise AssertionError(
            f"CDFC_REQUIRE_RUN=1 and {ART} is absent. Every test below would have SKIPPED and a "
            "green suite would have reported that three screens serve real data without asking "
            "any of them. `make attrition` produces it."
        )


pytestmark = pytest.mark.skipif(not _HAVE, reason="run `make attrition`")


@pytest.fixture(scope="module")
def art():
    return registry_store.load()


def _get(path: str, **query):
    return dispatch(Request("GET", path, query={k: str(v) for k, v in query.items()}))


# --- the artifact ----------------------------------------------------------------------------


def test_artifact__an_absent_artifact_raises_rather_than_returning_an_empty_library() -> None:
    with pytest.raises(artifact.ArtifactNotOnDisk):
        artifact.load(Path("reports/qualification/no-such-file.json"))


def test_artifact__a_foreign_schema_version_is_not_coerced() -> None:
    with pytest.raises(artifact.ArtifactSchemaMismatch):
        artifact.from_wire({"schemaVersion": 999})


def test_artifact__a_stage_that_did_not_run_carries_no_dispositions() -> None:
    """`NOT RUN` is a fourth state. A gate that never executed made no determination about
    anybody, and rendering it as one that skipped everyone claims one it never made."""
    with pytest.raises(ValueError, match="made no determination"):
        artifact.Stage(name="G4", entered=10, skipped=10, survived=0, rejected=0, ran=False)


def test_artifact__stage_arithmetic_is_enforced_by_the_surface_object() -> None:
    """The invariant lives in ONE place — `surface.funnel.FunnelStage` — and `Stage` asserts by
    constructing it, rather than re-implementing `entered == skipped + survived + rejected`."""
    from cdfc.surface.funnel import StageArithmeticDoesNotClose

    with pytest.raises(StageArithmeticDoesNotClose):
        artifact.Stage(name="G0", entered=10, skipped=3, survived=8, rejected=0, ran=True)


def test_artifact__the_funnel_is_in_gate_order(art) -> None:
    names = [s.name for s in art.stages]
    assert names == ["generated", "G0", "G1", "G3p", "G2", "G3e", "G4"]


def test_artifact__a_not_run_stage_renders_distinctly_from_a_skipped_one() -> None:
    not_run = artifact.Stage("G4", entered=5, skipped=0, survived=0, rejected=0, ran=False)
    skipped = artifact.Stage("G4", entered=5, skipped=5, survived=0, rejected=0, ran=True)
    assert not_run.render() != skipped.render()
    assert "NOT RUN" in not_run.render()
    assert "NOT APPLICABLE" in skipped.render()


# --- the library, and its honest emptiness ---------------------------------------------------


def test_library__is_empty_and_says_why_rather_than_rendering_a_blank(art) -> None:
    body = _get("/v1/predicates").json()
    assert body["rows"] == []
    assert body["admittedCount"] == 0
    # THE SENTENCE THAT STOPS THE EMPTINESS BEING MISREAD. A library reading `0 admitted` beside a
    # report reading `1,898 settled` invites exactly one inference, and it is false.
    assert body["predicatesThatProducedRuns"] > 0
    assert body["populationsAreDisjoint"] is True
    assert "different populations" in body["disjointNote"]


def test_library__carries_the_corpus_outcome_and_the_instrument_label(art) -> None:
    body = _get("/v1/predicates").json()
    assert body["corpus"]["outcome"] in ("PASS", "RESTRICTED", "FAIL")
    # A restricted pass rendered as a pass is the whole failure G-CORPUS exists to prevent.
    assert body["corpus"]["census"]["n"] >= 0
    assert "instrumentLabel" in body


def test_library__the_batch_is_visibly_unsigned(art) -> None:
    rows = _get("/v1/registry/roots").json()
    assert rows and rows[0]["signer"] == "UNSIGNED"
    assert rows[0]["badge"] == "UNSIGNED BATCH"


# --- the rejections, the flagship screen -----------------------------------------------------


def test_rejections__every_row_carries_the_number_that_decided_it(art) -> None:
    """**A rejection without its number is an opinion with a gate's name on it.**"""
    body = _get("/v1/rejections", limit=100).json()
    assert body["total"] > 0
    for row in body["rows"]:
        assert row["headline"].strip(), row["candidateId"]
        assert row["measured"], row["candidateId"]
        assert row["gate"] and row["reason"]


def test_rejections__the_cap_is_visible(art) -> None:
    body = _get("/v1/rejections", limit=5).json()
    assert body["returned"] == 5 < body["total"]
    assert len(body["rows"]) == body["returned"]


def test_rejections__offset_pages_without_repeating(art) -> None:
    a = _get("/v1/rejections", limit=5, offset=0).json()["rows"]
    b = _get("/v1/rejections", limit=5, offset=5).json()["rows"]
    assert {r["candidateId"] for r in a}.isdisjoint({r["candidateId"] for r in b})


def test_rejections__filters_are_exact_and_facets_carry_their_denominators(art) -> None:
    facets = _get("/v1/rejections", limit=1).json()["facets"]
    gate = next(iter(facets["gate"]))
    body = _get("/v1/rejections", gate=gate, limit=1).json()
    assert body["total"] == facets["gate"][gate]
    assert body["totalUnfiltered"] >= body["total"]


def test_rejections__an_unknown_filter_returns_zero_rows_not_all_of_them(art) -> None:
    """A filter that silently matches everything is worse than one that matches nothing: the
    reader believes they narrowed the list and read a number off the wrong population."""
    body = _get("/v1/rejections", gate="G-NOPE").json()
    assert body["total"] == 0 and body["rows"] == []
    assert body["totalUnfiltered"] > 0


def test_rejections__cells_would_have_covered_is_present_on_every_row(art) -> None:
    """It is what turns a rejection into `no_predicate.failed_qualification` and into the report's
    `counterEvidence[]`. Discarding it throws away what an audit standard makes mandatory."""
    for row in _get("/v1/rejections", limit=100).json()["rows"]:
        assert isinstance(row["cellsWouldHaveCovered"], int)


# --- the funnel ------------------------------------------------------------------------------


def test_funnel__three_integers_per_stage_and_the_fourth_state(art) -> None:
    body = _get("/v1/funnel").json()
    stages = body["stages"]
    assert stages
    for s in stages:
        if s["ran"]:
            assert s["entered"] == s["skipped"] + s["survived"] + s["rejected"], s["name"]
        else:
            assert s["skipped"] == s["survived"] == s["rejected"] == 0, s["name"]
            assert "NOT RUN" in s["render"]


def test_funnel__both_obligation_counts_travel_together(art) -> None:
    """A STATUTE count alone reads as *nothing is covered*; a TEMPLATE count alone as *everything
    is*. Both are wrong and each is wrong by the other's value."""
    pair = _get("/v1/funnel").json()["obligationCoverage"]
    assert (pair["withStatuteObligation"] is None) == (pair["withTemplateObligation"] is None)
    assert pair["total"] > 0 and pair["note"]


def test_funnel__publishing_a_zero_is_the_honest_case(art) -> None:
    pair = _get("/v1/funnel").json()["obligationCoverage"]
    if pair["withStatuteObligation"] == 0:
        assert "no harvested predicate yet implements a statutory clause" in pair["note"]


# --- the history, and the churn behind it ----------------------------------------------------


def test_history__the_series_steps_down_and_the_step_carries_its_cause() -> None:
    rows = _get("/v1/settled-fraction/history").json()
    assert len(rows) >= 2
    downs = [r for r in rows if r["steppedDown"]]
    assert downs, "the series never falls; criterion A8 is undemonstrated"
    for r in downs:
        assert (r["cause"] or "").strip()
        assert r["delta"] < 0


def test_history__nothing_sorts_smooths_clamps_or_takes_a_running_maximum(tmp_path) -> None:
    """Read in FILE order, which is EVENT order.

    Asserted on a series that RECOVERS — down, then back up — because the real one has two points
    and is coincidentally sorted descending, so it cannot tell *fell* from *sorted by value*. The
    first version of this test made exactly that mistake and asserted a tautology.

    `1000 → 800 → 900` distinguishes all four failure modes at once: a sort gives `1000, 900, 800`,
    a running maximum gives `1000, 1000, 1000`, a clamp at the first value gives the same, and any
    smoothing moves the middle point off 800.
    """
    p = tmp_path / "settled-history.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in [
        {"at": "2026-01-01", "settled": 1000, "fieldSurface": 3747, "admission": "PRE-GATE",
         "cause": None},
        {"at": "2026-02-01", "settled": 800, "fieldSurface": 3747, "admission": "PRE-GATE",
         "cause": "template bump moved 12 predicates to PROVISIONAL"},
        {"at": "2026-03-01", "settled": 900, "fieldSurface": 3747, "admission": "PRE-GATE",
         "cause": None},
    ]), encoding="utf-8")

    got = registry_store.history(p)
    assert [r["settled"] for r in got] == [1000, 800, 900]
    assert [r["steppedDown"] for r in got] == [False, True, False]
    assert [r["delta"] for r in got] == [None, -200, 100]


def test_history__an_unexplained_step_down_is_refused_rather_than_dropped(tmp_path) -> None:
    """**The step-downs are the most credible points on this chart.** Serving the others while
    dropping the unexplained one would hide exactly the point the chart exists for."""
    from cdfc.surface.history import UnlabelledStepDown

    p = tmp_path / "settled-history.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in [
        {"at": "2026-01-01", "settled": 1000, "fieldSurface": 3747, "admission": "PRE-GATE",
         "cause": None},
        {"at": "2026-02-01", "settled": 800, "fieldSurface": 3747, "admission": "PRE-GATE",
         "cause": None},
    ]), encoding="utf-8")
    with pytest.raises(UnlabelledStepDown):
        registry_store.history(p)


def test_history__an_absent_series_refuses_rather_than_serving_an_empty_chart() -> None:
    with pytest.raises(registry_store.HistoryNotMeasured):
        registry_store.history(Path("reports/no-such-history.jsonl"))


def test_churn__still_running_is_what_proves_detection_was_kept() -> None:
    body = _get("/v1/churn").json()
    assert set(body["stillRunning"]) == set(body["movedToProvisional"])
    assert set(body["numbersHidden"]) == set(body["movedToProvisional"])
    assert body["numeratorDelta"] < 0
    assert set(body["movedReason"]) == set(body["movedToProvisional"])


def test_churn__an_unswept_bump_refuses_rather_than_reporting_nothing_moved() -> None:
    with pytest.raises(registry_store.ChurnNotSwept):
        registry_store.churn(Path("reports/churn/no-such-sweep.json"))


# --- the two prohibitions still hold over the new payloads -----------------------------------


def test_new_endpoints__no_bare_rate_reaches_the_wire(art) -> None:
    """R2 over the ACTUAL bytes of every new endpoint, not over a docstring.

    A float between 0 and 1 with no integers beside it is a rate whose arithmetic a reader cannot
    reconstruct. The kill rates travel as the literal string `K/O`, which is why they pass.
    """
    import re

    for path in ("/v1/predicates", "/v1/funnel", "/v1/registry/roots",
                 "/v1/settled-fraction/history", "/v1/churn"):
        body = _get(path).body.decode("utf-8")
        assert not re.search(r"\d+\.\d+\s*%", body), path


def test_new_endpoints__no_cross_template_aggregate(art) -> None:
    """R4. Counts aggregate; fractions do not."""
    for path in ("/v1/predicates", "/v1/funnel", "/v1/rejections"):
        body = json.loads(_get(path).body)
        assert "average" not in json.dumps(body).lower()
