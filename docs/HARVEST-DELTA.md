# docs/HARVEST-DELTA.md

**Append-only.** Every movement of a harvest count, with a reason and a date. The golden tests read
the expected values from the LAST entry, so **moving a number without appending here fails the
build** — and the first thing P7's G3 will do is reject predicates, which will move these numbers
downward. A regression test that fails on correct behaviour gets deleted; a number that moves with
no recorded reason does not get past this file.

---

## Entry #1 — P4-B4's first harvest, 12 Aug 2026

**MEASURED: 592 candidates across the nine prescribed workbooks, non-empty on 7 of 9.**
Baseline for comparison: `fixtures/baselines/harvest-v0.json`, the frozen research harvest,
515 predicates. Command: `cdfc harvest --all`.

| workbook | v0 | P4-B4 | delta | v0 weak | P4-B4 skips |
|---|---:|---:|---:|---:|---:|
| `ALR_V2_3_20250808_1024.xlsx` | 19 | **32** | +13 | 234 | 2 |
| `AL_monthly_report_updated_final_20260717_0257.xlsx` | 16 | **16** | +0 | 43 | 0 |
| `Draft_ACAC_Format_20260605_0631.xlsx` | 0 | **0** | +0 | 9 | 0 |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx` | 1 | **1** | +0 | 0 | 0 |
| `IBU_Operations_Report_V2_3_20250808_1033.xlsx` | 10 | **10** | +0 | 1 | 0 |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx` | 0 | **0** | +0 | 0 | 0 |
| `ITFS_Monthly_report201220241626.xlsx` | 26 | **25** | -1 | 22 | 2 |
| `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` | 280 | **351** | +71 | 68 | 178 |
| `Updated___Quarterly_Reporting_Format_for_Capital_Market_Intermediaries_20260409_1019.xlsx` | 163 | **157** | -6 | 12 | 127 |
| **total** | **515** | **592** | **+77** | 389 | 309 |

### Why it moved, and both reasons are defects in v0 rather than changes of policy

1. **Shared formulas are now materialised.** v0 read `<f>` text and a shared dependent carries
   none, so 211 of FME's 505 formula cells were invisible to it. P4-B4 shifts each master's
   expression to its dependent's cell. This is the whole of the increase on FME and ALR.
2. **A body that is not exactly one call is no longer counted.** v0's greedy `^SUM\((.+)\)$`
   counted `SUM(A1:A5)+SUM(B1:B5)` as a `sum_identity` while deriving no expressible relation from
   it. P4-B4 counts parentheses and emits a typed `function_outside_vocabulary` skip instead — 58
   of them on FME. **The harvest under-produces and declares it.**

Both are recorded in `fixtures/baselines/README.md` beside the frozen file.

### The three numbers this entry pins for the goldens

- `test_golden__harvest_count__fme` -> **351**, with the class vector in
  `docs/measurements/P4-harvest-distribution.md`.
- `test_golden__cross_workbook_harvest_distribution` -> **592**, with all nine rows attached.
  Never the total alone: 508 of 592 come from two workbooks.
- `test_golden__zero_formula_template__edr1` -> **1** membership predicate on `230a6f0c`, and a
  mechanically derivable settled fraction of 0%. **Published anyway.**

### The `static_settled_cells` divergence, carried here as a finding

`len(cells_reachable)` for `7d9a1960` is **2,854**. The specification's figure is **2,373**
(`DERIVED-FROM-SPEC`). **Delta +481.** The spec attributed 2,329 of 2,373 settled cells to *53
validation predicates*; this harvest emits 20 membership + 12 numeric + 11 integer + 5 date = 48
validation predicates from a different class set, and 303 formula-derived ones the spec's figure
does not obviously account for. Either 2,373 was computed from an enumeration this build does not
produce, or the 53 is wrong. **It is published as a divergence and is not reconciled by adjusting
the harvest.** `2,373` is pinned as a literal in no golden test at this phase.

