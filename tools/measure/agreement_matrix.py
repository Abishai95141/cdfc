#!/usr/bin/env python
"""P1's measurement: the reader-agreement matrix, 8 fields x 9 workbooks = 72 cells.

Published as TWO vectors, never as one number. A single /72 figure averages an external
check against a self-check and reports the result as one instrument.

Also re-measures openpyxl's blind-control vector on every workbook rather than
remembering it. A pinned control that is never re-taken is a claim about the past.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest import reader_lxml as A  # noqa: E402
from cdfc.ingest import reader_lxml_b as AP  # noqa: E402
from cdfc.ingest import reader_openpyxl as B  # noqa: E402
from cdfc.ingest.agreement import Label, compare  # noqa: E402
from cdfc.ingest.competence import (  # noqa: E402
    AGREEMENT_FIELDS,
    THREE_PARTY_FIELDS,
    TWO_PARTY_FIELDS,
    Instrument,
)

FIX = REPO / "fixtures" / "prescribed"
OUT_JSON = REPO / "docs" / "measurements" / "p1-agreement.json"
OUT_MD = REPO / "docs" / "measurements" / "P1-agreement.md"


def sha8(p: Path) -> str:
    import hashlib

    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def run() -> dict:
    books = sorted(FIX.glob("*.xlsx"))
    all_cells = []
    blind: dict[str, dict[str, int]] = {}
    three_a = three_n = same_a = same_n = 0

    for p in books:
        s8 = sha8(p)
        a = A.read(p)
        ap = AP.read_b(p)
        b = B.read_formula_text_and_cached(p)
        blind[p.name] = dict(B.blind_controls(b))

        views = {
            Instrument.A: A.agreement_view(a),
            Instrument.A_PRIME: AP.agreement_view(ap),
            Instrument.B: B.agreement_view(b),
        }
        ag = compare(s8, views)
        ta, tn = ag.three_party
        sa, sn = ag.same_author
        three_a += ta
        three_n += tn
        same_a += sa
        same_n += sn
        for c in ag.cells:
            all_cells.append(
                {
                    "workbook": p.name,
                    "sha8": s8,
                    "field": c.field,
                    "label": str(c.label),
                    "values": {str(k): v for k, v in c.values.items()},
                    "mechanism": c.mechanism,
                    "second_party": c.second_party,
                }
            )

    counts: dict[str, int] = {}
    for c in all_cells:
        counts[c["label"]] = counts.get(c["label"], 0) + 1

    return {
        "warrant": "MEASURED",
        "denominator": len(all_cells),
        "workbooks": len(books),
        "fields": len(AGREEMENT_FIELDS),
        "label_counts": counts,
        "three_party_vector": {"agree": three_a, "comparable": three_n,
                               "fields": list(THREE_PARTY_FIELDS)},
        "same_author_vector": {"agree": same_a, "comparable": same_n,
                               "fields": list(TWO_PARTY_FIELDS),
                               "label": "SAME-AUTHOR — both implementations by one author"},
        "openpyxl_blind_controls": blind,
        "cells": all_cells,
    }


def render_md(r: dict) -> str:
    L = ["# P1 — the reader-agreement matrix",
         "",
         f"**{r['fields']} fields x {r['workbooks']} workbooks = {r['denominator']} cells. "
         f"Warrant MEASURED.**",
         "",
         "## Published as two vectors, never as one number",
         "",
         f"- **Three-party — {r['three_party_vector']['agree']} / "
         f"{r['three_party_vector']['comparable']}.** A, A' and openpyxl. "
         "The only vector containing an instrument nobody here wrote.",
         f"- **Same-author — {r['same_author_vector']['agree']} / "
         f"{r['same_author_vector']['comparable']}.** A and A' only, and both were written by "
         "the same author. This is a self-check and is labelled as one.",
         "",
         "A single 72-cell figure would average the two and report the result as one instrument. "
         "It is banned on every surface.",
         "",
         "## Label counts",
         ""]
    for k, v in sorted(r["label_counts"].items()):
        L.append(f"- `{k}` — {v}")
    L += ["", "## Every non-AGREE cell, with its mechanism", "",
          "| workbook | field | label | values | mechanism |", "|---|---|---|---|---|"]
    for c in r["cells"]:
        if c["label"] == "AGREE":
            continue
        vals = ", ".join(f"{k.split('_')[-1]}={v}" for k, v in c["values"].items()
                         if not isinstance(v, list))
        L.append(f"| {c['workbook'][:34]} | `{c['field']}` | {c['label']} | {vals or '—'} | "
                 f"{c['mechanism'] or '**NONE — escalates**'} |")
    L += ["", "## openpyxl's blind-control vector, re-measured on all nine",
          "",
          "A pinned control that is never re-taken is a claim about the past. These are taken "
          "on every run.",
          "",
          "| workbook | n_validations | n_cells | n_formula_cells | n_defined_names |",
          "|---|---:|---:|---:|---:|"]
    for name, d in sorted(r["openpyxl_blind_controls"].items()):
        L.append(f"| {name[:40]} | {d['n_validations']} | {d['n_cells']} | "
                 f"{d['n_formula_cells']} | {d['n_defined_names']} |")
    L.append("")
    return "\n".join(L)


def main() -> int:
    r = run()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(r, indent=1, sort_keys=True) + "\n")
    OUT_MD.write_text(render_md(r))
    tp, sa = r["three_party_vector"], r["same_author_vector"]
    print(f"cells                : {r['denominator']}")
    print(f"  {r['label_counts']}")
    print(f"three-party vector   : {tp['agree']} / {tp['comparable']}")
    print(f"same-author vector   : {sa['agree']} / {sa['comparable']}   (SAME-AUTHOR)")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
