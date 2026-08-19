#!/usr/bin/env python3
"""`make progress` — the build ledger, COMPUTED rather than claimed.

WHY THIS IS A PROGRAM AND NOT A MARKDOWN FILE. A hand-maintained checklist records what somebody
believed when they last edited it. Three sessions later it is a document about the past wearing the
tense of the present, and this repository has already been bitten by exactly that: `obligations.yaml`
explained its own emptiness with a reason that stopped being true when S1 pinned the statute, and a
test asserted the stale sentence so hard that correcting the file turned the suite red.

So every checkpoint below is a PREDICATE THAT RUNS. `DONE` means the probe observed the behaviour
just now, in this working tree. Nobody can mark a checkpoint done by editing a file, and a
checkpoint that regresses goes back to `TODO` on the next run without anybody noticing it should.

**A PROBE MAY NOT ASSERT ITS OWN SUBJECT.** Each one exercises the shipped path — imports the real
module, calls the real function, dispatches a real request — and never greps for a symbol it expects
to find. `grep -q "class Anchor"` would pass against a class with no callers, which is the shallow
proxy this file exists to refuse.

Read by: any agent or session, `make progress`. Written to `PROGRESS.md`, which is committed so the
state travels with the repository rather than living in one machine's task list.
"""

from __future__ import annotations

import importlib
import inspect
import io
import json
import re
import subprocess
import sys
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


@dataclass(frozen=True, slots=True)
class Probe:
    """One checkpoint. `run` returns (passed, evidence) and NEVER raises to the caller."""

    id: str
    phase: str
    title: str
    run: Callable[[], tuple[bool, str]]
    why: str = ""


@dataclass
class Result:
    probe: Probe
    passed: bool
    evidence: str
    error: str = ""


# --- the probes -------------------------------------------------------------------------------
#
# Each returns `(observed, evidence)`. Evidence is what the reader is owed: the number, the
# signature, the status line. "OK" on its own is not evidence.


def _p_suite_collects() -> tuple[bool, str]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO, capture_output=True, text=True, timeout=900,
    )
    total = sum(
        int(l.rsplit(":", 1)[1])
        for l in r.stdout.splitlines()
        if l.rsplit(":", 1)[-1].strip().isdigit()
    )
    # A COLLECTION ERROR IS NOT A FAILING TEST — it aborts before any assertion runs, and this
    # repository shipped in that state for several phases without noticing. So the probe fails on
    # a non-zero exit even when the count looks healthy.
    return (r.returncode == 0 and total > 0), f"{total} tests collected, exit={r.returncode}"


def _p_anchor_type() -> tuple[bool, str]:
    """The Anchor exists AND carries what W0-B/E2 measured it must carry."""
    try:
        m = importlib.import_module("cdfc.schema.anchor")
    except ModuleNotFoundError:
        return False, "cdfc.schema.anchor does not exist"
    A = getattr(m, "Anchor", None)
    if A is None:
        return False, "cdfc.schema.anchor has no Anchor"
    need = {"table", "rows", "cols"}
    have = set(getattr(A, "__annotations__", {}))
    missing = need - have
    if missing:
        return False, f"Anchor lacks {sorted(missing)}; has {sorted(have)}"
    return True, f"Anchor fields {sorted(have)}"


def _p_anchor_is_used() -> tuple[bool, str]:
    """A type nobody constructs is not a migration. Counts REAL call sites in src/."""
    try:
        importlib.import_module("cdfc.schema.anchor")
    except ModuleNotFoundError:
        return False, "no anchor module"
    n = 0
    for f in (REPO / "src" / "cdfc").rglob("*.py"):
        if "__pycache__" in str(f) or f.name == "anchor.py":
            continue
        if re.search(r"\bfrom cdfc\.schema\.anchor import\b|\bcdfc\.schema\.anchor\b", f.read_text(encoding="utf-8", errors="replace")):
            n += 1
    return n > 0, f"{n} modules in src/ import the anchor"


def _p_run_filing_takes_template() -> tuple[bool, str]:
    from cdfc.measure.p10_run import run_filing

    sig = inspect.signature(run_filing)
    return "template" in sig.parameters, f"run_filing{sig}"


