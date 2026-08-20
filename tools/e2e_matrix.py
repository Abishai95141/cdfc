#!/usr/bin/env python
"""C5 — the whole flow, over EVERY template, with the failures in the table.

    DEEPSEEK_API_KEY=... python tools/e2e_matrix.py [--batches 2]

One row per template. A template that refuses gets a row saying why; a template that produces no
admitted rule gets a row saying that. **A matrix that only lists what worked is a demo, not a
measurement** — the point of running nine is to find out on how many it does not work.

    statute -> divisions (durable eIds)
            -> model proposes rule->field bindings, AS DATA
            -> five gates adjudicate
            -> graph + coverage over a denominator that is not arguable

The model is called ONCE PER TEMPLATE, because the fields differ; the provisions do not, so the
same `shall`-bearing division set is offered every time and `provisions_offered` is comparable
across rows.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evidence.fields import from_template, select_rule  # noqa: E402
from cdfc.evidence.gates import adjudicate  # noqa: E402
from cdfc.evidence.graph import build  # noqa: E402
from cdfc.evidence.proposal import parse as evidence_parse  # noqa: E402
from cdfc.evidence.provisions import from_divisions  # noqa: E402
from cdfc.evidence.query import coverage  # noqa: E402
from cdfc.model.propose import ProposerError, propose  # noqa: E402
from cdfc.model.transport import DEEPSEEK_MODEL, deepseek  # noqa: E402
from cdfc.qualify.instruments import InstrumentStore  # noqa: E402

INSTRUMENT = "statute-fm-regulations-2025"
BLANKS = sorted((REPO / "fixtures/prescribed").glob("*.xlsx"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--batches", type=int, default=2)
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--out", type=pathlib.Path, default=REPO / "reports/e2e-matrix.json")
    a = ap.parse_args()

    it = InstrumentStore().get(INSTRUMENT)
    pv = from_divisions(it, only_with="shall")
    provisions = [(p.eid, p.text) for p in pv.provisions if p.text.strip()]
    batches = [provisions[i:i + a.batch] for i in range(0, len(provisions), a.batch)][:a.batches]
    transport = deepseek()

    print(f"instrument {INSTRUMENT}  provisions {len(provisions)} "
          f"({pv.durable_count} durable, {len(pv.refused_markers)} markers refused)")
    print(f"offering {len(batches)} batch(es) of {a.batch} to each of {len(BLANKS)} template(s)\n")
    hdr = f"{'template':<44} {'surface':>7} {'lab':>5} {'prop':>5} {'adm':>4} {'gov':>5}  state"
    print(hdr); print("-" * len(hdr))

    rows = []
    for blank in BLANKS:
        fs = from_template(blank, rule=select_rule(blank))
        row = {"template": blank.name, "surface": fs.surface_total,
               "labelled": len(fs.fields), "proposals": 0, "admitted": 0, "governed": 0}
        if fs.refusal is not None:
            row["state"] = f"REFUSED {fs.refusal.value}"
            rows.append(row)
            print(f"{blank.name[:42]:<44} {fs.surface_total:>7} {len(fs.fields):>5} "
                  f"{'-':>5} {'-':>4} {'-':>5}  {row['state']}")
            continue

        fields = [(f.ref, f.label) for f in fs.fields if str(f.label).strip()]
        if not fields:
            row["state"] = "no labelled field to offer"
            rows.append(row); print(f"{blank.name[:42]:<44} {fs.surface_total:>7} "
                                    f"{len(fs.fields):>5} {'-':>5} {'-':>4} {'-':>5}  {row['state']}")
            continue

        evidence_rows, failed = [], 0
        for batch in batches:
            try:
                ps = propose(batch, fields, model=DEEPSEEK_MODEL, transport=transport)
            except ProposerError:
                failed += 1
                continue
            evidence_rows.extend(ps.as_evidence_rows())
        try:
            props = evidence_parse(evidence_rows, source=blank.name)
            adj = adjudicate(props, pv, fs)
            g = build(adj, pv, fs)
            cov = coverage(g, adj, pv, fs)
            # NO `getattr(..., default)` IN A MEASUREMENT HARNESS.
            #
            # The first version read `getattr(cov, "governed", 0)`. The attribute is
            # `fields_governed`, so every row reported governed=0 and the column read as "this
            # flow governs nothing" across nine templates. The real number for the FME blank is
            # 30. A getattr with a default never fails; it just publishes a falsehood, which is
            # the same shape as a count nobody opened.
            row.update(proposals=len(props.proposals), admitted=len(adj.admitted),
                       governed=cov.fields_governed, labelled_total=cov.labelled_total,
                       provisions_cited=cov.provisions_cited,
                       state=f"ok ({failed} batch fail)" if failed else "ok")
        except Exception as exc:                                    # noqa: BLE001
            row["state"] = f"ERROR {type(exc).__name__}: {str(exc)[:40]}"
        rows.append(row)
        print(f"{blank.name[:42]:<44} {row['surface']:>7} {row['labelled']:>5} "
              f"{row['proposals']:>5} {row['admitted']:>4} {row['governed']:>5}  {row['state']}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    ok = [r for r in rows if str(r.get("state", "")).startswith("ok")]
    admitted = [r for r in ok if r["admitted"] > 0]
    print(f"\n  templates             {len(rows)}")
    print(f"  ran end to end        {len(ok)} of {len(rows)}")
    print(f"  admitted >= 1 rule    {len(admitted)} of {len(rows)}")
    print(f"  refused with a reason {sum(1 for r in rows if 'REFUSED' in str(r.get('state')))}"
          f" of {len(rows)}")
    print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
