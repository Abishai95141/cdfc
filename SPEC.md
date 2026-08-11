# THE COVERAGE-DECLARING FILING CHECKER
## Authoritative build specification · compiled 10 August 2026

**This document supersedes `RND-BRIEF.md`, `ARCHITECTURE.md` and the three intermediate drafts
(`research/synthesis/A`, `B`, `C`) wherever they conflict with it.** It was produced by fifteen research
lanes with adversarial verification on the load-bearing ones, reconciled against a ruling that resolved
31 contradictions between the drafts, and audited for whether that ruling landed. Where a lane opened a
primary source and the adversarial pass did not refute it, the lane wins.

**Read a number in this document with the label attached to it.** MEASURED (computed first-hand against
an artifact on disk, script named) · VERIFIED-AT-SOURCE (the primary document was opened and the clause
read off the page) · SECONDARY (a credible source describes it; the primary was not opened) · DERIVED
(arithmetic on stated inputs; carries the warrant of its weakest input) · MODELED (an assumption) ·
UNMEASURED / NOT-FOUND (we looked and could not settle it — a legitimate and required answer).

---

## THE ONE-PAGE VERSION

**The problem.** Every quarter each of the 217 fund managers licensed at GIFT City returns a spreadsheet
the regulator publishes. The only thing in it resembling a verdict is a Yes/No cell in which the manager
attests that its own valuations comply; nothing in the other 6,756 cells can contradict it. That is a
green tick with no denominator, and it is the general case — an audit opinion, a filing sign-off and a
sanctions disposition all end in *nothing wrong here*, and none of them says what was looked at.

The scarce quantity is not error detection. Detection is solved and cheap. The scarce quantity is **an
attributable, per-check, measured statement of how often that check is wrong, carried next to the finding
it produced, together with a computed declaration of what was not touched.** No product or published
system opened in this research prints either object for a regulated financial filing.

**What we are building.** A checker for a prescribed regulatory workbook that reports what it did not
check. It induces the field graph from the regulator's *blank* template — 505 formula-bearing cells, 54
data validations, a 3,747-cell filer-editable surface — harvests 280 executable predicates from what the
template already encodes, **with no model**, and admits a predicate to the active set only after
measuring its kill rate against seeded defects, proving it is not the flag-everything baseline, and
measuring its false-failure rate on a corpus its authors did not write. Every filing returns a signed
report carrying two counts of equal weight, a typed reason for every unsettled property, each firing
check's own error rate, and a replay proving the checks were alive on that document. **There is no field
in the schema where a downstream consumer could write "pass."**

**Why the parts need each other.** Each component alone is defeated by a measured fact, and each one's
failure mode is another's input. SPADE's own paper says its false-failure rate cannot be computed because
the example universe is unknown — seeded defects manufacture that universe with certain ground truth.
Seeded defects say nothing about properties with no oracle — differential relations over the
workbook-as-program settle some without one. Relations can be trivially true — the degeneracy gate
rejects them, and has already rejected five real predicates that assert only "this is a number" over
1,428 cells. The built path runs in **~30 ms** (MEASURED) and the verdict path is **specified to make zero
model calls, with the CI assertion listed as a build gate and not yet written** — so `pass^k` decay does
not apply to it by construction, but say "specified", not "does", until `test_no_model_in_verdict_path`
exists.

**What could kill it, in order.**
1. **The application portal returned HTTP 404** and nobody has seen the live form. Applications close
   **16 August**. Ten minutes in a browser settles it. This is the only item that can end the programme.
2. **IFSCA may already run these checks on receipt**, which makes the filer-side product a convenience
   rather than a gap. One email settles it and it is unsent.
3. **The headline 63.3% is computed from 280 predicates of which none is admissible under our own gate**,
   because no false-failure rate has been measured for any of them. A judge who connects those two facts
   wins — unless we say it first, which §IV.4.1 step 2 does, and which turns the objection into the
   strongest moment in the demo.
4. **The method may not transfer past one workbook.** Nine are already on disk to find out, and the
   measurement needs no model and no corpus.

**What to do first.** Open the portal and screenshot every field. Send the IFSCA email. Run the transfer
measurement. The settling experiment on whether a model can write a regulator-grade check costs about
thirteen dollars and belongs *after* all three, because it can only tell us how large the model's role is —
not whether anyone wants the thing.

---

## THE SIX DECISIONS THAT DETERMINE EVERYTHING DOWNSTREAM

| # | Decision | Beat | Because |
|---|---|---|---|
| 1 | **The unit of the denominator, of closure and of the settled fraction is the CELL** — the filer-editable, unlocked, non-formula cell | the `(field × obligation)` pair | Every quantity actually measured is a cell count. The pair model's `obligationsTotal` and `pairsTotal` had no derivation anywhere in the corpus and appeared with three mutually incompatible values |
| 2 | **The predicate language is CEL, admitted subset only, inside a three-slot envelope** (`applicable` / `expr` / `witness`) | generated Python; Rego; VTL; Great Expectations | Non-Turing-complete and terminating, so a confused model cannot write a predicate that hangs or reaches the filesystem; readable by an auditor; mechanically mutable; and the sandbox problem disappears rather than being contained |
| 3 | **L3 — the model — runs at build time, per template version, never per filing** | a model in the request path | Per-filing model cost is $0.00 and the report re-derives byte-identically. The verdict path is *specified* to make zero model calls so that `pass^k` decay cannot apply to it; that becomes a property of the system on the day the CI gate is written, and not before |
| 4 | **A predicate with no qualification record does not load** | admitting hand-authored checks and measuring later | The settled-fraction claim is then true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement. It is also why the currently defensible settled fraction is 0% and we say so on stage |
| 5 | **The verdict has eight closed item states and thirty namespaced reason codes; `cells_bound == 0` is an `ERROR` that makes the run `INVALID`, never a `PASS`** | the brief's single `UNCHECKED` token | A predicate that bound to nothing is the vacuous-pass failure the whole design exists to catch. Collapsing it into "unchecked" puts it in the same bucket as a rate-limited register |
| 6 | **The attestation's top-level object is `scope`, and the schema has no `result`, `status` or `pass` field at any depth** | signing a verdict | A surface that can render all-clear will eventually render it wrongly. Prohibiting it in the schema, and grepping for it in CI, is the only version of that commitment that is a system property rather than a preference |

---

## WHAT IS GENUINELY NEW, STATED AT SURVIVABLE STRENGTH

> **No product or published system, for any regulated financial filing, (a) admits a check into its
> active set only after measuring that check's own false-failure rate on a declared clean corpus and its
> kill rate against seeded defects, and (b) returns, alongside the verdict and signed with it, a computed
> per-field machine-readable declaration of which correctness propositions were not settled and why.**

For a slide: *everyone ships rules; nobody ships each rule's error rate, and nobody ships the residue.
We make both a product surface, and sign them.*

Three further claims are novel in their own right and were nearly lost to over-hedging. They are restored
in §I.5.1 and each is falsifiable:

- **The residue is a theorem, not a coverage gap.** A prescribed return is a closed arithmetic system. We
  can construct and exhibit a family of filings that are internally perfect under every relation the
  regulator's own template encodes and every relation we add — and materially false. In code mutation
  testing a mutant that changes behaviour is in principle killable by some test; here a mutant can change
  the *truth* of the artifact and be **provably unkillable by any predicate over the artifact alone**.
  That family is non-empty by construction and its size is measurable.
- **`INVALID` is a liveness proof, not a self-test.** No assurance artifact in existence carries evidence
  that the instrument that produced it was working on the specific document it examined. A clean audit
  opinion does not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict
  unless every check has just demonstrated, on your file, that it can still catch the fault it was
  admitted for.
- **The criterion source is citable, versionable and watchable — not more authoritative.** SPADE infers
  what correctness meant from the traces of a developer changing their mind. We do not have to infer it.
  The criterion is a published instrument with a version, an amendment chain machine-followable in 76 of
  82 cases, and a blank template with a content hash. It is *not* more authoritative — the regulator's own
  template computes a scheme total that misses two of its own nine legal values — but it can be cited,
  re-qualified when the clause moves, and quarantined the day a circular changes the rule.

**The honest limit, which stays permanently on the report surface:** *this system detects error, not
deception. Every check here is a consistency check over a self-reported document. A coherent liar passes
all of them.*

---

## WHAT THE RESEARCH KILLED

Recorded here because re-exploring any of it is wasted work, and because two of these were the brief's
own headline claims.

| Killed | By what observation |
|---|---|
| *"No measured system can say 'this one is clean'"* | Refuted from inside the brief's most-cited source. On FinVerBench's 43 clean statements Claude Sonnet 4 scored FPR **0.0%**, precision 100, recall 100, under the same guided-checklist prompt where seven of fourteen other complete runs flagged 43 of 43. The surviving statement is narrower and better: **a machine can be calibrated, and nothing in its output says whether it was** |
| *"Zero financial regulations encoded anywhere"* | EBA publishes 12,925 rule-instances (8,052 distinct), EIOPA 6,767, ESMA 68, XBRL US DQC ~196, FINOS CDM 640 named conditions. What is empty is the *civic* rules-as-code shelf — Catala and OpenFisca are entirely tax, benefit and pension, positive controls passed |
| *"No analogue exists for a financial assertion"* | ISA 705 ¶24 and ISRS 4400 ¶30(j) are financial and mandatory; ESMA publishes a per-rule `Automatable: Yes/No`, 8 of 68 declared No, six of them `MUST`; XCCDF Table 26 has nine per-item result states |
| *"CycloneDX `compositions.aggregate` — a ten-state enum since 1.2"* | The field first appears in **1.3 with six states**; the ten-state form arrives in 1.5. It is *aggregate*, not per-item |
| **The NAV-error wedge** | The string `NAV` does not occur in any XML part of any of the nine prescribed workbooks (MEASURED, positive controls: `Scheme` 123, `USD Million` 31, `Portfolio` 25, `valuation` 6). No NAV per unit, no units outstanding, no dealing price. Every NAV-error rule on earth operates on exactly those quantities. The *domain fact* — that CSSF publishes thresholds and IFSCA publishes none — stays as framing. The *product* does not |
| **The supervisor as a user** | That seat is procured: NEC Corporation India, 27 January 2026, ₹39,57,36,115.52, RE-facing portal explicitly in scope. The supervisor is not the buyer; the supervisor is why the filer cares |
| **The five original metamorphic relations** | Row reorder, zero-holding insertion, duplicate consolidation, unit scaling and currency round-trip all require NAV-shaped quantities the workbook does not contain. Replaced by differential probes over the workbook-as-program, including one nothing else in the design can do: detecting a formula cell overwritten with a literal |

Nine further withdrawn numbers, each with the evidence that moved it, are in §I.6 — **the ban list, which
is the section to read before a pitch.**

---

## HOW THIS DOCUMENT IS ORGANISED

| Part | What it settles |
|---|---|
| **I — The problem, the evidence, and the claim** | What the problem is and who has it; every load-bearing quantity with its warrant and denominator; what we are building and what it is not; the domain grounding; what is genuinely novel and the three strongest objections with their rebuttals; the ban list |
| **II — The architecture** | The layers with exact input and output types, which contain a model, their failure modes and their self-checks; the corrected data flow; the verdict model (eight states, thirty reason codes, the seven-term closure invariant, the five-rule evaluation contract); the predicate model and the five qualification gates; the report and its signing envelope |
| **III — The technology stack and the backend flow** | Every technology decision with the runner-up it beat and the condition to switch; the adopted open-source ledger with licences at their real warrant; the fifteen-step online flow and the eight offline flows; the data model and re-derivation proof; performance and cost; the API and the screens |
| **IV — The path, the deliverable, and what is open** | The experiment queue with pre-registered thresholds; the dated plan to 16 August, 21–22 August and the residency; the do-not-build list; the demo script line by line with every on-screen number's provenance; the acceptance criteria as CI tests; the risk register; twelve engineering gaps each decided or explicitly open; **seven questions only you can answer** |
| **V — Audit** | The independent check that the reconciliation ruling landed, with every edit made |

Supporting research is in `research/lanes/` (fifteen lanes, ~200,000 words, several carrying an appended
adversarial-verification pass), `research/synthesis/` (the superseded drafts and the reconciliation
ruling), and `research/scripts/` (the harnesses that produced every MEASURED number here).

---


# PART I — THE PROBLEM, THE EVIDENCE, AND THE CLAIM

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


---

# PART II — THE ARCHITECTURE

## II.0 — How to read this part

Every number carries a **warrant** and a **denominator**: `MEASURED` (we ran it on the artifact),
`VERIFIED-AT-SOURCE` (a primary source was opened and quoted), `SECONDARY` (reported by a source we did
not re-open), `DERIVED` (arithmetic over other numbers), `UNVERIFIED` (asserted nowhere we checked). A
derived number never claims a stronger warrant than its weakest input. Every decision below is written as
**DECIDED**, with the alternative it beat and the reason, or as **OPEN — USER DECISION** with the exact
question. There are no implicit choices in this part.

Three global renames are normative from here and are not repeated at every occurrence:

| Was | Is | Why |
|---|---|---|
| `coverage`, `coverageFraction`, `GET /v1/coverage/history` | **`settledFraction`**, `GET /v1/settled-fraction/history` | "coverage" is the conformal guarantee's word and it appears three pages away in that sense |
| `micro_units`, "integer micro-units" | **`MILLI_USD_MILLION`** — an `int64` count of 10⁻³ USD Million, 1 unit = USD 1,000, `12.34 → 12340`, half-ulp = 5 units, `τ(n) = 5n` | Two definitions differing by 10³ were live, and every tolerance in the design is expressed in units. **DECIDED** in favour of the definition that derives from guidance C111's two-decimal USD Million quantum. Alternative it beat: "micro-units", which had no derivation |
| `METAMORPHIC` (as a `method` value) | **`DIFFERENTIAL`** | Metamorphic testing requires a re-executable system under test; a filed workbook is a record. A correct small claim beats a large unbuildable one |

---

## II.1 — THE LAYERS, REVISED

### 1.0 What is actually built — the ruling, verbatim

> **"Schema induction, predicate harvest, arithmetic evaluation and the coverage denominator are built and
> reproduce in ~30 ms. Template binding, pre-flight, closure, canaries, attestation and `verify` are
> specified and not built."**

("Coverage denominator" in that ruling is the settled-fraction denominator; the rename above applies.) Any
sentence of the form *"L1→L5 runs end-to-end"* overstates it and must not be used. The honest form is:
*schema induction, predicate harvest and arithmetic evaluation run end-to-end in ~30 ms (MEASURED, single
run, cold, single process, one workbook); the verdict model, closure, canaries and attestation are
specified and unbuilt.*

Likewise: **the verdict path is specified to make zero model calls, and the assertion is listed as a build
gate; the gate is not yet written.** It is not yet a property of a running system.

### 1.1 The layer table

| Layer | Exact input | Exact output | Model? | Status |
|---|---|---|:--:|---|
| **L0 INGEST** | `bytes` (filing, blank template, instrument PDFs) + `HTTP GET spec` (register) | `ContentAddressedBlob{sha256_original, media_type, retrieved_at, origin_uri, parse_a, parse_b, agreement{field→bool}}`, `RegisterSnapshot{sha256, fetched_at, endpoint, records[]}`, `ExtractionManifest` | **No. Never.** | **PARTIALLY BUILT** — readers A and B built; container guard and the agreement check specified |
| **L1 SCHEMA INDUCTION** | the **blank template** blob, pinned by hash — never the filing | `TemplateSchema{template_sha256, fields{stable_key→Field}, vocabularies, carry_edges, field_surface[], manifest}` | No | **BUILT** — 28–44 ms (MEASURED) |
| **L1b CLAUSE GRAPH** | instrument PDFs | `Instrument{frbr_uri, as_at, pdf_sha256}` + `Clause{eId, text, charspan, bbox, provisos[], xrefs[]}` + `Amendment{src, tgt, effective_date, resolved}` | No (Docling is a parser, not a judge) | **SPECIFIED — nothing of L1b is built** |
| **L2a STRUCTURAL EXTRACTION** | filing blob + `TemplateSchema` + `RegisterSnapshot` | `Fact{key, value, unit, provenance_anchor, warrant=DETERMINISTIC}` | No | **BUILT** (fact-table construction) |
| **L2b DOCUMENT EXTRACTION** | unstructured attachment bytes + `TemplateSchema.stable_keys()` | `Fact{…, warrant=MODEL_EXTRACTED}` or an abstention | **Yes — contingency only** | **SPECIFIED / GATED** (see the pre-flight gate below) |
| **L3 CANDIDATE PROPOSAL** | `TemplateSchema` + `ClauseGraph` + the 505-cell native formula graph | `CandidatePredicate[]` — the §II.4 envelope, containing **CEL**, not Python | **Yes — the only model in the system, build time only** | **SPECIFIED** (the settling experiment is unrun) |
| **L4 QUALIFICATION** | `CandidatePredicate` + `TemplateSchema` + `CleanCorpus{provenance, n}` + `FaultModel{version}` | `AdmittedPredicate` with a **required** `qualification` block, **or** a typed `rejection` row | No | **PARTIALLY BUILT** — see the gate-by-gate status in §II.4.3 |
| **L5 EXECUTION AND VERDICT** | `AdmittedPredicate[]` pinned by registry root + `Facts` + `TemplateSchema` | one `Item` per **cell** (§II.3) + the computed scope object | **No. Zero model calls.** | **PARTIALLY BUILT** — arithmetic evaluation built; pre-flight and closure specified |
| **L6 DIFFERENTIAL & INVARIANT PROBES** | the fact table + admitted relations + the pinned blank | per relation: `PASS / FAIL / INFORMATIONAL(advisory) / OUT_OF_SCOPE(precondition unmet)` | No | **SPECIFIED** |
| **L6.5 SELF-CHECK AND RESIDUE** | the filing, the admitted set with its stored witnesses, the L5 result | `{canaries_run, canaries_passed, dead_predicates[], residue: ResidueSet, run_state: VALID\|INVALID}` | No | **SPECIFIED** |
| **L7 ATTESTATION** | the L5 scope object + L6 results + L6.5 proof + every content hash + the registry root | DSSE envelope over an in-toto Statement v1, one self-contained `report.html`, `run.jsonl`, declared-lossy OSCAL projections, an RO-Crate evidence crate | No | **PARTIALLY BUILT** — report render partial; attestation and `verify` specified |

**L6 is a loop over L0–L5 on transformed inputs, not a box after L5**, and its relations pass the same L4
gate as any other predicate. Drawn as a downstream stage it teaches the wrong mental model and implies
relations are self-validating. They are not: a violated relation means *the artifact is wrong* **or** *our
relation is wrong*.

### 1.2 L0 — INGEST

**Kills it, all observed on this artifact.** *Namespace blindness* — a reader that cannot see
`<x14:dataValidation>` reports **35** validations where there are **54** (35 main + 19 `x14`) and reports
the AML-CFT sheet as having zero where it has five; MEASURED on both a hand-written regex and openpyxl
3.1.5, **two independent instruments producing the identical wrong number by the identical mechanism, with
no error reaching a log**. *Shared-formula invisibility* — 211 of 505 formula cells are
`<f t="shared" si="N"/>`, an element with no text, so a text-matching pass loses 41.8% here and
**825 of 1,495 = 55.2%** across the nine workbooks (MEASURED); the loss concentrates on row and column
totals, so **the measurement error is correlated with the quantity being measured, in the direction that
supports the thesis** — the most dangerous shape an instrument error can take. *Destructive round-trip* —
an openpyxl load-and-save with nothing edited takes the workbook from 3,663,391 to 65,877 bytes and deletes
all 19 `x14` validations (MEASURED). *Register mutability* — the register is live and undated.
*Reading the wrong field* — `EncryptDId` is null in 2,005 of 2,005 records while `EncryptedId` is populated
in 2,005 of 2,005; keying on the first returns HTTP 302 on every record forever and yields an
honest-looking absence. **The corrected finding: the list endpoint returns `RegistrationNumber = null` on
650 of 650 fund rows, while the detail endpoint returns it on 228 of 228 live FMEs (VERIFIED-AT-SOURCE).**
*Zip and XML bombs* — an `.xlsx` is a zip of XML supplied by an adversarial-capable party, so entry count,
per-entry uncompressed size and total ratio are checked **before** parse, and `lxml` runs with
`resolve_entities=False`, no DTD and no network.

**Self-check.** Dual-parser agreement over `{n_sheets, sheet_names, hidden_sheets, n_cells,
n_formula_cells, n_validations, n_defined_names, merged_ranges}`. Disagreement on the first three makes the
run **`INVALID`** — the scope is not established, so nothing computed on top of it means anything.
Disagreement elsewhere marks those fields and every predicate reading them returns
`NOT_RUN(not_run.extractor_disagreement)`: the settled fraction falls, it does not silently succeed. The
extraction manifest (parts read, parts skipped, namespaces seen, constructs not understood) is a
first-class output, not a log. **No absence is reported without a declared positive control.** Evidence
this step earns its thirty lines: three implementations of this parse returned **244, 294 and 505** on the
same file on the same day, two of them in the same directory, and the divergence went undetected inside
the authoritative document.

**Components.** Authoritative parse: **raw `zipfile` + `lxml`** (stdlib / BSD), beating **openpyxl as the
schema authority**, which drops all 19 `x14` validations behind a `UserWarning` nobody reads; openpyxl is
retained only for row-shifting shared formulas (verified: `O4 → '=SUM(C4:N4)'`) and for writing mutants.
Register access: **one `GET DirectoryGetList` + one `GET DirectoryDetailGet?EncryptedId=…` per entity**,
snapshot content-addressed; state the plan as *1 list request + N detail requests, N = |records|*, and
report the actual request count of the run that produced the snapshot hash. **A figure of 2,235 requests
was carried in the drafts and is withdrawn to UNRECONCILED:** it matches neither `1 + 650 = 651` (the fund
population) nor `1 + 2,005 = 2,006` (the whole register), no document states the `N` it belongs to, and the
run cannot be re-executed from the artifacts on disk. Re-fetch under the stated plan, record the count in
the manifest, and quote that. Until then the fetch plan is quoted in its **form** — `1 list request + N
detail requests` — and never as an integer, which is the same rule this system applies to a filer. It beat **scraping the rendered page**, which is client-rendered with zero data
rows in the HTML. Parser sandbox: **gVisor (`runsc`) + `seccomp` + `--network=none` + read-only rootfs +
RLIMIT + wall-clock kill**, beating **Firecracker** (hypervisor isolation against an adversary we do not
have, at a VM per filing), **E2B** (the filing leaves our boundary — a data-residency conversation about
regulated filings we should not have to have) and **Pyodide/WASM** (the Grist "Cellbreak" escape,
`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, escaped a Pyodide sandbox by three independent routes and was fixed by
putting Deno's permission system underneath it — **WASM-of-CPython is a resource boundary, not a security
boundary**).

**LibreOffice — DECIDED: excluded from the verdict path entirely.** It sees the truth (it expands all 505
formulas to text and migrates the `x14` validations into the main namespace) but **writes 53 where
35 + 19 = 54: one validation lost, unexplained, in the very step being recommended.** It therefore runs
offline only — template admission and diagnosis — pinned by container digest. A verdict run never invokes
it; a run that would need it either terminates `INVALID` or marks the affected fields
`NOT_RUN(extractor_disagreement)`. *Alternative it beat:* pinning it by digest and keeping it inline —
rejected because an uncharacterised one-validation loss would then sit inside the programme's own
byte-identity acceptance test (§II.5.4).

### 1.3 L1 — SCHEMA INDUCTION

**What the induction recovers**, MEASURED on `sha256 7d9a…` and reproduced independently by four lanes and
one adversarial pass: 10 sheets (9 visible + `Dropdown`, `state="hidden"`) · 6,757 `<c>` elements · **505**
formula-bearing cells = 294 authored expressions + 211 shared dependents · 138 of 505 (27.3%) expressing a
checkable relationship, 223 (44.2%) pure carries · 195 of 294 (66.3%) cross-sheet · **54** data validations
(35 main + 19 `x14`), 22 list-type, 20 resolving to a real enumerable vocabulary · 15 vocabularies on the
hidden `Dropdown` sheet · 252 merged ranges · 12 defined names of which **4 point at `#REF!` in the
regulator's own published blank** · 9 of 10 sheets protected, **`Dropdown` alone unprotected *and*
hidden** · **field surface (unlocked ∧ non-formula) = 3,747 cells**, per sheet Portfolio 1,698 ·
Investors 897 · PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 ·
AML-CFT 22 · build time 28–44 ms cold. A separate pass counting *all* unlocked cells in used ranges returns
3,755; both are right under their own definitions and **3,747 is the denominator**.

**Kills it.** Scope truncation (iterating visible sheets drops `Dropdown`, the vocabulary set is empty, and
`all(v in vocab …)` passes vacuously). Vacuity by empty set. Coordinate-anchored keys silently rebinding on
a row insertion. **Vocabulary read from the wrong document** — `Dropdown` is the only unprotected sheet, so
a predicate resolving the vocabulary from the *filed* workbook validates the filer's data against a list
the filer can edit. Broken references shipped in the authoritative artifact. Scheduled obsolescence:
`Dropdown!$E$3:$E$6` runs out at `2028-29`, so the workbook cannot express FY2029-30.

**Self-check.** Three-way agreement on the induced schema; disagreeing fields become
`NOT_RUN(extractor_disagreement)` by construction. **The denominator is computed twice by independent code
paths**, because when numerator and denominator come from the same wrong parser the ratio stays plausible
and the error is invisible by construction. A named invariant guards the flattering direction: *the
denominator derives from the unlocked mask, never from the predicate set* — that mistake was made twice in
one afternoon by the person who knew about it, once by sampling mutation sites only from cells the
predicates already read and once by computing 99.2% settled from a denominator built out of the numerator.
Parse round-trip must reproduce all 505 formula cells, all 54 validations, all 252 merged ranges, the
hidden sheet and its 15 vocabularies.

**Constants tests — G8, DECIDED, split in two**, because a regression test that fails on correct behaviour
gets deleted: `test_schema_constants` asserts **505 / 294 / 211 / 54 / 22 / 20 / 252 / 3747**, properties
of the published file that must never move; `test_harvest_count` asserts **280 / 515**, properties of our
code that are **allowed to move with a recorded reason** — they will move the first time G3 rejects a
harvested predicate.

**Components.** Schema authority: **raw OOXML via `lxml`**, beating **openpyxl** (above) and **pandas
`read_excel`**, which collapses merged headers and returns cached values, i.e. exactly the numbers under
test. Key identity: **label-anchored `(sheet, merged_header_path, row_label)` with coordinates as a
resolved attribute**, beating **coordinate-anchored keys** because a version bump becomes a re-resolution
instead of a rewrite; measured support — under a naive `(sheet, label-above, label-left)` key **1,749 of
1,953 cells are ambiguous (89.6%)** because 100-row tables repeat the label pair, and the row ordinal
disambiguates completely and is arithmetic, not a prediction.

### 1.4 L1b — CLAUSE GRAPH

Clause identity is **Akoma Ntoso / OASIS LegalDocML** — `eId` per clause, FRBR URI per instrument, promoted
deterministically from `DoclingDocument` — beating **inventing a clause-key scheme**, because without
`eId` a predicate's "the clause it implements" is an unresolvable free-text string and L5 cannot cite; and
the amendment graph is machine-followable, **76 of 82 amending circulars citing a resolvable target
(92.7%, MEASURED)**, with the remaining 6 declared. **10 of 399 circulars are scanned images** — a
permanent declared coverage gap carried on every predicate whose correctness rests on a negative search
result, until they are OCR'd once, offline, and frozen. **FRBR URI handling — DECIDED: implement the
grammar ourselves, ~100 lines.** *Alternative it beat:* depending on `laws-africa/cobalt` — GitHub reports
**NOASSERTION** for `indigo` and `cobalt` and **no lane opened their LICENSE files**; adopt `cobalt` only
if someone opens its LICENSE and it is permissive. The sibling `bluebell` is **GPL-3.0 (verified)** and
must never be linked.

### 1.5 L2a / L2b — EXTRACTION, and why the split is the correction

**L2a needs no model.** For a native `.xlsx`, key-binding is a lookup against L1: **0 of 3,755 unlocked
cells are ambiguous under the address key**, and 154 (4.10%) under a header-anchored key that generalises
across row counts (MEASURED). Running a model to predict what L1 already computes, then conformalising it,
then abstaining, would be an elaborate way to reintroduce uncertainty the artifact does not contain.

**L2b applies to exactly four populations and only these:** P1 cross-document binding (a value in an
attached PDF that must bind to a template key — the real target); P2 template-version drift (23.1% of
circulars amend an earlier instrument, so drift is the normal case); P3 filer deviation (share
**UNMEASURED** — needs real filings); P4 free text, where there may be no key at all.

**Kills it.** *Shape is not truth* — constrained decoding guarantees the key is **a** valid key, never that
it is **the right** key. *The confidently-wrong regime* — structured extraction into a fixed template is
precisely the low-entropy regime where entropy-based abstention was measured to fail. *Void guarantees* —
split conformal requires exchangeability, and a team-authored calibration set against real filings is a
known distribution shift, so the coverage guarantee is **void, not degraded**; quoting a distribution-free
finite-sample guarantee under a known-violated assumption is a stronger error than a loose FFR, because it
borrows a theorem. *The wrong exchangeable unit* — **the exchangeable unit is the FILING; report `n = F`,
never `n = 3,755·F`.** *The forced-abstention floor* — where base error μ exceeds target risk α, any
distribution-free method must abstain on at least `(μ − α)/(1 − α)` of items. *Silent retry* manufactures
exactly the clean verdict this product refuses to give.

**Self-check.** The key is an enum over exactly L1's induced key set, so an off-schema key is outside the
reachable token space at generation time **and** is deterministically rejected afterwards — both kept,
because the post-hoc guard is the one you can prove to a reviewer. **Gate before the layer is built at
all:** measure key-binding accuracy μ on P1; **μ > 0.30 ⇒ do not build the conformal layer**, because at
α = 0.05 the forced-abstention floor already exceeds 26.3% and the honest product is *"cross-document
binding is unchecked"*. `MODEL_EXTRACT` may never be the sole `method` on a `PASS` — a schema constraint,
not a coding convention. Retry is banned; if ever enabled, a Fact produced on attempt *k > 1* carries that
in its provenance.

**Structured output — DECIDED: provider-native structured output with `key` typed as `Literal[*L1_KEYS]`,
plus the post-hoc deterministic key check.** *Alternative it beat:* `outlines` / `XGrammar` (both
Apache-2.0), which mask logits and are strictly better **but require a local model, and no local model is
in this stack**; they become primary the day an open-weight model enters the L2b path. **Whether
provider-native constraint is guaranteed or best-effort is UNVERIFIED — which is exactly why the post-hoc
guard is not optional.** Abstention library: **crepes (BSD-3) / MAPIE (BSD-3)**, beating **TorchCP
(LGPL-3.0)** on licence and **entropy thresholding** on measurement.

### 1.6 L3 — CANDIDATE PREDICATE PROPOSAL (build time only)

**Renamed from "synthesis" deliberately.** Every measured system in this literature that works, works
because a rejector exists; every one that fails, failed because the rejector was absent or fake. **L4 is
the rejector, and L4 is the product. L3 proposes.**

**Kills it, each measured.** The degenerate operating point is documented inside the paper we reuse:
selecting **all** generated candidates yields **100% coverage and 100% FFR** (VERIFIED-AT-SOURCE).
**44.4%** of raw candidates individually blow a 25% FFR budget, and in two of nine pipelines sets whose
every member individually met the constraint reached composite FFR of **88%** and **53%** — FFR is monotone
non-decreasing under union, so **a registry that admits checks one at a time, each individually
acceptable, drifts silently to a flag-everything product.** The modal output is the weakest output (Type
Check at 47.4% prevalence and 0.14 bug-completeness against Arithmetic Equality at 0.82 — a 6× gap). The
correctness prompt is not the completeness prompt (p = 0.008, Cohen's d = 1.73), so **two prompt regimes
run and L4 arbitrates**. And **Silent Scope Omission** is the failure the empirical gates cannot see:
frontier models ground the right clause spans (SpanFaith **0.77–0.79**) and wire the exception structure
wrong (Edge-F1 **0.215–0.246** over 2,290 provisions), while our instrument is full of defeaters — which is
why G0 exists.

**The criterion source, restored to its full and true claim.** SPADE infers what correctness meant from the
traces of a developer changing their mind. We do not have to infer it: **the criterion is a published
instrument with a version, an amendment chain that is machine-followable in 76 of 82 cases, and a blank
template with a content hash. The criterion source is not more *authoritative* than SPADE's — the
regulator's own template computes a scheme total that misses two of its own nine legal values — it is
*citable, versionable and watchable*, which is what lets a predicate be tied to a clause, re-qualified when
the clause moves, and quarantined the day a circular changes the rule.** That is exactly what the
instrument-stream watcher implements, and it is a novelty no earlier version of this document stated.

**Self-check.** A **verbatim-quote provenance guard** — `source_text.find(quote)` must succeed or the
candidate is rejected at the boundary, at zero extra model cost. **`schema_keys` machine-checked against
the CEL AST both ways**, possible only because the language has no variables and no loops, and the reason
the settled fraction is a *derived* quantity rather than an estimate. **Three mandatory free baselines, run
before the model:** B0 the template's own 138 checkable relations; B1 **Daikon** over the clean corpus at
`--conf_limit 0.99`, whose trivia output doubles as the degeneracy list; B2 the degenerate arm — "no cell
is blank and no cell errors" — the analogue of the `NoException` baseline that found **68.9%** of a
published neural oracle's bugs at **twice** its precision. **If L3 does not beat B0 ∪ B1 ∪ B2 on marginal
kill at equal FFR, it has produced nothing**, however many predicates survive.

**Components.** Selection: **reimplement SPADE's ILP** (~40 lines of PuLP/CBC; measured runtimes
0.104–1.197 s on thousands of variables), beating **depending on the SPADE repository** — 17★, 1 fork,
**no licence field**, last push 2024-04-07: reuse the algorithm, not the repository. Prompt construction:
feeding L1's induced schema in as an explicit I/O constraint is the dominant lever on **structural
similarity (+37–54 percentage points)** in the only published study of statute→executable-model generation
(arXiv:2604.17153, VERIFIED-AT-SOURCE); **that study's *outcome* equivalence tops out at 51–53%**, and its
own caveat is that structural similarity does not guarantee outcome equivalence, or vice versa. Framing:
**the output is a number — `k` of `n` model-proposed checks survived a gate specified before the model
ran**, beating *"L3 works"*, which is unfalsifiable. **`k = 0` is a publishable result.**

### 1.7 L4 — QUALIFICATION

Specified in full in §II.4.3, because the gates are a property of the predicate model rather than of the
pipeline. Two things belong here. **The ceiling, stated permanently:** `KR = 0.82` licenses exactly one
sentence — *"rejects 82% of the 340 defects I seeded, under fault model v3"* — and does **not** license
*"detects 82% of real filing errors"*. In code mutation testing the bridge is the coupling effect; there is
**no coupling study for financial filing data**, so the bridge does not exist and must not be walked
across. **And the honest statement of what the gate has demonstrated:** *the gate has one demonstrated
rejection — five of ALR's six bound predicates assert only `≥ −1e17` over 1,428 cells and are refused.
Whether it rejects anything on the FME workbook is unmeasured: 19 of 24 FME bounds are a real `≥ 0`.*

### 1.8 L5 — EXECUTION AND VERDICT

Specified in full in §II.3. The failure modes, enumerated as code because that is how they will arrive:

```python
# 1. VACUOUS PASS — the classic, and the most likely to ship
def check_all_percentages_sum_to_100(cells):
    return all(abs(sum(g) - 100) < 1e-9 for g in group(cells))
# group() returns [] because the selector missed a renamed sheet. all([]) is True.
# Returns PASS. Nothing checked. Nothing logged.

# 2. EMPTY-SET ARITHMETIC     sum([]) == 0 ;  len(rows) == declared  passes as 0 == 0
# 3. SELECTOR DRIFT — a regex over OOXML that cannot see <x14:dataValidation>. Reports 3.
#    Truth is 22. Confident, well-formed, wrong.
# 4. SCOPE TRUNCATION — 'Dropdown' is state="hidden"; its fields never enter the DENOMINATOR.
# 5. SHARED-DENOMINATOR ERROR — numerator and denominator from the same wrong parser. Ratio 1.0.
# 6. SWALLOWED EXCEPTION      except: result = UNCHECKED   # a crash that looks like a limit
```

`cells_bound == 0 ⇒ ERROR` kills modes 1–4 at once; the twice-computed denominator kills mode 5; the
eight-state vocabulary kills mode 6.

**Components.** Verdict model: **build it — nothing in the ecosystem has a third value.** *Alternative it
beat:* **Great Expectations**, disqualifying and in the exact direction that kills us — with
`catch_exceptions=True`, an expectation that *could not be evaluated* returns `success = False`, **the same
value it returns when it evaluated and the data was wrong**, and its documented result fields contain no
field for "not applicable", "out of scope" or "no oracle exists". **Soda Core** is disqualified on licence
— Elastic License 2.0 forbids providing the software to third parties as a hosted service, which is what we
are. **pandera** (MIT) is adopted **only** as a host-function implementation for bulk column checks, never
as the predicate language. The corrected guidance line: *do not rebuild the check **library**; you **must**
build the **verdict model**, because none of them has one.*

### 1.9 L6 — DIFFERENTIAL AND INVARIANT PROBES

**SUT — DECIDED: the workbook-as-program.** *Alternative it beat:* the filer's valuation engine, which
would require the FME to run our transformations through their own system — a different and more
interesting product, but not this one. The workbook is genuinely re-executable: **all 505 formula cells
carry cached computed values**, so a baseline exists. The relation set is **25, none requiring ground
truth**: 15 need the filing alone, 4 the filing plus the pinned blank, 3 two consecutive filings, 1
multiple instances, and 2 are checker self-tests never reported to the filer.

The relation that pays for the layer is the **formula-override differential**: for every cell the blank
template declares to be a formula, compare the filed value against the value obtained by evaluating the
template's formula over the filed inputs. **This is the only thing in the design that detects a filer
overwriting a formula cell with a literal** — a defect that leaves the filing perfectly self-consistent,
because the inconsistency was deleted along with the formula. Its oracle is the published blank, so it
needs no corpus. **It is predicate #1**, and its `method` value is `TEMPLATE_DIFF` — which is why dropping
`TEMPLATE_DIFF` from the schema would make the design's own flagship undescribable. Sheet protection does
not help: nine sheets carry SHA-512 `sheetProtection` hashes and stripping them is a zip edit, so **assume
the filed artifact is fully mutable and build no predicate whose validity depends on a range being
protected.**

**Kills it.** Relations are not self-validating — a violated relation means *the artifact is wrong* **or**
*our relation is wrong*, so every relation passes L4 like any other predicate. Null tests inflate the
settled fraction and are rejected automatically by G3. **Degenerate satisfaction** — an all-zero filing
satisfies every partition identity trivially, so every partition relation carries a **non-degeneracy
precondition** and returns `OUT_OF_SCOPE`, never `PASS`; without it an empty filing scores 100% through the
L6 door. **Cross-basis contamination** — Portfolio note 7 puts Tables 3.1/3.2 on a direct-investment basis
while the PMS note puts Table 5.6 on a look-through basis, so any relation adding a 3.x quantity to a 5.6
quantity is invalid by the artifact's own notes.

**Tolerance.** `τ(n) = 5n` units of `MILLI_USD_MILLION` (= `n × 0.005` USD Million), from guidance C111.
Integer arithmetic throughout; **counts get zero tolerance — a person is not a rounded quantity, and slack
there is how a missing investor hides.** A fixed epsilon is the single most likely source of spurious
failures.

**Components.** Execution vehicle: **Hypothesis** — reported **MPL-2.0, LICENSE not opened (SECONDARY)** —
with `@invariant` for necessary relations and in-rule assertions for expected ones, so the FAIL/ADVISORY
split is implemented by the library rather than by convention, plus shrinking and `@example` regression
pinning; it beat a bespoke loop, which loses both. Search budget **`max_examples = 50`**, beating
Hypothesis's default 100 and fuzzer scale because **55% of mutations are found with a single input and 76%
within the first 20**, and this input space is small and fixed. Relation authorship: **human, read off the
artifact's own formula graph and guidance notes, no model** — measured, model-generated metamorphic
relations score "markedly low" on novelty and recapitulate the textbook classes, which is exactly how an
earlier version of this design arrived at five relations of which four false-alarm on a *correct* filing
and the fifth is vacuous. Formula evaluator: **reimplement the eight-function vocabulary** (`SUM`,
`COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)`) over a topological sort of 505
cells, beating **`formulas` (EUPL 1.1+)** and **`pycel` (GPL-3.0)** on licence for a hosted product and on
method — importing someone else's evaluator imports an unmeasured error rate our own admission rules would
have to reject — **and the reimplementation *is* the differential arm.**

### 1.10 L6.5 and L7

Specified in §II.6 and §II.5 respectively.

---

## II.2 — THE CORRECTED DATA FLOW

```
 BUILD TIME — offline, batched, human-reviewed, amortised over every future filing
 ─────────────────────────────────────────────────────────────────────────────────────────────────
  regulation PDF ──┐
  399 circulars ───┼──►  L1b CLAUSE GRAPH            [deterministic · SPECIFIED, nothing built]
                   │      Docling → Akoma Ntoso · eId per clause · FRBR URI per instrument
                   │      76/82 amending circulars resolve · 10/399 scanned → declared gap
                   ▼
   ╔══════════════════════════════╗            ╔═══════════════════════════════════════════════╗
   ║  L3  CANDIDATE PROPOSAL      ║    CEL     ║  L4  QUALIFICATION — FIVE GATES, THIS ORDER   ║
   ║  ★ THE ONLY MODEL IN THE     ║  envelopes ║   G0  scope faithfulness            free      ║
   ║    ENTIRE SYSTEM ★           ║ ─────────► ║   G1  executes and binds            free      ║
   ║  ~600 calls per template     ║            ║   G3ᵖ non-degeneracy · proof arm    cheap     ║
   ║  version  (DERIVED: ~30      ║            ║   G2  seeded-defect kill            expensive ║
   ║  obligations × 10 candidates ║            ║   G3ᵉ non-degeneracy · control arm            ║
   ║  × 2 prompt regimes)         ║            ║   G4  false-failure rate + provenance         ║
   ╚══════════════════════════════╝            ║   emits kill_case + pass_case (liveness)      ║
             ▲                                 ║   ADMIT ⇒ append-only REGISTRY (Merkle root)  ║
   hand-authored predicates ────────────────► ║   REJECT ⇒ rejection row → counterEvidence[]  ║
   L6 relations ────────────────────────────► ╚═══════════════════════════════════════════════╝
                                                              │ registry_root
 ══════════════════════ THE DETERMINISTIC BOUNDARY ═══════════╪═══════════════════════════════════
  Every model output crosses this line as DATA that a program has already adjudicated.
  Nothing below opens a socket to a model endpoint.  (Specified; the CI gate is not yet written.)
                                                              │
 RUN TIME — per filing                                        │
 ─────────────────────────────────────────────────────────────┼───────────────────────────────────
  blank template ─┐                                           │
  filing .xlsx ───┼─► L0 INGEST  sha256 ORIGINAL BYTES ← what L7 signs
  register JSON ──┘   container guard · DUAL PARSER · agreement vector
        ▲             disagree on {sheets, names, hidden} ⇒ INVALID; else NOT_RUN(those fields)
        │                                  │
  [+] INSTRUMENT WATCHER                   ▼
  daily hash of circular +   ┌──────────────────────────────────────────┐
  Authority-meeting pages;   │ L1 SCHEMA INDUCTION  (from the BLANK)     │
  a new instrument citing a  │  all sheets incl. hidden · extLst/x14     ├── TemplateSchema (pinned)
  regulation a predicate     │  shared formulas materialised · degree map│        │
  claims ⇒ PROVISIONAL,      │  MILLI_USD_MILLION · label-anchored keys  │        │
  automatic and pessimistic  │  UNLOCKED-CELL MASK = THE DENOMINATOR     │        │
        └──────────────────  │  + EXTRACTION MANIFEST                    │        │
                             └──────────────────┬───────────────────────┘        │
                    ┌───────────────────────────┴──────────────┐                 │
                    ▼                                          ▼                 │
        L2a STRUCTURAL EXTRACTION           L2b DOCUMENT EXTRACTION               │
        deterministic · NO MODEL            ✦ MODEL · CONTINGENCY ONLY ✦          │
        lookup against L1                   unstructured attachments only;        │
        0 of 3,755 cells ambiguous          SKIPPED ENTIRELY when there are       │
        under the address key               none — the normal case, $0.00         │
                    │                                          │                 │
                    └──────────────────┬───────────────────────┘                 │
                                       ▼  Facts{key,value,unit,anchor,warrant}    │
        ┌────────────────────────────────────────────────────────────────┐        │
        │ L5  PRE-FLIGHT + EVALUATION + VERDICT       (deterministic)     │◄───────┘
        │  CEL over exactly two bound names: `filing`, `template`.        │  admitted predicates only
        │  No clock, no network, no filesystem. Terminating by design.    │
        │  8 states × 30 namespaced reasons × severity {BLOCKING|ADVISORY}│
        │  cells_bound per predicate; 0 ⇒ ERROR ⇒ run INVALID             │
        │  denominator computed TWICE by independent code paths           │
        └───────────────────────────┬────────────────────────────────────┘
        ┌───────────────────────────┴──── L6 IS A LOOP OVER L0–L5 ─────────────────┐
        │  transform the input → re-run → compare. 25 relations, all L4-qualified. │
        │  ★ TEMPLATE_DIFF: template says formula, filing carries a literal ★      │
        └───────────────────────────┬─────────────────────────────────────────────┘
                                    ▼
        ┌────────────────────────────────────────────────────────────────┐
        │ L6.5 SELF-CHECK AND RESIDUE                                     │
        │  replay each predicate's stored kill_case against THIS filing.  │
        │  any survivor ⇒ run state INVALID, and no settled fraction is   │
        │  emitted at all.  RESIDUE := WRONG mutants nothing rejects.     │
        └───────────────────────────┬────────────────────────────────────┘
                                    ▼
        ┌────────────────────────────────────────────────────────────────┐
        │ L7 ATTESTATION  DSSE + in-toto Statement v1                     │
        │  subject[] = filing ⊕ template.  ★ NO `result`. NO `status`. ★   │
        │  top level is `scope`.  → self-contained HTML → lossy OSCAL      │
        └────────────────────────────────────────────────────────────────┘
```

**How many model calls an honest implementation needs.** Not two. **Zero on the verdict path per filing**
(specified, gate unwritten). **~600 per template version at build time**, DERIVED from the pre-registered
design — ≈30 obligations drawn, 10 candidates per obligation per prompt regime, two regimes — plus the L3
baselines, which use no model at all. **O(1) per unstructured attachment on the L2b path**, which is
skipped entirely when a filing has no attachment, which is the normal case; if the conformal layer passes
its μ ≤ 0.30 gate it adds O(calibration set) calls, once, offline. A property you can assert in CI beats a
property you assert in prose, which is why the claim is *zero on the verdict path* and not a count.

---

## II.3 — THE VERDICT MODEL

This is the product's core object. Everything below is normative and replaces every earlier version.

### 3.1 The denominator's unit — G1, DECIDED

**DECIDED: the unit of the denominator is the CELL.** The report's primary key is `cell_id = stable_key`.
The obligation becomes an **attribute of the predicate**, never a factor of the denominator.

*Alternative it beat:* the `(field × obligation)` pair. It lost because **no derivation of it exists
anywhere in the corpus.** Three incompatible pair counts were in circulation, two of them lifted from an
*illustrative* JSON block that never claimed to be a measurement, and none reconcilable with the one
quantity that was actually measured. `obligationsTotal` and `pairsTotal` are therefore **deleted from the
schema** and must not appear in an example until a published enumeration rule exists. The measured
denominator is the **3,747-cell field surface**; 2,373 cells are settled by 280 harvested predicates and
1,374 are declared unchecked.

**Consequences, all of which are now normative:**

1. `run_item.pair_id` becomes `run_item.cell_id`; `scope.denominator.pairsTotal` becomes
   `scope.denominator.cellsTotal`, whose value **is** `fieldSurface`.
2. **Obligation binding — G6, DECIDED.** `obligation_id` comes from a **hand-maintained `obligations.yaml`**
   (`OBL-nnn` → `{frbr_uri, eId, verbatim_quote, char_span}`), because **L1b is entirely unbuilt** and a
   day-one answer that depends on an unbuilt layer is not an answer. When L1b ships, `obligations.yaml`
   becomes generated and the ids are preserved. Obligation is a grouping *view* over items; it is never a
   denominator.
3. **Many predicates may bind one cell.** A cell's item state is the maximum of its evaluations under the
   precedence order
   `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`.
   A cell is clean only if **every** predicate binding it passed. `NO_PREDICATE` is not in the order: it is
   the state of a cell with an empty evaluation set. Every item carries `evaluations[]` — the full
   per-predicate vector — so nothing is lost by taking a maximum.

### 3.2 The eight closed item states

| State | The rule that produces it | Settled denominator? | Precedent |
|---|---|:--:|---|
| `PASS` | `applicable` true, pre-flight clean, `expr` evaluated to true, `cells_bound > 0` | ✅ settled | XCCDF `pass` |
| `FAIL` | as above, `expr` evaluated to false; `witness` is evaluated for the cell list | ✅ settled | XCCDF `fail` |
| `INDETERMINATE` | the predicate ran to completion and the result is not decidable (abstention, tolerance straddle, source conflict, engine disagreement) | ✅ kept | XCCDF `unknown` |
| `NOT_RUN` | the predicate is admitted and in scope but did not execute (input unavailable, unreadable source, budget, deactivation, extractor disagreement) | ✅ kept | XCCDF `error`; C2PA `inaccessible` / `skipped` |
| `NO_PREDICATE` | the cell is in scope and **no admitted, qualified predicate binds it** | ✅ **kept — the deliberate divergence** | XCCDF `notchecked` |
| `ERROR` | the apparatus failed here: a predicate raised, `cells_bound == 0`, a canary was silent, closure was violated, the readers disagreed structurally | ✅ kept, **and the run becomes `INVALID`** | — |
| `OUT_OF_SCOPE` | `applicable` evaluated false, or the run profile excluded it, or the operator withheld it | ❌ removed | XCCDF `notapplicable` / `notselected` |
| `INFORMATIONAL` | the predicate ran and its output is a value for the reader, not a verdict (including a lawfully-failing *expected* relation) | ❌ removed | XCCDF `informational` |

**The divergence, and it is the single most important scoring decision in the design.** XCCDF removes
`notchecked` from its denominator because its denominator is a benchmark a human authored, so "no check
exists" means the author chose not to have one. **Ours is induced from the regulator's own published
template, which is authoritative and complete — so "no predicate exists" is a gap in *us*, not in the
specification.** Removing it would let the settled fraction rise by doing nothing. It ships with this
justification attached.

**Severity and override are orthogonal axes, not extra states.** `severity ∈ {BLOCKING, ADVISORY}` is set
by the measured FFR (§3.6). `override = {oldState, newState, remark, actor, time}` retains both states
inside the signed payload; an overridden item counts under its **new** state and the override count is
reported separately — a downstream reviewer will want it.

**Run states:** `VALID` (the pipeline ran, the checker demonstrated liveness on this artifact, closure
holds) · `INVALID` (the system could not demonstrate it was working here) · `REJECTED` (the submission
never became a run: size or media-type refusal, no run row created). **An `INVALID` run renders a report
that states why and carries no settled fraction at all, and its aggregate verdict is `null`, not
`SETTLEMENT_INSUFFICIENT` — the latter is a finding about the filing and this is a finding about us.**

### 3.3 The closure invariant — seven terms

```
outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == cellsTotal
                                   ( settled == pass + fail )
```

Checked at report-generation time. **A cell that lands in no bucket aborts the report.** This is the
terminal `DISALLOW *`: the in-toto specification names the hazard in its own text — an implicit open world
*"could allow artifacts to sneak into the step or inspection undetected."* The seven-term form is the only
one under which each of the eight states lands in exactly one bucket; the five-term version that was in
circulation had no bucket for `INFORMATIONAL` or `ERROR`, so under it every informational item aborted the
report. `inScope = cellsTotal − outOfScope − informational` is the settled fraction's denominator.

### 3.4 The evaluation contract — five rules

**G5, DECIDED: this subsection is the evaluation contract.** `EVALUATION-CONTRACT.md` is *generated* from
it by a build step, and a CI test asserts that the evaluator's transition table equals this table. It
appears in exactly one place because three different versions of it were live at once.

```
1.  Evaluate P.applicable
      error  -> NOT_RUN(not_run.source_unreadable)            [never FAIL]
      false  -> OUT_OF_SCOPE(P.reason_if_inapplicable ∈ out_of_scope.*)   [never PASS]
      true   -> continue

2.  PRE-FLIGHT. For every key k in P.schema_keys, test presence and type against the fact model
    BEFORE evaluating P.expr. Any k absent or mistyped -> NOT_RUN(not_run.source_unreadable: <k>).
      Why this is structural and not optional: the CEL specification states that for || and &&,
      if an operand's evaluation "produces a runtime error, it will be ignored." So
      `true || <error>` evaluates to TRUE, and an unguarded predicate can return PASS while
      silently swallowing an operand that could not be evaluated at all — the exact defect this
      product exists to prevent, manufactured by the language. Because schema_keys is
      machine-checked against the AST, the pre-flight set is EXACT, not an estimate.

3.  Evaluate P.expr under a step-count budget and a wall-clock kill
      budget exceeded -> NOT_RUN(not_run.budget_exhausted)     [never FAIL]
      runtime error   -> ERROR(error.predicate_raised), run_state = INVALID
      false           -> FAIL, then evaluate P.witness for the cell list
      true            -> PASS

4.  Warrant composes by WEAKEST INPUT: warrant = min over every fact the AST read, under
    DETERMINISTIC > MODEL_EXTRACTED > DERIVED; retrieved_at = max over inputs. A verdict is never
    fresher than its stalest input and never stronger than its weakest.

5.  Every predicate reports cells_bound. cells_bound == 0 -> ERROR(error.cells_bound_zero),
    run_state = INVALID. Binding to nothing is never a PASS.
```

The five rulings the drafts disagreed about, each stated once and finally:

| Situation | State | Reason code | Run state | Why not the alternative |
|---|---|---|---|---|
| `applicable` evaluates **false** | `OUT_OF_SCOPE` | `out_of_scope.*` | unchanged | The word `UNCHECKED` was retired when the state axis was opened up; an evaluation contract written in a retired vocabulary is not a contract |
| `expr` **raises** | `ERROR` | `error.predicate_raised` | **`INVALID`** | A predicate that raised is an **apparatus failure**, not an unreadable source. `not_run.source_unreadable` is reserved for inputs that could not be read, and the two have opposite remedies — fix the code versus retry |
| **budget exceeded** | `NOT_RUN` | `not_run.budget_exhausted` | unchanged | Never FAIL. A check that ran out of time has told us nothing about the filing |
| **`cells_bound == 0`** | `ERROR` | `error.cells_bound_zero` | **`INVALID`** | This is the vacuous-pass failure mode the whole design exists to catch. Demoting it to `NOT_RUN` puts it in the same bucket as a rate-limited register |
| a proviso is **declared but unimplemented** | `NO_PREDICATE` record | `no_predicate.not_yet_synthesised` | unchanged | It is not an ambiguous rule — the rule is clear and we have not implemented it. The record carries the proviso's **verbatim text and character span**, and the predicate's scope record carries `provisos_declared` |

**How a declared proviso interacts with the cell denominator — DECIDED.** Closure holds over cells, and a
proviso is not a cell. So: a predicate with `provisos_declared > 0` (a) is admitted at **`ADVISORY` at
most**, (b) stamps every item it settles with `scopeIncomplete: [{eId, char_span, quote}]`, and (c) causes
the report to emit one `NO_PREDICATE(no_predicate.not_yet_synthesised)` record per declared proviso into
`scopeCaveats[]`, counted and rendered in the unchecked panel. *Alternative it beat:* charging the proviso
against specific cells in the denominator — rejected because the cells a proviso governs are exactly the
ones we cannot identify (that is what "unimplemented" means), so any cell-level attribution would be
invented. A predicate that neither implements **nor** declares a proviso is rejected at G0; that is the
real gate.

### 3.5 The thirty reason codes

Closed, namespaced, five families. **Admission test, written into the spec: two reasons are distinct if and
only if they imply different remedies. If the operator's next action is the same, the codes merge.** That
test is why the vocabulary is 30 and also why it is not 60. A reason code is **required whenever the state
is not `PASS` or `FAIL`**, and forbidden when it is.

**`no_predicate.*` — 8. We have no qualified check. The honest core, and the backlog.**

| Code | Meaning | Remedy |
|---|---|---|
| `.undecidable_by_construction` | "correct" is not defined for this obligation — valuation appropriateness; whether a scheme is properly classified | **None. The permanent floor; report it forever** |
| `.requires_judgment` | a competent human can decide; no program can | Route to a human; never auto-close |
| `.not_yet_synthesised` | decidable in principle; nobody has written it. **Also the emission for a declared-but-unimplemented proviso** | The growable set — this is the settled-fraction-over-time story |
| `.failed_qualification` | a predicate **was** written and a gate rejected it; carries the rejecting gate and the measured number | Improve the predicate, or accept the gap knowingly |
| `.rule_ambiguous` | the obligation text does not determine a testable condition — reg 51(1)'s open delegation | Ask the regulator |
| `.no_obligation_specified` | **the instrument is clear and simply says nothing.** Two of nine legal Type-of-Scheme values have no NAV-frequency rule at all | Distinct from `.rule_ambiguous` (a rule exists and is unclear) and from `.not_yet_synthesised` (our gap). **Conflating "the regulator did not legislate this" with "we haven't got round to it" would be the most misleading thing this report could do** |
| `.rule_withdrawn` | previously admitted; its FFR later exceeded threshold, or its clause was amended | Re-qualify or retire |
| `.not_yet_requalified` | `PROVISIONAL`: an element of `qualified_against` changed. **It still runs, so detection is not lost, but it does not count in the settled numerator** | Human clears it |

**`not_run.*` — 10. We have a check; it did not run. Every one is an ops or data problem.**

`.input_unavailable.counterparty` (needs data held by a party who is not the filer) ·
`.input_unavailable.register` (live register unreachable, rate-limited or ambiguous at run time) ·
`.input_unavailable.prior_period` (needs a filing we do not hold) ·
`.source_unreadable` (the artifact or a region of it could not be parsed) ·
`.template_unbound` (L1 could not bind the filing to a published template hash — **this escalates: the
whole run is suspect**) ·
`.deactivated` (an admitted predicate deliberately switched off for this run, with a pointer to the
decision record — skipping is sometimes legitimate, and the moment it is legitimate the report must be able
to say so, or the skip becomes silent) ·
`.budget_exhausted` ·
`.external_source_lacks_field` — **the external source structurally does not carry the field. Our own
near-miss is the canonical illustration and not an instance: the register's *list* endpoint returns
`RegistrationNumber = null` on 650 of 650 rows while its *detail* endpoint returns it on 228 of 228.** ·
`.external_source_unavailable` (the source was down at filing time) ·
`.extractor_disagreement` (the readers disagreed on this field — added because a schema extractor that
silently returns 35 of 54 validations is the failure this product exists to prevent, occurring inside the
product).

**`indeterminate.*` — 4.** `.extraction_abstained` (the L2b conformal set was not a singleton — the
designed abstention) · `.tolerance_straddle` (the result sits inside the rounding band where both answers
are admissible; the rounding trade-off now has a name instead of being absorbed into a threshold) ·
`.conflicting_sources` (two admitted sources disagree and no tie-break rule is published) ·
`.engine_disagreement` (the two recalculation engines disagree on this cell — never `PASS`, never `FAIL`).

**`out_of_scope.*` — 3. Removed from the denominator, therefore the most abusable; each requires a
machine-checkable justification.** `.not_applicable` (a pointer to the schema condition that makes it
inapplicable) · `.not_selected` (a pointer to the named run profile and its digest) · `.withheld` (an actor
plus a rationale; **counted and displayed separately, never folded into `.not_applicable`**).

**`error.*` — 5. The apparatus failed. Any one sets `run_state = INVALID`.**
`.predicate_raised` · `.cells_bound_zero` · `.canary_silent` · `.closure_violated` ·
`.parser_disagreement_structural`.

**Why the distinctions are load-bearing, in one citation.** SPDX names three distinct causes of
non-assertion — the creator *"cannot reach a reasonable objective determination"*, *"has made no attempt"*,
and *"has intentionally provided no information"* — and then deliberately collapses all three into one
token, `NOASSERTION`. That is a documented decision, not an oversight, and it is precisely the collapse
this product exists to refuse.

### 3.6 The four enums that were in dispute

```
method      = RECOMPUTE | TIE_OUT | SCHEMA_BIND | TEMPLATE_DIFF | REGISTER_LOOKUP
            | CLAUSE_TEST | DIFFERENTIAL | MODEL_EXTRACT | UNKNOWN          -- NINE values
warrant     = DETERMINISTIC | MODEL_EXTRACTED | DERIVED                     -- composes by weakest input
provenance  = COMPUTED | DECLARED                                           -- by us | by the filer
corpus_provenance = SELF-AUTHORED | BLIND-FILLED | TEMPLATE-COMPUTED
                  | REGISTER-DERIVED | REAL-PARTNER | PUBLIC                -- SIX values
```

`TEMPLATE_DIFF` is the method of the formula-override detector, which both the design's own text and its
demo call predicate #1; a schema without it cannot describe the design's flagship. `DIFFERENTIAL` replaces
`METAMORPHIC` because the technique's own definition requires a re-executable system under test.

**`warrant` is the runtime provenance lattice and nothing else.** The four-value column
`MEASURED | MODELED | ASSERTED | UNCHECKED` that appeared in one draft is **deleted**: it confused the
corpus's documentation-warrant labels with the runtime lattice, and no rule composes `MEASURED` with
`ASSERTED`. The lattice composes: a derived fact takes `warrant = min(inputs)` and
`retrieved_at = max(inputs)`. It is **exact and not an estimate**, because `schema_keys` is machine-checked
against the AST.

**`provenance` is `COMPUTED | DECLARED`.** `GATHERED` is C2PA's word for a different distinction
(created versus gathered assertions) and importing it here would blur ours.

**`corpus_provenance` has six values and the register value is spelled `REGISTER-DERIVED`.** The five-value
version could not express the one false-failure rate this project can measure today, and a third spelling
(`REAL-REGISTER`) existed in a third document. **`SELF-AUTHORED` renders as `—` and the word
*uninformative*. It is not a number and the schema forbids one**, because an FFR measured on a corpus its
authors also wrote has expected value zero regardless of predicate quality — printing *"0.0% false failures
across 340 clean filings"* is worse than printing nothing, because it has the shape of evidence.

**Severity thresholds — G2, DECIDED and pre-registered before the first run:**

```
FFR Wilson UPPER bound  ≤ 0.02   ⇒  BLOCKING
                 0.02 <  ≤ 0.10  ⇒  ADVISORY
                        >  0.10  ⇒  NOT ADMITTED  (this is gate G4)
```

The threshold applies to the **Wilson upper bound**, not the point estimate. *Alternative it beat:* the
point estimate — rejected because `0 fires / 4 filings` has a point estimate of 0.000 and an interval of
`[0.000, 0.490]`, and a rule keyed on the point estimate would let a sample of four buy `BLOCKING`.
**Consequence, stated so nobody is surprised on stage: on day one almost nothing is `BLOCKING`.** A
predicate needs roughly `n ≥ 185` clean, non-self-authored filings with zero fires to clear 0.02 on the
upper bound. Everything enters as `ADVISORY` with its interval printed beside it. That is the EBA's
warnings-first convention with the measurement put back in, and it is defensible to a downstream reviewer
on day one because they already run the unmeasured version.

### 3.7 Aggregation, and the state name that replaces the green tick

```
residueIsConfined := (unsettled cells touch ≤ K distinct sheets)
                 AND (no unsettled cell is flagged material-by-policy)
                 AND (unsettled / inScope ≤ T)
```

| | residue confined | residue pervasive |
|---|---|---|
| **failures present** (`settled.fail > 0`) | `EXCEPTIONS_NOTED` | `ADVERSE` |
| **no failures, unsettled residue** | **`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`** | `SETTLEMENT_INSUFFICIENT` |
| **self-check failed** | `INVALID` (verdict field is `null`) | `INVALID` |

**There is no state whose name means "clean."** The best available verdict is literally
`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`, which cannot be quoted out of context without carrying its
own qualifier. This delivers the no-green-tick commitment **by naming**, which is far more robust than by
iconography: an icon can be screenshotted; a name travels with the claim. The report's own title string is
a function of the verdict state. When `SETTLEMENT_INSUFFICIENT`, the wording flips from *"this filing was
checked against N predicates"* to *"this filing was **submitted for** checking against N predicates;
coverage was insufficient to report."*

Say what we are doing and what we are not: "material" and "pervasive" are matters of professional judgment
in the standard we borrow the shape from. **We cannot compute them.** We can declare a published, versioned
policy and apply it deterministically, which is strictly more inspectable than judgment. **Do not claim to
have implemented ISA 705. Claim a declared policy in its shape.**

**`K` and `T` — OPEN — USER DECISION.** Two different parameter sets shipped in two drafts (`K = 3, T = 0.35,
v2` and `K = 3, T = 0.45, v1.1`), and **neither has a basis anywhere in the corpus**. There will be exactly
one file, `pervasiveness-policy-v1.json`, versioned inside the attestation. Until an argument for the
numbers exists, both are rendered as the literal string `PLACEHOLDER` in every example and every screen.
**The exact question: what is the maximum number of distinct sheets `K` an unsettled residue may touch, and
the maximum unsettled/inScope ratio `T`, before a report with no failures must be downgraded from
`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` to `SETTLEMENT_INSUFFICIENT` — and on what argument?**

---

## II.4 — THE PREDICATE MODEL

### 4.1 What a predicate IS

**A predicate is not an expression. It is a small, signed, content-addressed record that *contains*
expressions.** The envelope is what makes non-settlement a first-class evaluation outcome rather than an
exception, and it is where all qualification metadata lives. Content address = `sha256` of the RFC 8785
canonical serialisation (stated explicitly, because *"the sha256 of the JSON"* is not a definition and two
implementations disagreeing on key order produce two registry roots).

```yaml
# predicate/P-0041.yaml
id:            P-0041
version:       3
kind:          harvested            # harvested | proposed | hand_authored | relation
template:      sha256:7d9a…         # the PINNED blank this predicate binds to
schema_keys:   ["intro.tbl15.row[*].scheme_type", "vocab.scheme_type"]
                                    # DECLARED, machine-checked BOTH WAYS against the CEL AST.
                                    # Reads an undeclared key -> REJECT. Declares an unread key -> REJECT.
host_fns:      []                   # closed, versioned set; unregistered -> REJECT
obligation_id: OBL-014              # attribute, NOT a denominator factor  (§II.3.1)
clause:
  instrument:  "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30"
  eId:         "reg_27__para_1"
  span:        [10422, 10597]       # exact character span — G0 requires it
  quote:       "Type of Scheme"     # VERBATIM. source.find(quote) must succeed or REJECT.
  provisos:
    - text:    "Provided that this requirement shall not apply in case of a fund of funds scheme…"
      disposal: DECLARED            # IMPLEMENTED | DECLARED
      emits:    NO_PREDICATE(no_predicate.not_yet_synthesised)
rationale:     "Every declared scheme type must be a term the published template offers."

applicable: >                       # CEL -> bool. false => OUT_OF_SCOPE(reason_if_inapplicable)
  size(filing.intro.tbl15.rows) > 0
expr: >                             # CEL -> bool. true => PASS, false => FAIL
  filing.intro.tbl15.rows.all(r,
    r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)
witness: >                          # CEL -> list. what to show on FAIL
  filing.intro.tbl15.rows.filter(r,
    r.scheme_type != "" && !(r.scheme_type in template.vocab.scheme_type)).map(r, r.__cell__)

reason_if_inapplicable: "out_of_scope.not_applicable: no schemes declared"
tolerance:      null                # arithmetic predicates: {"tau_units_per_summand": 5}  (MILLI_USD_MILLION)
severity_tier:  ADVISORY            # SET BY THE MEASURED FFR (§II.3.6), never by hand

external_deps:                      # declared, so a schema change at the source degrades LOUDLY
  - endpoint: "https://ifsca.gov.in/DirectoryList/DirectoryDetailGet"
    field:    "RegistrationNumber"
    snapshot: sha256:…              # content-addressed; the register is mutable and undated
    on_missing: NOT_RUN(not_run.input_unavailable.register)

qualification:                      # WRITTEN BY L4. NOT HAND-EDITABLE. ABSENT => DOES NOT LOAD.
  g0: {provisos_total: 1, provisos_implemented: 0, provisos_declared: 1}   # must sum or REJECT
  g1: {executes: true, keys_resolve: true, cells_bound: 10}
  g2: {generated: 61, unobservable: 17, observable: 44, unreachable: 3, killed: 41,
       kill_rate: 0.932, by_fault_class: {F2: 1.00, F5: 0.00, F12: 0.93},
       marginal_kill_over_baselines: 0.11, fault_model: "v3", harness: "1.2.0"}
  g3: {method: "z3+empirical", verdict: "non_degenerate", witness: "sha256:…",
       control_arm: {seeded_outside_read_set: 41, spurious_fires: 0}}
  g4: {fired: 2, n: 96, rate: 0.021, wilson: [0.006, 0.074],
       corpus_id: "blind-fill-v2", corpus_provenance: "BLIND-FILLED",
       clean_corpus_independent_of_predicate: true,
       heldout: {fired: 1, n: 22, wilson: [0.001, 0.216], slice: "close-ended restricted schemes"},
       marginal_ffr: 0.010, conditioned_on: ["P-0007"]}
  liveness: {kill_case: "mutants/P-0041-kill.xlsx", pass_case: "clean/blind_fill_017.xlsx"}
  qualified_against:
    template_sha256: "7d9a…"        # every element here is part of the predicate's IDENTITY
    template_label: "FME_02012026"
    regulation_version: "2026-01-30"
    circular_corpus_snapshot: "2026-08-10T00:00Z"
    circulars_unreadable: 10        # of 399 — a permanent declared gap this predicate inherits
    evaluator_version: "0.4.1"
    proposer: null                  # kind=proposed: {model_id, date, prompt_sha256}
state:          ACTIVE              # ACTIVE | PROVISIONAL | QUARANTINED | WITHDRAWN
withdrawn_reason: null              # {rule_amended, ffr_exceeded_threshold, superseded_by, source_schema_changed}
```

### 4.2 The language — DECIDED: CEL, admitted subset only, in the three-slot envelope

*Alternative it beat, and it is the execution-substrate lane's own recommendation:* **plain Python plus a
data-validation framework**, which wins on expressiveness and developer speed and loses on four
independently decisive grounds. (i) **The settled fraction stops being computable** — you cannot statically
determine which fields a Python function reads, so the product's headline becomes an *estimate*, and this
corpus is a monument to what happens when a coverage claim is inferred rather than derived. (ii) Executing
model-written Python **requires a sandbox**, and the sandbox layer is where the 2026 CVEs are. (iii) The
predicate stops being auditable — the library screen shows a function body, not a rule. (iv) Mutating
arbitrary Python has a high, unbounded equivalent-mutant rate, versus a ~20-production grammar with
enumerable operators. The language definition states verbatim that CEL programs are **"terminating: CEL
programs cannot loop forever"** and **"side-effect-free"**, and the precedent that settles whether this is
a real engineering choice is **Kubernetes ValidatingAdmissionPolicy, GA in v1.30** — model-free CEL policy
over structured data, evaluated in-process, no container per check.

Runners-up, each with its specific loss: **Rego/OPA** on readability and host language (reconsider only if
the stack moves to Go); **Starlark** decisively, because a Starlark predicate has local state, so *"which
fields does this predicate read?"* stops being a static question; **JSONLogic** on types, dates and regex
(its *shape* — a rule is a tree — was stolen for the envelope); **SpEL** outright on security; **Z3** as a
category error (it answers *"is this predicate ever falsifiable"*, not *"is this filing correct"*, and is
adopted for G3 instead); **Drools / ZEN / json-rules-engine** because a rule engine's core competence is
conflict resolution and chaining, and **our architecture forbids exactly that** — every predicate must be
independently scored and independently attributable, and chaining makes both incoherent.

**Runtime: `celpy` (`cloud-custodian/cel-python`, Apache-2.0), pinned by PyPI name and wheel hash** — two
different projects live at a path called `cel-python`, which is a real footgun — with `cel-expr-python`
(Apache-2.0, a wrapper over the official CEL C++) as the drop-in when conformance exactness matters more
than deployment simplicity. **Whether `celpy` passes the CEL conformance suite is NOT-FOUND on its
repository page; both must be run against the suite before commitment**, because if they diverge *on error
semantics specifically*, the rule-2 guard behaves differently between them.

**The sandbox question mostly dissolves, and that is the point.** With a restricted language there is no
model-generated Python to contain: CEL *is* the sandbox — terminating, side-effect-free, no I/O, exactly
two bound names, plus a step-count budget and a wall-clock kill. Choosing the restricted language deletes
the hardest sandboxing problem instead of solving it. What remains is the parser tier, an ordinary
container-hardening exercise.

**The predicate population, stated correctly.** There are **24 candidate correctness predicates, of which
15 are exactly settleable, 2 are settleable only after a declared normalisation (NFKC, `U+2011 → U+002D`,
strip, case-fold) that carries its own measured false-failure rate, and 7 are not settleable from the
artifact at all.** Four of the settleable ones need capabilities the admitted grammar lacks and become
**host functions** — named, deterministic, individually versioned Python with their own test suites and
their own kill rates: `reg_resolves(kind, number)` (tri-state; **never resolves live at verdict time,
always against a content-addressed snapshot**), `gstin_valid(s)`, `template_current(hash)`, and
`nav_interval(scheme_type, open_closed, tenure)` — which **must be able to return `UNDERSPECIFIED`**,
because reg 51(1) ends *"in such manner as specified by the Authority"* and a system that resolves that
delegation into a concrete interval is asserting something the regulation does not say. **A host function
may be added only by a human, is never generated by a model, and must return a third value wherever its
answer can be unknown.** The set is closed at evaluation time.

### 4.3 The five gates — C16, DECIDED, in this order

```
G0  SCOPE FAITHFULNESS   verbatim clause quote locates deterministically; every proviso, exception
                         and cross-reference in the span is either implemented as a branch or
                         declared as a NO_PREDICATE(not_yet_synthesised) emission. Neither ⇒ REJECT.
                                                                                  [structural · free]
G1  EXECUTES AND BINDS   runs on the corpus without error; every key it reads exists in the induced
                         schema; cells_bound > 0.                                 [mechanical · free]
G3ᵖ NON-DEGENERACY,      Z3: trivially-true iff ¬P is UNSAT; always-flag iff P is UNSAT; redundant
    PROOF ARM            iff P₁ ∧ ¬P₂ is UNSAT. `unknown` ⇒ unproven, never "non-degenerate".
                                                                                        [proof · cheap]
G2  SEEDED-DEFECT KILL   KR = K/O over mutants verified OBSERVABLE by recalculation, under a declared
                         versioned fault model, reported as a per-fault-class VECTOR plus U/G, plus
                         marginal kill over B0 ∪ B1 ∪ B2.                         [empirical · expensive]
G3ᵉ NON-DEGENERACY,      seed a 10% control sample into fields the predicate does NOT read; count
    CONTROL ARM          spurious fires; hypergeometric random-flagger adjusted precision.
G4  FALSE-FAILURE RATE   FFR on a corpus whose provenance ≠ SELF-AUTHORED, with n, a Wilson interval,
                         clean_corpus_independent_of_predicate, a structurally-distinct held-out
                         slice reported separately, and the MARGINAL FFR conditioned on the
                         already-admitted set.                                        [empirical]
```

**Why five and not four.** G1 — *executes without error, every key exists in the induced schema,
`cells_bound > 0`* — is a separately testable admission condition that the four-gate versions folded
silently into the kill-rate gate, and **it is precisely the condition whose absence produces the vacuous
pass.** It is nearly free and proves nothing on its own; it is a gate so that its absence is impossible
rather than merely unlikely.

**Why this order — G7, DECIDED.** G0 and G1 are free and reject the failure classes the expensive gates
cannot see, so they run first. G3's proof arm runs before G2 because a predicate Z3 proves unfalsifiable
should never consume a mutation budget. G2 is the expensive step. G3's empirical arm needs G2's harness
already warm. G4 runs last because it needs the corpus and the already-admitted set.

**Two different thresholds for the same gate, and they are different tests — C17, DECIDED. State both,
report both attrition numbers separately.**

| Test | Threshold | Question it answers |
|---|---|---|
| **The settling experiment (E6)** | `K/O > 0` **and** marginal kill strictly greater than `B0 ∪ B1 ∪ B2` | *Can a model-proposed candidate fire at all, and does it beat the free baselines?* |
| **Registry admission** | `K/O ≥ 0.80` on the fault classes the predicate **claims** to cover | *Is this check good enough to be applied to a regulated filing?* |

A predicate at `K/O = 0.05` survives the experiment and fails the registry. Both numbers are published; a
document that quotes one attrition figure has quoted the wrong one.

**The scoring, and why it is strictly better than the formula it replaces.**

```
GENERATED G · UNOBSERVABLE U (recalculated grid identical to clean) · OBSERVABLE O = G − U
UNREACHABLE R (observable, but touching no field any admitted predicate reads) · KILLED K
KILL RATE  KR = K/O   ← the headline. NEVER K/G.
REACHABLE  RKR = K/(O − R)          UNOBSERVABLE RATE  UR = U/G   ← a property of the OPERATOR MIX
```

`MS = |killed| / (|mutants| − |equivalent|)` requires `|equivalent|`, which is undecidable in general.
`K/O` needs no such term, **because our mutants are data: "observable" is a *diff*, measured by
recalculation, whereas "equivalent" is a *theorem*.** The filter is not optional — **3,512 of 7,500
(46.8%)** of naively generated spreadsheet mutants in the canonical study produced no observable change.
One measured caution the vocabulary must carry: in the first real run — **19,782 mutants in 2.5 s
(7,946 mutants/second, MEASURED)** — every arithmetic operator killed at exactly **18.1%**, identical to
the fraction of sites inside the field graph. For identity predicates, **kill rate measures predicate
*reach*, not predicate *quality*, and the report must say which it is showing.** Every suppression is
logged with its reason; an undeclared suppression is a coverage lie.

**Gate status, mapped, because the four-gate numbering is still in circulation and does not line up:**

| Five-gate name | Old name | Status |
|---|---|---|
| G0 scope faithfulness | GATE 0 | SPECIFIED |
| G1 executes and binds | folded into GATE 1 | PARTIALLY BUILT (evaluation built; the AST both-ways check specified) |
| G2 seeded-defect kill | **GATE 1** | **BUILT** — 19,782 mutants, 2.5 s, `KR` reported with its observability term |
| G3 non-degeneracy | **GATE 2** | PARTIALLY BUILT — the vacuous-bound rejection is built; Z3 is specified |
| G4 false-failure rate | GATE 3 | SPECIFIED |

**And the sentence that survives from the brief's sharpest claim, in its corrected form:** *where a
programmatic oracle exists we do not need a model; where it does not, we manufacture labels by seeding
faults rather than by asking one.*

### 4.4 What a predicate carries permanently

Everything in `qualification`, `qualified_against`, `liveness_witness` and `external_deps` is part of the
predicate's **identity**, not metadata about it, and all of it is visible on the predicate-library screen:
the clause with FRBR URI, `eId` and the verbatim quote that located it; the code and its `sha256`; the kill
rate **with its denominator and its per-fault-class vector**, the fault-model version and the unobservable
rate; the degeneracy verdict, the Z3 counterexample and the random-flagger adjusted precision; the FFR as
`(rate, corpus_id, corpus_provenance, n)` **plus a two-sided Wilson interval**, with
`clean_corpus_independent_of_predicate` and the held-out slice beside it; the marginal FFR conditioned on
the admitted set; for model-proposed predicates the model id, date and prompt hash — so a re-synthesis
under a drifted model is a **diff, not a mystery**; the admission date and admitter; and the coverage gap
it inherits (`circulars_unreadable: 10/399`). **Two things the record must never contain: a bare percentage
anywhere, and a `SELF-AUTHORED` FFR rendered as a number.** Rejections are kept, not discarded: a candidate
failing any gate becomes a `rejection` row carrying the rejecting gate, the measured number, the cells it
would have covered and the obligation it claimed — that row *is* `no_predicate.failed_qualification` and
the report's `counterEvidence[]`.

### 4.5 Versioning against a changing template

**Version churn is not a risk. It is scheduled, and it has already happened.** The template's own
financial-year vocabulary runs out at 2028-29; **23.1% of circulars amend an earlier instrument**; and the
**29th IFSCA Authority Meeting of 24 July 2026** (VERIFIED-AT-SOURCE, dated 17 days before this
specification) decided that NAV periodicity for close-ended Restricted Schemes *"may be enhanced by the FME
from semi-annual to annual, subject to prior approval of at least 75% of the investors in the scheme by
value of their investments"* — which lands directly on the most sophisticated predicate in the set, and
**the owed frequency now depends on a fact the workbook does not collect.**

The failure this policy exists to prevent, concretely: that predicate **does not error, does not abstain,
and keeps computing a date difference against a rule that no longer exists.** A filer who lawfully moved to
annual NAV gets a false failure; a filer who moved without approval gets a silent pass. Both outputs are
clean, confident and well-formed.

| Rule | Statement |
|---|---|
| **V1** | Keys are label-anchored, never coordinate-anchored. A version bump is a **re-resolution**, not a rewrite. Unresolvable keys enter an explicit `UNRESOLVED` state that **blocks** the predicate; they never silently rebind |
| **V2** | Every element of `qualified_against` is part of the predicate's identity |
| **V3** | Any change to any element of `qualified_against` moves the predicate to `PROVISIONAL`. **It still runs**, so detection is not lost, but its measured numbers are hidden and replaced by *"not re-qualified for this template version"*, and **it does not count in the settled numerator** (`no_predicate.not_yet_requalified`) |
| **V4** | **Therefore the settled fraction falls when the template changes.** That is correct. A system whose coverage silently persists across a version boundary is lying — and the step-downs are the most credible thing on the chart, because they are the only evidence the system notices when the world moves |
| **V5** | Liveness witnesses are replayed, and a predicate whose `kill_case` stops dying is **quarantined automatically**. Its limit, stated honestly: applied to the NAV-frequency predicate, the `kill_case` was built against the semi-annual rule and would still die, because the mutant and the predicate moved together. **V5 alone does not catch a rule change. That needs V6** |
| **V6** | Watch the **instrument stream**, not just the instrument. Reg 51(1)'s delegation means the rule can change by circular without the regulation changing. A daily content hash of the circular and Authority-meeting pages; any new instrument citing a regulation a predicate claims to implement moves it to `PROVISIONAL` **automatically and pessimistically**; a human clears it. This is a diff-and-flag job, not an NLP problem, and it is the only mechanism that would have caught 24 July 2026 |
| **V7** | `withdrawn_on` / `withdrawn_reason` exist on every predicate, drawn from `{rule_amended, ffr_exceeded_threshold, superseded_by, source_schema_changed}`. A registry without a withdrawal state silently carries dead checks — which is exactly what a regulator's quarterly deactivation list is a public admission of |

**What happens when a predicate silently becomes untestable** is therefore covered twice and neither
mechanism is sufficient alone: V5 catches *the artifact moved under us* (parser drift, renamed sheet,
selector miss), V6 catches *the rule moved under us*. The residual class — the rule moved **and** the
witness moved with it — is caught by neither, is named here, and is the reason the instrument watcher is
pessimistic rather than clever.

---

## II.5 — THE REPORT

### 5.1 The envelope and the body

```jsonc
// DSSE envelope · payloadType "application/vnd.in-toto+json"
{ "_type": "https://in-toto.io/Statement/v1",
  "subject": [ { "name": "filing",   "digest": { "sha256": "<hash of the workbook AS RECEIVED>" } },
               { "name": "template", "digest": { "sha256": "7d9a1960085785ee…" } } ],
  "predicateType": "https://<ns>/filing-settlement-attestation/v1",
  "predicate": {
    "assessor": { "id": "https://<ns>/verifier/0.4.1", "thirdParty": false,
                  "components": { "registryRoot": "sha256:…", "schemaInducerVersion": "1.4.0",
                                  "faultModelVersion": "v3", "extractorModel": null } },
    "timeVerified": "2026-08-14T09:12:44Z",
    "expires":      "2026-11-14T00:00:00Z",
    "runState":     "VALID",
    "livenessProof": { "canariesRun": 280, "canariesPassed": 280 },

    "scope": {
      "denominator": { "source": "induced-from-template-unlocked-mask",
                       "generatorRule": "v3",
                       "unit": "CELL",
                       "fieldSurface": 3747,          // MEASURED
                       "cellsTotal":   3747,          // == fieldSurface; DISALLOW * applies to it
                       "computedTwiceAgreed": true },
      "plannedSelection": { "includeAll": true, "exclude": [] },
      "actualSelection":  { "includeAll": true, "exclude": [] },
      "selectionDelta":   []
    },

    "settledFraction": {
      "cellsTotal":  3747,                            // MEASURED
      "outOfScope":  0, "informational": 0,
      "inScope":     3747,                            // = cellsTotal − outOfScope − informational
      "settled":     { "pass": 2361, "fail": 12, "total": 2373 },   // total MEASURED (harvest), see
                                                                    // caveat; the pass/fail split is
                                                                    // illustrative, not a measurement
      "unsettled":   { "indeterminate": 0, "notRun": 0, "noPredicate": 1374, "error": 0 },
      "fraction":    0.6333,                          // DERIVED; meaningless without the counts above
      "aggregate":   "incomplete",
      "admissibilityCaveat":
        "None of the 280 predicates producing this number is admitted under gate G4: no false-failure
         rate has been measured for any of them on a corpus we did not write. Under this
         specification's own admission rule the currently admissible predicate set is empty and the
         currently defensible settled fraction is 0%.",
      "denominatorWarning":
        "Out-of-scope determinations are filing-specific, so the denominator varies between filings.
         Settled fractions are not directly comparable across filings."
    },

    "items": [
      { "id": "portfolio.tbl31.row[7].total_value", "pointer": "/predicate/items/0",
        "cell": "3. Portfolio!O7",
        "obligation": { "id": "OBL-014", "frbrUri": "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30",
                        "eId": "reg_27__para_1", "sourceDigest": { "sha256": "…" } },
        "state": "FAIL", "reason": null, "severity": "ADVISORY",
        "method": "TEMPLATE_DIFF", "warrant": "DETERMINISTIC", "provenance": "COMPUTED",
        "cellsBound": 12, "scopeIncomplete": [],
        "evaluations": [ { "predicate": { "id": "P-0041", "version": 3, "digest": { "sha256": "…" } },
                           "state": "FAIL", "elapsedUs": 41,
                           "witness": ["3. Portfolio!O7"],
                           "ffr": { "rate": 0.021, "n": 96, "wilson": [0.006, 0.074],
                                    "corpusId": "blind-fill-v2",
                                    "corpusProvenance": "BLIND-FILLED" } } ],
        "anchors": [ /* §5.2 */ ], "override": null } ],

    "counterEvidence": [
      { "kind": "rejected-predicate", "obligation": "OBL-031", "candidate": "sha256:…",
        "rejectedBy": "G4", "measured": { "ffr": 0.382, "n": 228, "corpusProvenance": "REGISTER-DERIVED" },
        "note": "registration-number format regex; 87 of 228 live FMEs fire. Would have covered 41 cells." } ],

    "scopeCaveats": [
      { "reason": "no_predicate.not_yet_synthesised", "kind": "declared-proviso",
        "predicate": "P-0041", "eId": "reg_26__para_2", "charSpan": [10422, 10597],
        "quote": "Provided that this requirement shall not apply in case of a fund of funds scheme…" } ],

    "verdict": { "state": "EXCEPTIONS_NOTED",
                 "policy": { "file": "pervasiveness-policy-v1.json", "version": "v1",
                             "K": "PLACEHOLDER", "T": "PLACEHOLDER",
                             "status": "PLACEHOLDER — K and T have no argued basis yet" } },

    "residue": { "survivors": 12, "faultModel": "v3",
                 "adjudicationRecord": "sha256:…", "manifest": "sha256:…" },
    "declaredGaps": [ { "kind": "unread-sources", "detail": "10 of 399 circulars are scanned images" } ],
    "boundedSilenceStatement": "Had additional predicates been executed, other matters might have been
      reported. This report states only the results of the predicates listed, and makes no representation
      that the predicate set is sufficient for any purpose.",
    "purposeStatement": "This report relates only to the cells enumerated in scope.denominator and does
      not extend to the filing taken as a whole.",
    "deceptionStatement": "This system detects error, not deception. Every check here is a consistency
      check over a self-reported document. A coherent liar passes all of them.",
    "summaryIsNotSubstitute": true
  } }
```

**The field that is absent by design: there is no `result` and no `status`, and there never will be.** The
top-level object of the predicate is `scope`. **There is nowhere in the schema to write "pass", so no
downstream consumer can render one.** Schema-level prohibition beats copy discipline because it survives
the screenshot, the API integration and the intern — and it is backed by a build gate that greps every
user-facing surface for tick glyphs and all-clear language. The four statement fields are **required by
schema**: making a disclaimer a mandatory field rather than a template string is the cheapest possible way
to guarantee it survives contact with a marketing page. And `NONE ≠ NOASSERTION ≠ absent` is enforced by
the JSON Schema: `[]` means *we determined there are none*, `null` means *we make no claim*, and an omitted
field is a schema violation the validator rejects.

**On the headline.** The hero is `<F> failures across <S> checks` and `<U> fields were not checked`, in
equal type, populated from the measured triple **2,373 / 1,374 / 3,747**. It is never populated from a
predicate-enumeration count. The reason the fraction had to go is that the decidable set is unbounded and
mechanically expandable — one predicate per formula-evaluating cell, per data validation, per shipped
vocabulary is `505 + 54 + 15 = 574`, taking a hand-classified 24-predicate ratio to `574 / 581 = 98.8%`
without writing a single interesting check. **That figure is DERIVED — an enumeration argument, not a
run** — and it exists in this specification only to demonstrate that the fraction is manipulable.

**And the corrected sentence about what the 63.3% means, which is stronger than the version it replaces:**

> *"280 predicates are mechanically derivable from the regulator's blank template with no model, and they
> touch 2,373 of 3,747 filer-editable cells. **None of them is admitted yet**, because no one has measured
> a false-failure rate for them on a corpus we did not write. That is the point: the number you are looking
> at is what every compliance product ships, and it is the number our own gate is designed to refuse. Watch
> what happens to it after qualification — that delta is the product."*

Two composition facts travel with it or it is not quoted: **2,329 of the 2,373 settled cells (98.1%) come
from the 53 validation predicates, not the 227 arithmetic ones**, and the validation-carried share is
weaker per cell — which is exactly what G3 exists to reject. And the cross-workbook figure **515** is
always published with its per-workbook distribution attached, never alone, because two of the nine
workbooks have zero formulas and one has zero validations too.

### 5.2 The provenance anchor

Docling's `ProvenanceItem` is adopted **verbatim** for the PDF class (`page_no`, `bbox{l,t,r,b,coord_origin}`,
`charspan`, optional `table_cell` offsets), which removes a translation layer and a coordinate-origin
guess, and the union is extended with two locator kinds document AI does not model: **`xlsx_cell`**
(carrying `formula.encoding ∈ {TEXT, SHARED_MASTER, SHARED_DEPENDENT, ARRAY, NONE}` — not decoration:
recording the encoding is what makes the 294-versus-505 undercount impossible to repeat silently) and
**`register_record`**. The register anchor carries **both `raw_value` and `normalised_value`, plus the
transformation list** — mandatory, because one live regulated entity's registration number contains
`U+2011 NON-BREAKING HYPHEN` rather than `U+002D`: visually identical, byte-wise different, invisible in
any log or screenshot. **A system that stores only the normalised form has destroyed the evidence that its
own normalisation was load-bearing.**

### 5.3 Exact relationship to the four standards

| Standard | What we take | What it cannot do — exactly |
|---|---|---|
| **OSCAL** (CC0 1.0 — no licence obstacle to profiling, forking or embedding) | `reviewed-controls` (planned versus actual scope with the delta visible); `observation.methods` and `origin-actor.type ∈ {tool, assessment-platform, party}`, so it can say *a machine asserted this*; `assessment-assets` for the registry version; `observation.expires`; and the **POA&M model as the unchecked panel's interchange format** — reason plus what would make it checkable is exactly a `poam-item` plus a `risk.response.lifecycle`. Tooling: `compliance-trestle`, Apache-2.0, ships pydantic models plus detached JSON signing | `finding-target.status.state` is a **closed two-value enum `{satisfied, not-satisfied}`** — the one field this product exists to add states to. Non-coverage is expressed by omission plus free-text scope, and `findings` was made optional in 2021, so **an OSCAL AR with zero findings is schema-valid and means nothing in particular.** Its ontology is security-control-shaped and **has no cell.** *The useful negative result:* OSCAL was asked for exactly this vocabulary in 2021, citing XCCDF's result states, and resolved it by adding an **open `reason` token** rather than states. Encoding our third state there would get OSCAL's syntax without OSCAL's validation — a validator would accept `{"state":"satisfied","reason":"actually-we-never-checked"}`, which is the worst of both |
| **ISRS 4400 (Revised)** — agreed-upon procedures | ¶30(j)'s **bounded-silence sentence as a required schema field**; ¶30(h)'s disclaimer of procedure appropriateness; ¶13(f)'s finding-is-objectively-verifiable definition; ¶32(b)'s "reading the summary is not a substitute"; and Appendix 2 Illustration 2's stated circumstances — **the regulator is the intended user and the entity it oversees is the engaging party**, which is our exact two-party model, already contemplated, with a report template supplied | The report is **human prose in a two-column Procedures/Findings table**: no schema, no closed vocabulary, no machine-readable form, no fraction, **no per-procedure error rate.** ¶A56's not-performed declaration is a *may*, not a *shall*, and it is free text. And **every procedure is agreed with the engaging party in advance, with its adequacy expressly disclaimed** — the denominator is negotiated, where ours is induced |
| **in-toto / DSSE** — **Apache-2.0, VERIFIED-AT-SOURCE** (the LICENSE file was opened and quoted) | The envelope; `subject[]` carrying **both** hashes, because a verdict against template v3 is meaningless if the entity filed on v4; and the deepest borrowing, the **`DISALLOW *` closed-world principle** — our L1-induced schema **is** the layout, which is why the closure is possible for us | Its subject is a build pipeline; steps are commands and artifacts are files. No notion of a partially-verified artifact, no reason codes, no coverage semantics in the envelope. Its standard `test-result` predicate has `passedTests[]`, `warnedTests[]`, `failedTests[]` and **no `skippedTests[]` — the standard test attestation cannot express a test that did not run** |
| **CycloneDX** | Three things, none of them the one usually cited. **(a)** `compositions.aggregate` demoted to one roll-up header field (six states in 1.3, ten in 1.5 — not ten in 1.2). **(b)** `declarations` (CDXA, 1.6): `assessors[].thirdParty` — *"a value of false indicates a self assessor"* — `attestations[].map[].{claims, counterClaims, conformance}`, and `standard.requirements[]` with regulations explicitly in scope. **(c)** 1.7's `citation` with **RFC 6901 JSON Pointers**, the right idiom for addressing a verdict to an exact location | `aggregate` is aggregate, not per-item: it says the *set* is incomplete and cannot say *which* component was not examined or why. CDXA's `conformance` is a **continuous score in [0,1] with free-text rationale — there is no discrete "not assessed" state, and a score of 0 is indistinguishable from "we never looked."** A float plus prose is exactly the interface we are arguing against |

**Projection rule, so the loss is explicit and auditable.** `PASS → satisfied`; `FAIL → not-satisfied`;
`INDETERMINATE / NOT_RUN / NO_PREDICATE →` an `observation` with our reason as a `prop`, **no finding**, and
a matching `exclude-controls[]` entry; `OUT_OF_SCOPE →` an `exclude-controls[]` entry only;
**`INVALID` → not representable at all.** Any party reading only the projection sees a smaller, cleaner
report than the truth, so the projection carries a **mandatory `metadata.prop` flagging it as lossy and
naming the URI of the normative artifact — in the file, not in a README.**

### 5.4 Signing

**DECIDED: the filer signs, with a detached key, over the report JSON. The vendor signs nothing about the
filing; the vendor appears only as `assessor.id` with `thirdParty: false`.** *Alternatives it beat:* **the
vendor signs** — the vendor would be attesting to a regulated filing it did not prepare, and **if an FME
shows an inspector a signed attestation over a filing that was wrong, the signature is the first exhibit**;
**Sigstore keyless** — keyless signing binds an identity into a public certificate published permanently,
so the fact and timing of a named entity running a pre-submission compliance check becomes world-readable
and correlatable (if a log is wanted, run a **private instance operated by the supervisor**, publishing
only salted hashes of filing identifiers); **no signature at all** — then the coverage claim is marketing
and the boundary can be restated later. Envelope: **DSSE + in-toto Statement v1** over **JWS/JSF**, because
it is Apache-2.0 (VERIFIED-AT-SOURCE), it is what the attestation ecosystem already speaks, and `subject[]`
naturally carries the two hashes. `--tlog-upload=false` is asserted in a test.

**The residual item is legal review of that decision, not the decision itself. OPEN — USER DECISION:
is a real FME prepared to sign, and does your legal review accept filer-side self-attestation as the signing
model?** Until it is answered, the demo signs a synthetic filing with a demo key and the demo script says
so out loud.

**Byte-identity — G12, DECIDED.** `verify` re-runs the pipeline pinned to
`{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha, evaluator_version,
fault_model_version, tool_versions{python, lxml, openpyxl, celpy, z3}}` and asserts a byte-identical
report. **LibreOffice is not in that list and is not on the verdict path** (§II.1.2). The four sources of
non-determinism are removed rather than tolerated: the mutable register is pinned by snapshot hash and the
host function never resolves live at verdict time; wall-clock time is an input recorded in the manifest and
CEL binds no clock; iteration order is fixed by RFC 8785 canonicalisation and explicit sort keys; and there
is no floating point, because money is `int64 MILLI_USD_MILLION` and tolerances are integers. **A model
call is never on the re-derivation path**: if a filing had attachments, the *facts* L2b produced are
content-addressed and pinned, and `verify` replays those facts rather than re-calling the model. That is
the only honest treatment — a model output is an input to the verdict, not a step of it.

---

## II.6 — THE SELF-CHECK LAYER

### 6.1 The claim, restored

> **No assurance artifact in existence carries evidence that the instrument that produced it was working on
> the specific document it examined. A clean audit opinion does not. An SBOM does not. A validation report
> does not. Ours refuses to issue a verdict unless every check has just demonstrated, on your file, that it
> can still catch the fault it was admitted for.**

That sentence is falsifiable, it is not a novelty claim about a mechanism, and it needs no citation — the
mechanism is two extra executions per predicate. The hedged version ("we self-test") buried the actual
claim, which is that **the verdict is conditioned on a proof obtained from the artifact under test, in the
same execution, and is withheld when that proof fails.** The nearest named prior art is SRE synthetic
monitoring and hardware built-in self-test, not anything in the testing literature. *A formal-methods
citation for vacuity detection is **UNVERIFIED** and must not be asserted.*

### 6.2 The mechanism

```python
def verdict_with_self_check(filing, predicates):
    result = run_all(filing, predicates)
    silent = []
    for p in predicates:
        # instantiate THIS predicate's stored kill_case against THIS filing's cells,
        # in the in-memory fact table — never against the file, never re-serialising it
        mutant = p.liveness.kill_case.apply(filing.facts)
        if not run_one(mutant, p).state == "FAIL":
            silent.append(p.id)
    if silent:
        return Report(run_state="INVALID", reason="error.canary_silent",
                      dead_predicates=silent,
                      settled_fraction=None,      # not zero. Not omitted. NULL.
                      verdict=None)               # a finding about us, not about the filing
    return result.with_liveness_proof(run=len(predicates), passed=len(predicates))
```

**Why it is the answer and not a nicety.** It runs **on the artifact under test, not on a training
corpus**, so it catches parser drift, selector misses, renamed sheets, hidden-sheet truncation, encoding
changes and empty-set vacuity **for this file** — the failure class that produced five documented instances
inside this project's own research, three mechanisms, all under-counting in the same direction. L4
qualifies predicates **at admission, against the corpus of that moment**; nothing else re-checks at run
time that the predicates still bind to anything.

**Cost.** Canaries operate on the in-memory fact table, not the file. At the measured harness throughput of
**7,946 mutants/second (MEASURED)**, 280 canaries ≈ **35 ms** (DERIVED from a measured rate; the canary
loop itself is not yet built) against a ~30 ms baseline pipeline. **There is no reason not to.**

**What makes a run `INVALID`** — the complete list, and each is an engineering incident rather than a
filing outcome: a container guard trip · structural disagreement between the readers on
`{n_sheets, sheet_names, hidden_sheets}` · an unbound template · `cells_bound == 0` on any predicate · a
predicate raising inside `expr` · **a silent canary** · a closure violation · the two denominator
computations disagreeing. An `INVALID` run renders a report that states which of these fired, carries
**no settled fraction at all**, and sets the aggregate verdict to `null`.

### 6.3 The residue set, and the class that is the product

```
1. Take the filing under test, F.
2. Generate mutants of F under a declared, versioned fault model.
3. Adjudicate each: INNOCUOUS (still correct) / WRONG (materially false).   <- the only human step
4. Run the full admitted predicate set + every admitted relation on every WRONG mutant.
5. RESIDUE := { WRONG mutants that no predicate and no relation rejects }
6. Report |RESIDUE| and, for each survivor, the class of falsehood it represents.
```

**It cannot be inflated by boring checks**, because the residue is populated by falsehoods consistent with
every arithmetic relation in the file — which is exactly the property the fraction lacks. **It converts a
hand classification into a measurement**, and it is **reproducible given the published fault model *and the
published adjudication record*, both content-addressed** — step 3 is a human INNOCUOUS/WRONG judgment,
it is one-time per fault-model version, and it is auditable per mutant by content hash. Saying "a third
party can re-run it" without naming the adjudication record would repeat the error this whole document
exists to correct.

**Three mutant classes, and the third one is the product.** Code mutation testing has one nuisance class,
the equivalent mutant. Data fault seeding has two, and they point in opposite directions. **INNOCUOUS** —
a data edit that leaves the filing correct (reordering rows where order carries no meaning, reformatting a
number, rewording a rationale); like equivalent mutants these cannot be killed and **must leave the
denominator**, or the score is understated. **WRONG-AND-KILLABLE** — the ordinary case. And:

> **A prescribed return is a closed arithmetic system. We can construct, and exhibit, a family of filings
> that are internally perfect under every relation the regulator's own template encodes and every relation
> we have added — and materially false. That family is non-empty by construction, its size is measurable,
> and measuring it is the first quantitative statement anyone has made about the limit of document-level
> verification for a regulated filing.**

In code mutation testing a mutant that changes behaviour is in principle killable by *some* test. Here, a
mutant can change the **truth** of the artifact and be **provably unkillable by any predicate over the
artifact alone.** That is not a coverage gap; it is a theorem about the artifact class, and it is the
reason the risk *"the residue set comes back empty"* is graded **Low → structurally impossible** rather
than merely unlikely. It is also the honest content of the unchecked panel: that panel should not list
reasons, it should list **demonstrated survivors** — a coordinated misstatement propagated through all 181
cross-sheet carries and all 35 SUM identities, exhibited, with its content hash.

**And the sentence that stays permanently on the report surface, because it is the boundary the residue set
measures from the other side:** *this system detects error, not deception. Every check here is a
consistency check over a self-reported document. A coherent liar passes all of them.*


---

# PART III — THE TECHNOLOGY STACK AND THE BACKEND FLOW

**Warrant key, governing every number below.** `MEASURED` — run against the primary artifact.
`VERIFIED-AT-SOURCE` — the primary document was opened and the value read off it. `SECONDARY` — a
credible source states it; the primary was not opened. `DERIVED` — arithmetic from stated inputs, and **it
never claims a stronger warrant than its weakest input**. `UNVERIFIED` — could not check. Every fraction
carries its denominator inline.

**Four renames are decided here and bind every JSON key, API path and screen label in the programme.**

| Old | **New** | Why |
|---|---|---|
| `coverage`, `coverageFraction` | **`settledFraction`** | "Coverage" is reserved for the conformal guarantee, which appears three pages away. One word, one meaning |
| money in "micro-units" | **`MILLI_USD_MILLION`** — `int64` count of 10⁻³ USD Million; **1 unit = USD 1,000**; `12.34 → 12340`; half-ulp 5 units; `τ(n) = 5n` | The drafts differed by 10³ and every tolerance is in units |
| the `(field × obligation)` pair | **the cell** | The unit of the denominator, of closure and of the settled fraction is the filer-editable cell. `obligation` becomes a predicate attribute (§4.2) |
| `COVERAGE_INSUFFICIENT`, `…WITHIN_STATED_COVERAGE` | **`SETTLEMENT_INSUFFICIENT`**, **`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`** | Same rename on the verdict enum. The property that matters — a verdict name unquotable without its own qualifier — survives |

---

## 1. THE DECISION TABLE

Every row is a decision: the component, the decision, the runner-up it beat, the evidence, the **licence
with its warrant** — a licence read at source and a licence merely reported are different facts and the
table shows the difference — and the testable trigger under which we switch.

| # | Component / layer | **DECISION** | Beat | Evidence | Licence + warrant | Switch when |
|---|---|---|---|---|---|---|
| 1 | Workbook parsing — authoritative reader | **`zipfile` + `lxml` 6.1.1, namespace-aware, over sheet XML, `styles.xml`, `sharedStrings.xml`, `workbook.xml`, `extLst`** | openpyxl 3.1.5 as schema source | openpyxl sees **35 of 54** validations and reports the AML-CFT sheet as **0 when it is 5**; a hand regex reaches the identical wrong 35 by the identical mechanism. Full parse **28 ms** (MEASURED, L14) | BSD — **SECONDARY** | Never for schema induction. Hard rule, with a constants test |
| 2 | Second reader | **openpyxl 3.1.5: formula text with shared-formula row-shifting; `data_only=True` cached values** | Hand-rolling `si`→master translation | openpyxl returns the *translated* dependent (`O4 → =SUM(C4:N4)`), which a hand-rolled reader gets wrong. 202 ms (MEASURED) | MIT — **SECONDARY** | We write and mutation-test our own translator. Until then: never for validations, **never to re-serialise** (round-trip loses 98.2% of bytes and all 19 `x14` validations, MEASURED) |
| 3 | Third reader / normaliser | **LibreOffice headless, pinned by container digest, offline only — not on the verdict path (§7 G12)** | LibreOffice as primary analysis path | It expands all 505 formulas and migrates `x14` into the main namespace in 3.9 s — **but writes 53 where 35 + 19 = 54: one validation lost, unexplained, in the step being recommended** (MEASURED, L05) | MPL-2.0 — **SECONDARY**; file-level copyleft, subprocess use imposes nothing | The 53-vs-54 loss is characterised as a duplicate-`sqref` merge |
| 4 | Schema induction | **Ours, ~200 lines over the OOXML cell graph** | QuantMind (2.3k★) | BUILT, 28–44 ms: 505 formula cells, 54 validations, 3,747-cell field surface, 280 predicates (MEASURED, L14) | MIT — SECONDARY (not adopted) | Never. **Do not take a 2.3k-star dependency to save 200 lines** |
| 5 | Regulation-text parsing | **Docling → `DoclingDocument`; `ProvenanceItem{page_no,bbox,charspan}` adopted verbatim as our `pdf_span`** | MinerU | Docling publishes the only typed, versioned, per-cell provenance schema with an explicit `coord_origin` enum (VERIFIED-AT-SOURCE, L08) | Docling MIT — SECONDARY. **MinerU is Apache-2.0 *plus riders* — VERIFIED-AT-SOURCE**: its §2 requires prominent attribution for any online service. "Apache-2.0" on a slide would be false | Docling's table fidelity blocks a clause. Then PaddleOCR-VL primary |
| 6 | Scanned circulars | **PaddleOCR-VL, run once offline, output frozen and content-addressed** | olmOCR, Marker, Nougat | 10 of 399 circulars are images (2.5%). Marker is worst on OmniDocBench v1.6_full tables (TEDS 65.77); Markdown linearisation destroys the anchor | Apache-2.0 — SECONDARY | Never re-enters a verdict path |
| 7 | Clause identity | **Akoma Ntoso: `eId` per clause, FRBR URI per instrument, via a deterministic promoter** | Inventing a clause-key scheme | OASIS standard designed for amendment commands. **866 dated cross-references in 58.6% of circulars; 76 of 82 amending circulars cite a resolvable target (92.7%)** (MEASURED, L08) | OASIS spec — no obstacle | Never |
| 8 | FRBR URI handling | **Implement the URI grammar ourselves, ~100 lines** | `laws-africa/cobalt` | GitHub reports **NOASSERTION** for `cobalt` and `indigo`; no lane opened either LICENSE | **NOT-FOUND**. `bluebell` is **GPL-3.0 — VERIFIED** and must never be linked | Someone opens `cobalt`'s LICENSE and it is permissive. We adopt Indigo's amendment/point-in-time *data model* either way, never the platform |
| 9 | Citation anaphora | **Ours, modelled on `eyecite`'s antecedent architecture** | Adopting `eyecite` | Its power is `reporters-db`/`courts-db` — US case reporters, zero knowledge of `IFSCA/GN/2025/…`. **The algorithm transfers; the data does not** | BSD-2 — SECONDARY (not adopted) | An Indian statutory-citation library is found. **L08 states it did not search that ecosystem at all** — that search must run before any novelty claim here |
| 10 | Predicate language | **CEL, admitted subset, in a three-slot envelope `applicable`/`expr`/`witness`** | Python + pandera | **The settled fraction is statically computable only because the language has no variables**; model-written Python needs a sandbox and the sandbox layer is where the 2026 CVEs are; an auditor must read a rule, not a function body; a ~20-production grammar has enumerable mutation operators. Precedent: **Kubernetes ValidatingAdmissionPolicy, GA in v1.30** | Apache-2.0 spec — SECONDARY | A predicate class the grammar cannot express **and** cannot be quarantined into a host function. Rego only if the stack moves to Go |
| 11 | CEL runtime | **`celpy` (`cloud-custodian/cel-python`), pinned by PyPI name *and* wheel hash** | `cel-expr-python` | Pure Python, no C++ build, auditable. **Naming trap: two different projects live at a path called `cel-python`** | Apache-2.0 — SECONDARY | `celpy` fails the conformance suite **on error semantics**, where the `&&`/`\|\|` guard lives. `cel-expr-python` wraps the official C++ and inherits conformance |
| 12 | Arithmetic representation | **`MILLI_USD_MILLION` (see rename table)** | `double`; or `Decimal` outside CEL | CEL has **no decimal type**. Guidance C111 fixes 2 dp on USD Million, so the quantum is USD 10,000 and lawful per-cell slack USD 5,000. As `double`, every arithmetic predicate acquires an FFR we did not choose and cannot attribute | — | Never |
| 13 | Tolerance model | **`τ(n) = 5n` units, declared in each predicate and versioned with it; `ROUND_HALF_UP`; counts get zero tolerance** | A constant epsilon | A constant epsilon is the likeliest source of spurious failures. Two predicates differing only in tolerance are two rows with two measured FFRs — **which makes tolerance a measured parameter, not a hidden constant** | — | Never |
| 14 | Formula evaluation | **Ours: topological evaluator over the induced cell graph in `Decimal`; eight functions — `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)`** | `formulas` 1.3.4 | Licence: `formulas` **EUPL 1.1+**, `pycel` **GPL-3.0** (SECONDARY) — copyleft with a live network-deployment question. Method: an imported evaluator imports an unmeasured error rate our own gate would reject. **And building it is the differential arm** — the only check that detects a formula cell overwritten with a literal | Ours (Apache-2.0) | A template's function vocabulary exceeds what we implement exactly |
| 15 | Cross-check recalculation | **The template's own cached values (present on 505 of 505 formula cells, MEASURED) are the primary cross-check; LibreOffice is the *offline* second engine** | Trusting one engine online | The 91.9% LibreOffice recalc-exact figure comes from a **three-hour, unreplicated, self-graded vendor repo** whose top entrant is the owner's product — ruled **evidentially void**. So we quote no floor and **measure disagreement per cell, per template version, offline** | MPL-2.0 — SECONDARY | The engines agree across the full 505-cell graph with a positive control on `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101` |
| 16 | Degeneracy prover | **Z3 for the proof arm of gate G3: `¬P` SAT, `P` SAT, subsumption `P₁ ∧ ¬P₂` UNSAT** | Empirical degeneracy alone | It is a satisfiability question; CEL's comparison fragment maps to SMT-LIB nearly 1:1; Z3 returns a **model** — a counterexample workbook that enters the library as evidence | **MIT (SECONDARY — the LICENSE was not opened by any lane; open it before shipping)** | Never removed, never trusted alone. Host functions are uninterpreted; `unknown` is treated as **unproven, never as non-degenerate** |
| 17 | Fault-seeding harness | **Ours, ~200 lines. Abraham & Erwig's 17 spreadsheet mutation operators (IEEE TSE 35(1):94–108, 2009) + F12 vocabulary drift, F13 carry desync, F14 vocabulary-gap exploitation** | mutmut / PIT / Stryker | **Category error**: those mutate source code; our mutants are *data* and the subject under evaluation is the *predicate set*. BUILT: **19,782 mutants in 2.5 s = 7,946/second** (MEASURED, L14) | Ours (Apache-2.0); mutmut BSD-3 — SECONDARY, retained for mutating **our own** code | Never |
| 18 | Scoring | **`KR = K/O` with both integers, plus `UR = U/G`, plus the per-fault-class vector. Never a bare percentage** | `killed/(mutants − equivalent)` | **3,512 of 7,500 (46.8%)** comparable spreadsheet mutants are irreversible. A rate over *generated* mutants understates every predicate by roughly half, variably by operator mix. **Observability is a diff; equivalence is a theorem** | — | Never |
| 19 | Registry minimisation | **Reimplement SPADE's ILP in PuLP/CBC, ~40 lines, with the interaction bound `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`** | `shreyashankar/spade-experiments` | 17★, 1 fork, **no LICENSE file present**, last push 2024-04-07. Unlicensed is unusable in a commercial product regardless of quality | PuLP MIT / CBC EPL-2.0 — SECONDARY | Never |
| 20 | Interval statistics | **Wilson interval on every rate, ~8 lines. A point estimate is forbidden by schema** | A bare percentage | `0 fires / 4 real → [0.000, 0.490]`. **A real FFR from 4 real filings with an interval of [0, 0.49] is more honest and more useful than 0.0% from 340 workbooks we wrote ourselves** | — | Never |
| 21 | Differential / relation execution | **`Hypothesis` `RuleBasedStateMachine`: `@invariant` for *necessary* relations (⇒ FAIL), in-rule assertions for *expected* (⇒ `INFORMATIONAL`). `max_examples = 50`** | Hand-rolled loops | The necessary/expected split is enforced by the library, not by our convention. **55% of mutations found at n = 1, 76% within 20 inputs** — the input space is small and fixed | **Reported MPL-2.0 — SECONDARY, LICENSE not re-read.** This ledger does not assert a licence nobody opened | Cross-table set relations outgrow a CEL one-liner. Then Soufflé (UPL-1.0), at the cost of a second toolchain |
| 22 | Relation authorship | **Human, read off the formula graph and guidance notes. No model** | Asking a model for relations | MEASURED: model-generated relations score *"markedly low"* on novelty — which is how the brief got five relations of which **four false-alarm on a correct filing and the fifth is vacuous** | — | Never. **The one layer where the model is measurably worse than a person with the file open** |
| 23 | Conformal / abstention | **`crepes` (`MondrianCategorizer`) + `MAPIE` (`OnlineMartingaleTest`), RAPS over the induced key set — BUILD GATED** | `TorchCP` | TorchCP is **LGPL-3.0 (SECONDARY)**; `nonconformist` dead since 2021-03-20; `Fortuna` archived; `puncc` ships no root LICENSE | crepes / MAPIE BSD-3 — SECONDARY | **Pre-registered gate:** measure key-binding accuracy `μ`. Forced abstention `r ≥ (μ−α)/(1−α)`. **`μ > 0.30` ⇒ do not build it** (α = 0.05 forces ≥ 26.3% abstention from base error alone); `μ ≤ 0.10` ⇒ build; between ⇒ build and ship the **abstention rate** as the headline |
| 24 | Structured output (attachments) | **Provider-native structured output, `key` typed `Literal[*L1_KEYS]`, retry disabled, plus the post-hoc deterministic key check** | `outlines` / `XGrammar` | The key is an enum over exactly the induced keys, so an off-schema key is **ungeneratable**. `outlines`/`XGrammar` mask logits and are strictly better **but require a local model, and no local model is in this stack**. **Whether provider-native constraint is guaranteed or best-effort is UNVERIFIED — which is exactly why the post-hoc guard is not optional** | Apache-2.0 — SECONDARY (not adopted) | **An open-weight model enters this path. Then `outlines` becomes primary.** Retry-until-valid is banned outright: it manufactures the clean verdict this product exists to refuse |
| 25 | Model provider | **Anthropic** | Open-weight local | The comparison is **UNVERIFIED**; a guessed URL is the fabrication this programme forbids. **The architecture converts it into a measurement:** the gate adjudicates deterministically, so *model choice affects yield, not correctness*. Measure admitted predicates per unit cost | — | The measurement says otherwise |
| 26 | Model — candidate proposal | **`claude-opus-5`, Batch API (50% off), prompt caching on the schema prefix. Offline, once per template version** | `claude-sonnet-5` | A bad candidate costs a rejection, not an error — the right place to spend on capability. Offline ⇒ Batch applies; stable prefix ⇒ caching applies. **The failure mode being bought down is a plausible-but-wrong check** | — | Yield-per-rupee says Sonnet 5 wins. Under ten dollars either way (§5) |
| 27 | Model — attachment extraction | **`claude-haiku-4-5` bulk, escalating to `claude-sonnet-5` when the conformal set is not a singleton** | Opus 5 for everything | The hard key guard makes failures cheap: a wrong key is caught, a non-singleton set abstains. **A filing with no attachments has a marginal model cost of exactly $0.00** | — | Escalation exceeds ~30%; promote the bulk model |
| 28 | Model — evaluation, relations, verdict, attestation | **No model. Anywhere. Ever.** | LLM-as-judge | LLM judges detect false success at **AUROC ≤ 0.65, 13% recall at a 10% flag rate**; TF-IDF + logistic regression over the same trajectories reaches 0.825–0.953 at **3,364× lower latency** — and even that runs at **50% precision at a 10% flag rate** | — | Never. Enforced at schema level: `MODEL_EXTRACT` may never be the sole `method` on a `PASS` |
| 29 | Data-validation substrate | **Ours. There is no substrate to adopt.** `pandera` 0.32.1 adopted **only** as a host-function implementation for bulk column checks | Great Expectations / Soda Core / dbt / Deequ | **GX is disqualified on semantics:** with `catch_exceptions=True`, *"execution will not fail… it will return `success = False`"* — the same value it returns when the data was wrong. **A framework that folds *could-not-check* into *failed* destroys the denominator**, which is the product. No field for not-applicable, out-of-scope or no-oracle at any verbosity | pandera MIT — SECONDARY (version VERIFIED-AT-SOURCE via PyPI JSON; its release date **UNVERIFIED**). **Soda Core is Elastic 2.0 — VERIFIED-AT-SOURCE**: *"You may not provide the software to third parties as a hosted or managed service"*. Our product **is** that | Never. Read *"do not rebuild Great Expectations"* as: **do not rebuild the check library; you must build the verdict model, because it exists nowhere in the ecosystem** |
| 30 | Model-free baselines, run **before** the model | **B0 the template's own 138 checkable relations · B1 Daikon over the clean corpus · B2 the degenerate arm** | Proposing without baselines | The free baseline beats the neural method more often than not here: SPADE's select-all is 100% settled at 100% FFR; TOGA's `NoException` baseline gets **68.9% of TOGA's bugs at 2× the precision**. **If proposal does not beat B0 ∪ B1 ∪ B2 on marginal kill at equal FFR it has produced nothing** | Daikon MIT-equivalent — SECONDARY (licence text not opened) | Never. Daikon's trivia output doubles as the degeneracy list |
| 31 | Sandboxing — parser tier | **gVisor (`runsc`) + `seccomp` + `--network=none` + read-only rootfs + capped tmpfs + non-root uid + `no-new-privileges` + RLIMITs + wall-clock kill; zip guards *before* parse; `lxml` with `resolve_entities=False`, no DTD, no network** | Firecracker | The threat model is a confused model and a malformed file — but the **filer** is hostile-capable and an `.xlsx` is a zip of XML. **The parser, not the predicate, is the exposed surface.** Firecracker buys hypervisor isolation against an adversary we do not have, at a VM per filing | **NOT-FOUND** — no lane opened gVisor's LICENSE. Widely reported Apache-2.0; not asserted here. **Open it before the code ships** | Multi-tenant SaaS with untrusted tenants. **E2B rejected permanently**: the filing would leave our boundary — a data-residency conversation about regulated filings we should not have to have |
| 32 | Sandboxing — evaluator tier | **An ordinary process. CEL is terminating, side-effect-free, has no I/O and binds two names: the language *is* the sandbox.** Plus a step-count budget and a wall-clock kill | Pyodide / WASM; RestrictedPython | **WASM-of-CPython is a resource boundary, not a security boundary.** In the Grist "Cellbreak" escape (`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1) a spreadsheet formula escaped Pyodide by **three independent routes**, fixed by putting Deno's permission system underneath. RestrictedPython's own docs: *"not a sandbox system or a secured environment"*. **Correction that travels with this: CVE-2026-5752 is against Cohere Terrarium, not Pyodide** | Pyodide MPL-2.0 — SECONDARY (not a boundary) | Client-side predicates: Pyodide returns as *portability* only |
| 33 | Storage and content addressing | **SQLite + `blobs/sha256/<aa>/<rest>`; sha256 over exact received bytes, lowercase hex, plus a per-sheet hash of every `xl/worksheets/sheetN.xml`** | PostgreSQL | **SQLite is a file, so it can be hashed and named in the run manifest** — exactly what the attestation needs. A Postgres cluster cannot be content-addressed. Per-sheet hashes let a re-derivation say *which* sheet changed | Public domain — SECONDARY | **A second concurrent writer exists.** That is the trigger — not row count, not volume (§5.3) |
| 34 | Attestation and signing | **DSSE + in-toto Statement v1; `subject[]` carrying the filing digest **and** the template digest; `predicateType: …/filing-settlement-attestation/v1`; local Ed25519 key, `--tlog-upload=false`** | JWS/JSF; Sigstore keyless + Rekor | `subject[]` carries the two hashes that must be bound — **a verdict against template v3 is meaningless if the entity filed on v4**. **Rekor is a public log**: a named FME's pre-submission check must never be published to it | **in-toto/attestation: Apache-2.0 — VERIFIED-AT-SOURCE** (L10 opened the LICENSE and quotes it). **cosign: Apache-2.0 — SECONDARY**, LICENSE not opened | Sigstore's public-instance logging/retention policy is opened and read. Until then keyed mode with the log off, **asserted in a test** |
| 35 | Result vocabulary | **8 states × 30 namespaced reason codes (§4.4); `override` orthogonal; `severity_tier` set by measured FFR** | `PASS/FAIL/UNCHECKED` × 6 flat reasons | Without `OUT_OF_SCOPE` the fraction is computed against the wrong denominator on every real filing (217 heterogeneous FMEs will not populate all 10 sheets). Without `ERROR`, a crashing predicate is indistinguishable from an uncheckable property. Without `no_predicate.failed_qualification` the gate's rejections are discarded | — | A code is admitted **iff it implies a different remedy** from every existing code. That test is why 30 beats 6 and why it is not 60 |
| 36 | API framework | **FastAPI 0.141.1** | Litestar 2.24.0 | **Not a performance argument.** ~18 paths over a sub-second computation; throughput is irrelevant by three orders of magnitude and the binding constraint is how fast a mentor or judge reads the code. Django-ninja rejected: it puts a migration between us and a reproducible report | MIT — SECONDARY | The team already knows Litestar |
| 37 | Job execution | **Synchronous request/response. No queue, no broker, no workers.** Offline sweeps from a `Makefile` + the Batch API | Celery / Redis / RQ | MEASURED: the deterministic core is ~30 ms; the 19,782-mutant campaign 2.5 s. **The question "do we need a queue for a sub-60-second job" does not arise for a sub-second job** | — | If in-process queuing is needed, a SQLite/Postgres job table **before** any broker |
| 38 | Frontend — the report | **One self-contained HTML file: inline CSS and JS, no external requests, server-generated** | Next.js + shadcn/ui | It opens from `file://` with the wifi down; it is phone-safe with no build target; it is **emailable**, which is how a compliance officer shares a report; and decisively **it is the attested artifact — a file has a hash, a single-page app does not** | — | Never for the report. **SvelteKit is the post-residency answer for the shell.** Streamlit/Reflex/NiceGUI rejected permanently: all bind the UI to a live session |
| 39 | Frontend — shell | **Jinja2 from FastAPI + Tailwind compiled to a static stylesheet + ~50 lines of vanilla JS** | Any SPA framework | Five screens, ≤ 515 rows in the largest table; a plain `<table>` with a filter renders 280 rows in under 200 ms | — | The registry passes ~5,000 rows |
| 40 | Deployment | **One Docker container on Fly.io (`shared-cpu-1x`, 512 MB). The laptop is the demo path and is mandatory as the fallback** | Vercel + Railway | Two targets, two failure modes; Vercel's serverless model fights a long-lived registry file and a content-addressed blob directory. **New Fly.io accounts get no free allowance** (legacy tier closed to organisations created after 7 Oct 2024, VERIFIED-AT-SOURCE) | — | A second concurrent writer or a real availability obligation |
| 41 | Observability | **The run manifest, content addressing end to end, a JSONL log (`{predicate_id, state, reason, cells_bound, elapsed_us}`), and `verify`** | OpenTelemetry / Sentry | Sub-second, single-node; tracing would be theatre. **The question a downstream reviewer asks is not "what was the p99" but "can I get this same answer again", and `verify` answers it** | — | A real user is on the system |

**Rows 10, 17 and 28 are one decision seen from three sides**, and it is the programme's thesis executed
as engineering: *where a programmatic oracle exists we do not need a model; where it does not, we
manufacture labels by seeding faults rather than by asking one.*

---

## 2. THE ADOPTED OPEN-SOURCE LEDGER

| Project | Used for | Explicitly **not** used for | Licence + commercial implication | Maintenance risk | Fallback if abandoned |
|---|---|---|---|---|---|
| **`lxml` 6.1.1** | Every authoritative OOXML read, incl. `styles.xml` (the unlocked mask that fixes the denominator) and the `extLst` block where the 19 `x14` validations live; XML hardening | Spreadsheet semantics — formulas, style resolution, shared-formula groups are all our code | BSD (SECONDARY). No obligation for a hosted commercial product | Minimal | stdlib `xml.etree` with manual namespaces; a 5× slowdown on a 28 ms parse is survivable |
| **`openpyxl` 3.1.5** | Two things: formula text with correct shared-formula row-shifting, and cached values (present on 505 of 505 formula cells). Offline: writing mutant workbooks | **Hard rule with a test:** schema derivation, validations, defined names as authority, and **re-serialising the artifact anywhere**. Round-trip destroys **98.2% of bytes (3,663,391 → 65,877)** and every `x14` validation — **if the pipeline ever re-serialises, the hash we attest is a hash of something that is not the filing** | MIT (SECONDARY). Clean | Low — it is the ecosystem default, which is why its blind spot is our best demo material: the failure is not ours and needs no defence | ~80 lines of `si`→master translation over lxml. **Mutation-test it first; the row-shift is the part that silently goes wrong** |
| **`celpy`** | Evaluating the admitted CEL subset under a step-count budget | Anything outside the admitted grammar: nested comprehensions, `filter()` outside `witness`, `map()` outside `sum()`, protobuf, `bytes`, `uint`, `type()`, `dyn()`, excluded by an AST walker at admission. **Nested comprehensions are the only route to exponential blow-up the CEL spec names** | Apache-2.0 (SECONDARY). Clean, patent grant included | Moderate and named. **Publishes no CEL conformance claim (NOT-FOUND on its repo page)**, and our absorption guard depends on error semantics | `cel-expr-python`, which wraps the official CEL C++ and inherits conformance, at the cost of a C++ build. **Run the conformance suite against both and record which one the registry root was qualified against** |
| **`SQLite`** | Registry, run manifests, run rows, template records, snapshot index, watch log — one hashable file | Blob storage: blobs are files, so anyone can diff, rsync and hash them without our code | Public domain (SECONDARY). No obligation of any kind | None worth modelling | Postgres on the named trigger; §4.2 is portable SQL for exactly that — no SQLite-only types, no `WITHOUT ROWID`, no JSON1 dependency |
| **`FastAPI`** | ~18 paths, one SSE surface, generated OpenAPI | Background work, scheduling, orchestration | MIT (SECONDARY) | Low | Litestar — a mechanical port; nothing in the domain layer touches the framework |
| **`Z3`** | **The proof arm of gate G3 only**; its model is the non-degeneracy witness and enters the library as evidence | Evaluating predicates against filings — that would put a potentially non-terminating tool into a terminating pipeline | **MIT (SECONDARY — the LICENSE was not opened by any lane). Open it before shipping** | Low | The empirical control arm, which runs regardless. **Losing Z3 costs the proof and the witness, not the gate** |
| **`Hypothesis`** | Driving the relation set; every real defect pinned as an `@example` | **Generating relations.** It generates *inputs*, never *properties* | **Reported MPL-2.0 — SECONDARY, LICENSE not re-read. Read it before adoption**; file-level copyleft would be acceptable unmodified | Low | ~150 lines of hand-rolled transformation loops; the necessary/expected split then becomes our convention rather than the library's enforcement — a real loss, so put it in a test |
| **`pandera`** | Host functions for bulk column checks (`failure_cases` gives row-level provenance free) | The predicate language, the verdict model, anything needing a third value | MIT (SECONDARY; version VERIFIED-AT-SOURCE via PyPI JSON, release date **UNVERIFIED**) | Low | Trivial — a few dozen lines per host function |
| **in-toto Statement / DSSE** | The attestation envelope and the `DISALLOW *` closed-world principle | Build-pipeline semantics. **Its standard `test-result` predicate has `passedTests[]`, `warnedTests[]`, `failedTests[]` and no `skippedTests[]` — it cannot express a test that did not run**, which is why we define our own `predicateType` | **Apache-2.0 — VERIFIED-AT-SOURCE** (L10 opened the LICENSE and quotes it verbatim) | Low | **DSSE is a 40-line spec** (PAE + a signature); sign with `cryptography`'s Ed25519. **The envelope format is the asset; the tool is not** |
| **`Docling`** (offline) | The 102-page FM Regulations and 389 native-text circulars, with typed per-element provenance | **The filing.** All nine workbooks contain **zero embedded images** (`xl/media/` empty, 9 of 9, MEASURED) — no model touches the primary artifact. Also not clause identity | MIT (SECONDARY) | Low; IBM-backed | PaddleOCR-VL or Marker, at a documented cost; neither publishes an equivalent typed cell-level provenance contract. The corpus is static — a one-time re-parse is affordable |
| **`PaddleOCR-VL`** (offline) | The 10 of 399 scanned circulars | The 389 native-text ones | Apache-2.0 (SECONDARY) | Low | Any OCR, or carry `declared_gap: 10/399 sources unread` on every predicate resting on the full-text negative result |
| **`mutmut` 3.7.0** (offline) | Mutating **our own code**: host functions, schema inducer, CEL profile checker — where the silent failures live | Gate G2. **Our mutants are filings, not programs** | BSD-3 (SECONDARY); a dev tool, not a runtime dependency | Low, irrelevant | `cosmic-ray` (MIT). The comparative study favouring it was **not opened — UNVERIFIED** |
| **`crepes` / `MAPIE`** (gated) | Mondrian bookkeeping and the **`OnlineMartingaleTest`** — the instrument that makes the system **refuse to certify** when the population has drifted from the calibration set | **Anything on the workbook path.** MEASURED: **0 of 3,755 unlocked cells are ambiguous under the address key**; 154 (4.10%) under a header-anchored key. **There is no learning problem in the workbook** | BSD-3 both (SECONDARY). TorchCP (LGPL-3.0) rejected on that basis | Low | Split conformal is ~15 lines. **Non-negotiable rule that travels with them: the exchangeable unit is the FILING, not the cell** — report `n = F` beside every number |
| **`PuLP` + CBC** (offline) | Registry-minimisation ILP and the subsumption DAG, at admission | Anything at run time | PuLP MIT / CBC EPL-2.0 (SECONDARY); invoking the solver binary imposes nothing | Low | Greedy set cover with the same constraints, **reported as greedy** |
| **LibreOffice** (offline) | Third reader at template admission; second engine in the observability filter. **Pinned by container digest** | **The verdict path; the artifact we attest over; the normalising authority** | MPL-2.0 (SECONDARY); subprocess use imposes nothing | None | Our evaluator alone, with the observability filter reported as single-engine — a strictly weaker instrument, and the experiment report must say so |
| **`Daikon`** (offline) | Baseline B1; one row per filing, one column per stable key, `--conf_limit 0.99` | Production synthesis — its output goes through the identical gate as a model's | MIT-equivalent (SECONDARY — licence text not opened) | Low | None needed. **It earns its place because it emits trivia — in one published study 27 of 40 correct invariants were "pointer not null" — and the trivia *is* the degeneracy list** |
| **`cosign`** | DSSE construction and Ed25519 signing in **keyed mode** | Keyless signing; **never** the transparency log (`--tlog-upload=false` asserted in a test) | Apache-2.0 — **SECONDARY**; its LICENSE was not opened (the in-toto LICENSE that *was* opened is a different repository) | Low | `cryptography` Ed25519 + 40 lines of DSSE |

**The projects whose licence is not established, named plainly.** **gVisor — NOT-FOUND**, and it is the
parser sandbox; the fallback is plain `seccomp` + namespaces, a weaker boundary that would have to be
disclosed. **Hypothesis — reported MPL-2.0, not re-read.** **`cobalt`/`indigo` — NOASSERTION**, so we
implement the URI grammar and adopt only Indigo's data model; **`bluebell` is GPL-3.0, VERIFIED, and must
never be linked.** Two more must be opened before the code ships: **Z3's**, and **`xbrl.us/dqc-license`** —
if the latter is permissive, the XBRL US DQC rule corpus is the only ready-made financial-filing
evaluation set found anywhere in this research.

---

## 3. THE BACKEND FLOW

Two clocks. The **online** path runs per filing and makes **no model call**. The **offline** paths run per
template version, per regulation version, or on a change signal. The relation layer is **a loop over the
online path on transformed inputs, not a stage after it**, and relations route **through** the
qualification gate like any other predicate.

### 3.1 ONLINE — fifteen steps, F0 to F14

| Step | In → Out | Det. | Failure handling | Human | ⏱ | Status |
|---|---|---|---|---|---|---|
| **F0 RECEIPT** | bytes → `filing_sha256` over the **exact received bytes**, blob, `run` row | total | over the cap or non-zip → `413`/`415`, **no run row**. There is no partial run | no | ~10 ms D | BUILT |
| **F1 CONTAINER GUARD** | digest → pass or `INVALID` | total | zip entry count, per-entry uncompressed size, total ratio, media types, required parts — **all before any XML is parsed**. Any trip → `INVALID` with the **run-level** cause `invalid.container_guard_tripped` (see §III.4.4.1 — run-level causes are a separate closed vocabulary from the item-level 8 × 30, because a guard trip is not a property of any cell). **Not a FAIL: a filing we could not safely open is not a filing that failed a check** | triage | <5 ms D | SPECIFIED |
| **F2 DUAL-READER INGEST** | digest → `RawWorkbook` + extraction manifest | given pinned versions | A (lxml, structure) and B (openpyxl, formula text and cached values) are compared on `n_sheets`, `sheet_names`, `hidden_sheets`, `n_cells`, `n_formula_cells`, `n_validations`, `n_defined_names`, `merged_ranges`. **Disagreement on sheets, names or hidden state → `INVALID`** — the scope is not established. Elsewhere → those fields are marked and every predicate reading them returns `NOT_RUN(extractor_disagreement)`. **No third reader is called online** (§7 G12) | triage | ~230 ms M | PARTIALLY BUILT |
| **F3 TEMPLATE BINDING** | `RawWorkbook` → `template_sha256` + `TemplateSchema` | total | Binding is by **structural fingerprint** over `(sheet names + states, dimensions, merged-range set, defined-name list, unlocked mask)`. **Formula content is deliberately excluded** — otherwise a filer who overwrote a formula with a literal would fail to *bind*, and formula-override must surface as a **predicate failure**, not a binding error. No match → `INVALID` with `NOT_RUN(template_unbound)`, **which escalates**: it is also the signal that a new template version was published | **yes** — new version, superseded, or corrupt? | <1 ms D | SPECIFIED |
| **F4 FACT TABLE** | `RawWorkbook` + `TemplateSchema` → the two-document fact model | total | Two top-level names bound: `filing` and `template`. No clock, no network, no filesystem. **Vocabularies always resolve against `template`, never `filing`** — the `Dropdown` sheet is hidden **and the only unprotected sheet**, and sheet protection is an application flag anyway (**assume the filed artifact is fully mutable**). Every leaf carries `__cell__`. Money is scaled to `MILLI_USD_MILLION` here, once | no | 1 ms M | BUILT |
| **F5 ATTACHMENT EXTRACTION** | attachments + `stable_keys()` → `Fact{…, warrant = MODEL_EXTRACTED}` | **no — model-bearing** | **Skipped entirely when there are no attachments, which is normal; marginal model cost then exactly $0.00.** Three guards: (1) `key` typed `Literal[*L1_KEYS]`, so off-schema keys are *ungeneratable*; (2) post-hoc deterministic rejection — kept though redundant, **because this is the one you can prove to an auditor**; (3) conformal abstention (gated) — abstain unless the set is a singleton; an empty set maps to `INDETERMINATE(extraction_abstained)`. **Retry banned.** Model or network error → `NOT_RUN(source_unreadable)` | no at run time | seconds | SPECIFIED/GATED |
| **F6 PREDICATE SELECTION** | template digest + pinned registry root → `ACTIVE` / `PROVISIONAL` | total | A predicate qualified against a different template **is not evaluated**; its cells land in `NO_PREDICATE(not_yet_requalified)`. A `PROVISIONAL` predicate **still runs**, so detection is not lost, but its numbers are hidden and its cells are **not counted as settled**. An empty active set is not an error — it is an honest report with `settled.total = 0` | no | <1 ms D | SPECIFIED |
| **F7 PRE-FLIGHT** | declared `schema_keys` (machine-checked against the AST at admission, so exact and not an estimate) + fact table → `PROCEED` or `NOT_RUN(source_unreadable: <key>)` | total | **The structural mitigation for CEL's documented error absorption.** The spec says that for `&&`/`\|\|`, if one operand determines the result, an error in the other *"will be ignored"* — so `true \|\| <error>` yields `true`. Pre-flighting every declared key **before evaluation begins** makes the guard independent of how the predicate was written | no | sub-ms D | SPECIFIED |
| **F8 EVALUATION** | active set + fact table → one `run_check` row per predicate | total | The five-rule contract below, which lives in exactly one file, `EVALUATION-CONTRACT.md` (§7 G5) | no | sub-ms for 227 arithmetic predicates M | BUILT |
| **F9 RELATION PROBES** | fact table + admitted relations + pinned template → per relation `PASS`/`FAIL`/`INFORMATIONAL`/`OUT_OF_SCOPE` | total | **A loop over F4–F8 on transformed fact tables.** 25 relations, all oracle-free: 15 need the filing alone, 4 the versioned blank, 3 two consecutive filings, 1 multiple instances, 2 are checker self-tests never shown to the filer. Each carries a **degree map** (money = 1; counts, dates, ratios, categoricals = 0), a **necessary/expected flag**, and a **non-degeneracy precondition** — because an all-zero filing satisfies partition relations trivially. Violated *necessary* → FAIL with both value sets as witness; violated *expected* → `INFORMATIONAL` carrying the guidance note that makes the exception lawful | no at run time | ~160 ms D | SPECIFIED |
| **F10 SEEDED CANARIES** | each admitted predicate's stored `kill_case` + this filing's fact table → `canaries_passed`, or dead predicates and `INVALID` | total | Instantiate the fault each predicate is *known to detect* against **this filing's cells**, re-evaluate, confirm it fires. Catches parser drift, selector misses, renamed sheets, hidden-sheet truncation, encoding changes, empty-set vacuity — **for this file** | **yes on failure.** A silent canary is an engineering incident, not a filing outcome | ~35 ms D, from 7,946 mutants/s M | SPECIFIED |
| **F11 SETTLED FRACTION + CLOSURE** | every field-surface cell + every state → the settled-fraction object (§4.3) | total | The denominator is the **field surface** from `styles.xml` (`cellXfs → <protection locked="0"/>`) — **3,747 for the FME workbook (MEASURED, L14 §1.12)**. It is **computed twice by two independent readers and the run is `INVALID` if they disagree**, because when numerator and denominator come from one wrong parser the ratio is still plausible and the error is invisible by construction. A test asserts the denominator comes from the unlocked mask and **never from the predicate set** — that mistake was made twice in one afternoon by the person who knew about it. **A cell landing in no bucket aborts report generation** | no | <5 ms D | BUILT (denominator) / SPECIFIED (closure) |
| **F12 AGGREGATE VERDICT** | settled-fraction object + `pervasiveness-policy-v1.json` → one verdict state | total | `residueIsConfined := (unsettled cells touch ≤ K sheets) AND (no unsettled cell is material-by-policy) AND (unsettled/inScope ≤ T)`. **`K` and `T` render `PLACEHOLDER` until the argument that sets them exists** (§7). 2×2: failures × confined → `EXCEPTIONS_NOTED`; failures × pervasive → `ADVERSE`; none × confined → `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`; none × pervasive → `SETTLEMENT_INSUFFICIENT`. **No state's name means "clean"** | no | <1 ms D | SPECIFIED |
| **F13 REPORT + ATTESTATION + LOG** | → `report.html` (self-contained, opens from `file://`, no green tick), `attestation.json`, `run.jsonl`, plus **declared-lossy** OSCAL AR / POA&M / RO-Crate projections | total | The manifest is embedded in the report footer where a human can read it. **A closure violation or a no-green-tick gate failure aborts report generation. There is no degraded report** | no | ~20 ms D | PARTIALLY BUILT |
| **F14 `verify`** | report or attestation + the blobs it names → `REPRODUCED` + byte comparison, or a diff | total | Re-runs the pipeline from the embedded manifest at the pinned registry root, template, register snapshot and tool versions. **The programme's acceptance test: a third party clones the repo, runs `verify` on another machine, and gets a byte-identical re-derivation. If it does not reproduce, it does not ship** | no | = full pipeline | SPECIFIED |

**F8 — the evaluation contract, corrected. The word `UNCHECKED` appears nowhere in it**; it was a state
the vocabulary retired and the drafts kept quoting.

```
1.  Evaluate P.applicable
      error -> NOT_RUN(not_run.source_unreadable)        [never FAIL, never PASS]
      false -> OUT_OF_SCOPE(P.reason_if_inapplicable)    [never PASS]
      true  -> continue
2.  Pre-flight (F7) already ran; any missing/mistyped declared key ->
      NOT_RUN(not_run.source_unreadable: <key>) and expr is never evaluated.
3.  Evaluate P.expr under a step budget and a wall-clock kill
      budget exceeded -> NOT_RUN(not_run.budget_exhausted)         [never FAIL]
      runtime error   -> ERROR(error.predicate_raised), run := INVALID
                         -- a predicate that RAISED is an apparatus failure, not an
                            unreadable source; NOT_RUN(source_unreadable) is reserved
                            for inputs we could not read
      false -> FAIL, then evaluate P.witness for the cell list
      true  -> PASS
4.  Provenance composes by WEAKEST INPUT:
      warrant := min over every fact the AST read, DETERMINISTIC > MODEL_EXTRACTED > DERIVED
      retrieved_at := max over inputs
      -- never fresher than its stalest input, never stronger than its weakest.
5.  cells_bound == 0 -> ERROR(error.cells_bound_zero), run := INVALID
      -- binding to nothing is never a PASS.  Demoting this to NOT_RUN would put the
         vacuous-pass failure mode in the same bucket as a rate-limited register.
```

**Rule 3 is the whole product in four lines**: everywhere a conventional framework turns doubt into a
failure (`success = False`) or into silence, this turns it into a counted, reasoned, reported
non-settlement. **Rule 5 kills the four likeliest silent failures at once** — vacuous pass (`all([])` is
`True`), empty-set arithmetic, selector drift, scope truncation.

**Three run states.** `VALID`: the pipeline ran, the checker demonstrated liveness on this artifact, and
closure holds. `INVALID`: **the system could not demonstrate it was working here** — set by an F1 guard
trip, F2 structural disagreement, F3 unbound template, F8 `cells_bound == 0`, F8 predicate raised, F10
silent canary, F11 closure violation or denominator disagreement. `REJECTED`: the submission never became
a run. **An `INVALID` run renders a report that states why and carries no settled fraction at all**; the
verdict is `null`, not `SETTLEMENT_INSUFFICIENT`, because the latter is a finding about the filing and
this is a finding about us.

**What F10 claims, at full strength.** *No assurance artifact in existence carries evidence that the
instrument that produced it was working on the specific document it examined. A clean audit opinion does
not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict unless every check
has just demonstrated, on your file, that it can still catch the fault it was admitted for.* That is
falsifiable, claims no novelty for the mechanism (two extra executions per predicate), and needs no
citation.

### 3.2 OFFLINE A — template admission and predicate harvest

**T1 Fetch** the published URL → bytes + `template_sha256` + timestamp and origin URI; **a changed hash at
an unchanged URL is a version event, not an error**. **T2 Triple-read** — as F2 *plus* the digest-pinned
LibreOffice reader, available here because this path is offline; **any structural disagreement blocks
admission**. **T3 Induce schema** (deterministic, **28–44 ms MEASURED**) → `TemplateSchema{formulas 505,
validations 54, vocabularies 15, unlocked_mask, field_surface 3747, stable_keys, carry_table 195 edges}`;
a construct not understood is recorded in the manifest and its fields are excluded from `in_scope` **with
a stated reason**, never silently dropped. **T4 Harvest** → **280 executable predicates for the FME
workbook, zero model involvement (MEASURED, L14 §1.9)**: `cross_sheet_equality` 181, `sum_identity` 35,
`membership` 20, `numeric_bound` 13, `integer_bound` 11, `same_sheet_equality` 11, `date_bound` 6,
`tally_identity` 3, `conditional_required` 0. This step cannot fail, only under-produce. **T5
Function-vocabulary check** — an unimplemented function makes those cells `NOT_RUN(source_unreadable)`, or
the pinned second engine is promoted for this template and its disagreement rate published; **a human
decides**. **T6 Stable keys** `= (sheet_name, merged_header_path, row_label)`, coordinates a *resolved
attribute*; an unresolvable key enters `UNRESOLVED` and **blocks** its predicates rather than silently
binding to the wrong cell. **T7 Register** — **a human signs the admission, because this fixes the
denominator every subsequent number is a fraction of.**

**Why T4's 20 membership predicates matter more than their count:** they take the workbook from **3
enforced controlled vocabularies to 20** with no model at all, and one of them — `'3. Portfolio'`
instrument-type over `I116:I126` and `M116:M126` — covers **210 cells with a two-value vocabulary**. *The
check was already latent in the artifact; nobody had extracted it.*

### 3.3 OFFLINE B — clause-graph induction (L1b)

389 native-text circulars → Docling; 10 scanned → PaddleOCR-VL, frozen once and content-addressed; both
into a **deterministic promoter** (numbered headings → `<section>`; `(1)/(a)/(i)` → nested `<paragraph>`;
"Provided that" → `<proviso>`) → Akoma Ntoso with `eId` per clause and an FRBR URI per instrument, plus a
dated cross-reference extractor and an amendment graph. Recall is checked against a declared denominator —
the measured **8,866 `shall` occurrences across 361 circulars**; a promoter that loses `shall` clauses is
losing obligations and the count is the regression test. **90 of 389 circulars amend an earlier
instrument; 76 of 82 amending circulars cite a resolvable target (92.7%, MEASURED).** An unpromotable
region is recorded with its page span and every obligation inside it is `NO_PREDICATE(rule_ambiguous)`
until a human promotes it. **Status: SPECIFIED. Nothing of L1b is built** — which is why the obligation
table is hand-maintained on day one (§4.2).

### 3.4 OFFLINE C — candidate proposal

**The rename is substantive:** this is candidate *proposal*; the gate is *admission*. Every measured system
in this literature that works, works because a rejector exists; every one that fails, fails because the
rejector was absent or fake. **The gate is the rejector and it is the actual product.** In: the
`TemplateSchema` as an explicit I/O constraint, the clause unit with its `eId` and FRBR URI, and the
template's own 505 formulas as an **available** criterion source. Out: candidates in the envelope format,
each carrying its clause locator, exact character span, an enumeration of every proviso in that span, and
a rationale. Model: `claude-opus-5`, Batch, cached prefix, offline, once per template version, never in a
request path. **Determinism: none, and it does not need any** — a weaker model proposes more rejects; it
cannot smuggle an unqualified predicate past a gate that requires a measured kill rate and a measured FFR.
A malformed candidate is discarded and counted: **the discard pile is data** and appears in the attrition
funnel.

**The I/O-constraint intervention, corrected.** Feeding an induced schema in as an explicit I/O constraint
is the dominant lever on **structural similarity (+37–54 percentage points)** in the only published study
of statute→executable-model generation (arXiv:2604.17153, VERIFIED-AT-SOURCE via L04 §2.13); **that
study's *outcome* equivalence tops out at 51–53%**, and its own caveat is that structural similarity does
not guarantee outcome equivalence, or the reverse.

**And the criterion-source claim, restored.** SPADE infers what correctness meant from the traces of a
developer changing their mind, because in a software pipeline nothing else records it. **We do not have to
infer it: the criterion is a published instrument with a version, an amendment chain machine-followable in
76 of 82 cases, and a blank template with a content hash.** It is not more *authoritative* than SPADE's —
the regulator's own template computes a scheme total that misses two of its own nine legal values — it is
**citable, versionable and watchable**, which is precisely what lets a predicate be tied to a clause,
re-qualified when the clause moves, and quarantined the day a circular changes the rule. §3.6 implements
it, and no draft stated it as a contribution.

### 3.5 OFFLINE D — qualification. **Five gates, in this order**

`G0 (free) → G1 (free) → G3 proof arm (cheap) → G2 (expensive) → G3 empirical arm → G4.` Nothing expensive
runs behind something free, and a predicate Z3 proves unfalsifiable never consumes a mutation budget.

- **G0 scope faithfulness.** The candidate carries the exact character span of the clause it implements,
  `source.find(quote)` succeeds deterministically, and every proviso, exception and cross-reference in that
  span is **either implemented by a branch or emitted as `NO_PREDICATE(no_predicate.not_yet_synthesised)`
  carrying the proviso's verbatim text and character span**, with `provisos_declared` recorded. Neither ⇒
  reject. Models ground spans well (SpanFaith 0.77–0.79) and wire exception structure badly (Edge-F1 ≈
  0.22), and our instrument is full of provisos — **reg 51(1) ends "in such manner as specified by the
  Authority"**, a live delegation hook.
- **G1 executes and binds.** Runs without error, every key exists in the induced schema, **`cells_bound >
  0`**. Nearly free and proves nothing alone — which is exactly why it is separate. **It is the condition
  whose absence produces the vacuous pass.**
- **G3 proof arm.** Z3 as above; `unknown` is **unproven, never "non-degenerate"**.
- **G2 seeded-defect kill.** `KR = K/O` over mutants **verified observable by recalculation**, plus the
  per-fault-class vector and `UR = U/G`. Seeding targets the fields `schema_keys` reads **plus a 10%
  control sample of fields it does not** — without the control arm a flag-everything predicate scores
  perfectly. Mutants are made by **raw-zip surgery** (copy every part byte-for-byte, rewrite one worksheet
  XML; MEASURED: one part differs, the 3.55 MB data model and all 19 `x14` validations survive
  byte-identical). The **observability filter** decides whether a kill rate means anything: recalculate,
  diff the value grid, **discard mutants no cell value distinguishes**. Expected discard is high —
  **3,512 of 7,500 (46.8%)** on a comparable operator suite — **and we report our own figure every run,
  because it is a property of our operator mix and must not be assumed.**
- **G3 empirical arm.** Spurious firing on the control sample below threshold; flags ≤ 50% of the clean
  corpus; not equivalent to a published degeneracy-list member. SPADE's own paper: taking every candidate
  yields 100% settled at 100% FFR.
- **G4 false-failure rate.** `FFR ≤ 0.10` with `n`, a Wilson interval, `corpus_provenance ≠
  SELF-AUTHORED`, a structurally distinct held-out slice reported separately, and the **marginal** FFR
  under `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`. In two of SPADE's nine pipelines, assertions
  that each individually met the budget composed to **88%** and **53%**.

**Two thresholds, and they are different tests — the drafts stated them as one.** The settling experiment
asks *"can this candidate fire at all, and does it beat the free baselines"* — `K/O > 0` plus marginal
kill strictly greater than `B0 ∪ B1 ∪ B2`. **The registry admits at `K/O ≥ 0.80` on the fault classes the
predicate claims to cover.** Both are stated; the two attrition numbers are reported separately.

**FFR corpora, ranked; every FFR carries which one produced it.** `BLIND-FILLED` (Person A fills from
template and regulation only, never having seen the predicate set; Person B authors predicates never
having seen A's workbooks) — **an FFR that *can* be non-zero, therefore one that carries information, and
the minimum bar below which no FFR may be printed anywhere in the product**. `TEMPLATE-COMPUTED` — fill
the inputs and let the workbook's own 505 formula cells compute the rest; **a predicate that fires on a
cell IFSCA's own artifact computed is a genuine false failure, because the regulator authored the ground
truth**; ready today. `REGISTER-DERIVED` — **MEASURED**. `REAL-PARTNER` — needs a partner we do not have;
`n` will be tiny and that is fine if reported as an interval. `SELF-AUTHORED` — **renders as `—` and the
word `uninformative`. Not a number. The schema forbids it.**

**What `REGISTER-DERIVED` licenses, precisely.** Every entity in the register is validly registered, **so a
predicate asserting *membership* cannot have a true positive there** — the register licenses an FFR for
the membership predicate only. A predicate asserting *format* can: the regex any competent engineer would
write after five examples, `^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$`, **fires on 87 of 228 live FMEs — a
38.2% false-failure rate, MEASURED, denominator 228 live FMEs resolved via the detail endpoint, 10 Aug
2026 (L08 §C.3)**. Two incompatible identifier schemes are live in the same register on the same day (141
legacy, 84 new, 3 neither), and one of the three carries a `U+2011 NON-BREAKING HYPHEN` homoglyph —
visually identical, byte-wise different, invisible in any screenshot. **The admitted predicate is
therefore set membership against a snapshotted register under a declared normalisation (NFKC, `U+2011 →
U+002D`, strip, case-fold), never a format grammar.**

**And the design's own sentence must be corrected.** *"A check whose error rate is unknown is not admitted
— which makes the coverage claim true by construction"* becomes: **the settled-fraction claim is true to
the extent the admission measurements are valid, and each predicate carries the provenance of its own
measurement.** Longer, weaker, defensible.

### 3.6 OFFLINE E, F, G — admission, re-qualification, and the watcher that quarantines a moved clause

**Admission (R1–R7).** R1: the AST walker enforces the grammar and **verifies `schema_keys` against the
AST both ways** — a predicate reading an undeclared key, or declaring one it does not read, is rejected;
**this is what makes the settled fraction computable rather than estimated**. R2: host-function references
checked against the closed registry. R3: the ILP selects a minimal set; the Z3 subsumption DAG removes
implied predicates. R4: **liveness witnesses stored with the predicate** — a `kill_case` (a mutant it is
known to reject) and a `pass_case`; F10 replays the `kill_case` on every filing. R5: append-only;
supersession is a new row. R6: the **registry root** — a Merkle tree over sorted `code_sha256`, leaf
`sha256(0x00 ‖ h)`, internal `sha256(0x01 ‖ l ‖ r)`, odd node promoted; **domain separation is not
decoration**. R7: **a human signs the batch** — the gate is mechanical, shipping a check that will be
applied to a regulated filing is not. **A predicate whose `qualification` block is absent does not load**,
and a test attempts the admission and asserts the rejection. Every rejection records the gate, the measured
number, the cells it would have covered and the obligation it claimed — that record *is*
`no_predicate.failed_qualification` and the `counterEvidence` array. **We were going to discard exactly
the information an audit-documentation standard makes mandatory.**

**Re-qualification is live, not hypothetical.** The FME workbook is dated 02 Jan 2026; the FM Regulations
are consolidated as amended to 30 Jan 2026; and the **29th IFSCA Authority Meeting of 24 Jul 2026**
decided that NAV periodicity for close-ended Restricted Schemes *"may be enhanced by the FME from
semi-annual to annual, subject to prior approval of at least 75% of the investors in the scheme by value
of their investments"* (VERIFIED-AT-SOURCE). The owed frequency now depends on **a fact the workbook does
not collect**. The predicate neither errors nor abstains — it keeps computing a date difference against a
rule that no longer exists: **a filer who lawfully moved to annual gets a false failure; a filer who moved
without approval gets a silent pass. Both outputs are clean, confident and well-formed.**

Seven rules. (1) **Keys are label-anchored, never coordinate-anchored**; a version bump is a
re-resolution, not a rewrite. (2) Every predicate carries a `qualified_against` record **as part of its
identity** — template digest and label, regulation version, circular snapshot, count of unreadable
circulars, corpus id and provenance, `n`, harness and evaluator versions, and for proposed predicates the
model id, date and prompt hash, **so a re-synthesis under a drifted model is a diff and not a mystery**.
(3) Any change to any element moves the predicate to `PROVISIONAL`: it still runs, its numbers are hidden,
and it does not count in the settled numerator. (4) **Therefore the settled fraction falls when the world
moves**, and the chart must be able to step down — **the step-downs are the most credible thing on it,
because they are the only evidence the system notices when the world moves**. (5) Liveness witnesses are
re-run on every version change and every filing; a predicate whose `kill_case` no longer dies is
quarantined automatically — **but this alone cannot catch a rule change**, because the mutant and the
predicate move together, which is why rule 6 exists. (6) **Watch the instrument stream, not just the
instrument**: a daily content-hash of the circular list, Authority-meeting page and download page, diffed
against the last snapshot; any new instrument citing a regulation a predicate claims to implement puts
that predicate into `PROVISIONAL` **automatically and pessimistically**, only a human clears it, and **the
watcher never re-admits**. A fetch failure is recorded as **a gap in the watch log with its duration**,
never as "no change" — an unobserved day is not a quiet day. This is diff-and-flag, not NLP, and **it is
the only mechanism that would have caught 24 Jul 2026**. (7) Carry the 10 unreadable circulars as a
permanent declared gap — or OCR them, which is an afternoon.

**One version event is already on the calendar:** `Dropdown!$E$3:$E$6 = {2025-26, 2026-27, 2027-28,
2028-29}`. **The workbook cannot express FY2029-30.**

### 3.7 OFFLINE H — the residue set

Take the filing `F`; generate mutants under a declared, versioned fault model; adjudicate each INNOCUOUS
or WRONG (**the only human step**); run the full admitted predicate set and all admitted relations over
every WRONG mutant; `RESIDUE := {WRONG mutants nothing rejects}`; report `|RESIDUE|` and each survivor's
class of falsehood. **It cannot be inflated by boring checks** — adding 505 recompute predicates does not
shrink it, because the residue is populated by falsehoods consistent with every arithmetic relation in the
file. It **makes 100% structurally unreachable**, because the count is never zero and it is a permanent
row in the denominator. It is **reproducible given the published fault model *and the published
adjudication record*, both content-addressed.**

**The class it names, at full strength.** A prescribed return is a closed arithmetic system. **We can
construct, and exhibit, a family of filings that are internally perfect under every relation the
regulator's own template encodes and every relation we have added — and materially false.** In code
mutation testing a mutant that changes behaviour is in principle killable by *some* test; here a mutant
can change the **truth** of the artifact and be **provably unkillable by any predicate over the artifact
alone**. That family is non-empty by construction, its size is measurable, and measuring it is the first
quantitative statement anyone has made about the limit of document-level verification for a regulated
filing. It follows that *"the residue set comes back empty"* is not a Low risk; **it is structurally
impossible.**

### 3.8 Where a human is required

Template admission sign-off (fixes the denominator); the function-vocabulary decision; promoter failures
and the 6 of 82 unresolved amendment chains; **host-function authoring — added only by a human, never
generated by a model**; relation authoring; **blind-fill corpus construction, which is both the
measurement and the expensive input**; the admission batch signature; clearing a `PROVISIONAL` flag;
INNOCUOUS/WRONG adjudication; `INVALID` triage; override entry (both states retained, inside the signed
payload; the override count is reported separately — a downstream reviewer will want it); and the
pre-registered go/no-go on candidate proposal, **recorded on the date it was taken, whichever way it
goes**. **Nowhere here does a human adjudicate a PASS. The verdict itself is never negotiated.**

---

## 4. THE DATA MODEL

### 4.1 Content addressing

`sha256` over exact bytes, lowercase hex, at `blobs/sha256/<aa>/<remaining-62>`. No compression, no
re-encoding, no normalisation: **the bytes we hash are the bytes we received.** Canonical serialisation
for every hashed JSON object is **RFC 8785**, stated explicitly because *"the sha256 of the JSON"* is not
a definition and two implementations that disagree on key order produce two roots for one registry.
Content-addressed and named in the run manifest: the filing; **each worksheet inside it**, so a
re-derivation can say *which sheet* changed; the blank template; the `TemplateSchema`; each predicate,
host function (source + test-vector result) and relation; the registry root; each regulation PDF; the
**register snapshot** (the register is mutable and undated — a verdict citing "the register" without a
snapshot hash is not reproducible and cannot be signed); each mutant; the per-template engine-disagreement
set; and the report.

### 4.2 Tables — and the decision that the unit is the cell

**DECIDED.** The unit of the denominator, of closure and of the settled fraction is the **filer-editable
cell**; `obligation` becomes a **predicate attribute**, not a denominator axis. It beat the
`(field × obligation)` pair on one fact: every measurement in this corpus is a cell count (**2,373 settled
of a 3,747-cell field surface, MEASURED, L14 §1.12**), while the pair model has no published enumeration
rule anywhere — the drafts' figures came from an illustrative JSON block that never claimed to be a
measurement. **Consequently no total over obligations and no total over pairs appears in this
specification, in any schema or in any example.** Obligation identity comes from a hand-maintained
`obligation` table (`source='hand'`) because nothing of L1b is built; it flips to `source='l1b'` the day
the clause graph produces `eId`s. Two run tables follow, and the split is what makes closure one SQL
statement.

```sql
blob(sha256 PK, n_bytes, media_type, first_seen_at, origin_uri, retrieved_at)
template(template_sha256 PK, label, published_at, fetched_at, origin_uri,
         structural_fingerprint, admitted_at, admitted_by, superseded_by NULL)
template_sheet(template_sha256 FK, sheet_index, sheet_name, sheet_state, sheet_sha256,
               protected, dimension, PRIMARY KEY(template_sha256, sheet_index))
field(template_sha256 FK, stable_key, sheet_name, merged_header_path, row_label, resolved_ref,
      dtype, unit,                 -- MILLI_USD_MILLION | COUNT | DATE | TEXT | ENUM
      is_unlocked, is_formula, in_field_surface,
      resolution_state,            -- RESOLVED | UNRESOLVED
      PRIMARY KEY(template_sha256, stable_key))
vocabulary(template_sha256 FK, vocab_key, source_ref, terms_json, term_count, wired_by_validation)
validation(template_sha256 FK, seq, namespace,      -- 'main' | 'x14'
           type, sqref, formula1, resolved_vocab_key NULL, cell_count)
carry_edge(template_sha256 FK, src_ref, dst_ref, formula_text, encoding)
           -- TEXT | SHARED_MASTER | SHARED_DEPENDENT | ARRAY
engine_disagreement(template_sha256 FK, cell_ref, our_value, lo_value, lo_container_digest,
                    measured_at, PRIMARY KEY(template_sha256, cell_ref))
           -- computed OFFLINE; the online path reads this table, never LibreOffice

instrument(frbr_uri PK, title, as_at, pdf_sha256, page_count, promoter_version)
clause(frbr_uri FK, eId, text, page_no, bbox_json, charspan_json, provisos_json, xrefs_json,
       PRIMARY KEY(frbr_uri, eId))
amendment(source_frbr_uri, target_frbr_uri, target_eId, effective_date, resolved BOOLEAN)
obligation(obligation_id PK, frbr_uri NULL, eId NULL, quote, span_json, source)  -- 'hand' | 'l1b'

predicate(predicate_id, version, PRIMARY KEY(predicate_id, version),
          kind,                    -- harvested | proposed | hand_authored | relation
          template_sha256, obligation_id NULL, clause_span_json NULL,
          envelope_json, code_sha256, schema_keys_json, host_fns_json,
          state,                   -- ACTIVE | PROVISIONAL | QUARANTINED | WITHDRAWN
          severity_tier,           -- BLOCKING | ADVISORY, set by measured FFR (§7 G2)
          admitted_at, admitted_by, superseded_by NULL)
qualification(predicate_id, version, PRIMARY KEY(predicate_id, version),
  g0_scope_faithful, g0_provisos_declared, g0_provisos_implemented,
  g1_executes, g1_cells_bound,
  g2_killed, g2_observable, g2_generated, g2_unobservable, g2_unreachable,
  g2_by_fault_class_json, fault_model_version, harness_version,
  g3_method,          -- z3 | empirical | both
  g3_verdict,         -- non_degenerate | trivially_true | always_flag | unknown
  g3_witness_sha256 NULL, g3_control_arm_spurious,
  g4_fired, g4_n, g4_wilson_lo, g4_wilson_hi, g4_corpus_id,
  g4_corpus_provenance,  -- SELF-AUTHORED | BLIND-FILLED | TEMPLATE-COMPUTED
                         -- | REGISTER-DERIVED | REAL-PARTNER | PUBLIC
  g4_heldout_fired NULL, g4_heldout_n NULL, g4_marginal_ffr NULL, g4_conditioned_on_json NULL,
  kill_case_sha256, pass_case_sha256, qualified_against_json, qualified_at)
-- INVARIANT enforced by the loader: a predicate row with no qualification row DOES NOT LOAD.
rejection(candidate_sha256 PK, predicate_id NULL, obligation_id, rejecting_gate,
          measured_json, cells_would_have_covered, rejected_at)
host_function(name, version, PRIMARY KEY(name, version), source_sha256, signature,
              returns_tristate, test_vector_sha256, mutation_score_json, authored_by)
registry_root(root PK, computed_at, n_predicates, predicate_ids_json)

run(run_id PK, filing_sha256, template_sha256, registry_root, register_snapshot_sha256 NULL,
    run_state,               -- VALID | INVALID | REJECTED
    aggregate_verdict NULL,  -- EXCEPTIONS_NOTED | ADVERSE
                             -- | EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE | SETTLEMENT_INSUFFICIENT
    invalid_reason NULL, canaries_run, canaries_passed,
    started_at, finished_at, manifest_json, report_sha256, attestation_sha256)
run_check(run_id FK, predicate_id, predicate_version,
          state,        -- 8 values, §4.4
          reason_code,  -- 30 values; REQUIRED iff state not in (PASS, FAIL)
          method,       -- RECOMPUTE | TIE_OUT | SCHEMA_BIND | TEMPLATE_DIFF | REGISTER_LOOKUP
                        -- | CLAUSE_TEST | DIFFERENTIAL | MODEL_EXTRACT | UNKNOWN     (nine)
          warrant,      -- DETERMINISTIC | MODEL_EXTRACTED | DERIVED  (composes by weakest input)
          provenance,   -- COMPUTED | DECLARED
          cells_bound, witness_json NULL, elapsed_us,
          PRIMARY KEY(run_id, predicate_id))
-- CONSTRAINT: method='MODEL_EXTRACT' AND state='PASS' is rejected at write time.
run_cell(run_id FK, stable_key, state, reason_code NULL, settled_by_predicate_id NULL,
         PRIMARY KEY(run_id, stable_key))
-- materialised for EVERY field-surface cell before evaluation, defaulting to
-- NO_PREDICATE(not_yet_synthesised).  Closure is one GROUP BY over this table.
override(run_id FK, stable_key, old_state, new_state, remark, actor_id, decided_at, evidence_sha256)
extraction_manifest(run_id FK, reader, parts_read_json, parts_skipped_json, namespaces_json,
                    constructs_not_understood_json, agreement_json)
register_snapshot(snapshot_sha256 PK, endpoint, fetched_at, n_records, n_requests,
                  list_response_sha256, detail_response_shas_json)
instrument_watch(observed_at PK, endpoint, content_sha256, changed, gap_since NULL,
                 predicates_flagged_json)
```

**The cell roll-up rule, stated once so ambiguity cannot re-enter.** Scope is determined first: a cell is
`OUT_OF_SCOPE` only if a scope rule with a **machine-checkable pointer to the schema condition** makes it
inapplicable, or a named run profile excludes it (and the profile digest is recorded). For every in-scope
cell the state is the maximum over the predicates that read it under
`ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`, with
`settled_by_predicate_id` naming the producer. `NO_PREDICATE` is not in the order: it is the state of a
cell whose evaluation set is empty.

> **RESOLVED (owner decision, 10 Aug 2026 — this was the audit's one blocking contradiction).** An
> earlier draft of this section ordered `PASS ≻ INDETERMINATE ≻ NOT_RUN` and concluded that *"a cell read
> by one passing and one not-run predicate is settled."* **That is withdrawn.** The order above is
> normative, it is §II.3.1's, and under it **a cell is clean only if every predicate binding it passed** —
> one `NOT_RUN` makes the cell unsettled no matter how many other predicates passed.
>
> *Why the other order could not stand:* both §II and §3.1 F2 state that when the two readers disagree on
> a field, every predicate reading it returns `NOT_RUN(extractor_disagreement)` and **"the settled fraction
> falls, it does not silently succeed."** Under `PASS ≻ NOT_RUN` that sentence is false in exactly the case
> it was written for — a passing predicate would absorb the un-run one and the fraction would hold. A check
> that did not run must never be absorbed by one that did. That is the product.
>
> *What it changes, and what it does not.* It changes the **runtime** settled count, which can now be lower
> than the static figure — which is the intended behaviour, not a defect. It does **not** change the
> harvest figure **2,373 of 3,747**: that is a static count of cells reachable by at least one harvested
> predicate, computed before any evaluation, and it is unaffected by roll-up precedence.

The not-run predicate remains visible in `run_check`: the two tables answer two different questions and
neither is derivable from the other alone.

### 4.3 The settled-fraction object — never a bare fraction

```jsonc
"settledFraction": {
  "denominator": { "source": "induced-from-template-unlocked-mask",   // NOT negotiated
                   "generatorRule": "v3", "fieldSurface": 3747, "computedTwiceAgreed": true },
  "outOfScope": 214, "informational": 38,     // both removed from the denominator
  "inScope": 3495,                            // <- THE denominator
  "settled":   { "pass": 2361, "fail": 12, "total": 2373 },
  "unsettled": { "indeterminate": 41, "notRun": 88, "noPredicate": 993, "error": 0 },
  "fraction": 0.6789,                         // meaningless without the six counts above
  "residue": { "survivors": 12, "faultModel": "v3", "adjudicationRecord": "sha256:…" },
  "declaredGaps": [ { "kind": "unread-sources", "detail": "10 of 399 circulars are scanned images" } ],
  "denominatorWarning": "Out-of-scope determinations are filing-specific, so the denominator varies
     between filings. Settled fractions are not directly comparable across filings."
}
```

*(A schema example on a hypothetical filing, not a measurement. The measured triple for the published FME
blank filled clean is **2,373 settled / 1,374 unchecked / 3,747 field surface**, MEASURED, L14 §1.12.)*

**The most important scoring decision in the design.** XCCDF removes `notchecked` from its denominator; **we
keep `noPredicate` in.** XCCDF's denominator is a benchmark a human authored, so "no check exists" means
the author chose not to have one. **Ours is induced from the regulator's own template, so "no predicate
exists" is a gap in *us*, not in the specification** — and removing it would let the fraction rise by doing
nothing. **Absent ≠ empty ≠ zero:** `[]` = *we determined there are none*; `null` = *we make no claim*; an
omitted field is a schema violation. **For an unprotected template there is no unlocked mask**, so
`settledFraction: null` and `denominator.source: "not derivable — template ships no protection mask"`;
**two of the nine prescribed workbooks are in this state.** The settled fraction is a **per-template
property and must never be averaged across templates.**

**And the number ships with the sentence that makes it honest.** 280 predicates are mechanically derivable
from the regulator's blank template with no model, and they touch 2,373 of 3,747 filer-editable cells
(MEASURED). **None of them is admitted yet**, because no false-failure rate has been measured for any of
them on a corpus we did not write — so under this specification's own admission rule the currently
admissible set is empty and the currently defensible settled fraction is 0%. **That is the point: the
number you are looking at is what every compliance product ships, and it is the number our own gate is
designed to refuse. Watch what happens to it after qualification — that delta is the product.** The
composition matters too: **2,329 of the 2,373 settled cells (98.1%) come from the 53 validation
predicates, not the 227 arithmetic ones** (MEASURED, L14 §1.12), and the validation-carried share is
weaker per cell — some of those bounds are near-vacuous, which is exactly what gate G3 exists to reject.

### 4.4 The state and reason vocabulary — frozen at 8 × 30

#### 4.4.1 Two vocabularies, not one — RESOLVED (owner decision, 10 Aug 2026)

The audit found the container guard emitting `ERROR(source_unreadable)`, a pair the frozen 8 × 30 cannot
represent: `source_unreadable` is a `not_run.*` code, and none of the five `error.*` codes fits a guard
trip. The same hole swallows two more of the eight documented `INVALID` causes — an unbound template, and
the two denominator computations disagreeing.

**The fix is not a 31st code. It is a category correction.** The 8 × 30 vocabulary is **per item**, and an
item is a cell. A container guard trip, a reader disagreement on sheet structure, an unbound template and a
closure violation are not properties of any cell — forcing them into a per-cell reason code was the error.

> **Run-level `INVALID` causes are their own closed vocabulary, `invalid.*`, with exactly the eight causes
> already enumerated in §II.6.2:** `.container_guard_tripped` · `.reader_structural_disagreement` ·
> `.template_unbound` · `.cells_bound_zero` · `.predicate_raised` · `.canary_silent` ·
> `.closure_violated` · `.denominator_disagreement`.
>
> The item-level count **stays pinned at 8 × 30** in all four places. An `INVALID` run renders a report
> naming which `invalid.*` cause fired, carries **no settled fraction of any kind**, and sets the aggregate
> verdict to `null`. Where a run-level cause has an item-level analogue — `.cells_bound_zero` and
> `.predicate_raised` — the item still carries its `error.*` code and the run additionally carries the
> `invalid.*` cause; the two are not alternatives.

**There are eight closed item states — `PASS`, `FAIL`, `INDETERMINATE`, `NOT_RUN`, `NO_PREDICATE`,
`ERROR`, `OUT_OF_SCOPE`, `INFORMATIONAL` — of which the first six are in the settled denominator and any
`ERROR` sets the run state to `INVALID`.** `PASS` and `FAIL` form the settled bucket; the other four
in-denominator states are unsettled; `OUT_OF_SCOPE` and `INFORMATIONAL` are removed from the denominator.
**Closure, seven terms, enforced not documented:**

```
outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface
```

It is the only form under which all eight states land in exactly one bucket, it is one `GROUP BY` over
`run_cell`, and **a cell that lands in no bucket aborts report generation.**

**The reason vocabulary is closed, namespaced and has 30 codes across five state families; a code is
admitted only if it implies a different remedy from every existing code.** `NO_PREDICATE` (8):
`.undecidable_by_construction`, `.requires_judgment`, `.not_yet_synthesised`, `.failed_qualification`,
`.rule_ambiguous`, `.no_obligation_specified` (**never conflate "the regulator did not legislate this"
with "we haven't got round to it"**), `.rule_withdrawn`, `.not_yet_requalified`. `NOT_RUN` (10):
`.input_unavailable.{counterparty,register,prior_period}`, `.source_unreadable`, `.template_unbound`,
`.deactivated`, `.budget_exhausted`, `.external_source_lacks_field`, `.external_source_unavailable`,
`.extractor_disagreement`. `INDETERMINATE` (4): `.extraction_abstained`, `.tolerance_straddle`,
`.conflicting_sources`, `.engine_disagreement`. `OUT_OF_SCOPE` (3): `.not_applicable` (requires a
machine-checkable pointer), `.not_selected` (requires the profile and its digest), `.withheld` (requires
an actor and rationale; **counted and displayed separately, never folded in**). `ERROR` (5):
`.predicate_raised`, `.cells_bound_zero`, `.canary_silent`, `.closure_violated`,
`.parser_disagreement_structural` — **any one sets `run_state = INVALID`.**

**Two codes carry corrections that travel with them.** `.external_source_lacks_field` means *the external
source structurally does not carry the field*; **our own near-miss is the canonical illustration and not
an instance** — the register's **list** endpoint returns `RegistrationNumber = null` on 650 of 650 fund
rows while its **detail** endpoint returns it on 228 of 228 (MEASURED, L08 §C.1, §C.3).
`.engine_disagreement` is emitted only when the cell appears in the **offline, digest-pinned
`engine_disagreement` table** for this template version — never from a live LibreOffice call.

**Severity is orthogonal to state**, not a ninth value: `BLOCKING | ADVISORY`, set by measured FFR (§7 G2),
with the number printed beside it. **`override` is likewise orthogonal**: it changes the result, retains
both states, and sits inside the signed payload.

### 4.5 How a report is proven to re-derive

The manifest embedded in every report footer pins eight things:
`{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha,
evaluator_version, fault_model_version, tool_versions:{python, lxml, openpyxl, celpy, z3}}`.
**`libreoffice` is deliberately absent, because LibreOffice is not on the verdict path** (§7 G12); the
offline artifacts it produced carry `lo_container_digest` and are content-addressed, so a quoted kill rate
stays reproducible even though the binary is not in the online pin.

| Non-determinism | Removal |
|---|---|
| The mutable register | `register_snapshot_sha256`. **The host function never resolves live at verdict time** — it resolves against a content-addressed snapshot, or the report is not reproducible |
| Wall-clock time | Every timestamp is an input recorded in the manifest, never read at evaluation. **CEL binds no clock** |
| Iteration order | RFC 8785 wherever a hash is taken; all report ordering by an explicit sort key |
| Floating point | There is none. Money is `int64 MILLI_USD_MILLION`; tolerances are integers |

**A model call is never on the re-derivation path.** If a filing had attachments, the *facts* the model
produced are content-addressed and pinned; `verify` replays those facts, it does not re-call the model.
**A model output is an input to the verdict, not a step of it.**

**The attestation** is a DSSE envelope over an in-toto Statement v1 whose `subject[]` carries the filing
digest **and** the template digest. Its top-level object is `scope`; it carries `assessor{id,
thirdParty:false, components}`, `timeVerified`, `expires`, `runState`, `livenessProof{canariesRun,
canariesPassed}`, the settled-fraction object, the per-check items, `counterEvidence[]`, the verdict with
its policy version, and four required sentences — bounded silence, purpose, `summaryIsNotSubstitute: true`,
and the detection boundary: *"This system detects error, not deception. Every check here is a consistency
check over a self-reported document. A coherent liar passes all of them."* **There is no `result`,
`status` or `pass` field anywhere in the schema and there never will be** — schema-level prohibition
survives the screenshot, the API integration and the intern.

**Who signs: DECIDED.** The **filer** signs with a detached key; the vendor signs nothing about the filing
and appears only as `assessor.id` with `thirdParty: false`. Vendor signing was rejected because it would
have the vendor attesting to a regulated filing it did not prepare — **if an FME shows an inspector a
signed attestation over a filing that was wrong, the signature is the first exhibit.** Sigstore keyless was
rejected because a public transparency log makes *the fact and timing of a named FME running a
pre-submission check* world-readable and correlatable. **The residual open item is legal review of that
decision, not the decision itself.**

---

## 5. PERFORMANCE AND COST

**Runtime per filing.** Reader A full structural parse **28–44 ms (MEASURED)**; reader B openpyxl load
**202 ms (MEASURED)**; fact table over 511 cells **1 ms (MEASURED)**; evaluation of 227 arithmetic
predicates **sub-millisecond (MEASURED)** and ~2 ms for all 280 (DERIVED); relation probes ~160 ms and
canaries ~35 ms (both DERIVED from the measured 7,946 fact-table mutations/s); receipt ~10 ms, guard <5 ms,
binding <1 ms, settled fraction + closure <5 ms, render + sign ~20 ms (all DERIVED).

**Three totals, and the middle one is the number to quote.** The **deterministic core as built today is
~30 ms (MEASURED)** — which is what makes "no queue" a measurement rather than a preference. A **complete
online run** with readers agreeing and no attachments is **≈ 450 ms (DERIVED)**, dominated by openpyxl and
the probes. **There is no third, worse figure any more:** removing LibreOffice from the online path removes
the 3.9 s tail. The 19,782-mutant campaign is **2.5 s (MEASURED)** and is offline, per template version.

**What is actually built.** *Schema induction, predicate harvest, arithmetic evaluation and the
settled-fraction denominator are built and reproduce in ~30 ms. Template binding, pre-flight, closure,
canaries, attestation and `verify` are specified and not built.* Relatedly: **the verdict path is specified
to make zero model calls, and the assertion is listed as a build gate; the gate is not yet written.**

**Model cost.** Prices VERIFIED-AT-SOURCE at `platform.claude.com/docs/en/about-claude/pricing`, 10 Aug
2026, USD/MTok: Opus 5 $5 in / $25 out (5-min cache write $6.25, cache hit $0.50); Sonnet 5 $2/$10 through
31 Aug 2026 and **$3/$15 from 1 Sep 2026**; Haiku 4.5 $1/$5. **Batch is 50% off both directions and the
cache multipliers stack with it.** Two dated facts that must not survive onto a slide: **Sonnet 5's
introductory pricing expires the day before the residency starts**, and **Opus 5 uses the newer tokenizer,
which produces approximately 30% more tokens for the same text** — so every estimate below is **MODELED**,
not measured with `count_tokens`, and **must be re-baselined before it is quoted**, not multiplied by a
guess.

Candidate proposal, per template version, one-time, on the model actually chosen (Opus 5, cached prefix
~6,000 tokens, ~600 fresh tokens of clause text, ~1,500 output tokens per candidate, Batch): **$0.0218 per
candidate, $0.52 for 24 obligations**, plus a one-time cache write of $0.0375. **About $0.55 per template
version; under $6 for the entire nine-workbook corpus, paid once per revision (MODELED).** The settling
experiment at its pre-registered size (≈30 obligations drawn × 10 candidates × 2 prompt regimes = 600
candidates) is **≈ $13 (MODELED)**, budgeted at $25 with re-runs — *the settling experiment for the entire
AI half of the architecture costs under thirty dollars, which is the correct reason to run it before
elaborating anything on top of it.* Attachment
extraction, per filing and only when attachments exist (20-page PDF ≈ 25,000 in / ~3,000 out): Haiku 4.5
**$0.040**, Sonnet 5 from 1 Sep **$0.120**, Opus 5 **$0.200** (all MODELED).

**The three headline numbers. Marginal model cost per filing on the workbook path: $0.00** — the 280
predicates, the settled fraction, the canaries, the probes and the verdict involve no model at all.
**Annual model spend across the whole modelled population: under $200**, even routing every attachment
through Opus 5. **And the cost that matters is not inference: it is the blind-filled qualification
corpus** — human time, for which no amount of model spend substitutes. **Do not pitch inference savings;
pitch the boundary.** Infrastructure is Fly.io `shared-cpu-1x`/512 MB at **$3.32/month ≈ ₹290/month
(VERIFIED-AT-SOURCE)** and ~3.4 GB/yr of storage: **≈ $240 ≈ ₹21,000 a year all in.**

**At 868 filings a year, and at 100×.** **868/yr is MODELED** — 217 FMEs × 4 quarters, assuming every FME
files every quarter including those registered mid-year. That is ~3.4 filings per working day, or **1.5
seconds of compute per day**. **This must be said out loud rather than hidden:** as a *deployment* this
architecture is absurdly over-engineered for 3.4 documents a day. **As a research instrument it is not** —
the layers are how the measurement is made legible. *The IFSCA workbook is the testbed, not the market: it
is public, machine-readable, small enough to characterise exhaustively, and has a real regulator behind
it. The asset is the method.* At 86,800/yr — 340 per working day, ≈ 11 minutes of compute per day —
**nothing about the request path breaks.** What breaks first, in order: (1) **blob storage**, 3.66 MB ×
86,800 ≈ **320 GB/yr**, triggered by disk not throughput → object storage on the identical `sha256` path,
**the content-addressing scheme unchanged, which is the point of choosing it**; (2) **SQLite's single
writer**, triggered by **concurrent uploads, not row count** → Postgres, **losing content-addressability,
so the manifest must then name a logical snapshot id instead of a file hash**; (3) **the register
snapshot** — the fetch plan is **1 list request + N detail requests where N = |records|**, and the run
that produced the 10 Aug 2026 snapshot made **`1 + N` GETs where `N = |records|`** (the drafts carried
**2,235**; that figure is **withdrawn to UNRECONCILED** — see §II.1.2 — because it matches neither 651 nor
2,006 and no document states its `N`) at 0.06–0.25 s spacing → snapshot
daily, cite the snapshot hash **and its age**, degrade past a staleness bound to
`NOT_RUN(input_unavailable.register)`, and **read IFSCA's terms of use before any scheduled polling**,
which has not been done; (4) **the qualification corpus, which is the real one — it does not scale with
filings at all, it scales with *templates***. That last is the transfer question, **and it is the
experiment that decides whether this is a product or a paper**: what fraction of the FME predicate set
transfers to a second prescribed format, at what human cost per transferred predicate, against a
pre-registered threshold. Nine workbooks are already on disk. **What never becomes the constraint at
either scale is inference:** at 100× with every attachment through Opus 5 the annual bill is **$17,400
(MODELED)** — the cheapest line in the table and the one everybody expects to be expensive.

---

## 6. THE INTERFACES

**Who these surfaces are for.** The buyer is **the filer's compliance officer**, who runs this before
submitting; the unit of value is the avoided deficiency — the inspection observation, the rework, the
Principal Officer's personal exposure — **and that value is UNMEASURED**. The supervisor is **not** a user
and not a buyer: the supervisory system is procured. **The supervisor is why the filer cares.** Where a
surface is useful to a supervisor it is described as useful to *a downstream reviewer*. The single question
that decides whether the entity-facing product is worth anything is **how often IFSCA returns an FME filing
for correction**, and it is answerable by one email.

**API.** FastAPI, `/v1`, JSON except where noted, OpenAPI generated, **no authentication before 30 October**
except on the mutating endpoints, which take an operator token.

| Method | Path | Request | Response |
|---|---|---|---|
| `POST` | `/v1/filings` | multipart: `filing` (.xlsx, required), `attachments[]`, `template_sha256`, `profile` | `201 {run_id, filing_sha256, template_sha256, run_state, report_url, attestation_url}`. Synchronous, median ~450 ms. `413` over cap, `415` non-zip, **`422` on `template_unbound` with the structural fingerprint in the body so an operator can admit the new template** |
| `GET` | `/v1/runs/{id}` | — | the full `run` record incl. `settledFraction`, `verdict`, `livenessProof`, `manifest` |
| `GET` | `/v1/runs/{id}/checks` | `?state=&reason=&predicate_id=` | paginated `run_check[]`, one row per predicate evaluation |
| `GET` | `/v1/runs/{id}/cells` | `?state=&reason=&sheet=` | paginated `run_cell[]` — **the closure table, and what a downstream reviewer's triage tool consumes** |
| `GET` | `/v1/runs/{id}/report.html` · `/attestation.json` · `/log.jsonl` | — | the self-contained HTML (byte-identical to disk, sha256 in the manifest); the DSSE envelope; NDJSON, one line per evaluation |
| `POST` | `/v1/runs/{id}/overrides` | `{stable_key, new_state, remark, evidence_sha256}` + token | the updated cell. **Both states retained**, inside the signed payload, counted separately |
| `POST` | `/v1/verify` | multipart: `report` or `attestation` | `{reproduced, diff[]}` |
| `GET` | `/v1/templates` · `/v1/templates/{sha}/schema` | `?state=` | `template[]` with `field_surface`, `n_predicates`, **`settled_fraction_ceiling` (`null` for unprotected templates — the absent-vs-empty rule applied to our own headline)**; and the full `TemplateSchema` + extraction manifest |
| `POST` | `/v1/templates` | `{origin_uri}` + token | `201`; runs T1–T6 and **stops at T7 awaiting a human signature** |
| `GET` | `/v1/predicates` · `/v1/predicates/{id}/versions/{v}` | `?template=&state=&kind=&obligation=&min_kr=&max_ffr=` | `predicate[]` with the **full qualification block** incl. `g4_corpus_provenance`; and per version the envelope, liveness witnesses and the mutants it kills by fault class. **This endpoint is the product's honesty, exposed — public and unauthenticated by design** |
| `GET` | `/v1/rejections` | `?template=&gate=` | every candidate the gate refused, with the gate, the measured number and the cells it would have covered |
| `GET` | `/v1/registry/roots` · `/v1/settled-fraction/history` | `?template=` | roots with timestamps and counts; the admission timeline annotated with measured rates. **Must be able to step down** |
| `GET` | `/v1/healthz` · `/v1/openapi.json` | — | — |

**Two prohibitions, enforced by schema and by test.** (1) **No endpoint returns a boolean pass/fail, a
`status: "clean"`, or a bare settled fraction** — every figure comes inside the object of §4.3 with all six
counts, so a consumer who wants one number must compute it and will have the denominators in hand when
they do. (2) **`ffr` renders as `null` with `g4_corpus_provenance: "SELF-AUTHORED"`** when that is the
provenance, so a client cannot display an uninformative rate as a measurement.

**CLI** (the primary interface during the residency; the API is the demo surface): `ingest` · `induce` ·
`harvest` · `propose` · `seed` · `qualify` · `admit` · `run` · `verify` · `watch` · `residue` ·
`transfer`. `make demo` runs `ingest → induce → harvest → run` against the workbook as published, on a
judge's laptop, offline after the fetch.

**Screens. One commitment governs all of them: there is no green tick anywhere in the product.**

**1 — Drop.** One control, no settings, no account. On submit: the run state and the two hero counts.

**2 — Report.** The hero is two counts of equal weight, same type size, same ink, no colour on either:
`12 failures across 2,373 checks.` and `1,374 fields were not checked.` The binding is fixed in the label
registry so it cannot drift: `<F>` = failing cells; **`<S>` = settled cells (2,373 on the reference
filing) — in this one label a "check" is a settled field, one per cell**; `<U>` = unsettled cells (1,374).
**The predicate count (280) belongs to the strap line and never to the hero.** The right-hand number is
never smaller, never grey, never below the fold, never collapsed. No progress bar, no ring, no percentage
in the hero: a fixed-height **stacked band** labelled by absolute count, with **the unchecked segment
hatched, not muted** — muted reads as "resolved, minor"; hatched reads as "not filled in", which is the
truth. **The band never fills**, because two permanent rows sit inside the denominator — *properties no
predicate can settle from this artifact alone*, and *demonstrated survivors from the residue set*. **100%
is structurally unreachable, and that is architectural rather than cosmetic.** Nothing renders green;
passing checks take body-text ink; only failures take colour — *the absence of colour is not the presence
of green.* One expandable strap line under the band: `denominator from styles.xml unlocked mask v3 ·
predicate set v11 · registry root 9f3c… · qualified against template sha256:7d9a… · 4 predicates
provisional · 280/280 canaries passed`. **Each failure expands to four things:** both cells, the clause
with its `eId` and a link to the exact page and bounding box, the CEL source, and — the unusual part —
**that check's own measured false-failure rate inline**: `fired on 2 of 96 clean filings [0.6%–7.4%] ·
corpus: BLIND-FILLED, n=96`. A permanent, non-dismissible sentence carries the detection boundary. **When
the run is `INVALID` the whole screen is replaced by the reason, the dead predicates, and no settled
fraction of any kind.**

**3 — The Unchecked panel.** Not an appendix: it sits on Screen 2, above the fold, and it is the
differentiator. Grouped by reason code with counts, and per entry **"what would make this checkable"**,
specific rather than generic. The canonical entry is writable today: *Third Schedule Part A(g) — whether
the valuation is appropriate*, `no_predicate.requires_judgment`, and what would fix it: *a materiality
threshold by scheme class of the kind CSSF Circular 24/856 Tables 1–3 specify (0.20% money-market / 0.50%
bond and mixed / 1.00% equity and other), plus a compensation-direction rule of the kind its Tables 4–5
specify.* Beneath the reasons: **demonstrated survivors** — not reasons but exhibits.

**4 — The predicate library.** Every admitted check, filterable, ≤ 515 rows, a plain `<table>`. Per row:
clause (`eId` + quote), CEL source, `KR = K/O` with both integers **and** the per-fault-class vector, the
degeneracy verdict with its Z3 witness, FFR with corpus provenance, `n` and Wilson interval, severity tier,
admission date, liveness witnesses — **and, beside each rule, what a flag-everything rule would have
scored.** Two tabs the category does not have: **Rejected**, and **the five-gate attrition funnel** per
obligation (generated → executed and bound → non-degenerate → killed → FFR-admitted). **A 20:1 attrition
ratio displayed honestly is a stronger demo than a settled-fraction bar, because no competitor will show
it.** One caution the screen must obey: **the gate has exactly one demonstrated rejection** — five of ALR's
six bound predicates assert only `≥ −1e17` over 1,428 cells and are refused (MEASURED, L14 §1.12) — and
**whether it rejects anything on the FME workbook is unmeasured**, since 19 of that workbook's 24 bounds
are a real `≥ 0`.

**5 — Settled fraction over time.** Renders from a static JSON log, no live backend. Each increment
annotated with the predicate's measured rates; **the chart must be able to step down** and every step-down
is labelled with its cause. Beside it, on the same axis, `R/O` — the fraction of observable defects no
admitted predicate can reach — the inverse curve. **When the 515-predicate figure appears it appears with
its per-workbook distribution attached, never alone:** it is a sum over nine workbooks and it is
concentrated, since `EDR_1` has zero formulas and `IFSCA_Annual_Reporting_Format` has zero formulas and
zero validations. **Publishing that distribution is a build gate, because no lane published it.**

**Build gates — commitments that are tested rather than believed.** `ci/no-green-tick.sh` (grep for
`✓ ✔ ✅ 🟢 / all clear / no issues / looks good / verified clean / compliant / passed all / fully checked`
over `src/ templates/ locales/`); `test_schema_constants` (**505 / 294 / 211 / 54 / 22 / 20 / 252 /
3,747** — properties of the file); `test_harvest_count` (**280** and **515** with the per-workbook
distribution — **a property of our code, allowed to move with a recorded reason**, split from the constants
test so a correct rejection by gate G3 does not fail the build); `test_denominator_provenance`;
`test_ffr_provenance`; `test_unmeasured_predicate_rejected`; `test_closure`; `test_error_absorption`;
`test_vacuity`; `test_predicate_raise_is_error`; `test_dual_reader`; `test_no_model_in_verdict_path`
(**not yet written**); `test_no_libreoffice_online`; `test_no_tlog`;
`test_attestation_has_no_status_field`; `test_openpyxl_never_writes_the_artifact`.

---

## 7. DECIDED HERE, AND WHAT REMAINS OPEN

| Ref | Item | Status |
|---|---|---|
| **G1** | Unit of the denominator and of closure | **DECIDED: the cell.** Beat the pair model because every measurement is a cell count and the pair model has no published enumeration rule (§4.2) |
| **G2** | FFR threshold setting `severity_tier` | **DECIDED, pre-registered: `FFR ≤ 0.02 ⇒ BLOCKING`; `0.02 < FFR ≤ 0.10 ⇒ ADVISORY`; `FFR > 0.10 ⇒ not admitted`.** Any defensible number beats none; changeable only by an argument that the old one was wrong, recorded with its date |
| **G3** | Money scale | **DECIDED: `MILLI_USD_MILLION`, `int64`, 1 unit = USD 1,000, `τ(n) = 5n`**, everywhere including the `Field.unit` enum |
| **G4** | State/reason vocabulary | **DECIDED: 8 × 30, frozen and normative** (§4.4). Any plan targeting 7 states or 19 codes is regenerated from this |
| **G5** | Where the evaluation contract lives | **DECIDED: one file, `EVALUATION-CONTRACT.md`**, containing the five rules and nothing else; every other document links to it |
| **G6** | How an obligation binds to a field | **DECIDED: a hand-maintained `obligation` table (`source='hand'`)**, because nothing of L1b is built; it flips to `'l1b'` when the clause graph produces `eId`s |
| **G7** | Gate order | **DECIDED: G0 → G1 → G3 proof → G2 → G3 empirical → G4** |
| **G8** | Regression constants | **DECIDED: split** into `test_schema_constants` and `test_harvest_count` |
| **G9** | Repo licence | **DECIDED: Apache-2.0** — it carries a patent grant and every core dependency chosen is compatible. First file created |
| **G12** | LibreOffice and the toolchain pin | **DECIDED: excluded from the online verdict path entirely** — it was a cross-check, so this is free, and it removes an unpinnable subprocess from under a byte-identity acceptance test. **Pinned by container digest wherever it runs offline**, with its outputs content-addressed so quoted kill rates stay reproducible. Consequence: `INDETERMINATE(engine_disagreement)` comes from the pinned per-template table, never a live call |
| **C21** | Who signs | **DECIDED: the filer, detached key**; vendor only as `assessor.id`, `thirdParty: false`. Residual: legal review of the decision, not the decision |
| **C22** | Pervasiveness `K`, `T` | **OPEN, non-blocking.** One file, `pervasiveness-policy-v1.json`, versioned inside the attestation. **Until the argument that sets them exists both render `PLACEHOLDER`, and no number for either appears anywhere** |
| **G10** | Person A | **OPEN — USER DECISION.** *Name one person, not on the team and having never seen the predicate set, who will fill ≥ 30 clean workbooks from the template and regulation only — or authorise the audited second-model-instance route, with the fill prompt hashed and published before the first workbook is filled.* **Every FFR in the product depends on this, and no FFR may be printed until it exists** |
| — | Licences not opened | **OPEN, engineering, before the code ships:** gVisor, Z3, `xbrl.us/dqc-license`, `cobalt`/`indigo` — **and IFSCA's terms of use for the register API**, a gap in conduct rather than code |
| — | Measurements before any number is quoted | **OPEN, ordered:** does our evaluator reproduce the template's cached values exactly, incl. `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101` — **a positive control is required before any kill rate is quoted**; our own `U/G`; does `celpy` pass the conformance suite **on error semantics**; key-binding accuracy `μ`; **the vocabulary→validation mapping — two lanes imply different counts and neither figure may be quoted until the build computes it**; whether a filer's Excel round-trip rewrites the 211 shared-formula followers; the field surface for an unprotected template; whether the `D17` COUNTIF defect recurs in the other prescribed workbooks (20 minutes, and it turns one finding into a pattern); **the transfer measurement** |

**One last thing this part must not sand off.** The gate, the seeded defects, the relations and the typed
non-settlement vocabulary are not four features. Remove seeded defects and the FFR is uncomputable and the
gate is decorative. Remove the gate and the settled fraction is an assertion. Remove relations and it is a
ceiling rather than a growth curve. Remove typed non-settlement and the whole thing is a linter. **No part
is removable — which is the test of whether an assembly is a design rather than a stack.**


---

# PART IV — THE PATH, THE DELIVERABLE, AND WHAT IS OPEN

**Warrant key.** **MEASURED** — produced first-hand by a re-runnable script against the real artifact ·
**VERIFIED-AT-SOURCE** — a primary document was opened and read · **SECONDARY** — a credible source says
so, nobody here opened the primary · **DERIVED** — arithmetic, inputs named · **MODELED** — an assumption
with the arithmetic shown · **UNVERIFIED**. A derived number never claims a stronger warrant than its
weakest input.

Two standing rules govern every line below. (1) Before reporting an absence, run a positive control and
state the denominator. (2) A pre-registered criterion may change only by an argument that the old
criterion was wrong — never by the discovery that it cannot be met. Both were broken inside this
research; the breakages are in the evidence base rather than hidden.

---

## 1. THE EXPERIMENT QUEUE, RE-ORDERED BY WHAT DECIDES THE DESIGN

Ordered by **blast radius per rupee**: an experiment ranks higher if a negative result deletes more of
the plan per unit cost. Three ranks look wrong and all three are deliberate. A **ten-minute browser
check** ranks first — it is the only item that can end the programme. A **twenty-minute email** outranks
every engineering experiment. The **settling experiment drops to eighth** — it can only tell us how large
the model's role is, and the architecture survives its failure smaller. This ordering is written against
the standing bias: *you will pay any price to avoid believing something false, and almost no price to
find out whether the thing is over.*

| # | Experiment | What it settles | Cost | Pre-registered threshold, written before the run | What a negative result kills |
|---|---|---|---|---|---|
| **E0** | Open `giftifih.getkruu.com/apply` in a real browser; screenshot every field | Whether there is a programme to enter | 10 min | Binary: the form loads and accepts a draft. Any mismatch against the recorded field caps is logged before a word is written | **The entire programme.** WebFetch returned HTTP 404, the root served only an SPA shell, and nobody in this corpus has seen the live form. No second entry |
| **E1** | One email to IFSCA's Division of Investment Funds: are these checks already run on receipt? how often is an FME return sent back for correction? are any filed returns obtainable? | Whether the filer-side product is a gap or a convenience | 20 min + wait | No numeric threshold. *If IFSCA already validates on receipt, the entity-facing product is reclassified as a convenience in the application text before submission* | **The product, not the research.** The NEC SupTech award (27 Jan 2026, ₹39,57,36,115.52, scope includes an RE-facing portal, VERIFIED-AT-SOURCE) makes it urgent |
| **E1b** | The administrator call — KFin / CAMS / Basiz (§1.3) | Whether the valuation-error boundary already exists privately | 1 call | None. A written house tolerance *improves* the problem statement | **Nothing.** Demoted from killer to pitch-shaping |
| **E4** | Cross-format transfer over the nine prescribed workbooks already on disk | Product or paper about one workbook | 2 days | **If the human cost per transferred predicate is not materially below the cost of authoring one from scratch, the method does not generalise.** Publish per-template settled fractions including the zero cases | The claim to be a **product**. Exactly one thing must hold for this to matter beyond one regulator: induction plus qualification must transfer at bounded human cost |
| **E3** | Formula-override detection end-to-end: any cell carrying a formula in the pinned blank and a literal in the filing | Whether the flagship check works on the real artifact | 1 day | Must detect a seeded F11 **pair** and fire on zero template-computed clean filings | Nothing, but load-bearing: it needs **no corpus** — its oracle is the regulator's published blank. Predicate #1; `TEMPLATE_DIFF` is its method in the schema |
| **E2** | Decidability pilot: draw and stratify `shall` clauses until Stratum A holds 20 | The denominator E6 needs | ½ day, no model | Report `\|A\|/\|drawn\|` — the measured decidable fraction of the instrument. No kill threshold | Nothing. It stops E6 measuring a curation instead of a model |
| **E5** | Baselines `B0 ∪ B1 ∪ B2` — native formulas (35 SUM identities + 3 COUNTIF tallies = 38 of 294 authored expressions; 138 of 505 evaluated cells), Daikon at `--conf_limit 0.99`, and the degenerate arm | The bar E6 must clear | 1 hour | None; **the output is the bar.** Runs **before** E6 | Runs first or E6 is uninterpretable |
| **E11** | Characterise the LibreOffice normalisation defect and run the value-agreement positive control. `soffice` migrates 19 `x14` validations into the main namespace and expands 294 → 505 formulas in 3.9 s, but writes **53** main-namespace validations where 35 + 19 = 54 | Whether the engine under the observability filter is trustworthy | 2 hours | The missing validation is identified by name **and** LibreOffice reproduces Excel's values exactly, including `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101`. **No kill rate renders before this passes** | Normalisation, and every kill rate computed through it. *A one-validation silent loss in the tool adopted to fix a silent loss is the failure this product exists to prevent* |
| **E6** | The settling experiment (§1.2) | How large the model's role is | 1–2 weeks human · ≈$13 model | **≥ 6 of 20** in Stratum A survive all five gates **and** the surviving set beats `B0∪B1∪B2` on marginal kill at equal FFR | **L3, and only L3.** Predicates become hand-authored from the 294 native expressions, the 20 resolving vocabularies and the statute |
| **E7** | The residue set: generate mutants, adjudicate INNOCUOUS/WRONG, run the admitted set, report survivors | The size of the class of filings that are internally perfect and materially false | 1 week | None. **`\|RESIDUE\| ≠ 0` is expected and is the finding** | Nothing — it is the publishable result. Re-runnable by a third party **given the published fault model and the published adjudication record**, both content-addressed |
| **E8** | Blind-fill corpus: ≥30 correctly-filled workbooks by someone who has never seen the predicate set | Whether any FFR in the product means anything | 2–3 weeks human | A predicate whose only FFR is `SELF-AUTHORED` cannot be admitted and renders `uninformative`, never a number | **Every FFR the product displays**, and with it the headline settled fraction (§4.1 step 2). Highest blast radius of anything that is not cheap |
| **E9** | Differential and invariant relations, rescoped: 25 candidates, of which **15 need nothing but the filing** | Whether the growth story is real | 2 weeks | Each passes the five gates like any predicate; publish the before/after delta **and the relations that moved nothing, as moving nothing** | The growth curve. Ceiling stated in advance: this moves **≈0 of the 7** properties not settleable from the artifact at all |
| **E10** | Feasibility gate on the conformal layer: measure μ, then apply the forced-abstention floor `r ≥ (μ−α)/(1−α)` | Whether it is built at all | ½ day, on paper | **μ > 0.30 ⇒ do not build it**; at α = 0.05 the floor already exceeds 26.3% | The conformal machinery. Largely settled: **0 of 3,755** unlocked cells are ambiguous under the address key, **154 of 3,755 (4.10%)** under a header-anchored key (MEASURED), so binding is a lookup, not a prediction |
| **E13** | Open PROVE (arXiv:2607.28218) in full | Whether novelty claim N3 needs narrowing | 1 hour | Binary: the implementation section either does or does not contain a per-rule coverage or error-rate table | Only the **abstract** has been read. The two quantitative facts we use are in it and survive; every *absence* claim about PROVE currently reads **not visible in the abstract; the full text is unread**. Open it before the pitch |
| **E12 / E14** | The three-paper checker contradiction · QuantMind on a protected xlsx | — | — | — | **Both closed.** E12 is dissolved into an architectural constraint — **L5 must never repair; it adjudicates and reports.** E14 is moot: ingest is ~200 lines of `lxml` at 28 ms; protection is advisory and every reader tested reads through it; merged headers recover identically across three readers (252 ranges). The real obstacle was the extension namespace |

### 1.1 The settling experiment, pre-registered

> **DECISION E6.1 — Stratum A contains 20 obligations. Retain L3 for Stratum A iff ≥ 6 of 20 survive all
> five gates AND the surviving set beats `B0 ∪ B1 ∪ B2` on marginal kill at equal false-failure rate.
> Delete at ≤ 2 of 20. A result of 3–5 triggers exactly one pre-committed extension to n = 40 at a
> threshold of ≥ 12, and no further extension ever.**
> *Alternative it beat:* the brief's `n = 10, delete below 3`, and the intermediate drafts' `n = 12`.
> *Reason:* `3 of 10` cannot distinguish the hypotheses it was written to distinguish — at p = 0.35 it
> deletes a working L3 26.2% of the time, at p = 0.15 it keeps a broken one 18% of the time. The drafts
> then kept the power table while halving the sample. **The figures below are exact binomial tails for
> n = 20 and belong to no other n.**

**The draw.** Enumerate every `shall` in the chapters of the *IFSCA (Fund Management) Regulations 2025 as
amended to 30 January 2026* (102 pp, published 07/05/2026, VERIFIED-AT-SOURCE) governing scheme
operation, valuation and periodic reporting. Order by (regulation number, sub-clause). Seed a PRNG with a
value written into the pre-registration file; draw without replacement. A **human**, not a model, assigns
each clause to Stratum A (arithmetically closed — quantities, dates, counts, identifiers or relations
among fields in the L1-induced schema) or Stratum B (judgment-bearing or externally dependent), and
records the assignment before generation. Draw until `|A| = 20`; cap Stratum B at 10; ≈30 drawn in total.
`|drawn|` and `|A|/|drawn|` are the experiment's first result — the measured decidable fraction of the
instrument, which nobody has.

**Power at the n it belongs to (DERIVED, exact binomial):**

| True per-obligation survival rate p | P(X ≤ 5) — retain threshold not met | P(X ≤ 2) — outright delete | P(3 ≤ X ≤ 5) — extension fires |
|---:|---:|---:|---:|
| 0.15 | **0.933** | 0.405 | 0.528 |
| 0.20 | 0.804 | 0.206 | 0.598 |
| 0.25 | 0.617 | 0.091 | 0.526 |
| 0.30 | 0.416 | 0.036 | 0.381 |
| 0.35 | **0.245** | 0.012 | 0.233 |

Two things this says that the drafts did not. The celebrated figures — 0.933 at p = 0.15 and 0.245 at
p = 0.35 — are `P(X ≤ 5 | n = 20)`, the probability the *retain* threshold is not met, **not** the
probability of outright deletion, which is `P(X ≤ 2)` and is far smaller. And the extension zone fires
more than half the time at p = 0.15–0.25, so **the n = 40 extension is the modal path and must be
budgeted as such**. Over both stages the rule deletes L3 92.9% of the time at p = 0.15 and wrongly
deletes it 13.4% of the time at p = 0.35 (DERIVED). The revision is legitimate because it is entirely
*ex ante*, made before a single model call, and moves the threshold in the direction that makes L3
**harder** to keep at low p (0.929 vs the old 0.820). *A criterion revision that increases the chance of
killing your favourite layer is not a rescue.* The 95% Wilson interval at p̂ = 0.30 is **[0.145, 0.519]**
at n = 20, against [0.108, 0.603] at n = 10; the interval goes on the slide, the point estimate never.

**The five gates. An obligation survives iff at least one of its 20 candidates passes all five. Ordering
is fixed: G0 → G1 → G3 proof arm → G2 → G3 empirical arm → G4** (free before cheap before expensive).

| Gate | Test | Why it exists |
|---|---|---|
| **G0 — scope faithfulness** | The candidate carries the exact character span of the clause it claims to implement, `source.find(quote)` succeeds deterministically, and every proviso, exception and cross-reference in that span is either implemented by a branch **or** emitted as `NO_PREDICATE(no_predicate.not_yet_synthesised)` carrying the proviso's verbatim text and character span, with `provisos_declared` in the predicate's scope block. Neither ⇒ reject | Frontier models ground statutory spans well (SpanFaith 0.77–0.79) and wire the override structure wrong (Edge-F1 ≈ 0.22, n = 2,290). Gates 1–4 cannot see a silently dropped proviso |
| **G1 — executes and binds** | Runs without error; every key it reads exists in the induced schema; **`cells_bound > 0`**. Binding to zero is `ERROR(cells_bound_zero)` and makes the run `INVALID` — never `PASS`, and never `NOT_RUN`, which would file the vacuous pass beside a rate-limited register | Only **563 of 29,000+** of TOGA's bad assertions were non-compiling; the errors are semantic and survive a compile gate |
| **G2 — kills** | `K/O > 0` on **observable** seeded defects **and** marginal kill strictly greater than `B0∪B1∪B2` | Two of the three demolitions in this literature are demolitions by baseline |
| **G3 — non-degenerate** | Not equivalent to a published degeneracy class; flags ≤ 50% of the clean corpus; spurious firing on the 10% control sample below threshold; `degenerate_floor` margin > 0 | Taking every candidate a model writes yields **100% coverage and 100% FFR** (SPADE's own paper). And the peer-reviewed exhibit: CLAUSE's best F1 over an 80-cell table is **65.4** on a ~49.5%-positive split where a constant always-flag classifier scores **66.2** (DERIVED), with a full-text positive control finding zero occurrences of "majority baseline", "constant classifier", "random baseline", "trivial baseline" or "degenerate" |
| **G4 — false-failure rate** | `FFR ≤ τ = 0.10` computed **for the set, not the predicate**, using `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`; reported as a Wilson interval with `n`; **and `corpus_provenance ≠ SELF-AUTHORED`** | 44.4% of raw candidates individually blow a 25% FFR budget, and in two of SPADE's nine pipelines assertions that each met the budget composed to **88%** and **53%**. A registry that admits one at a time drifts to flag-everything |

> **DECISION E6.2 — the experiment's bar and the registry's bar are different numbers, reported
> separately.** E6 asks *can this fire at all, and does it beat the free baselines* — `K/O > 0` plus
> marginal kill. The **registry** admits at `K/O ≥ 0.80` on the fault classes the predicate claims to
> cover. *Alternative it beat:* one threshold. *Reason:* a predicate at `K/O = 0.05` survives the
> experiment and fails the registry, and the drafts stated both numbers without saying they were
> different tests. Two attrition numbers, always published side by side.

**Corpus provenance — six values: `SELF-AUTHORED` · `BLIND-FILLED` · `TEMPLATE-COMPUTED` ·
`REGISTER-DERIVED` · `REAL-PARTNER` · `PUBLIC`.** The register value is spelled `REGISTER-DERIVED`
everywhere. G4 is computed in this priority order, and provenance travels with every number.
**`TEMPLATE-COMPUTED`** — fill the input cells and let the workbook's own 505 formula-bearing cells
compute the derived ones; a predicate firing on a cell IFSCA's artifact computed is a genuine false
failure (MEASURED: all 505 carry cached values). **`REGISTER-DERIVED`** — for identity predicates the
clean corpus is the live register: **228 of 228 live FMEs return a non-empty `RegistrationNumber` via the
detail endpoint** (MEASURED, 1 fetch error, coverage 99.6% of 229); no synthetic caveat applies. Its
warrant is narrow and must be stated narrowly: *every entity in the register is validly registered, so a
predicate asserting membership cannot have a true positive there; a predicate asserting **format** can,
and **87 of 228** registration numbers fail the obvious regex.* **`BLIND-FILLED`** — the minimum bar
below which no FFR may be printed anywhere. **`SELF-AUTHORED`** — renders as `—` and the word
**uninformative**; the schema forbids a number.

**Cost (DERIVED from a MODELED unit price, therefore MODELED):** 30 obligations × 2 prompt regimes ×
k = 10 = 600 candidates at ~$0.0218 each with a cached schema prefix and the Batch API's 50% discount ≈
**$13**; budget $25 with re-runs and **$26 more if the extension fires**. The two drafts quoted two
different totals with no arithmetic; this is the arithmetic.

**Written down before the first API call**, in `experiments/9.1/PREREGISTRATION.md`, committed,
content-addressed, hash published in the README, nothing added afterwards: the sampling rule and PRNG
seed; the stratum assignment for all ~30 obligations by a named human, dated; `|drawn|`; both prompts
verbatim with hashes; model id, API date, `k`, temperature, Batch job id; `τ = 0.10`, the fault-model
version and operator list, and the code hashes of B0/B1/B2; the five gates and their order; the decision
rule and its power table; the corpus provenance of every FFR that will be computed; a commitment to
publish either way; and **the arguments that will not be accepted as grounds for changing the criterion**
— *"we should have sampled better obligations"* (the rule is pre-registered), *"the clean corpus was
synthetic"* (known in advance, and symmetric with the baselines), *"Stratum B was always going to fail"*
(hence a separate stratum with a pre-registered expectation of 0–1 of 10), *"the language was wrong"*
(the Python arm is exploratory and may never change the CEL decision).

**The framing that makes the experiment unfailable in the only sense that matters.** The deliverable is
not "L3 works" but a number: *of N model-proposed regulatory checks, k survived a five-gate admission
test specified before the model ran.* **k = 0 is a result** — the first measurement anyone has of whether
a frontier model can write a regulator-grade executable check. The search establishing that the space is
empty is in this corpus **with its positive control**: across the arXiv abstract index on 10 Aug 2026,
zero papers report a false-failure rate or a mutation kill rate for an executable predicate synthesised
from regulatory text, and the control query returns the known-present paper.

**The caveat that ships with every kill rate.** The bridge from seeded to real faults is the coupling
effect, and **there is no coupling study for financial filing data**. `KR = 0.82` licenses exactly one
sentence: *"rejects 82% of the N defects I seeded, under fault model v3, of which U were discarded as
unobservable."* It does not license *"detects 82% of real filing errors."*

### 1.2 The two field observations

**E1 — the IFSCA email**, sent 11 Aug, ranked joint-first with E0. It asks whether the Division of
Investment Funds runs arithmetic or structural validation on FME quarterly returns at receipt; how often
a return is sent back for correction; whether any filed returns are obtainable, even unlabelled; and, at
no extra cost, whether the public register's null descriptive fields are a privacy posture or a defect.

**E1b — the administrator call. DECIDED: it stays, scheduled in M0, demoted from killer to
pitch-shaping.** The valuation wedge was deleted for five independent measured reasons, foremost that
whole-word `NAV`, `per unit`, `units outstanding` and `dealing` return **0 hits** across all nine
prescribed workbooks in every XML part, with positive controls passing on the same interface (`Scheme`
123, `USD Million` 31, `Portfolio` 25, `valuation` 6). A written house tolerance therefore cannot end the
programme; it changes one paragraph. It stays because it costs one call and a positive answer *improves*
the problem statement. The question, in this exact wording, to KFin Technologies, CAMS or Basiz Fund
Services:

> **"When you strike a NAV for an IFSC scheme and it differs from what you expected — from your own
> recomputation, from the prior valuation point, or from the manager's shadow — what is the number that
> makes you stop and escalate rather than release? Is that number written down, and who set it: you, the
> FME, or the administration agreement?"**

This closes the disagreement in which one draft ranked the call joint-first and another omitted it: it is
neither joint-first nor absent. It is M0, and it is not a killer.

---

## 2. THE DATED BUILD PLAN

### 2.0 What is built, and what is specified

> **Schema induction, predicate harvest, arithmetic evaluation and the settled-fraction denominator are
> built and reproduce in ~30 ms. Template binding, pre-flight, closure, canaries, attestation and
> `verify` are specified and not built.**

**BUILT:** L0 receipt and content addressing · L1 induction (`lxml`, all sheets, `extLst`/`x14`, shared
formulas) at 28–44 ms · predicate harvest with no model (280 FME / 515 across nine) · fact-table
construction (~1 ms) · arithmetic evaluation (sub-ms for 227 predicates) · the 3,747-cell denominator ·
the seeded-defect harness's first gate (19,782 mutants in 2.5 s = 7,946/s) · the degenerate-bound
rejection. **PARTIALLY BUILT:** dual-reader ingest (both readers exist, the agreement check does not) ·
the report renderer. **SPECIFIED, NOT BUILT:** container guard · template binding · predicate selection ·
pre-flight key check · differential probes · run-time canaries · closure · aggregate verdict · `verify` ·
the clause-graph layer · L3 — and nothing of L3 should be built until E6 runs.

Two claims must carry their real warrant. *"15 exact + 2 normalisation-dependent of 24 → 574/581 = 98.8%
in an afternoon"* is **DERIVED —
an enumeration argument, not a run**; nobody generated 574 predicates and measured anything. And *"zero
model calls in the verdict path"* is a **design property with a build gate specified and not yet
written**; it becomes a property of the system the day `test_no_model_in_verdict_path` exists.

### 2.1 By 16 August — the application and the one link

> **DECISION 2.1 — one URL: a public GitHub repository whose README is the pitch. Licence: Apache-2.0.**
> *Alternatives it beat.* **Demo video** — a judge cannot distinguish a real pipeline from a screen
> recording of a mock, and *that distinction is the entire subject of this project*; losing it in the
> artifact would be self-refuting. Put a 60-second capture inside the README; it costs no URL. **Deck** —
> everyone sends one and it cannot show that a number was computed rather than authored. **Figma** —
> signals a design exercise. **Website** — another thing to be down at 09:00 on the 16th. **MVP behind a
> login** — judges will not create accounts. Apache-2.0 beat MIT because it carries a patent grant and
> every core dependency chosen is compatible.

| Date | Work | Done means |
|---|---|---|
| **Mon 11 Aug** | (a) **E0 — open the portal in a real browser, screenshot every field, start a draft.** (b) **E1 email sent.** (c) Repo skeleton, `LICENSE`, CI. (d) L0 ingest: nine workbooks, content-addressed, manifest written. (e) Delete the superseded probe script that still reports `xsheet=0` on all ten sheets and sits beside the corrected one with nothing marking which is authoritative. (f) Write `docs/ABSENCE-SCOPE.md`: the **inclusion rule** for what counts as an opened vendor page, plus the list | Form confirmed live with screenshots; email sent; `ingest.py` run twice yields byte-identical manifests; every `sha256` matches; the broken script deleted, not patched around; **no absence claim anywhere quotes a vendor count — only the list** |
| **Tue 12 Aug** | L1 induction: `lxml` only, **all** sheets including hidden, `extLst`/`x14` parsed, shared formulas materialised, keys label-anchored `(sheet, header_path, row_label)` with coordinates as a resolved attribute. Predicate harvest. **Split the constants test** | `test_schema_constants` pins **505 formula cells (294 authored, 211 shared dependents), 54 validations, 22 list-type, 20 resolving, 252 merged ranges, 3,747 field-surface cells** — properties of the file. `test_harvest_count` pins **280 / 515** — a property of our code, allowed to move with a recorded reason |
| **Wed 13 Aug** | L5 execution with the **eight-state axis** and the **thirty-code namespaced reason vocabulary**, `cells_bound` per predicate, settled fraction against the unlocked-cell field surface, self-contained HTML report | Clean filing → 0 FAIL; one seeded fault → exactly the predicates reading that cell FAIL; a unit test asserts the denominator comes from the unlocked mask and **not** from the predicate set; the report opens from `file://` with networking off |
| **Thu 14 Aug** | Seeded-defect harness with the observability filter and the control arm; degenerate-bound rejection; register snapshot and the identity predicate | `KR = K/O` printed with both integers and `U/G`; **ALR's five `−1e17` bounds rejected** and its settled fraction recomputes downward; **FME's 19 `≥ 0` bounds admitted**; the register predicate ships with its **measured 38.2% (87 of 228)** regex false-failure rate as the worked example of why the FFR column exists |
| **Fri 15 Aug** | README as pitch; `make demo`; `verify`; 60-second capture; the ~1,100 words. **Complete the FinVerBench warrant annotation and the +37–54 correction (below)** | `make demo` reproduces every README number on a clean clone; the CI grep for banned all-clear glyphs and phrases fails the build |
| **Sat 16 Aug** | Submit in the morning — **or Friday the 15th if the user takes §7 Q4** | Repo tagged `v0.1-application`, its commit sha in the application text |

**The README, in order** (the ordering is the argument): one sentence — *a regulated filing checker that
reports what it did **not** check*; then **the silent false negatives in a table, leading with the one
that is not our code** — `openpyxl` 3.1.5 sees **35 of 54** validations and reports the **AML-CFT sheet
as having zero when it has five**; our addressee parser reported 64.5% coverage against a true 79.9%; our
formula regex `<f[ >][^>]*>` could not match `<f>SUM(...)</f>` and reported **zero** cross-sheet formulas
where the FME workbook alone has **195 of 294**; our own qualification harness v1 printed a mutation
score of **100.1%** — arithmetically impossible — cleanly and confidently, from two independent defects,
one of them the degenerate-baseline failure committed by the harness built to detect it. **A fifth was
committed while writing this specification:** a field named `EncryptDId` was tested, found null in 650 of
650 rows, and reported as an absence; the correct field, `EncryptedId`, is populated in 650 of 650 rows
and resolves **228 of 228** live FMEs. The positive-control rule would have caught it and was not run.
All are deterministic programs; all produced clean, confident, well-formed wrong output. Then the
measured result as real program output — 280 predicates touching 2,373 of 3,747 filer-editable cells,
1,374 declared unchecked, ~30 ms, no model calls — **immediately followed, in the same block, by the
admission caveat of §4.1 step 2. The number does not ship naked.** Then a report screenshot showing the
two-count hero and the Unchecked panel, no green tick; `make demo`; **what is not built yet**, named
plainly, plus §3's do-not-build list, because a do-not-build list in a README is itself evidence of the
discipline being pitched; then the capture.

**Application fields** (~1,100 words, caps enforced by the portal): Solution Title names the *boundary*,
not the AI · Elevator Pitch 150 w · Problem Statement 250 w covering *what problem / who experiences it /
why it matters / how it is handled today*, leading with the AML-CFT blind spot because a judge can check
it in ninety seconds and it is not our code · Proposed Solution 250 w, uniqueness = three claims and no
more · Current Stage **Prototype** · Demo URL = the repo · Focus Area **Theme 1 → Fraud, Risk &
Compliance** (alternative: *Autonomous Banking*, better fit for the agentic framing, less workflow
density) · Why Fintech / GIFT City 200 w · Future Potential 250 w with M1 named as an experiment allowed
to fail.

**Claims permitted in the application, and no others.** The measured triple 2,373 / 1,374 / 3,747 with
its admission caveat; 280 predicates, and **515 always with its per-workbook distribution attached**
because two of the nine templates have zero formulas and one has zero validations as well; ~30 ms; 505
formula cells; 54 validations of which 22 list-type and 20 resolving; `openpyxl`'s 35-of-54 and the
AML-CFT zero-of-five; the `Special Situation Fund` / `Family Investment Fund` COUNTIF gap; the
38.2%-of-228 register FFR; **217 FMEs and 360 schemes as at the Q4 FY2025-26 bulletin date**, and
separately **650 Fund Management register rows as at 10 Aug 2026, of which 229 resolve as live FME
registrations** — never blended in one sentence, and **no scheme count is published from the register
until the split rule is written down**; ~868 filings a year labelled **MODELED (217 × 4)**; and for the
India-asymmetry paragraph, that the **EBA publishes 12,925 rule-instances resolving to 8,052 distinct
rules** quarterly, EIOPA 6,767, ESMA ships a per-rule `Automatable Yes/No` column, and **RBI's
validation-rules trail dead-ends at a 3,254-byte login shell** (VERIFIED-AT-SOURCE). Where the EBA's
deactivation record is used it reads: **1,692 of the 20,562 validation rules in release 3.5 have been
deactivated at least once (8.23%); 1,008 are still off, 343 of those at `error` severity** — and the
12,925 figure is never divided into it.

Two annotations are non-negotiable before submission. **FinVerBench:** attach *"(FinVerBench,
arXiv:2605.29586 — single-author preprint, not peer-reviewed, artifacts not released in v1, n = 43
clean)"* to its first occurrence and never let two rows sourced from it read as two independent
measurements; the refutation it supports still stands — *a model can be calibrated on 43 clean
statements, and nine of fourteen complete frontier runs were not, on the same 43, with nothing in any of
the fourteen complete outputs distinguishing the calibrated run from the rest* — but say in the same
sentence that **the clean set was built to satisfy the checks**, which is why a 0% false-positive rate on
it is partly true by construction. **The +37–54 figure:** write it as *feeding an induced schema in as an
explicit I/O constraint is the dominant lever on **structural similarity** (+37–54 percentage points) in
the only published study of statute→executable-model generation (arXiv:2604.17153); that study's
**outcome** equivalence tops out at 51–53%, and the paper itself states that structural similarity does
not guarantee outcome equivalence, or vice versa.*

### 2.2 21–22 August — the two-day build, with a hard cut line

**Scope thesis: the surfaces and the honesty machinery, not the parser.** Everything above the cut line
is the demo; everything below is abandoned without hesitation if the line is reached.

| # | Task | Depends on | Acceptance test |
|---|---|---|---|
| T1 | **L0 ingest, content-addressed, with dual-parser differential ingest** — disagreement on sheet count, cell count, formula-cell count, validation count, defined names or hidden sheets **fails the run, loudly** | — | Feed it a fixture where the parsers disagree; assert the run aborts. *This research is the proof it works: three implementations gave 244 / 294 / 505 on the same file, two of them sitting in the same directory undetected* |
| T2 | **L1 induction + extraction manifest** — parts read, parts skipped, namespaces seen, constructs not understood | T1 | The pinned constants; where readers disagree, affected fields are `NOT_RUN(not_run.source_unreadable)` **by construction**, never silently absent |
| T3 | **Predicate harvest** — nine classes, 280 / 515 | T2 | Every predicate round-trips through JSON; vocabularies resolve from the **pinned blank template**, never from the artifact under test |
| T4 | **L5 execution** — 8 states, 30 reason codes, `cells_bound`, provenance composing by weakest input | T3 | Clean → 0 FAIL; seeded fault → exactly the reading predicates FAIL; **`cells_bound == 0 ⇒ ERROR(cells_bound_zero)` and run state `INVALID`** — never `PASS`, never `NOT_RUN`; a runtime error in `expr` ⇒ `ERROR(predicate_raised)` ⇒ `INVALID`; `applicable == false ⇒ OUT_OF_SCOPE` from the `out_of_scope.*` family |
| T5 | **Settled fraction against the field surface, computed twice by independent code paths** | T2, T4 | Prints `2,373 of 3,747`; the two computations must agree or the run is `INVALID`; a test asserts the denominator's provenance |
| T6 | **Run manifest + content addressing** — `{template_sha, filing_sha, predicate_set_root, code_git_sha, python_version, tool_versions, register_snapshot_sha}` | T4 | `verify` re-derives the report from the manifest and byte-matches |
| T7 | **Self-contained HTML report** — one file, inline CSS/JS, no external requests | T4–T6 | Opens from `file://` with networking off; renders on a phone; the CI grep for `✓ ✔ ✅ 🟢 "all clear" "no issues" "looks good" "verified clean" "compliant" "passed all" "fully checked"` fails the build |
| T8 | **Seeded-defect harness** — observability filter, 10% control arm, per-fault-class kill vector, `K/O` + `U/G` | T4 | Reproduces on the real artifact; a test asserts the **site set is the field surface, not the predicate graph**; **E11's positive control has passed** or no kill rate renders |
| T9 | **The qualification gate** — degenerate-floor rejection; every admitted predicate carries `mutation_score`, `ffr`, `ffr_corpus_n`, `ffr_corpus_kind`, `severity_tier`, `admitted_at` | T8 | ALR's five `−1e17` bounds rejected; FME's 19 `≥ 0` bounds admitted; **admitting a predicate with an unknown error rate raises, and the test asserts the rejection** |
| T10 | **Run-time seeded canaries** — for every admitted predicate, instantiate its stored kill-witness against **this** filing and re-run. Any predicate that fails to fire on a fault it is known to detect ⇒ **`INVALID`** | T8, T9 | Rename a sheet deliberately; assert the run returns `INVALID` naming the dead predicates — **not** a clean report |
| — | **====== HARD CUT LINE — the demo is complete above this ======** | | |
| T11–T15 | Drop screen · predicate-library screen with the five-gate attrition funnel · settled-count-over-time that can step down · attestation stub with no `result`/`status`/`pass` property at any depth · three differential relations (formula-override, cross-format agreement, four-way funds-raised partition) | T7, T9 | 280 rows in <200 ms with no virtualisation library; a synthetic template-version bump makes the line fall; tampering with one cell changes the report sha and `verify` fails; each relation holds on the clean filing, is violated by a targeted mutant, **and passes the five gates first** |

**Cut-line discipline.** T1–T10 is the whole demo: the pipeline runs, the report renders, the denominator
is computed twice, the gate visibly rejects bad predicates, and the system proves it was alive. If Day 2
morning is lost to a venue problem, ship T1–T10 and present from the HTML file and the terminal. **The
relations sit below the line deliberately** — two days is not enough to author them honestly, and doing
it badly would poison the most publishable component. **Not in the two days at all:** any model call, any
database, any auth, any deploy pipeline, any queue, any framework.

### 2.3 1 September – 30 October — the residency

Eight and a half weeks, five funded milestones plus an unfunded pre-residency week, each with a
measurable acceptance test that can fail. M1 is the settling experiment, because the standing bias is to
elaborate rather than to find out whether the thing is over.

**M0 — pre-residency (23–31 Aug), unfunded.** E1 follow-up if unanswered; **E1b**; run **E2** and
**E4**; write and commit `experiments/9.1/PREREGISTRATION.md` and publish its hash; publish
`docs/OWNERS.md` (§6 G11). **Acceptance:** the pre-registration hash is public **before 1 September** and
no model has been called against the E6 prompts. If the hash is late, the experiment is downgraded to
exploratory and says so.

**M1 — weeks 1–2 (1–14 Sep): run the settling experiment and let it decide L3.** E5 then E6. Also the
open-weight comparison, run as *admitted predicates per rupee* and *admitted per 100 candidates* on an
identical prompt set — converting an unanswerable question into a measurable one; **the gate adjudicates
every candidate deterministically, so model choice affects yield, never correctness.** **Acceptance:**
`experiments/9.1/` contains inputs, every candidate including discards, the five-gate attrition funnel,
the Wilson interval, the per-stratum split, the marginal kill over each baseline **separately**, `U/G`,
both attrition numbers from DECISION E6.2, and a dated `DECISION.md`. **Failure is a valid, funded
outcome — say so to the mentors in week 1 so the result cannot be renegotiated in week 6.**

**M2 — weeks 2–4 (8–28 Sep): the corpus and its declared weakness.** E8's blind-fill firewall, with a
predicate-free fill prompt **hashed and published before the first workbook is filled** if a second model
instance acts as Person A. Build the three corpus-free oracles: template-computed, register-derived,
cross-format. Publish a **per-template** settled-fraction table — embarrassing for `EDR_1` (zero
formulas) and `IFSCA_Annual_Reporting_Format` (zero formulas *and* zero validations, so mechanically
derivable settled fraction 0%). Publish it anyway; **the settled fraction is a per-template property and
must never be averaged across templates.** **Acceptance:** a test fails the build if any FFR renders
without corpus provenance and `n`, and a second asserts `SELF-AUTHORED` renders `uninformative` rather
than a number. *Discipline that is not mechanised does not survive week 6.*

**M3 — weeks 4–6 (22 Sep – 12 Oct): qualification as a product.** Harden all five gates; reimplement the
selection ILP with the sub-additivity bound and the subsumption DAG in ~40 lines of PuLP/CBC (**the SPADE
repo is 17★, 1 fork, no licence field, last push 2024-04-07 — under GitHub's terms, all rights
reserved**). Qualification records: `qualified_against{template_sha, regulation_version,
circular_corpus_snapshot, circulars_unreadable, corpus_id, corpus_provenance, n}`, plus the model id,
date and prompt hash used to synthesise each predicate, so a re-synthesis under a drifted model is a diff
rather than a mystery. Ship the `PROVISIONAL` state and the instrument-stream watcher (daily content-hash
of IFSCA's circular and Authority-meeting pages). **Publish `pervasiveness-policy-v1.json` with the
argument that sets `K` and `T`; until that argument exists both render `PLACEHOLDER` in every example and
in the attestation.** **Acceptance (three tests):** a predicate with an unknown error rate cannot be
admitted; bumping the template hash moves affected predicates to `PROVISIONAL`, hides their numbers and
makes **the settled fraction fall**; a predicate whose stored kill-case stops dying is quarantined
automatically.

**M4 — weeks 6–8 (6–24 Oct): the residue set and the relations.** E7, the publishable component, and E9
— including the four-way funds-raised partition, the highest-value relation in the design and not in the
brief: the workbook reports funds raised by investor category, by country, by accreditation status and
via the Summary carry, and **enforces agreement between none of them** — Tables 4.2 and 4.3 contain zero
formulas (MEASURED). **Acceptance:** publish the before/after settled-count delta naming the relation
that moved each item; a relation that moves nothing is reported as moving nothing; publish the residue
set's size, fault-model version, **adjudication-record hash**, and at least one **demonstrated survivor**
rendered in the Unchecked panel.

**M5 — weeks 8–8.5 (20–30 Oct): attestation, reproduction, demo-day artifact.** The scope-only schema
(no `result` or `status` field exists to write a pass into), DSSE + in-toto statement (**Apache-2.0,
VERIFIED-AT-SOURCE — the LICENSE was opened and quoted verbatim**), **detached key signing rather than
keyless**, because a keyless signature puts the fact that a named FME ran a pre-submission check into a
permanent public transparency log. **Acceptance:** a third party clones the repo, runs
`verify <report.html>`, and gets a byte-identical re-derivation on a different machine. **If it does not
reproduce, it does not ship.**

**Funding.** ₹1,00,000 in five objectively checkable tranches, so no tranche can be argued: M1 =
experiment run and decision recorded · M2 = corpus published with mechanised provenance strings · M3 =
the gate provably rejects unmeasured predicates and the settled fraction provably falls on version churn
· M4 = before/after delta and residue set published · M5 = third-party reproduction succeeds.

**Model cost (MODELED, arithmetic shown; this model family produces ~30% more tokens for the same text,
so re-baseline with `count_tokens` before quoting).** L3 runs **once per template version, not per
filing**: ≈$0.55 per template version, **under $6 for the entire nine-template corpus**. Document
extraction is needed only for unstructured attachments; the annual bill for all ~868 modelled filings is
**under $200** even routing every attachment through the frontier model. **Marginal model cost per filing
on the workbook path: $0.00.** Deployment: one container, 512 MB ≈ **$3.32/month** (VERIFIED-AT-SOURCE;
new accounts get no free allowance). *The expensive input is not inference. It is the human-built
blind-filled corpus, and no amount of model spend substitutes for it.*

---

## 3. THE DO-NOT-BUILD LIST

Ranked by how likely each is to be built anyway.

| # | Do not build | Reason |
|---|---|---|
| 1 | **An agent loop, cross-step memory, or retry-until-it-passes** | `pass^k` collapses ~60% → ~25% over 8 attempts on **τ-retail (n = 115)**; τ-airline never reaches 60% even at k = 1; `0.9⁸ = 0.4305`. **The model appears exactly twice in this design, both offline** — proposing candidates a deterministic gate then rejects, and reading attachments a deterministic schema then constrains. *If a demo needs an agent to be impressive, the demo is wrong* |
| 2 | **A green tick, an "all clear", or a PASS summary badge** | The single design commitment, mechanised twice: a build-time grep **and** a schema with no `result`, `status` or `pass` property at any depth, so there is nowhere for a downstream consumer to read one. Schema-level prohibition survives the screenshot, the API integration and the intern; copy discipline does not |
| 3 | **A settled-fraction percentage as the hero number** | 71% → 98.8% in one afternoon under a different enumeration of the same file. Two counts, equal weight, same ink, side by side — and **100% must be structurally unreachable**, because the denominator permanently contains the not-settleable-from-the-artifact rows and the residue count, which is never zero |
| 4 | **A denominator derived from the predicate set** | Committed twice in one afternoon by the person hunting for it; the first coverage figure produced in this research was 99.2% and circular. The honest denominator is the unlocked-cell field surface from `styles.xml`; assert its provenance in a test and compute it twice |
| 5 | **`openpyxl` anywhere in the schema-induction path — ever** | Sees 35 of 54 validations, blanks the AML-CFT sheet, and its round-trip destroys the file: **3,663,391 → 65,877 bytes**, 24 parts deleted including a 3.55 MB data model that is 96.9% of the workbook (MEASURED). Convenience reads and mutant writing only |
| 6 | **`mutmut` / PIT / Stryker for the seeded-defect harness** | Category error: they mutate *source code* and ask whether *your tests* fail; we mutate *data* and ask whether *the predicate set* fails. Subject, mutant and denominator all differ. ~200 lines of our own at 7,946 mutants/second. They **are** right one level up — for mutating our host functions and our schema inducer, which is where the silent failures live |
| 7 | **A model as judge anywhere in the verdict path** | LLM judges detect false success at AUROC ≤ 0.65 with 13% recall at a 10% flag rate. *Where a programmatic oracle exists we do not need a model; where it does not, we manufacture labels by seeding faults rather than by asking one* |
| 8 | **A NAV recomputation engine, or NAV-per-unit in any data model** | Whole-word `NAV` occurs **0 times** across all nine prescribed workbooks in every XML part (MEASURED, positive controls passing). No NAV per unit, no units outstanding, no dealing price, no dealing date — and every NAV-error rule on earth operates on exactly those. **You cannot build a NAV-error checker for an artefact that does not contain a NAV.** What the return *does* carry is fund-level net assets and gross subscription/redemption flows, which is why the flow-identity predicates survive and the wedge does not |
| 9 | **A valuation-error materiality regime as the pitch** | You cannot ship a policy. Ireland — second-largest fund domicile — still has none as of S.I. 316 of 2026 (VERIFIED-AT-SOURCE); the set of jurisdictions with a prescribed regime is roughly {Luxembourg, UK} and they disagree with each other. "IFSCA lacks this" is the majority position, not a scandal. What survives: **CSSF 24/856 as the prior art for coverage declaration**, and valuation staleness against regs 27(1)/39(1)/51(1) as a predicate. **The Luxembourg 1.72% may never be imported as an FFR prior** — comparator for the pitch, input to nothing |
| 10 | **The brief's five metamorphic relations** | Four false-alarm on a correct filing as written; the fifth is vacuous because guidance mandates per-transaction historical rates. And metamorphic testing needs a re-executable system under test; a filed workbook is a record. Deleted — **do not restore**. Build differential probes over the workbook-as-program instead |
| 11 | **The supervisor as a user or a buyer** | Deleted. The supervisory system is procured; the buyer is the filer's compliance officer. **The supervisor is not the buyer; the supervisor is why the filer cares.** Where a surface happens to suit a supervisor, call that reader *a downstream reviewer*; do not frame the product as having "two surfaces" |
| 12 | **A queue, Redis, Celery, a worker pool** | The job is ~30 ms; the whole 19,782-mutant campaign is 2.5 s. Offline batches go to the Batch API plus a Makefile |
| 13 | **Postgres, an ORM, migrations** | Single writer, dataset well under 10 MB. **SQLite is a file, so it can be hashed and named in the run manifest** — exactly what the attestation needs. A Postgres cluster cannot be content-addressed |
| 14 | **React, Next.js, any component library** | It becomes the project. The deliverable is a *file*: it survives the venue, renders on a phone, is emailable, and is the only form of the report that can be hashed and signed. An architectural argument, not a preference |
| 15 | **Auth, multi-tenancy, user accounts** before 30 October | Judges will not sign up, and each adds a failure mode to a system whose demo must run offline from a file |
| 16 | **Rebuilding Great Expectations / pandera / Soda Core / dbt / Deequ** | They are the check-library substrate. But **none has a third verdict value** (Great Expectations actively converts *could-not-check* into *failed*), and **Soda Core is Elastic License 2.0**, unembeddable in a hosted product. *The check library need not be rebuilt; the verdict model must be, because it does not exist anywhere in the ecosystem* |
| 17 | **A rules-as-code framework** (Catala, OpenFisca, Blawx) | 16★, no commit since 5 Jun 2024, and the field's own diagnosis is that they *"require manual predicate engineering and detach from source"*. And do not repeat the refuted absence claim about executable financial rules: ≈**14,819 distinct** EU supervisory rules exist like-for-like; the mixed-unit sum is never quotable |
| 18 | **`bluebell`; and `cobalt` until someone opens its LICENSE** | `bluebell` is **GPL-3.0, confirmed**, and must never be linked. GitHub reports `NOASSERTION` for `cobalt`/`indigo` and no lane opened the LICENSE files. **Implement the FRBR URI grammar ourselves, ~100 lines**; adopt `cobalt` only if its LICENSE is opened and permissive |
| 19 | **An FFR without its corpus provenance, `n` and interval** | Enforced by a failing test, not by remembering. `0 fires / 340 self-authored` and `0 fires / 4 real` must not look alike: the Wilson intervals are `[0.000, 0.011]` and `[0.000, 0.490]` |
| 20 | **Keyless signing for filer-side attestations** | The signing identity lands in a permanent public transparency log; the fact that a named FME ran a pre-submission check becomes world-readable and correlatable. Detached key signing; a private log only if the supervisor operates it |
| 21 | **Any predicate whose validity depends on a range being protected, or on a vocabulary read from the filed artifact** | `sheetProtection` is an application-level flag with a SHA-512 hash, not encryption — every byte is readable and a filer can strip it with a zip edit. The `Dropdown` sheet holding the controlled vocabularies is **hidden and the only unprotected sheet**. Pin vocabularies from the blank template's content hash |
| 22 | **The ESEF conformance suite as a free benchmark** | A 68-row index whose test-case cells contain free-text English descriptions — no valid/invalid flag, no expected-error-code column. It **names** 212 test cases in an archive nobody in this corpus has opened. Candidate corpus, not a benchmark |
| 23 | **Anything that repairs the artifact** | Deterministic ledger feedback pushed models to *reconcile* contradictory documents rather than report them, costing 13–52 pp on inconsistency detection while gaining 30–33 pp on the primary task. **L5 must never repair. It adjudicates and reports** |
| 24 | **A hosted spreadsheet cell store on the verdict path** | The Grist "Cellbreak" escape (`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1) is why the verdict path evaluates a terminating expression language in-process over a flat fact table. The advisory ID carries the fact; do not quote a date and a verb the drafts disagree on |

---

## 4. WHAT THE FINAL PROTOTYPE DELIVERS

### 4.1 The demo script — four minutes, wifi off, laptop only

The deployed URL is for judges who read the application. **The demo runs from disk.**

| # | On screen | What the operator says |
|---|---|---|
| 0 | Terminal: `openpyxl` against the regulator's published workbook printing `AML-CFT: 0 data validations`; then the raw OOXML parse printing `AML-CFT: 5` | *"This is the standard Python spreadsheet library, reading the regulator's own published reporting format. It says the anti-money-laundering sheet has no validation rules. It has five. No error, no warning — a clean, confident, well-formed wrong answer. It is not that machines can't find errors. It is that when they find nothing, you learn nothing."* |
| 1 | Drop screen, one control. Drag the FME quarterly return as published on `ifsca.gov.in`, `sha256 7d9a1960085785ee…`, filled, with one deliberately corrupted cell | *"This is the real prescribed quarterly return for a GIFT City fund manager. Two hundred and seventeen of them file it. I have filled it and broken exactly one cell."* |
| 2 | Report renders in under a second. Hero: **two counts of equal weight, same type size, same ink, no colour on either** — `1 failure across 2,373 checks` and `1,374 fields were not checked` — with `predicate set: PRE-GATE` and the 280-predicate strap line in the same block, never in the hero. A hatched stacked band below. **No percentage in the hero, no ring, no green** | *"First: there is no green tick in this product and there never will be. A surface that can say 'all clear' will eventually say it wrongly, and nothing in the output would tell you which time. Second, and this is the part you should push on —* **280 predicates are mechanically derivable from the regulator's blank template with no model, and they touch 2,373 of 3,747 filer-editable cells. None of them is admitted yet, because no one has measured a false-failure rate for them on a corpus we did not write. That is the point: the number you are looking at is what every compliance product ships, and it is the number our own gate is designed to refuse. Watch what happens to it after qualification — that delta is the product.**" |
| 3 | Expand the single FAIL: both cells — the corrupted one and the one it disagrees with — the clause with its `eId`, the check's kill vector by fault class, and its FFR with its Wilson interval **and the words** *"measured on 34 blind-filled workbooks; not a measurement of real filings"* | *"Every check here carries how often it cries wolf, measured, with the corpus it was measured on and how big that corpus was. No compliance product tells you that, and neither does any auditing standard — the profession's most coverage-honest report form expressly disclaims any representation about whether the procedures were the right ones."* |
| 4 | The **Unchecked panel**: 1,374 fields grouped by reason from the closed thirty-code vocabulary. Point at `no_predicate.requires_judgment` — *is the disclosed valuation appropriate (Third Schedule Part A(g), p.90)* — and read the "what would make this checkable" text | *"This panel is the product. Not the failure — the panel. It says what could not be settled, why, and exactly what instrument would move each one across the line: a materiality threshold by scheme class of the kind CSSF Circular 24/856 Tables 1–3 specify — 0.20% money-market, 0.50% bond and mixed, 1.00% equity and other — plus a compensation-direction rule of the kind its Tables 4–5 specify. One regulator in the world publishes, in advance, what it will and will not treat as a finding, then publishes the resulting rate annually. We compute the equivalent per filing, for a jurisdiction that has neither."* |
| 5 | The **predicate library**: 280 rows. Filter to the five ALR bounds the gate **rejected** for asserting only `−100000000000000000` over 1,428 cells. Show one obligation's five-gate attrition funnel: generated → executed and bound → non-degenerate → killed a seeded defect and beat the baselines → FFR-admitted. Beside each rule, what a flag-everything rule would have scored | *"A check whose error rate we could not measure is not in this list. Here is what the gate threw away — including five rules the regulator's own template ships that assert only 'this is a number'. That is one demonstrated rejection, on one workbook, on one predicate class. Whether the gate rejects anything on this workbook is unmeasured: 19 of its 24 bounds are a real 'greater than or equal to zero'. I am telling you the size of my own evidence."* |
| 6 | `demo --break-parser` renames a sheet. The report returns **`INVALID`**, naming the predicates that failed to fire on faults they are known to detect, and showing **no settled fraction of any kind** | *"No assurance artifact in existence carries evidence that the instrument that produced it was working on the specific document it examined. A clean audit opinion does not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict unless every check has just demonstrated, on your file, that it can still catch the fault it was admitted for."* |
| 7 | The **residue** row of the Unchecked panel: a demonstrated survivor — a coordinated misstatement propagated through all 181 cross-sheet carries and all 35 SUM identities, which every admitted check passes | *"A prescribed return is a closed arithmetic system. We can construct, and exhibit, a family of filings that are internally perfect under every relation the regulator's own template encodes and every relation we have added — and materially false. That family is non-empty by construction, its size is measurable, and measuring it is the first quantitative statement anyone has made about the limit of document-level verification for a regulated filing. In code, a mutant that changes behaviour is in principle killable by some test. Here, a mutant can change the truth of the artifact and be provably unkillable by any predicate over the artifact alone."* |
| 8 | Terminal: `verify report.html` → byte-identical re-derivation. Then, in Excel, type `Special Situation Fund` into `'1. Introduction'!G54` and show `D17` — *"Total No. of Schemes of the FME authorised by IFSCA"* — failing to increment | *"Two facts. Not one model was called in anything you just saw. And the regulator's own workbook computes its own scheme total with three COUNTIFs that between them miss two of the nine scheme types its own validation permits. You can check that yourself in thirty seconds. That is the class of confident, well-formed, wrong answer this exists to make impossible to give."* |

**Why step 2 is the strongest moment and not the fatal objection.** A judge who connects the admission
gate to the headline gets to say the product failed its own test on stage — unless we say it first. The
composition makes it sharper: **2,329 of the 2,373 settled cells (98.1%) come from the 53 validation
predicates and only 271 from the 227 arithmetic ones**, and the validation-carried cells are weaker per
cell — some are near-vacuous, which is precisely what G3 exists to reject. The pre-gate number is the
industry's number, displayed with the label the industry does not print.

**Two lines that stay on the report surface permanently.** The honest limit: *"This system detects error,
not deception. Every check here is a consistency check over a self-reported document. A coherent liar
passes all of them."* And the claim about the criterion source, which no other section states as a
novelty: *SPADE infers what correctness meant from the traces of a developer changing their mind. We do
not have to infer it — the criterion is a published instrument with a version, an amendment chain that is
machine-followable in 76 of 82 cases, and a blank template with a content hash. The criterion source is
not more* authoritative *than SPADE's — the regulator's own template computes a scheme total that misses
two of its own nine legal values — it is* **citable, versionable and watchable**, *which is what lets a
predicate be tied to a clause, re-qualified when the clause moves, and quarantined the day a circular
changes the rule.* That is what the instrument-stream watcher implements.

### 4.2 The acceptance criteria that make the demo honest

Each is a **test in CI**, not a value. A design commitment that is not tested is a preference.

| # | Criterion | Enforcement |
|---|---|---|
| A1 | No all-clear glyph or phrase reaches a user-facing surface | `ci/no-green-tick.sh` greps `src/ templates/ locales/` and exits non-zero |
| A2 | The attestation cannot express a pass | JSON Schema: top-level object is `scope`; no `result`, `status` or `pass` at any depth; additional properties rejected |
| A3 | The denominator is not derived from the predicate set | Asserted structurally against the `styles.xml` unlocked mask, and recomputed by a second independent code path; disagreement ⇒ `INVALID` |
| A4 | No FFR renders without provenance and `n` | Render a `SELF-AUTHORED` predicate; assert the output contains `uninformative` and no digits |
| A5 | No predicate binding to zero cells returns PASS | `cells_bound == 0 ⇒ ERROR(cells_bound_zero)`, run state ⇒ `INVALID` |
| A6 | Zero model calls in the verdict path | Static check: no import of the model client reachable from L5/L6/L7, plus a run with the network namespace closed. **Not yet written — this is the gate that turns a design property into a system property** |
| A7 | The report re-derives byte-identically on another machine | `verify` in CI on a second runner image, toolchain pinned per §6 G12 |
| A8 | The settled fraction can fall | Bump the template hash; assert affected predicates go `PROVISIONAL`, their numbers hide, and the settled count decreases |
| A9 | Every seeded-defect number is `K/O` with both integers plus `U/G` | The renderer refuses a bare percentage |
| A10 | The demo runs offline | Report opens from `file://` with wifi off; the register is read from its content-addressed snapshot, never live |
| A11 | **No settled count renders without the admission state of the predicate set that produced it** | Render from an unqualified set; assert `PRE-GATE` appears in the same block as the count. The mechanised form of step 2 |
| A12 | Closure | `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface`, over cells, or report generation aborts |
| A13 | Error absorption cannot manufacture a pass | A predicate written `true \|\| <unreadable>` returns `NOT_RUN`, never `PASS` |
| A14 | The two readers must agree | Readers A and B disagree on a crafted fixture ⇒ `INVALID`, loudly |
| A15 | The received filing is never re-serialised | No code path writes the artifact back |

### 4.3 Every number on screen, and where each comes from

| Number | Value | Warrant | Denominator / provenance |
|---|---|---|---|
| Fields settled | **2,373** | MEASURED | Union of the 280 harvested predicates over the field surface. **Pre-gate** until E8 and the gate run |
| Fields not checked | **1,374** | MEASURED | `3,747 − 2,373` |
| Field surface | **3,747** | MEASURED | Unlocked, non-formula cells from `styles.xml` `cellXfs → <protection locked="0"/>`; 105 unlocked style ids; 9 of 10 sheets protected. Per sheet: Portfolio 1,698 · Investors 897 · PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22 |
| Settled fraction (subordinate, never the hero) | **63.3%** | DERIVED | `2,373 / 3,747`; per-template, never averaged; always carries the admission state |
| Composition of the settled count | **2,329 of 2,373 (98.1%) from 53 validation predicates; 271 cells from 227 arithmetic predicates** | MEASURED | A union, so the two do not sum. Validation-carried cells are weaker per cell |
| Checks in the active set | **280** (FME) · **515** (all nine, **always with the per-workbook distribution attached**) | MEASURED | From the blank template's own OOXML: 181 cross-sheet equalities, 35 SUM identities, 20 membership, 13 numeric bounds, 11 integer bounds, 11 same-sheet equalities, 6 date bounds, 3 tallies |
| Formula-bearing cells | **505** (294 authored expressions, 211 shared-formula dependents) | MEASURED | Two true statements about different quantities; state which |
| Data validations | **54** (35 main-namespace + 19 `x14`), **22** list-type, **20** resolving | MEASURED | Replaces the brief's 35 / 3 |
| Run time | **~30 ms** | MEASURED | L1 28–44 ms + synthesis 1 ms + evaluation sub-ms, cold, single process |
| Seeded-defect campaign | **19,782 mutants, 2.5 s, 7,946/s** | MEASURED | 2,826 sites × 7 numeric operators; the kill rate is always `K/O` with both integers and `U/G` |
| Register identity FFR | **38.2% (87 of 228)** | MEASURED | 228 of 229 live FMEs, detail endpoint, 10 Aug 2026: 141 legacy `IFSCA/FME/<I\|II\|III>/<FY>/<n>`, 84 new `FDM<YYYY><AAA><NNNN>`, 3 neither — one carrying `U+2011 NON-BREAKING HYPHEN`, byte-different and invisible in any screenshot. `REGISTER-DERIVED`, so no synthetic caveat applies |
| Register fetch plan | **1 list request + N detail requests, N = \|records\|** | MEASURED (form) | The actual request count of the run that produced the snapshot hash is recorded in the manifest. **IFSCA's terms of use for the register API have not been read — a gap in conduct, and it must be read before any scheduled polling** |
| Population | **217 FMEs, 360 schemes** as at the Q4 FY2025-26 bulletin; **650 Fund Management register rows as at 10 Aug 2026, of which 229 resolve as live FME registrations** | VERIFIED-AT-SOURCE / MEASURED | **Never blend the two denominators in one sentence.** No scheme count is published from the register until the split rule is written down |
| Filings per year | **~868** | MODELED | `217 × 4`, assuming every FME files every quarter including those registered mid-year. Labelled on screen |
| Per-filing model cost | **$0.00** | DERIVED | The workbook path calls no model |
| The enumeration illustration | **505 + 54 + 15 = 574**, and `574 / 581 = 98.8%` | DERIVED — an enumeration argument, not a run | Shown only to demonstrate that a fraction is manipulable by re-enumeration. Never a hero number, never a coverage claim |

The **unit of value — the avoided deficiency** (the inspection observation, the rework, the Principal
Officer's personal exposure) — is **UNMEASURED, and the screen says so.** E1 is how that changes. And the
canonical illustration of the reason code `.external_source_lacks_field` is our own near-miss, which is
an illustration and **not an instance**: the register's **list** endpoint returns `RegistrationNumber =
null` on 650 of 650 rows while its **detail** endpoint returns it on 228 of 228.

### 4.4 The sentence a judge should be able to repeat

> **"They built the compliance checker that tells you what it did *not* check — every rule carries its
> own measured error rate, and the report proves the checks were alive on *your* document."**

If only half a sentence survives the walk to the next table, the half that must survive is: **"it tells
you what it didn't check."**

---

## 5. THE RISK REGISTER

**P** = probability to 30 Oct 2026. **RETIRED** rows were live risks closed by a measurement.

| # | Risk | P | Blast radius | Early-warning signal | Mitigation | Status |
|---|---|---|---|---|---|---|
| R1 | The application portal is not live, or the form differs from the recorded spec | Low–Med | **The whole programme; no second entry** | WebFetch to `giftifih.getkruu.com/apply` returned HTTP 404; the root served only an SPA shell titled *"KYF Programme"* | E0 first thing on 11 Aug: real browser, screenshot every field, submit a draft early. Rely on no cached spec | **OPEN — highest urgency** |
| R2 | The headline settled fraction is pre-gate, and a judge connects it to our own admission rule | **High — a good judge will raise it** | The credibility of everything else, if we do not say it first | Not a signal, a fact: no FFR has been measured for any of the 280 | Say it first, in the operator's own words at step 2; mechanise it as A11 so no surface can print the number without `PRE-GATE`; publish the delta after M2/M3 | **Mitigated by disclosure — and it becomes the strongest moment in the demo** |
| R3 | L3 does not work | Med (central p ≈ 0.25–0.30) | **L3 only**; predicates become hand-authored, the rest is unaffected | The attrition funnel collapsing at G2 or G3 | Criterion pre-registered before the run; k = 0 is publishable; the baselines already yield 280 predicates with no model | Managed |
| R4 | No labelled clean corpus of real filings exists | High (near-certain) | Every FFR the product displays | Already realised — filed FME returns are not public | Four-tier corpus hierarchy with provenance in the record; blind-fill firewall; template-computed oracle; the register as a real clean corpus for the identity class; Wilson intervals so `n = 4` and `n = 340` cannot look alike | Managed, not solved |
| R5 | Our own silent false negative ships | High if unmitigated | Everything — we would commit the failure we sell against | **Five instances in this corpus**, four in deterministic programs, one committed by the design team while designing; all under-counted in the direction that supports the thesis | Run-time canaries with `INVALID` · dual-parser ingest that fails the run on disagreement · `cells_bound == 0 ⇒ ERROR` · the denominator computed twice · the positive-control rule now written into the pre-registration | Mitigated by design; T1 and T10 sit above the cut line |
| R6 | Version churn silently invalidates a predicate | High | Predicates returning confident verdicts against rules that no longer exist | **Already realised**: the 29th IFSCA Authority Meeting, 24 Jul 2026, lets close-ended Restricted Schemes move NAV computation from semi-annual to annual with 75% investor approval by value — a fact the workbook does not collect — and relaxes independent valuation where the underlying is valued by an independent entity | Qualification records; the `PROVISIONAL` state that keeps detection but hides numbers and leaves the numerator; liveness witnesses; a daily content-hash watcher on the circular and Authority-meeting streams. `reg 51(1)` ends *"in such manner as specified by the Authority"*, so watching the regulation alone is insufficient | **OPEN — M3 deliverable** |
| R7 | The product has no buyer | Med | The product, not the research | E1's answer; the NEC SupTech award (₹39,57,36,115.52, 27 Jan 2026) explicitly scopes an RE-facing portal | E1 joint-first; the supervisor deleted as a user; the unit of value named and labelled UNMEASURED; the workbook named for what it is — the testbed, not the market | Partially retired: the internal contradiction is gone, the demand question is open |
| R8 | The method does not transfer beyond one workbook | Med | The claim to be a product rather than a paper | E4's transfer cost per predicate; two of nine templates have zero formulas, one has zero validations as well | E4 pre-registered with a threshold, runnable today on nine workbooks already on disk; publish per-template settled fractions including the 0% cases | **OPEN — M0 deliverable** |
| R9 | The residue set is empty | **Low → structurally impossible** | Claim N3's second half and the publishable result | E7 returns no surviving WRONG mutants | A coordinated misstatement propagated through all 181 carries and all 35 SUM identities is **provably unkillable by any predicate over the artifact alone**; the class is non-empty by construction and only its size is open | **Structurally retired; the measurement is the deliverable** |
| R10 | A judge knows the prior art we claimed did not exist | Was High | Credibility of everything else | Two absence claims already refuted internally | Both corrected before the application; fifteen prior-art items handed over up front, including the published hypergeometric random-flagger baseline that precedes our degenerate-baseline test, and the paper that proposed an observability interface displaying each constraint's precision and recall a year before this brief did | **RETIRED** |
| R11 | The problem statement's opening sentence is refuted on stage | Was High | The problem statement | A frontier model **was** calibrated on the clean split of the benchmark most cited here | Restated before submission: *a model can be calibrated on 43 clean statements — a set built to satisfy the checks — and nine of fourteen complete frontier runs were not, on the same 43, with nothing in any of the fourteen complete outputs distinguishing the calibrated run from the rest.* The benchmark author's own conclusion, and it points at the gate, the verdict model and the attestation rather than at a capability claim a judge can break by clicking one link | **RETIRED** |
| R12 | The evidence base is more concentrated than it looks | Was High | Five separately-tabulated rows | Five rows and one architecture fact all trace to one 37-page single-author unreviewed preprint with unreleased code and a 43-instance clean split | Add the Warrant column naming the paper so a reader sees the rows are one instrument. Ten minutes, non-negotiable | **RETIRED, action pending — closes 15 Aug** |
| R13 | An absence claim ships with an unreconciled denominator | Med | The central novelty claim, from inside it | The opened-vendor-pages count did not reconcile with its own source tables: two totals, no stated inclusion rule | **No count ships.** Publish the list and a written inclusion rule (`docs/ABSENCE-SCOPE.md`, 11 Aug), then recompute before any absence claim is made | **OPEN — closes 11 Aug** |
| R14 | A negative claim about PROVE is wrong because nobody opened the paper | Med | Novelty claim N3's scope sentence | Only the abstract has been read; the two quantitative facts we use are in it and survive, the absence claims do not | E13 before the pitch. Until then every such claim reads *not visible in the abstract; the full text is unread*. **A coverage table in its implementation section would narrow N3, and better to find that now** | **OPEN — closes before submission** |
| R15 | The conformal guarantee is void, not merely degraded | Was High | That layer's entire justification | Split conformal requires exchangeability; a team-authored calibration set against real filings is a known shift, and quoting a theorem under a violated assumption is worse than a loose FFR | The layer leaves the critical path: **0 of 3,755** unlocked cells are ambiguous under the address key. Build the test martingale — which detects that the guarantee has lapsed and withdraws the claim — before any predictor | **RETIRED** |
| R16 | The relation layer is unbuildable as specified | Was High | The layer the design leaned on hardest | No re-executable system under test; `NAV` absent from all nine workbooks | Rescoped to differential and invariant probing over the workbook-as-program (505 recomputable cells with cached baselines), routed through the same five gates, ceiling stated: **it moves ≈0 of the 7** | **RETIRED** |
| R17 | A licence trap ships inside the product | Med | Distribution | `formulas` is EUPL 1.1+; `pycel` GPL-3.0; CheckCell/DataDebug GPL-2.0; Soda Core Elastic 2.0; `bluebell` GPL-3.0; the SPADE repo has no licence field; FINOS CDM is Community Specification License 1.0, *"not intended for source code"*; the DQC ruleset *"may not be modified in any way"*; FUSE is CC BY 4.0 | A licence gate in CI over the dependency tree before any hosted deployment; reimplement the ILP rather than importing it. **Open the LICENSE files still unread: Z3 (MIT, SECONDARY), Hypothesis (reported MPL-2.0, SECONDARY, LICENSE not re-read), gVisor (not opened), `cobalt`/`indigo` (`NOASSERTION`), `xbrl.us/dqc-license`. in-toto/DSSE is settled: Apache-2.0, VERIFIED-AT-SOURCE** | **OPEN** |
| R18 | The normalisation step loses data | Med | The fix adopted to prevent silent loss | Measured: `soffice` writes **53** main-namespace validations where 35 + 19 = 54 | E11 with the Excel value-agreement positive control **before any kill rate is quoted**; until then normalise for analysis only and content-address the artifact as delivered for signing; and per §6 G12 LibreOffice is excluded from the verdict path | **OPEN — E11** |
| R19 | Frontier-model drift moves a measured result under a fixed alias | Med | Any quoted L3 yield | Documented: a failure cell moved from 96.6% to 100% on the same prompt and harness under the same alias, with no version bump | The attestation signs the model identifier, the date and the prompt hash used to synthesise each predicate, so re-synthesis is a diff rather than a mystery | Mitigated |
| R20 | The attestation's signer | Med | Legal exposure — if an FME shows an inspector a signed attestation over a filing that was wrong, the signature is the first exhibit | Not a signal; it is decided | **Decided: the filer signs with a detached key over the report JSON; the vendor signs nothing and appears only as `assessor.id` with `thirdParty: false`.** The residual item is legal review of that decision, not the decision | **DECIDED, pending legal review** |
| R21 | A stray demo dependency on the network | Low | Demo day | Any external fetch in the report | A10; a single self-contained file; the register read from its content-addressed snapshot | Mitigated |
| R22 | Team bandwidth — two days plus eight and a half weeks, four people maximum | Med | Scope | The cut line being crossed | The hard cut line; the do-not-build list; the owner map (§6 G11); and the reallocation the research made possible — the parser is done, so the scarce resource goes to the honesty machinery | Managed |

---

## 6. THE TWELVE BLOCKING GAPS — EACH DECIDED, OR EXPLICITLY OPEN

| # | Gap | Resolution |
|---|---|---|
| **G1** | The unit of the denominator: cells or (field × obligation) pairs? | **DECIDED: the unit is the CELL.** The denominator is the 3,747-cell field surface; closure (A12) is over cells; "obligation" becomes an attribute of a predicate, not a dimension of the denominator. **`obligationsTotal` and `pairsTotal` are deleted from every schema, example and screen**, along with the two numbers the drafts carried for them — copied from an illustrative block and never derived. *Reason:* every measurement in this corpus is a cell count, nobody has published a rule enumerating obligations, and a denominator with no derivation cannot be the thing a signed coverage claim is a fraction of |
| **G2** | What FFR makes a predicate `ADVISORY` rather than `BLOCKING`? | **DECIDED and pre-registered with the admission thresholds: `FFR ≤ 0.02 ⇒ BLOCKING · 0.02 < FFR ≤ 0.10 ⇒ ADVISORY · FFR > 0.10 ⇒ not admitted`. The number compared is the Wilson *upper bound*, not the point estimate**, so a small corpus cannot buy a BLOCKING tier — `0 fires / 4` has an upper bound of 0.490 and falls outside admission entirely. *Reason:* any defensible number beats none, and the upper bound makes the tier a statement about evidence rather than about luck |
| **G3** | Money scale | **DECIDED: `MILLI_USD_MILLION`, an `int64` count of 10⁻³ USD Million (1 unit = USD 1,000); `12.34 → 12340`; half-ulp 5 units; `τ(n) = 5n`.** The phrase "integer micro-units" is deleted everywhere, including from the `Field.unit` enum. *Reason:* the drafts differed by 10³ and every tolerance is expressed in units |
| **G4** | The state and reason vocabulary is not one vocabulary | **DECIDED: eight states × thirty reason codes, frozen and normative.** States: `PASS · FAIL · INDETERMINATE · NOT_RUN · NO_PREDICATE · ERROR · OUT_OF_SCOPE · INFORMATIONAL`; the first six are in the settled denominator and any `ERROR` sets the run state to `INVALID`. Thirty codes across five state families, and a code is admitted only if it implies a **different remedy** from every existing code. Schema, build plan and architecture are regenerated from this one source, and the mapping table from the brief's six original codes to the thirty ships with it |
| **G5** | Where the evaluation contract lives | **DECIDED: one file, `EVALUATION-CONTRACT.md`, generated from §II.3.4 and the only place the contract appears.** Its five rules are **(1) `applicable` · (2) pre-flight · (3) `expr` · (4) warrant composition · (5) `cells_bound`** — the same five as §II.3.4 and §III.3.1, because a CI test asserts the evaluator's transition table equals that file and a build cannot satisfy two different fives. The three rulings the drafts disagreed about sit inside rules 1, 3 and 5 and are resolved as: `applicable == false ⇒ OUT_OF_SCOPE(P.reason_if_inapplicable)` from the `out_of_scope.*` family, **never PASS**, with the token `UNCHECKED` appearing nowhere in any state or reason name; a runtime error inside `expr` ⇒ `ERROR(predicate_raised)` and the run becomes `INVALID`, while `NOT_RUN(source_unreadable)` is reserved for inputs that could not be read; and `cells_bound == 0 ⇒ ERROR(cells_bound_zero)`, run `INVALID`. Budget exhaustion is a sub-case of rule 2 and emits `NOT_RUN` with a code from the frozen thirty. *Reason:* three drafts gave three answers to rules 1, 3 and 5, and a fourth enumerated a different five rules entirely |
| **G6** | How an obligation binds to a field | **DECIDED: report items are keyed by the cell — `cell_id = stable_key`** (§II.3.1), with each item carrying its per-predicate `evaluations[]`. The obligation travels as a predicate attribute — `clause{eId, span}` — resolved through a **hand-maintained `obligations.yaml`** until the clause-graph layer exists. That layer is entirely unbuilt, so the hand-maintained table is the honest day-one answer. The composite key of the form `"…scheme_type × reg27(1)"` is withdrawn: nothing constructs that join |
| **G7** | Gate order and ownership | **DECIDED: G0 (free) → G1 (free) → G3 proof arm (cheap) → G2 (expensive) → G3 empirical arm → G4.** Written once, in the pre-registration file; the harness is a pipeline in that order |
| **G8** | `test_constants` pins numbers two documents disagree about | **DECIDED: split it.** `test_schema_constants` pins 505 / 294 / 211 / 54 / 22 / 20 / 252 / 3,747 — properties of the file, where a change is a parser regression. `test_harvest_count` pins 280 / 515 — a property of our code, allowed to move **with a recorded reason**, because the first thing the gate does is reject predicates. *Reason:* a regression test that fails on correct behaviour gets deleted |
| **G9** | Repo licence | **DECIDED: Apache-2.0, created 11 Aug.** It carries a patent grant and every core dependency chosen is compatible |
| **G10** | Who is Person A? | **OPEN — USER DECISION (§7 Q3).** *Exact question: "Is there a named person, not on the build team, who will fill ≥30 FME workbooks from the template and regulation alone, having never seen the predicate set?"* **Deadline 25 Aug.** Decided fallback, firing automatically at 18:00 on 25 Aug if unanswered: the audited second-model-instance route, with a predicate-free fill prompt hashed and published **before the first workbook is filled**. The fallback is weaker than a human and the record will say so |
| **G11** | The residency plan has no owner map | **DECIDED as to form and deadline: `docs/OWNERS.md`, one table — milestone × person × hours — committed by 25 Aug, covering M0–M5 and all twelve human-required decision points.** Names come from §7 Q3. M2 (corpus) and M4 (residue adjudication) are human-time-bound rather than compute-bound and the table must show that |
| **G12** | `verify` byte-identity against an unpinned toolchain | **DECIDED: LibreOffice is excluded from the verdict path entirely.** It is a cross-check and an offline recalculation engine for the observability filter, so the exclusion costs nothing. Where it is used offline it is pinned **by container digest**, and its output never enters a signed report. *Reason:* the programme's acceptance test is byte-identical re-derivation on another machine, and the one subprocess in the stack has a measured, uncharacterised one-validation loss |

---

## 7. THE SEVEN QUESTIONS ONLY THE USER CAN ANSWER

Ordered by deadline. The first costs ten minutes and is the only one that can end the programme.

| # | Question | Deadline | What changes with the answer |
|---|---|---|---|
| **Q1** | **Is the application portal live, and does the form match the recorded spec?** Open `giftifih.getkruu.com/apply` in a real browser and screenshot every field. WebFetch returned **HTTP 404** and the root served only an SPA shell; nobody in this corpus has seen the live form. Applications close **16 Aug** | **11 Aug, morning** | *Live and matching* → the plan runs as written. *Live but different* → the ~1,100-word field spec is rewritten the same day, before prose is drafted against caps that do not exist. *Not live* → **the programme is over and everything after this line is moot.** Ten minutes against a zero-slack plan |
| **Q2** | **Do you want the E1 email sent, and from whom?** *"Does IFSCA already run these checks on receipt, and how often is an FME filing returned for correction?"* It needs a named sender and a reply address | **11 Aug** | *Yes, they validate on receipt* → the entity-facing product is reclassified as a convenience **in the application text**, and the research result — the residue set and the measured boundary — becomes the pitch. *No* → the gap claim is evidenced rather than assumed. *No reply by 1 Sep* → it ships as an open question in the risk register, which is worse than either answer |
| **Q3** | **Who is on the team, and is anyone eligible to be Person A?** Person A must fill ≥30 workbooks having never seen the predicate set; the team is ≤4 people, all of whom have. Also settles the under-29 and Indian-institution eligibility test and the names in `docs/OWNERS.md` | **Team: 12 Aug. Person A: 25 Aug** | *A named human* → every FFR in the product is `BLIND-FILLED` and means something. *Nobody* → the decided fallback fires (§6 G10), the corpus is second-model-instance, and that must be labelled wherever an FFR renders. **Without one of the two, the product has no admissible predicate at all** |
| **Q4** | **Are you willing to submit on 15 Aug rather than 16 Aug?** | **12 Aug** | *Yes* → one day of slack against a portal that returned 404, at the cost of one day of README polish. *No* → the plan has zero slack and a portal failure on the morning of the 16th ends the programme. This is the cheapest risk reduction available |
| **Q5** | **Does a fund administrator serving GIFT IFSC (KFin / CAMS / Basiz) have a written house NAV tolerance?** Scheduled as E1b in M0 with its exact question text (§1.2); the user decision is whether to spend the call and who makes it | **23 Aug** | *Yes, written* → the problem statement improves: *the threshold is private, uncomparable across administrators, and invisible to the supervisor.* One paragraph of the pitch changes. *No* → nothing changes. **Either way it is no longer a killer** — the valuation wedge was deleted for five independent measured reasons and this question was demoted with it |
| **Q6** | **If E6 returns k = 0, do you still want to run the residency as specified?** | **31 Aug, before M1 starts — not during** | *Yes* → the plan is already written for it: k = 0 is a funded, publishable outcome, predicates become hand-authored from the 294 native expressions and the statute, and the gate, the coverage declaration and the residue set are untouched. *No* → M2–M5 need re-planning **now**, not in week 6, and the mentors need telling in week 1. A commitment made after seeing the result is not a commitment |
| **Q7** | **Is anyone prepared to sign the attestation?** The decision is made — the filer signs, with a detached key — which means a real FME must exist and consent | **20 Oct (M5 gate)** | *Yes, a real FME* → the demo signs a real report and `assessor.thirdParty: false` describes a real relationship. *No* → **the demo signs nothing real and the demo script says so on screen**; the attestation is exercised against a self-filled workbook and labelled a self-assessment exercise. It does not block M5's acceptance test, which is byte-identical re-derivation, not legal effect |

---

**Cross-references.** The problem, the four missing properties and the architecture are in the earlier
parts; the data model, the stack and the flow are in the part preceding this one; this part carries the
experiment queue, the dated plan, the deliverable and everything still open.

**Closing check on discipline.** The plan is written against the standing bias in three concrete places,
and they are the three to check if it drifts. A ten-minute browser check and a twenty-minute email rank
ahead of every engineering experiment, because they are the only two that can tell you the thing is over.
The settling experiment's criterion was **tightened**, not loosened, before the run, from published
reference-class rates — and the arguments that will not be accepted as grounds for changing it again are
hashed into the pre-registration file. And k = 0 is a funded, publishable outcome, shipped on the date it
is taken. If in October the answer is *"the model cannot write a regulator-grade check, and here is the
measured attrition funnel showing exactly where the twenty candidates per obligation died"* — that is the
first such measurement anyone has, the architecture survives it smaller, and the coverage declaration,
the qualification gate and the residue set were never the parts that depended on it.


---

# PART V — AUDIT AND POST-AUDIT RESOLUTIONS

# PART V — AUDIT

**An adversarial check of whether the reconciliation ruling `research/synthesis/D-reconciliation.md`
landed in Parts 0–IV, run 10 August 2026 after the merge. Nothing here is new research. Every grade is
against D's ruled `Replacement:` sentence, not against my own preference.**

**Line numbers in this audit are POST-EDIT.** Seventeen edits were made during the audit; they are
listed with before/after in §V.7. Six of them changed line counts in `02-architecture.md` (+2),
`03-stack.md` (+1) and `04-path.md` (+1); every reference below has been re-resolved against the
current files.

**Scope note.** The brief named Parts I–IV. `00-executive.md` was audited as well, because it ships in
front of them and a divergence there is the most visible kind. Two defects were found in it and fixed.

**Headline counts.**

| Class | Total | LANDED | NOT-LANDED | NEW-DIVERGENCE |
|---|---:|---:|---:|---:|
| Contradictions C1–C31 | 31 | **29** | 0 | **2** (C11, C12) |
| Surviving falsehoods F1–F9 | 9 | **8** | **1** (F8) | 0 |
| Unwarranted confidence U1–U11 | 11 | **11** | 0 | 0 |
| Innovation restorations I1–I3 | 3 | **3** | 0 | 0 |

**All four defects above are now fixed.** What remains open is a separate and more serious class: **six
cross-part semantic divergences that D never ruled on**, three of which cannot be closed without the
owner. They are §V.5. One of them — the cell-state precedence order — changes the value of the
product's headline number.

---

## V.1 — THE 31 CONTRADICTIONS

Grading rule: **LANDED** = D's ruled Replacement is what the spec says. **NOT-LANDED** = the spec says
one of the two losing versions. **NEW-DIVERGENCE** = the spec says a third thing.

| # | Ruled replacement | Grade | Evidence |
|---|---|---|---|
| **C1** | Eight closed item states, first six in the settled denominator, any `ERROR` ⇒ `INVALID` | **LANDED** | `01:376` "Eight closed item states — `PASS`, `FAIL`, `INDETERMINATE`, `NOT_RUN`, `NO_PREDICATE`, `ERROR`, `OUT_OF_SCOPE`, `INFORMATIONAL` — of which the first six are in the settled denominator"; `02:482` the eight-row table; `03:555` verbatim; `04:543` G4 verbatim. Four independent statements, one wording. |
| **C2** | 30 codes, five families, admitted only if a different remedy | **LANDED** | `02:582–635` enumerates 8 + 10 + 4 + 3 + 5 = 30; `03:568` "closed, namespaced and has 30 codes across five state families; a code is admitted only if it implies a different remedy". Family counts reconcile in both parts. |
| **C3** | B's seven-term closure | **LANDED** | `02:516`; `03:562`; `04:463` A12. `02` uses `== cellsTotal`, `03`/`04` use `== fieldSurface`; `02:1008` defines `cellsTotal` as `== fieldSurface`, so this is one equation. |
| **C4** | `applicable == false ⇒ OUT_OF_SCOPE`; `UNCHECKED` nowhere in the contract | **LANDED** | `02:536`, `02:566`, `03:139`, `04:545`. **One leak found and fixed:** `02:866` used `UNCHECKED` as the G3 proof-arm outcome where Part III (`03:41`, `03:261`) says `unproven`. Edit 1. |
| **C5** | `expr` raises ⇒ `ERROR(predicate_raised)`, run `INVALID` | **LANDED** | `02:550`, `02:567`, `03:145–148` with the remedy argument, `04:282` T4, `04:545`. |
| **C6** | `cells_bound == 0 ⇒ ERROR(cells_bound_zero)`, run `INVALID` | **LANDED** | `01:379`; `02:558`; `03:155`; `04:91` and `04:456` A5, both with "never `NOT_RUN`". C's demotion is dead everywhere. |
| **C7** | Declared proviso ⇒ `NO_PREDICATE(no_predicate.not_yet_synthesised)` + verbatim text + span + `provisos_declared` | **LANDED** | `02:570`, `02:572–580` (the cell-denominator interaction), `02:859` G0, `03:253`, `04:90`. |
| **C8** | Nine methods incl. `TEMPLATE_DIFF` + `DIFFERENTIAL`; warrant lattice; `provenance ∈ {COMPUTED, DECLARED}` | **LANDED** | `02:646–651` all three enums; `02:658` deletes the four-value `MEASURED\|MODELED\|ASSERTED\|UNCHECKED` column explicitly; `03:483–486` the SQL matches value-for-value. `METAMORPHIC` survives only in the rename table (`02:16`). |
| **C9** | Six values, spelled `REGISTER-DERIVED` | **LANDED** | `02:650`, `02:668`; `03:463`; `04:103` "The register value is spelled `REGISTER-DERIVED` everywhere". `REAL-REGISTER` appears once, at `02:670`, as the withdrawn third spelling. |
| **C10** | Denominator is the 3,747-cell field surface; pair model unbuilt | **LANDED** | `01:192`; `02:453–464`; `03:410`; `04:540`. `pairsTotal`/`obligationsTotal` appear only in deletion statements. |
| **C11** | Hero is `<F> failures across <S> checks` / `<U> fields were not checked`, from 2,373 / 1,374 / 3,747 | **NEW-DIVERGENCE → fixed** | Correct in `01:201`, `02:1090`, `03:750`. **`04:421` rendered a third form** — `1 failure · 2,373 fields settled across 280 checks` — which puts the predicate count in the hero, the one thing `03:753` forbids ("The predicate count (280) belongs to the strap line and never to the hero"). Edit 13. |
| **C12** | Quantity is the settled fraction; "coverage" reserved for the conformal guarantee; rename key, path and label in one commit | **NEW-DIVERGENCE → fixed** | Landed for the quantity and the API path (`02:14`, `03:11`, `03:731` `/v1/settled-fraction/history`). **Three identifiers were not renamed in Part II** while Part III had renamed them: the verdict enum (`COVERAGE_INSUFFICIENT` / `…WITHIN_STATED_COVERAGE` at `02:511,703,707,710,725` vs `SETTLEMENT_INSUFFICIENT` / `…WITHIN_STATED_SCOPE` at `03:14,129,170,477`), the `predicateType` (`filing-coverage-attestation/v1` vs `filing-settlement-attestation/v1` at `03:59`), and the JSON key `coverageGaps` vs `declaredGaps` (`03:523`). Edits 2, 3, 4. |
| **C13** | 1,692 of 20,562 (8.23%); separately 12,925 → 8,052; do not divide | **LANDED** | `01:697–700`; `01:829` ban row; `04:255`. The 8.23%-of-12,925 pairing occurs nowhere. |
| **C14** | No opened-vendor integer until an inclusion rule exists | **LANDED** | `01:607` "**Neither number is quotable** … the absence claim ships with the list above and no integer"; `01:596` carries the list; `04:208` Fri 11 Aug requires `docs/ABSENCE-SCOPE.md`; `04:523` R13. No `16` or `21` survives. |
| **C15** | Stratum A = 20, ≥ 6 of 20 retain, ≤ 2 delete, one extension to n = 40 at ≥ 12 | **LANDED** | `04:44–47` verbatim as DECISION E6.1; `04:60` "Draw until \|A\| = 20; cap Stratum B at 10; ≈30 drawn in total"; `04:64–72` the power table is stated as exact binomial for n = 20 and labelled "belong to no other n". *A downstream arithmetic divergence in the experiment's size and cost is reported at §V.5.4.* |
| **C16** | Five gates: G0 · G1 · G2 · G3 · G4 | **LANDED** | `01:371`; `02:856–877`; `02:879` "Why five and not four"; `03:246`; `04:85`. The four-gate numbering survives only in the mapping table at `02:920`. |
| **C17** | Two different tests: E6 at `K/O > 0` + marginal kill; registry at `K/O ≥ 0.80` | **LANDED** | `02:890–899` states both in a two-row table and "a document that quotes one attrition figure has quoted the wrong one"; `03:279`; `04:96` DECISION E6.2. |
| **C18** | Provider-native structured output + post-hoc key check; `outlines` when an open-weight model enters | **LANDED** | `02:205–209`; `03:49` row 24. Both carry "whether provider-native constraint is guaranteed or best-effort is UNVERIFIED — which is exactly why the post-hoc guard is not optional". |
| **C19** | Implement the FRBR URI grammar (~100 lines); `cobalt` only if its LICENSE is opened; `bluebell` GPL-3.0 never linked | **LANDED** | `02:167–171`; `03:33` row 8; `03:98`; `04:400`. |
| **C20** | Z3 MIT SECONDARY · Hypothesis reported MPL-2.0 SECONDARY · in-toto Apache-2.0 VERIFIED-AT-SOURCE, deleted from the unread table | **LANDED** | Z3: `03:41`, `03:83`, `04:527`. Hypothesis: `02:338`, `03:46`, `03:84`. in-toto: `01:762`, `02:1131`, `03:59`, `03:86`, `04:355`. `03:96–102` lists the unestablished licences and in-toto is correctly absent. |
| **C21** | Filer signs, detached key; vendor only as `assessor.id`, `thirdParty:false`; residual is legal review | **LANDED** | `02:1141`; `03:623`; `03:825`; `04:530` R20 "**DECIDED, pending legal review**"; `04:567` Q7. "Nobody has raised it yet" is gone. |
| **C22** | One `pervasiveness-policy-v1.json`; both numbers `PLACEHOLDER` until argued | **LANDED** | `02:719–725`; `02:1060` renders `"K": "PLACEHOLDER", "T": "PLACEHOLDER"`; `03:129` F12; `03:827`; `04:337` M3. |
| **C23** | Supervisor is not a user; say "a downstream reviewer"; delete "the two surfaces" | **LANDED** | `01:104`; `01:109` "the phrase 'the two surfaces' does not appear in this specification" — and it does not; `03:707`; `03:723` "what a downstream reviewer's triage tool consumes"; `04:393`. |
| **C24** | "Data model, stack and flow in B; experiment queue, dated plan and deliverable in C" | **LANDED** | `04:571–573` "the data model, the stack and the flow are in the part preceding this one; this part carries the experiment queue, the dated plan, the deliverable and everything still open". The inversion is gone. |
| **C25** | "…any of the fourteen complete outputs" | **LANDED** | `01:59`; `04:263`; `04:521` R11. No "fifteen outputs" anywhere. |
| **C26** | State the plan as `1 list + N detail`, report the run's actual count | **LANDED (with residue)** | `01:236`; `02:94`; `03:691`; `04:483`. *Residue at §V.6.1: 2,235 is reported as MEASURED in two parts and reconciles with no N stated anywhere in the document.* |
| **C27** | One date with one verb, or neither | **LANDED** | `02:101` and `03:57` quote the advisory ID and CVSS only; `04:406` states the rule explicitly. No date survives. |
| **C28** | Quote only what one instrument returned; no scheme count from the register | **LANDED** | `01:115`, `01:120`; `04:484`. The 390 is deleted and its deletion is recorded at `01:122`. |
| **C29** | Induction, harvest, arithmetic evaluation and the denominator are built; the rest is specified | **LANDED** | `02:24` quotes the ruling verbatim and forbids the "L1→L5" form; `01:391`; `03:647`; `04:177`. Layer-by-layer statuses reconcile across `02:39–51`, `03:117–131` and `04:181–188`. |
| **C30** | `.external_source_lacks_field` — our near-miss is the illustration, not an instance | **LANDED** | `01:227`; `02:614`; `03:582`; `04:491`. All four carry "illustration and not an instance" with both endpoints. |
| **C31** | Add the administrator call to M0 as E1b, or record its retirement — not both states | **LANDED (label mismatch, §V.5.6)** | `04:28` E1b; `04:154` "**DECIDED: it stays, scheduled in M0, demoted from killer to pitch-shaping**" with the exact question text at `04:163`; `04:565` Q5. |

---

## V.2 — THE NINE SURVIVING FALSEHOODS

| # | Grade | Evidence |
|---|---|---|
| **F1** `555` / `562` | **LANDED** | Zero occurrences outside the ban row at `01:822`. The enumeration is `505 + 54 + 15 = 574` and `574 / 581 = 98.8%` at `01:325`, `02:1092`, `04:487`, each labelled DERIVED. |
| **F2** "+37–54 pp of functional equivalence" | **LANDED** | The phrase occurs only in the ban row (`01:825`). The corrected sentence — structural similarity, and outcome equivalence 51–53% — is at `01:261`, `02:255`, `03:231`, `04:266`. |
| **F3** "Hypothesis (MPL-2.0)" as bare fact | **LANDED** | `02:338`, `03:46`, `03:84` all read "reported MPL-2.0 … LICENSE not (re-)read". |
| **F4** "Z3 (MIT)" as bare fact | **LANDED** | `03:41`, `03:83` "MIT (SECONDARY — the LICENSE was not opened by any lane); open it before shipping". |
| **F5** "in-toto — UNVERIFIED" | **LANDED** | Inverted correctly; see C20. |
| **F6** "sixteen commercial products" | **LANDED** | See C14. |
| **F7** "8.23% of ~12,925" | **LANDED** | See C13. |
| **F8** bare "the 17 decidable predicates" | **NOT-LANDED → fixed** | `04:190` carried `*"17 of 24 → 574/581 = 98.8% in an afternoon"*` as a live claim needing a warrant label — the banned figure, presented as a claim rather than quoted as dead. Every other part uses the ruled replacement (`01:299`, `01:823`, `02:843`). Edit 11. |
| **F9** PROVE rows marked VERIFIED-AT-SOURCE | **LANDED** | `01:256` is labelled **ABSTRACT-ONLY** and states "Every negative claim about PROVE … is downgraded to 'not visible in the abstract; the full text is unread'"; `01:733`; `04:39` E13; `04:524` R14. |

---

## V.3 — THE ELEVEN UNWARRANTED-CONFIDENCE RESTATEMENTS

**U1 — the one that matters. PRESENT, PROMINENT, AND USED AS AN ASSET.** This is the strongest thing
the merge did. The corrected paragraph appears verbatim in four places, never in a footnote:

- `01:313` — inside §I.2.5, introduced as "**the one that matters most, because it is about us**", with
  the reasoning spelled out first at `01:305`: "under this specification's own admission rule, **the
  currently admissible predicate set is empty and the currently defensible settled fraction is 0%.**"
- `02:1098` — as the corrected sentence attached to the report's headline, plus a **schema field**
  carrying it: `02:1023` `"admissibilityCaveat": "None of the 280 predicates producing this number is
  admitted under gate G4 … the currently defensible settled fraction is 0%."` Putting it in the payload
  is stronger than D asked for.
- `03:542` — attached to the settled-fraction object.
- `04:420` — as the operator's spoken line at demo step 2, with `04:428` "**Why step 2 is the strongest
  moment and not the fatal objection**", `04:512` R2 ("Mitigated by disclosure — and it becomes the
  strongest moment in the demo"), and `04:462` **A11**, a CI test: "No settled count renders without the
  admission state of the predicate set that produced it … assert `PRE-GATE` appears in the same block".

The composition caveat travels with it in all four (`01:319`, `02:1104`, `03:549`, `04:430`): 2,329 of
2,373 (98.1%) from 53 validation predicates, 271 cells from 227 arithmetic ones. **Those class counts
reconcile against the harvest breakdown at `03:189`** — 181 + 35 + 11 = 227 arithmetic, 20 + 13 + 11 + 6
+ 3 = 53 validation-derived — which is a check D did not ask for and which passes.

| # | Grade | Evidence |
|---|---|---|
| **U2** "L1→L5 runs end-to-end" | **LANDED** | `02:29` bans the form by name; `02:24`, `01:391`, `03:647`, `04:177` carry the ruled sentence. |
| **U3** "zero model calls" stated as a property | **LANDED** | `02:34`, `01:394`, `03:649`, `04:192`, `04:457` A6 "**Not yet written — this is the gate that turns a design property into a system property**"; `03:805` lists `test_no_model_in_verdict_path` as "(**not yet written**)". *Minor residue at §V.6.6.* |
| **U4** FinVerBench concentration | **LANDED** | `01:243` is a bold single-instrument warning governing the first four rows, each tagged `[FVB]`; `04:259` makes the annotation non-negotiable before submission; `04:522` R12. |
| **U5** "0% FPR" true by construction | **LANDED** | `01:253` "**Calibration is achievable, and it was measured on a clean set built to satisfy the checks. Say both in one sentence.**"; `04:266`. |
| **U6** residue reproducibility | **LANDED** | `01:801`, `02:1241`, `03:367`, `04:35` — all four carry "and the published adjudication record", content-addressed. |
| **U7** 98.8% asserted as measured | **LANDED** | `01:328`, `02:1093`, `04:190` (as corrected), `04:487` — all labelled "DERIVED — an enumeration argument, not a run". |
| **U8** "the gate demonstrably does real work" | **LANDED** | `01:795`, `02:268`, `03:785`, `04:423` — all four state one rejection, five predicates, 1,428 cells, and "whether it rejects anything on the FME workbook is unmeasured — 19 of 24 FME bounds are a real `≥ 0`". |
| **U9** "the register is clean by definition" | **LANDED** | `01:231`, `03:294`, `04:111` — membership vs format split, with 87 of 228. |
| **U10** τ-bench denominator | **LANDED** | `01:258` "τ-retail, n = 115 tasks; τ-airline (n = 50) … **The denominator travels or the figure does not**"; `01:404`; `04:383`. |
| **U11** 515 never alone | **LANDED** | `01:188`, `02:1106`, `03:793`, `04:244`, `04:477` — every occurrence carries the per-workbook distribution requirement, and `03:796` makes publishing it a build gate. |

---

## V.4 — THE THREE INNOVATION RESTORATIONS

All three are restored in D's bolder-and-truer form, not sanded off. Each is carried as a block quote in
at least three parts, which is what makes it survivable.

**I1 — the undetectable-in-principle mutant class. RESTORED.**
> `01:533` / `02:1253` / `03:370` / `04:426`: *"A prescribed return is a closed arithmetic system. We can
> construct, and exhibit, a family of filings that are internally perfect under every relation the
> regulator's own template encodes and every relation we have added — and materially false. That family
> is non-empty by construction, its size is measurable, and measuring it is the first quantitative
> statement anyone has made about the limit of document-level verification for a regulated filing."*

The consequence D asked for is drawn: `04:520` grades R9 **"Low → structurally impossible"** and marks
it "Structurally retired; the measurement is the deliverable". `02:1259` and `03:377` state the same.

**I2 — `INVALID` as a liveness proof. RESTORED.**
> `01:551` / `02:1178` / `03:173` / `04:425`: *"No assurance artifact in existence carries evidence that
> the instrument that produced it was working on the specific document it examined. A clean audit
> opinion does not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict
> unless every check has just demonstrated, on your file, that it can still catch the fault it was
> admitted for."*

The hedges D said to keep are kept and subordinated: `02:1184` "The nearest named prior art is SRE
synthetic monitoring and hardware built-in self-test" and "*A formal-methods citation for vacuity
detection is **UNVERIFIED** and must not be asserted.*"

**I3 — the criterion-source substitution. RESTORED.**
> `01:564` / `02:232` / `03:237` / `04:438`: *"SPADE infers what correctness meant from the traces of a
> developer changing their mind. We do not have to infer it: the criterion is a published instrument
> with a version, an amendment chain that is machine-followable in 76 of 82 cases, and a blank template
> with a content hash. The criterion source is not more* authoritative *than SPADE's — the regulator's
> own template computes a scheme total that misses two of its own nine legal values — it is* **citable,
> versionable and watchable***…"*

`02:239` and `03:244` both add the sentence D wanted: this is what the instrument-stream watcher
implements, and no draft stated it as a novelty. The brief's sharpest sentence is carried in its only
defensible form at `01:578`, `02:930`, `03:69` and `04:389`.

---

## V.5 — CROSS-PART SEMANTIC DIVERGENCE

**This is the section that matters. D ruled on none of these, so none of them is a failure of the
merge — they are places where two parts, each internally coherent, assign two different values or two
different meanings to one thing. Ranked by consequence.**

### V.5.1 — THE CELL-STATE PRECEDENCE ORDER IS TWO DIFFERENT ORDERS, AND THEY DISAGREE ON THE HEADLINE NUMBER — **UNRESOLVED, OWNER DECISION REQUIRED**

> `02:477`: `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`
> and `02:478`: "A cell is clean only if **every** predicate binding it passed."

> `03:506`: `ERROR ≻ FAIL ≻ PASS ≻ INDETERMINATE ≻ NOT_RUN ≻ NO_PREDICATE`
> and `03:507`: "A cell read by one passing and one not-run predicate is **settled**."

These are opposite rules for the same case. Under Part II a cell read by one passing and one `NOT_RUN`
predicate is **unsettled**; under Part III it is **settled**. The settled fraction — 2,373 / 3,747, the
number the whole document is built around — is not well defined until one of them wins. The two orders
also differ in membership: Part II includes `INFORMATIONAL` and `OUT_OF_SCOPE` and excludes
`NO_PREDICATE` (`02:478–480`); Part III includes `NO_PREDICATE` and excludes the other two, having
determined scope first (`03:503`).

**Recommendation, not applied because D does not rule it.** Part II's order is the one consistent with
both parts' prose. `02:83` and `03:119` both say that when the readers disagree on a field, every
predicate reading it returns `NOT_RUN(extractor_disagreement)` and **"the settled fraction falls, it
does not silently succeed"** — which is only true if `NOT_RUN ≻ PASS`. Part III's order makes that
sentence false in exactly the case it was written for. Adopting Part II's order requires flipping the
claim at `03:507` and re-deriving nothing else.

### V.5.2 — THE "FIVE RULES" OF THE EVALUATION CONTRACT ARE TWO DIFFERENT FIVES — **UNRESOLVED**

`02:534–560` and `03:137–157` are identical, rule for rule: (1) `applicable` · (2) pre-flight ·
(3) `expr` · (4) warrant composition · (5) `cells_bound`. `04:545` G5 enumerates a **different** five:
(1) `applicable == false` · (2) `expr` true/false · (3) runtime error · (4) budget · (5) `cells_bound`.

Nothing in Part IV's five is *wrong*; it drops pre-flight and warrant composition and splits rule 3.
But `03:819` G5 says the contract "**contain[s] the five rules and nothing else; every other document
links to it**", and `02:529` says a CI test asserts the evaluator's transition table equals that table.
A build that generates `EVALUATION-CONTRACT.md` from Part II and tests it against Part IV's G5 fails.

**Recommended replacement for `04:545`**, not applied because it rewrites rather than corrects:
*"DECIDED: one file, `EVALUATION-CONTRACT.md`, generated from §II.3.4 and the only place the contract
appears. Its five rules are `applicable`, pre-flight, `expr`, warrant composition and `cells_bound`; the
three rulings the drafts disagreed about are rules 1, 3 and 5, resolved as `OUT_OF_SCOPE`,
`ERROR(predicate_raised)` and `ERROR(cells_bound_zero)`."*

### V.5.3 — THE CONTAINER GUARD EMITS A REASON CODE THAT IS NOT IN THE CLOSED VOCABULARY — **UNRESOLVED**

> `03:118` F1: "Any trip → `INVALID` with `ERROR(source_unreadable)`."

`source_unreadable` is a `not_run.*` code (`02:607`, `03:573`). The `error.*` family has exactly five
members and none of them fits a container-guard trip (`02:633`, `03:578`). This is the closed-world
promise failing inside the document that makes it: a state/reason pair is emitted that the frozen 8 × 30
vocabulary cannot represent. `02:1221` lists "a container guard trip" among the `INVALID` causes and
assigns it no code at all, so there is no second opinion to copy.

**Two admissible fixes, both needing the owner:** map it to `error.parser_disagreement_structural`
(stretching that code's meaning), or admit a 31st code `error.container_guard_tripped` under the
stated admission test — it plainly implies a different remedy from every existing code, which is the
test at `02:584`. **The count 8 × 30 is pinned in four places, so this is not a free change.**

### V.5.4 — THE SETTLING EXPERIMENT SHIPPED THREE SIZES AND THREE COSTS — **FIXED**

`04:118` derives 600 candidates ≈ $13 from ≈30 obligations drawn, consistent with `02:373` ("~600 calls
per template version … ~30 obligations × 10 candidates × 2 prompt regimes"). `03:665` carried "20
obligations × 10 candidates × 2 prompt regimes = 400 candidates … ≈ $9.10" — a fourth arithmetic that
does not even multiply out (400 × $0.0218 = $8.72) — and `00:64` carried "about nine dollars". Both
aligned to Part IV's shown arithmetic, which is the only one that reconciles with C15's ≈30 drawn.
Edits 8 and 9.

### V.5.5 — SMALLER DIVERGENCES, ALL FIXED

| Thing | Part II said | Part III / IV said | Resolution |
|---|---|---|---|
| Verdict enum | `COVERAGE_INSUFFICIENT`, `…_WITHIN_STATED_COVERAGE` | `SETTLEMENT_INSUFFICIENT`, `…_WITHIN_STATED_SCOPE` (`03:14` decides it, with a reason) | Part II aligned to Part III (edit 4) |
| `predicateType` | `filing-coverage-attestation/v1` | `filing-settlement-attestation/v1` (`03:59`) | Part II aligned (edit 2) |
| Declared-gaps key | `coverageGaps` | `declaredGaps` (`03:523`) | Part II aligned (edit 3) |
| Predicate `state` enum | `ACTIVE \| PROVISIONAL \| QUARANTINED \| WITHDRAWN` (`02:802`) | `ACTIVE \| PROVISIONAL \| WITHDRAWN \| REJECTED` (`03:451`) — **no `QUARANTINED`, though `02:972` V5 and `03:345` both mandate automatic quarantine** | Part III aligned to Part II (edit 7). *Residual: `REJECTED` is now absent from both; rejected candidates live in the `rejection` table with `predicate_id NULL` (`03:468`), so this is believed correct — confirm.* |
| Report item key | `cell_id = stable_key` (`02:455`) | `item_id = (stable_key, predicate_id)` (`04:546`) | Part IV aligned to Part II (edit 15) |
| Obligation table file | `obligations.yaml` (`02:470`) | `obligations.csv` (`04:546`) | Part IV aligned (edit 15) |
| Money-scale enum | `field(… unit …)` (`03:428`), `Field.unit` (`03:818`) | `Field.scale` (`04:543`) — names a field that exists nowhere | Part IV aligned (edit 14) |
| Fact-table build time | — | 1 ms MEASURED (`03:636`) vs ~10 ms (`04:183`, the receipt figure) | Part IV aligned (edit 12) |
| Residue exhibit | "all 223 carries and all 135 SUM identities" — 135 is sourced nowhere in the corpus | "all 181 cross-sheet carries and all 35 SUM identities" (`04:426`, `04:520`), matching the harvest breakdown at `03:189` | Part II aligned (edit 6) |
| G3 proof-arm outcome | `unknown ⇒ UNCHECKED` (`02:866`) — a retired token | `unknown` is `unproven` (`03:41`, `03:261`) | Part II aligned (edit 1) |

### V.5.6 — DIVERGENCES LEFT DELIBERATELY UNTOUCHED

- **E1b status label.** `01:507` opens the administrator call as "**OPEN — USER DECISION** … is the
  fund-administrator call still live?" with a default of retirement-as-killer; `04:154` says
  "**DECIDED: it stays**, scheduled in M0, demoted from killer to pitch-shaping". The *substance* is
  identical (not a killer; still worth one call) and `04:565` Q5 preserves the user's decision, so this
  is a label mismatch, not a contradiction. Worth one word if the owner wants it tidy.
- **`K`/`T` absolutism.** `03:827` says "**no number for either appears anywhere**", while `02:719`
  quotes the two withdrawn parameter sets (`K = 3, T = 0.35, v2` and `K = 3, T = 0.45, v1.1`) in a
  withdrawal note. Part II's usage matches the convention every ban table in the document uses; Part
  III's absolute is what is overstated. Left alone.
- **Severity threshold precision.** `02:678` and `04:542` both key the tier on the **Wilson upper
  bound** and argue it; `03:817` G2 states the same thresholds without saying which statistic. Silence,
  not contradiction — but in a document whose §V.6 exists, the words "Wilson upper bound" are worth
  three characters of ink at `03:817`.
- **SPADE's own metric.** `02:220` and `04:93` render it "100% coverage and 100% FFR"; `03:273` renders
  it "100% settled at 100% FFR". Quoting another system's metric name is defensible, so C12 is not
  violated; but two renderings of one quoted fact is a smell.

---

## V.6 — WARRANT DISCIPLINE: NUMBERS WITHOUT A DENOMINATOR OR A WARRANT

Judged against the document's own rule (`01:3`: "Every quantity below carries a warrant label and a
denominator"). Worst first.

1. **`02:96` and `03:693` — "2,235 requests / 2,235 GETs (MEASURED)".** The plan is stated as
   `1 list + N detail where N = |records|`. The document publishes two candidate values of `|records|`:
   650 fund rows and 2,005 register records (`01:209–210`), giving 651 or 2,006. **2,235 reconciles with
   neither, and neither part says what it counts.** D's C26 asked for the plan *and* the run's count;
   the merge delivered both and reconciled neither, so the arithmetic an adversary checks first is still
   unaccounted for. This is the single worst offender because it is the same species of defect — a
   number whose denominator is not stated — that the document exists to attack.
2. **`02:220`, `03:55`, `04:93` — "44.4% of raw candidates individually blow a 25% FFR budget".** No
   denominator (44.4% of how many candidates?), no warrant label, in all three parts.
3. **`02:247`, `03:55` — "68.9% of a published neural oracle's bugs at twice its precision".** No
   denominator, no warrant label.
4. **`02:342`, `03:46` — "55% of mutations are found with a single input and 76% within the first 20".**
   No denominator, no warrant label; it is load-bearing, because it sets `max_examples = 50`.
5. **`03:636` — "fact table over 511 cells 1 ms (MEASURED)".** 511 appears exactly once in the corpus
   and is never defined. The field surface is 3,747; the formula-cell count is 505. A reader cannot tell
   whether 511 is a typo, a subset, or a different filing.
6. **`00:47` — "The whole thing runs in ~30 ms with zero model calls on the verdict path."** Stated as a
   present-tense property of a running system, which is exactly what U3 forbids. The four numbered parts
   all carry the "specified, gate not yet written" caveat; the executive summary does not. *Not edited —
   the same sentence appears in D's own executive verdict, so the owner may have wanted it. It is
   nonetheless the one sentence in the front matter a judge can falsify.*
7. **`02:687` — "roughly `n ≥ 185` clean, non-self-authored filings".** DERIVED and correct, but
   unlabelled and with no shown arithmetic, sitting one line from a paragraph about labelling.
8. **`01:144` — "20% of *inspected* Big Four US audits".** The qualifier "inspected" is carried
   correctly and never drops off, but the inspected population is never given a number, so the
   percentage has a named denominator and no size.

**Also fixed under this heading:** `02:1019` rendered `"settled": { "pass": 2361, "fail": 12, "total":
2373 }` under the comment `// MEASURED (harvest)`. The total is measured; the 2,361/12 split is
invented. Part III's twin block carries the disclaimer (`03:529`: "*A schema example on a hypothetical
filing, not a measurement*"); Part II asserted MEASURED over a fabricated failure count. Edit 5.

---

## V.7 — EDITS MADE

Seventeen edits. Every one is a token or single-clause replacement; no section was rewritten, no claim
was added, no structure changed.

| # | File:line | Before | After | Authority |
|---|---|---|---|---|
| 1 | `02:866` | ``` `unknown` ⇒ UNCHECKED, never "non-degenerate"``` | ``` `unknown` ⇒ unproven, never "non-degenerate"``` | C4 (retired token); `03:41`, `03:261` |
| 2 | `02:993` | `"predicateType": "https://<ns>/filing-coverage-attestation/v1"` | `…/filing-settlement-attestation/v1` | C12; `03:59` |
| 3 | `02:1068` | `"coverageGaps": [ … ]` | `"declaredGaps": [ … ]` | C12; `03:523` |
| 4 | `02:511`, `02:703` (×2), `02:707`, `02:710`, `02:725` (×2) | `COVERAGE_INSUFFICIENT` · `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE` | `SETTLEMENT_INSUFFICIENT` · `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` | C12; `03:14` is the only place the question is decided. **Reversible in one commit if the owner prefers the old spelling — but one of the two must go.** |
| 5 | `02:1019` | `// MEASURED (harvest), see caveat` | `// total MEASURED (harvest), see caveat; the pass/fail split is illustrative, not a measurement` | Warrant rule `01:3`; `03:529` |
| 6 | `02:1264–1265` | "all 223 carries and all 135 SUM identities" | "all 181 cross-sheet carries and all 35 SUM identities" | `03:189` harvest breakdown; `04:425`, `04:519`. 135 is sourced nowhere. |
| 7 | `03:451` | `-- ACTIVE \| PROVISIONAL \| WITHDRAWN \| REJECTED` | `-- ACTIVE \| PROVISIONAL \| QUARANTINED \| WITHDRAWN` | `02:802`; V5 at `02:972` and `03:345` both mandate automatic quarantine |
| 8 | `03:665–667` | "(20 obligations × 10 × 2 = 400 candidates) is ≈ $9.10 … costs under ten dollars" | "(≈30 obligations drawn × 10 × 2 = 600 candidates) is ≈ $13, budgeted at $25 with re-runs … costs under thirty dollars" | C15 (≈30 drawn); `04:118` shows the arithmetic |
| 9 | `00:64` | "costs about nine dollars" | "costs about thirteen dollars" | same |
| 10 | `00:76` | "This is what makes the coverage claim true by construction rather than by discipline." | "The settled-fraction claim is then true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement." | `03:305–308` explicitly withdraws the sentence the executive summary was still using |
| 11 | `04:190` | *"17 of 24 → 574/581 = 98.8% in an afternoon"* | *"15 exact + 2 normalisation-dependent of 24 → 574/581 = 98.8% in an afternoon"* | F8; `01:299`, `01:823` |
| 12 | `04:183` | "fact-table construction (~10 ms)" | "fact-table construction (~1 ms)" | `03:636` MEASURED |
| 13 | `04:421` | `` `1 failure · 2,373 fields settled across 280 checks` `` … "in the same block." | `` `1 failure across 2,373 checks` `` … "with `predicate set: PRE-GATE` and the 280-predicate strap line in the same block, never in the hero." | C11; `03:750–753` |
| 14 | `04:543` | "including from the `Field.scale` enum" | "including from the `Field.unit` enum" | `03:428` SQL, `03:818`; no `scale` field exists |
| 15 | `04:546` | "report items are keyed `item_id = (stable_key, predicate_id)` … `obligations.csv`" | "report items are keyed by the cell — `cell_id = stable_key` (§II.3.1), with each item carrying its per-predicate `evaluations[]` … `obligations.yaml`" | `02:455`, `02:468`, `02:470` |
| 16 | `01:146` | "the warrant is qualified in §I.2.3" | "…in §I.5.3" | §I.2.3 contains no PCAOB row; the qualification is at `01:664` |
| 17 | `01:64` | "§I.5.3 states the search that failed to find one" | "§I.5.2 states…" | The search scope and the list are at `01:596`, inside §I.5.2 |

---

## V.8 — WHAT WAS NOT FIXED, AND WHY

| # | Problem | Why I did not fix it | What closing it costs |
|---|---|---|---|
| 1 | **Cell-state precedence (§V.5.1)** | D issues no ruling, and both orders are argued in place. Choosing changes the value of the settled fraction — the product's headline — so it is not an auditor's call. | One sentence at `03:506–507`, plus a line in the closure test. Ten minutes, and it must happen before `test_closure` is written. |
| 2 | **Two "five rules" (§V.5.2)** | Correcting `04:545` means rewriting the cell, not correcting a token. | Replace `04:545` with the text drafted in §V.5.2. |
| 3 | **`ERROR(source_unreadable)` outside the vocabulary (§V.5.3)** | Needs either a 31st reason code or a stretched meaning; both change a count pinned in four places. | One decision, then a one-word edit at `03:118` or a 31st row at `02:633` and `03:578` — and the "30 codes" count updated everywhere if the latter. |
| 4 | **The unreconciled 2,235 (§V.6.1)** | The reconciliation is a fact about a run I cannot re-execute. | Re-read the snapshot manifest and state what the 2,235 counts, or drop the figure and cite the manifest. |
| 5 | **`00:47` present-tense "runs with zero model calls" (§V.6.6)** | The identical sentence is in D's own executive verdict, so this may be intentional. | Add the six-word caveat the other four parts carry. |
| 6 | **Undefined `511 cells` (§V.6.5)** | I cannot invent the denominator. | Define it or delete it. |
| 7 | **`REJECTED` now absent from the predicate `state` enum (§V.5.5)** | Edit 7 aligned Part III to Part II's four values; if a *predicate row* (not a candidate) can be rejected, the enum needs five. | Confirm that rejected candidates only ever exist in the `rejection` table. |
| 8 | **Document title, `00:1` — "THE COVERAGE-DECLARING FILING CHECKER"** | Renaming the document's title is not a surgical edit. | Under C12 the word "coverage" is reserved for the conformal guarantee; the title uses it as the product's defining property. Either accept "coverage declaration" as a distinct concept phrase (it is used that way at `01:495` and `04:391`) or retitle. |

---

## V.9 — VERDICT

**The ruling landed.** Twenty-nine of thirty-one contradictions state D's replacement in the exact terms
D wrote, most of them in three or four parts independently; eight of nine falsehoods are dead and quoted
only in ban tables; all eleven unwarranted-confidence corrections are present; and all three sanded-off
innovations are restored in the bolder form, block-quoted, with the consequences D asked for actually
drawn (R9 regraded to structurally impossible; the admissibility caveat promoted into the attestation
schema and into a CI test). **U1 in particular is not merely present — it is the spine of the demo, a
required schema field, and a build gate.** That is more than the ruling asked for.

**The residual risk is not in the ruling; it is in the seams.** Three unruled cross-part divergences
survive, and one of them — whether a cell read by one passing and one not-run predicate is settled —
changes the number on the front page. A specification whose thesis is that a denominator must be
derived rather than asserted cannot ship with two derivations of its own denominator.

**Fit to hand to its owner: yes, with one blocking item.** Resolve §V.5.1 before anyone writes
`test_closure`; §V.5.2 and §V.5.3 before the evaluation contract is generated. Everything else in §V.8
is an afternoon.

---

## V.7 — POST-AUDIT RESOLUTIONS (owner, 10 Aug 2026)

The three items the audit correctly declined to fix on its own authority have been decided. Each was a
determined answer under the design's own thesis, not a preference; each is recorded here and applied in
place in the parts named.

### V.7.1 resolves V.5.1 — cell-state precedence · **APPLIED to §III.4.2**

**Decision: §II's order is normative** — `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻
OUT_OF_SCOPE`, and **a cell is clean only if every predicate binding it passed.** §III's
`PASS ≻ INDETERMINATE ≻ NOT_RUN` and its claim that a cell read by one passing and one not-run predicate
is *settled* are withdrawn.

*Why it is determined rather than chosen:* both parts state that on reader disagreement every predicate
reading the field returns `NOT_RUN(extractor_disagreement)` and **"the settled fraction falls, it does not
silently succeed."** Under `PASS ≻ NOT_RUN` that sentence is false in exactly the case it was written for —
a passing predicate absorbs the un-run one and the fraction holds. A check that did not run must never be
absorbed by one that did; that is the product, not a tie-break.

*Blast radius:* the **runtime** settled count can now fall below the static figure, which is the intended
behaviour. The harvest figure **2,373 of 3,747** is unaffected — it counts cells reachable by at least one
harvested predicate, computed before any evaluation.

### V.7.2 resolves V.5.2 — the two different "five rules" · **APPLIED to §IV.6 G5**

**Decision: the five rules are §II.3.4's** — `applicable` · pre-flight · `expr` · warrant composition ·
`cells_bound` — because `EVALUATION-CONTRACT.md` is *generated* from §II.3.4 and a CI test asserts the
evaluator's transition table equals it. §IV's alternative five (which dropped pre-flight and warrant
composition and split rule 3) was not wrong, but a build cannot satisfy two fives. The three rulings the
drafts disagreed about now sit **inside** rules 1, 3 and 5, and budget exhaustion is a sub-case of rule 2.

### V.7.3 resolves V.5.3 — the container guard's reason code · **APPLIED to §III.4.4.1**

**Decision: neither of the audit's two options. A category correction instead.** The 8 × 30 vocabulary is
**per item**, and an item is a cell. A container guard trip is not a property of any cell — nor are an
unbound template or a denominator disagreement, both of which fall through the same hole. Forcing them into
a per-cell reason code was the error, not the missing code.

Run-level `INVALID` causes therefore become their own closed vocabulary, `invalid.*`, with exactly the
eight causes §II.6.2 already enumerates. **The item-level count stays pinned at 8 × 30 in all four
places**, so nothing pinned moves. Where a run-level cause has an item-level analogue
(`.cells_bound_zero`, `.predicate_raised`) both are carried; they are not alternatives.

### V.7.4 resolves the worst of V.6 — warrant discipline · **APPLIED to §II.1.2, §III.5, §0**

- **"2,235 register GETs (MEASURED)" is withdrawn to UNRECONCILED** in both places it appeared. It matches
  neither `1 + 650 = 651` nor `1 + 2,005 = 2,006`, no document states its `N`, and the run cannot be
  re-executed from the artifacts on disk. The fetch plan is now quoted in its **form** — `1 list request +
  N detail requests` — and never as an integer until a re-fetch records one in the manifest. This is the
  same rule the system applies to a filer, applied to the system.
- **Zero model calls in the verdict path** is stated in the executive summary as *specified, with the CI
  gate listed and not yet written* — never in the present tense as a property of a running system.

### V.7.5 — What remains genuinely open after this pass

Not defects, and not fixable by decision: the undefined "511 cells" reference in §III.5; the "44.4% of raw
candidates" and "68.9% of TOGA's bugs" figures carried without their denominators; and the `REJECTED`
predicate state, now absent from both enums on the belief that rejected candidates live in the `rejection`
table with `predicate_id NULL` — **confirm before the schema is written.** These are listed so the next
pass starts from them rather than rediscovering them.
