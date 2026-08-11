#!/usr/bin/env python
"""foundation_probe.py — the measurements §0 of plan/02-phases-foundation.md rests on.

Run:  /Users/abishaikc/Gift/.venv/bin/python research/scripts/foundation_probe.py
Moves to tools/measure/foundation_probe.py at P0-B2 and becomes `make measure-foundation`.

Every figure printed here is MEASURED against the nine prescribed workbooks at
/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx, unmodified.

N1..N8 are the eight NEW measurements; the rest reproduce figures the spec already carries.
FOUR of the eight change a pre-registered gate. N1 is the one to read first: the blank
template's 505 cached values are 301 numeric zeros and 204 copies of the string "NA", so
gate G-EVAL as written is satisfied by an evaluator that computes nothing.
"""
from __future__ import annotations

import collections
import glob
import hashlib
import json
import os
import re
import sys
import warnings
import zipfile
from typing import Any

from lxml import etree

DIR = "/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle"
FME = "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
X14 = "{http://schemas.microsoft.com/office/spreadsheetml/2009/9/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def sheets_of(z: zipfile.ZipFile) -> list[tuple[str, str, str]]:
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm = {r.get("Id"): "xl/" + r.get("Target").lstrip("/") for r in rels}
    return [(s.get("name"), s.get("state") or "visible", rm[s.get(REL + "id")])
            for s in wb.find(M + "sheets")]


def style_classes(z: zipfile.ZipFile) -> tuple[set[int], set[int], set[int], int]:
    """-> (explicitly unlocked, explicitly locked, absent-<protection>, applyProtection=1)."""
    st = etree.fromstring(z.read("xl/styles.xml"))
    cx = st.find(M + "cellXfs")
    unlocked, locked, applyprot = set(), set(), 0
    for i, xf in enumerate(cx):
        if xf.get("applyProtection") in ("1", "true"):
            applyprot += 1
        prot = xf.find(M + "protection")
        if prot is None:
            continue
        (unlocked if prot.get("locked") in ("0", "false") else locked).add(i)
    absent = set(range(len(cx))) - unlocked - locked
    return unlocked, locked, absent, applyprot


def field_surface(path: str) -> dict[str, Any]:
    """The denominator, plus the two misreadings that would replace it (N2, N4)."""
    z = zipfile.ZipFile(path)
    unlocked, locked, absent, applyprot = style_classes(z)
    sh = sheets_of(z)
    protected = 0
    fs = all_unlocked = absent_nonformula = fs_visible_only = 0
    per_sheet: dict[str, int] = {}
    for name, state, part in sh:
        root = etree.fromstring(z.read(part))
        if root.find(M + "sheetProtection") is not None:
            protected += 1
        n = 0
        for c in root.iter(M + "c"):
            s = int(c.get("s") or 0)
            is_f = c.find(M + "f") is not None
            if s in unlocked:
                all_unlocked += 1
                if not is_f:
                    fs += 1
                    n += 1
                    if state == "visible":
                        fs_visible_only += 1
            if s in absent and not is_f:
                absent_nonformula += 1
        per_sheet[name] = n
    derivable = protected > 0
    return {
        "sheets": len(sh), "protected": protected,
        "style_ids": {"unlocked": len(unlocked), "explicit_locked": len(locked),
                      "absent_protection": len(absent), "applyProtection_1": applyprot},
        "field_surface": fs if derivable else None,          # None == "not derivable" (NC-D03)
        "field_surface_visible_sheets_only": fs_visible_only if derivable else None,   # N2
        "all_unlocked_in_used_ranges": all_unlocked,
        "absence_means_unlocked_would_add": absent_nonformula,                          # N4
        "per_sheet": {k: v for k, v in per_sheet.items() if v},
    }


