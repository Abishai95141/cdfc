# P6 — the fault campaign, model `v3`

**Warrant: MEASURED.** Produced by `make campaign`. Reports in
`reports/campaigns/fme-v3-seed20260810/`.

**What did not exist before this run.** `U/G` for OUR operator mix — the literature's comparable
figure, 3,512 of 7,500 = 46.8%, is a property of a different suite and must not be assumed for
ours. And `K/O` per class where **killed means a predicate returned `FAIL` under the eight-state
verdict model**, rather than a boolean.

## The sample, and its rule

Site universe: **4252** cells. Sampling rule, published because the number is a fraction of
it: `stratified by dtype, at most 12 sites per stratum, seed 20260810; 72 of 4252 field-surface cells (COUNT+F:12/378, DATE:12/23, ENUM:12/401, MILLI_USD_MILLION:12/1880, MILLI_USD_MILLION+F:12/127, TEXT:12/1443); plus 40 cell(s) that feed a formula this evaluator cannot compute, so the INDETERMINATE class is measurable at all rather than depending on which cells the RNG chose (30 such formula cells)`

Reducing the operator set to make the number look better is the manipulation this project bans.
Reducing the sample and saying so is arithmetic.

## The six integers

| class | G | U | I | O | R | K | K/O |
|---|---:|---:|---:|---:|---:|---:|---|
| F01 | 29 | 0 | 0 | 29 | 0 | 29 | `29/29` |
| F02 | 72 | 0 | 0 | 72 | 0 | 20 | `20/72` |
| F03 | 58 | 0 | 0 | 58 | 0 | 14 | `14/58` |
| F04 | 5 | 0 | 0 | 5 | 0 | 2 | `2/5` |
| F05 | 224 | 0 | 1 | 223 | 33 | 53 | `53/223` |
| F06 | 24 | 0 | 0 | 24 | 0 | 2 | `2/24` |
| F07 | 112 | 0 | 1 | 111 | 16 | 34 | `34/111` |
| F08 | 16 | 0 | 0 | 16 | 1 | 5 | `5/16` |
| F09 | 36 | 0 | 0 | 36 | 0 | 12 | `12/36` |
| F10 | 32 | 0 | 0 | 32 | 0 | 0 | `0/32` |
| F11 | 25 | 0 | 0 | 25 | 6 | 7 | `7/25` |
| F12 | 100 | 12 | 20 | 68 | 0 | 68 | `68/68` |
| F13 | 36 | 0 | 0 | 36 | 0 | 11 | `11/36` |
| F14 | 4 | 0 | 0 | 4 | 0 | 0 | `0/4` |
| **TOTAL** | **773** | **12** | **22** | **739** | **56** | **257** | **257/739** |

    U/G = 12/773      I/G = 22/773      K/O = 257/739

**`I` is our EVALUATOR, not the fault model, and it never renders without `U/G` beside it.** A cell
in `not_run` is identical in both grids *by construction*, so a two-way classification banks its
mutants as unobservable, removes them from `O`, and — because `O = G − U − I` — **raises** `K/O`.
The measurement error would be correlated with the quantity being measured, in the direction that
flatters us.

### `I = 0` on this campaign, and a zero is not the same as an absent column

The sample deliberately includes every cell that feeds a formula this evaluator cannot compute, so
the class is *reachable* rather than depending on which cells the RNG chose. It still measures
zero, and the reason is worth stating: **every operator in this model edits a cell whose own value
moves**, and the edited cell's literal is part of the comparison. A mutant is therefore observable
at its own site before propagation is considered, and `INDETERMINATE` — *the grids agree but we
could not adjudicate the path* — needs a mutant that is invisible at its own site. This model has
none.

The class is implemented, controlled and rendered anyway. A campaign whose operator mix did produce
one would count it, and `U/G` would still not absorb it.

### The cells behind every `I`

- **F05** — 
- **F07** — 
- **F12** — 

### What the `U = 12` actually are, because a rate is only as honest as its composition

All 12 are `F12.c` — the trailing-whitespace operator — applied to cells the clean filing holds
the integer `1` in. `"1 "` parses back as `1` through any numeric read, in this system and in
Excel: **the fault is one the format cannot carry.** That is precisely what `U/G` is for.

It is also partly an artifact of the fixture, and saying so is the point of publishing the
composition: the synthetic filing writes `1` into every field-surface cell that carries no data
validation, so the `TEXT` stratum is full of integers. A filing with real text in those cells would
move this number. **`U/G` is a property of our operator mix ON THIS FILING**, and neither half of
that sentence is optional.

## The v0 restatement

v0 published MS = 3574/19760 = 3574 killed over 19782 generated less 22 asserted equivalents. This build does not compute that form: `E` is a theorem and `U` is a diff. v0's 22 'equivalents' were all produced by the round-to-integer operator and were asserted, not proved. A further observation from v0 that is not arithmetic: every arithmetic operator killed at exactly 18.1%, identical to the fraction of sites inside the field graph — for identity predicates that number is REACH, not QUALITY, and this report says which it is showing.

## What this licenses, and what it does not

> The predicate set rejects **257 of 739** observable defects seeded under fault model `v3`, of
> which **12 of 773** were discarded as unobservable and **22 of 773** could not be
> adjudicated by our own evaluator.

It does **not** license *"detects X% of real filing errors"*. The bridge from seeded faults to real
ones is the coupling effect, and **there is no coupling study for financial filing data** — NC-N50,
where a negative control is impossible because no filed FME return is public and the denominator
does not exist.

**Three classes are designed misses.** `F10`, `F12`'s homoglyph form and `F14` are classes our own
predicates cannot catch by construction. **A per-class vector that is uniformly high would be
evidence that the model is too weak, not that the predicates are good.**
