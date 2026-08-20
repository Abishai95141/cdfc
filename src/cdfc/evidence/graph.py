"""LAYER 4 — the graph, built ONLY from admitted proposals.

**networkx and rdflib are deliberately absent.** The spike used both and they were the right tool
for a throwaway; they are the wrong dependency here. This package sits behind a product whose
claim is a small auditable verdict path, and a graph library in that closure is a large amount of
code nobody on this project has read. The graph we need is nodes, typed edges, and adjacency --
about eighty lines. An RDF projection remains available as an EXPORT, computed from these nodes,
which is where a serialisation format belongs.

**The refusals are not in it, and that is the load-bearing property.** A query over this graph
cannot return an ungrounded claim, because a claim that failed a gate never became a node. The
adjudication is retained ALONGSIDE the graph rather than inside it, so *what was refused and why*
stays answerable without ever being reachable from a traversal.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum

from cdfc.evidence.fields import FieldSet
from cdfc.evidence.gates import Adjudication
from cdfc.evidence.provisions import ProvisionSet


class NodeKind(StrEnum):
    PROVISION = "Provision"
    FIELD = "Field"
    RULE = "Rule"
    # B2. A RECORD is one row of one document — OBSERVED. An ENTITY is one identity resolved
    # across records — DERIVED. Two kinds rather than one, because an auditor needs to tell what a
    # document SAID from what we CONCLUDED by putting two documents side by side.
    RECORD = "Record"
    ENTITY = "Entity"


class EdgeKind(StrEnum):
    CITES = "cites"            # Rule  -> Provision
    GOVERNS = "governs"        # Rule  -> Field
    REFERS_TO = "refers_to"    # Rule  -> Provision (a cross-reference that RESOLVED)
    RESOLVES_TO = "resolves_to"    # Record -> Entity
    EVIDENCES = "evidences"        # Record -> Field  (a record supplied this field's value)


@dataclass(frozen=True, slots=True)
class Node:
    id: str
    kind: NodeKind
    attrs: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class Edge:
    src: str
    kind: EdgeKind
    dst: str


@dataclass(frozen=True, slots=True)
class Graph:
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]

    def by_kind(self, kind: NodeKind) -> tuple[Node, ...]:
        return tuple(n for n in self.nodes if n.kind is kind)

    def out(self, src: str, kind: EdgeKind | None = None) -> tuple[Edge, ...]:
        return tuple(e for e in self.edges
                     if e.src == src and (kind is None or e.kind is kind))

    def into(self, dst: str, kind: EdgeKind | None = None) -> tuple[Edge, ...]:
        return tuple(e for e in self.edges
                     if e.dst == dst and (kind is None or e.kind is kind))

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for n in self.nodes:
            out[n.kind.value] = out.get(n.kind.value, 0) + 1
        return dict(sorted(out.items()))

    def triples(self) -> Iterator[tuple[str, str, str]]:
        """An RDF-shaped projection, computed on demand. Declared lossy: node attributes that
        are not scalars are omitted rather than serialised into a shape nobody declared."""
        for n in self.nodes:
            yield (n.id, "rdf:type", n.kind.value)
            for k, v in n.attrs:
                yield (n.id, k, v)
        for e in self.edges:
            yield (e.src, e.kind.value, e.dst)


def build(adj: Adjudication, provisions: ProvisionSet, fields: FieldSet,
          entities: Any = None) -> Graph:
    """`entities` is an optional `cdfc.evidence.entities.EntitySet`.

    Optional because the rules-and-fields graph predates it and every caller that does not resolve
    records still gets exactly the graph it got before — an empty entity layer is ABSENT, not a
    layer of zero, and `counts()` simply carries no Record or Entity key.
    """
    nodes: list[Node] = []
    edges: list[Edge] = []

    for p in provisions.provisions:
        nodes.append(Node(
            id=f"prov:{p.eid}", kind=NodeKind.PROVISION,
            attrs=(("eid_kind", p.eid_kind.value), ("durable", str(p.durable).lower())),
        ))
    for f in fields.fields:
        nodes.append(Node(
            id=f"field:{f.ref}", kind=NodeKind.FIELD,
            attrs=(("type", f.type.value), ("asks", f.asks.value), ("label", f.label)),
        ))

    if entities is not None:
        field_refs = {f.ref for f in fields.fields}
        for r in entities.records:
            nodes.append(Node(id=r.id, kind=NodeKind.RECORD,
                              attrs=(("document", r.document), ("row", str(r.row)))))
        for e in entities.entities:
            nodes.append(Node(
                id=e.id, kind=NodeKind.ENTITY,
                attrs=(("resolved_by", e.resolved_by.value),
                       ("documents", ",".join(e.documents)),
                       ("cross_document", str(e.is_cross_document).lower())),
            ))
            for r in e.records:
                # An entity resolved across two documents gets TWO of these, which is what makes
                # "one identity, seen in both files" a traversable fact rather than a claim.
                edges.append(Edge(src=r.id, dst=e.id, kind=EdgeKind.RESOLVES_TO))
                for name in r.fields:
                    ref = name if name in field_refs else None
                    if ref is not None:
                        edges.append(Edge(src=r.id, dst=f"field:{ref}", kind=EdgeKind.EVIDENCES))

    # ONLY ADMITTED PROPOSALS. The index is the position in the admitted sequence, so a rule id
    # is stable for a given input set and says nothing about the refused ones.
    for i, v in enumerate(adj.admitted):
        p = v.proposal
        rid = f"rule:{p.eid}#{i}"
        nodes.append(Node(id=rid, kind=NodeKind.RULE, attrs=(("kind", p.kind.value),)))
        edges.append(Edge(rid, EdgeKind.CITES, f"prov:{p.eid}"))
        if p.field_ref:
            edges.append(Edge(rid, EdgeKind.GOVERNS, f"field:{p.field_ref}"))
        for t in p.refers_to:
            edges.append(Edge(rid, EdgeKind.REFERS_TO, f"prov:{t}"))

    return Graph(nodes=tuple(nodes), edges=tuple(edges))
