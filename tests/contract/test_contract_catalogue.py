"""Contract over the negative-control catalogue itself."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
CATALOGUE = REPO / "tests" / "negative" / "catalogue.yaml"

REQUIRED = {"id", "component", "break", "measured_instance", "injector", "guard_tests",
            "positive_control", "status"}


def entries() -> list[dict]:
    return yaml.safe_load(CATALOGUE.read_text())["entries"]


def test_contract__catalogue_schema() -> None:
    for e in entries():
        missing = REQUIRED - set(e)
        assert not missing, f"{e.get('id')}: missing {sorted(missing)}"
        for g in e["guard_tests"]:
            assert isinstance(g, dict), f"{e['id']}: a bare string guard — `flips` is required"
            assert "path" in g and "flips" in g, f"{e['id']}: guard needs path and flips"
            assert isinstance(g["flips"], bool), f"{e['id']}: flips must be a bool"
        if e["injector"] == "NONE":
            assert e.get("why_impossible"), f"{e['id']}: injector NONE requires why_impossible"


def test_contract__every_entry_expects_something_to_flip() -> None:
    """flips:false on every guard is a schema error: an entry that expects nothing to
    flip is not a negative control. PROVISIONAL entries are the declared exception and
    must say why."""
    for e in entries():
        if e["injector"] == "NONE" or e.get("provisional"):
            assert e.get("why_impossible") or e.get("why_provisional"), (
                f"{e['id']}: exempted from the flip requirement without a stated reason"
            )
            continue
        assert any(g["flips"] for g in e["guard_tests"]), (
            f"{e['id']}: no guard expects to flip; this entry proves nothing"
        )


def test_nc_meta__ids_are_unique() -> None:
    ids = [e["id"] for e in entries()]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate catalogue ids: {sorted(dupes)}"


def test_nc_meta__no_orphan_guard() -> None:
    """Every named guard resolves to a test that exists."""
    import subprocess

    nodes = sorted({g["path"] for e in entries() for g in e["guard_tests"]})
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *nodes, "--collect-only", "-q", "--no-header"],
        cwd=REPO, capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
    )
    assert proc.returncode == 0, f"a named guard does not resolve:\n{proc.stdout}\n{proc.stderr}"
