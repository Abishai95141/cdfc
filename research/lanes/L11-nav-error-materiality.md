# L11 — NAV error, materiality thresholds and the boundary of a valuation verdict

**Lane:** ground the domain. Establish what the rest of the world actually does about NAV errors, so the
IFSCA gap can be stated precisely, and judge whether that gap is the sharper wedge or a distraction.

**Run 10 August 2026.** Every number below carries its warrant and its denominator. Where a source
refused to open, that is stated as NOT-FOUND, not smoothed over.

**Warrant key** — `VERIFIED-AT-SOURCE` = I opened the primary document and read the clause off the page ·
`SECONDARY` = a credible source describes it, I did not reach the primary · `UNVERIFIED` = could not
confirm · `DERIVED` = arithmetic on stated inputs, never stronger than its weakest input.

---

## PART 0 — METHOD, AND WHAT I COULD NOT OPEN

**Instruments actually opened and text-extracted this lane** (all with `pdftotext -layout`, greps run
over the extraction, positive controls declared alongside every absence):

| Instrument | Pages / lines extracted | Source |
|---|---|---|
| Circular CSSF 24/856 (EN) | 47 pp / 2,622 lines | `https://www.cssf.lu/wp-content/uploads/CSSF24_856eng.pdf` |
| CSSF Annual Report 2024 (EN) | 8,875 lines | `https://www.cssf.lu/wp-content/uploads/CSSF_RA_2024_EN.pdf` (on disk at `lane_fundops/cssf_ar2024.txt`) |
| CBI Consultation Paper 130 | 669 lines | `https://www.centralbank.ie/docs/default-source/publications/consultation-papers/cp130/cp130-treatment-correction-and-redress-of-errors-in-investment-funds.pdf?sfvrsn=5` |
| S.I. No. 316 of 2026 — Central Bank UCITS Regulations 2026 | 5,060 lines | `https://www.centralbank.ie/docs/default-source/regulation/industry-market-sectors/funds/ucits/s-i-316-of-2026---central-bank-(supervision-and-enforcement)-act-2013-(section-48(1))-(undertakings-for-collective-investment-in-transferable-securities)-regul.pdf` |
| FCA Handbook COLL 6.3 (live HTML) | 1,761 lines | `https://www.handbook.fca.org.uk/handbook/COLL/6/3.html` |
| ESMA 2022 CSA on Asset Valuation — Final Report (ESMA34-45-1802) | 976 lines | `https://www.esma.europa.eu/sites/default/files/2023-05/ESMA34-45-1802_2022_CSA_on_Asset_Valuation_-_Final_Report.pdf` |
| SEBI Master Circular for Mutual Funds as on 20 Mar 2026 | 748 pp / 35,350 lines / 1,291,125 chars | `https://www.sebi.gov.in/sebi_data/attachdocs/mar-2026/1774024028162.pdf` |
| IFSCA (Fund Management) Regulations 2025, amended up to 30 Jan 2026 | 102 pp / 3,963 lines | `https://ifsca.gov.in/Common/PreviewPdf?id=91427247c5628a865846d173bc1f61aa&fileName=IFSCA__Fund_Management___Amendment__Regulations_2026__Amended_up_to_January_30__2026_20260507_0802.pdf` |
| IFSCA FM FAQ, 3 Aug 2026 | 68 pp / 2,3xx lines | `https://ifsca.gov.in/Common/PreviewPdf?id=29709e474fe6b066fc0cb19f7daba881&fileName=FAQs_for_website_final_20260803_0125.pdf` |
| K&L Gates, *Mutual Fund Pricing and Fair Valuation*, DC IM Conference 7 Nov 2018 | 330 lines | `https://files.klgates.com/files/uploads/documents/2018_im_conf/dc_im_2018_session_viib.pdf` |
| Ignites, *Calculating NAV Is Hard. More Funds Got It Wrong in 2022*, 3 Mar 2023 | — | `https://www.fundguard.com/wp-content/uploads/2023/06/Ignites_Calculating-NAV-Is-Hard.pdf` |
| The FME quarterly workbook itself (OOXML, raw ZIP) | 10 sheets | `scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` |

**Refused to open — record these as coverage holes, not as absences:**

- **iosco.org returns HTTP 403** to every fetch. Both `IOSCOPD824.pdf` and `IOSCOPD413.pdf` returned 403.
  A previous lane's downloads at `lane_fundops/iosco824.pdf` and `iosco797.pdf` are **Cloudflare HTML
  challenge pages, not PDFs** (`head -c 300` shows `<!DOCTYPE html>`). **Do not cite an IOSCO document
  number from this corpus.** The IOSCO principle below is quoted at one remove, from the Central Bank of
  Ireland.
- **eCFR (`ecfr.gov`) 302-redirects to `unblock.federalregister.gov`**; **sec.gov returns 403**. US rule
  text below is from Cornell LII, which is a faithful mirror but is not the eCFR.
- **The exact Form N-CEN item number for NAV errors is NOT-FOUND.** sec.gov 403; eCFR blocked; Cornell
  17 CFR 274.101 incorporates the form by reference and does not reproduce it; two DuckDuckGo queries
  returned zero results. The *existence* of the item is SECONDARY only.
- **CSSF Annual Report 2025 is not published** as of 10 Aug 2026 (the `cssf.lu/en/Document/annual-report-2024/`
  page carries no 2025 link; AR2024 itself was published 28 Aug 2025). So the 2024 figures below are the
  latest, and they are the **last cohort measured under the old circular**.
- **WebSearch budget was exhausted at 200/200 calls** early in this lane. Everything after that point was
  done with direct `curl`/WebFetch on constructed URLs plus DuckDuckGo HTML. Absences found via
  DuckDuckGo are weak and are labelled UNVERIFIED throughout.

---

## PART 1 — LUXEMBOURG: THE REFERENCE IMPLEMENTATION

`VERIFIED-AT-SOURCE` — every quote below read off the 47-page English PDF.

### 1.1 The instrument

**Circular CSSF 24/856**, *Protection of investors in case of an NAV calculation error, an instance of
non-compliance with the investment rules and other errors at UCI level*. Dated **Luxembourg, 28 March
2024**. Point 162: *"This Circular enters into force with effect from 1 January 2025. UCIs must apply the
guidelines of this Circular to any error/non-compliance detected as from 1 January 2025."* Chapter 10
repeals **Circular CSSF 02/77**.

Scope (points 1–4): UCITS, UCIs Part II, SIFs, SICARs in their entirety; Luxembourg ELTIFs, MMFs,
EuVECAs and EuSEFs that are not UCIs Part II/SIFs/SICARs (including RAIFs) **in their entirety except
Chapter 8** (auditor intervention).

### 1.2 The thresholds — the actual numbers

Point 35. **Table 1 — MMFs governed by the MMFR: 0.20% of NAV.**

Point 35(b). **Table 2 — UCITS (except MMFs):**

| Principal investment policy as defined in the constitutive documents and/or prospectus | Tolerance threshold (in % of NAV) |
|---|---|
| UCITS which invest primarily in bonds and/or other debt securities ("bond UCIs") | **0.50%** |
| UCITS which pursue a mixed investment policy ("mixed UCIs") | **0.50%** |
| UCITS which invest primarily in shares and/or other securities equivalent to shares ("equity UCIs") | **1.00%** |
| UCITS which invest primarily in other eligible assets for a UCITS | **1.00%** |

