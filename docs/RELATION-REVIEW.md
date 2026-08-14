# RELATION-REVIEW.md — every relation drafted, admitted or refused

**APPEND-ONLY.** A row is never edited in place and never deleted. **The refusals are the evidence
that the authoring protocol did anything**, and the phase's own failure branch says they are the
more interesting result: a smaller, more interesting paper than the one where a round number of
relations shipped unexamined.

**Every row on this page is `SINGLE-SIGNER — a weaker review`.** `plan/05` P9-B2 ruling (c)
budgets 2–3 person-days of a second person's calendar for the review signatures. There is no
second person on this project. The rule it gives for that case is followed exactly: one signature,
the literal label on every affected row, and that label rendered beside every relation-derived
number on the report surface — not in a residue section.
`tests/unit/test_relation_registry.py::test_reg__two_signatures_or_the_weaker_label` refuses a row
that has one signer and no label, so the third option — a row that quietly has one signature and
says nothing — is unreachable.

## The protocol, and what each step refuses

| step | the question | who refuses |
|---:|---|---|
| 1 | name the artifact fact — a cell range, a formula, a guidance note, a validation | the loader, on an empty `evidence` |
| 2 | `NECESSARY` (violation ⇒ `FAIL`) or `EXPECTED` (violation ⇒ `INFORMATIONAL`) | the loader, and an `EXPECTED` row with no `guidance_note` |
| 3 | write the non-degeneracy precondition **first** | the loader, on an empty `precondition` |
| 4 | declare the basis set — one member | `basis.assert_single_basis` |
| 5 | declare the degree map and `claims_fault_classes`, **before any campaign** | the loader, on an empty claim set |
| 6 | check for redundancy against the harvested set | the reviewer, and the removal is recorded — see R-04 below |
| 7 | two humans sign | the loader, or the weaker-review label |

*"It seems like it should hold"* is a refusal at step 1. *"Whichever classes it turns out to kill"*
is a refusal at step 5 — a denominator chosen after the result is not a denominator.

---

## Admitted — 6

| id | title | class | necessity | review |
|---|---|---|---|---|
| **R-01** | `TEMPLATE_DIFF` — the filed value against the template's own formula over filed inputs | `FILING_AND_BLANK` | NECESSARY | 14 Aug 2026 · SINGLE-SIGNER — a weaker review |
| **R-02** | Funds-raised partition — the investor-category and accreditation breakups must agree | `FILING_ONLY` | NECESSARY | 14 Aug 2026 · SINGLE-SIGNER — a weaker review |
| **R-03** | Scheme-total consistency against the full nine-member vocabulary | `FILING_ONLY` | **EXPECTED** | 14 Aug 2026 · SINGLE-SIGNER — a weaker review |
| **R-05** | Denominator self-agreement | `SELF_TEST` | NECESSARY | 14 Aug 2026 · SINGLE-SIGNER — a weaker review |
| **R-06** | Canary-population self-agreement | `SELF_TEST` | NECESSARY | 14 Aug 2026 · SINGLE-SIGNER — a weaker review |
| **R-07** | Prior-period opening/closing continuity | `TWO_CONSECUTIVE` | NECESSARY | 14 Aug 2026 · SINGLE-SIGNER — a weaker review |

---

## Refused — 2

### R-04 — *Vocabulary closure under the pinned blank* · REFUSED at step 6, redundant

**Drafted as:** every categorical cell holds a term from `Dropdown`, resolved from the **blank**,
never from the filing. The artifact fact behind it is real and was verified first-hand: `Dropdown`
is `state="hidden"` and is **the only unprotected sheet of the ten** (MEASURED 14 Aug 2026), so a
relation resolving its vocabulary from the *filing* would validate the filer against a list the
filer can edit.

**Refused because the harvest already does exactly this, and does it from the blank.** `P-0017`:

```
filing.n_1_introduction.dv_g54.cells.all(c, c.v == "" || c.v in template.vocab.n_1_introduction_g54)
```

`template.vocab.…` resolves from the pinned blank by NC-D01c, so the property R-04 was drafted to
add is already asserted, by 20 harvested membership predicates over the validation ranges.
Admitting R-04 would have inflated the before/after delta with a rename — NC-R07's mechanism,
committed by the author of the relation set.

**The removal is recorded rather than silent** (NC-Q07d). Guard:
`tests/unit/test_relation_registry.py::test_reg__R04_is_refused_because_the_harvest_already_asserts_it`,
which fails if `P-0017` ever stops existing — because then the refusal would have removed a real
relation and left nothing in its place.

### R-02's country arm — *the third breakup* · REFUSED, inexpressible in the admitted subset

**Drafted as:** the per-scheme totals must also agree with Table 4.3's country-wise breakup, making
the partition three-way rather than two-way.

**The artifact fact is the strongest of the three** — Table 4.3 has **no total row and no total
column**, so nothing in the workbook relates it to either of the other breakups. But the relation
cannot be written:

- the sum would be over ten country cells per scheme, and **a blank numeric cell is *absent* from
  the fact model, not zero** (F05's blank-and-zero distinction, which the fault model carries as
  two operators). A `has()`-guarded sum is un-runnable on any filing that leaves one country
  blank, which is every filing;
- summing over a range needs a range host function that does not exist, and adding one to admit a
  relation would be widening the subset to fit the check rather than the other way round.

**Recorded rather than dropped**, because the fact it rests on is the most interesting one on the
sheet and it is what a range-aware successor should be built for. The two-way partition R-02
admits is the part that can be checked today, and it is checked.

---

## The counts, and where they come from

Both are **computed**, never written down: `registry.CATALOGUE_SIZE` for admitted, and the rows of
this file for refused. `docs/measurements/P9-relation-runnability.md` publishes the split on the
day the catalogue was written, not discovered later. A layer that quietly ships `n − k` relations
while claiming `n` is the coverage lie in miniature — and a layer that claims a round number it
chose before authoring anything is the same lie, one document earlier.

**The stopping rule for further authoring, pre-registered:** authoring stops when three consecutive
candidates are refused at step 1 for want of an artifact fact. That is the corpus telling us the
ground is exhausted, and it is a publishable finding. Two of the first eight candidates were
refused, neither at step 1, so the ground is not exhausted.
