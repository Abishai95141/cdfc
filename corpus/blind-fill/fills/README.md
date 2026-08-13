# corpus/blind-fill/fills — five blind fills, and what they are worth

**Five fresh model instances filled the FME return.** Each received the workbook's own field
labels, the regulator's own data validations and permitted vocabularies, and an instruction to fill
correctly and plausibly as a compliance officer would. **None received any predicate, expression,
report or gate output.**

`filler_task.json` is exactly what they were given — 454 fields. `fill_groups.json` maps each field
id to the cells it covers. `fill_00N.json` is each filler's answer: a value list per field, cycled
across that field's rows.

## They license NO tier, and the code enforces it

`person_a_kind: "model-instance"`, and `severity.BLOCKING_REQUIRES_PERSON_A == "human"` refuses
`BLOCKING` on that value **however large `n` grows**. A corpus filled by instances of the same model
that wrote the predicates is nearer to *"we generated it"* than to *"the world produced it"* — F2 at
the level of the mind rather than of the code — and the same answer applies: keep the evidence,
refuse the tier.

## Three weaknesses, stated where the fills are

1. **The fillers share our weights.** If the harvest misreads a construct, a sibling reading the
   same blank can make the same misreading.
2. **The regulation was not available to them** (D-P7-01), so they had the blank alone. The fills
   are PLAUSIBLE, not certified correct.
3. **Only the regulator-validated fields were offered** — 2,323 of the 3,747-cell surface. The rest
   take the same declared default the seeded generator uses. A PARTIAL blind fill.

## What they are for

To FIND DEFECTS the seeded generator cannot. `P-0009` — a COUNTIF wildcard translated as a string
equality — was caught only because inputs varied. These fills vary them plausibly rather than
uniformly, which is the one thing `randint(1, 5)` cannot do.

`tools/corpus/blind_fill_probe.py` consumes them. **It has not yet produced a measurement**: the
run exits without output and without a traceback, and the cause was not diagnosed. Treat
`docs/measurements/P8-blind-probe.md` as ABSENT, not as zero.

## One defect these fills already found, before any of them was run

The task file's original id was `<sheet>|<column>`, which is **not unique**: 454 distinct stacked
fields collapse onto 103 such keys. A JSON object could carry only 103 of the 454 decisions, and
every stacked field sharing a column would have been given the same values. **The first filler
flagged it in its reply** rather than quietly emitting 103 keys. Had it not, predicates would have
fired on that collapse and the fires would have looked exactly like a real defect.
