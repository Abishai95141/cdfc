"""The link: stored artefacts -> bound evidence -> adjudicated fills, end to end."""

from __future__ import annotations

from pathlib import Path

import pytest

from cdfc.fill.pipeline import run
from cdfc.ingest.tabular import TabularError, header_and_rows, read_delimited
from cdfc.qualify.textsource import Corroboration
from cdfc.registry import ArtefactKind, Registry

TPL = Path("fixtures/synthetic/clean__template-computed__fme-q1.xlsx")
CSV = (
    b"Category of Registration of FME,Net worth,Number of investors\n"
    b"Registered FME (Retail),750000,1284\n"
)


@pytest.fixture
def reg(tmp_path):
    return Registry(root=tmp_path / "reg")


# --- the two-parser tabular ingest -----------------------------------------------------------


def test_tabular__two_parsers_agree_on_an_unambiguous_export():
    it = read_delimited(CSV, instrument_id="s")
    assert it.counts()["DISPUTED"] == 0
    assert it.counts()["units_total"] == 2
    # both parsers are OURS, so the corroboration is SAME_AUTHOR and never EXTERNAL
    assert it.agreement()["EXTERNAL"] == (0, 0)
    assert it.agreement()["SAME_AUTHOR"][1] == 2


def test_tabular__a_quoted_delimiter_DISPUTES_the_row_rather_than_guessing():
    """THE POINT OF THE SECOND PARSER. `csv.reader` respects the quotes and the naive splitter
    does not, so the row whose field boundaries depend on which you believed is excluded — not
    resolved in favour of whichever ran first."""
    data = b'name,amount\n"Fund A, Series II",750000\n'
    it = read_delimited(data, instrument_id="s")
    disputed = [u for u in it.units if u.corroboration is Corroboration.DISPUTED]
    assert len(disputed) == 1
    assert it.slice.__self__ is it  # sanity: the addressable API is present
    with pytest.raises(Exception):
        it.slice(disputed[0].span)      # a disputed span is not addressable


def test_tabular__refuses_an_empty_export_rather_than_returning_no_rows():
    with pytest.raises(TabularError, match="empty"):
        read_delimited(b"   \n", instrument_id="s")


def test_tabular__header_and_rows_uses_the_QUOTED_reading():
    header, rows = header_and_rows(b'a,b\n"x,y",2\n')
    assert header == ["a", "b"]
    assert rows == [["x,y", "2"]]


# --- the pipeline ----------------------------------------------------------------------------


def test_pipeline__binds_a_stored_source_to_a_stored_template_and_fills(reg):
    t = reg.put_file(TPL, kind=ArtefactKind.TEMPLATE)
    s = reg.put(CSV, kind=ArtefactKind.SOURCE, filename="custodian.csv")
    r = run(reg, template_digest=t.digest, source_digest=s.digest, template_path=TPL)

    assert r.schema_match.columns == 3
    admitted = r.declaration.admitted()
    assert len(admitted) == 1
    p = admitted[0]
    assert p.value == "Registered FME (Retail)"
    assert p.ref == "1. Introduction!D10"
    # THE SPAN IS REAL: it re-reads byte-exact out of the source document
    assert p.document.startswith("source:")
    assert all(c.holds for c in p.conditions)


def test_pipeline__every_proposed_value_is_LOCATED_in_the_source_it_cites(reg):
    """A binder could hand A5 a value and a field; `REVERIFIES` would then be unfalsifiable.

    `W0-C` had a similarity locator return SUPPORTED 20 of 20 on DELETED evidence, so a value that
    is not findable in the document it claims to come from produces NO observation at all.
    """
    t = reg.put_file(TPL, kind=ArtefactKind.TEMPLATE)
    s = reg.put(CSV, kind=ArtefactKind.SOURCE, filename="c.csv")
    r = run(reg, template_digest=t.digest, source_digest=s.digest, template_path=TPL)
    src = read_delimited(CSV, instrument_id=f"source:{s.digest[:12]}")
    for p in r.declaration.admitted():
        assert src.text[p.span[0]:p.span[1]] == p.value


