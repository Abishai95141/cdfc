#!/usr/bin/env python
"""The negative-control sweep — EXACT-SET semantics.

THE CHANGE THIS FILE EXISTS FOR. The obvious contract is: apply the injector, re-run the
named guards, assert **at least one** fails. That is the defect. An entry naming four
guards is recorded as `caught` the moment its *weakest* guard goes red, and the guard the
whole story rests on may never have been exercised — it could have been deleted three
commits earlier and nothing would notice. `no_orphan_guard` does not see it: the test
still exists and is still named. It is simply never observed red.

So every guard carries `flips: true|false` and the sweep asserts the EXACT SET:
every `flips: true` guard is red under the injector, every `flips: false` guard is green
(a positive control — without one, a gate that rejects everything scores perfectly), and
the run fails if either set differs by one member.

Then the injector is removed and everything must be green again. A guard that stays red
is a leaked injector, which is itself a defect.

Five integers, never a percentage: entries_caught / entries_active,
guards_flipped / guards_expected_to_flip, none_count. `provisional_count` is reported
separately and EXCLUDED from entries_caught, because a green entry with no information in
it must not be counted as evidence.

NO TIMING FIELD ENTERS THIS REPORT (R3). Timings go to reports/perf/.
"""

from __future__ import annotations

import json
import re
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

from injectors import BY_NAME, Injector, inject  # noqa: E402

CATALOGUE = REPO / "tests" / "negative" / "catalogue.yaml"
REPORT = REPO / "reports" / "negative-control-sweep.json"

# `/abs/path/file.py:57: AssertionError: text`
TB_LINE = re.compile(r"^(?P<path>[^\s:]+\.py):(?P<line>\d+):\s*(?P<text>.*)$")

# The sentinel for "this guard went red and pytest gave us no line to quote". It is deliberately
# NOT a phrase that could pass for a captured assertion — `"reported failed"` did, and 13 rows of
# the committed report carried it while the test asserting reviewability saw a non-empty string.
NO_ASSERTION_CAPTURED = "(NO ASSERTION TEXT CAPTURED — the guard went red without a quotable line)"
HEXADDR = re.compile(r"0x[0-9a-fA-F]+")


@dataclass
class GuardResult:
    path: str
    flips_expected: bool
    observed_red: bool
    assertion_text: str = ""
    node_id: str = ""


@dataclass
class EntryResult:
    id: str
    injector: str
    status: str
    provisional: bool
    guards: list[GuardResult] = field(default_factory=list)
    caught: bool = False
    leaked: list[str] = field(default_factory=list)
    error: str = ""


def _normalise(text: str) -> str:
    """Deterministic assertion text: repo-relative paths, no addresses, collapsed space."""
    text = text.replace(str(REPO) + "/", "").replace(str(REPO), "")
    text = HEXADDR.sub("0xADDR", text)
    return " ".join(text.split())[:400]


def _run_guards(node_ids: list[str]) -> dict[str, tuple[bool, str]]:
    """Run guards in one pytest process. -> {node_id: (passed, assertion_text)}."""
    if not node_ids:
        return {}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *node_ids, "-q", "--no-header", "--tb=line", "-rf"],
        cwd=REPO,
        capture_output=True,
        text=True,
        # A deliberately minimal environment, for determinism — plus the ONE variable that tells
        # a shell gate which interpreter to use. Dropping CDFC_PY made every guard that invokes a
        # gate unrunnable wherever the venv is not at the gate's default path, and the sweep
        # reported "guards not green before injection" rather than saying so. Found in a fresh
        # clone, which is the only place it could be found.
        env={
            "PYTHONPATH": str(REPO / "src"),
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "HOME": str(Path.home()),
            **({"CDFC_PY": os.environ["CDFC_PY"]} if os.environ.get("CDFC_PY") else {}),
        },
    )
    out = proc.stdout + proc.stderr

    # Map failures by NODE ID. Mapping by file path marked every guard in a file red as
    # soon as one of them failed — which silently inflated the flipped set and would
    # have reported an exact-set match that never happened.
    failed_nodes: dict[str, str] = {}
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("FAILED ") or s.startswith("ERROR "):
            body = s.split(" ", 1)[1]
            nid = body.split(" - ")[0].strip()
            msg = body.split(" - ", 1)[1] if " - " in body else ""
            failed_nodes[nid] = _normalise(msg)

    # assertion text, keyed by file:line, to enrich the message
    tb: dict[str, str] = {}
    for line in out.splitlines():
        m = TB_LINE.match(line.strip())
        if m:
            tb[m.group("path")] = _normalise(m.group("text"))

    result: dict[str, tuple[bool, str]] = {}
    for nid in node_ids:
        red = nid in failed_nodes
        text = failed_nodes.get(nid, "")
        if red and not text:
            # **THE LOOKUP ONLY MATCHED A TRACEBACK KEYED ON THE GUARD'S OWN FILE**, so a guard
            # whose assertion is raised deeper — `RegistryError` out of `src/cdfc/gates.py`, say —
            # missed and fell back to the literal `"reported failed"`. 13 of 160 red guards carried
            # that placeholder instead of a captured assertion, and the test that exists to make
            # the artifact reviewable asserted only that the field was non-empty, so it could not
            # tell the difference.
            #
            # The run is per-guard, so ANY captured traceback line belongs to this guard's failure.
            # Preferring the guard's own file keeps the most specific line when there is one.
            f = nid.split("::")[0]
            text = next((v for k, v in tb.items() if k.endswith(f) or f.endswith(k)), "")
            if not text and tb:
                text = next(iter(tb.values()))
            # A visibly-named absence, never a phrase that reads like a captured assertion.
            text = text or NO_ASSERTION_CAPTURED
        result[nid] = (not red, text)
    return result


