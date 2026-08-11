# L13 — THE ADVERSARY
### Attacking the eight-layer design, then repairing what breaks

**Lane:** architecture adversary · **Compiled:** 10 Aug 2026
**Inputs read:** `/Users/abishaikc/Thinking/gift-ifsc-ground/RND-BRIEF.md`, `/Users/abishaikc/Thinking/gift-ifsc-ground/ARCHITECTURE.md`
**Artifacts opened first-hand:** `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/` (9 workbooks + 4 analysis scripts), `/Users/abishaikc/Thinking/gift-ifsc-ground/{b_q4,ar2425,am_jul26,bulletin_janmar2025}.txt`
**Interpreter:** `/Users/abishaikc/Gift/.venv/bin/python` (openpyxl 3.x, lxml, stdlib `zipfile`/`re`)

---

## COVERAGE DECLARATION (this lane's own boundary, stated first)

Applying the brief's Rule 2 to myself.

| What I could do | What I could not |
|---|---|
| Re-run the operator's own scripts and three independent parsers over the real FME workbook | Verify any ⓐ arXiv identifier from §6.1 (see below) |
| Verify FME/scheme population counts against IFSCA's own bulletin text on disk | Verify the CycloneDX ten-state enum (fetched twice, both returns truncated before `compositions`) |
| Verify SPADE's abstract, authors, and headline numbers at arXiv | Verify the 46%-staffing figure — it appears nowhere in the brief's evidence tables |
| Verify the definitions of mutation testing and metamorphic testing at a tertiary source | Run any live search — **this session's WebSearch budget (200/200) was exhausted before my first query.** Every external claim below is either WebFetch-at-source or explicitly UNVERIFIED |

**Positive control on the local corpus:** before reporting any absence in the workbook, I confirmed the parser sees what it should — `openpyxl` reports all 10 sheets, 505 formula cells, 12 defined names, and the hidden sheet. A parser that returns 0 for a class is not evidence of absence; §4.4 is the proof, and this lane found three more instances of it.

---

## PART 0 — THE VERDICT IN ONE PAGE

Three attacks are **fatal if unanswered**. Two of them I can settle now, with measurements.

1. **F1 — The qualification gate is two-thirds built, and the missing third is load-bearing.** L4's third test (FFR on a clean corpus) is unrunnable as specified, because the team that authors the predicates also authors the clean corpus. FFR on a self-authored corpus has expected value zero *regardless of predicate quality*. It is not a weak measurement; it carries **no information**. Every claim of the form "which makes the coverage claim true by construction" collapses with it.
2. **F2 — Nothing in the architecture catches the architecture's own §4.4 failure.** The system is a deterministic program that reports "no failures". The brief documents two silent false negatives from deterministic programs and calls that the strongest evidence in the pitch. There is no layer that would catch the same failure *in us*. **I found three more instances of that exact failure, live, in the authoritative brief, today** (Part 1). The failure mode is not historical. It recurs, it is systematic, and it is biased in a consistent direction.
3. **F3 — Coverage-as-a-fraction is a metric that improves monotonically with effort spent on things that do not matter.** The decidable set is unbounded and mechanically expandable; the undecidable set is fixed at 7. I took the brief's own 17/24 = 71% to **555/562 = 98.8%** in one afternoon without writing a single interesting check. A number that moves that far under an author's choice of enumeration is not a measurement.

**The repair for all three is the same object**, and it is the most valuable thing in this document: **the residue set** — the set of semantically-wrong mutants of *this filing* that survive the *entire* predicate set. It is adversarial, so it cannot be inflated by adding boring checks; it runs on the artifact under test, so it catches our own parser drift; and it is a direct, reproducible measurement of the boundary that §2.5 says does not exist. It replaces the hand-classified 17/24 with something a third party can re-run.

---

## PART 1 — THE MEASUREMENT THIS LANE RAN
### Five parser divergences on the artifact the whole design rests on

This is the lane's original contribution and it should be read before the attacks, because three of the attacks are grounded in it.

### 1.1 Three implementations, three answers, same file, same day

`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/` contains two of the operator's own scripts. I ran both, plus `openpyxl` as an independent third.

| Implementation | Method | formulas | cross-sheet |
|---|---|---:|---:|
| `an.py` | regex `<f[ >](?:[^>]*)>([^<]*)</f>` + self-closing fallback | **244** | **0** |
| `an2.py` | regex `<f[^>]*>([^<]*)</f>` | **294** | **195** |
| `openpyxl` | OOXML object model, shared formulas materialised | **505** | **195** |

**Warrant: VERIFIED-AT-SOURCE** — I executed all three.

`an.py` still reports **`xsheet=0` for every one of the 10 sheets.** That is the precise false finding §4.4 item 2 documents and says was corrected. It was not corrected — a *second* script was written beside it and the first was left in place, still producing the wrong answer, with nothing in the directory marking which is authoritative. **The §4.4 failure was patched by addition, not by retirement, and the patched-around artifact still runs.**

### 1.2 Why the counts diverge — and why the bias is systematic, not random

Census of every `<f>` element in the FME workbook:

```
t=array    with-text          :   1
t=normal   with-text          : 261
t=shared   with-text          :  32     <- the "master" of a shared formula
t=shared   EMPTY/self-closing : 211     <- <f t="shared" si="N"/> — carries NO text
                               ----
TOTAL <f> elements             : 505
```

- **294** = `<f>` elements carrying literal formula text = **distinct authored expressions**.
- **505** = cells that actually evaluate a formula.
- **211 of 505 = 41.8%** are shared-formula stubs, structurally invisible to *any* text-matching regex.

The bias is not random. Excel factors a formula into a shared master + stubs exactly when the same relation is repeated down a column — which is precisely what **row and column totals** are. So a text regex systematically under-counts *the checking arithmetic* and leaves the *one-off carries* fully visible. **The measurement error is correlated with the quantity being measured, in the direction that supports the brief's thesis.** That is the most dangerous shape an instrument error can have.

Measured: the 32 shared masters cover 243 cells, of which **SUM masters alone cover 118 cells** against 35 authored SUM expressions.

### 1.3 The §4.3 headline: arithmetically correct, and its conclusion does not follow

I reproduced the brief's table exactly, then recomputed it per-cell.

| | per authored expression (n=294) | per formula-evaluating cell (n=505) |
|---|---:|---:|
| pure cross-sheet carry | 181 = **61.6%** | 181 = **35.8%** |
| IFERROR wrapper | 50 = 17.0% | 129 = 25.5% |
| SUM (row/col total) | 35 = 11.9% | 135 = 26.7% |
| IF (conditional carry) | 14 = 4.8% | 14 = 2.8% |
| other/ref | 11 = 3.7% | 43 = 8.5% |
| COUNTIF (tally) | 3 = 1.0% | 3 = 0.6% |
| **"checkable relationship" (SUM+COUNTIF)** | **38 = 12.9%** | **138 = 27.3%** |

**Warrant: VERIFIED-AT-SOURCE.** The brief's arithmetic is exactly right: 38/294 = 12.9%, 181/294 = 61.6%. **I am not correcting the brief's numbers. I am correcting what they are numbers *of*.**

The brief writes:

> "**38 of 294 (13%) express a checkable relationship. 181 (62%) copy a value.** The workbook moves numbers between sheets and that motion is counted as validation."

The first two sentences are true of *authored expressions*. The third sentence is a claim about *the workbook's behaviour*, which is a per-cell property. Per cell, checking arithmetic covers **27.3%** and carrying covers **35.8%** — comparable, not a 1:5 ratio. The rhetorical punch does not survive the correct denominator.

**This is the §4.4 failure class in its purest form: a well-formed, confidently stated, arithmetically correct output that supports a conclusion it does not license.** It came from a denominator choice, not a regex, which is why no amount of parser care would have caught it. Only a second reading of the same artifact with a different question would.

### 1.4 A straight regex miss: the data-validation count

The brief: *"35 data validations (only **3** list-type with a named vocabulary)."* This supports the argument that the template barely constrains anything.

| | count |
|---|---:|
| `<dataValidation>` in the sheet body | 35 |
| of which `type="list"` | 3 |
| **`<x14:dataValidation>` inside `<extLst>`** | **19** |
| of which `type="list"` | **19** |
| **TRUE TOTAL** | **54 validation elements, 22 list-type with a named vocabulary** |

**Warrant: VERIFIED-AT-SOURCE.** The 19 are disjoint from the 35 (different sqrefs) and every one points at the hidden `Dropdown` sheet:

```
type=list sqref=D2              source=Dropdown!$D$3:$D$6    (reporting quarter)
type=list sqref=D3              source=Dropdown!$E$3:$E$6    (financial year)
type=list sqref=D10             source=Dropdown!$J$3:$J$5    (FME category)
type=list sqref=D12             source=Dropdown!$G$3:$G$7    (entity type)
type=list sqref=G54:G63         source=Dropdown!$F$3:$F$11   (scheme category, 9 terms)
type=list sqref=H54:H63         source=Dropdown!$I$3:$I$4    (open/close-ended)
type=list sqref=W88:W97 ...     source=Dropdown!$M$3:$M$14   (instrument type, 12 terms)
type=list sqref=C20             source=Dropdown!$O$3:$O$4    (Manual / Automated)
type=list sqref=C22             source=Dropdown!$P$3:$P$4    (System / Manual)
... 10 more
```

Why the miss: OOXML cannot express a cross-sheet list source in the base `formula1`, so Excel writes those validations into the `x14` extension list. **The validations that live in `extLst` are exactly the ones whose vocabulary is on another sheet — i.e. exactly the ones that matter.** Same systematic bias as §1.2: the structures that constitute the workbook's checking logic are the ones the naive parse cannot see.

The workbook enforces **22** controlled vocabularies, **7.3× the brief's figure**. This makes the product *better* and the problem statement *weaker*.

### 1.5 The hidden sheet — and an exploitable bug in one of the "decidable 17"

```
<sheet name="Dropdown" sheetId="31" state="hidden" r:id="rId10"/>
   sheet_state = hidden
   protected   = False        <-- the ONLY unprotected sheet of the 10
```

The `Dropdown` sheet carries **15 controlled vocabularies** (columns D–R): quarter, financial year, scheme category (9), entity type (5), Yes/No/NA, open/close-ended, FME category (3), constitution (3), PMS type (3), instrument type (12), complaint status (3), valuation mode (Manual/Automated), NAV computation mode (System/Manual), investor-count band (4), scheme status (Active/Expired/Wound up).

**22 validations reference these; 12 of the 15 vocabularies are shipped but unenforced.**

