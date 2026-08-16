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


def test_store__refuses_to_invent_a_reason_code(run_id: str) -> None:
    """**The breakdown is declared absent, never fabricated.**

    `run.jsonl` records only cells that were EVALUATED, so the no-predicate set is not in it. The
    first version of this store defaulted a null reason to `NO_PREDICATE` — a code that is not in
    the closed thirty-member vocabulary. An invented code on the wire is worse than no breakdown:
    a client renders it beside real ones and nobody downstream can tell them apart.
    """
    run = store.load(run_id, runs_dir=RUNS)
    with pytest.raises(store.BreakdownNotInArtifact):
        store.unchecked_groups(run)
    # The TOTAL is a real measurement and is still served.
    assert store.unchecked_total(run) > 0


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


def test_api__unchecked_declares_the_gap_rather_than_serving_an_empty_list(run_id: str) -> None:
    """`groups: null` — NOT `[]`, which reads as *every cell accounted for, none has a reason*."""
    body = dispatch(Request("GET", f"/v1/runs/{run_id}/unchecked")).json()
    assert body["total"] > 0
    assert body["groups"] is None
    assert "not invented" in body["breakdownUnavailable"]


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


def test_serve__every_response_carries_a_locked_down_csp() -> None:
    """The report has no script and no external reference; the header says so to the browser too.

    If a script ever reaches a rendered page, `default-src 'none'` makes the browser refuse it and
    the failure is loud rather than a silently-working feature nobody audited.
    """
    for path in ("/", "/v1/healthz", "/v1/nope"):
        _s, _b, headers = _wsgi("GET", path)
        csp = headers["Content-Security-Policy"]
        assert "default-src 'none'" in csp
        assert "script-src" not in csp, "a script-src directive would permit scripts"
        assert headers["X-Content-Type-Options"] == "nosniff"


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
