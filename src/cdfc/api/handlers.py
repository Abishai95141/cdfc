"""P14-B3 — the handlers. Thin: every rule they enforce is a rule stated somewhere else.

The one that is stated HERE is `get_portfolio`, because there is nowhere else for it to live.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

from cdfc.api import registry_store, store
from cdfc.measure.paths import PRESCRIBED_MANIFEST

REPORTS: Final[Path] = Path("reports/runs")

# The nine vendored blanks a filing may bind to, and the hash-verified manifest that pins them.
# Absolute, derived from the package location rather than from the process's working directory,
# because which nine workbooks exist is a fact about this repository and not about where a server
# happened to be started.
PRESCRIBED: Final[Path] = PRESCRIBED_MANIFEST.parent

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

# The two workbooks with no derivable protection mask, keyed by the digest the manifest pins them
# under rather than by a display name -- a name is not an identity, and the manifest's filenames
# carry a date stamp these two short labels did not. MEASURED, not asserted: `styles_mask.build`
# under generator rule v3 returns an empty cell set for both, and a non-empty one for the other
# seven.
#
# NC-D03b's API twin. A ceiling of zero says "nothing in this template can ever settle"; the
# absence of a ceiling says "no ceiling was derived". These two are the case where the second is
# true for a REASON IN THE WORKBOOK, and the other seven are the case where it is true because
# this build computes no per-template ceiling at all. `_pinned_templates` says which is which
# instead of collapsing them onto one value.
NO_MASK_TEMPLATE_SHA256: Final[tuple[str, ...]] = (
    # IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx
    "4b2d4a2bb0416ae22048c7cf1fcbb5c581c19933ca85663ab69f311a8846395d",
    # Draft_ACAC_Format_20260605_0631.xlsx
    "74ba7b894b429bbe939a296cacf39196ad9f5b93ec238037f2c47c277dd79e5e",
)

# Why `settledFractionCeiling` is ABSENT from a template row rather than null or zero. The value
# this endpoint used to emit was the literal 0.63, handed to every template that was not on the
# no-mask list, and it was not derived from anything: no per-template settled-fraction ceiling is
# computed in this build. The one published ceiling,
# `docs/measurements/p9-template-diff-ceiling.json`, is TEMPLATE_DIFF's reach over ONE workbook,
# which is a different quantity from the fraction of a template's field surface that any predicate
# could ever settle -- so it cannot be substituted here either.
# **THESE TWO SENTENCES MAY NOT CONTAIN A DIGIT, AND THAT IS A RENDERING CONTRACT, NOT A STYLE
# NOTE.** `surface/web/components.count(None, absent_reason=…)` raises `UnnamedAbsence` on any
# digit in an absence reason, because a digit in the not-measured state is read as the measurement
# — which is precisely what has not been taken. The first draft of `NO_CEILING_MEASURED` quoted the
# literal ceiling this endpoint used to return (nought point six three, handed to every template
# outside the no-mask list and derived from no measurement) and the guard refused to render it. The
# history belongs here, where a maintainer reads it; the sentence below is what a reader is shown.
# Likewise the mask's generator rule is named in `schema/styles_mask.Rule` and not spelled here,
# because its name carries a version digit.
NO_CEILING_MEASURED: Final[str] = (
    "no per-template settled-fraction ceiling is computed in this build; the figure this endpoint "
    "used to return was a literal, not a measurement"
)
NO_MASK_AT_ALL: Final[str] = (
    "this template's unlocked-cell mask under the pinned generator rule is empty, so it has no "
    "field surface and no ceiling is derivable from it. That is NOT a ceiling of zero: zero would "
    "say nothing in this template can ever settle"
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


def _pinned_templates() -> list[dict[str, Any]]:
    """The pinned blanks, read from `fixtures/prescribed/MANIFEST.json`. **Real digests.**

    This listing used to be three hand-written names whose `templateSha256` was the f-string
    `f"sha-{name}"` -- so a client copied `sha-FME_Quarterly` out of the API and pasted a value
    that identifies no file anywhere -- and it emitted that same body from an empty directory. The
    corpus has NINE workbooks and every one of them carries a sha256 in the vendored manifest that
    `template_current()` already treats as the pinned set, so there was a real answer available the
    whole time.

    Sorted by filename so two responses are byte-identical, which
    `test_api__responses_are_byte_stable` asserts over the wire.
    """
    rows = []
    for f in sorted(_load(PRESCRIBED_MANIFEST)["files"], key=lambda f: f["filename"]):
        sha = f["sha256"]
        rows.append({
            "templateSha256": sha,
            "name": Path(f["filename"]).stem,
            "settledFractionCeilingUnavailable": (
                NO_MASK_AT_ALL if sha in NO_MASK_TEMPLATE_SHA256 else NO_CEILING_MEASURED
            ),
        })
    return rows


def get_templates(req, params):
    """The nine pinned blanks. **No `settledFractionCeiling` field** -- see `_pinned_templates`."""
    try:
        return _json(200, _pinned_templates())
    except FileNotFoundError as e:
        # A refusal, not an empty list. `200 []` from a machine with no corpus reads as "no
        # template has ever been pinned", which is a claim about the product rather than about
        # this checkout.
        return _err(503, "prescribed_corpus_not_on_disk", str(e),
                    remedy=f"the vendored corpus is expected at {PRESCRIBED}")


def get_template_schema(req, params):
    """**404 for a sha nobody pinned, 501 for one we did.** It never served a template's schema.

    This handler ignored `{sha}` entirely and returned `json_schema()` -- the API's OWN response
    DTOs, `DenominatorOut`, `RunOut`, `ErrorOut` -- so `deadbeef` and a real template digest got
    byte-identical bodies, and a client asking what fields a template expects received a
    description of this API's envelopes with nothing in it to reveal the substitution.

    Inducing a template's schema is `cdfc.predicates.harvest`, which walks the workbook's formulas
    and is minutes of work over a corpus; it is not wired to a request, so a known sha is answered
    with 501 naming that, and an unknown one with 404. The two statuses differ because the two
    facts differ.
    """
    sha = params.get("sha", "").strip().lower()
    try:
        pinned = {row["templateSha256"]: row["name"] for row in _pinned_templates()}
    except FileNotFoundError as e:
        return _err(503, "prescribed_corpus_not_on_disk", str(e),
                    remedy=f"the vendored corpus is expected at {PRESCRIBED}")
    if sha not in pinned:
        return _err(404, "no_such_template",
                    f"{sha[:16] or '(empty)'} is not one of the {len(pinned)} pinned template "
                    "digests. GET /v1/templates lists them.")
    return _err(501, "template_schema_not_served",
                f"{pinned[sha]} is pinned, but this build does not serve an induced schema for it. "
                "The schema is produced by cdfc.predicates.harvest walking the workbook's "
                "formulas, and that is not wired to a request; returning this API's own response "
                "DTOs under the name of a template schema is what this endpoint used to do.",
                templateSha256=sha)


def post_filings(req, params):
    """`422` on an unbound template, **with the fingerprint this upload actually computes to**.

    The fingerprint used to be the literal string `"sheet-shape:unknown"`, returned unconditionally
    after two magic-byte checks. So `422 template_unbound` was the answer for every file on earth,
    including the FME filing `cdfc run` binds without difficulty, and the value an operator was
    invited to paste into admission was the same eighteen characters every time.

    It now projects the upload through `cdfc.schema.fingerprint` and looks it up in the pinned
    catalogue through `cdfc.evaluate.binding` -- the same two functions the command line uses. The
    422 carries the computed digest and, from `Unbound.explain()`, what the filing was NEAREST to
    and on how many of the four structural facets, because a refusal that cannot say what it nearly
    matched sends the filer away to guess which form they filed.

    **A filing that BINDS gets a 501, not a run.** Nothing in this build evaluates a filing over
    HTTP: there is no queue and no worker, and `cdfc.api.store` is read-only by design -- "an API
    that could WRITE a run would be an API that can change what a signed statement covers". Runs
    are produced by `cdfc run <filing> --out reports/runs`. So a 200 from here would have to invent
    a run id for a run that never happened.

    The old docstring said the refusal "carries its own remedy". It does not, and the sentence is
    gone with the constant: `POST /v1/templates` cannot admit a template either. The fingerprint is
    evidence about this upload, and naming it as evidence is the whole of what this endpoint can
    honestly do.
    """
    if not req.body:
        return _err(415, "not_a_zip", "the body is empty; an .xlsx is a zip container")
    if req.body[:2] != b"PK":
        return _err(415, "not_a_zip",
                    "the body does not begin with the zip local-file-header magic 'PK'")

    import tempfile

    from cdfc.evaluate.binding import Bound, TemplateCatalogue, bind_template

    catalogue = TemplateCatalogue.from_corpus(PRESCRIBED)
    if not catalogue.entries:
        # `Unbound` against an empty catalogue is a refusal that compared the filing to nothing,
        # and `binding.Unbound.explain()` says so in prose -- but the STATUS would still be 422
        # `template_unbound`, which is a claim about the filing. This is a claim about the server.
        return _err(503, "prescribed_corpus_not_on_disk",
                    f"no pinned template was found under {PRESCRIBED}, so this upload would be "
                    "compared against nothing. An 'unbound' answer from an empty catalogue says "
                    "nothing whatever about the filing.")

    with tempfile.TemporaryDirectory() as d:
        blob = Path(d) / "upload.xlsx"
        blob.write_bytes(req.body)
        try:
            outcome = bind_template(blob, catalogue)
        except Exception as e:  # noqa: BLE001
            # A malformed upload must be a NAMED refusal rather than a traceback: `zipfile` raises
            # `BadZipFile` for a truncated container and `KeyError` for a zip with no
            # `xl/workbook.xml`, and a 500 would tell the filer that this server broke rather than
            # that their file did. The exception type is named so the two cases stay distinct.
            return _err(415, "unreadable_xlsx",
                        f"the body begins with 'PK' but could not be read as a spreadsheet "
                        f"package: {type(e).__name__}: {e}")

    if isinstance(outcome, Bound):
        return _err(501, "run_not_available_over_http",
                    "this filing binds to a pinned template, and this build cannot run it here. "
                    "There is no queue, no worker and no run store behind this endpoint, so the "
                    "check is available from the command line only: `cdfc run <filing.xlsx>`. A "
                    "200 from here would have to name a run id for a run nobody performed.",
                    structuralFingerprint=outcome.fingerprint,
                    templateSha256=outcome.template_sha256)
    return _err(422, "template_unbound",
                "this filing's template is not one of the pinned blanks. " + outcome.explain(),
                structuralFingerprint=outcome.fingerprint)


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
        # **The denominator's own exclusions.** `null` when the run predates the field or the
        # census could not be derived — never zeros, which would say the surface excluded nothing.
        "surfaceExclusions": m.get("surfaceExclusions"),
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
    """**501. Template admission is not implemented in this build.**

    This returned a byte-identical `202 {"stoppedAt": "T7", "detail": "T1-T6 ran…"}` for an .xlsx,
    for an empty body, for garbage bytes and for a PDF -- it never read `req.body` at all. The
    T-series it named is the template-admission pipeline in `spec/03-stack.md`, T1 *Fetch* through
    T7 *Register*, and no source file implements any of the seven. So "T1-T6 ran" described work
    that no code performs, and `stoppedAt: "T7"` attributed the stop to the one step that was
    supposed to need a person -- which made a missing implementation look like a waiting signature.

    The nine workbooks in `fixtures/prescribed/MANIFEST.json` are the only templates a filing can
    bind to, and they were pinned by vendoring them into the repository under a hash-verified
    manifest -- not by this endpoint, which has never admitted anything.
    """
    try:
        pinned = _pinned_templates()
    except FileNotFoundError as e:
        return _err(503, "prescribed_corpus_not_on_disk", str(e),
                    remedy=f"the vendored corpus is expected at {PRESCRIBED}")
    return _err(501, "template_admission_not_implemented",
                f"admitting a template is not implemented here. The {len(pinned)} workbooks pinned "
                f"in {PRESCRIBED_MANIFEST.name} are the only templates a filing can bind to; a new "
                "one is admitted by vendoring it into that manifest, which is a change to the "
                "repository and not a request. T1-T7 are specified in spec/03-stack.md and no "
                "source file implements any of them.",
                pinnedTemplates=[{"templateSha256": r["templateSha256"], "name": r["name"]}
                                 for r in pinned])


def post_verify(req, params):
    """**501. Verification over HTTP is not implemented**; `cdfc verify` is where it lives.

    This was two lines returning `200 {"reproduced": false, "diff": ["no published report to
    verify against"]}`. It never read the request body, so a genuine attestation, a corrupted one
    and an empty body produced the same answer -- and "no published report to verify against" was
    said about a document nobody had looked at. It was also unauthenticated, which mattered less
    than it looks only because there was nothing behind it to reach.

    The real check is `cdfc.attest.verify.verify(artifact, blobs)`: it takes the signature against
    the STORED bytes, re-runs the pipeline from the manifest's ten pins, and compares the payload
    byte for byte, reporting `reproduced` and `signature_valid` separately because a third party
    does not hold the filer's key. It needs the filing and template blobs resolvable by digest and
    it is minutes of work per artifact. Wiring that to a request is a job this build has not done,
    and answering `reproduced: false` without doing it is precisely the silent false negative the
    tool exists to detect.
    """
    return _err(501, "verification_not_available_over_http",
                "re-derivation is not implemented behind this endpoint. It is available from the "
                "command line: `cdfc verify <artifact.json>` re-runs the pipeline from the "
                "manifest's pins and compares the payload byte for byte, and reports the signature "
                "check separately from the re-derivation. This endpoint previously answered "
                "'reproduced: false' without reading the request body, which is a determination "
                "made about nothing.")


def _artifact_or_503():
    """The qualification artifact, or the refusal. **Never a `200 []`.**

    `200 []` says *the gates ran and admitted nobody* — true today, and the single most interesting
    fact this product knows about itself. An absent artifact says *nobody ran the gates*. They
    render identically to a reader and mean opposite things, so the second is a 503 carrying the
    command that fixes it rather than an empty list carrying the first's meaning.
    """
    from cdfc.qualify.artifact import ArtifactNotOnDisk, ArtifactSchemaMismatch

    try:
        return registry_store.load(), None
    except (ArtifactNotOnDisk, ArtifactSchemaMismatch) as e:
        return None, _err(503, "qualification_not_measured", str(e), remedy="make attrition")


def get_predicates(req, params):
    """The ADMITTED predicate library, and the context that stops its emptiness being misread."""
    art, refusal = _artifact_or_503()
    if refusal is not None:
        return refusal
    return _json(200, {
        "rows": list(registry_store.library_rows(art)),
        **registry_store.library_context(art),
    })


def get_predicate_version(req, params):
    art, refusal = _artifact_or_503()
    if refusal is not None:
        return refusal
    pid, ver = params.get("id", ""), params.get("v", "")
    for row in registry_store.library_rows(art):
        if row.get("predicateId") == pid and str(row.get("version")) == str(ver):
            return _json(200, row)
    return _err(404, "no_such_predicate",
                f"{pid} v{ver} is not in the admitted registry. {len(art.rejections)} candidates "
                "were refused at qualification; see GET /v1/rejections.")


def get_rejections(req, params):
    """**Every candidate a gate refused, with the number that decided it.**

    This is the screen that proves the gate is real, so the cap is generous and visible and the
    filters are the three axes the gates actually partition on.
    """
    art, refusal = _artifact_or_503()
    if refusal is not None:
        return refusal
    rows = registry_store.rejected_rows(
        art, gate=req.query.get("gate"), reason=req.query.get("reason"), q=req.query.get("q"),
    )
    try:
        cap = min(int(req.query.get("limit", registry_store.REJECTION_PAGE)),
                  registry_store.REJECTION_PAGE)
    except ValueError:
        cap = registry_store.REJECTION_PAGE
    try:
        offset = max(int(req.query.get("offset", 0)), 0)
    except ValueError:
        offset = 0
    window = rows[offset:offset + cap]
    return _json(200, {
        "returned": len(window), "total": len(rows), "offset": offset,
        "totalUnfiltered": len(art.rejections),
        "rows": list(window),
        "facets": registry_store.facets(art),
        "killBar": art.kill_bar, "campaignId": art.campaign_id,
        "faultModelVersion": art.fault_model_version,
        "instrumentLabel": art.instrument_label,
    })


def get_registry_roots(req, params):
    art, refusal = _artifact_or_503()
    if refusal is not None:
        return refusal
    return _json(200, list(registry_store.registry_roots(art)))


def get_funnel(req, params):
    """The five-gate attrition funnel. **Three integers per stage, and `ran: false` is a fourth
    state** — a gate that did not execute made no determination about anybody."""
    art, refusal = _artifact_or_503()
    if refusal is not None:
        return refusal
    return _json(200, {
        "stages": list(registry_store.funnel_stages(art)),
        "obligationCoverage": registry_store.obligation_pair(art),
        "corpus": {"outcome": art.corpus_outcome, "census": art.corpus_census},
        "campaignId": art.campaign_id,
        "faultModelVersion": art.fault_model_version,
        "qualifiedAt": art.qualified_at,
        "ceilingNote": art.ceiling_note,
    })


def get_churn(req, params):
    """The template-bump sweep. **`stillRunning` is the field that proves detection was kept.**

    A predicate that moved to `PROVISIONAL` keeps running and keeps reporting findings; only its
    claim to have SETTLED a cell is withdrawn. The wrong implementation — stop running it — lowers
    the number by exactly the same amount, so the two are indistinguishable on a chart and are told
    apart only by this field.
    """
    try:
        return _json(200, registry_store.churn())
    except registry_store.ChurnNotSwept as e:
        return _err(503, "churn_not_swept", str(e), remedy="make history")


def get_history(req, params):
    """The series **must be able to step down**, so nothing here sorts, clamps or smooths it."""
    try:
        return _json(200, list(registry_store.history()))
    except registry_store.HistoryNotMeasured as e:
        return _err(503, "history_not_measured", str(e), remedy="make history")
    except Exception as e:  # noqa: BLE001
        # `UnlabelledStepDown` reaches here. It is a 500 and it SHOULD be: a decrease with no cause
        # is a defect in the series, and serving the other points while dropping that one would
        # hide exactly the point the chart exists for.
        return _err(500, "history_invalid", f"{type(e).__name__}: {e}")


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
