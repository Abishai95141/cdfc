# L05 — Spreadsheet error empirics, oracle-free detection, public corpora, and the L1 toolchain

**Lane run 10 Aug 2026.** Two questions: (i) what is actually *measured* about spreadsheet errors, and
(ii) what finds spreadsheet errors **without an oracle** — the exact problem the brief claims is open.
Plus a full, executed verification of the L1 extraction toolchain against the real IFSCA artifact.

**Warrant key used throughout:**
- **VERIFIED-AT-SOURCE** — I opened the primary artifact myself: I ran the code and read the output, or
  I converted the paper PDF with `pdftotext -layout` and read the raw text.
- **SECONDARY** — a credible source (or a `WebFetch` summariser reading the primary page) describes it;
  a model stood between me and the page.
- **UNVERIFIED / NOT-FOUND** — could not confirm. Stated as such, never smoothed over.

---

## 0. EXECUTIVE SUMMARY — the six things that matter

1. **§4.3 reproduces exactly — every single number — and the reproduction found a third silent false
   negative of the same shape as §4.4's two.** The operator's 294 formulas, 181 cross-sheet carries,
   35 SUM, 3 COUNTIF, 50 IFERROR, 14 IF, 11 other, 195 cross-sheet, 6,757 cells, 9/10 protected, and
   the entire seven-workbook cross-format table all reproduce to the digit from an independent
   `zipfile + lxml` pass. **Two counts are undercounts, both in the same direction:** there are
   **505 formula-bearing cells, not 294** (211 shared-formula continuation cells carry no text), and
   **54 data validations of which 22 are list-type, not 35 of which 3 are list-type** (19 live in the
   `x14` extension namespace, invisible to a main-namespace parser *and* to openpyxl).
2. **openpyxl silently drops those 19 validations** with only a `UserWarning`, and its round-trip
   destroys the file: **3,663,391 → 65,877 bytes**, 24 parts deleted, including a **3.55 MB Power Pivot
   data model that is 96.9% of the workbook** and **26 Power Query connections**. If L0/L1 is
   "openpyxl + save", the system silently loses 97% of the artifact and 86% of its list vocabularies.
3. **There is a one-line deterministic fix.** `soffice --headless --convert-to xlsx` normalises the
   workbook: it expands shared formulas (294 → 505 text-bearing) **and migrates all 19 `x14`
   validations into the main namespace** (3 → 22 list-type). Verified by execution. This belongs in L0
   as a mandatory pre-parse normalisation step.
4. **The whole deterministic spine — L0 → L1 → L4 → L5 — runs today, end-to-end, on the real IFSCA
   workbook, with zero model involvement.** I seeded a mutant by raw-zip surgery (42/42 parts
   preserved byte-for-byte except the one edited sheet; the 3.55 MB model, the `x14` validations and
   the SHA-512 sheet protection all intact), recalculated both instances with the `formulas` engine,
   and ran a predicate transcribed from the template's own native formula. Clean → PASS (D17 = 9.0);
   mutant → FAIL (D17 = 5.0). **Mutation score 1/1, false-failure contribution 0/1.** L4 is not a
   research risk; it is an afternoon.
5. **Oracle-free spreadsheet error detection has ~25 years of measured results, and the numbers are
   sobering.** The best published no-oracle detector (ExceLint, OOPSLA 2018) reports **mean precision
   64.1% / mean recall 62.1% over 70 benchmarks**; the prior state of the art (CUSTODES) reports
   **mean precision 20.3%, median precision 0.0%**. ExceLint already implements *exactly* the brief's
   L4 test-2: a **hypergeometric random-flagger baseline** and an explicit "high precision when doing
   nothing" analysis. This is direct, citable prior art for the qualification gate that the brief
   currently presents as novel.
6. **The public corpora do not solve §9.2, and I can say precisely why.** ENRON (15,770 sheets,
   CC BY 4.0), FUSE (249,376, unencumbered), EUSES (~4,498), VEnron2 (12,254) are all real and all
   downloadable — but **none carries per-cell correctness labels**. The only hand-built real-error
   ground truth in the literature is measured in *dozens*: 397 formula errors over 70 spreadsheets
   (ExceLint, 34 person-hours) and 28 quantitative errors from ~200 Enron files (Schmitz & Jannach).
   **A generic-business corpus is useless for the FME false-failure rate and genuinely useful for
   testing L1 robustness.** Section 5.5 says exactly which.

---

## 1. THE OPERATOR'S §4.3 COUNT — INDEPENDENT REPRODUCTION

**Method.** `zipfile` + `lxml` over the raw OOXML, no openpyxl, no regex over serialised XML.
Script: `/private/tmp/.../scratchpad/extract_raw.py`, `extract_ext.py`. Environment:
`/Users/abishaikc/Gift/.venv/bin/python` — Python 3.12.12, openpyxl 3.1.5, lxml 6.1.1.
Target: `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`
(3,663,391 bytes).

The extraction walks `xl/workbook.xml` → `xl/_rels/workbook.xml.rels` → each `xl/worksheets/sheetN.xml`,
counting `<c>` elements, `<f>` elements (both text-bearing and empty shared children), `<mergeCell>`,
`<dataValidation>` in **both** the main namespace `.../spreadsheetml/2006/main` and the extension
namespace `http://schemas.microsoft.com/office/spreadsheetml/2009/9/main`, plus `<sheetProtection>`,
`<definedName>` and `<workbookProtection>`.

### 1.1 Agreement table — VERIFIED-AT-SOURCE (I ran it)

| §4.3 claim | My independent count | Verdict |
|---|---|---|
| 10 sheets | 10 (9 visible + `Dropdown` hidden) | **CONFIRMED** |
| 6,757 cells | 6,757 `<c>` elements | **CONFIRMED — exact** |
| 294 formulas | 294 `<f>` elements carrying text | **CONFIRMED — exact, but see §1.2** |
| 181 pure cross-sheet carry (62%) | 181 | **CONFIRMED — exact** |
| 50 IFERROR wrapper (17%) | 50 | **CONFIRMED — exact** |
| 35 SUM row/column total (12%) | 35 | **CONFIRMED — exact** |
| 14 IF conditional carry (5%) | 14 | **CONFIRMED — exact** |
| 3 COUNTIF scheme-type tally (1%) | 3 | **CONFIRMED — exact** |
| 11 other/ref (4%) | 192 pure references − 181 cross-sheet = 11 | **CONFIRMED — exact** |
| 195 cross-sheet (66%) | 195 of 294 text-bearing = 66.3% | **CONFIRMED — exact** |
| 9 of 10 sheets protected | 9 (`Dropdown` alone unprotected — and hidden) | **CONFIRMED** |
| 494 distinct strings | `sharedStrings.xml` `uniqueCount="494"` | **CONFIRMED — exact** |
| 854 label instances | `count="1249"` total `<si>` references | **NOT REPRODUCED** — 854 presumably counts label cells after filtering numerics; the raw total is 1,249. Not a disagreement, an undeclared filter. |
| 35 data validations | 35 in the **main namespace** | **QUALIFIED — 54 exist** (§1.3) |
| only 3 list-type | 3 in the **main namespace** | **QUALIFIED — 22 exist** (§1.3) |

### 1.2 Disagreement 1 — 294 formulas is 505 formula-bearing cells

```
<f> elements total          : 505
<f> WITH text               : 294     <- the operator's number
<f> EMPTY (shared children) : 211
shared-formula MASTERS      : 32
t='array' formulas          : 1
```

OOXML stores a copied formula once. The master cell carries
`<f t="shared" si="3" ref="E76:E84">IFERROR(D76/$O$3,0)</f>`; the eight continuation cells carry
`<f t="shared" si="3"/>` — a formula element with **no text**. A pass that counts text-bearing `<f>`
elements sees 294. A pass that counts *cells that compute something* sees **505**.

Both counts are defensible; only one is the right denominator for a coverage claim. **If L5 reports
"N field × predicate pairs in scope", and N is derived from 294, the system under-reports its own
scope by 41.8% (211/505) and the coverage fraction printed on Screen 2 is wrong.** openpyxl expands
shared formulas correctly and returns 505 — verified: `'1. Introduction'!E76 == '=F55'`,
`'3. Portfolio'!E84 == '=IFERROR(D84/$O$3,0)'`.

Note also: `xl/calcChain.xml` contains **506** entries against 505 `<f>` elements. One-cell
discrepancy, unexplained; flagged, not resolved.

### 1.3 Disagreement 2 — the `x14` blind spot, and it is the load-bearing one

The claim in §4.3 that carries the most argumentative weight is *"35 data validations (only **3**
list-type with a named vocabulary)"* — it is what makes the template look like it barely constrains
anything. **It is wrong, and the mechanism is exactly §4.4's.**

Excel writes a list validation into the main namespace only when its source range is on the *same*
sheet. A list whose vocabulary lives on another sheet is written to
`<extLst><ext><x14:dataValidations>` instead. A main-namespace parser cannot see them. Neither can
openpyxl — which emits a warning and discards them:

```
openpyxl/worksheet/_reader.py:329: UserWarning: Data Validation extension is not supported
and will be removed
```

All 19 hidden validations, VERIFIED-AT-SOURCE (`extract_ext.py`), every one `type="list"`:

| sheet | sqref | vocabulary |
|---|---|---|
| 1. Introduction | D2 | `Dropdown!$D$3:$D$6` |
| 1. Introduction | D10 | `Dropdown!$J$3:$J$5` |
| 1. Introduction | D12 | `Dropdown!$G$3:$G$7` |
| 1. Introduction | D21:D22, L54:L63 | `Dropdown!$H$3:$H$5` |
| 1. Introduction | D39, J54:K63, M54:M63 | `Dropdown!$H$3:$H$4` |
| 1. Introduction | D3 | `Dropdown!$E$3:$E$6` |
| 1. Introduction | F54:F63 | `Dropdown!$K$3:$K$5` |
| 1. Introduction | G54:G63 | `Dropdown!$F$3:$F$11` |
| 1. Introduction | H54:H63 | `Dropdown!$I$3:$I$4` |
| 3. Portfolio | 24 ranges (I116:I126 … M98) | `Dropdown!$H$3:$H$4` |
| 3. Portfolio | 10 ranges (W88:W97 … C75:C84) | `Dropdown!$M$3:$M$14` |
| 6. Complaints | C6 | `Dropdown!$H$3:$H$4` |
| 7. AML-CFT | C13 | `Dropdown!$N$3:$N$5` |
| 7. AML-CFT | C16, C18 | `Dropdown!$H$3:$H$4` |
| 7. AML-CFT | C20 | `Dropdown!$O$3:$O$4` |
| 7. AML-CFT | C22 | `Dropdown!$P$3:$P$4` |
| 7. AML-CFT | C32 | `Dropdown!$Q$3:$Q$6` |
| 8. Compliance Status | C12 | `Dropdown!$H$3:$H$5` |
| 8. Compliance Status | C4:C9 | `Dropdown!$H$3:$H$4` |

