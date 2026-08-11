import zipfile, re, sys
from lxml import etree

P = "/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

z = zipfile.ZipFile(P)
# workbook -> sheet name/rId/state
wb = etree.fromstring(z.read("xl/workbook.xml"))
rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rmap = {r.get("Id"): r.get("Target") for r in rels}
sheets = []
for s in wb.iter(M+"sheet"):
    rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    tgt = rmap[rid]
    if not tgt.startswith("xl/"): tgt = "xl/"+tgt.lstrip("/")
    sheets.append((s.get("name"), s.get("state","visible"), tgt))

# styles: unlocked xf ids
st = etree.fromstring(z.read("xl/styles.xml"))
cellXfs = st.find(M+"cellXfs")
unlocked = set()
for i, xf in enumerate(cellXfs.findall(M+"xf")):
    prot = xf.find(M+"protection")
    if prot is not None and prot.get("locked") == "0":
        unlocked.add(i)

tot_cells=0; tot_formula=0; tot_unlocked=0; unlocked_formula=0; unlocked_nonformula=0
per_sheet={}
formula_cells=[]   # (sheet, ref, unlocked?, has_cached_value?)
for name, state, tgt in sheets:
    root = etree.fromstring(z.read(tgt))
    prot = root.find(M+"sheetProtection")
    nf=0; nu=0; nuf=0; nunf=0; nc=0; cached=0
    for c in root.iter(M+"c"):
        nc+=1
        s_idx = int(c.get("s") or 0)
        f = c.find(M+"f"); v = c.find(M+"v")
        isf = f is not None
        isu = s_idx in unlocked
        if isf:
            nf+=1
            formula_cells.append((name, c.get("r"), isu, v is not None))
            if v is not None: cached+=1
        if isu:
            nu+=1
            if isf: nuf+=1
            else: nunf+=1
    per_sheet[name]=dict(state=state, protected=prot is not None, cells=nc, formula=nf,
                         unlocked=nu, unlocked_formula=nuf, field_surface=nunf, cached=cached)
    tot_cells+=nc; tot_formula+=nf; tot_unlocked+=nu; unlocked_formula+=nuf; unlocked_nonformula+=nunf

print("TOTALS cells=%d formula=%d unlocked=%d unlocked&formula=%d unlocked&nonformula(field surface)=%d"
      % (tot_cells, tot_formula, tot_unlocked, unlocked_formula, unlocked_nonformula))
print("formula cells carrying a cached <v>: %d of %d" % (sum(1 for x in formula_cells if x[3]), len(formula_cells)))
print()
for k,v in per_sheet.items():
    print("%-24s state=%-7s prot=%-5s cells=%5d formula=%4d cached=%4d unlocked=%5d u&f=%3d FIELD=%5d"
          % (k, v["state"], v["protected"], v["cells"], v["formula"], v["cached"], v["unlocked"], v["unlocked_formula"], v["field_surface"]))
print()
print("UNLOCKED FORMULA CELLS (the overwritable-formula set):")
for s,r,u,c in formula_cells:
    if u: print("   %s!%s cached=%s" % (s,r,c))
