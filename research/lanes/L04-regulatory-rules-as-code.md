# L04 — REGULATORY RULES AS CODE: is the brief's "zero financial regulations encoded anywhere" true?

**Lane run 10 August 2026.** Every number below was produced by opening the primary artifact — in most
cases by downloading the regulator's own spreadsheet and counting rows with `openpyxl`. Scripts and
downloads are in
`/private/tmp/claude-501/-Users-abishaikc-Gift/894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad/`.

**Warrant key** — `VERIFIED-AT-SOURCE` = I opened the primary artifact (regulator file, repo, licence
file, paper page) and read/counted it myself · `SECONDARY` = a credible source describes it and I did
not open the primary · `UNVERIFIED` = could not confirm.

---

## PART 0 — THE ONE-PARAGRAPH VERDICT

**The brief's Part 7 line — "Regulation-as-code as a going concern … DEAD FOR FINANCE … zero financial
regulations encoded anywhere" — is wrong as written, and wrong in a way that matters.** There are, at
minimum, **19,692 executable financial-reporting validation rules in the current-generation EU
supervisory sets alone** — EBA release 4.3 (12,925 rule × framework-version rows, 8,052 distinct codes)
plus EIOPA Solvency II 2.10.0 (6,767) — in machine-readable form, freely downloadable, updated
quarterly, with per-rule deactivation records going back to 2014. The EBA's still-applicable legacy set
adds 20,563 more for release 3.5 alone. *(Denominator discipline: 12,925 counts rule-instances, not
distinct rules, and the legacy releases overlap each other, so these figures do not simply sum.)* The brief reached its conclusion by looking at the *academic/civic* rules-as-code
projects (Catala, OpenFisca, Blawx) and one FINOS demonstrator, and never looked at the *supervisory
reporting* stack, which is where the entire industry actually lives.

**But the thing the architecture is actually claiming to be novel survives — narrowed and sharpened.**
Nobody in this corpus publishes a **measured per-rule false-failure rate**. The rule sets that
withdraw broken rules (EBA, EIOPA) do so *after the field complains*, months to years later, with a
two-value reason enum and no error rate. And one finding forces a real correction: **ESMA already
publishes a per-rule `Automatable: Yes/No` column** — a declared boundary of what the rule set cannot
check — so the brief's "no analogue exists for a financial assertion" is **REFUTED for the static
case** and survives only for the *per-filing, measured* case.

Net effect on the project: **L3's novelty claim shrinks, L4's novelty claim grows, L5's novelty claim
must be restated, and the whole thing gets a benchmark corpus it did not have.**

---

## PART 1 — METHOD AND COVERAGE DENOMINATORS

Read this before quoting any number below.

| What I searched | Interface | Coverage / limit |
|---|---|---|
| EBA validation rules | `eba.europa.eu` "Validation rules packages" page → the two published .xlsx | **Complete for releases 4.0–4.3 and 2.0–3.5.** These two files *are* the corpus, not an index of it. |
| EIOPA validation rules | `dev.eiopa.europa.eu` Taxonomy tree → Solvency II 2.10.0 validations .xlsx + List of Known Issues .xlsx | Solvency II only. I did **not** open Pension Funds, FICOD, PEPP or IRRD files (URLs recorded below). |
| ESEF | ESMA conformance-suite summary-of-tests .xlsx, 2024 and 2025 editions | Complete for the conformance suite. I did **not** unzip the 157-package test archive. |
| GitHub repos | GitHub REST API v3, authenticated (`gh`), plus shallow clones of CDM / Catala / catala-examples / FIRE | Repo metadata is exact as of 10 Aug 2026. Star counts move. |
| DRR model source | GitHub repo search + full enumeration of `orgs/REGnosys/repos` (18) and `orgs/finos/repos` + Maven Central `g:com.regnosys*` (36 artifacts) | **Positive control passed:** the identical repo-search query returns `finos/common-domain-model`. So the search works and the DRR model's absence from public GitHub is a finding, not a search failure. |
| Catala financial content | Shallow clone of `CatalaLang/catala-examples`, grep across all `.catala*` | **Positive control passed:** grep for `allocations familiales|aides logement|impot` hits real files. Financial grep (`solvency|basel|capital adequacy|prospectus|securities|liquidity coverage|derivativ`) hits only `LICENSE.txt`. |
| OpenFisca domain coverage | Full enumeration of `orgs/openfisca/repos` filtered to `openfisca-*` | 28 packages listed; all tax/benefit/pension microsimulation. |
| FFIEC / Call Report edits | `ffiec.gov` | **BLOCKED — HTTP 403 to both WebFetch and curl with a browser UA.** Everything on FFIEC below is SECONDARY. This is a real gap in this lane. |
| Bank of England | `bankofengland.co.uk` | **BLOCKED — HTTP 403 to WebFetch.** BoE claims below are SECONDARY. |
| RBI | `rbi.org.in` fetched successfully (60 kB page, content parsed); followed its own link | **Positive control passed** — the RBI site is reachable and I parsed its content table. The login wall at the end of the trail is the actual state. |

**Two things I did not do and that a follow-up should:** (1) run Arelle against a formula linkbase to
confirm executability end-to-end — I read the source but did not execute it; (2) reach the FFIEC edit
criteria files, which need a non-blocked route.

---

## PART 2 — THE ASSETS, ONE BY ONE

### 2.1 EBA — the largest published financial rule corpus on earth, with a published failure record

**Primary sources (both downloaded and parsed):**
- Index page: `https://www.eba.europa.eu/risk-and-data-analysis/reporting/reporting-frameworks/validation-rules-packages`
- Current: `https://www.eba.europa.eu/sites/default/files/2026-07/8894f4ee-c018-4aff-b720-ed4540292da2/eba_validation_rules_4.3_2026_06_23.xlsx` (1,071,753 bytes, page-dated 09/07/2026)
- Legacy: `https://www.eba.europa.eu/sites/default/files/2026-06/12d2a6ae-9f58-47ab-a684-cdc9924ed4aa/(up to 3.5) EBA_validation_rules_2026-06-10.xlsx` (13,050,707 bytes)

**Licence:** none stated on the files. EBA content is generally reusable with attribution; **treat as
UNVERIFIED for redistribution** — check before shipping the corpus inside a product.

#### Size — release 4.3 (current, DPM 2.0) · VERIFIED-AT-SOURCE

Single sheet `EBA_VR_4.3_2026_06_23`, 12,926 rows including header.

| Quantity | Value |
|---|---:|
| Rule × framework-version rows | **12,925** |
| Distinct VR codes | **8,052** |
| **Active rows** | 11,056 (85.54%) |
| **Inactive rows** | **1,869 / 12,925 = 14.46%** |
| Distinct codes inactive in *every* framework they appear in | 1,151 / 8,052 = 14.29% |
| Distinct codes inactive in *at least one* framework | 1,333 / 8,052 = **16.55%** |
| Severity `warning` | 12,125 (93.81%) |
| Severity `error` (blocks submission) | **800 (6.19%)** |
| Implemented in XBRL | 12,412 yes / 513 no |
| Cross-module rules | 328 |

Columns are: `VR Code, Source, Frameworks, Modules, Cross module, Tables, Expression, Precondtion
[sic], Description, IsActive, FromReferenceDate, ToReferenceDate, Severity, FromSubmissionDate,
Implemented in XBRL`. **There is no reason-for-deactivation column.** For 98 rows the `Description`
has been replaced by the single word `Deactivated` — the rule text is *erased*, not annotated.

**How the rules are produced** — the `Source` column is the most reusable fact in this file:

| Source | Rows | Share |
|---|---:|---:|
| `user_defined` (hand-authored by experts) | 9,671 | **74.83%** |
| `sign` (auto-derived: sign conventions) | 1,925 | 14.89% |
| `hierarchy` (auto-derived: DPM hierarchy) | 1,300 | 10.06% |
| `existence` | 28 | 0.22% |
| `variant` | 1 | 0.01% |

Corroborated independently in the legacy file's `Type` column for release 3.5 (`Manual` 6,821 /
`Identity` 10,809 / `Sign` 1,272 / `Hierarchy` 973 / `Allowed values for metric` 279 / `Unique
identifier` 141 / `Allowed values for cell(s)` 78 / `eQuivalence` 77 / `Existence check` 67 /
`Nonexistence check` 25 / `Coherence check` 16, n=20,563).

> **≈25% of a world-class regulatory rule set is mechanically derivable from the data model with no
> model and no human.** That is our L1, already validated at industrial scale by a supervisor.

#### Deactivation by framework — release 4.3 · VERIFIED-AT-SOURCE

| Framework | Rules | Inactive | % |
|---|---:|---:|---:|
| **PILLAR3** | 545 | **545** | **100.0%** |
| AE, FINREP | 43 | 21 | 48.8% |
| REM | 611 | 190 | 31.1% |
| DORA | 71 | 22 | 31.0% |
| IRRBB | 206 | 55 | 26.7% |
| COREP | 3,886 | 642 | 16.5% |
| SBP | 106 | 16 | 15.1% |
| IF | 608 | 82 | 13.5% |
| ESG | 507 | 55 | 10.8% |
| MICA | 157 | 16 | 10.2% |
| RES | 178 | 14 | 7.9% |
| AE | 230 | 12 | 5.2% |
| FP | 240 | 12 | 5.0% |
| MREL | 118 | 5 | 4.2% |
| **FINREP** | 4,752 | 168 | **3.5%** |
| AMLA / PAY / FC / TCB / FINREP+FP | 137/127/114/108/126 | 0 | 0.0% |

The **entire Pillar 3 disclosure rule set is switched off.** The newest frameworks (DORA 31%, REM 31%,
IRRBB 27%) fail hardest; the oldest and most-exercised (FINREP 3.5%) fails least. **The deactivation
rate is a decay curve against exposure** — which is exactly what you would predict if the only
qualification gate is production.

#### The historical record — release 2.0 → 3.5 · VERIFIED-AT-SOURCE

The legacy workbook has explicit `Deactivated on` / `Reactivated on` / `Deleted` columns per sheet.

