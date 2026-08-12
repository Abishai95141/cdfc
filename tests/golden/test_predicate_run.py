"""P4's value demonstration, as a test: a seeded carry desync is caught, and the control is clean.

The control matters more than the finding. A predicate set that fires on an untouched filing is
not detecting anything, and the seeded count would carry no information.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

import demo_predicate_run as demo  # noqa: E402

from cdfc.evaluate.celrt import CelRuntime  # noqa: E402
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402


def test_golden__a_seeded_carry_desync_is_caught_and_the_control_is_clean(capsys) -> None:
    rc = demo.main()
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "control findings 0" in out, "the untouched filing produced a finding"
    assert "seeded findings 1" in out, "the seeded carry desync was not detected exactly once"


def test_golden__the_demo_reports_what_did_not_run() -> None:
    """21 of 181 carries cannot run: one end is blank in the blank template.

    That is coverage this predicate set does NOT have, and it renders beside what it does.
    """
    res = harvest(demo.FME)
    carries = [c for c in res.candidates if "carried across sheets" in c.rationale]
    rt = CelRuntime(profile_version="P4", host_fns=default_registry())
    findings, passed = demo.run("probe", demo.fact_tree(demo.FME), carries, rt)
    assert findings == []
    assert 0 < len(passed) < len(carries), (
        "either nothing ran or everything did; both would mean the not-run count carries no "
        "information"
    )


def test_golden__the_demo_exits_nonzero_when_the_seed_is_not_detected() -> None:
    """The admission side of the demonstration itself: it reports a miss rather than a pass.

    Run as a subprocess with the carries filtered to none, so the seed cannot land anywhere a
    predicate is watching. The demo must exit non-zero and say so.
    """
    script = (
        "import sys; sys.path.insert(0, %r); sys.path.insert(0, %r)\n"
        "import demo_predicate_run as d\n"
        "_h = d.harvest\n"
        "d.harvest = lambda p: type('R', (), {'candidates': ()})()\n"
        "raise SystemExit(d.main())\n"
    ) % (str(REPO / "src"), str(REPO / "tools"))
    r = subprocess.run([sys.executable, "-c", script], cwd=REPO, capture_output=True, text=True)
    assert r.returncode != 0, "a demonstration with nothing to run must not report success"
    assert "cannot be placed" in r.stdout or "NOT detected" in r.stdout