def test_pipeline__refuses_to_read_a_FILING_as_evidence(reg):
    """Kind is declared, and binding a filing as evidence is a different operation."""
    t = reg.put_file(TPL, kind=ArtefactKind.TEMPLATE)
    s = reg.put(CSV, kind=ArtefactKind.FILING, filename="not-a-source.csv")
    with pytest.raises(ValueError, match="not 'source'"):
        run(reg, template_digest=t.digest, source_digest=s.digest, template_path=TPL)


def test_pipeline__records_the_merkle_root_over_its_own_two_inputs(reg):
    t = reg.put_file(TPL, kind=ArtefactKind.TEMPLATE)
    s = reg.put(CSV, kind=ArtefactKind.SOURCE, filename="c.csv")
    r = run(reg, template_digest=t.digest, source_digest=s.digest, template_path=TPL)
    assert r.merkle_root == reg.inputs([t.digest, s.digest]).merkle_root
    reg.put(b"unrelated", kind=ArtefactKind.SOURCE, filename="u.csv")
    again = run(reg, template_digest=t.digest, source_digest=s.digest, template_path=TPL)
    assert again.merkle_root == r.merkle_root


def test_pipeline__the_declaration_still_closes_over_the_whole_surface(reg):
    t = reg.put_file(TPL, kind=ArtefactKind.TEMPLATE)
    s = reg.put(CSV, kind=ArtefactKind.SOURCE, filename="c.csv")
    d = run(reg, template_digest=t.digest, source_digest=s.digest,
            template_path=TPL).declaration
    c = d.counts()
    assert c["proposed"] + c["refused"] + c["attestations"] == c["surface_total"]


def test_pipeline__carries_the_binding_provenance_into_the_declaration(reg):
    """A refusal that cannot say whose proposal it refused is not an audit record."""
    t = reg.put_file(TPL, kind=ArtefactKind.TEMPLATE)
    s = reg.put(CSV, kind=ArtefactKind.SOURCE, filename="c.csv")
    run(reg, template_digest=t.digest, source_digest=s.digest, template_path=TPL)
    # A TEST THAT CANNOT FAIL PROVES NOTHING. The first version of this assertion ended in
    # `or True`, which made it unfailable — the same defect shape as a gate whose control flips
    # no guard. It is now asserted where the provenance actually lives.
    import inspect

    from cdfc.fill import pipeline

    src = inspect.getsource(pipeline.run)
    assert "binding_provenance=" in src
    with pytest.raises(ValueError, match="provenance"):
        from cdfc.evidence.fields import from_template
        from cdfc.fill.propose import propose
        from cdfc.ingest.tabular import read_delimited

        propose(from_template(TPL), {}, read_delimited(CSV, instrument_id="s"),
                binding_provenance="")


# --- B2: multiple sources in one run ----------------------------------------------------------

