"""LAYER 2, claim extraction. NO NETWORK: every test supplies a transport.

The subject is not extraction quality. It is that the SPAN is computed here, that a claim whose
evidence the document does not contain yields nothing, and that neither failure is silent.
"""

from __future__ import annotations

import json

import pytest

from cdfc.model.extract import extract, label_binding, locate, parse
from cdfc.model.propose import ProposerError
from cdfc.qualify.textsource import Extraction, Unit, build

LINES = ["The net worth of the FME as at the reporting date is 7,50,000 as certified.",
         "Assets under management total 12,40,00,000 at period end."]


def _src(lines=LINES):
    units = tuple(Unit(key=f"r{i:04d}", text=t, page=1) for i, t in enumerate(lines))
    return build("src", [Extraction(extractor=n, version="1", external=False, units=units,
                                    blind_to={}) for n in ("a", "b")])


def _reply(claims):
    return {"content": [{"type": "text", "text": json.dumps({"claims": claims})}]}


def test_extract__returns_candidates_with_no_span():
    """The model supplies evidence, never an offset. An offset it supplied is a number nobody
    checked, and W0-C measured what trusting one costs."""
    cs = extract(_src(), transport=lambda _p: _reply([
        {"value": "7,50,000", "label": "net worth", "evidence": LINES[0]}]))
    c = cs.claims[0]
    assert c.value == "7,50,000"
    assert not hasattr(c, "span") and not hasattr(c, "offset")


def test_extract__refuses_a_value_that_is_not_inside_its_own_evidence():
    cs = extract(_src(), transport=lambda _p: _reply([
        {"value": "9,99,999", "label": "net worth", "evidence": LINES[0]}]))
    assert cs.claims == ()
    assert "the search returned no match" in cs.malformed[0]


def test_locate__computes_the_span_and_it_re_reads_exactly():
    src = _src()
    cs = extract(src, transport=lambda _p: _reply([
        {"value": "7,50,000", "label": "net worth", "evidence": LINES[0]}]))
    obs, lost = locate(cs, src)
    assert lost == () and len(obs) == 1
    o = obs[0]
    assert src.text[o.span[0]:o.span[1]] == "7,50,000"
    assert o.reverify(src) is True                    # A5's trigger passes on a real span


def test_locate__a_fabricated_evidence_sentence_yields_NO_observation():
    """THE SAFETY PROPERTY, and it does not depend on the model being careful."""
    src = _src()
    cs = extract(src, transport=lambda _p: _reply([
        {"value": "7,50,000", "label": "net worth",
         "evidence": "The net worth of the FME is 7,50,000 per the auditor's opinion."}]))
    assert len(cs.claims) == 1                        # it parsed
    obs, lost = locate(cs, src)                       # and located nothing
    assert obs == ()
    assert "evidence_not_located" in lost[0]


def test_locate__refuses_a_span_inside_a_disputed_region():
    """The readers disagree there, so a re-read returns the sentinel, not the value."""
    data = b'name,amount\n"Fund A, Series II",750000\n'
    from cdfc.ingest.tabular import read_delimited
    src = read_delimited(data, instrument_id="s")
    from cdfc.model.extract import ClaimCandidate, ClaimSet
    cs = ClaimSet(claims=(ClaimCandidate(value="750000", label="amount",
                                         evidence='Fund A, Series II | 750000', model="m",
                                         index=0),), model="m", document="s",
                  chars_offered=len(src.text), raw_blocks=1)
    obs, lost = locate(cs, src)
    assert obs == () and lost


def test_extract__unparseable_reply_raises_rather_than_reporting_an_empty_document():
    with pytest.raises(ProposerError, match="not JSON"):
        parse("The net worth is 7,50,000.", model="m", document="d", chars_offered=10)


def test_extract__refuses_an_empty_source():
    units = (Unit(key="r0", text="x", page=1),)
    src = build("s", [Extraction(extractor=n, version="1", external=False, units=units,
                                 blind_to={}) for n in ("a", "b")])
    object.__setattr__(src, "text", "   ")
    with pytest.raises(ProposerError, match="was shown nothing"):
        extract(src, transport=lambda _p: _reply([]))


def test_label_binding__is_crude_and_declared_so():
    """A weak binder costs COVERAGE and cannot cost correctness — A5's six conditions see to that."""
    from cdfc.evidence.fields import from_template
    from pathlib import Path

    src = _src()
    cs = extract(src, transport=lambda _p: _reply([
        {"value": "7,50,000", "label": "net worth", "evidence": LINES[0]}]))
    obs, _ = locate(cs, src)
    fs = from_template(Path("fixtures/synthetic/clean__template-computed__fme-q1.xlsx"))
    b = label_binding(cs, obs, fs)
    assert isinstance(b, dict)
    for refs in b.values():
        assert all(o.reverify(src) for o in refs)     # only located observations are ever bound
