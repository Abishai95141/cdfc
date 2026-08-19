"""Layer 3 — THE ADJUDICATOR. Deterministic. Decides what the LLM proposed.

Four gates, each answering a question with no judgement in it:
  G-QUOTE  does the quoted text occur VERBATIM inside the provision it cites?
  G-TYPE   is the field's DECLARED type compatible with what the rule requires?
  G-VOCAB  is the rule's vocabulary a subset of the field's validated list?
  G-XREF   does every cross-reference resolve to a provision that exists?
"""
import json, re
from pathlib import Path

TXT = Path("regs.txt").read_text()
PROV = {p["eId"]: p for p in json.load(open("provisions.json"))}
FIELD = {f["field"]: f for f in json.load(open("fields.json"))}

# what a requirement DEMANDS of a field's declared kind
DEMANDS = {"unit": {"money"}, "temporal": {"date"}, "vocabulary": {"text"}, "present": None}

def g_quote(p):
    prov = PROV.get(p["eId"])
    if prov is None: return False, f"provision {p['eId']} does not exist"
    body = TXT[prov["span"][0]:prov["span"][1]]
    # whitespace is normalised because a PDF line break is not a difference in the law
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    if norm(p["quote"]) in norm(body):
        off = norm(body).index(norm(p["quote"]))
        return True, f"verbatim at +{off}"
    return False, "quote does not occur in the cited provision"

def g_type(p):
    if p.get("field") is None: return True, "no field claimed"
    f = FIELD.get(p["field"])
    if f is None: return False, f"field {p['field']} is not in the template"
    req = p.get("requires") or {}
    for key, allowed in DEMANDS.items():
        if key in req and allowed is not None:
            if f["kind"] not in allowed:
                return False, (f"rule needs {key}, field {p['field']} is declared "
                               f"{f['kind']!r} ({f['label']})")
    return True, f"{p['field']} declared {f['kind']}"

def g_vocab(p):
    req = (p.get("requires") or {}).get("vocabulary")
    if not req: return True, "no vocabulary claimed"
    f = FIELD.get(p["field"], {})
    have = set(f.get("vocabulary") or [])
    missing = set(req) - have
    return (not missing), ("covered by the template's validation list" if not missing
                           else f"terms absent from the field's list: {sorted(missing)}")

def g_xref(p):
    bad = [r for r in (p.get("refers_to") or []) if r not in PROV]
    return (not bad), ("all targets resolve" if not bad else f"dangling: {bad}")

GATES = [("G-QUOTE", g_quote), ("G-TYPE", g_type), ("G-VOCAB", g_vocab), ("G-XREF", g_xref)]

def adjudicate():
    admitted, refused = [], []
    for p in json.load(open("layer2_llm_proposals.json")):
        verdicts = {}
        for name, fn in GATES:
            ok, why = fn(p)
            verdicts[name] = (ok, why)
        if all(ok for ok, _ in verdicts.values()):
            admitted.append({**p, "_verdicts": verdicts})
        else:
            refused.append({**p, "_verdicts": verdicts})
    return admitted, refused

if __name__ == "__main__":
    a, r = adjudicate()
    print(f"proposals {len(a)+len(r)}   ADMITTED {len(a)}   REFUSED {len(r)}\n")
    print("=== REFUSED ===")
    for p in r:
        planted = p.get("_planted_error")
        print(f"  {p['eId']:26} field={str(p.get('field')):5} "
              f"{'[PLANTED] ' + planted if planted else '[NOT PLANTED — a real disagreement]'}")
        for g, (ok, why) in p["_verdicts"].items():
            if not ok: print(f"      {g}: {why}")
    print("\n=== ADMITTED ===")
    for p in a:
        print(f"  {p['eId']:26} -> {str(p.get('field')):5} {p['kind']:22} {p['_verdicts']['G-QUOTE'][1]}")
    json.dump(a, open("admitted.json","w"), indent=1)
    json.dump(r, open("refused.json","w"), indent=1)