BLANK = Path(
    "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)
ENTITY = (b"Category of Registration of FME,Legal Structure of FME,Date of Registration of FME,"
          b"PAN of FME,Address of FME\n"
          b"Registered FME (Retail),Company,2025-04-01,AABCF1234K,Unit 402 GIFT City\n")
OFFICERS = (b"Name of the Principal Officer,Email address of the Principal Officer,"
            b"Contact no. of the Principal Officer\n"
            b"Asha Rao,asha.rao@example.com,+91 79 4000 1234\n")


@pytest.fixture
def two_sources(reg):
    if not BLANK.is_file():
        pytest.skip("the vendored FME blank is not in this checkout")
    t = reg.put_file(BLANK, kind=ArtefactKind.TEMPLATE)
    a = reg.put(ENTITY, kind=ArtefactKind.SOURCE, filename="entity-master.csv")
    b = reg.put(OFFICERS, kind=ArtefactKind.SOURCE, filename="officers.csv")
    return reg, t, a, b


def test_b2__two_documents_are_bound_in_ONE_run(two_sources):
    reg, t, a, b = two_sources
    r = run(reg, template_digest=t.digest, source_digest=[a.digest, b.digest],
            template_path=BLANK)
    assert r.source_digests == (a.digest, b.digest)
    assert r.schema_match.columns == 8          # 5 + 3, from both documents
    # values from BOTH documents reach the return
    docs = {p.document for p in r.declaration.admitted()} | {
        d.supported_by[0] for d in r.declaration.derived if d.supported_by}
    assert len(docs) == 2, f"only {docs} contributed; a source was silently dropped"


def test_b2__an_observation_re_verifies_against_ITS_OWN_document(two_sources):
    """THE MULTI-SOURCE DEFECT THIS FIXES.

    A5 took one `InstrumentText` and re-read every span in it, so every observation from the
    SECOND document failed REVERIFIES — not because the span was wrong but because it was re-read
    in the wrong file. Five correctly-bound fields were refused as unverifiable.

    Worse than losing them: a span from document A re-read in document B could match by
    coincidence and would then PASS. Re-verifying against the wrong document is not a weaker
    check, it is a check of something else.
    """
    reg, t, a, b = two_sources
    r = run(reg, template_digest=t.digest, source_digest=[a.digest, b.digest],
            template_path=BLANK)
    from cdfc.ingest.tabular import read_delimited

    texts = {f"source:{a.digest[:12]}": read_delimited(ENTITY, instrument_id=f"source:{a.digest[:12]}"),
             f"source:{b.digest[:12]}": read_delimited(OFFICERS, instrument_id=f"source:{b.digest[:12]}")}
    for p in r.declaration.admitted():
        src = texts[p.document]
        assert src.text[p.span[0]:p.span[1]] == p.value


def test_b2__an_observation_naming_an_unread_document_is_REFUSED(reg):
    """A span this run cannot re-read is refused, not re-verified somewhere else."""
    from cdfc.evidence.fields import Field, FieldSet, LabelRule
    from cdfc.evidence.observe import Observation
    from cdfc.evidence.vocabulary import Asks, FieldType
    from cdfc.fill.propose import FillRefusal, propose
    from cdfc.ingest.tabular import read_delimited

    src = read_delimited(b"a,b\nx,1\n", instrument_id="known")
    f = Field(ref="S!A1", label="L", type=FieldType.TEXT, asks=Asks.FACT)
    fs = FieldSet(template_sha256="t" * 64, surface_total=1, label_rule=list(LabelRule)[0],
                  fields=(f,), surface=frozenset({"S!A1"}))
    ghost = Observation(value="x", document="a-document-this-run-never-read", span=(0, 1),
                        page=1, context="")
    d = propose(fs, {"S!A1": (ghost,)}, {src.instrument_id: src}, binding_provenance="p")
    assert d.refused[0].reason is FillRefusal.REVERIFICATION_FAILED
    assert "did not read" in d.refused[0].detail


def test_b2__the_binder_ignores_stopwords(two_sources):
    """`of` occurs in 73 of 132 FME labels and `the` in 45. As a binary evidence bit, a match on
    `of` was indistinguishable from a match on `investors`, and the binder scored 1 of 3."""
    from cdfc.correspond.schema import STOPWORDS, _tokens

    assert "of" in STOPWORDS and "the" in STOPWORDS
    assert _tokens("Number of investors") & _tokens("Category of Registration of FME") == frozenset()
    reg, t, a, b = two_sources
    r = run(reg, template_digest=t.digest, source_digest=[a.digest, b.digest],
            template_path=BLANK)
    assert len(r.schema_match.pairs) == r.schema_match.columns   # all 8 bind


def test_b2__an_undeclared_type_is_DERIVED_not_refused(two_sources):
    """92 of 124 FACT fields on this return declare no type. Refusing them capped the product at
    32 fillable cells because the WORKBOOK is sloppy. They are placed, and labelled derived."""
    reg, t, a, b = two_sources
    r = run(reg, template_digest=t.digest, source_digest=[a.digest, b.digest],
            template_path=BLANK)
    assert r.declaration.counts()["derived"] > 0
    # every derived cell still had a real, located observation behind it
    for d in r.declaration.derived:
        assert d.supported_by and d.supported_by[0].startswith("source:")
        assert "no type" in d.basis
    # and none of them is counted as checked
    assert set(x.ref for x in r.declaration.derived).isdisjoint(
        x.ref for x in r.declaration.admitted())
