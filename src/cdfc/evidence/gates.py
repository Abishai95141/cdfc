"""LAYER 3 — five deterministic gates decide whether a model's proposal becomes a node.

**This is the layer the architecture rests on.** The claim is not that the model is accurate; it
is that the model's errors are CATCHABLE without a human reading every one. On the real IFSCA
instrument the spike measured that: of 15 proposals the gates refused 5 -- all 3 planted errors,
AND 2 of 12 genuine ones, cells cited without checking they exist.

    G-QUOTE   the cited bytes are verbatim at the cited provision
    G-FIELD   the cited cell is in the template's OWN field surface
    G-TYPE    what the rule demands matches what the TEMPLATE DECLARES the field to be
    G-VOCAB   every term the rule requires is in the field's own validation list
    G-XREF    every cross-reference resolves to a provision that exists

`G-TYPE` is the one worth understanding, because it is what makes a prose-proposed binding safe
without labels and without a model: the template's own declarations become the type system that
adjudicates the claim. A model proposes *"regulation 8(1) governs `1. Introduction!D40`"* and the
gate refuses it because D40 is date-validated while a threshold needs a money amount.

**Every gate votes on ADMISSION and none of them can be persuaded.** A refusal names a reason
from a closed vocabulary, so a caller can act on it; there is no free-text refusal and no
`OTHER`.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from cdfc.evidence.fields import FieldSet
from cdfc.evidence.proposal import Proposal, ProposalSet
from cdfc.evidence.provisions import ProvisionSet
from cdfc.evidence.vocabulary import DEMANDS, FieldType, Refusal, RuleKind

_WS = re.compile(r"\s+")


def _norm(s: str) -> str:
    """Whitespace-insensitive comparison, and NOTHING else is normalised.

    A PDF extraction breaks lines wherever the column ended, so requiring byte equality across
    newlines would refuse quotes that are genuinely present. Case, punctuation and digits are
    left alone: those are the things a wrong quote gets wrong.
    """
    return _WS.sub(" ", s).strip()


@dataclass(frozen=True, slots=True)
class Verdict:
    proposal: Proposal
    refusals: tuple[tuple[str, Refusal, str], ...]     # (gate, reason, detail)

    @property
    def admitted(self) -> bool:
        return not self.refusals

    @property
    def reasons(self) -> tuple[Refusal, ...]:
        return tuple(r for _g, r, _d in self.refusals)


@dataclass(frozen=True, slots=True)
class Adjudication:
    verdicts: tuple[Verdict, ...]

    @property
    def admitted(self) -> tuple[Verdict, ...]:
        return tuple(v for v in self.verdicts if v.admitted)

    @property
    def refused(self) -> tuple[Verdict, ...]:
        return tuple(v for v in self.verdicts if not v.admitted)

    def planted_caught(self) -> tuple[int, int]:
        """(planted proposals refused, planted proposals). A control, not a score."""
        planted = [v for v in self.verdicts if v.proposal.is_planted]
        return (sum(1 for v in planted if not v.admitted), len(planted))

    def genuine_refused(self) -> tuple[int, int]:
        """(genuine proposals refused, genuine proposals) -- the model's real error rate."""
        genuine = [v for v in self.verdicts if not v.proposal.is_planted]
        return (sum(1 for v in genuine if not v.admitted), len(genuine))


def g_quote(p: Proposal, provisions: ProvisionSet) -> tuple[Refusal, str] | None:
    prov = provisions.get(p.eid)
    if prov is None:
        return (Refusal.PROVISION_NOT_IN_CORPUS,
                f"no provision {p.eid!r} in {provisions.instrument_id}")
    if _norm(p.quote) not in _norm(prov.text):
        return (Refusal.QUOTE_NOT_VERBATIM, f"the quote is not the text at {p.eid}")
    if prov.disputed:
        # NOT the same refusal as "nowhere". The extractors disagreed about these bytes, and the
        # remedy is to re-pin the region rather than to rewrite the quote.
        return (Refusal.QUOTE_IN_DISPUTED_REGION, f"{p.eid} overlaps a disputed region")
    return None


