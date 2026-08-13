"""READER A — the authoritative reading. Raw zipfile + lxml, namespace-aware.

Authoritative because it is the only reader that sees all four of the fields the
ecosystem's standard library is blind to. Every one of those blindnesses is measured, not
assumed, and the measurements are in `docs/READER-COMPETENCE.md`.

Traversal: workbook.xml's relationship graph. Reader A' (`reader_lxml_b.py`) computes the
same eight fields by a DIFFERENT traversal — `[Content_Types].xml` part enumeration —
precisely so that a shared traversal bug cannot make both agree and both be wrong.
"""

from __future__ import annotations

import zipfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from cdfc.ingest.xmlsafe import fromstring

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
X14 = "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main"
# The x14 extension puts its FORMULA BODY and its SQREF in a third namespace, `xm:`, not in
# x14 and not in main. Reading them from {X14} returned the empty string for all 19 x14
# validations on FME — the COUNT was right and every BODY was empty, and nothing caught it
# because every cross-check compared counts. Found at P4 when the harvest produced zero
# membership predicates from them. This is the same defect shape as `<f[ >][^>]*>` over OOXML:
# a correct count with wrong contents.
XM = "http://schemas.microsoft.com/office/excel/2006/main"

FormulaEncoding = Literal["TEXT", "SHARED_MASTER", "SHARED_DEPENDENT", "ARRAY", "NONE"]


@dataclass(frozen=True)
class SheetRecord:
    name: str
    state: str
    part: str
    sheet_sha256: str
    protected: bool
    dimension: str | None


@dataclass(frozen=True)
class FormulaRecord:
    sheet: str
    ref: str
    encoding: FormulaEncoding
    text: str | None  # None iff encoding == SHARED_DEPENDENT
    si: int | None
    master_ref: str | None
    shared_ref_range: str | None
    materialised: str | None = None


@dataclass(frozen=True)
class ValidationRecord:
    sheet: str
    namespace: Literal["main", "x14"]
    type: str
    sqref: str
    formula1: str | None
    formula2: str | None
    resolution: Literal["RANGE", "DEFINED_NAME", "FILING_CONDITIONAL", "UNRESOLVED"]
    resolved_range: str | None
    # ADDED AT P4, and its absence was not cosmetic: `formula1` alone does not say whether a
    # bound is a floor, a ceiling or an equality. A harvest that defaulted to `>=` would be
    # writing a threshold the artifact never stated.
    operator: str = ""


@dataclass(frozen=True)
class DefinedName:
    name: str
    scope: str  # "WORKBOOK" or a sheet name
    value: str
    is_ref_error: bool


@dataclass(frozen=True)
class StyleTable:
    unlocked_style_ids: frozenset[int]
    n_cell_xfs: int


@dataclass(frozen=True)
class RawWorkbook:
    sheets: tuple[SheetRecord, ...]
    n_cells: int
    formulas: tuple[FormulaRecord, ...]
    validations: tuple[ValidationRecord, ...]
    defined_names: tuple[DefinedName, ...]
    merged_ranges: tuple[str, ...]
    styles: StyleTable
    shared_strings: tuple[str, ...]
    unlocked_cells: tuple[tuple[str, str], ...]  # (sheet, ref) — the field surface

    # --- the eight agreement fields, computed once, named once -------------------
    @property
    def n_sheets(self) -> int:
        return len(self.sheets)

    @property
    def sheet_names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.sheets)

    @property
    def hidden_sheets(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.sheets if s.state != "visible")

    @property
    def n_formula_cells(self) -> int:
        """Every <c> containing an <f> child, ANY encoding.

        The definition matters: counting only formulas with TEXT misses the 211 shared
        dependents in the FME workbook, which is 211 of 505 formula cells.
        """
        return len(self.formulas)

    @property
    def n_validations(self) -> int:
        return len(self.validations)

    @property
    def n_defined_names(self) -> int:
        return len(self.defined_names)


def _sha(b: bytes) -> str:
    import hashlib

    return hashlib.sha256(b).hexdigest()


