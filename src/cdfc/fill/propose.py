"""A5 — THE FILL LANE. Two lanes, six mechanical conditions, and a declaration that must close.

## The claim this serves, and the two words it does not use

> *"…autonomously populates the regulator's prescribed filing template."*

`CLAUDE.md §5` records that the product claim deliberately omits two words, and **`autonomously` is
one of them**. This module proposes a value for every field it can evidence and refuses every field
it cannot, with a reason from a closed vocabulary. It does not decide that a filing is right, and
it never signs anything.

## THE TRIGGER IS MECHANICAL, NEVER A MODEL'S CONFIDENCE

`W0-C` measured what happens when a similarity judgement is trusted: the locator returned
`SUPPORTED` **20 of 20** times on evidence that had been DELETED. So the question asked here is not
*how sure are we* but:

    is there a grounded observation that RE-VERIFIES BYTE-EXACT at the span it cites?

`Observation.reverify` re-reads the cited span in the source and requires the exact bytes back. No
score, no threshold, no model. A locator that cannot reproduce what it claims to have found is not
evidence.

## The six conditions

Each is separately named, separately testable, and reported WHETHER OR NOT IT HELD — a proposal
carries all six outcomes, so a reader can see which one was load-bearing rather than a single
boolean.

    1  GROUNDED            at least one observation is bound to this field
    2  REVERIFIES          the chosen observation re-reads byte-exact          <- the trigger
    3  UNIQUE              the supporting observations agree on ONE value
    4  TYPE_ADMITS         the value parses under the type the TEMPLATE declares
    5  VOCABULARY_ADMITS   for an ENUM, the value is in the template's own list
    6  LANE_IS_FACT        the field asks for a value, not for a signature

**All six must hold.** Any that does not becomes the refusal reason, and where more than one fails
the FIRST in this order is reported, because the later ones are not meaningful once an earlier one
has failed — a value that does not re-verify has no type worth checking.

## THE TWO LANES DO NOT MIX

`FACT` fills from evidence. `ATTESTATION` never does: it assembles what supports the statement,
records what is being certified, and stops, because a certification is a natural person accepting
liability and no system may forge one. The spike measured the split on the FME return —
attestations are a small, localised minority, and `8. Compliance Status!C6` is one of them: *"The
Net worth requirement has been complied with…"*. The return never asks for the figure, so nothing
can fill that cell from any source at all.

## Where the binding comes from, and why it is an INPUT

This module does not decide which observation belongs to which field. That is
`cdfc.correspond`'s job (use 2: source column to template field) or, once `E6` licenses one, a
model's PROPOSAL. Taking the binding as an argument is what keeps this lane deterministic and
model-free: `cdfc.fill` is inside `VERDICT_ROOTS`, so it must not be able to consult the thing it
is adjudicating.

## Nothing here writes a workbook

`ci/no-openpyxl-writer.sh` exists because an openpyxl round-trip of the FME workbook **drops 24
parts and all 19 `x14` data validations and shrinks 3.66 MB to 66 kB**. A "filled" template written
that way is a different document that happens to share a name. Fills are emitted as DATA; writing
one into a real workbook needs raw-zip surgery and is a separate, gated decision.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from cdfc.evidence.fields import FieldSet
from cdfc.evidence.observe import Observation, canonical
from cdfc.evidence.vocabulary import Asks, FieldType
from cdfc.qualify.textsource import InstrumentText


class FillRefusal(StrEnum):
    """Why a field was not filled. CLOSED, and every refusal takes exactly one.

    `absent != empty != zero`: a field nothing observed is a different fact from one whose evidence
    would not re-verify, and both differ from one two sources disagree about.
    """

    FIELD_NOT_LABELLED = "field_not_labelled"
    NOT_LOCATABLE_IN_SOURCE = "not_locatable_in_source"
    NO_OBSERVATION = "no_observation"
    REVERIFICATION_FAILED = "reverification_failed"
    SUPPORT_CONTRADICTED = "support_contradicted"
    TYPE_NOT_ADMITTED = "type_not_admitted"
    VOCABULARY_NOT_ADMITTED = "vocabulary_not_admitted"
    ATTESTATION_REQUIRES_SIGNATORY = "attestation_requires_signatory"


# The six, in the order they are evaluated. Order matters and is part of the contract: a value that
# does not re-verify has no type worth checking, so the FIRST failure is the reported reason.
CONDITIONS: Final[tuple[str, ...]] = (
    "GROUNDED", "REVERIFIES", "UNIQUE", "TYPE_ADMITS", "VOCABULARY_ADMITS", "LANE_IS_FACT",
)


@dataclass(frozen=True, slots=True)
class Condition:
    name: str
    holds: bool
    detail: str


@dataclass(frozen=True, slots=True)
class FillProposal:
    """A value proposed for one field, with the evidence and ALL SIX condition outcomes."""

    ref: str
    label: str
    value: str
    document: str
    span: tuple[int, int]
    page: int | None
    context: str
    conditions: tuple[Condition, ...]

    @property
    def admitted(self) -> bool:
        return all(c.holds for c in self.conditions)

    def first_failure(self) -> Condition | None:
        return next((c for c in self.conditions if not c.holds), None)


@dataclass(frozen=True, slots=True)
class Refusal:
    ref: str
    label: str
    reason: FillRefusal
    detail: str


@dataclass(frozen=True, slots=True)
class Derived:
    """A value a model produced that NO SPAN SUPPORTS — admitted, and labelled as what it is.

    ## Why this lane exists

    Requiring a byte-exact span refuses everything a model SYNTHESISES: a figure summed across
    three custodian files, a total restated from a table, a value read out of a chart. Those are
    real and useful and the product needs them, and refusing them was holding back the semantic
    half for a property that only ever applied to QUOTED evidence.

    So they are admitted. **What does not happen is that they are counted as evidenced.**

    `Derived` is a third lane beside `FillProposal` and `Attestation`, and the separation is the
    entire safety property that replaces the one being relaxed:

    * it is **never** in `admitted()`, so no coverage figure counts it;
    * it carries `supported_by` — the units the model says it read — which is weaker than a span
      and is not nothing;
    * `cdfc attest` must not sign over one, because a signature is a claim that a named human
      accepted something re-derivable, and this is not.

    A reader gets both numbers and can tell them apart. That is the difference between flexibility
    and quietly widening what "checked" means.
    """

    ref: str
    label: str
    value: str
    basis: str                      # the model's own account of where the value came from
    supported_by: tuple[str, ...]   # unit keys it says it read; NOT spans, and never treated as
    model: str

    def as_canonical_obj(self) -> dict[str, object]:
        return {"ref": self.ref, "label": self.label, "value": self.value, "basis": self.basis,
                "supported_by": list(self.supported_by), "model": self.model,
                "evidenced": False}


@dataclass(frozen=True, slots=True)
class Attestation:
    """A field a human must sign. NEVER filled, and the evidence is assembled anyway.

    Assembling it is the useful part: the signatory sees what supports the statement they are being
    asked to certify, which is the difference between a signature and a guess.
    """

    ref: str
    label: str
    supporting: tuple[Observation, ...]
    certifies: str


@dataclass(frozen=True, slots=True)
class FillDeclaration:
    """What was filled, what was refused, what awaits a signature — and it must CLOSE.

    `__post_init__` raises unless the three lanes partition the field surface. A fill report whose
    stages do not sum has lost fields silently, which is the defect `RuleCoverage` refuses on the
    rule side and `Linkage` refuses on the record side.
    """

    template_sha256: str
    surface_total: int
    proposed: tuple[FillProposal, ...]
    refused: tuple[Refusal, ...]
    attestations: tuple[Attestation, ...]
    derived: tuple[Derived, ...] = ()

    def __post_init__(self) -> None:
        seen = ([p.ref for p in self.proposed] + [r.ref for r in self.refused]
                + [a.ref for a in self.attestations] + [d.ref for d in self.derived])
        if len(set(seen)) != len(seen):
            dupes = sorted({r for r in seen if seen.count(r) > 1})
            raise ValueError(
                f"the fill declaration addresses {len(dupes)} field(s) in more than one lane, e.g. "
                f"{dupes[:3]}. A field is filled, refused or awaiting a signature — never two."
            )
        if len(seen) != self.surface_total:
            raise ValueError(
                f"the declaration does not close: {len(self.proposed)} proposed + "
                f"{len(self.refused)} refused + {len(self.attestations)} attestations + "
                f"{len(self.derived)} derived = {len(seen)}, over a surface of "
                f"{self.surface_total}. A fill report whose lanes do not sum has lost fields "
                "silently."
            )

    def admitted(self) -> tuple[FillProposal, ...]:
        """EVIDENCED fills only. `derived` is deliberately absent: a value no span supports has
        not been checked, and putting it here would make one number mean two things."""
        return tuple(p for p in self.proposed if p.admitted)

    def filled(self) -> tuple[str, ...]:
        """Every ref this run PUTS A VALUE IN, evidenced or derived. The product's own count."""
        return tuple(sorted([p.ref for p in self.admitted()] + [d.ref for d in self.derived]))

    def counts(self) -> dict[str, int]:
        by_reason: dict[str, int] = {}
        for r in self.refused:
            by_reason[r.reason.value] = by_reason.get(r.reason.value, 0) + 1
        return {
            "surface_total": self.surface_total,
            "proposed": len(self.proposed),
            "admitted": len(self.admitted()),
            "refused": len(self.refused),
            "attestations": len(self.attestations),
            "derived": len(self.derived),
            "filled_total": len(self.filled()),
            **{f"refused_{k}": v for k, v in sorted(by_reason.items())},
        }

    def lines(self) -> tuple[str, ...]:
        c = self.counts()
        out = [
            f"of {c['surface_total']} fields in the surface, we propose a value for "
            f"{c['admitted']}.",
            "",
            "the typed reason for each of the others:",
        ]
        for k, v in sorted(c.items()):
            if k.startswith("refused_"):
                out.append(f"  {k[len('refused_'):]:34} {v:6} of {c['surface_total']}")
        out += [
            "",
            f"awaiting a named signatory  {c['attestations']} of {c['surface_total']}",
            f"DERIVED, no span supports them  {c['derived']} of {c['surface_total']}",
            "",
            f"values placed in the return  {c['filled_total']} of {c['surface_total']}  "
            f"= {c['admitted']} evidenced + {c['derived']} derived",
            "",
            "An EVIDENCED value cites a document and a span that re-reads byte-exact. A DERIVED "
            "value is one a model produced that no span supports — it is placed in the return and "
            "it is NOT counted as checked. Neither is a claim that the figure is correct.",
        ]
        return tuple(out)


