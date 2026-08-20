"""A SHACL shapes projection of an induced field surface. EXPORT ONLY.

## Why SHACL, and why this is assembly rather than invention

The research answer is unambiguous for this domain: **SHACL is the constraint language for
regulatory requirements, because it is CLOSED-WORLD.** *"Regulatory requirements do not allow for
incomplete knowledge"* — a statement is true or false, and a field that was not reported is not
thereby satisfied. That is this repository's `absent != empty != zero` rule, already standardised
by someone else, and already spoken by every RDF validator.

The second reason is the one that matters architecturally. In a property-graph engine, a constraint
becomes *"part of the engine's write-time behaviour"*; in SHACL it stays **a separate artifact whose
execution model is decided independently**. That is exactly the propose/decide split this system is
built on — our gates DECIDE, and the shapes are DATA that anybody may run.

## What this converts, and what it cannot

A field surface — induced from a workbook's number formats and validation lists (`evidence/fields`)
or read from a regulator's XSD (`schema/xsd`) — is already a set of constraints:

    declared type          -> sh:datatype
    declared vocabulary    -> sh:in            (the template's OWN data-validation list)
    declared requiredness  -> sh:minCount
    single- vs multivalued -> sh:maxCount

**Nothing is invented.** A field the template left `UNDECLARED` produces a `NodeShape` with no
constraint and a `cdfc:undeclared` annotation, NOT a permissive `sh:datatype xsd:string`. A shape
that accepts anything is indistinguishable from a shape nobody wrote, and `A5` already refuses to
fill those fields for the same reason.

## THIS IS AN EXPORT AND IT IS NEVER RUN HERE

`pyshacl` and `rdflib` are absent, deliberately, and this module does not validate anything. It
emits Turtle for an external validator — a regulator's, an auditor's, a customer's — so that our
induced surface can be checked by a tool nobody here wrote. **A shapes file we also validate with
is a claim we grade ourselves**, and `N4` is the measurement that made this project stop doing
that.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Final, Protocol

SH: Final[str] = "http://www.w3.org/ns/shacl#"
XSD: Final[str] = "http://www.w3.org/2001/XMLSchema#"
CDFC: Final[str] = "https://cdfc.dev/ns#"

# Our declared types to XSD datatypes. CLOSED: an unmapped type produces an UNCONSTRAINED shape
# with a reason, never a guess. `MONEY` maps to `decimal` for the export ONLY — internally it is
# an int64 count of 10^-3 USD million, and `schema/xsd.py` refuses the reverse direction for
# exactly that reason.
DATATYPE: Final[dict[str, str]] = {
    "money": f"{XSD}decimal",
    "percent": f"{XSD}decimal",
    "number": f"{XSD}decimal",
    "count": f"{XSD}integer",
    "date": f"{XSD}date",
    "text": f"{XSD}string",
    # AN ENUM IS TYPED, and the first version of this map omitted it. The shape then emitted
    # `cdfc:undeclared "the source declares no type"` in the same property block as an `sh:in`
    # carrying the template's own validation list — a shape asserting on its face that it knew
    # nothing about a field whose permitted values it was listing. The datatype of an enumerated
    # value is the lexical space its members are written in; `sh:in` is the constraint that
    # matters and it needs a datatype to sit beside, not instead of.
    "enum": f"{XSD}string",
}


class HasSurface(Protocol):
    """Anything that declares fields. Both ingresses satisfy it without knowing about this."""

    ...


def _esc(v: str) -> str:
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")


def _slug(ref: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in ref)


def shape_of(
    *, ref: str, label: str, dtype: str, vocabulary: Sequence[str] = (),
    required: bool = False, multivalued: bool = False,
) -> str:
    """One `sh:NodeShape` for one field. Pure; the caller supplies what the regulator declared."""
    name = _slug(ref)
    lines = [
        f"cdfc:{name} a sh:NodeShape ;",
        f'    sh:targetObjectsOf cdfc:{name} ;',
        f'    rdfs:label "{_esc(label or ref)}" ;',
        f'    cdfc:ref "{_esc(ref)}" ;',
    ]
    prop: list[str] = []
    dt = DATATYPE.get(dtype.lower())
    if dt:
        prop.append(f"        sh:datatype <{dt}> ;")
    else:
        # UNDECLARED. No constraint, and it SAYS so — a permissive shape would be
        # indistinguishable from a shape nobody wrote.
        prop.append(f'        cdfc:undeclared "the source declares no type for this field, so '
                    f'no datatype constraint is emitted" ;')
    if vocabulary:
        vals = " ".join(f'"{_esc(v)}"' for v in vocabulary)
        prop.append(f"        sh:in ( {vals} ) ;")
    prop.append(f"        sh:minCount {1 if required else 0} ;")
    if not multivalued:
        prop.append("        sh:maxCount 1 ;")
    lines.append("    sh:property [")
    lines.append(f"        sh:path cdfc:{name} ;")
    lines.extend(prop)
    lines.append("    ] .")
    return "\n".join(lines)


PREFIXES: Final[str] = (
    "@prefix sh:   <http://www.w3.org/ns/shacl#> .\n"
    "@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    "@prefix cdfc: <https://cdfc.dev/ns#> .\n"
)


def from_fieldset(fs) -> str:
    """Turtle shapes for a workbook-induced field surface (`cdfc.evidence.fields.FieldSet`)."""
    body = [
        shape_of(ref=f.ref, label=f.label, dtype=f.type.value, vocabulary=f.vocabulary,
                 required=False, multivalued=False)
        for f in fs.fields
    ]
    return _document(body, source=f"workbook sha256 {fs.template_sha256[:16]}…",
                     declared=len(fs.fields), surface=len(fs.surface) or len(fs.fields))


def from_xsd_surface(surface) -> str:
    """Turtle shapes for an XSD-read field surface (`cdfc.schema.xsd.XsdSurface`)."""
    body = [
        shape_of(ref=f.path, label=f.label, dtype=f.dtype, vocabulary=f.vocabulary,
                 required=f.required, multivalued=f.is_multivalued)
        for f in surface.fields
    ]
    return _document(body, source=f"xsd {surface.schema_id} ({surface.target_namespace})",
                     declared=len(surface.fields),
                     surface=len(surface.fields) + len(surface.refused))


def _document(body: Iterable[str], *, source: str, declared: int, surface: int) -> str:
    header = (
        f"{PREFIXES}\n"
        f"# SHACL shapes projected from {source}\n"
        f"# {declared} of {surface} declared members carry a shape.\n"
        "# GENERATED, and an EXPORT: nothing in cdfc validates against these. They exist so an\n"
        "# external validator can check our induced surface with a tool nobody here wrote.\n"
        "# A field whose source declared no type carries cdfc:undeclared and NO sh:datatype:\n"
        "# a permissive shape is indistinguishable from a shape nobody wrote.\n\n"
    )
    return header + "\n\n".join(body) + "\n"
