# A — THE PROBLEM AND THE ARCHITECTURE
### The authoritative build specification. Section A of the specification: what the problem is, what we are building, how it is put together, what a predicate is, what the report is, and what is genuinely new.

**Compiled 10 August 2026.** This section supersedes `RND-BRIEF.md` Parts 2 and 5, and supersedes
`ARCHITECTURE.md` in its entirety, wherever they conflict. It incorporates the fifteen research
lanes (L01–L15) and their adversarial verification passes. Where a lane cites a primary source and
the adversarial pass did not refute it, the lane wins.

**Nothing in this document may be quoted without the warrant and the denominator attached to it in
the same sentence.** That is not editorial preference; it is the product thesis applied to its own
specification, and this corpus has already been burned five times by ignoring it.

---

## A.0 — WARRANT KEY, AND HOW TO READ A NUMBER IN THIS DOCUMENT

| Mark | Means |
|---|---|
| **MEASURED-HERE** | Computed first-hand against an artifact on disk (the workbook, the register, the circular corpus) by the operator or a named lane, with the script identified. Reproducible. |
| **VERIFIED-AT-SOURCE** | The primary document was opened and the clause/number read off the page. |
| **SECONDARY** | A credible source describes it; the primary was not opened. |
| **DERIVED** | Arithmetic performed on stated inputs. Carries the warrant of its weakest input. |
| **MODELED** | Produced by an assumption, not an observation. Always labelled at the point of use. |
| **ASSERTED** | Someone's claim, published, with no method or denominator we can inspect. |
| **UNMEASURED / NOT-FOUND** | We looked and could not settle it. A legitimate answer and a required one. |

**Three rules govern every number below, and each earned its place by being violated:**

1. A derived number never claims a stronger warrant than its weakest input.
2. Before any absence is reported, a positive control is stated and the coverage denominator is
   declared. Two claims in this corpus collapsed because a search interface was mistaken for the
   corpus it searched; a third collapsed because a lane read `EncryptDId` where the populated field
   was `EncryptedId`.
3. Open the instrument and read the clause off the page. Nine withdrawn numbers moved because a
   pass inferred from a definition instead of reading the document.

**The register of withdrawn claims is in §A.1.7.** Anything listed there is dead. It does not
reappear in a slide, a README, or the application form.

---

# PART 1 — THE PROBLEM

## 1.1 The statement, in the only form that survives its own evidence

The brief's headline was:

> *"Machines can already find the error. What no measured system can do is say 'this one is clean.'"*

**That absolute is refuted, from inside the brief's own most-cited source, and it must be deleted
before anything is submitted.** In FinVerBench (arXiv:2605.29586), on n = 105 instances (43 clean,
62 error-injected), **Claude Sonnet 4 scored Accuracy 100.0 / Precision 100.0 / Recall 100.0 /
F1 100.0 / FPR 0.0** — under the same guided-checklist prompt on which seven of fourteen other
complete runs flagged 43 of 43 clean statements. On the harder rounded rendering the same model
held **0% FPR at 79.0% recall**. VERIFIED-AT-SOURCE (paper HTML Table 6, read independently by two
passes). A judge who clicks one link ends the pitch in thirty seconds.

**The statement that survives is narrower, is not refutable from that table, and is a better
problem:**

> **A machine can be calibrated. Nothing in its output says whether it was.**
>
> Nine of fourteen complete frontier-model runs flagged **≥95.3% of 43 clean financial
> statements**; one flagged none of them; **and nothing in any of the fifteen outputs distinguished
> the calibrated run from the uncalibrated ones.** The scarce quantity is not detection and it is
> not even calibration — it is **an attributable, per-check, measured statement of how often this
> check is wrong, carried alongside the verdict it produced, together with a computed declaration of
> what the check set did not touch.** No product and no published system produces either object for
> a regulated financial filing.

That is falsifiable in one move: produce a shipping product, or a published system, that prints a
per-rule false-failure rate measured on a declared clean corpus next to the finding that rule
generated, and a computed per-filing residue. §A.6 states the search that failed to find one and
its denominator.

**The three supporting facts, each with its own warrant and denominator:**

| Fact | Number, with denominator | Warrant |
|---|---|---|
| The uncalibrated operating point is the modal one | 7 of 14 complete runs at exactly 100.0% FPR, 2 more at 95.3% (41/43), on 43 clean SEC 10-K-derived statements; the paper explicitly disclaims prompt-invariance | VERIFIED-AT-SOURCE (arXiv:2605.29586 Table 6) |
| The published state of the art in an adjacent task sits below a one-line constant classifier, and nobody computed the line | Best F1 in an 80-cell table = **65.4**; constant always-flag classifier on the ~49.5%-positive CUAD split = **66.2**; across the full ±0.05pp rounding box the floor exceeds the measured maximum by **0.62–0.99 F1 points**, strictly positive at every corner. Zero occurrences of majority/constant/random/trivial/always-predict baseline in the full 2,466-line camera-ready | VERIFIED-AT-SOURCE + DERIVED (CLAUSE, arXiv:2511.00340 / `2026.findings-eacl.305`, EACL 2026 Findings, peer-reviewed; four non-frontier models) |
| Silence from a deterministic program is not evidence either, and this corpus is the proof | **Five** instances of clean, confident, well-formed, wrong output from deterministic programs, found during the preparation of this specification | MEASURED-HERE (§1.5) |

## 1.2 Who has it

**Decision: the buyer is the filer's compliance officer. The supervisor is deleted as a user.**

