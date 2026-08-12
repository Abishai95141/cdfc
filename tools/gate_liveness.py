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
    3: "NC-CI01",   # scan roots exist
    4: "NC-CI02",   # openpyxl warning is an error  (PROVISIONAL)
    5: "NC-CI10",   # lockfile hash pinning
    6: "NC-CI06",   # registry schema / duplicate id
    7: "NC-CI08",   # no permanently-pending gate
    8: "NC-CI07",   # the LIVE set is pre-registered
    9: "NC-CI05",   # a stub that exits 0
    10: "NC-CI12",  # --version reads the registry
    11: "NC-CI13",  # licence denylist
    12: "NC-CI14",  # encoding / NUL byte
    13: "NC-CI01",  # a grep over a missing root
    17: "NC-CI15",  # no timing in a hashed payload
    18: "NC-CI16",  # a total equals the sum of its rows
    19: "NC-CI17",  # no machine-local absolute path in the build
    20: "NC-E13",   # no float in the deterministic numeric core
    # P4
    21: "NC-Q44",   # key extraction is structural, not lexical
    22: "NC-Q41",   # the digest covers every field of the record
    23: "NC-Q42",   # the two key mismatches stay distinguishable
    24: "NC-Q46",   # the weak pile is counted
    25: "NC-Q48",   # the G2 denominator is declared per class
    26: "NC-Q49",   # a host function never resolves live
    27: "NC-Q02",   # the predicate schema and the loader invariant
}


def main() -> int:
    gates = parse()
    live = [g for g in gates if g.liveness == "LIVE"]
    pending = [g for g in gates if g.liveness == "PENDING"]

    if not SWEEP.exists():
        print(f"no sweep report at {SWEEP}; run `make nc-sweep` first", file=sys.stderr)
        return 1
    rep = json.loads(SWEEP.read_text())
    by_id = {r["id"]: r for r in rep["rows"]}

    observed: dict[int, str] = {}
    for g in live:
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
