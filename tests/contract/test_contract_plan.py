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


# --- P9's exit gate, and the two criteria it met IN PART -------------------------------------


def test_contract__p9_exit_gate_states_its_partial_criteria() -> None:
    """**The exit gate is a claim, so it gets a guard.**

    Two of P9's nine criteria are met in part, and both partial answers are published with the
    reason and the repair. If either is later completed, this test fails — which is the point: a
    phase document that silently becomes true is a phase document nobody re-read. The repair is
    to move the criterion to MET in the same commit that makes it so.
    """
    import json
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo / "src"))
    text = (repo / "docs" / "measurements" / "P9-exit-gate.md").read_text(encoding="utf-8")
    assert text.count("**MET IN PART**") == 2
    assert text.count("**MET**") == 7

    # Criterion 3 is partial because the flagship cannot become a CEL envelope.
    from cdfc.probes.qualify import RelationEnvelopeError, to_envelope
    from cdfc.probes.relations.registry import load

    by_id = {s.id: s for s in load()}
    try:
        to_envelope(by_id["R-01"], "0" * 64)
    except RelationEnvelopeError:
        pass
    else:  # pragma: no cover - the branch this test exists to catch
        raise AssertionError(
            "R-01 now converts to an envelope. Criterion 3 is no longer MET IN PART and "
            "P9-exit-gate.md must be moved in this commit."
        )

    # Criterion 4 is partial because a relation has no obligation, so G0 RAISES before any gate
    # arithmetic. Asserted against the real pipeline rather than against a stored number: the
    # first version of this guard checked `bound == 0`, which was a mechanism asserted from
    # plausibility, and the relations bind 10, 11 and 10 cells.
    from cdfc.predicates.obligations import ObligationError
    from cdfc.probes.qualify import to_envelope as _to_envelope

    d = json.loads(
        (repo / "docs" / "measurements" / "p9-relation-attrition.json").read_text(encoding="utf-8")
    )
    assert all(row["bound"] > 0 for row in d["rows"]), "the converted relations do bind cells"
    assert all(row["delta"] == 0 for row in d["rows"]), (
        "a relation now reaches a cell the harvest does not; the delta column has moved"
    )

    from cdfc.predicates.harvest import harvest
    from cdfc.predicates.obligations import generate_template_obligations
    from cdfc.qualify.template_instrument import emit

    fme = (
        repo / "fixtures" / "prescribed"
        / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
    )
    res = harvest(fme)
    obligations = generate_template_obligations(res, emit(fme))
    cand = _to_envelope(by_id["R-02"], res.template_sha256)
    try:
        obligations[cand.obligation_id]
    except ObligationError:
        pass
    else:  # pragma: no cover - the branch this test exists to catch
        raise AssertionError(
            "a relation now has an obligation, so it can enter the pipeline. Criterion 4 is no "
            "longer MET IN PART and P9-exit-gate.md must be moved in this commit."
        )
