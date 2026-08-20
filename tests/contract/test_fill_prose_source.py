"""C4 — a PROSE source reaches the fill. `custodian feeds ... and PDF valuation packs` is ONE path.

`pipeline.run()` read delimited bytes and only delimited bytes, so a PDF-derived source could not
reach the fill at all: B3 made a PDF addressable and nothing consumed it. These tests pin the four
properties that make the prose path safe rather than merely present.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from cdfc.evidence.fields import from_template
from cdfc.fill.pipeline import run
from cdfc.qualify.instruments import deserialise
from cdfc.registry import ArtefactKind, Registry

REPO = Path(__file__).resolve().parents[2]
PINNED = REPO / "corpus/instruments/source-fincen-boir-instructions.text.json"
TEMPLATE = REPO / ("fixtures/prescribed/"
                   "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")

pytestmark = pytest.mark.skipif(not PINNED.is_file(), reason="the pinned PDF source is absent")


def _fixture(tmp: Path):
    it, _kind, _name, _sha = deserialise(PINNED.read_bytes())
    reg = Registry(tmp / "reg")
    td = reg.put(TEMPLATE.read_bytes(), kind=ArtefactKind.TEMPLATE, filename=str(TEMPLATE)).digest
    sd = reg.put(PINNED.read_bytes(), kind=ArtefactKind.SOURCE, filename=PINNED.name).digest
    return it, reg, td, sd


def _an_agreed_value(it) -> str:
    from cdfc.qualify.textsource import Corroboration

    for u in it.units:
        if u.corroboration is Corroboration.AGREED:
            words = it.slice(u.span).split()
            if len(words) >= 6:
                return " ".join(words[1:5])
    raise AssertionError("no AGREED unit with enough words")


def test_prose__a_pdf_value_fills_a_cell_and_is_EVIDENCED() -> None:
    """The positive path, end to end: PDF bytes -> pinned text -> located span -> a placed value."""
    with tempfile.TemporaryDirectory() as d:
        it, reg, td, sd = _fixture(Path(d))
        text_fields = [f for f in from_template(TEMPLATE).fields if f.type.value == "text"]
        assert text_fields, "the template declares no TEXT field; this test would prove nothing"
        value = _an_agreed_value(it)
        r = run(reg, template_digest=td, source_digest=sd, template_path=TEMPLATE,
                claims=[{"document": it.instrument_id, "field": text_fields[0].ref,
                         "value": value}])
        placed = r.declaration.counts()
        assert placed.get("proposed", 0) >= 1, (
            f"a value located byte-exact in a pinned PDF produced no fill: {placed}")
        assert not r.unlocatable, r.unlocatable


def test_prose__a_claim_naming_an_UNKNOWN_document_is_refused_not_guessed() -> None:
    """The defect this guards is the one A5 was corrected for: a span located against the WRONG
    document re-verifies on a coincidence. Falling back to 'the only source' would reintroduce it.
    """
    with tempfile.TemporaryDirectory() as d:
        it, reg, td, sd = _fixture(Path(d))
        r = run(reg, template_digest=td, source_digest=sd, template_path=TEMPLATE,
                claims=[{"document": "not-a-real-document", "field": "1. Introduction!D28",
                         "value": _an_agreed_value(it)}])
        assert len(r.unlocatable) == 1, "a claim naming no known document must not bind"
        assert "not-a-real-document" in r.unlocatable[0][1]


def test_prose__a_claim_whose_value_is_NOT_in_the_document_yields_no_observation() -> None:
    """A claim is a hint about where to look, never evidence that something is there."""
    with tempfile.TemporaryDirectory() as d:
        it, reg, td, sd = _fixture(Path(d))
        r = run(reg, template_digest=td, source_digest=sd, template_path=TEMPLATE,
                claims=[{"document": it.instrument_id, "field": "1. Introduction!D28",
                         "value": "this string is nowhere in the FinCEN instructions at all"}])
        assert len(r.unlocatable) == 1
        assert r.declaration.counts().get("proposed", 0) == 0


def test_prose__the_fill_lane_still_cannot_reach_the_model() -> None:
    """`cdfc.fill` is a VERDICT ROOT. The claims arrive as DATA; nothing here calls a provider."""
    from negative.importgraph import banned_in, import_closure, third_party_in

    closure = import_closure("cdfc.fill", src=REPO / "src")
    assert not any(m.startswith("cdfc.model") for m in closure), (
        "cdfc.fill reaches cdfc.model. The prose path must arrive as data, exactly as "
        "evidence.run takes its proposals as a file.")
    assert not banned_in(closure)
    assert not third_party_in(closure)
