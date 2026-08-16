"""P14-B3 — the OpenAPI document, GENERATED from the route table and the dataclasses.

The gate walks **this**, not a hand-written list of models. That is the whole point: a model added
without touching the gate is still scanned, and a property named `status` cannot reach a client by
being added somewhere nobody thought to check.
"""

from __future__ import annotations

from typing import Any

from cdfc.api.routes import ROUTES
from cdfc.api.schemas import json_schema


def openapi_document() -> dict[str, Any]:
    paths: dict[str, Any] = {}
    for r in ROUTES:
        entry = paths.setdefault(r.path, {})
        op: dict[str, Any] = {
            "summary": r.summary,
            "operationId": r.handler,
            "responses": {"200": {"description": r.summary}},
        }
        if r.mutating:
            op["security"] = [{"operatorToken": []}]
            op["responses"]["401"] = {"description": "operator token required"}
            op["responses"]["503"] = {"description": "operator token not configured"}
        entry[r.method.lower()] = op
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "cdfc",
            "version": "0.0.1",
            "description": (
                "A coverage declaration. This API reports what was checked and what was not. "
                "It has no property that means a filing passed, and it cannot emit a settled "
                "fraction without the six counts that give it a denominator."
            ),
        },
        "components": {
            "securitySchemes": {
                "operatorToken": {"type": "http", "scheme": "bearer"},
            },
        },
        "paths": paths,
        **json_schema(),
    }
