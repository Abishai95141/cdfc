#!/usr/bin/env python
"""
true_coverage.py — compute the COVERAGE FRACTION against an honest denominator.

Why this file exists: the first attempt used
    denominator = (cells in the predicate graph) U (cells carrying a validation)
and reported 99.2% coverage. That number is circular — the denominator was
defined as "cells that already have a check", so it cannot come out low. It is
the degenerate-baseline failure (L4 test 2) committed by the measurement itself.

The honest denominator is THE FIELD SURFACE: every cell the filer can actually
type into. In a protected sheet that is exactly the set of UNLOCKED cells, which
is recoverable from styles.xml (cellXfs -> <protection locked="0"/>), because
Excel sheet protection locks every cell by default and the template author
unlocks precisely the input cells.

Run: /Users/abishaikc/Gift/.venv/bin/python true_coverage.py
"""
import zipfile, re, sys
from collections import Counter
from lxml import etree

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
M = "{%s}" % MAIN
R = "{%s}" % REL
DIR = "/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/"
P = DIR + "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"

sys.path.insert(0, "/Users/abishaikc/Gift/research/scripts")
from l4_mutation_harness import build_graph, dv_input_cells, expand  # noqa: E402


def unlocked_style_ids(z):
    """Style indices whose xf declares locked=0 -> an editable cell."""
    root = etree.fromstring(z.read("xl/styles.xml"))
    cellxfs = root.find(M + "cellXfs")
    out = set()
    if cellxfs is None:
        return out
    for i, xf in enumerate(cellxfs.findall(M + "xf")):
        pr = xf.find(M + "protection")
        if pr is not None and pr.get("locked") == "0":
            out.add(str(i))
    return out


def main():
    z = zipfile.ZipFile(P)
    unlocked = unlocked_style_ids(z)
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rl = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rl}

    field_surface = set()      # unlocked, non-formula cells = filer input
    formula_cells = set()
    all_cells = 0
    protected_sheets = set()
    per_sheet = Counter()
    for s in wb.iter(M + "sheet"):
        name = s.get("name")
        t = rid2t.get(s.get(R + "id"), "")
        part = t if t.startswith("xl/") else "xl/" + t.lstrip("/")
        if part not in z.namelist():
            continue
        root = etree.fromstring(z.read(part))
        if root.find(M + "sheetProtection") is not None:
            protected_sheets.add(name)
        for c in root.iter(M + "c"):
            all_cells += 1
            ref = c.get("r")
            has_f = c.find(M + "f") is not None
            if has_f:
                formula_cells.add((name, ref))
                continue
            if (c.get("s") or "0") in unlocked:
                field_surface.add((name, ref))
                per_sheet[name] += 1

    preds = build_graph()
    graph = {p["target"] for p in preds} | {s for p in preds for s in p["srcs"]}
    dv = dv_input_cells()

    denom = field_surface
    arith = graph & denom
    dvc = dv & denom
    union = (graph | dv) & denom

    print("=" * 92)
    print("COVERAGE FRACTION AGAINST AN HONEST DENOMINATOR — IFSCA FME workbook")
    print("=" * 92)
    print(f"  unlocked style ids in styles.xml        : {len(unlocked)}")
    print(f"  protected sheets                        : {len(protected_sheets)} of 10")
    print(f"  cells present in the workbook           : {all_cells}")
    print(f"  formula cells (not filer-editable)      : {len(formula_cells)}")
    print()
    print(f"  THE FIELD SURFACE (unlocked, non-formula): {len(denom)} cells   <- the denominator")
    for k, v in per_sheet.most_common():
        print(f"        {k[:30]:32} {v:5}")
    print()
    print("  WHAT THE MECHANICALLY-DERIVED PREDICATE SET COVERS:")
    print(f"     arithmetic predicates (227)          : {len(arith):5}  "
          f"({100*len(arith)/max(len(denom),1):5.1f}% of field surface)")
    print(f"     validation predicates (53)           : {len(dvc):5}  "
          f"({100*len(dvc)/max(len(denom),1):5.1f}%)")
    print(f"     UNION (280 predicates)               : {len(union):5}  "
          f"({100*len(union)/max(len(denom),1):5.1f}%)")
    print(f"     UNCHECKED residue                    : {len(denom-union):5}  "
          f"({100*len(denom-union)/max(len(denom),1):5.1f}%)")
    print()
    print("  This is the number the product puts at the top of the report, and it is")
    print("  computed, not asserted. The residue is the Unchecked panel's contents.")

    ex = sorted(denom - union)[:10]
    if ex:
        print("\n  sample of the UNCHECKED residue (no predicate reads these cells):")
        for sh, cc in ex:
            print(f"     {sh[:26]:28}!{cc}")


if __name__ == "__main__":
    main()
