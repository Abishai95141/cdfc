"""The twelve screens. **Each one renders what `/v1` returns and computes nothing.**

Every screen fetches through `cdfc.api.app.dispatch` — the same pure `Request -> Response` a client
calls over HTTP, invoked in-process. That is deliberate and it is the enforcement of
`docs/FRONTEND-SCOPE.md` §10.1: a screen cannot compute a settled fraction of its own, because it
never sees the run — it sees the response, and the response carries the six counts the run
recorded.

It also means the screen and the API cannot disagree. A second data path would be a second answer
to *how much of this filing was checked*, and this product has room for exactly one.

## Refusals render as refusals

Six endpoints can return `503` with a remedy — the qualification artifact is not measured, the
history has not been produced. Those screens render the server's `detail` **verbatim** and the
command that fixes it. None of them renders an empty table: an empty predicate library says the
gates admitted nobody, and a 503 says nobody ran them.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote, urlencode

from cdfc.api.app import Request, dispatch
from cdfc.surface.markup import esc
from cdfc.surface.web import components as C
from cdfc.surface.web.shell import page

# The closure terms, in the order the band draws them. The last two are hatched and are why the
# band can never fill: `NOT_SETTLEABLE_FROM_ARTIFACT` and `RESIDUE` are always drawn.
BAND_TERMS: tuple[tuple[str, str, str], ...] = (
    ("settled", "seg-solid", "settled — a check ran and did not fire"),
    ("failed", "seg-solid k-SETTLED_FAIL", "settled — a check ran and fired"),
    ("indeterminate", "seg-solid k-NO_PREDICATE", "not settled — could not decide"),
    ("notRun", "seg-solid k-NO_PREDICATE", "not settled — did not run"),
    ("noPredicate", "seg-hatch", "NOT CHECKED — no predicate exists for these cells"),
    ("error", "seg-solid k-SETTLED_FAIL", "not settled — errored"),
)


def _get(path: str, **query: Any) -> tuple[int, Any]:
    q = {k: str(v) for k, v in query.items() if v not in (None, "")}
    r = dispatch(Request("GET", path, query=q))
    return r.status, r.json()


def _refusal(body: dict[str, Any], what: str) -> str:
    return C.error_state(
        f"{what} has not been measured",
        str(body.get("detail") or body.get("error") or "no detail was returned"),
        remedy=str(body.get("remedy") or ""),
    )


def _tallies() -> dict[str, Any]:
    """The rail's counts. **Counts only — a rail is the most tempting place to put an average.**"""
    out: dict[str, Any] = {}
    s, b = _get("/v1/portfolio")
    if s == 200:
        out["/portfolio"] = len(b.get("rows", []))
    s, b = _get("/v1/rejections", limit=1)
    if s == 200:
        out["/rejections"] = b.get("totalUnfiltered")
    s, b = _get("/v1/predicates")
    if s == 200:
        out["/predicates"] = b.get("admittedCount")
    return out


def _link(href: str, text: str, *, cls: str = "") -> str:
    c = f' class="{esc(cls)}"' if cls else ""
    return f'<a href="{esc(href)}"{c}>{esc(text)}</a>'


def _digest(value: str, *, chars: int = 16) -> str:
    if not value:
        return C.count(None, absent_reason="not recorded")
    short = value[:chars]
    return (f'<code data-copy="{esc(value)}">{esc(short)}…</code> '
            f'<button type="button" class="btn btn-quiet" data-copy-btn>copy</button>')


# ============================== S-1 · DROP =====================================================


def drop_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    """**One control.** Every setting here would change what gets checked without changing what
    the report says was checked, and the Unchecked panel would be defeated from outside itself."""
    from cdfc.surface.drop import ACCEPT, CONTROL_LABEL, LEDE, NOTE, SUBMIT

    body = f"""<div class="drop">
  <p class="page-lede">{esc(LEDE)}</p>
  <form class="drop-form" method="post" action="/" enctype="multipart/form-data">
    <label class="drop-target" for="filing">
      <span class="drop-word">{esc(CONTROL_LABEL)}</span>
      <span class="note">drag it here, or choose a file</span>
      <input id="filing" name="filing" type="file" accept="{esc(ACCEPT)}" required>
      <span class="drop-chosen figure"></span>
    </label>
    <progress id="drop-progress" hidden></progress>
    <div class="actions">
      <button type="submit" class="btn btn-primary">
        <span class="idle">{esc(SUBMIT)}</span>
        <span class="pending"><span class="spinner"></span>checking</span>
      </button>
    </div>
  </form>
  <div id="drop-result" aria-live="polite"></div>
  <p class="note">{esc(NOTE)}</p>
</div>"""
    return page(title="Check a filing", active="/", heading="Check a filing", body=body,
                tallies=_tallies())


def _post(path: str, body: bytes = b"", *, content_type: str = "application/octet-stream",
          token: str = "") -> tuple[int, Any]:
    headers = {"content-type": content_type}
    if token:
        headers["authorization"] = f"Bearer {token}"
    r = dispatch(Request("POST", path, headers=headers, body=body))
    return r.status, r.json()


# The four refusal states from `docs/FRONTEND-SCOPE.md` §2, rendered as PAGES. With scripting on,
# `script.py` renders the same four inline without a navigation; with it off, these are what a
# reader gets instead of raw JSON.
_UPLOAD_TITLES: dict[int, str] = {
    413: "That file is over the 25 MB cap",
    415: "That file is not an .xlsx",
    422: "This template has not been admitted",
    503: "The server refused rather than guessing",
}


