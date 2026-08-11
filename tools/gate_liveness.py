#!/usr/bin/env python
"""P0's measurement: which gates are LIVE, and which have been OBSERVED RED.

This is the number P0 produces that did not exist before. It is deliberately not
"how many gates are written" — writing a gate is free. The quantity that carries
information is **how many have been observed failing on a deliberately broken build**,
because a gate that has never gone red is a preference with a filename.

`observed_red` is populated only by an actual injector run. Nothing here trusts a
declaration.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO))

from cdfc.gates import parse  # noqa: E402
from cdfc.measure.paths import P0_GATE_LIVENESS  # noqa: E402


def _pytest(node: str) -> bool:
    """Run one test node; True if it passes."""
    return (
        subprocess.run(
            [sys.executable, "-m", "pytest", node, "-q", "--no-header"],
            cwd=REPO,
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
        ).returncode
        == 0
    )


# A gate counts as OBSERVED RED only if a test that injects its named broken_build and
# asserts the gate rejects it currently passes. The mapping is explicit: a gate with no
# entry here is NOT counted, and that absence is the honest answer.
OBSERVED_BY: dict[int, str] = {
    1: "tests/negative/test_nc_ci.py::test_nc__CI03_green_tick_gate_rejects_an_all_clear",
    2: "tests/negative/test_nc_ci.py::test_nc__CI04_bare_except_is_rejected",
    3: "tests/negative/test_nc_ci.py::test_nc__CI01_missing_scan_root_fails",
    4: "tests/negative/test_nc_ci.py::test_nc__CI02_openpyxl_warning_is_an_error",
    6: "tests/contract/test_contract_gates.py::test_contract__registry_parser_rejects_a_duplicate_id",
    9: "tests/negative/test_nc_ci.py::test_nc__CI05_a_stub_that_exits_zero_is_rejected",
    13: "tests/negative/test_nc_ci.py::test_nc__CI01_missing_scan_root_fails",
    18: "tests/contract/test_contract_plan.py::test_plan__the_total_check_can_fail",
}


def main() -> int:
    gates = parse()
    live = [g for g in gates if g.liveness == "LIVE"]
    pending = [g for g in gates if g.liveness == "PENDING"]

    observed: dict[int, bool] = {}
    for gid, node in OBSERVED_BY.items():
        observed[gid] = _pytest(node)

    n_observed = sum(1 for v in observed.values() if v)
    result = {
        "phase": "P0",
        "warrant": "MEASURED",
        "gates_total": len(gates),
        "gates_live": len(live),
        "gates_pending": len(pending),
        "gates_with_an_observed_red": n_observed,
        "denominator_for_observed": len(live),
        "observed": {str(k): v for k, v in sorted(observed.items())},
        "live_ids": sorted(g.id for g in live),
        "pending_ids": sorted(g.id for g in pending),
        "note": (
            "gates_with_an_observed_red counts gates for which an injector run currently "
            "demonstrates rejection. Gates without an entry in OBSERVED_BY are NOT counted; "
            "that absence is the measurement, not a rounding-up opportunity."
        ),
    }
    P0_GATE_LIVENESS.parent.mkdir(parents=True, exist_ok=True)
    P0_GATE_LIVENESS.write_text(json.dumps(result, indent=1) + "\n")

    print(f"gates total        : {len(gates)}")
    print(f"  LIVE             : {len(live)}   {sorted(g.id for g in live)}")
    print(f"  PENDING          : {len(pending)}   {sorted(g.id for g in pending)}")
    print(f"OBSERVED RED       : {n_observed} of {len(live)} live gates")
    print(f"  not yet observed : {sorted(set(g.id for g in live) - set(OBSERVED_BY))}")
    print(f"wrote {P0_GATE_LIVENESS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
