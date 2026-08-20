"""D2 — a field surface read out of an XML SCHEMA, from the regulator's OWN declarations.

## Why this exists

The ingress was `.xlsx` only, and the product claim is *"upload your exports in whatever shape they
arrive"*. A workbook is one way a regulator declares a return; an **XSD is another**, and it is the
one FinCEN, ESMA and every XBRL-lineage regulator use. If the field surface can only be induced
from a spreadsheet, the schema-free claim is really a spreadsheet-free claim.

**Nothing here infers anything.** It is the same architectural move as reading a workbook's number
formats and data-validation lists: the regulator has already declared the type, the label, the
cardinality and often the vocabulary, and this reads those declarations. A workbook makes us work
for the label — `docs/measurements/N2-labelling-rule.md` found 351 of 498 "labels" were the literal
string `NA` — whereas an XSD hands it over in `<xsd:documentation>`. **The XSD is the richer
source, not the harder one.**

## What is declared, and what is refused

    xsd:string                    -> TEXT
    xsd:date, xsd:dateTime        -> DATE
    xsd:long, xsd:int, xsd:integer, xsd:short, xsd:nonNegativeInteger, xsd:positiveInteger
                                  -> COUNT
    an inline restriction carrying <enumeration>  -> ENUM, with the values as its vocabulary

Everything else is REFUSED with a reason from a closed vocabulary. In particular:

**`xsd:decimal` IS NOT MONEY AND IS NOT MAPPED.** The repository's money type is
`MILLI_USD_MILLION` — an int64 count of 10^-3 USD million — and an XSD that says `decimal` has
declared a number, not a currency, a scale or a unit. Guessing would put an unlabelled quantity
into a typed slot and every comparison against it would be arithmetic on an assumption. It is
`type_declares_no_unit`, and the coverage declaration carries it.

## The traversal, and the two things that bite

* **Schemas are recursive.** `PartyType` can contain a `Party`. The walk carries the set of type
  names on the current path and stops when it meets one again, recording `RECURSIVE_TYPE` rather
  than following it — an unbounded path is not a field.
* **A container is not a field.** An element whose type is a `complexType` with a `sequence` is a
  branch; only leaves with a simple type become fields. Counting branches as fields is how a
  surface comes to report a plausible total nobody has opened.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from lxml import etree

from cdfc.ingest.xmlsafe import fromstring as _safe_fromstring

XS: Final[str] = "{http://www.w3.org/2001/XMLSchema}"

# The base types this reader admits, and their `Field.dtype`. CLOSED on purpose: an unmapped base
# type is a REFUSAL with a name, never a silent TEXT. A reader that defaults unknown types to TEXT
# reports full coverage of a surface it did not understand.
BASE_TYPES: Final[Mapping[str, str]] = {
    "string": "TEXT", "normalizedString": "TEXT", "token": "TEXT", "anyURI": "TEXT",
    "date": "DATE", "dateTime": "DATE", "gYear": "DATE", "gYearMonth": "DATE",
    "long": "COUNT", "int": "COUNT", "integer": "COUNT", "short": "COUNT", "byte": "COUNT",
    "nonNegativeInteger": "COUNT", "positiveInteger": "COUNT", "unsignedLong": "COUNT",
    "unsignedInt": "COUNT",
}

# Declared, and declared as a refusal rather than as an omission.
UNMAPPED_WITH_REASON: Final[Mapping[str, str]] = {
    "decimal": "type_declares_no_unit",
    "double": "type_declares_no_unit",
    "float": "type_declares_no_unit",
    "boolean": "type_is_not_a_reported_value",
    "base64Binary": "type_is_not_a_reported_value",
    "hexBinary": "type_is_not_a_reported_value",
}

MAX_DEPTH: Final[int] = 24


class XsdRefusal(StrEnum):
    """Why a declared element did not become a field. CLOSED; every refusal takes one."""

    NO_DECLARED_TYPE = "no_declared_type"
    TYPE_DECLARES_NO_UNIT = "type_declares_no_unit"
    TYPE_IS_NOT_A_REPORTED_VALUE = "type_is_not_a_reported_value"
    TYPE_NOT_IN_VOCABULARY = "type_not_in_vocabulary"
    UNRESOLVED_TYPE_REF = "unresolved_type_ref"
    RECURSIVE_TYPE = "recursive_type"
    DEPTH_EXCEEDED = "depth_exceeded"


class XsdError(RuntimeError):
    """The schema cannot be read. Never repaired, never defaulted."""


@dataclass(frozen=True, slots=True)
class FieldDecl:
    """One leaf the regulator declared, with everything the regulator said about it."""

    path: str                      # Activity.Party.PartyName.RawPartyFullName
    name: str
    dtype: str                     # TEXT | COUNT | DATE | ENUM
    label: str                     # the regulator's own <xsd:documentation>
    required: bool                 # minOccurs >= 1
    repeatable: bool               # maxOccurs != 1
    vocabulary: tuple[str, ...]    # declared <enumeration> values, in schema order
    xsd_type: str
    # THE REPEATABLE ANCESTORS ON THIS PATH, and without them the field count is a lie.
    # `BSABase.Activity.Party.PartyName.RawPartyFullName` is not ONE value: `Activity` and `Party`
    # are both `maxOccurs="unbounded"`, so it is one value PER party PER activity. A surface that
    # flattens that reports 3,837 addressable fields for a filing whose real cardinality depends on
    # how many parties the filer has. A consumer that fills or checks this must know it is
    # addressing a list, so the list-forming ancestors travel with the field.
    repeating_ancestors: tuple[str, ...] = ()

    @property
    def is_multivalued(self) -> bool:
        return bool(self.repeating_ancestors) or self.repeatable

    def as_canonical_obj(self) -> dict[str, object]:
        return {
            "path": self.path, "name": self.name, "dtype": self.dtype, "label": self.label,
            "required": self.required, "repeatable": self.repeatable,
            "vocabulary": list(self.vocabulary), "xsd_type": self.xsd_type,
            "repeating_ancestors": list(self.repeating_ancestors),
        }


@dataclass(frozen=True, slots=True)
class XsdSurface:
    """The field surface of one schema, with its refusals travelling beside it.

    `fields` alone would be a coverage numerator with the denominator removed. `refused` is part of
    the artefact and every entry names why, from `XsdRefusal`.
    """

    schema_id: str
    target_namespace: str
    roots: tuple[str, ...]
    fields: tuple[FieldDecl, ...]
    refused: tuple[tuple[str, str, str], ...]      # (path, reason, detail)
    containers: int

    def counts(self) -> dict[str, int]:
        by_type: dict[str, int] = {}
        for f in self.fields:
            by_type[f.dtype] = by_type.get(f.dtype, 0) + 1
        by_reason: dict[str, int] = {}
        for _p, why, _d in self.refused:
            by_reason[why] = by_reason.get(why, 0) + 1
        return {
            "fields_total": len(self.fields),
            "refused_total": len(self.refused),
            "containers": self.containers,
            "declared_total": len(self.fields) + len(self.refused),
            "fields_singleton": sum(1 for f in self.fields if not f.is_multivalued),
            "fields_multivalued": sum(1 for f in self.fields if f.is_multivalued),
            **{f"dtype_{k}": v for k, v in sorted(by_type.items())},
            **{f"refused_{k}": v for k, v in sorted(by_reason.items())},
        }

    def with_vocabulary(self) -> tuple[FieldDecl, ...]:
        return tuple(f for f in self.fields if f.vocabulary)


def _local(qname: str | None) -> str:
    """The local part of `xsd:string` or `fc2:PartyType`. Prefixes are per-document and are not
    identity; the local name plus the schema's own type table is."""
    if not qname:
        return ""
    return qname.split(":", 1)[-1]


