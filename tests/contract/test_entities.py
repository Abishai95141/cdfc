"""B2 — cross-document entity resolution, and the Record/Entity layer of the graph."""

from __future__ import annotations

import pytest

from cdfc.correspond.link import Comparison, exact
from cdfc.evidence.entities import (
    EntitySet,
    Record,
    ResolvedBy,
    from_extracted,
    records_from_rows,
    resolve,
)
from cdfc.evidence.graph import EdgeKind, Graph, Node, NodeKind

ENT_H = ["PAN", "Name of the Principal Officer", "Legal Structure of FME"]
ENT_R = [["AABCF1234K", "Asha Rao", "Company"], ["AAECG9876M", "Priya Nair", "LLP"]]
OFF_H = ["PAN", "Name of the Principal Officer", "Email"]
OFF_R = [["AABCF1234K", "Asha  Rao", "asha.rao@example.com"],
         ["AAFCH5555Q", "Rahul Menon", "rahul@example.com"]]


def _norm(a: str, b: str) -> bool:
    return " ".join(a.split()).casefold() == " ".join(b.split()).casefold()


COMPS = [Comparison("PAN", exact), Comparison("Name of the Principal Officer", _norm)]


@pytest.fixture
def resolved():
    left = records_from_rows("entity-master.csv", ENT_H, ENT_R)
    right = records_from_rows("officers.csv", OFF_H, OFF_R)
    return resolve(left, right, COMPS)


def test_entities__one_identity_in_two_documents_becomes_ONE_node(resolved):
    """THE B2 CHECK. `AABCF1234K` is in both files, spelled `Asha Rao` and `Asha  Rao`."""
    cross = resolved.cross_document()
    assert len(cross) == 1
    e = cross[0]
    assert e.documents == ("entity-master.csv", "officers.csv")
    assert e.resolved_by is ResolvedBy.LINKAGE
    assert e.label("PAN") == "AABCF1234K"
    assert len(e.records) == 2


def test_entities__records_PARTITION_into_entities(resolved):
    """A record that belongs to no entity has been dropped, and a resolution that drops a record
    reports a coverage it does not have."""
    covered = [r.id for e in resolved.entities for r in e.records]
    assert sorted(covered) == sorted(r.id for r in resolved.records)
    assert len(set(covered)) == len(covered)
    c = resolved.counts()
    assert c["records"] == 4 and c["entities"] == 3 and c["cross_document"] == 1


def test_entities__a_record_in_two_entities_is_REFUSED_at_construction():
    r = Record(document="d", row=0, fields={"a": "1"})
    from cdfc.evidence.entities import Entity

    a = Entity(id="e1", records=(r,), resolved_by=ResolvedBy.SINGLETON)
    b = Entity(id="e2", records=(r,), resolved_by=ResolvedBy.SINGLETON)
    with pytest.raises(ValueError, match="more than one entity"):
        EntitySet(entities=(a, b), records=(r,), refused=())


def test_entities__a_dropped_record_is_REFUSED_at_construction():
    r = Record(document="d", row=0, fields={"a": "1"})
    with pytest.raises(ValueError, match="belong to no entity"):
        EntitySet(entities=(), records=(r,), refused=())


def test_entities__resolution_with_no_declared_comparison_is_REFUSED():
    """No comparison would link every record to every other; the fields compared are a
    declaration, not a default."""
    left = records_from_rows("a", ENT_H, ENT_R)
    right = records_from_rows("b", OFF_H, OFF_R)
    with pytest.raises(ValueError, match="declaration, not a default"):
        resolve(left, right, [])


def test_entities__a_model_proposed_entity_is_marked_and_never_merged():
    """`D3` measured GraphRAG at 29 entities with no span. They carry the same standing as a
    `Derived` fill: present, useful, not counted as evidenced."""
    es = from_extracted("ifsca-statute", ["FME", "AUTHORITY", "IFSC"], kind="ORGANIZATION")
    assert all(e.resolved_by is ResolvedBy.MODEL for e in es.entities)
    assert es.counts()["by_model"] == 3
    assert es.counts()["by_linkage"] == 0
    assert not es.cross_document()          # a model entity spans one document by construction


def test_entities__one_document_only_yields_singletons_not_an_empty_resolution():
    left = records_from_rows("only.csv", ENT_H, ENT_R)
    es = resolve(left, [], COMPS)
    assert es.counts()["entities"] == 2
    assert all(e.resolved_by is ResolvedBy.SINGLETON for e in es.entities)


# --- the graph layer --------------------------------------------------------------------------


def test_graph__record_and_entity_nodes_with_resolves_to_edges(resolved):
    """An entity resolved across two documents gets TWO `resolves_to` edges — which is what makes
    'one identity, seen in both files' a traversable fact rather than a claim."""
    from cdfc.evidence.fields import Field, FieldSet, LabelRule
    from cdfc.evidence.vocabulary import Asks, FieldType

    class _Adj:
        admitted = ()
        refused = ()

    class _Provs:
        provisions = ()

    fs = FieldSet(template_sha256="t" * 64, surface_total=1, label_rule=list(LabelRule)[0],
                  fields=(Field(ref="PAN", label="PAN", type=FieldType.TEXT, asks=Asks.FACT),),
                  surface=frozenset({"PAN"}))
    from cdfc.evidence.graph import build

    g = build(_Adj(), _Provs(), fs, entities=resolved)
    kinds = g.counts()
    assert kinds[NodeKind.RECORD.value] == 4
    assert kinds[NodeKind.ENTITY.value] == 3

    cross = resolved.cross_document()[0]
    into = g.into(cross.id, EdgeKind.RESOLVES_TO)
    assert len(into) == 2, "a cross-document entity must be reachable from BOTH its records"
    assert {e.src for e in into} == {r.id for r in cross.records}


def test_graph__without_entities_the_layer_is_ABSENT_not_empty():
    """An empty entity layer is absent, not a layer of zero — every caller that does not resolve
    records gets exactly the graph it got before B2."""
    from cdfc.evidence.fields import FieldSet, LabelRule
    from cdfc.evidence.graph import build

    class _Adj:
        admitted = ()
        refused = ()

    class _Provs:
        provisions = ()

    fs = FieldSet(template_sha256="t" * 64, surface_total=0, label_rule=list(LabelRule)[0],
                  fields=(), surface=frozenset())
    g = build(_Adj(), _Provs(), fs)
    assert NodeKind.RECORD.value not in g.counts()
    assert NodeKind.ENTITY.value not in g.counts()
