"""P3-B1 — the two-document fact model.

**Exactly two bound names: `filing` and `template`.** Every predicate this system will ever
run is written over those two and nothing else. A third name is a way for a predicate to
read something nobody declared.

`template` is resolved from the PINNED BLANK DIGEST and never from the filing. The defect
that prevents: a filer who edits a vocabulary, then satisfies a membership check against
their own edited vocabulary. The template's digest is carried on the table so a report can
name which blank it was checked against.

**Every leaf carries `__cell__`.** No exceptions, and it is asserted over the whole field
surface. A value with no cell cannot be shown to a filer, cannot be re-opened by a
reviewer, and cannot be re-derived — so it is not evidence, whatever its number says.

Hard constraints, each with a test: no clock, no network, no filesystem read below
`build`; money is scaled to `MILLI_USD_MILLION` here, exactly once.
"""

from __future__ import annotations

import datetime as _dt
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from cdfc.facts.anchor import Anchor, Warrant, compose
from cdfc.facts.units import Unit, to_units


class FactError(ValueError):
    pass


@dataclass(frozen=True)
class Leaf:
    value: int | str | _dt.date | bool | None
    unit: Unit
    cell: str
    anchor: Anchor

    def __post_init__(self) -> None:
        if not self.cell:
            raise FactError(
                "a leaf without __cell__ cannot be shown, re-opened or re-derived, so it "
                "is not evidence whatever its value says"
            )

    def as_canonical_obj(self) -> dict[str, Any]:
        v = self.value
        return {
            "value": v.isoformat() if isinstance(v, _dt.date) else v,
            "unit": str(self.unit),
            "__cell__": self.cell,
            "anchor": self.anchor.as_canonical_obj(),
        }


@dataclass(frozen=True)
class FactTable:
    filing: Mapping[str, Leaf]
    template: Mapping[str, Leaf]
    filing_sha256: str = ""
    template_sha256: str = ""

    def keys(self) -> frozenset[str]:
        return frozenset(self.filing)

    def leaf(self, key: str) -> Leaf:
        if key not in self.filing:
            raise FactError(f"{key!r} is not in the induced key set; it cannot be read")
        return self.filing[key]

    def derive(self, *keys: str) -> Anchor:
        """The anchor a value derived from `keys` must carry — weakest input wins."""
        return compose(*(self.leaf(k).anchor for k in keys))

    def as_canonical_obj(self) -> dict[str, Any]:
        return {
            "filing_sha256": self.filing_sha256,
            "template_sha256": self.template_sha256,
            "filing": {k: v.as_canonical_obj() for k, v in sorted(self.filing.items())},
            "template": {k: v.as_canonical_obj() for k, v in sorted(self.template.items())},
        }


def _classify(raw: Any) -> tuple[Any, Unit]:
    if raw is None or raw == "":
        return None, Unit.TEXT
    if isinstance(raw, bool):
        return raw, Unit.ENUM
    if isinstance(raw, _dt.date):
        return raw, Unit.DATE
    if isinstance(raw, (int, Decimal)):
        return raw, Unit.COUNT
    return str(raw), Unit.TEXT


def build(
    *,
    filing_cells: Mapping[tuple[str, str], Any],
    template_cells: Mapping[tuple[str, str], Any],
    key_of: Any,
    money_keys: frozenset[str] = frozenset(),
    filing_sha256: str = "",
    template_sha256: str = "",
) -> FactTable:
    """Build the two-document model.

    `key_of((sheet, ref)) -> stable key | None`. A cell with no stable key is DROPPED and
    that is deliberate: a key nobody induced is a key no predicate can name.
    `money_keys` is the set of stable keys whose values are amounts — scaled to
    MILLI_USD_MILLION HERE, once, and nowhere else.
    """
    def _side(cells: Mapping[tuple[str, str], Any], source: str, warrant: Warrant) -> dict[str, Leaf]:
        out: dict[str, Leaf] = {}
        for (sheet, ref), raw in cells.items():
            key = key_of((sheet, ref))
            if key is None:
                continue
            value, unit = _classify(raw)
            if key in money_keys:
                value, unit = to_units(value if value is None or isinstance(value, (Decimal, int, str)) else None), Unit.MILLI_USD_MILLION
            out[key] = Leaf(
                value=value,
                unit=unit,
                cell=f"{sheet}!{ref}",
                anchor=Anchor(warrant, source=source, cell=f"{sheet}!{ref}"),
            )
        return out

    return FactTable(
        filing=_side(filing_cells, filing_sha256, Warrant.DETERMINISTIC),
        # The template side is DETERMINISTIC too, but anchored to the PINNED BLANK, so a
        # report can say which blank a membership check was made against.
        template=_side(template_cells, template_sha256, Warrant.DETERMINISTIC),
        filing_sha256=filing_sha256,
        template_sha256=template_sha256,
    )
