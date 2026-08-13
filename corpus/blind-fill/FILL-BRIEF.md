# corpus/blind-fill/FILL-BRIEF.md — the instructions given to Person A

**HASHED AND PUBLISHED BEFORE THE FIRST WORKBOOK IS FILLED.** `test_corpus__brief_predates_first_workbook`
asserts that this file's commit is an **ancestor** of the first filled workbook's commit, read from
the corpus repository's git history. *A commitment made after seeing the result is not a
commitment, and here the git history is the evidence.*

**No workbook has been filled.** D-P8-01 records why: this is 15–25 person-days of somebody who has
never seen the predicate set, and no such person exists on this project. The brief is committed now
so that the ancestry holds by construction on the day one does.

## What Person A receives

1. The pinned blank: **FME `7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39`**.
2. The regulation, as published by the Authority.
3. This brief.

## What Person A NEVER receives

`src/cdfc/predicates/`, `predicates.json`, any report this product has produced, any list of
checks, any gate output, and no member of the plan or the specification. **Not a summary of them
either.**

## The task

Fill **at least 30** copies of the blank **correctly**, per the regulation, as if filing them.

* Do not consult anyone on the build team about any cell.
* Record a **stopwatch time per workbook**.
* Vary the filings as a real population would vary: the declared strata are in `SLICES.md`, which
  is hashed with this brief so the held-out slice pre-exists the corpus.

## The instruction that is a measurement rather than housekeeping

> **Record every cell you could not fill, and why.**

A cell a competent filler cannot complete from the template and the regulation alone is **evidence
about the instrument**, not noise. Those rows feed `no_predicate.rule_ambiguous` and
`no_predicate.no_obligation_specified`, and they are **the only independent read anyone on this
project will get on which parts of the return are underspecified.**

## What the manifest must carry, per workbook

`sha256` · `filler_id` · `elapsed_minutes` · `cells_written[]` · `cells_left_blank[]` ·
`blank_reasons[]`.

`cells_written[]` is not bookkeeping: it is the input to **F36**, the only external instrument in
this plan that can falsify the 3,747-cell denominator. `tools/corpus/mask_vs_filler.py` publishes
two integers from it — cells a filler wrote that lie OUTSIDE the mask (the mask is too small, and
every settled fraction then overstates coverage) and cells inside the mask no filler ever wrote.

## If Person A is a model instance rather than a human

The fallback is pre-decided and it is **weaker**. The fill prompt is hashed and published before
the first workbook; `corpus_provenance` stays `BLIND-FILLED` **only if** the instance was never
shown the predicate set; and the record carries `person_a_kind: "model-instance"`, **which renders
wherever the FFR renders**. It does not silently become a number that looks like a person's.