Point 35(c). **Table 3 — UCIs Part II (except MMFs) and ELTIFs whose units can be held by investors that
are *not* well-informed or professional:** identical structure — bond 0.50%, mixed 0.50%, equity 1.00%,
other assets 1.00% (*"'Other assets' refer, for example, to unlisted shares, buildings, loans or eligible
investments for ELTIFs."*). A derogation above 1% is available for the "other assets" line *"if the
characteristics of the UCI, including its risk profile justify it. A specific well-documented analysis
must be the basis"*, plus investor notification.

Point 35(d). **Part II/ELTIFs reserved to well-informed or professional investors, SIFs, SICARs, EuVECAs,
EuSEFs:** self-determined, against five mandatory considerations (open/closed-ended type and dealing
frequency; investment policy; nature of investments listed/unlisted; risk profile incl. liquidity, market,
credit risk and volatility; valuation policy), with Table 3 as an explicit reference point, and a hard cap:

> *"The tolerance threshold must not exceed 5% of the NAV. In no case are UCIs permitted to use by default
> the 5%-threshold, knowing that the tolerance threshold must, in accordance with the above-mentioned
> conditions, be established subject to a specific analysis..."*

Point 36 allows lower thresholds *"applied on a consistent basis over time."*

**What changed from 02/77.** The one threshold I can compare directly is MMFs: **0.25% under 02/77 →
0.20% under 24/856** (`SECONDARY` — from multiple law-firm briefings; I could not open the 02/77 PDF, the
CSSF URL I constructed returned 404, and I did not find a working link before the search budget expired).
The 0.50%/1.00% bond/mixed/equity tiers are widely described as carried over from 02/77 but I did not
verify that at source, so **treat "the percentages are unchanged for non-MMFs" as UNVERIFIED**. What is
`VERIFIED-AT-SOURCE` is that 24/856 *extended scope* (SIFs, SICARs, ELTIFs, EuVECAs, EuSEFs, RAIFs) and
added four new error classes that 02/77 did not cover: **incorrect application of swing pricing (6.1),
non-compliant payment of costs/fees at UCI level (6.2), incorrect application of cut-off rules (6.3), and
investment allocation errors (6.4)**.

### 1.3 The application rules — this is the part that is actually machine-shaped

Point 37 is a set of six deterministic disambiguation rules, and they read like a specification:

- **(i)** umbrella UCI → threshold determined **per sub-fund**; where a sub-fund has several classes,
  **a single threshold applies to all classes**.
- **(ii)** the threshold must be fixed, documented, **before the first NAV is published**.
- **(iii)** the investment objective and policy *"as laid down in the constitutive documents and/or the
  prospectus, must be used as a reference"*. — the classifier's input is a named document, not a judgement.
- **(iv)** fund-of-funds, index-tracker, feeder → threshold **by reference to the target UCIs' principal
  investment policy** (or the index's principal composition). Same for UCIs implementing policy mainly
  through derivatives.
- **(v)** cross-border: the default is the Luxembourg threshold, **but a more restrictive threshold
  required by a marketing jurisdiction wins, and then applies to the whole sub-fund and all investors
  regardless of origin.**

Point 38 carries the **aggregation rule**, and it matters for L6:

> *"Significant NAV calculation errors are to be understood not only as isolated calculation errors which
> have a significant impact on the NAV but also as simultaneous or successive calculation errors which
> have not been treated and were each below the tolerance threshold and which, if considered on an
> aggregate basis, reach or exceed that threshold."*

Point 39: *"The remediation of any loss is only compulsory for the dates on which NAV calculation errors
were significant."*

### 1.4 Compensation mechanics

Points 41–47. The direction of compensation is a two-by-two, stated as Tables 4 and 5:

| | Investors | UCI |
|---|---|---|
| **NAV undervalued** (Table 4) | investors who **redeemed** during the error period are compensated for corrected NAV − undervalued NAV on the redeemed units | the UCI is compensated for the difference on units **subscribed** during the error period |
| **NAV overvalued** (Table 5) | investors who **subscribed** during the error period are compensated for overvalued NAV − corrected NAV on the units subscribed | the UCI is compensated for the difference on units **redeemed** during the error period |

Point 44: clawback from an investor who involuntarily benefited is permitted *"when it is a
well-informed/professional investor"*; for others *"it is, in principle, not appropriate."* Point 45 allows
netting across an investor's transactions provided the same final beneficiary can be established. Point 47:
the financial impact may be determined by the **compound** method (each NAV corrected for the direct effect
*and* the indirect effect of cumulative subs/reds struck at an erroneous NAV) or the **non-compound**
method.

**De minimis** (7.2.2, points 123–127): the de minimis is **not a regulator-set number**. It is set *per
UCI or per sub-fund*, justified by *"the level of bank charges and other fees which are charged to
investors due to a payment by bank transfer"*, and must be documented in the UCI's internal policy. And
critically, point 127:

> *"For compensation to be paid out to the UCI, the de minimis rule is not applicable. As a consequence,
> all compensation amounts due to an UCI following an error/non-compliance must be paid out, unless that
> amount is lower than one monetary unit."*

Point 128–129: compensation by **allocation of additional units** avoids bank charges and *"permits full
compensation as it is carried out without applying the de minimis rule."*

7.3 (points 130–132): un-payable compensation to former investors goes to the **Caisse de consignation**
under Article 1(2) of the Law of 29 April 1999.

7.4 (points 133–135): *"The fees resulting from the corrective actions of an error/non-compliance must not
be borne by the UCI and must thus not be withdrawn from its assets"*, and *"must also not be indirectly
recharged to the UCI through the increase of costs/fees to be borne by the UCI."*

### 1.5 The auditor trigger — the only euro amounts in the circular

Point 138. The CSSF requests an **additional control** by the *réviseur d'entreprises agréé* (REA),
resulting in a **special report** to the UCI's dirigeants and to the CSSF, where **both**:

- the error/non-compliance relates to a **UCITS or a UCI Part II**; **and**
- **the total compensation amount exceeds EUR 50,000, or the compensation to be paid to one single
  investor exceeds EUR 5,000.**

> *"In order to determine the 'total compensation amount' for the purposes of applying the EUR 50,000
> threshold, both the compensation paid out to the UCI and the compensation paid out to all investors
> should be taken into account."*

Point 140: if the REA detects the error and the dirigeants do not act, the REA must notify the CSSF at the
latest with its management letter — and **immediately** where the inaction *"may adversely affect the
rights of the UCI and/or its investors."*

### 1.6 Notification — including the part everyone gets wrong

Chapter 9. Every error/non-compliance is notified on a **specific form** published on the CSSF website.
Point 154: *"A quantitative impact calculation allowing the CSSF to trace how the impact ... was determined
must be attached to the notification."* Point 155: *"The CSSF refuses incomplete notifications."*

Point 158 — the **deadline is 4 to 8 weeks after detection**, not after correction:

> *"for an error/non-compliance which does not entail the payment of compensation to investors, the
> deadline for notification is 4 to 8 weeks at the latest after the date on which the error/non-compliance
> has been detected. More complex errors/instances of non-compliance which imply compensation to a great
> number of investors in different jurisdictions must be reported to the CSSF within the above deadlines,
> without mandatorily including the date the investors are compensated."*

Monthly progress reporting thereafter. Point 157: REA special report to the CSSF *"in principle, within 3
months as from the date of submission of the complete notification form."*

Point 159 is the one people misread: *"the corrective actions indicated in the notification form by the UCI
are **not subject to the CSSF's approval**. Therefore, the CSSF will not provide specific feedback."* This
is a **declaration regime, not an approval regime** — which is exactly the shape a coverage-declaring
verifier fits into.

### 1.7 The base rate Luxembourg publishes — and nobody else does

`VERIFIED-AT-SOURCE`, CSSF Annual Report 2024, §4.1.2 and §1.2.

| Quantity | 2022 | 2023 | 2024 |
|---|---:|---:|---:|
| **NAV calculation errors declared** | **462** | **344** | **234** |
| Instances of non-compliance with investment rules declared | 1,382 | 1,265 | 1,297 |
| Total declarations under Circular CSSF 02/77 | — | **1,609** | **1,531** |
| "Normal procedure" notifications (compensation exceeding 02/77 thresholds) | — | 148 | **107** |
| Total compensation following NAV errors — **investors** (EUR) | 21,187,863.80 | 49,601,054.10 | **11,810,270.57** |
| Total compensation following NAV errors — **UCIs/sub-funds** (EUR) | 26,901,611.60 | 14,109,720.70 | **8,571,914.50** |

Denominators, as at 31 December 2024 (CSSF AR2024 §1.2): **3,143 UCIs on the official list · 13,599 fund
units · EUR 5,820 bn net assets.**

Arithmetic check: 234 + 1,297 = 1,531 ✓ (matches the stated total).

`DERIVED` — and no stronger than the inputs:

- **234 / 13,599 = 1.72% of Luxembourg fund units had a declared NAV calculation error in 2024.**
  *(Flow-over-stock: declarations during 2024 against the unit count at 31 Dec 2024.)*
- 234 / 3,143 = **7.44% per registered UCI**.
- 107 / 1,531 = **6.99%** of all declarations went through the "normal" (full compensation) procedure
  rather than the simplified one.
- Total NAV-error compensation 2024 = 11,810,270.57 + 8,571,914.50 = **EUR 20,382,185.07**, which is
  **0.00035% of EUR 5,820 bn** in net assets. CSSF's own wording: *"the total amount of compensation still
  remained moderate as compared to the total amount of assets under management."*
- Mean ≈ **EUR 87,103 per declared NAV error** (20,382,185.07 / 234). **MODELED, not measured** — the
  compensation totals are a payment flow that may relate to errors declared in earlier years.

**Critical caveat that must travel with every one of these numbers:** 2024 declarations were made under
**02/77**, whose thresholds differ (MMF 0.25% vs 0.20%) and whose scope excluded SIFs, SICARs and the four
new error classes. **The 2025 cohort will be the first under 24/856 and is not yet published.** Any
statement of the form "the NAV error rate is 1.72%" is a statement about Luxembourg, in 2024, under the
old circular, for declared significant errors only.

---

## PART 2 — IRELAND: THE COUNTER-EXAMPLE THAT KILLS THE EASY PITCH

This is the single most important finding in the lane, because it destroys the framing "every serious
fund jurisdiction has a NAV-error regime and IFSCA is behind."

### 2.1 What was proposed, in 2019

`VERIFIED-AT-SOURCE` — CBI **Consultation Paper 130**, *Treatment, Correction and Redress of Errors in
Investment Funds*, published **9 September 2019**, closing **9 December 2019**.

Proposed quantitative thresholds, stated identically twice (main text and "Proposed Approach"):

| | Threshold |
|---|---|
| Money Market Funds (MMFs) | **0.10% of NAV** |
| Other investment funds | **0.50% of NAV** |

Four error types: **NAV Error, Investment Breach Error, Fee Error, Control Breach Error**.

"Appropriately Rectified" = *"(i) identification and classification of the error (including assessing
materiality), (ii) correction of the error (including compliance with any reporting and notification
obligations) and (iii) redress of the error (including the payment of redress to the fund and / or
investors)"* — and the paper states this *"will be explicitly set out by way of an obligation in future
iterations of Central Bank UCITS Regulations and the Central Bank AIF Rulebook / AIF Regulations."*

The **industry** de minimis, quoted by the CBI: *"The industry standard De Minimis Limits currently applied
are **€50 for retail investors and €500 for institutional investors**."* The CBI's view: *"the current De
Minimis Limits appear excessive, particularly for institutional investors."*

Two footnotes in CP130 are worth more than the rest of the paper:

> Footnote 1 — *"IOSCOs Principles for the Valuation of Collective Investment Schemes - Principle 5: A CIS
> should have policies and procedures in place that seek to detect and prevent pricing errors. Pricing
> errors that result in a material harm to CIS investors should be addressed promptly, and investors fully
> compensated."*

> Footnote 2 — *"IMF: Detailed Assessment of Observance, IOSCO Objectives and Principles of Securities
> Regulation – Ireland, April 2014. Principle 27 page 27 – 'While there is industry guidance, the Central
> Bank has not issued rules prescribing how pricing errors are to be treated by CIS.'"*

And CP130's own description of the status quo: *"The representative body for the funds industry in Ireland
(Irish Funds) has longstanding guidance on the treatment and compensation of errors and breaches. **This
guidance has neither been sanctioned nor approved by the Central Bank.**"*

### 2.2 What actually happened — seven years later

`VERIFIED-AT-SOURCE`. I downloaded and grepped **S.I. No. 316 of 2026 — Central Bank (Supervision and
Enforcement) Act 2013 (Section 48(1)) (Undertakings for Collective Investment in Transferable Securities)
Regulations 2026**, the rebased Irish UCITS rulebook (published July 2026). Extraction: 5,060 lines.

| Pattern | Hits |
|---|---:|
| `materiality` | **0** |
| `toleran*` | **0** |
| `redress` | **0** |
| `rectif*` | 1 — regulatory-capital position of a management company, Reg 99(1) |
| `compensat*` | 2 |
| `error` | 7 — **all** either "tracking error" (definition at Reg 2, Reg 55-ish disclosure, Schedule items) or a client-funds *recordkeeping* error at Reg 100 |
| **positive control** `net asset value` | **37** |

**There is no NAV-error materiality threshold, no redress regime and no error-notification regime in the
current Irish UCITS Regulations.** CP130 was never converted into rules. The world's second-largest fund
domicile was told by the IMF in 2014 to publish rules, consulted in 2019, and as of the July 2026 rebase
still has none — Irish practice runs on **industry guidance the regulator has explicitly not approved.**

*Coverage note on the absence:* the grep denominator is the consolidated 2026 UCITS Regulations only. I did
**not** open the Central Bank AIF Rulebook, the CBI's UCITS Q&A (42nd edition), or the Irish Funds guidance
itself (member-gated). A DuckDuckGo `site:centralbank.ie` search for a CP130 feedback statement returned
only the consultation paper page and an unrelated CP162 feedback statement. **Whether the CBI has issued
guidance outside the Regulations remains UNVERIFIED.** The Regulations finding stands on its own.

---

## PART 3 — UNITED KINGDOM: FCA COLL 6.3

`VERIFIED-AT-SOURCE` — FCA Handbook, COLL 6.3, live page (adjacent rules carry a 30/04/2026 date stamp, so
this is current).

The operative **rule** is **COLL 6.6.3R(3)(c)**, which places a duty on the authorised fund manager to
reimburse affected unitholders, former unitholders and the scheme. **COLL 6.3.6G** is *guidance* — a table
titled *"Table: Recording and reporting of instances of incorrect pricing"* — and it is where the number
lives.

**Section 4 — recording and reporting:**

> (1) *"An authorised fund manager should record each instance where the price of a unit is incorrect as
> soon as the error is discovered, and report the fact to the depositary together with details of the
> action taken, or to be taken, to avoid repetition as soon as practicable."*

> (3) *"A depositary should also report to the FCA immediately any instance of incorrect pricing where the
> error is **0.5% or more of the price of a unit**, where a depositary believes that reimbursement or
> payment is inappropriate and should not be paid by an authorised fund manager."*

> (4) *"In accordance with **SUP 16.6.8 R**, a depositary should also make a return to the FCA on a
> quarterly basis which summarises the number of instances of incorrect pricing during a particular
> period."*

**Section 5 — rectification:**

> (2) *"A depositary may consider that the instance of incorrect pricing is of minimal significance if:
> the authorised fund manager and depositary meet the standards of control set out in Section 2 and
> Section 3 of this Table; and **the error in pricing of a unit is less than 0.5% of the correct price**."*

> (3) *"In determining (2), if the instance of incorrect pricing is due to one or more factors or exists
> over a period of time, **each price should be considered separately**."*

> (8) *"In all cases where reimbursement or payment is required, amounts due to be reimbursed to unitholders
> for individual sums which are reasonably considered by the authorised fund manager and depositary to be
> **immaterial**, need not normally be paid."*

**Three things to notice, and one of them is a genuine conflict:**

1. **The UK threshold is fund-type-blind.** One number, 0.5%, for everything. Luxembourg uses four tiers
   plus a self-set regime. This is a real design disagreement between two mature regulators about whether
   the tolerance is a property of the fund or of the process.
2. **The UK de minimis has no number.** "Immaterial" is left to the AFM and depositary jointly. Luxembourg
   fixes it per UCI against bank charges; Irish Funds fixes it at €50/€500.
3. **COLL 6.3.6G s.5(3) and CSSF 24/856 point 38 are in direct opposition on aggregation.** The UK says
   consider each price separately; Luxembourg says successive sub-threshold errors that aggregate to the
   threshold *are* a significant error. Same phenomenon, opposite rule. **This is not a detail — it is
   evidence that "materiality of a NAV error" is not a fact about the world, it is a jurisdictional
   parameter.** Which is precisely why a verifier should declare its parameters rather than assert a
   verdict.

`UNVERIFIED` — whether the FCA publishes the aggregate SUP 16.6.8R quarterly return data. I did not find a
published dataset; the search budget was gone. If it is published, it is the UK analogue of the CSSF base
rate and worth ten minutes of somebody's time.

---

## PART 4 — UNITED STATES: CODIFIED PENNIES, CONVENTIONAL PERCENTAGES

### 4.1 What is actually in the rules

`VERIFIED-AT-SOURCE` (Cornell LII mirror; eCFR and sec.gov both blocked me).

**17 CFR 270.2a-4(b)** — the penny-a-share rule, and note its narrow scope:

> *"The items which would otherwise be required to be reflected by paragraphs (a)(4) and (6) of this
> section need not be so reflected if cumulatively, when netted, they do not amount to as much as one cent
> per outstanding share."*

Paragraph (a)(4) is expenses including advisory fees; (a)(6) is interest and other income. **So the codified
US penny threshold is a rule about accruals, not a general NAV-error materiality threshold.** Anyone
quoting Rule 2a-4 as "the US NAV error rule" is over-reading it.

**17 CFR 270.2a-7(g)(1)(i)(B)** — the money market fund shadow-price rule:

> *"In the event such deviation from the money market fund's amortized cost price per share exceeds 1/2 of
> 1 percent, the board of directors shall promptly consider what action, if any, should be initiated by the
> board of directors."*

This is a *deviation-monitoring* rule for stable-NAV MMFs — again not a general error-correction threshold.

### 4.2 What the industry actually does

`SECONDARY` — K&L Gates, *Mutual Fund Pricing and Fair Valuation*, 2018 Washington D.C. Investment
Management Conference, 7 November 2018, Arthur C. Delibert and Betsy M. Johnson. Slide "CORRECTION OF
PRICING ERRORS", verbatim:

> *"Errors of less than 1¢ per share are immaterial and do not require corrective action."*
> *"Errors of 1¢ or more per share require financial adjustments in favor of the fund, but no payments to
> affected shareholders or reprocessing of shareholder accounts is required unless the errors amount to at
> least ½ of 1% of per share NAV."*
> *"Even here, there is a de minimis exception."*

**The slide cites no authority.** I searched for the underlying SEC no-action letter / AICPA Audit and
Accounting Guide chapter / ICI memorandum and found none; two DuckDuckGo queries returned zero results and
the WebSearch budget was exhausted. **Status: the US thresholds are a widely-followed practitioner
convention whose codified basis I could not establish.** That is a *finding*, not a gap in my work —
because it means the US does not in fact have what Luxembourg has.

The adjacent slides are on **ASC 820** (fair value hierarchy, Levels 1/2/3, and the Level-3 reconciliation
disclosure). ASC 946 (Financial Services — Investment Companies) was not reachable — FASB's codification is
paywalled. `NOT-FOUND`.

### 4.3 The one genuinely interesting US artefact

**Form N-CEN.** `SECONDARY` (Ignites, 3 Mar 2023): *"Open-end funds report on Form N-CEN the NAV errors
that required shareholders to be repaid or their accounts reprocessed."* The SEC publishes N-CEN data as
structured flat-file datasets extracted from the XML submissions (`sec.gov/data-research/sec-markets-data/form-n-cen-data-sets`,
`SECONDARY`).

**This is the closest thing anywhere in the world to the artefact class this project targets: a prescribed
regulatory return with a NAV-error field, filed as XML, published as a structured dataset.** If a
clean/dirty corpus of real filings is ever needed (Risk 2 in ARCHITECTURE Part 5), N-CEN is the only public
candidate I found. **The exact item number is NOT-FOUND** — verify it before it reaches a slide.

Measured US frequency, `SECONDARY`, and read the denominator warning:

> Ignites, Sonya Swink & Greg Saitz, 3 March 2023: *"During the first 10 months of 2022, those responsible
> for striking NAVs seriously bungled the process almost 130 times, an 18% increase from the same period in
> 2021"*; *"some 129 funds reported NAV restatements to the Securities and Exchange Commission, an increase
> of 20 funds compared to the year prior"*; *"the process failed hundreds of times at funds with $342
> billion in assets"* over two years; *"The number of fund shops reporting such mistakes increased even
> more, by over 29%."*

**No denominator is given** — the article never states the total number of open-end funds. **A rate cannot
be computed from this and must not be quoted as one.** Contrast the CSSF, which publishes both numerator
and denominator in the same report.

Also note the confounder the article itself supplies: *"The year-over-year change would have been three
times greater had it not been for Principal Funds reporting 2021 NAV miscues in 29 of its funds."* A single
filer moves the series. This is a fragile time series.

---

## PART 5 — IOSCO AND ESMA: PRINCIPLE WITHOUT PARAMETER

### 5.1 IOSCO

`SECONDARY`, quoted from CBI CP130 footnote 1 (see Part 2.1). Principle 5 of the *Principles for the
Valuation of Collective Investment Schemes*:

> *"A CIS should have policies and procedures in place that seek to detect and prevent pricing errors.
> Pricing errors that result in a material harm to CIS investors should be addressed promptly, and
> investors fully compensated."*

**IOSCO sets no threshold.** "Material harm" is undefined at the IOSCO level and delegated to members. I
could not open the IOSCO source (403); **do not cite a document number.**

The chain matters: **IOSCO Principle 5 → IMF Article IV / FSAP assessment of member compliance → national
rule.** That chain is how Luxembourg and (nominally) Ireland got here. It is the correct lever to name if
anyone asks "why would IFSCA ever do this?" — but see Part 2: the lever failed in Ireland for twelve years.

### 5.2 ESMA

`VERIFIED-AT-SOURCE` — 2022 Common Supervisory Action on Asset Valuation, Final Report, ESMA34-45-1802,
24 May 2023.

Controlled greps over the 976-line extraction: **`materiality` 0 · `toleran*` 0 · `pricing error` 0 ·
`valuation error` 12 · `compensat*` 8.** **ESMA sets no threshold either.**

Section 7, *Early detection mechanisms for valuation errors and transparency to investors*:

> ¶33 — *"NCAs were asked to report on the mechanisms implemented by fund managers for early detection of
> incorrect NAV calculations and valuation errors, as well as the relevant remedial procedures. While NCAs'
> feedback suggests that fund managers have early mechanisms in place for the detection of errors, **the
> related remedial procedures are not always sufficiently formalised** in the relevant valuation policies
> and procedures. In addition, the majority of NCAs reported that fund managers often did not calculate the
> NAV internally but relied on third-party administrators, which were often part of their depositary's
> group."*

> ¶34 — *"...early warnings and to detect valuation errors... are generally based on a **two-stage control**,
> the first one performed by the third-party administrator, and a subsequent escalation to the fund manager
> in case an unusual valuation is reported."*

> ¶38 — *"Overall, **only a low number** of incorrect NAV calculations and/or valuation errors which
> resulted in investor detriment were detected by NCAs, in the course of the CSA exercise."*

> ¶39 — *"...among the **five NCAs** that observed a proportion between **0-10% of the funds in the CSA
> sample** ... where incorrect calculation of NAV and/or valuation errors caused investor detriment, four
> NCAs are planning to take supervisory action to ensure investor compensation."*

> ESMA view XI — *"ESMA stresses the importance of ensuring **full investor compensation in all cases**
> where valuation errors caused harm to investors."*

**Denominator warning:** the report states minimum coverage thresholds were agreed and met but **never
publishes an absolute sample size** — no count of managers or funds. "0-10% of the funds in the CSA sample"
therefore has no computable numerator. That is a supervisory report that would fail this project's own
rule 4. Worth saying out loud in a pitch: *the pan-EU supervisor's own valuation report cannot be converted
into a rate.*

---

## PART 6 — INDIA ONSHORE (SEBI): THE TOLERANCE THAT MUST EXIST BUT HAS NO NUMBER

`VERIFIED-AT-SOURCE` — SEBI **Master Circular for Mutual Funds as on March 20, 2026**, 748 pp, 35,350
extracted lines, 1,291,125 characters.

### 6.1 Controlled measurement

| Pattern | Hits |
|---|---:|
| `NAV error` | **0** |
| `incorrect NAV` | **0** |
| `erroneous NAV` | **0** |
| `valuation error` | **0** |
| `de minimis` | **0** |
| `materiality` | 1 — outsourcing risk assessment, unrelated |
| `toleran*` | 4 |
| `swing pricing` | 24 |
| `rectif*` | 8 |
| `compensat*` | 19 |
| **positive controls** | `NAV` **371** · `Net Asset Value` **28** · `shall` **2,687** · `valuation` **223** |

**Proximity test** (the strong form): over the whole 1.29M-character flattened text, there are **34 windows
of ±180 characters containing any of `error|erroneous|incorrect|wrong|mis-stat|mis-calcul`. Exactly one of
those 34 also mentions NAV — and it is "Tracking Error" sitting next to "Computation of NAV" in a
disclosure-format table.**

**Conclusion: SEBI's consolidated instrument for mutual funds contains no NAV-error correction regime.**

### 6.2 What SEBI *does* require — and it is the interesting part

Master Circular, Annexure, **para 2.9.3.1(v)(e)** — outsourcing controls:

> *"Communication of its **error tolerance**, code of conduct and objective to its third party service
> providers (Fund Administrators / Custodians / R&T agents)."*

**para 2.9.3.1(vii)** — fund accounting system requirements:

> *"The Mutual Fund should ensure that the fund accounting systems used (inhouse or by the fund accountant
> to whom this activity has been outsourced) facilitate:*
> *a. **Validation of NAV calculations.***
> *b. Automated and manual price feeds.*
> *c. Identification of missing prices.*
> *d. **Flagging of price variances beyond pre-established tolerance levels**."*

