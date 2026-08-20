#!/usr/bin/env python
"""B2's FUNCTIONALITY CHECK. `make demo-fuse`.

Binds TWO source documents to the regulator's blank in ONE run and proves:

  1. both documents are bound in one run, and BOTH contribute values;
  2. every evidenced observation re-verifies byte-exact IN ITS OWN document;
  3. the fill count rises from B1's 1, and the number is recorded rather than asserted;
  4. the declaration still closes across four lanes;
  5. the written return still changes nothing but the cells it names.

Exit 0 only if all five hold. Prints the numbers either way.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.fill.pipeline import run                                     # noqa: E402
from cdfc.fill.write import verify_written, write, written_values      # noqa: E402
from cdfc.ingest.tabular import read_delimited                         # noqa: E402
from cdfc.registry import ArtefactKind, Registry                       # noqa: E402

BLANK = REPO / ("fixtures/prescribed/"
                "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")

# TWO documents an FME actually holds, with columns the return actually asks for. The first demo
# source asked for net worth, AUM and investor counts — NONE of which this return has a field for:
# it asks whether the requirements were COMPLIED WITH. A binder cannot fill a field that is absent,
# and measuring one against a source pack the return never asks for measures nothing.
ENTITY = (b"Category of Registration of FME,Legal Structure of FME,"
          b"Date of Registration of FME,PAN of FME,Address of FME\n"
          b"Registered FME (Retail),Company,2025-04-01,AABCF1234K,"
          b"Unit 402 GIFT City Gandhinagar\n")
OFFICERS = (b"Name of the Principal Officer,Email address of the Principal Officer,"
            b"Contact no. of the Principal Officer,Name of the Compliance Officer,"
            b"Email address of the Compliance Officer\n"
            b"Asha Rao,asha.rao@example.com,+91 79 4000 1234,Vikram Shah,"
            b"vikram.shah@example.com\n")

B1_FILLED = 1          # what B1 achieved on one source with the polluted binder


def main() -> int:
    if not BLANK.is_file():
        print(f"REFUSED: {BLANK.relative_to(REPO)} is absent.")
        return 1
    fail: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        reg = Registry(root=tmpd / "registry")
        t = reg.put_file(BLANK, kind=ArtefactKind.TEMPLATE)
        a = reg.put(ENTITY, kind=ArtefactKind.SOURCE, filename="entity-master.csv")
        b = reg.put(OFFICERS, kind=ArtefactKind.SOURCE, filename="officers-register.csv")

        t0 = time.time()
        r = run(reg, template_digest=t.digest, source_digest=[a.digest, b.digest],
                template_path=BLANK)
        dt = time.time() - t0
        c = r.declaration.counts()

        print("=" * 76)
        print("B2 · two documents, one run, one return")
        print("=" * 76)
        print(f"  sources bound    {len(r.source_digests)}   "
              f"{[d[:12] + '…' for d in r.source_digests]}")
        print(f"  merkle root      {r.merkle_root[:16]}…")
        print(f"  columns offered  {r.schema_match.columns}")
        print(f"  MATCHED          {len(r.schema_match.pairs)} of {r.schema_match.columns}"
              f"   refused {len(r.schema_match.refused)}")
        print(f"  wall clock       {dt:.2f}s")

        print("\n  CHECK 1 — both documents contribute")
        contributing = {p.document for p in r.declaration.admitted()} | {
            d.supported_by[0] for d in r.declaration.derived if d.supported_by}
        for d in sorted(contributing):
            print(f"    {d}")
        if len(contributing) < 2:
            fail.append(f"only {len(contributing)} document(s) contributed; a source was dropped")

        print("\n  CHECK 2 — every evidenced span re-verifies IN ITS OWN document")
        texts = {f"source:{a.digest[:12]}": read_delimited(
                     ENTITY, instrument_id=f"source:{a.digest[:12]}"),
                 f"source:{b.digest[:12]}": read_delimited(
                     OFFICERS, instrument_id=f"source:{b.digest[:12]}")}
        for p in r.declaration.admitted():
            src = texts.get(p.document)
            ok = src is not None and src.text[p.span[0]:p.span[1]] == p.value
            print(f"    {'OK ' if ok else 'BAD'} {p.ref:26} {str(p.span):>12}  {p.document}")
            if not ok:
                fail.append(f"{p.ref} does not re-verify in {p.document}")

        print(f"\n  CHECK 3 — the fill count, recorded not asserted")
        print(f"    evidenced        {c['admitted']}")
        print(f"    derived          {c['derived']}")
        print(f"    FILLED           {c['filled_total']}   (B1 achieved {B1_FILLED})")
        if c["filled_total"] <= B1_FILLED:
            fail.append(f"filled {c['filled_total']}, no better than B1's {B1_FILLED}")

        print("\n  CHECK 4 — the declaration closes across four lanes")
        total = c["proposed"] + c["refused"] + c["attestations"] + c["derived"]
        print(f"    {c['proposed']} proposed + {c['refused']} refused + "
              f"{c['attestations']} attestations + {c['derived']} derived = {total}"
              f"  over {c['surface_total']}")
        if total != c["surface_total"]:
            fail.append("the declaration does not close")

        out = tmpd / "filled.xlsx"
        rec = write(r.declaration, BLANK, out)
        v = verify_written(BLANK, out, rec, expect_validations=19)
        print("\n  CHECK 5 — the written return changes only what it names")
        print(f"    parts            {v['parts_before']} -> {v['parts_after']}")
        print(f"    x14 validations  {v['x14_validations_before']} -> "
              f"{v['x14_validations_after']}")
        print(f"    cells changed    {v['cells_changed']}   named {v['cells_named']}")
        if v["cells_changed"] != v["cells_named"] or v["parts_before"] != v["parts_after"]:
            fail.append("the written return changed something it did not name")

        print("\n  THE RETURN, as written:")
        got = written_values(out, [x.ref for x in rec.cells])
        for x in rec.cells:
            print(f"    [{x.lane:9}] {x.ref:26} = {got.get(x.ref)!r}")

        keep = REPO / "reports/demo-fuse"
        keep.mkdir(parents=True, exist_ok=True)
        import shutil

        shutil.copy(out, keep / "filled.xlsx")
        (keep / "fuse-record.json").write_text(json.dumps({
            "sources": list(r.source_digests), "merkle_root": r.merkle_root,
            "columns": r.schema_match.columns, "matched": len(r.schema_match.pairs),
            "declaration": c, "verify": v,
            "cells": [{"ref": x.ref, "value": x.value, "lane": x.lane, "document": x.document,
                       "span": list(x.span) if x.span else None} for x in rec.cells],
        }, indent=1), encoding="utf-8")
        print(f"\n  wrote reports/demo-fuse/filled.xlsx and fuse-record.json")

    print("\n" + "=" * 76)
    if fail:
        print(f"DEMO-FUSE FAILED — {len(fail)} check(s):")
        for f in fail:
            print(f"  * {f}")
        return 1
    print("DEMO-FUSE PASSED — all five checks.")
    print("  NOT shown: an ENTITY node. Cross-document entity RESOLUTION — one entity appearing")
    print("  in both sources resolving to one node — is not built; this fuses FIELDS, not")
    print("  entities. And no filled value is claimed CORRECT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