def drop_post(_params: dict[str, str], form: dict[str, Any]) -> str:
    """`POST /` — the drop screen without scripting. **Renders the refusal, never raw JSON.**"""
    filing = form.get("filing")
    if not isinstance(filing, tuple) or not filing[1]:
        return page(
            title="Check a filing", active="/", heading="Check a filing",
            body=C.error_state("No file was submitted",
                               "The form carries exactly one control and it is required."),
            tallies=_tallies(),
        )
    name, blob = filing
    status, body = _post("/v1/filings", blob,
                         content_type="application/vnd.openxmlformats-officedocument."
                                      "spreadsheetml.sheet")
    if status == 201 and body.get("runId"):
        return run_screen({"id": str(body["runId"])}, {})

    extra = ""
    if status == 413:
        extra = (f'<p class="err-remedy"><span class="meta">this file is</span> '
                 f'<span class="figure">{len(blob):,}</span> bytes</p>')
    if body.get("structuralFingerprint"):
        # A 422 that only says "unknown template" leaves an operator with nothing to act on. The
        # fingerprint is what they paste into template admission, so the refusal carries its remedy.
        extra += (
            f'<p class="err-remedy"><span class="meta">structural fingerprint</span> '
            f'<code data-copy="{esc(body["structuralFingerprint"])}">'
            f'{esc(body["structuralFingerprint"])}</code> '
            f'<button type="button" class="btn btn-quiet" data-copy-btn>copy</button></p>'
            f'<p class="err-remedy">{_link("/templates", "Begin admission", cls="btn btn-quiet")}</p>'
        )
    title = _UPLOAD_TITLES.get(status, f"The server refused ({status})")
    return page(
        title="Check a filing", active="/", heading="Check a filing",
        body=f'<p class="page-lede">{esc(name)} was not accepted.</p>'
             + C.error_state(title, str(body.get("detail") or body.get("error") or ""))
             + (f'<div class="err">{extra}</div>' if extra else "")
             + f'<div class="actions">{_link("/", "Try another file", cls="btn btn-primary")}</div>',
        tallies=_tallies(),
    )


def templates_post(_params: dict[str, str], form: dict[str, Any]) -> str:
    """`POST /templates` — admission runs T1–T6 and **stops at T7 awaiting a human signature.**"""
    status, body = _post("/v1/templates", b"{}", content_type="application/json",
                         token=str(form.get("token") or ""))
    if status == 202:
        outcome = C.error_state(
            f"Admission stopped at {body.get('stoppedAt', 'T7')}",
            str(body.get("detail", "")),
        )
    elif status == 503:
        outcome = C.error_state("The operator token is not configured on this server",
                                str(body.get("detail", "")),
                                remedy="export CDFC_OPERATOR_TOKEN=…")
    else:
        outcome = C.error_state(f"The server refused ({status})",
                                str(body.get("detail") or body.get("error") or ""))
    return page(title="Templates", active="/templates", heading="Template admission",
                body=outcome + f'<div class="actions">'
                               f'{_link("/templates", "Back to templates", cls="btn")}</div>',
                tallies=_tallies())


def verify_post(_params: dict[str, str], form: dict[str, Any]) -> str:
    """`POST /verify` — re-derive and compare. **The comparison is over BYTES.**"""
    status, body = _post("/v1/verify", b"{}", content_type="application/json")
    reproduced = bool(body.get("reproduced"))
    diff = body.get("diff") or []
    if status == 200 and reproduced:
        outcome = C.error_state(
            "The bytes match",
            "The statement re-derived from the run on disk is byte-for-byte the published file. "
            "That says the document was not altered. It says nothing about whether the filing is "
            "correct — that is what the coverage declaration is for.",
        )
    else:
        outcome = C.error_state(
            "The bytes do not match, or there is nothing to compare against",
            "; ".join(str(d) for d in diff) or str(body.get("detail", "")),
            remedy="cdfc verify <run-id> --against <published.html>",
        )
    supplied = form.get("report")
    if isinstance(supplied, tuple) and supplied[1]:
        outcome += C.error_state(
            "The uploaded file was not compared",
            f"{supplied[0]} ({len(supplied[1]):,} bytes) reached the server. `POST /v1/verify` "
            "re-derives from a run id and does not yet accept an uploaded document, so it was "
            "read and discarded rather than silently treated as the subject of the comparison.",
        )
    return page(title="Verify a report", active="/verify", heading="Verification result",
                body=outcome + f'<div class="actions">'
                               f'{_link("/verify", "Verify another", cls="btn")}</div>',
                tallies=_tallies())


# ============================== S-2 · RUN REPORT ===============================================


def run_screen(params: dict[str, str], _query: dict[str, str]) -> str:
    rid = params["id"]
    status, run = _get(f"/v1/runs/{quote(rid)}")
    if status != 200:
        return page(title="No such run", active="/portfolio", heading="No such run",
                    body=C.error_state("That run is not on disk", str(run.get("detail", ""))),
                    tallies=_tallies())

    f = run["settledFraction"]
    unchecked_status, unchecked = _get(f"/v1/runs/{quote(rid)}/unchecked")

    # THE HERO. Two lines, ONE type token, one ink. The moment one is larger or more coloured than
    # the other the reader has been told which matters -- and the one they would be told to ignore
    # is the count of fields nobody checked.
    hero = C.settled_count(f["settled"], f["inScope"], f["admissionState"], label="cells settled")
    not_checked = (
        '<div class="settled-block">'
        f'<p class="hero">{C.fraction(f["notChecked"], f["inScope"], unit="fields NOT checked")}</p>'
        '<p class="admission">No predicate exists for these cells. They were not examined and '
        "found acceptable; they were not examined.</p></div>"
    )

    closure_status, closure = _get(f"/v1/runs/{quote(rid)}/cells", limit=1)
    band = _band(f)

    counts = "".join([
        _stat("settled", C.fraction(f["settled"], f["inScope"]), "a check ran and did not fire"),
        _stat("not checked", C.count(f["notChecked"]), "no predicate exists for the cell"),
        _stat("unsettled", C.count(f["unsettled"]), "ran and could not decide, or errored"),
        _stat("field surface", C.count(f["cellsTotal"]),
              "the unlocked-cell mask under generator rule v3"),
    ])

    actions = f"""<div class="actions">
  {_link(f"/runs/{rid}/unchecked", "What was not checked", cls="btn btn-primary")}
  {_link(f"/runs/{rid}/cells", "Explore every cell", cls="btn")}
  {_link(f"/v1/runs/{rid}/report.html", "Download the report", cls="btn")}
  {_link(f"/v1/runs/{rid}/attestation.json", "Download the attestation", cls="btn")}
  {_link("/verify", "Verify a published report", cls="btn")}
</div>"""

    gap = ""
    if unchecked_status == 200 and unchecked.get("groups") is None:
        gap = C.error_state(
            "The per-reason breakdown is not in this artifact",
            str(unchecked.get("breakdownUnavailable", "")),
        )

    body = f"""
{hero}{not_checked}
<p class="caveat">{esc(f["denominatorWarning"])}</p>
{actions}
<section><h2>Coverage</h2>{band}</section>
<section><h2>Is the field surface the whole form?</h2>{_exclusions(run.get("surfaceExclusions"))}</section>
<section><h2>The six counts</h2><div class="grid grid-2">{counts}</div></section>
<section><h2>What was not checked</h2>{gap}
  <p class="page-lede">{esc(str(unchecked.get("total", 0)))} cells carry no predicate.
  {esc("The panel is the product; it is not an appendix.")}</p>
  {_link(f"/runs/{rid}/unchecked", "Open the panel", cls="btn btn-primary")}
</section>
<section><h2>Provenance</h2><dl class="kvs">
  {C.kv("run id", f'<code>{esc(run["runId"])}</code>', raw=True)}
  {C.kv("filing sha256", _digest(run["filingSha256"]), raw=True)}
  {C.kv("template sha256", _digest(run["templateSha256"]), raw=True)}
  {C.kv("run state", esc(run["runState"]))}
  {C.kv("cells returned by the closure endpoint",
        C.fraction(closure.get("returned", 0), closure.get("total", 0))
        if closure_status == 200 else C.count(None, absent_reason="the endpoint refused"),
        raw=True)}
</dl></section>
<section><h2>The report file</h2>
  <p class="page-lede">The downloadable report is the artifact the attestation covers, and it is
  served byte-for-byte from disk. This screen is a view of it and is not a substitute for it.</p>
</section>"""
    return page(title=f"Run {rid}", active="/portfolio", heading="Coverage declaration",
                lede="What was checked in this filing, and what was not.",
                crumb=_link("/portfolio", "Filings") + " / " + esc(rid),
                body=body, tallies=_tallies())