Three consequences, all concrete:

1. **A free predicate harvest.** 12 vocabularies the regulator authored and did not wire up. Each is a high-precision, hand-authorable membership predicate. They cost nothing and they are all boring — see Attack 1.
2. **An exploitable bug in decidable-predicate #13, "dropdown ∈ vocabulary".** The vocabulary source is hidden *and unprotected*. A predicate that reads the vocabulary from the **filed** workbook is validating the filer's data against a list the filer can edit. Any filer who edits `Dropdown!$F$3:$F$11` to add a scheme category passes the check. **The vocabulary must be pinned from the blank template's content hash, never read from the artifact under test.** This is not hypothetical; it is a one-line consequence of `protected=False`.
3. **A vacuity trap.** Any L1 schema induction that iterates *visible* sheets silently drops `Dropdown`. The vocabulary set becomes empty, and `all(v in vocab for v in values)` over an empty vocab either fails everything (100% FPR) or, in the far more likely coding, passes vacuously. Attack 9.

### 1.6 Two more artifact facts the design needs

- **All 505 formula cells carry a cached computed value** (`data_only=True` returns non-`None` for 505/505). This is load-bearing for the L6 repair: there *is* a recomputation baseline in the file.
- **4 of the 12 defined names point at `#REF!`** in the regulator's own published blank template:
  `ExternalData_1 = '2. Summary'!#REF!`, `ExternalData_2 = '1. Introduction'!#REF!`, `ExternalData_3 = '3. Portfolio'!#REF!`, `ExternalData_17 = '4. Investors'!#REF!`.
  Any predicate resolving defined names must handle a broken reference in the *authoritative* artifact. The blank template ships broken.
- **The template has a built-in expiry.** `Dropdown!$E$3:$E$6` = `2025-26, 2026-27, 2027-28, 2028-29`. The workbook cannot express FY2029-30. Version churn is not a risk; it is scheduled.

### 1.7 Population denominators — verified against IFSCA's own bulletin

From `b_q4.txt` (IFSCA Bulletin Q4 FY2025-26), verbatim table row:

> `Fund Management Entity (FME) 202 217` · `Fund Management AIFs/ Schemes 327* 360`

**217 FMEs and 360 schemes as on Mar 2026: VERIFIED-AT-SOURCE.** Trajectory across four IFSCA documents on disk: FMEs 139 (Dec-24) → 162 (Mar-25) → 202 (Dec-25) → **217 (Mar-26)**; schemes 327 (Dec-25) → **360 (Mar-26)**.

**The ~868 filings/year is MODELED, not measured** — it is 217 × 4, and it assumes every FME files every quarter including those registered mid-year. Label it accordingly wherever it appears.

---

## PART 2 — THE ATTACKS

Each: **ATTACK** in the strongest form I can build → **REPAIR** → honest label.

---

## ATTACK 1 — "Very nearly disjoint" vs "71%, the check passes"

### The attack

These are not merely in tension. **They are answers to two different questions, and the document uses the answer to one as evidence for the other.**

- §2.4's claim is about *the relationship between two sets*: `{machine-verifiable}` and `{machine-needed-for}` barely intersect.
- §4.3's 17/24 = 71% is a *cardinality ratio within one enumeration*, scored against a threshold ("Threshold was 50%. The check passes").

A ratio of cardinalities cannot confirm a claim about disjointness, because **the enumeration is author-chosen and the two sets grow at wildly different rates.** And I can now put a number on that.

**Measured, this lane:** predicates mechanically derivable from the blank template with no model and no judgment —

| Source | Decidable predicates |
|---|---:|
| Recompute-and-compare, one per formula-evaluating cell | 505 |
| Range / type / date-bound, one per data validation | 35 |
| Vocabulary membership, one per `Dropdown` column | 15 |
| **Total** | **555** |

The undecidable set stays at **7** — is the portfolio composition accurate; is the valuation appropriate; is the reg 119(3)(e) rationale adequate; are the AML-CFT answers truthful; was a complaint resolved satisfactorily; is the scheme correctly classified; is look-through data about other managers' schemes correct.

> **17/24 = 71% → 555/562 = 98.8%, in one afternoon, without writing a single interesting check.**

The decidable set is **unbounded** (one predicate per cell, per validation, per vocabulary, per cross-sheet carry — and 505 of them are literally generated by a `for` loop). The undecidable set is **fixed at 7 and does not grow with effort**, because it is bounded by what the artifact does not contain, not by what we have not yet written.

Therefore:

> **Coverage-as-a-fraction is a metric that improves monotonically with effort spent on the things that do not matter, and is invariant to effort spent on the things that do.**

That is a textbook Goodhart failure, and it is the *headline metric of the product*. Screen 2's coverage meter and Screen 4's "coverage over time — the demo, the pitch" are both charts of this quantity.

**Does the product have a customer?** On the 17 as enumerated: partly. Six of the 17 are genuinely non-trivial (register resolution against a live source, GSTIN check digit, template-version currency, NAV frequency vs. regulation, Principal Officer ≠ Compliance Officer, scheme-auth-date ≤ period-end). The other 11 are arithmetic a competent Excel user already has. But **none of the 17 addresses a single one of the 7**, and the 7 are where a filing actually goes wrong in a way that matters to a regulator.

**Does L6 move the boundary?** No — see Attack 3's finding and Attack 10.1. As specified it cannot, because metamorphic testing requires a re-executable system under test and a filed workbook is a record, not a program. In the strongest available repair (below) L6 moves the boundary by roughly **zero of the 7**, and adds more of the boring kind.

### The repair

**R1.1 — Retire the fraction as a headline. Replace with two numbers that cannot be traded off.**
Never `71%`. Always: **"N checks ran. K properties of this filing cannot be settled from this artifact."** K is the honest quantity. K does not fall when you add boring checks — which is exactly the property the fraction lacks.

**R1.2 — Fix the denominator by rule, not by taste.** The predicate enumeration must be *generated*, and the generator published, so a third party gets the same denominator:
```
one predicate per formula-evaluating cell        (505)
one per data validation                          ( 35)
one per shipped controlled vocabulary            ( 15)
one per "shall" clause in the FM Regulations that names a template field
one per admitted metamorphic / cross-period relation
```
Then the ratio is reproducible. It is still not *meaningful* — R1.1 is the fix for that — but it stops being adversarially manipulable by the party quoting it.

**R1.3 — Weight by consequence, from a source we do not control.** If a fraction must exist, weight predicates by an external signal: whether the clause they implement carries a penalty provision; whether the field feeds an IFSCA published aggregate; observed defect frequency from Attack 4's corpora. Report weighted and unweighted, always both.

**R1.4 — Replace the hand-classified 17/24 with the residue set (Attack 2).** Instead of a human declaring a predicate decidable, *measure* it: mutate the filing in ways that make it wrong, run everything, and report what survives. Adversarial, reproducible, and immune to inflation by boring checks.

**Label: MEASURED for the attack** (555/562 computed first-hand). **HOPED-FOR for R1.3** (no consequence-weighting source identified). **R1.1, R1.2, R1.4 are buildable now.**

---

## ATTACK 2 — "Mutation testing" is the wrong name, and the right name changes three things

### The attack

L4 test 1 seeds faults into **data**. Mutation testing mutates **the program under test**, to measure **test-suite adequacy**.

> "Mutation testing involves making small changes to the program being tested." … "The article clearly distinguishes: mutations alter the **program code itself**, not test inputs or data values."
> — *Wikipedia, Mutation testing* (opened; **SECONDARY** — the primary is DeMillo, Lipton & Sayward 1978, which I did **not** open: **UNVERIFIED**)

Consequences, in order of severity:

1. **The named tools are a category error.** ARCHITECTURE L4.1 lists *"mutmut for Python, PIT for JVM, Stryker for JS"*. All three mutate **source code**. None of them will ever be pointed at an `.xlsx`. If this reaches a slide in front of anyone who has run mutation testing, the design loses credibility on a detail that is trivially fixable. The mutation operators over the OOXML cell graph must be written by us; there is no off-the-shelf tool for it.
2. **The fault model is undeclared, and the mutation score means nothing without it.** In code mutation testing the operator set is standard and published (AOR, ROR, statement deletion…), so "MS = 0.8" is comparable across projects. Here the operator set *is the experiment*, and nobody has published one for financial filings.
3. **The equivalent-mutant analogue is not one class but two, and they point in opposite directions.**

### The correct methodology, named

The mapping the design wants is coherent — it is just not mutation testing:

| Role in mutation testing | Role here |
|---|---|
| program under test | the **filed artifact** |
| test suite | the **admitted predicate set** |
| mutant | a **corrupted filing** |
| mutation score | fraction of corrupted filings the predicate set rejects |

The correct names for this are **fault injection / error seeding** (the general technique) and, in the data-quality literature, **error generation for constraint-benchmarking**. Wikipedia's *Fault injection* article confirms fault injection is *"a testing technique for understanding how computing systems behave when stressed in unusual ways"* and — checked explicitly — **does not cover error seeding, Mills' seeding, capture-recapture estimators, or data corruption as a distinct methodology** (VERIFIED-AT-SOURCE that the article does not cover them; that is a gap in the source, not evidence the techniques do not exist).

