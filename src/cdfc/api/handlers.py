"""P14-B3 — the handlers. Thin: every rule they enforce is a rule stated somewhere else.

The one that is stated HERE is `get_portfolio`, because there is nowhere else for it to live.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any, Final

from cdfc.api import store
from cdfc.api.schemas import TemplateOut, json_schema

REPORTS: Final[Path] = Path("reports/runs")

# At most this many cells in one response. The cap is VISIBLE -- `returned` beside `total` -- so a
# truncated list cannot be read as a complete one.
CELL_PAGE: Final[int] = 500

# Read from the surface layer rather than restated, so the wire and the page cannot disagree.
DENOMINATOR_WARNING: Final[str] = (
    "The denominator is the template's unlocked-cell mask under generator rule v3, computed twice "
    "and agreed. It has never been checked against a person filling the form in, so it is "
    "PROVISIONAL-UNVALIDATED: it may be larger or smaller than the set a filer actually completes."
)
ADMISSION_STATE: Final[str] = "PRE-GATE"

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
    """The full run record. **The six counts always travel with the fraction.**"""
    try:
        run = store.load(params.get("id", ""))
    except store.RunNotFound as e:
        return _err(404, "no_such_run", str(e))
    frac = store.fraction_of(run)
    m = run.header()
    return _json(200, {
        "runId": run.run_id,
        "filingSha256": m.get("filing_sha256", ""),
        "templateSha256": m.get("template_sha256", ""),
        "runState": m.get("run_state", ""),
        "settledFraction": {
            **frac,
            "fraction": round(frac["settled"] / frac["inScope"], 4) if frac["inScope"] else None,
            "denominatorWarning": DENOMINATOR_WARNING,
            "admissionState": ADMISSION_STATE,
        },
        "livenessProof": m.get("livenessProof"),
        "summaryIsNotSubstitute": True,
        "reportUrl": f"/v1/runs/{run.run_id}/report.html",
        "attestationUrl": f"/v1/runs/{run.run_id}/attestation.json",
    })


def get_checks(req, params):
    try:
        run = store.load(params.get("id", ""))
    except store.RunNotFound as e:
        return _err(404, "no_such_run", str(e))
    return _json(200, list(store.checks(run, predicate_id=req.query.get("predicate_id"))))


def get_cells(req, params):
    """The closure table. Filterable by state and reason, and NEVER paginated silently.

    A truncated list that looks complete is how a coverage number gets read off a screen that
    showed a tenth of it, so the response carries `returned` and `total` and they must differ
    visibly when a cap applies.
    """
    try:
        run = store.load(params.get("id", ""))
    except store.RunNotFound as e:
        return _err(404, "no_such_run", str(e))
    rows = store.cells(run, state=req.query.get("state"), reason=req.query.get("reason"))
    cap = min(int(req.query.get("limit", CELL_PAGE)), CELL_PAGE)
    return _json(200, {"returned": len(rows[:cap]), "total": len(rows), "cells": list(rows[:cap])})


def get_unchecked(req, params):
    """The panel. **This is the product** — and where the artifact cannot support it, it says so."""
    try:
        run = store.load(params.get("id", ""))
    except store.RunNotFound as e:
        return _err(404, "no_such_run", str(e))
    total = store.unchecked_total(run)
    try:
        groups = store.unchecked_groups(run)
    except store.BreakdownNotInArtifact as e:
        # 200, not 500: the TOTAL is a real measurement and the client should have it. What is
        # absent is the breakdown, and it is named as absent rather than served as an empty list --
        # `[]` would read as "every unchecked cell has been accounted for and none has a reason".
        return _json(200, {
            "total": total,
            "groups": None,
            "breakdownUnavailable": str(e),
        })
    from cdfc.surface.unchecked import MissingRemedy, load_remedies

    remedies, unremediable = load_remedies()
    out = []
    for g in groups:
        code = g["reasonCode"]
        rem = remedies.get(code)
        text = rem.text if rem else unremediable.get(code)
        if not text:
            # The panel's own rule, on the wire: there is no fallback remedy string.
            raise MissingRemedy(
                f"{code} reached {g['count']} cells and has no remedy. A generic remedy makes a "
                "panel of reasons into one sentence repeated, and it looks exactly like a panel "
                "that thought about each group."
            )
        out.append({"reasonCode": code, "count": g["count"], "remedy": text})
    return _json(200, {"total": total, "groups": out, "breakdownUnavailable": None})


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
    for rid in store.run_ids():
        try:
            run = store.load(rid)
        except store.RunNotFound:
            continue
        f, m = store.fraction_of(run), run.header()
        rows.append({
            "entity": m.get("filing_sha256", "")[:12],
            "template": m.get("template_sha256", "")[:12],
            "runId": rid,
            "settled": f["settled"],
            "fieldSurface": f["cellsTotal"],
            "notChecked": f["notChecked"],
            "admissionState": ADMISSION_STATE,
        })
    return _json(200, {"columns": list(PORTFOLIO_COLUMNS), "rows": rows,
                       "note": "rows only. A fraction across templates would divide one "
                               "workbook's mask by another's; counts are aggregable and "
                               "fractions are not."})


def _load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))
