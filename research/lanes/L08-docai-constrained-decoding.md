# L08 — The Extraction Stack

**Lane:** document AI, table benchmarks, regulation-text structuring, constrained decoding.
**Date:** 10 August 2026. **Author:** research lane 08.

**Warrant key used throughout, per program rules:**
- **VERIFIED-AT-SOURCE** — I opened the primary artifact (repo file, licence text, dataset file, live
  API response, the workbook on disk) and read the value off it.
- **SECONDARY** — a credible source describes it; I did not open the primary.
- **UNVERIFIED** — could not confirm. Stated as such, not smoothed over.

**What I actually opened, so the coverage denominator is declared:**
the OmniDocBench `README.md` at `main` (2,400 lines, parsed programmatically, not by eye);
`allenai/olmocr` `olmocr/bench/tests.py`; the HuggingFace dataset file
`allenai/olmOCR-bench :: bench_data/table_tests.jsonl` (1,022 records); `docling-core`
`types/doc/common/reference.py`, `types/doc/base.py`, `types/doc/items/table/table_data.py`;
`opendatalab/MinerU` `LICENSE.md`; `datalab-to/marker` `LICENSE`; the GitHub REST API for 23 repos;
the live IFSCA register JSON API (2,005 records + 228 detail records fetched today); and all nine
`.xlsx` workbooks in `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/`.

**What I did NOT open, and therefore do not assert:** the OmniDocBench CVPR paper PDF; the
"Let Me Speak Freely" PDF body (only the ACL Anthology abstract page); the olmOCR 2 paper body
(the arXiv HTML summary I obtained conflicts with the repo, see §D.4 — I report the conflict rather
than pick a side); LlamaParse's Terms of Service.

---

## §0 — THE HEADLINE, IN ONE PARAGRAPH

The brief treats "document AI" as a single dependency of L2. It is not. There are **three source
classes with three genuinely different extraction stacks**, and the most important of them —
the filing itself — **needs no document AI at all and no model at all**. I verified this: all nine
prescribed workbooks contain **zero embedded images** (`xl/media/` empty, 0 bytes, 9 of 9), so every
number is native. Document AI belongs only to the regulation-and-circular path. Meanwhile the two
places where this program will actually lose data are not the parser at all — they are **a
shared-formula encoding in OOXML that hides 55.2% of the workbooks' formula-bearing cells from a
naive reader**, and **a regulator's register in which 38.2% of live registration numbers fail the
regex any competent engineer would write**. Both are measured below, first-hand, with denominators.

---

## §A — SOURCE CLASS 1: THE XLSX FILING (the primary artifact)

### A.1 Verified: no OCR is needed, and no model is needed

Measured by me today over all nine workbooks in `scratchpad-oracle/`, by reading the OOXML zip
directly:

| Workbook | sheets | valued cells | native numeric | `xl/media/` entries | media bytes |
|---|---:|---:|---:|---:|---:|
| `Reporting_Format_for_Fund_Management_Entities_02012026…` | 10 | 3,740 | 2,438 | **0** | **0** |
| `Updated___Quarterly_Reporting_Format_for_Capital_Market_Interm…` | 18 | 2,404 | 1,187 | **0** | **0** |
| `AL_monthly_report_updated_final_20260717_0257` | 4 | 1,292 | 663 | **0** | **0** |
| `Draft_ACAC_Format_20260605_0631` | 13 | 1,149 | 519 | **0** | **0** |
| `ALR_V2_3_20250808_1024` | 9 | 1,057 | 287 | **0** | **0** |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved…` | 9 | 479 | 240 | **0** | **0** |
| `IBU_Operations_Report_V2_3_20250808_1033` | 8 | 308 | 120 | **0** | **0** |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030` | 3 | 262 | 115 | **0** | **0** |
| `ITFS_Monthly_report201220241626` | 2 | 220 | 112 | **0** | **0** |

**VERIFIED-AT-SOURCE.** Denominator: 9 of 9 workbooks, 10,911 valued cells total.
"Valued cells" = cells containing a `<v>` or `<is>` element. "Native numeric" = valued cells with no
`t="s"|"str"|"inlineStr"` attribute and no formula.

**Consequence:** every OmniDocBench number, every TEDS score, every VLM parameter count in §D is
**irrelevant to the artifact the product is actually about.** They matter only for §B. The brief's
L2 bullet ("Document AI for unstructured sources: Docling / Marker / MinerU") should be explicitly
scoped to the regulation path, or a reader will conclude the filing pipeline has a model in it.

**Reconciliation with §4.3 of the brief:** the brief reports 6,757 cells for the FME workbook. I
reproduce **6,757 exactly** when counting all `<c>` elements. My 3,740 counts only cells with a
value. Same instrument, different denominator — **no disagreement**, but the two numbers must never
be quoted against each other.

### A.2 The finding that matters: 825 formula-bearing cells are invisible to a text-only reader

OOXML has two ways to store a formula. A cell may carry its own text —
`<f>SUM(C3:N3)</f>` — or it may be a **shared-formula dependent**: one *master* cell holds
`<f t="shared" ref="O3:O12" si="4">SUM(C3:N3)</f>` and every other cell in the range holds
`<f t="shared" si="4"/>` — **an empty, self-closing element with no formula text at all.**

The brief's §4.3 counts formulas by their text. That is the correct count *of formula texts*. It is
**not** the count of cells that compute something. Measured by me today:

| | FME workbook | all 9 workbooks |
|---|---:|---:|
| cells with formula **text** (what §4.3 counted) | **294** | **670** |
| shared-formula **dependents** (no text, inherit) | **211** | **825** |
| **total formula-bearing cells** | **505** | **1,495** |
| fraction invisible to a text-only reader | **41.8%** | **55.2%** |

**VERIFIED-AT-SOURCE.** The 294 reproduces the brief's number exactly, which is what makes the
comparison trustworthy: same file, same parser, one extra element form.

Per workbook, the undercount is wildly uneven — which means it cannot be corrected by a constant:

| Workbook | f-text | shared deps | total | undercount |
|---|---:|---:|---:|---:|
| `Draft_ACAC_Format` | 9 | 103 | 112 | **92.0%** |
| `AL_monthly_report` | 49 | 112 | 161 | **69.6%** |
| `ALR_V2_3` | 246 | 399 | 645 | **61.9%** |
| `Reporting_Format_for_FMEs` | 294 | 211 | 505 | **41.8%** |
| `ITFS_Monthly_report` | 32 | 0 | 32 | 0.0% |
| `Updated___Quarterly…CMI` | 33 | 0 | 33 | 0.0% |
| `IBU_Operations_Report` | 7 | 0 | 7 | 0.0% |
| `EDR_1` | 0 | 0 | 0 | — |
| `IFSCA_Annual_Reporting_Format` | 0 | 0 | 0 | — |

Note the brief's line *"Draft ACAC 9/0"*. True figure: **9 formula texts, 103 hidden dependents,
112 formula-bearing cells.** The workbook that looked emptiest is 92% hidden.

### A.3 What the hidden cells are — and why this moves a load-bearing number

I resolved each dependent to its master's formula text by `si` index and classified:

| Class | with text | inherited | **total** |
|---|---:|---:|---:|
| cross-sheet / cell carry | 192 | 31 | 223 |
| **SUM identity — CHECKABLE** | 35 | **100** | **135** |
| IFERROR wrapper | 50 | 80 | 130 |
| IF conditional carry | 14 | 0 | 14 |
| **COUNTIF tally — CHECKABLE** | 3 | 0 | **3** |

> **The brief states: "38 of 294 (13%) express a checkable relationship. 181 (62%) copy a value."**
> **Corrected, same file, same classification rule: 138 of 505 = 27.3% express a checkable
> relationship.** VERIFIED-AT-SOURCE.

The checkable fraction is **more than double** what the brief reports. The rhetorical point in §4.3 —
*"the workbook moves numbers between sheets and that motion is counted as validation"* — survives
(carries are still the largest single class at 223/505 = 44.2%), but the specific ratio does not.
And since L3's stated criterion source is *"statutory text plus the template's own 294 native
formulas"*, **L3's criterion source is 505 formulas, of which 138 are already executable checks
someone else authored.** That is a materially larger free starting inventory for the predicate
registry.

### A.4 This is the same failure as §4.4 #2, for the third time

