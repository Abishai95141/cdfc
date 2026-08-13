"""P4 — the negative controls for the predicate envelope, the CEL substrate and the harvest.

Every entry here ships with its admission-side twin. Without one, a check that rejects everything
scores perfectly: the guard goes red under injection because it goes red under everything.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.harvest_report import render_report  # noqa: E402
from cdfc.predicates.ast_walker import check_declared_keys, read_keys  # noqa: E402
from cdfc.predicates.canonical import code_sha256, envelope_projection  # noqa: E402
from cdfc.predicates.cel_profile import check_subset  # noqa: E402
from cdfc.predicates.envelope import EnvelopeSchemaError  # noqa: E402
from cdfc.predicates.errors import (  # noqa: E402
    DeclaredKeyUnread,
    SubsetViolation,
    UndeclaredKeyRead,
)
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.harvest_classes import CLAIMS  # noqa: E402
from cdfc.predicates.loader import (  # noqa: E402
    UnqualifiedPredicateError,
    load_candidate,
    load_predicate,
)

GOOD = REPO / "fixtures" / "predicates" / "good"
BROKEN = REPO / "fixtures" / "predicates" / "broken"
FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
ITFS = FIX / "ITFS_Monthly_report201220241626.xlsx"
P0041 = GOOD / "P-0041__scheme-type-membership.yaml"
P0007 = GOOD / "P-0007__intro-D17-integer-bound.yaml"


# --- NC-Q02 — the loader invariant, LIVE from P4 ------------------------------------------


def test_nc__Q02b_the_predicate_loader_refuses_an_unqualified_envelope() -> None:
    with pytest.raises(UnqualifiedPredicateError):
        load_predicate(BROKEN / "P-NC02__no-qualification.yaml")


def test_nc__Q02c_a_qualified_predicate_does_load() -> None:
    """THE ADMISSION-SIDE TWIN, impossible before P4 because the schema did not exist."""
    p = load_predicate(P0007)
    assert p.qualification is not None and p.state


# --- NC-Q41 — a field leaves the canonical serialisation ------------------------------------


def test_nc__Q41_every_record_field_is_inside_the_digest() -> None:
    for env in (load_candidate(P0041), load_predicate(P0007)):
        import dataclasses

        projected = set(envelope_projection(env))
        for f in dataclasses.fields(env):
            assert f.name in projected, (
                f"{f.name} is not in the canonical projection, so it is not in the identity: a "
                "predicate could be re-issued with it changed under the same code_sha256"
            )


def test_nc__Q41b_two_envelopes_differing_only_in_a_claim_have_different_digests() -> None:
    """The admission side: the digest does distinguish envelopes it should distinguish."""
    import yaml

    raw = yaml.safe_load(P0041.read_text(encoding="utf-8"))
    a = load_candidate(raw)
    b = load_candidate({**raw, "claims_fault_classes": ["F12", "F05"]})
    assert code_sha256(a) != code_sha256(b)


# --- NC-Q42 — the two directions of the both-ways check are distinguishable ------------------


def test_nc__Q42_the_two_key_mismatches_raise_different_types() -> None:
    with pytest.raises(UndeclaredKeyRead):
        check_declared_keys(load_candidate(BROKEN / "P-NC04a__reads-undeclared.yaml"))
    with pytest.raises(DeclaredKeyUnread):
        check_declared_keys(load_candidate(BROKEN / "P-NC04b__declares-unread.yaml"))


def test_nc__Q42b_a_correct_envelope_raises_neither() -> None:
    """The admission side. A check that always raises satisfies the test above."""
    check_declared_keys(load_candidate(P0041))
    check_declared_keys(load_predicate(P0007))


# --- NC-Q43 — the subset walker actually walks ----------------------------------------------


BANNED_FORMS = (
    "filing.rows.all(r, r.sub.all(s, s.x > 0))",
    'filing.a.matches("^x")',
    "dyn(filing.a) == 1",
    "filing.a == 1.5",
    "other.a == 1",
)


def test_nc__Q43_a_banned_construct_is_refused() -> None:
    """Deliberately a loop rather than a `parametrize`.

    The sweep maps guard results BY NODE ID, and a parametrised test's node ids carry a `[case]`
    suffix — so the catalogue would have to name each case, and adding a banned form would
    silently leave the new case outside the declared exact set.
    """
    for src in BANNED_FORMS:
        with pytest.raises(SubsetViolation):
            check_subset(src, slot="expr")


def test_nc__Q43d_a_flat_comprehension_is_admitted() -> None:
    """The admission-side twin: the walker is not simply rejecting everything."""
    check_subset("filing.rows.all(r, r.x > 0)", slot="expr")
    check_subset("filing.rows.filter(r, r.x == 0).map(r, r.__cell__)", slot="witness")


# --- NC-Q44 — key extraction is structural, not lexical --------------------------------------


def test_nc__Q44_the_comprehension_binding_is_never_a_document_root() -> None:
    keys = read_keys("filing.rows.all(r, r.x in template.v.k)", slot="expr")
    assert "r.x" not in keys, "a lexical pass reports the binding as a root"
    assert "filing.rows[*].x" in keys, "and loses the [*] that says the key is a column"


def test_nc__Q44c_both_roots_are_reported() -> None:
    """The admission-side twin: the walker reads BOTH documents, not just the filing."""
    keys = read_keys("filing.rows.all(r, r.x in template.v.k)", slot="expr")
    assert {"filing.rows[*].x", "template.v.k"} == set(keys)


# --- NC-Q45 — the total never renders without its distribution --------------------------------


def test_nc__Q45_the_distribution_renders_beside_the_total() -> None:
    results = [harvest(ITFS), harvest(FME)]
    doc = render_report(results)
    for r in results:
        assert f"`{r.template_sha256[:8]}`" in doc, (
            "a workbook is missing from the rendered distribution; the total alone reads as "
            "breadth when the distribution is concentrated"
        )
    assert "Concentration:" in doc


def test_nc__Q45b_the_total_itself_still_renders() -> None:
    """The admission side: the fix is not to delete the total."""
    doc = render_report([harvest(ITFS)])
    assert "| **total** |" in doc


# --- NC-Q46 — the weak pile is counted, not dropped --------------------------------------------


def test_nc__Q46_a_construct_outside_the_class_set_is_recorded() -> None:
    res = harvest(FME)
    assert res.skipped, "FME carries constructs the class set cannot express; none was recorded"
    assert res.skips_by_kind.get("function_outside_vocabulary", 0) > 0
    for s in res.skipped:
        assert s.sheet and s.ref and s.detail


def test_nc__Q46b_a_workbook_with_nothing_to_skip_records_nothing() -> None:
    """The admission side: the counter is not simply always non-zero."""
    res = harvest(FIX / "EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx")
    assert res.skipped == ()


# --- NC-Q47 — a clause-less candidate declares why ----------------------------------------------


def test_nc__Q47_a_template_obligation_must_declare_why_it_cites_no_statute() -> None:
    import yaml

    raw = yaml.safe_load(P0041.read_text(encoding="utf-8"))
    with pytest.raises(EnvelopeSchemaError, match="declare why"):
        load_candidate({**raw, "clause_absent_reason": None})


def test_nc__Q47b_every_harvested_candidate_declares_why() -> None:
    """280-style instance count: the guard fires on every harvested candidate, not zero."""
    res = harvest(FME)
    assert res.candidates
    for c in res.candidates:
        assert c.obligation_source == "TEMPLATE" and c.clause_absent_reason


# --- NC-Q48 — the claim is a pure function of the class ------------------------------------------


def test_nc__Q48_claims_precede_the_campaign_and_do_not_vary_per_predicate() -> None:
    res = harvest(FME)
    by_class: dict[tuple[str, ...], set[tuple[str, ...]]] = {}
    for c in res.candidates:
        by_class.setdefault(tuple(c.claims_fault_classes), set()).add(tuple(c.claims_fault_classes))
    declared = {tuple(v) for v in CLAIMS.values()}
    for claim in by_class:
        assert claim in declared, (
            f"{claim} is not any harvest class's declared constant, so it was derived per "
            "predicate — which is the kill vector choosing the denominator"
        )


def test_nc__Q48b_the_declared_claims_are_non_empty_and_resolve() -> None:
    """The admission side: the classes do declare claims, and every member resolves."""
    from cdfc.predicates.fault_model import known_ids

    assert CLAIMS
    for name, classes in CLAIMS.items():
        assert classes, f"{name} claims nothing"
        assert set(classes) <= known_ids()


# --- NC-Q49 — the host functions -------------------------------------------------------------------


def test_nc__Q49_reg_resolves_never_answers_without_a_snapshot() -> None:
    from cdfc.predicates.host_fns import HostFnRegistry, SnapshotMissing
    from cdfc.predicates.host_fns import reg_resolves as mod

    reg = HostFnRegistry()
    mod.bind_registry(reg)
    with pytest.raises(SnapshotMissing):
        mod.reg_resolves("IFSCA-FME-001")


def test_nc__Q49b_with_a_snapshot_bound_it_answers() -> None:
    """The admission side."""
    from cdfc.predicates.host_fns import HostFnRegistry
    from cdfc.predicates.host_fns import reg_resolves as mod

    reg = HostFnRegistry()
    reg.bind_snapshot("deadbeef", {"IFSCA-FME-001": True})
    mod.bind_registry(reg)
    assert str(mod.reg_resolves("IFSCA-FME-001")) == "TRUE"


def test_nc__Q49c_nav_interval_keeps_its_third_value() -> None:
    from cdfc.predicates.host_fns import UNDERSPECIFIED
    from cdfc.predicates.host_fns.nav_interval import nav_interval

    assert str(nav_interval("Restricted", "Close-ended", "NA")) == UNDERSPECIFIED, (
        "a two-valued nav_interval has to pick a frequency where the regulator gave none, and "
        "the report then presents our guess as the rule"
    )


def test_nc__Q49d_nav_interval_still_answers_where_the_regulation_determines_it() -> None:
    """The admission side: it has not become UNDERSPECIFIED for everything."""
    from cdfc.predicates.host_fns.nav_interval import nav_interval

    assert str(nav_interval("Retail", "Open-ended", "NA")) == "P1M"


# --------------------------------------------------------------------------------
# P7-B0 — NC-Q50
#
# **Renumbered from the plan's NC-Q47, and the collision is recorded rather than absorbed.**
# `plan/04-phases-qualification.md` P7-B0 names this control NC-Q47, and NC-Q47 has been taken
# since P4 — `a template obligation must declare why it cites no statute`. Reusing the id would
# have silently REPLACED that entry and its two guards in the catalogue, which is the exact defect
# the P5 renumber (E20..E23 -> E30..E37) was recorded for. Second occurrence; `ci/catalogue-ids.sh`
# catches the duplicate in the catalogue, and nothing catches it in a test file, which is why the
# collision is checked by hand before an id is written.
# --------------------------------------------------------------------------------


def _two_parties_that_disagree():
    """A minimal instrument whose two parties read one unit differently.

    Constructed rather than harvested, and the reason is a measurement: across all nine pinned
    blanks the two extractions disagree on **0 of 1,729 units**. A guard pointed at a region the
    corpus does not contain would be green and would prove nothing, so the disagreement is built.
    The mechanism under test is the exclusion RULE, and the rule does not know where its input
    came from. That the rule can also see a real disagreement is asserted separately, by
    `tests/differential/test_diff__two_extractions_agree.py`, which perturbs the shared-formula
    shift on the real workbook.
    """
    from cdfc.qualify.textsource import Extraction, Unit

    def party(name, k2_text, external):
        return Extraction(
            extractor=name, version="nc", external=external,
            units=(Unit(key="k1", text="an agreed sentence", page=1),
                   Unit(key="k2", text=k2_text, page=4)),
            blind_to={},
        )

    return [party("alpha", "the fund shall report within 30 days", False),
            party("beta", "the fund shall report within 90 days", True)]


def test_nc__Q50_disputed_regions_are_excluded() -> None:
    """Un-injected: a quote inside a disputed region is refused, and the refusal names the region.

    The two extractions read the same unit as `30 days` and `90 days`. Neither is authoritative,
    so the text is not addressable there — and the answer is a named refusal rather than one
    party's reading silently winning.
    """
    from cdfc.qualify import textsource as ts

    it = ts.build("nc-q50", _two_parties_that_disagree())
    d = it.disputed[0]
    assert d.key == "k2" and d.page == 4
    assert set(d.readings.values()) == {
        "the fund shall report within 30 days", "the fund shall report within 90 days"
    }
    with pytest.raises(ts.DisputedRegionError):
        it.slice(d.span)
    assert it.addressable_fraction() == (1, 2)
    assert it.counts()["DISPUTED"] == 1


Q50_INJECTED_PROBE = """
import sys
sys.path.insert(0, "src")
from cdfc.qualify.textsource import Extraction, Unit, build
def party(name, k2, ext):
    return Extraction(extractor=name, version="nc", external=ext,
                      units=(Unit(key="k1", text="an agreed sentence", page=1),
                             Unit(key="k2", text=k2, page=4)), blind_to={})
