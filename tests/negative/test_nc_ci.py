"""NC-CI negative controls for P0.

Each test injects a specific, named break and asserts the guard REJECTS it. A guard that
has never been observed red is a preference, not a gate.

Every rejection test has an admission-side twin where one is meaningful, because a gate
that rejects everything scores perfectly on the negative control alone.
"""

from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from injectors import (  # noqa: E402
    BareExcept,
    EmptyScanRoot,
    GreenTick,
    RemoveScanRoot,
    StubExitsZero,
    inject,
    run_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FME = Path(
    "/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/"
    "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)


# --------------------------------------------------------------------------- NC-CI01
def test_nc__CI01_missing_scan_root_fails() -> None:
    """A grep gate whose scan root does not exist must NOT report success.

    This is NC-D01's mechanism applied to CI: `grep -r pattern missing/` exits 0.
    """
    assert run_gate("ci/no-bare-except.sh") == 0, "precondition: the gate is green on a correct tree"
    with inject(RemoveScanRoot()):
        rc = run_gate("ci/no-bare-except.sh")
    assert rc != 0, "a gate over a MISSING scan root reported success"
    assert run_gate("ci/no-bare-except.sh") == 0, "the tree was not restored"


def test_nc__CI01b_present_empty_scan_root_passes() -> None:
    """Admission-side twin: an EXISTING but empty root passes.

    The rule is 'the root must exist', not 'the root must be non-empty'. Without this
    twin the gate could be satisfied by rejecting everything.
    """
    with inject(EmptyScanRoot()):
        rc = run_gate("ci/no-bare-except.sh")
    assert rc == 0, "an existing but empty scan root was rejected; the rule is over-strict"


# --------------------------------------------------------------------------- NC-CI02
def test_nc__CI02_openpyxl_warning_is_an_error() -> None:
    """openpyxl's data-validation warning must RAISE, not be discarded.

    This one line of configuration stands between the project and the exact signal that
    produced its flagship finding: a parser that reads the FME workbook and reports the
    AML-CFT sheet as having zero data validations when it has five.
    """
    pytest.importorskip("openpyxl")
    assert FME.exists(), f"the evidence base is missing: {FME}"
    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(UserWarning, match="[Dd]ata ?[Vv]alidation"):
            openpyxl.load_workbook(FME)


def test_nc__CI02b_the_warning_is_real_not_a_test_artifact() -> None:
    """Positive control for CI02: the warning genuinely comes from the artifact.

    Without this, CI02 would pass on a workbook that emits no warning at all and the
    test would be asserting a property of `simplefilter`, not of the parser.
    """
    pytest.importorskip("openpyxl")
    import openpyxl

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        openpyxl.load_workbook(FME)
    msgs = [str(w.message) for w in caught]
    assert any("Data Validation" in m for m in msgs), (
        f"expected openpyxl to warn about data validations on the FME workbook; got {msgs!r}"
    )


# --------------------------------------------------------------------------- NC-CI03
def test_nc__CI03_green_tick_gate_rejects_an_all_clear() -> None:
    assert run_gate("ci/no-green-tick.sh") == 0, "precondition: green on a correct tree"
    with inject(GreenTick()):
        rc = run_gate("ci/no-green-tick.sh")
    assert rc != 0, "an all-clear reached a user surface and the gate reported success"


# --------------------------------------------------------------------------- NC-CI04
def test_nc__CI04_bare_except_is_rejected() -> None:
    with inject(BareExcept()):
        rc = run_gate("ci/no-bare-except.sh")
    assert rc != 0, "a bare except survived the gate"


# --------------------------------------------------------------------------- NC-CI05
def test_nc__CI05_a_stub_that_exits_zero_is_rejected() -> None:
    """A stub that exits 0 is an all-clear. The unit test must catch it."""
    with inject(StubExitsZero()):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit/test_cli.py", "-q", "--no-header"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    assert proc.returncode != 0, (
        "cli.py was made to exit 0 for an unimplemented subcommand and the unit test "
        "still passed — the test does not test what it claims"
    )