The brief's §4.4 documents a regex `<f[ >][^>]*>` that could not match `<f>SUM(...)</f>`, and calls
it a silent false negative. The corrected regex still cannot match `<f t="shared" si="4"/>`
correctly — it matches the element but finds no text and the cell is dropped. **Same instrument,
same class of defect, one layer deeper.** This is not a criticism of the operator; it is the single
best available demonstration of the product thesis, it is *deterministic*, and it happened twice on
the same file. **It belongs in the pitch alongside the two existing examples.**

### A.5 The fix is one line, and it is already installed

**`openpyxl` 3.1.5 resolves shared formulas correctly and transparently.** Verified on the FME
workbook: reading dependent cells returns the *translated* formula, not `None` and not the master's
unshifted text.

```
sheet index 2:  O3 -> '=SUM(C3:N3)'      O4 -> '=SUM(C4:N4)'      O5 -> '=SUM(C5:N5)'
                E76 -> '=IFERROR(D76/$O$3,0)'   E77 -> '=IFERROR(D77/$O$3,0)'
                G41 -> '=SUM(C41:F41)'   G42 -> '=SUM(C42:F42)'
```

VERIFIED-AT-SOURCE, `/Users/abishaikc/Gift/.venv/bin/python`, openpyxl 3.1.5. Note `O4` and `E77`
are **dependents**, and openpyxl returned the correctly row-shifted formula for each. Row-shifting
is exactly what a hand-rolled XML reader gets wrong even when it notices the dependent exists.

**Caveat, and it is important for L1:** openpyxl emits
`UserWarning: Data Validation extension is not supported and will be removed`
when loading this workbook. The brief's §4.3 counts **35 data validations, only 3 list-type with a
named vocabulary**, and one of the 17 decidable predicates is *"dropdown ∈ vocabulary."*
**openpyxl is not a safe reader for the validation layer** — it drops an extension it does not
model. L1 must read `<dataValidation>` and the `x14:dataValidations` extension block **from the raw
XML**, and use openpyxl only for formulas and values.

### A.6 RECOMMENDED STACK — xlsx filing

| Job | Tool | Why it beats the alternative |
|---|---|---|
| formulas (incl. shared) + values + merged ranges | **openpyxl 3.1.5** (MIT) | Only reader tested here that row-shifts shared formulas. A regex over OOXML loses 41.8–92.0% of formula cells per workbook, silently. |
| data validations, protection, `x14` extensions | **raw `zipfile` + `lxml` over `xl/worksheets/*.xml`** | openpyxl *warns and discards* the DV extension. The vocabulary predicate depends on it. |
| content addressing | `sha256` of the zip **and** of each `sheetN.xml` | Per-sheet hashes let a re-derivation say *which* sheet changed, not just that the file did. |
| **not used** | pandas / `read_excel` | Collapses merged headers and discards formulas entirely — it returns the *cached values*, i.e. exactly the numbers under test. |
| **not used** | any document-AI parser, any VLM | Zero images in 9/9 workbooks; introducing a model here converts a deterministic layer into a model-bearing one for no gain. |

**Where it stops.** openpyxl does not evaluate formulas — it returns text or the last cached value.
So L5 cannot ask "does this SUM come out right?" without an evaluator. For the 138 checkable
relations, the honest options are (a) re-implement SUM/COUNTIF/IFERROR over the extracted grid
(trivial, ~50 lines, and deterministic), or (b) `formulas` / `pycel` (both PyPI, licences
**UNVERIFIED** — I did not open them). Option (a) is preferable because the reimplementation *is*
the predicate, and it can carry a mutation score. Option (b) imports someone else's semantics with
an unmeasured error rate — which L4 would have to reject on its own rules.

---

## §B — SOURCE CLASS 2: THE REGULATION AND CIRCULAR PDFs

This is the only class where document AI is warranted: the 102-page FM Regulations and 399
circulars, of which the brief measured **10 unreadable by `pdftotext -layout` because they are
scanned images**.

### B.1 The parser field, with primary-source licence and activity

All rows below: **VERIFIED-AT-SOURCE** via the GitHub REST API (`repos/{owner}/{repo}`) on
10 Aug 2026, except where noted. `pushed` is the last push to the default branch — the honest
activity signal.

| Parser | Licence | ★ | last push | Size / cost | Citation anchors (page + bbox)? |
|---|---|---:|---|---|---|
| **Docling** (IBM) `docling-project/docling` | **MIT** | 64,531 | 2026-08-10 | CPU-viable pipeline; VLM optional | **YES — typed `ProvenanceItem` + per-cell `TableCell.bbox`. Best in field.** |
| **MinerU** `opendatalab/MinerU` | **NOASSERTION** — Apache-2.0 **+ additional terms** (see B.2) | 77,270 | 2026-08-08 | MinerU2.5 **1.2B** | YES — `[xmin,ymin,xmax,ymax]`, normalised to [0,1] (SECONDARY) |
| **Marker** `datalab-to/marker` | **Apache-2.0** (LICENSE file read; plain Apache, no rider found) | 38,632 | 2026-08-07 | pipeline, GPU-preferred | Partial (JSON blocks w/ polygons) — **UNVERIFIED** at schema level |
| **PaddleOCR / PaddleOCR-VL** `PaddlePaddle/PaddleOCR` | **Apache-2.0** | 87,345 | 2026-07-22 | **0.9B** (ERNIE-4.5-0.3B LM) | YES — layout detection is native; v1.5+ moved to instance segmentation (SECONDARY) |
| **Surya** `datalab-to/surya` | **Apache-2.0** | 21,242 | 2026-07-23 | OCR + layout + table, 90+ langs | YES — line/layout bboxes |
| **unstructured** `Unstructured-IO/unstructured` | **Apache-2.0** | 15,290 | 2026-08-04 | ETL wrapper, delegates OCR | Coordinates on elements; **UNVERIFIED** whether per-table-cell |
| **olmOCR** (AI2) `allenai/olmocr` | **Apache-2.0** (code, model, and training mixes) | 19,288 | **2026-03-25** (≈4.5 mo stale) | **7B** VLM | Linearises to Markdown — **anchors are not the output contract** |
| **dots.ocr** `studio-dots-ai/dots.ocr` (**moved** from `rednote-hilab`) | **MIT** | 9,065 | **2026-03-24** | **3B** | YES (layout+content) — **UNVERIFIED** |
| **Nougat** (Meta) `facebookresearch/nougat` | MIT (repo) | 10,056 | **2025-02-21 — ~18 months stale** | 0.25/0.35B | No page/bbox contract; academic-PDF-shaped |
| **LlamaParse** `run-llama/llama_cloud_services` | client MIT; **service is proprietary SaaS** | 4,258 | 2026-05-18 | 1–90 credits/page, ~$0.001/credit (SECONDARY) | Proprietary output schema |

**Do not use** for this program: **Nougat** (18 months without a push, and it is tuned for academic
papers with LaTeX maths, not statutory prose); **LlamaParse** (a regulator-facing verification
product cannot send the corpus to a third-party SaaS, and self-host is enterprise-tier —
SECONDARY); **olmOCR** as a *parser* (its value here is its benchmark, §D.4, not its output).

### B.2 The MinerU licence rider — read it before adopting

**VERIFIED-AT-SOURCE**, `LICENSE.md` on `master`. GitHub reports `NOASSERTION`; the actual text is:

> "MinerU is licensed under Apache License 2.0 and is subject to the additional terms below."
> **§1** commercial use is free unless MAU > 100 million **or** monthly revenue > USD 20 million;
> **§2** "If you provide online services to third parties based on MinerU, you must clearly and
> prominently indicate … that MinerU is used."; **§3** breach terminates the licence automatically.

For this program §1 is irrelevant and **§2 is a live obligation** — a hosted verification product
built on MinerU must display attribution. Cheap, but it is a term, and "Apache-2.0" in a slide would
be wrong. Docling (MIT) and PaddleOCR (Apache-2.0) carry no such rider.

### B.3 Docling's provenance schema — this is the one to standardise on

**VERIFIED-AT-SOURCE**, `docling-core` @ `main`:

`docling_core/types/doc/common/reference.py`:
```python
class ProvenanceItem(BaseModel):
    """Provenance information for elements extracted from a textual document.

    A `ProvenanceItem` object acts as a lightweight pointer back into the original
    document for an extracted element. It applies to documents with an explicit
    or implicit layout, such as PDF, HTML, docx, or pptx.
    """
    page_no: Annotated[int, Field(description="Page number")]
    bbox: Annotated[BoundingBox, Field(description="Bounding box")]
    charspan: CharSpan
```

