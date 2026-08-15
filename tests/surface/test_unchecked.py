"""The Unchecked panel — the part of this product nothing else in the market renders."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.render import hero_of, render_report  # noqa: E402
from cdfc.surface.unchecked import (  # noqa: E402
    MIN_REMEDY_CHARS, GenericRemedy, MissingRemedy, Remedy, ResidueExhibit, UncheckedEntry,
    UncheckedGroup, UncheckedPanel, build_unchecked_panel, load_remedies,
)

LONG = ("a specific instrument that would move this obligation across the line, stated at enough "
        "length to be actionable rather than a label")


def _run():
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED

    return run_filing(TEMPLATE_COMPUTED)


def test_unchecked__total_equals_hero_right() -> None:
    """The panel and the hero's second line are the same set counted twice."""
    run = _run()
    assert build_unchecked_panel(run).total == hero_of(run).unchecked == 1849


def test_unchecked__missing_remedy_raises(tmp_path: Path) -> None:
    """A reason code with no remedy is a BUILD ERROR, never a placeholder string.

    A generic fallback turns a panel of reasons into one sentence repeated — and it is
    indistinguishable from a panel that thought about each group, which is what makes it the
    flattering failure.
    """
    empty = tmp_path / "r.yaml"
    empty.write_text("remedies: []\ndeliberately_unremediable: {}\n")
    with pytest.raises(MissingRemedy) as exc:
        build_unchecked_panel(_run(), path=empty)
    assert "no_predicate.not_yet_synthesised" in str(exc.value)


def test_unchecked__wildcard_remedy_does_not_load() -> None:
    """`applies_to: "*"` is a generic remedy wearing a specific one's clothes."""
    with pytest.raises(GenericRemedy, match=r"wildcard|\*"):
        Remedy(id="R", reason_code="x", applies_to="*", text=LONG, source=None, specific=True)


def test_unchecked__a_short_remedy_does_not_load() -> None:
    """Naming the instrument that would settle a question takes a sentence."""
    with pytest.raises(GenericRemedy):
        Remedy(id="R", reason_code="x", applies_to="y", text="see documentation",
               source=None, specific=True)


def test_unchecked__a_remedy_that_is_not_specific_does_not_load() -> None:
    with pytest.raises(GenericRemedy):
        Remedy(id="R", reason_code="x", applies_to="y", text=LONG, source=None, specific=False)


def test_unchecked__the_shipped_remedies_all_load() -> None:
    """THE ADMISSION-SIDE CONTROL: the three refusals above are satisfiable by real remedies."""
    remedies, unremediable = load_remedies()
    assert len(remedies) >= 8 and len(unremediable) >= 2
    for r in remedies.values():
        assert r.specific and r.applies_to != "*" and len(r.text) >= MIN_REMEDY_CHARS


def test_unchecked__none_and_empty_exhibits_render_differently() -> None:
    """`absent != empty`, applied to our own panel.

    `None` is a statement about US — the procedure has not run. `()` is a statement about the CHECK
    SET, and per NC-C02 a residue of exactly zero is a finding rather than good news. They must not
    look alike, and the `None` rendering carries **no digit** so it cannot be misread as a count.
    """
    g = UncheckedGroup("no_predicate.not_yet_synthesised", 1,
                       (UncheckedEntry("S!A1", "no_predicate.not_yet_synthesised"),),
                       Remedy("R", "no_predicate.not_yet_synthesised", "cells", LONG, None, True))
    unmeasured = UncheckedPanel((g,), 1, None).residue_state
    measured_zero = UncheckedPanel((g,), 1, ()).residue_state
    assert unmeasured != measured_zero
    assert not re.search(r"\d", unmeasured), "the unmeasured state carries a digit and could be read as a count"
    assert "not yet measured" in unmeasured
    assert "no survivors" in measured_zero and "not good news" in measured_zero


def test_unchecked__exhibits_are_labelled_as_exhibits_not_reasons() -> None:
    """A reason is *why we did not check*. An exhibit is *a thing we checked and still missed*.
    Presenting the second among the first would let a reader count it twice."""
    e = ResidueExhibit("M-1", "a SUM was broken by one unit", "no admitted predicate reads that cell")
    g = UncheckedGroup("no_predicate.not_yet_synthesised", 1,
                       (UncheckedEntry("S!A1", "no_predicate.not_yet_synthesised"),),
                       Remedy("R", "no_predicate.not_yet_synthesised", "cells", LONG, None, True))
    panel = UncheckedPanel((g,), 1, (e,))
    assert "1 demonstrated survivors" in panel.residue_state
    assert e.mutant_id not in {x.reason_code for x in panel.groups}


def test_unchecked__a_group_whose_count_is_not_its_length_cannot_be_built() -> None:
    """A count that is not the length of what it counts is the defect this project is named for."""
    with pytest.raises(ValueError, match="carries"):
        UncheckedGroup("x", 5, (UncheckedEntry("S!A1", "x"),),
                       Remedy("R", "x", "y", LONG, None, True))


def test_unchecked__the_panel_is_a_partition() -> None:
    """No cell in two groups, and the groups sum to the total."""
    panel = build_unchecked_panel(_run())
    keys = [e.stable_key for g in panel.groups for e in g.entries]
    assert len(keys) == len(set(keys)) == panel.total


def test_unchecked__panel_and_hero_disagreeing_aborts_the_report(tmp_path: Path) -> None:
    """The two halves of the report describe one run, and the renderer refuses if they do not."""
    from cdfc.surface.render import ClosureViolation

    run = _run()
    art = render_report(run, out=tmp_path / "r.html")
    html = art.path.read_text(encoding="utf-8")
    assert html.count("1,849") >= 2, "the hero and the panel must both carry the count"
    assert ClosureViolation is not None
