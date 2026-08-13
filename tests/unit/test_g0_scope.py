"""P7-B2 — G0, and every one of its seven closed reasons observed red on a REAL candidate.

**Why the seven are exercised individually rather than in aggregate.** On this corpus G0 rejects
nothing: 572 of 572 pass. A funnel row of `572 → 572` is only evidence if the gate can be shown to
fail, and *showing it can fail* means showing each reason firing on a candidate drawn from the
population the funnel was computed over — not on a toy. Every rejection below starts from a real
harvested candidate and perturbs exactly one thing.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.envelope import Clause, Proviso  # noqa: E402
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.obligations import (  # noqa: E402
    Obligation,
    ObligationSource,
    ObligationTable,
    generate_template_obligations,
)
from cdfc.qualify.errors import (  # noqa: E402
    SuspiciousUniformityError,
    UnsourcedObligationError,
)
from cdfc.qualify.g0_scope import (  # noqa: E402
    CLOSED_REASONS,
    REMEDY,
    Reason,
    assert_not_uniformly_proviso_free,
    check,
)
from cdfc.qualify.instruments import CORPUS, InstrumentStore  # noqa: E402
from cdfc.qualify.provisos import ProvisoRecallUnmeasured  # noqa: E402
from cdfc.qualify.template_instrument import emit  # noqa: E402
from cdfc.qualify.textsource import Extraction, Unit, build  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


@pytest.fixture(scope="module")
def world():
    r = harvest(FME)
    it = emit(FME)
    store = InstrumentStore(REPO / CORPUS)
    store.in_memory(it)
    return r, it, store, generate_template_obligations(r, it)


def _with_obligation(tbl: ObligationTable, oid: str, **over) -> ObligationTable:
    o = tbl[oid]
    return ObligationTable({**tbl.rows, oid: dataclasses.replace(o, **over)})


def _cand(r, oid: str):
    return next(c for c in r.candidates if c.obligation_id == oid)


SUM_D17 = "OBL-TEMPLATE-F-1._Introduction-D17"


# --- the closed set ------------------------------------------------------------------------


def test_g0__the_reason_set_is_closed_and_each_reason_has_its_own_remedy():
    """The admission test for a reason code: a reason whose remedy is another's is not a second
    reason."""
    assert len(CLOSED_REASONS) == 7
    assert set(REMEDY) == set(CLOSED_REASONS)
    assert len(set(REMEDY.values())) == 7


def test_g0__every_candidate_has_exactly_one_disposition(world):
    """F9. There is no skip: `entered == skipped + rejected + survived`, and `skipped` is 0."""
    r, _it, store, tbl = world
    entered = skipped = rejected = survived = 0
    for c in r.candidates:
        out = check(c, tbl, store)
        entered += 1
        if out.skipped is not None:
            skipped += 1
        elif out.passed:
            survived += 1
        else:
            rejected += 1
            assert out.reason in CLOSED_REASONS
        # A DISPOSITION IS A COMPUTATION, NOT A VERDICT. Counting outcomes alone cannot tell a
        # pass that resolved a span from a pass that returned early having computed nothing —
        # which is exactly NC-Q51's injected build, and this assertion is what makes the count
        # above evidence rather than arithmetic.
        assert out.measured, f"{c.id}: a G0 outcome whose record is empty computed nothing"
        for field in ("instrument_id", "obligation_source", "occurrences", "span",
                      "corroboration", "provisos_total", "markers_version"):
            assert field in out.measured, f"{c.id}: G0 did not record {field}"
    assert entered == 348
    assert entered == skipped + rejected + survived
    assert skipped == 0, "a skip at G0 is the vacuous pass in its purest form"


def test_g0__an_unsourced_candidate_raises_rather_than_passing(world):
    """A candidate that cannot be gated is not a candidate that passes. The envelope refuses to
    build one, so the shape has to be constructed — which is the point: a FUTURE predicate kind
    that arrives without an obligation must hit this, not a default."""
    _r, _it, store, tbl = world

    class NoObligation:
        id = "P-FUTURE-KIND"
        obligation_id = ""
        obligation_source = "TEMPLATE"
        clause = None

    with pytest.raises(UnsourcedObligationError, match="no skip at G0"):
        check(NoObligation(), tbl, store)


def test_g0__a_candidate_disagreeing_with_the_table_raises(world):
    """Two answers to one question is not a gate input."""
    _r, _it, store, tbl = world

    class Disagrees:
        id = "P-DISAGREES"
        obligation_id = SUM_D17
        obligation_source = "STATUTE"
        clause = Clause(instrument="x", eId="e", span=(0, 1), quote="q")

    with pytest.raises(UnsourcedObligationError, match="Two answers to one question"):
        check(Disagrees(), tbl, store)


# --- reason 1: quote_not_located -----------------------------------------------------------


def test_g0__verbatim_quote_required(world):
    """`find` must succeed, and the U+002D → U+2011 homoglyph variant is REJECTED.

    This is why `textsource.normalise` refuses to unify dashes: a normaliser that folded them
    would make this gate unfailable."""
    r, it, store, tbl = world
    c = _cand(r, SUM_D17)
    assert check(c, tbl, store).passed

    original = tbl[SUM_D17].quote
    assert "-" not in original  # the FME sum carries no hyphen, so plant one that exists
    hyphenated = next(
        (o for o in tbl.rows.values() if "-" in o.quote and it.text.count(o.quote) >= 1), None
    )
    assert hyphenated is not None, "no obligation in this corpus carries a hyphen-minus"
    homoglyph = hyphenated.quote.replace("-", "‑", 1)
    assert homoglyph != hyphenated.quote
    bad = _with_obligation(tbl, hyphenated.obligation_id, quote=homoglyph)
    out = check(_cand(r, hyphenated.obligation_id), bad, store)
    assert not out.passed and out.reason == Reason.QUOTE_NOT_LOCATED


def test_g0__a_construct_the_blank_does_not_carry_is_not_located(world):
    r, _it, store, tbl = world
    bad = _with_obligation(tbl, SUM_D17, quote="SUM(D18:D21)")
    out = check(_cand(r, SUM_D17), bad, store)
    assert not out.passed and out.reason == Reason.QUOTE_NOT_LOCATED
    assert out.measured["occurrences"] == 0


# --- reason 2: span_mismatch ---------------------------------------------------------------


def test_g0__span_and_quote_must_agree(world):
    """The span and the quote disagree; one of them is a lie."""
    r, _it, store, tbl = world
    o = tbl[SUM_D17]
    bad = _with_obligation(tbl, SUM_D17, span=(o.span[0] + 3, o.span[1] + 3))
    out = check(_cand(r, SUM_D17), bad, store)
    assert not out.passed and out.reason == Reason.SPAN_MISMATCH


# --- reason 3: quote_ambiguous -------------------------------------------------------------


def test_g0__ambiguous_quote_rejected(world):
    """A quote occurring more than once with a span selecting NEITHER occurrence.

    *`find` succeeding is not locating deterministically.*
    """
    r, it, store, tbl = world
    repeated = next(
        o for o in tbl.rows.values() if len(it.find_all(o.quote)) > 1
    )
    # ADMISSION SIDE: the same quote, with a span that selects one occurrence, passes.
    assert check(_cand(r, repeated.obligation_id), tbl, store).passed
    assert len(it.find_all(repeated.quote)) > 1

    # REJECTION SIDE: a span of the right LENGTH and the right TEXT, at an offset that is not one
    # of the occurrences. The text there matches by coincidence only if the quote repeats
    # contiguously, so a span shifted off every occurrence is the ambiguous case.
    hits = it.find_all(repeated.quote)
    off = (hits[0][0] + 1, hits[0][1] + 1)
    bad = _with_obligation(tbl, repeated.obligation_id, span=off)
    out = check(_cand(r, repeated.obligation_id), bad, store)
    assert not out.passed
    assert out.reason in (Reason.SPAN_MISMATCH, Reason.QUOTE_AMBIGUOUS)


def test_g0__ambiguity_is_reachable_and_is_not_span_mismatch():
    """**The ordering defect this test found.** With `span_mismatch` checked first,
    `g0.quote_ambiguous` was UNREACHABLE — `find_all` returns every offset where the text matches,
    so a span selecting no occurrence always fails the slice test too, and the more specific
    finding never surfaced. A reason code that cannot be reached is a remedy nobody is offered.

    The two are separate because the remedies are: a UNIQUE quote with a wrong span is fixed by
    fixing the span; a REPEATED quote with a wrong span may need a wider quote, because that text
    alone cannot name one occurrence.
    """
    store = InstrumentStore(REPO / CORPUS)

    def instrument(name, body):
        it = build(f"template-{name}", [
            Extraction(extractor="a", version="t", external=False, blind_to={},
                       units=(Unit(key="k1", text=body, page=1),)),
            Extraction(extractor="b", version="t", external=True, blind_to={},
                       units=(Unit(key="k1", text=body, page=1),)),
        ])
        store.in_memory(it)
        return it

    def table(it, quote, span):
        return ObligationTable({"OBL-TEMPLATE-F-x-A1": Obligation(
            obligation_id="OBL-TEMPLATE-F-x-A1", source=ObligationSource.TEMPLATE,
            instrument_id=it.instrument_id, frbr_uri=None, eId=None, quote=quote,
            span=span, ingest_source="harvest")})

    class C:
        id = "P-X"
        obligation_id = "OBL-TEMPLATE-F-x-A1"
        obligation_source = "TEMPLATE"
        clause = None

    # REPEATED quote, span selecting neither occurrence -> AMBIGUOUS
    rep = instrument("amb-repeated", "ab ab")
    assert rep.find_all("ab") == ((0, 2), (3, 5))
    out = check(C(), table(rep, "ab", (1, 3)), store)
    assert not out.passed and out.reason == Reason.QUOTE_AMBIGUOUS
    assert out.measured["occurrences"] == 2

    # ADMISSION-SIDE TWIN: the same repeated quote with a span ON an occurrence passes.
    assert check(C(), table(rep, "ab", (3, 5)), store).passed

    # UNIQUE quote, wrong span -> SPAN MISMATCH, a different remedy
    uniq = instrument("amb-unique", "abc def")
    assert uniq.find_all("abc") == ((0, 3),)
    out2 = check(C(), table(uniq, "abc", (1, 4)), store)
    assert not out2.passed and out2.reason == Reason.SPAN_MISMATCH


# --- reason 4: quote_in_disputed_region -----------------------------------------------------


def test_g0__a_quote_in_a_disputed_region_is_refused(world):
    """NC-Q50's admission-side consequence, at the gate. A span into text one extractor never saw
    is not a span, and the refusal is NAMED rather than being a silent failure to locate."""
    r, _it, store, tbl = world
    disputed = build("template-disputed-fme", [
        Extraction(extractor="a", version="t", external=False, blind_to={},
                   units=(Unit(key="k1", text="SUM(D18:D20)", page=1),)),
        Extraction(extractor="b", version="t", external=True, blind_to={},
                   units=(Unit(key="k1", text="SUM(D18:D21)", page=1),)),
    ])
    store.in_memory(disputed)
    bad = ObligationTable({SUM_D17: dataclasses.replace(
        tbl[SUM_D17], instrument_id=disputed.instrument_id, span=disputed.units[0].span)})
    out = check(_cand(r, SUM_D17), bad, store)
    assert not out.passed and out.reason == Reason.QUOTE_IN_DISPUTED_REGION
    assert out.measured["corroboration"] == "DISPUTED"


# --- reasons 5-7: the provisos --------------------------------------------------------------


def _statute_world(quote: str):
    """A STATUTE instrument, built in memory. There is none on disk (D-P7-01), so a guard for the
    proviso reasons has to construct one — and it constructs a REAL instrument through the same
    dual-extraction harness, not a stub."""
    it = build("fm-regulations-TEST", [
        Extraction(extractor="alpha", version="t", external=False, blind_to={},
                   units=(Unit(key="reg51", text=quote, page=7),)),
        Extraction(extractor="beta", version="t", external=True, blind_to={},
                   units=(Unit(key="reg51", text=quote, page=7),)),
    ])
    store = InstrumentStore(REPO / CORPUS)
    store.in_memory(it, kind="STATUTE")
    tbl = ObligationTable({"OBL-014": Obligation(
        obligation_id="OBL-014", source=ObligationSource.STATUTE,
        instrument_id=it.instrument_id, frbr_uri=None, eId="reg_51__subreg_1",
        quote=quote, span=(0, len(quote)), ingest_source="hand")})
    return it, store, tbl


def _statute_cand(provisos: tuple[Proviso, ...], quote: str):
    class C:
        id = "P-STATUTE-1"
        obligation_id = "OBL-014"
        obligation_source = "STATUTE"
        clause = Clause(instrument="fm-regulations-TEST", eId="reg_51__subreg_1",
                        span=(0, len(quote)), quote=quote, provisos=provisos)

    return C()


CLAUSE = ("The net asset value shall be computed. Provided that the scheme is close-ended.")


def test_g0__a_statute_candidate_is_refused_while_recall_is_unmeasured():
    """Before any proviso reason can be reached, the detector must have a measured recall."""
    _it, store, tbl = _statute_world(CLAUSE)
    with pytest.raises(ProvisoRecallUnmeasured):
        check(_statute_cand((), CLAUSE), tbl, store)


def _with_labels(tmp_path, monkeypatch):
    import json

    import cdfc.qualify.provisos as P

    p = tmp_path / "labels.json"
    p.write_text(json.dumps({
        "labeller": "A. Reader", "labelled_at": "2026-08-13",
        "spans": [{"text": "Provided that x is so", "kind": "proviso"}],
    }), encoding="utf-8")
    monkeypatch.setattr(P, "LABELS_PATH", p)
    return p


def test_g0__an_undisposed_proviso_is_rejected(tmp_path, monkeypatch):
    _with_labels(tmp_path, monkeypatch)
    _it, store, tbl = _statute_world(CLAUSE)
    out = check(_statute_cand((), CLAUSE), tbl, store)
    assert not out.passed and out.reason == Reason.PROVISO_UNDISPOSED
    assert out.measured["provisos_total"] == 1
    assert out.measured["undisposed"] == 1


def test_g0__proviso_arithmetic_must_sum(tmp_path, monkeypatch):
    """`provisos_total != implemented + declared`. The record does not sum; it is not a record."""
    _with_labels(tmp_path, monkeypatch)
    _it, store, tbl = _statute_world(CLAUSE)
    # Two declared provisos against one detected: the arithmetic fails before disposal does.
    two = (Proviso(text="Provided that the scheme is close-ended", disposal="IMPLEMENTED",
                   emits=None, span=(0, 1)),
           Proviso(text="Provided that a second one exists", disposal="IMPLEMENTED",
                   emits=None, span=(1, 2)))
    out = check(_statute_cand(two, CLAUSE), tbl, store)
    assert not out.passed and out.reason == Reason.PROVISO_ARITHMETIC


def test_g0__a_declared_proviso_must_name_what_it_emits(tmp_path, monkeypatch):
    """A declaration that emits nothing is a silent drop wearing a label. `Proviso` refuses it at
    construction, so the gate's reason is reachable only through a record built around the type —
    and both refusals are asserted, because the envelope's is the one a hand-authored YAML meets
    and the gate's is the one a generated record meets."""
    from cdfc.predicates.envelope import Candidate, EnvelopeSchemaError

    _with_labels(tmp_path, monkeypatch)
    _it, store, tbl = _statute_world(CLAUSE)

    class Bare:
        text = "Provided that the scheme is close-ended"
        disposal = "DECLARED"
        emits = None
        span = (0, 1)

    out = check(_statute_cand((Bare(),), CLAUSE), tbl, store)
    assert not out.passed and out.reason == Reason.DECLARED_PROVISO_MISSING_EMISSION

    # The envelope refuses the same thing at construction — two independent refusals, because a
    # hand-authored YAML meets the first and a generated record meets the second.
    with pytest.raises(EnvelopeSchemaError, match="undisposed proviso with a label"):
        Candidate(
            id="P-X", version=1, kind="hand_authored", template="t" * 64,
            schema_keys=("filing.a",), host_fns=(), obligation_id="OBL-014",
            obligation_source="STATUTE",
            clause=Clause(instrument="i", eId="e", span=(0, 1), quote="q", provisos=(
                Proviso(text="x", disposal="DECLARED", emits=None, span=(0, 1)),)),
            rationale="r", clause_absent_reason=None, claims_fault_classes=("F01",),
            applicable="true", expr="true", witness="[]", reason_if_inapplicable="r",
            tolerance=None,
        )


