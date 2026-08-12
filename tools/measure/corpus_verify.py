#!/usr/bin/env python
"""Re-hash the vendored corpus against its manifest.

Exits non-zero on ANY drift and NAMES the file. A drift detector that reports
"verification failed" without saying which of nine files moved is a detector nobody
uses, so the filename is part of the contract and `test_nc__F01_fixture_drift_is_caught`
asserts it appears in the output.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "fixtures" / "prescribed"
MANIFEST = FIXTURES / "MANIFEST.json"


def main() -> int:
    if not MANIFEST.exists():
        print(f"corpus-verify: no manifest at {MANIFEST}", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text())
    declared = {r["filename"]: r for r in manifest["files"]}

    on_disk = {p.name for p in FIXTURES.glob("*.xlsx")}
    problems: list[str] = []

    for missing in sorted(set(declared) - on_disk):
        problems.append(f"MISSING: {missing} is in the manifest and not on disk")
    for extra in sorted(on_disk - set(declared)):
        problems.append(f"UNDECLARED: {extra} is on disk and not in the manifest")

    for name in sorted(set(declared) & on_disk):
        raw = (FIXTURES / name).read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        want = declared[name]["sha256"]
        if got != want:
            problems.append(f"DRIFT: {name}\n    expected sha256 {want}\n    found    sha256 {got}")
        elif len(raw) != declared[name]["bytes"]:
            problems.append(
                f"DRIFT: {name} size {len(raw)} != declared {declared[name]['bytes']}"
            )

    if problems:
        print("corpus-verify: FAIL", *problems, sep="\n  ", file=sys.stderr)
        # also to stdout, so a caller capturing either stream sees the filename
        print("corpus-verify: FAIL", *problems, sep="\n  ")
        return 1

    print(f"corpus-verify: OK ({len(declared)} files, all sha256 match)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
