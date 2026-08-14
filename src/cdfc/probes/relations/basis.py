"""P9-B2 step 4 — the accounting-basis guard, and the note that licenses it.

**The artifact fact, quoted first-hand from the pinned blank** (`'3. Portfolio'!A130`):

> *"While information in Table 3.5 should be provided on non-look through basis, the information
> in Table 3.6 should be provided on look-through basis."*

Two tables on one sheet, describing the same portfolio, on two different bases. A relation that
added a Table 3.5 quantity to a Table 3.6 quantity would be adding two different measurements of
the same money and calling the difference a filer error. It would false-alarm on a **correct**
filing — which is the failure mode that produced five relations of which four false-alarm, and
the reason step 4 exists.

**The guard is a singleton rule, not a compatibility matrix.** `bases` must have exactly one
member. A matrix invites the argument that this particular pair is fine; a singleton has nothing
to argue about, and a relation that genuinely spans bases has to be split into two relations that
each say what they measure.
"""

from __future__ import annotations

from typing import Final

# The bases this template declares, and the table ranges that carry them. Rows are (sheet, first
# row, last row) taken from the blank's own table headings — measured, not assumed.
NON_LOOK_THROUGH: Final[str] = "NON_LOOK_THROUGH"
LOOK_THROUGH: Final[str] = "LOOK_THROUGH"
INVESTOR_SIDE: Final[str] = "INVESTOR_SIDE"

BASES: Final[frozenset[str]] = frozenset({NON_LOOK_THROUGH, LOOK_THROUGH, INVESTOR_SIDE})

# `'3. Portfolio'!A130` note 3, verbatim in `EVIDENCE` below, decides the first two. The investor
# side is a third basis rather than a variant of either: Tables 4.x measure money coming IN from
# investors, and adding it to a portfolio quantity would double-count the same money once as an
# inflow and once as a holding.
TABLE_BASIS: Final[dict[tuple[str, int, int], str]] = {
    ("3. Portfolio", 72, 99): NON_LOOK_THROUGH,     # Table 3.5, Top 10 Investments
    # Table 3.6, underlying schemes at or above the threshold the regulator's own heading names
    ("3. Portfolio", 100, 132): LOOK_THROUGH,
    ("4. Investors", 1, 200): INVESTOR_SIDE,
    ("5. PMS", 1, 200): INVESTOR_SIDE,
}

EVIDENCE: Final[str] = (
    "'3. Portfolio'!A130, note 3 of the Portfolio sheet: \"While information in Table 3.5 should "
    "be provided on non-look through basis, the information in Table 3.6 should be provided on "
    "look-through basis.\" MEASURED first-hand from the pinned blank, 14 Aug 2026."
)


class BasisContamination(ValueError):
    """A relation drafted across two accounting bases. Refused at authoring review."""


def basis_of(sheet: str, row: int) -> str | None:
    """The declared basis of a cell, or `None` where the blank declares none."""
    for (s, lo, hi), basis in TABLE_BASIS.items():
        if s == sheet and lo <= row <= hi:
            return basis
    return None


def bases_of(cells: list[str]) -> frozenset[str]:
    """Every basis the given `Sheet!Ref` cells touch. `None`s are dropped — a cell on no declared
    table contaminates nothing, and treating it as its own basis would refuse every relation."""
    from cdfc.schema.stable_keys import split_ref

    out: set[str] = set()
    for cell in cells:
        sheet, ref = cell.split("!", 1)
        try:
            _col, row = split_ref(ref)
        except ValueError:
            continue
        b = basis_of(sheet, row)
        if b is not None:
            out.add(b)
    return frozenset(out)


def assert_single_basis(relation_id: str, cells: list[str]) -> frozenset[str]:
    """Refuse a relation that spans bases, naming both and the note that separates them."""
    found = bases_of(cells)
    if len(found) > 1:
        raise BasisContamination(
            f"{relation_id} spans {sorted(found)}. {EVIDENCE} A relation across them adds two "
            "different measurements of the same money and reports the difference as the filer's "
            "error — a false alarm on a CORRECT filing."
        )
    return found