I could not run a live search to confirm the canonical citation for benchmark error generation (the data-cleaning literature's `BART` is the artifact I believe fits: **UNVERIFIED — do not put it on a slide until opened**).

**Recommended name for the paper and the product: "seeded-defect adequacy."** It is honest, it does not borrow credibility from a technique we are not using, and it survives a referee.

### What changes

**(a) The denominator.**
```
Mutation testing :  MS = |killed| / (|mutants| − |equivalent|)
Seeded-defect    :  DA = |rejected| / (|seeded| − |innocuous| − |undetectable-in-principle|)
```

**(b) The equivalent-mutant analogue — two classes, not one.**

- **INNOCUOUS mutants** (the true analogue). A data edit that leaves the filing *correct*: reordering rows where order carries no meaning; reformatting `1000000` → `1,000,000`; changing a date's display format; rewording a free-text rationale; changing a genuinely unconstrained field. Like equivalent mutants, these **cannot be killed and must leave the denominator**, or the score is understated.
- **UNDETECTABLE-IN-PRINCIPLE mutants — no analogue in code mutation testing, and this is the important one.** A mutation that makes the filing **factually wrong** while leaving it **internally perfect**. Change the reported NAV from 100.00 to 100.05 and propagate it through all 181 cross-sheet carries and all 135 SUM relations. Every predicate passes. The filing is wrong. In code mutation testing, a mutant that changes behaviour is in principle killable by *some* test. Here, a mutant can change the *truth* of the artifact and be **provably unkillable by any predicate over the artifact alone**.

> **That third class is the product.** It is not a nuisance term in a denominator — it is the measured boundary that §2.5 says does not exist anywhere.

**(c) The fault-model coverage claim, and the honest ceiling.**
`DA = 0.82` licenses exactly one sentence: *"rejects 82% of the 340 defects I seeded, under fault model v3."* It does **not** license *"detects 82% of real filing errors."* In code, that bridge is the **coupling effect** — simple mutants couple to real faults — which Wikipedia states as a foundational hypothesis of the technique. There is **no coupling study for financial filing data**, and I could not run one. So the bridge does not exist and must not be walked across.

### The repair — **the residue set**, and it repairs Attacks 1, 2, 4 and 9 at once

```
1. Take the filing under test, F.
2. Generate mutants of F under a declared, versioned fault model.
3. Adjudicate each mutant: INNOCUOUS (still correct) / WRONG (materially false).
4. Run the full admitted predicate set + L6 on every WRONG mutant.
5. RESIDUE := { WRONG mutants that no predicate rejects }
6. Report |RESIDUE| and, for each survivor, the class of falsehood it represents.
```

Properties that make this the centre of the revised design:

- **It cannot be inflated by boring checks.** Adding 505 recompute predicates does not shrink the residue, because the residue is populated by falsehoods that are consistent with every arithmetic relation in the file. This is the exact property `71%` lacks.
- **It converts a hand-classification into a measurement.** §4.3's 17/24 was produced by one person deciding what is decidable. The residue set is produced adversarially and a third party can re-run it on the same file and get the same answer.
- **It is the deliverable of the research.** "Here is a class of falsehoods that survives every check anyone has written, on a real regulator's real return, and here is its size" — that is a publishable result and it is *the* result the brief says is missing.
- **It is the honest content of the Unchecked panel.** Today that panel lists reasons. It should list *demonstrated* survivors: "a coordinated 0.05% NAV misstatement survives all 555 checks — here it is."

**Label: HOPED-FOR but immediately buildable.** Nothing blocks it. Steps 1, 2, 4, 5 are mechanical; step 3 (adjudicating INNOCUOUS vs WRONG) is the only judgment, it is one-time per fault-model version, and it is exactly the kind of judgment a domain expert renders quickly and a reviewer can audit.

---

## ATTACK 3 — "Two model calls, both short"

### The attack

The claim does not survive contact, and it contradicts the architecture's own text in two places.

**It contradicts L2.** Split conformal prediction requires a held-out **calibration set** with labelled key-bindings and a nonconformity score **per item**. That is O(calibration set) model calls before the system runs at all, plus one prediction set per extracted fact. A 6,757-cell workbook does not yield one call.

**It contradicts L3.** SPADE is an *iterative* loop — I verified the abstract at source: it *"analyzes histories of prompt versions over time to create candidate assertion functions"* and then selects a subset under coverage and accuracy constraints. Generation, execution, scoring and selection are not one call.

**An honest count.** Splitting by phase, which is the thing the claim fails to do:

| Phase | Work | Model calls (order) |
|---|---|---|
| **Build** | Chunk + embed 399 circulars (7.3 MB text) for retrieval | 10³–10⁴ embedding calls |
| **Build** | Clause segmentation of a 102-page regulation | 10²  (or **0** — see repair) |
| **Build** | Relevance filter: which clauses constrain a template field | 10² |
| **Build** | Predicate generation per relevant clause, with repair loops | 10²–10³ |
| **Build** | Amendment-chain resolution for the 6/82 = 7.3% unresolvable targets | 10¹ |
| **Build** | Conformal calibration labelling | 10² |
| **Build** | Re-synthesis on template version change | × N versions |
| **Run** | Extraction from a **native xlsx** | **0** |
| **Run** | Extraction from an unstructured attachment | 10⁰–10² |
| **Run** | Verdict | **0** |

### The repair — and it makes the claim *stronger*

**R3.1 — Rewrite the property as: "Zero model calls in the verdict path."**

That is true, checkable, and far more valuable to a compliance buyer than "two short calls". It is enforceable as a *test*: assert that the process handling a filing opens no network socket to a model endpoint. A property you can assert in CI beats a property you assert in prose.

**R3.2 — State the real shape: build-time is batched, offline, human-reviewed, and amortised.** Predicate synthesis is a **library-construction** activity, not an inference-time activity. Its cost divides over 868 filings/year and over every future filing. Saying so converts an apparent weakness into the actual architecture.

**R3.3 — For a native `.xlsx`, a run has zero model calls, full stop.** Verified this lane: `openpyxl` recovers every cell, every formula, all 505 cached values, 54 validations, 12 defined names and the hidden sheet, deterministically. **L2's model is a contingency for unstructured attachments, not a stage in the main path.** The architecture currently presents L2 as one of two model-bearing layers on the critical path; it is not.

**R3.4 — Provenance anchoring costs zero extra calls if you make it a guard, not a task.** Require every generated predicate to emit a **verbatim quote** of the clause it implements; then `source_text.find(quote)` deterministically. No match → reject the predicate. This is the same shape as L2's key guard, it is free, and it kills clause hallucination at the boundary.

**R3.5 — Amendment-chain resolution is mostly deterministic already.** §4.2 measured 76/82 = 92.7% of amending circulars cite a resolvable target. Resolve those with a parser. The 6 remainder go to `UNCHECKED(rule ambiguous)`.

**Label: MEASURED** — R3.3 is verified first-hand on the real artifact. R3.1/R3.2/R3.4 are definitional rewrites, available now.

---

## ATTACK 4 — The corpus problem (the fatal one)

### The attack, in its strongest form

The brief already concedes this is *"the design's largest structural weakness"* and that a synthetic clean corpus *"is not a measurement of real filings."* **That concession is too weak.** The problem is not realism. It is circularity.

The same team authors the predicates **and** fills the clean corpus. Both come from one mental model of what a correct filing looks like. So the corpus is, operationally, *defined as* "filings that satisfy our predicates."

> **FFR measured on a self-authored clean corpus has expected value zero regardless of predicate quality. It is not a weak measurement — it carries no information at all.** A number that is guaranteed to come out at 0 before you run it is not a measurement; and printing "0.0% false failures across 340 clean filings" in the UI is *worse* than printing nothing, because it has the shape of evidence.

The consequences cascade further than the brief admits:

1. **L4 test 3 is unrunnable as specified.** So the gate has two working tests, not three.
2. **Therefore this sentence is false:** *"A check whose error rate is unknown is not admitted — which makes the coverage claim true by construction, not by discipline."* If FFR is uninformative, every admitted predicate's error rate **is** unknown, so by the gate's own rule **nothing may be admitted.** The claim "true by construction" is precisely the sort of unfalsifiable phrasing the brief's own Rule 1 forbids.
3. **The UX differentiator dies with it.** Screen 2's signature element — *"this check fired on 2.1% of 340 clean filings"* — is the thing the brief says no compliance product does. It is currently a number generated by us, about us.
4. **L2's conformal guarantee is void, not merely degraded.** Split conformal's coverage guarantee requires **exchangeability** between calibration and deployment data. A team-authored calibration set against real FME filings is a known distribution shift. Quoting "distribution-free, finite-sample coverage" under a known-violated assumption is a stronger error than a loose FFR, because it borrows a *theorem*.

### Every repair, ranked

**Rank 1 — The blind-fill firewall.** *Restores information content. Cheapest thing on this list.*
Person A fills clean workbooks from the **template and regulation only**, having never seen the predicate set. Person B authors predicates having never seen A's workbooks. Neither sees the other until measurement. FFR can now be non-zero, so it can now carry information. **This is the minimum bar below which no FFR may be printed anywhere in the product.** A second model instance with a clean context window is an acceptable Person A if — and only if — the prompt does not contain the predicates. *(The brief's own memory notes a related trap: context blobs pasted into subagent prompts get silently dropped. Here the requirement is the inverse and equally strict: the fill prompt must be auditable and predicate-free.)*

**Rank 2 — The template's own native formulas as an externally-authored oracle.** *The most under-used asset in the design, and it is already on disk.*
The workbook computes 505 cells itself, and **all 505 carry cached values** (verified this lane). Fill the input cells; let Excel/LibreOffice compute the derived cells. Any predicate that fires on a cell **IFSCA's own artifact computed** is a genuine false failure, because the ground truth was authored by the regulator, not by us. Denominator: 138 checkable relations over 505 formula cells. Limitation: covers arithmetic predicates only — it says nothing about the 7, and nothing about register resolution or vocabulary membership.

**Rank 2b — The strongest check nobody has proposed: formula-override detection.** Diff the *filed* workbook against the *blank* template. Any cell that carries a formula in the template and a literal in the filing is an **overwritten formula** — the single most common and most consequential real spreadsheet defect, and the classic route by which a wrong number is made to look computed. Sheet protection does not prevent it (protection is an application-level flag; 9 sheets carry SHA-512 `sheetProtection` hashes, and stripping them is a zip edit). This predicate needs **no corpus at all** — its oracle is the published blank template. It should be predicate #1 in the hand-authored set.

**Rank 3 — Privacy-preserving FFR from a real FME partner.** *The only construction that yields a genuinely real FFR.*
Run client-side; the FME returns **only aggregate firing counts per predicate**, never data. No NDA blocker, no data transfer, and it produces the one number that matters. n will be tiny (1 FME × 4 quarters = 4 filings) — which is fine if reported as an interval (R4.x below).

**Rank 4 — Differential testing between prescribed formats.** Where two of the 7 formats ask for the same quantity in different shapes, **the pair is an oracle** with no corpus required. All 9 workbooks are on disk. This is real, cheap, and it is the one repair that also serves Attack 7's transfer question.

**Rank 5 — Public spreadsheet corpora.** Supports a *different but defensible* claim: "our structural predicates fired on X of N real-world spreadsheets." Gives real human filling behaviour, which we otherwise have none of. Wikipedia's *Spreadsheet* article reports *"around 1% of all formulas in operational spreadsheets are in error"* (**SECONDARY**, no denominator given at source). It also cites a 2011 ClusterSeven survey of ~1,500 UK users — **and by the brief's own discipline that must be discounted: ClusterSeven sold spreadsheet controls, which is the exact "every cost figure traces to a party selling the data" problem the brief applied to corporate actions.** The named academic corpora (EUSES, FUSE, Enron, VEnron) I could **not** verify this session: **UNVERIFIED — open before citing.**

