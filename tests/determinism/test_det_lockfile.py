"""Every dependency is pinned by name AND wheel hash.

THE FIRST VERSION OF THIS TEST WAS VACUOUS AND IS RECORDED HERE RATHER THAN QUIETLY
REPLACED. It split the lockfile on blank lines and asserted each "block" contained a
`--hash=`. `uv pip compile` emits **no blank lines at all**, so the whole file was one
block: the assertion held as long as *any* line anywhere carried a hash, and a dependency
with none would have passed. The negative control caught it — `UnpinDependency` removed a
hash and the test stayed green, which is the sweep earning its keep on its first run.

The parser below is structural: a package block starts at a line beginning in column 0
that contains `==`, and continues through its indented continuation lines.
"""

from __future__ import annotations

from pathlib import Path

import pytest

LOCK = Path(__file__).resolve().parents[2] / "requirements.lock"


def parse_blocks(text: str) -> dict[str, list[str]]:
    """{'attrs==26.1.0': [continuation lines]} — one entry per pinned package."""
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[:1].isspace() and "==" in line:
            current = line.split("\\")[0].strip()
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line.strip())
    return blocks


def test_det__lockfile_exists() -> None:
    assert LOCK.exists(), "requirements.lock is missing; the toolchain is not pinned"


def test_det__lockfile_is_hash_pinned() -> None:
    if not LOCK.exists():
        pytest.skip("covered by test_det__lockfile_exists")
    blocks = parse_blocks(LOCK.read_text())
    assert blocks, "no package blocks parsed; the test would be vacuous"
    unpinned = [
        name for name, cont in blocks.items() if not any(c.startswith("--hash=sha256:") for c in cont)
    ]
    assert not unpinned, f"dependencies pinned by version but not by wheel hash: {unpinned}"


def test_det__the_parser_sees_one_block_per_package() -> None:
    """Guard against the vacuity that made version 1 useless.

    If the parser collapses the file into one block, a single hash anywhere satisfies
    everything. Assert it finds as many blocks as there are top-level `name==` lines.
    """
    text = LOCK.read_text()
    expected = sum(
        1
        for ln in text.splitlines()
        if ln and not ln[:1].isspace() and "==" in ln and not ln.startswith("#")
    )
    assert len(parse_blocks(text)) == expected > 1, (
        "the lockfile parser did not resolve one block per package"
    )


def test_det__the_hash_check_can_fail() -> None:
    """Negative control on the parser itself, inline: a package with no hash is caught."""
    synthetic = "good==1.0 \\\n    --hash=sha256:aaaa\nbad==2.0 \\\n    # via nothing\n"
    blocks = parse_blocks(synthetic)
    unpinned = [n for n, c in blocks.items() if not any(x.startswith("--hash=sha256:") for x in c)]
    assert unpinned == ["bad==2.0"], f"the check failed to catch an unpinned package: {unpinned}"
