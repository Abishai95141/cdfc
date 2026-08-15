# docs/DESIGN-ADAPTATION.md — how `DESIGN.md` is used here

**`DESIGN.md` is *Ecosystem Visualization* (Neuform, author @vanh), installed 15 Aug 2026,
replacing the Meta commerce system that occupied this slot from 11 Aug.** It is the reference for
every surface this project builds (P14). This file records what is adopted, what is **excluded**,
what is **derived because the source value fails a measurement**, and — because a design rule that
is only prose is a preference — how each exclusion is enforced by a build gate.

**The product structure did not move.** The report is still two counts in one ink, a findings
column, a coverage rail, an Unchecked panel and a drop screen. What changed is the form language
they are drawn in.

---

## The collision, stated first — and it is a different collision from the last one

The previous source was a **commerce** system, and its collision was a single object: a green,
pill-shaped chip reading *Verified*. One token, one gate, done.

This source is a **status-dashboard** system — *"System Metriqs. Real-time mapping of data
streams."* Its tags are `feature, section, animated, bento, charts`. **Its collision is not a
token; it is a grammar.** The entire visual language of an operations dashboard is *everything is
nominal, and you would know if it were not* — dense metric tiles, sparklines trending flat, an
ambient sense of a system being watched and found well. There is no `badge-success` to ban,
because the reassurance is not in a component. It is in the composition.

That makes it **harder to gate and easier to adopt by accident**, and it is why this file is longer
than the one it replaces.

The commitment is unchanged, it is registry row 1, it is enforced by `ci/no-green-tick.sh`, and it
has been observed red:

> *There is no affirmative mark anywhere, and a surface that can render an all-clear will
> eventually render one wrongly, with nothing in the output to distinguish that time from a
> correct one.*

---

## ADOPTED — the form language, in full

| Layer | What we take |
|---|---|
| **Palette** | The eight source tokens, unchanged in value: `primary #E48B59`, `secondary`/`accent #ED7B46`, `background #FFFFFF`, `surface #53617A`, `text-primary #111827`, `text-secondary #4B5563`, `border #D8DADF`. **Three derived tokens are added; see the measurements below.** |
| **Type** | `Inter` for display and body, `JetBrains Mono` for labels and technical metadata. The source's three tokens are quoted exactly — `display-lg` 64/500/1.04, `body-md` 16/400/1.6, `label-md` 12/600/1.2 — and the intermediate scale is **derived** between them, because a landing page needs three sizes and a coverage report needs a hierarchy. |
| **Numerals** | Extended, not merely adopted: **every figure on the surface is set in the mono face**, not only labels. A count in a proportional face does not align down a column, and a column of counts that does not align is a column a reader skims instead of reads. |
| **Spacing** | The 8px base, `gap` 16, `card-padding` 24, `section-padding` 80. The previous 4px base is retained as a single half-step (`xxs`) for the gap between a figure and the unit that qualifies it, which reads as two words at 8px and as one at 4px. |
| **Radius** | `card` 16, `control` 8, `pill` 9999 — replacing the previous 32/24. The source's guardrail *"keep buttons, cards and badges aligned to the same radius language"* is adopted as written. |
| **Elevation** | Cards take a border **and** a shallow shadow, replacing the previous "no card chrome" principle. The source's nested-surface hierarchy is what makes a dense report readable. Kept shallow deliberately — see the exclusions. |
| **Motion** | All five cues: masked reveals, staggered entrance, hover lift, scroll-triggered transitions, ambient movement, smooth restrained easing. **Adopted under two rules that are not in the source**; both are below and both are load-bearing. |
| **Effects** | The atmospheric layer, as a gradient wash **behind** the hero. Adopted as strictly decorative — `aria-hidden`, no information, skipped under reduced motion. |
| **Layout** | The bento density informs the coverage rail's tiles. The 58/42 findings-column and rail split is **kept from the previous adaptation**, because it is a property of the content rather than of either design system. |

---

## DERIVED — three tokens, because the source value fails the job the source assigns it

Every ratio below is computed, not estimated, and reproduces with:

```bash
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); from cdfc.surface.design import CONTRAST; print(CONTRAST)"
```

| # | The source says | Measured | The problem | Derived token |
|---|---|---:|---|---|
| 1 | *"card background: use the surface token"* with `text-primary` ink | **2.84:1** | Unreadable. `text-secondary` on it is **1.21:1** — very nearly invisible. But `background` on `surface` is **6.25:1**. | **`surface` is an INVERTED PANEL, not a card.** It carries light ink; `on-surface #FFFFFF` names that ink so the pairing lives in the token set rather than in whoever writes the CSS. Body cards are `background` with a border. |
| 2 | `accent #ED7B46` as *"the main action"* colour | **2.79:1** on white | Fails normal text (4.5) **and** fails the 3.0 floor for a non-text interface boundary. **This one matters more here than it would anywhere else:** the accent is the attention colour, so if it is the least legible thing on the page then *the marking of a problem is harder to see than the rest of the report.* That inverts the product. | The accent is a **FILL under dark ink** — `text-primary` on `accent` is **6.35:1** — and is never ink itself. Where the attention colour must be ink, `accent-ink #B45D35` is the accent darkened until it carries text on the background: **4.61:1**. |
| 3 | `border #D8DADF` | **1.40:1** | A decorative hairline. Fine between two paragraphs; not fine as the only thing separating *checked* from *not checked*. | `border-strong #868E9C` at **3.30:1** for any border that is the sole carrier of a distinction. |

