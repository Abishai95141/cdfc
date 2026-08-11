"""Unit tests for the CLI. A stub that exits 0 is an all-clear."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cdfc.cli import main, version_line  # noqa: E402
from cdfc.gates import parse  # noqa: E402
from cdfc.surface.labels import banned_tokens  # noqa: E402


def test_cli__unimplemented_subcommand_exits_nonzero(capsys) -> None:
    rc = main(["run"])
    assert rc == 2, "an unimplemented subcommand must exit 2; exiting 0 is an all-clear"
    err = capsys.readouterr().err.lower()
    for tok in banned_tokens():
        assert tok.lower() not in err, f"CLI output contains banned token {tok!r}"
    assert "not implemented" in err and "p5" in err, "the message must name the phase that builds it"


def test_cli__version_reports_gate_count(capsys) -> None:
    rc = main(["--version"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == version_line()
    assert f"gates {len(parse())}" in out, "a row added to the registry must be visible in --version"
