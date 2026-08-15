"""The rendered artifact: self-contained, deterministic, and structurally unable to omit a number."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.admission import admission_state, caveat  # noqa: E402
from cdfc.surface.inline import ExternalReference, assert_no_external_refs  # noqa: E402
from cdfc.surface.labels import REQUIRED_NUMBERS, render_ffr  # noqa: E402
from cdfc.surface.render import Hero, render_report  # noqa: E402


def _run():
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED

    return run_filing(TEMPLATE_COMPUTED)


def test_render__hero_without_an_admission_state_is_unconstructible() -> None:
    """Criterion A11 as a TYPE rather than a convention: a settled count cannot exist on this
    surface without the admission state of the predicate set that produced it."""
    with pytest.raises(TypeError):
        Hero(failures=0, settled=1, unchecked=2)          # type: ignore[call-arg]
    assert Hero(failures=0, settled=1, unchecked=2, admission="PRE-GATE").admission == "PRE-GATE"


def test_render__the_report_reaches_outside_itself_for_nothing(tmp_path: Path) -> None:
    """It opens from `file://` with the network down. A file has a hash; an SPA does not."""
    html = render_report(_run(), out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    assert "<link" not in html.lower()
    assert "http://" not in html and "https://" not in html
    assert_no_external_refs(html)


def test_render__an_external_reference_is_refused() -> None:
    """THE GUARD, exercised — otherwise the test above only proves this artifact happens to be clean."""
    for bad in ('<link rel="stylesheet" href="https://cdn/x.css">',
                '<img src="/logo.png">',
                '<script>fetch("/api")</script>',
                '<style>@import url(x.css)</style>'):
        with pytest.raises(ExternalReference):
            assert_no_external_refs(bad)


def test_render__is_byte_identical_across_renders(tmp_path: Path) -> None:
    """The report is the attested artifact, so its bytes are the thing that gets hashed."""
    run = _run()
    a = render_report(run, out=tmp_path / "a.html")
    b = render_report(run, out=tmp_path / "b.html")
    assert a.sha256 == b.sha256 and a.n_bytes == b.n_bytes


def test_render__every_required_number_appears_in_the_bytes(tmp_path: Path) -> None:
    """The registry is the denominator of *renders every number*, and this checks the claim
    against the artifact rather than against the intention."""
    run = _run()
    html = render_report(run, out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    missing = [n.id for n in REQUIRED_NUMBERS if n.extract(run) not in html]
    assert missing == []


def test_render__the_two_hero_counts_are_both_present(tmp_path: Path) -> None:
    """1,898 settled and 1,849 unchecked. The second is the one a competitor would not show."""
    html = render_report(_run(), out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    assert "1,898" in html and "1,849" in html


def test_render__the_admission_state_and_its_caveat_travel_together(tmp_path: Path) -> None:
    run = _run()
    html = render_report(run, out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    state = admission_state(run)
    assert state == "PRE-GATE", "the reference run is PRE-GATE; G-CORPUS is on its FAIL branch"
    assert state in html and caveat(state)[:40] in html


def test_render__the_denominator_warning_is_on_the_page(tmp_path: Path) -> None:
    """The denominator is PROVISIONAL-UNVALIDATED and the page has to say so — a count whose
    denominator nobody validated is a count with an unstated assumption."""
    html = render_report(_run(), out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    assert "PROVISIONAL-UNVALIDATED" in html


def test_render__ffr_refuses_a_digit_in_all_three_uninformative_cases() -> None:
    class SelfAuthored:
        corpus_provenance, false_failure_rate, n = "SELF-AUTHORED", "0/30", 30
        clean_corpus_independent_of_predicate = True

    class NotIndependent:
        corpus_provenance, false_failure_rate, n = "REGISTER-DERIVED", "0/30", 30
        clean_corpus_independent_of_predicate = False

    for q in (None, SelfAuthored(), NotIndependent()):
        cell = render_ffr(q)
        assert cell.text == "uninformative" and not cell.digits


def test_render__an_admissible_ffr_still_prints_its_digits_and_its_n() -> None:
    """THE ADMISSION-SIDE TWIN. Without it, `render_ffr` could return `uninformative` for
    everything and score perfectly on the three refusals above."""
    class Admissible:
        corpus_provenance, false_failure_rate, n = "REGISTER-DERIVED", "0", 30
        clean_corpus_independent_of_predicate = True

    cell = render_ffr(Admissible())
    assert cell.digits and "30" in cell.text


def test_render__no_banned_token_reaches_the_rendered_report(tmp_path: Path) -> None:
    """SG1's rendered arm, and it catches something the SOURCE grep cannot.

    `ci/no-green-tick.sh` scans `src/cdfc/surface/`. It cannot see a banned phrase that arrives
    **through data** — `openitems.py` reads `docs/OPEN-ITEMS.md`, which is outside every scan root,
    and renders its contents onto the page. A phrase planted there reaches a reader while every
    source gate stays green.
    """
    from cdfc.surface.labels import banned_tokens

    html = render_report(_run(), out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    body = html.split("</style>", 1)[-1].lower()
    hits = sorted({t for t in banned_tokens() if t.lower() in body})
    assert hits == [], f"banned tokens reached the rendered report through data: {hits}"


def test_render__the_open_items_section_is_never_absent(tmp_path: Path) -> None:
    """THE ADMISSION-SIDE CONTROL for the test above: the section renders real items, so the
    absence of a banned token is not the absence of the section."""
    html = render_report(_run(), out=tmp_path / "r.html").path.read_text(encoding="utf-8")
    assert "Standing open items" in html
    assert "clean corpus is not funded" in html, "the open items are not reaching the page"
