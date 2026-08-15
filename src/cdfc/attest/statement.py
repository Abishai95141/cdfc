"""P11-B1 — the in-toto Statement v1, and the fields that are absent by design.

**The top-level object of the predicate is `scope`. There is no `result`, no `status` and no `pass`
field at any depth, and there never will be.** That is not a naming preference; it is the only
version of *"this system cannot render an all-clear"* that is a property of the artifact rather than
of whoever last edited a template. `tests/contract/schema_walk.py` walks the schema and enforces it
at every depth, through every combinator.

## The subject is BOTH documents

`subject[] = filing ⊕ template`, because **a verdict against template v3 is meaningless if the
entity filed on v4**. An attestation naming only the filing is a statement whose meaning depends on
something it does not carry.

## `NONE ≠ NOASSERTION ≠ absent`

- `[]` means *we determined there are none*
- `null` means *we make no claim*
- an **omitted** field is a violation the validator rejects

Three states, three encodings, and the schema enforces all three. SPDX's `NOASSERTION` collapse —
one token for *"we looked and found nothing"* and *"we did not look"* — is the failure this rule
exists to avoid, and it is the single most-cited example in this project's own design record.

## `settledFraction` on an `INVALID` run — PRESENT and `null` (adversary F24)

Three documents asserted three different things about one field in one state: `plan/03` P5-B4
returns `SettledFraction | None` (present, `null`); an earlier contract test said the schema
**forbids** the property; `plan/01` §1.9 says an **omitted** field is a violation. Those are three
different things, and P5 and P11 each passed their own test while the integration produced an
attestation that either failed validation or dropped the `null` that `E2E-INVALID` exists to assert.

> **RULING: on `INVALID`, `settledFraction` is PRESENT and `null`. Same for `verdict`.**
>
> The plan's own `NONE ≠ NOASSERTION ≠ absent` rule already fixes the meanings, and **`INVALID` is
> precisely the state in which we make no claim** — so `null` is the only value that says the true
> thing. Forbidding the property would make the one state we most need to express indistinguishable
> from a malformed statement. **Zero is a finding about the filing; `null` is a finding about us;
> absence is a bug.**

## The four statements are REQUIRED FIELDS, not template strings

Making a disclaimer a mandatory field rather than a string in a renderer is the cheapest possible
way to guarantee it survives contact with a marketing page. A template can be edited by anyone; a
`required` in a JSON Schema fails the build.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from cdfc.attest.policy import expires_for
from cdfc.canon import canonical_json, sha256_hex

STATEMENT_TYPE: Final[str] = "https://in-toto.io/Statement/v1"
PREDICATE_TYPE: Final[str] = "https://cdfc.dev/filing-settlement-attestation/v1"

# The four statements, verbatim, as REQUIRED fields. Their text is here so one edit changes every
# surface, and their presence is enforced by the schema so no edit can remove them.
STATEMENTS: Final[Mapping[str, str]] = {
    "boundedSilence": (
        "Silence in this document is BOUNDED, not general. Every cell this system did not settle "
        "is counted and named with the reason it was not settled. A field absent from the findings "
        "is not a field that passed."
    ),
    "purpose": (
        "This is a coverage declaration for a pre-submission self-check. It states what was "
        "checked and what was not. It does not state that the filing is correct, and it is not an "
        "audit opinion, an assurance engagement, or a regulatory clearance."
    ),
    "summaryIsNotSubstitute": (
        "Any summary, projection or excerpt of this statement is LOSSY by construction. The "
        "normative artifact is this attestation and the run record it names; a reader acting on a "
        "smaller document is acting on less than the evidence."
    ),
    "detectionBoundary": (
        "The residue this statement carries is the measured count of constructed falsehoods that "
        "no admitted check rejects. It is a lower bound on what this instrument cannot see, not an "
        "upper bound, because it is measured against one declared fault model."
    ),
}

# **`livenessProof` is the reason there is anything to sign.** An attestation without it is a
# statement about a filing produced by an instrument nobody demonstrated was working.
REQUIRED_PREDICATE_KEYS: Final[tuple[str, ...]] = (
    "scope", "runState", "invalidCauses", "settledFraction", "verdict",
    "livenessProof", "residue", "counterEvidence", "falseFailureRate",
    "corpusProvenance", "statements", "assessor", "manifest",
    "timeVerified", "expires", "openItems",
)

# The eight pins `verify` re-runs the pipeline against, plus the two run-level INPUTS the probe and
# attestation layers added. Named here so `verify` and the builder read one list.
MANIFEST_PINS: Final[tuple[str, ...]] = (
    "template_sha256", "filing_sha256", "registry_root", "register_snapshot_sha256",
    "code_git_sha", "evaluator_version", "fault_model_version", "tool_versions",
)
MANIFEST_RUN_INPUTS: Final[tuple[str, ...]] = ("probe_seed", "timeVerified")


class StatementError(ValueError):
    """A statement that must not be built. Never a warning."""


@dataclass(frozen=True, slots=True)
class Subject:
    name: str
    sha256: str

    def as_obj(self) -> dict[str, Any]:
        return {"name": self.name, "digest": {"sha256": self.sha256}}


@dataclass(frozen=True, slots=True)
class Statement:
    """The whole predicate. Every field is either a value or an explicit `null`; none is optional."""

    subjects: tuple[Subject, ...]
    scope: Mapping[str, Any]
    run_state: str
    invalid_causes: tuple[str, ...]
    settled_fraction: Mapping[str, Any] | None
    verdict: Mapping[str, Any] | None
    liveness_proof: Mapping[str, Any] | None
    residue: Mapping[str, Any] | None
    counter_evidence: tuple[Mapping[str, Any], ...]
    false_failure_rate: Mapping[str, Any] | None
    corpus_provenance: str
    assessor: Mapping[str, Any]
    manifest: Mapping[str, Any]
    time_verified: str
    open_items: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if len(self.subjects) < 2:
            raise StatementError(
                "the subject is BOTH the filing and the template. A verdict against template v3 is "
                "meaningless if the entity filed on v4, so a statement naming one document is a "
                "statement whose meaning depends on something it does not carry."
            )
        if self.run_state not in ("VALID", "INVALID"):
            raise StatementError(f"runState {self.run_state!r} is not VALID or INVALID")
        if self.run_state == "INVALID":
            # F24. PRESENT and null — not forbidden, not omitted.
            if self.settled_fraction is not None or self.verdict is not None:
                raise StatementError(
                    "an INVALID run carries settledFraction: null and verdict: null. INVALID is "
                    "precisely the state in which we make no claim, and a number here would be a "
                    "claim. Zero is a finding about the filing; null is a finding about us."
                )
            if not self.invalid_causes:
                raise StatementError(
                    "an INVALID run with no cause is a refusal nobody can act on"
                )
        elif self.invalid_causes:
            raise StatementError("a VALID run carries no invalid cause")

    @property
    def expires(self) -> str:
        """Derived from `timeVerified`. **Reads no clock** — see `attest/policy.py`."""
        return expires_for(self.time_verified)

    def as_predicate(self) -> dict[str, Any]:
        return {
            "scope": dict(self.scope),
            "runState": self.run_state,
            "invalidCauses": list(self.invalid_causes),
            "settledFraction": None if self.settled_fraction is None else dict(self.settled_fraction),
            "verdict": None if self.verdict is None else dict(self.verdict),
            "livenessProof": None if self.liveness_proof is None else dict(self.liveness_proof),
            "residue": None if self.residue is None else dict(self.residue),
            "counterEvidence": [dict(c) for c in self.counter_evidence],
            "falseFailureRate": None if self.false_failure_rate is None else dict(self.false_failure_rate),
            "corpusProvenance": self.corpus_provenance,
            "statements": dict(STATEMENTS),
            "assessor": dict(self.assessor),
            "manifest": dict(self.manifest),
            "timeVerified": self.time_verified,
            "expires": self.expires,
            "openItems": [dict(o) for o in self.open_items],
        }

    def as_obj(self) -> dict[str, Any]:
        return {
            "_type": STATEMENT_TYPE,
            "subject": [s.as_obj() for s in self.subjects],
            "predicateType": PREDICATE_TYPE,
            "predicate": self.as_predicate(),
        }

    def canonical(self) -> bytes:
        return canonical_json(self.as_obj())

    def digest(self) -> str:
        return sha256_hex(self.canonical())


def from_run(
    result: Any,
    *,
    template_sha256: str,
    template_name: str,
    filing_name: str,
    manifest: Mapping[str, Any],
    time_verified: str,
    residue: Mapping[str, Any] | None = None,
    counter_evidence: Sequence[Mapping[str, Any]] = (),
    assessor: Mapping[str, Any] | None = None,
    open_items: Sequence[Mapping[str, Any]] = (),
) -> Statement:
    """Build the statement from a `RunResult`. **Nothing here reads a clock.**

    `falseFailureRate` is `null` with `corpusProvenance: "SELF-AUTHORED"` on G-CORPUS's FAIL branch,
    which is this build's branch — a *schema* requirement rather than a rendering one, and the
    reason P8's outcome had to be settled before the first envelope could be signed.
    """
    from cdfc.verdict.settled_fraction import serialise

    part = getattr(result, "partition", None)
    fraction = getattr(result, "fraction", None)
    invalid = tuple(str(c) for c in getattr(result, "invalid_causes", ()))
    liveness = getattr(result, "liveness", None)

    payload = serialise(fraction)
    settled = None if fraction is None else {
        "settled": payload["settledFraction"]["settled"] if isinstance(payload.get("settledFraction"), dict)
        else None,
        **{k: v for k, v in payload.items() if k != "settledFraction"},
        "value": None if payload.get("settledFraction") is None else str(payload["settledFraction"]),
    }
    if fraction is not None:
        settled = {
            "settled": int(fraction.settled.total),
            "inScope": int(fraction.inScope),
            "cellsTotal": int(fraction.cellsTotal),
            "denominatorWarning": str(fraction.denominatorWarning),
            "admissibilityCaveat": str(fraction.admissibilityCaveat or ""),
        }

    return Statement(
        subjects=(
            Subject(name=filing_name, sha256=result.filing_sha256),
            Subject(name=template_name, sha256=template_sha256),
        ),
        scope={
            "fieldSurface": None if part is None else int(part.cellsTotal),
            "inScope": None if part is None else int(part.inScope),
            "outOfScope": None if part is None else int(part.outOfScope),
            "outOfScopeRetained": None if part is None else int(part.outOfScopeRetained),
            "runId": result.run_id,
        },
        run_state=result.run_state,
        invalid_causes=invalid,
        settled_fraction=settled if result.run_state == "VALID" else None,
        verdict=(
            {"state": "SETTLEMENT_DECLARED"} if result.run_state == "VALID" else None
        ),
        liveness_proof=None if liveness is None else liveness.as_liveness_proof(),
        residue=None if residue is None else dict(residue),
        counter_evidence=tuple(dict(c) for c in counter_evidence),
        # G-CORPUS's FAIL branch. `null` and NOT zero: a rate of zero would be a claim.
        false_failure_rate=None,
        corpus_provenance="SELF-AUTHORED",
        assessor=dict(assessor or {"id": "cdfc", "thirdParty": False}),
        manifest=dict(manifest),
        time_verified=time_verified,
        open_items=tuple(dict(o) for o in open_items),
    )
