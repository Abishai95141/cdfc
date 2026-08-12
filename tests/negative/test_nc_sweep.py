"""The sweep, run as a test — registry row 10's real form.

`test_nc_meta__every_expected_guard_flipped` is the exact-set assertion. Its predecessor
asserted "at least one guard fails", under which an entry is caught the moment its
WEAKEST guard goes red and the guard the whole story rests on may never be exercised.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
REPORT = REPO / "reports" / "negative-control-sweep.json"


def _report() -> dict:
    if not REPORT.exists():
        pytest.skip("run `make nc-sweep` first; the sweep takes minutes and is a separate CI stage")
    return json.loads(REPORT.read_text())


def test_nc_meta__every_expected_guard_flipped() -> None:
    rep = _report()
    assert rep["guards_flipped"] == rep["guards_expected_to_flip"], (
        f"{rep['guards_flipped']} of {rep['guards_expected_to_flip']} guards flipped; "
        "the exact set was not observed"
    )
    for row in rep["rows"]:
        assert not row["error"], f"{row['id']}: {row['error']}"
        assert not row["leaked"], f"{row['id']}: injector leaked into {row['leaked']}"


def test_sweep__records_the_failing_assertion_text() -> None:
    """DoD line C4 must resolve to an artifact, not a paste. Every flipped guard carries
    the captured assertion and its node id, so a reviewer opens a file rather than
    trusting a plausible-looking quotation in a PR description."""
    rep = _report()
    for row in rep["rows"]:
        for g in row["guards"]:
            if g["observed_red"]:
                assert g["assertion_text"], f"{row['id']} {g['path']}: no assertion captured"
                assert g["node_id"], f"{row['id']} {g['path']}: no node id captured"


def test_sweep__provisional_entries_are_excluded_from_caught() -> None:
    rep = _report()
    assert rep["provisional_count"] >= 1
    caught_ids = {r["id"] for r in rep["rows"] if r["caught"]}
    prov_ids = {r["id"] for r in rep["rows"] if r["provisional"]}
    assert not (caught_ids & prov_ids), "a provisional entry was counted as caught"


def test_sweep__report_carries_no_timing_field() -> None:
    """R3. A duration in a hashed or compared artifact makes it non-reproducible."""
    blob = REPORT.read_text() if REPORT.exists() else ""
    for banned in ("elapsed", "duration", "seconds", "_ms", "took"):
        assert banned not in blob, f"the sweep report carries a timing field: {banned!r}"
