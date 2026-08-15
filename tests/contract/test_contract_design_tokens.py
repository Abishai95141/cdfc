"""The design tokens carry an EXCLUSION, and the exclusion must survive a change of design system.

`src/cdfc/surface/design.py` states in prose that there is no affirmative colour and no affirmative
badge token — the asymmetry the whole product rests on: *this system may say something is wrong
here, and may never say the opposite.* The P6 audit found the module reached by nothing and its
central claim asserted only in a docstring. A claim in a docstring is a claim nobody checks.

**These tests were written against the Meta commerce system and are re-pointed at Ecosystem
Visualization (15 Aug 2026) rather than rewritten**, and the difference matters. The old source
shipped an affirmative token to ban; the new one ships none — so the exclusion is now *cheaper*,
which makes it easier to lose. The tests below therefore check the property, never the source's
component list, and `test_design__the_superseded_vocabulary_is_still_banned` exists specifically to
stop the previous system's token names being tidied out of the banned list now that nothing defines
them.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface import design  # noqa: E402
from cdfc.surface.labels import BANNED_GLYPHS, BANNED_PHRASES  # noqa: E402

# Every name a design system uses for "this is fine". Neither source may ship one, and neither may
# a future one.
AFFIRMATIVE = (
    "success", "ok", "pass", "valid", "verified", "clean", "complete", "approved",
    "positive", "good", "safe", "green", "check", "tick", "compliant",
    # Added with the Ecosystem Visualization adaptation: its genre is the operations dashboard,
    # and these are the words that genre names its calm state with.
    "healthy", "nominal", "operational", "uptime",
)


def _all_token_names() -> set[str]:
    names: set[str] = set()
    for attr in dir(design):
        if attr.startswith("_"):
            continue
        value = getattr(design, attr)
        names.add(attr)
        if isinstance(value, dict):
            names |= {str(k) for k in value}
    return names


def test_design__there_is_no_affirmative_token() -> None:
    tokens = _all_token_names()
    assert tokens, "the module exposes no tokens at all; this test would pass over nothing"
    offenders = sorted(
        t for t in tokens
        if any(word in t.lower().replace("-", "_").split("_") for word in AFFIRMATIVE)
    )
    assert offenders == [], (
        f"an affirmative design token exists: {offenders}. This system may say *something is "
        "wrong here*; it may never say the opposite, and a token named for the second is how the "
        "second gets rendered."
    )


def _rgb(value: str) -> tuple[int, int, int]:
    h = value.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def test_design__no_palette_value_is_a_green() -> None:
    """By HUE, not by a list of literals — the list was the weaker half of the old test.

    The previous version banned three measured hex values that the Meta system shipped. Under a
    new source those three do not appear, so the test would have passed over a palette containing
    any other green. A green is a green because of where it sits on the wheel, and that is what is
    checked now: the literals were a pre-filter for one design system, and the hue is the rule.
    """
    assert design.COLOR, "no palette found; the assertion would be vacuous"
    greens = []
    for name, value in design.COLOR.items():
        if not (isinstance(value, str) and value.startswith("#") and len(value) == 7):
            continue
        r, g, b = _rgb(value)
        # Green-dominant and saturated enough to read as one. A near-grey with g one point high is
        # not a success colour, and flagging it would make the test a nuisance rather than a gate.
        if g > r + 24 and g > b + 24:
            greens.append(f"{name}={value}")
    assert greens == [], (
        f"a green is in the palette: {greens}. Colour must not encode a verdict at all, and the "
        "one colour this product may never own is the one that reads as an all-clear."
    )


def test_design__the_superseded_vocabulary_is_still_banned() -> None:
    """The tokens of a design system that no longer exists stay in the banned list.

    This is the test that stops a tidy-up. `badge-success`, `badge-promo-yellow` and
    `promo-banner` are defined by nothing now — DESIGN.md is Ecosystem Visualization — so the
    natural next edit is to remove them as dead entries. The list would then be one design system
    behind, and it would be one behind *silently*, because no gate fires for a token nobody uses.
    """
    banned = " ".join(BANNED_PHRASES).lower()
    for name in ("badge-success", "badge-promo-yellow", "promo-banner"):
        assert name in banned, f"{name} was removed from the banned vocabulary"
    assert BANNED_GLYPHS, "no banned glyphs; ci/no-green-tick.sh would scan for nothing"


def test_design__the_dashboard_vocabulary_is_banned() -> None:
    """Ecosystem Visualization's collision is a GRAMMAR, and these are the words it uses."""
    banned = " ".join(BANNED_PHRASES).lower()
    for name in ("all systems", "operational", "uptime", "healthy", "nominal"):
        assert name in banned, (
            f"{name!r} is the status-dashboard idiom this design system is built from and it is "
            "not in the banned vocabulary"
        )


