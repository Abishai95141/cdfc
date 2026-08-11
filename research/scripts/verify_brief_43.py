#!/usr/bin/env python
"""
verify_brief_43.py — confirm or correct every number the operator asserts in
RND-BRIEF section 4.3, against the actual FME workbook.

Run: /Users/abishaikc/Gift/.venv/bin/python verify_brief_43.py
"""
import zipfile, re, time, hashlib
from collections import Counter
from lxml import etree

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
M = "{%s}" % MAIN
R = "{%s}" % REL
P = ("/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/"
     "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")

t0 = time.time()
raw = open(P, "rb").read()
z = zipfile.ZipFile(P)
wb = etree.fromstring(z.read("xl/workbook.xml"))
rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rid2t = {r.get("Id"): r.get("Target") for r in rels}
sheets = []
for s in wb.iter(M + "sheet"):
    t = rid2t.get(s.get(R + "id"), "")
    sheets.append((s.get("name"), t if t.startswith("xl/") else "xl/" + t.lstrip("/")))

ssroot = etree.fromstring(z.read("xl/sharedStrings.xml"))
ss = ["".join(t.text or "" for t in si.iter(M + "t")) for si in ssroot.iter(M + "si")]

cells = fbody = fall = merged = 0
dv_main = dv_x14 = 0
dv_types = Counter()
prot = []
labels = []
fclass = Counter()
numeric_fmt = 0

PURE = re.compile(r"^'?[^!'\[\]]+'?!\$?[A-Z]{1,3}\$?\d+$")
for name, part in sheets:
    if part not in z.namelist():
        continue
    root = etree.fromstring(z.read(part))
    cells += len(list(root.iter(M + "c")))
    fs = list(root.iter(M + "f"))
    fall += len(fs)
    for f in fs:
        b = (f.text or "").strip()
        if not b:
            continue
        fbody += 1
        if PURE.match(b):
            fclass["pure cross-sheet carry-forward"] += 1
        elif b.startswith("IFERROR"):
            fclass["IFERROR wrapper"] += 1
        elif b.startswith("SUM("):
            fclass["SUM row/col total"] += 1
        elif b.startswith("IF("):
            fclass["IF conditional carry"] += 1
        elif b.startswith("COUNTIF"):
            fclass["COUNTIF tally"] += 1
        else:
            fclass["other/ref"] += 1
    mc = root.find(M + "mergeCells")
    if mc is not None:
        merged += len(list(mc.iter(M + "mergeCell")))
    sp = root.find(M + "sheetProtection")
    if sp is not None:
        prot.append((name, dict(sp.attrib)))
    for e in root.iter():
        if etree.QName(e).localname == "dataValidation":
            if etree.QName(e).namespace == MAIN:
                dv_main += 1
            else:
                dv_x14 += 1
            dv_types[e.get("type")] += 1
    for c in root.iter(M + "c"):
        if c.get("t") == "s":
            v = c.find(M + "v")
            if v is not None and v.text is not None:
                i = int(v.text)
                if i < len(ss):
                    labels.append(" ".join(ss[i].split()))

elapsed = time.time() - t0

# field-shape counts, from the label strings
lab_l = [l.lower() for l in labels]
whether = sum(1 for l in lab_l if l.startswith("whether"))
datey = sum(1 for l in lab_l if "date" in l)
amount = sum(1 for l in lab_l if any(k in l for k in
            ("amount", "value", "nav", "aum", "number of", "no. of", "corpus",
             "fee", "(in ", "usd", "inr", "%", "percent")))

print("=" * 92)
print("BRIEF §4.3 — CLAIM-BY-CLAIM VERIFICATION")
print("=" * 92)
print(f"file sha256          : {hashlib.sha256(raw).hexdigest()}")
print(f"parse wall-clock     : {elapsed*1000:.0f} ms  (lxml, single process, cold)")
print()
rows = [
    ("10 sheets",                 len(sheets), 10),
    ("6,757 cells",               cells, 6757),
    ("494 distinct strings",      len(ss), 494),
    ("854 label instances",       len(labels), 854),
    ("294 formulas",              fbody, 294),
    ("35 data validations",       dv_main + dv_x14, 35),
    ("9 of 10 sheets protected",  len(prot), 9),
]
for claim, actual, asserted in rows:
    verdict = "CONFIRMED" if actual == asserted else f"CORRECTED -> {actual}"
    print(f"  {claim:28} asserted={asserted:6}  actual={actual:6}  {verdict}")
print()
print(f"  formula ELEMENTS (all <f>)   : {fall}")
print(f"    with a formula body        : {fbody}   <- this is the brief's '294'")
print(f"    shared-formula dependents  : {fall - fbody}   <- NOT counted by the brief")
print()
print("  formula classification (of the 294 with bodies):")
for k, v in fclass.most_common():
    print(f"      {v:4}  ({100*v/fbody:4.1f}% of 294)  {k}")
print()
print(f"  dataValidation split         : main-namespace={dv_main}  x14-extension={dv_x14}  total={dv_main+dv_x14}")
print(f"  dataValidation by type       : {dict(dv_types)}")
print()
print("  field shape (label-string heuristic, NOT a strict count):")
print(f"      labels starting 'Whether' : {whether}   (brief asserts 16 yes/no)")
print(f"      labels containing 'date'  : {datey}   (brief asserts 15 dates)")
print(f"      labels matching amount/num: {amount}   (brief asserts 84 numeric/amount)")
print()
print("  sheet protection detail:")
for name, attrs in prot:
    keys = {k: v for k, v in attrs.items() if k in
            ("algorithmName", "hashValue", "spinCount", "sheet", "objects", "scenarios")}
    has_pw = "hashValue" in attrs
    print(f"      {name[:26]:28} password-protected={has_pw}  algo={attrs.get('algorithmName','-')}")
