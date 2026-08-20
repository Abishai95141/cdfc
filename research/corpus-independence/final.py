"""The corpus-independence measurement. Ground truth is DECLARED here and authored by me from
reading each document; that is a label, not a tuning knob, and it is stated so it can be disputed."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from induct import occurrences, templates
from boiler import rank

# (corpus, what the top-level logical division axis IS, how many, how to recognise a candidate)
TRUTH = {
 "ifsca_gazette": ("regulations 1..148, margin-numbered", 147, lambda r: r["chain"] >= 100 and "LE" in str(r["key"])),
 "gdpr":          ("recitals (1)..(173) then Articles 1..99", 173, lambda r: r["chain"] >= 90),
 "gutenberg_prideprejudice": ("CHAPTER I..LXI", 61, lambda r: "chapter" in str(r["key"]).lower()),
 "rfc2616":       ("sections 1..19 incl. 1.1 style", 19, lambda r: "MULTI_INDEX" in str(r["key"]) or (r["chain"]>=15 and "LS" in str(r["key"]) and "page" not in str(r["key"]))),
 "rfc5321":       ("sections 1..8 incl. 4.1.1 style", 8, lambda r: "MULTI_INDEX" in str(r["key"])),
 "rfc8259":       ("sections 1..15", 15, lambda r: "MULTI_INDEX" in str(r["key"]) or (r["chain"]>=10 and "LS" in str(r["key"]))),
 "ecfr_17_275":   ("sections 275.0-2 .. 275.usc", 40, lambda r: "MULTI_INDEX" in str(r["key"])),
 "us_bill_hr3684":("SEC. n across divisions", 100, lambda r: "sec." in str(r["key"]).lower()),
 "w3c_html52":    ("sections 1..14 incl. 4.1 style", 14, lambda r: "MULTI_INDEX" in str(r["key"])),
 "india_const":   ("Articles / Parts", 20, lambda r: "article" in str(r["key"]).lower() or "part" in str(r["key"]).lower()),
 "rbi_circular":  ("numbered paragraphs", 5, lambda r: r["chain"]>=4 and "LS" in str(r["key"])),
}
TEXT = Path(__file__).resolve().parent / "corpora_text"
out = {}
hits1 = hits5 = hitsAny = 0
print(f"{'corpus':26} {'rank':>5} {'chain':>6}  top-1 template")
for name, (desc, n, ok) in TRUTH.items():
    p = TEXT / f"{name}.txt"
    if not p.exists(): print(f"  {name}: MISSING"); continue
    t = p.read_text(); rows = rank(t, templates(occurrences(t)))
    pos = next((i + 1 for i, r in enumerate(rows) if ok(r)), None)
    top = rows[0] if rows else None
    hits1 += pos == 1; hits5 += bool(pos and pos <= 5); hitsAny += bool(pos)
    out[name] = {"expected": desc, "rank_of_correct": pos,
                 "top1": f"{top['key'][0]}:{'|'.join(str(x) for x in top['key'][1])}" if top else None,
                 "top1_chain": top["chain"] if top else 0,
                 "top5": [{"k": f"{r['key'][0]}:{'|'.join(str(x) for x in r['key'][1])}",
                           "score": round(r["score"], 3), "chain": r["chain"], "cands": r["cands"],
                           "variety": round(r["variety"], 3)} for r in rows[:5]]}
    print(f"{name:26} {str(pos or '-'):>5} {top['chain'] if top else 0:>6}  "
          f"{(top['key'][0]+':'+'|'.join(str(x) for x in top['key'][1]))[:44] if top else '-'}")
n = len(TRUTH)
print(f"\ncorrect axis at rank 1 : {hits1} of {n}")
print(f"correct axis in top 5  : {hits5} of {n}")
print(f"correct axis anywhere  : {hitsAny} of {n}")
out["_summary"] = {"corpora": n, "rank1": hits1, "top5": hits5, "found": hitsAny}
json.dump(out, open(TEXT.parent / "corpus_independence.json", "w"), indent=1)