---

## Entry #2 — P5 refuses a bound outside int64, 12 Aug 2026

**MEASURED: 572 candidates across the nine, down from 592.** FME falls from 351 to 349.

**Why it moved.** A `decimal` validation on `'3. Portfolio'` declares an upper bound of
9.99999999999999E+21 — about a thousand times the int64 ceiling. P4 emitted it as a CEL integer
literal, and at P5 the runtime **exhausted memory** on that one predicate and the run was killed.

Two repairs, and both are refusals rather than approximations:

1. `harvest_classes/_bounds.py` refuses a bound outside int64 and emits a typed `dv_no_type` skip
   naming it. Money is an int64 count of 10^-3 MILLI_USD_MILLION, so a threshold that large is
   outside the model — and **a predicate whose threshold cannot be represented is a skip, not a
   predicate with an approximated threshold.**
2. `cel_profile` bans an integer literal outside int64 outright, with its own sentence. The
   runtime does not merely reject such a literal; it exhausts memory trying to represent it.

**A second movement in the same entry, and it is a code change rather than a count change.** The
bound classes no longer emit a `c.v == ""` blank arm. A bound is over NUMBERS, and comparing an
integer to a string is a TYPE ERROR in CEL rather than `false` — five predicates on the clean
filing produced `ERROR(error.predicate_raised)` and invalidated the run. The arm was also
unnecessary: a blank NUMERIC cell is ABSENT from the fact model (F05 — blank is not zero), so it
never reaches `.all()`. Removing it makes the inferred type unambiguous, which moves a text value
in a numeric column from `ERROR` (our apparatus failed) to `NOT_RUN` (the source could not be
read) at pre-flight — **the honest state, and one with a different remedy.**

### The three numbers this entry pins for the goldens

- `test_golden__harvest_count__fme` -> **349**
- `test_golden__cross_workbook_harvest_distribution` -> **572**
- `test_golden__zero_formula_template__edr1` -> **1**

## 13 Aug 2026 — P7-B1: `obligation_id` gains a construct-kind discriminator

**Nothing about the harvest's OUTPUT moved. Every id did.** `obligation_id` is now
`OBL-TEMPLATE-<F|V>-<sheet>-<ref>`; it was `OBL-TEMPLATE-<sheet>-<ref>`.

**The defect.** `1. Introduction!D17` on the FME blank carries **both** a formula (`=SUM(D18:D20)`)
and a `whole >= 0` data validation. Those are two different obligations — *the total equals its
parts* and *this cell is a non-negative whole number* — and under the old scheme they shared one
id. The obligation's verbatim quote would then have been whichever harvest class ran last, and one
of the two predicates would have been checked at G0 against a construct **it was not derived
from**. `cells_would_have_covered` and the rejection reason would both have named the wrong
relation.

One instance across all nine workbooks, and it was found by an equality assertion in `harvest()`
rather than by inspection: a second class recording a DIFFERENT construct for one obligation now
raises instead of overwriting.

**The counts, all unchanged.** The pins below are re-stated rather than referenced, because
`tests/golden/test_harvest_count.py` reads them from the LAST entry of this ledger — so an entry
that changed something else and dropped them would leave the harvest unpinned:

- `test_golden__harvest_count__fme` -> **349**
- `test_golden__cross_workbook_harvest_distribution` -> **572**
- `test_golden__zero_formula_template__edr1` -> **1**

and, new at this phase, `total obligations` -> **572** — one per candidate, injective for the
first time.

**What moved:** every harvested envelope's `code_sha256`, because `obligation_id` is inside
`envelope_projection()`. That is correct rather than unfortunate — a candidate whose obligation is
a different obligation IS a different predicate. Nothing was admitted under the old digests: the
registry has refused unconditionally since P0 and P7-B4 is the build that changes it.

The two committed fixtures moved with it, and `docs/measurements/P4-envelope-digests.md` carries
both new values with this reason.


