"""P14-B1 — the template primitive. **Escaping is not a setting. It is the only substitution.**

## Why this exists instead of Jinja2 — DECIDED, and it is a deviation from `plan/07`

`plan/07` P14-B1 names `.j2` templates and assumes Jinja2. **Jinja2 is not in `requirements.lock`
and there is no `pip` in this environment**, so it cannot be added by this build. That is the
occasion; it is not the argument. The argument is:

1. **The report is the attested artifact.** It is hashed and it is what a third party reads. A
   template engine is a large body of code inside the trust boundary of the one file that has to be
   trustworthy, added to render a page with no loops over untrusted input.
2. **Escaping is the entire risk, and Jinja's escaping is a CONSTRUCTOR ARGUMENT.**
   `Environment(autoescape=True)` is a flag somebody sets — and *"a flag is what somebody sets when
   a pipeline is failing and the deadline is Friday"* is this project's own standing objection,
   used to reject a parameter on `project_oscal` at P11. Here the flag governs whether a sheet name
   containing `<` becomes markup on a compliance document.
3. **Precedent.** Ed25519, RFC 8785 canonicalisation, the Wilson interval and the CEL AST walk are
   all hand-rolled in this repository with the argument recorded. This is smaller than any of them.

**So: `fill()` escapes every value it substitutes, and there is no parameter that turns it off.**
Raw markup requires wrapping a value in `Raw(...)`, which is a distinct type, greppable in one
command, and asserted by `test_markup__raw_is_used_only_where_it_is_argued`. A caller cannot
accidentally emit markup; they can only do it on purpose, in a way that shows up in a diff.

## What it deliberately does not have

No loops, no conditionals, no filters, no inheritance, no expression language. A placeholder is
`{{name}}` and it is replaced by an escaped string. **Anything that needs a loop builds its rows in
Python**, where the escaping is the same function and the logic is testable without rendering. A
template language rich enough to hold logic is a second program in a file nobody runs tests
against.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

# `{{name}}` — no spaces, no filters, no expressions. The narrowness is the point: this pattern
# cannot match anything that would need evaluating.
PLACEHOLDER: Final[re.Pattern[str]] = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_.]*)\}\}")


class UnfilledPlaceholder(KeyError):
    """A template names a value the caller did not supply.

    **This raises rather than rendering an empty string.** A missing number on a coverage report is
    the exact failure this product exists to refuse: a blank where a count should be reads as
    *nothing to report*, and there is no way for a reader to tell it from a genuine zero.
    """


class UnusedValue(ValueError):
    """The caller supplied a value the template does not use.

    Checked in the other direction for the same reason the AST walker checks declared keys both
    ways: a value computed and never rendered is a number the report was supposed to carry and
    silently does not.
    """


@dataclass(frozen=True, slots=True)
class Raw:
    """Markup that is inserted verbatim. **The only way to bypass escaping.**

    It is a type rather than a flag so that every bypass is a distinct token in the source,
    countable with one grep, and reviewable as a list.
    """

    markup: str


def esc(value: Any) -> str:
    """Escape for HTML text and attribute context. `quote=True` covers `"` and `'`."""
    return html.escape(str(value), quote=True)


def fill(template: str, values: dict[str, Any]) -> str:
    """Substitute `{{name}}` with escaped values. **Both directions are checked.**

    Every placeholder must have a value, and every value must have a placeholder. A template and
    its caller that disagree in either direction is a report with a hole or a number that was
    computed and dropped, and neither is visible in the rendered page.
    """
    used: set[str] = set()

    def sub(m: re.Match[str]) -> str:
        name = m.group(1)
        if name not in values:
            raise UnfilledPlaceholder(
                f"the template names {{{{{name}}}}} and no value was supplied. This raises rather "
                "than rendering an empty string: a blank where a count should be reads as nothing "
                "to report, and a reader cannot tell it from a genuine zero."
            )
        used.add(name)
        v = values[name]
        return v.markup if isinstance(v, Raw) else esc(v)

    out = PLACEHOLDER.sub(sub, template)
    unused = sorted(set(values) - used)
    if unused:
        raise UnusedValue(
            f"{unused} were supplied and the template renders none of them. A number computed and "
            "never rendered is a number this report was supposed to carry."
        )
    return out


def load(path: Path) -> str:
    """Read a template. **HTML comments are refused.**

    Jinja comments are stripped at render; HTML comments are not, and reach the browser — the
    existing `report.html.j2` already carries that warning in its own head. Here the rule is
    enforced instead of noted: a `<!--` in a template is an unrendered note that ships to whoever
    opens the file, and `ci/no-green-tick.sh` does not scan inside one.
    """
    text = path.read_text(encoding="utf-8")
    if "<!--" in text:
        raise ValueError(
            f"{path} contains an HTML comment. It is not stripped at render and reaches the "
            "reader; put the note in the Python that fills the template, where it is scanned."
        )
    return text
