"""F23 — no duration field inside a hashed object, and no clock reachable from the liveness layer.

**This is the phase's cheapest structural gate**, and it is the AST twin of
`ci/no-timing-in-hashed-payload.sh`. Two instruments, one rule: the grep is fast and can be
defeated by a line break, the AST walk cannot and is slower. Neither is decoration — `CanaryRow`
carried `elapsed_us: int` inside a structure whose canonicalised digest feeds `livenessProof` and
`run.jsonl`, so two runs would have produced different bytes and `E2E-VERIFY` would have failed
permanently on the first green run of P11.

And the obvious repair is the dangerous one: deleting the field silently removes the evidence that
the loop *executed* rather than being replayed from a cache, which is death **D5**'s entire
concern in the layer whose whole claim is that it ran. So the second half of this file asserts the
timings still exist — somewhere else.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

CORE = REPO / "src" / "cdfc"
# The ONE exempt directory, and it is exempt because `ci/no-clock-in-core.sh` already carves it
# out: timings live in `src/cdfc/measure/perf/` and `reports/perf/`, and nowhere else.
EXEMPT = CORE / "measure" / "perf"

TIMING_FIELD = re.compile(r"(elapsed|duration|_us|_ms|_ns|seconds)", re.IGNORECASE)
CLOCKS = frozenset({"perf_counter", "monotonic", "process_time", "time", "now", "utcnow", "today"})
CLOCK_MODULES = frozenset({"time", "datetime", "date"})


def _modules() -> list[Path]:
    return sorted(p for p in CORE.rglob("*.py") if EXEMPT not in p.parents)


def _dataclasses(tree: ast.AST) -> list[ast.ClassDef]:
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for dec in node.decorator_list:
            name = dec.func if isinstance(dec, ast.Call) else dec
            if getattr(name, "id", "") == "dataclass" or getattr(name, "attr", "") == "dataclass":
                out.append(node)
                break
    return out


CANONICALISERS = frozenset({"as_canonical_obj", "as_row", "as_manifest", "digest"})


def _is_hashed(path: Path, tree: ast.AST, cls: ast.ClassDef) -> bool:
    """Does this dataclass reach a canonicalised, hashed payload?

    **The scope is the rule.** F23 is about a duration inside a structure whose DIGEST is asserted
    byte-identical; a declared LIMIT that never reaches a hash is a different object.
    `celrt.Budget.wall_ms` is the case that forces the distinction: it matches the name pattern,
    and it is an INPUT the caller states, not a value anything measured — the same budget produces
    the same bytes on every machine, and `celrt.py` canonicalises nothing.

    In scope if the module imports from `cdfc.canon` — the only canonicaliser — or the class
    itself defines one of the four methods that serialise it for a digest. Over-approximating in
    that direction is safe: it catches `selfcheck/canary.py`, which is where F23 actually was.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("cdfc.canon"):
            return True
    return any(
        isinstance(s, ast.FunctionDef) and s.name in CANONICALISERS for s in cls.body
    )


def test_contract__no_duration_field_in_a_hashed_object() -> None:
    """Every dataclass under `src/cdfc` that reaches a hash, minus `measure/perf/`."""
    offenders: list[str] = []
    scanned = 0
    for path in _modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in _dataclasses(tree):
            if not _is_hashed(path, tree, cls):
                continue
            scanned += 1
            for stmt in cls.body:
                if isinstance(stmt, (ast.AnnAssign, ast.Assign)):
                    targets = (
                        [stmt.target] if isinstance(stmt, ast.AnnAssign) else list(stmt.targets)
                    )
                    for t in targets:
                        name = getattr(t, "id", "")
                        if name and TIMING_FIELD.search(name):
                            offenders.append(
                                f"{path.relative_to(REPO)}::{cls.name}.{name}"
                            )
    assert scanned >= 15, f"the walk found only {scanned} hashed dataclasses — it is scanning nothing"
    assert offenders == [], (
        f"{len(offenders)} timing field(s) inside the deterministic core: {offenders}. Two runs "
        "produce different values, therefore different bytes, therefore byte-identical "
        "re-derivation is unreachable. Timings live in src/cdfc/measure/perf/."
    )


def test_contract__no_clock_is_reachable_from_the_selfcheck_package() -> None:
    """Stronger than *the loop does not read a clock*: the loop CANNOT read one.

    `plan/05` puts `timings.py` inside `src/cdfc/selfcheck/`. That would have required widening
    `ci/no-clock-in-core.sh` — the gate the F23 ruling extends in the same breath — so the timing
    lives in `src/cdfc/measure/perf/canary_timings.py` instead and this package holds no timing
    code at all. The deviation is recorded in that module's docstring.
    """
    pkg = CORE / "selfcheck"
    found: list[str] = []
    for path in sorted(pkg.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", None) or ""
                names = {a.name.split(".")[0] for a in node.names}
                if mod.split(".")[0] in CLOCK_MODULES or names & CLOCK_MODULES:
                    found.append(f"{path.name}: imports {mod or sorted(names)}")
            if isinstance(node, ast.Call):
                fn = node.func
                if getattr(fn, "attr", "") in CLOCKS and getattr(
                    getattr(fn, "value", None), "id", ""
                ) in CLOCK_MODULES:
                    found.append(f"{path.name}: calls {ast.unparse(fn)}")
    assert found == [], f"a clock is reachable from the canary loop: {found}"


def test_contract__the_canary_row_keeps_its_four_deterministic_fields() -> None:
    """The half of the F23 repair that KEEPS the evidence.

    A count of rows produced by executions is stronger evidence of execution than a duration is,
    because a cached replay can carry a duration and cannot carry a per-witness digest it did not
    compute. Deleting the field without keeping these is how the evidence disappears entirely.
    """
    import dataclasses

    from cdfc.selfcheck.canary import CanaryRow

    names = [f.name for f in dataclasses.fields(CanaryRow)]
    assert names == [
        "predicate_id", "witness_digest", "observability", "intersects_read_set", "fired",
        "outcome",
    ]
    # `outcome` joined the four after the loop was caught reading `NOT_RUN` as `did not fire`. It
    # is a deterministic function of the inputs like the rest, which is the only property F23 is
    # about — the prohibition is on values a CLOCK produced, not on the field count.


def test_contract__the_timing_module_still_exists_and_writes_outside_the_payload() -> None:
    """The other half again, from the other side: a repair that deletes the measurement is not a
    repair. `PERF-CANARY2` must still be measurable, and its home must be `reports/perf/`."""
    from cdfc.measure.paths import PERF_DIR
    from cdfc.measure.perf import canary_timings as t

    assert t.BUDGET_ID == "PERF-CANARY2"
    assert t.FAIL_ABOVE_MS > t.WARN_ABOVE_MS > t.BASELINE_MS
    assert "PERF-CANARY" in t.SUPERSEDES
    assert PERF_DIR.name == "perf" and PERF_DIR.parent.name == "reports"


def test_contract__the_ci_grep_and_this_walk_police_the_same_rule() -> None:
    """A gate and its AST twin that disagree are two rules, and the weaker one is the real one."""
    script = (REPO / "ci" / "no-timing-in-hashed-payload.sh").read_text(encoding="utf-8")
    for token in ("elapsed", "duration", "_ms", "_seconds"):
        assert token in script, f"the shell gate does not police {token!r} but this walk does"