`docling_core/types/doc/base.py`:
```python
class CoordOrigin(str, Enum):
    TOPLEFT = "TOPLEFT"
    BOTTOMLEFT = "BOTTOMLEFT"

class BoundingBox(BaseModel):
    l: float  # left
    t: float  # top
    r: float  # right
    b: float  # bottom
    coord_origin: CoordOrigin = CoordOrigin.TOPLEFT
```

`docling_core/types/doc/items/table/table_data.py`:
```python
class TableCell(BaseModel):
    bbox: Optional[BoundingBox] = None
    row_span: int = 1
    col_span: int = 1
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    text: str
    column_header: bool = False
    row_header: bool = False
    row_section: bool = False
    fillable: bool = False
```

Three things this buys that no competitor publishes as a typed contract:
1. **`charspan` alongside `bbox`** — a *textual* offset as well as a *visual* box. A citation that
   survives re-rendering.
2. **Per-cell `bbox` plus grid offsets and spans** — so a numeric cell in a regulation's schedule
   gets its own pointer, not just its table's.
3. **An explicit `coord_origin` enum.** PDF-native coordinates are bottom-left; almost every
   rendering stack is top-left. Every silent off-by-a-flip bug in provenance rendering lives here,
   and Docling makes the choice explicit and defaults it to `TOPLEFT`.

**Where it stops.** `TableCell.bbox` is `Optional[…] = None`. Docling *may* return a cell with no
box. L5's weakest-input rule must treat `bbox is None` as `UNCHECKED(source unreadable)` for any
predicate whose failure message points at that cell — not as a pass. Separately, the brief is right
that Docling's confidence is a small set of heuristic page-level scores, i.e. **a page ordinal, not
a per-value probability**; it must never be fed to L2's conformal step as if it were a score.

### B.4 RECOMMENDED STACK — regulation PDF

**Docling (MIT) as the default, with a scanned-page fallback to PaddleOCR-VL (Apache-2.0).**

- **Beats MinerU** on licence cleanliness (MIT vs Apache + attribution rider) and on the only axis
  the brief says matters more than accuracy — *anchors*: Docling publishes a typed, versioned,
  per-cell provenance schema; MinerU publishes normalised boxes without an equivalent typed
  contract for cell-level pointers (my check: SECONDARY, not VERIFIED).
- **Beats Marker/Surya** on the same axis, and Marker is the **worst table row on OmniDocBench
  v1.6_full** (TEDS 65.77 — §D.1).
- **Beats olmOCR/Nougat** on activity (Docling pushed the day of writing; olmOCR 4.5 months, Nougat
  18 months) and because both linearise to Markdown, which *destroys* the anchor.
- **PaddleOCR-VL is the fallback, not the default**, because it is genuinely better at the parse
  (rank 1 on OmniDocBench v1.6_full: Overall 96.34, TEDS 94.76 at **0.9B**) but it is a VLM — a
  model — and this program's rule is that models go only where generation is hard. For the ~10
  scanned circulars out of 399 (2.5%), generation *is* hard and there is no alternative. For the
  389 native ones, Docling's deterministic path is preferable and its output is checkable against
  the operator's existing `pdftotext -layout` extraction as a cross-check.

**Where it stops.** Docling gives you *a faithful structured document*. It does not give you a
*clause*. That is §E.

---

## §C — SOURCE CLASS 3: THE LIVE REGISTER

The brief lists two of the 17 decidable predicates as *"registration number resolves in live
register"* and *"scheme number resolves."* Nobody had checked whether the register is machine-
readable. I checked. It is — and what came back is the most useful thing in this lane.

### C.1 The register is a documented JSON API (undocumented publicly, but real)

**VERIFIED-AT-SOURCE**, fetched today. `https://ifsca.gov.in/DirectoryList` serves an HTML shell
whose table has **headers and zero data rows**; the body is client-rendered (no `__VIEWSTATE`; a
DataTables instance in `/CustomJS/DirectoryList.js`). A `curl` of the page gets you nothing — the
same trap the operator hit on `giftifih.getkruu.com/apply`. The real endpoints, read out of that JS:

```
GET https://ifsca.gov.in/DirectoryList/DirectoryGetList
    ?draw=1&start=0&length=2100&PageNumber=1&PageSize=2100
    &SearchText=&SearchName=&Id=0&ParentTypeId=0
    &EntityFilter=&CategoryFilter=0&SubCategoryFilter=0
  → 200, application/json, 3,393,650 bytes, 2,005 records in one call.

GET https://ifsca.gov.in/DirectoryList/DirectoryDetailGet?EncryptedId=<id>
  → 200, application/json, one entity's registration detail.
```

**Trap, and it is exactly this program's subject matter.** The list payload contains **both**
`EncryptDId` and `EncryptedId`. `EncryptDId` is **`None` in 2,005 of 2,005 records**; `EncryptedId`
is populated in **2,005 of 2,005**. A reader that picks the first plausible field gets a 302
redirect and no data, on every record, forever. I hit it. Likewise `RegistrationNumber`,
`DateOfRegistration`, `ValidityFromDate`, `ValidityToDate` are **present in the list schema and
`None` in 650 of 650 fund rows** — the fields exist and are always empty. **The list endpoint tells
you who exists; only the detail endpoint tells you their registration number.**

### C.2 The register population, measured today

**VERIFIED-AT-SOURCE.** `recordsTotal` = **2,005** entities. Top parent categories:

| Parent category | n |
|---|---:|
| Fund Management | **650** |
| Metals & Commodities entities | 391 |
| Qualified Jewellers | 261 |
| Capital Market Intermediaries | 223 |
| Finance Company | 101 |
| TAS Service Provider | 82 |
| Fintech Sandbox Entities | 63 |
| Banking | 45 |
| Ancillary Service Provider | 43 |
| IFSC Insurance Office (IIO) | 39 |
| Surrendered/Cancelled CoRs | 37 |

Within `Fund Management` (650): Category III AIF 232, **Registered FME (Non-Retail) 194**,
Category II AIF 121, Portfolio Management Services 31, Category I AIF 23,
**Registered FME (Retail) 22**, Retail Scheme 13, **Authorised FME 13**, Angel Fund 1.

> **FMEs = 194 + 22 + 13 = 229 live** (parent = Fund Management).
> **Schemes = 232 + 121 + 23 + 13 + 1 = 390 live.**
> The brief states **217 FMEs, 360 schemes**. **QUALIFIED, not refuted** — I cannot see the brief's
> counting rule or as-of date, and a further **8 FME-subcategory rows sit under
> `Surrendered/Cancelled CoRs`** (237 FME rows across all parents), so a defensible count exists
> anywhere in 229–237 depending on whether surrendered entities are included. **Whichever number
> the pitch uses must state the rule and the date**, because the register moves.

### C.3 The registration-number finding — a 38.2% false-failure rate, measured

I fetched the detail record for **228 of the 229 live FMEs** (1 fetch error; coverage 99.6%).
**228 of 228 have a non-empty RegistrationNumber. 228 of 228 have a DateOfRegistration, all in
`DD/MM/YYYY`.** So the predicate is *satisfiable*. But:

| Format | n | share of 228 |
|---|---:|---:|
| Legacy `IFSCA/FME/<I\|II\|III>/<FY>/<n>` — e.g. `IFSCA/FME/II/2023-24/026` | 141 | **61.8%** |
| New `FDM<YYYY><AAA><NNNN>` — e.g. `FDM2026FMR1118` | 84 | **36.8%** |
| Neither | 3 | 1.3% |

**Two incompatible identifier schemes are live in the same register on the same day.** And the
three stragglers are worth the whole exercise — I inspected them at codepoint level:

1. `IFSCA/FME/**IV**/2023-24/033` — ASK Investment Managers Limited (IFSC Branch). Roman numeral
   **IV**, when the FME categories are I, II and III. Either a register data-entry defect or a
   category the schema does not know about.
2. `IFSCA/FME/III/2022‑23/037` — MARCELLUS INVESTMENT MANAGERS PRIVATE LIMITED. The hyphen is
   **`U+2011 NON-BREAKING HYPHEN`**, not `U+002D`. **VERIFIED at codepoint level.** A homoglyph.
   Visually identical, byte-wise different, invisible in any log or screenshot.
3. `100` — Teak Blossom C FME 2023 IFSC Private Limited. A bare integer.

