"""P7-B2 — G0, scope faithfulness. The free structural gate, and it runs for real over everything.

**The question G0 asks.** *Does this predicate faithfully implement the relation it claims to
implement, and is that relation present in the artifact it cites, at the offset recorded?*

**F9 — there is no skip.** Every candidate has exactly one G0 disposition drawn from the closed
reason set below, resolved against **its own** `instrument_id`: the regulation's normalised text
for `source == STATUTE`, the pinned blank's `template_instrument.emit()` for `source == TEMPLATE`.
The rejected alternative — a `SKIPPED_NOT_APPLICABLE` branch for clause-less candidates — made
stage one of the funnel read `N → N`, *a constant wearing the shape of a measurement*, and a gate
stage that cannot fail is this product's own failure mode wearing a gate's clothes.

**Seven closed reasons, and each implies a different remedy** — which is the admission test for a
reason code. `check()` raises `UnsourcedObligationError` rather than returning an eighth outcome,
so a future predicate kind cannot enter the funnel by defaulting into a pass.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from cdfc.predicates.obligations import ObligationSource, ObligationTable
from cdfc.qualify.errors import SuspiciousUniformityError, UnsourcedObligationError
from cdfc.qualify.instruments import InstrumentNotFound, InstrumentStore
from cdfc.qualify.provisos import (
    MARKERS_VERSION,
    DetectedProviso,
    assert_measured_for_statute,
    detect,
)
from cdfc.qualify.result import GateId, GateOutcome
from cdfc.qualify.textsource import Corroboration


class Reason:
    QUOTE_NOT_LOCATED: Final[str] = "g0.quote_not_located"
    QUOTE_AMBIGUOUS: Final[str] = "g0.quote_ambiguous"
    SPAN_MISMATCH: Final[str] = "g0.span_mismatch"
    PROVISO_UNDISPOSED: Final[str] = "g0.proviso_undisposed"
    PROVISO_ARITHMETIC: Final[str] = "g0.proviso_arithmetic"
    DECLARED_PROVISO_MISSING_EMISSION: Final[str] = "g0.declared_proviso_missing_emission"
    QUOTE_IN_DISPUTED_REGION: Final[str] = "g0.quote_in_disputed_region"


CLOSED_REASONS: Final[tuple[str, ...]] = (
    Reason.QUOTE_NOT_LOCATED,
    Reason.QUOTE_AMBIGUOUS,
    Reason.SPAN_MISMATCH,
    Reason.PROVISO_UNDISPOSED,
    Reason.PROVISO_ARITHMETIC,
    Reason.DECLARED_PROVISO_MISSING_EMISSION,
    Reason.QUOTE_IN_DISPUTED_REGION,
)

# The remedy for each, because a reason whose remedy is the same as another's is not a second
# reason. Rendered into the attrition page beside every rejection.
REMEDY: Final[Mapping[str, str]] = {
    Reason.QUOTE_NOT_LOCATED: "fix the quote — zero model cost, at the boundary",
    Reason.QUOTE_AMBIGUOUS: "widen the quote or fix the span; `find` succeeding is not locating "
                            "deterministically",
    Reason.SPAN_MISMATCH: "the span and the quote disagree; one of them is a lie",
    Reason.PROVISO_UNDISPOSED: "implement the branch or declare what it emits",
    Reason.PROVISO_ARITHMETIC: "the record does not sum; it is not a record",
    Reason.DECLARED_PROVISO_MISSING_EMISSION: "a declaration that emits nothing is a silent drop "
                                              "wearing a label",
    Reason.QUOTE_IN_DISPUTED_REGION: "re-quote from an agreed region, or accept that this "
                                     "obligation is not addressable and record it",
}


@dataclass(frozen=True, slots=True)
class G0Measured:
    """Everything G0 computed, written verbatim into `qualification.g0`."""

    instrument_id: str
    obligation_source: str
    occurrences: int
    span: tuple[int, int]
    corroboration: str
    provisos_total: int
    provisos_implemented: int
    provisos_declared: int
    markers_version: str
    recall: str

    def as_mapping(self) -> Mapping[str, object]:
        return {
            "instrument_id": self.instrument_id,
            "obligation_source": self.obligation_source,
            "occurrences": self.occurrences,
            "span": list(self.span),
            # D-P7-02: a pass over an uncorroborated construct says so, rather than looking like a
            # pass over a corroborated one.
            "corroboration": self.corroboration,
            "provisos_total": self.provisos_total,
            "provisos_implemented": self.provisos_implemented,
            "provisos_declared": self.provisos_declared,
            "markers_version": self.markers_version,
            "g0_marker_recall": self.recall,
        }


def check(cand: Any, obligations: ObligationTable, store: InstrumentStore) -> GateOutcome:
    """One candidate, one G0 disposition. Never a skip, never a seventh outcome."""
    oid = getattr(cand, "obligation_id", None)
    source = getattr(cand, "obligation_source", None)
    if not oid or not source:
        raise UnsourcedObligationError(
            f"{getattr(cand, 'id', cand)!r}: no obligation_id or no obligation_source. There is "
            "no skip at G0 — a candidate that cannot be gated is not a candidate that passes."
        )
    o = obligations[oid]
    if o.source.value != source:
        raise UnsourcedObligationError(
            f"{cand.id}: the envelope declares obligation_source={source!r} and the obligations "
            f"table says {o.source.value!r}. Two answers to one question is not a gate input."
        )
    try:
        it = store.get(o.instrument_id)
    except InstrumentNotFound as e:
        raise UnsourcedObligationError(
            f"{cand.id}: obligation {oid} names instrument {o.instrument_id!r}, which is not "
            "pinned. It does not resolve against an empty string — it does not resolve at all."
        ) from e

    recall_line = "n/a — TEMPLATE obligations carry no prose to detect provisos in"
    provisos: tuple[DetectedProviso, ...] = ()
    if o.source is ObligationSource.STATUTE:
        recall_line = assert_measured_for_statute().render()
        provisos = detect(o.quote, o.span[0])

    unit = it.unit_at(o.span)
    corroboration = unit.corroboration.value if unit else Corroboration.DISPUTED.value

    def measured(**over: object) -> Mapping[str, object]:
        base = G0Measured(
            instrument_id=o.instrument_id,
            obligation_source=o.source.value,
            occurrences=len(it.find_all(o.quote)),
            span=o.span,
            corroboration=corroboration,
            provisos_total=len(provisos),
            provisos_implemented=_disposed(cand, "IMPLEMENTED"),
            provisos_declared=_disposed(cand, "DECLARED"),
            markers_version=MARKERS_VERSION,
            recall=recall_line,
        ).as_mapping()
        return {**base, **over}

    def reject(reason: str, **over: object) -> GateOutcome:
        return GateOutcome(gate=GateId.G0, passed=False, measured=measured(**over), reason=reason)

    # --- 1. the span must be addressable at all -------------------------------------------
    # FIRST, because a span inside a disputed region has no authoritative reading and every
    # question below would be asked of one party's opinion.
    if it.is_disputed(o.span):
        return reject(Reason.QUOTE_IN_DISPUTED_REGION)

    # --- 2. the quote must be present ------------------------------------------------------
    occurrences = it.find_all(o.quote)
    if not occurrences:
        return reject(Reason.QUOTE_NOT_LOCATED)

    # --- 3. locating must be DETERMINISTIC -------------------------------------------------
    # `find` succeeding is not locating deterministically. A quote occurring more than once is
    # admitted only when the declared span selects one of the occurrences.
    #
    # **ORDER MATTERS AND THE FIRST DRAFT HAD IT WRONG.** With `span_mismatch` checked first,
    # `quote_ambiguous` was UNREACHABLE: `find_all` returns every offset where the text matches,
    # so `text[span] == quote` implies `span in occurrences`, and a span that selects no
    # occurrence always fails the slice test too. A reason code that cannot be reached is a
    # remedy nobody is ever offered. The two are kept apart because the remedies differ — a
    # unique quote with a wrong span is fixed by fixing the span; a repeated quote with a wrong
    # span may need a WIDER QUOTE, because one occurrence cannot be named by that text alone.
    if len(occurrences) > 1 and o.span not in occurrences:
        return reject(Reason.QUOTE_AMBIGUOUS)

    # --- 4. the span and the quote must agree ----------------------------------------------
    if it.text[o.span[0] : o.span[1]] != o.quote:
        return reject(Reason.SPAN_MISMATCH)

    # --- 5. every DETECTED proviso must be covered by a recorded disposition ----------------
    # Matched by TEXT, not by count. Two records and one detection is a different finding from
    # zero records and one detection, and only the second is an undisposed proviso.
    recorded = _provisos_of(cand)
    uncovered = [d for d in provisos if not any(d.text in (p.text or "") for p in recorded)]
    if uncovered:
        return reject(Reason.PROVISO_UNDISPOSED,
                      undisposed=len(uncovered),
                      detected=[d.text for d in provisos])

    # --- 6. and the record must SUM ---------------------------------------------------------
    # `provisos_total` is what the DETECTOR found; the two buckets are what the record disposes
    # of. They must agree. This fires where rule 5 cannot: a record that disposes of more provisos
    # than exist, or one carrying a disposal outside the closed set — in `total` and in neither
    # bucket. The record does not sum; it is not a record.
    implemented = _disposed(cand, "IMPLEMENTED")
    declared_n = _disposed(cand, "DECLARED")
    if len(provisos) != implemented + declared_n:
        return reject(Reason.PROVISO_ARITHMETIC,
                      recorded=len(recorded), implemented=implemented, declared=declared_n)

    # --- 7. a DECLARED proviso must name what it emits --------------------------------------
    for p in recorded:
        if p.disposal == "DECLARED" and not p.emits:
            return reject(Reason.DECLARED_PROVISO_MISSING_EMISSION)

    return GateOutcome(gate=GateId.G0, passed=True, measured=measured())


def _provisos_of(cand: Any) -> tuple[Any, ...]:
    clause = getattr(cand, "clause", None)
    return tuple(getattr(clause, "provisos", ()) or ())


def _disposed(cand: Any, disposal: str) -> int:
    return sum(1 for p in _provisos_of(cand) if p.disposal == disposal)


def assert_not_uniformly_proviso_free(outcomes: Mapping[str, GateOutcome], candidates: Any) -> None:
    """NC-Q35, and **the scoping is the whole point**.

    An empty marker list makes G0 report `provisos_total == 0` for everything and pass everything —
    scope truncation applied to the gate that exists to catch scope truncation. So a run where
    EVERY statutory candidate reports zero provisos raises.

    **Scoped to `source == STATUTE`.** Under F9's ruling every harvested candidate is
    `source: TEMPLATE` with a legitimate `provisos_total == 0`, and an unscoped guard would fire on
    a correct build — and would then be "fixed" by deleting it, which is how a real guard dies.
    """
    statutory = [
        c for c in candidates if getattr(c, "obligation_source", None) == ObligationSource.STATUTE.value
    ]
    if not statutory:
        return
    totals = [outcomes[c.id].measured.get("provisos_total", 0) for c in statutory if c.id in outcomes]
    if totals and all(t == 0 for t in totals):
        raise SuspiciousUniformityError(
            f"G0 reported provisos_total == 0 for all {len(totals)} STATUTE candidate(s). The "
            "instrument is measurably full of provisos, so this is an empty marker list rather "
            "than a proviso-free corpus. (The guard is scoped to STATUTE: a TEMPLATE obligation's "
            "zero is the truth, and an unscoped guard would fire on a correct build.)"
        )