**Corrected totals: 54 data validations, 22 list-type with a named vocabulary.** The operator's
instrument saw 35/3 — a **35% undercount on validations and an 86% undercount on the enumerated
vocabularies**, which are the single most directly checkable predicate class in the whole workbook
("dropdown ∈ vocabulary" is item 13 of the 17 decidable).

The direction matters: **the template constrains substantially more than the brief says.** The
argument "the workbook moves numbers between sheets and that motion is counted as validation"
survives on the formula analysis (still 38 of 294 checkable), but the "only 3 named vocabularies"
half of it does not.

### 1.4 What neither pass saw at all: the workbook is 97% Power Pivot

`xl/model/item.data` is **3,551,232 bytes of the 3,663,391-byte file (96.9%)** — a Power Pivot data
model. `xl/connections.xml` declares **27 connections**: 26 Power Query connections named
`Query - Page001` … `Query - Page026`, plus `ThisWorkbookDataModel` (`type="5"`, `command="Model"`).
Four hidden defined names `ExternalData_1/2/3/17` resolve to `#REF!` — the residue of query output
ranges that were deleted.

VERIFIED-AT-SOURCE. Implication for L0: **the artifact under test has a machine-readable provenance
surface that the current design does not model at all**, and any content-addressed hash of "the
template" is dominated by a binary blob nobody has parsed.

### 1.5 Cross-workbook — the whole §4.3 table reproduces, and generalises

Independent pass over all nine prescribed workbooks in `scratchpad-oracle/`. VERIFIED-AT-SOURCE.

| workbook | sheets | cells | `<f>` cells | `<f>` w/ text | cross-sheet | dv main | dv list | **dv x14** | protected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALR_V2_3 | 9 | 2,889 | 645 | **246** | **35** | 7 | 1 | 0 | 9 |
| AL_monthly_report | 4 | 4,215 | 161 | **49** | **6** | 1 | 0 | **9** | 3 |
| Draft_ACAC_Format | 13 | 3,793 | 112 | **9** | **0** | 0 | 0 | 0 | 0 |
| EDR_1_Exposure_Data | 3 | 397 | 0 | 0 | 0 | 1 | 1 | 0 | 3 |
| IBU_Operations_Report | 8 | **961** | 7 | **7** | 7 | 4 | 4 | 0 | 8 |
| IFSCA_Annual_Reporting | 9 | 1,708 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| ITFS_Monthly_report | 2 | 732 | 32 | **32** | **11** | 7 | 0 | **9** | 1 |
| **FME Reporting Format** | 10 | **6,757** | **505** | **294** | **195** | 35 | 3 | **19** | 9 |
| CMI Quarterly (Updated) | 18 | 7,810 | 33 | **33** | **8** | 142 | 52 | 0 | 17 |
| **TOTAL** | **76** | **29,262** | **1,495** | **670** | **262** | **197** | **61** | **37** | **50** |

Every bolded figure in the "`<f>` w/ text" and "cross-sheet" columns matches §4.3's cross-workbook
line exactly: *FME 294/195; ALR 246/35; AL monthly 49/6; CMI quarterly 33/8; ITFS 32/11; Draft ACAC
9/0; IBU 7 formulas across 961 cells.* **Seven of seven, to the digit.** That is a strong positive
control on the operator's method.

Two things generalise:
- **The formula-cell undercount is systemic:** 670 counted against **1,495 formula-bearing cells** across the corpus — the counted set is **45%** of the real one.
- **The `x14` blind spot is not a one-off:** **37 hidden validations in 3 of 9 workbooks.**
- One more, worth a note: **the CMI quarterly workbook has 142 main-namespace validations, 52 of them list-type** — an order of magnitude more constrained than the FME workbook. The FME workbook is not representative of IFSCA templates in general.

---

## 2. THE L1 TOOLING MATRIX — every claim executed, not read

All timings on this machine, single run, VERIFIED-AT-SOURCE.
Script: `/private/tmp/.../scratchpad/tool_matrix.py`, `tool_matrix2.py`.

| capability | **openpyxl 3.1.5** | **python-calamine 0.8.2** | **xlsx2csv 0.8.6** | **raw zipfile+lxml** | **formulas 1.3.4** | **pycel 1.0b30** | **LibreOffice (soffice)** |
|---|---|---|---|---|---|---|---|
| licence | MIT | MIT | MIT | stdlib / BSD | **EUPL 1.1+** ⚠ | **GPL-3.0** ⚠ | MPL-2.0 |
| load time | 0.18 s | **0.002 s** | 0.024 s | ~0.1 s | 2.33 s | 0.41 s | 3.9 s |
| sheet list | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| hidden-sheet state | ✅ `sheet_state` | ✅ `SheetVisibleEnum` | ❌ | ✅ `state="hidden"` | — | — | ✅ |
| **formulas** | ✅ **505**, shared expanded | ❌ **values only** | ❌ values only | ✅ 505 raw / 294 text | ✅ parsed to AST | ✅ | ✅ (rewrites) |
| array formula | ⚠ opaque `ArrayFormula` object | ❌ | ❌ | ✅ `t="array"` | ✅ | ✅ | ✅ |
| **sheet protection** | ✅ full (`algorithmName`, `hashValue`, `saltValue`, `spinCount`) | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ preserved |
| workbook protection | ✅ `wb.security` | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| merged ranges | ✅ 252 | ✅ `merged_cell_ranges` | ❌ | ✅ 252 | ❌ | ❌ | ✅ 252 |
| dataValidation (main) | ✅ 35 | ❌ | ❌ | ✅ 35 | ❌ | ❌ | ✅ |
| **dataValidation (x14)** | ❌ **DROPPED, warning only** | ❌ | ❌ | ✅ **19** | ❌ | ❌ | ✅ **migrated to main ns** |
| defined names | ✅ 4 global + 4 sheet-local | ❌ | ❌ | ✅ 12 | ✅ | ✅ | ✅ 12 |
| cached values | ✅ `data_only=True` | ✅ | ✅ | ✅ `<v>` | ✅ | ✅ | ✅ |
| **recalculation** | ❌ **no engine** | ❌ | ❌ | ❌ | ✅ **works** | ✅ works | ✅ works |
| **whole-workbook dep. graph** | ❌ | ❌ | ❌ | build it yourself | ✅ **4,627 nodes / 3,185 edges in 2.33 s** | ⚠ **lazy — 33 nodes after 3 evals** | ❌ |
| write / mutate | ✅ (destructive, §2.2) | ❌ read-only | ❌ | ✅ **surgical, §3** | ✅ writes results | ❌ | ✅ (lossy, §2.3) |

### 2.1 openpyxl — reads almost everything, and lies about one thing

Answers to the lane's explicit questions, all executed:

- **Does it read formulas from a PROTECTED workbook?** **Yes.** Sheet protection in xlsx is advisory —
  a SHA-512 hash that the Excel *UI* honours. It is not encryption. openpyxl reads all 505 formulas
  from nine protected sheets without a password, and reports the protection metadata faithfully:
  `{'algorithmName': 'SHA-512', 'spinCount': 100000, 'sheet': '1', 'objects': '1', 'scenarios': '1'}`.
- **Merged cells?** **Yes** — 252 ranges, agrees exactly with the raw pass.
- **dataValidation?** **Partially, and this is the failure.** 35 of 54; 3 of 22 list-type. The 19
  `x14` validations are discarded with a `UserWarning`, which in a batch pipeline is invisible.
- **Defined names?** **Yes, and correctly split**: 4 workbook-level (`Choicelist`, `NA`, `YesNolist`,
  `YesNoNA`) and 4 sheet-local (`ExternalData_1/2/3/17`). Note `openpyxl` exposes the 4 `_xlnm.Print_Area`
  entries separately, so `len(wb.defined_names) == 4` where the raw XML has 12 `<definedName>` elements
  — a second, smaller denominator trap.
- **`data_only=True`?** Works; returns the cached values. In the blank template every cached formula
  value is `0` — which is why the mutation demo in §3 has to *fill* the template first.
- **Can it write into a protected sheet?** **Yes.** `wb["3. Portfolio"]["C17"] = 123456789` saves and
  reads back, with `protection.sheet == True` preserved. Mutation testing is mechanically possible.

### 2.2 openpyxl round-trip is destructive — measured

`load_workbook(PATH)` → `save()`, nothing edited:

```
original 3,663,391 bytes  ->  round-trip 65,877 bytes   (98.2% of the file gone)
parts: 42 -> 18
```

Dropped, verified by zip-entry diff:
`xl/model/item.data` (the 3.55 MB Power Pivot model) · `xl/connections.xml` (all 26 Power Query
connections + the data-model connection) · `xl/calcChain.xml` · `xl/metadata.xml` ·
`xl/sharedStrings.xml` (rewritten inline) · 8 × `printerSettings*.bin` · 8 × `worksheets/_rels/*` ·
3 × `customXml/*` · **and every `x14` dataValidation** (post-round-trip audit: `dvX14 = 0`,
`dvMain = 35`, `dvList = 3`).

**Consequence for L7.** If the pipeline ever re-serialises the artifact with openpyxl, the content
hash it attests over is a hash of something that is not the filing. The attestation must be taken over
the **original bytes**, never over a re-saved copy.

### 2.3 LibreOffice headless is a *normaliser* — the most useful single finding in this section

