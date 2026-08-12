# P3 — THE TWO EVALUATION SUBSTRATES · plan

**Barrier 2. Gate G-EVAL. Experiment E11.** 17 engineer-days (B1 2.0 · B2 1.5 · B3 1.5 · **B4 12.0**),
**plus 1.5 person-days of a second author that are not the engineer's** and that block the gate.

Entry criteria are met: P2 complete, field surface published, G-DENOM 9/9, `StableKey` frozen, the carry
graph read (294 authored formulas, 195 cross-sheet), and `calc/` is inside the float scan set.

---

## 1. What P3 settles, and the fact that reshapes it

Everything downstream depends on the evaluator. No evaluator → no observability filter → no `O` → no
`K/O` → gate G2 measures **reach** rather than **quality**. And `TEMPLATE_DIFF` — predicate #1, the only
check in the design that detects a formula cell overwritten with a literal — is unbuildable without it.

The obvious way to validate it is the regulator's own cached values: recalculate the 505 formula cells and
compare. **I measured that control before planning around it.**

> **The blank FME template's 505 formula cells carry exactly TWO distinct cached values: 301 `0` and
> 204 `"NA"`.** Warrant MEASURED, denominator 505, re-derivable with `tools/measure/cached_values.py`.
>
> **A stub returning `0` for every numeric cell and `"NA"` for every text cell scores 100%.**

So the positive control that gates every kill rate in this system, as originally posed, **contains no
information.** Arm 1 cannot distinguish a correct evaluator from a constant. This is not a reason to skip
the comparison — a *disagreement* would still be real evidence of a defect — but agreement on it is worth
nothing, and P3 must not report it as though it were.

**Consequence: G-EVAL gets two arms, and the phase publishes two numbers with two denominators.**

| arm | what it compares | what agreement is worth |
|---|---|---|
| **1** | evaluator vs the template's cached values, n = 505 | **near zero.** A constant scores 100%. Reported with that sentence attached, always |
| **2** | evaluator vs an expectation file authored by a SECOND PERSON over a discriminating filled workbook | **the actual gate.** This is the only arm that can fail for a real reason |

### And a finding the spec did not have — the corpus already contains a discriminating control

The plan's §0.2 N1 measured the FME workbook alone. Measuring all nine changes the shape of this phase:

| workbook | formula cells | distinct cached values | trivial | verdict |
|---|---:|---:|---:|---|
| **Draft ACAC** | **112** | **44** | **0.0%** | **DISCRIMINATES** |
| ITFS monthly | 32 | 7 | 59.4% | partial |
| AL monthly | 161 | 38 | 70.8% | partial |
| CMI quarterly | 33 | 2 | 75.8% | partial |
| ALR | 645 | 2 | 99.8% | vacuous |
| IBU Operations | 7 | 1 | 100.0% | vacuous |
| **FME quarterly** | **505** | **2** | **100.0%** | **vacuous** |

Corpus-wide: 1,495 formula cells, 1,314 trivial (87.9%) — and **181 non-trivial cells that already
constitute a real control, authored by the regulator rather than by us.**

**This is better than a manufactured fixture**, because a fixture we generate to test our evaluator is
still ours. Draft ACAC's 112 cells with 44 distinct values were computed by Excel on the regulator's
machine, and nothing about them was chosen with our implementation in mind.

**It does not remove the need for a second author** — 181 cells exercise whatever functions those
workbooks happen to use, and arm 2 is what covers the ones they do not, notably
`AGGREGATE(15,6,…)` over an array. But it substantially de-risks the phase: arm 1 becomes a real check on
seven workbooks instead of a vacuous one on the flagship, and it can run on day one, before any second
author is scheduled.

**Arm 1 is therefore re-specified: run it against the whole corpus, report per workbook, and rank by
trivial share.** A single corpus-wide percentage would average a control that discriminates against six
that do not — the same defect as a single /72 agreement figure.

---

## 2. Builds

### P3-B1 — the two-document fact model · 2.0 d
Exactly two bound names, `filing` and `template`, over which every predicate will ever be written.
Every leaf carries `__cell__` — no exceptions, tested over all 3,747 field-surface cells. `template` is
resolved from the **pinned blank digest** and never from the filing. Money is scaled to
`MILLI_USD_MILLION` here, **once**. No clock, no network, no filesystem below `build`.

### P3-B2 — units and tolerance · 1.5 d
`int64` counts of 10⁻³ USD Million. Half-ulp 5 units, `τ(n) = 5n` for an n-summand sum. `Decimal` under a
pinned context **from the first line**, never floats converted later — R4 puts `calc/` in the float scan
set precisely so this cannot drift in.

### P3-B3 — the provenance anchor union · 1.5 d
Every value carries where it came from, composing by weakest input.

### P3-B4 — the formula evaluator · 12.0 d — **the phase**
- `calc/graph.py` — topological sort over the carry edges. **A cycle is `NOT_RUN`, never a guess.**
- `calc/functions.py` — the vocabulary is **nine** functions, not eight.
- `calc/operators.py`, `calc/errors.py` — the six Excel error values as first-class.
- `calc/evaluate.py` — `recalculate(..., formula_source: "TEMPLATE" | "FILING")` with **no default**.
  Every call site states which formulas it means; the defect it prevents is comparing a filing against
  formulas the filing itself supplied.

---

## 3. The one thing that blocks the gate, and it is not code

**Arm 2 needs an expectation file authored by someone who is not the person who wrote the evaluator.**
Otherwise the gate under every kill rate in the system resolves to a self-check: the author's
understanding of `AGGREGATE(15,6,…)` would be compared against the author's implementation of it, and they
would agree for the same reason.

**1.5 person-days, a different person, and the plan budgets it as person-days rather than engineer-days
precisely so it cannot be quietly absorbed.** This is the same class of open item as Person A for the
blind-fill corpus, and it should be settled in the same conversation.

**If no second author is available**, the honest branch is: build the evaluator, run arm 1, publish
`K/G` (reach) rather than `K/O` (quality), label G2 a *reach* measurement everywhere it appears, and mark
`TEMPLATE_DIFF` as specified-not-admitted. That is a smaller system that still ships — which is the rule
every gate in this plan is written to.

---

## 4. Exit gate

1. The evaluator reproduces cached values **per workbook, reported per workbook**, never as one corpus
   figure. FME's 505/505 ships with "a constant scores 100% here"; **Draft ACAC's 112 is the row that
   carries information** and is the one to read first.
2. **Arm 2 green on the discriminating fixture**, against a second author's expectations.
3. `formula_source` has no default at any call site (AST-checked).
4. No float anywhere in `calc/` (`ci/no-float-money.sh`, a new gate row).
5. A cycle produces `NOT_RUN` with a reason, never a value.
6. `docs/measurements/P3-evaluator.md` publishes **both arms with both denominators**, and never one number.

**If arm 1 exceeds 25 failures:** those cells are excluded from the site set and flagged
`INDETERMINATE(engine_disagreement)` from a pinned table, G2 downgrades to a reach measurement reported as
`K/G`, and `TEMPLATE_DIFF` is deleted. Written down now, before the run.

---

## 5. First three builds, in order

1. `tools/measure/cached_values.py` — **built and committed**; the two-arm design now rests on a
   reproducible measurement over all nine rather than a remembered one over one.
2. `src/cdfc/facts/fact_table.py` (B1) with `test_fact_table__two_names_only` and the `__cell__` test over
   3,747 cells.
3. `src/cdfc/calc/errors.py` + `operators.py` under `Decimal` (B2), before any function exists — the
   numeric contract first, the vocabulary second.
