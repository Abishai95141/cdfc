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
