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
import shutil
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
    # `import importlib` does NOT bind importlib.util. This worked under pytest only
    # because pytest imports importlib.util first — a dependency on what else happened
    # to run, which is exactly the class of latent defect this project is about.
    import importlib
    import importlib.util
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
        # Purge on APPLY as well as on restore. The staleness is SYMMETRIC and fixing
        # only the restore direction left the injector silently not taking effect: a
        # same-length edit inside one mtime tick leaves the pre-injection bytecode
        # judged current, so the interpreter runs the CORRECT build while the source is
        # broken — a negative control that quietly proves nothing. It passed for a while
        # only because a preceding restore happened to bump the mtime first.
        for _p in inj.touches:
            _purge_bytecode(_p)
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
    """A declared scan root does not exist, so every grep over it passes trivially.

    REPAIRED AT P4, dated 12 Aug 2026, and the repair is the reason to read this class.
    The first version deleted `src/cdfc/evaluate/__init__.py` and then `rmdir`-ed the directory,
    with the failure suppressed. That worked while `evaluate/` held exactly one file. P4-B3 added
    `celrt.py`, so the `rmdir` began failing silently, **the directory went on existing, the gate
    stayed green, and the flagship P0 negative control proved nothing** — while still reporting
    itself as caught.

    Nothing about the sweep could see this: the injector applied cleanly, the tree restored
    exactly, and the digest check passed. It was found only because the guard test went red, which
    it did for the right reason. The injector now removes **every** file under the root, so it
    cannot quietly become a no-op again as the package grows.
    """

    def __init__(self) -> None:
        root = EVALUATE_INIT.parent
        files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix != ".pyc")
        super().__init__(name="remove_scan_root", touches=files or [EVALUATE_INIT])

    def apply(self) -> None:
        root = EVALUATE_INIT.parent
        if root.is_dir():
            shutil.rmtree(root)

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


# --------------------------------------------------------------------------------
# P0-B3 injectors — one per catalogue entry that declares a flipping guard
# --------------------------------------------------------------------------------

GATES_MD = REPO_ROOT / "ci" / "GATES.md"
LOCKFILE = REPO_ROOT / "requirements.lock"
CALC_INIT = REPO_ROOT / "src" / "cdfc" / "calc" / "__init__.py"
PERF_PKG = REPO_ROOT / "src" / "cdfc" / "measure" / "perf" / "__init__.py"
FIXTURE = REPO_ROOT / "fixtures" / "prescribed" / "ITFS_Monthly_report201220241626.xlsx"
ABSENCE_DOC = REPO_ROOT / "docs" / "ABSENCE-SCOPE.md"


class DuplicateGateId(Injector):
    """Two registry rows share an id, so the registry is shorter than it looks."""

    def __init__(self) -> None:
        super().__init__(name="duplicate_gate_id", touches=[GATES_MD])

    def apply(self) -> None:
        GATES_MD.write_text(GATES_MD.read_text().replace("| 18 | pytest |", "| 17 | pytest |", 1))


class DemoteGateToPending(Injector):
    """A gate that resisted demonstration is quietly moved to PENDING."""

    def __init__(self) -> None:
        super().__init__(name="demote_gate_to_pending", touches=[GATES_MD])

    def apply(self) -> None:
        t = GATES_MD.read_text()
        # row 2 -> PENDING
        lines = t.splitlines()
        for i, ln in enumerate(lines):
            if ln.startswith("| 2 |"):
                lines[i] = ln.rsplit("| LIVE |", 1)[0] + "| PENDING |"
                break
        GATES_MD.write_text("\n".join(lines) + "\n")


class BlankDemonstrableRed(Injector):
    """A gate loses the phase at which it can be observed red."""

    def __init__(self) -> None:
        super().__init__(name="blank_demonstrable_red", touches=[GATES_MD])

    def apply(self) -> None:
        lines = GATES_MD.read_text().splitlines()
        for i, ln in enumerate(lines):
            if ln.startswith("| 1 |"):
                cells = ln.split("|")
                cells[5] = "  "  # demonstrable_red_at
                lines[i] = "|".join(cells)
                break
        GATES_MD.write_text("\n".join(lines) + "\n")


class AddGateRow(Injector):
    """A row is appended without anything else noticing."""

    def __init__(self) -> None:
        super().__init__(name="add_gate_row", touches=[GATES_MD])

    def apply(self) -> None:
        t = GATES_MD.read_text()
        marker = "| 18 | pytest |"
        idx = t.index(marker)
        end = t.index("\n", idx) + 1
        # id 99: the injector must not collide with a REAL row. It used 19, and the
        # moment row 19 was genuinely registered the parser raised on the duplicate and a
        # second guard went red — the sweep caught it as an exact-set mismatch.
        row = "| 99 | shell | an injected row nobody registered | P0 | P0 | injector | LIVE |\n"
        GATES_MD.write_text(t[:end] + row + t[end:])


class UnpinDependency(Injector):
    """A dependency loses its wheel hash."""

    def __init__(self) -> None:
        super().__init__(name="unpin_dependency", touches=[LOCKFILE])

    def apply(self) -> None:
        # Remove EVERY hash line of the FIRST package block. Removing one of two leaves
        # the package pinned by the other, and the control proves nothing — which is
        # exactly what the first version of this injector did.
        lines = LOCKFILE.read_text().splitlines()
        out, in_first, seen_pkg = [], False, False
        for ln in lines:
            is_pkg = bool(ln) and not ln[:1].isspace() and "==" in ln and not ln.startswith("#")
            if is_pkg:
                if not seen_pkg:
                    seen_pkg, in_first = True, True
                else:
                    in_first = False
            if in_first and ln.strip().startswith("--hash=sha256:"):
                continue
            if in_first and is_pkg:
                ln = ln.replace(" \\", "")
            out.append(ln)
        LOCKFILE.write_text("\n".join(out) + "\n")


class ClockInCore(Injector):
    """A self-measured duration enters the deterministic core."""

    def __init__(self) -> None:
        super().__init__(name="clock_in_core", touches=[CALC_INIT])

    def apply(self) -> None:
        CALC_INIT.write_text(
            CALC_INIT.read_text()
            + "\nimport time\n\n\ndef _elapsed() -> float:\n    return time.perf_counter()\n"
        )


class FlipFixtureByte(Injector):
    """A vendored fixture drifts by one byte."""

    def __init__(self) -> None:
        super().__init__(name="flip_fixture_byte", touches=[FIXTURE])

    def apply(self) -> None:
        b = bytearray(FIXTURE.read_bytes())
        b[-1] ^= 0x01
        FIXTURE.write_bytes(bytes(b))


class AbsenceCitesEmptyControl(Injector):
    """A document asserts an absence citing a ledger row whose control count is zero."""

    def __init__(self) -> None:
        # the ledger is in `touches` so the planted row is removed on restore; a
        # leaked row would make the gate red for every later test.
        from cdfc.measure.absence import DEFAULT_LEDGER
        super().__init__(name="absence_cites_empty_control", touches=[ABSENCE_DOC, DEFAULT_LEDGER])

    def apply(self) -> None:
        from cdfc.measure.absence import DEFAULT_LEDGER  # noqa: PLC0415

        DEFAULT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
        import json

        row = {
            "row_id": "deadbeefdeadbeef",
            "query_name": "injected_empty_control",
            "corpus_id": "injected",
            "count": 0,
            "positive_control_count": 0,
            "admissible": False,
        }
        with DEFAULT_LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        # assembled at runtime — see tests/negative/test_nc_absence.py for why
        phrase = "does not " + "occur"
        ABSENCE_DOC.write_text(
            ABSENCE_DOC.read_text()
            + f"\nThe term {phrase} anywhere in the corpus (ledger:deadbeefdeadbeef).\n"
        )


ALL_INJECTORS = ALL_INJECTORS + (
    DuplicateGateId,
    DemoteGateToPending,
    BlankDemonstrableRed,
    AddGateRow,
    UnpinDependency,
    ClockInCore,
    FlipFixtureByte,
    AbsenceCitesEmptyControl,
)

BY_NAME: dict[str, type[Injector]] = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# GATE-DEFEATING injectors.
#
# The composition rule this project learned on its first sweep: **a guard that itself
# applies an injector cannot be a control under a second injector.** For a gate-style
# entry the break is not "the artifact is broken" — the guard already breaks it — it is
# "THE GATE IS DEFEATED". So these injectors weaken the gate script, and the guard, which
# injects an artifact break and asserts rejection, goes red because nothing rejects.
#
# The admission-side twin then stays green, because a defeated gate still passes the
# legitimate case. Both directions of every entry carry information.
# --------------------------------------------------------------------------------

CI = REPO_ROOT / "ci"


class _DefeatGate(Injector):
    """Make a gate script exit 0 unconditionally, keeping its output shape."""

    script = ""

    def __init__(self) -> None:
        super().__init__(name=f"defeat_{self.script}", touches=[CI / self.script])

    def apply(self) -> None:
        p = CI / self.script
        p.write_text(
            "#!/usr/bin/env bash\n# DEFEATED BY AN INJECTOR\nset -euo pipefail\n"
            f'echo "{self.script.removesuffix(".sh")}: OK"\nexit 0\n'
        )


class DefeatGreenTickGate(_DefeatGate):
    script = "no-green-tick.sh"


class DefeatBareExceptGate(_DefeatGate):
    script = "no-bare-except.sh"


class DefeatClockGate(_DefeatGate):
    script = "no-clock-in-core.sh"


class DefeatAbsenceGate(_DefeatGate):
    script = "no-bare-absence.sh"


