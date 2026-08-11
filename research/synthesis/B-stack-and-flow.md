# B — THE TECHNOLOGY STACK AND THE BACKEND FLOW

**Authoritative build specification, section B. Compiled 10 Aug 2026 from `RND-BRIEF.md`, `ARCHITECTURE.md`
and the fifteen research lanes in `/Users/abishaikc/Gift/research/lanes/`.**

Where this document disagrees with `RND-BRIEF.md` or `ARCHITECTURE.md`, **this document governs**, because
every disagreement below is a lane measurement against a primary source that the adversarial pass did not
refute. Every such override is named in §0.2 with its mechanism, so nothing is changed silently.

**Status labels used throughout, and they are load-bearing:**

| Label | Meaning |
|---|---|
| **BUILT** | Code exists on disk, has been run against the real published artifact, and the number quoted was produced by that run |
| **SPECIFIED** | Designed to the level of an acceptance test; not built |
| **GATED** | The build decision is deferred to a named, pre-registered measurement. The measurement, not a preference, decides |
| **REJECTED** | Considered and refused, with the reason recorded so nobody re-explores it |

**Warrant labels:** `MEASURED` (run by an operator or lane against the primary artifact) · `VERIFIED-AT-SOURCE`
(primary document opened and the value read off it) · `SECONDARY` (a credible source describes it; the primary
was not opened) · `MODELED` (derived by arithmetic from stated assumptions) · `NOT-VERIFIED` (could not check —
a legitimate answer, never smoothed over).

**A derived number never claims a stronger warrant than its weakest input.** Every fraction in this document
carries its denominator inline. Where a lane and its adversarial pass disagreed, §0.2 records which won and why.

---

## §0 — WHAT IS SETTLED BEFORE ANY TECHNOLOGY IS CHOSEN

### 0.1 The artifact, measured

All figures below are for `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`
as published on `ifsca.gov.in/Download`, `sha256 = 7d9a1960085785ee…`. They are the constants the build
asserts in a regression test, so that a parser regression is loud rather than silent.

| Quantity | Value | Warrant |
|---|---:|---|
| Sheets | 10 (9 protected, `Dropdown` unprotected **and** `state="hidden"`) | MEASURED, L13 §1.5, L14 §1.8 |
| `<c>` elements (all cells) | 6,757 | MEASURED, L14 §1.8 (exact) |
| Cells carrying a value | 3,740 | MEASURED, L08 §A.1 |
| **Formula-bearing cells** | **505** | MEASURED, L08 §A.2, L09 §A.0.2, L13 §1.2, L14 §1.4 (four independent reproductions) |
| — of which carry formula **text** | 294 | same |
| — of which are shared-formula dependents `<f t="shared" si="N"/>` | 211 (41.8%) | same |
| Cross-sheet formula strings | 195 of 294 (66.3%) | MEASURED, confirmed exactly by four lanes |
| **Checkable relations (SUM + COUNTIF), per cell** | **138 of 505 = 27.3%** | MEASURED, L08 §A.3, L09 §A.0.2, L13 §1.3 |
| Pure carries, per cell | 223 of 505 = 44.2% | same |
| **Data validations** | **54** (35 main namespace + 19 `x14` extension) | MEASURED, L13 §1.4, L14 §1.5 |
| — list-type with a named vocabulary | **22** | same |
| — resolving to a real enumerable vocabulary | **20** | MEASURED, L14 §1.9 |
| Vocabularies shipped on the `Dropdown` sheet | 15 | MEASURED, L09 §A.0.1(b), L13 §1.5 |
| Merged ranges | 252 | MEASURED, L05 §2 (three readers agree) |
| Defined names | 12 raw `<definedName>` elements; **4 point at `#REF!`** in the published blank | MEASURED, L13 §1.6 |
| Shared-string cells / with `len>3` / distinct `<si>` | 1,249 / 854 / 494 | MEASURED, L14 §1.7 |
| **Field surface (unlocked, non-formula) — the coverage denominator** | **3,747** | MEASURED, L14 §1.12 |
| Executable predicates harvested with no model — FME / all nine workbooks | **280 / 515** | BUILT, L14 §1.9 |
| Coverage of the field surface by those 280 | **63.3%** (2,373 of 3,747; 1,374 declared unchecked) | BUILT, L14 §1.12 |
| Embedded images across all nine workbooks | **0** (`xl/media/` empty, 9 of 9) | MEASURED, L08 §A.1 |

**Two defects in the regulator's own published blank template, both first-hand:**

1. `'1. Introduction'!D17` ("Total No. of Schemes of the FME authorised by IFSCA") is `SUM(D18:D20)` over three
   `COUNTIF` patterns that match **7 of the 9** terms in the template's own scheme-type vocabulary. **"Special
   Situation Fund" and "Family Investment Fund" are counted by nothing.** MEASURED, L09 §A.0.1(a), corroborated
   L06 §11, L11 §9.1.
2. `'4. Investors'` rows 2–17 are **hidden, formula-live, and duplicate table numbers 4.1 and 4.2** with a
   superseded block. MEASURED, L06 §7.3.

Both are checkable in one predicate each and both are the strongest demo material in the build. They are also
the proof that L3's criterion source is *available*, not *authoritative* — a predicate mined from `D17` inherits
`D17`'s defect and would pass a wrong filing while failing a right one.

### 0.2 Reconciliations — where lanes disagreed, and which instrument won

**The tie-break rule, and it is the project's own thesis applied to its own corpus:** where two readings of the
same file disagree, the reading produced by the *more capable instrument* wins, not the reading with more votes.
A namespace-blind reader cannot produce 54; a namespace-aware reader can produce both 35 and 54 and can say
which is which.

