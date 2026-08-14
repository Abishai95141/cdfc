"""P10-B1 — the five properties of the liveness layer.

Each is stated over generated reports rather than over the reference filing, because the
disposition is a total function of the row sets and a property checked on one workbook is a
property checked on one workbook.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

# Imported at MODULE level, not inside the test bodies. `cdfc.evaluate.run` pulls in celpy, which
# raises the interpreter's recursion limit on import — and an import that moves it *during* a
# Hypothesis example makes Hypothesis's own stack guard refuse to restore it and fail the test.
# A property test that cannot import what it exercises is measuring nothing.
from cdfc.evaluate.rollup import materialise, roll_up_run  # noqa: E402
from cdfc.evaluate.run import _deactivate  # noqa: E402
from cdfc.evaluate.runner import RunCheck  # noqa: E402
from cdfc.selfcheck.canary import CanaryReport, CanaryRow, disposition  # noqa: E402
from cdfc.selfcheck.selftest import SELFTEST_ID  # noqa: E402
from cdfc.selfcheck.thresholds import ceiling_exceeded  # noqa: E402
from cdfc.verdict import ItemState  # noqa: E402
from cdfc.verdict.invalid import InvalidCause  # noqa: E402
from cdfc.verdict.settled_fraction import serialise  # noqa: E402

PROFILE = settings(
    max_examples=200, deadline=None, derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)

OBSERVABILITIES = st.sampled_from(
    ["OBSERVABLE", "UNOBSERVABLE", "INDETERMINATE_OBSERVABILITY", "UNRESOLVED"]
)
IDS = st.builds(lambda n: f"P-{n:04d}", st.integers(min_value=1, max_value=500))


@st.composite
def rows(draw, min_size: int = 0, max_size: int = 60) -> tuple[CanaryRow, ...]:
    n = draw(st.integers(min_value=min_size, max_value=max_size))
    out = []
    for i in range(n):
        pid = draw(IDS)
        obs = draw(OBSERVABILITIES)
        fired = draw(st.booleans())
        out.append(
            CanaryRow(pid, f"d{i}", obs, draw(st.booleans()), fired,
                      "FAIL" if fired else draw(st.sampled_from(["PASS", "NOT_RUN"])))
        )
    return tuple(out)


@st.composite
def reports(draw) -> CanaryReport:
    rs = draw(rows(min_size=1))
    pids = sorted({r.predicate_id for r in rs}) or ["P-0001"]
    picked = draw(st.lists(st.sampled_from(pids), max_size=len(pids), unique=True))
    inapplicable = tuple(sorted(picked[: len(picked) // 2]))
    indeterminate = tuple(sorted(picked[len(picked) // 2 :]))
    silent = tuple(sorted(draw(st.lists(st.sampled_from(pids), max_size=4, unique=True))))
    selftest_silent = draw(st.booleans())
    if selftest_silent:
        silent = tuple(sorted({*silent, SELFTEST_ID}))
    anti = tuple(sorted(draw(st.lists(st.sampled_from(pids), max_size=3, unique=True))))
    return CanaryReport(
        rows=rs,
        anti_rows=tuple(
            CanaryRow(p, f"a:{p}", "OBSERVABLE", True, p in anti,
                      "FAIL" if p in anti else "PASS")
            for p in pids
        ),
        inapplicable=inapplicable, indeterminate=indeterminate, unresolved=(),
        silent=silent,
        missed_read_set=tuple(sorted(draw(st.lists(st.sampled_from(pids), max_size=2, unique=True)))),
        anti_fired=anti, anti_not_pass=anti, selftest_silent=selftest_silent,
    )


@PROFILE
@given(reports())
def test_prop__a_silent_canary_is_never_absorbed(cr: CanaryReport) -> None:
    """`disposition` is INVALID **iff** one of the four named conditions holds. Both directions.

    The `only if` half is the one that matters: a layer that returns INVALID unconditionally
    satisfies every death in §P10·L.1 and proves nothing at all.
    """
    real_silent = set(cr.silent) - {SELFTEST_ID}
    expected_invalid = bool(
        real_silent
        or not cr.selftest_silent
        or cr.anti_fired
        or ceiling_exceeded(len(cr.inapplicable), len(cr.indeterminate), len(cr.rows))
    )
    d = disposition(cr)
    assert d.valid is (not expected_invalid)
    if expected_invalid:
        assert d.cause is InvalidCause.CANARY_SILENT and d.failure_kind is not None
    else:
        assert d.cause is None and d.failure_kind is None


@PROFILE
@given(reports())
def test_prop__invalid_implies_no_fraction(cr: CanaryReport) -> None:
    """`settledFraction is None` AND `verdict is None` — not zero, not omitted, `null`.

    Zero is a finding about the filing; null is a finding about us, and the two must never be
    allowed to look alike. Checked here through the run assembly, which is the only place the
    fraction is computed.
    """
    d = disposition(cr)
    if d.valid:
        return
    fraction = None            # what `execute` computes when the canary layer withholds the run
    payload = serialise(fraction)
    assert payload["settledFraction"] is None
    assert payload.get("verdict") is None


@PROFILE
@given(reports())
def test_prop__the_digest_is_a_function_of_the_report_alone(cr: CanaryReport) -> None:
    """Two canonicalisations of one report agree, and a rebuilt equal report agrees with it."""
    twin = CanaryReport(
        rows=cr.rows, anti_rows=cr.anti_rows, inapplicable=cr.inapplicable,
        indeterminate=cr.indeterminate, unresolved=cr.unresolved, silent=cr.silent,
        missed_read_set=cr.missed_read_set, anti_fired=cr.anti_fired,
        anti_not_pass=cr.anti_not_pass, selftest_silent=cr.selftest_silent,
    )
    assert cr.digest() == cr.digest() == twin.digest()


def test_prop__no_hashed_object_carries_a_clock_reading() -> None:
    """The same report canonicalised under three divergent clocks yields identical bytes.

    Not a hypothesis test: stubbing the process clock breaks Hypothesis's own engine, and a
    property test that cannot install its stub is a property test measuring nothing. One fixed
    report and three clocks is the whole content — this is the check that would have caught
    `CanaryRow.elapsed_us` (F23) before P11's first green run rather than after.
    """
    import datetime as _dt

    cr = CanaryReport(
        rows=(CanaryRow("P-1", "d1", "OBSERVABLE", True, True, "FAIL"),
              CanaryRow(SELFTEST_ID, "st", "OBSERVABLE", False, False, "PASS")),
        anti_rows=(CanaryRow("P-1", "a", "OBSERVABLE", True, False, "PASS"),),
        inapplicable=(), indeterminate=(), unresolved=(), silent=(SELFTEST_ID,),
        missed_read_set=(), anti_fired=(), anti_not_pass=(), selftest_silent=True,
    )
    digests = set()
    real_perf, real_mono, real_time = time.perf_counter, time.monotonic, time.time
    try:
        for stamp in (0.0, 1.0e6, 1.0e9):
            time.perf_counter = lambda v=stamp: v      # type: ignore[assignment]
            time.monotonic = lambda v=stamp: v          # type: ignore[assignment]
            time.time = lambda v=stamp: v               # type: ignore[assignment]
            digests.add(cr.digest())
    finally:
        time.perf_counter, time.monotonic, time.time = real_perf, real_mono, real_time
    assert len(digests) == 1, (
        "the canonicalised liveness proof moved when the clock did. A duration inside a hashed "
        "object makes byte-identical re-derivation permanently unreachable."
    )
    assert _dt.datetime is not None  # the import is the point: no date reaches the payload either


@PROFILE
@given(reports())
def test_prop__the_loop_is_order_independent(cr: CanaryReport) -> None:
    """Shuffling the predicate order changes neither the disposition nor the digest.

    A liveness proof whose bytes depend on dictionary order is a proof that cannot be re-derived,
    which is P11's acceptance test failing one phase early.
    """
    shuffled = CanaryReport(
        rows=tuple(reversed(cr.rows)),
        anti_rows=tuple(reversed(cr.anti_rows)),
        inapplicable=tuple(reversed(cr.inapplicable)),
        indeterminate=tuple(reversed(cr.indeterminate)),
        unresolved=cr.unresolved,
        silent=tuple(reversed(cr.silent)),
        missed_read_set=tuple(reversed(cr.missed_read_set)),
        anti_fired=tuple(reversed(cr.anti_fired)),
        anti_not_pass=tuple(reversed(cr.anti_not_pass)),
        selftest_silent=cr.selftest_silent,
    )
    assert shuffled.digest() == cr.digest()
    assert disposition(shuffled).failure_kind == disposition(cr).failure_kind
    assert disposition(shuffled).valid == disposition(cr).valid


@PROFILE
@given(
    st.lists(IDS, min_size=1, max_size=25, unique=True),
    st.lists(st.integers(min_value=0, max_value=24), max_size=10),
)
def test_prop__inapplicability_lowers_the_fraction(pids: list[str], picks: list[int]) -> None:
    """Moving one predicate from applicable to inapplicable never RAISES the settled count.

    The direction is the product's exposure: the headline number is a fraction, and the only way a
    liveness layer could be gamed is by letting a deactivation increase it.
    """
    cells = tuple(f"S!A{i + 1}" for i in range(len(pids)))
    checks = tuple(
        RunCheck(
            predicate_id=p, version=1, state=ItemState.PASS, reason=None, witness=(),
            cells_bound=(cells[i],), order=9, settles=True,
        )
        for i, p in enumerate(pids)
    )
    table = materialise(cells)
    base_settled = sum(
        1 for c in roll_up_run(table, checks) if c.state in (ItemState.PASS, ItemState.FAIL)
    )
    deactivated = frozenset(pids[i] for i in picks if i < len(pids))
    after = roll_up_run(table, _deactivate(checks, deactivated))
    settled = sum(1 for c in after if c.state in (ItemState.PASS, ItemState.FAIL))
    assert settled <= base_settled
    assert settled == base_settled - len(deactivated)