def test_g0__a_disposed_proviso_passes(tmp_path, monkeypatch):
    """THE ADMISSION-SIDE TWIN for all three proviso reasons. Without it the proviso branch is
    indistinguishable from a branch that rejects every statutory candidate."""
    _with_labels(tmp_path, monkeypatch)
    _it, store, tbl = _statute_world(CLAUSE)
    ok = (Proviso(text="Provided that the scheme is close-ended", disposal="DECLARED",
                  emits="NO_PREDICATE(no_predicate.not_yet_synthesised)", span=(38, 51)),)
    out = check(_statute_cand(ok, CLAUSE), tbl, store)
    assert out.passed, out.reason
    assert out.measured["provisos_total"] == 1
    assert out.measured["provisos_declared"] == 1
    assert "A. Reader" in str(out.measured["g0_marker_recall"])


def test_g0__a_proviso_free_statutory_clause_passes(tmp_path, monkeypatch):
    """NC-Q35's admission-side twin: a genuinely proviso-free clause reports zero and no error."""
    _with_labels(tmp_path, monkeypatch)
    plain = "The net asset value shall be computed on the last business day of the quarter."
    _it, store, tbl = _statute_world(plain)
    out = check(_statute_cand((), plain), tbl, store)
    assert out.passed and out.measured["provisos_total"] == 0


