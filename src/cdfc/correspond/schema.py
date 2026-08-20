"""A1c use 2 — a SOURCE COLUMN to a TEMPLATE FIELD. Schema matching, on declared evidence.

Use 1 aligns two revisions of the same form and can use structure, because they share an address
space. **Here there is no shared address space at all**: a custodian export and a regulator's
template have nothing in common but meaning. So the evidence is what each side DECLARES —

    the header text        a source column names itself
    the declared type      money, percent, date, enum, read from the workbook (`N2`)
    the value shape        do the column's values look like that type's values
    the vocabulary         an enum field's own validation list

and the weights over that evidence are **derived by the same Fellegi-Sunter EM as use 3**, not
chosen. `W0-C` is why: a similarity threshold reported SUPPORTED 20 of 20 for values that had been
DELETED. One component, three uses, one way of deciding.

**A tie is refused.** Two template fields that fit a column equally well is the same hazard as two
pinned blanks sharing a sheet set.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final
from pathlib import Path

from cdfc.correspond.link import Comparison, estimate
from cdfc.evidence.fields import Field, FieldSet
from cdfc.evidence.vocabulary import FieldType

_WORD = re.compile(r"[a-z0-9]+")
_MONEY = re.compile(r"^-?[0-9][0-9,]*(\.[0-9]+)?$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$|^\d{2}[-/]\d{2}[-/]\d{4}$")
_PCT = re.compile(r"^-?[0-9.]+\s*%$")


@dataclass(frozen=True, slots=True)
class SourceColumn:
    """One column of an uploaded export: what it calls itself and what it holds."""

    name: str
    values: tuple[str, ...]

    def shape(self) -> FieldType:
        """What the VALUES look like. Not what the header claims -- headers lie, values do not."""
        seen = [v for v in self.values if str(v).strip()][:50]
        if not seen:
            return FieldType.UNDECLARED
        if all(_PCT.match(str(v).strip()) for v in seen):
            return FieldType.PERCENT
        if all(_DATE.match(str(v).strip()) for v in seen):
            return FieldType.DATE
        if all(_MONEY.match(str(v).strip()) for v in seen):
            return FieldType.MONEY
        return FieldType.TEXT


# Tokens that appear in so many labels that their presence is not evidence. MEASURED over the FME
# return's 132 labelled fields, not chosen from a list: `of` occurs in **73 of 132** and `the` in
# **45**, so `header_token_overlap` fired on more than half the surface for any label containing
# one — and as a BINARY bit, a match on `of` was indistinguishable from a match on `investors`.
# That is why `Number of investors` scored a hit against `Category of Registration of FME`.
#
# The list is closed and short on purpose. A longer stopword list would start removing words that
# ARE evidence in a regulatory label (`fee`, `date`, `name`), and the fix for a weak signal is to
# stop counting the uninformative one, not to guess which words matter.
STOPWORDS: Final[frozenset[str]] = frozenset({
    "of", "the", "a", "an", "and", "or", "to", "in", "for", "on", "at", "by", "with", "as",
    "is", "are", "be", "if", "any", "all", "its", "it", "this", "that", "from", "under",
})


def _tokens(s: str) -> frozenset[str]:
    """Informative tokens of a label. Stopwords removed — see `STOPWORDS`."""
    return frozenset(_WORD.findall(s.casefold())) - STOPWORDS


@dataclass(frozen=True, slots=True)
class SchemaMatch:
    pairs: tuple[tuple[str, str, float], ...]       # (column name, field ref, weight)
    refused: tuple[tuple[str, str], ...]            # (column name, why)
    columns: int
    fields: int
    m: tuple[float, ...] = ()
    u: tuple[float, ...] = ()

    def lines(self) -> tuple[str, ...]:
        out = [
            f"source columns    {self.columns}",
            f"template fields   {self.fields}",
            f"MATCHED           {len(self.pairs)} of {self.columns}",
            f"  refused         {len(self.refused)}",
        ]
        if self.m:
            out.append("  weights DERIVED by EM, not chosen: "
                       + " ".join(f"m={a:.3f}/u={b:.3f}" for a, b in zip(self.m, self.u)))
        return tuple(out)


# The four pieces of declared evidence, in the order their weights are reported.
EVIDENCE = ("header_token_overlap", "declared_type_matches_value_shape",
            "value_in_field_vocabulary", "header_equals_label")


def _gamma(col: SourceColumn, f: Field) -> tuple[bool, ...]:
    ct, lt = _tokens(col.name), _tokens(f.label)
    overlap = bool(ct & lt)
    type_ok = f.type is not FieldType.UNDECLARED and col.shape() is f.type
    vocab_ok = bool(f.vocabulary) and any(
        str(v).strip().casefold() in {x.casefold() for x in f.vocabulary}
        for v in col.values if str(v).strip())
    exact_name = ct == lt and bool(ct)
    return (overlap, type_ok, vocab_ok, exact_name)


def match(columns: list[SourceColumn], fields: FieldSet, *, margin: float = 1.0) -> SchemaMatch:
    """Match each source column to at most one template field, or refuse it."""
    targets = list(fields.fields)
    if not columns or not targets:
        return SchemaMatch((), tuple((c.name, "no candidate fields") for c in columns),
                           len(columns), len(targets))

    gammas = [(i, j, _gamma(c, f)) for i, c in enumerate(columns) for j, f in enumerate(targets)]
    w = estimate(gammas, len(EVIDENCE))
    scored = sorted(((w.score(g), i, j) for i, j, g in gammas), reverse=True)

    best: dict[int, list[float]] = {}
    for s, i, _j in scored:
        best.setdefault(i, []).append(s)

    taken_j: set[int] = set()
    done_i: set[int] = set()
    pairs: list[tuple[str, str, float]] = []
    refused: list[tuple[str, str]] = []
    for s, i, j in scored:
        if i in done_i or j in taken_j or s <= 0:
            continue
        runners = best.get(i, [])
        second = runners[1] if len(runners) > 1 else float("-inf")
        if s - second < margin:
            refused.append((columns[i].name,
                            f"two fields fit within {margin} bits; a tie is not a match"))
            done_i.add(i)
            continue
        pairs.append((columns[i].name, targets[j].ref, s))
        done_i.add(i)
        taken_j.add(j)
    for i, c in enumerate(columns):
        if i not in done_i:
            refused.append((c.name, "no field carries evidence for it"))

    return SchemaMatch(tuple(sorted(pairs)), tuple(sorted(refused)),
                       len(columns), len(targets), m=w.m, u=w.u)


def columns_from_rows(header: list[str], rows: list[list[str]]) -> list[SourceColumn]:
    """A source export as columns. The shape a CSV or a custodian feed arrives in."""
    return [SourceColumn(name=h, values=tuple(str(r[i]) for r in rows if i < len(r)))
            for i, h in enumerate(header)]
