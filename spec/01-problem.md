## I.0 — How to read a number in this part

Every quantity below carries a warrant label and a denominator. This is not editorial preference. It
is the product thesis applied to its own specification, and this corpus has been burned five times by
ignoring it (§I.2.4).

| Mark | Means |
|---|---|
| **MEASURED** | Computed first-hand against an artifact on disk — the workbook, the register, the circular corpus, the EBA spreadsheet — by a named lane, with the script identified. Reproducible. |
| **VERIFIED-AT-SOURCE** | The primary document was opened and the clause or number read off the page. |
| **SECONDARY** | A credible source describes it; the primary was not opened. |
| **DERIVED** | Arithmetic performed on stated inputs. Carries the warrant of its weakest input, never a stronger one. |
| **MODELED** | Produced by an assumption, not an observation. Labelled at the point of use. |
| **ABSTRACT-ONLY** | The paper's abstract was read; the full text was not. Positive claims quoted from the abstract survive; **absence claims about the paper do not.** |
| **UNVERIFIED / NOT-FOUND** | We looked and could not settle it. A legitimate answer and a required one. |

**Three standing rules, each of which earned its place by being violated inside this corpus:**

1. A derived number never claims a stronger warrant than its weakest input.
2. Before any absence is reported, a positive control is stated and the coverage denominator is
   declared. Two claims here collapsed because a search interface was mistaken for the corpus it
   searched; a third collapsed because a lane read `EncryptDId` where the populated field was
   `EncryptedId`.
3. Open the instrument and read the clause off the page. Nine withdrawn numbers moved because a pass
   inferred from a definition instead of reading the document.

**Terminology decision, taken once and propagated everywhere.** The quantity `settled / field surface`
is the **settled fraction**. The word **coverage** is reserved exclusively for the conformal guarantee.
*Alternative it beat:* keeping "coverage" for both, which is what the drafts did. *Reason it lost:*
the two senses appear within three pages of each other, and a reader who conflates a conformal coverage
level with a fraction of settled cells will read a statistical guarantee into a counting exercise. The
JSON key, the API path and every screen label change in one commit.

---

## I.1 — THE PROBLEM

### I.1.1 The statement

Every quarter, 217 fund managers licensed at GIFT City return a spreadsheet the regulator publishes.
The only thing in it resembling a verdict is a Yes/No box in which the manager attests that its own
valuations comply; nothing in the other 6,756 cells can contradict it. That is a green tick with no
denominator.

It is also the general case. An audit opinion, a filing sign-off and a sanctions disposition all end in
*nothing wrong here*, and none of them says what was looked at. The scarce quantity is not error
detection. **It is an attributable, per-check, measured statement of how often that check is wrong,
carried next to the finding it produced, together with a computed declaration of what was not touched.**
No product opened in this research prints either.

The brief's original headline — *"machines can already find the error; what no measured system can do
is say 'this one is clean'"* — is **refuted from inside the brief's own most-cited source** and must
never be said again (§I.2.5). What survives is narrower, is not refutable from that table, and is a
better problem:

> **A machine can be calibrated. Nothing in its output says whether it was.**
>
> Nine of fourteen complete frontier-model runs flagged ≥95.3% of 43 clean financial statements; one
> flagged none of them; **and nothing in any of the fourteen complete outputs distinguished the
> calibrated run from the uncalibrated ones.**

**Falsifiable in one move.** Produce a shipping product, or a published system, that prints a per-rule
false-failure rate measured on a declared clean corpus next to the finding that rule generated, and a
computed per-filing residue. §I.5.2 states the search that failed to find one, and attaches the list of
pages it opened rather than a count.

### I.1.2 The specific case — the FME quarterly return

The artifact is
`Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`, published on
`ifsca.gov.in/Download`, `sha256 = 7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39`.
It has 6,757 `<c>` elements across 10 sheets, 9 of them protected. Two defects in the **regulator's own
published blank**, both MEASURED first-hand and both reproducible by an audience in thirty seconds:

**(a) The return ships its own green tick.** `'8. Compliance Status'!C11` is a **Yes/No** cell reading
*"The FME is in compliance with Investment Valuation Norms as specified in Sixth Schedule of IFSCA
(Fund Management) Regulations, 2025."* Nothing in the other 6,756 cells can contradict it. The
supervisory record's only place for a valuation problem to surface is a self-attested checkbox.

**(b) The return computes a wrong number without noticing.** `'1. Introduction'!D17`, labelled *"Total
No. of Schemes of the FME authorised by IFSCA"*, is `=SUM(D18:D20)` where

```
D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")
D19 = COUNTIF(G54:G63,"*Restricted*")
D20 = COUNTIF(G54:G63,"*Retail*") + COUNTIF(G54:G63,"*Exchange Traded Fund*")
```

`G54:G63` is governed by an `x14:dataValidation` list over `Dropdown!$F$3:$F$11` — exactly **nine**
permitted values. **"Special Situation Fund" and "Family Investment Fund" match none of the five
COUNTIF patterns.** A filing declaring either reports a total silently short by one per such scheme,
and the value is legal under the template's own data validation. The defence *"D17 only ever meant the
total of those three sub-rows"* is answered by D17's own label, which is unrestricted — quote the label;
the argument turns on it. **Exposure is UNMEASURED**: how many of the 360 authorised schemes are of
those two types is not in any register dump held here. Do not claim an exposure figure. The defect is
real whether the exposure is 0 or 60.

D17 is also the proof of a limit we impose on ourselves: the criterion source is **available**, not
**authoritative**. A predicate mined from D17 inherits D17's defect and would pass a wrong filing while
failing a right one.

### I.1.3 Who has it, and what it costs them

**Decision: the buyer is the filer's compliance officer. The supervisor is not a user and not a buyer;
the supervisor is why the filer cares.** *Alternative it beat:* a two-user model with a supervisor
triaging filings. *Reason it lost:* supervisor-side SupTech for IFSCA is already **procured** — NEC
Corporation India, awarded 27 January 2026, ₹39,57,36,115.52, scope explicitly including an RE-facing
portal. Where a surface happens to be useful to a supervisor, it is described as serving *a downstream
reviewer*; the phrase "the two surfaces" does not appear in this specification.

| Population | Value | As at | Warrant |
|---|---|---|---|
| Fund Management Entities | **217** | Mar 2026, IFSCA Bulletin Q4 FY2025-26 (verbatim row `Fund Management Entity (FME) 202 217`) | VERIFIED-AT-SOURCE |
| Schemes | **360** | same bulletin | VERIFIED-AT-SOURCE |
| Fund Management rows in the public register | **650**, of which **229 resolve as live FME registrations** | 10 Aug 2026 | MEASURED (L08 §C.2) |
| Filings per year | **~868** | — | **MODELED**: 217 × 4, assuming every FME files every quarter including those registered mid-year |

**Never blend these in one sentence.** The bulletin is a stock at a quarter end; the register is live
and carries branch and multi-capacity registrations. Quote only what a single instrument returned:
*"650 Fund Management register rows as at 10 Aug 2026, of which 229 resolve as live FME
registrations."* **No scheme count is published from the register** until the entity/scheme split rule
is written down — the drafts carried a 390 that does not reconcile with 229 + 390 ≠ 650, and it is
deleted here.

**What it costs them is UNMEASURED, and saying so is load-bearing.** Nobody has measured how often
IFSCA returns an FME filing for correction, what an inspection observation costs an FME, or what the
Principal Officer's personal exposure is worth. The unit of value is **the avoided deficiency**, and
its price is unknown. **868 filings a year is ~3.4 per working day** — a volume one competent person
handles with a spreadsheet and a checklist. **The product is not selling labour savings and must not
pretend to.** One email to IFSCA's Division of Investment Funds, asking whether these checks are
already run on receipt, is therefore not an errand; it is the demand-side settling experiment, and it
is unsent.

### I.1.4 How it is handled today — five mechanisms, each with its exact stopping point

| # | Mechanism | Where it stops |
|---|---|---|
| 1 | **The template's own self-attestation** (`'8. Compliance Status'!C11`) | It is the filer's own Yes/No. Nothing else in the workbook can contradict it. |
| 2 | **The template's own arithmetic** (505 formula-bearing cells) | It computes a scheme total that misses two of its own nine legal scheme types (§I.1.2b). The instrument is part of the problem. |
| 3 | **Commercial validation catalogues** | The most complete public validation catalogue found anywhere in this research — Milestone Group's pControl NAV Oversight, ~25 named validation families, page returned verbatim twice — publishes **no false-positive rate, no detection rate, and no declaration of what the oversight cannot check.** Others advertise counts: *"40+ countries, 90+ regimes"*; *"850+ pre-coded global rules… 100+ jurisdictions"* (SECONDARY). |
| 4 | **The assurance profession's boundary declaration** | ISRS 4400 (Revised) ¶30(j) *requires* the statement *"Had we performed additional procedures, other matters might have come to our attention that would have been reported."* ISA 705 (Revised) ¶24 requires the auditor to state the reasons for an inability to obtain evidence. **But ¶20 begins "When the auditor modifies the opinion…" — an unmodified opinion carries no statement of what was not checked.** The clean audit report is the canonical silent all-clear. |
| 5 | **Threshold arithmetic, where a regime exists** | `daappa`'s NAV Error Materiality Calculator is free, no-signup, runs in the browser, and already encodes CSSF Circular 24/856 in full. VERIFIED-AT-SOURCE, confirmed live. **The scarce good is not the threshold arithmetic.** |

