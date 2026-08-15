"""P14-B1 — the renderer. **One self-contained file, and it is the attested artifact.**

`reports/<run_id>/report.html`: inline CSS, inline JS, **zero external references**, openable from
`file://` with the network stack down, emailable, hashable. A file has a hash; a single-page
application does not, and the thing that gets attested has to be the thing the reader reads.

## `Hero` has no default for `admission`

Criterion A11 says a settled count may not render without the admission state of the predicate set
that produced it. A default would make that a convention somebody has to remember. **A frozen
dataclass with no default makes a `Hero` without an admission state unconstructible**, which is the
same move as `Observation.__post_init__` making *"no change"* unrepresentable on a failed fetch.

## There is no degraded report

`render_report` raises rather than emitting a partial document. A report that renders with a
section missing is a report whose silence is indistinguishable from a section that had nothing to
say — and that distinction is the entire product.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from cdfc.surface import band as band_mod
from cdfc.surface.admission import AdmissionState, admission_state, caveat
from cdfc.surface.inline import assert_no_external_refs
from cdfc.surface.labels import LABEL_REGISTRY, REQUIRED_NUMBERS, SURFACES
from cdfc.surface.markup import Raw, esc, fill
from cdfc.surface.stylesheet import stylesheet

TEMPLATE_DIR: Final[Path] = Path(__file__).resolve().parent / "templates"
REPORTS_DIR: Final[Path] = Path("reports")


class ClosureViolation(RuntimeError):
    """The run's seven-term closure does not hold. **Report generation ABORTS.**"""


class UnregisteredSurface(RuntimeError):
    """A template emitted a surface id that is not in `SURFACES`."""


class MissingRequiredNumber(RuntimeError):
    """A number the registry says must appear did not appear in the rendered bytes."""


@dataclass(frozen=True, slots=True)
class Hero:
    failures: int
    settled: int
    unchecked: int
    admission: AdmissionState        # NO DEFAULT. A Hero cannot be built without it.


@dataclass(frozen=True, slots=True)
class ReportArtifact:
    path: Path
    sha256: str
    n_bytes: int
    surfaces_rendered: frozenset[str]


def hero_of(run: Any) -> Hero:
    sf = run.fraction
    u = sf.unsettled
    return Hero(
        failures=int(sf.settled.failed),
        settled=int(sf.settled.total),
        unchecked=int(u.indeterminate) + int(u.notRun) + int(u.noPredicate) + int(u.error),
        admission=admission_state(run),
    )


def _band_markup(segments: tuple[band_mod.Segment, ...]) -> tuple[str, str]:
    bars = "".join(
        f'<div class="seg seg-{"hatch" if s.pattern == "HATCH" else "solid"} k-{esc(s.kind)}"'
        f' style="width:{s.width_permille / 10:.2f}%" title="{esc(s.label)}"></div>'
        for s in segments
    )
    legend = "".join(
        f'<li><span class="swatch {"seg-hatch" if s.pattern == "HATCH" else "seg-solid"}'
        f' k-{esc(s.kind)}"></span><span class="figure">'
        f'{esc(f"{s.count:,}" if s.count is not None else "not yet measured")}</span>'
        f"<span>{esc(band_mod.HUMAN[s.kind])}</span></li>"
        for s in segments
    )
    return bars, legend


def _open_items_markup(run: Any) -> str:
    from cdfc.surface.openitems import standing_open_items

    items = standing_open_items(run)
    if not items:
        # An EMPTY LIST IS RENDERED AS ONE. The section is never absent: an absent section is how
        # the panel's strongest row disappears silently.
        return '<tr><td colspan="2">no standing open item is recorded</td></tr>'
    return "".join(
        f"<tr><td>{esc(i.text)}</td><td>{esc(i.age)}</td></tr>" for i in items
    )


def render_report(run: Any, *, out: Path | None = None) -> ReportArtifact:
    """Render, assert, hash, write. **Raises rather than degrading.**"""
    if getattr(run, "closure_error", None):
        raise ClosureViolation(
            f"the run's closure does not hold: {run.closure_error}. There is no degraded report — "
            "a document whose counts do not add up is a document whose counts cannot be read."
        )

    sf = run.fraction
    h = hero_of(run)
    segments = band_mod.band_segments(sf, getattr(sf, "residue", None))
    bars, legend = _band_markup(segments)

    template = (TEMPLATE_DIR / "report.html").read_text(encoding="utf-8")
    html = fill(template, {
        "run_id": run.run_id,
        "run_state": run.run_state,
        "hero_left": LABEL_REGISTRY["hero.left"].template.format(F=f"{h.failures:,}",
                                                                S=f"{h.settled:,}"),
        "hero_right": LABEL_REGISTRY["hero.right"].template.format(U=f"{h.unchecked:,}"),
        "hero_admission": LABEL_REGISTRY["hero.admission"].template.format(A=h.admission),
        "hero_denominator": LABEL_REGISTRY["hero.denominator_rule"].template.format(
            R=sf.denominator.generatorRule),
        "admission_caveat": caveat(h.admission),
        "denominator_warning": sf.denominatorWarning,
        "settled_text": band_mod.settled_fraction_text(sf),
        "field_surface": f"{int(sf.cellsTotal):,}",
        "in_scope": f"{int(sf.inScope):,}",
        "subordinate": str(band_mod.subordinate_fraction(sf)),
        # `selection.active` — the predicates that RAN, not the registry's size. A report quoting
        # the registry would claim coverage from predicates that never bound to this filing.
        "n_predicates": f"{len(getattr(getattr(run, 'selection', None), 'active', ()) or ()):,}",
        "template_sha": run.template_sha256[:16],
        "filing_sha": run.filing_sha256[:16],
        "band_bars": Raw(bars),
        "band_legend": Raw(legend),
        "open_items": Raw(_open_items_markup(run)),
        "style": Raw(f"<style>\n{stylesheet()}\n</style>"),
    })

    assert_no_external_refs(html)

    # EVERY REQUIRED NUMBER MUST BE IN THE BYTES. The registry is the denominator of "renders every
    # number", and this is where the claim is checked against the artifact rather than the intent.
    missing = [n.id for n in REQUIRED_NUMBERS if n.extract(run) not in html]
    if missing:
        raise MissingRequiredNumber(
            f"{missing} are in REQUIRED_NUMBERS and do not appear in the rendered report. A number "
            "the registry says must be shown and is not shown is a number this report was supposed "
            "to carry."
        )

    rendered = frozenset(s.id for s in SURFACES if s.kind == "HTML")
    unknown = rendered - {s.id for s in SURFACES}
    if unknown:
        raise UnregisteredSurface(f"{sorted(unknown)} are not in SURFACES")

    data = html.encode("utf-8")
    target = out or (REPORTS_DIR / str(run.run_id) / "report.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return ReportArtifact(
        path=target, sha256=hashlib.sha256(data).hexdigest(), n_bytes=len(data),
        surfaces_rendered=rendered,
    )
