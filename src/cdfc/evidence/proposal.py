"""LAYER 2 — a model's `rule -> field` bindings, arriving AS DATA and trusted for nothing.

**The model is not called from here.** It writes a JSON file; this module reads it. That is the
whole seam, and it is what lets `tests/negative/importgraph.py` prove no model reaches a verdict:
there is no client to import because there is no call to make.

Validation here is for SHAPE ONLY -- is this a well-formed record with the fields a gate will
need. Whether the quote is real, the field exists, the type fits, the vocabulary covers the terms
or the cross-references resolve are five separate questions, and every one of them belongs to
`gates.py`. A loader that started deciding those would be a loader nobody could audit.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from cdfc.evidence.vocabulary import RuleKind


class MalformedProposal(ValueError):
    """The file is not a set of proposals. Distinct from a proposal a gate refused."""


@dataclass(frozen=True, slots=True)
class Proposal:
    """One claim: *this provision, quoting these bytes, governs this field, in this way.*"""

    eid: str                              # the provision it cites
    quote: str                            # the bytes it claims are there, verbatim
    kind: RuleKind
    field_ref: str | None = None          # the field it governs; None for DEFINITION/APPLICABILITY
    terms: tuple[str, ...] = ()           # the vocabulary it requires of an ENUM field
    refers_to: tuple[str, ...] = ()       # eIds it cross-references
    note: str = ""                        # free model text. NEVER reaches a verdict or a surface.
    planted: str = ""                     # a deliberately wrong proposal, for the controls

    @property
    def is_planted(self) -> bool:
        return bool(self.planted)


@dataclass(frozen=True, slots=True)
class ProposalSet:
    source: str
    proposals: tuple[Proposal, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        return len(self.proposals)

    @property
    def planted(self) -> tuple[Proposal, ...]:
        return tuple(p for p in self.proposals if p.is_planted)


_REQUIRED = ("eid", "quote", "kind")


def parse(rows: Sequence[dict], *, source: str = "<memory>") -> ProposalSet:
    out: list[Proposal] = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            raise MalformedProposal(f"{source}[{i}] is {type(r).__name__}, not an object")
        missing = [k for k in _REQUIRED if not r.get(k)]
        if missing:
            raise MalformedProposal(
                f"{source}[{i}] omits {missing}. A proposal without a provision, a quote and a "
                "kind cannot be adjudicated -- and a loader that filled a default here would be "
                "authoring the claim it is supposed to be checking."
            )
        try:
            kind = RuleKind(r["kind"])
        except ValueError as e:
            raise MalformedProposal(
                f"{source}[{i}] kind={r['kind']!r} is outside the closed vocabulary "
                f"{[k.value for k in RuleKind]}"
            ) from e
        out.append(Proposal(
            eid=str(r["eid"]),
            quote=str(r["quote"]),
            kind=kind,
            field_ref=(str(r["field"]) if r.get("field") else None),
            terms=tuple(str(t) for t in (r.get("terms") or ())),
            refers_to=tuple(str(t) for t in (r.get("refers_to") or ())),
            note=str(r.get("note") or ""),
            planted=str(r.get("planted") or ""),
        ))
    return ProposalSet(source=source, proposals=tuple(out))


def load(path: Path) -> ProposalSet:
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise MalformedProposal(f"{path} is not JSON: {e}") from e
    if not isinstance(rows, list):
        raise MalformedProposal(f"{path} holds {type(rows).__name__}, expected a list")
    return parse(rows, source=str(path))
