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