Even the "new format" is not clean: the 3-letter codes are `FNR` 70, `FMR` 9, `FUM` 4, `FIF` 1 —
and **`FNR` appears once on a `Registered FME (Retail)` entity** (1 of 70), while legacy roman `I`
(otherwise = Authorised FME, 8 of 9) appears once on a Non-Retail FME. **The code does not reliably
determine the category.**

> **The measured consequence.** The predicate any engineer would write after looking at five
> examples —
> `^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$` —
> **fires on 87 of 228 currently-registered FMEs: a 38.2% false-failure rate.** VERIFIED-AT-SOURCE,
> denominator 228 live FMEs, 10 Aug 2026.

This is a *deterministic* predicate, written from real data, that is confidently and catastrophically
wrong — and nothing in its output would say so. It is the **best single artifact this program has**
for the pitch, better than the two in §4.4, because the false failures are *named live regulated
entities* and the reviewer can look them up. It is also a direct, unarguable validation of L4 test 3
(FFR on a clean corpus): **the clean corpus here is the regulator's own register**, no synthesis
required, so the caveat in risk #2 ("a synthetic clean corpus is not a measurement of real filings")
**does not apply to this predicate class.** That is a real, unforced win.

### C.4 RECOMMENDED STACK — live register

| Job | Choice | Why |
|---|---|---|
| enumerate | one `GET DirectoryGetList` with `PageSize=2100` | Whole register, 2,005 records, one request, ~3.4 MB. No scraping, no browser. |
| resolve identity | `GET DirectoryDetailGet?EncryptedId=…` per entity | The only source of `RegistrationNumber`. 229 calls for FMEs; ~2,005 for the full register. Cache by content hash. |
| **never** | a format regex on the registration number | Measured 38.2% FFR (§C.3). |
| the predicate | **set membership against a snapshotted register**, normalised: NFKC + map `U+2011→U+002D` + strip whitespace, compared case-insensitively | Handles the homoglyph and the two schemes without asserting a grammar the regulator does not follow. |
| provenance | store the register snapshot's sha256 + fetch timestamp + endpoint + `EncryptedId` | The register mutates. A verdict that cites "the register" without a snapshot hash is not reproducible, and L7 cannot sign it. |
| **required declaration** | any FME whose number matches neither scheme → `UNCHECKED(rule ambiguous)` | Not FAIL. The entity is validly registered; our grammar is incomplete. This is precisely the distinction the product exists to make. |

**Where it stops.** No `robots.txt` / rate-limit / terms-of-use review was performed — I made 2,235
polite GETs at ~0.06–0.25 s spacing with no failures other than one timeout. **Before any scheduled
or productionised polling, someone must read IFSCA's terms of use.** Flagging this rather than
assuming it. Also **UNVERIFIED**: whether scheme-level records expose a scheme number in the detail
endpoint (I sampled FMEs only).

---

## §D — BENCHMARKS

### D.1 The brief's TEDS claim: **CONFIRMED, exactly**

The brief states: *"TEDS-S exceeds TEDS on all 32 leaderboard rows."*