def _sheet_parts(z: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    wb = fromstring(z.read("xl/workbook.xml"))
    rels = fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid = {r.get("Id"): r.get("Target") for r in rels.iter(f"{{{PR}}}Relationship")}
    out = []
    for sh in wb.iter(f"{{{M}}}sheet"):
        t = rid.get(sh.get(f"{{{R}}}id"), "")
        out.append((sh.get("name", ""), sh.get("state", "visible"), _resolve_part(t)))
    return out


def _resolve_part(target: str) -> str:
    """Resolve a relationship Target against the `xl/` base.

    A Target may be RELATIVE (`worksheets/sheet1.xml`) or ABSOLUTE
    (`/xl/worksheets/sheet1.xml`). The nine prescribed workbooks all use the relative
    form, so a naive `"xl/" + target` worked on the whole corpus and produced
    `xl/xl/worksheets/sheet1.xml` the first time it met a file written by openpyxl.

    Found by the round-trip golden, not by the corpus — which is the argument for having
    a fixture the corpus did not produce.
    """
    t = target.lstrip("/")
    return t if t.startswith("xl/") else f"xl/{t}"


def _classify_dv_resolution(f1: str | None, defined: set[str]) -> tuple[str, str | None]:
    if not f1:
        return "UNRESOLVED", None
    s = f1.strip()
    if s.startswith('"'):
        return "RANGE", s  # inline literal list
    if "!" in s or "$" in s or ":" in s:
        return "RANGE", s
    if s in defined:
        return "DEFINED_NAME", s
    if any(op in s for op in ("(", "=", "<", ">")):
        return "FILING_CONDITIONAL", None
    return "UNRESOLVED", None


def read(blob_path: Path) -> RawWorkbook:
    with zipfile.ZipFile(blob_path) as z:
        names = set(z.namelist())

        # styles
        unlocked: set[int] = set()
        n_xfs = 0
        if "xl/styles.xml" in names:
            st = fromstring(z.read("xl/styles.xml"))
            cx = st.find(f"{{{M}}}cellXfs")
            if cx is not None:
                xfs = cx.findall(f"{{{M}}}xf")
                n_xfs = len(xfs)
                for i, xf in enumerate(xfs):
                    p = xf.find(f"{{{M}}}protection")
                    if p is not None and p.get("locked") == "0":
                        unlocked.add(i)

        # shared strings
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            ss = fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss.iter(f"{{{M}}}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{M}}}t")))

        # defined names
        wb = fromstring(z.read("xl/workbook.xml"))
        sheet_order = [s.get("name", "") for s in wb.iter(f"{{{M}}}sheet")]
        dnames: list[DefinedName] = []
        dn_parent = wb.find(f"{{{M}}}definedNames")
        if dn_parent is not None:
            for dn in dn_parent.findall(f"{{{M}}}definedName"):
                val = (dn.text or "").strip()
                lid = dn.get("localSheetId")
                scope = "WORKBOOK"
                if lid is not None and lid.isdigit() and int(lid) < len(sheet_order):
                    scope = sheet_order[int(lid)]
                dnames.append(
                    DefinedName(dn.get("name", ""), scope, val, "#REF!" in val)
                )
        defined_set = {d.name for d in dnames}

        sheets: list[SheetRecord] = []
        formulas: list[FormulaRecord] = []
        validations: list[ValidationRecord] = []
        merged: list[str] = []
        unlocked_cells: list[tuple[str, str]] = []
        n_cells = 0

        for name, state, part in _sheet_parts(z):
            raw = z.read(part)
            root = fromstring(raw)
            dim = root.find(f"{{{M}}}dimension")
            protected = root.find(f"{{{M}}}sheetProtection") is not None
            sheets.append(
                SheetRecord(name, state, part, _sha(raw), protected,
                            dim.get("ref") if dim is not None else None)
            )

            shared_master: dict[int, tuple[str, str]] = {}
            pending_dependents: list[tuple[str, int]] = []

            for c in root.iter(f"{{{M}}}c"):
                n_cells += 1
                ref = c.get("r", "")
                f = c.find(f"{{{M}}}f")
                if f is None:
                    s = c.get("s")
                    if s is not None and s.isdigit() and int(s) in unlocked:
                        unlocked_cells.append((name, ref))
                    continue
                t = f.get("t")
                body = (f.text or "").strip()
                si = int(f.get("si")) if f.get("si", "").isdigit() else None
                if t == "shared":
                    if body:
                        shared_master[si] = (ref, body)  # type: ignore[index]
                        formulas.append(FormulaRecord(name, ref, "SHARED_MASTER", body, si,
                                                      None, f.get("ref")))
                    else:
                        pending_dependents.append((ref, si))  # type: ignore[arg-type]
                        formulas.append(FormulaRecord(name, ref, "SHARED_DEPENDENT", None, si,
                                                      None, None))
                elif t == "array":
                    formulas.append(FormulaRecord(name, ref, "ARRAY", body, None, None, f.get("ref")))
                else:
                    formulas.append(FormulaRecord(name, ref, "TEXT", body, None, None, None))

            merged.extend(mc.get("ref", "") for mc in root.iter(f"{{{M}}}mergeCell"))

            for dv in root.iter(f"{{{M}}}dataValidation"):
                f1 = dv.findtext(f"{{{M}}}formula1")
                f2 = dv.findtext(f"{{{M}}}formula2")
                res, rng = _classify_dv_resolution(f1, defined_set)
                validations.append(
                    ValidationRecord(name, "main", dv.get("type", ""), dv.get("sqref", ""),
                                     f1, f2, res, rng, dv.get("operator", ""))  # type: ignore[arg-type]
                )
            # x14 — the extension namespace openpyxl discards with a warning
            for dv in root.iter(f"{{{X14}}}dataValidation"):
                # `xm:` first — that is where Excel actually writes them.
                f1 = (dv.findtext(f"{{{X14}}}formula1/{{{XM}}}f")
                      or dv.findtext(f"{{{X14}}}formula1/{{{M}}}f")
                      or dv.findtext(f"{{{X14}}}formula1"))
                f2 = (dv.findtext(f"{{{X14}}}formula2/{{{XM}}}f")
                      or dv.findtext(f"{{{X14}}}formula2/{{{M}}}f")
                      or dv.findtext(f"{{{X14}}}formula2"))
                sq = (dv.findtext(f"{{{XM}}}sqref")
                      or dv.findtext(f"{{{X14}}}sqref")
                      or dv.get("sqref", ""))
                res, rng = _classify_dv_resolution(f1, defined_set)
                validations.append(
                    ValidationRecord(name, "x14", dv.get("type", ""), sq, f1, f2, res, rng,
                                     dv.get("operator", ""))  # type: ignore[arg-type]
                )

    return RawWorkbook(
        sheets=tuple(sheets),
        n_cells=n_cells,
        formulas=tuple(formulas),
        validations=tuple(validations),
        defined_names=tuple(dnames),
        merged_ranges=tuple(merged),
        styles=StyleTable(frozenset(unlocked), n_xfs),
        shared_strings=tuple(shared),
        unlocked_cells=tuple(unlocked_cells),
    )


def agreement_view(wb: RawWorkbook) -> Mapping[str, object]:
    """The eight fields, in the one shape `agreement.compare` consumes."""
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
