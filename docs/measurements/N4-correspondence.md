# N4 — scoring the correspondence, and the comparison I could not make fair on the first three tries

*Run 20 Aug 2026. `tools/measure/n4_linkage.py`. Splink 4.0.16 installed for the comparison.*

## The linkage arm: ours against Splink, on a population built to hurt

The clean case discriminates nothing — three exactly-agreeing fields fit `m=1.0, u=0.0` and
anything wins. So the population carries what custodian data carries: **1 in 3 loses its
identifier, 1 in 3 has a name variant, 1 in 4 is rounded.** Ground truth is held by the generator
— a construction, not a judgement made afterwards.

    population   left 120   right 110   true matches 70

| | tp | fp | fn | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| **ours** (Fellegi-Sunter, EM) | 67 | 2 | 3 | 0.971 | 0.957 | **0.964** |
| **Splink 4.0.16** | 59 | 0 | 11 | **1.000** | 0.843 | 0.915 |

**This is NOT a ranking, and saying it were would be the shallow proxy this run exists to avoid.**
These are single points on two different operating curves: Splink is running at a 0.5
match-probability threshold and its perfect precision says it is being conservative there, not
that it cannot reach those 11. A fair ranking needs both curves, and this measures one point each.

### Three harness bugs, each of which flattered us

Recorded because the first three runs all favoured our implementation for reasons that had nothing
to do with the model:

1. **Blocking rules dropped the degraded records.** `block_on("name"), block_on("lei"),
   block_on("nav")` never compares a pair that agrees exactly on nothing — which is precisely the
   population the experiment is about. Replaced with a cartesian rule so every pair is compared.
2. **Blank identifiers agreed with each other.** `cl.ExactMatch("lei")` treats `"" == ""` as
   agreement, so 21 records with no LEI all "agreed"; our own `exact()` already requires a
   non-empty value. The two were not being asked the same question. Blanks are now `None`.
3. **A blocking rule that trained nothing.** `block_on("source_dataset")` produced no valid pairs
   for `link_only`, Splink logged *"m probability not trained for lei"*, and scored **0.000** —
   a result I could have published as a rout.

**The honest reading: ours works, and whether it beats Splink is not established here.**

## A defect the comparison found in our own EM

The first run reported `converged: False` after 200 iterations. The fit was sound — `m` moved from
0.7071 to 0.7053 over 150 wasted iterations — but the convergence test was an **absolute delta over
all parameters**, and `u` for a near-unique field is squeezed toward its floor where it keeps
shrinking by amounts that are tiny absolutely and large relatively. One tolerance cannot serve
parameters spanning six orders of magnitude.

Now it converges on the **observed-data log-likelihood**, which is the quantity EM monotonically
increases and is scale-free by construction: **converged in 54 iterations.** A number from a fit
that reports it did not converge has no warrant, and publishing it anyway is how an unwarranted
figure enters a record.

## The schema-matching arm (use 2)

Source columns matched to template fields with **no shared address space** — only meaning in
common. Ground truth is a construction: the headers are the fields' own labels.

    source columns 6   template fields 132   MATCHED 5 of 6   refused 1

All five verified correct against the workbook's own labels. The sixth, `Unrelated Column`, is
**refused rather than forced onto the least-bad field**. Weights are derived by the same EM as the
linkage arm, not chosen.

## What N4 does NOT establish

* **The independence criterion is UNMET.** `PLAN.md` specifies *"judged by somebody who did not
  write it"*. Every number here was produced by the author of the thing measured, on populations
  the author generated. The ground truths are constructions rather than judgements, which is the
  strongest available substitute and is not the same thing.
* **Valentine's own datasets were not used.** The Valentine *metrics* (precision, recall, F1 over
  a ground-truth matching) are what is computed; its published corpora are not in reach offline,
  so "beats the published baselines" remains unmeasured.
* **One population per arm.** Both are single draws under one seed.
