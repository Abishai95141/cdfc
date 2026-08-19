"""The spike, run against the REAL IFSCA instrument and the REAL FME template."""
import json, re, networkx as nx
from rdflib import Graph as RDFGraph, Literal, Namespace, RDF, URIRef

PROV  = {p["eId"]: p for p in json.load(open('real_provisions.json'))}      # 274 English
FIELD = {f["field"]: f for f in json.load(open('real_fields.json'))}        # 724 labelled
SPLIT = json.load(open('field_split.json'))
ATTEST = {f["field"] for f in SPLIT["attestation"]}

# --- LAYER 2: my proposals over the REAL instrument. eIds and quotes are from real_provisions.
PROPOSALS = json.load(open("real_proposals.json"))

def norm(s): return re.sub(r"\s+", " ", s).strip()

def gate(p):
    v = {}
    prov = PROV.get(p["eId"])
    v["G-QUOTE"] = (bool(prov) and norm(p["quote"]) in norm(prov["text"]),
                    "verbatim" if prov and norm(p["quote"]) in norm(prov["text"]) else "not in provision")
    v["G-FIELD"] = (p["field"] is None or p["field"] in FIELD,
                    "field exists" if p["field"] is None or p["field"] in FIELD else "no such field")
    bad = [r for r in p["refers_to"] if r not in PROV]
    v["G-XREF"] = (not bad, "resolves" if not bad else f"dangling {bad}")
    return v

admitted, refused = [], []
for p in PROPOSALS:
    v = gate(p)
    (admitted if all(ok for ok,_ in v.values()) else refused).append((p, v))

print(f"=== ADJUDICATION over the REAL instrument ===")
print(f"  provisions available {len(PROV)}   labelled fields {len(FIELD)}")
print(f"  proposals {len(PROPOSALS)}   ADMITTED {len(admitted)}   REFUSED {len(refused)}")
for p, v in refused:
    print(f"   REFUSED {p['eId']:22} {'[PLANTED] '+p['_planted'] if '_planted' in p else '[real]'}")
    for g,(ok,why) in v.items():
        if not ok: print(f"       {g}: {why}")

# --- LAYER 4: the graph over the REAL artefacts -------------------------------------------
G = nx.MultiDiGraph()
for eid in PROV: G.add_node(f"prov:{eid}", kind="Provision")
for ref, f in FIELD.items():
    G.add_node(f"field:{ref}", kind="Field", label=f["label"],
               asks="ATTESTATION" if ref in ATTEST else "FACT")
for i,(p,_v) in enumerate(admitted):
    rid=f"rule:{p['eId']}#{i}"; G.add_node(rid, kind="Rule", rule_kind=p["kind"])
    G.add_edge(rid, f"prov:{p['eId']}", key="cites")
    if p["field"]: G.add_edge(rid, f"field:{p['field']}", key="governs")

print(f"\n=== GRAPH over the real artefacts ===")
kinds=collections={}
for _,d in G.nodes(data=True): kinds[d["kind"]]=kinds.get(d["kind"],0)+1
print(f"  nodes {G.number_of_nodes()} {kinds}   edges {G.number_of_edges()}")

NS=Namespace("http://ifsca/"); rg=RDFGraph()
for n,d in G.nodes(data=True):
    u=URIRef(NS[n.replace(':','_').replace('!','_').replace(' ','_').replace('#','_').replace('.','_')])
    rg.add((u,RDF.type,NS[d["kind"]]))
    for k,val in d.items():
        if k!="kind": rg.add((u,NS[k],Literal(str(val))))
for a,b,k in G.edges(keys=True):
    f=lambda x:URIRef(NS[x.replace(':','_').replace('!','_').replace(' ','_').replace('#','_').replace('.','_')])
    rg.add((f(a),NS[k],f(b)))
print(f"  RDF triples {len(rg)}")

print("\n=== QUERY: how much of the real return is governed by an admitted rule? ===")
gov={b for a,b,k in G.edges(keys=True) if k=="governs"}
print(f"  fields governed        {len(gov)} of {len(FIELD)}")
print(f"  provisions cited        {len({b for a,b,k in G.edges(keys=True) if k=='cites'})} of {len(PROV)}")
q="""PREFIX i: <http://ifsca/>
SELECT ?f ?label ?asks WHERE { ?r i:governs ?f . ?f i:label ?label . ?f i:asks ?asks }"""
for row in rg.query(q):
    print(f"   governed -> {str(row[2]):12} {str(row[1])[:56]}")
