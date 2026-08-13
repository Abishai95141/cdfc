# experiments/P8/PREREGISTRATION.md

**Committed and hashed BEFORE the first G4 run.** A threshold chosen after seeing the result is not
a threshold; it is a description of the result.

## The three constants

```
BLOCKING_MAX               = 0.02      # Wilson UPPER bound, never the point estimate
ADVISORY_MAX               = 0.10      # above this: NOT ADMITTED — this IS gate G4
BLOCKING_MIN_NON_SYNTHETIC = 30        # filings a PERSON or THE WORLD produced
```

All three live in `src/cdfc/qualify/severity.py` as module constants, and
`test_severity__thresholds_are_constants` asserts each by value so a change is a diff.

## The rule, stated before it was run

```
hi <= 0.02  AND  n_non_synthetic >= 30   ->  BLOCKING
hi <= 0.10                               ->  ADVISORY
hi  > 0.10                               ->  NOT ADMITTED
UNDEFINED (raises) where the provenance is SELF-AUTHORED,
          or where clean_corpus_independent_of_predicate is False
```

## The three predictions, recorded before the measurement

1. **`BLOCKING` will be `0`.** No non-synthetic corpus exists, so the floor cannot be met whatever
   the interval says. *If `BLOCKING` is non-zero, the floor is not being enforced.*
2. **Zero predicates will be refused a rate on a `FOREIGN_ENGINE` corpus.** Conjunct (1)'s escape
   hatch applies to every predicate, because the derivation shares no module with the evaluator.
   *If any predicate is refused, the closure computation disagrees with the design.*
3. **The measured FFR will be low but is NOT predicted to be zero.** The oracle is an independent
   engine; a disagreement between it and a harvested predicate is a real finding either way, and
   the direction it points is not pre-judged here.

## What this pre-registration does NOT cover

The corpus itself: `n = 30`, `seed = 20260813`, FME `7d9a1960`, `derived_by = FOREIGN_ENGINE`.
Those are recorded in `fixtures/corpus_manifest.json` at generation time. The pre-registration
covers the **decision rule**, which is the thing that could otherwise be tuned to the answer.

Dated 13 Aug 2026.
