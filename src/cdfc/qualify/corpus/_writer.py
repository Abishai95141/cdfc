"""P8-B2 — raw-zip writes for the clean corpus. **Parsed as XML, never pattern-matched.**

`ci/no-regex-over-xml.sh` exists because a lexical matcher over OOXML returns a CORRECT COUNT with
WRONG CONTENTS, and it has done so three times here. Every part is copied byte-for-byte except the
worksheets that change.

**This module imports nothing from `cdfc.calc`**, and that is load-bearing: it is inside the
FOREIGN_ENGINE derivation's import closure, and `g4_ffr.independent()` reads that closure.
"""

from __future__ import annotations

import zipfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from cdfc.ingest.reader_lxml import _sheet_parts
from cdfc.ingest.xmlsafe import fromstring

M: Final[str] = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _set_value(c: Any, value: object) -> None:
    from lxml import etree

    ns = f"{{{M}}}"
    for tag in ("v", "is"):
        for node in c.findall(f"{ns}{tag}"):
            c.remove(node)
    if isinstance(value, str):
        c.set("t", "inlineStr")
        is_el = etree.SubElement(c, f"{ns}is")
        t = etree.SubElement(is_el, f"{ns}t")
        t.text = value
    else:
        if c.get("t") in ("s", "str", "inlineStr"):
            del c.attrib["t"]
        v = etree.SubElement(c, f"{ns}v")
        v.text = str(value)


def _rewrite(xml: bytes, values: Mapping[str, object], *, strip_cached: bool) -> bytes:
    from lxml import etree

    root = fromstring(xml)
    ns = f"{{{M}}}"
    seen: set[str] = set()
    for c in root.iter(f"{ns}c"):
        ref = c.get("r") or ""
        seen.add(ref)
        formula = c.find(f"{ns}f")
        if formula is not None:
            if strip_cached:
                for v in c.findall(f"{ns}v"):
                    c.remove(v)
            elif ref in values:
                _set_value(c, values[ref])
            continue
        if ref in values:
            _set_value(c, values[ref])
    _insert_missing(root, {k: v for k, v in values.items() if k not in seen}, etree)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _insert_missing(root: Any, values: Mapping[str, object], etree: Any) -> None:
    """A cell the pinned blank does not carry an element for. Rows stay in ascending order and
    cells stay in ascending column order — a worksheet whose cells are out of order is one Excel
    repairs, and a repaired fixture is not a fixture."""
    from cdfc.schema.stable_keys import col_to_index, split_ref

    if not values:
        return
    ns = f"{{{M}}}"
    data = root.find(f"{ns}sheetData")
    if data is None:
        return
    rows = {int(r.get("r")): r for r in data.findall(f"{ns}row") if r.get("r")}
    by_row: dict[int, list[tuple[int, str, object]]] = {}
    for ref, value in values.items():
        try:
            col, row = split_ref(ref)
        except ValueError:
            continue
        by_row.setdefault(row, []).append((col_to_index(col), ref, value))
    for row_n in sorted(by_row):
        row_el = rows.get(row_n)
        if row_el is None:
            row_el = etree.SubElement(data, f"{ns}row")
            row_el.set("r", str(row_n))
            data[:] = sorted(data, key=lambda r: int(r.get("r") or 0))
            rows[row_n] = row_el
        for _idx, ref, value in sorted(by_row[row_n]):
            c = etree.SubElement(row_el, f"{ns}c")
            c.set("r", ref)
            _set_value(c, value)
        row_el[:] = sorted(row_el, key=lambda c: col_to_index(split_ref(c.get("r") or "A1")[0]))


def _repack(source: Path, target: Path, per_part: Mapping[str, bytes]) -> None:
    with zipfile.ZipFile(source) as z:
        parts = {n: z.read(n) for n in z.namelist()}
        infos = {i.filename: i for i in z.infolist()}
    parts.update(per_part)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in parts.items():
            info = zipfile.ZipInfo(name, date_time=infos[name].date_time)
            info.compress_type = infos[name].compress_type
            info.external_attr = infos[name].external_attr
            out.writestr(info, data)


def strip_and_write(blank: Path, target: Path, inputs: Mapping[tuple[str, str], object]) -> None:
    """Write the INPUT cells and REMOVE every cached formula value.

    The strip is what makes `derived_by` mean something: the filing that leaves this function has
    no derived values at all, so whatever appears in a formula cell afterwards was put there by the
    engine `derived_by` names and by nothing else.
    """
    with zipfile.ZipFile(blank) as z:
        sheets = {name: part for name, _s, part in _sheet_parts(z) if part in z.namelist()}
        raw = {part: z.read(part) for part in sheets.values()}
    out: dict[str, bytes] = {}
    for sheet, part in sheets.items():
        per_sheet = {ref: v for (s, ref), v in inputs.items() if s == sheet}
        out[part] = _rewrite(raw[part], per_sheet, strip_cached=True)
    _repack(blank, target, out)


def write_values(base: Path, target: Path, values: Mapping[tuple[str, str], object]) -> None:
    """Write cached values into the workbook at `target`, keeping every other part byte-identical."""
    with zipfile.ZipFile(target) as z:
        sheets = {name: part for name, _s, part in _sheet_parts(z) if part in z.namelist()}
        raw = {part: z.read(part) for part in sheets.values()}
    out: dict[str, bytes] = {}
    for sheet, part in sheets.items():
        per_sheet = {ref: v for (s, ref), v in values.items() if s == sheet}
        if not per_sheet:
            continue
        out[part] = _rewrite(raw[part], per_sheet, strip_cached=False)
    _repack(target, target, out)


def formula_values(blob: Path) -> dict[tuple[str, str], object]:
    """Every FORMULA cell's cached value. The numbers a computation wrote, not the shape."""
    out: dict[tuple[str, str], object] = {}
    with zipfile.ZipFile(blob) as z:
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            for c in root.iter(f"{{{M}}}c"):
                if c.find(f"{{{M}}}f") is None:
                    continue
                v = c.find(f"{{{M}}}v")
                if v is None or v.text is None:
                    continue
                out[(name, c.get("r") or "")] = _typed(v.text)
    return out


def _typed(text: str) -> object:
    """A cached value carries its TYPE, not just its characters.

    **This is the root cause of the 6 GB hang.** `formula_values` returned `v.text` — a `str` — for
    every derived cell, and `_set_value` writes a `str` as an inline STRING. So every
    foreign-engine-derived cell in the corpus was TEXT, a numeric column came back part number and
    part text, and a `c.v >= 0` over it is a type error the runtime cannot cheaply refuse.

    A cached numeric value is a number. Anything that does not parse as one stays a string, which
    is what an error literal or a genuine text result is.
    """
    from decimal import Decimal, InvalidOperation

    t = (text or "").strip()
    if not t:
        return t
    try:
        d = Decimal(t)
    except (TypeError, ValueError, InvalidOperation):
        return text
    # `Decimal`, never `float`: R4 makes every quantity here exact, and a float in a filing is a
    # value nobody can re-derive. `_set_value` stringifies it, so the XML carries the same digits.
    return int(d) if d == d.to_integral_value() else d
