"""P10-B1 — the loop, the anti-canary, and the disposition.

Most of these are over synthesised `CanaryReport`s, deliberately: the disposition is a total
function of the row sets, and testing it through a workbook would test the workbook.
`test_c__the_loop_runs_end_to_end_on_the_reference_filing` is the one that runs the real thing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.selfcheck.canary import CanaryReport, CanaryRow, disposition  # noqa: E402
from cdfc.selfcheck.selftest import SELFTEST_ID  # noqa: E402
from cdfc.verdict.invalid import InvalidCause  # noqa: E402
from cdfc.verdict.reasons import ReasonCode  # noqa: E402

OBS = "OBSERVABLE"
UNOBS = "UNOBSERVABLE"
IND = "INDETERMINATE_OBSERVABILITY"


def _row(
    pid: str, *, obs: str = OBS, reads: bool = True, fired: bool = True, outcome: str | None = None
) -> CanaryRow:
    state = outcome if outcome is not None else ("FAIL" if fired else "PASS")
    return CanaryRow(pid, f"d:{pid}:{obs}:{fired}", obs, reads, fired, state)


def _report(
    *,
    rows: tuple[CanaryRow, ...] = (),
    anti: tuple[CanaryRow, ...] = (),
    inapplicable: tuple[str, ...] = (),
    indeterminate: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
    silent: tuple[str, ...] = (SELFTEST_ID,),
    missed: tuple[str, ...] = (),
    anti_fired: tuple[str, ...] = (),
    anti_not_pass: tuple[str, ...] = (),
    selftest_silent: bool = True,
) -> CanaryReport:
    return CanaryReport(
        rows=rows or (_row("P-1"), _row(SELFTEST_ID, fired=False)),
        anti_rows=anti or (_row("P-1", fired=False),),
        inapplicable=inapplicable, indeterminate=indeterminate, unresolved=unresolved,
        silent=silent, missed_read_set=missed, anti_fired=anti_fired,
        anti_not_pass=anti_not_pass or anti_fired, selftest_silent=selftest_silent,
    )


# --- D5: the counts are row counts, never variables ----------------------------------------


def test_c__counts_are_row_counts_not_variables() -> None:
    """Every published count is `len()` of a row set. There is no assignment for a defect in.

    The split between `rowsTotal` and `canariesRun` is the self-test's, and it is published rather
    than hidden: the self-test is silent BY DESIGN, so counting it in `canariesPassed` would make
    every healthy run look one canary short for ever. Its outcome is `selfTestSilent`, and
    `rowsTotal` carries the undivided count so the split cannot conceal a row.
    """
    rows = tuple(_row(f"P-{i}") for i in range(7)) + (_row(SELFTEST_ID, fired=False),)
    cr = _report(rows=rows, anti=tuple(_row(f"P-{i}", fired=False) for i in range(7)))
    proof = cr.as_liveness_proof()
    assert proof["rowsTotal"] == len(cr.rows) == 8
    assert proof["canariesRun"] == len(cr.predicate_rows) == 7
    assert proof["antiCanariesRun"] == len(cr.anti_rows) == 7
    assert proof["canariesPassed"] == 7, "the self-test is silent by design and is not a pass"
    for key, value in proof.items():
        assert isinstance(value, (int, bool)), f"{key} is not an integer computed from a row set"


def test_c__a_hard_coded_count_disagrees_with_the_rows() -> None:
    """The admission-side twin of D5: if `canariesRun` were `len(predicates)` it would be 3, not 5."""
    rows = tuple(_row("P-1") for _ in range(5))
    cr = _report(rows=rows)
    assert cr.canaries_run == 5 != 3


# --- the two silent kinds have different remedies -------------------------------------------


def test_c__witness_missing_the_read_set_is_a_distinct_kind() -> None:
    """`WITNESS_MISSES_READ_SET` != `PREDICATE_DID_NOT_FIRE`.

    Different remedies: re-qualify the admission, versus fix the code. Merging them is the SPDX
    `NOASSERTION` collapse in miniature — one label for two facts, and the reader cannot act on it.
    """
    dead_check = _report(silent=(SELFTEST_ID, "P-1"))
    dead_witness = _report(silent=(SELFTEST_ID, "P-1"), missed=("P-1",))
    assert disposition(dead_check).failure_kind == "PREDICATE_DID_NOT_FIRE"
    assert disposition(dead_witness).failure_kind == "WITNESS_MISSES_READ_SET"
    assert "re-qualify" in disposition(dead_witness).detail
    assert "The check is dead" in disposition(dead_check).detail


def test_c__the_dead_predicate_is_named_not_merely_counted() -> None:
    d = disposition(_report(silent=(SELFTEST_ID, "P-0042")))
    assert "P-0042" in d.detail, "a run withheld without naming what died is unactionable"


# --- the four INVALID rows, and the one VALID row -------------------------------------------


def test_c__a_healthy_report_is_valid() -> None:
    d = disposition(_report())
    assert d.valid and d.cause is None and d.failure_kind is None


@pytest.mark.parametrize(
    "kw,kind",
    [
        ({"silent": (SELFTEST_ID, "P-1")}, "PREDICATE_DID_NOT_FIRE"),
        ({"selftest_silent": False, "silent": ()}, "SELFTEST_NOT_SILENT"),
        ({"anti_fired": ("P-1",)}, "ANTI_CANARY_FIRED"),
        ({"inapplicable": ("P-1",)}, "WHOLESALE_INAPPLICABILITY"),
    ],
)
def test_c__each_death_is_invalid_canary_silent(kw: dict, kind: str) -> None:
    d = disposition(_report(**kw))
    assert not d.valid
    assert d.cause is InvalidCause.CANARY_SILENT
    assert d.failure_kind == kind


def test_c__the_failure_kind_does_not_depend_on_iteration_order() -> None:
    """Two simultaneous failures report the same kind on every machine."""
    both = _report(selftest_silent=False, silent=("P-1",), anti_fired=("P-2",))
    assert disposition(both).failure_kind == "SELFTEST_NOT_SILENT", (
        "a loop that is not running says nothing trustworthy about a predicate, so its own death "
        "is reported first"
    )


def test_c__the_selftest_alone_being_silent_is_health() -> None:
    assert disposition(_report(silent=(SELFTEST_ID,))).valid
    assert not disposition(_report(silent=(), selftest_silent=False)).valid, (
        "an empty silent set means the always-true check reported that it FIRED"
    )


def test_c__the_selftest_flag_cannot_disagree_with_the_silent_set() -> None:
    """§P10·L.4's hole, closed at the type.

    Reporting `selftest_silent=True` while the self-test is absent from the silent set is the
    one-line injection that makes the disposition go green on a loop that is not running.
    """
    with pytest.raises(ValueError) as e:
        _report(silent=(), selftest_silent=True)
    assert "did not compute" in str(e.value)
    with pytest.raises(ValueError):
        _report(silent=(SELFTEST_ID,), selftest_silent=False)


# --- the anti-canary publishes both readings ------------------------------------------------


def test_c__the_anti_canary_publishes_both_readings() -> None:
    """`plan/05` writes the anti-canary as `state != PASS`; this build turns the disposition on
    `state == FAIL` and publishes both, so the weaker reading is not taken quietly."""
    cr = _report(anti_fired=(), anti_not_pass=("P-9",))
    proof = cr.as_liveness_proof()
    assert proof["antiCanariesFired"] == 0
    assert proof["antiCanariesNotPass"] == 1
    assert disposition(cr).valid, "inapplicability on the pass case is not drift"


# --- the deactivated set, and the fraction that falls ---------------------------------------


def test_c__inapplicable_predicates_are_deactivated_not_passed() -> None:
    """NC-C06. An inapplicable witness scored as a passed canary is a liveness claim nobody made."""
    cr = _report(rows=tuple(_row(f"P-{i}") for i in range(8)), inapplicable=("P-7",))
    assert cr.as_liveness_proof()["canariesInapplicable"] == 1
    d = disposition(cr)
    assert d.valid, "one inapplicable of eight is below the ceiling"
    assert d.deactivated == ("P-7",)
    assert d.deactivated_reason is ReasonCode.NR_DEACTIVATED


def test_c__indeterminate_is_never_pooled_into_inapplicable() -> None:
    """F18. One is a fact about the filing, the other a fact about our evaluator."""
    cr = _report(rows=tuple(_row(f"P-{i}") for i in range(10)),
                 inapplicable=("P-1",), indeterminate=("P-2",))
    proof = cr.as_liveness_proof()
    assert proof["canariesInapplicable"] == 1 and proof["canariesIndeterminate"] == 1
    assert "canariesIndeterminate" in proof and "canariesInapplicable" in proof


def test_c__an_empty_loop_is_not_a_pass() -> None:
    """A build with no canary layer at all attempts nothing. That is not a rate of zero."""
    cr = CanaryReport(rows=(), anti_rows=(), inapplicable=(), indeterminate=(), unresolved=(),
                      silent=(SELFTEST_ID,), missed_read_set=(), anti_fired=(), anti_not_pass=(),
                      selftest_silent=True)
    assert disposition(cr).failure_kind == "WHOLESALE_INAPPLICABILITY"


# --- the digest carries no clock and does not move with order --------------------------------


def test_c__the_digest_is_order_invariant() -> None:
    a = _report(rows=(_row("P-1"), _row("P-2"), _row(SELFTEST_ID, fired=False)))
    b = _report(rows=(_row("P-2"), _row(SELFTEST_ID, fired=False), _row("P-1")))
    assert a.digest() == b.digest()


def test_c__the_row_carries_no_duration_field() -> None:
    """F23, at the type. A duration inside a hashed object makes byte-identity unreachable."""
    import dataclasses

    names = {f.name for f in dataclasses.fields(CanaryRow)}
    assert names == {"predicate_id", "witness_digest", "observability", "intersects_read_set",
                     "fired", "outcome"}
    assert not any("elapsed" in n or n.endswith(("_us", "_ms", "_ns")) for n in names)


# --- the real loop ---------------------------------------------------------------------------


def test_c__first_observable_witness_is_the_canary() -> None:
    """The loop stops at the first observable witness and RECORDS the ones it skipped.

    Recording the skips is what keeps `canariesRun` an honest count of attempts: a loop that
    silently discarded them would report a smaller denominator and a better rate.
    """
    from cdfc.evaluate.liveness import run
    from tests.selfcheck_fixtures import liveness_inputs

    report, _d = run(liveness_inputs())
    by_pred: dict[str, list[CanaryRow]] = {}
    for r in report.rows:
        by_pred.setdefault(r.predicate_id, []).append(r)
    for pid, rows in by_pred.items():
        observable = [r for r in rows if r.observability == OBS]
        assert len(observable) <= 1, f"{pid} evaluated {len(observable)} observable witnesses"
        if observable:
            assert rows[-1] is observable[0], f"{pid} kept going after its canary fired"


def test_c__the_loop_runs_end_to_end_on_the_reference_filing() -> None:
    from cdfc.evaluate.liveness import run
    from tests.selfcheck_fixtures import liveness_inputs, population

    report, d = run(liveness_inputs())
    proof = report.as_liveness_proof()
    assert proof["canariesRun"] > 0, "the layer must EXIST before any claim about it means anything"
    assert proof["antiCanariesRun"] == len(population())
    assert proof["selfTestSilent"] is True
    assert isinstance(d.valid, bool)
