"""The page skeleton and the navigation. **Every screen is reachable with scripting off.**

The rail is a `<nav>` of ordinary `<a href>`s. There is no client-side router, no history
interception and no hidden state: a screen's URL is the whole of its state, so a link to a filtered
rejection list is a link somebody can paste into a ticket and get the same list back.

## The counts in the rail are real, and they are counts rather than fractions

Each entry may carry a tally. `348` beside *Rejected* and `0` beside *Library* are the two numbers
that describe this product most accurately, so they are on every screen. **No entry carries a
percentage** — R4: counts aggregate, fractions do not, and a rail is the most tempting place in any
application to put a cross-template average.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from cdfc.surface.markup import esc

PRODUCT: Final[str] = "cdfc"
TAGLINE: Final[str] = "coverage declaration for filed compliance"


@dataclass(frozen=True, slots=True)
class NavItem:
    href: str
    label: str
    group: str


NAV: Final[tuple[NavItem, ...]] = (
    NavItem("/", "Check a filing", "start"),
    NavItem("/portfolio", "Filings", "start"),
    NavItem("/templates", "Templates", "start"),
    NavItem("/predicates", "Predicate library", "the checks"),
    NavItem("/rejections", "Rejected candidates", "the checks"),
    NavItem("/funnel", "Attrition funnel", "the checks"),
    NavItem("/history", "Settled over time", "the checks"),
    NavItem("/churn", "Template churn", "the checks"),
    NavItem("/verify", "Verify a report", "evidence"),
    NavItem("/open-items", "Open items", "evidence"),
)

GROUP_ORDER: Final[tuple[str, ...]] = ("start", "the checks", "evidence")


def _nav(active: str, tallies: dict[str, Any]) -> str:
    out: list[str] = []
    for group in GROUP_ORDER:
        out.append(f'<p class="rail-group">{esc(group)}</p>')
        for item in NAV:
            if item.group != group:
                continue
            cur = ' aria-current="page"' if item.href == active else ""
            t = tallies.get(item.href)
            tally = (f'<span class="tally">{esc(t)}</span>') if t is not None else ""
            out.append(f'<a href="{esc(item.href)}"{cur}>'
                       f"<span>{esc(item.label)}</span>{tally}</a>")
    return "".join(out)


def page(
    *,
    title: str,
    active: str,
    body: str,
    tallies: dict[str, Any] | None = None,
    heading: str = "",
    lede: str = "",
    crumb: str = "",
) -> str:
    """One page. **The stylesheet and the script are same-origin files, not inline blobs.**

    `report.html` inlines its CSS because it must survive being emailed as one file. The app is
    served, so it links instead — which is what lets the app CSP forbid `'unsafe-inline'` for
    scripts while the report keeps a policy with no `script-src` at all.
    """
    head = ""
    if heading:
        head += f'<h1 class="page">{esc(heading)}</h1>'
    if lede:
        head += f'<p class="page-lede">{esc(lede)}</p>'
    crumbs = f'<p class="crumb">{crumb}</p>' if crumb else ""
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)} · {esc(PRODUCT)}</title>"
        '<link rel="stylesheet" href="/static/app.css">'
        '<link rel="icon" href="data:,">'
        "</head><body>"
        '<a class="skip" href="#main">Skip to content</a>'
        '<div class="app">'
        '<aside class="rail">'
        f'<p class="brand">{esc(PRODUCT)}</p>'
        f'<p class="brand-sub">{esc(TAGLINE)}</p>'
        f"<nav>{_nav(active, tallies or {})}</nav>"
        '<p class="rail-foot">This states what was checked and what was not. '
        "It does not state that a filing is correct.</p>"
        "</aside>"
        '<div class="main"><main id="main" class="wrap"><div class="wash" aria-hidden="true"></div>'
        f"{crumbs}{head}{body}"
        "</main></div></div>"
        '<script src="/static/app.js" defer></script>'
        "</body></html>"
    )