```
soffice --headless --convert-to xlsx --outdir lo_rt <FME workbook>
```
3.9 s, 211,940 bytes out. Post-conversion audit vs. original:

| | `<f>` cells | `<f>` w/ text | dv main | dv list | **dv x14** | merged | protected sheets | defined names |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **ORIGINAL (IFSCA)** | 505 | **294** | 35 | **3** | **19** | 252 | 9 | 12 |
| **LibreOffice round-trip** | 505 | **505** | **53** | **22** | **0** | 252 | 9 | 12 |
| openpyxl round-trip | 505 | 505 | 35 | **3** | **0** | 252 | 9 | 12 |

LibreOffice does two things no Python reader does: it **expands every shared formula into an explicit
text-bearing `<f>`**, and it **migrates the `x14` extension validations into the main namespace**. A
naïve main-namespace parser run *after* LibreOffice sees 505 formulas and 22 list validations —
i.e. it sees the truth. (One validation is lost in the merge: 35 + 19 = 54 but LO writes 53. Flagged,
unexplained, and it means LO is a normaliser, not a lossless one — it also drops the Power Pivot model
and `calcChain`.)

**Design consequence: L0 should normalise through LibreOffice for *analysis*, and content-address the
*original* for attestation.** Two artifacts, two purposes, both deterministic.

### 2.4 Formula engines

- **`formulas` 1.3.4** (EUPL 1.1+, 499★, release 2026-03-11 — SECONDARY, from the repo page). Loads
  the whole workbook into a dispatcher graph: **4,627 nodes / 3,185 edges in 2.33 s**, `calculate()`
  in 0.23 s producing 3,836 outputs. This is the only tool tested that gives a **whole-workbook
  dependency graph for free**, which is precisely what L1 needs to know which fields feed which
  totals. Self-reported coverage: 483 of 536 Excel functions (90.1%); Lookup 82.5%, Math & Trig 88.8%,
  Text 88%, Information 72.7% (SECONDARY, README). **⚠ EUPL 1.1+ is a copyleft licence** — a
  network-deployed derivative may carry obligations. Legal check required before it goes in the core.
- **`pycel` 1.0b30** (GPL-3.0, 629★ — SECONDARY). Evaluates named cells correctly
  (`'1. Introduction'!D17 → 0`), but its dependency graph is built **lazily from what you evaluate**:
  after three `evaluate()` calls the graph had **33 nodes**, not 4,627. It is a targeted evaluator,
  not a schema extractor. **⚠ GPL-3.0.**
- **`koala2`** — 0.0.36 on PyPI, repo `vallettea/koala`, **not actively maintained**; the community
  successor is `bradbase/xlcalculator`. SECONDARY. Not tested. **Do not adopt.**
- **`python-calamine` 0.8.2** — 500× faster than openpyxl to load and gives sheet visibility and merged
  ranges, but the sheet API is `['end','height','iter_rows','merged_cell_ranges','name','start',
  'to_python','total_height','total_width','width']` — **no formula accessor at all**. Values only.
- **`xlsx2csv` 0.8.6** — cached values, one sheet per call. Useful for a cheap diff, nothing else.

### 2.5 Independent evidence on reader fidelity at scale

`witanlabs/xlsx-corpus-bench` (Apache-2.0, **2★**, last full run 2026-06-12 — SECONDARY, repo page):
~16,000 workbooks / 6.8 M formula cells from FUSE (10,544) + SpreadsheetBench (5,426), scored against
Microsoft Excel as ground truth.

| library | FUSE open | FUSE round-trip | FUSE recalc exact |
|---|---:|---:|---:|
| witan | 100% | 100% | 95.3% |
| LibreOffice | 100% | 94.8% | 91.9% |
| ClosedXML | 99.7% | 98.6% | 82.1% |
| EPPlus | 98.6% | 98.6% | 62.3% |
| **openpyxl** | — | — | **N/A — no calculation engine** |

Two★ and self-published by a vendor whose own product tops the table: **treat the ranking as
promotional and the *shape* as informative.** The informative shape is that even LibreOffice
reproduces Excel's arithmetic exactly on only ~92% of real workbooks. **Any L5 predicate that compares
a recomputed total to a cell's cached value inherits a several-percent engine-disagreement floor, and
that floor must be reported as part of the predicate's FFR, not silently absorbed.**

---

## 3. THE END-TO-END DEMONSTRATION — L0→L1→L4→L5 on the real artifact, no model

This is the part I would put on a slide.

### 3.1 Mutation seeding without destroying the workbook

openpyxl's round-trip is unusable as a mutation substrate (§2.2). The alternative is **raw-zip
surgery**: copy every part byte-for-byte, rewrite exactly one worksheet XML.

```python
zin = zipfile.ZipFile(SRC)
raw = zin.read("xl/worksheets/sheet1.xml").decode("utf-8")
mut = raw.replace("<f>SUM(D18:D20)</f>", "<f>SUM(D18:D19)</f>", 1)   # off-by-one omission mutant
zout = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    zout.writestr(it, mut.encode("utf-8") if it.filename == "xl/worksheets/sheet1.xml"
                                          else zin.read(it.filename))
```

Verified result:
```
orig size 3,663,391  mutant size 3,646,759
ORIG   <f>=505 dvMain=35 dvX14=19 parts=42 model=3551232 bytes
MUTANT <f>=505 dvMain=35 dvX14=19 parts=42 model=3551232 bytes
parts differing from original: ['xl/worksheets/sheet1.xml']
openpyxl reads mutant D17 = =SUM(D18:D19) | protection still on: True
```
**One part changed. Everything else, including the 3.55 MB data model and all 19 hidden validations,
byte-identical.**

### 3.2 The kill

The blank template's cached values are all zero, so a mutant is unobservable until the template is
*filled* — which is itself a measurement of the brief's §9.2 weakness. I built a minimal clean
instance by the same surgery (D18=2, D19=3, D20=4 written as literals, replacing the COUNTIF cells),
then recalculated both with `formulas`:

```
CLEAN : {'D17': 9.0, 'D18': 2.0, 'D19': 3.0, 'D20': 4.0}
MUTANT: {'D17': 5.0, 'D18': 2.0, 'D19': 3.0, 'D20': 4.0}

predicate P: D17 == D18+D19+D20          # transcribed from the template's own =SUM(D18:D20)
  on CLEAN  -> PASS
  on MUTANT -> FAIL
  mutation score for this 1-mutant set: 1/1
```

**Warrant: VERIFIED-AT-SOURCE — I ran it.** This is L1 (the predicate is read off the template's own
formula), L4 test 1 (mutation kill), L4 test 3 (FFR contribution 0/1 on the clean instance) and L5
(PASS / FAIL) executing on the real IFSCA workbook with zero model involvement, in under three
seconds. Denominator discipline: **n = 1 mutant, n = 1 clean instance.** It proves the machinery
runs; it measures nothing about the rate.

---

## 4. THE EMPIRICAL LITERATURE ON SPREADSHEET ERRORS

### 4.1 Panko's numbers, with their denominators

**Primary source A — Panko, "What We Don't Know About Spreadsheet Errors Today", EuSpRIG 2015
Conference "Spreadsheet Risk Management", ISBN 978-1-905404-52-0, arXiv:1602.02601.**
VERIFIED-AT-SOURCE (converted with `pdftotext -layout`, read the raw text).

- **Table 1** (cell error rate from development experiments): *"14 laboratories spreadsheet development
  studies involving 967 individuals working alone on a variety of tasks… The average across these
  studies is a cell error rate of 3.9%."* Comparator rows in the same table: National Software Quality
  Experiment 2.0% per LoC; 2,500 Cisco inspections 3.2%; AT&T 2.5 M LoC over 8 releases 3.7%.
- **Table 2** (operational spreadsheets, intensive inspection): six studies —
  Hicks 1995 (**1** sheet, 100%, CER 1.2%), Coopers & Lybrand 1997 (**23**, 91%, NR),
  KPMG 1998 (**22**, 91%, NR), Lukasic 1998 (**2**, 100%, CER 2.2% / 2.5%),
  Butler 2000 (**7**, 86%, NR), Lawrence & Lee 2001 (**30**, 100%, NR).
  **Total / weighted average: 85 spreadsheets, 94% with errors.**
  Only **three** of the six report a cell error rate at all.
- Detection, same paper: *"nine experiments using over 1,000 participants in total have found average
  error detection rates of 60%."* Software single-inspector detection 20–40%. Anderson 2004: of 14
  seeded errors, three had detection rates **below 10%** and half below 40%.
