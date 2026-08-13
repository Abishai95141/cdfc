"""P8 — the corpus oracles, Wilson, set-FFR, G4's independence check and the severity tiers."""

from __future__ import annotations

import dataclasses
import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.qualify import g4_ffr, severity, wilson  # noqa: E402
from cdfc.qualify.corpus.provenance import (  # noqa: E402
    ADMISSIBLE,
    NON_SYNTHETIC,
    CorpusProvenance,
    UninformativeCorpusError,
)
from cdfc.qualify.corpus.template_computed import (  # noqa: E402
    CleanFiling,
    DerivedBy,
    generator_closure,
    synthesise,
)
from cdfc.qualify.set_ffr import FireMatrix, marginal_ffr, set_ffr  # noqa: E402

FME = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


@pytest.fixture(scope="module")
def fme():
    return harvest(FME)


def _filing(derived_by, cells, *, provenance=CorpusProvenance.TEMPLATE_COMPUTED, closure=None):
    return CleanFiling(
        path=Path(f"x-{derived_by.value}.xlsx"), sha256="a" * 64, provenance=provenance,
        derived_by=derived_by,
        derived_engine_digest="e" * 64 if derived_by is DerivedBy.FOREIGN_ENGINE else None,
        computed_cells=frozenset(cells),
        generator_import_closure=frozenset(closure if closure is not None
                                           else generator_closure(derived_by)),
        seed=1,
    )


# --- provenance -------------------------------------------------------------------------


def test_contract__six_corpus_provenances():
    assert len(CorpusProvenance) == 6
    assert CorpusProvenance.REGISTER_DERIVED.value == "REGISTER-DERIVED"
    assert ADMISSIBLE == frozenset(CorpusProvenance) - {CorpusProvenance.SELF_AUTHORED}
    assert NON_SYNTHETIC == frozenset({
        CorpusProvenance.BLIND_FILLED, CorpusProvenance.REAL_PARTNER, CorpusProvenance.PUBLIC})


# --- Wilson -----------------------------------------------------------------------------


def test_wilson__the_spec_values():
    assert wilson.wilson(0, 4)[2] == Decimal("0.489891")
    assert wilson.wilson(2, 96)[1:] == (Decimal("0.005732"), Decimal("0.072807"))
    assert wilson.wilson(0, 340)[2] == Decimal("0.011172")


def test_wilson__lower_bound_is_clamped_to_zero():
    """`-0.000000` must never reach a surface: a reader who sees a negative rate stops believing
    the column."""
    lo = wilson.wilson(0, 340)[1]
    assert lo == 0 and str(lo) == "0.000000"


def test_wilson__zero_sample_raises():
    with pytest.raises(wilson.ZeroSampleError, match="not a small rate"):
        wilson.wilson(0, 0)


def test_wilson__z_is_a_pinned_constant():
    assert wilson.WILSON_Z == Decimal("1.959963984540054")


def test_wilson__blocking_threshold_is_n_189_at_zero_fires():
    """**The spec's 'roughly n >= 185' is DERIVED and off by four.** The module computes it."""
    assert wilson.n_for_upper_bound(Decimal("0.02")) == 189
    assert wilson.wilson(0, 188)[2] > Decimal("0.02") >= wilson.wilson(0, 189)[2]


def test_wilson__thirty_filings_do_not_license_advisory():
    """**A correction P8 measured against its own plan.** F37 says *30 blind-filled workbooks
    satisfy G-CORPUS and license ADVISORY (hi(0,30) = 0.1139)*. The parenthetical is right and the
    conclusion is not: `ADVISORY_MAX` is 0.10."""
    assert wilson.wilson(0, 30)[2] > severity.ADVISORY_MAX
    assert wilson.n_for_upper_bound(severity.ADVISORY_MAX) == 35