it = build("nc-q50", [party("alpha", "the fund shall report within 30 days", False),
                      party("beta", "the fund shall report within 90 days", True)])
print(it.counts()["DISPUTED"], it.addressable_fraction()[0], "30 days" in it.text,
      "90 days" in it.text)
"""


def test_nc__Q50b_injected_a_span_resolves_against_one_reading() -> None:
    """Injected: the exclusion is dropped, the first extraction is used alone, and the span
    resolves — to text the other extractor never saw.

    The probe runs in a SUBPROCESS. Reloading the module in-process would depend on whether some
    earlier test had already imported it, which is the sort of order-dependence that makes a
    negative control report a colour it did not earn.
    """
    import subprocess
    import sys

    from injectors import REPO_ROOT, TextsourceSingleExtraction, inject

    with inject(TextsourceSingleExtraction()):
        out = subprocess.run([sys.executable, "-c", Q50_INJECTED_PROBE], cwd=REPO_ROOT,
                             capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    disputed, addressable, has30, has90 = out.stdout.split()
    assert disputed == "0", "the injector did not take effect"
    assert addressable == "2", "every unit is addressable once nothing is compared"
    assert (has30, has90) == ("True", "False"), (
        "with one party the losing reading vanishes without a trace, and a span resolves against "
        "text the second extractor never saw"
    )


def test_nc__Q50c_an_agreed_region_locates_and_passes() -> None:
    """THE ADMISSION-SIDE TWIN. Without it the exclusion rule is indistinguishable from a rule
    that refuses every span."""
    from cdfc.qualify import textsource as ts

    it = ts.build("nc-q50", _two_parties_that_disagree())
    spans = it.find_all("an agreed sentence")
    assert len(spans) == 1
    assert it.slice(spans[0]) == "an agreed sentence"
    assert not it.is_disputed(spans[0])


# --------------------------------------------------------------------------------
# P7-B2 — NC-Q01, NC-Q11, NC-Q35, NC-Q39, NC-Q51
# --------------------------------------------------------------------------------


def _fme_world():
    from cdfc.evaluate.celrt import CelRuntime
    from cdfc.facts.build import fact_set_for
    from cdfc.predicates.harvest import harvest
    from cdfc.predicates.host_fns import default_registry
    from cdfc.predicates.obligations import generate_template_obligations
    from cdfc.qualify.instruments import InstrumentStore
    from cdfc.qualify.template_instrument import emit

    root = Path(__file__).resolve().parents[2]
    fme = root / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
    filing = root / "fixtures/synthetic/clean__independently-computed__fme-q1.xlsx"
    r = harvest(fme)
    it = emit(fme)
    store = InstrumentStore(root / "corpus/instruments")
    store.in_memory(it)
    hf = default_registry()
    return (r, it, store, generate_template_obligations(r, it), fact_set_for(filing, fme), hf,
            CelRuntime(profile_version="P7", host_fns=hf))


def test_nc__Q01_a_zero_binding_candidate_is_refused_at_G1() -> None:
    """NC-Q01, and it is the P7-side tooth. `all([])` is True: a predicate binding nothing returns
    a clean pass over nothing at all, and the settled fraction counts it for free."""
    import dataclasses

    from cdfc.qualify import g1_binds

    r, _it, _store, _tbl, facts, hf, rt = _fme_world()
    c = next(x for x in r.candidates if x.id == "P-0001")
    vocab = next(k for k in c.schema_keys if k.startswith("template."))
    zero = dataclasses.replace(c, schema_keys=(vocab,), applicable="true", expr="true", witness="[]")
    out = g1_binds.check(zero, r.schema, facts, rt, hf)
    assert not out.passed and out.reason == g1_binds.Reason.CELLS_BOUND_ZERO
    assert out.measured["cells_bound"] == 0
    assert "expr_outcome" not in out.measured, "it must never reach the expression"


def test_nc__Q01b_a_binding_candidate_is_admitted() -> None:
    """The admission-side twin: without it the rule is a reject-everything baseline."""
    from cdfc.qualify import g1_binds

    r, _it, _store, _tbl, facts, hf, rt = _fme_world()
    c = next(x for x in r.candidates if x.id == "P-0001")
    out = g1_binds.check(c, r.schema, facts, rt, hf)
    assert out.passed and out.measured["cells_bound"] > 0


def test_nc__Q39_unresolved_key_blocks_admission() -> None:
    """NC-Q39. An UNRESOLVED key BLOCKS; it never degrades to a guess. Paired with NC-D04a so the
    same defect is caught at induction AND at admission."""
    from cdfc.predicates.ast_walker import TemplateSchema
    from cdfc.qualify import g1_binds

    r, _it, _store, _tbl, facts, hf, rt = _fme_world()
    c = next(x for x in r.candidates if x.id == "P-0041")
    victim = sorted(k for k in c.schema_keys if k.startswith("filing."))[0]
    holed = TemplateSchema(
        {k: (frozenset() if k == victim else r.schema.cells_for(k)) for k in r.schema.keys()},
        r.schema.template_sha256,
    )
    out = g1_binds.check(c, holed, facts, rt, hf)
    assert not out.passed and out.reason == g1_binds.Reason.KEY_UNRESOLVED


def test_nc__Q35_empty_marker_list_is_detected() -> None:
    """NC-Q35. A G0 run reporting `provisos_total == 0` across every STATUTE candidate raises
    rather than passing, because a real instrument is measurably full of provisos."""
    from cdfc.qualify.errors import SuspiciousUniformityError
    from cdfc.qualify.g0_scope import assert_not_uniformly_proviso_free

    class Statutory:
        id = "P-S1"
        obligation_source = "STATUTE"

    class Zero:
        measured = {"provisos_total": 0}

    with pytest.raises(SuspiciousUniformityError):
        assert_not_uniformly_proviso_free({"P-S1": Zero()}, [Statutory()])


def test_nc__Q35b_a_proviso_free_clause_is_allowed() -> None:
    """The admission-side twin: one statutory candidate reporting a non-zero count is enough for
    the guard to hold, so a genuinely proviso-free clause among others is not a build failure."""
    from cdfc.qualify.g0_scope import assert_not_uniformly_proviso_free

    class S:
        def __init__(self, i):
            self.id = i
            self.obligation_source = "STATUTE"

    class M:
        def __init__(self, n):
            self.measured = {"provisos_total": n}

    assert_not_uniformly_proviso_free({"a": M(0), "b": M(2)}, [S("a"), S("b")])


def test_nc__Q35c_uniformity_guard_is_scoped_to_statute() -> None:
    """**The scoping is asserted, not assumed.** All 349 harvested FME candidates are
    `source: TEMPLATE` with a legitimate `provisos_total == 0`, so an unscoped guard would fire on
    a correct build — and would then be "fixed" by deleting it."""
    from cdfc.qualify.g0_scope import assert_not_uniformly_proviso_free, check

    r, _it, store, tbl, _facts, _hf, _rt = _fme_world()
    outcomes = {c.id: check(c, tbl, store) for c in r.candidates}
    assert all(o.measured["provisos_total"] == 0 for o in outcomes.values())
    assert_not_uniformly_proviso_free(outcomes, r.candidates)  # must NOT raise


def test_nc__Q11a_undeclared_proviso_rejected(tmp_path, monkeypatch) -> None:
    """NC-Q11. The empirical gates cannot see a dropped proviso: a predicate that silently ignores
    an exception still kills mutants and still fires on nothing clean. Only G0 can see it."""
    import json

    import cdfc.qualify.provisos as P
    from cdfc.predicates.envelope import Clause
    from cdfc.predicates.obligations import Obligation, ObligationSource, ObligationTable
    from cdfc.qualify.g0_scope import Reason, check
    from cdfc.qualify.instruments import InstrumentStore
    from cdfc.qualify.textsource import Extraction, Unit, build

    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({
        "labeller": "A. Reader", "labelled_at": "2026-08-13",
        "spans": [{"text": "Provided that x is so", "kind": "proviso"}]}), encoding="utf-8")
    monkeypatch.setattr(P, "LABELS_PATH", labels)

    quote = "The scheme shall report quarterly. Provided that the scheme is close-ended."
    it = build("fm-regulations-NCQ11", [
        Extraction(extractor="a", version="t", external=False, blind_to={},
                   units=(Unit(key="reg", text=quote, page=3),)),
        Extraction(extractor="b", version="t", external=True, blind_to={},
                   units=(Unit(key="reg", text=quote, page=3),)),
    ])
    store = InstrumentStore(Path(__file__).resolve().parents[2] / "corpus/instruments")
    store.in_memory(it, kind="STATUTE")
    tbl = ObligationTable({"OBL-014": Obligation(
        obligation_id="OBL-014", source=ObligationSource.STATUTE, instrument_id=it.instrument_id,
        frbr_uri=None, eId="reg_9", quote=quote, span=(0, len(quote)), ingest_source="hand")})

    class Silent:
        id = "P-S1"
        obligation_id = "OBL-014"
        obligation_source = "STATUTE"
        clause = Clause(instrument=it.instrument_id, eId="reg_9", span=(0, len(quote)),
                        quote=quote, provisos=())

    out = check(Silent(), tbl, store)
    assert not out.passed and out.reason == Reason.PROVISO_UNDISPOSED
    assert out.measured["provisos_total"] == 1


def test_nc__Q51_disposition_of_a_clauseless_candidate_is_specified_and_counted() -> None:
    """NC-Q51 (the plan's NC-Q48, renumbered: that id has been taken since P4).

    Every candidate has exactly ONE G0 disposition from the closed set,
    `entered == skipped + rejected + survived`, and `skipped` is never added to survivors.
    """
    from cdfc.qualify.g0_scope import CLOSED_REASONS, check

    r, _it, store, tbl, _facts, _hf, _rt = _fme_world()
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
        assert out.measured, "a G0 outcome with an empty record computed nothing"
        assert "instrument_id" in out.measured and "occurrences" in out.measured
    assert entered == 349 == skipped + rejected + survived
    assert skipped == 0


def test_nc__Q51b_a_template_candidate_passes_with_zero_provisos() -> None:
    """The admission-side twin: a template-derived candidate whose construct locates passes G0
    with `provisos_total == 0` and no error."""
    from cdfc.qualify.g0_scope import check

    r, _it, store, tbl, _facts, _hf, _rt = _fme_world()
    out = check(r.candidates[0], tbl, store)
    assert out.passed
    assert out.measured["provisos_total"] == 0
    assert out.measured["obligation_source"] == "TEMPLATE"


# --------------------------------------------------------------------------------
# P7-B3/B4 — NC-Q02, NC-Q07, NC-Q34, NC-Q36, NC-Q38, NC-Q55
# --------------------------------------------------------------------------------


def test_nc__Q34_order_is_enforced_by_shape() -> None:
    """NC-Q34. **Assert on the SPY, not on the outcome**: the outcome is the same either way, and
    the COST is the thing being gated. A candidate that fails G0's free check must generate zero
    mutants."""
    from cdfc.qualify.pipeline import QualificationContext, qualify
    from cdfc.qualify.result import GATE_ORDER, GateId

    seen: list[str] = []
    r, it, store, tbl, facts, hf, rt = _fme_world()
    import dataclasses

    from cdfc.evaluate.celrt import CelRuntime  # noqa: F401
    from cdfc.predicates.obligations import ObligationTable

    victim = r.candidates[0]
    broken = ObligationTable({**tbl.rows, victim.obligation_id: dataclasses.replace(
        tbl[victim.obligation_id], quote="A CONSTRUCT THE PINNED BLANK DOES NOT CARRY")})
    ctx = QualificationContext(obligations=broken, store=store, schema=r.schema, facts=facts,
                               runtime=rt, hostfns=hf, qualified_at="2026-08-13")
    res = qualify(victim, ctx, through=GateId.G3E, spy=lambda g: seen.append(g.value))
    assert seen == ["G0"], (
        f"a candidate failing the FREE gate reached {seen[1:]}; the stop is the cost control"
    )
    assert res.row.rejecting_gate is GateId.G0
    assert GATE_ORDER[0] is GateId.G0


def test_nc__Q34b_the_order_is_read_from_the_tuple() -> None:
    """The admission-side twin: the pipeline reads GATE_ORDER rather than hard-coding a sequence,
    which is what makes the injector able to reverse it at all."""
    import ast

    src = (Path(__file__).resolve().parents[2] / "src/cdfc/qualify/pipeline.py").read_text()
    assert "GATE_ORDER[" in src and "GATE_ORDER.index" in src
    tree = ast.parse(src)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "GATE_ORDER" in names


def test_nc__Q02_unqualified_predicate_does_not_load() -> None:
    """NC-Q02, and it **stops being provisional at P7**: both branches are now reachable.

    For four phases this entry was green while proving nothing — the registry refused everything,
    so its admission-side twin was impossible and the sweep reported it in its own column.
    """
    import dataclasses

    from cdfc.predicates.registry import UNSIGNED, Registry, UnqualifiedPredicate, registry_root

    r, _it, _store, _tbl, _facts, _hf, _rt = _fme_world()
    c = r.candidates[0]
    reg = Registry()
    with pytest.raises(UnqualifiedPredicate):
        reg.load(c.id, 1)
    assert reg.root() == registry_root([]), "an unadmitted predicate is absent from the root"
    before = reg.root()

    with pytest.raises(UnqualifiedPredicate):
        reg.admit(c, None, signer=UNSIGNED, signature=b"", batch_manifest_sha256="m",
                  admitted_at="2026-08-13")
    assert reg.root() == before, "a refused admission leaves the root unchanged"

    # THE ADMISSION-SIDE TWIN, impossible before P7.
    row = reg.admit(dataclasses.replace(c), {"g0": {}}, signer=UNSIGNED, signature=b"",
                    batch_manifest_sha256="m", admitted_at="2026-08-13")
    assert reg.load(c.id, 1).code_sha256 == row.code_sha256
    assert reg.root() != before


def test_nc__Q38_domain_separation_is_load_bearing() -> None:
    """NC-Q38. The classic two-leaf / one-internal collision."""
    import hashlib

    from cdfc.predicates.registry import INTERNAL_PREFIX, LEAF_PREFIX, registry_root

    a, b = "11" * 32, "22" * 32
    root = registry_root([a, b])
    naive = hashlib.sha256(bytes.fromhex(a) + bytes.fromhex(b)).hexdigest()
    assert root != naive
    assert LEAF_PREFIX == b"\x00" and INTERNAL_PREFIX == b"\x01"


def test_nc__Q55_admission_requires_a_human() -> None:
    """NC-Q55. And the signer is not a constant or an environment default: the ONLY constant
    permitted is the literal `UNSIGNED`, which every surface renders beside the count."""
    import os

    from cdfc.predicates.registry import UNSIGNED, UNSIGNED_BADGE, Registry
    from cdfc.qualify.errors import UnsignedAdmissionError

    r, _it, _store, _tbl, _facts, _hf, _rt = _fme_world()
    reg = Registry()
    with pytest.raises(UnsignedAdmissionError):
        reg.admit(r.candidates[0], {}, signer="A. Human", signature=b"",
                  batch_manifest_sha256="m", admitted_at="2026-08-13")
    row = reg.admit(r.candidates[0], {}, signer=UNSIGNED, signature=b"",
                    batch_manifest_sha256="m", admitted_at="2026-08-13")
    assert row.signer == UNSIGNED and row.badge() == UNSIGNED_BADGE
    assert UNSIGNED not in os.environ, "the unsigned signer is a literal, not an environment value"
    doc = (Path(__file__).resolve().parents[2] / "docs/measurements/P7-attrition.md").read_text()
    assert "UNSIGNED" in doc, "the weakening is published where the admitted count is read"


def test_nc__Q36_removal_is_recorded() -> None:
    """NC-Q36. A subsumed predicate that vanishes without a row moves the settled fraction with no
    cause on the chart."""
    from cdfc.qualify import ilp

    class C:
        def __init__(self, i):
            self.id = i

    sel = ilp.select([C("a"), C("b")], subsumes=lambda x, y: x.id == "a" and y.id == "b",
                     cells_of={"b": 9})
    assert sel.kept == ("a",)
    assert len(sel.removals) == 1
    assert sel.removals[0].subsumed_by == "a"
    assert sel.removals[0].cells_would_have_covered == 9


def test_nc__Q36b_a_non_subsumed_predicate_is_retained() -> None:
    from cdfc.qualify import ilp

    class C:
        def __init__(self, i):
            self.id = i

    sel = ilp.select([C("a"), C("b")], subsumes=lambda x, y: False, cells_of={})
    assert sel.kept == ("a", "b") and not sel.removals


def test_nc__Q07_unknown_is_unproven() -> None:
    """NC-Q07. `unknown` must never be recorded as PROVED. It does not reject either — the
    empirical arm decides — but it never earns `non_degenerate`."""
    from cdfc.qualify import g3_degeneracy
    from cdfc.qualify.domain import load as load_domain

    root = Path(__file__).resolve().parents[2]
    r, _it, _store, _tbl, _facts, _hf, _rt = _fme_world()
    dom = load_domain(root / "domain-policy-v1.json")
    unproven = [c for c in r.candidates
                if g3_degeneracy.proof_arm(c, dom, harvest_class=r.class_of[c.id])
                .measured["verdict"] == "unknown"]
    assert unproven, "no candidate is unproven; this guard has nothing to point at"
    for c in unproven[:10]:
        o = g3_degeneracy.proof_arm(c, dom, harvest_class=r.class_of[c.id])
        assert o.measured["proved"] is False
        assert o.measured["verdict"] != "non_degenerate"


def test_nc__Q07b_a_proved_predicate_is_recorded_as_proved() -> None:
    """The admission-side twin: `proved` is not simply always False."""
    import dataclasses

    from cdfc.qualify import g3_degeneracy
    from cdfc.qualify.domain import load as load_domain

    root = Path(__file__).resolve().parents[2]
    r, _it, _store, _tbl, _facts, _hf, _rt = _fme_world()
    dom = load_domain(root / "domain-policy-v1.json")
    o = g3_degeneracy.proof_arm(dataclasses.replace(r.candidates[0], expr="filing.a.v >= 0"),
                                dom, harvest_class="sum_identity")
    assert o.measured["proved"] is True and o.passed
