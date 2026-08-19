#!/usr/bin/env python3
"""The instrument the Anchor substitution is measured with. **Not the envelope diff — that is blind.**

WHY THIS FILE EXISTS. The obvious way to measure a change to the cell-identity type is to re-emit
the 571 committed predicate envelopes and assert that none differs. W0-E checked whether that
measurement can see anything, and it cannot: `Sheet!REF` occurs in 571 of 571 envelope files and
**only inside `rationale` and `reason_if_inapplicable`** — prose. No structural field of an envelope
holds a cell string, so the three hazards a type substitution actually carries — iteration order over
a `frozenset`, `canonical_json` key order, a dropped `sorted()` — touch none of those bytes. A green
triple of integers would unblock the migration having exercised nothing.

WHAT IT MEASURES INSTEAD, and the split is the whole design:

  PUBLISHED     what `evaluate.run.write()` emits — `run.jsonl`, `manifest.json`, `run.db`. These
                must be byte-identical across hash seeds AND across the substitution. They are
                stable today ONLY BECAUSE sorting discipline is applied on the way out; the raw
                surfaces below are not.
                **`report.html` IS NOT COVERED and the omission is stated rather than left to be
                discovered.** It is rendered by `cli._render_report` after `write()` returns, so it
                is not in this instrument's reach. It is a published artefact and it deserves the
                same treatment; until it gets it, a green `--check` says nothing about the report.

  ORDER-BEARING the projections that expose the hazard: bound-cell sets in ITERATION order, the
                campaign site set, the schema-key union. MEASURED under three hash seeds these
                produce three different digests, which is what makes them a tripwire rather than
                decoration. They are recorded, never asserted stable — asserting them would be
                asserting that Python's set ordering is fixed, which it is not.

  SORTED        the same sets, sorted. Stable, and the control: if a SORTED projection ever moves
                across seeds, the perturbation is not ordering, it is content.

USAGE
    tools/anchor_hazard.py --baseline    snapshot before the substitution
    tools/anchor_hazard.py --check       compare against the snapshot; non-zero on drift
    tools/anchor_hazard.py --selftest    prove the instrument SEES a seeded perturbation

`--selftest` is not optional politeness. An instrument that has never been shown to go red is a
green light with no evidence behind it, which is the failure this whole repository is organised
against.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SNAPSHOT = REPO / "reports" / "anchor-hazard.json"
SEEDS = ("0", "1", "2")


def _digest(obj: object) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=False, separators=(",", ":"), default=str).encode()
    ).hexdigest()[:16]


def projections() -> dict[str, dict[str, str]]:
    """Computed IN THIS PROCESS, so the ambient `PYTHONHASHSEED` is the variable under test."""
    sys.path.insert(0, str(REPO / "src"))
    from cdfc.measure.p5_run import FME, harvest_for, surface_for
    from cdfc.predicates.ast_walker import bound_cells

    h = harvest_for(FME)
    n, cells, state = surface_for(FME)

    order_bearing: dict[str, str] = {}
    sorted_: dict[str, str] = {}

    # 1. bound-cell sets. `bound_cells` returns a frozenset; iterating it is the hazard.
    per_cand = {c.id: bound_cells(c, h.schema) for c in h.candidates}
    order_bearing["bound_cells_iteration"] = _digest({k: list(v) for k, v in per_cand.items()})
    sorted_["bound_cells_sorted"] = _digest({k: sorted(v) for k, v in per_cand.items()})
    sorted_["bound_cells_counts"] = _digest({k: len(v) for k, v in per_cand.items()})

    # 2. the schema-key union — a set built by accumulation across candidates.
    ks: set[str] = set()
    for c in h.candidates:
        ks.update(c.schema_keys or ())
    order_bearing["schema_key_union_iteration"] = _digest(list(ks))
    sorted_["schema_key_union_sorted"] = _digest(sorted(ks))

    # 3. the campaign site set — the matching surface G2 scores against.
    sites: set[str] = set()
    camp = REPO / "reports/campaigns/fme-v3-seed20260810"
    for f in ("killed.jsonl", "survived.jsonl", "indeterminate.jsonl",
              "unobservable.jsonl", "unreachable.jsonl"):
        p = camp / f
        if not p.is_file():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                sites.update(json.loads(line).get("sites") or [])
    order_bearing["campaign_sites_iteration"] = _digest(list(sites))
    sorted_["campaign_sites_sorted"] = _digest(sorted(sites))

    # 4. the field surface itself, as the run consumes it.
    sorted_["field_surface"] = _digest({"n": n, "state": state, "cells": list(cells)})

    return {"order_bearing": order_bearing, "sorted": sorted_}


def published(out: Path) -> dict[str, str]:
    """The artefacts a reader receives. Produced by the REAL runner, not re-implemented here."""
    sys.path.insert(0, str(REPO / "src"))
    from cdfc.evaluate.run import write
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import FME

    target = write(run_filing(FME), out)
    got: dict[str, str] = {}
    for p in sorted(Path(target).rglob("*")):
        if p.is_file():
            got[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return got


def _one_seed(seed: str, tmp: Path) -> dict:
    """Re-exec so `PYTHONHASHSEED` is set BEFORE the interpreter starts. Setting it in-process is
    a no-op, and an instrument that silently measures one seed three times is worse than none."""
    env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(REPO / "src")}
    r = subprocess.run(
        [sys.executable, __file__, "--emit", "--out", str(tmp / f"seed{seed}")],
        cwd=REPO, env=env, capture_output=True, text=True, timeout=1800,
    )
    if r.returncode != 0:
        raise SystemExit(f"emit failed under seed {seed}:\n{r.stderr[-1500:]}")
    return json.loads(r.stdout)


def collect() -> dict:
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        per = {s: _one_seed(s, tmp) for s in SEEDS}

    pub = {k: {s: per[s]["published"].get(k) for s in SEEDS}
           for k in sorted(per[SEEDS[0]]["published"])}
    srt = {k: {s: per[s]["sorted"].get(k) for s in SEEDS}
           for k in sorted(per[SEEDS[0]]["sorted"])}
    ordb = {k: {s: per[s]["order_bearing"].get(k) for s in SEEDS}
            for k in sorted(per[SEEDS[0]]["order_bearing"])}
    return {"published": pub, "sorted": srt, "order_bearing": ordb}


def _report(snap: dict, baseline: dict | None) -> int:
    bad = 0
    print(f"{'projection':34} {'seed0':18} {'seed1':18} {'seed2':18} verdict")
    print("-" * 108)

    for group, must_be_stable in (("published", True), ("sorted", True), ("order_bearing", False)):
        for k, v in snap[group].items():
            vals = [v[s] for s in SEEDS]
            stable = len(set(vals)) == 1
            if must_be_stable and not stable:
                verdict, bad = "MOVED ACROSS SEEDS", bad + 1
            elif must_be_stable:
                verdict = "stable"
            else:
                # A tripwire that does NOT move means the hazard surface stopped being one. That is
                # not reassurance: it means this instrument can no longer see what it was built for.
                verdict = "varies (tripwire live)" if not stable else "TRIPWIRE WENT QUIET"
                if stable:
                    bad += 1
            print(f"{k[:32]:34} {vals[0]:18} {vals[1]:18} {vals[2]:18} {verdict}")

    if baseline is not None:
        print()
        moved = [k for k in snap["published"]
                 if baseline.get("published", {}).get(k, {}).get("0") != snap["published"][k]["0"]]
        if moved:
            bad += len(moved)
            print(f"PUBLISHED ARTEFACTS THAT MOVED SINCE THE BASELINE: {len(moved)}")
            for k in moved:
                was = baseline["published"].get(k, {}).get("0", "(absent)")
                print(f"   {k:24} {was} -> {snap['published'][k]['0']}")
        else:
            print(f"published artefacts unchanged since the baseline: "
                  f"{len(snap['published'])} of {len(snap['published'])}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--out", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()

    if a.emit:
        p = projections()
        p["published"] = published(Path(a.out))
        print(json.dumps(p))
        return 0

    if a.selftest:
        # THE INSTRUMENT MUST BE SHOWN TO GO RED. A frozenset of the same members iterated under two
        # different hash seeds is precisely the substitution hazard, so if this comparison does not
        # differ the instrument cannot see the thing it exists for.
        code = ("import json;"
                "s=frozenset('Sheet%d!A%d'%(i%7,i) for i in range(400));"
                "print(json.dumps(list(s)))")
        outs = []
        for seed in SEEDS:
            env = {**os.environ, "PYTHONHASHSEED": seed}
            outs.append(subprocess.run([sys.executable, "-c", code], capture_output=True,
                                       text=True, env=env).stdout)
        distinct = len(set(outs))
        print(f"selftest: a 400-member frozenset iterated under {len(SEEDS)} hash seeds "
              f"produced {distinct} distinct orderings")
        if distinct == 1:
            print("SELFTEST FAILED: set iteration did not vary, so this instrument is blind and "
                  "a green --check would mean nothing.", file=sys.stderr)
            return 1
        print("selftest OK: the hazard is real on this interpreter and the instrument can see it.")
        return 0

    snap = collect()
    base = json.loads(SNAPSHOT.read_text()) if (a.check and SNAPSHOT.is_file()) else None
    if a.check and base is None:
        print(f"no baseline at {SNAPSHOT}; run --baseline before the substitution", file=sys.stderr)
        return 1

    bad = _report(snap, base)
    if a.baseline:
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(snap, indent=1, sort_keys=True))
        print(f"\nwrote {SNAPSHOT}")
    print(f"\nanchor-hazard: {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
