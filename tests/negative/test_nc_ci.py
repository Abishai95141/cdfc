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
from contextlib import closing
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
# The VENDORED corpus, not the external one it was originally copied from. A reader or a
# control validated against a fixture that can drift validates nothing, and an external
# absolute path also makes the repository non-portable: a fresh clone fails.
# Mechanised by ci/no-external-paths.sh (registry row 19).
FME = REPO_ROOT / "fixtures" / "prescribed" / (
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
            openpyxl.load_workbook(FME)  # raises before it can return a handle


def test_nc__CI02b_the_warning_is_real_not_a_test_artifact() -> None:
    """Positive control for CI02: the warning genuinely comes from the artifact.

    Without this, CI02 would pass on a workbook that emits no warning at all and the
    test would be asserting a property of `simplefilter`, not of the parser.
    """
    pytest.importorskip("openpyxl")
    import openpyxl

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with closing(openpyxl.load_workbook(FME)):
            pass
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


# --------------------------------------------------------------------------------- NC-CI11
def test_nc__CI11_monotonic_clock_is_rejected() -> None:
    """A duration we measured ourselves must not enter the deterministic core."""
    from injectors import ClockInCore

    assert run_gate("ci/no-clock-in-core.sh") == 0, "precondition: green on a correct tree"
    with inject(ClockInCore()):
        rc = run_gate("ci/no-clock-in-core.sh")
    assert rc != 0, "a perf_counter() reached the deterministic core and the gate passed"


def test_nc__CI11b_clock_in_measure_perf_is_allowed() -> None:
    """Admission-side twin: timings ARE allowed in src/cdfc/measure/perf/.

    Without this the gate could be satisfied by banning the clock everywhere, which
    would delete the evidence that a loop ran rather than keep it out of the hash.
    """
    p = Path("src/cdfc/measure/perf/__init__.py")
    original = p.read_bytes()
    try:
        p.write_bytes(original + b"\nimport time\n\n\ndef t() -> float:\n    return time.perf_counter()\n")
        assert run_gate("ci/no-clock-in-core.sh") == 0, (
            "a timing inside measure/perf was rejected; that is where timings live"
        )
    finally:
        p.write_bytes(original)


# --------------------------------------------------------------------------------- NC-CI12
def test_nc__CI12_version_must_read_the_registry() -> None:
    """Gate 10. A hard-coded gate count drifts the moment a row is added."""
    from injectors import AddGateRow, HardcodeGateCount

    with inject(HardcodeGateCount()), inject(AddGateRow()):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/unit/test_cli.py::test_cli__version_reports_gate_count",
             "-q", "--no-header"],
            cwd=REPO_ROOT, capture_output=True, text=True,
            env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
        )
    assert proc.returncode != 0, "the CLI reported a hard-coded gate count and the test passed"


# --------------------------------------------------------------------------------- NC-CI13
def test_nc__CI13_denylisted_runtime_licence_is_rejected() -> None:
    """Gate 11. A denylisted licence in the resolved runtime set fails the build."""
    from injectors import DenylistedRuntimeDep

    assert run_gate("ci/licence-denylist.sh") == 0, "precondition: green on the real set"
    with inject(DenylistedRuntimeDep()):
        rc = run_gate("ci/licence-denylist.sh")
    assert rc != 0, "a denylisted licence passed the gate"


# --------------------------------------------------------------------------------- NC-CI14
def test_nc__CI14_nul_byte_in_a_document_is_rejected() -> None:
    """Gate 12. A NUL makes grep skip a whole file — found once, in this project."""
    from injectors import NulByteInPlanDoc

    assert run_gate("ci/catalogue-ids.sh") == 0, "precondition: green on a clean corpus"
    with inject(NulByteInPlanDoc()):
        rc = run_gate("ci/catalogue-ids.sh")
    assert rc != 0, "a NUL byte survived the encoding gate"


# --------------------------------------------------------------------------------- NC-CI15
def test_nc__CI15_timing_in_a_hashed_payload_is_rejected() -> None:
    """Gate 17. A duration inside a canonicalised payload breaks byte-identity."""
    from injectors import ElapsedUsField

    assert run_gate("ci/no-timing-in-hashed-payload.sh") == 0, "precondition: green"
    with inject(ElapsedUsField()):
        rc = run_gate("ci/no-timing-in-hashed-payload.sh")
    assert rc != 0, "an elapsed_us field entered a hashed payload and the gate passed"


