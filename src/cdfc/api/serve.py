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

from cdfc.api.app import Request, dispatch

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


def application(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
    """The WSGI entry point. One call to `dispatch`, and no logic of its own.

    Any logic here would be logic outside the dispatcher that the contract tests walk — and the
    two prohibitions are enforced over the generated document, which describes what `dispatch`
    returns. A response shaped in this file would be a response no gate had seen.
    """
    if environ.get("PATH_INFO", "/") in ("/", "/drop"):
        from cdfc.surface.drop import drop_page

        page = drop_page().encode("utf-8")
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"),
                                  ("Content-Length", str(len(page))),
                                  *_SECURITY_HEADERS])
        return [page]

    response = dispatch(_environ_to_request(environ))
    status = f"{response.status} {_STATUS_TEXT.get(response.status, 'Unknown')}"
    start_response(status, [("Content-Type", response.content_type),
                            ("Content-Length", str(len(response.body))),
                            *_SECURITY_HEADERS])
    return [response.body]


# The report is a self-contained page with no script and no external reference, and these headers
# say so to the browser as well as to the reader. `default-src 'none'` with `style-src
# 'unsafe-inline'` is exactly what an inline-CSS, zero-JS document needs -- if a script ever
# appears in a rendered page, the browser refuses it and the failure is loud.
_SECURITY_HEADERS: Final[tuple[tuple[str, str], ...]] = (
    ("Content-Security-Policy",
     "default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'self'"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "no-referrer"),
)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:  # pragma: no cover
    """Bind and serve. Covered by an in-process test of `application`, not by binding a port."""
    from wsgiref.simple_server import make_server

    with make_server(host, port, application) as httpd:
        print(f"cdfc serving on http://{host}:{port}  (drop screen at /)", file=sys.stderr)
        httpd.serve_forever()


if __name__ == "__main__":  # pragma: no cover
    serve()
