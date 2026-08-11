import zipfile
from lxml import etree
P="/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
M="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
z=zipfile.ZipFile(P)
wb=etree.fromstring(z.read("xl/workbook.xml")); rels=etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rmap={r.get("Id"):r.get("Target") for r in rels}
sh={s.get("name"):(lambda t: t if t.startswith("xl/") else "xl/"+t.lstrip("/"))(rmap[s.get(R+"id")]) for s in wb.iter(M+"sheet")}
ss=[]
if "xl/sharedStrings.xml" in z.namelist():
    sst=etree.fromstring(z.read("xl/sharedStrings.xml"))
    ss=["".join(t.text or "" for t in si.iter(M+"t")) for si in sst.iter(M+"si")]
def dump(sheet, refs):
    root=etree.fromstring(z.read(sh[sheet]))
    for c in root.iter(M+"c"):
        if c.get("r") in refs:
            f=c.find(M+"f"); v=c.find(M+"v")
            val=v.text if v is not None else None
            if c.get("t")=="s" and val is not None: val=ss[int(val)]
            print("  %s!%-6s f=%s  v=%r" % (sheet, c.get("r"), (f.text if f is not None else None), val))
print("=== '1. Introduction' D14:D18, C14:C18 ===")
dump("1. Introduction", {"C14","D14","C15","D15","C16","D16","C17","D17","C18","D18"})
print("\n=== Dropdown sheet, all cells ===")
root=etree.fromstring(z.read(sh["Dropdown"]))
for c in root.iter(M+"c"):
    v=c.find(M+"v"); val=v.text if v is not None else None
    if c.get("t")=="s" and val is not None: val=ss[int(val)]
    print("   %-6s %r" % (c.get("r"), val))
