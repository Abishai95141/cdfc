"""The receipt is clock-free and timezone-free (R3).

`received_at` is an ARGUMENT. A core module that reads a clock cannot be re-derived, and
a receipt that changes with the machine's timezone makes every downstream digest
machine-dependent.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

FME = REPO / "fixtures" / "prescribed" / (
    "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)

SNIPPET = """
import sys, json, tempfile, pathlib
sys.path.insert(0, "src")
from cdfc.ingest.receipt import receive
from cdfc.canon import canonical_json
d = pathlib.Path(sys.argv[1]).read_bytes()
with tempfile.TemporaryDirectory() as tmp:
    r = receive(d, media_type="x", cap_bytes=10_000_000,
                blob_root=pathlib.Path(tmp), received_at="2026-08-11T09:00:00Z")
    sys.stdout.write(canonical_json(r.as_canonical_obj()).decode())
"""


def _receipt_under(tz: str) -> str:
    env = dict(os.environ, TZ=tz, PYTHONPATH=str(REPO / "src"))
    proc = subprocess.run(
        [sys.executable, "-c", SNIPPET, str(FME)],
        cwd=REPO, capture_output=True, text=True, env=env,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def test_det__receipt_is_clock_free() -> None:
    """Two timezones fourteen hours apart produce an identical receipt."""
    a = _receipt_under("Pacific/Kiritimati")  # UTC+14
    b = _receipt_under("UTC")
    assert a == b, "the receipt changed with the machine's timezone"


def test_det__receipt_is_stable_across_processes() -> None:
    assert _receipt_under("UTC") == _receipt_under("UTC")


def test_det__no_clock_call_in_the_ingest_package() -> None:
    """The static form. `ci/no-clock-in-core.sh` covers this too; the test states the
    property where an engineer reading the package will see it."""
    import ast

    offenders = []
    for path in (REPO / "src" / "cdfc" / "ingest").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                if name in {"time", "perf_counter", "monotonic", "now", "utcnow", "today"}:
                    offenders.append(f"{path.name}: {name}()")
    assert not offenders, f"a clock is read inside the ingest package: {offenders}"