- Error taxonomy: Panko & Halverson 2001 — 45% logic, 23% mechanical, 31% omission. Panko & Sprague
  1998 — 44% logic, 3% mechanical, **53% omission** (Panko himself calls this *"an anomaly of the task
  statement wording"*).
- Panko cites Hermans & Murphy-Hill for the Enron scale: *"9,120 Enron spreadsheets with formulas…
  20,277,835 cells with formulas."*

**Primary source B — `panko.com/ssr/Audits.html`.** SECONDARY (a WebFetch summariser read the page).
Two *different* tables from the same author: a core table totalling **55 spreadsheets at 91%**, and a
broader table adding Lawrence & Lee 2001, Clermont 2002, and Powell/Baker/Lawson 2008a+b, totalling
**163 spreadsheets at 83%**. Panko's own stated caveats on that page include *"In general, these
studies probably underestimated the number of errors strongly."*

**Primary source C — Powell, Baker & Lawson, "A critical review of the literature on spreadsheet
errors", *Decision Support Systems* 46 (2008) 128–138.** VERIFIED-AT-SOURCE (pdftotext, read raw).
Their Table 2, captioned *"Spreadsheet error rates (after Panko [25])"*, reproduces seven sources with
footnotes: **"Weighted average of 88 spreadsheets in sources 1–7"** → 94% with errors; **"Weighted
average of 43 spreadsheets in sources 3–7"** → cell error rate 5.2%.

### 4.2 The "88% of spreadsheets have errors" folklore — resolved, and it is worse than a rounding error

**NOT-FOUND: I could not locate any primary source stating "88% of spreadsheets contain errors."**
`panko.com/ssr/whatknow.htm` returned **HTTP 404** and `panko.shidler.hawaii.edu` no longer resolves
(`ENOTFOUND`), so the canonical page is not currently reachable. A search snippet attributed to a
later Panko revision the phrasing *"88% of the 113 spreadsheets audited in 7 field audit studies"* —
**UNVERIFIED; I could not open that page.**

What I *can* state at source: **the same author's headline appears with four different denominators
across four Panko-derived documents.**

| source | spreadsheets (n) | % with errors | CER | CER denominator |
|---|---:|---:|---:|---:|
| Powell et al. 2008, Table 2 "after Panko" | **88** | 94% | 5.2% | **43** |
| Panko, EuSpRIG 2015, Table 2 | **85** | 94% | — | 3 studies report one |
| panko.com/ssr/Audits.html, core table | **55** | 91% | — | — |
| panko.com/ssr/Audits.html, broad table | **163** | 83% | — | — |
| unreachable later revision (reported) | 113 | 88% | — | — |

**The most defensible reading is that the folklore "88%" is the sample size 88 read as a percentage**,
reinforced by a later revision that genuinely reports 88% of a *different* n. Either way: **never
quote 88% without a denominator, because there isn't one denominator.**

### 4.3 The criticisms — quoted, because they are the whole point

Powell, Baker & Lawson dismantle the estimate they reproduce. VERIFIED-AT-SOURCE, quoted from the
converted PDF:

> "There are several reasons to question the reliability of these estimates. First, three of the seven
> sources are unpublished. Second, the majority of the sources gave little or no information on their
> definition of errors or on the methods used to find errors. Third, Lawrence and Lee [19], whose
> observations account for 70% of the sample used to estimate the cell error rate, did not actually
> report a cell error rate of 6.9% on completed spreadsheets. Rather, they reported that auditors had
> 'issues' on the initial review of a model that they subsequently discussed with the developers
> concerning 6.9% of the cells."

And the model that produced the 6.9% *"was revised an average of six times before the model was
complete."* Their conclusion:

> "To be clear, we do not mean to suggest that the 'true' error rates in operational spreadsheets are
> negligible. Our own studies suggest the opposite. However, the evidence behind the estimates in the
> literature does not provide sufficient grounds for a reliable, quantitative estimate."

They name three missing standards: **the definition of errors · the methods used to detect errors ·
the sample of spreadsheets studied.** And: *"the characteristics of the spreadsheets used in the
experimental sample have rarely been reported, so we cannot know whether the results apply to any
particular area of interest."*

Their own measurement (Powell, Lawson & Baker, "Impact of Errors in Operational Spreadsheets",
arXiv:0801.0715, VERIFIED-AT-SOURCE): *"In a previous study of 50 operational spreadsheets we found
errors in **0.8% to 1.8% of all formula cells, depending on how errors are defined.**"* The follow-up
study covers **25 operational spreadsheets from five organisations**, and finds *"that many errors
have no quantitative impact on the spreadsheet."*

**This is the single most transferable methodological lesson in the lane, and it is the brief's own
argument arriving from an unrelated field twenty years early:** an error rate is not a number, it is a
number *plus* a definition of error, a detection method, and a described sample. **A system that
reports a per-predicate FFR without those three is reproducing exactly the defect Powell et al.
identify.** Screen 3 (the predicate library) must carry all three, not just the FFR percentage.

### 4.4 EuSpRIG itself

European Spreadsheet Risks Interest Group — the venue that publishes most of this work
(`eusprig.org`, conference proceedings with ISBNs, "Horror Stories" page). SECONDARY. The widely
repeated *"EuSpRIG estimates over 90% of all spreadsheets contain errors"* traces back to the Panko
tables above and inherits every caveat in §4.3. **Do not cite EuSpRIG as an independent corroboration
of Panko; it is the venue Panko publishes in.**

---

## 5. ORACLE-FREE DETECTION — the state of the art, with numbers

### 5.1 ExceLint — the strongest result, and it already implements L4 test 2

**Barowy, Berger & Zorn, "ExceLint: Automatically Finding Spreadsheet Formula Errors",
*Proc. ACM Program. Lang.* 2, OOPSLA, Article 148 (November 2018), 26 pp,
doi:10.1145/3276518; preprint arXiv:1901.11100.** VERIFIED-AT-SOURCE (pdftotext, read raw).

**Method.** Static analysis, no oracle. Each formula gets a *fingerprint* (a vector of its reference
shape); `EntropyTree` decomposes the sheet into rectangular regions by minimising total entropy across
splits; a formula that is a *surprising* disruption to its rectangular neighbourhood is flagged. The
insight it monetises: *"our analysis directly leverages the rectangular character of spreadsheets."*

**Corpus.** 70 benchmarks, *"developed by researchers (not us)"* for CUSTODES, drawn from the EUSES
corpus. **99 to 12,121 cells (mean 1,580); 3 to 2,662 formulas (mean 360).**

**Ground truth, and this is the expensive part.** The authors re-annotated all 70 spreadsheets by hand,
**~34 person-hours cumulatively**, one formula error per 5.1 minutes. Result: CUSTODES' own ground-truth
file marks **1,199 cells as smells**; of those, **102 are actual formula errors**; re-annotation found
**295 more**, for **397 formula errors total**. Separately they observed **9,924 "unusual
constructions"** they declined to call errors.

**Numbers.**

| | ExceLint | CUSTODES |
|---|---:|---:|
| mean precision (per workbook) | **64.1%** | **20.3%** |
| median precision | **100%** | **0.0%** |
| mean recall | **62.1%** | **61.2%** |
| median recall | 100% | 100% |
| **mean *adjusted* precision** (vs random flagger) | **63.7%** | **19.6%** |
| random flagger beats it | **7 of 70** | 14 of 70 |
| median runtime | 5 s / spreadsheet | comparable |

**The random-flagger baseline is L4 test 2, already built.** Verbatim:

> "The baseline is the expected precision obtained by randomly flagging cells. … A random flagger
> samples without replacement; even a bad tool should not flag the same cell twice. Therefore, we
> compute the expected value using the hypergeometric distribution, which corrects for small sample
> size."

And they pre-empt the degenerate-predicate objection explicitly, under the heading **"High Precision
When Doing Nothing"**:

> "ExceLint flags no cells in 33 of 70 cases. However, two facts dispel this concern. First, ExceLint
> has a high formula error recall of 62.1%. Second, in 22 cases where ExceLint does nothing, the
> benchmark contains no formula error."

**Honesty about recall, which the brief should copy verbatim:**

> "recall is inherently difficult to measure when using real-world spreadsheets as benchmarks. To
> accurately compute recall, the true number of false negatives must be known. … Since we adopt a
> conservative definition for error, it is likely that the real recall figures are lower than what we
> report."

Other measured facts worth carrying: fingerprint collisions average **0.33%** per workbook;
**62.3% of all regions and 86.8% of formula regions are rectangular** (mean; medians 63.2% / 90.5%) —
the assumption the whole method rests on, measured rather than asserted.

**Code.** `github.com/ExceLint/ExceLint` — **BSD-2-Clause, 74★, archived 8 Jun 2021**, F#/C#, Excel-COM
bound. Successor `github.com/ExceLint/ExceLint-addin` — **Apache-2.0, 105★**, TypeScript, Office.js,
"works for all modern versions of Excel including Mac, Windows, and online", sideloaded manifest, not
in the Office store, *"provided without any guarantee of support."* SECONDARY (repo pages).

- **Where it fits:** **L6-adjacent / a candidate L4 mutant-generator oracle.** Its real contribution to
  this program is the **methodology** — hypergeometric degenerate baseline, adjusted precision,
  explicit "flags nothing" accounting, honest recall caveat — which is directly transplantable into
  the qualification gate.
- **Where it stops:** it finds *formula* errors in *user-authored* layouts. The IFSCA template's
  formulas are authored by the regulator and are not under test; the *filer's data* is. ExceLint has
  nothing to say about whether a portfolio value is right. Also: COM/Office.js bound, so it does not
  run headless in a Python pipeline without an Excel host.

### 5.2 CheckCell — data debugging, the closest conceptual relative

**Barowy, Gochev & Berger, "CheckCell: Data Debugging for Spreadsheets", OOPSLA '14 (ACM SIGPLAN
Notices 49(10)), doi:10.1145/2714064.2660207.** SECONDARY — I read the venue page and search summaries;
I did **not** open the preprint PDF, so I have **no precision/recall figures for CheckCell**.

**Method (SECONDARY).** Combines program analysis with statistical analysis to find *input data* whose
value has an unusual impact on the spreadsheet's outputs — it perturbs inputs, measures output
sensitivity, and ranks cells by impact. Reported: it finds injected typographical errors produced by a
generative typo model *"trained with data entry from 100,000 Mechanical Turk tasks"*, and
*"automatically identifies a key flaw in the infamous Reinhart and Rogoff spreadsheet."*
Code: `github.com/plasma-umass/DataDebug`.

- **Where it fits:** **directly on L6, and it is the best available prior art for it.** The brief's L6
  proposes metamorphic relations authored by hand. CheckCell is the *dual*: instead of asking "does
  output change when it shouldn't", it asks "which input has an implausibly large influence on the
  output" — and it needs no oracle either. On a fund return, an impact-ranked list of input cells is
  exactly the triage order a supervisor wants for the seven **undecidable** predicates.
- **Where it stops:** it ranks *suspicion*, it does not decide. It has no notion of a regulatory
  clause. And crucially, **on the FME workbook there is almost nothing for it to work with**: 38 of
  294 formulas express a checkable relation, so the computational graph through which impact
  propagates is thin. The 4,627-node graph `formulas` builds is mostly carry-forward edges.
- **Open: UNVERIFIED** — I do not have its measured precision/recall. Anyone citing CheckCell in this
  program must open the OOPSLA'14 preprint first (`people.cs.umass.edu/~emery/pubs/CheckCell-preprint-OOPSLA2014.pdf`).

### 5.3 CUSTODES — and a correction to the lane brief

**Cheung, Chen, Liu & Xu, "CUSTODES: Automatic Spreadsheet Cell Clustering and Smell Detection Using
Strong and Weak Features", ICSE 2016** (38th ICSE) — **not ICSE 2017**, as the lane framing had it.
The IEEE Xplore record 7886926 is the 2016 proceedings. SECONDARY.

