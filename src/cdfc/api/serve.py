"""P14-B3 completion — the HTTP server. **The only module in `cdfc.api` that opens a socket.**

`app.dispatch()` is a pure `Request -> Response`. This file is the thin shell that binds a port and
calls it, and it is deliberately the ONLY place a socket appears: `tests/unit/test_api.py::
test_api__no_socket_in_the_import_closure` walks every other module in the package and fails if one
imports `socket`, `httpx` or a vendor SDK, with this file explicitly excluded by name.

That split is not tidiness. `plan/06` P13-B0 bans network modules from the closure of every verdict
root, and it is the reason the API lives in `cdfc.api` rather than `cdfc.surface`. Keeping the
socket in a leaf nothing imports means the dispatcher stays testable in-process, the report
renderer stays inside a clean closure, and neither claim rests on the other.

## `wsgiref`, not a framework

The standard library's WSGI server is ~30 lines away from a working service here, single-threaded
and synchronous — which is what the measurement says this workload is: the deterministic core is
~30 ms and the traffic is **3.4 filings per working day** (868/yr MODELED, from 217 FMEs x 4
quarters). A throughput target would be theatre, and `plan/07` says so in as many words. Adding a
framework would add a dependency surface to a product whose claim is that its verdict path is
small and auditable, in exchange for concurrency nobody needs.

**It binds 127.0.0.1 by default.** A coverage tool that listens on 0.0.0.0 the first time somebody
runs it is a coverage tool that ends up on a network nobody meant to put it on. Binding publicly is
an explicit argument.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Final

from cdfc.api.app import MAX_UPLOAD_BYTES, Request, dispatch

DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 8765

# Read paths are public by design -- the predicate library and the rejection list are the two
# surfaces this product exists to expose. Nothing here adds authentication; the three mutating
# paths carry their own operator token, checked in `app.dispatch`.
_HOP_BY_HOP: Final[frozenset[str]] = frozenset({"connection", "keep-alive", "transfer-encoding"})


def _environ_to_request(environ: dict[str, Any]) -> Request:
    from urllib.parse import parse_qs

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length else b""
    query = {k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}
    headers = {
        k[5:].replace("_", "-").lower(): v
        for k, v in environ.items()
        if k.startswith("HTTP_") and k[5:].replace("_", "-").lower() not in _HOP_BY_HOP
    }
    if environ.get("CONTENT_TYPE"):
        headers["content-type"] = environ["CONTENT_TYPE"]
    return Request(
        method=environ.get("REQUEST_METHOD", "GET"),
        path=environ.get("PATH_INFO", "/"),
        query=query,
        headers=headers,
        body=body,
    )


_STATUS_TEXT: Final[dict[int, str]] = {
    200: "OK", 201: "Created", 202: "Accepted", 401: "Unauthorized", 404: "Not Found",
    413: "Payload Too Large", 415: "Unsupported Media Type", 422: "Unprocessable Content",
    500: "Internal Server Error", 501: "Not Implemented", 503: "Service Unavailable",
}


def _serve(start_response: Callable[..., Any], status: int, body: bytes, ctype: str,
           headers: tuple[tuple[str, str], ...]) -> list[bytes]:
    line = f"{status} {_STATUS_TEXT.get(status, 'Unknown')}"
    start_response(line, [("Content-Type", ctype), ("Content-Length", str(len(body))), *headers])
    return [body]


def application(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
    """The WSGI entry point. **It chooses a CSP and calls one of two pure renderers.**

    No response is SHAPED here — a response shaped in this file would be a response no gate had
    seen. What this file decides is which security policy a path carries, and that decision is a
    lookup in `_csp_for`, which a test walks over every route in both tables.
    """
    path = environ.get("PATH_INFO", "/")

    if path.startswith("/static/"):
        return _static(start_response, path)

    # The twelve screens. Everything NOT under `/v1` is a screen, so a new API route can never
    # accidentally acquire the app's looser policy by being added to the wrong table.
    if not path.startswith("/v1/"):
        from cdfc.surface.web import render_path

        method = environ.get("REQUEST_METHOD", "GET").upper()
        form = _form_of(environ) if method == "POST" else {}
        status, html = render_path(path, _query_of(environ), method=method, form=form)
        return _serve(start_response, status, html.encode("utf-8"),
                      "text/html; charset=utf-8", _APP_HEADERS)

    response = dispatch(_environ_to_request(environ))
    return _serve(start_response, response.status, response.body, response.content_type,
                  _ARTIFACT_HEADERS)


def _query_of(environ: dict[str, Any]) -> dict[str, str]:
    from urllib.parse import parse_qs

    return {k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}


# The multipart boundary parser below is ~20 lines and replaces `cgi.FieldStorage`, which is
# deprecated in 3.12 and REMOVED in 3.13. A dependency added to parse one upload would be a
# dependency inside a product whose claim is that its serving path is small and auditable.
def _form_of(environ: dict[str, Any]) -> dict[str, Any]:
    """The submitted form. **This exists so every screen works with scripting off.**

    Without it the drop form's `POST /v1/filings` renders raw JSON in the browser — which is a
    working API and a broken product. Text fields come back as `str`; the single file field comes
    back as `(filename, bytes)`.
    """
    from urllib.parse import parse_qs

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    if length <= 0 or length > MAX_UPLOAD_BYTES:
        return {}
    body = environ["wsgi.input"].read(length)
    ctype = environ.get("CONTENT_TYPE", "")

    if ctype.startswith("application/x-www-form-urlencoded"):
        return {k: v[0] for k, v in parse_qs(body.decode("utf-8", "replace")).items()}
    if not ctype.startswith("multipart/form-data") or "boundary=" not in ctype:
        return {}

    boundary = ctype.split("boundary=", 1)[1].strip().strip('"').encode()
    out: dict[str, Any] = {}
    for part in body.split(b"--" + boundary):
        head, sep, payload = part.partition(b"\r\n\r\n")
        if not sep:
            continue
        disposition = ""
        for line in head.decode("utf-8", "replace").splitlines():
            if line.lower().startswith("content-disposition:"):
                disposition = line
        if 'name="' not in disposition:
            continue
        name = disposition.split('name="', 1)[1].split('"', 1)[0]
        value = payload[:-2] if payload.endswith(b"\r\n") else payload
        if 'filename="' in disposition:
            filename = disposition.split('filename="', 1)[1].split('"', 1)[0]
            out[name] = (filename, value)
        else:
            out[name] = value.decode("utf-8", "replace")
    return out


def _static(start_response: Callable[..., Any], path: str) -> list[bytes]:
    """The stylesheet and the script, GENERATED — there is no static directory on disk.

    Nothing is read from the filesystem here, so there is no path to traverse: an unknown name is a
    404 rather than an attempt to open something. Both assets are produced by functions in
    `cdfc.surface.web`, which is what keeps the palette in `design.py` and nowhere else.
    """
    from cdfc.surface.web.script import app_script
    from cdfc.surface.web.style import app_stylesheet

    assets = {
        "/static/app.css": (app_stylesheet, "text/css; charset=utf-8"),
        "/static/app.js": (app_script, "text/javascript; charset=utf-8"),
    }
    hit = assets.get(path)
    if hit is None:
        return _serve(start_response, 404, b"not found", "text/plain; charset=utf-8",
                      _ARTIFACT_HEADERS)
    build, ctype = hit
    return _serve(start_response, 200, build().encode("utf-8"), ctype, _APP_HEADERS)


# ============================ THE TWO POLICIES ================================================
#
# THE ARTIFACT POLICY. `default-src 'none'` with **no `script-src` directive at all**, so the
# browser refuses any script rather than permitting one from a source. This covers every `/v1`
# path, and the one that matters is `GET /v1/runs/{id}/report.html`: the report is the ATTESTED
# artifact, its digest is what a third party verifies, and a script inside it would be executable
# code inside the one file that has to be trustworthy.
_ARTIFACT_HEADERS: Final[tuple[tuple[str, str], ...]] = (
    ("Content-Security-Policy",
     "default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'self'"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "no-referrer"),
    ("X-Frame-Options", "DENY"),
)

# THE APP POLICY. The twelve screens are an interactive product and need a script, so they get
# `script-src 'self'` -- one same-origin file and nothing else.
#
# **This is a narrowing, not a loosening.** The old header was applied to every response because
# every response was static, which said nothing about what was IN any of them. The guarantee is now
# asserted where it is claimed: `test_web__the_report_route_forbids_script` checks the header AND
# greps the served bytes of `report.html` for `<script`, which the blanket header never did.
#
# What is deliberately absent from this policy:
#   * no `'unsafe-inline'` for scripts -- an injected `onclick=` cannot run even if one reached
#     the DOM, which is why `script.py` attaches every handler with `addEventListener`;
#   * no `'unsafe-eval'`;
#   * no host in any directive -- `'self'` only, so a CDN cannot be added without changing this
#     tuple, and this tuple is asserted by a test.
_APP_HEADERS: Final[tuple[tuple[str, str], ...]] = (
    ("Content-Security-Policy",
     "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
     "img-src 'self' data:; connect-src 'self'; form-action 'self'; base-uri 'none'; "
     "frame-ancestors 'none'"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "same-origin"),
    ("X-Frame-Options", "DENY"),
)


def csp_for(path: str) -> str:
    """The policy a path carries. Exposed so a test can walk every route rather than sample two."""
    headers = _ARTIFACT_HEADERS if path.startswith("/v1/") else _APP_HEADERS
    return dict(headers)["Content-Security-Policy"]


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:  # pragma: no cover
    """Bind and serve. Covered by an in-process test of `application`, not by binding a port."""
    from wsgiref.simple_server import make_server

    with make_server(host, port, application) as httpd:
        print(f"cdfc serving on http://{host}:{port}  (drop screen at /)", file=sys.stderr)
        httpd.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    serve()