**SEBI mandates that a tolerance exist, be pre-established, be enforced by the system, and be communicated
to the administrator. SEBI does not say what it is.** That is a materially different design from Luxembourg
(regulator sets it) and from the UK (regulator sets one number). It is the "declare your own parameter"
design — and it is the closest existing regulatory analogue to what this project proposes at L7.

### 6.3 The clause IFSCA copied

Master Circular Formats section, p.512, reproducing **SEBI (Mutual Funds) Regulations, Regulation
22(9)(b)(ii)**:

> *"The asset management company and the sponsor of the mutual fund shall be liable to compensate affected
> investors and/or the scheme for any unfair treatment to an investor resulting from inappropriate
> valuation."*

Set that beside IFSCA FM Regulations **Third Schedule Part A(g)** (Part 7 below). They are the same
sentence with the nouns swapped. **IFSCA's valuation-liability clause is a lift from SEBI's — and SEBI's
own clause has no threshold either.** This is important for the pitch: the gap is not an IFSCA oversight,
it is an inherited Indian regulatory design in which liability is asserted and its trigger is left to
industry.

### 6.4 Swing pricing — India onshore has it, GIFT does not

`VERIFIED-AT-SOURCE`, Master Circular para 5.8, deriving from **SEBI/HO/IMD/IMD-II DOF3/P/CIR/2021/631
dated 29 September 2021** and **SEBI/HO/IMD/IMD-II DOF3/P/CIR/2022/24 dated 25 February 2022**.

