"""P7-B2 — the proviso marker detector, and the refusal that follows from an unmeasured recall."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.provisos import (  # noqa: E402
    LABELS_PATH,
    MARKERS,
    MARKERS_VERSION,
    ProvisoRecallUnmeasured,
    assert_measured_for_statute,
    detect,
    recall,
)

LABELS = REPO / LABELS_PATH


def test_provisos__each_marker_fires_on_its_exemplar():
    """Table-driven over all fifteen markers. A marker with no exemplar is a pattern nobody has
    seen match anything."""
    assert len(MARKERS) == 15
    for m in MARKERS:
        hits = detect(m.exemplar, 0)
        assert any(d.marker == m.pattern for d in hits), (
            f"{m.pattern} did not match its own exemplar {m.exemplar!r}"
        )
        assert all(d.kind == m.kind for d in hits if d.marker == m.pattern)


def test_provisos__spans_are_absolute():
    """A proviso reported at a span relative to its clause is a span a reader cannot open."""
    text = "Provided that the scheme is close-ended"
    d = detect(text, 5000)[0]
    assert d.span == (5000, 5013)
    assert d.text == "Provided that"


def test_provisos__offset_has_no_default():
    with pytest.raises(TypeError):
        detect("Provided that x")  # type: ignore[call-arg]


def test_provisos__the_three_provisos_do_not_collapse():
    """`Provided that`, `Provided further that` and `Provided also that` are three facts. A clause
    carrying all three has three provisos, and collapsing them would under-count exactly the
    structure G0 exists to check."""
    text = ("Provided that a is so. Provided further that b is so. Provided also that c is so.")
    kinds = [d.text.lower() for d in detect(text, 0) if d.kind == "proviso"]
    assert sorted(kinds) == ["provided also that", "provided further that", "provided that"]


def test_provisos__the_reg_51_delegation_hook_is_detected_and_typed():
    """R-GOLD-2 value assertion. The delegation is the case where the obligation is GENUINELY
    UNDERSPECIFIED, and its output is `NO_PREDICATE(no_obligation_specified)` — kept strictly
    apart from `not_yet_synthesised`."""
    text = "The net asset value shall be computed in such manner as specified by the Authority."
    hits = [d for d in detect(text, 0) if d.kind == "delegation"]
    assert hits, "the reg 51(1) delegation hook was not detected"
    assert any(d.text.lower() == "in such manner as specified by the authority" for d in hits)


def test_provisos__cross_references_carry_their_number():
    hits = {d.text for d in detect("as required by regulation 51 and sub-regulation (2)", 0)}
    assert "regulation 51" in hits
    assert "sub-regulation (2)" in hits


def test_provisos__an_unknown_marker_version_raises():
    """`MARKERS_VERSION` enters `qualification.g0`. A predicate qualified under one list is not
    silently re-qualified under another."""
    assert MARKERS_VERSION == "v1"
    with pytest.raises(ValueError, match="not the pinned version"):
        detect("Provided that x", 0, markers_version="v2")


# --- recall ------------------------------------------------------------------------------


def test_provisos__recall_is_two_integers_and_a_provenance():
    r = recall(LABELS)
    assert (r.detected, r.labelled) == (0, 0)
    assert not r.measured
    assert r.labeller is None and r.labelled_at is None
    line = r.render()
    assert "NOT MEASURED" in line
    assert "0 / 0" in line, "even an unmeasured recall renders both integers"
    # **THIS ASSERTION USED TO REQUIRE A FALSE SENTENCE.** It pinned the words *"no statutory
    # instrument is pinned"* — the D-P7-01 reason — long after S1 pinned the FM Regulations, so
    # correcting the reason turned the suite red and the falsehood became a build requirement. It
    # now pins the PROPERTY the render must carry: the recall is unmeasured, and the sentence says
    # what would measure it. The specific blocker may move again; that it must be named may not.
    low = line.lower()
    assert "labelled span" in low or "labeller" in low, (
        "an unmeasured recall must name what would measure it — labelled spans and who recorded "
        "them — rather than merely reporting that it is unmeasured"
    )
    assert "no statutory instrument is pinned" not in low, (
        "the stale D-P7-01 reason is back; corpus/instruments/MANIFEST.json carries "
        "statute-fm-regulations-2025"
    )


def test_provisos__a_statute_candidate_is_refused_while_recall_is_unmeasured():
    """THE TEETH. A detector whose recall nobody has measured cannot tell 'this clause has no
    proviso' from 'we did not see the proviso it has', and the first is what G0 is asking."""
    with pytest.raises(ProvisoRecallUnmeasured, match="unmeasured"):
        assert_measured_for_statute(LABELS)


def test_provisos__a_labelled_set_makes_the_refusal_stop(tmp_path):
    """ADMISSION-SIDE TWIN. Without it the refusal is indistinguishable from a gate that refuses
    every statutory candidate for ever."""
    import json

    p = tmp_path / "labels.json"
    p.write_text(json.dumps({
        "markers_version": "v1",
        "labeller": "A. Reader",
        "labelled_at": "2026-08-13",
        "spans": [
            {"text": "Provided that the scheme is close-ended", "kind": "proviso"},
            {"text": "Notwithstanding anything contained in regulation 12", "kind": "exception"},
            {"text": "a sentence with no marker at all in it", "kind": "proviso"},
        ],
    }), encoding="utf-8")
    r = assert_measured_for_statute(p)
    assert (r.detected, r.labelled) == (2, 3), (
        "the third span carries no marker, so the detector misses it — and a MISS is the finding "
        "this measurement exists to publish"
    )
    assert r.measured
    assert "2 / 3" in r.render() and "A. Reader" in r.render()
    assert "NOT MEASURED" not in r.render()


def test_provisos__a_labelled_set_without_a_named_person_is_not_measured(tmp_path):
    """A recall figure with no name and no date is a number somebody produced and nobody stands
    behind."""
    import json

    p = tmp_path / "labels.json"
    p.write_text(json.dumps({
        "labeller": None, "labelled_at": None,
        "spans": [{"text": "Provided that x", "kind": "proviso"}],
    }), encoding="utf-8")
    assert not recall(p).measured
    with pytest.raises(ProvisoRecallUnmeasured):
        assert_measured_for_statute(p)


def test_provisos__the_committed_labels_file_says_why_it_is_empty():
    import json

    doc = json.loads(LABELS.read_text(encoding="utf-8"))
    assert doc["spans"] == []
    assert "D-P7-01" in doc["reason_if_absent"]
    assert doc["how_to_fill_this"], "an empty file with no instructions is an empty file"