def _exclusions(ex: dict[str, Any] | None) -> str:
    """**No, and here is exactly what was removed.**

    The field surface is a number arrived at by taking cells away, and for as long as nothing
    recorded what was taken, a reader had no way to ask the question this section is named for.
    That is the coverage lie this product exists to refuse, aimed at its own denominator.
    """
    if not ex:
        return C.empty_state(
            "The exclusion census is not on this run",
            "It is not rendered as zeros. Zero excluded would say the field surface is the whole "
            "workbook, and that is a claim this run did not make. Re-run the filing to produce it.",
        )
    rows = [
        [f'<span class="figure">{ex["formula"]:,}</span>',
         "formula cells — the template computes them, so they are not fields a filer writes"],
        [f'<span class="figure">{ex["locked"]:,}</span>',
         "locked cells — the protection mask says a filer cannot write them"],
        [f'<span class="figure">{ex["field_surface"]:,}</span>',
         "THE FIELD SURFACE — everything left, and the denominator of every count on this page"],
    ]
    return (
        f'<p class="page-lede">No. The workbook records '
        f'{C.fraction(ex["field_surface"], ex["recorded"], unit="cells as the field surface")}. '
        "The rest were removed before the count began, and this is what they were.</p>"
        + C.table([("cells", "n"), ("why it is not a field", "w")], rows,
                  caption="The three buckets are disjoint and sum to the recorded total. "
                          "`recorded` is cells the WORKBOOK RECORDS: OOXML omits an entry for a "
                          "cell that is empty and unstyled, so this is not the size of the grid.")
    )


def _stat(label: str, value: str, sub: str) -> str:
    return (f'<div class="stat"><dt>{esc(label)}</dt><dd>{value}</dd>'
            f'<p class="sub">{esc(sub)}</p></div>')


def _band(f: dict[str, Any]) -> str:
    """**The band never fills.** The last two segments are drawn at a floor even at zero.

    Each legend swatch carries its segment's own class, so the key matches the band. A legend of
    identical empty squares is a legend that names five things and distinguishes none of them.
    """
    total = f["cellsTotal"] or 1
    segs: list[tuple[str, int, str, bool]] = [
        ("seg-solid", f["settled"], "settled — a check ran", False),
        ("seg-hatch", f["notChecked"], "NOT CHECKED — no predicate exists", False),
        ("seg-solid k-NO_PREDICATE", f["unsettled"],
         "not settled — ran and could not decide, or errored", False),
        ("seg-hatch", 0, "not settleable from this filing", True),
        ("seg-hatch", 0, "residue — demonstrated survivors", True),
    ]
    legend = "".join(
        f'<li><span class="swatch {esc(cls)}"></span><span>{esc(t)}</span> '
        + (C.count(None, absent_reason="never measured") if always
           else f'<span class="figure">{n:,}</span>')
        + "</li>"
        for cls, n, t, always in segs
    )
    return (C.bar(segs, total)
            + f'<ul class="legend">{legend}</ul>'
            + '<p class="note">The last two terms are drawn at a floor and never vanish, and they '
              "carry no digit because neither has been measured. A band that reaches the far edge "
              "would be a bug: it would say the field surface is fully accounted for.</p>")


# ============================== S-3 · UNCHECKED ================================================