Hybrid framework for open-ended debt schemes (except overnight, Gilt, and 10-yr constant-maturity Gilt),
outflow scenarios only: partial swing in normal times, mandatory full swing on a declared market
dislocation. **AMFI prescribes the broad parameters and an indicative range of swing thresholds; the AMC
sets the swing factor.** On declared dislocation, mandatory for High/Very-High risk-o-meter schemes in PRC
cells A-III, B-II, B-III, C-I, C-II, C-III, with a **minimum swing factor table** — Class I × Class C =
**1.5%**, Class II × Class B = **1.25%**, Class II × Class C = **1.75%**, other cells "Optional".

`SECONDARY` — implementation was originally 1 March 2022, deferred to 1 May 2022 at AMFI's request.

### 6.5 AMFI — NOT REACHED

`NOT-FOUND`. `amfiindia.com/circulars` is a client-rendered shell; the fetched 261KB HTML yields exactly
one text line and zero circular entries. Two DuckDuckGo queries for an AMFI Best Practice Guideline on NAV
errors returned only unrelated BPG circulars (99/2021-22 data sharing, 110/2024 transmission of units,
108/2023-24 public issues, 93/2021-22 liquidity risk). **Whether AMFI publishes a NAV-error BPG with a
numeric threshold is UNVERIFIED.** Given that SEBI para 2.9.3.1(v)(e) presumes a tolerance exists, an AMFI
BPG is the likely home for it. **This is the single highest-value unresolved item on the India side** and
it is a 15-minute job with a working search budget.

---

## PART 7 — GIFT IFSC / IFSCA: WHAT IS SPECIFIED, MEASURED WITH CONTROLS

### 7.1 The controlled measurement, on the two instruments the circular corpus does not contain

The operator's §4.1 measurement covered 389 readable circular bodies. It did **not** cover the Regulations
themselves or the FAQ. I extended it to both.

**IFSCA (Fund Management) Regulations 2025, amended up to 30 January 2026 — 102 pages, 3,963 lines:**

| Pattern | Hits | What they are |
|---|---:|---|
| `NAV error` | **0** | — |
| `valuation error` | **0** | — |
| `incorrect NAV` | **0** | — |
| `toleran*` | **0** | — |
| `swing pricing` | **0** | — |
| `de minimis` | **0** | — |
| `restat*` | **0** | — |
| `materiality` | 1 | an Explanation about *"the decision to determine materiality"* in an unrelated provision |
| `compensat*` | **1** | Third Schedule Part A(g), below |
| `error` | 5 | 3 × "tracking error", 2 × "Financing of Terrorism" |
| **positive controls** | `shall` **728** · `valuer` **32** · `true and fair` **6** · `Sixth Schedule` **5** | instrument reads correctly |

**IFSCA Fund Management FAQ, 3 August 2026 — 68 pages:**

| Pattern | Hits |
|---|---:|
| `error` (the bare substring) | **0** |
| `NAV error`, `valuation error`, `incorrect NAV`, `materiality`, `toleran*`, `swing pricing`, `compensat*`, `de minimis`, `rectif*`, `restat*` | **0 each** |
| **positive controls** | `NAV` **13** · `valuation` **5** · `valuer` **6** · `shall` **183** · `scheme` **405** |

The 68-page FAQ published one week ago, on the regulations that govern 217 FMEs and 360 schemes, **does not
contain the substring "error" anywhere.** Its 13 NAV mentions are all frequency-of-computation and
disclosure-timeline questions (Q27, Q55, Q56/57, Q72) plus the ETF discount trigger.

**The operator's finding is CONFIRMED and extended: across the 389 readable circular bodies, the 102-page
current Regulations, and the 68-page current FAQ, there is no NAV-error, materiality, tolerance,
compensation-trigger or swing-pricing provision.**

### 7.2 What IFSCA *does* specify, quoted exactly

**Third Schedule, Part A — Code of Conduct and Obligations of the Fund Management Entity, p.87 of the
100-page original / Third Schedule of the 102-page amended text:**

> *"(f) The FME shall compute and carry out valuation of investments made by its scheme(s) in accordance
> with the investment valuation norms specified in Sixth Schedule, and shall publish the same."*

> *"(g) The FME and its controlling shareholders shall be liable to compensate the affected investors
> and/or the scheme for any unfair treatment to any investor as a result of inappropriate valuation."*

**Sixth Schedule — Investment Valuation Norms, Principles of Fair Valuation, clause (g):**

> *"The responsibility of true and fairness of valuation and correct NAV shall be of the FME, irrespective
> of disclosure of the approved valuation policies and procedures i.e., if the established policies and
> procedures of valuation do not result in fair/ appropriate valuation, the FME shall deviate from the
> established policies and procedures in order to value the assets/ financial products / securities at fair
> value: Provided that any deviation from the disclosed valuation policy and procedures may be allowed with
> appropriate disclosures to investors."*

**Independent valuation — regs 26(2) (venture capital) / 38(2) (restricted) / 50(2) (retail),
substantively identical:**

> *"In line with the investment valuation norms, the assets of the scheme shall be valued by an independent
> service provider, such as a fund administrator, a custodian, a credit rating agency registered with the
> Authority or a valuer registered with Insolvency and Bankruptcy Board of India or such other person as
> may be specified by the Authority: Provided that this requirement shall not apply in case of a fund of
> funds scheme that invests in scheme(s) regulated by a financial sector regulator, directly or through a
> manager, in IFSC, India or foreign jurisdiction(s), which are valued by any independent entity."*

**NAV frequency:**

| Reg | Scheme class | Obligation |
|---|---|---|
| **27(1)** | Venture Capital scheme | *"compute the NAV ... at least on an annual basis"* |
| **39(1)** | Restricted scheme | *"at least on a monthly basis: Provided that in case of a close ended restricted scheme the computation of NAV shall take place at least half-yearly."* |
| **51(1)** | Retail scheme | *"computed on a daily basis in case of an open-ended scheme and on a weekly basis in case of a close-ended scheme; **in such manner as specified by the Authority**."* |
| **69(1)** | ETF | *"compute the NAV of each ETF on a daily basis and publish the same on its website and inform the same to the recognised stock exchange where it is listed for disclosure on its website."* |

Each of 27/39/51 carries a sub-(2) in identical wording — and note the modal verb:

> *"The procedure and methodology for calculating the NAV **should** be fully documented, and such
> documentation should be regularly verified and amended, if required."*

**"Should", not "shall", in an instrument that uses "shall" 728 times.** That is a soft obligation sitting
exactly where Luxembourg puts its hardest ones.

### 7.3 The precise statement of the gap

**IFSCA specifies, with the force of "shall": who must value (an independent service provider, with a
fund-of-funds carve-out), how often the NAV must be computed (per scheme class), that the FME owns the
truth of the NAV, and that the FME and its controlling shareholders are liable to compensate for
inappropriate valuation.**

**IFSCA does not specify: what makes a NAV wrong, how wrong is wrong enough to matter, who must be told,
when, in what form, how the compensation is computed, in which direction it flows, whether there is a floor
below which it is not paid, who bears the cost of correction, or whether an auditor is drawn in.**

Third Schedule Part A(g) is **a liability rule with no trigger**. CSSF 24/856 is 47 pages of exactly the
trigger. That is the gap, stated defensibly.

**And reg 51(1) ends "in such manner as specified by the Authority"** — a live delegation hook. IFSCA can
put a NAV-error regime in place by circular tomorrow without amending a regulation. Worth one line in a
pitch; worth nothing as a product.

---

## PART 8 — THE DECISIVE TEST: DOES THE PRESCRIBED RETURN EVEN CARRY A NAV?

`VERIFIED-AT-SOURCE`, first-hand this lane, on
`Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`.

I searched all ten sheets for any field matching `NAV | net asset | valuation | valuer | corpus | AUM`, and
separately for `unit | per unit | outstanding | NAV per`. The complete NAV-adjacent surface of the artefact
is:

| Sheet | Cell | Label |
|---|---|---|
| 1. Introduction | L73 | *"Valuer, if any"* (with M74 *"IFSCA Registration No. / IBBI Registration No."*) |
| 1. Introduction | G53 / H53 / K53 | *"Type of Scheme"* / *"Open-Ended / Close-Ended"* / *"Whether Scheme is set up as a Fund of Funds (FoF) Scheme"* |
| 2. Summary | V4 | *"Net Assets Under Management as at the end of quarter (USD Million)"* |
| 2. Summary | X4 | *"Average Net Assets under Management for the quarter (USD Million)"* |
| 3. Portfolio | A176 | **Table 3.9: Details of Valuation** — C177 total portfolio value, **D177 "Latest Valuation of investments of scheme (in USD Million)", E177 "Date of latest Valuation", F177 "Date of previous valuation"** |
| 4. Investors | F79 | *"Net Assets under Management sourced through Distributors..."* |
| 8. Compliance Status | B11 / **C11** | *"The FME is in compliance with Investment Valuation Norms as specified in Sixth Schedule of IFSCA (Fund Management) Regulations, 2025."* → **a Yes/No cell** |

**Searches for unit-level data returned nothing.** There is **no NAV per unit, no units outstanding, no
dealing price, no subscription or redemption struck at a price, and no error period** anywhere in the
prescribed FME return. The only unit-shaped strings in the workbook are "outstanding borrowing",
"outstanding derivative contracts", "complaints outstanding" and "Financial Intelligence Unit-India".

**A NAV-error checker has no input in this artefact class.** Every one of the Luxembourg, UK and US rules
above operates on (NAV per unit, units dealt, dealing date). None of those three quantities is filed.

What the return *does* contain, at **`'8. Compliance Status'!C11`**, is a binary self-attestation that the
FME complied with the valuation norms. **The prescribed return already ships a green tick for valuation,
and nothing else in the 6,757 cells can contradict it.** If the pitch needs one cell reference, that is the
one.

---

## PART 9 — TWO ORIGINAL DEFECTS FOUND IN THE REGULATOR'S OWN ARTEFACT

Both are first-hand, reproducible in under a minute, and both are the project's thesis in miniature.

### 9.1 The scheme-count identity is silently wrong for 2 of its own 9 dropdown values

`VERIFIED-AT-SOURCE` — read from the raw OOXML, not through a library.

`'1. Introduction'!G54:G63` ("Type of Scheme") is constrained by an **OOXML `x14:dataValidation` list**
whose formula is `Dropdown!$F$3:$F$11` — nine permitted values:

```
F3  Venture Capital Scheme
F4  Angel Scheme
F5  Restricted Scheme (Category I)
F6  Restricted Scheme (Category II)
F7  Restricted Scheme (Category III)
F8  Retail Scheme
F9  Exchange Traded Fund
F10 Special Situation Fund
F11 Family Investment Fund
```

`'1. Introduction'!D17`, labelled **"Total No. of Schemes of the FME authorised by IFSCA"**, is:

```
D17 = SUM(D18:D20)
D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")
D19 = COUNTIF(G54:G63,"*Restricted*")
D20 = COUNTIF(G54:G63,"*Retail*") + COUNTIF(G54:G63,"*Exchange Traded Fund*")
```

Applying the three COUNTIF patterns to the nine permitted values:

| Vocabulary value | Bucket |
|---|---|
| Venture Capital Scheme | D18 |
| Angel Scheme | D18 |
| Restricted Scheme (Category I / II / III) | D19 |
| Retail Scheme | D20 |
| Exchange Traded Fund | D20 |
| **Special Situation Fund** | **none** |
| **Family Investment Fund** | **none** |

> **A filing that declares a Special Situation Fund or a Family Investment Fund reports a total scheme
> count that is silently short by one per such scheme. The value is legal under the template's own data
> validation. No cell in the workbook flags it. The workbook computes a clean, well-formed, wrong number
> and calls it a total.**

This is a **live defect in a prescribed regulatory return currently in use**, found by a script, and it is
the strongest demo asset in the whole corpus because the audience can check it themselves in Excel in
thirty seconds.

