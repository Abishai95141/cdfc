"""Contract tests over the gate registry."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cdfc.gates import RegistryError, live_ids, parse, pending_ids  # noqa: E402

# PRE-REGISTERED AS LITERAL SETS. Moving a row between them fails the build unless
# ci/GATES.md carries an appended, dated argument naming the row.
#
# Why a set and not a count: the exit gate was `gates_live == gates_written`, where
# `gates_written` meant "the gates whose subject exists" -- decided by the same person
# deciding whether a gate can be demonstrated. Any gate that resisted demonstration
# could be moved to PENDING and the ratio would become n/n. The gate could not fail.
# Each phase's additions are a SEPARATE frozen literal, never an edit to an earlier one. A row
# that was LIVE at P0 stays in `LIVE_AT_P0` for ever, so a row cannot quietly leave the LIVE set
# by being edited out of a growing list — which is the failure the pre-registration exists to
# prevent, and which a single mutable set would permit.
LIVE_AT_P0 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20}
ADDED_LIVE_AT_P4 = {21, 22, 23, 24, 25, 26, 27}   # docs/GATE-CHANGES.md, 12 Aug 2026
ADDED_LIVE_AT_P5 = {28, 29, 30, 31, 32, 33, 34, 35, 36}   # docs/GATE-CHANGES.md, 12 Aug 2026
ADDED_LIVE_AT_P6 = set(range(37, 48))   # docs/GATE-CHANGES.md, 13 Aug 2026
# Rows 14 and 16 moved PENDING -> LIVE at P6: their subjects shipped at P5 and the audit
# found them still deferred. See docs/GATE-CHANGES.md, 13 Aug 2026.
PROMOTED_AT_P6 = {14, 16}
LIVE_EXPECTED = (LIVE_AT_P0 | ADDED_LIVE_AT_P4 | ADDED_LIVE_AT_P5 | ADDED_LIVE_AT_P6
                 | PROMOTED_AT_P6)
PENDING_AT_P0 = {14, 15, 16}
# The PENDING set SHRINKS as subjects ship, and a row may only leave it into LIVE — never the
# other way. Keeping `PENDING_AT_P0` frozen and naming the departures separately is what stops a
# gate that resists demonstration being quietly moved back.
PENDING_NOW = PENDING_AT_P0 - PROMOTED_AT_P6


def test_contract__gates_registry_schema() -> None:
    gates = parse()
    assert len(gates) == len(LIVE_EXPECTED | PENDING_NOW)
    assert len({g.id for g in gates}) == len(gates), "gate ids must be unique"
    for g in gates:
        assert g.kind and g.gate and g.broken_build


def test_contract__pending_rows_name_a_phase() -> None:
    """There is no permanently-pending gate."""
    for g in parse():
        assert g.demonstrable_red_at, f"gate {g.id} can never be observed red"


def test_contract__live_set_is_pre_registered() -> None:
    gates = parse()
    assert live_ids(gates) == LIVE_EXPECTED, "the LIVE set changed without a dated argument"
    assert pending_ids(gates) == PENDING_NOW, "the PENDING set changed without a dated argument"
    assert PROMOTED_AT_P6 <= LIVE_EXPECTED, "a promoted row must be LIVE"
    assert PROMOTED_AT_P6 <= PENDING_AT_P0, "only a row that WAS pending can be promoted"
    assert LIVE_EXPECTED & PENDING_NOW == set()
    assert len(LIVE_EXPECTED | PENDING_NOW) == len(gates)
    assert LIVE_AT_P0 <= live_ids(gates), (
        "a gate that was LIVE at P0 has left the LIVE set. Demoting a gate is exactly what the "
        "pre-registration exists to make impossible without a dated argument."
    )


def test_contract__registry_parser_rejects_a_duplicate_id(tmp_path: Path) -> None:
    """Negative control for the parser itself: a tolerant parser over a registry is how
    a registry comes to have fewer rows than it appears to."""
    src = Path("ci/GATES.md").read_text()
    dup = src.replace("| 18 | pytest |", "| 17 | pytest |", 1)
    p = tmp_path / "GATES.md"
    p.write_text(dup)
    with pytest.raises(RegistryError, match="duplicate gate id"):
        parse(p)


def test_contract__registry_parser_rejects_a_nul_byte(tmp_path: Path) -> None:
    """A NUL makes grep skip the whole file. Found once already, in this project."""
    p = tmp_path / "GATES.md"
    p.write_bytes(Path("ci/GATES.md").read_bytes() + b"\x00")
    with pytest.raises(RegistryError, match="NUL"):
        parse(p)
