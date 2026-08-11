"""Injectors — the deliberately broken builds every gate must reject.

A test that has never been observed to fail is not evidence. Every gate in
`ci/GATES.md` names a `broken_build`, and that name resolves to something here.

The contract is deliberately narrow:

    with inject(GreenTick()):
        assert run_gate("ci/no-green-tick.sh") != 0

An injector MUST restore the tree exactly, including on exception, or the next test
runs against a corrupted worktree and the suite reports a colour that means nothing.
`restores_exactly()` is asserted by the meta-test, not trusted.
"""

from __future__ import annotations

import contextlib
import hashlib
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _digest(paths: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(paths):
        if p.is_file():
            out[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        elif p.is_dir():
            out[str(p)] = "DIR"
        else:
            out[str(p)] = "ABSENT"
    return out


@dataclass
class Injector:
    """Base class. Subclasses implement `apply` and declare the paths they touch."""

    name: str = "injector"
    touches: list[Path] = field(default_factory=list)
    _saved: dict[Path, bytes | None] = field(default_factory=dict, repr=False)

    def apply(self) -> None:  # pragma: no cover - overridden
        raise NotImplementedError

    def _save(self) -> None:
        for p in self.touches:
            self._saved[p] = p.read_bytes() if p.is_file() else None

    def _restore(self) -> None:
        for p, data in self._saved.items():
            if data is None:
                if p.is_file():
                    p.unlink()
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            _purge_bytecode(p)


def _purge_bytecode(path: Path) -> None:
    """Delete any cached bytecode for `path`, and make its mtime unambiguously new.

    WHY THIS EXISTS, because it is not hygiene and it cost a real failure.

    CPython decides a `.pyc` is current by comparing the source's (mtime, size) against
    the pair recorded in the cache header. Every injector here performs a SAME-LENGTH
    substitution — `EXIT_NOT_IMPLEMENTED = 2` becomes `= 0` — and apply-then-restore
    happens well inside one mtime tick. So after a faithful restore the pair is
    unchanged, the cache is judged current, and **the interpreter keeps executing the
    injected bytecode while the source on disk reads correctly.**

    Observed, not hypothesised: `src/cdfc/cli.py` read `= 2` and `main(["run"])`
    returned 0, so `test_cli__unimplemented_subcommand_exits_nonzero` failed against a
    tree that was byte-for-byte correct.

    Note what did NOT catch it. `inject()` verifies a sha256 digest of the SOURCE before
    and after, and that check passed — it is blind to bytecode by construction. A
    harness whose self-check cannot see its own contamination is this project's failure
    mode occurring inside the instrument built to detect it. That is the fourth such
    instance in this corpus and the first in executable code.
    """
    if path.suffix != ".py":
        return
    import importlib
    import os

    cache = Path(importlib.util.cache_from_source(str(path)))
    if cache.exists():
        cache.unlink()
    if path.is_file():
        st = path.stat()
        os.utime(path, (st.st_atime, st.st_mtime + 1))
    importlib.invalidate_caches()


@contextlib.contextmanager
def inject(inj: Injector) -> Iterator[Injector]:
    before = _digest(inj.touches)
    inj._save()
    try:
        inj.apply()
        yield inj
    finally:
        inj._restore()
    after = _digest(inj.touches)
    if before != after:
        raise AssertionError(
            f"injector {inj.name!r} did not restore the tree exactly: "
            f"{ {k: (before.get(k), after.get(k)) for k in before if before.get(k) != after.get(k)} }"
        )


def run_gate(script: str) -> int:
    """Run a shell gate and return its exit code."""
    return subprocess.run(
        ["bash", str(REPO_ROOT / script)], cwd=REPO_ROOT, capture_output=True, text=True
    ).returncode


# --------------------------------------------------------------------------------
# The P0 injectors
# --------------------------------------------------------------------------------

TEMPLATE = REPO_ROOT / "src" / "cdfc" / "surface" / "templates" / "report.html.j2"
EVALUATE_INIT = REPO_ROOT / "src" / "cdfc" / "evaluate" / "__init__.py"
CLI_PY = REPO_ROOT / "src" / "cdfc" / "cli.py"
PYPROJECT = REPO_ROOT / "pyproject.toml"


class GreenTick(Injector):
    """An all-clear reaches a user surface."""

    def __init__(self) -> None:
        super().__init__(name="green_tick", touches=[TEMPLATE])

    def apply(self) -> None:
        TEMPLATE.write_text(TEMPLATE.read_text() + '\n<p class="ok">All clear ✅</p>\n')


class BareExcept(Injector):
    """A crash is swallowed into a clean state."""

    def __init__(self) -> None:
        super().__init__(name="bare_except", touches=[EVALUATE_INIT])

    def apply(self) -> None:
        EVALUATE_INIT.write_text(
            EVALUATE_INIT.read_text()
            + "\n\ndef _swallow() -> None:\n    try:\n        pass\n    except:\n        pass\n"
        )


class RemoveScanRoot(Injector):
    """A declared scan root does not exist, so every grep over it passes trivially."""

    def __init__(self) -> None:
        super().__init__(name="remove_scan_root", touches=[EVALUATE_INIT])

    def apply(self) -> None:
        EVALUATE_INIT.unlink()
        # remove the directory too, so the root is genuinely missing
        with contextlib.suppress(OSError):
            EVALUATE_INIT.parent.rmdir()

    def _restore(self) -> None:
        EVALUATE_INIT.parent.mkdir(parents=True, exist_ok=True)
        super()._restore()


class EmptyScanRoot(Injector):
    """Admission-side twin: the root EXISTS but is empty. This must PASS."""

    def __init__(self) -> None:
        super().__init__(name="empty_scan_root", touches=[EVALUATE_INIT])

    def apply(self) -> None:
        EVALUATE_INIT.unlink()  # directory remains


class StubExitsZero(Injector):
    """An unimplemented subcommand reports success."""

    def __init__(self) -> None:
        super().__init__(name="stub_exits_zero", touches=[CLI_PY])

    def apply(self) -> None:
        CLI_PY.write_text(CLI_PY.read_text().replace("EXIT_NOT_IMPLEMENTED = 2", "EXIT_NOT_IMPLEMENTED = 0"))


class WarningsTolerated(Injector):
    """`filterwarnings = ["error"]` is relaxed, so the parser's own warning is discarded."""

    def __init__(self) -> None:
        super().__init__(name="warnings_tolerated", touches=[PYPROJECT])

    def apply(self) -> None:
        PYPROJECT.write_text(
            PYPROJECT.read_text().replace('filterwarnings = ["error"]', 'filterwarnings = ["default"]')
        )


ALL_INJECTORS: tuple[type[Injector], ...] = (
    GreenTick,
    BareExcept,
    RemoveScanRoot,
    EmptyScanRoot,
    StubExitsZero,
    WarningsTolerated,
)