Mechanism 4 also **fails to fire when it should, at a measured rate**: 20% of *inspected* Big Four US
audits in 2024 carried a Part I.A deficiency (26% in 2023). The word **inspected** never comes off —
PCAOB selects engagements risk-targeted, not at random — and the warrant is qualified in §I.5.3.

### I.1.5 What specifically is absent — four properties, each independently falsifiable

The gap is not "nobody declares coverage." That sentence is false and a judge with an audit background
knows it. It is a conjunction of four properties.

| # | Property | Nearest existing thing, and exactly where it stops | Falsified by |
|---|---|---|---|
| **P1** | The check set is **derived from the artifact and the instrument**, not agreed with the party being checked | ISRS 4400 procedures are agreed with the engaging party and their appropriateness is **expressly disclaimed** (¶30(h)). XCCDF's denominator is a benchmark someone wrote; OSCAL's is a control catalog someone wrote | Any system that induces its check set from a regulator's own published artifact and says so |
| **P2** | Each check carries a **measured false-failure rate on a named clean corpus, with n**, rendered next to the finding it produced | SPADE computes FFR and consumes it internally; XBRL US DQC gates *for* false positives before publication but publishes no rate; the EBA publishes a binary post-hoc deactivation list; ESMA publishes authored severity (`ERROR/WARNING/OK`, Assertion Severity 2.0, REC 21 Jul 2022), which is **intent, not evidence**; LangSmith ships an *alignment score* — agreement with human labels, private, non-gating | Any product page showing a per-rule error rate with a denominator |
| **P3** | The **residue is computed and typed** — per field, per predicate, from a closed vocabulary, with *what would make it checkable* | ISA 705 ¶24 is prose, once per engagement, only on modification; ESMA's `Automatable` is a static property of the **rulebook**, not of a filing; CycloneDX `compositions.aggregate` is an inventory roll-up with no reasons; SPDX names three distinct causes of non-assertion and deliberately collapses them into one token | Any system computing, per filing, which correctness propositions were not settled and why |
| **P4** | Both are **bound cryptographically** to the template hash, filing hash, register snapshot hash and predicate-set version, so the boundary is third-party auditable and cannot be restated later | CycloneDX allows a signature over a composition; in-toto/DSSE signs build steps; **no financial analogue found across the opened set** | Any signed financial assertion carrying a settled-fraction denominator |

---

## I.2 — THE EVIDENCE BASE, CORRECTED

### I.2.1 The artifact — every load-bearing quantity that survives

Unless stated otherwise, all rows are for the FME workbook at the sha256 above. These are the constants
the build asserts in regression tests, so a parser regression is loud rather than silent.

| Claim | Number | Denominator | Source / instrument | Warrant |
|---|---|---|---|---|
| Cells | 6,757 | all `<c>` elements, 10 sheets | raw OOXML, lxml | MEASURED (L14 §1.8) |
| Formula-bearing cells | **505** | of 6,757 | four independent reproductions (L08, L09, L13, L14) | MEASURED |
| — carrying formula text | 294 | of 505 | same | MEASURED |
| — shared-formula dependents `<f t="shared" si="N"/>` | 211 (41.8%) | of 505 | same | MEASURED |
| Cross-sheet formula strings | 195 | of 294 (66.3%) | same | MEASURED |
| Checkable relations (SUM + COUNTIF) | **138** | of 505 = 27.3% | L08 §A.3, L09, L13 | MEASURED |
| Pure carries | 223 | of 505 = 44.2% | same | MEASURED |
| **Data validations** | **54** | 35 main namespace + 19 `x14` extension | namespace-aware lxml (L13 §1.4, L14 §1.5) | MEASURED |
| — list-type with a named vocabulary | 22 | of 54 | same | MEASURED |
| — resolving to a real enumerable vocabulary | 20 | of 54 | L14 §1.9 | MEASURED |
| Merged ranges | 252 | — | three readers agree (L05 §2) | MEASURED |
| Defined names | 12, of which **4 point at `#REF!`** in the published blank | of 12 | L13 §1.6 | MEASURED |
| **Field surface — the denominator** | **3,747** | unlocked **and** non-formula cells, from `styles.xml` `cellXfs → <protection locked="0"/>`; 105 unlocked style ids; 9 of 10 sheets protected | L14 §1.12 | MEASURED |
| Predicates harvested from the template with **no model** | **280** (FME) | — | L14 §1.9 | MEASURED (built; ~30 ms) |
| Cells settled by those 280 | **2,373** | of 3,747 = 63.3% | L14 §1.12 | MEASURED, **pre-gate — see §I.2.5** |
| Cells declared unchecked | **1,374** | of 3,747 = 36.7% | `3,747 − 2,373` | DERIVED from MEASURED |
| Composition of the 2,373 | **2,329 (98.1%) from 53 validation predicates; 271 cells (7.2% of the field surface) from 227 arithmetic predicates** | of 2,373 | L14 §1.12 | MEASURED |
| Predicates across all nine prescribed workbooks | **515** | nine workbooks | L14 §1.9 | MEASURED — **never quoted without its per-workbook distribution: two of the nine have zero formulas and one of those has zero validations, so 515 is concentrated** |
| Seeded-defect campaign throughput | 19,782 mutants in 2.5 s = 7,946/sec | 2,826 sites × 7 numeric operators | L14 | MEASURED |
| Embedded images | **0** | `xl/media/`, 9 of 9 workbooks | L08 §A.1 | MEASURED |

**The unit is the CELL. DECIDED (D-G1).** The closure invariant, the settled fraction and the
attestation's `scope` object are all defined over **cells**, and "obligation" is an attribute of a
predicate, not a second axis of a product. *Alternative it beat:* a `(field × obligation)` pair model.
*Reason it lost:* every measurement in this corpus is a cell count; the two drafts published
`pairsTotal` values of 1,187 and 4,021, neither of which is compatible with the other, with 3,747 × 41,
or with 63.3%, and the 1,187 was lifted verbatim from an **illustrative** JSON block that never claimed
to be a measurement. **`obligationsTotal` and `pairsTotal` have no derivation anywhere in this corpus
and must not appear in a schema example, a test or a screen until one exists.**

**The hero, fixed.** The headline is `<F> failures across <S> checks` and `<U> fields were not checked`,
in equal type, populated from the measured triple 2,373 / 1,374 / 3,747. It is **never** populated from
the enumeration argument of §I.2.5, which exists only to demonstrate that a fraction is manipulable.

### I.2.2 The register — the only non-synthetic clean corpus in the design

| Claim | Number | Denominator | Source | Warrant |
|---|---|---|---|---|
| Register entities enumerable in one request | 2,005 records, ~3.4 MB | `GET /DirectoryList/DirectoryGetList?PageSize=2100` | L08 §C.1 | MEASURED |
| Fund Management parent rows | 650 | of 2,005 | same | MEASURED |
| Live FME registrations | **229** (Registered Non-Retail 194 + Registered Retail 22 + Authorised 13) | of 650 | same | MEASURED |
| Registration numbers that resolve | **228 of 228** fetched (1 fetch error, coverage 99.6% of 229) | via `GET /DirectoryDetailGet?EncryptedId=…` | L08 §C.3 | MEASURED |
| Legacy scheme `IFSCA/FME/<I\|II\|III>/<FY>/<n>` | 141 (61.8%) | of 228 | L08 §C.3 | MEASURED |
| New scheme `FDM<YYYY><AAA><NNNN>` | 84 (36.8%) | of 228 | same | MEASURED |
| Matching neither | 3 (1.3%) — incl. one Roman `IV` where categories are I/II/III, one whose hyphen is `U+2011 NON-BREAKING HYPHEN` (verified at codepoint level), and one bare integer `100` | of 228 | same | MEASURED |
| **False-failure rate of the obvious regex** `^IFSCA/FME/(I\|II\|III)/\d{4}-\d{2}/\d+$` | **38.2% (87 of 228)** | 228 live FMEs, detail endpoint, 10 Aug 2026 | L08 §C.3 | MEASURED |

This is the single most valuable measurement in the corpus, because **the clean corpus here is the
regulator's own register** — no synthesis, no blind-fill firewall, no circularity caveat. A
deterministic predicate any competent engineer would write after looking at five examples is
catastrophically wrong on more than a third of currently-registered entities, and **nothing in its
output would say so.**

**Two corrections that must travel with it.**

