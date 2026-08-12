# P4-B2/B4 — `schema_keys` both ways

**This is the phase's headline number.** The settled fraction is *derivable* rather than
*estimated* only because the key set a predicate reads can be determined statically. That
claim becomes true — or measurably false — the day `schema_keys` is machine-checked
against the CEL AST **in both directions** and the shortfall is counted.

## **572 of 572** candidates agree in both directions

| workbook | sha8 | agree | candidates | shortfalls |
|---|---|---:|---:|---:|
| `ALR_V2_3_20250808_1024.xlsx` | `a414d8d3` | 32 | 32 | 0 |
| `AL_monthly_report_updated_final_20260717_0257.xlsx` | `79e43a7f` | 16 | 16 | 0 |
| `Draft_ACAC_Format_20260605_0631.xlsx` | `74ba7b89` | 0 | 0 | 0 |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx` | `230a6f0c` | 1 | 1 | 0 |
| `IBU_Operations_Report_V2_3_20250808_1033.xlsx` | `bf6bbf6b` | 10 | 10 | 0 |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx` | `4b2d4a2b` | 0 | 0 | 0 |
| `ITFS_Monthly_report201220241626.xlsx` | `446b811a` | 25 | 25 | 0 |
| `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` | `7d9a1960` | 349 | 349 | 0 |
| `Updated___Quarterly_Reporting_Format_for_Capital_Market_Intermediaries_20260409_1019.xlsx` | `82dd291f` | 139 | 139 | 0 |
| **total** | — | **572** | **572** | 0 |

## The two directions, and why they are different exception types

- **read but not declared** (`UndeclaredKeyRead`) — the pre-flight set is too small, and
  P5 rule 2 is guarding the wrong keys. A predicate can return `PASS` over a key nobody
  checked was present.
- **declared but not read** (`DeclaredKeyUnread`) — the declared footprint overstates what
  the predicate settles, which inflates the settled **numerator**.

One is a hole in the guard; the other is a lie in the headline number. A single
`KeysMismatch` type would fail NC-Q04, because a repair applied to the wrong side of a
collapsed message is a repair that fixes nothing.

## Shortfalls

None. **What that means and what it does not:** the declared key set equals the
AST-read key set for every candidate. It says nothing about whether a predicate
encodes its clause — that is NC-N01, where a negative control is impossible, and a
predicate can clear all five gates and enforce a rule that does not exist.
