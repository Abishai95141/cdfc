"""Registry row 18 — a displayed total must equal the sum of its own parts.

This gate exists from the first commit because the defect it guards was found in the
build plan itself: §7's critical-path row displayed a total that did not equal the sum
of the per-phase figures it was made of, after two phases were re-estimated. That is the
shared-denominator error in a schedule, and a schedule is read under pressure.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DECOMP = REPO / "plan" / "00-decomposition.md"

ROW_RE = re.compile(
    r"^\s*((?:\d+(?:\.\d+)?\s+)+\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)\s+working days\s*$",
    re.MULTILINE,
)


def _rows(text: str) -> list[tuple[list[float], float]]:
    out = []
    for parts, total in ROW_RE.findall(text):
        out.append(([float(x) for x in parts.split()], float(total)))
    return out


def test_plan__critical_path_total_equals_sum_of_rows() -> None:
    if not DECOMP.exists():
        pytest.skip("plan/00-decomposition.md not present")
    rows = _rows(DECOMP.read_text())
    assert rows, "no critical-path row found; the gate would pass trivially"
    for parts, total in rows:
        assert abs(sum(parts) - total) < 1e-9, (
            f"a displayed total does not equal its parts: {parts} sums to {sum(parts)}, "
            f"displayed {total}"
        )


def test_plan__the_total_check_can_fail() -> None:
    """Negative control for row 18. Without this the gate is a regex that never fires."""
    broken = "P0 → P1\n 8    9    = 99 working days\n"
    rows = _rows(broken)
    assert rows, "the parser did not see the row; the gate would be vacuous"
    parts, total = rows[0]
    assert abs(sum(parts) - total) > 1e-9, "the control is not actually broken"
