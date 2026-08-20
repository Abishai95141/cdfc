"""The driver: instrument + template + proposals -> adjudication -> graph -> declaration.

One function, so the flow is readable in one screen and so there is exactly one place where the
order of the layers is decided.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cdfc.evidence.fields import FieldSet, LabelRule, from_template
from cdfc.evidence.gates import Adjudication, adjudicate
from cdfc.evidence.graph import Graph, build
from cdfc.evidence.proposal import ProposalSet, load
from cdfc.evidence.provisions import ProvisionSet, from_divisions, from_instrument
from cdfc.evidence.query import Coverage, coverage
from cdfc.qualify.instruments import InstrumentStore


@dataclass(frozen=True, slots=True)
class EvidenceRun:
    provisions: ProvisionSet
    fields: FieldSet
    proposals: ProposalSet
    adjudication: Adjudication
    graph: Graph
    coverage: Coverage

    def report(self) -> str:
        head = (
            f"instrument   {self.provisions.instrument_id}  "
            f"({self.provisions.instrument_sha256[:12]}…)",
            f"template     {self.fields.template_sha256[:12]}…",
            f"proposals    {self.proposals.source}",
            f"graph        {sum(self.graph.counts().values())} nodes "
            f"{self.graph.counts()} · {len(self.graph.edges)} edges",
            "",
        )
        body = list(self.coverage.lines())
        if self.adjudication.refused:
            body += ["", "REFUSED, with the gate that decided it:"]
            for v in self.adjudication.refused:
                tag = f"[planted: {v.proposal.planted}]" if v.proposal.is_planted else "[genuine]"
                body.append(f"  {v.proposal.eid:16} {tag}")
                for gate, reason, detail in v.refusals:
                    body.append(f"      {gate:8} {reason.value}: {detail}")
        return "\n".join([*head, *body])


def run(
    *,
    instrument_id: str,
    template: Path,
    proposals: Path,
    only_with: str | None = None,
    label_rule: LabelRule = LabelRule.ADJACENT_LEFT,
    store: InstrumentStore | None = None,
    durable: bool = False,
) -> EvidenceRun:
    it = (store or InstrumentStore()).get(instrument_id)
    # DURABLE addressing cites the instrument's own numbering (`div1_0002__sub_0002`); COORDINATE
    # cites page-and-sentence (`p0146.s0013`), which moves on re-extraction. The choice is the
    # caller's and it is RECORDED on every provision as `eid_kind`, so a reader can tell a durable
    # citation from a fragile one without reading this docstring.
    provs = (from_divisions if durable else from_instrument)(it, only_with=only_with)
    flds = from_template(template, rule=label_rule)
    props = load(proposals)
    adj = adjudicate(props, provs, flds)
    g = build(adj, provs, flds)
    return EvidenceRun(
        provisions=provs, fields=flds, proposals=props,
        adjudication=adj, graph=g, coverage=coverage(g, adj, provs, flds),
    )
