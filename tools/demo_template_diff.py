#!/usr/bin/env python
"""TEMPLATE_DIFF — the flagship check, run end to end for the first time.

The claim: a filer who overwrites a formula cell with a literal is invisible to every
other check in the design. Nothing about the value is wrong — 999,999 is a perfectly
well-formed number — and no arithmetic identity notices, because the identity that WOULD
have caught it is the formula that was deleted.

The check: bind the filing to its template by STRUCTURAL fingerprint (which deliberately
excludes formula content, so an overwritten filing still binds), then recompute the
TEMPLATE's formula over the FILING's inputs and compare against what the filing actually
holds.

`formula_source` makes the distinction explicit at the call site, and it is the whole
point: recomputing with `formula_source="FILING"` would use the filer's own rewritten
formulas and the filer would pass their own rewritten check.

Output is a coverage declaration, not a verdict: what was checked, what was found, and —
in equal weight — what was NOT checked and why.

**TWO CORRECTIONS AT P9, both measured, and both to claims this file used to make.**

1. *"the fingerprint excludes formula content"* is true of formula **text** and false of
   formula **presence**. The field surface is `unlocked ∧ non-formula`, so deleting a
   formula from one of the eight cells that are unlocked AND formula-bearing moves that
   cell INTO the field surface, moves the mask, and the filing no longer binds. Section A
   works because `'3. Portfolio'!O7` is LOCKED. See
   `docs/measurements/P9-template-diff-ceiling.md`.
2. This demo detects an override **structurally** — the cell no longer carries an `<f>`
   element. That is a subset of what `TEMPLATE_DIFF` means. `src/cdfc/probes/template_diff.py`
   compares the recomputed VALUE, which also catches a stale carry and a rewritten formula.
   Section B's control was `values-written__50-cells.xlsx`, which this demo called untouched
   and which the value comparison shows has **twenty stale derived cells**. The control is
   now a filing that is clean under both readings.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools" / "measure"))

from evaluator_arm1 import load  # noqa: E402

from cdfc.schema.anchor import Anchor
from cdfc.calc.evaluate import recalculate  # noqa: E402
from cdfc.ingest.reader_lxml import read  # noqa: E402
from cdfc.schema.fingerprint import structural_fingerprint  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
SYN = REPO / "fixtures" / "synthetic"
TEMPLATE = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


def run(filing: Path, template: Path = TEMPLATE) -> int:
    print(f"  filing   {filing.name}")
    print(f"  template {template.name}\n")

    # --- 1. BIND -----------------------------------------------------------------
    fp_t, fp_f = structural_fingerprint(template), structural_fingerprint(filing)
    if fp_t != fp_f:
        print(f"  BINDING  INVALID(invalid.template_unbound) — {fp_f[:12]} != {fp_t[:12]}")
        print("           No checks run. This is an apparatus outcome, not a finding.")
        return 1
    print(f"  BINDING  bound to template {fp_t[:12]}  (the fingerprint excludes formula TEXT,")
    print("           which is why an overwritten LOCKED formula cell still binds)\n")

    # --- 2. WHAT THE TEMPLATE SAYS EACH DERIVED CELL SHOULD BE -------------------
    t_formulas, _t_lit, _t_cached, t_def = load(template)
    _f_formulas, f_literals, _f_cached, _f_def = load(filing)

    grid = recalculate(
        t_formulas, f_literals,
        formula_source="TEMPLATE",  # NOT the filing's formulas. That is the check.
        deferred={k: "deferred: master not visible" for k in t_def},
    )

    # --- 3. WHAT THE FILING ACTUALLY HOLDS ---------------------------------------
    filing_wb = read(filing)
    filing_formula_cells = {(f.sheet, f.ref) for f in filing_wb.formulas}
    template_formula_cells = set(t_formulas) | set(t_def)

    overwritten = sorted(template_formula_cells - filing_formula_cells)

    findings: list[tuple[str, str, str, str]] = []
    for sheet, ref in overwritten:
        expected = grid.values.get((sheet, ref))
        actual = f_literals.get((sheet, ref))
        exp_s = "not computed" if expected is None else str(
            expected.normalize() if isinstance(expected, Decimal) else expected
        )
        act_s = "blank" if actual is None else str(actual)
        findings.append((Anchor.cell(sheet, ref).render(), exp_s, act_s, t_formulas.get((sheet, ref), "")))

    # --- 4. THE DECLARATION ------------------------------------------------------
    checked = len(template_formula_cells) - len(grid.not_run)
    print(f"  {len(findings)} formula cell(s) overwritten with a literal\n")
    for cell, exp, act, src in findings:
        print(f"    FAIL  {cell}")
        print(f"          the template computes  = {src[:56]}")
        print(f"          which over this filing's inputs yields  {exp}")
        print(f"          the filing instead holds the literal    {act}")
        print("          method TEMPLATE_DIFF · warrant DETERMINISTIC")
    print()
    print(f"  {checked} of {len(template_formula_cells)} derived cells checked")
    print(f"  {len(grid.not_run)} NOT CHECKED, each with a declared reason:")
    reasons: dict[str, int] = {}
    for why in grid.not_run.values():
        k = why.split(":")[0]
        reasons[k] = reasons.get(k, 0) + 1
    for k, n in sorted(reasons.items()):
        print(f"      {n:>3}  {k}")
    # NOTE: this line used to read "There is no all-clear in this output", which
    # contains the banned phrase and was correctly rejected by ci/no-green-tick.sh. A
    # gate cannot distinguish an assertion from its negation and should not try; the copy
    # adapts, the gate stays strict.
    print("\n  Both counts carry equal weight. This output states what was checked and")
    print("  what was not. It does not state that the filing is correct.")
    return 0


def main() -> int:
    print("=" * 78)
    print("  A. A FILING WITH ONE FORMULA OVERWRITTEN BY A LITERAL")
    print("=" * 78)
    rc = run(SYN / "formula-overwritten__portfolio-O7.xlsx")
    print()
    print("=" * 78)
    print("  B. THE ADMISSION-SIDE CONTROL — a clean filing must produce NO findings")
    print("=" * 78)
    # The derived cells of this one were computed by LIBREOFFICE, so a zero-finding result here
    # is not `x == x`. Its predecessor as this control — `values-written__50-cells.xlsx` — has
    # twenty stale derived cells, which the structural detector below cannot see.
    rc |= run(SYN / "clean__independently-computed__fme-q1.xlsx")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
