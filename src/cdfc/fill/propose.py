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
    # UNDECLARED. The template declares nothing, so nothing can be TYPE-CHECKED against it — but
    # that is a fact about the workbook, not about the value. See `_undeclared` below.
    return False, "the template declares no type for this field, so no value can be type-checked"


def propose(
    fields: FieldSet,
    binding: Mapping[str, Sequence[Observation]],
    source: InstrumentText | Mapping[str, InstrumentText],
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

    # EVERY OBSERVATION RE-VERIFIES AGAINST ITS OWN DOCUMENT, and a run may name several.
    #
    # The first version took ONE `InstrumentText` and re-read every span in it. With a custodian
    # feed AND an officers register bound in one run, every observation from the second document
    # failed `REVERIFIES` — not because the span was wrong, but because it was re-read in the
    # wrong file. Five correctly-bound fields were refused as unverifiable evidence.
    #
    # Worse than losing them: a span from document A re-read in document B could COINCIDENTALLY
    # match, and would then pass. Re-verification against the wrong document is not a weaker check,
    # it is a check of something else.
    by_doc: Mapping[str, InstrumentText] = (
        {source.instrument_id: source} if isinstance(source, InstrumentText) else dict(source)
    )
    if not by_doc:
        raise ValueError("no source document was supplied, so no span could be re-verified.")

    by_ref = fields.by_ref()
    proposed: list[FillProposal] = []
    refused: list[Refusal] = []
    attestations: list[Attestation] = []
    derived: list[Derived] = []

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

        conds, value, chosen = _evaluate(field, obs, by_doc)
        first = next((c for c in conds if not c.holds), None)

        # AN UNDECLARED FIELD IS PLACED, NOT REFUSED — and it lands in `Derived`, labelled.
        #
        # `TYPE_ADMITS` refuses a field whose type the template never declared, and on the FME
        # return that is **92 of 124** FACT-shaped labelled fields. Refusing them outright caps
        # the whole product at 32 fillable cells because the WORKBOOK is sloppy, which is a cost
        # borne by the filer for somebody else's omission.
        #
        # So: when the ONLY failing condition is `TYPE_ADMITS`, and it failed because the template
        # declared no type at all, the value is placed in the derived lane. Every other condition
        # still had to hold — it is grounded, it re-verified byte-exact, the sources agree, and it
        # is not an attestation. What is missing is the template's own type declaration, and the
        # lane says so rather than the coverage count silently absorbing it.
        # `first` being TYPE_ADMITS already proves GROUNDED, REVERIFIES and UNIQUE held — they
        # are evaluated before it and a failure short-circuits. The first version of this branch
        # also required `all(c.holds for c in conds if c.name != "TYPE_ADMITS")`, which is never
        # true: the conditions AFTER the failure are recorded as `not reached` with holds=False,
        # so the guard excluded every case it existed to admit.
        if (first is not None and first.name == "TYPE_ADMITS"
                and field.type is FieldType.UNDECLARED and chosen is not None):
            derived.append(Derived(
                ref=ref, label=field.label, value=value,
                basis=("evidenced at a re-verified span, but the template declares no type for "
                       "this field so no value can be type-checked against it"),
                supported_by=(chosen.document,), model=binding_provenance,
            ))
            continue

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
        derived=tuple(derived),
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
    field, obs: tuple[Observation, ...], by_doc: Mapping[str, InstrumentText]
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

    # THE TRIGGER. Only observations that re-read byte-exact IN THEIR OWN DOCUMENT may support a
    # fill. An observation naming a document this run did not read is refused rather than
    # re-verified somewhere else, which would be a check of a different file.
    verified = tuple(o for o in obs
                     if o.document in by_doc and o.reverify(by_doc[o.document]))
    unknown = sorted({o.document for o in obs if o.document not in by_doc})
    out.append(Condition(
        "REVERIFIES", bool(verified),
        "" if verified else (
            f"none of {len(obs)} bound observation(s) re-reads byte-exact at the span it cites"
            + (f"; {len(unknown)} name a document this run did not read, e.g. {unknown[:2]}"
               if unknown else "")
            + ". A locator that cannot reproduce its own find is not evidence"),
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
        # THE OBSERVATION IS STILL RETURNED. It is grounded, it re-verified byte-exact and the
        # sources agree — only the TEMPLATE's type declaration is missing. Returning `None` here
        # discarded a perfectly good observation because of a fact about the workbook, and it made
        # the UNDECLARED-to-derived route in `propose` unreachable: that branch requires a chosen
        # observation and never got one.
        return (tuple(out + [Condition(n, False, "not reached") for n in CONDITIONS[4:]]),
                value, chosen)

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