def test_design__tokens_are_typed_and_complete() -> None:
    """The admission-side control: the module is a real artifact, not an empty shell.

    Without this, deleting every token would make every test above pass.
    """
    assert len(design.TYPE) >= 6, "the type scale is missing"
    for name, spec in design.TYPE.items():
        assert len(spec) == 4, f"{name} is not (px, weight, line-height, family)"
        px, weight, line, family = spec
        assert isinstance(px, int) and isinstance(weight, int) and isinstance(line, float)
        assert family in design.FONT_STACK, f"{name} names font {family!r} with no stack"
    assert len(design.SPACING) >= 6 and len(design.COLOR) >= 8


def test_design__the_two_hero_lines_cannot_be_given_different_ink() -> None:
    """One token and one ink constant, used by both lines.

    The moment the hero's two counts can take different values, a stylesheet can make one of them
    the accent — and the one that would lose the argument is the count of fields nobody checked.
    """
    assert isinstance(design.HERO_TOKEN, str) and design.HERO_TOKEN in design.TYPE
    assert isinstance(design.HERO_INK, str) and design.HERO_INK in design.COLOR


def test_design__every_permitted_pairing_clears_its_floor() -> None:
    """Every pairing in CONTRAST is legible at the job it is named for.

    Three tokens in this palette are DERIVED because the source value failed here — the accent at
    2.79:1 could not carry text, and an attention colour that is the least legible thing on the
    page inverts the product. This test is what keeps the derivation from being reverted to the
    source value by someone matching the design file.
    """
    assert design.CONTRAST, "no measured pairings; the floors would guard nothing"
    for (fg, bg), ratio in design.CONTRAST.items():
        assert fg in design.COLOR and bg in design.COLOR, f"({fg}, {bg}) names an unknown token"
        assert ratio >= design.CONTRAST_FLOOR_BOUNDARY, (
            f"{fg} on {bg} is {ratio}:1, below the {design.CONTRAST_FLOOR_BOUNDARY}:1 floor for a "
            "boundary that carries meaning"
        )
    for pair in (("text-primary", "background"), ("accent-ink", "background"),
                 ("on-surface", "surface"), ("text-primary", "accent")):
        assert design.carries_text(*pair), f"{pair} cannot carry text"


def test_design__an_unmeasured_pairing_raises_rather_than_defaulting() -> None:
    """`accent` as INK is exactly the pairing that must not silently return a number.

    It is 2.79:1 on the background and fails every floor, which is why it is absent from CONTRAST.
    A `contrast_of` that returned a default would report a measurement nobody took.
    """
    import pytest

    with pytest.raises(KeyError):
        design.contrast_of("accent", "background")


def test_design__no_content_is_gated_on_an_animation() -> None:
    """Rule one of the motion adaptation, as a property rather than a paragraph.

    A staggered reveal that holds items out of the layout means a reader who scrolls past
    mid-stagger sees fewer findings than exist — under-reporting that looks like completeness,
    reached through a CSS choice. The reveal may animate opacity and transform and nothing else.
    """
    assert set(design.REVEAL_ANIMATES_ONLY) == {"opacity", "transform"}
    for prop in ("display", "visibility", "height", "max-height", "content-visibility"):
        assert prop in design.REVEAL_NEVER_ANIMATES
        assert prop not in design.REVEAL_ANIMATES_ONLY
    assert design.STAGGER_TOTAL_CAP_MS <= 600, (
        "an uncapped stagger is an unbounded window in which the surface is incomplete"
    )


def test_design__no_figure_counts_up() -> None:
    """Rule two. Every intermediate value of a count-up is smaller than the truth.

    For the duration of such an animation the surface understates what was not checked, and a
    screenshot taken during it is a document that is wrong in the flattering direction.
    """
    assert design.FIGURES_ANIMATE is False
    assert design.DURATION_MS["instant"] == 0
    assert design.REDUCED_MOTION_COLLAPSES_TO == "instant"


def test_design__the_effect_layer_carries_no_information() -> None:
    """A decorative layer that carried meaning would be meaning nobody can copy, search or hear."""
    assert design.EFFECT_LAYER_IS_DECORATIVE_ONLY is True
    assert "gradient" in design.GRADIENT_WASH


def test_design__both_font_stacks_end_in_a_system_face() -> None:
    """Nothing here opens a socket, so neither font can be fetched.

    The mono fallback is load-bearing rather than cosmetic: the figure tokens are aligned by the
    FACE, so a fallback that is not monospaced loses the alignment the token exists for.
    """
    assert design.FONT_STACK[design.SANS].rstrip().endswith("sans-serif")
    assert design.FONT_STACK[design.MONO].rstrip().endswith("monospace")
    assert "monospace" in design.FONT_STACK[design.MONO]
    for token, (_px, _w, _lh, family) in design.TYPE.items():
        if token.startswith(("figure", "label")):
            assert family == design.MONO, f"{token} is a figure or label and is not in the mono face"
