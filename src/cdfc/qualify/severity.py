"""P8-B4 — severity tiers, keyed on the Wilson UPPER bound and floored on non-synthetic filings.

    hi <= 0.02  AND  n_non_synthetic >= 30   ->  BLOCKING
    hi <= 0.10                               ->  ADVISORY
    hi  > 0.10                               ->  NOT ADMITTED   (this IS gate G4)

**Why the upper bound and not the point estimate.** `0 fires / 4 filings` has a point estimate of
`0.000` and an interval of `[0.000, 0.490]`. A rule keyed on the point estimate would let a sample
of four buy `BLOCKING`. The upper bound makes the tier a statement about EVIDENCE rather than LUCK.

**Why the upper bound alone was still not enough — the second half of F2.** The interval is a
statement about a SAMPLE, and a sample the product generates is unbounded in `n` at a cost of one
command: `synthesise(..., n=189)` clears `hi <= 0.02` in an afternoon. So `BLOCKING` additionally
requires **thirty filings a person or the world produced**, whatever the total `n`.

*The alternative it beat:* forbidding synthetic filings from the FFR denominator entirely —
rejected because a foreign-engine corpus is genuinely informative about arithmetic predicates and
discarding it would cost real evidence. **The floor keeps the evidence and refuses the tier.**

**The consequence, stated in advance so nobody is surprised.** On day one almost nothing is
`BLOCKING`: a predicate needs `n >= 189` clean non-self-authored filings with zero fires to clear
`0.02` on the upper bound, AND thirty of them must be non-synthetic. Everything enters as
`ADVISORY` **with its interval printed beside it**. That is the EBA's warnings-first convention
with the measurement put back in.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any, Final

from cdfc.qualify.corpus.provenance import CorpusProvenance, UninformativeCorpusError

# PRE-REGISTERED, all three together, inside `experiments/P8/PREREGISTRATION.md`'s hash.
BLOCKING_MAX: Final[Decimal] = Decimal("0.02")
ADVISORY_MAX: Final[Decimal] = Decimal("0.10")
BLOCKING_MIN_NON_SYNTHETIC: Final[int] = 30  # F2 / F12


class Severity(StrEnum):
    BLOCKING = "BLOCKING"
    ADVISORY = "ADVISORY"
    NOT_ADMITTED = "NOT ADMITTED"


@dataclass(frozen=True, slots=True)
class TierDecision:
    tier: Severity
    reason: str
    wilson_hi: Decimal
    n: int
    n_non_synthetic: int

    def render(self) -> str:
        """The tier NEVER renders without its interval and both integers of its denominator."""
        return (
            f"{self.tier.value} — Wilson hi {self.wilson_hi}, n={self.n}, "
            f"n_non_synthetic={self.n_non_synthetic}/{BLOCKING_MIN_NON_SYNTHETIC} required for "
            f"BLOCKING. {self.reason}"
        )


def tier(g4: Mapping[str, Any]) -> TierDecision:
    """The tier for one `g4` record. Raises rather than defaulting where the tier is UNDEFINED."""
    provenance = g4.get("corpus_provenance")
    if provenance == CorpusProvenance.SELF_AUTHORED.value:
        raise UninformativeCorpusError(
            "severity_tier is UNDEFINED on a SELF-AUTHORED corpus, not defaulted to ADVISORY. "
            "A default here is the uninformative number arriving with a label attached."
        )
    if g4.get("clean_corpus_independent_of_predicate") is not True:
        raise UninformativeCorpusError(
            "severity_tier is UNDEFINED where the corpus is not independent of the predicate "
            "(F5). The predicate would be re-checking our answer against our answer."
        )

    hi = Decimal(str(g4["wilson"][1]))
    n = int(g4["n"])
    n_ns = int(g4["n_non_synthetic"])

    if hi > ADVISORY_MAX:
        return TierDecision(Severity.NOT_ADMITTED,
                            f"the Wilson upper bound exceeds {ADVISORY_MAX}", hi, n, n_ns)
    if hi <= BLOCKING_MAX and n_ns < BLOCKING_MIN_NON_SYNTHETIC:
        # THE ADVERSARY'S ONE-COMMAND ATTACK, REFUSED. The evidence is kept; the tier is not.
        return TierDecision(
            Severity.ADVISORY,
            f"the interval clears {BLOCKING_MAX}, but BLOCKING requires "
            f"{BLOCKING_MIN_NON_SYNTHETIC} filings a person or the world produced and this corpus "
            f"has {n_ns}. A sample the product generates is unbounded in n at a cost of one "
            "command.",
            hi, n, n_ns,
        )
    if hi <= BLOCKING_MAX:
        return TierDecision(Severity.BLOCKING,
                            f"the interval clears {BLOCKING_MAX} on {n_ns} non-synthetic filings",
                            hi, n, n_ns)
    return TierDecision(Severity.ADVISORY,
                        f"the interval clears {ADVISORY_MAX} but not {BLOCKING_MAX}", hi, n, n_ns)
