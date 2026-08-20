"""The artefact registry's contract, and the cross-upload flow it exists to make possible."""

from __future__ import annotations

import hashlib

import pytest

from cdfc.registry import (
    Artefact,
    ArtefactKind,
    DigestMismatch,
    Registry,
    RegistryError,
    RunInputs,
)
from cdfc.registry.prov import artefact_uri, n_triples, triples
from cdfc.registry.store import merkle_root_of


@pytest.fixture
def reg(tmp_path):
    return Registry(root=tmp_path / "registry")


def test_registry__the_digest_is_the_identity_and_the_filename_is_not(reg):
    """Two custodians sending identical bytes under different names uploaded ONE artefact."""
    data = b"opening balance,1000\nclosing balance,1200\n"
    a = reg.put(data, kind=ArtefactKind.SOURCE, filename="custodian-jan.csv")
    b = reg.put(data, kind=ArtefactKind.SOURCE, filename="TB_2026Q1_final_v2.csv")
    assert a.digest == b.digest == hashlib.sha256(data).hexdigest()
    assert len(reg.list()) == 1
    # the FIRST name is kept: a later rename must not rewrite the provenance of runs that
    # already named this artefact
    assert reg.meta(a.digest).filename == "custodian-jan.csv"


def test_registry__is_idempotent_and_has_no_update(reg):
    data = b"x" * 100
    reg.put(data, kind=ArtefactKind.SOURCE, filename="a.bin")
    reg.put(data, kind=ArtefactKind.SOURCE, filename="a.bin")
    assert reg.counts()["artefacts"] == 1
    assert not hasattr(reg, "update")
    assert not hasattr(reg, "delete")


def test_registry__get_rehashes_and_refuses_a_mismatch(reg):
    """A store that hands back whatever is at a path has made its addresses into filenames."""
    a = reg.put(b"the real bytes", kind=ArtefactKind.SOURCE, filename="s.txt")
    blob = reg.root / "blobs" / a.digest[:2] / a.digest
    blob.write_bytes(b"tampered bytes")
    with pytest.raises(DigestMismatch, match="reading different bytes"):
        reg.get(a.digest)


def test_registry__refuses_an_address_that_is_not_a_digest(reg):
    with pytest.raises(RegistryError, match="not a sha256"):
        reg.get("../../etc/passwd")
    with pytest.raises(RegistryError, match="not a sha256"):
        reg.has_ = reg._blob_path("deadbeef")


def test_registry__refuses_a_nameless_upload(reg):
    with pytest.raises(RegistryError, match="nameless"):
        reg.put(b"x", kind=ArtefactKind.SOURCE, filename="   ")


def test_registry__a_run_may_not_name_an_artefact_the_registry_cannot_produce(reg):
    a = reg.put(b"one", kind=ArtefactKind.RULES, filename="rules.xlsx")
    absent = "f" * 64
    with pytest.raises(RegistryError, match="cannot re-read"):
        reg.inputs([a.digest, absent])


def test_registry__run_inputs_are_a_sorted_set(reg):
    a = reg.put(b"one", kind=ArtefactKind.RULES, filename="r.xlsx")
    b = reg.put(b"two", kind=ArtefactKind.TEMPLATE, filename="t.xlsx")
    i = reg.inputs([b.digest, a.digest, b.digest])          # unsorted, duplicated
    assert i.digests == tuple(sorted({a.digest, b.digest}))
    with pytest.raises(RegistryError, match="stored sorted"):
        RunInputs(digests=tuple(sorted({a.digest, b.digest}, reverse=True)), merkle_root="x")
    with pytest.raises(RegistryError, match="same artefact twice"):
        RunInputs(digests=(a.digest, a.digest), merkle_root="x")


def test_registry__the_merkle_root_is_over_THIS_RUNS_inputs_not_the_whole_registry(reg):
    """THE PROPERTY THAT MAKES A RUN REPRODUCIBLE NEXT YEAR.

    A root over everything present would move under every unrelated upload, and the run id would
    stop being a function of its own inputs.
    """
    a = reg.put(b"rules", kind=ArtefactKind.RULES, filename="r.xlsx")
    b = reg.put(b"template", kind=ArtefactKind.TEMPLATE, filename="t.xlsx")
    before = reg.inputs([a.digest, b.digest])
    reg.put(b"an unrelated upload from another entity", kind=ArtefactKind.SOURCE, filename="u.csv")
    after = reg.inputs([a.digest, b.digest])
    assert before.merkle_root == after.merkle_root
    assert reg.counts()["artefacts"] == 3


def test_registry__the_merkle_root_is_order_independent_but_content_sensitive(reg):
    a = reg.put(b"one", kind=ArtefactKind.RULES, filename="r")
    b = reg.put(b"two", kind=ArtefactKind.SOURCE, filename="s")
    assert merkle_root_of([a.digest, b.digest]) == merkle_root_of([b.digest, a.digest])
    assert merkle_root_of([a.digest]) != merkle_root_of([a.digest, b.digest])


# --- THE CROSS-UPLOAD FLOW, which is the whole point ----------------------------------------


