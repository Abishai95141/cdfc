"""Cell text and DECLARED number formats, read from the raw zip. **openpyxl is not used here.**

That is not a preference. `pytest.ini` turns openpyxl's warnings into errors (NC-CI02), and the
warning this workbook raises -- *"Data Validation extension is not supported and will be
removed"* -- is not noise: 19 of its 54 validations live in the `x14` namespace, and a reader that
drops them reports zero inline vocabularies, which is a clean, empty and WRONG answer. The gate is
telling the truth about the reader, so the reader changes.

Everything here is `zipfile` + `lxml` over the same bytes the fingerprint is taken from, which is
also what `ci/no-regex-over-xml.sh` requires: XML is parsed, never matched — and every parse goes
through `cdfc.ingest.xmlsafe.fromstring`, the single hardened factory. This module reached
`lxml.etree.fromstring` directly on its first run and `NC-P08` failed the build: the XXE spy in
NC-P05a can only watch one door, so a second call site defeats the control without saying so.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

from cdfc.ingest.xmlsafe import fromstring   # the ONE hardened factory; NC-P08 walks the AST

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"

# The built-in numFmtId ranges Excel reserves. A cell whose style points at one of these has a
# DECLARED type even though the workbook writes no `numFmtCode` for it.
BUILTIN: dict[int, str] = {
    **{i: "number" for i in (1, 2, 3, 4, 37, 38, 39, 40)},
    **{i: "percent" for i in (9, 10)},
    **{i: "date" for i in (14, 15, 16, 17, 22, 27, 30, 36, 45, 46, 47, 50, 57, 58)},
    **{i: "money" for i in (5, 6, 7, 8, 41, 42, 43, 44)},
    49: "text",
}


@dataclass(frozen=True, slots=True)
class Cell:
    sheet: str
    ref: str
    text: str | None          # the cell's own text, shared strings resolved
    is_text: bool             # is that text a STRING, or the decimal rendering of a number?
    number_format: str        # the format CODE, or "" when the style declares none
    builtin: str              # "number" | "percent" | "date" | "money" | "text" | ""


def read_cells(blob: Path) -> tuple[Cell, ...]:
    with zipfile.ZipFile(blob) as z:
        shared = _shared_strings(z)
        fmt_code, fmt_id = _formats(z)
        out: list[Cell] = []
        for name, part in _sheet_parts(z):
            root = fromstring(z.read(part))
            for c in root.iter(f"{M}c"):
                ref = c.get("r")
                if ref is None:
                    continue
                s = int(c.get("s") or 0)
                text, is_text = _text(c, shared)
                out.append(Cell(
                    sheet=name,
                    ref=ref,
                    text=text,
                    is_text=is_text,
                    number_format=fmt_code.get(s, ""),
                    builtin=BUILTIN.get(fmt_id.get(s, 0), ""),
                ))
    return tuple(out)


def _text(c, shared: list[str]) -> tuple[str | None, bool]:
    """`(text, is_it_a_string)`.

    **The flag is not cosmetic.** A numeric cell also carries `<v>`, so returning its digits as
    "text" makes every number to the left of a field look like that field's label. That inflated
    the labelled population from 498 to 2,169 on the FME return the first time this reader ran --
    the same denominator-by-unwritten-convention defect `M-CEIL` measured, reintroduced by a
    reader instead of by a rule.
    """
    t = c.get("t")
    if t == "inlineStr":
        node = c.find(f"{M}is")
        return (("".join(node.itertext()).strip(), True) if node is not None else (None, False))
    v = c.find(f"{M}v")
    if v is None or v.text is None:
        return (None, False)
    if t == "s":
        try:
            return (shared[int(v.text)], True)
        except (ValueError, IndexError):
            return (None, False)
    return (v.text, t == "str")


def _shared_strings(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(si.itertext()).strip() for si in root.iter(f"{M}si")]


def _formats(z: zipfile.ZipFile) -> tuple[dict[int, str], dict[int, int]]:
    """`style index -> (format code, numFmtId)`, resolving custom codes through `numFmts`."""
    if "xl/styles.xml" not in z.namelist():
        return ({}, {})
    root = fromstring(z.read("xl/styles.xml"))
    custom = {int(n.get("numFmtId")): (n.get("formatCode") or "")
              for n in root.iter(f"{M}numFmt") if n.get("numFmtId")}
    codes: dict[int, str] = {}
    ids: dict[int, int] = {}
    xfs = root.find(f"{M}cellXfs")
    if xfs is None:
        return ({}, {})
    for i, xf in enumerate(xfs.iter(f"{M}xf")):
        fid = int(xf.get("numFmtId") or 0)
        ids[i] = fid
        codes[i] = custom.get(fid, "")
    return (codes, ids)


def _sheet_parts(z: zipfile.ZipFile) -> list[tuple[str, str]]:
    wb = fromstring(z.read("xl/workbook.xml"))
    rels = fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels.iter(f"{PR}Relationship")}
    out: list[tuple[str, str]] = []
    for sh in wb.iter(f"{M}sheet"):
        rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        t = target.get(rid or "")
        if not t:
            continue
        part = t[1:] if t.startswith("/") else (t if t.startswith("xl/") else f"xl/{t}")
        if part in z.namelist():
            out.append((sh.get("name") or "", part))
    return out
