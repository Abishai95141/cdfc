# D-P10-01 — a cell with no value is `ABSENT`, and `_coerce(None)` raises

**Found by the thing built to find it.** P10's canary loop replays each admitted predicate's stored
kill case against the filing under test and asserts the predicate still returns `FAIL`. Its first
run over the committed campaign reported **81 of 125 predicates silent** — the loop's own alarm for
*the check is dead*.

The check was not dead. **The recorded kill was.**

## The mechanism, on one mutant

`facts/build.py::_coerce` begins `text = str(raw)`. Called with `None` it returns the
four-character string `"None"`. `measure/p6_kill.py::_patch` called it with exactly that:
`calc.recalculate` returns `None` for a formula cell whose input has been blanked, and every such
cell entered the mutant's fact tree as the string `"None"`.

Mutant `edfc99e6` is `F05.b` — blank `'1. Introduction'!D11`. `D40` is the formula `=D11`.

```
filing.n_1_introduction.r11.cd.v  ->  ''        the blanked cell, patched with ""
filing.n_1_introduction.r40.cd.v  ->  'None'    D40 = D11, uncomputable, coerced
```

`P-0012` is `filing.n_1_introduction.r40.cd.v == filing.n_1_introduction.r11.cd.v`. Its recorded
kill is `'' == 'None'` evaluating to false. **The predicate did not catch the fault. It compared
two coercion artifacts, and the campaign banked the result as evidence that the check works.**

Pre-flight did not stop it and was right not to: neither key's type is inferable from
`a.v == b.v`, so D-P5-03's rule made it presence-only, and both keys were present. The guard was
working correctly on a fact tree that should never have existed.

## Decision

**A cell with no value is `ABSENT` — not `""`, not `0`, and not the string `"None"`.**

1. `_coerce(None)` **raises `FactError`**, so the defect is unrepresentable rather than
   discouraged. Nothing legitimate called it that way: `filing_tree` skips a cell the workbook does
   not carry (`if ref not in values: continue`), which is what absence already meant.
2. `facts/patch.py` becomes the **single** fact-tree patcher, shared by P6's campaign and P10's
   canary loop, and its `value_for()` maps `None` and `""` to the `ABSENT` sentinel. An `ABSENT`
   patch **deletes the leaf's `v`**, which is byte-for-byte the shape `filing_tree` produces for a
   cell the workbook does not carry.
3. A predicate over an absent declared key therefore reports `NOT_RUN(source_unreadable)` at
   pre-flight, which is the honest answer: **an equality has nothing to compare.**

## Why one patcher and not two

The canary's whole claim is *this predicate still catches the fault it was admitted for*. If the
campaign patches the fact tree one way and the canary another, the loop tests whether two
implementations of one idea agree — not whether the check works. Sharing the module is what
surfaced this in the first place, because the disagreement had nowhere to hide.

## What it costs, and the direction it costs in

**`K` falls.** Every kill that rested on a comparison against `"None"` disappears, and with it the
`F05` and `F07` blank-out classes' contribution to the kill rate. `docs/measurements/P6-fault-model-v3.md`,
`docs/measurements/P7-attrition.md` and the campaign manifest are all regenerated, and the deltas are
published in `docs/measurements/P10-canary-cost.md`.

The number moved **against us**, which is the only direction a repair to a headline number is
allowed to move without further argument.

## Alternative it beat

Keeping `"None"` and adding a rule that pre-flight refuses it. Rejected: that leaves a value in the
fact model whose only purpose is to be recognised and rejected downstream, and every future reader
of a `v` field has to know about it. `ABSENT` is already the model's own answer, stated in
`facts/build.py`'s docstring since P5 — the defect was that one caller did not route through it.

## Mechanised by

- `tests/unit/test_fact_patch.py::test_patch__none_is_absent_never_the_string`
- `tests/unit/test_fact_patch.py::test_patch__coerce_refuses_none`
- `tests/unit/test_fact_patch.py::test_patch__an_absent_patch_deletes_the_leaf_value`
- `tests/unit/test_fact_patch.py::test_patch__the_input_tree_is_unchanged`
- `tests/negative/test_nc_selfcheck.py::test_nc__C12a_a_none_coerced_kill_is_not_a_kill`
- catalogue entry `NC-C12`, injector `coerce_none_to_string`
