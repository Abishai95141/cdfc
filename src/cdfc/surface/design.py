"""Design tokens adopted from DESIGN.md (Meta commerce), per docs/DESIGN-ADAPTATION.md.

One artifact, not two: P14 imports these rather than re-typing values out of the
markdown, because a token re-typed in two places drifts and the copy that drifts is the
one nobody is reading.

WHAT IS DELIBERATELY ABSENT. There is no `SUCCESS` colour and no affirmative badge
token. `DESIGN.md` defines both; `docs/DESIGN-ADAPTATION.md` excludes them; and
`ci/no-green-tick.sh` fails the build if either name appears in a surface file. The
asymmetry is the design: this system may say *something is wrong here*, and may never say
*nothing is wrong here*.
"""

from __future__ import annotations

from typing import Final

# --- type scale (px, weight, line-height) -----------------------------------------
TYPE: Final[dict[str, tuple[int, int, float]]] = {
    "hero-display": (64, 500, 1.16),
    "display-lg": (48, 500, 1.17),
    "heading-lg": (36, 500, 1.28),
    "heading-md": (28, 300, 1.21),
    "heading-sm": (24, 500, 1.25),
    "subtitle-lg": (18, 700, 1.44),
    "subtitle-md": (18, 400, 1.44),
    "body-md": (16, 400, 1.50),
    "body-md-bold": (16, 700, 1.50),
    "body-sm": (14, 400, 1.43),
    "body-sm-bold": (14, 700, 1.43),
    "caption-bold": (12, 700, 1.33),
    "caption": (12, 400, 1.33),
    "button-md": (14, 700, 1.43),
    "link-md": (16, 700, 1.50),
}

# --- spacing (px), 4px base ---------------------------------------------------------
SPACING: Final[dict[str, int]] = {
    "xxs": 4, "xs": 8, "sm": 10, "md": 12, "base": 16, "lg": 20, "xl": 24,
    "xxl": 32, "xxxl": 40, "section-sm": 48, "section": 64, "section-lg": 80, "hero": 120,
}

RADIUS: Final[dict[str, int | str]] = {"xxxl": 32, "feature": 24, "full": "9999px"}

# --- the two-count hero -------------------------------------------------------------
# BOTH lines take the same token. Same size, same weight, same ink. The moment one is
# larger or greener than the other, the reader has been told which one matters.
HERO_TOKEN: Final[str] = "display-lg"

# The report's layout, mapped from the PDP two-column split.
FINDINGS_COLUMN_PCT: Final[int] = 58
COVERAGE_RAIL_PCT: Final[int] = 42
COVERAGE_RAIL_MAX_PX: Final[int] = 380
MOBILE_BREAKPOINT_PX: Final[int] = 768
