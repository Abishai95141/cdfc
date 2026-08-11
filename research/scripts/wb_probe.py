#!/usr/bin/env python
"""
wb_probe.py — deterministic structural probe of IFSCA prescribed reporting workbooks.

Run:  /Users/abishaikc/Gift/.venv/bin/python wb_probe.py <dir-or-files...>

Design notes (these matter — the brief records a regex miss that produced a
confident wrong answer, RND-BRIEF §4.4):
  * Parse OOXML with lxml, never with a regex over the XML text.
  * Count <f> ELEMENTS, not <f>text</f> matches. A shared-formula dependent cell
    is <f t="shared" si="N"/> with NO text node; a regex requiring a closing tag
    with a text body silently drops every one of them.
  * Report the master/dependent split explicitly so the denominator is legible.
  * Never call openpyxl's data_only=True here: these are blank templates, so a
    cached value is a template artefact, not a filed value.
"""
import sys, os, zipfile, json, re, hashlib
from collections import Counter, defaultdict
from lxml import etree

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKGREL = "http://schemas.openxmlformats.org/package/2006/relationships"
M = "{%s}" % MAIN
R = "{%s}" % REL


def _q(tag):
    return M + tag


def sheet_map(z):
    """Return [(sheet_name, sheetId, state, part_path)] in workbook order."""
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for s in wb.iter(_q("sheet")):
        rid = s.get(R + "id")
        tgt = rid2t.get(rid, "")
        if tgt.startswith("/"):
            part = tgt.lstrip("/")
        elif tgt.startswith("xl/"):
            part = tgt
        else:
            part = "xl/" + tgt
        out.append((s.get("name"), s.get("sheetId"), s.get("state") or "visible", part))
    return out


def defined_names(z):
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    out = []
    for dn in wb.iter(_q("definedName")):
        out.append({
            "name": dn.get("name"),
            "localSheetId": dn.get("localSheetId"),
            "hidden": dn.get("hidden"),
            "value": (dn.text or "")[:200],
        })
    return out


def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = etree.fromstring(z.read("xl/sharedStrings.xml"))
    out = []
    for si in root.iter(_q("si")):
        # concatenate every <t> descendant (rich text runs)
        out.append("".join(t.text or "" for t in si.iter(_q("t"))))
    return out


FUNC_HEAD = re.compile(r"^([A-Z][A-Z0-9_.]*)\s*\(")
# A pure cross-sheet carry: optionally-quoted sheet name, '!', one absolute-or-relative cell ref.
PURE_CARRY = re.compile(r"^'?[^!'\[\]]+'?!\$?[A-Z]{1,3}\$?\d+$")
SAME_SHEET_REF = re.compile(r"^\$?[A-Z]{1,3}\$?\d+$")


def classify(formula: str) -> str:
    """Classify a formula string into the brief's §4.3 taxonomy (extended)."""
    f = (formula or "").strip()
    if not f:
        return "shared-dependent (no body)"
    if PURE_CARRY.match(f):
        return "pure cross-sheet carry-forward"
    if SAME_SHEET_REF.match(f):
        return "same-sheet cell ref"
    h = FUNC_HEAD.match(f)
    head = h.group(1) if h else None
    if head == "IFERROR":
        return "IFERROR wrapper"
    if head == "SUM":
        return "SUM row/col total"
    if head == "COUNTIF" or head == "COUNTIFS":
        return "COUNTIF tally"
    if head == "IF":
        return "IF conditional carry"
    if head in ("SUMIF", "SUMIFS"):
        return "SUMIF conditional total"
    if head in ("VLOOKUP", "HLOOKUP", "INDEX", "MATCH", "XLOOKUP"):
        return "lookup"
    if head in ("TEXT", "CONCATENATE", "LEFT", "RIGHT", "MID", "TRIM"):
        return "text formatting"
    if head:
        return "other function: " + head
    if re.search(r"[-+*/]", f):
        return "bare arithmetic"
    return "other/ref"


def dv_vocab(node):
    """Extract a data-validation's list vocabulary if it is a literal one."""
    f1 = node.find(_q("formula1"))
    txt = (f1.text or "").strip() if f1 is not None else ""
    if not txt:
        return None, ""
    # A literal list looks like "Yes,No" (quoted, comma separated)
    if txt.startswith('"') and txt.endswith('"') and len(txt) > 2:
        return [v.strip() for v in txt[1:-1].split(",")], txt
    return None, txt


