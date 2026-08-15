"""P14-B1 — the inliner, and the assertion that the report reaches for nothing.

**The report is one file with no external references.** It opens from `file://` with the network
stack down, it survives being emailed, and — because it is a file — **it has a hash**. A
single-page application does not, and the attested artifact has to be the thing the reader
actually reads.

## Why the assertion is a scan and not a convention

A single `<link rel=stylesheet>` added in a hurry turns the report into a document that renders
differently depending on whether a server answered, and the difference is invisible in the hash. So
`assert_no_external_refs` scans for **every attribute and construct that can fetch**, and raises
naming the offender rather than warning.

The scan is deliberately broader than `src` and `href`, because the ways a page reaches out are
numerous and only some of them look like links: `srcset`, `poster`, `data`, `action`,
`formaction`, `@import`, `url()`, and the fetch primitives inside any inlined script.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

# Attributes whose value is a URL. `data` and `formaction` are here because they are the two people
# forget, and either one is a fetch.
URL_ATTRS: Final[tuple[str, ...]] = (
    "src", "href", "srcset", "poster", "data", "action", "formaction", "background",
    "cite", "longdesc", "manifest", "profile", "usemap",
)

# Anything matching this in an attribute value is remote, whatever the attribute is called.
REMOTE: Final[re.Pattern[str]] = re.compile(r"^\s*(https?:|//|wss?:|ftp:)", re.IGNORECASE)

# Fetch primitives inside inlined script. A report that calls one is a report whose content depends
# on a network reply, and its hash then covers the shell rather than the evidence.
SCRIPT_FETCH: Final[tuple[str, ...]] = (
    "fetch(", "XMLHttpRequest", "WebSocket(", "import(", "importScripts(",
    "navigator.sendBeacon", "EventSource(",
)

CSS_FETCH: Final[tuple[str, ...]] = ("@import", "url(")

ATTR: Final[re.Pattern[str]] = re.compile(
    r"""(?P<name>[a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?P<q>["'])(?P<val>.*?)(?P=q)""", re.DOTALL
)


class ExternalReference(RuntimeError):
    """The report reaches outside itself. **Report generation aborts.**"""


def inline_assets(html: str, *, static_dir: Path) -> str:
    """Replace `{{inline:name}}` markers with the file's contents, wrapped appropriately.

    A marker rather than a `<link>` that is later rewritten: there is no window in which the
    document contains an external reference, so a partially-rendered file cannot leak one.
    """
    def sub(m: re.Match[str]) -> str:
        name = m.group(1)
        path = static_dir / name
        if not path.is_file():
            raise ExternalReference(
                f"the report asks to inline {name!r} and {path} does not exist. It would otherwise "
                "render with the asset silently missing."
            )
        body = path.read_text(encoding="utf-8")
        if name.endswith(".css"):
            return f"<style>\n{body}\n</style>"
        if name.endswith(".js"):
            return f"<script>\n{body}\n</script>"
        raise ExternalReference(f"{name!r}: only .css and .js are inlined")

    return re.sub(r"\{\{inline:([A-Za-z0-9_.-]+)\}\}", sub, html)


def assert_no_external_refs(html: str) -> None:
    """Raise `ExternalReference` naming the offending attribute and its value."""
    offenders: list[str] = []

    for m in ATTR.finditer(html):
        name, val = m.group("name").lower(), m.group("val")
        if REMOTE.match(val):
            offenders.append(f"{name}={val[:80]!r} is remote")
        elif name in URL_ATTRS and val.strip() and not val.startswith("#"):
            # A local path is still a second file, and a second file does not travel with the
            # first. `#anchor` is the one admissible value: it addresses this document.
            offenders.append(f"{name}={val[:80]!r} points outside this file")

    if "<link" in html.lower():
        offenders.append("<link> element: a stylesheet that is not in this file")

    for token in CSS_FETCH:
        if token in html:
            offenders.append(f"stylesheet contains {token!r}, which fetches")
    for token in SCRIPT_FETCH:
        if token in html:
            offenders.append(f"script contains {token!r}: the report would depend on a reply")

    if offenders:
        raise ExternalReference(
            "the report reaches outside itself:\n  " + "\n  ".join(offenders)
            + "\nA report with an external reference renders differently depending on whether a "
            "server answered, and the difference does not appear in its hash."
        )
