"""P7-B1 — the qualification contract: the gate order, the four states, and the rejection row.

E7.3 is **asserted here rather than believed**, because `migrations/001_qualification.sql` was
written on the strength of it: there is no `REJECTED` predicate state, so a rejected candidate
never acquires a `predicate_id` and lives in `rejection` keyed by `candidate_sha256`.
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.envelope import PREDICATE_STATES  # noqa: E402
from cdfc.qualify.result import (  # noqa: E402
    GATE_COST,
    GATE_ORDER,
    GateId,
    GateOutcome,
    GateSkipReason,
    QualificationRecord,
    RejectionRow,
)

MIGRATION = REPO / "migrations" / "001_qualification.sql"


def test_contract__gate_order_is_the_decided_order():
    """A TUPLE, NOT A COMMENT. Free before cheap before expensive, and the pipeline reads this
    rather than hard-coding a sequence — which is what lets NC-Q34 reverse it."""
    assert GATE_ORDER == (GateId.G0, GateId.G1, GateId.G3P, GateId.G2, GateId.G3E, GateId.G4)
    assert [g.value for g in GATE_ORDER] == ["G0", "G1", "G3p", "G2", "G3e", "G4"]
    assert set(GATE_COST) == set(GATE_ORDER), "every gate declares what it costs"
    # The one expensive stage is placed after two free ones and a bounded one. That ordering IS
    # the cost control, so it is asserted rather than described.
    assert GATE_ORDER.index(GateId.G2) > GATE_ORDER.index(GateId.G0)
    assert GATE_ORDER.index(GateId.G2) > GATE_ORDER.index(GateId.G1)
    assert GATE_ORDER.index(GateId.G2) > GATE_ORDER.index(GateId.G3P)
    assert "EXPENSIVE" in GATE_COST[GateId.G2]


def test_contract__no_rejected_predicate_state():
    """E7.3, asserted. Four states, and REJECTED is not one of them — in the enum AND in the SQL."""
    assert set(PREDICATE_STATES) == {"ACTIVE", "PROVISIONAL", "QUARANTINED", "WITHDRAWN"}
    sql = MIGRATION.read_text(encoding="utf-8")
    # The EXECUTABLE schema, with comment lines removed. The comments say the word `REJECTED`
    # precisely because they explain why it is not a state.
    executable = "\n".join(ln.split("--", 1)[0] for ln in sql.splitlines())
    assert "REJECTED" not in executable
    assert "REJECTED" in sql, "the schema explains WHY it is not a state; that comment is load-bearing"
    m = re.search(r"state\s+TEXT NOT NULL CHECK \(state IN \(([^)]*)\)\)", sql)
    assert m and sorted(x.strip().strip("'") for x in m.group(1).split(",")) == [
        "ACTIVE", "PROVISIONAL", "QUARANTINED", "WITHDRAWN"
    ]


def test_contract__rejection_predicate_id_is_nullable_and_null():
    sql = MIGRATION.read_text(encoding="utf-8")
    assert "predicate_id     TEXT," in sql, "the column exists and is nullable"
    assert "CHECK (predicate_id IS NULL)" in sql, (
        "nullable is not enough: the schema must refuse a non-null predicate_id, because a "
        "rejected candidate never acquires an id at all"
    )
    con = sqlite3.connect(":memory:")
    con.executescript(sql)
    con.execute("INSERT INTO obligation VALUES ('OBL-1','TEMPLATE','template-abc',NULL,NULL,'q',0,1,'harvest')")
    con.execute(
        "INSERT INTO rejection VALUES ('cand-1', NULL, 'OBL-1', 'G2', '{}', 1428, '2026-08-13')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(
            "INSERT INTO rejection VALUES ('cand-2','P-0001','OBL-1','G2','{}',1,'2026-08-13')"
        )


def test_contract__the_migration_refuses_a_mislabelled_obligation():
    """C2 in the schema, in both directions."""
    con = sqlite3.connect(":memory:")
    con.executescript(MIGRATION.read_text(encoding="utf-8"))
    with pytest.raises(sqlite3.IntegrityError):  # TEMPLATE with an FRBR URI
        con.execute("INSERT INTO obligation VALUES ('a','TEMPLATE','template-x','/akn/x',NULL,'q',0,1,'harvest')")
    with pytest.raises(sqlite3.IntegrityError):  # TEMPLATE against a non-template instrument
        con.execute("INSERT INTO obligation VALUES ('b','TEMPLATE','fm-2025',NULL,NULL,'q',0,1,'harvest')")
    with pytest.raises(sqlite3.IntegrityError):  # STATUTE against a pinned blank
        con.execute("INSERT INTO obligation VALUES ('c','STATUTE','template-x',NULL,NULL,'q',0,1,'hand')")
    with pytest.raises(sqlite3.IntegrityError):  # a source outside the closed set
        con.execute("INSERT INTO obligation VALUES ('d','GUESSED','template-x',NULL,NULL,'q',0,1,'hand')")


def test_rejection__cells_would_have_covered_is_required():
    ok = RejectionRow(
        candidate_sha256="a" * 64, predicate_id=None, obligation_id="OBL-1",
        rejecting_gate=GateId.G2, measured={"kr_claimed": "0/41"},
        cells_would_have_covered=1428, rejected_at="2026-08-13",
    )
    assert ok.cells_would_have_covered == 1428
    with pytest.raises(ValueError, match="counterEvidence"):
        RejectionRow(candidate_sha256="a" * 64, predicate_id=None, obligation_id="OBL-1",
                     rejecting_gate=GateId.G2, measured={}, cells_would_have_covered=None,  # type: ignore[arg-type]
                     rejected_at="2026-08-13")
    with pytest.raises(ValueError, match="never acquires a predicate_id"):
        RejectionRow(candidate_sha256="a" * 64, predicate_id="P-0001", obligation_id="OBL-1",  # type: ignore[arg-type]
                     rejecting_gate=GateId.G2, measured={}, cells_would_have_covered=1,
                     rejected_at="2026-08-13")


def test_gate_outcome__a_pass_carries_no_reason_and_a_rejection_carries_one():
    with pytest.raises(ValueError, match="reason on a pass"):
        GateOutcome(gate=GateId.G0, passed=True, measured={}, reason="g0.quote_not_located")
    with pytest.raises(ValueError, match="different remedy"):
        GateOutcome(gate=GateId.G0, passed=False, measured={})
    assert GateOutcome(gate=GateId.G0, passed=True, measured={"provisos_total": 0}).reason is None


def test_gate_skip__is_one_member_and_is_never_a_pass():
    """Stage one renders `entered / skipped / survived` and `skipped` is never counted as a
    survivor, whatever its value. The column exists so a future source cannot enter silently."""
    assert [r.value for r in GateSkipReason] == ["subject_not_built"]
    o = GateOutcome(gate=GateId.G4, passed=True, measured={}, skipped=GateSkipReason.SUBJECT_NOT_BUILT)
    assert o.skipped is GateSkipReason.SUBJECT_NOT_BUILT
    with pytest.raises(ValueError, match="cannot also reject"):
        GateOutcome(gate=GateId.G4, passed=False, measured={}, reason="x",
                    skipped=GateSkipReason.SUBJECT_NOT_BUILT)


def test_qualification_record__carries_exactly_one_rejection():
    """The pipeline stops at the first failure: the stop is the cost control AND the evidence."""
    two = QualificationRecord(
        candidate_sha256="a" * 64, obligation_id="OBL-1", qualified_at="2026-08-13",
        outcomes=(
            GateOutcome(gate=GateId.G0, passed=False, measured={}, reason="g0.quote_not_located"),
            GateOutcome(gate=GateId.G1, passed=False, measured={}, reason="g1.cells_bound_zero"),
        ),
    )
    with pytest.raises(ValueError, match="exactly one gate"):
        _ = two.rejecting

    one = QualificationRecord(
        candidate_sha256="a" * 64, obligation_id="OBL-1", qualified_at="2026-08-13",
        outcomes=(
            GateOutcome(gate=GateId.G0, passed=True, measured={}),
            GateOutcome(gate=GateId.G1, passed=False, measured={}, reason="g1.cells_bound_zero"),
        ),
    )
    assert one.rejecting is not None and one.rejecting.gate is GateId.G1
    assert not one.passed
    assert one.ran_in_order()
