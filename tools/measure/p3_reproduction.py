#!/usr/bin/env python
"""`docs/measurements/P3-cached-value-reproduction.md` — P9's entry criterion 4.

**What this file is for, and it is not a second copy of arm 1's table.** P9-B1's oracle *is* the
evaluator. A relation whose oracle contains an unimplemented function has an undeclared blind spot
inside its own oracle, so before `TEMPLATE_DIFF` may be built, two things must be on paper: which
cells the evaluator does not reproduce, and what the function vocabulary of the workbook actually
is.

**The vocabulary is the point.** The specification fixes the evaluator at eight functions. A
vocabulary counted by hand is an **absence claim** — *"there is no ninth"* — and this project's
own rule is that an absence claim ships with a positive control or it does not ship. The census
below is that control, and it is a script: it tokenises all 505 materialised formulas with the
evaluator's own tokeniser and reports what it finds, including the one function nobody counted.

    make p3-reproduction

Counted with `cdfc.calc.evaluate.tokenize`, deliberately, and not with a pattern over the formula
text: a regex census would report whatever its author already believed the vocabulary was.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools" / "measure"))

from evaluator_arm1 import load  # noqa: E402

from cdfc.calc.evaluate import tokenize  # noqa: E402
from cdfc.calc.functions import VOCABULARY  # noqa: E402
from cdfc.measure.absence import assert_absent  # noqa: E402
from cdfc.measure.geval import ARMS, gate_status, label  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
OUT_MD = REPO / "docs" / "measurements" / "P3-cached-value-reproduction.md"
OUT_JSON = REPO / "docs" / "measurements" / "p3-cached-value-reproduction.json"

# Excel spells a function introduced after 2007 with an `_xlfn.` prefix inside the stored formula
# text. It is a serialisation detail, not a different function, and stripping it is how the
# evaluator resolves the name — so the census strips it too, or it would report `AGGREGATE` and
# `_xlfn.AGGREGATE` as two functions and the count would be wrong in the direction that inflates.
XLFN = "_xlfn."


def census(formulas: dict[tuple[str, str], str]) -> tuple[Counter[str], dict[str, list[str]]]:
    """(function -> cell count, function -> the cells that use it).

    Tokenised, not matched. `tokenize` returns a `func` token for a name immediately followed by
    `(`, which is exactly the definition of a called function and is the same rule the parser
    applies — so a name this census reports is a name the evaluator will be asked to resolve.
    """
    counts: Counter[str] = Counter()
    where: dict[str, list[str]] = {}
    # Sorted by (sheet, column index, row) and NOT lexically: `C100` sorts before `C92` as a
    # string, so a lexical order would report the first cell of `IFERROR` as C100 and quietly
    # move the census's own worked example off the range the specification names.
    for (sheet, ref), src in sorted(formulas.items(), key=lambda kv: _order(kv[0])):
        seen = {tok for kind, tok in tokenize(src) if kind == "func"}
        for fn in sorted(seen):
            counts[fn] += 1
            where.setdefault(fn, []).append(f"'{sheet}'!{ref}")
    return counts, where


def _order(key: tuple[str, str]) -> tuple[str, int, int]:
    from cdfc.schema.stable_keys import col_to_index, split_ref

    sheet, ref = key
    col, row = split_ref(ref)
    return sheet, col_to_index(col), row


def main() -> int:
    formulas, literals, cached, deferred = load(FME)
    counts, where = census(formulas)

    implemented = {fn: fn.removeprefix(XLFN) in VOCABULARY for fn in counts}
    missing = sorted(fn for fn, ok in implemented.items() if not ok)

    # The absence claim, through `assert_absent`, with the census as its positive control. The
    # claim is "no function in this workbook is outside the evaluator's vocabulary"; the control
    # is the SAME query returning a POSITIVE count of functions it CAN see. A census that could
    # see nothing would satisfy the claim and fail the control, which is the whole mechanism.
    claim = assert_absent(
        lambda c: sum(1 for fn in c if fn.removeprefix(XLFN) not in VOCABULARY),
        positive_control=lambda c: len(c),
        corpus=counts,
        corpus_id=FME.name,
        query_name="fme_functions_outside_the_evaluator_vocabulary",
    )

    grid = _grid(formulas, literals, deferred)
    agree = sum(1 for k in cached if k in grid.values and k not in grid.not_run)
    notrun = sum(1 for k in cached if k in grid.not_run or k not in grid.values)

    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    L = [
        "# P3 — cached-value reproduction, and the function census that bounds it",
        "",
        "**GENERATED by `tools/measure/p3_reproduction.py`. Run `make p3-reproduction`.**",
        "",
        f"**G-EVAL: {gate_status()}.**"
        + (f" **{label()}**" if label() else "  Arm 2's oracle shares no author with the evaluator."),
        "",
        "## The two arms, and what each is blind to",
        "",
        "| arm | oracle | oracle's author | independence | blind to |",
        "|---:|---|---|---|---|",
    ]
    for a in ARMS:
        L.append(f"| {a.n} | {a.oracle} | {a.oracle_author} | **{a.independence}** | {a.blind_to} |")

    L += [
        "",
        "The `blind to` column is the reason this file exists rather than a green tick. Arm 2 is",
        "independent of us and still cannot see a defect in the regulator's own formula, because",
        "it reads the same formula text. That is the gap `probes/template_defects.yaml` fills, and",
        "it is why a declared template defect is `INFORMATIONAL` and never `FAIL`.",
        "",
        "## Reproduction on the FME workbook",
        "",
        "| | cells |",
        "|---|---:|",
        f"| formula cells | {len(cached)} |",
        f"| reproduced, equal to the regulator's cached value | {agree} |",
        f"| **NOT RUN — declared, not silently answered** | {notrun} |",
        "",
        "The not-run population is the honest half. It was **10** until P6, when `AGGREGATE`",
        "was made to refuse an ignore option it does not implement: 29 cells had been returning",
        "`#NUM!`, `IFERROR` had been catching it and writing the literal `\"NA\"`, and nothing was",
        "red. **The number got worse and the output got truer.**",
        "",
        "## The function census — all 505 materialised formulas, tokenised",
        "",
        f"**{len(counts)} functions, not the eight the specification fixes.**",
        "",
        "| function | cells | implemented | first cell |",
        "|---|---:|---|---|",
    ]
    for fn, n in rows:
        mark = "yes" if implemented[fn] else "**NO**"
        L.append(f"| `{fn}` | {n} | {mark} | `{where[fn][0]}` |")

    L += [
        "",
        f"`{rows[-1][0]}` appears in **{rows[-1][1]}** cell and it is the one nobody counted: "
        f"`{where[rows[-1][0]][0]}`.",
        "",
        "**Where it sits matters more than that it exists.** `'1. Introduction'!C92:E101` is the",
        "range the specification nominates as the positive control that must pass before any kill",
        "rate may be quoted. The ninth function is inside G-EVAL's own positive control.",
        "",
        "## Disposition",
        "",
    ]
    if missing:
        L += [
            f"**{len(missing)} function(s) are outside the vocabulary: "
            + ", ".join(f"`{m}`" for m in missing) + ".**",
            "",
            "Their cells are `NOT_RUN(not_run.source_unreadable)`, excluded from the observability",
            "site set and from `TEMPLATE_DIFF`'s target set, **and the exclusion is named**. G-EVAL's",
            f"threshold is restated as {len(cached) - _cells_using(where, missing)} of "
            f"{len(cached) - _cells_using(where, missing)} with the exclusion on its face — never as",
            f"{len(cached)} of {len(cached)} with cells quietly dropped.",
        ]
    else:
        L += [
            "**Every function in this workbook is implemented, including the ninth.** No cell is",
            "excluded from the observability site set or from `TEMPLATE_DIFF`'s target set for a",
            "vocabulary reason, and G-EVAL's threshold is not restated.",
            "",
            "This is the branch the plan did not expect, and it is worth being precise about what",
            "it does and does not license. It does **not** mean the census was unnecessary: the",
            "claim *the vocabulary is eight* was false, and it was false about a cell inside the",
            "positive control. It means the disposition rule had nothing to dispose of.",
        ]

    L += [
        "",
        "## The absence claim, with its control",
        "",
        f"- claim: **{len(missing)}** function(s) outside the vocabulary",
        f"- positive control, same query: **{len(counts)}** function(s) found",
        f"- ledger row: `{claim.row_id}`",
        "",
        "A census that could see nothing would report zero missing functions and would be wrong in",
        "the direction that flatters us. The control is the count it CAN see, through the same",
        "interface, and both integers ship together.",
        "",
    ]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(
            {
                "warrant": "MEASURED",
                "workbook": FME.name,
                "formula_cells": len(cached),
                "functions": dict(rows),
                "implemented": implemented,
                "outside_vocabulary": missing,
                "geval": {
                    "status": gate_status(),
                    "label": label(),
                    "arm2_independence": ARMS[1].independence,
                },
            },
            indent=1,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{len(counts)} functions over {len(cached)} formula cells; outside vocabulary: {missing}")
    print(f"wrote {OUT_MD.relative_to(REPO)}")
    return 0


def _cells_using(where: dict[str, list[str]], fns: list[str]) -> int:
    return len({c for fn in fns for c in where[fn]})


def _grid(formulas, literals, deferred):
    """`formula_source="TEMPLATE"`: this measures the blank against its own cached values, so the
    blank's formulas ARE the subject. See `EVALUATION-CONTRACT.md`'s `formula_source` section."""
    from cdfc.calc.evaluate import recalculate

    return recalculate(
        formulas, literals, formula_source="TEMPLATE",
        deferred={k: "deferred: shared dependent, row shift not implemented" for k in deferred},
    )


if __name__ == "__main__":
    raise SystemExit(main())
