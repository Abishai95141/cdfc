"""B2 — cross-document entity resolution. RECORDS are observed; ENTITIES are resolved.

## The shape, and why it is two node kinds rather than one

    RECORD    one row, in one document, at a span.        OBSERVED.
    ENTITY    one identity, resolved across records.      DERIVED, and it says so.

Collapsing them into a single "entity carrying a list of documents" loses the thing an auditor
needs: **which document actually said what**, versus **what we concluded from putting them side by
side**. A record is a fact about a file. An entity is a judgement about two files, and a judgement
belongs in a node that can be wrong and can be revised.

`ERKG` (DerwenAI) argues the same order from the other direction — **resolve entities BEFORE
building the graph**, because unresolved duplicates poison everything downstream. This system
already did that: `cdfc.correspond.link` runs before the evidence graph. What was missing was the
NODE, so the resolution existed and was invisible.

## The resolver is `cdfc.correspond.link`, unchanged

Fellegi-Sunter, with `m`, `u` and prevalence fitted by EM on **no labelled pairs**, scored against
Splink 4.0.16 in `N4`. Nothing here re-implements matching, and nothing here uses a model: an
entity resolved by an LLM would be a judgement nobody could re-derive, and `link` already refuses a
tie within `margin` bits rather than breaking it.

**`Linkage` partitions its input** — linked, ambiguous, unlinked — and refuses construction
otherwise, which is what stops a record vanishing between two documents.

## What an ambiguous resolution does

It becomes **two separate entities**, not one, and the refusal is recorded. Two candidate identities
of comparable weight is the same hazard as two pinned blanks sharing a sheet set: merging them
silently would put one filer's data under another's name, which is the worst thing this system
could do.

## GraphRAG's entities, and the lane they land in

`D3` measured GraphRAG producing **29 entities and 45 relationships** from 6,000 characters of the
pinned instrument, carrying `text_unit_ids` and **no span**. Those enter through `from_extracted`
and are marked `resolved_by="model"` — they are never merged with linkage-resolved entities and
never counted as evidenced, for the same reason `Derived` exists in the fill lane.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from cdfc.correspond.link import Comparison, Linkage, link


class ResolvedBy(StrEnum):
    """How an identity was arrived at. Never inferred from the data; always recorded."""

    LINKAGE = "linkage"        # Fellegi-Sunter over declared comparisons, EM-fitted, no model
    SINGLETON = "singleton"    # seen in one document only; nothing was resolved
    MODEL = "model"            # an LLM proposed it; DERIVED, never counted as evidenced


class EntityRefusal(StrEnum):
    AMBIGUOUS_LINK = "ambiguous_link"
    NO_COMPARABLE_FIELD = "no_comparable_field"


@dataclass(frozen=True, slots=True)
class Record:
    """One row of one document. The atom that is OBSERVED."""

    document: str
    row: int
    fields: Mapping[str, str]

    @property
    def id(self) -> str:
        return f"rec:{self.document}#{self.row}"

    def get(self, name: str) -> str:
        return str(self.fields.get(name, "") or "")


@dataclass(frozen=True, slots=True)
class Entity:
    """One resolved identity. DERIVED from records, and it names which."""

    id: str
    records: tuple[Record, ...]
    resolved_by: ResolvedBy
    weight: float | None = None        # log2 bits of evidence; None for singletons and model

    @property
    def documents(self) -> tuple[str, ...]:
        return tuple(sorted({r.document for r in self.records}))

    @property
    def is_cross_document(self) -> bool:
        return len(self.documents) > 1

    def label(self, field: str) -> str:
        for r in self.records:
            v = r.get(field)
            if v:
                return v
        return ""

    def as_canonical_obj(self) -> dict[str, Any]:
        return {
            "id": self.id, "resolved_by": self.resolved_by.value,
            "documents": list(self.documents),
            "records": [r.id for r in self.records],
            "weight": None if self.weight is None else repr(self.weight),
        }


@dataclass(frozen=True, slots=True)
class EntitySet:
    """Resolved entities, the records behind them, and every refusal. MUST partition the records."""

    entities: tuple[Entity, ...]
    records: tuple[Record, ...]
    refused: tuple[tuple[str, str, str], ...]      # (record id, reason, detail)
    linkage: Linkage | None = None

    def __post_init__(self) -> None:
        covered = [r.id for e in self.entities for r in e.records]
        if len(set(covered)) != len(covered):
            dupes = sorted({r for r in covered if covered.count(r) > 1})
            raise ValueError(
                f"{len(dupes)} record(s) belong to more than one entity, e.g. {dupes[:3]}. A "
                "record is one row of one document and it has one identity."
            )
        if set(covered) != {r.id for r in self.records}:
            missing = sorted({r.id for r in self.records} - set(covered))
            raise ValueError(
                f"{len(missing)} record(s) belong to no entity, e.g. {missing[:3]}. A resolution "
                "that drops a record reports a coverage it does not have."
            )

    def cross_document(self) -> tuple[Entity, ...]:
        return tuple(e for e in self.entities if e.is_cross_document)

    def counts(self) -> dict[str, int]:
        by = {k.value: 0 for k in ResolvedBy}
        for e in self.entities:
            by[e.resolved_by.value] += 1
        return {
            "records": len(self.records),
            "entities": len(self.entities),
            "cross_document": len(self.cross_document()),
            "refused": len(self.refused),
            **{f"by_{k}": v for k, v in sorted(by.items())},
        }

    def lines(self) -> tuple[str, ...]:
        c = self.counts()
        out = [
            f"records            {c['records']}",
            f"ENTITIES           {c['entities']}",
            f"  cross-document   {c['cross_document']}   (one identity, seen in more than one file)",
            f"  by linkage       {c['by_linkage']}",
            f"  singletons       {c['by_singleton']}",
            f"  model-proposed   {c['by_model']}   (DERIVED; never counted as evidenced)",
            f"refused            {c['refused']}",
        ]
        if self.linkage is not None:
            out += ["", *self.linkage.lines()]
        return tuple(out)


def records_from_rows(document: str, header: Sequence[str], rows: Sequence[Sequence[str]],
                      ) -> tuple[Record, ...]:
    """One `Record` per data row. The header names the fields; nothing is renamed."""
    return tuple(
        Record(document=document, row=i,
               fields={h: (r[j] if j < len(r) else "") for j, h in enumerate(header)})
        for i, r in enumerate(rows)
    )


def resolve(
    left: Sequence[Record],
    right: Sequence[Record],
    comparisons: Sequence[Comparison],
    *,
    margin: float = 1.0,
) -> EntitySet:
    """Resolve records across TWO documents into entities. Deterministic; no model.

    A linked pair becomes ONE entity spanning both documents. An ambiguous pair becomes TWO
    entities and a refusal — merging on a tie would put one filer's data under another's name.
    """
    if not comparisons:
        raise ValueError(
            "resolution with no declared comparison would link every record to every other. The "
            "fields being compared are a declaration, not a default."
        )
    if not left or not right:
        # Nothing to resolve ACROSS; every record is its own identity and the surface says so
        # rather than reporting an empty resolution as a successful one.
        recs = tuple([*left, *right])
        return EntitySet(
            entities=tuple(Entity(id=f"ent:{r.id}", records=(r,),
                                  resolved_by=ResolvedBy.SINGLETON) for r in recs),
            records=recs, refused=(), linkage=None,
        )

    lk = link([dict(r.fields) for r in left], [dict(r.fields) for r in right],
              comparisons, margin=margin)

    entities: list[Entity] = []
    refused: list[tuple[str, str, str]] = []
    paired_l: set[int] = set()
    paired_r: set[int] = set()
    for i, j, w in lk.pairs:
        paired_l.add(i)
        paired_r.add(j)
        entities.append(Entity(id=f"ent:{left[i].id}+{right[j].id}",
                               records=(left[i], right[j]),
                               resolved_by=ResolvedBy.LINKAGE, weight=w))
    for i, _j, n in lk.ambiguous:
        refused.append((left[i].id, EntityRefusal.AMBIGUOUS_LINK.value,
                        f"{n} candidates within {margin} bits; merged to none, kept separate"))
    for i, why in lk.unlinked:
        refused.append((left[i].id, EntityRefusal.NO_COMPARABLE_FIELD.value, why))

    for i, r in enumerate(left):
        if i not in paired_l:
            entities.append(Entity(id=f"ent:{r.id}", records=(r,),
                                   resolved_by=ResolvedBy.SINGLETON))
    for j, r in enumerate(right):
        if j not in paired_r:
            entities.append(Entity(id=f"ent:{r.id}", records=(r,),
                                   resolved_by=ResolvedBy.SINGLETON))

    return EntitySet(entities=tuple(sorted(entities, key=lambda e: e.id)),
                     records=tuple([*left, *right]), refused=tuple(sorted(refused)), linkage=lk)


def from_extracted(document: str, titles: Sequence[str], *, kind: str = "") -> EntitySet:
    """Entities an LLM proposed — GraphRAG's, or `cdfc.model.extract`'s. `resolved_by=MODEL`.

    They are NEVER merged with linkage-resolved entities here. A model's identity judgement and a
    Fellegi-Sunter one are different evidence, and averaging them would produce a graph where
    nobody can tell which is which. `D3` measured GraphRAG at 29 entities with no span; these
    carry the same standing as a `Derived` fill: present, useful, not counted as checked.
    """
    recs = tuple(Record(document=document, row=i, fields={"title": t, "type": kind})
                 for i, t in enumerate(titles) if str(t).strip())
    return EntitySet(
        entities=tuple(Entity(id=f"ent:model:{document}#{r.row}", records=(r,),
                              resolved_by=ResolvedBy.MODEL) for r in recs),
        records=recs, refused=(), linkage=None,
    )
