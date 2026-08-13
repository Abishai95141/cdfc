"""P7-B2 — the deterministic proviso detector, versioned, with its recall MEASURED not assumed.

**Two things to say plainly.**

**(a) A regex over statutory prose is the right tool and is not what `ci/no-regex-over-xml.sh`
forbids.** That gate scans `src/cdfc/ingest/` and `src/cdfc/schema/` and exists because a lexical
matcher over a structured format is a build error — `<f[ >][^>]*>` over OOXML returned a CORRECT
COUNT with WRONG BODIES. Normative prose is not a structured format; there is no parser to prefer.

**(b) THE DETECTOR'S RECALL IS BELOW 1, AND AN UNMEASURED RECALL IS THE INSTRUMENT THIS PROJECT
REFUSES TO SHIP.** So `recall()` reads `fixtures/predicates/proviso-labels.json` — spans labelled
by a NAMED person on a DATED day — and returns two integers. It never returns a rate.

**And the consequence, which is the part with teeth: while the labelled set is empty, G0 REFUSES a
`source == STATUTE` candidate** with `ProvisoRecallUnmeasured` rather than passing it on an
unmeasured detector. The labelled set is empty today for the reason in D-P7-01: there is no
statutory instrument in this repository to label spans of. **Zero STATUTE candidates exist, so
nothing is blocked — and the moment one exists, it is blocked until somebody labels.**

**The marker list is LEXICAL and VERSIONED.** `MARKERS_VERSION` enters `qualification.g0`, so a
predicate qualified under `v1` is not silently re-qualified when the list grows. Matching is
case-insensitive at a word boundary, which is a declared property of the version and is recorded in
`docs/PROVISO-MARKERS-v1.md` beside what it deliberately does not do.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

MARKERS_VERSION: Final[str] = "v1"

LABELS_PATH: Final[Path] = Path("fixtures/predicates/proviso-labels.json")

ProvisoKind = Literal["proviso", "exception", "cross_reference", "explanation", "delegation"]


class ProvisoRecallUnmeasured(RuntimeError):
    """A `source == STATUTE` candidate reached G0 while the detector's recall is unmeasured.

    A detector whose recall nobody has measured cannot distinguish *"this clause has no proviso"*
    from *"we did not see the proviso it has"*, and G0's whole job at that point is the first of
    those. Refusing is the only honest outcome; passing would be scope truncation performed by the
    gate that exists to catch scope truncation.
    """


@dataclass(frozen=True, slots=True)
class Marker:
    pattern: str
    kind: ProvisoKind
    exemplar: str  # a phrase this marker must match, asserted in the unit tests
    note: str = ""


# The fifteen markers of `v1`, for Indian statutory drafting. Order is presentation order; the
# detector reports every match, and OVERLAPS ARE KEPT — "Provided further that" is a different
# fact from "Provided that", and collapsing them would under-count the provisos in a clause that
# carries several.
MARKERS: Final[tuple[Marker, ...]] = (
    Marker(r"\bProvided\s+further\s+that\b", "proviso", "Provided further that the Authority may"),
    Marker(r"\bProvided\s+also\s+that\b", "proviso", "Provided also that no fee shall"),
    Marker(r"\bProvided\s+that\b", "proviso", "Provided that the scheme is close-ended"),
    Marker(r"\bNotwithstanding\b", "exception", "Notwithstanding anything contained in regulation 12"),
    Marker(r"\bsubject\s+to\b", "exception", "subject to such conditions as may be specified"),
    Marker(r"\bexcept\b", "exception", "except where the scheme is exempt"),
    Marker(r"\bunless\b", "exception", "unless the Authority directs otherwise"),
    Marker(r"\bsave\s+as\b", "exception", "save as otherwise provided"),
    Marker(r"\bExplanation\b", "explanation", "Explanation - For the purposes of this regulation"),
    Marker(r"\bin\s+such\s+manner\s+as\s+specified\s+by\s+the\s+Authority\b", "delegation",
           "in such manner as specified by the Authority",
           note="the reg 51(1) delegation hook: the obligation is GENUINELY UNDERSPECIFIED and "
                "the right output is NO_PREDICATE(no_obligation_specified), kept strictly apart "
                "from not_yet_synthesised"),
    Marker(r"\bas\s+may\s+be\s+specified\b", "delegation", "as may be specified by the Authority"),
    Marker(r"\bregulation\s+\d+\b", "cross_reference", "regulation 51"),
    Marker(r"\bsub-regulation\s+\(\d+\)", "cross_reference", "sub-regulation (2)"),
    Marker(r"\bclause\s+\([A-Za-z0-9]+\)", "cross_reference", "clause (a)"),
    Marker(r"\bSchedule\b", "cross_reference", "as set out in Schedule II"),
)

_COMPILED: Final[tuple[tuple[re.Pattern[str], Marker], ...]] = tuple(
    (re.compile(m.pattern, re.IGNORECASE), m) for m in MARKERS
)


@dataclass(frozen=True, slots=True)
class DetectedProviso:
    kind: ProvisoKind
    text: str
    span: tuple[int, int]  # absolute, into the instrument's normalised text
    marker: str  # the pattern that matched, for auditability


def detect(
    span_text: str, offset: int, markers_version: str = MARKERS_VERSION
) -> tuple[DetectedProviso, ...]:
    """Every marker match in `span_text`, with spans shifted to the instrument's coordinates.

    `offset` is not optional and has no default: a proviso reported at a span relative to a clause
    is a span a reader cannot open, and the whole point of this phase is that an offset resolves.
    """
    if markers_version != MARKERS_VERSION:
        raise ValueError(
            f"marker list {markers_version!r} is not the pinned version {MARKERS_VERSION!r}. The "
            "version enters qualification.g0, so a predicate qualified under one list is not "
            "silently re-qualified under another."
        )
    out: list[DetectedProviso] = []
    for pattern, m in _COMPILED:
        for hit in pattern.finditer(span_text):
            out.append(
                DetectedProviso(
                    kind=m.kind,
                    text=hit.group(0),
                    span=(offset + hit.start(), offset + hit.end()),
                    marker=m.pattern,
                )
            )
    return tuple(sorted(out, key=lambda d: (d.span, d.marker)))


# --- recall, and the refusal that follows from it -----------------------------------------


@dataclass(frozen=True, slots=True)
class Recall:
    """TWO INTEGERS AND A PROVENANCE, never a rate.

    `labeller` and `labelled_at` are inside the record because a recall figure with no named
    person and no date is a number somebody produced and nobody stands behind.
    """

    detected: int
    labelled: int
    labeller: str | None
    labelled_at: str | None
    reason_if_absent: str = ""

    @property
    def measured(self) -> bool:
        return self.labelled > 0 and bool(self.labeller) and bool(self.labelled_at)

    def render(self) -> str:
        if not self.measured:
            return (
                f"g0_marker_recall = NOT MEASURED ({self.detected} / {self.labelled} labelled "
                f"spans) — {self.reason_if_absent}"
            )
        return (
            f"g0_marker_recall = {self.detected} / {self.labelled} "
            f"(labelled by {self.labeller}, {self.labelled_at})"
        )


def recall(path: Path | None = None) -> Recall:
    """Run the detector over the hand-labelled spans and report both integers.

    A labelled span records the marker text a person found. Recall is *how many of those the
    detector also finds* — so a labelled span the detector misses is the finding, and the number is
    the deliverable rather than a threshold.
    """
    path = path or LABELS_PATH
    if not path.is_file():
        return Recall(0, 0, None, None, reason_if_absent=f"{path} does not exist")
    doc = json.loads(path.read_text(encoding="utf-8"))
    spans: Sequence[dict] = doc.get("spans") or ()
    if not spans:
        return Recall(0, 0, doc.get("labeller"), doc.get("labelled_at"),
                      reason_if_absent=doc.get("reason_if_absent", "no spans are labelled"))
    hits = 0
    for s in spans:
        found = detect(s["text"], 0)
        if any(d.kind == s["kind"] for d in found):
            hits += 1
    return Recall(hits, len(spans), doc.get("labeller"), doc.get("labelled_at"))


def assert_measured_for_statute(path: Path | None = None) -> Recall:
    """The refusal. Called by G0 for every `source == STATUTE` candidate and by nothing else.

    `path` is resolved at CALL time rather than bound as a default, so `LABELS_PATH` can be
    redirected. A default argument evaluated at import is a path a test cannot move, and a guard
    nobody can point at a different fixture is a guard with one input for ever.
    """
    path = path or LABELS_PATH
    r = recall(path)
    if not r.measured:
        raise ProvisoRecallUnmeasured(
            f"a STATUTE obligation reached G0 while the proviso detector's recall is unmeasured: "
            f"{r.render()}. A detector whose recall nobody has measured cannot tell "
            "'this clause has no proviso' from 'we did not see the proviso it has', and the first "
            "of those is exactly what G0 is being asked. Label spans in "
            f"{path} — a named person, a date — before a statutory obligation is gated."
        )
    return r