def unchecked_screen(params: dict[str, str], _query: dict[str, str]) -> str:
    """**This is the product.** The only screen here that says what the tool did not do."""
    rid = params["id"]
    status, body = _get(f"/v1/runs/{quote(rid)}/unchecked")
    if status != 200:
        return page(title="Unchecked", active="/portfolio", heading="What was not checked",
                    body=C.error_state("Could not read the run", str(body.get("detail", ""))),
                    tallies=_tallies())

    total = body["total"]
    groups = body.get("groups")
    if groups is None:
        # `groups: null` is NOT an empty list. `[]` would read as *every unchecked cell is
        # accounted for and none has a reason*, which is false.
        inner = C.error_state(
            "The per-reason breakdown is not derivable from this run's artifact",
            str(body.get("breakdownUnavailable", "")),
            remedy="persist the unevaluated cells with their reasons in evaluate/run.write",
        )
    elif not groups:
        inner = C.empty_state(
            "Every cell in the field surface carries a predicate",
            "That is a statement about coverage and not about correctness: a predicate ran over "
            "each cell, and whether each predicate is right is a separate question the "
            "qualification gates answer.",
        )
    else:
        rows = [
            [C.reason_code(g["reasonCode"]),
             f'<span class="figure">{g["count"]:,}</span>',
             f'<span class="w">{esc(g["remedy"])}</span>']
            for g in groups
        ]
        inner = C.table([("reason", ""), ("cells", "n"), ("what would make this checkable", "w")],
                        rows, caption="Grouped by reason code, from the closed thirty.")

    residue = f"""<section><h2>Residue — demonstrated survivors</h2>
{C.empty_state(
    "The residue procedure has not been run against this predicate set",
    "This renders no digit on purpose. A residue that has not been measured and a residue "
    "measured at zero are different facts, and a zero here would be the weaker news of the two: "
    "it would mean either the check set is complete or the fault model is too narrow to "
    "construct a survivor, and the second is more likely.",
)}</section>"""

    hero = (
        '<div class="settled-block">'
        f'<p class="hero">{C.count(total)} <span class="fr-sep">cells were not checked</span></p>'
        '<p class="admission">They were not examined and found acceptable. They were not '
        "examined.</p></div>"
    )
    return page(
        title="What was not checked", active="/portfolio",
        heading="What was not checked",
        lede="The panel this product exists for. It is not an appendix and it does not live "
             "behind a tab.",
        crumb=_link("/portfolio", "Filings") + " / " + _link(f"/runs/{rid}", rid) + " / unchecked",
        body=hero + f"<section><h2>By reason</h2>{inner}</section>" + residue,
        tallies=_tallies(),
    )


# ============================== S-4 · CELLS ====================================================


def cells_screen(params: dict[str, str], query: dict[str, str]) -> str:
    rid = params["id"]
    status, body = _get(f"/v1/runs/{quote(rid)}/cells",
                        state=query.get("state"), reason=query.get("reason"),
                        limit=query.get("limit", 200))
    if status != 200:
        return page(title="Cells", active="/portfolio", heading="Cell explorer",
                    body=C.error_state("Could not read the run", str(body.get("detail", ""))),
                    tallies=_tallies())

    states = sorted({str(c.get("state", "")) for c in body["cells"] if c.get("state")})
    filters = _filter_form(f"/runs/{rid}/cells", [
        ("state", "state", states, query.get("state", "")),
    ], search=("reason", query.get("reason", ""), "reason code contains"))

    rows = [
        [f'<code>{esc(c.get("stable_key", ""))}</code>',
         f'<code>{esc(c.get("predicate_id") or "")}</code>',
         esc(str(c.get("state", ""))),
         ("yes" if c.get("settles") else "no"),
         (C.reason_code(c["reason"]) if c.get("reason") else
          C.count(None, absent_reason="no reason recorded — the check settled")),
         f'<span class="trunc">{esc(", ".join(map(str, c.get("witness") or [])))}</span>']
        for c in body["cells"]
    ]
    table = C.table(
        [("cell", "m"), ("predicate", "m"), ("state", "m"), ("settles", "m"),
         ("reason", ""), ("witness", "w")],
        rows,
        caption=f"Showing {body['returned']:,} of {body['total']:,} evaluated cells. "
                "The cap is visible so a short list cannot be read as a complete one.",
    ) if rows else C.empty_state(
        "No evaluated cell matches this filter",
        "That is a statement about the filter, not about the filing. Clear it to see the "
        f"{body['total']:,} evaluations this run recorded.",
        action=_link(f"/runs/{rid}/cells", "Clear the filter", cls="btn"),
    )

    cap = ""
    if body["returned"] < body["total"]:
        cap = C.error_state(
            "This list is capped",
            f"{body['returned']:,} of {body['total']:,} rows are shown. A truncated list that "
            "looks complete is how a coverage number gets read off a screen that showed a tenth "
            "of it.",
            remedy=f"/runs/{rid}/cells?limit=500",
        )

    return page(
        title="Cell explorer", active="/portfolio", heading="Cell explorer",
        lede="Every cell this run evaluated, with the predicate that decided it and the witness "
             "it recorded.",
        crumb=_link("/portfolio", "Filings") + " / " + _link(f"/runs/{rid}", rid) + " / cells",
        body=filters + cap + table, tallies=_tallies(),
    )


def _filter_form(action: str, selects: list[tuple[str, str, list[str], str]], *,
                 search: tuple[str, str, str] | None = None) -> str:
    fields = []
    for name, label, options, current in selects:
        opts = '<option value="">any</option>' + "".join(
            f'<option value="{esc(o)}"{" selected" if o == current else ""}>{esc(o)}</option>'
            for o in options
        )
        fields.append(f'<div class="field"><label for="f-{esc(name)}">{esc(label)}</label>'
                      f'<select id="f-{esc(name)}" name="{esc(name)}">{opts}</select></div>')
    if search:
        name, current, label = search
        fields.append(
            f'<div class="field"><label for="f-{esc(name)}">{esc(label)}</label>'
            f'<input id="f-{esc(name)}" type="search" name="{esc(name)}" '
            f'value="{esc(current)}" placeholder="type to filter"></div>'
        )
    fields.append('<div class="field"><button type="submit" class="btn">Apply</button></div>')
    fields.append(f'<div class="field">{_link(action, "Clear", cls="btn btn-quiet")}</div>')
    return (f'<form class="filters" method="get" action="{esc(action)}">'
            + "".join(fields) + "</form>")


# ============================== S-5 · PORTFOLIO ================================================


