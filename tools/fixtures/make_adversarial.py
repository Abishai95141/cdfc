#!/usr/bin/env python
"""Build the adversarial fixtures, deterministically from a seed.

These are the container guard's negative controls. They are GENERATED rather than
committed as binaries because a reviewer must be able to see what makes each one
adversarial — a committed zip bomb is a blob nobody can read.

Determinism matters: `zipfile` writes an mtime into every local header, so every entry
gets a fixed `date_time` and the output is byte-identical across runs. Without that the
fixtures drift and `corpus-verify` would report drift that means nothing.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "fixtures" / "adversarial"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)

MINIMAL_PARTS = {
    "[Content_Types].xml": b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
    "xl/workbook.xml": b'<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets/></workbook>',
    "xl/_rels/workbook.xml.rels": b'<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
}


def _write(path: Path, entries: dict[str, bytes], *, compress: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    with zipfile.ZipFile(path, "w", mode) as z:
        for name, body in entries.items():
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.compress_type = mode
            z.writestr(info, body)


def build() -> dict[str, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    made: dict[str, str] = {}

    # 1. entry count over the limit (1024)
    e = dict(MINIMAL_PARTS)
    for i in range(1200):
        e[f"xl/worksheets/sheet{i}.xml"] = b"<x/>"
    _write(OUT / "zipbomb-entrycount__x1200.xlsx", e)

    # 2. compression ratio over the limit (100:1)
    e = dict(MINIMAL_PARTS)
    e["xl/model/item.data"] = b"\x00" * (2 * 1024 * 1024)  # compresses ~1000:1
    _write(OUT / "zipbomb-ratio__x1000.xlsx", e)

    # 3. single entry over the per-entry limit (16 MiB)
    e = dict(MINIMAL_PARTS)
    e["xl/model/item.data"] = (b"cdfc" * 64) * (17 * 1024 * 1024 // 256)
    _write(OUT / "zipbomb-entrysize__17mb.xlsx", e, compress=False)

    # 4. XXE — an external entity pointed at a local file.
    #
    # THE ENTITY MUST BE IN ELEMENT TEXT, NOT IN AN ATTRIBUTE. The first version of this
    # fixture put it in `sheet name="&xxe;"`, and lxml refuses external entities in
    # attributes REGARDLESS of parser configuration — so the hardened and unhardened
    # parsers behaved identically and the control discriminated nothing. A control that
    # would also pass on a broken build is not a control.
    e = dict(MINIMAL_PARTS)
    e["xl/workbook.xml"] = (
        b'<?xml version="1.0"?>\n'
        b'<!DOCTYPE workbook [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n'
        b'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        b"<sheets><sheet>&xxe;</sheet></sheets></workbook>"
    )
    _write(OUT / "xxe-entity__passwd.xlsx", e)

    # 5. not a zip at all, renamed
    p = OUT / "not-a-zip__renamed.xlsx"
    p.write_bytes(b"This is not a zip container. It is a text file with an .xlsx name.\n")

    # 6. a required part missing
    e = {k: v for k, v in MINIMAL_PARTS.items() if k != "xl/workbook.xml"}
    _write(OUT / "missing-part__no-workbook.xlsx", e)

    # 7. a disallowed entry suffix — an executable smuggled into the container
    e = dict(MINIMAL_PARTS)
    e["xl/macros/payload.sh"] = b"#!/bin/sh\necho no\n"
    _write(OUT / "disallowed-suffix__shell.xlsx", e)

    for f in sorted(OUT.glob("*.xlsx")):
        made[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / "MANIFEST.json").write_text(
        json.dumps({"generated_by": "tools/fixtures/make_adversarial.py", "files": made},
                   indent=1, sort_keys=True) + "\n"
    )
    return made


def main() -> int:
    made = build()
    for name, d in sorted(made.items()):
        print(f"  {d[:12]}  {name}")
    print(f"{len(made)} adversarial fixtures in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
