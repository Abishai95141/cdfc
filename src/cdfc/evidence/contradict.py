"""A3 — *"here are the values your own documents contradict; here is what nothing supports."*

Three states, and **the third is the one this product exists to say**:

    CONTRADICTED   a rule binds this field to a quantity the source states DIFFERENTLY
    SUPPORTED      the source states this exact value
    NOT_ASSESSED   nothing in the corpus bears on it

**CONTRADICTED requires a RULE, and that is not a limitation to apologise for.** *"The filing says
380,000 and the corpus says 500,000"* is only a contradiction if something establishes those two
numbers are about the same quantity. Without that, two different numbers in two documents are two
different numbers. The rule supplies it — which is why A3 composes with the admitted rules of the
evidence layer rather than standing alone, and why a system with no admitted rules can report
SUPPORTED and NOT_ASSESSED but honestly cannot report a single contradiction.

**Exact matching only** (`W0-C`): similarity reported SUPPORTED 20 of 20 for values that had been
DELETED from the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cdfc.evidence.observe import Observation, canonical


class Standing(StrEnum):
    CONTRADICTED = "contradicted"
    SUPPORTED = "supported"
    NOT_ASSESSED = "not_assessed"


class NotAssessed(StrEnum):
    """Why a filed value could not be assessed. CLOSED — `absent != empty != zero`."""

    NO_OBSERVATION = "no_observation"
    """The corpus states nothing matching this value. **NOT 'the value is wrong'** — it is the
    honest report that our documents do not speak to it."""

    FIELD_EMPTY = "field_empty"
    """The filer wrote nothing. Distinct from a zero and from an absence in the corpus."""

    NO_RULE_BINDS_IT = "no_rule_binds_it"
    """An observation exists but nothing establishes it is about THIS field, so a disagreement
    between them would not be a contradiction."""

    ATTESTATION_NOT_A_MEASUREMENT = "attestation_not_a_measurement"
    """The field asks the filer to CERTIFY, and no observation settles a certification (`N2`).

    **This was found by A3's first run producing a contradiction that should not exist.** A
    hand-supplied binding put the Second Schedule's net-worth threshold against
    `8. Compliance Status!C6` — which holds `Yes`, because the return never asks for the figure
    (`F6`). Comparing a money amount to a certification is a category error, and it produced the
    headline finding of the whole phase out of nothing. `G-TYPE` would have refused that binding;
    A3 now refuses it too, because a declaration must not depend on a caller having been careful."""


@dataclass(frozen=True, slots=True)
class Assessment:
    field: str
    filed: str
    standing: Standing
    reason: NotAssessed | None = None
    evidence: tuple[Observation, ...] = ()
    expected: str = ""

    def line(self) -> str:
        if self.standing is Standing.CONTRADICTED:
            o = self.evidence[0]
            return (f"{self.field}: filed {self.filed!r}, but {o.document} p{o.page} states "
                    f"{self.expected!r}")
        if self.standing is Standing.SUPPORTED:
            o = self.evidence[0]
            return f"{self.field}: {self.filed!r} — {o.document} p{o.page}"
        return f"{self.field}: {self.filed!r} — {self.reason.value if self.reason else '?'}"


@dataclass(frozen=True, slots=True)
class Declaration:
    contradicted: tuple[Assessment, ...]
    supported: tuple[Assessment, ...]
    not_assessed: tuple[Assessment, ...]
    observations: int
    source_document: str

    def __post_init__(self) -> None:
        # Every filed value lands in exactly one state. A field in none of them has been dropped.
        pass

    @property
    def total(self) -> int:
        return len(self.contradicted) + len(self.supported) + len(self.not_assessed)

    def lines(self) -> tuple[str, ...]:
        out = [
            f"source corpus     {self.source_document}",
            f"  observations    {self.observations}  (exact match only; W0-C killed similarity)",
            "",
            f"of {self.total} filed values:",
            f"  CONTRADICTED    {len(self.contradicted)} of {self.total}",
            f"  SUPPORTED       {len(self.supported)} of {self.total}",
            f"  NOT ASSESSED    {len(self.not_assessed)} of {self.total}",
        ]
        if self.contradicted:
            out += ["", "your own documents contradict these:"]
            out += [f"  {a.line()}" for a in self.contradicted]
        by: dict[str, int] = {}
        for a in self.not_assessed:
            k = a.reason.value if a.reason else "?"
            by[k] = by.get(k, 0) + 1
        if by:
            out += ["", "not assessed, by reason:"]
            out += [f"  {k:20} {v} of {self.total}" for k, v in sorted(by.items())]
        return tuple(out)


def assess(
    filed: dict[str, str],
    observed: dict[str, tuple[Observation, ...]],
    *,
    bindings: dict[str, str] | None = None,
    attestations: frozenset[str] = frozenset(),
    source_document: str = "",
) -> Declaration:
    """Assess every filed value. `bindings` maps a field to the value the RULES say it must equal.

    A field with a binding whose filed value differs from the bound value is CONTRADICTED — and
    only then. Without a binding, a filed value that appears in the corpus is SUPPORTED and one
    that does not is NOT_ASSESSED, never 'wrong'.
    """
    bindings = bindings or {}
    con: list[Assessment] = []
    sup: list[Assessment] = []
    na: list[Assessment] = []

    for field, value in sorted(filed.items()):
        if not str(value).strip():
            na.append(Assessment(field, value, Standing.NOT_ASSESSED, NotAssessed.FIELD_EMPTY))
            continue
        key = canonical(str(value))
        hits = observed.get(key, ())

        if field in attestations:
            # No observation settles a certification. A binding pointed at one is a category
            # error, and A3's first run turned exactly that into a false headline contradiction.
            na.append(Assessment(field, value, Standing.NOT_ASSESSED,
                                 NotAssessed.ATTESTATION_NOT_A_MEASUREMENT))
            continue

        if field in bindings:
            want = canonical(bindings[field])
            if want != key:
                ev = observed.get(want, ())
                con.append(Assessment(field, value, Standing.CONTRADICTED,
                                      evidence=ev, expected=bindings[field]))
                continue
            sup.append(Assessment(field, value, Standing.SUPPORTED, evidence=hits))
            continue

        if hits:
            # The value is in the corpus, but nothing says this observation is about THIS field.
            na.append(Assessment(field, value, Standing.NOT_ASSESSED,
                                 NotAssessed.NO_RULE_BINDS_IT, evidence=hits))
            continue
        na.append(Assessment(field, value, Standing.NOT_ASSESSED, NotAssessed.NO_OBSERVATION))

    return Declaration(
        contradicted=tuple(con), supported=tuple(sup), not_assessed=tuple(na),
        observations=sum(len(v) for v in observed.values()),
        source_document=source_document,
    )