`UNMEASURED` — how many of the 360 authorised schemes are of these two types. That needs the IFSCA scheme
register broken down by type; the on-disk `research/05_Fund_Management_Entities_217_FMEs_360_schemes.json`
is a research-lane summary, not a register dump, and carries no type distribution. **Do not claim an
exposure figure.** The defect is real whether the exposure is 0 or 60.

### 9.2 Correction to RND-BRIEF §4.3: the data-validation count is understated by 35%

The brief states: *"35 data validations (only **3** list-type with a named vocabulary)."*

Measured this lane by parsing `xl/worksheets/sheetN.xml` directly and counting `<dataValidation>` in the
sheet body separately from `<x14:dataValidation>` inside `<extLst>`:

| Sheet | standard `<dataValidation>` (of which list) | `<x14:dataValidation>` list |
|---|---:|---:|
| 1. Introduction | 8 (1) | **9** |
| 2. Summary | 3 (0) | 0 |
| 3. Portfolio | 11 (0) | **2** |
| 4. Investors | 3 (0) | 0 |
| 5. PMS | 6 (0) | 0 |
| 6. Complaints | 1 (0) | **1** |
| **7. AML-CFT** | **0 (0)** | **5** |
| 8. Compliance Status | 2 (2) | **2** |
| Dropdown | 1 (0) | 0 |
| **TOTAL** | **35 (3)** | **19** |

> **True totals: 54 data validations, of which 22 are list-type with a named vocabulary — not 35 and 3.**
> The 35/3 figure is what `openpyxl`'s default reader sees. It drops the entire `<extLst>` block and emits
> only `UserWarning: Data Validation extension is not supported and will be removed`.

The '7. AML-CFT' row is the sharpest: **under the default lens that sheet has zero data validations; it
actually has five.**

**This is a third silent false negative from a deterministic program, and unlike the two in §4.4 it changes
a load-bearing number in the architecture** — "dropdown ∈ vocabulary" is one of the 17 predicates listed as
decidable, and its true scope is **7× larger** (22 vocabularies, not 3) than the brief records. The
17/24 = 71% headline is unaffected in count, but the *content* of predicate 13 is much bigger than stated.

---

## PART 10 — OPERATIONAL REALITY: WHO ACTUALLY CHECKS A NAV, AND WITH WHAT

### 10.1 What NAV oversight is

`SECONDARY`. Two independent descriptions converge. ESMA CSA ¶34 describes the market structure: a
**two-stage control** — third-party administrator strikes the NAV and runs the first control, escalation to
the fund manager on an unusual valuation. ESMA ¶33 adds the structural fact that most managers do **not**
calculate NAV internally and rely on administrators *"often part of their depositary's group"*.

The operational content, from a practitioner write-up (`https://fundcount.com/nav-oversight-controls-review-workflow-breakpoints/`),
is eight control areas — cash reconciliation, position completeness, stale prices and overrides, FX source
consistency across GL/positions/reports, corporate actions captured once with correct effective dates, fee
accruals against contractual terms, expense accrual completeness, investor allocations tying fund-level to
investor-level with equalisation — and an eight-step workflow ending in "final approval and release" and
"post-close remediation". **The article publishes no numeric thresholds and says so**, recommending
"both absolute and percentage thresholds (for example, base currency amount and basis points of NAV)"
tailored per fund type. Those are the author's recommendations, not rules.

### 10.2 The software

`SECONDARY`, from vendor pages.

**Milestone Group pControl NAV Oversight** (`https://www.milestonegroup.com/solutions/nav-oversight-validations`)
publishes its check taxonomy, and it reads like a predicate library:

- *Top-down:* Fund/Portfolio Validations · Expected Price Calculations · Expected Fee Calculations · Share
  Class Validations · Clean Price Analysis · Backup NAV Calculations
- *Bottom-up:* Holding Validations · Transaction Validations · Corporate Actions Validations · Account
  Balance Validations · Units and Capital Flow Validations · Market Data Validations · Data Consistency
  Checks
- *Analysis:* Expected vs Actual NAV · NAV Movement Analysis · Share Class Divergence · Benchmark and
  Sister Fund Divergence · Maker/Checker Review · Multi-Exception Clearance · Auto Clearance of Exceptions
- The product calculates an expected NAV *"based on previous valuation point positions, market data and
  transactions to provide an independent and reliable reference for comparison to the service provider's
  actual NAV"*, and compares *"against prescribed tolerance levels to ensure rapid identification of
  exceptions"*.

> **It does not publish how many checks it ships with, and it publishes no false-alarm rate and no
> detection rate.** Neither does FundGuard (NAV contingency / "Contingent NAV", incl. an Ultimus case
> study). **This is the direct competitive opening and it is the same one the architecture already
> identifies: the incumbent tools tell you what they checked but never how often each check cries wolf.**

**daappa NAV Error Materiality Calculator** (`https://www.daappa.com/nav-error-materiality-calculator`) —
a **free public tool that already encodes CSSF 24/856**: the 0.20%/0.50%/0.50%/1%/1% tables, the 5% cap for
reserved vehicles, the 4–8 week notification window and the EUR 50,000 / EUR 5,000 auditor triggers.
**Read this as a warning: where the regime exists, the calculator is already a giveaway.** The scarce good
is the regime, not the arithmetic.

### 10.3 Administrators serving GIFT IFSC

`SECONDARY` / `UNVERIFIED`.

- **Basiz Fund Services** — GIFT City (Gandhinagar) among its locations; describes NAV and fee-compute
  services; described as the first fund administrator licensed in GIFT City. `basizfa.com`
- **KFin Technologies** — GIFT City page (`kfintech.com/gift-city/`); fund accounting & administration,
  transfer agency. A press item reports *"KFintech has formally signed up with 4 GIFT city funds and 2
  global funds in GIFT City"* (`SECONDARY`, marketscreener, undated in the snippet — **do not quote this
  count**).
- CAMS, Apex, Vistra, Orbis — **no GIFT-specific material surfaced in the searches I could run.**

> **No fund administrator serving GIFT IFSC publishes a house NAV tolerance or an error policy that I could
> find.** Coverage: public web pages via DuckDuckGo HTML only, after the WebSearch budget was exhausted, no
> client-portal or contractual material. **This absence is weak and is labelled UNVERIFIED.** It is exactly
> the unknown Part 12 is designed to settle.

### 10.4 Is there measured data on NAV error frequency anywhere?

**Yes, in exactly one place: the CSSF Annual Report** (Part 1.7) — numerator *and* denominator, three-year
series, split by error class, with compensation totals. Nothing else I found comes close.

Second-best is the **Ignites/N-CEN** count (Part 4.3) — a numerator with no denominator.

A vendor blog claiming a *"40% error rate in manual quarterly valuations"* for private funds surfaced in
search. **No denominator, no method, no population, vendor-published. Do not use it.** Recording it here
only so nobody re-finds it and treats it as a datum.

---

## PART 11 — REUSABLE ASSETS, WITH L0–L7 FIT AND WHERE EACH STOPS

| Asset | Warrant | Fits | Verdict | Where it stops |
|---|---|---|---|---|
| **Circular CSSF 24/856** (47 pp) | VERIFIED | **L3 corpus + L5 vocabulary.** The best existing example anywhere of a regulator declaring, *ex ante*, the boundary of what counts as a finding: four tiers, six disambiguation rules (point 37), an aggregation rule (38), a compensation direction matrix (Tables 4/5), two euro triggers, a notification deadline. Point 37(i)–(v) are directly transcribable into executable predicates. | **ADOPT as exhibit and as predicate-shape reference.** | Luxembourg-only, and it operates on (NAV/unit, units dealt, dealing date) — **none of which exist in the IFSCA artefact.** Cannot be ported; can only be cited. |
| **CSSF Annual Report 2024 §4.1.2 / §1.2** | VERIFIED | **The only real-world prior for a NAV-error base rate.** Use in the pitch as "this is what a jurisdiction that declares its coverage can report about itself." | **ADOPT as comparator.** | 2024 = old circular; different jurisdiction, artefact and error class. **Must never be imported as an FFR prior for the IFSCA predicate set.** |
| **CBI CP130** (2019) | VERIFIED | **L5 reason vocabulary.** Its four error types (NAV / Investment Breach / Fee / Control Breach) and its "Appropriately Rectified" three-step (classify → correct → redress) are a clean taxonomy to borrow. | **ADOPT the taxonomy.** | It is a **consultation that never became rules** (Part 2.2). Cite it as a proposal, never as law. |
| **S.I. 316 of 2026 (Irish UCITS Regs 2026)** | VERIFIED | **The counter-example.** Kills "everyone else has a NAV-error regime". | **ADOPT as the pitch's honesty exhibit.** | Only tells you about Ireland's UCITS rulebook; AIF Rulebook and CBI Q&A unchecked. |
| **FCA COLL 6.3.6G** | VERIFIED | **L6.** Section 5(3) ("each price considered separately") vs CSSF point 38 (aggregate) is a **measured jurisdictional disagreement about a metamorphic relation.** This is the first real evidence that a relation must carry a parameter, not a truth value. | **ADOPT into L6 design.** | Guidance, not rule; the rule is COLL 6.6.3R(3)(c). No numeric de minimis. |
| **17 CFR 270.2a-4(b) / 270.2a-7(g)(1)(i)(B)** | VERIFIED (Cornell mirror) | Reference points for "the codified US thresholds are narrower than people say". | **ADOPT with the caveat.** | 2a-4(b) is about accruals only; 2a-7 is about stable-NAV MMF deviation. Neither is a general error rule. |
| **Form N-CEN + SEC structured datasets** | SECONDARY | **L0 / experiment 9.2.** The only public corpus of *real filed* NAV-error disclosures I found anywhere. Candidate for a real (not synthetic) clean/dirty corpus. | **EVALUATE — high value, unverified.** | **Exact item number NOT-FOUND** (sec.gov 403). US open-end funds only; wrong artefact class; would ground a base rate, not a predicate set. |
| **ESMA34-45-1802 CSA on Asset Valuation** | VERIFIED | Framing: pan-EU supervisor says remedial procedures *"not always sufficiently formalised"*; two-stage control is the market structure. | **ADOPT as framing.** | **Publishes no absolute sample size** — its own percentages are un-denominated. Sets no threshold. |
| **SEBI Master Circular Annexure 2.9.3.1(v)(e) & (vii)** | VERIFIED | **The closest regulatory analogue to L7.** A regulator requiring that a tolerance be pre-established, system-enforced, and *communicated* — without setting it. | **ADOPT as the Indian precedent for "declare your parameter".** | Onshore India only. Does not bind IFSCA. Says nothing about what the number should be. |
| **SEBI swing pricing (para 5.8; circulars 2021/631 and 2022/24)** | VERIFIED | Contrast exhibit: India onshore has a swing framework with minimum factors (1.25% / 1.5% / 1.75%); GIFT has zero. | **ADOPT as contrast.** | Open-ended debt schemes only, outflows only. |
| **daappa NAV Error Materiality Calculator** | SECONDARY | Competitive intelligence. | **REJECT for reuse; ADOPT as evidence.** | Proves the calculator layer is already free where a regime exists — i.e. that the *arithmetic* is not the scarce good. |
| **Milestone Group pControl NAV Oversight taxonomy** | SECONDARY | **L3/L5.** Its 19 named validation families are a ready-made check taxonomy to compare a synthesised predicate set against. | **EVALUATE.** | Vendor page, no schema, closed source, **no published check count, false-alarm rate or detection rate.** |
| **OpenIM entity E-36 "Oversight Exception"** — `https://github.com/antikas/open-investment-model` | VERIFIED (repo opened) | Names a `shadow_nav_difference` exception type with `severity` ∈ {minor, material, significant}, `monetary_impact_amount`, lifecycle `status`. Vocabulary only. | **REJECT for reuse.** | **MIT, 3 stars, 0 forks, 30 commits, v0.3.0.** Pre-alpha. Self-described as *"a reference model, not a design blueprint"*. Borrow the field names if useful; depend on nothing. |
| **Raw OOXML `x14:dataValidation` parsing** | VERIFIED (this lane) | **L1, mandatory.** See Part 9.2. | **ADOPT — this is a required fix, not an option.** | `openpyxl` default silently drops 19 of 54 validations and 19 of 22 named vocabularies. |