# --- the type admission, read from what the TEMPLATE declared --------------------------------

_NUMERIC = re.compile(r"^[0-9][0-9,]*(?:\.[0-9]+)?$")
_DATEISH = re.compile(r"^\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}$")


def _type_admits(value: str, ftype: FieldType) -> tuple[bool, str]:
    """Does `value` parse under the type the template declares? No coercion, ever.

    A money field handed `"approximately 5 lakh"` is NOT a money field with a soft value; it is a
    field whose evidence does not fit what the regulator asked for, and saying so is the product.
    """
    v = value.strip()
    if not v:
        return False, "the observed value is empty"
    if ftype in (FieldType.MONEY, FieldType.NUMBER, FieldType.PERCENT):
        return (bool(_NUMERIC.match(v)),
                f"{v!r} is not a bare grouped number, which is what a {ftype.value} field declares")
    if ftype is FieldType.DATE:
        return bool(_DATEISH.match(v)), f"{v!r} is not a date this reader admits"
    if ftype in (FieldType.TEXT, FieldType.ENUM):
        return True, ""
    # UNDECLARED. The template said nothing, so nothing can be admitted against it.
    return False, "the template declares no type for this field, so no value can be type-checked"


def propose(
    fields: FieldSet,
    binding: Mapping[str, Sequence[Observation]],
    source: InstrumentText,
    *,
    binding_provenance: str,
) -> FillDeclaration:
    """Apply the six conditions to every field in the surface. Deterministic; no model, no network.

    `binding` maps a field ref to the observations bound to it, and `binding_provenance` names what
    produced it. Both are INPUTS: this lane adjudicates a binding, and a lane that could also
    create one could not be trusted to refuse it.
    """
    if not binding_provenance.strip():
        raise ValueError(
            "a binding with no declared provenance cannot be adjudicated: the refusals would not "
            "say whose proposal was refused."
        )

    by_ref = fields.by_ref()
    proposed: list[FillProposal] = []
    refused: list[Refusal] = []
    attestations: list[Attestation] = []

    for ref in sorted(fields.surface or {f.ref for f in fields.fields}):
        field = by_ref.get(ref)
        if field is None:
            # We cannot fill a cell we cannot name. `N2` measured the labelled population at 132 of
            # 3,747 on this return, so this is the largest lane and it must be visible, not absent.
            refused.append(Refusal(ref, "", FillRefusal.FIELD_NOT_LABELLED,
                                   "no label resolves for this cell under the pinned label rule, "
                                   "so there is nothing to bind evidence to"))
            continue

        obs = tuple(binding.get(ref, ()))

        # 6 is checked FIRST for the attestation lane, because an attestation is not a refusal —
        # it is a different lane, and routing it through the fill conditions would report a
        # signature as a missing value.
        if field.asks is Asks.ATTESTATION:
            attestations.append(Attestation(
                ref=ref, label=field.label, supporting=obs,
                certifies=field.label or "(the statement this cell carries)",
            ))
            continue

        conds, value, chosen = _evaluate(field, obs, source)
        first = next((c for c in conds if not c.holds), None)
        if first is None and chosen is not None:
            proposed.append(FillProposal(
                ref=ref, label=field.label, value=value, document=chosen.document,
                span=chosen.span, page=chosen.page, context=chosen.context, conditions=conds,
            ))
        else:
            refused.append(Refusal(ref, field.label, _REASON_FOR[first.name], first.detail))

    return FillDeclaration(
        template_sha256=fields.template_sha256,
        surface_total=len(fields.surface) or len(fields.fields),
        proposed=tuple(proposed), refused=tuple(refused), attestations=tuple(attestations),
    )


