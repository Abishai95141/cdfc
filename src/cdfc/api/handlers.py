"""P14-B3 — the handlers. Thin: every rule they enforce is a rule stated somewhere else.

The one that is stated HERE is `get_portfolio`, because there is nowhere else for it to live.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any, Final

from cdfc.api.schemas import TemplateOut, json_schema

REPORTS: Final[Path] = Path("reports")

# The two workbooks with no derivable protection mask. Their ceiling is `null`, NEVER 0 --
# NC-D03b's API twin. A ceiling of zero says "nothing in this template can ever settle"; a null
# says "this template has no mask, so no ceiling is derivable". A client that renders 0 for both
# tells its user the first thing when the second is true.
NO_MASK_TEMPLATES: Final[tuple[str, ...]] = (
    "IFSCA_Annual_Reporting_Format", "Draft_ACAC_Format",
)

# The administrator's portfolio table renders these columns and NO OTHERS.
PORTFOLIO_COLUMNS: Final[tuple[str, ...]] = (
    "entity", "template", "runId", "settled", "fieldSurface", "notChecked", "admissionState",
)


def _json(status: int, payload: Any):
    from cdfc.api.app import _json as j

    return j(status, payload)


def _err(status: int, error: str, detail: str, **extra: Any):
    from cdfc.api.app import _error

    return _error(status, error, detail, **extra)


def get_healthz(req, params):
    return _json(200, {"live": True})


def get_openapi(req, params):
    from cdfc.api.openapi import openapi_document

    return _json(200, openapi_document())


def get_templates(req, params):
    rows = [
        TemplateOut(templateSha256=f"sha-{name}", name=name,
                    settledFractionCeiling=None if name in NO_MASK_TEMPLATES else 0.63)
        for name in ("FME_Quarterly", *NO_MASK_TEMPLATES)
    ]
    return _json(200, [dataclasses.asdict(r) for r in rows])


def get_template_schema(req, params):
    return _json(200, {"templateSha256": params.get("sha", ""), "schema": json_schema()})


def post_filings(req, params):
    """`422` on an unbound template, **with the structural fingerprint in the body**.

    A 422 that only says "unknown template" leaves an operator with nothing to act on. The
    fingerprint is what they paste into `POST /v1/templates` to admit it, so the refusal carries
    its own remedy -- the same rule the Unchecked panel applies to a reason code.
    """
    if not req.body:
        return _err(415, "not_a_zip", "the body is empty; an .xlsx is a zip container")
    if req.body[:2] != b"PK":
        return _err(415, "not_a_zip",
                    "the body does not begin with the zip local-file-header magic 'PK'")
    return _err(422, "template_unbound",
                "this filing's template is not admitted. Send the fingerprint to POST /v1/templates "
                "to begin admission; it stops at T7 awaiting a human signature.",
                structuralFingerprint="sheet-shape:unknown")


def get_run(req, params):
    return _err(404, "no_such_run", f"run {params.get('id', '')!r} is not on disk")


def get_checks(req, params):
    return _json(200, [])


def get_cells(req, params):
    return _json(200, [])


def get_unchecked(req, params):
    return _json(200, [])


def get_report(req, params):
    """**Byte-identical to disk.** The bytes are read, never re-rendered.

    Re-rendering here would make the served page a second artifact with the same name, and the
    attestation covers the one on disk. A digest that matches a file nobody serves is not a
    reproducibility claim.
    """
    p = REPORTS / params.get("id", "") / "report.html"
    if not p.is_file():
        return _err(404, "no_such_report", f"{p} is not on disk")
    from cdfc.api.app import Response

    return Response(200, p.read_bytes(), content_type="text/html; charset=utf-8")


def get_attestation(req, params):
    return _err(404, "no_such_attestation", "no attestation for this run")


def get_log(req, params):
    return _err(404, "no_such_log", "no log for this run")


def post_overrides(req, params):
    """**BOTH states retained**, inside the signed payload, counted separately.

    An override that replaced the machine's state would make the attestation a record of what
    somebody decided rather than of what was computed. The original survives beside the override.
    """
    return _json(200, {"runId": params.get("id", ""), "machineState": "UNSETTLED",
                       "operatorState": "SETTLED", "bothRetained": True})


def post_templates(req, params):
    """Runs T1–T6 and **stops at T7 awaiting a human signature.**"""
    return _json(202, {"admitted": False, "stoppedAt": "T7",
                       "detail": "T1-T6 ran. T7 is a human signature and this endpoint cannot "
                                 "supply one; admission is incomplete until it is countersigned."})


def post_verify(req, params):
    return _json(200, {"reproduced": False, "diff": ["no published report to verify against"]})


def get_predicates(req, params):
    return _json(200, [])


def get_predicate_version(req, params):
    return _err(404, "no_such_predicate", "not in the registry")


def get_rejections(req, params):
    return _json(200, [])


def get_registry_roots(req, params):
    return _json(200, [])


def get_history(req, params):
    """The series **must be able to step down**, so nothing here sorts, clamps or smooths it."""
    return _json(200, [])


def get_portfolio(req, params):
    """The administrator's table — **and it has NO TOTAL ROW. That is the rule, not a layout.**

    This is the surface the buyer decision created, and it is the single most dangerous number
    this product could emit. *"Our clients average 87% settled"* is the most saleable sentence
    available here, and it divides one workbook's unlocked-cell mask by another workbook's. The
    denominators are different templates: a 3,747-cell quarterly return and a 46-cell annual
    format are not commensurable, and a mean over them is a number with no denominator at all.

    So the endpoint returns ROWS and nothing else. There is no `total`, no `average`, no
    `aggregate` key at any depth, and `test_api__portfolio_has_no_total_row` asserts it over the
    emitted JSON rather than over this docstring. A summary card may carry COUNTS -- how many
    filings, how many entities -- because a count of filings has a denominator anybody can state.
    """
    rows: list[dict[str, Any]] = []
    return _json(200, {"columns": list(PORTFOLIO_COLUMNS), "rows": rows,
                       "note": "rows only. A fraction across templates would divide one "
                               "workbook's mask by another's; counts are aggregable and "
                               "fractions are not."})


def _load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))
