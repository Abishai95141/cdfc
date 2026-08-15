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
    # P5
    29: "NC-E30",   # the vacuous pass is unreachable
    30: "NC-E31",   # the cell table is the denominator
    31: "NC-E32",   # null is not zero and not omitted
    32: "NC-E33",   # two vocabularies, disjoint
    33: "NC-E34",   # no value-derived removal
    34: "NC-E35",   # an INFORMATIONAL-only cell stays counted
    35: "NC-E36",   # the contract is generated
    36: "NC-E37",   # pre-flight blocks expr
    # P6
    37: "NC-Q64",   # no bare rate
    38: "NC-Q30",   # no openpyxl writer
    39: "NC-Q33",   # the digest covers the operator table
    40: "NC-Q31",   # the filter recalculates
    41: "NC-Q60",   # F18
    42: "NC-Q61",   # F19
    43: "NC-Q37",   # unobservable mutants are retained
    44: "NC-Q32",   # the control arm excludes the cone
    45: "NC-Q63",   # the universe cannot see the predicates
    46: "NC-Q62",   # counts get zero tolerance
    47: "NC-Q33",   # the taxonomy document is generated
    # P7
    49: "NC-Q50",   # the disputed-region exclusion
    50: "NC-Q51",   # G0 computes a disposition, never a skip
    51: "NC-Q51",   # C2's two numbers — the same funnel-integrity entry
    52: "NC-Q34",   # the free gate runs before the expensive one
    53: "NC-Q38",   # Merkle domain separation
    54: "NC-Q55",   # admission requires a human
    55: "NC-Q07",   # UNPROVEN is never PROVED
    56: "NC-Q36",   # a removal is never silent
    # P8
    57: "NC-Q58",   # F2 — a corpus we generated cannot license an arithmetic FFR
    58: "NC-Q59",   # F5 — independence is a RESULT, not a string
    59: "NC-Q56",   # the interval re-derives on another machine
    60: "NC-Q10",   # set-FFR is `at least one`, never the mean
    61: "NC-Q09",   # the tier is keyed on the upper bound
    62: "NC-Q60b",  # F2's second half — the non-synthetic floor
    63: "NC-Q65",   # a heterogeneous column never reaches the runtime
    14: "NC-E33",   # no model client in the verdict path (promoted at P6)
    16: "NC-E30",   # the seven-term closure invariant (promoted at P6)
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
    64: "NC-R03",   # `recalculate`'s source is explicit at every call site
    65: "NC-R12",   # G-EVAL's label is computed from the oracle's author
    66: "NC-R01",   # a relation never PASSes an empty filing
    67: "NC-R02",   # a finding binds inside the field surface
    68: "NC-R03",   # the spike is a demonstration, not an admission
    69: "NC-R04",   # a defective oracle never fails a filer
    70: "NC-R05",   # no relation spans two accounting bases
    71: "NC-R06",   # the probe seed is an input, not entropy
    72: "NC-R07",   # a rename does not inflate the delta
    73: "NC-R09",   # filling in less never scores better
    74: "NC-R10",   # declaring a defect never raises the headline
    75: "NC-R12",   # a half repair of the unit defect cannot land quietly
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
    80: "NC-C04",   # under an apparatus break the cause set is exactly {canary_silent}
    81: "NC-C04c",  # a healthy run is VALID with digits — the admission-side positive control
    82: "NC-C05c",  # liveness is proved on the in-memory fact table (D6)
    83: "NC-C09",   # the expected-silent set is a constant, never derived from the registry
    84: "NC-C01b",  # a threshold moves only with its dated row
    85: "NC-C07",   # the residue never prints without the rejector set it was computed against
    86: "NC-C07",   # an adjudication with no argument is refused — the same renderer's refusal
    87: "NC-C13",   # the recompute-blind set, with its paired value assertion
    88: "NC-C01b",  # every published liveness count is len() of a row set (D5)
    89: "NC-C12",   # a cell with no value is ABSENT, never the string "None"
    # NC-C03 carries `injector: NONE`, so the sweep can never report it CAUGHT — an entry that
    # injects nothing catches nothing. Its GENERAL form is what row 90 guards, and NC-C03b
    # injects that: deleting `layer_exists_assertion` from the catalogue.
    90: "NC-C03b",  # an absence claim proves, in the same breath, that the layer exists (F6)
    # --- P11, rows 91-98, and row 15 -----------------------------------------------------
    # Row 15 waited eleven phases for a schema to walk. Its evidence is NC-A17's injector,
    # because the substring/exact substitution is the shape that makes the walk wrong in a way
    # that still reports a number.
    15: "NC-A17",   # the attestation schema has no banned name at any depth
    91: "NC-A17",   # the same walk, and the same break
    92: "NC-A17",   # the three-part rule, both halves
    93: "NC-A16",   # no JSON float token in the canonicalised bytes
    94: "NC-A18",   # expires is a function of timeVerified, not of the clock
    95: "NC-A19",   # verify checks the stored signature, never a fresh one
    96: "NC-A18",   # E2E-VERIFY catches the clock read three layers away
    97: "NC-A20",   # an INVALID run projects to nothing
    98: "NC-A16",   # the non-determinism enumeration is complete and states its boundary
}


def _catalogue_entries() -> list[dict]:
    import yaml

    raw = yaml.safe_load((REPO / "tests" / "negative" / "catalogue.yaml").read_text(encoding="utf-8"))
    return list(raw.get("entries") or []) if isinstance(raw, dict) else list(raw or [])


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
