#!/usr/bin/env python
"""P5's measurement: the runtime seven-term closure on a real filing, and the static/runtime delta.

**Nobody has this number.** The static figure counts cells reachable by at least one harvested
predicate, computed before any evaluation. The runtime figure is what a filing actually produces —
and under the binding precedence order it can be LOWER, because a cell read by one passing and one
not-run predicate is unsettled. Both are published, with the delta.

    make run-fme
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.p5_run import (  # noqa: E402
    INDEPENDENT,
    INDEPENDENT_LABEL,
    SEEDED,
    SMOKE_LABEL,
    TEMPLATE_COMPUTED,
    failing_predicate_ids,
    fme_harvest,
    fme_surface,
    predicates_reading,
    run_filing,
)
from cdfc.verdict.closure import TERMS  # noqa: E402
from cdfc.verdict.settled_fraction import runtime_settled_cells, static_settled_cells  # noqa: E402

OUT_MD = REPO / "docs" / "measurements" / "P5-runtime-closure.md"
OUT_JSON = REPO / "docs" / "measurements" / "p5-verdict-closure.json"
SEED_CELL = "1. Introduction!C54"


def main() -> int:
    h = fme_harvest()
    n_surface, _cells, validation_state = fme_surface()
    static = static_settled_cells(h.candidates, h.schema)

    clean = run_filing(INDEPENDENT)
    seeded = run_filing(SEEDED)
    smoke = run_filing(TEMPLATE_COMPUTED)

    runtime = runtime_settled_cells(clean.cells)
    surface = set(_cells)
    outside = static - surface                 # bound by a predicate, not in the denominator
    inside_unsettled = (static & surface) - runtime
    p = clean.partition
    sf = clean.fraction
    assert p is not None and sf is not None, clean.closure_error

    data = {
        "warrant": "MEASURED",
        "filing_primary": INDEPENDENT.name,
        "filing_primary_label": INDEPENDENT_LABEL,
        "filing_smoke": TEMPLATE_COMPUTED.name,
        "filing_smoke_label": SMOKE_LABEL,
        "field_surface": n_surface,
        "validation_state": validation_state,
        "static_settled_cells": len(static),
        "runtime_settled_cells": len(runtime),
        "delta_runtime_minus_static": len(runtime) - len(static),
        # The delta DECOMPOSED, because an undecomposed delta reads as roll-up lowering when most
        # of it is something else entirely.
        "statically_bound_outside_the_field_surface": len(outside),
        "in_surface_bound_but_unsettled": len(inside_unsettled),
        "closure": p.as_row(),
        "fraction": str(sf.fraction),
        "admission_state": sf.admissionState,
        "keys_preflighted": clean.keys_checked,
        "keys_type_checked": clean.keys_type_checked,
        "cells_lowered_by_rollup": p.loweredByRollup,
        "seeded": {
            "cell": SEED_CELL,
            "expected_failures": list(predicates_reading(SEED_CELL)),
            "observed_failures": list(failing_predicate_ids(seeded)),
        },
        "smoke": {
            "run_state": smoke.run_state,
            "checks": len(smoke.checks),
            "note": "result NOT consulted by the exit gate",
        },
    }
    OUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render(data, clean, sf, p), encoding="utf-8")
    print(f"fraction {data['fraction']}  settled {p.settled}/{p.inScope}  "
          f"static {data['static_settled_cells']}  runtime {data['runtime_settled_cells']} "
          f"(delta {data['delta_runtime_minus_static']:+d}) -> {OUT_MD.relative_to(REPO)}")
    return 0


def render(d: dict, clean, sf, p) -> str:
    terms = "  +  ".join(f"{t} {getattr(p, t)}" for t in TERMS)
    return f"""# P5 — the runtime closure partition, on a real filing

**Warrant: MEASURED.** Produced by `make run-fme`. Nobody has this number: the static figure is
computed before any evaluation, and the runtime figure is what a filing actually produces.

## The filing the claim is made on

`{d['filing_primary']}`

> {d['filing_primary_label']}

## The seven terms, and they sum to the field surface

    {terms}
      ==  {p.total}   (cellsTotal {p.cellsTotal})

    of which retained: outOfScope {p.outOfScopeRetained}   informational {p.informationalRetained}
    inScope            {p.inScope}
    fraction           {d['fraction']}   =  settled {p.settled} / inScope {p.inScope}

`fraction` never renders without `cellsTotal` and `inScope` beside it. A shrinking denominator
must be visible on the page, not merely correct in the object.

| field | value |
|---|---:|
| field surface (denominator) | **{d['field_surface']}** |
| denominator validation state | `{d['validation_state']}` |
| admission state | `{d['admission_state']}` |
| keys pre-flighted | {d['keys_preflighted']} |
| keys **type**-checked | {d['keys_type_checked']} |
| cells lowered by roll-up | {d['cells_lowered_by_rollup']} |

**`keys_type_checked` is published beside `keys_preflighted` because a type check that did not
happen is never reported as one** (D-P5-03). Where the AST cannot decide a key's type, the key is
presence-checked only and the difference between these two numbers is how much.

## Static against runtime

| number | value | what it counts |
|---|---:|---|
| `static_settled_cells` | **{d['static_settled_cells']}** | cells reachable by >= 1 harvested predicate, before any evaluation |
| `runtime_settled_cells` | **{d['runtime_settled_cells']}** | cells whose ROLLED-UP state is PASS or FAIL on this filing |
| delta | **{d['delta_runtime_minus_static']:+d}** | — |

### The delta, decomposed

| part | cells | what it is |
|---|---:|---|
| statically bound but **outside the field surface** | {d['statically_bound_outside_the_field_surface']} | a predicate binds a LOCKED or FORMULA cell. It is checked; it is not part of the denominator, which is what a filer fills in |
| in the surface, bound, and **not settled** | {d['in_surface_bound_but_unsettled']} | the part the roll-up is responsible for |

**Most of the delta is the first row, and saying so matters**: an undecomposed delta reads as
roll-up lowering when most of it is a difference of populations.

**Under the binding precedence order the runtime figure CAN be lower**, because a cell read by one
passing and one not-run predicate is unsettled — *the settled fraction falls, it does not silently
succeed.* On this filing {d['cells_lowered_by_rollup']} cell(s) were lowered by roll-up.

## One seeded fault, and the predicates are named rather than counted

Seeded at `{d['seeded']['cell']}` by raw-zip surgery: one worksheet part differs and nothing else.

| | |
|---|---|
| predicates reading that cell | `{'`, `'.join(d['seeded']['expected_failures'])}` |
| predicates that FAILED | `{'`, `'.join(d['seeded']['observed_failures'])}` |

The clean filing produced **zero** failures. Without that control the seeded number would carry no
information.

## The smoke filing, and why its number is not on this page as a claim

`{d['filing_smoke']}` — run state `{d['smoke']['run_state']}`, {d['smoke']['checks']} checks.

> {d['filing_smoke_label']}

**Its result does not enter P5's exit gate.** The gate is TRUE or FALSE without consulting it, and
a red there is a defect report rather than a gate failure.

## What this measurement does not license

That any of these predicates is right. `admissionState` is `PRE-GATE`: none of them is admitted
under G4, and the number says how much of the denominator a check ran over — not that any check
encodes the rule it is named for. The denominator itself is `PROVISIONAL-UNVALIDATED`: nobody
outside this repository has checked the unlocked mask against a person filling the form in.
"""


if __name__ == "__main__":
    raise SystemExit(main())