def portfolio_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    """**The sharpest rule in the product: no total row, no average, no portfolio number.**"""
    status, body = _get("/v1/portfolio")
    if status != 200:
        return page(title="Filings", active="/portfolio", heading="Filings",
                    body=C.error_state("Could not list runs", str(body.get("detail", ""))),
                    tallies=_tallies())
    rows_data = body["rows"]
    if not rows_data:
        return page(
            title="Filings", active="/portfolio", heading="Filings",
            body=C.empty_state(
                "No filing has been checked yet",
                "This is an empty list of runs. It is not a statement about any filing.",
                action=_link("/", "Check one", cls="btn btn-primary"),
            ),
            tallies=_tallies(),
        )

    rows = [
        [_link(f"/runs/{r['runId']}", r["runId"], cls="mono"),
         f'<code>{esc(r["entity"])}</code>',
         f'<code>{esc(r["template"])}</code>',
         f'<span class="figure">{r["settled"]:,}</span>',
         f'<span class="figure">{r["fieldSurface"]:,}</span>',
         f'<span class="figure">{r["notChecked"]:,}</span>',
         C.admission_badge(r["admissionState"])]
        for r in rows_data
    ]
    table = C.table(
        [("run", "m"), ("entity", "m"), ("template", "m"), ("settled", "n"),
         ("field surface", "n"), ("not checked", "n"), ("admission", "")],
        rows,
        caption="Rows only. Sorting by a settled COUNT is available; sorting by an implied "
                "percentage is not, because that percentage would divide one workbook's mask by "
                "another's.",
    )
    summary = "".join([
        _stat("filings", C.count(len(rows_data)), "a count of filings has a denominator "
              "anybody can state"),
        _stat("distinct templates", C.count(len({r["template"] for r in rows_data})),
              "counts aggregate across templates"),
        _stat("a portfolio coverage figure", C.count(
            None, absent_reason="not computable — the denominators are different workbooks"),
            "R4: a mean over incommensurable denominators is a number with no denominator"),
    ])
    return page(
        title="Filings", active="/portfolio", heading="Filings",
        lede="Every filing checked here, one row each.",
        body=f'<div class="grid grid-3">{summary}</div>'
             f'<section><h2>The table</h2>{table}</section>'
             f'<p class="caveat">{esc(body["note"])}</p>',
        tallies=_tallies(),
    )


# ============================== S-6 · PREDICATE LIBRARY ========================================


def predicates_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    status, body = _get("/v1/predicates")
    if status != 200:
        return page(title="Predicate library", active="/predicates", heading="Predicate library",
                    body=_refusal(body, "The qualification"), tallies=_tallies())

    corpus = body["corpus"]
    header = _corpus_header(corpus)
    label = body.get("instrumentLabel")
    instrument = (C.kv("instrument", esc(label)) if label
                  else C.kv("instrument", C.count(
                      None, absent_reason="no weakening label applies — see the arms below"),
                      raw=True))
    arms = _arms_block(body.get("instrumentArms") or [])

    if body["rows"]:
        rows = [
            [f'<code>{esc(r["predicateId"])}</code>',
             f'<span class="trunc">{esc(r.get("celSource", ""))}</span>',
             esc(str(r.get("krClaimed") or "")),
             esc(str(r.get("krAllClasses") or "")),
             esc(", ".join(r.get("claimsFaultClasses") or [])),
             esc(str(r.get("state", "")))]
            for r in body["rows"]
        ]
        listing = C.table(
            [("predicate", "m"), ("expression", "w"), ("kr claimed", "m"),
             ("kr all classes", "m"), ("claims", ""), ("state", "m")],
            rows,
            caption="Both kill rates render or neither does. The GAP between them is the number a "
                    "reviewer wants: G2's bar is measured over the classes a predicate CLAIMS, and "
                    "the claim is selected after the campaign has run.",
        )
    else:
        listing = C.empty_state(
            "No predicate is admitted through the five gates",
            "This is a measured zero, not a blank. Every one of the harvested candidates was "
            "refused at G2 — and because a refused candidate never acquires a predicate id, none "
            "of them can appear in this list. The rows a reader wants are on the rejected page, "
            "where each carries the number that decided it.",
            action=_link("/rejections", "See every refusal", cls="btn btn-primary"),
        )

    disjoint = C.error_state(
        "The predicates that produced the runs are NOT the predicates in this library",
        str(body["disjointNote"]),
    )
    reg = body["registry"]
    provenance = f"""<section><h2>Provenance</h2><dl class="kvs">
  {C.kv("campaign", esc(body["campaignId"]))}
  {C.kv("fault model", esc(body["faultModelVersion"]))}
  {C.kv("kill bar", esc(body["killBar"]))}
  {C.kv("qualified at", esc(body["qualifiedAt"]))}
  {instrument}
  {C.kv("registry root", _digest(reg["root"]), raw=True)}
  {C.kv("signer", f'<span class="badge">{esc(reg["signer"])}</span>', raw=True)}
  {C.kv("admitted rows", C.count(reg["rows"]), raw=True)}
</dl></section>"""

    return page(
        title="Predicate library", active="/predicates", heading="Predicate library",
        lede="Every check admitted through the five qualification gates, with both of its kill "
             "rates and the corpus that licenses them.",
        body=header + disjoint + f"<section><h2>Admitted</h2>{listing}</section>"
             + arms + provenance + f'<p class="caveat">{esc(body["ceilingNote"])}</p>',
        tallies=_tallies(),
    )


def _arms_block(arms: list[dict[str, Any]]) -> str:
    """**What the instrument cannot see, even when it is green.**

    Every kill rate in this programme rests on *our evaluator reproduces the regulator's own
    values*. `blindTo` is the field that earns this section: arm 1 is satisfied by a workbook whose
    cached values are constant, and arm 2 agrees with us about a formula that is wrong. A screen
    that shows the rates without saying that is showing half a measurement.
    """
    if not arms:
        return ""
    items = "".join(
        f'<details class="disclose"><summary>arm {a["n"]} — {esc(a["name"])} '
        f'<span class="badge">{esc(a["independence"])}</span></summary>'
        f'<dl class="kvs disclose-body">'
        f'{C.kv("oracle", esc(a["oracle"]))}'
        f'{C.kv("who wrote the oracle", esc(a["oracleAuthor"]))}'
        f'{C.kv("what a disagreement means", esc(a["finds"]))}'
        f'{C.kv("blind to, even when green", esc(a["blindTo"]))}'
        f"</dl></details>"
        for a in arms
    )
    return (f"<section><h2>The instrument</h2>"
            f'<p class="page-lede">Independence is COMPUTED from who wrote each oracle, never '
            f"declared. An arm whose oracle shares an author with this evaluator is a self-check "
            f"and renders as one.</p>{items}</section>")


