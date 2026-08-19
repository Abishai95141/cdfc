"""Layer 4 — THE GRAPH. networkx for structure, rdflib for a queryable projection.

Only ADMITTED rules enter. A refused proposal is never a node: the graph is the set of
things that survived adjudication, so a query over it cannot return an ungrounded claim.
"""
import json
import networkx as nx
from rdflib import Graph as RDFGraph, Literal, Namespace, RDF, URIRef

PROV  = {p["eId"]: p for p in json.load(open("provisions.json"))}
FIELD = {f["field"]: f for f in json.load(open("fields.json"))}
ADMITTED = json.load(open("admitted.json"))
REFUSED  = json.load(open("refused.json"))

G = nx.MultiDiGraph()
for eid, p in PROV.items():
    G.add_node(f"prov:{eid}", kind="Provision", eId=eid, span=tuple(p["span"]))
for ref, f in FIELD.items():
    G.add_node(f"field:{ref}", kind="Field", label=f["label"], declared=f["kind"])

for i, r in enumerate(ADMITTED):
    rid = f"rule:{r['eId']}#{i}"
    G.add_node(rid, kind="Rule", rule_kind=r["kind"], deontic=r.get("deontic"))
    G.add_edge(rid, f"prov:{r['eId']}", key="cites")
    if r.get("field"):
        G.add_edge(rid, f"field:{r['field']}", key="governs")
    for t in (r.get("refers_to") or []):
        G.add_edge(rid, f"prov:{t}", key="refers_to")
    for fref, val in (r.get("applies_when") or {}).items():
        G.add_edge(rid, f"field:{fref}", key="applies_when", value=val)
    if r["kind"] == "EXCEPTION":
        base = r["eId"].split("__proviso")[0]
        for other in G.nodes:
            if other.startswith(f"rule:{base}#"): G.add_edge(rid, other, key="excepts")

print("=== GRAPH ===")
kinds = {}
for _, d in G.nodes(data=True): kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
print("  nodes:", kinds, "total", G.number_of_nodes())
ek = {}
for _, _, k in G.edges(keys=True): ek[k] = ek.get(k, 0) + 1
print("  edges:", ek, "total", G.number_of_edges())

# --- RDF projection, so the graph is queryable with a standard language ---------------------
NS = Namespace("http://spike/")
rg = RDFGraph()
for n, d in G.nodes(data=True):
    u = URIRef(NS[n.replace(":", "_").replace("#", "_")])
    rg.add((u, RDF.type, NS[d["kind"]]))
    for k, v in d.items():
        if k != "kind": rg.add((u, NS[k], Literal(str(v))))
for a, b, k in G.edges(keys=True):
    rg.add((URIRef(NS[a.replace(":", "_").replace("#", "_")]), NS[k],
            URIRef(NS[b.replace(":", "_").replace("#", "_")])))
print(f"  RDF triples: {len(rg)}")

print("\n=== QUERY 1 — which fields are governed, and by what? ===")
q1 = """PREFIX s: <http://spike/>
SELECT ?f ?label ?rk WHERE { ?r s:governs ?f . ?r s:rule_kind ?rk . ?f s:label ?label } ORDER BY ?f"""
for row in rg.query(q1):
    print(f"   {str(row[0]).split('field_')[-1]:5} {str(row[1])[:34]:36} <- {row[2]}")

print("\n=== QUERY 2 — provisions that yielded NO admitted rule (the unchecked half) ===")
governed_prov = {b for a, b, k in G.edges(keys=True) if k == "cites"}
for eid in PROV:
    if f"prov:{eid}" not in governed_prov:
        print(f"   {eid:28} {PROV[eid]['text'][:60]!r}")

print("\n=== QUERY 3 — fields with NO rule governing them ===")
gov_fields = {b for a, b, k in G.edges(keys=True) if k == "governs"}
for ref, f in FIELD.items():
    if f"field:{ref}" not in gov_fields:
        print(f"   {ref:5} {f['label'][:40]:42} declared={f['kind']}")