def sweep(catalogue: Path = CATALOGUE) -> dict[str, Any]:
    doc = yaml.safe_load(catalogue.read_text())
    entries = doc["entries"]

    results: list[EntryResult] = []
    for e in entries:
        er = EntryResult(
            id=e["id"],
            injector=str(e.get("injector", "NONE")),
            status=e.get("status", "active"),
            provisional=bool(e.get("provisional", False)),
        )
        guards = e["guard_tests"]
        node_ids = [g["path"] for g in guards]

        if er.injector == "NONE":
            er.guards = [GuardResult(g["path"], g["flips"], False, node_id=g["path"]) for g in guards]
            results.append(er)
            continue

        clean = _run_guards(node_ids)
        not_green = [n for n, (ok, _) in clean.items() if not ok]
        if not_green:
            er.error = f"guards not green before injection: {not_green}"
            er.guards = [GuardResult(g["path"], g["flips"], False, node_id=g["path"]) for g in guards]
            results.append(er)
            continue

        cls = BY_NAME.get(er.injector)
        if cls is None:
            er.error = f"injector {er.injector!r} not found"
            results.append(er)
            continue

        inj: Injector = cls()
        with inject(inj):
            under = _run_guards(node_ids)

        after = _run_guards(node_ids)
        er.leaked = [n for n, (ok, _) in after.items() if not ok]

        for g in guards:
            nid = g["path"]
            ok, text = under[nid]
            er.guards.append(
                GuardResult(
                    path=nid,
                    flips_expected=bool(g["flips"]),
                    observed_red=not ok,
                    assertion_text=text if not ok else "",
                    node_id=nid,
                )
            )
        expected = {g["path"] for g in guards if g["flips"]}
        observed = {gr.path for gr in er.guards if gr.observed_red}
        er.caught = (expected == observed) and not er.leaked and not er.provisional
        if expected != observed:
            er.error = (
                f"exact-set mismatch: expected red {sorted(expected)}, observed red {sorted(observed)}"
            )
        results.append(er)

    active = [r for r in results if r.status == "active" and not r.provisional and r.injector != "NONE"]
    report = {
        "contract": "EXACT SET — every flips:true guard red, every flips:false guard green. Never 'at least one'.",
        "entries_active": len(active),
        "entries_caught": sum(1 for r in active if r.caught),
        "guards_expected_to_flip": sum(
            1 for r in results for g in r.guards if g.flips_expected and not r.provisional
        ),
        "guards_flipped": sum(
            1 for r in results for g in r.guards if g.flips_expected and g.observed_red and not r.provisional
        ),
        "none_count": sum(1 for r in results if r.injector == "NONE"),
        "provisional_count": sum(1 for r in results if r.provisional),
        "rows": [asdict(r) for r in results],
    }
    return report


def main() -> int:
    rep = sweep()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")

    print(f"entries_caught          : {rep['entries_caught']} / {rep['entries_active']}")
    print(f"guards_flipped          : {rep['guards_flipped']} / {rep['guards_expected_to_flip']}")
    print(f"none_count              : {rep['none_count']}")
    print(f"provisional_count       : {rep['provisional_count']}  (excluded from entries_caught)")
    bad = [r for r in rep["rows"] if r["error"] or r["leaked"]]
    for r in bad:
        print(f"  !! {r['id']}: {r['error']}{' LEAKED:' + str(r['leaked']) if r['leaked'] else ''}")
    print(f"wrote {REPORT}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
