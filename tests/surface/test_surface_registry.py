"""The surface registry — **the gate divides by it, and this build writes it.**

That is M1, this plan's founding defect, sitting inside the gate meant to prevent it. A surface
that cannot be made to pass SG1-SG4 can be deleted from `SURFACES` and the exit gate goes green
with the negative-control sweep still reporting `caught == active` — the sweep catches a surface
that renders through a known path, not one **removed from the register**.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.labels import (  # noqa: E402
    REQUIRED_NUMBERS, SURFACES, SurfaceSpec, live_surfaces, scanned_surfaces,
)

LOG = REPO / "docs" / "SURFACE-REGISTRY-LOG.md"


def _logged_ids() -> set[str]:
    """The ids recorded in the growth log's fenced block."""
    text = LOG.read_text(encoding="utf-8")
    block = text.split("```")[1]
    return {ln.strip() for ln in block.splitlines() if ln.strip() and not ln.startswith("#")}


def test_surface__registry_is_append_only() -> None:
    """Diffed against the LOG, not against a previous commit — so the check survives a squash.

    An id that was in the registry and is no longer in it has been deleted, and deletion is how the
    gate's denominator shrinks to meet its numerator.
    """
    assert LOG.is_file(), "the growth log is missing; append-only would be unenforceable"
    logged, current = _logged_ids(), {s.id for s in SURFACES}
    missing = sorted(logged - current)
    assert missing == [], (
        f"{missing} were in the registry and are gone. A row may be RETIRED with a dated argument "
        "and never deleted: a retired row keeps its entry and leaves only the gate's denominator."
    )


def test_surface__gate_floor_is_the_logged_cardinality() -> None:
    """`len(SURFACES)` may grow and may never fall below what the log records."""
    assert len(SURFACES) >= len(_logged_ids())


def test_surface__retired_rows_are_still_scanned() -> None:
    """A surface we gave up AUDITING is not a surface we gave up PROHIBITING an affirmative claim on.

    Retirement removes a row from the gate's denominator. It must not remove it from the scan.
    """
    assert {s.id for s in scanned_surfaces()} == {s.id for s in SURFACES}
    assert {s.id for s in live_surfaces()} <= {s.id for s in scanned_surfaces()}


def test_surface__a_retirement_with_a_dated_argument_is_accepted() -> None:
    """THE ADMISSION-SIDE CONTROL.

    Without it, "append-only" is satisfiable by a rule that forbids every change — and a registry
    that can never be corrected is its own problem. A retirement carrying both a date and a reason
    must construct.
    """
    s = SurfaceSpec("S99.example", "HTML", frozenset({"NONE"}), "x",
                    retired_on="2026-08-15", retired_because="superseded by S02")
    assert s.retired and s.id not in {x.id for x in live_surfaces()}


def test_surface__a_retirement_without_an_argument_is_refused() -> None:
    """A row retired with no reason is a row deleted with extra steps."""
    with pytest.raises(ValueError, match="BOTH a date and an argument"):
        SurfaceSpec("S98.x", "HTML", frozenset({"NONE"}), "x", retired_on="2026-08-15")


def test_surface__the_log_records_the_cardinality_over_time() -> None:
    """`|SURFACES|` per commit, so a registry that shrinks the day before a gate is read is
    visible in the artifact the gate is read from."""
    text = LOG.read_text(encoding="utf-8")
    rows = re.findall(r"^\| \d{4}-\d{2}-\d{2} \| *(\d+) \|", text, re.M)
    assert rows, "the log carries no dated cardinality row"
    assert int(rows[-1]) <= len(SURFACES)


def test_surface__required_numbers_all_name_a_registered_surface() -> None:
    """A number required on a surface nobody registered is required nowhere."""
    ids = {s.id for s in SURFACES}
    for n in REQUIRED_NUMBERS:
        assert set(n.surfaces) <= ids, f"{n.id} names {set(n.surfaces) - ids}"


def test_surface__both_registries_are_non_empty() -> None:
    """The admission-side control for the two tests above: deleting every row would satisfy them."""
    assert len(SURFACES) >= 5 and len(REQUIRED_NUMBERS) >= 5


def test_surface__residue_section_always_present() -> None:
    """The residue section renders whether or not the residue has been measured.

    An absent section is how the panel's strongest row disappears silently: a reader who does not
    see it concludes there is nothing to see, and there is no way to tell that from a section that
    was never rendered. Only its CONTENTS are pending.
    """
    from pathlib import Path as _P

    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED
    from cdfc.surface.render import render_report

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        html = render_report(run_filing(TEMPLATE_COMPUTED),
                             out=_P(d) / "r.html").path.read_text(encoding="utf-8")
    assert "demonstrated survivors" in html, "the residue section is absent from the report"
    assert "residue not yet measured" in html, "its unmeasured state does not render"