---

## PART 12 — THE JUDGEMENT: WHICH WEDGE IS SHARPER

**Prescribed-return verification with declared coverage. Not a NAV-error regime. The margin is not close,
and five independent observations point the same way.**

**1. The artefact test settles it on its own.** The IFSCA FME quarterly return contains no NAV per unit, no
units outstanding, no dealing price and no dealing date (Part 8). Every NAV-error rule on earth — CSSF
Tables 4/5, COLL 6.3.6G, Rule 2a-4 — operates on exactly those quantities. **You cannot build a NAV-error
checker for an artefact that does not contain a NAV.** To build one you would first have to invent the
corpus, which is Risk 2 in ARCHITECTURE Part 5 made worse, not better.

**2. Ireland removes the moral force of the gap.** The pitch "IFSCA is missing what mature jurisdictions
have" requires that mature jurisdictions have it. Ireland — second-largest fund domicile — was told by the
IMF in 2014, consulted in 2019, and as of **S.I. 316 of 2026** still has no rule, running instead on
industry guidance its own regulator says it *"has neither sanctioned nor approved."* The US thresholds are
practitioner convention with no authority I could find on the slide that states them. ESMA and IOSCO set no
number. **The set of jurisdictions with a prescribed NAV-error materiality regime is roughly {Luxembourg,
UK}, and they disagree with each other about tiering and about aggregation.** "IFSCA lacks this" is not a
scandal; it is the majority position.

**3. A NAV-error regime is a policy proposal, and you cannot ship a policy.** The judging criteria are
*problem relevance, innovation and creativity, **solution feasibility**, team capability, presentation*.
Only IFSCA can set a materiality threshold. A team of four with a two-day build cannot. Whereas
L0+L1+L5+hand-authored predicates over a real published artefact runs end-to-end with zero model
involvement, which the architecture already commits to.

**4. Where the regime exists, the tooling is already commoditised.** daappa gives the CSSF 24/856
calculator away free. Milestone and FundGuard sell the oversight platform. If GIFT ever gets a regime, the
calculator arrives with it from vendors who already have it. **The scarce good is not the threshold
arithmetic — it is the coverage declaration, which nobody sells and no regulator requires.**

**5. The prescribed-return route already has first-hand defects to demonstrate, and the NAV route has
none.** Part 9.1 is a live, checkable, silently-wrong total in a return currently in use. Part 9.2 is a
third silent false negative from a deterministic program, this time in the project's own measurement
apparatus. Both are on-thesis, both are reproducible by the audience, both took under a minute.

**What survives from the NAV-error work, and it is not nothing:**

- **CSSF 24/856 becomes the pitch's prior art for coverage declaration.** Its tolerance tables *are* a
  regulator's ex-ante declaration of the boundary of what counts. The line is: *"One regulator in the world
  publishes, in advance, exactly what it will and will not treat as a finding, and then publishes the
  resulting rate every year. We compute the equivalent per filing, for a jurisdiction that has neither."*
- **Keep exactly one NAV-shaped predicate: valuation staleness.** It is statute-derived, non-degenerate,
  mutation-killable, and computable from fields the return actually contains. It gives the pitch a
  valuation story without needing a threshold that does not exist. Sketch:

```python
# L5 predicate: valuation currency vs the NAV-computation frequency owed under
# IFSCA (Fund Management) Regulations 2025, regs 27(1) / 39(1) / 51(1) / 69(1).
# Reads ONLY fields present in the prescribed FME workbook.
#
#   scheme_type  <- '1. Introduction'!G54:G63   (x14 list, vocab = Dropdown!F3:F11)
#   ended        <- '1. Introduction'!H54:H63   (Dropdown!I3:I4)
#   last_val     <- '3. Portfolio'!E178:E187    ("Date of latest Valuation")
#   prev_val     <- '3. Portfolio'!F178:F187    ("Date of previous valuation")
#   period_end   <- derived from '1. Introduction'!D2 (Quarter) + D3 (Financial Year)

MAX_GAP_DAYS = {
    ("Venture Capital Scheme",           "*"):            366,   # reg 27(1) annual
    ("Angel Scheme",                     "*"):            366,   # grouped w/ VC by the
                                                                 # template's own D18 COUNTIF
    ("Restricted Scheme (Category I)",   "Open-Ended"):    31,    # reg 39(1) monthly
    ("Restricted Scheme (Category I)",   "Close-Ended"):  184,    # reg 39(1) proviso, half-yearly
    ("Restricted Scheme (Category II)",  "Open-Ended"):    31,
    ("Restricted Scheme (Category II)",  "Close-Ended"):  184,
    ("Restricted Scheme (Category III)", "Open-Ended"):    31,
    ("Restricted Scheme (Category III)", "Close-Ended"):  184,
    ("Retail Scheme",                    "Open-Ended"):     1,    # reg 51(1) daily
    ("Retail Scheme",                    "Close-Ended"):    7,    # reg 51(1) weekly
    ("Exchange Traded Fund",             "*"):              1,    # reg 69(1) daily
    # ("Special Situation Fund", *)   -> ABSENT: no NAV-frequency obligation located
    # ("Family Investment Fund", *)   -> ABSENT: no NAV-frequency obligation located
}

def valuation_staleness(row, period_end):
    key = (row.scheme_type, row.ended)
    limit = MAX_GAP_DAYS.get(key) or MAX_GAP_DAYS.get((row.scheme_type, "*"))
    if limit is None:
        # THE PRODUCT. Not a pass, not a fail.
        return UNCHECKED(
            reason="no obligation specified",
            detail=f"'{row.scheme_type}' is a permitted value of the template's own "
                   f"Type-of-Scheme vocabulary (Dropdown!F3:F11) but no NAV-computation "
                   f"frequency for it was located in the FM Regulations 2025 "
                   f"(as amended to 30 Jan 2026).",
            what_would_make_it_checkable="an IFSCA circular under the reg 51(1) "
                   "delegation, or an amendment adding the scheme class to Ch. IV/V/VI.")
    if row.last_val is None:
        return UNCHECKED(reason="source unreadable", detail="Table 3.9 E-column empty")
    if (period_end - row.last_val).days > limit:
        return FAIL(clause=f"reg mapped from {key}", observed=(period_end - row.last_val).days,
                    limit=limit)
    return PASS(limit=limit, margin=limit - (period_end - row.last_val).days)
```

  Two of the nine legal scheme types resolve to **UNCHECKED("no obligation specified")**. That is the
  entire product in one function: the boundary is computed from the instrument and the vocabulary, not
  asserted, and it is visible on screen.

- **A second predicate falls straight out of regs 26(2)/38(2)/50(2) and is worth having** because it uses
  the fund-of-funds proviso as a genuine conditional:

```python
# L5 predicate: independent valuer present unless the FoF proviso applies.
#   fof      <- '1. Introduction'!K54:K63  ("Whether Scheme is set up as a Fund of Funds")
#   valuer   <- '1. Introduction'!L75:L84  ("Valuer, if any" -> name)
#   valuer_r <- '1. Introduction'!M75:M84  ("IFSCA Registration No. / IBBI Registration No.")
#   admin    <- '1. Introduction'!H75:H84  ("Fund Administrator, if any")
#   cust     <- '1. Introduction'!F75:F84  ("Custodian, if any")
def independent_valuation(row, ifsca_register, ibbi_register):
    if row.fof == "Yes":
        return UNCHECKED(reason="requires counterparty data",
                         detail="reg 26(2)/38(2)/50(2) proviso: exemption turns on whether the "
                                "target schemes are regulated by a financial sector regulator AND "
                                "valued by an independent entity — neither fact is filed here.")
    providers = [p for p in (row.valuer, row.admin, row.cust) if p]
    if not providers:
        return FAIL(clause="reg 26(2)/38(2)/50(2)", detail="no independent valuation provider named")
    if row.valuer and not (ifsca_register.resolves(row.valuer_r) or ibbi_register.resolves(row.valuer_r)):
        return FAIL(clause="reg 26(2)/38(2)/50(2)",
                    detail=f"valuer registration {row.valuer_r!r} resolves in neither register")
    return PASS()
```

  Note that the FoF branch returns **UNCHECKED("requires counterparty data")** rather than a pass — the
  proviso's two conditions are facts about schemes the FME does not manage. That reason code is already in
  L5's closed vocabulary. This is the architecture doing its job on a real clause.

---

## PART 13 — THE EXACT QUESTION TO PUT TO A FUND ADMINISTRATOR

One call, to whoever runs fund accounting for GIFT IFSC schemes at **KFin Technologies, CAMS or Basiz Fund
Services**. Ask this, in this order, and do not paraphrase the first one:

> **"When you strike a NAV for an IFSC scheme and it differs from what you expected — from your own
> recomputation, from the prior valuation point, or from the manager's shadow — what is the number that
> makes you stop and escalate rather than release? Is that number written down, and who set it: you, the
> FME, or the administration agreement?"**

The answer is binary and it settles the whole domain question:

- **If there is a number** — the tolerance regime exists in GIFT contractually rather than in regulation.
  Then the gap is *not* "nobody has a threshold", it is **"the threshold is private, uncomparable across
  administrators, and invisible to the supervisor."** That is a *better* problem statement than the one in
  the brief, and it makes the coverage-declaration product stronger, not weaker: the boundary already
  exists and is simply undeclared.
- **If there is no number** — the operator's measured absence extends from the regulation into practice,
  and the "17/24 boundary is undeclared everywhere in this workflow" claim becomes end-to-end.

Then, and only then, the two follow-ups:

> **"In the last twelve months, how many times did you restate a published NAV for an IFSC scheme — and
> when you did, what did you have to do for the investors, and who decided?"**

> **"Does anything you file with IFSCA — anywhere in the FME quarterly return or elsewhere — ever tell
> them that a NAV was restated?"**

The last question is the one that closes the loop with Part 8. I expect the answer to be *no*, and if it
is, then **`'8. Compliance Status'!C11` is the only place a valuation problem could surface in the
supervisory record, and it is a self-attested Yes/No box.**

Log the answers against RND-BRIEF §9.6 (the IFSCA email) — the two together settle whether the
entity-facing product is a gap or a convenience.

---

## PART 14 — WHAT THIS CHANGES ABOUT THE DESIGN

Seven changes, each traceable to a measurement above.

**1. L1 must parse OOXML `extLst` / `x14:dataValidation`, not just the sheet body.** *(Part 9.2.)* The
default `openpyxl` reader drops 19 of 54 validations (35%) and 19 of 22 named vocabularies (86%), and
reports a sheet with five validations as having none — emitting only a `UserWarning`. Any schema induced
without this is silently, confidently incomplete. **This is a required fix and it should carry a regression
test asserting `54` and `22` against the checked-in workbook hash.**

**2. L5's closed reason vocabulary gains one entry it demonstrably lacks: `no obligation specified`.**
*(Parts 7.2, 12.)* Distinct from `rule ambiguous` (a rule exists and is unclear) and from `predicate not
yet synthesised` (our gap). Here the instrument is clear and simply says nothing — two of nine legal
Type-of-Scheme values have no NAV-frequency rule. Conflating "the regulator did not legislate this" with
"we haven't got round to it" would be the single most misleading thing the coverage panel could do.

