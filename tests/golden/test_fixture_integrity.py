"""The evidence base, asserted file by file AND value by value.

R-GOLD-2: a hash check alone proves the bytes did not move; it does not prove the file is
the artifact we think it is. So at least one VALUE is drawn from the workbooks too.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "measure"))
FIX = REPO / "fixtures" / "prescribed"
MANIFEST = FIX / "MANIFEST.json"

FME = "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


def test_golden__fixture_integrity__all_nine() -> None:
    man = json.loads(MANIFEST.read_text())
    assert man["count"] == 9, "the evidence base is nine prescribed workbooks"
    for row in man["files"]:
        p = FIX / row["filename"]
        assert p.exists(), f"missing fixture: {row['filename']}"
        raw = p.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["sha256"], f"sha256 drift: {row['filename']}"
        assert len(raw) == row["bytes"], f"size drift: {row['filename']}"


def test_golden__fixture_values_are_asserted_not_just_hashes() -> None:
    """R-GOLD-2. Draw a real value out of the FME workbook: the SUM identity at
    '3. Portfolio'!O3, which is one of the 35 row totals the harvest turns into a
    predicate."""
    with zipfile.ZipFile(FIX / FME) as z:
        names = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet")]
        found = None
        for n in names:
            xml = z.read(n).decode("utf-8", "replace")
            if 'r="O3"' in xml and "SUM(" in xml:
                i = xml.index('r="O3"')
                found = xml[i : i + 220]
                break
    assert found is not None, "the O3 SUM identity was not found in any sheet part"
    assert "SUM(C3:N3)" in found, f"expected SUM(C3:N3) at O3; got {found[:160]!r}"


def test_golden__probe_reproduces_the_published_numbers() -> None:
    """The ten numbers the specification publishes for the FME workbook, re-derived from
    raw OOXML by our own probe rather than quoted."""
    from foundation_probe import probe_one

    r = probe_one(FIX / FME)
    expected = {
        "N3_formula_cells": 505, "N3_formula_authored": 294, "N3_formula_shared_dependents": 211,
        "N4_data_validations": 54, "N4_dv_main_namespace": 35, "N4_dv_x14_extension": 19,
        "N4_dv_list_type": 22, "N5_merged_ranges": 252, "N6_defined_names": 12,
        "N7_field_surface": 3747,
    }
    got = {k: r[k] for k in expected}
    assert got == expected, f"probe diverged from the published numbers: {got} != {expected}"


def test_golden__openpyxl_under_reports_and_we_measure_the_gap() -> None:
    """The flagship finding, asserted rather than recounted: openpyxl sees 35 of 54
    validations and the AML-CFT sheet as 0 of 5."""
    from foundation_probe import probe_one, probe_openpyxl

    xml = probe_one(FIX / FME)
    lib = probe_openpyxl(FIX / FME)
    assert lib["openpyxl_data_validations"] == 35
    assert xml["N4_data_validations"] == 54
    assert lib["openpyxl_dv_per_sheet"].get("7. AML-CFT") == 0
    assert xml["N8_dv_per_sheet"].get("7. AML-CFT") == 5
