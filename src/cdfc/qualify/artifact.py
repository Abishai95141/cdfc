"""The qualification result, persisted. **The funnel stops being a markdown table.**

`tools/measure/p7_attrition.py` has computed the five-gate attrition since P7 and written it to
`docs/measurements/P7-attrition.md`. A human can read that; a screen cannot. This module is the
structured form of the same computation, and it is deliberately produced *by the same call* — the
tool builds one `QualificationArtifact` and renders both the markdown and the JSON from it, so the
published table and the served payload cannot disagree about a number.

## Why the artifact is committed rather than regenerated on demand

`reports/*` is gitignored except where a gate reads it, and this is one of those places. The
alternative — re-running qualification when a client asks for `/v1/rejections` — would put a
27-second mutation-campaign join behind an HTTP GET, and worse, it would make the API a thing that
*computes* verdicts rather than serves them. `cdfc.api.store` is read-only for exactly this reason.

## The four-state stage, and why `NOT RUN` is not `skipped`

`surface.funnel.FunnelStage` distinguishes *skipped* (the gate ran and declared itself
inapplicable) from *survived*. This module adds the third absence: a gate that **was never
executed**. G3e and G4 are in that state in every campaign this repo has run, and the difference
matters —

* `NOT RUN`      — the gate did not execute. Nothing is known about these candidates from it.
* `NOT APPLICABLE` — the gate executed and declared itself inapplicable to every candidate.
* `0 rejected`   — the gate executed, applied, and rejected nobody.

Collapsing the first into the third is how a funnel reports a stage that passed everything, which
is a vacuous pass wearing a funnel row. Collapsing it into the second claims the gate made a
determination it never made.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from cdfc.surface.funnel import FunnelStage, ObligationCoverage
from cdfc.surface.funnel import RejectionRow as SurfaceRejectionRow

ARTIFACT_PATH: Final[Path] = Path("reports/qualification/qualification.json")

SCHEMA_VERSION: Final[int] = 2

# The generated stage that precedes every gate. Not a gate; a census of what entered.
GENERATED: Final[str] = "generated"


class ArtifactNotOnDisk(FileNotFoundError):
    """No qualification artifact. **Not served as an empty library.**

    An empty predicate library and an unmeasured one render identically to a reader and mean
    opposite things: the first says the gates rejected everything, the second says nobody ran them.
    """


class ArtifactSchemaMismatch(ValueError):
    """The artifact on disk was written by a different schema version."""


@dataclass(frozen=True, slots=True)
class Rejection:
    """One refused candidate, **with the number that decided it.**

    `measured` is the rejecting gate's own mapping, written verbatim. It is not summarised into a
    sentence here: the Rejected screen is the one place this product proves its gate is real, and a
    rejection reduced to prose is an opinion with a gate's name on it.
    """

    candidate_id: str
    candidate_sha256: str
    obligation_id: str
    gate: str
    reason: str
    measured: dict[str, Any]
    cells_would_have_covered: int
    harvest_class: str
    remedy: str

    def headline(self) -> str:
        """The single number a reader scans the column for. Never empty — the row would not exist.

        Preference order is the order in which a number *decides* the gate: an explicit kill rate,
        then whatever scalar the gate recorded. A row with no scalar at all renders the mapping's
        first key rather than a blank, because `surface.funnel.RejectionRow` refuses a rejection
        whose measured string is empty.
        """
        m = self.measured
        for k in ("kr_claimed", "kr_all_classes", "marker_recall", "false_failure_rate"):
            v = m.get(k)
            if v not in (None, ""):
                return f"{k} = {v}"
        for k, v in sorted(m.items()):
            if isinstance(v, (str, int, float)) and v not in (None, ""):
                return f"{k} = {v}"
        return f"{self.gate} rejected with reason {self.reason}"


@dataclass(frozen=True, slots=True)
class Stage:
    """A funnel stage plus the one thing `FunnelStage` cannot express: *the gate did not run.*"""

    name: str
    entered: int
    skipped: int
    survived: int
    rejected: int
    ran: bool
    reasons: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.ran:
            if self.skipped or self.survived or self.rejected:
                raise ValueError(
                    f"{self.name}: ran=False but the stage carries dispositions "
                    f"(skipped={self.skipped}, survived={self.survived}, rejected={self.rejected}). "
                    "A gate that did not execute made no determination about anybody."
                )
            return
        # The invariant lives in ONE place. Constructing the surface object is the assertion --
        # re-implementing `entered == skipped + survived + rejected` here would be a second copy
        # of the rule, and the copy that drifts is the one nobody is reading.
        FunnelStage(
            name=self.name, entered=self.entered, skipped=self.skipped, survived=self.survived,
            rejections=tuple(
                SurfaceRejectionRow(candidate_id=f"_{i}", gate=self.name, measured="counted",
                                    cells_it_would_have_covered=0)
                for i in range(self.rejected)
            ),
        )

    def render(self) -> str:
        if not self.ran:
            return f"{self.name}: NOT RUN — the gate was not executed in this campaign"
        if self.entered > 0 and self.skipped == self.entered:
            return f"{self.name}: NOT APPLICABLE — 0 evaluated"
        return (f"{self.name}: entered {self.entered} · skipped {self.skipped} · "
                f"survived {self.survived} · rejected {self.rejected}")


@dataclass(frozen=True, slots=True)
class QualificationArtifact:
    """Everything screens S-6, S-7 and S-8 render, and nothing they compute."""

    schema_version: int
    qualified_at: str
    campaign_id: str
    fault_model_version: str
    kill_bar: str
    instrument_label: str | None
    # G-EVAL's two arms, with each one's COMPUTED independence and — the field that earns its
    # place — what each arm is blind to even when it is green. Every kill rate in this programme
    # rests on *our evaluator reproduces the regulator's own values*, and a screen that shows the
    # rates without saying what the instrument cannot see is showing half a measurement.
    instrument_arms: tuple[dict[str, Any], ...]
    corpus_outcome: str
    corpus_census: dict[str, int]
    registry_root: str
    registry_rows: int
    registry_unsigned: int
    registry_signer: str
    obligation_statute: int | None
    obligation_template: int | None
    obligation_total: int
    stages: tuple[Stage, ...]
    rejections: tuple[Rejection, ...]
    library: tuple[dict[str, Any], ...]
    predicates_that_produced_runs: int
    ceiling_note: str

    def coverage(self) -> ObligationCoverage:
        return ObligationCoverage(
            with_statute_obligation=self.obligation_statute,
            with_template_obligation=self.obligation_template,
            total=self.obligation_total,
        )

    def to_wire(self) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "qualifiedAt": self.qualified_at,
            "campaignId": self.campaign_id,
            "faultModelVersion": self.fault_model_version,
            "killBar": self.kill_bar,
            "instrumentLabel": self.instrument_label,
            "instrumentArms": list(self.instrument_arms),
            "corpus": {"outcome": self.corpus_outcome, "census": self.corpus_census},
            "registry": {
                "root": self.registry_root, "rows": self.registry_rows,
                "unsigned": self.registry_unsigned, "signer": self.registry_signer,
            },
            "obligationCoverage": {
                "withStatuteObligation": self.obligation_statute,
                "withTemplateObligation": self.obligation_template,
                "total": self.obligation_total,
                "note": self.coverage().render(),
            },
            "funnel": [
                {"name": s.name, "entered": s.entered, "skipped": s.skipped,
                 "survived": s.survived, "rejected": s.rejected, "ran": s.ran,
                 "reasons": s.reasons, "render": s.render()}
                for s in self.stages
            ],
            "rejections": [
                {"candidateId": r.candidate_id, "candidateSha256": r.candidate_sha256,
                 "obligationId": r.obligation_id, "gate": r.gate, "reason": r.reason,
                 "measured": r.measured, "headline": r.headline(),
                 "cellsWouldHaveCovered": r.cells_would_have_covered,
                 "harvestClass": r.harvest_class, "remedy": r.remedy}
                for r in self.rejections
            ],
            "library": list(self.library),
            "predicatesThatProducedRuns": self.predicates_that_produced_runs,
            "ceilingNote": self.ceiling_note,
        }

    def write(self, path: Path = ARTIFACT_PATH) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_wire(), indent=1, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path


def from_wire(w: dict[str, Any]) -> QualificationArtifact:
    if w.get("schemaVersion") != SCHEMA_VERSION:
        raise ArtifactSchemaMismatch(
            f"artifact schema {w.get('schemaVersion')!r}, this build reads {SCHEMA_VERSION}. "
            "Re-run `make attrition`; an artifact from another schema is not silently coerced."
        )
    oc = w["obligationCoverage"]
    return QualificationArtifact(
        schema_version=w["schemaVersion"],
        qualified_at=w["qualifiedAt"],
        campaign_id=w["campaignId"],
        fault_model_version=w["faultModelVersion"],
        kill_bar=w["killBar"],
        instrument_label=w["instrumentLabel"],
        instrument_arms=tuple(w["instrumentArms"]),
        corpus_outcome=w["corpus"]["outcome"],
        corpus_census=w["corpus"]["census"],
        registry_root=w["registry"]["root"],
        registry_rows=w["registry"]["rows"],
        registry_unsigned=w["registry"]["unsigned"],
        registry_signer=w["registry"]["signer"],
        obligation_statute=oc["withStatuteObligation"],
        obligation_template=oc["withTemplateObligation"],
        obligation_total=oc["total"],
        stages=tuple(
            Stage(name=s["name"], entered=s["entered"], skipped=s["skipped"],
                  survived=s["survived"], rejected=s["rejected"], ran=s["ran"],
                  reasons=s.get("reasons", {}))
            for s in w["funnel"]
        ),
        rejections=tuple(
            Rejection(candidate_id=r["candidateId"], candidate_sha256=r["candidateSha256"],
                      obligation_id=r["obligationId"], gate=r["gate"], reason=r["reason"],
                      measured=r["measured"],
                      cells_would_have_covered=r["cellsWouldHaveCovered"],
                      harvest_class=r["harvestClass"], remedy=r["remedy"])
            for r in w["rejections"]
        ),
        library=tuple(w["library"]),
        predicates_that_produced_runs=w["predicatesThatProducedRuns"],
        ceiling_note=w["ceilingNote"],
    )


def load(path: Path = ARTIFACT_PATH) -> QualificationArtifact:
    """Read the artifact. **Raises when it is absent rather than returning an empty one.**"""
    if not path.is_file():
        raise ArtifactNotOnDisk(
            f"{path} is not on disk. The predicate library, the rejected-candidate list and the "
            "attrition funnel are all derived from it, and none of the three is served as an "
            "empty collection: an empty library says the gates rejected everything, an absent one "
            "says nobody ran them. Produce it with `make attrition`."
        )
    return from_wire(json.loads(path.read_text(encoding="utf-8")))
