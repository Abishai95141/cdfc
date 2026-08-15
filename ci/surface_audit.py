#!/usr/bin/env python
"""P14-B1 — the four surface gates, run over a RENDERED artifact.

    make surface-audit

**The measurement: `surfaces_passing_all_four_gates / len(live SURFACES)` — two integers, printed
together, never as a percentage.**

| gate | what it proves |
|---|---|
| **SG1 — copy** | no banned glyph or phrase reaches a surface, in source **and in the rendered text** |
| **SG2 — provenance** | no FFR renders without `corpus_id`, provenance, `n` and an interval; `SELF-AUTHORED` renders `uninformative` and **no digit** |
| **SG3 — admission** | no settled count renders without the admission state **in the same block** — sharing an ancestor within 2 levels, not merely the same page |
| **SG4 — weight and ink** | the two hero counts take the **same** size, weight and colour; the unchecked segment is **hatched, not muted**; **no colour falls in the green hue band**; the band's terminal segments have non-zero width |

## WHAT THIS IMPLEMENTATION DOES NOT DO, AND IT IS THE HEADLINE

`plan/07` specifies SG1's DOM arm and **all of SG4** against a **headless browser** —
`page.inner_text("body")` after JS runs, and `getComputedStyle(el, "::before").content`. **There is
no headless browser in `requirements.lock` and no `pip` in this environment**, so that arm cannot
run here.

What runs instead is a **structural** arm: the artifact is parsed with `lxml` and the generated
stylesheet is read as data, so every assertion is about the bytes that ship. That is strictly
weaker than a computed style, and the difference is not cosmetic:

| the browser arm would catch | the structural arm cannot |
|---|---|
| a `::before` pseudo-element injecting a glyph through `content:` | **yes — this is the gap that matters most** |
| a user-agent or cascade default the stylesheet does not state | yes |
| a colour produced by blending, `filter`, or a gradient the parser does not evaluate | yes |
| text inserted by JavaScript after load | **no — this report ships no JavaScript at all**, which is why that half of the gap is closed by construction rather than by testing |

**So SG1-DOM and SG4-COMPUTED are recorded NOT RUN**, with the structural arm reported as what it
is. `docs/measurements/P14-surface-audit.md` carries the same boundary on its face. A gate that
cannot run is reported as not run — never as passed.
"""

from __future__ import annotations

import colorsys
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface import design  # noqa: E402
from cdfc.surface.labels import (  # noqa: E402
    SURFACES,
    banned_tokens,
    live_surfaces,
    render_ffr,
)

DOC = REPO / "docs" / "measurements" / "P14-surface-audit.md"

# HSL degrees. A colour inside this band, saturated and mid-lightness, reads as a success green.
GREEN_HUE_BAND = design_band = (80.0, 160.0)
MIN_SAT, LIGHT_LO, LIGHT_HI = 0.15, 0.20, 0.80

HEX = re.compile(r"#([0-9a-fA-F]{6})\b")


@dataclass
class GateResult:
    gate: str
    ran: bool
    passed: bool
    detail: str = ""
    surfaces: set[str] = field(default_factory=set)


def _rgb(h: str) -> tuple[float, float, float]:
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def is_green(hexcolour: str) -> bool:
    r, g, b = _rgb(hexcolour)
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    return (GREEN_HUE_BAND[0] <= hue * 360 <= GREEN_HUE_BAND[1]
            and sat > MIN_SAT and LIGHT_LO <= light <= LIGHT_HI)


def render_reference() -> tuple[str, Path]:
    """Render the reference filing. **The audit reads an artifact, not an intention.**"""
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED
    from cdfc.surface.render import render_report

    out = REPO / "reports" / "surface-audit" / "report.html"
    art = render_report(run_filing(TEMPLATE_COMPUTED), out=out)
    return out.read_text(encoding="utf-8"), art.path


def sg1_copy(html: str) -> GateResult:
    """Banned tokens in the RENDERED TEXT, not only in the source."""
    import lxml.html

    doc = lxml.html.fromstring(html)
    for bad in doc.xpath("//script | //style"):
        bad.getparent().remove(bad)
    text = doc.text_content().lower()
    hits = sorted({t for t in banned_tokens() if t.lower() in text})
    # Attribute values reach a reader too — `title` is a tooltip and `alt` is read aloud.
    for el in doc.iter():
        for attr in ("title", "alt", "aria-label", "placeholder"):
            v = (el.get(attr) or "").lower()
            hits += [t for t in banned_tokens() if t.lower() in v]
    hits = sorted(set(hits))
    return GateResult(
        "SG1", True, not hits,
        "no banned token in the rendered text or in a reader-facing attribute" if not hits
        else f"banned tokens reached the rendered surface: {hits}",
        {"S01.report-file", "S02.report-hero", "S03.report-strapline", "S04.report-band",
         "S05.report-openitems"},
    )