## 13 Aug 2026 — P8: a wildcard COUNTIF leaves the harvest, found by the first measured FFR

**`P-0009` fired on 18 of 40 clean filings and was refused at G4.** The FME blank declares
`1. Introduction!D19` as `=COUNTIF(G54:G63, "*Restricted*")`. In Excel and in LibreOffice the `*`
is a **wildcard**: the criterion counts every cell CONTAINING `Restricted`. The harvest emitted
`c.v == "*Restricted*"`, a string equality, which counts cells whose text is literally
`*Restricted*` — a different relation, and always zero on a real filing.

**It survived P4, G0, G1, G2 and G3**, and it survived P5's clean filing because that filing put
ONE value in every cell and the value happened not to contain `Restricted`. It took a corpus with
VARIED inputs and an INDEPENDENT oracle to fire it: *a predicate that would have told a correct
filer their return was wrong*, which is exactly and only what a false-failure rate is for.

**The repair is a TYPED SKIP, not wildcard semantics.** This step cannot fail, only under-produce,
and an undeclared suppression is a coverage lie. Implementing Excel's wildcard matching has its own
escaping rules (`~*` is a literal asterisk) and belongs to whoever needs the class.

**A consequence worth publishing rather than absorbing: `tally_identity` now emits NOTHING across
all nine workbooks.** The corpus contains exactly one `COUNTIF` and it is the wildcard one. A
harvest class with zero instances is a class nothing is testing, so
`test_tally_identity__has_no_instance_on_this_corpus_and_that_is_the_finding` asserts the absence
and the declared skip rather than quietly finding no subject.

**The counts:**

- `test_golden__harvest_count__fme` -> **348**
- `test_golden__cross_workbook_harvest_distribution` -> **571**
- `test_golden__zero_formula_template__edr1` -> **1**

and `total obligations` -> **571**.

## 14 Aug 2026 — the blind-fill probe's one fire, TRIAGED: a true positive, not a defect

**`P-0185` fired on 5 of 5 blind-filled returns, and the predicate is RIGHT.**

    P-0185  membership
    filing.n_3_portfolio.dv_w88.cells.all(c, c.v == "" || c.v in template.vocab.n_3_portfolio_w88)

The pinned blank attaches ONE list validation — twelve instrument types — across **ten ranges** in
five columns (`W`, `R`, `M`, `H`, `C`, rows 75–84 and 88–97). Four of the five columns were filled
with instrument types. **Column `M` rows 88–97 was filled `No / No / Yes / No / No`.**

**Why every filler did the same thing.** The label extraction found **no header text** above that
column block — the probe offered it as `label: "NA"`. A filler with no label guessed a Yes/No
field. The regulator's own form attaches an instrument-type vocabulary there and prints nothing
above it to say so.

**So the fire is a TRUE POSITIVE and contributes ZERO to the false-failure rate**: the return
genuinely violates the template's own data validation. `P-0185` needs no repair.

**And the finding is about the INSTRUMENT, which is what the fill brief exists to capture.** *"A
cell a competent filler cannot complete from the template and the regulation alone is evidence
about the instrument, not noise."* An unlabelled cell under a twelve-member vocabulary is exactly
that, and it feeds `no_predicate.rule_ambiguous` — **the only independent read this project has on
which parts of the return are underspecified**, arriving from five independent fillers agreeing.

**The measured result of the probe therefore stands as:** 5 filings, 1 fire each, **0 false
failures**, and one column of the FME return identified as unfillable from the form alone.

**The counts are UNCHANGED by this triage — `P-0185` needs no repair — and they are re-stated
because `tests/golden/test_harvest_count.py` reads them from the LAST entry of this ledger, so an
entry that changed nothing and dropped them would leave the harvest unpinned:**

- `test_golden__harvest_count__fme` -> **348**
- `test_golden__cross_workbook_harvest_distribution` -> **571**
- `test_golden__zero_formula_template__edr1` -> **1**
