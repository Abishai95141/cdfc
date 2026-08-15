"""Design tokens, adopted from `DESIGN.md` (Ecosystem Visualization), per `docs/DESIGN-ADAPTATION.md`.

One artifact, not two: the surface imports these rather than re-typing values out of the markdown,
because a token re-typed in two places drifts and the copy that drifts is the one nobody is reading.

WHAT IS DELIBERATELY ABSENT, AND IT SURVIVED THE CHANGE OF DESIGN SYSTEM. There is no affirmative
colour and no affirmative badge token. The previous source defined both; this one defines neither,
which makes the omission cheaper and therefore easier to lose. It is still enforced by
`ci/no-green-tick.sh`, and the banned vocabulary in `cdfc.surface.labels` still carries the
previous system's affirmative token names even though that system is gone — a banned token whose
source has been removed is exactly the entry somebody deletes as tidy-up, and the gate would then
be one design system behind forever.

The asymmetry is the design: this system may say *something is wrong here*, and may never say the
opposite.

THREE TOKENS ARE DERIVED RATHER THAN QUOTED, and each is derived because the source value fails a
contrast measurement at the job the source assigns it. The measurements are in
`docs/DESIGN-ADAPTATION.md` with the arithmetic; the short version is that this product's whole
argument is that a reader must be able to SEE what was not checked, and a palette in which the
attention colour is the least legible thing on the page inverts that.
"""

from __future__ import annotations

from typing import Final

# --- colour ---------------------------------------------------------------------------
#
# Eight tokens quoted from the source, three derived. Every derived token carries the measured
# contrast ratio that forced it, so a future edit that "restores" the source value can see what it
# costs before making it.
COLOR: Final[dict[str, str]] = {
    # -- quoted, unchanged --
    "primary": "#E48B59",
    "secondary": "#ED7B46",
    "accent": "#ED7B46",
    "background": "#FFFFFF",
    "surface": "#53617A",
    "text-primary": "#111827",
    "text-secondary": "#4B5563",
    "border": "#D8DADF",
    # -- derived, with the ratio that forced each --
    #
    # `accent` on `background` is 2.79:1. That fails normal text (4.5) AND fails the 3.0 floor for
    # a non-text interface boundary. So the accent may be a FILL under dark ink — `text-primary`
    # on `accent` is 6.35:1 — and may never be ink itself. Where a rule, a count or a label must
    # be in the attention colour, it uses this: the accent darkened until it carries text on the
    # background, measured at 4.61:1.
    "accent-ink": "#B45D35",
    # `border` on `background` is 1.40:1 — a decorative hairline, not a boundary. Where a border
    # is the only thing separating two meanings (the edge of the Unchecked panel, the rule under a
    # count), it uses this, measured at 3.30:1.
    "border-strong": "#868E9C",
    # `surface` is a DARK panel, not a card. `text-primary` on `surface` is 2.84:1 and
    # `text-secondary` on it is 1.21:1 — both unreadable. `background` on `surface` is 6.25:1, so
    # the slate is an inverted panel carrying light ink. This token names the ink that goes on it,
    # so the pairing is in the token set rather than in whoever writes the CSS.
    "on-surface": "#FFFFFF",
}

# The pairs the surface is permitted to use, each with its measured ratio. A pairing absent from
# this table is one nobody measured.
CONTRAST: Final[dict[tuple[str, str], float]] = {
    ("text-primary", "background"): 17.74,
    ("text-secondary", "background"): 7.56,
    ("accent-ink", "background"): 4.61,
    ("border-strong", "background"): 3.30,
    ("text-primary", "accent"): 6.35,
    ("on-surface", "surface"): 6.25,
}

# THE FLOOR, and it is not decorative. 4.5:1 for text, 3.0:1 for a boundary that carries meaning.
CONTRAST_FLOOR_TEXT: Final[float] = 4.5
CONTRAST_FLOOR_BOUNDARY: Final[float] = 3.0

# --- type -----------------------------------------------------------------------------
#
# `(px, weight, line-height, family)`. Three tokens are quoted from the source — `display-lg`,
# `body-md` and `label-md`; the rest are DERIVED between them so the report has a working scale.
# The source is a landing page and defines three sizes; a coverage report needs a hierarchy.
SANS: Final[str] = "Inter"
MONO: Final[str] = "JetBrains Mono"