- **The register does resolve registration numbers.** The claim that it does not is dead (§I.2.5). The
  canonical statement of the near-miss: *the register's **list** endpoint returns `RegistrationNumber
  = null` on 650 of 650 fund rows while its **detail** endpoint returns it on 228 of 228.* That is the
  illustration for the reason code `external_source_lacks_field` — **it is an illustration, not an
  instance**, because the source does carry the field.
- **"Clean by definition" licenses exactly one predicate.** Every entity in the register is validly
  registered, so a predicate asserting **membership** cannot have a true positive there. A predicate
  asserting **format** can, and 87 of 228 registration numbers fail the obvious regex. Do not let the
  first sentence launder an FFR for the second class.

**Fetch-plan statement (replaces two irreconcilable request counts in the drafts):** the plan is
`1 list request + N detail requests where N = |records|`, and the run that produces a snapshot hash
reports its own actual request count. IFSCA's terms of use for the register API **have not been read**;
they must be, before any scheduled or productionised polling. That is a gap in conduct, not in code.

### I.2.3 What the published literature actually supports

**Single-instrument concentration warning, and it governs the first four rows.** Rows tagged
**[FVB]** all derive from **FinVerBench, arXiv:2605.29586 — a 37-page single-author preprint (Silu
Panda), no institutional affiliation on the paper, not peer-reviewed, artifacts not released in v1,
clean split n = 43.** They do not corroborate one another; they co-vary perfectly. Never let two of
them read as two independent measurements.

| Claim | Number | Denominator | Source | Warrant |
|---|---|---|---|---|
| **[FVB]** Uncalibrated operating point is the modal one | 7 of 14 complete runs at exactly 100.0% FPR; 2 more at 95.3% (41/43) | 43 clean SEC 10-K-derived statements, n = 105 per row (43 clean + 62 injected) | arXiv:2605.29586 Table 6 | VERIFIED-AT-SOURCE (read by two independent passes) |
| **[FVB]** Calibration is achievable | Claude Sonnet 4: Acc 100.0 / Prec 100.0 / Rec 100.0 / F1 100.0 / **FPR 0.0**; on the rounded rendering, 0% FPR at 79.0% recall | same n = 105 | same | VERIFIED-AT-SOURCE |
| **[FVB]** …and the 0% is weaker than it looks, **twice over** | the paper's own 95% Wilson upper bound on 0/43 is **8.2%**; and the rule verifier's 15 relations are, in the paper's words, *"guaranteed consistent in our clean data by construction"* — the same construction applies to the clean split the 0% FPR is measured on | 43 clean | same | VERIFIED-AT-SOURCE. **Calibration is achievable, and it was measured on a clean set built to satisfy the checks. Say both in one sentence.** |
| **[FVB]** The paper disclaims prompt-invariance | verbatim: *"We therefore do not claim that the observed FPRs are prompt-invariant."* | — | same | VERIFIED-AT-SOURCE |
| Published state of the art in an adjacent task sits **below a one-line constant classifier**, and nobody computed the line | best F1 in an 80-cell binary-detection table = **65.4**; constant always-flag classifier on the ~49.5%-positive CUAD split = **66.2**; across the full ±0.05pp rounding box the floor exceeds the measured maximum by **0.62–0.99 F1 points**, strictly positive at every corner; **zero** occurrences of majority/constant/random/trivial/always-predict baseline in the 2,466-line camera-ready | 80-cell table, four non-frontier models | CLAUSE, arXiv:2511.00340 = `2026.findings-eacl.305`, **EACL 2026 Findings, peer-reviewed** | VERIFIED-AT-SOURCE + DERIVED (prevalence replicates across six internal checks) |
| Deterministic adjudication of model output for a regulatory submission, with fault injection | 10 replicates × 15 injected discrepancies = 150; reports **aggregate** recall and F1, with the hedge *"within the implemented rule classes"* | as stated | PROVE, arXiv:2607.28218 (30 Jul 2026) | **ABSTRACT-ONLY.** The quantitative facts are in the abstract and survive. **Every negative claim about PROVE — "no admission gate", "no relation layer", "no per-check rate" — is downgraded to "not visible in the abstract; the full text is unread" until someone opens it.** Opening it is cheap and must happen before the pitch: a coverage table in its implementation section would narrow our third novelty claim. |
| Wrapping a model in deterministic checkers, measured like-for-like | **82.09%** joint audit accuracy, 95% CI **[75.8, 90.2]**, **n = 67** (29 10-K + 38 10-Q across 47 tickers); **+14.93 points over the strongest baseline** (Single Agent 67.16). Ablating the deterministic checkers drops it to 17.91% **and raises invalid outputs from 1.49% to 35.82%**, so roughly half the collapse is unparseable output | n = 67 | AuditFlow, arXiv:2606.03031 | VERIFIED-AT-SOURCE. **The "+64 points" framing is dead: 82.09 − 17.91 = 64.18 is a self-ablation of a symbolic-first system, not a method comparison.** On n = 67, 14.93 points is 10 instances, and the paper significance-tests backbone differences only. |
| Reliability decays multiplicatively over steps | `pass^k` falls ~60% at k=1 to ~25% at k=8 | **τ-retail, n = 115 tasks**; τ-airline (n = 50) never reaches 60% even at k=1 | τ-bench, arXiv:2406.12045 | VERIFIED-AT-SOURCE. **The denominator travels or the figure does not.** |
| A per-step reliability of 0.9 over 8 steps | **0.9⁸ = 0.4305 → 43% reliable** | — | arithmetic | DERIVED |
| A model judge cannot backstop this | false-success detection at AUROC ≤ 0.65, 13% recall at a 10% flag rate | as published | L02 B.18 chain | VERIFIED-AT-SOURCE |
| Closest published work to synthesising executable rules from legal text | **Feeding an induced schema in as an explicit I/O constraint is the dominant lever on *structural similarity* (+37–54%)**; that study's ***outcome* equivalence tops out at 51–53%**, and the paper states that *"structural similarity does not guarantee outcome equivalence, and vice versa"* | 95 production decision models, Dutch Environment and Planning Act | arXiv:2604.17153 | VERIFIED-AT-SOURCE. **Environmental/planning law, not finance. No qualification gate. No false-failure rate.** |

### I.2.4 The evidence we produced ourselves — five silent false negatives

The strongest evidence in this corpus is not a paper. It is five instances of clean, confident,
well-formed, **wrong** output from **deterministic programs**, produced while preparing this
specification, with nothing in the output to distinguish it from a correct answer. All MEASURED.

| # | Instrument | What it reported | The truth | Mechanism |
|---|---|---|---|---|
| 1 | Operator's addressee parser | 64.5% of circulars name their addressee | **79.9%** | Over-narrow lexical rule |
| 2 | Operator's formula regex `<f[ >][^>]*>` | **zero** cross-sheet formulas in every workbook | **195 of 294** in the FME workbook alone | The regex cannot match `<f>SUM(...)</f>` — a formula element with no attributes |
| 3 | **openpyxl 3.1.5 — not our code, the ecosystem default** | **35** data validations; `7. AML-CFT` has **zero** | **54** validations (35 main + 19 `x14`); AML-CFT has **five** | Namespace blindness: `<dataValidation` cannot match `<x14:dataValidation`. openpyxl emits only `UserWarning: Data Validation extension is not supported and will be removed` |
| 4 | A register probe in this very research | *"The IFSCA public register does not resolve registration numbers"* | It does — **228 of 228** | The list payload carries **both** `EncryptDId` (null in 2,005/2,005) and `EncryptedId` (populated in 2,005/2,005). The probe read the first, got HTTP 302, and reported an absence |
| 5 | The qualification harness, v1 | Kill rate 100.0%, mutation score **100.1%** | 18.1% after two fixes | (a) equivalent mutants excluded from both numerator and denominator; (b) mutation sites sampled **only from cells the predicates already read** — the degenerate-baseline failure, committed by the harness built to detect it |

Instances 3, 4 and 5 are strictly better pitch material than 1 and 2: **3 is not our code**, **4 lands
on a live regulator's register**, and **5 is the failure occurring inside the machinery designed to
prevent it.** Instance 3 needs no defence and no explanation of anyone's code — a compliance tool built
on openpyxl would report full validation coverage of the anti-money-laundering section while checking
none of it. (openpyxl's round-trip also destroys the file: **3,663,391 → 65,877 bytes**, 24 parts
deleted including a 3.55 MB data model that is 96.9% of the workbook.)

**Three mechanisms, named:** lexical over-narrowing, namespace blindness, and a denominator drawn from
the numerator. "The system found nothing is not information" has moved from anecdote to a pattern with
a sample size and a taxonomy.

### I.2.5 Brief-era claims that are now dead, and why

Repeating any of these is a build error, not a style problem.

| Dead claim | Why it died | What replaces it |
|---|---|---|
| *"No measured system can say 'this one is clean'"* | Refuted inside the brief's own most-cited source: one run scored 0.0% FPR at 100% recall on the same instances under the same prompt | §I.1.1's calibration/attribution statement |
| *"Zero financial regulations encoded anywhere"* | EBA, EIOPA, ESMA, XBRL US DQC and FINOS CDM all publish executable rules | Like-for-like distinct total **14,819** (EBA 8,052 distinct + EIOPA 6,767), **never** the mixed-unit sum. What is empty is the *civic/academic* rules-as-code shelf: Catala's 12 domains and OpenFisca's 28 packages are entirely tax/benefit/pension, positive controls passed; FINOS's US LCR demonstrator has had no commit on `main` since 5 Jun 2024 at 16★ |
| *"No analogue exists for a financial assertion"* | ISA 705 ¶24 and ISRS 4400 ¶30(j) are financial and mandatory; ESMA publishes a per-rule `Automatable: Yes/No` (8 of 68 declared No, six of them `MUST`); XCCDF Table 26 (NIST, 2012) has nine per-item result states | §I.5's narrowed claim |
| *"The IFSCA register does not resolve registration numbers"* | 228 of 228 live FMEs resolve via the detail endpoint | §I.2.2, plus instance 4 above |
| *"35 data validations, only 3 list-type"* | Namespace-blind count | 54 validations (35 main + 19 `x14`), 22 list-type, 20 resolving |
| *"17 of 24 predicates are script-settleable"* as a bare phrase | Its stated justification depended on the refuted register finding | **the 24 candidate correctness predicates, of which 15 are exactly settleable, 2 are settleable only after a declared normalisation (NFKC, `U+2011 → U+002D`, strip, case-fold) that carries its own measured false-failure rate, and 7 are not settleable from the artifact at all** |
| *"AUDITFLOW +64 points"* as a method comparison | It is a self-ablation, and ~half the collapse is unparseable output | +14.93 points over the strongest baseline, 95% CI [75.8, 90.2], n = 67 |
| *"PASC names financial documents as a target"* | `financial` occurs once, in the Introduction, in a list of motivating domains; `finance`, `XBRL`, `invoice` = 0; every experiment is CoNLL-2003 / WNUT-17 / WikiNEuRal NER | Cite PASC for its joint-coverage method only, or not at all |
| *"A 90%-per-step agent is 57% reliable over 8 steps"* | 57% is the *failure* probability | **0.9⁸ = 0.4305 → 43%** |
| *"46% staffing"*, *"84 numeric / 15 date fields"*, *"the registry grows monotonically"*, *"two model calls, both short"*, *"95%+ of AML alerts are false positives"*, *"the sandbox is a nearly empty room"*, *"Reg 7(7) makes agentic AI illegal"* | No evidence table, no reproducible counting rule, or refuted at source | See §I.6 |

**And the one that matters most, because it is about us.** All three drafts led with *"63.3% of 3,747
fields settled by 280 predicates."* All three also state that a predicate whose `qualification` block
is absent does not load, and that an FFR whose corpus provenance is `SELF-AUTHORED` is not a number. No
blind-fill corpus exists. No false-failure rate has been measured for any of the 280. Therefore, under
this specification's own admission rule, **the currently admissible predicate set is empty and the
currently defensible settled fraction is 0%.** The corrected phrasing is mandatory, and it is stronger
than the number it replaces:

> **"280 predicates are mechanically derivable from the regulator's blank template with no model, and
> they touch 2,373 of 3,747 filer-editable cells. None of them is admitted yet, because no one has
> measured a false-failure rate for them on a corpus we did not write. That is the point: the number
> you are looking at is what every compliance product ships, and it is the number our own gate is
> designed to refuse. Watch what happens to it after qualification — that delta is the product."**

The composition makes the point sharper: **2,329 of the 2,373 settled cells (98.1%) come from 53
validation predicates, not from the 227 arithmetic ones**, and validation-carried cells are weaker per
cell. The non-degeneracy gate exists to reject exactly those.

**And the fraction is manipulable, which is why it is not the hero.** The hand classification of 24
candidate predicates yields 15 exact + 2 normalisation-dependent of 24 = 71%. A per-cell, per-
validation, per-vocabulary enumeration of the *same file* yields 505 + 54 + 15 = 574 predicates against
574 + 7 = 581 propositions = **98.8%**, obtained in one afternoon without writing a single interesting
check. That is an **enumeration argument, not a run** — nobody generated 574 predicates and measured
anything. **Label it DERIVED and never render it as a result.**

---

## I.3 — WHAT WE ARE ACTUALLY BUILDING

### I.3.1 For a non-specialist

Every quarter, each of the 217 fund managers licensed at GIFT City fills in a spreadsheet the regulator
publishes and sends it back. Somebody then has to decide whether it is right. Today the only thing in
that spreadsheet resembling an answer is a Yes/No box in which the manager attests that its own
valuations comply — and nothing in the other 6,756 cells can contradict it. We are building the
opposite of a Yes/No box: a checker that reads the regulator's own blank template, works out for itself
every relationship the template implies, tests each of those checks against deliberately corrupted
copies of a filing to prove the check can actually catch something, tests it against correctly-filled
copies to measure how often it cries wolf, and then runs **only** the checks that survived. What it
hands back is not a verdict of "clean." It is two numbers that cannot be traded against each other —
*this many checks ran, and these many properties of your filing could not be settled at all* — with
every unsettled property named, the reason given from a fixed list, and, where we know it, the exact
thing that would make it checkable. Every check that fires shows how often that same check has fired on
filings known to be correct. The whole report is signed against the hash of the template, the hash of
the filing and the version of the check set, so anyone can re-run it and get the identical answer, or
catch us if they cannot. **The product is not a better tick. It is the removal of the tick and the
printing of the boundary.**

### I.3.2 For an engineer

A content-addressed pipeline over a prescribed OOXML workbook.

- **L0 — ingest.** Fetch and hash four source classes (blank template, regulation and circular text,
  live register snapshot, the filing under test); parse the workbook twice with independent
  implementations and fail the run on disagreement. Never `openpyxl` for structure.
- **L1 — schema induction, no model.** Induce the field graph from the *blank* template's raw OOXML:
  505 formula-bearing cells (294 authored expressions + 211 shared dependents), 54 data validations of
  which 22 are list-type and 20 resolve to an enumerable vocabulary, 252 merged ranges, 12 defined
  names, protection state, hidden sheets, and the unlocked-cell mask that defines the **3,747-cell
  field surface**. Emits label-anchored stable keys and its own extraction manifest. **Money is an
  `int64` count of 10⁻³ USD Million — one unit = USD 1,000, `12.34 → 12340`, half-ulp 5 units,
  `τ(n) = 5n`.** DECIDED (D-G3); the phrase "micro-units" is deleted from this specification because
  it differs by 10³ and every tolerance is expressed in units.
- **L3 — candidate proposal, build time only.** The only model-bearing layer on the critical path, run
  per template version, **never per filing**. Proposes predicates as expressions inside a three-slot
  envelope (`applicable` / `expr` / `witness`).
- **L4 — qualification, the gate and the product.** Five gates: **G0** scope faithfulness · **G1**
  executes and binds (`cells_bound > 0`, every declared key exists in the induced schema) · **G2**
  seeded-defect kill with marginal kill over the free baselines · **G3** non-degeneracy · **G4**
  false-failure rate with corpus provenance and a Wilson interval. **A predicate with no qualification
  record does not load.**
- **L5 — execution and verdict, deterministic.** Eight closed item states — `PASS`, `FAIL`,
  `INDETERMINATE`, `NOT_RUN`, `NO_PREDICATE`, `ERROR`, `OUT_OF_SCOPE`, `INFORMATIONAL` — of which the
  first six are in the settled denominator; a closed, namespaced 30-code reason vocabulary across five
  state families; `cells_bound == 0` is `ERROR(cells_bound_zero)` and makes the run `INVALID`, never
  `PASS`.
- **L6 — differential and invariant probes**, including the check nothing else in the design can
  perform: a differential against the blank template's formula graph that detects a formula cell
  overwritten with a literal.
- **L6.5 — self-check and residue.** Replay every admitted predicate's stored kill-witness against
  *this* filing in the same execution; return `INVALID` if any predicate fails to fire on a fault it is
  known to detect; then compute the residue set.
- **L7 — attestation.** A DSSE/in-toto Statement whose top-level object is `scope` and which **has no
  `result` or `status` field at all**, binding template hash, filing hash, register snapshot hash,
  predicate-set Merkle root, fault-model version and every predicate's measured rates.

**Status, stated honestly, because two drafts overstated it.** *"Schema induction, predicate harvest,
arithmetic evaluation and the settled-fraction denominator are built and reproduce in ~30 ms. Template
binding, pre-flight, closure, canaries, attestation and `verify` are specified and not built."*
Likewise: **the verdict path is specified to make zero model calls, and the assertion is listed as a
build gate — the gate is not yet written.** Do not state either as a present-tense property of a
running system.

### I.3.3 The scope boundary — what this is NOT

| It is not | Why |
|---|---|
| **A NAV-error materiality regime, or a NAV recomputation engine** | The string `NAV` does not occur in any of the nine prescribed workbooks, in any XML part (MEASURED, with positive controls: `Scheme` 123, `USD Million` 31, `Portfolio` 25, `valuation` 6). No NAV per unit, no units outstanding, no dealing price, no dealing date. Every NAV-error rule on earth operates on exactly those quantities. See §I.4. |
| **A fraud detector** | This detects error, not deception. Every check is a consistency check over a self-reported document. **A coherent liar passes all of them**, and that sentence stays permanently on the report surface. |
| **An agent** | `pass^k` collapses ~60% → ~25% over 8 attempts on τ-retail (n = 115); `0.9⁸ = 0.4305`. No agent loop, no cross-step memory, no retry-until-it-passes. |
| **A model judge** | A model may never be the final adjudicator: false-success detection at AUROC ≤ 0.65, 13% recall at a 10% flag rate. |
| **A repair tool** | L5 adjudicates and reports. It never repairs. Deterministic ledger feedback has been measured to push models to *reconcile* contradictory documents rather than report them, costing 13–52pp on inconsistency detection. |
| **A supervisory system** | That seat is procured (NEC, 27 Jan 2026, ₹39.57 crore, RE-facing portal in scope). We are in the filer's seat and say so early. |
| **A replacement for check libraries** | Great Expectations, pandera, Soda Core, dbt and Deequ are the substrate. **None of them has a third verdict value** — Great Expectations actively converts *could-not-check* into *failed*. The check library need not be rebuilt; **the verdict model must be, because it does not exist anywhere in the ecosystem.** |

---

## I.4 — THE DOMAIN GROUNDING, AND THE SPLIT THAT MUST NOT BE RE-OPENED

**The split, stated first so nobody re-opens it.** The **domain fact** stays. The **product framing**
does not. The NAV-error wedge — building the Indian analogue of CSSF Circular 24/856 — was deleted for
five independent measured reasons, and it is not restorable.

### I.4.1 What the rest of the world specifies

| Jurisdiction | What is specified | Warrant | Where it stops |
|---|---|---|---|
| **Luxembourg** | **Circular CSSF 24/856**, 28 Mar 2024, in force 1 Jan 2025, repealing 02/77, 47 pp. Tolerances (point 35): MMFs under MMFR **0.20%**; UCITS and comparable Part II/ELTIFs bond **0.50%**, mixed **0.50%**, equity **1.00%**, other eligible assets **1.00%**. Self-set regime capped at **5%** with *"In no case are UCIs permitted to use by default the 5%-threshold"*. Six deterministic disambiguation rules (point 37), whose classifier input is *"the constitutive documents and/or the prospectus"* — a named document, not a judgement. Aggregation of successive sub-threshold errors (point 38). Compensation direction tables 4/5. Auditor trigger at **EUR 50,000** total or **EUR 5,000** per investor (point 138). Notification **4–8 weeks after detection**, and *"the corrective actions… are not subject to the CSSF's approval"* | VERIFIED-AT-SOURCE, independently re-derived | It is a **declaration** regime, not an approval regime |
| **Luxembourg, published base rate** | **234** declared NAV calculation errors in 2024 over **13,599** fund units at 31 Dec 2024 = **1.72%**; 234/3,143 registered UCIs = 7.44%; total compensation EUR **20,382,185.07** = 0.00035% of EUR 5,820bn net assets. Series: 462 (2022) / 344 (2023) / 234 (2024) | VERIFIED-AT-SOURCE + DERIVED | Flow-over-stock; 2024 declarations were made under the **old** circular. **A permanent guardrail: this may never be imported as an FFR prior for any predicate here. It is a comparator for the pitch and an input to nothing.** |
| **Ireland** | CP130 (2019) proposed MMFs 0.10% / other 0.50%. **Seven years later it is still not law.** `S.I. No. 316 of 2026`, 5,060 extracted lines, greps as `materiality` **0**, `toleran*` **0**, `redress` **0**, `de minimis` **0**. Positive controls: `net asset value` **37**, `valuation` 48, `shall` 485 | MEASURED, reproduced independently | **Ireland does impose an immediate error-notification duty in these Regulations — for client recordkeeping, not for NAV. The absence is a choice, not an oversight.** *Coverage note:* the AIF Rulebook, the UCITS Q&A and Irish Funds guidance were **not opened** |
| **UK** | **COLL 6.3.6G** §4(3): depositary reports immediately at **0.5% or more of the price of a unit**; §5(2) minimal significance below 0.5%; §5(3) *"each price should be considered separately"* | VERIFIED-AT-SOURCE (live FCA Handbook) | **Fund-type-blind.** No numeric de minimis |
| **US** | **17 CFR 270.2a-4(b)** is a **penny-per-share rule about accruals**, not a general NAV-error rule; **270.2a-7(g)(1)(i)(B)** is a stable-NAV MMF shadow-price rule at ½ of 1% | VERIFIED-AT-SOURCE (Cornell LII mirror) | The widely-quoted "<1¢ immaterial / ≥½ of 1% reprocess" thresholds trace to a **practitioner slide that cites no authority**. **The US does not in fact have what Luxembourg has** |
| **IOSCO** | Principle 5: pricing errors causing material harm addressed promptly, investors fully compensated | SECONDARY, at one remove — iosco.org returns HTTP 403 to every fetch. **Do not cite an IOSCO document number** | Sets no threshold |
| **ESMA** | 2022 Common Supervisory Action on Asset Valuation: `materiality` **0**, `toleran*` **0**, `pricing error` **0**; reports a two-stage control (administrator first, escalation to manager) and that *"the related remedial procedures are not always sufficiently formalised"* | VERIFIED-AT-SOURCE | Sets no threshold, and **publishes no absolute sample size**, so its own "0–10% of the funds in the CSA sample" has no computable numerator |
| **SEBI (India onshore)** | Master Circular for Mutual Funds as at 20 Mar 2026, 748 pp, 35,350 lines: `NAV error`, `incorrect NAV`, `erroneous NAV`, `valuation error`, `de minimis` = **0 each**. Positive controls `NAV` **371**, `shall` **2,687**. Over 1.29M characters there are **34 windows of ±180 chars containing any of `error\|erroneous\|incorrect\|wrong\|mis-stat\|mis-calcul`; exactly one also mentions NAV — and it is "Tracking Error"** | MEASURED | But Annexure **2.9.3.1(vii)** requires fund accounting systems to facilitate *"Flagging of price variances beyond pre-established tolerance levels"*, and 2.9.3.1(v)(e) requires the AMC to communicate its **error tolerance** to service providers. **SEBI mandates that a tolerance exist, be pre-established, be system-enforced and be communicated. SEBI does not say what it is.** That is the closest regulatory analogue anywhere to what this system proposes: *declare your parameter.* |

**And the finding that outranks every threshold.** COLL 6.3.6G §5(3) says *"each price should be
considered separately."* CSSF 24/856 point 38 says successive sub-threshold errors that aggregate
**are** significant. **Two mature regulators, the same phenomenon, opposite rules, both read off the
page.** Materiality of a NAV error is not a fact about the world; **it is a jurisdictional parameter.**
That is the hard evidence that a checking relation is not a law of nature — it is a rule with an owner —
and it is why **every predicate must carry the instrument that authorises it, and the report must state
which one it applied.**

### I.4.2 What IFSCA specifies, and what it does not

**IFSCA (Fund Management) Regulations 2025, amended to 30 Jan 2026 — 102 pp, 3,963 lines:** `NAV error`
**0** · `valuation error` **0** · `incorrect NAV` **0** · `toleran*` **0** · `swing pricing` **0** ·
`de minimis` **0** · `restat*` **0** · `materiality` **1** (an unrelated disqualification provision) ·
`compensat*` **1** · `error` **5** (3 × "tracking error", 2 × "Financing of Terrorism"). Positive
controls: `shall` **728** · `valuer` **32** · `true and fair` **6** · `Sixth Schedule` **5**. The IFSCA
Fund Management FAQ of 3 Aug 2026, 68 pp, contains the bare substring `error` **zero** times, against
positive controls `NAV` 13 · `shall` 183 · `scheme` 405. All MEASURED, every count reproduced by an
independent pass.

What IFSCA does specify, quoted exactly: **Third Schedule Part A(f)** (the FME shall compute and carry
out valuation per the Sixth Schedule and publish it); **Third Schedule Part A(g)** (*"The FME and its
controlling shareholders shall be liable to compensate the affected investors and/or the scheme for any
unfair treatment to any investor as a result of inappropriate valuation."*); **Sixth Schedule, fair
valuation clause (g)** (responsibility for true and fair valuation and correct NAV is the FME's);
independent valuation under regs 26(2)/38(2)/50(2) with a **fund-of-funds proviso**; NAV frequency under
regs **27(1)** (VC, annual), **39(1)** (restricted, monthly, half-yearly proviso for close-ended),
**51(1)** (retail, daily/weekly *"in such manner as specified by the Authority"*), **69(1)** (ETFs,
daily). And the modal verb that matters: regs 27(2), 39(2), 51(2) **and 69(2)** — *four, not three* —
each say the NAV procedure *"**should** be fully documented"*, in an instrument that uses **shall** 728
times. **A soft obligation sitting exactly where Luxembourg puts its hardest one.**

> **IFSCA specifies, with the force of "shall": who must value, how often the NAV must be computed per
> scheme class, that the FME owns the truth of the NAV, and that the FME and its controlling
> shareholders are liable to compensate for inappropriate valuation.**
>
> **IFSCA does not specify: what makes a NAV wrong, how wrong is wrong enough to matter, who must be
> told, when, in what form, how compensation is computed, in which direction it flows, whether there is
> a floor below which it is not paid, who bears the cost of correction, or whether an auditor is drawn
> in.**
>
> **Third Schedule Part A(g) is a liability rule with no trigger. CSSF 24/856 is 47 pages of exactly
> the trigger.**

### I.4.3 Why the wedge is prescribed-return verification and not a NAV regime

**Decision: DECIDED and closed.** *Alternative it beat:* building the Indian analogue of CSSF 24/856.
*Five independent measured reasons:*

1. **The artifact cannot support it.** Across all nine prescribed workbooks, in every XML part: `NAV`
   **0**, `per unit` / `unit price` / `units outstanding` **0**. *Correction that must travel with
   this:* the return **does** carry fund-level flows — `'2. Summary'` row 4 carries cumulative
   commitments, cumulative and in-quarter funds raised, cumulative and in-quarter redemptions,
   distributions, net inflow/outflow and investor counts. The precise claim is therefore: **the return
   carries fund-level net assets and gross subscription/redemption flows, but no per-unit price, no
   units outstanding and no dealing date, so no NAV-error rule on earth can be evaluated against it.**
2. **Ireland removes the moral force.** The set of jurisdictions with a prescribed NAV-error regime is
   roughly {Luxembourg, UK}, and they disagree with each other about aggregation. "IFSCA lacks this" is
   the majority position, not a scandal.
3. **A regime is a policy proposal, and you cannot ship a policy.** Only IFSCA can set a threshold, and
   the judging criteria include solution feasibility.
4. **Where the regime exists the tooling is commoditised** (daappa, free, in-browser).
5. **The prescribed-return route has first-hand reproducible defects to demonstrate; the NAV route has
   none.**

**What survives, and it is not nothing.** CSSF 24/856 becomes **the prior art for coverage
declaration**: *one regulator in the world publishes, in advance, exactly what it will and will not
treat as a finding, and then publishes the resulting rate annually. We compute the equivalent per
filing, for a jurisdiction that has neither.* **Third Schedule Part A(g) becomes the canonical unchecked
entry**, and its *what-would-make-it-checkable* text is now writable with numbers that are all
VERIFIED-AT-SOURCE: *"a materiality threshold by scheme class of the kind CSSF Circular 24/856 Tables
1–3 specify (0.20% MMF / 0.50% bond and mixed / 1.00% equity and other), plus a compensation-direction
rule of the kind its Tables 4–5 specify."* Two valuation-axis predicates survive (staleness against the
frequency owed under regs 27(1)/39(1)/51(1)/69(1); independent-valuer presence with the fund-of-funds
proviso emitting a typed non-settlement), and flow-identity predicates over `'2. Summary'` S4/T4/U4/V4
are computable and currently unclaimed.

**OPEN — USER DECISION (D §4.2 q3).** One question from the NAV work is still ranked joint-first in one
draft and absent from another, and only the user can close it: *is the fund-administrator call still
live?* The exact question, to KFin Technologies, CAMS or Basiz Fund Services, is: **"When you strike a
NAV for an IFSC scheme and it differs from what you expected — from your own recomputation, from the
prior valuation point, or from the manager's shadow — what is the number that makes you stop and
escalate rather than release? Is that number written down, and who set it: you, the FME, or the
administration agreement?"** If the answer is yes, the boundary already exists and is merely private,
which is a **better** problem statement, not a worse one — *"the threshold is private, uncomparable
across administrators, and invisible to the supervisor"* — but it changes the pitch.
**Default if the user does not rule:** the call is retired as a *killer* alongside the NAV wedge and
kept only as a market-structure enquiry, and the "two calls, both ranked joint-first" phrasing is struck
from every document. It must not remain ranked joint-first in one place and absent from another.

---

## I.5 — WHAT IS GENUINELY NOVEL

### I.5.1 Three claims that were narrowed past accuracy, restored

Three genuinely novel things were sanded down in the name of defensibility. Each is restored here in a
form that is both **bolder and more true** than the hedged version.

**I1 — The undetectable-in-principle mutant class.** The residue was being presented as "which
falsehoods survive every check we have" — a statement about our check set, and therefore a statement
about our incompleteness. The stronger claim is a theorem about the artifact class:

> **A prescribed return is a closed arithmetic system. We can construct, and exhibit, a family of
> filings that are internally perfect under every relation the regulator's own template encodes and
> every relation we have added — and materially false. That family is non-empty by construction, its
> size is measurable, and measuring it is the first quantitative statement anyone has made about the
> limit of document-level verification for a regulated filing.**

In code mutation testing, a mutant that changes behaviour is in principle killable by *some* test.
Here, a mutant can change the *truth* of the artifact and be **provably unkillable by any predicate over
the artifact alone.** That is not a coverage gap. The consequence for the risk register: "the residue
set is empty" is correctly graded **Low → structurally impossible**.

**I2 — `INVALID` as a liveness proof, not a self-check.** The hedged version buried the claim under
"the nearest named prior art is SRE synthetic monitoring and hardware built-in self-test" (true, and it
stays) plus the correct caution that *a formal-methods citation for vacuity detection is UNVERIFIED and
must not be asserted* (also true, and it stays). The actual claim is not "we self-test" — everything
self-tests. It is that **the verdict is conditioned on a proof obtained from the artifact under test, in
the same execution, and is withheld when that proof fails.**

> **No assurance artifact in existence carries evidence that the instrument that produced it was working
> on the specific document it examined. A clean audit opinion does not. An SBOM does not. A validation
> report does not. Ours refuses to issue a verdict unless every check has just demonstrated, on your
> file, that it can still catch the fault it was admitted for.**

That sentence is falsifiable, is not a novelty claim about a mechanism (two extra executions per
predicate), and needs no citation. Given that the strongest evidence in this whole corpus is five
deterministic programs producing confident wrong answers (§I.2.4), **this state is not optional.**

**I3 — The criterion-source substitution, honestly downgraded but not deleted.** The brief claimed the
criterion source was *authoritative*; that was correctly downgraded to *available* (D17 proves it). But
the downgrade swallowed the actual novelty, which survives intact:

> **SPADE infers what correctness meant from the traces of a developer changing their mind. We do not
> have to infer it: the criterion is a published instrument with a version, an amendment chain that is
> machine-followable in 76 of 82 cases, and a blank template with a content hash. The criterion source
> is not more *authoritative* than SPADE's — the regulator's own template computes a scheme total that
> misses two of its own nine legal values — it is *citable, versionable and watchable*, which is what
> lets a predicate be tied to a clause, re-qualified when the clause moves, and quarantined the day a
> circular changes the rule.**

(76 of 82 amending circulars cite a resolvable target = 92.7%; 866 dated cross-references across 58.6%
of circulars. MEASURED.) That is what the instrument-stream watcher implements, and no draft stated it
as a novelty.

**And the brief's sharpest sentence, in its only defensible form.** *"The verification problem and the
capability problem are the same problem"* is not restorable as written — the seeded-defect labels are
precisely the counter-example. Its corrected form is worth exactly one line: **where a programmatic
oracle exists we do not need a model; where it does not, we manufacture labels by seeding faults rather
than by asking one.**

### I.5.2 The single defensible novelty sentence

Everything else in this part is support for one sentence. It is stated at the strength it can survive an
adversarial reading and no stronger:

> **No product or published system, for any regulated financial filing, (a) admits a check into its
> active set only after measuring that check's own false-failure rate on a declared clean corpus and its
> kill rate against seeded defects, and (b) returns, alongside the verdict and signed with it, a
> computed per-field machine-readable declaration of which correctness propositions were not settled and
> why.**

The one-line version, for a slide: **everyone ships rules; nobody ships each rule's error rate, and
nobody ships the residue. We make both a product surface, and sign them.**

**The scope of the search that found the absence must travel with the claim.** It comprised: **every
vendor and product page opened in this research** (Suade, Regnology, Confluence; Milestone Group,
Clearwater; MindBridge, DataSnipper, Fieldguide, Numeric; LangSmith, Braintrust, promptfoo, DeepEval,
Guardrails; Great Expectations, Deequ, dbt-coverage, Monte Carlo, Anomalo; Lawrbit, Gieom) — **the list
is the denominator, not a count**; seven arXiv metadata queries with a 186-result positive control; the
LangChain documentation index (99,944 bytes, 960 lines, 57 evaluation-related lines, `grep -ci spade` =
0, `grep -ci "false failure"` = 0); the CycloneDX 1.2–1.7 JSON schemas parsed programmatically; XCCDF
Table 26; OSCAL v1.2.3; ISRS 4400 (Revised) and ISA 705 (Revised) read in full; the EBA 4.3 and legacy
rule files, the EIOPA Solvency II 2.10.0 file with its Known Issues register, and the ESEF 2024/2025
summary-of-tests, downloaded and counted.

**BLOCKING — DECIDED (D-C14/F6).** Two different opened-vendor counts were published in the drafts
(16 and 21), and the lane that produced the claim flagged its own denominator as unreconciled. **Neither
number is quotable.** Until a written inclusion rule exists (does an open-source project count? does a
docs page count separately from a product page? do two pages of one vendor count once or twice?) and the
count is recomputed under it, **the absence claim ships with the list above and no integer.** A larger
denominator strengthens an absence claim, so this costs nothing but the appearance of precision — and in
a document whose entire method is denominator discipline, an unreconciled denominator inside the central
novelty claim is the first thing an adversary pulls.

**The largest single weakness in the novelty claim, stated by us before anyone else states it:** 20+
further named vendors were never opened — AxiomSL/Nasdaq (timed out), Wolters Kluwer OneSumX and
Corlytics (HTTP 403), Vermeg, Ascent, Clausematch, Hexanika, Gresham, SS&C, Northern Trust, BNY,
Trullion, Caseware IDEA, Klarity, AuditBoard, Basis, Bluecopa, Patronus, Arize Phoenix, Evidently,
Giskard, Ragas, Soda, Sifflet, Bigeye, and all Big Four in-house tools. **Any of them could publish a
per-rule measured error rate and we would not know.**

### I.5.3 The three strongest "this already exists" objections, and the exact rebuttals

**Objection 1 — *"This is SPADE. Berkeley published it in 2024, LangChain shipped it, 2,000+ pipelines.
You have re-skinned an existing product."*** The most dangerous objection, because the brief itself said
"reuse SPADE". Concede the reuse immediately, then be more precise about SPADE than the objector is.

1. **The criterion source is different, and a regulation cannot supply SPADE's.** SPADE mines
   *prompt-version deltas*: *"developers implicitly embed data quality requirements through changes to
   the prompt."* **A regulation has no prompt-diff history** — and does not need one (I3).
2. **SPADE's own paper says its central metric cannot be computed in general** — *"coverage and FFR are
   impossible to compute since the universe of examples 𝐸 is unknown"* — and its tasks average **34 bad
   examples**. **Seeded-defect adequacy is the answer to the sentence SPADE could not answer.** That is
   not a re-skin; it is the missing input.
3. **What shipped is not what the objection claims.** The public release with LangChain is *Component 1,
   candidate assertion generation*, delivered in November 2023 as an early prototype via a Streamlit
   application, and the "2,000+ pipelines" attaches to that generator. Today the LangChain documentation
   index carries 57 evaluation-related lines, `grep -ci spade` = 0, `grep -ci "false failure"` = 0, and
   `assertions.md` describes assertions **written by a human reviewer**. What LangSmith actually ships
   is an **alignment score** — agreement with human labels, computed privately, **non-gating**. The
   Streamlit prototype is no longer publicly reachable (it 303-redirects into a login loop that exhausts
   50 redirects). *Source:* `shreyashankar/spade-experiments` — 17★, 1 fork, **no licence field**, last
   push 2024-04-07. Reimplement the ILP (~40 lines of PuLP/CBC); cite the paper.
4. **SPADE has no residue.** It selects a set of assertions. **It never emits what it could not assert.**

**Do not use the "finance is one prompt in twenty-four" closer.** It is derivable from Figure 5 and it is
a misreading — the paper's body frames that chart as a breakdown of the 2,000+ deployment runs, not of a
24-item sample. A judge holding the PDF turns it into *"you misread a figure to make your competitor look
small"* and discounts everything else. **The defensible replacement, which is enough:** *SPADE's
evaluation set contains one finance pipeline — summarising earnings-call transcripts, with examples from
Kaggle — and no regulated filing anywhere in the paper.*

**Objection 2 — *"Auditors have declared what they couldn't check for decades. ISA 705. Qualified
opinions. You have rebuilt the audit report."*** Concede the concept loudly — it is our best legitimising
precedent — then show three places it fails.

1. **It fires only on modification.** ¶20 begins *"When the auditor **modifies** the opinion…"*; ¶24
   conditions on *"**If** the modification results from an inability to obtain sufficient appropriate
   audit evidence…"* **An unmodified opinion carries no statement of what was not checked. The clean
   audit report is the canonical silent all-clear** — the exact artifact this project exists to abolish.
2. **The mechanism demonstrably fails to fire when it should, at a measured rate.** **20% of *inspected*
   Big Four US audits in 2024 carried a Part I.A deficiency** (26% in 2023). In one inspected engagement
   in five, the evidence was insufficient and the opinion was issued anyway. *Warrant discipline:* 2024
   and 2023 are VERIFIED-AT-SOURCE at the PCAOB release; **the 2022 figure and the "lacked sufficient
   appropriate evidence" gloss are SECONDARY, and the re-verification pass could not reach pcaobus.org.
   Open the release and fix both before this is said out loud**, and never let *inspected* drop off,
   because PCAOB selects risk-targeted rather than at random. **A declaration that depends on a human
   noticing they should declare is not a coverage guarantee; it is a hope.** Ours is produced by a schema
   constraint: a predicate whose error rate is unknown **cannot be represented**, so it appears in the
   residue automatically rather than by anyone's virtue.
3. **It is prose, per engagement, with no rate and no arithmetic.** ¶20(b) asks for *"a description of
   the matter giving rise to the modification"* — a paragraph, in English, once per audit, naming no
   procedure, carrying no false-positive rate, yielding no fraction. **You cannot sort 868 filings by it.
   You cannot diff it between quarters. You cannot verify it cryptographically.**

**One-line form:** *ISA 705 declares the boundary when the auditor already knows they hit one. We declare
it every time, per field, as a number, whether or not anyone noticed.* **And the sharpest sentence
available comes from the standard that is otherwise our closest competitor:** ISRS 4400 ¶30(h) requires
the practitioner to state that they **make no representation regarding the appropriateness of the
agreed-upon procedures.** *The profession's most coverage-honest report form disclaims the one question
our qualification gate answers with a number.*

**Objection 3 — *"Reg-reporting vendors ship thousands of validation rules. The EBA publishes twelve
thousand. This is a mature, crowded category and you are late."*** Concede the crowding immediately — and
**delete the brief's false version of this claim first**, because *"zero financial regulations encoded
anywhere"* is checkable in ninety seconds by anyone in a GIFT City room who has worked in regulatory
reporting. Then attack the metric.

1. **The category competes on rule count and regime count, and those are the wrong axes.** Every vendor
   page opened states counts, never quality. The most complete public validation catalogue found anywhere
   — ~25 named validation families over exactly our artifact class — publishes **no false-positive rate,
   no detection rate, and no declaration of what the oversight cannot check.**
2. **The rule authors themselves publish that their rules are wrong.** The EBA deactivates validation
   rules quarterly *"either for incorrectness or for triggering IT problems"* and instructs authorities
   that submissions *"should not be formally validated against the set of deactivated rules."*
   **1,692 of the 20,562 validation rules in EBA release 3.5 have been deactivated at least once
   (8.23%); 1,008 are still off; 343 of those are at `error` severity; and it is still happening — 205 in
   2024, 94 in 2025, 27 by mid-2026.** Separately, **the EBA publishes 12,925 rule-instances resolving to
   8,052 distinct rules — do not divide one figure by the other.** MEASURED: L04 downloaded and counted
   the EBA's own spreadsheet, and the adversarial pass reproduced it. **If a rule count were a quality
   signal, the EBA would not need a kill-list.** This is simultaneously the strongest external evidence
   that the missing quantity is real and the cleanest statement of what it costs to find out from the
   field: **the gate is the proposition that you can find out before you ship.**
3. **On the actual target artifact, the incumbent rule inventory is not thousands.** 505 formula-bearing
   cells, of which 138 (27.3%) express a checkable relationship and 223 (44.2%) copy a value; the IBU
   Operations Report has **7 formulas across 961 cells**; **two of the nine prescribed workbooks contain
   zero formulas, and one of those has zero data validations as well** — a typed form with no internal
   consistency structure at all. **The settled fraction is a per-template property and must never be
   averaged across the corpus.**
4. **Count says nothing about the residue.** Of the 24 candidate correctness predicates on this return,
   **15 are exactly settleable, 2 are settleable only after a declared normalisation (NFKC, `U+2011 →
   U+002D`, strip, case-fold) that carries its own measured false-failure rate, and 7 are not settleable
   from the artifact at all** — and none of the settleable ones addresses any of the 7. **A vendor with
   10,000 rules and no residue declaration is asserting, by silence, that the 7 do not exist.**
5. **We are not competing with the category; we are supplying the column it does not have.** A predicate
   registry carrying kill rates and FFRs is something an incumbent would want to *consume*. And the seat
   matters: the supervisory seat at IFSCA is already procured. **We are in the filer's seat, and we say
   so early.**

**Three cheaper objections that must not be met unprepared.** *(a) "XBRL assertions have carried severity
since 2016."* True — Assertion Severity REC 19 Apr 2016, 2.0 REC 21 Jul 2022, three levels
`ERROR/WARNING/OK`. *Rebuttal:* **severity is declared by the rule's author before anyone runs it; a
false-failure rate is measured against a corpus after. One is intent, the other is evidence — and the
EBA's deactivation list is what happens when you only have the first.** *(b) "MindBridge already does
100% coverage: Full Population Analysis."* **Population coverage is not predicate coverage.** Scoring
every transaction answers *"which rows look unusual"*, not *"which correctness propositions about this
filing have been settled, and which cannot be"*; the product publishes no false-positive rate and no
declaration of analytical limitations. *(c) "PROVE already published your thesis."* **Cite it yourself,
first, on the slide that states the thesis.** *"LLM interprets, programs adjudicate, for a regulatory
submission"* is no longer novel as of 30 July 2026, and independent convergence in a different regulated
industry is **corroboration, not a threat**. What PROVE leaves is our claims — **but state that as "not
visible in the abstract; the full text is unread", because only the abstract was read (§I.2.3), and open
it before the pitch.**

### I.5.4 The honest ledger — what is assembly, and why the assembly is the contribution

**Show the list rather than hide it. A judge who finds one of these after the pitch discounts everything;
a judge handed all of them upfront reads the team as competent.** Borrowed, with named sources: the
generate-then-adjudicate thesis (PROVE; "Confidently Wrong", arXiv:2607.23386); assertion synthesis and
FFR-based selection (SPADE, arXiv:2401.03038 / PVLDB 17(12):4173–4186); non-LLM constraint suggestion
(Deequ, Apache-2.0, 3,638★) and dynamic invariant mining (Daikon); mutation adequacy at production scale
and its suppression discipline (Google, arXiv:2102.11378 / IEEE TSE 2021); the 17 spreadsheet mutation
operators including `FRC` "formula replacement with constant" (Abraham & Erwig, IEEE TSE 35(1):94–108,
2009); the hypergeometric random-flagger baseline and adjusted precision (ExceLint, OOPSLA 2018,
doi:10.1145/3276518) — **a published precedent for the degenerate-baseline test the brief presented as
new**; relations derived from statute (arXiv:2205.04998, ICSE-SEIS 2023); an observability interface
displaying per-constraint precision and recall (*Semantic Integrity Constraints*, arXiv:2503.00600 — our
predicate-library screen, in a database paper, a year early); nine per-item result states and the
denominator rules (XCCDF Table 26, NISTIR 7275r4, NIST 2012); a required completeness enum with an
explicit not-specified state (CycloneDX `compositions.aggregate` — six states in 1.3, ten in 1.5–1.7);
an explicit code when a check is deliberately not performed (C2PA 2.4 §15.9.2); the bounded-silence
sentence and the appropriateness disclaimer (ISRS 4400 ¶30(j), ¶30(h)); the boundary declaration
(ISA 705 ¶¶7(b), 9, 17, 24); documenting what contradicts your conclusion (PCAOB AS 1215 .08); a
false-positive-gated publicly-reviewed rule registry over regulated financial filings for a decade
(XBRL US DQC, 6,309 commits, Xule on Arelle — **note its licence is a bespoke AICPA/Calcbench/Toppan
Merrill/Workiva/XBRL US *document* licence, not OSI-approved; read it in full before it enters a
dependency list**); authored per-rule severity (XBRL Assertion Severity 2.0); a regulator declaring which
of its own rules are automatable (ESMA ESEF `Automatable Yes/No`, 8 of 68 No, six of them `MUST`); a rule
author publishing that its own rules are wrong (EBA); coverage-as-presence (dbt-coverage, MIT, 241★);
signed attestation and closed-world enforcement (in-toto / DSSE / SLSA VSA — **in-toto/attestation is
Apache-2.0, VERIFIED-AT-SOURCE, LICENSE read verbatim**); and model-free policy in a restricted
expression language in-process (Kubernetes ValidatingAdmissionPolicy, GA in v1.30).

**The test of whether an assembly is a contribution: can you remove one part and keep the claim?** Each
part alone is defeated by a measured fact, and each part's failure mode is another part's input.

- **SPADE alone fails** — its FFR needs labelled data its own paper says cannot exist in general.
  → **Seeded defects supply labelled dirty data by construction, at arbitrary n, with certain ground
  truth. The seeded fault *is* the label.** This is the load-bearing join and it is why this is not a
  mashup.
- **Seeded-defect adequacy alone fails** — it measures whether a check *can* fire and says nothing about
  the propositions with no oracle. → **Differential and invariant relations settle a subset of those
  without an oracle**, so the boundary becomes measured and movable — **while honestly moving ≈0 of the
  7 and saying so.**
- **Relations alone fail** — a relation can be trivially satisfiable or trivially violated, landing on
  the degenerate operating point where a flag-everything classifier beats the state of the art.
  → **The non-degeneracy gate rejects it**, which is why relations route *through* qualification and not
  around it.
- **All of them together still fail** unless the residue is emitted — a system that silently drops what
  it could not check has produced a false success by definition. → **The closed reason vocabulary and the
  computed residue make a false success structurally impossible to render, because there is no green tick
  to render.**
- **And the whole thing is worthless with an agent loop** — `pass^k` collapse and `0.9⁸ = 0.4305` — which
  is why the model runs at build time only and **the registry, not the model, is the durable asset.**

Remove seeded defects → the FFR is uncomputable and the gate is decorative. Remove the gate → the settled
fraction is an assertion and we are an incumbent with better copy. Remove the relations → the settled
fraction is a ceiling, not a growth curve, and the demo has no second act. Remove the reason vocabulary →
it is a linter. Remove the self-check → we are the thing we are selling against. **No part is removable.
That is what makes it a design rather than a stack.**

### I.5.5 What the gate has actually demonstrated, and what it has not

**One demonstrated rejection, stated at exactly its size.** *The gate has one demonstrated rejection:
five of the ALR workbook's six bound predicates assert only `≥ −1e17` over 1,428 cells and are refused.
Whether it rejects anything on the FME workbook is unmeasured — 19 of the FME's 24 bounds are a real
`≥ 0`.* Do not say "the gate demonstrably does real work" and stop there; one workbook, one predicate
class, five predicates is what exists.

**And the residue's reproducibility carries a condition.** The residue is *reproducible given the
published fault model **and the published adjudication record**, both content-addressed* — because the
INNOCUOUS/WRONG classification of a surviving mutant is the design's one human step. Saying "a third
party can re-run it and get the same answer" without that clause overstates it.

**OPEN — USER DECISION (D-G10).** Every false-failure rate in the product depends on a clean corpus
filled by someone who has **never seen the predicate set**, and the team is ≤4 people, all of whom have.
The exact question: **who is Person A, or do we commit to the audited second-model-instance route with
the fill prompt hashed and published before the first workbook is filled?** Until this is answered, every
FFR in the system renders as the word *uninformative* and no digits, and the corrected §I.2.5 phrasing is
the only defensible way to present the settled fraction.

---

## I.6 — THE BAN LIST

**Read this before a pitch.** Every string below is dead. Repeating one is a build error, not a style
problem — and most of them are dead because someone in this project checked and found the corpus wrong.

| Dead string | Why it died | Say instead |
|---|---|---|
| **"555 checks" / "562"** | Built on the namespace-blind validation count of 35; the design's own thesis is that a parser reporting 35 is the failure the product exists to prevent | The enumeration is 505 + 54 + 15 = **574**, and the Goodhart illustration is **574 / 581 = 98.8%**, labelled **DERIVED — an enumeration argument, not a run** |
| **"the 17 decidable predicates"** | Its justification rested on the refuted register finding | **the 24 candidate correctness predicates, of which 15 are exactly settleable, 2 are settleable only after a declared normalisation (NFKC, `U+2011 → U+002D`, strip, case-fold) that carries its own measured false-failure rate, and 7 are not settleable from the artifact at all** |
| **"sixteen commercial products opened"** (and "21") | The lane that produced the claim flagged its own denominator as unreconciled; no inclusion rule exists | *"every vendor page opened in this research"* + the list in §I.5.2, **and no integer** until the rule is written and the count recomputed |
| **"+37–54 percentage points of functional equivalence"** | Conflates two different metrics in the same paper | *"Feeding an induced schema in as an explicit I/O constraint is the dominant lever on **structural similarity** (+37–54%) in the only published study of statute→executable-model generation (arXiv:2604.17153); that study's **outcome** equivalence tops out at 51–53%."* |
| **"Hypothesis (MPL-2.0)"** as bare fact | No lane opened the LICENSE | "reported MPL-2.0, LICENSE not opened (SECONDARY)" |
| **"Z3 (MIT)"** as bare fact | Marked SECONDARY at source | "MIT (SECONDARY — open the LICENSE before shipping)" |
| **"in-toto / Sigstore — UNVERIFIED"** | The inverse error: the LICENSE **was** opened and quoted verbatim | **in-toto/attestation: Apache-2.0, VERIFIED-AT-SOURCE.** Delete it from any "licences not read" table |
| **"8.23% of 12,925"** | Arithmetically false — 8.23% of 12,925 is 1,064 | **1,692 of the 20,562 rules in EBA release 3.5 deactivated at least once (8.23%); 1,008 still off; 343 at `error` severity. Separately, 12,925 rule-instances resolving to 8,052 distinct rules — do not divide one by the other** |
| **"two model calls, both short"** | Wrong shape | **Zero model calls in the verdict path** — and state it as *specified with a build gate not yet written*, not as a present-tense property |
| **"zero financial regulations encoded anywhere"** | Refuted | **14,819 distinct** executable EU supervisory rules like-for-like; what is empty is the civic/academic rules-as-code shelf |
| **"no analogue exists for a financial assertion"** | Refuted | ISA 705 ¶24 and ISRS 4400 ¶30(j) both require a declared boundary; what does not exist is a per-item, machine-readable, schema-induced, per-check-error-rated version |
| **"the registry grows monotonically"** | Incompatible with re-qualification | **The settled fraction must be able to fall**, and the step-downs are the most credible thing on the chart |
| **"the register does not resolve registration numbers"** | Refuted the same day by a sibling lane | **228 of 228 live FMEs resolve via `DirectoryDetailGet?EncryptedId=…`.** The list endpoint returns null on 650 of 650 rows; the detail endpoint returns the number on 228 of 228 — an **illustration** of `external_source_lacks_field`, not an instance of it |
| **"46% staffing"** | Appears in no evidence table anywhere in the corpus | Delete. Do not replace |
| **"Fifth Schedule Part A(g)"** | No such provision is cited anywhere | **Third Schedule Part A(g)** (liability for inappropriate valuation); valuation norms are the **Sixth Schedule** |
| **"a 90%-per-step agent is 57% reliable"** | 57% is the failure probability | **0.9⁸ = 0.4305 → 43% reliable over 8 steps** |
| **"PASC names financial documents as a target"** | `financial` occurs once, in a list of motivating domains; zero financial experiments | Cite PASC for joint conformal coverage only, or not at all |
| **"no measured system can say 'this one is clean'"** | Refuted inside our own most-cited source | **"A machine can be calibrated. Nothing in its output says whether it was."** |
| **"35 data validations, only 3 list-type"** | Namespace-blind | **54 validations (35 main + 19 `x14`), 22 list-type, 20 resolving** |
| **"the workbook has 294 formulas"** (alone) | Two true quantities conflated | **294 distinct formula expressions across 505 formula-bearing cells** |
| **"AUDITFLOW +64 points"** | A self-ablation used as a method comparison | **+14.93 points over the strongest baseline, 95% CI [75.8, 90.2], n = 67**; the ablation also raises invalid outputs 1.49% → 35.82% |
| **"coverage" for the settled fraction** | Collides with conformal coverage three pages away | **settled fraction**; "coverage" only for the conformal guarantee |
| **"the two surfaces" / the supervisor as a user** | The supervisory seat is procured | **The supervisor is not a user and not a buyer; the supervisor is why the filer cares.** Say "a downstream reviewer" |
| **"L1→L5 runs end-to-end"** | Overstates what is built | **"Schema induction, predicate harvest, arithmetic evaluation and the settled-fraction denominator are built and reproduce in ~30 ms. Template binding, pre-flight, closure, canaries, attestation and `verify` are specified and not built."** |
| **"63.3% settled"** as a headline, unqualified | None of the 280 predicates is admissible under our own gate | The corrected paragraph in §I.2.5, verbatim |
| **"229 live FMEs and 390 schemes of 650 rows"** | 229 + 390 ≠ 650, and no split rule is written | **"650 Fund Management register rows as at 10 Aug 2026, of which 229 resolve as live FME registrations."** No scheme count from the register |
| **"~2,235 GETs for a full register refresh"** | Does not reconcile with 1 list + N detail | **"1 list request + N detail requests where N = |records|"**, plus the actual request count of the run that produced the snapshot hash |
| **PROVE "has no admission gate / no relation layer"** | Absence claims about a paper nobody opened | **"Not visible in the abstract; the full text is unread."** Open it before the pitch |