def _corpus_header(corpus: dict[str, Any]) -> str:
    """Three outcomes, rendered DISTINCTLY. **`FAIL` carries no digit anywhere.**"""
    outcome, census = corpus["outcome"], corpus["census"]
    if outcome == "FAIL":
        return C.error_state(
            "G-CORPUS: FAIL",
            "No false-failure rate is licensed and no digit appears on this screen. The corpus "
            "provenance census is below its floor.",
        )
    if outcome == "RESTRICTED":
        return C.error_state(
            "G-CORPUS: RESTRICTED",
            f"n = {census['n']} filings, of which n_non_synthetic = {census['n_non_synthetic']}. "
            "The corpus is TEMPLATE-COMPUTED, so every severity tier is capped at ADVISORY. A "
            "restricted pass rendered as a pass is the failure this gate exists to prevent.",
        )
    return C.error_state(
        "G-CORPUS: PASS",
        f"n = {census['n']} filings, n_non_synthetic = {census['n_non_synthetic']}. Every "
        "predicate class may be admitted and BLOCKING is reachable.",
    )


# ============================== S-7 · REJECTED CANDIDATES ======================================


def rejections_screen(_params: dict[str, str], query: dict[str, str]) -> str:
    """**The one place this product proves its gate is real.**"""
    try:
        offset = max(int(query.get("offset", 0)), 0)
    except ValueError:
        offset = 0
    status, body = _get("/v1/rejections", gate=query.get("gate"), reason=query.get("reason"),
                        q=query.get("q"), offset=offset, limit=50)
    if status != 200:
        return page(title="Rejected candidates", active="/rejections",
                    heading="Rejected candidates",
                    body=_refusal(body, "The qualification"), tallies=_tallies())

    facets = body["facets"]
    filters = _filter_form("/rejections", [
        ("gate", "rejecting gate", sorted(facets["gate"]), query.get("gate", "")),
        ("reason", "reason", sorted(facets["reason"]), query.get("reason", "")),
    ], search=("q", query.get("q", ""), "candidate or class contains"))

    chips = "".join(
        f'<a class="chip" href="/rejections?{urlencode({"reason": k})}" '
        f'aria-pressed="{"true" if query.get("reason") == k else "false"}">'
        f'{esc(k)} <span class="figure">{v:,}</span></a>'
        for k, v in sorted(facets["reason"].items(), key=lambda kv: -kv[1])
    )

    rows = [
        [f'<code>{esc(r["candidateId"])}</code><br>'
         f'<span class="count-label">{esc(r["harvestClass"])}</span>',
         f'<code>{esc(r["gate"])}</code>',
         (C.reason_code(r["reason"]) if _known(r["reason"])
          else f'<code class="reason">{esc(r["reason"])}</code>'),
         f'<span class="figure">{esc(r["headline"])}</span>',
         f'{r["cellsWouldHaveCovered"]:,}',
         esc(r["remedy"] or "—")]
        for r in body["rows"]
    ]
    if rows:
        listing = C.table(
            [("candidate", "m"), ("gate", "m"), ("reason", "m"),
             ("what decided it", "m"), ("cells it covered", "n"), ("remedy", "w")],
            rows,
            caption=f"Showing {body['returned']:,} of {body['total']:,} matching "
                    f"({body['totalUnfiltered']:,} refusals in total). Every row carries the "
                    "number that decided it — a rejection without one is an opinion with a gate's "
                    "name on it.",
        )
    else:
        listing = C.empty_state(
            "No refusal matches this filter",
            f"That is a statement about the filter. {body['totalUnfiltered']:,} candidates were "
            "refused in total.",
            action=_link("/rejections", "Clear the filter", cls="btn"),
        )

    pager = _pager("/rejections", query, offset, body["returned"], body["total"], 50)
    covered = sum(r["cellsWouldHaveCovered"] for r in body["rows"])
    stats = "".join([
        _stat("refusals", C.count(body["totalUnfiltered"]), "candidates a gate turned away"),
        _stat("matching this filter", C.count(body["total"]), "before the page cap"),
        _stat("cells this page would have covered", C.count(covered),
              "each becomes no_predicate.failed_qualification"),
    ])

    return page(
        title="Rejected candidates", active="/rejections", heading="Rejected candidates",
        lede="Every candidate check a gate refused, and the measurement that refused it. This is "
             "the evidence that the gates are not decorative.",
        body=f'<div class="grid grid-3">{stats}</div>'
             f'<section><h2>By reason</h2><div class="chips">{chips}</div>{filters}{listing}'
             f"{pager}</section>",
        tallies=_tallies(),
    )


def _known(code: str) -> bool:
    from cdfc.verdict import ReasonCode

    return code in {str(getattr(r, "value", r)) for r in ReasonCode}


def _pager(path: str, query: dict[str, str], offset: int, returned: int, total: int,
           size: int) -> str:
    if total <= size:
        return ""
    base = {k: v for k, v in query.items() if k != "offset" and v}
    parts = []
    if offset > 0:
        parts.append(_link(f"{path}?{urlencode({**base, 'offset': max(offset - size, 0)})}",
                           "Previous", cls="btn"))
    if offset + returned < total:
        parts.append(_link(f"{path}?{urlencode({**base, 'offset': offset + size})}",
                           "Next", cls="btn btn-primary"))
    where = (f'<span class="note">rows {offset + 1:,}–{offset + returned:,} '
             f'of {total:,}</span>')
    return f'<div class="actions">{"".join(parts)}{where}</div>'


# ============================== S-8 · FUNNEL ===================================================


def funnel_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    status, body = _get("/v1/funnel")
    if status != 200:
        return page(title="Attrition funnel", active="/funnel", heading="Attrition funnel",
                    body=_refusal(body, "The qualification"), tallies=_tallies())

    stages = "".join(_stage(s) for s in body["stages"])
    pair = body["obligationCoverage"]
    if pair["withStatuteObligation"] is None:
        coverage = C.count(None, absent_reason="obligation coverage has not been measured")
    else:
        coverage = (
            f'<p>{C.fraction(pair["withStatuteObligation"], pair["total"], unit="carry a STATUTE obligation")}</p>'
            f'<p>{C.fraction(pair["withTemplateObligation"], pair["total"], unit="carry a TEMPLATE obligation")}</p>'
            f'<p class="note">{esc(pair["note"])}</p>'
        )

    return page(
        title="Attrition funnel", active="/funnel", heading="Attrition funnel",
        lede="Where every harvested candidate died, in gate order. Three integers per stage, and "
             "a gate that did not run says so rather than reporting a stage that passed everyone.",
        body=f"<section><h2>The five gates, in order</h2>{stages}</section>"
             f"<section><h2>Obligation coverage</h2>"
             f'<div class="card">{coverage}</div>'
             '<p class="note">Two numbers, always both. A STATUTE count alone reads as '
             '"nothing is covered"; a TEMPLATE count alone reads as "everything is". Both are '
             "wrong and each is wrong by the other's value.</p></section>"
             + _corpus_header(body["corpus"])
             + f'<p class="caveat">{esc(body["ceilingNote"])}</p>',
        tallies=_tallies(),
    )


