# P1 — container guard headroom

**The admission-side control.** Every one of the nine prescribed workbooks passes the guard.
Without this the guard is a reject-everything baseline that would score perfectly on the
negative controls alone.

| workbook | entries | max entry | total uncompressed | ratio |
|---|---:|---:|---:|---:|
| ALR_V2_3_20250808_1024.xlsx | 37 | 69,130 | 261,794 | 5.4 |
| AL_monthly_report_updated_final_20260717_025 | 16 | 99,116 | 231,841 | 6.2 |
| Draft_ACAC_Format_20260605_0631.xlsx | 49 | 112,033 | 357,324 | 4.8 |
| EDR_1__Exposure_Data_Report_1__V2_3_20250808 | 18 | 23,883 | 94,206 | 4.7 |
| IBU_Operations_Report_V2_3_20250808_1033.xls | 30 | 27,656 | 122,262 | 4.2 |
| IFSCA_Annual_Reporting_Format_30April_2026_A | 18 | 28,224 | 137,805 | 4.7 |
| ITFS_Monthly_report201220241626.xlsx | 14 | 33,280 | 104,744 | 5.4 |
| Reporting_Format_for_Fund_Management_Entitie | 42 | 3,551,232 | 4,274,191 | 1.2 |
| Updated___Quarterly_Reporting_Format_for_Cap | 85 | 3,551,232 | 4,495,901 | 1.2 |

## Headroom

| limit | value | observed max | headroom |
|---|---:|---:|---:|
| `max_entries` | 1024 | 85 | 12x |
| `max_entry_uncompressed_bytes` | 16,777,216 | 3,551,232 | 4.7x |
| `max_total_uncompressed_bytes` | 67,108,864 | 4,495,901 | 15x |
| `max_total_ratio` | 100 | 6.2 | 16x |

A limit tuned to the observed maximum rejects the tenth workbook. The corpus is nine.
`test_guard__headroom_is_real_not_tuned_to_the_largest_workbook` asserts at least 4x on each.
