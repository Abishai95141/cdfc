"""P10-B4 — the demonstrated survivors. **Exhibits, not reasons.**

The Unchecked panel's strongest row is not an argument that a class of falsehood is unreachable.
It is a *file*, with a content hash, that no admitted check rejects — and the difference matters,
because a reason can be disputed and an exhibit can be opened.

## Two families, and the second is this document's contribution

| family | construction | why it is unkillable |
|---|---|---|
| **E1 — the coordinated misstatement** | scale every quantity in one connected component of the carry graph by the same factor | internally perfect under every cross-sheet carry and every SUM identity. In code mutation a mutant that changes behaviour is in principle killable by *some* test; **here a mutant changes the TRUTH of the artifact and is provably unkillable by any predicate over the artifact alone** |
| **E2 — the categorical swap inside the vocabulary** | change a categorical cell to another **legal** member of its own controlled vocabulary | passes every membership predicate **by construction**, and it lands in the field-surface cells that feed no template formula at all, so no recompute, carry or sum identity can reach it either. **A one-character edit that changes what the scheme IS, and that nothing in the artifact contradicts** |

E2 matters because **E1 is a construction and E2 is a measurement**: the recompute-blind set is
computed from the regulator's own formula graph by `probes/precedents.py`, and the swap is legal by
the regulator's own data validation. Both facts are in the artifact; neither is our opinion.

## Exhibits render as exhibits

Every exhibit carries `CDFC_SYNTHETIC = true`, a content hash, and a construction description —
and **no reason code**. A reason code would put it in the same vocabulary as a finding about the
filer's document, and it is not one: it is a statement about the limits of the instrument.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

Family = Literal["E1", "E2"]

# Carried on every exhibit and rendered beside it. An exhibit that could be mistaken for a real
# filing is a fixture that will eventually be quoted as one.
SYNTHETIC: Final[str] = "CDFC_SYNTHETIC"


class ExhibitError(ValueError):
    """An exhibit that must not be rendered."""


@dataclass(frozen=True, slots=True)
class Exhibit:
    family: Family
    title: str
    construction: str            # HOW it was built, in one sentence a reader can re-perform
    content_sha256: str
    cells: tuple[str, ...]       # the cells it changes, named
    survives_against: str        # the rejector set it was shown to survive, NAMED
    why_unkillable: str

    def __post_init__(self) -> None:
        if not self.content_sha256 or len(self.content_sha256) != 64:
            raise ExhibitError(
                f"{self.family}: an exhibit with no content hash cannot be opened by a reader, "
                "so it is a reason wearing an exhibit's clothes"
            )
        if not self.construction.strip():
            raise ExhibitError(f"{self.family}: an exhibit with no construction cannot be re-built")
        if not self.survives_against.strip():
            raise ExhibitError(
                f"{self.family}: 'survives' is meaningless without the set it survived. An "
                "exhibit that survives an EMPTY admitted set survives nothing."
            )

    def as_row(self) -> dict[str, Any]:
        return {
            SYNTHETIC: True,
            "family": self.family,
            "title": self.title,
            "construction": self.construction,
            "content_sha256": self.content_sha256,
            "cells": list(self.cells),
            "survives_against": self.survives_against,
            "why_unkillable": self.why_unkillable,
        }


def render(exhibits: Sequence[Exhibit]) -> str:
    """The Unchecked panel's exhibit block. **A content hash and a construction, and no reason.**"""
    if not exhibits:
        raise ExhibitError(
            "refusing to render an empty exhibit block. `|RESIDUE| > 0` with no exhibit is a claim "
            "about a population nobody can open."
        )
    out = ["UNCHECKED — demonstrated survivors", ""]
    for e in exhibits:
        out += [
            f"  [{e.family}] {e.title}",
            f"        content   sha256:{e.content_sha256}",
            f"        synthetic {SYNTHETIC} = true",
            f"        cells     {', '.join(e.cells)}",
            f"        built by  {e.construction}",
            f"        survives  {e.survives_against}",
            f"        why       {e.why_unkillable}",
            "",
        ]
    return "\n".join(out)


def recompute_blind(precedent_map: Any, field_surface: frozenset[str]) -> frozenset[str]:
    """Field-surface cells that feed **no** template formula — E2's landing ground.

    Computed from the regulator's own formula graph rather than asserted: `pm.reachable` is the
    union of every formula cell's field-surface precedents under the `transitive` reading, so the
    complement is exactly the set no recompute, carry or sum identity can reach.
    """
    return field_surface - precedent_map.reachable


def e2_candidates(
    vocabularies: Mapping[str, Sequence[str]],
    cell_of_vocab: Mapping[str, str],
    blind: frozenset[str],
) -> tuple[tuple[str, str, str], ...]:
    """`(cell, from_member, to_member)` for every legal swap that lands in the blind set.

    A **two-member** vocabulary is the strongest form: there is exactly one other legal value, so
    the swap is forced rather than chosen, and no membership predicate can distinguish the two.
    """
    out: list[tuple[str, str, str]] = []
    for slug, members in sorted(vocabularies.items()):
        cell = cell_of_vocab.get(slug)
        if cell is None or cell not in blind or len(members) < 2:
            continue
        out.append((cell, str(members[0]), str(members[1])))
    return tuple(out)
