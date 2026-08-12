# docs/DESIGN-ADAPTATION.md — how `DESIGN.md` is used here

**Installed 11 Aug 2026 via `npx getdesign@latest add meta`.** `DESIGN.md` is the reference for every
surface this project builds (P14). This file records what is adopted, what is **excluded**, and — because a
design rule that is only prose is a preference — how the exclusion is enforced by a build gate.

---

## The collision, stated first

`DESIGN.md` is Meta's **commerce** language: product photography, buy-now flows, promotional strips,
affirmative status chips. Its component list includes:

> **`badge-success`** — Affirmative status ("In stock", **"Verified"**, "Free shipping").
> Background `{colors.success}`, text `{colors.canvas}`, rounded `{rounded.full}`.

A green, pill-shaped, affirmative chip reading *Verified* is **exactly** the object this product exists to
refuse. The single design commitment that governs every screen is: *there is no green tick anywhere, and a
surface that can render "all clear" will eventually render it wrongly, with nothing in the output to
distinguish that time from a correct one.*

That commitment is registry row 1, it is enforced by `ci/no-green-tick.sh`, and it has been **observed
red**. So the collision is resolved in the gate, not in a paragraph.

---

## ADOPTED — the form language, in full

These carry no semantic claim and are taken as-is. P14 imports them from
`src/cdfc/surface/design.py`, which is generated from this table so the tokens are one artifact rather
than two.

| Layer | What we take |
|---|---|
| **Type scale** | The full 15-token hierarchy, `hero-display` 64px through `caption` 12px. The **two-count hero** (`<F> failures across <S> checks` and `<U> fields were not checked`) uses `{typography.display-lg}` 48/500 for **both** lines — same size, same weight, same ink. The design system's own dual-CTA symmetry is the right precedent for two things that must not be traded against each other. |
| **Spacing** | The 4px base and the full token set. Report sections separate at `{spacing.section}` (64px); the Unchecked panel's rows tighten to `{spacing.xl}` (24px). |
| **Radius** | `{rounded.xxxl}` (32px) on panel containers, `{rounded.full}` on chips. |
| **Layout** | The PDP two-column split maps directly onto the report: findings gallery left (~58%), a sticky **coverage rail** right (~42%, `max-width: 380px`). The rail carries the settled fraction, its admission state, and the residue count. |
| **Elevation** | The "no card chrome" principle — no border, no shadow, content is the surface treatment. Suits a test-run report; a compliance surface should not look like a dashboard. |
| **Responsive** | The <768px collapse: hero stacks, three-up flattens, the right rail becomes a sticky bottom bar. The coverage rail becoming a sticky bottom bar is *better* than the desktop form, because the residue count then follows the reader down the page. |
| **Inputs, nav, cards** | As specified. |

## EXCLUDED — and each exclusion is a gate, not a note

| Excluded | Why | Enforcement |
|---|---|---|
| **`badge-success`** | An affirmative green chip is the all-clear this product refuses to render | `ci/no-green-tick.sh`, registry row 1. The literal token `badge-success` is in `cdfc.surface.labels.BANNED_PHRASES`; a template using it fails the build |
| **`badge-promo-yellow`**, **`promo-banner`** | Time-bound persuasion has no place on an assurance surface; a promotional strip above a verdict is a category error | same gate, same list |
| **`{colors.success}` as a verdict colour** | Colour must not encode a verdict at all. The hero's two counts are **the same ink** — the moment one is green and the other red, the reader has been told which one matters | same gate |
| **The photography-first hero** | There is no product photograph. The hero is two numbers | not gated; there is nothing to grep |

**`badge-critical` and `badge-attention` are NOT excluded.** Asymmetry is deliberate and it is the point:
this system may say *something is wrong here* and may never say *nothing is wrong here*. A failure chip is a
claim about a specific cell backed by a predicate with a measured false-failure rate. A success chip is a
claim about everything nobody looked at.

---

## What would falsify this adaptation

If P14 ships a surface where a reader can, at a glance, conclude "this filing is fine" — from a colour, a
glyph, a chip, or a 100% fraction — the adaptation failed regardless of what this file says. The gate
catches the tokens; it cannot catch a layout that implies an all-clear without naming one. **That residue
is declared here rather than assumed away**, and it is what the P14 copy review is for.
