"""THE QUESTIONING LAYER. A refusal becomes a question; an answer becomes a labelled value.

`cdfc.ask` is a VERDICT ROOT and may never import `cdfc.model`. An answer is a named human's
assertion, and a layer able to consult a model while stamping `resolved_by: human` would make that
label forgeable — which is the same argument that keeps `cdfc.fill` out of the model's reach.
"""

from cdfc.ask.answers import (
    Answer,
    AnswerNotAdmitted,
    AnswerRefusal,
    Applied,
    Redirect,
    apply,
    claims_from,
)
from cdfc.ask.questions import (
    ASKABLE,
    NOT_ASKABLE,
    Askable,
    AnswerShape,
    NotAsked,
    Option,
    Question,
    QuestionSet,
    askable,
    question_id,
    questions_for,
)

__all__ = [
    "ASKABLE", "NOT_ASKABLE", "Answer", "AnswerNotAdmitted", "AnswerRefusal", "AnswerShape",
    "Applied", "Askable", "NotAsked", "Option", "Question", "QuestionSet", "Redirect", "apply",
    "askable", "claims_from", "question_id", "questions_for",
]
