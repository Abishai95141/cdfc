#!/usr/bin/env python
"""THE USER FLOW, run end to end on the IFSCA corpus and blank. Nothing mocked.

    python tools/user_flow.py

Walks the product's own sentence, one stage per section, and prints what a filer would see. Every
number is computed here from real artefacts: the vendored IFSCA blank, the pinned FM Regulations
2025, a custodian register and a trial balance, and the pinned FinCEN PDF as a prose source.

**A stage that does not work prints what it did instead.** The point of this script is to find out
whether the flow runs, not to show that it does.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.correspond.link import Comparison, exact  # noqa: E402
from cdfc.evidence.entities import records_from_rows, resolve  # noqa: E402
from cdfc.evidence.fields import from_template, select_rule  # noqa: E402
from cdfc.evidence.gates import adjudicate  # noqa: E402
from cdfc.evidence.graph import build as build_graph  # noqa: E402
from cdfc.evidence.proposal import load as load_proposals  # noqa: E402
from cdfc.evidence.provisions import from_divisions, from_instrument  # noqa: E402
from cdfc.fill.pipeline import run as fill_run  # noqa: E402
from cdfc.ingest.tabular import header_and_rows  # noqa: E402
from cdfc.qualify.instruments import InstrumentStore  # noqa: E402
from cdfc.registry import ArtefactKind, Registry  # noqa: E402

BLANK = REPO / ("fixtures/prescribed/"
                "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
STATUTE = "statute-fm-regulations-2025"
PROPOSALS = REPO / "fixtures/evidence/fme-proposals-generated.json"

CUSTODIAN = b"""PAN of FME,Name of the FME,Legal structure,Contact person
AAACI1234K,Meridian Capital IFSC Ltd,Company,Asha Rao
AAACX9999Z,Northbank Asset Managers,Limited Liability Partnership,R Iyer
"""
TRIAL_BALANCE = b"""PAN of FME,Contact person,Email
AAACI1234K,Asha  Rao,asha.rao@meridian.example
AAACX9999Z,R Iyer,iyer@northbank.example
"""
SUBJECT = {"PAN of FME": "AAACI1234K"}


def head(n: int, title: str) -> None:
    print(f"\n{'=' * 76}\n{n}. {title}\n{'=' * 76}")


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp())
    reg = Registry(tmp / "registry")
    ok: dict[str, bool] = {}

    head(1, "UPLOAD — raw exports, zero manual formatting")
    td = reg.put(BLANK.read_bytes(), kind=ArtefactKind.TEMPLATE, filename=str(BLANK)).digest
    c = reg.put(CUSTODIAN, kind=ArtefactKind.SOURCE, filename="custodian_register.csv").digest
    t = reg.put(TRIAL_BALANCE, kind=ArtefactKind.SOURCE, filename="trial_balance.csv").digest
    pdf_pin = REPO / "corpus/instruments/source-fincen-boir-instructions.text.json"
    p = (reg.put(pdf_pin.read_bytes(), kind=ArtefactKind.SOURCE, filename=pdf_pin.name).digest
         if pdf_pin.is_file() else None)
    print(f"   template  {td[:16]}…  {BLANK.name[:44]}")
    print(f"   source    {c[:16]}…  custodian_register.csv")
    print(f"   source    {t[:16]}…  trial_balance.csv")
    print(f"   source    {p[:16] if p else '—':<17}  {'a PDF, pinned at build time' if p else 'ABSENT'}")
    inputs = reg.inputs([td, c, t] + ([p] if p else []))
    print(f"   merkle root over THIS run's inputs  {inputs.merkle_root[:32]}…")
    ok["upload"] = True

    head(2, "RESOLVE + FUSE — one identity across two documents")
    hc, rc = header_and_rows(CUSTODIAN, delimiter=",")
    ht, rt = header_and_rows(TRIAL_BALANCE, delimiter=",")
    left = records_from_rows("custodian_register.csv", hc, rc)
    right = records_from_rows("trial_balance.csv", ht, rt)
    es = resolve(left, right, [Comparison(name="PAN of FME", agree=exact),
                       Comparison(name="Contact person", agree=exact)])
    cts = es.counts()
    print(f"   records {cts['records']} -> entities {cts['entities']}"
          f"   cross-document {cts['cross_document']}   refused {cts['refused']}")
    for e in es.cross_document():
        print(f"     {e.id[:58]:<58} documents {list(e.documents)}")
    ok["fuse"] = cts["cross_document"] >= 1

    head(3, "MAP — the statute, against the template")
    it = InstrumentStore().get(STATUTE)
    # THE PROPOSALS AND THE PROVISIONS MUST SHARE AN ADDRESS SPACE. `adjudicate` now refuses a
    # mismatch outright rather than refusing 172 proposals one at a time at G-QUOTE, so pick the
    # addressing the proposals file was WRITTEN in and say which it is.
    pv_durable = from_divisions(it, only_with="shall")
    pv = pv_durable
    if PROPOSALS.is_file():
        _p = load_proposals(PROPOSALS)
        known = {x.eid for x in pv_durable.provisions}
        if _p.proposals and not any(x.eid in known for x in _p.proposals):
            pv = from_instrument(it, only_with="shall")
            print(f"   proposals are COORDINATE-addressed ({_p.proposals[0].eid}); "
                  f"adjudicating against the coordinate provision set")
            print(f"   [durable set available: {len(pv_durable.provisions)} provisions, "
                  f"{pv_durable.durable_count} durable]")
    fs = from_template(BLANK, rule=select_rule(BLANK))
    print(f"   provisions {len(pv.provisions)}  durable {pv.durable_count} of {len(pv.provisions)}"
          f"   markers refused {len(pv.refused_markers)}")
    print(f"   field surface {fs.surface_total}   labelled {len(fs.fields)}"
          f"   refusal {fs.refusal.value if fs.refusal else 'none'}")
    if PROPOSALS.is_file():
        props = load_proposals(PROPOSALS)
        adj = adjudicate(props, pv, fs)
        g = build_graph(adj, pv, fs)
        kinds = {}
        for n in g.nodes:
            k = getattr(n, "kind", None)
            kinds[getattr(k, "value", str(k))] = kinds.get(getattr(k, "value", str(k)), 0) + 1
        print(f"   proposals {len(props.proposals)}  ADMITTED {len(adj.admitted)}"
              f"  refused {len(adj.refused)}")
        print(f"   graph {sum(kinds.values())} nodes {kinds}")
        ok["map"] = len(adj.admitted) > 0
    else:
        print(f"   NO PROPOSALS FILE at {PROPOSALS} — the mapping stage did not run")
        ok["map"] = False

    head(4, "POPULATE — a value in every cell we can evidence")
    fr = fill_run(reg, template_digest=td, source_digest=[c, t], template_path=BLANK,
                  subject=SUBJECT)
    d = fr.declaration
    dc = d.counts()
    print(f"   subject named            {SUBJECT}")
    print(f"   source columns matched   {len(fr.schema_match.pairs)}")
    print(f"   PROPOSED (evidenced)     {dc.get('proposed', 0)}")
    print(f"   DERIVED (no span)        {dc.get('derived', 0)}")
    print(f"   refused                  {dc.get('refused', 0)}")
    print(f"   attestations (a human signs) {dc.get('attestations', 0)}")
    print(f"   values a column offered that are NOT IN the source  {len(fr.unlocatable)}")
    ok["populate"] = dc.get("proposed", 0) > 0

    head(5, "WHAT NEEDS YOUR JUDGEMENT — the refusals, by reason")
    from collections import Counter
    reasons = Counter()
    for r in getattr(d, "refused", ()):
        reasons[str(getattr(r, "reason", "?"))] += 1
    for reason, n in reasons.most_common(6):
        print(f"   {n:>6}  {reason}")
    print(f"\n   Every refusal takes its reason from a CLOSED vocabulary. "
          f"{sum(reasons.values())} refusals, {len(reasons)} distinct reasons.")
    ok["explain"] = bool(reasons)

    print(f"\n{'=' * 76}\nSTAGE RESULTS\n{'=' * 76}")
    for k, v in ok.items():
        print(f"   {k:<10} {'WORKS' if v else 'DOES NOT WORK'}")
    return 0 if all(ok.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