def _doc(node: etree._Element) -> str:
    d = node.find(f"{XS}annotation/{XS}documentation")
    return " ".join((d.text or "").split()) if d is not None else ""


def _restriction_of(node: etree._Element) -> etree._Element | None:
    return node.find(f"{XS}simpleType/{XS}restriction")


def read(path: Path, *, schema_id: str | None = None) -> XsdSurface:
    """Read an `.xsd` into a field surface. Deterministic; no model, no network, no inference."""
    # THROUGH `xmlsafe`, THE ONE DOOR, and this was a real hole rather than a style point. The
    # first version called `etree.parse(path)` directly, which resolves entities and is exactly the
    # XXE surface `xmlsafe` exists to close — on a schema fetched from a regulator's website over
    # the public internet. `test_nc__P08_only_one_parser_factory` walks the AST for precisely this
    # and caught it; NC-P05a's spy watches this door and can only watch one.
    try:
        root = _safe_fromstring(path.read_bytes())
    except etree.XMLSyntaxError as exc:  # a malformed schema is a refusal, not an empty surface
        raise XsdError(f"{path.name}: not parseable as XML — {exc}") from exc
    if not root.tag.endswith("}schema"):
        raise XsdError(
            f"{path.name}: root is {root.tag!r}, not an XML Schema. A field surface read from a "
            "document that does not declare one would be a surface of nothing."
        )

    complex_types = {c.get("name"): c for c in root.iter(f"{XS}complexType") if c.get("name")}
    simple_types = {s.get("name"): s for s in root.iter(f"{XS}simpleType") if s.get("name")}

    fields: list[FieldDecl] = []
    refused: list[tuple[str, str, str]] = []
    containers = 0

    # Top-level elements are the roots. A schema with none declares no document.
    tops = [e for e in root if e.tag == f"{XS}element" and e.get("name")]
    if not tops:
        raise XsdError(f"{path.name}: declares no top-level element, so it has no root to walk.")

    for top in tops:
        containers += _walk(top, "", complex_types, simple_types, fields, refused,
                            frozenset(), 0, ())

    return XsdSurface(
        schema_id=schema_id or path.stem,
        target_namespace=root.get("targetNamespace") or "",
        roots=tuple(e.get("name") for e in tops),
        fields=tuple(fields),
        refused=tuple(refused),
        containers=containers,
    )


