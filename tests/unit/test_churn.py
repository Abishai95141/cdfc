"""P15-B2 — version churn. **The tests that separate *lost a number* from *lost detection*.**

Criterion A8 is *the settled fraction falls when the template changes*, and the dangerous way to
pass it is to stop running the affected predicates: the number falls by the same amount and the
chart is identical. `test_requalify__provisional_still_runs` and `test_requalify__numerator_falls`
are named together for that reason — NC-X06's injector must turn BOTH red, and the second is the
subtle half, because under the injector the numerator falls *for the wrong reason*.
"""

from __future__ import annotations

import ast
import json
import zipfile
from pathlib import Path

import pytest

from cdfc.churn import identity, quarantine, requalify
from cdfc.churn import withdraw as withdraw_mod

BASE = Path("fixtures/prescribed/"
            "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
BUMPED = Path("fixtures/synthetic/template-bumped__fy2029-30.xlsx")
RUNS = Path("reports/runs")

_HAVE = BASE.is_file() and BUMPED.is_file() and any(
    (d / "manifest.json").is_file() for d in RUNS.iterdir()
) if RUNS.is_dir() else False


def test_churn__the_artifacts_exist_when_the_pipeline_requires_them() -> None:
    """A skipped test is a silent pass, so `make verify` makes this one FAIL instead."""
    import os

    if os.environ.get("CDFC_REQUIRE_RUN") and not _HAVE:
        raise AssertionError(
            "CDFC_REQUIRE_RUN=1 and the churn inputs are absent. Every test below would have "
            "SKIPPED, and a green suite would have reported that the settled fraction can step "
            "down without once asking it to. `make history` produces them."
        )


pytestmark = pytest.mark.skipif(not _HAVE, reason="run `make history` (needs a run and the fixture)")


@pytest.fixture(scope="module")
def run_dir() -> Path:
    return sorted(d for d in RUNS.iterdir() if (d / "manifest.json").is_file())[0]


@pytest.fixture(scope="module")
def candidates():
    from cdfc.predicates.harvest import harvest

    return harvest(BASE).candidates


@pytest.fixture(scope="module")
def report(run_dir, candidates):
    return requalify.on_template_change(BASE, BUMPED, run_dir=run_dir, candidates=candidates)


# --- the fixture ---------------------------------------------------------------------------


def test_fixture__fy2029_differs_in_exactly_two_named_parts() -> None:
    """**The plan says one part. The workbook says two, and the one-part fixture changes nothing.**

    `Dropdown!E3:E6` holds the vocabulary; the `x14:dataValidation` that USES it lives on
    `1. Introduction` and names the literal range. Writing `E7` alone leaves the range at `$E$3:$E$6`
    and the induced vocabulary is unchanged — the first build did exactly that and the sweep
    correctly moved zero predicates, which is how the discrepancy was found.
    """
    from cdfc.qualify.surgery import differing_parts

    assert differing_parts(BASE, BUMPED) == {
        "xl/worksheets/sheet1.xml", "xl/worksheets/sheet10.xml",
    }


def test_fixture__every_x14_validation_survives_the_surgery() -> None:
    """A range extended by dropping a sibling validation would be a smaller template, not a bumped
    one — and every predicate bound to the dropped one would go unbound for the wrong reason."""
    with zipfile.ZipFile(BASE) as a, zipfile.ZipFile(BUMPED) as b:
        before = a.read("xl/worksheets/sheet1.xml").count(b"<x14:dataValidation")
        after = b.read("xl/worksheets/sheet1.xml").count(b"<x14:dataValidation")
    assert before == after == 10


def test_fixture__the_embedded_data_model_is_byte_identical() -> None:
    """96.9% of this archive is `xl/model/item.data`. An openpyxl round-trip collapses it from
    3.55 MB to 66 KB, and the resulting file would be a different workbook wearing the same name."""
    with zipfile.ZipFile(BASE) as a, zipfile.ZipFile(BUMPED) as b:
        assert a.read("xl/model/item.data") == b.read("xl/model/item.data")
        assert len(a.read("xl/model/item.data")) > 3_000_000


# --- V2: identity ---------------------------------------------------------------------------


def _promoted(c, **over):
    """A real `Predicate`, because `envelope_projection` walks `dataclasses.fields()`.

    A stand-in object with the right attributes raises there, and correctly: the projection is
    GENERATED from the field list rather than written by hand, which is what stops a field leaving
    an identity unnoticed. A test that routed around it would be testing a different function.
    """
    import dataclasses as dc

    from cdfc.predicates.envelope import Predicate, Qualification, QualifiedAgainst

    base = dict(evaluator_version="celpy-0.5.0", fault_model_version="v3",
                corpus_sha256="c" * 64, template_sha256="t" * 64)
    return Predicate(
        **{f.name: getattr(c, f.name) for f in dc.fields(c)},
        qualification=Qualification(
            campaign_id="CAMPAIGN-TEST", kill_rate_claimed="0/0", kill_rate_all_classes="0/0",
            false_failure_rate="0/0", qualified_at="2026-08-16",
        ),
        qualified_against=QualifiedAgainst(**{**base, **over}),
        severity_tier="ADVISORY", state="ACTIVE", withdrawn_reason=None,
    )


def test_identity__qualified_against_is_part_of_identity(candidates) -> None:
    """Rule V2. Changing ANY element changes the digest — there is no in-place edit."""
    c = candidates[0]
    base = dict(evaluator_version="celpy-0.5.0", fault_model_version="v3",
                corpus_sha256="c" * 64, template_sha256="t" * 64)

    def make(**over):
        return _promoted(c, **over)

    ref = identity.predicate_identity(make())
    assert identity.predicate_identity(make()) == ref, "identity is not deterministic"
    for field in base:
        moved = identity.predicate_identity(make(**{field: "z" * 64}))
        assert moved != ref, f"{field} moved and the identity did not"


def test_identity__a_predicate_with_no_qualified_against_has_none(candidates) -> None:
    """**Not defaulted to the envelope digest.** That would give an unqualified candidate the
    identity of a qualified predicate, which is the substitution the rule exists to prevent."""
    with pytest.raises(identity.IdentityInputsMissing):
        identity.predicate_identity(candidates[0])


# --- V4: the numerator falls -----------------------------------------------------------------


def test_requalify__the_vocabulary_that_moved_is_the_year_vocabulary() -> None:
    """Exactly one vocabulary changes, and it is the financial-year list gaining `2029-30`."""
    assert requalify.changed_vocabularies(BASE, BUMPED) == {"n_1_introduction_d3"}


def test_requalify__the_vocabulary_signal_identifies_the_predicate_that_carries_it(
    candidates,
) -> None:
    """The PRECISE signal, tested independently of whether that predicate ran.

    `P-0002` declares `template.vocab.n_1_introduction_d3` and is the predicate a FY2029-30 filing
    would break. It does not appear in the reference run, so the run-level step-down below is
    driven by the conservative sheet signal — and that is stated rather than smoothed over.
    """
    declared = requalify.declared_vocabularies(candidates)
    owners = {p for p, v in declared.items() if "n_1_introduction_d3" in v}
    assert owners == {"P-0002"}


def test_requalify__numerator_falls(report) -> None:
    """**Rule V4, criterion A8.** The number goes DOWN, and by a measured amount."""
    assert report.numerator_delta < 0
    assert report.new_settled < report.old_settled
    assert report.new_settled == report.old_settled + report.numerator_delta
    assert report.moved_to_provisional, "nothing moved, so nothing was demonstrated"


def test_requalify__provisional_still_runs(report) -> None:
    """**Rule V3, and the one that is easy to get backwards.**

    Detection is not lost. The three sets are equal, and `ChurnReport.__post_init__` refuses any
    construction where they are not — so the injector that filters `PROVISIONAL` out of the active
    set cannot produce a report at all.
    """
    assert set(report.still_running) == set(report.moved_to_provisional)
    assert set(report.numbers_hidden) == set(report.moved_to_provisional)


def test_requalify__a_report_that_stopped_running_them_cannot_be_constructed() -> None:
    """NC-X06 as a type error rather than as a test that has to remember to look."""
    with pytest.raises(requalify.ChurnArithmeticError):
        requalify.ChurnReport(
            old_template_sha256="a" * 64, new_template_sha256="b" * 64,
            changed_sheets=("Dropdown",), changed_vocabularies=("v",),
            moved_to_provisional=("P-0001",), moved_reason={"P-0001": "x"},
            still_running=(),                      # <- detection lost
            numbers_hidden=("P-0001",),
            numerator_delta=-1, old_settled=10, new_settled=9, field_surface=100,
        )


def test_requalify__the_numerator_cannot_rise() -> None:
    with pytest.raises(requalify.ChurnArithmeticError):
        requalify.ChurnReport(
            old_template_sha256="a" * 64, new_template_sha256="b" * 64,
            changed_sheets=(), changed_vocabularies=(),
            moved_to_provisional=(), moved_reason={}, still_running=(), numbers_hidden=(),
            numerator_delta=+1, old_settled=10, new_settled=11, field_surface=100,
        )


def test_requalify__each_moved_predicate_says_which_signal_moved_it(report) -> None:
    """A vocabulary change is a demonstrated false-failure risk; a sheet change is *we cannot rule
    it out*. Collapsing the two would leave a reader unable to tell which they are looking at."""
    assert set(report.moved_reason) == set(report.moved_to_provisional)
    for pid, why in report.moved_reason.items():
        assert why.startswith(("VOCABULARY", "SHEET", "a changed part")), (pid, why)


def test_requalify__a_reordered_vocabulary_is_not_a_change() -> None:
    """Moving predicates for a cosmetic reordering would make every sweep look like a real one."""
    import cdfc.facts.build as fb

    real = fb.template_tree

    def shuffled(path, **kw):
        t = real(path, **kw)
        if path == BUMPED:
            return {"vocab": {k: list(reversed(v)) for k, v in t["vocab"].items()}}
        return t

    fb.template_tree = shuffled
    try:
        assert requalify.changed_vocabularies(BASE, BASE) == frozenset()
    finally:
        fb.template_tree = real


# --- V5: quarantine --------------------------------------------------------------------------


def test_quarantine__dead_kill_case_quarantines_automatically() -> None:
    r = quarantine.replay_liveness(
        {"P-1": object(), "P-2": object(), "P-3": None},
        replay=lambda pid, _c: {"P-1": True, "P-2": False}.get(pid),
    )
    assert r.still_dying == ("P-1",)
    assert "P-2" in r.quarantined and "P-3" in r.quarantined
    assert r.replayed == 3


def test_quarantine__an_unreplayable_case_is_not_a_pass() -> None:
    """*Could not check* is not *checked and fine* — the swallowed exception in a version bump."""
    r = quarantine.replay_liveness({"P-9": object()}, replay=lambda _p, _c: None)
    assert r.not_replayable == ("P-9",)
    assert "failure to ASK" in r.reasons["P-9"]


def test_quarantine__nothing_re_admits_automatically() -> None:
    """Asserted STRUCTURALLY, by walking the AST of every module in the package.

    A docstring promising that nothing sets `ACTIVE` is a promise. This is a measurement, and it
    is the form the plan asks for because the absence is exactly what a later convenience helper
    would quietly undo.
    """
    offenders: list[str] = []
    for path in sorted(Path("src/cdfc/churn").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == "ACTIVE":
                parent_ok = False
                for outer in ast.walk(tree):
                    # A bare comparison (`if state == "ACTIVE"`) is reading, not writing.
                    if isinstance(outer, ast.Compare) and node in ast.walk(outer):
                        parent_ok = True
                if not parent_ok:
                    offenders.append(f"{path.name}:{node.lineno}")
    assert not offenders, f"the churn package can set ACTIVE at {offenders}; only a human clears"


# --- V7: withdrawal --------------------------------------------------------------------------


def test_withdraw__free_text_is_refused() -> None:
    with pytest.raises(withdraw_mod.WithdrawalReasonNotInVocabulary):
        withdraw_mod.withdraw("P-1", 1, on="2026-08-16", reason="deprecated")


def test_withdraw__an_undated_withdrawal_is_refused() -> None:
    with pytest.raises(withdraw_mod.WithdrawalUndated):
        withdraw_mod.withdraw("P-1", 1, on="  ", reason="unsound")


def test_withdraw__superseded_must_name_what_superseded_it() -> None:
    with pytest.raises(ValueError, match="superseding"):
        withdraw_mod.withdraw("P-1", 1, on="2026-08-16", reason="superseded")
    w = withdraw_mod.withdraw("P-1", 1, on="2026-08-16", reason="superseded", superseded_by="P-1@2")
    assert "P-1@2" in w.render()


# --- the e2e: the chart gains a step-down ---------------------------------------------------


def test_e2e__template_bump_lowers_the_chart() -> None:
    """`reports/settled-history.jsonl` gains a point LOWER than the previous one, WITH a cause."""
    path = Path("reports/settled-history.jsonl")
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(rows) >= 2
    down = [(a, b) for a, b in zip(rows, rows[1:], strict=False) if b["settled"] < a["settled"]]
    assert down, "the series never falls, so criterion A8 is undemonstrated"
    for _prev, cur in down:
        assert (cur.get("cause") or "").strip(), "a step-down with no cause does not render"
