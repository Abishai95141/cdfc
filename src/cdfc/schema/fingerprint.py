"""The structural fingerprint — what binds a filing to a template version.

**FORMULA CONTENT IS DELIBERATELY EXCLUDED, and the exclusion is load-bearing.**

A filer who overwrites a formula cell with a literal must fail a PREDICATE — that is
`TEMPLATE_DIFF`, the flagship check, and the one thing in the design nothing else can do.
If formula content entered the fingerprint, that filing would fail to *bind* instead, and
would be reported as `invalid.template_unbound`: an apparatus failure about US rather than
a finding about the FILING. The most valuable check in the system would be converted into
a shrug.

So the fingerprint covers structure a filer cannot lawfully change — sheet names and
states, per-sheet dimension, the merged-range set, the defined-name list, and the unlocked
mask — and nothing else.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from cdfc.canon import canonical_json, sha256_hex
from cdfc.ingest.xmlsafe import fromstring
from cdfc.schema.styles_mask import Rule, build

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


def structural_projection(blob_path: Path) -> dict[str, object]:
    """The exact object the fingerprint is taken over. Returned so a mismatch can be
    diffed rather than merely reported."""
    with zipfile.ZipFile(blob_path) as z:
        wb = fromstring(z.read("xl/workbook.xml"))
        rels = fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid = {r.get("Id"): r.get("Target") for r in rels.iter(f"{{{PR}}}Relationship")}

        sheets: list[dict[str, object]] = []
        merged: list[str] = []
        for sh in wb.iter(f"{{{M}}}sheet"):
            name = sh.get("name", "")
            state = sh.get("state", "visible")
            t = (rid.get(sh.get(f"{{{R}}}id"), "") or "").lstrip("/")
            part = t if t.startswith("xl/") else f"xl/{t}"
            dim = None
            if part in z.namelist():
                root = fromstring(z.read(part))
                d = root.find(f"{{{M}}}dimension")
                dim = d.get("ref") if d is not None else None
                merged.extend(mc.get("ref", "") for mc in root.iter(f"{{{M}}}mergeCell"))
            sheets.append({"name": name, "state": state, "dimension": dim})

        dnames: list[str] = []
        dn = wb.find(f"{{{M}}}definedNames")
        if dn is not None:
            dnames = sorted(d.get("name", "") for d in dn.findall(f"{{{M}}}definedName"))

    fs = build(blob_path, Rule.V3)
    return {
        "sheets": sheets,
        "merged_ranges": sorted(merged),
        "defined_names": dnames,
        "unlocked_mask": sorted(f"{s}!{r}" for s, r in fs.cells),
        # NOTE: no formula content, by design. See the module docstring.
    }


def structural_fingerprint(blob_path: Path) -> str:
    return sha256_hex(canonical_json(structural_projection(blob_path)))
