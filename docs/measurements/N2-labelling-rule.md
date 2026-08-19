# N2 — pinning the labelling rule, and what fell out of it

*Run 20 Aug 2026 at `4f9bbae`. Prerequisite for any measurement over labelled fields.*

`M-CEIL` found the labelled population moving by a factor of six across three readings of *"this
field has a label"* over the same 3,747 cells, and said the rule had to be pinned **before**
anything was measured over it. This pins it — and reading the labels turned up three further
things, each of which had been counted as a field.

---

## Stage 1 — four rules, and the discriminator is not the count

| rule | labelled | distinct labels | **fields per label** |
|---|---:|---:|---:|
| **ADJACENT_LEFT** — the cell immediately left holds text | 498 | 127 | **3.9** |
| NEAREST_LEFT — nearest text anywhere left on the row | 3,104 | 154 | 20.2 |
| NEAREST_ABOVE — nearest text above in the column | 3,592 | 156 | 23.0 |
| ABOVE_OR_LEFT — either | 3,609 | 241 | 15.0 |

**Fields-per-label is the discriminator, not the raw count.** A rule that names FIELDS gives each
one its own label. A rule that names ROWS hands a single header to every column in the row, and its
ratio blows out. `NEAREST_ABOVE` was measured because many forms label columns rather than rows;
on this return it is the worst of the four.

**`ADJACENT_LEFT` is pinned.** It is `PINNED_RULE` in `src/cdfc/evidence/fields.py` and travels on
every `FieldSet`, so a count carries the rule that produced it.

## Stage 2 — reading the labels, which is where three problems were

Pinning the rule was not enough. All 125 distinct labels under it were read, one by one.

**(a) 351 of the 498 "labels" are the literal string `NA`.** Verified against the workbook's own
cells: this return uses `NA` as filler in the column left of a field. Counting those as labelled
inflated the population fourfold.

**(b) Twelve more are instruction text or table captions** — nine numbered instructions
(*"1. Additional rows may be inserted to add more countries."*), two captions (*"Table 4.1: Details
of investors in Investment Fund"*), one bare lead-in (*"Note:"*). A field whose "label" is a
footnote has not been labelled.

**(c) The attestation rubric keyed on the word "whether" and was wrong.** It classified *"Whether
the sanction screening is manual or automated?"* and *"Whether FME has paid the applicable
recurring fees"* as attestations. **A source document can answer both.** Calling them attestations
would refuse to fill fields the system can evidence.

### The principle that replaced the word list

> **An ATTESTATION is a claim NO OBSERVATION CAN SETTLE.**

*"The FME is in compliance with the IFSCA (Fund Management) Regulations"* is a legal representation
over a whole body of obligations — no span in any document makes it true, and a system that ticked
it would be signing on the filer's behalf. *"Was there a true match against the UNSC list?"* is a
question about an event, and an event leaves evidence. The implementation follows the shape: a
declarative asserting compliance is an attestation; an interrogative is a report.

## The result

    field surface                        3,747
    labelled under the pinned rule         132        distinct 113   1.2 fields per label
      FACT-shaped                          124
      ATTESTATION-shaped                     8

**All eight attestations, in full** — these are what a human must sign, and no observation settles
any of them:

| cell | what it certifies |
|---|---|
| `8. Compliance Status!C4` | the FME and its operations are in compliance with the IFSCA (FM) Regulations |
| `8. Compliance Status!C6` | the net worth requirement has been complied with at all times |
| `8. Compliance Status!C8` | the FME has the necessary infrastructure |
| `8. Compliance Status!C9` | the FME, its fiduciaries and KMPs are in compliance |
| `8. Compliance Status!C10` | in compliance with disclosure requirements |
| `8. Compliance Status!C11` | in compliance with Investment Valuation Norms |
| `8. Compliance Status!C12` | distributors are in compliance with the code of conduct |
| `6. Complaints!C6` | the complaint-handling policy is in place |

## Every number this supersedes

| published | where | now |
|---|---|---|
| 724 labelled, 702 FACT / 22 ATTESTATION | `docs/spike/README.md` | not reproducible; the rule was never recorded |
| 498 labelled, 481 FACT / 17 ATTESTATION | `M-CEIL`, `EVIDENCE-LAYER` | **132 labelled, 124 / 8** |
| 3,104 with 154 distinct | `M-CEIL` | 726 with 152 distinct once placeholders are excluded |

**The shape held through every correction and the ratio did not.** The return is overwhelmingly
factual and the attestations are a small, localised minority — true under all of them. But
attestations are **8 of 132**, about one labelled field in sixteen, not the 22 of 724 first
published.

## What this does NOT establish

* **One adjudicator is one adjudicator.** All 125 labels were read by the same person who wrote the
  rubric. The repository's own standard says that measures one person's idea of an attestation, and
  a second named adjudicator with published agreement is the thing that would settle it. That is
  the same human blocker that gates the rest of the semantic half.
* **One return.** Placeholder conventions, instruction styles and certification phrasing are this
  form's. `PLACEHOLDER` and `_NON_LABEL` are closed lists derived from it by enumeration, and the
  first genuinely different return will extend them.
* **132 of 3,747 is not a coverage claim.** It is how many fields this reader can NAME. The other
  3,615 are unlabelled under this rule, and `G-FIELD` reports a citation to one as
  `field_not_labelled` — a gap in what we can read, distinct from a bad citation.
