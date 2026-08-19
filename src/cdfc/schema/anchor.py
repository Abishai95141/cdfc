"""`Anchor` — WHERE a fact lives, in a form that survives leaving a spreadsheet.

## Why a string was not enough, measured rather than argued

Cell identity in this repository is the string `"3. Portfolio!O7"`. That is not a key language
problem — `predicates.harvest.cel_path` already emits an ABSTRACT dotted path (`n_3_portfolio.r7.co`)
with no `!` in it, so the CEL layer, the AST walker, `FactView` and four of the five gates are
already document-agnostic. What is spreadsheet-shaped is this one string, and it is the thing a
witness names, a campaign seeds into, and a report renders.

**Experiment E2 measured what it would have to become, on two regulators' published rule sets:**

    EBA    with {tC_25.01.a, r0010, c0060}: {r0040} = {r0050} + {r0060}
    EIOPA  {t: S.05.01.13.01, r: R1300, c: C0200, z: Z0001, seq: False, id: v1}

    table addresses parsed, EBA      18,827   of which resolved to the rule's own scope  18,826
    table addresses parsed, EIOPA    30,987   full {t:,r:,c:} triples                    23,843
    A1-style cell references, EBA        11

Two regulators, two notations, ONE structure — and 11 A1-style references in 18,827. A published
rule addresses a **data point**, and `"Sheet!REF"` cannot hold one.

## The five requirements, each from a measurement and not from a preference

1. **A (table, rows, cols) triple**, of which a spreadsheet cell is the DEGENERATE case: one sheet,
   one row, one column.
2. **`rows` and `cols` are SEQUENCES.** `r: R0010; R0030; R0110; R0140; …` is a single EIOPA
   address covering eleven rows. A scalar field here would have forced eleven anchors for one rule
   and lost the fact that they are one assertion. This is the requirement the architecture document
   guessed wrong.
3. **Unknown axes are CARRIED, not dropped.** EIOPA adds `z:`, `f:`, `fv:`, `seq:`, `id:`. An anchor
   that silently discards an axis it does not understand is an anchor that claims two different data
   points are the same one.
4. **The dialect is NOT part of the identity.** The same data point reached through EBA notation and
   through EIOPA notation is one anchor, or two rule sets can never be merged and a filing can never
   be checked against both.
5. **`NULL` is absent.** EBA rule `v3695_s` carries the literal four characters `NULL` in its
   declared-tables cell. Read as a table name it becomes a table that does not exist; read as absence
   it is the deactivated rule it actually is.

## What this module deliberately does NOT do yet

It does not replace the `"Sheet!REF"` string anywhere. `render()` reproduces that string EXACTLY for
the spreadsheet case, so an `Anchor` can be introduced at a construction site without moving a single
published byte — which is the only way to make a substitution across dozens of sites safely, and it
is checked by `tools/anchor_hazard.py --check` rather than asserted here.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

# A spreadsheet reference: one or more letters, then one or more digits. Anchored on both ends
# because `A1B2` is not a cell and admitting it would let a typo become a coordinate.
_A1: Final[re.Pattern[str]] = re.compile(r"^([A-Za-z]{1,3})([0-9]{1,7})$")

# The literal a publisher writes where it means nothing. See requirement 5.
_ABSENT: Final[frozenset[str]] = frozenset({"", "NULL", "null", "None", "-"})

WILDCARD: Final[str] = "*"


class AnchorError(ValueError):
    """A refusal to construct an address that does not identify anything."""


@dataclass(frozen=True, slots=True)
class Anchor:
    """One addressed position. Immutable, hashable, and ordered by its canonical rendering.

    `axes` holds what this build does not interpret. It participates in equality (requirement 3)
    and it is a `tuple` of pairs rather than a dict so the type stays hashable and its ordering is
    fixed rather than insertion-dependent — an anchor whose hash depended on dict order would be a
    fresh instance of the very hazard `tools/anchor_hazard.py` was built to catch.
    """

    table: str
    rows: tuple[str, ...] = ()
    cols: tuple[str, ...] = ()
    axes: tuple[tuple[str, str], ...] = ()
    # NOT part of identity — requirement 4. Excluded from comparison and from the hash.
    dialect: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.table or self.table in _ABSENT:
            raise AnchorError(
                f"an anchor needs a table or sheet; got {self.table!r}. The literal 'NULL' is "
                "ABSENCE and must not become the name of a table nobody has."
            )
        for name, seq in (("rows", self.rows), ("cols", self.cols)):
            for v in seq:
                if v in _ABSENT:
                    raise AnchorError(f"{name} contains an absent marker {v!r}")

    # --- construction -------------------------------------------------------------------------

    @staticmethod
    def cell(sheet: str, ref: str) -> Anchor:
        """The degenerate case: one sheet, one cell. `Anchor.cell("3. Portfolio", "O7")`."""
        m = _A1.match(ref.replace("$", ""))
        if not m:
            raise AnchorError(f"{ref!r} is not an A1 reference")
        col, row = m.group(1).upper(), m.group(2)
        return Anchor(table=sheet, rows=(row,), cols=(col,), dialect="a1")

    @staticmethod
    def parse(text: str) -> Anchor:
        """`"3. Portfolio!O7"` back into an anchor. The inverse of `render()` for the A1 case.

        Splits on the LAST `!` — sheet names in this corpus contain `.` and spaces, and one of the
        nine pinned blanks would round-trip wrongly under a first-`!` split the day a sheet name
        contains one.
        """
        if "!" not in text:
            raise AnchorError(f"{text!r} carries no sheet separator")
        sheet, _, ref = text.rpartition("!")
        return Anchor.cell(sheet, ref)

    @staticmethod
    def data_point(
        table: str,
        rows: Sequence[str] | str = (),
        cols: Sequence[str] | str = (),
        axes: Mapping[str, str] | None = None,
        dialect: str = "",
    ) -> Anchor:
        """A published rule's address. `rows`/`cols` accept a scalar for the common single case."""
        def _seq(v: Sequence[str] | str) -> tuple[str, ...]:
            if isinstance(v, str):
                v = [p.strip() for p in re.split(r"[;,]", v)] if v else []
            return tuple(x for x in (s.strip() for s in v) if x and x not in _ABSENT)

        return Anchor(
            table=table.strip(), rows=_seq(rows), cols=_seq(cols),
            axes=tuple(sorted((k, str(x)) for k, x in (axes or {}).items())),
            dialect=dialect,
        )

    # --- rendering ----------------------------------------------------------------------------

    def render(self) -> str:
        """The canonical string. **For a single spreadsheet cell this is byte-identical to the
        `"Sheet!REF"` this project has always written**, which is what lets an `Anchor` be
        introduced at a construction site without moving a published byte."""
        if self.is_cell:
            return f"{self.table}!{self.cols[0]}{self.rows[0]}"
        bits = [self.table]
        if self.rows:
            bits.append("r=" + ";".join(self.rows))
        if self.cols:
            bits.append("c=" + ";".join(self.cols))
        bits.extend(f"{k}={v}" for k, v in self.axes)
        return "{" + ", ".join(bits) + "}"

    def __str__(self) -> str:
        return self.render()

    def __lt__(self, other: Anchor) -> bool:
        return self.render() < other.render()

    # --- questions ----------------------------------------------------------------------------

    @property
    def is_cell(self) -> bool:
        """True when this addresses exactly one spreadsheet cell — no wildcard, no axes."""
        return (
            len(self.rows) == 1 and len(self.cols) == 1 and not self.axes
            and WILDCARD not in self.rows and WILDCARD not in self.cols
            and bool(_A1.match(f"{self.cols[0]}{self.rows[0]}"))
        )

    @property
    def spans(self) -> int:
        """How many positions this addresses. A wildcard is UNKNOWN and refuses to be counted."""
        if WILDCARD in self.rows or WILDCARD in self.cols:
            raise AnchorError(
                f"{self.render()} contains a wildcard, so how many positions it covers is a "
                "question about a template this anchor has not been resolved against. Returning a "
                "number here would be inventing one."
            )
        return max(len(self.rows), 1) * max(len(self.cols), 1)
