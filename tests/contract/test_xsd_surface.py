"""D2 — the XSD field surface, and the properties that must hold for it to be evidence.

These are CONTRACT tests: they pin behaviour a consumer relies on, not incidental numbers. The one
figure pinned is the FinCEN schema's field count, because it is the denominator of a published
coverage claim and a silent change to it changes that claim.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cdfc.schema.xsd import BASE_TYPES, FieldDecl, XsdError, XsdRefusal, read

SCHEMA = Path("corpus/regulators/fincen_bsa_xml_2.0.xsd")

# Pinned 20 Aug 2026 against `fincen_bsa_xml_2.0.xsd`. A change here is a change to a published
# denominator and must be deliberate.
FINCEN_FIELDS = 3837
FINCEN_REFUSED = 44
FINCEN_CONTAINERS = 366


@pytest.fixture(scope="module")
def surface():
    if not SCHEMA.is_file():
        pytest.skip(f"{SCHEMA} is not vendored in this checkout")
    return read(SCHEMA, schema_id="fincen-bsa-xml-2.0")


def test_xsd__reads_the_declared_surface(surface):
    assert surface.target_namespace == "www.fincen.gov/base"
    assert surface.roots == ("BSABase",)
    c = surface.counts()
    assert c["fields_total"] == FINCEN_FIELDS
    assert c["refused_total"] == FINCEN_REFUSED
    assert c["containers"] == FINCEN_CONTAINERS


def test_xsd__every_field_carries_a_declared_type(surface):
    """No field may reach the surface without a type the regulator declared.

    A reader that defaults an unrecognised base type to TEXT reports full coverage of a surface it
    did not understand — the exact shape of defect `no_predicate.not_yet_synthesised` exists to
    keep visible on the other side of the system.
    """
    assert all(f.dtype in ("TEXT", "COUNT", "DATE", "ENUM") for f in surface.fields)
    assert all(f.xsd_type for f in surface.fields)


def test_xsd__every_refusal_takes_a_reason_from_the_closed_vocabulary(surface):
    """`absent != empty != zero`. A refusal with no reason is an omission wearing a count."""
    allowed = {r.value for r in XsdRefusal}
    for path, why, detail in surface.refused:
        assert why in allowed, f"{path}: {why!r} is not in the closed vocabulary"
        assert detail.strip(), f"{path}: refused with an empty detail"


def test_xsd__decimal_is_refused_and_never_becomes_money(surface):
    """`xsd:decimal` declares a number, not a currency, a scale or a unit.

    Mapping it to `MILLI_USD_MILLION` would make every comparison against it arithmetic on an
    assumption nobody recorded. All 44 refusals in this schema are exactly this.
    """
    assert "decimal" not in BASE_TYPES
    reasons = {why for _p, why, _d in surface.refused}
    assert reasons == {XsdRefusal.TYPE_DECLARES_NO_UNIT.value}


def test_xsd__multivalued_fields_declare_their_repeating_ancestors(surface):
    """THE FIELD COUNT IS NOT A COUNT OF ADDRESSES, and this is why.

    `BSABase.Activity` is `maxOccurs="unbounded"`, so every field beneath it is one value PER
    activity. Measured: **0 of 3,837 fields in this schema are single-valued.** A surface that
    flattened that would report 3,837 addressable cells for a filing whose real cardinality
    depends on how many activities and parties the filer has — a plausible total nobody opened,
    and directly comparable to the IFSCA workbook's 3,747 SINGLE-valued cells when it is not.
    """
    c = surface.counts()
    assert c["fields_singleton"] + c["fields_multivalued"] == c["fields_total"]
    assert c["fields_singleton"] == 0
    for f in surface.fields:
        assert f.is_multivalued
        assert f.repeating_ancestors or f.repeatable
        for anc in f.repeating_ancestors:
            assert f.path.startswith(anc + "."), f"{f.path} does not sit under {anc}"


def test_xsd__requiredness_comes_from_the_schema_and_this_one_declares_none(surface):
    """1,527 of 1,528 elements declare `minOccurs="0"`.

    FinCEN mandates nothing in the SCHEMA; requiredness lives in its business rules. Recorded
    because a downstream consumer must not read "0 required" as "nothing is mandatory".
    """
    assert sum(1 for f in surface.fields if f.required) == 0


def test_xsd__refuses_a_document_that_is_not_a_schema(tmp_path):
    p = tmp_path / "not-a-schema.xsd"
    p.write_text("<html><body>hello</body></html>", encoding="utf-8")
    with pytest.raises(XsdError, match="not an XML Schema"):
        read(p)


def test_xsd__refuses_a_schema_with_no_root_element(tmp_path):
    p = tmp_path / "rootless.xsd"
    p.write_text(
        '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:x">'
        '<xsd:complexType name="T"><xsd:sequence/></xsd:complexType></xsd:schema>',
        encoding="utf-8",
    )
    with pytest.raises(XsdError, match="no top-level element"):
        read(p)


def test_xsd__an_inline_enumeration_becomes_a_declared_vocabulary(tmp_path):
    """A POSITIVE CONTROL. The FinCEN base schema carries ZERO enumerations — its code lists live
    in a separate `www.fincen.gov/codes` namespace we do not have — so without this the ENUM branch
    would be untested and could be dead. A vocabulary path nothing exercises is a vocabulary path
    nobody has seen work."""
    p = tmp_path / "enum.xsd"
    p.write_text(
        '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:x">'
        '<xsd:element name="Return"><xsd:complexType><xsd:sequence>'
        '<xsd:element name="Status" minOccurs="1"><xsd:annotation>'
        "<xsd:documentation>The filing status.</xsd:documentation></xsd:annotation>"
        '<xsd:simpleType><xsd:restriction base="xsd:string">'
        '<xsd:enumeration value="NEW"/><xsd:enumeration value="AMENDED"/>'
        "</xsd:restriction></xsd:simpleType></xsd:element>"
        "</xsd:sequence></xsd:complexType></xsd:element></xsd:schema>",
        encoding="utf-8",
    )
    s = read(p)
    assert len(s.fields) == 1
    f: FieldDecl = s.fields[0]
    assert f.dtype == "ENUM"
    assert f.vocabulary == ("NEW", "AMENDED")
    assert f.label == "The filing status."
    assert f.required is True
    assert f.is_multivalued is False
    assert s.with_vocabulary() == (f,)


def test_xsd__a_recursive_type_is_refused_rather_than_followed(tmp_path):
    """A POSITIVE CONTROL for the recursion guard. Without it this schema does not terminate."""
    p = tmp_path / "recursive.xsd"
    p.write_text(
        '<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:x">'
        '<xsd:complexType name="NodeType"><xsd:sequence>'
        '<xsd:element name="Value" type="xsd:string"/>'
        '<xsd:element name="Child" type="NodeType" minOccurs="0"/>'
        "</xsd:sequence></xsd:complexType>"
        '<xsd:element name="Root" type="NodeType"/></xsd:schema>',
        encoding="utf-8",
    )
    s = read(p)
    assert any(why == XsdRefusal.RECURSIVE_TYPE.value for _p, why, _d in s.refused)
    assert [f.path for f in s.fields] == ["Root.Value"]
