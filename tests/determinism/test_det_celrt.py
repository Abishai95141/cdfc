"""P4-B3 — the CEL layer binds no clock, and its results do not move with the timezone.

The subset bans `timestamp`, `duration` and `now`, so the clock is unreachable through the
grammar. That is the property under test; the TZ sweep is the check that it is actually true rather
than intended, because `pendulum` and `tzdata` are in `celpy`'s import closure and a construct that
slipped past the ban would read a real clock.

The wall-clock kill is the one deliberate exception, and it lives outside the deterministic core
(`cdfc.measure.perf.deadline`) with `CelResult.deterministic == False` attached to anything it
kills.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import CelRuntime, Outcome  # noqa: E402
from cdfc.facts.view import FactView  # noqa: E402
from cdfc.predicates.errors import SubsetViolation  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402

SNIPPET = (
    "import sys; sys.path.insert(0, %r)\n"
    "from cdfc.evaluate.celrt import CelRuntime\n"
    "from cdfc.facts.view import FactView\n"
    "from cdfc.predicates.host_fns import default_registry\n"
    "rt = CelRuntime(profile_version='P4', host_fns=default_registry())\n"
    "f = FactView({'d': '2026-03-31', 'n': 7, 'rows': [{'x': 1}, {'x': 2}]}, root='filing')\n"
    "t = FactView({'d': '2026-03-31'}, root='template')\n"
    "for src in ('filing.d == template.d', 'filing.n > 0', 'filing.rows.all(r, r.x > 0)'):\n"
    "    r = rt.evaluate(rt.compile(src, slot='expr'), filing=f, template=t)\n"
    "    print(r.outcome, r.value, r.steps)\n"
) % str(REPO / "src")


def _run(env_overrides: dict[str, str]) -> str:
    env = {**os.environ, **env_overrides}
    env.pop("PYTHONPATH", None)
    r = subprocess.run([sys.executable, "-c", SNIPPET], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


@pytest.mark.parametrize("tz", ["UTC", "Pacific/Kiritimati", "Asia/Kolkata"])
def test_det__celrt_results_do_not_move_with_the_timezone(tz: str) -> None:
    assert _run({"TZ": tz}) == _run({"TZ": "UTC"})


@pytest.mark.parametrize("seed", ["0", "1"])
def test_det__celrt_results_do_not_move_with_the_hash_seed(seed: str) -> None:
    assert _run({"PYTHONHASHSEED": seed}) == _run({"PYTHONHASHSEED": "0"})


def test_det__a_time_construct_does_not_compile() -> None:
    rt = CelRuntime(profile_version="P4", host_fns=default_registry())
    for src in (
        'filing.d > timestamp("2026-01-01T00:00:00Z")',
        'filing.d > duration("24h")',
        "filing.n > now",
    ):
        with pytest.raises(SubsetViolation):
            rt.compile(src, slot="expr")


def test_det__the_step_count_is_the_same_on_every_run() -> None:
    """The step budget is the deterministic one, so its counter must be too."""
    rt = CelRuntime(profile_version="P4", host_fns=default_registry())
    f = FactView({"rows": [{"x": i} for i in range(50)]}, root="filing")
    t = FactView({}, root="template")
    prog = rt.compile("filing.rows.all(r, r.x >= 0)", slot="expr")
    runs = [rt.evaluate(prog, filing=f, template=t) for _ in range(5)]
    assert len({r.steps for r in runs}) == 1
    assert {r.outcome for r in runs} == {Outcome.OK}


def test_det__the_snippet_produces_output_worth_comparing() -> None:
    """The admission side: identical empty output would satisfy every sweep above."""
    out = _run({})
    assert out.count("\n") == 3 and "OK" in out
