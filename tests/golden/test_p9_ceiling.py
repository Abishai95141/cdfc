"""P9-B1 goldens — the published ceiling, the function census, and the eight blind cells.

**Every assertion here is PAIRED (R-GOLD-2): a count and a body.** A golden that pins only
`957` is green on a map that reaches 957 different cells; one that pins only
`'3. Portfolio'!O4 == "SUM(C4:N4)"` is green on a map that resolves one formula and drops the
rest. The pair is what makes either mean anything.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.precedents import build_precedent_map, ceiling, materialised_formulas  # noqa: E402
from cdfc.probes.template_diff import load_defects  # noqa: E402
from cdfc.schema.fingerprint import structural_fingerprint  # noqa: E402
from cdfc.schema.styles_mask import Rule, build as build_mask  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
SYN = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
CEILING_JSON = REPO / "docs" / "measurements" / "p9-template-diff-ceiling.json"
CENSUS_JSON = REPO / "docs" / "measurements" / "p3-cached-value-reproduction.json"


@pytest.fixture(scope="module")
def pm():
    return build_precedent_map(FME)


def test_golden__ceiling_is_957_of_3747(pm) -> None:
    """The published ceiling, with its per-sheet split AND the shared-dependent control."""
    assert ceiling(pm) == (957, 3747)
    assert pm.per_sheet() == {
        "1. Introduction": 64, "2. Summary": 20, "3. Portfolio": 400,
        "4. Investors": 368, "5. PMS": 104, "8. Compliance Status": 1,
    }
    text, _deferred = materialised_formulas(FME)
    assert text["3. Portfolio!O4"] == "SUM(C4:N4)"


def test_golden__the_published_file_carries_the_measured_numbers() -> None:
    """A measurement file is only a measurement while its generator still produces it."""
    d = json.loads(CEILING_JSON.read_text(encoding="utf-8"))
    assert d["warrant"] == "MEASURED"
    assert (d["ceiling_all_formula_cells"], d["field_surface"]) == (957, 3747)
    assert d["ceiling_binding_formula_cells"] == 869
    assert d["reachable_only_via_unbinding_cells"] == 88
    assert d["readings"] == {"lexical": 957, "value": 957, "transitive": 957}
    assert d["unreachable_by_reading"] == {"lexical": 115, "value": 115, "transitive": 0}


def test_golden__eight_unlocked_formula_cells() -> None:
    """The eight overwritable-in-Excel cells, BY NAME. A change here is a parser regression or a
    new template version, and both must be loud."""
    d = json.loads(CEILING_JSON.read_text(encoding="utf-8"))
    assert d["unlocked_formula_cells"] == [
        "4. Investors!N14", "4. Investors!N15", "4. Investors!N16", "4. Investors!N17",
        "4. Investors!N5", "4. Investors!N6", "4. Investors!N7", "4. Investors!N8",
    ]


def test_golden__an_unlocked_overwrite_unbinds_and_a_locked_one_does_not() -> None:
    """**The measured correction to the plan.** The eight cells a filer can overwrite without
    stripping protection are the eight `TEMPLATE_DIFF` can never see: the overwrite moves the
    cell into the field surface, the mask moves, the fingerprint moves, and the run ends at F3
    with `invalid.template_unbound` — five steps before the relation executes."""
    base_fp = structural_fingerprint(FME)
    base_n = build_mask(FME, Rule.V3).n_cells
    assert base_n == 3747

    locked = SYN / "formula-overwritten__portfolio-O7.xlsx"
    assert structural_fingerprint(locked) == base_fp
    assert build_mask(locked, Rule.V3).n_cells == 3747

    unlocked = SYN / "formula-overwritten__investors-N5.xlsx"
    assert structural_fingerprint(unlocked) != base_fp
    assert build_mask(unlocked, Rule.V3).n_cells == 3748


def test_golden__nine_functions_not_eight() -> None:
    """§0.6. The absence claim *"the vocabulary is eight"* is now a script with a positive
    control, and the ninth function sits inside G-EVAL's own positive control range."""
    d = json.loads(CENSUS_JSON.read_text(encoding="utf-8"))
    assert d["functions"] == {
        "SUM": 135, "IFERROR": 130, "INDEX": 30, "ROW": 30, "ROWS": 30,
        "_xlfn.AGGREGATE": 30, "IF": 14, "COUNTIF": 3, "_xlfn.SINGLE": 1,
    }
    assert d["outside_vocabulary"] == []
    assert all(d["implemented"].values())


def test_golden__zero_formula_template_yields_no_relation() -> None:
    """`EDR_1` and `IFSCA_Annual_Reporting_Format` carry **zero** formula cells. The relation
    must produce an empty set and say so — not crash, not silently succeed, and not report a
    ceiling of `0/0` as though it were a coverage figure."""
    for name in (
        "EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx",
        "IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx",
    ):
        p = FIX / name
        assert p.is_file(), f"{name} is not in the corpus; this test would pass over an absence"
        m = build_precedent_map(p)
        assert m.formula_text == {}
        assert m.by_formula_cell == {}
        assert m.unreachable == frozenset()
        n, d = ceiling(m)
        assert n == 0
        assert (n, d) != (0, 0) or d == 0, "a 0/0 ceiling must be reported as a shape, not a rate"


def test_golden__alr_has_the_worst_shared_share() -> None:
    """`ALR_V2_3` is where a precedent map built from formula TEXT fails first and hardest."""
    from cdfc.ingest.reader_lxml import read

    alr = FIX / "ALR_V2_3_20250808_1024.xlsx"
    records = read(alr).formulas
    shared = [f for f in records if f.encoding == "SHARED_DEPENDENT"]
    assert (len(records), len(shared)) == (645, 399)
    m = build_precedent_map(alr)
    assert ceiling(m) == (914, 1599)
    assert m.deferred == {}


def test_probes__every_declared_defect_has_a_reproducing_command() -> None:
    """**A defect table without re-runnable evidence is a list of opinions.** The command runs,
    and it exits non-zero when its claim stops reproducing."""
    defects = load_defects()
    assert defects.by_cell, "an empty defect table makes this test vacuous"
    for cell, d in sorted(defects.by_cell.items()):
        cmd = d.evidence_command.replace(".venv/bin/python", sys.executable).split()
        p = subprocess.run(
            cmd, cwd=REPO, capture_output=True, text=True,
            env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
        )
        assert p.returncode == 0, f"{cell}: {d.evidence_command} failed: {p.stderr[-600:]}"
        payload = json.loads(p.stdout)
        assert payload["claim_reproduces"] is True, f"{cell}: the declared defect no longer holds"


def test_golden__the_D17_defect_is_seven_of_nine() -> None:
    """The claim itself, pinned: nine scheme types, five patterns, seven matched, two not."""
    p = subprocess.run(
        [sys.executable, "tools/probes/p9_scheme_vocabulary.py"], cwd=REPO,
        capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
    )
    assert p.returncode == 0, p.stderr
    d = json.loads(p.stdout)
    assert d["vocabulary_size"] == 9
    assert d["matched"] == 7
    assert d["unmatched"] == ["Special Situation Fund", "Family Investment Fund"]
    assert d["total_formula"] == "SUM(D18:D20)"
    assert d["vocabulary_range"] == "Dropdown!F3:F11"
