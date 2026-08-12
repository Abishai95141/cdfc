"""The pinned fault taxonomy, parsed from `docs/FAULT-MODEL-v3.md`.

**The ids live in the document, not here.** A predicate's `claims_fault_classes` is validated
against this parse, and P6's executable model reads the same table. A Python constant listing
the ids beside the document would be a second list, and the one that drifts is the one nobody
is reading.

The parse asserts the class count. A row lost to a bad edit would otherwise shrink the
denominator of every `K/O` in the programme without anything going red.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Final

MODEL_VERSION: Final[str] = "v3"
EXPECTED_CLASSES: Final[int] = 14

_DOC: Final[Path] = Path(__file__).resolve().parents[3] / "docs" / "FAULT-MODEL-v3.md"
_ROW = re.compile(r"^\|\s*(F\d{2})\s*\|")


class FaultModelError(ValueError):
    """The pinned taxonomy could not be read, or does not say what it must say."""


@dataclass(frozen=True, slots=True)
class FaultClass:
    id: str
    name: str
    operator: str
    applies_to: tuple[str, ...]
    scope: str
    rationale: str


def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


@lru_cache(maxsize=1)
def fault_classes(doc: Path | None = None) -> dict[str, FaultClass]:
    """`{id: FaultClass}` in document order. Cached; the document is pinned, not live."""
    path = doc or _DOC
    if not path.is_file():
        raise FaultModelError(
            f"the pinned fault taxonomy is missing at {path.name}. Every predicate's "
            "claims_fault_classes resolves against it; without it a claim resolves against "
            "nothing and G2's bar has no denominator."
        )
    out: dict[str, FaultClass] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not _ROW.match(line):
            continue
        cells = _split_row(line)
        if len(cells) != 6:
            raise FaultModelError(f"malformed taxonomy row (expected 6 columns): {line!r}")
        fid, name, operator, applies, scope, why = cells
        if fid in out:
            raise FaultModelError(f"duplicate fault class id {fid!r} in the pinned taxonomy")
        out[fid] = FaultClass(
            id=fid,
            name=name,
            operator=operator,
            applies_to=tuple(a.strip() for a in applies.split(",")),
            scope=scope,
            rationale=why,
        )
    if len(out) != EXPECTED_CLASSES:
        raise FaultModelError(
            f"the pinned taxonomy parses to {len(out)} classes, not {EXPECTED_CLASSES}. "
            "A lost row silently shrinks the denominator of every kill rate in the programme."
        )
    if "F11" not in out:
        raise FaultModelError(
            "F11 is the formula-override class and is named by id in P9's exit gate. "
            "It may not be renumbered."
        )
    return out


def known_ids() -> frozenset[str]:
    return frozenset(fault_classes())


def resolve(claim: str) -> FaultClass:
    classes = fault_classes()
    if claim not in classes:
        raise FaultModelError(
            f"{claim!r} is not a class of the pinned fault model {MODEL_VERSION}. "
            f"Admissible: {', '.join(sorted(classes))}."
        )
    return classes[claim]
