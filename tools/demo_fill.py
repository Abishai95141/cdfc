#!/usr/bin/env python
"""B1's FUNCTIONALITY CHECK. `make demo-fill`.

Fills the REAL vendored IFSCA blank from a source pack and proves, on the artefact rather than on
a record, that:

  1. every XML part re-parses and no zip entry is corrupt;
  2. the part list is IDENTICAL before and after;
  3. all 19 `x14` data validations survive, COUNTED BY PARSING;
  4. every cell the declaration named holds its value, READ BACK OUT OF THE FILE;
  5. no cell the declaration did not name has changed, over every sheet.

Exit 0 only if all five hold. Prints the numbers either way, because a check that says only
"passed" is a check nobody can audit.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.fill.pipeline import run                                    # noqa: E402
from cdfc.fill.write import _count_x14, verify_written, write, written_values  # noqa: E402
from cdfc.ingest.xmlsafe import fromstring                            # noqa: E402
from cdfc.registry import ArtefactKind, Registry                      # noqa: E402

BLANK = REPO / ("fixtures/prescribed/"
                "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
SOURCE = (b"Category of Registration of FME,Net worth,Number of investors\n"
          b"Registered FME (Retail),750000,1284\n")


def main() -> int:
    if not BLANK.is_file():
        print(f"REFUSED: {BLANK.relative_to(REPO)} is absent.")
        return 1
    fail: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        reg = Registry(root=tmpd / "registry")
        t = reg.put_file(BLANK, kind=ArtefactKind.TEMPLATE)
        s = reg.put(SOURCE, kind=ArtefactKind.SOURCE, filename="custodian-feed-2026Q1.csv")

        t0 = time.time()
        r = run(reg, template_digest=t.digest, source_digest=s.digest, template_path=BLANK)
        out = tmpd / "filled.xlsx"
        rec = write(r.declaration, BLANK, out)
        dt = time.time() - t0

        print("=" * 74)
        print("B1 · fill the regulator's own blank, and change nothing else")
        print("=" * 74)
        for line in rec.lines():
            print(f"  {line}")
        print(f"  wall clock       {dt:.2f}s")

        v = verify_written(BLANK, out, rec, expect_validations=19)
        print("\n  CHECK 2/3/5 — parts, validations, cells")
        print(f"    parts            {v['parts_before']} -> {v['parts_after']}")
        print(f"    x14 validations  {v['x14_validations_before']} -> "
              f"{v['x14_validations_after']}   (parsed, not byte-counted)")
        print(f"    cells            {v['cells_before']} -> {v['cells_after']}")
        print(f"    cells changed    {v['cells_changed']}   named {v['cells_named']}")
        if v["parts_before"] != v["parts_after"]:
            fail.append("the part list changed")
        if v["x14_validations_after"] != 19:
            fail.append(f"x14 validations are {v['x14_validations_after']}, pinned at 19")
        if v["cells_changed"] != v["cells_named"]:
            fail.append("a cell changed that the declaration did not name")

        print("\n  CHECK 1 — the artefact opens and every part re-parses")
        with zipfile.ZipFile(out) as z:
            bad = z.testzip()
            xml = [n for n in z.namelist() if n.endswith(".xml")]
            for n in xml:
                try:
                    fromstring(z.read(n))
                except Exception as exc:                              # noqa: BLE001
                    fail.append(f"{n} does not re-parse: {type(exc).__name__}")
            print(f"    crc              {'OK' if bad is None else 'CORRUPT ' + bad}")
            print(f"    xml parts        {len(xml)} re-parsed")
            if bad is not None:
                fail.append(f"corrupt zip entry {bad}")

        print("\n  CHECK 4 — every named cell, READ BACK OUT OF THE FILE")
        got = written_values(out, [c.ref for c in rec.cells])
        for c in rec.cells:
            actual = got.get(c.ref)
            ok = actual == c.value
            print(f"    {'OK ' if ok else 'BAD'} {c.ref:32} = {actual!r}   [{c.lane}]")
            if not ok:
                fail.append(f"{c.ref} holds {actual!r}, declared {c.value!r}")

        keep = REPO / "reports/demo-fill"
        keep.mkdir(parents=True, exist_ok=True)
        shutil.copy(out, keep / "filled.xlsx")
        (keep / "write-record.json").write_text(json.dumps({
            "template_sha256": rec.template_sha256, "output_sha256": rec.output_sha256,
            "parts_changed": list(rec.parts_changed), "counts": rec.counts(),
            "verify": v,
            "cells": [{"ref": c.ref, "value": c.value, "lane": c.lane,
                       "document": c.document, "span": list(c.span) if c.span else None}
                      for c in rec.cells],
            "attestations_left_blank": list(rec.attestations_left_blank),
        }, indent=1), encoding="utf-8")
        print(f"\n  wrote reports/demo-fill/filled.xlsx and write-record.json")

    print("\n" + "=" * 74)
    if fail:
        print(f"DEMO-FILL FAILED — {len(fail)} check(s):")
        for f in fail:
            print(f"  * {f}")
        return 1
    print("DEMO-FILL PASSED — all five checks, on the artefact.")
    print("  NOT shown: whether any filled value is CORRECT. This proves the return was written")
    print("  faithfully, not that the figures are right — that needs the 30 source-pack pairs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
