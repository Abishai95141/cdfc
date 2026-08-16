"""P14-B3 — the API's behaviour, and the one rule that lives only here: NO TOTAL ROW."""

from __future__ import annotations

import json

import pytest

from cdfc.api.app import MAX_UPLOAD_BYTES, OPERATOR_TOKEN_ENV, Request, dispatch
from cdfc.api.handlers import NO_MASK_TEMPLATES
from cdfc.api.routes import MUTATING, ROUTES

# Any key at any depth that would let a reader take one number as a summary of the portfolio.
AGGREGATE_KEYS = {"total", "totals", "average", "averages", "mean", "aggregate", "overall",
                  "combined", "summary_fraction", "portfolioFraction", "settledFraction"}


def _get(path: str, **kw) -> object:
    return dispatch(Request("GET", path, **kw))


def test_api__healthz_is_live() -> None:
    assert _get("/v1/healthz").status == 200


def test_api__unknown_route_is_404_not_500() -> None:
    assert _get("/v1/nope").status == 404


def test_api__non_zip_upload_is_415() -> None:
    r = dispatch(Request("POST", "/v1/filings", body=b"this is not a zip"))
    assert r.status == 415
    assert r.json()["error"] == "not_a_zip"


def test_api__oversized_upload_is_413() -> None:
    r = dispatch(Request("POST", "/v1/filings", body=b"PK" + b"0" * (MAX_UPLOAD_BYTES + 1)))
    assert r.status == 413


def test_api__422_carries_the_structural_fingerprint() -> None:
    """A 422 that only says 'unknown template' leaves an operator with nothing to act on."""
    r = dispatch(Request("POST", "/v1/filings", body=b"PK\x03\x04rest-of-a-zip"))
    assert r.status == 422
    body = r.json()
    assert body["error"] == "template_unbound"
    assert body["structuralFingerprint"], "the fingerprint is what an operator pastes to admit it"


def test_api__mutating_paths_require_a_token(monkeypatch) -> None:
    """TABLE-DRIVEN over `MUTATING`. A new mutating path added without a token fails here."""
    monkeypatch.setenv(OPERATOR_TOKEN_ENV, "s3cret")
    for route in MUTATING:
        path = route.path.replace("{id}", "r1").replace("{sha}", "abc")
        assert dispatch(Request(route.method, path)).status == 401, route.path
        ok = dispatch(Request(route.method, path, headers={"authorization": "Bearer s3cret"}))
        assert ok.status < 400, (route.path, ok.status)


def test_api__an_unset_token_refuses_rather_than_admits(monkeypatch) -> None:
    """**An absent secret is not an open door.** 503, never 200."""
    monkeypatch.delenv(OPERATOR_TOKEN_ENV, raising=False)
    for route in MUTATING:
        path = route.path.replace("{id}", "r1").replace("{sha}", "abc")
        r = dispatch(Request(route.method, path, headers={"authorization": "Bearer anything"}))
        assert r.status == 503, route.path


def test_api__read_paths_need_no_token(monkeypatch) -> None:
    """The predicate library is public and unauthenticated BY DESIGN."""
    monkeypatch.delenv(OPERATOR_TOKEN_ENV, raising=False)
    assert _get("/v1/predicates").status == 200
    assert _get("/v1/rejections").status == 200


def test_api__templates_ceiling_is_null_not_zero() -> None:
    """NC-D03b's API twin. `null` says *no mask*; `0` says *nothing can ever settle*."""
    rows = _get("/v1/templates").json()
    by_name = {r["name"]: r for r in rows}
    for name in NO_MASK_TEMPLATES:
        assert by_name[name]["settledFractionCeiling"] is None, name
    # And the JSON really carries `null`, distinguishable from 0 on the wire.
    raw = _get("/v1/templates").body.decode("utf-8")
    assert '"settledFractionCeiling":null' in raw