**Rank 6 — Held-out fault seeding.** Belongs on the *other* axis. It measures detection, not false failure. Listing it as an FFR repair is a category error in the queue as written.

**Rank 7 — Cross-template transfer.** Predicates written against the FME quarterly, evaluated against ALR / AL-monthly. Firing on a format they were not written for is a generalisation failure, not an FFR.

**Rank 8 — The regulator's published aggregates.** Not an FFR source. But genuinely useful for **realism**: IFSCA publishes FME and scheme counts by category (verified: 217 FMEs, 360 schemes as on Mar 2026, with per-category breakdowns). Construct the synthetic corpus so its **marginals match the published aggregates**. Does not fix circularity; does make the corpus less obviously fake, and it is free.

### Is there any construction under which a quoted FFR is honest?

**Yes, exactly one shape.** FFR is never a bare percentage. It is always a quadruple rendered inline, never in a tooltip:

```
FFR = (rate, corpus_id, corpus_provenance, n)   +  a two-sided interval
```

- `corpus_provenance ∈ {SELF-AUTHORED, BLIND-FILLED, TEMPLATE-COMPUTED, REAL-PARTNER, PUBLIC}`
- **`SELF-AUTHORED` renders the rate as `—` and the word `uninformative`.** Not a number. The schema forbids it.
- **Report a Wilson or Jeffreys interval, never a point estimate.** This single change makes small-n honest:

```python
def ffr_interval(fires, n, z=1.96):
    """Wilson score interval. n=4 and n=340 must not look alike."""
    if n == 0: return None
    p = fires / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0.0, c-h), min(1.0, c+h))

# 0 fires / 340 clean  -> [0.000, 0.011]   "at most 1.1%"
# 0 fires /   4 real   -> [0.000, 0.490]   "at most 49%"   <- honest, and it shows
```

A real FFR from 4 real filings with an interval of [0, 0.49] is **more honest and more useful** than 0.0% from 340 self-authored ones, and the UI should make the second literally impossible to render.

**Label: MEASURED for the attack** (the circularity is structural, not empirical). **Rank 2 and 2b are MEASURED-ready** — the artifact and its 505 cached values are on disk. **Rank 1 is buildable this week.** **Rank 3 is HOPED-FOR** — it needs a partner the project does not have.

---

## ATTACK 5 — "No green tick anywhere" vs a 100% coverage meter

### The attack

A coverage meter **is** a green tick with extra steps.

1. **100% is reachable in the UI as specified**, and when it reads 100% it is a green tick that took four seconds longer to render.
2. **71% is itself a summary statistic that can be wrong** — it inherits every error in the predicate set, every error in the schema induction that fixed its denominator, and the denominator is author-chosen (Attack 1). The product's central commitment is that a single confident summary is dangerous, and its headline is a single confident summary.
3. **A progress bar carries an implicit target of 100% and therefore a success state.** Users do not read "71% checked, 0 failures" as a scope declaration. They read it as "71% clean", then as "clean". The design cannot ship a shape whose entire visual grammar means *completion* and expect copy to override it.
4. **The export path is where the tick sneaks back in.** Someone screenshots the meter and pastes it into a board pack. Copy discipline does not survive a screenshot.

### The repair — at the level of pixels, copy and schema

**R5.1 — Kill the fraction in the hero. Two counts, equal weight.**
```
  0 failures across 555 checks.        7 properties were not checked.
  ───────────────────────────────      ───────────────────────────────
  (same type size, same weight, same ink, side by side, no colour on either)
```
The right-hand number is never smaller, never grey, never below the fold, never in a collapsed panel.

**R5.2 — No progress bar, no ring, no percentage.** Replace with a fixed-height **stacked band**, segments labelled with absolute counts. The unchecked segment is **hatched**, not muted — muted reads as "resolved, minor". Hatched reads as "not filled in", which is the truth.

**R5.3 — Nothing renders green. Ever.** Passing checks take the same neutral ink as body text. Only failures get colour. *The absence of colour is not the presence of green* — that is the whole visual thesis and it is achievable.

**R5.4 — Make 100% structurally unreachable.** The coverage denominator **must include the known-uncheckable**. A permanent, non-dismissible final row:
```
  Outside the boundary — properties no predicate can settle from this artifact alone   7
  Demonstrated survivors — corruptions that passed every check (residue set)          12
```
The residue count (Attack 2) is never zero, so the band never fills. **This is architectural, not cosmetic**: it changes what coverage is a fraction *of*.

**R5.5 — The meter carries its own provenance.** Under it, always: `denominator generated by rule v3 · predicate set v11 · qualified against template sha256:9f3c… · 4 predicates stale`. One click expands. A summary statistic that cannot be interrogated is the thing the product exists to oppose.

**R5.6 — Enforce the copy commitment as a build gate, not a value.** This is the cheapest high-integrity thing in the document:
```bash
# ci/no-green-tick.sh — fails the build
BANNED='✓|✔|✅|🟢|all clear|all-clear|no issues|looks good|verified clean|compliant|passed all|fully checked'
if grep -rniE "$BANNED" src/ templates/ locales/ ; then
  echo "FAIL: banned all-clear language or glyph in a user-facing surface"; exit 1
fi
```
A design commitment that is not tested is a preference. This makes it a property.

**R5.7 — Forbid the verdict at the schema level (L7).** The attestation JSON has **no `result` or `status` field**. Its top-level object is `scope`. There is no place in the schema to write "pass", so no downstream consumer can render one:
```json
{ "scope": { "checks_run": 555, "failures": 0,
             "unchecked": [{"reason":"requires judgment","count":7}],
             "residue": {"survivors": 12, "fault_model":"v3"} },
  "qualified_against": { "template_sha256":"9f3c…", "regulation_version":"2026-01-30",
                         "predicate_set":"v11" } }
```
Schema-level prohibition beats copy discipline, because it survives the screenshot, the API integration, and the intern.

**R5.8 — One sentence, permanently on Screen 2, because it is the honest limit:**
> **This system detects error, not deception. Every check here is a consistency check over a self-reported document. A coherent liar passes all of them.**

Nothing in the architecture addresses adversarial filers, and a supervisor who does not know that will misuse the output. Saying it costs nothing and it is the sentence that makes the rest believable.

**Label: buildable immediately, all of it.** R5.6 and R5.7 are MEASURED-ready (they are tests). The rest is design.

---

## ATTACK 6 — Version churn, and it is not hypothetical

### The attack, with a live instance found this lane

Three artifacts, three vintages, none aligned:

| Artifact | Vintage |
|---|---|
| FME reporting workbook on disk | **02 Jan 2026** |
| FM Regulations 2025 as consolidated (§6.3) | as amended to **30 Jan 2026** |
| **29th IFSCA Authority Meeting** | **24 Jul 2026** |

From `am_jul26.txt`, **VERIFIED-AT-SOURCE**, dated 17 days before today:

> "Decisions taken in the 29th IFSCA Authority Meeting dated 24.7.2026 … **A. Independent Valuation** 1. To reduce the operational burden on Fund Management Entities (FMEs), the periodicity for computation and disclosure of Net Asset Value (NAV) by close-ended Restricted Schemes **may be enhanced by the FME from semi-annual to annual, subject to prior approval of at least 75% of the investors in the scheme by value of their investments.** 2. Further, the requirement of obtaining an independent valuation of the portfolio of Venture Capital Schemes (VC Schemes), Restricted Schemes and Retail Schemes **shall be relaxed for the investments made in underlying scheme(s) which are valued by an independent entity.**"

This lands **directly** on the two most sophisticated predicates in the decidable-17:

- **Predicate #17** — *"latest valuation date vs NAV frequency owed under regs 27(1)/39(1)/51(1)."* Before 24 Jul 2026: pure date arithmetic. After: the owed frequency depends on **whether 75% of investors by value approved** — a fact **the workbook does not collect**.
- **The independent-valuer predicate** (regs 26(2)/38(2)/50(2), cited in §6.3): now relaxed conditional on how the underlying scheme was valued — again, a fact outside the artifact.

**This is exactly the case the brief asks about — "a predicate silently becomes untestable" — and it has already happened.** The predicate does not error. It does not abstain. It keeps computing a date difference and returning PASS or FAIL against a rule that no longer exists. A filer who lawfully moved to annual NAV gets a **false failure**; a filer who moved without the 75% approval gets a **silent pass**. Both outputs are clean, confident and well-formed.

And note the second-order effect: **reg 51(1) ends "in such manner as specified by the Authority"** (§6.3) — a live delegation hook. The rule can change by circular without the regulation changing, so **watching the regulation's version is insufficient**; the circular stream must be watched too. §4.1 found 0 hits for NAV-error language across 389 readable bodies — but **10 of 399 circulars are unreadable scanned images**. Predicate #17's correctness rests on a *negative search result over 97.5% of the corpus*.

### The repair — the versioning and re-qualification policy

**R6.1 — Keys are label-anchored, never coordinate-anchored.**
```
key    = (sheet_name, merged_header_path, row_label)   # identity, survives row insertion
coords = resolved attribute, re-derived per template version
```
A version bump becomes a **re-resolution**, not a rewrite. Unresolvable keys enter an explicit `UNRESOLVED` state that blocks the predicate; they never silently bind to the wrong cell.

**R6.2 — Every predicate carries a qualification record, and it is part of its identity.**
```json
{ "predicate_id": "nav_freq_vs_reg_27_39_51",
  "qualified_against": {
    "template_sha256": "9f3c…", "template_label": "FME_02012026",
    "regulation_version": "2026-01-30",
    "circular_corpus_snapshot": "2026-08-10T00:00Z", "circulars_unreadable": 10,
    "corpus_id": "blind-fill-v2", "corpus_provenance": "BLIND-FILLED", "n": 47 },
  "measured": { "seeded_defect_adequacy": 0.83, "fault_model": "v3",
                "ffr": 0.021, "ffr_ci95": [0.006, 0.074] },
  "liveness_witness": { "kill_case": "mutants/nav_freq_late.xlsx",
                        "pass_case": "clean/blind_fill_017.xlsx" },
  "state": "ACTIVE" }
```

**R6.3 — Any change to any element of `qualified_against` moves the predicate to `PROVISIONAL`.** It still **runs** (so detection is not lost) but:
- its measured numbers are **hidden** in the UI, replaced by *"not re-qualified for this template version"*;
- it **does not count in the coverage numerator**.

**Therefore coverage falls when the template changes.** That is correct, and it is the honest behaviour. A system whose coverage silently persists across a version boundary is lying.

