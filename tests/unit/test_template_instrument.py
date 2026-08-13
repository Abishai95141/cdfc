"""P7-B1 — the pinned blank as an addressable instrument (F9).

The admission-side test and the rejection-side test are here together, deliberately. A locator
that finds everything and a locator that finds nothing both pass one of them.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.obligations import ObligationError, generate_template_obligations  # noqa: E402
from cdfc.qualify.template_instrument import (  # noqa: E402
    TemplateInstrumentError,
    emit,
    instrument_id,
)

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


@pytest.fixture(scope="module")
def fme():
    return harvest(FME), emit(FME)


def test_ti__every_harvested_candidate_locates(fme):
    """ADMISSION SIDE. All 349 harvested FME candidates have an obligation whose construct is
    present in the pinned blank at the recorded span."""
    r, it = fme
    tbl = generate_template_obligations(r, it)
    assert len(r.candidates) == 349
    located = 0
    for c in r.candidates:
        o = tbl[c.obligation_id]
        assert it.text[o.span[0] : o.span[1]] == o.quote
        assert o.quote in it.text
        located += 1
    assert located == 349


def test_ti__a_stale_construct_is_not_located(fme):
    """REJECTION SIDE, and it is the template-churn regression check. Re-point a candidate's
    obligation at a formula the pinned blank does not carry and generation refuses — which is
    `g0.quote_not_located` caught one step earlier."""
    r, it = fme
    stale = dict(r.constructs)
    victim = "OBL-TEMPLATE-F-1._Introduction-D17"
    assert victim in stale
    stale[victim] = ("formula", ("SUM(D18:D21)",), "1. Introduction", "ZZ9999")

    class Stale:
        constructs = stale

    with pytest.raises(ObligationError, match="different template versions"):
        generate_template_obligations(Stale(), it)


def test_ti__a_construct_whose_TEXT_moved_is_refused(fme):
    """The other half of staleness: the cell still exists, the formula in it changed. Nothing
    about the address catches that, which is why the CONSTRUCT is compared and not the address."""
    r, it = fme
    moved = dict(r.constructs)
    victim = "OBL-TEMPLATE-F-1._Introduction-D17"
    moved[victim] = ("formula", ("SUM(D18:D99)",), "1. Introduction", "D17")

    class Moved:
        constructs = moved

    with pytest.raises(ObligationError, match="read one construct differently"):
        generate_template_obligations(Moved(), it)


def test_ti__the_D17_collision_is_two_obligations_not_one(fme):
    """The defect P7-B1 found in P4's id scheme. `1. Introduction!D17` carries BOTH a formula and
    a `whole >= 0` validation — two different obligations that shared one id, so the quote would
    have been whichever harvest class ran last."""
    r, it = fme
    tbl = generate_template_obligations(r, it)
    f = tbl["OBL-TEMPLATE-F-1._Introduction-D17"]
    v = tbl["OBL-TEMPLATE-V-1._Introduction-D17"]
    assert f.quote == "SUM(D18:D20)"
    assert v.quote.startswith("whole")
    assert f.span != v.span
    assert it.text[f.span[0] : f.span[1]] == f.quote
    assert it.text[v.span[0] : v.span[1]] == v.quote


def test_ti__obligation_ids_are_injective_over_the_corpus():
    """One obligation per construct, corpus-wide. A foreign key that is not injective points at
    the wrong row silently."""
    total_c = total_o = 0
    for p in sorted(FIX.glob("*.xlsx")):
        r = harvest(p)
        total_c += len(r.candidates)
        total_o += len(r.constructs)
    assert (total_c, total_o) == (572, 572)


def test_ti__instrument_id_is_the_template_digest():
    assert instrument_id("7d9a1960085785ee" + "0" * 48) == "template-7d9a1960"


def test_ti__a_reader_miss_is_not_an_exclusion(monkeypatch):
    """`emit` refuses when the external party produced nothing at a key neither declared mechanism
    explains. Without that rule a reader that silently dropped a construct would be labelled
    merely uncorroborated."""
    import cdfc.qualify.template_instrument as TI

    real = TI._party_b

    def drops_a_formula(blob, order):
        units, arrays = real(blob, order)
        victim = next(k for k in sorted(units) if "|F|" in k)
        del units[victim]
        return units, arrays

    monkeypatch.setattr(TI, "_party_b", drops_a_formula)
    with pytest.raises(TemplateInstrumentError, match="neither declared mechanism explains"):
        TI.emit(FME)


def test_ti__party_a_may_not_be_blind(monkeypatch):
    """The symmetric rule. `reader_lxml` enumerates the raw XML and declares no blindness, so an
    absence on its side is a defect in this repository rather than an exclusion."""
    import cdfc.qualify.template_instrument as TI

    real = TI._party_a

    def drops_a_formula(wb):
        units, x14, arrays = real(wb)
        victim = next(k for k in sorted(units) if "|F|" in k)
        del units[victim]
        return units, x14, arrays

    monkeypatch.setattr(TI, "_party_a", drops_a_formula)
    with pytest.raises(TemplateInstrumentError, match="defect in this repository's reader"):
        TI.emit(FME)
