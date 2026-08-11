#!/usr/bin/env python
"""
predicate_harvest.py — derive EXECUTABLE predicates from a BLANK IFSCA template,
with zero model involvement. This is layer L1 of the architecture, run for real.

Every predicate emitted here is machine-derived from the workbook's own OOXML:
  * cross-sheet carry      -> equality check   (target cell == source cell)
  * SUM(range)             -> sum identity     (target == sum of range)
  * COUNTIF(range,crit)    -> tally identity
  * IFERROR(x, y)          -> equality-or-blank (weaker; recorded, flagged)
  * dataValidation list    -> membership check (value in resolved vocabulary)
  * dataValidation date    -> date-bound check
  * dataValidation whole   -> integer-bound check
  * dataValidation decimal -> numeric-bound check
  * dataValidation custom  -> conditional-required check (formula is the condition)

Run: /Users/abishaikc/Gift/.venv/bin/python predicate_harvest.py <dir-or-files>
"""
import sys, os, re, json, zipfile, hashlib
from collections import Counter, defaultdict
from lxml import etree

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
M = "{%s}" % MAIN
R = "{%s}" % REL

CELL_RE = re.compile(r"^\$?([A-Z]{1,3})\$?(\d+)$")
RANGE_REF = re.compile(r"^(?:'([^']+)'|([A-Za-z0-9_. ]+))!(\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)$")
PURE_CARRY = re.compile(r"^'?[^!'\[\]]+'?!\$?[A-Z]{1,3}\$?\d+$")
SUM_RE = re.compile(r"^SUM\((.+)\)$", re.S)
COUNTIF_RE = re.compile(r"^COUNTIFS?\((.+)\)$", re.S)
IFERROR_RE = re.compile(r"^IFERROR\((.+)\)$", re.S)


def sheets(z):
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rels}
    out = []
    for s in wb.iter(M + "sheet"):
        t = rid2t.get(s.get(R + "id"), "")
        part = t if t.startswith("xl/") else ("xl/" + t.lstrip("/"))
        out.append((s.get("name"), part))
    return out


def defined_names(z):
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    return {dn.get("name"): (dn.text or "") for dn in wb.iter(M + "definedName")
            if not (dn.get("name") or "").startswith("_xlnm")}


def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    root = etree.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(M + "t")) for si in root.iter(M + "si")]


def load_values(z, ss):
    """cell text values per sheet, so we can RESOLVE dropdown ranges to a real vocabulary."""
    vals = {}
    for name, part in sheets(z):
        if part not in z.namelist():
            continue
        root = etree.fromstring(z.read(part))
        d = {}
        for c in root.iter(M + "c"):
            ref = c.get("r")
            v = c.find(M + "v")
            isn = c.find(M + "is")
            if c.get("t") == "s" and v is not None and v.text is not None:
                i = int(v.text)
                if i < len(ss):
                    d[ref] = ss[i]
            elif isn is not None:
                d[ref] = "".join(t.text or "" for t in isn.iter(M + "t"))
            elif v is not None and v.text is not None:
                d[ref] = v.text
        vals[name] = d
    return vals


def col_to_n(c):
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def n_to_col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def expand(ref):
    """'A1:A5' -> ['A1','A2',...]. Single cell -> [cell]."""
    ref = ref.replace("$", "")
    if ":" not in ref:
        return [ref]
    a, b = ref.split(":")
    ma, mb = CELL_RE.match(a), CELL_RE.match(b)
    if not (ma and mb):
        return []
    c1, r1 = col_to_n(ma.group(1)), int(ma.group(2))
    c2, r2 = col_to_n(mb.group(1)), int(mb.group(2))
    if (c2 - c1 + 1) * (r2 - r1 + 1) > 5000:
        return []
    return [f"{n_to_col(c)}{r}" for c in range(min(c1, c2), max(c1, c2) + 1)
            for r in range(min(r1, r2), max(r1, r2) + 1)]


def resolve_vocab(f1, dn, vals, cur_sheet):
    """Resolve a list-validation formula1 into an actual vocabulary."""
    f1 = (f1 or "").strip()
    if not f1:
        return None, "empty"
    if f1.startswith('"') and f1.endswith('"'):
        return [v.strip() for v in f1[1:-1].split(",")], "literal"
    target = dn.get(f1, f1)          # defined name -> its refers-to
    kind = "named-range" if f1 in dn else "range"
    m = RANGE_REF.match(target.strip())
    if m:
        sheet = m.group(1) or m.group(2)
        rng = m.group(3)
    elif CELL_RE.match(target.strip().split(":")[0].replace("$", "")):
        sheet, rng = cur_sheet, target.strip()
    else:
        return None, "unresolved:" + target[:40]
    sv = vals.get(sheet)
    if sv is None:
        return None, "sheet-missing:" + str(sheet)
    vocab = [sv[c] for c in expand(rng) if c in sv and str(sv[c]).strip()]
    return (vocab or None), kind


def dv_nodes(root):
    out = []
    for e in root.iter():
        if etree.QName(e).localname != "dataValidation":
            continue
        ns = etree.QName(e).namespace
        f1 = ""
        for ch in e:
            if etree.QName(ch).localname == "formula1":
                f1 = "".join(ch.itertext()).strip()
        sq = e.get("sqref") or ""
        if not sq:
            for ch in e.iter():
                if etree.QName(ch).localname == "sqref":
                    sq = (ch.text or "").strip()
        out.append((e.get("type"), sq, f1, "main" if ns == MAIN else "x14"))
    return out


