"""P4-B1 — the envelope digest is stable across hash seed, locale and working directory.

A digest that moves with `PYTHONHASHSEED` is a registry root that moves with the hash seed: the
same predicate would be admitted twice, and the two admissions would carry different
qualification records.

Run in a subprocess because the seed and the locale are process-wide.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

SNIPPET = (
    "import sys; sys.path.insert(0, %r)\n"
    "from cdfc.predicates.loader import load_candidate, load_predicate\n"
    "from cdfc.predicates.canonical import code_sha256\n"
    "g = %r\n"
    "print(code_sha256(load_candidate(g + '/P-0041__scheme-type-membership.yaml')))\n"
    "print(code_sha256(load_predicate(g + '/P-0007__intro-D17-integer-bound.yaml')))\n"
) % (str(REPO / "src"), str(REPO / "fixtures" / "predicates" / "good"))


def _run(env_overrides: dict[str, str], cwd: Path) -> str:
    env = {**os.environ, **env_overrides}
    env.pop("PYTHONPATH", None)
    r = subprocess.run(
        [sys.executable, "-c", SNIPPET], env=env, cwd=cwd, capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr
    return r.stdout


@pytest.mark.parametrize("seed", ["0", "1"])
def test_det__envelope_digest_stable_under_hash_seed(seed: str) -> None:
    assert _run({"PYTHONHASHSEED": seed}, REPO) == _run({"PYTHONHASHSEED": "0"}, REPO)


@pytest.mark.parametrize("locale", ["C", "en_IN.UTF-8"])
def test_det__envelope_digest_stable_under_locale(locale: str) -> None:
    assert _run({"LC_ALL": locale}, REPO) == _run({"LC_ALL": "C"}, REPO)


def test_det__envelope_digest_stable_across_working_directories(tmp_path: Path) -> None:
    assert _run({}, REPO) == _run({}, tmp_path)


def test_det__the_two_digests_differ_from_each_other() -> None:
    """The admission-side control: identical output would satisfy every test above."""
    lines = _run({}, REPO).split()
    assert len(lines) == 2 and lines[0] != lines[1], (
        "both fixtures digest identically, so a stability test comparing them proves nothing"
    )