def formulas_and_cache(path: str) -> dict[str, Any]:
    """Encoding census, function vocabulary (N5) and the cached-value census (N1)."""
    z = zipfile.ZipFile(path)
    enc = collections.Counter()
    fns = collections.Counter()
    cache = collections.Counter()
    groups: set[tuple[str, str]] = set()
    for name, _state, part in sheets_of(z):
        root = etree.fromstring(z.read(part))
        for c in root.iter(M + "c"):
            f = c.find(M + "f")
            if f is None:
                continue
            t = f.get("t") or "normal"
            body = "".join(f.itertext())
            if t == "shared":
                groups.add((name, f.get("si")))
                enc["SHARED_MASTER" if body.strip() else "SHARED_DEPENDENT"] += 1
            elif t == "array":
                enc["ARRAY"] += 1
            else:
                enc["TEXT"] += 1
            for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_.]*)\s*\(", body):
                fns[m.group(1)] += 1
            v = c.find(M + "v")
            val = v.text if v is not None else None
            ct = c.get("t") or "n"
            if val is None:
                cache["absent"] += 1
            elif ct == "str":
                cache[f"str:{val}"] += 1
            elif ct == "e":
                cache[f"err:{val}"] += 1
            else:
                cache["num:0" if float(val) == 0 else "num:nonzero"] += 1
    total = sum(enc.values())
    return {"total_formula_cells": total,
            "authored": enc["TEXT"] + enc["SHARED_MASTER"] + enc["ARRAY"],
            "encodings": dict(enc), "shared_groups": len(groups),
            "function_call_sites": dict(fns.most_common()),
            "cached_value_census": dict(cache)}


def validations(path: str) -> dict[str, Any]:
    """Per-sheet main/x14 split, and the 22->20 resolution rule (N7)."""
    z = zipfile.ZipFile(path)
    per, res = {}, collections.Counter()
    conditional = []
    for name, _state, part in sheets_of(z):
        root = etree.fromstring(z.read(part))
        main = list(root.iter(M + "dataValidation"))
        ext = list(root.iter(X14 + "dataValidation"))
        per[name] = (len(main), len(ext))
        for ns, dv in [("main", d) for d in main] + [("x14", d) for d in ext]:
            if dv.get("type") != "list":
                continue
            f1 = dv.find(M + "formula1")
            if f1 is None:
                f1 = dv.find(X14 + "formula1")
            txt = "".join(f1.itertext()) if f1 is not None else None
            if txt and "!" in txt and "$" in txt:
                res["RANGE"] += 1
            elif txt and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", txt):
                res["DEFINED_NAME"] += 1
            else:
                res["FILING_CONDITIONAL"] += 1
                conditional.append((name, dv.get("sqref"), txt))
    return {"per_sheet_main_x14": per,
            "total": sum(a + b for a, b in per.values()),
            "list_resolution": dict(res),
            "resolving": res["RANGE"] + res["DEFINED_NAME"],
            "filing_conditional": conditional}


def dropdown_wiring(path: str) -> dict[str, Any]:
    """Which of the 15 Dropdown vocabularies any validation actually enforces (N8)."""
    z = zipfile.ZipFile(path)
    used, referenced = set(), set()
    for name, _state, part in sheets_of(z):
        root = etree.fromstring(z.read(part))
        if name == "Dropdown":
            for c in root.iter(M + "c"):
                used.add(re.match(r"[A-Z]+", c.get("r")).group(0))
        for dv in list(root.iter(M + "dataValidation")) + list(root.iter(X14 + "dataValidation")):
            f1 = dv.find(M + "formula1")
            if f1 is None:
                f1 = dv.find(X14 + "formula1")
            txt = "".join(f1.itertext()) if f1 is not None else ""
            for m in re.finditer(r"Dropdown!\$([A-Z]+)\$", txt):
                referenced.add(m.group(1))
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    dn = wb.find(M + "definedNames")
    for d in (dn if dn is not None else []):
        for m in re.finditer(r"Dropdown!\$([A-Z]+)\$", d.text or ""):
            referenced.add(m.group(1))
    return {"columns_used": sorted(used), "columns_referenced": sorted(referenced),
            "wired": len(used & referenced), "unwired": sorted(used - referenced)}


def agreement_row(path: str) -> dict[str, Any]:
    """Readers A and B on the eight agreement fields (N3). One row of P1's 8x9 matrix."""
    z = zipfile.ZipFile(path)
    sh = sheets_of(z)
    a = {"n_sheets": len(sh), "sheet_names": [n for n, _, _ in sh],
         "hidden_sheets": [n for n, s, _ in sh if s != "visible"]}
    nc = nf = nv = mr = 0
    for _n, _s, part in sh:
        root = etree.fromstring(z.read(part))
        nc += len(list(root.iter(M + "c")))
        nf += len(list(root.iter(M + "f")))
        nv += len(list(root.iter(M + "dataValidation"))) + len(list(root.iter(X14 + "dataValidation")))
        m = root.find(M + "mergeCells")
        mr += int(m.get("count")) if m is not None else 0
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    dn = wb.find(M + "definedNames")
    a |= {"n_cells": nc, "n_formula_cells": nf, "n_validations": nv,
          "n_defined_names": len(dn) if dn is not None else 0, "merged_ranges": mr}

    import openpyxl  # imported late: reader B is a second instrument, not a dependency of A
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        w = openpyxl.load_workbook(path)
        seen = sorted({str(x.message) for x in caught})
    b = {"n_sheets": len(w.worksheets), "sheet_names": [s.title for s in w.worksheets],
         "hidden_sheets": [s.title for s in w.worksheets if s.sheet_state != "visible"]}
    bc = bf = bv = bm = 0
    for s in w.worksheets:
        for row in s.iter_rows():
            for c in row:
                if c.value is not None:
                    bc += 1
                if isinstance(c.value, str) and c.value.startswith("="):
                    bf += 1
        bv += len(s.data_validations.dataValidation)
        bm += len(s.merged_cells.ranges)
    b |= {"n_cells": bc, "n_formula_cells": bf, "n_validations": bv,
          "n_defined_names": len(w.defined_names), "merged_ranges": bm}
    fields = ("n_sheets", "sheet_names", "hidden_sheets", "n_cells", "n_formula_cells",
              "n_validations", "n_defined_names", "merged_ranges")
    return {"A": {k: a[k] for k in fields}, "B": {k: b[k] for k in fields},
            "agree": {k: a[k] == b[k] for k in fields}, "reader_b_warnings": seen}


def main() -> int:
    paths = sorted(glob.glob(os.path.join(DIR, "*.xlsx")))
    if not paths:
        print(f"no workbooks at {DIR}", file=sys.stderr)
        return 1
    fme = os.path.join(DIR, FME)

    out: dict[str, Any] = {"corpus": {}, "fme": {}}
    for p in paths:
        out["corpus"][os.path.basename(p)] = {
            "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
            "bytes": os.path.getsize(p),
            **field_surface(p),
        }
    out["fme"] = {
        "N1_cached_and_formula_census": formulas_and_cache(fme),
        "N3_agreement_row": agreement_row(fme),
        "N7_validations": validations(fme),
        "N8_dropdown_wiring": dropdown_wiring(fme),
    }

    f = out["fme"]["N1_cached_and_formula_census"]
    a = out["fme"]["N3_agreement_row"]
    v = out["fme"]["N7_validations"]
    d = out["fme"]["N8_dropdown_wiring"]
    s = out["corpus"][FME]

    print("=== N1  the blank's cached values carry no information ===")
    print("   ", f["cached_value_census"], " <- 301 zeros + 204 'NA', 0 non-zero numeric")
    print("=== N2  visible-sheets-only does not move the denominator ===")
    print("    field_surface", s["field_surface"], " visible-only", s["field_surface_visible_sheets_only"])
    print("=== N3  readers disagree on 4 of 8 fields, 3 of them definitionally ===")
    for k, ok in a["agree"].items():
        if not ok:
            print(f"    {k:18s} A={str(a['A'][k])[:14]:>14s}  B={str(a['B'][k])[:14]:>14s}")
    print("    reader B warnings:", a["reader_b_warnings"])
    print("=== N4  322 of 434 cellXfs declare no <protection> ===")
    print("   ", s["style_ids"], " absence-means-unlocked would add",
          s["absence_means_unlocked_would_add"], "->", s["field_surface"] + s["absence_means_unlocked_would_add"])
    print("=== N5  nine functions, not eight; one array formula ===")
    print("   ", f["function_call_sites"])
    print("   ", f["encodings"], "shared groups", f["shared_groups"])
    print("=== N7  22 list validations resolve as 19 + 1 + 2 -> resolving = 20 ===")
    print("   ", v["list_resolution"], "resolving", v["resolving"])
    print("    filing-conditional:", v["filing_conditional"])
    print("=== N8  2 of 15 Dropdown vocabularies are wired to nothing ===")
    print("   ", "wired", d["wired"], "unwired columns", d["unwired"])
    print("=== field surface, all nine (None == no protection mask) ===")
    for name, row in out["corpus"].items():
        print(f"    {name[:52]:52s} {str(row['field_surface']):>6s}")

    with open(os.environ.get("FOUNDATION_PROBE_JSON", "/dev/null"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