| Disagreement | Resolution | Mechanism |
|---|---|---|
| **35 data validations, 3 list-type** (RND-BRIEF §4.3; reproduced by L06 §11 and L09 §A.0.1(b)) vs **54, 22 list-type** (L13 §1.4, L14 §1.5) | **54 / 22 / 20-resolving governs.** | The 35 is the main-namespace count. `<x14:dataValidation>` lives in `extLst` and is invisible to both `r'<dataValidation[ >]'` and **openpyxl 3.1.5**, which emits only a `UserWarning`. L14 ran the regex proof: operator regex → 35, `x14` regex → 19, namespace-aware lxml → 54. L06 and L09 read through openpyxl and inherited its blind spot |
| **"294 formulas"** vs **505** | Both true of different quantities. **Report both, always: "294 distinct formula expressions across 505 formula-bearing cells."** | 211 shared-formula dependents carry no text node |
| **"38 of 294 (13%) express a checkable relationship"** as a claim about *the workbook's behaviour* | **REFUTED as a behavioural claim.** Per evaluating cell: checking arithmetic 27.3%, carrying 35.8% — comparable, not 1:5 | L13 §1.3. The arithmetic 38/294 = 12.9% is exactly right; it is a fact about authored expressions, not about cells |
| **The IFSCA register cannot resolve registration numbers** (L15 §3) vs **228 of 228 live FMEs have a non-empty RegistrationNumber** (L08 §C.3) | **L08 governs.** The *list* endpoint carries no registration numbers (confirmed three times: L15, L08, L12 adversarial #14). The *detail* endpoint does, keyed on **`EncryptedId`** | The payload carries two similarly-named fields: `EncryptDId` is `None` in 2,005 of 2,005 records; `EncryptedId` is populated in 2,005 of 2,005. L15 keyed on the first, got HTTP 302 on every record, and reported an absence. **This is a silent false negative produced between two of our own lanes, on the same endpoint, on the same day** — and it is now the fourth instance of the failure class the pitch is built on |
| FME population: **217 FMEs / 360 schemes** (IFSCA Q4 FY2025-26 bulletin) vs **229 live FMEs / 390 schemes / 650 Fund-Management register rows** (L08 §C.2) vs **~285 entity-like of 650** (L15 §5) | **Never blended.** Quote "217 FMEs and 360 schemes as at the Mar-2026 bulletin" or "229 live FMEs in the register as at 10 Aug 2026", with the rule and the date, never a blend | Different instruments, different as-of dates; the register carries branch and multi-capacity registrations the bulletin counts once. L13 §1.7 verified the bulletin figures at source |
| Field surface **3,747** (L14) vs unlocked cells **3,755** (L07 §9.1) | **3,747 is the denominator** (unlocked **and** non-formula). 3,755 is unlocked cells in used ranges, including unlocked formula cells | Different definitions of the same mask. The build asserts 3,747 and states the filter |
| "12 of 15 vocabularies unenforced" (L13 §1.5) vs L14's enumeration implying ≥9 wired | **UNRECONCILED — declared gap (§7.3).** The build computes the vocabulary→validation mapping and asserts it in a test. Nobody quotes either figure until it does | Multiple validations may point at one vocabulary; neither lane published the full mapping |

### 0.3 Numbers and claims that must never reappear

Removed or restated by lane measurement. Repeating any of these in a slide, a README or a code comment is a
build error, not a style problem.

| Must not be said | Say instead |
|---|---|
| "35 data validations, only 3 list-type" | 54 validations (35 main + 19 `x14`), 22 list-type, 20 resolving to a real vocabulary |
| "The workbook has 294 formulas" (alone) | 294 distinct formula expressions across 505 formula-bearing cells |
| "38 of 294 (13%) check anything — the workbook mostly copies values" | Per evaluating cell: 27.3% checking, 44.2% pure carry. The rhetorical point survives; the ratio does not |
| "L4 test 1 is mutation testing; use mutmut / PIT / Stryker" | **Seeded-defect adequacy.** Those tools mutate *code*; L4 mutates *data*. The harness is ours, ~200 lines, and it runs at 7,946 mutants/second |
| `MS = killed / (mutants − equivalent)` | `KR = K / O`, where `O` is mutants **measured by recalculation** to change at least one reported value. "Equivalent" is a theorem; "observable" is a diff |
| "Zero financial regulations are encoded anywhere" | EBA publishes ~12,925 validation rules and has deactivated 8.23% of them; EIOPA publishes 6,767 with a 243-item known-issues register; ESMA publishes 68 ESEF rules **with an `Automatable Yes/No` flag**; FINOS CDM/ISDA DRR carries 640 executable conditions; XBRL US DQC has run a false-positive-gated rule registry over SEC filings for a decade (L04, L09 §C.2) |
| "No analogue exists for a financial assertion" | ISA 705 (Revised) ¶24 and ISRS 4400 (Revised) ¶30(j) both require a declared boundary. What does not exist is a **per-item, machine-readable, schema-induced, per-check-error-rated** version (L10 §6.2) |
| "CycloneDX `compositions.aggregate` — a ten-state enum since 1.2" | Six states in **1.3**; ten in 1.5/1.6/1.7. And it is one header field, not the prior art — the per-item prior art is **XCCDF Table 26, NIST, 2012** (L10 §1.1, §2) |
| "PASC names financial documents as a target" | **Zero** occurrences of financial/finance/invoice/KYC/regulatory in the paper; its datasets are CoNLL-2003, WNUT-17, WikiNEuRal (L02 B-item 18, L07 §2.1) |
| "Adding memory made all 10 models worse" | The memory scaffold **never helped**: 6 of 10 hurt, 4 neutral within ±0.03 GDS, **all ten open-weight** (L02 B.10) |
| "Rounding tolerance costs 21 points of recall — that is the price of FP suppression" | −21.0 pp recall is correct, but **precision stayed 100.0 and FPR stayed 0.0**. It is a rendering artifact, not a trade-off (L02 B.6) |
| "Reuse SPADE" (as a dependency) | `shreyashankar/spade-experiments`: 17★, 1 fork, **no licence field**, last push 2024-04-07. Reimplement the ILP (~40 lines of PuLP/CBC); cite the paper (L03 §12.2) |
| "Reuse QuantMind for L0" | **Not adopted.** L0+L1 are ~200 lines of lxml measured at 28 ms. Do not take a 2.3k-star dependency to save 200 lines (L14 §9) |
| "The predicate registry grows monotonically" | Incompatible with re-qualification. **Coverage must be able to fall**, and the step-downs are the most credible thing on the coverage-over-time chart (L13 R6.4) |
| "Two model calls, both short" | **Zero model calls in the verdict path.** L3 is build-time and per-template-version; L2b runs only when an unstructured attachment exists (L13 M5, L14 §6.2) |
| "Coverage meter at the top: 71% of predicates settled" | 71% is the *decidability ratio* from a hand classification of 24 candidate predicates. It is not a coverage measurement of any filing. The demo shows what it computed: **63.3% of 3,747 fields** (L13 §10.5) |
| "17 of 24 predicates are script-settleable" | **15 exact + 2 approximate.** The two register predicates are fuzzy name/number matching with a non-zero false-failure rate by construction (L15 §4) |
| "Independent state verification took false success from 45–47% to 3% — a measured intervention" | A **hypothesis** the author explicitly declines to call causal: one dual-control domain, **n = 15 false-success cases**, confounds unresolved (L01 adversarial V.2) |
| "868 filings a year" (unqualified) | **MODELED**: 217 × 4, assuming every FME files every quarter including those registered mid-year (L13 §1.7) |
| "46% staffing" | Appears in no evidence table anywhere in the corpus. **Delete** (L13 §10.10) |
| "84 numeric / 15 date fields" | Not reproducible without the counting rule. 19 distinct labels contain "date". Withdraw both until the rule is written down (L14 §1.7, §1.13) |
| "The supervisor triages an inbox of 868 filings" | The supervisory system is **procured** (NEC Corporation India, 27 Jan 2026, ₹39,57,36,115.52, scope includes an RE-facing portal). *The supervisor is not the buyer; the supervisor is why the filer cares* (L13 R7.1) |

---

## §1 — THE DECISION TABLE

Every row is a decision, not an option. Each names the layer it serves, the runner-up it beat, the evidence
that decided it, and **the condition under which we switch** — stated as a testable trigger, not a feeling.

### 1.1 Master table

| # | Layer | **DECISION** | Runner-up it beat | Evidence for the choice | We switch when |
|---|---|---|---|---|---|
| 1 | **L0/L1 — workbook parsing (authoritative reader)** | **Raw `zipfile` + `lxml` 6.1.1 (BSD), namespace-aware, over `xl/worksheets/*.xml`, `styles.xml`, `sharedStrings.xml`, `workbook.xml` and `extLst`** | openpyxl 3.1.5 as the schema source | openpyxl sees **35 of 54** validations and reports the **AML-CFT sheet as having zero when it has five**; a hand-written regex reaches the identical wrong 35 by the identical mechanism. lxml gives a full parse in **28 ms** (L14 §1.6, §1.10) | Never for schema induction. This is a hard rule with a regression test asserting 54/22/505/3,747 |
| 2 | **L0/L1 — shared-formula expansion (second reader)** | **openpyxl 3.1.5 (MIT), `data_only=False`, for formula text with correct row-shifting; and `data_only=True` for cached values** | Hand-rolling `si`→master translation in reader A | openpyxl returns the *translated* dependent formula (`O4 → =SUM(C4:N4)`), which is exactly what a hand-rolled reader gets wrong even when it notices the dependent exists (L08 §A.5). Cost 202 ms | We write and mutation-test our own translator. Until then openpyxl is used **only** for formulas and cached values, **never** for validations, and **never** to re-serialise (round-trip loses 98.2% of bytes and every `x14` validation — L05 §2.2) |
| 3 | **L0 — third reader / normaliser (cross-check only)** | **LibreOffice headless (MPL-2.0), `--convert-to xlsx`, run in the sandbox tier, as the third leg of a triple-reader agreement check** | Adopting LibreOffice normalisation as the primary analysis path (L05 §9.1's recommendation) | LO expands all 505 formulas to text and migrates `x14` validations into the main namespace — it "sees the truth". **But L05's own residue records that LO writes 53 where 35+19 = 54: one validation lost, unexplained, in the very step being recommended.** A normaliser with an uncharacterised loss cannot be the authority | The 53-vs-54 loss is characterised and shown to be a duplicate-sqref merge. Then LO may be promoted from cross-check to normaliser |
| 4 | **L1 — schema induction** | **Ours (`wb_probe.py` / `predicate_harvest.py`), ~200 lines over the OOXML cell graph** | QuantMind (MIT, 2.3k★) | BUILT: 28–44 ms, emits 505 formula cells, 54 validations, 3,747 field-surface cells, 280 executable predicates for the FME workbook and 515 across nine (L14 §1.9, §1.10). QuantMind's shapes are research artifacts (Papers/News/Earnings/Factors/Theses); brief §9.7 asked whether they extend to a protected xlsx and **the question is moot at 200 lines** | Never for this artifact class. Revisit only if the ingest surface expands to research documents |
| 5 | **L1b — regulation-text parsing** | **Docling (MIT, 64,531★, pushed 2026-08-10) → `DoclingDocument`, with per-element `ProvenanceItem{page_no, bbox, charspan}` and per-cell `TableCell` offsets** | MinerU (77,270★) | Docling publishes a **typed, versioned, per-cell provenance schema** with an explicit `coord_origin` enum — the only one in the field. MinerU's `LICENSE.md` is Apache-2.0 **plus riders**: §2 requires prominent attribution for any online service built on it — a live obligation, and "Apache-2.0" on a slide would be wrong (L08 §B.1, §B.2, §B.3) | Docling's table fidelity blocks a needed clause. Then PaddleOCR-VL (Apache-2.0, 0.9B, rank 1 on OmniDocBench v1.6_full) becomes primary and Docling the cross-check |
| 6 | **L1b — scanned-circular fallback** | **PaddleOCR-VL (Apache-2.0, 87,345★) for the 10 of 399 circulars that are scanned images** | olmOCR (7B), Marker, Nougat | 2.5% of the corpus, where generation genuinely is hard. Marker is the **worst table row on OmniDocBench v1.6_full (TEDS 65.77)**; olmOCR and Nougat linearise to Markdown, which destroys the anchor, and Nougat is 18 months without a push (L08 §B.1, §B.4) | The 10 unreadable circulars are OCR'd once, offline, and the output frozen. This is an afternoon, and the alternative is carrying `coverage_gap: 10/399 sources unread` on every predicate whose correctness rests on the §4.1 negative result (L13 R6.7) |
| 7 | **L1b — clause identity and citation** | **Akoma Ntoso / OASIS LegalDocML: `eId` per clause + FRBR URI per instrument; a deterministic promoter from `DoclingDocument` → AKN** | Inventing a clause-key scheme | An OASIS Standard whose Naming Convention is *designed* for amendment commands; the operator measured **866 dated cross-references in 58.6% of circulars** and **76 of 82 amending circulars citing a resolvable target (92.7%)**, so the amendment graph is machine-followable. Without `eId`, L3's "the clause it implements" is an unresolvable free-text string and L5 cannot cite (L08 §E.1, §E.5) | Never. This is settled prior art |
| 8 | **L1b — FRBR URI handling** | **Implement `cobalt`'s URI grammar ourselves (~100 lines) unless its licence clears** | Depending on `laws-africa/cobalt` | GitHub reports **NOASSERTION** for both `indigo` and `cobalt`; the lane did not open the LICENSE files. Sibling `bluebell` is **GPL-3.0** and must not be linked into a commercial product (L08 §E.2, open question 4) | Someone opens `cobalt`'s LICENSE and it is permissive. Then depend on it. We adopt **Indigo's amendment/point-in-time data model** either way; we do not adopt the Indigo platform (77★, Django-shaped, built for a curated human editorial workflow) |
| 9 | **L1b — citation anaphora (`the said circular`)** | **Ours, modelled on `eyecite`'s antecedent-resolution architecture** | Adopting `eyecite` (BSD-2-Clause, 267★) | eyecite's resolution power is entirely in `reporters-db`/`courts-db` — **US case reporters**. It has no knowledge of `IFSCA/GN/2025/…` and would resolve approximately nothing. The *algorithm* transfers; the data does not (L08 §E.3) | An Indian statutory-citation library is found. **L08 declares it did not search the Indian legal-tech ecosystem at all** — that search must run before any novelty claim on IFSCA citation resolution |
| 10 | **L3/L5 — predicate language** | **CEL (Common Expression Language), admitted subset only, in a three-slot envelope (`applicable` / `expr` / `witness`)** | Plain Python + pandera | Four independently decisive reasons (L09 §A.7): **(i) coverage is statically computable only because the language has no variables** — the headline number becomes derived rather than estimated; (ii) executing model-written Python requires a sandbox, and the sandbox layer is where the 2026 CVEs are; (iii) a predicate library an auditor inspects must show a rule, not a function body; (iv) mutating a 20-production grammar has enumerable operators. Precedent: **Kubernetes ValidatingAdmissionPolicy, GA in v1.30** — model-free CEL policy over structured data, in-process | A predicate class arrives that the admitted grammar cannot express **and** that cannot be quarantined into a host function. Rego becomes the answer only if the stack moves to Go |
| 11 | **L5 — CEL runtime** | **`celpy` (`cloud-custodian/cel-python`, Apache-2.0, 171★), pinned by PyPI name `cel-python` and wheel hash** | `cel-expr-python` (`cel-expr/cel-python`, Apache-2.0, 76★) | Pure Python, no C++ build, trivially auditable, years of use inside Cloud Custodian. **Naming trap: two different projects both live at a path called `cel-python`** — pin by PyPI name and hash or you will get the wrong one (L09 §A.2) | `celpy` fails the CEL conformance suite on **error semantics specifically** — which is where our `&&`/`||` absorption guard lives. Both must be run against the conformance suite before commitment (L09 open question 5). `cel-expr-python` wraps the official C++ and inherits conformance by construction; it is the drop-in |
| 12 | **L5 — arithmetic representation** | **Money carried as an `int64` count of 10⁻³ USD Million (1 unit = USD 1,000). A 2-dp filing value `12.34` becomes `12340`. Half-ulp = 5 units. `τ(n) = 5n`** | `double` (CEL's only numeric type), or `Decimal` outside CEL | CEL has **no decimal type**. Guidance C111 fixes values at 2 decimal places on USD Million, so the quantum is USD 10,000 and the lawful per-cell slack is USD 5,000. Left as `double`, every arithmetic predicate acquires a floating-point false-failure rate we did not choose and cannot attribute (L09 §A.7(d), L06 §7.2(5)) | Never. This is a schema requirement and it is cheap only if done at the start |
| 13 | **L5 — the tolerance model** | **`τ(n) = n × 0.005 USD Million = 5n units`, declared inside each predicate and versioned with it. Rounding `ROUND_HALF_UP`, never Python's banker's rounding. Counts get zero tolerance** | A constant epsilon | A constant epsilon is the single most likely source of spurious L6 and L5 failures (L06 §9, §11). Two predicates differing only in tolerance are two registry entries with two measured FFRs, and the library shows both — which is what makes the tolerance a *measured parameter* rather than a hidden constant | Never |
| 14 | **L5 — recalculation engine** | **Ours: a topological evaluator over the induced cell graph in `Decimal`, implementing the workbook's entire function vocabulary — `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)`, direct refs. Eight functions** | `formulas` 1.3.4 | Three reasons: **licence** — `formulas` is **EUPL 1.1+** and `pycel` is **GPL-3.0**, both copyleft with a live network-deployment question for a hosted product (L05 §2.4, adversarial #7); **method** — importing someone else's evaluator imports an unmeasured error rate that L4 would have to reject on its own rules (L08 §A.6); **and building it is itself the differential arm of MR-19**, the only check that detects a filer overwriting a formula cell with a literal (L06 §10.1) | The function vocabulary of a newly admitted template exceeds what we can implement exactly. Then adopt `formulas` **behind a completed licence review**, or route recalculation through LibreOffice and carry the engine's own disagreement rate inside the predicate's FFR |
| 15 | **L5 — second recalculation engine (differential)** | **LibreOffice headless, in the sandbox tier. Where the two engines disagree on a recomputed cell, every predicate reading that cell returns `INDETERMINATE(engine_disagreement)` — never PASS, never FAIL** | Trusting one engine | An independent benchmark puts LibreOffice's recalc-exact rate at 91.9% on FUSE — but the adversarial pass found that repo is a **three-hour, unreplicated, self-graded vendor artifact** (19 commits in one morning, top entrant is the repo owner's product) and ruled the number **evidentially void** (L05 adversarial #4). We therefore do not quote a floor; we **measure disagreement per cell, per run**, and report it | The two engines are shown to agree on the full 505-cell graph across the clean corpus, with a positive control on `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101`. Then the second engine moves offline |
| 16 | **L4 — degeneracy prover** | **Z3 (MIT) for L4 test 2: trivially-true iff `¬P` is UNSAT; always-flag iff `P` is UNSAT; subsumption iff `P₁ ∧ ¬P₂` is UNSAT** | Empirical degeneracy testing alone | It is literally a satisfiability question, CEL's comparison fragment maps to SMT-LIB almost one-to-one, and Z3 returns a **model** — a concrete counterexample workbook that goes into the predicate library as evidence (L09 §A.3) | Never removed, but **never trusted alone**: host functions are uninterpreted to Z3, and Z3's string theory can return `unknown`. **`unknown` is treated as UNCHECKED, never as "non-degenerate."** The empirical control arm (§3.5) runs regardless |
| 17 | **L4 — fault-seeding harness** | **Ours, ~200 lines over the cell graph. Operators: Abraham & Erwig's 17 spreadsheet mutation operators (IEEE TSE 35(1):94–108, 2009) plus F12 vocabulary drift, F13 carry desynchronisation, F14 vocabulary-gap exploitation** | mutmut / PIT / Stryker | **Category error**: those mutate source code and re-run a test suite. Our mutants are *data*; the subject under evaluation is the *predicate set*. BUILT and measured: **19,782 mutants in 2.5 s = 7,946 mutants/second** (L14 §1.11, L09 §C.1) | Never. mutmut 3.7.0 (BSD-3-Clause, 31 Jul 2026, requires `fork`) is retained one level up — for mutating **our own** host functions, the L1 inducer and the profile checker (L09 §C.6) |
| 18 | **L4 — scoring** | **`KR = K/O` reported with both integers, plus the unobservable rate `U/G`, plus the per-fault-class vector. Never a bare percentage** | `MS = killed/(mutants − equivalent)` | Abraham & Erwig measured **3,512 of 7,500 (46.8%)** of comparable spreadsheet mutants as *irreversible* — no observable change. A kill rate over generated mutants understates every predicate by roughly half, variably by operator mix. Observability is a **diff**; equivalence is a theorem (L09 §C.2, §C.5) | Never |
| 19 | **L4 — registry minimisation** | **Reimplement SPADE's ILP in PuLP/CBC (~40 lines): `min Σxⱼ s.t. Coverage(F′) ≥ α, FFR(F′) ≤ τ`, with the interaction bound `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`** | Depending on `shreyashankar/spade-experiments` | 17★, 1 fork, **no licence field**, last push 2024-04-07. An unlicensed repository is legally unusable in a commercial product regardless of its quality. Measured ILP runtimes 0.1–1.2 s on thousands of variables (L03 §12.2) | Never |
| 20 | **L4 — interval statistics** | **Wilson score interval on every rate, ~8 lines. A point estimate is forbidden by schema** | statsmodels; or a bare percentage | `0 fires / 340 clean → [0.000, 0.011]`; `0 fires / 4 real → [0.000, 0.490]`. **A real FFR from 4 real filings with an interval of [0, 0.49] is more honest and more useful than 0.0% from 340 self-authored ones** (L13 Attack 4) | Never |
| 21 | **L6 — metamorphic / differential execution** | **`Hypothesis` `RuleBasedStateMachine`: `@invariant` for *necessary* relations (violation ⇒ FAIL), in-rule assertions for *expected* relations (violation ⇒ advisory). `max_examples = 50`** | Hand-rolled transformation loops | The necessary/expected split is done by the library rather than by us, which is what stops it being a convention. Ravi & Coblenz: **55% of mutations found at n=1, 76% within the first 20 inputs** — the input space here is small and fixed, so 50 beats Hypothesis's default 100 and beats a fuzzer's millions (L06 §5.1, §10.2, §10.3) | Cross-table set relations multiply past what a CEL one-liner expresses. Then Soufflé/Datalog (UPL-1.0) enters — at the cost of a second toolchain and a second sandbox |
| 22 | **L6 — relation authorship** | **Human, read off the artifact's own formula graph and guidance notes. No model.** | Asking a model for metamorphic relations | Measured: LLM-generated MRs score **"markedly low" on novelty** — they recapitulate the textbook classes, which is exactly how the brief arrived at its five, of which **four false-alarm on a correct filing and the fifth is vacuous** (L06 §0, §3.4, §8). Every relation worth having came from a guidance note, a `COUNTIF` pattern, or a hidden `IF` branch | Never. This is the one layer where the model is measurably worse than a person with the file open |
| 23 | **L2b — conformal / abstention library** | **`crepes` (BSD-3-Clause, 581★) for the calibration core with `MondrianCategorizer`; `MAPIE` (BSD-3-Clause, 1,578★) for the sklearn-shaped surface and its `OnlineMartingaleTest`. RAPS score over L1's key set. — BUILD GATED, see below** | `TorchCP` (475★) | TorchCP is **LGPL-3.0**: relinking/source obligations the BSD pair does not carry. `nonconformist` is dead (no push since 2021-03-20); `Fortuna` is **archived** by AWS. `puncc` ships no root LICENSE file (MIT confirmed only from `pyproject.toml`) (L07 §8) | **The gate, pre-registered:** measure key-binding accuracy `μ` on cross-document binding. Forced abstention is `r ≥ (μ−α)/(1−α)`. **If `μ > 0.30`, do not build the conformal layer** — at α=0.05 it forces ≥26.3% abstention from base error alone, and the honest product is "cross-document binding is UNCHECKED(requires judgment)". If `μ ≤ 0.10`, build it. Between, build it and ship the **abstention rate** as the headline, not coverage (L07 §9.5) |
| 24 | **L2b — structured output** | **Provider-native structured outputs (`output_config.format`) on Anthropic models, with the `key` field typed as `Literal[*L1_KEYS]`. Retry disabled and, if ever enabled, counted into provenance** | `outlines` / `XGrammar` (Apache-2.0) | The key is not a free string; it is an enum over exactly the keys L1 induced, so an off-schema key is **ungeneratable**, not merely rejected. `outlines`/`XGrammar` mask logits and are strictly better — but they require a local model. Keep both guards: generation-time impossibility *and* the post-hoc deterministic check, because the latter is what you can prove to an auditor (L08 §F.2) | A local open-weight model enters the L2b path. Then `outlines` becomes primary. **Instructor-style retry-until-valid is banned outright**: retry is exactly what `pass^k` penalises, and a library that silently retries and returns the first parse that validated is manufacturing the clean verdict this product exists to refuse (L08 §F.4) |
| 25 | **Model provider** | **Anthropic** | Open-weight local | The comparison is **NOT-VERIFIED** — L14's discovery budget was exhausted and a guessed URL is the fabrication this brief forbids. **The architecture converts this into a measurable question instead of a guess:** L4 adjudicates every candidate deterministically, so *model choice cannot affect correctness, only yield*. Measure **admitted predicates per unit cost** and **admitted per 100 candidates** (L14 §6.3) | The measurement, run inside experiment 9.1 where the harness already exists, says otherwise. Re-run whenever the line-up changes |
| 26 | **Model per step — L3 candidate proposal** | **`claude-opus-5` ($5/$25 per MTok), via the **Batch API** (50% off both directions) with prompt caching (5-min write 1.25×, cache read 0.1×; the discounts stack). Offline, once per template version** | `claude-sonnet-5` | L3 generates candidates that L4 adjudicates, so a bad candidate costs a rejection, not an error — the ideal place to spend on capability. It is offline (latency irrelevant → Batch applies) and the template schema is a large stable prefix (→ caching applies). **The failure mode being bought down is a plausible-but-wrong check** (L14 §6.2) | Experiment 9.1 measures admitted-per-rupee and Sonnet 5 wins. Cost is so low either way (§5) that capability decides until measurement says otherwise |
| 27 | **Model per step — L2b attachment extraction** | **`claude-haiku-4-5` ($1/$5) for the bulk pass, escalating to `claude-sonnet-5` when the conformal set is not a singleton** | Opus 5 for everything | L1's hard guard makes L2b's failure modes cheap: a wrong key is *caught*, a non-singleton set *abstains*. A cheap high-volume pass with a capable escalation path is the economically right shape. **And L2b is not on the critical path for the workbook at all** — a filing with no attachments has a marginal model cost of exactly **$0.00** (L14 §6.2) | Escalation rate exceeds ~30%, at which point promote the bulk model rather than paying twice |
| 28 | **Model per step — L5, L6, L7, the verdict** | **No model. Anywhere. Ever.** | LLM-as-judge | LLM judges detect false success at **AUROC ≤ 0.65, 13% recall at a 10% flag rate**; a TF-IDF + logistic-regression classifier over the same trajectories reaches 0.825–0.953 AUROC at **3,364× lower latency**. And even that detector runs at **50% precision at a 10% flag rate** — half the flags wrong (L01 adversarial V.4). A model may never be the final adjudicator | Never. This is enforced at the schema level: `MODEL_EXTRACT` may never be the sole `method` on a `PASS` (L10 §7.4) |
| 29 | **Data-validation substrate (the verdict model)** | **Ours. There is no substrate to adopt.** `pandera` 0.32.1 (MIT) is adopted **only** as a host-function implementation for bulk column checks | Great Expectations / Soda Core / dbt tests / Deequ | **Great Expectations is disqualified on semantics:** with `catch_exceptions=True`, *"execution will not fail if the Expectation encounters an error. Instead, it will return `success = False`"* — the same value it returns when it evaluated and the data was wrong. **A framework that folds *could-not-check* into *failed* destroys the coverage denominator**, which is the entire product. Its result schema has no field for "not applicable", "out of scope" or "no oracle exists". **Soda Core is disqualified on licence** — Elastic License 2.0, verbatim: *"You may not provide the software to third parties as a hosted or managed service…"*. dbt tests are two-valued by construction and need a warehouse (L09 §A.1) | Never for the verdict model. The brief's line *"do not rebuild Great Expectations / pandera / Soda Core"* must be read as: **do not rebuild the check library; you must build the verdict model, because it does not exist anywhere in the ecosystem** |
| 30 | **L3 — model-free baselines (mandatory, run before the model)** | **B0 the template's own 138 checkable relations · B1 Daikon (260★, ships a CSV front end) over the clean corpus · B2 the degenerate arm ("no cell blank, no cell errors")** | Running L3 without baselines | In this literature **the free baseline beats the neural method more often than not**: SPADE's select-all yields 100% coverage at 100% FFR; TOGA's `NoException` baseline gets **68.9% of TOGA's bugs at 2× the precision**. **If L3 does not beat B0 ∪ B1 ∪ B2 on marginal kill at equal FFR, it has produced nothing**, however many predicates survive (L03 §11.5, §12.4) | Never. The baselines are permanent, and Daikon's trivia output doubles as the degeneracy list |
| 31 | **Sandboxing — parser tier** | **gVisor (`runsc`) + `seccomp` + `--network=none` + read-only rootfs + size-capped tmpfs + non-root uid + `no-new-privileges` + `RLIMIT_AS`/`RLIMIT_CPU` + wall-clock kill. Zip guards **before** parse (entry count, per-entry uncompressed size, total ratio). `lxml` with `resolve_entities=False`, no DTD, no network** | Firecracker | **The threat model is a confused model and a malformed file, not a hostile attacker** — but the *filer* is genuinely hostile-capable, and an `.xlsx` is a zip of XML: zip bombs, XXE, billion-laughs, quadratic blowup. **The parser, not the predicate, is the exposed surface.** Firecracker buys hypervisor-grade isolation against an adversary we do not have and costs a VM per filing (L09 §B.1, §B.3, §B.4) | Multi-tenant SaaS with untrusted tenants. Then Firecracker. **E2B is rejected permanently**: a managed remote sandbox means the filing leaves our boundary, which is a data-residency conversation about IFSCA-regulated filings that we should not have to have |
| 32 | **Sandboxing — evaluator tier** | **An ordinary process. CEL is terminating, side-effect-free, has no I/O and binds exactly two names. There is nothing to sandbox: the language *is* the sandbox.** Plus a per-predicate cost budget (celpy step counter) and a wall-clock kill | Pyodide / WASM; RestrictedPython | **WASM-of-CPython is a resource boundary, not a security boundary.** Grist/"Cellbreak" (`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, patched 20 Jan 2026): a spreadsheet formula escaped Pyodide by **three independent routes**, and the fix was to run Pyodide *under Deno's permission system*. RestrictedPython's own docs say it *"is not a sandbox system or a secured environment"* (L09 §B.2, §B.3). **Correction that must travel with this: CVE-2026-5752 is against Cohere Terrarium, not Pyodide, and "Pyodide is unmaintained" is a conflation — it is MPL-2.0 with 14.8k★ and active governance** | If predicates ever run client-side, Pyodide returns as a *portability* layer only. If we ever compile the evaluator to WASM, `wasmtime`'s **deterministic fuel metering** is exactly the right shape for a reproducible cost budget |
| 33 | **Storage and content addressing** | **SQLite (public domain) + a `blobs/sha256/<aa>/<rest>` directory. sha256 over exact received bytes, lowercase hex, plus a per-sheet hash of every `xl/worksheets/sheetN.xml`** | PostgreSQL | **SQLite is a file, so it can be hashed and named in the run manifest** — which is exactly what L7 needs. A Postgres cluster cannot be content-addressed. Postgres wins on a concurrency this project does not have and costs a service to run, back up and reproduce. Per-sheet hashes let a re-derivation say *which* sheet changed (L14 §5.3, L08 §A.6) | **A second concurrent writer exists.** That is the trigger — not row count, not data volume. §5.4 says what actually breaks first at 100× and in what order |
| 34 | **Attestation and signing** | **DSSE envelope + in-toto Statement v1 (`payloadType: application/vnd.in-toto+json`), `subject[]` carrying **both** the filing digest and the template digest, `predicateType: https://<ns>/filing-coverage-attestation/v1`. Signed with a local Ed25519 key via `cosign sign-blob --key … --tlog-upload=false`** | JWS / JSF (CycloneDX's own signing), or Sigstore keyless with Rekor | in-toto/DSSE is Apache-2.0 and is what cosign, SLSA VSA and the whole attestation ecosystem already speak; `subject[]` naturally carries the two hashes we must bind, and **a verdict against template v3 is meaningless if the entity filed on v4** (L10 §7.1). **Rekor is a public transparency log** — a filer's attestation must never be published to it (L10 §5.6, §9.3) | The Sigstore public-good-instance policy on logging, retention and identity disclosure is opened and read. Until then, keyed mode with the transparency log off, and **`--tlog-upload=false` asserted in a test** |
| 35 | **Report schema — result vocabulary** | **8 states × 30 namespaced reason codes (§4.5), with `override` orthogonal (XCCDF Table 27) and a `BLOCKING | ADVISORY` severity tier determined by measured FFR** | The brief's `PASS / FAIL / UNCHECKED` × 6 flat reasons | Without `OUT_OF_SCOPE` **the coverage fraction is computed against the wrong denominator on every real filing**, because 217 heterogeneous FMEs will not populate all 10 sheets. Without `ERROR`, a crashing predicate is indistinguishable from a philosophically-uncheckable property. Without `no_predicate.failed_qualification`, L4's rejections are discarded — which is precisely the counter-evidence PCAOB AS 1215 .08 makes mandatory (L10 §8, L13 SC-3) | A new code is admitted **iff it implies a different remedy** from every existing code. That test is why 30 beats 6 and also why it is not 60 |
| 36 | **API framework** | **FastAPI 0.141.1 (MIT)** | Litestar 2.24.0 (MIT, 11 Jun 2026) | **Not a performance argument.** Litestar is the better-engineered framework for a large application; every one of its advantages pays off at a scale this project will not reach inside 60 days. The job is ~12 endpoints over a sub-second computation, so throughput is irrelevant by three orders of magnitude, and the binding constraint is **how fast a mentor, a teammate or a judge can read the code**. Django-ninja is rejected outright: it puts a migration between us and a reproducible report (L14 §5.2) | The team already knows Litestar. The switching cost is the only real cost either way |
| 37 | **Job execution** | **Synchronous request/response. No queue, no broker, no worker pool.** Offline sweeps run from a `Makefile` + the Anthropic Batch API | Celery / Redis / RQ | Measured: the whole deterministic pipeline is **~30 ms**, and the 19,782-mutant L4 campaign is **2.5 s**. The question "do we need a queue for a sub-60-second job" does not arise for a sub-second job (L14 §1.10, §5.2) | If in-process queuing is ever genuinely needed, use a **SQLite- or Postgres-backed job table before adding a broker**. Do not add Redis to a system whose unit of work is 30 ms |
| 38 | **Frontend — the report** | **A single self-contained HTML file: inline CSS and JS, no external requests, generated server-side** | Next.js + shadcn/ui | Four grounds no framework can match: it **opens from `file://` with the wifi down**; it is phone-safe with no build target or hydration; it is **emailable**, which is how a compliance officer actually shares a report; and — decisively — **it is the attestation artifact. A file has a hash. A single-page app does not** (L14 §5.4). React requires a build, a second deploy target and an API boundary a server already rendering HTML does not need | Never for the report. **SvelteKit is the post-residency answer for the shell** — single build artifact, and `adapter-static` can even emit the self-contained report. Streamlit, Reflex and NiceGUI are rejected permanently: all three bind the UI to a live session, which is exactly wrong for an artifact that must survive being emailed, hashed and signed |
| 39 | **Frontend — the interactive shell** | **Jinja2 templates from FastAPI + Tailwind compiled to a static stylesheet + ~50 lines of vanilla JS** | Any SPA framework | Five screens, ≤515 rows in the largest table. A plain `<table>` with a filter input renders 280 rows in under 200 ms; TanStack Table is overkill below ~5,000 registry rows (L14 §5.4) | The predicate registry passes ~5,000 rows |
| 40 | **Deployment** | **One Docker container on Fly.io (`shared-cpu-1x`, 512 MB ≈ **$3.32/mo** ≈ ₹290/mo). The laptop is the demo path and is mandatory as the fallback** | Vercel + Railway | Two deploy targets, two failure modes, two dashboards — and Vercel's serverless model actively fights a long-lived predicate registry file and a content-addressed blob directory. Splitting a 30 ms computation across a network boundary buys nothing. **New Fly.io accounts get no free allowance** (legacy free tier closed to organisations created after 7 Oct 2024) (L14 §5.5). Kubernetes at this scale would itself be evidence against the feasibility criterion | The deployed instance acquires a second concurrent writer or a real availability obligation |
| 41 | **Observability** | **The run manifest, content addressing end to end, a structured JSONL log (one line per predicate evaluation: `{predicate_id, verdict, reason, cells_bound, elapsed_us}`), and the `verify` command** | OpenTelemetry / Sentry / Prometheus | The system is sub-second and single-node; distributed tracing would be theatre. **The question a supervisor asks is not "what was the p99" but "can I get this same answer again", and `verify` answers it** (L14 §5.6) | A real user is on the system. Not before |

### 1.2 The four choices most likely to be challenged, argued at length

**(a) "Why a restricted expression language instead of Python? Everyone writes checks in Python."**

Because the product's headline number is a *coverage fraction*, and a coverage fraction is
`|covered ∩ in_scope| / |in_scope|` where `covered = ⋃ {P.schema_keys : P evaluated}`. That union is exact only
if the set of fields a predicate reads is **statically extractable from its text**. CEL has no assignment, no
loops and no user-defined functions, so an AST walker recovers the exact read-set and the envelope's declared
`schema_keys` can be **machine-checked against it at admission** — a predicate that reads a key it did not
declare, or declares one it does not read, is rejected. In Python the read-set requires taint analysis and the
answer becomes an estimate. `RND-BRIEF` §4.4 is a monument to what happens when a deterministic program's
coverage claim is inferred rather than derived. **The coverage meter is not a UI feature; it is a language
requirement that propagates all the way down** (L09 §A.6.5).

The honest cost: 13 of the 17 decidable predicates are pure expression evaluation; **four are not** (live
register lookup, GSTIN check digit, template-hash comparison, regulation-conditioned date arithmetic). Those
become **host functions** — named, deterministic, individually versioned Python functions with their own test
suites and their own mutation scores, added **only by a human, never generated by a model**, and each required
to return a third value wherever its answer can be unknown. The impurity is quarantined into a small enumerable
set, and a predicate calling an unregistered function is rejected at admission (L09 §A.8).

**(b) "You are choosing CEL, whose `||` swallows errors. That is the exact bug you claim to prevent."**

Correct, and it is the sharpest edge in the stack. The CEL specification states that for `&&` and `||`, *"if any
of their operands uniquely determines the result … the other operand may or may not be evaluated, and if that
evaluation produces a runtime error, **it will be ignored**."* So `true || <error>` evaluates to `true`: a
predicate can return PASS while silently swallowing an operand that could not be evaluated at all.

The mitigation is **structural, not documentary**. Before `expr` runs, the evaluator pre-flights every key in
`P.schema_keys` for presence and type against the fact model. Any key absent or mistyped yields
`NOT_RUN(source_unreadable: <k>)` **before evaluation begins**. Because `schema_keys` is machine-checked against
the AST, the pre-flight set is exact and not an estimate. The guard therefore does not depend on how the
predicate was written (L09 §A.6.4 rule 2). This is asserted by a unit test that feeds a predicate an unreadable
operand behind a short-circuiting `||` and requires the result to be `NOT_RUN`, not `PASS`.

**(c) "Why write your own formula evaluator when two exist on PyPI?"**

Licence and method. `formulas` 1.3.4 is **EUPL 1.1+** and `pycel` 1.0b30 is **GPL-3.0** — both copyleft, both
with an unresolved network-deployment question for a hosted commercial product, and the lane that measured them
flagged both with an explicit legal gate (L05 §2.4, adversarial verdict #7 CONFIRMED). Beyond licence: adopting
someone else's evaluator imports an error rate we did not measure, into the one layer whose entire claim is that
every check carries its measured error rate — **L4 would have to reject it on our own rules.** And the
reimplementation is not overhead: it is the second independent implementation whose disagreement with IFSCA's
own formulas *is* the detector (MR-19). The function vocabulary is eight functions over 505 cells.

**(d) "No queue, no Postgres, no React — isn't that under-engineering?"**

The measurements are: L1 schema build 28–44 ms; clean-filing synthesis 1 ms; L5 evaluation of 227 arithmetic
predicates sub-millisecond; full structural probe of all nine workbooks well under 1 s; 19,782 mutants in 2.5 s.
The durable state is a few hundred registry rows and a directory of blobs. **A queue, a cluster and a client
framework would each add a failure mode to a system whose unit of work is 30 ms.** §5.4 states, in order,
exactly what breaks first at 100× volume and what the replacement is — so the decision is reversible on a named
trigger rather than defended as a taste.

---

## §2 — THE ADOPTED OPEN-SOURCE LEDGER

One entry per adopted project. Each states **what we use it for**, **what we deliberately do not use it for**,
its **licence and the commercial implication**, its **maintenance risk**, and the **fallback if it is
abandoned**. Star counts and push dates are VERIFIED-AT-SOURCE via the GitHub REST API on 10 Aug 2026 unless
marked otherwise. Where a lane could not open a LICENSE file, this ledger says so rather than assuming.

### 2.1 Core — on the verdict path

**`lxml` 6.1.1 — BSD**
- **Used for:** every authoritative read of OOXML. Sheet XML, `styles.xml` (the unlocked mask that fixes the
  coverage denominator), `sharedStrings.xml`, `workbook.xml`, and the `extLst` block where the 19 `x14`
  validations live. Also XML hardening: `resolve_entities=False`, no DTD, no network.
- **Not used for:** spreadsheet semantics. lxml has no notion of a formula, a style resolution or a shared-formula
  group. Every one of those is our code.
- **Licence:** BSD. No obligation for a commercial hosted product.
- **Maintenance risk:** minimal. C-backed, decades old, the default XML stack in Python.
- **Fallback:** Python's stdlib `xml.etree` with manual namespace handling, at a measurable speed cost. The
  parse is 28 ms; a 5× slowdown is survivable. The schema logic is ours and does not move.

**`openpyxl` 3.1.5 — MIT**
- **Used for:** exactly two things. (1) Reading formula text with **correct row-shifting of shared-formula
  dependents** — `O4 → =SUM(C4:N4)`, which a hand-rolled reader gets wrong. (2) `data_only=True` cached values,
  which are present on **505 of 505** formula cells and are the recomputation baseline. Plus one offline use:
  writing mutant workbooks in the fault-seeding harness.
- **Not used for, and this is a hard rule with a test:** deriving the schema; reading data validations; reading
  defined names as the authority; and **re-serialising the artifact anywhere in the pipeline**.
- **Why the rule exists:** openpyxl sees **35 of 54** validations, silently drops all 19 `x14` entries, and
  **reports the AML-CFT sheet as having zero data validations when it has five** — with a `UserWarning` that is
  invisible in a batch pipeline. Its round-trip destroys **98.2% of the file's bytes** (3,663,391 → 65,877), 24
  of 42 parts, including the 3.55 MB Power Pivot model and every `x14` validation. **If the pipeline ever
  re-serialises with openpyxl, the hash L7 attests over is a hash of something that is not the filing.**
- **Licence:** MIT. Clean.
- **Maintenance risk:** low. It is the ecosystem default, which is also precisely why its blind spot is the best
  pitch material in the build — the failure is not ours and needs no defence of our code.
- **Fallback:** implement `si`→master shared-formula translation over lxml (≈80 lines: resolve the `si` index,
  compute the row/column delta from `ref`, shift every relative reference). Mutation-test it before trusting it;
  the row-shift is the part that silently goes wrong.

**`celpy` (`cloud-custodian/cel-python`) — Apache-2.0, 171★, 40 forks**
- **Used for:** evaluating the admitted CEL subset for `applicable`, `expr` and `witness`, with a step-counter
  cost budget per predicate.
- **Not used for:** anything outside the admitted grammar (§1.1 row 10). Nested comprehensions, `filter()`
  outside `witness`, `map()` outside `sum()`, protobuf messages, `bytes`, `uint`, `type()` and `dyn()` are
  excluded by an AST walker at admission. Nested comprehensions are the *only* route to exponential blow-up the
  CEL spec names, and excluding them turns "can be curtailed by the implementation" from a promise into a fact.
- **Licence:** Apache-2.0. Clean for a commercial hosted product; patent grant included.
- **Maintenance risk:** moderate and named. Two different projects live at a path called `cel-python`; pin by
  PyPI name (`cel-python`, module `celpy`) **and wheel hash**. **`celpy` publishes no CEL conformance claim
  (NOT-FOUND on its repo page)** — and our error-absorption guard depends on error semantics specifically.
- **Fallback, already identified:** `cel-expr-python` (`cel-expr/cel-python`, Apache-2.0, 76★, 81 commits,
  announced by Google Open Source 3 Mar 2026, repo launched read-only), which wraps the official CEL C++ and
  therefore inherits conformance by construction, at the cost of a C++ build dependency. **Run the CEL
  conformance suite against both before committing**, and record which one the registry root was qualified
  against.

**`SQLite` — public domain**
- **Used for:** the predicate registry, run manifests, run items, template records, register-snapshot index and
  the instrument-watch log. One file, hashable, nameable in the run manifest.
- **Not used for:** blob storage. Blobs are files in `blobs/sha256/`, because a blob store that is a directory
  can be diffed, rsynced and hashed by anybody without our code.
- **Licence:** public domain. No obligation of any kind.
- **Maintenance risk:** none worth modelling.
- **Fallback:** Postgres, on the named trigger (a second concurrent writer). The schema in §4.2 is written in
  portable SQL for that reason — no SQLite-specific types, no `WITHOUT ROWID`, no JSON1 dependencies that
  Postgres cannot mirror.

**`FastAPI` 0.141.1 — MIT** (with `uvicorn`, `pydantic`, `Jinja2`)
- **Used for:** ~12 HTTP endpoints (§6.1), `StaticFiles`, `StreamingResponse` for the one SSE surface, and
  generated OpenAPI.
- **Not used for:** background work, scheduling or job orchestration. Anything beyond request/response goes to
  a `Makefile` and the Batch API.
- **Licence:** MIT.
- **Maintenance risk:** low; very large user base.
- **Fallback:** Litestar 2.24.0 (MIT), which is the better-engineered framework and a mechanical port at this
  endpoint count. Nothing in the domain layer touches the framework.

**`Z3` — MIT (SECONDARY; the LICENSE file was not opened by any lane)**
- **Used for:** L4 test 2 only — proving a predicate is falsifiable (`¬P` SAT), proving it is not the
  flag-everything baseline (`P` SAT), and registry subsumption (`P₁ ∧ ¬P₂` UNSAT ⇒ P₂ adds no coverage). Its
  **model** is the non-degeneracy witness and goes into the predicate library entry as evidence.
- **Not used for:** evaluating a predicate against a filing. That is one-shot arithmetic; an SMT solver would
  introduce a potentially non-terminating tool into a terminating pipeline.
- **Licence:** MIT per secondary sources. **Open the LICENSE file before shipping** — this ledger will not
  assert it.
- **Maintenance risk:** low (Microsoft Research, very widely deployed).
- **Fallback:** empirical degeneracy only — the 10% control-sample arm of the fault-seeding harness (§3.5),
  which runs regardless. Losing Z3 costs the *proof* and the counterexample witness, not the gate.

**`Hypothesis` — licence NOT VERIFIED by any lane**
- **Used for:** driving metamorphic and differential relations. `RuleBasedStateMachine` with `@invariant` for
  necessary relations and in-rule assertions for expected ones, `max_examples = 50`, every real defect pinned as
  an `@example`.
- **Not used for:** generating the relations. Hypothesis generates *inputs*, never *properties* — confirmed
  against the brief's own §6.2 claim. Every relation is authored by a human off the artifact.
- **Licence:** **NOT-VERIFIED. Read `LICENSE` before adoption.** It is widely reported as MPL-2.0, which is
  file-level copyleft and would be acceptable for an unmodified dependency, but this ledger does not assert a
  licence nobody opened.
- **Maintenance risk:** low.
- **Fallback:** hand-rolled transformation loops over the fact table, ~150 lines. The necessary/expected split
  then becomes our convention rather than the library's enforcement, which is a real loss — put it in a test.

**`pandera` 0.32.1 — MIT (version VERIFIED-AT-SOURCE via the PyPI JSON API; the release date the fetch returned
was inconsistent with the version line and is UNVERIFIED)**
- **Used for:** host-function implementations of bulk column-shaped checks, where its `failure_cases` frame
  gives row-level provenance for free.
- **Not used for:** the predicate language, the verdict model, or anything that needs a third value. Its unit is
  a dataframe; ours is a cell graph.
- **Licence:** MIT.
- **Maintenance risk:** low (Union.ai, 4.4k★).
- **Fallback:** trivial — the host functions it would back are a few dozen lines each.

### 2.2 Build-time and offline — never on the verdict path

**`Docling` — MIT, 64,531★, pushed 2026-08-10**
- **Used for:** converting the 102-page FM Regulations and the 389 machine-readable circulars into a structured
  document with **typed per-element provenance** (`page_no`, `bbox` with an explicit `coord_origin`, `charspan`)
  and per-cell table offsets. We adopt `ProvenanceItem` **verbatim** as our `pdf_span` locator so the PDF
  anchor needs no translation layer.
- **Not used for:** the filing. All nine workbooks contain **zero embedded images** (`xl/media/` empty, 9 of 9),
  so no document AI and no model touches the primary artifact. Also not used for clause identity — Docling gives
  a faithful structured document, not a clause.
- **Licence:** MIT. Clean.
- **Maintenance risk:** low; pushed the day of writing, IBM-backed, 64k★.
- **Fallback:** PaddleOCR-VL (Apache-2.0) or Marker (Apache-2.0), both at a documented cost — Marker is the
  worst table row on OmniDocBench v1.6_full (TEDS 65.77), and neither publishes an equivalent typed cell-level
  provenance contract. The regulation corpus is static and small; a one-time re-parse is affordable.
- **Known limit that must be handled, not assumed away:** `TableCell.bbox` is `Optional[…] = None`. **A cell with
  no box must resolve to `NOT_RUN(source_unreadable)` for any predicate whose failure message points at it —
  never to PASS.** Separately, Docling's confidence is four heuristic page-level scores, i.e. a page ordinal, and
  **must never be fed to a conformal step as if it were a per-value probability.**

**`PaddleOCR` / PaddleOCR-VL — Apache-2.0, 87,345★, pushed 2026-07-22**
- **Used for:** the ~10 of 399 circulars that are scanned images (2.5% of the corpus).
- **Not used for:** the 389 native-text circulars, where Docling's deterministic path is preferable and its
  output is cross-checkable against the operator's existing `pdftotext -layout` extraction.
- **Licence:** Apache-2.0. Clean.
- **Maintenance risk:** low.
- **Fallback:** any OCR; or accept the gap and carry `coverage_gap: 10/399 sources unread (scanned images)` on
  every predicate whose correctness rests on the §4.1 negative search result.

**`mutmut` 3.7.0 — BSD-3-Clause, released 31 Jul 2026, 1.4k★, requires `fork` (no native Windows)**
- **Used for:** mutating **our own code** — the host-function set, the L1 schema inducer, and the CEL profile
  checker. Those three are where the silent failures live: the L1 inducer is where `RND-BRIEF` §4.4's bugs lived
  and where a lane's own §A.0.2 bug lived; the profile checker decides coverage, and coverage is the product.
- **Not used for:** L4 test 1. **This is the correction that removes a dependency:** L4's mutants are filings,
  not programs, so the harness is ours.
- **Licence:** BSD-3-Clause.
- **Maintenance risk:** low, and irrelevant — it is a development tool, not a runtime dependency.
- **Fallback:** `cosmic-ray` (MIT). A comparative study is reported to call it more actively maintained with a
  broader operator set — **SECONDARY, the study was not opened, treat the claim as UNVERIFIED.**

**`crepes` — BSD-3-Clause, 581★, pushed 2026-07-08** and **`MAPIE` — BSD-3-Clause, 1,578★, pushed 2026-08-05**
- **Used for (GATED, see §1.1 row 23):** crepes supplies the pluggable nonconformity function and first-class
  `MondrianCategorizer`, which is how the four-category taxonomy gets implemented. MAPIE supplies the
  sklearn-shaped surface and, more valuably, an **`OnlineMartingaleTest`** — a conformal test martingale that
  accumulates evidence against exchangeability and rejects when it exceeds `1/test_level`. That is the
  instrument that makes the system **refuse to certify** when the deployment population has drifted away from
  the calibration set.
- **Not used for:** anything on the native-workbook path. Measured: **0 of 3,755 unlocked cells are ambiguous
  under the address key**; 154 (4.10%) under a header-anchored key that generalises across row counts. **There
  is no learning problem in the workbook.** Running a model to predict what L1 already computes, then
  conformalising it, would reintroduce uncertainty the artifact does not contain.
- **Licence:** BSD-3-Clause for both. Clean. **TorchCP is LGPL-3.0 and is rejected on that basis.**
- **Maintenance risk:** low for both; the dead options (`nonconformist`, last push 2021-03-20) and the archived
  one (AWS `Fortuna`) are already excluded.
- **Fallback:** the split-conformal recipe is ~15 lines and we can implement it. The libraries buy Mondrian
  bookkeeping and the martingale, not the theorem.
- **The rule that travels with this, non-negotiable:** **the exchangeable unit is the FILING, not the cell.**
  Treating one filled workbook as 3,755 calibration points would inflate every guarantee we quote — cells within
  one workbook share a filer, a period, a convention and, if the filer misunderstands a definition, a correlated
  error. Report `n = F` (filings) next to every number, and make per-cell statements only through conformal risk
  control with a per-filing loss.

**`PuLP` + CBC — MIT / EPL**
- **Used for:** the registry-minimisation ILP (~40 lines) and the subsumption DAG.
- **Not used for:** anything at run time. The ILP runs at admission, offline.
- **Licence:** PuLP is MIT; the bundled CBC solver is EPL-2.0, which is file-level copyleft and imposes no
  obligation on a product that merely invokes the solver binary.
- **Maintenance risk:** low.
- **Fallback:** greedy set cover with the same constraints, reported as greedy. The ILP is an optimisation of a
  selection we can make suboptimally without breaking any claim.

**LibreOffice (`soffice`) — MPL-2.0**
- **Used for:** the third reader in the triple-reader agreement check, and the second recalculation engine in
  the differential arm and the observability filter of the fault-seeding harness. Runs inside the gVisor tier.
- **Not used for:** producing the artifact we attest over, and not (yet) as the normalising authority — see the
  53-vs-54 defect in §1.1 row 3.
- **Licence:** MPL-2.0. File-level copyleft; invoking the binary as a subprocess imposes no obligation on our
  source.
- **Maintenance risk:** none.
- **Fallback:** our own evaluator alone, with the differential arm reported as unavailable and `INDETERMINATE`
  never emitted for `engine_disagreement` — a strictly weaker instrument, and the report must say so.

**`Daikon` — MIT-equivalent licence, 260★, ships a CSV front end**
- **Used for:** the mandatory model-free L3 baseline **B1**. One row per filing, one column per L1 stable key,
  `--conf_limit 0.99`.
- **Not used for:** production predicate synthesis. Its output goes through the identical L4 gate as a model's.
- **Licence:** MIT-equivalent (SECONDARY — the licence text was not opened).
- **Maintenance risk:** low; long-lived academic tool, pushed within days of 10 Aug 2026.
- **Fallback:** none needed — if Daikon is unavailable the baseline is B0 (the template's own 138 checkable
  relations) plus B2 (the degenerate arm), and the loss is recorded in the experiment report.
- **Why it earns a place beyond the baseline:** it will emit trivia (in one published study, **27 of 40** correct
  Daikon invariants were "pointer not null") and spurious relations that survive test validation. Both are
  useful: the trivia *is* the degeneracy list, and the spurious ones are a measured demonstration **on our own
  corpus** that a check whose error rate is unknown must not be admitted.

**`cosign` / in-toto (Sigstore) — Apache-2.0 (marked UNVERIFIED in L14; not re-checked live this session)**
- **Used for:** DSSE envelope construction and Ed25519 signing of the attestation, in **keyed mode**.
- **Not used for:** keyless signing, and **never** the public transparency log. `--tlog-upload=false` is asserted
  in a test, because a filer's coverage attestation published to Rekor is a disclosure event.
- **Licence:** Apache-2.0 per the ecosystem; **re-verify before M5 commits to a signing format.**
- **Maintenance risk:** low; it is the de-facto standard.
- **Fallback:** DSSE is a 40-line specification (`PAE` pre-authentication encoding + a signature). Sign with
  `cryptography`'s Ed25519 directly. **The envelope format is the asset; the tool is not.**

### 2.3 Considered and rejected, recorded so nobody re-explores

| Project | Licence | Rejected because |
|---|---|---|
| **Great Expectations (GX Core)** | Apache-2.0 (SECONDARY) | `catch_exceptions=True → success = False`. Folds *could-not-check* into *failed* and destroys the coverage denominator. No field for not-applicable, out-of-scope or no-oracle in any `result_format` verbosity level |
| **Soda Core / SodaCL** | **Elastic License 2.0** (VERIFIED — LICENSE read on `main`) | Verbatim: *"You may not provide the software to third parties as a hosted or managed service, where the service provides users with access to any substantial set of the features or functionality of the software."* Our product **is** that. Unusable regardless of merit; its YAML syntax remains worth reading as a design reference |
| **dbt tests** | Apache-2.0 (SECONDARY) | A test is "a SELECT returning failing rows; zero rows = pass" — two-valued by construction. Also requires a warehouse |
| **Deequ / PyDeequ** | Apache-2.0, 3,638★ | Kept as the **non-LLM L3 baseline** (automatic constraint suggestion). Rejected as substrate: Spark-shaped, and its constraint suggestion is profile-driven, not statute-driven |
| **Rego / OPA** | Apache-2.0, CNCF graduated | Genuinely close — its `undefined` semantics are nearer to UNCHECKED than CEL's booleans. Rejected on two grounds: the default-deny/undefined model is famously hard to read, and **a rule an auditor cannot read has negative value in a product whose Screen 3 is an inspectable predicate library**; and the mature implementation is Go, so embedding means a subprocess or a WASM bundle per evaluation. Reconsider only if the stack moves to Go |
| **Starlark** | — | Has statements, assignment and local state, so **"which fields does this predicate read?" stops being a static question** — which deletes the coverage computation |
| **JSONLogic** | — | No types, no date arithmetic, no regex in the core spec; cannot express three of the 17 predicates. Its *shape* (a rule is a JSON tree) is stolen for the envelope |
| **JMESPath** | — | **Adopted, but for provenance pointers, not predicates.** It is a query language: no boolean operators of the kind needed, no arithmetic |
| **SpEL** | — | Evaluates against a full JVM object graph with constructor and method invocation. SpEL injection is a known RCE class. It is a scripting hook into a runtime, i.e. the opposite of a restricted language |
| **Drools / GoRules ZEN / json-rules-engine / Nools** | Apache-2.0 / MIT / NOT-FOUND / NOT-FOUND | A rule engine's core competence is **conflict resolution and chaining** — rules producing facts that fire other rules. Our architecture forbids exactly that: every predicate must be independently scored (kill rate, FFR) and independently attributable. **Chaining makes both incoherent.** ZEN's JDM decision tables remain a good Screen-3 UI reference |
| **VTL 2.2 (SDMX)** | spec; ESCB engine EUPL | Right domain, wrong altitude. VTL is statistical-dataset algebra over identifier/measure/attribute cubes; our artifact is a 10-sheet workbook with merged headers, and **getting it into VTL's data model is the hard part, which VTL does not help with.** Live implementations are still on the **1.1 draft**, five-plus years behind the published spec. **Its `check_datapoint`/`check_hierarchy` operator vocabulary is mined as a taxonomy** — European statistical authorities have already enumerated the shapes of "a validation rule over a regulatory return" |
| **Catala / OpenFisca / Blawx / finos/open-reg-tech-us-lcr** | OSS | Rules-as-code for finance is dead: 16★, no commit since 5 Jun 2024. **But the kill needs a scope line:** *rules-as-code (logic) is dead for finance; legislation-as-XML (structure) is not.* Akoma Ntoso is an OASIS standard and Indigo was pushed three days before the lane ran. Conflating them would make us reject the one live thing that fits |
| **Indigo (the platform)** | NOASSERTION | 77★, Django-shaped, built for African jurisdictions, assumes a curated human editorial workflow. **We adopt its amendment/point-in-time data model, not the platform.** Its sibling `bluebell` is GPL-3.0 and must not be linked |
| **`eyecite`** | BSD-2-Clause, 267★ | Its resolution power is entirely `reporters-db`/`courts-db` — US case reporters. Zero knowledge of `IFSCA/GN/2025/…`. **The architecture transfers; the data does not** |
| **MinerU** | NOASSERTION — Apache-2.0 **plus riders** | §2 of its LICENSE.md: *"If you provide online services to third parties based on MinerU, you must clearly and prominently indicate … that MinerU is used."* A live obligation for a hosted product. Cheap to comply with, but "Apache-2.0" on a slide would be false |
| **LlamaParse** | client MIT; **service proprietary SaaS** | A regulator-facing verification product cannot send the regulation corpus to a third-party SaaS |
| **Nougat** | MIT | ~18 months without a push, and tuned for academic papers with LaTeX maths, not statutory prose |
| **Instructor / BAML retry-and-repair** | MIT / Apache-2.0 | Retry-on-validation-failure is their headline feature, and **retry is exactly what `pass^k` penalises**. A library that silently retries three times and returns the first parse that validated is manufacturing the clean verdict this product exists to refuse. Use Instructor's typing with retries disabled, or `outlines` directly |
| **Pyodide / RestrictedPython as security boundaries** | MPL-2.0 / — | See §1.1 row 32. Retained as a portability layer and as defence-in-depth *inside* a real boundary, never as the boundary |
| **Firecracker / E2B** | — / managed | Firecracker: wrong threat model, a VM per filing. E2B: the filing leaves our boundary — a data-residency conversation about regulated filings that we should not have to have |
| **`formulas` / `pycel`** | **EUPL 1.1+** / **GPL-3.0** | Copyleft, with an unresolved network-deployment question, in the one layer whose claim is that every component carries a measured error rate |
| **`shreyashankar/spade-experiments`** | **no licence field** | 17★, 1 fork, last push 2024-04-07. Reimplement the ILP; cite the paper |
| **QuantMind** | MIT, 2.3k★ | Its typed shapes are research artifacts (Papers/News/Earnings/Factors/Theses). L0+L1 are ~200 lines of lxml measured at 28 ms. **Do not take a 2.3k-star dependency to save 200 lines** |
| **`python-calamine` / `xlsx2csv` / `pandas.read_excel`** | MIT / MIT / BSD | calamine loads 500× faster than openpyxl but has **no formula accessor at all**. `read_excel` collapses merged headers and returns **the cached values — i.e. exactly the numbers under test** |
| **`koala2`** | — | Not actively maintained; the community successor is `xlcalculator`. Not tested. Do not adopt |
| **XBRL / Xule / Arelle** | licence at `xbrl.us/dqc-license` **NOT-FOUND** | **The DQC's *process* is adopted wholesale** (draft → test against historical filings for false positives → public review → effective dates → publication); the *tooling* is XBRL-only, US-GAAP-taxonomy-only, and there is no IFSCA analogue. **Open the licence** — if permissive, the DQC rule corpus is the only ready-made financial-filing evaluation set found anywhere for L3 |

---

## §3 — THE BACKEND FLOW

Two clocks. The **online flow** (§3.1) runs per filing and contains **no model call on the verdict path**. The
**offline flows** (§3.2–§3.8) run per template version, per regulation version, or on a change signal — and
they are where the models, the humans and the expensive measurements live.

The block diagram in `ARCHITECTURE.md` Part 3 is wrong in two ways and is corrected here: **L6 is a loop over
L0–L5 on transformed inputs, not a downstream box after L5**, and **metamorphic relations route through the L4
gate before use, exactly like any other predicate.**

### 3.1 ONLINE — a filing arrives, and a signed report exists

Fourteen steps. Each names its inputs, outputs, determinism, failure handling, and whether a human is required.
`⏱` is the measured or derived time cost. Status is per §0 preamble.

---

**F0 — RECEIPT** · deterministic · ⏱ I/O-bound · **BUILT**

- **In:** the uploaded bytes; optionally a list of attachment bytes; optionally a declared template id.
- **Out:** `filing_sha256` over the **exact received bytes**, written to `blobs/sha256/<aa>/<rest>`; a `run` row
  in state `RECEIVED`.
- **Determinism:** total. The same bytes always produce the same digest and the same blob path.
- **Failure:** payload over the configured size cap, or a non-zip container → HTTP 413/415 and **no run row is
  created**. There is no partial run.
- **The rule that makes L7 possible:** the artifact is **never re-serialised**. Every downstream reader operates
  on a copy; the attested hash is always over these bytes.
- **Human:** no.

---

**F1 — CONTAINER GUARD** · deterministic · ⏱ <5 ms · **SPECIFIED**

- **In:** `filing_sha256`.
- **Out:** `PASS`, or a run terminated in state `INVALID`.
- **What it checks, before any XML is parsed:** zip entry count; per-entry *uncompressed* size; total compression
  ratio; declared media types; presence of the parts a workbook must have.
- **Determinism:** total.
- **Failure:** any guard trips → the run terminates as `INVALID` with `ERROR(source_unreadable)`. **It does not
  become a FAIL.** A filing we could not safely open is not a filing that failed a check.
- **Where it runs:** inside the gVisor tier. This is the only genuinely adversarial surface in the system.
- **Human:** no, but an `INVALID` run raises an operator notification (§3.9).

---

**F2 — TRIPLE-READER INGEST** · deterministic given pinned versions · ⏱ ~250 ms typical, ~4.2 s when the third
reader is invoked · **PARTIALLY BUILT** (readers A and B built; the agreement check specified)

- **In:** `filing_sha256`.
- **Out:** a `RawWorkbook` structure, plus an **extraction manifest**.
- **The three readers:**
  - **A — `zipfile` + `lxml`, namespace-aware.** Authoritative for structure: sheets and their `state`,
    dimensions, merged ranges, `<dataValidation>` **and** `<x14:dataValidation>`, `sheetProtection`, defined
    names, the `styles.xml` unlocked mask, per-sheet sha256. ⏱ ~100 ms.
  - **B — `openpyxl` 3.1.5.** Authoritative for formula text with shared-formula translation, and for cached
    values. ⏱ 202 ms.
  - **C — LibreOffice-normalised copy, re-read by A.** Invoked **only** when A and B disagree, or when the
    filing's function vocabulary exceeds our evaluator's. ⏱ 3.9 s when invoked.
- **The agreement vector, compared field by field:** `n_sheets`, `sheet_names`, `hidden_sheets`, `n_cells`,
  `n_formula_cells`, `n_validations`, `n_defined_names`, `merged_ranges`.
- **Failure handling, and it is graded:**
  - Disagreement on `n_sheets`, `sheet_names` or `hidden_sheets` → the run is **`INVALID`**. The scope is not
    established, so nothing computed on top of it means anything.
  - Disagreement on any other field → the affected fields are marked, and every predicate reading them returns
    **`NOT_RUN(extractor_disagreement)`**. Coverage falls. It does not silently succeed.
- **Why this step exists, and it is not hypothetical:** three implementations of this parse — two of them sitting
  in the same directory — returned **244, 294 and 505** on the same file on the same day. Nobody had run them
  against each other, and the divergence sat undetected inside the authoritative document. **This step is thirty
  lines and it converts that silence into a build failure.**
- **The extraction manifest is a first-class output**, not a log: parts read, parts skipped, namespaces
  encountered, constructs not understood (`x14:dataValidation`, `model/item.data`, `connections.xml`,
  `t="array"`), and the three-way agreement result. **A schema extractor that silently returns 35 of 54
  validations is the exact failure this product exists to prevent, occurring inside the product.**
- **Human:** no, except to triage an `INVALID`.

---

**F3 — TEMPLATE BINDING** · deterministic · ⏱ <1 ms · **SPECIFIED**

- **In:** the `RawWorkbook` structure.
- **Out:** `template_sha256` — the digest of the **pinned blank template** this filing is a filled copy of — and
  the `TemplateSchema` loaded from the template registry.
- **How binding works, and the decomposition matters:** the filing's sha256 necessarily differs from the blank's,
  so binding is by **structural fingerprint**: sha256 over the canonical serialisation of
  `(sheet names + states, sheet dimensions, merged-range set, defined-name list, unlocked-cell mask)`.
  **Formula-cell content is deliberately excluded from the fingerprint.** If it were included, a filer who
  overwrote a formula with a literal would fail to *bind* — and formula-override is the single most consequential
  real spreadsheet defect and the classic route by which a wrong number is made to look computed. It must surface
  as a **predicate failure** (MR-19, §3.1/F9), not as a binding error.
- **Failure:** no template matches → the run terminates `INVALID` with `NOT_RUN(template_unbound)`. **This
  escalates**: the whole run is suspect, and it is also the signal that a new template version has been published
  and the offline admission flow (§3.2) must run.
- **Human:** yes, on failure. A human decides whether this is a new template version, a filer using a superseded
  one, or a corrupted file.

---

**F4 — FACT-TABLE CONSTRUCTION** · deterministic · ⏱ ~10 ms · **BUILT**

- **In:** `RawWorkbook` + `TemplateSchema`.
- **Out:** the **two-document fact model** the CEL environment sees. Exactly two top-level names are bound. No
  clock, no network, no filesystem.

```
filing.<sheet_key>.<table_key>.rows[i].<field_key>   -> typed scalar
filing.<sheet_key>.<field_key>                       -> typed scalar
filing.<...>.__cell__                                -> "3. Portfolio!O7"   (provenance pointer)
filing.__hash__                                      -> sha256 of the submitted workbook
template.vocab.<vocab_key>                           -> list<string>   (from the PINNED blank)
template.formula.<cell>                              -> string         (the native formula text)
template.__hash__                                    -> sha256 of the pinned blank
```

- **Two rules that are non-negotiable:**
  1. **Vocabularies always resolve against `template`, never `filing`.** The `Dropdown` sheet is **hidden and
     the only unprotected sheet in the workbook**. Reading the vocabulary from the submission would let a filer
     define their own legality by editing one range. This is not hypothetical; it is a one-line consequence of
     `protected=False`, and sheet protection is an application-level flag anyway — nine sheets carry SHA-512
     `sheetProtection` hashes and stripping them is a zip edit. **Assume the filed artifact is fully mutable.**
  2. **Every leaf carries `__cell__`.** The report must expand a failure to the actual cells, and the
     weakest-input provenance rule needs a pointer per input, not per predicate.
- **Money scaling:** every monetary cell is converted to an `int64` count of 10⁻³ USD Million at this step, once.
- **Failure:** a cell whose declared type and content disagree is carried as `null` with a type-error marker;
  the pre-flight in F7 turns that into `NOT_RUN(source_unreadable)` for the predicates that read it.
- **Human:** no.

---

**F5 — ATTACHMENT EXTRACTION (L2b)** · **model-bearing** · ⏱ seconds, and only when attachments exist ·
**SPECIFIED / GATED**

- **In:** attachment bytes; `TemplateSchema.stable_keys()`.
- **Out:** `Fact{key, value, unit, provenance_anchor}` records with `warrant = MODEL_EXTRACTED`.
- **Skipped entirely when there are no attachments — which is the normal case, and the marginal model cost of
  that filing is exactly $0.00.**
- **The three guards, in order:**
  1. **Generation-time:** `key` is typed `Literal[*L1_KEYS]`, so an off-schema key is **ungeneratable**.
  2. **Post-hoc deterministic:** any key not in `TemplateSchema` is rejected. Kept even though guard 1 makes it
     redundant, because **this is the one you can prove to an auditor.**
  3. **Conformal abstention (GATED):** emit a prediction set; abstain unless it is a singleton. Empty sets are
     not suppressed — an empty set is an unambiguous abstention and maps straight to
     `INDETERMINATE(extraction_abstained)`.
- **Retry is banned.** If ever enabled, a Fact produced on attempt *k > 1* must carry that in its provenance.
- **What the guarantee actually is, stated so the UI cannot misstate it:** the unconditional rate of *silently
  accepting a wrong key* stays ≤ α under the singleton rule. The rate **conditional on having accepted** is
  ≤ α/P(accept). At the best measured document-IE singleton rate found anywhere (**70%**), α = 0.05 becomes a
  **7.14%** conditional bound. **If the UI shows "5%" anywhere near an accepted binding, it is wrong.**
- **Failure:** any model or network error → `NOT_RUN(source_unreadable)` for the affected keys. Never a FAIL,
  never a silent omission.
- **Human:** no at run time; yes at calibration-set construction (offline).

---

**F6 — PREDICATE SELECTION** · deterministic · ⏱ <1 ms · **SPECIFIED**

- **In:** `template_sha256`; the registry root pinned for this run (default: current head).
- **Out:** the active predicate set, partitioned into `ACTIVE` and `PROVISIONAL`.
- **Rules:**
  - A predicate whose `qualified_against.template_sha256` ≠ this filing's template is **not evaluated**;
    its pairs land in `NO_PREDICATE(not_yet_requalified)`.
  - A `PROVISIONAL` predicate (any element of its `qualified_against` has changed — §3.7) **still runs**, so
    detection is not lost, but its measured numbers are hidden in the UI and **its pairs are counted under
    `NO_PREDICATE(not_yet_requalified)`, not under `settled`.**
  - **Therefore coverage falls when the template or the regulation changes.** That is correct behaviour. A system
    whose coverage silently persists across a version boundary is lying.
- **Failure:** an empty active set is not an error — it is a report with `coverage.settled.total = 0` and every
  pair in `NO_PREDICATE`. That report is honest and should be renderable.
- **Human:** no.

---

**F7 — PRE-FLIGHT KEY CHECK** · deterministic · ⏱ sub-ms · **SPECIFIED**

- **In:** each predicate's declared `schema_keys` (machine-checked against its CEL AST at admission, so the set
  is exact and not an estimate); the fact table.
- **Out:** for each predicate, `PROCEED` or `NOT_RUN(source_unreadable: <key>)`.
- **Why it exists:** it is the structural mitigation for CEL's documented error absorption. Without it,
  `true || <error>` yields PASS from an unreadable input, and the guard would depend on how each predicate
  happened to be written.
- **Determinism:** total.
- **Human:** no.

---

**F8 — EVALUATION (L5)** · deterministic · ⏱ sub-millisecond for 227 arithmetic predicates · **BUILT**

The five-rule evaluation contract, in order:

```
1.  Evaluate P.applicable.
      error   -> NOT_RUN("source_unreadable")              [never FAIL]
      false   -> OUT_OF_SCOPE(P.reason_if_inapplicable)    [never PASS]
      true    -> continue

2.  PRE-FLIGHT (F7) already ran. Any missing/mistyped key -> NOT_RUN, expr never evaluated.

3.  Evaluate P.expr under a step-count budget and a wall-clock kill.
      budget exceeded -> NOT_RUN("budget_exhausted")       [never FAIL]
      runtime error   -> NOT_RUN("source_unreadable")      [never FAIL]
      false           -> FAIL, and evaluate P.witness for the cell list
      true            -> PASS

4.  Provenance composes by WEAKEST INPUT: warrant = min over every fact the AST read, under
    DETERMINISTIC > MODEL_EXTRACTED > DERIVED; retrieved_at = max over inputs. A verdict is never
    fresher than its stalest input and never stronger than its weakest.

5.  Every predicate reports cells_bound. cells_bound == 0 -> ERROR(cells_bound_zero), and the run
    becomes INVALID. Binding to nothing is never a PASS.
```

- **Rule 3 is the whole product in four lines.** Everywhere a conventional validation framework converts doubt
  into a failure (`success = False`) or into silence, this converts it into a **counted, reasoned, reported**
  non-settlement.
- **Rule 5 kills the four most likely silent-failure modes at once:** vacuous pass (`all([]) is True`),
  empty-set arithmetic (`sum([]) == 0`), selector drift, and scope truncation.
- **Human:** no.

---

**F9 — METAMORPHIC AND DIFFERENTIAL PROBES (L6)** · deterministic · ⏱ ≤2 s DERIVED · **SPECIFIED**

This is a **loop over F4–F8 on transformed fact tables**, not a stage after F8.

- **In:** the fact table; the admitted relation set; the pinned template.
- **Out:** per relation, `PASS / FAIL / INFORMATIONAL(advisory) / OUT_OF_SCOPE(non-degeneracy precondition
  unmet)`.
- **The relation set is 25, all oracle-free.** By what each needs: **15 need the filing alone**; 4 need the
  filing plus the versioned blank; 3 need two consecutive filings; 1 needs multiple instances of one filing;
  2 are checker self-tests and are never reported to the filer.
- **Every relation carries three annotations, and every false alarm in the analysis traced to a missing one:**
  a **degree map** over every field (money = 1; counts, dates, ratios and categoricals = 0), a
  **necessary/expected flag**, and a **non-degeneracy precondition** — because an all-zero filing satisfies the
  partition relations trivially, which would let an empty filing score 100% coverage through the L6 door.
- **The highest-value relation is not in the brief:** four independent partitions of *funds raised* exist in the
  FME workbook (by investor category, by country, by accreditation status, and the Summary carry) and **the
  workbook enforces agreement between none of them** — Tables 4.2 and 4.3 contain zero formulas. A mismatch is
  unambiguously a defect, and no oracle is required.
- **MR-19, the differential arm, is the one that pays for the evaluator:** for each of the 505 formula cells,
  recompute with our evaluator and compare against the value the filing carries. **This is the only check in the
  entire design that detects a filer overwriting a formula cell with a literal** — a defect that leaves the
  filing perfectly self-consistent, because the inconsistency was deleted along with the formula. Its oracle is
  the published blank template, so **it needs no corpus at all.** It should be predicate #1 in the hand-authored
  set.
- **The honest limit, stated on the report surface:** L6 does not decide whether the disclosed composition is
  *accurate*. It decides whether the filing is *internally coherent under transformations that must preserve its
  meaning*. **An FME that fabricates a consistent set of numbers passes all 25.**
- **Failure:** a violated *necessary* relation is a FAIL with the transformation and both value sets as witness.
  A violated *expected* relation is `INFORMATIONAL` carrying the quoted guidance note that makes the exception
  lawful.
- **Human:** no at run time; yes to author relations (§3.9).

---

**F10 — RUN-TIME SEEDED CANARIES** · deterministic · ⏱ ~35 ms DERIVED · **SPECIFIED** · *the most important
addition to the architecture*

- **In:** every admitted predicate's stored `kill_case` witness; this filing's fact table.
- **Out:** `canaries_passed = N`, or a list of **dead predicates** and a run state of `INVALID`.
- **What it does:** for each admitted predicate, instantiate the fault it is *known to detect* against **this
  filing's cells**, re-evaluate, and confirm the predicate fires.
- **Why it is the answer to the design's own worst hole:** the system is a deterministic program that outputs
  "no failures", and `RND-BRIEF` §4.4's argument applies to it with full force. L4 qualifies predicates **at
  admission, against the corpus of that moment**; nothing else re-checks, at run time, on *this* artifact, that
  the predicates still bind to anything. Canaries catch parser drift, selector misses, renamed sheets,
  hidden-sheet truncation, encoding changes and empty-set vacuity — **for this file.**
- **The output is a third run state: `INVALID`.** Not "clean", not "unchecked" — *"this system could not
  demonstrate it was working here."*
- **Cost derivation:** canaries operate on the in-memory fact table, not the file. At the measured harness
  throughput of **7,946 mutants/second**, 280 canaries ≈ **35 ms**. (DERIVED from a measured rate; the canary
  loop itself is not yet built.)
- **The line this earns:** *every report carries proof that the checker was alive when it ran — on your
  document, not on a benchmark.*
- **Human:** yes, on failure. A silent canary is an engineering incident, not a filing outcome.

---

**F11 — COVERAGE COMPUTATION AND CLOSURE** · deterministic · ⏱ <5 ms · **BUILT (denominator) / SPECIFIED
(closure)**

- **In:** every `(field × obligation)` pair in scope; every item state from F8–F10.
- **Out:** the coverage object (§4.4), never a bare fraction.
- **The denominator is the field surface** — every cell the filer can actually type into, recovered from
  `styles.xml` (`cellXfs → <protection locked="0"/>`), because Excel locks every cell by default and the template
  author unlocks precisely the input cells. **3,747 for the FME workbook.**
- **The denominator is computed twice, by two independent readers, and the run is `INVALID` if they disagree** —
  because when numerator and denominator come from the same parser and the parser is wrong, the ratio is still
  plausible and the error is invisible by construction.
- **A named, tested invariant guards the flattering direction:** the denominator must be derived from the
  unlocked mask, **never from the predicate set**. That mistake was made twice in one afternoon by the person
  who knew about it — once in the mutation harness (sampling mutation sites only from cells the predicates
  already read) and once in the coverage calculation (99.2%, from a denominator built out of the numerator).
- **Closure is enforced, not documented:**
  `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == pairsTotal`.
  **A pair that lands in no bucket aborts report generation.** This makes the coverage claim true by
  construction in the same way the admission gate makes the error-rate claim true by construction.
- **For an unprotected template there is no unlocked mask**, so the field surface is not mechanically derivable.
  **Decision: such a template reports counts only, with `coverage: null` and
  `denominator.source: "not derivable — template ships no protection mask"`.** `null` means *we make no claim*;
  it is not zero and it is not omitted. Two of the nine prescribed workbooks are in this state.
- **Coverage is a per-template property and must never be averaged across templates.** `EDR_1` has zero
  formulas; `IFSCA_Annual_Reporting_Format` has zero formulas *and* zero validations. A corpus-wide coverage
  number would be exactly the kind of silent all-clear the product exists to prevent.
- **Human:** no.

---

**F12 — AGGREGATE VERDICT** · deterministic · ⏱ <1 ms · **SPECIFIED**

A declared, versioned, deterministic policy in the shape of ISA 705 — explicitly a policy, not a claim to
implement an auditing standard.

```
residueIsConfined := (unsettled pairs touch <= K distinct sheets)
                     AND (no unsettled pair is flagged material-by-policy)
                     AND (unsettled / inScope <= T)
```

`K`, `T` and the material-by-policy field list are **published, versioned parameters carried inside the
attestation**, never constants in code.

| | residue confined | residue pervasive |
|---|---|---|
| **failures present** | `EXCEPTIONS_NOTED` | `ADVERSE` |
| **no failures, unsettled residue** | `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE` | `COVERAGE_INSUFFICIENT` |

- **There is no state whose name means "clean."** The best available verdict is
  `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE`, which cannot be quoted out of context without carrying its own
  qualifier. **This delivers "no green tick" by naming rather than by iconography — an icon can be
  screenshotted; a name travels with the claim.**
- **The report's own title string is a function of the verdict state**, not a fixed "Coverage Report".
- **When `COVERAGE_INSUFFICIENT`, the wording flips** from "this filing was checked against N predicates" to
  "this filing was *submitted for* checking against N predicates; coverage was insufficient to report."
- **Human:** no.

---

**F13 — REPORT, ATTESTATION AND LOG** · deterministic · ⏱ ~20 ms · **PARTIALLY BUILT**

- **Out, in this order:**
  1. **`report.html`** — one self-contained file, inline CSS and JS, zero external requests, opens from
     `file://` with networking off, renders on a phone, and **contains no green tick** (enforced by a build-time
     grep, §6.4).
  2. **`attestation.json`** — DSSE envelope over an in-toto Statement v1 whose `subject[]` carries **both** the
     filing digest and the template digest (§4.6).
  3. **`run.jsonl`** — one line per predicate evaluation:
     `{predicate_id, verdict, reason, cells_bound, elapsed_us}`.
  4. Optional projections, each **declared lossy**: OSCAL Assessment Results, OSCAL POA&M (the Unchecked panel
     plus "what would make it checkable"), and an RO-Crate evidence crate.
- **The run manifest is embedded in the report's own footer**, where a human can read it:
  `{template_sha256, filing_sha256, registry_root, predicate_set_version, code_git_sha, python_version,
  lxml_version, openpyxl_version, celpy_version, evaluator_version, tool_versions, canaries_passed}`.
- **Three schema-required sentences that no marketing page can remove**, because they are fields and not
  template strings: the bounded-silence statement, the purpose statement, and `summaryIsNotSubstitute: true`.
- **One more, permanently on the report surface:** *"This system detects error, not deception. Every check here
  is a consistency check over a self-reported document. A coherent liar passes all of them."*
- **Failure:** the closure invariant (F11) or the no-green-tick gate failing **aborts report generation**. There
  is no degraded report.
- **Human:** no.

---

**F14 — `verify`** · deterministic · ⏱ = the full pipeline · **SPECIFIED**

- **In:** `report.html` (or the attestation) plus the blobs it names.
- **Out:** `REPRODUCED` with a byte-comparison, or a diff.
- **What it does:** re-runs the pipeline from the embedded manifest at the pinned registry root, pinned template,
  pinned register snapshot and pinned tool versions, and asserts a byte-identical report.
- **This is the observability story.** The question a supervisor asks is not "what was the p99 latency" but
  "can I get this same answer again."
- **Acceptance test for the whole programme:** a third party clones the repo, runs `verify <report.html>` on a
  different machine, and gets a byte-identical re-derivation. **If it does not reproduce, it does not ship.**
- **Human:** no.

---

### 3.1.1 The three run states, and why the third one exists

| Run state | Meaning | Set by |
|---|---|---|
| `VALID` | The pipeline ran, the checker demonstrated liveness on this artifact, and the closure invariant holds | F10 + F11 |
| `INVALID` | **The system could not demonstrate it was working here.** Not clean, not unchecked | F1 guard trip · F2 structural disagreement · F3 unbound template · F8 `cells_bound == 0` · F8 predicate raised · F10 silent canary · F11 closure violation or denominator disagreement |
| `REJECTED` | The submission never became a run | F0 size/type refusal |

**An `INVALID` run renders a report that states why, and carries no coverage fraction at all.** The aggregate
verdict field is `null`, not `COVERAGE_INSUFFICIENT` — because the latter is a finding about the filing and this
is a finding about us.

---

### 3.2 OFFLINE A — TEMPLATE ADMISSION (per published template version)

Triggered by the instrument-stream watcher (§3.8) or by an `F3 template_unbound` escalation.

| Step | In | Out | Determinism | Failure | Human |
|---|---|---|---|---|---|
| **T1 Fetch** | the published URL on `ifsca.gov.in/Download` | bytes + `template_sha256` + recorded fetch timestamp and origin URI | deterministic given the bytes | fetch failure → retry; a changed hash at an unchanged URL is a **version event**, not an error | no |
| **T2 Triple-read** | template bytes | `RawTemplate` + extraction manifest | as F2 | any structural disagreement **blocks admission**. A template we cannot read three ways does not enter the registry | on disagreement |
| **T3 Induce schema** | `RawTemplate` | `TemplateSchema{cells, merges, formulas(505), validations(54), vocabularies(15), protection, unlocked_mask, field_surface(3747), stable_keys, carry_table(195 edges), version_hash}` | deterministic, **28–44 ms MEASURED** | a construct not understood is recorded in the manifest and its fields are excluded from `in_scope` with a stated reason — never silently dropped | no |
| **T4 Harvest predicates** | `TemplateSchema` | **280 candidate predicates for the FME workbook, 515 across nine**, in nine classes: `cross_sheet_equality` (181), `membership` (20), `sum_identity` (35), `numeric_bound` (13), `integer_bound` (11), `date_bound` (6), `same_sheet_equality` (11), `conditional_required` (0), `tally_identity` (3) | deterministic, **MEASURED, zero model involvement** | none — this step cannot fail, only under-produce | no |
| **T5 Function-vocabulary check** | the 505 formula texts | the set of Excel functions used | deterministic | a function our evaluator does not implement → those cells are `NOT_RUN(source_unreadable)` until it is implemented, **or** the LibreOffice engine is promoted to primary for this template and its disagreement rate is measured | yes, to decide |
| **T6 Stable keys** | `TemplateSchema` | `key = (sheet_name, merged_header_path, row_label)`; coordinates are a **resolved attribute**, re-derived per version | deterministic | a key that does not resolve enters an explicit `UNRESOLVED` state and **blocks** every predicate that declares it. It never silently binds to the wrong cell | no |
| **T7 Register** | all of the above | a `template` row + a `template_version` row; the schema serialised and content-addressed | deterministic | — | **yes — a human signs the admission**, because this fixes the denominator that every subsequent number is a fraction of |

**Why T4's 20 membership predicates matter more than their count:** they take the workbook from **3 enforced
controlled vocabularies to 20**, with zero model involvement, entirely from the induced schema. One of them —
`'3. Portfolio'` instrument-type over `I116:I126` and `M116:M126` — covers **210 cells** with a two-value
vocabulary. That is the thesis in one line: *the check was already latent in the artifact; nobody had extracted
it.*

---

### 3.3 OFFLINE B — CLAUSE-GRAPH INDUCTION (the regulation side)

`ARCHITECTURE.md` has no analogue of L1 on the regulation side, and without one, L3's "the clause it claims to
implement" is a free-text string and L5 cannot cite. This is **L1b**.

```
399 circulars + 102 pp FM Regulations (PDF)
  ├─ 389 native-text ──► Docling (MIT) ──► DoclingDocument [page_no, bbox, charspan per element]
  └─  10 scanned     ──► PaddleOCR-VL (Apache-2.0, 0.9B) ──► same
                             │
                             ▼
                    deterministic promoter
        (numbered headings → <section>; (1)/(a)/(i) → nested <paragraph>;
         "Provided that" → <proviso>)
                             │
                             ▼
                   Akoma Ntoso: eId per clause, FRBR URI per instrument
                             │
        ┌────────────────────┼────────────────────────────┐
        ▼                    ▼                            ▼
  instrument identity   dated x-ref extractor      amendment graph
  + point-in-time       (866 known targets)        "as amended up to <date>"
```

- **Recall check with a declared denominator:** the promoter is validated against the operator's measured
  **8,866 `shall` occurrences across 361 circulars**. A promoter that loses `shall` clauses is losing
  obligations, and the count is the regression test.
- **Amendment resolution is a real engineering problem, not an aspiration:** 90 of 389 circulars amend an earlier
  instrument, and **76 of 82 amending circulars cite a resolvable target (92.7%)**.
- **Output per clause:** `{frbr_uri, eId, as_at, pdf_span{page_no,bbox,charspan}, text, provisos[], xrefs[]}`.
- **Determinism:** the promoter is deterministic. The **model-bearing part is confined to the 10 scanned
  circulars**, and their output is frozen once and content-addressed, so it never re-enters a verdict path.
- **Failure:** an unpromotable region is recorded with its page span and every obligation inside it is
  `NO_PREDICATE(rule_ambiguous)` until a human promotes it.
- **Human:** yes, to adjudicate promoter failures and to confirm amendment chains that do not resolve.
- **Status: SPECIFIED.** Nothing of L1b is built.

---

### 3.4 OFFLINE C — CANDIDATE PREDICATE PROPOSAL (L3)

**Renamed, and the rename is substantive.** L3 is **candidate proposal**, not synthesis; L4 is **admission**.
Every measured system in the literature that works, works because a rejector exists; every one that fails, fails
because the rejector was absent or fake. **L4 is the rejector and it is the actual product.**

| | |
|---|---|
| **In** | `TemplateSchema` (as an explicit I/O constraint in the prompt — the single measured intervention that most improves this exact task, worth +37–54 pp in the only published study of statute→executable-model generation); the clause unit with its `eId` and FRBR URI; the template's own 505 formulas as an *available* criterion source |
| **Out** | candidate predicates in the envelope format (§4.3), each carrying its clause locator, the exact character span it implements, an enumeration of every proviso in that span, and a natural-language rationale |
| **Model** | `claude-opus-5`, Batch API, prompt caching on the schema prefix. **Offline, once per template version.** Never in a request path |
| **Determinism** | **None, and it does not need any.** L3's output is inadmissible until gated. A weaker model proposes more rejects; it cannot smuggle an unqualified predicate past the gate, because admission requires a measured kill rate and FFR |
| **Failure** | a malformed candidate is discarded and counted. **The discard pile is data** and appears in the attrition funnel |
| **Human** | no at generation; yes at the go/no-go decision |

**The criterion-source claim must be stated in its corrected form.** `ARCHITECTURE.md` calls the template's
native formulas *"an authoritative criterion source rather than an inferred one."* It is an **available**
criterion source, not an authoritative one — proven at source: `D17 = SUM(D18:D20)` over three `COUNTIF`
patterns that miss two of the template's own nine vocabulary terms. A predicate mined from it would pass a wrong
filing and fail a right one. **The L4 gate is not an optimisation; it is the only thing standing between the
template's bugs and our verdict.**

**The settling experiment, pre-registered, replacing the brief's version.** The brief's design — n = 10, delete
L3 below 3 — is underpowered in both directions: at a true rate of 0.35 it deletes L3 **26%** of the time; at
0.15 it keeps L3 **18%** of the time; the 95% Wilson interval at p̂ = 0.30 is **[0.108, 0.603]**. It cannot
distinguish "one in ten" from "three in five". Replace with:

- **n = 20 obligations**, drawn by a stated rule, **stratified before any model runs** into **Stratum A —
  arithmetically closed** (≈12) and **Stratum B — judgment-bearing or externally dependent** (≈8).
- **k = 10 candidates per obligation per prompt regime, two regimes** ("base" and "simple"), because the
  correctness-maximising prompt is measurably not the completeness-maximising one. Report accept@1/@5/@10 and
  the union.
- **Three mandatory baselines run *before* the model:** B0 the template's 138 checkable relations; B1 Daikon;
  B2 the degenerate arm. **If L3 does not beat B0 ∪ B1 ∪ B2 on marginal kill at equal FFR, it has produced
  nothing**, however many candidates survive.
- **Decision rule:** Stratum A ≥ 6/12 **and** L3 beats the baselines → L3 retained as a candidate generator
  whose output is inadmissible until gated. Stratum A ≤ 3/12 → **L3 deleted for Stratum A**; predicates are
  hand-authored; the rest of the architecture is unaffected. 4 or 5 → **underpowered; report the interval and
  either extend n or stop. Do not negotiate.** Stratum B: pre-registered expectation 0–1 of 8, and a Stratum-B
  survivor is treated as a **suspected false positive** requiring manual adjudication before it counts.
- **Power at n = 20, threshold ≥ 6:** P(delete | p = 0.15) = 0.933; P(delete | p = 0.35) = 0.245. Wilson at
  p̂ = 0.30 = [0.145, 0.519]. Still not tight — **so the honest report is the interval, and the interval is what
  goes on the slide.**
- **Run 9.1 with both target languages, Python and CEL, and report the two rates separately.** CEL is a far
  smaller output space with the schema in the prompt, and far rarer in pretraining corpora. The sign is unknown;
  it is a one-line change that doubles what the experiment settles.
- **Written down now, before the result:** the criterion may change only by an argument that the old criterion
  was wrong. *"We should have sampled better obligations"* is not such an argument — the sampling rule is
  pre-registered. *"The clean corpus was synthetic"* is not such an argument — it applies symmetrically to the
  baselines. *"Stratum B was always going to fail"* is not such an argument — that is why it is a separate
  stratum with its own pre-registered expectation.

**Status: SPECIFIED / GATED.** Nothing of L3 is built, and nothing should be until the experiment runs.

---

### 3.5 OFFLINE D — QUALIFICATION (L4). Four gates.

**Renamed:** this is **seeded-defect adequacy**, not mutation testing. The name change is not cosmetic — it
stops the design borrowing credibility from a technique it is not using, and it survives a referee.

| | Mutation testing (classical) | Seeded-defect adequacy (this) |
|---|---|---|
| Subject under evaluation | a **test suite** | the **predicate set** |
| A mutant is | a variant of the **program** | a variant of the **filing** |
| "Killed" means | some test fails | some predicate FAILs |
| The nuisance class | equivalent mutant (a theorem) | **unobservable mutant (a diff)** |

**GATE 0 — SCOPE FAITHFULNESS.** Every candidate must carry (a) the exact character span of the clause it
implements, (b) an explicit enumeration of every proviso, exception and cross-reference in that span, and (c)
for each one, **either an implementing branch or an emitted `NO_PREDICATE(rule_ambiguous)` declaring it**.
**A predicate that neither implements nor declares a proviso is rejected.** This gate exists because frontier
models ground the right spans well (SpanFaith 0.77–0.79) and wire the exception structure badly (Edge-F1 ≈ 0.22)
— and our instrument is full of provisos: reg 39(1) has a half-yearly proviso for close-ended restricted
schemes; regs 26(2)/38(2)/50(2) have a fund-of-funds proviso; **reg 51(1) ends "in such manner as specified by
the Authority"**, a live delegation hook. It is a structural check, not a semantic one, and it is cheap.

**GATE 1 — CAN IT FIRE? (kill rate)** Six steps, and step 3 is the one the brief does not have.

```
1  TARGET SELECTION
   Seed into the fields P.schema_keys reads (from the CEL AST), PLUS a 10% CONTROL SAMPLE of
   fields it does NOT read.  Without the control arm a flag-everything predicate scores a
   perfect kill rate.  This is L4 test 2 implemented empirically alongside the Z3 proof.

2  GENERATION
   For each (clean workbook c) x (target field f) x (fault class F1..F14):
     m = apply(F, c, f), manifest {clean_hash, fault_class, target_cell, param, seed}
   At most ONE mutant per (field, fault class) per clean workbook.
   Mutants are produced by RAW-ZIP SURGERY: copy every part byte-for-byte, rewrite exactly one
   worksheet XML.  MEASURED: one part differs; the 3.55 MB data model and all 19 x14
   validations survive byte-identical.  (openpyxl's round-trip would destroy 98.2% of the file.)

3  OBSERVABILITY FILTER   <- the step that decides whether the kill rate means anything
   Recalculate m with BOTH engines; diff the resulting value grid against the recalculated clean.
     no cell value differs                      -> DISCARD as UNOBSERVABLE, counted separately
     differs only where no admitted predicate can reach -> retain, tag UNREACHABLE
     otherwise                                  -> admit to the denominator
   Expected discard rate is HIGH: 3,512 of 7,500 (46.8%) measured on a comparable operator suite.
   REPORT OUR OWN FIGURE EVERY RUN.  It is a property of the operator mix and must not be assumed.

4  EXECUTION      run P (and, for interaction, the admitted set) over every admitted mutant and
                  over every clean workbook
5  SCORING        below
6  PROVENANCE     every mutant content-addressed; every kill records (mutant_hash, predicate_id,
                  predicate_version, template_hash, harness_version, corpus_label)
```

**Scoring — three numbers, never one:**

```
GENERATED     G   UNOBSERVABLE  U   OBSERVABLE  O = G-U   UNREACHABLE  R   KILLED  K
KILL RATE            KR  = K / O            <- the headline; NEVER K/G
REACHABLE KILL RATE  RKR = K / (O - R)      <- adequacy of the rules we HAVE
UNOBSERVABLE RATE    UR  = U / G            <- a property of the OPERATORS, reported so the mix is auditable
```

**Four reporting rules:** never quote a bare score — quote `K/O` with both integers plus `UR`; report the
**per-fault-class vector**, because a predicate that kills 100% of sign flips and 0% of stale carry-forwards has
a meaningless average; **`R` is a coverage statement, not a failure** — `R/O` rising over time is the inverse of
the coverage curve and belongs beside it; and **every suppression is logged with its reason — an undeclared
suppression is a coverage lie.**

**One measured caution the product's vocabulary must carry:** in the built run, **every arithmetic operator
killed at exactly 18.1%**, identical to the field-graph coverage fraction — because any perturbation of a cell
an identity reads breaks it and no perturbation of a cell it does not read can. **For identity predicates, kill
rate measures predicate *reach*, not predicate *quality*.** The report must say which it is showing.

**GATE 2 — CAN A DEGENERATE ARTIFACT SATISFY IT?** Z3 proof plus the empirical control arm. Rejects
trivially-true predicates (`¬P` UNSAT), always-flag predicates (`P` UNSAT — the flag-everything baseline in
disguise), and near-vacuous bounds. **The gate demonstrably does real work:** of ALR's six bound predicates,
**five assert only `≥ -1e17` — "this is a number" — over 1,428 cells and are rejected**, while 19 of the FME
workbook's 24 bounds are a real `≥ 0` non-negativity constraint and are admitted. `unknown` from Z3 is treated
as UNCHECKED, never as "non-degenerate".

**GATE 3 — DOES IT DISCRIMINATE? (FFR)** *This is the gate the brief cannot run as specified, and the repair is
the most important process decision in the document.*

The attack: the same team authors the predicates **and** fills the clean corpus, so the corpus is operationally
*defined as* "filings that satisfy our predicates". **FFR measured that way has expected value zero regardless
of predicate quality — it carries no information at all**, and printing "0.0% false failures across 340 clean
filings" is worse than printing nothing, because it has the shape of evidence.

Four corpus constructions, ranked, and each FFR carries which one produced it:

| Rank | Construction | What it yields | Status |
|---|---|---|---|
| **1** | **The blind-fill firewall.** Person A fills clean workbooks from the **template and regulation only**, never having seen the predicate set; Person B authors predicates never having seen A's workbooks; neither sees the other until measurement | An FFR that *can* be non-zero, therefore one that carries information. **This is the minimum bar below which no FFR may be printed anywhere in the product** | buildable this week |
| **2** | **The template's own native formulas as an externally-authored oracle.** All 505 formula cells carry cached values. Fill the inputs; let the workbook compute the derived cells. **A predicate that fires on a cell IFSCA's own artifact computed is a genuine false failure, because the ground truth was authored by the regulator** | Covers arithmetic predicates only. Denominator: 138 checkable relations over 505 formula cells | **MEASURED-ready — the artifact and its cached values are on disk** |
| **2b** | **The live register as a real clean corpus for one predicate class.** Every entity in the IFSCA register is validly registered, so the register *is* clean by definition. **Measured: the registration-number regex any competent engineer would write fires on 87 of 228 live FMEs — a 38.2% false-failure rate, on real data, today** | The only genuinely non-synthetic FFR available before the residency. **The synthetic-corpus caveat does not apply to this predicate class** | **MEASURED** |
| **3** | **Privacy-preserving FFR from a real FME partner.** Runs client-side; the FME returns only aggregate firing counts per predicate, never data | The one number that matters. `n` will be tiny (1 FME × 4 quarters = 4 filings) — fine, if reported as an interval | needs a partner we do not have |
| **4** | **Differential testing between prescribed formats.** Where two of the prescribed workbooks ask for the same quantity in different shapes, **the pair is an oracle** with no corpus required. All nine are on disk | Also serves the transfer question (§3.9) | runnable today |

**The only honest rendering of an FFR:** `(rate, corpus_id, corpus_provenance, n)` plus a two-sided Wilson
interval, inline, never in a tooltip. `corpus_provenance ∈ {SELF-AUTHORED, BLIND-FILLED, TEMPLATE-COMPUTED,
REGISTER-DERIVED, REAL-PARTNER, PUBLIC}`. **`SELF-AUTHORED` renders as `—` and the word `uninformative`. Not a
number. The schema forbids it.**

**And the architecture's own sentence must be corrected.** *"A check whose error rate is unknown is not admitted
— which makes the coverage claim true by construction"* becomes: **"the coverage claim is true to the extent the
admission measurements are valid, and each predicate carries the provenance of its own measurement."** Longer,
weaker, defensible.

**Pre-registered admission thresholds** (proposed, to be argued before first use): admit iff `K/O ≥ 0.80` on the
fault classes the predicate *claims* to cover, **and** Gate 2 returns non-degenerate or an empirical falsifying
witness exists, **and** `FFR ≤ 0.10` with `n` and `corpus_provenance` stated, **and** the marginal FFR
conditioned on the already-admitted set is reported using the interaction bound
`max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`.

**Held-out slice, mandatory:** a *structurally distinct* slice of the clean corpus (e.g. filings for a scheme
type absent from the fitting slice) with FFR reported on it separately. Without it, every FFR printed is an
upper bound on our own optimism.

**Status: GATE 1 BUILT** (19,782 mutants, 2.5 s, `KR` reported with its equivalent term) · **GATE 2 partially
built** (the vacuous-bound rejection is built; Z3 is specified) · **GATE 0 and GATE 3 SPECIFIED.**

---

### 3.6 OFFLINE E — REGISTRY ADMISSION

| Step | What happens |
|---|---|
| **R1** | The AST walker enforces the admitted CEL grammar and **verifies `schema_keys` against the AST both ways** — a predicate that reads an undeclared key, or declares a key it does not read, is **rejected**. This is what makes coverage computable |
| **R2** | Host-function references are checked against the closed registry. An unregistered function → rejected |
| **R3** | The ILP selects a minimal set subject to `Coverage(F′) ≥ α, FFR(F′) ≤ τ`; the subsumption DAG (from Z3) removes predicates implied by others |
| **R4** | **Liveness witnesses are emitted and stored with the predicate:** a `kill_case` (a mutant it is known to reject) and a `pass_case` (a clean artifact it is known to accept). F10 replays the `kill_case` on every filing |
| **R5** | The row is written **append-only**. Supersession is a new row, never an update |
| **R6** | The **registry root** is recomputed: a binary Merkle tree over the sorted `code_sha256` of admitted predicates, with domain separation (`0x00` leaf, `0x01` internal) |
| **R7** | **A human signs the admission batch.** The gate is mechanical; the decision to ship a check that will be applied to a regulated filing is not |

**A predicate whose `qualification` block is absent does not load.** *"A check whose error rate is unknown is
not admitted"* is a schema constraint, not a discipline — and there is a test that attempts the admission and
asserts the rejection.

**What is recorded when a candidate is rejected, and this is not optional:** the rejecting gate, the measured
number that rejected it, the pairs it would have covered, and the obligation it claimed. That record populates
`NO_PREDICATE(failed_qualification)` and the `counterEvidence` array. **Documenting what argues against your
conclusion is mandatory in audit documentation, and we were going to discard exactly that information.**

---

### 3.7 OFFLINE F — RE-QUALIFICATION ON CHANGE

**The problem is live, not hypothetical.** Three artifacts, three vintages: the FME workbook is dated **02 Jan
2026**; the FM Regulations are consolidated **as amended to 30 Jan 2026**; and the **29th IFSCA Authority Meeting
of 24 Jul 2026** decided that the periodicity of NAV computation by close-ended Restricted Schemes *"may be
enhanced by the FME from semi-annual to annual, subject to prior approval of at least 75% of the investors in
the scheme by value of their investments"*, and that independent valuation *"shall be relaxed for the investments
made in underlying scheme(s) which are valued by an independent entity."*

That lands directly on the two most sophisticated predicates in the decidable set. Before 24 Jul 2026,
predicate #17 was pure date arithmetic; after it, the owed frequency depends on **whether 75% of investors by
value approved — a fact the workbook does not collect.** The predicate does not error and does not abstain. It
keeps computing a date difference against a rule that no longer exists: **a filer who lawfully moved to annual
gets a false failure; a filer who moved without approval gets a silent pass. Both outputs are clean, confident
and well-formed.**

**The policy, seven rules:**

1. **Keys are label-anchored, never coordinate-anchored** (T6). A version bump is a **re-resolution**, not a
   rewrite. Unresolvable keys enter `UNRESOLVED` and block their predicates.
2. **Every predicate carries a `qualified_against` record and it is part of its identity:** template sha256 and
   label, regulation version, circular-corpus snapshot, count of unreadable circulars, corpus id, corpus
   provenance, `n`, harness version, evaluator version, and — for L3-proposed predicates — **the model
   identifier, the date, and the prompt hash**, so a re-synthesis under a drifted model is a diff and not a
   mystery.
3. **Any change to any element of `qualified_against` moves the predicate to `PROVISIONAL`.** It still runs, so
   detection is not lost; its measured numbers are hidden and replaced by *"not re-qualified for this template
   version"*; and **it does not count in the coverage numerator.**
4. **Therefore coverage falls when the world moves. "Grows monotonically" is deleted from the architecture**,
   and the coverage-over-time chart must be able to step down. **The step-downs are the most credible thing on
   that chart, because they are the only evidence the system notices when the world moves.**
5. **Liveness witnesses are re-run on every version change and on every filing** (F10). A predicate whose
   `kill_case` no longer dies is quarantined automatically. **This alone does not catch a rule change** — the
   mutant and the predicate move together — which is why rule 6 exists.
6. **Watch the instrument stream, not just the instrument** (§3.8). Any new instrument citing a regulation a
   predicate claims to implement puts that predicate into `PROVISIONAL` **automatically and pessimistically**;
   a human clears it. This is a diff-and-flag job, not an NLP problem, and it is the only mechanism that would
   have caught 24 Jul 2026.
7. **Carry the 10 unreadable circulars as a permanent declared gap** — `coverage_gap: 10/399 sources unread
   (scanned images)` — on every predicate whose correctness rests on the full-text negative result. Or OCR them,
   which is an afternoon.

**One scheduled version event is already known:** the template's financial-year vocabulary is
`Dropdown!$E$3:$E$6 = {2025-26, 2026-27, 2027-28, 2028-29}`. **The workbook cannot express FY2029-30.** Version
churn here is not a risk; it is on the calendar.

---

### 3.8 OFFLINE G — THE INSTRUMENT-STREAM WATCHER

- **What:** a daily fetch of IFSCA's circular list, Authority-meeting page and download page; content-hash each;
  diff against the last snapshot.
- **Out:** new-instrument events; template-hash-change events (→ §3.2); a signed watch log.
- **Determinism:** the diff is deterministic; the fetch is not, so every snapshot is content-addressed with its
  timestamp and endpoint.
- **Failure:** a fetch failure is recorded as a **gap in the watch log with its duration**, never as "no
  change". An unobserved day is not a quiet day.
- **Human:** yes — a human clears every `PROVISIONAL` flag the watcher raises. The watcher never re-admits.
- **Status: SPECIFIED.**

---

### 3.9 OFFLINE H — THE RESIDUE SET (the boundary measurement)

This is the object that answers three separate attacks at once, and it is the research deliverable.

```
1. Take the filing under test, F.
2. Generate mutants of F under a declared, versioned fault model.
3. Adjudicate each: INNOCUOUS (still correct) / WRONG (materially false).      <- the only human step
4. Run the full admitted predicate set + all admitted relations on every WRONG mutant.
5. RESIDUE := { WRONG mutants that no predicate and no relation rejects }
6. Report |RESIDUE| and, for each survivor, the class of falsehood it represents.
```

**Why it belongs in the design rather than in an appendix:**

- **It cannot be inflated by boring checks.** Adding 505 recompute predicates does not shrink the residue,
  because the residue is populated by falsehoods consistent with every arithmetic relation in the file. This is
  the property a coverage fraction lacks — a coverage fraction moved from 71% to 98.8% in one afternoon without
  a single interesting check being written.
- **It converts a hand classification into a measurement.** The 17-of-24 split was produced by one person
  deciding what is decidable. The residue set is produced adversarially and a third party can re-run it.
- **It makes 100% coverage structurally unreachable**, because the residue count is never zero and it is a
  permanent row in the denominator.
- **It is the honest content of the Unchecked panel.** Today that panel lists reasons. It should list
  *demonstrated survivors*: "a coordinated 0.05% misstatement propagated through all 181 carries and all 135 SUM
  identities survives every admitted check — here it is."
- **The class it names has no analogue in code mutation testing.** An **undetectable-in-principle** mutant makes
  the filing factually wrong while leaving it internally perfect. In code, a mutant that changes behaviour is in
  principle killable by *some* test. Here, a mutant can change the *truth* of the artifact and be provably
  unkillable by any predicate over the artifact alone. **That third class is the product** — it is the measured
  boundary the problem statement says does not exist anywhere.

**Status: SPECIFIED, and nothing blocks it.** Steps 1, 2, 4, 5 are mechanical on machinery that already runs;
step 3 is one-time per fault-model version.

---

### 3.10 WHERE A HUMAN IS REQUIRED — consolidated

| # | Decision | Why it cannot be automated | Frequency |
|---|---|---|---|
| 1 | **Template admission sign-off** (§3.2 T7) | It fixes the denominator every subsequent number is a fraction of | per template version |
| 2 | **Function-vocabulary decision** (§3.2 T5) | Choosing between "implement it", "mark those cells unchecked" and "promote the second engine" is a trade-off, not a computation | per template version |
| 3 | **Promoter failures and unresolved amendment chains** (§3.3) | 8% of amending circulars cite a target that does not resolve mechanically | per regulation update |
| 4 | **Host-function authoring** (L09 §A.8) | A host function is the only impurity in the language. **It may be added only by a human and is never generated by a model** | rare, and the set stays small |
| 5 | **Metamorphic relation authoring** (§3.1 F9) | Measured: model-generated relations recapitulate the textbook classes. Every relation worth having was read off a guidance note or a formula | per template |
| 6 | **Blind-fill corpus construction** (§3.5 Gate 3) | The firewall *is* the measurement. **This is also the expensive input — it is human time, and no amount of model spend substitutes for it** | per template |
| 7 | **Predicate admission batch signature** (§3.6 R7) | The gate is mechanical; shipping a check that will be applied to a regulated filing is a decision | per admission batch |
| 8 | **Clearing a `PROVISIONAL` flag** (§3.7 rule 6, §3.8) | Automatic and pessimistic flagging; only a human re-admits | per instrument event |
| 9 | **INNOCUOUS vs WRONG adjudication** (§3.9 step 3) | The only judgment in the residue construction, one-time per fault-model version, and auditable | per fault-model version |
| 10 | **`INVALID` run triage** (§3.1.1) | An engineering incident, not a filing outcome | exception |
| 11 | **Override entry** (XCCDF Table 27) | Both states are retained, the remark and the actor are recorded, and the override sits **inside the signed payload**. Overrides are a first-class number a supervisor will want | exception |
| 12 | **The go/no-go on L3** (§3.4) | Pre-registered, recorded in the repo on the date it was taken, **whichever way it goes** | once |

**Nowhere in this table does a human adjudicate a PASS.** Humans admit checks, author relations, fix the
instrument and clear flags. **The verdict itself is never negotiated.**

---

## §4 — THE DATA MODEL

### 4.1 Content addressing

**Scheme.** `sha256` over exact bytes, lowercase hex, stored at `blobs/sha256/<first-two-hex>/<remaining-62>`.
No compression, no re-encoding, no normalisation. **The bytes we hash are the bytes we received.**

**What is content-addressed, and every one of these appears in the run manifest:**

| Object | Digest of | Why it must be pinned |
|---|---|---|
| Filing | the exact uploaded bytes | the subject |
| Each worksheet inside it | `xl/worksheets/sheetN.xml` | so a re-derivation can say *which sheet* changed, not just that the file did |
| Blank template | the published bytes from `ifsca.gov.in` | **a verdict against template v3 is meaningless if the entity filed on v4** |
| `TemplateSchema` | its canonical JSON serialisation | the denominator |
| Predicate | the canonical serialisation of its envelope | the check |
| Host function | its source text + its test-suite result vector | the impurity, versioned |
| Relation (L6) | its canonical serialisation | same as a predicate |
| Registry root | Merkle root over admitted `code_sha256` | the exact check set |
| Regulation PDF | the published bytes | so `frbr_uri@as_at` resolves to bytes |
| **Register snapshot** | the full list response + every detail response | **the register is mutable and undated; a verdict citing "the register" without a snapshot hash is not reproducible and cannot be signed** |
| Mutant | the mutated workbook bytes | so a quoted kill rate is reproducible or it is not quoted |
| Report | the rendered HTML | the attested artifact |

**Registry root construction.** Sort admitted predicates by `code_sha256` ascending; leaf = `sha256(0x00 ‖
code_sha256)`; internal node = `sha256(0x01 ‖ left ‖ right)`; odd node promoted unchanged. Domain separation is
not decoration — without it a leaf and an internal node are confusable.

**Canonical serialisation** for every hashed JSON object: RFC 8785 JSON Canonicalisation Scheme. **Stated
explicitly because "the sha256 of the JSON" is not a definition**, and two implementations that disagree on key
order produce two roots for one registry.

### 4.2 Tables (SQLite; portable SQL so the Postgres migration is mechanical)

```sql
-- ── artifacts ────────────────────────────────────────────────────────────────
blob(sha256 PK, n_bytes, media_type, first_seen_at, origin_uri, retrieved_at)

template(template_sha256 PK, label, published_at, fetched_at, origin_uri,
         structural_fingerprint, admitted_at, admitted_by, superseded_by NULL)

template_sheet(template_sha256 FK, sheet_index, sheet_name, sheet_state,
               sheet_sha256, protected, dimension, PRIMARY KEY(template_sha256, sheet_index))

field(template_sha256 FK, stable_key PK-part, sheet_name, merged_header_path, row_label,
      resolved_ref, dtype, unit, is_unlocked, is_formula, in_field_surface,
      resolution_state)          -- RESOLVED | UNRESOLVED

vocabulary(template_sha256 FK, vocab_key, source_ref, terms_json, term_count,
           wired_by_validation)  -- BOOLEAN; the 15-vs-22 mapping this asserts (see §7.3)

validation(template_sha256 FK, seq, namespace, -- 'main' | 'x14'
           type, sqref, formula1, resolved_vocab_key NULL, cell_count)

carry_edge(template_sha256 FK, src_ref, dst_ref, formula_text, encoding)
           -- encoding: TEXT | SHARED_MASTER | SHARED_DEPENDENT | ARRAY

-- ── regulation ───────────────────────────────────────────────────────────────
instrument(frbr_uri PK, title, as_at, pdf_sha256, page_count, promoter_version)
clause(frbr_uri FK, eId PK-part, text, page_no, bbox_json, charspan_json,
       provisos_json, xrefs_json)
amendment(source_frbr_uri, target_frbr_uri, target_eId, effective_date, resolved BOOLEAN)

-- ── the registry ─────────────────────────────────────────────────────────────
predicate(predicate_id, version, PRIMARY KEY(predicate_id, version),
          kind,                    -- harvested | proposed | hand_authored | relation
          template_sha256, frbr_uri NULL, eId NULL, clause_span_json NULL,
          envelope_json, code_sha256, schema_keys_json, host_fns_json,
          state,                   -- ACTIVE | PROVISIONAL | WITHDRAWN | REJECTED
          severity_tier,           -- BLOCKING | ADVISORY   (set by measured FFR)
          admitted_at, admitted_by, superseded_by NULL)

qualification(predicate_id, version, PRIMARY KEY(predicate_id, version),
  gate0_scope_faithful BOOLEAN, gate0_provisos_declared INT, gate0_provisos_implemented INT,
  kr_killed INT, kr_observable INT, kr_generated INT, kr_unobservable INT, kr_unreachable INT,
  kr_by_fault_class_json, fault_model_version, harness_version,
  gate2_method,            -- 'z3' | 'empirical' | 'both'
  gate2_verdict,           -- 'non_degenerate' | 'trivially_true' | 'always_flag' | 'unknown'
  gate2_witness_sha256 NULL,
  ffr_fired INT, ffr_n INT, ffr_wilson_lo REAL, ffr_wilson_hi REAL,
  ffr_corpus_id, ffr_corpus_provenance,   -- SELF-AUTHORED | BLIND-FILLED | TEMPLATE-COMPUTED
                                          -- | REGISTER-DERIVED | REAL-PARTNER | PUBLIC
  ffr_heldout_fired INT NULL, ffr_heldout_n INT NULL,
  marginal_ffr REAL NULL, conditioned_on_json NULL,
  kill_case_sha256, pass_case_sha256,     -- the liveness witnesses
  qualified_against_json,                 -- see §3.7 rule 2, incl. model id + prompt hash
  qualified_at)
-- INVARIANT, enforced by the loader: a predicate row with no qualification row DOES NOT LOAD.

rejection(candidate_sha256 PK, predicate_id NULL, frbr_uri, eId, rejecting_gate,
          measured_json, pairs_would_have_covered INT, rejected_at)
-- this table IS `no_predicate.failed_qualification` and the counterEvidence array

host_function(name, version, PRIMARY KEY(name, version), source_sha256, signature,
              returns_tristate BOOLEAN, test_vector_sha256, mutation_score_json, authored_by)

registry_root(root PK, computed_at, n_predicates, predicate_ids_json)

-- ── runs ─────────────────────────────────────────────────────────────────────
run(run_id PK, filing_sha256, template_sha256, registry_root, register_snapshot_sha256 NULL,
    run_state,               -- VALID | INVALID | REJECTED
    aggregate_verdict NULL,  -- EXCEPTIONS_NOTED | ADVERSE
                             -- | EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE | COVERAGE_INSUFFICIENT
    invalid_reason NULL, canaries_run INT, canaries_passed INT,
    started_at, finished_at, manifest_json, report_sha256, attestation_sha256)

run_item(run_id FK, pair_id,           -- "<stable_key>×<obligation_id>"
         predicate_id NULL, predicate_version NULL,
         state,                        -- 8 values, §4.5
         reason_code NULL,             -- 30 values, §4.5; REQUIRED iff state not in (PASS,FAIL)
         method,                       -- RECOMPUTE | TIE_OUT | SCHEMA_BIND | REGISTER_LOOKUP
                                       -- | CLAUSE_TEST | METAMORPHIC | MODEL_EXTRACT | UNKNOWN
         warrant,                      -- MEASURED | MODELED | ASSERTED | UNCHECKED
         provenance,                   -- COMPUTED | GATHERED
         cells_bound INT, witness_json NULL, elapsed_us,
         PRIMARY KEY(run_id, pair_id))
-- CONSTRAINT: method='MODEL_EXTRACT' AND state='PASS' is rejected at write time.

override(run_id FK, pair_id FK, old_state, new_state, remark, actor_id, decided_at,
         evidence_sha256)

extraction_manifest(run_id FK, reader, parts_read_json, parts_skipped_json,
                    namespaces_json, constructs_not_understood_json, agreement_json)

register_snapshot(snapshot_sha256 PK, endpoint, fetched_at, n_records,
                  list_response_sha256, detail_response_shas_json)

instrument_watch(observed_at PK, endpoint, content_sha256, changed BOOLEAN,
                 gap_since NULL, predicates_flagged_json)
```

### 4.3 The predicate envelope

A predicate is **not** a CEL expression. It is a small, signed, content-addressed record *containing* CEL
expressions. The envelope is what makes non-settlement a first-class evaluation outcome instead of an exception.

```yaml
# predicate/P-0041.yaml — content-addressed by sha256 of its RFC-8785 canonical serialisation
id:            P-0041
version:       3
kind:          harvested                  # harvested | proposed | hand_authored | relation
template:      sha256:7d9a1960085785ee…    # the PINNED blank this predicate is bound to
schema_keys:   ["intro.tbl15.row[*].scheme_type", "vocab.scheme_type"]
                                          # DECLARED, and machine-checked BOTH WAYS against the AST
host_fns:      []                         # closed, versioned set; unregistered -> rejected
clause:
  instrument:  "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30"
  eId:         "sch_3__part_A__point_g"
  span:        [10422, 10597]             # exact character span — GATE 0 requires it
  provisos:    ["Provided that ... fund of funds ..."]   # enumerated; each implemented or declared
  quote:       "Type of Scheme"
rationale:     "Every declared scheme type must be a term the published template offers."

applicable: >                             # CEL -> bool. false => OUT_OF_SCOPE(reason_if_inapplicable)
  size(filing.intro.tbl15.rows) > 0
expr: >                                   # CEL -> bool. true => PASS, false => FAIL
  filing.intro.tbl15.rows.all(r,
    r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)
witness: >                                # CEL -> list. what to show on FAIL
  filing.intro.tbl15.rows.filter(r,
    r.scheme_type != "" && !(r.scheme_type in template.vocab.scheme_type)).map(r, r.__cell__)

reason_if_inapplicable: "out_of_scope.not_applicable: no schemes declared"
tolerance:      null                      # for arithmetic predicates: {"tau_units_per_summand": 5}
severity_tier:  ADVISORY                  # set by measured FFR, never by hand

qualification:                            # written by L4. NOT hand-editable. Absent => does not load.
  admitted:     "2026-08-14"
  gate0:        {provisos_declared: 1, provisos_implemented: 0, declared_unchecked: 1}
  gate1:        {killed: 41, observable: 44, generated: 61, unobservable: 17, unreachable: 3,
                 by_fault_class: {F2: 1.00, F5: 0.00, F12: 0.93},
                 fault_model: "v3", harness: "1.2.0"}
  gate2:        {method: "z3+empirical", verdict: "non_degenerate",
                 witness: "sha256:…", control_arm_spurious: 0}
  gate3:        {fired: 2, n: 96, rate: 0.021, wilson: [0.006, 0.074],
                 corpus_id: "blind-fill-v2", corpus_provenance: "BLIND-FILLED",
                 heldout: {fired: 1, n: 22, wilson: [0.001, 0.216]},
                 marginal_ffr: 0.010, conditioned_on: ["P-0007"]}
  liveness:     {kill_case: "mutants/P-0041-kill.xlsx", pass_case: "clean/blind_fill_017.xlsx"}
  qualified_against:
    template_sha256: "7d9a1960085785ee…"
    regulation_version: "2026-01-30"
    circular_corpus_snapshot: "2026-08-10T00:00Z"
    circulars_unreadable: 10
    evaluator_version: "0.4.1"
    proposer: null            # for kind=proposed: {model, date, prompt_sha256}
```

**Three properties no framework in the ecosystem has:**

1. **Non-settlement is produced by evaluation, not by exception.** `applicable` is a *predicate about
   applicability*, evaluated first, with its own semantics. A predicate that does not apply is not a failure and
   is not a pass — it is removed from the denominator **with a stated reason**.
2. **`schema_keys` is declared and then machine-checked both ways.** That is what makes coverage computable, and
   it is a static check only because the language has no variables.
3. **`qualification` is required by schema.** *"A check whose error rate is unknown is not admitted"* is a
   loader constraint, not a discipline.

### 4.4 The coverage object — never a bare fraction

```jsonc
"coverage": {
  "denominator": { "source": "induced-from-template-unlocked-mask",   // NOT negotiated
                   "fieldSurface": 3747,
                   "computedTwiceAgreed": true,
                   "obligationsTotal": 41,
                   "pairsTotal": 4021 },
  "outOfScope":    214,                 // removed from the denominator
  "informational":  38,                 // removed from the denominator
  "inScope":      3769,                 // <- THE denominator
  "settled":   { "pass": 2361, "fail": 12, "total": 2373 },
  "unsettled": { "indeterminate": 41, "notRun": 88, "noPredicate": 1267, "error": 0 },
  "coverageFraction": 0.6296,           // meaningless without the six counts above
  "residue":   { "survivors": 12, "faultModel": "v3" },   // never zero -> 100% unreachable
  "aggregate": "incomplete",
  "denominatorWarning":
    "Out-of-scope determinations are filing-specific, so the denominator varies between filings.
     Coverage fractions are not directly comparable across filings."
}
```

**One deliberate divergence from the closest prior art, and it is the most important scoring decision in the
design.** XCCDF removes `notchecked` (no check exists) from its denominator. **We keep `noPredicate` in.**
XCCDF's denominator is a benchmark a human authored, so "no check exists" means the author chose not to have
one. **Ours is induced from the regulator's own template, which is authoritative and complete — so "no predicate
exists" is a gap in *us*, not in the specification.** Removing it would let coverage rise by doing nothing.

**Absent ≠ empty ≠ zero**, and the JSON Schema must distinguish all three: `[]` means *we determined there are
none*; `null` means *we make no claim*; an omitted field is a **schema violation** the validator rejects.

### 4.5 The state and reason vocabulary

**8 states, closed.** In the coverage denominator unless marked.

| State | Meaning | Denominator |
|---|---|---|
| `PASS` | predicate ran, condition held | ✅ settled |
| `FAIL` | predicate ran, condition did not hold | ✅ settled |
| `INDETERMINATE` | predicate ran to completion, result not decidable | ✅ |
| `NOT_RUN` | predicate is admitted and in scope, but did not execute | ✅ |
| `NO_PREDICATE` | pair in scope, no *qualified* predicate covers it | ✅ **(divergence above)** |
| `ERROR` | the checking apparatus failed here | ✅ **and the run becomes `INVALID`** |
| `OUT_OF_SCOPE` | does not apply to this filing, or excluded by this run's profile | ❌ removed |
| `INFORMATIONAL` | ran; the output is a value for the reader, not a verdict | ❌ removed |

**30 reason codes, closed and namespaced.** Required whenever the state is not `PASS`/`FAIL`. **Admission test
for a new code: two reasons are distinct if and only if they imply different remedies.** That test is why 30
beats the brief's 6 and also why it is not 60.

```
NO_PREDICATE (8) — we have no qualified check. This is the backlog and the permanent floor.
  .undecidable_by_construction   "correct" is undefined here (valuation appropriateness;
                                 whether a scheme is properly classified "infrastructure")
  .requires_judgment             a competent human can decide; no program can
  .not_yet_synthesised           decidable in principle, nobody has written it  <- the growable set
  .failed_qualification          a predicate WAS written and L4 rejected it; carries the gate
                                 and the measured number
  .rule_ambiguous                the obligation does not determine a testable condition
                                 (reg 51(1): "in such manner as specified by the Authority")
  .no_obligation_specified       the instrument is clear and simply says nothing — e.g. two of
                                 nine legal scheme types have no NAV-frequency rule at all.
                                 NEVER conflate with .not_yet_synthesised: "the regulator did not
                                 legislate this" vs "we haven't got round to it"
  .rule_withdrawn                previously admitted; its FFR later exceeded threshold or its
                                 clause was amended
  .not_yet_requalified           PROVISIONAL: an element of qualified_against changed

NOT_RUN (10) — we have a check; it did not run. Every one is an ops or data problem.
  .input_unavailable.counterparty     needs data held by a party who is not the filer
  .input_unavailable.register         live register unreachable or ambiguous at run time
  .input_unavailable.prior_period     needs a filing we do not hold
  .source_unreadable                  the artifact or a region could not be parsed
  .template_unbound                   L1 could not bind to a published template — ESCALATES
  .deactivated                        admitted but deliberately switched off, with a decision record
  .budget_exhausted                   time or cost limit reached before this pair
  .external_source_lacks_field        the external source no longer carries the field the predicate
                                      reads — measured live: the register LIST endpoint returns
                                      RegistrationNumber = null on 650 of 650 fund rows
  .external_source_unavailable        the external source was down at filing time
  .extractor_disagreement             two readers disagree on this field's structure

INDETERMINATE (4) — the check ran and could not decide.
  .extraction_abstained         L2b conformal set was not a singleton — the designed abstention
  .tolerance_straddle           the result sits inside the band where both answers are admissible
  .conflicting_sources          two admitted sources disagree, no published tie-break
  .engine_disagreement          the two recalculation engines disagree on this cell

OUT_OF_SCOPE (3) — removed from the denominator, therefore the most abusable.
  .not_applicable   requires a machine-checkable pointer to the schema condition making it inapplicable
  .not_selected     requires a pointer to the named run profile and its digest
  .withheld         requires an actor + rationale; COUNTED AND DISPLAYED SEPARATELY, never folded in

ERROR (5) — the apparatus failed. Any one of these sets run_state = INVALID.
  .predicate_raised   .cells_bound_zero   .canary_silent
  .closure_violated   .parser_disagreement_structural
```

**Severity is orthogonal to state**, not a ninth value: each predicate carries `BLOCKING | ADVISORY`, **set by
its measured FFR**, with the number printed next to it. That is the EBA's warnings-first convention with the
measurement put back in — and it is defensible to a supervisor on day one, because they already run the
unmeasured version. **`override` is likewise orthogonal**: it changes the result and is recorded beside it,
inside the signed payload, with both states retained.

**A metamorphic relation that lawfully fails on one column does not need a ninth state either.** It is
`INFORMATIONAL` carrying `advisory: {relation, lawful_exception_quote, clause}` — the quoted guidance note that
makes the exception lawful.

### 4.6 The attestation

```jsonc
// DSSE envelope, payloadType "application/vnd.in-toto+json"
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    { "name": "filing",   "digest": { "sha256": "…" } },
    { "name": "template", "digest": { "sha256": "7d9a1960085785ee…" } }
  ],
  "predicateType": "https://<ns>/filing-coverage-attestation/v1",
  "predicate": {
    "assessor": { "id": "https://<ns>/verifier/0.4.1",
                  "thirdParty": false,          // we are a self-assessment tool. Saying so is required.
                  "components": { "registryRoot": "…", "schemaInducerVersion": "1.4.0",
                                  "evaluatorVersion": "0.4.1", "extractorModel": null } },
    "timeVerified": "2026-08-10T09:12:44Z",
    "expires": "2026-11-10T00:00:00Z",
    "runState": "VALID",
    "livenessProof": { "canariesRun": 280, "canariesPassed": 280 },
    "scope":      { /* §4.4 denominator */ },
    "items":      [ /* §4.2 run_item, one per pair */ ],
    "coverage":   { /* §4.4 */ },
    "counterEvidence": [ /* every L4 rejection that would have covered pairs in scope */ ],
    "verdict":    { "state": "EXCEPTIONS_NOTED", "policy": { "K": 3, "T": 0.45, "version": "1.1" } },
    "boundedSilenceStatement": "Had additional predicates been executed, other matters might have
      been reported. This report states only the results of the predicates listed, and makes no
      representation that the predicate set is sufficient for any purpose.",
    "purposeStatement": "This report relates only to the fields enumerated in scope.denominator and
      does not extend to the filing taken as a whole.",
    "summaryIsNotSubstitute": true,
    "detectionBoundary": "This system detects error, not deception. Every check is a consistency
      check over a self-reported document. A coherent liar passes all of them."
  }
}
```

**There is no `result`, `status` or `pass` field anywhere in this schema, and there never will be.**
Schema-level prohibition beats copy discipline, because it survives the screenshot, the API integration and the
intern. The top-level object of the predicate is `scope`.

### 4.7 How a report is proven to re-derive exactly

The manifest embedded in every report's footer pins **eight** things, and each one is a thing that can silently
move:

```
{ template_sha256, filing_sha256, registry_root, register_snapshot_sha256,
  code_git_sha, evaluator_version, fault_model_version,
  tool_versions: { python, lxml, openpyxl, celpy, libreoffice, z3 } }
```

`verify` re-runs the pipeline pinned to all eight and asserts a byte-identical report. **The four sources of
non-determinism, and how each is removed:**

| Source | Removal |
|---|---|
| The mutable register | pinned by `register_snapshot_sha256`. **The host function never resolves live at verdict time** — it resolves against a content-addressed snapshot, or the report is not reproducible |
| Wall-clock time | every timestamp is an input recorded in the manifest, never read at evaluation time. CEL binds no clock |
| Dictionary/set iteration order | RFC 8785 canonical serialisation everywhere a hash is taken; all report ordering is by an explicit sort key |
| Floating point | there is none. Money is `int64` micro-units; tolerances are integers |

**A model call is never on the re-derivation path.** If a filing had attachments, the *facts* L2b produced are
content-addressed and pinned in the manifest; `verify` replays those facts, it does not re-call the model. That
is the only honest treatment: a model output is an input to the verdict, not a step of it.

---

## §5 — PERFORMANCE AND COST

### 5.1 Runtime per filing

Measured components are marked `M` (single run, cold, single process, on the operator's machine). Derived
components are marked `D` with the measured rate they were derived from. **Nothing here is a benchmark; the
numbers are small enough that precision does not matter and honesty does.**

| Step | Cost | Warrant |
|---|---|---|
| F0 receipt + blob write | ~10 ms | D (I/O) |
| F1 container guard | <5 ms | D |
| F2 reader A (`zipfile` + lxml, full structural parse) | **28–44 ms** | **M** |
| F2 reader B (openpyxl load) | **202 ms** | **M** |
| F2 reader C (LibreOffice normalise) — **conditional** | **3,900 ms** | **M** |
| F3 template binding | <1 ms | D |
| F4 fact-table construction (511 cells, dependency-ordered) | **1 ms** | **M** |
| F8 evaluation of 227 arithmetic predicates | **sub-millisecond** | **M** |
| F8 evaluation of all 280 predicates incl. 53 validations | ~2 ms | D |
| F9 metamorphic probes, 25 relations × 50 examples | **~160 ms** | D, from the measured 7,946 fact-table mutations/s |
| F10 canaries, 280 predicates | **~35 ms** | D, same rate |
| F11 coverage + closure (computed twice) | <5 ms | D |
| F13 render + sign | ~20 ms | D |

**Three honest totals, and the middle one is the number to quote:**

- **The deterministic core alone, as built today: ~30 ms.** L1 (28 ms) + synthesis (1 ms) + L5 (sub-ms). This
  is the measured figure and it is what makes "no queue" a measurement rather than a preference.
- **A complete online run with everything specified in §3.1, readers agreeing, no attachments: ≈ 450 ms**,
  dominated by openpyxl's 202 ms and the L6 probes' 160 ms.
- **Worst case, reader C invoked: ≈ 4.4 s.** LibreOffice is 90% of that. It is invoked only on reader
  disagreement or an unimplemented function.

**The 19,782-mutant L4 campaign runs in 2.5 s (7,946 mutants/second) — `M`** — but it is **offline**, per
template version, not per filing.

**What this settles architecturally:** the lane brief asked whether a queue is needed for a sub-60-second job.
The job is **sub-second**, so the question does not arise. Plain request/response. When a queue *would* be
justified — the L3 sweep and large L4 campaigns — those are offline and batch, so the answer there is the
Batch API plus a `Makefile`, not Celery.

### 5.2 Model token cost

**All prices VERIFIED-AT-SOURCE at `platform.claude.com/docs/en/about-claude/pricing`, fetched 10 Aug 2026,
per million tokens (MTok), USD.**

| Model | ID | Input | 5-min cache write | Cache hit | Output |
|---|---|---:|---:|---:|---:|
| Claude Opus 5 | `claude-opus-5` | $5 | $6.25 | $0.50 | $25 |
| Claude Sonnet 5 (**through 31 Aug 2026**) | `claude-sonnet-5` | $2 | $2.50 | $0.20 | $10 |
| Claude Sonnet 5 (**from 1 Sep 2026**) | `claude-sonnet-5` | $3 | $3.75 | $0.30 | $15 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1 | $1.25 | $0.10 | $5 |

**Batch API: 50% off both directions.** Cache multipliers: 5-min write 1.25×, 1-hour write 2×, cache read 0.1×.
Verbatim: *"These multipliers stack with other pricing modifiers, including the Batch API discount."*

**Two dated facts that must not survive unchallenged into a slide:**
1. **Sonnet 5's introductory pricing expires 31 August 2026 — the day before the residency starts.** Any L2b
   budget modelled at $2/$10 must be re-modelled at $3/$15.
2. **Opus 5 uses the newer tokenizer, which produces approximately 30% more tokens for the same text.** Every
   token estimate below is MODELED, not measured with `count_tokens`, and **must be re-baselined before it is
   quoted**, not multiplied by a guess.

**L3 — per template version, one-time, not per filing.** Assumptions stated so the arithmetic is auditable:
~6,000-token cached schema prefix, ~600 fresh tokens of clause text, ~1,500 output tokens per candidate.

| Path | Per candidate | × 24 obligations |
|---|---:|---:|
| Opus 5, no caching, no batch | $0.0705 | $1.69 |
| Opus 5, cached prefix | $0.0435 | $1.04 |
| **Opus 5, cached + Batch (50%)** | **$0.0218** | **$0.52** |

Plus a one-time 5-minute cache write of 6,000 tokens at $6.25/MTok = $0.0375. **Round figure: about $0.55 per
template version. Nine templates: under $6 for the entire IFSCA prescribed-format corpus**, paid once per
template revision.

**Experiment 9.1 v2, costed at the pre-registered design** (20 obligations × 10 candidates × 2 prompt regimes
= **400 candidates**), Opus 5 cached + Batch: `400 × $0.0218 = $8.70`, plus ~20 cache writes at the
batch-discounted $3.125/MTok × 6,000 tokens = $0.38. **≈ $9.10. MODELED.** The settling experiment for the
entire AI half of the architecture costs under ten dollars, which is the correct reason to run it before
elaborating anything on top of it.

**L2b — per filing, and only when unstructured attachments exist.** A 20-page PDF ≈ 25,000 input tokens,
~3,000 output tokens:

| Model | Per filing | × 868 filings/yr |
|---|---:|---:|
| Haiku 4.5 | $0.040 | **$35** |
| Sonnet 5 (standard, from 1 Sep 2026) | $0.120 | **$104** |
| Opus 5 | $0.200 | **$174** |
| Sonnet 5 via Batch | $0.060 | **$52** |

**The three headline numbers, and they should be said plainly on stage:**

- **Marginal model cost per filing on the workbook path: $0.00.** The 280 predicates, the coverage fraction, the
  canaries, the metamorphic probes and the verdict involve no model at all.
- **Annual model spend to process the entire measured population of ~868 filings: under $200**, even routing
  every attachment through Opus 5.
- **The cost that matters is not inference. It is the blind-filled qualification corpus** — human time, and no
  amount of model spend substitutes for it. **Do not pitch inference savings; pitch the boundary.**

### 5.3 Infrastructure cost

| Item | Cost |
|---|---:|
| Fly.io `shared-cpu-1x`, 512 MB (VERIFIED-AT-SOURCE) | **$3.32/month ≈ ₹290/month** |
| Storage at 868 filings/yr (3.66 MB workbook + ~200 KB report + attestation) | ~3.4 GB/yr |
| Model spend, all 868 filings, worst routing | <$200/yr |
| **Total annual run cost at the measured population** | **≈ $240 ≈ ₹21,000** |

**New Fly.io accounts get no free allowance** — the legacy free tier is closed to organisations created after
7 October 2024. Budget it. It is noise against a ₹1,00,000 milestone, and the demo must not depend on it: the
signed HTML report opens from disk with the network off.

### 5.4 At 868 filings a year, and at 100 times that

**868/yr is MODELED** — 217 FMEs × 4 quarters, assuming every FME files every quarter including those registered
mid-year. It is **~3.4 filings per working day.** At 450 ms each that is **1.5 seconds of compute per day.**

**This must be said out loud rather than hidden:** as a *deployment*, an eight-layer architecture with a
predicate registry, seeded-defect adequacy, metamorphic probes and signed attestation is absurdly
over-engineered for 3.4 documents a day. **As a research instrument it is not** — the layers are how the
measurement is made legible. The failure mode to avoid is presenting an instrument as a product. The honest
framing: *the IFSCA workbook is the testbed, not the market. It was chosen because it is public,
machine-readable, small enough to characterise exhaustively, and has a real regulator behind it — the properties
of a good experimental subject. The asset is the method.*

**At 86,800 filings a year (100×): 340 per working day, one every ~85 seconds at 8 h/day, ≈ 11 minutes of
compute per day.** Still trivially serial on one process. **Nothing about the request path breaks.** What breaks
first, in order, with the trigger and the replacement:

| # | What breaks | Trigger | Replacement |
|---|---|---|---|
| 1 | **Blob storage.** 3.66 MB × 86,800 ≈ **320 GB/yr**, plus mutants | disk, not throughput | Move blobs to object storage keyed by the identical `sha256` path; keep the manifest in SQLite. **The content-addressing scheme is unchanged, which is the point of choosing it** |
| 2 | **SQLite's single writer** | **concurrent uploads**, not row count — the registry is a few hundred rows at any scale | Postgres. The schema in §4.2 is portable SQL for exactly this migration. **Note what is lost: a Postgres cluster cannot be content-addressed, so the run manifest must then name a logical snapshot id instead of a file hash** |
| 3 | **The register snapshot.** A full refresh is ~2,235 polite GETs | you cannot snapshot per filing at 340/day | Snapshot **daily**; every predicate cites the snapshot hash **and its age**; a staleness bound is a predicate parameter, and exceeding it degrades to `NOT_RUN(input_unavailable.register)`. **Someone must read IFSCA's terms of use before any scheduled polling** — 2,235 GETs were made politely once, at 0.06–0.25 s spacing, with no terms review |
| 4 | **The LibreOffice tail.** 3.9 s × the disagreement rate | if disagreement is 5%, that is 17 invocations/day ≈ 66 s — fine. At 50% it is 11 minutes | Pre-warm a `soffice` daemon, or implement the missing functions in our evaluator. This is the only step with a genuinely bad constant |
| 5 | **The qualification corpus — and this is the real one** | **it does not scale with filings at all. It scales with *templates*** | Nothing technical. **This is the transfer question, and it is the experiment that decides whether this is a product or a paper:** what fraction of the FME predicate set transfers to a second prescribed format, and at what human cost per transferred predicate? Nine workbooks are already on disk; the threshold must be pre-registered. If transfer cost per predicate is not materially below authoring cost, the method does not generalise |

**What never becomes the constraint, at either scale: inference.** At 100× with every attachment routed through
Opus 5, the annual model bill is **$17,400** — real money, but it is the cheapest line in the table and it is
the one everybody expects to be expensive.

---

## §6 — THE INTERFACES

### 6.1 The API surface

FastAPI, `/v1`, JSON except where noted, OpenAPI generated. **No authentication before 30 October** — judges
will not sign up — except on the two mutating endpoints, which take an operator token.

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| `POST` | `/v1/filings` | `multipart/form-data`: `filing` (required, .xlsx), `attachments[]` (optional), `template_sha256` (optional), `profile` (optional named run profile) | `201 {run_id, filing_sha256, template_sha256, run_state, report_url, attestation_url}` | Synchronous. Median ~450 ms. `413` over the size cap, `415` on a non-zip, `422` if `template_unbound` — and a `422` body carries the structural fingerprint so the operator can admit the new template |
| `GET` | `/v1/runs/{run_id}` | — | the full `run` record incl. `coverage`, `verdict`, `livenessProof`, `manifest` | The canonical machine surface |
| `GET` | `/v1/runs/{run_id}/items` | `?state=&reason=&sheet=&predicate_id=` | paginated `run_item[]` | This is what a supervisor's triage tool consumes |
| `GET` | `/v1/runs/{run_id}/report.html` | — | `text/html`, **self-contained**, `Content-Disposition: attachment` | Byte-identical to the file on disk; its sha256 is in the manifest |
| `GET` | `/v1/runs/{run_id}/attestation.json` | — | the DSSE envelope (§4.6) | |
| `GET` | `/v1/runs/{run_id}/log.jsonl` | — | `application/x-ndjson`, one line per evaluation | |
| `POST` | `/v1/runs/{run_id}/overrides` | `{pair_id, new_state, remark, evidence_sha256}` + operator token | the updated item | **Both states retained.** Recorded inside the signed payload; counted and displayed separately |
| `POST` | `/v1/verify` | `multipart`: `report` or `attestation` | `{reproduced: bool, diff[]}` | Re-derives from the embedded manifest and byte-compares |
| `GET` | `/v1/templates` | `?state=` | `template[]` with `field_surface`, `n_predicates`, `coverage_ceiling` | `coverage_ceiling` is `null` for unprotected templates — **the absent-vs-empty rule applied to our own headline** |
| `GET` | `/v1/templates/{sha256}/schema` | — | the full `TemplateSchema` + the extraction manifest | The denominator, inspectable |
| `POST` | `/v1/templates` | `{origin_uri}` + operator token | `201 template` | Runs §3.2 T1–T6 and stops at T7 awaiting a human signature |
| `GET` | `/v1/predicates` | `?template=&state=&kind=&clause=&min_kr=&max_ffr=` | `predicate[]` with the **full qualification block**, including `ffr_corpus_provenance` | **This endpoint is the product's honesty, exposed.** It is public and unauthenticated by design |
| `GET` | `/v1/predicates/{id}/versions/{v}` | — | the envelope, the qualification block, the liveness witnesses, and the mutants it kills by fault class | |
| `GET` | `/v1/rejections` | `?template=&gate=` | every candidate L4 refused, with the rejecting gate and the measured number | The counter-evidence surface. **Nothing else in the category publishes this** |
| `GET` | `/v1/registry/roots` | — | `registry_root[]` with timestamps and predicate counts | |
| `GET` | `/v1/coverage/history` | `?template=` | the admission timeline, each step annotated with the predicate's measured rates | Feeds Screen 5. **Must be able to step down** |
| `GET` | `/v1/healthz` · `/v1/openapi.json` | — | — | |

**Two prohibitions, enforced by schema and by test:**

1. **No endpoint returns a boolean pass/fail, a `status: "clean"`, or a bare coverage number.** Every coverage
   figure is returned inside the object of §4.4, with all six counts. An API consumer that wants a single number
   must compute it themselves and will have the denominators in hand when they do.
2. **`GET /v1/predicates` renders `ffr` as `null` with `ffr_corpus_provenance: "SELF-AUTHORED"` when that is the
   provenance.** Not a number. A client cannot accidentally display an uninformative rate as if it were a
   measurement.

### 6.2 The CLI

The CLI is the primary interface during the residency; the API is the demo surface. Every command is
reproducible and writes content-addressed output.

```
ingest       <url|path>...            fetch, hash, store, manifest        [§3.2 T1–T2]
induce       <template_sha>           emit TemplateSchema + extraction manifest        [T3]
harvest      <template_sha>           emit candidate predicates from the schema alone  [T4]
propose      <template_sha> <clauses> L3 candidate proposal via the Batch API          [§3.4]
seed         <template_sha> --faults  generate + observability-filter the mutant set   [§3.5 G1]
qualify      <predicate...>           run gates 0–3; write the qualification block      [§3.5]
admit        <predicate...>           ILP + subsumption + Merkle root; requires a signer [§3.6]
run          <filing> [--attach ...]  the full online flow; writes report + attestation  [§3.1]
verify       <report.html>            re-derive and byte-compare                        [F14]
watch        [--since]                instrument-stream diff; flag predicates PROVISIONAL [§3.8]
residue      <filing> --fault-model   build and report the residue set                  [§3.9]
transfer     <template_a> <template_b> what fraction of A's predicates transfer, and at what cost
```

`make demo` runs `ingest → induce → harvest → run` against the workbook as published on `ifsca.gov.in`,
reproducing **63.3% coverage of 3,747 fields with 280 predicates and zero model calls**, on a judge's laptop,
offline after the fetch.

### 6.3 The screens

**One commitment governs all of them: there is no green tick anywhere in the product.** A surface that can
render "all clear" will eventually render it wrongly, and nothing in the output would distinguish that from
correct.

---

**Screen 1 — Drop.** One control. Accepts a workbook, optionally attachments. No settings, no options, no
account. On submit it shows the run state and the two hero counts; nothing else.

---

**Screen 2 — Report.** Shaped like a test run, because that is what it is.

**The hero is two counts of equal weight, side by side, same type size, same ink, no colour on either:**

```
   12 failures across 2,373 checks.        1,374 fields were not checked.
   ─────────────────────────────────       ─────────────────────────────────
```

The right-hand number is **never** smaller, never grey, never below the fold, never inside a collapsed panel.

- **No progress bar, no ring, no percentage in the hero.** A fixed-height **stacked band** with segments labelled
  by absolute count. **The unchecked segment is hatched, not muted** — muted reads as "resolved, minor"; hatched
  reads as "not filled in", which is the truth.
- **The band never fills**, because two permanent rows are inside the denominator: *"Outside the boundary —
  properties no predicate can settle from this artifact alone"* and *"Demonstrated survivors — corruptions that
  passed every check (residue set)"*. **100% is structurally unreachable.** That is architectural, not cosmetic.
- **Nothing renders green.** Passing checks take the same neutral ink as body text. Only failures take colour.
  *The absence of colour is not the presence of green.*
- **Under the band, always, one line, expandable:** `denominator from styles.xml unlocked mask v3 · predicate
  set v11 · registry root 9f3c… · qualified against template sha256:7d9a… · 4 predicates provisional · 280/280
  canaries passed`.
- **Each failure expands to four things:** both cells (the value and the cell it disagrees with), the clause it
  implements with its `eId` and a link to the exact page and bounding box, the predicate's CEL source, and —
  **the unusual part** — *that check's own measured false-failure rate*, rendered inline as
  `fired on 2 of 96 clean filings [0.6%–7.4%] · corpus: BLIND-FILLED, n=96`. **No compliance product tells you
  how often each of its rules cries wolf.**
- **A permanent, non-dismissible sentence:** *"This system detects error, not deception. Every check here is a
  consistency check over a self-reported document. A coherent liar passes all of them."*
- **When the run is `INVALID`**, the entire screen is replaced by the reason, the dead predicates, and no
  coverage figure of any kind.

---

**Screen 3 — The Unchecked panel.** Not an appendix. It sits on Screen 2, above the fold, and it is the
differentiator.

Grouped by reason code, each group carrying its count and, per entry, **"what would make this checkable"** — and
that text is specific, not generic. The canonical entry, and it is writable today:

> **Third Schedule Part A(g) — whether the valuation is appropriate.**
> Reason: `no_predicate.requires_judgment`.
> What would make it checkable: *a materiality threshold by scheme class, of the kind CSSF Circular 24/856
> Tables 1–3 specify (0.20% money-market / 0.50% bond and mixed / 1.00% equity and other), plus a
> compensation-direction rule of the kind its Tables 4–5 specify.*

**That is the Unchecked panel doing something no compliance product does: naming the specific instrument that
would move a predicate across the boundary, with the numbers.**

And beneath the reasons, the **demonstrated survivors** from the residue set — not reasons, but exhibits: *"a
coordinated 0.05% misstatement propagated through all 181 carries and all 135 SUM identities survives every
admitted check. Here it is."*

---

**Screen 4 — The predicate library.** Every admitted check, filterable, ≤515 rows, a plain `<table>`.

Per row: the clause (`eId` + quote), the CEL source, `KR = K/O` with both integers **and the per-fault-class
vector**, the degenerate-baseline result and its Z3 witness, the FFR with its corpus provenance, `n` and Wilson
interval, the severity tier, the admission date, and the liveness witnesses.

**And, next to each rule, what a flag-everything rule would have scored.** Every adjacent product competes on
rule *count*; this is the cheapest way to make a judge feel the difference — it is the `65.4 vs 66.2` result
rendered as a product surface.

**Two tabs the category does not have:**
- **Rejected** — every candidate L4 refused, the gate that refused it, the measured number, and the pairs it
  would have covered. This is where L4's rejections become visible instead of being discarded.
- **The attrition funnel**, per obligation: *candidates generated → executed → fired → non-degenerate →
  FFR-admitted*. **A 20:1 attrition ratio displayed honestly is a stronger demo than a coverage bar, because no
  competitor will show it.**

---

**Screen 5 — Coverage over time.** The demo, and it renders from a static JSON log with no live backend.

Coverage moving as predicates are admitted, each increment annotated with the predicate's measured rates.
**The chart must be able to step down**, and every step-down is labelled with what caused it — a template
version bump, a regulation amendment, an instrument-stream flag, an FFR that later exceeded threshold. **The
step-downs are the most credible thing on the chart**, because they are the only evidence the system notices
when the world moves. Beside it, plotted on the same axis, `R/O` — the fraction of observable defects no
admitted predicate can reach — which is the inverse curve.

---

**Who the two surfaces are for.** The filer's compliance officer runs this before submitting; the unit of value
is **the avoided deficiency** — the inspection observation, the rework, the Principal Officer's personal
exposure — and **that value is UNMEASURED.** The supervisor is **not** the buyer: the supervisory system is
procured. *The supervisor is why the filer cares.* The single question that decides whether the entity-facing
product is worth anything is **how often IFSCA returns an FME filing for correction**, and it is answerable by
one email to the Division of Investment Funds. **That email is the demand-side settling experiment and it should
be joint-first with the L3 experiment, not sixth in a queue behind three engineering questions.**

### 6.4 Build gates — the commitments that are tested rather than believed

A design commitment that is not tested is a preference. Each of these fails the build.

| Gate | What it asserts |
|---|---|
| `ci/no-green-tick.sh` | `grep -rniE '✓\|✔\|✅\|🟢\|all clear\|all-clear\|no issues\|looks good\|verified clean\|compliant\|passed all\|fully checked'` over `src/ templates/ locales/` returns nothing |
| `test_constants` | On the pinned FME sha256: **505** formula cells, **294** with bodies, **211** shared dependents, **54** validations, **22** list-type, **20** resolving, **3,747** field surface, **280** predicates, **252** merged ranges. A parser regression is loud |
| `test_denominator_provenance` | The coverage denominator is derived from the `styles.xml` unlocked mask and **not** from the predicate set. Asserted structurally, not by inspection |
| `test_ffr_provenance` | An FFR cannot be rendered without its corpus id, provenance, `n` and interval. `SELF-AUTHORED` renders `—` and `uninformative` |
| `test_unmeasured_predicate_rejected` | Attempt to admit a predicate with no qualification block; assert the rejection. **This is what makes the coverage claim structural rather than disciplinary, and it should be provable in one test** |
| `test_closure` | `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == pairsTotal`, or report generation aborts |
| `test_error_absorption` | A predicate written `true || <unreadable>` returns `NOT_RUN`, never `PASS` |
| `test_vacuity` | A predicate binding to zero cells returns `ERROR`, never `PASS`; `all([])` cannot produce a pass |
| `test_dual_reader` | Readers A and B disagree on a crafted fixture → the run is `INVALID`, loudly |
| `test_no_model_in_verdict_path` | Static check: no import of the model client is reachable from the L5/L6/L7 modules |
| `test_no_tlog` | The signing invocation carries `--tlog-upload=false` |
| `test_attestation_has_no_status_field` | The JSON Schema rejects any payload containing `result`, `status` or `pass` at any depth |
| `test_openpyxl_never_writes_the_artifact` | No code path re-serialises the received filing |

---

## §7 — WHAT IS NOVEL IN THIS STACK, WHAT IS ASSEMBLY, AND WHAT IS UNKNOWN

### 7.1 Assembly — cite it, do not claim it

Every part below exists, is documented, and a judge may know it. **Show the list rather than hide it.** A judge
who finds one of these after the pitch discounts everything; a judge handed all of them up front reads the team
as competent.

| Part of our stack | Prior art it comes from |
|---|---|
| LLM → executable assertions, with FFR as the selection criterion and an interaction bound | **SPADE**, arXiv:2401.03038 / PVLDB 17(12):4173–4186 |
| Non-LLM automatic rule synthesis | **Deequ** constraint suggestion (Apache-2.0, 3,638★); **Daikon** invariant mining |
| Seeded-defect operators for spreadsheets, and the unobservability problem | **Abraham & Erwig**, IEEE TSE 35(1):94–108, 2009 — 17 operators, **46.8% irreversible** |
| Mutation-score reporting discipline and suppression heuristics | **Petrović et al.**, IEEE TSE 2021 / arXiv:2102.11378 — 85% → 11% unproductive via learned suppression |
| Metamorphic relations derived from statute | **arXiv:2205.04998**, ICSE-SEIS 2023 — IRS Pub 596 / Sch 8812 / Form 8863 |
| The oracle problem and metamorphic testing as its principal answer | **Barr, Harman, McMinn, Shahbaz & Yoo**, IEEE TSE 41(5):507–525, 2015; Chen et al. 1998 |
| Deterministic adjudication of LLM output for a regulatory submission | **PROVE**, arXiv:2607.28218, 30 Jul 2026 — *independent convergence on our design thesis in clinical-trial reporting, eleven days before the corpus was compiled* |
| LLM-authors-rules + deterministic execution, and the Level-2 gap named | **"Confidently Wrong"**, arXiv:2607.23386 |
| An observability interface displaying per-constraint precision and recall | **"Semantic Integrity Constraints"**, arXiv:2503.00600 — our Screens 2/3 in a database paper, a year early |
| Nine per-item result states including `notchecked`, `notselected`, `notapplicable`, `error`, `unknown`, **and the denominator rules** | **XCCDF Table 26**, NISTIR 7275r4, NIST, 2012 |
| A completeness enum as a *required* field with an explicit `not_specified` state | **CycloneDX** `compositions.aggregate` (six states in 1.3, ten in 1.5–1.7) |
| `shall` issue an explicit code when a check is deliberately not performed | **C2PA 2.4 §15.9.2**, and its deprecation of a boolean `success` in v2.1 |
| Declaring the reasons you could not obtain evidence, and a whole verdict state for it | **ISA 705 (Revised) ¶¶7(b), 9, 17, 24** |
| The bounded-silence sentence, mandatory in every report | **ISRS 4400 (Revised) ¶30(j)**, with ¶30(h) disclaiming the *appropriateness* of the procedure set |
| Documenting what contradicts your conclusion | **PCAOB AS 1215 .08** |
| A false-positive-gated, publicly-reviewed rule registry over regulated financial filings, for a decade | **XBRL US Data Quality Committee** (Xule on Arelle) |
| Per-rule severity declared by the rule's author | **XBRL Assertion Severity 2.0**, REC 21 Jul 2022 (ERROR / WARNING / OK) |
| A regulator declaring which of its own rules are automatable | **ESMA ESEF**: an `Automatable Yes/No` flag per rule — 8 of 68 declared non-automatable, six of them mandatory |
| A regulator publishing that its own rules are wrong | **EBA** quarterly deactivation list — **8.23% of ~12,925 rules deactivated at least once**; **EIOPA**'s 243-item known-issues register |
| Coverage as a shipped metric | **dbt-coverage** (MIT, 241★) — coverage-as-presence |
| Signed attestation over an artifact; closed-world enforcement | **in-toto / DSSE / SLSA VSA**; in-toto's `DISALLOW *` |
| Model-free policy in a restricted expression language over structured data, in-process | **Kubernetes ValidatingAdmissionPolicy**, GA in v1.30 |

### 7.2 Genuinely new — five claims, each with what would falsify it

Stated narrowly on purpose. **Each is a claim about an absence, so each carries the scope of the search that
found the absence** — and each names the observation that would kill it.

**N1 — Measurement is the admission condition.** Not "we measured our rules", but *a rule with no measured
kill rate, no degeneracy verdict and no FFR-with-provenance is inadmissible, and the loader enforces it.*
Nothing in the sixteen commercial products opened, in SPADE, in PROVE, in the XBRL DQC, or in the assurance
standards has an admission gate.
> **Falsified by:** any shipped system in which a rule cannot enter the active set without a measured error
> rate. The DQC comes closest — it gates *for* false positives before publication — so the claim must always be
> stated as **the quantified, per-rule, published version of a discipline the DQC already practises
> qualitatively.** That is smaller, defensible, and it arrives with a named precedent.

**N2 — The per-rule false-failure rate rendered on the verdict surface, beside the failure it caused.** SPADE
computes FFR and consumes it internally; XBRL Assertion Severity declares the *author's intent* before anyone
runs the rule; the EBA publishes deactivations after the fact. **One is intent, one is a post-mortem; neither is
evidence attached to the finding.**
> **Falsified by:** one screenshot of any product showing a measured false-failure rate, with its denominator,
> next to a finding a user must act on.

**N3 — Per-field, closed-vocabulary, computed non-settlement for a financial artifact, against a denominator
induced from the regulator's own published template.** The assurance profession declares the boundary **in
prose, once, per report, about a procedure set whose adequacy it expressly disclaims.** XCCDF's denominator is a
benchmark someone wrote; OSCAL's is a catalog someone wrote; ISRS 4400's is a list someone agreed.
**Ours is mechanically recoverable from the blank template** — which is why a closed-world `DISALLOW *` is
possible for us and is not possible for any of them.
> **Falsified by:** a per-item, machine-readable coverage declaration for a financial filing, with a denominator
> the assessor did not choose.

**N4 — The residue set as a measured boundary.** A class of falsehoods, demonstrated on a real regulator's real
return, that survives every check anyone has written — with a size, a taxonomy and a reproduction. The problem
statement says no measured boundary exists between what a machine may be trusted to assert and what it may not.
**This is that boundary, produced adversarially rather than by hand classification, and a third party can re-run
it.**
> **Falsified by:** any published measurement of the surviving-falsehood class for a complete check set on a
> regulated return. **And weakened, honestly, by its own dependence on a human INNOCUOUS/WRONG adjudication** —
> which is why that step is one-time, versioned and auditable rather than continuous.

**N5 — The coverage fraction cryptographically bound to the template hash, the filing hash, the registry root,
and every predicate's measured rates.** CycloneDX allows a signature over a composition; no financial analogue
was found.
> **Falsified by:** a financial attestation carrying a coverage denominator.

**And one claim that is explicitly NOT made.** *"Nobody declares coverage"* is false and a judge with an audit
background may know it. The defensible sentence is: **the profession declares it in prose, once, per report,
about a procedure set whose adequacy it disclaims — we declare it per field, in a closed vocabulary, against a
denominator we derive from the regulator's own workbook, with a measured error rate on every check.**

### 7.3 Why the assembly is itself the contribution

**The test of whether an assembly is a design rather than a stack: can you remove one part and keep the claim?**

- **SPADE alone fails**, because its FFR needs labelled data its own paper says cannot exist in general.
  → **Seeded defects supply labelled dirty data by construction, at arbitrary n, with certain ground truth. The
  seeded fault *is* the label.** This is the load-bearing join.
- **Seeded-defect adequacy alone fails**, because it measures whether a check *can fire* and says nothing about
  the properties with no oracle. → **Metamorphic and differential relations settle a subset of those without an
  oracle**, so the boundary becomes measured and movable rather than philosophical.
- **Relations alone fail**, because an unqualified relation can be trivially satisfiable or trivially violated
  — the degenerate operating point where a flag-everything classifier beats the state of the art.
  → **The degeneracy gate rejects it.** This is why relations route *through* L4 and not around it.
- **All of them together still fail**, because a system that silently drops what it could not check has produced
  a false success by definition. → **The typed non-settlement vocabulary and the computed coverage fraction are
  the only outputs that make a false success structurally impossible to render**, because there is no green tick
  to render.
- **And the whole thing is worthless without short, stateless, model-free execution**, which is why there is no
  agent loop, no cross-step memory, no retry, and **why the registry — not the model — is the durable asset.**

Remove seeded defects → FFR is uncomputable and the gate is decorative. Remove the gate → coverage is an
assertion. Remove relations → coverage is a ceiling, not a growth curve. Remove typed non-settlement → it is a
linter. **No part is removable.**

---

## §8 — DECLARED GAPS

Stated in the form the product itself would use, because a specification that hides its own residue is refuted
by its own thesis.

### 8.1 Licences not read — must be opened before the code ships

| Item | State | Consequence if it goes the wrong way |
|---|---|---|
| **gVisor** | `NOT-FOUND` — no lane opened the LICENSE | It is the parser sandbox. Widely reported as Apache-2.0; this document will not assert it |
| **`Hypothesis`** | `NOT-FOUND` | It drives L6. Reported as MPL-2.0, which would be acceptable unmodified; a copyleft surprise would mean hand-rolling ~150 lines |
| **Z3** | `SECONDARY` (MIT) | Gate 2's proof arm. The empirical arm survives without it |
| **`cobalt` / `indigo`** | GitHub reports `NOASSERTION`; not opened | If restrictive, implement the FRBR URI grammar ourselves. **`bluebell` is GPL-3.0 — confirmed — and must not be linked** |
| **`xbrl.us/dqc-license`** | `NOT-FOUND` | If permissive, the DQC rule corpus is the **only ready-made financial-filing evaluation set found anywhere** for L3 |
| **in-toto / Sigstore** | `UNVERIFIED` — not re-checked live | DSSE is a 40-line spec; the format is the asset, not the tool |
| **`pandera` release date** | `UNVERIFIED` — the version is right, the date the PyPI fetch returned is inconsistent with it | Cosmetic |
| **IFSCA's terms of use for the register API** | **Not read.** 2,235 polite GETs were made once, at 0.06–0.25 s spacing | **Must be read before any scheduled or productionised polling.** This is a gap in conduct, not in code |

### 8.2 Measurements that must run before a number is quoted

| # | Question | Why it blocks something | Cost |
|---|---|---|---|
| 1 | **Does LibreOffice reproduce Excel's values exactly on this workbook**, including `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101`? | If the two engines disagree, the **observability filter is measuring the wrong thing** and every kill rate is suspect. **Positive control required before any kill rate is quoted** | hours |
| 2 | **Does the unobservable rate on our fault taxonomy resemble the published 46.8%?** | It is a property of *our* operator mix. **Measure it; do not assume it** | hours |
| 3 | **Does `celpy` pass the CEL conformance suite, on error semantics specifically?** | Our `&&`/`||` absorption guard depends on it, and the two candidate runtimes may differ | hours |
| 4 | **What is the key-binding accuracy `μ` on cross-document binding?** | It is the pre-registered gate that decides whether the conformal layer is built at all. At the architecture's own stated key accuracy, forced abstention is **100% at every risk level** — conformal would price a broken extractor honestly and look broken doing it | one afternoon |
| 5 | **The 15-vs-22 vocabulary→validation mapping** | Two lanes imply different counts of unwired vocabularies. **Neither figure may be quoted until the build computes the mapping and asserts it** | minutes |
| 6 | **Does an Excel round-trip by a filer rewrite the 211 shared-formula followers as text-bearing formulas?** | If it does, a filed workbook and the blank differ structurally in a way a template-integrity relation would flag as a parser bug when it is normal. **Must be tested on a filing that has been through Excel** | hours |
| 7 | **What is the field-surface denominator for an *unprotected* template?** | Two of nine prescribed workbooks have no protection mask. Current answer: `coverage: null`. That is honest but it is also a hole in the cross-template story | days |
| 8 | **Is the `D17` COUNTIF defect present in the other prescribed workbooks?** | Same method, ~20 minutes, and it turns one finding into a pattern | 20 minutes |
| 9 | **The transfer measurement:** what fraction of the FME predicate set transfers to a second prescribed format, and at what human cost per predicate? | **This is the experiment that decides whether this is a product or a paper.** Nine workbooks are on disk | days |
| 10 | **Does IFSCA already run these checks on receipt, and how often is an FME filing returned for correction?** | One email. **If the answer is "yes, we run them", the entity-facing product is a convenience and the research result is the entire value.** Better to know that in August than in October | one email |

### 8.3 Things this section deliberately does not specify

- **Who signs the attestation.** If the vendor signs, the vendor is attesting to a regulated filing. If the filer
  signs, it is self-attestation. If an FME shows an inspector a signed attestation over a filing that was wrong,
  the signature is the first exhibit. The scope-only schema with no `result` field is a **partial** answer; the
  signer question needs an explicit decision before L7 ships, and it is a legal decision, not an engineering one.
- **Authentication, multi-tenancy and user accounts.** Not before 30 October. Judges will not sign up, and every
  one of them adds a failure mode to a system whose demo must run offline from a file.
- **The clean-corpus construction protocol beyond the blind-fill firewall.** The firewall is the minimum bar; the
  sampling design that makes the corpus *representative* (marginals matching IFSCA's published per-category
  aggregates) is specified in outline only, and it does not fix circularity — it only makes the corpus less
  obviously synthetic.
- **Any open-weight model recommendation.** `NOT-VERIFIED`, and the architecture converts it into a measurement
  (admitted predicates per unit cost) rather than a guess. **A guessed URL is the fabrication this programme
  forbids.**

---

## §9 — THE ONE-PARAGRAPH SUMMARY, FOR SOMEONE WHO WILL BUILD IT TOMORROW

Read the workbook with namespace-aware `lxml` and never with `openpyxl` for structure; induce the field graph,
the 54 validations, the 20 resolvable vocabularies and the 3,747-cell unlocked field surface from the blank
template in 28 milliseconds; harvest 280 executable predicates from what the template already encodes, with no
model; express every predicate as one line of a restricted CEL subset inside a three-slot envelope, so that the
set of fields it reads is statically extractable and the coverage fraction is therefore derived rather than
estimated; scale money to integer micro-units because CEL has no decimals; evaluate it against a two-document
fact model in which vocabularies always resolve against the pinned blank and never against the submission,
because the vocabulary sheet is the one sheet a filer can edit; pre-flight every declared key before evaluation,
because CEL's `||` silently swallows errors; treat every doubt as a counted, reasoned non-settlement rather than
a failure; prove on every single filing, with seeded canaries, that the checker was alive on *that* document;
compute the denominator twice with two readers and abort if they disagree; enforce closure so that every pair
lands in exactly one of eight states; sign the coverage over the filing hash, the template hash, the registry
root and every predicate's measured rates; and admit no check whose kill rate, degeneracy verdict and
false-failure rate — with its corpus provenance and its Wilson interval — are not already in the registry.
**The model appears exactly twice, both offline: proposing candidates that a deterministic gate then rejects,
and reading attachments that a deterministic schema then constrains. It never touches the verdict. The registry
is the asset. The residue is the result.**
