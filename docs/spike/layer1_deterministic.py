"""Layer 1 — DETERMINISTIC. No model touches this file.

Two extractions, both from declared structure:
  * provisions  : regulation text -> AKN-style eIds with exact character spans
  * fields      : the template's OWN declarations -> type, vocabulary, format
"""
import json, re, zipfile
from pathlib import Path
from lxml import etree

TXT = Path("regs.txt").read_text()

# --- the segmenter. Anchored on a numbered regulation followed by a sub-regulation. ---------
REG = re.compile(r'(?m)^(\d{1,3})\.\s*\((\d+)\)')
PROVISO = re.compile(r'Provided that\b')

def provisions():
    out, hits = [], list(REG.finditer(TXT))
    for i, m in enumerate(hits):
        start = m.start()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(TXT)
        body = TXT[start:end].rstrip()
        eid = f"reg_{m.group(1)}__subreg_{m.group(2)}"
        out.append({"eId": eid, "reg": int(m.group(1)), "span": [start, start + len(body)],
                    "text": body})
        # a proviso is its own addressable unit — it carries an EXCEPTION
        for p in PROVISO.finditer(body):
            out.append({"eId": f"{eid}__proviso_1", "reg": int(m.group(1)),
                        "span": [start + p.start(), start + len(body)],
                        "text": body[p.start():]})
    return out

# --- the template's own declarations --------------------------------------------------------
M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def fields():
    z = zipfile.ZipFile("template.xlsx")
    # sharedStrings is OPTIONAL — openpyxl writes inline strings and omits the part entirely.
    # A reader that assumes it exists raises KeyError on a perfectly ordinary workbook.
    sst = []
    if 'xl/sharedStrings.xml' in z.namelist():
        sst = [''.join(t.text or '' for t in si.iter(M + 't'))
               for si in etree.fromstring(z.read('xl/sharedStrings.xml')).iter(M + 'si')]
    styles = etree.fromstring(z.read('xl/styles.xml'))
    numfmt = {n.get('numFmtId'): n.get('formatCode')
              for n in styles.iter(M + 'numFmt')}
    xfs = list(styles.find(M + 'cellXfs'))
    sheet = etree.fromstring(z.read('xl/worksheets/sheet1.xml'))

    def val(c):
        if c.get('t') == 'inlineStr':
            return ''.join(t.text or '' for t in c.iter(M + 't'))
        v = c.find(M + 'v')
        if v is None: return ''
        if c.get('t') == 's' and v.text and v.text.isdigit(): return sst[int(v.text)]
        return v.text or ''

    labels, out = {}, []
    for c in sheet.iter(M + 'c'):
        ref = c.get('r')
        if ref and ref.startswith('A'): labels[ref[1:]] = val(c)
    # the validated vocabulary, read from the template rather than assumed
    vocab = []
    for dv in sheet.iter(M + 'dataValidation'):
        if dv.get('type') == 'list':
            ls = etree.fromstring(z.read('xl/worksheets/sheet2.xml'))
            vocab = [val(c) for c in ls.iter(M + 'c') if val(c)]
    for c in sheet.iter(M + 'c'):
        ref = c.get('r')
        if not ref or not ref.startswith('B') or ref == 'B1': continue
        s = c.get('s')
        code = ''
        if s is not None and int(s) < len(xfs):
            fid = xfs[int(s)].get('numFmtId')
            code = numfmt.get(fid, {'0': 'General', '14': 'yyyy-mm-dd'}.get(fid, ''))
        kind = ("money" if '$' in (code or '') else
                "date" if 'yy' in (code or '') else
                "count" if code == '0' else "text")
        locked = (c.get('s') is not None and
                  xfs[int(c.get('s'))].find(M + 'protection') is not None and
                  xfs[int(c.get('s'))].find(M + 'protection').get('locked') == '0')
        out.append({"field": ref, "label": labels.get(ref[1:], ''), "format": code,
                    "kind": kind, "vocabulary": vocab if ref == 'B3' else [],
                    "filer_writable": bool(locked)})
    return out

if __name__ == "__main__":
    p, f = provisions(), fields()
    json.dump(p, open("provisions.json", "w"), indent=1)
    json.dump(f, open("fields.json", "w"), indent=1)
    print(f"provisions segmented : {len(p)}")
    for x in p: print(f"   {x['eId']:28} span={x['span']}  {x['text'][:52]!r}")
    print(f"\nfields declared      : {len(f)}")
    for x in f: print(f"   {x['field']:4} {x['kind']:6} {x['label'][:36]:38} vocab={len(x['vocabulary'])}")