def test_api__portfolio_has_no_total_row() -> None:
    """**The rule the buyer decision made load-bearing**, asserted over the emitted JSON.

    *"Our clients average 87% settled"* is the most saleable sentence this product could emit and
    it divides one workbook's unlocked-cell mask by another workbook's. The denominators are
    different templates. So: rows, and no aggregate at any depth.
    """
    body = _get("/v1/portfolio").json()
    assert "rows" in body and "columns" in body

    def keys(node):
        if isinstance(node, dict):
            for k, v in node.items():
                yield k
                yield from keys(v)
        elif isinstance(node, list):
            for v in node:
                yield from keys(v)

    found = {k for k in keys(body) if k in AGGREGATE_KEYS}
    assert not found, (
        f"the portfolio emits {sorted(found)}. A fraction across templates divides one workbook's "
        "mask by another's; counts are aggregable and fractions are not."
    )


def test_api__the_report_is_served_from_disk_not_re_rendered(tmp_path, monkeypatch) -> None:
    """Byte-identical to disk. A re-render would be a second artifact the attestation misses."""
    import cdfc.api.handlers as h

    run = tmp_path / "run-1"
    run.mkdir()
    (run / "report.html").write_bytes(b"<!doctype html><title>x</title>")
    monkeypatch.setattr(h, "REPORTS", tmp_path)
    r = dispatch(Request("GET", "/v1/runs/run-1/report.html"))
    assert r.status == 200
    assert r.body == (run / "report.html").read_bytes()
    assert r.content_type.startswith("text/html")


def test_api__responses_are_byte_stable() -> None:
    """Same object, same bytes — a client diffing two responses diffs content, not dict order."""
    a = _get("/v1/templates").body
    b = _get("/v1/templates").body
    assert a == b


def test_api__every_route_has_a_handler() -> None:
    """A route naming a handler that does not exist is a build error, not a 404."""
    import cdfc.api.handlers as h

    missing = [r.path for r in ROUTES if not hasattr(h, r.handler)]
    assert not missing, missing


def test_api__the_admission_endpoint_stops_at_a_human_signature(monkeypatch) -> None:
    monkeypatch.setenv(OPERATOR_TOKEN_ENV, "s3cret")
    r = dispatch(Request("POST", "/v1/templates", headers={"authorization": "Bearer s3cret"}))
    assert r.json()["admitted"] is False
    assert r.json()["stoppedAt"] == "T7"


def test_api__overrides_retain_both_states(monkeypatch) -> None:
    """An override that replaced the machine's state would make the attestation a record of a
    decision rather than of a computation."""
    monkeypatch.setenv(OPERATOR_TOKEN_ENV, "s3cret")
    r = dispatch(Request("POST", "/v1/runs/r1/overrides",
                         headers={"authorization": "Bearer s3cret"}))
    body = r.json()
    assert body["machineState"] and body["operatorState"]
    assert body["bothRetained"] is True


def test_api__no_socket_in_the_import_closure() -> None:
    """`cdfc.api.app` must be importable without a socket. `serve.py` is where one lives.

    This is P13-B0's rule applied early to the package most likely to break it.
    """
    import ast
    from pathlib import Path

    banned = {"socket", "httpx", "requests", "http.client", "urllib.request"}
    for p in sorted(Path("src/cdfc/api").glob("*.py")):
        if p.name == "serve.py":
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {node.module or ""}
            else:
                continue
            hit = {n for n in names if n.split(".")[0] in {b.split(".")[0] for b in banned}}
            assert not hit, f"{p}: imports {hit}"


@pytest.mark.parametrize("path", [r.path for r in ROUTES if "{" not in r.path and r.method == "GET"])
def test_api__every_plain_get_returns_json_or_a_declared_error(path: str) -> None:
    r = _get(path)
    assert r.status in (200, 404, 501)
    if r.status == 200 and r.content_type == "application/json":
        json.loads(r.body)
