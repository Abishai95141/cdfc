#!/usr/bin/env python
"""The evidence command for template defect `TD-01`, and it is a check rather than a printout.

**The claim.** `'1. Introduction'!D17` — *"Total No. of Schemes of the FME authorised by IFSCA"* —
is `SUM(D18:D20)` over three `COUNTIF` rows whose five wildcard patterns match only **seven of the
nine** scheme types the workbook's own validation offers at `Dropdown!F3:F11`. A filer who declares
a *Special Situation Fund* or a *Family Investment Fund* at `'1. Introduction'!G54:G63` is counted
by none of them, so the regulator's own total under-reports by exactly the number of such schemes.

**This script exits non-zero if the defect stops reproducing**, which is the whole point of an
`evidence_command`. A defect table whose evidence is a sentence is a list of opinions; a defect
whose evidence is a script that can fail is a claim somebody could refute.

    .venv/bin/python tools/probes/p9_scheme_vocabulary.py

Prints a JSON object on stdout: the vocabulary, the patterns, and the unmatched members.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.harvest import _load_context  # noqa: E402

FME = (
    REPO / "fixtures" / "prescribed"
    / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)
SHEET = "1. Introduction"
VOCAB_RANGE = ("Dropdown", "F", 3, 11)      # the scheme-type list the validation offers
COUNTIF_ROWS = ("D18", "D19", "D20")
TOTAL_CELL = "D17"


def _patterns(body: str) -> list[str]:
    """The quoted criteria of every COUNTIF in a formula body, in order."""
    out, i = [], 0
    while True:
        j = body.find('"', i)
        if j < 0:
            return out
        k = body.find('"', j + 1)
        if k < 0:
            return out
        out.append(body[j + 1 : k])
        i = k + 1


def _matches(pattern: str, term: str) -> bool:
    """Excel's `*` wildcard, which is a CONTAINS when it brackets the criterion.

    Deliberately implemented here rather than imported: this script is the *evidence* for a
    claim about the workbook, and evidence that shares an implementation with the thing it
    attests to is not independent of it.
    """
    parts = pattern.split("*")
    if len(parts) == 1:
        return term.casefold() == pattern.casefold()
    t = term.casefold()
    pos = 0
    for n, part in enumerate(parts):
        if not part:
            continue
        p = part.casefold()
        if n == 0:
            if not t.startswith(p):
                return False
            pos = len(p)
            continue
        found = t.find(p, pos)
        if found < 0:
            return False
        pos = found + len(p)
    if parts[-1] and not pattern.endswith("*"):
        return t.endswith(parts[-1].casefold())
    return True


def main() -> int:
    ctx = _load_context(FME)
    sheet, col, r1, r2 = VOCAB_RANGE
    text = ctx.cell_text.get(sheet, {})
    vocabulary = [text[f"{col}{r}"] for r in range(r1, r2 + 1) if text.get(f"{col}{r}")]

    formulas = {
        (f.sheet, f.ref): (f.text or f.materialised or "")
        for f in ctx.wb.formulas
    }
    patterns: list[str] = []
    for ref in COUNTIF_ROWS:
        patterns.extend(_patterns(formulas.get((SHEET, ref), "")))

    unmatched = [v for v in vocabulary if not any(_matches(p, v) for p in patterns)]

    result = {
        "cell": f"{SHEET}!{TOTAL_CELL}",
        "total_formula": formulas.get((SHEET, TOTAL_CELL), ""),
        "vocabulary_range": f"{sheet}!{col}{r1}:{col}{r2}",
        "vocabulary": vocabulary,
        "vocabulary_size": len(vocabulary),
        "patterns": patterns,
        "matched": len(vocabulary) - len(unmatched),
        "unmatched": unmatched,
        "claim_reproduces": bool(unmatched),
    }
    print(json.dumps(result, indent=1, sort_keys=True))

    if not unmatched:
        print(
            "EVIDENCE FAILS: every scheme type is matched by some COUNTIF pattern. The declared "
            "defect no longer reproduces, so its row in template_defects.yaml is now an opinion "
            "and must be removed or restated.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