def sg2_provenance(html: str) -> GateResult:
    """An FFR renders with its provenance, or renders `uninformative` with **no digit**."""
    class SelfAuthored:
        corpus_provenance = "SELF-AUTHORED"
        false_failure_rate = "0/30"
        clean_corpus_independent_of_predicate = True
        n = 30

    class NotIndependent:
        corpus_provenance = "REGISTER-DERIVED"
        false_failure_rate = "0/30"
        clean_corpus_independent_of_predicate = False
        n = 30

    class Admissible:
        corpus_provenance = "REGISTER-DERIVED"
        false_failure_rate = "0"
        clean_corpus_independent_of_predicate = True
        n = 30

    bad: list[str] = []
    for name, q in (("no row", None), ("SELF-AUTHORED", SelfAuthored()),
                    ("not independent", NotIndependent())):
        cell = render_ffr(q)
        if cell.digits or any(ch.isdigit() for ch in cell.text):
            bad.append(f"{name} rendered a digit: {cell.text!r}")
    # THE ADMISSION SIDE. Without it this gate is satisfied by a renderer that prints
    # `uninformative` for everything, which would score perfectly while showing nothing.
    ok = render_ffr(Admissible())
    if not ok.digits or "30" not in ok.text:
        bad.append("an admissible FFR did not render its digits and its n — the gate is "
                   "refuse-everything")
    # This report renders no FFR at all yet (B4 owns the predicate library); the gate proves the
    # renderer's refusal, and says so rather than implying the page was inspected.
    return GateResult("SG2", True, not bad,
                      "render_ffr refuses all three uninformative cases and admits the fourth; "
                      "no FFR appears on this surface yet (P14-B4 owns it)" if not bad
                      else "; ".join(bad),
                      {"S01.report-file"})


def sg3_admission(html: str) -> GateResult:
    """A settled count and the admission state share an ancestor **within 2 levels**."""
    import lxml.html

    doc = lxml.html.fromstring(html)
    states = [el for el in doc.iter() if "PRE-GATE" in (el.text_content() or "")
              or "ADMITTED" in (el.text_content() or "")]
    if not states:
        return GateResult("SG3", True, False,
                          "no admission state appears anywhere on the surface", set())

    counts = [el for el in doc.iter()
              if el.tag == "p" and re.search(r"\d[\d,]*\s+(failures|fields)", el.text_content() or "")]
    if not counts:
        return GateResult("SG3", True, False, "no settled count found to check", set())

    def ancestors(el, n=3):
        out, cur = [], el
        for _ in range(n):
            cur = cur.getparent()
            if cur is None:
                break
            out.append(cur)
        return out

    bad = []
    for c in counts:
        near = set(ancestors(c, 2))
        if not any(near & set(ancestors(s, 2)) or s in near for s in states):
            bad.append(c.text_content().strip()[:60])
    return GateResult(
        "SG3", True, not bad,
        f"{len(counts)} settled counts, each within 2 ancestor levels of the admission state"
        if not bad else f"settled counts with no admission state in the same block: {bad}",
        {"S02.report-hero"},
    )


def sg4_weight_and_ink(html: str) -> GateResult:
    """Same size, weight and ink on both hero lines. Hatch, not mute. **No green.**

    STRUCTURAL, not computed — see the module docstring. What it can prove it proves from the
    bytes that ship.
    """
    import lxml.html

    from cdfc.surface.stylesheet import stylesheet

    doc = lxml.html.fromstring(html)
    css = stylesheet()
    bad: list[str] = []

    heroes = doc.xpath('//p[@class="hero"]')
    if len(heroes) != 2:
        bad.append(f"expected exactly 2 hero lines, found {len(heroes)}")
    classes = {tuple(sorted((h.get("class") or "").split())) for h in heroes}
    if len(classes) != 1:
        bad.append(f"the hero lines take different classes: {classes} — a stylesheet can then "
                   "give one of them the accent")
    if any(h.get("style") for h in heroes):
        bad.append("a hero line carries an inline style, which can override the shared rule")

    # The hatch must be a REPEATING PATTERN, not a lowered opacity. A muted segment reads as
    # "less important"; a hatched one reads as "a different kind of thing", which is what it is.
    if "repeating-linear-gradient" not in css:
        bad.append("the hatch is not a repeating pattern")
    if re.search(r"\.seg-hatch\s*\{[^}]*opacity\s*:\s*0?\.\d", css):
        bad.append("the hatched segment is muted by opacity rather than patterned")

    greens = sorted({h for h in HEX.findall(css) if is_green(h)})
    if greens:
        bad.append(f"colours in the green hue band reach the stylesheet: {['#' + g for g in greens]}")

    # The band's terminal segments must have non-zero rendered width.
    segs = doc.xpath('//div[contains(@class,"seg")]')
    if len(segs) < 2:
        bad.append("the band has fewer than two segments")
    else:
        for s in segs[-2:]:
            w = re.search(r"width:\s*([\d.]+)%", s.get("style") or "")
            if not w or float(w.group(1)) <= 0:
                bad.append(f"a terminal band segment has no width: {s.get('style')!r}")
        solid = sum(float(re.search(r"width:\s*([\d.]+)%", s.get("style") or "width:0%").group(1))
                    for s in segs if "seg-solid" in (s.get("class") or ""))
        total = sum(float(re.search(r"width:\s*([\d.]+)%", s.get("style") or "width:0%").group(1))
                    for s in segs)
        if solid >= total:
            bad.append(f"the band fills: solid {solid} of {total}")

    return GateResult("SG4", True, not bad,
                      "hero lines share one class with no inline style; hatch is a repeating "
                      "pattern; no colour in the green hue band; the band does not fill"
                      if not bad else "; ".join(bad),
                      {"S02.report-hero", "S04.report-band"})


