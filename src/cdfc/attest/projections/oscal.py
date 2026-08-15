"""P11-B3 — the OSCAL projection. **Declared lossy, and it refuses the one case it cannot say.**

Any party reading only this projection sees a smaller, cleaner report than the truth. That is the
point of saying so **inside the file**: `metadata.props` carries a mandatory `lossy` flag and the
URI of the normative artifact, so a reader who never saw the attestation still knows they are
holding a projection of one.

## The mapping

| our state | OSCAL |
|---|---|
| `PASS` | a finding with `status.state = satisfied` |
| `FAIL` | a finding with `status.state = not-satisfied` |
| `INDETERMINATE` · `NOT_RUN` · `NO_PREDICATE` | an **observation** carrying our reason as a prop, **no finding**, plus an `exclude-controls[]` entry |
| `OUT_OF_SCOPE` | an `exclude-controls[]` entry only |
| `ERROR` | an observation, **no finding** — an error is a fact about us |
| `INFORMATIONAL` | an observation, **no finding** |
| **`INVALID` (run level)** | **not representable at all** |

A finding is only emitted for the two states where we settled something. Everything else becomes an
observation and an exclusion, because **OSCAL's `finding-target.status.state` is a closed two-value
enum `{satisfied, not-satisfied}`** and there is no third member meaning *we did not look*. Mapping
`NOT_RUN` onto either one would be inventing a verdict.

## THE `INVALID` RULING, and it is the one a naive projector gets wrong in the worst direction

**An OSCAL Assessment Result with zero findings is schema-valid and means nothing in particular.**
So a projector that emits an empty AR for an `INVALID` run has published a **clean assurance
document for a run in which we could not demonstrate our instrument was working** — a document that
reads, to anyone who does not know the mapping, as *checked and nothing found*.

> **RULING: `project_oscal(statement)` raises `NotRepresentable` when `runState == "INVALID"`.**
> It does not emit a degraded document, it does not emit an empty one, and **there is no flag to
> make it.** The CLI prints the `invalid.*` cause and exits non-zero.

The absence of a flag is the substance of the ruling. A flag is what somebody sets when a pipeline
is failing and the deadline is Friday.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

NORMATIVE_URI: Final[str] = "https://cdfc.dev/filing-settlement-attestation/v1"

LOSSY_NOTICE: Final[str] = (
    "LOSSY PROJECTION. This document is a projection of a filing settlement attestation and carries "
    "strictly less than it does: four of the eight item states cannot be expressed as OSCAL "
    "findings at all, and appear here as observations and exclusions. The normative artifact is the "
    "attestation named in this metadata. A party acting on this document alone is acting on less "
    "than the evidence."
)

# The two states that become findings, and the closed enum they map onto.
SETTLED: Final[Mapping[str, str]] = {"PASS": "satisfied", "FAIL": "not-satisfied"}

# Everything else. An observation and — where the cell left the denominator — an exclusion.
OBSERVED: Final[tuple[str, ...]] = (
    "INDETERMINATE", "NOT_RUN", "NO_PREDICATE", "ERROR", "INFORMATIONAL",
)
EXCLUDED_ONLY: Final[tuple[str, ...]] = ("OUT_OF_SCOPE",)

# Every item state, so the projection's totality is checkable rather than assumed.
ALL_STATES: Final[frozenset[str]] = frozenset(SETTLED) | frozenset(OBSERVED) | frozenset(EXCLUDED_ONLY)


class NotRepresentable(ValueError):
    """The statement cannot be projected. **Raised, never degraded.**"""


def project_oscal(statement: Any, *, cells: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    """An OSCAL Assessment Results document — or a refusal.

    `cells` is the run's cell table: `[{stable_key, state, reason}, …]`. It is passed in rather
    than re-derived so this stays a pure function of a statement plus its run record, which is what
    `test_det__projections_are_byte_identical` needs.
    """
    pred = statement.as_predicate() if hasattr(statement, "as_predicate") else statement["predicate"]
    if pred["runState"] == "INVALID":
        causes = ", ".join(pred["invalidCauses"]) or "unstated"
        raise NotRepresentable(
            f"this run is INVALID ({causes}) and OSCAL cannot express it. Its "
            "`finding-target.status.state` is a closed two-value enum, and an Assessment Result "
            "with zero findings is schema-valid and reads as *checked and nothing found* — which "
            "would publish a clean assurance document for a run in which we could not demonstrate "
            "our instrument was working. There is no flag to emit it anyway."
        )

    findings: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for cell in cells:
        state, key = str(cell["state"]), str(cell["stable_key"])
        reason = cell.get("reason")
        if state in SETTLED:
            findings.append(
                {
                    "uuid": _uuid_for(key, state),
                    "title": key,
                    "target": {
                        "type": "objective-id",
                        "target-id": key,
                        "status": {"state": SETTLED[state]},
                    },
                }
            )
            continue
        if state in EXCLUDED_ONLY:
            excluded.append({"control-id": key, "remarks": str(reason or "")})
            continue
        if state not in OBSERVED:
            raise NotRepresentable(
                f"{key}: item state {state!r} has no projection rule. A state with no rule would "
                "be silently dropped, and a dropped cell is a cell this document implies was "
                "checked."
            )
        observations.append(
            {
                "uuid": _uuid_for(key, state),
                "title": key,
                "description": f"{state}: {reason or 'no reason recorded'}",
                "methods": ["TEST"],
                "props": [
                    {"name": "cdfc-item-state", "value": state, "ns": NORMATIVE_URI},
                    {"name": "cdfc-reason", "value": str(reason or ""), "ns": NORMATIVE_URI},
                ],
            }
        )
        excluded.append({"control-id": key, "remarks": f"{state}: {reason or ''}"})

    return {
        "assessment-results": {
            "uuid": _uuid_for("assessment", pred["scope"]["runId"]),
            "metadata": {
                "title": "Filing settlement — OSCAL projection",
                "version": "1",
                "oscal-version": "1.1.2",
                # **IN THE FILE, not in a README.** A reader who never saw the attestation still
                # learns from the document itself that they are holding a projection of one.
                "props": [
                    {"name": "lossy", "value": "true", "ns": NORMATIVE_URI},
                    {"name": "normative-artifact", "value": NORMATIVE_URI, "ns": NORMATIVE_URI},
                    {"name": "normative-run-id", "value": pred["scope"]["runId"], "ns": NORMATIVE_URI},
                    {"name": "lossy-notice", "value": LOSSY_NOTICE, "ns": NORMATIVE_URI},
                ],
            },
            "import-ap": {"href": f"{NORMATIVE_URI}#{pred['scope']['runId']}"},
            "results": [
                {
                    "uuid": _uuid_for("result", pred["scope"]["runId"]),
                    "title": "Coverage declaration",
                    "description": LOSSY_NOTICE,
                    "start": pred["timeVerified"],
                    "reviewed-controls": {
                        "control-selections": [{"exclude-controls": excluded}]
                    },
                    "observations": observations,
                    "findings": findings,
                }
            ],
        }
    }


def _uuid_for(*parts: str) -> str:
    """A UUIDv5-shaped identifier **derived from the content**, never generated.

    `uuid4()` here would make every projection differ from its own re-derivation, and
    `test_det__projections_are_byte_identical` puts both projections in `make determinism`'s
    comparison set precisely because *a lossy projection that is also non-deterministic is a second
    artifact a consumer could diff and mis-read.*
    """
    import hashlib

    h = hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()
    return f"{h[:8]}-{h[8:12]}-5{h[13:16]}-a{h[17:20]}-{h[20:32]}"
