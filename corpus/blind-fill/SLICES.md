# corpus/blind-fill/SLICES.md — the held-out slice, DECLARED BEFORE THE CORPUS EXISTS

Hashed with `FILL-BRIEF.md`. **A slice chosen after the corpus is filled is a SUBGROUP ANALYSIS**,
and it is labelled one on every surface. This file exists so that cannot happen quietly.

## The strata Person A fills across

| stratum | what varies | target share of the corpus |
|---|---|---|
| `S1` | close-ended **restricted** schemes | ~1/4 |
| `S2` | open-ended **retail** schemes | ~1/4 |
| `S3` | schemes with **zero** portfolio rows (a lawful empty return) | ~1/8 |
| `S4` | schemes at or near a declared bound (the largest lawful values) | ~1/8 |
| `S5` | everything else | the remainder |

## The held-out slice

**`S1` — close-ended restricted schemes.**

It is held out entirely from any tuning, threshold selection or predicate repair, and its FFR is
reported SEPARATELY in `qualification.g4.heldout` with its own `n` and its own interval. A rate
computed over a corpus that shaped the predicates is a rate about the predicates' authors.

`S1` is chosen because it is the stratum whose obligations the regulation delegates most — reg
51(1)'s *"in such manner as specified by the Authority"* — so it is where a predicate is most
likely to be wrong for a reason nobody noticed.

## The rule, stated before the corpus exists

* the slice is never used to choose a threshold, a tolerance or a marker;
* a predicate repaired after seeing `S1` moves the slice's status to `CONTAMINATED` on every
  surface and its FFR is republished as a subgroup analysis;
* `qualification.g4.heldout` is `null` **with a reason** where no slice exists, never absent.

Today it is `null`, and the reason is D-P8-01: there is no corpus.
