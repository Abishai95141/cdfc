#!/usr/bin/env python
"""Emit `web/data/state.json` — the REAL flow's output, for the surface to render.

    python tools/build_frontend_data.py

The surface renders a snapshot rather than calling the pipeline in a request handler, for the same
reason the graph is a projection: a screen that recomputes is a screen that can disagree with the
run it claims to show. Every number here is produced by the same functions `tools/user_flow.py`
runs, over the vendored IFSCA blank and the pinned FM Regulations 2025.

**Nothing in this file invents a number.** A stage that cannot run writes its refusal into the
snapshot, and the surface renders the refusal.
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.correspond.link import Comparison, exact  # noqa: E402
from cdfc.evidence.entities import records_from_rows, resolve  # noqa: E402
from cdfc.evidence.fields import from_template, select_rule  # noqa: E402
from cdfc.evidence.gates import adjudicate  # noqa: E402
from cdfc.evidence.graph import build as build_graph  # noqa: E402
from cdfc.evidence.proposal import load as load_proposals  # noqa: E402
from cdfc.evidence.provisions import from_divisions, from_instrument  # noqa: E402
from cdfc.evidence.query import coverage  # noqa: E402
from cdfc.fill.pipeline import run as fill_run  # noqa: E402
from cdfc.ingest.tabular import header_and_rows  # noqa: E402
from cdfc.qualify.instruments import InstrumentStore  # noqa: E402
from cdfc.registry import ArtefactKind, Registry  # noqa: E402

BLANK = REPO / ("fixtures/prescribed/"
                "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
STATUTE = "statute-fm-regulations-2025"
PROPOSALS = REPO / "fixtures/evidence/fme-proposals-generated.json"
PDF_PIN = REPO / "corpus/instruments/source-fincen-boir-instructions.text.json"
OUT = REPO / "web/data/state.json"

CUSTODIAN = b"""PAN of FME,Name of the FME,Legal structure,Contact person
AAACI1234K,Meridian Capital IFSC Ltd,Company,Asha Rao
AAACX9999Z,Northbank Asset Managers,Limited Liability Partnership,R Iyer
"""
TRIAL_BALANCE = b"""PAN of FME,Contact person,Email
AAACI1234K,Asha  Rao,asha.rao@meridian.example
AAACX9999Z,R Iyer,iyer@northbank.example
"""
SUBJECT = {"PAN of FME": "AAACI1234K"}


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp())
    reg = Registry(tmp / "registry")
    state: dict = {"generated_from": "tools/build_frontend_data.py", "stages": {}}

    # 1 INTAKE ---------------------------------------------------------------------------------
    arts = []
    td = reg.put(BLANK.read_bytes(), kind=ArtefactKind.TEMPLATE, filename=BLANK.name)
    arts.append({"digest": td.digest, "kind": "template", "name": BLANK.name,
                 "bytes": len(BLANK.read_bytes())})
    c = reg.put(CUSTODIAN, kind=ArtefactKind.SOURCE, filename="custodian_register.csv")
    arts.append({"digest": c.digest, "kind": "source", "name": "custodian_register.csv",
                 "bytes": len(CUSTODIAN)})
    t = reg.put(TRIAL_BALANCE, kind=ArtefactKind.SOURCE, filename="trial_balance.csv")
    arts.append({"digest": t.digest, "kind": "source", "name": "trial_balance.csv",
                 "bytes": len(TRIAL_BALANCE)})
    p = None
    if PDF_PIN.is_file():
        p = reg.put(PDF_PIN.read_bytes(), kind=ArtefactKind.SOURCE, filename=PDF_PIN.name)
        arts.append({"digest": p.digest, "kind": "source", "name": "FinCEN BOIR (PDF, pinned)",
                     "bytes": len(PDF_PIN.read_bytes())})
    digests = [td.digest, c.digest, t.digest] + ([p.digest] if p else [])
    state["stages"]["intake"] = {
        "artefacts": arts, "merkle_root": reg.inputs(digests).merkle_root}

    # 2 FUSE -----------------------------------------------------------------------------------
    hc, rc = header_and_rows(CUSTODIAN, delimiter=",")
    ht, rt = header_and_rows(TRIAL_BALANCE, delimiter=",")
    es = resolve(records_from_rows("custodian_register.csv", hc, rc),
                 records_from_rows("trial_balance.csv", ht, rt),
                 [Comparison(name="PAN of FME", agree=exact),
                  Comparison(name="Contact person", agree=exact)])
    state["stages"]["fuse"] = {
        "counts": es.counts(),
        "entities": [e.as_canonical_obj() for e in es.entities],
        "refused": [{"record": r, "reason": why, "detail": d} for r, why, d in es.refused],
    }

    # 3 MAP ------------------------------------------------------------------------------------
    it = InstrumentStore().get(STATUTE)
    fs = from_template(BLANK, rule=select_rule(BLANK))
    pv_d = from_divisions(it, only_with="shall")
    mapping: dict = {"template": BLANK.name, "surface_total": fs.surface_total,
                     "labelled": len(fs.fields),
                     "template_refusal": fs.refusal.value if fs.refusal else None,
                     "durable_available": pv_d.durable_count,
                     "markers_refused": [{"eid": e, "why": w} for e, w in pv_d.refused_markers]}
    if PROPOSALS.is_file():
        props = load_proposals(PROPOSALS)
        known = {x.eid for x in pv_d.provisions}
        pv = pv_d if any(x.eid in known for x in props.proposals) else from_instrument(
            it, only_with="shall")
        mapping["addressing"] = pv.eid_kind.value
        adj = adjudicate(props, pv, fs)
        g = build_graph(adj, pv, fs)
        cov = coverage(g, adj, pv, fs)
        kinds = Counter(getattr(getattr(n, "kind", None), "value", "?") for n in g.nodes)
        mapping.update(
            provisions=len(pv.provisions), proposals=len(props.proposals),
            admitted=len(adj.admitted), refused=len(adj.refused),
            fields_governed=cov.fields_governed, labelled_total=cov.labelled_total,
            provisions_cited=cov.provisions_cited, provisions_durable=cov.provisions_durable,
            graph_nodes=dict(kinds), graph_edges=len(g.edges),
            rules=[{"eid": v.proposal.eid, "field": v.proposal.field_ref,
                    "kind": v.proposal.kind.value, "quote": v.proposal.quote[:220]}
                   for v in adj.admitted[:40]],
            gate_refusals=[{"eid": v.proposal.eid,
                            "gates": [{"gate": gname, "reason": str(getattr(r, "value", r)),
                                       "detail": det} for gname, r, det in v.refusals]}
                           for v in adj.refused[:30]],
        )
    state["stages"]["map"] = mapping

    # 4 RETURN + 5 JUDGEMENT -------------------------------------------------------------------
    fr = fill_run(reg, template_digest=td.digest, source_digest=[c.digest, t.digest],
                  template_path=BLANK, subject=SUBJECT)
    d = fr.declaration
    reasons = Counter(str(getattr(r, "reason", "?")) for r in getattr(d, "refused", ()))
    state["stages"]["return"] = {
        "subject": SUBJECT, "counts": d.counts(),
        "columns_matched": len(fr.schema_match.pairs),
        "merkle_root": fr.merkle_root,
        # NO `getattr(x, name, default)` HERE. `FillProposal` carries document/span/page/context
        # DIRECTLY -- there is no `.observation` -- and reading a nested attribute that does not
        # exist produced a provenance column of em-dashes on every row, which is the whole product
        # rendered as absent. The same default trap emptied the e2e matrix's `governed` column the
        # same day. A serializer must read the real attribute and fail loudly if it moves.
        "proposed": [{"field": x.ref, "value": str(x.value), "label": str(x.label),
                      "document": x.document, "span": list(x.span), "page": x.page,
                      "context": str(x.context)[:180],
                      "conditions": [{"name": c.name, "holds": bool(c.holds),
                                      "detail": str(c.detail)[:140]} for c in x.conditions]}
                     for x in d.proposed],
        "derived": [{"field": x.ref, "value": str(x.value), "label": str(x.label),
                     "why": str(getattr(x, "why", "") or getattr(x, "detail", ""))}
                    for x in d.derived],
        "attestations": [{"field": x.ref, "label": str(x.label)} for x in d.attestations],
        "unlocatable": [{"field": f, "value": v} for f, v in fr.unlocatable[:30]],
    }
    state["stages"]["judgement"] = {
        "by_reason": [{"reason": k, "count": v} for k, v in reasons.most_common()],
        "total": sum(reasons.values()),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}  ({OUT.stat().st_size:,} bytes)")
    for name, st in state["stages"].items():
        keys = ", ".join(f"{k}={v}" for k, v in list(st.items())[:1])
        print(f"  {name:<10} {keys[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