def probe(path):
    raw = open(path, "rb").read()
    z = zipfile.ZipFile(path)
    ss = shared_strings(z)
    res = {
        "file": os.path.basename(path),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "sheets": [],
        "defined_names": defined_names(z),
        "workbook_protection": "workbookProtection" in z.read("xl/workbook.xml").decode("utf8", "ignore"),
    }
    tot = Counter()
    fclass = Counter()
    dv_all = []
    label_instances = 0
    distinct_labels = set()
    formulas_dump = []

    for name, sid, state, part in sheet_map(z):
        if part not in z.namelist():
            res["sheets"].append({"name": name, "MISSING_PART": part})
            continue
        root = etree.fromstring(z.read(part))

        f_elems = list(root.iter(_q("f")))
        n_f = len(f_elems)
        n_shared_master = sum(1 for f in f_elems if f.get("t") == "shared" and f.get("ref"))
        n_shared_dep = sum(1 for f in f_elems if f.get("t") == "shared" and not f.get("ref"))
        n_array = sum(1 for f in f_elems if f.get("t") == "array")
        n_body = sum(1 for f in f_elems if (f.text or "").strip())
        n_nobody = n_f - n_body

        xsheet = 0
        for f in f_elems:
            body = (f.text or "").strip()
            k = classify(body)
            fclass[k] += 1
            if "!" in body:
                xsheet += 1
            if body:
                formulas_dump.append((name, body))

        cells = list(root.iter(_q("c")))
        n_cells = len(cells)

        # labelled fields: shared-string cells whose text is a real label
        sheet_labels = 0
        for c in cells:
            if c.get("t") == "s":
                v = c.find(_q("v"))
                if v is None or v.text is None:
                    continue
                i = int(v.text)
                if i < len(ss):
                    s = " ".join(ss[i].split())
                    if len(s) > 3:
                        sheet_labels += 1
                        distinct_labels.add(s)
        label_instances += sheet_labels

        prot = root.find(_q("sheetProtection"))
        prot_d = None
        if prot is not None:
            prot_d = {k: v for k, v in prot.attrib.items()}

        merges = root.find(_q("mergeCells"))
        merge_list = []
        if merges is not None:
            merge_list = [m.get("ref") for m in merges.iter(_q("mergeCell"))]

        # data validations, incl. the x14 extension list (Excel 2010+)
        dvs = list(root.iter(_q("dataValidation")))
        x14 = [e for e in root.iter() if etree.QName(e).localname == "dataValidation"
               and etree.QName(e).namespace != MAIN]
        sheet_dv = []
        for d in dvs + x14:
            vocab, f1 = dv_vocab(d) if etree.QName(d).namespace == MAIN else (None, "")
            if etree.QName(d).namespace != MAIN:
                f1n = [e for e in d if etree.QName(e).localname == "formula1"]
                if f1n:
                    inner = "".join(f1n[0].itertext()).strip()
                    f1 = inner
                    if inner.startswith('"') and inner.endswith('"'):
                        vocab = [v.strip() for v in inner[1:-1].split(",")]
            sqref = d.get("sqref") or ""
            if not sqref:
                sq = [e for e in d.iter() if etree.QName(e).localname == "sqref"]
                if sq:
                    sqref = (sq[0].text or "").strip()
            rec = {
                "sheet": name,
                "type": d.get("type"),
                "sqref": sqref,
                "formula1": f1[:180],
                "literal_vocab": vocab,
                "allowBlank": d.get("allowBlank"),
                "ns": "x14" if etree.QName(d).namespace != MAIN else "main",
            }
            sheet_dv.append(rec)
            dv_all.append(rec)

        res["sheets"].append({
            "name": name, "state": state, "cells": n_cells,
            "formulas": n_f, "formula_with_body": n_body, "formula_no_body": n_nobody,
            "shared_master": n_shared_master, "shared_dependent": n_shared_dep,
            "array": n_array, "cross_sheet": xsheet,
            "protected": prot_d is not None,
            "protection": prot_d,
            "merged_ranges": len(merge_list),
            "merged_sample": merge_list[:6],
            "data_validations": len(sheet_dv),
            "labels": sheet_labels,
        })
        tot["cells"] += n_cells
        tot["formulas"] += n_f
        tot["formula_with_body"] += n_body
        tot["formula_no_body"] += n_nobody
        tot["cross_sheet"] += xsheet
        tot["merged"] += len(merge_list)
        tot["dv"] += len(sheet_dv)
        tot["protected"] += 1 if prot_d is not None else 0

    res["totals"] = dict(tot)
    res["n_sheets"] = len([s for s in res["sheets"] if "MISSING_PART" not in s])
    res["formula_classes"] = dict(fclass.most_common())
    res["label_instances"] = label_instances
    res["distinct_labels"] = len(distinct_labels)
    res["shared_strings"] = len(ss)
    res["dv_list_with_literal_vocab"] = [d for d in dv_all if d["literal_vocab"]]
    res["dv_list_type"] = [d for d in dv_all if d["type"] == "list"]
    res["dv_by_type"] = dict(Counter(d["type"] for d in dv_all))
    res["_dv_all"] = dv_all
    res["_formulas"] = formulas_dump
    res["_labels"] = sorted(distinct_labels)
    return res


