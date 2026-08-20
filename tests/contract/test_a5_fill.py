"""A5 — the fill lane's contract. Every condition gets a POSITIVE control that makes it fail.

A condition nothing has been observed refusing is a condition nobody has seen work. Each of the six
has a test that constructs the exact situation it exists to catch and asserts the named refusal —
and one that constructs the situation where it holds, so the tests cannot all pass by refusing
everything.
"""

from __future__ import annotations

import pytest

from cdfc.evidence.fields import Field, FieldSet
from cdfc.evidence.observe import Observation
from cdfc.evidence.vocabulary import Asks, FieldType
from cdfc.fill.propose import (
    CONDITIONS,
    FillDeclaration,
    FillRefusal,
    propose,
)
from cdfc.qualify.textsource import (
    Corroboration,
    InstrumentText,
    ResolvedUnit,
)

PROV = "test-binding"


def _source(text: str) -> InstrumentText:
    """A minimal addressable text. The digest is not re-derived here: these tests are about the
    fill conditions, and `test_textsource_pins` is what guards the digest."""
    return InstrumentText(
        instrument_id="t", text=text,
        units=(ResolvedUnit(key="u0", page=1, span=(0, len(text)),
                            corroboration=Corroboration.AGREED, parties=("a", "b"),
                            external_party=True),),
        disputed=(), manifests=(), transformations=(), refused_transformations=(),
        divisions=__import__("cdfc.qualify.provisions", fromlist=["recover"]).recover(
            [("u0", 1, (0, len(text)), "AGREED")], text),
        sha256="0" * 64,
    )


def _fields(*fields: Field, surface: frozenset[str] | None = None) -> FieldSet:
    refs = surface if surface is not None else frozenset(f.ref for f in fields)
    return FieldSet(template_sha256="t" * 64, surface_total=len(refs),
                    label_rule=list(__import__("cdfc.evidence.fields", fromlist=["LabelRule"])
                                    .LabelRule)[0],
                    fields=fields, surface=refs)


# The document name must MATCH the source's instrument_id. It did not before — the fixtures said
# "src.pdf" while `_source` built an instrument called "t" — and nothing noticed, because
# re-verification ignored which document a span belonged to. It no longer does: a run may read
# several sources, and a span from one re-read in another could match by coincidence.
def _obs(value: str, text: str, *, doc: str = "t") -> Observation:
    lo = text.index(value)
    return Observation(value=value, document=doc, span=(lo, lo + len(value)), page=1,
                       context=text[:60])


# --- the happy path, so the suite cannot pass by refusing everything -------------------------


def test_a5__a_grounded_reverifying_typed_value_is_proposed():
    text = "The net worth of the entity is 5,00,000 as at the reporting date."
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f), {"S!A1": (_obs("5,00,000", text),)}, _source(text),
                binding_provenance=PROV)
    assert len(d.proposed) == 1
    p = d.proposed[0]
    assert p.admitted
    assert p.value == "5,00,000"
    assert p.span == (31, 39)
    assert [c.name for c in p.conditions] == list(CONDITIONS)
    assert all(c.holds for c in p.conditions)
    assert d.counts()["admitted"] == 1


# --- one positive control per condition ------------------------------------------------------


def test_a5__GROUNDED_refuses_a_field_nothing_observed():
    text = "Nothing here."
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f), {}, _source(text), binding_provenance=PROV)
    assert d.refused[0].reason is FillRefusal.NO_OBSERVATION
    assert not d.proposed


def test_a5__REVERIFIES_refuses_evidence_whose_span_does_not_reproduce():
    """THE TRIGGER, and the one this product exists to get right.

    `W0-C` had a similarity locator return SUPPORTED 20 of 20 on DELETED evidence. Here the span
    points at text that says something else, and the observation is refused for that reason alone —
    no score, no threshold.
    """
    text = "The net worth of the entity is 5,00,000."
    lying = Observation(value="9,99,999", document="t", span=(31, 39), page=1, context="")
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f), {"S!A1": (lying,)}, _source(text), binding_provenance=PROV)
    assert d.refused[0].reason is FillRefusal.REVERIFICATION_FAILED
    assert "byte-exact" in d.refused[0].detail


def test_a5__UNIQUE_refuses_two_sources_that_disagree():
    text = "Net worth is 5,00,000 in one place and 7,00,000 in another."
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f), {"S!A1": (_obs("5,00,000", text), _obs("7,00,000", text))},
                _source(text), binding_provenance=PROV)
    assert d.refused[0].reason is FillRefusal.SUPPORT_CONTRADICTED
    assert "disagree" in d.refused[0].detail


def test_a5__TYPE_ADMITS_refuses_prose_offered_for_a_money_field():
    text = "The net worth is approximately five lakh rupees."
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f), {"S!A1": (_obs("approximately five lakh", text),)}, _source(text),
                binding_provenance=PROV)
    assert d.refused[0].reason is FillRefusal.TYPE_NOT_ADMITTED


def test_a5__VOCABULARY_ADMITS_refuses_a_value_outside_the_templates_own_list():
    text = "The scheme category is Growth for this period."
    f = Field(ref="S!A1", label="Category", type=FieldType.ENUM, asks=Asks.FACT,
              vocabulary=("Retail", "Non-Retail"))
    d = propose(_fields(f), {"S!A1": (_obs("Growth", text),)}, _source(text),
                binding_provenance=PROV)
    assert d.refused[0].reason is FillRefusal.VOCABULARY_NOT_ADMITTED
    assert "data validation" in d.refused[0].detail