Method: clusters spreadsheet cells adaptively using "strong and weak features" so the clustering
adapts to each sheet's tabulation style, then detects smells within clusters. Reported **F-measure
0.72** on **70 spreadsheets randomly sampled from EUSES, containing 1,610 formula cell clusters**.

**The important qualification comes from ExceLint, VERIFIED-AT-SOURCE:** *"CUSTODES is not an error
finder"* — it finds *smells*. Measured against a formula-error ground truth its mean per-workbook
precision is **20.3%, median 0.0%**. **A smell detector and an error detector are different products,
and the F-measure 0.72 is against a smell label, not an error label.** This is the same
definition-of-error problem Powell et al. identify, recurring inside the tooling literature.

- **Where it fits:** its **benchmark suite** is the reusable asset, not the tool.
- **Where it stops:** median precision 0.0% is a 100%-FPR operating point on half the corpus — precisely
  the failure mode §2.3.1 of the brief says is fatal.

### 5.4 CACheck / AmCheck — cell arrays

**Dou, Xu, Cheung & Wei, "CACheck: Detecting and Repairing Cell Arrays in Spreadsheets",
IEEE TSE 43(3), 2017, doi:10.1109/TSE.2016.2584059.** SECONDARY.

Method, no oracle: cells computed under the same semantics cluster into a *cell array* (a row or
column); ad-hoc edits *degenerate* the array; a degenerated array is a smell, and the intended
semantics can be recovered and the array repaired. Reported: **1,586 cell arrays in EUSES suffer
ambiguous computation smells, covering 7.8% of identified cell arrays**; CACheck detects **98.3%** of
AmCheck's detections plus **401 additional** smelly arrays. Also evaluated on Enron.

- **Where it fits:** **L1 and L6.** The IFSCA workbook is *made of* cell arrays — the 32 shared-formula
  groups I measured (`E76:E84`, `D167:L167`, `AA22:AA30` …) are literally cell arrays with the master
  formula declared. **A filed workbook whose shared-formula group has been broken in one row is a
  degenerated cell array, and CACheck's criterion detects that with no oracle.** This is a concrete,
  cheap L6 relation the brief does not currently list: *every cell in a template-declared shared-formula
  range must still carry the template's formula.*
- **Where it stops:** it works on user-evolved spreadsheets. Here the template *declares* the arrays, so
  the detection is trivial and the interesting question — is the *data* right — is untouched.

### 5.5 Melford — neural, and honest about what it detects

**Singh, Livshits & Zorn, "Melford: Using Neural Networks to Find Spreadsheet Errors", Microsoft
Technical Report MSR-TR-2017-5, January 2017.** VERIFIED-AT-SOURCE (pdftotext of the MSR PDF; some
tables are two-column-mangled, so I quote only what read cleanly).

Method: a spatial abstraction of the 5×5 neighbourhood around a cell (cell *types*, not values) feeds
a neural classifier that predicts whether a cell **should contain a formula given that it contains a
number** — the "number where a formula belongs" error class (e.g. a hardcoded column total). *"The
approach requires no labeled data"*: labels come from the corpus itself, since most cells that should
be formulas are.

Numbers, VERIFIED-AT-SOURCE from the raw text: trained on ~**9.1 million vectors** from the
ExcelSamples dataset (80/20 split), with **VEnron** (`sccpu2.cse.ust.hk/venron/`, 360 clusters) as the
other training corpus; evaluated on the **CUSTODES benchmark** (290 sheets, 22 with no numeric cells;
of 2,212 cells, 422 are CUSTODES-labelled errors); *"finds more than **150 real errors** in a collection
of **70 benchmark workbooks**"*; applied to **720 EUSES financial spreadsheets**, *"within hours it
confirmed real errors previously unknown to us in **26 of the 696 workbooks**"*. Reported as
*"average precision close to CUSTODES with a significantly lower false positive rate."*

- **Where it fits:** **L2 hard-guard analogue and an L6 relation.** *"A cell that the template declares
  as a formula must not, in the filing, contain a literal"* is a deterministic version of Melford's
  entire error class — and **L1 already knows exactly which 505 cells those are.** No neural network
  required; the template *is* the label. This is a free predicate the brief has not enumerated.
- **Where it stops:** one error class; a tech report, not a peer-reviewed paper; **no public code or
  model release found — NOT-FOUND.** Precision/recall numbers I could not read cleanly from the
  two-column PDF: **UNVERIFIED** beyond what is quoted above.

### 5.6 Schmitz & Jannach — how real spreadsheet ground truth actually gets made

**Schmitz & Jannach, "Finding Errors in the Enron Spreadsheet Corpus", VL/HCC 2016, TU Dortmund.**
VERIFIED-AT-SOURCE (pdftotext, read raw).

Their opening criticism is the brief's §9.2 problem, stated for spreadsheets:

> "the proposed methods were often designed based on assumptions about the nature of errors and were
> evaluated with mutations of correct spreadsheets."

Method, no oracle and no mutation: recover *versions* of the same spreadsheet from the Enron corpus —
by reconstructing email conversations and looking for bug-fix language, and by filename similarity
(`_v2`, `_fixed`) — then diff formulas between versions. If one or a few formulas changed, that is a
candidate error. A human then adjudicates.

**Yield, and this is the number to remember:** from ~200 manually inspected files they identified
**28 quantitative errors** with high confidence — **14 mechanical, 9 logical, 5 omission** — plus
**8 qualitative errors** (e.g. wrong labels). One example is a genuine omission error whose fix email
said *"Had to scale column M by the gas price!!!"*.

- **Where it fits:** **§9.2 methodology.** It is the only published technique for extracting *real*
  labelled spreadsheet errors from an unlabelled corpus, and its lever is **version pairs plus a
  human-authored change rationale**.
- **Where it stops:** **28 errors.** After mining a 15,770-spreadsheet corpus. That is the true cost of
  real ground truth, and it should be quoted whenever anyone proposes "just find a labelled corpus."
- **Transfer to IFSCA — this is the actionable bit.** IFSCA publishes **versioned templates** (the
  scratchpad has `ALR_V2_3`, `EDR_1_V2_3`, `IBU_Operations_Report_V2_3`, an FME format dated 02/01/2026,
  a CMI format "Updated" 09/04/2026). **Diffing successive published versions of the same prescribed
  format is the Schmitz method applied to the regulator's own corrections** — and each diff is a
  *statement by the regulator about what was wrong or under-specified before.* That is a labelled
  signal that exists today, is public, and nobody has mined it.

### 5.7 The LLM era — 2024–2026