def _walk(
    node: etree._Element,
    prefix: str,
    complex_types: Mapping[str, etree._Element],
    simple_types: Mapping[str, etree._Element],
    fields: list[FieldDecl],
    refused: list[tuple[str, str, str]],
    seen_types: frozenset[str],
    depth: int,
    repeating: tuple[str, ...] = (),
) -> int:
    """Walk one element. Returns the number of CONTAINERS found at or under it."""
    name = node.get("name")
    if not name:
        return 0
    path = f"{prefix}.{name}" if prefix else name
    if depth > MAX_DEPTH:
        refused.append((path, XsdRefusal.DEPTH_EXCEEDED.value, f"深 depth {depth}"))
        return 0

    label = _doc(node)
    required = (node.get("minOccurs") or "1") not in ("0",)
    repeatable = (node.get("maxOccurs") or "1") not in ("1",)
    type_ref = _local(node.get("type"))

    # 1. An inline restriction is the richest declaration: base type plus, often, a vocabulary.
    inline = _restriction_of(node)
    if inline is not None:
        return _leaf_from_restriction(inline, path, name, label, required, repeatable,
                                      fields, refused, repeating=repeating)

    # 2. A named simple type in this schema.
    if type_ref and type_ref in simple_types:
        res = simple_types[type_ref].find(f"{XS}restriction")
        if res is not None:
            return _leaf_from_restriction(res, path, name, label, required, repeatable,
                                          fields, refused, xsd_type=type_ref, repeating=repeating)

    # 3. A built-in base type: this is a leaf.
    if type_ref and type_ref not in complex_types:
        if type_ref in BASE_TYPES:
            fields.append(FieldDecl(path=path, name=name, dtype=BASE_TYPES[type_ref], label=label,
                                    required=required, repeatable=repeatable, vocabulary=(),
                                    xsd_type=type_ref, repeating_ancestors=repeating))
        elif type_ref in UNMAPPED_WITH_REASON:
            refused.append((path, UNMAPPED_WITH_REASON[type_ref], f"xsd type {type_ref!r}"))
        else:
            refused.append((path, XsdRefusal.UNRESOLVED_TYPE_REF.value,
                            f"type {type_ref!r} is neither a complexType in this schema nor a "
                            "base type this reader admits"))
        return 0

    # 4. A complex type: a CONTAINER. Recurse into its children.
    ct = complex_types.get(type_ref) if type_ref else node.find(f"{XS}complexType")
    if ct is None:
        refused.append((path, XsdRefusal.NO_DECLARED_TYPE.value,
                        "no type=, no inline simpleType and no inline complexType"))
        return 0
    if type_ref and type_ref in seen_types:
        refused.append((path, XsdRefusal.RECURSIVE_TYPE.value,
                        f"type {type_ref!r} already appears on this path; an unbounded path is "
                        "not a field"))
        return 0

    found = 1
    nxt = seen_types | ({type_ref} if type_ref else frozenset())
    # A container that may occur more than once makes every field beneath it multivalued.
    onward = repeating + ((path,) if repeatable else ())
    for child in ct.iter(f"{XS}element"):
        if child is node:
            continue
        found += _walk(child, path, complex_types, simple_types, fields, refused, nxt, depth + 1,
                       onward)
    return found


def _leaf_from_restriction(
    res: etree._Element, path: str, name: str, label: str, required: bool, repeatable: bool,
    fields: list[FieldDecl], refused: list[tuple[str, str, str]], xsd_type: str | None = None,
    repeating: tuple[str, ...] = (),
) -> int:
    base = _local(res.get("base"))
    enums = tuple(e.get("value") for e in res.findall(f"{XS}enumeration") if e.get("value"))
    declared = xsd_type or base
    if enums:
        # A DECLARED VOCABULARY. This is the strongest thing a schema can say about a field and it
        # is exactly what a workbook's data-validation list gives us — from the regulator, not
        # from a sample of values somebody happened to see.
        fields.append(FieldDecl(path=path, name=name, dtype="ENUM", label=label, required=required,
                                repeatable=repeatable, vocabulary=enums, xsd_type=declared,
                                repeating_ancestors=repeating))
        return 0
    if base in BASE_TYPES:
        fields.append(FieldDecl(path=path, name=name, dtype=BASE_TYPES[base], label=label,
                                required=required, repeatable=repeatable, vocabulary=(),
                                xsd_type=declared, repeating_ancestors=repeating))
    elif base in UNMAPPED_WITH_REASON:
        refused.append((path, UNMAPPED_WITH_REASON[base], f"xsd type {base!r}"))
    else:
        refused.append((path, XsdRefusal.TYPE_NOT_IN_VOCABULARY.value,
                        f"restriction base {base!r} is not a base type this reader admits"))
    return 0


def surfaces_of(paths: Sequence[Path]) -> tuple[XsdSurface, ...]:
    return tuple(read(p) for p in paths)
