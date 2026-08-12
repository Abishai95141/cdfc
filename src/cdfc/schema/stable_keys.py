"""Stable keys — a key that survives a row insertion, or refuses to.

WHY A COORDINATE CANNOT BE THE IDENTITY. A key of `'3. Portfolio'!O7` silently rebinds
the moment a row is inserted above it: the predicate goes on passing, against a different
cell. Nothing in the output distinguishes that from a correct binding.

WHY THE LABEL PAIR IS NOT ENOUGH, measured rather than assumed. Under a naive
`(sheet, label-above, label-left)` key, **1,749 of 1,953 candidate cells collide (89.6%)**
on the FME workbook, because its 100-row tables repeat the same label pair on every row.

So the key carries a **row ordinal**, which is arithmetic over the table's own rows rather
than a prediction about where a cell will be. Coordinates become a RESOLVED ATTRIBUTE, and
a key that cannot be resolved is `UNRESOLVED` — which **blocks** its predicates. It never
degrades to a guess, because a guess is how a predicate comes to pass against the wrong
cell.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

CELL_RE = re.compile(r"^([A-Z]+)(\d+)$")


def col_to_index(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n


def split_ref(ref: str) -> tuple[str, int]:
    m = CELL_RE.match(ref)
    if not m:
        raise ValueError(f"not a cell reference: {ref!r}")
    return m.group(1), int(m.group(2))


def _slug(s: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "_", (s or "").strip().lower()).strip("_")
    return s or "unnamed"


@dataclass(frozen=True)
class StableKey:
    sheet_name: str
    merged_header_path: tuple[str, ...]
    row_label: str
    row_ordinal: int

    def __str__(self) -> str:
        head = ".".join(_slug(p) for p in self.merged_header_path) if self.merged_header_path else "root"
        return f"{_slug(self.sheet_name)}.{head}.row[{self.row_ordinal}].{_slug(self.row_label)}"


@dataclass(frozen=True)
class Field:
    stable_key: str
    resolved_ref: str | None
    resolution_state: Literal["RESOLVED", "UNRESOLVED"]
    dtype: Literal["MILLI_USD_MILLION", "COUNT", "DATE", "TEXT", "ENUM"]
    is_unlocked: bool
    is_formula: bool
    in_field_surface: bool

    def as_canonical_obj(self) -> dict[str, object]:
        return {
            "stable_key": self.stable_key,
            "resolved_ref": self.resolved_ref,
            "resolution_state": self.resolution_state,
            "dtype": self.dtype,
            "is_unlocked": self.is_unlocked,
            "is_formula": self.is_formula,
            "in_field_surface": self.in_field_surface,
        }


class UnresolvedKey(Exception):
    """A key that did not resolve. It blocks its predicates; it never guesses."""


def bind(field: Field) -> str:
    """The only sanctioned way to turn a key into a reference."""
    if field.resolution_state != "RESOLVED" or field.resolved_ref is None:
        raise UnresolvedKey(
            f"{field.stable_key} is UNRESOLVED and cannot be bound. A predicate reading it "
            "does not run; it does not fall back to a coordinate."
        )
    return field.resolved_ref


# --------------------------------------------------------------------------------
# Key construction from a reading of the template
# --------------------------------------------------------------------------------


def _merged_index(merged_ranges: tuple[str, ...]) -> dict[tuple[str, int], str]:
    """(col, row) -> the anchor ref of the merged range covering it."""
    out: dict[tuple[str, int], str] = {}
    for rng in merged_ranges:
        if ":" not in rng:
            continue
        a, b = rng.split(":", 1)
        try:
            c1, r1 = split_ref(a)
            c2, r2 = split_ref(b)
        except ValueError:
            continue
        for ci in range(col_to_index(c1), col_to_index(c2) + 1):
            for ri in range(r1, r2 + 1):
                out[(ci, ri)] = a
    return out


def build_keys(
    *,
    sheet: str,
    cell_text: Mapping[str, str],
    unlocked: set[str],
    formula_refs: set[str],
    merged_ranges: tuple[str, ...] = (),
) -> dict[str, Field]:
    """Derive one Field per cell of a sheet.

    `merged_header_path` is the nearest merged-range anchor text above the cell — the 252
    merged ranges on FME are what make that path non-trivial. `row_label` is the leftmost
    non-empty text on the cell's own row. `row_ordinal` is the cell's row number, which is
    arithmetic and not a prediction.
    """
    merged = _merged_index(merged_ranges)
    by_row: dict[int, list[tuple[int, str]]] = {}
    for ref, txt in cell_text.items():
        try:
            c, r = split_ref(ref)
        except ValueError:
            continue
        by_row.setdefault(r, []).append((col_to_index(c), txt))

    row_label: dict[int, str] = {}
    for r, cols in by_row.items():
        for _ci, txt in sorted(cols):
            if txt and txt.strip():
                row_label[r] = txt.strip()
                break

    fields: dict[str, Field] = {}
    for ref in sorted(set(cell_text) | unlocked | formula_refs):
        try:
            c, r = split_ref(ref)
        except ValueError:
            continue
        ci = col_to_index(c)

        header: list[str] = []
        anchor = merged.get((ci, r))
        if anchor is None:
            for rr in range(r - 1, max(0, r - 12), -1):
                a = merged.get((ci, rr))
                if a is not None:
                    anchor = a
                    break
        if anchor is not None:
            t = cell_text.get(anchor, "")
            if t.strip():
                header.append(t.strip())

        label = row_label.get(r) or cell_text.get(ref, "") or c
        key = StableKey(sheet, tuple(header), label, r)
        is_formula = ref in formula_refs
        is_unlocked = ref in unlocked
        fields[str(key)] = Field(
            stable_key=str(key),
            resolved_ref=ref,
            resolution_state="RESOLVED",
            dtype="TEXT",
            is_unlocked=is_unlocked,
            is_formula=is_formula,
            in_field_surface=is_unlocked and not is_formula,
        )
    return fields


def collision_census(
    *, cell_text: Mapping[str, str], with_ordinal: bool
) -> tuple[int, int]:
    """(colliding cells, total cells) under the naive key or the ordinal-bearing one.

    This is the measurement that justifies the ordinal, re-taken rather than remembered.
    """
    by_row: dict[int, str] = {}
    parsed: list[tuple[str, int, int]] = []
    for ref, txt in cell_text.items():
        try:
            c, r = split_ref(ref)
        except ValueError:
            continue
        parsed.append((ref, col_to_index(c), r))
        if txt and txt.strip() and (r not in by_row):
            by_row[r] = txt.strip()

    counts: dict[tuple, int] = {}
    for ref, ci, r in parsed:
        label = by_row.get(r, "")
        above = by_row.get(r - 1, "")
        k: tuple = (above, label, ci) if not with_ordinal else (above, label, ci, r)
        counts[k] = counts.get(k, 0) + 1
    colliding = sum(n for n in counts.values() if n > 1)
    return colliding, len(parsed)