| Sheet | Rules | Ever deactivated | Reactivated | **Still deactivated** | Deleted |
|---|---:|---:|---:|---:|---:|
| 3.5 | 20,563 | 1,692 (8.23%) | 684 | 1,008 (4.90%) | 1,911 |
| 3.4 | 20,016 | 1,638 (8.18%) | 685 | 953 (4.76%) | 1,898 |
| 3.3 | 19,989 | 1,628 (8.14%) | 667 | 961 (4.81%) | 1,889 |
| 3.2 | 10,629 | 1,490 (14.02%) | 668 | 822 (7.73%) | 1,884 |
| 3.1 | 9,320 | 1,272 (13.65%) | — | 688 (7.38%) | — |
| 3.0 | 8,935 | 1,215 (13.60%) | — | 631 (7.06%) | — |
| 2.10 | 7,875 | 1,022 (12.98%) | — | 555 (7.05%) | — |
| 2.9 | 7,129 | 954 (13.38%) | — | 489 (6.86%) | — |
| 2.8 | 5,704 | 823 (14.43%) | — | 385 (6.75%) | — |

**Deactivation events by year (3.5 sheet, n=1,691 dated, 1 malformed `11/049/2024`):**

`2014: 484 · 2015: 53 · 2016: 29 · 2017: 47 · 2018: 121 · 2019: 53 · 2020: 184 · 2021: 175 ·
2022: 62 · 2023: 158 · 2024: 204 · 2025: 94 · 2026: 27`

This is a **continuous 12-year stream**, not a one-off cleanup. And of the 1,008 rules still
deactivated in 3.5, **343 carried `error` severity** — rules that would have *blocked a regulatory
submission*, withdrawn because they were wrong.

#### What the EBA says, verbatim · VERIFIED-AT-SOURCE (`Explanation` sheet)

> "The EBA from time to time publishes information about Validation rules which should be disregarded
> (**primarily due to being identified as potentially incorrect**)."

> "Note that ultimately **the veracity of reported data is the responsibility of the reporting
> entity.**"

> "Except for validation rules reflecting technical requirements, **new validation rules are introduced
> as warnings initially.**"

> "EBA validation rules are expected to be applied taking into account the specific value and accuracy
> of the reported information … in order to determine any appropriate 'tolerances' when determining if
> a rule holds or is broken for a particular data set — see e.g.
> `https://en.wikipedia.org/wiki/Interval_arithmetic` for an introduction to suitable methods."

Three things fall out of those quotes:

1. **The EBA runs an informal L4 gate already** — "new rules are introduced as warnings initially" is
   a probation period. It is a *time-based* gate, not a *measurement-based* one: the rule graduates
   because nobody complained, not because its FFR was measured. That distinction is our entire pitch.
2. **The EBA disclaims the clean verdict outright.** "The veracity of reported data is the
   responsibility of the reporting entity" is a supervisor saying, in the rulebook, that passing 11,056
   validation rules is not an assertion that the filing is correct. **Quote this in the pitch.** It is
   the strongest possible external corroboration of §2.1 of the brief, from the authority with the
   biggest rule set in the world.
3. **Tolerance is undefined and delegated.** The EBA hands the reporter a Wikipedia link on interval
   arithmetic and lets them pick. The brief's measured "rounding tolerance costs 21 points of recall"
   result lands directly in this hole.

**The published reason taxonomy** (`Last Change` column, 20,545 of 20,563 rules annotated in 3.5) is:
`Add` (14,169) · `4 digits` (3,666) · `Delete` (1,289) · `Change` (943) · `Severity` (44) ·
**`Correction` (33)** · `Reexpressed` (18) · `Reactivate` (18) · `Rename/Split table` (12) …
The EBA defines `Correction` as: *"Business semantics of the rule had been incorrect, and were change
[sic] to correct this."*

**Where this fits L0–L7.** The 4.3 file is a **direct benchmark corpus for L4** and a **prior-art
skeleton for L5**. The `Source` breakdown validates **L1**. The `Explanation` sheet is the best
available external justification for **L5's UNCHECKED vocabulary** and for the no-green-tick UX.

**Where it stops.** No per-rule error rate. No count of clean filings a rule fired on. No reason
attached to any individual deactivation. Deactivation is discovered by field complaint, on a quarterly
cycle, and the rule's own text is deleted rather than annotated — so you cannot even do post-hoc
forensics on *why* a withdrawn rule was wrong.

---

### 2.2 EIOPA — the best deactivation governance in the world, and it still has no error rate

**Primary sources (downloaded and parsed):**
- `https://dev.eiopa.europa.eu/Taxonomy/Full/2.10.0/S2/EIOPA_SolvencyII_Validations_2.10.0.xlsx` (8,821,323 bytes; workbook `LAST UPDATE ON 2026-06-30`)
- `https://dev.eiopa.europa.eu/Taxonomy/Full/2.8.2/S2/EIOPA_List_of_Known_Issues_Published.xlsx` (94,854 bytes; `LAST UPDATE ON 2026-06-03`)
- Not opened, URLs recorded: Pension Funds 2.9.0 HF2, FICOD 2.8.1 HF2, PEPP PR 2.7.0 HF3, **IRRD 2.11.0 (published 27/07/2026)**, and `EIOPA_Validation_Syntax.pdf` per release.

#### Size and structure · VERIFIED-AT-SOURCE

20 worksheets covering releases 2.4.0 → 2.10.0.

| Sheet | Rules | Deactivated | % | Reason stated |
|---|---:|---:|---:|---|
| Business Validation **2.10.0** | 6,767 | 0 | 0.00% | — (fresh release) |
| Business Validation **2.8.2 HF** | 6,145 | **128** | **2.08%** | **128 / 128** |
| Business Validation **2.8.0 HotF** | 5,512 | **289** | **5.24%** | **286 / 289** |

The 2.10.0 sheet carries 31 columns. The ones that matter:

`Deactivated` · `Deactivated on` · **`Reason for deactivation`** · **`Full or partial deactivation`** ·
`Reactivated on` · `Always execute` · **`Under investigation`** · `General comments` ·
**`Temporary or permanent deactivation`** · `Severity and modules`

**EIOPA's own definitions, verbatim · VERIFIED-AT-SOURCE (`Readme` sheet):**

> `Deactivated on` — "Identifies validations which should be disregarded (**primarily due to being
> identified as potentially incorrect**). In case no date is provided a rule is considered active and
> always need to be fulfilled, otherwise it is deactivated on the indicated date."

> `Reason for deactivation` — "Identifies the reason for which validation is deactivated: **Business**
> if it was due to business reasons, **Technical** if the reason was technical, **Business/Technical**
> if it was due to both."

> `Under investigation` — "Indicates to reporting entities potential issues under EIOPA investigation.
> **Note that those validations are still ACTIVE.**"

> `Temporary or permanent deactivation` — "Temporary deactivation is made when an amendment of the
> validation is planned to be made in the future… Permanent deactivation correspond with the situation
> that a validation is not any longer needed."

> `Severity and modules` — "**ERROR** for validations that must be executed without errors to be able
> to submit the report successfully, **WARNING**, which may indicate to filers potential errors, but
> does not block the report."

**Measured reason distribution · VERIFIED-AT-SOURCE:**

- 2.8.2 HF: `Business` 69 · `Technical` 59 (n=128). All 128 `Temporary`, all 128 `Full`. 3 flagged `Under investigation` on 2025-04-07.
- 2.8.0 HotF: `Technical` 164 · `Business` 122 · blank 3 (n=289). 286 `Temporary`/`Full`. 8 `Under investigation` on 2023-12-20.

**`Under investigation` is the single closest thing in the world to our design.** It is a published,
first-class field meaning *"this rule is still firing, and we are not sure it is right."* A supervisor
shipping doubt as a data field. **It is a two-value enum and a date. It is not a rate.**

#### The Known Issues register · VERIFIED-AT-SOURCE

243 issue rows. Columns: `#, Affected version, Bugzilla Issue Reference, Affected artefact, Issue
title, Publication date, Severity, Issue description, Solution, Status, Impact on instances, Company
reporting the issue, Issue reporting date`.

- Severity: `Medium` 133 · `Low` 93 · `High` 17
- Statuses observed include `To be fixed in the next release`, `To be fixed in 2.10.0`, and — notably
  — **`Not to be fixed`**.