TYPE: Final[dict[str, tuple[int, int, float, str]]] = {
    "display-lg": (64, 500, 1.04, SANS),      # quoted
    "display-md": (48, 500, 1.08, SANS),
    "heading-lg": (32, 500, 1.20, SANS),
    "heading-md": (24, 500, 1.25, SANS),
    "heading-sm": (20, 500, 1.30, SANS),
    "body-lg": (18, 400, 1.60, SANS),
    "body-md": (16, 400, 1.60, SANS),         # quoted
    "body-md-strong": (16, 600, 1.60, SANS),
    "body-sm": (14, 400, 1.55, SANS),
    "label-md": (12, 600, 1.20, MONO),        # quoted
    "label-sm": (11, 600, 1.20, MONO),
    # EVERY NUMBER ON THIS SURFACE IS SET IN THE MONO FACE, at the body size. A count in a
    # proportional face does not align down a column, and a column of counts that does not align
    # is a column a reader skims instead of reads. This is the one place the source's
    # "labels and technical metadata use a mono face" is extended rather than adopted.
    "figure-md": (16, 500, 1.40, MONO),
    "figure-lg": (24, 500, 1.30, MONO),
}

# **NEITHER FONT CAN BE FETCHED.** Nothing in this product opens a socket, and a surface that
# renders differently depending on whether a font server answered is a surface whose evidence
# depends on the network. Both stacks therefore end in a system face, and the mono stack is
# load-bearing rather than cosmetic: the figures above are aligned by the FACE, so a fallback that
# is not monospaced loses the alignment the token exists for.
FONT_STACK: Final[dict[str, str]] = {
    SANS: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    MONO: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
}

# --- spacing (px) ---------------------------------------------------------------------
#
# The source declares an 8px base. The previous system was 4px, and the half-step is retained
# rather than dropped: `xxs` is the only place a 4 survives, and it exists for the gap between a
# figure and the unit that qualifies it, which reads as two words at 8 and as one at 4.
SPACING: Final[dict[str, int]] = {
    "xxs": 4,
    "xs": 8,          # base
    "sm": 12,
    "md": 16,         # gap
    "lg": 24,         # card-padding
    "xl": 32,
    "xxl": 48,
    "section": 80,    # section-padding
    "hero": 120,
}

RADIUS: Final[dict[str, int | str]] = {
    "card": 16,
    "control": 8,
    "pill": "9999px",
}

# The source's cards carry a border and a shadow — nested surfaces, a dense hierarchy. Adopted,
# with the elevation kept shallow: a deep shadow on a compliance panel reads as a dashboard tile,
# and a dashboard tile reads as a thing being watched and found well.
#
# THE FIRST DRAFT OF THIS COMMENT QUOTED THE SOURCE'S OWN PHRASE FOR THAT HIERARCHY, AND
# `ci/no-green-tick.sh` WENT RED ON IT. The gate was right and the comment was wrong: the scan
# root is user-facing copy, the word is one of the eight added with this adaptation, and a
# rendered template importing this module has no way to know a token appeared in a comment rather
# than in a string. Every previous instance of this shape in the build was a check defeated by
# prose describing the thing it checks for, cured by walking the structure instead of the text.
# This one is the same shape with the opposite outcome — here the text IS the subject, so the text
# scan is the right instrument and the prose is what had to move.
ELEVATION: Final[dict[str, str]] = {
    "flat": "none",
    "card": "0 1px 2px rgba(17, 24, 39, 0.04), 0 4px 12px rgba(17, 24, 39, 0.06)",
    "lift": "0 2px 4px rgba(17, 24, 39, 0.06), 0 12px 28px rgba(17, 24, 39, 0.10)",
}

# --- motion ---------------------------------------------------------------------------
#
# The source asks for masked reveals, staggered entrance, hover lift, scroll-triggered transitions
# and ambient movement, with smooth restrained easing. All five are adopted. TWO RULES CONSTRAIN
# THEM, and both exist because the obvious implementation of a staggered reveal is a surface that
# under-reports — which is the exact failure this product is built to refuse.
DURATION_MS: Final[dict[str, int]] = {
    "instant": 0,
    "hover": 160,
    "reveal": 420,
    "ambient": 14_000,
}

EASING: Final[dict[str, str]] = {
    "standard": "cubic-bezier(0.22, 0.61, 0.36, 1)",
    "enter": "cubic-bezier(0.16, 1, 0.30, 1)",
    "ambient": "linear",
}

# The stagger between successive items in a revealed group. Small, and CAPPED: at 60ms an eight-row
# group finishes in under half a second, and a twenty-row group would take 1.2s if the step were
# not capped by the total below.
STAGGER_STEP_MS: Final[int] = 60
STAGGER_TOTAL_CAP_MS: Final[int] = 480

