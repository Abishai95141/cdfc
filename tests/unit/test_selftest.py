"""P10-B1 — `P-SELFTEST-DEAD`, the canary for the canary loop, and where the recursion stops."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.selfcheck import selftest as st  # noqa: E402
from cdfc.selfcheck.selftest import (  # noqa: E402
    EXPECTED_SILENT,
    P_SELFTEST_DEAD,
    SELFTEST_ID,
    SelfTestPredicate,
)


def test_st__expected_set_is_a_constant() -> None:
    """§P10·L.4, and it is one line and no more.

    Derived from the loaded registry, a loader that silently drops the self-test makes the
    expected set empty, the observed set is empty, they agree, and the run goes green — the
    recursion closing on itself in the direction that flatters us. The set is a module-level
    literal, so nothing that happens at load time can move it.
    """
    import ast

    src = Path(st.__file__).read_text(encoding="utf-8")
    node = next(
        n for n in ast.walk(ast.parse(src))
        if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "EXPECTED_SILENT"
    )
    assert isinstance(node.value, ast.Call), "EXPECTED_SILENT is not a constructor call"
    assert getattr(node.value.func, "id", "") == "frozenset"
    for arg in ast.walk(node.value):
        assert not isinstance(arg, ast.Attribute), (
            "EXPECTED_SILENT reaches through an attribute. Any expression that consults the "
            "loaded registry re-opens the hole this constant exists to close: the loader drops "
            "the self-test, the expected set becomes empty, the observed set is empty, they "
            "agree, and the run goes green."
        )
    assert EXPECTED_SILENT == frozenset({SELFTEST_ID})


def test_st__it_cannot_be_made_to_fail() -> None:
    """Its entire evidential value is that no fault can make it FAIL."""
    assert P_SELFTEST_DEAD.expr == "true"
    with pytest.raises(ValueError) as e:
        SelfTestPredicate(expr="filing.a.b.v > 0")
    assert "ambiguous" in str(e.value)


def test_st__an_id_outside_the_expected_set_is_refused() -> None:
    with pytest.raises(ValueError):
        SelfTestPredicate(id="P-SELFTEST-9999")


def test_st__selftest_settles_no_cell() -> None:
    """Absent from `run_cell`, from the settled fraction, and from every filer-facing surface.

    **Absence, checked — not exclusion, declared.** `plan/05` makes it a registry row with
    `kind='selftest'` filtered out downstream; this build never puts it in the predicate list at
    all, so the property is structural. This asserts the structure actually holds by running a
    real filing end to end and searching every artifact the run produces.
    """
    from cdfc.evaluate.run import run_jsonl
    from cdfc.measure.p5_run import TEMPLATE_COMPUTED, run_filing

    result = run_filing(TEMPLATE_COMPUTED)
    assert SELFTEST_ID not in {c.predicate_id for c in result.checks}
    assert SELFTEST_ID not in {c.settled_by for c in result.cells if c.settled_by}
    assert SELFTEST_ID not in run_jsonl(result)
    assert SELFTEST_ID not in str(result.as_manifest())


def test_st__it_declares_no_footprint() -> None:
    """A declared key is a footprint, and a footprint is what puts a check on a filer surface."""
    assert not hasattr(P_SELFTEST_DEAD, "schema_keys")
    assert not hasattr(P_SELFTEST_DEAD, "claims_fault_classes"), (
        "the self-test claims no fault class: it catches nothing, and that is the point"
    )


def test_st__the_selftest_runs_on_the_same_runtime_as_every_other_check() -> None:
    """Death D4 is only catchable if a stubbed evaluator can make this one fire.

    Asserted on object identity: the runtime the loop hands the self-test is the same object it
    hands every predicate, so a short-circuited or stubbed runtime reports the self-test as having
    fired and the disposition withholds the verdict.
    """
    from cdfc.evaluate.liveness import selftest_fired
    from tests.selfcheck_fixtures import image, runtime

    rt = runtime()
    assert selftest_fired(P_SELFTEST_DEAD, image().facts, rt=rt) is False
    from tests.selfcheck_fixtures import liveness_inputs

    assert liveness_inputs().rt is rt


def test_st__a_broken_runtime_makes_the_selftest_fire() -> None:
    """The other half: anything but `True` is a fire, including an error and a budget kill."""
    from cdfc.evaluate.liveness import selftest_fired
    from tests.selfcheck_fixtures import image

    class _DeadRuntime:
        def compile(self, src, slot):  # noqa: ANN001, ARG002
            raise RuntimeError("the runtime is not running")

    assert selftest_fired(P_SELFTEST_DEAD, image().facts, rt=_DeadRuntime()) is True


def test_st__C09a_selftest_runs_with_no_environment_set() -> None:
    """NC-C09. `plan/01` §2.5 NC-C01b seeds it under `CDFC_CANARY_SELFTEST=1`; the flag is removed.

    A self-test that runs only when a flag is set is a self-test that is off in production, which
    is the failure this layer exists to catch, one level up. Run in a subprocess with the
    environment stripped, because a flag read at import time would be invisible in-process.
    """
    code = (
        "import sys; sys.path.insert(0, 'src');"
        "from cdfc.selfcheck.selftest import P_SELFTEST_DEAD, EXPECTED_SILENT;"
        "print(P_SELFTEST_DEAD.id, sorted(EXPECTED_SILENT))"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
    )
    assert proc.returncode == 0, proc.stderr
    assert SELFTEST_ID in proc.stdout

    # Over the CODE, not the text: this module's own docstring says "environment" four times, and
    # a substring scan that its own prose defeats is a gate that checks the comments.
    import ast

    names = {
        n.attr for n in ast.walk(ast.parse(Path(st.__file__).read_text(encoding="utf-8")))
        if isinstance(n, ast.Attribute)
    } | {
        getattr(n.func, "id", "") for n in ast.walk(
            ast.parse(Path(st.__file__).read_text(encoding="utf-8"))
        ) if isinstance(n, ast.Call)
    }
    assert not (names & {"environ", "getenv", "get_environ"}), (
        "the self-test module reads the environment. A flag is a way to be off in production, "
        f"which is the failure this layer exists to catch one level up. Found: {sorted(names)}"
    )
