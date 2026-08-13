"""The design tokens carry an EXCLUSION, and until now nothing checked it.

`src/cdfc/surface/design.py` states in prose that there is no `SUCCESS` colour and no affirmative
badge token — the asymmetry the whole product rests on: *this system may say something is wrong
here, and may never say nothing is wrong here.* The P6 audit found the module reached by nothing
and its central claim asserted only in a docstring.

A claim in a docstring is a claim nobody checks. These tests make the exclusion a property.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface import design  # noqa: E402
from cdfc.surface.labels import BANNED_GLYPHS, BANNED_PHRASES  # noqa: E402

# Every name a design system uses for "this is fine". `DESIGN.md` (Meta commerce) ships all of
# them; `docs/DESIGN-ADAPTATION.md` excludes them; this test is what makes the exclusion true.
AFFIRMATIVE = (
    "success", "ok", "pass", "valid", "verified", "clean", "complete", "approved",
    "positive", "good", "safe", "green", "check", "tick", "compliant",
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
        "wrong here*; it may never say *nothing is wrong here*, and a token named for the second "
        "is how the second gets rendered."
    )


def test_design__there_is_no_success_colour() -> None:
    palette = {
        k.lower(): v for name in dir(design) if not name.startswith("_")
        for k, v in (getattr(design, name).items() if isinstance(getattr(design, name), dict) else ())
    }
    assert palette, "no palette found; the assertion would be vacuous"
    assert not any("success" in k for k in palette)
    # The MEASURED green DESIGN.md ships for `badge-success`. If a value equal to it ever appears
    # in the palette, the token has been re-added under another name.
    greens = [k for k, v in palette.items() if isinstance(v, str) and v.lower() in ("#42b72a", "#31a24c", "#00a400")]
    assert greens == [], f"a success green is in the palette under {greens}"


def test_design__the_banned_vocabulary_covers_the_design_system_names() -> None:
    """The gate and the token module must agree about what is excluded."""
    banned = " ".join(BANNED_PHRASES).lower()
    for name in ("badge-success", "promo-banner"):
        assert name in banned, f"{name} is shipped by DESIGN.md and not in the banned vocabulary"
    assert BANNED_GLYPHS, "no banned glyphs; ci/no-green-tick.sh would scan for nothing"


def test_design__tokens_are_typed_and_complete() -> None:
    """The admission-side control: the module is a real artifact, not an empty shell.

    Without this, deleting every token would make all three tests above pass.
    """
    assert len(design.TYPE) >= 6, "the type scale is missing"
    for name, spec in design.TYPE.items():
        assert len(spec) == 3, f"{name} is not (px, weight, line-height)"
        px, weight, line = spec
        assert isinstance(px, int) and isinstance(weight, int) and isinstance(line, float)
