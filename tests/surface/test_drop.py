"""P14-B3 — the drop screen. **One control, and the reason it is one.**"""

from __future__ import annotations

import re

from cdfc.surface.drop import ACCEPT, CONTROLS, drop_markup, drop_page
from cdfc.surface.labels import BANNED_GLYPHS, BANNED_PHRASES


def test_drop__exactly_one_control() -> None:
    """`plan/07`: one control, no settings, no account. Asserted, not described.

    Every setting here is a way to change what gets checked without changing what the report says
    was checked, which would defeat the Unchecked panel from outside the panel.
    """
    assert CONTROLS == ("file",)
    page = drop_page()
    assert page.count("<input") == 1
    assert page.count("<select") == 0
    assert page.count('type="checkbox"') == 0
    assert page.count('type="radio"') == 0


def test_drop__is_self_contained() -> None:
    """Inline CSS, no external reference — the same rule the report obeys."""
    page = drop_page()
    assert not re.findall(r"https?://", page)
    assert "<script" not in page
    assert "<style>" in page


def test_drop__no_banned_glyph_or_phrase_reaches_it() -> None:
    """SG1's rendered arm, applied to the new surface rather than only to the report."""
    page = drop_page().lower()
    for g in BANNED_GLYPHS:
        assert g not in drop_page(), f"banned glyph {g!r} on the drop screen"
    for phrase in BANNED_PHRASES:
        assert phrase.lower() not in page, f"banned phrase {phrase!r} on the drop screen"


def test_drop__states_what_it_returns_and_what_it_is_not() -> None:
    """The disclaimer is on the page a user sees FIRST, not only on the report they get after."""
    body = drop_markup()
    assert "not an audit opinion" in body
    assert "what was checked, and what was not" in body


def test_drop__accepts_only_xlsx() -> None:
    assert ACCEPT == ".xlsx"
    assert f'accept="{ACCEPT}"' in drop_page()


def test_drop__renders_byte_identically() -> None:
    assert drop_page() == drop_page()