- Real example (issue #244, published 2026-06-03, reported by a company on 2026-04-07): Bulgaria's euro
  adoption breaks templates EP.03.01/EP.04.01; solution is *"continue to use the current reporting
  package, but treat Bulgaria as part of the eurozone and sum the values accordingly."* — i.e. a
  documented, published instruction to **work around the regulator's own instrument**.

**Where this fits L0–L7.** The EIOPA column set is **the schema our L4/L5 registry should copy almost
verbatim**, extended with the two fields it lacks (mutation score, FFR). The Known Issues register is
the prior art for **L5's UNCHECKED reason vocabulary** and for the "what would make it checkable" line
in the Unchecked panel. `Not to be fixed` is a permanent-UNCHECKED state.

**Where it stops.** `Reason for deactivation` has a **cardinality of three**. There is no rate, no
denominator, no clean-corpus measurement, and no link from a deactivation back to the filings the rule
wrongly failed. `Under investigation` fires on 3 of 6,145 rules (0.05%) — it is a hand-curated
exception list, not a measurement.

---

### 2.3 ESMA ESEF — **the finding that forces a correction to the architecture**

**Primary sources (downloaded and parsed):**
- `https://www.esma.europa.eu/sites/default/files/2025-01/esef_conformance_suite_2024_summary_of_tests.xlsx` (47,104 bytes)
- `https://www.esma.europa.eu/sites/default/files/2026-04/esef_conformance_suite_2025_summary_of_tests.xlsx` (47,836 bytes) — the 2025 suite was published **21 April 2026**
- Test archive `esef_conformance_suite_2024.zip` and documentation PDF: URLs recorded, **not** downloaded.

#### Structure · VERIFIED-AT-SOURCE

One sheet, `CS`. Columns: `Code, Reference, Description, **Automatable**, **Criticality**, Test case
1 … Test case 8`.

| Suite | Rules | `Automatable = Yes` | `Automatable = No` | `MUST` | `SHOULD` |
|---|---:|---:|---:|---:|---:|
| **2025** (pub. 21 Apr 2026) | **68** | **60** | **8** | 54 | 14 |
| **2024** | **67** | **59 (88.1%)** | **8 (11.9%)** | 54 | 13 |

2024 cross-tabulation: `(Yes, MUST)` 48 · `(Yes, SHOULD)` 11 · **`(No, MUST)` 6** · `(No, SHOULD)` 2.
**203 test cases across 67 rules, mean 3.03 per rule**, and per xbrl.org (SECONDARY) *"for each
identified rule and guideline there is at least one valid and one invalid test case."*

#### The eight rules ESMA declares non-automatable · VERIFIED-AT-SOURCE

| Code | Reference | Description |
|---|---|---|
| `G3-4-4` | G3.4.4 | Use of preferred labels on presentation links in extension taxonomies |
| `G3-4-7` | G3.4.7 | Issuer shall create a separate extended link role for each Primary Financial Statement |
| `RTS_Annex_II_Par_1` | RTS Annex II Par 1 | All monetary items are reported with a declared currency |
| `RTS_Annex_II_Par_1_RTS_Annex_IV_par_7` | RTS Annex II Par 1; IV Par 7 | All primary financial statements present in a report are marked up |
| `RTS_Annex_IV_Par_11_G3-2-2` | RTS Annex IV Par 11; G3.2.2 | Issuers shall not define a custom type if a suitable type already exists |
| `RTS_Annex_IV_Par_4_1` | RTS Annex IV Par 4 | Extension elements must not duplicate core taxonomy elements and be identifiable |
| `RTS_Annex_IV_Par_4_2` | RTS Annex IV Par 4 | Extension elements must be equipped with an appropriate balance attribute |
| `RTS_Annex_IV_Par_6` | RTS Annex IV Par 6 | Each issuer-specific PFS structure must be equipped with the calculation linkbase |

Six of these eight are **`MUST`** — legally mandatory *and* declared not machine-checkable, by the
regulator, in a published spreadsheet, stable across two annual editions.

> **This is a regulator publishing its own version of the brief's 17/24 boundary.** The brief's §4.3
> classification (17 script-settleable, 7 not) is *the same instrument* ESMA has been shipping since at
> least the 2020 suite.

**Where this fits L0–L7.** Three places, and all three are corrections rather than additions:
- **L5** — the UNCHECKED-with-reason output has direct regulatory prior art. That is *good for
  adoption* and *bad for the novelty claim*. Reframe: our contribution is not the existence of the
  boundary but that it is **computed per filing** rather than declared per rule at design time.
- **L4** — 203 valid/invalid test cases across 67 rules is a **ready-made admission-gate corpus**. Each
  invalid case is a hand-authored mutant with a known expected error code. This is L4 test 1 (can it
  fire?) already built, by a regulator, for a real financial reporting regime.
- **L1/L7** — the `Criticality` MUST/SHOULD split is the severity model to copy.

**Where it stops.** `Automatable` is a **static, design-time, binary** property of the rule. It is not
measured, it does not vary by filing, it carries no error rate, and it says nothing about how often the
59 automatable rules fire wrongly. ESMA also never computes a coverage fraction for an individual
report.

---

### 2.4 XBRL: Formula 1.0, the assertion specs, Arelle, XULE, and the US DQC

#### The specification layer · VERIFIED-AT-SOURCE

| Spec | Status | Date |
|---|---|---|
| **Formula 1.0** | XBRL International **Recommendation**, normative, "no errata have been incorporated" | **22 June 2009** |
| Value Assertions 1.0 | Recommendation | 22 June 2009 |
| Existence Assertions 1.0 | Recommendation | 22 June 2009 |
| Consistency Assertions 1.0 | Recommendation | 22 June 2009 |
| Assertion Severity 1.0 | Recommendation | 19 April 2016 |
| Assertion Severity 2.0 | Recommendation | 21 July 2022 |
| **Assertion Sets 2.0** | **Public Working Draft — still not a Recommendation after 9 years** | 4 May 2017 |

Formula 1.0 abstract, verbatim: *"a modular extension to the XBRL Specification that builds upon the
XBRL Variables Specification. It defines a syntax for formulae that can be processed to produce XBRL
facts in an output XBRL instance from information obtained from XBRL reports and their supporting
metadata."*

**Read the shape of that.** Formula 1.0 is a *fact-production* language that assertions are layered on
top of. It is 17 years old, stable, and the substrate the EBA and EIOPA rule sets actually compile to.
Assertion **Severity** reached Recommendation twice (2016, 2022) — the ecosystem has spent a decade
formalising *how loudly a rule complains* and has never formalised *how often it is wrong*.

#### Arelle · VERIFIED-AT-SOURCE

`https://github.com/Arelle/Arelle` — **227 stars, 359 forks, created 2011-06-08, pushed 2026-08-10**
(i.e. today). `LICENSE.md`: *"Copyright © 2011-present Workiva, Inc. Licensed under the **Apache
License, Version 2.0**"* — GitHub reports `NOASSERTION` only because the file also carries bundled
third-party notices. **Effective licence: Apache-2.0.**

**Yes, it executes a formula linkbase.** `arelle/formula/` contains:

| File | Bytes |
|---|---:|
| `ValidateFormula.py` | 97,595 |
| `FormulaEvaluator.py` | 76,804 |
| `XPathParser.py` | 50,369 |
| `XPathContext.py` | 50,326 |
| `FormulaConsisAsser.py` | 7,567 |
| `FactAspectsCache.py` | 2,706 |

That is a complete XPath 2.0 parser plus a formula evaluation engine — ~285 kB of it.
*(Caveat: I read the source tree; I did **not** run it. Executability is `VERIFIED-AT-SOURCE` as to
the code's existence and evident purpose, `UNVERIFIED` as to a working end-to-end run.)*

**The plugin architecture is per-regulator and already populated.** `arelle/plugin/validate/` ships
directories for: **CIPC · DBA · EBA · ESEF · EDINET · FERC · NL · ROS · UK.** Plus
`formulaLoader.py`, `formulaSaver.py`, `formulaXPathChecker.py`, `profileFormula.py`, `xuleSaver.py`.

> **Could we emit our predicates as XBRL formula assertions?** Mechanically, yes — the language, the
> severity model and an Apache-2.0 engine all exist. **But it would be a mistake to make that the
> primary representation.** A formula assertion has no place to carry a mutation score or an FFR, and
> the whole point of L4 is that a predicate without its measured error rate is not admissible. Emit
> XBRL formula as an **export format** for interoperability, keep the registry native.

#### XULE · VERIFIED-AT-SOURCE

`https://github.com/xbrlus/xule` — **Apache-2.0**, 38 stars, 16 forks, created 2021-09-10, pushed
2026-08-04. Described as *"An open-source XBRL processor for business rules, rendering and custom data
reporting."* This is the language the DQC rules are written in, and it runs as an Arelle plugin.

#### XBRL US Data Quality Committee · VERIFIED-AT-SOURCE

`https://github.com/DataQualityCommittee/dqc_us_rules` — 31 stars, 39 forks, created 2015-07-06,
**pushed 2026-08-05**. Latest release **v30.0.1, 2026-08-05**; v30.0.0 2026-06-30.

**Size:** 201 rule documentation directories (**179 `DQC_US_*` + 22 `DQC_IFRS_*`**), plus an `ESEF`
directory. Numbering runs `0001`–`0243` with **43 numbers unused** (2, 3, 7, 10, 12, 16–32, 34, 35,
37–40, 42, 50, 56, 58, 59, 63, 64, 66, 75, 96, 97, 106, 111, 138, 151, 240). *I did not establish
whether the unused numbers were withdrawn rules or never issued — do not claim withdrawal.*
XBRL US's own page states **"196 DQC Approved Rules"** (SECONDARY) — the gap against 201 doc
directories is presumably draft rules.

**Licence — this one matters and is easy to get wrong.** GitHub reports `NOASSERTION`. The actual
`License.md`, verbatim:

> "Copyright © 2015-present, American Institute of CPAs (AICPA) / Calcbench, Inc. / Toppan Merrill LLC
> / Workiva Inc. / XBRL US, Inc. … This document and translations of it may be copied and furnished to
> others, and derivative works that comment on or otherwise explain it or assist in its implementation
> may be prepared, copied, published and distributed, in whole or in part, without restriction of any
> kind, provided that the above copyright notice and this paragraph are included on all such copies and
> derivative works. **However, this document itself may not be modified in any way**, such as by
> removing the copyright notice or references to XBRL US…"

**This is not an OSI open-source licence.** We may **run** DQC rules and **benchmark against** them
freely; we may **not** fork and modify the rule set. Plan accordingly.

**Governance — the part worth copying · VERIFIED-AT-SOURCE (repo README) + SECONDARY (xbrl.us):**
- Semantic versioning `MAJOR.MINOR.FIX`; a major release means *"a new set of rules have been approved,
  coded, and accepted by the DQC **after a public comment period**."*
- Merge gate: *"at least one `+1` comment from DQC member or XBRL US staff"*, then *"a second `+1`
  comment from a second DQC member"* for code changes, then *"a `+10` comment"* after QA review.
- SECONDARY, from xbrl.us: rules are *"approved by the XBRL US Data Quality Committee after considering
  comments received during public review periods"*, and *"each DQC rule for SEC Filers is scheduled
  with an effective date, **60-90 days after approval**."*

**Where this fits L0–L7.** The **60–90 day effective-date lag plus two-reviewer-plus-QA gate is the
governance model to copy for L4 admission.** It is the most explicit rule-admission process in the
corpus. XULE + Arelle is a credible **L5 execution substrate** for anything XBRL-shaped.

**Where it stops.** *(Positive control: I read the DQC repo README, the `docs/README.md`, the
`GlobalRuleLogic.md` listing, and the xbrl.us "Approved Validation Rules" page.)* **No false-positive
rate is published for any rule.** The governance is entirely *procedural* — who signed off, and how
long filers get to prepare. Not one number about how often a rule is wrong. And the IFSCA workbooks
are `.xlsx`, not XBRL, so none of this executes on our artifact without an L0/L1 bridge.

---

### 2.5 SDMX + VTL — the strongest candidate compile target, and a real one

**Standard · VERIFIED-AT-SOURCE** (`https://github.com/sdmx-twg/vtl`, releases API):

| Version | Released |
|---|---|
| **v2.2** | **14 July 2026** |
| V2.1 | 11 April 2025 |
| V2.0.0 | 20 April 2018 |
| v1.0.0 | 21 November 2016 |

Maintained by the **SDMX Technical Working Group / VTL Task Force**, launched by the SDMX Secretariat
end-2012. The spec repo itself declares **no licence** (`license: null`, 13 stars) — a gap to resolve
before depending on it commercially. Package is a User Manual + Reference Manual + EBNF grammar.
SECONDARY (sdmx.org): contributors include Bank of Italy, BIS, ECB, Eurostat, ILO, ISTAT, OECD,
Statistics Netherlands, UNESCO; the **ECB BIRD portal uses VTL** to document statistical validations
and transformations.

**Engines · VERIFIED-AT-SOURCE:**

| Engine | Owner | Language | Licence | Stars | Latest | Verdict |
|---|---|---|---|---:|---|---|
| **Trevas** `InseeFr/Trevas` | INSEE (French NSI) | Java | **MIT** | 20 | **v2.5.0, 28 Jun 2026**; pushed 9 Aug 2026 | **ALIVE** |
| **vtlengine** `Meaningful-Data/vtlengine` | MeaningfulData | Python | **AGPL-3.0** | 12 | **PyPI 1.9.1**; pushed 10 Aug 2026 | **ALIVE** — *AGPL is a real constraint* |
| `eurostat/VTL` | Eurostat | Java | EUPL-1.2 | 9 | pushed **29 May 2020** | **DEAD (6 years)** |
| `InseeFr/Trevas-TS` | INSEE | TS | MIT | 9 | pushed 23 Jan 2026 | alive |

> Note the repo name: it is **`vtlengine`**, not `vtl-engine`. The latter 404s.

**Is VTL a serious candidate as the language our predicates compile to?** **Evaluate, do not adopt
yet.** For it: a live ISO-adjacent standard (v2.2 six weeks old), central-bank provenance, two
maintained engines, and a Python one we could call directly. Against it: VTL is a *dataset algebra*
built for statistical time-series cubes, not for a protected `.xlsx` with merged headers and 181
cross-sheet carries; the Python engine is **AGPL-3.0**, which is viral over a hosted service unless we
keep it out-of-process; and the spec repo has no licence.

**Where this fits L0–L7.** A candidate **L5 execution target** and a candidate **L3 output language**.
The reason to care is not the syntax — it is that a VTL predicate is *portable to a supervisor*, which
is what makes the predicate registry an asset rather than a private artefact.

**Where it stops.** VTL has no notion of a rule's error rate, no severity model as rich as XBRL's, and
no coverage concept. Nothing in the VTL world declares what the rule set does not cover.

---

### 2.6 FINOS CDM / Rune DSL / ISDA DRR — **640 executable financial conditions, open, alive today**

#### The CDM itself · VERIFIED-AT-SOURCE (shallow clone, 151 MB)

`https://github.com/finos/common-domain-model` — **273 stars, 130 forks, created 2018-02-08, pushed
2026-08-10** (today).

| Quantity | Value |
|---|---:|
| `.rosetta` model files | **145** (148 incl. non-source paths) |
| Total lines of model | **43,733** |
| **`condition` blocks (executable data rules)** | **640** |
| Distinct condition names | **543** |
| `type` definitions | 760 |
| **Paired ingest test files (`input/` → `output/`)** | **799 in / 799 out** |
| Function test resource files | 228 |

**A CDM condition has exactly the shape our L3 is supposed to emit** — a name, a natural-language
rationale, and an executable expression. Verbatim examples:

```
condition ReturnType_Total_Requires_Dividends: <"A total return implies both a price and a dividend return">
    if payout as PerformancePayout -> returnTerms -> priceReturnTerms -> returnType all = ReturnTypeEnum -> Total
    then payout as PerformancePayout -> returnTerms -> dividendReturnTerms exists
```

```
condition LastRegularPaymentDate: <"FpML specifies that lastRegularPaymentDate must only be included if
    there is a final stub. As part of the CDM, this data rule has been adjusted to specify that it only
    applies to interest rate swaps, as the credit derivatives products can have a specified
    lastRegularPaymentDate while the stub is typically not applicable to those.">
    if payout as InterestRatePayout -> paymentDates -> lastRegularPaymentDate exists
            and payout as InterestRatePayout -> stubPeriod -> finalStub exists
    then payout as InterestRatePayout count = 2
```

Note what the second rationale *is*: a documented **divergence from the source standard, with the
reason**. That is a governance artefact our predicate library should imitate exactly.

**Licence — a trap.** `LICENSE.md` is the **Community Specification License 1.0**, whose own second
sentence reads: *"**It is not intended for source code.**"* The model is licensed as a *specification*.
The generated code and the tooling are Apache-2.0. **Do not assume the 640 conditions are Apache-2.0.**

#### Rune DSL and the tooling · VERIFIED-AT-SOURCE

`REGnosys/rosetta-dsl` **now redirects to `finos/rune-dsl`** — the DSL has been donated to FINOS.
Apache-2.0, 48 stars, pushed 2026-08-10. Companions in the FINOS org, all pushed within the last 24
hours: `rune-common` (8★), `rune-testing` (4★), `rune-python-generator` (1★), `rune-python-runtime`
(0★), `cdm-object-builder` (12★).

**Maven Central, group `com.regnosys.*`: 36 artifacts, all at 11.70.2**, including
`com.regnosys:ingest-test-framework`, `com.regnosys:rosetta-testing`, and code generators for
**csv, excel, typescript, c-sharp, golang, json-schema, python, scala, daml, kotlin**.

> **The Excel code generator is worth a look on its own.** `com.regnosys.rosetta.code-generators:excel`
> generates spreadsheet artefacts from a Rune model — the exact direction we need for L1→L5 on an
> `.xlsx` template.

#### The DRR model — **not public** · VERIFIED-AT-SOURCE (with positive control)

I searched GitHub repo search for `drr in:name org:finos` and `regulatory-reporting rosetta`, and
enumerated **the entire `REGnosys` org (18 repos)** and the FINOS org listing, plus Maven Central for
`g:com.regnosys*` (36 artifacts) and a keyword search for `drr` (1 hit, an unrelated Vue grid
component). **The DRR model source appears in none of them.**

*Positive control:* the identical repo-search query returns `finos/common-domain-model`. The search
works; the absence is real.

**So the correct statement is:** *ISDA DRR encodes reporting regulation as executable, testable code —
but only the **DSL, the code generators and the testing framework** are open source (Apache-2.0). The
**encoded regulatory rules themselves** are distributed to ISDA members via the Rosetta platform.*
This is a **QUALIFIED** result, not a refutation of the brief and not a confirmation of it.

**Coverage and testing** (SECONDARY, `drr.docs.rosetta-technology.io/source/overview.html`): CFTC
Rewrite *delivered*, EMIR Refit *in progress*, proof-of-concept for EMIR / MiFIR / MAS. Testing is by
**"Test Pack"** — *"Synthetic data samples for each step's input and output are captured in a 'Test
Pack' that allows to validate any implementation against those tests."* The docs give **no statement of
what the model does not cover** — only maturity labels (delivered / in progress / PoC).

**FCA/BoE DRR pilot** — Phase 2 Viability Assessment is real and published at
`https://www.fca.org.uk/publication/discussion/digital-regulatory-reporting-pilot-phase-2-viability-assessment.pdf`
(SECONDARY — I did not re-open it this lane). The brief's existing numbers (firm cost £1,140k → £760k,
+£361k central, **2% net**, *"unlikely to be considered worthwhile for a firm"*) stand unchallenged and
should be retained. PA Consulting conducted an independent review of Phases 1 and 2 (SECONDARY).

**Where this fits L0–L7.** Three concrete reuses:
- **L3 output format** — copy the `condition Name: <"rationale"> expression` shape verbatim. It is
  battle-tested across 543 named rules and it forces the model to state *why*.
- **L4 benchmark** — **799 input/output pairs** is a real, open, verified financial corpus. It does not
  cover fund returns, but it is a legitimate second dataset for testing the mutation harness on
  something we did not author.
- **L7 / governance** — the "documented divergence with reason" pattern in CDM rationales.

**Where it stops.** CDM conditions encode **product and data-model constraints derived from FpML and
industry convention — not statutes.** The statutory layer (DRR) is exactly the part that is closed.
And the Community Specification License is not a source-code licence.

---

### 2.7 FIRE (Suade Labs) — a data standard, **not** a rule corpus

`https://github.com/SuadeLabs/fire` · **Apache-2.0** (clean, real Apache text in `LICENSE`) · 82 stars,
52 forks, created 2016-01-19, **pushed 2026-07-22**. VERIFIED-AT-SOURCE via shallow clone.

**20 JSON Schema files** (`account, adjustment, agreement, batch, collateral, common, curve, customer,
derivative, derivative_cash_flow, entity, exchange_rate, guarantor, issuer, loan, loan_cash_flow,
loan_transaction, risk_rating, security, example`), 95 `.json` files in total, plus
`random_fire_generator.py`. README: *"defines a common specification for the transmission of granular
data between regulatory systems in finance."* Supported by the European Commission, ODI and ODINE via
Horizon 2020.

**Assessment: REJECT for rules; note for schema.** The only constraint machinery is JSON Schema
`required` / type declarations — one to four per schema. That is **L1-shaped, not L3/L5-shaped**. FIRE
tells you what a loan record looks like; it does not tell you anything that could be true or false about
a filing. Its `random_fire_generator.py` is mildly interesting as a synthetic-corpus generator pattern.

---

### 2.8 FINOS overall — the brief's "dead" verdict is wrong for the foundation, right for the one repo it named

**FINOS is emphatically alive · VERIFIED-AT-SOURCE.** A `sort=pushed` enumeration of `orgs/finos/repos`
returns 45+ repos pushed within the last four days, including `git-proxy` (237★, pushed today),
`architecture-as-code` (371★, today), `common-domain-model` (273★, today), `legend` (1,539★, today),
`FDC3` (267★, today), `morphir` (204★, 5 Aug), and the whole Rune family.

| Repo | Stars | Licence | Last push | Status |
|---|---:|---|---|---|
| `finos/legend` | 1,539 | Apache-2.0 | 2026-08-10 | alive |
| `finos/architecture-as-code` | 371 | Apache-2.0 | 2026-08-10 | alive |
| `finos/common-domain-model` | 273 | Community Spec 1.0 | 2026-08-10 | alive |
| `finos/FDC3` | 267 | NOASSERTION | 2026-08-10 | alive |
| `finos/morphir` | 204 | Apache-2.0 | 2026-08-05 | alive |
| `finos/ai-governance-framework` | 93 | **CC-BY-4.0** | 2026-07-21 | alive |
| `finos/rune-dsl` | 48 | Apache-2.0 | 2026-08-10 | alive |
| **`finos/open-reg-tech-us-lcr`** | **16** | Apache-2.0 | see below | **stale on `main`** |

**On `open-reg-tech-us-lcr`, the brief is CONFIRMED and I nearly got this wrong.** The GitHub
`pushed_at` field reads `2026-05-25`, which looks alive. It is not: I enumerated all **11 branches** and
pulled the commit list for `main`, whose most recent commit is **`2024-06-05T00:34:21Z`** ("Merge pull
request #67 … upgraded morphir"). The 2026 `pushed_at` is branch/bot noise. **The brief's "16★, no
commit since 5 Jun 2024" is exactly right.**

*(Method note for the whole corpus: `pushed_at` is not an activity signal. Always pull the default
branch's commit list. This cost me one near-miss and is worth carrying into other lanes.)*

`finos/ai-governance-framework` is **CC-BY-4.0**, not a code licence — consistent with the brief's
"prose with 0 conformance tests".

---

### 2.9 United States — **the gap in this lane**

**FFIEC: BLOCKED.** `www.ffiec.gov` returned **HTTP 403** to WebFetch *and* to curl with a full browser
User-Agent, on both `/resources/reporting-forms/ffiec101-validation` and
`/resources/reporting-forms/ffiec031`. I could not open the primary source. Everything here is
**SECONDARY** and must be re-run through a non-blocked route before it reaches a slide.

SECONDARY findings, from search result snippets:
- FFIEC publishes **Validation Criteria** pages per form (confirmed to exist for **FFIEC 101** and
  **FFIEC 102**), with **Validity Edits and Quality Edits in both Excel and PDF**, most recently updated
  **22 January 2026**.
- The two edit classes: *"Validity edits flag Call Report data that have mathematical errors and
  discrepancies or factual inconsistencies. Quality edits flag conditions that may indicate reporting
  errors."*
- The remedy asymmetry is the interesting part: *"The Agencies require banks to **correct** all data
  that fail validity edits and to either **correct or explain** all conditions identified by quality
  edits."* — i.e. the US model has an **explain-instead-of-fix** channel for the class of rules known to
  misfire. That is a third verdict state alongside PASS/FAIL, and it is *not* the same as UNCHECKED.
- *"The FFIEC will provide all edit criteria and make them publicly available both to banks and to
  vendors."*
- **MDRM** (Micro Data Reference Manual, `federalreserve.gov/apps/mdrm/series`, HTTP 200, ~708 kB) is the
  eight-character data-element dictionary underpinning both Call Report and FR Y-9C; CDR taxonomies
  *"incorporate presentation views, **business rule formulas**, and reporting instructions."*

**I found no evidence, at any warrant level, that FFIEC or the Federal Reserve publish per-edit error
rates or a deactivated-edits list.** Given the 403 I cannot call that an absence — **UNVERIFIED**.

**SR 26-2 — verified, and it changes the compliance framing · VERIFIED-AT-SOURCE.**
`https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf` (237,044 bytes, downloaded and
text-extracted). Dated **17 April 2026**; supersedes **SR 11-7** (4 Apr 2011) and SR 21-8; applies to
banking organizations **over $30 billion in total assets**. **Footnote 3, verbatim:**

> "Generative AI and agentic AI models are novel and rapidly evolving. As such, **they are not within
> the scope of this guidance.** Nonetheless, a banking organization's risk management and governance
> practices should guide the determination of appropriate governance and controls for any tools,
> processes, or systems not covered in this document. However, the principles described in this
> guidance apply to traditional statistical and quantitative models and non-generative, non-agentic AI
> models."

The letter's own validation vocabulary — **"Conceptual Soundness"** (§ at line 442) and **"Outcomes
Analysis"**, defined as *"compares model outputs to corresponding real-world outcomes to assess model
performance relative to model objectives and business use"* — is precisely the language L4 implements.

> **The US model-risk regime was rewritten four months ago and it explicitly declines to cover the kind
> of model our L2 and L3 contain.** There is now a named, dated, official governance vacuum around
> exactly our design, and the regulator's stated fallback is *"a banking organization's risk management
> and governance practices should guide the determination."* **The predicate registry with measured
> error rates is a concrete answer to a question a US supervisor has just formally declined to answer.**

---

### 2.10 United Kingdom — SECONDARY only

`www.bankofengland.co.uk` returned **HTTP 403** to WebFetch. All SECONDARY:

- BoE publishes a **taxonomy, DPM dictionary, annotated templates and validation rules** for both
  Banking and Statistical reporting, downloadable as ZIP and XLSX, under the Statistical Code of
  Practice. Banking taxonomy release notes go to at least **v3.8.0 (PWD, 5 Feb 2024)**; Statistical
  Forms Taxonomy to **v1.3.1** (Statistical Notice 2025/02).
- **BEEDS** (Bank of England Electronic Data Submission portal) introduced 2015, upgraded 2018, with
  *"automatic validation checks."*
- **Transforming Data Collection (TDC)**, plus the Banking Data Review, *"have evolved into a new
  project, **Future Banking Data (FBD)**"*, per the PRA Business Plan 2025/26.
- A PWD release *"aims to address known issues in data modelling and **validation rules**"* — so the BoE
  has a known-issues concept too, but I could not open the register.

**Do not quote UK numbers.** Re-run this section through a working route.

---

### 2.11 India — **the rules exist and are behind a login wall** · VERIFIED-AT-SOURCE

This is the most decision-relevant section for the GIFT application.

**Trail, followed end to end and verified:**

1. `https://www.rbi.org.in/scripts/ValidationRules.aspx` → HTTP 200, 60,112 bytes, title
   **"Validation Rules/Taxonomy of Returns | Official Website of Reserve Bank of India"**.
2. The page's entire content is a **one-row table**, verbatim:
   > "1. To access the Taxonomy/Validation Rules of CIMS returns: `https://sankalan.rbi.org.in/`"
3. `https://sankalan.rbi.org.in/` → HTTP 200, 3,254 bytes, `<title>CIMSLOGIN</title>`. Body is an empty
   SPA shell. **Login wall.**
4. `https://cims.rbi.org.in/` → identical: HTTP 200, 3,254 bytes, `<title>CIMSLOGIN</title>`.

*Positive control:* the RBI site is fully reachable — I fetched, parsed and extracted the content table
from `ValidationRules.aspx`. The wall at the end of the trail is the state of the world, not a fetch
failure.

**SEBI / AMFI:** searched; found only prose circulars and PDF formats (Master Circular formats, AMFI
Best Practice Guidelines, quarterly Compliance Test Reports). **No machine-readable validation rule set
located.** Warrant: **UNVERIFIED** as an absence — my search was keyword-based over general web results,
not an enumeration of sebi.gov.in, and per the brief's own rule that is not a corpus.

> **The asymmetry is the pitch.** The EBA publishes 12,925 rules and 12 years of its own withdrawals as
> a spreadsheet anyone can download. India's equivalent is four kilobytes of login page. And IFSCA —
> per the brief's §4.3, measured — ships workbooks in which **38 of 294 formulas (13%) express a
> checkable relationship and 181 (62%) merely copy a value**. Nobody is going to hand us a rule corpus
> for GIFT City. We have to synthesise or hand-author it, and *that is the actual reason L3 and L4
> exist.*

---

### 2.12 Catala / OpenFisca — the brief's original evidence, checked properly

**Catala · VERIFIED-AT-SOURCE.** `CatalaLang/catala`: **2,358 stars**, Apache-2.0, **pushed
2026-08-10** (today). The brief's framing of Catala as part of a dead category is **wrong on
liveness** — this is one of the most active language projects in the space, with 17 repos in the org.

**But on finance the brief is right, and I ran the control properly.** The encoded law lives in
`CatalaLang/catala-examples` (Apache-2.0, 16★, pushed 2026-08-05), which I shallow-cloned. **92
`.catala*` files across 12 domains:**

`NSW_community_gaming · aides_logement · allocations_familiales · asp ·
base_mensuelle_allocations_familiales · droit_successions · impot_revenu · polish_taxes ·
prestations_familiales · prologue_france · smic · us_tax_code`

- *Positive control:* grep for `allocations familiales|aides logement|impot` → hits real `.catala_fr`
  source files. The corpus and the grep both work.
- *Financial grep:* `solvency|basel|capital adequacy|prospectus|securities|bank capital|liquidity
  coverage|derivativ` across the whole clone → **one hit, `LICENSE.txt`.**

**Verdict: zero financial regulations encoded in Catala. CONFIRMED, with a passing positive control.**
(Note `CatalaLang/french-law`, 7★, last pushed 2025-07-31 — the generated-artefact repo, also
tax/benefit.)

**OpenFisca · VERIFIED-AT-SOURCE.** `openfisca-core`: 234★, **AGPL-3.0**, pushed 2026-04-22. Full
enumeration of `orgs/openfisca/repos` filtered to `openfisca-*` returns **28 packages**: france (308★),
tunisia (20★), senegal, paraguay, mali, nouvelle-caledonie, paris, france-entreprises, france-local,
france-pension, france-inheritance, france-indirect-taxation, france-fiscalite-miniere, tunisia-pension,
tunisie-entreprises, ceq, plus tooling. **Every one is tax/benefit/pension microsimulation. Zero
financial-regulation packages. CONFIRMED.**

---

### 2.13 The closest published work to L3 — and it is not in finance

Two papers surfaced and I opened both at source.

**`arXiv:2604.17153` — "From Legal Text to Executable Decision Models: Evaluating Structured
Representations for Legal Decision Model Generation", David Graus, submitted 18 April 2026.**
VERIFIED-AT-SOURCE (abstract page read in full).

- Dataset: **95 production decision models** paired with legal text from the **Dutch Environment and
  Planning Act**, powering the Omgevingsloket government permit platform. **Publicly released.**
- Four input conditions compared: raw legal text; + semantic role labels; + I/O constraints; + both.
- **I/O constraints give the dominant gain: +37–54% structural similarity over baseline.** Semantic role
  labels: modest.
- **Outcome evaluation: generated models match the gold standard on 51–53% of test scenarios.**
- LLMs eliminate redundant pass-through logic comprising **45–55% of nodes**.
- *"Structural similarity and outcome equivalence are complementary: structural similarity does not
  guarantee outcome equivalence, and vice versa."*
- **Domain: environmental/planning law. Not financial. No qualification gate. No false-failure rate.**

**`arXiv:2608.06312` — "Benchmarking and Enhancing LLMs for Rule-Intensive Review of National Standard
Documents", Wang, Yang, Liang, Lin, Wang, Cao, Hao; 6 August 2026.** VERIFIED-AT-SOURCE.

- **GB/T-Bench**: **488 documents → 7,306 traceable review error instances, 25 diagnosable error types**,
  over Chinese GB/T national standards.
- Best baseline LLM **0.3280 CMCS**; their GB/T-Reviewer framework **0.5094**; **expert 0.6640**.
- Uses *"deterministic rules combined with **constrained LLM rewriting for counterexample generation**"*
  — i.e. model-generated mutants, which is L4 test 1 in a different costume.
- **Domain: national technical standards. Not financial. No separately reported FP/FN rates.**

**What these two do to our claims.** They **REFUTE** any claim that "LLM → executable rules from legal
text" is unexplored. They **CONFIRM** that (i) it has not been done for financial regulation, (ii)
nobody attaches a qualification gate with a measured false-failure rate, and (iii) the field's own best
result — **51–53% functional equivalence on production models** — sits almost exactly at the brief's
pre-registered L3 threshold of **3 of 10 surviving**. That is a useful prior: **experiment 9.1 is likely
to land near its threshold rather than far above or below it, so the pre-registration must be honoured
literally.**

---

## PART 3 — THE THREE QUESTIONS, ANSWERED

### (a) What survives of "zero financial regulations encoded anywhere"?

**Nothing survives of the sentence as written.** Here is the strongest defensible restatement, with each
clause carrying its own warrant:

> **Executable financial-regulatory validation rules exist at very large scale and are actively
> maintained — the EBA alone publishes 12,925 rule-instances (8,052 distinct) for its current framework
> and ~20,500 for its legacy one; EIOPA publishes 6,767 for Solvency II 2.10.0; ESMA publishes 68 ESEF
> rules with 203 valid/invalid test cases; the XBRL US DQC publishes ~196 approved rules; and the FINOS
> CDM carries 640 executable conditions.** *(all VERIFIED-AT-SOURCE)*
>
> **What is empty is a different set:** the *civic/academic* rules-as-code projects contain **no
> financial regulation whatsoever** — Catala's 12 encoded domains and OpenFisca's 28 country packages
> are entirely tax, benefit and pension law *(VERIFIED-AT-SOURCE, positive controls passed)*, and
> FINOS's own US LCR demonstrator has had **no commit on `main` since 5 June 2024** at 16 stars
> *(VERIFIED-AT-SOURCE via branch enumeration)*.
>
> **And what is missing everywhere is the measurement:** across every corpus above, **not one publishes
> a measured false-failure rate for any individual rule.**

The brief's error has a clean diagnosis worth recording: it **searched the wrong shelf**. "Regulation as
code" is the name of a civic-tech movement; the financial industry does the same thing under the name
"supervisory reporting validation rules" and never uses the phrase. This is the brief's own working
rule #2 failing — a search interface (the rules-as-code literature) was mistaken for the corpus it
purports to cover.

### (b) Does any of this make our idea unoriginal?

Taken sub-question by sub-question, with the positive control stated for every absence claim.

---

**(i) Does anyone publish a measured false-failure rate per rule? — NO.**

*What I searched:* the EBA 4.3 file (all 15 columns × 12,925 rows) and the legacy file (all sheets +
the `Explanation` sheet in full); the EIOPA Solvency II validations file (all 31 columns × 6,767 rows)
and its Known Issues register (243 rows × 13 columns); the ESEF 2024 and 2025 summary-of-tests files
(all columns); the DQC repo README, `docs/README.md` and the xbrl.us Approved Validation Rules page; a
grep for `false positive|false-positive|failure rate|coverage report` across **every `.md` in the CDM
clone**; and a targeted web search for `"false positive rate" per validation rule regulatory reporting
published measured supervisory`.

*Positive control:* the same column-by-column reading **did** find EIOPA's `Reason for deactivation`,
`Under investigation` and `Temporary or permanent` fields, and ESMA's `Automatable` field. So the method
detects governance metadata when it is present.

*Result:* **Zero measured per-rule error rates.** The nearest approaches are:
- **EBA — a population-level rate, discoverable but never stated by the EBA.** 1,692 of 20,563 rules in
  release 3.5 have been deactivated at least once = **8.23%**; 1,869 of 12,925 rows in release 4.3 are
  currently inactive = **14.46%**. *This is a lifetime withdrawal rate for expert-authored regulatory
  rules, and I computed it — the EBA does not publish it as a statistic.*
- **EIOPA — a 3-value enum** (`Business` / `Technical` / `Business/Technical`) attached to each
  deactivation, plus a boolean-plus-date `Under investigation` flag firing on **3 of 6,145 rules
  (0.05%)**.
- **The only quantitative signal anyone publishes is the severity split**, which is a *prior* on
  trustworthiness, not a measurement: EBA 4.3 is **93.81% warning / 6.19% error**.

> **The EBA's decade-old convention — "new validation rules are introduced as warnings initially" — is
> a qualification gate with the measurement removed.** A rule earns blocking status by surviving
> production without complaint. We propose it earn admission by surviving a mutation harness and a
> clean corpus with the number written down. That is the whole delta, and it is real.

**Our idea is NOT unoriginal on (i).**

---

**(ii) Does anyone declare what the rule set does NOT cover, as a first-class output? — YES, and this
REFUTES part of the brief.**

**ESMA does, per rule, in a published spreadsheet, stably across editions.** `Automatable: Yes/No`,
**8 of 67 (2024) and 8 of 68 (2025) declared not automatable, six of them `MUST`-criticality**, each
named with its RTS/Guideline reference. *(VERIFIED-AT-SOURCE)*

**EIOPA does, per instrument defect**, in its 243-row Known Issues register with a `Not to be fixed`
status. *(VERIFIED-AT-SOURCE)*

**The EBA does, at the level of the whole regime**, in one sentence: *"ultimately the veracity of
reported data is the responsibility of the reporting entity."* *(VERIFIED-AT-SOURCE)*

**Therefore ARCHITECTURE §L7's claim — "There is no analogue for a financial assertion" — is REFUTED
as stated and must be rewritten.** CycloneDX `compositions.aggregate` is no longer the only prior art;
ESMA's `Automatable` column is closer, in finance, and predates us.

**What survives, and it is narrower but sharper:**

> Every existing declaration is **static, design-time, per-rule and binary**. It is a property of the
> *rulebook*. **No one computes a coverage fraction for an individual filing**, no one composes it with
> provenance, no one grows it (our L6), and no one signs it (our L7). *"11.9% of ESEF rules cannot be
> automated"* is a fact about ESEF. *"This filing was checked on 71% of its in-scope predicates, and
> here are the 29% and why"* is a fact about **this filing**, and nobody produces it.

That restatement is defensible and still gets the product its distinctive surface. It also *helps*: we
can now say "ESMA already does this per rule; we do it per filing" — which is a far easier sell to a
supervisor than "nobody has ever thought of this."

---

**(iii) Does anyone synthesise rules with a model under a qualification gate? — NO. Half of it is done;
the gate is not.**

*What I searched:* targeted searches for LLM/model-generated executable validation rules in regulatory
reporting; opened both papers that surfaced at their arXiv abstract pages; checked the DQC governance
docs and the CDM `CONTRIBUTING.md`/`GOVERNANCE.md` presence; and searched the DRR documentation for a
generation step.

*Positive control:* the search **did** surface two directly on-target 2026 papers (`2604.17153`,
`2608.06312`), so it is not returning empty because the query is bad.

*Result:*
- **Model synthesis of executable rules from legal text: DONE, twice, in 2026, outside finance.**
  51–53% functional equivalence on 95 production Dutch models; GB/T-Bench on 488 Chinese standards.
- **In financial regulation: not found.** Every financial rule corpus I opened is hand-authored by
  committee (DQC: two `+1`s and a `+10`; EBA: 74.8% `user_defined`; EIOPA: expert-defined; CDM: FINOS
  working group).
- **Under a qualification gate with a measured false-failure rate: found nowhere, in any domain.**
  arXiv:2604.17153 reports functional equivalence against a gold standard — a *fidelity* measure, not a
  false-failure rate on clean inputs, and with no admission decision attached. GB/T-Bench generates
  counterexamples but does not use them to admit or reject a rule.

**Our idea is NOT unoriginal on (iii)** — but the honest framing changed. It is no longer *"can a model
write an executable check from law?"* (answer: partially, ~51–53%, published). It is *"can a model
write an executable check from law **that survives a gate strict enough that its silence means
something**?"* That is a better question and a harder one, and experiment 9.1 now has a published prior
to be scored against instead of a vacuum.

---

### (c) What can we literally reuse?

**Rule corpora to benchmark against** *(all downloaded and parsed this lane)*
1. **EBA 4.3** — 12,925 rules with active/inactive, severity, expression, and the `Source` field that
   proves 25% are schema-derivable. The single best external validation of L1 and L4.
2. **EBA legacy 2.0–3.5** — 12 years of deactivation and reactivation events with dates. **The only
   longitudinal record of hand-authored regulatory rules failing in production that exists anywhere.**
3. **EIOPA Solvency II 2.10.0 + Known Issues** — the column schema to copy for the predicate registry.
4. **ESEF 2024/2025 summary-of-tests** — 203 valid/invalid cases over 67 rules; the `Automatable`
   column; the `MUST`/`SHOULD` severity model.
5. **FINOS CDM** — 640 executable conditions with rationales, and **799 input/output test pairs**.

**A DSL to compile to**
- **Rune DSL** (`finos/rune-dsl`, **Apache-2.0**, pushed today) — **ADOPT the `condition Name:
  <"rationale"> expression` shape for L3's output format** even if we never run the Rune toolchain.
- **VTL 2.2** (14 Jul 2026) — **EVALUATE** as a portable export. Watch the spec repo's missing licence
  and vtlengine's AGPL-3.0.
- **XBRL Formula 1.0 + Assertion Severity 2.0** — **EVALUATE as an export format only.** No slot for a
  mutation score or an FFR; making it primary would delete the thing that makes our registry worth
  having.

**An engine to execute in**
- **Arelle** (**Apache-2.0**, 227★, pushed today) — a working XPath 2.0 + formula evaluator with
  per-regulator validation plugins already shipping for EBA, ESEF, EDINET, FERC, UK and four others.
  **ADOPT if and when the artifact is XBRL. It is not the right substrate for a protected `.xlsx`.**
- **vtlengine** (Python, PyPI 1.9.1) / **Trevas** (Java, MIT, v2.5.0) — EVALUATE.
- **`com.regnosys.rosetta.code-generators:excel`** — worth an hour: a Rune→Excel generator is pointed in
  exactly the direction L1 needs.

**A governance model to copy** — this is the highest-value non-code asset in the lane, and it is a
composite of four regulators:

| Take | From | Why |
|---|---|---|
| Two-reviewer `+1`/`+1` then QA `+10`, **public comment period**, **60–90 day effective-date lag** | XBRL US DQC | The most explicit rule-admission process in existence. Our L4 adds the measurement it lacks. |
| `Reason for deactivation` · `Full or partial` · `Temporary or permanent` · **`Under investigation`** · `Reactivated on` | EIOPA | The registry schema, near-verbatim. Add `mutation_score` and `ffr` and it is L4. |
| `Automatable: Yes/No` × `Criticality: MUST/SHOULD` | ESMA ESEF | The UNCHECKED taxonomy, with regulatory precedent. |
| **"New validation rules are introduced as warnings initially"** | EBA | Probation before blocking. We keep the shape and replace "time elapsed" with "measured FFR". |
| **"The veracity of reported data is the responsibility of the reporting entity"** | EBA | The disclaimer that proves a supervisor already knows a rule-set pass is not a clean verdict. |
| **Correct-or-explain** for the misfire-prone rule class | FFIEC *(SECONDARY)* | A third verdict state we had not considered. |

---

## PART 4 — WHAT THIS CHANGES ABOUT THE DESIGN

Six changes. Three are corrections, three are upgrades.

**1. Delete the "zero financial regulations encoded anywhere" line from the brief and the pitch.**
It is false and it is checkable in about ninety seconds by anyone in the room who has worked in
regulatory reporting — which, at a GIFT City fintech event, is most of them. Replace it with the
restatement in §(a). The replacement is *stronger*: "the EU publishes ~20,000 executable rules and
still had to withdraw 8.2% of them after the fact, with no error rate attached to any" is a far better
opening than "nobody has done this."

**2. Rewrite L7's novelty claim; ESMA got there first.** ARCHITECTURE §L7's *"There is no analogue for
a financial assertion"* is REFUTED. New wording, which the evidence supports:

> *Prior art exists for declaring coverage: ESMA publishes an `Automatable Yes/No` flag per ESEF rule
> (8 of 68 declared non-automatable in the 2025 suite, six of them mandatory), and EIOPA publishes a
> 243-item known-issues register including a `Not to be fixed` status. **Both are static properties of
> the rulebook.** No one computes coverage for an individual filing, composes it by provenance, grows
> it by metamorphic probing, or signs it. That is L5–L7.*

**3. L3's framing changes from "unprecedented" to "unprecedented in finance, and with a known prior."**
arXiv:2604.17153 gets **51–53% functional equivalence** generating executable decision models from
Dutch statute, with **I/O constraints as the dominant lever (+37–54%)**. Two consequences:
- **Feed L1's induced schema into the L3 prompt as an explicit I/O constraint.** That is the single
  measured intervention that most improves this exact task, from the only paper that has measured it.
  This is a concrete, cheap, evidence-backed change to experiment 9.1's design.
- The pre-registered "3 of 10" threshold now sits near a published prior rather than in a vacuum.
  **Honour it literally.** A result of 3–5 of 10 is the *expected* outcome, not a triumph.

**4. L4 gets promoted — it is the whole contribution.** Every other layer now has prior art. The
mutation-score + degenerate-baseline + FFR gate does not, anywhere, in any domain. And it now has an
external justification that needs no explaining: **the EBA, with ~20,500 expert-authored rules, EU-wide
consultation and a decade of iteration, has deactivated 8.23% of them at least once, is still
deactivating them (204 in 2024, 94 in 2025, 27 by mid-2026), and 343 of the currently-withdrawn ones
were hard-blocking `error` severity.** They find out from the field. **L4 is the proposition that you
can find out before you ship.** That is the sentence the whole application should be built around.

**5. Add a third verdict state, and take severity seriously.** The corpus is unanimous that PASS/FAIL is
too coarse, and it splits the difference two different ways:
- **Severity**: EBA 93.81% warning / 6.19% error; ESMA MUST/SHOULD; EIOPA ERROR/WARNING.
- **Remedy**: FFIEC's *correct-or-explain* for quality edits *(SECONDARY)*.

Our L5 vocabulary should therefore be a **2-tuple: `(PASS | FAIL | UNCHECKED(reason))` ×
`(BLOCKING | ADVISORY)`**, with a predicate's measured FFR *determining* which tier it enters — high
FFR means advisory, and the number is printed next to it. That is the EBA's warnings-first convention
with the measurement put back in, and it is defensible to a supervisor on day one because they already
run the un-measured version.

**6. The India asymmetry is the strategic argument, and it is now evidenced.** EBA: 12,925 rules,
downloadable, quarterly. EIOPA: 6,767 rules with per-deactivation reasons. ESMA: 68 rules with a
declared automatability boundary and 203 test cases. **RBI: a 4 kB login page.** IFSCA: workbooks where
13% of formulas check anything and 62% copy a value. There is no rule corpus to inherit in this
jurisdiction — which is precisely why the *generator plus gate* (L3+L4), rather than a rule engine
(L5 alone), is the right thing to build here and the wrong thing to build in Frankfurt.

**One thing that did not change:** the brief's §4.3 measurement (17/24 decidable) is now
*corroborated by a regulator*. ESMA's independently-derived automatable fraction is **88.1%** on a
rule set of a different shape; the operator's is **71%** on IFSCA predicates. Different denominators,
different artifacts, same instrument. That the two exist at all is the point: **the boundary is a thing
professionals already measure, which makes it a thing worth productising.**

---

## PART 5 — OPEN QUESTIONS

1. **FFIEC is unread.** `ffiec.gov` 403s to every route I tried. The Validity/Quality edit files for
   FFIEC 031/041/051/101/102 are the largest unexamined rule corpus in this lane, and the
   *correct-or-explain* remedy split suggests their governance is genuinely different from the EU's. Get
   them.
2. **Does anyone publish a deactivation *reason narrative*?** EIOPA's `General comments` column is
   documented as describing *"the rationale behind amendment or partial deactivation"* — I counted the
   enum but did not read the free text. If those comments contain real diagnoses, that is a labelled
   dataset of *why regulatory rules are wrong*, and it would be the best possible training signal for
   L4's mutation operators.
3. **Bank of England known-issues register.** Blocked. A PWD release note says it exists.
4. **Can Arelle actually execute a formula linkbase end to end?** I read 285 kB of evaluator source; I
   did not run it. One afternoon settles it.
5. **Is the EBA corpus redistributable?** No licence on the files. This decides whether it can ship
   inside a product or only be cited.
6. **The DQC's 43 unused rule numbers.** Withdrawn rules, or never issued? If withdrawn, that is a
   second withdrawal-rate datapoint (43/243 = 17.7%) from a completely different governance regime, and
   it would let us say something about whether the EBA's 8.23% is typical.
7. **EIOPA's other four rule sets** (Pension Funds, FICOD, PEPP, **IRRD 2.11.0 published 27 Jul 2026**)
   are unopened. IRRD is brand new — a *fresh* rule set is the ideal place to watch a deactivation curve
   start from zero, which would directly estimate the "cost of shipping unqualified rules."
8. **SEBI/AMFI absence is UNVERIFIED.** I keyword-searched; I did not enumerate sebi.gov.in. By the
   brief's own rule #2 that is not good enough to claim an absence.
9. **Does the ESEF conformance archive contain machine-readable expected error codes?** The 157-package
   zip is undownloaded. If the mapping is machine-readable, L4's harness gets a free regression suite.

---

## Adversarial verification (independent pass)

**Run 10 August 2026 by a separate agent instructed to refute, not to agree.** Nothing below accepts the
lane's own citation as evidence. Every file was re-downloaded from the URL the lane gives, into a fresh
directory (`scratchpad/adv/`), and every count was re-derived with an independently written script.
Where I could not confirm at primary source, the verdict is REFUTED or UNVERIFIABLE, not "probably
fine".

**Headline: the lane holds up unusually well.** Ten of thirteen load-bearing claims reproduce to the
digit, including every claim the design actually rests on. **One is REFUTED** (the ESEF test-case
count), **two are QUALIFIED** on secondary rows that change no conclusion. The lane's method — download
the regulator's own spreadsheet and count it — is the reason: it is the kind of claim that either
reproduces exactly or fails loudly, and it reproduced.

### Verdict table

| # | Claim | Verdict |
|---|---|---|
| 1 | `arXiv:2604.17153` — identity, author, date, and all four numbers | **CONFIRMED** |
| 2 | `arXiv:2608.06312` — identity, GB/T-Bench sizes, all three CMCS scores | **CONFIRMED** |
| 3 | ESMA ESEF publishes a per-rule `Automatable` column; 8 of 67/68 declared No; 6 of the 8 are `MUST` | **CONFIRMED** |
| 4 | "**203 test cases across 67 rules, mean 3.03**" and "a ready-made admission-gate corpus" | **REFUTED** (number) / **UNVERIFIABLE** (characterisation) |
| 5 | EBA 4.3 — 12,925 rows, 8,052 codes, 1,869 inactive, 800 `error`, `Source` breakdown, PILLAR3 100% off | **CONFIRMED** |
| 6 | EBA legacy 3.5 — **8.23% ever deactivated, 1,008 still off, 343 of them `error` severity**, 12-year stream | **CONFIRMED** |
| 7 | EIOPA — `Under investigation` is a real published field; **3 of 6,145**; reason enum has cardinality 3 | **CONFIRMED** / row for 2.8.0 HotF **QUALIFIED** |
| 8 | SR 26-2 footnote 3 — genAI and agentic AI **out of scope**; 17 Apr 2026; supersedes SR 11-7; >$30bn | **CONFIRMED** (verbatim) |
| 9 | `finos/open-reg-tech-us-lcr` — `main` has no commit since **2024-06-05**, 16★, `pushed_at` is noise | **CONFIRMED** |
| 10 | FINOS CDM — **640 conditions, 543 distinct names, 145 source files, 43,733 lines, 799/799 test pairs** | **CONFIRMED** |
| 11 | CDM licence is Community Specification License 1.0, *"not intended for source code"* | **CONFIRMED** (verbatim) |
| 12 | DQC `License.md` — *"may not be modified in any way"*; not an OSI licence | **CONFIRMED** (quote elides an exception) |
| 13 | VTL v2.2 released 14 Jul 2026; spec repo has **no licence**; `vtlengine` is AGPL-3.0; `eurostat/VTL` dead | **CONFIRMED** |
| 14 | RBI validation-rules trail dead-ends at a 3,254-byte `CIMSLOGIN` shell | **CONFIRMED** |

### The one refutation, and what it costs

**§2.3 — "203 test cases across 67 rules, mean 3.03 per rule" is wrong.**

I re-downloaded `esef_conformance_suite_2024_summary_of_tests.xlsx` (47,104 bytes — byte-identical size
to the lane's) and counted the eight `Test case 1…8` columns directly:

| Suite | Rules | Non-empty test-case cells | Distinct test-case descriptions | Mean per rule |
|---|---:|---:|---:|---:|
| 2024 | 67 | **212** | **211** | **3.164** |
| 2025 | 68 | **215** | **214** | **3.162** |

The lane's 203 does not reproduce under any reading I could construct. The correct figure is **212**
(211 distinct — exactly one description is shared by two rules). The error is ~4% and in the
*conservative* direction, so **the argument it supports gets slightly stronger, not weaker.** But it is
a number the lane marked `VERIFIED-AT-SOURCE`, and it is the only such number in the lane that failed
to reproduce. Correct it before it reaches a slide, and treat the lane's arithmetic-over-a-parsed-file
claims as reproducible-but-not-infallible.

**The second half of that claim is worse than wrong — it is unsupported.** The lane says the suite is
"**203 valid/invalid test cases** … Each invalid case is a hand-authored mutant with a known expected
error code. This is L4 test 1 (can it fire?) already built." **None of that is in the file.** The `CS`
sheet has exactly six meaningful columns — `Code, Reference, Description, Automatable, Criticality,
Test case 1…8` — and the test-case cells contain **free-text English descriptions**, e.g. *"Inline XBRL
document with `<xbrli:period>` defined in YYYY-MM-DD format without time component"*. There is:

- **no valid/invalid flag**, so the valid:invalid split is unknown — the lane's own source for it is a
  SECONDARY xbrl.org sentence, not the file;
- **no expected-error-code column**, so "with a known expected error code" is an inference about the
  undownloaded 157-package archive, which the lane's own §1 records as *not opened*.

**Damage:** the ESEF suite is **not** a drop-in L4 admission-gate corpus. It is a 68-row index that
*names* 212 test cases living in an archive nobody in this corpus has opened. Open questions §9 already
asks the right question; it should be promoted from "would be nice" to "**required before L4 claims a
free benchmark**". Downgrade §2.3's L4 bullet and §(c) reuse-item 4 to a *candidate* corpus.

### The two qualifications

**§2.2, EIOPA 2.8.0 HotF row.** The load-bearing EIOPA claims all reproduce exactly — 2.10.0 has
**6,767** rules with `Deactivated=no` on all of them; 2.8.2 HF has **6,145** rules, **128** deactivated
(2.08%), reason stated on **128/128** (`Business` 69 / `Technical` 59), all `Temporary`, all `Full`, and
**`Under investigation` on exactly 3 rows, all dated 2025-04-07** — i.e. the 0.05% that the lane's
"Where it stops" paragraph turns on. Two figures in the 2.8.0 HotF row do not:

- **Rules: 5,479 populated rows, not 5,512.** The sheet's `max_row` is 5,513; there are 33 structurally
  present but entirely empty trailing rows. The lane used `max_row − 1`. Deactivation rate becomes
  289/5,479 = **5.27%**, not 5.24%.
- **`Under investigation`: 12 non-blank, not 8** — 11 dated 2023-12-20 and one dated 2024-08-07.

Neither changes a conclusion. Both indicate the lane counted `max_row` rather than populated rows on at
least one sheet, which is worth knowing before any of these figures is quoted to two decimal places.

**§2.1, EBA legacy 3.5.** The pitch sentence — *"the EBA has deactivated 8.23% of its rules at least
once, is still deactivating them, and 343 of the currently-withdrawn ones were hard-blocking `error`
severity"* — **reproduces exactly**: 1,692 ever-deactivated, 684 reactivated, 1,008 still deactivated
(4.90%), 1,911 deleted, and the still-deactivated severity split is `warning` 662 / **`error` 343** /
blank 3. The `Type` and `Last Change` distributions match every value the lane lists. Two off-by-ones:
**n = 20,562 populated rows, not 20,563** (same `max_row` artefact; 8.23% is unaffected), and the year
histogram is **2024: 205, not 204** — the lane's self-disclosed malformed date `11/049/2024` parsed
cleanly for me, so its dated total is 1,692 with zero malformed, not 1,691 with one.

### What I confirmed hardest, because it matters most

**SR 26-2 footnote 3 is real and verbatim.** I downloaded `SR2602.pdf` (237,044 bytes) from
federalreserve.gov and extracted it. Header reads `SR 26-2 / April 17, 2026`; *"Supersedes: SR letter
11-7"*; applicability *"banking organizations with over $30 billion in total assets"*. Footnote 3 is
character-for-character as quoted, including *"they are not within the scope of this guidance"* and the
fallback *"a banking organization's risk management and governance practices should guide the
determination."* The `Outcomes Analysis` definition is also verbatim. **The named, dated governance
vacuum around L2/L3 is genuine and is the strongest single external fact in this lane.**

**The FINOS CDM numbers are exact.** Fresh `--depth 1` clone (150 MB): **145** `.rosetta` under
`rosetta-source/src/main/rosetta` (148 including 3 test-resource files), **43,733** lines, **640 named
`condition` blocks**, **543** distinct condition names, **760** `type` definitions, **799** files under
`input/` and **799** under `output/`. The quoted `ReturnType_Total_Requires_Dividends` condition matches
the repo character-for-character. *One nuance the lane omits:* there are **664** condition blocks in
total — 640 named plus **24 anonymous** (`condition:` with no name). The lane's 640 is the named count
and is the right one to quote, but say "named" when you quote it.

**Both licence traps are real.** `finos/common-domain-model` `LICENSE.md` is Community Specification
License 1.0 and its second sentence is verbatim *"It is not intended for source code."* GitHub reports
`NOASSERTION`. The DQC `License.md` contains *"this document itself may not be modified in any way"* —
**but the lane's quote truncates immediately before the clause `except as required to translate it into
languages other than English`.** The elision does not change the conclusion (still not OSI, still
run-and-benchmark-only), but restore the full clause before any lawyer reads it.

**`finos/open-reg-tech-us-lcr` is exactly as the lane describes**, and the lane's near-miss warning is
the most transferable thing in it: `pushed_at` = `2026-05-25T22:12:44Z`, 11 branches, but `main`'s most
recent commit is `83ec54a7`, **`2024-06-05T00:34:21Z`**, *"Merge pull request #67 … upgraded morphir"*.
16 stars, Apache-2.0, not archived. **Carry the `pushed_at`-is-not-activity rule into every other lane.**

**RBI.** `ValidationRules.aspx` → HTTP 200, 60,111 bytes, title *"Validation Rules/Taxonomy of Returns |
Official Website of Reserve Bank of India"*, and its entire content is the one row the lane quotes.
`sankalan.rbi.org.in` and `cims.rbi.org.in` both → HTTP 200, **3,254 bytes**, `<title>CIMSLOGIN</title>`.
The India asymmetry is real.

**FFIEC is genuinely blocked, not a lane failure.** I re-tried three URLs with a full desktop Chrome
User-Agent: all **HTTP 403** (with a 244 kB block page). The lane's SECONDARY labelling on everything
FFIEC — including the *correct-or-explain* remedy split that Part 4 item 5 imports into the design — is
honest, and that quote remains **UNVERIFIABLE at primary source**. Do not put *correct-or-explain* in a
governance table as though it were read off a regulator's page.

### One framing challenge the numbers do not settle

Part 0's headline — *"**19,692** executable financial-reporting validation rules in the current-
generation EU supervisory sets alone"* — is arithmetically 12,925 + 6,767, and both addends are
confirmed. But **the two addends are different units.** The EBA's 12,925 counts rule × framework-version
*instances*; its distinct-rule count is **8,052**. EIOPA's 6,767 is a rule count. The lane discloses this
in its own parenthetical, which is to its credit — but the sentence still leads with a number built from
mixed denominators. **The defensible like-for-like figure is 8,052 + 6,767 = 14,819 distinct rules.**
That is still an order of magnitude more than "zero", so the refutation of the brief survives intact;
only the headline number needs restating. Quote **14,819 distinct** or quote **12,925 rule-instances**,
and never the sum of the two without the caveat attached in the same breath.

### Net effect on the design

Nothing in the architecture moves. The three findings that actually change the design — ESMA's
`Automatable` column refuting L7's novelty claim, SR 26-2's footnote 3 opening a governance vacuum
around L2/L3, and the EBA's 8.23%-with-343-blocking-errors justifying L4 — are all **CONFIRMED at
primary source by an independent pass**. The single refutation costs the lane a free L4 benchmark it
had not actually opened, which is a scoping correction rather than an architectural one.