**`design.contrast_of()` raises `KeyError` on a pairing nobody measured**, which is the correct
outcome: it means the surface is about to put ink on a ground whose legibility is unknown, and
returning a plausible default would be a measurement nobody took, rendered as one that was.

---

## THE TWO MOTION RULES — and the first one is the most important line in this file

The source asks for *"masked reveals, staggered entrance, scroll-triggered transitions"*. The
obvious implementation of a staggered reveal holds each item out of the layout until its turn.

> **RULE ONE — no content is gated on an animation.** Every element is in the DOM, laid out, and
> present to a text extractor before any reveal runs. A reveal animates `opacity` and `transform`
> **only**, and never `display`, `visibility`, `height`, `max-height`, `content-visibility`, or a
> conditional render.
>
> **What it forbids:** a reader scrolls past a findings group before its stagger completes and
> **sees fewer findings than exist**, with nothing in the output to distinguish that from a
> shorter list. On a marketing page that is a missed flourish. Here it is this product's one
> unforgivable defect — under-reporting that looks like completeness — reached through a CSS
> choice rather than through a bug in the gate. The stagger is capped at 480ms total for the same
> reason.

> **RULE TWO — no figure counts up.** A count animating from zero renders every intermediate
> value, and **every one of them is smaller than the truth.** For the duration of the animation
> the surface understates what was not checked, and a screenshot taken during it is a document
> that is wrong in the flattering direction. `FIGURES_ANIMATE = False`.

`prefers-reduced-motion` collapses every duration to zero. With rule one in force this is not a
courtesy — the reduced rendering carries **identical content** to the animated one, which makes it
the proof that rule one holds.

---

## EXCLUDED — and each exclusion is a gate, not a note

| Excluded | Why | Enforcement |
|---|---|---|
| **Any affirmative colour, chip or glyph** | The all-clear this product refuses to render. The source ships none — which makes the omission *cheaper* and therefore easier to lose in a future edit | `ci/no-green-tick.sh` (row 1) + `tests/contract/test_contract_design_tokens.py`, which asserts no token name contains an affirmative word **and** that no palette value is a green by hue |
| **The previous system's token names, kept in the banned list** | `badge-success`, `badge-promo-yellow`, `promo-banner` no longer exist in any source. **They stay banned anyway.** A banned token whose source has been removed is exactly the entry somebody deletes as tidy-up, and the gate would then be one design system behind forever | `cdfc.surface.labels.BANNED_PHRASES`, asserted by `test_design__the_banned_vocabulary_covers_the_design_system_names` |
| **The status-dashboard vocabulary** | New to this adaptation. *"All systems", "operational", "nominal", "uptime", "healthy"* are the idiom this source's genre is built from, and every one of them is an all-clear in a word | same gate, same list — added at this adaptation |
| **Deep elevation / the tile aesthetic** | Adopted shallow. A deep shadow on a compliance panel reads as a dashboard tile, and a dashboard tile reads as *a thing being monitored, and fine* | not gated; a judgement recorded here and reviewed at P14 |
| **Sparklines and trend indicators on coverage figures** | A trend line implies a direction of travel and therefore a rate of improvement. The settled fraction is not a KPI, and a figure that appears to be trending upward is an affirmative claim drawn as a chart | not gated — there is no token to grep. Declared residue |
| **Colour as a verdict** | Unchanged from the previous adaptation, and it survives the palette change intact: the hero's two counts are **the same ink**. The moment one is accent-coloured and the other is not, the reader has been told which one matters — and it would be the count of fields nobody checked that was told to matter less | `HERO_TOKEN` and `HERO_INK` are single constants used by both lines |

**Attention and critical marks are NOT excluded**, and the asymmetry is deliberate: this system may
say *something is wrong here* and may never say the opposite. A failure mark is a claim about a
specific cell backed by a predicate with a measured false-failure rate. An affirmative mark is a
claim about everything nobody looked at.

---

## What would falsify this adaptation

If P14 ships a surface where a reader can, at a glance, conclude *this filing is fine* — from a
colour, a glyph, a chip, a trend, a density of calm tiles, or a fraction near 1 — the adaptation
failed regardless of what this file says.

**And the residue is larger under this source than under the last one.** The gate catches tokens;
it cannot catch a *composition* that implies an all-clear without naming one, and this design
system's entire genre is that composition. The previous adaptation declared the same residue
against a system whose reassurance lived in one green pill. Here it lives in the grammar, so:

- the P14 copy review is now also a **layout** review, and
- the falsification test is run against a **screenshot with the text removed** — if the shape
  alone reads as calm, the shape is making a claim the words are not.
