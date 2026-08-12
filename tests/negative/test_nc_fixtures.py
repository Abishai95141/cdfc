"""NC-F01 — a vendored fixture drifts."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from injectors import FlipFixtureByte, inject  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def _corpus_verify() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/measure/corpus_verify.py"], cwd=REPO, capture_output=True, text=True
    )


def test_nc__F01_fixture_drift_is_caught() -> None:
    assert _corpus_verify().returncode == 0, "precondition: the vendored corpus verifies"
    with inject(FlipFixtureByte()):
        proc = _corpus_verify()
    assert proc.returncode != 0, "a one-byte drift in the evidence base was not detected"
    out = proc.stdout + proc.stderr
    assert "ITFS_Monthly_report" in out, (
        "the drift detector did not NAME the file; a detector that does not name the "
        "file is a detector nobody uses"
    )