def test_registry__rules_today_financials_next_week_a_filing_the_week_after(reg):
    """`PLAN.md §2`'s user flow, end to end, as three separate uploads and one run.

    This is what `D-A3-01a` found unbuildable: there was nowhere to put the first two uploads.
    """
    day1 = reg.put(b"<rules>published validation rules</rules>",
                   kind=ArtefactKind.RULES, filename="eba-rules-4.3.xlsx")
    day8 = reg.put(b"net worth,750000\naum,124000000\n",
                   kind=ArtefactKind.SOURCE, filename="custodian-feed-q1.csv")
    day15 = reg.put(b"<template/>", kind=ArtefactKind.TEMPLATE, filename="fme-return.xlsx")

    run = reg.inputs([day1.digest, day8.digest, day15.digest])
    assert len(run.digests) == 3

    # the week after, the run re-reads every one of them, byte-exact
    assert reg.get(day1.digest).startswith(b"<rules>")
    assert b"750000" in reg.get(day8.digest)
    assert reg.get(day15.digest) == b"<template/>"

    # and a later, unrelated upload does not change what this run named
    reg.put(b"someone else's filing", kind=ArtefactKind.FILING, filename="other.xlsx")
    assert reg.inputs([day1.digest, day8.digest, day15.digest]).merkle_root == run.merkle_root


def test_registry__counts_split_by_kind_and_kind_is_declared_never_sniffed(reg):
    reg.put(b"a", kind=ArtefactKind.RULES, filename="a")
    reg.put(b"b", kind=ArtefactKind.SOURCE, filename="b")
    reg.put(b"c", kind=ArtefactKind.SOURCE, filename="c")
    c = reg.counts()
    assert c["artefacts"] == 3
    assert c["kind_source"] == 2
    assert c["kind_rules"] == 1
    # the SAME BYTES declared as a different kind is still one artefact: the bytes are the
    # identity, and a kind that could split them would make the digest not an address
    assert len(reg.list(ArtefactKind.SOURCE)) == 2


# --- the PROV-O projection ------------------------------------------------------------------


def test_prov__projects_used_and_generated_by(reg):
    a = reg.put(b"rules", kind=ArtefactKind.RULES, filename="r.xlsx")
    b = reg.put(b"src", kind=ArtefactKind.SOURCE, filename="s.csv")
    inputs = reg.inputs([a.digest, b.digest])
    metas = {x.digest: x for x in reg.list()}
    rows = list(triples("run123", inputs, metas, outputs=("coverage-declaration",)))
    assert (f"urn:cdfc:run:run123", f"http://www.w3.org/ns/prov#used",
            artefact_uri(a.digest)) in rows
    assert any(p.endswith("wasGeneratedBy") for _s, p, _o in rows)
    assert any(p.endswith("wasDerivedFrom") for _s, p, _o in rows)
    nt = n_triples(iter(rows))
    assert nt.endswith("\n") and "<urn:sha256:" in nt


def test_prov__attributes_a_run_to_nobody_unless_a_signatory_is_named(reg):
    """Inventing an agent would put a name against a filing no person accepted."""
    a = reg.put(b"x", kind=ArtefactKind.SOURCE, filename="x")
    inputs = reg.inputs([a.digest])
    metas = {x.digest: x for x in reg.list()}
    unsigned = list(triples("r", inputs, metas))
    assert not any(p.endswith("wasAttributedTo") for _s, p, _o in unsigned)
    signed = list(triples("r", inputs, metas, signatory="A. Adjudicator"))
    assert any(p.endswith("wasAttributedTo") for _s, p, _o in signed)


def test_prov__is_deterministic(reg):
    a = reg.put(b"one", kind=ArtefactKind.RULES, filename="r")
    b = reg.put(b"two", kind=ArtefactKind.SOURCE, filename="s")
    inputs = reg.inputs([a.digest, b.digest])
    metas = {x.digest: x for x in reg.list()}
    assert (n_triples(triples("r", inputs, metas))
            == n_triples(triples("r", inputs, metas)))


# --- the SHACL shapes projection -------------------------------------------------------------


def test_shapes__an_enum_carries_BOTH_a_datatype_and_its_value_list():
    """THE DEFECT THIS PINS. The first version had no `enum` entry in the datatype map, so a shape
    emitted `cdfc:undeclared "the source declares no type"` in the same property block as an
    `sh:in` listing that type's permitted values — a shape asserting it knew nothing about a field
    whose vocabulary it was reciting."""
    from cdfc.registry.shapes import shape_of

    ttl = shape_of(ref="S!A1", label="Category", dtype="enum",
                   vocabulary=("Retail", "Non-Retail"))
    assert "sh:datatype <http://www.w3.org/2001/XMLSchema#string>" in ttl
    assert 'sh:in ( "Retail" "Non-Retail" )' in ttl
    assert "cdfc:undeclared" not in ttl


def test_shapes__an_undeclared_type_gets_NO_datatype_and_says_why():
    """A permissive `sh:datatype xsd:string` is indistinguishable from a shape nobody wrote."""
    from cdfc.registry.shapes import shape_of

    ttl = shape_of(ref="S!A2", label="Something", dtype="undeclared")
    assert "sh:datatype" not in ttl
    assert "cdfc:undeclared" in ttl


def test_shapes__requiredness_and_cardinality_come_from_the_source():
    from cdfc.registry.shapes import shape_of

    req = shape_of(ref="a", label="l", dtype="text", required=True, multivalued=False)
    assert "sh:minCount 1" in req and "sh:maxCount 1" in req
    multi = shape_of(ref="b", label="l", dtype="text", required=False, multivalued=True)
    assert "sh:minCount 0" in multi and "sh:maxCount" not in multi


def test_shapes__nothing_in_cdfc_validates_against_the_shapes_it_emits():
    """`pyshacl` and `rdflib` are absent DELIBERATELY: a shapes file we also validate with is a
    claim we grade ourselves, which is what `N4` made this project stop doing."""
    import cdfc.registry.shapes as m

    src = __import__("inspect").getsource(m)
    assert "pyshacl" not in src.replace("`pyshacl`", "")
    assert "import rdflib" not in src
