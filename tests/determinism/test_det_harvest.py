"""P4-B4 — the harvest is byte-identical across runs, seeds, locales and working directories.

Emission order and id assignment are a pure function of `(template_sha256, sheet index, cell ref)`.
A harvest keyed on set iteration order produces a different registry root every run, and the
registry root is what an attestation signs.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.canonical import code_sha256  # noqa: E402
from cdfc.predicates.harvest import emit_envelopes, harvest  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
ITFS = FIX / "ITFS_Monthly_report201220241626.xlsx"

SNIPPET = (
    "import sys; sys.path.insert(0, %r)\n"
    "from pathlib import Path\n"
    "from cdfc.predicates.harvest import harvest\n"
    "from cdfc.predicates.canonical import code_sha256\n"
    "r = harvest(Path(%r))\n"
    "for c in r.candidates:\n"
    "    print(c.id, code_sha256(c))\n"
    "print('skips', sorted((s.kind, s.sheet, s.ref) for s in r.skipped))\n"
) % (str(REPO / "src"), str(ITFS))


def _run(env_overrides: dict[str, str], cwd: Path) -> str:
    env = {**os.environ, **env_overrides}
    env.pop("PYTHONPATH", None)
    r = subprocess.run([sys.executable, "-c", SNIPPET], env=env, cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_det__harvest_is_ordered() -> None:
    a, b = harvest(ITFS), harvest(ITFS)
    assert [c.id for c in a.candidates] == [c.id for c in b.candidates]
    assert [code_sha256(c) for c in a.candidates] == [code_sha256(c) for c in b.candidates]
    ids = [c.id for c in a.candidates]
    assert ids == sorted(ids), "ids are assigned in the canonical emission order"


def test_det__emitted_envelopes_are_byte_identical(tmp_path: Path) -> None:
    one = {p.name: p.read_bytes() for p in emit_envelopes(harvest(ITFS), tmp_path / "a")}
    two = {p.name: p.read_bytes() for p in emit_envelopes(harvest(ITFS), tmp_path / "b")}
    assert one == two and one


def test_det__emit_removes_a_stale_envelope(tmp_path: Path) -> None:
    """A shrinking harvest must not leave last run's predicates behind pretending to be current."""
    out = tmp_path / "out"
    res = harvest(ITFS)
    emit_envelopes(res, out)
    stale = out / res.template_sha256[:8] / "P-9999__harvested.yaml"
    stale.write_text("id: P-9999\n", encoding="utf-8")
    emit_envelopes(res, out)
    assert not stale.exists()


@pytest.mark.parametrize("seed", ["0", "1"])
def test_det__harvest_is_stable_under_the_hash_seed(seed: str) -> None:
    assert _run({"PYTHONHASHSEED": seed}, REPO) == _run({"PYTHONHASHSEED": "0"}, REPO)


@pytest.mark.parametrize("locale", ["C", "en_IN.UTF-8"])
def test_det__harvest_is_stable_under_the_locale(locale: str) -> None:
    assert _run({"LC_ALL": locale}, REPO) == _run({"LC_ALL": "C"}, REPO)


def test_det__harvest_is_stable_across_working_directories(tmp_path: Path) -> None:
    assert _run({}, REPO) == _run({}, tmp_path)


def test_det__the_snippet_produces_output_worth_comparing() -> None:
    """The admission side: identical empty output would satisfy every sweep above."""
    out = _run({}, REPO)
    assert out.count("\n") > 10 and "P-0001" in out
