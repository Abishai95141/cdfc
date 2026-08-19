"""LAYER 4b — coverage over the graph, and it answers unflatteringly by construction.

The one number this package exists to produce is *how much of the template any rule governs*,
over a denominator that is not arguable. Three properties are deliberate:

**The denominator travels with the numerator, always.** `9 of 724` is a fact; `9` is a boast and
a fraction alone is unauditable. Every count here is returned paired.

**The labelled population is NOT the field surface, and both are reported.** `M-CEIL` measured
the labelled count moving by a factor of six across three defensible labelling rules over the
same 3,747 cells. So the declaration carries the surface total, the labelled total, and the rule
that produced the second -- a reader who disagrees with the rule can see exactly what it cost.

**A third state exists between governed and ungoverned.** The spike's query reported two fields
as untouched when they were READ AS A CONDITION by an admitted rule without being governed by
one. Two states could not express it, so it reported the wrong one.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cdfc.evidence.fields import FieldSet
from cdfc.evidence.gates import Adjudication
from cdfc.evidence.graph import EdgeKind, Graph, NodeKind
from cdfc.evidence.provisions import ProvisionSet
from cdfc.evidence.vocabulary import Asks


class Standing(StrEnum):
    GOVERNED = "governed"          # some admitted rule governs this field
    READ_AS_CONDITION = "read"     # named by an admitted rule, but not governed by one
    UNGOVERNED = "ungoverned"      # no admitted rule reaches it


@dataclass(frozen=True, slots=True)
class Coverage:
    surface_total: int
    labelled_total: int
    label_rule: str
    fields_governed: int
    fields_read: int
    fields_ungoverned: int
    provisions_total: int
    provisions_cited: int
    provisions_durable: int
    rules_admitted: int
    proposals_total: int
    planted_caught: tuple[int, int]
    genuine_refused: tuple[int, int]
    attestation_fields: int

    def lines(self) -> tuple[str, ...]:
        """The declaration as text. Every figure carries its denominator."""
        return (
            f"field surface                {self.surface_total}",
            f"  labelled ({self.label_rule})  {self.labelled_total} of {self.surface_total}",
            f"  governed                   {self.fields_governed} of {self.labelled_total}",
            f"  read as a condition        {self.fields_read} of {self.labelled_total}",
            f"  ungoverned                 {self.fields_ungoverned} of {self.labelled_total}",
            f"  of which ATTESTATION       {self.attestation_fields} of {self.labelled_total}"
            "   (a human signs; the system never fills one)",
            f"provisions                   {self.provisions_total}",
            f"  cited by an admitted rule  {self.provisions_cited} of {self.provisions_total}",
            f"  durably addressable        {self.provisions_durable} of {self.provisions_total}",
            f"rules admitted               {self.rules_admitted} of {self.proposals_total}",
            f"  planted errors caught      {self.planted_caught[0]} of {self.planted_caught[1]}",
            f"  genuine proposals refused  {self.genuine_refused[0]} of {self.genuine_refused[1]}",
        )


def standing(g: Graph, field_ref: str) -> Standing:
    node = f"field:{field_ref}"
    if g.into(node, EdgeKind.GOVERNS):
        return Standing.GOVERNED
    if g.into(node):
        return Standing.READ_AS_CONDITION
    return Standing.UNGOVERNED


def coverage(g: Graph, adj: Adjudication, provisions: ProvisionSet,
             fields: FieldSet) -> Coverage:
    governed = read = ungoverned = 0
    for f in fields.fields:
        s = standing(g, f.ref)
        governed += s is Standing.GOVERNED
        read += s is Standing.READ_AS_CONDITION
        ungoverned += s is Standing.UNGOVERNED

    cited = {e.dst for e in g.edges if e.kind in (EdgeKind.CITES, EdgeKind.REFERS_TO)}
    return Coverage(
        surface_total=fields.surface_total,
        labelled_total=len(fields),
        label_rule=fields.label_rule.value,
        fields_governed=governed,
        fields_read=read,
        fields_ungoverned=ungoverned,
        provisions_total=len(provisions),
        provisions_cited=len(cited & {n.id for n in g.by_kind(NodeKind.PROVISION)}),
        provisions_durable=provisions.durable_count,
        rules_admitted=len(adj.admitted),
        proposals_total=len(adj.verdicts),
        planted_caught=adj.planted_caught(),
        genuine_refused=adj.genuine_refused(),
        attestation_fields=sum(1 for f in fields.fields if f.asks is Asks.ATTESTATION),
    )
