#!/usr/bin/env python
"""P0's measurement: which gates are LIVE, and which have been OBSERVED RED.

This is the number P0 produces that did not exist before. It is deliberately not "how
many gates are written" — writing a gate is free. The quantity that carries information
is **how many have been observed failing on a deliberately broken build**, because a gate
that has never gone red is a preference with a filename.

EVIDENCE COMES FROM THE SWEEP, NOT FROM A SECOND LIST. An earlier version of this file
kept its own `OBSERVED_BY` mapping of gate id -> pytest node and re-ran those nodes. That
is a second hand-maintained list beside `tests/negative/catalogue.yaml`, and two lists
drift — the one that drifts is the one nobody is reading. So each gate names its
catalogue entry, and a gate is OBSERVED RED iff that entry was `caught` in
`reports/negative-control-sweep.json`, under the exact-set contract.

A gate with no catalogue entry is NOT counted. That absence is the measurement.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO))

from cdfc.gates import parse  # noqa: E402
from cdfc.measure.paths import P0_GATE_LIVENESS  # noqa: E402

SWEEP = REPO / "reports" / "negative-control-sweep.json"

# gate id -> the catalogue entry whose sweep result is its evidence.
# A gate absent from this map has no evidence and is reported as such.
EVIDENCE: dict[int, str] = {
    1: "NC-CI03",   # no-green-tick
    2: "NC-CI04",   # no-bare-except
    6: "NC-CI06",   # registry schema / duplicate id
    7: "NC-CI08",   # no permanently-pending gate
    8: "NC-CI07",   # the LIVE set is pre-registered
    11: "NC-CI13",  # licence denylist
    12: "NC-CI14",  # encoding / NUL byte
    17: "NC-CI15",  # no timing in a hashed payload
    19: "NC-CI17",  # no machine-local absolute path in the build
    20: "NC-E13",   # no float in the deterministic numeric core
    # P4
    21: "NC-Q44",   # key extraction is structural, not lexical
    27: "NC-Q02",   # the predicate schema and the loader invariant
    # P5
    # P6
    37: "NC-Q64",   # no bare rate
    38: "NC-Q30",   # no openpyxl writer
    47: "NC-Q33",   # the taxonomy document is generated
    # P7
    # P8
    14: "NC-E33",   # no model client in the verdict path (promoted at P6)
    # --- P9, rows 64-75 -----------------------------------------------------------------
    # Rows 64 and 65 guard the P9 ENTRY criteria, whose subjects shipped at P3. They are bound
    # to the NC entries whose injectors break the same rule: NC-R03 breaks the envelope
    # adapter's refusal, which is what makes the flagship's demonstration a demonstration, and
    # NC-R12 pins the tolerance-unit pair. See docs/GATE-CHANGES.md, 14 Aug 2026.
    # Rows 3, 28 and 48 were bound to injectors that break something ELSE and leave the gate
    # green. `gate_liveness` now RUNS a shell gate under its bound injector, so a nominal binding
    # reports `BINDING NOT VERIFIED` rather than being counted as a red observation.
    3:  "NC-CI18",  # a missing scan root, planted by the injector that names it
    28: "NC-CI19",  # a pattern over an OOXML cell element
    48: "NC-CI20",  # a wall clock on the solver
    # Rows 76 and 77: two gates that had run in `make greps` since P0 with NO registry row, so they
    # were outside this measurement's denominator entirely — never LIVE, never PENDING, never
    # observed red. Registering `no-clock-in-core` found a second defect in it: its pattern listed
    # only the MONOTONIC clocks, so a `time.time()` in the deterministic core left it green.
    76: "NC-CI21",  # a wall clock in the deterministic core
    77: "NC-CI22",  # a bare absence on a surface
    # --- P10, rows 78-90 ----------------------------------------------------------------
    # L6.5's gates. Row 80 is bound to NC-C04 and NOT to NC-C01, deliberately: cause isolation is
    # only meaningful under an APPARATUS break — a stubbed loop trips it too, but a broken key
    # resolver is the case where every other layer stays green and only the canary layer knows.
    78: "NC-C10",   # no duration field inside a hashed object (F23)
    79: "NC-C10",   # no clock reachable from the selfcheck package — the same ruling's other half
    # NC-C03 carries `injector: NONE`, so the sweep can never report it CAUGHT — an entry that
    # injects nothing catches nothing. Its GENERAL form is what row 90 guards, and NC-C03b
    # injects that: deleting `layer_exists_assertion` from the catalogue.
    # --- P11, rows 91-98, and row 15 -----------------------------------------------------
    # Row 15 waited eleven phases for a schema to walk. Its evidence is NC-A17's injector,
    # because the substring/exact substitution is the shape that makes the walk wrong in a way
    # that still reports a number.
    15: "NC-A17",   # the attestation schema has no banned name at any depth
    91: "NC-A17",   # the same walk, and the same break
    92: "NC-A17",   # the three-part rule, both halves
    93: "NC-A16",   # no JSON float token in the canonicalised bytes
    # --- P12: the settling experiment. Each row guards the ORDERING rather than a verdict.
    # --- P14-B1: the surfaces. Row 112 guards the gate's own denominator.
    # --- P14-B2: the Unchecked panel. Row 114 keeps `None` and `()` apart.
    113: "NC-A33",   # an imported prior may not become our threshold
}


def _catalogue_entries() -> list[dict]:
    import yaml

    raw = yaml.safe_load((REPO / "tests" / "negative" / "catalogue.yaml").read_text(encoding="utf-8"))
    return list(raw.get("entries") or []) if isinstance(raw, dict) else list(raw or [])


def _test_of(g) -> str | None:
    """The pytest node id a `pytest` row names, DISCOVERED rather than hard-coded.

    The row names its test in backticks; the file is found by searching `tests/`. A hard-coded
    path table would be a second list, and this module already carries the scar of one.
    """
    m = re.search(r"`(test_[A-Za-z0-9_]+)`", g.gate)
    if not m:
        return None
    name = m.group(1)
    for f in sorted((REPO / "tests").rglob("test_*.py")):
        if re.search(rf"^def {re.escape(name)}\b", f.read_text(encoding="utf-8"), re.M):
            return f"{f.relative_to(REPO)}::{name}"
    return None


def _derive_pytest_evidence(rep: dict) -> dict[str, tuple[str, bool]]:
    """test node id -> (NC entry that demonstrated it, provisional).

    **THIS REPLACES A HAND-MAINTAINED MAP FOR THE LARGER GATE POPULATION, AND THAT IS THE POINT.**
    `EVIDENCE` below is exactly the kind of hand-kept list this module's own docstring argues
    should not exist -- and it behaved like one twice. It drifted (rows 28 and 48 pointed at
    injectors touching neither gate's subject) and then it fell BEHIND: it stops at gate 115 while
    the registry reached 125, so ten LIVE gates reported `NO CATALOGUE ENTRY` and the published
    figure read `115 of 125` when the controls for those gates were green in the sweep all along.

    The sweep already records, per NC entry, every guard's `node_id`, whether it was EXPECTED to
    flip, and whether it was OBSERVED red. That is the evidence itself. A `pytest` gate IS a named
    test, so the binding is a lookup rather than an assertion: the gate is observed red exactly
    when some non-provisional entry made THAT test go red while expecting it to. Nobody maintains
    it, so nobody can forget to.
    """
    out: dict[str, tuple[str, bool]] = {}
    for row in rep.get("rows", []):
        for g in row.get("guards", []):
            if not g.get("flips_expected") or not g.get("observed_red"):
                continue
            node = g.get("node_id") or g.get("path") or ""
            # A non-provisional demonstration beats a provisional one; otherwise first wins.
            prov = bool(row.get("provisional"))
            if node not in out or (out[node][1] and not prov):
                out[node] = (row["id"], prov)
    return out


def _script_of(g) -> str | None:
    """The `ci/*.sh` path a shell row names, from its own gate text."""
    m = re.search(r"(ci/[A-Za-z0-9_.-]+\.sh)", g.gate)
    if not m:
        return None
    return m.group(1) if (REPO / m.group(1)).is_file() else None


def main() -> int:
    gates = parse()
    live = [g for g in gates if g.liveness == "LIVE"]
    pending = [g for g in gates if g.liveness == "PENDING"]

    if not SWEEP.exists():
        print(f"no sweep report at {SWEEP}; run `make nc-sweep` first", file=sys.stderr)
        return 1
    rep = json.loads(SWEEP.read_text())
    by_id = {r["id"]: r for r in rep["rows"]}

    derived = _derive_pytest_evidence(rep)

    # --- EVIDENCE IS NOW A SHELL-ROW MAP, AND THAT IS ENFORCED RATHER THAN ASKED FOR ---------
    #
    # Every `pytest` row derives its evidence from the sweep. A hand row for a pytest gate is
    # therefore UNREAD, and an unread hand row is the thing that drifts silently -- a future
    # editor would add one, see the gate reported green, and conclude the row did it. So a
    # pytest id left in `EVIDENCE` is a hard failure with the reason on the face of it.
    kind_of = {g.id: g.kind for g in gates}
    stray = sorted(i for i in EVIDENCE if kind_of.get(i) == "pytest")
    if stray:
        print(f"GATE-LIVENESS FAIL: EVIDENCE carries pytest rows {stray}. Pytest evidence is "
              f"DERIVED from the sweep's own per-guard record; a hand row for one is never read "
              f"and would drift unnoticed. Delete them.", file=sys.stderr)
        return 1

    observed: dict[int, str] = {}
    for g in live:
        # `pytest` rows derive their evidence from the sweep and never consult EVIDENCE. A row
        # whose named test is nobody's flipping guard is reported as such -- that is a REAL gap
        # in the controls, and it is now visible instead of being papered over by a map entry.
        if g.kind == "pytest":
            node = _test_of(g)
            if node is None:
                observed[g.id] = "GATE ROW NAMES NO TEST"
            elif node not in derived:
                observed[g.id] = f"{node.split('::')[-1]}: NO CONTROL FLIPS IT"
            else:
                nc, prov = derived[node]
                observed[g.id] = f"{nc}: PROVISIONAL" if prov else f"{nc}: OBSERVED RED"
            continue
        nc = EVIDENCE.get(g.id)
        if nc is None:
            observed[g.id] = "NO CATALOGUE ENTRY"
        elif nc not in by_id:
            observed[g.id] = f"{nc}: NOT IN SWEEP"
        elif by_id[nc]["provisional"]:
            observed[g.id] = f"{nc}: PROVISIONAL"
        elif by_id[nc]["caught"]:
            observed[g.id] = f"{nc}: OBSERVED RED"
        else:
            observed[g.id] = f"{nc}: NOT CAUGHT"

    # --- THE BINDING IS VERIFIED FOR SHELL GATES, NOT TRUSTED --------------------------------
    #
    # `EVIDENCE` is a HAND-MAINTAINED MAP, and this module's own docstring argues that a
    # hand-maintained `OBSERVED_BY` list drifts and was removed for that reason. It is exactly
    # such a list, and it drifted: rows 28 (`no-regex-over-xml`) and 48 (`no-wallclock-z3`) were
    # published OBSERVED RED on injectors that edit `EVALUATION-CONTRACT.md` and Z3's `unknown`
    # handling respectively — neither touches either gate's subject, and neither gate goes red
    # under it. Both gates ARE functional; the evidence pointed at the wrong break.
    #
    # For a `shell` row the claim is directly checkable: run the script under the bound injector
    # and require a non-zero exit. A row whose bound injector leaves its script green is reported
    # as `BINDING NOT VERIFIED` rather than counted, because a red observation nobody can
    # reproduce is the thing this whole file exists to refuse.
    shell_rows = [g for g in live if g.kind == "shell" and observed.get(g.id, "").endswith("OBSERVED RED")]
    if shell_rows:
        sys.path.insert(0, str(REPO))
        from injectors import BY_NAME, inject  # noqa: PLC0415

        entries = {e["id"]: e for e in _catalogue_entries()}
        for g in shell_rows:
            nc = EVIDENCE[g.id]
            inj = (entries.get(nc) or {}).get("injector")
            cls = BY_NAME.get(inj) if inj else None
            if cls is None:
                observed[g.id] = f"{nc}: BINDING NOT VERIFIED (no injector {inj!r})"
                continue
            script = _script_of(g)
            if script is None:
                continue
            probe = cls()
            # TWO INJECTOR SHAPES, and only one of them is checkable this way.
            #
            #   (a) BREAK THE SUBJECT — plant the thing the gate exists to find. The gate must go
            #       RED, and that is verifiable here.
            #   (b) DEFEAT THE GATE — the `_DefeatGate` family replaces the script itself with a
            #       stub that exits 0. Under it the gate is green BY DESIGN and its evidence is a
            #       guard test that notices the gate stopped working. Requiring a non-zero exit
            #       there would report a false defect on a legitimate control.
            #
            # The two are told apart by what the injector TOUCHES: an injector that rewrites the
            # gate's own script is shape (b).
            if any(str(p).endswith(script.split("/")[-1]) for p in getattr(probe, "touches", ())):
                continue
            with inject(probe):
                rc = subprocess.run(["bash", script], cwd=REPO, capture_output=True).returncode
            if rc == 0:
                observed[g.id] = (
                    f"{nc}: BINDING NOT VERIFIED — `{script}` exits 0 under `{inj}`"
                )

    n_observed = sum(1 for v in observed.values() if v.endswith("OBSERVED RED"))
    result = {
        "phase": "P0",
        "warrant": "MEASURED",
        "evidence_source": "reports/negative-control-sweep.json (exact-set contract)",
        "gates_total": len(gates),
        "gates_live": len(live),
        "gates_pending": len(pending),
        "gates_with_an_observed_red": n_observed,
        "denominator_for_observed": len(live),
        "per_gate": {str(k): v for k, v in sorted(observed.items())},
        "live_ids": sorted(g.id for g in live),
        "pending_ids": sorted(g.id for g in pending),
        "sweep": {
            k: rep[k]
            for k in (
                "entries_caught",
                "entries_active",
                "guards_flipped",
                "guards_expected_to_flip",
                "none_count",
                "provisional_count",
            )
        },
        "note": (
            "A gate is OBSERVED RED iff its catalogue entry was caught under the sweep's "
            "exact-set contract: every flips:true guard red, every flips:false guard green. "
            "PROVISIONAL entries prove nothing yet and are excluded — a green entry with no "
            "information in it must not be counted as evidence."
        ),
    }
    P0_GATE_LIVENESS.parent.mkdir(parents=True, exist_ok=True)
    P0_GATE_LIVENESS.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")

    print(f"gates total          : {len(gates)}")
    print(f"  LIVE               : {len(live)}   {sorted(g.id for g in live)}")
    print(f"  PENDING            : {len(pending)}   {sorted(g.id for g in pending)}")
    print(f"OBSERVED RED         : {n_observed} of {len(live)} live gates")
    for gid, why in sorted(observed.items()):
        if not why.endswith("OBSERVED RED"):
            print(f"  gate {gid:>2}  {why}")
    print(f"sweep: entries {rep['entries_caught']}/{rep['entries_active']} · "
          f"guards {rep['guards_flipped']}/{rep['guards_expected_to_flip']} · "
          f"provisional {rep['provisional_count']}")
    print(f"wrote {P0_GATE_LIVENESS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
