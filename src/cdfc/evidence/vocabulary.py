"""The closed vocabularies. A refusal that cannot be named is a refusal nobody can act on."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class Refusal(StrEnum):
    """Why a proposal was refused. CLOSED: a gate may not invent a reason at the point of use."""

    QUOTE_NOT_VERBATIM = "quote_not_verbatim"
    QUOTE_IN_DISPUTED_REGION = "quote_in_disputed_region"
    PROVISION_NOT_IN_CORPUS = "provision_not_in_corpus"
    FIELD_NOT_IN_SURFACE = "field_not_in_surface"
    # DISTINCT FROM THE ABOVE, AND THE DISTINCTION WAS PAID FOR. The spike published "2 of my 12
    # genuine proposals were refused -- I cited cells without checking they exist", and an audit
    # of that claim found BOTH cells exist AND are in the 3,747-cell surface. What they lack is a
    # LABEL under the pinned labelling rule. The gate had been checking membership of the labelled
    # subset while its reason string said "field surface", so a defect in OUR reader was published
    # as the proposer's error rate. Two reasons, because they have two different remedies: the
    # first is a bad citation, the second is a gap in what we can read.
    FIELD_NOT_LABELLED = "field_not_labelled"
    TYPE_MISMATCH = "type_mismatch"
    TERM_NOT_IN_VOCABULARY = "term_not_in_vocabulary"
    XREF_UNRESOLVED = "xref_unresolved"


class FieldType(StrEnum):
    """What the TEMPLATE declares a field to be. Read from the workbook, never guessed."""

    MONEY = "money"
    PERCENT = "percent"
    DATE = "date"
    NUMBER = "number"
    ENUM = "enum"          # a data validation list; the vocabulary travels with it
    TEXT = "text"
    UNDECLARED = "undeclared"


class Asks(StrEnum):
    """What a field asks the filer to DO. The two lanes are handled differently and must not mix."""

    FACT = "fact"                  # report a value; fillable from evidence
    ATTESTATION = "attestation"    # certify a statement; a named human signs, the system never fills


class RuleKind(StrEnum):
    THRESHOLD = "threshold"
    DEADLINE = "deadline"
    ENUMERATION = "enumeration"
    DISCLOSURE = "disclosure"
    DEFINITION = "definition"
    APPLICABILITY = "applicability"


class EIdKind(StrEnum):
    """How a provision is ADDRESSED, and it decides whether a stored rule survives re-extraction.

    `COORDINATE` is `p0143.s0008` -- page 143, sentence 8. It is what the pinned corpus supports
    today, and it MOVES if the instrument is re-extracted, if the layout shifts, or if an
    amendment adds a page. `PROVISION` is `reg_8__subreg_1`, which does not move.

    The distinction is carried in the data rather than in a comment because a rule stored against
    a COORDINATE has a different lifetime from one stored against a PROVISION, and a reader who
    cannot tell them apart will assume the longer one.
    """

    COORDINATE = "coordinate"
    PROVISION = "provision"


# The type a rule of each kind DEMANDS of the field it governs. This is `G-TYPE`, and it is the
# mechanism that makes a prose-proposed binding safe: the template's own declarations adjudicate
# the model's claim, with no labels and no model.
DEMANDS: Final[dict[RuleKind, frozenset[FieldType]]] = {
    RuleKind.THRESHOLD: frozenset({FieldType.MONEY, FieldType.PERCENT, FieldType.NUMBER}),
    RuleKind.DEADLINE: frozenset({FieldType.DATE}),
    RuleKind.ENUMERATION: frozenset({FieldType.ENUM}),
    RuleKind.DISCLOSURE: frozenset({FieldType.TEXT, FieldType.ENUM, FieldType.UNDECLARED}),
    RuleKind.DEFINITION: frozenset(),        # governs no field; see gates.G_FIELD
    RuleKind.APPLICABILITY: frozenset(),     # governs no field; it selects a bearer
}