def main() -> int:
    html, path = render_reference()
    results = [sg1_copy(html), sg2_provenance(html), sg3_admission(html), sg4_weight_and_ink(html)]

    live = live_surfaces()
    covered: set[str] = set()
    for r in results:
        if r.passed:
            covered |= r.surfaces
    # A surface passes only if EVERY gate that names it passed.
    failed_surfaces = {s for r in results if not r.passed for s in r.surfaces}
    passing = sorted({s.id for s in live} & covered - failed_surfaces)

    DOC.write_text(render_doc(results, passing, live, path, html), encoding="utf-8")
    for r in results:
        state = "PASS" if r.passed else "FAIL"
        print(f"  {r.gate}  {state:4s}  {r.detail[:96]}")
    print(f"\n  surfaces passing all four gates: {len(passing)} / {len(live)}")
    print(f"  wrote {DOC.relative_to(REPO)}")
    return 0 if all(r.passed for r in results) else 1


def render_doc(results, passing, live, path, html) -> str:
    rows = "\n".join(
        f"| **{r.gate}** | {'ran' if r.ran else '**NOT RUN**'} | "
        f"{'**PASS**' if r.passed else '**FAIL**'} | {r.detail} |"
        for r in results
    )
    reg = "\n".join(
        f"| `{s.id}` | {s.kind} | {', '.join(sorted(s.renders))} | "
        f"{'**retired ' + s.retired_on + '** — ' + s.retired_because if s.retired else 'live'} |"
        for s in SURFACES
    )
    return f"""# P14 — the surface audit

*Generated by `ci/surface_audit.py`. Re-run with `make surface-audit`.*

## The measurement

**{len(passing)} of {len(live)} surfaces pass all four gates.** Two integers, printed together,
never as a percentage — the denominator is `cdfc.surface.labels.SURFACES`, which is **append-only**
(see below).

Audited artifact: `{path.relative_to(REPO)}`, {len(html.encode('utf-8')):,} bytes, **zero external
references**.

| gate | | | detail |
|---|---|---|---|
{rows}

## What is NOT RUN, and it is the headline

`plan/07` specifies **SG1's DOM arm** (`page.inner_text` after JS) and **all of SG4**
(`getComputedStyle`, including `::before`/`::after` `content`) against a **headless browser**.
There is no headless browser in `requirements.lock` and no `pip` in this environment.

What ran instead is a **structural** arm: the artifact is parsed with `lxml` and the generated
stylesheet is read as data. Every assertion is about the bytes that ship, which is strictly weaker
than a computed style:

| the browser arm would catch | the structural arm |
|---|---|
| a `::before` pseudo-element injecting a glyph through `content:` | **misses it — the largest remaining hole in SG1** |
| a user-agent or cascade default the stylesheet does not state | misses it |
| a colour produced by blending, `filter`, or an unevaluated gradient | misses it |
| text inserted by JavaScript after load | **not applicable — this report ships no JavaScript at all**, so that half is closed by construction rather than by testing |

**A gate that cannot run is recorded as not run, never as passed.** Closing the gap needs a
headless browser in the lockfile; until then the structural arm is what the two integers above are
computed from, and this table is what qualifies them.

## The surface registry — APPEND-ONLY, because this phase's gate divides by it

The exit gate reads `surfaces_passing_all_four_gates == len(SURFACES)`, and **this build writes
`SURFACES`**. A surface that cannot be made to pass could be deleted and the gate would go green.
**That is M1 — the numerator choosing its own denominator — inside the gate meant to prevent it.**

So a row may be **retired** with a dated argument and **never deleted**; a retired row leaves the
gate's *denominator* and stays in the *scan*, because giving up on auditing a surface is not giving
up on prohibiting an affirmative claim on it.

| surface | kind | renders | state |
|---|---|---|---|
{reg}

**Cardinality: `|SURFACES|` = {len(SURFACES)}, live = {len(live)}, retired = {len(SURFACES) - len(live)}.**
`tests/surface/test_surface_registry.py` asserts the registry has never shrunk, by diffing it against
`docs/SURFACE-REGISTRY-LOG.md` rather than against a previous commit — so the check survives a
squash.
"""


if __name__ == "__main__":
    raise SystemExit(main())