Source: `opendatalab/OmniDocBench` `README.md` @ `main`, table
**"Comprehensive evaluation of document parsing on OmniDocBench (v1.6_full)"**. Repo **Apache-2.0**,
1,961★, pushed 2026-07-27. Dataset itself: **research-only, not for commercial use** (SECONDARY —
per the repo's dataset note; I did not open a separate dataset licence file). Benchmark size stated
in the README: **1,651 PDF pages, 10 document types, 5 layout types, 5 language types**.

I parsed the table programmatically rather than reading it, because a WebFetch summariser told me
this table had **24 rows** and it has 32 — the exact failure mode this program is about.

> **Result: 32 rows. 32 of 32 have TEDS-S > TEDS. Zero exceptions.**
> Gap (TEDS-S − TEDS): **min +2.22, median +3.56, mean +3.70, max +7.47.**
> **VERIFIED-AT-SOURCE.**

Extremes, which are the interesting part:

| Model | Type | Size | TEDS | TEDS-S | gap |
|---|---|---|---:|---:|---:|
| Marker | Pipeline Tools | – | 65.77 | 73.24 | **+7.47** |
| MinerU-Pipeline | Pipeline Tools | – | 81.88 | 88.68 | +6.80 |
| InternVL3.5-241B | General VLM | 241B | 74.35 | 79.78 | +5.43 |
| GPT-5.2 | General VLM | – | 82.95 | 87.93 | +4.98 |
| Gemini 3 Flash | General VLM | – | 89.29 | 93.51 | +4.22 |
| olmOCR | Specialized VLM | 7B | 83.00 | 87.17 | +4.17 |
| dots.ocr | Specialized VLM | 3B | 87.18 | 90.58 | +3.40 |
| MinerU-2.5 | Specialized VLM | 1.2B | 87.88 | 91.47 | +3.59 |
| PaddleOCR-VL-1.6 | Specialized VLM | **0.9B** | **94.76** | **97.10** | +2.34 |
| HunyuanOCR | Specialized VLM | 1B | 91.01 | 93.23 | **+2.22** |

**What the gap actually means, and why the brief's use of it is right.** TEDS-S is structure-only;
TEDS adds cell *content*. The gap is therefore **the content penalty** — everything the model got
wrong *inside* the cells, once the grid was right. It is positive on every row, which is the brief's
point: **structure is easier than content, and the headline table metric is inflated relative to the
thing we care about.** A 0.9B model already reads the grid at 97.10.

**The sharper version of the argument, which the brief does not make and should.** TEDS compares
cell content by *normalised string edit distance*, not numeric equality (SECONDARY — the TEDS
definition is in Zhong et al., arXiv:1911.10683, whose PDF body I could not read; the OmniDocBench
README credits `ibm-aur-nlp/PubTabNet` for the metric implementation). If that is right — and it is
the standard understanding — then **`1,234,567` misread as `1,234,507` is one character in nine and
scores ≈0.89 content similarity while being a materially false financial statement.** A 3-point TEDS
gap is not "3% of cells wrong"; it is compatible with *most* numeric cells being subtly wrong. **We
should not quote a TEDS number in support of extraction quality at all.** The correct statement is
that TEDS is the wrong instrument for our error class, not that our parser scores well on it.

### D.2 2026 entrants (from the same verified table)

The field moved a long way past the brief's "Docling / Marker / MinerU / Surya / unstructured" list.
Present on v1.6_full and absent from the brief: **PaddleOCR-VL 1.5/1.6 (0.9B), GLM-OCR (0.9B),
Youtu-Parsing (2.5B), Qianfan-OCR (4B), Logics-Parsing-v2 (4B), ABot-OCR (2B), FireRed-OCR (2B),
OpenDoc-0.1B, DeepSeek-OCR 2 (3B), HunyuanOCR (1B), Dolphin-v2 (3B), OCRVerse (4B),
MonkeyOCR-pro-3B, Ovis2.6-30B-A3B, Gemini 3 Pro/Flash, GPT-5.2, Kimi K2.5 (1T),
Qwen3-VL-235B.** VERIFIED-AT-SOURCE (leaderboard rows).

The structural fact worth carrying into the design: **the top of the leaderboard is a 0.9B
specialised model that beats a 1T general model and GPT-5.2 by ~10 points overall.** Document
parsing does not need a frontier model. Any architecture slide that implies "we call a big VLM to
read the PDF" is both wrong and expensive.

### D.3 "OmniDocBench is saturated"

LlamaIndex published a piece titled *"OmniDocBench is Saturated, What's Next for OCR Benchmarks?"*
(`llamaindex.ai/blog/omnidocbench-is-saturated-…`). **SECONDARY — title and existence confirmed
from search results; I did not open it.** Consistent with the leaderboard (top 12 models within
~3 points of each other on Overall). Treat as directional only.

### D.4 **Does any published document-AI benchmark bound per-cell numeric error?**

The brief asserts: *"No published metric bounds per-cell numeric error."*
**This is REFUTED as literally stated, and the correction makes our position stronger, not weaker.**

**Positive control, declared.** I did not search a search box and report an absence. I downloaded and
parsed the actual test file — `allenai/olmOCR-bench :: bench_data/table_tests.jsonl`,
1,022 records — and I read the executing code, `allenai/olmocr :: olmocr/bench/tests.py`.

**What olmOCR-Bench does.** Its stated design principle, from `olmocr/bench/README.md`
(VERIFIED-AT-SOURCE):

> "We stay away from soft metrics like edit distance comparisons, because they may assign lower
> scores for parses of the document that differ from the reference, but may in fact still be
> correct."

Its `TableTest` (VERIFIED-AT-SOURCE, `tests.py` L342+):

```python
class TableTest(BasePDFTest):
    """Test to verify certain properties of a table are held, namely that some
    cells appear relative to other cells correctly"""
    cell: str            # target cell, must exist somewhere in the table
    up: str = ""         # cell immediately above has this string
    down: str = ""
    left: str = ""
    right: str = ""
    top_heading: str = ""    # column heading
    left_heading: str = ""   # row heading
```
```python
threshold = 1.0 - (self.max_diffs / (len(self.cell) if len(self.cell) > 0 else 1))
threshold = max(0.5, threshold)
...
similarity = fuzz.ratio(self.cell, normalize_text(cell_content)) / 100.0
if similarity >= threshold: matches.append(rowcol)
```
with `max_diffs: int = 0` as the **class default** (`BasePDFTest`, L100).

**Measured over the actual 1,022 table tests:**

| Quantity | Value |
|---|---|
| table tests in `table_tests.jsonl` | **1,022** (1,020 `table` + 2 `baseline`) |
| distinct (pdf, page) pairs | **188** |
| tests with `max_diffs = 0` → **exact** string match required | **920 / 1,022 = 90.0%** |
| tests with `max_diffs ≥ 1` → fuzzy | 101 / 1,022 (48×1, 44×2, 5×3, 3×4, 1×5) |
| **target cells that are purely numeric** (e.g. `0.569`, `4.11`, `23.6%`, `2.069`) | **386 / 1,022 = 37.8%** |
| dataset licence | **ODC-BY** (VERIFIED via HF API `cardData.license`) |

A real record:
```json
{"pdf":"tables/b5c5b8661b5a272e7a175cdb20d49e67ba0d_pg4.pdf","page":1,
 "id":"...pg4_table_02","type":"table","max_diffs":0,"checked":"verified",
 "cell":"0.569","left_heading":"BO",
 "url":"http://www.aensiweb.com/old/jasa/rjfh/2014/995-1001.pdf"}
```

> **So: a published document-AI benchmark DOES assert exact per-cell values, including numeric ones
> — 920 of 1,022 tests at exact match, 386 of 1,022 on purely numeric cells.**
> **The brief's sentence must be withdrawn as written.**

**The defensible restatement, which is what we should actually say:**

> *No published document-AI benchmark yields a **bound on per-cell numeric error for a new,
> unseen document**. olmOCR-Bench comes closest and is the right prior art to cite: it replaces
> similarity scores with deterministic unit tests, 90% of them exact-match, 38% of them on numeric
> cells. What it produces is a **pass rate over a fixed 1,022-test suite on 188 pages** — a property
> of the suite, not a calibrated per-value error rate that transfers to our filing. Nothing in
> "MinerU 2.5.4 scores 84.9 on Tables" tells you the probability that **this** cell in **this**
> workbook is wrong.*

That is a stronger claim than the brief's, because it survives the obvious rebuttal ("what about
olmOCR-Bench?") instead of being killed by it.

**Two further qualifications, both verified.** (i) Even the exact tests are *string* equality after
`normalize_text`, which strips markdown emphasis and `<br>` but does **not** normalise number
formatting — so `1,000` vs `1000` **fails** while being numerically identical, and the metric has
no concept of tolerance in either direction. (ii) The 101 fuzzy tests use `fuzz.ratio` with a
**floor of 0.5**, so on those a wrong digit can pass.

**Also relevant, lower warrant:**
- **DocILE** (`rossumai/docile`, KILE + LIR; 6,680 annotated + 100k synthetic business documents)
  matches a predicted field to ground truth by **field type + bounding-box overlap with OCR words**,
  scoring AP/F1/precision/recall micro-averaged over fields — i.e. *field-level* localisation and
  extraction, closer to our unit than TEDS. **SECONDARY** (I read the search-result description and
  the repo landing page, not the paper's metric section).
- **GriTS** (Smock et al., Microsoft Table Transformer) scores topology, **content** and
  localisation on a grid. **SECONDARY.** Still a similarity, not a bound.
- **FinTabNet** — 113K financial tables from S&P 500 annual reports, cell-level annotations,
  evaluated with **TEDS**. **SECONDARY.** The only *financial* table corpus in the field, and it is
  scored with the metric §D.1 shows to be blind to our error class. Worth saying out loud: **the
  finance-specific table benchmark uses the finance-blind metric.**

### D.5 Where these fit, and where they stop

| Asset | Fits at | Stops at |
|---|---|---|
| **OmniDocBench** | **L2** parser selection for the regulation path; nothing else | Research-only dataset licence; measures structure/text, not numeric truth; saturated at the top |
| **olmOCR-Bench** (ODC-BY) | **L4** — *this is the design pattern to copy*, not a parser to adopt: deterministic binary unit tests over a document parse, each independently checkable, aggregated to a declared coverage | Its tests are hand-authored against academic/scanned pages; nothing about IFSCA workbooks; a pass rate ≠ a per-value bound |
| **DocILE / GriTS / FinTabNet** | **L2** evaluation vocabulary | All similarity/AP metrics; none yields a per-document error bound |

---

## §E — THE REGULATION-TEXT PATH: 102 PAGES + 399 CIRCULARS → CITABLE CLAUSE UNITS

The operator has already measured that this is mechanisable: **8,866 `shall` occurrences across 361
circulars; 866 explicit dated cross-references in 58.6% of circulars; 90 of 389 circulars amend an
earlier instrument; and 76 of 82 amending circulars cite a resolvable target (92.7%).**
That last number is the one that makes amendment-chain resolution a real engineering problem rather
than an aspiration. Here is the prior art.

### E.1 Akoma Ntoso / LegalDocML — the standard, and it is the right one

**OASIS Akoma Ntoso v1.0** (`docs.oasis-open.org/legaldocml/akn-core/v1.0/`), an OASIS Standard from
the LegalDocumentML TC. Two parts matter to us:
- **Part 1: XML Vocabulary** — `<article>`, `<section>`, `<paragraph>`, `<proviso>`, and critically
  a stable **`eId`** attribute per element, which is exactly "a stable key for a clause."
- **The Naming Convention (`akn-nc/v1.0`)** — an FRBR-derived **URI syntax for legal citations**,
  designed as "a precise pointer to the actual part of the document mentioned," and explicitly
  intended for use in **amendment commands**. SECONDARY (I read the OASIS overview pages, not the
  full specification text).

**Why this matters more than it looks.** The program already needs a stable key per *field* (L1
gives it, from cell coordinates). It equally needs a stable key per *clause*, because L3 emits
predicates that "carry the clause they claim to implement" and L5/L7 must cite it. **Akoma Ntoso's
`eId` + FRBR URI is that key, it is an OASIS standard, and inventing our own is strictly worse.**
The brief's L7 section hunts for prior art for coverage declaration and finds only CycloneDX. For
*clause identity* the prior art is settled and we should just adopt it.

### E.2 Indigo (Laws.Africa) — the amendment-chain engine, and it is alive

`laws-africa/indigo` — **77★, pushed 2026-08-07, 203 open issues, licence NOASSERTION** (custom;
**UNVERIFIED** — I did not open the LICENSE file). Companion libraries:
`laws-africa/cobalt` (27★, pushed 2026-06-18, NOASSERTION) — a Python library for Akoma Ntoso FRBR
URIs; `laws-africa/bluebell` (23★, pushed 2026-07-13, **GPL-3.0**) — an AKN parser/generator.
All three: repo metadata **VERIFIED-AT-SOURCE** via GitHub API.

Indigo is described by its maintainers as a platform for "managing, consolidating and publishing
legislation in the Akoma Ntoso format," supporting "amendments, point-in-time comparison, complex
commencements," tracking multiple amended versions of a work and visualising differences between
them. **SECONDARY** (laws.africa product pages and repo description; I did not run it).

> **This directly qualifies one of the brief's kills.** PART 7 says *"Regulation-as-code as a going
> concern — 16★ no commit since Jun 2024; zero financial regulations encoded anywhere."* That kill
> is about **rules-as-code** (Catala, OpenFisca, Blawx — encoding a rule's *logic* as executable
> code), and it should stand. **Indigo is not that.** It is **document-structure-as-code**: it
> models the text, its clause identifiers, its commencement dates and its amendment relationships —
> and it is actively developed, in production at AfricanLII and Kenya Law, and pushed three days
> ago. Conflating the two would cause us to reject the one piece of live prior art that fits, on the
> evidence for a different thing. **The kill needs a scope line: "rules-as-code (logic) is dead for
> finance; legislation-as-XML (structure) is not."**

**Where it stops.** 77 stars is a small project. It is Django-shaped, built for African
jurisdictions, and assumes a curated editorial workflow — humans marking up legislation. It gives us
**a data model and an amendment algebra**, not an ingestion pipeline that will eat 399 IFSCA PDFs.
The realistic use is: **adopt `cobalt`'s FRBR URI scheme and Indigo's amendment/point-in-time data
model; do not adopt the platform.**

### E.3 Statutory citation resolution — and the honest negative

`freelawproject/eyecite` — **267★, BSD-2-Clause, pushed 2026-08-08.** VERIFIED-AT-SOURCE (GitHub
API). Published in JOSS. Extracts full, **short-form**, **`supra`**, **`id.`** and **`ibid.`**
citations and "heuristically resolve[s] short case, supra, and id citations to their appropriate
full case antecedents"; tested against 50M+ citations across CourtListener and the Caselaw Access
Project; built on `courts-db` and `reporters-db`. SECONDARY for the feature descriptions.

**And here is the negative, which is the useful part.** eyecite's resolution power comes *entirely*
from `reporters-db`/`courts-db` — lookup tables of **US case reporters and courts**. It has **no
knowledge of `IFSCA/GN/2025/…`, `F.No. 521/IFSCA/…`, or "the Fund Management Regulations, 2025 as
amended up to 30 January 2026."** Adopting eyecite for IFSCA text would resolve approximately
nothing. **What transfers is its architecture, not its data**: the `id.`/`supra`/short-form
antecedent-resolution algorithm is exactly the shape of the problem in a circular that says "the
said circular" or "the aforementioned regulations," and the operator's 866 dated cross-references
are the *easy* half — the anaphoric ones are the hard half and eyecite is the only mature open
implementation of that pattern I found.

**I did not find** an open tool that resolves Indian financial-regulator citations. Reporting this
as **UNVERIFIED-absence**, not as "none exists": my corpus was GitHub search + web search in English,
and I did not check the India-specific ecosystem (e.g. Indian Kanoon's tooling, `nyaya`-family
projects) at all. **Someone should run that search before we claim novelty.**

### E.4 Layout-aware chunking

**UNVERIFIED / thin.** I did not find a specific, credible, primary-sourced tool for *statutory*
layout-aware chunking beyond what Docling already gives (structure-preserving conversion with
per-element provenance) and what Akoma Ntoso gives (an explicit clause hierarchy). My assessment,
labelled as assessment not finding: **the chunking problem largely dissolves once the document is in
AKN**, because the clause hierarchy *is* the chunking, and `eId` *is* the chunk key. The unsolved
step is PDF → AKN, which is where Docling's structured output feeds a rule-based promoter (numbered
headings → `<section>`, `(1)`/`(a)`/`(i)` → nested `<paragraph>`, "Provided that" → `<proviso>`).
That promoter is deterministic, small, and testable against the 8,866 `shall` occurrences as a
recall check. **I am not aware of an off-the-shelf one for Indian regulator PDFs.**

### E.5 RECOMMENDED STACK — regulation path

```
399 circulars + 102pp regs (PDF)
  └─ Docling (MIT) ──────────────► DoclingDocument  [page_no, bbox, charspan per element]
       └─ deterministic promoter ─► Akoma Ntoso     [eId per clause, FRBR URI per instrument]
            ├─ cobalt (FRBR URIs) ─► instrument identity, point-in-time
            ├─ dated x-ref extractor (866 known targets — regex + eyecite-style anaphora)
            └─ amendment graph  ───► "as amended up to <date>" resolution
                                      (Indigo's data model, not Indigo)
  └─ ~10 scanned circulars ──────► PaddleOCR-VL (Apache-2.0, 0.9B) ──► same promoter
```
- **L0** — Docling + PaddleOCR-VL fallback; content-address every PDF.
- **L1** — the AKN promoter. This is the *regulation-side analogue of schema induction*, and the
  brief does not currently have it: L1 induces a schema from the blank template but nothing induces
  a clause graph from the regulation. **Without it, L3's "clause it claims to implement" is a
  free-text string, and L5 cannot cite.**
- **L3** — reads clause units, emits predicates tagged with `eId` + FRBR URI.
- **L7** — the attestation cites `<FRBR URI>#<eId>` plus the PDF page/bbox. Reproducible.

---

## §F — CONSTRAINED DECODING AND STRUCTURED OUTPUT

### F.1 The field, with primary-source metadata

**VERIFIED-AT-SOURCE** (GitHub REST API, 10 Aug 2026):

| Library | Licence | ★ | last push | Layer |
|---|---|---:|---|---|
| **outlines** `dottxt-ai/outlines` | Apache-2.0 | 15,560 | 2026-08-07 | grammar/regex-constrained decoding |
| **XGrammar** `mlc-ai/xgrammar` | Apache-2.0 | 1,814 | 2026-08-06 | decoding backend |
| **llguidance** `guidance-ai/llguidance` | MIT | 830 | 2026-08-06 | decoding backend (Rust) |
| **guidance** `guidance-ai/guidance` | MIT | 21,709 | 2026-05-21 | programmatic constrained generation |
| **LM Format Enforcer** `noamgat/lm-format-enforcer` | MIT | 2,027 | **2026-04-04** (~4 mo) | token-filter enforcement |
| **Instructor** `567-labs/instructor` | MIT | 13,709 | 2026-08-09 | Pydantic-typed extraction + retry |
| **BAML** `BoundaryML/baml` | Apache-2.0 | 8,857 | 2026-08-10 | DSL + schema-aligned parsing |
| **PydanticAI** `pydantic/pydantic-ai` | MIT | 19,188 | 2026-08-10 | agent/typed-output framework |

Backend context, **SECONDARY**: XGrammar is reported as the default structured-generation backend
for vLLM, SGLang and TensorRT-LLM as of March 2026, at "under 40 microseconds per token"; a paper
**XGrammar-2** (`arXiv:2601.04426`) reports llguidance at ~250 µs/token on one format and >1000
µs/token on another, and compilation times of ~10 ms (XGrammar-2) vs >1000 ms (XGrammar). I did not
open the paper; **treat every one of those numbers as SECONDARY and do not put them on a slide.**
The only load-bearing point is that **per-token overhead is no longer a reason to avoid constrained
decoding**, and that has been true since at least 2025.

### F.2 The one that matters for L2's hard guard

The brief's L2 says: *"any key not in L1's induced schema is rejected deterministically."*
**Constrained decoding lets that guard be enforced at generation time rather than after it**, and the
distinction is architecturally meaningful:

```python
# L1 gives us the induced schema — 854 label instances, 494 distinct strings.
FIELD_KEYS = induced_schema.stable_keys()   # a closed, finite vocabulary

# The key is NOT a free string. It is an enum over exactly the keys L1 found.
class Fact(BaseModel):
    key: Literal[*FIELD_KEYS]      # constrained decoding makes an off-schema key UNGENERATABLE
    value: Decimal | date | bool | str
    unit: Literal["INR","USD","percent","count","none"]
    provenance: ProvenancePointer
    # NOTE: no `confidence` field — see F.4
```

With outlines/XGrammar over a local model, an off-schema key is **not merely rejected — it is
outside the reachable token space.** That converts the brief's post-hoc deterministic guard into a
generation-time impossibility. Both should be kept (belt and braces; the guard is what you can
*prove* to an auditor), but it is worth stating that the measured "100% of digits, 0% of the key"
failure mode is *structurally* eliminated, not just caught.

**Where it stops, and this is the whole point:** the enum guarantees the key is *a* valid key. It
says nothing about whether it is *the right* key. Shape ≠ truth. That is why conformal prediction on
the key-binding step (PASC) remains necessary and is not made redundant by constrained decoding.

### F.3 The format-restriction cost: both sides, then a position

**Side 1 — the paper the brief relies on.** *"Let Me Speak Freely? A Study On The Impact Of Format
Restrictions On Large Language Model Performance"*, Zhi Rui Tam, Cheng-Kuang Wu, Yi-Lin Tsai,
Chieh-Yen Lin, Hung-yi Lee, Yun-Nung Chen. **EMNLP 2024 Industry Track**,
`aclanthology.org/2024.emnlp-industry.91/`, `arXiv:2408.02442` (v3, last revised 14 Oct 2024).
Abstract, **VERIFIED-AT-SOURCE** (ACL Anthology page):

> "Surprisingly, we observe a significant decline in LLMs' reasoning abilities under format
> restrictions. Furthermore, we find that stricter format constraints generally lead to greater
> performance degradation in reasoning tasks."

**I could not extract the per-task numbers** from the anthology landing page or the arXiv abstract
page. **UNVERIFIED**: the specific magnitudes, the model list, and whether the authors softened the
claim between v1 and v3. Anyone quoting a number from this paper must open the PDF first.

**Side 2 — the rebuttal.** `.txt` (the outlines authors), *"Say What You Mean: A Response to 'Let Me
Speak Freely'"*, `blog.dottxt.ai/say-what-you-mean.html` (note: `blog.dottxt.co` 301-redirects
here). Their replication, **SECONDARY** (I fetched the post; I did not re-run their code):

