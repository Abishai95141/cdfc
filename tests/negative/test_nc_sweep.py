"""The sweep, run as a test — registry row 10's real form.

`test_nc_meta__every_expected_guard_flipped` is the exact-set assertion. Its predecessor
asserted "at least one guard fails", under which an entry is caught the moment its
WEAKEST guard goes red and the guard the whole story rests on may never be exercised.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
REPORT = REPO / "reports" / "negative-control-sweep.json"


def _report() -> dict:
    if not REPORT.exists():
        # CDFC_REQUIRE_SWEEP is set by the CI stage that runs AFTER the sweep. Without it
        # these three tests skipped in every CI run — the report is gitignored, the tests
        # ran before the sweep, and the exact-set contract was therefore never asserted
        # as a test. Found by verifying in a fresh clone, not by running in place.
        if os.environ.get("CDFC_REQUIRE_SWEEP"):
            pytest.fail("the sweep report is missing at a stage that requires it")
        pytest.skip("run `make nc-sweep` first; the sweep is a separate CI stage")
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
    trusting a plausible-looking quotation in a PR description.

    **THIS ASSERTED ONLY THAT THE FIELD WAS NON-EMPTY**, and the sweep supplied the literal
    `"reported failed"` whenever no line was captured — so the test could never fail, and 13 of
    160 red guards carried the placeholder rather than an assertion. The lookup matched only a
    traceback keyed on the guard's OWN file, so any guard whose assertion is raised deeper (a
    `RegistryError` out of `src/cdfc/gates.py`) fell through.

    The capture now falls back to any line from the guard's own run, and a genuine absence is a
    NAMED sentinel that cannot read as a quotation. This test counts them.
    """
    sys.path.insert(0, str(REPO / "tools"))
    from nc_sweep import NO_ASSERTION_CAPTURED  # noqa: PLC0415

    rep = _report()
    red = uncaptured = 0
    for row in rep["rows"]:
        for g in row["guards"]:
            if not g["observed_red"]:
                continue
            red += 1
            assert g["assertion_text"], f"{row['id']} {g['path']}: no assertion captured"
            assert g["node_id"], f"{row['id']} {g['path']}: no node id captured"
            if g["assertion_text"] == NO_ASSERTION_CAPTURED:
                uncaptured += 1
    assert red, "no guard went red; this test would pass over an empty sweep"
    assert uncaptured == 0, (
        f"{uncaptured} of {red} red guards carry no quotable assertion. A reviewer cannot open "
        "what the sweep did not capture."
    )


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
