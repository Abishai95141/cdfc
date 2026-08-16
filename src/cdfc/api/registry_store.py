"""The read-only view of the qualification artifact. **Screens 6, 7 and 8 read only this.**

`cdfc.api.store` is the same idea for runs: the API serves what is on disk and computes nothing.
The rule matters more here than there, because the thing on disk took a 27-second mutation-campaign
join to produce and re-deriving it inside a request handler would put the qualification pipeline
behind an HTTP GET.

## Every function here can refuse, and none of them returns `[]` on absence

`artifact.load()` raises `ArtifactNotOnDisk`. The handlers turn that into a **503 with the
remedy**, never a `200 []`:

* `200 []` says *the gates ran and admitted nobody* — which is TRUE today and is the product's
  most interesting single fact.
* An absent artifact says *nobody ran the gates*.

Those render identically to a reader and mean opposite things, so the distinction is carried on the
wire. It is the same rule `/unchecked` follows with `groups: null`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from cdfc.qualify import artifact

# At most this many rejections in one response. 348 rows carrying each gate's full `measured`
# mapping is ~600 KB of JSON; the cap is VISIBLE beside the total, exactly as `get_cells` does it,
# so a truncated list can never be read as a complete one.
REJECTION_PAGE: Final[int] = 100

ARTIFACT: Final[Path] = artifact.ARTIFACT_PATH


def load(path: Path = ARTIFACT) -> artifact.QualificationArtifact:
    return artifact.load(path)


def library_rows(art: artifact.QualificationArtifact) -> tuple[dict[str, Any], ...]:
    """The ADMITTED predicates. Empty today, and the emptiness is a measurement.

    Every one of the 348 harvested candidates was refused at G2, so `D-P4-01`'s rule — four
    predicate states, and `REJECTED` is not one of them — means none of them acquired a predicate
    id and none of them can appear here. The rows a reader wants are on `/v1/rejections`.
    """
    return tuple(art.library)


def library_context(art: artifact.QualificationArtifact) -> dict[str, Any]:
    """What must render BESIDE the rows, whether or not there are any.

    `predicatesThatProducedRuns` is the one a reader cannot be left to infer. A library reading
    *0 admitted* next to a report reading *1,898 settled* invites exactly one inference — that the
    settled count came from admitted predicates — and it did not: runs bind harvested candidates
    directly under `PRE-GATE`. The two populations are disjoint and the surface says so.
    """
    return {
        "admittedCount": len(art.library),
        "predicatesThatProducedRuns": art.predicates_that_produced_runs,
        "populationsAreDisjoint": True,
        "disjointNote": (
            f"{art.predicates_that_produced_runs} predicates produced settled cells in the runs on "
            f"disk and {len(art.library)} predicates are admitted through the five gates. These "
            "are different populations: a run binds harvested candidates directly under PRE-GATE. "
            "No settled count in this product rests on a gate-admitted predicate."
        ),
        "corpus": {"outcome": art.corpus_outcome, "census": art.corpus_census},
        "instrumentLabel": art.instrument_label,
        "instrumentArms": list(art.instrument_arms),
        "killBar": art.kill_bar,
        "campaignId": art.campaign_id,
        "faultModelVersion": art.fault_model_version,
        "qualifiedAt": art.qualified_at,
        "registry": {
            "root": art.registry_root, "rows": art.registry_rows,
            "unsigned": art.registry_unsigned, "signer": art.registry_signer,
        },
        "ceilingNote": art.ceiling_note,
    }


def rejected_rows(
    art: artifact.QualificationArtifact, *,
    gate: str | None = None, reason: str | None = None, q: str | None = None,
) -> tuple[dict[str, Any], ...]:
    """Every candidate a gate refused, **with the number that decided it.**

    Filtering is exact-match on `gate` and `reason` and substring on the candidate id, because the
    three are the only axes the screen offers. Nothing here sorts by a score: the rows are in
    candidate order, and re-ordering them by how badly each failed would invent a ranking the gates
    never produced.
    """
    rows = art.rejections
    if gate:
        rows = tuple(r for r in rows if r.gate.upper() == gate.upper())
    if reason:
        rows = tuple(r for r in rows if r.reason.lower() == reason.lower())
    if q:
        needle = q.lower()
        rows = tuple(r for r in rows
                     if needle in r.candidate_id.lower() or needle in r.harvest_class.lower())
    return tuple(
        {"candidateId": r.candidate_id, "candidateSha256": r.candidate_sha256,
         "obligationId": r.obligation_id, "gate": r.gate, "reason": r.reason,
         "headline": r.headline(), "measured": r.measured,
         "cellsWouldHaveCovered": r.cells_would_have_covered,
         "harvestClass": r.harvest_class, "remedy": r.remedy}
        for r in rows
    )


def facets(art: artifact.QualificationArtifact) -> dict[str, dict[str, int]]:
    """The counts behind the filter controls, so a filter chip can carry its own denominator."""
    by_gate: dict[str, int] = {}
    by_reason: dict[str, int] = {}
    by_class: dict[str, int] = {}
    for r in art.rejections:
        by_gate[r.gate] = by_gate.get(r.gate, 0) + 1
        by_reason[r.reason] = by_reason.get(r.reason, 0) + 1
        key = r.harvest_class or "(unclassified)"
        by_class[key] = by_class.get(key, 0) + 1
    return {"gate": dict(sorted(by_gate.items())),
            "reason": dict(sorted(by_reason.items())),
            "harvestClass": dict(sorted(by_class.items()))}


def funnel_stages(art: artifact.QualificationArtifact) -> tuple[dict[str, Any], ...]:
    """The five gates in GATE ORDER, three integers each, and the fourth state named.

    `ran: false` is NOT `skipped`. A gate that never executed made no determination about anybody,
    and rendering it as a stage that skipped everyone claims one it never made.
    """
    return tuple(
        {"name": s.name, "entered": s.entered, "skipped": s.skipped, "survived": s.survived,
         "rejected": s.rejected, "ran": s.ran, "reasons": s.reasons, "render": s.render(),
         "whollyNotApplicable": s.ran and s.entered > 0 and s.skipped == s.entered}
        for s in art.stages
    )


def obligation_pair(art: artifact.QualificationArtifact) -> dict[str, Any]:
    """TWO numbers, never one. A `null` pair is served as a pair of nulls, never as zeros."""
    return {
        "withStatuteObligation": art.obligation_statute,
        "withTemplateObligation": art.obligation_template,
        "total": art.obligation_total,
        "note": art.coverage().render(),
    }


HISTORY: Final[Path] = Path("reports/settled-history.jsonl")


class HistoryNotMeasured(FileNotFoundError):
    """No series on disk. **Not an empty chart** — that reads as *it has never moved*."""


def history(path: Path = HISTORY) -> tuple[dict[str, Any], ...]:
    """The settled fraction over time. **Nothing here sorts, clamps, smooths or takes a max.**

    The absence of those four operations is the feature, and `surface.history.history_points`
    re-asserts it: a decrease with no cause raises rather than rendering. The points are returned in
    FILE ORDER, which is event order — sorting by value would put every step-down at the end and
    turn a measurement into a ranking.
    """
    if not path.is_file():
        raise HistoryNotMeasured(
            f"{path} is absent. The settled-fraction chart is not served as an empty series: an "
            "empty chart and a chart that has never stepped down look identical and mean opposite "
            "things. Produce it with `make history`."
        )
    import json

    from cdfc.surface.history import HistoryPoint, history_points

    raw = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    points = history_points(tuple(
        HistoryPoint(at=r["at"], settled=r["settled"], field_surface=r["fieldSurface"],
                     admission=r["admission"], cause=r.get("cause"))
        for r in raw
    ))
    return tuple(
        {"at": p.at, "settled": p.settled, "fieldSurface": p.field_surface,
         "admission": p.admission, "cause": p.cause,
         "runId": r.get("runId"),
         "steppedDown": bool(prev is not None and p.settled < prev.settled),
         "delta": (p.settled - prev.settled) if prev is not None else None}
        # `strict=True` on all three: the previous form paired `(None, *points)` against `points`
        # and raised, which the handler surfaced as a 500 rather than serving a short series. That
        # is the right failure mode and it is why the flag is here — a lenient zip would have
        # dropped the last point, and the last point is the step-down.
        for prev, p, r in zip((None, *points[:-1]), points, raw, strict=True)
    )


CHURN: Final[Path] = Path("reports/churn/fy2029-30.json")


class ChurnNotSwept(FileNotFoundError):
    """No sweep on disk. **Not served as *nothing moved*.**"""


def churn(path: Path = CHURN) -> dict[str, Any]:
    """The persisted template-bump sweep. Read, never recomputed.

    Recomputing it here would give the API its own opinion about which predicates stopped settling,
    and the chart, the report and the wire would then be three answers to one question.
    """
    import json

    if not path.is_file():
        raise ChurnNotSwept(
            f"{path} is absent. The sweep is not served as *no predicate moved*: an unmeasured "
            "template bump and a bump that moved nobody are different facts. Produce it with "
            "`make history`."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def registry_roots(art: artifact.QualificationArtifact) -> tuple[dict[str, Any], ...]:
    """The batch root, with its signer. **`UNSIGNED` is a literal signer, not a missing field.**

    No signer exists in this repository, so the batch is admitted visibly weaker rather than
    silently: every surface renders `UNSIGNED BATCH` beside the count.
    """
    return ({
        "root": art.registry_root,
        "rows": art.registry_rows,
        "unsigned": art.registry_unsigned,
        "signer": art.registry_signer,
        "badge": "UNSIGNED BATCH" if art.registry_unsigned or not art.registry_rows else "",
        "campaignId": art.campaign_id,
        "qualifiedAt": art.qualified_at,
    },)