_REASON_FOR: Final[Mapping[str, FillRefusal]] = {
    "GROUNDED": FillRefusal.NO_OBSERVATION,
    "REVERIFIES": FillRefusal.REVERIFICATION_FAILED,
    "UNIQUE": FillRefusal.SUPPORT_CONTRADICTED,
    "TYPE_ADMITS": FillRefusal.TYPE_NOT_ADMITTED,
    "VOCABULARY_ADMITS": FillRefusal.VOCABULARY_NOT_ADMITTED,
    "LANE_IS_FACT": FillRefusal.ATTESTATION_REQUIRES_SIGNATORY,
}


def _evaluate(
    field, obs: tuple[Observation, ...], source: InstrumentText
) -> tuple[tuple[Condition, ...], str, Observation | None]:
    """The six, in order, short-circuiting the DETAIL but never the REPORT.

    Every condition appears in the returned tuple whether or not it was reached; the ones after a
    failure are marked as not holding with `not reached`, so the report never implies a check ran
    that did not.
    """
    out: list[Condition] = []

    grounded = bool(obs)
    out.append(Condition("GROUNDED", grounded,
                         "" if grounded else "no observation is bound to this field"))
    if not grounded:
        return tuple(out + [Condition(n, False, "not reached") for n in CONDITIONS[1:]]), "", None

    # THE TRIGGER. Only observations that re-read byte-exact may support a fill.
    verified = tuple(o for o in obs if o.reverify(source))
    out.append(Condition(
        "REVERIFIES", bool(verified),
        "" if verified else (
            f"none of {len(obs)} bound observation(s) re-reads byte-exact at the span it cites; "
            "a locator that cannot reproduce its own find is not evidence"),
    ))
    if not verified:
        return tuple(out + [Condition(n, False, "not reached") for n in CONDITIONS[2:]]), "", None

    distinct = sorted({canonical(o.value) for o in verified})
    unique = len(distinct) == 1
    out.append(Condition("UNIQUE", unique,
                         "" if unique else
                         f"{len(verified)} verified observation(s) disagree: {distinct[:4]}"))
    if not unique:
        return tuple(out + [Condition(n, False, "not reached") for n in CONDITIONS[3:]]), "", None

    chosen = verified[0]
    value = chosen.value

    ok, why = _type_admits(value, field.type)
    out.append(Condition("TYPE_ADMITS", ok, why))
    if not ok:
        return tuple(out + [Condition(n, False, "not reached") for n in CONDITIONS[4:]]), value, None

    in_vocab = (not field.vocabulary) or value in field.vocabulary
    out.append(Condition(
        "VOCABULARY_ADMITS", in_vocab,
        "" if in_vocab else
        f"{value!r} is not in the {len(field.vocabulary)} value(s) the template's own data "
        "validation declares",
    ))
    if not in_vocab:
        return tuple(out + [Condition("LANE_IS_FACT", False, "not reached")]), value, None

    out.append(Condition("LANE_IS_FACT", True, ""))
    return tuple(out), value, chosen
