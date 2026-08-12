# EVALUATION-CONTRACT.md

**GENERATED from `src/cdfc/evaluate/contract.py::TRANSITIONS`. Never hand-edited.**
Run `make contract` to regenerate. A hand edit fails the build:
`test_nc__E03b_contract_is_generated_not_edited` regenerates and asserts byte-identity,
and `test_contract__evaluation_contract_matches_evaluator` compares the same table
set-equal to the pinned extraction of the specification's own five rules.

**`order` is not `rule`.** `rule` is the specification's conceptual numbering; `order` is
the order the evaluator applies them. D-P5-01 puts `cells_bound == 0` at order 4 —
**before pre-flight and before `expr`** — because `all([])` is `True`, and a design that
lets the vacuous pass be produced and then corrected is trusting itself to overwrite a
`PASS`. The vacuous pass must be unreachable, not repaired.

The `never` column is the specification's bracketed `[never FAIL]` annotations, carried
as assertions: `assert_permitted(order, state)` raises if a transition ever realises a
state its own row forbids.

| order | rule | trigger | state | reason | run state | never |
|---:|---:|---|---|---|---|---|
| 1 | 1 | applicable errors | `NOT_RUN` | `not_run.source_unreadable` | unchanged | FAIL |
| 2 | 1 | applicable false | `OUT_OF_SCOPE` | `out_of_scope.not_applicable` | unchanged | PASS, FAIL |
| 3 | 1 | applicable true | — (continue) | — | unchanged | — |
| 4 | 5 | cells_bound == 0 | `ERROR` | `error.cells_bound_zero` | **INVALID** | PASS, NOT_RUN |
| 5 | 2 | declared key absent or mistyped | `NOT_RUN` | `not_run.source_unreadable` | unchanged | PASS, FAIL |
| 6 | 3 | expr budget exceeded | `NOT_RUN` | `not_run.budget_exhausted` | unchanged | FAIL |
| 7 | 3 | expr runtime error | `ERROR` | `error.predicate_raised` | **INVALID** | NOT_RUN, PASS, FAIL |
| 8 | 3 | expr false | `FAIL` | — | unchanged | — |
| 9 | 3 | expr true | `PASS` | — | unchanged | — |

## Rows 4 and 7, against each other

A predicate that **raised** is an apparatus failure — fix the code. A source that could
not be read is `not_run.source_unreadable` — retry. **They have opposite remedies**, and
collapsing them into one outcome is NC-E01: a crash that looks like a limit.

## Rule 4 is not a transition

It is composition, and it is the sentence the whole contract rests on: **a verdict is
never fresher than its stalest input and never stronger than its weakest.**

- `compose_warrant` takes the **minimum** under `DETERMINISTIC > MODEL_EXTRACTED >
  DERIVED`. The empty set **raises** rather than returning the strongest warrant — a
  value derived from nothing is not deterministic, and order 4 already owns that case.
- `compose_retrieved_at` takes the **minimum**, i.e. the OLDEST retrieval. The plan's
  interface block annotates it `# max`, two lines below its own statement of the rule;
  the two cannot both hold, and `min` is the one that makes the sentence true. Under
  `max` a verdict composed from a January snapshot and a filing read today would report
  today, and a reader would take the whole verdict to be that fresh.