**3. L6 metamorphic relations must be parameterised by jurisdiction, and there is now a measured case.**
*(Parts 1.3, 3.)* CSSF 24/856 point 38 says sub-threshold errors that aggregate over successive dates *are*
significant. FCA COLL 6.3.6G s.5(3) says *"each price should be considered separately."* Two mature
regulators, opposite rules, same phenomenon. **A relation is not a law of nature; it is a rule with an
owner.** Every L6 relation should carry the instrument that authorises it, and the report should say which
one it applied. This is the first evidence the design has for that, and it is worth a slide.

**4. Third Schedule Part A(g) is the canonical Unchecked entry, and its "what would make it checkable"
text is now writable.** *(Parts 7.2, 1.2.)* Reason: `requires judgment`. What would make it checkable:
*"a materiality threshold by scheme class, of the kind CSSF Circular 24/856 Tables 1–3 specify (0.20% MMF /
0.50% bond and mixed / 1.00% equity and other), plus a compensation-direction rule of the kind its Tables
4–5 specify."* **That is the Unchecked panel doing something no compliance product does: naming the
specific instrument that would move a predicate across the boundary, with the numbers.**

**5. Do not build a NAV recomputation engine, and delete NAV-per-unit from every data model.** *(Part 8.)*
The prescribed return has no NAV per unit, no units outstanding and no dealing data. Anything downstream
that assumes those fields exist is designing for an artefact that was never filed. Keep the two predicates
in Part 12 and nothing more on the valuation axis.

**6. The FFR discipline needs an explicit ban on importing the Luxembourg prior.** *(Parts 1.7, 10.4.)*
1.72% of Luxembourg fund units per year is the only real-world NAV-error base rate published anywhere, and
it is for a different jurisdiction, artefact, error class and circular vintage. It is a *comparator for the
pitch* and never an input to a predicate's measured error rate. Add it to WITHDRAWALS-style guardrails
before somebody quotes it as "the expected failure rate."

**7. The pitch gets a one-cell opening and it should use it.** *(Part 8.)* `'8. Compliance Status'!C11` is
a Yes/No box asserting compliance with the Sixth Schedule valuation norms. **The prescribed return already
contains a green tick, and nothing in the other 6,756 cells can contradict it.** Set that beside Part 9.1 —
the workbook's own scheme-count total is silently wrong for two of its own nine legal values — and the two
slides together make the argument without a single citation to a paper: *this is what a regulated filing
looks like today. It ships an all-clear it cannot support, and it computes a wrong number without
noticing. The product does not add a better tick. It removes the tick and prints the boundary.*

---

## PART 15 — OPEN QUESTIONS (ordered by value per minute)

1. **Does AMFI publish a Best Practice Guideline with a numeric NAV-error threshold?** SEBI Master Circular
   2.9.3.1(v)(e) presumes a tolerance exists. `amfiindia.com/circulars` is a JS shell; two DDG queries
   failed. **15 minutes with a working search budget.** If yes, India onshore has a number and the
   IFSCA contrast becomes India-internal, which is much sharper for a GIFT audience.
2. **The exact Form N-CEN item that captures NAV errors, and whether the SEC structured dataset exposes
   it.** sec.gov 403'd, eCFR redirected, Cornell incorporates by reference. If it is a queryable field,
   it is the only public corpus of real filed NAV-error disclosures in the world and it changes what
   experiment 9.2 can be.
3. **Did the CBI ever issue final guidance outside the Regulations?** S.I. 316 of 2026 is clean, but the
   AIF Rulebook and the UCITS Q&A (42nd edition) are unchecked. Cheap; would firm up Part 2 from
   "no rule in the UCITS Regulations" to "no rule anywhere in Ireland".
4. **The house tolerance question in Part 13**, to KFin / CAMS / Basiz. This is the operator's already-flagged
   live kill and it remains unrun.
5. **The 02/77 non-MMF thresholds at source.** I could confirm only MMF 0.25% → 0.20%. The claim that the
   0.50%/1.00% tiers are unchanged is UNVERIFIED. One working PDF link settles it.
6. **Does the FCA publish aggregate SUP 16.6.8R quarterly pricing-error returns?** If it does, that is a
   second published base rate and the "only Luxembourg publishes this" claim needs qualifying.
7. **How many of the 360 authorised GIFT schemes are Special Situation Funds or Family Investment Funds?**
   This is the exposure denominator for the Part 9.1 defect. Needs the IFSCA scheme register by type.
8. **ASC 946 and the AICPA Audit and Accounting Guide chapter on NAV error correction** — both paywalled.
   The K&L Gates slide cites no authority; if the authority exists, it is in one of those two.
9. **Whether IFSCA's own receipt-side processing already runs any of these checks** — RND-BRIEF §9.6. Note
   the NEC SupTech award (27 Jan 2026, ₹39.57 crore, RE-facing portal in scope) makes this urgent: if the
   supervisor's new system does arithmetic validation on receipt, the entity-facing product is a
   convenience.

---

## Adversarial verification (independent pass)

**Run 10 August 2026, by a verifier instructed to refute.** I selected the eight claims whose falsity
would most damage the design, and re-derived each at primary source without accepting this lane's
citation as evidence. Every PDF below was re-downloaded from the URL in Part 0, re-extracted with
`pdftotext -layout` on my own machine, and re-grepped; the workbook was re-parsed from raw OOXML. Where
I reproduce a count, I ran it myself.

**My own coverage hole, declared first.** The session-wide WebSearch budget was already exhausted
(200/200) before I began, exactly as it was for this lane. I could therefore run **no independent
keyword search** — only direct WebFetch on constructed URLs. This has a specific consequence: I can
confirm that a named instrument does not contain a rule, but I **cannot** independently establish that
no *other* instrument does. Every absence below is an absence *in the document named*, with the same
coverage boundary the lane declared. The IOSCO PDFs, the AIF Rulebook, the CBI UCITS Q&A, AMFI and
Form N-CEN remain unopened by me as well.

### Verdict summary

| # | Claim | Verdict |
|---|---|---|
| 1 | Part 8 — the prescribed FME return carries no NAV-per-unit / units / dealing data | **QUALIFIED** |
| 2 | Part 9.1 — scheme-count identity silently drops 2 of its own 9 dropdown values | **CONFIRMED** |
| 3 | Part 9.2 — 54 data validations / 22 named vocabularies, not 35 / 3 | **CONFIRMED** |
| 4 | Part 2.2 — Irish UCITS Regulations 2026 contain no NAV-error regime | **CONFIRMED** |
| 5 | Part 1.2 / 1.5 — CSSF 24/856 thresholds, 5% cap and EUR 50,000 / 5,000 triggers | **CONFIRMED** |
| 6 | Part 1.7 — CSSF base rate, its denominators, and the derived 1.72% | **CONFIRMED** |
| 7 | Part 3 — FCA COLL 6.3.6G vs CSSF point 38 aggregation conflict | **CONFIRMED** |
| 8 | Part 7.1 — IFSCA Regulations and FAQ contain no NAV-error provision | **CONFIRMED** |
| 9 | Part 11 — OpenIM entity E-36 "Oversight Exception" / `shadow_nav_difference` | **UNVERIFIABLE** |

Seven of eight load-bearing claims survive an adversarial re-derivation intact. That is an unusually
high survival rate and it should be read as a property of this lane's method — it quoted clause numbers
and published its greps, which is precisely what makes refutation cheap. Two corrections follow.

---

### 1. Part 8 — the artefact test — **QUALIFIED**

Re-parsed `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` (SHA-256
`7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39`) from raw OOXML.

**What I confirm.** 6,757 `<c>` elements (matches §4.3 exactly), 494 shared strings, 1,174 cells
carrying text. Searching every one:

| Pattern | Hits |
|---|---:|
| `NAV` (whole word, any case) | **0** |
| `per unit` | **0** |
| `dealing` | **0** |
| `subscrib*` | **0** |
| `\bunit` | **1** — "Financial Intelligence Unit- India" |

The core conclusion is **correct and stronger than stated**: the string "NAV" does not occur anywhere in
the workbook. There is no NAV per unit, no units outstanding, no dealing price and no dealing date, so
the CSSF Table 4/5 compensation arithmetic and the COLL 6.3.6G per-unit test are both uncomputable from
this artefact. **Part 14.5 ("delete NAV-per-unit from every data model") stands.**

**The correction.** Part 8 states *"The complete NAV-adjacent surface of the artefact is:"* and then
lists seven cells. It is not complete. Sheet `2. Summary` row 4 carries a per-scheme flow block the
table omits entirely:

| Cell | Label |
|---|---|
| J4 | Cumulative commitments raised, as at the end of quarter (USD Million) |
| K4 / Q4 | Cumulative funds raised, as at the end of quarter (USD Million) |
| R4 | Funds raised during the quarter (USD million) |
| **S4** | **Cumulative redemptions, as at the end of quarter (USD Million)** |
| **T4** | **Redemptions during the quarter (USD Million)** |
| U4 | Net Inflow(+ve)/Outflow(-ve) during the quarter (USD Million) |
| P4 | Cumulative distributions made, as at the end of quarter (USD Million) |
| H4 / I4 | No. of investors who have contributed / who have committed |

The lane's Part 8 search patterns were `NAV | net asset | valuation | valuer | corpus | AUM` and
`unit | per unit | outstanding | NAV per`. None of those match "redemptions", "funds raised" or
"commitments", so the omission is a **false negative produced by an under-inclusive grep** — the same
failure mode as RND-BRIEF §4.4, in the lane that diagnoses it. The prose sentence *"no subscription or
redemption **struck at a price**"* is carefully worded and remains true; the table's claim to be
*complete* is not.

**Damage: contained but real.** The return does carry per-scheme net assets, gross subscriptions,
gross redemptions and investor counts, quarterly. That is enough to support flow-consistency and
identity predicates on the valuation axis (e.g. cumulative-vs-period redemption monotonicity;
`net inflow ≈ funds raised − redemptions`; AUM roll-forward) that Part 12 does not propose. **Part 12's
"keep exactly two predicates and nothing more on the valuation axis" is under-scoped against the
artefact's actual content.** Fix the Part 8 table before it reaches a slide — an audience member with
the workbook open will find S4 and T4 in under a minute, and Part 8 is the pillar of the Part 12
judgement.

### 2. Part 9.1 — the scheme-count defect — **CONFIRMED**

Read from raw OOXML. Reproduced exactly and verbatim:

```
D17 = SUM(D18:D20)          label: "Total No. of Schemes of the FME authorised by IFSCA"
D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")
D19 = COUNTIF(G54:G63, "*Restricted*")
D20 = COUNTIF(G54:G63,"*Retail*")+COUNTIF(G54:G63,"*Exchange Traded Fund*")
```

`G54:G63` is governed by an `x14:dataValidation` of `type="list"` with `formula1 = Dropdown!$F$3:$F$11`.
`Dropdown!F3:F11` reads exactly: Venture Capital Scheme · Angel Scheme · Restricted Scheme (Category
I) · (Category II) · (Category III) · Retail Scheme · Exchange Traded Fund · **Special Situation
Fund** · **Family Investment Fund**. F12 is empty, so the vocabulary is exactly nine.

Neither "Special Situation Fund" nor "Family Investment Fund" contains any of the five COUNTIF
substrings. The defect is real, and the demo is reproducible in thirty seconds as claimed.

*One point an adversary will press, and it is answerable.* The three sub-rows are labelled by category
("No. of Venture Capital Schemes (including Angel Schemes)", etc.), so a defender could argue D17 only
ever meant "total of these three". The answer is the label on D17 itself — *"Total No. of Schemes of
the FME authorised by IFSCA"* — which is unrestricted. Quote that label on the slide; the argument
turns on it.

### 3. Part 9.2 — 54 validations / 22 vocabularies — **CONFIRMED**

Parsed each `xl/worksheets/sheetN.xml`, splitting the sheet body from `<extLst>` before counting. My
per-sheet counts reproduce the lane's table cell-for-cell: **35 standard (3 list) + 19 `x14` (19 list)
= 54 total, 22 list-type.** The `7. AML-CFT` row reproduces as **0 standard / 5 x14** — under the
default `openpyxl` lens that sheet has zero validations and actually has five.