def g_field(p: Proposal, fields: FieldSet) -> tuple[Refusal, str] | None:
    if p.kind in (RuleKind.DEFINITION, RuleKind.APPLICABILITY):
        # These govern no field by construction. A field_ref on one is a category error and is
        # refused rather than ignored -- silently dropping it would admit a claim nobody checked.
        if p.field_ref is None:
            return None
        return (Refusal.FIELD_NOT_IN_SURFACE,
                f"a {p.kind.value} rule governs no field, yet it names {p.field_ref!r}")
    if p.field_ref is None:
        return (Refusal.FIELD_NOT_IN_SURFACE, f"a {p.kind.value} rule must name a field")
    if fields.get(p.field_ref) is None:
        # THE TWO CASES ARE NOT THE SAME AND MUST NOT SHARE A REASON. A cell outside the surface
        # is a bad citation. A cell INSIDE the surface that carries no label is a gap in what our
        # reader can see -- the proposal may be perfectly correct, and saying "not in the field
        # surface" about a cell that is in the field surface is a false sentence in a refusal.
        if p.field_ref in fields.surface:
            return (Refusal.FIELD_NOT_LABELLED,
                    f"{p.field_ref} IS in the {fields.surface_total}-cell field surface but "
                    f"carries no label under the {fields.label_rule.value} rule, so G-TYPE and "
                    "G-VOCAB have nothing to adjudicate against")
        return (Refusal.FIELD_NOT_IN_SURFACE,
                f"no field {p.field_ref!r} in the {fields.surface_total}-cell field surface")
    return None


def g_type(p: Proposal, fields: FieldSet) -> tuple[Refusal, str] | None:
    demanded = DEMANDS.get(p.kind, frozenset())
    if not demanded or p.field_ref is None:
        return None
    f = fields.get(p.field_ref)
    if f is None:
        return None                                  # G-FIELD already refused it
    if f.type is FieldType.UNDECLARED:
        # The template declares nothing, so the type system has nothing to say. Admitting on
        # silence is the honest reading: the gate has no evidence either way, and inventing a
        # refusal here would make an unformatted cell unusable rather than merely unchecked.
        return None
    if f.type not in demanded:
        return (Refusal.TYPE_MISMATCH,
                f"{p.kind.value} needs {sorted(t.value for t in demanded)}; "
                f"{p.field_ref} is declared {f.type.value}")
    return None


def g_vocab(p: Proposal, fields: FieldSet) -> tuple[Refusal, str] | None:
    if not p.terms or p.field_ref is None:
        return None
    f = fields.get(p.field_ref)
    if f is None or not f.vocabulary:
        return None
    lower = {v.lower() for v in f.vocabulary}
    missing = sorted(t for t in p.terms if t.lower() not in lower)
    if missing:
        return (Refusal.TERM_NOT_IN_VOCABULARY,
                f"{missing} absent from {p.field_ref}'s validation list {list(f.vocabulary)}")
    return None


def g_xref(p: Proposal, provisions: ProvisionSet) -> tuple[Refusal, str] | None:
    dangling = tuple(e for e in p.refers_to if provisions.get(e) is None)
    if dangling:
        return (Refusal.XREF_UNRESOLVED, f"{list(dangling)} resolve to no provision")
    return None


def adjudicate(
    proposals: ProposalSet | Sequence[Proposal],
    provisions: ProvisionSet,
    fields: FieldSet,
) -> Adjudication:
    """Run all five gates over every proposal. **Every gate runs; the first refusal does not stop
    the rest**, because a caller fixing one defect needs to see the others in the same pass."""
    rows = proposals.proposals if isinstance(proposals, ProposalSet) else tuple(proposals)
    out: list[Verdict] = []
    for p in rows:
        refusals: list[tuple[str, Refusal, str]] = []
        for name, hit in (
            ("G-QUOTE", g_quote(p, provisions)),
            ("G-FIELD", g_field(p, fields)),
            ("G-TYPE", g_type(p, fields)),
            ("G-VOCAB", g_vocab(p, fields)),
            ("G-XREF", g_xref(p, provisions)),
        ):
            if hit is not None:
                refusals.append((name, hit[0], hit[1]))
        out.append(Verdict(proposal=p, refusals=tuple(refusals)))
    return Adjudication(verdicts=tuple(out))
