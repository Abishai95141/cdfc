#!/usr/bin/env python
"""
l4_mutation_harness.py — RUN layer L4 test 1 (mutation testing) for real,
on the real IFSCA FME workbook, with zero model involvement.

WHY THIS SCRIPT EXISTS
----------------------
ARCHITECTURE.md L4 test 1 says "seed faults into clean artifacts and measure the
fraction the predicate kills. Tools: mutmut, PIT, Stryker."  That tool list is a
category error, and this script demonstrates the correct shape:

    mutmut mutates PYTHON SOURCE and asks whether YOUR TESTS fail.
    L4 needs to mutate THE FILING (data) and ask whether THE PREDICATES fire.

  mutation-testing concept | classic (mutmut)      | what L4 actually needs
  -------------------------|-----------------------|------------------------
  program under test       | your .py source       | the filed workbook (data)
  test suite               | your pytest suite     | the admitted predicate set
  a mutant                 | source with 1 edit    | a filing with 1 cell perturbed
  "killed"                 | a test fails          | a predicate FAILs

So the L4 harness is ~200 lines of our own code over the cell graph. mutmut is
still useful, but one level up: mutating the predicate IMPLEMENTATIONS to check
the harness itself. It is not the L4-test-1 tool.

WHAT THIS DOES
--------------
1. Derives the field graph from the BLANK template  (L1, deterministic).
2. Synthesises a CLEAN filing that satisfies every derived predicate
   (this is the synthetic clean corpus; §9.2's caveat applies and is printed).
3. Runs every predicate against it   -> expect 0 failures.
4. Seeds single-cell mutations and measures, per predicate class, the kill rate
   MS = |killed| / (|mutants| - |equivalent|).
5. Reports which mutants NO predicate catches — the measured blind spot. That
   residue is exactly what L5 must declare as UNCHECKED rather than pass silently.

Run: /Users/abishaikc/Gift/.venv/bin/python l4_mutation_harness.py
"""
import zipfile, re, random, time, json
from collections import defaultdict, Counter
from lxml import etree

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
M = "{%s}" % MAIN
R = "{%s}" % REL
P = ("/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/"
     "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")

CELL = re.compile(r"^\$?([A-Z]{1,3})\$?(\d+)$")
CARRY = re.compile(r"^'?([^!'\[\]]+)'?!(\$?[A-Z]{1,3}\$?\d+)$")
SUMF = re.compile(r"^SUM\((.+)\)$", re.S)
RANGE = re.compile(r"^(?:'([^']+)'|([A-Za-z0-9_. ]+))!(\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)$")


def cn(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def nc(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def expand(ref):
    ref = ref.replace("$", "")
    if ":" not in ref:
        return [ref]
    a, b = ref.split(":")
    ma, mb = CELL.match(a), CELL.match(b)
    if not (ma and mb):
        return []
    c1, r1 = cn(ma.group(1)), int(ma.group(2))
    c2, r2 = cn(mb.group(1)), int(mb.group(2))
    if (abs(c2 - c1) + 1) * (abs(r2 - r1) + 1) > 5000:
        return []
    return [f"{nc(c)}{r}" for c in range(min(c1, c2), max(c1, c2) + 1)
            for r in range(min(r1, r2), max(r1, r2) + 1)]


# ---------------------------------------------------------------- L1: field graph
def build_graph():
    z = zipfile.ZipFile(P)
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rl = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rl}
    sheets = []
    for s in wb.iter(M + "sheet"):
        t = rid2t.get(s.get(R + "id"), "")
        sheets.append((s.get("name"), t if t.startswith("xl/") else "xl/" + t.lstrip("/")))
    preds = []
    for name, part in sheets:
        if part not in z.namelist():
            continue
        root = etree.fromstring(z.read(part))
        for c in root.iter(M + "c"):
            f = c.find(M + "f")
            if f is None or not (f.text or "").strip():
                continue
            body = f.text.strip()
            tgt = (name, c.get("r"))
            m = CARRY.match(body)
            if m:
                preds.append({"id": f"P{len(preds):04d}", "kind": "cross_sheet_equality",
                              "target": tgt, "srcs": [(m.group(1), m.group(2).replace("$", ""))],
                              "expr": body})
                continue
            m = SUMF.match(body)
            if m:
                srcs = []
                for tok in m.group(1).split(","):
                    tok = tok.strip()
                    rm = RANGE.match(tok)
                    if rm:
                        sh = rm.group(1) or rm.group(2)
                        srcs += [(sh, cc) for cc in expand(rm.group(3))]
                    elif CELL.match(tok.split(":")[0].replace("$", "")):
                        srcs += [(name, cc) for cc in expand(tok)]
                if srcs:
                    preds.append({"id": f"P{len(preds):04d}", "kind": "sum_identity",
                                  "target": tgt, "srcs": srcs, "expr": body})
                continue
            if CELL.match(body.replace("$", "")):
                preds.append({"id": f"P{len(preds):04d}", "kind": "same_sheet_equality",
                              "target": tgt, "srcs": [(name, body.replace("$", ""))],
                              "expr": body})
    return preds


# ------------------------------------------------- synthesise a CLEAN filing
def synth_clean(preds, seed=20260810):
    rng = random.Random(seed)
    derived = {p["target"]: p for p in preds}
    filing = {}

    def val(cell, stack=()):
        if cell in filing:
            return filing[cell]
        if cell in stack:                     # cycle guard
            filing[cell] = 0.0
            return 0.0
        p = derived.get(cell)
        if p is None:                         # a leaf input: choose a value
            v = float(rng.randrange(1000, 999999)) / 100.0
            filing[cell] = v
            return v
        st = stack + (cell,)
        if p["kind"] in ("cross_sheet_equality", "same_sheet_equality"):
            v = val(p["srcs"][0], st)
        else:                                  # sum_identity
            v = round(sum(val(s, st) for s in p["srcs"]), 6)
        filing[cell] = v
        return v

    for p in preds:
        val(p["target"])
    return filing


def dv_input_cells():
    """Every cell under a dataValidation — a filer-populated input cell by construction.
    Namespace-aware: the x14 extension validations are counted too (the naive regex
    r'<dataValidation[ >]' silently misses all 19 of them in this workbook)."""
    z = zipfile.ZipFile(P)
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rl = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rl}
    out = set()
    for s in wb.iter(M + "sheet"):
        t = rid2t.get(s.get(R + "id"), "")
        part = t if t.startswith("xl/") else "xl/" + t.lstrip("/")
        if part not in z.namelist():
            continue
        root = etree.fromstring(z.read(part))
        for e in root.iter():
            if etree.QName(e).localname != "dataValidation":
                continue
            sq = e.get("sqref") or ""
            if not sq:
                for ch in e.iter():
                    if etree.QName(ch).localname == "sqref":
                        sq = (ch.text or "").strip()
            for tok in sq.split():
                for c in expand(tok):
                    out.add((s.get("name"), c))
    return out