def test_a5__an_attestation_is_never_filled_even_with_perfect_evidence():
    """THE LANE SEPARATION. The evidence here re-verifies and is unique; it is still not filled,
    because a certification is a natural person accepting liability."""
    text = "The Net worth requirement has been complied with: Yes."
    f = Field(ref="S!C6", label="The Net worth requirement has been complied with",
              type=FieldType.TEXT, asks=Asks.ATTESTATION)
    d = propose(_fields(f), {"S!C6": (_obs("Yes", text),)}, _source(text),
                binding_provenance=PROV)
    assert not d.proposed
    assert not d.refused
    assert len(d.attestations) == 1
    a = d.attestations[0]
    assert a.ref == "S!C6"
    assert len(a.supporting) == 1            # the evidence IS assembled for the signatory
    assert "complied with" in a.certifies


# --- the declaration's own discipline --------------------------------------------------------


def test_a5__an_unlabelled_cell_is_refused_by_name_not_omitted():
    """`N2` measured 132 labelled of 3,747. The unlabelled majority must be VISIBLE."""
    text = "irrelevant"
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f, surface=frozenset({"S!A1", "S!A2", "S!A3"})),
                {}, _source(text), binding_provenance=PROV)
    reasons = {r.ref: r.reason for r in d.refused}
    assert reasons["S!A2"] is FillRefusal.FIELD_NOT_LABELLED
    assert reasons["S!A3"] is FillRefusal.FIELD_NOT_LABELLED
    assert reasons["S!A1"] is FillRefusal.NO_OBSERVATION


def test_a5__the_declaration_refuses_to_be_constructed_unless_it_closes():
    with pytest.raises(ValueError, match="does not close"):
        FillDeclaration(template_sha256="t" * 64, surface_total=5,
                        proposed=(), refused=(), attestations=())


def test_a5__a_field_may_not_appear_in_two_lanes():
    from cdfc.fill.propose import Refusal

    r = Refusal("S!A1", "x", FillRefusal.NO_OBSERVATION, "d")
    with pytest.raises(ValueError, match="more than one lane"):
        FillDeclaration(template_sha256="t" * 64, surface_total=2,
                        proposed=(), refused=(r, r), attestations=())


def test_a5__a_binding_with_no_declared_provenance_is_refused():
    """A refusal that cannot say WHOSE proposal it refused is not an audit record."""
    text = "x"
    f = Field(ref="S!A1", label="L", type=FieldType.TEXT, asks=Asks.FACT)
    with pytest.raises(ValueError, match="provenance"):
        propose(_fields(f), {}, _source(text), binding_provenance="  ")


def test_a5__every_condition_is_reported_even_when_not_reached():
    """A report that silently omitted the checks it skipped would imply they passed."""
    text = "Nothing here."
    f = Field(ref="S!A1", label="Net worth", type=FieldType.MONEY, asks=Asks.FACT)
    d = propose(_fields(f), {}, _source(text), binding_provenance=PROV)
    assert not d.proposed and len(d.refused) == 1
    # the happy-path proposal carries all six; so must a failed evaluation's internal record
    text2 = "The net worth of the entity is 5,00,000."
    d2 = propose(_fields(f), {"S!A1": (_obs("5,00,000", text2),)}, _source(text2),
                 binding_provenance=PROV)
    assert len(d2.proposed[0].conditions) == len(CONDITIONS)


# --- the DERIVED lane: model-synthesised values are ADMITTED, and labelled ---------------------


def test_a5__a_derived_value_is_admitted_but_never_counted_as_evidenced():
    """THE FLEXIBILITY, and the line that replaces the one it relaxes.

    Requiring a byte-exact span refused everything a model SYNTHESISES — a figure summed across
    three custodian files, a total restated from a table. Those are now admitted. What does not
    happen is that they enter the evidenced count.
    """
    from cdfc.fill.propose import Derived

    d = Derived(ref="S!A9", label="Total AUM", value="1,55,40,00,000",
                basis="summed across three custodian files",
                supported_by=("r0004", "r0011", "r0027"), model="m")
    decl = FillDeclaration(template_sha256="t" * 64, surface_total=1,
                           proposed=(), refused=(), attestations=(), derived=(d,))
    c = decl.counts()
    assert c["derived"] == 1
    assert c["admitted"] == 0                 # NOT evidenced
    assert c["filled_total"] == 1             # but a value IS placed in the return
    assert decl.filled() == ("S!A9",)
    assert d.as_canonical_obj()["evidenced"] is False
    assert "DERIVED, no span supports them" in "\n".join(decl.lines())


def test_a5__the_declaration_still_closes_with_four_lanes():
    from cdfc.fill.propose import Derived

    d = Derived(ref="S!A1", label="l", value="v", basis="b", supported_by=(), model="m")
    with pytest.raises(ValueError, match="does not close"):
        FillDeclaration(template_sha256="t" * 64, surface_total=3,
                        proposed=(), refused=(), attestations=(), derived=(d,))


def test_a5__a_field_may_not_be_both_evidenced_and_derived():
    """One field, one lane. A ref in two lanes would be counted twice by `filled()`."""
    from cdfc.fill.propose import Derived, Refusal

    d = Derived(ref="S!A1", label="l", value="v", basis="b", supported_by=(), model="m")
    r = Refusal("S!A1", "l", FillRefusal.NO_OBSERVATION, "d")
    with pytest.raises(ValueError, match="more than one lane"):
        FillDeclaration(template_sha256="t" * 64, surface_total=2,
                        proposed=(), refused=(r,), attestations=(), derived=(d,))
