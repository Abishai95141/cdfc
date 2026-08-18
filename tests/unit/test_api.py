"""P14-B3 — the API's behaviour, and the one rule that lives only here: NO TOTAL ROW."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from cdfc.api.app import MAX_UPLOAD_BYTES, OPERATOR_TOKEN_ENV, Request, dispatch
from cdfc.api.handlers import NO_MASK_TEMPLATE_SHA256
from cdfc.api.routes import MUTATING, ROUTES
from cdfc.schema.fingerprint import structural_fingerprint

SYNTHETIC = Path("fixtures/synthetic")
# Binds: a filing prepared on the pinned FME blank. Structure is unchanged by writing values in.
BINDS = SYNTHETIC / "clean__independently-computed__fme-q1.xlsx"
# Does not bind: a row inserted moves the dimension and the unlocked mask, which are two of the
# four structural facets `binding` compares.
DOES_NOT_BIND = SYNTHETIC / "row-inserted__portfolio-r7.xlsx"

SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

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


def test_api__422_carries_the_fingerprint_the_upload_actually_computes_to() -> None:
    """**THIS TEST USED TO PIN THE BUG.**

    It posted fourteen bytes of nonsense, asserted `422`, and then asserted only that
    `structuralFingerprint` was TRUTHY -- which the constant `"sheet-shape:unknown"` satisfies. So
    the handler returned that literal for every file on earth, including the FME filing the CLI
    binds without difficulty, and this test agreed with it. A truthiness assertion over a value
    that is supposed to be computed cannot tell a computation from a constant.

    It now posts a real workbook and asserts the digest equals what `structural_fingerprint`
    computes from the same bytes.
    """
    r = dispatch(Request("POST", "/v1/filings", body=DOES_NOT_BIND.read_bytes()))
    assert r.status == 422
    body = r.json()
    assert body["error"] == "template_unbound"
    fp = body["structuralFingerprint"]
    assert fp != "sheet-shape:unknown", "the placeholder is back"
    assert SHA256_HEX.match(fp), fp
    assert fp == structural_fingerprint(DOES_NOT_BIND)
    # And the refusal says what it was NEAREST to, on how many of the four structural facets.
    assert "Nearest is" in body["detail"]


def test_api__a_filing_that_binds_is_501_not_a_fabricated_run() -> None:
    """No queue, no worker, no run store: a 200 here would name a run id for a run nobody made."""
    r = dispatch(Request("POST", "/v1/filings", body=BINDS.read_bytes()))
    assert r.status == 501, r.json()
    body = r.json()
    assert body["error"] == "run_not_available_over_http"
    assert body["structuralFingerprint"] == structural_fingerprint(BINDS)
    assert SHA256_HEX.match(body["templateSha256"])
    assert "cdfc run" in body["detail"], "a refusal names where the check IS available"


def test_api__two_different_workbooks_do_not_share_a_fingerprint() -> None:
    """The value varies with the upload. A constant passes every single-file assertion above."""
    a = dispatch(Request("POST", "/v1/filings", body=BINDS.read_bytes())).json()
    b = dispatch(Request("POST", "/v1/filings", body=DOES_NOT_BIND.read_bytes())).json()
    assert a["structuralFingerprint"] != b["structuralFingerprint"]


def test_api__a_pk_prefixed_body_that_is_not_a_workbook_is_named_not_a_traceback() -> None:
    """415 with the exception type, never a 500: the filer's file broke, not this server."""
    r = dispatch(Request("POST", "/v1/filings", body=b"PK\x03\x04rest-of-a-zip"))
    assert r.status == 415
    assert r.json()["error"] == "unreadable_xlsx"
    assert "BadZipFile" in r.json()["detail"]


def test_api__mutating_paths_require_a_token(monkeypatch) -> None:
    """TABLE-DRIVEN over `MUTATING`. A new mutating path added without a token fails here."""
    monkeypatch.setenv(OPERATOR_TOKEN_ENV, "s3cret")
    for route in MUTATING:
        path = route.path.replace("{id}", "r1").replace("{sha}", "abc")
        assert dispatch(Request(route.method, path)).status == 401, route.path
        ok = dispatch(Request(route.method, path, headers={"authorization": "Bearer s3cret"}))
        # NOT `< 400`. `POST /v1/templates` is now a 501 -- template admission is not implemented
        # -- and a status assertion that demanded a success would force the endpoint back into
        # claiming it did something. What this test is about is the TOKEN, so it asserts that the
        # token was accepted: neither 401 (rejected) nor 503 (never configured).
        assert ok.status not in (401, 503), (route.path, ok.status)


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


