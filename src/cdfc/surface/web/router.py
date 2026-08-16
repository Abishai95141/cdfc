"""Path → screen. **A table, walked in order, with one templated segment.**

The same shape as `cdfc.api.routes`, and for the same reason: a route table that a test can walk is
a route table where a screen added without a test is a visible diff. There is no regex and no
ordering surprise — exact matches first, then one templated segment at a time.

`render_path` returns `(status, html)`. The status is the SCREEN's, not the API's: a screen whose
data endpoint refused with 503 still renders at 200, because the page itself was found and it says
what refused and how to fix it. A 404 here means no screen claims this path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Final

from cdfc.surface.markup import esc
from cdfc.surface.web import screens
from cdfc.surface.web.shell import page


@dataclass(frozen=True, slots=True)
class Screen:
    path: str
    render: Callable[[dict[str, str], dict[str, str]], str]
    title: str
    # The screens that accept a submission. Each renders the OUTCOME as a page rather than letting
    # the browser land on raw JSON — which is what a form posting straight to `/v1` does with
    # scripting off, and is a working API beside a broken product.
    post: Callable[[dict[str, str], dict[str, Any]], str] | None = None


SCREENS: Final[tuple[Screen, ...]] = (
    Screen("/", screens.drop_screen, "S-1 drop", screens.drop_post),
    Screen("/portfolio", screens.portfolio_screen, "S-5 portfolio"),
    Screen("/predicates", screens.predicates_screen, "S-6 predicate library"),
    Screen("/rejections", screens.rejections_screen, "S-7 rejected candidates"),
    Screen("/funnel", screens.funnel_screen, "S-8 attrition funnel"),
    Screen("/history", screens.history_screen, "S-9 settled over time"),
    Screen("/churn", screens.churn_screen, "template churn"),
    Screen("/templates", screens.templates_screen, "S-10 template admission",
           screens.templates_post),
    Screen("/verify", screens.verify_screen, "S-11 verify", screens.verify_post),
    Screen("/open-items", screens.open_items_screen, "S-12 open items"),
    Screen("/runs/{id}", screens.run_screen, "S-2 run report"),
    Screen("/runs/{id}/unchecked", screens.unchecked_screen, "S-3 unchecked panel"),
    Screen("/runs/{id}/cells", screens.cells_screen, "S-4 cell explorer"),
)

NOT_FOUND: Final[int] = 404


def _match(path: str) -> tuple[Screen, dict[str, str]] | None:
    for s in SCREENS:
        if s.path == path:
            return s, {}
    want = [p for p in path.strip("/").split("/") if p != ""]
    for s in SCREENS:
        have = [p for p in s.path.strip("/").split("/") if p != ""]
        if len(have) != len(want) or not have:
            continue
        if all(h == w or (h.startswith("{") and h.endswith("}")) for h, w in zip(have, want)):
            return s, {h[1:-1]: w for h, w in zip(have, want)
                       if h.startswith("{") and h.endswith("}")}
    return None


def render_path(path: str, query: dict[str, str] | None = None, *, method: str = "GET",
                form: dict[str, Any] | None = None) -> tuple[int, str]:
    """Render one screen. **A failure inside a screen renders as a page, never as a blank.**

    An unhandled exception here would otherwise reach the WSGI layer and produce an empty 500 —
    which on a coverage surface is the worst possible output, because a blank page and a page
    reporting nothing to report are the same thing to a reader.
    """
    hit = _match(path)
    if hit is None:
        return NOT_FOUND, page(
            title="No such screen", active="", heading="No such screen",
            body='<p class="page-lede">No screen claims that path. The rail lists every one.</p>',
        )
    screen, params = hit
    if method == "POST" and screen.post is None:
        from cdfc.surface.web import components as C

        return 405, page(
            title="Not a submission", active="", heading="That screen takes no submission",
            body=C.error_state("405 — this screen is read-only",
                               f"{screen.path} renders what the run recorded. Nothing on it "
                               "changes anything, which is why there is no way to submit it."),
        )
    try:
        if method == "POST":
            return 200, screen.post(params, dict(form or {}))  # type: ignore[misc]
        return 200, screen.render(params, dict(query or {}))
    except Exception as e:  # noqa: BLE001 — see the docstring; a blank page is the worst output
        from cdfc.surface.web import components as C

        return 500, page(
            title="This screen failed", active="", heading="This screen failed to render",
            body=C.error_state(
                f"{type(e).__name__} while rendering {screen.title}",
                str(e) or "no detail was raised",
            ) + '<p class="note">This is a defect in the screen, not a finding about a filing. '
                "Nothing here should be read as a coverage result.</p>",
        )


def screen_titles() -> dict[str, str]:
    return {s.path: s.title for s in SCREENS}


def nav_html_for(path: str) -> str:  # pragma: no cover — convenience for tests
    return esc(path)


def all_paths(sample_run: str = "RUN") -> list[str]:
    """Every screen path, with the template filled. Used by the coverage test over the rail."""
    return [s.path.replace("{id}", sample_run) for s in SCREENS]


def data_endpoints() -> dict[str, Any]:  # pragma: no cover — documentation helper
    return {s.path: s.title for s in SCREENS}
