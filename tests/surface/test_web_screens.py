"""The twelve screens. **Every rule asserted over the RENDERED BYTES, not over a docstring.**

`docs/FRONTEND-SCOPE.md` §0 fixes five rules and says a screen that violates one must not ship.
Each is checked here against the actual HTML the server would send, because the failure mode this
project keeps finding is a check defeated by prose describing the thing it checks for.

The one that needed a decision rather than a test is the CSP, and it is the first section below.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest

from cdfc.api.serve import application, csp_for
from cdfc.surface.web import components as C
from cdfc.surface.web.router import SCREENS, render_path

RUNS = Path("reports/runs")
_RUN_IDS = sorted(d.name for d in RUNS.iterdir() if (d / "manifest.json").is_file()) \
    if RUNS.is_dir() else []
_HAVE = bool(_RUN_IDS)


def test_web__the_run_exists_when_the_pipeline_requires_one() -> None:
    import os

    if os.environ.get("CDFC_REQUIRE_RUN") and not _HAVE:
        raise AssertionError(
            "CDFC_REQUIRE_RUN=1 and reports/runs is empty; every screen test would have skipped."
        )


def _wsgi(path: str, query: str = "") -> tuple[str, bytes, dict[str, str]]:
    env = {"REQUEST_METHOD": "GET", "PATH_INFO": path, "QUERY_STRING": query,
           "wsgi.input": io.BytesIO(b""), "CONTENT_LENGTH": "0"}
    cap: dict = {}

    def start(status: str, headers: list) -> None:
        cap["status"], cap["headers"] = status, dict(headers)

    body = b"".join(application(env, start))
    return cap["status"], body, cap["headers"]


def _paths() -> list[str]:
    rid = _RUN_IDS[0] if _RUN_IDS else "none"
    return [s.path.replace("{id}", rid) for s in SCREENS]


# ============================ THE CSP, WHICH IS A DECISION ====================================


def test_web__the_artifact_routes_forbid_script_entirely() -> None:
    """**No `script-src` directive at all** on `/v1`, so the browser refuses any script.

    This is the guarantee that used to be global. It is now asserted where it is claimed, and the
    claim is about the ATTESTED artifact: `report.html`'s digest is what a third party verifies,
    and executable code inside it would be executable code inside the one file that has to be
    trustworthy.
    """
    for path in ("/v1/healthz", "/v1/nope", "/v1/portfolio"):
        _s, _b, headers = _wsgi(path)
        csp = headers["Content-Security-Policy"]
        assert "default-src 'none'" in csp, path
        assert "script-src" not in csp, f"{path}: a script-src directive would PERMIT scripts"
        assert headers["X-Content-Type-Options"] == "nosniff"


@pytest.mark.skipif(not _HAVE, reason="no run on disk")
def test_web__the_report_route_forbids_script_in_the_header_AND_in_the_bytes() -> None:
    """**Stronger than the blanket header ever was.**

    A header applied to every response says nothing about what is IN any of them. This checks both:
    the policy on the wire, and that the served file contains no `<script` at all.
    """
    rid = _RUN_IDS[0]
    status, body, headers = _wsgi(f"/v1/runs/{rid}/report.html")
    if not status.startswith("200"):
        pytest.skip("no report.html for this run")
    assert "script-src" not in headers["Content-Security-Policy"]
    assert b"<script" not in body.lower(), "a script reached the attested artifact"
    assert b"http://" not in body.lower() and b"https://" not in body.lower().replace(
        b"https://schemas.openxmlformats.org", b""
    ), "the report must have no external reference"


def test_web__the_app_routes_permit_only_a_same_origin_script() -> None:
    """`script-src 'self'` — and nothing looser. No `unsafe-inline`, no `unsafe-eval`, no host.

    `unsafe-inline` is the one that matters: without it an injected `onclick=` cannot run even if
    one reached the DOM, which is why `script.py` attaches every handler with `addEventListener`.
    """
    for path in ("/", "/portfolio", "/rejections", "/static/app.js"):
        _s, _b, headers = _wsgi(path)
        csp = headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp, path
        assert "unsafe-inline" not in csp.split("style-src")[0], f"{path}: script may be inline"
        assert "unsafe-eval" not in csp, path
        assert "frame-ancestors 'none'" in csp and "base-uri 'none'" in csp, path
        assert "http" not in csp, f"{path}: a host in a CSP directive means a CDN can be added"


def test_web__csp_is_chosen_by_prefix_so_a_new_api_route_cannot_get_the_looser_one() -> None:
    """The split is `/v1/` vs everything else, walked over both route tables rather than sampled."""
    from cdfc.api.routes import ROUTES

    for r in ROUTES:
        assert "script-src" not in csp_for(r.path), r.path
    for s in SCREENS:
        assert "script-src 'self'" in csp_for(s.path), s.path


def test_web__no_inline_event_handler_or_inline_script_in_any_screen() -> None:
    """Belt and braces: the CSP would block them, and they are not emitted either."""
    for path in _paths():
        _s, body, _h = _wsgi(path)
        text = body.decode("utf-8")
        assert "<script>" not in text, path
        assert not re.search(r"\son[a-z]+\s*=", text), f"{path}: inline event handler"
        assert "javascript:" not in text, path


# ============================ THE FIVE RULES ==================================================


def test_web__R1_no_screen_carries_an_affirmative_verdict() -> None:
    """The banned vocabulary, read from `labels`, over every rendered screen."""
    from cdfc.surface.labels import banned_tokens

    for path in _paths():
        _s, body, _h = _wsgi(path)
        low = body.decode("utf-8").lower()
        for tok in banned_tokens():
            assert tok.lower() not in low, f"{path} contains {tok!r}"


def test_web__R2_no_bare_rate_on_any_screen() -> None:
    """Every percentage renders with both integers of its fraction, or does not render.

    Checked as: no `NN.NN%` and no `NN%` anywhere in the served HTML of any screen.
    """
    for path in _paths():
        _s, body, _h = _wsgi(path)
        text = body.decode("utf-8")
        # CSS lives in a separate file, so a percentage here can only be content.
        assert not re.search(r"\d+(\.\d+)?\s*%", text), f"{path}: a bare rate reached the screen"


@pytest.mark.skipif(not _HAVE, reason="no run on disk")
def test_web__R3_a_settled_count_never_travels_without_its_admission_state() -> None:
    """Ancestor distance <= 2, not merely the same page.

    `settled_count()` emits the number and the caveat as ONE element, so no layout can separate
    them. This asserts the emitted structure rather than trusting the function.
    """
    rid = _RUN_IDS[0]
    _s, body, _h = _wsgi(f"/runs/{rid}")
    text = body.decode("utf-8")
    block = re.search(r'<div class="settled-block">(.*?)</div>', text, re.S)
    assert block, "no settled block on the run screen"
    inner = block.group(1)
    assert "hero" in inner and "admission" in inner, "the caveat is not inside the block"
    assert "PRE-GATE" in text


def test_web__R3_the_component_refuses_a_count_with_no_admission_state() -> None:
    with pytest.raises(C.AdmissionStateMissing):
        C.settled_count(1898, 3747, "")
    with pytest.raises(C.AdmissionStateMissing):
        C.settled_count(1898, 3747, "FINE")


def test_web__R4_no_cross_template_aggregate_on_the_portfolio() -> None:
    """No total row, no average row, no portfolio number — and the screen SAYS the figure is not
    computable rather than leaving the absence to be noticed."""
    _s, body, _h = _wsgi("/portfolio")
    text = body.decode("utf-8").lower()
    for banned in ("average", "portfolio health", "overall coverage", "mean coverage"):
        assert banned not in text.replace("a portfolio coverage figure", ""), banned
    assert "not computable" in text


def test_web__R5_the_not_measured_state_carries_no_digit() -> None:
    """`absent != empty != zero`, and the absent rendering contains no digit ANYWHERE."""
    out = C.count(None, absent_reason="never measured")
    assert not any(ch.isdigit() for ch in re.sub(r"<[^>]+>", "", out))
    assert C.count(0) != out, "a measured zero and an unmeasured value must not render alike"
    with pytest.raises(C.UnnamedAbsence):
        C.count(None)
    with pytest.raises(C.UnnamedAbsence):
        C.count(None, absent_reason="0 measurements taken")


# ============================ THE COMPONENTS ==================================================


def test_components__fraction_cannot_be_built_from_a_percentage() -> None:
    """There is no parameter that takes a rate. A caller holding only one has nothing to pass."""
    with pytest.raises(C.BareRate):
        C.fraction(0.5065, 1)          # type: ignore[arg-type]
    with pytest.raises(C.BareRate):
        C.fraction(1898, 3747.0)       # type: ignore[arg-type]


def test_components__the_unit_sits_outside_the_nowrap_span() -> None:
    """At 390px the hero read `1,849 of 3,747 fields NOT ch` because the unit was inside `.fr`,
    which is `white-space: nowrap`. The two integers stay unbreakable; the unit wraps."""
    out = C.fraction(1849, 3747, unit="fields NOT checked")
    assert out.index("</span>") < out.index("fields NOT checked")
    assert 'class="fr-u"' in out


def test_components__an_unknown_reason_code_is_an_error_not_a_label() -> None:
    with pytest.raises(C.UnknownReasonCode):
        C.reason_code("NO_PREDICATE")   # invented; not one of the closed thirty


def test_components__the_band_never_fills() -> None:
    """The two `always` segments are drawn at the floor **even at zero**.

    The first version dropped every zero-count segment, which silently removed
    `NOT_SETTLEABLE_FROM_ARTIFACT` and `RESIDUE` — the two terms whose whole job is to be there —
    and the band then reached its own far edge.
    """
    out = C.bar([("seg-solid", 100, "settled", False),
                 ("seg-hatch", 0, "not settleable", True),
                 ("seg-hatch", 0, "residue", True)], 100)
    assert out.count("<div class=\"seg") == 3
    grows = [int(m) for m in re.findall(r"flex-grow:(\d+)", out)]
    assert grows[1] > 0 and grows[2] > 0, "an always-drawn segment vanished at zero"


def test_components__an_empty_state_may_not_be_an_all_clear() -> None:
    with pytest.raises(C.BannedAffirmation):
        C.empty_state("Nothing wrong", "everything checks out")


# ============================ THE SCREENS THEMSELVES ==========================================


def test_web__every_screen_renders_and_none_is_blank() -> None:
    for path in _paths():
        status, body, headers = _wsgi(path)
        assert status.startswith("200"), f"{path} -> {status}"
        assert headers["Content-Type"].startswith("text/html")
        assert len(body) > 1200, f"{path} rendered {len(body)} bytes; a near-blank coverage screen"
        assert b"</html>" in body


def test_web__an_unknown_path_is_a_404_page_not_a_blank() -> None:
    status, body, _h = _wsgi("/no-such-screen")
    assert status.startswith("404")
    assert b"No such screen" in body


def test_web__a_screen_that_raises_renders_a_page_saying_so() -> None:
    """A blank 500 on a coverage surface is the worst possible output: a blank page and a page
    reporting nothing to report are the same thing to a reader."""
    # The route table binds the FUNCTION at import time, so patching the module attribute does
    # nothing — which is the router behaving correctly, and is why the table itself is replaced.
    from cdfc.surface.web import router as R

    def boom(_p, _q):
        raise RuntimeError("boom")

    real = R.SCREENS
    R.SCREENS = (R.Screen("/portfolio", boom, "S-5 portfolio"),)
    try:
        status, html = render_path("/portfolio")
    finally:
        R.SCREENS = real
    assert status == 500
    assert "RuntimeError" in html and "boom" in html
    assert "should be read as a coverage result" in html


def test_web__the_drop_screen_still_has_exactly_one_control() -> None:
    """A second control would be a way to change what gets checked without changing what the
    report says was checked."""
    _s, body, _h = _wsgi("/")
    text = body.decode("utf-8")
    assert text.count("<input") == 1 and 'type="file"' in text
    assert "<select" not in text
    assert 'type="checkbox"' not in text and 'type="radio"' not in text


def test_web__every_screen_is_reachable_from_the_rail_or_from_a_screen() -> None:
    """No orphan. A screen nobody can navigate to is a screen nobody audits."""
    from cdfc.surface.web.shell import NAV

    rail = {n.href for n in NAV}
    linked = set(rail)
    for path in _paths():
        _s, body, _h = _wsgi(path)
        linked |= set(re.findall(r'href="(/[^"#?]*)"', body.decode("utf-8")))
    rid = _RUN_IDS[0] if _RUN_IDS else "none"
    for s in SCREENS:
        concrete = s.path.replace("{id}", rid)
        assert concrete in linked or s.path in rail, f"{s.path} is unreachable"


@pytest.mark.skipif(not _HAVE, reason="no run on disk")
def test_web__the_unchecked_screen_renders_the_real_breakdown() -> None:
    """**The flagship screen, with the reasons on it.**

    This asserted the screen rendered the *gap* — `groups: null` and the sentence explaining why
    the breakdown could not be derived. That was the honest state and it is no longer the true one:
    the run measures the breakdown, so the screen shows it. What must never appear is an empty
    list, and the summing assertion in `test_api__unchecked_serves_the_breakdown…` is what stops it.
    """
    _s, body, _h = _wsgi(f"/runs/{_RUN_IDS[0]}/unchecked")
    text = body.decode("utf-8")
    assert "1,849" in text
    assert "no_predicate.failed_qualification" in text
    assert "no_predicate.not_yet_synthesised" in text
    # Every group carries a remedy, and the two differ — the panel's own rule, on the page.
    assert "what would make this checkable" in text
    assert "declined to ship" in text          # the failed-qualification remedy
    assert "five gates" in text                # the not-yet-synthesised remedy


def test_web__the_library_says_the_two_populations_are_disjoint() -> None:
    """A library reading `0 admitted` beside a report reading `1,898 settled` invites exactly one
    inference, and it is false."""
    _s, body, _h = _wsgi("/predicates")
    text = body.decode("utf-8")
    assert "different populations" in text
    assert "See every refusal" in text


def test_web__the_funnel_distinguishes_NOT_RUN_from_NOT_APPLICABLE() -> None:
    _s, body, _h = _wsgi("/funnel")
    text = body.decode("utf-8")
    assert "NOT RUN" in text
    assert "made no determination about anybody" in text


def test_web__every_rejection_row_shows_the_number_that_decided_it() -> None:
    _s, body, _h = _wsgi("/rejections", "limit=20")
    text = body.decode("utf-8")
    assert text.count("kr_claimed") >= 10
    assert "cells it covered" in text


def test_web__filters_are_server_side_links_not_client_side_filtering() -> None:
    """A client-side filter over one page of a capped list is how a truncated list gets read as a
    complete one. The script file must contain no filtering of table rows."""
    from cdfc.surface.web.script import app_script

    js = app_script()
    assert "f.submit()" in js, "the filters must submit to the server"
    for forbidden in ("tbody", "tr.style.display", "filter(function(row"):
        assert forbidden not in js, f"the script filters rows on the client: {forbidden}"


def test_web__the_script_computes_no_fraction() -> None:
    """§10.1 — two implementations of the settled fraction is one more than this project can
    defend. Enforced structurally: there is no arithmetic in the file to review."""
    from cdfc.surface.web.script import app_script

    js = app_script()
    for op in ("settled /", "/ total", "* 100", "toFixed(1) + '%'"):
        assert op not in js, f"the script does arithmetic on a coverage number: {op}"


# ============================ THE THREE POST FLOWS, WITHOUT SCRIPTING =========================


_BOUNDARY = b"----cdfcTEST"


def _multipart(name: str, filename: str, data: bytes) -> bytes:
    return (b"--" + _BOUNDARY + b'\r\nContent-Disposition: form-data; name="' + name.encode()
            + b'"; filename="' + filename.encode() + b'"\r\nContent-Type: application/octet-stream'
            + b"\r\n\r\n" + data + b"\r\n--" + _BOUNDARY + b"--\r\n")


def _post(path: str, body: bytes, ctype: str) -> tuple[str, bytes]:
    env = {"REQUEST_METHOD": "POST", "PATH_INFO": path, "QUERY_STRING": "",
           "wsgi.input": io.BytesIO(body), "CONTENT_LENGTH": str(len(body)),
           "CONTENT_TYPE": ctype}
    cap: dict = {}

    def start(status: str, headers: list) -> None:
        cap["status"] = status

    out = b"".join(application(env, start))
    return cap["status"], out


def test_web__the_drop_screen_works_with_scripting_off() -> None:
    """**A form posting straight to `/v1` renders raw JSON in the browser.**

    That is a working API beside a broken product, and it is what every one of these three forms
    did before. Each now posts to its own screen route and the outcome renders as a page.
    """
    ct = "multipart/form-data; boundary=" + _BOUNDARY.decode()
    status, body = _post("/", _multipart("filing", "notes.txt", b"hello"), ct)
    assert status.startswith("200")
    assert b"not an .xlsx" in body
    # The server's own detail, verbatim — the backend's messages carry the argument.
    assert b"does not begin with the zip" in body
    assert b"{" not in body.split(b"<body")[0], "raw JSON reached the reader"


def test_web__a_422_carries_the_structural_fingerprint_and_a_route_to_admission() -> None:
    """A 422 that only says *unknown template* leaves an operator with nothing to act on."""
    blob = Path("fixtures/synthetic/clean__independently-computed__fme-q1.xlsx").read_bytes()
    ct = "multipart/form-data; boundary=" + _BOUNDARY.decode()
    status, body = _post("/", _multipart("filing", "f.xlsx", blob[:200_000]), ct)
    assert status.startswith("200")
    assert b"not been admitted" in body
    assert b"structural fingerprint" in body
    assert b'href="/templates"' in body


def test_web__template_admission_refuses_without_an_operator_token() -> None:
    """An unset secret is not a pass. It is a 503 carrying the variable that fixes it."""
    import os

    saved = os.environ.pop("CDFC_OPERATOR_TOKEN", None)
    try:
        status, body = _post("/templates", b"token=", "application/x-www-form-urlencoded")
    finally:
        if saved is not None:
            os.environ["CDFC_OPERATOR_TOKEN"] = saved
    assert status.startswith("200")
    assert b"operator token is not configured" in body
    assert b"CDFC_OPERATOR_TOKEN" in body


def test_web__verification_reports_a_mismatch_rather_than_a_match_on_the_numbers() -> None:
    status, body = _post("/verify", b"runId=x", "application/x-www-form-urlencoded")
    assert status.startswith("200")
    assert b"do not match" in body or b"bytes match" in body


def test_web__a_read_only_screen_refuses_a_submission() -> None:
    status, body = _post("/portfolio", b"", "application/x-www-form-urlencoded")
    assert status.startswith("405")
    assert b"read-only" in body


def test_web__every_form_posts_to_a_screen_route_not_to_the_api() -> None:
    """Walked over the rendered HTML of every screen, so a new form cannot be added the old way."""
    for path in _paths():
        _s, body, _h = _wsgi(path)
        for action in re.findall(r'<form[^>]*action="([^"]+)"', body.decode("utf-8")):
            assert not action.startswith("/v1/"), (
                f"{path}: a form posts to {action}; with scripting off the reader lands on JSON"
            )


def test_web__the_stylesheet_has_no_colour_outside_the_palette() -> None:
    """Over the GENERATED BYTES. The fastest way to reintroduce an affirmative colour is to add
    it under a name nobody would grep for."""
    from cdfc.surface import design
    from cdfc.surface.web.style import app_stylesheet

    css = app_stylesheet()
    allowed = {v.lower() for v in design.COLOR.values()}
    for hexv in set(re.findall(r"#[0-9a-fA-F]{3,8}", css)):
        assert hexv.lower() in allowed, f"{hexv} is not in design.COLOR"


def test_web__no_colour_in_the_generated_css_falls_in_the_green_hue_band() -> None:
    import colorsys

    from cdfc.surface.web.style import app_stylesheet

    for hexv in set(re.findall(r"#([0-9a-fA-F]{6})", app_stylesheet())):
        r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (0, 2, 4))
        h, ll, s = colorsys.rgb_to_hls(r, g, b)
        assert not (80 <= h * 360 <= 160 and s > 0.15 and 0.2 <= ll <= 0.8), f"#{hexv} is green"


def test_web__the_static_assets_are_generated_and_have_no_filesystem_path() -> None:
    """No static directory, so there is no path to traverse; an unknown name is a 404."""
    status, _b, _h = _wsgi("/static/../../etc/passwd")
    assert status.startswith("404")
    for path in ("/static/app.css", "/static/app.js"):
        status, body, headers = _wsgi(path)
        assert status.startswith("200") and len(body) > 2000
        assert "charset=utf-8" in headers["Content-Type"]