def test_api__templates_carry_the_real_pinned_digests() -> None:
    """**The listing used to fabricate its own key.**

    `templateSha256` was `f"sha-{name}"`, so the wire carried `sha-FME_Quarterly` -- a value that
    identifies no file anywhere -- for three hand-written names against a corpus of nine. Every
    digest here now has to match the hash-verified manifest the rest of the system pins against.
    """
    manifest = json.loads(Path("fixtures/prescribed/MANIFEST.json").read_text(encoding="utf-8"))
    expected = {f["sha256"] for f in manifest["files"]}

    rows = _get("/v1/templates").json()
    assert len(rows) == len(expected) == manifest["count"]
    assert {r["templateSha256"] for r in rows} == expected
    for r in rows:
        assert SHA256_HEX.match(r["templateSha256"]), r
        assert not r["templateSha256"].startswith("sha-"), "the fabricated key is back"


def test_api__templates_omit_the_ceiling_rather_than_inventing_one() -> None:
    """The old ceiling was the literal 0.63, the same for every row and derived from nothing.

    Omitted, not null and not zero. NC-D03b's distinction survives in the REASON: the two
    workbooks with an empty v3 mask say so, and the other seven say that this build computes no
    per-template ceiling at all. Those are different absences and one value for both would be the
    collapse the null-versus-zero rule exists to prevent.
    """
    rows = _get("/v1/templates").json()
    for r in rows:
        assert "settledFractionCeiling" not in r, r
        assert r["settledFractionCeilingUnavailable"]
    reasons = {r["templateSha256"]: r["settledFractionCeilingUnavailable"] for r in rows}
    no_mask = {reasons[sha] for sha in NO_MASK_TEMPLATE_SHA256}
    others = {v for k, v in reasons.items() if k not in NO_MASK_TEMPLATE_SHA256}
    assert len(no_mask) == 1 and len(others) == 1
    assert no_mask.isdisjoint(others), "one reason for two different absences"


def test_api__template_schema_does_not_serve_the_same_body_for_any_sha() -> None:
    """It ignored `{sha}` and returned this API's OWN response DTOs, identically, for everything."""
    manifest = json.loads(Path("fixtures/prescribed/MANIFEST.json").read_text(encoding="utf-8"))
    pinned = sorted(f["sha256"] for f in manifest["files"])[0]

    known = _get(f"/v1/templates/{pinned}/schema")
    unknown = _get("/v1/templates/deadbeef/schema")
    assert known.body != unknown.body
    assert unknown.status == 404 and unknown.json()["error"] == "no_such_template"
    assert known.status == 501 and known.json()["error"] == "template_schema_not_served"
    # And neither one hands back `DenominatorOut`/`RunOut`/`ErrorOut` under a template's name.
    for r in (known, unknown):
        assert b"DenominatorOut" not in r.body


def test_api__verify_refuses_rather_than_answering_without_reading_the_body() -> None:
    """It was a two-line constant: a genuine attestation, garbage and an empty body all got the
    same `reproduced: false`, which is a determination made about a document nobody opened."""
    for body in (b"", b"not-json", b'{"runId": "r1"}'):
        r = dispatch(Request("POST", "/v1/verify", body=body))
        assert r.status == 501, body
        assert r.json()["error"] == "verification_not_available_over_http"
        # No `reproduced` FIELD. The detail quotes the word to name what it used to answer, which
        # is why this asserts over the keys rather than over the bytes.
        assert "reproduced" not in r.json()


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


def test_api__admission_refuses_instead_of_claiming_six_stages_ran(monkeypatch) -> None:
    """**It returned the same 202 for an .xlsx, an empty body, garbage and a PDF.**

    `"T1-T6 ran. T7 is a human signature"` described work no code performs: T1 through T7 are
    named in `spec/03-stack.md` and no source file implements any of them. The endpoint never read
    the request body either, so the sentence was not even about the upload.
    """
    monkeypatch.setenv(OPERATOR_TOKEN_ENV, "s3cret")
    bodies = [b"", b"%PDF-1.4 not a workbook", b"\x00\x01\x02", BINDS.read_bytes()]
    seen = set()
    for body in bodies:
        r = dispatch(Request("POST", "/v1/templates",
                             headers={"authorization": "Bearer s3cret"}, body=body))
        assert r.status == 501, body[:8]
        assert r.json()["error"] == "template_admission_not_implemented"
        assert "T1-T7" in r.json()["detail"] or "T1" in r.json()["detail"]
        seen.add(r.body)
    # It is still one answer for every body -- but now the answer is "this is not implemented",
    # which is TRUE of every body, rather than "six stages ran", which was true of none.
    assert len(seen) == 1

    # The nine pinned blanks are named, because they are the only templates a filing can bind to.
    rows = dispatch(Request("POST", "/v1/templates",
                            headers={"authorization": "Bearer s3cret"})).json()["pinnedTemplates"]
    manifest = json.loads(Path("fixtures/prescribed/MANIFEST.json").read_text(encoding="utf-8"))
    assert {r["templateSha256"] for r in rows} == {f["sha256"] for f in manifest["files"]}


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