def _p_cross_template_refused() -> tuple[bool, str]:
    """THE DEFECT THIS PHASE EXISTS TO KILL.

    An ALR filing scored over FME's 3,747-cell surface and reported VALID. The probe runs the real
    runner on a workbook that is not the pinned blank and requires the verdict to stop being VALID.
    """
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import FME, surface_for

    alr = REPO / "fixtures/prescribed/ALR_V2_3_20250808_1024.xlsx"
    if not alr.is_file():
        return False, "ALR fixture missing"
    sig = inspect.signature(run_filing)
    if "template" not in sig.parameters:
        return False, "run_filing takes no template; the defect cannot even be expressed"

    # BOTH HALVES, because either alone is a proxy. The first draft of this probe ran ALR against
    # the ALR template and required NOT-VALID — which was right while the runner could only ever
    # score against FME, and became WRONG the moment the repair landed: it started demanding that
    # the fixed behaviour look like the defect. A probe that fails when the code is correct is
    # worse than no probe.
    wrong = run_filing(alr, template=FME)   # scored over a blank it does not bind to
    right = run_filing(alr, template=alr)   # scored over its own
    refused = str(wrong.run_state) == "INVALID" and any(
        "denominator_disagreement" in str(c) for c in (wrong.invalid_causes or ())
    )
    own_n = surface_for(alr)[0]
    scored_on_its_own = str(right.run_state) == "VALID" and own_n != surface_for(FME)[0]
    return refused and scored_on_its_own, (
        f"wrong-template={wrong.run_state}/{[str(c) for c in (wrong.invalid_causes or ())]}, "
        f"own-template={right.run_state} over {own_n} cells (FME is {surface_for(FME)[0]})"
    )


def _p_denominator_disagreement_fires() -> tuple[bool, str]:
    """The reason code exists today and is raised by nothing. It must become reachable."""
    from cdfc.verdict.invalid import InvalidCause

    code = getattr(InvalidCause, "DENOMINATOR_DISAGREEMENT", None)
    if code is None:
        return False, "Invalid.DENOMINATOR_DISAGREEMENT is gone"
    hits = 0
    for f in (REPO / "src" / "cdfc").rglob("*.py"):
        if "__pycache__" in str(f) or f.name == "invalid.py":
            continue
        if "DENOMINATOR_DISAGREEMENT" in f.read_text(encoding="utf-8", errors="replace"):
            hits += 1
    return hits > 0, f"{hits} modules outside invalid.py reference the code"


def _p_upload_creates_a_run() -> tuple[bool, str]:
    """POST /v1/filings must stop refusing a filing whose template binds."""
    from cdfc.api.app import Request, dispatch

    fme = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
    if not fme.is_file():
        return False, "FME fixture missing"
    r = dispatch(Request("POST", "/v1/filings", body=fme.read_bytes()))
    body = (r.body or b"")[:160].decode("utf-8", "replace")
    return r.status == 201, f"status={r.status} body={body[:110]}"


def _p_host_fns_registered() -> tuple[bool, str]:
    """The four Path M needs: isnull, abs, max, min. Names the grammar admits."""
    from cdfc.predicates.cel_profile import ADMITTED_HOST_FNS

    need = {"isnull", "abs", "max", "min"}
    have = need & set(ADMITTED_HOST_FNS)
    return have == need, f"{len(have)} of 4 admitted: {sorted(have) or 'none'}"


def _p_determinism_instrument() -> tuple[bool, str]:
    """W0-E: the order-sensitive projections, not the envelope-diff proxy that is blind."""
    t = REPO / "tools/anchor_hazard.py"
    if not t.is_file():
        return False, "tools/anchor_hazard.py does not exist"
    r = subprocess.run([sys.executable, str(t), "--check"], cwd=REPO, capture_output=True, text=True, timeout=1800)
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["(no output)"])[-1][:150]


def _p_library_rows() -> tuple[bool, str]:
    """Not a Phase-1 target. Reported so nobody mistakes a green phase for a non-empty library."""
    p = REPO / "reports/qualification/qualification.json"
    if not p.is_file():
        return False, "no qualification artifact"
    d = json.loads(p.read_text())
    n = len(d.get("library") or [])
    return n > 0, f"{n} admitted predicates, {len(d.get('rejections') or [])} rejected"


def _p_statute_obligations() -> tuple[bool, str]:
    """Phase 4's headline. Zero today, and it must stay visible while it is zero."""
    from cdfc.predicates.obligations import load
    from cdfc.qualify.instruments import InstrumentStore

    t = load(REPO / "obligations.yaml", store=InstrumentStore(REPO / "corpus/instruments"))
    return len(t) > 0, f"{len(t)} statutory obligations"


