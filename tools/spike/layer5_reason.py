"""Layer 5 — REASONING. Atoms computed deterministically; Datalog chains them.

The split is forced by measurement, not taste: semantica's Datalog ACCEPTED an inline
comparison and silently derived nothing, so every comparison is computed here, in Python,
and enters the engine as a ground fact. Datalog does only what it is sound at — chaining.
"""
import json
from semantica.reasoning.datalog_reasoner import DatalogReasoner

ADMITTED = json.load(open("admitted.json"))

FILINGS = {
    "fme_a": {"B3": "Registered (Non-Retail)", "B4": 300000, "B9": "no",  "B10": "no"},
    "fme_b": {"B3": "Registered (Non-Retail)", "B4": 300000, "B9": "yes", "B10": "no"},
    "fme_c": {"B3": "Authorised",              "B4":  50000, "B9": "no",  "B10": "no"},
}

def slug(v: str) -> str:
    """The engine's fact parser refuses quoted literals containing spaces or parentheses, so a
    term is slugified on the way in. MEASURED, not assumed: `category(x, "Registered (Non-Retail)")`
    raises `Invalid fact syntax`. The mapping is one-to-one and kept so the graph can render the
    original wording rather than the slug."""
    import re
    return re.sub(r"[^a-z0-9]+", "_", v.lower()).strip("_")


def atoms(entity, filed):
    """THE COMPARISONS. Computed here so the engine never has to do arithmetic."""
    out = [f"category({entity}, {slug(filed['B3'])})"]
    for r in ADMITTED:
        req = r.get("requires") or {}
        if "value" in req and req.get("unit") == "USD" and r.get("field") == "B4":
            rid = r["eId"]
            ok = filed["B4"] >= req["value"] if req["comparator"] == ">=" else None
            out.append(f"{'meets' if ok else 'below'}({entity}, {rid})")
        for f, v in (r.get("applies_when") or {}).items():
            if f == "B9" and filed.get("B9") == v:
                out.append(f"restricted_only({entity})")
    return sorted(set(out))

RULES = [
    # applicability -> obligation
    'obliged(X, reg_8__subreg_1) :- category(X, registered_non_retail)',
    'obliged(X, reg_9__subreg_1) :- category(X, authorised)',
    # THE EXCEPTION: the proviso displaces the base obligation
    'obliged(X, reg_8__subreg_1__proviso_1) :- obliged(X, reg_8__subreg_1), restricted_only(X)',
    'displaced(X, reg_8__subreg_1) :- obliged(X, reg_8__subreg_1), restricted_only(X)',
    # breach = obliged, below the threshold, and not displaced
    'breach(X, R) :- obliged(X, R), below(X, R)',
]

for entity, filed in FILINGS.items():
    r = DatalogReasoner()
    a = atoms(entity, filed)
    for f in a: r.add_fact(f)
    for rule in RULES: r.add_rule(rule)
    r.derive_all()
    breaches   = [b["R"] for b in r.query("breach(X, R)", {"X": entity})] if r.query("breach(X, R)") else []
    breaches   = sorted({row.get("R") for row in r.query("breach(X, R)")})
    obliged    = sorted({row.get("R") for row in r.query("obliged(X, R)")})
    displaced  = sorted({row.get("R") for row in r.query("displaced(X, R)")})
    print(f"\n=== {entity}  cat={filed['B3']!r} net_worth={filed['B4']:,} restricted_only={filed['B9']}")
    print(f"   atoms      : {a}")
    print(f"   obliged by : {obliged}")
    print(f"   displaced  : {displaced or '-'}")
    print(f"   BREACH     : {breaches or 'none'}")