def main():
    args = sys.argv[1:]
    files = []
    for a in args:
        if os.path.isdir(a):
            files += [os.path.join(a, f) for f in sorted(os.listdir(a)) if f.endswith(".xlsx")]
        else:
            files.append(a)
    allres = []
    for p in files:
        try:
            r = probe(p)
        except Exception as e:
            print(f"!! {os.path.basename(p)}: {type(e).__name__}: {e}")
            continue
        allres.append(r)
        t = r["totals"]
        print("=" * 100)
        print(f"{r['file']}")
        print(f"  sha256={r['sha256'][:16]}…  bytes={r['bytes']:,}")
        print(f"  sheets={r['n_sheets']}  cells={t.get('cells',0):,}  "
              f"formulas={t.get('formulas',0)}  (with body {t.get('formula_with_body',0)}, "
              f"shared-dependent/no-body {t.get('formula_no_body',0)})")
        print(f"  cross-sheet={t.get('cross_sheet',0)}  merged={t.get('merged',0)}  "
              f"dataValidations={t.get('dv',0)}  protectedSheets={t.get('protected',0)}/{r['n_sheets']}")
        print(f"  labels: {r['label_instances']} instances / {r['distinct_labels']} distinct   "
              f"sharedStrings={r['shared_strings']}   definedNames={len(r['defined_names'])}")
        print(f"  dv by type: {r['dv_by_type']}   list-type={len(r['dv_list_type'])}   "
              f"with literal vocabulary={len(r['dv_list_with_literal_vocab'])}")
        print("  formula classes:")
        for k, v in r["formula_classes"].items():
            pct = 100.0 * v / max(1, t.get("formulas", 1))
            print(f"      {v:5}  ({pct:4.1f}%)  {k}")
        print("  per-sheet:")
        for s in r["sheets"]:
            if "MISSING_PART" in s:
                print(f"      {s['name'][:38]:40} MISSING PART {s['MISSING_PART']}")
                continue
            print(f"      {s['name'][:38]:40} cells={s['cells']:6} f={s['formulas']:5} "
                  f"xs={s['cross_sheet']:5} prot={str(s['protected']):5} dv={s['data_validations']:3} "
                  f"merged={s['merged_ranges']:4} labels={s['labels']:5}")
        if r["defined_names"]:
            print("  defined names:")
            for d in r["defined_names"][:15]:
                print(f"      {d['name'][:40]:42} -> {d['value'][:70]}")
        if r["dv_list_with_literal_vocab"]:
            print("  list validations WITH a literal vocabulary:")
            for d in r["dv_list_with_literal_vocab"][:20]:
                print(f"      [{d['sheet'][:20]:22}] {d['sqref'][:28]:30} {d['formula1'][:80]}")
        other_dv = [d for d in r["_dv_all"] if not d["literal_vocab"]]
        if other_dv:
            print(f"  other validations ({len(other_dv)}), first 12:")
            for d in other_dv[:12]:
                print(f"      [{d['sheet'][:20]:22}] type={str(d['type'])[:12]:13} "
                      f"{d['sqref'][:24]:26} f1={d['formula1'][:60]}")

    out = "/Users/abishaikc/Gift/research/scripts/probe_out.json"
    with open(out, "w") as fh:
        json.dump([{k: v for k, v in r.items() if not k.startswith("_")} for r in allres], fh, indent=1)
    print("\nwrote", out)


if __name__ == "__main__":
    main()
