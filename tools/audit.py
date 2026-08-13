#!/usr/bin/env python
"""The audit sweeps of `docs/AUDIT-P0-P6.md`, re-runnable.

An audit that cannot be re-run is a snapshot. These are the mechanical checks; the reading is in
the document. `make audit` runs them and exits non-zero on any finding that has a fix.

    make audit
"""

from __future__ import annotations

import ast
import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

FINDINGS: list[str] = []
NOTES: list[str] = []


def section(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def unconditional_assertions() -> None:
    """`assert ... or True` and `assert <truthy constant>` are assertions that cannot fail."""
    section("1. TESTS THAT CANNOT FAIL")
    bad = []
    for f in sorted(REPO.glob("tests/**/*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue
            t = node.test
            if isinstance(t, ast.Constant) and t.value:
                bad.append(f"{f.relative_to(REPO)}:{node.lineno}: assert <constant truthy>")
            if isinstance(t, ast.BoolOp) and isinstance(t.op, ast.Or) and any(
                isinstance(v, ast.Constant) and v.value for v in t.values
            ):
                bad.append(f"{f.relative_to(REPO)}:{node.lineno}: assert ... or <truthy>")
    print(f"  {len(bad)} unconditional assertion(s)")
    for b in bad:
        print(f"      {b}")
    FINDINGS.extend(bad)


def gates_named_but_absent() -> None:
    """A gate named in a comment is not a gate. This one cost two live defects."""
    section("2. GATES NAMED IN A COMMENT BUT NOT PRESENT")
    named: set[str] = set()
    for f in list(REPO.glob("ci/*.sh")) + list(REPO.glob("src/**/*.py")):
        named |= set(re.findall(r"ci/[a-z0-9-]+\.sh", f.read_text(encoding="utf-8", errors="replace")))
    missing = sorted(n for n in named if not (REPO / n).is_file())
    print(f"  {len(missing)} named gate(s) do not exist")
    for m in missing:
        print(f"      {m}")
    FINDINGS.extend(f"gate named but absent: {m}" for m in missing)


def pending_with_a_shipped_subject() -> None:
    """`PENDING` is the state that lets a gate avoid demonstration."""
    section("3. PENDING GATES WHOSE SUBJECT MAY HAVE SHIPPED")
    rows = re.findall(r"^\| (\d+) \| \S+ \| (.+?) \| (\S+) \| (\S+) \| .+ \| (LIVE|PENDING) \|$",
                      (REPO / "ci" / "GATES.md").read_text(encoding="utf-8"), re.M)
    pending = [(i, subj, at) for i, subj, at, _red, live in rows if live == "PENDING"]
    print(f"  {len(pending)} PENDING row(s)")
    for i, subj, at in pending:
        print(f"      row {i}: subject exists at {at} — {subj[:70]}")
    NOTES.append(f"{len(pending)} PENDING gate row(s); each must be re-read every phase")


def bare_rates() -> None:
    section("4. BARE RATES")
    import subprocess

    r = subprocess.run(["bash", str(REPO / "ci" / "no-bare-rate.sh")], cwd=REPO,
                       capture_output=True, text=True)
    print("  " + (r.stdout or r.stderr).strip().splitlines()[0])
    if r.returncode != 0:
        FINDINGS.append("ci/no-bare-rate.sh is red")


def catalogue_health() -> None:
    section("5. THE NEGATIVE-CONTROL CATALOGUE")
    import yaml

    entries = yaml.safe_load((REPO / "tests/negative/catalogue.yaml").read_text())["entries"]
    ids = [e["id"] for e in entries]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    no_injector = [e["id"] for e in entries if e.get("injector") == "NONE"]
    provisional = [e["id"] for e in entries if e.get("provisional")]
    no_positive = [e["id"] for e in entries if not e.get("positive_control")]
    print(f"  entries {len(entries)} · duplicate ids {dupes or 'none'}")
    print(f"  injector NONE {no_injector or 'none'} · provisional {provisional or 'none'}")
    print(f"  no positive control {no_positive or 'none'}")
    FINDINGS.extend(f"duplicate catalogue id: {d}" for d in dupes)
    FINDINGS.extend(f"catalogue entry with no positive control: {e}" for e in no_positive)
    NOTES.extend(f"provisional catalogue entry (excluded from caught): {p}" for p in provisional)


def ledger_health() -> None:
    section("6. THE VALIDATION LEDGER")
    rows = [json.loads(x) for x in
            (REPO / "reports/validation-ledger.jsonl").read_text().splitlines() if x.strip()]
    validation = [r for r in rows if "metric" in r]
    absence = [r for r in rows if "query_name" in r]
    no_caveat = [r["metric"] for r in validation if not r.get("caveat")]
    print(f"  validation rows {len(validation)} · absence rows {len(absence)}")
    print(f"  rows with no caveat: {no_caveat or 'none'}")
    print(f"  by phase: {dict(sorted(collections.Counter(r['phase'] for r in validation).items()))}")
    FINDINGS.extend(f"ledger row with no caveat: {m}" for m in no_caveat)


def unreached_modules() -> None:
    section("7. MODULES REACHED BY NOTHING")
    mods = {}
    for f in sorted(REPO.glob("src/cdfc/**/*.py")):
        mod = str(f.relative_to(REPO / "src")).replace("/", ".")[:-3]
        mods[mod.removesuffix(".__init__")] = f
    used: set[str] = set()
    for f in list(REPO.glob("src/**/*.py")) + list(REPO.glob("tests/**/*.py")) + list(REPO.glob("tools/**/*.py")):
        src = f.read_text(encoding="utf-8")
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                used |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                used.add(n.module)
                used |= {f"{n.module}.{a.name}" for a in n.names}
        for m in mods:
            leaf = m.rsplit(".", 1)[-1]
            if f'"{leaf}"' in src or f"'{leaf}'" in src:
                used.add(m)
    orphans = [m for m in sorted(mods) if m not in used]
    # A package marker exists because SCAN_ROOTS enumerates it; a deleted root would make every
    # grep gate report success over nothing.
    markers = [m for m in orphans if mods[m].name == "__init__.py"]
    real = [m for m in orphans if m not in markers]
    print(f"  {len(markers)} package marker(s) (required by SCAN_ROOTS)")
    print(f"  {len(real)} other module(s) reached by nothing: {real or 'none'}")
    FINDINGS.extend(f"module reached by nothing: {m}" for m in real)


def main() -> int:
    unconditional_assertions()
    gates_named_but_absent()
    pending_with_a_shipped_subject()
    bare_rates()
    catalogue_health()
    ledger_health()
    unreached_modules()

    section("SUMMARY")
    for n in NOTES:
        print(f"  note    : {n}")
    for f in FINDINGS:
        print(f"  FINDING : {f}")
    print(f"\n  {len(FINDINGS)} finding(s), {len(NOTES)} note(s)")
    print("  The reading half of the audit is in docs/AUDIT-P0-P6.md.")
    return 1 if FINDINGS else 0


if __name__ == "__main__":
    raise SystemExit(main())
