"""READER A' — an independently written second implementation of the same eight fields.

WHY IT EXISTS. Reader B (openpyxl) is not a competent party for four of the eight
agreement fields — it is namespace-blind on validations, returns objects rather than text
for array formulas, counts values rather than cells, and sees only workbook-scoped
defined names. On those four, comparing A against B would compare a reading against a
known-wrong reading, so the check would fire every time and be switched off. A' gives
those four fields a second party.

**A' IS DELIBERATELY NOT A REFACTOR OF A.** It reaches the same eight numbers by a
different route:

* A walks `xl/workbook.xml`'s relationship graph to find worksheet parts.
  A' enumerates `[Content_Types].xml` overrides and filters by content type.
* A dispatches on `<f t="...">`. A' counts `<f>` elements structurally and classifies
  afterwards.
* A resolves x14 validations through `<extLst>` traversal from the sheet root.
  A' collects every element whose qualified name is `{x14}dataValidation`, wherever it is.

A shared traversal bug is the only way two readings can be wrong together, and this is
what removes it. **Same author, though**: the honest label on the four A/A′-only fields is
SAME-AUTHOR, and the agreement matrix publishes those separately for that reason.
"""

from __future__ import annotations

import zipfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from cdfc.ingest.xmlsafe import fromstring

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
X14 = "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
WORKSHEET_CT = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
)


@dataclass(frozen=True)
class RawWorkbookB:
    n_sheets: int
    sheet_names: tuple[str, ...]
    hidden_sheets: tuple[str, ...]
    n_cells: int
    n_formula_cells: int
    n_validations: int
    n_defined_names: int
    merged_ranges: tuple[str, ...]


def read_b(blob_path: Path) -> RawWorkbookB:
    with zipfile.ZipFile(blob_path) as z:
        # --- route 1: part enumeration from [Content_Types].xml, not the rel graph ---
        ct = fromstring(z.read("[Content_Types].xml"))
        worksheet_parts = [
            o.get("PartName", "").lstrip("/")
            for o in ct.iter(f"{{{CT}}}Override")
            if o.get("ContentType") == WORKSHEET_CT
        ]
        # `[Content_Types].xml` gives no order and no names; names come from workbook.xml,
        # but the SET of parts is derived independently. If the two disagree on how many
        # worksheet parts exist, that is itself a finding.
        wb = fromstring(z.read("xl/workbook.xml"))
        sheet_els = list(wb.iter(f"{{{M}}}sheet"))
        names = tuple(s.get("name", "") for s in sheet_els)
        hidden = tuple(s.get("name", "") for s in sheet_els if s.get("state", "visible") != "visible")

        n_cells = 0
        n_formula_cells = 0
        n_validations = 0
        merged: list[str] = []

        for part in sorted(worksheet_parts):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            # --- route 2: structural counting, classification afterwards -------------
            for el in root.iter():
                tag = el.tag
                if not isinstance(tag, str):
                    continue
                if tag == f"{{{M}}}c":
                    n_cells += 1
                    # a formula cell is one with an <f> child, whatever its encoding
                    for child in el:
                        if child.tag == f"{{{M}}}f":
                            n_formula_cells += 1
                            break
                elif tag == f"{{{M}}}mergeCell":
                    merged.append(el.get("ref", ""))
                # --- route 3: qualified-name match anywhere in the tree --------------
                elif tag in (f"{{{M}}}dataValidation", f"{{{X14}}}dataValidation"):
                    n_validations += 1

        dn = wb.find(f"{{{M}}}definedNames")
        n_defined = 0 if dn is None else len(dn.findall(f"{{{M}}}definedName"))

    return RawWorkbookB(
        n_sheets=len(sheet_els),
        sheet_names=names,
        hidden_sheets=hidden,
        n_cells=n_cells,
        n_formula_cells=n_formula_cells,
        n_validations=n_validations,
        n_defined_names=n_defined,
        merged_ranges=tuple(merged),
    )


def agreement_view(wb: RawWorkbookB) -> Mapping[str, object]:
    return {
        "n_sheets": wb.n_sheets,
        "sheet_names": list(wb.sheet_names),
        "hidden_sheets": list(wb.hidden_sheets),
        "n_cells": wb.n_cells,
        "n_formula_cells": wb.n_formula_cells,
        "n_validations": wb.n_validations,
        "n_defined_names": wb.n_defined_names,
        "merged_ranges": sorted(wb.merged_ranges),
    }