def _stage(s: dict[str, Any]) -> str:
    if not s["ran"]:
        return (f'<div class="stage"><div class="stage-head">'
                f'<span class="stage-name">{esc(s["name"])}</span>'
                f'<span class="stage-notrun">NOT RUN — the gate was not executed in this '
                f"campaign, so it made no determination about anybody</span></div></div>")
    if s.get("whollyNotApplicable"):
        return (f'<div class="stage"><div class="stage-head">'
                f'<span class="stage-name">{esc(s["name"])}</span>'
                f'<span class="stage-notrun">NOT APPLICABLE — 0 evaluated</span></div></div>')
    total = s["entered"] or 1
    bar = "".join(
        f'<div class="{cls}" style="flex-grow:{max(n * 1000 // total, 8 if n else 0)}"></div>'
        for cls, n in (("s-survived", s["survived"]), ("s-skipped", s["skipped"]),
                       ("s-rejected", s["rejected"])) if n
    )
    reasons = "".join(
        f'<li>{esc(k)} — <span class="figure">{v:,}</span></li>'
        for k, v in sorted(s.get("reasons", {}).items(), key=lambda kv: -kv[1])
    )
    detail = (f'<details class="disclose"><summary>{s["rejected"]:,} refused here</summary>'
              f'<ul class="disclose-body">{reasons}</ul></details>') if reasons else ""
    return (
        f'<div class="stage"><div class="stage-head">'
        f'<span class="stage-name">{esc(s["name"])}</span>'
        f'<span class="stage-nums">entered {s["entered"]:,} · skipped {s["skipped"]:,} · '
        f'survived {s["survived"]:,} · rejected {s["rejected"]:,}</span></div>'
        f'<div class="stage-bar">{bar}</div>{detail}</div>'
    )


# ============================== S-9 · HISTORY ==================================================


def history_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    status, body = _get("/v1/settled-fraction/history")
    if status != 200:
        return page(title="Settled over time", active="/history", heading="Settled over time",
                    body=_refusal(body, "The series"), tallies=_tallies())
    if len(body) < 2:
        return page(
            title="Settled over time", active="/history", heading="Settled over time",
            body=C.empty_state(
                "The series has fewer than two points",
                "A chart with one point cannot show a change, and a chart that has never fallen "
                "is indistinguishable from one that cannot.",
            ),
            tallies=_tallies(),
        )

    chart = C.sparkline(body)
    rows = [
        [esc(p["at"]),
         C.fraction(p["settled"], p["fieldSurface"]),
         (f'<span class="figure">{p["delta"]:+,}</span>' if p["delta"] is not None
          else C.count(None, absent_reason="first point — no previous value")),
         C.admission_badge(p["admission"]),
         f'<span class="w">{esc(p["cause"] or "—")}</span>']
        for p in body
    ]
    table = C.table(
        [("at", "m"), ("settled", "m"), ("change", "n"), ("admission", ""), ("cause", "w")],
        rows,
        caption="Nothing here sorts, smooths, clamps or takes a running maximum. The absence of "
                "those four operations is the feature.",
    )
    downs = [p for p in body if p["steppedDown"]]
    stats = "".join([
        _stat("points", C.count(len(body)), "in event order, not sorted by value"),
        _stat("step-downs", C.count(len(downs)),
              "the most credible points on this chart"),
        _stat("largest fall",
              C.count(min((p["delta"] for p in downs), default=None),
                      absent_reason="the series has never fallen")
              if downs else C.count(None, absent_reason="the series has never fallen"),
              "cells that stopped being settled"),
    ])
    return page(
        title="Settled over time", active="/history", heading="Settled over time",
        lede="A coverage number that can only rise is a marketing chart. Every decrease here "
             "carries the cause that produced it, and one without a cause does not render.",
        body=f'<div class="grid grid-3">{stats}</div>'
             f'<section><h2>The series</h2><div class="card">{chart}'
             f'<p class="readout" id="chart-readout" aria-live="polite">Hover or focus a point to '
             f"read it.</p></div></section>"
             f"<section><h2>Every point</h2>{table}</section>",
        tallies=_tallies(),
    )


# ============================== CHURN ==========================================================


def churn_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    status, body = _get("/v1/churn")
    if status != 200:
        return page(title="Template churn", active="/churn", heading="Template churn",
                    body=_refusal(body, "The sweep"), tallies=_tallies())

    moved = body["movedToProvisional"]
    rows = [[f'<code>{esc(p)}</code>', f'<span class="w">{esc(body["movedReason"][p])}</span>']
            for p in moved]
    table = C.table([("predicate", ""), ("why it moved", "w")], rows,
                    caption="Each row says which signal moved it. A vocabulary change is a "
                            "demonstrated false-failure risk on a valid filing; a sheet change is "
                            "a conservative 'we cannot rule it out'.") if rows else C.empty_state(
        "This template change moved no predicate",
        "The bump was measured and nothing it touched is read by a predicate that settles cells.",
    )
    stats = "".join([
        _stat("moved to PROVISIONAL", C.count(len(moved)), "they still run; they stop settling"),
        _stat("cells that stopped settling", C.count(abs(body["numeratorDelta"])),
              "removed from the settled numerator"),
        _stat("settled, after", C.fraction(body["newSettled"], body["fieldSurface"]),
              f"was {body['oldSettled']:,}"),
    ])
    detection = C.error_state(
        "Detection was NOT lost",
        f"All {len(moved)} predicates keep running and keep reporting findings. Only their claim "
        "to have SETTLED a cell is withdrawn. The alternative implementation — stop running them "
        "— lowers the number by exactly the same amount and is indistinguishable on a chart.",
    )
    return page(
        title="Template churn", active="/churn", heading="Template churn",
        lede="What happens to coverage when the template moves under it.",
        body=f'<div class="grid grid-3">{stats}</div>'
             + detection
             + f"<section><h2>What moved</h2>{table}</section>"
             + f"""<section><h2>The bump</h2><dl class="kvs">
  {C.kv("swept at", esc(body["sweptAt"]))}
  {C.kv("from template", _digest(body["oldTemplateSha256"]), raw=True)}
  {C.kv("to template", _digest(body["newTemplateSha256"]), raw=True)}
  {C.kv("changed vocabularies",
        esc(", ".join(body["changedVocabularies"]) or "none") )}
  {C.kv("changed sheets", esc(", ".join(body["changedSheets"]) or "none"))}
  {C.kv("granularity", esc(body["granularity"]))}
</dl></section>""",
        tallies=_tallies(),
    )