| Task | Unstructured | Structured |
|---|---:|---:|
| GSM8K | 0.77 | **0.78** |
| Last Letter | 0.73 | **0.77** |
| Shuffle Object | 0.41 | **0.44** |

Their four alleged methodological errors: (1) *"The prompts used for unstructured (NL) generation
are markedly different than the ones used for structured generation"* — so the comparison is not
controlled; (2) the JSON-mode prompts were under-specified (a prompt that "doesn't mention the tools
to use"); (3) the paper **conflates JSON-mode (an API setting) with structured generation
(constrained decoding)** — different mechanisms; (4) the paper used Claude-3-Haiku as a "Perfect
Text Parser" to extract answers, and `.txt`'s plain regex beat it, **61% vs 57%**, so parser noise
contaminated the measurement.

**My defensible position, and the brief should adopt it:**

> **The cost of format restriction is contested, not settled, and it is the wrong axis for this
> architecture anyway.**
>
> 1. Point (3) is the strongest and is not really disputable: **JSON-mode ≠ constrained decoding.**
>    The EMNLP paper's headline is largely about prompting a model to emit JSON; outlines/XGrammar
>    mask logits. A result about the former does not transfer to the latter. Both sides' numbers can
>    be simultaneously true.
> 2. Point (4) is a *measurement-apparatus* failure of exactly the kind this program exists to
>    surface — an LLM in the evaluation harness, underperforming a regex, with nothing in the output
>    to say so. It is worth citing for that reason alone, independent of who is right.
> 3. **Neither side's finding threatens us**, because both are about **reasoning under format
>    constraint**, and in this architecture **L2 does no reasoning.** L2 does key-binding and
>    transcription against a schema L1 already derived. If format restriction costs chain-of-thought
>    quality, that is a tax on a faculty we deliberately do not use. Where reasoning does live —
>    L3, writing a predicate from a clause — the output is **code**, which is generated freely and
>    then adjudicated by L4's three tests, so its shape is never constrained during generation.
>
> **Therefore: the brief's line "buying the shape guarantee measurably costs reasoning quality"
> should be changed to "…is contested (EMNLP-2024 vs the dottxt replication), and is not on this
> system's critical path, because the model-bearing layers are split so that the constrained one
> does no reasoning and the reasoning one is not constrained."** That is both more accurate and a
> better answer to a judge who has read either paper.

### F.4 Provider-native structured outputs, and one warning

OpenAI, Anthropic and Google all ship provider-side structured/JSON output modes.
**UNVERIFIED** — I did not open any provider's documentation in this lane and will not state
capabilities, version names or guarantees from memory. If a provider-native mode is used, someone
must open the current docs and record what is *guaranteed* versus *best-effort*, because the
difference is exactly the L2 hard guard.

**One warning that is independent of provider.** Several of these libraries (notably Instructor)
implement **retry-on-validation-failure** as their headline feature. Retry is exactly what `pass^k`
penalises by construction, and the brief already lists "Retry" among the fixes that fail. **Any
retry in L2 must be counted and reported, and a Fact produced on attempt *k*>1 must carry that in
its provenance.** A library that silently retries three times and returns the first parse that
validated is *manufacturing* the clean verdict this product exists to refuse. **Recommend: use
Instructor's typing, disable its retries, or use `outlines` directly.**

### F.5 Where these fit / where they stop

| Asset | Fits at | Stops at |
|---|---|---|
| outlines / XGrammar / llguidance | **L2** — makes an off-schema key ungeneratable | Guarantees shape only; silent on truth; needs a local/open model to mask logits |
| Instructor / PydanticAI / BAML | **L2** typing and validation ergonomics | **Retry semantics are a `pass^k` hazard (F.4).** BAML's schema-aligned parsing is a *repair* step — repair hides the error it repaired |
| LM Format Enforcer | alternative L2 backend | 4 months since last push; the other three are more active |

---

## §G — THE PROVENANCE-POINTER FORMAT TO STANDARDISE ON

The brief calls provenance pointers "a hard requirement" but never specifies one. Here is the
proposal, built to satisfy L5's weakest-input composition rule and L7's signature.

**Design decision: adopt Docling's `ProvenanceItem` verbatim for the PDF class, and extend the union
with two locator kinds document AI does not have — an OOXML cell and a register record.** Verbatim
adoption matters: it means the PDF locator needs no translation layer, no coordinate-origin
guesswork, and it inherits a maintained, typed, versioned schema from a 64k-star MIT project.

```jsonc
{
  "anchor": "1.0",
  "source": {
    "content_sha256": "…",           // the exact bytes verified
    "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "retrieved_at": "2026-08-10T12:14:56Z",
    "origin_uri": "https://ifsca.gov.in/Download/…"
  },
  "extractor": { "name": "openpyxl", "version": "3.1.5", "mode": "DETERMINISTIC" },
  "warrant": "DETERMINISTIC",        // DETERMINISTIC | MODEL_EXTRACTED | DERIVED
  "locator": { /* exactly one of the four below */ }
}
```

**1 — `xlsx_cell`** (source class 1). Nothing in document AI models this; it is ours.
```jsonc
{ "kind": "xlsx_cell",
  "sheet_name": "Table 1.5", "sheet_index": 2, "sheet_sha256": "…",  // per-sheet hash
  "ref": "O4", "row": 4, "col": 15,
  "merged_anchor": null,                    // if inside a merged range, the top-left ref
  "formula": { "present": true,
               "encoding": "SHARED_DEPENDENT", // TEXT | SHARED_MASTER | SHARED_DEPENDENT | ARRAY | NONE
               "si": 4, "master_ref": "O3",
               "resolved": "=SUM(C4:N4)" } }
```
> **`formula.encoding` is not decoration.** §A.2 shows that 55.2% of formula-bearing cells across
> the nine workbooks are `SHARED_DEPENDENT`. Recording the encoding is what makes the undercount
> *impossible to repeat silently*: a report can state "505 formula-bearing cells, of which 211
> shared dependents," and any future reader who sees only 294 knows immediately what happened.

**2 — `pdf_span`** (source class 2). **Docling's `ProvenanceItem`, field-for-field.**
```jsonc
{ "kind": "pdf_span",
  "page_no": 90,
  "bbox": { "l": 72.0, "t": 118.4, "r": 523.6, "b": 141.2, "coord_origin": "TOPLEFT" },
  "charspan": [1042, 1197],
  "table_cell": { "start_row_offset_idx": 3, "end_row_offset_idx": 4,
                  "start_col_offset_idx": 2, "end_col_offset_idx": 3,
                  "row_span": 1, "col_span": 1 }   // present only for table cells; may be null
}
```

**3 — `clause`** (the regulation, once promoted to AKN). Identity from the OASIS naming convention.
```jsonc
{ "kind": "clause",
  "frbr_uri": "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30",
  "eId": "sch_3__part_A__point_g",
  "as_at": "2026-01-30",
  "pdf_span": { /* a full pdf_span, so the clause is also visually citable */ } }
```

**4 — `register_record`** (source class 3). Ours; no prior art found.
```jsonc
{ "kind": "register_record",
  "endpoint": "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet",
  "query": { "EncryptedId": "…" },
  "snapshot_sha256": "…",              // hash of the full 2,005-record list snapshot
  "fetched_at": "2026-08-10T12:31:02Z",
  "field": "RegistrationNumber",
  "raw_value": "IFSCA/FME/III/2022‑23/037",   // EXACT bytes, homoglyph preserved
  "normalised_value": "IFSCA/FME/III/2022-23/037",
  "normalisation": ["NFKC", "U+2011->U+002D", "strip"] }
```
> **`raw_value` and `normalised_value` are both mandatory, and `normalisation` lists every
> transformation applied.** §C.3 is the reason: the difference between those two strings is a
> non-breaking hyphen in a live regulator's register, and a system that stores only the normalised
> form has destroyed the evidence that its own normalisation was load-bearing.

**Composition rule (implements L5's weakest-input requirement).** A derived Fact carries the list of
its input anchors and takes `warrant = min(inputs)` under
`DETERMINISTIC > MODEL_EXTRACTED > DERIVED`, and `retrieved_at = max(inputs)` — so a verdict is
never fresher than its stalest input, and never stronger than its weakest.

**What to sign at L7.** `source.content_sha256` for every input, the register `snapshot_sha256`, the
AKN `frbr_uri@as_at` for every cited clause, the predicate-set version, and each predicate's
mutation score and FFR. That set is sufficient to re-derive the verdict byte-for-byte.

---

## What this changes about the design

**1. L2 is two layers, not one, and one of them has no model in it.**
The filing path (xlsx) is 100% deterministic — verified, 0 bytes of embedded media across 9
workbooks. Document AI, constrained decoding and conformal prediction belong **only** to the
regulation path and to hypothetical scanned filings. The architecture diagram should split L2 into
**L2a Structural extraction (deterministic, xlsx + register)** and **L2b Document extraction
(model-bearing, PDF)**. As written, the brief implies the primary artifact passes through a model,
which is both false and needlessly weakens the pitch — *"the filing pipeline contains no model at
all"* is a far stronger claim than anything in Part 5.

**2. A load-bearing number in §4.3 is wrong, and correcting it helps us.**
"38 of 294 (13%) express a checkable relationship" → **138 of 505 (27.3%)**. 825 of 1,495
formula-bearing cells across the nine workbooks (55.2%) are shared-formula dependents invisible to a
text-only reader; per workbook the undercount ranges 0% to **92.0%**. L3's free starting inventory of
authored checks is **135 SUM identities + 3 COUNTIF tallies**, not 38. And the fix is `openpyxl`,
verified working, already installed — but openpyxl **discards the data-validation extension**, so
L1 must read validations from raw XML. Two lines of code, one of them a warning nobody read.

**3. We have a real clean corpus for one predicate class, today, with no synthesis.**
Risk #2 in the architecture says the clean corpus is the design's largest structural weakness
because filed returns are not public. **The live register is public, it is 229 FMEs, and it is
clean by definition** — every entity in it is validly registered. Any predicate about registration
identity can have a **real, non-synthetic FFR measured immediately.** I measured one: the obvious
registration-number regex has a **38.2% false-failure rate on 228 live FMEs.** That is a genuine
L4-test-3 measurement on real data, available before the hackathon, and it should be in the demo.

**4. The strongest demo asset is now a named-entity false failure, not a synthetic one.**
`IFSCA/FME/III/2022‑23/037` (Marcellus Investment Managers) contains **U+2011**, not a hyphen.
`IFSCA/FME/IV/2023-24/033` (ASK Investment Managers) uses a category numeral that does not exist.
One FME's registration number is the string `100`. A reviewer can verify all three in ninety seconds
on the regulator's own site. **This beats the two self-demonstrations in §4.4** because the victim
is the regulator's data rather than the operator's code, and because it shows the failure is
*endemic to regulated reporting*, not incidental to one script.

**5. The TEDS claim survives verbatim — use it, and sharpen it.**
32 of 32 rows on OmniDocBench v1.6_full, mean gap +3.70, max +7.47 (Marker). **CONFIRMED.** But stop
short of the current wording: the right claim is not "table benchmarks are near-blind to our error
class" as an assertion, it is that **TEDS compares cell content by string similarity, so a single
wrong digit in a nine-digit figure scores ~0.89** — near-blind *by construction*, and demonstrably so.

**6. The "no per-cell numeric metric" claim must be withdrawn and replaced.**
olmOCR-Bench asserts exact per-cell values on **920 of 1,022** table tests, **386 of 1,022** on
purely numeric cells. The claim as written is refuted by a file I downloaded. The replacement claim
— *no benchmark yields a per-cell numeric bound for a **new, unseen** document; what exists is a
pass rate over a fixed suite* — is true, survives the obvious rebuttal, and is more useful.
**Bonus: olmOCR-Bench is independent prior art for L4's design pattern** (deterministic binary unit
tests over a document, aggregated to declared coverage, explicitly rejecting edit-distance because
"soft metrics … may assign lower scores for parses … that may in fact still be correct"). We should
cite it as convergent evidence, not treat the benchmark section as purely negative.

**7. L1 needs a twin on the regulation side, and it is missing from the architecture.**
L1 induces a schema from the blank template. Nothing induces a **clause graph** from the regulation.
Without it, L3's "the clause it claims to implement" is an unresolvable free-text string and L5
cannot cite. The fix is standardised and cheap: **Docling → Akoma Ntoso, `eId` per clause, FRBR URI
per instrument, `cobalt` for URI handling.** Add it to the diagram as **L1b**.

**8. One PART 7 kill needs a scope line.**
"Regulation-as-code as a going concern" is dead for **rules-as-code** (Catala/OpenFisca/Blawx —
encoding logic). It is **not** dead for **legislation-as-XML** (Akoma Ntoso/Indigo — encoding
structure and amendment chains), which is an OASIS standard with a repo pushed three days ago.
Amendment-chain resolution — the operator's own 76/82 = 92.7% resolvable-target measurement — has
live prior art. Keeping the kill unqualified would cause us to reject the one thing that fits.

**9. Two of the 17 "decidable" predicates were decidable only by luck.**
"Registration number resolves in live register" and "scheme number resolves" depend on an endpoint
whose list payload returns `None` for `RegistrationNumber` on 650 of 650 fund rows, and whose
obvious ID field (`EncryptDId`) is `None` on 2,005 of 2,005 records. They are decidable — I decided
them — but only via a second undocumented endpoint keyed on a differently-named field. **Any
predicate that depends on a live external interface must record the interface's snapshot hash and
must degrade to `UNCHECKED(source unreadable)`, never to PASS, when the interface changes.** That
belongs in L5's closed vocabulary handling explicitly.

**10. Ban silent retry in L2.**
Instructor-style retry-until-valid is the default ergonomic in three of the four high-level
libraries and it manufactures exactly the clean verdict this product refuses to give. Either disable
it or count it into the provenance.

---

## Open questions (things I could not settle)

1. **The "Let Me Speak Freely" per-task numbers.** I only opened the ACL Anthology abstract page.
   Nobody should quote a magnitude from that paper until the PDF is opened. Also unknown whether v3
   (14 Oct 2024) softened v1's claim.
2. **olmOCR-Bench's total size.** The repo's own bench README, an arXiv HTML summary, and a
   third-party summary gave me **three different figures** (I verified only the table subset:
   1,022 tests / 188 pages). Do not quote a total.
3. **Indian statutory citation tooling.** I searched GitHub + English web only. I did not check the
   Indian legal-tech ecosystem at all. Before claiming novelty on IFSCA citation resolution,
   run that search.
4. **Indigo / cobalt licences.** GitHub reports `NOASSERTION` for both. I did not open the LICENSE
   files. `bluebell` is GPL-3.0 (verified) — **GPL-3.0 is a real constraint if we link it**.
5. **IFSCA terms of use for the register API.** 2,235 GETs made politely today with no issue, but
   nobody has read the site's terms. Do this before any scheduled polling.
6. **Whether scheme records expose a scheme number** in `DirectoryDetailGet`. I sampled FMEs only.
7. **TEDS's exact content-comparison function.** I could not read arXiv:1911.10683's body. The
   "normalised string edit distance" characterisation is SECONDARY and the §D.1 sharpened argument
   depends on it. **Open that PDF before the argument goes on a slide.**
8. **Formula evaluation library licences** (`formulas`, `pycel`) — UNVERIFIED. Recommendation is to
   re-implement the ~4 needed functions anyway.
9. **Provider-native structured output guarantees** — deliberately not researched in this lane;
   must be read from current provider docs, not memory.
10. **Docling on a protected xlsx with merged headers** (the brief's experiment 9.7) — I did not run
    it, and my recommendation makes it moot: **do not use Docling for the xlsx class at all.**
    That answers 9.7 by removing the dependency rather than testing it.
