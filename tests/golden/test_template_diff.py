"""TEMPLATE_DIFF end to end — the flagship check, with its admission-side control."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _run() -> str:
    p = subprocess.run(
        [sys.executable, "tools/demo_template_diff.py"], cwd=REPO,
        capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
    )
    assert p.returncode == 0, p.stderr
    return p.stdout


def test_golden__template_diff_detects_an_overwritten_formula() -> None:
    out = _run()
    assert "FAIL  3. Portfolio!O7" in out
    assert "SUM(C7:N7)" in out, "the finding must show the template formula that was deleted"
    assert "999999" in out, "the finding must show the literal the filer wrote"
    assert "TEMPLATE_DIFF" in out


def test_golden__an_untouched_filing_produces_no_findings() -> None:
    """The admission-side control. Without it the check is a reject-everything baseline
    that would score perfectly on the negative control alone."""
    out = _run()
    section_b = out.split("ADMISSION-SIDE CONTROL")[1]
    assert "0 formula cell(s) overwritten" in section_b
    assert "FAIL" not in section_b


def test_golden__the_output_declares_what_it_did_not_check() -> None:
    out = _run()
    assert "NOT CHECKED, each with a declared reason" in out
    assert "495 of 505 derived cells checked" in out
    assert "It does not state that the filing is correct" in out


def test_golden__the_output_contains_no_banned_surface_token() -> None:
    sys.path.insert(0, str(REPO / "src"))
    from cdfc.surface.labels import banned_tokens

    out = _run().lower()
    for tok in banned_tokens():
        assert tok.lower() not in out, f"the flagship output contains {tok!r}"