I went one step further than the lane and checked whether all 22 list validations reference a *named*
vocabulary rather than an inline literal. They do: 20 point at `Dropdown!$X$n:$X$m` ranges, and 2 at
defined names (`Choicelist`, and `IF(C5="No",Choicelist,YesNolist)` on `'8. Compliance Status'!C10:C11`).
**"22 list-type with a named vocabulary" is exact, not approximate.** Part 14.1's regression test
asserting `54` and `22` against the workbook hash is well-founded; use the SHA-256 above.

*Housekeeping only:* the lane's Part 9.2 table lists nine sheets and omits `9. Compliance Report`. That
sheet has 0 standard and 0 x14 validations, so **no total is affected** — but the workbook has ten
sheets, and the table should say so.

### 4. Part 2.2 — Ireland — **CONFIRMED**

Re-downloaded from centralbank.ie. Title reads off the page verbatim: **"S.I. No. 316 of 2026 — CENTRAL
BANK (SUPERVISION AND ENFORCEMENT) ACT 2013 (SECTION 48(1)) (UNDERTAKINGS FOR COLLECTIVE INVESTMENT IN
TRANSFERABLE SECURITIES) REGULATIONS 2026"**. Extraction: **5,060 lines** — identical to the lane's.

My greps, run independently:

| Pattern | Hits |
|---|---:|
| `materiality` | **0** |
| `toleran*` | **0** |
| `redress` | **0** |
| `de minimis` | **0** |
| `rectif*` | 1 |
| `compensat*` | 2 |
| `error` | 7 |
| positive controls | `net asset value` **37** · `valuation` **48** · `shall` **485** |

I also read every hit in context, which the lane asserted but did not print. The characterisation holds:
5 of the 7 `error` hits are "tracking error"; the other 2 are a client-funds recordkeeping error
("*there has been an error in recordkeeping or in the reconciliation of accounts*" … "*shall notify the
Bank without delay of the error, the reasons for its occurrence and its correction*"). The 2
`compensat*` hits are the **dilution levy** definition and a performance-fee *"compensation for past
underperformance"* — neither is investor redress. The 1 `rectif*` hit is a management company's
regulatory-capital position.

**This is the lane's strongest claim and it survives cleanly.** Note the sharp irony my context-read
surfaces: Ireland *does* impose an immediate error-notification duty in these Regulations — for client
**recordkeeping**, not for NAV. That makes the absence a choice rather than an oversight, which is a
better version of the argument than the lane makes.

### 5. Part 1.2 / 1.5 — CSSF 24/856 — **CONFIRMED**

Re-downloaded `CSSF24_856eng.pdf`; extraction **2,622 lines**, identical to the lane's. Read off the
page:

- Header: *"Circular CSSF 24/856 … Luxembourg, 28 March 2024"*. Point 162: *"This Circular enters into
  force with effect from 1 January 2025."* Point 166: *"Circular CSSF 02/77 is repealed upon the entry
  into force of this Circular."*
- **Table 1** MMF governed by the MMFR **0.20%**. **Table 2** bond **0.50%** · mixed **0.50%** · equity
  **1.00%** · other eligible assets **1.00%**. **Table 3** identical, with the footnote *"'Other assets'
  refer, for example, to unlisted shares, buildings, loans or eligible investments for ELTIFs."*
- Point 35(d)(iii) verbatim: *"The tolerance threshold must not exceed 5% of the NAV. In no case are
  UCIs permitted to use by default the 5%-threshold…"*
- Point 138 verbatim: *"the total compensation amount exceeds EUR 50,000 or the compensation to be paid
  out to one single investor exceeds EUR 5,000"*, with the aggregation gloss on "total compensation
  amount" exactly as quoted.
- Point 38 aggregation paragraph: verbatim match, word for word.
- Point 158: *"the deadline for notification is 4 to 8 weeks at the latest after the date on which the
  error/non-compliance has been detected"* — verbatim.
- Point 159: *"the corrective actions indicated in the notification form by the UCI are not subject to
  the CSSF's approval"* — verbatim. The declaration-not-approval reading is sound.

**Every number Part 14.4 proposes to write into the Unchecked panel's "what would make it checkable"
text is correct at source.** That text can ship.

### 6. Part 1.7 — the base rate — **CONFIRMED**

`CSSF_RA_2024_EN.pdf`, 160 pp, extraction **8,875 lines** — identical to the lane's. §4.1.2 and §1.2
read off the page. Every figure in the lane's table reproduces: NAV calculation errors **462 / 344 /
234**; non-compliance **1,382 / 1,265 / 1,297**; total declarations **1,609 (2023) / 1,531 (2024)**;
normal-procedure notifications **148 / 107**; investor compensation **21,187,863.80 / 49,601,054.10 /
11,810,270.57**; UCI/sub-fund compensation **26,901,611.60 / 14,109,720.70 / 8,571,914.50**. CSSF's own
sentence — *"the total amount of compensation still remained moderate as compared to the total amount of
assets under management"* — is verbatim.

Denominators verified at §1.2, stated *"as at 31 December 2024"*: **3,143 UCIs registered on the
official list · 13,599 fund units · EUR 5,820 bn net assets.** I recomputed every derived figure:
234/13,599 = **1.72%** ✓ · 234/3,143 = **7.44%** ✓ · 107/1,531 = **6.99%** ✓ · sum
= **EUR 20,382,185.07** ✓ · /5,820bn = **0.00035%** ✓ · mean **EUR 87,103** ✓ · 234 + 1,297 = 1,531 ✓.

**This is the one claim in the lane where a number carries both numerator and denominator from the same
document, and it holds.** The lane's own three caveats — flow-over-stock, MODELED mean, old-circular
cohort — are each correct and each necessary. Part 14.6's ban on importing 1.72% as an FFR prior is
well-founded and should be enforced.

### 7. Part 3 — the aggregation conflict — **CONFIRMED**

FCA Handbook COLL 6.3, live page. All four quoted elements returned verbatim: the depositary's immediate
report at *"0.5% or more of the price of a unit"*; minimal significance at *"less than 0.5% of the
correct price"*; *"if the instance of incorrect pricing is due to one or more factors or exists over a
period of time, each price should be considered separately"*; and the `SUP 16.6.8 R` quarterly return.

Set against CSSF point 38 (verified verbatim above), **the conflict is real and directly evidenced from
two primary sources.** Part 14.3 — that L6 relations must carry the instrument that authorises them —
is the best-supported design change in this lane. It rests on two clauses I read myself, not on a
secondary characterisation.

### 8. Part 7.1 — the IFSCA gap — **CONFIRMED**

Both instruments re-downloaded from ifsca.gov.in and re-grepped.

**FM Regulations 2025 as amended to 30 Jan 2026** — 102 pp, **3,963 lines** (identical). `NAV error` 0 ·
`valuation error` 0 · `incorrect NAV` 0 · `toleran*` 0 · `swing pricing` 0 · `de minimis` 0 · `restat*`
0 · `materiality` **1** · `compensat*` **1** · `error` **5**. Positive controls: `shall` **728** ·
`valuer` **32** · `true and fair` **6** · `Sixth Schedule` **5**. Every count matches the lane's.

Context-read of the non-zero hits, which the lane asserted: the 5 `error` hits are **3 × "tracking
error"** and **2 × "Combating the Financing of Terrorism"** — exactly as claimed. `materiality` is
*"the decision to determine materiality shall be that of the Authority"* in a disqualification
provision — unrelated, as claimed. The single `compensat*` hit is Third Schedule Part A(g), verbatim:

> *"(g) The FME and its controlling shareholders shall be liable to compensate the affected investors
> and/or the scheme for any unfair treatment to any investor as a result of inappropriate valuation."*

with (f) immediately preceding it, also verbatim as quoted. **Part A(g) is confirmed as a liability rule
with no trigger.**

**FM FAQ, 3 Aug 2026** — 68 pp confirmed from the PDF catalogue. `error` **0** — the bare substring does
not occur. Positive controls: `NAV` **13** · `valuation` **5** · `valuer` **6** · `shall` **183** ·
`scheme` **405**. Every one matches.

*One extension in the lane's favour.* The lane says regs 27/39/51 each carry a sub-(2) using "should"
rather than "shall". **It is four, not three** — reg **69(2)** (ETFs) carries the identical sentence.
The soft-modal observation is stronger than stated.

### 9. Part 11 — OpenIM entity E-36 — **UNVERIFIABLE**

`github.com/antikas/open-investment-model` exists; **MIT, 3 stars, 0 forks, 30 commits** — confirmed.
The self-description as a *"reference model"* rather than a design blueprint is confirmed.

But the lane marks this row `VERIFIED (repo opened)` and attributes to it a specific entity — **E-36
"Oversight Exception", with a `shadow_nav_difference` exception type, `severity` ∈ {minor, material,
significant}, `monetary_impact_amount` and a lifecycle `status`.** I searched the repository README and
**none of "Oversight Exception", "E-36", "shadow_nav_difference", "shadow NAV" or
"monetary_impact_amount" appears.** The claimed version **v0.3.0** also did not resolve to any release
or tag I could see. The README describes 86 entities, so the entity may well live in a file I did not
reach — but I could not reach it, and with no search budget I could not locate the entity index.

**Status: NOT-FOUND, not "probably fine."** Damage is minimal — the lane's own verdict is **REJECT for
reuse** and it explicitly says "depend on nothing" — but the row's warrant should be downgraded from
`VERIFIED` to `SECONDARY / entity NOT-FOUND`, and no field name from E-36 should be copied into L5's
vocabulary on this citation alone.

### Also spot-checked, and clean

- **CBI CP130** — re-downloaded, **669 lines** (identical). Proposed thresholds **MMF 0.10% of NAV /
  other funds 0.50% of NAV**, stated twice as the lane says. The four error types (NAV, Investment
  Breach, Fee, Control Breach) verbatim. Industry de minimis *"€50 for retail investors and €500 for
  institutional investors"* verbatim. **Both footnotes verbatim**, including the IOSCO Principle 5 text
  and the IMF 2014 line *"the Central Bank has not issued rules prescribing how pricing errors are to be
  treated by CIS."* Closing date 9 December 2019 confirmed in the body. The lane's discipline in
  quoting IOSCO at one remove, and refusing to cite an IOSCO document number, is correct and should be
  preserved.
- **daappa NAV Error Materiality Calculator** — the page is live and is a **free, no-signup,
  runs-in-browser** tool encoding CSSF 24/856: 0.20% / 0.50% / 0.50% / 1% / 1%, "up to 5% with
  documented analysis", the four-to-eight-week notification window, and the EUR 50,000 / EUR 5,000
  auditor triggers. **Part 12 argument 4 — that the arithmetic is already commoditised where the regime
  exists — is confirmed at source.**

### What this changes

**Nothing in Part 12's judgement.** The five observations behind "prescribed-return verification, not a
NAV-error regime" are each verified: the artefact carries no per-unit price (1), Ireland has no rule
(4), the CSSF/FCA disagreement is real so materiality is a jurisdictional parameter (5, 7), the
calculator is already free (daappa), and the first-hand defects are reproducible (2, 3). The wedge
choice is sound.

**Two edits before anything ships:**

1. **Rewrite the Part 8 table.** Drop the word "complete", add the `2. Summary` flow block, and restate
   the finding as its true and narrower form: *the return carries fund-level net assets and gross
   subscription/redemption flows, but no per-unit price, no units outstanding and no dealing date — so
   no NAV-error rule on earth can be evaluated against it.* Then **revisit Part 12's two-predicate
   cap**, because flow-identity predicates over S4/T4/U4/V4 are computable from fields that are
   actually filed and are currently unclaimed.
2. **Downgrade the OpenIM row** from `VERIFIED` to `SECONDARY / entity NOT-FOUND`.

Everything else in this lane can be quoted as written.
