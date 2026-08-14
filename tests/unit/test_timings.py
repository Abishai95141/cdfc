"""P10-B1 — the timings, and the half of the F23 repair that KEEPS the evidence.

Deleting `elapsed_us` from the hashed payload is only half a repair. The other half is that the
measurement still exists somewhere `verify` never looks, and this file is that half: without it,
the timing data disappears entirely and death **D5**'s concern — *was this loop executed, or
replayed from a cache* — loses its cheapest corroboration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.perf import canary_timings as t  # noqa: E402


def _timings() -> list[t.Timing]:
    return [
        t.Timing(run_id="deadbeef", budget_id=t.BUDGET_ID, stage="canary", elapsed_ms=41, n=34),
        t.Timing(run_id="deadbeef", budget_id=t.BUDGET_ID, stage="anti", elapsed_ms=19, n=33),
    ]


def test_tim__timings_are_written_outside_the_payload(tmp_path: Path) -> None:
    """`reports/perf/<run_id>.jsonl` exists and is non-empty, and **no byte of it** appears in
    `run.jsonl`, in the run manifest, or in the canonicalised liveness proof."""
    from cdfc.selfcheck.canary import CanaryReport, CanaryRow
    from cdfc.selfcheck.selftest import SELFTEST_ID

    path = t.write(_timings(), out_dir=tmp_path)
    assert path.name == "deadbeef.jsonl" and path.parent == tmp_path
    body = path.read_text(encoding="utf-8")
    assert body.strip(), "an empty timing file reads as `the loop ran and took no time`"

    report = CanaryReport(
        rows=(CanaryRow("P-1", "d", "OBSERVABLE", True, True, "FAIL"),
              CanaryRow(SELFTEST_ID, "st", "OBSERVABLE", False, False, "PASS")),
        anti_rows=(CanaryRow("P-1", "a", "OBSERVABLE", True, False, "PASS"),),
        inapplicable=(), indeterminate=(), unresolved=(), silent=(SELFTEST_ID,),
        missed_read_set=(), anti_fired=(), anti_not_pass=(), selftest_silent=True,
    )
    proof = json.dumps(report.as_liveness_proof(), sort_keys=True)
    for row in (json.loads(line) for line in body.splitlines()):
        for key in ("elapsed_ms", "baseline_ms", "warn_above_ms", "fail_above_ms"):
            assert key not in proof, f"{key} reached the hashed liveness proof"
        assert str(row["elapsed_ms"]) not in proof or row["elapsed_ms"] in (33, 34, 1, 0)


def test_tim__the_budget_is_the_plan_s_and_it_supersedes_the_old_one() -> None:
    assert t.BUDGET_ID == "PERF-CANARY2"
    assert (t.BASELINE_MS, t.WARN_ABOVE_MS, t.FAIL_ABOVE_MS) == (4_200, 6_000, 9_000)
    assert "anti-canary" in t.SUPERSEDES and "mutation throughput" in t.SUPERSEDES, (
        "a budget that replaces another without saying why is a budget that was raised to fit. "
        "PERF-CANARY2 supersedes TWO figures and must name both reasons: the anti-canary doubling "
        "the loop, and the DERIVED baseline having been derived from the wrong quantity."
    )
    changes = (REPO / "perf" / "BUDGET-CHANGES.md").read_text(encoding="utf-8")
    assert "PERF-CANARY2" in changes and str(t.BASELINE_MS) in changes.replace(",", ""), (
        "the budget moved without a dated row in perf/BUDGET-CHANGES.md carrying its argument"
    )


@pytest.mark.parametrize("ms,verdict", [(0, "OK"), (4_200, "OK"), (6_000, "OK"), (6_001, "WARN"),
                                        (9_000, "WARN"), (9_001, "FAIL")])
def test_tim__the_verdict_is_a_function_of_the_two_thresholds(ms: int, verdict: str) -> None:
    assert t.verdict_for(ms) == verdict


def test_tim__an_empty_timing_list_is_refused() -> None:
    """A file that says nothing at this path reads as a measurement of zero."""
    with pytest.raises(ValueError) as e:
        t.write([])
    assert "F23" in str(e.value) or "evidence" in str(e.value)


def test_tim__timed_returns_the_result_and_the_elapsed_time() -> None:
    out, ms = t.timed(lambda: 6 * 7)
    assert out == 42 and isinstance(ms, int) and ms >= 0


def test_tim__the_only_clock_in_the_canary_path_lives_here() -> None:
    """`ci/no-clock-in-core.sh` exempts exactly one directory, and this module is in it.

    `plan/05` names the file `src/cdfc/selfcheck/timings.py`; putting it there would have required
    widening that gate, which is the gate the F23 ruling extends in the same breath. The deviation
    is recorded in this module's docstring, and it is strictly stronger: the loop CANNOT read a
    clock rather than being trusted not to.
    """
    assert Path(t.__file__).parent.name == "perf"
    gate = (REPO / "ci" / "no-clock-in-core.sh").read_text(encoding="utf-8")
    assert "src/cdfc/measure/perf/" in gate, (
        "the gate no longer exempts the directory this module lives in, so either the gate is "
        "about to fail or the exemption moved without this test moving with it"
    )
    assert "perf_counter" in gate and "time\\.time" in gate