**R6.4 — This kills "grows monotonically".** ARCHITECTURE Part 3 asserts the registry *"grows monotonically as L3/L4 admit new checks"*, and §5.3 repeats it. **Monotonic growth is incompatible with re-qualification and quarantine.** Both statements must go. Screen 4's "coverage over time" chart must be able to **step down** — and the step-downs are the most credible thing on that chart, because they are the only evidence the system notices when the world moves.

**R6.5 — The silent-untestable case, caught by a liveness witness.** Every predicate ships with a stored `kill_case` (a mutant it is *known* to reject) and a `pass_case` (a clean artifact it is known to accept). On every template version change — and on every run, see Attack 9 —

> **re-run both witnesses. A predicate whose `kill_case` no longer dies is quarantined automatically.**

This is the analogue of **vacuity detection** in model checking (an assertion that passes because its antecedent is never satisfied). I could **not** verify the canonical vacuity-detection citation this session (**UNVERIFIED** — Beer/Ben-David/Eisner/Rodeh is my recollection; open before citing). The *mechanism* needs no citation: it is two extra executions per predicate, and it converts a silent failure into a loud one.

Applied to the July 2026 amendment: predicate #17's `kill_case` was built against the semi-annual rule. It would still die, because the mutant and the predicate moved together — **so R6.5 alone does not catch a rule change.** That needs R6.6.

**R6.6 — Watch the instrument stream, not just the instrument.** A daily fetch of IFSCA's circular and Authority-meeting pages, content-hashed. Any new instrument that cites a regulation a predicate claims to implement puts that predicate into `PROVISIONAL` **automatically and pessimistically** — a human clears it. This is a diff-and-flag job, not an NLP problem, and it is the only mechanism that would have caught 24 Jul 2026.

**R6.7 — Carry the 10 unreadable circulars as a permanent declared gap** on every predicate whose correctness rests on the §4.1 negative result: `coverage_gap: 10/399 sources unread (scanned images)`. Or OCR them, which is an afternoon.

**Label: MEASURED for the attack** — the 24 Jul 2026 instance is verified at source, on disk. **R6.1–R6.5 and R6.7 are buildable now. R6.6 is HOPED-FOR** (needs an operational crawler and someone to clear flags).

---

## ATTACK 7 — Scale: 217 FMEs, 360 schemes, ~868 filings a year

### The attack

**Verified this lane** from IFSCA's own Q4 FY2025-26 bulletin: `Fund Management Entity (FME) 202 217` and `Fund Management AIFs/ Schemes 327* 360`. The 868 is **MODELED** — it is 217 × 4 and assumes every FME files every quarter.

**868 filings a year is ~3.4 per working day.** For comparison, that is a volume one competent person handles with a spreadsheet and a checklist.

**Is the supervisor user real? No — and the brief already killed them.**

PART 7 of the brief, under *"WHAT DIED (do not re-explore)"*:

> **"Supervisor-side SupTech for IFSCA — Procured.** NEC Corporation India awarded 27 Jan 2026, ₹39,57,36,115.52, scope includes an RE-facing portal; ₹300 crore turnover pre-qualification IFSCA refused in writing to lower."

And ARCHITECTURE Part 4, under *UX*, three sections later:

> "**Two users, one artifact.** … A supervisor receiving ~868 filings a year at 46% staffing triages an inbox sorted by coverage and failure count."

**One of the product's two named users was killed by the operator's own research and left standing in the UX section.** The scope of the procured system explicitly includes an RE-facing portal — which is also the filer-side surface. This is the single clearest internal contradiction in the corpus, and a judge who reads both parts will find it.

*(Separately: the "46% staffing" figure appears twice — ARCHITECTURE Part 4 and RND-BRIEF §5.4 — and **appears in none of the brief's evidence tables**. Source it or delete it. Rule 1.)*

**Is the filer user real?** More plausibly, but the value is unmeasured. 217 compliance officers, four workbooks a year each. They are not buying labour savings — a quarterly workbook is a day's work. They are buying **the avoided deficiency**: the observation in an inspection report, the rework, the Principal Officer's personal exposure. **Nobody has measured how often IFSCA returns an FME filing for correction.** That single number decides whether the product is worth anything, and it is question **9.6** in the queue — currently ranked sixth, behind three engineering experiments.

> **9.6 is not an errand. It is the demand-side settling experiment, and it should be joint-first with 9.1.** 9.1 asks "can we build it". 9.6 asks "does anyone need it". Running 9.1 first is the standing bias in Part 11 operating exactly as described: paying any price to avoid believing something false, and almost none to find out whether the thing is over.

**Is the architecture over-engineered?** As a deployment, yes, absurdly — eight layers, conformal prediction, signed attestation and a predicate registry for 3.4 documents a day. As a **research instrument**, no: the layers are how you make the measurement legible. The failure is not the design; it is presenting an instrument as a product.

### The repair

**R7.1 — Delete the supervisor user.** Restate: *"The supervisor is not the buyer. The supervisor is why the filer cares."* One sentence, and it removes the contradiction with PART 7.

**R7.2 — Name the unit of value honestly: the avoided deficiency.** Price unknown. Label **UNMEASURED**, and make 9.6 the way to measure it.

**R7.3 — Promote 9.6 to joint-first with 9.1.** One email. If IFSCA already runs these checks on receipt, the entity-facing product is a convenience, and the *research* result (the residue set, the boundary) is the entire value. Better to know that in August than in October.

**R7.4 — Say what the IFSCA workbook actually is: the testbed, not the market.** It was chosen because it is public, machine-readable, small enough to characterise exhaustively, and has a real regulator behind it. Those are the properties of a **good experimental subject**, and they are the honest reasons. The asset is the method: a qualification gate and coverage declaration for machine assertions over *any* structured regulated artifact.

**R7.5 — Add the transfer experiment, and put it second in the queue.** This is the one that decides whether this is a product or a paper, and **it is runnable today on material already on disk.** Nine workbooks sit in `scratchpad-oracle/`: ALR, AL monthly, Draft ACAC, EDR-1, IBU Operations, IFSCA Annual, ITFS Monthly, CMI Quarterly, FME Quarterly.

> **Measure: what fraction of the FME predicate set transfers to a second prescribed format, and what is the human cost per transferred predicate?**

Pre-register the threshold. If transfer cost per predicate is not materially below authoring cost, the method does not generalise and the honest output is a paper about one workbook. This doubles as Attack 4's Rank 4 repair.

**R7.6 — What would have to be true to matter beyond one regulator.** Exactly one thing: **schema induction plus predicate qualification must transfer across templates at bounded human cost.** Everything else — 8 layers, attestation, conformal — is downstream. R7.5 measures it directly, on nine workbooks, this week.

**Label: MEASURED for the attack** (217/360 verified at source; the PART 7 contradiction is textual and checkable). **R7.5 is MEASURED-ready** — the corpus is on disk.

---

## ATTACK 8 — Why does this need an LLM at all?

### The attack, answered honestly

**For the verdict path: it does not.** Verified this lane — for a native `.xlsx`, `openpyxl` recovers every cell, all 505 formula cells with cached values, 54 validations, 12 defined names and the hidden vocabulary sheet, deterministically, in under a second. **A run over a native workbook needs zero model calls.**

Of the eight layers, six are already marked deterministic. Of the two that are not:
- **L2 is a contingency**, not a stage — it earns its place only for unstructured attachments (Attack 3, R3.3).
- **L3 is a hypothesis** the brief itself has pre-registered a kill criterion for.

So the honest answer is: **mostly it does not, and the design already knows.** The architecture's own thesis sentence says as much — *"put the model only where generation is hard and verification is cheap"* — it just has not followed it to the conclusion.

**What happens to the pitch.** For a compliance buyer, "no AI in the verdict path" is the strongest sentence available and should be the headline. For a hackathon judged partly on *innovation and creativity*, it reads as a retreat. That trade is real and should be faced, not finessed.

### The stronger framing — small but load-bearing

Three roles survive scrutiny, each with the generate/verify asymmetry that justifies a model:

1. **L3 — proposing what to check.** ~50 predicates from a 102-page regulation plus 399 circulars is a human-hours problem, and every candidate is **cheap to falsify** by L4. Generation hard, verification cheap. This is the textbook case for a model and the only clean one here.
2. **Clause → field linking.** Which of 854 labels does a given "shall" clause constrain? A many-to-many matching problem over 8,866 "shall" occurrences; a human verifies each proposal in seconds. Same asymmetry.
3. **L2 for unstructured attachments only.** Real, narrow, contingent.

**And the reframe that makes the model's role load-bearing without overclaiming:**

> **The deliverable of 9.1 is not "L3 works." It is a number: of 10 model-proposed regulatory checks, k survived a three-test gate that was specified before the model ran.**

That number is publishable at any value of k. **k = 0 is a result** — it is the first measurement anyone has of whether a frontier model can write a regulator-grade executable check, and the brief's own §6.2 establishes the field is empty (zero financial regulations encoded in Catala, OpenFisca or Blawx; FINOS's demonstrator at 16 stars, no commit since 5 Jun 2024). Framed this way, the experiment cannot fail — it can only return a small k — and the model's role is small, honest, and the thing being measured.

**R8.1 — Make the qualified admission rate the headline result, not a gate on the product.**
**R8.2 — Lead the compliance pitch with "zero model calls in the verdict path" and enforce it as a test (R3.1).**
**R8.3 — For the hackathon, the innovation is not the LLM. It is the coverage boundary as a measured object** — the residue set. That is genuinely novel, the brief's §6.2 says no analogue exists for a financial assertion, and it does not depend on a model at all.

**Label: MEASURED** — the zero-model-call claim is verified first-hand on the real artifact.

---

## ATTACK 9 — Our own analogue of §4.4 (the most important hole)

### The attack

§4.4 is the pitch's strongest asset: two silent false negatives from **deterministic programs**, producing *"clean, confident, well-formed output that was wrong, with nothing to distinguish it from a correct answer."*

**Our system is a deterministic program that outputs "no failures."** The brief's argument applies to it with full force, and **nothing in the eight layers would catch it.**

L4 qualifies predicates **at admission**, against the corpus of that moment. Nothing re-checks, at run time, on *this* artifact, that the predicates still bind to anything. That gap is the hole.

**Part 1 of this document is the proof that the failure recurs.** Three fresh instances, found today, in the authoritative brief:

| # | Instance | Effect |
|---|---|---|
| 1 | `an.py` still reports `xsheet=0` on all 10 sheets, beside `an2.py`'s 195 | The §4.4 bug was patched by addition; the broken script still runs and still lies |
| 2 | 294 authored expressions read as 505 formula cells | §4.3's conclusion does not follow from §4.3's (correct) numbers |
| 3 | 3 list-validations vs 22 (19 hidden in `extLst`) | A 7.3× undercount of the template's own vocabulary enforcement |

