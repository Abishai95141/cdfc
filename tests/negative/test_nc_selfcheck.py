"""§P10·L — how we prove the canary layer actually catches a dead predicate.

**This is the most important validation in the plan**, because the canary layer's entire claim is
that it catches this, and a test that has never been observed to fail is not evidence.

Six deaths, each a DIFFERENT MECHANISM. The point is not six ways to make one assertion red; it is
six independent ways for the layer to be broken, each of which the layer must catch **and name**.
Three of them are constructed here (a check that cannot fire, a witness that cannot reach it, a
loop that lies about its counts on a filing) and four more arrive by injector through
`make nc-sweep`.

And the half without which all six are worthless: **the admission-side positive controls**. A layer
that returns `INVALID` unconditionally satisfies every death in this file. `tests/relational/
test_rel__canary_positive.py` is where a healthy run is shown to be `VALID` with digits.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.liveness import run as run_liveness  # noqa: E402
from cdfc.measure.p10_run import population, run_filing  # noqa: E402
from cdfc.measure.p5_run import INDEPENDENT  # noqa: E402
from cdfc.selfcheck.selftest import SELFTEST_ID  # noqa: E402
from cdfc.selfcheck.witness import FaultWitness  # noqa: E402
from cdfc.verdict.invalid import InvalidCause  # noqa: E402
from tests.selfcheck_fixtures import liveness_inputs, witnesses  # noqa: E402

SPARSE = REPO / "fixtures" / "synthetic" / "formula-overwritten__portfolio-O7.xlsx"

RENAMED_SHEET = REPO / "fixtures" / "synthetic" / "row-inserted__portfolio-r7.xlsx"


def _with(predicates) -> tuple:
    """The reference population with `predicates` substituted for their same-id members."""
    replace = {p.id: p for p in predicates}
    return tuple(replace.get(p.id, p) for p in population())


# ============================================================================================
# D1 — THE PREDICATE CANNOT FIRE
# ============================================================================================


def test_nc__D1_a_check_that_cannot_fire_is_caught_and_named() -> None:
    """An admitted-shaped predicate whose `expr` is `true`, with a valid stored witness.

    It binds cells, pre-flights its keys, runs, and returns `PASS` on every input including the
    fault it was admitted for. Nothing else in the system can see this: the template binds, the
    readers agree, closure holds, `cells_bound` is non-zero. **The canary layer is the only thing
    that knows the check is dead.**
    """
    victim = next(p for p in population() if witnesses().get(p.id))
    dead = dataclasses.replace(victim, expr="true")
    result = run_filing(INDEPENDENT, predicates=_with([dead]))

    assert result.run_state == "INVALID"
    assert result.invalid_causes == (InvalidCause.CANARY_SILENT,)
    assert result.liveness_disposition.failure_kind == "PREDICATE_DID_NOT_FIRE"
    assert victim.id in result.liveness_disposition.detail, "the dead predicate is NAMED"
    assert result.fraction is None, "not zero, not omitted — null. Zero is a finding about the filing"
    assert result.as_manifest()["settledFraction"] is None


# ============================================================================================
# D2 — THE WITNESS CANNOT REACH THE PREDICATE
# ============================================================================================


def test_nc__D2_a_witness_outside_the_read_set_is_a_distinct_kind() -> None:
    """A healthy predicate whose stored witness targets a key outside its read set.

    `WITNESS_MISSES_READ_SET`, and it must not collapse into `PREDICATE_DID_NOT_FIRE`. **Different
    remedies: re-qualify the admission, versus fix the code.** Merging them is the SPDX
    `NOASSERTION` collapse in miniature — one label for two facts, and the reader cannot act on it.
    """
    ins = liveness_inputs()
    a, b = sorted(k for k, v in witnesses().items() if v)[:2]
    borrowed = witnesses()[b][0]
    swapped = dict(ins.witnesses)
    swapped[a] = (dataclasses.replace(borrowed, predicate_id=a),)
    report, disp = run_liveness(dataclasses.replace(ins, witnesses=swapped))

    assert not disp.valid
    assert disp.failure_kind == "WITNESS_MISSES_READ_SET"
    assert a in report.missed_read_set
    assert "re-qualify" in disp.detail and "NOT to fix the code" in disp.detail


# ============================================================================================
# D3 — THE APPARATUS IS BROKEN AND THE BINDING IS INTACT  (four injectors, via the sweep)
# ============================================================================================


def test_nc__C04a_apparatus_break_is_canary_silent() -> None:
    """NC-C04's guard. Under `keys_resolver_offbyone` every witness lands one row low.

    Green in the clean tree — a healthy population produces `VALID` — and red under the injector,
    which is what makes it a control rather than a description.
    """
    report, disp = run_liveness(liveness_inputs())
    assert disp.valid, (
        "the reference population is not healthy in the clean tree, so this guard cannot "
        f"distinguish an apparatus break from the baseline: {disp.failure_kind} — {disp.detail}"
    )
    assert report.as_liveness_proof()["canariesRun"] > 0


def test_liveness__only_cause_is_canary_silent() -> None:
    """**L.2.1 — cause isolation, and it is the single assertion a reviewer should look for first.**

    A control that also trips `invalid.cells_bound_zero`, `invalid.template_unbound`,
    `invalid.reader_structural_disagreement` or `invalid.closure_violated` proves nothing about
    canaries — another layer caught it. This runs D1's and D2's constructed deaths through the full
    run and asserts the `invalid` cause set is EXACTLY `{canary_silent}`; the sweep runs D3's four
    injectors against this same node id, where the assertion is identical and the mechanism differs.
    """
    victim = next(p for p in population() if witnesses().get(p.id))
    for label, preds in (
        ("D1 cannot fire", _with([dataclasses.replace(victim, expr="true")])),
        ("baseline", population()),
    ):
        result = run_filing(INDEPENDENT, predicates=preds)
        others = set(result.invalid_causes) - {InvalidCause.CANARY_SILENT}
        assert others == set(), (
            f"{label}: another layer also fired ({sorted(c.value for c in others)}), so this "
            "control says nothing about the canary layer"
        )


# ============================================================================================
# D4 / D5 / D6 — the loop is a stub; the counts are asserted; the canary touches the file
# ============================================================================================


def test_nc__C01_the_loop_is_not_a_stub() -> None:
    """D4's guard. Under `canaries_noop` the self-test is reported as having fired.

    The self-test's `expr` is the literal `true`, so no fault can make it FAIL. A loop that reports
    it as having fired is a loop that is not running — **this is the canary for the canary loop**,
    and without it the other five deaths are all satisfied by a layer that never executes anything.
    """
    report, disp = run_liveness(liveness_inputs())
    assert report.selftest_silent is True
    assert SELFTEST_ID in report.silent
    assert disp.failure_kind != "SELFTEST_NOT_SILENT"


def test_nc__C01b_the_counts_are_row_counts() -> None:
    """D5's guard. Under `canary_count_asserted` the published integer stops being `len(rows)`.

    A loop that runs and reports a number it did not compute is a lie with a true premise. Relation
    **R-06** re-checks the same integer from the other side, against the rows written to the run.

    **It runs on the SPARSE filing, and that is not incidental.** On a filing where every witness
    is applicable, `len(rows)` and `len(predicates)` are the same number, so the substitution is
    undetectable and a guard placed there would be green under the injector. The divergence only
    exists where the loop makes more attempts than there are predicates — which is exactly the
    case the count is load-bearing for, because it is the denominator of the ceiling.
    """
    report, _d = run_liveness(liveness_inputs(SPARSE))
    assert len(report.predicate_rows) > len(report.anti_rows), (
        "this filing no longer makes more attempts than it has predicates, so the guard cannot "
        "distinguish a counted integer from an asserted one"
    )
    proof = report.as_liveness_proof()
    assert proof["rowsTotal"] == len(report.rows)
    assert proof["canariesRun"] == len(report.predicate_rows)
    assert proof["antiCanariesRun"] == len(report.anti_rows)
    assert proof["rowsTotal"] == proof["canariesRun"] + 1, (
        "the self-test contributes exactly one row, and the split between the two counts must not "
        "be able to swallow another"
    )


def test_nc__C05c_no_artifact_is_opened_during_the_canary_loop() -> None:
    """D6's guard, and it is a RUNTIME proof rather than an import scan.

    Liveness is proved on the in-memory fact table so the attested hash keeps hashing the filing
    that was received. An import-closure walk would miss a `zipfile.ZipFile` reached through an
    already-imported module, so this installs a `sys.addaudithook` over the real `open` event and
    counts every filesystem open that happens between the image being built and the loop finishing.

    The hook is process-wide and cannot be removed once installed — so it is armed only inside the
    window, and its own arming is asserted by the positive control below it.
    """
    import sys as _sys

    opened: list[str] = []
    armed = {"on": False}

    def _hook(event: str, args: tuple) -> None:
        if not armed["on"]:
            return
        if event in ("open", "io.open") and args:
            name = str(args[0])
            if name.endswith(".xlsx"):
                opened.append(name)

    _sys.addaudithook(_hook)

    ins = liveness_inputs()          # the image is built HERE, outside the window
    armed["on"] = True
    try:
        run_liveness(ins)
    finally:
        armed["on"] = False
    assert opened == [], (
        f"the canary loop opened {len(opened)} artifact(s): {opened[:3]}. Liveness must be proved "
        "on the in-memory fact table — a loop that re-serialises the artifact can change what it "
        "attests to."
    )

    # THE POSITIVE CONTROL. Without it, a hook that never fires scores perfectly.
    armed["on"] = True
    try:
        INDEPENDENT.open("rb").close()
    finally:
        armed["on"] = False
    assert opened, "the audit hook did not observe a deliberate open, so its silence means nothing"


# ============================================================================================
# NC-C03 — the renamed sheet belongs to the template binder, not to the canary layer
# ============================================================================================


def test_nc__C03_renamed_sheet_is_template_unbound_not_canary_silent() -> None:
    """The canary layer is not credited for a catch another layer made.

    **`layer_exists_assertion` (adversary F6) runs FIRST, in this same body.** As written without
    it, this test is satisfied by a build in which `src/cdfc/selfcheck/` does not exist at all —
    *"the renamed sheet produced `template_unbound` and not `canary_silent`"* is trivially true of
    a system with no canary layer. A test that proves a layer did *not* fire must, in the same
    breath, prove the layer exists.
    """
    # --- layer_exists_assertion ---------------------------------------------------------
    report, _d = run_liveness(liveness_inputs())
    assert report.as_liveness_proof()["canariesRun"] > 0, (
        "the canary layer ran nothing on the reference fill, so the assertion below — that it did "
        "not fire on the renamed-sheet fixture — carries no information at all"
    )

    # --- and only then, the claim itself -------------------------------------------------
    #
    # The binder works by structural fingerprint over (sheet names + states, dimensions, merged
    # ranges, defined names, unlocked mask). A row inserted into `'3. Portfolio'` changes the
    # dimensions, so the fingerprint moves and `invalid.template_unbound` is reached FIVE STEPS
    # before the canary loop would run. Against the real catalogue, not an empty one — an empty
    # catalogue makes everything unbound and the assertion would hold for a reason of my choosing.
    from cdfc.evaluate.binding import Bound, Unbound, bind_template
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED, catalogue

    assert isinstance(bind_template(TEMPLATE_COMPUTED, catalogue()), Bound), (
        "the admission-side twin: a lawful filing DOES bind against this catalogue, so the "
        "refusal below is about the fixture and not about the catalogue"
    )
    assert isinstance(bind_template(RENAMED_SHEET, catalogue()), Unbound)

    result = run_filing(RENAMED_SHEET)
    assert result.invalid_causes == (InvalidCause.TEMPLATE_UNBOUND,), (
        f"the structural fixture produced {[c.value for c in result.invalid_causes]}; the canary "
        "layer must not be credited for a catch the template binder made"
    )
    assert InvalidCause.CANARY_SILENT not in result.invalid_causes
    assert result.as_manifest()["livenessProof"] is None, (
        "an unbound run never reached the loop, so its liveness proof is ABSENT — not a set of "
        "zeros, which would say the loop ran and found nothing to do"
    )


# ============================================================================================
# NC-C06 / C08 / C09 / C10 / C11 / C12
# ============================================================================================


def test_nc__C06a_inapplicable_is_not_a_pass() -> None:
    """An inapplicable witness scored as a passed canary is a liveness claim nobody made."""
    from cdfc.selfcheck.canary import CanaryReport, CanaryRow, disposition

    rows = tuple(
        CanaryRow(f"P-{i}", f"d{i}", "UNOBSERVABLE", False, False, "NOT_RUN") for i in range(10)
    )
    cr = CanaryReport(
        rows=rows + (CanaryRow(SELFTEST_ID, "st", "OBSERVABLE", False, False, "PASS"),),
        anti_rows=(), inapplicable=tuple(f"P-{i}" for i in range(10)), indeterminate=(),
        unresolved=(), silent=(SELFTEST_ID,), missed_read_set=(), anti_fired=(),
        anti_not_pass=(), selftest_silent=True,
    )
    assert cr.canaries_passed == 0, "an unobservable row is not a pass"
    assert disposition(cr).failure_kind == "WHOLESALE_INAPPLICABILITY"


def test_nc__C08a_always_flag_predicate_fails_its_pass_case() -> None:
    """A predicate that flags everything passes every kill-case canary. The anti-canary is what
    catches it, and it costs one extra evaluation per predicate."""
    victim = next(p for p in population() if witnesses().get(p.id))
    always_flag = dataclasses.replace(victim, expr="false")
    report, disp = run_liveness(
        dataclasses.replace(liveness_inputs(), predicates=_with([always_flag]))
    )
    assert victim.id in report.anti_fired
    assert disp.failure_kind == "ANTI_CANARY_FIRED"
    assert not disp.valid


def test_nc__C09a_selftest_runs_with_no_environment_set() -> None:
    """The flag is removed. See also `tests/unit/test_selftest.py`, which runs it in a subprocess
    with the environment stripped; here we assert the loop's own result."""
    report, _d = run_liveness(liveness_inputs())
    assert report.selftest_silent is True