# ============================== S-10 · TEMPLATES ===============================================


def templates_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    status, body = _get("/v1/templates")
    if status != 200:
        return page(title="Templates", active="/templates", heading="Templates",
                    body=C.error_state("Could not list templates", str(body)), tallies=_tallies())
    rows = [
        [f'<code>{esc(t["name"])}</code>',
         _digest(t["templateSha256"]),
         (C.count(None, absent_reason="no protection mask — no ceiling is derivable")
          if t["settledFractionCeiling"] is None
          else f'<span class="figure">{esc(str(t["settledFractionCeiling"]))}</span>')]
        for t in body
    ]
    table = C.table([("template", "m"), ("sha256", "m"), ("settled-fraction ceiling", "")], rows,
                    caption="A null ceiling is NOT zero. Zero says nothing in this template can "
                            "ever settle; null says the template has no mask, so no ceiling is "
                            "derivable. A client that renders 0 for both tells its reader the "
                            "first thing when the second is true.")
    admission = """<section><h2>Admit a template</h2>
  <form class="filters" method="post" action="/templates">
    <div class="field"><label for="fp">structural fingerprint</label>
      <input id="fp" type="text" name="fingerprint" placeholder="sheet-shape:…"></div>
    <div class="field"><label for="tok">operator token</label>
      <input id="tok" type="text" name="token" placeholder="required"></div>
    <div class="field"><button type="submit" class="btn btn-primary">
      <span class="idle">Begin admission</span>
      <span class="pending"><span class="spinner"></span>running T1–T6</span></button></div>
  </form>"""
    admission += C.error_state(
        "Admission cannot complete here",
        "T1–T6 run automatically. T7 is a human signature and this endpoint cannot supply one, so "
        "admission stops there and the template stays unadmitted until it is countersigned. An "
        "unset operator token refuses with 503 rather than passing — treating an absent secret as "
        "an open door is how a check disappears in production while every test still passes.",
    ) + "</section>"
    return page(title="Templates", active="/templates", heading="Templates",
                lede="The blank forms this product can check a filing against.",
                body=f"<section><h2>Admitted</h2>{table}</section>{admission}",
                tallies=_tallies())


# ============================== S-11 · VERIFY ==================================================


def verify_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    status, body = _get("/v1/registry/roots")
    roots = body if status == 200 else []
    form = """<form class="filters" method="post" action="/verify" enctype="multipart/form-data">
  <div class="field"><label for="v-run">run id</label>
    <input id="v-run" type="text" name="runId" placeholder="f5eb385a8888c55b"></div>
  <div class="field"><label for="v-file">the published report</label>
    <input id="v-file" type="file" name="report" accept=".html,.json"></div>
  <div class="field"><button type="submit" class="btn btn-primary">
    <span class="idle">Re-derive and compare</span>
    <span class="pending"><span class="spinner"></span>re-deriving</span></button></div>
</form>"""
    explain = C.error_state(
        "Verification compares BYTES, not a summary",
        "`cdfc verify` re-derives the statement from the run on disk and compares it byte-for-byte "
        "with the published file. A report that renders the same numbers but differs in one byte "
        "is a report the attestation does not cover, and the comparison says so rather than "
        "reporting a match on the numbers.",
        remedy="cdfc verify <run-id> --against <published.html>",
    )
    root_rows = [
        [_digest(r["root"]), f'<span class="badge">{esc(r["signer"])}</span>',
         f'<span class="figure">{r["rows"]:,}</span>', esc(r["campaignId"]), esc(r["qualifiedAt"])]
        for r in roots
    ]
    table = C.table([("registry root", "m"), ("signer", ""), ("rows", "n"), ("campaign", "m"),
                     ("qualified at", "m")], root_rows,
                    caption="The batch is admitted under the literal signer UNSIGNED. No signer "
                            "exists in this repository, so the batch is visibly weaker rather "
                            "than silently so.") if root_rows else C.empty_state(
        "No registry root has been published",
        "There is no admitted batch to verify a report against yet.",
    )
    return page(title="Verify a report", active="/verify", heading="Verify a published report",
                lede="Check that a report you were given is the one this system produced.",
                body=f"<section><h2>Compare</h2>{form}{explain}</section>"
                     f"<section><h2>Registry roots</h2>{table}</section>",
                tallies=_tallies())


# ============================== S-12 · OPEN ITEMS ==============================================


def open_items_screen(_params: dict[str, str], _query: dict[str, str]) -> str:
    from pathlib import Path

    src = Path("docs/OPEN-ITEMS.md")
    if not src.is_file():
        body = C.empty_state(
            "The open-items register is not on disk",
            "It is a document in the repository, not a computed artifact, and its absence here is "
            "a fact about this deployment rather than about the register.",
        )
    else:
        items = [
            line.strip() for line in src.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith(("- ", "* ", "| D-", "| F"))
        ]
        rows = [[f'<span class="w">{esc(i.lstrip("-* ").strip())}</span>'] for i in items[:300]]
        body = C.table([("item", "w")], rows,
                       caption=f"{len(items):,} entries, read from docs/OPEN-ITEMS.md.") \
            if rows else C.empty_state(
                "The register is on disk and lists nothing",
                "That is a measured empty register, not an absent one.",
            )
    return page(title="Open items", active="/open-items", heading="Open items",
                lede="What this build knows it has not settled. Carried on the report as well as "
                     "here, because an open item that lives only in a repository is an open item "
                     "the reader of a report never sees.",
                body=body, tallies=_tallies())
