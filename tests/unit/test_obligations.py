"""P7-B1 — the obligations table, and arbitration C2's two-number rule."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.obligations import (  # noqa: E402
    NO_STATUTORY_PREDICATE,
    Obligation,
    ObligationError,
    ObligationSource,
    ObligationTable,
    UnpairedObligationCount,
    assert_pair_rendered,
    generate_template_obligations,
    load,
)
from cdfc.qualify.instruments import CORPUS, InstrumentStore  # noqa: E402
from cdfc.qualify.template_instrument import emit  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


@pytest.fixture(scope="module")
def fme():
    r = harvest(FME)
    it = emit(FME)
    return r, it, generate_template_obligations(r, it)


# --- the row -----------------------------------------------------------------------------


def test_obligations__span_matches_quote(fme):
    """For every row, `instrument_text[span] == quote`, resolved against the row's OWN instrument.
    A row that does not is a data error and fails at load."""
    _r, it, tbl = fme
    for oid, o in tbl.rows.items():
        assert o.instrument_id == it.instrument_id
        assert it.text[o.span[0] : o.span[1]] == o.quote, oid


def test_obligations__ids_are_stable_across_ingest_source_flip(fme):
    """`ingest_source` records HOW THE ROW GOT HERE. Changing it — and populating `eId` — must
    not move a single `obligation_id`, because the id is a foreign key from every envelope."""
    _r, _it, tbl = fme
    flipped = {
        oid: Obligation(
            obligation_id=o.obligation_id, source=o.source, instrument_id=o.instrument_id,
            frbr_uri=o.frbr_uri, eId="reg_51__subreg_1", quote=o.quote, span=o.span,
            ingest_source="l1b",
        )
        for oid, o in tbl.rows.items()
    }
    assert set(flipped) == set(tbl.rows)


def test_obligations__source_is_required_and_closed():
    """F9 / C2. Two members, no default, no None; and `source` and `ingest_source` are DISTINCT
    fields neither of which is derived from the other."""
    assert [s.value for s in ObligationSource] == ["STATUTE", "TEMPLATE"]

    base = dict(obligation_id="OBL-X", instrument_id="template-7d9a1960", frbr_uri=None,
                eId=None, quote="q", span=(0, 1), ingest_source="harvest")
    with pytest.raises(ObligationError, match="must be an ObligationSource"):
        Obligation(source="TEMPLATE", **base)  # type: ignore[arg-type]

    # source=TEMPLATE  =>  frbr_uri is None AND instrument_id is a pinned blank
    with pytest.raises(ObligationError, match="no FRBR URI"):
        Obligation(**{**base, "source": ObligationSource.TEMPLATE, "frbr_uri": "/akn/in/act/2025"})
    with pytest.raises(ObligationError, match="is not one"):
        Obligation(**{**base, "source": ObligationSource.TEMPLATE, "instrument_id": "fm-2025"})
    # and the reverse direction, which is the one C2 exists to prevent
    with pytest.raises(ObligationError, match="one direction C2 exists to prevent"):
        Obligation(**{**base, "source": ObligationSource.STATUTE})

    with pytest.raises(ObligationError, match="ingest_source"):
        Obligation(**{**base, "source": ObligationSource.TEMPLATE, "ingest_source": "guessed"})


def test_obligations__a_row_naming_an_absent_instrument_is_refused(tmp_path):
    """D-P7-01. While the statutory corpus is empty a STATUTE row cannot enter the funnel by
    resolving against nothing — it does not resolve at all."""
    p = tmp_path / "obligations.yaml"
    p.write_text(
        "obligations:\n"
        "  - obligation_id: OBL-014\n"
        "    source: STATUTE\n"
        "    instrument_id: fm-regulations-2025\n"
        "    eId: reg_51__subreg_1\n"
        "    quote: 'the Authority may specify'\n"
        "    span: [10, 34]\n"
        "    ingest_source: hand\n",
        encoding="utf-8",
    )
    with pytest.raises(ObligationError, match="not pinned"):
        load(p, store=InstrumentStore(REPO / CORPUS))


def test_obligations__the_committed_table_is_empty_and_says_why():
    tbl = load(REPO / "obligations.yaml", store=InstrumentStore(REPO / CORPUS))
    assert len(tbl) == 0
    text = (REPO / "obligations.yaml").read_text(encoding="utf-8")
    assert "D-P7-01" in text and "statute_instruments: []" in text


def test_obligations__a_span_that_disagrees_with_its_quote_fails_at_load(tmp_path):
    store = InstrumentStore(REPO / CORPUS)
    it = store.get("template-7d9a1960")
    p = tmp_path / "obligations.yaml"
    p.write_text(
        "obligations:\n"
        "  - obligation_id: OBL-BAD\n"
        "    source: TEMPLATE\n"
        "    instrument_id: template-7d9a1960\n"
        "    quote: 'this text is not at that offset'\n"
        "    span: [0, 31]\n"
        "    ingest_source: hand\n",
        encoding="utf-8",
    )
    with pytest.raises(ObligationError, match="one of them is a lie"):
        load(p, store=store)
    assert it.text[0:31] != "this text is not at that offset"


# --- C2: two numbers, never one ------------------------------------------------------------


def test_p7__both_obligation_counts_render_or_neither_does(fme):
    _r, _it, tbl = fme
    rendered = tbl.render_coverage_pair(_r.candidates)
    assert "predicates_with_a_STATUTE_obligation  = 0 / 349" in rendered
    assert "predicates_with_a_TEMPLATE_obligation = 349 / 349" in rendered
    assert NO_STATUTORY_PREDICATE.capitalize() in rendered
    assert_pair_rendered(rendered)

    with pytest.raises(UnpairedObligationCount, match="TEMPLATE"):
        assert_pair_rendered("predicates_with_a_STATUTE_obligation = 0 / 349")
    with pytest.raises(UnpairedObligationCount, match="STATUTE"):
        assert_pair_rendered("predicates_with_a_TEMPLATE_obligation = 349 / 349")
    assert_pair_rendered("a surface that mentions neither is not making the claim")


def test_p7__there_is_no_accessor_that_returns_one_count(fme):
    """The rule is enforced by the SHAPE of the interface, not by a convention. A surface can
    render one number alone only by discarding the others it was handed."""
    _r, _it, tbl = fme
    assert not hasattr(tbl, "statute_count")
    assert not hasattr(tbl, "template_count")
    assert len(tbl.coverage_pair(_r.candidates)) == 3


def test_p7__the_pair_is_computed_over_the_whole_corpus():
    total_s = total_t = 0
    for p in sorted(FIX.glob("*.xlsx")):
        r = harvest(p)
        if not r.candidates:
            continue
        tbl = generate_template_obligations(r, emit(p))
        s, t, _n = tbl.coverage_pair(r.candidates)
        total_s += s
        total_t += t
    assert (total_s, total_t) == (0, 572), (
        "0 STATUTE is not 'nobody has written one yet' — no statute is pinned in this repository "
        "at all (D-P7-01)"
    )


def test_obligations__a_candidate_with_an_unknown_obligation_raises(fme):
    """There is no seventh G0 outcome and no skip: a candidate whose obligation is missing must
    not fall through to a pass."""
    _r, _it, tbl = fme

    class Orphan:
        obligation_id = "OBL-TEMPLATE-F-Nowhere-A1"

    with pytest.raises(ObligationError, match="wearing a gate's clothes"):
        tbl.coverage_pair([Orphan()])


def test_obligations__table_is_a_mapping_that_refuses_defaults(fme):
    _r, _it, tbl = fme
    assert isinstance(tbl, ObligationTable)
    assert "OBL-TEMPLATE-F-1._Introduction-D17" in tbl
    with pytest.raises(ObligationError):
        tbl["OBL-DOES-NOT-EXIST"]