*Alternative it beat:* the two-user model in `ARCHITECTURE.md` Part 4 ("the filer's compliance
officer pre-submission; a supervisor triaging ~868 filings/year"). *Reason it lost:* the brief's own
Part 7 records that supervisor-side SupTech for IFSCA is **procured** — NEC Corporation India,
awarded 27 January 2026, **₹39,57,36,115.52**, scope explicitly including an RE-facing portal, with
IFSCA refusing in writing to lower a ₹300 crore turnover pre-qualification. Leaving the supervisor
standing in the UX section while the research section kills them is the single clearest internal
contradiction in the corpus and a judge who reads both parts will find it.

**Restatement to use everywhere:** *the supervisor is not the buyer; the supervisor is why the filer
cares.*

**The population, with the denominators kept apart because they are not interchangeable:**

| Population | Value | As at | Warrant |
|---|---|---|---|
| Fund Management Entities | **217** | Mar 2026, IFSCA Bulletin Q4 FY2025-26 (verbatim row `Fund Management Entity (FME) 202 217`) | VERIFIED-AT-SOURCE (`b_q4.txt`) |
| Schemes | **360** | same bulletin (`Fund Management AIFs/ Schemes 327* 360`) | VERIFIED-AT-SOURCE |
| Live Fund Management rows in the public register | **650** | 10 Aug 2026 | MEASURED-HERE (L15, L08) |
| Live FME rows by register sub-category (Registered Retail 22 + Non-Retail 194 + Authorised 13) | **229** | 10 Aug 2026 | MEASURED-HERE (L08) |
| Filings per year | **~868** | — | **MODELED**: 217 × 4, assuming every FME files every quarter including those registered mid-year |

**Never blend these in one sentence.** "217 FMEs and 360 schemes as at the bulletin date" or "650
current Fund Management register entries as at 10 Aug 2026" — never a mixture. The bulletin is a
stock at a quarter end; the register is live and carries branch and multi-capacity registrations.

FME trajectory, VERIFIED-AT-SOURCE across four IFSCA documents on disk: 139 (Dec-24) → 162 (Mar-25)
→ 202 (Dec-25) → **217** (Mar-26). Schemes: 327 (Dec-25) → **360** (Mar-26).

## 1.3 What it costs them

**The honest answer is UNMEASURED, and saying so is load-bearing.**

Nobody has measured how often IFSCA returns an FME filing for correction, what an observation in an
inspection report costs an FME, or what the Principal Officer's personal exposure is worth. The unit
of value is **the avoided deficiency**, and its price is unknown. `RND-BRIEF` §9.6 — one email to
IFSCA's Division of Investment Funds asking whether these checks are already run on receipt — is
therefore **not an errand. It is the demand-side settling experiment and it ranks joint-first with
the supply-side one.** Running the engineering experiment first is the corpus's documented standing
bias operating exactly as described: paying any price to avoid believing something false, and almost
none to find out whether the thing is over.

**868 filings a year is ~3.4 per working day.** That is a volume one competent person handles with a
spreadsheet and a checklist. The product is not selling labour savings and must not pretend to.

**What is measured, and belongs in the pitch as comparators rather than as our cost model:**

| Comparator | Number with denominator | Warrant | What it is NOT |
|---|---|---|---|
| Luxembourg NAV-error base rate | **234** declared NAV calculation errors in 2024 over **13,599** fund units at 31 Dec 2024 = **1.72%**; 234/3,143 registered UCIs = 7.44%; total compensation EUR **20,382,185.07** = 0.00035% of EUR 5,820bn net assets | VERIFIED-AT-SOURCE (CSSF Annual Report 2024 §4.1.2, §1.2), DERIVED for the ratios, independently re-derived by the adversarial pass | Flow-over-stock. 2024 declarations were made under the **old** circular (02/77). **Never importable as an FFR prior for any predicate here.** |
| Human-control failure rate at the top of the profession | **20%** of *inspected* Big Four US audits in 2024 carried a Part I.A deficiency (26% in 2023) | VERIFIED-AT-SOURCE for 2024/2023 at the PCAOB release; **2022 = 26% is SECONDARY**; the "lacked sufficient appropriate evidence" gloss is the Part I.A definition and must be cited from staff guidance, not the release. **The adversarial re-verification pass could not reach pcaobus.org and did not confirm it** | Not 20% of Big Four audits. PCAOB selects engagements risk-targeted, not at random. The word **inspected** never comes off. |
| Rate at which expert-authored regulatory rules are withdrawn | **1,692 of 20,562** EBA validation rules in release 3.5 deactivated at least once = **8.23%**; 1,008 still deactivated, **343 of those `error` severity**; still deactivating (205 in 2024, 94 in 2025, 27 by mid-2026) | MEASURED-HERE (L04 downloaded and counted the EBA's own spreadsheet; independently reproduced by the adversarial pass) | Not an error rate. It is a *lifetime withdrawal rate*, discoverable only because the EBA publishes the events; the EBA never states it as a statistic. |

That last row is the strongest external justification the design has, and it is the sentence the
application should be built around: **the EBA, with ~20,500 expert-authored rules, EU-wide
consultation and a decade of iteration, finds out its rules are wrong from the field.**

## 1.4 How it is handled today — five mechanisms, each with its exact stopping point

**(a) The prescribed return ships its own green tick.**
`'8. Compliance Status'!C11` is a **Yes/No** cell reading *"The FME is in compliance with Investment
Valuation Norms as specified in Sixth Schedule of IFSCA (Fund Management) Regulations, 2025."*
MEASURED-HERE. Nothing in the other 6,756 cells can contradict it. The supervisory record's only
place for a valuation problem to surface is a self-attested checkbox.

**(b) The prescribed return computes a wrong number without noticing.**
`'1. Introduction'!D17`, labelled *"Total No. of Schemes of the FME authorised by IFSCA"*, is
`=SUM(D18:D20)` where
`D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")`,
`D19 = COUNTIF(G54:G63,"*Restricted*")`,
`D20 = COUNTIF(G54:G63,"*Retail*") + COUNTIF(G54:G63,"*Exchange Traded Fund*")`.
Column `G54:G63` is governed by an `x14:dataValidation` list over `Dropdown!$F$3:$F$11` — exactly
**nine** permitted values. **"Special Situation Fund" and "Family Investment Fund" match none of the
five COUNTIF patterns.** A filing declaring either reports a total silently short by one per such
scheme, and the value is legal under the template's own data validation. MEASURED-HERE, read from
raw OOXML, reproduced verbatim by an independent adversarial pass, checkable by an audience in
Excel in thirty seconds. The defence *"D17 only ever meant the total of those three sub-rows"* is
answered by D17's own label, which is unrestricted — quote the label on the slide; the argument
turns on it. **Exposure is UNMEASURED** — how many of the 360 authorised schemes are of those two
types is not in any register dump we hold. Do not claim an exposure figure. The defect is real
whether the exposure is 0 or 60.

**(c) The incumbent tools compete on rule count and publish no error rate.**
Milestone Group's pControl NAV Oversight publishes the most complete public validation catalogue
found anywhere in this research — ~25 named validation families across top-down, bottom-up and
analysis tiers — and **no false-positive rate, no detection rate, and no declaration of what the
oversight cannot check** (VERIFIED-AT-SOURCE, page returned verbatim twice). Confluence advertises
*"40+ countries, 90+ regimes"*; FundApps *"850+ pre-coded global rules… 100+ jurisdictions"*
(SECONDARY). Of **21 vendor/product pages opened at primary URLs** across regulatory reporting,
fund/NAV oversight, audit AI, LLM-evaluation and data-quality tooling, **zero publish a per-rule
measured false-positive rate on clean inputs, and zero declare a first-class residue.** The closest
was Fieldguide's *"an error rate of less than 1% versus manual processes"* — one number for a whole
agent, no denominator, no corpus, benchmarked against another unmeasured baseline. **Coverage
caveat, and it is large: 20+ further named vendors were never opened** (AxiomSL/Nasdaq timed out,
Wolters Kluwer OneSumX and Corlytics returned HTTP 403, all Big Four in-house tools unchecked). The
absence claim is scoped to the opened set and must be stated that way.

**(d) The assurance profession declares the boundary — in prose, once per engagement, and only
when it already knows it hit one.**
- **ISRS 4400 (Revised)** ¶30(j) *requires* the statement *"Had we performed additional procedures,
  other matters might have come to our attention that would have been reported."* ¶30(i) requires
  the report to say no opinion or assurance conclusion is expressed. ¶30(h) requires the
  practitioner to state that they **make no representation regarding the appropriateness of the
  procedures**. ¶13(f) makes objective verifiability a *definitional precondition* of being a
  reportable finding. ¶A56 permits — *may*, not *shall* — identifying procedures that could not be
  performed and why. VERIFIED-AT-SOURCE (IAASB final pronouncement, April 2020, effective for
  engagements agreed on or after 1 Jan 2022).
- **ISA 705 (Revised)** ¶24: *"If the modification results from an inability to obtain sufficient
  appropriate audit evidence, the auditor **shall** include in the Basis for Opinion section the
  reasons for that inability."* ¶19(c) forbids the report from even implying the work was completed
  when disclaiming. ¶17 carries the entire distinction between a known defect and an unexamined
  region in one word: *"possible effects"*. VERIFIED-AT-SOURCE.
- **Where it stops:** ¶20 begins *"When the auditor **modifies** the opinion…"*. **An unmodified
  opinion carries no statement of what was not checked.** The clean audit report is the canonical
  silent all-clear. And the mechanism demonstrably fails to fire when it should, at a measured rate
  — see the PCAOB row above, with the word *inspected* attached.

**(e) Where a regime exists, the arithmetic is already free.**
`daappa`'s NAV Error Materiality Calculator is a **free, no-signup, runs-in-browser** tool that
already encodes CSSF Circular 24/856 — the 0.20%/0.50%/0.50%/1.00%/1.00% tables, the 5% cap, the
4-to-8-week notification window and the EUR 50,000 / EUR 5,000 auditor triggers. VERIFIED-AT-SOURCE,
confirmed live by the adversarial pass. **The scarce good is not the threshold arithmetic.**

## 1.5 The five silent false negatives — the evidence base for the whole product

The brief documented two. Preparing this specification produced three more, across three distinct
mechanisms, from **deterministic programs**, one of them the ecosystem's default library. All five
produced clean, confident, well-formed output that was wrong, with nothing in the output to
distinguish it from a correct answer.

| # | Instrument | What it reported | The truth | Mechanism |
|---|---|---|---|---|
| 1 | Operator's addressee parser | 64.5% of circulars name their addressee | **79.9%** | Over-narrow lexical rule (required the line after `To,` to start with All/The/Chief/Managing) |
| 2 | Operator's formula regex `<f[ >][^>]*>` | **zero** cross-sheet formulas in every workbook | **195 of 294** in the FME workbook alone | Regex cannot match `<f>SUM(...)</f>` — a formula element with no attributes |
| 3 | **openpyxl 3.1.5** — not our code, the ecosystem default | **35** data validations; `7. AML-CFT` has **zero** | **54** validations (35 main-namespace + 19 in the `x14` extension); AML-CFT has **five** | Namespace blindness. `<dataValidation` cannot match `<x14:dataValidation`. openpyxl emits only `UserWarning: Data Validation extension is not supported and will be removed` |
| 4 | Lane L15's register probe | *"The IFSCA public register is a NAME LIST. It does not resolve registration numbers."* | It does. **228 of 228** live FMEs fetched carry a non-empty `RegistrationNumber` via `DirectoryDetailGet` | The list payload carries **both** `EncryptDId` (null in 2,005/2,005) and `EncryptedId` (populated in 2,005/2,005). The probe read the first field, got HTTP 302, and reported an absence |
| 5 | The L4 mutation harness, v1 | Kill rate 100.0%, **mutation score 100.1%** | 18.1% after two fixes | (a) equivalent mutants excluded from both numerator and denominator; (b) mutation sites sampled **only from cells the predicates already read** — the degenerate-baseline failure, committed by the harness built to detect it |

All MEASURED-HERE. Instances 3, 4 and 5 are strictly better pitch material than 1 and 2, because
**3 is not our code**, **4 lands on a live regulator's register**, and **5 is the failure occurring
inside the machinery designed to prevent it.** Instance 3 in particular needs no defence and no
explanation of anyone's code: a compliance tool built on openpyxl would report full validation
coverage of the anti-money-laundering section while checking none of it.

**The claim "the system found nothing is not information" has moved from anecdote to a pattern with
a sample size and a taxonomy.** Three mechanisms: lexical over-narrowing, namespace blindness, and
a denominator drawn from the numerator.

## 1.6 The domain grounding — what the rest of the world specifies, and what IFSCA does not

This subsection exists because the obvious pitch — *"IFSCA is missing what mature jurisdictions
have"* — is false, and a judge from the funds industry will know it. The honest version is stronger.

### 1.6.1 Luxembourg: the reference implementation, and the only place a base rate is published

**Circular CSSF 24/856**, *Protection of investors in case of an NAV calculation error…*, dated
28 March 2024, in force 1 January 2025, repealing Circular CSSF 02/77. 47 pages, opened and
text-extracted; every element below VERIFIED-AT-SOURCE and independently re-derived by the
adversarial pass.

| Element | Content |
|---|---|
| Tolerance thresholds (point 35) | MMFs under the MMFR **0.20%** of NAV. UCITS and comparable UCIs Part II/ELTIFs: bond **0.50%**, mixed **0.50%**, equity **1.00%**, other eligible assets **1.00%** |
| Self-set regime | Part II/ELTIFs reserved to well-informed/professional investors, SIFs, SICARs, EuVECAs, EuSEFs set their own against five mandatory considerations, **capped at 5%**, and *"In no case are UCIs permitted to use by default the 5%-threshold"* |
| Disambiguation (point 37) | Six deterministic rules: per sub-fund for umbrellas, one threshold across all classes; fixed and documented **before the first NAV is published**; the classifier's input is *"the constitutive documents and/or the prospectus"* — a named document, not a judgement; fund-of-funds/index/feeder take the target's policy; a more restrictive marketing-jurisdiction threshold wins and then binds all investors |
| Aggregation (point 38) | Successive sub-threshold errors that **aggregate** to the threshold *are* significant |
| Compensation direction (Tables 4/5) | NAV undervalued → redeemers compensated, UCI compensated on subscriptions. NAV overvalued → subscribers compensated, UCI compensated on redemptions. Clawback permitted only from well-informed/professional investors |
| De minimis (points 123–127) | **Not a regulator-set number** — set per UCI against bank-transfer charges, documented in internal policy; **inapplicable to compensation owed to the UCI** ("unless that amount is lower than one monetary unit") |
| Auditor trigger (point 138) | REA special report where the error concerns a UCITS or UCI Part II **and** total compensation exceeds **EUR 50,000** or a single investor's exceeds **EUR 5,000** |
| Notification (points 154–159) | Deadline **4 to 8 weeks after detection**, not after correction; a quantitative impact calculation must be attached; *"The CSSF refuses incomplete notifications"*; and point 159 — *"the corrective actions… are **not subject to the CSSF's approval**"*. **A declaration regime, not an approval regime** |
| Published base rate | NAV calculation errors declared: **462 (2022) / 344 (2023) / 234 (2024)**; instances of investment-rule non-compliance 1,382 / 1,265 / 1,297; compensation to investors EUR 11,810,270.57 and to UCIs EUR 8,571,914.50 in 2024. Denominators in the same report: **3,143 UCIs, 13,599 fund units, EUR 5,820bn** at 31 Dec 2024 |

### 1.6.2 Ireland: the counter-example that kills the easy pitch

**Central Bank of Ireland Consultation Paper 130** (9 Sep 2019) proposed **MMFs 0.10% / other funds
0.50%**, four error types (NAV, Investment Breach, Fee, Control Breach), an "Appropriately
Rectified" three-step, and recorded the industry de minimis as **€50 retail / €500 institutional**,
which the CBI called *"excessive, particularly for institutional investors."* It quoted the IMF's
2014 assessment: *"the Central Bank has not issued rules prescribing how pricing errors are to be
treated by CIS."* VERIFIED-AT-SOURCE.

**Seven years later it is still not law.** `S.I. No. 316 of 2026` — the rebased Central Bank UCITS
Regulations 2026, July 2026, 5,060 extracted lines — greps as: `materiality` **0**, `toleran*` **0**,
`redress` **0**, `de minimis` **0**, `rectif*` 1 (management-company regulatory capital),
`compensat*` 2 (dilution levy; performance-fee "compensation for past underperformance"), `error` 7
(five "tracking error", two a **client-funds recordkeeping** error). Positive control: `net asset
value` **37**, `valuation` 48, `shall` 485. MEASURED-HERE, reproduced independently by the
adversarial pass, which added the sharpest observation: **Ireland does impose an immediate
error-notification duty in these Regulations — for client recordkeeping, not for NAV. The absence is
a choice, not an oversight.** Irish practice runs on Irish Funds guidance the CBI says it *"has
neither sanctioned nor approved."*

*Coverage note:* the grep denominator is the consolidated 2026 UCITS Regulations only. The AIF
Rulebook, the UCITS Q&A (42nd edition) and the Irish Funds guidance were **not opened**. Whether the
CBI has issued guidance outside the Regulations is **UNVERIFIED**.

### 1.6.3 United Kingdom, United States, IOSCO, ESMA — and the jurisdictional conflict

| Jurisdiction | What is specified | Warrant | Where it stops |
|---|---|---|---|
| **UK** | **COLL 6.3.6G** §4(3): depositary reports immediately where the error is **0.5% or more of the price of a unit**; §5(2): minimal significance if the error is **less than 0.5% of the correct price**; §5(3): *"each price should be considered separately"*; §5(8): amounts "immaterial" need not be paid. The **rule** is COLL 6.6.3R(3)(c); 6.3.6G is guidance | VERIFIED-AT-SOURCE (live FCA Handbook) | **Fund-type-blind** — one number for everything. **No numeric de minimis.** Whether the FCA publishes the SUP 16.6.8R quarterly aggregate is **UNVERIFIED** |
| **US** | **17 CFR 270.2a-4(b)** is a **penny-per-share rule about accruals** (expenses, advisory fees, interest and other income), not a general NAV-error rule. **270.2a-7(g)(1)(i)(B)** is a stable-NAV MMF **shadow-price deviation** rule at ½ of 1% | VERIFIED-AT-SOURCE (Cornell LII mirror; eCFR redirected, sec.gov 403) | The widely-quoted "<1¢ immaterial / ≥½ of 1% reprocess" thresholds come from a **practitioner slide that cites no authority**. Searches for the underlying no-action letter / AICPA guide chapter / ICI memo returned nothing. **The US does not in fact have what Luxembourg has** |
| **IOSCO** | Principle 5: *"Pricing errors that result in a material harm to CIS investors should be addressed promptly, and investors fully compensated"* | SECONDARY — quoted at one remove from CBI CP130 footnote 1, because iosco.org returns HTTP 403 to every fetch and two previously-downloaded "PDFs" are Cloudflare challenge pages. **Do not cite an IOSCO document number** | **Sets no threshold.** "Material harm" is delegated to members |
| **ESMA** | 2022 Common Supervisory Action on Asset Valuation (ESMA34-45-1802): `materiality` **0**, `toleran*` **0**, `pricing error` **0**. Reports the market structure — a **two-stage control**, third-party administrator first, escalation to the manager — and that *"the related remedial procedures are not always sufficiently formalised"* | VERIFIED-AT-SOURCE | **Sets no threshold**, and **publishes no absolute sample size**, so its own "0-10% of the funds in the CSA sample" has no computable numerator. The pan-EU supervisor's valuation report cannot be converted into a rate |

**And the finding that matters more than any threshold:** COLL 6.3.6G §5(3) says *"each price should
be considered separately."* CSSF 24/856 point 38 says successive sub-threshold errors that aggregate
**are** significant. **Two mature regulators, the same phenomenon, opposite rules, both read off the
page.** Materiality of a NAV error is not a fact about the world; **it is a jurisdictional
parameter.** That is the first hard evidence the design has that **a checking relation is not a law
of nature — it is a rule with an owner — and every relation must carry the instrument that
authorises it, with the report stating which one it applied.**

### 1.6.4 India onshore: SEBI mandates that a tolerance exist and does not say what it is

SEBI **Master Circular for Mutual Funds as on 20 March 2026** — 748 pages, 35,350 extracted lines,
1,291,125 characters. MEASURED-HERE.

| Pattern | Hits |
|---|---:|
| `NAV error`, `incorrect NAV`, `erroneous NAV`, `valuation error`, `de minimis` | **0 each** |
| `materiality` | 1 — outsourcing risk assessment, unrelated |
| `toleran*` | 4 |
| `swing pricing` | 24 |
| **positive controls** | `NAV` **371** · `Net Asset Value` **28** · `shall` **2,687** · `valuation` **223** |

**The strong form of the absence:** over the whole 1.29M-character flattened text there are **34
windows of ±180 characters containing any of `error|erroneous|incorrect|wrong|mis-stat|mis-calcul`.
Exactly one of the 34 also mentions NAV — and it is "Tracking Error" adjacent to "Computation of
NAV" in a disclosure-format table.**

What SEBI **does** require, Annexure para **2.9.3.1(vii)**: fund accounting systems must facilitate
*"a. Validation of NAV calculations… d. **Flagging of price variances beyond pre-established
tolerance levels**"*; and para 2.9.3.1(v)(e) requires the AMC to communicate its **error tolerance**
to third-party service providers. **SEBI mandates that a tolerance exist, be pre-established, be
system-enforced, and be communicated. SEBI does not say what it is.** That is the closest existing
regulatory analogue anywhere to what this system proposes: *declare your parameter.*

And the clause IFSCA copied: SEBI (Mutual Funds) Regulations **22(9)(b)(ii)** — *"The asset
management company and the sponsor… shall be liable to compensate affected investors and/or the
scheme for any unfair treatment to an investor resulting from inappropriate valuation."* Set beside
IFSCA's Third Schedule Part A(g), they are the same sentence with the nouns swapped. **The gap is
not an IFSCA oversight; it is an inherited Indian regulatory design in which liability is asserted
and its trigger is left to industry.**

### 1.6.5 GIFT IFSC / IFSCA: what is specified, measured with controls

Extending the operator's §4.1 grep (all 399 circulars, 389 readable, 10 scanned-image failures) to
the two instruments the circular corpus does not contain:

**IFSCA (Fund Management) Regulations 2025, amended to 30 January 2026 — 102 pp, 3,963 lines:**
`NAV error` **0** · `valuation error` **0** · `incorrect NAV` **0** · `toleran*` **0** ·
`swing pricing` **0** · `de minimis` **0** · `restat*` **0** · `materiality` **1** (an unrelated
disqualification provision) · `compensat*` **1** (Third Schedule Part A(g)) · `error` **5** (3 ×
"tracking error", 2 × "Financing of Terrorism"). Positive controls: `shall` **728** · `valuer` **32**
· `true and fair` **6** · `Sixth Schedule` **5**.

**IFSCA Fund Management FAQ, 3 August 2026 — 68 pp:** the bare substring **`error` appears zero
times**. Positive controls: `NAV` 13 · `valuation` 5 · `valuer` 6 · `shall` 183 · `scheme` 405.

All MEASURED-HERE, every count reproduced independently by an adversarial pass.

**What IFSCA does specify, quoted exactly:**

- **Third Schedule Part A(f):** *"The FME shall compute and carry out valuation of investments made
  by its scheme(s) in accordance with the investment valuation norms specified in Sixth Schedule,
  and shall publish the same."*
- **Third Schedule Part A(g):** *"The FME and its controlling shareholders shall be liable to
  compensate the affected investors and/or the scheme for any unfair treatment to any investor as a
  result of inappropriate valuation."*
- **Sixth Schedule, Principles of Fair Valuation, clause (g):** *"The responsibility of true and
  fairness of valuation and correct NAV shall be of the FME…"*
- **Independent valuation, regs 26(2) / 38(2) / 50(2):** assets *"shall be valued by an independent
  service provider"* — with a **fund-of-funds proviso** disapplying it where the target schemes are
  regulated by a financial sector regulator and valued by an independent entity.
- **NAV frequency:** reg **27(1)** VC schemes *"at least on an annual basis"*; reg **39(1)**
  restricted schemes *"at least on a monthly basis"* with a **half-yearly proviso for close-ended
  restricted schemes**; reg **51(1)** retail schemes daily (open-ended) / weekly (close-ended)
  *"in such manner as specified by the Authority"*; reg **69(1)** ETFs daily.
- And the modal verb that matters: regs 27(2), 39(2), 51(2) **and 69(2)** — *four, not three*, a
  correction the adversarial pass supplied — each say the NAV procedure *"**should** be fully
  documented"*, in an instrument that uses **shall** 728 times. **A soft obligation sitting exactly
  where Luxembourg puts its hardest one.**

**The gap, stated so it survives an adversary:**

> **IFSCA specifies, with the force of "shall": who must value, how often the NAV must be computed
> per scheme class, that the FME owns the truth of the NAV, and that the FME and its controlling
> shareholders are liable to compensate for inappropriate valuation.**
>
> **IFSCA does not specify: what makes a NAV wrong, how wrong is wrong enough to matter, who must be
> told, when, in what form, how compensation is computed, in which direction it flows, whether there
> is a floor below which it is not paid, who bears the cost of correction, or whether an auditor is
> drawn in.**
>
> **Third Schedule Part A(g) is a liability rule with no trigger. CSSF 24/856 is 47 pages of exactly
> the trigger.**

And reg 51(1) ends *"in such manner as specified by the Authority"* — a **live delegation hook**.
IFSCA can install a NAV-error regime by circular tomorrow without amending a regulation. Worth one
line in a pitch; worth nothing as a product.

### 1.6.6 The artifact test — and why the NAV wedge is not the product

**Decision: the wedge is prescribed-return verification with declared coverage. It is not a
NAV-error regime.** *Alternative it beat:* building the Indian analogue of CSSF 24/856. *Five
independent reasons, each measured:*

1. **The artifact cannot support it.** Searching all 6,757 `<c>` elements of the FME workbook
   (SHA-256 `7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39`): whole-word `NAV`
   **0 hits**, `per unit` **0**, `dealing` **0**, `subscrib*` **0**, `\bunit` **1** ("Financial
   Intelligence Unit-India"). Across **all nine** prescribed workbooks, in every XML part: `NAV`
   **0**, `per unit` / `unit price` / `units outstanding` **0**. Positive controls on the same
   interface: `Scheme` 123, `USD Million` 31, `Portfolio` 25, `valuation` 6. MEASURED-HERE.
   **Every NAV-error rule on earth — CSSF Tables 4/5, COLL 6.3.6G, Rule 2a-4 — operates on
   (NAV per unit, units dealt, dealing date). None of those three quantities is filed.**
   *Correction the adversarial pass forced, and it must be carried:* the return **does** contain
   fund-level flows — `'2. Summary'` row 4 carries cumulative commitments, cumulative and
   in-quarter funds raised, **cumulative and in-quarter redemptions**, distributions, net
   inflow/outflow and investor counts. The precise claim is therefore: *the return carries
   fund-level net assets and gross subscription/redemption flows, but no per-unit price, no units
   outstanding and no dealing date, so no NAV-error rule on earth can be evaluated against it.*
2. **Ireland removes the moral force.** The set of jurisdictions with a prescribed NAV-error
   materiality regime is roughly **{Luxembourg, UK}**, and they disagree with each other about
   tiering and about aggregation. "IFSCA lacks this" is the majority position, not a scandal.
3. **A regime is a policy proposal, and you cannot ship a policy.** Only IFSCA can set a materiality
   threshold. The judging criteria include *solution feasibility*.
4. **Where the regime exists the tooling is already commoditised** (daappa, free, in-browser).
5. **The prescribed-return route already has first-hand, reproducible defects to demonstrate; the
   NAV route has none.**

**What survives from the NAV work, and it is not nothing:**

- **CSSF 24/856 becomes the prior art for coverage declaration.** Its tolerance tables *are* a
  regulator's ex-ante declaration of the boundary of what counts as a finding, and it publishes the
  resulting rate every year. The line is: *one regulator in the world publishes, in advance, exactly
  what it will and will not treat as a finding, and then publishes the resulting rate annually. We
  compute the equivalent per filing, for a jurisdiction that has neither.*
- **Third Schedule Part A(g) becomes the canonical Unchecked entry**, and its
  *what-would-make-it-checkable* text is now writable with numbers: *"a materiality threshold by
  scheme class of the kind CSSF Circular 24/856 Tables 1–3 specify (0.20% MMF / 0.50% bond and mixed
  / 1.00% equity and other), plus a compensation-direction rule of the kind its Tables 4–5
  specify."* Every number in that sentence is VERIFIED-AT-SOURCE and can ship.
- **Two valuation-axis predicates survive** (specified in Part 4): valuation staleness against the
  frequency owed under regs 27(1)/39(1)/51(1)/69(1), and independent-valuer presence with the
  fund-of-funds proviso returning `UNCHECKED(requires counterparty data)`.
- **Flow-identity predicates over `'2. Summary'` S4/T4/U4/V4 are computable and currently
  unclaimed** — cumulative-vs-period redemption monotonicity, `net inflow ≈ funds raised −
  redemptions`, AUM roll-forward. The "keep exactly two predicates on the valuation axis" cap is
  under-scoped against the artifact and is lifted.
- **A permanent guardrail:** the Luxembourg 1.72% may never be imported as an FFR prior. It is a
  comparator for the pitch and an input to nothing.

## 1.7 The register of withdrawn claims — none of these reappears

| Claim | Status | What replaces it |
|---|---|---|
| *"No measured system can say 'this one is clean'"* | **REFUTED** | §1.1's calibration/attribution statement |
| *"Zero financial regulations encoded anywhere"* | **REFUTED** | EBA 12,925 rule-instances (8,052 distinct), EIOPA 6,767, ESMA 68, XBRL US DQC ~196, FINOS CDM 640 named conditions. Like-for-like distinct total **14,819**, never the mixed-unit sum. What is empty is the *civic/academic* rules-as-code shelf: Catala's 12 domains and OpenFisca's 28 packages are entirely tax/benefit/pension (positive controls passed); FINOS's US LCR demonstrator has no commit on `main` since **5 Jun 2024** at 16★ |
| *"No analogue exists for a financial assertion"* (L7 novelty) | **REFUTED** | ISA 705 ¶24 and ISRS 4400 ¶30(j) are financial and mandatory; ESMA publishes a per-rule `Automatable: Yes/No` (**8 of 68** declared No in the 2025 suite, **six of them `MUST`**); XCCDF Table 26 (NIST, 2012) has **nine** per-item result states. §A.6 states what survives |
| *"CycloneDX `compositions.aggregate`, a ten-state completeness enum, has existed since 1.2"* | **REFUTED** | The field first appears in **1.3 with six states**; the ten-state form arrives in **1.5**; `meta:enum` prose is added in **1.7**. It is *aggregate*, not per-item, and eight of its ten values are one domain-specific partition (first/third party × all/proprietary/opensource) |
| *"Allow rounding tolerance → the recall loss is exactly the price of the FP suppression"* | **REFUTED as framed** | Precision stayed **100.0** and FPR stayed **0.0**; only recall moved (−21.0pp, 100.0→79.0). It is a *rendering artifact*: the injector produced `$534.66M` inside statements otherwise in whole millions, and the model was partly detecting the decimal anomaly. It converts into an L6 relation (*presentation-precision invariance*) with a published effect size |
| *"Adding memory made all 10 models worse"* | **QUALIFIED, source is self-contradictory** | The abstract says *"universally hurt… across all 10 models"*; the body says *"6 models are hurt, 4 are neutral (within ±0.03 GDS)"*. All ten are open-weight; one scaffold; one benchmark. Use *"the memory scaffold never helped"* and state that the paper's abstract and body disagree — or drop the citation |
| *"Reasoning fine-tuning makes abstention 24% worse"* attributed to AgentAbstain | **MISCITED** | The source is **AbstentionBench, arXiv:2506.09038** (Meta/FAIR). The 24% is over **two open-weight distillation pairs** (R1-Distill-Llama-70B vs Llama-3.3-70B-Instruct; s1.1-32B vs Qwen-2.5-32B-Instruct), not 20 models. Relative-vs-percentage-points is **UNRESOLVED** |
| *"AUDITFLOW +64pts"* used as a method comparison | **MISLEADING** | 82.09 − 17.91 = 64.18 is a **self-ablation** of a symbolic-first system on n=67, and invalid outputs rise 1.49% → 35.82%, so roughly half the collapse is unparseable output. The like-for-like number is **+14.93 points** over the strongest baseline, 95% CI **[75.8, 90.2]** |
| *"One 50-task airline benchmark contains 75+ task defects"* | **MISATTRIBUTED** | "75+ task fixes" spans airline, retail **and banking** (τ²-bench). Airline-specific: **27 of 50 tasks fixed** in τ³-bench, with pass^1 rising **+14 to +20 points** after the fixes (retail: −0.4 to +5.5) |
| *"PASC names financial documents as a target"*, marked ⓞ | **REFUTED** | `financial` occurs **once**, in the Introduction, in a list of motivating domains. `finance`, `XBRL`, `invoice` = 0. Every experiment is CoNLL-2003 / WNUT-17 / WikiNEuRal NER. Additionally its Table 1 is internally inconsistent by **≥0.033** in mean prediction-set size, and it shares a sole author with the impossibility-bound paper the design would also have leaned on. **Neither may be cited** |
| *"A 90%-per-step agent is 57% reliable over 8 steps"* | **REFUTED** | **0.9⁸ = 0.4305 → 43%.** 57% is the failure probability |
| *"The IFSCA sandbox is a nearly empty room"* | **REFUTED** | 10 current entities, 47 exits, 5–6 authorisations Feb–Jul 2026 |
| *"Reg 7(7) makes agentic AI illegal"* | **REFUTED** | It sits under *Appointment of Principal Officers and other KMP* — geographic substance, not human-vs-machine. Altus Fund Management IFSC has run an algorithmic Category III AIF at GIFT under it since 28 Apr 2025 |
| *"95%+ of AML alerts are false positives"* | **NOT-FOUND** | No primary study. Nearest independent: BPI 2017, 19 banks, 96% of ~16M alerts never became a SAR — **a different quantity** |
| *"The IFSCA register does not resolve registration numbers"* | **REFUTED, same day, by a sibling lane** | 228 of 228 live FMEs resolve via `DirectoryDetailGet?EncryptedId=…`. See §1.5 instance 4 |
| *"Only 3 data validations are list-type with a named vocabulary"* | **REFUTED** | **22** list-type of **54** validations; **20 resolve to a real enumerable vocabulary** when defined names and cross-sheet ranges are followed |
| *"46% staffing"* | **UNSOURCED** | Appears in `ARCHITECTURE.md` Part 4 and `RND-BRIEF` §5.4 and in **none** of the evidence tables. **Deleted** |
| *"84 numeric/amount fields"* | **UNVERIFIED** | Not reproducible under any defensible counting rule. Either document the rule or withdraw the number. Withdrawn here |
| *"15 date fields"* | **QUALIFIED** | 19 distinct labels contain "date"; the counting rule is undocumented |

## 1.8 What specifically is missing — the four properties, and what would falsify each

The gap is not "nobody declares coverage." It is a conjunction of four properties, and every one of
them is independently checkable.

| # | Property | Nearest existing thing, and exactly where it stops | Falsified by |
|---|---|---|---|
| **P1** | The check set is **derived from the artifact and the instrument**, not agreed with the party being checked | ISRS 4400 procedures are agreed with the engaging party and their appropriateness is **expressly disclaimed** (¶30(h)). XCCDF's denominator is a benchmark someone wrote; OSCAL's is a control catalog someone wrote | Any system that induces its check set from a regulator's own published artifact and says so |
| **P2** | Each check carries a **measured false-failure rate on a named clean corpus, with n**, rendered next to the finding it produced | SPADE computes FFR and consumes it internally; XBRL US DQC gates *for* false positives before publication but publishes no rate; EBA publishes a binary post-hoc deactivation list; ESMA publishes authored severity (`ERROR/WARNING/OK`, Assertion Severity 2.0, REC 21 Jul 2022) which is **intent, not evidence**; LangSmith ships an *alignment score* (agreement with human labels, private, non-gating) | Any product page showing a per-rule error rate with a denominator |
| **P3** | The **residue is computed and typed** — per field, per predicate, from a closed vocabulary, with *what would make it checkable* | ISA 705 ¶24 is prose, once per engagement, **only on modification**; ESMA's `Automatable` is a static property of the **rulebook**, not of a filing; CycloneDX `compositions.aggregate` is an inventory roll-up with no reasons; SPDX names three distinct causes of non-assertion and **deliberately collapses them into one token** | Any system computing, per filing, which correctness propositions were not settled and why |
| **P4** | Both are **bound cryptographically** to the template hash, the filing hash, the register snapshot hash and the predicate-set version, so the boundary is third-party auditable and cannot be restated later | CycloneDX allows a signature over a composition; in-toto/DSSE signs build steps; **no financial analogue found** across the opened set | Any signed financial assertion carrying a coverage denominator |

**The unoccupied claim, in one sentence, with the denominator that must travel with it:**

> **No product or published system, for any regulated financial filing, (a) admits a check into its
> active set only after measuring that check's own false-failure rate on a declared clean corpus and
> its kill rate against seeded defects, and (b) returns, alongside the verdict and signed with it, a
> computed per-field machine-readable declaration of which correctness propositions were not settled
> and why.**
>
> *Established against: 21 vendor/product pages opened at primary URLs across regulatory reporting,
> fund/NAV oversight, audit AI, LLM-evaluation and data-quality tooling, with 20+ further named
> vendors **not checked**; seven arXiv metadata queries with a 186-result positive control; the
> LangChain documentation index (99,944 bytes, 960 lines, 57 matching "eval", `grep -ci spade` = 0,
> `grep -ci "false failure"` = 0); the CycloneDX 1.2–1.7 JSON schemas parsed programmatically;
> XCCDF Table 26; OSCAL v1.2.3; ISRS 4400 (Revised) and ISA 705 (Revised) read in full; the EBA 4.3
> and legacy rule files, the EIOPA Solvency II 2.10.0 file and its Known Issues register, and the
> ESEF 2024/2025 summary-of-tests, all downloaded and counted; and the 63-row IFSCA Fintech Sandbox
> register.*

## 1.9 The two things that would kill this problem statement

Stated now, before either is run, because a criterion may change only by an argument that the old
criterion was wrong — never by the discovery that we cannot meet it.

1. **If IFSCA already runs arithmetic validation on receipt** (`RND-BRIEF` §9.6, one email), the
   entity-facing product is a convenience, not a gap. The *research* result — the residue set and
   the measured boundary — survives and becomes the entire value. The NEC procurement makes this
   urgent: if the supervisor's new system validates on receipt, the filer-side product is a
   nice-to-have.
2. **If a fund administrator serving GIFT IFSC has a written house NAV tolerance**, the boundary
   already exists and is merely private. That is a *better* problem statement, not a worse one —
   *"the threshold is private, uncomparable across administrators, and invisible to the
   supervisor"* — but it changes the pitch. The question, in this exact wording, to KFin
   Technologies, CAMS or Basiz Fund Services: **"When you strike a NAV for an IFSC scheme and it
   differs from what you expected — from your own recomputation, from the prior valuation point, or
   from the manager's shadow — what is the number that makes you stop and escalate rather than
   release? Is that number written down, and who set it: you, the FME, or the administration
   agreement?"** Both calls are **UNRUN**.

---

# PART 2 — WHAT WE ARE ACTUALLY BUILDING

## 2.1 For a non-specialist, in one paragraph

Every quarter, each of the 217 fund managers licensed at GIFT City fills in a spreadsheet the
regulator publishes and sends it back. Somebody then has to decide whether it is right. Today the
only thing in that spreadsheet resembling an answer is a Yes/No box in which the manager attests
that its own valuations comply — and nothing in the other 6,756 cells can contradict it. We are
building the opposite of a Yes/No box: a checker that reads the regulator's own blank template,
works out for itself every relationship the template implies, tests each of those checks against
deliberately corrupted copies of the filing to prove the check can actually catch something, tests
it against correctly-filled copies to measure how often it cries wolf, and then runs only the checks
that survived. What it hands back is not a verdict of "clean." It is two numbers that cannot be
traded against each other — *this many checks ran, and these many properties of your filing could
not be settled at all* — with every unsettled property named, the reason given from a fixed list,
and, where we know it, the exact thing that would make it checkable. Every check that fires shows
how often that same check has fired on filings known to be correct. The whole report is signed
against the hash of the template, the hash of the filing and the version of the check set, so anyone
can re-run it and get the identical answer, or catch us if they cannot. **The product is not a
better tick. It is the removal of the tick and the printing of the boundary.**

## 2.2 For an engineer, in one paragraph

A content-addressed pipeline over a prescribed OOXML workbook. **L0** fetches and hashes four source
classes (blank template, regulation and circular text, live register snapshot, the filing under
test), normalises the workbook through LibreOffice for analysis while attesting over the original
bytes, and parses it twice with independent implementations, failing the run on disagreement. **L1**
induces a field graph directly from the *blank* template's raw OOXML — 6,757 cells, 505
formula-bearing cells (294 authored expressions plus 211 shared-formula dependents), 54 data
validations of which 22 are list-type and 20 resolve to an enumerable vocabulary, 252 merged ranges,
12 defined names, protection state, hidden sheets and the unlocked-cell mask that defines the
denominator — emitting label-anchored stable keys, a degree map (money = 1, counts/dates/ratios/
categoricals = 0), monetary values scaled to integer micro-units, and its own extraction manifest.
**L3** proposes candidate predicates from statutory text and the template's own formulas as **CEL
expressions inside a three-slot envelope** (`applicable` / `expr` / `witness`); it is the only
model-bearing layer on the critical path and it runs **at build time, per template version, never
per filing**. **L4** is the gate and the product: every candidate must carry a verbatim quote of its
clause that `source.find()` locates, an enumeration of every proviso in that clause either
implemented or declared, a seeded-defect kill rate computed over *observably-faulty* mutants only, a
non-degeneracy verdict from Z3 plus a hypergeometric random-flagger control arm, and a false-failure
rate with a corpus provenance tag and a Wilson interval — a predicate with no qualification record
does not load. **L5** evaluates the admitted set in a terminating, side-effect-free language over a
two-document fact model (`filing`, `template`), emitting one of **seven** closed states with a
reason from a **closed vocabulary of nineteen**, per (field × obligation) pair, with `cells_bound`
reported per predicate and zero binding forced to `ERROR`, never `PASS`. **L6** loops the pipeline
over transformed inputs — 25 authored differential and invariant relations, of which 15 need nothing
but the filing — and includes the one check nothing else in the design can perform: a differential
against the blank template's formula graph that detects a formula cell overwritten with a literal.
**L6.5** re-runs every admitted predicate's stored kill-witness against *this* filing in the same
execution and returns `INVALID` if any predicate fails to fire on a fault it is known to detect,
then computes the **residue set** — semantically-wrong mutants of this filing that survive the
entire predicate set. **L7** signs a DSSE/in-toto Statement whose top-level object is `scope` and
which **has no `result` or `status` field at all**, binding template hash, filing hash, register
snapshot hash, predicate-set Merkle root, fault-model version and every predicate's measured rates,
and emits a declared-lossy OSCAL projection for GRC interop. **The whole run over a native `.xlsx`
makes zero model calls, completes in ~30 ms, and that property is enforced as a test, not asserted
as prose.**

---

# PART 3 — THE ARCHITECTURE, REVISED

## 3.0 The dynamics that determine the design

Nine facts. Every decision below is downstream of one of them. Each carries its warrant and its
denominator, and where the brief's version of the fact has been corrected, the corrected form is
what appears here. **If a fact is withdrawn, the decision it drove must be revisited.**

| # | Fact, as it now stands | What it forces |
|---|---|---|
| **F1** | Frontier models flag **≥95.3% of 43 clean** financial statements in 9 of 14 complete runs — **and one run flagged none of them, under the same prompt.** VERIFIED-AT-SOURCE, n = 105 (43 clean / 62 error), 0% FPR carries a 95% Wilson upper bound of **8.2%** | Optimise **false-failure rate**, never detection. And **calibration is achievable and unattributable** — so the product is the attribution, not the calibration |
| **F2** | The published state of the art in contract-discrepancy detection scores **F1 65.4** against a constant always-flag floor of **66.2** on a ~49.5%-positive split; the floor exceeds the measured maximum by **0.62–0.99 F1 points across the entire rounding box**; the camera-ready contains **zero** mentions of a constant/majority/random baseline over 2,466 extracted lines | **L4 test 2 (non-degeneracy) is a gate, not a precaution**, and it has a peer-reviewed exhibit |
| **F3** | A deterministic rule verifier gets **0% false alarms at 52.8% recall** over 1,942 injected errors — **and the 0% is true by construction**: the 15 relations are *"guaranteed consistent in our clean data by construction"* | Rules are precise and incomplete, **and an FFR measured on a corpus built to satisfy the predicate is not an FFR.** `clean_corpus_independent_of_predicate` becomes a required field |
| **F4** | **45–48%** of agent failures in single-control domains are false successes (airline 45% of 393, retail 47% of 895); **75.8%** on AppWorld (1,425 of 1,879 trajectories with explicit status claims, covering 2 of 4 architectures); pooled tau2 rate **35.6% of 1,730**. An LLM judge detects them at **AUROC ≤0.65**; a TF-IDF+XGBoost detector reaches 0.825–0.953 | **A model may never be the final judge.** Every model output crosses a deterministic boundary before affecting a verdict |
| **F5** | At a 10% flag rate the structural detector recalls **72% [63,80] at 50% precision [40,60]**; the LLM judge recalls **13% [8,17] at 58% precision [32,79]**. **The judge's precision is equal or higher at 10% and 20% flag rates** | **Precision is scarce for both methods.** Every detector, including ours, ships its own FFR next to its output — including the ones we like |
| **F6** | The evidence that the fix works is a **hypothesis, not an effect size**: false success falls to **3%** in the one dual-control domain where the simulator can independently verify state, but that is **15 false-success cases in one domain**, and the author explicitly declines the causal reading — *"confounds remain… we flag this as a hypothesis warranting future study"* | Carry it as the author carries it. It is directionally the best support the design has and it is **not** a number for a slide |
| **F7** | `pass^k` collapses ~60% → ~25% over 8 attempts (gpt-4o function-calling, **τ-retail only, n=115**; τ-airline never reaches 60% at k=1). **0.9⁸ = 0.4305** | Keep model-bearing chains **short and stateless**. Report `pass^k`, never `pass@1`. **No agent loop** |
| **F8** | Capability does not supply restraint: **59.5% best paired accuracy** across 263 paired tasks / 42 executable environments / 17 frontier models / 4 harnesses; act 80.6% vs abstain 59.1% | Do not wait for a better model, and do not rely on model self-assessment for abstention. *(This row alone carries the claim; the memory and reasoning-fine-tuning rows are withdrawn to footnotes — see §1.7)* |
| **F9** | On a real prescribed return, **17 of 24** candidate correctness predicates are script-settleable — **and the composition matters more than the ratio: 15 exact + 2 approximate**, because register resolution is a fuzzy name/number match with a non-zero false-failure rate by construction. Independently, **the decidable set is unbounded and the undecidable set is fixed at 7**: one predicate per formula-evaluating cell (505) + per validation (35) + per shipped vocabulary (15) takes 17/24 = 71% to **555/562 = 98.8%** in an afternoon without writing a single interesting check | **The boundary is the product, and it must not be reported as a fraction.** A metric that improves monotonically with effort spent on things that do not matter, and is invariant to effort spent on things that do, is Goodhart-broken. Replace with two counts and a **measured residue** |

**The design thesis, unchanged in substance and corrected in claim:**

> *Put the model only where generation is hard and verification is cheap, adjudicate it with
> programs, and make the residue a declared output rather than a silence.*

**This thesis is no longer novel and must not be claimed as such.** PROVE (arXiv:2607.28218,
30 July 2026) states it almost verbatim for clinical-trial regulatory reporting — *"not reliable
substitutes for programmed statistical checks… reserving numerical and logical decisions for
programmed validators"* — eleven days before this specification. Cite it as corroboration on the
slide that states the thesis. **The novelty moves to the gate and the residue.** (§A.6.)

## 3.1 What changed from the eight-layer design, in one table

| Layer | Change | Driver |
|---|---|---|
| **L0** | **[+]** dual-parser differential ingest, fail on disagreement · **[+]** LibreOffice normalisation for analysis with attestation over original bytes · **[+]** instrument-stream watcher · **[~]** QuantMind demoted to unnecessary for this artifact class | Three implementations returned 244 / 294 / 505 on one file; openpyxl round-trip destroys 98.2% of the file; the 29th Authority Meeting of 24 Jul 2026 moved a predicate's rule and nothing would have noticed |
| **L1** | **[~]** iterate **all** sheets including hidden · **[+]** parse `extLst`/`x14:dataValidation` · **[+]** materialise shared formulas · **[~]** label-anchored keys, coordinates as a resolved attribute · **[+]** pin vocabularies from the blank template's hash · **[+]** degree map · **[+]** integer micro-units · **[+]** extraction manifest · **[+]** L1b clause graph | The `Dropdown` sheet is hidden **and is the only unprotected sheet**; 19 of 22 list validations live in `extLst`; 211 of 505 formula cells are text-free stubs; CEL has no decimal type |
| **L2** | **[~]** split into **L2a structural (deterministic)** and **L2b document (model-bearing)**; **removed from the critical path**; conformal coverage claim withdrawn unless exchangeability is argued; conformal scoped to four named populations | Zero embedded images in 9 of 9 workbooks; 0 of 3,755 unlocked cells ambiguous under the address key; a team-authored calibration set against real filings is a known distribution shift and the guarantee is **void, not degraded** |
| **L3** | **[!]** renamed *candidate predicate proposal* · **[+]** verbatim-quote provenance guard · **[+]** output is **CEL in an envelope**, not Python · **[~]** reframed as the measurement, not the gate | Every measured system that works has a rejector; every one that fails lacked one. `k = 0` is a publishable result |
| **L4** | **[!]** renamed **seeded-defect adequacy** (not "mutation testing") · **[~]** denominator becomes `K/O` over *observably-faulty* mutants · **[+]** a **fourth test: scope faithfulness** · **[+]** FFR requires `corpus_provenance ≠ SELF-AUTHORED` · **[+]** Wilson intervals, never point estimates · **[+]** control arm seeding into fields the predicate does **not** read · **[+]** emits liveness witnesses · **[+]** L6 relations qualify here | mutmut/PIT/Stryker mutate **code**; 46.8% of naively generated spreadsheet mutants are unobservable; FFR on a self-authored corpus has expected value zero regardless of predicate quality; frontier models wire provisos wrong at Edge-F1 ≈ 0.22 while grounding the right spans at SpanFaith 0.77–0.79 |
| **L5** | **[~]** **seven** states, not three · **[~]** **nineteen** namespaced reasons, not six · **[+]** `cells_bound` per predicate, zero ⇒ `ERROR` · **[+]** denominator computed twice by independent code paths · **[+]** severity tier orthogonal to state | XCCDF separates four causes the six-reason vocabulary conflates or omits; a crashing predicate was indistinguishable from a philosophically-uncheckable property; a shared-parser denominator error is invisible by construction |
| **L6** | **[!]** renamed **differential and invariant probes**; **[~]** it is a **loop over the pipeline**, not a downstream stage · **[−]** all three NAV-invariance relations deleted · **[~]** SUT declared: the workbook-as-program · **[+]** formula-override detection · **[+]** cross-format agreement · **[+]** cross-period continuity | Metamorphic testing requires a re-executable system under test and a filed workbook is a **record**; four of the brief's five relations false-alarm on a *correct* filing and the fifth is vacuous; there is no NAV field anywhere in nine workbooks |
| **L6.5** | **[+] NEW LAYER: run-time self-check + residue set**, producing a third verdict state `INVALID` | Nothing in the eight layers would catch the design's own §4.4 failure, and five instances of it were found while writing this |
| **L7** | **[~]** schema has **no** `result`/`status` field; top level is `scope` · **[+]** `qualified_against{}`, residue size, fault-model version, unread-source gap · **[!]** "coverage" renamed **settled fraction** · **[+]** OSCAL projection declared lossy · **[?]** signer decided (§5.2) | A downstream consumer must not be able to render a pass because there is nowhere to read one; "coverage" collides with conformal coverage three pages away |

**Two sentences are deleted from the corpus permanently:**
- *"the registry grows monotonically"* — incompatible with re-qualification and quarantine. **Coverage must be able to fall, and the step-downs are the most credible thing on the chart.**
- *"which makes the coverage claim true by construction, not by discipline"* — unfalsifiable as written. Replacement: *"the coverage claim is true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement."*

## 3.2 The corrected data flow

```
 ┌──────────────────────────────── BUILD TIME — batched, offline, human-reviewed, amortised ───────────────────────────────┐
 │                                                                                                                          │
 │  regulation PDF ─┐                                                                                                       │
 │  399 circulars ──┼──► L1b CLAUSE GRAPH (deterministic)                                                                   │
 │                  │      Docling → Akoma Ntoso; eId per clause; FRBR URI per instrument; amendment chains                 │
 │                  │      76/82 = 92.7% of amending circulars cite a resolvable target → parser; the 6 → UNCHECKED         │
 │                  │      10/399 circulars unreadable (scanned) → permanent declared coverage gap on every predicate       │
 │                  │      whose correctness rests on the negative search result                                            │
 │                  ▼                                                                                                       │
 │            ╔═══════════════════════╗          ╔═══════════════════════════════════════════════════════════╗              │
 │            ║  L3  CANDIDATE        ║  CEL     ║  L4  QUALIFICATION GATE          (deterministic)          ║              │
 │            ║      PROPOSAL         ║ envelopes║   T0 scope faithfulness  — every proviso implemented       ║              │
 │            ║   ★ THE ONLY MODEL ★  ║ ───────► ║      or declared, verbatim clause quote must locate        ║              │
 │            ║   statutory text +    ║          ║   T1 seeded-defect adequacy  KR = K/O  (O by recalc)       ║              │
 │            ║   template formulas   ║          ║   T2 non-degeneracy   Z3 UNSAT proof + hypergeometric      ║              │
 │            ║   verbatim-quote guard║          ║      random-flagger control arm                            ║              │
 │            ╚═══════════════════════╝          ║   T3 false-failure rate  + corpus_provenance + Wilson CI   ║              │
 │                        ▲                      ║   emits: kill_case, pass_case (liveness witnesses)         ║              │
 │            hand-authored predicates ─────────►║   ADMIT ⇒ append-only PREDICATE REGISTRY (Merkle root)     ║              │
 │            L6 relations ─────────────────────►╚═══════════════════════════════════════════════════════════╝              │
 └──────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                            │  registry_root
 ┌──────────────────── RUN TIME — ZERO MODEL CALLS ON THE VERDICT PATH (asserted in CI) ───────┼──────────────────────────┐
 │                                                                                             │                          │
 │  blank template ──┐                                                                         │                          │
 │  filing .xlsx ────┼──► L0 INGEST (deterministic)                                            │                          │
 │  register JSON ───┘      • sha256 ORIGINAL BYTES  ← this is what L7 signs                    │                          │
 │       ▲                  • soffice --convert-to xlsx  → normalised copy FOR ANALYSIS ONLY    │                          │
 │       │                  • DUAL PARSER: raw zipfile+lxml  ⟂  openpyxl                        │                          │
 │       │                    disagree on {sheets, cells, formula cells, validations,           │                          │
 │       │                    defined names, hidden sheets} ⇒ IngestDisagreement, FAIL THE RUN  │                          │
 │       │                  • register snapshot content-addressed (it is mutable and undated)   │                          │
 │       │                                    │                                                 │                          │
 │  [+] INSTRUMENT WATCHER                    ▼                                                 │                          │
 │  daily hash of IFSCA        ┌───────────────────────────────────────────────┐                │                          │
 │  circulars + Authority      │ L1  SCHEMA INDUCTION       (deterministic)     │                │                          │
 │  meeting pages.             │  from the BLANK template, all sheets incl.     │                │                          │
 │  new instrument citing      │  hidden; extLst/x14 validations; shared        │                │                          │
 │  a regulation a predicate   │  formulas materialised; label-anchored keys;   │                │                          │
 │  claims ⇒ that predicate    │  degree map; integer micro-units;              ├── TemplateSchema (pinned, hashed)         │
 │  → PROVISIONAL              │  UNLOCKED-CELL MASK = THE DENOMINATOR;         │       │                                   │
 │  (pessimistic, human clears)│  + EXTRACTION MANIFEST (parts read/skipped,    │       │                                   │
 │       ▲                     │    constructs not understood, 3-way agreement) │       │                                   │
 │       └─────────────────────└───────────────────────┬───────────────────────┘       │                                   │
 │                                                     │                               │                                   │
 │                    ┌────────────────────────────────┴──────────┐                    │                                   │
 │                    ▼                                            ▼                    │                                   │
 │      L2a STRUCTURAL EXTRACTION            L2b DOCUMENT EXTRACTION                    │                                   │
 │      (deterministic — NO MODEL)           (model — CONTINGENCY ONLY)                 │                                   │
 │      native xlsx + register JSON.         unstructured attachments only.             │                                   │
 │      key = lookup against L1.             constrained decoding over L1's key         │                                   │
 │      0 of 3,755 cells ambiguous           enum; conformal abstention on P1–P4;       │                                   │
 │      under the address key.               NEVER the sole method on a PASS.           │                                   │
 │                    │                                            │                    │                                   │
 │                    └────────────────┬───────────────────────────┘                    │                                   │
 │                                     ▼   Facts{key, value, unit, provenance, warrant} │                                   │
 │                    ┌────────────────────────────────────────────────────────────┐   │                                   │
 │                    │ L5  EXECUTION AND VERDICT            (deterministic)         │◄──┘  admitted predicates only          │
 │                    │  CEL over two bound names: `filing`, `template`. No clock,   │                                       │
 │                    │  no network, no filesystem. Terminating by language design.  │                                       │
 │                    │  PASS · FAIL · INDETERMINATE · NOT_RUN · NO_PREDICATE ·      │                                       │
 │                    │  OUT_OF_SCOPE · INFORMATIONAL     × 19 namespaced reasons    │                                       │
 │                    │  × severity tier {BLOCKING | ADVISORY}, set by measured FFR  │                                       │
 │                    │  cells_bound reported per predicate; 0 ⇒ ERROR, never PASS   │                                       │
 │                    │  denominator computed TWICE by independent code paths        │                                       │
 │                    │  provenance composes by weakest input                        │                                       │
 │                    └──────────────────────────┬─────────────────────────────────┘                                       │
 │                                               │                                                                          │
 │        ┌──────────────────────────────────────┴──── L6 IS A LOOP, NOT A STAGE ────────────────────────────┐              │
 │        │  L6 DIFFERENTIAL & INVARIANT PROBES     SUT = the workbook-as-program (505 recomputable cells,     │              │
 │        │                                          all carrying cached values → a baseline exists)           │              │
 │        │  transform the input → re-run L0…L5 → compare. 25 relations, all qualified through L4:            │              │
 │        │    15 need the filing alone · 4 need the pinned template · 3 need two filings · 1 multi-instance  │              │
 │        │    2 are checker self-tests (not reported to the filer)                                           │              │
 │        │  ★ formula-override differential: template says formula, filing carries a literal ★               │              │
 │        │  τ(n) = n × 0.005 USD Million. Decimal, ROUND_HALF_UP. Counts get ZERO tolerance.                  │              │
 │        └──────────────────────────────────────┬───────────────────────────────────────────────────────────┘              │
 │                                               ▼                                                                          │
 │                    ┌────────────────────────────────────────────────────────────┐                                       │
 │                    │ L6.5  SELF-CHECK AND RESIDUE          (deterministic)       │                                       │
 │                    │  for each admitted predicate: instantiate its stored        │                                       │
 │                    │  kill_witness against THIS filing and re-run.               │                                       │
 │                    │  any survivor ⇒ verdict state = INVALID                     │                                       │
 │                    │     "this system could not demonstrate it was working here" │                                       │
 │                    │  RESIDUE SET := WRONG mutants of THIS filing that no        │                                       │
 │                    │  predicate rejects. Reported with each survivor's class.    │                                       │
 │                    └──────────────────────────┬─────────────────────────────────┘                                       │
 │                                               ▼                                                                          │
 │                    ┌────────────────────────────────────────────────────────────┐                                       │
 │                    │ L7  ATTESTATION                       (deterministic)       │                                       │
 │                    │  DSSE + in-toto Statement. subject[] = filing ⊕ template.   │                                       │
 │                    │  ★ NO `result` FIELD. NO `status` FIELD. Top level = scope ★ │                                       │
 │                    │  binds: template sha256 · filing sha256 · register snapshot │                                       │
 │                    │  sha256 · registry Merkle root · fault-model version ·      │                                       │
 │                    │  per-predicate KR and FFR with corpus provenance ·          │                                       │
 │                    │  residue size · unread-source gap (10/399) ·                │                                       │
 │                    │  boundedSilenceStatement (required by schema)               │                                       │
 │                    │  → self-contained HTML report (hashable, emailable, offline)│                                       │
 │                    │  → OSCAL AR + POA&M projection, flagged LOSSY in the file   │                                       │
 │                    └────────────────────────────────────────────────────────────┘                                       │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Four properties of this diagram that the previous one got wrong, and each is load-bearing:**

1. **The model is at build time, not run time.** "Two model calls, both short" contradicted L2 (split
   conformal needs O(calibration set) calls plus one prediction set per fact) and L3 (SPADE is an
   iterative generate-execute-score-select loop). The honest and stronger property is **"zero model
   calls in the verdict path"** — enforceable as a CI assertion that the process handling a filing
   opens no socket to a model endpoint. A property you can assert in CI beats a property you assert
   in prose.
2. **L6 is a loop over L0–L5, not a box after L5**, and its relations pass through L4 like any other
   predicate. Drawn as a downstream stage it teaches the wrong mental model to everyone who reads it,
   and it implies relations are self-validating. They are not: a violated relation means *the artifact
   is wrong* **or** *our relation is wrong*.
3. **L6.5 exists**, and it is the only layer that would have caught the five failures in §1.5.
4. **The unlocked-cell mask, not the predicate set, defines the denominator.** Deriving the
   denominator from the numerator produced a 99.2% coverage figure in one lane and a 100.1% mutation
   score in another, on the same afternoon.

## 3.3 Layer by layer

Each layer is specified with the same six fields: **input type · output type · model? · failure
modes · self-check · reused component and the alternative it beat.**

---

### L0 — INGEST · *deterministic, no model*

**Input**
```
BlankTemplate   : bytes            (published .xlsx, retrieved from a named URL)
Instrument[]    : bytes            (regulation PDF, 399 circular PDFs)
RegisterQuery[] : HTTP GET spec    (DirectoryGetList, DirectoryDetailGet)
Filing          : bytes            (the .xlsx under test, as delivered)
```

**Output**
```
ContentAddressedBlob {
  sha256_original : str            # over the bytes AS DELIVERED — this is what L7 signs
  media_type      : str
  retrieved_at    : RFC3339
  origin_uri      : str
  normalised_ref  : sha256 | null  # the LibreOffice output, for ANALYSIS ONLY
  parse_a         : ParseResult    # raw zipfile + lxml
  parse_b         : ParseResult    # openpyxl
  agreement       : {field: bool}  # any false ⇒ the run does not proceed
}
RegisterSnapshot { sha256, fetched_at, endpoint, records[] }
```

**Model?** No. Never.

**Failure modes, all observed**
- *Namespace blindness.* A parser that cannot see `<x14:dataValidation>` reports 35 validations where
  there are 54, and reports the AML-CFT sheet as having zero where it has five. MEASURED-HERE on both
  a hand-written regex and openpyxl 3.1.5 — **two independent instruments producing the identical
  wrong number by the identical mechanism, with no error and no warning that reaches a log.**
- *Shared-formula invisibility.* 211 of 505 formula cells in the FME workbook are
  `<f t="shared" si="N"/>` — an element with no text. A text-matching pass loses **41.8%** here, and
  across all nine workbooks **825 of 1,495 = 55.2%**, ranging **0% to 92.0%** per workbook. The bias
  is not random: Excel factors a formula into a shared master plus stubs exactly when the same
  relation repeats down a column, which is precisely what **row and column totals** are. **The
  measurement error is correlated with the quantity being measured, in the direction that supports
  the thesis.** That is the most dangerous shape an instrument error can take.
- *Destructive round-trip.* `load_workbook(path)` → `save()` with nothing edited takes the FME
  workbook from **3,663,391 → 65,877 bytes**, 42 parts → 18, deleting a **3.55 MB Power Pivot model
  that is 96.9% of the file**, 26 Power Query connections, `calcChain.xml`, and **every one of the 19
  `x14` validations**. MEASURED-HERE.
- *Register mutability.* The register is live and undated. A verdict citing "the register" without a
  snapshot hash is not reproducible and L7 cannot sign it.
- *Reading the wrong field.* `EncryptDId` is null in 2,005 of 2,005 records; `EncryptedId` is
  populated in 2,005 of 2,005. Reading the first produces HTTP 302 on every record forever, and the
  honest-looking conclusion *"the register does not expose registration numbers."*
- *Zip and XML bombs.* An `.xlsx` is a zip of XML supplied by an adversarial-capable party. Entry
  count, per-entry uncompressed size and total ratio must be checked **before** parse; `lxml` must
  run with `resolve_entities=False`, no DTD and no network.

**Self-check**
- **Dual-parser differential ingest.** Two independent implementations must agree on `n_sheets`,
  `n_cells`, `n_formula_cells`, `n_validations`, `n_defined_names`, `sheet_names`, `hidden_sheets`.
  Disagreement raises loudly and **fails the run** — it is never logged and continued.
  *This lane's own history is the evidence it works: three implementations returned 244 / 294 / 505
  on the same file, two of them sitting in the same directory, and the divergence went undetected in
  the authoritative document.*
- **Extraction manifest**: parts read, parts skipped, namespaces encountered, constructs not
  understood (`x14:dataValidation`, `model/item.data`, `connections.xml`, `t="array"`). Any construct
  in the "not understood" list marks its affected fields `UNCHECKED(extractor_disagreement)` — never
  silently absent.
- **Positive control before any absence.** A parser returning 0 for a class is not evidence of
  absence until it has returned a non-zero count for a class known to be present.

**Component decisions**

| Job | **Decision** | Alternative it beat, and why |
|---|---|---|
| Authoritative parse | **raw `zipfile` + `lxml`** (stdlib / BSD) | **openpyxl alone** — drops all 19 `x14` validations with a `UserWarning` nobody reads, and its round-trip destroys 98.2% of the file. openpyxl is retained for two narrow jobs it does better than anything else: **row-shifting shared formulas** (verified: `O4 → '=SUM(C4:N4)'`, `E77 → '=IFERROR(D77/$O$3,0)'` on dependents) and **writing mutants**. It is never the schema authority |
| Normalisation for analysis | **`soffice --headless --convert-to xlsx`** (MPL-2.0) | **Nothing** — but it earns its place by measurement, not preference: it expands every shared formula into explicit text (294 → 505) **and migrates all 19 `x14` validations into the main namespace** (3 → 22 list-type), deterministically, in 3.9 s. Caveat carried: it writes **53** where 35 + 19 = 54, drops the Power Pivot model and `calcChain`, so it is a **normaliser, not a lossless converter**, and the discrepancy must be characterised before it ships |
| Attestation target | **the original bytes** | **the normalised copy** — attesting over a re-serialised file means signing a hash of something that is not the filing |
| Document AI for the xlsx | **none** | **Docling / Marker / MinerU** — MEASURED-HERE: `xl/media/` is empty, **0 bytes, in 9 of 9 workbooks**. Every number is native. Introducing a model here converts a deterministic layer into a model-bearing one for no gain |
| Knowledge-engineering framework | **none** | **QuantMind** (MIT, 2.3k★, NeurIPS 2025 GenAI-in-Finance workshop) — its typed shapes are Papers/News/Earnings/Factors/Theses, i.e. *research* artifacts. A protected xlsx with merged headers, a hidden sheet, `extLst` validations and four `#REF!` defined names is not in that family, and `zipfile` + `lxml` + `openpyxl` already does everything L0 needs for this artifact class. **The dependency is unnecessary; queue item 9.7 is answered without running it** |
| Register access | **one `GET DirectoryGetList` with `PageSize=2100`** (2,005 records, ~3.4 MB, one request) **+ `GET DirectoryDetailGet?EncryptedId=…` per entity**, snapshot content-addressed | **Scraping the rendered page** — the page is client-rendered with zero data rows in the HTML, the same trap that hid the hackathon FAQ. **A format regex on the registration number** is separately rejected at 38.2% measured FFR (§3.3/L4) |
| Sandboxing the parser | **gVisor (`runsc`) + `seccomp` + `--network=none` + read-only rootfs + tmpfs + RLIMIT + wall-clock kill** | **Firecracker** — hypervisor-grade isolation against an adversary we do not have, at a VM per filing. **E2B** — a managed remote service means the filing leaves our boundary, which is a data-residency conversation we should not have to have. **Pyodide/WASM** — the Grist "Cellbreak" escape (`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, disclosed 21 Jan 2026) escaped a Pyodide sandbox by three independent routes and was fixed by putting Deno's permission system underneath it, not by hardening Pyodide. **WASM-of-CPython is a resource boundary and a portability layer, not a security boundary.** *(And the circulating claim that "CVE-2026-5752 is a Pyodide vulnerability and the project is unmaintained" is a conflation: that CVE is against **Cohere Terrarium**, and Pyodide is a 14.8k★ MPL-2.0 project with active governance. Do not repeat it.)* |

**[+] The instrument-stream watcher.** A daily content-hash of IFSCA's circular page and Authority-
meeting page. Any new instrument citing a regulation that a predicate claims to implement moves that
predicate to `PROVISIONAL`, **automatically and pessimistically**; a human clears it. This is a
diff-and-flag job, not an NLP problem, and it is the only mechanism that would have caught the
**29th IFSCA Authority Meeting of 24 July 2026**, which decided that NAV periodicity for close-ended
Restricted Schemes *"may be enhanced by the FME from semi-annual to annual, subject to prior approval
of at least 75% of the investors in the scheme by value of their investments"* and that independent
valuation *"shall be relaxed for the investments made in underlying scheme(s) which are valued by an
independent entity."* VERIFIED-AT-SOURCE, dated 17 days before this specification. Both decisions
land directly on the two most sophisticated predicates in the decidable set, and **the owed frequency
now depends on a fact the workbook does not collect.**

---

### L1 — SCHEMA INDUCTION · *deterministic, no model*

**Input**: `BlankTemplate` blob (pinned by hash) — **never the filing.**

**Output**
```
TemplateSchema {
  template_sha256 : str
  fields : { stable_key -> Field }
  Field {
    key            : (sheet_name, merged_header_path, row_label)   # IDENTITY
    coords         : "Sheet!A1" | UNRESOLVED                        # a RESOLVED ATTRIBUTE, not identity
    type           : numeric | date | bool | string | enum
    degree         : 0 | 1              # 1 = money (scales), 0 = counts/dates/ratios/categoricals
    scale          : micro_units | none # monetary values are integers, not floats
    unit           : "USD Million" | "count" | "percent" | ...
    validation     : {kind, bounds, vocabulary_ref} | null
    formula        : {encoding: TEXT|SHARED_MASTER|SHARED_DEPENDENT|ARRAY|NONE, si, master_ref, resolved}
    unlocked       : bool               # from styles.xml cellXfs → <protection locked="0"/>
  }
  vocabularies  : { vocab_key -> [str] }   # PINNED from the blank template's hash
  carry_edges   : [(src_key, dst_key)]     # 195 cross-sheet formula strings, 223 carry cells
  field_surface : [stable_key]             # unlocked ∧ non-formula — THE DENOMINATOR
  manifest      : ExtractionManifest
}
```

**Model?** No.

**What the induction actually recovers, measured on the real artifact** (MEASURED-HERE, reproduced
independently by four lanes and one adversarial pass, on SHA-256 `7d9a…ea39`):

| Quantity | Value | Note |
|---|---:|---|
| Sheets | **10** | 9 visible + `Dropdown` (`state="hidden"`) |
| Cells (`<c>` elements) | **6,757** | exact agreement across every independent pass |
| Formula-bearing cells | **505** | = 294 authored expressions + 211 shared-formula dependents |
| — of which express a checkable relationship | **138 (27.3%)** | 135 SUM identities + 3 COUNTIF tallies |
| — of which are pure carries | **223 (44.2%)** | the rhetorical point survives at both denominators |
| Distinct authored expressions | **294** | 181 cross-sheet carries (61.6%), 50 IFERROR, 35 SUM, 14 IF, 11 other, 3 COUNTIF — **class by class confirmed by three independent parsers** |
| Cross-sheet formula strings | **195 of 294 = 66.3%** | confirmed exactly |
| Data validations | **54** | 35 main-namespace + **19 in `extLst`/`x14`** |
| — list-type with a named vocabulary | **22** | 20 point at `Dropdown!$X$n:$X$m`, 2 at defined names |
| — that resolve to a real enumerable vocabulary | **20** | resolver follows `Choicelist`/`YesNolist`/`YesNoNA` and cross-sheet ranges |
| Vocabularies shipped on the hidden `Dropdown` sheet | **15** | 12 of them **unwired** — a free predicate harvest |
| Merged ranges | **252** | three-way agreement (openpyxl, calamine, raw XML) |
| Defined names | **12** | **4 point at `#REF!`** in the regulator's own published blank |
| Protected sheets | **9 of 10** | SHA-512 `sheetProtection`; `Dropdown` alone unprotected **and hidden** |
| **Field surface** (unlocked ∧ non-formula) | **3,747** | **the denominator.** Per sheet: Portfolio 1,698 · Investors 897 · PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22 |
| Build time, cold, single process | **28–44 ms** | lxml |

*Denominator note, so two true numbers are never quoted against each other:* 3,747 counts **unlocked
non-formula** cells; a separate pass counting **all unlocked cells in used ranges** returns 3,755.
Both are right under their own definitions; the field surface is 3,747 and every coverage statement
uses it.

**Failure modes**
- *Scope truncation.* Iterating **visible** sheets silently drops `Dropdown`, so the vocabulary set
  becomes empty, and `all(v in vocab for v in values)` over an empty vocabulary either fails
  everything or — far more likely in practice — **passes vacuously.**
- *Vacuity by empty set.* `all([])` is `True`. `sum([]) == 0`. `len(rows) == declared` is satisfied
  by `0 == 0` when extraction silently returned nothing.
- *Coordinate-anchored keys.* A row insertion in a new template version silently rebinds every key
  below it.
- *Vocabulary read from the wrong document.* `Dropdown` is **the only unprotected sheet**. A
  predicate that reads the vocabulary from the **filed** workbook is validating the filer's data
  against a list the filer can edit. Any filer who edits `Dropdown!$F$3:$F$11` to add a scheme
  category passes the check. This is not hypothetical; it is a one-line consequence of
  `protected=False`.
- *Float arithmetic.* CEL has no decimal type and the filing is USD Million to two decimals.
  Unscaled, every arithmetic predicate inherits a floating-point false-failure rate we did not
  choose and cannot attribute.
- *Broken references in the authoritative artifact.* `ExternalData_1 = '2. Summary'!#REF!` and three
  more. **The blank template ships broken**; any predicate resolving defined names must handle it.
- *Scheduled obsolescence.* `Dropdown!$E$3:$E$6` = `2025-26, 2026-27, 2027-28, 2028-29`. The workbook
  **cannot express FY2029-30.** Version churn is not a risk; it is scheduled.

**Self-check**
- Three-way agreement on the induced schema (raw / openpyxl / post-normalisation). Where they
  disagree, the affected fields are `UNCHECKED(extractor_disagreement)` **by construction**.
- A **regression test asserting `54` validations and `22` list-type against the checked-in workbook
  hash.** This is a required fix with a required test, not an option.
- The denominator is computed **twice, by independent code paths**, because a shared-parser error is
  invisible in a ratio: numerator and denominator move together and the ratio stays 1.0.
- **Parse round-trip** (relation MR-17): `xlsx → schema + facts → regenerated xlsx → re-induced
  facts` must be identical, including all 505 formula cells, all 54 validations with bounds, all 252
  merged ranges, all hidden-row flags, all protection flags, the hidden sheet and its 15
  vocabularies.

**Component decisions**

| Job | **Decision** | Alternative it beat |
|---|---|---|
| Schema authority | **raw OOXML via `lxml`** | **openpyxl** — §L0. **pandas `read_excel`** — collapses merged headers and returns *cached values*, i.e. exactly the numbers under test |
| Fast triage | **`python-calamine`** (MIT, 2 ms load) for sheet list, visibility, merged ranges | Only for triage — it has **no formula accessor at all** |
| Key identity | **label-anchored** `(sheet, header_path, row_label)`; coordinates resolved per version; unresolvable ⇒ explicit `UNRESOLVED` that blocks the predicate | **Coordinate-anchored keys** — a version bump becomes a rewrite instead of a re-resolution, and keys silently rebind. *Measured support:* under a naive `(sheet, label-above, label-left)` key, **1,749 of 1,953** cells are ambiguous (89.6%) because 100-row tables repeat the label pair; the **row ordinal disambiguates completely and is arithmetic, not a prediction** |
| Monetary representation | **integer micro-units** | **float** — see failure modes |
| Clause graph (**L1b**) | **Docling → Akoma Ntoso**, `eId` per clause, FRBR URI per instrument (`/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30`), `cobalt` for URI handling | **Free-text clause strings** — L3's "the clause it claims to implement" becomes unresolvable and L5 cannot cite. *Scope correction the design must carry:* the kill on "regulation-as-code" applies to **rules-as-code** (Catala/OpenFisca/Blawx — encoding logic). It does **not** apply to **legislation-as-XML** (Akoma Ntoso/Indigo — encoding structure and amendment chains), which is an OASIS standard with a live repository. Amendment-chain resolution — **76 of 82 = 92.7%** of amending circulars cite a resolvable target — has real prior art. Licence gate: `bluebell` is **GPL-3.0** (verified); Indigo and cobalt report `NOASSERTION` and their LICENSE files are **unopened** |

---

### L2a — STRUCTURAL EXTRACTION · *deterministic, no model*
### L2b — DOCUMENT EXTRACTION · *model-bearing, contingency only*

**The split is the correction.** The brief presented L2 as one of two model-bearing layers on the
critical path. It is not on the critical path at all for the artifact this product is about.

**L2a input**: `Filing` blob + `TemplateSchema` + `RegisterSnapshot`.
**L2a output**: `Fact{key, value, unit, provenance_anchor, warrant=DETERMINISTIC}`.
**L2a model?** **No.** For a native `.xlsx`, key-binding is a **lookup against L1**:
**0 of 3,755 unlocked cells are ambiguous under the address key**, and 154 (4.10%) under a
header-anchored key that generalises across row counts. MEASURED-HERE. Running a model to predict
something L1 already computes, then conformalising the model, then abstaining, would be an elaborate
way to reintroduce uncertainty the artifact does not contain — and would be a live instance of the
corpus's own §2.4 failure: *where a deterministic oracle exists, the oracle is the answer and no
model is warranted.*

**L2b applies to exactly four populations, and only these:**

| Population | Why the key is genuinely uncertain |
|---|---|
| **P1 cross-document binding** | A value in an attached PDF (valuation report, bank statement, auditor's letter) must bind to a template key. No geometry connects them. **This is the real target.** |
| **P2 template-version drift** | A filing submitted on an older template whose geometry does not match the current schema. **23.1% of circulars amend an earlier instrument**, so drift is the normal case |
| **P3 filer deviation** | Inserted rows, renamed labels, a table run past its 100-row allowance. **Share UNMEASURED** — needs real filings |
| **P4 free text** | Reg 119(3)(e) rationale, complaint narratives, AML-CFT explanations. There may be no key at all |

**L2b failure modes**
- *Shape is not truth.* Constrained decoding guarantees the key is **a** valid key. It says nothing
  about whether it is **the right** key.
- *The confidently-wrong regime.* Structured extraction into a fixed template is **precisely** the
  low-entropy regime in which entropy-based abstention was measured to fail: *"Many answers, both
  correct and hallucinated, collapse to SE = 0."* A naive confidence threshold is already known to
  be unsafe here.
- *Void guarantees.* Split conformal requires **exchangeability** between calibration and deployment
  data. A team-authored calibration set against real FME filings is a known distribution shift, so
  the coverage guarantee is **void, not degraded**. Quoting *"distribution-free, finite-sample
  coverage"* under a known-violated assumption is a stronger error than a loose FFR, because it
  borrows a theorem.
- *The wrong exchangeable unit.* Treating one filled workbook as 3,755 calibration points inflates
  every quoted guarantee: cells within a workbook share a filer, a period, a convention and — if the
  filer misunderstands a definition — a correlated error. **The exchangeable unit is the FILING.
  Report `n = F`, never `n = 3,755·F`.** Per-cell statements go through conformal **risk** control
  with a per-filing monotone loss.
- *The forced-abstention floor.* Where base error rate μ exceeds target risk α, any distribution-free
  method must abstain on at least `(μ − α)/(1 − α)` of items. At the architecture's own stated
  extraction failure (*"0% of the key"*, μ = 1.0) that is **100% abstention at every α**. **Conformal
  cannot rescue a broken extractor; it can only price one.**
- *Silent retry.* Retry-until-valid is the default ergonomic in three of the four high-level
  extraction libraries, and it **manufactures exactly the clean verdict this product refuses to
  give.** Either disable it or count it into the provenance.

**L2b self-check**
- **Hard guard, enforced twice.** The key is an `enum` over exactly L1's induced key set, so an
  off-schema key is **outside the reachable token space** at generation time; and it is
  deterministically rejected after generation. Both are kept — the post-hoc guard is what you can
  *prove* to an auditor.
- **Pre-flight gate before the L2b step even runs.** Measure key-binding accuracy μ on P1 first.
  **μ > 0.30 ⇒ do not build the conformal layer** — at α = 0.05 the forced-abstention floor already
  exceeds 26.3% and the honest product is *"cross-document binding is UNCHECKED."* This is
  pre-registerable and costs an afternoon.
- **`MODEL_EXTRACT` may never be the sole method on a `PASS`.** Encoded as a schema constraint in
  L7's `method` field, not as a coding convention.
- **Conformal test martingale, built before the conformal predictor.** It is the only component whose
  value does not depend on the calibration set being valid: it detects that exchangeability has
  lapsed and **withdraws the claim**, emitting `INDETERMINATE(calibration_not_exchangeable)`.

**Component decisions**

| Job | **Decision** | Alternative it beat |
|---|---|---|
| Native xlsx extraction | **L1 lookup, no model** | **Any document-AI parser** — 0 embedded images in 9/9 workbooks |
| PDF structure (regulation path only) | **Docling** | **Marker / MinerU / Surya** — Docling ships a typed, versioned `ProvenanceItem` we adopt field-for-field (§5.1), which removes a translation layer and a coordinate-origin guess |
| Shape guarantee | **outlines / XGrammar** (both Apache-2.0, actively pushed) | **Provider-native JSON mode** — **UNVERIFIED** what is *guaranteed* versus *best-effort*, and that difference is exactly the hard guard. *And the "format restriction costs reasoning" objection is contested, not settled* (EMNLP-2024 vs the dottxt replication showing GSM8K 0.77→0.78, Last Letter 0.73→0.77) **and is not on this system's critical path**: the constrained layer does no reasoning, and the reasoning layer's output is code, generated freely and adjudicated afterwards |
| Abstention | **split conformal with a RAPS score over L1's key set, Mondrian by four categories** (`NUMERIC_TABLE`, `SCALAR_HEADER`, `CATEGORICAL`, `FREE_TEXT`), via **crepes** (BSD-3) | **Entropy thresholding** — measured to fail in exactly our regime. **PASC (arXiv:2605.18812)** — **must not be cited**: its Table 1 reports a 9.9-point coverage spread across three nested-threshold methods at an *identical* mean set size, which its own construction forbids by ≥0.033; it shares a sole author with the impossibility-bound paper the design would also have leaned on; and the brief's claim that it "names financial documents as a target" is refuted (one mention, in the Introduction). The joint-coverage *idea* — conformalise the max-of-stages score — is one line from exchangeability and is reconstructed independently. The refereed anchor to lead with is **Mohri & Hashimoto, ICML 2024** |
| Runtime licence gate | **crepes (BSD-3) / MAPIE (BSD-3)** | **TorchCP** — LGPL-3.0, decision required before it becomes a core dependency |

---

### L3 — CANDIDATE PREDICATE PROPOSAL · *model-bearing, BUILD TIME ONLY*

**Renamed from "predicate synthesis" deliberately.** Every measured system in this literature that
works, works because a **rejector** exists: SMT solver → loop invariants at ~99.5%; JasperGold →
AssertLLM2; a unit-test suite → ClassInvGen 77% → 100%. Every one that fails, fails because the
rejector was absent or fake: TOGA's 96% held-out accuracy collapsing to **0.38% precision** and
**+0.3% marginal mutation kill on 51,385 mutants** under two independent re-evaluations; De Jure's
quality scored entirely by an LLM judging another LLM. **L4 is the rejector, and L4 is the product.
L3 proposes.**

**Input**
```
TemplateSchema        (L1 — passed into the prompt as an explicit I/O constraint)
ClauseGraph           (L1b — AKN clause units with eId + FRBR URI)
NativeFormulaGraph    (505 formula cells; 138 already express a checkable relation)
```

**Output**: `CandidatePredicate[]` — the envelope of §4.1, containing **CEL**, not Python.

**Model?** Yes — and it is the **only** model on the critical path of the system as a whole. It runs
**once per template version**, not per filing. Marginal model cost per filing on the workbook path is
**$0.00**; the entire annual inference bill across ~868 filings is under $200. **Do not pitch
inference-cost savings. Pitch the boundary.**

**Failure modes, each measured**
- *The degenerate operating point, documented inside the paper we reuse.* Selecting **all** generated
  candidates yields **100% coverage and 100% FFR** — "due to at least one assertion failing all
  tests." VERIFIED-AT-SOURCE.
- *Individually safe, jointly fatal.* **44.4%** of raw candidates individually blow a 25% FFR budget;
  and in two of nine pipelines, sets in which **every** member individually met the FFR constraint
  reached composite FFR of **88%** and **53%**. FFR is monotone non-decreasing under union. **A
  registry that admits checks one at a time, each individually acceptable, drifts silently to a
  flag-everything product.**
- *The modal output is the weakest output.* In the closest published analogue, the most prevalent
  atomic postcondition category is **Type Check at 47.4% prevalence and 0.14 bug-completeness on
  natural bugs**; the strongest is **Arithmetic Equality at 0.82** — a 6× gap. The model's default
  is the useless one.
- *The correctness prompt is not the completeness prompt.* Measured: the prompt maximising test-set
  correctness (accept@1 = 0.77) collapses bug-completeness to 26.2% of problems, and vice versa
  (p = 0.008, Cohen's d = 1.73). **A single prompt regime sits on one horn. Run two and let L4
  arbitrate.**
- ***Silent Scope Omission* — the failure L4's first three tests cannot see.** Frontier models ground
  the right clause spans (SpanFaith **0.77–0.79**, hallucination 0.21–0.29) and **wire the exception
  structure wrong**: Edge-F1 **0.215–0.246** over 2,290 provisions. Our instrument is full of
  defeaters — reg 39(1)'s half-yearly proviso for close-ended restricted schemes; the fund-of-funds
  proviso in regs 26(2)/38(2)/50(2); reg 51(1)'s open delegation. **A predicate implementing reg
  39(1) without the proviso passes a seeded-defect test, passes FFR on a clean corpus containing no
  close-ended restricted scheme, and is wrong in production.**
- *The criterion source is not authoritative.* The brief's novelty claim was *"statutory text plus
  the template's own native formulas — an **authoritative** criterion source rather than an inferred
  one."* **Downgrade to "available".** `'1. Introduction'!D17` is proof: a predicate mined from that
  formula would **pass a wrong filing and fail a right one**. The template's formulas are an
  available criterion source; L4 is what stands between the template's bugs and our verdict.
- *Domain fine-tunes are worse, not better.* Legal-domain models score **near-random on structure**
  (NodeSpan-F1 ≈ 0.18, Edge-F1 ≈ 0.04) against frontier models' 0.42–0.45 / 0.22–0.25. **Do not reach
  for a "legal LLM."**
- *The empirical surface moves without notice.* A documented instance: the same model alias moved a
  failure cell from **96.6% to 100%** between March and April 2026 with no version bump. **Frontier
  accuracy is a moving compliance boundary.**

**Self-check**
- **Verbatim-quote provenance guard.** Every candidate must emit an exact quote of the clause it
  implements; `source_text.find(quote)` must succeed or the candidate is **rejected at the
  boundary**. Zero extra model calls; kills clause hallucination structurally. Same shape as L2's key
  guard, and free.
- **`schema_keys` machine-checked against the CEL AST.** The harness walks the AST, extracts every
  field selection, and rejects the predicate if it reads a key it did not declare **or** declares a
  key it does not read. This is possible **only because the language has no variables and no loops** —
  and it is what makes settled-fraction a *derived* quantity rather than an estimate.
- **Three mandatory free baselines, run *before* the model**, because in this literature the free
  baseline beats the neural method more often than not:
  - **B0 — the native formulas.** The 138 checkable relations already in the template. Zero model.
  - **B1 — Daikon** (MIT-equivalent licence, 260★, pushed 8 Aug 2026, ships `scripts/convertcsv.pl`)
    over the clean corpus at `--conf_limit 0.99`. It will mine the SUM identities and cross-sheet
    carries for free — and it will also emit trivia (in one controlled study **27 of 40** correct
    Daikon invariants were merely "pointer is not null") and **7 spurious invariants that survived
    test validation**. Both outcomes are useful: the trivia is the degeneracy list, and the spurious
    ones are a measured demonstration, on our own corpus, that a check whose error rate is unknown
    must not be admitted.
  - **B2 — the degenerate arm**: "no cell is blank and no cell errors." The analogue of the
    `NoException` baseline that found **68.9%** of a published neural oracle's bugs at **twice** its
    precision.
  - **If L3 does not beat B0 ∪ B1 ∪ B2 on marginal kill at equal FFR, it has produced nothing**,
    however many predicates survive.

**Component decisions**

| Job | **Decision** | Alternative it beat |
|---|---|---|
| Selection algorithm | **Reimplement SPADE's ILP** — `minimize card(F') s.t. Coverage(F') ≥ α, FFR(F') ≤ τ`, with the two-sided interaction bound `max(FFR(S), FFR({f})) ≤ FFR(S ∪ {f}) ≤ FFR(S) + FFR({f})` and the subsumption DAG (topological sort with no incoming edges when no labelled examples exist — **which is our day-one mode**). ~40 lines of PuLP/CBC; measured runtimes 0.104–1.197 s on thousands of variables | **Depending on the SPADE repo** — `shreyashankar/spade-experiments`: **17★, 1 fork, NO LICENCE FIELD (all rights reserved), last push 2024-04-07**. Reuse the algorithm, not the repository |
| Output language | **CEL in a three-slot envelope** (§4.2) | **Python** — four independently decisive losses, in §4.2 |
| Criterion source | **statutory clause units (L1b) + the template's own 505-cell formula graph**, with I/O constraints in the prompt | **Prompt-version history** (SPADE's own source) — a regulation has no prompt-diff history. *And note the measured intervention:* in the one published study of generating executable models from statute, **I/O constraints are the dominant lever, worth +37–54 percentage points**. Feeding L1's induced schema into the prompt is therefore not a nicety; it is the single measured change that most improves this exact task |
| Framing | **the output is a number: `k` of `n` model-proposed checks survived a gate specified before the model ran** | **"L3 works"** — unfalsifiable. **`k = 0` is a publishable result**, and it is the first measurement anyone has of whether a frontier model can write a regulator-grade executable check |

**The pre-registration, restated, because the brief's version is underpowered in both directions.**
With `n = 10` and a "delete below 3" rule: if L3 truly works at p = 0.35 there is a **26.2% chance
the experiment deletes it**; if L3 is broken at p = 0.15 there is an **18.0% chance it is kept**; and
the 95% Wilson interval at `p̂ = 0.30, n = 10` is **[0.108, 0.603]** — the experiment cannot
distinguish "one in ten" from "three in five." **Replace with: n = 20, stratified before running into
Stratum A (arithmetically closed, expected ≈12) and Stratum B (judgment-bearing or
externally-dependent, expected ≈8); k = 10 candidates per obligation per prompt regime, two regimes;
report accept@1/@5/@10 and the union; retain L3 for Stratum A iff ≥ 6 of 12 survive AND L3 beats
B0∪B1∪B2 on marginal kill; delete for Stratum A at ≤ 3 of 12; 4–5 of 12 is "underpowered — report
the interval and either extend n or stop."** Power at n = 20, threshold ≥6: P(delete | p=0.15) =
**0.933**; P(delete | p=0.35) = **0.245**. Pre-register that a Stratum-B survivor is treated as a
**suspected false positive requiring manual adjudication before it counts** — a check that appears to
settle a judgment obligation is more likely degenerate than a breakthrough.

**And the sentence to write down before the result, because the standing bias will attack it:**
*"We should have sampled better obligations" is not an argument that the criterion was wrong — the
sampling rule is pre-registered. "The clean corpus was synthetic" is not such an argument — that
limitation is known in advance and applies symmetrically to the baselines. "Stratum B was always
going to fail" is not such an argument — that is why it is a separate stratum with its own
pre-registered expectation.*

---

### L4 — QUALIFICATION · *deterministic — the gate, and the contribution*

**Input**: `CandidatePredicate` + `TemplateSchema` + `CleanCorpus{provenance, n}` + `FaultModel{version}`.
**Output**: `AdmittedPredicate` (envelope with a **required** `qualification` block) **or** a typed
rejection recorded as counter-evidence. **A predicate without a qualification block does not load.**

**Model?** No.

#### T0 — Scope faithfulness *(new; NormBench is why)*

Every admitted predicate must carry (a) the exact character span of the clause it implements,
(b) an explicit enumeration of every proviso, exception and cross-reference in that span, and
(c) for each one, **either** an implementing branch in the expression **or** an emitted
`UNCHECKED(scope: <proviso text>)`. **A predicate that neither implements nor declares a proviso is
rejected.** This is a structural check on a pair, not a semantic one, so it is cheap; it is exactly
the "explicit exclusion guards" discipline; and it converts the design's most dangerous silent
failure into a coverage line — the product's own thesis applied to itself.

#### T1 — Seeded-defect adequacy *(renamed; the brief's name and tooling were a category error)*

`mutmut`, `PIT` and `Stryker` mutate **source code** to measure **test-suite adequacy**. None of them
will ever be pointed at an `.xlsx`. The correct mapping:

| Mutation testing | Here |
|---|---|
| program under test | the **filed artifact** |
| test suite | the **admitted predicate set** |
| mutant | a **corrupted filing** |
| mutation score | fraction of corrupted filings the predicate set rejects |

**The score, and it is strictly better than the formula it replaces:**

```
GENERATED     G  = mutants generated
UNOBSERVABLE  U  = mutants whose RECALCULATED value grid is identical to clean
OBSERVABLE    O  = G − U
UNREACHABLE   R  = observable mutants touching no field any admitted predicate reads
KILLED        K  = observable mutants for which at least one predicate returned FAIL

KILL RATE           KR  = K / O          ← the headline. NEVER K/G.
REACHABLE KILL RATE RKR = K / (O − R)
UNOBSERVABLE RATE   UR  = U / G          ← a property of the OPERATOR MIX, reported so it is auditable
```

`MS = |killed| / (|mutants| − |equivalent|)` requires `|equivalent|`, which is **undecidable in
general**. `K/O` needs no such term, because **our mutants are data**: "observable" is a *diff*,
measured by recalculation, whereas "equivalent" is a *theorem*. **This substitution is available only
because the artifact is data, and it is the single biggest practical improvement to the gate.**

Why the observability filter is not optional: **3,512 of 7,500 (46.8%)** of naively generated
spreadsheet mutants in the canonical study produced no observable change on the artifact they were
seeded into. Without the filter, roughly half the denominator is unkillable by anyone and every
predicate looks worse than it is, by a factor that varies with the operator mix.

**The fault model is versioned and published**, and it is 14 classes, each with a generator and an
observability condition: transposition · sign flip · off-by-one row shift · unit confusion · stale
carry-forward · duplicated row · dropped row · date off-by-period · currency mislabel · rounding
drift · **formula overwritten by a constant** · vocabulary drift · carry desynchronisation ·
vocabulary-gap exploitation. Two of them need care:
- **Formula-overwrite must be generated as a *pair*** — overwrite the formula with its current value
  **then perturb an input it depended on**. Generated as a single edit it is unobservable by
  construction and contributes only to `U`. A harness that gets this wrong reports a spuriously low
  kill rate.
- **Vocabulary-gap exploitation** (declare every scheme a `Special Situation Fund`) is invisible to
  the template's own formula. **A rule set mined from the template is blind by construction to a
  fault class the template creates.**

**Suppression is learned and logged, never silent.** Any operator/target combination we stop
generating is recorded with its reason in the harness manifest. *(Precedent: at production scale,
developer feedback reduced unproductive mutants from **85% to 11%**, and one operator — ABS — was
dropped outright for "predominantly creating unproductive mutants." What transfers is the structure,
not the numbers.)* **An undeclared suppression is a coverage lie.**

**And the ceiling, stated permanently:** `KR = 0.82` licenses exactly one sentence — *"rejects 82% of
the 340 defects I seeded, under fault model v3."* It does **not** license *"detects 82% of real
filing errors."* In code mutation testing the bridge is the coupling effect. **There is no coupling
study for financial filing data**, so the bridge does not exist and must not be walked across.

**One measured caution about what T1 is even measuring.** In the first real run — 2,826 sites × 7
operators = **19,782 mutants in 2.5 s (7,946 mutants/sec)** — every arithmetic operator killed at
**exactly 18.1%**, identical to the fraction of sites inside the field graph. That is correct and
expected for equality and sum identities: *any* perturbation of a cell an identity reads breaks it,
and no perturbation of a cell it does not read can. **For this predicate class, kill rate is a
measure of predicate *reach*, not predicate *quality*, and the product's vocabulary must say which.**

#### T2 — Non-degeneracy *(the peer-reviewed exhibit, and the empirical control arm)*

Two independent instruments, because one is a proof and the other is a measurement:

- **Proof arm — Z3 (MIT).** Trivially-true iff `¬P` is UNSAT over the field domains; always-flag iff
  `P` is UNSAT; redundancy iff `P₁ ∧ ¬P₂` is UNSAT (so P₂ adds no coverage). Z3 returns a **model** —
  a concrete counterexample workbook — which is directly usable as a seeded fault and goes into the
  library entry as evidence. CEL's arithmetic-comparison fragment translates to SMT-LIB almost
  one-to-one. **Where it stops:** host functions are uninterpreted, and Z3's string theory is
  decidable only for fragments — **treat `unknown` as UNCHECKED, never as "non-degenerate."**
- **Empirical arm — seed a 10% control sample into fields the predicate does *not* read** and count
  spurious firings. Without it, a flag-everything predicate scores a perfect kill rate. This is the
  gate's own answer to the F2 result, run rather than argued.
- **The random-flagger baseline is published prior art and should be cited rather than claimed.** The
  strongest no-oracle spreadsheet error detector reports **mean precision 64.1% / recall 62.1%** over
  70 benchmarks against a prior state of the art at **20.3% mean / 0.0% median precision**, and
  computes its adjusted precision against a **hypergeometric** random flagger (sampling without
  replacement, corrected for small sample size), plus an explicit "high precision when doing nothing"
  accounting — it flags no cells in 33 of 70 cases, **22 of which contain no formula error at all**.
  Adopt the discipline wholesale and cite OOPSLA 2018 for it.
- **A worked rejection that must be in the demo:** of the FME workbook's 24 bound predicates, 19 are
  a real `≥ 0`; but in the ALR workbook **five of six bounds are `−100000000000000000`**, asserting
  only "this is a number" over **1,428 cells**. T2 rejects those at admission and the settled
  fraction must not count them. **This is the first concrete demonstration that the gate does work
  rather than rubber-stamping.**

#### T3 — False-failure rate *(the test that was unrunnable, and the firewall that fixes it)*

**The attack, in its strongest form:** the same team authors the predicates **and** fills the clean
corpus. Both come from one mental model of what a correct filing looks like, so the corpus is
operationally *defined as* "filings that satisfy our predicates." **FFR measured on a self-authored
clean corpus has expected value zero regardless of predicate quality. It is not a weak measurement;
it carries no information at all**, and printing *"0.0% false failures across 340 clean filings"* is
worse than printing nothing, because it has the shape of evidence.

**The rule that makes an FFR admissible.** FFR is never a bare percentage. It is a quadruple rendered
inline, never in a tooltip, plus a two-sided interval:

```
FFR = (rate, corpus_id, corpus_provenance, n)  +  Wilson interval

corpus_provenance ∈ { SELF-AUTHORED, BLIND-FILLED, TEMPLATE-COMPUTED, REAL-PARTNER, PUBLIC }

SELF-AUTHORED renders as "—  uninformative".  Not a number.  The schema forbids one.
```

```python
def ffr_interval(fires, n, z=1.96):
    """Wilson score interval. n=4 and n=340 must not look alike."""
    if n == 0: return None
    p = fires / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

# 0 fires / 340 self-authored -> rendered as "—  uninformative"
# 0 fires / 340 blind-filled   -> [0.000, 0.011]   "at most 1.1%"
# 0 fires /   4 real           -> [0.000, 0.490]   "at most 49%"   <- honest, and it shows
```

**A real FFR from 4 real filings with an interval of [0, 0.49] is more honest and more useful than
0.0% from 340 self-authored ones, and the UI must make the second literally impossible to render.**

**The five corpus constructions, ranked, with what each can and cannot measure:**

| Rank | Construction | What it buys | Where it stops |
|---|---|---|---|
| **1** | **The blind-fill firewall.** Person A fills clean workbooks from the **template and regulation only**, having never seen the predicate set; Person B authors predicates having never seen A's workbooks; neither sees the other until measurement. A second model instance with a clean context window is an acceptable Person A **if and only if the fill prompt is auditable and predicate-free** | Restores information content. **The minimum bar below which no FFR may be printed anywhere in the product** | Still synthetic. Realism unaddressed |
| **2** | **The template's own native formulas as an externally-authored oracle.** Fill the input cells; let Excel/LibreOffice compute the derived cells; **all 505 formula cells carry cached values**, so a baseline exists. Any predicate that fires on a cell **IFSCA's own artifact computed** is a genuine false failure — the ground truth was authored by the regulator | Real ground truth, available today, no partner needed. Denominator: 138 checkable relations over 505 formula cells | Arithmetic predicates only. Says nothing about the 7, nothing about register resolution or vocabulary membership |
| **2b** | **The register as a real clean corpus for the identity-predicate class.** The live register is public, it is **229 live FMEs**, and it is **clean by definition** — every entity in it is validly registered. **MEASURED: the regex any competent engineer writes after five examples, `^IFSCA/FME/(I\|II\|III)/\d{4}-\d{2}/\d+$`, fires on 87 of 228 currently-registered FMEs — a 38.2% false-failure rate on real data, with a real denominator, available before the hackathon** | **The only non-synthetic FFR in the design.** Risk-2's caveat does not apply to this predicate class | One predicate class. Requires a register snapshot hash and a normalisation record |
| **3** | **Privacy-preserving FFR from a real FME partner** — runs client-side, the FME returns **only aggregate firing counts per predicate**, never data | The only construction yielding a genuinely real FFR on filings | `n` will be tiny (1 FME × 4 quarters). Fine **if reported as an interval**. Needs a partner the project does not have |
| **4** | **Differential testing between prescribed formats.** Where two of the nine workbooks ask for the same quantity in different shapes, **the pair is an oracle** with no corpus required | Real, cheap, on disk today; doubles as the transfer measurement | Only covers quantities that appear twice |

**Rejected as an FFR source, and recorded so nobody re-proposes it:** held-out fault seeding (it
measures detection, not false failure — a category error in the queue as written); cross-template
transfer (firing on a format a predicate was not written for is a *generalisation* failure);
**public spreadsheet corpora** (ENRON 15,770 CC BY 4.0; FUSE 249,376 **CC BY 4.0, not
"unencumbered"** — the deposit record says so even though the paper describes the underlying content
as unencumbered; EUSES ~4,498, licence NOT-FOUND). **None carries per-cell correctness labels**, and
a predicate like *"Principal Officer ≠ Compliance Officer"* cannot bind to a Common Crawl budget
spreadsheet at all — measuring FFR there returns 0% on a denominator of zero applicable rows, which
is not a low false-failure rate, it is a category error. *They are, however, exactly the right
instrument for a different and publishable question: on what fraction of real workbooks does our
extractor silently return a wrong count? Compute the schema three ways per workbook and report the
disagreement rate by construct. **Disagreement is a defect detected without an oracle.***

**The one real labelled signal nobody has mined:** IFSCA publishes **versioned** templates
(`ALR_V2_3`, `EDR_1_V2_3`, `IBU_Operations_Report_V2_3`, an FME format dated 02/01/2026, a CMI format
"Updated" 09/04/2026). **Diffing successive published versions of the same prescribed format is the
regulator stating what was wrong or under-specified before.** Nine workbooks with version strings are
on disk. That is a public, labelled corpus of regulator-confirmed template defects, and it costs an
afternoon.

**Required field, and it exists because a published 0% FPR turned out to be a tautology:**
`clean_corpus_independent_of_predicate : bool`. An FFR measured on a corpus generated to satisfy the
predicate is not an FFR. Two fields, not one: `ffr_constructed_corpus` and `ffr_independent_corpus`,
the second usually `null` and **visibly** so.

**Admission thresholds, pre-registered before the first run:** admit iff `K/O ≥ 0.80` on the fault
classes the predicate *claims* to cover, **AND** T2 returns non-degenerate (or an empirical
falsifying witness exists), **AND** `FFR ≤ 0.10` with `n` stated and provenance ≠ SELF-AUTHORED,
**AND** the marginal FFR conditioned on the already-admitted set is reported. *(If τ must be raised
to find any feasible set, **that raise is itself the result and must be reported, not absorbed** —
in one published instance a 10% budget had to be relaxed to 40% before a feasible assertion set
existed on one of two pipelines.)*

**Emitted on admission, and used at run time:** a **`kill_case`** (a mutant this predicate is known
to reject) and a **`pass_case`** (a clean artifact it is known to accept). These are the liveness
witnesses L6.5 replays.

**Self-check of the gate itself.** Report per fault class, never only in aggregate — a predicate that
kills 100% of sign flips and 0% of stale carry-forwards has a headline near 50% and two completely
different properties, so **the library entry carries the vector**. Report `R/O` (observable mutants
nothing reads) next to the settled-fraction curve: it is the *inverse* of that curve and is the
empirical shape of the unchecked region. And mutate **our own** code — the host functions, the L1
inducer (where the §4.4-class bugs live and where their failures are silent), and the AST profile
checker (if it is wrong, the settled fraction is wrong, and the settled fraction is the product).
`mutmut` (BSD-3-Clause, 3.7.0, 31 Jul 2026) is the right tool **there**, and only there.

---

### L5 — EXECUTION AND VERDICT · *deterministic*

**Input**: `AdmittedPredicate[]` (pinned by registry Merkle root) + `Facts` + `TemplateSchema`.
**Output**: one `Item` per (field × obligation) pair — the full schema is §5.1 — plus the computed
scope object.

**Model?** No. **Zero model calls, asserted in CI.**

**The evaluation contract, five rules, and rule 2 exists only because of a language hazard**

```
1.  Evaluate P.applicable
      error  -> UNCHECKED("source unreadable")          [NOT FAIL]
      false  -> UNCHECKED(P.reason_if_inapplicable)     [NOT PASS]
      true   -> continue

2.  PRE-FLIGHT: for every key k in P.schema_keys, test presence and type against the fact model
    BEFORE evaluating P.expr.  Any k absent or mistyped -> UNCHECKED("source unreadable: <k>").
      Why this is structural and not optional: CEL's specification states that for || and &&,
      "if that evaluation produces a runtime error, it will be ignored."  So `true || <error>`
      evaluates to TRUE.  Left unguarded, a predicate can return PASS while silently swallowing
      an operand that could not be evaluated at all — the exact defect this product exists to
      prevent, manufactured by the language.  Pre-flight makes the guard structural rather than
      dependent on how the predicate happened to be written.

3.  Evaluate P.expr under a cost budget and a wall-clock kill
      budget exceeded -> UNCHECKED("predicate exceeded evaluation budget")   [NEVER FAIL]
      runtime error   -> ERROR(predicate, exception)                          [NEVER FAIL, NEVER UNCHECKED]
      false           -> FAIL, then evaluate P.witness for the cell list
      true            -> PASS

4.  Provenance composes by WEAKEST INPUT: the verdict's warrant is min() over the warrants of
    every fact the AST read.  Because schema_keys is machine-checked against the AST, this set
    is EXACT and not an estimate.

5.  A predicate whose qualification block is absent, or whose `template` hash does not equal the
    pinned template hash for this filing, is NOT EVALUATED:
      UNCHECKED("predicate not yet synthesised" | "template version mismatch")
```

**Rule 3 is the whole product in four lines.** Everywhere a conventional validation framework
converts doubt into a failure or into silence, this converts it into a **counted, reasoned, reported**
non-settlement.

**Failure modes, enumerated as code because that is how they will arrive**

```python
# 1. VACUOUS PASS — the classic, and the most likely to ship
def check_all_percentages_sum_to_100(cells):
    return all(abs(sum(g) - 100) < 1e-9 for g in group(cells))
# group() returns [] because the selector missed a renamed sheet.  all([]) is True.
# Returns PASS. Nothing checked. Nothing logged.

# 2. EMPTY-SET ARITHMETIC
sum([]) == 0            # a "total" that matches because both sides are empty
len(rows) == declared   # 0 == 0 passes when extraction silently returned nothing

# 3. SELECTOR DRIFT — a regex over OOXML that cannot see <x14:dataValidation>.
#    Reports 3. Truth is 22. Confident, well-formed, wrong.

# 4. SCOPE TRUNCATION — L1 iterates visible sheets; 'Dropdown' is state="hidden".
#    Its fields never enter the DENOMINATOR. Settled fraction reads 100% of a scope that is short.

# 5. SHARED-DENOMINATOR ERROR — numerator and denominator from the same parser.
#    The parser is wrong. The ratio is still 1.0. Invisible by construction.

# 6. SWALLOWED EXCEPTION
try:    result = predicate(artifact)
except: result = UNCHECKED          # <- a crash indistinguishable from a philosophical limit
```

**Self-check**
- **`cells_bound` is reported per predicate, and binding to zero is an automatic `ERROR`, never a
  `PASS`.** This single rule kills modes 1, 2, 3 and 4.
- **`ERROR(predicate, exception)` is a distinct state**, and any `ERROR` makes the run `INVALID`.
  One word, large payoff — it separates *"the register was down"* (retry) from *"no predicate exists
  for this clause"* (write code), which have opposite remedies.
- **The scope denominator is computed twice by independent code paths** (mode 5).
- **Re-run determinism**: the entire pipeline run twice on identical bytes, in separate processes,
  with `PYTHONHASHSEED` varied, must produce a byte-identical verdict, an identical settled fraction
  and an identical multiset of reasons. **A verdict that is not reproducible is not a verdict**, and
  this is the one relation with zero tolerance.

**Component decisions**

| Job | **Decision** | Alternative it beat |
|---|---|---|
| Verdict model | **Build it.** Nothing in the ecosystem has a third value | **Great Expectations** — disqualifying, and it fails in the exact direction that kills us: `catch_exceptions=True` means an expectation that *could not be evaluated* returns `success = False`, **the same value it returns when it evaluated and the data was wrong.** For a product whose headline is a scope declaration, a framework that folds *could-not-check* into *failed* destroys the denominator, and it violates weakest-input provenance at the substrate level. Its documented result fields (`element_count`, `unexpected_count`, `unexpected_percent`, `missing_count`, `observed_value`, …) contain **no field for "not applicable", "out of scope" or "no oracle exists"** |
| Substrate for bulk column checks | **pandera** (MIT, 4.4k★) as a **host-function implementation only** | **pandera as the predicate language** — its failure-case frame is rich on failures and silent on non-evaluation |
| YAML rule syntax reference | **Read SodaCL for design ideas; link nothing** | **Soda Core** — **Elastic License 2.0**, verbatim: *"You may not provide the software to third parties as a hosted or managed service, where the service provides users with access to any substantial set of the features or functionality of the software."* Our product is a hosted service whose substantial functionality is data validation. **Unusable as an engine regardless of merit**, and the brief's §6.2 row listing it beside Apache-2.0 projects is a licence error |
| The revised line to replace the brief's §6.2 guidance | *"Do not rebuild the check **library**. You **must** build the **verdict model**, because none of them has one."* | *"Great Expectations / pandera / Soda Core / dbt tests / Deequ — L5 substrate — do not rebuild"* |
| Nearest existing third value, worth naming | **Pointblank**'s report carries an `EVAL` column flagging whether the step evaluated at all | The closest thing in the ecosystem — and still no reason vocabulary |

---

### L6 — DIFFERENTIAL AND INVARIANT PROBES · *deterministic — a LOOP over L0–L5, not a stage*

**The hardest technical finding in the review, and it deletes the brief's version of this layer.**
Metamorphic relations *"must involve multiple executions of the software"* — the technique requires a
**re-executable system under test**. The brief's five relations are *"reordering portfolio rows must
not change NAV; adding a zero-value holding must not change NAV; consolidating two identical
positions must not change NAV; scaling the reporting unit must scale every derived total;
currency round-trip within tolerance."* These are relations about **the filer's NAV computation,
which we cannot re-execute.** A filed workbook is a **record**, not a program. The NAV in it is a
number someone typed or pasted; reordering rows does not re-run a valuation engine, it reorders rows.

**And there is no NAV.** Full-XML grep across **all nine** workbooks: `NAV` **0 hits**;
`net asset` 4, all in the FME workbook and all aggregates in USD Million; `per unit` / `unit price` /
`units outstanding` **0**. Positive controls on the same interface, same file: `Scheme` 123,
`USD Million` 31, `Portfolio` 25, `Total Portfolio Value` 9, `valuation` 6, `Sixth Schedule` 1.
**All five relations are stated against a quantity the artifact class does not contain.**

**Taken apart individually, four of the five produce false alarms on a *correct* filing and the fifth
is vacuous:**

| # | Relation | Verdict | Why it false-alarms on a correct filing |
|---|---|---|---|
| 1 | Reorder portfolio rows | **REFUTED** | The rows are **schemes**, not holdings, and they are **formula-bound**: `'3. Portfolio'!B3 = '1. Introduction'!D54`. Permuting one table in isolation re-pairs each scheme's name with another scheme's amounts. **The checker would flag a defect it introduced itself.** *(The classic lot-ordering/FIFO exception, incidentally, does not bite here: guidance C111 puts values on cost basis in asset-class buckets with no disposals — saying so is more useful than repeating the generic caveat)* |
| 2 | Add a zero-value holding | **QUALIFIED** | Money is invariant; **counts are equivariant (+1)**. `Intro D17` and the three COUNTIF tallies all increment, as do investee-company, startup, infrastructure and investor counts. Asserted as full invariance it fires **every time it runs** |
| 3 | Consolidate two identical positions | **REFUTED** | There are no position-level rows to consolidate — positions arrive pre-consolidated into eleven asset-class buckets per scheme |
| 4 | Scale the reporting unit | **QUALIFIED** | The workbook is **not homogeneous**: counts, ratios, tenures, dates and categoricals are degree-0 and must not scale. Two-decimal rounding also breaks exact proportionality: for `O = SUM(C3:N3)` with n = 12, worst case is **0.06 USD Million = USD 60,000** on a correct filing. And Excel's `ROUND` is half-away-from-zero while Python's `round` is **banker's rounding** — `round(0.125, 2)` is `0.12` in Python and `0.13` in Excel. Finally, guidance **C109** forbids modifying table headings, and the unit is written into them |
| 5 | Currency round-trip | **DELETED, not repaired** | Guidance **C110**: conversion is at *"the same rate as applicable on the date of such transaction"* — per-transaction historical rates. Under a single rate, `x → x·r → x` is arithmetically true for any x whatsoever: it tests IEEE-754 and nothing about the filing. **It can never fail, so it can never be admitted by T2** — the gate would have caught it. Faithfully, it needs a transaction ledger that is not in the filing |

**Decision: SUT-A — the workbook-as-program.** *Alternative it beat:* **SUT-B, the filer's valuation
engine**, which would require the FME to run our transformations through their own system — a
completely different product, and a far more interesting one, but not this one. SUT-A is real and
re-executable: **all 505 formula cells carry cached computed values**, so a baseline exists.

**The honest claim about what this buys, stated plainly:** *this moves approximately **zero of the
seven** undecidable predicates.* It adds high-value boring checks and one check nothing else can
perform. **Say so.** What L6 buys is that **incoherence can no longer hide, and the boundary between
coherence and truth can be stated.** A filing can be perfectly coherent and completely false; an FME
that fabricates a consistent set of numbers passes all 25 relations.

**The replacement set: 25 relations, none requiring ground truth**, organised by what they need:

| Needs | Count | Examples |
|---|---:|---|
| **The filing alone** | **15** | four-way partition of funds raised; complaint/appeal flow identities; debt-grade cross-table identity; typed λ-scaling; zero-scaling; sign flip on declared-signed fields; definitional bounds; half-yearly gating |
| **The filing + the pinned blank template** | **4** | source-consistent permutation; `AGGREGATE` multiset re-ordering; parse round-trip; **formula-override differential** |
| **Two consecutive filings** | **3** | opening balance = prior closing; cumulative monotonicity; static-field stability |
| **Multiple instances of one filing** | **1** | multi-instance coherence |
| **Checker self-tests** (never reported to the filer) | **2** | re-run determinism; scale round-trip |

**The five that carry the layer:**

1. **Formula-override differential.** For every cell the **blank template** declares to be a formula,
   compare the value in the filed workbook against the value obtained by evaluating the template's
   formula over the filed inputs. **This is the only thing in the entire design that detects a filer
   overwriting a formula cell with a literal** — the single most likely real defect in a protected
   workbook, and one that leaves the filing *perfectly self-consistent* because the inconsistency was
   deleted along with the formula. Sheet protection is an **application-level flag, not encryption**:
   nine sheets carry SHA-512 `sheetProtection` hashes and stripping them is a zip edit. **Assume the
   filed artifact is fully mutable, and build no predicate whose validity depends on a range being
   protected.** Needs no corpus; its oracle is the published blank. **This should be predicate #1.**
2. **The four-way partition of funds raised.** For each scheme and for the FME total, the same
   quantity is computable by **four independent routes** — by investor category (`'4. Investors'!AA`,
   12 summands), by country (Table 4.3), by accreditation status (Table 4.2), and the Summary carry —
   with count duals. **The workbook enforces agreement between none of them: Tables 4.2 and 4.3
   contain zero formulas.** With four routes there are six pairs, and *the pattern of disagreement
   localises the fault*. Tolerance: `τ(12) = 0.06` USD Million on amounts, **exact on counts — a
   person is not a rounded quantity, and slack there is how a missing investor hides.** Guard against
   the set-equality trap: assert **value** equality, not merely that the same schemes appear.
3. **Half-yearly gating of the AML-CFT sheet.** Sheet 7 states on its face: *"To be reported
   half-yearly, i.e., for the periods ending on September 30 and March 31 of every year."* **A
   checker that demands sheet 7 every quarter is wrong on exactly half the filings — a 50%
   false-positive rate by construction, on ~868 filings a year — and no formula in the workbook
   encodes it (sheet 7 has zero formulas).** Stated as a rule it is a special case someone must
   remember; stated as a relation it is mechanically testable and also catches the converse error.
4. **The scheme split.** Take a scheme with monetary vector **v** and place it across two slots as
   **a** + **b** = **v** with the same authorisation number. Money aggregates stay invariant; the
   scheme count rises by one; `D17` now exceeds the count of **distinct** authorisation numbers. **The
   disagreement between two relations that should agree is the detector** — splitting or duplicating
   a scheme to move money between reporting buckets is caught with no oracle, no register and no
   knowledge of what the right numbers were.
5. **The `IF`-branch coherence check.** `'3. Portfolio'!L(s) = IF(Summary D(s)="Retail Scheme",
   Summary W(s), Summary N(s))`. If a filer has populated **both** the retail and non-retail columns
   for one scheme, **the `IF` silently reads one branch and never looks at the other.** This is a
   defect the workbook's own formula is *structurally incapable* of surfacing — a clean demonstration
   of what relation-checking adds over formula-checking.

**The tolerance model, and it is not a constant.** `τ(n) = n × 0.005` USD Million, from guidance
C111 (values to two decimals, USD Million, so the quantum is USD 10,000 and per-cell rounding error
is at most USD 5,000). **A fixed epsilon is wrong and is the single most likely source of spurious
L6 failures.** Arithmetic in `Decimal` with `ROUND_HALF_UP`; **never compare floats with `==`**;
**counts get zero tolerance.**

**Two annotations do all the remaining work, and every false alarm above traces to a missing one:**
a **degree map** over every field, and a **necessary / expected flag**. A **necessary** relation is
entailed by the template's own formula graph or by the arithmetic of a partition — violating it is a
**FAIL**. An **expected** relation is a convention that admits lawful exceptions — violating it emits
**ADVISORY**, never FAIL. The worked case: cumulative columns `K, M, O, P, Q, S` are non-decreasing
(**necessary**), but column **J (cumulative commitments) is not**, because Summary note 4 says it
*"includes gross commitment raised since inception **deducting such commitments which have been
exited due to forefeiture / exit / reduction in commitment**."* **A relation asserting "all
cumulative columns are non-decreasing" false-alarms on column J on a correct filing.**

**Failure modes of the layer itself**
- *Relations are not self-validating.* A violated relation means *the artifact is wrong* **or** *our
  relation is wrong*. **Every relation passes L4 like any other predicate.** The brief's *"Every
  violated relation is a defect found without an oracle"* is false as stated.
- *Null tests inflate the settled fraction.* A relation that cannot fail scores zero on T1 and is
  rejected automatically — **the gate would have caught the currency round-trip on its own.**
- *Degenerate satisfaction.* An all-zero filing satisfies every partition and flow identity
  trivially. **Every partition relation needs a non-degeneracy precondition** — at least two routes
  non-zero, or the verdict is `UNCHECKED(no data)`, never PASS. Without it an empty filing scores
  100%, which is the F2 failure arriving through the L6 door.
- *Cross-basis contamination.* Portfolio note 7 puts Tables 3.1/3.2 on a **direct-investment** basis;
  the PMS note puts Table 5.6 on a **look-through** basis. **Any relation adding a 3.x quantity to a
  5.6 quantity is invalid by the artifact's own notes.**
- *Jurisdictional parameterisation.* CSSF point 38 aggregates successive sub-threshold errors; FCA
  COLL 6.3.6G §5(3) says consider each price separately. **Every relation carries the instrument that
  authorises it, and the report states which one it applied.**

**Self-check**: a relation must have failed at least once on a deliberately broken artifact before
admission; relations are re-qualified when the template changes; and the evaluator built to run them
is *itself* the second independent implementation whose disagreement with IFSCA's formulas is the
detector.

**Component decisions**

| Job | **Decision** | Alternative it beat |
|---|---|---|
| Execution vehicle | **Hypothesis** (MPL-2.0): `@invariant` for necessary relations, assertions inside `@rule` for expected ones — **the FAIL/ADVISORY split implemented by the library rather than by us**; `Bundle` for scheme slots; shrinking so a failure reports *"the smallest edit that breaks partition identity is setting cell 4.3!C60"* rather than a diff of two workbooks; `@example` to pin every real defect as a permanent regression | **A bespoke loop** — loses shrinking and regression pinning. **Where it stops, unchanged from the brief: Hypothesis generates *inputs*, never *properties*. Relations must be authored** |
| Search budget | **`max_examples = 50`** | **Hypothesis's default 100, or fuzzer-scale millions** — measured: **55%** of mutations are found with a **single** input and **76%** within the first 20. The artifact's input space is small and fixed (ten scheme slots, closed vocabularies). **A handful of well-chosen transformed workbooks captures roughly three-quarters of what unbounded random generation would**, and that is a citation rather than a hope |
| Relation generation | **Read them off the artifact's own formula graph and sheet notes. Use no model.** | **Ask a model** — measured: LLM-generated metamorphic relations score high on correctness, clarity and computational feasibility and **"markedly low"** on novelty; they recapitulate the textbook classes. **Those textbook classes are exactly the brief's five relations, and §L6 above is what they cost.** Every relation worth having here came from a note about forfeiture, a note about look-through, a sentence about half-yearly reporting, a COUNTIF that misses two dropdown values, and an `IF` that hides a double-populated branch. **No model produces those, and the literature says so.** *(L3 mines statute with a model; L6 must not share L3's generation strategy)* |
| Relation authoring method | **Category–choice decomposition** over the seven categories the workbook actually branches on (scheme type ×11, open/close ×2, FME category ×3, quarter ×4, PMS provided ×2, third-party FM ×3, scheme count) | **Mining an existing test suite** — there is no test suite for an IFSCA filing; the mining substrate does not exist. **Substitute the template's own formula graph, mirroring the L3 substitution** |
| Formula evaluator | **Reimplement the eight-function vocabulary** — `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)` — in `Decimal`, over a topological sort of 505 cells | **`formulas`** (EUPL 1.1+, copyleft, 90.1% function coverage) and **`pycel`** (GPL-3.0, and its dependency graph is **lazy** — 33 nodes after three evaluations, not 4,627). Two reasons the reimplementation wins: the licences are a real gate on a hosted product, and **the reimplementation *is* the differential arm** — a second independent implementation that can carry its own kill rate. *Carry the caution:* even LibreOffice reproduces Excel's arithmetic exactly on only ~92% of real workbooks by one vendor-authored measurement (**2★ repo, all 19 commits in a single three-hour session, self-graded, vendor tops its own table — treat the ranking as promotional and the shape as a warning**). Any predicate comparing a recomputed total to a cached value inherits an engine-disagreement floor, and it must be **measured independently before it is quoted**, not imported |
| Naming | **"differential and invariant probes"** | **"metamorphic testing"** — the technique requires a re-executable SUT; our cross-period and cross-format checks are **differential testing**. A correct small claim beats a large unbuildable one |

---

### L6.5 — SELF-CHECK AND RESIDUE · *deterministic — NEW LAYER, and the most important addition*

**Why it exists.** The pitch's strongest asset is that deterministic programs produce *"clean,
confident, well-formed output that was wrong, with nothing to distinguish it from a correct
answer."* **Our system is a deterministic program that outputs "no failures."** The argument applies
to it with full force, and **nothing in the eight layers would catch it.** L4 qualifies predicates
**at admission**, against the corpus of that moment; nothing re-checks, **at run time, on *this*
artifact**, that the predicates still bind to anything. §1.5 is the proof that the failure recurs:
five instances, three mechanisms, all under-counting in the same direction.

**Input**: the filing, the admitted predicate set with its stored witnesses, the L5 result.
**Output**: `{ selfcheck_passed : int, dead_predicates : [id], residue : ResidueSet, state : VALID | INVALID }`.

**Model?** No.

```python
def verdict_with_self_check(filing, predicates):
    result = run_all(filing, predicates)

    canaries = []
    for p in predicates:
        # instantiate THIS predicate's stored kill-witness against THIS filing's cells
        mutant = p.kill_witness.apply(filing)
        if not run_all(mutant, predicates).rejected_by(p):
            canaries.append(p.id)

    if canaries:
        return Report(state="INVALID",
                      reason="self-check failed; these predicates did not fire on a fault "
                             "they are known to detect, in this artifact",
                      dead_predicates=canaries)
    return result.with_selfcheck(passed=len(predicates))
```

**Why this is the answer and not a nicety:**
- **It runs on the artifact under test, not on a training corpus** — so it catches parser drift,
  selector misses, renamed sheets, hidden-sheet truncation, encoding changes and empty-set vacuity
  **for this file**.
- **The output is a third state: `INVALID`** — not "clean", not "unchecked", but *"this system could
  not demonstrate it was working here."* That state does not exist anywhere else in the design and it
  is the single most important addition.
- **It would have caught every one of the six L5 failure modes**, and both of the original two
  documented false negatives.
- **Cost:** N predicates × one pipeline run over a 6,757-cell workbook. Milliseconds to seconds
  against a 30 ms baseline. **There is no reason not to.**

> **The best line in the pitch: *every report carries proof that the checker was alive when it ran —
> on your document, not on a benchmark.***

**The residue set — the product's central measurement**

```
1. Take the filing under test, F.
2. Generate mutants of F under a declared, versioned fault model.
3. Adjudicate each mutant: INNOCUOUS (still correct) / WRONG (materially false).
4. Run the full admitted predicate set + L6 on every WRONG mutant.
5. RESIDUE := { WRONG mutants that no predicate rejects }
6. Report |RESIDUE| and, for each survivor, the class of falsehood it represents.
```

**The three mutant classes, and the third one is the product.** Code mutation testing has one
nuisance class (equivalent mutants). Data fault seeding has two, and they point in opposite
directions:

- **INNOCUOUS** — a data edit leaving the filing *correct*: reordering rows where order carries no
  meaning, reformatting `1000000` → `1,000,000`, changing a date's display format, rewording a
  free-text rationale. Like equivalent mutants, these cannot be killed and **must leave the
  denominator**, or the score is understated.
- **UNDETECTABLE-IN-PRINCIPLE** — a mutation that makes the filing **factually wrong** while leaving
  it **internally perfect.** Change the reported figure and propagate it through all 223 carries and
  all 135 SUM relations: every predicate passes, and the filing is wrong. **In code mutation testing,
  a mutant that changes behaviour is in principle killable by *some* test. Here, a mutant can change
  the *truth* of the artifact and be provably unkillable by any predicate over the artifact alone.**

> **That third class is not a nuisance term in a denominator. It is the measured boundary that the
> problem statement says exists nowhere.**

**Properties that make the residue the centre of the design, and each is why it replaces the
fraction:**
- **It cannot be inflated by boring checks.** Adding 505 recompute predicates does not shrink it,
  because the residue is populated by falsehoods consistent with every arithmetic relation in the
  file. This is the exact property `71%` lacks — and the reason the fraction had to go, since the
  same enumeration that produces 17/24 = 71% produces **555/562 = 98.8%** in an afternoon.
- **It converts a hand-classification into a measurement.** 17/24 was one person deciding what is
  decidable. The residue is produced adversarially and **a third party can re-run it on the same file
  and get the same answer.**
- **It is the honest content of the Unchecked panel.** Today that panel lists *reasons*. It should
  list *demonstrated survivors*: **"a coordinated 0.05% misstatement survives all 555 checks — here
  it is."**
- **It is the publishable result**, and the one the problem statement says is missing.

**Self-check of the self-check:** step 3 (INNOCUOUS vs WRONG) is the only judgment in the loop. It is
**one-time per fault-model version**, it is exactly the kind of judgment a domain expert renders
quickly, and **it is auditable by a reviewer** because the adjudication is recorded per mutant with
its content hash.

**Named prior art:** the nearest is SRE **synthetic monitoring / canaries** and hardware
**built-in self-test**, not anything in the testing literature. A formal-methods citation for
vacuity detection in model checking is **UNVERIFIED** and must not be asserted. **The mechanism needs
no citation: it is two extra executions per predicate, and it converts a silent failure into a loud
one.**

---

### L7 — ATTESTATION · *deterministic*

**Input**: the L5 scope object + L6 relation results + L6.5 self-check and residue + every content
hash + the registry Merkle root.
**Output**: a signed DSSE envelope (§5.2), a self-contained HTML report, a declared-lossy OSCAL
projection, and an evidence crate.

**Model?** No.

**Failure modes**
- *A `result` field.* If the schema has one, a downstream consumer will render a pass, a screenshot
  will carry it, and every copy commitment in the product is void. **Schema-level prohibition beats
  copy discipline, because it survives the screenshot, the API integration and the intern.**
- *A fraction without its counts.* One live system demonstrates the failure: its aggregate score
  silently drops inconclusive checks, so a repository with **8 of 19 checks inconclusive and one with
  0 of 19 print the same number.** That failure mode is exactly what this product must not reproduce,
  and it is why the residue counts travel *with* the fraction or the fraction is not emitted.
- *Attesting over the wrong bytes.* If the pipeline ever re-serialises the artifact with openpyxl,
  the content hash is a hash of something that is not the filing (98.2% of it having been deleted).
- *An unassigned liability surface.* If the vendor signs, the vendor is attesting to a regulated
  filing. If the filer signs, it is self-attestation. **If an FME shows an inspector a signed
  attestation over a filing that was wrong, the signature is the first exhibit.** Decided in §5.2.
- *Disclosure by transparency log.* Keyless signing binds a workload/human identity into a public
  certificate published permanently. For filings by named FMEs, **the fact and timing of a named
  entity running a pre-submission compliance check becomes world-readable and correlatable.**
- *A comparable-looking fraction that is not comparable.* The denominator varies between filings
  because out-of-scope determinations are filing-specific. XCCDF wrote this warning into its own
  normative text in 2012: *"scores between different target systems may not be directly comparable
  because the maximum score can vary."* It ships in the payload as `denominatorWarning`.

**Self-check**
- **Closure is an enforced invariant, not a discipline.**
  `outOfScope + settled.total + indeterminate + notRun + noPredicate == pairsTotal`, checked at
  report-generation time. **Any pair that lands in no bucket aborts the report.** This is the
  `DISALLOW *` move: the in-toto specification itself warns that its default open-world behaviour
  *"could allow artifacts to sneak into the step or inspection **undetected**."* Our L1-induced
  schema **is** a signed layout — an authoritative, complete enumeration of the universe, derived
  deterministically from the regulator's own published artifact — which is precisely why the closure
  is possible for us and is not possible for XCCDF, OSCAL or ISRS 4400.
- **The no-green-tick commitment is a build gate.** A design commitment that is not tested is a
  preference:
  ```bash
  # ci/no-green-tick.sh — fails the build
  BANNED='✓|✔|✅|🟢|all clear|all-clear|no issues|looks good|verified clean|compliant|passed all|fully checked'
  if grep -rniE "$BANNED" src/ templates/ locales/ ; then
    echo "FAIL: banned all-clear language or glyph in a user-facing surface"; exit 1
  fi
  ```
- **`verify <report>`** re-derives from the embedded run manifest
  (`{template_sha256, filing_sha256, register_snapshot_sha256, registry_root, fault_model_version,
  code_git_sha, python_version, lxml_version, tool_versions}`) and asserts a **byte-identical**
  report. That single command is the strongest thing to hand a supervisor, and it is the honest
  observability story: the question is not *"what was the p99 latency"* but *"can I get this same
  answer again."*
- **`NONE ≠ NOASSERTION ≠ absent`**, enforced by the JSON Schema: `[]` means *we determined there are
  none*; `null` means *we make no claim*; **field omitted is a schema violation the validator
  rejects.**

**Component decisions**

| Job | **Decision** | Alternative it beat |
|---|---|---|
| Envelope | **DSSE + in-toto Statement v1**, `subject[]` carrying **both** the filing hash and the template hash | **JSF (CycloneDX)** or bare JWS — in-toto/DSSE is Apache-2.0, is what the whole attestation ecosystem already speaks, and `subject[]` naturally carries the two hashes we must bind. **A verdict against template v3 is meaningless if the entity filed on v4** |
| Signing | **Detached key signing over the report JSON** (available in `compliance-trestle`, Apache-2.0, v5.0.0, actively released) | **Sigstore keyless on the public-good instance** — the transparency log is public and permanent; the disclosure surface above is the reason. If a log is wanted, use a **private transparency-log instance operated by the supervisor**, whose audience is already the regulator, and publish only salted hashes of filing identifiers |
| Normative representation | **Our own schema (§5.1)** | **OSCAL as primary** — its `finding-target.status.state` is a **closed two-value enum** `{satisfied, not-satisfied}`, which is precisely the one field this product exists to add a third value to. Encoding our third state in OSCAL's **open `reason` token** gets us OSCAL's syntax without OSCAL's validation — a validator would accept `{"state":"satisfied","reason":"actually-we-never-checked"}`. **That is the worst of both** |
| Interop | **An OSCAL Assessment Results projection + an OSCAL POA&M, both flagged LOSSY in the file itself** | **No export** — the projection is what a supervisor's GRC stack already ingests, and it is free via `compliance-trestle`'s pydantic models. **The loss is stated in a mandatory `metadata.prop` naming the URI of the normative artifact — in the file, not in a README** |
| Report artifact | **A single self-contained HTML file** (inline CSS/JS, no external requests) | **Any SPA framework** — four grounds a framework cannot match: it opens from `file://` with the venue wifi down; it is phone-safe with no build target; **it is emailable, which is how a compliance officer actually shares a report**; and **it is the attestation artifact — L7 signs a hash of *something*, and a file has a hash while a single-page app does not** |
| Storage | **SQLite + a directory of `sha256`-named blobs** | **Postgres** — wins on a concurrency this project does not have, costs a service to run and back up, and **cannot be content-addressed. A file can be hashed and named in the run manifest; a cluster cannot** |
| Registry version | **A Merkle root over the sorted `code_sha256` of admitted predicates** | **A monotonic integer** — a root *pins the exact check set*, and a report naming one root is re-derivable |

## 3.4 Four invariants that hold across every layer

1. **Zero model calls in the verdict path**, enforced as a test that asserts the process handling a
   filing opens no socket to a model endpoint. Build-time model work is batched, offline,
   human-reviewed and amortised over 868 filings a year and every future filing.
2. **Every model output crosses a deterministic boundary before it can affect a verdict**, and
   `MODEL_EXTRACT` may never be the sole method on a `PASS` — a **schema constraint**, not a coding
   convention.
3. **Provenance composes by weakest input** under `DETERMINISTIC > MODEL_EXTRACTED > DERIVED`, with
   `retrieved_at = max(inputs)`: a verdict is never fresher than its stalest input and never stronger
   than its weakest. Exact, not estimated, because `schema_keys` is machine-checked against the AST.
4. **Every denominator is computed twice, by independent code paths**, and every absence is preceded
   by a declared positive control.

---

# PART 4 — THE PREDICATE MODEL

## 4.1 What a predicate IS

**A predicate is not an expression. It is a small, signed, content-addressed record that *contains*
expressions.** The envelope is what makes non-settlement a first-class evaluation outcome rather than
an exception, and it is where all qualification metadata lives.

```yaml
# predicate/P-0041.yaml — content-addressed by sha256 of the canonical serialisation
id:          P-0041
version:     3
kind:        arithmetic | membership | bound | identity | temporal | external | relation

# ── BINDING ────────────────────────────────────────────────────────────────────
template:    sha256:9f3c…                       # the PINNED blank template this predicate binds to
schema_keys: ["intro.tbl15.row[*].scheme_type", "vocab.scheme_type"]
             # DECLARED, and machine-checked against the CEL AST at admission.
             # Reads a key it did not declare  -> REJECTED.
             # Declares a key it does not read -> REJECTED.

# ── WHAT IT CLAIMS TO IMPLEMENT ────────────────────────────────────────────────
clause:
  instrument:   "IFSCA (Fund Management) Regulations, 2025 (as amended to 30 Jan 2026)"
  frbr_uri:     "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30"
  eId:          "sch_3__part_A__point_g"
  locator:      "Reporting Format FME v02012026, Table 1.5 col G"
  quote:        "Type of Scheme"        # VERBATIM. source.find(quote) must succeed or REJECT.
  provisos:                             # T0 — every proviso enumerated, each disposed of
    - text:     "Provided that this requirement shall not apply in case of a fund of funds scheme…"
      disposal: DECLARED                # IMPLEMENTED | DECLARED
      emits:    UNCHECKED(not_run.input_unavailable.counterparty)
rationale:   "Every declared scheme type must be a term the published template offers."

# ── THE THREE SLOTS ────────────────────────────────────────────────────────────
applicable: >                           # CEL -> bool.  false => UNCHECKED(reason_if_inapplicable)
  size(filing.intro.tbl15.rows) > 0
expr: >                                 # CEL -> bool.  true => PASS, false => FAIL
  filing.intro.tbl15.rows.all(r,
    r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)
witness: >                              # CEL -> list.  what to show the user on FAIL
  filing.intro.tbl15.rows.filter(r,
    r.scheme_type != "" && !(r.scheme_type in template.vocab.scheme_type)).map(r, r.__cell__)

reason_if_inapplicable: "predicate not applicable: no schemes declared"

# ── EXTERNAL DEPENDENCIES, DECLARED SO A SCHEMA CHANGE DEGRADES LOUDLY ─────────
external_deps:
  - endpoint:   "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet"
    field:      "RegistrationNumber"
    snapshot:   sha256:…                # content-addressed at run time; the register is mutable
    on_missing: UNCHECKED(not_run.input_unavailable.register)

# ── WRITTEN BY L4. NOT HAND-EDITABLE. ABSENT ⇒ THE PREDICATE DOES NOT LOAD. ────
qualification:
  admitted_on:  "2026-08-14"
  admitted_by:  "…"
  scope_faithfulness:
    provisos_total: 1
    provisos_implemented: 0
    provisos_declared: 1                       # 1 + 0 must equal provisos_total or REJECT
  seeded_defect_adequacy:
    fault_model:  "v3"
    generated:    412
    unobservable: 187                          # measured BY RECALCULATION, never estimated
    observable:   225
    unreachable:  31
    killed:       196
    kill_rate:    0.871                        # K/O.  NEVER K/G.
    by_fault_class: {F1: 1.00, F2: 1.00, F5: 0.12, F11: 0.94, …}   # the VECTOR, not the scalar
    unobservable_rate: 0.454                   # a property of the operator mix; reported so it is auditable
  degeneracy:
    method:       "z3"
    verdict:      "non-degenerate"
    witness:      "w/P-0041-neg.json"          # Z3's model — a directly usable seeded fault
    control_arm:  {seeded_outside_read_set: 41, spurious_fires: 0}
    random_flagger_adjusted_precision: 0.92
  ffr:
    fired:        2
    n:            96
    rate:         0.021
    ci95:         [0.006, 0.074]               # Wilson. NEVER a bare point estimate.
    corpus_id:    "blind-fill-v2"
    corpus_provenance: "BLIND-FILLED"          # SELF-AUTHORED renders as "— uninformative"
    clean_corpus_independent_of_predicate: true
    ffr_held_out_slice: {rate: 0.033, n: 30, slice: "close-ended restricted schemes"}
  interaction:
    conditioned_on: ["P-0007"]
    marginal_ffr:   0.010                      # SPADE bound: max(FFR(S),FFR(f)) ≤ FFR(S∪f) ≤ FFR(S)+FFR(f)

# ── LIVENESS WITNESSES — replayed by L6.5 on EVERY run, against THIS filing ────
liveness_witness:
  kill_case: "mutants/scheme_type_out_of_vocab.xlsx"     # it is known to REJECT this
  pass_case: "clean/blind_fill_017.xlsx"                 # it is known to ACCEPT this

# ── STATE MACHINE ──────────────────────────────────────────────────────────────
qualified_against:
  template_sha256:           "9f3c…"
  template_label:            "FME_02012026"
  regulation_version:        "2026-01-30"
  circular_corpus_snapshot:  "2026-08-10T00:00Z"
  circulars_unreadable:      10                # 10 of 399 are scanned images — a permanent declared gap
  model_id:                  "…"               # null for hand-authored
  prompt_sha256:             "…"               # null for hand-authored
state:        ACTIVE          # ACTIVE | PROVISIONAL | QUARANTINED | WITHDRAWN
severity:     BLOCKING        # BLOCKING | ADVISORY — SET BY THE MEASURED FFR, not by taste
withdrawn_on: null
withdrawn_reason: null        # {rule_amended, ffr_exceeded_threshold, superseded_by, source_schema_changed}
```

**Five properties of this object, none of which any existing framework has:**

1. **Non-settlement is produced by evaluation, not by exception.** `applicable` is a *predicate about
   applicability*, evaluated first, with its own semantics. A predicate that does not apply is
   neither a failure nor a pass — it is removed from the settled denominator **with a stated reason**.
2. **`schema_keys` is declared and then machine-checked.** This is what makes the settled fraction a
   *derived* quantity, and it is possible **only because the language has no variables and no loops**.
3. **`qualification` is required by schema.** *"A check whose error rate is unknown is not admitted"*
   becomes a **schema constraint**, not a discipline.
4. **`external_deps` is explicit**, with the field and the endpoint, so that a schema change at the
   source degrades the predicate to `UNCHECKED` **loudly instead of silently**. This is the direct
   architectural answer to the register failure in §1.5.
5. **`severity` is set by the measured FFR, not by an author's opinion.** This is the EBA's
   decade-old warnings-first convention with the measurement put back in — and it is defensible to a
   supervisor on day one because they already run the unmeasured version.

## 4.2 The language

**Decision: CEL (Common Expression Language), evaluated by a Python host process over a flat typed
fact table, inside the three-slot envelope above.**

**Why, in the two sentences the spec turns on.** The language definition states, verbatim, that CEL
programs are **"terminating: CEL programs cannot loop forever"** and **"side-effect-free: a CEL
program only computes an output from its inputs."** It has no user-defined functions and no loops;
`for`, `while`, `function`, `loop`, `break` and `continue` are reserved *and unavailable*. Six macros
exist (`has`, `all`, `exists`, `exists_one`, `map`, `filter`), and the spec names them as the only
avenue for exponential behaviour.

**The requirement matrix that decided it, scored against the 17 decidable predicates:**

| Requirement | **CEL** | Python + pandera/GX | Rego | Z3 | Drools / ZEN | Starlark | JSONLogic |
|---|---|---|---|---|---|---|---|
| Guaranteed to terminate on model-written input | **yes, by language design** | no | yes | decidable fragments only | engine-dependent | yes | yes |
| Safe to evaluate model-generated text without a container | **yes** | **no** | yes | no | no | yes | yes |
| One auditable line a lawyer can read | **yes** | no (a function body) | partly | no | no (a DRL/graph) | no (multi-line, stateful) | no (a JSON tree) |
| Serialisable, content-addressable, diffable | **yes — it is a string** | no | yes | yes | yes | partly | yes |
| Mechanically mutable (perturb the AST) | **yes, ~20-production grammar** | yes, huge grammar | yes | yes | awkward | yes | yes |
| **Settled fraction statically computable from field refs** | **yes** | **no — needs taint analysis** | partly | yes | partly | **no — has local state** | yes |
| Expresses the 17 decidable predicates | **13 natively + 4 host functions** | 17 | 15 | 6 | 10 | 17 | ≤10 |

**The alternative it had to beat, and why it lost on four independent grounds.** *Plain Python plus a
data-validation framework* wins on expressiveness and developer speed. It loses because:
(i) **the settled fraction stops being computable** — you cannot statically determine which fields a
Python function reads, so the product's headline number becomes an *estimate*, and this corpus is a
monument to what happens when a coverage claim is inferred rather than derived;
(ii) **executing model-written Python requires a sandbox**, and the sandbox layer is where the 2026
CVEs actually are;
(iii) **the predicate stops being auditable** — the predicate-library screen shows a function body,
not a rule, and the regulator-facing artifact degrades;
(iv) **mutating the predicate itself** (needed for registry hygiene) means mutating arbitrary Python,
where the equivalent-mutant rate is high and unbounded, versus a small grammar where the mutation
operators are enumerable. **Adopt pandera anyway — as a host-function implementation for bulk column
checks, never as the predicate language.**

**The runners-up, each with its specific loss:**

- **Rego / OPA** — genuinely close, and its *undefined* semantics are arguably closer to what we want
  than CEL's booleans. Lost on **readability** (the predicate library is the artifact a regulator
  would want, and a rule an auditor cannot read has negative value) and on **host language** (mature
  implementation is Go; embedding means a subprocess or a WASM bundle per evaluation). **Reconsider
  if the stack ever moves to Go.**
- **Starlark** — deterministic, hermetic, terminating. Lost **decisively** because a Starlark
  predicate has **local state**, so *"which fields does this predicate read?"* stops being a static
  question — and the settled fraction is computed from that question.
- **JSONLogic** — no type system, no date arithmetic, no regex in the core spec; cannot express the
  date-comparison or NAV-frequency predicates without extension. **Its *shape* — a rule is a tree —
  is worth stealing for the envelope, and we did.**
- **JMESPath** — a *query* language, not a predicate language. **Adopted for a different job: naming
  the exact fact a predicate read, in provenance pointers.**
- **SpEL** — rejected outright on security. It evaluates against a full JVM object graph with type
  references and constructor/method invocation; SpEL injection is a known RCE class. **It is not a
  restricted language, it is a scripting hook into a runtime.**
- **Z3 as the primary language** — a category error. Z3 answers *"is this predicate ever
  falsifiable"*, not *"is this filing correct"*. **Adopted for L4 T2, rejected for L5.**
- **Drools / GoRules ZEN / json-rules-engine / Nools** — a rule engine's core competence is
  **conflict resolution and chaining**: deciding which of many applicable rules to fire and letting
  rules produce facts that trigger other rules. **Our architecture forbids exactly that**, because
  every predicate must be independently scored (kill rate, FFR) and independently attributable in the
  report, and chaining makes both incoherent. **We do not have a rules-engine problem. We have an
  assertion-evaluation problem.** *(ZEN's JSON Decision Model tables are a good rendering of a rule
  set for non-programmers and are worth stealing for the predicate-library screen.)*
- **VTL 2.2 (SDMX)** — right domain, wrong altitude. It is designed for *statistical dataset* algebra
  over identifier/measure/attribute cubes; our artifact is a 10-sheet workbook with merged headers,
  and **getting it into VTL's data model is the hard part, which VTL does not help with**. Live
  implementations are stuck on the **1.1 draft**, five-plus years behind the published spec, and the
  Python engine is **AGPL-3.0** while the spec repo has **no licence**. **Reject as the language;
  mine its `check_datapoint`/`check_hierarchy` operator vocabulary**, because European statistical
  authorities have already enumerated the shapes of "a validation rule over a regulatory return."
- **XBRL Formula 1.0 + Assertion Severity 2.0 / Rune DSL** — **evaluate as export formats only.**
  Neither has a slot for a kill rate or an FFR, and making either primary would delete the thing that
  makes the registry worth having. *Adopt Rune's `condition Name: <"rationale"> expression` shape for
  L3's output format even if the Rune toolchain never runs.*

**The precedent that settles whether this is a real engineering choice rather than an affectation:**
Kubernetes ValidatingAdmissionPolicy — alpha in v1.26, beta in v1.28, **GA in v1.30** — is *"a
declarative, in-process alternative to validating admission webhooks"* using CEL. **That is exactly
our shape: model-free policy over structured data, evaluated in-process, no container per check.**
Kubernetes also demonstrates the two resource controls we need — a **runtime cost budget** that halts
execution when exceeded, and a **static estimate** that refuses to persist an expression whose worst
case is prohibitive. *(The widely-repeated numeric cost constant is **NOT-FOUND** in the
documentation; it lives in source. **Do not quote a figure** — calibrate our own budget on our own
workbook.)*

### 4.2.1 The admitted grammar profile

We do **not** admit all of CEL. The profile is enforced by an AST walker at admission time, and it is
what makes both mutation and static field-extraction tractable.

```ebnf
predicate   ::= disjunction
disjunction ::= conjunction ( "||" conjunction )*
conjunction ::= negation    ( "&&" negation    )*
negation    ::= [ "!" ] atom
atom        ::= comparison | membership | quantifier | call | "(" disjunction ")"

comparison  ::= arith relop arith
relop       ::= "==" | "!=" | "<" | "<=" | ">" | ">="
arith       ::= term ( ("+"|"-") term )*
term        ::= factor ( ("*"|"/") factor )*
factor      ::= number | string | selector | agg | call | "(" arith ")"

membership  ::= arith "in" ( selector | listlit )
quantifier  ::= selector "." ( "all" | "exists" | "exists_one" ) "(" ident "," disjunction ")"
agg         ::= "sum" "(" selector "." "map" "(" ident "," arith ")" ")" | "size" "(" selector ")"
selector    ::= root ( "." ident | "[" int "]" )+
root        ::= "filing" | "template"
call        ::= hostfn "(" arith { "," arith } ")"
```

**Deliberately excluded:** `map()` for anything but the argument of `sum()`; nested comprehensions;
`filter()` outside `witness`; protobuf messages; `bytes`; `uint`; `type()`; `dyn()`. **Nested
comprehensions are the only route to exponential blow-up the spec names**, and excluding them turns
*"can be curtailed by the implementation"* from a promise into a fact.

### 4.2.2 The fact model

L1 emits two content-addressed documents. CEL binds **exactly two top-level names**. Nothing else is
in scope — no clock, no network, no filesystem.

```
filing.<sheet_key>.<table_key>.rows[i].<field_key>   -> typed scalar (money as integer micro-units)
filing.<sheet_key>.<field_key>                       -> typed scalar
filing.<...>.__cell__                                -> "3. Portfolio!O7"   (provenance pointer)
filing.__hash__                                      -> sha256 of the submitted workbook
template.vocab.<vocab_key>                           -> list<string>   (from the PINNED blank)
template.formula.<cell>                              -> string         (the native formula text)
template.__hash__                                    -> sha256 of the pinned blank template
```

**Two non-negotiable rules:**
- **Vocabularies always resolve against `template`, never `filing`.** `Dropdown` is the only
  unprotected sheet; reading the vocabulary from the submission lets a filer define their own
  legality.
- **Every leaf carries `__cell__`.** The report must expand a failure to actual cells, and
  weakest-input provenance needs a pointer **per input**, not per predicate.

### 4.2.3 The escape hatch, and the rule that stops it eating the design

Four of the 17 decidable predicates cannot be expressed in the profile. Each becomes a **host
function**: named, deterministic, individually versioned Python, registered into the CEL environment,
with **its own test suite and its own kill rate**. The predicate stays one readable line; the
impurity is quarantined and enumerable.

| Host function | Serves | Why it cannot be CEL | Its own contract |
|---|---|---|---|
| `reg_resolves(kind, number)` | register resolution | external state | **Tri-state** `TRUE / FALSE / UNKNOWN(snapshot stale)`; UNKNOWN ⇒ `UNCHECKED(not_run.input_unavailable.register)`. **Never resolves live at verdict time — always against a content-addressed snapshot**, or the report is not reproducible. Normalisation is **NFKC + `U+2011 → U+002D` + strip**, compared case-insensitively, with **both `raw_value` and `normalised_value` recorded and the transformation list published** |
| `gstin_valid(s)` | GSTIN check digit | 15-char structure + mod-36 over a 36-character alphabet | Pure. Unit tests + its own kill rate; belongs to the deterministic half of the coverage claim |
| `template_current(hash)` | template-version currency | needs the corpus | Tri-state `CURRENT / SUPERSEDED / UNKNOWN` |
| `nav_interval(scheme_type, open_closed, tenure)` | NAV frequency owed | encodes regulation, including reg 39(1)'s half-yearly proviso and reg 51(1)'s delegation | **Must be able to return `UNDERSPECIFIED`** ⇒ `UNCHECKED(no_predicate.rule_ambiguous)`. **Reg 51(1) ends "in such manner as specified by the Authority." A system that resolves that delegation into a concrete interval is asserting something the regulation does not say.** This single signature is the architecture's thesis executed at the level of a function |
| `matches` `date` `months_between` `abs` `round` `normalize` `period_end` | regex, dates, arithmetic, name comparison, quarter→date mapping | pure utility | Versioned with the profile. `normalize` is a host function **precisely so its behaviour is separately versioned and separately tested** — *"Mr. Rajesh Kumar"* vs *"Rajesh  Kumar"* is the entire difficulty of the Principal-Officer predicate, and burying it in the expression would make that predicate's FFR depend on an invisible string-handling decision. `period_end` maps the two dropdown vocabularies to a concrete date and is **regulation-derived, so it is a versioned artifact with a clause citation, not a helper** |

**The rule:** a host function may be **added only by a human**, is **never generated by a model**, has
its **own test suite and kill rate**, and **must be able to return a third value wherever its answer
can be unknown**. The set is closed at evaluation time; a predicate calling an unregistered function
is rejected at admission.

### 4.2.4 Runtime, sandbox, and one measured consequence

**Start on `celpy`** (`cloud-custodian/cel-python`, **Apache-2.0**, pure Python, 171★/40 forks, years
of use inside Cloud Custodian) and keep **`cel-expr-python`** (`cel-expr/cel-python`, Apache-2.0, a
wrapper over the official CEL C++, announced 3 Mar 2026, 76★, repository launched read-only) as the
drop-in for when conformance exactness matters more than deployment simplicity. **Pin by PyPI name
and hash: two different projects both live at a path called `cel-python`, and that is a real
footgun.** Whether `celpy` passes the CEL conformance suite is **NOT-FOUND on its repository page** —
**run the conformance suite against both before committing**, because if they diverge *on error
semantics specifically*, the §L5 rule-2 guard behaves differently between them.

**The sandbox question mostly dissolves, and that is the point.** With a restricted language there is
no model-generated Python to contain: **CEL *is* the sandbox** — terminating, side-effect-free, no
I/O, exactly two bound names. What remains is the **parser tier**, which is an ordinary,
well-understood container-hardening exercise (§L0). **Choosing a restricted language in Part A
deletes the hardest sandboxing problem instead of solving it.**

**And one numeric requirement falls straight out of the language choice: CEL has no decimal type.**
The filing is denominated in USD Million to two decimal places. **L1 must scale monetary values to
integer micro-units before they enter the fact model**, or every arithmetic predicate acquires a
floating-point false-failure rate we did not choose and cannot attribute. This is a schema
requirement, and it is cheap only if done at the start.

## 4.3 How a predicate is qualified — the four gates, in order

```
T0  SCOPE FAITHFULNESS   verbatim clause quote locates in the source; every proviso in that span is
                         either implemented as a branch or declared as an UNCHECKED emission.
                         Neither ⇒ REJECT.                                    [structural, cheap]

T1  SEEDED-DEFECT        KR = K/O over mutants verified OBSERVABLE by recalculation, under a
    ADEQUACY             declared versioned fault model, reported as a per-fault-class VECTOR
                         plus the unobservable rate.  Admit at KR ≥ 0.80 on the classes the
                         predicate CLAIMS to cover.                            [empirical]

T2  NON-DEGENERACY       Z3: ¬P SAT (it can fail) and P SAT (it can pass) over the field domains;
                         plus a 10% control arm seeded into fields the predicate does NOT read,
                         counting spurious fires; plus the hypergeometric random-flagger adjusted
                         precision.  `unknown` from Z3 ⇒ UNCHECKED, never "non-degenerate".
                                                                               [proof + empirical]

T3  FALSE-FAILURE RATE   FFR on a clean corpus whose provenance ≠ SELF-AUTHORED, with n, a Wilson
                         interval, `clean_corpus_independent_of_predicate`, a held-out
                         structurally-distinct slice reported separately, and the MARGINAL FFR
                         conditioned on the already-admitted set.  Admit at FFR ≤ 0.10.
                                                                               [empirical]
```

**Ordering matters.** T0 is structural and costs nothing, so it runs first and rejects the failure
class the other three cannot see. T2's proof arm runs before T1's empirical arm, because a predicate
Z3 proves unfalsifiable should never consume a mutation budget.

**The held-out slice is not optional.** Our clean corpus is both synthetic and small. Hold out a
**structurally distinct** slice — filings for a scheme type absent from the fitting slice — and
report its FFR separately. **Without it, every FFR we print is an upper bound on our own optimism.**

**Rejections are kept, not discarded.** A candidate that fails any gate is recorded as
`no_predicate.failed_qualification` with the rejecting test and the measured number, and it appears
in the report's `counterEvidence[]`. This is required by the documentation standard we are borrowing
from: audit documentation **must include information that is inconsistent with or contradicts the
final conclusions**. We were going to throw exactly that away.

## 4.4 What a predicate carries permanently

Everything in `qualification`, `qualified_against`, `liveness_witness` and `external_deps` is part of
the predicate's **identity**, not metadata about it. Concretely, permanently, and visible on the
predicate-library screen:

- the clause, with FRBR URI and `eId`, and the **verbatim quote** that located it;
- the code, and its `sha256`;
- the **kill rate with its denominator and its per-fault-class vector**, the fault-model version, and
  the unobservable rate;
- the **degeneracy verdict, the Z3 counterexample, and the random-flagger adjusted precision**;
- the **FFR as a quadruple plus an interval**, with `corpus_provenance` and
  `clean_corpus_independent_of_predicate`, and the held-out-slice FFR beside it;
- the **marginal FFR conditioned on the admitted set**;
- for model-proposed predicates, the **model id, the date and the prompt hash** — so that a
  re-synthesis under a drifted model is a **diff, not a mystery**;
- the admission date, the admitter, and — if applicable — the withdrawal date and reason;
- the **coverage gap it inherits**: `circulars_unreadable: 10/399`, carried on every predicate whose
  correctness rests on the §4.1 negative search result. *(Or OCR them, which is an afternoon.)*

**Two things the record must never contain:** a bare percentage anywhere, and a `SELF-AUTHORED` FFR
rendered as a number.

## 4.5 Versioning against a changing template

**Version churn is not a risk. It is scheduled, and it has already happened.** The template's own
financial-year vocabulary runs out at **2028-29**; the 29th Authority Meeting of **24 July 2026**
moved the rule under the most sophisticated predicate in the set; and **23.1% of circulars amend an
earlier instrument.**

**The failure this policy exists to prevent, stated concretely.** Predicate #17 — *latest valuation
date vs the NAV frequency owed under regs 27(1)/39(1)/51(1)* — was pure date arithmetic before
24 July 2026. After it, the owed frequency depends on **whether 75% of investors by value approved**,
a fact the workbook does not collect. **The predicate does not error. It does not abstain. It keeps
computing a date difference against a rule that no longer exists.** A filer who lawfully moved to
annual NAV gets a **false failure**; a filer who moved without the approval gets a **silent pass**.
Both outputs are clean, confident and well-formed.

**The policy, in six rules:**

**V1 — Keys are label-anchored, never coordinate-anchored.**
`key = (sheet_name, merged_header_path, row_label)` is identity; `coords` is a resolved attribute,
re-derived per template version. **A version bump becomes a re-resolution, not a rewrite.**
Unresolvable keys enter an explicit `UNRESOLVED` state that **blocks** the predicate; they never
silently rebind to the wrong cell.

**V2 — Every element of `qualified_against` is part of the predicate's identity**: template hash and
label, regulation version, circular-corpus snapshot, unreadable-circular count, corpus id and
provenance and n, and for model-proposed predicates the model id and prompt hash.

**V3 — Any change to any element of `qualified_against` moves the predicate to `PROVISIONAL`.** It
still **runs**, so detection is not lost, but:
- its measured numbers are **hidden** in the UI and replaced by *"not re-qualified for this template
  version"*; and
- **it does not count in the settled numerator.**

**Therefore the settled fraction falls when the template changes. That is correct, and it is the
honest behaviour. A system whose coverage silently persists across a version boundary is lying.**

**V4 — "Grows monotonically" is deleted from the corpus.** Monotonic growth is incompatible with
re-qualification and quarantine. The coverage-over-time chart must be able to **step down**, and the
step-downs are the most credible thing on it: they are the only evidence the system notices when the
world moves.

**V5 — Liveness witnesses are replayed, and a predicate whose `kill_case` stops dying is quarantined
automatically.** This is the analogue of **vacuity detection** in model checking — an assertion that
passes because its antecedent is never satisfied. *(The canonical formal-methods citation for vacuity
detection is **UNVERIFIED** and must not be asserted; the mechanism needs none — it is two extra
executions per predicate.)* **Note its limit honestly: applied to predicate #17, the `kill_case` was
built against the semi-annual rule and would still die, because the mutant and the predicate moved
together. V5 alone does not catch a rule change. That needs V6.**

**V6 — Watch the instrument stream, not just the instrument.** Reg 51(1) ends *"in such manner as
specified by the Authority"* — a live delegation hook, so **the rule can change by circular without
the regulation changing**, and watching the regulation's version is insufficient. A daily
content-hash of the circular and Authority-meeting pages; any new instrument citing a regulation a
predicate claims to implement moves that predicate to `PROVISIONAL` automatically and pessimistically;
a human clears it. **This is the only mechanism that would have caught 24 July 2026.**

**And a seventh rule that is a consequence of V1–V6:** `withdrawn_on` / `withdrawn_reason` exist on
every predicate, with the reason drawn from `{rule_amended, ffr_exceeded_threshold, superseded_by,
source_schema_changed}`. **A registry that grows without a withdrawal state silently carries dead
checks** — which is precisely what the EBA's quarterly deactivation list is a public admission of,
and the design should not repeat the mistake it is selling against.

## 4.6 The exact semantics of the verdict

### 4.6.1 The state axis — seven closed values, and what each does to the denominator

The brief had one axis (`PASS / FAIL / UNCHECKED(reason)`) with six reasons. It has **four defects**,
each traceable to a source that solved it in 2012 or earlier:

1. **No `notapplicable`.** On a 10-sheet workbook filed by 217 heterogeneous FMEs, **whole sheets
   legitimately do not apply** — the AML-CFT sheet is half-yearly on its face. **Without this state
   the denominator is wrong on every real filing.**
2. **No `notselected`.** A targeted run over a subset is not the same as no-predicate-exists.
3. **No runtime-error state.** *"The register was down"* and *"no predicate exists for this clause"*
   have **opposite remedies** — retry versus write code — and the six-reason vocabulary cannot
   distinguish them.
4. **`no oracle exists` and `requires judgment` overlap almost totally**, while the operationally
   distinct case — *a predicate was written and the gate rejected it* — has **no state at all**. That
   is the most honest thing the system can emit, and the vocabulary omits it.

| State | Meaning | In the settled denominator? | Precedent |
|---|---|:--:|---|
| `PASS` | predicate ran; condition held | ✅ settled | XCCDF `pass` |
| `FAIL` | predicate ran; condition did not hold | ✅ settled | XCCDF `fail` |
| `INDETERMINATE` | predicate ran to completion; the result is not decidable | ✅ **kept** | XCCDF `unknown` |
| `NOT_RUN` | predicate is admitted and in scope but did not execute | ✅ **kept** | XCCDF `error`; C2PA `inaccessible` / `skipped` |
| `NO_PREDICATE` | field × obligation is in scope; no admitted predicate covers it | ✅ **kept — see the divergence below** | XCCDF `notchecked` |
| `OUT_OF_SCOPE` | does not apply to this filing, or excluded by this run's profile | ❌ removed | XCCDF `notapplicable` / `notselected` |
| `INFORMATIONAL` | predicate ran; the output is a value for the reader, not a verdict | ❌ removed | XCCDF `informational` |

**Plus one run-level state and one orthogonal axis:**
- **`INVALID`** — a *run* state, not an item state, produced by L6.5 when a predicate fails to fire on
  a fault it is known to detect, or by any `ERROR`. *"This system could not demonstrate it was
  working here."*
- **`ERROR(predicate, exception)`** — an item state distinct from every reason code above. **Any
  `ERROR` makes the run `INVALID`.**
- **`override`** — orthogonal, not an eighth state: `{oldState, newState, remark, actor, time}`, both
  states retained, inside the signed payload. The compliance officer *will* disagree with a FAIL, and
  the answer is to keep both results, require a rationale and a timestamp, and make the override part
  of the record. An overridden item counts under its **new** state, and **the override count is
  reported separately** — a supervisor will want it.
- **`severity ∈ {BLOCKING, ADVISORY}`**, set by the measured FFR. A high-FFR predicate enters as
  ADVISORY with its number printed beside it. *(This is the EBA's warnings-first convention with the
  measurement restored; ESMA runs `MUST/SHOULD`, EIOPA `ERROR/WARNING`, EBA **93.81% warning /
  6.19% error**.)*

**The denominator rule, and the one deliberate divergence from the standard.**
XCCDF's normative scoring algorithm removes `{notapplicable, notchecked, informational, notselected}`
and **keeps `error`, `unknown`, `fail`** — an asymmetry that is deliberate and correct, because
otherwise a tool could raise its score by failing. We adopt it with one change:

> **We keep `NO_PREDICATE` in the denominator.** XCCDF's denominator is a benchmark a human authored,
> so "no check exists" means the author chose not to have one. **Ours is induced from the regulator's
> own template, which is authoritative and complete — so "no predicate exists" is a gap in *us*, not
> in the specification.** Removing it would let the product's settled fraction rise by doing nothing.
> **This is the single most important scoring decision in the design and it ships with this
> justification attached.**

### 4.6.2 The reason vocabulary — closed, namespaced, nineteen codes

**The admission test for a reason code, written into the spec:**
> *Two reasons are distinct if and only if they imply different remedies. If the operator's next
> action is the same, the codes merge.*

That test is why the vocabulary is 19 and not 6, and also why it is not 40.

**`NO_PREDICATE.*` — we have no check. The honest core; this is the backlog.**

| Code | Meaning | Remedy |
|---|---|---|
| `no_predicate.undecidable_by_construction` | "correct" is not defined for this obligation — Third Schedule Part A(g) valuation appropriateness; whether a scheme is properly classified | **None. This is the permanent floor; report it forever** |
| `no_predicate.requires_judgment` | a competent human can decide; no program can — reg 119(3)(e) rationale adequacy; whether a complaint was resolved satisfactorily | Route to a human; never auto-close |
| `no_predicate.not_yet_synthesised` | decidable in principle; nobody has written it | **The L3 backlog — the growable set, and the coverage-over-time story** |
| `no_predicate.failed_qualification` | a predicate **was** written and **the gate rejected it** — carries the rejecting test and the measured number | Improve the predicate, or accept the gap knowingly |
| `no_predicate.rule_ambiguous` | the obligation text does not determine a testable condition — reg 51(1)'s open delegation | Ask the regulator |
| `no_predicate.no_obligation_specified` | **the instrument is clear and simply says nothing.** Two of nine legal Type-of-Scheme values have **no NAV-frequency rule at all** | **Distinct from `rule_ambiguous` (a rule exists and is unclear) and from `not_yet_synthesised` (our gap). Conflating "the regulator did not legislate this" with "we haven't got round to it" would be the single most misleading thing the panel could do** |

**`NOT_RUN.*` — we have a check; it did not run. Every one is an ops or data problem.**

| Code | Meaning |
|---|---|
| `not_run.input_unavailable.counterparty` | needs data held by a party who is not the filer (look-through into schemes the FME does not manage) |
| `not_run.input_unavailable.register` | live register unreachable, rate-limited, or ambiguous at run time |
| `not_run.input_unavailable.prior_period` | needs a filing we do not hold |
| `not_run.source_unreadable` | the artifact or a region of it could not be parsed |
| `not_run.extractor_disagreement` | **the three readers disagreed on this field.** Added because a schema extractor that silently returns 35 of 54 validations is the failure the product exists to prevent, occurring inside the product |
| `not_run.external_source_lacks_field` | the external source **structurally does not carry the field** the predicate needs. *Added because a lane spent a day concluding the register was a name list; the honest verdict for that state is neither PASS nor FAIL* |
| `not_run.template_unbound` | L1 could not bind the filing to a published template hash — **the whole run is suspect; this escalates** |
| `not_run.predicate_error` | the predicate raised at runtime |
| `not_run.deactivated` | an admitted predicate deliberately switched off for this run, with a pointer to the decision record. *Skipping is sometimes legitimate, and the moment it is legitimate the report **must** be able to say so, or the skip becomes silent. Ours will arise the first time a predicate's FFR is found unacceptable in production and someone switches it off mid-quarter* |
| `not_run.budget_exhausted` | time or cost limit hit before this pair was reached |

**`INDETERMINATE.*` — the check ran and could not decide.**

| Code | Meaning |
|---|---|
| `indeterminate.extraction_abstained` | the L2b conformal prediction set was not a singleton — the designed abstention |
| `indeterminate.tolerance_straddle` | the result falls inside the rounding band where both answers are admissible. **The rounding-tolerance trade-off now has a name instead of being absorbed into a threshold** |
| `indeterminate.conflicting_sources` | two admitted sources disagree and no tie-break rule is published |
| `indeterminate.calibration_not_exchangeable` | the conformal test martingale rejected exchangeability; the guarantee has lapsed and the claim is withdrawn |

**`OUT_OF_SCOPE.*` — removed from the denominator, therefore the most abusable. Each requires a machine-checkable justification.**

| Code | Meaning | Justification required |
|---|---|---|
| `out_of_scope.not_applicable` | field/sheet does not apply to this entity or scheme type | a pointer to the schema condition that makes it inapplicable |
| `out_of_scope.not_selected` | excluded by this run's profile | a pointer to the named profile and its digest |
| `out_of_scope.withheld` | the operator intentionally provides no information | an actor + rationale; **counted and displayed separately, never folded into `not_applicable`** |

**Mapping from the brief's six, so nothing is lost:** *no oracle exists* →
`no_predicate.undecidable_by_construction`; *requires counterparty data* →
`not_run.input_unavailable.counterparty`; *requires judgment* → `no_predicate.requires_judgment`;
*source unreadable* → `not_run.source_unreadable`; *rule ambiguous* →
`no_predicate.rule_ambiguous`; *predicate not yet synthesised* →
`no_predicate.not_yet_synthesised`. **The other thirteen are new, and eleven of the thirteen come
straight out of XCCDF, C2PA, SPDX or SLSA rather than being invented here.**

**Why the distinctions are load-bearing, in one measured example.** SPDX names **three** distinct
causes of non-assertion — *"the creator has attempted to but cannot reach a reasonable objective
determination"*, *"has made no attempt to determine this field"*, and *"has intentionally provided no
information"* — and then **deliberately collapses all three into one token, `NOASSERTION`.** That is
a documented decision, not an oversight. **It is precisely the collapse this product exists to
refuse**, and it is the cleanest single citation for *"the state of the art names the distinction and
then throws it away."*

### 4.6.3 Aggregation — from a vector of item states to a document-level verdict

The brief emitted per-item states and then **stopped**. There was no rule for turning that vector
into a filing-level verdict. ISA 705 is that rule, and it has been the global standard for decades.

**A declared, published, versioned pervasiveness policy, applied deterministically:**

```
residueIsConfined :=  (unsettled pairs touch ≤ K distinct sheets)
                  AND (no unsettled pair is flagged material-by-policy)
                  AND (unsettled / inScope ≤ T)
```

`K`, `T` and the material-by-policy field list are **published, versioned parameters carried in the
attestation** — not constants in code.

| | residue confined | residue pervasive |
|---|---|---|
| **failures present** (`settled.fail > 0`) | `EXCEPTIONS_NOTED` *(≈ qualified)* | `ADVERSE` |
| **no failures, unsettled residue** | `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE` *(≈ qualified for scope)* | **`COVERAGE_INSUFFICIENT`** *(≈ disclaimer)* |
| **self-check failed** | `INVALID` | `INVALID` |

**Three consequences taken directly from the standard, and all three matter:**

- **There is no state whose name means "clean."** The best available verdict is literally called
  `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE`, **which cannot be quoted out of context without
  carrying its own qualifier.** This delivers the no-green-tick commitment **by naming**, which is
  far more robust than by iconography: **an icon can be screenshotted; a name travels with the
  claim.**
- **The heading changes with the residue.** The report's own title string is a function of the
  verdict state, not a fixed "Coverage Report".
- **When `COVERAGE_INSUFFICIENT`, the report must not describe itself as having verified the
  filing.** The wording flips from *"this filing was checked against N predicates"* to *"this filing
  was **submitted for** checking against N predicates; coverage was insufficient to report."*

**Say what we are doing, and what we are not.** "Material" and "pervasive" are matters of
professional judgment in the standard. **We cannot compute them.** We can define a declared,
published, versioned policy and apply it deterministically — which is strictly more inspectable than
judgment, and is the honest form of the borrowing. **Do not claim to have implemented ISA 705. Claim
a declared policy in its shape.**

### 4.6.4 The headline, and why it is not a fraction

**Decision: the headline is two counts of equal weight, plus a residue count.**
*Alternative it beat:* a coverage meter reading *"71% of predicates settled."* *Why it lost, in four
measured steps:*

1. **A coverage meter is a green tick with extra steps.** 100% is reachable in the UI as specified,
   and when it reads 100% it is a green tick that took four seconds longer to render.
2. **The fraction is Goodhart-broken.** The decidable set is unbounded and mechanically expandable
   (one predicate per formula cell, per validation, per vocabulary — **505 + 35 + 15 = 555**); the
   undecidable set is **fixed at 7** and does not grow with effort. **17/24 = 71% → 555/562 = 98.8%
   in one afternoon without writing a single interesting check.** A number that moves that far under
   an author's choice of enumeration is not a measurement.
3. **A progress bar carries an implicit target of 100% and therefore a success state.** Users do not
   read *"71% checked, 0 failures"* as a scope declaration. They read it as *"71% clean"*, then as
   *"clean."*
4. **The export path is where the tick sneaks back in.** Copy discipline does not survive a
   screenshot.

**What ships instead:**

```
  0 failures across 555 checks.        7 properties were not checked.
  ───────────────────────────────      ───────────────────────────────
  (same type size, same weight, same ink, side by side, no colour on either)

  Outside the boundary — properties no predicate can settle from this artifact alone      7
  Demonstrated survivors — corruptions that passed every check (residue set)              12
```

- **No progress bar, no ring, no percentage.** A fixed-height stacked band with absolute counts; the
  unchecked segment is **hatched**, not muted — muted reads as *"resolved, minor"*; hatched reads as
  *"not filled in"*, which is the truth.
- **Nothing renders green, ever.** Passing checks take the same neutral ink as body text; only
  failures get colour. **The absence of colour is not the presence of green.**
- **100% is structurally unreachable**, because the denominator includes the known-uncheckable and
  the residue count is never zero. **This is architectural, not cosmetic: it changes what the number
  is a fraction of.**
- **The meter carries its own provenance**, always: `denominator generated by rule v3 · predicate set
  v11 · qualified against template sha256:9f3c… · 4 predicates stale`. **A summary statistic that
  cannot be interrogated is the thing the product exists to oppose.**
- **If a fraction must exist, report weighted and unweighted, always both**, with the weights taken
  from a source we do not control — whether the clause carries a penalty provision, whether the field
  feeds a published IFSCA aggregate, observed defect frequency. *(No consequence-weighting source has
  been identified. Label it **HOPED-FOR** until one is.)*
- **The predicate enumeration is generated by a published rule**, so a third party gets the same
  denominator: one predicate per formula-evaluating cell, one per data validation, one per shipped
  controlled vocabulary, one per "shall" clause naming a template field, one per admitted relation.
  **It is still not *meaningful* — the two counts are the fix for that — but it stops being
  adversarially manipulable by the party quoting it.**
- **And the demo must never display 71% unless 71% is what it computed.** 71% is the *decidability
  ratio* from a hand classification; a settled fraction is a *measurement of a filing*. Two different
  quantities, one number, is exactly the conflation the corpus's own rules forbid. *(The first honest
  computed figure, for the record: **63.3% of a 3,747-cell field surface settled by 280 mechanically
  derived predicates, 1,374 declared unchecked, in 30 ms with no model.** MEASURED-HERE.)*

**One sentence is permanent on the report surface, because it is the honest limit:**

> **This system detects error, not deception. Every check here is a consistency check over a
> self-reported document. A coherent liar passes all of them.**

Nothing in the architecture addresses adversarial filers, and a supervisor who does not know that
will misuse the output. **Saying it costs nothing and it is the sentence that makes the rest
believable.**

---

# PART 5 — THE REPORT

**Design rule used throughout: borrow the field, keep the citation.** Every element below traces to a
named source. Where something is invented, it says so.

## 5.1 The report object

### 5.1.1 The envelope

```jsonc
// DSSE envelope · payloadType "application/vnd.in-toto+json"
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    { "name": "filing",   "digest": { "sha256": "<hash of the filed workbook AS RECEIVED>" } },
    { "name": "template", "digest": { "sha256": "<hash of the published blank template>" } }
  ],
  "predicateType": "https://<ns>/filing-coverage-attestation/v1",
  "predicate": { /* §5.1.2 */ }
}
```

**Why in-toto/DSSE and not JSF or bare JWS:** it is Apache-2.0, it is what cosign, SLSA VSA and the
whole attestation ecosystem already speak, and **`subject[]` naturally carries the two hashes that
must be bound**. Binding the template hash is not optional — **a verdict against template v3 is
meaningless if the entity filed on v4.**

### 5.1.2 The predicate body

```jsonc
{
  // ── WHO, AND WITH WHAT ────────────────────────────────────────────────────
  "assessor": {
    "id": "https://<ns>/verifier/v3.2.1",   // version the id when verification logic changes materially
    "thirdParty": false,                     // false == SELF-ASSESSOR. Mandatory honesty.
    "components": {
      "predicateSetVersion": "3.2.1",
      "predicateSetRoot":    { "sha256": "…" },   // Merkle root over sorted code hashes
      "schemaInducerVersion":"1.4.0",
      "faultModelVersion":   "v3",
      "extractorModel":      null                  // null on the workbook path. ALWAYS null there.
    }
  },
  "timeVerified": "2026-08-10T09:12:44Z",
  "expires":      "2026-11-10T00:00:00Z",   // evidence goes stale; this field is required
  "specVersion":  "1.0.0",                   // the version of the checking apparatus's contract

  // ── WHAT WAS IN SCOPE, AND WHAT WAS TAKEN OUT ─────────────────────────────
  "scope": {
    "denominator": {
      "source":          "induced-from-template",   // NOT negotiated. This is the novelty.
      "generatorRule":   "v3",                       // published, so a third party reproduces it
      "fieldSurface":    3747,                       // unlocked ∧ non-formula cells
      "obligationsTotal": 41,
      "pairsTotal":      1187                        // the closed universe; DISALLOW * applies to it
    },
    "plannedSelection": { "includeAll": true, "exclude": [ /* selector + reason code */ ] },
    "actualSelection":  { "includeAll": true, "exclude": [ /* … */ ] },
    "selectionDelta":   [ /* results must show every change from the plan */ ],

    "checksRun": 555,
    "failures": 0,
    "unchecked": [ { "reason": "no_predicate.undecidable_by_construction", "count": 7 } ],
    "residue":  { "survivors": 12, "faultModel": "v3", "adjudicatedBy": "…", "manifest": "sha256:…" },
    "selfCheck": { "predicatesReplayed": 555, "deadPredicates": [], "passed": true }
  },

  // ── THE ITEMS ─────────────────────────────────────────────────────────────
  "items": [
    {
      "id":       "intro.tbl15.row[3].scheme_type × reg27(1)",
      "pointer":  "/report/items/0",                  // RFC 6901 JSON Pointer into this document
      "obligation": {
        "standard":   "IFSCA (Fund Management) Regulations 2025 (as amended to 30 Jan 2026)",
        "frbrUri":    "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30",
        "eId":        "reg_27__para_1",
        "sourceDigest": { "sha256": "…" }             // the exact PDF the clause was read from
      },
      "predicate": { "id": "P-0117", "version": 2, "digest": { "sha256": "…" } },
      "method":    "RECOMPUTE",                        // §5.1.3
      "state":     "PASS",                             // §4.6.1 — closed, 7 values
      "reason":    null,                               // §4.6.2 — closed, required iff state ∉ {PASS,FAIL}
      "severity":  "BLOCKING",                         // set by the measured FFR
      "provenance":"COMPUTED",                         // COMPUTED (by us) vs DECLARED (by the filer)
      "warrant":   "DETERMINISTIC",                    // DETERMINISTIC > MODEL_EXTRACTED > DERIVED
      "cellsBound": 10,                                // 0 ⇒ ERROR, never PASS
      "anchors":   [ /* §5.1.4 provenance anchors, one per input read */ ],
      "qualification": { /* the full §4.1 block, copied by value, not by reference */ },
      "override":  null                                // {oldState,newState,remark,actor,time}
    }
  ],

  // ── WHAT ARGUES AGAINST US ────────────────────────────────────────────────
  "counterEvidence": [
    { "kind": "rejected-predicate", "obligation": "reg 51(1)", "predicateId": "P-0203",
      "rejectedBy": "T3", "measured": { "ffr": 0.41, "n": 340, "corpusProvenance": "BLIND-FILLED" },
      "note": "would have covered 6 further pairs; rejected on false-failure rate" },
    { "kind": "near-miss", "predicateId": "P-0117", "faultClass": "F5", "killRate": 0.12 }
  ],

  // ── THE ARITHMETIC, WITH ITS DENOMINATORS ─────────────────────────────────
  "settledFraction": {                       // renamed from "coverage": that word means something
    "pairsTotal":  1187,                     // else three pages away, in the conformal sense
    "outOfScope":  214,                      // removed from the denominator
    "inScope":     973,                      // = pairsTotal − outOfScope  ← THE denominator
    "settled":     { "pass": 611, "fail": 12, "total": 623 },
    "unsettled":   { "indeterminate": 41, "notRun": 88, "noPredicate": 221 },  // ALL KEPT IN
    "fraction":    0.6402,                   // meaningless without the four counts above
    "aggregate":   "incomplete",             // CycloneDX aggregateType, as ONE roll-up header field
    "denominatorWarning":
      "The denominator varies between filings because out-of-scope determinations are filing-specific.
       Settled fractions are not directly comparable across filings."
  },

  // ── THE AGGREGATE VERDICT ─────────────────────────────────────────────────
  "verdict": {
    "state": "EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE",
    "pervasivenessPolicy": { "version": "v2", "K": 3, "T": 0.35, "materialFields": [ "…" ] }
  },

  // ── THE SENTENCES THAT MAY NOT BE REMOVED ─────────────────────────────────
  "boundedSilenceStatement":
    "Had additional predicates been executed, other matters might have been reported. This report
     states only the results of the predicates listed, and makes no representation that the predicate
     set is sufficient for any purpose.",
  "purposeStatement":
    "This report relates only to the fields enumerated in scope.denominator and does not extend to
     the filing taken as a whole.",
  "deceptionStatement":
    "This system detects error, not deception. Every check is a consistency check over a
     self-reported document. A coherent liar passes all of them.",
  "summaryIsNotSubstitute": true,
  "coverageGaps": [ { "kind": "unread-sources", "detail": "10 of 399 circulars are scanned images" } ]
}
```

**`boundedSilenceStatement`, `purposeStatement`, `deceptionStatement` and `summaryIsNotSubstitute`
are required by schema.** Making a disclaimer a mandatory field rather than a template string is the
cheapest possible way to guarantee it survives contact with a marketing page.

**And the field that is absent by design: there is no `result` and no `status`.** The top-level object
is `scope`. **There is nowhere in the schema to write "pass", so no downstream consumer can render
one.** Schema-level prohibition beats copy discipline because it survives the screenshot, the API
integration and the intern.

### 5.1.3 `method` — how a thing was checked

The standard vocabulary (`EXAMINE`, `INTERVIEW`, `TEST`, `UNKNOWN`) does not distinguish anything
that matters here. The closed extension, each value naming a distinct epistemic basis:

| Method | Meaning | Maps to |
|---|---|---|
| `RECOMPUTE` | the value was recomputed from other cells in the filing and compared | 135 SUM identities + 3 COUNTIF tallies |
| `TIE_OUT` | a cross-sheet carry compared against its source cell | 223 carry cells |
| `SCHEMA_BIND` | the value conforms to the induced schema (type, vocabulary, format, bound) | 54 validations, 22 list-type, 20 resolvable |
| `TEMPLATE_DIFF` | the filed cell compared against what the template's own formula computes | **the formula-override detector** |
| `REGISTER_LOOKUP` | resolved against a content-addressed snapshot of a live external register | registration / scheme-number resolution |
| `CLAUSE_TEST` | a synthesised predicate implementing a specific clause | the L3/L4 output |
| `DIFFERENTIAL` | a relation between two runs or two documents; no absolute oracle used | L6 |
| `MODEL_EXTRACT` | a value bound to a key by a model, then schema-validated | L2b — **never alone** |
| `UNKNOWN` | retained for projection fidelity | — |

**Rule: `MODEL_EXTRACT` may never be the sole method on a `PASS`.** This encodes *"a model may never
be the final judge"* as a **schema constraint** rather than a coding convention.

### 5.1.4 The provenance anchor

**Decision: adopt Docling's `ProvenanceItem` verbatim for the PDF class, and extend the union with two
locator kinds document AI does not have — an OOXML cell and a register record.** Verbatim adoption
means the PDF locator needs no translation layer and no coordinate-origin guesswork, and it inherits
a maintained, typed, versioned schema.

```jsonc
{
  "anchor": "1.0",
  "source":    { "content_sha256": "…", "media_type": "…", "retrieved_at": "…", "origin_uri": "…" },
  "extractor": { "name": "lxml", "version": "6.1.1", "mode": "DETERMINISTIC" },
  "warrant":   "DETERMINISTIC",
  "locator":   { /* exactly one of four */ }
}
```

**1 — `xlsx_cell`** *(ours; nothing in document AI models it)*
```jsonc
{ "kind": "xlsx_cell",
  "sheet_name": "3. Portfolio", "sheet_index": 2, "sheet_sha256": "…",
  "ref": "O4", "row": 4, "col": 15,
  "merged_anchor": null,
  "formula": { "present": true,
               "encoding": "SHARED_DEPENDENT",     // TEXT | SHARED_MASTER | SHARED_DEPENDENT | ARRAY | NONE
               "si": 4, "master_ref": "O3", "resolved": "=SUM(C4:N4)" } }
```
> **`formula.encoding` is not decoration.** 211 of 505 cells here, and **825 of 1,495 (55.2%) across
> the nine workbooks**, are `SHARED_DEPENDENT`. Recording the encoding is what makes the undercount
> **impossible to repeat silently**: a report can state *"505 formula-bearing cells, of which 211
> shared dependents"*, and any future reader who sees only 294 knows immediately what happened.

**2 — `pdf_span`** *(Docling's `ProvenanceItem`, field for field: `page_no`, `bbox{l,t,r,b,coord_origin}`, `charspan`, optional `table_cell` offsets)*

**3 — `clause`** *(FRBR URI + `eId` + `as_at`, carrying a full `pdf_span` so the clause is also visually citable)*

**4 — `register_record`** *(ours; no prior art found)*
```jsonc
{ "kind": "register_record",
  "endpoint": "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet",
  "query": { "EncryptedId": "…" },
  "snapshot_sha256": "…", "fetched_at": "…",
  "field": "RegistrationNumber",
  "raw_value":        "IFSCA/FME/III/2022‑23/037",     // EXACT bytes, homoglyph preserved
  "normalised_value": "IFSCA/FME/III/2022-23/037",
  "normalisation": ["NFKC", "U+2011->U+002D", "strip"] }
```
> **`raw_value` and `normalised_value` are both mandatory, and `normalisation` lists every
> transformation applied.** The reason is a live regulated entity: that registration number contains
> **`U+2011 NON-BREAKING HYPHEN`**, not `U+002D` — visually identical, byte-wise different, invisible
> in any log or screenshot. **A system that stores only the normalised form has destroyed the
> evidence that its own normalisation was load-bearing.**

**Composition rule, implementing weakest-input provenance:** a derived Fact carries the list of its
input anchors, takes `warrant = min(inputs)` under `DETERMINISTIC > MODEL_EXTRACTED > DERIVED`, and
`retrieved_at = max(inputs)` — **so a verdict is never fresher than its stalest input and never
stronger than its weakest.**

### 5.1.5 Two structural rules the schema enforces

1. **`NONE ≠ NOASSERTION ≠ absent.`** `[]` = *we determined there are none*; `null` = *we make no
   claim*; **field omitted = a schema violation the validator rejects.** All three must be
   distinguishable, and the third must be impossible. *(Borrowed verbatim in spirit from SLSA's
   normative treatment of `dependencyLevels` — "an unset or null … means that the verifier makes no
   claims" — and from SPDX's NONE/NOASSERTION split.)*
2. **Closure is enforced, not documented.**
   `outOfScope + settled.total + indeterminate + notRun + noPredicate == pairsTotal`, checked at
   report generation. **A pair that lands in no bucket aborts the report.** This is the terminal
   `DISALLOW *`, and it is the second load-bearing use of the same move — which is a good sign about
   the design.

### 5.1.6 What we emit, and in what order

| Artifact | Format | Normative? | Why |
|---|---|---|---|
| Coverage attestation | DSSE + in-toto Statement (§5.1.1–5.1.2) | **yes** | the only complete representation |
| Human report | **a single self-contained HTML file** | no | the two screens; renders the four counts, never the fraction alone; **hashable, emailable, offline** |
| OSCAL Assessment Results projection | OSCAL AR v1.2.3 JSON | no — **declared lossy** | GRC interop; free via `compliance-trestle` |
| OSCAL POA&M | OSCAL POA&M v1.2.3 JSON | no | **the Unchecked panel is a POA&M**: "reason + what would make it checkable" is exactly a `poam-item` plus a `risk.response.lifecycle ∈ {recommendation, planned, completed}`. **Do not invent a data model for the differentiator; there is a public-domain one with a Python writer** |
| Evidence crate | RO-Crate | no | blank template + circular PDFs + register snapshot + the filing, packaged and addressable |

## 5.2 The signing envelope, and who signs

**Decision: the filer signs, with a detached key, over the report JSON. The vendor signs nothing
about the filing; the vendor's identity appears only as `assessor.id` inside the payload, with
`thirdParty: false`.**

*Alternatives it beat:*
- **The vendor signs** — the vendor would be attesting to a regulated filing it did not prepare and
  cannot verify beyond its own declared scope. **If an FME shows an inspector a signed attestation
  over a filing that was wrong, the signature is the first exhibit.** The schema's absent `result`
  field is a partial answer; the signer question needed an explicit decision and this is it.
- **Sigstore keyless on the public-good instance** — keyless signing binds a workload or human
  identity into a **public certificate published permanently to a transparency log.** For filings by
  named FMEs that is a disclosure surface: **the fact and timing of a named entity running a
  pre-submission compliance check becomes world-readable and correlatable.** *(The transparency-log
  property is a documented design property of the system; the public-good instance's specific policy
  page was **not opened** — that is stated rather than assumed.)*
- **No signature at all** — then the coverage claim is marketing, the boundary can be restated later,
  and P4 of the problem statement is unmet.

**If a transparency log is wanted**, run a **private log instance operated by the supervisor**, whose
audience is already the regulator, and publish **only salted hashes** of filing identifiers.

**What is signed, and it is exactly the set sufficient to re-derive the verdict byte-for-byte:**
every input's `content_sha256`; the register `snapshot_sha256`; the AKN `frbr_uri@as_at` for every
cited clause; the predicate-set Merkle root; each predicate's kill rate and FFR **with corpus
provenance**; the fault-model version; the residue size and its manifest hash; the self-check result;
and the declared coverage gaps.

**Inherited limit, stated because the standards state it:** *a verification summary does not protect
against compromise of the verifier.* We inherit that exactly, and it is one more reason `verify` —
re-derive and byte-compare — is the observability story rather than a metrics backend.

## 5.3 Relationship to the standards the lanes found

**The brief's L7 sentence — *"There is no analogue for a financial assertion"* — is refuted on both
axes it asserts, by six counter-examples, five of them opened at source.** It must be rewritten
before anything is submitted, and the replacement is stronger because it names four specific
properties nobody has instead of one general absence that is false.

| Standard | What we take | What it cannot do, exactly |
|---|---|---|
| **XCCDF** (NISTIR 7275r4, March 2012) — **the real per-item prior art, and the brief never cited it** | **Table 26's nine result states** (`pass, fail, error, unknown, notapplicable, notchecked, notselected, informational, fixed`), which separate four distinct causes of non-settlement our six-reason vocabulary conflated or omitted; **§7.3.2.2/§7.3.2.3's denominator rule**, including the deliberate asymmetry that keeps `error` and `unknown` in so a tool cannot raise its score by failing; and **Table 27's `<override>`** `{old-result, new-result, remark, time}` with the rule that the result **shall** be changed to match | XML/SCAP-shaped, tied to `<xccdf:check>` → OVAL, and its target model is **a host, not a document**. We take the vocabulary and the scoring rule, not the format. *And it wrote our own UX warning into its normative text in 2012: "scores between different target systems may not be directly comparable because the maximum score can vary"* |
| **ISRS 4400 (Revised)** — *this alone refutes "no financial analogue"* | ¶30(j)'s **bounded-silence sentence, as a required schema field**; ¶30(h)'s disclaimer of procedure appropriateness; ¶13(f)'s definition of a finding as **objectively verifiable**; ¶A56's not-performed declaration; ¶32(b)'s "reading the summary is not a substitute"; and Appendix 2 Illustration 2's stated circumstances — *the regulator is the intended user and the entity overseen by the regulator is the engaging party* — **which is our exact two-party model, already contemplated, with the report template supplied** | ¶A56 is a **may**, not a **shall**, and it is free text. The report is **human prose in a two-column `Procedures` / `Findings` table**: no schema, no closed vocabulary, no machine-readable form, no fraction, **no per-procedure error rate**. And every procedure is **agreed with the engaging party in advance**, with its adequacy expressly disclaimed |
| **ISA 705 (Revised)** | The **2×2 aggregation rule** the design did not have (misstatement vs inability × confined vs pervasive); ¶24's *shall state the reasons*; ¶17's *"possible effects"* keeping a known defect distinguishable from an unexamined region in **one word**; ¶20(a)'s **heading that changes shape with the residue**; ¶19(c)'s prohibition on implying the work was completed; ¶21's mandated *"we could not even size this"* statement | "Material" and "pervasive" are matters of **professional judgment**. We cannot compute them; we declare a policy in their shape and apply it deterministically. **Fires only on a modified opinion** |
| **PCAOB AS 1215** | **.06A, the experienced-auditor test — the design test for the whole product**: our report is adequate iff *"an experienced auditor, having no previous connection with the engagement"* can reconstruct what was checked, how, by what version, and what was not. And **.08's counter-evidence requirement**, which is why L4's rejected predicates and near-misses are kept in `counterEvidence[]` rather than discarded | A documentation-retention standard for a US public-company audit: no schema, no vocabulary, no coverage concept, and a **seven-year retention obligation** if we ever position the output as audit documentation. **Position it explicitly as an input to the auditor's work, not as audit documentation** |
| **in-toto / DSSE** | The **envelope**; `subject[]` carrying two hashes; and the deepest borrowing — the **`DISALLOW *` closed-world principle**. The spec names the hazard in its own text: an implicit terminal `ALLOW *` *"could allow artifacts to sneak into the step or inspection **undetected**."* **Our L1-induced schema is the layout**, which is why the closure is possible for us | Its subject is a build pipeline; steps are commands and artifacts are files. **No notion of a partially-verified artifact, no reason codes, no coverage semantics in the envelope.** And its standard `test-result` predicate has `passedTests[]`, `warnedTests[]`, `failedTests[]` and **no `skippedTests[]`** — the "were they all run" check is performed by an out-of-band policy. **The standard test attestation cannot express a test that did not run** |
| **CycloneDX** | Three things, none of them the one the brief cited. **(a)** `compositions.aggregate` demoted from *"the prior art"* to **one roll-up header field** — and corrected: **six states in 1.3, ten in 1.5, not ten in 1.2**. **(b)** The far better prior art the brief missed: **`declarations` (CDXA, added in 1.6)** — `assessors[].thirdParty` (*"a value of false indicates a self assessor"*), `attestations[].map[].{claims, counterClaims, conformance, confidence}`, `claims[]` whose field is literally called **`predicate`**, `evidence[].expires`, and `standard.requirements[]` with **regulations explicitly in scope**. **(c)** 1.7's `citation` with **RFC 6901 JSON Pointers** — the right idiom for addressing a verdict to an exact location | `aggregate` is **aggregate, not per-item**: it tells you the *set* is incomplete and cannot say *which* component was not examined or why, and eight of its ten values encode one software-specific partition. CDXA's `conformance` is a **continuous score in [0,1] with free-text rationale** — **there is no discrete "not assessed" state, and a score of 0 is indistinguishable from "we never looked."** A float plus prose is exactly the interface we are arguing against |
| **C2PA 2.4** | The **strongest technical analogue found.** Its `status-codes-map` is `{success, informational, failure}`, and **`"success": bool` is marked DEPRECATED** — the 2.1 change log records *"LOTS of new validation status codes, including a new 'informational' code type."* **A shipping ecosystem shipped binary, found it insufficient in production, and replaced it with three-way classification.** Its five OCSP outcomes are the model for our reason codes: `notRevoked` (checked, clean) / `revoked` (checked, dirty) / `unknown` (the oracle said don't know) / `inaccessible` (tried, no response) / **`skipped` (deliberately did not check)** — and **§15.9.2 makes emitting the last two a `shall`.** Also: `created_assertions` vs `gathered_assertions`, which is our COMPUTED vs DECLARED distinction, cleanly encoded. And its governing principle, §1: *"C2PA specifications SHOULD NOT provide value judgments about whether a given set of provenance data is 'good' or 'bad,' merely whether the assertions included within can be validated"* — **the no-green-tick commitment written as a spec principle by a consortium** | **Every status code is about cryptographic or structural integrity.** Not one concerns whether an asserted fact is **true**. It answers *"was this manifest tampered with"*, never *"is this number right."* **That is the entire remaining distance, and it is our distance** |
| **SLSA VSA** | `verifier{id, version}` with the recommendation to **version the id when verification logic changes materially**; `policy{uri, digest}`; `inputAttestations[]`; **`UNEVALUATED`** as a nameable state; and the **absent-vs-empty rule** stated normatively | `UNEVALUATED` is **per-track** — two or three coarse buckets, no per-check granularity and no reason code — and `verificationResult` itself remains binary `PASSED\|FAILED` |
| **OpenSSF Scorecard** | Three properties we need and one warning. `InconclusiveResultScore = -1` as a **distinct sentinel**; **exclusion from the aggregate denominator**; and **a distinct rendering (`"?"`) so it can never be mistaken for a low score** | **The warning is the point: silent denominator shrinkage.** Nothing in its aggregate says how many checks were inconclusive, so a repository with **8 of 19 inconclusive** and one with **0 of 19** print the same score. **That is the failure mode our residue counts exist to prevent** |
| **OSCAL** (CC0 1.0 / public domain — **no licence obstacle to profiling, forking or embedding**) | `reviewed-controls` (**planned vs actual scope, with the delta visible**); `observation.methods` and `origin-actor.type ∈ {tool, assessment-platform, party}` — **OSCAL can say *a machine asserted this*** and distinguish it from a human; `assessment-assets` as the slot for "predicate registry v3.2.1, sha256:…"; `observation.expires`; and the **POA&M model as the Unchecked panel's interchange format**. Tooling: `compliance-trestle`, **Apache-2.0, Python, v5.0.0**, ships pydantic models for AR/AP/POA&M/component **plus detached JSON signing** | **Three hard stops.** (1) `finding-target.status.state` is a **closed two-value enum** `{satisfied, not-satisfied}` — the one field this product exists to add a third value to. (2) Non-coverage is expressed **by omission plus a free-text scope statement**, and `findings` was made **optional** in 2021 — so **an OSCAL AR with zero findings is schema-valid and means nothing in particular.** (3) The ontology is security-control-shaped; **our unit of assessment is a cell in a workbook bound to a clause, and OSCAL has no cell** |

### 5.3.1 The single most useful negative result

**OSCAL was asked for exactly our vocabulary, in 2021, and declined.** Issue #841 — *"AssessmentResults
findings with flexible results values… beyond the allowed values {satisfied, not satisfied}"* — cited
XCCDF Table 26 explicitly. It was resolved by adding a `reason` field (`anyOf` with an **open** token
branch), not by adding states. Five years and one major version later, `state` is still `allOf` with
**two** values.

> **The most mature, best-funded, government-backed assessment-reporting standard in existence looked
> directly at a nine-state vocabulary and shipped two states plus a free-text escape hatch. If we
> adopt one, we should expect to have to defend it — and the defence is XCCDF, C2PA and Scorecard,
> not novelty.**

The same issue thread contains the silent all-clear described precisely, by an implementer, in the
standard's own tracker: *"say you have 1 observation which is 'not applicable'. There would be no
finding in that case, **since neither satisfied nor not satisfied is known**."* **That is our problem
statement, stated by someone else, in 2021, and resolved by making the findings list optional.**

### 5.3.2 The projection rule, so the loss is explicit and auditable

| Our state | OSCAL AR encoding | What is lost |
|---|---|---|
| `PASS` | `finding` with `status.state = "satisfied"` | nothing |
| `FAIL` | `finding` with `status.state = "not-satisfied"` | nothing |
| `INDETERMINATE` / `NOT_RUN` / `NO_PREDICATE` | **an `observation`** with `methods:["TEST"]`, our reason as a `prop` in our namespace, **and no `finding`**, **and** a matching `reviewed-controls.control-selections[].exclude-controls[]` entry | the state is demoted from a **verdict** to an **observation**; a naive OSCAL consumer sees only "no finding" |
| `OUT_OF_SCOPE` | `exclude-controls[]` entry only | the reason code survives only as a `prop` |
| `INVALID` | **not representable** | **the run-level self-check result cannot be projected at all** |

**Any downstream party reading only the OSCAL projection will see a smaller, cleaner report than the
truth.** The projection therefore carries a **mandatory `metadata.prop` flagging that it is a lossy
projection and naming the URI of the normative artifact — in the file, not in a README.**

---

# PART 6 — WHAT IS GENUINELY NOVEL

## 6.1 First, the assembly — shown, not hidden

**A judge who finds one of these after the pitch discounts everything. A judge handed all seventeen
upfront reads the team as competent.** Every one of these is prior art, and every one of them is
cited rather than claimed.

| Part | Prior art | Warrant |
|---|---|---|
| LLM → executable assertions | **SPADE** (arXiv:2401.03038 / PVLDB 17(12):4173–4186) | VERIFIED-AT-SOURCE |
| Non-LLM automatic rule synthesis | **Deequ** *"Automatic suggestion of constraints for large datasets"* (Apache-2.0, 3,638★) | VERIFIED-AT-SOURCE |
| Dynamic invariant mining with no model at all | **Daikon** (MIT-equivalent, 260★, ships a CSV front end) | VERIFIED-AT-SOURCE |
| Auto-proposed checks shipping in a product | **LangSmith Engine** auto-proposing assertions from flagged production traces; **Braintrust Loop** generating scorers | PRIMARY-PAGE-READ |
| False-failure rate as a selection criterion | **SPADE Definition 3.2**, ILP with `Coverage ≥ α, FFR ≤ τ` | VERIFIED-AT-SOURCE |
| Evaluator-vs-human agreement shown in-product | **LangSmith alignment score** | PRIMARY-PAGE-READ |
| Mutation testing as an adequacy criterion at production scale | Google, arXiv:2102.11378 / IEEE TSE 2021 | VERIFIED-AT-SOURCE |
| **Spreadsheet mutation operators** — 17 of them, including `FRC` = "formula replacement with constant" | Abraham & Erwig, **IEEE TSE 35(1):94–108, 2009** | VERIFIED-AT-SOURCE |
| Degenerate-baseline discipline for a no-oracle detector — **hypergeometric random flagger, adjusted precision, "flags nothing" accounting** | **ExceLint**, OOPSLA 2018 (doi:10.1145/3276518) | VERIFIED-AT-SOURCE |
| Metamorphic relations derived from statute | arXiv:2205.04998, IRS Pub 596 / Sch 8812 / Form 8863, ICSE-SEIS 2023 | VERIFIED-AT-SOURCE |
| Deterministic adjudication of LLM output for a regulatory submission | **PROVE**, arXiv:2607.28218, **30 July 2026** | VERIFIED-AT-SOURCE |
| Fault-injection evaluation with paired clean/dirty packages | **PROVE**: 10 replicates × 15 injected discrepancies | VERIFIED-AT-SOURCE |
| LLM-authors-rules + deterministic execution, with the formalisation gap named | **"Confidently Wrong"**, arXiv:2607.23386, Jul 2026 | VERIFIED-AT-SOURCE |
| **An observability interface displaying the precision and recall of each constraint** | **Semantic Integrity Constraints**, Brown, arXiv:2503.00600 (Aug 2025) — **our predicate-library screen, in a database paper, a year early** | VERIFIED-AT-SOURCE |
| Completeness declared as a required enum with an explicit "not specified" state | **CycloneDX** `aggregateType` | VERIFIED-AT-SOURCE |
| Coverage as a shipped metric | **dbt-coverage** (MIT, 241★) — **coverage-as-presence**: which columns have a test | VERIFIED-AT-SOURCE |
| Declaring reasons you could not check | **ISA 705 ¶24 / ASA 705 ¶24**, and **ISRS 4400 ¶30(j)** | VERIFIED-AT-SOURCE |
| **A per-rule declared automatability boundary, in finance** | **ESMA ESEF `Automatable: Yes/No`** — 8 of 68 declared No, six of them `MUST` | MEASURED-HERE |
| **Authored severity per assertion, in finance, since 2016** | **XBRL Assertion Severity** REC 19 Apr 2016; **2.0** REC 21 Jul 2022 — `ERROR / WARNING / OK` | VERIFIED-AT-SOURCE |
| A rule author publishing that its own rules are wrong | **EBA quarterly deactivation list** — *"either for incorrectness or for triggering IT problems"* | VERIFIED-AT-SOURCE |
| A false-positive-gated, publicly-reviewed rule registry over regulated financial filings | **XBRL US DQC** — 6,309 commits, Xule on Arelle, *"Every draft rule is tested by running it against historical corporate filings… because the risk is too high that a filer will be led astray"* | VERIFIED-AT-SOURCE |
| Signed attestation over an artifact | in-toto / Sigstore / SLSA VSA | VERIFIED-AT-SOURCE |
| Authored statements of out-of-scope use | Model cards | SECONDARY |

## 6.2 The claim, narrowed to what survives

**Five things. Four of them are joins rather than inventions, and §6.3 argues why the join is the
contribution.**

**N1 — A permanent predicate registry in which *measurement is the admission condition*.**
Not *"we measured our rules"* — **a rule with no measured error rate is not representable**, because
`qualification` is a required field of the record and a predicate without it does not load. Nothing
in the 21 opened products, in SPADE, in PROVE, in the audit standards, in XBRL US DQC, or in the EBA/
EIOPA/ESMA rule sets has an admission gate of this shape. **The closest existing thing is the EBA's
decade-old convention that "new validation rules are introduced as warnings initially" — which is a
qualification gate with the measurement removed**: a rule earns blocking status by surviving
production without complaint. We propose it earn admission by surviving a seeded-defect harness and a
clean corpus **with the number written down**. That is the whole delta, and it is real.

**N2 — The per-rule FFR rendered on the verdict surface, next to the failure it caused.**
*"This check fired on 2.1% of 96 blind-filled filings [0.6%–7.4%]."* SPADE computes the number and
consumes it internally; the DQC gates for false positives before publication and publishes no rate;
ESMA and XBRL publish **authored severity**, which is intent, not evidence; **no product opened
displays a per-rule error rate to whoever must act on the alert.**

**N3 — Non-settlement as a typed, closed-vocabulary, per-field, *computed* output for a financial
artifact.** ISA 705 has the concept in prose, on modification, once per engagement. XCCDF has the
per-item vocabulary but its target is a host and its denominator is an authored benchmark. ESMA's
`Automatable` is a static property of the **rulebook**. CycloneDX's enum is an inventory roll-up.
**The join — per-field, per-predicate, with reasons, computed from an induced denominator, in
finance — is empty across everything searched.**

**N4 — The residue set: a measured boundary rather than a hand classification.**
Not *"how many predicates settled"* but **"which falsehoods survive every check we have, on this
filing."** It is adversarial, so boring checks cannot inflate it; it is reproducible, so a third
party can re-run it and get the same answer; and it is the direct measurement of the boundary the
problem statement says exists nowhere. **It replaces 17/24 with something that can be wrong in
public.** *(And it is the reason the third mutant class — factually wrong, internally perfect,
provably unkillable by any predicate over the artifact alone — is a first-class output rather than a
denominator nuisance.)*

**N5 — `INVALID`: a run-time proof that the checker was alive, on this document.**
Every report replays each predicate's stored kill-witness against the artifact just cleared, in the
same execution, and refuses to certify if any predicate fails to fire on a fault it is known to
detect. **The nearest named prior art is SRE synthetic monitoring and hardware built-in self-test —
not anything in the testing or assurance literature.** Given that the strongest evidence in this
whole corpus is five deterministic programs producing confident wrong answers, **this state is not
optional.**

**Binding all five: N1–N5 are signed together against the template hash, the filing hash, the register
snapshot hash and the predicate-set Merkle root**, so the boundary is auditable by a third party and
cannot be restated later. **No financial analogue found.**

**The one-line version, for a slide:**

> **Everyone ships rules. Nobody ships each rule's error rate, and nobody ships the residue. We make
> both a product surface, and sign them.**

**And the honest framing that makes it defensible to a professional rather than to a novice:**

> The assurance profession already knows how to declare the boundary of what was examined — ISRS 4400
> (Revised) ¶30(j) requires the statement in every agreed-upon-procedures report, and ISA 705
> (Revised) ¶24 requires the auditor to state the reasons for any inability to obtain evidence. What
> does not exist is a version of that declaration that is **(i) per-item** rather than per-report,
> **(ii) machine-readable** against a closed vocabulary rather than prose, **(iii) computed from an
> independently-induced denominator** rather than negotiated in advance with the engaging party, and
> **(iv) carried alongside a measured error rate for each individual check.** **ISRS 4400 ¶30(h)
> makes the point for us: the practitioner expressly makes no representation about whether the
> procedures were the right ones. Our qualification gate is a machine-checked answer to exactly that
> disclaimed question.**

## 6.3 Why the assembly is itself the contribution

The argument has to be structural, not rhetorical, and here it is: **each part, alone, is defeated by
a measured fact in §3.0. The parts are chosen so that each one's failure mode is another one's
input.**

- **SPADE alone fails on F3 and on its own admission.** Its FFR needs labelled data, and the paper
  states plainly that *"coverage and FFR are impossible to compute since the universe of examples 𝐸
  is unknown"*, falling back to a manually provided subset averaging **34 bad examples per task**.
  → **Seeded defects supply labelled dirty data by construction, at arbitrary n, with certain ground
  truth. The seeded fault *is* the label.** This is the load-bearing join and it is the reason the
  architecture is not a mashup.
- **Seeded-defect adequacy alone fails on F9.** It measures whether a check can fire; it says nothing
  about the seven predicates with no oracle. → **Differential and invariant relations settle a subset
  of those without an oracle**, so the boundary becomes a *measured, movable* quantity rather than a
  philosophical limit — **while honestly moving ~0 of the 7 and saying so.**
- **Relations alone fail on F2.** A relation can be trivially satisfiable or trivially violated;
  unqualified, it lands on the degenerate operating point where a flag-everything classifier beats
  the state of the art. → **The non-degeneracy gate rejects it**, and it would have rejected the
  currency round-trip automatically.
- **All of them together still fail on F4** — 45–76% of agent failures are false successes and a
  model judge detects them at AUROC ≤0.65 — **unless the residue is emitted.** A system that silently
  drops what it could not check has produced a false success by definition. → **The closed reason
  vocabulary and the computed residue are the only outputs that make a false success structurally
  impossible to render, because there is no green tick to render.**
- **And the whole thing is worthless without F7** — `pass^k` collapse and `0.9⁸ = 0.4305` — which is
  why there is **no agent loop**, why the model runs at build time only, and why **the registry, not
  the model, is the durable asset.**

**The test of whether an assembly is a contribution: can you remove one part and keep the claim?**
Remove seeded defects → FFR is uncomputable and the gate is decorative. Remove the gate → the
settled fraction is an assertion and we are an incumbent with better copy. Remove the relations →
coverage is a ceiling, not a growth curve, and the demo has no second act. Remove the reason
vocabulary → it is a linter. Remove the self-check → we are the thing we are selling against.
**No part is removable. That is what makes it a design rather than a stack.**

## 6.4 The three strongest objections, and the exact rebuttals

---

### Objection 1 — *"This is SPADE. Berkeley published it in 2024, LangChain shipped it, 2,000+ pipelines. You have re-skinned an existing product."*

**The most dangerous objection, because the brief itself said "Reuse SPADE."** Concede the reuse
immediately, then be more precise about SPADE than the objector is. Four points, all read off the
PVLDB PDF:

1. **The criterion source is different, and a regulation cannot supply SPADE's.** SPADE mines
   *prompt-version deltas*: *"developers implicitly embed data quality requirements through changes
   to the prompt."* **A regulation has no prompt-diff history.** Our criterion source is statutory
   clause units plus the template's own formula graph. *(And we downgrade our own claim honestly:
   that source is **available**, not **authoritative** — `'1. Introduction'!D17` proves a predicate
   mined from the template's formula would pass a wrong filing and fail a right one.)*
2. **SPADE's own paper says its central metric cannot be computed in general** — *"coverage and FFR
   are impossible to compute since the universe of examples 𝐸 is unknown"* — and its tasks average
   **34 bad examples**. **Seeded-defect adequacy is the answer to the sentence SPADE could not
   answer.** That is not a re-skin; it is the missing input.
3. **What shipped is not what the objection claims.** The public release with LangChain is
   *"this component"* — **Component 1, candidate assertion generation** — delivered in **November
   2023 as an early prototype via a Streamlit application**, and the "2,000+ pipelines" attaches to
   that generator. **Today, the LangChain documentation index carries 57 evaluation-related lines and
   `grep -ci spade` returns 0 and `grep -ci "false failure"` returns 0**; `assertions.md` describes
   assertions **written by a human reviewer**. What LangSmith actually ships is an **alignment
   score** — *"the percentage of examples where the evaluator's judgment matches that of the human
   expert"* — which is aggregate agreement against human labels, computed privately, **non-gating**.
   And **the Streamlit prototype is no longer publicly reachable** (it 303-redirects into a login
   loop that exhausts 50 redirects).
4. **SPADE has no residue.** It selects a set of assertions. **It never emits what it could not
   assert.** The reason vocabulary and the computed settled fraction have no counterpart in the paper
   or the product.

**Do not use the "finance is one prompt in twenty-four" closer.** It is arithmetically derivable from
Figure 5 and **it is a misreading**: the paper's body frames that chart as a breakdown of the 2,000+
deployment runs, not of a 24-item sample. A judge holding the PDF turns it into *"you misread a
figure to make your competitor look small"* and discounts everything else. **The defensible
replacement, which is enough:** *SPADE's evaluation set contains one finance pipeline —
summarising earnings-call transcripts, with examples from Kaggle — and no regulated filing anywhere
in the paper.*

---

### Objection 2 — *"Auditors have declared what they couldn't check for decades. ISA 705. Qualified opinions. You have rebuilt the audit report."*

**Concede the concept loudly — it is our best legitimising precedent — then show three places it
fails.**

1. **It fires only on modification.** ¶20 begins *"When the auditor **modifies** the opinion…"* and
   ¶24 conditions on *"**If** the modification results from an inability to obtain sufficient
   appropriate audit evidence…"* **An unmodified opinion carries no statement of what was not
   checked. The clean audit report is the canonical silent all-clear** — the exact artifact this
   project exists to abolish. **The standard declares the boundary only in the cases where the
   boundary was already conceded.**
2. **The mechanism demonstrably fails to fire when it should, at a measured rate.** **20% of
   *inspected* Big Four US audits in 2024 carried a Part I.A deficiency** (26% in 2023). In one
   inspected engagement in five, the evidence was insufficient **and the opinion was issued anyway.**
   *(Keep the word **inspected** permanently attached: PCAOB selects risk-targeted, not at random.
   And note the 2022 figure and the deficiency definition are **SECONDARY**, and that a
   re-verification pass could not reach pcaobus.org — **open the release and fix both before this is
   said out loud.**)* **A declaration that depends on a human noticing they should declare is not a
   coverage guarantee; it is a hope.** Ours is produced by a schema constraint: a predicate whose
   error rate is unknown cannot be represented, so it appears in the residue **automatically rather
   than by anyone's virtue.**
3. **It is prose, per engagement, with no rate and no arithmetic.** ¶20(b) asks for *"a description
   of the matter giving rise to the modification"* — a paragraph, in English, once per audit, naming
   no procedure, carrying no false-positive rate, yielding no fraction. **You cannot sort 868 filings
   by it. You cannot diff it between quarters. You cannot verify it cryptographically.**

**One-line form:** *ISA 705 declares the boundary when the auditor already knows they hit one. We
declare it every time, per field, as a number, whether or not anyone noticed.*

**And the sharpest single sentence available, which comes from the standard that is otherwise our
closest competitor:** ISRS 4400 ¶30(h) requires the practitioner to state that they **make no
representation regarding the appropriateness of the agreed-upon procedures.** *The profession's most
coverage-honest report form disclaims the one question our qualification gate answers with a number.*

---

### Objection 3 — *"Reg-reporting vendors ship thousands of validation rules. The EBA publishes twelve thousand. This is a mature, crowded category and you are late."*

**Concede the crowding immediately — and delete the brief's false version of this claim first.**
*"Zero financial regulations encoded anywhere"* is wrong and checkable in ninety seconds by anyone in
a GIFT City room who has worked in regulatory reporting. Then attack the metric, in five steps:

1. **The category competes on rule count and regime count, and those are the wrong axes.** Every
   vendor page opened states counts, never quality: *"40+ countries, 90+ regimes"*; *"850+ pre-coded
   global rules… 100+ jurisdictions"*. The most complete public validation catalogue found anywhere —
   ~25 named validation families over exactly our artifact class — publishes **no false-positive
   rate, no detection rate, and no declaration of what the oversight cannot check.**
2. **The rule authors themselves publish that their rules are wrong.** The **EBA deactivates
   validation rules quarterly *"either for incorrectness or for triggering IT problems"*** and
   instructs authorities that submissions *"should not be formally validated against the set of
   deactivated rules."* **1,692 of 20,562 rules in release 3.5 have been deactivated at least once
   (8.23%); 1,008 are still off; 343 of those were hard-blocking `error` severity; and it is still
   happening — 205 in 2024, 94 in 2025, 27 by mid-2026.** **If a rule count were a quality signal,
   the EBA would not need a kill-list.** This is simultaneously the strongest external evidence that
   the missing quantity is real and the cleanest statement of what it costs to find out from the
   field: **L4 is the proposition that you can find out before you ship.**
3. **On the actual target artifact, the incumbent rule inventory is not thousands.** MEASURED-HERE on
   the prescribed FME return: **505 formula-bearing cells, of which 138 (27.3%) express a checkable
   relationship and 223 (44.2%) copy a value**; the IBU Operations Report has **7 formulas across
   961 cells**; two of the nine prescribed workbooks contain **zero formulas**, and one of those has
   **zero data validations as well** — a typed form with no internal consistency structure at all.
   **Coverage is a per-template property and must never be averaged across the corpus.**
4. **Count says nothing about the residue.** Of 24 candidate correctness predicates on this return,
   **15 are exactly settleable, 2 approximately, and 7 not at all** — and none of the 17 addresses
   any of the 7. **A vendor with 10,000 rules and no residue declaration is asserting, by silence,
   that the 7 do not exist.**
5. **We are not competing with the category; we are supplying the column it does not have.** The
   natural end state is that a predicate registry carrying kill rates and FFRs is something an
   incumbent would want to *consume*. **That is a better answer to "crowded category" than claiming
   they are all wrong.** And the seat matters: the **supervisory** seat at IFSCA is already procured
   (NEC, 27 Jan 2026, ₹39.57 crore, RE-facing portal in scope). **We are in the filer's seat, and we
   say so early.**

---

### Three further objections that are cheap to raise and must not be met unprepared

**3a — *"XBRL assertions have carried severity since 2016."*** True: XBRL **Assertion Severity**
(REC 19 Apr 2016; **2.0** REC 21 Jul 2022) defines exactly three levels — `ERROR / WARNING / OK` —
assignable statically or by expression, and it was **missed by one lane's search and caught by its
adversarial pass**, which is itself instructive. **The rebuttal is one line and it is strong:**
*severity is declared by the rule's author before anyone runs it; a false-failure rate is measured
against a corpus after. One is intent, the other is evidence — and the EBA's own deactivation list is
what happens when you only have the first.*

**3b — *"MindBridge already does 100% coverage: Full Population Analysis."*** **Population coverage is
not predicate coverage.** Scoring every transaction against a fixed set of models answers *"which
rows look unusual."* It does not answer *"which correctness propositions about this filing have been
settled, and which cannot be."* The product publishes **no false-positive rate and no declaration of
analytical limitations**, and a risk score over 100% of rows with an unknown error rate is exactly
the operating point F1 and F2 rule out.

**3c — *"PROVE already published your thesis, eleven days ago."*** **Cite it yourself, first, on the
slide that states the thesis.** *"LLM interprets, programs adjudicate, for a regulatory submission"*
is **no longer novel** as of 30 July 2026, and independent convergence in a different regulated
industry is **corroboration, not a threat**. What PROVE leaves is precisely our five claims: it
reports **aggregate recall and F1 over 150 injected discrepancies with no per-check rate**; its own
hedge — ***"Within the implemented rule classes"*** — is a **prose caveat where ours is a computed,
typed, per-field output**; it has **no admission gate**, so nothing prevents a validator with a
terrible FFR from being in the set; and it has **no relation layer**. *(Its full text was not read —
only the abstract. **Read it before the pitch**, because its "implemented rule classes" section may
contain a coverage table that narrows N3.)*

**And one governance fact worth having ready, because it converts a gap into an opening:** the US
model-risk regime was rewritten on **17 April 2026** (SR 26-2, superseding SR 11-7, applying to
banking organisations over **$30 billion** in total assets), and **footnote 3 states verbatim that
generative and agentic AI models *"are not within the scope of this guidance"***, with the fallback
that *"a banking organization's risk management and governance practices should guide the
determination."* **There is now a named, dated, official governance vacuum around exactly the kind of
model our build-time layer contains — and a predicate registry with measured error rates is a
concrete answer to a question a US supervisor has just formally declined to answer.** The same
letter's own validation vocabulary — *Conceptual Soundness* and *Outcomes Analysis*, defined as
*"compares model outputs to corresponding real-world outcomes"* — is precisely the language the
qualification gate implements.

## 6.5 What would falsify the novelty claim

**Stated now, so that it can be checked rather than argued.** Any one of these ends N1–N5 as written:

1. **A shipping product or published system that displays a per-rule measured false-failure rate,
   with a denominator, next to the finding that rule produced.** *(20+ named vendors were never
   opened — AxiomSL/Nasdaq, Wolters Kluwer OneSumX, Corlytics, Vermeg, Ascent, Clausematch, Hexanika,
   Gresham, SS&C, Northern Trust, BNY, Trullion, Caseware IDEA, Klarity, AuditBoard, Basis, Bluecopa,
   Patronus, Arize Phoenix, Evidently, Giskard, Ragas, Soda, Sifflet, Bigeye, and all Big Four
   in-house tools. **Any of them could publish one and we would not know. This is the largest single
   weakness in the novelty claim and it must be re-run with a working search budget before the claim
   goes on a slide as an absolute.**)*
2. **A regulator publishing a per-rule misfire rate** rather than a binary deactivation list. ESMA's
   rejection rates (1–2.5%) are a *submission* statistic, not a *rule* statistic; the EBA's list is
   binary and post-hoc. **Whether any regulator anywhere publishes one is UNRESOLVED.**
3. **A system computing a per-filing residue** — which falsehoods survive its own check set on this
   document — rather than a static automatability flag on its rulebook.
4. **A financial assertion signed together with a coverage denominator.** CycloneDX permits a
   signature over a composition; no financial analogue was found across the opened set.
5. **Prior application of learn-then-test-style multiple-hypothesis control to test-suite or rule-set
   admission.** Our gate selects a configuration (which predicates to admit) by testing many
   candidates on shared data — that **is** multiple testing over a grid, with kill rate, degeneracy
   and FFR as three risks. **If nobody has framed rule admission that way, it is a genuinely
   publishable connection — and it is UNVERIFIED as novel because nobody searched for it.**

**And the two facts that would most change what we should build, both currently UNRUN:** whether
IFSCA already runs these checks on receipt, and whether a fund administrator serving GIFT IFSC has a
written house NAV tolerance (§1.9).

## 6.6 The honest ledger, in one paragraph

**What is borrowed:** the generate-then-adjudicate thesis (PROVE, "Confidently Wrong"); assertion
synthesis and FFR-based selection (SPADE); mutation adequacy and its suppression discipline (Google);
the spreadsheet fault taxonomy (Abraham & Erwig); the hypergeometric degenerate baseline and adjusted
precision (ExceLint); relations from statute (the tax-preparation work); the nine-state per-item
vocabulary and the denominator asymmetry (XCCDF); the bounded-silence sentence, the objective-
verifiability definition and the two-party report model (ISRS 4400); the aggregation 2×2 and the
"possible effects" distinction (ISA 705); the experienced-auditor test and the counter-evidence
requirement (PCAOB AS 1215); three-way status classification and mandatory skip-declaration (C2PA);
the absent-vs-empty rule (SLSA, SPDX); the inconclusive sentinel and its distinct rendering
(Scorecard); the closed-world terminal deny (in-toto); the completeness enum, the self-assessor flag
and the JSON-Pointer citation idiom (CycloneDX); the POA&M model, the planned-vs-actual scope delta
and the machine-vs-human actor type (OSCAL); the rule-admission governance process (XBRL US DQC); the
warnings-first probation convention (EBA); the automatability boundary (ESMA); the declare-your-own-
parameter design (SEBI 2.9.3.1(vii)); the ex-ante published boundary and the annual base rate (CSSF
24/856); and the language, the profile and the in-process policy precedent (CEL, Kubernetes
ValidatingAdmissionPolicy). **What is new is five things — measurement as the admission condition,
the per-rule error rate on the verdict surface, the computed typed residue, the residue set as a
measured boundary, and a run-time proof that the checker was alive — bound together by a signature
over an induced denominator.** **What is unmeasured is whether anyone needs it**, and the two calls
that would settle that are one email and one phone call, both unrun, both ranked joint-first.

---

*End of Section A. The predicate registry schema, the qualification harness and the report renderer
are specified for build in Section C; the experiment queue and its pre-registered thresholds are in
Section B.*
