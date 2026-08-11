import zipfile,re
from lxml import etree
from openpyxl.formula.translate import Translator
from collections import Counter
P="/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
M="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"; R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
z=zipfile.ZipFile(P); wb=etree.fromstring(z.read("xl/workbook.xml")); rels=etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rmap={r.get("Id"):r.get("Target") for r in rels}
sheets=[(s.get("name"),(lambda t: t if t.startswith("xl/") else "xl/"+t.lstrip("/"))(rmap[s.get(R+"id")])) for s in wb.iter(M+"sheet")]
mat={}; masters={}; raw={}
for name,tgt in sheets:
    root=etree.fromstring(z.read(tgt))
    for c in root.iter(M+"c"):
        f=c.find(M+"f")
        if f is None: continue
        raw[(name,c.get("r"))]=(f.get("t"),f.get("si"),f.text or "")
        if f.get("t")=="shared" and f.text: masters[(name,f.get("si"))]=(c.get("r"),f.text)
for (sh,ref),(t,si,txt) in raw.items():
    if txt: mat[(sh,ref)]=txt
    else:
        a,m=masters[(sh,si)]; mat[(sh,ref)]=Translator("="+m,origin=a).translate_formula(ref)[1:]
FN=re.compile(r"([A-Za-z_][A-Za-z0-9_.]*)\s*\(")
c=Counter(); cells_by_fn={}
for k,txt in mat.items():
    for fn in set(FN.findall(txt)):
        c[fn]+=1; cells_by_fn.setdefault(fn,[]).append(k)
for fn,n in c.most_common():
    print("%-18s %4d   e.g. %s" % (fn,n,cells_by_fn[fn][0]))
print("\ntotal formula cells:",len(mat))
print("cells using _xlfn.SINGLE:",[k for k in cells_by_fn.get("_xlfn.SINGLE",[])])
