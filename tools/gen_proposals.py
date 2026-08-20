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
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evidence.fields import from_template  # noqa: E402
from cdfc.evidence.provisions import from_instrument  # noqa: E402
from cdfc.model.propose import ProposerError, propose  # noqa: E402
from cdfc.model.transport import DEEPSEEK_MODEL, deepseek  # noqa: E402
from cdfc.qualify.instruments import InstrumentStore  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--template", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--only-with", default="shall")
    ap.add_argument("--batch", type=int, default=40)
    ap.add_argument("--max-batches", type=int, default=0, help="0 = every batch")
    ap.add_argument("--model", default=DEEPSEEK_MODEL)
    a = ap.parse_args()

    it = InstrumentStore().get(a.instrument)
    pv = from_instrument(it, only_with=a.only_with)
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
    print(f"  provisions {len(provisions)} (only_with={a.only_with!r})  fields {len(fields)}")
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

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")

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
