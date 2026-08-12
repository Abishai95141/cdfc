#!/usr/bin/env python
"""How much information is in the positive control that gates every kill rate?

P3's arm 1 compares our evaluator against the template's own cached values. This script
measures what agreement on that comparison is worth. The answer for the blank FME
template is: nothing. Committed so the two-arm design rests on a reproducible measurement
rather than on a remembered one.
"""
from __future__ import annotations

import collections
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.reader_lxml import _sheet_parts  # noqa: E402
from cdfc.ingest.xmlsafe import fromstring  # noqa: E402

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
FIX = REPO / "fixtures" / "prescribed"
OUT = REPO / "docs" / "measurements" / "p3-cached-values.json"


def cached_values(path: Path) -> list[str]:
    out: list[str] = []
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(f"{{{M}}}t"))
                      for si in ss.iter(f"{{{M}}}si")]
        for _n, _s, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            for c in fromstring(z.read(part)).iter(f"{{{M}}}c"):
                if c.find(f"{{{M}}}f") is None:
                    continue
                v = c.findtext(f"{{{M}}}v")
                if v is None:
                    out.append("<none>")
                elif c.get("t") == "s" and v.isdigit() and int(v) < len(shared):
                    out.append(shared[int(v)])
                else:
                    out.append(v)
    return out


def main() -> int:
    rows = {}
    for p in sorted(FIX.glob("*.xlsx")):
        vals = cached_values(p)
        if not vals:
            continue
        c = collections.Counter(vals)
        trivial = sum(n for v, n in c.items() if str(v) in ("0", "0.0") or str(v).strip().upper() == "NA")
        rows[p.name] = {
            "formula_cells": len(vals),
            "distinct_cached_values": len(c),
            "trivial": trivial,
            "trivial_share_pct": round(100 * trivial / len(vals), 1),
            "top": c.most_common(4),
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"warrant": "MEASURED", "workbooks": rows}, indent=1, sort_keys=True) + "\n")
    print(f"{'workbook':44s} {'cells':>6} {'distinct':>9} {'trivial':>8}")
    for name, r in rows.items():
        print(f"  {name[:42]:42s} {r['formula_cells']:>6} {r['distinct_cached_values']:>9} "
              f"{r['trivial_share_pct']:>7}%")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
