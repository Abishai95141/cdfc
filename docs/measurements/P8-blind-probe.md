# docs/measurements/P8-blind-probe.md — the blind-fill probe

**THE PROBE DID NOT PRODUCE A FALSE-FAILURE RATE. It produced something worse and more useful: a
filing that makes an admitted predicate run without bound.**

## What was run

Five fresh model instances filled the FME return (`corpus/blind-fill/fills/`). Each received the
workbook's own field labels, the regulator's own data validations and permitted vocabularies, and
an instruction to fill correctly and plausibly. **None received any predicate, expression, report or
gate output.** All five covered 454 of 454 fields.

Each fill is expanded to cells, written by raw-zip surgery, recalculated by the pinned offline
engine, and run against the 348 admitted predicates.

## THE FINDING — `P-0054`, and the budget that does not bound it

    P-0054   numeric_bound   filing.n_2_summary.dv_f5.cells.all(c, c.v >= 0)   — 170 cells

On the blind-filled filing, evaluating **this one predicate** takes the process from **85 MB to
6 GB** and does not return. Measured, repeatedly:

| elapsed | resident |
|---|---|
| 2:07 | 6,083 MB |
| 2:43 | 5,205 MB |
| 3:37 | 6,011 MB |

**And the declared step budget does not stop it.** Re-run with `Budget(steps=2000)` — a budget so
small it should kill almost anything — `evaluate_one` still had not returned after 100 seconds.

`celrt.Budget`'s own docstring states the rule this violates:

> *"A declared budget nobody enforces is worse than no budget: it appears in the run record, a
> reviewer reads it as a bound, and nothing was bounded."*

That is the state. The budget appears in the run record. It bounds nothing here.

## Why this is a PRODUCT defect and not a harness artefact

* The same predicate, the same budget and the same 348-predicate set run to completion on **40**
  seeded `TEMPLATE-COMPUTED` filings (`docs/measurements/P8-ffr.md`). It is the FILING that
  changes the behaviour, not the predicate.
* Both filings are produced by the same writer and recalculated by the same pinned engine. The
  difference is the VALUES a filler chose.
* A checker that will be pointed at filings it did not generate **must terminate on every filing.**
  A filing that hangs the evaluator is a denial of service against the product delivered by its own
  input, and no gate in this system currently catches it: `G1` evaluates against ONE reference
  filing, and that filing is ours.

## What this does NOT say

* **It does not say which value triggers it.** The F-column values the filler wrote are `35, 18,
  12`; no recalculated value in that column is long or exponential. The trigger was not isolated.
* **It does not give a false-failure rate.** No `n`, no interval, no tier. Nothing downstream may
  quote a rate from this probe, because none was computed.
* **It does not license anything.** `person_a_kind: "model-instance"`, and
  `severity.BLOCKING_REQUIRES_PERSON_A` refuses `BLOCKING` on that value however large `n` grows.

## A defect in this harness, found on the way and recorded

`tools/corpus/blind_fill_probe.py`'s README stated that cells the filler was not offered take the
declared default. **The code did not do it** — ~900 unlocked cells were left empty. Fixed. It did
not resolve the runaway, so it is not the cause; it is a document that described a behaviour the
code did not have, which is this project's own subject matter occurring inside its own instrument.

## What has to happen next

1. **Isolate the trigger.** Evaluate `P-0054` against the blind filing with the fact tree dumped
   for `filing.n_2_summary.dv_f5.cells`, and find what makes `.all()` over 170 cells unbounded.
2. **Make the budget bound it**, whatever it is. A step budget that a real expression can escape is
   not a budget, and `test_g1__budget_exhausted_is_its_own_reason` currently passes because the
   expression it tests is one the budget CAN stop.
3. **Then** re-run this probe for the rate it was built to produce.