# --- NC-Q35's scoping -----------------------------------------------------------------------


def test_g0__the_uniformity_guard_is_scoped_to_statute(world):
    """**The scoping is asserted, not assumed.** Under F9 all 349 harvested candidates are
    `source: TEMPLATE` with a legitimate `provisos_total == 0`. An unscoped guard would fire on a
    correct build — and would then be "fixed" by deleting it."""
    r, _it, store, tbl = world
    outcomes = {c.id: check(c, tbl, store) for c in r.candidates}
    assert all(o.measured["provisos_total"] == 0 for o in outcomes.values())
    assert_not_uniformly_proviso_free(outcomes, r.candidates)  # must NOT raise

    class Statutory:
        id = "P-STATUTE-1"
        obligation_source = "STATUTE"

    fake = {**outcomes, "P-STATUTE-1": next(iter(outcomes.values()))}
    with pytest.raises(SuspiciousUniformityError, match="scoped to STATUTE"):
        assert_not_uniformly_proviso_free(fake, [*r.candidates, Statutory()])


def test_g0__measured_carries_the_corroboration_of_the_unit(world):
    """D-P7-02. A pass over an uncorroborated construct says so, rather than looking like a pass
    over a corroborated one."""
    r, _it, store, tbl = world
    states = {check(c, tbl, store).measured["corroboration"] for c in r.candidates}
    assert states == {"AGREED", "SINGLE_PARTY"}, (
        "both states occur on FME — 19 x14 validations and one array formula are uncorroborated — "
        "and G0 must be recording which"
    )
