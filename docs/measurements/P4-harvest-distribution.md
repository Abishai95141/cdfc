# P4-B4 — the harvest distribution, across all nine prescribed workbooks

**Warrant: MEASURED.** Produced by `cdfc harvest --all`; re-render with `make harvest`.
These are properties of *our code* and they will move — the first thing P7's G3 does is
reject predicates, and this number will fall, which is correct behaviour. Moving one
without an entry in `docs/HARVEST-DELTA.md` fails the build.

## Every row, including the two zeroes

**Publishing the total alone is banned.** The distribution is concentrated — see the
concentration line below — and `571` on its own conceals which workbooks produced it.

| workbook | sha8 | candidates | conditional_required | cross_sheet_equality | date_bound | integer_bound | membership | numeric_bound | same_sheet_equality | sum_identity | skipped | cells reachable |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ALR_V2_3_20250808_1024.xlsx` | `a414d8d3` | **32** | 0 | 8 | 0 | 1 | 1 | 5 | 9 | 8 | 2 | 1492 |
| `AL_monthly_report_updated_final_20260717_0257.xlsx` | `79e43a7f` | **16** | 1 | 0 | 0 | 0 | 9 | 0 | 0 | 6 | 0 | 1661 |
| `Draft_ACAC_Format_20260605_0631.xlsx` | `74ba7b89` | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx` | `230a6f0c` | **1** | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `IBU_Operations_Report_V2_3_20250808_1033.xlsx` | `bf6bbf6b` | **10** | 0 | 6 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 18 |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx` | `4b2d4a2b` | **0** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `ITFS_Monthly_report201220241626.xlsx` | `446b811a` | **25** | 1 | 1 | 0 | 1 | 8 | 1 | 0 | 13 | 2 | 88 |
| `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` | `7d9a1960` | **348** | 0 | 181 | 5 | 11 | 20 | 10 | 42 | 79 | 181 | 2794 |
| `Updated___Quarterly_Reporting_Format_for_Capital_Market_Intermediaries_20260409_1019.xlsx` | `82dd291f` | **139** | 10 | 0 | 17 | 32 | 47 | 10 | 0 | 23 | 117 | 1040 |
| **total** | — | **571** | 12 | 196 | 22 | 45 | 90 | 26 | 51 | 129 | 302 | 7094 |

**Concentration: 487 of 571 come from two workbooks.** That is why the total
is never published without this table.

**Non-empty on 7 of 9.** G-TRANSFER (mech)'s pre-registered threshold
is >= 5 of 9, so it is met. This is the mechanical arm only: it states
nothing about per-predicate human cost, which is P15's arm and is not touched here.

## The weak pile, typed and counted

An undeclared suppression is a coverage lie. Every construct the class set cannot express
is a typed `SkipRecord` naming the sheet, the cell and the reason.

| workbook | `dv_no_type` | `function_outside_vocabulary` | `key_unresolved` | `list_unresolved` | total |
|---|---:|---:|---:|---:|---:|
| `ALR_V2_3_20250808_1024.xlsx` | 0 | 0 | 2 | 0 | 2 |
| `AL_monthly_report_updated_final_20260717_0257.xlsx` | 0 | 0 | 0 | 0 | 0 |
| `Draft_ACAC_Format_20260605_0631.xlsx` | 0 | 0 | 0 | 0 | 0 |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx` | 0 | 0 | 0 | 0 | 0 |
| `IBU_Operations_Report_V2_3_20250808_1033.xlsx` | 0 | 0 | 0 | 0 | 0 |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx` | 0 | 0 | 0 | 0 | 0 |
| `ITFS_Monthly_report201220241626.xlsx` | 1 | 0 | 1 | 0 | 2 |
| `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` | 2 | 59 | 118 | 2 | 181 |
| `Updated___Quarterly_Reporting_Format_for_Capital_Market_Intermediaries_20260409_1019.xlsx` | 18 | 0 | 99 | 0 | 117 |

**The FME reconciliation, in one sentence.** The 2 `list_unresolved` skips on
`7d9a1960` are exactly the pinned `22 list-type validations - 20 resolving` gap: both
are `IF(C5="No",Choicelist,YesNolist)`, a vocabulary that depends on a value the
FILING supplies. Resolving it from the filing would be NC-D01c; it is skipped instead.

## `static_settled_cells`, computed — and reconciled against the spec's figure

| number | value | warrant |
|---|---:|---|
| `len(cells_reachable)` for `7d9a1960`, computed here | **2794** | MEASURED |
| the specification's figure | 2373 | DERIVED-FROM-SPEC |
| delta | **+421** | — |

**The delta is a finding. It is published and it is not reconciled by adjusting the
harvest.** The computed figure is the union of cells bound by the 348 candidates
this build emits; the spec attributed 2,329 of 2,373 settled cells to 53 validation
predicates, and this harvest emits a different number of validation predicates from a
different class set. Either 2,373 was computed from an enumeration this build does not
produce, or the 53 is wrong. `docs/HARVEST-DELTA.md` entry #1 carries it.

**`2,373` may not be pinned as a literal in any golden test at this phase.** It
resolves to no ledger row and to no measurement this code produces.

## The obligation coverage pair — two numbers, never one

| published number | value | what it means |
|---|---:|---|
| `predicates_with_a_STATUTE_obligation / 571` | **0 / 571** | *No harvested predicate yet implements a statutory clause.* |
| `predicates_with_a_TEMPLATE_obligation / 571` | **571 / 571** | Every harvested predicate implements a relation the regulator's own pinned blank encodes. |

**The two counts are never added together, and publishing either alone fails the exit
gate.** The first alone conceals that these predicates are grounded in a real regulator
artifact; the second alone conceals that not one of them is grounded in the statute.

`clause_absent_reason` distribution:

| reason | count |
|---|---:|
| `derived_from_data_validation` | 195 |
| `derived_from_template_formula` | 376 |

## `fault_classes_claimed_by_no_harvested_candidate`

**{F10, F11, F14}** — 3 of 14 classes in the pinned fault model
are claimed by no harvested class. *A fault class nobody claims is the most useful thing on
this page.*

| class | why it is unclaimed |
|---|---|
| **F10** | legal enum substitution. A membership test cannot see one legal vocabulary term substituted for another BY CONSTRUCTION — the value is in the vocabulary. A designed miss, and P10's residue feedstock. |
| **F11** | formula override. Claimed by TEMPLATE_DIFF, which is a RELATION and is built at P9-B1, not by any harvested class. No relation the template encodes can detect the deletion of the formula that encodes it. |
| **F14** | vocabulary-gap exploitation — a value legal under the template's own defective logic but outside the regulation. MEASURED: the FME template computes a scheme total with three COUNTIFs that between them miss two of its nine legal Type-of-Scheme values. No relation derived from that template can see a filing exploiting it. |

## What each harvest class claims, and why

Declared per class as a module-level constant, so a claim cannot be tuned per predicate
after a campaign without changing `code_sha256`. Committed in P4, four phases before the
first campaign runs.

| harvest class | `claims_fault_classes` |
|---|---|
| `conditional_required` | F05 |
| `cross_sheet_equality` | F01 F02 F03 F04 F05 F13 |
| `date_bound` | F09 |
| `integer_bound` | F01 F03 F06 |
| `membership` | F12 |
| `numeric_bound` | F01 F03 |
| `same_sheet_equality` | F01 F02 F03 F04 F05 |
| `sum_identity` | F01 F02 F03 F04 F05 F07 F08 |
| `tally_identity` | F05 F07 F08 |

## What this measurement does not license

That any of these predicates means what a regulation means. Not one cites a clause — that
is the whole point of the pair above. **NC-N01** is the control that cannot be built: a
predicate can clear all five gates and enforce a rule that does not exist.
