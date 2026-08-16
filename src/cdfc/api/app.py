"""P14-B3 — the dispatcher. **A pure function from `Request` to `Response`. It opens no socket.**

`dispatch()` is synchronous, has no queue, no broker and no workers, and touches no network. That
is not asceticism: it is what lets `cdfc.api` be imported by a test without dragging `socket` into
an import closure that `plan/06` P13-B0 will walk. A socket exists in `serve.py` and nowhere else,
and nothing under test imports it.

## The operator token is compared in constant time, and its absence is not a pass

`hmac.compare_digest`, and a *missing* `CDFC_OPERATOR_TOKEN` in the environment means every
mutating path returns 503 rather than 200. An unset secret that disables the check is the
`swallowed exception` failure wearing a deployment's clothes.
"""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass, field
from typing import Any, Final

from cdfc.api import handlers
from cdfc.api.routes import Route, by_method_and_path, path_params

OPERATOR_TOKEN_ENV: Final[str] = "CDFC_OPERATOR_TOKEN"

# 25 MB. `plan/07` fixes 413 over the cap; the number is here so the gate and the handler cannot
# disagree about it.
MAX_UPLOAD_BYTES: Final[int] = 25 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class Request:
    method: str
    path: str
    query: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    def bearer(self) -> str | None:
        raw = self.headers.get("authorization") or self.headers.get("Authorization") or ""
        return raw[7:] if raw.startswith("Bearer ") else None


@dataclass(frozen=True, slots=True)
class Response:
    status: int
    body: bytes
    content_type: str = "application/json"

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


def _json(status: int, payload: Any) -> Response:
    # `sort_keys` and a fixed separator: the same object must serialise to the same bytes, because
    # `GET /v1/runs/{id}/report.html` is asserted byte-identical to disk and a client that diffs
    # two responses must be diffing content rather than dict ordering.
    return Response(status, json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                       ensure_ascii=False).encode("utf-8"))


def _error(status: int, error: str, detail: str, **extra: Any) -> Response:
    return _json(status, {"error": error, "detail": detail, **extra})


def dispatch(req: Request) -> Response:
    route = by_method_and_path(req.method, req.path)
    if route is None:
        return _error(404, "no_such_route", f"{req.method} {req.path} is not a route")

    if route.mutating:
        expected = os.environ.get(OPERATOR_TOKEN_ENV)
        if not expected:
            # NOT a pass. A deployment that forgot the secret must refuse the write, loudly.
            return _error(
                503, "operator_token_not_configured",
                f"{OPERATOR_TOKEN_ENV} is unset. A mutating path whose secret is missing refuses; "
                "treating an absent secret as an open door is how a check disappears in "
                "production while every test still passes.",
            )
        supplied = req.bearer()
        if supplied is None or not hmac.compare_digest(supplied, expected):
            return _error(401, "operator_token_required",
                          f"{req.method} {route.path} requires a bearer operator token")

    if len(req.body) > MAX_UPLOAD_BYTES:
        return _error(413, "too_large",
                      f"{len(req.body)} bytes exceeds the {MAX_UPLOAD_BYTES}-byte cap")

    fn = getattr(handlers, route.handler, None)
    if fn is None:
        # A route whose handler does not exist is a build error surfaced at request time; saying
        # so is better than a 404 that reads as "the client asked for the wrong thing".
        return _error(501, "handler_missing",
                      f"route {route.method} {route.path} names handler {route.handler!r}, "
                      "which does not exist")
    return fn(req, path_params(route, req.path))


def route_of(method: str, path: str) -> Route | None:
    return by_method_and_path(method, path)
