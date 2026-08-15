"""P14-B1 — the admission state. **Computed per run. Never a constant.**

Criterion A11: a settled count may not render without the admission state of the predicate set that
produced it. This module is the half that makes the state true; `render.py`'s `Hero` — which has no
default for `admission` — is the half that makes it unavoidable.

## Why it is computed rather than configured

The obvious implementation is a string in a config file that someone updates when the corpus lands.
That string would be correct for exactly as long as somebody remembered, and it would be **wrong in
the flattering direction** the moment a predicate set changed underneath it: a report saying
`ADMITTED` over a run whose predicates were never qualified makes exactly the claim this product
exists to refuse, wearing a status label instead of a glyph.

So `admission_state()` reads the **qualification rows of the predicates that actually produced this
run's counts** and derives the state each time. There is no setter, no override and no cached
value.

## The three states, and why `PRE-GATE` is not `FAIL`

| state | when | what a reader may conclude |
|---|---|---|
| `PRE-GATE` | **no** contributing predicate has a G4 row with a provenance other than `SELF-AUTHORED` | *a check ran over this much of the form.* **Nothing about whether any check is right** |
| `PARTIALLY-ADMITTED` | some do, some do not | the settled count mixes admitted and unadmitted work, and the caveat says which |
| `ADMITTED` | every contributing predicate is admitted | the strongest claim available, and it is still only about the fault model |

**`PRE-GATE` is a statement about us, not about the filing.** It says the instrument has not been
qualified, not that the filing failed — and keeping those apart is the distinction the whole
project is named for. On this tree it is the true state: `G-CORPUS` is on its `FAIL` branch, no
clean corpus exists, and no predicate has an admissible G4 row.
"""

from __future__ import annotations

from typing import Any, Final, Literal

AdmissionState = Literal["PRE-GATE", "PARTIALLY-ADMITTED", "ADMITTED"]

# A G4 row over a corpus we wrote ourselves licenses nothing: the false-failure rate of a predicate
# measured on filings authored by the same person who wrote the predicate is a measurement of an
# intention. `qualify/g4_ffr.py` refuses it upstream; this is the surface's independent read.
INADMISSIBLE_PROVENANCE: Final[str] = "SELF-AUTHORED"

CAVEAT: Final[dict[str, str]] = {
    "PRE-GATE": (
        "PRE-GATE: none of the predicates producing this number is admitted under G4. The number "
        "says how much of the denominator a check ran over, not that any check is right."
    ),
    "PARTIALLY-ADMITTED": (
        "PARTIALLY-ADMITTED: some predicates producing this number are admitted under G4 and some "
        "are not. The count mixes the two and cannot be read as either."
    ),
    "ADMITTED": (
        "ADMITTED: every predicate producing this number cleared all five gates, including a "
        "measured false-failure rate on a corpus this project did not author. That is a claim "
        "about the fault model, not about the filing being correct."
    ),
}


def _is_admitted(pred: Any) -> bool:
    """One predicate, by its own qualification row. **Absent is not admitted.**"""
    q = getattr(pred, "qualification", None)
    if q is None:
        return False
    provenance = str(
        getattr(q, "corpus_provenance", None)
        or getattr(getattr(q, "g4", None), "corpus_provenance", "")
    ).upper()
    if not provenance or INADMISSIBLE_PROVENANCE in provenance:
        return False
    # An FFR that was never computed is not an FFR that came back clean.
    return getattr(q, "false_failure_rate", None) is not None


def contributing_predicates(run: Any) -> tuple[Any, ...]:
    """The predicates that produced this run's counts — **not every predicate in the registry.**

    A registry full of admitted predicates does not make *this* run admitted if none of them bound
    to a cell in *this* filing. The denominator of the claim is the set that contributed to it.
    """
    seen: dict[str, Any] = {}
    for cell in getattr(run, "cells", ()):
        for ev in getattr(cell, "evaluations", ()) or ():
            p = getattr(ev, "predicate", None) or getattr(ev, "envelope", None)
            pid = getattr(p, "id", None) or getattr(ev, "predicate_id", None)
            if pid is not None and pid not in seen:
                seen[pid] = p
    return tuple(v for v in seen.values() if v is not None)


def admission_state(run: Any) -> AdmissionState:
    """`PRE-GATE` / `PARTIALLY-ADMITTED` / `ADMITTED`, derived every time it is asked for."""
    preds = contributing_predicates(run)
    if not preds:
        # No contributing predicate at all is the weakest state, not an error and not the
        # strongest. A run in which nothing bound has certainly not admitted anything.
        return "PRE-GATE"
    admitted = sum(1 for p in preds if _is_admitted(p))
    if admitted == 0:
        return "PRE-GATE"
    if admitted == len(preds):
        return "ADMITTED"
    return "PARTIALLY-ADMITTED"


def caveat(state: AdmissionState) -> str:
    """The sentence that travels with the state. **Required beside any settled count.**"""
    return CAVEAT[state]
