"""P14-B1 — the stylesheet, GENERATED from `design.py`. **One artifact, not two.**

A hand-written `.css` beside a token module is two copies of the palette, and the one that drifts
is the one nobody is reading. So the CSS is emitted from the tokens, which means:

- a colour that is not in `COLOR` cannot appear on the report;
- the two hero lines take one class, so no rule can give one of them the accent;
- the derived tokens (`accent-ink`, `border-strong`, `on-surface`) are the only ones used where
  legibility matters, and `design.contrast_of()` has already refused every pairing nobody measured.

**Every literal colour here is a token lookup.** `test_style__no_literal_colour_outside_the_palette`
asserts it, because the fastest way to reintroduce a success green is to type one.
"""

from __future__ import annotations

from cdfc.surface import design


def _t(token: str) -> str:
    px, weight, line, family = design.TYPE[token]
    return (f"font-family:{design.FONT_STACK[family]};font-size:{px}px;"
            f"font-weight:{weight};line-height:{line}")


def stylesheet() -> str:
    """The whole report's CSS, from the tokens."""
    c = design.COLOR
    s = design.SPACING
    r = design.RADIUS
    return f"""
:root {{ color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: {c["background"]}; color: {c["text-primary"]};
  {_t("body-md")};
  -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: {s["section"]}px {s["lg"]}px; position: relative; }}

/* The atmospheric layer: BEHIND the content, aria-hidden, carrying no information.
   A decorative layer that carried meaning would be meaning nobody can copy or hear. */
.wash {{
  position: absolute; inset: 0; z-index: 0; pointer-events: none;
  background: {design.GRADIENT_WASH};
}}
.wrap > *:not(.wash) {{ position: relative; z-index: 1; }}

/* THE HERO. Both lines take THIS class. One rule, one ink — a stylesheet cannot give one of
   them the accent, because there is only one selector. */
.hero {{ {_t(design.HERO_TOKEN)}; color: {c[design.HERO_INK]}; margin: 0 0 {s["sm"]}px; letter-spacing: -0.01em; }}
.hero-block {{ margin-bottom: {s["xl"]}px; }}
.meta {{ {_t("label-md")}; color: {c["text-secondary"]}; text-transform: uppercase;
        letter-spacing: 0.06em; margin: 0 0 {s["xs"]}px; }}
.caveat {{ {_t("body-md")}; color: {c["text-secondary"]}; max-width: 68ch;
          border-left: 3px solid {c["accent"]}; padding-left: {s["md"]}px; margin: {s["md"]}px 0 0; }}

/* THE BAND. It never fills: the last two segments are hatched and always drawn. */
.band {{ display: flex; width: 100%; height: 44px; border-radius: {r["control"]}px;
        overflow: hidden; border: 1px solid {c["border-strong"]}; margin: {s["lg"]}px 0 {s["md"]}px; }}
/* no height: flex children stretch by default, and `ci/no-bare-rate.sh` reads a CSS
   percentage as a rate — correctly by its own rule, since it cannot tell one from a
   geometry. The cure here is to not need the number. */
.seg {{ align-self: stretch; }}
.seg-solid {{ background: {c["surface"]}; }}
.seg-solid.k-SETTLED_FAIL {{ background: {c["accent"]}; }}
.seg-solid.k-NO_PREDICATE {{ background: {c["border"]}; }}
.seg-hatch {{
  background: repeating-linear-gradient(45deg,
    {c["border-strong"]} 0, {c["border-strong"]} 4px,
    {c["background"]} 4px, {c["background"]} 9px);
}}
.legend {{ list-style: none; padding: 0; margin: 0; display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: {s["xs"]}px {s["lg"]}px; }}
.legend li {{ {_t("body-sm")}; color: {c["text-secondary"]}; display: flex; align-items: baseline; gap: {s["xs"]}px; }}
.swatch {{ width: 10px; height: 10px; border-radius: 2px; flex: none;
          border: 1px solid {c["border-strong"]}; }}
.figure {{ {_t("figure-md")}; color: {c["text-primary"]}; font-variant-numeric: tabular-nums; }}

section {{ margin-top: {s["section"]}px; }}
h2 {{ {_t("heading-md")}; margin: 0 0 {s["md"]}px; }}
.card {{ background: {c["background"]}; border: 1px solid {c["border"]};
        border-radius: {r["card"]}px; padding: {s["lg"]}px; box-shadow: {design.ELEVATION["card"]}; }}
.panel-dark {{ background: {c["surface"]}; color: {c["on-surface"]};
              border-radius: {r["card"]}px; padding: {s["lg"]}px; }}
.panel-dark .meta {{ color: {c["on-surface"]}; opacity: .82; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ text-align: left; padding: {s["xs"]}px {s["sm"]}px;
         border-bottom: 1px solid {c["border"]}; {_t("body-sm")}; }}
th {{ {_t("label-md")}; color: {c["text-secondary"]}; text-transform: uppercase; letter-spacing: .06em; }}
td.num {{ {_t("figure-md")}; text-align: right; font-variant-numeric: tabular-nums; }}
.pill {{ display: inline-block; border-radius: {r["pill"]}; padding: 2px {s["sm"]}px;
        background: {c["accent"]}; color: {c["text-primary"]}; {_t("label-md")}; }}
.strapline {{ {_t("body-sm")}; color: {c["text-secondary"]}; margin-top: {s["xxl"]}px;
             border-top: 1px solid {c["border"]}; padding-top: {s["md"]}px; }}

/* MOTION. Rule one: the reveal animates opacity and transform ONLY — every row is in the DOM
   and laid out before it runs, so a reader who scrolls past mid-stagger sees every finding. */
.reveal {{ opacity: 0; transform: translateY(6px);
          animation: rise {design.DURATION_MS["reveal"]}ms {design.EASING["enter"]} forwards; }}
@keyframes rise {{ to {{ opacity: 1; transform: none; }} }}
@media (prefers-reduced-motion: reduce) {{
  .reveal {{ animation: none; opacity: 1; transform: none; }}
}}
@media (max-width: {design.MOBILE_BREAKPOINT_PX}px) {{
  .wrap {{ padding: {s["xxl"]}px {s["md"]}px; }}
  .hero {{ font-size: {design.TYPE["heading-lg"][0]}px; }}
}}
""".strip() + "\n"
