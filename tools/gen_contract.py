#!/usr/bin/env python
"""Render `src/cdfc/evaluate/contract.py::TRANSITIONS` to `EVALUATION-CONTRACT.md`.

The code is the source of truth and the markdown is generated. A hand edit to the markdown fails
`test_nc__E03b_contract_is_generated_not_edited`, which regenerates and asserts byte-identity.

    make gen-contract    # or: python tools/gen_contract.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.calc.evaluate import FORMULA_SOURCE_CONTRACT  # noqa: E402
from cdfc.evaluate.contract import TRANSITIONS  # noqa: E402

OUT = REPO / "EVALUATION-CONTRACT.md"


def render() -> str:
    lines = [
        "# EVALUATION-CONTRACT.md",
        "",
        "**GENERATED from `src/cdfc/evaluate/contract.py::TRANSITIONS`. Never hand-edited.**",
        "Run `make gen-contract` to regenerate. A hand edit fails the build:",
        "`test_nc__E03b_contract_is_generated_not_edited` regenerates and asserts byte-identity,",
        "and `test_contract__evaluation_contract_matches_evaluator` compares the same table",
        "set-equal to the pinned extraction of the specification's own five rules.",
        "",
        "**`order` is not `rule`.** `rule` is the specification's conceptual numbering; `order` is",
        "the order the evaluator applies them. D-P5-01 puts `cells_bound == 0` at order 4 —",
        "**before pre-flight and before `expr`** — because `all([])` is `True`, and a design that",
        "lets the vacuous pass be produced and then corrected is trusting itself to overwrite a",
        "`PASS`. The vacuous pass must be unreachable, not repaired.",
        "",
        "The `never` column is the specification's bracketed `[never FAIL]` annotations, carried",
        "as assertions: `assert_permitted(order, state)` raises if a transition ever realises a",
        "state its own row forbids.",
        "",
        "| order | rule | trigger | state | reason | run state | never |",
        "|---:|---:|---|---|---|---|---|",
    ]
    for t in TRANSITIONS:
        state = "— (continue)" if t.state is None else f"`{t.state.value}`"
        reason = "—" if t.reason is None else f"`{t.reason.value}`"
        run = "unchanged" if t.run_state_effect.value == "UNCHANGED" else "**INVALID**"
        never = ", ".join(s.value for s in t.never) or "—"
        lines.append(f"| {t.order} | {t.rule} | {t.trigger} | {state} | {reason} | {run} | {never} |")

    lines += [
        "",
        "## Rows 4 and 7, against each other",
        "",
        "A predicate that **raised** is an apparatus failure — fix the code. A source that could",
        "not be read is `not_run.source_unreadable` — retry. **They have opposite remedies**, and",
        "collapsing them into one outcome is NC-E01: a crash that looks like a limit.",
        "",
        "## Rule 4 is not a transition",
        "",
        "It is composition, and it is the sentence the whole contract rests on: **a verdict is",
        "never fresher than its stalest input and never stronger than its weakest.**",
        "",
        "- `compose_warrant` takes the **minimum** under `DETERMINISTIC > MODEL_EXTRACTED >",
        "  DERIVED`. The empty set **raises** rather than returning the strongest warrant — a",
        "  value derived from nothing is not deterministic, and order 4 already owns that case.",
        "- `compose_retrieved_at` takes the **minimum**, i.e. the OLDEST retrieval. The plan's",
        "  interface block annotates it `# max`, two lines below its own statement of the rule;",
        "  the two cannot both hold, and `min` is the one that makes the sentence true. Under",
        "  `max` a verdict composed from a January snapshot and a filing read today would report",
        "  today, and a reader would take the whole verdict to be that fresh.",
        "",
        "## `formula_source` — which formulas 'recalculate' means",
        "",
        "**GENERATED from `src/cdfc/calc/evaluate.py::FORMULA_SOURCE_CONTRACT`.** C8b puts the",
        "rule here and nowhere else — there is no separate `docs/RECALCULATION-SOURCE.md`, because",
        "a rule published in two files is a rule that will be true in one of them.",
        "",
        "`recalculate` has **no default** `formula_source`. A call site that omits it is a",
        "`TypeError`, not a quietly-chosen meaning. `test_contract__formula_source_is_explicit`",
        "scans `src/cdfc/` by AST and fails the build on a missing, computed or non-literal",
        "argument; the caller column below is checked against the same scan, so a caller that",
        "moves without updating this table is red.",
        "",
        "| caller | `formula_source` | because |",
        "|---|---|---|",
    ]
    for r in FORMULA_SOURCE_CONTRACT:
        lines.append(f"| `{r.caller}` | **`{r.source}`** | {r.because} |")

    lines += [
        "",
        "**The defect this prevents (F19), stated once.** The observability filter classifies a",
        "mutant by comparing two *recalculated* grids. An **F11** mutant is a cell the pinned",
        "blank declares a formula, carrying a literal — so recalculating it through the",
        "**template's** formula graph overwrites the literal with the formula's own value, the two",
        "grids come out identical, and the flagship fault class is classified `UNOBSERVABLE` **by",
        "construction**. `O` for F11 is then 0, `Campaign.kill_rate()` raises on `O == 0`, and",
        "`TEMPLATE_DIFF` dies at the third gate with an arithmetic exception rather than with a",
        "measured refusal. Each phase passes its own tests throughout.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    text = render()
    changed = not OUT.is_file() or OUT.read_text(encoding="utf-8") != text
    OUT.write_text(text, encoding="utf-8")
    print(f"{'wrote' if changed else 'unchanged'} {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
