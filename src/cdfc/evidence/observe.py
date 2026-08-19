"""A3 — observations located in a source document, by EXACT match and nothing else.

**`W0-C` is why there is no similarity here at all.** Under similarity matching, values that had
been DELETED from the corpus were reported SUPPORTED **20 of 20**, across all three deletion
strata, at every threshold tried. Under exact matching, **0 of 20**. That is not a tuning problem
with a better threshold behind it: a similarity score has no representation for *absent*, so it
answers the question it was asked with the nearest thing it can find.

So an observation exists only where the source document contains the value's exact bytes, and the
span it cites re-reads to those bytes. Anything else is `NOT_ASSESSED`, which is a state this
system is built to say out loud.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cdfc.qualify.textsource import InstrumentText


@dataclass(frozen=True, slots=True)
class Observation:
    """One value, found at one place in one document. The span is the evidence."""

    value: str
    document: str
    span: tuple[int, int]
    page: int | None
    context: str          # the surrounding sentence, for a human to judge

    def reverify(self, source: InstrumentText) -> bool:
        """Re-read the cited span and require the exact bytes back.

        A locator that cannot reproduce what it claims to have found is not evidence, and this is
        the cheapest possible check on it — the same discipline `G-QUOTE` applies to a provision.
        """
        lo, hi = self.span
        if not (0 <= lo <= hi <= len(source.text)):
            return False
        return source.text[lo:hi] == self.value


# A money amount as this instrument writes them, including the Indian grouping `5,00,000`.
MONEY = re.compile(r"(?:USD|INR|Rs\.?)\s*([0-9][0-9,]{2,})")
# A bare grouped number, which is how a filed figure most often appears.
NUMBER = re.compile(r"\b([0-9]{1,3}(?:,[0-9]{2,3})+|[0-9]{4,})\b")


def observe(source: InstrumentText, *, patterns: tuple[re.Pattern[str], ...] = (MONEY, NUMBER),
            ) -> tuple[Observation, ...]:
    """Every quantity the source document states, with the span that proves it.

    Deliberately a small, closed set of patterns. A general extractor would find more and would
    need a model to decide what it found; this finds what it can name, and everything it cannot
    find leaves its field `NOT_ASSESSED` rather than unsupported.
    """
    out: list[Observation] = []
    for pat in patterns:
        for m in pat.finditer(source.text):
            span = (m.start(1), m.end(1))
            if source.is_disputed(span):
                # The extractors disagreed about these bytes. An observation drawn from a disputed
                # region would carry a value neither of them vouches for.
                continue
            unit = source.unit_at(span)
            lo = max(0, m.start() - 60)
            out.append(Observation(
                value=m.group(1),
                document=source.instrument_id,
                span=span,
                page=(unit.page if unit else None),
                context=" ".join(source.text[lo:m.end() + 60].split()),
            ))
    # Deterministic order: by position. Two runs over the same bytes give the same list.
    return tuple(sorted(out, key=lambda o: (o.span, o.value)))


def index(observations: tuple[Observation, ...]) -> dict[str, tuple[Observation, ...]]:
    """`value -> every place it was observed`. The key is the EXACT string, normalised only for
    the grouping separators a filer and a statute write differently."""
    out: dict[str, list[Observation]] = {}
    for o in observations:
        out.setdefault(canonical(o.value), []).append(o)
    return {k: tuple(v) for k, v in out.items()}


def canonical(value: str) -> str:
    """Strip grouping separators and a trailing decimal zero — NOTHING else.

    `5,00,000` and `500000` are the same number written by two conventions, and refusing to see
    that would report a contradiction that is a typographic difference. Rounding, unit conversion
    and scale inference are all excluded: each would be a judgement, and a judgement here is the
    similarity failure wearing a different name.
    """
    v = value.strip().replace(",", "").replace(" ", "")
    if "." in v:
        v = v.rstrip("0").rstrip(".")
    return v