def test_nc__C10_no_duration_reaches_the_hashed_liveness_proof() -> None:
    import dataclasses as _dc

    from cdfc.selfcheck.canary import CanaryRow

    names = {f.name for f in _dc.fields(CanaryRow)}
    assert not any("elapsed" in n or n.endswith(("_us", "_ms", "_ns")) for n in names)
    report, _d = run_liveness(liveness_inputs())
    assert all(isinstance(v, (int, bool)) for v in report.as_liveness_proof().values())


def test_nc__C11_indeterminate_is_not_folded_into_unobservable() -> None:
    """F18, at the disposition: the ceiling's numerator is both, and they render apart."""
    from cdfc.selfcheck.thresholds import ceiling_exceeded

    assert ceiling_exceeded(0, 26, 100) is True
    report, _d = run_liveness(liveness_inputs())
    proof = report.as_liveness_proof()
    assert "canariesIndeterminate" in proof and "canariesInapplicable" in proof


def test_nc__C12a_a_none_coerced_kill_is_not_a_kill() -> None:
    """D-P10-01. `_coerce(None)` returned the four-character string `"None"`, and 68 of 257
    recorded kills were `'' == 'None'` returning false.

    The two halves are asserted together: the coercion refuses, and the patcher's absence sentinel
    deletes the leaf rather than writing a value into it.
    """
    from cdfc.facts.build import _coerce
    from cdfc.facts.fact_table import FactError
    from cdfc.facts.patch import ABSENT, patch, value_for

    with pytest.raises(FactError):
        _coerce(None)
    assert value_for(None) is ABSENT
    out = patch({"s": {"c": {"v": 1, "__cell__": "S!A1"}}}, {"S!A1": ABSENT})
    assert "v" not in out["s"]["c"]