def harvest(path):
    raw = open(path, "rb").read()
    z = zipfile.ZipFile(path)
    ss = shared_strings(z)
    dn = defined_names(z)
    vals = load_values(z, ss)
    preds = []
    weak = []
    for name, part in sheets(z):
        if part not in z.namelist():
            continue
        root = etree.fromstring(z.read(part))

        # ---- formula-derived predicates
        for c in root.iter(M + "c"):
            f = c.find(M + "f")
            if f is None:
                continue
            body = (f.text or "").strip()
            ref = c.get("r")
            if not body:
                continue
            if PURE_CARRY.match(body):
                preds.append({"kind": "cross_sheet_equality", "sheet": name, "cell": ref,
                              "expr": body, "checks": f"{name}!{ref} == {body}"})
            elif SUM_RE.match(body):
                preds.append({"kind": "sum_identity", "sheet": name, "cell": ref,
                              "expr": body, "checks": f"{name}!{ref} == {body}"})
            elif COUNTIF_RE.match(body):
                preds.append({"kind": "tally_identity", "sheet": name, "cell": ref,
                              "expr": body, "checks": f"{name}!{ref} == {body}"})
            elif IFERROR_RE.match(body):
                weak.append({"kind": "iferror_wrapper", "sheet": name, "cell": ref, "expr": body})
            elif CELL_RE.match(body.replace("$", "")):
                preds.append({"kind": "same_sheet_equality", "sheet": name, "cell": ref,
                              "expr": body, "checks": f"{name}!{ref} == {name}!{body}"})
            elif re.match(r"^IF\(", body):
                weak.append({"kind": "if_conditional_carry", "sheet": name, "cell": ref, "expr": body})
            else:
                weak.append({"kind": "other_formula", "sheet": name, "cell": ref, "expr": body})

        # ---- data-validation-derived predicates
        for typ, sq, f1, ns in dv_nodes(root):
            cells = []
            for part_ref in sq.split():
                cells += expand(part_ref)
            n = len(cells) or 1
            if typ == "list":
                vocab, how = resolve_vocab(f1, dn, vals, name)
                if vocab:
                    preds.append({"kind": "membership", "sheet": name, "sqref": sq,
                                  "n_cells": n, "vocab": vocab, "vocab_size": len(vocab),
                                  "source": how, "formula1": f1})
                else:
                    weak.append({"kind": "list_unresolved", "sheet": name, "sqref": sq,
                                 "formula1": f1, "why": how})
            elif typ == "date":
                preds.append({"kind": "date_bound", "sheet": name, "sqref": sq,
                              "n_cells": n, "formula1": f1})
            elif typ == "whole":
                preds.append({"kind": "integer_bound", "sheet": name, "sqref": sq,
                              "n_cells": n, "formula1": f1})
            elif typ == "decimal":
                preds.append({"kind": "numeric_bound", "sheet": name, "sqref": sq,
                              "n_cells": n, "formula1": f1})
            elif typ == "custom":
                preds.append({"kind": "conditional_required", "sheet": name, "sqref": sq,
                              "n_cells": n, "formula1": f1})
            elif typ in (None, "", "textLength"):
                weak.append({"kind": "dv_no_type", "sheet": name, "sqref": sq, "formula1": f1})
    return {
        "file": os.path.basename(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "predicates": preds,
        "weak": weak,
    }


def main():
    args = sys.argv[1:]
    files = []
    for a in args:
        if os.path.isdir(a):
            files += [os.path.join(a, f) for f in sorted(os.listdir(a)) if f.endswith(".xlsx")]
        else:
            files.append(a)
    grand = Counter()
    rows = []
    dump = {}
    for p in files:
        try:
            r = harvest(p)
        except Exception as e:
            print(f"!! {os.path.basename(p)}: {type(e).__name__}: {e}")
            continue
        k = Counter(x["kind"] for x in r["predicates"])
        w = Counter(x["kind"] for x in r["weak"])
        cellcov = sum(x.get("n_cells", 1) for x in r["predicates"])
        rows.append((r["file"], sum(k.values()), cellcov, dict(k), dict(w)))
        grand.update(k)
        dump[r["file"]] = r
        print("=" * 100)
        print(r["file"])
        print(f"  MECHANICALLY DERIVED PREDICATES: {sum(k.values())}   "
              f"(covering {cellcov} cell-slots)")
        for kk, vv in k.most_common():
            print(f"      {vv:5}  {kk}")
        if w:
            print(f"  not directly executable ({sum(w.values())}):")
            for kk, vv in w.most_common():
                print(f"      {vv:5}  {kk}")
        mem = [x for x in r["predicates"] if x["kind"] == "membership"]
        if mem:
            print(f"  resolved vocabularies ({len(mem)} membership predicates):")
            for x in mem[:14]:
                print(f"      [{x['sheet'][:18]:20}] {x['sqref'][:20]:22} n={x['n_cells']:4} "
                      f"|V|={x['vocab_size']:3} ({x['source']}) {str(x['vocab'][:5])[:78]}")
            if len(mem) > 14:
                print(f"      ... +{len(mem)-14} more")

    print("\n" + "=" * 100)
    print("GRAND TOTAL across all workbooks — predicates derivable with ZERO model involvement")
    for kk, vv in grand.most_common():
        print(f"   {vv:6}  {kk}")
    print(f"   {sum(grand.values()):6}  TOTAL")
    out = "/Users/abishaikc/Gift/research/scripts/predicates.json"
    with open(out, "w") as fh:
        json.dump(dump, fh, indent=1)
    print("\nwrote", out)


if __name__ == "__main__":
    main()
