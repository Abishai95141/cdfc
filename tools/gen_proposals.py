#!/usr/bin/env python
"""C3 — GENERATE the proposals file the driver reads. LAYER 2, wired at last.

    DEEPSEEK_API_KEY=... python tools/gen_proposals.py \
        --instrument statute-fm-regulations-2025 --template <blank.xlsx> --out <proposals.json>

## Why this tool exists

`cdfc.model` was ORPHANED: nothing under `src/` imported it. The proposals `cdfc evidence` read
were **hand-written** (`fixtures/evidence/fme-proposals.json`, 11 rows), so the sentence *"maps
them directly against statutory rules"* was true of a fixture and of nothing else.

This closes it, and it closes it **through the seam the architecture already has** rather than
around it. The model writes a FILE; `cdfc.evidence.run(proposals=Path)` reads the file; the five
gates adjudicate. Nothing on the verdict path calls a provider, because nothing on the verdict path
calls anything — it reads data.

## Chunking, and why the denominator survives it

532 `shall`-bearing provisions against 132 labelled fields does not fit in one context. Provisions
are sent in batches; **every batch sees ALL the fields**, because a rule may bind to any field and
a batch that saw half the surface would produce a proposal set whose denominator nobody could
state. `provisions_offered` is summed across batches and published, so the attrition funnel starts
from a number that is true.

A batch that fails is **counted as a failed batch**, never as a batch that proposed nothing —
`ProposerError` is the whole reason `_call` exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evidence.fields import from_template  # noqa: E402
from cdfc.evidence.provisions import from_divisions, from_instrument  # noqa: E402
from cdfc.model.propose import SYSTEM, ProposerError, propose  # noqa: E402
from cdfc.model.transport import DEEPSEEK_MODEL, deepseek  # noqa: E402
from cdfc.qualify.instruments import InstrumentStore  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--template", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--only-with", default="shall")
    ap.add_argument("--coordinate", action="store_true",
                    help="offer page-and-sentence eIds instead of durable ones")
    ap.add_argument("--batch", type=int, default=40)
    ap.add_argument("--max-batches", type=int, default=0, help="0 = every batch")
    ap.add_argument("--model", default=DEEPSEEK_MODEL)
    a = ap.parse_args()

    it = InstrumentStore().get(a.instrument)
    # DURABLE BY DEFAULT. A model asked to cite `p0146.s0013` is being asked to cite the
    # rendering; asked to cite `div1_0002__sub_0002` it cites the law, and the citation
    # survives re-extraction.
    pv = (from_instrument if a.coordinate else from_divisions)(it, only_with=a.only_with)
    fs = from_template(a.template)

    provisions = [(p.eid, p.text) for p in pv.provisions if p.text.strip()]
    fields = [(f.ref, f.label) for f in fs.fields if str(f.label).strip()]
    if not provisions or not fields:
        print(f"FAIL: {len(provisions)} provision(s), {len(fields)} field(s) — nothing to offer.")
        return 1

    batches = [provisions[i:i + a.batch] for i in range(0, len(provisions), a.batch)]
    if a.max_batches:
        batches = batches[:a.max_batches]

    transport = deepseek(model=a.model)
    rows: list[dict] = []
    offered = 0
    raw_blocks = 0
    malformed: list[str] = []
    failed: list[str] = []

    print(f"{a.instrument}  ->  {a.template.name}")
    print(f"  provisions {len(provisions)} (only_with={a.only_with!r}, addressing={pv.eid_kind.value}, durable {pv.durable_count})  fields {len(fields)}")
    print(f"  {len(batches)} batch(es) of {a.batch}, every batch sees ALL {len(fields)} fields\n")

    for i, batch in enumerate(batches, start=1):
        try:
            ps = propose(batch, fields, model=a.model, transport=transport)
        except ProposerError as exc:
            # A FAILED BATCH IS NOT AN EMPTY BATCH.
            failed.append(f"batch {i}: {exc}")
            print(f"  batch {i:>2}/{len(batches)}  FAILED  {str(exc)[:80]}")
            continue
        offered += ps.provisions_offered
        raw_blocks += ps.raw_blocks
        malformed.extend(f"batch {i}: {m}" for m in ps.malformed)
        rows.extend(ps.as_evidence_rows())
        print(f"  batch {i:>2}/{len(batches)}  {len(ps.proposals):>3} proposal(s)"
              f"  raw {ps.raw_blocks}  malformed {len(ps.malformed)}")

    # THE PROPOSAL SET IS A PINNED ARTEFACT, and it has to be, because THE MODEL IS NOT
    # REPRODUCIBLE.
    #
    # Measured 20 Aug 2026: two runs of `tools/e2e_matrix.py` over IDENTICAL inputs at
    # `temperature=0` gave ALR_V2_3 9 proposals then 2, ITFS_Monthly 11 then 0, AL_monthly 0 then
    # 10, Quarterly_CMI 19 then 42. `deepseek-v4-flash` is a reasoning model and its sampling is
    # not pinned by the temperature parameter.
    #
    # **Nothing here can make the model deterministic, and pretending otherwise would be worse
    # than the non-determinism.** What CAN be made reproducible is the SYSTEM: generation is a
    # BUILD step whose output is content-addressed, and a run names the digest of the proposal set
    # it used. The same digest re-derives the same adjudication, for ever. This is exactly how an
    # instrument is pinned, and for the same reason.
    #
    # The sidecar records what produced these bytes so a later reader can tell a re-generation
    # from a re-run: a DIFFERENT digest under the same inputs is the model moving, not us.
    a.out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(rows, indent=1, ensure_ascii=False)
    a.out.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    side = a.out.with_suffix(".provenance.json")
    side.write_text(json.dumps({
        "proposals_sha256": digest,
        "model": a.model,
        "instrument": a.instrument,
        "instrument_sha256": it.sha256,
        "template": a.template.name,
        "template_sha256": fs.template_sha256,
        "addressing": pv.eid_kind.value,
        "only_with": a.only_with,
        "provisions_offered": offered,
        "batch_size": a.batch,
        "prompt_sha256": hashlib.sha256(SYSTEM.encode("utf-8")).hexdigest(),
        "raw_blocks": raw_blocks,
        "malformed": len(malformed),
        "batches_failed": len(failed),
        "reproducible": False,
        "why": ("the model is not reproducible: two runs over identical inputs at temperature=0 "
                "produced materially different proposal counts. This artefact is pinned so the "
                "RUN is re-derivable even though the GENERATION is not."),
    }, indent=1), encoding="utf-8")
    print(f"  proposals sha256     {digest[:32]}…")
    print(f"  provenance           {side.name}")

    print(f"\n  provisions offered   {offered}")
    print(f"  raw blocks           {raw_blocks}")
    print(f"  malformed            {len(malformed)}")
    for m in malformed[:5]:
        print(f"      {m}")
    print(f"  batches FAILED       {len(failed)} of {len(batches)}"
          f"   (a failed batch is not a batch that proposed nothing)")
    print(f"  proposals written    {len(rows)}  ->  {a.out}")
    return 1 if failed and not rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