**All three under-count in the same direction — the direction that supports the thesis.** That is the signature of a systematic instrument bias, and it is exactly what §4.4 warns about, one level up.

### Our specific failure modes, enumerated

```python
# 1. VACUOUS PASS — the classic, and the most likely to ship
def check_all_percentages_sum_to_100(cells):
    return all(abs(sum(g) - 100) < 1e-9 for g in group(cells))
# group() returns [] because the selector missed a renamed sheet
# all([]) is True.  Returns PASS.  Nothing checked.  Nothing logged.

# 2. EMPTY-SET ARITHMETIC
sum([]) == 0          # a "total" that matches because both sides are empty
len(rows) == declared # 0 == 0 passes when extraction silently returned nothing

# 3. SELECTOR DRIFT — literally instance #3 above
#    A regex over OOXML that cannot see <x14:dataValidation>.
#    Reports 3. Truth is 22. Confident, well-formed, wrong.

# 4. SCOPE TRUNCATION — the most dangerous of all
#    L1 iterates visible sheets. 'Dropdown' is state="hidden".
#    Its fields never enter the DENOMINATOR.
#    Coverage reads 100% of a scope that is silently short.

# 5. SHARED-DENOMINATOR ERROR
#    numerator and denominator come from the same parser.
#    The parser is wrong. The ratio is still 1.0. Invisible by construction.

# 6. SWALLOWED EXCEPTION
try:    result = predicate(artifact)
except: result = UNCHECKED          # <- there is no ERROR state in the vocabulary
```

On (6): L5's closed vocabulary is *no oracle exists · requires counterparty data · requires judgment · source unreadable · rule ambiguous · predicate not yet synthesised*. **There is no state for "the predicate raised."** A crashing predicate is currently indistinguishable from a philosophically-uncheckable property. That is a one-word fix with a large payoff.

### The repair — three self-checks, in priority order

**SC-1 (the centrepiece) — RUN-TIME SEEDED CANARIES.**

Prove, on the artifact just cleared, in the same execution, that the system can still find a fault it knows about.

```python
def verdict_with_self_check(filing, predicates):
    result = run_all(filing, predicates)

    canaries = []
    for p in predicates:
        # instantiate this predicate's stored kill-witness against THIS filing's cells
        mutant = p.kill_witness.apply(filing)
        if not run_all(mutant, predicates).rejected_by(p):
            canaries.append(p.id)

    if canaries:
        return Report(state="INVALID",
                      reason="self-check failed; these predicates did not fire on a "
                             "fault they are known to detect, in this artifact",
                      dead_predicates=canaries)
    return result.with_selfcheck(passed=len(predicates))
```

Why this is the answer:
- **It runs on the artifact under test, not on a training corpus** — so it catches parser drift, selector misses, renamed sheets, hidden-sheet truncation, encoding changes, and empty-set vacuity *for this file*.
- **The output is a third state: INVALID.** Not "clean", not "unchecked" — *"this system could not demonstrate it was working here."* That state does not currently exist and it is the single most important addition to the design.
- **It would have caught every one of the six modes above**, and both of §4.4's original failures.
- **Cost:** N predicates × 1 pipeline run on a 6,757-cell workbook. Milliseconds to seconds. There is no reason not to.
- **The nearest named prior art is SRE synthetic monitoring / canaries and hardware built-in self-test**, not anything in the testing literature — I could not verify a formal-methods citation this session (**UNVERIFIED**). The mechanism needs none.

And it is the best line in the pitch:

> **Every report carries proof that the checker was alive when it ran — on your document, not on a benchmark.**

**SC-2 — DUAL-PARSER DIFFERENTIAL INGEST. Fail the run on disagreement.**

```python
a = parse_with_openpyxl(path)      # object model
b = parse_with_raw_ooxml(path)     # zipfile + lxml over sheetN.xml + extLst
for field in ("n_sheets","n_cells","n_formula_cells","n_validations","n_defined_names",
              "sheet_names","hidden_sheets"):
    if a[field] != b[field]:
        raise IngestDisagreement(field, a[field], b[field])   # LOUD, not logged
```

**This lane is the proof it works.** Three implementations gave 244 / 294 / 505 on the same file. Two of them were already sitting in the same directory. **Nobody ran them against each other, and the divergence sat undetected in the authoritative document.** SC-2 is thirty lines and it converts that silence into a build failure.

Critically, the **coverage denominator must be computed twice, independently**, because mode (5) makes a shared-parser error invisible.

**SC-3 — Add `ERROR(predicate, exception)` to L5's vocabulary**, distinct from `UNCHECKED`. Any `ERROR` makes the run `INVALID`. One word, large payoff.

**SC-4 — Vacuity guard at execution.** Every predicate reports the **number of cells it actually bound to**. Binding to zero is an automatic `ERROR`, never a `PASS`. This alone kills modes 1, 2, 3 and 4.

**Label: HOPED-FOR but trivially buildable — and SC-2 is MEASURED**, in the sense that this lane ran the experiment and it found three real defects on first contact.

---

## ATTACK 10 — Everything else that is wrong, circular, unfalsifiable or unbuildable

### 10.1 — L6 cannot work as specified: there is no system under test

**The hardest technical finding in this lane.**

> "Metamorphic relations … **must involve multiple executions of the software**." … "Yes, metamorphic testing requires re-executing the system under test."
> — *Wikipedia, Metamorphic testing*, **VERIFIED-AT-SOURCE**; originated T.Y. Chen, 1998 HKUST technical report

ARCHITECTURE L6's relations are: *"reordering portfolio rows must not change NAV; adding a zero-value holding must not change NAV; consolidating two identical positions must not change NAV."*

**These are relations about the filer's NAV computation, which we cannot re-execute.** A filed workbook is a **record**, not a program. The NAV in it is a number someone typed or pasted. Reordering rows in a spreadsheet does not re-run a valuation engine; it reorders rows.

**L6 as written is unbuildable**, and it is the layer the design leans on hardest — *"this is what moves the 17/24 boundary"*, *"the most novel component and the most likely to produce a publishable result"* (9.3).

**Repair — identify the SUT, and there are exactly two candidates.**

- **SUT-A: the workbook as a spreadsheet program.** This one is real and re-executable. All **505 formula cells carry cached values** (verified this lane), so there is a baseline. Transform inputs, recompute with LibreOffice headless or a formula evaluator, compare. What it detects: broken internal consistency, and — most valuably — **hardcoded overrides of formula cells** (Attack 4, Rank 2b). What it does **not** touch: the valuation, the composition, the AML answers. **It moves approximately zero of the 7.**
- **SUT-B: the filer's valuation engine.** Not available. Would require the FME to run our transformations through their own system — a completely different product (and a far more interesting one).

**Also: relations are not self-validating.** Wikipedia states the technique *presumes* relation validity because relations express necessary properties of the intended function. **Ours would be authored by us or by a model, not derived from a specification.** So a violated relation means *the artifact is wrong* **or** *our relation is wrong*, and ARCHITECTURE's *"Every violated relation is a defect found without an oracle"* is false as stated. **Metamorphic relations must pass L4 like any other predicate.** In the current block diagram L6 sits *downstream of L5 and outside the qualification gate*.

**Rename the honest, valuable part.** The genuinely useful oracle-free checks here are **cross-period and cross-format invariants**, which are *differential testing*, not metamorphic testing:
- closing NAV of Q1 = opening NAV of Q2 (needs two filings)
- scheme count monotonicity against the register
- the same quantity asked by two prescribed formats must agree (Attack 4, Rank 4 — **runnable today on nine workbooks on disk**)

Call these what they are. The design is stronger with a correct small claim than a large unbuildable one.

### 10.2 — The block diagram is wrong

Part 3 draws L6 as a stage after L5. But metamorphic/differential probing **re-runs L0–L5 on transformed inputs**. It is a **loop over the pipeline**, not a downstream box. And L6's relations must route through L4 before use. Redraw, or the diagram teaches the wrong mental model to everyone who reads it.

### 10.3 — "True by construction" is unfalsifiable phrasing

> "A check whose error rate is unknown is not admitted — which makes the coverage claim true by construction, not by discipline."

It is true **given** that the qualification measurements are valid, which Attack 4 shows they are not yet. Rewrite: *"the coverage claim is true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement."* Longer, weaker, defensible. Rule 1 applies to the architecture's prose as much as to its numbers.

### 10.4 — "Grows monotonically" contradicts re-qualification

Stated in ARCHITECTURE Part 3 and RND-BRIEF §5.3. Incompatible with Attack 6's quarantine policy. Delete both. Coverage must be able to fall.

### 10.5 — The UI reuses 17/24's 71% as a coverage value

ARCHITECTURE Part 4: *"Coverage meter at the top: '71% of predicates settled.'"* But 71% is the **decidability ratio from §4.3**, not a coverage measurement of any filing. Two different quantities, one number, in the mock. Exactly the conflation the corpus's own rules forbid. **The demo must never display 71% unless 71% is what it computed.**

### 10.6 — "Coverage" is overloaded within the same document

L2 uses *coverage* in the **conformal prediction** sense (a probabilistic guarantee that the true label is in the prediction set). L5 uses *coverage* in the **predicate-fraction** sense. Two distinct technical meanings, three pages apart. Rename ours — **"settled fraction"** or **"declared scope"** — and reserve *coverage* for the statistical sense.

### 10.7 — The attestation creates an unassigned liability surface

L7 signs a coverage claim. **Who signs?** If the vendor, the vendor is attesting to a regulated filing. If the filer, it is self-attestation. If an FME shows an inspector a signed attestation over a filing that was wrong, the signature is the first exhibit. The design says nothing. R5.7's scope-only schema (no `result` field) is a partial answer; the signer question needs an explicit decision before L7 is built.

### 10.8 — Detects error, not deception

Every check in the design is a consistency check over a **self-reported** artifact. A filer who is internally coherent and factually false passes all 555. This is not a flaw to fix — it is the honest boundary — but it must be **stated on the report surface** (R5.8), or a supervisor will read silence as assurance. Which is the exact failure the product exists to prevent.

### 10.9 — Section 3.4's absence claim has no declared positive control

> "**No measured before/after with a control** for agentic AI at any financial institution exists anywhere."

Rule 2 requires a positive control and a coverage denominator before an absence is reported. None is stated for this one. Either declare the corpus searched or downgrade the claim.

### 10.10 — The unsourced 46%

