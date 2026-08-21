"""THE QUESTIONING LAYER — a refusal, turned into a question a filer can answer.

## The sentence this closes

> *"…tell you exactly what nothing supports, what two of your documents disagree about, and what
> needs your judgement."*

That is a system that **ASKS**. Before this module the system counted: `cdfc.fill` produced 3,735
refusals over the FME blank, every one carrying a reason from a closed vocabulary, and no question
was ever put, no answer could be given, and no answer could become a value. A lane in name only.

## SIX OF THE EIGHT REASONS ARE QUESTIONS. TWO ARE NOT, AND MUST NEVER BE SHOWN AS ONES

`ASKABLE` is an **allowlist**, and that is the load-bearing choice. A denylist of *"reasons not to
ask about"* refuses only what somebody remembered to write down; this project has been bitten by
that shape five times. Here the consequence is specific and measurable: on the pinned FME return
`field_not_labelled` is **3,615 of 3,735** refusals — measured 20 Aug 2026 by
`tools/user_flow.py`, not cited — and a screen that headlines 3,735 as *"needs your judgement"*
is off by a factor of twenty-nine. `NOT_ASKABLE` names the two and says why each one is not a
question:

* **`field_not_labelled`** — the regulator's own cell carries no label under the pinned label rule.
  There is no question to formulate. *"What value goes in `Sheet3!AC118`?"* is not a question, it
  is a coordinate; the filer would have to open the workbook and read the merged header themselves,
  at which point we have asked them to do the work and called it an answer.
* **`reverification_failed`** — a span we cited did not re-read byte-exact. That is **our** defect,
  not the filer's, and asking them to adjudicate it invites them to wave through a locator fault.

`_check_disposition_is_total()` runs at import and raises unless every member of `FillRefusal` is
in exactly one of the two tables. A ninth reason added to the vocabulary is therefore a build
error rather than a reason that is silently unaskable — or, worse, silently asked.

## An answer is a WEAKER TIER, and it is labelled

Answering does not make a cell evidenced. `cdfc.ask.answers.apply` puts the value in
`FillDeclaration.asserted`, which `admitted()` excludes and `filled()` includes, carrying the
answering person, the instant, and the id of the question they answered. See `fill.propose.Asserted`.

## No model, no clock, no network

`cdfc.ask` is a VERDICT ROOT. An answer is a named human's assertion, and a layer that could
consult a model while claiming `resolved_by: human` would make that label forgeable. The instant
is an argument for the same reason `ci/no-clock-in-core.sh` exists: a value read from the wall
clock inside the core is a value the caller cannot pin.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from cdfc.evidence.fields import FieldSet
from cdfc.evidence.observe import Observation
from cdfc.fill.propose import FillDeclaration, FillRefusal


class AnswerShape(StrEnum):
    """What a valid answer LOOKS like. Closed, because the surface renders one widget per shape."""

    VALUE = "value"            # free text the filer asserts
    ONE_OF = "one_of"          # a choice among options THIS SYSTEM supplies
    DOCUMENT = "document"      # names one of the documents this run actually read
    SIGNATORY = "signatory"    # a named natural person, accepting liability


@dataclass(frozen=True, slots=True)
class Askable:
    """One refusal reason, and the question it becomes."""

    reason: FillRefusal
    shape: AnswerShape
    question: str      # put to the filer, in the filer's terms
    resolves: str      # how an answer resolves it — shown, so the filer knows what they are doing


# THE ALLOWLIST. Six rows, each one a reason a filer can actually do something about.
ASKABLE: Final[Mapping[FillRefusal, Askable]] = {
    FillRefusal.NO_OBSERVATION: Askable(
        FillRefusal.NO_OBSERVATION, AnswerShape.VALUE,
        "Nothing you gave us contains a value for this field. What is it?",
        "upload a document that carries it, or assert the value here",
    ),
    FillRefusal.SUPPORT_CONTRADICTED: Askable(
        FillRefusal.SUPPORT_CONTRADICTED, AnswerShape.ONE_OF,
        "Two of your documents disagree about this field. Which is right?",
        "choose the value, and the document it came from is recorded with your choice",
    ),
    FillRefusal.NOT_LOCATABLE_IN_SOURCE: Askable(
        FillRefusal.NOT_LOCATABLE_IN_SOURCE, AnswerShape.DOCUMENT,
        "A column offered a value for this field and no document you gave us contains it. "
        "Which document should it have come from?",
        "name the document; we re-read it, and a value we still cannot locate is still refused",
    ),
    FillRefusal.VOCABULARY_NOT_ADMITTED: Askable(
        FillRefusal.VOCABULARY_NOT_ADMITTED, AnswerShape.ONE_OF,
        "Your value is not in the list this form declares. Which of these did you mean?",
        "choose a term from the form's own data validation list",
    ),
    FillRefusal.TYPE_NOT_ADMITTED: Askable(
        FillRefusal.TYPE_NOT_ADMITTED, AnswerShape.VALUE,
        "This cell needs a value in the type the form declares. What is it?",
        "supply one in that type; we do not coerce, so a value that still does not parse is "
        "still refused",
    ),
    FillRefusal.ATTESTATION_REQUIRES_SIGNATORY: Askable(
        FillRefusal.ATTESTATION_REQUIRES_SIGNATORY, AnswerShape.SIGNATORY,
        "This is a certification. Who is signing it?",
        "a named natural person accepts liability for the statement; no system may forge one",
    ),
}

# THE OTHER HALF, NAMED. Not a comment — a table, so that the totality check below can see it.
NOT_ASKABLE: Final[Mapping[FillRefusal, str]] = {
    FillRefusal.FIELD_NOT_LABELLED: (
        "the regulator's cell carries no label under the pinned label rule, so there is no "
        "question to formulate. Asking 'what value goes in this coordinate?' asks the filer to "
        "read the workbook for us and calls their reading an answer. On the pinned FME return "
        "this is 3,615 of 3,735 refusals, so presenting it as a question would misstate the work "
        "by a factor of twenty-nine"
    ),
    FillRefusal.REVERIFICATION_FAILED: (
        "a span we cited did not re-read byte-exact in the document we cited it from. That is our "
        "defect and not the filer's, and putting it to them invites a person with no way to check "
        "to wave through a locator fault"
    ),
}


def _check_disposition_is_total() -> None:
    """Every reason is askable or is named as not-a-question. Neither by default, and never both.

    Raises at IMPORT. A ninth reason added to `FillRefusal` with no declared disposition is a build
    error, which is the only way this stays an allowlist rather than a list somebody remembers to
    extend.
    """
    declared = set(ASKABLE) | set(NOT_ASKABLE)
    both = set(ASKABLE) & set(NOT_ASKABLE)
    missing = set(FillRefusal) - declared
    extra = declared - set(FillRefusal)
    if both:
        raise RuntimeError(
            f"{sorted(r.value for r in both)} are declared BOTH askable and not-a-question. A "
            "reason has one disposition; two means the surface decides by whichever table it "
            "reads first."
        )
    if missing:
        raise RuntimeError(
            f"FillRefusal has {len(missing)} reason(s) with no declared disposition: "
            f"{sorted(r.value for r in missing)}. Add a row to ASKABLE with the question it "
            "becomes, or to NOT_ASKABLE with the reason it is not one. An undeclared reason must "
            "not default either way: defaulting to askable puts an unanswerable question to a "
            "filer, and defaulting to silent hides work from them."
        )
    if extra:
        raise RuntimeError(f"{sorted(extra)} are not members of FillRefusal")


_check_disposition_is_total()


@dataclass(frozen=True, slots=True)
class Option:
    """One choice the system offers. `value` is what an answer submits; `note` is why it is here."""

    value: str
    note: str


@dataclass(frozen=True, slots=True)
class Question:
    """One question, about one field, arising from one refusal."""

    id: str
    ref: str
    label: str
    reason: FillRefusal
    shape: AnswerShape
    question: str
    resolves: str
    detail: str                       # what the fill lane said when it refused
    options: tuple[Option, ...] = ()  # non-empty for ONE_OF and DOCUMENT
    certifies: str = ""               # non-empty for SIGNATORY

    def admits(self, value: str) -> bool:
        """Is `value` an answer this question can take? Options are a CLOSED set when present."""
        v = value.strip()
        if not v:
            return False
        if self.shape in (AnswerShape.ONE_OF, AnswerShape.DOCUMENT):
            return any(v == o.value for o in self.options)
        return True

    def as_canonical_obj(self) -> dict[str, object]:
        return {
            "id": self.id, "ref": self.ref, "label": self.label, "reason": self.reason.value,
            "shape": self.shape.value, "question": self.question, "resolves": self.resolves,
            "detail": self.detail, "certifies": self.certifies,
            "options": [{"value": o.value, "note": o.note} for o in self.options],
        }


@dataclass(frozen=True, slots=True)
class NotAsked:
    """A refusal population that is NOT a question, reported as such and never as one."""

    reason: FillRefusal
    count: int
    why: str


@dataclass(frozen=True, slots=True)
class QuestionSet:
    """The questions, AND the refusals that are not questions. Both, or the total misleads."""

    template_sha256: str
    questions: tuple[Question, ...]
    not_asked: tuple[NotAsked, ...]

    def by_id(self) -> Mapping[str, Question]:
        return {q.id: q for q in self.questions}

    def counts(self) -> dict[str, int]:
        by_reason: dict[str, int] = {}
        for q in self.questions:
            by_reason[q.reason.value] = by_reason.get(q.reason.value, 0) + 1
        return {
            "questions": len(self.questions),
            "not_asked": sum(n.count for n in self.not_asked),
            **{f"ask_{k}": v for k, v in sorted(by_reason.items())},
            **{f"not_asked_{n.reason.value}": n.count for n in self.not_asked},
        }

    def lines(self) -> tuple[str, ...]:
        c = self.counts()
        out = [f"{c['questions']} question(s) we can put to you:"]
        for k, v in sorted(c.items()):
            if k.startswith("ask_"):
                out.append(f"  {k[len('ask_'):]:34} {v:6}")
        out += ["", f"{c['not_asked']} refusal(s) that are NOT questions:"]
        for n in self.not_asked:
            out.append(f"  {n.reason.value:34} {n.count:6}  — {n.why[:60]}…")
        return tuple(out)


def question_id(template_sha256: str, ref: str, reason: FillRefusal) -> str:
    """Stable and content-derived, so an answer names the question it answered and nothing else.

    A counter would renumber the moment a source is added and the previous run's answers would
    silently re-target other cells.
    """
    h = hashlib.sha256(f"{template_sha256}\x1f{ref}\x1f{reason.value}".encode()).hexdigest()
    return f"q_{h[:16]}"


def askable(reason: FillRefusal) -> Askable | None:
    """The question this reason becomes, or None. **The only admission point.**"""
    return ASKABLE.get(reason)


def questions_for(
    declaration: FillDeclaration,
    fields: FieldSet,
    *,
    binding: Mapping[str, Sequence[Observation]] | None = None,
    documents: Sequence[str] = (),
    document_names: Mapping[str, str] | None = None,
) -> QuestionSet:
    """Every refusal that IS a question, plus a truthful count of the ones that are not.

    `binding` is read for `support_contradicted`, so the options are the observations that actually
    disagree rather than a parse of the refusal's prose. `documents` are the sources this run read,
    which is what a `not_locatable_in_source` answer chooses among.

    `document_names` maps an instrument id to the name a person uploaded it as. The ANSWER still
    carries the instrument id, because that is what a claim resolves against — but *"as read in
    `source:543d3d1c87a2`"* is not a question a filer can act on, and a question nobody can act on
    is the thing this module exists to stop producing.
    """
    by_ref = fields.by_ref()
    named: Mapping[str, str] = dict(document_names or {})
    bound: Mapping[str, Sequence[Observation]] = dict(binding or {})
    qs: list[Question] = []
    not_asked: dict[FillRefusal, int] = {}

    for r in declaration.refused:
        spec = askable(r.reason)
        if spec is None:
            not_asked[r.reason] = not_asked.get(r.reason, 0) + 1
            continue
        field = by_ref.get(r.ref)
        options: tuple[Option, ...] = ()
        if spec.shape is AnswerShape.ONE_OF and r.reason is FillRefusal.VOCABULARY_NOT_ADMITTED:
            options = tuple(Option(v, "the form's own data validation list")
                            for v in (field.vocabulary if field else ()))
        elif spec.shape is AnswerShape.ONE_OF and r.reason is FillRefusal.SUPPORT_CONTRADICTED:
            # READ THE OBSERVATIONS, never the refusal's sentence. `Refusal.detail` renders the
            # first four disagreeing values into prose for a human; recovering them by parsing that
            # string would make the option list depend on a message's formatting.
            seen: dict[str, str] = {}
            for o in bound.get(r.ref, ()):
                seen.setdefault(o.value, o.document)
            options = tuple(Option(v, f"as read in {named.get(d, d)}")
                            for v, d in sorted(seen.items()))
        elif spec.shape is AnswerShape.DOCUMENT:
            options = tuple(Option(d, named.get(d, "a document this run read"))
                            for d in sorted(set(documents)))
        qs.append(Question(
            id=question_id(declaration.template_sha256, r.ref, r.reason),
            ref=r.ref, label=r.label, reason=r.reason, shape=spec.shape,
            question=spec.question, resolves=spec.resolves, detail=r.detail, options=options,
        ))

    # THE ATTESTATION LANE IS THE SIXTH QUESTION, and it is not in `refused` by design.
    #
    # `propose()` routes an attestation to its own lane before the six conditions run, so
    # `LANE_IS_FACT` never fails and `FillRefusal.ATTESTATION_REQUIRES_SIGNATORY` is constructed by
    # nothing — verified 20 Aug 2026 by grepping every `FillRefusal.` site. The reason is still the
    # right NAME for what is being asked, so the question carries it while the lane stays separate:
    # a certification is not a refusal, and reporting it as one would say the system tried to fill
    # a signature and failed.
    for a in declaration.attestations:
        qs.append(Question(
            id=question_id(declaration.template_sha256, a.ref,
                           FillRefusal.ATTESTATION_REQUIRES_SIGNATORY),
            ref=a.ref, label=a.label, reason=FillRefusal.ATTESTATION_REQUIRES_SIGNATORY,
            shape=AnswerShape.SIGNATORY,
            question=ASKABLE[FillRefusal.ATTESTATION_REQUIRES_SIGNATORY].question,
            resolves=ASKABLE[FillRefusal.ATTESTATION_REQUIRES_SIGNATORY].resolves,
            detail=(f"{len(a.supporting)} observation(s) support this statement; a signature is a "
                    "natural person accepting liability and no system may forge one"),
            certifies=a.certifies,
        ))

    return QuestionSet(
        template_sha256=declaration.template_sha256,
        questions=tuple(qs),
        not_asked=tuple(NotAsked(reason, n, NOT_ASKABLE[reason])
                        for reason, n in sorted(not_asked.items(), key=lambda kv: -kv[1])),
    )