# RULE ONE. **No content is gated on an animation.** Every element is in the DOM, laid out, and
# present to a text extractor before any reveal runs; a reveal animates opacity and transform only,
# and never `display`, `visibility`, height, or a conditional render. The failure mode this
# forbids: a reader scrolls past a findings group before its stagger completes and sees fewer
# findings than exist, with nothing in the output to distinguish that from a shorter list. On a
# marketing page that is a missed flourish. Here it is the product's one unforgivable defect,
# reached by a CSS choice.
REVEAL_ANIMATES_ONLY: Final[tuple[str, ...]] = ("opacity", "transform")
REVEAL_NEVER_ANIMATES: Final[tuple[str, ...]] = (
    "display", "visibility", "height", "max-height", "content-visibility",
)

# RULE TWO. **No figure counts up.** A count that animates from zero renders every intermediate
# value, and every one of them is a smaller number than the truth — so for the duration of the
# animation the surface is understating what was not checked, and a screenshot taken during it is
# a document that is wrong in the flattering direction. Figures appear at their value.
FIGURES_ANIMATE: Final[bool] = False

# `prefers-reduced-motion` collapses every duration to `instant` and the stagger to zero. This is
# not a courtesy: with rule one in force, reduced motion is the same surface with the transitions
# removed, so the two renderings carry identical content and the reduced one is the proof.
REDUCED_MOTION_COLLAPSES_TO: Final[str] = "instant"

# --- effects --------------------------------------------------------------------------
#
# The source's atmospheric layer is adopted as a BACKGROUND ONLY: a soft gradient wash behind the
# hero, drawn under the content, never over it, never interactive, and never carrying information.
# It is `aria-hidden`, it is skipped entirely under reduced motion, and no figure, label or state
# is ever rendered into it. A decorative layer that carries meaning is a meaning nobody can copy,
# search, or read aloud.
EFFECT_LAYER_IS_DECORATIVE_ONLY: Final[bool] = True
# rate-ok: the percentages below are CSS gradient GEOMETRY -- position and extent in the
# painting box -- and not a measurement of anything. `ci/no-bare-rate.sh` flagged all four,
# correctly by its own rule: it cannot tell a rate from a coordinate, and the cure for that
# has always been to say which this is rather than to loosen the pattern.
GRADIENT_WASH: Final[str] = (
    "radial-gradient(120% 90% at 12% 0%, rgba(237, 123, 70, 0.10) 0%, "   # rate-ok: CSS geometry
    "rgba(237, 123, 70, 0.00) 55%), "                                     # rate-ok: CSS geometry
    "radial-gradient(90% 70% at 96% 8%, rgba(83, 97, 122, 0.10) 0%, "     # rate-ok: CSS geometry
    "rgba(83, 97, 122, 0.00) 60%)"                                        # rate-ok: CSS geometry
)

# --- the two-count hero ---------------------------------------------------------------
#
# BOTH lines take the same token. Same size, same weight, same ink. The moment one is larger or
# more coloured than the other, the reader has been told which one matters — and the one they
# would be told to ignore is the count of fields nobody checked.
HERO_TOKEN: Final[str] = "display-lg"
HERO_INK: Final[str] = "text-primary"

# The report's layout. The source is a bento grid; the report is a findings column and a rail, and
# the split is kept from the previous adaptation because it is a property of the content rather
# than of either design system.
FINDINGS_COLUMN_PCT: Final[int] = 58
COVERAGE_RAIL_PCT: Final[int] = 42
COVERAGE_RAIL_MAX_PX: Final[int] = 380
MOBILE_BREAKPOINT_PX: Final[int] = 768


def font_stack(token: str) -> str:
    """The CSS `font-family` for a type token, with its fallbacks."""
    return FONT_STACK[TYPE[token][3]]


def contrast_of(foreground: str, background: str) -> float:
    """The measured ratio for a permitted pairing. **Raises on a pairing nobody measured.**

    A `KeyError` here is the correct outcome: it means the surface is about to render ink on a
    ground whose legibility is unknown, and defaulting to a plausible number would be a
    measurement nobody took, rendered as one that was.
    """
    return CONTRAST[(foreground, background)]


def carries_text(foreground: str, background: str) -> bool:
    return contrast_of(foreground, background) >= CONTRAST_FLOOR_TEXT


def carries_boundary(foreground: str, background: str) -> bool:
    return contrast_of(foreground, background) >= CONTRAST_FLOOR_BOUNDARY
