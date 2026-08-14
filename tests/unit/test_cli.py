"""Unit tests for the CLI. A stub that exits 0 is an all-clear."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cdfc.cli import main, version_line  # noqa: E402
from cdfc.gates import parse  # noqa: E402
from cdfc.surface.labels import banned_tokens  # noqa: E402


def test_cli__unimplemented_subcommand_exits_nonzero(capsys) -> None:
    """**THIS TEST USED TO PIN `run` AS ABSENT.** It asserted `main(["run"]) == 2` and that the
    message named P5 — so it enforced that a P5 deliverable stay unbuilt, and would have gone red
    the day somebody built it. `run` shipped four phases late partly because the suite defended
    its absence.

    The rule it was written for is real and is kept, over a command that genuinely is not built:
    a stub that exits 0 is an all-clear, and this product's thesis is that a silent success
    carries no information.
    """
    rc = main(["qualify"])
    assert rc == 2, "an unimplemented subcommand must exit 2; exiting 0 is an all-clear"
    err = capsys.readouterr().err.lower()
    for tok in banned_tokens():
        assert tok.lower() not in err, f"CLI output contains banned token {tok!r}"
    assert "not implemented" in err and "p7" in err, "the message must name the phase that builds it"


def test_cli__run_is_built_and_declares_coverage(tmp_path, capsys) -> None:
    """`cdfc run` — P5's deliverable, reachable at last. The output is a COVERAGE DECLARATION:
    what was checked and what was not, and the fraction never renders without its denominator."""
    repo = Path(__file__).resolve().parents[2]
    filing = repo / "fixtures" / "synthetic" / "formula-overwritten__portfolio-O7.xlsx"
    rc = main(["run", str(filing), "--out", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out

    assert "cellsTotal" in out and "inScope" in out, (
        "the settled fraction must never render without both denominator terms"
    )
    assert "settled fraction" in out
    assert "It does not state that the" in out, "the declaration must refuse an all-clear reading"
    for tok in banned_tokens():
        assert tok.lower() not in out.lower()

    runs = list(tmp_path.iterdir())
    assert len(runs) == 1
    for artifact in ("run.jsonl", "run.db", "manifest.json"):
        assert (runs[0] / artifact).is_file(), f"{artifact} was not written"


def test_cli__closure_explain_renders_the_seven_terms(tmp_path, capsys) -> None:
    """`verdict/closure.py::explain()` had zero callers and zero tests, and a measurement tool
    re-implemented the same rendering by hand."""
    repo = Path(__file__).resolve().parents[2]
    filing = repo / "fixtures" / "synthetic" / "formula-overwritten__portfolio-O7.xlsx"
    assert main(["run", str(filing), "--out", str(tmp_path)]) == 0
    capsys.readouterr()

    assert main(["closure", "explain", "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    for term in ("outOfScope", "informational", "settled", "indeterminate",
                 "notRun", "noPredicate", "error"):
        assert term in out, f"the seven-term closure is missing {term}"
    assert "cellsTotal" in out and "inScope" in out


def test_cli__version_reports_gate_count(capsys) -> None:
    rc = main(["--version"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == version_line()
    assert f"gates {len(parse())}" in out, "a row added to the registry must be visible in --version"
