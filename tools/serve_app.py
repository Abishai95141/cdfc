#!/usr/bin/env python
"""THE APPLICATION SERVER — the new `web/` surface and the `/v1` API, on one origin.

    python tools/serve_app.py [--port 8777] [--host 127.0.0.1]

## Why this is a tool and not `cdfc.api.serve`

Two reasons, and both are architectural rather than tidiness.

**The PDF reader.** `cdfc.ingest` is INSIDE the verdict closure, so no PDF reader may live in it —
`CLAUDE.md §4`, and `tests/negative/importgraph.py` enforces it positively. A PDF is read by
`tools/pdf_ingest.py`, which imports `docling` and `pdfplumber`. This launcher installs that
reader into `cdfc.api.live` through the seam it declares, exactly as a caller supplies
`model.propose(transport=…)`. If the libraries are absent the seam stays empty, the API refuses a
raw PDF with the reason and the remedy, and NOTHING about the closure changes.

**The old surface.** `cdfc.api.serve.application` serves `cdfc.surface.web`, the deprecated
thirteen-screen surface. Pointing it at the new one would leave two apps fighting over `/`.

## One origin, so there is no CORS and no second host

`fetch('/v1/…')` from `web/app.js` is same-origin. A separate API host would need `Access-Control-
Allow-Origin`, which is a header whose value is a decision about who may read a filer's data.

## The operator token

Three paths mutate: uploading an artefact, opening a return, and ANSWERING a question. An answer is
a named human asserting a value that goes into a regulator's return, so it carries a token like any
other accountable write. If `CDFC_OPERATOR_TOKEN` is unset this launcher generates one, prints it
ONCE on stderr, and exports it into the process — an unset secret makes every mutating path 503,
which is right for a deployment and useless for a person trying the application on their laptop.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import secrets
import sys
from typing import Any, Callable, Final

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.api.app import Request, dispatch  # noqa: E402
from cdfc.api.serve import _APP_HEADERS, _ARTIFACT_HEADERS, _STATUS_TEXT  # noqa: E402

WEB: Final[pathlib.Path] = REPO / "web"

# SAMPLE FILES, as a DECLARED TABLE — never a directory listing.
#
# The application is useless to try without something to upload, and hunting through `fixtures/`
# for the right five files is not a product. So the launcher mounts these at `/samples/`, the
# surface offers a one-click load, and the bytes go through exactly the same
# `POST /v1/artefacts` path a file picker uses. Nothing is faked: these are the real vendored
# blank, the real pinned statute and the real generated proposals.
#
# A table rather than a mount of `fixtures/`: a served directory is a path to traverse, and this
# way each sample carries the kind it is DECLARED as, which is the uploader's call and not a
# guess from an extension.
SAMPLES: Final[tuple[tuple[str, pathlib.Path, str, str], ...]] = (
    ("Reporting_Format_for_Fund_Management_Entities.xlsx",
     REPO / ("fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_"
             "02012026_20260102_0255.xlsx"),
     "template",
     "the IFSCA return, vendored under a hash-verified manifest. 3,747 unlocked cells"),
    ("statute-fm-regulations-2025.text.json",
     REPO / "corpus/instruments/statute-fm-regulations-2025.text.json",
     "instrument",
     "the FM Regulations 2025, already pinned — read by TWO INDEPENDENT extractors"),
    ("rules-corpus.txt", REPO / "fixtures/demo/rules-corpus.txt", "instrument",
     "a plain-text corpus, segmented by two of OUR OWN readers. Weaker corroboration, and the "
     "Corpus screen says so"),
    ("custodian_register.csv", REPO / "fixtures/demo/custodian_register.csv", "source",
     "two FMEs, with a legal structure and a contact person"),
    ("trial_balance.csv", REPO / "fixtures/demo/trial_balance.csv", "source",
     "the same two FMEs — and it DISAGREES with the register about one legal structure"),
    ("fme-proposals-generated.json", REPO / "fixtures/evidence/fme-proposals-generated.json",
     "rules",
     "LAYER 2 as DATA: 172 rule→field bindings a model wrote and the five gates adjudicate"),
)
_BY_NAME: Final[dict[str, tuple[pathlib.Path, str, str]]] = {
    n: (p, k, why) for n, p, k, why in SAMPLES
}


def _samples(start_response: Callable[..., Any], path: str) -> list[bytes]:
    """`/samples/index.json` lists them; `/samples/<name>` serves one. Name must be IN the table."""
    name = path[len("/samples/"):]
    if name == "index.json":
        import json

        body = json.dumps([
            {"name": n, "kind": k, "why": why, "bytes": (p.stat().st_size if p.is_file() else None),
             "present": p.is_file()}
            for n, p, k, why in SAMPLES
        ]).encode("utf-8")
        return _serve(start_response, 200, body, "application/json", _ARTIFACT_HEADERS)
    hit = _BY_NAME.get(name)
    if hit is None or not hit[0].is_file():
        return _serve(start_response, 404, b"no such sample", "text/plain; charset=utf-8",
                      _ARTIFACT_HEADERS)
    return _serve(start_response, 200, hit[0].read_bytes(), "application/octet-stream",
                  _ARTIFACT_HEADERS)


_TYPES: Final[dict[str, str]] = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
}


def _install_pdf_reader() -> bool:
    """Wire `tools/pdf_ingest.py` into the API's seam, if its readers are importable.

    Returns whether one was installed. **A failure to import is reported, never swallowed**: a
    launcher that silently ran without a PDF reader would leave the surface saying `installed:
    false` with no way to find out why.
    """
    try:
        import docling  # noqa: F401
        import pdfplumber  # noqa: F401
    except ImportError as e:
        print(f"pdf reader: NOT installed ({e}). A raw PDF upload will be refused with the "
              f"remedy; a pinned .text.json uploads normally.", file=sys.stderr)
        return False
    sys.path.insert(0, str(REPO / "tools"))
    from pdf_ingest import ingest  # noqa: PLC0415

    from cdfc.api.live import install_pdf_reader
    from cdfc.qualify.instruments import serialise

    def read(path: pathlib.Path, instrument_id: str) -> bytes:
        it = ingest(path, instrument_id)
        return serialise(it, kind="instrument", source_name=path.name,
                         source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    install_pdf_reader(read)
    print("pdf reader: installed (docling + pdfplumber, two arms)", file=sys.stderr)
    return True


def _serve(start_response: Callable[..., Any], status: int, body: bytes, ctype: str,
           headers: tuple[tuple[str, str], ...]) -> list[bytes]:
    start_response(f"{status} {_STATUS_TEXT.get(status, 'OK')}",
                   [("Content-Type", ctype), ("Content-Length", str(len(body))), *headers])
    return [body]


def _static(start_response: Callable[..., Any], path: str) -> list[bytes]:
    """Serve `web/`. **Resolved and then checked to be inside `web/`** — a path that escapes is a
    404 rather than a file, and the check is on the RESOLVED path, not on the string."""
    rel = "index.html" if path in ("", "/") else path.lstrip("/")
    target = (WEB / rel).resolve()
    try:
        target.relative_to(WEB.resolve())
    except ValueError:
        return _serve(start_response, 404, b"not found", "text/plain; charset=utf-8",
                      _ARTIFACT_HEADERS)
    if not target.is_file():
        return _serve(start_response, 404, b"not found", "text/plain; charset=utf-8",
                      _ARTIFACT_HEADERS)
    ctype = _TYPES.get(target.suffix, "application/octet-stream")
    return _serve(start_response, 200, target.read_bytes(), ctype, _APP_HEADERS)


def application(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
    path = environ.get("PATH_INFO", "/")
    if path.startswith("/samples/"):
        return _samples(start_response, path)
    if not path.startswith("/v1/"):
        return _static(start_response, path)

    from urllib.parse import parse_qs

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length else b""
    headers = {k[5:].replace("_", "-").lower(): v for k, v in environ.items()
               if k.startswith("HTTP_")}
    if environ.get("CONTENT_TYPE"):
        headers["content-type"] = environ["CONTENT_TYPE"]
    req = Request(
        method=environ.get("REQUEST_METHOD", "GET"),
        path=path,
        query={k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()},
        headers=headers,
        body=body,
    )
    r = dispatch(req)
    return _serve(start_response, r.status, r.body, r.content_type, _ARTIFACT_HEADERS)


def main() -> int:  # pragma: no cover
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8777)
    ap.add_argument("--app-root", default=os.environ.get("CDFC_APP_ROOT") or "runs/app")
    args = ap.parse_args()

    os.environ["CDFC_APP_ROOT"] = args.app_root
    token = os.environ.get("CDFC_OPERATOR_TOKEN")
    if not token:
        token = secrets.token_urlsafe(18)
        os.environ["CDFC_OPERATOR_TOKEN"] = token
        print("\n  CDFC_OPERATOR_TOKEN was unset, so one was generated for this process.\n"
              "  Three paths mutate — upload, open a return, and ANSWER a question — and each "
              "needs it.\n"
              f"\n      {token}\n\n"
              "  Paste it into the application's header field. It is not written to disk.\n",
              file=sys.stderr)

    _install_pdf_reader()

    from wsgiref.simple_server import make_server

    if not WEB.is_dir():
        print(f"no web/ directory at {WEB}", file=sys.stderr)
        return 2
    print(f"cdfc application on http://{args.host}:{args.port}   "
          f"(app root {pathlib.Path(args.app_root).resolve()})", file=sys.stderr)
    with make_server(args.host, args.port, application) as httpd:
        httpd.serve_forever()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
