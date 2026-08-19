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
ADDED_LIVE_AT_P7 = set(range(48, 57))   # docs/GATE-CHANGES.md, 13 Aug 2026
ADDED_LIVE_AT_P8 = set(range(57, 64))   # docs/GATE-CHANGES.md, 13 Aug 2026
# Rows 64 and 65 guard the P9 ENTRY criteria and their subjects shipped at P3 — they are
# `demonstrable_red_at P9` because that is when the guard was written, not when the code arrived.
ADDED_LIVE_AT_P9 = set(range(64, 78))   # docs/GATE-CHANGES.md, 14 Aug 2026
ADDED_LIVE_AT_P10 = set(range(78, 91))  # docs/GATE-CHANGES.md, 14 Aug 2026
# Row 15 was PENDING from P0: its subject — the attestation schema — did not exist until
# P11 wrote it. It is the only row in this registry to have moved between the two sets,
# and the move is dated in docs/GATE-CHANGES.md.
ADDED_LIVE_AT_P11 = set(range(91, 99)) | {15}  # docs/GATE-CHANGES.md, 15 Aug 2026
# 76 and 77 are gates that RAN in `make greps` from P0 with no row at all — registered
# during the audit repair, so the liveness ratio counts what CI actually executes.
# Rows 14 and 16 moved PENDING -> LIVE at P6: their subjects shipped at P5 and the audit
# found them still deferred. See docs/GATE-CHANGES.md, 13 Aug 2026.
PROMOTED_AT_P6 = {14, 16}
# P12's nine rows. They guard a property no earlier row does: not that a filing was judged
# correctly, but that the criterion deciding what the result MEANS was fixed before the result
# existed. Row 105 is a SIGNATURE check — `decide()` acquiring a keyword-only `override=None`
# changes no behaviour and passes every behavioural test, so nothing behavioural could catch it.
ADDED_LIVE_AT_P12 = set(range(99, 108))  # docs/GATE-CHANGES.md, 15 Aug 2026
# P14-B1's five. Rows 108 and 111 are STRUCTURAL arms of gates plan/07 specifies against a headless
# browser; the browser halves are recorded NOT RUN rather than passed. Row 112 guards the gate's own
# denominator against M1.
ADDED_LIVE_AT_P14 = set(range(108, 116))  # docs/GATE-CHANGES.md, 15 Aug 2026 (B1 108-112, B2 113-115)
# S1, 16 Aug 2026. Row 116 guards the EXTRACTION PARTIES that build a STATUTE instrument. It
# exists because `ci/licence-denylist.sh` (row 11) resolves the RUNTIME set and never sees a
# build-time tool, and the best-scoring PDF arm was AGPL-3.0 -- a denied licence entering through
# a door the gate does not watch. Argument in docs/GATE-CHANGES.md.
ADDED_LIVE_AT_P13 = {116}
# P14-B3 and P14-B4, 16 Aug 2026. 117-119: the API cannot express a pass and the
# portfolio cannot emit a cross-template average. 120-122: the two kill rates, the
# funnel's three integers, and a chart that can step down.
ADDED_LIVE_AT_P14B = {117, 118, 119, 120, 121, 122}
# P13-B0, 16 Aug 2026. The guard precedes the thing it guards: this phase is where a
# model first enters the codebase, and 124 refuses a proposer that ships against its
# own experiment's answer.
ADDED_LIVE_AT_P13B0 = {123, 124, 125}
# A1 adversarial audit, 20 Aug 2026. 126: a sheet name may contain `!` and a reference may
# not, so only the LAST `!` delimits a cell string. `Anchor.parse` right-split and was right;
# eighteen call sites left-split and were not. Argument in docs/GATE-CHANGES.md.
ADDED_LIVE_AT_A1_AUDIT = {126}
LIVE_EXPECTED = (LIVE_AT_P0 | ADDED_LIVE_AT_P4 | ADDED_LIVE_AT_P5 | ADDED_LIVE_AT_P6
                 | ADDED_LIVE_AT_P7 | ADDED_LIVE_AT_P8 | ADDED_LIVE_AT_P9
                 | ADDED_LIVE_AT_P10 | ADDED_LIVE_AT_P11 | ADDED_LIVE_AT_P12
                 | ADDED_LIVE_AT_P13 | ADDED_LIVE_AT_P14 | ADDED_LIVE_AT_P14B
                 | ADDED_LIVE_AT_P13B0 | ADDED_LIVE_AT_A1_AUDIT
                 | PROMOTED_AT_P6)
PENDING_AT_P0 = {14, 15, 16}
# The PENDING set SHRINKS as subjects ship, and a row may only leave it into LIVE — never the
# other way. Keeping `PENDING_AT_P0` frozen and naming the departures separately is what stops a
# gate that resists demonstration being quietly moved back.
# **ROW 15 SHIPPED AT P11, AND THE PENDING SET IS NOW EMPTY.** It was written at P0 — *the
# attestation schema has no `result`/`status`/`pass` at any depth* — and could not be demonstrated
# for eleven phases because there was no schema to walk. P11-B1 wrote one; `injectors/
# banned_names_substring_only.py` makes the walk red; and NC-A01's own shape, a `status` planted
# inside a `$defs` entry referenced from an `allOf` two levels down, is what the descent had to be
# total to catch.
#
# This is the FIRST row in this registry to move between the two sets, and the whole design is that
# doing so fails the build until somebody writes down why. `docs/GATE-CHANGES.md` carries the dated
# row; this literal carries the same date.
PROMOTED_AT_P11 = {15}   # docs/GATE-CHANGES.md, 15 Aug 2026
PENDING_NOW = PENDING_AT_P0 - PROMOTED_AT_P6 - PROMOTED_AT_P11


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


# The sentinel `AddGateRow` injects with. It must stay outside any id the registry can reach, and
# the assertion exists because the alternative — "a number beyond the current registry" — has now
# been outrun by the build TWICE: the injector used 19 until row 19 was registered, then 99 until
# row 99 was registered at P12, and each time a real row silently turned a one-guard control into
# a two-guard exact-set mismatch.
INJECTOR_SENTINEL_ID = 9_999_999


def test_contract__registry_ids_are_below_the_injector_sentinel() -> None:
    """A real row may never collide with the id the duplicate-row injector plants."""
    ids = {g.id for g in parse()}
    assert ids, "an empty registry would make this assertion vacuous"
    assert max(ids) < INJECTOR_SENTINEL_ID, (
        f"gate id {max(ids)} has reached the injector's sentinel {INJECTOR_SENTINEL_ID}. "
        "AddGateRow would then plant a DUPLICATE of a real row, the parser would raise, and a "
        "control that guards one thing would go red for another — which is how this was found, "
        "twice."
    )


def test_contract__registry_rejects_a_phase_outside_both_sequences(tmp_path: Path) -> None:
    """`PHASE_RE` was widened for the A-sequence on 20 Aug 2026. A widened check that admits
    anything is not a check, so this pins what it still refuses."""
    from cdfc.gates import PHASE_RE

    for good in ("P0", "P15", "A0", "A1", "A1c", "A5"):
        assert PHASE_RE.match(good), f"{good} is a real phase and must be admitted"
    for bad in ("P16", "A6", "A2c", "Q1", "", "P", "A", "P1x", "phase1", "A1C"):
        assert not PHASE_RE.match(bad), f"{bad} is not a phase and must be refused"
