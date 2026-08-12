#!/usr/bin/env python
"""Synthetic fixtures by RAW-ZIP SURGERY, never openpyxl.

openpyxl's round trip on these workbooks is destructive — 3,663,391 bytes to 65,877, and
all 19 x14 validations gone. A fixture built with it would be a different document, and a
test against it would measure the tool that made it.

So every fixture here rewrites one part of the zip and copies the rest byte-for-byte, with
a fixed date_time so output is byte-identical across runs.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIX = REPO / "fixtures" / "prescribed"
OUT = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
FIXED = (2026, 1, 1, 0, 0, 0)


def _rewrite(src: Path, dst: Path, edits: dict[str, bytes]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = edits.get(info.filename, zin.read(info.filename))
            ni = zipfile.ZipInfo(info.filename, date_time=FIXED)
            ni.compress_type = zipfile.ZIP_DEFLATED
            ni.external_attr = info.external_attr
            zout.writestr(ni, data)


def _portfolio_part(z: zipfile.ZipFile) -> str:
    """The worksheet part backing '3. Portfolio'."""
    from cdfc.ingest.reader_lxml import _sheet_parts  # noqa: PLC0415

    for name, _state, part in _sheet_parts(z):
        if name.strip().lower().startswith("3."):
            return part
    raise LookupError("no '3. Portfolio' sheet")


def build() -> dict[str, str]:
    sys.path.insert(0, str(REPO / "src"))
    OUT.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(FME) as z:
        part = _portfolio_part(z)
        xml = z.read(part).decode("utf-8")

    # 1. a row inserted above row 7: every row from 7 down shifts by one.
    #    A coordinate-shaped key silently rebinds here; a stable key must resolve to the
    #    correct new reference or refuse.
    def _shift(m: re.Match[str]) -> str:
        col, row = m.group(1), int(m.group(2))
        return f'r="{col}{row + 1}"' if row >= 7 else m.group(0)

    shifted = re.sub(r'r="([A-Z]+)(\d+)"', _shift, xml)
    _rewrite(FME, OUT / "row-inserted__portfolio-r7.xlsx", {part: shifted.encode()})

    # 2. a formula cell overwritten with a literal — the TEMPLATE_DIFF target.
    #    This MUST still bind to the template (the fingerprint excludes formula content)
    #    so it can be reported as a FINDING rather than as invalid.template_unbound.
    # O7 is `<f t="shared" si="0"/>` — SELF-CLOSING. A pattern of `<f...>.*?</f>` runs
    # past it to the NEXT cell's `</f>` and corrupts a second cell: the first version of
    # this fixture destroyed two formula cells while claiming to overwrite one, and the
    # only reason it was caught is that the formula count was checked (505 -> 503, not
    # 504). Both encodings are handled explicitly.
    # REPAIRED AT P5. Both transforms here were patterns over OOXML, and `ci/no-regex-over-xml.sh`
    # — the sibling gate `ci/no-regex-over-cel.sh` names and that did not exist until P5 — found
    # them on its first run. The comment above records what the pattern form already cost once: it
    # destroyed two formula cells while claiming to overwrite one. The elements are edited through
    # the one parser factory now, so the self-closing `<f/>` case stops being a special case at
    # all — it is an element with no children.
    overwritten = _overwrite_formula_cell(xml, "O7", "999999")
    _rewrite(FME, OUT / "formula-overwritten__portfolio-O7.xlsx", {part: overwritten})

    # 3. fifty values written into field-surface cells — the fingerprint must NOT move.
    _rewrite(FME, OUT / "values-written__50-cells.xlsx", {part: _write_fifty_values(xml)})

    made = {}
    for f in sorted(OUT.glob("*.xlsx")):
        made[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / "MANIFEST.json").write_text(
        json.dumps({"generated_by": "tools/fixtures/make_synthetic.py", "base": FME.name,
                    "files": made}, indent=1, sort_keys=True) + "\n"
    )
    return made


def main() -> int:
    for name, d in sorted(build().items()):
        print(f"  {d[:12]}  {name}")
    return 0


M_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _parse(xml: str | bytes):
    import sys as _sys

    _sys.path.insert(0, str(REPO / "src"))
    from cdfc.ingest.xmlsafe import fromstring

    return fromstring(xml.encode() if isinstance(xml, str) else xml)


def _serialise(root) -> bytes:
    from lxml import etree

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _sub_element(parent, tag: str):
    from lxml import etree

    return etree.SubElement(parent, tag)


def _overwrite_formula_cell(xml: str, ref: str, literal: str) -> bytes:
    """F11 — a cell the pinned blank declares a formula for carries a literal instead."""
    root = _parse(xml)
    for c in root.iter(f"{M_NS}c"):
        if c.get("r") != ref:
            continue
        for child in list(c):
            c.remove(child)
        c.attrib.pop("t", None)
        _sub_element(c, f"{M_NS}v").text = literal
        break
    return _serialise(root)


def _write_fifty_values(xml: str) -> bytes:
    """Fifty EMPTY field-surface cells given a value. The fingerprint must NOT move."""
    root = _parse(xml)
    written = 0
    for c in root.iter(f"{M_NS}c"):
        if written >= 50 or len(c) or c.get("t"):
            continue
        _sub_element(c, f"{M_NS}v").text = "1"
        written += 1
    return _serialise(root)


if __name__ == "__main__":
    raise SystemExit(main())