def test_wilson__math_is_not_in_this_module():
    """NC-Q56: a `float` bound makes two machines produce two 6-dp strings and the attestation
    stops re-deriving. Asserted on the SOURCE, not on the numbers happening to agree."""
    import ast

    tree = ast.parse((REPO / "src/cdfc/qualify/wilson.py").read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert "math" not in imported, "NC-Q56: a float bound stops the attestation re-deriving"
    calls = {n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "float" not in calls
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "sqrt" in attrs, "Decimal.sqrt, with the pinned context"


# --- set-FFR ----------------------------------------------------------------------------


def test_set_ffr__is_at_least_one_and_not_the_mean():
    m = FireMatrix(filings=("a", "b", "c", "d"),
                   fires={"P1": frozenset({"a"}), "P2": frozenset({"b"})})
    assert set_ffr(["P1", "P2"], m) == Decimal(1) / 2 or set_ffr(["P1", "P2"], m).numerator == 1
    assert set_ffr(["P1", "P2"], m).numerator / set_ffr(["P1", "P2"], m).denominator == 0.5, (
        "a MEAN would say 1/4; the union of two disjoint fire sets is 2/4"
    )


def test_set_ffr__subadditivity_holds_and_the_mean_violates_it():
    from fractions import Fraction

    m = FireMatrix(filings=tuple("abcdefgh"),
                   fires={"P1": frozenset({"a", "b"}), "P2": frozenset({"c"})})
    s, f = ["P1"], "P2"
    lower = max(set_ffr(s, m), set_ffr([f], m))
    upper = set_ffr(s, m) + set_ffr([f], m)
    union = set_ffr([*s, f], m)
    assert lower <= union <= upper
    mean = (set_ffr(s, m) + set_ffr([f], m)) / 2
    assert mean < lower, "the mean implementation violates the subadditivity LOWER bound"
    assert marginal_ffr(s, f, m) == (Fraction(1, 8), ("P1",))


def test_set_ffr__a_fire_on_an_uncounted_filing_is_refused():
    with pytest.raises(ValueError, match="shared-denominator"):
        FireMatrix(filings=("a",), fires={"P1": frozenset({"z"})})


# --- the derived_by split (F2) ------------------------------------------------------------


def test_tc__foreign_engine_closure_excludes_calc():
    """And `cdfc.calc` is PRESENT under CALC — the positive control, because a check that cannot
    detect the case it exists for is not a check."""
    calc = generator_closure(DerivedBy.CALC)
    foreign = generator_closure(DerivedBy.FOREIGN_ENGINE)
    assert any(m.startswith("cdfc.calc") for m in calc)
    assert not any(m.startswith("cdfc.calc") for m in foreign)


def test_tc__computed_cells_are_recorded_and_exact(tmp_path):
    made = synthesise(FME, tmp_path, seed=7, n=1, derived_by=DerivedBy.NONE)
    assert made[0].computed_cells == frozenset()
    with pytest.raises(ValueError, match="NONE means nobody derived anything"):
        _filing(DerivedBy.NONE, {"S!A1"})
    with pytest.raises(ValueError, match="computed_cells is EMPTY"):
        _filing(DerivedBy.CALC, set())


def test_tc__an_engine_digest_is_required_exactly_where_it_means_something():
    with pytest.raises(ValueError, match="no engine digest"):
        CleanFiling(path=Path("x"), sha256="a" * 64,
                    provenance=CorpusProvenance.TEMPLATE_COMPUTED,
                    derived_by=DerivedBy.FOREIGN_ENGINE, derived_engine_digest=None,
                    computed_cells=frozenset({"S!A1"}), generator_import_closure=frozenset(), seed=1)
    with pytest.raises(ValueError, match="an engine digest under derived_by"):
        CleanFiling(path=Path("x"), sha256="a" * 64,
                    provenance=CorpusProvenance.TEMPLATE_COMPUTED, derived_by=DerivedBy.CALC,
                    derived_engine_digest="e" * 64, computed_cells=frozenset({"S!A1"}),
                    generator_import_closure=frozenset(), seed=1)


def test_tc__every_output_is_labelled(tmp_path):
    made = synthesise(FME, tmp_path, seed=7, n=1, derived_by=DerivedBy.NONE)
    side = json.loads(made[0].path.with_suffix(".prov.json").read_text(encoding="utf-8"))
    assert side["CDFC_SYNTHETIC"] is True
    assert side["CDFC_PROVENANCE"] == "TEMPLATE-COMPUTED"
    assert side["CDFC_DERIVED_BY"] == "NONE"
    assert side["may_be_quoted_as"].endswith(".") and " " in side["may_be_quoted_as"], (
        "`may_be_quoted_as` is a SENTENCE: a fixture whose licence you cannot read off its own "
        "record is one somebody will reuse in the wrong gate"
    )


# --- G4's independence (F2 / F5) -----------------------------------------------------------


def test_clean_corpus_is_not_produced_by_the_code_under_test(fme):
    """**F2 / F5.** An arithmetic predicate against a `derived_by=CALC` corpus raises. The SAME
    predicate against `FOREIGN_ENGINE` is admitted, and the record carries the engine digest."""
    arithmetic = next(c for c in fme.candidates if fme.class_of[c.id] == "sum_identity")
    read = g4_ffr.read_cells(arithmetic, fme.schema)
    assert read, "the predicate must read something for this test to mean anything"

    # 40 filings, so the INTERVAL is not what decides this: `hi(0, 1)` is 0.79 and would reject
    # for a reason that has nothing to do with independence.
    matrix = FireMatrix(filings=tuple(f"f{i}" for i in range(40)), fires={})
    calc = g4_ffr.CleanCorpus("calc", tuple(_filing(DerivedBy.CALC, read) for _ in range(40)))
    with pytest.raises(UninformativeCorpusError, match="not independent"):
        g4_ffr.check(arithmetic, calc, matrix, [], fme.schema)

    foreign = g4_ffr.CleanCorpus(
        "foreign", tuple(_filing(DerivedBy.FOREIGN_ENGINE, read) for _ in range(40)))
    out = g4_ffr.check(arithmetic, foreign, matrix, [], fme.schema)
    assert out.passed
    assert out.measured["corpus_derived_engine_digest"] == "e" * 64
    assert out.measured["clean_corpus_independent_of_predicate"] is True


def test_template_computed_licenses_a_membership_ffr(fme):
    """The second positive control: on a `CALC` corpus a predicate reading only INPUT cells is
    admitted, because its read set never touches `computed_cells`. Without this the repair has
    replaced a false number with no number."""
    membership = next(c for c in fme.candidates if fme.class_of[c.id] == "membership")
    read = g4_ffr.read_cells(membership, fme.schema)
    other = {"3. Portfolio!ZZ1", "3. Portfolio!ZZ2"}
    assert not (read & other)
    calc = g4_ffr.CleanCorpus("calc", tuple(_filing(DerivedBy.CALC, other) for _ in range(40)))
    out = g4_ffr.check(membership, calc,
                       FireMatrix(filings=tuple(f"f{i}" for i in range(40)), fires={}), [],
                       fme.schema)
    assert out.passed and out.measured["clean_corpus_independent_of_predicate"] is True


def test_g4__self_authored_raises_rather_than_returning_zero(fme):
    corpus = g4_ffr.CleanCorpus("self", (_filing(DerivedBy.NONE, set(),
                                                 provenance=CorpusProvenance.SELF_AUTHORED),))
    with pytest.raises(UninformativeCorpusError, match="shape of evidence"):
        g4_ffr.check(fme.candidates[0], corpus, FireMatrix(filings=("f",), fires={}), [], fme.schema)


def test_g4__a_foreign_engine_sharing_a_module_is_not_independent(fme):
    """Conjunct (1)'s escape hatch is a CLOSURE check, not a label. A `FOREIGN_ENGINE` corpus whose
    generator shares a module with the evaluator is not independent, whatever it is called."""
    arithmetic = next(c for c in fme.candidates if fme.class_of[c.id] == "sum_identity")
    read = g4_ffr.read_cells(arithmetic, fme.schema)
    shared = g4_ffr.evaluation_import_closure(arithmetic)
    corpus = g4_ffr.CleanCorpus(
        "liar", (_filing(DerivedBy.FOREIGN_ENGINE, read, closure=shared),))
    with pytest.raises(UninformativeCorpusError, match="shared modules"):
        g4_ffr.check(arithmetic, corpus, FireMatrix(filings=("f",), fires={}), [], fme.schema)


def test_contract__independence_is_a_property_not_a_field(fme):
    """`clean_corpus_independent_of_predicate` has **no setter and no constructor argument**, and
    the loader recomputes it and refuses a disagreement."""
    assert not hasattr(g4_ffr.Independence, "set_independent")
    import ast

    tree = ast.parse((REPO / "src/cdfc/qualify/g4_ffr.py").read_text(encoding="utf-8"))
    keywords = {k.arg for n in ast.walk(tree) if isinstance(n, ast.Call) for k in n.keywords}
    assert "clean_corpus_independent_of_predicate" not in keywords, (
        "the field is CONSTRUCTED nowhere: it is the return value of independent()"
    )
    assert not any(isinstance(n, ast.arg) and n.arg == "clean_corpus_independent_of_predicate"
                   for n in ast.walk(tree)), "and it is not a parameter either"

    cand = fme.candidates[0]
    corpus = g4_ffr.CleanCorpus(
        "c", tuple(_filing(DerivedBy.FOREIGN_ENGINE, {"S!ZZ1"}) for _ in range(40)))
    good = g4_ffr.check(cand, corpus,
                        FireMatrix(filings=tuple(f"f{i}" for i in range(40)), fires={}), [],
                        fme.schema)
    g4_ffr.load_g4(good.measured, corpus, cand, fme.schema)  # must not raise

    lied = {**good.measured, "clean_corpus_independent_of_predicate": False}
    with pytest.raises(g4_ffr.IncompleteG4Record, match="no setter"):
        g4_ffr.load_g4(lied, corpus, cand, fme.schema)


def test_contract__g4_record_is_complete(fme):
    cand = fme.candidates[0]
    corpus = g4_ffr.CleanCorpus(
        "c", tuple(_filing(DerivedBy.FOREIGN_ENGINE, {"S!ZZ1"}) for _ in range(40)))
    rec = g4_ffr.check(cand, corpus,
                       FireMatrix(filings=tuple(f"f{i}" for i in range(40)), fires={}), [],
                       fme.schema).measured
    for field in g4_ffr.REQUIRED_G4_FIELDS:
        with pytest.raises(g4_ffr.IncompleteG4Record, match="does not load"):
            g4_ffr.load_g4({k: v for k, v in rec.items() if k != field}, corpus, cand, fme.schema)


def test_g4__the_wildcard_predicate_is_refused(fme):
    """**THE DEMONSTRATION SURVIVES THE FIX THAT REMOVED ITS SUBJECT.**

    `P-0009` translated `COUNTIF(G54:G63, "*Restricted*")` as a string equality and fired on 18 of
    40 clean filings. It is now a typed skip, so the predicate is reconstructed here and G4 is
    asserted to refuse it — otherwise the repair would have deleted the evidence that the gate
    works.
    """
    cand = dataclasses.replace(fme.candidates[0], id="P-WILDCARD")
    corpus = g4_ffr.CleanCorpus(
        "foreign", tuple(_filing(DerivedBy.FOREIGN_ENGINE, {"S!ZZ1"}) for _ in range(40)))
    fires = FireMatrix(filings=tuple(f"f{i}" for i in range(40)),
                       fires={"P-WILDCARD": frozenset(f"f{i}" for i in range(18))})
    out = g4_ffr.check(cand, corpus, fires, [], fme.schema)
    assert not out.passed and out.reason == g4_ffr.Reason.ABOVE_ADVISORY
    assert out.measured["fired"] == 18 and out.measured["n"] == 40
    assert Decimal(out.measured["wilson"][1]) > severity.ADVISORY_MAX
    assert severity.tier(out.measured).tier is severity.Severity.NOT_ADMITTED


# --- severity ------------------------------------------------------------------------------


def _rec(k, n, ns, prov="TEMPLATE-COMPUTED", independent=True):
    _p, lo, hi = wilson.wilson(k, n)
    return {"wilson": [str(lo), str(hi)], "n": n, "n_non_synthetic": ns,
            "corpus_provenance": prov, "clean_corpus_independent_of_predicate": independent}


def test_severity__uses_wilson_upper():
    assert severity.tier(_rec(0, 4, 0)).tier is severity.Severity.NOT_ADMITTED
    assert severity.tier(_rec(2, 96, 96)).tier is severity.Severity.ADVISORY
    assert severity.tier(_rec(0, 189, 30)).tier is severity.Severity.BLOCKING


def test_severity__synthetic_corpus_cannot_buy_blocking():
    """**F2 / F12 — the adversary's one-command attack, asserted as a test.**"""
    d = severity.tier(_rec(0, 189, 0))
    assert d.tier is severity.Severity.ADVISORY
    assert "one command" in d.reason
    assert str(severity.BLOCKING_MIN_NON_SYNTHETIC) in d.render()


def test_severity__thresholds_are_constants_and_are_pre_registered():
    assert severity.BLOCKING_MAX == Decimal("0.02")
    assert severity.ADVISORY_MAX == Decimal("0.10")
    assert severity.BLOCKING_MIN_NON_SYNTHETIC == 30
    pre = (REPO / "experiments/P8/PREREGISTRATION.md").read_text(encoding="utf-8")
    for token in ("BLOCKING_MAX", "0.02", "ADVISORY_MAX", "0.10",
                  "BLOCKING_MIN_NON_SYNTHETIC", "30"):
        assert token in pre, f"{token} is not inside the pre-registration's hash"


def test_severity__self_authored_and_non_independent_are_undefined_not_advisory():
    with pytest.raises(UninformativeCorpusError, match="UNDEFINED"):
        severity.tier(_rec(0, 189, 30, prov="SELF-AUTHORED"))
    with pytest.raises(UninformativeCorpusError, match="F5"):
        severity.tier(_rec(0, 189, 30, independent=False))


def test_severity__a_tier_never_renders_without_its_interval():
    r = severity.tier(_rec(0, 189, 30)).render()
    assert "Wilson hi" in r and "n=" in r and "n_non_synthetic=" in r
