#!/usr/bin/env python
"""G-EVAL arm 1 — our evaluator against the regulator's own cached values.

REPORTED PER WORKBOOK, NEVER AS ONE CORPUS FIGURE. A single percentage would average one
control that discriminates (Draft ACAC: 112 cells, 44 distinct values, 0% trivial) against
six that do not (FME: 505 cells, 2 distinct values — a constant scores 100%). That is the
same defect as a single agreement figure over the reader matrix.

Every row carries its trivial share, so a reader can see at a glance which rows are
evidence and which are arithmetic about zeros.
"""

from __future__ import annotations

import json
import sys
import zipfile
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.calc.errors import is_error  # noqa: E402
from cdfc.calc.evaluate import recalculate  # noqa: E402
from cdfc.ingest.reader_lxml import _sheet_parts, read  # noqa: E402
from cdfc.ingest.xmlsafe import fromstring  # noqa: E402

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
FIX = REPO / "fixtures" / "prescribed"
OUT = REPO / "docs" / "measurements" / "p3-evaluator.json"
OUT_MD = REPO / "docs" / "measurements" / "P3-evaluator.md"


def load(path: Path):
    """(formulas, literals, cached) keyed by (sheet, ref)."""
    wb = read(path)
    materialised = {}
    masters = {f.si: f for f in wb.formulas if f.encoding == "SHARED_MASTER"}
    for f in wb.formulas:
        if f.text:
            materialised[(f.sheet, f.ref)] = f.text
        elif f.encoding == "SHARED_DEPENDENT" and f.si in masters:
            # A shared dependent's expression is the master's, shifted. Row-shifting is
            # P3-B4's own sub-problem; until it lands the dependent is NOT_RUN rather
            # than silently evaluated with the master's unshifted references.
            materialised[(f.sheet, f.ref)] = None

    literals: dict[tuple[str, str], object] = {}
    cached: dict[tuple[str, str], str] = {}
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(f"{{{M}}}t"))
                      for si in ss.iter(f"{{{M}}}si")]
        for name, _s, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            for c in fromstring(z.read(part)).iter(f"{{{M}}}c"):
                ref = c.get("r", "")
                v = c.findtext(f"{{{M}}}v")
                is_f = c.find(f"{{{M}}}f") is not None
                if v is None:
                    val: object = None
                elif c.get("t") == "s" and v.isdigit() and int(v) < len(shared):
                    val = shared[int(v)]
                elif c.get("t") == "str":
                    val = v
                else:
                    try:
                        val = Decimal(v)
                    except Exception:  # noqa: BLE001
                        val = v
                if is_f:
                    cached[(name, ref)] = "" if v is None else str(val)
                else:
                    literals[(name, ref)] = val
    formulas = {k: v for k, v in materialised.items() if v}
    return formulas, literals, cached, {k for k, v in materialised.items() if v is None}


def compare(path: Path) -> dict:
    formulas, literals, cached, deferred = load(path)
    grid = recalculate(
        formulas, literals, formula_source="TEMPLATE",
        deferred={k: "deferred: shared dependent, row shift not implemented" for k in deferred},
    )

    agree = disagree = 0
    not_run = len(deferred)
    samples: list[str] = []
    for key, want in cached.items():
        if key in deferred:
            continue
        if key in grid.not_run:
            not_run += 1
            continue
        if key not in grid.values:
            not_run += 1
            continue
        got = grid.values[key]
        if is_error(got):
            got_s = str(got)
        elif isinstance(got, Decimal):
            got_s = str(got.normalize())
        elif isinstance(got, bool):
            # Excel caches a boolean as 1/0, not as TRUE/FALSE. Comparing "TRUE" against
            # "1" was a defect in the COMPARISON, not in the evaluator.
            got_s = "1" if got else "0"
        else:
            got_s = "" if got is None else str(got)
        w = want.strip()
        try:
            # Excel caches ~15 significant decimal digits; we compute at 34. Comparing
            # full precision reports a disagreement that is an artifact of OUR precision
            # being higher, which is a measurement of the instrument.
            a_, b_ = Decimal(got_s or "0"), Decimal(w or "0")
            same = a_ == b_ or (
                a_ != 0 and abs(a_ - b_) / abs(a_) < Decimal("1e-15")
            )
        except Exception:  # noqa: BLE001
            same = got_s.strip().upper() == w.upper()
        if same:
            agree += 1
        else:
            disagree += 1
            if len(samples) < 4:
                samples.append(f"{key[0]}!{key[1]} want={w!r} got={got_s!r}")

    trivial = sum(1 for v in cached.values() if v.strip() in ("0", "0.0") or v.strip().upper() == "NA")
    return {
        "workbook": path.name,
        "formula_cells": len(cached),
        "compared": agree + disagree,
        "agree": agree,
        "disagree": disagree,
        "not_run": not_run,
        "trivial_share_pct": round(100 * trivial / len(cached), 1) if cached else 0.0,
        "distinct_cached": len(set(cached.values())),
        "samples": samples,
    }


def main() -> int:
    rows = [compare(p) for p in sorted(FIX.glob("*.xlsx")) if read(p).formulas]
    rows.sort(key=lambda r: r["trivial_share_pct"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"warrant": "MEASURED", "arm": 1, "rows": rows}, indent=1) + "\n")

    L = ["# P3 — G-EVAL arm 1: evaluator against the regulator's cached values", "",
         "**Reported per workbook, never as one corpus figure.** A single percentage would average a",
         "control that discriminates against six that do not.", "",
         "| workbook | cells | compared | agree | disagree | not run | trivial | worth |",
         "|---|---:|---:|---:|---:|---:|---:|---|"]
    print(f"{'workbook':40s} {'cells':>6} {'agree':>6} {'dis':>5} {'n/run':>6} {'trivial':>8}  worth")
    for r in rows:
        worth = ("EVIDENCE" if r["trivial_share_pct"] < 10 else
                 "partial" if r["trivial_share_pct"] < 80 else "a constant scores here")
        L.append(f"| {r['workbook'][:38]} | {r['formula_cells']} | {r['compared']} | {r['agree']} "
                 f"| {r['disagree']} | {r['not_run']} | {r['trivial_share_pct']}% | {worth} |")
        print(f"  {r['workbook'][:38]:38s} {r['formula_cells']:>6} {r['agree']:>6} "
              f"{r['disagree']:>5} {r['not_run']:>6} {r['trivial_share_pct']:>7}%  {worth}")
    L.append("")
    OUT_MD.write_text("\n".join(L))
    print(f"\nwrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
