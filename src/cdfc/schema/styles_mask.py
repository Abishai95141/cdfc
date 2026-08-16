"""PATH A of the unlocked-cell mask — styles.xml `cellXfs` with `xfId` inheritance.

Implements `docs/PROTECTION-RESOLUTION.md`, which was written first. Path B
(`styles_mask_b.py`) implements the same rule by a separate route and must not import
anything from here: the differential check is worthless if the two paths share a module.

What the differential proves, and what it does not: it proves these are two
implementations rather than one function called twice. **It cannot prove the rule is
right** — both paths would agree just as well on `v3-abs`. The external falsifier is at
P8-B1, and until then the denominator ships `PROVISIONAL-UNVALIDATED`.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from cdfc.ingest.xmlsafe import fromstring

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


class Rule(StrEnum):
    V3 = "v3"            # ADOPTED
    V3_UW = "v3-uw"      # lawful, not adopted: does not exclude unlocked formula cells
    V3_ABS = "v3-abs"    # lawful, REJECTED: absence of <protection> read as unlocked


@dataclass(frozen=True)
class StyleCensus:
    n_cell_xfs: int
    explicit_unlocked: int
    explicit_locked: int
    inheriting: int
    apply_protection: int


@dataclass(frozen=True)
class ExclusionCensus:
    """**What the denominator LEFT OUT, counted.** Three disjoint buckets that close.

    `n_cells` is a number arrived at by removing things, and until this existed nothing recorded
    what was removed. A reader of a report saw `3,747` and had no way to answer *is that the whole
    form?* — which is precisely the question a coverage claim has to be able to answer, in the one
    product whose differentiator is reporting what it did not check.

    The partition is evaluated in this order and each cell lands in exactly one bucket:

    | bucket | rule |
    |---|---|
    | `formula` | rule 5 — the template computes it, so it is not a filer field |
    | `locked` | the protection mask says a filer cannot write it |
    | `field_surface` | everything else; this is `n_cells` |

    **`recorded` is cells the WORKBOOK RECORDS, not cells in the grid.** OOXML omits `<c>` for a
    cell that is empty and unstyled, so a 1,048,576-row sheet does not contribute a million entries.
    Naming it `recorded` rather than `total` keeps that limit on the number instead of in a comment
    nobody reads beside it.
    """

    recorded: int
    formula: int
    locked: int
    field_surface: int

    def __post_init__(self) -> None:
        if self.recorded != self.formula + self.locked + self.field_surface:
            raise ValueError(
                f"recorded={self.recorded} but formula+locked+field_surface="
                f"{self.formula + self.locked + self.field_surface}. A census of exclusions that "
                "does not close is a census that lost cells on the way to a denominator."
            )

    def as_canonical_obj(self) -> dict[str, int]:
        return {"recorded": self.recorded, "formula": self.formula,
                "locked": self.locked, "field_surface": self.field_surface}


@dataclass(frozen=True)
class FieldSurface:
    """The denominator. `None` when the template ships no protection mask at all."""

    n_cells: int | None
    cells: tuple[tuple[str, str], ...]
    per_sheet: dict[str, int]
    generator_rule: str
    source: str
    validation_state: Literal["PROVISIONAL-UNVALIDATED", "EXTERNALLY-CHECKED"] = (
        "PROVISIONAL-UNVALIDATED"
    )
    census: StyleCensus | None = None
    sheets_in_scope: tuple[str, ...] = ()
    # WHAT THE DENOMINATOR EXCLUDED. `None` only when no mask was derivable and there is
    # therefore no denominator to have excluded anything from.
    exclusions: ExclusionCensus | None = None

    def as_canonical_obj(self) -> dict[str, object]:
        return {
            "n_cells": self.n_cells,
            "generator_rule": self.generator_rule,
            "source": self.source,
            "validation_state": self.validation_state,
            "per_sheet": dict(sorted(self.per_sheet.items())),
            "sheets_in_scope": list(self.sheets_in_scope),
        }


def _sheet_parts(z: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    wb = fromstring(z.read("xl/workbook.xml"))
    rels = fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid = {r.get("Id"): r.get("Target") for r in rels.iter(f"{{{PR}}}Relationship")}
    out = []
    for sh in wb.iter(f"{{{M}}}sheet"):
        t = (rid.get(sh.get(f"{{{R}}}id"), "") or "").lstrip("/")
        part = t if t.startswith("xl/") else f"xl/{t}"
        # HIDDEN SHEETS ARE IN SCOPE. Skipping them returns 3,747 on FME anyway, which
        # would be right by accident while the code was wrong (NC-D03).
        out.append((sh.get("name", ""), sh.get("state", "visible"), part))
    return out


def _resolve_locked(
    style_id: int,
    cell_xfs: list[tuple[bool | None, int | None, bool]],
    style_xfs: list[bool | None],
    rule: Rule,
) -> bool:
    """Rules 2-4 of PROTECTION-RESOLUTION.md. Returns the resolved locked bit."""
    if style_id >= len(cell_xfs):
        return True  # OOXML default
    explicit, xf_id, _apply = cell_xfs[style_id]
    if explicit is not None:
        return explicit                      # rule 2: an explicit value wins outright
    if rule is Rule.V3_ABS:
        return False                         # the rejected reading: absence means unlocked
    if xf_id is not None and xf_id < len(style_xfs):
        inherited = style_xfs[xf_id]
        if inherited is not None:
            return inherited                 # rule 3: inherit from cellStyleXfs
    return True                              # rule 3 tail: OOXML default locked="1"


def build(blob_path: Path, rule: Rule = Rule.V3) -> FieldSurface:
    with zipfile.ZipFile(blob_path) as z:
        names = set(z.namelist())
        cell_xfs: list[tuple[bool | None, int | None, bool]] = []
        style_xfs: list[bool | None] = []
        n_apply = 0

        if "xl/styles.xml" in names:
            st = fromstring(z.read("xl/styles.xml"))
            csx = st.find(f"{{{M}}}cellStyleXfs")
            if csx is not None:
                for xf in csx.findall(f"{{{M}}}xf"):
                    p = xf.find(f"{{{M}}}protection")
                    style_xfs.append(None if p is None or p.get("locked") is None
                                     else p.get("locked") == "1")
            cx = st.find(f"{{{M}}}cellXfs")
            if cx is not None:
                for xf in cx.findall(f"{{{M}}}xf"):
                    p = xf.find(f"{{{M}}}protection")
                    # Rule 2a: a <protection> element that declares no @locked is still
                    # PRESENT, and @locked defaults to true under ECMA-376. That is an
                    # explicit lock, not an inheritance case. On FME 7 styles are
                    # <protection hidden="1"/>; reading them as inheriting changes v3-abs
                    # by three cells and leaves v3 unchanged, which is how the ambiguity
                    # stayed invisible until the rejected reading was computed.
                    if p is None:
                        explicit = None
                    elif p.get("locked") is None:
                        explicit = True
                    else:
                        explicit = p.get("locked") == "1"
                    xf_id = int(xf.get("xfId")) if (xf.get("xfId") or "").isdigit() else None
                    apply_p = xf.get("applyProtection") == "1"
                    n_apply += apply_p
                    cell_xfs.append((explicit, xf_id, apply_p))

        census = StyleCensus(
            n_cell_xfs=len(cell_xfs),
            explicit_unlocked=sum(1 for e, _, _ in cell_xfs if e is False),
            explicit_locked=sum(1 for e, _, _ in cell_xfs if e is True),
            inheriting=sum(1 for e, _, _ in cell_xfs if e is None),
            apply_protection=n_apply,
        )

        sheets = _sheet_parts(z)
        roots = {}
        any_protection = False
        for name, _state, part in sheets:
            if part not in names:
                continue
            root = fromstring(z.read(part))
            roots[name] = root
            if root.find(f"{{{M}}}sheetProtection") is not None:
                any_protection = True

        # RULE 6, checked BEFORE rule 5 so a stray unlocked style id cannot manufacture a
        # small answer from a workbook that ships no protection mask at all.
        if not any_protection:
            return FieldSurface(
                n_cells=None,
                cells=(),
                per_sheet={},
                generator_rule=str(rule),
                source="not derivable — template ships no protection mask",
                census=census,
                sheets_in_scope=tuple(n for n, _, _ in sheets),
            )

        cells: list[tuple[str, str]] = []
        per_sheet: dict[str, int] = {}
        # THE EXCLUSIONS, TALLIED ON THE SAME WALK. Counting them in a second pass would be a
        # second traversal that could disagree with the first about which cells exist.
        n_recorded = n_formula = n_locked = 0
        for name, _state, part in sheets:
            root = roots.get(name)
            if root is None:
                continue
            here = 0
            for c in root.iter(f"{{{M}}}c"):
                n_recorded += 1
                has_formula = c.find(f"{{{M}}}f") is not None
                if has_formula and rule is not Rule.V3_UW:
                    n_formula += 1
                    continue                 # rule 5: a formula cell is not a filer field
                s = c.get("s")
                sid = int(s) if (s or "").isdigit() else 0
                if not _resolve_locked(sid, cell_xfs, style_xfs, rule):
                    cells.append((name, c.get("r", "")))
                    here += 1
                else:
                    n_locked += 1
            per_sheet[name] = here

    return FieldSurface(
        n_cells=len(cells),
        cells=tuple(cells),
        per_sheet=per_sheet,
        generator_rule=str(rule),
        source="styles.xml cellXfs with xfId inheritance (path A)",
        census=census,
        sheets_in_scope=tuple(n for n, _, _ in sheets),
        # `__post_init__` refuses a census that does not close, so a future edit that adds a
        # `continue` without a tally fails here rather than shrinking the denominator quietly.
        exclusions=ExclusionCensus(
            recorded=n_recorded, formula=n_formula, locked=n_locked, field_surface=len(cells),
        ),
    )