| work | what it is | measured | warrant |
|---|---|---|---|
| **SpreadsheetBench** (NeurIPS 2024 D&B, spotlight) | 912 real questions from Excel forums, OJ-style eval, 3 test cases per instruction | model scores **0.05% – 23.65%** | SECONDARY |
| **SpreadsheetBench 2** — arXiv:**2606.29955**v1, 29 Jun 2026, Renmin Univ. / Aptura AI / Shortcut AI / AfterQuery | **321 tasks**, generation + **debugging** + visualisation, built from *"authentic business data, including financial reports and corporate filings"*, expert-annotated. Avg **11.8 worksheets/instance**, **429.0** instruction words, **593.5** cell modifications | see table below | **VERIFIED-AT-SOURCE** (pdftotext) |
| **SheetCopilot** | 221 synthetic tasks, Exec@1 / Pass@1 | SheetMind reports 54.8% functional correctness vs SheetCopilot 44.3% | SECONDARY |
| **SheetAgent** (WWW '25, doi:10.1145/3696410.3714962) | generalist spreadsheet agent | *"16.8% higher Pass@1"* than SheetCopilot; on SheetRM, Pass@1 **46.1** (GPT-4o) / **62.5** (o1) | SECONDARY |
| **FLARE** — Thorne, EuSpRIG 2025, arXiv:2506.17330 | "Formula Logic, Auditing, Reasoning and Evaluation" — the only benchmark found that names **auditing** as a task | scores NOT-FOUND — the EuSpRIG PDF returned HTTP 403 | SECONDARY (abstract only) |
| **A Survey on LLMs for Spreadsheet Intelligence** — Vuong, Tit, Cordy, Univ. Luxembourg, 2026, handle 10993/67962 | survey; no arXiv ID or DOI found | — | SECONDARY |

**SpreadsheetBench 2, Table 3 — VERIFIED-AT-SOURCE, read from the converted PDF:**

| Model | Template Acc. | Financial Modeling Acc. | **Debugging Acc.** | Visualization Acc. | **Overall Acc.** |
|---|---:|---:|---:|---:|---:|
| Claude Opus 4.6 | 52.58 | 34.00 | **12.00** | 62.50 | **34.89** |
| GPT-5.2 | 35.05 | 33.00 | **8.00** | 45.83 | 26.79 |
| Gemini 3.1 Pro | 28.87 | 31.00 | **7.00** | 41.67 | 23.68 |
| GLM-5 | 17.53 | 22.00 | 7.00 | 37.50 | 17.14 |
| Deepseek-V3.2 | 25.77 | 7.00 | 10.00 | 33.33 | 15.58 |
| Kimi K2.5 | 18.56 | 15.00 | 4.00 | 41.67 | 14.64 |
| Qwen3.5-397B-A17B | 17.53 | 10.00 | 3.00 | 25.00 | 11.22 |
| MiniMax M2.5 | 7.22 | 8.00 | 4.00 | 16.67 | 7.17 |

All eight evaluated in thinking mode, GPT-5.2 and Gemini 3.1 Pro at high reasoning effort, SWE-agent
scaffold, 50-turn cap, tools `bash` / `view_xlsx` / `submit`. The authors' own diagnosis:

> "insufficient spreadsheet inspection and incorrect target-cell selection are the dominant
> bottlenecks."

**This is the most directly citable new evidence in the entire lane for the brief's Part 2.** A
frontier model, in thinking mode, with 50 turns and a shell, on *financial* spreadsheets curated from
*corporate filings*, achieves **12.00% accuracy at debugging** — the task closest to "find what is
wrong with this filing" — and **34.89% overall**. Denominator: 321 tasks total; the debugging subset's
own n is not stated in the portion I read (the debugging Acc. figures are round multiples of 1.00,
consistent with n = 100). **Flag that n as UNVERIFIED before quoting.**

**Also note what the benchmark does *not* measure: the false-positive direction.** Every metric is
"did you match the golden file", so a system that reports a problem where none exists is not scored.
The absent arm the brief keeps finding is absent here too.

---

## 6. PUBLIC SPREADSHEET CORPORA — sizes, licences, locations, and honest utility

| corpus | size | source | licence | location | warrant |
|---|---|---|---|---|---|
| **ENRON** (Hermans & Murphy-Hill, ICSE 2015, "Enron's Spreadsheets and Related Emails: A Dataset and Analysis") | **15,770** spreadsheets, **9,120 with formulas**, **20,277,835 formula cells**; from 265,586 attachments / 51,572 Excel files / 16,189 unique by MD5 | Enron email archive (subpoenaed, public) | **CC BY 4.0** | figshare `1221767` (posted 30 Oct 2014); mirror `sheetjs.github.io/enron_xls/` | SECONDARY (figshare/blog); the 9,120 / 20,277,835 figures are **VERIFIED-AT-SOURCE** via Panko 2015 quoting Hermans |
| **FUSE** (Barik, Lubick, Smith, Slankas, Murphy-Hill, MSR 2015, pp. 486–489) | **249,376** unique spreadsheets from **2,127,284** spreadsheet-returning URLs, filtered from **26.83 billion** HTTP responses / **1.9 PB** of Common Crawl; ~60,000 compute-hours | Common Crawl | *"unencumbered by any license agreements"* | Zenodo record `581678` | SECONDARY |
| **EUSES** (Fisher & Rothermel, WEUSE/SIGSOFT SEN 30(4), 2005) | **~4,498** spreadsheets (5,607 files, 4,499 unique/processable) | assorted web sources; database, financial, grading, homework, inventory, modelling | **unclear** — the `funcalc-euses` variant is CC BY 4.0; the original's licence NOT-FOUND | tera-PROMISE / `openscience.us/repo`; TU Graz modified variant | SECONDARY |
| **VEnron 1.0 / 1.1 / 2** and **VEUSES** | VEnron1.0 **360 groups / 7,294** sheets; VEnron1.1 **322 / 7,171**; **VEnron2 1,609 groups / 12,254 sheets**; VEUSES **177 / 363** | Enron (versioned) and EUSES (versioned) | NOT-FOUND | `tcse.cn/~wsdou/project/venron`; `castle.cse.ust.hk/venron/` | SECONDARY |
| **CUSTODES benchmark suite** | **70** spreadsheets, 1,610 formula-cell clusters, hand-labelled smells (1,199 smell cells); ExceLint's re-annotation adds **397** formula-error labels | subset of EUSES | inherits EUSES | `sccpu2.cse.ust.hk/custodes/` | ExceLint numbers **VERIFIED-AT-SOURCE**; availability SECONDARY |
| **SpreadsheetBench** | **912** tasks / 5,426 workbooks (per xlsx-corpus-bench) | Excel forums | NOT-FOUND (repo `RUCKBReasoning/SpreadsheetBench`) | GitHub | SECONDARY |
| **SpreadsheetBench 2** | **321** tasks, avg 11.8 sheets | financial reports & corporate filings, expert-curated | NOT-FOUND | `spreadsheetbench.github.io` | task counts **VERIFIED-AT-SOURCE** |

### 6.1 The honest assessment the lane asked for

**For the false-failure rate on the FME return: useless, and it is not a close call.**

The FFR the product prints on Screen 2 is *"this check fired on X% of N clean **IFSCA FME quarterly
returns**"*. That quantity is defined over a population of 217 FMEs / 360 schemes / ~868 filings a
year, filed on one prescribed template with one prescribed vocabulary. **Nothing in ENRON, FUSE, EUSES
or VEnron is a member of that population.** A predicate like *"Principal Officer ≠ Compliance Officer"*
or *"scheme auth date ≤ period end"* cannot fire on a Common Crawl budget spreadsheet at all — it has
no fields to bind to. Measuring FFR there would produce 0% on a denominator of zero applicable rows,
which is not a low false-failure rate, it is a category error. §9.2 stands **unrelieved**.

**For testing L1 schema-induction robustness: genuinely useful, and this is the strongest new
argument for using them.**

L1's job is to derive a field graph from an arbitrary published `.xlsx`. Its failure modes are
*parsing* failure modes, and those are corpus-general: shared formulas, `x14` extensions, merged
headers, hidden sheets, array formulas, external links, legacy `.xls`, embedded models. **This lane
found two such failures on a single workbook.** FUSE (249,376 sheets, unencumbered) and ENRON (15,770,
CC BY 4.0) are exactly the right instrument for the question *"on what fraction of real workbooks does
my extractor silently return a wrong count?"* — and the answer is measurable, publishable, and
requires no correctness labels at all.

**Concretely proposed L1 robustness metric (no oracle needed):**
> For each workbook in a random sample of FUSE ∪ ENRON, compute the schema three ways — raw OOXML,
> openpyxl, and post-LibreOffice-normalisation — and report the fraction on which the three
> **disagree**, broken down by construct. Disagreement is a defect detected without an oracle. This is
> a metamorphic relation over *readers*, and it is L6 applied to the instrument instead of the artifact.

That framing also answers the brief's standing bias directly: it is a measurement that can *fail*, it
is cheap, and it does not require the corpus to be labelled.

**Third use, secondary:** ENRON/VEnron2 are the right corpus for calibrating an L4 **mutation
operator** distribution — what kinds of formula edits do real people actually make — which is currently
an unexamined assumption. Schmitz & Jannach's 28 errors (14 mechanical / 9 logical / 5 omission) are
the only real-world prior available, n = 28.

---

## 7. ASSET REGISTER — where each fits in L0–L7, and where it stops

| asset | licence / status | **fits** | **stops** |
|---|---|---|---|
| **raw `zipfile` + `lxml`** | stdlib / BSD, in-venv | **L0/L1 core.** The only reader that sees `x14` validations, shared-formula masters, `connections.xml`, the data model, `calcChain`. Also the **L4 mutation substrate** (§3.1) | you write the OOXML semantics yourself; no recalculation |
| **openpyxl 3.1.5** | MIT | **L1** for protection, merged geometry, defined names, shared-formula expansion (505) | **drops all `x14` validations with a warning**; **round-trip destroys 98.2% of the file**; no calc engine |
| **LibreOffice headless** | MPL-2.0, `/opt/homebrew/bin/soffice` | **L0 normaliser — adopt.** Expands shared formulas *and* migrates `x14` → main namespace, verified | drops the Power Pivot model and `calcChain`; loses 1 of 54 validations; 3.9 s/workbook; heavyweight dependency |
| **`formulas` 1.3.4** | **EUPL 1.1+ ⚠** | **L1 dependency graph** (4,627 nodes / 3,185 edges, 2.33 s) and **L5 recalculation**; the engine behind the §3.2 kill | 90.1% function coverage (Lookup 82.5%); copyleft — legal review before core adoption |
| **`pycel` 1.0b30** | **GPL-3.0 ⚠** | L5 targeted cell evaluation | dependency graph is **lazy**, not a workbook extractor; copyleft |
| **`python-calamine` 0.8.2** | MIT | L0 fast triage: sheet list, visibility, merged ranges, values in 2 ms | **no formulas, no validations, no protection** |
| **`xlsx2csv` 0.8.6** | MIT | cheap value diff | cached values only |
| **`koala2`** | — | — | **REJECT** — unmaintained; successor is `xlcalculator` |
| **`knowledgestack/excel-parser`** | MIT, 51★ | claims *"data validation — all types incl. cross-sheet lists"*, dependency graphs, citation-ready JSON; wraps openpyxl *"and uses lxml for the bits openpyxl loses"* — i.e. it claims to solve exactly the §1.3 gap | **EVALUATE, do not adopt.** **Not installable from PyPI under `excel-parser` or `excel_parser`** — install failed, so the `x14` claim is **UNVERIFIED**. Also self-declares: pivot tables not fully parsed, sparklines dropped, external links unresolved |
| **`witanlabs/xlsx-corpus-bench`** | Apache-2.0, **2★** | reference method for measuring reader fidelity at corpus scale | vendor-authored, vendor tops the table; treat rankings as promotional |
| **ExceLint / ExceLint-addin** | BSD-2-Clause (archived 2021) / Apache-2.0, 105★ | **L4 methodology — adopt the method, not the code:** hypergeometric random-flagger baseline, adjusted precision, "flags nothing" accounting | Excel-COM / Office.js bound, no headless Python path; targets user-authored formula errors, not filer data |
| **CheckCell / `plasma-umass/DataDebug`** | licence NOT-FOUND | **L6 dual** — impact-ranked suspicion over *inputs*, no oracle | ranks, does not decide; **no precision/recall obtained — UNVERIFIED**; thin computational graph on the FME workbook |
| **CUSTODES benchmark suite** | inherits EUSES | the 70-sheet suite is a reusable L1-robustness fixture | the *tool* has median precision 0.0% — a 100%-FPR operating point |
| **CACheck criterion** | paper only | **L6 relation, free:** every cell in a template-declared shared-formula range must still carry the template's formula (32 groups in the FME workbook) | detection is trivial once L1 declares the arrays; says nothing about data |
| **Melford criterion** | no code found | **L6 relation, free:** a cell the template declares as a formula must not contain a literal in the filing (L1 knows all 505) | one error class; no released model |
| **ENRON (figshare 1221767)** | **CC BY 4.0** | L1 robustness corpus; mutation-operator calibration | **no correctness labels**; wrong population for FFR |
| **FUSE (Zenodo 581678)** | unencumbered | L1 robustness corpus at scale (249,376) | same |
| **EUSES / VEnron2** | unclear / NOT-FOUND | benchmark provenance for every tool above | same; licence unresolved |
| **SpreadsheetBench 2 (arXiv:2606.29955)** | NOT-FOUND | **evidence, not a component** — 12.00% debugging accuracy on financial-filing data | measures only the miss direction; debugging-subset n **UNVERIFIED** |

---

## 8. CORRECTIONS TO THE BRIEF AND ARCHITECTURE

1. **§4.3 "35 data validations (only 3 list-type with a named vocabulary)" → 54 validations, 22
   list-type.** Nineteen live in the `x14` extension namespace. The sub-claim that the template
   barely constrains its vocabularies is **REFUTED**; the sibling claim about formulas is confirmed.
2. **§4.3 / L1 "294 formulas" → 505 formula-bearing cells; 294 is the count of `<f>` elements carrying
   text.** Both are correct measurements of different things. Only 505 is the right denominator for a
   coverage fraction.
3. **ARCHITECTURE L1 "all extracted by pattern-matching the OOXML in minutes"** — true, and the same
   sentence is now the third demonstrated instance of §4.4's failure mode. **Recommend promoting it
   into §4.4 as self-demonstration #3**, because it is the best one: it was found by a *replication*,
   which is the control the brief says it wants.
4. **CUSTODES is ICSE 2016, not ICSE 2017.**
5. **ARCHITECTURE L4 test 2 ("can a degenerate artifact satisfy it?") is not novel** — ExceLint
   (OOPSLA 2018) implements a hypergeometric random-flagger baseline and reports adjusted precision.
   **This is good news**: it is a published, citable precedent for the gate's most defensible test.
6. **RND-BRIEF §6.2 lists no spreadsheet-specific tooling at all.** The L0/L1 row is QuantMind, whose
   fit is marked unverified. On the evidence here, **L0/L1 is `soffice --convert-to xlsx` +
   `zipfile`/`lxml` + `formulas`**, all verified by execution today, and QuantMind is not needed for
   this layer.
7. **§9.7 ("check whether QuantMind's typed shapes extend to a protected xlsx with merged headers") is
   answerable without QuantMind and the answer is now known for the general case:** protection is not
   an obstacle (it is advisory; every reader tested read straight through it). Merged headers are
   recovered identically by openpyxl, calamine and raw XML (252 ranges, three-way agreement). **The
   real obstacle is neither — it is the extension namespace.** Recommend rewriting §9.7 accordingly.

---

## 9. What this changes about the design

**1. L0 gains a mandatory normalisation step, and L7 gains a matching prohibition.**
Every artifact is processed twice: content-addressed **as delivered** (that hash is what L7 signs),
and normalised through `soffice --headless --convert-to xlsx` **for analysis**. Verified: normalisation
converts 294 → 505 visible formulas and 3 → 22 visible list vocabularies, deterministically, in 3.9 s.
The prohibition: **never re-serialise the artifact with openpyxl anywhere in the pipeline** — measured
loss 98.2% of bytes, 24 parts, and every `x14` validation.

**2. L1 must declare its own extraction coverage, not just the artifact's.**
The system's founding claim is that a silent all-clear is not information. The same argument applies
one level down: **a schema extractor that silently returns 35 of 54 validations is the failure the
product exists to prevent, occurring inside the product.** L1 should emit, alongside the field graph,
an *extraction manifest*: parts read, parts skipped, namespaces encountered, constructs not understood
(`x14:dataValidation`, `model/item.data`, `connections.xml`, `t="array"`), and a three-way
raw/openpyxl/normalised agreement check. **Where the three readers disagree, the affected fields are
`UNCHECKED(source unreadable)` by construction, not silently absent.** This adds a seventh reason to
L5's closed vocabulary: **`extractor disagreement`**.

**3. Three no-oracle predicate families are now free, and they were not on the list.**
All three are read directly off L1's induced schema, need no model, and need no correct answer:
- **Melford's class, deterministically:** a cell the template declares as a formula must not contain a
  literal in the filing. **505 cells** are covered on day one.
- **CACheck's class:** every cell inside a template-declared shared-formula range must still carry the
  template's formula. **32 groups** in the FME workbook.
- **Vocabulary membership over the *complete* validation set:** **22** enumerated vocabularies, not 3.
These materially move the coverage fraction on Screen 2 without touching L3, and they are exactly the
kind of increment Screen 4 exists to show.

**4. L4 is no longer a research risk and should move ahead of L3 in the residency plan.**
The mutation loop ran end-to-end on the real artifact in seconds (§3): surgical mutant, engine recalc,
predicate kill, mutation score 1/1, FFR contribution 0/1. Adopt ExceLint's published discipline
wholesale — hypergeometric random-flagger baseline, *adjusted* precision, explicit accounting of runs
where the predicate fires on nothing — and cite OOPSLA 2018 for it rather than presenting it as new.

**5. Every FFR the product prints must carry Powell's three declarations, or it repeats the defect it
was built to expose.** *The definition of error · the detection method · the described sample.* The
literature's headline number has **four different denominators across four documents by the same
author** (§4.2), and the field's own critical review concludes the evidence *"does not provide
sufficient grounds for a reliable, quantitative estimate."* Screen 3 must therefore show, per
predicate: the clause, the code, the mutation score **and its equivalent-mutant denominator**, the FFR
**and the corpus it was measured on with n**, and the admission date. **A bare percentage on Screen 2
is the same instrument failure at a different scale.**

**6. §9.2's clean-corpus problem is unrelieved by public corpora — but a real labelled signal exists
and nobody has mined it.** ENRON/FUSE/EUSES/VEnron are the wrong population for FFR and the right
population for L1 robustness (§6.1). The unexploited asset is **Schmitz & Jannach's method applied to
IFSCA's own versioned templates**: successive published versions of the same prescribed format,
diffed. Each diff is the regulator stating what was wrong before. Nine workbooks with version strings
are already on disk. That is a public, labelled, defensible corpus of *regulator-confirmed* template
defects — and it costs an afternoon.

**7. New external evidence for Part 2, stronger than anything currently in §3.5.**
SpreadsheetBench 2 (arXiv:2606.29955, 29 Jun 2026): 321 expert-curated tasks built from financial
reports and corporate filings, eight frontier models in thinking mode with a 50-turn agent scaffold —
**best overall accuracy 34.89%, best *debugging* accuracy 12.00%** (Claude Opus 4.6). The authors'
diagnosis is *"insufficient spreadsheet inspection and incorrect target-cell selection."* And, in the
brief's own idiom: **the benchmark scores only the miss direction — a system that flags a non-existent
problem is not penalised anywhere in it.** The absent arm is absent in the state of the art too.

---

## 10. OPEN, UNVERIFIED, AND NOT-FOUND — the declared residue

- **CheckCell precision/recall: UNVERIFIED.** I did not open the OOPSLA'14 preprint. Nobody may cite a
  CheckCell number in this program until someone does.
- **The "88% of spreadsheets have errors" primary source: NOT-FOUND.** `panko.com/ssr/whatknow.htm`
  → HTTP 404; `panko.shidler.hawaii.edu` → DNS failure. The reported "88% of 113" phrasing is
  **UNVERIFIED**.
- **SpreadsheetBench 2 debugging-subset n: UNVERIFIED.** The 12.00 / 8.00 / 7.00 pattern is consistent
  with n = 100 but the paper section I read does not state it.
- **FLARE (EuSpRIG 2025) scores: NOT-FOUND** — the EuSpRIG PDF returns HTTP 403.
- **Melford's precision/recall table: UNVERIFIED** — the MSR tech report's two-column tables did not
  survive `pdftotext`.
- **`knowledgestack/excel-parser`'s cross-sheet-list claim: UNVERIFIED** — not installable from PyPI
  under either candidate name; the claim would, if true, close the §1.3 gap in one dependency.
- **EUSES and VEnron licences: NOT-FOUND.** Do not redistribute either until resolved.
- **`calcChain` has 506 entries against 505 `<f>` elements.** One-cell discrepancy, unexplained.
- **LibreOffice writes 53 main-namespace validations where 35 + 19 = 54.** One validation lost in
  normalisation, unexplained. **This is a defect in the step §9 recommends adopting** and must be
  characterised before it ships.

### Coverage denominators for every absence claimed above
- *"No public corpus carries per-cell correctness labels"* — searched: ENRON (figshare), FUSE (Zenodo),
  EUSES (tera-PROMISE), VEnron/VEnron2/VEUSES (tcse.cn), CUSTODES suite, SpreadsheetBench 1 & 2.
  **Positive control passed:** the CUSTODES suite *does* carry 1,199 hand-labelled smell cells and
  ExceLint's re-annotation adds 397 error labels — so labelled data is findable when it exists, and
  n = 70 spreadsheets is its scale.
- *"No spreadsheet checker declares per-rule coverage or per-rule false-failure rate"* — searched
  GitHub and the web for spreadsheet validation with coverage declaration; found only commercial
  21-CFR-Part-11 validation vendors (Ofni ExcelSafe, SciCord, spreadsheetvalidation.com) and generic
  data-quality frameworks. **Positive control passed:** ExceLint *does* publish per-benchmark precision
  with a degenerate baseline — so a per-rule error-rate disclosure is findable in the *research*
  literature. **NOT-FOUND in any shipping product.** The claim that survives is narrow and true:
  *no shipping compliance product discloses each rule's measured false-failure rate.*
- *"openpyxl drops x14 validations"* — **not a search result; measured.** Warning emitted at
  `openpyxl/worksheet/_reader.py:329`, and post-round-trip audit shows `dvX14 = 0`.

---

### Reproduction

```
python  = /Users/abishaikc/Gift/.venv/bin/python   (3.12.12; openpyxl 3.1.5, lxml 6.1.1,
          formulas 1.3.4, pycel 1.0b30, python-calamine 0.8.2, xlsx2csv 0.8.6 — installed via uv)
soffice = /opt/homebrew/bin/soffice
scripts = /private/tmp/claude-501/-Users-abishaikc-Gift/894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad/
            extract_raw.py     — raw OOXML schema induction, 9-workbook audit
            extract_ext.py     — x14 validations, shared-formula groups, connections, calcChain
            tool_matrix.py     — openpyxl capability + destructive round-trip measurement
            tool_matrix2.py    — calamine / xlsx2csv / formulas / pycel
          (mutation seeding and the kill demo were run inline; both are reproduced verbatim in §3)
target  = /Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx
```

---

## Adversarial verification (independent pass)

**Run 10 Aug 2026 by a separate agent tasked to REFUTE, not to agree.** I did not accept any citation
in this lane as evidence. For each claim below I opened the primary artifact myself — the arXiv abstract
page or the PDF I downloaded and converted, the GitHub REST API record, the Zenodo/figshare API record,
the licence file — and re-derived the number. Where I could not confirm, the verdict is REFUTED or
UNVERIFIABLE, not "probably fine". Claims selected on one criterion: **if this were false, what breaks
in the design?**

Note on the lane's own internal measurements (§1–§3): those are executions against a local file. I did
not re-run them, and they are outside this pass's remit. Everything below is an *external* claim — a
paper, a repo, a licence, a corpus — i.e. exactly the class the lane could only take on trust.

### Verdict table

| # | Claim (as stated in this lane) | Verdict | Primary artifact I opened |
|---|---|---|---|
| 1 | SpreadsheetBench 2 = arXiv:2606.29955, 321 tasks, best overall **34.89%**, best debugging **12.00%** (Claude Opus 4.6) | **CONFIRMED** | arXiv abs page + `arxiv.org/pdf/2606.29955v1` → `pdftotext`; Table 3 row reproduces to the digit |
| 2 | "The benchmark scores only the miss direction — a system that flags a non-existent problem is not penalised anywhere in it" | **REFUTED as stated** | SB2 Table 3 caption + Appendix D.4 |
| 3 | ExceLint: mean precision 64.1% / recall 62.1%; CUSTODES 20.3% / median 0.0%; adjusted 63.7% vs 19.6%; random flagger wins 7 of 70; flags nothing in 33 of 70, 22 of which contain no error; hypergeometric baseline | **CONFIRMED — verbatim** | `arxiv.org/pdf/1901.11100` → `pdftotext`, lines 1162–1167, 1286–1296, 1339–1348 |
| 4 | `witanlabs/xlsx-corpus-bench`: LibreOffice recalc-exact **91.9%** on FUSE ⇒ "L5 predicates inherit a several-percent engine-disagreement floor" | **QUALIFIED — evidentially void** | GitHub REST API: repo + full commit log |
| 5 | FUSE is *"unencumbered by any license agreements"* | **REFUTED** | `zenodo.org/api/records/581678` → `license: cc-by-4.0` |
| 6 | CheckCell / `plasma-umass/DataDebug` licence **NOT-FOUND** | **REFUTED** | GitHub API → `GPL-2.0`, plainly declared |
| 7 | `formulas` is EUPL 1.1+ ⚠; `pycel` is GPL-3.0 ⚠ (copyleft gate on the L1/L5 core) | **CONFIRMED (minor qualification)** | GitHub API + `LICENSE.txt` raw |
| 8 | ENRON corpus is **CC BY 4.0**, figshare `1221767`, posted 30 Oct 2014 | **CONFIRMED** | `api.figshare.com/v2/articles/1221767` |
| 9 | CUSTODES is **ICSE 2016, not ICSE 2017** (correction #4 to the brief) | **CONFIRMED** | dblp record: *ICSE 2016: 464–475*, doi `10.1145/2884781.2884796` |
| 10 | Panko §4.1 (3.9% CER / 967 participants / 85 sheets at 94% / 60% detection / 9,120 Enron sheets / 20,277,835 formula cells) and Powell arXiv:0801.0715 (0.8–1.8% of formula cells, 50 sheets; follow-up n=25) | **CONFIRMED — verbatim** | `arxiv.org/pdf/1602.02601` and `arxiv.org/abs/0801.0715` |
| 11 | FLARE (EuSpRIG 2025) scores **NOT-FOUND** — "the EuSpRIG PDF returned HTTP 403" | **QUALIFIED — over-declared** | `arxiv.org/abs/2506.17330` is open access, 18 pp / 10 tables |
| 12 | `knowledgestack/excel-parser` MIT, 51★, and **not installable from PyPI** | **CONFIRMED — both halves** | GitHub API; `pypi.org/pypi/{excel-parser,excel_parser}/json` → 404, 404 |

### The four that matter, with the evidence

**#2 — the "absent arm" claim about SpreadsheetBench 2 is overstated, and the correct version is
sharper.** The lane writes that SB2 does not penalise a system that flags a non-existent problem. SB2's
own Table 3 caption says: *"Acc. reports the fraction of tasks where every cell in the output matches
the golden file."* Whole-output exact match **does** penalise spurious edits, and the paper documents
exactly that failure — Appendix D.4 describes an agent that *"expanded its edits beyond what the
instruction asked for, and the out-of-scope changes were not only unnecessary but harmful."* What is
genuinely absent is a **clean instance class**: Appendix B.4 states *"Each debugging instance contains
one or more injected errors drawn from this taxonomy."* There is no debugging task in SB2 whose correct
answer is "nothing is wrong". **Rewrite the claim as: SB2 contains no negative-control instance, so it
cannot measure the false-alarm rate at the verdict level — every one of its 100 debugging tasks has a
bug by construction.** That is a stronger and true statement, and it is the brief's actual point.

Second-order: SB2's debugging errors are **injected**, i.e. mutants. §5.6 of this lane quotes Schmitz &
Jannach criticising methods *"evaluated with mutations of correct spreadsheets"* — and then §5.7 holds
up SB2 as the lane's strongest new external evidence without noting that SB2's debugging arm is exactly
that. The two sections should be reconciled before either is cited.

Bonus: the lane's declared residue *"SpreadsheetBench 2 debugging-subset n: UNVERIFIED"* is
**resolvable and now resolved.** SB2 **Table 1** gives per-category counts: Financial Modeling 100,
**Debugging 100**, Template 97, Visualization 24, Overall 321. The n=100 inference was right. Also note
Visualization Acc. is a **VLM-judge rubric pass rate over n=24**, not a task accuracy — the lane's §5.7
table presents it in the same column as the exact-match figures without that flag.

**#4 — the "~92% engine agreement floor" rests on an artifact with no evidential standing.** The repo is
real, is Apache-2.0, has 2 stars, and its README numbers reproduce exactly as tabulated. But the GitHub
commit log shows **all 19 commits landed on a single day, 2026-06-12, between 07:03 and 10:31 UTC** —
the repo was created at 08:30 that morning and has not been touched since. Commits are co-authored by an
AI assistant (`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`). The results were *regraded
twice during that same session* as the vendor's own engine version moved (`witan version: api/v2.50.0`
→ `api/v2.49.0`; *"FUSE regrade @ 04a5971: 95.3% clean"*), and the top-scoring entrant is the repo
owner's own product, invoked through its public CLI. The lane already calls it promotional — that is
not strong enough. **A three-hour, unreplicated, self-graded vendor artifact cannot support a
quantitative floor that the design then requires every L5 predicate to carry in its FFR.** Either
measure the LibreOffice-vs-Excel disagreement rate independently, or state the floor as ASSERTED with
no denominator and stop attributing a number to it. (Minor: the lane's §2.5 table shows "—" for openpyxl
open/round-trip; the README actually reports 99.9%/99.9%.)

**#5 — FUSE is CC BY 4.0, not unencumbered.** The Zenodo deposit that the lane itself cites as the
location (`581678`) returns `"license": {"id": "cc-by-4.0"}`. The MSR-2015 paper's *"unencumbered by any
license agreements"* describes the provenance of the underlying Common Crawl content, not the terms of
the distributed corpus. CC BY 4.0 carries an attribution obligation. §10's instruction *"do not
redistribute EUSES or VEnron until resolved"* should extend to a positive statement for FUSE: it may be
redistributed, **with attribution**. Any L1-robustness result published off FUSE inherits that.

**#6 — CheckCell's licence is not missing; the search was.** `plasma-umass/DataDebug` declares **GPL-2.0**
in the repository metadata, 48★, last pushed 22 Dec 2015. This matters twice: it removes a line from the
declared residue, and it puts CheckCell in the *same copyleft category* as `pycel` and `formulas` — so
the asset register's "L6 dual — adopt" recommendation carries the same legal gate the lane correctly
applies elsewhere. It is also an Excel 2010/2013 COM add-in dormant for eleven years, so only the method
transfers. Note the lane's own working rule about positive controls: a licence that is declared in the
repo sidebar and returned by an unauthenticated API call is not a NOT-FOUND, it is a missed check —
which is the third instance in this lane of the failure mode it was written to expose.

### What survives unscathed

The evidential spine of §4 and §5.1 is **solid at primary source**. Every ExceLint figure the design
adopts — 64.1/62.1, 20.3/median 0.0, adjusted 63.7/19.6, 7-of-70, 33-of-70-flags-nothing with 22
genuinely empty, and the hypergeometric baseline construction — reproduces verbatim from the arXiv PDF,
including the two long quotations. **Design point #4 (adopt ExceLint's discipline and cite OOPSLA 2018
rather than claim novelty) is fully supported.** So is design point #5's foundation: Panko's Table 1/2
figures and Powell's 0.8–1.8% all read exactly as quoted, and CUSTODES is indeed ICSE 2016.
SpreadsheetBench 2 is a real, current, well-constructed paper and its headline numbers are exactly as
reported — the lane's most load-bearing new citation holds.

### Residue this pass could not close

- **The FUSE/ENRON *content* counts** (249,376; 15,770) — Zenodo confirms 249,376 and the 2,127,284 /
  26.83 bn / 1.9 PB figures verbatim; the ENRON 15,770 figure is **not** stated on the figshare record
  and remains SECONDARY, as the lane says.
- **The Powell et al. DSS 2008 quotations** (§4.3) — the article is behind Elsevier. I verified the
  companion arXiv paper's 0.8–1.8% figure at source but **did not independently re-open the DSS PDF**;
  the three long quotations there remain on the lane's warrant, not mine. **UNVERIFIABLE in this pass.**
- **Schmitz & Jannach's 28 errors, Melford's figures, CACheck's 1,586 cell arrays, CUSTODES' F=0.72** —
  not re-checked. Budget went to the claims with the largest design blast radius.
- **My web-search budget was exhausted mid-pass**, so a small number of secondary cross-checks (the MSR
  FUSE paper's exact licence sentence) were resolved from the deposit record rather than the paper.

