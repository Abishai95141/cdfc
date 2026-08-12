"""P3-B3 — the provenance anchor, composing by WEAKEST INPUT.

Every value carries where it came from. A derived value never claims a stronger warrant
than its weakest input: a sum of three deterministic reads and one model-extracted value
is MODEL_EXTRACTED, not DETERMINISTIC. Without that rule a single extracted number
launders itself into a deterministic total, and the report says the total was read off the
page when part of it was inferred.

The lattice is deliberately short. Three values, totally ordered, and the composition is
`min`. A partial order would need a join nobody could explain on a report surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

# The order IS the strength. Lower is weaker, and composition takes the minimum.
class Warrant(IntEnum):
    DERIVED = 0          # computed by us from other values
    MODEL_EXTRACTED = 1  # a model read it out of an unstructured source
    DETERMINISTIC = 2    # read directly from the artifact's own bytes

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Anchor:
    """Where a value came from, precisely enough to re-open the source."""

    warrant: Warrant
    source: str          # a blob sha256, or a template digest
    part: str | None = None    # e.g. xl/worksheets/sheet3.xml
    cell: str | None = None    # e.g. '3. Portfolio'!O7
    note: str | None = None

    def as_canonical_obj(self) -> dict[str, Any]:
        return {
            "warrant": str(self.warrant),
            "source": self.source,
            "part": self.part,
            "cell": self.cell,
            "note": self.note,
        }


def compose(*anchors: Anchor) -> Anchor:
    """The weakest-input rule. A derived value's warrant is the minimum of its inputs.

    With no inputs the result is DERIVED with an explicit note — a value that came from
    nothing is not deterministic, and calling it so is how a constant acquires a warrant.
    """
    if not anchors:
        return Anchor(Warrant.DERIVED, source="", note="composed from no inputs")
    weakest = min(a.warrant for a in anchors)
    sources = sorted({a.source for a in anchors if a.source})
    cells = [a.cell for a in anchors if a.cell]
    return Anchor(
        warrant=weakest,
        source=sources[0] if len(sources) == 1 else ",".join(sources),
        part=anchors[0].part if len({a.part for a in anchors}) == 1 else None,
        cell=None if len(cells) != 1 else cells[0],
        note=f"composed from {len(anchors)} input(s), weakest {weakest!s}",
    )
