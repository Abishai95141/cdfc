"""P8-B3 — the six corpus provenances, and the two sets that decide what each licenses.

**Six values, and one of them is not a number.** `SELF-AUTHORED` renders as `—` and the word
*uninformative*, and the schema FORBIDS a number: an FFR measured on a corpus its authors also
wrote has expected value zero regardless of predicate quality. Printing *"0.0% false failures  <!-- rate-ok: the forbidden rendering, quoted as the defect it is -->
across 340 clean filings"* is worse than printing nothing, **because it has the shape of
evidence**.

The two intervals that must never be allowed to look alike are `0/340 → [0.000, 0.011]` and
`0/4 → [0.000, 0.490]`. That is why the tier is keyed on the Wilson UPPER bound and never on the
point estimate — and why `NON_SYNTHETIC` exists on top of it.

**`NON_SYNTHETIC` is the half of F2 that closes the buy-a-tier-in-an-afternoon hole.** The interval
is a statement about a SAMPLE, and a sample the product generates is unbounded in `n` at a cost of
one command: `synthesise(..., n=189)` clears `hi <= 0.02` in an afternoon. So `BLOCKING`
additionally requires thirty filings **a person or the world produced**, whatever the total `n`.

*The alternative it beat:* forbidding synthetic filings from the FFR denominator entirely —
rejected because a foreign-engine corpus is genuinely informative about arithmetic predicates and
discarding it would cost real evidence. **The floor keeps the evidence and refuses the tier.**
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class CorpusProvenance(StrEnum):
    SELF_AUTHORED = "SELF-AUTHORED"
    BLIND_FILLED = "BLIND-FILLED"
    TEMPLATE_COMPUTED = "TEMPLATE-COMPUTED"
    REGISTER_DERIVED = "REGISTER-DERIVED"
    REAL_PARTNER = "REAL-PARTNER"
    PUBLIC = "PUBLIC"


ADMISSIBLE: Final[frozenset[CorpusProvenance]] = (
    frozenset(CorpusProvenance) - {CorpusProvenance.SELF_AUTHORED}
)

# F2 / F12: what a PERSON or THE WORLD produced, not what we generated.
NON_SYNTHETIC: Final[frozenset[CorpusProvenance]] = frozenset({
    CorpusProvenance.BLIND_FILLED,
    CorpusProvenance.REAL_PARTNER,
    CorpusProvenance.PUBLIC,
})

SYNTHETIC: Final[frozenset[CorpusProvenance]] = frozenset(CorpusProvenance) - NON_SYNTHETIC

UNINFORMATIVE_WORD: Final[str] = "uninformative"

# What a surface renders in place of a rate. NOT a number, and not an empty cell either: an empty
# cell is read as "we did not get round to it".
UNINFORMATIVE_RENDER: Final[str] = "— uninformative (SELF-AUTHORED)"


class UninformativeCorpusError(RuntimeError):
    """The corpus cannot license an FFR for this predicate.

    **RAISES rather than returning zero, and rather than returning a rate with a caveat**, so that
    no code path can carry an uninformative number forward. A caveat is a string somebody drops
    when they reformat a table; an exception is not.
    """


def person_a_kind_note(kind: str) -> str:
    """What renders wherever an FFR renders, when Person A was not a human.

    The fallback is weaker than a human and the record says so. It does not silently become a
    `BLIND-FILLED` number that looks like a person's.
    """
    if kind == "human":
        return ""
    return (
        f"person_a_kind: {kind} — the filler was not a human. The fallback is weaker than a human "
        "and this number carries that label wherever it renders."
    )
