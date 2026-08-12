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
