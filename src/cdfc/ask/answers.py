"""An answer, admitted or refused — and the value it becomes, labelled as what it is.

## An answer is not evidence, and the label is the product

`cdfc.fill` proposes a value only when a grounded observation **re-reads byte-exact** at the span
it cites. An answer re-reads nothing: a person typed it. Admitting it is right — the filer knows
things no document we hold contains — and counting it as evidenced would quietly widen what
*"checked"* means, which is the failure `Derived` was created to avoid on the model's side.

So an admitted answer lands in `FillDeclaration.asserted` carrying the answering person, the
instant, and the id of the question it answered. `admitted()` excludes it; `filled()` includes it.

## A DOCUMENT answer is not a value, and it is not asserted either

Five of the six shapes yield a value. The sixth — `not_locatable_in_source` — asks *which document
should this have come from*, and the honest resolution is to **go and read that document**, not to
write the document's name into the regulator's cell. Those answers come back as `Redirect`s, which
a caller feeds to `fill.pipeline.run(claims=…)`: the value is located in the named document or it
is refused again. An answer that sends us to look is worth more than an answer that overrides the
looking, and it is the one shape where the filer's knowledge can produce an EVIDENCED fill.

## Refusing an answer

`AnswerRefusal` is closed, for the same reason `FillRefusal` is. The one that matters most is
`ANSWER_NOT_IN_OPTIONS`: when this system offered the choices, a value outside them is not a
freer answer, it is an answer to a different question.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from cdfc.ask.questions import AnswerShape, Question, QuestionSet
from cdfc.fill.propose import Asserted, Attestation, FillDeclaration, Refusal


class AnswerRefusal(StrEnum):
    """Why an answer was not admitted. CLOSED, and every refusal takes exactly one."""

    NO_SUCH_QUESTION = "no_such_question"
    QUESTION_NOT_OPEN = "question_not_open"
    EMPTY_ANSWER = "empty_answer"
    ANSWER_NOT_IN_OPTIONS = "answer_not_in_options"
    UNNAMED_ANSWERER = "unnamed_answerer"
    UNDATED_ANSWER = "undated_answer"


class AnswerNotAdmitted(ValueError):
    """Raised with a reason from the closed vocabulary. Never downgraded to a skipped answer."""

    def __init__(self, reason: AnswerRefusal, detail: str) -> None:
        self.reason, self.detail = reason, detail
        super().__init__(f"{reason.value}: {detail}")


@dataclass(frozen=True, slots=True)
class Answer:
    """What a filer submitted. `answered_at` is an ARGUMENT — the core reads no clock."""

    question_id: str
    value: str
    answered_by: str
    answered_at: str


@dataclass(frozen=True, slots=True)
class Redirect:
    """An answer naming a document. Directs a re-read; becomes a claim, never a value."""

    ref: str
    document: str
    question_id: str
    answered_by: str
    answered_at: str

    def as_claim(self, value: str) -> dict[str, str]:
        """The shape `fill.pipeline.run(claims=…)` reads. The value must still be LOCATED there."""
        return {"document": self.document, "field": self.ref, "value": value}


@dataclass(frozen=True, slots=True)
class Applied:
    """The declaration after answers, and what each answer did."""

    declaration: FillDeclaration
    asserted: tuple[Asserted, ...]
    redirects: tuple[Redirect, ...]


def _validate(q: Question | None, a: Answer) -> Question:
    if q is None:
        raise AnswerNotAdmitted(
            AnswerRefusal.NO_SUCH_QUESTION,
            f"{a.question_id!r} is not a question this run put. Question ids are derived from the "
            "template digest, the field ref and the reason, so an id from another run addresses "
            "another run's cell.",
        )
    if not a.value.strip():
        raise AnswerNotAdmitted(
            AnswerRefusal.EMPTY_ANSWER,
            f"the answer to {q.ref} is empty. `absent != empty != zero`: an unanswered question "
            "stays a question, and recording an empty string as an assertion would put a blank in "
            "the return under a person's name.",
        )
    if not a.answered_by.strip():
        raise AnswerNotAdmitted(
            AnswerRefusal.UNNAMED_ANSWERER,
            f"the answer to {q.ref} names nobody. An assertion whose author is unknown cannot be "
            "labelled `resolved_by: human` — there is no human in it.",
        )
    try:
        datetime.fromisoformat(a.answered_at)
    except (TypeError, ValueError) as e:
        raise AnswerNotAdmitted(
            AnswerRefusal.UNDATED_ANSWER,
            f"the answer to {q.ref} carries {a.answered_at!r}, which is not an ISO 8601 instant "
            f"({e}). The instant is supplied by the caller because the core reads no clock, and "
            "an unparseable one is not a weaker timestamp, it is none.",
        ) from e
    if not q.admits(a.value):
        raise AnswerNotAdmitted(
            AnswerRefusal.ANSWER_NOT_IN_OPTIONS,
            f"{a.value!r} is not one of the {len(q.options)} option(s) offered for {q.ref} "
            f"({[o.value for o in q.options][:4]}). This system supplied the choices; a value "
            "outside them is an answer to a different question.",
        )
    return q


def apply(
    declaration: FillDeclaration,
    questions: QuestionSet,
    answers: Sequence[Answer],
) -> Applied:
    """Move every answered field out of `refused`/`attestations` and into `asserted`.

    The declaration must still CLOSE — `FillDeclaration.__post_init__` re-checks the partition, so
    an answer that duplicated a ref or lost one raises here rather than producing a report whose
    lanes do not sum.
    """
    by_id = questions.by_id()
    open_refs = {r.ref for r in declaration.refused} | {a.ref for a in declaration.attestations}

    asserted: list[Asserted] = []
    redirects: list[Redirect] = []
    taken: set[str] = set()

    for a in answers:
        q = _validate(by_id.get(a.question_id), a)
        if q.ref not in open_refs:
            raise AnswerNotAdmitted(
                AnswerRefusal.QUESTION_NOT_OPEN,
                f"{q.ref} is no longer refused or awaiting a signature in this declaration, so "
                "there is nothing for an answer to resolve. Re-read the questions and answer the "
                "ones this run actually put.",
            )
        if q.ref in taken:
            raise AnswerNotAdmitted(
                AnswerRefusal.QUESTION_NOT_OPEN,
                f"{q.ref} was answered twice in one submission. A field takes one value; applying "
                "both would put the field in the asserted lane twice and the declaration would "
                "not close.",
            )
        taken.add(q.ref)

        if q.shape is AnswerShape.DOCUMENT:
            # NOT A VALUE. The filer named where to look, and looking is what settles it.
            redirects.append(Redirect(ref=q.ref, document=a.value.strip(),
                                      question_id=q.id, answered_by=a.answered_by.strip(),
                                      answered_at=a.answered_at))
            taken.discard(q.ref)   # the ref stays open: nothing has been placed in it yet
            continue

        asserted.append(Asserted(
            ref=q.ref, label=q.label, value=a.value.strip(), question_id=q.id, reason=q.reason,
            answered_by=a.answered_by.strip(), answered_at=a.answered_at,
        ))

    moved = {s.ref for s in asserted}
    kept_refused: tuple[Refusal, ...] = tuple(r for r in declaration.refused if r.ref not in moved)
    kept_attest: tuple[Attestation, ...] = tuple(
        a for a in declaration.attestations if a.ref not in moved
    )

    return Applied(
        declaration=FillDeclaration(
            template_sha256=declaration.template_sha256,
            surface_total=declaration.surface_total,
            proposed=declaration.proposed,
            refused=kept_refused,
            attestations=kept_attest,
            derived=declaration.derived,
            asserted=declaration.asserted + tuple(asserted),
        ),
        asserted=tuple(asserted),
        redirects=tuple(redirects),
    )


def claims_from(redirects: Sequence[Redirect], offered: Mapping[str, str]) -> list[dict[str, str]]:
    """Turn document answers into `fill.pipeline.run(claims=…)` rows.

    `offered` is what a column offered for each ref and could not be located — the value the filer
    is telling us to go and find. A redirect for a ref nothing was offered for is dropped, because
    there is no value to look for and inventing one would be the system answering its own question.
    """
    return [r.as_claim(offered[r.ref]) for r in redirects if offered.get(r.ref, "").strip()]
