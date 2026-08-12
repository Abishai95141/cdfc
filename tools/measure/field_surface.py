#!/usr/bin/env python
"""P2's measurement: the field surface for all nine, computed TWICE, with G-DENOM.

G-DENOM: the denominator is computed by two independent code paths and they must agree,
per workbook. A workbook where they disagree gets `field_surface = null` and is published
as such — the corpus shrinks and the plan continues.

Two of the nine ship no protection mask at all, so their denominator is not derivable.
That `null` is the measurement, not a gap in it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema import styles_mask_b as B  # noqa: E402
from cdfc.schema.styles_mask import Rule, build  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
OUT_JSON = REPO / "docs" / "measurements" / "p2-field-surface.json"
OUT_MD = REPO / "docs" / "measurements" / "P2-field-surface.md"


def run() -> dict:
    rows = []
    agree = derivable = 0
    for p in sorted(FIX.glob("*.xlsx")):
        fs = build(p, Rule.V3)
        b = B.count_field_surface(p)
        ok = fs.n_cells == b
        agree += ok
        derivable += fs.n_cells is not None
        rows.append(
            {
                "workbook": p.name,
                "sha8": hashlib.sha256(p.read_bytes()).hexdigest()[:8],
                "path_a": fs.n_cells,
                "path_b": b,
                "agree": ok,
                "generator_rule": fs.generator_rule,
                "validation_state": fs.validation_state,
                "source": fs.source,
                "sheets_in_scope": len(fs.sheets_in_scope),
                "per_sheet": fs.per_sheet,
                "census": None if fs.census is None else {
                    "cell_xfs": fs.census.n_cell_xfs,
                    "explicit_unlocked": fs.census.explicit_unlocked,
                    "explicit_locked": fs.census.explicit_locked,
                    "inheriting": fs.census.inheriting,
                    "apply_protection": fs.census.apply_protection,
                },
            }
        )
    fme = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
    return {
        "warrant": "MEASURED",
        "workbooks": len(rows),
        "g_denom_agree": agree,
        "derivable": derivable,
        "not_derivable": len(rows) - derivable,
        "adopted_rule": "v3",
        "validation_state": "PROVISIONAL-UNVALIDATED",
        "lawful_readings_on_fme": {
            "v3": build(fme, Rule.V3).n_cells,
            "v3-uw": build(fme, Rule.V3_UW).n_cells,
            "v3-abs": build(fme, Rule.V3_ABS).n_cells,
        },
        "rows": rows,
    }


def render(r: dict) -> str:
    L = [
        "# P2 — the field surface",
        "",
        f"**The denominator every later number is a fraction of. {r['workbooks']} workbooks, "
        f"computed twice. Warrant MEASURED.**",
        "",
        f"- **G-DENOM: {r['g_denom_agree']} / {r['workbooks']} agree** between two independent paths",
        f"- **{r['derivable']} derivable · {r['not_derivable']} NOT DERIVABLE** — those ship no "
        "protection mask, so their denominator is `null` and that null is the measurement",
        f"- adopted rule **`{r['adopted_rule']}`** · validation state "
        f"**`{r['validation_state']}`**",
        "",
        "| workbook | path A | path B | agree | sheets | source |",
        "|---|---:|---:|:--:|---:|---|",
    ]
    for row in r["rows"]:
        a = "null" if row["path_a"] is None else f"{row['path_a']:,}"
        b = "null" if row["path_b"] is None else f"{row['path_b']:,}"
        L.append(f"| {row['workbook'][:40]} | {a} | {b} | {'yes' if row['agree'] else '**NO**'} "
                 f"| {row['sheets_in_scope']} | {row['source'][:44]} |")
    lr = r["lawful_readings_on_fme"]
    L += [
        "",
        "## The three lawful readings, on FME",
        "",
        "All three are readings a competent engineer produces from ECMA-376. Every surface printing a",
        "settled fraction prints the rule that produced its denominator beside it.",
        "",
        "| rule | field surface | status |",
        "|---|---:|---|",
        f"| `v3` | **{lr['v3']:,}** | ADOPTED |",
        f"| `v3-uw` | {lr['v3-uw']:,} | lawful, not adopted |",
        f"| `v3-abs` | {lr['v3-abs']:,} | lawful, REJECTED by NC-D05 |",
        "",
        "## NOTHING IN P2 CAN FALSIFY THE ADOPTED RULE",
        "",
        "Both paths implement a rule we wrote. Their agreement proves they are two implementations",
        "rather than one function called twice — it cannot prove the rule is right, because both would",
        "agree just as well on `v3-abs`. The external falsifier arrives at P8-B1: the cells a competent",
        "filler actually wrote into. Until then this denominator is `PROVISIONAL-UNVALIDATED` and says so",
        "on every surface that prints a fraction of it.",
        "",
    ]
    return "\n".join(L)


def main() -> int:
    r = run()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(r, indent=1, sort_keys=True) + "\n")
    OUT_MD.write_text(render(r))
    print(f"G-DENOM        : {r['g_denom_agree']} / {r['workbooks']} agree")
    print(f"derivable      : {r['derivable']}   not derivable: {r['not_derivable']}")
    print(f"FME readings   : {r['lawful_readings_on_fme']}")
    print(f"state          : {r['validation_state']}")
    print(f"wrote {OUT_MD}")
    return 0 if r["g_denom_agree"] == r["workbooks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
