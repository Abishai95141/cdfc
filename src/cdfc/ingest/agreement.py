"""The agreement vector — and the rule that it is published as TWO vectors, never one.

A single `/72` figure averages an external check (a library nobody here wrote) with a
self-check (two implementations by the same author) and reports the result as one
instrument. That is the shared-denominator error in an agreement matrix, so it is banned
on every surface and `test_contract__agreement_renders_as_two_vectors` asserts it.

Cell labels:
  AGREE                 every party present produced the same value
  DISAGREE_ESCALATED    parties disagree and no pinned mechanism explains it -> INVALID
  DISAGREE_PINNED       the disagreement is a known, named, measured mechanism
  NOT_COMPARABLE        a party is excluded, or its exclusion was never measured here
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from cdfc.ingest.competence import (
    AGREEMENT_FIELDS,
    COMPETENCE,
    EXCLUSION_MECHANISM,
    STRUCTURAL_FIELDS,
    THREE_PARTY_FIELDS,
    TWO_PARTY_FIELDS,
    Instrument,
)
from cdfc.verdict.invalid import InvalidCause


class Label(StrEnum):
    AGREE = "AGREE"
    DISAGREE_ESCALATED = "DISAGREE_ESCALATED"
    DISAGREE_PINNED = "DISAGREE_PINNED"
    NOT_COMPARABLE = "NOT_COMPARABLE"


@dataclass(frozen=True)
class Cell:
    field: str
    workbook: str
    label: Label
    values: dict[str, Any]
    mechanism: str | None = None
    second_party: str | None = None


@dataclass(frozen=True)
class Agreement:
    cells: tuple[Cell, ...]
    invalid_cause: InvalidCause | None

    def by_field(self, field: str) -> tuple[Cell, ...]:
        return tuple(c for c in self.cells if c.field == field)

    def vector(self, fields: tuple[str, ...]) -> tuple[int, int]:
        """(agreeing cells, comparable cells) over the named fields."""
        cells = [c for c in self.cells if c.field in fields]
        comparable = [c for c in cells if c.label is not Label.NOT_COMPARABLE]
        return sum(1 for c in comparable if c.label is Label.AGREE), len(comparable)

    @property
    def three_party(self) -> tuple[int, int]:
        """The only vector containing an instrument nobody here wrote."""
        return self.vector(THREE_PARTY_FIELDS)

    @property
    def same_author(self) -> tuple[int, int]:
        """A/A′ only. Labelled SAME-AUTHOR wherever it is rendered."""
        return self.vector(TWO_PARTY_FIELDS)


def compare(
    workbook_sha8: str,
    views: Mapping[Instrument, Mapping[str, Any]],
    *,
    blind_controls: Mapping[str, int] | None = None,
) -> Agreement:
    cells: list[Cell] = []
    escalated = False

    for field in AGREEMENT_FIELDS:
        comp = COMPETENCE[field]
        present = {i: v[field] for i, v in views.items() if field in v}

        # A party excluded from the field is not compared. A party whose exclusion was
        # never measured on THIS workbook is also not compared — that cell is
        # NOT_COMPARABLE(competence_unmeasured), never AGREE.
        eligible = {i: val for i, val in present.items() if i in comp.parties}
        if workbook_sha8 not in comp.measured_on and len(comp.parties) < len(Instrument):
            cells.append(
                Cell(field, workbook_sha8, Label.NOT_COMPARABLE, dict(eligible),
                     mechanism="competence_unmeasured",
                     second_party=None)
            )
            continue

        if len(eligible) < 2:
            cells.append(
                Cell(field, workbook_sha8, Label.NOT_COMPARABLE, dict(eligible),
                     mechanism="fewer than two competent parties",
                     second_party=None)
            )
            continue

        vals = list(eligible.values())
        if all(v == vals[0] for v in vals):
            cells.append(Cell(field, workbook_sha8, Label.AGREE, dict(eligible),
                              second_party=sorted(str(i) for i in eligible)[1]))
            continue

        mech = EXCLUSION_MECHANISM.get(field)
        if mech and Instrument.B in eligible:
            cells.append(Cell(field, workbook_sha8, Label.DISAGREE_PINNED, dict(eligible),
                              mechanism=mech,
                              second_party=str(Instrument.B)))
        else:
            cells.append(Cell(field, workbook_sha8, Label.DISAGREE_ESCALATED, dict(eligible),
                              mechanism=None,
                              second_party=sorted(str(i) for i in eligible)[1]))
            if field in STRUCTURAL_FIELDS:
                escalated = True

    return Agreement(
        tuple(cells),
        InvalidCause.READER_STRUCTURAL_DISAGREEMENT if escalated else None,
    )