Appears in ARCHITECTURE Part 4 and RND-BRIEF §5.4, in none of the evidence tables. Source or delete.

### 10.11 — Nine of ten sheets are protected, and it means nothing

`<sheetProtection algorithmName="SHA-512" hashValue="…" saltValue="…">` on 9 sheets. It is an **application-level flag**, not encryption — a filer can strip it with a zip edit and change any cell, including the hidden vocabulary sheet. **Do not build any predicate whose validity depends on a range being protected.** The workbook's protection is a UI convenience, not an integrity control, and the design should assume the filed artifact is fully mutable.

---

## PART 3 — PRIORITISED

### FATAL IF UNANSWERED

| # | Attack | Why fatal | Answerable? |
|---|---|---|---|
| **F1** | Attack 4 — FFR on a self-authored corpus is uninformative, so L4 has two tests, not three, and "true by construction" collapses | Every number the product displays flows through it | **Yes** — blind-fill firewall (Rank 1) + template-computed oracle (Rank 2) + intervals |
| **F2** | Attack 9 — no self-check; the system's own §4.4 failure is undetectable, and this lane found three fresh instances today | The pitch's strongest asset indicts the product | **Yes** — SC-1 canaries, SC-2 dual parser, SC-3 ERROR state, SC-4 vacuity guard |
| **F3** | Attacks 1 + 5 — coverage-as-a-fraction is Goodhart-broken (71% → 98.8% in an afternoon) and 100% is a green tick | The headline metric and the central design commitment | **Yes** — residue set + two-count hero + structurally unreachable 100% |

### MUST BE ANSWERED BEFORE THE DESIGN IS DEFENSIBLE

| # | Attack | Fix |
|---|---|---|
| M1 | **10.1** — L6 has no system under test; metamorphic testing requires re-execution | Name SUT-A, scope the claim to internal consistency + override detection, rename cross-period checks *differential*, route relations through L4 |
| M2 | **Attack 2** — wrong methodology name; mutmut/PIT/Stryker are a category error | Rename to seeded-defect adequacy; declare the fault model; adopt the two-class denominator; ship the residue set |
| M3 | **Attack 6** — version churn is live: 24 Jul 2026 already moved predicate #17's rule | Qualification records, PROVISIONAL state, liveness witnesses, instrument-stream watch |
| M4 | **Attack 7** — the supervisor user was killed in PART 7 and survives in the UX | Delete the user; promote 9.6 to joint-first; add the transfer experiment at #2 |
| M5 | **Attack 3** — "two model calls" contradicts L2 and L3 | Rewrite as "zero model calls in the verdict path"; separate build-time from run-time |
| M6 | **Part 1** — the §4.3 numbers describe expressions and are read as behaviour; DV count is 54/22 not 35/3 | Publish the corrected table; retire `an.py`; adopt SC-2 |

### CAN BE ANSWERED LATER

| # | Item |
|---|---|
| L1 | 10.7 — who signs the attestation |
| L2 | 10.6 — rename "coverage" to avoid the conformal collision |
| L3 | 10.2 — redraw the block diagram |
| L4 | L2's conformal machinery — it is a contingency for unstructured inputs, not a critical-path layer; defer until an unstructured input exists |
| L5 | 10.9, 10.10 — the unsourced 46% and the undeclared positive control in §3.4 |
| L6 | 9.5 — open every ⓐ arXiv identifier (still outstanding; this lane could not, search budget exhausted) |

---

## PART 4 — THE REVISED ARCHITECTURE

Changes marked **[+] added · [~] changed · [−] removed · [!] renamed**.

```
                      ┌──────────────── deterministic ─────────────────┐
 templates ──►  L0 ingest  ─────►  L1 schema induction  ──────────┐    │
 regulations ─►     │  [+] DUAL PARSER, fail on disagreement      │    │
 registers ───►     │  [+] instrument-stream watcher (daily hash) │    │
 filing ──────►     │                                        TemplateSchema
                    ▼                                             │    │
              ContentStore ◄──────────────────────────── key validation
                    │                                             ▲    │
        ┌───────────┴────────────┐                                │    │
        ▼ (contingency)          ▼ model                          │    │
   L2 extraction            L3 predicate synth                    │    │
   [~] ONLY for unstructured    (SPADE-style)                     │    │
       attachments; a native    [+] verbatim-quote provenance     │    │
       xlsx needs ZERO calls        guard (deterministic match)   │    │
        │                        │                                │    │
        │ Facts                  │ candidates                     │    │
        │                        ▼                                │    │
        │           L4 QUALIFICATION GATE ────────────────────────┘    │
        │           [!] seeded-defect adequacy (was "mutation testing")│
        │           [~] denominator − innocuous − undetectable-in-principle
        │           [+] FFR requires corpus_provenance ≠ SELF-AUTHORED │
        │           [+] Wilson interval, never a point estimate        │
        │           [+] emits liveness witnesses (kill_case, pass_case)│
        │           [+] metamorphic/differential relations pass HERE   │
        │                        │ admitted only                       │
        ▼                        ▼                                     │
   ┌──────────────────── L5 execution ────────────────────┐            │
   │  PASS / FAIL / UNCHECKED(reason) / [+] ERROR(pred)   │            │
   │  [+] every predicate reports cells_bound;            │            │
   │      cells_bound == 0  ⇒  ERROR, never PASS          │            │
   │  [+] denominator computed TWICE, independently       │            │
   └────────────────────────┬─────────────────────────────┘            │
                            │                                          │
        ┌───────────────────┴──── [~] L6 is a LOOP, not a stage ───────┤
        │  [!] L6 differential & invariant probes                      │
        │      SUT = the workbook-as-program (505 recomputable cells)  │
        │      [+] formula-override detection (template vs filing)     │
        │      [+] cross-format agreement (9 workbooks on disk)        │
        │      [+] cross-period continuity (needs 2 filings)           │
        │      [−] "reordering rows must not change NAV" — no SUT      │
        └───────────────────┬──────────────────────────────────────────┘
                            ▼
        [+] L6.5 SELF-CHECK ──────────────────────────────────────────┐
            run every predicate's kill-witness against THIS filing.   │
            any survivor ⇒ verdict state = INVALID.                   │
            [+] RESIDUE SET: wrong-mutants surviving ALL predicates   │
                            │                                         │
                            ▼                                         │
        L7 attestation ─────────────────────────────────────────────┘
            [~] schema has NO result/status field. Top level = scope.
            [+] carries qualified_against{} + residue size + fault model
```

### Layer-by-layer changes and why

**L0 — Ingest** · *deterministic*
- **[+] Dual-parser differential ingest.** Two independent implementations; disagreement on sheet count, cell count, formula-cell count, validation count, defined names or hidden sheets **fails the run**. *Why:* this lane got 244 / 294 / 505 from three implementations on one file, and two of them were already in the same directory, undetected.
- **[+] Instrument-stream watcher.** Daily content-hash of IFSCA's circular and Authority-meeting pages. *Why:* the 24 Jul 2026 meeting moved predicate #17's rule and nothing would have noticed.
- **[~] QuantMind reuse: demote to UNVERIFIED-pending.** Its shapes are Papers/News/Earnings/Factors/Theses. A protected xlsx with merged headers, a hidden sheet, `extLst` validations and 4 `#REF!` defined names is not in that family. **Queue item 9.7 should run before L0 is designed around it** — and note that `openpyxl` + `zipfile` already does everything L0 needs for this artifact class, so the dependency may be unnecessary.

**L1 — Schema induction** · *deterministic*
- **[~] Iterate ALL sheets including hidden.** The `Dropdown` sheet is `state="hidden"` and holds 15 controlled vocabularies; skipping it silently truncates the scope denominator.
- **[+] Parse `extLst` / `x14:dataValidation`.** 19 of 22 list validations live there. Missing them undercounts the template's own enforcement 7.3×.
- **[+] Materialise shared formulas.** 211 of 505 formula cells are `<f t="shared" si="N"/>` stubs. A text regex cannot see them, and the bias is systematically toward under-counting checking arithmetic.
- **[~] Keys are label-anchored** `(sheet, header_path, row_label)`; coordinates are a resolved attribute. Unresolvable ⇒ explicit `UNRESOLVED`, never a silent rebind.
- **[+] Pin vocabularies from the blank template's content hash**, never read them from the filed artifact. *Why:* `Dropdown` is the only unprotected sheet, and a filer can edit their own vocabulary.

**L2 — Fact extraction** · *model, contingency only*
- **[~] Demoted from critical path.** A native `.xlsx` needs zero model calls. L2 exists for unstructured attachments.
- **[~] Conformal coverage claim withdrawn unless exchangeability is argued.** A team-authored calibration set against real filings is a known shift; the guarantee is void, not degraded. Either argue exchangeability, restrict to a sub-task where it holds, or use the prediction set as a heuristic and say so.

**L3 — Predicate synthesis** · *model*
- **[+] Verbatim-quote provenance guard.** Every candidate emits an exact quote of its clause; `source.find(quote)` must succeed or the candidate is rejected. Zero extra model calls, kills clause hallucination at the boundary.
- **[~] Reframed as the measurement, not the gate.** The output is *k of 10 survived a pre-specified gate*. k = 0 is publishable.

**L4 — Qualification** · *deterministic, the gate*
- **[!] Renamed: seeded-defect adequacy.** *Why:* mutation testing mutates the program, not the data, and mutmut/PIT/Stryker will never run on an xlsx.
- **[~] Denominator:** `|rejected| / (|seeded| − |innocuous| − |undetectable-in-principle|)`.
- **[+] The third class is a first-class output**, not a nuisance term — it *is* the boundary.
- **[+] FFR admission rule:** a predicate cannot be admitted on a `SELF-AUTHORED` corpus. Provenance is part of the record.
- **[+] Intervals, never point estimates.**
- **[+] Emits liveness witnesses** used by L6.5 and by re-qualification.
- **[+] Metamorphic and differential relations are qualified here**, like any other predicate.

**L5 — Execution** · *deterministic*
- **[+] `ERROR(predicate, exception)`** added to the closed vocabulary; distinct from `UNCHECKED`; any ERROR ⇒ run INVALID.
- **[+] `cells_bound` reported per predicate; zero ⇒ ERROR, never PASS.** Kills vacuous-pass, empty-set arithmetic, selector drift and scope truncation in one rule.
- **[+] The scope denominator is computed twice, by independent code paths.**