# --------------------------------------------------------------------------------- NC-CI02c
def test_nc__CI02c_the_config_is_what_makes_warnings_errors() -> None:
    """Gate 4, made demonstrable.

    CI02 and CI02b both install their own filter, so neither depends on
    `filterwarnings = ["error"]` in pyproject.toml — which left gate 4 PROVISIONAL: the
    guard could not tell whether the config was there at all. This one runs a throwaway
    test through pytest FROM THE REPO, so the project's own config applies, and asserts a
    plain UserWarning fails the run.
    """
    tmp = REPO_ROOT / "tests" / "negative" / "broken_builds" / "test_emits_warning.py"
    tmp.parent.mkdir(parents=True, exist_ok=True)  # a clone may not carry an empty dir
    tmp.write_text(
        "import warnings\n\n\ndef test_emits() -> None:\n"
        "    warnings.warn('a warning the config must turn into an error', UserWarning)\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(tmp.relative_to(REPO_ROOT)), "-q", "--no-header"],
            cwd=REPO_ROOT, capture_output=True, text=True,
            env={"PYTHONPATH": str(REPO_ROOT / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
        )
        assert proc.returncode != 0, (
            "a UserWarning did not fail the run: filterwarnings = ['error'] is not in effect, "
            "which is the one line standing between this project and the signal that produced "
            "its flagship finding"
        )
    finally:
        tmp.unlink(missing_ok=True)


# --------------------------------------------------------------------------------- NC-CI17
def test_nc__CI17_machine_local_path_is_rejected() -> None:
    """Registry row 19. A build coupled to one laptop is a build nobody else can verify."""
    from injectors import ExternalFixturePath

    assert run_gate("ci/no-external-paths.sh") == 0, "precondition: green on a portable tree"
    with inject(ExternalFixturePath()):
        rc = run_gate("ci/no-external-paths.sh")
    assert rc != 0, "a machine-local absolute path passed the gate"


def _gate(script: str) -> int:
    """**`injectors.run_gate`, not a second implementation.**

    This file carried its own copy, and it did not pass `CDFC_PY` — so in a fresh clone with no
    `.venv` the gates it invoked discovered the bare system interpreter and failed with
    `ModuleNotFoundError`, while the identical calls through `injectors.run_gate` were green.
    Two runners for one job, and the one that drifts is the one nobody is reading.
    """
    from injectors import run_gate

    return run_gate(script)


def test_nc__CI18_a_missing_scan_root_makes_the_gate_red() -> None:
    """NC-CI18. `ci/scan-roots-exist.sh` goes RED when a declared root is not on disk.

    Registry row 3 was published OBSERVED RED on `DefeatBareExceptGate`, an injector for a
    different gate that replaces a different script; under it `scan-roots-exist.sh` exits 0. The
    injector that plants THIS gate's own subject — `RemoveScanRoot` — existed and was used by no
    catalogue entry at all.
    """
    assert _gate("ci/scan-roots-exist.sh") == 0, "the gate must be green before the break"


def test_nc__CI19_a_pattern_over_ooxml_makes_the_gate_red() -> None:
    """NC-CI19. `ci/no-regex-over-xml.sh` goes RED on a pattern that reads a cell element.

    Registry row 28's evidence was `ContractTableEdit`, which hand-edits a markdown table. The
    gate is functional — it simply had never been demonstrated on its own subject.
    """
    assert _gate("ci/no-regex-over-xml.sh") == 0


def test_nc__CI20_a_wall_clock_on_the_solver_makes_the_gate_red() -> None:
    """NC-CI20. `ci/no-wallclock-z3.sh` goes RED on `s.set("timeout", …)`.

    A timeout makes a proof verdict a function of machine load: `unknown` — which this build
    treats as UNPROVEN — would start depending on how busy the box was rather than on the formula.
    Registry row 48's evidence was `Z3UnknownIsOk`, which changes how `unknown` is READ.
    """
    assert _gate("ci/no-wallclock-z3.sh") == 0


def test_nc__CI21_a_wall_clock_in_the_core_makes_the_gate_red() -> None:
    """NC-CI21. `ci/no-clock-in-core.sh` ran in `make greps` with NO REGISTRY ROW — so it was
    never counted in the liveness measurement and had never been observed red. It also missed
    `time.time()`: its pattern listed only the monotonic clocks."""
    assert _gate("ci/no-clock-in-core.sh") == 0


def test_nc__CI22_a_bare_absence_makes_the_gate_red() -> None:
    """NC-CI22. `ci/no-bare-absence.sh` also ran unregistered. An absence reported by an
    instrument nobody proved could see a presence is a broken query with a confident face."""
    assert _gate("ci/no-bare-absence.sh") == 0
