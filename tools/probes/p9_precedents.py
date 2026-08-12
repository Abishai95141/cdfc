import zipfile, re
from lxml import etree
from openpyxl.formula.translate import Translator
P="fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
M="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
z=zipfile.ZipFile(P)
wb=etree.fromstring(z.read("xl/workbook.xml")); rels=etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rmap={r.get("Id"):r.get("Target") for r in rels}
sheets=[(s.get("name"), (lambda t: t if t.startswith("xl/") else "xl/"+t.lstrip("/"))(rmap[s.get(R+"id")])) for s in wb.iter(M+"sheet")]
names=[s[0] for s in sheets]
st=etree.fromstring(z.read("xl/styles.xml")); cellXfs=st.find(M+"cellXfs")
unlocked={i for i,xf in enumerate(cellXfs.findall(M+"xf"))
          if xf.find(M+"protection") is not None and xf.find(M+"protection").get("locked")=="0"}
field=set(); formulas={}; masters={}
for name,tgt in sheets:
    root=etree.fromstring(z.read(tgt))
    for c in root.iter(M+"c"):
        f=c.find(M+"f"); s_idx=int(c.get("s") or 0)
        if f is None:
            if s_idx in unlocked: field.add((name,c.get("r")))
            continue
        formulas[(name,c.get("r"))]=(f.get("t"), f.get("si"), f.text or "", f.get("ref"))
        if f.get("t")=="shared" and f.text: masters[(name,f.get("si"))]=(c.get("r"), f.text)
# materialise
mat={}
for (sh,ref),(t,si,txt,rng) in formulas.items():
    if txt: mat[(sh,ref)]=txt
    elif t=="shared" and (sh,si) in masters:
        anchor, mtxt = masters[(sh,si)]
        mat[(sh,ref)]=Translator("="+mtxt, origin=anchor).translate_formula(ref)[1:]
    else: mat[(sh,ref)]=None
print("materialised:", sum(1 for v in mat.values() if v), "of", len(mat))
print("sample  '3. Portfolio'!O4 =", mat.get(("3. Portfolio","O4")))
REF=re.compile(r"(?:'([^']+)'!|([A-Za-z0-9_.]+)!)?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?")
def cn(s):
    n=0
    for ch in s: n=n*26+ord(ch)-64
    return n
def nc(n):
    s=""
    while n: n,r=divmod(n-1,26); s=chr(65+r)+s
    return s
touched=set()
for (sh,ref),txt in mat.items():
    if not txt: continue
    for m in REF.finditer(txt):
        sname=(m.group(1) or m.group(2) or "").strip()
        tsheet = sname if sname in names else sh
        c1,r1,c2,r2=m.group(3),int(m.group(4)),m.group(5),m.group(6)
        rng=[(cc,rr) for cc in range(cn(c1), cn(c2)+1 if c2 else cn(c1)+1)
                     for rr in range(r1, int(r2)+1 if c2 else r1+1)]
        for cc,rr in rng:
            k=(tsheet, nc(cc)+str(rr))
            if k in field: touched.add(k)
from collections import Counter
print("FIELD-SURFACE CELLS FEEDING >=1 TEMPLATE FORMULA (shared dependents row-shifted):", len(touched), "of", len(field))
print(sorted(Counter(s for s,_ in touched).items(), key=lambda x:-x[1]))