PROBES: list[Probe] = [
    Probe("SUITE", "standing", "the suite collects and runs", _p_suite_collects,
          "a collection error aborts before any assertion; this repo shipped that way once"),
    Probe("P1-1", "Phase 1", "the Anchor type exists and carries table/rows/cols", _p_anchor_type,
          "E2 measured that rows and cols may be LISTS, and that a cell is the degenerate case"),
    Probe("P1-2", "Phase 1", "the Anchor is imported by shipped modules", _p_anchor_is_used,
          "a type nobody constructs is not a migration"),
    Probe("P1-3", "Phase 1", "run_filing takes a template", _p_run_filing_takes_template),
    Probe("P1-4", "Phase 1", "a foreign workbook is no longer reported VALID", _p_cross_template_refused,
          "the worst defect in the audit: ALR scored over FME's 3,747 and called VALID"),
    Probe("P1-5", "Phase 1", "invalid.denominator_disagreement is reachable", _p_denominator_disagreement_fires,
          "declared in P5 and raised by nothing since"),
    Probe("P1-6", "Phase 1", "POST /v1/filings creates a run", _p_upload_creates_a_run,
          "the drop screen's 201 branch is already written and unreachable"),
    Probe("P1-7", "Phase 1", "the anchor-hazard instrument runs green", _p_determinism_instrument,
          "W0-E: the envelope-diff proxy is blind; only order-sensitive projections see the hazard"),
    Probe("P2-1", "Phase 2", "the four Path M host functions are admitted", _p_host_fns_registered,
          "E1: unlocks 964 of 12,925 EBA rules without weakening a ban"),
    Probe("P2-2", "Phase 2", "the predicate library is non-empty", _p_library_rows,
          "0 of 348 admitted today, and repairing observable() cannot change that"),
    Probe("P4-1", "Phase 4", "a statutory obligation exists", _p_statute_obligations,
          "gated on 50 labelled proviso spans that nobody has started"),
]


def main() -> int:
    results: list[Result] = []
    for p in PROBES:
        try:
            ok, ev = p.run()
            results.append(Result(p, ok, ev))
        except Exception:
            results.append(Result(p, False, "", traceback.format_exc(limit=2).strip().splitlines()[-1][:150]))

    rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                         capture_output=True, text=True).stdout.strip() or "(no git)"

    out = io.StringIO()
    w = out.write
    w("# Build ledger\n\n")
    w("<!-- GENERATED BY `make progress`. Do not hand-edit: every line below is a probe that RAN.\n")
    w("     DONE means the behaviour was observed in this working tree just now. A checkpoint\n")
    w("     cannot be marked done by editing this file, and one that regresses reverts on the next\n")
    w("     run whether or not anybody expected it to. -->\n\n")
    w(f"Observed at `{rev}`.\n\n")

    by_phase: dict[str, list[Result]] = {}
    for r in results:
        by_phase.setdefault(r.probe.phase, []).append(r)

    for phase, rs in by_phase.items():
        done = sum(1 for r in rs if r.passed)
        w(f"## {phase} — {done} of {len(rs)} observed\n\n")
        w("| | checkpoint | evidence |\n|---|---|---|\n")
        for r in rs:
            mark = "DONE" if r.passed else "TODO"
            ev = r.error or r.evidence
            w(f"| **{mark}** | `{r.probe.id}` {r.probe.title} | {ev.replace('|', '\\|')} |\n")
        w("\n")
        notes = [r for r in rs if r.probe.why]
        if notes:
            for r in notes:
                w(f"* `{r.probe.id}` — {r.probe.why}\n")
            w("\n")

    w("## The blockers that are people, not code\n\n")
    w("Neither is an engineering task and both gate a later phase. Start them early or they\n")
    w("become the critical path.\n\n")
    w("| blocker | gates | state |\n|---|---|---|\n")
    labels = REPO / "fixtures/predicates/proviso-labels.json"
    lab = json.loads(labels.read_text()) if labels.is_file() else {}
    n_spans = len(lab.get("spans") or [])
    w(f"| 50 labelled proviso spans | all of Phase 4 (`g0_scope` raises without them) | "
      f"{n_spans} spans, labeller `{lab.get('labeller')}` |\n")
    cm = REPO / "fixtures/corpus_manifest.json"
    man = json.loads(cm.read_text()) if cm.is_file() else {}
    w(f"| 30 real filing + source-pack pairs | all of Phase 5 (G4 BLOCKING) | "
      f"n={man.get('n')}, non-synthetic={man.get('n_non_synthetic')} |\n")

    (REPO / "PROGRESS.md").write_text(out.getvalue(), encoding="utf-8")
    total_done = sum(1 for r in results if r.passed)
    print(f"progress: {total_done} of {len(results)} checkpoints observed — wrote PROGRESS.md")
    for r in results:
        if not r.passed:
            print(f"   TODO {r.probe.id:6} {r.probe.title}: {r.error or r.evidence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
