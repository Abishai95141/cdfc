"""P14-B3 completion — the store reads real runs, and the server actually serves.

Before this, the contract layer was real and tested while every handler returned an empty
collection. These tests are the difference between *"a `status` property cannot reach a client"*
and *"a client can get the run."*
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from cdfc.api import store
from cdfc.api.app import Request, dispatch
from cdfc.api.serve import application

RUNS = Path("reports/runs")

# A SKIPPED TEST IS A SILENT PASS, and `reports/*` is gitignored so a fresh clone has no run.
# The repo already has the idiom for this: `CDFC_REQUIRE_SWEEP=1` makes the sweep test FAIL rather
# than skip when its artifact is absent. `make verify` sets `CDFC_REQUIRE_RUN=1` after producing a
# run, so the skip can only happen on a developer's machine and never in the pipeline that decides
# whether the build is green.
_HAVE_RUN = bool(store.run_ids(runs_dir=RUNS))


def test_api_store__a_run_exists_when_the_pipeline_requires_one() -> None:
    """Fails loudly rather than skipping, when `CDFC_REQUIRE_RUN` says a run should be there."""
    import os

    if os.environ.get("CDFC_REQUIRE_RUN") and not _HAVE_RUN:
        raise AssertionError(
            "CDFC_REQUIRE_RUN=1 and reports/runs is empty. Every test in this module would have "
            "SKIPPED, and a green suite would have reported that the API serves real data without "
            "once asking it to."
        )


pytestmark = pytest.mark.skipif(
    not _HAVE_RUN, reason="no run on disk; `cdfc run <filing> --out reports/runs`"
)


@pytest.fixture(scope="module")
def run_id() -> str:
    return store.run_ids(runs_dir=RUNS)[0]


def _wsgi(method: str, path: str, body: bytes = b"", query: str = "") -> tuple[str, bytes, dict]:
    env = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
           "wsgi.input": io.BytesIO(body), "CONTENT_LENGTH": str(len(body))}
    cap: dict = {}

    def start(status: str, headers: list) -> None:
        cap["status"], cap["headers"] = status, dict(headers)

    out = b"".join(application(env, start))
    return cap["status"], out, cap["headers"]


# --- the store ---------------------------------------------------------------------------


def test_store__reads_the_manifest_as_the_header(run_id: str) -> None:
    """`manifest.json` is the header; `run.jsonl` is the evaluation stream. Not the reverse."""
    run = store.load(run_id, runs_dir=RUNS)
    assert run.header()["run_id"] == run_id
    assert run.closure()["cellsTotal"] > 0
    assert run.records, "the stream is empty"


def test_store__the_fraction_is_read_not_recomputed(run_id: str) -> None:
    """Two implementations of the settled fraction is one more than this project can defend."""
    run = store.load(run_id, runs_dir=RUNS)
    f, c = store.fraction_of(run), run.closure()
    assert f["settled"] == c["settled"]
    assert f["notChecked"] == c["noPredicate"]
    assert f["inScope"] == c["inScope"]


def test_store__serves_the_breakdown_the_RUN_measured(run_id: str) -> None:
    """**The gap is closed at the source, not by the API learning to derive one.**

    This used to assert `pytest.raises(BreakdownNotInArtifact)`, and the refusal was right: the
    per-reason breakdown genuinely was not in the artifact, because `run.jsonl` is one line per
    EVALUATION and a cell nothing evaluated leaves no trace in it.

    The run now COUNTS the breakdown at write time and puts it in the manifest beside the closure,
    so this reads a measurement rather than reconstructing one. The refusal path is still tested,
    below, against an artifact that lacks the field.
    """
    run = store.load(run_id, runs_dir=RUNS)
    groups = store.unchecked_groups(run)
    assert groups, "the breakdown is empty; the run did not measure it"
    assert sum(g["count"] for g in groups) == store.unchecked_total(run)
    from cdfc.verdict import ReasonCode

    known = {str(getattr(r, "value", r)) for r in ReasonCode}
    for g in groups:
        assert g["reasonCode"] in known, f"{g['reasonCode']!r} is not one of the thirty"


def test_store__still_refuses_to_invent_a_reason_code(run_id: str) -> None:
    """**THE CONTROL, kept.** An artifact without the field gets a refusal, not a reconstruction.

    The first version of this store defaulted a null reason to `NO_PREDICATE` — a code that is not
    in the closed thirty-member vocabulary. An invented code on the wire is worse than no
    breakdown: a client renders it beside real ones and nobody downstream can tell them apart. A
    run written before `uncheckedByReason` existed must still get the refusal.
    """
    import dataclasses

    run = store.load(run_id, runs_dir=RUNS)
    older = dataclasses.replace(
        run, manifest={k: v for k, v in run.manifest.items() if k != "uncheckedByReason"}
    )
    with pytest.raises(store.BreakdownNotInArtifact):
        store.unchecked_groups(older)
    # The TOTAL is a real measurement and is still served.
    assert store.unchecked_total(older) > 0


def test_store__an_absent_run_raises_rather_than_returning_empty() -> None:
    with pytest.raises(store.RunNotFound):
        store.load("no-such-run", runs_dir=RUNS)


def test_store__is_read_only() -> None:
    """No code path here opens a file for writing. An API that could write a run could change
    what a signed statement covers."""
    src = Path("src/cdfc/api/store.py").read_text(encoding="utf-8")
    for forbidden in ("open(", ".write_text(", ".write_bytes(", ".unlink(", ".mkdir("):
        assert forbidden not in src, f"store.py contains {forbidden!r}"


# --- the handlers, on real data -----------------------------------------------------------


def test_api__run_endpoint_returns_all_six_counts(run_id: str) -> None:
    body = dispatch(Request("GET", f"/v1/runs/{run_id}")).json()
    frac = body["settledFraction"]
    for k in ("settled", "notChecked", "unsettled", "inScope", "outOfScope", "informational"):
        assert k in frac, k
    assert frac["fraction"] is not None
    # NC-A05 on the wire: no settled count without its admission state and denominator warning.
    assert frac["admissionState"] and frac["denominatorWarning"]


def test_api__unchecked_serves_the_breakdown_with_a_distinct_remedy_per_group(
    run_id: str,
) -> None:
    """The panel that is the product. **`groups: null` was the honest answer and is no longer the
    true one** — the run measures the breakdown now, so the endpoint serves it.

    `groups: []` would still be forbidden and is not reachable: an empty list reads as *every
    unchecked cell is accounted for and none has a reason*, and the summing assertion below would
    fail before anybody could ship it.
    """
    body = dispatch(Request("GET", f"/v1/runs/{run_id}/unchecked")).json()
    assert body["total"] > 0
    assert body["groups"], "an empty list reads as 'no cell has a reason', which is false"
    assert body["breakdownUnavailable"] is None
    assert sum(g["count"] for g in body["groups"]) == body["total"]
    # NO FALLBACK REMEDY. A generic one makes a panel of reasons into one sentence repeated, and
    # it looks exactly like a panel that thought about each group.
    assert len({g["remedy"] for g in body["groups"]}) == len(body["groups"])


def test_api__cells_declares_its_cap(run_id: str) -> None:
    """A truncated list that looks complete is how a coverage number gets read off a short screen."""
    body = dispatch(Request("GET", f"/v1/runs/{run_id}/cells")).json()
    assert body["returned"] <= body["total"]
    assert len(body["cells"]) == body["returned"]


def test_api__checks_are_per_predicate_not_per_cell(run_id: str) -> None:
    rows = dispatch(Request("GET", f"/v1/runs/{run_id}/checks")).json()
    assert rows and len({r["predicateId"] for r in rows}) == len(rows)


def test_api__portfolio_lists_real_runs_and_still_has_no_total(run_id: str) -> None:
    body = dispatch(Request("GET", "/v1/portfolio")).json()
    assert any(r["runId"] == run_id for r in body["rows"])
    assert "total" not in body and "average" not in json.dumps(body)


# --- the server --------------------------------------------------------------------------


def test_serve__root_is_the_drop_screen() -> None:
    status, body, headers = _wsgi("GET", "/")
    assert status.startswith("200")
    assert b"Check a filing" in body
    assert headers["Content-Type"].startswith("text/html")


def test_serve__api_paths_dispatch(run_id: str) -> None:
    status, body, _ = _wsgi("GET", f"/v1/runs/{run_id}")
    assert status.startswith("200")
    assert json.loads(body)["runId"] == run_id


def test_serve__every_artifact_response_carries_a_locked_down_csp() -> None:
    """**Narrowed from every response to every `/v1` response, and it is a strengthening.**

    This test used to walk `/`, `/v1/healthz` and `/v1/nope` and assert no `script-src` on any of
    them. `/` is now an app screen and carries `script-src 'self'`, because the twelve screens are
    an interactive product and a product without scripts is a document.

    The guarantee did not weaken. It was GLOBAL and vacuous — a header applied to every response
    says nothing about what is in any of them — and it is now asserted where it is claimed:
    `tests/surface/test_web_screens.py::test_web__the_report_route_forbids_script_in_the_header_
    AND_in_the_bytes` checks the policy on `report.html` AND greps the served bytes for `<script`,
    which the blanket header never did.

    What must never acquire the looser policy is anything under `/v1`, and the split is by path
    prefix so a new API route cannot get it by being added to the wrong table.
    """
    for path in ("/v1/healthz", "/v1/nope", "/v1/portfolio"):
        _s, _b, headers = _wsgi("GET", path)
        csp = headers["Content-Security-Policy"]
        assert "default-src 'none'" in csp
        assert "script-src" not in csp, "a script-src directive would permit scripts"
        assert headers["X-Content-Type-Options"] == "nosniff"


def test_serve__the_app_screens_permit_only_a_same_origin_script() -> None:
    """And nothing looser: no `unsafe-inline`, no `unsafe-eval`, no host in any directive."""
    _s, _b, headers = _wsgi("GET", "/")
    csp = headers["Content-Security-Policy"]
    assert "default-src 'none'; script-src 'self'" in csp
    assert "unsafe-eval" not in csp
    assert "http" not in csp, "a host in a CSP directive means a CDN can be added"


def test_serve__status_line_matches_the_dispatcher() -> None:
    status, _b, _h = _wsgi("GET", "/v1/nope")
    assert status == "404 Not Found"


def test_serve__is_the_only_module_that_may_open_a_socket() -> None:
    """The split the whole `cdfc.api` package exists for, asserted rather than described."""
    import ast

    for p in sorted(Path("src/cdfc/api").glob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))
        names = {
            a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names
        } | {
            n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
        }
        hits = {n for n in names if n.split(".")[0] in {"socket", "wsgiref", "http", "httpx"}}
        if p.name == "serve.py":
            continue
        assert not hits, f"{p.name} imports {hits}; only serve.py may"
