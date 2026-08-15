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
    """R3. A duration in a hashed or compared artifact makes it non-reproducible.

    **Over the report's KEYS, not over its text**, and the difference is not cosmetic. The report
    captures each red guard's assertion message so a reviewer can see WHY it went red — and P10's
    F23 guard is a gate against duration fields, so its message necessarily contains the word
    `elapsed`. A substring scan reads that as a violation and the only way to satisfy it is to
    stop capturing assertion text, which destroys the reviewability the sweep exists for.

    So the ban is on the structure: no key of any object in this report may name a duration. That
    is what "no timing field enters this report" means, and it is checkable without silencing the
    evidence.
    """
    import json as _json

    blob = _json.loads(REPORT.read_text()) if REPORT.exists() else {}
    banned = ("elapsed", "duration", "seconds", "_ms", "took")
    offenders: list[str] = []

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if any(b in str(k).lower() for b in banned):
                    offenders.append(f"{path}.{k}")
                walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    walk(blob, "$")
    assert offenders == [], f"the sweep report carries timing FIELDS: {offenders}"


def test_sweep__no_entry_changes_a_path_it_does_not_declare() -> None:
    """An entry that writes outside its `touches` poisons every entry after it.

    `inject()` digests the declared paths before and after, and is blind by construction to
    anything else — so an undeclared write survives the restore, silently, and the harness reports
    success. **This is the shape of defect the whole harness exists to catch, occurring in the
    harness.**

    The realised instance: `NC-CI14`'s guard runs `ci/catalogue-ids.sh`, which runs
    `plan/scripts/nc_audit.py`, which writes `plan/scripts/nc_audit_result.json`. Under injection
    the plan document carries a NUL byte, so the audit wrote a corrupted result — to a path the
    injector never declared. It stayed in the tree for the remainder of the sweep.

    The lesson in the assertion: **`touches` is everything the entry can change, guard tests
    included** — not only what `apply()` edits.
    """
    rep = _report()
    dirty = {r["id"]: r["contaminated"] for r in rep["rows"] if r.get("contaminated")}
    assert dirty == {}, (
        f"{len(dirty)} entries changed paths their injector does not declare: {dirty}. Each one "
        "survives the restore and is present for every later entry, so the failure it causes is "
        "attributed to whichever control happens to run next."
    )


def test_sweep__a_leak_carries_its_assertion_text() -> None:
    """A leak reported as a bare list of node ids is a rumour.

    The post-restore run's failure text used to be discarded, so `leaked: [...]` said WHICH guard
    was still red and never WHY — and the next person had to reproduce the whole 20-minute sweep to
    learn anything. This asserts the evidence travels with the finding.
    """
    rep = _report()
    for row in rep["rows"]:
        if row["leaked"]:
            assert "leaked after restore:" in row["error"], (
                f"{row['id']} leaked {row['leaked']} and its error carries no assertion text"
            )
