"""P3 negative controls."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from injectors import FloatInCalc, inject, run_gate  # noqa: E402


def test_nc__E13_float_in_the_core_is_rejected() -> None:
    assert run_gate("ci/no-float-money.sh") == 0, "precondition: green on a Decimal-only core"
    with inject(FloatInCalc()):
        rc = run_gate("ci/no-float-money.sh")
    assert rc != 0, "a float reached the deterministic numeric core and the gate passed"
