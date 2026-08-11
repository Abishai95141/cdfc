# LANE L6 — METAMORPHIC RELATIONS FOR A REGULATED FUND RETURN
### Checking relations between runs when no oracle exists. Literature verified at source, and the brief's five relations taken apart against the real artifact.

**Compiled 10 Aug 2026.** Every claim carries a warrant label:
**VERIFIED-AT-SOURCE** (I opened the primary artifact — paper PDF, repo, regulator's file, or ran the measurement myself) ·
**SECONDARY** (a credible source describes it; I did not open the primary) ·
**UNVERIFIED** / **NOT-FOUND** (could not check — a required and legitimate answer).

---

## PART 0 — THE HEADLINE, BEFORE THE EVIDENCE

Five things this lane found that change L6:

1. **The string `NAV` does not occur in any of the nine prescribed IFSCA workbooks on disk, in any XML part.** All five of the brief's metamorphic relations are stated as *"must not change NAV."* They are stated against a quantity the artifact class does not contain. (§7.1, VERIFIED-AT-SOURCE with positive controls.)
2. **Of the brief's five relations, four produce false alarms on a correct filing as written, and the fifth is vacuous.** Zero survive unmodified. (§8.)
3. **The single highest-value relation in the whole design is not in the brief:** four independent partitions of *funds raised* exist in the FME workbook (by investor category, by country, by accreditation status, and the Summary carry) and **the workbook enforces agreement between none of them** — Tables 4.2 and 4.3 contain zero formulas. This is the NASA-DAT pattern, needs no oracle, and a mismatch is unambiguously a defect. (§9, MR-11.)
4. **The measured literature says LLM-generated MRs score "markedly low" on novelty** — they recapitulate published relations. An LLM asked for MRs on a fund return will return exactly the brief's five. The domain-specific ones must be read off the artifact's own formula graph. (§3.4, VERIFIED-AT-SOURCE.)
5. **The brief's §4.3 formula census reproduces exactly** — 294 formulas, 181 cross-sheet carries, 35 SUM, 3 COUNTIF, 50 IFERROR, 14 IF, 11 other. I tried to correct it, and the correction was my own instrument bug. There is a real *extension*: 294 counts `<f>` elements carrying text; **505 cells actually evaluate a formula**, because 211 are shared-formula followers. For L6 the relevant unit is the evaluated cell. (§7.4.)

---

## PART 1 — METHOD AND COVERAGE DECLARATION

**Interfaces searched, and what each one actually covers.** A search box is not the corpus it searches; each is named with its real denominator.

| Interface | What it indexes | Used for |
|---|---|---|
| WebSearch (Google-backed, US) | open web, ranked, no total counts | discovery only, never for absence |
| `export.arxiv.org/api/query` | arXiv **metadata** — title, abstract, authors, comments, journal-ref. **NOT full text** | absence claims with exact `totalResults` |
| WebFetch on publisher/repository PDFs | the paper itself | every VERIFIED-AT-SOURCE citation |
| dblp record pages | curated bibliographic records | volume/issue/page verification |
| `unzip -p '*.xml'` over the 9 workbooks at `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/` | **every XML part** of each workbook — sharedStrings, sheet XML, formulas, inline strings | artifact absence claims |
| `openpyxl` + raw OOXML regex, `/Users/abishaikc/Gift/.venv/bin/python` | cell values, formulas, validations, protection, hidden rows | artifact measurement |

**Known coverage holes, stated up front:**
- arXiv is *not* where most metamorphic-testing work lands. Segura et al.'s survey drew 65 of 119 primary studies from IEEEXplore and **zero** from arXiv (arXiv was not among its six sources). An arXiv count is therefore a **lower bound on preprints**, not a statement about the field.
- ACM DL and IEEE Xplore both returned **HTTP 403** to WebFetch. Where I needed their records I used dblp (curated) or the author's self-archived copy. Two papers I could not open at all are marked SECONDARY below and named.
- I did not have institutional access to any paywalled full text.

---

## PART 2 — FOUNDATIONS, VERIFIED

### 2.1 The oracle-problem survey — exact citation, as requested

> **Barr, E. T., Harman, M., McMinn, P., Shahbaz, M., and Yoo, S. "The Oracle Problem in Software Testing: A Survey." *IEEE Transactions on Software Engineering*, vol. 41, no. 5, pp. 507–525, 1 May 2015. DOI 10.1109/TSE.2014.2372785.**

**Warrant: VERIFIED-AT-SOURCE (triangulated, two independent primaries).**
- The reference list of Rahman & Izurieta's IRI 2023 paper, whose PDF I opened in full, gives reference [1] verbatim: *"E. T. Barr, M. Harman, P. McMinn, M. Shahbaz and S. Yoo, 'The Oracle Problem in Software Testing: A Survey,' in IEEE Transactions on Software Engineering, vol. 41, no. 5, pp. 507-525, 1 May 2015, doi: 10.1109/TSE.2014.2372785."*
- Corroborated independently by the KAIST and UCL Discovery records surfaced in search.
- I could **not** open UCL Discovery directly (HTTP 403) and did **not** open IEEE Xplore. The article number 6963470 surfaced in search results and is **UNVERIFIED** — do not put it on a slide.

**The brief's ARCHITECTURE.md §L6 cites this as `41(5):507–525, 2015`. That is exactly correct.** Confirmed, no change.

### 2.2 The 1998 technical report

> Chen, T. Y., Cheung, S. C., and Yiu, S. M. "Metamorphic Testing: A New Approach for Generating Next Test Cases." Technical Report **HKUST-CS98-01**, Department of Computer Science, Hong Kong University of Science and Technology, 1998.

**Warrant: SECONDARY.** The report number `HKUST-CS98-01` is consistent across many secondary descriptions, but **I could not open the report itself** — HKUST does not serve it at a stable public URL that WebFetch could reach. Note that Rahman & Izurieta's reference [9], which I *did* read off the page, cites it **without** a report number: *"T.Y. Chen, S. C. Cheung and S. M. Yiu, 'Metamorphic testing: A new approach for generating next test cases', 1998."* Segura et al.'s survey (opened, p.1) says only *"a technical report by Chen et al. [5] published in 1998."*
**Recommendation: cite it as "Chen, Cheung and Yiu, 1998" and add the report number only if someone opens the PDF.** This is precisely the withdrawal class the brief's Part 8 exists to prevent.

### 2.3 The two surveys

| Work | Exact record | Warrant |
|---|---|---|
| Segura, S., Fraser, G., Sánchez, A. B., Ruiz-Cortés, A. **"A Survey on Metamorphic Testing."** *IEEE TSE* **42(9):805–824, 2016**, DOI 10.1109/TSE.2016.2532875 | dblp record opened + White Rose accepted-version PDF opened (cover page states *"IEEE Transactions on Software Engineering, 42 (9). pp. 805-824. ISSN: 0098-5589"*) | **VERIFIED-AT-SOURCE** |
| Chen, T. Y., Kuo, F.-C., Liu, H., Poon, P.-L., Towey, D., Tse, T. H., Zhou, Z. Q. **"Metamorphic Testing: A Review of Challenges and Opportunities."** *ACM Computing Surveys* **51(1), Article 4, pp. 4:1–4:27, 2018**, DOI 10.1145/3143561 | dblp record opened (full seven-author list, article number, page range) | **VERIFIED-AT-SOURCE** (dblp); ACM DL returned 403 |

**Segura et al. 2016, numbers read off the opened PDF — all VERIFIED-AT-SOURCE:**

- **119 primary studies**, published 1 Jan 1998 – 30 Nov 2015; search executed 30 Dec 2015. Filtered from 362 candidates.
- Sources: IEEEXplore **65**, Google Scholar (+5 citations) **16**, ACM DL **15**, Springer **13**, Elsevier ScienceDirect **6**, Wiley **4**. Total 119.
- **86 of 119** published 2009 or later.
- 183 distinct co-authors, 74 organisations, 72 venues. T. Y. Chen alone on **44 of 119**.
- Geography by first author: Australia 36, China 25, USA 17, Hong Kong 12, Germany 8, Spain 7, **India 5**, UK 3, Switzerland 3, Malaysia 2, France 1 — only 11 countries.
- Contribution type: case study **50%**, new technique **31%**, assessment/empirical **10%**, other 7%, **tool 2%**.
- Research topic: applications **49%**, **construction of metamorphic relations 19%**, integration with other techniques 10%, survey 7%, assessment 6%, execution 5%, source-test-case generation 4%.
- **145 distinct subject programs**; Java 46.2%, C/C++ 35.5%; sizes 12 to 12,795 LOC. Research programs 83 vs real-world 62 (cumulative to 2015).
- Source test cases: **random 57%**, existing test suite 34%, tool-based 6%, not reported 3%.
- *"metamorphic testing has been used to detect about **295 distinct real faults in 36 different tools, 23 of which are real world programs**."*

**The one finding from this survey that changes our design** (p.5, quoted): Chen et al. *"compared the effectiveness of metamorphic relations solely based on the theoretical knowledge of the problem (black–box) versus those derived from the program structure (white–box) using two case studies. They concluded that theoretical knowledge of the problem domain is not adequate for distinguishing good metamorphic relations. Instead, good metamorphic relations should be preferably selected with regard to the algorithm under test following a white–box approach."* The survey notes Mayer and Guderlei later disputed this.

**Why this matters to us:** we *have* the white box. L1 schema induction hands us the artifact's entire formula graph — 294 formula texts, 505 evaluated cells, 35 data validations, protection state, hidden rows. **Our MRs should be derived from that graph, not from fund-accounting theory.** The brief's five relations are pure black-box domain theory, and that is exactly the mode the literature measured as inadequate.

### 2.4 Necessary vs expected properties — the distinction the brief is missing

Xie et al., testing machine-learning classifiers by metamorphic testing (*Journal of Systems and Software*, 2011 — **SECONDARY**, I did not open the PDF; description consistent across the Columbia self-archive listing and search):

> Metamorphic relations represent **both necessary and expected** properties. Violation of a **necessary** property indicates a **fault** (verification). Violation of an **expected** property indicates **divergence between the algorithm and user expectation** (validation).

**This is the single most useful conceptual import for L6.** In a regulated filing the split is sharp and it maps directly onto the brief's PASS / FAIL / UNCHECKED vocabulary:

- A **necessary** MR is one entailed by the template's own formula graph or by the arithmetic of a partition. Violating it is a **FAIL**, full stop.
- An **expected** MR is a fund-accounting convention that admits lawful exceptions. Violating it must emit **ADVISORY**, never FAIL — otherwise it is a false-alarm generator.

The brief's five relations mix the two classes without distinguishing them, and every false alarm identified in §8 traces to that conflation.

---

## PART 3 — HOW ARE METAMORPHIC RELATIONS OBTAINED? (the crux)

### 3.1 The state-of-the-art survey of MR generation

> Li, R., Liu, H., Poon, P.-L., Towey, D., Sun, C.-A., Zheng, Z., Zhou, Z. Q., Chen, T. Y. **"Metamorphic Relation Generation: State of the Art and Visions for Future Research."** arXiv:**2406.05397** (v1 8 Jun 2024, v2 11 Jun 2024).

**Warrant: VERIFIED-AT-SOURCE** (abstract and HTML v2 opened). A journal version appears as *ACM TOSEM*, DOI 10.1145/3708521, under the title *"Metamorphic Relation Generation: State of the Art and Research Directions"* — **SECONDARY**, surfaced in search, record not opened.

**Numbers, read off the v2 HTML:** **75 papers** on systematic MR generation, 1 Jan 1998 – 31 Dec 2023; **57 of the 75 published 2019–2023.**

**Taxonomy, verbatim category names:**

```
1. Generation from EXISTING MRs
   └── Composition (build new MRs by combining component MRs)

2. Generation from SCRATCH
   ├── Artificial-Intelligence-based techniques
   ├── Metamorphic Relation Patterns
   ├── Category-Choice Framework based techniques   (this is METRIC)
   ├── Genetic approach
   ├── Search-based techniques
   └── Miscellaneous — data mutation · iterative development · NLP ·
       template-based · guideline-based · tabular expression ·
       behaviour-driven · online game · user forum · hierarchical
```

I could not extract per-category paper counts from the served HTML. **NOT-FOUND** — do not quote a distribution over these categories.

### 3.2 METRIC — the category-choice route

> Chen, T. Y., Poon, P.-L., Xie, X. **"METRIC: METamorphic Relation Identification based on the Category-choice framework."** *Journal of Systems and Software*, vol. **116**, pp. **177–190**, 2016.

**Warrant: SECONDARY.** ScienceDirect abstract page surfaced in search; I did not open it (paywall). The volume/page numbers came from search-result summary text and are **UNVERIFIED at source** — verify before publication.

**What it is, and why it is the most transferable method for us.** METRIC works inside the specification-based **category–choice** framework: a specification is decomposed into *categories* (parameters/environment conditions that affect behaviour), each category into disjoint *choices*, and a *complete test frame* is a consistent selection of one choice per category. MRs are then identified by systematically relating pairs of complete test frames. A successor, **METRIC+**, extends the technique to the *output* domain as well as the input domain (*"METRIC+: a metamorphic relation identification technique based on input plus output domains"* — **SECONDARY**, ResearchGate listing only).

**Fit for us: this is the method that mechanises MR authoring over our workbook, and it fits L1 exactly.** L1 already induces the field graph. Cast into the category-choice frame:

| Category | Choices (read off the artifact) |
|---|---|
| Scheme type | Venture Capital · Angel · Restricted Cat-I/II/III · Retail · ETF · Special Situation Fund · Family Investment Fund *(Dropdown!F3:F11, 11 values)* |
| Open/close-ended | Open-Ended · Close-Ended *(Dropdown!I3:I4)* |
| FME category | Registered FME (Retail) · Registered FME (Non-Retail) · Authorised FME *(Dropdown!J3:J5)* |
| Reporting quarter | Apr–Jun · Jul–Sep · Oct–Dec · Jan–Mar *(Dropdown!D3:D6)* |
| PMS provided? | Yes · No *(Intro C21)* |
| Third-party FM? | Yes · No · Not Applicable *(Dropdown!H3:H5, wired to Intro N54:N63)* |
| Scheme count | 1 … 10 · >10 (multi-instance, guidance C113) |

Seven categories, product of choices ≈ 11 × 2 × 3 × 4 × 2 × 3 × 11 ≈ **17,000 complete test frames** — and the *relations between adjacent frames* are precisely where the FME workbook's conditional logic lives: the `IF('2. Summary'!D5="Retail Scheme", 'Summary'!W5, 'Summary'!N5)` branch on Portfolio L3:L12, the `COUNTIF` scheme-type tallies at Intro D18:D20, the `AGGREGATE`-filtered third-party list at Intro C92:E101, the retail/non-retail column split at Summary I3:P3 vs Q3:X3, and the half-yearly gate on sheet 7. **Every one of those is a category-choice MR waiting to be written, and none of the brief's five touches any of them.**

**Where it stops:** METRIC requires a specification decomposed into categories. Ours is a spreadsheet plus prose notes, not a specification. The decomposition above is *mine*, hand-made in one pass; it is not derived and not validated. Someone must check it against the FM Regulations before it carries weight.

### 3.3 MR patterns (MRP / MRIP / MROP)

**Warrant: SECONDARY** — I did not open Zhou et al.'s or Segura et al.'s MRP papers; descriptions below are from search-result summaries and are consistent across three of them.

- **MRP** (metamorphic relation pattern): *"an abstraction that characterizes a set of (possibly infinitely many) metamorphic relations"* — Zhou et al., 2018.
- **MRIP** (input pattern): *"an abstraction that characterizes the relations among the source and follow-up inputs"* of a set of MRs.
- **MROP** (output pattern): the dual, over outputs.
- Segura et al. (**"Metamorphic Relation Patterns for Query-Based Systems"**, self-archived at `personales.us.es/sergiosegura/files/papers/segura19-met.pdf` — **not opened**) identify **six MROPs in terms of set operations for RESTful Web APIs: equivalence, equality, subset, disjoint, complete, difference.**

**Fit for us: the six set-operation MROPs are a near-perfect template for a filing.** A regulatory workbook *is* a query-based system — every table is a projection/aggregation over the same underlying population of schemes, investors and positions. Recast:

| MROP | Instance in the FME workbook |
|---|---|
| **equivalence** | funds raised by investor category (4.1 AA) ≡ by country (4.3) ≡ by accreditation (4.2 G) |
| **equality** | Portfolio 3.3 G (listed-debt total by grade) = Portfolio 3.1 E (listed debt securities), same scheme |
| **subset** | schemes reported in 1.7 (third-party managed) ⊆ schemes in 1.5 |
| **disjoint** | accredited investors ∩ non-accredited investors = ∅ (4.2) |
| **complete** | 1.5 scheme set = 1.6 service-provider set = 2.1 set = 3.1 set (all 10 rows, same population) |
| **difference** | scheme set(q) \ scheme set(q−1) = schemes authorised during the quarter |

**Where it stops:** MRPs are abstractions, not code. Each still has to be instantiated against real cell addresses, and the tolerance model is not part of the pattern.

### 3.4 Automated MR inference and mining

#### MR-Scout — mining MRs from existing test code

> Xu, C., Terragni, V., Zhu, H., Wu, J., Cheung, S.-C. **"MR-Scout: Automated Synthesis of Metamorphic Relations from Existing Test Cases."** arXiv:**2304.07548** (v1 15 Apr 2023; v5 11 Apr 2026). Journal ref: ***ACM TOSEM*, vol. 33, no. 6, Article 150, July 2024.**

**Warrant: VERIFIED-AT-SOURCE** (arXiv abstract page opened; journal reference read from the arXiv metadata).

Measured, with denominators as reported:
- Discovered **over 11,000 metamorphic test cases (MTCs)** from **701 open-source projects**.
- *"Over **97%** of codified MRs are of high quality for automated test case generation."*
- Codified-MR-based tests added to developer-written tests gave **+13.52% line coverage** and **+9.42% mutation score**.
- Developer comprehension: **55.76% to 76.92%** of codified MRs judged adequately understandable.

Related: **MR-Adopt** (automatic deduction of the input *transformation function*, ASE 2024, DOI 10.1145/3691620.3696020) and **MR-Coupler** (arXiv:2604.10126). Both **SECONDARY** — titles/venues from search, not opened.

**Fit for us — and it is a hard stop.** MR-Scout's premise is that *developer-written test cases embed domain knowledge encoding MRs*. **There is no test suite for an IFSCA filing.** There is a blank template, prose notes, and a regulation. The mining substrate does not exist. **MR-Scout is REJECT for L6.**

But the *idea* transfers with a substitution that mirrors the brief's own SPADE substitution at L3: **mine the template's own formula graph instead of a test suite.** The workbook's 294 formulas are the domain expert's encoded knowledge — they are what IFSCA's drafter believed must hold. §7.4 measures exactly how much is there.

#### LLM-generated MRs — the measured result

> Zhang, Y., Towey, D., Pike, M., Luu, Q.-H., Liu, H., Chen, T. Y. **"Integrating Artificial Intelligence with Human Expertise: An In-depth Analysis of ChatGPT's Capabilities in Generating Metamorphic Relations."** arXiv:**2503.22141v1**, 28 Mar 2025. Nottingham Ningbo + Swinburne.

**Warrant: VERIFIED-AT-SOURCE** — PDF opened, pages 1–3 read.

Setup: zero-shot prompting, **5 MRs per system under test**, **9 SUTs** ranging from simple programs to AI/ML-bearing systems; the anchor comparison is the autonomous-driving parking function from the authors' earlier study. Evaluated by human experts **and** a custom GPT evaluator, on **7 criteria each scored 0–5**: correctness, applicability, novelty, clarity, relevance to safety, overall usefulness, computational feasibility.

Measured results, quoted:
- *"The total score reveals that GPT-4, with a score of **24.0**, outperforms GPT-3.5, which had a score of **22.2**."*
  (Denominator: 7 criteria × 5 = **35 maximum**. The paper states the totals; **the 35 denominator is my arithmetic from its Table I scale**, so 24.0/35 ≈ 69% is a derived figure and must be labelled as such.)
- *"in terms of 'novelty', **all the MRs generated showed markedly low scores**. This suggests that the MRs show many similarities with the ones already established in the literature, indicating a lack of innovative content or original approaches."*
- *"'computational feasibility' is a standout feature for all MRs."* *"'Clarity' is consistently high across all MRs."*
- GPT-4 over GPT-3.5: *"a slight improvement in 'correctness'"*; *"clarity is significantly better"*; *"GPT-3.5 scores slightly higher"* on relevance to safety; equal on applicability and overall usefulness.
- The authors' framing is complementarity, not replacement: they underscore *"the irreplaceable value of human expertise in conducting critical and detail-oriented evaluation processes."*

Corroborating, from the MR-generation survey (arXiv:2406.05397 v2, opened): on ChatGPT-3.5 for autonomous driving, *"the relations generated by ChatGPT had varying quality, dependent on various factors... **Human interventions... were required to validate whether a generated relation was a correct MR**."*

Other work in this space, all **SECONDARY** (titles and venues confirmed by search; results not read at source, and several carry 26xx arXiv IDs I have not opened — treat exactly as the brief treats its ⓐ set):
- Zhang, J., Sun, C.-A., Liu, H., Dong, S. *"Can Large Language Models Discover Metamorphic Relations? A Large-Scale Empirical Study."* SANER 2025, pp. 24–35, DOI 10.1109/SANER64311.2025.00011. **I could not obtain its results — IEEE Xplore returned 403. Its headline number is NOT-FOUND.**
- *"Towards Generating Executable Metamorphic Relations Using Large Language Models"* (Springer, 2024; Univ. Luxembourg ORBilu record). Not opened.
- *"Bidirectional Empowerment of Metamorphic Testing and Large Language Models: A Systematic Survey"*, arXiv:2605.13898. **Not opened; 2026 ID unverified.**
- *"Validating LLM-Generated Programs with Metamorphic Prompt Testing"*, arXiv:2406.06864 — reported to detect **75% of erroneous GPT-4 programs at 8.6% false-positive rate** on HumanEval. **SECONDARY, not opened. If this number is used anywhere, open it first.**

**THE DESIGN CONSEQUENCE, and it is the sharpest thing in this lane.**

The measured signature of LLM-generated MRs is: **high correctness, high clarity, high computational feasibility, markedly low novelty.** That is a precise description of what you get if you ask a model for metamorphic relations on a fund return: *permutation invariance, identity-element insertion, duplicate consolidation, scaling homogeneity, round-trip.*

**Those are the brief's five relations.** They are the textbook MR classes — Murphy et al.'s six classes for ML (additive, multiplicative, permutative, invertive, inclusive, exclusive) with the labels changed. The brief arrived at them the same way a model would, and the low-novelty finding predicts precisely their failure mode: they are generic, so they are stated against a generic fund rather than against *this* artifact, and §8 shows what that costs.

**So: L3 (model-written predicates) and L6 (metamorphic relations) must not share a generation strategy.** L3 mines statute. L6 must mine the **formula graph and the sheet notes**, because that is where the non-generic relations are, and a model will not produce them.

### 3.5 Other automated routes, briefly

- **Search-based / genetic MR generation** — a named category in the 2024 survey. Fits a setting where you can *score* a candidate MR; we can (L4's mutation score). **EVALUATE**, not now.
- **Data-mutation-directed MR identification** (Sun et al., *Software: Practice and Experience*, 2024, DOI 10.1002/spe.3280 — **SECONDARY**, abstract page not opened). Closest in spirit to L4's mutation harness.
- **ML-predicted MRs from code representations** — the 2024 survey reports work using CFG/PDG features with SVM and decision trees on **48 scientific functions**, where *"the predicted MRs were effective in killing the majority of mutants"* and *"SVM seemed superior to DT."* No usable percentage given. **Not applicable:** a workbook has no CFG.

---

## PART 4 — MT IN DATA-HEAVY DOMAINS

### 4.1 Databases and SQL engines — the most mature analogue, and the best template

**Warrant: SECONDARY throughout this subsection unless flagged.** I did not open the SQLancer papers; the descriptions are consistent across the SQLancer repo's `docs/PAPERS.md` listing and multiple search summaries.

The three SQLancer oracles are worth naming because each is a *shape* we can reuse:

| Oracle | Mechanism | Our analogue |
|---|---|---|
| **PQS** (Pivoted Query Synthesis) | pick a random row, synthesise a query guaranteed to return it, check it does | pick one scheme, synthesise every table's view of it, check all agree |
| **NoREC** (Non-Optimizing Reference Engine Construction) | rewrite an optimised query into a form the optimiser cannot touch; compare | compute a total via the workbook's own SUM vs via an independent Python sum over the induced schema |
| **TLP** (Ternary Logic Partitioning) | split a predicate into `p`, `NOT p`, `p IS NULL`; the union must equal the unpartitioned result | partition the investor population three different ways; all must total the same |

Reported: *"PQS has found close to 100 bugs in widely-used DBMS."* **QTRAN** (ACM, DOI 10.1145/3728908) reports **24 previously unknown logical bugs, 16 confirmed**. **ValScope** (USENIX OSDI '26) is explicitly motivated by the gap that *"existing MT approaches mainly rely on equivalent or set-semantic relations, and thus fail to detect subtle bugs that preserve the result set while corrupting value semantics, such as faulty aggregation, ordering, or numeric computation."*

**That ValScope sentence is a warning aimed straight at us.** A pure set-equality MR over a filing will pass while the *values* are wrong. Every MR in §9 that asserts set or multiset equality is paired with a value-level assertion for exactly this reason.

**Also directly reusable — and the closest published thing to what L6 should be** (Segura survey §5.1.11, **VERIFIED-AT-SOURCE**): Lindvall et al. on NASA's **Data Access Toolkit**, a large telemetry database with an advanced query interface. *"Due to the massive amount of data contained in the database, checking the correctness of the query results is challenging. To address this issue, metamorphic testing was used by **formulating the same query in different equivalent ways, and asserting that the resulting datasets are the same**. Several issues were detected with this approach."*

**This is MR-11 in §9.** Same quantity, several inequivalent-looking derivations, assert agreement. No oracle anywhere.

### 4.2 Spreadsheets — thin, and the honest count

**arXiv metadata search, run 10 Aug 2026:**

| Query | `totalResults` |
|---|---|
| `all:"metamorphic testing"` | **186** ← positive control, non-zero |
| `all:"metamorphic testing" AND all:"autonomous driving"` | **9** ← second positive control |
| `all:"metamorphic testing" AND all:"spreadsheet"` | **0** |

From the Segura survey (**VERIFIED-AT-SOURCE**, §5.1.11): *"Chen et al. [120] claimed that metamorphic testing is both practical and effective for end-user programmers. To support their claim, the authors **briefly suggested** how metamorphic relations could be used to detect bugs in **spreadsheet**, database and web applications."* — a suggestion, not a case study.

Outside arXiv, two real spreadsheet-MT items surfaced (**SECONDARY**, neither opened):
- *"Error Trapping and Metamorphic Testing for Spreadsheet Failure Detection"*, **Journal of Organizational and End User Computing**, DOI 10.4018/JOEUC.2017040102. Reported conclusion: *"neither technique is sufficient in spreadsheet testing. Rather, ET and MT are complementary and they should be used together."*
- *"Implementation of Metamorphic Testing on Spreadsheet Applications"* (Academia.edu copy).

Adjacent and stronger, though not MT: **ExceLint** — *"ExceLint: automatically finding spreadsheet formula errors"*, *Proc. ACM Programming Languages* (OOPSLA), DOI 10.1145/3276518. **SECONDARY.** It finds formula errors by *spatial-structural anomaly detection over the formula layout* — no oracle, no relations. **EVALUATE for L1/L5:** it would flag the kind of defect I found by hand in §7.3 (a hidden orphan table block with live formulas) without anyone writing a rule.

**Defensible statement:** *Spreadsheet metamorphic testing exists but is a handful of papers in end-user-computing venues; the arXiv preprint corpus contains **0 of 186** MT papers mentioning spreadsheets in their metadata; the canonical MT survey records only a suggestion, not a case study. No published work applies MT to a regulatory reporting workbook.*

### 4.3 Financial software and accounting — the absence, properly controlled

**This is the claim the lane was told to make honestly, so here is the full apparatus.**

**Evidence 1 — the curated SE corpus (Segura et al., 119 studies, 1998–Nov 2015). VERIFIED-AT-SOURCE, quoted from the opened PDF:**

> *"The most popular domains are web services and applications (16%) followed by computer graphics (12%), simulation and modelling (12%) and embedded systems (10%). We also found a variety of applications to other fields (21%) such as **financial software**, optimisation programs or encryption programs. **Each of the other domains is explored in no more than four papers, to date.**"*

The timeline (Fig. 5) places "Financial software" first appearing around **2010**. The one named financial work (§5.1.11): *"**Sim et al.** presented a metamorphic testing approach for financial software. Several metamorphic relations were integrated into the commercial tool **MetaTrader** following a self-testing strategy. Source and follow-up test cases were derived from the real-time input price data collected at different time periods."* — MetaTrader is a retail FX/CFD **trading terminal**, not an accounting or reporting system. Also noted: *"Batra and Singh proposed using UML diagrams to guide the selection of metamorphic relations and presented a **small case study using a banking application**."*

**Evidence 2 — the arXiv preprint corpus. VERIFIED-AT-SOURCE (my own queries, 10 Aug 2026):**

| Query | `totalResults` | What the hits actually are |
|---|---|---|
| `all:"metamorphic testing"` | **186** | positive control |
| `all:"metamorphic testing" AND all:"autonomous driving"` | **9** | positive control — the interface does find domain applications |
| `all:"metamorphic testing" AND all:"financial"` | **3** | **none are about financial software**: 2606.22519 (homomorphic-encryption frameworks), 2401.00751 (machine translation), 2411.02077 (zero-knowledge circuits) |
| `all:"metamorphic testing" AND all:"regulatory"` | **0** | — |
| `all:"metamorphic testing" AND all:"spreadsheet"` | **0** | — |

**Evidence 3 — the one substantive banking-MT paper, opened in full. VERIFIED-AT-SOURCE:**

> Rahman, K., and Izurieta, C. **"An Approach to Testing Banking Software Using Metamorphic Relations."** Gianforte School of Computing, Montana State University. **24th IEEE International Conference on Information Reuse and Integration for Data Science (IRI), August 2023.** PDF: `https://www.cs.montana.edu/izurieta/pubs/IRI_2023.pdf`

Full setup and results, read off the pages:
- Three functions: **Deposit, Withdrawal, Transfer**, implemented in Java from a *"usability guideline for banking software design"* reference.
- **17 MRs total**: 5 for Deposit, 6 for Withdrawal, 6 for Transfer. All are directional arithmetic relations of the form *"add credit C > 0 to the initial input; the follow-up output will increase from the initial output"* — MR1 Addition, MR2 Subtraction, MR3 Multiplication, MR4 Division, MR5 Negative, MR6 Add-insufficient-fund.
- Mutants generated with **PIT**, active mutators listed (BOOLEAN_FALSE_RETURN, CONDITIONALS_BOUNDARY, MATH_MUTATOR, NEGATE_CONDITIONALS, …). **This resulted in 16 mutants.**
- Result, exactly as printed in Table III's Total row: **Mutation score 12/16 = 75%; Test strength 12/16 = 75%; line coverage 100%.**
- Per-function: Deposit all-MRs 4/6 = 67%; Withdrawal all-MRs 6/9 = 67%; Transfer all-MRs 6/9 = 67%.
- The authors' own threat to validity, quoted: *"The study utilized a one banking application with mathematical functions that perform standard calculations and a relatively small data set. Therefore, the results may not explicitly confirm that this approach will work for industrial-sized software."*
- Their stated future work is *"to improve the automation capability of MT by predicting MRs based on program execution flow."*

**Read the denominator: the headline "75% of mutants killed" is 12 of 16 mutants, on three textbook functions, on a program the authors wrote.** This is the closest published work to our domain, and it is a six-page conference paper whose entire evidence base is 16 mutants. Quoting "MT detects 75% of faults in banking software" without that denominator would be exactly the failure the brief's Rule 1 exists to prevent.

Also noted in passing, **SECONDARY**: *"An LLM Agentic Approach for Legal-Critical Software: A Case Study for Tax Prep Software"* (arXiv:2509.13471) applies MT to tax preparation, using directional relations (*increased income should lead to increased tax*). Not opened. Tax prep is the nearest legal-critical analogue to a regulatory return that I found.

**THE DEFENSIBLE ABSENCE STATEMENT, with its coverage denominator attached:**

> *Across (a) the 119-paper curated survey of metamorphic testing 1998–2015, where financial software falls inside the 21% "other" bucket and every domain in that bucket is explored in **no more than four papers**, with one named financial application (a retail trading terminal); (b) the arXiv preprint corpus, where **0 of 186** MT papers mention "regulatory" or "spreadsheet" in their metadata and the 3 that mention "financial" are about encryption, translation and ZK circuits; and (c) the one substantive banking-MT paper, whose evidence base is **12 of 16 mutants on three textbook functions** — **no published work applies metamorphic testing to a regulated financial filing, an accounting system, or a supervisory reporting artifact.** Coverage caveat: the arXiv API searches metadata, not full text, and arXiv supplied **0 of 119** primary studies to the canonical survey. This does not prove the field empty; it proves that nothing in these three corpora announces such work.*

That is a real, defensible novelty claim for L6 — the strongest one in the whole architecture. It survives adversarial review because it names what it searched.

### 4.4 Machine learning models

**SECONDARY** unless flagged. Murphy et al. identified **six MR classes for ML applications: additive, multiplicative, permutative, invertive, inclusive, exclusive.** Xie et al. applied them to **Weka 3.5.7's kNN and naive Bayes**, finding *"both algorithms violated some of the necessary properties identified as metamorphic relations"* and *"real bugs were detected in the open-source machine learning tool Weka."* (Segura survey §5.1.5, **VERIFIED-AT-SOURCE** for the Weka claim.)

**Relevance:** the six classes are the generic MR vocabulary. Our §9 set is organised by the same algebra — permutation ≈ permutative, identity-element ≈ additive with zero, scaling ≈ multiplicative, round-trip ≈ invertive, partition ≈ inclusive/exclusive. **We should say so explicitly** rather than presenting the classes as novel, because a reviewer will recognise them instantly. The novelty is not the classes; it is the instantiation against a statutory reporting template and the false-alarm analysis.

### 4.5 Scientific and numerical code

Segura survey (**VERIFIED-AT-SOURCE**): *"only 4% of the papers reported results in numerical programs, even though this seems to be the dominant domain used to illustrate metamorphic testing in the literature."* A gap between illustration and evidence — worth remembering when we illustrate with `sin(x) = sin(π − x)`.

Named: Chen et al. on partial differential equations for heat distribution in a square plate — *"Special test cases were unable to detect the fault, while metamorphic testing was effective at revealing it using a single metamorphic relation."* Also compilers: Le et al.'s equivalence-modulo-inputs approach *"detected 147 confirmed bugs in two open source C compilers, GCC and LLVM."*

**What transfers:** the *tolerance* discipline. Numerical MT is where accumulated floating-point error was first confronted, and it is why §9's tolerance model is per-MR rather than a global epsilon.

---

## PART 5 — PROPERTY-BASED TESTING AS THE EXECUTION VEHICLE

### 5.1 The measured case for PBT

> Ravi, S., and Coblenz, M. **"An Empirical Evaluation of Property-Based Testing in Python."** *Proc. ACM Program. Lang.* **9, OOPSLA2, Article 412 (October 2025), 32 pages.** DOI **10.1145/3764068**. CC-BY.

**Warrant: VERIFIED-AT-SOURCE** — PDF opened, pages 1–4 read.

Setup, with denominators:
- Corpus **426 Python programs** importing Hypothesis, from the Boa February 2022 GitHub snapshot; **0.42%** of projects in the overall dataset. Mean **29,972 LOC**, median **5,042 LOC**. **7,125 property-based tests** total.
- **12 formal categories** of property-based test; a static analyser classified **94%** of all PBTs in the corpus into one of them. A held-out set of **50** further projects was used to evaluate the categorisation.
- Mutation testing on **40** of the projects.

Results, quoted:
- *"each property-based test kills about **50 times** as many mutants as the average unit test"* — and *"even when controlling for the test suite's code coverage percentage."*
- *"tests that look for exceptions, that test inclusion in collections, and that check types are over **19 times** more effective at finding mutations than other kinds of property-based tests."* Exception-raising tests were the single most successful category.
- Parameter sweep: *"**55%** of mutations found were found with a single input, and **76%** within the first 20."*

The authors' own limitations, quoted, and they matter more to us than the headline:
- *"**98.4%** of all tests were unit tests, so overall, unit tests found more bugs than PBTs."*
- *"we cannot infer causation from our corpus study, which did not involve random assignment."*
- *"We also suspect that the bug-finding power of PBTs may not arise from the random generation of many test inputs: our parameter sweep experiments showed that over half of the mutations found by a PBT were found with a single input."*

**THE DESIGN CONSEQUENCE.** The measured benefit of property-based testing comes overwhelmingly **from the property, not from the search.** 55% of detections at n=1; 76% by n=20.

Our artifact has a **fixed geometry** — exactly 10 scheme slots, a fixed column set, a closed dropdown vocabulary. There is no large input space to search. That looked like a weakness for PBT; the measurement says it is not one. **A handful of well-chosen transformed workbooks captures roughly three-quarters of what unbounded random generation would.** L6 can be cheap and still be most of the value, and we can say so with a citation instead of a hope.

### 5.2 Hypothesis — the concrete mechanism

**Warrant: VERIFIED-AT-SOURCE** (`hypothesis.readthedocs.io/en/latest/stateful.html` opened).

The stateful API is the right shape for a workbook, because a filing is not a scalar — it is a *state* reached by a sequence of edits:

| Construct | Documented behaviour | Our use |
|---|---|---|
| `RuleBasedStateMachine` | must have ≥1 rule; a single function cannot define multiple rules | one machine per workbook-under-test |
| `@initialize` | *"a special case of rules, which are guaranteed to be run exactly once before any normal rule is called"* | load the blank template, induce the L1 schema |
| `@rule` | an action; may take strategies as arguments and return values into a `Bundle` | one rule per metamorphic transformation (permute, scale, zero-insert, …) |
| `Bundle` | *"a named collection of generated values that can be reused by other operations"*; `consumes()` draws and removes atomically | the pool of scheme slots, so a rule can claim slot *k* without collision |
| `@precondition` | *"used on rule-decorated functions… given a function that returns True or False based on the RuleBasedStateMachine instance"*; filters before execution, more efficient than `assume()` | gate retail-only rules on scheme type; gate sheet-7 rules on quarter |
| `@invariant` | *"Often there are invariants that you want to ensure are met after every step in a process"* — run automatically after each rule | **this is where the necessary MRs live**: after *any* sequence of transformations, the partition identities must still hold |

**The `@invariant` / `@rule` split maps exactly onto the necessary/expected distinction of §2.4.** Necessary MRs become `@invariant` — they must hold after *every* step, in every state. Expected MRs become assertions inside a specific `@rule`, where their preconditions are known to hold. That is a mechanical implementation of the FAIL/ADVISORY split, and it is why Hypothesis is the right vehicle and not merely a convenient one.

Two further features that earn their place:
- **Shrinking.** On failure Hypothesis minimises the input. For us that means: *"the smallest edit to a clean filing that breaks partition identity A2 is setting cell 4.3!C60"* — a report a compliance officer can act on, not a diff of two workbooks.
- **`@example`.** Explicit examples are always run alongside generated ones. Every real defect we ever find gets pinned as an `@example` and becomes a permanent regression — this is how the predicate registry grows monotonically, using the library's own mechanism rather than one we build.

**Where it stops:** the brief's §6.2 already says it — *"Relations must be authored."* Hypothesis generates *inputs*, never *properties*. It will not tell us that funds-raised has four partitions. Correct as written; no change.

### 5.3 Schemathesis

**Warrant: SECONDARY.** Schemathesis derives property-based test cases from an OpenAPI or GraphQL schema and runs them through Hypothesis; with OpenAPI `links` it produces *stateful* tests as dependent request sequences. One comparative evaluation reportedly found it detected **1.4×–4.5× more defects** than other API fuzzing tools (**UNVERIFIED** — I did not open the study; the academic reference surfaced was *"Automated Test Generation for REST APIs: No Time to Rest Yet"*, arXiv:2204.08348, also not opened).

**Fit: the architectural lesson, not the tool.** Schemathesis's whole idea is *the schema is the test generator*. We have an induced schema (L1) that is strictly richer than an OpenAPI document — it carries cell coordinates, merged-header geometry, native formulas, data validations with their bounds, protection state, and closed dropdown vocabularies. **The 35 data validations are already a generator specification.** I read the bounds directly: `decimal ≥ 0` on most monetary ranges, `whole ≥ 0` on counts, `date ≥ 32874` (i.e. 1 Jan 1990) on registration dates, `date ≥ 40179` (1 Jan 2010) on scheme authorisation dates, `decimal ≥ -5000000` on Portfolio E27:F27, `decimal ≥ -9999999999` on PMS C10:C11, `decimal ≤ 9.99999999999999E+21` on Portfolio J17:N26.

**A schema-to-strategy compiler is therefore a real, small, and genuinely reusable component** — perhaps 200 lines — that turns the induced L1 schema into Hypothesis strategies automatically. **ADOPT the pattern; do not adopt the tool** (it speaks HTTP, we speak OOXML).

### 5.4 The QuickCheck lineage

> Claessen, K., and Hughes, J. **"QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs."** *Proc. 5th ACM SIGPLAN International Conference on Functional Programming (ICFP '00)*, pp. **268–279**. DOI 10.1145/351240.351266.

**Warrant: SECONDARY** — page range and DOI consistent across the ACM DL listing and the UPenn-hosted PDF surfaced in search; I did not open either. A freely readable copy is at `https://www.cis.upenn.edu/~bcpierce/courses/552-2008/resources/icfp-quickcheck.pdf`.

Relevant because it is the origin of the *properties-as-code, generators-as-values* idea that Hypothesis inherits, and because Ravi & Coblenz note *"In a survey of 25,000 Python developers in 2023, 5% reported using Hypothesis, placing it as the 6th most used testing framework"* (**VERIFIED-AT-SOURCE**, read in the opened PDF) — i.e. the lineage is alive but niche, which is worth knowing before we build on it.

### 5.5 Differential and back-to-back testing

**Warrant: SECONDARY / definitional.**

Differential (back-to-back) testing runs the *same input* through *two or more independent implementations* and compares outputs; disagreement localises a fault without either implementation being an oracle. It is metamorphic testing's sibling: MT varies the input and fixes the implementation, differential testing fixes the input and varies the implementation.

Named instances from the opened Segura survey: Tao et al.'s *"equivalence preservation"* MR for compilers (generate an equivalent variant program, check the executables behave the same on random inputs — *"revealed two real bugs in two C compilers"*), and Le et al.'s profiling-and-pruning variant (**147 confirmed bugs in GCC and LLVM**). In the DBMS world, NoREC and DQE are the same idea.

**Direct application to our artifact, and it is available for free.** Every derived value in the filing has **two independent implementations already on disk**:
1. the workbook's own formula, as authored by IFSCA (e.g. `O3 = SUM(C3:N3)`), and
2. our L1-induced schema plus an independent evaluator we write in Python.

Running both and comparing is textbook back-to-back testing, and it needs **no ground truth and no second filing.** It catches: our parser mis-reading merged headers; our schema binding the wrong column; the filer having *overwritten a formula cell with a literal* — which is the single most likely real-world defect in a protected workbook, and which nothing else in the design detects.

**That last one deserves emphasis.** Nine of ten sheets are protected, but protection in OOXML is advisory — it is trivially removed. If a filer unprotects Portfolio and types `1234` over `O3 = SUM(C3:N3)`, the workbook still opens, still looks right, and every value in it is internally consistent because the inconsistency was *deleted along with the formula*. Only a differential check against the blank template's formula graph sees it. **This is MR-19.**

---

## PART 6 — THE ASSET TABLE (where each thing fits, where it stops)

| Asset | Licence / status | Warrant | Fits | Where it stops | Verdict |
|---|---|---|---|---|---|
| **Hypothesis** (Python) | MPL-2.0, mature | SECONDARY (licence not re-read) | **L6 execution vehicle.** `@invariant` = necessary MRs, `@rule` = transformations, `Bundle` = scheme slots, shrinking = actionable failure reports, `@example` = regression pinning | Generates inputs, never properties. Relations must be authored. No OOXML awareness | **ADOPT** |
| **Ravi & Coblenz OOPSLA 2025** | paper, CC-BY | **VERIFIED-AT-SOURCE** | Justifies a *cheap* L6: 55% of detections at n=1, 76% by n=20 | Corpus study, no random assignment, authors disclaim causation; 98.4% of tests in corpus were unit tests | **CITE** |
| **Segura et al. TSE 2016** | paper, self-archived | **VERIFIED-AT-SOURCE** | The denominator for every absence claim about MT in finance; the white-box>black-box MR finding that redirects our generation strategy | Corpus closes Nov 2015. Anything after is uncovered by it | **CITE — load-bearing** |
| **Chen et al. CSUR 2018** | paper | **VERIFIED-AT-SOURCE** (dblp record only) | Canonical framing citation alongside Barr et al. | I did not read its body. Do not quote its content | **CITE (record only)** |
| **Barr et al. TSE 2015** | paper | **VERIFIED-AT-SOURCE** (via opened reference list, ×2 sources) | Names the oracle problem; already correctly cited in ARCHITECTURE.md | Article number 6963470 unverified | **CONFIRMED** |
| **Rahman & Izurieta IRI 2023** | paper, self-archived PDF | **VERIFIED-AT-SOURCE** (full text read) | The only substantive MT-in-banking paper; its *weakness* is our opening | 17 MRs over 3 toy functions, **12/16 mutants**, authors disclaim generalisation | **CITE WITH DENOMINATOR** |
| **MR-Scout** | arXiv:2304.07548 / TOSEM 33(6) Art.150 | **VERIFIED-AT-SOURCE** (abstract) | Nothing directly | **Requires a developer-written test suite. An IFSCA filing has none.** Substrate absent | **REJECT** |
| **METRIC / category-choice** | JSS 116:177–190 (2016) | SECONDARY (page nos. unverified) | **L6 MR authoring method.** §3.2 maps our 7 categories onto the workbook's actual conditional logic | Needs a specification decomposed into categories; my decomposition is unvalidated | **ADOPT the method** |
| **MR patterns (MRP/MRIP/MROP)** | Zhou et al. 2018; Segura et al. 2019 | SECONDARY | The six set-operation MROPs map 1:1 onto workbook table relations (§3.3) | Abstractions, not code. No tolerance model | **ADOPT as checklist** |
| **SQLancer oracles (PQS/NoREC/TLP)** | MIT, active | SECONDARY | Three reusable oracle *shapes* for L6 (§4.1) | Built for SQL engines; none of the code transfers | **ADOPT the shapes** |
| **ExceLint** | OOPSLA, DOI 10.1145/3276518 | SECONDARY | **L1/L5.** Spatial-structural anomaly detection over formula layout — would flag the orphan block of §7.3 with no rule authored | Not MT. Finds *layout* anomalies, not value errors | **EVALUATE** |
| **Schemathesis** | MIT | SECONDARY | The *pattern*: schema → strategies. Our 35 data validations already specify generators | Speaks HTTP/OpenAPI, not OOXML. The comparative "1.4×–4.5×" figure is UNVERIFIED | **ADOPT pattern, not tool** |
| **QuickCheck** | ICFP '00, pp. 268–279 | SECONDARY | Lineage citation | Haskell; historical | **CITE** |
| **LLM MR generation** | arXiv:2503.22141 | **VERIFIED-AT-SOURCE** | Tells us **not** to use a model for L6 MRs: novelty scores "markedly low" | 9 SUTs, 5 MRs each, zero-shot, GPT-3.5/4 era. Newer models unmeasured here | **CITE — negative result** |
| **"Can LLMs Discover MRs?" SANER 2025** | DOI 10.1109/SANER64311.2025.00011 | SECONDARY (record only) | Would be the decisive measurement | **Its results are NOT-FOUND — IEEE returned 403. Do not cite a number from it** | **OPEN BEFORE USE** |
| **`openpyxl` + raw OOXML** | BSD / stdlib | **VERIFIED-AT-SOURCE** (ran it) | **L0/L1/L6.** Reads formulas, validations, protection, hidden rows | Does **not** evaluate formulas. `data_only=True` returns only Excel's *cached* values — which is why L6 needs its own evaluator (§10) | **ADOPT** |

---

## PART 7 — WHAT L6 ACTUALLY OPERATES ON

Everything in this Part is **VERIFIED-AT-SOURCE — I ran it myself, today,** against
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`.

### 7.1 There is no NAV

Full-XML grep (`unzip -p <file> '*.xml' | grep`) across **all nine** workbooks:

| Term | Hits, all 9 workbooks |
|---|---|
| `NAV` | **0** |
| `net asset` (case-insensitive) | **4**, all in the FME workbook |

**Positive controls on the same interface, same FME workbook:** `Scheme` → 123, `USD Million` → 31, `Portfolio` → 25, `Total Portfolio Value` → 9, `valuation` → 6, `Sixth Schedule` → 1. The instrument works.

The four `net asset` hits, in full:
1. `Net Assets` (a merged header)
2. `Net Assets under Management sourced through Distributors as at end of the quarter (USD Million)` — Table 4.4, column F
3. `Average Net Assets under Management for the quarter (USD Million)` — Table 2.1, column X
4. note 9: *"'Average Net Assets under Management for the quarter' is the average of the daily AuM of the Retail Scheme for the quarter."*

A separate grep for `per unit`, `unit price`, `no. of units`, `units outstanding` returns **0 across all nine workbooks.**

> **CONCLUSION. The FME quarterly return reports Net Assets Under Management for retail schemes as an aggregate in USD Million. It does not report NAV, does not report units in issue, and does not report NAV per unit. No prescribed IFSCA workbook on disk does.**

Every one of the brief's five L6 relations is written as *"must not change NAV."* They are stated against a field that does not exist in the artifact class. This does not make metamorphic testing wrong here — it makes **these five** relations un-runnable as written.

### 7.2 The geometry that constrains every transformation

| Sheet | Dimensions | Protected | Hidden rows |
|---|---|---|---|
| 1. Introduction | B1:X117 | yes | — |
| 2. Summary | A2:X26 | yes | — |
| 3. Portfolio | A1:Z190 | yes | — |
| 4. Investors | A2:AB89 | yes | **2–17** |
| 5. PMS | A1:AB83 | yes | — |
| 6. Complaints | A1:C45 | yes | — |
| 7. AML-CFT | A1:C59 | yes | — |
| 8. Compliance Status | A1:H19 | yes | — |
| 9. Compliance Report | B2:J27 | yes | — |
| Dropdown | D3:R14 | **no** | sheet itself hidden |

**Five structural facts that kill or reshape the naive transformations:**

1. **Ten scheme slots, hard-capped.** Guidance C113: *"This reporting format (excel sheet) has been designed to obtain data for up to 10 (ten) schemes for each FME. Therefore, if a FME has obtained authorisation for more than 10 (ten) schemes, it shall submit its quarterly filing by using more than 1 instances of such excel sheet."* You cannot "add a row." You can only occupy an empty slot, or spill into a second file.

2. **Per-scheme rows are positionally bound by formula.** `'3. Portfolio'!B3 = '1. Introduction'!D54`, `'2. Summary'!C5 = '1. Introduction'!D54`, `'4. Investors'!B21 = '2. Summary'!C5`. Row *k* of every per-scheme table is wired to row 53+*k* of Table 1.5. **Permuting one table's rows in isolation is not a valid transformation — it desynchronises the carry graph.** A permutation MR must permute the *source* (Introduction rows 54–63) and let the carries follow.

3. **Table 3.1 has no column-total row.** Rows 3–12 carry `O = SUM(C:N)` per scheme; there is **no** row 13 summing down the columns. Same for 3.2, 3.3, 3.4, 4.2, 4.3, 4.4. So an additivity MR over schemes has **no observable inside the workbook** — L6 must compute the aggregate itself. That is a feature: L6 manufactures observables L5 does not have.

4. **The reporting basis is mixed within one workbook.** Portfolio note 7: *"Information in Tables 3.1 and 3.2 should be provided on the basis of **direct investments** or borrowing activities undertaken in the scheme, and **not on look-through basis**."* PMS note: *"Information in Table 5.6 should be provided on a **look-through basis**."* **Any MR that adds a 3.x quantity to a 5.6 quantity is invalid by the artifact's own notes.**

5. **The values are cost-basis, to two decimals.** Guidance C111: *"Wherever applicable, the values of investments shall be provided on **cost-basis**, unless otherwise specified. Further, wherever applicable, the values may be filled up to **2 decimal points**."* Unit is USD Million throughout, so **the quantum is 0.01 USD Million = USD 10,000** and the maximum per-cell rounding error is **0.005 USD Million = USD 5,000.** This single sentence is the entire tolerance model.

### 7.3 A defect in the shipped blank template

Rows **2–17 of sheet `4. Investors` are hidden** and contain a complete, superseded table block with **live formulas**: `N5 = SUM(C5:M5)` through `N8`, and `N14 = SUM(C14:M14)` through `N17`. Their headers read *"Table 4.1: Details of investors in Investment Fund"* (A2) and *"Table 4.2: Funds raised from various categories of investors in Investment Fund"* (A11).

The **visible** tables on the same sheet are *"Table 4.1: Funds raised from various categories of investors"* at A18 and *"Table 4.2: Funds raised from various types of investors"* at A39.

> **The blank template ships with duplicate table numbers — "Table 4.1" at A2 and A18, "Table 4.2" at A11 and A39 — where the A2/A11 pair is an orphan block, hidden but formula-live, from a superseded revision.**

**Warrant: VERIFIED-AT-SOURCE** (row-hidden flags read from `row_dimensions`; cell contents and formulas read from the file).

Why this matters to L6, in three ways:
- It is a **worked example of the problem statement.** The template is protected, formula-bearing, and looks clean; a checker keyed on table *labels* would bind "Table 4.1" ambiguously and silently pick one. Cross-sheet carry `'2. Summary'!H5 = '4. Investors'!AB21` points at the *visible* table — but nothing in the label tells you that.
- It generates a real MR (**MR-20**): the hidden block must remain empty and must not contribute to any total, under every transformation.
- It is an argument for **ExceLint-style layout anomaly detection** at L1: nobody would have written a rule for "orphan hidden table with live formulas," and a structural anomaly detector would surface it unprompted.

### 7.4 The formula census — the brief confirmed, and extended

I attempted to correct the brief's §4.3 census and **found my own instrument was wrong.** My first OOXML tokenizer used `<f\b[^>]*>(.*?)</f>` with `re.DOTALL`, which matches a *self-closing* `<f t="shared" si="0"/>` as though it were an opening tag and then scans forward to the next `</f>`, swallowing intervening markup. It produced 53 garbage classifications. **This is the third instance in this project of the same failure class the brief documents in §4.4 — a regex over OOXML that cannot see the shape of the element it is matching. It produced clean, confident, well-formed output that was wrong.**

With a tokenizer that handles both forms (`<f\b(attrs)(?:/>|>(body)</f>)`), the brief reproduces **exactly**:

| Class | Mine, text-bearing `<f>` | % of 294 | Brief §4.3 |
|---|---|---|---|
| Cross-sheet carry | **181** | 61.6% | **181 (62%)** ✓ |
| IFERROR wrapper (incl. the 30 `IFERROR(AGGREGATE(...))`) | 20 + 30 = **50** | 17.0% | **50 (17%)** ✓ |
| SUM row/column total | **35** | 11.9% | **35 (12%)** ✓ |
| IF conditional carry | **14** | 4.8% | **14 (5%)** ✓ |
| Other / same-sheet ref | **11** | 3.7% | **11 (4%)** ✓ |
| COUNTIF tally | **3** | 1.0% | **3 (1%)** ✓ |
| **Total** | **294** | 100% | **294** ✓ |
| *Checkable (SUM + COUNTIF)* | **38** | **12.9%** | **38 of 294 (13%)** ✓ |

> **The brief's §4.3 formula census is CONFIRMED, class by class, at its own denominator. No correction.**

**The extension.** 294 counts `<f>` elements *carrying formula text*. The workbook contains **505** `<f>` elements; the other **211** are empty shared-formula followers (`<f t="shared" si="N"/>`) generated by **32** masters. Resolving each follower to its master's formula:

| Class | Formula-evaluating **cells** | % of 505 |
|---|---|---|
| Cross-sheet carry | 181 | 35.8% |
| **SUM aggregate** | **135** | **26.7%** |
| IFERROR wrapper | 100 | 19.8% |
| Same-sheet carry | 42 | 8.3% |
| AGGREGATE filtered list | 30 | 5.9% |
| IF conditional carry | 14 | 2.8% |
| COUNTIF tally | 3 | 0.6% |
| **Total** | **505** | 100% |
| *Checkable (SUM + COUNTIF)* | **138** | **27.3%** |

Per sheet (evaluating cells): Portfolio 250, Investors 88, Introduction 66, Summary 50, PMS 46, Compliance Status 4, Complaints 1, AML-CFT 0, Compliance Report 0, Dropdown 0.

**Which denominator L6 should use, and why it matters.** 294 is the right count of *distinct authored relations*. 505 is the right count of *cells a transformation can perturb*. For metamorphic testing the unit is the perturbable cell, so:

> **38 distinct checkable relation templates, instantiated across 138 evaluated cells.** Both numbers are true; they answer different questions. The brief's headline — *"the workbook moves numbers between sheets and that motion is counted as validation"* — survives under both denominators (44.2% of evaluated cells are pure carries; 61.6% of authored formulas are).

### 7.5 What the workbook does *not* enforce — the L6 opportunity

Sheets with **zero** formulas: `7. AML-CFT` (59 rows), `9. Compliance Report`. Tables with zero formulas despite obvious arithmetic: **4.2** (accredited/non-accredited, `G`/`H` totals blank), **4.3** (country breakup, no totals), **4.4** (distributors, no totals), **5.4**, **5.5**, **5.6**, **6.2** (complaint flow), **6.3** (appeals flow), **3.1/3.2/3.3/3.4** (no column totals over schemes).

**That is where L6 lives.** Every arithmetic relation the drafter implied in a note but did not wire into a formula is a checkable relation with no oracle requirement.

---

## PART 8 — THE BRIEF'S FIVE RELATIONS, TAKEN APART

Verdict summary, then one section each.

| # | Brief's relation | Sound? | False alarm on a *correct* filing? |
|---|---|---|---|
| 1 | Reordering portfolio rows must not change NAV | **No** — desynchronises the carry graph; no NAV field | **YES** |
| 2 | Adding a zero-value holding must not change NAV | **Partially** — money invariant, counts are not | **YES** |
| 3 | Consolidating two identical positions must not change NAV | **Not expressible** — no position-level rows exist | **YES** |
| 4 | Scaling the reporting unit must scale every derived total proportionally | **Partially** — degree-1 only, and needs a rounding tolerance | **YES** |
| 5 | Currency round-trip within tolerance | **Vacuous or underdetermined** | No — worse: **always passes** |

> **Four of five produce false alarms as written. The fifth is a null test that will always pass and silently inflate the coverage fraction. None survives unmodified.**

### 8.1 "Reordering portfolio rows must not change NAV"

**Three independent problems.**

*(a) There is no NAV.* §7.1.

*(b) The rows are not holdings — they are schemes.* Table 3.1's rows are the FME's ten scheme slots; its *columns* are the asset classes (Equity listed, Unlisted equity, Debt listed, Unlisted debt, Other Schemes in IFSC/India/Foreign, LLP interest, Physical Assets, Cash equivalents, Derivatives, Other instruments). There is no holding-level detail anywhere in the return. "Reordering portfolio rows" reorders *funds*, not *positions*.

*(c) The transformation as stated is invalid, and that is what causes the false alarm.* `'3. Portfolio'!B3` is not data — it is `='1. Introduction'!D54`. Permuting rows 3–12 of Table 3.1 while leaving Introduction rows 54–63 fixed re-pairs each scheme's *name* with another scheme's *amounts*. The resulting workbook is genuinely wrong. A checker that applies this transformation and then flags the difference has flagged **a defect it introduced itself**, on a filing that was correct.

Additionally, `L3 = IF('2. Summary'!D5="Retail Scheme", '2. Summary'!W5, '2. Summary'!N5)` reads Summary row 5 regardless of which scheme now sits in Portfolio row 3 — so the transformation also crosses the retail/non-retail branch.

**The fund-accounting exception the prompt asked about — lot-level cost basis and FIFO/average-cost ordering — is real in general but does *not* bite this artifact.** Guidance C111 puts values on **cost basis**, aggregated to asset-class buckets, with no disposals and no realised-gain-on-disposal field. Lot-matching order cannot change any figure in Tables 3.1, 3.3 or 3.4. It *could* affect Table 3.2 column M (*"Net Gains / Losses booked on cumulative basis on Derivative Contracts"*), which is a realised figure — but that ordering happens upstream in the FME's ledger, not inside the filing, so no MR over the filing can see it. **Honest answer: the classic ordering exception is inapplicable here, and saying so is more useful than repeating it.**

**Repair → MR-01, MR-02** (§9).

### 8.2 "Adding a zero-value holding must not change NAV"

**Half right, and the wrong half is the expensive one.**

You cannot add a row (ten fixed slots, §7.2). The nearest valid transformation is: occupy an empty scheme slot with a scheme carrying all-zero amounts.

- **Money is invariant.** ✓ Every `SUM` gains a zero. Necessary property, holds.
- **Counts are not invariant.** ✗ `Intro D17 = SUM(D18:D20)` and the three `COUNTIF(G54:G63, "*Retail*")`-family tallies at D18:D20 all increment. So do Summary F (*No. of Investee Companies*), Table 3.4 D (*No. of startups invested in*) and F (*No. of investments in infrastructure*), and Investors AB (*No. of Investors*).

A relation stated as *"adding a zero-value holding must not change the filing"* fires on Intro D17–D20 **on a correct filing.** That is a false alarm, and it is not a rare edge case — it is guaranteed, every time the MR runs.

The correct statement is a **typed** one: money invariant (degree-1 quantities), counts **equivariant** (+1). Which requires a degree map over every field — which the brief does not have, and §9 supplies.

*Genuine zero-value insertion that is fully invariant:* setting an already-blank asset-class cell to `0.00` (e.g. Portfolio K, *Physical Assets*). Money and counts both unchanged. That is **MR-04**, and it is a real necessary property — it tests whether the checker distinguishes *blank* from *zero*, which the workbook itself does not (Table 3.1 ships pre-filled with literal `0`s, while Investors Table 4.2 rows 42–51 ship truly blank).

**Repair → MR-04, MR-05, MR-06.**

### 8.3 "Consolidating two identical positions must not change NAV"

**Not expressible on this artifact.** There are no position rows to consolidate. Positions arrive pre-consolidated into eleven asset-class buckets per scheme. The consolidation the MR describes happens in the FME's books, upstream of anything IFSCA receives.

Forcing it onto scheme rows — merging two rows into one whose amounts are the sum — is **not** value-preserving: the scheme count drops by one, `Intro D17` and the `COUNTIF` tallies fall, and `Table 1.7`'s `AGGREGATE`-filtered third-party list changes length. A checker asserting invariance false-alarms.

**But the inverse transformation is one of the most valuable MRs in the set, and it is fraud-shaped.** Take one scheme with amount *A* and split it across two slots as *a* + *b* = *A*, with the same authorisation number. Money aggregates are invariant; scheme count rises by one; and `D17` now disagrees with the count of distinct authorisation numbers and with the live register. **Splitting or duplicating a scheme to move money between reporting buckets is detectable purely by the disagreement between the money relation and the count relation — no oracle, no register lookup.** That is **MR-07**.

**Repair → MR-07** (and record MR-3 as inexpressible-on-this-artifact, expressible on the source ledger).

### 8.4 "Scaling the reporting unit must scale every derived total proportionally"

**The soundest of the five, and still a false-alarm generator in two independent ways.**

*(a) "Every derived total" is wrong — the workbook is not homogeneous.* Fields partition by degree:

| Degree | Behaviour under ×λ | Fields |
|---|---|---|
| **1** (money) | scales by λ | all `USD Million` columns; Portfolio C–O, Summary G, J–X, Investors amounts, PMS amounts |
| **0** (counts) | **invariant** | Intro D17–D20, D35; Summary F, H, I; Portfolio 3.4 D, F; Investors D,F,…,Z,AB; Complaints 6.2/6.3 |
| **0** (ratios) | **invariant** | AML-CFT 1f (*Percentage of total customers classified High risk*) |
| **0** (time) | **invariant** | Intro I54:I63 (*Tenure in Years*), all 15 date fields |
| **0** (categorical) | **invariant** | all 16 `Whether…` yes/no fields, all dropdown selections, names, GSTIN, PAN |

A relation asserting that *every* derived total scales fires on Intro D17–D20 and on Portfolio 3.4 D/F **on a correct filing**. Guaranteed false alarm.

*(b) Two-decimal rounding breaks exact proportionality, and this is the deeper problem.* Guidance C111 fixes two decimals on USD Million. If the filer re-derives each cell as `round(λ·xᵢ, 2)`, then for a row of *n* cells:

```
| Σᵢ round(λ·xᵢ, 2)  −  λ·Σᵢ xᵢ |   ≤   n × 0.005 USD Million
```

For Table 3.1's `O = SUM(C3:N3)`, *n* = 12, so the worst-case discrepancy is **0.06 USD Million = USD 60,000** — on a *correct* filing. An MR with a fixed epsilon of, say, 0.01 fires. **The tolerance must be a function of the number of summands, not a constant.**

*(c) A third trap, smaller but sharper: rounding mode.* Excel's `ROUND` is round-half-away-from-zero. Python's built-in `round` is **round-half-even** (banker's rounding). `round(0.125, 2)` is `0.12` in Python and `0.13` in Excel. A checker using Python floats will disagree with a correct filing at every exact half. **L6 must use `decimal.Decimal` with `ROUND_HALF_UP`, and must never compare floats with `==`.** This is a one-line fix that would otherwise produce an irreproducible trickle of false alarms.

*(d) And the transformation may be forbidden outright.* Guidance C109: *"The headings of the tables, rows, columns and the information in drop-down or pre-filled / auto-filled cells **shall not be modified**."* The unit "USD Million" is written into the table headings. Re-denominating to USD Thousand modifies a heading. So the *literal* transformation the brief proposes is prohibited by the instrument; the sound version scales the *values* while holding the declared unit fixed, which is a checker-internal test rather than an artifact test.

**Repair → MR-08, MR-09, MR-10.**

### 8.5 "Currency round-trip within tolerance"

**This one is not a false alarm. It is worse: it is a null test that always passes, and every passing null test inflates the coverage fraction the whole product is built on.**

Guidance C110, verbatim:

> *"If a currency conversion is required for the purpose of this report, FME may undertake the conversion at the same rate as applicable on the date of such transaction."*

Read the clause. Conversion is at the **transaction-date historical rate**, per transaction — not at a single reporting-date rate. So a reported aggregate in USD is a sum of amounts each converted at a *different* rate:

```
reported_USD  =  Σᵢ  amountᵢ_FCY  ×  rate(dateᵢ)
```

Now consider the proposed round-trip:

- **If you round-trip through a single rate *r*:** `x → x·r → (x·r)/r = x`. This is arithmetically true for any *x* whatsoever. It tests IEEE-754 float behaviour and nothing about the filing. It will pass on a correct filing, on a wrong filing, and on a filing of random numbers. **It can never fail, so it can never be admitted by L4 test 2 — "can a degenerate artifact satisfy it?" Yes. Trivially.**
- **If you round-trip faithfully, at per-transaction rates:** you need `{(amountᵢ, dateᵢ)}` — the transaction ledger. **That is not in the filing, and it is not public.** The MR is undefined on the available data.

There is no middle position. **MR-5 must be deleted, not repaired.**

Two things do survive from the neighbourhood, and both are real:

1. **MR-21 — FX convention consistency across formats.** The FME quarterly uses transaction-date rates (C110). The IBC annual format uses a *different* rule: *"All financial figures in Column C and E in table 1.11 and 1.12 shall be reported in USD after conversion based on the **RBI reference rate as on 31st** [March]"* (**VERIFIED-AT-SOURCE**, `F. Financial Information`!B38). **IFSCA uses two incompatible FX conventions across two of its own prescribed formats.** A checker that assumes one convention is wrong on the other half of the corpus. The checkable relation is: *the FX convention asserted by the checker must match the convention stated in the format it is checking* — a check on **us**, and exactly the kind of self-directed check the coverage claim needs.

2. **MR-22 — declared-unit consistency.** Every monetary column in the FME workbook is headed `USD Million` (31 occurrences). The relation: no cell in a `USD Million` column may carry a magnitude consistent with raw USD. A scheme reporting `50000000` in a USD-Million column has entered raw dollars — a unit error, one of the most common and most consequential real filing defects, detectable with no oracle at all by order-of-magnitude reasoning against the column's own declared unit.

---

## PART 9 — THE MR SET

**25 relations, organised by invariant class.** Each carries: transformation · expected relation · tolerance model · mechanical procedure · failure interpretation · **N** = necessary (violation ⇒ FAIL) or **E** = expected (violation ⇒ ADVISORY) · **GT** = ground truth required.

**Notation.** `T` = the filing under test. `π` = a permutation of scheme slots 1–10. `λ` > 0. `q` = reporting quarter. `round₂` = `Decimal.quantize(0.01, ROUND_HALF_UP)`. `n` = number of summands in the aggregate under test. **The default tolerance for any sum of *n* two-decimal USD-Million cells is `τ(n) = n × 0.005` USD Million**, derived in §8.4(b); a constant epsilon is wrong and is the single most likely source of spurious L6 failures.

### Class A — Permutation

**MR-01 · Scheme permutation, source-consistent** — N — **GT: none**
- **Transformation.** Apply π to Introduction rows 54–63 (Table 1.5) **and** to every downstream per-scheme block in lockstep: Summary 5–14, Portfolio 3–12 / 17–26 / 41–50 / 55–64, Investors 21–30, and the 1.6 block 75–84.
- **Expected.** Every scalar aggregate **invariant**: `Intro D17`, `D18`, `D19`, `D20`. Every per-scheme derived value **equivariant** — it travels with its scheme. Every cross-sheet carry still resolves to the same scheme's data.
- **Tolerance.** Exact for counts. `τ(n)` for money only if the implementation re-rounds; a pure permutation should be bit-identical.
- **Procedure.** Permute; recompute the induced formula graph; assert `multiset(rows_before) == multiset(rows_after)` **and** `scalar_aggregates_before == scalar_aggregates_after` **and** for each scheme *s*, `row(s)_before == row(π(s))_after` cell for cell.
- **Failure.** A scalar aggregate that moves ⇒ an order-dependent aggregation. A row that does not travel intact ⇒ a broken carry binding, i.e. the checker's schema binds by position where it should bind by scheme identity.
- **Note.** This is the repaired form of the brief's MR-1. The repair is *"permute the source, not the view."*

**MR-02 · `AGGREGATE` list re-ordering — multiset, not vector** — N — **GT: none**
- **Transformation.** MR-01's π, observing Table 1.7 (Intro C92:E101).
- **Expected.** `IFERROR(INDEX($C$54:$C$63, AGGREGATE(15,6, (ROW(...)−ROW($C$54)+1)/($N$54:$N$63="yes"), ROWS(...))), "NA")` — `AGGREGATE(15,…)` is `SMALL`, so it returns the *k*-th smallest source row index among schemes flagged third-party-managed. Under π the **set** of listed schemes is invariant; their **order** follows the new source indices. So: **multiset equality, explicitly not vector equality.**
- **Tolerance.** Exact, on the multiset.
- **Procedure.** `assert sorted(list_before) == sorted(list_after)` and `assert list_before != list_after` whenever π moves a flagged scheme (a positive control that the transformation actually did something).
- **Failure.** Multiset changed ⇒ the filter predicate `N54:N63="yes"` is order-sensitive or case-sensitive in a way it should not be. (Note: it *is* case-sensitive to `"yes"` vs the dropdown's `"Yes"` — worth its own predicate at L5.)
- **Why it earns its place.** Stating this as vector equality is the textbook way to manufacture a false alarm, and it is exactly what a naive reading of "reordering must not change anything" produces.

**MR-03 · Investor-category column permutation** — N — **GT: none**
- **Transformation.** Permute the twelve (amount, count) column-pairs of Investors Table 4.1 — (C,D), (E,F), … (Y,Z) — carrying headers with data.
- **Expected.** `AA` (total amount) and `AB` (total count) invariant.
- **Tolerance.** `τ(12)` = 0.06 USD Million on `AA`; exact on `AB`.
- **Procedure.** Permute; recompute; compare `AA`, `AB`.
- **Failure.** Movement ⇒ the checker binds columns by position rather than by header name.
- **Evidence this is a real property of the artifact:** PMS `AB23 = SUM(D23,F23,H23,J23,P23,R23,L23,N23,T23,V23,X23,Z23)` lists the same twelve columns in a **scrambled order** compared to Investors `AB21 = SUM(D21,F21,H21,J21,L21,N21,P21,R21,T21,V21,X21,Z21)`. Same set, different sequence — the drafter is already relying on commutativity. **VERIFIED-AT-SOURCE.**

### Class B — Identity element

**MR-04 · Blank → explicit zero** — N — **GT: none**
- **Transformation.** For each blank cell in a numeric range with a `decimal ≥ 0` validation, write `0.00`.
- **Expected.** Every derived value invariant. Every `UNCHECKED` reason invariant.
- **Tolerance.** Exact.
- **Procedure.** Enumerate blank numeric cells from the L1 schema's validation map; set to zero one at a time and in bulk; recompute; compare full fact set.
- **Failure.** Any movement ⇒ the checker conflates blank with zero, or a `SUM` is treating blank as something other than zero. **Real risk:** Table 3.1 ships pre-filled with literal `0`s while Investors Table 4.2 (rows 42–51) ships genuinely blank. The two are semantically different — *"reported as nil"* vs *"not reported"* — and the difference is exactly what an `UNCHECKED` verdict is for.

**MR-05 · Zero-value scheme in an empty slot — typed partial invariance** — N — **GT: none**
- **Transformation.** Occupy an empty scheme slot with a valid scheme: authorisation number, name, a type drawn from `Dropdown!F3:F11`, authorisation date ≤ period end, all monetary cells `0.00`, all counts `0`.
- **Expected.** Money **invariant**; `Intro D17` **+1**; exactly one of `D18`/`D19`/`D20` **+1** according to the chosen type; `Table 1.6` gains one row; `Table 1.7` gains a row **iff** `N=yes`.
- **Tolerance.** Exact on counts; exact on money (adding zeros).
- **Procedure.** Insert; recompute; assert the money set is unchanged **and** the count deltas match the predicted vector exactly.
- **Failure.** Money moved ⇒ a non-linear aggregation. A count delta ≠ predicted ⇒ the `COUNTIF` pattern (`"*Angel*"`, `"*Venture*"`, `"*Restricted*"`, `"*Retail*"`, `"*Exchange Traded Fund*"`) does not partition the dropdown vocabulary as intended.
- **This is the repaired brief MR-2**, and the repair is the word *typed*.
- **A latent template defect this MR would find:** `D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")`, `D19 = COUNTIF(G54:G63,"*Restricted*")`, `D20 = COUNTIF(G54:G63,"*Retail*") + COUNTIF(G54:G63,"*Exchange Traded Fund*")`. The dropdown offers **eleven** scheme types including `Special Situation Fund` and `Family Investment Fund` — **neither matches any of the three patterns.** An FME with one Special Situation Fund gets `D17 = SUM(D18:D20) = 0` while having one authorised scheme. MR-05 detects this on the first insertion of that type. **VERIFIED-AT-SOURCE** — patterns and vocabulary both read off the file.

**MR-06 · Zero investor category** — N — **GT: none**
- **Transformation.** Set an unused investor-category pair in Table 4.1 to (`0.00`, `0`).
- **Expected.** `AA`, `AB`, and `Summary H` (which carries `'4. Investors'!AB21`) all invariant.
- **Tolerance.** Exact.
- **Failure.** Movement ⇒ blank/zero conflation in the count path.

### Class C — Idempotence

**MR-07 · Scheme split (the fraud-shaped transformation)** — N — **GT: none**
- **Transformation.** Take a scheme with monetary vector **v** occupying one slot; place it across two slots as **a** + **b** = **v**, both carrying the *same* authorisation number and name.
- **Expected.** All money aggregates **invariant**. Scheme count **+1**. Therefore: `Intro D17` now exceeds the number of **distinct** authorisation numbers by exactly 1.
- **Tolerance.** `τ(n)` per aggregate; exact on counts.
- **Procedure.** Split; recompute; assert money invariance; then assert `D17 == |distinct(C54:C63) \ {"NA"}|` and observe it **fail**.
- **Failure interpretation — and this is the point.** The MR is designed so that a *correct* filing satisfies both the money relation and the count relation, and the split satisfies only the money relation. **The disagreement between two relations that should agree is the detector.** Splitting or duplicating a scheme to move money between reporting buckets — a plausible way to keep a scheme under a threshold — is caught without an oracle, without the register, and without knowing what the right numbers were.
- **This replaces the brief's MR-3**, which is inexpressible.

**MR-08 · Re-run determinism** — N — **GT: none**
- **Transformation.** None. Run the entire pipeline twice on identical bytes, in separate processes, with `PYTHONHASHSEED` varied.
- **Expected.** Byte-identical verdict, identical coverage fraction, identical multiset of `UNCHECKED(reason)`.
- **Tolerance.** Exact — this is the one MR with zero tolerance.
- **Procedure.** Hash the serialised verdict; compare.
- **Failure.** Nondeterminism in L2's model call, in dict/set iteration order, or in floating-point accumulation order.
- **Why it is in the set.** This is the MR that catches *our own* silent failures — the §4.4 class, and the class I hit twice today. A verdict that is not reproducible is not a verdict. It costs one line and it is the cheapest honest thing in the design.

### Class D — Scaling / homogeneity

**MR-09 · Typed λ-scaling** — N — **GT: none**
- **Transformation.** Multiply every **degree-1** cell by λ (test λ ∈ {2, 10, 0.5, 1.0001}), re-rounding to two decimals. Leave degree-0 fields untouched.
- **Expected.** Every degree-1 derived total scales by λ. Every degree-0 field invariant.
- **Tolerance.** `|derived_after − λ·derived_before| ≤ n × 0.005 × max(1, λ)`, with `n` the summand count of that specific aggregate. **Never a constant.**
- **Procedure.** Requires a **degree map** over every field, produced once at L1 from column headers and validation types: `USD Million` in the header ⇒ degree 1; `whole` validation or `No. of` / `Number of` in the header ⇒ degree 0; `date` validation ⇒ degree 0; list validation ⇒ degree 0; `%` in header ⇒ degree 0.
- **Failure.** A degree-1 total that does not scale ⇒ a hard-coded constant or a non-linear step (a fee band, a cap). A degree-0 field that moves ⇒ the degree map is wrong, or a count is being computed from an amount.
- **This is the repaired brief MR-4.** The repairs are: the degree map, and `τ(n)`.

**MR-10 · Zero-scaling (λ = 0)** — N — **GT: none**
- **Transformation.** All degree-1 cells → `0.00`.
- **Expected.** All monetary aggregates `0.00`. All counts unchanged. **Every ratio becomes `UNCHECKED(undefined)` — not `0%`, and not a FAIL.**
- **Tolerance.** Exact.
- **Failure.** A division that returns `0` or raises instead of abstaining ⇒ an unguarded denominator. AML-CFT 1f (*"Percentage of total customer/client classified as High risk"*) is the live instance: with zero clients the percentage is undefined, and a checker that reports `0%` has asserted something it does not know.
- **Direct tie to the architecture:** this MR mechanically finds the places where the system would otherwise emit a confident value in place of an abstention. It is the coverage-honesty check, expressed as a metamorphic relation.

**MR-11 · Sign flip on signed fields** — N — **GT: none**
- **Transformation.** Negate the fields the artifact declares signed: Portfolio 3.2 M, N (*"In calculating 'Net Gains / Losses', if there is a net loss, the same may be indicated as a negative figure"* — note 6) and PMS 5.2 E, F.
- **Expected.** Sign propagates into any aggregate containing them; no aggregate takes an absolute value; validation floors respected (measured: `decimal ≥ −5,000,000` on Portfolio E27:F27; `decimal ≥ −9,999,999,999` on PMS C10:C11).
- **Tolerance.** Exact.
- **Failure.** An aggregate that does not move ⇒ an `ABS()` or a `MAX(0, ·)` somewhere it should not be — a classic way to make a loss disappear.

### Class E — Additivity / partition — **the highest-value class**

**MR-12 · Four-way partition of funds raised — the flagship** — N — **GT: none**
- **Transformation.** None on the artifact. Compute the same quantity by four independent routes and compare. *(Recompute after MR-01/05/07/09 as well: the agreement must survive every other transformation.)*
- **Expected.** For each scheme *s*, and for the FME total:
  ```
  P₁ = Σ over investor categories        →  '4. Investors'!AA(s)          [12 summands]
  P₂ = Σ over countries                  →  '4. Investors'!C60:C69 …      [no total exists]
  P₃ = Σ over accreditation status       →  '4. Investors'!G(s)  (4.2)    [no formula exists]
  P₄ = the Summary carry                 →  '2. Summary'!K(s) non-retail / Q(s) retail
  assert  P₁ ≈ P₂ ≈ P₃ ≈ P₄
  ```
  And the count duals: `AB(s)` ≈ Σ country counts ≈ Σ accreditation counts ≈ `Summary H(s)` (which is `='4. Investors'!AB21`).
- **Tolerance.** `τ(12) = 0.06` USD Million pairwise on amounts; **exact** on counts. Counts must be exact — a person is not a rounded quantity, and permitting slack there is how a missing investor hides.
- **Procedure.** Extract all four; compare pairwise; report which *pair* disagrees, not just that a disagreement exists. With 4 routes there are 6 pairs, and the pattern of disagreement localises the fault: if P₁ = P₄ but P₂ = P₃ ≠ P₁, the country and accreditation tables were built from a different extract than the category table.
- **Failure.** Any disagreement is a defect. There is no lawful reading under which the same population's funds raised differs by how you partition it.
- **Status in the artifact: the workbook enforces NONE of this.** Table 4.2 has **zero formulas** (its `G`/`H` total columns are empty). Table 4.3 has **zero formulas**. Only `AA`/`AB` and the `Summary H` carry exist. **This is the NASA Data Access Toolkit pattern** (§4.1) — *"formulating the same query in different equivalent ways, and asserting that the resulting datasets are the same"* — and it is the single strongest argument that L6 grows coverage: four partitions, six pairwise checks, all from data already in the filing, none requiring an oracle.
- **Guard against the ValScope failure (§4.1):** assert value equality, not just that the same schemes appear. Set-level agreement with corrupted values is precisely the bug class MT is known to miss.

**MR-13 · PMS three-way partition** — N — **GT: none**
- **Expected.** `'5. PMS'!AA26` (total across Discretionary + Non-Discretionary + Advisory, itself `SUM(C26,E26,…)` over `C26 = SUM(C23:C25)`) ≈ Table 5.4 `G40` (accredited + non-accredited) ≈ Σ Table 5.5 country amounts. Count duals likewise via `AB26`.
- **Tolerance.** `τ(12)` on amounts; exact on counts.
- **Status.** Tables **5.4 and 5.5 have zero formulas.** Only the 5.3 block is wired.
- **Do NOT extend this to 5.6.** Table 5.6 is **look-through** by its own note; 5.1/5.3 are not. Adding them is invalid by the artifact's own rules.

**MR-14 · Complaint and appeal flow identities** — N — **GT: none**
- **Expected.** On sheet `6. Complaints`, three independent identities over Table 6.2:
  ```
  (i)   r17 + r18 − r19 − r22 = r23      opening + received − disposed − withdrawn = pending
  (ii)  r19 = r20 + r21                  disposed = resolved + rejected
  (iii) r19 = r24 + r25                  disposed = within-30-days + after-30-days
  ```
  and the same three over Table 6.3 for appeals: `r31 + r32 − r33 − r36 = r37`; `r33 = r34 + r35`; `r33 = r38 + r39`.
- **Tolerance.** **Exact.** These are integer counts.
- **Status.** Sheet 6 contains **exactly one formula** — `C5 = '1. Introduction'!D8`, a registration-number carry. **Six checkable integer identities, zero enforced.**
- **Failure.** (i) fails ⇒ complaints appeared or vanished. (ii) or (iii) fails ⇒ the disposal breakdown is inconsistent with the disposal count. (ii) and (iii) are two *different* partitions of the same disposals, so they also cross-check each other — the same four-way-partition logic at small scale.

**MR-15 · Debt-grade cross-table identity** — N — **GT: none**
- **Expected.** Per scheme: `'3. Portfolio'!G(3.3) = SUM(C:F)` (grade breakdown of listed debt) must equal `'3. Portfolio'!E(3.1)` (listed debt securities). Likewise `L(3.3) = SUM(H:K)` must equal `F(3.1)` (unlisted debt).
- **Tolerance.** `τ(4) = 0.02` USD Million each.
- **Status.** `G` and `L` **are** formulas (`SUM(C41:F41)`, `SUM(H41:K41)`); their equality with 3.1 `E` and `F` is **not** enforced.
- **Failure.** Disagreement ⇒ the grade breakdown and the asset-class breakdown were prepared from different extracts, or a security was classified listed in one table and unlisted in the other.

**MR-16 · Cash-equivalents branch coherence** — N — **GT: none**
- **Transformation.** Toggle `'2. Summary'!D(s)` between `"Retail Scheme"` and any other type.
- **Expected.** `'3. Portfolio'!L(s) = IF(Summary D(s)="Retail Scheme", Summary W(s), Summary N(s))` must switch source. If the filer has populated **both** `N(s)` and `W(s)` with non-zero values for the same scheme, the toggle changes `L(s)` — and that is a defect, because a scheme is retail or it is not, and only one of the two columns is applicable to it.
- **Tolerance.** Exact.
- **Procedure.** For each scheme, assert `not (N(s) ≠ 0 and W(s) ≠ 0)`; then toggle and confirm `L(s)` changes iff exactly one is populated.
- **Failure.** Both branches populated ⇒ a filer filled the retail and non-retail column blocks for one scheme. **The `IF` silently hides this — it reads one branch and never looks at the other.** This is a defect the workbook's own formula is structurally incapable of surfacing, which makes it a clean demonstration of what relation-checking adds over formula-checking.

### Class F — Round-trip

**MR-17 · Parse round-trip** — N — **GT: none**
- **Transformation.** `xlsx → L1 induced schema + fact set → regenerated xlsx → re-induced fact set`.
- **Expected.** Fact sets identical, including: all 505 formula-evaluating cells, all 35 data validations with bounds, all merged ranges (13 on Summary alone), all hidden-row flags, all protection flags, the hidden `Dropdown` sheet and its 15 vocabularies.
- **Tolerance.** Exact.
- **Failure.** Any loss ⇒ L0/L1 parser gap. **Known live trap, hit today:** 211 of 505 formula cells are empty shared-formula followers. A parser that reads only `<f>` elements with text loses **41.8%** of the formula cells, and loses them *silently* — the workbook still parses, still validates, still produces a confident answer. This MR is the regression test for the exact bug class the brief documents in §4.4 and that I reproduced in §7.4.

**MR-18 · Scale round-trip (checker self-test)** — N — **GT: none**
- **Transformation.** `x → λx → x/λ`.
- **Expected.** Recovery within `2 × τ(n)` (two rounding operations).
- **Failure.** Loss beyond tolerance ⇒ the arithmetic uses binary floats where it should use `Decimal`, or the rounding mode is half-even where the artifact implies half-up.
- **Scope note.** This tests **us**, not the filing. It belongs in L4's qualification harness, not in the filing report.

### Class G — Monotonicity

**MR-19 · Formula-cell differential (back-to-back)** — N — **GT: none**
- **Transformation.** None. For every cell the *blank template* declares to be a formula, compare (a) the value in the filed workbook against (b) the value obtained by evaluating the template's formula over the filed inputs.
- **Expected.** Equal for all 505 formula-evaluating cells.
- **Tolerance.** `τ(n)` for `SUM` cells; exact for carries and `COUNTIF`.
- **Procedure.** Two independent implementations, both already available: IFSCA's formula (from the versioned blank template) and our own evaluator over the L1 schema. Compare.
- **Failure — and this is the highest-probability real defect in the corpus.** Nine of ten sheets are protected, but OOXML sheet protection is advisory and trivially removed. If a filer unprotects a sheet and types a literal over `O3 = SUM(C3:N3)`, the filed workbook is *internally consistent* — the inconsistency was deleted along with the formula — and **nothing else in the entire L0–L7 design detects it.** Only a differential against the blank template sees it. Requires no oracle and no second filing; requires only that we content-address the blank template, which L0 already does.

**MR-20 · Cumulative monotonicity across quarters — with its lawful exception** — **E for column J, N for the rest** — **GT: none; needs the prior filing**
- **Transformation.** None. Compare `T(q)` with `T(q−1)`.
- **Expected.** Non-decreasing, per scheme: `K` (cumulative funds raised, non-retail), `M` (cumulative investments), `O` (cumulative fees and expenses), `P` (cumulative distributions), `Q` (cumulative funds raised, retail), `S` (cumulative redemptions).
- **THE EXCEPTION, and it is exactly the kind this lane was asked to find.** Column `J` (*Cumulative commitments raised*) is **NOT** monotone. Summary note 4, verbatim: *"'Cumulative Commitments raised' includes gross commitment raised since inception **deducting such commitments which have been exited due to forefeiture / exit / reduction in commitment**."* Commitments can lawfully be deducted, so `J` can lawfully fall. **A relation asserting "all cumulative columns are non-decreasing" false-alarms on column J on a correct filing.** `J` must be **E** (advisory, with the note quoted in the report) while `K`, `M`, `O`, `P`, `Q`, `S` are **N**.
- **A second exception, on `O`.** Cumulative fees include performance fees, which **crystallise** as discrete events. `O` stays monotone (fees only accumulate), so the monotonicity check is safe — but any *smoothness* or *rate-of-change* check on `O` would false-alarm at crystallisation, and simultaneously `V` (NAUM) drops while `O` jumps. **Do not write a relation coupling `V` to `K − P`.**
- **Tolerance.** `≥ −τ(1) = −0.005` USD Million, to absorb a re-rounding of the prior figure.
- **Failure.** A genuine decrease in `K`, `M`, `O`, `P`, `Q` or `S` ⇒ a restatement, a period-vs-cumulative confusion, or a sign error. All three are real and all three are invisible to any single-filing check.

**MR-21 · Definitional bounds** — **N** — **GT: none**
- **Expected**, all within one filing, all entailed by the columns' own definitions:
  ```
  '3. Portfolio'!G(3.2) ≥ F(3.2)   highest borrowing in quarter ≥ borrowing at end
  '3. Portfolio'!G(3.2) ≥ C(3.2)   highest borrowing in quarter ≥ borrowing at start
  '3. Portfolio'!K(3.2) ≥ J(3.2)   highest notional in quarter ≥ gross notional at end
  '3. Portfolio'!J(3.2) ≥ L(3.2)   gross notional ≥ net unhedged notional
  '5. PMS'!C(5.2)       ≥ D(5.2)   same, for PMS
  ```
- **Warrant for the last two:** Portfolio note 5 — *"'Net Unhedged Notional Exposure through Derivatives' include only such derivative positions which remain after offsetting those derivative positions that are in nature of hedging"* — so net-unhedged is a subset of gross by construction. Note 4 confirms gross is un-netted: *"the gross exposure across all contracts may be aggregated. Exposure across multiple derivative contracts (such as Long and Short positions) shall not be netted out."*
- **Tolerance.** `≥ −0.005` USD Million.
- **Failure.** Violation ⇒ netting applied where the note forbids it, or a period-end figure entered in a during-period column.
- **One relation to mark E, not N:** `Summary I ≥ Summary H` (investors who *committed* ≥ investors who *contributed*). Intuitive, but an investor can contribute without a recorded prior commitment in some structures. **ADVISORY only.**

### Class H — Temporal consistency across filing periods

**MR-22 · Opening balance = prior closing balance** — N — **GT: none; needs the prior filing**
- **Expected.**
  ```
  '6. Complaints'!r17(q) = '6. Complaints'!r23(q−1)     complaints outstanding
  '6. Complaints'!r31(q) = '6. Complaints'!r37(q−1)     appeals outstanding
  '3. Portfolio'!C(3.2)(q, s) = '3. Portfolio'!F(3.2)(q−1, s)   borrowing, per scheme
  ```
- **Tolerance.** Exact for the two integer counts; `τ(1)` for borrowing.
- **Failure.** A discontinuity across the quarter boundary ⇒ items appeared or vanished between filings. **Detectable with two filings and no ground truth whatsoever** — this is metamorphic testing in its purest form, and it is the relation a supervisor triaging 868 filings a year would most want.
- **Note.** The prior filing is not public. In the entity-facing product the filer has it. In the supervisor-facing product IFSCA has it. Neither needs an oracle.

**MR-23 · Static-field stability** — **N with a declared exception list** — **GT: none; needs the prior filing**
- **Expected.** Identical across consecutive filings: `Intro D8` (FME registration number), `D9` (name), `D11` (date of registration), `D13` (PAN), `D14` (GSTIN), `D12` (legal structure); and per scheme, `C54:C63` (authorisation numbers), `E54:E63` (authorisation dates), `F54:F63` (legal structure).
- **Tolerance.** Exact string / exact date.
- **Exceptions that are lawful and must be declared, not flagged:** a genuine name change, a GSTIN re-issue, a legal-structure conversion. Each is a real corporate event — so the verdict is **FAIL with a named remedy** (*"a change here requires an accompanying explanation"*), never a silent pass and never an unexplained flag.
- **Failure.** A *date of registration* that moves is never lawful — the past does not change. This is the sharpest single instance: **a mutable immutable.**

**MR-24 · Half-yearly gating of the AML-CFT sheet** — N — **GT: none**
- **Transformation.** Vary `Intro` Table 1.1 *Quarter* across the four dropdown values (`April - June`, `July - September`, `October - December`, `January - March`).
- **Expected.** Sheet `7. AML-CFT` states, at A2: *"To be reported half-yearly, i.e., for the periods ending on **September 30 and March 31** of every year."* So the sheet is **required** for the Jul–Sep and Jan–Mar filings and **not applicable** for Apr–Jun and Oct–Dec.
- **Tolerance.** n/a — presence/absence.
- **Failure.** A checker that demands sheet 7 in every quarter is wrong on **exactly half** the filings — a **50% false-positive rate by construction**, on a population of ~868 filings a year. That is the single largest avoidable FPR in the design, it is written on the face of the sheet, and no formula in the workbook encodes it (sheet 7 has **zero** formulas).
- **Why it is an MR and not a rule.** Stated as a rule it is a special case someone must remember. Stated as a relation — *"varying the quarter must toggle sheet 7's applicability, and must change nothing else"* — it is mechanically testable and it also catches the converse error of a checker that *never* demands sheet 7.

### Class I — Cross-report consistency

**MR-25 · Multi-instance coherence for FMEs with more than ten schemes** — N — **GT: none**
- **Transformation.** None. Relate the multiple workbook instances one FME submits for one quarter.
- **Warrant.** Guidance C113: *"if a FME has obtained authorisation for more than 10 (ten) schemes, it shall submit its quarterly filing by using more than 1 instances of such excel sheet. Each such additional instance shall be renamed as `<full name of the FME>_Additional Instance <x>`."*
- **Expected.** Across all instances of one FME for one quarter:
  ```
  identical:   D8 (reg no.), D9 (name), D11 (date of reg), D13 (PAN), D14 (GSTIN),
               and every field in Tables 1.3 and 1.4
  disjoint:    the sets of scheme authorisation numbers   (no scheme reported twice)
  additive:    Σ over instances of D17 = the FME's true authorised scheme count
  once only:   the recurring-fee block (Table 1.4) must appear in exactly one instance,
               or the FME's fee payment is double-counted
  ```
- **Tolerance.** Exact.
- **Failure.** A scheme appearing in two instances is double-counted in every aggregate. A fee block repeated across instances double-counts the fee. **Nothing in the workbook, and nothing in the brief's design, looks across instances at all** — the design assumes one file per filing. C113 says otherwise.
- **Population note.** 217 FMEs, 360 schemes (brief §4.3) ⇒ mean 1.66 schemes per FME, so multi-instance filers are a small minority — but they are by construction the **largest** FMEs, i.e. the ones whose filings matter most.

### Not adopted, and why — recorded so nobody re-explores it

| Candidate | Why not |
|---|---|
| **Currency round-trip** (brief MR-5) | Vacuous under a single rate; underdetermined under C110's per-transaction rate; requires a ledger not in the filing. **Deleted, §8.5.** |
| **Country-row permutation** (4.3 / 5.5 / 5.6) | Sound in principle, but those tables have **no total row and no formulas** — there is no observable to compare. Becomes viable only once L6 manufactures the totals, at which point it is subsumed by MR-12. |
| **Position consolidation** (brief MR-3) | No position-level rows exist. Expressible on the FME's source ledger, not on the filing. |
| **Unit re-denomination** USD Million → USD Thousand | Prohibited by guidance C109 (headings shall not be modified). |
| **Cross-report FME-quarterly ↔ "annual format"** | **The annual workbook is not an FME return.** See §11. |

### Ground-truth summary

**All 25 relations require no ground truth.** None needs a known-correct filing, a labelled corpus, or a human judgement about whether a value is *right*.

They split by what they *do* need:

| Needs | MRs | Count |
|---|---|---|
| **The filing alone** | 03, 04, 05, 06, 07, 09, 10, 11, 12, 13, 14, 15, 16, 21, 24 | **15** |
| **The filing + the versioned blank template** (already content-addressed by L0) | 01, 02, 17, 19 | **4** |
| **Two consecutive filings** — another *run*, not an oracle | 20, 22, 23 | **3** |
| **Multiple instances of one filing** | 25 | **1** |
| **Checker self-tests** (L4, not reported to the filer) | 08, 18 | **2** |

**This is the number that moves the 17/24 boundary.** The brief's oracle check found 17 of 24 predicates script-settleable, with the settleable and the valuable sets nearly disjoint. These 25 relations are all settleable, none requires an oracle, and several — MR-07 (scheme splitting), MR-16 (both branches populated), MR-19 (overwritten formula), MR-12 (partition disagreement) — bear directly on questions from the *undecidable* seven, because a filing whose partitions disagree is one whose *"disclosed portfolio composition"* cannot be accurate, whatever the true composition is.

**The honest limit, stated plainly.** L6 does not decide whether the disclosed composition is *accurate*. It decides whether the filing is *internally coherent under transformations that must preserve its meaning*. Those are different predicates. A filing can be perfectly coherent and completely false — an FME that fabricates a consistent set of numbers passes all 25. **What L6 buys is that incoherence can no longer hide, and that the boundary between the two can be stated.** That is a smaller claim than "we verified the filing," and it is the only one the evidence supports.

---

## PART 10 — MECHANICAL DESIGN

### 10.1 The formula evaluator is unavoidable

`openpyxl` with `data_only=True` returns only the values **Excel cached at last save**. Transform the inputs and the cached outputs do not move. So L6 cannot observe any consequence of any transformation without an independent evaluator over the induced formula graph.

That evaluator is small, because the graph is small. From §7.4, the entire function vocabulary of the FME workbook is: `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)` (i.e. `SMALL` ignoring errors), and direct cell references. **Eight functions.** A topological sort over 505 cells plus eight function implementations, in `Decimal`.

**And building it is itself the differential arm of MR-19** — the second independent implementation whose disagreement with IFSCA's own formulas is the detector.

### 10.2 Sketch

```python
from decimal import Decimal, ROUND_HALF_UP
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, initialize, Bundle

Q2 = Decimal("0.01")
def r2(x: Decimal) -> Decimal:            # Excel semantics, NOT Python's round()
    return Decimal(x).quantize(Q2, rounding=ROUND_HALF_UP)

def tau(n: int, lam: Decimal = Decimal(1)) -> Decimal:
    """Accumulated 2-dp rounding slack for a sum of n cells. NEVER a constant."""
    return Decimal("0.005") * n * max(Decimal(1), abs(lam))

class FilingMachine(RuleBasedStateMachine):
    slots = Bundle("free_scheme_slots")

    @initialize(target=slots)
    def load(self):
        self.template = induce_schema(BLANK_TEMPLATE_SHA256)   # L1
        self.wb       = load_filing(FILING_UNDER_TEST)          # L0
        self.baseline = evaluate(self.template, self.wb)        # our evaluator
        return free_slots(self.wb)

    # ---- transformations (each is one MR's follow-up input) ----

    @rule(perm=st.permutations(range(10)))
    def permute_schemes(self, perm):                            # MR-01, MR-02
        self.wb = permute_source_and_carries(self.wb, perm)
        self.perm = perm

    @rule(slot=slots, kind=st.sampled_from(SCHEME_TYPES))       # MR-05
    def insert_zero_scheme(self, slot, kind):
        self.expected_count_delta[kind] += 1
        self.wb = insert_scheme(self.wb, slot, kind, amounts=Decimal("0.00"))

    @rule(lam=st.sampled_from([Decimal("2"), Decimal("10"),
                               Decimal("0.5"), Decimal("0")]))  # MR-09, MR-10
    def scale_degree_one(self, lam):
        self.wb  = scale(self.wb, lam, degree_map=self.template.degrees)
        self.lam = lam

    # ---- necessary MRs: must hold after EVERY step, in every state ----

    @invariant()
    def funds_raised_partitions_agree(self):                    # MR-12  (flagship)
        v = evaluate(self.template, self.wb)
        for s in v.schemes:
            routes = {
                "by_category":     v.investors_AA(s),
                "by_country":      sum(v.country_amounts(s)),
                "by_accreditation":sum(v.accreditation_amounts(s)),
                "summary_carry":   v.summary_funds_raised(s),
            }
            for (na, a), (nb, b) in pairs(routes.items()):
                assert abs(a - b) <= tau(12, self.lam), \
                    f"{s}: {na}={a} vs {nb}={b}  (delta {a-b})"
            # counts are people: EXACT, no slack
            assert len(set(count_routes(v, s))) == 1

    @invariant()
    def complaint_flow_closes(self):                            # MR-14
        c = evaluate(self.template, self.wb).complaints
        assert c.open + c.received - c.disposed - c.withdrawn == c.pending
        assert c.disposed == c.resolved + c.rejected
        assert c.disposed == c.within30  + c.after30

    @invariant()
    def scheme_count_matches_distinct_authorisations(self):     # MR-07
        v = evaluate(self.template, self.wb)
        assert v.cell("1. Introduction", "D17") == \
               len({a for a in v.authorisation_numbers() if a != "NA"})

    @invariant()
    def template_formulas_still_hold(self):                     # MR-19 (differential)
        for addr, f in self.template.formulas.items():          # 505 cells
            ours   = self.evaluator.eval(f, self.wb)
            filed  = self.wb.cached(addr)
            assert abs(ours - filed) <= tau(f.n_summands, self.lam), \
                f"{addr}: template says {ours}, filing carries {filed}"
```

`@invariant` for necessary relations, assertions inside `@rule` for expected ones — the FAIL/ADVISORY split of §2.4, implemented by the library rather than by us.

### 10.3 Budget

Ravi & Coblenz: **55%** of mutations found at n=1, **76%** within the first 20 inputs (VERIFIED-AT-SOURCE, §5.1). The artifact's input space is small and fixed. **Set `max_examples` at 50, not Hypothesis's default 100 or a fuzzer's millions**, and pin every real defect as an `@example`. L6 should cost seconds per filing.

### 10.4 The three qualification tests, applied to L6

L4's gate applies to metamorphic relations exactly as to predicates:

1. **Can it fire?** Seed the transformation *without* the compensating change and confirm the MR fails. An MR that has never failed on a deliberately broken artifact is not admitted. This is also the guard against MR-5-shaped null tests — a relation that cannot fail scores zero and is rejected automatically, so the qualification gate would have caught the currency round-trip on its own.
2. **Can a degenerate artifact satisfy it?** An all-zero filing satisfies MR-12, MR-14, MR-15 trivially. **Every partition MR needs a non-degeneracy precondition**: at least two routes non-zero, or the verdict is `UNCHECKED(no data)`, not PASS. Without this, an empty filing scores 100% coverage — the exact degenerate operating point the brief's §5.2 L4 test 2 exists to catch, arriving through the L6 door.
3. **Does it discriminate?** Measure the false-failure rate of each MR on the clean corpus. **Carry the brief's own caveat (§9.2): a synthetic clean corpus is not a measurement of real filings, and every FFR quoted from it must say so.**

---

## PART 11 — CORRECTIONS TO THE BRIEF AND ARCHITECTURE

| Claim | Status | Evidence |
|---|---|---|
| Barr et al., *IEEE TSE* 41(5):507–525, 2015 | **CONFIRMED** | Read verbatim in the reference list of the opened IRI 2023 PDF; corroborated by KAIST/UCL records |
| §4.3: 294 formulas / 181 cross-sheet / 35 SUM / 3 COUNTIF / 50 IFERROR / 14 IF / 11 other; **38 of 294 = 13%** checkable | **CONFIRMED, class by class** | My own OOXML tokenizer, after fixing my own bug. §7.4 |
| "181 (62%) copy a value" | **CONFIRMED at its denominator; QUALIFIED as a description** | 181/294 = 61.6% of authored formulas. But 505 cells evaluate a formula (211 shared-formula followers), so 181/505 = 35.8% of evaluated cells. Both true; state which |
| L6: "reordering portfolio rows must not change NAV" | **REFUTED** | No NAV field (0 hits across 9 workbooks, all XML); rows are schemes not holdings; rows are formula-bound to Introduction, so the transformation is invalid → false alarm. §7.1, §8.1 |
| L6: "adding a zero-value holding must not change NAV" | **QUALIFIED** | Money invariant, counts equivariant (+1 on D17/D18/D19/D20). Asserted as full invariance it false-alarms. §8.2 |
| L6: "consolidating two identical positions must not change NAV" | **REFUTED as stated** | No position-level rows. The *inverse* (splitting a scheme) is a strong MR — MR-07. §8.3 |
| L6: "scaling the reporting unit must scale every derived total proportionally" | **QUALIFIED** | Degree-1 only; needs `τ(n) = n × 0.005` not a constant; needs `ROUND_HALF_UP` not banker's rounding; and C109 forbids modifying the unit heading. §8.4 |
| L6: "currency round-trip within tolerance" | **REFUTED** | C110 mandates per-transaction historical rates. Single-rate round-trip is vacuous; faithful round-trip needs a ledger not in the filing. **Delete.** §8.5 |
| L6 "moves the 17/24 boundary" | **CONFIRMED and strengthened** | 25 relations, all oracle-free; 15 need only the filing. §9 |
| Cross-report consistency "between the FME quarterly and the annual format" *(lane brief)* | **REFUTED** | `IFSCA_Annual_Reporting_Format_30April_2026_Approved…xlsx` Summary Sheet A1 reads *"Annual Reporting Format for **International Branch Campuses** in GIFT IFSC"* — universities. Its sheets are Degree Programmes, Faculty, Student Grievances, Campus Infrastructure. **There is no FME annual workbook among the nine.** The real cross-report axes are multi-instance (MR-25) and quarter-over-quarter (MR-20/22/23) |
| §6.2: "Hypothesis / QuickCheck — relations must be authored" | **CONFIRMED** | Hypothesis generates inputs, never properties. §5.2 |
| Only 3 of 35 data validations are list-type with a named vocabulary | **CONFIRMED** | `Intro N54:N63` (Choicelist) + `Compliance Status C10`, `C11` (both `IF(C5="No",Choicelist,YesNolist)`). The hidden `Dropdown` sheet holds **15** vocabularies; **12 are unwired** |
| 9 of 10 sheets protected | **CONFIRMED** | Only `Dropdown` is unprotected — and it is also `sheet_state="hidden"` |

**New findings not in the brief:**

1. **The blank template ships a hidden orphan table block** — Investors rows 2–17, formula-live, duplicating table numbers 4.1 and 4.2. §7.3.
2. **The `COUNTIF` scheme-type tallies do not partition the dropdown vocabulary.** `Special Situation Fund` and `Family Investment Fund` match none of the five patterns, so `D17 = SUM(D18:D20)` undercounts for any FME holding one. §9/MR-05.
3. **211 of 505 formula cells are shared-formula followers carrying no text** — the trap that would silently lose 41.8% of the formula graph to a text-only parser. §7.4.
4. **IFSCA uses two incompatible FX conventions across its own formats** — transaction-date (FME quarterly, C110) vs RBI reference rate at 31 March (IBC annual). §8.5.
5. **One workbook mixes look-through and non-look-through bases** — Portfolio note 7 vs PMS Table 5.6 note. Any MR spanning them is invalid. §7.2.
6. **Sheet 7 is half-yearly**, so a checker demanding it every quarter has a 50% FPR by construction. §9/MR-24.

---

## What this changes about the design

**1. L6 stops being a footnote and becomes the largest source of oracle-free coverage in the system.** The brief allocates five relations to L6 and schedules it fourth in residency. The measured position is: four of those five false-alarm, the fifth is vacuous, and the replacement set is 25 relations of which 15 need nothing but the filing itself. L6 should move ahead of L2 in the build order — it is deterministic, it needs no labelled corpus, and it is the only component with a defensible novelty claim (§4.3).

**2. The generation strategy for L6 must be the opposite of L3's.** L3 mines statute with a model. **L6 must not use a model at all.** The measured signature of LLM-generated MRs is high correctness and *markedly low novelty* — a model returns the textbook classes, which is exactly how the brief arrived at its five. Every relation worth having here was read off the artifact: a note about forfeiture (MR-20's exception), a note about look-through (a killed relation), a sentence about half-yearly reporting (MR-24), a `COUNTIF` pattern that misses two dropdown values, an `IF` that hides a double-populated branch. No model produces these, and the literature says so.

**3. Every metamorphic relation must be typed by degree and by necessity, or it is a false-alarm generator.** Two annotations do all the work: a **degree map** over every field (money=1, counts/dates/ratios/categoricals=0), and a **necessary/expected flag**. Every false alarm in §8 traces to a missing one of these. Both are cheap, both belong in the L1 induced schema, and both must be produced before the first relation is written.

**4. The tolerance model is `τ(n) = n × 0.005` USD Million, and the rounding mode is `ROUND_HALF_UP`.** Not a constant epsilon, and not Python's default `round`. Guidance C111 fixes two decimals on USD Million, so a sum of *n* cells carries up to *n* × USD 5,000 of lawful slack, while Excel and Python disagree at every exact half. Counts get **zero** tolerance — a person is not a rounded quantity. Getting this wrong produces an irreproducible trickle of false alarms that would be blamed on the model.

**5. Add a back-to-back differential arm against the blank template (MR-19).** It is the only thing in the whole L0–L7 design that detects a filer overwriting a formula cell with a literal — the most likely real defect in a protected workbook, and one that leaves the filing perfectly self-consistent because the inconsistency was deleted along with the formula. It costs one comparison over 505 cells and requires no oracle.

**6. The report needs a fourth verdict.** `PASS / FAIL / UNCHECKED(reason)` cannot express what MR-20 does with column J: a relation that holds for six columns and lawfully fails for a seventh. Add **`ADVISORY(relation, lawful_exception)`**, carrying the quoted note that makes the exception lawful. Without it, the design's own commitment — no green tick, always a coverage fraction — collapses the moment a correct filing produces a red one.

**7. Two structural assumptions need revising.** The design assumes one file per filing; guidance C113 says FMEs with more than ten schemes submit several, and nothing looks across them (MR-25). And there is **no FME annual workbook** — the "annual format" on disk is for university branch campuses, so the cross-report axis is quarter-over-quarter and instance-to-instance, not quarterly-to-annual.

**8. The strongest pitch material in this lane is a defect I found in IFSCA's own blank template, and a bug I made while looking for it.** The template ships a hidden, formula-live, superseded table block with duplicate table numbers. I found it in one pass with `openpyxl`. And while measuring the formula graph I wrote a regex that silently mis-parsed 53 elements and produced a confident, well-formed correction to the brief that was wrong — the third instance of the exact failure class the brief documents in §4.4, and the second one produced by a *deterministic program*. That pair is the argument: **the artifact is not clean, the instrument is not clean, and neither announces it.** It is the same demonstration the brief already uses, now with a fresh instance from today, and it is worth more on a slide than any benchmark number.

---

## Open questions

1. **What is the false-failure rate of each of the 25 relations on real filings?** Unmeasurable today — filed FME returns are not public (brief §9.2). Everything here is derived from the blank template plus the regulation. **Any FFR quoted from a synthetic corpus must say so.**
2. **Does an FME with a `Special Situation Fund` or `Family Investment Fund` actually file `D17 = 0`?** The `COUNTIF` patterns say it must. One real filing would settle it. Until then it is a predicted defect, not an observed one.
3. **What does "Can LLMs Discover Metamorphic Relations?" (SANER 2025, DOI 10.1109/SANER64311.2025.00011) actually measure?** IEEE returned 403. Its headline number is **NOT-FOUND** and the §3.4 conclusion rests on arXiv:2503.22141 alone.
4. **METRIC's exact citation.** *JSS* 116:177–190 (2016) came from a search summary, not the page. **UNVERIFIED.**
5. **Is Chen, Cheung & Yiu's report number really HKUST-CS98-01?** Widely repeated; the two primary sources I opened cite the report *without* a number. Do not print it unverified.
6. **Do the 211 shared-formula followers survive an Excel round-trip by a filer?** If Excel rewrites them as text-bearing formulas on save, the filed workbook and the blank template differ structurally in a way MR-17 would flag as a parser bug when it is actually normal. **This must be tested on a filing that has been through Excel before MR-17 is admitted.**
7. **Does IFSCA already run any of these checks on receipt?** Brief §9.6's unrun email. If MR-12 and MR-14 are already run at the regulator, the entity-facing product is a convenience, not a gap — and that changes the pitch, not the engineering.
8. **Which of the 25 survive L4's mutation gate?** No relation in this document has been through the qualification gate. Until it has, this is a designed set, not a measured one, and it should be described that way.
