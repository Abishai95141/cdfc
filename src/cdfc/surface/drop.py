"""P14-B3 — the drop screen. **One control, no settings, no account.**

`plan/07`: *"One control, no settings, no account."* That is a constraint on what the screen may
contain, so it is asserted rather than described: `CONTROLS` is the closed list, and
`test_drop__exactly_one_control` fails if a second one appears.

## Why one control is a coverage argument and not a taste in design

Every setting on this screen is a way for a user to change what gets checked without changing what
the report SAYS was checked. A "strict mode" toggle, a sheet selector, a "skip empty rows" box —
each one silently moves the denominator, and the report's own headline (`1,898 checks`,
`1,849 not checked`) becomes a number about a configuration nobody recorded. The Unchecked panel is
this product; a control that alters coverage without appearing in the panel would defeat it from
the outside.

So the screen takes a file and nothing else. What was checked is a function of the filing and the
admitted predicate set, both of which are in the attestation.
"""

from __future__ import annotations

from typing import Final

from cdfc.surface.markup import Raw, fill
from cdfc.surface.stylesheet import stylesheet

# THE CLOSED LIST. A second entry is a visible diff and fails a test.
CONTROLS: Final[tuple[str, ...]] = ("file",)

# Accepted upload types. `.xlsx` is a zip container, and the API rejects a non-zip with 415 before
# anything reads it -- the screen states the same rule so a user is not told by a 415 what the
# page could have told them first.
ACCEPT: Final[str] = ".xlsx"

_TEMPLATE: Final[str] = """<main class="drop">
  <h1>{{heading}}</h1>
  <p class="lede">{{lede}}</p>
  <form class="drop-form" method="post" action="/v1/filings" enctype="multipart/form-data">
    <label class="drop-target" for="filing">
      <span class="drop-word">{{control_label}}</span>
      <input id="filing" name="filing" type="file" accept="{{accept}}" required>
    </label>
    <button type="submit">{{submit}}</button>
  </form>
  <p class="note">{{note}}</p>
</main>"""

HEADING: Final[str] = "Check a filing"
LEDE: Final[str] = (
    "You get back a coverage declaration: what was checked, and what was not. "
    "It is not an audit opinion, an assurance engagement, or a regulatory clearance."
)
CONTROL_LABEL: Final[str] = "Choose an .xlsx filing"
SUBMIT: Final[str] = "Check it"
NOTE: Final[str] = (
    "There are no settings. Every option on this screen would be a way to change what gets "
    "checked without changing what the report says was checked."
)


def drop_markup() -> str:
    """The screen's body. Escaped through `fill`, which has no off switch."""
    return fill(_TEMPLATE, {
        "heading": HEADING,
        "lede": LEDE,
        "control_label": CONTROL_LABEL,
        "accept": ACCEPT,
        "submit": SUBMIT,
        "note": NOTE,
    })


def drop_page() -> str:
    """A self-contained page: inline CSS, no external reference, same rule as the report."""
    return fill(
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>{{title}}</title><style>{{css}}</style></head><body>{{body}}</body></html>",
        {"title": "Check a filing", "css": Raw(stylesheet()), "body": Raw(drop_markup())},
    )