# ------------------------------------------------------------- L5: evaluate
TOL = 1e-6


def evaluate(preds, filing):
    fails = []
    for p in preds:
        t = filing.get(p["target"], 0.0)
        if p["kind"] in ("cross_sheet_equality", "same_sheet_equality"):
            e = filing.get(p["srcs"][0], 0.0)
        else:
            e = round(sum(filing.get(s, 0.0) for s in p["srcs"]), 6)
        if abs(t - e) > TOL:
            fails.append(p["id"])
    return fails


# --------------------------------------------------------- L4: mutate & score
def main():
    t0 = time.time()
    preds = build_graph()
    t_graph = time.time() - t0
    by_kind = Counter(p["kind"] for p in preds)

    clean = synth_clean(preds)
    t_synth = time.time() - t0

    base_fails = evaluate(preds, clean)
    print("=" * 96)
    print("L1 -> L5 -> L4, RUN FOR REAL ON THE IFSCA FME WORKBOOK")
    print("=" * 96)
    print(f"  predicates derived from the BLANK template : {len(preds)}   {dict(by_kind)}")
    print(f"  distinct cells in the field graph          : {len(clean)}")
    print(f"  L1 graph build                             : {t_graph*1000:.0f} ms")
    print(f"  clean-filing synthesis                     : {(t_synth-t_graph)*1000:.0f} ms")
    print(f"  L5 evaluation of the clean filing          : {len(base_fails)} failures "
          f"({'CLEAN as constructed' if not base_fails else 'BUG — investigate'})")
    print()
    print("  !! §9.2 caveat, printed by construction: this clean corpus is SYNTHETIC.")
    print("     No false-failure rate quoted from it is a measurement of real filings.")
    print()

    # ---- MUTATION SITES.
    # BUG FOUND AND FIXED HERE (recorded deliberately — it is the point).
    # v1 of this script sampled sites ONLY from cells the predicates already read:
    #     sites = {p["target"]} | {p["srcs"]}
    # That scored a 100.0% kill rate on 3,574 mutants and printed a clean,
    # confident, well-formed result. It was wrong. Mutating only the cells the
    # checks read cannot do anything BUT pass — it is precisely L4 test 2, the
    # degenerate baseline, committed by the harness that is supposed to detect it.
    # The honest denominator is every cell a filer can populate, so the run can
    # measure the cells no predicate touches. That residue is the whole product.
    graph_cells = ({p["target"] for p in preds} | {s for p in preds for s in p["srcs"]})
    input_cells = dv_input_cells()          # every cell under a dataValidation
    sites = sorted(graph_cells | input_cells)
    rng = random.Random(7)
    mutators = [
        ("sign_flip",      lambda v: -v),
        ("scale_x10",      lambda v: v * 10),
        ("scale_div10",    lambda v: v / 10),
        ("off_by_one",     lambda v: v + 1),
        ("digit_transpose", lambda v: float(str(int(abs(v)))[::-1] or 0)),
        ("zero_out",       lambda v: 0.0),
        ("round_to_int",   lambda v: float(round(v))),
    ]
    results = defaultdict(lambda: {"mutants": 0, "killed": 0, "equivalent": 0})
    unkilled_examples = []
    sample = sites if len(sites) <= 4000 else rng.sample(sites, 4000)

    t1 = time.time()
    survivors_by_cell = Counter()
    for cell in sample:
        # input cells outside the field graph carry no synthesised value yet
        if cell not in clean:
            clean[cell] = float(rng.randrange(1000, 999999)) / 100.0
        for mname, fn in mutators:
            orig = clean[cell]
            try:
                nv = fn(orig)
            except Exception:
                continue
            # BUG FIX: every generated mutant counts in the denominator.
            # v1 did `continue` before incrementing, which put equivalent mutants
            # in neither numerator nor denominator and produced MS = 100.1% —
            # an arithmetically impossible number that still printed cleanly.
            results[mname]["mutants"] += 1
            if abs(nv - orig) <= TOL:
                results[mname]["equivalent"] += 1   # provably no observable change
                continue
            clean[cell] = nv
            fails = evaluate(preds, clean)
            clean[cell] = orig
            if fails:
                results[mname]["killed"] += 1
            else:
                survivors_by_cell[cell] += 1
                if len(unkilled_examples) < 8:
                    unkilled_examples.append((cell, mname, orig, nv))
    t_mut = time.time() - t1

    tot_m = sum(r["mutants"] for r in results.values())
    tot_k = sum(r["killed"] for r in results.values())
    tot_e = sum(r["equivalent"] for r in results.values())
    print(f"  MUTATION RUN: {len(sample)} sites x {len(mutators)} operators "
          f"in {t_mut:.1f}s  ({tot_m/max(t_mut,1e-9):,.0f} mutants/sec)")
    print()
    print(f"  {'operator':16} {'mutants':>8} {'killed':>8} {'equiv':>7} {'kill rate':>10}")
    for mname, _ in mutators:
        r = results[mname]
        mr = f"{100*r['killed']/r['mutants']:.1f}%" if r["mutants"] else "-"
        print(f"  {mname:16} {r['mutants']:8} {r['killed']:8} {r['equivalent']:7} {mr:>10}")
    print(f"  {'TOTAL':16} {tot_m:8} {tot_k:8} {tot_e:7} "
          f"{100*tot_k/max(tot_m,1):9.1f}%")
    print()
    print(f"  MUTATION SCORE  MS = killed / (mutants - equivalent)")
    print(f"                     = {tot_k} / ({tot_m} - {tot_e}) "
          f"= {100*tot_k/max(tot_m-tot_e,1):.1f}%")
    print()
    print("  THE MEASURED BLIND SPOT — mutants no predicate catches:")
    print(f"     {tot_m - tot_k} of {tot_m} single-cell corruptions pass every derived check.")
    print("     These cells are read by no predicate, so L5 must return UNCHECKED for them,")
    print("     not PASS. This is the coverage denominator, computed rather than asserted.")
    for cell, mname, o, n in unkilled_examples:
        print(f"       {cell[0][:18]:20}!{cell[1]:6} {mname:14} {o:12.2f} -> {n:12.2f}  survives")

    print()
    print("  COVERAGE, computed rather than asserted:")
    print(f"     mutation sites total          : {len(sites)}")
    print(f"       in the predicate field graph: {len(graph_cells & set(sites))}")
    print(f"       input cells outside it      : {len(set(sites) - graph_cells)}")
    print(f"     cells with >=1 surviving mutant: {len(survivors_by_cell)}  "
          f"-> L5 must return UNCHECKED for these, never PASS")
    cov = 100 * len(graph_cells & set(sites)) / max(len(sites), 1)
    print(f"     COVERAGE FRACTION             : {cov:.1f}%  "
          f"({len(graph_cells & set(sites))} of {len(sites)} sites)")
    out = "/Users/abishaikc/Gift/research/scripts/l4_result.json"
    json.dump({"n_predicates": len(preds), "by_kind": dict(by_kind),
               "cells_in_graph": len(clean), "mutants": tot_m, "killed": tot_k,
               "equivalent": tot_e,
               "mutation_score_pct": round(100*tot_k/max(tot_m-tot_e, 1), 2),
               "per_operator": {k: dict(v) for k, v in results.items()}},
              open(out, "w"), indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