class WeakenCliTest(Injector):
    """The unit test that catches a zero-exit stub is relaxed to accept any exit code."""

    def __init__(self) -> None:
        super().__init__(name="weaken_cli_test", touches=[REPO_ROOT / "tests" / "unit" / "test_cli.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "tests" / "unit" / "test_cli.py"
        p.write_text(
            p.read_text().replace(
                'assert rc == 2, "an unimplemented subcommand must exit 2; exiting 0 is an all-clear"',
                "assert rc >= 0  # DEFEATED BY AN INJECTOR",
            )
        )


ALL_INJECTORS = ALL_INJECTORS + (
    DefeatGreenTickGate,
    DefeatBareExceptGate,
    DefeatClockGate,
    DefeatAbsenceGate,
    WeakenCliTest,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


PLAN_DOC = REPO_ROOT / "plan" / "00-decomposition.md"


class HardcodeGateCount(Injector):
    """The CLI stops reading the registry and pins the count as a literal.

    Gate 10's registered broken_build was "add a row without touching cli.py" — but
    `--version` READS the registry, so the count tracks automatically and that break
    cannot make the gate red. A gate whose named broken_build cannot make it fail is a
    preference with a filename, which the registry's own rule forbids. The break that
    CAN fail it is the one that stops it reading.
    """

    def __init__(self) -> None:
        super().__init__(name="hardcode_gate_count", touches=[CLI_PY])

    def apply(self) -> None:
        CLI_PY.write_text(
            CLI_PY.read_text().replace(
                'return f"cdfc {__version__} (schema {_schema_sha8()}, gates {len(parse())})"',
                'return f"cdfc {__version__} (schema {_schema_sha8()}, gates 18)"',
            )
        )


class DenylistedRuntimeDep(Injector):
    """A copyleft-incompatible package enters the declared RUNTIME set."""

    def __init__(self) -> None:
        super().__init__(name="denylisted_runtime_dep", touches=[CI / "licence-denylist.sh"])

    def apply(self) -> None:
        p = CI / "licence-denylist.sh"
        t = p.read_text()
        # declare a package we know carries GPL-3.0 metadata in this environment
        t = t.replace(
            'DENY = {"GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0", "AGPL-3.0-only", "SSPL-1.0"}',
            'DENY = {"GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0", "AGPL-3.0-only", "SSPL-1.0", "MIT"}',
        )
        p.write_text(t)


class NulByteInPlanDoc(Injector):
    """A raw NUL makes grep skip an entire document.

    Not hypothetical: one was found in this project's own plan, and it would have made
    the id-collision gate run green over the largest instance of the problem it checks.
    """

    def __init__(self) -> None:
        super().__init__(name="nul_byte_in_plan_doc", touches=[PLAN_DOC])

    def apply(self) -> None:
        PLAN_DOC.write_bytes(PLAN_DOC.read_bytes() + b"\x00")


class ElapsedUsField(Injector):
    """A duration field is written into a hashed payload's shape."""

    def __init__(self) -> None:
        super().__init__(name="elapsed_us_field", touches=[REPO_ROOT / "src" / "cdfc" / "attest" / "__init__.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src" / "cdfc" / "attest" / "__init__.py"
        p.write_text(
            p.read_text()
            + "\n\nclass CanaryRow:\n    predicate_id: str = \"\"\n    elapsed_us: int = 0\n"
        )


ALL_INJECTORS = ALL_INJECTORS + (
    HardcodeGateCount,
    DenylistedRuntimeDep,
    NulByteInPlanDoc,
    ElapsedUsField,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class HardcodeCountAndAddRow(Injector):
    """Composite: pin the count as a literal AND add a row, so the literal is wrong.

    Neither half flips gate 10 alone — a hardcoded 18 matches an 18-row registry, and a
    19th row is tracked automatically by a CLI that reads. The break is the PAIR, and an
    entry whose injector performs only half of it reports a mismatch rather than a catch.
    """

    def __init__(self) -> None:
        super().__init__(name="hardcode_count_and_add_row", touches=[CLI_PY, GATES_MD])

    def apply(self) -> None:
        HardcodeGateCount().apply()
        AddGateRow().apply()


ALL_INJECTORS = ALL_INJECTORS + (HardcodeCountAndAddRow,)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class BreakCriticalPathTotal(Injector):
    """A per-phase figure changes and the displayed total does not follow.

    The shared-denominator error, in a schedule. Found in this project's own plan, where
    two phases were re-estimated and the critical-path total kept its old value.
    """

    def __init__(self) -> None:
        super().__init__(name="break_critical_path_total", touches=[PLAN_DOC])

    def apply(self) -> None:
        t = PLAN_DOC.read_text()
        PLAN_DOC.write_text(
            t.replace(" 8    8    10   17   14   12  10.5  16   9.5    6     16    =  127 working days",
                      " 9    8    10   17   14   12  10.5  16   9.5    6     16    =  127 working days")
        )


ALL_INJECTORS = ALL_INJECTORS + (BreakCriticalPathTotal,)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# P1 injectors
# --------------------------------------------------------------------------------

READER_AP = REPO_ROOT / "src" / "cdfc" / "ingest" / "reader_lxml_b.py"
MANIFEST_PY = REPO_ROOT / "src" / "cdfc" / "ingest" / "manifest.py"
RECEIPT_PY = REPO_ROOT / "src" / "cdfc" / "ingest" / "receipt.py"
GUARD_PY = REPO_ROOT / "src" / "cdfc" / "ingest" / "container_guard.py"


class ReaderAPrimeMiscounts(Injector):
    """Reader A' returns a wrong sheet count.

    The control on the agreement matrix itself: 72/72 AGREE is evidence only if the
    comparator has been observed reporting something else.
    """

    def __init__(self) -> None:
        super().__init__(name="reader_a_prime_miscounts", touches=[READER_AP])

    def apply(self) -> None:
        READER_AP.write_text(
            READER_AP.read_text().replace("n_sheets=len(sheet_els),", "n_sheets=len(sheet_els) + 1,")
        )


class ManifestSwallowsConstruct(Injector):
    """The manifest stops recording constructs it did not understand."""

    def __init__(self) -> None:
        super().__init__(name="manifest_swallows_construct", touches=[MANIFEST_PY])

    def apply(self) -> None:
        MANIFEST_PY.write_text(
            MANIFEST_PY.read_text().replace(
                "        counts[tag] = counts.get(tag, 0) + 1",
                "        continue  # INJECTED: the residue is swallowed",
            )
        )


class SkipWithoutReasonAllowed(Injector):
    """A part may be skipped with no stated reason."""

    def __init__(self) -> None:
        super().__init__(name="skip_without_reason_allowed", touches=[MANIFEST_PY])

    def apply(self) -> None:
        t = MANIFEST_PY.read_text()
        MANIFEST_PY.write_text(t.replace("            if not reason or not reason.strip():",
                                         "            if False:"))


class SecondParserFactory(Injector):
    """lxml is constructed outside the single sanctioned factory, defeating the spy."""

    def __init__(self) -> None:
        super().__init__(name="second_parser_factory", touches=[GUARD_PY])

    def apply(self) -> None:
        GUARD_PY.write_text(
            GUARD_PY.read_text()
            + "\n\ndef _sneaky(b: bytes):\n"
            "    from lxml import etree\n"
            "    return etree.fromstring(b)\n"
        )


class ReceiptNormalisesBytes(Injector):
    """The receipt hashes a normalised form instead of the exact received bytes."""

    def __init__(self) -> None:
        super().__init__(name="receipt_normalises_bytes", touches=[RECEIPT_PY])

    def apply(self) -> None:
        RECEIPT_PY.write_text(
            RECEIPT_PY.read_text().replace(
                "    digest_hex = hashlib.sha256(data).hexdigest()",
                "    digest_hex = hashlib.sha256(data.rstrip(b'\\x00')).hexdigest()",
            )
        )


ALL_INJECTORS = ALL_INJECTORS + (
    ReaderAPrimeMiscounts,
    ManifestSwallowsConstruct,
    SkipWithoutReasonAllowed,
    SecondParserFactory,
    ReceiptNormalisesBytes,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class ExternalFixturePath(Injector):
    """A test points at a machine-local absolute path instead of the vendored fixture."""

    def __init__(self) -> None:
        super().__init__(name="external_fixture_path",
                         touches=[REPO_ROOT / "tests" / "unit" / "test_receipt.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "tests" / "unit" / "test_receipt.py"
        p.write_text(p.read_text() + '\n\nEXTERNAL = "/Users/somebody/corpus/f.xlsx"\n')


ALL_INJECTORS = ALL_INJECTORS + (ExternalFixturePath,)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# P2 injectors
# --------------------------------------------------------------------------------

MASK_A = REPO_ROOT / "src" / "cdfc" / "schema" / "styles_mask.py"


class MaskSkipsHiddenSheets(Injector):
    """Scope truncation by hidden sheet.

    The defect P2's own headline number cannot see: on FME this still returns 3,747, so
    the number is right by accident while the code is wrong. Only a test asserting the
    SHEET SET catches it.
    """

    def __init__(self) -> None:
        super().__init__(name="mask_skips_hidden_sheets", touches=[MASK_A])

    def apply(self) -> None:
        MASK_A.write_text(
            MASK_A.read_text().replace(
                '        out.append((sh.get("name", ""), sh.get("state", "visible"), part))',
                '        if sh.get("state", "visible") != "visible":\n            continue\n'
                '        out.append((sh.get("name", ""), sh.get("state", "visible"), part))',
            )
        )


class MaskReadsAbsenceAsUnlocked(Injector):
    """The rejected reading becomes the adopted one, silently."""

    def __init__(self) -> None:
        super().__init__(name="mask_reads_absence_as_unlocked", touches=[MASK_A])

    def apply(self) -> None:
        MASK_A.write_text(
            MASK_A.read_text().replace(
                "    if rule is Rule.V3_ABS:\n        return False",
                "    if True:\n        return False",
            )
        )


class MaskDropsValidationState(Injector):
    """The denominator stops declaring that nothing has externally validated it."""

    def __init__(self) -> None:
        super().__init__(name="mask_drops_validation_state", touches=[MASK_A])

    def apply(self) -> None:
        MASK_A.write_text(
            MASK_A.read_text().replace(
                '            "validation_state": self.validation_state,\n', ""
            )
        )


class MaskSkipsRuleSix(Injector):
    """Rule 6 stops firing, so a workbook with no protection mask gets a number anyway."""

    def __init__(self) -> None:
        super().__init__(name="mask_skips_rule_six", touches=[MASK_A])

    def apply(self) -> None:
        MASK_A.write_text(MASK_A.read_text().replace("        if not any_protection:", "        if False:"))


ALL_INJECTORS = ALL_INJECTORS + (
    MaskSkipsHiddenSheets,
    MaskReadsAbsenceAsUnlocked,
    MaskDropsValidationState,
    MaskSkipsRuleSix,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


KEYS_PY = REPO_ROOT / "src" / "cdfc" / "schema" / "stable_keys.py"
FP_PY = REPO_ROOT / "src" / "cdfc" / "schema" / "fingerprint.py"


class KeysAreCoordinates(Injector):
    """The stable key degrades to a coordinate, so a row insertion rebinds silently."""

    def __init__(self) -> None:
        super().__init__(name="keys_are_coordinates", touches=[KEYS_PY])

    def apply(self) -> None:
        KEYS_PY.write_text(
            KEYS_PY.read_text().replace(
                '        return f"{_slug(self.sheet_name)}.{head}.row[{self.row_ordinal}].{_slug(self.row_label)}"',
                '        return f"{_slug(self.sheet_name)}.{head}.{_slug(self.row_label)}"',
            )
        )


class UnresolvedKeyGuesses(Injector):
    """An UNRESOLVED key falls back to a coordinate instead of blocking."""

    def __init__(self) -> None:
        super().__init__(name="unresolved_key_guesses", touches=[KEYS_PY])

    def apply(self) -> None:
        KEYS_PY.write_text(
            KEYS_PY.read_text().replace(
                '    if field.resolution_state != "RESOLVED" or field.resolved_ref is None:',
                '    if False:',
            )
        )


class FingerprintIncludesFormulas(Injector):
    """Formula content enters the structural fingerprint.

    Converts the design's flagship check — a formula cell overwritten with a literal —
    from a FINDING about the filing into `invalid.template_unbound`, an apparatus failure
    about us.
    """

    def __init__(self) -> None:
        super().__init__(name="fingerprint_includes_formulas", touches=[FP_PY])

    def apply(self) -> None:
        FP_PY.write_text(
            FP_PY.read_text().replace(
                '        "unlocked_mask": sorted(f"{s}!{r}" for s, r in fs.cells),',
                '        "unlocked_mask": sorted(f"{s}!{r}" for s, r in fs.cells),\n'
                '        "formulas": sorted(\n'
                '            f"{f.sheet}!{f.ref}={f.text}"\n'
                '            for f in __import__("cdfc.ingest.reader_lxml", fromlist=["read"])\n'
                '            .read(blob_path).formulas\n'
                '        ),',
            )
        )


ALL_INJECTORS = ALL_INJECTORS + (KeysAreCoordinates, UnresolvedKeyGuesses, FingerprintIncludesFormulas)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class FloatInCalc(Injector):
    """A float enters the deterministic numeric core."""

    def __init__(self) -> None:
        super().__init__(name="float_in_calc",
                         touches=[REPO_ROOT / "src" / "cdfc" / "calc" / "operators.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src" / "cdfc" / "calc" / "operators.py"
        p.write_text("def _ratio(a, b) -> float:\n    return float(a) / float(b)\n")


class EvaluatorIgnoresNotRunInputs(Injector):
    """A cell reading a NOT_RUN cell computes with a zero instead of blocking."""

    def __init__(self) -> None:
        super().__init__(name="evaluator_ignores_not_run_inputs",
                         touches=[REPO_ROOT / "src" / "cdfc" / "calc" / "evaluate.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src" / "cdfc" / "calc" / "evaluate.py"
        p.write_text(p.read_text().replace(
            "        blocked = sorted(d for d in deps.get(key, ()) if d in not_run)",
            "        blocked = []"))


ALL_INJECTORS = ALL_INJECTORS + (FloatInCalc, EvaluatorIgnoresNotRunInputs)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class DependentUsesMasterUnshifted(Injector):
    """A shared dependent evaluates the master's expression WITHOUT shifting it.

    Returns a well-formed number for the wrong row — 211 of 505 FME formula cells.
    """

    def __init__(self) -> None:
        super().__init__(name="dependent_uses_master_unshifted",
                         touches=[REPO_ROOT / "src" / "cdfc" / "calc" / "shift.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src" / "cdfc" / "calc" / "shift.py"
        p.write_text(p.read_text().replace(
            "    if drow == 0 and dcol == 0:\n        return text",
            "    if True:\n        return text"))


class ShapeRefsCountAsValueDeps(Injector):
    """ROWS()/ROW() arguments are treated as value dependencies.

    Invents circular references that do not exist — thirty of them in the FME workbook —
    and reports them as NOT_RUN, i.e. as a finding about the regulator's template rather
    than a defect in our dependency analyser.
    """

    def __init__(self) -> None:
        super().__init__(name="shape_refs_count_as_value_deps",
                         touches=[REPO_ROOT / "src" / "cdfc" / "calc" / "evaluate.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src" / "cdfc" / "calc" / "evaluate.py"
        p.write_text(p.read_text().replace(
            "SHAPE_ONLY_FUNCTIONS = frozenset({\"ROW\", \"ROWS\", \"COLUMN\", \"COLUMNS\"})",
            "SHAPE_ONLY_FUNCTIONS = frozenset()"))


ALL_INJECTORS = ALL_INJECTORS + (DependentUsesMasterUnshifted, ShapeRefsCountAsValueDeps)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


FACTS = REPO_ROOT / "src" / "cdfc" / "facts"


class MoneyScaledTwice(Injector):
    """Money is scaled a second time — a well-formed number 1000x wrong."""

    def __init__(self) -> None:
        super().__init__(name="money_scaled_twice", touches=[FACTS / "units.py"])

    def apply(self) -> None:
        p = FACTS / "units.py"
        p.write_text(p.read_text().replace(
            "        scaled = d * UNITS_PER_USD_MILLION",
            "        scaled = d * UNITS_PER_USD_MILLION * UNITS_PER_USD_MILLION"))


class WarrantComposesByStrongest(Injector):
    """The anchor lattice takes the MAXIMUM, so one extracted value launders itself into a
    deterministic total."""

    def __init__(self) -> None:
        super().__init__(name="warrant_composes_by_strongest", touches=[FACTS / "anchor.py"])

    def apply(self) -> None:
        p = FACTS / "anchor.py"
        p.write_text(p.read_text().replace(
            "    weakest = min(a.warrant for a in anchors)",
            "    weakest = max(a.warrant for a in anchors)"))


class LeafWithoutCellAllowed(Injector):
    """A leaf may exist with no __cell__ — a value that cannot be shown or re-derived."""

    def __init__(self) -> None:
        super().__init__(name="leaf_without_cell_allowed", touches=[FACTS / "fact_table.py"])

    def apply(self) -> None:
        p = FACTS / "fact_table.py"
        p.write_text(p.read_text().replace("        if not self.cell:", "        if False:"))


class ToleranceBecomesRelative(Injector):
    """Tolerance becomes a percentage, so a total of zero admits everything."""

    def __init__(self) -> None:
        super().__init__(name="tolerance_becomes_relative", touches=[FACTS / "units.py"])

    def apply(self) -> None:
        p = FACTS / "units.py"
        p.write_text(p.read_text().replace(
            "    return abs(a - b) <= tau(n_summands)",
            "    return abs(a - b) <= max(abs(a), abs(b)) // 100"))


ALL_INJECTORS = ALL_INJECTORS + (
    MoneyScaledTwice, WarrantComposesByStrongest, LeafWithoutCellAllowed, ToleranceBecomesRelative,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# The P4 injectors — the predicate envelope, the CEL substrate, the harvest
# --------------------------------------------------------------------------------

PRED = REPO_ROOT / "src" / "cdfc" / "predicates"
MEASURE = REPO_ROOT / "src" / "cdfc" / "measure"


class ProjectionDropsAField(Injector):
    """A field leaves the canonical serialisation, so it leaves the predicate's IDENTITY.

    The consequence is not abstract: a predicate could then be re-issued with a narrowed
    `claims_fault_classes` under the SAME `code_sha256`, and the registry would treat it as the
    same predicate it already qualified.
    """

    def __init__(self) -> None:
        super().__init__(name="projection_drops_a_field", touches=[PRED / "canonical.py"])

    def apply(self) -> None:
        p = PRED / "canonical.py"
        p.write_text(p.read_text().replace(
            "    out = {f.name: _plain(getattr(c, f.name)) for f in fields(c)}",
            "    out = {f.name: _plain(getattr(c, f.name)) for f in fields(c)\n"
            "           if f.name != 'claims_fault_classes'}"))


class KeysMismatchCollapsed(Injector):
    """Both directions of the both-ways check raise ONE type, so the two are indistinguishable.

    NC-Q04's subject. A key read-but-not-declared means the pre-flight set is too small; a key
    declared-but-not-read means the settled numerator is overstated. A repair applied to the wrong
    side of a collapsed message is a repair that fixes nothing.
    """

    def __init__(self) -> None:
        super().__init__(name="keys_mismatch_collapsed", touches=[PRED / "ast_walker.py"])

    def apply(self) -> None:
        p = PRED / "ast_walker.py"
        p.write_text(p.read_text().replace(
            "    unread = tuple(sorted(declared - read))\n    if unread:\n        raise DeclaredKeyUnread(pid, unread)",
            "    unread = tuple(sorted(declared - read))\n    if unread:\n        raise UndeclaredKeyRead(pid, unread)"))


class PermissiveSubsetWalker(Injector):
    """The subset checker stops walking, so every banned construct is admitted."""

    def __init__(self) -> None:
        super().__init__(name="permissive_subset_walker", touches=[PRED / "cel_profile.py"])

    def apply(self) -> None:
        p = PRED / "cel_profile.py"
        p.write_text(p.read_text().replace(
            "    tree = parse(source, slot=slot)\n    _walk(",
            "    tree = parse(source, slot=slot)\n    return None\n    _walk("))


class LexicalKeyExtraction(Injector):
    """`read_keys` becomes a regex over the source.

    It reports the comprehension binding as a document root and loses `[*]` — the same defect
    class as `<f[ >][^>]*>` over OOXML, one level up, where the key set is the settled fraction's
    denominator.
    """

    def __init__(self) -> None:
        super().__init__(name="lexical_key_extraction", touches=[PRED / "ast_walker.py"])

    def apply(self) -> None:
        p = PRED / "ast_walker.py"
        p.write_text(p.read_text().replace(
            "def walk_source(source: str, *, slot: Slot) -> WalkResult:\n    w = _Walker()",
            "def walk_source(source: str, *, slot: Slot) -> WalkResult:\n"
            "    import re as _re\n"
            "    _lex = frozenset(_re.findall(r'[A-Za-z_][A-Za-z0-9_.]*\\\\.[A-Za-z_][A-Za-z0-9_]*', source))\n"
            "    return WalkResult(keys=_lex, host_fns=frozenset(), refs=(), types={})\n"
            "    w = _Walker()"))


class TotalWithoutDistribution(Injector):
    """The harvest measurement renders its total and drops the per-workbook table.

    515 alone reads as breadth. 443 of it came from two workbooks, and the reader cannot tell.
    """

    def __init__(self) -> None:
        super().__init__(name="total_without_distribution", touches=[MEASURE / "harvest_report.py"])

    def apply(self) -> None:
        p = MEASURE / "harvest_report.py"
        p.write_text(p.read_text().replace(
            "    for r in rows:\n        cells = \" | \".join(str(r.by_class.get(k, 0)) for k in all_classes)",
            "    for r in []:\n        cells = \" | \".join(str(r.by_class.get(k, 0)) for k in all_classes)"))


class WeakPileDropped(Injector):
    """A construct the class set cannot express is dropped instead of recorded.

    The coverage claim then counts what was harvested and says nothing about what was passed over,
    which is the definition of an undeclared suppression.
    """

    def __init__(self) -> None:
        super().__init__(name="weak_pile_dropped", touches=[PRED / "harvest.py"])

    def apply(self) -> None:
        p = PRED / "harvest.py"
        p.write_text(p.read_text().replace(
            "    def skip(self, kind: SkipKind, sheet: str, ref: str, detail: str) -> None:\n"
            "        self.skips.append(SkipRecord(kind=kind, sheet=sheet, ref=ref, detail=detail))",
            "    def skip(self, kind: SkipKind, sheet: str, ref: str, detail: str) -> None:\n"
            "        return None"))


class ClauselessReasonOptional(Injector):
    """A TEMPLATE-obligation candidate may cite no statute and say nothing about why.

    The published pair then reports `0 / N` with no way to tell a deliberate absence from an
    unfilled field.
    """

    def __init__(self) -> None:
        super().__init__(name="clauseless_reason_optional", touches=[PRED / "envelope.py"])

    def apply(self) -> None:
        p = PRED / "envelope.py"
        p.write_text(p.read_text().replace(
            "        if c.clause_absent_reason not in CLAUSE_ABSENT_REASONS:",
            "        if False and c.clause_absent_reason not in CLAUSE_ABSENT_REASONS:"))


class ClaimsFromKillVector(Injector):
    """The fault-class claim is narrowed per predicate instead of declared per class.

    This is D-P4-06's whole subject: a claim tuned after a campaign lets a predicate that killed
    one class of one operator score 1.00 and be admitted BLOCKING.
    """

    def __init__(self) -> None:
        super().__init__(
            name="claims_from_kill_vector",
            touches=[PRED / "harvest_classes" / "sum_identity.py"],
        )

    def apply(self) -> None:
        p = PRED / "harvest_classes" / "sum_identity.py"
        p.write_text(p.read_text().replace(
            "            claims_fault_classes=CLAIMS_FAULT_CLASSES,",
            "            claims_fault_classes=(CLAIMS_FAULT_CLASSES[0],) if int(ref[1:] or 0) % 2 "
            "else CLAIMS_FAULT_CLASSES,"))


class HostFnResolvesLive(Injector):
    """`reg_resolves` falls back to an answer when no snapshot is bound.

    A verdict that depends on what a remote endpoint said at run time cannot be re-derived from the
    filing's bytes, and the fallback is invisible in the report.
    """

    def __init__(self) -> None:
        super().__init__(
            name="host_fn_resolves_live",
            touches=[PRED / "host_fns" / "reg_resolves.py"],
        )

    def apply(self) -> None:
        p = PRED / "host_fns" / "reg_resolves.py"
        p.write_text(p.read_text().replace(
            "    record = _REGISTRY.lookup(key)   # raises SnapshotMissing when nothing is bound",
            "    try:\n"
            "        record = _REGISTRY.lookup(key)\n"
            "    except Exception:\n"
            "        record = True   # the silent live-ish fallback this control exists to catch"))


class HostFnLosesItsThirdValue(Injector):
    """`nav_interval` becomes two-valued, so *the regulator did not legislate this* disappears.

    The item then reports a frequency we picked, and the report presents our guess as the rule.
    """

    def __init__(self) -> None:
        super().__init__(
            name="host_fn_loses_its_third_value",
            touches=[PRED / "host_fns" / "nav_interval.py"],
        )

    def apply(self) -> None:
        p = PRED / "host_fns" / "nav_interval.py"
        p.write_text(p.read_text().replace(
            "        return celtypes.StringType(UNDERSPECIFIED)\n"
            "    return celtypes.StringType(_DETERMINED.get((st, oc), UNKNOWN_COMBINATION))",
            "        return celtypes.StringType(\"P6M\")\n"
            "    return celtypes.StringType(_DETERMINED.get((st, oc), \"P6M\"))"))


class LoaderSkipsQualificationCheck(Injector):
    """`load_predicate` accepts an envelope with no qualification record.

    NC-Q02's injector, which becomes possible at P4 because the schema now exists. Before P4 the
    entry was PROVISIONAL: the admission-side twin — a QUALIFIED predicate that DOES load — could
    not be written, and a green entry with no information in it is not evidence.
    """

    def __init__(self) -> None:
        super().__init__(name="loader_skips_qualification_check", touches=[PRED / "loader.py"])

    def apply(self) -> None:
        p = PRED / "loader.py"
        p.write_text(p.read_text().replace(
            "    missing = [k for k in PREDICATE_KEYS if raw.get(k) is None]",
            "    missing = []  # the admission rule the settled-fraction claim rests on"))


ALL_INJECTORS = ALL_INJECTORS + (
    ProjectionDropsAField, KeysMismatchCollapsed, PermissiveSubsetWalker, LexicalKeyExtraction,
    TotalWithoutDistribution, WeakPileDropped, ClauselessReasonOptional, ClaimsFromKillVector,
    HostFnResolvesLive, HostFnLosesItsThirdValue, LoaderSkipsQualificationCheck,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# The P5 injectors — run assembly, the verdict model, closure, the settled fraction
# --------------------------------------------------------------------------------

VERDICT = REPO_ROOT / "src" / "cdfc" / "verdict"
EVAL = REPO_ROOT / "src" / "cdfc" / "evaluate"


class CellsBoundAfterExpr(Injector):
    """`cells_bound == 0` is checked AFTER `expr`, so the vacuous pass is produced and corrected.

    `all([])` is `True`. A design that lets the PASS exist and then overwrites it is trusting
    itself to overwrite it, and NC-E20 exists because that trust is exactly what fails.
    """

    def __init__(self) -> None:
        super().__init__(name="cells_bound_after_expr", touches=[EVAL / "runner.py"])

    def apply(self) -> None:
        p = EVAL / "runner.py"
        p.write_text(p.read_text().replace(
            "    bound = bind_count(p, schema)\n    if not bound:",
            "    bound = bind_count(p, schema) or ('<deferred>',)\n    if False:"))


class CellsFromEvaluations(Injector):
    """`run_cell` is accumulated from the evaluations instead of materialised from the denominator.

    The table then has exactly as many rows as things that happened, and the cells nothing happened
    to — the ones that matter — are absent. Closure cannot see a hole it was never given.
    """

    def __init__(self) -> None:
        super().__init__(name="cells_from_evaluations", touches=[EVAL / "rollup.py"])

    def apply(self) -> None:
        p = EVAL / "rollup.py"
        p.write_text(p.read_text().replace(
            "        for key in sorted(set(cells))\n    }",
            "        for key in sorted(set(cells))[:1]\n    }"))


class InvalidEmitsZero(Injector):
    """An INVALID run emits `0` for the settled fraction instead of a present `null`."""

    def __init__(self) -> None:
        super().__init__(name="invalid_emits_zero", touches=[VERDICT / "settled_fraction.py"])

    def apply(self) -> None:
        p = VERDICT / "settled_fraction.py"
        p.write_text(p.read_text().replace(
            '    return {"settledFraction": None if sf is None else sf.as_row()}',
            '    return {} if sf is None else {"settledFraction": sf.as_row()}'))


class RunCauseInItemReason(Injector):
    """A run-level `invalid.*` cause is written into an item's reason field.

    The two vocabularies stop being disjoint, and the item-level count is no longer 8 x 30.
    """

    def __init__(self) -> None:
        super().__init__(name="run_cause_in_item_reason", touches=[VERDICT / "invalid.py"])

    def apply(self) -> None:
        # Injected on the RUN-LEVEL side. Changing an ITEM code to an `invalid.*` string breaks
        # the family map at import, so the module never loads and the guards ERROR at collection
        # rather than going red — a break the sweep cannot attribute. This one collides the two
        # vocabularies while leaving both modules importable.
        p = VERDICT / "invalid.py"
        p.write_text(p.read_text().replace(
            '    CANARY_SILENT = "invalid.canary_silent"',
            '    CANARY_SILENT = "error.canary_silent"'))


class ValueDerivedRemoval(Injector):
    """A cell leaves `inScope` for a reason derived from the filing's own VALUES.

    D-P5-05's whole subject: `scope_kind == PREDICATE_PRECONDITION` starts removing cells, so a
    predicate whose `applicable` went degenerate shrinks the denominator it is measured against —
    and a filer who fills in less gets a better settled fraction.
    """

    def __init__(self) -> None:
        super().__init__(name="value_derived_removal", touches=[VERDICT / "states.py"])

    def apply(self) -> None:
        p = VERDICT / "states.py"
        p.write_text(p.read_text().replace(
            "        return scope_kind != LEAVES_IN_SCOPE",
            "        return False"))


class InformationalOnlyLeaves(Injector):
    """An INFORMATIONAL-only cell rolls up to INFORMATIONAL, which LEAVES the denominator.

    Adding a row to `template_defects.yaml` then raises the headline fraction.
    """

    def __init__(self) -> None:
        super().__init__(name="informational_only_leaves", touches=[EVAL / "rollup.py"])

    def apply(self) -> None:
        p = EVAL / "rollup.py"
        p.write_text(p.read_text().replace(
            "    if all(e.state is ItemState.INFORMATIONAL for e in evals):",
            "    if False and all(e.state is ItemState.INFORMATIONAL for e in evals):"))


class ContractTableEdit(Injector):
    """One cell of the GENERATED contract table is hand-edited."""

    def __init__(self) -> None:
        super().__init__(name="contract_table_edit", touches=[REPO_ROOT / "EVALUATION-CONTRACT.md"])

    def apply(self) -> None:
        p = REPO_ROOT / "EVALUATION-CONTRACT.md"
        p.write_text(p.read_text().replace("| 4 | 5 | cells_bound == 0 |", "| 4 | 5 | cells bound is zero |"))


class PreflightDisabled(Injector):
    """Pre-flight is skipped, so `true || <error>` returns PASS over a key nobody checked."""

    def __init__(self) -> None:
        super().__init__(name="preflight_disabled", touches=[EVAL / "runner.py"])

    def apply(self) -> None:
        p = EVAL / "runner.py"
        p.write_text(p.read_text().replace(
            "    pf: PreflightResult = preflight(p, facts)\n    if not pf.proceed:",
            "    pf: PreflightResult = preflight(p, facts)\n    if False:"))


ALL_INJECTORS = ALL_INJECTORS + (
    CellsBoundAfterExpr, CellsFromEvaluations, InvalidEmitsZero, RunCauseInItemReason,
    ValueDerivedRemoval, InformationalOnlyLeaves, ContractTableEdit, PreflightDisabled,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# The P6 injectors — the fault model, surgery, observability, the site universe
# --------------------------------------------------------------------------------

QUALIFY = REPO_ROOT / "src" / "cdfc" / "qualify"
PREDICATES = REPO_ROOT / "src" / "cdfc" / "predicates"


class FaultDigestConstant(Injector):
    """The fault model is version-pinned in NAME ONLY: `model_digest` ignores the operator table.

    A silently edited operator then keeps its `v3` label, and every kill rate ever quoted is
    qualified against a model that no longer exists.
    """

    def __init__(self) -> None:
        super().__init__(name="fault_digest_constant", touches=[QUALIFY / "fault_model.py"])

    def apply(self) -> None:
        p = QUALIFY / "fault_model.py"
        p.write_text(p.read_text().replace(
            "    return sha256_hex(canonical_json(canonical_table(version)))",
            "    return sha256_hex(canonical_json({'version': version}))"))


class MutantViaOpenpyxl(Injector):
    """Mutants written by a re-serialising writer instead of raw-zip surgery.

    The mutant loses 24 parts and 19 `x14` validations, so the observability diff is a diff of THE
    WRITER rather than of the fault, and `U/G` collapses to zero.
    """

    def __init__(self) -> None:
        super().__init__(name="mutant_via_openpyxl", touches=[QUALIFY / "surgery.py"])

    def apply(self) -> None:
        p = QUALIFY / "surgery.py"
        src = p.read_text()
        # The writer REALLY becomes openpyxl. The one-part check has to come out with it, because
        # the check is what would otherwise catch the swap — and an injector that trips the guard
        # it is meant to bypass demonstrates nothing.
        src = src.replace(
            '    out.parent.mkdir(parents=True, exist_ok=True)\n'
            '    with zipfile.ZipFile(out, "w") as w:',
            '    out.parent.mkdir(parents=True, exist_ok=True)\n'
            '    import openpyxl, warnings\n'
            '    with warnings.catch_warnings():\n'
            '        warnings.simplefilter("ignore")\n'
            '        _wb = openpyxl.load_workbook(base)\n'
            '        _wb.save(out)\n'
            '        _wb.close()\n'
            '    with zipfile.ZipFile(out, "a") as w:')
        src = src.replace(
            "    changed = differing_parts(base, out)\n    expected = set(named_parts.values())\n"
            "    if changed != expected:",
            "    changed = differing_parts(base, out)\n    expected = set(named_parts.values())\n"
            "    if False:")
        p.write_text(src)


class ObservabilityCachedGrid(Injector):
    """The filter reads the mutant's CACHED values instead of recalculating.

    A raw-zip edit does not update Excel's cached values, so the filter reports a difference at
    exactly the edited cell and nowhere else — it measures the EDIT, not its PROPAGATION, and
    returns `U = 0` on every campaign.
    """

    def __init__(self) -> None:
        super().__init__(name="observability_cached_grid", touches=[QUALIFY / "observability.py"])

    def apply(self) -> None:
        p = QUALIFY / "observability.py"
        p.write_text(p.read_text().replace(
            "    if cone is None:\n        return recalculate(",
            "    if True:\n        return _cached_grid(blob)\n    if cone is None:\n        return recalculate(",
        ).replace(
            "def grid_of(",
            "def _cached_grid(blob: Path) -> ValueGrid:\n"
            "    ex = extract(blob)\n"
            "    return ValueGrid(values=dict(ex.literals), not_run={},\n"
            "                     computed_cells=frozenset(ex.literals), formula_source='FILING')\n\n\n"
            "def grid_of(", 1))


class NotrunCountsAsIdentical(Injector):
    """F18: `INDETERMINATE_OBSERVABILITY` is folded back into `UNOBSERVABLE`.

    A cell our evaluator could not compute is then banked as evidence that the MUTANT is invisible.
    Those mutants leave `O`, and because `O = G − U − I` the kill rate RISES.
    """

    def __init__(self) -> None:
        super().__init__(name="notrun_counts_as_identical", touches=[QUALIFY / "observability.py"])

    def apply(self) -> None:
        p = QUALIFY / "observability.py"
        p.write_text(p.read_text().replace(
            "    blocked = frozenset(set(clean.not_run) | set(mutant.not_run))\n    if blocked:",
            "    blocked = frozenset(set(clean.not_run) | set(mutant.not_run))\n    if False:"))


class ObservabilityUsesTemplateFormulas(Injector):
    """F19: observability recalculates with the TEMPLATE's formulas.

    An F11 override is then overwritten by the very formula it deleted, the flagship class
    classifies UNOBSERVABLE with `O = 0`, and `TEMPLATE_DIFF` becomes unadmittable at G2.
    """

    def __init__(self) -> None:
        super().__init__(
            name="observability_uses_template_formulas", touches=[QUALIFY / "observability.py"]
        )

    def apply(self) -> None:
        # The REAL break is reading the TEMPLATE's `<f>` elements, not relabelling the argument.
        # The first version only flipped the literal `"FILING"` to `"TEMPLATE"` — and since
        # `grid_of` extracts from the file it is handed, the classification did not change at all.
        # An injector that renames a label demonstrates nothing.
        p = QUALIFY / "observability.py"
        p.write_text(p.read_text().replace(
            "    ex = extract(blob)\n    if cone is None:",
            "    ex = extract(_TEMPLATE_FOR_F19)\n    if cone is None:",
        ).replace(
            "CellRef = tuple[str, str]",
            "CellRef = tuple[str, str]\n_TEMPLATE_FOR_F19 = Path(__file__).resolve().parents[3] / "
            "'fixtures' / 'prescribed' / "
            "'Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx'",
        ).replace('formula_source="FILING"', 'formula_source="TEMPLATE"'))


class DiscardUnobservable(Injector):
    """An unobservable mutant is DESTROYED rather than retained with its reason.

    `U/G` becomes unauditable and P10 loses its residue feedstock.
    """

    def __init__(self) -> None:
        super().__init__(name="discard_unobservable", touches=[QUALIFY / "runner.py"])

    def apply(self) -> None:
        p = QUALIFY / "runner.py"
        p.write_text(p.read_text().replace(
            '        "unobservable.jsonl": [o for o in outcomes if o.observability is Observability.UNOBSERVABLE],',
            '        "unobservable.jsonl": [],'))


class SitesFromReadSet(Injector):
    """Mutation sites sampled from the predicates' read set. v0 scored 100.0% on 3,574 mutants."""

    def __init__(self) -> None:
        super().__init__(name="sites_from_read_set", touches=[QUALIFY / "sites.py"])

    def apply(self) -> None:
        p = QUALIFY / "sites.py"
        p.write_text(p.read_text().replace(
            "def site_universe(\n    field_surface: Iterable[tuple[str, str]] | Iterable[CellKey],\n    *,\n    excluded: Iterable[CellKey] = (),\n) -> frozenset[CellKey]:",
            "def site_universe(\n    field_surface: Iterable[tuple[str, str]] | Iterable[CellKey],\n    read_set: Iterable[CellKey] = (),\n    *,\n    excluded: Iterable[CellKey] = (),\n) -> frozenset[CellKey]:"))


class ControlFromReadSetComplement(Injector):
    """The control arm excludes only the READ SET, not the upstream cone.

    Legitimate propagation is then counted as a spurious fire, the threshold has to be softened to
    a fudge factor, and the fudge factor hides a real flag-everything predicate.
    """

    def __init__(self) -> None:
        super().__init__(name="control_from_read_set_complement", touches=[QUALIFY / "sites.py"])

    def apply(self) -> None:
        p = QUALIFY / "sites.py"
        p.write_text(p.read_text().replace(
            "    cone: set[CellKey] = set(reads)\n    for cell in reads:\n        cone |= upstream.get(cell, frozenset())",
            "    cone: set[CellKey] = set(reads)\n    for cell in reads:\n        pass"))


class ToleranceOnCounts(Injector):
    """`tau(n) = 5n` applied to a COUNT cell. A person is not a rounded quantity."""

    def __init__(self) -> None:
        super().__init__(name="tolerance_on_counts", touches=[QUALIFY / "fault_model.py"])

    def apply(self) -> None:
        p = QUALIFY / "fault_model.py"
        p.write_text(p.read_text().replace(
            '"F06", "round_to_integer", frozenset({MONEY})',
            '"F06", "round_to_integer", frozenset({MONEY, Dtype.COUNT})'))


ALL_INJECTORS = ALL_INJECTORS + (
    FaultDigestConstant, MutantViaOpenpyxl, ObservabilityCachedGrid, NotrunCountsAsIdentical,
    ObservabilityUsesTemplateFormulas, DiscardUnobservable, SitesFromReadSet,
    ControlFromReadSetComplement, ToleranceOnCounts,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class ClosureDropsABucket(Injector):
    """A bucket leaves the seven-term sum, so a cell of the denominator is in no bucket.

    Gate 16's registered broken build. Closure then holds over a smaller total and every fraction
    is a fraction of something nobody enumerated.
    """

    def __init__(self) -> None:
        super().__init__(name="closure_drops_a_bucket", touches=[VERDICT / "closure.py"])

    def apply(self) -> None:
        p = VERDICT / "closure.py"
        p.write_text(p.read_text().replace(
            '    "outOfScope", "informational", "settled", "indeterminate", "notRun", "noPredicate", "error"',
            '    "outOfScope", "informational", "settled", "indeterminate", "notRun", "noPredicate"'))


class ModelClientInVerdictPath(Injector):
    """A model client is imported into the verdict path.

    Gate 14's registered broken build. The headline number would then depend on a sampling
    temperature, and the coverage claim rests on it being re-derivable from the filing's bytes.
    """

    def __init__(self) -> None:
        super().__init__(name="model_client_in_verdict_path", touches=[VERDICT / "closure.py"])

    def apply(self) -> None:
        p = VERDICT / "closure.py"
        p.write_text(p.read_text().replace(
            "from cdfc.verdict.reasons import ReasonCode",
            "import anthropic  # noqa: F401\nfrom cdfc.verdict.reasons import ReasonCode"))


ALL_INJECTORS = ALL_INJECTORS + (ClosureDropsABucket, ModelClientInVerdictPath)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class RenderBareRate(Injector):
    """A published rate loses the two integers of its fraction.

    Gate 37's registered broken build. The v0 harness printed `MS = 18.09%` over a denominator
    nobody could reconstruct, and a later one printed **100.1%** — impossible, and unnoticed
    because a percentage carries no evidence of its own arithmetic.
    """

    def __init__(self) -> None:
        super().__init__(name="render_bare_rate", touches=[QUALIFY / "campaign.py"])

    def apply(self) -> None:
        p = QUALIFY / "campaign.py"
        p.write_text(p.read_text().replace(
            '            f"  U/G = {t.U}/{t.G}   I/G = {t.I}/{t.G}   '
            '(I is OUR EVALUATOR, not the fault model)",',
            '            f"  unobservable {100 * t.U / max(t.G, 1):.1f}%",'))


ALL_INJECTORS = ALL_INJECTORS + (RenderBareRate,)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# --------------------------------------------------------------------------------
# The P7 injectors
# --------------------------------------------------------------------------------


class TextsourceSingleExtraction(Injector):
    """The disputed-region exclusion is dropped and the FIRST extraction is used alone.

    NC-Q47. A span then resolves against text the second extractor never saw, and every unit
    reports itself uncorroborated-but-addressable — which is what an instrument built from one
    reading always looks like from the inside. The build's own refusal of a single extraction is
    the thing being defeated, so the injector defeats it directly rather than passing one party.
    """

    def __init__(self) -> None:
        super().__init__(name="textsource_single_extraction", touches=[QUALIFY / "textsource.py"])

    def apply(self) -> None:
        p = QUALIFY / "textsource.py"
        p.write_text(p.read_text().replace(
            "    if len(extractions) < 2:\n"
            "        raise TextSourceError(",
            "    extractions = list(extractions)[:1]\n"
            "    if len(extractions) < 1:\n"
            "        raise TextSourceError(", 1))


ALL_INJECTORS = ALL_INJECTORS + (TextsourceSingleExtraction,)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class ProvisoMarkersEmpty(Injector):
    """The proviso detector's marker list is emptied.

    NC-Q35. G0 then reports `provisos_total == 0` for every candidate and passes everything —
    **scope truncation applied to the gate that exists to catch scope truncation.**
    """

    def __init__(self) -> None:
        super().__init__(name="proviso_markers_empty", touches=[QUALIFY / "provisos.py"])

    def apply(self) -> None:
        p = QUALIFY / "provisos.py"
        p.write_text(p.read_text().replace(
            "_COMPILED: Final[tuple[tuple[re.Pattern[str], Marker], ...]] = tuple(\n"
            "    (re.compile(m.pattern, re.IGNORECASE), m) for m in MARKERS\n"
            ")",
            "_COMPILED: Final[tuple[tuple[re.Pattern[str], Marker], ...]] = ()", 1))


class G1IgnoresUnresolved(Injector):
    """G1 admits a predicate whose declared key is UNRESOLVED.

    NC-Q39. A version bump then silently rebinds it to a different row of the same table, and the
    predicate goes on reporting a clean pass about a cell nobody meant.
    """

    def __init__(self) -> None:
        super().__init__(name="g1_ignores_unresolved", touches=[QUALIFY / "g1_binds.py"])

    def apply(self) -> None:
        p = QUALIFY / "g1_binds.py"
        p.write_text(p.read_text().replace(
            "    unresolved = sorted(k for k in cand.schema_keys if _is_unresolved(schema, k))",
            "    unresolved = []  # INJECTED", 1))


class G1IgnoresZeroBind(Injector):
    """G1 admits a predicate that binds zero cells.

    NC-Q01. `all([])` is True, so the predicate returns a clean pass over nothing at all and the
    settled fraction counts it for free. This is the vacuous pass in its purest form.
    """

    def __init__(self) -> None:
        super().__init__(name="g1_ignores_zero_bind", touches=[QUALIFY / "g1_binds.py"])

    def apply(self) -> None:
        p = QUALIFY / "g1_binds.py"
        p.write_text(p.read_text().replace(
            "    if not cells:\n"
            "        return reject(Reason.CELLS_BOUND_ZERO, cells_bound=0)",
            "    if False:  # INJECTED\n"
            "        return reject(Reason.CELLS_BOUND_ZERO, cells_bound=0)", 1))


class G0SkipsProvisos(Injector):
    """G0 stops asking whether a detected proviso was disposed of.

    NC-Q11. Frontier models ground clause spans well and wire exception structure badly, and the
    EMPIRICAL gates cannot see a dropped proviso: a predicate that silently ignores an exception
    still kills mutants and still fires on nothing clean.
    """

    def __init__(self) -> None:
        super().__init__(name="g0_skips_provisos", touches=[QUALIFY / "g0_scope.py"])

    def apply(self) -> None:
        p = QUALIFY / "g0_scope.py"
        p.write_text(p.read_text().replace(
            "    uncovered = [d for d in provisos if not any(d.text in (p.text or \"\") for p in recorded)]",
            "    uncovered = []  # INJECTED", 1))


class G0SkipsClauseless(Injector):
    """G0 returns a passing outcome, computing nothing, for a candidate with no clause.

    NC-Q51 (the plan's NC-Q48, renumbered — that id has been taken since P4). Stage one of the
    funnel then reads `N -> N`, **a constant wearing the shape of a measurement**, and a gate stage
    that cannot fail is this product's own failure mode wearing a gate's clothes.
    """

    def __init__(self) -> None:
        super().__init__(name="g0_skips_clauseless", touches=[QUALIFY / "g0_scope.py"])

    def apply(self) -> None:
        p = QUALIFY / "g0_scope.py"
        p.write_text(p.read_text().replace(
            "    # --- 1. the span must be addressable at all "
            "-------------------------------------------",
            "    if getattr(cand, 'clause', None) is None:  # INJECTED\n"
            "        return GateOutcome(gate=GateId.G0, passed=True, measured={})\n"
            "    # --- 1. the span must be addressable at all "
            "-------------------------------------------", 1))


ALL_INJECTORS = ALL_INJECTORS + (
    ProvisoMarkersEmpty, G1IgnoresUnresolved, G1IgnoresZeroBind, G0SkipsProvisos, G0SkipsClauseless,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class GateOrderShuffled(Injector):
    """`GATE_ORDER` is reversed, so the expensive gate runs before the free one.

    NC-Q34. The OUTCOME is usually the same; the COST is not. A candidate that fails G0's free
    structural check would consume a whole mutation campaign, and worse, a candidate Z3 would have
    proved degenerate is admitted on an expensive number instead of refused on a free one.
    """

    def __init__(self) -> None:
        super().__init__(name="gate_order_shuffled", touches=[QUALIFY / "result.py"])

    def apply(self) -> None:
        p = QUALIFY / "result.py"
        p.write_text(p.read_text().replace(
            "GATE_ORDER: Final[tuple[GateId, ...]] = (\n"
            "    GateId.G0,\n    GateId.G1,\n    GateId.G3P,\n    GateId.G2,\n"
            "    GateId.G3E,\n    GateId.G4,\n)",
            "GATE_ORDER: Final[tuple[GateId, ...]] = (\n"
            "    GateId.G4,\n    GateId.G3E,\n    GateId.G2,\n    GateId.G3P,\n"
            "    GateId.G1,\n    GateId.G0,\n)", 1))


class MerkleNoDomainSep(Injector):
    """The Merkle leaf and internal prefixes are dropped.

    NC-Q38. Two different admitted sets can then be made to share a root, and the attestation's
    `registryRoot` stops identifying what ran.
    """

    def __init__(self) -> None:
        super().__init__(name="merkle_no_domain_sep", touches=[PREDICATES / "registry.py"])

    def apply(self) -> None:
        p = PREDICATES / "registry.py"
        s = p.read_text()
        s = s.replace('LEAF_PREFIX: Final[bytes] = b"\\x00"', 'LEAF_PREFIX: Final[bytes] = b""')
        s = s.replace('INTERNAL_PREFIX: Final[bytes] = b"\\x01"', 'INTERNAL_PREFIX: Final[bytes] = b""')
        p.write_text(s)


class AdmitAutosign(Injector):
    """`admit()` fills in a signer instead of refusing.

    NC-Q55. R7 exists because the gate is mechanical and shipping a check that will be applied to a
    regulated filing is not.
    """

    def __init__(self) -> None:
        super().__init__(name="admit_autosign", touches=[PREDICATES / "registry.py"])

    def apply(self) -> None:
        p = PREDICATES / "registry.py"
        p.write_text(p.read_text().replace(
            "        if signer != UNSIGNED and not signature:",
            "        signature = signature or b'auto'  # INJECTED\n"
            "        if signer != UNSIGNED and not signature:", 1))


class IlpSilentRemoval(Injector):
    """The ILP drops a subsumed predicate without recording the removal.

    NC-Q36. The predicate vanishes from the registry and the settled fraction moves with no cause
    on the chart.
    """

    def __init__(self) -> None:
        super().__init__(name="ilp_silent_removal", touches=[QUALIFY / "ilp.py"])

    def apply(self) -> None:
        p = QUALIFY / "ilp.py"
        p.write_text(p.read_text().replace(
            "        removals=tuple(\n"
            "            Removal(removed=k, subsumed_by=v, cells_would_have_covered=cells_of.get(k, 0))\n"
            "            for k, v in sorted(removed.items())\n"
            "        ),",
            "        removals=(),  # INJECTED", 1))


class Z3UnknownIsOk(Injector):
    """`unknown` from the proof arm is read as `non_degenerate`.

    NC-Q07. A degenerate or always-flagging predicate then passes the proof arm because nobody
    could decide it — UNPROVEN read as PROVED, which is this project's subject matter inside its
    own degeneracy gate.
    """

    def __init__(self) -> None:
        super().__init__(name="z3_unknown_is_ok", touches=[QUALIFY / "g3_degeneracy.py"])

    def apply(self) -> None:
        p = QUALIFY / "g3_degeneracy.py"
        p.write_text(p.read_text().replace(
            '             "proved": verdict is DegeneracyVerdict.NON_DEGENERATE, **over}',
            '             "proved": verdict in (DegeneracyVerdict.NON_DEGENERATE,\n'
            '                                   DegeneracyVerdict.UNKNOWN), **over}', 1))


ALL_INJECTORS = ALL_INJECTORS + (
    GateOrderShuffled, MerkleNoDomainSep, AdmitAutosign, IlpSilentRemoval, Z3UnknownIsOk,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


CORPUS = REPO_ROOT / "src" / "cdfc" / "qualify" / "corpus"


class TcLicensesArithmetic(Injector):
    """`independent()` ignores conjunct (1), so `TEMPLATE-COMPUTED` licenses an arithmetic FFR.

    NC-Q58 / **F2**. The identity predicates then draw a zero false-failure rate from cells
    `src/cdfc/calc/` wrote, and `n = 189` buys `BLOCKING` in an afternoon.
    """

    def __init__(self) -> None:
        super().__init__(name="tc_licenses_arithmetic", touches=[QUALIFY / "g4_ffr.py"])

    def apply(self) -> None:
        p = QUALIFY / "g4_ffr.py"
        p.write_text(p.read_text().replace(
            "    overlap = sorted(read_cells(cand, schema) & corpus.computed_cells)",
            "    overlap = []  # INJECTED", 1))


class IndependenceHardcoded(Injector):
    """Independence is hand-set back to `true` instead of recomputed at load.

    NC-Q59 / **F5**. The field returns to being a string in a file that nothing computes — which is
    what it was before this build, when no build computed it, no test asserted it, no negative
    control broke and no gate read it.
    """

    def __init__(self) -> None:
        super().__init__(name="independence_hardcoded", touches=[QUALIFY / "g4_ffr.py"])

    def apply(self) -> None:
        p = QUALIFY / "g4_ffr.py"
        p.write_text(p.read_text().replace(
            "    recomputed = independent(corpus, cand, schema).independent",
            "    recomputed = record['clean_corpus_independent_of_predicate']  # INJECTED", 1))


class WilsonFloat(Injector):
    """The Wilson bound is computed in `float` via `math.sqrt`.

    NC-Q56. Two machines then produce two 6-dp strings and the attestation stops re-deriving.
    """

    def __init__(self) -> None:
        super().__init__(name="wilson_float", touches=[QUALIFY / "wilson.py"])

    def apply(self) -> None:
        p = QUALIFY / "wilson.py"
        s = p.read_text()
        s = s.replace("from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext",
                      "import math\nfrom decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext")
        s = s.replace("half = (z * radicand.sqrt()) / denom",
                      "half = (z * Decimal(repr(math.sqrt(float(radicand))))) / denom")
        p.write_text(s)


class SetFfrIsMean(Injector):
    """The set-level FFR is implemented as a MEAN instead of `at least one member fires`.

    NC-Q10. The registry then drifts to flag-everything one admission at a time: in two of SPADE's
    nine pipelines, sets whose every member individually met the constraint reached composite FFRs
    a mean could never have shown.
    """

    def __init__(self) -> None:
        super().__init__(name="set_ffr_is_mean", touches=[QUALIFY / "set_ffr.py"])

    def apply(self) -> None:
        p = QUALIFY / "set_ffr.py"
        p.write_text(p.read_text().replace(
            "    union: set[str] = set()\n"
            "    for m in members:\n"
            "        union |= fires.of(m)\n"
            "    return Fraction(len(union), fires.n)",
            "    if not members:  # INJECTED — the mean\n"
            "        return Fraction(0, 1)\n"
            "    return sum((Fraction(len(fires.of(m)), fires.n) for m in members),\n"
            "               Fraction(0, 1)) / len(members)", 1))


class SeverityPointEstimate(Injector):
    """Severity keyed on the POINT ESTIMATE instead of the Wilson upper bound.

    NC-Q09. `0 fires / 4 filings` then has a point estimate of `0.000` and buys `BLOCKING`.
    """

    def __init__(self) -> None:
        super().__init__(name="severity_point_estimate", touches=[QUALIFY / "severity.py"])

    def apply(self) -> None:
        p = QUALIFY / "severity.py"
        p.write_text(p.read_text().replace(
            '    hi = Decimal(str(g4["wilson"][1]))',
            '    hi = Decimal(str(g4["wilson"][0]))  # INJECTED — the LOWER bound stands in for the\n'
            '                                        # point estimate; both are 0.000 at zero fires', 1))


class SyntheticBuysBlocking(Injector):
    """The `n_non_synthetic` floor is removed, so a corpus the product generated buys `BLOCKING`.

    NC-Q60b / **F2's second half**. `synthesise(..., n=189)` is one command and one afternoon.
    """

    def __init__(self) -> None:
        super().__init__(name="synthetic_buys_blocking", touches=[QUALIFY / "severity.py"])

    def apply(self) -> None:
        p = QUALIFY / "severity.py"
        p.write_text(p.read_text().replace(
            "    if hi <= BLOCKING_MAX and n_ns < BLOCKING_MIN_NON_SYNTHETIC:",
            "    if False:  # INJECTED", 1))


ALL_INJECTORS = ALL_INJECTORS + (
    TcLicensesArithmetic, IndependenceHardcoded, WilsonFloat, SetFfrIsMean,
    SeverityPointEstimate, SyntheticBuysBlocking,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class MixedColumnProceeds(Injector):
    """A repeated node whose element types DISAGREE is waved through pre-flight.

    NC-Q65. `type_of` reports a mixture as `MIXED`; the injector puts it back to `None`, which
    pre-flight reads as *"the fact side cannot decide either; still presence only"* and PROCEEDS.
    A blind-filled return whose column held 45 numbers and 125 numeric strings then reached the CEL
    runtime, where `c.v >= 0` is a type error on 125 of 170 elements — and evaluating that ONE
    predicate took the process from 85 MB to **6 GB without returning**, with a 2,000-step budget
    unable to stop it because the step meter only ticks on fact-tree access.
    """

    def __init__(self) -> None:
        super().__init__(name="mixed_column_proceeds", touches=[REPO_ROOT / "src/cdfc/facts/view.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/facts/view.py"
        p.write_text(p.read_text().replace(
            '        # NOT None. `None` means *nobody can tell*; this is *we can tell, and they disagree*.\n'
            '        return "MIXED"',
            "        return None  # INJECTED", 1))


ALL_INJECTORS = ALL_INJECTORS + (MixedColumnProceeds,)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# ---------------------------------------------------------------------------------------
# P9 — the probe layer. Each injector breaks ONE rule of the relation layer, and each leaves
# every other guard in the system silent: that is what makes the control a control rather than
# a demonstration that something somewhere is broken.
# ---------------------------------------------------------------------------------------


class RelationNoPrecondition(Injector):
    """NC-R01. `applicable()` is bypassed, so a relation returns PASS on a filing that satisfies
    it only because the filing is EMPTY.

    The blank's own cached grid is essentially zeros and `"NA"` strings — `'1. Introduction'!D17`,
    `D18`, `D19`, `D20` all cache `0`; `C92`, `D92`, `E92` all cache `"NA"` (MEASURED). Without the
    precondition an unfilled filing scores a clean sweep through the flagship's door.
    """

    def __init__(self) -> None:
        super().__init__(name="relation_no_precondition",
                         touches=[REPO_ROOT / "src/cdfc/probes/template_diff.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/template_diff.py"
        p.write_text(p.read_text().replace(
            "        scope = applicable(filed, cell, pm)",
            '        scope = "IN_SCOPE"  # INJECTED', 1))


class TdBindsTheFormulaCell(Injector):
    """NC-R02. A `TEMPLATE_DIFF` finding binds the FORMULA CELL, which is not in the field
    surface — 497 of FME's 505 formula cells are locked, therefore outside the 3,747-cell
    denominator. The numerator would then be choosing its own denominator."""

    def __init__(self) -> None:
        super().__init__(name="td_binds_the_formula_cell",
                         touches=[REPO_ROOT / "src/cdfc/probes/template_diff.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/template_diff.py"
        p.write_text(p.read_text().replace(
            "        bound = pm.in_field_surface.get(cell, frozenset())",
            "        bound = frozenset({cell})  # INJECTED", 1))


class RelationWithoutQualification(Injector):
    """NC-R03. The envelope adapter admits a relation whose expression the CEL subset cannot
    parse, so the flagship would be routed to the gates with no declarable read set and its
    demonstration output would become an admission."""

    def __init__(self) -> None:
        super().__init__(name="relation_without_qualification",
                         touches=[REPO_ROOT / "src/cdfc/probes/qualify.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/qualify.py"
        p.write_text(p.read_text().replace(
            '    if spec.expr_language != "CEL":',
            "    if False:  # INJECTED", 1))


class DefectTableIgnored(Injector):
    """NC-R04. `template_defects.yaml` is read and discarded, so the regulator's own defect at
    `'1. Introduction'!D17` — four COUNTIF patterns matching seven of the nine scheme types in
    `Dropdown!F3:F11` — is reported as the FILER's failure."""

    def __init__(self) -> None:
        super().__init__(name="defect_table_ignored",
                         touches=[REPO_ROOT / "src/cdfc/probes/template_diff.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/template_diff.py"
        p.write_text(p.read_text().replace(
            "    declared = defects.for_template(pm.template_sha256).by_cell",
            "    declared = {}  # INJECTED", 1))


class DefectMovesASoleEvaluationOutOfScope(Injector):
    """NC-R10. The F14 fallback is removed, so a declared defect on a cell with no other binding
    evaluation emits `INFORMATIONAL` — which LEAVES the denominator, so `fraction = s/(i-1) >
    s/i`. **Adding a row to the defect table would raise the headline.**"""

    def __init__(self) -> None:
        super().__init__(name="defect_moves_a_sole_evaluation_out_of_scope",
                         touches=[REPO_ROOT / "src/cdfc/probes/template_diff.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/template_diff.py"
        p.write_text(p.read_text().replace(
            "            sole = frozenset(bound) - otherwise_bound",
            "            sole = frozenset()  # INJECTED", 1))


class BasisGuardDisabled(Injector):
    """NC-R05. A relation drafted across two accounting bases is admitted. `'3. Portfolio'!A130`
    puts Table 3.5 on a non-look-through basis and Table 3.6 on a look-through one, so such a
    relation adds two different measurements of the same money and reports the difference as the
    filer's error — a false alarm on a CORRECT filing."""

    def __init__(self) -> None:
        super().__init__(name="basis_guard_disabled",
                         touches=[REPO_ROOT / "src/cdfc/probes/relations/registry.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/relations/registry.py"
        p.write_text(p.read_text().replace(
            "    if len(bases) != 1:",
            "    if False:  # INJECTED", 1))


class ProbeSeedFromEntropy(Injector):
    """NC-R06. The probe search draws its seed from entropy, so the report cannot be
    re-derived. A search with an unpinned seed makes `verify` unable to reproduce a probe result
    at all."""

    def __init__(self) -> None:
        super().__init__(name="probe_seed_from_entropy",
                         touches=[REPO_ROOT / "src/cdfc/probes/driver.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/driver.py"
        p.write_text(p.read_text().replace(
            'DEFAULT_SEED: Final[int] = 0',
            "import os as _os  # INJECTED\nDEFAULT_SEED: Final[int] = int.from_bytes(_os.urandom(2))", 1))


class SubsumptionCheckDisabled(Injector):
    """NC-R07. The redundancy check at protocol step 6 is removed, so R-04 — vocabulary closure,
    which `P-0017` already asserts from the blank — would be admitted and the before/after delta
    would count the same cell twice under a new name."""

    def __init__(self) -> None:
        super().__init__(name="subsumption_check_disabled",
                         touches=[REPO_ROOT / "src/cdfc/probes/relations/catalogue.yaml"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/relations/catalogue.yaml"
        p.write_text(p.read_text() + (
            "\n  - id: R-04\n"
            "    title: Vocabulary closure under the pinned blank (INJECTED — refused at step 6)\n"
            "    necessity: NECESSARY\n"
            "    inputs: FILING_AND_BLANK\n"
            "    bases: [INVESTOR_SIDE]\n"
            "    precondition: 'has(filing.n_1_introduction.r54.cg.v)'\n"
            "    expr: 'filing.n_1_introduction.r54.cg.v in template.vocab.n_1_introduction_g54'\n"
            "    witness: '[filing.n_1_introduction.r54.cg.__cell__]'\n"
            "    evidence: Dropdown is hidden and unprotected\n"
            "    claims_fault_classes: [F09]\n"
            "    reviewed_by: [injected]\n"
            "    reviewed_at: 2026-08-14\n"
            "    review_label: SINGLE-SIGNER — a weaker review\n"
        ))


class DegenerateScopeLeavesTheDenominator(Injector):
    """NC-R09. `applicable()` returns `DECLARED_CHARACTERISTIC` for a degenerate precondition, so
    a cell that is out of scope because THIS FILER left its inputs empty LEAVES the in-scope
    denominator — and a filer who fills in less gets a better settled fraction."""

    def __init__(self) -> None:
        super().__init__(name="degenerate_scope_leaves_the_denominator",
                         touches=[REPO_ROOT / "src/cdfc/probes/template_diff.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/probes/template_diff.py"
        p.write_text(p.read_text().replace(
            '    return "PREDICATE_PRECONDITION"',
            '    return "DECLARED_CHARACTERISTIC"  # INJECTED', 1))


class ToleranceUnitsSilentlyReconciled(Injector):
    """NC-R12. The measured, still-open unit defect is 'repaired' on ONE side only: the harvested
    `τ` literals are divided by 1,000 while the fact tree stays unscaled, or the reverse. Either
    half alone is the same defect with the sign flipped, and the guard exists so that a partial
    repair cannot land quietly."""

    def __init__(self) -> None:
        super().__init__(name="tolerance_units_silently_reconciled",
                         touches=[REPO_ROOT / "src/cdfc/facts/units.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/facts/units.py"
        p.write_text(p.read_text().replace(
            "HALF_ULP: Final[int] = 5",
            "HALF_ULP: Final[int] = 0  # INJECTED", 1))


ALL_INJECTORS = ALL_INJECTORS + (
    RelationNoPrecondition, TdBindsTheFormulaCell, RelationWithoutQualification,
    DefectTableIgnored, DefectMovesASoleEvaluationOutOfScope, BasisGuardDisabled,
    ProbeSeedFromEntropy, SubsumptionCheckDisabled, DegenerateScopeLeavesTheDenominator,
    ToleranceUnitsSilentlyReconciled,
)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


# ---------------------------------------------------------------------------------------
# THE THREE GATES WHOSE PUBLISHED RED OBSERVATION WAS BOUND TO AN UNRELATED BREAK.
#
# `tools/gate_liveness.py` now RUNS a shell gate under its bound injector and requires a non-zero
# exit, so a binding that never demonstrated anything reports `BINDING NOT VERIFIED` instead of
# being counted. These three injectors plant each gate's OWN subject.
# ---------------------------------------------------------------------------------------


class RegexOverOoxml(Injector):
    """A pattern is used to read an OOXML cell element instead of the one parser factory.

    `ci/no-regex-over-xml.sh` exists because this shape has appeared three times in this
    repository — most recently in P7-B3's own baselines, written by the author of the gate that
    bans it. Its registry row was published OBSERVED RED on `ContractTableEdit`, which hand-edits
    a markdown table and leaves the gate green.
    """

    def __init__(self) -> None:
        super().__init__(name="regex_over_ooxml",
                         touches=[REPO_ROOT / "src/cdfc/schema/styles_mask.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/schema/styles_mask.py"
        p.write_text(p.read_text() + (
            "\n\ndef _cells_by_pattern(xml: str):  # INJECTED\n"
            '    import re\n'
            '    return re.findall(r\'<c r="([A-Z]+[0-9]+)"\', xml)\n'
        ))


class WallclockZ3(Injector):
    """The proof arm is driven by a wall clock instead of `rlimit`.

    A timeout makes a proof verdict a function of how busy the machine was, so `unknown` — which
    this build treats as UNPROVEN — starts depending on load rather than on the formula. Registry
    row 48 was published OBSERVED RED on `Z3UnknownIsOk`, which changes how `unknown` is READ and
    leaves the wall-clock gate green.
    """

    def __init__(self) -> None:
        super().__init__(name="wallclock_z3",
                         touches=[REPO_ROOT / "src/cdfc/qualify/g3_degeneracy.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/qualify/g3_degeneracy.py"
        t = p.read_text()
        marker = "\n\ndef "
        i = t.index(marker)
        p.write_text(t[:i] + (
            "\n\ndef _deadline(s):  # INJECTED\n"
            '    s.set("timeout", 5000)\n'
        ) + t[i:])


# NC-CI01's break — *"a grep over a missing directory exits 0 and reports success"* — is planted
# by `RemoveScanRoot`, which existed UNUSED by any catalogue entry while NC-CI01 was bound to
# `DefeatBareExceptGate`, an injector for a different gate. It is not re-implemented here: it
# already handles the directory restore that a naive subclass gets wrong (it removes every file
# under the root and re-creates the directory before restoring, because a `touches` list of files
# cannot restore a directory that no longer exists).

ALL_INJECTORS = ALL_INJECTORS + (RegexOverOoxml, WallclockZ3)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}


class WallClockInCore(Injector):
    """A wall clock in the deterministic core. `ci/no-clock-in-core.sh`'s pattern listed only the
    MONOTONIC clocks, so `time.time()` — the one a person reaches for when STAMPING something,
    and the one that makes a hashed payload non-reproducible — went straight past it."""

    def __init__(self) -> None:
        super().__init__(name="wall_clock_in_core",
                         touches=[REPO_ROOT / "src/cdfc/verdict/closure.py"])

    def apply(self) -> None:
        p = REPO_ROOT / "src/cdfc/verdict/closure.py"
        p.write_text(p.read_text() + "\n\nimport time  # INJECTED\n\n\ndef _stamp():\n    return time.time()\n")


class BareAbsenceOnASurface(Injector):
    """An absence claim with no `ledger:<row_id>` citation. The gate exists because an absence
    reported by an instrument nobody proved could see a presence is a broken query with a
    confident face."""

    def __init__(self) -> None:
        super().__init__(name="bare_absence_on_a_surface",
                         touches=[REPO_ROOT / "docs/HARVEST-DELTA.md"])

    def apply(self) -> None:
        p = REPO_ROOT / "docs/HARVEST-DELTA.md"
        p.write_text(p.read_text() + "\n\nThe construct does not occur in the corpus.\n")


ALL_INJECTORS = ALL_INJECTORS + (WallClockInCore, BareAbsenceOnASurface)
BY_NAME = {c.__name__: c for c in ALL_INJECTORS}
