"""The template primitive: **escaping is the only substitution, and it has no off switch.**"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.markup import (  # noqa: E402
    PLACEHOLDER, Raw, UnfilledPlaceholder, UnusedValue, esc, fill, load,
)


def test_markup__every_substituted_value_is_escaped() -> None:
    """A sheet name containing `<` must not become markup on a compliance document."""
    out = fill("<p>{{x}}</p>", {"x": '<script>alert("x")</script>'})
    assert "<script>" not in out
    assert "&lt;script&gt;" in out and "&quot;" in out


def test_markup__there_is_no_parameter_that_disables_escaping() -> None:
    """The whole argument for hand-rolling this. Jinja's `autoescape` is a constructor argument;
    here there is no argument at all, so there is nothing to set on a Friday."""
    import inspect

    params = list(inspect.signature(fill).parameters)
    assert params == ["template", "values"], f"fill() takes {params}"
    assert not any("escape" in p.lower() or "safe" in p.lower() for p in params)


def test_markup__raw_is_the_only_bypass_and_it_is_a_type() -> None:
    """A bypass has to be a distinct token in the source, countable with one grep."""
    assert fill("{{x}}", {"x": Raw("<b>ok</b>")}) == "<b>ok</b>"
    assert fill("{{x}}", {"x": "<b>no</b>"}) == "&lt;b&gt;no&lt;/b&gt;"


def test_markup__an_unfilled_placeholder_raises_rather_than_rendering_blank() -> None:
    """A blank where a count should be reads as *nothing to report*, and a reader cannot tell it
    from a genuine zero."""
    with pytest.raises(UnfilledPlaceholder):
        fill("{{a}} {{b}}", {"a": 1})


def test_markup__an_unused_value_raises_too() -> None:
    """The other direction, for the reason the AST walker checks declared keys both ways: a number
    computed and never rendered is a number the report was supposed to carry."""
    with pytest.raises(UnusedValue):
        fill("{{a}}", {"a": 1, "b": 2})


def test_markup__the_placeholder_grammar_admits_no_expression() -> None:
    """`{{ x|filter }}` and `{{ x + 1 }}` must not match. A template rich enough to hold logic is a
    second program nobody runs tests against."""
    assert PLACEHOLDER.findall("{{ok_name}} {{a.b}}") == ["ok_name", "a.b"]
    assert PLACEHOLDER.findall("{{ x|e }} {{a + 1}} {{ spaced }}") == []


def test_markup__a_template_with_an_html_comment_is_refused(tmp_path: Path) -> None:
    """Jinja comments are stripped at render; HTML comments are not, and reach the reader."""
    p = tmp_path / "t.html"
    p.write_text("<p>hi</p>\n<!-- a note that ships -->\n")
    with pytest.raises(ValueError, match="HTML comment"):
        load(p)


def test_markup__the_shipped_template_loads_under_that_rule() -> None:
    """THE ADMISSION-SIDE CONTROL: the rule above is satisfiable by the template we actually ship,
    so it is a constraint rather than a prohibition on templates."""
    from cdfc.surface.render import TEMPLATE_DIR

    assert load(TEMPLATE_DIR / "report.html").strip().startswith("<!doctype html>")


def test_markup__esc_covers_both_quote_characters() -> None:
    """Attribute context needs `'` as well as `"`; a title attribute is a reader-facing string."""
    assert esc("a\"b'c") == "a&quot;b&#x27;c"
