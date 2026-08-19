"""Layer 5b — PRECEDENCE RESOLVED BEFORE THE ENGINE, so the engine never needs negation.

MEASURED: semantica's Datalog accepts `not` / `!` / `NOT` in a rule body and SILENTLY IGNORES
them, deriving a breach the exception displaces. It also accepts an inline comparison and
derives nothing. Two silent acceptances — so it may chain, and nothing else.

The repair is not a better rule. It is to compute WHICH OBLIGATION IS IN FORCE deterministically
and hand the engine only that one. An exception is a precedence question, and precedence is a
total order we can compute; negation was only ever the way to express it inside Datalog.
"""
import json
from semantica.reasoning.datalog_reasoner import DatalogReasoner

ADMITTED = json.load(open("admitted.json"))
BY_ID = {r["eId"]: r for r in ADMITTED}

# EXCEPTION edges from the graph: proviso displaces its base provision
DISPLACES = {r["eId"]: r["eId"].split("__proviso")[0]
             for r in ADMITTED if r["kind"] == "EXCEPTION"}

FILINGS = {
    "fme_a": {"B3": "Registered (Non-Retail)", "B4": 300000, "B9": "no"},
    "fme_b": {"B3": "Registered (Non-Retail)", "B4": 300000, "B9": "yes"},
    "fme_c": {"B3": "Authorised",              "B4":  50000, "B9": "no"},
}

def applies(rule, filed):
    for f, v in (rule.get("applies_when") or {}).items():
        if str(filed.get(f)).strip().lower() != str(v).strip().lower():
            return False
    return True

def effective(filed):
    """The obligations IN FORCE for this filing, after precedence. Deterministic."""
    live = {r["eId"] for r in ADMITTED
            if r.get("field") == "B4" and r.get("requires", {}).get("value") and applies(r, filed)}
    for proviso, base in DISPLACES.items():
        if proviso in live:
            live.discard(base)          # the exception displaces its base — computed, not inferred
    return sorted(live)

RULES = ['breach(X, R) :- in_force(X, R), below(X, R)']

# THE LIBRARY WRITES `\r` PROGRESS BARS TO STDOUT, and the next call's bar erases the previous
# printed line. Results are therefore COLLECTED and rendered after every engine call has finished.
# Discovered by a row going missing from a three-row table — a library that owns stdout can
# silently delete its caller's output.
_rows = []
for e, filed in FILINGS.items():
    live = effective(filed)
    r = DatalogReasoner()
    for rid in live:
        r.add_fact(f"in_force({e}, {rid})")
        if filed["B4"] < BY_ID[rid]["requires"]["value"]:
            r.add_fact(f"below({e}, {rid})")
    for rule in RULES: r.add_rule(rule)
    r.derive_all()
    br = sorted({row.get("R") for row in r.query("breach(X, R)")})
    thr = ", ".join(f"{BY_ID[x]['requires']['value']:,}" for x in live)
    _rows.append(f"{e:8} {filed['B3']:26} {filed['B4']:>10,}  {(live[0] if live else '-')[:30]:32} "
                 f"{'BREACH ' + br[0] if br else 'compliant (threshold ' + thr + ')'}")

print(f"{'entity':8} {'category':26} {'net worth':>10}  {'obligation in force':32} verdict")
print("-" * 108)
for row in _rows: print(row)