**L6 — [!] Differential and invariant probes** · *deterministic, a loop*
- **[−] The three NAV-invariance relations.** No re-executable SUT.
- **[~] SUT declared: the workbook-as-program**, 505 recomputable cells with cached baselines.
- **[+] Formula-override detection** — template-vs-filing diff. Needs no corpus; its oracle is the published blank. Should be predicate #1.
- **[+] Cross-format agreement** across the 9 prescribed workbooks on disk.
- **[+] Cross-period continuity** where two filings exist.
- **[~] Honest claim: this moves ~0 of the 7.** It adds high-value boring checks. Say so.

**L6.5 — [+] SELF-CHECK · NEW LAYER · deterministic**
- Run every admitted predicate's kill-witness against **this** filing. Any survivor ⇒ **`INVALID`**, a third verdict state.
- Compute and publish the **residue set**.
- *Why:* this is the answer to §4.4 turned on ourselves, and it is the only layer that would catch the three defects Part 1 found.

**L7 — Attestation** · *deterministic*
- **[~] No `result` / `status` field in the schema.** Top-level object is `scope`. A downstream consumer cannot render a pass because there is nowhere to read one.
- **[+] Carries `qualified_against{}`, residue size, fault-model version, and the unread-source gap (10/399 circulars).**
- **[!] "Coverage" renamed "settled fraction"** to stop colliding with conformal coverage.
- **[?] Signer unresolved** — decide before building.

### The revised experiment queue

| # | Experiment | Change |
|---|---|---|
| **1a** | **9.1** — can a model write a correct executable check? | unchanged, still first, still pre-registered at 3/10 |
| **1b** | **9.6** — *one email to IFSCA: are these checks already run on receipt?* | **promoted from 6th to joint-first.** Demand-side settling |
| **2** | **[+] Cross-format transfer** over the 9 workbooks on disk | **new.** Decides product-vs-paper. Runnable today |
| **3** | **[+] The residue set** on the FME workbook | **new.** The publishable result and the honest boundary |
| **4** | **9.2** — corpus, **under the blind-fill firewall** | **rewritten.** Without the firewall it measures nothing |
| **5** | **[+] Formula-override detection** end-to-end | **new.** Highest value per hour; oracle is the blank template |
| 6 | 9.3 — relations, **rescoped to SUT-A and renamed differential** | rescoped |
| 7 | 9.7 — QuantMind on a protected xlsx | **run before designing L0 around it** |
| 8 | 9.4, 9.5 | unchanged |

---

## PART 5 — ASSETS: WHERE EACH FITS, AND WHERE IT STOPS

| Asset | Verified | Fits at | Where it stops |
|---|---|---|---|
| **SPADE** — arXiv:2401.03038 | **VERIFIED-AT-SOURCE** (abstract, authors, 14% / 21% / 2,000+ pipelines) | L3 + L4 | Criterion source is *prompt-version history*, confirmed verbatim at source. Our statutory substitution is untested — the transfer is exactly risk #4 in ARCHITECTURE Part 5 |
| **`openpyxl` + `zipfile`/`lxml`** at `/Users/abishaikc/Gift/.venv/bin/python` | **VERIFIED** — ran it | L0, L1 | Recovers 505 formula cells, all cached values, 54 validations, 12 defined names, hidden sheets. **This alone makes L2 unnecessary for native xlsx.** Stops at unstructured attachments |
| **The 9 prescribed workbooks** in `scratchpad-oracle/` | **VERIFIED** — opened | L6 differential, transfer experiment | Blank templates, not filings. Gives structure, not filling behaviour |
| **The blank template itself** | **VERIFIED** | L6 override detection | The only corpus-free oracle in the design. Covers formula overrides and vocabulary membership; touches none of the 7 |
| **IFSCA bulletins on disk** (`b_q4.txt`, `ar2425.txt`) | **VERIFIED** — 217 FMEs, 360 schemes Mar-2026 | Attack 7 denominators; corpus realism (Rank 8) | Aggregates only. No per-filing data, so no FFR |
| **`am_jul26.txt`** — 29th Authority Meeting, 24 Jul 2026 | **VERIFIED-AT-SOURCE** | L0 watcher, L4 re-qualification | Proves version churn is live. It is a *decisions* note, not the amending instrument — the gazetted text must be fetched separately |
| **Mutation testing literature** | **SECONDARY** (Wikipedia opened; DeMillo/Lipton/Sayward **UNVERIFIED**) | L4 naming and denominator | Mutates programs. **mutmut / PIT / Stryker do not apply to L4 test 1** — they apply to testing the *predicate implementations* |
| **Metamorphic testing** (Chen, 1998 HKUST TR) | **SECONDARY** (Wikipedia opened) | L6 | **Requires a re-executable SUT.** Kills L6 as written |
| **CycloneDX `compositions.aggregate`** | **PARTIAL** — field exists, described as *"how complete a relationship is"*. **The ten-state count is UNVERIFIED** (two fetches, both truncated) | L7 prior art | Verify the enum before it reaches a slide |
| **Public spreadsheet corpora** (EUSES / FUSE / Enron / VEnron) | **UNVERIFIED** — could not search | Attack 4 Rank 5 | Not IFSCA filings. Supports only a generic-structural-predicate claim |
| **Spreadsheet error base rate** — *"around 1% of all formulas in operational spreadsheets are in error"* | **SECONDARY**, no denominator at source | Problem statement | The adjacent ClusterSeven 2011 survey (~1,500 UK users) is **vendor-authored** and must be discounted by the brief's own rule |
| **in-toto / Sigstore** | **UNVERIFIED** this lane | L7 | Mature, but the **signer question is unresolved** and is a liability decision, not a technical one |

---

## PART 6 — WHAT THIS CHANGES ABOUT THE DESIGN

**1. The headline metric changes from a fraction to a pair, and the fraction stops being the pitch.** `71%` moved to `98.8%` in one afternoon under a different enumeration of the same artifact. A number that mobile cannot be the product's central claim. The headline becomes two counts that cannot be traded against each other, and the growth chart on Screen 4 must be able to step down.

**2. The product's central measurement becomes the residue set.** Not "how many predicates settled" but "**which falsehoods survive every check we have**". It is adversarial, so boring checks cannot inflate it; it is reproducible, so a third party can re-run it; and it is the direct measurement of the boundary §2.5 says exists nowhere. It replaces the hand-classified 17/24 with something that can be wrong in public.

**3. A third verdict state exists: `INVALID`.** Today the system can say PASS, FAIL or UNCHECKED. It cannot say *"I could not demonstrate I was working."* Given that the pitch's strongest evidence is two deterministic programs that produced confident wrong answers, that state is not optional. It is produced by L6.5's run-time canaries, on the artifact under test, in the same execution as the verdict.

**4. L4 loses a test and gains a firewall.** FFR on a self-authored corpus is uninformative, so the gate has two working tests until the blind-fill protocol exists. "True by construction" must go. `corpus_provenance` becomes part of every admitted predicate's identity, and `SELF-AUTHORED` renders as `uninformative`, not as a number.

**5. L6 shrinks and becomes buildable.** Metamorphic testing needs a re-executable system under test; a filed workbook is a record. The three NAV-invariance relations are deleted. What replaces them — formula-override detection against the blank template, cross-format agreement, cross-period continuity — is smaller, honest, needs no corpus, and includes the single highest-value check in the design. **L6 moves ~0 of the 7, and the design should stop claiming otherwise.**

**6. L2 leaves the critical path.** A native `.xlsx` run makes zero model calls. "Two model calls, both short" becomes "**zero model calls in the verdict path**", enforced as a test rather than asserted as prose — a stronger claim, and a checkable one.

**7. Version churn becomes a first-class state machine.** Qualification records, a `PROVISIONAL` state that hides numbers without losing detection, liveness witnesses that quarantine a predicate whose kill-case stops dying, and a watcher on the instrument stream. Justified not by principle but by an instrument dated 24 July 2026 that already moved the rule under predicate #17. **"Grows monotonically" is deleted.**

**8. One of the two users is deleted.** The supervisor was killed in PART 7 (NEC, ₹39.57 crore, 27 Jan 2026, scope includes an RE-facing portal) and left standing in the UX section. The filer remains, the unit of value is the avoided deficiency, its price is UNMEASURED, and **9.6 — one email — is promoted to joint-first**, because it is the only experiment that can tell you the thing is over.

**9. The IFSCA workbook is named for what it is: the testbed.** 217 FMEs and ~868 modeled filings a year is not a market. It is an unusually good experimental subject — public, machine-readable, exhaustively characterisable, with a real regulator. The asset is the method, and **the transfer experiment across the nine workbooks already on disk is what decides whether that is true.** It goes second in the queue.

**10. And the correction this lane owes the brief.** §4.3's arithmetic is exactly right and its conclusion does not follow: **294 counts authored expressions; the workbook evaluates 505 formula cells**, and per cell the checking arithmetic (27.3%) is comparable to the carrying (35.8%), not one-fifth of it. **The template enforces 22 controlled vocabularies, not 3.** All the errors run the same way — toward the thesis — because a text regex over OOXML cannot see the shared formulas and extension-list validations that *are* the workbook's checking logic. The good news is that the artifact is richer than believed and the two-day build has more material than budgeted. The bad news is the one that matters: **this is the §4.4 failure, it recurred three times in the authoritative document, and it will recur in our code unless something in the architecture is built to catch it.** That is L6.5, and it is the most important thing in this revision.

---

## PART 7 — OPEN QUESTIONS

1. **What is the residue set's actual size on the FME workbook?** The single most valuable unrun experiment. Everything above argues it should exist; nobody has run it.
2. **Does IFSCA already run these checks on receipt?** (9.6.) Decides whether the entity-facing product exists at all.
3. **What fraction of predicates transfers to a second prescribed format, at what human cost?** Runnable today on nine workbooks on disk.
4. **What is the CycloneDX `compositions.aggregate` enum?** Two fetches, both truncated. The "ten-state" claim in ARCHITECTURE L7 is currently **UNVERIFIED**.
5. **Do EUSES / FUSE / Enron / VEnron exist as usable corpora, with what licences?** Could not search.
6. **Is there a published coupling study** relating seeded data defects to real filing errors? If not, `DA` never licenses a real-world detection claim, and that limitation is permanent.
7. **Who signs the L7 attestation?** A liability decision, not a technical one.
8. **What is the gazetted text of the 24 Jul 2026 FM Regulations amendment**, versus the decisions note on disk?
9. **The 46% staffing figure** — source or delete.
10. **Every ⓐ arXiv identifier in §6.1 is still unopened** (9.5). This lane could not open them; the search budget was exhausted at the first query. The 26xx IDs remain plausible-but-unverified, and the brief's own warning stands.
