"""Every dependency is pinned by name AND wheel hash."""
from __future__ import annotations

from pathlib import Path

import pytest

LOCK = Path(__file__).resolve().parents[2] / "requirements.lock"


def test_det__lockfile_exists() -> None:
    assert LOCK.exists(), "requirements.lock is missing; the toolchain is not pinned"


def test_det__lockfile_is_hash_pinned() -> None:
    if not LOCK.exists():
        pytest.skip("covered by test_det__lockfile_exists")
    unpinned = []
    for block in LOCK.read_text().split("\n\n"):
        if not block.strip() or block.lstrip().startswith("#"):
            continue
        first = block.strip().splitlines()[0]
        if first.startswith("-") or "==" not in first:
            continue
        if "--hash=sha256:" not in block:
            unpinned.append(first.strip())
    assert not unpinned, f"dependencies without a wheel hash: {unpinned}"
