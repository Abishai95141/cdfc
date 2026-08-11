"""Meta-tests: negative controls ON THE NEGATIVE-CONTROL HARNESS ITSELF.

The harness is a program, and a program that returns a clean, confident, well-formed
wrong answer is the thing this project exists to refuse. These tests exist because the
harness already did exactly that once: a same-length injection left stale bytecode that
kept executing after a byte-perfect restore, and the harness's own sha256 self-check
could not see it because it hashes source, not bytecode.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from injectors import ALL_INJECTORS, StubExitsZero, inject  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PY = REPO_ROOT / "src" / "cdfc" / "cli.py"


def _constant_in_a_fresh_interpreter() -> int:
    """Read the constant from a NEW process, so an in-memory module cannot mask a
    stale cache. Reading it in-process would test our own imports, not the tree."""
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0,'src');"
            "from cdfc.cli import EXIT_NOT_IMPLEMENTED as e; print(e)",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return int(proc.stdout.strip())


def test_nc_meta__injector_does_not_poison_bytecode() -> None:
    """A same-length injection must not survive its own restore as cached bytecode.

    THE REGRESSION THIS PINS. `EXIT_NOT_IMPLEMENTED = 2` -> `= 0` is a same-length edit,
    and apply/restore happen inside one mtime tick. CPython validates a .pyc on
    (mtime, size); both are unchanged after a faithful restore, so without an explicit
    purge the interpreter serves the injected bytecode while the source reads correctly.
    """
    assert _constant_in_a_fresh_interpreter() == 2, "precondition: the tree is correct"

    with inject(StubExitsZero()):
        assert _constant_in_a_fresh_interpreter() == 0, (
            "the injector did not take effect; the negative control would be vacuous"
        )

    assert _constant_in_a_fresh_interpreter() == 2, (
        "STALE BYTECODE SURVIVED THE RESTORE. Every test after this one would have run "
        "against the injected build while the source tree looked clean."
    )


def test_nc_meta__source_digest_alone_cannot_detect_the_poisoning() -> None:
    """Pin the reason the harness's own self-check was insufficient.

    inject() compares a sha256 of the source before and after. That digest is equal in
    both the poisoned and the healthy case, so it can never distinguish them. This test
    documents the blind spot rather than leaving it to be rediscovered.
    """
    import hashlib

    before = hashlib.sha256(CLI_PY.read_bytes()).hexdigest()
    with inject(StubExitsZero()):
        pass
    after = hashlib.sha256(CLI_PY.read_bytes()).hexdigest()
    assert before == after, "source restore is faithful — and this is exactly what made the bug invisible"


def test_nc_meta__every_injector_restores_exactly() -> None:
    """Every injector round-trips the tree. inject() raises if it does not."""
    for cls in ALL_INJECTORS:
        with inject(cls()):
            pass  # inject() asserts the digest on exit


def test_nc_meta__every_injector_actually_changes_something() -> None:
    """An injector that changes nothing makes its negative control vacuous.

    Without this, a broken injector would leave every guard green and the suite would
    report that all controls pass.
    """
    import hashlib

    for cls in ALL_INJECTORS:
        inj = cls()
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None for p in inj.touches}
        with inject(inj):
            after = {
                p: hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None for p in inj.touches
            }
        assert before != after, f"injector {inj.name!r} changed nothing; its control is vacuous"
