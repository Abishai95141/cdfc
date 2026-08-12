#!/usr/bin/env python
"""P0 foundation probe — the measurements N1..N8, taken from raw OOXML.

WHY NOT openpyxl. openpyxl 3.1.5 reads the FME workbook and reports 35 data validations
where there are 54, and the AML-CFT sheet as having zero where it has five, because the
`x14` extension validations live in `<extLst>` and it discards them with a warning. That
under-report is this project's flagship finding. A probe built on the library that
commits it would inherit it silently, so every count here comes from the XML.

Every function returns integers with a named denominator. Nothing here rounds, infers,
or falls back to a library when the XML is hard.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from lxml import etree

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "x14": "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
}

CELL_RE = re.compile(r"^([A-Z]+)(\d+)$")


def _xml(z: zipfile.ZipFile, name: str) -> etree._Element | None:
    try:
        return etree.fromstring(z.read(name))
    except KeyError:
        return None


def _sheet_parts(z: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    """[(sheet_name, state, part_path)] in workbook order."""
    wb = _xml(z, "xl/workbook.xml")
    rels = _xml(z, "xl/_rels/workbook.xml.rels")
    if wb is None or rels is None:
        return []
    rid_to_target = {
        r.get("Id"): r.get("Target")
        for r in rels.iter("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
    }
    out = []
    for sh in wb.iter(f"{{{NS['m']}}}sheet"):
        rid = sh.get(f"{{{NS['r']}}}id")
        target = rid_to_target.get(rid, "")
        part = target if target.startswith("xl/") else f"xl/{target.lstrip('/')}"
        out.append((sh.get("name", ""), sh.get("state", "visible"), part))
    return out


def _unlocked_style_ids(z: zipfile.ZipFile) -> set[int]:
    """Style indices whose xf carries <protection locked="0"/>.

    This is the FIELD SURFACE's basis: on a protected sheet, a cell is filer-editable iff
    its style is unlocked. Absence of <protection> means INHERIT (locked by default) —
    reading absence as unlocked is negative control NC-D05.
    """
    st = _xml(z, "xl/styles.xml")
    if st is None:
        return set()
    out: set[int] = set()
    cell_xfs = st.find(f"{{{NS['m']}}}cellXfs")
    if cell_xfs is None:
        return out
    for i, xf in enumerate(cell_xfs.findall(f"{{{NS['m']}}}xf")):
        prot = xf.find(f"{{{NS['m']}}}protection")
        if prot is not None and prot.get("locked") == "0":
            out.add(i)
    return out


def probe_one(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    res: dict[str, Any] = {
        "filename": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }
    with zipfile.ZipFile(path) as z:
        sheets = _sheet_parts(z)
        unlocked_styles = _unlocked_style_ids(z)

        n_sheets = len(sheets)
        n_hidden = sum(1 for _, state, _ in sheets if state != "visible")
        n_protected = 0
        n_cells = 0
        formula_authored = 0      # <f> carrying an expression
        formula_shared_dep = 0    # <f t="shared" si=n/> with no text — a real formula cell
        n_merged = 0
        dv_main = 0
        dv_x14 = 0
        dv_list = 0
        field_surface = 0
        per_sheet_surface: dict[str, int] = {}
        dv_per_sheet: dict[str, int] = {}

        for name, _state, part in sheets:
            root = _xml(z, part)
            if root is None:
                continue
            if root.find(f"{{{NS['m']}}}sheetProtection") is not None:
                n_protected += 1
            surface_here = 0
            for c in root.iter(f"{{{NS['m']}}}c"):
                n_cells += 1
                f = c.find(f"{{{NS['m']}}}f")
                if f is not None:
                    if (f.text or "").strip():
                        formula_authored += 1
                    elif f.get("t") == "shared":
                        formula_shared_dep += 1
                    continue  # a formula cell is never part of the filer-editable surface
                s = c.get("s")
                if s is not None and int(s) in unlocked_styles:
                    surface_here += 1
            field_surface += surface_here
            per_sheet_surface[name] = surface_here
            n_merged += len(root.findall(f".//{{{NS['m']}}}mergeCell"))

            here_main = len(root.findall(f".//{{{NS['m']}}}dataValidation"))
            here_x14 = len(root.findall(f".//{{{NS['x14']}}}dataValidation"))
            dv_main += here_main
            dv_x14 += here_x14
            dv_per_sheet[name] = here_main + here_x14
            for dv in list(root.iter(f"{{{NS['m']}}}dataValidation")) + list(
                root.iter(f"{{{NS['x14']}}}dataValidation")
            ):
                if dv.get("type") == "list":
                    dv_list += 1

        wb = _xml(z, "xl/workbook.xml")
        defined_names = 0
        if wb is not None:
            dn = wb.find(f"{{{NS['m']}}}definedNames")
            defined_names = 0 if dn is None else len(dn.findall(f"{{{NS['m']}}}definedName"))

    res.update(
        {
            "N1_sheets": n_sheets,
            "N1_hidden_sheets": n_hidden,
            "N1_protected_sheets": n_protected,
            "N2_cells": n_cells,
            "N3_formula_cells": formula_authored + formula_shared_dep,
            "N3_formula_authored": formula_authored,
            "N3_formula_shared_dependents": formula_shared_dep,
            "N4_data_validations": dv_main + dv_x14,
            "N4_dv_main_namespace": dv_main,
            "N4_dv_x14_extension": dv_x14,
            "N4_dv_list_type": dv_list,
            "N5_merged_ranges": n_merged,
            "N6_defined_names": defined_names,
            "N7_field_surface": field_surface,
            "N7_field_surface_per_sheet": per_sheet_surface,
            "N8_dv_per_sheet": dv_per_sheet,
        }
    )
    return res


def probe_openpyxl(path: Path) -> dict[str, Any]:
    """What openpyxl sees — kept ONLY to measure the gap, never as a source of truth."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import openpyxl

        wb = openpyxl.load_workbook(path)
        dv = 0
        per_sheet = {}
        for ws in wb.worksheets:
            n = len(ws.data_validations.dataValidation)
            dv += n
            per_sheet[ws.title] = n
    return {"openpyxl_data_validations": dv, "openpyxl_dv_per_sheet": per_sheet}


def probe_all(paths: Sequence[Path]) -> dict[str, Any]:
    """One key per measurement id. Canonical, sorted, reproducible."""
    files = {p.name: probe_one(p) for p in sorted(paths, key=lambda q: q.name)}
    totals = {
        "workbooks": len(files),
        "formula_cells": sum(v["N3_formula_cells"] for v in files.values()),
        "data_validations": sum(v["N4_data_validations"] for v in files.values()),
        "field_surface": sum(v["N7_field_surface"] for v in files.values()),
    }
    return {"totals": totals, "files": files}


def canonical(obj: Any) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0]) if argv else Path("fixtures/prescribed")
    paths = sorted(root.glob("*.xlsx"))
    if not paths:
        print(f"no workbooks under {root}", file=sys.stderr)
        return 1
    res = probe_all(paths)
    print(canonical(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
