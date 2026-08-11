# L03 — ASSERTION / ORACLE SYNTHESIS
### Can a machine WRITE a correct executable check? The measured literature, and what to pre-register for experiment 9.1.

**Lane:** L3 predicate synthesis (model writes executable predicates from statutory text) + L4 qualification gate.
**Compiled:** 10 August 2026. **Operator:** research agent, this session.
**Warrant key:** **V** = VERIFIED-AT-SOURCE (I opened the paper PDF / the repo / the API and read the number off the page) · **S** = SECONDARY (a credible source describes it; I did not open the primary) · **U** = UNVERIFIED · **D** = derived by me from a primary table (arithmetic shown).

---

## PART 0 — THE ONE-PARAGRAPH ANSWER

The question "can a model write a correct executable check from prose?" has been measured, repeatedly, in four adjacent literatures, and the measurements agree on a shape that the brief's Part 5 does not yet encode. **Generating a syntactically valid, plausible-looking, even *test-set-correct* check is easy — 77–96% depending on the task.** **Generating a check that actually fires on a seeded fault is hard — 5–19% per attempt in the closest published setting.** And **the gap between those two numbers is exactly the gap L4 exists to measure.** The single most instructive number in this lane is TOGA's: a neural oracle generator reported **96% accuracy on a held-out set** (ICSE 2022) and was subsequently measured at **0.38% precision** and **+0.3% marginal mutation kill** by two independent replication groups. That is §4.4 of the brief — clean, confident, well-formed output that was wrong — happening to a published state of the art, twice, with the field not noticing for eighteen months.

**Recommendation: do NOT pre-register "3 of 10." Pre-register a two-tier threshold on n = 20, split by predicate class, with accept@k reported.** Reasoning and arithmetic in Part 11.

---

## PART 1 — WHAT I SEARCHED, AND THE POSITIVE CONTROLS

Before any absence claim below, the corpus and the control:

| Interface | Query | Result | Control |
|---|---|---|---|
| arXiv API (`export.arxiv.org/api/query`), abstract index | `abs:"data quality assertions"` | **1 result — SPADE arXiv:2401.03038** | **POSITIVE CONTROL PASSED.** The abstract index is live and returns the known-present paper. **V** |
| arXiv API, abstract index | `abs:"false failure rate"` | **2 total results**, neither is SPADE (SPADE's abstract says "false failures", not "false failure rate"), neither is about assertions | SPADE's central metric name has **not propagated into any other abstract on arXiv**. **V** |
| arXiv API, abstract index | `abs:"mutation testing" AND abs:"regulatory"` | **0 results** | **V** |
| arXiv API, abstract index | `abs:"mutation testing" AND abs:"compliance"` | **1 result** — *Test-Driven AI Agent Definition (TDAD)*, arXiv:2603.08806, 9 Mar 2026 (behavioural specs → executable tests for agents; not regulatory filings) | **V** |
| arXiv API, all-fields | `all:"regulatory" AND all:"executable" AND all:"assertion"` | **0 results** | **V** |
| arXiv API, abstract index | `abs:"regulation" AND abs:"LLM" AND abs:"executable"`, newest-first, 30 returned | 30 hits, of which **3** are on point (NormBench 2606.08932; ISO-13849 robotics predicates 2604.20193; floor-plan compliance 2607.00015). **None** measures false-failure rate or mutation kill of a generated regulatory predicate. **V** |
| GitHub REST API `/repos/{owner}/{repo}` | 9 repos | live star/licence/last-push data, Part 9 | **V** |
| WebSearch | ~18 queries across SPADE, EvalGen, TOGA/TOGLL, nl2postcond, SpecGen/AutoSpec/ClassInvGen, AssertLLM, Daikon/DIG, DocETL/LOTUS/Palimpzest/Aryn, RegNLP/ObliQA, BIM ACC | — | — |
| Primary PDFs downloaded and text-extracted locally with `pdftotext` | 12 papers | see Part 2–10; every number below marked **V** was read off the extracted text | — |

**The defensible absence claim, stated with its denominator:**

> Across the arXiv abstract index as queried on 10 Aug 2026 (positive control passed), **no paper reports a false-failure rate or a mutation kill rate for an executable predicate synthesised from regulatory text.** The nearest neighbours — AssertLLM2 (hardware spec documents, 83 designs), nl2postcond (JavaDoc + real code, 525 bugs), De Jure (regulatory rule extraction, LLM-judge scored) — each drop exactly one of the three: regulatory source, executable predicate, or measured error rate. **The combination is genuinely unoccupied.** That is the lane's strongest strategic finding and it survives a control.

Not checked, and I say so: ACM DL and IEEE Xplore full text (ScienceDirect returned HTTP 403; ACM/IEEE not systematically enumerated), non-English literature, and any proprietary vendor evaluation.

---

## PART 2 — SPADE (Shankar, Li, Asawa, Hulsebos, Lin, Zamfirescu-Pereira, Chase, Fu-Hinthorn, Parameswaran, Wu)

**arXiv:2401.03038v2 (31 Mar 2024) · PVLDB Vol. 17 No. 12, pp. 4173–4186 · doi:10.14778/3685800.3685835 · UC Berkeley / HKUST / LangChain / Columbia.** I downloaded `https://www.vldb.org/pvldb/vol17/p4173-shankar.pdf` (1.32 MB, 14 pp) and extracted the full text. Every number below is **V** unless marked **D**.

### 2.1 The algorithm, exactly

**Component 1 — candidate generation from *prompt deltas*.** A prompt delta ΔP_i is the diff between prompt version P_{i−1} and P_i, as a set of sentences each tagged `+` (addition) or `−` (deletion). The insight: developers *implicitly encode data-quality requirements* by editing the prompt over time, so each `+` sentence is a candidate assertion criterion.

Taxonomy built by open + axial coding over **19 LLM pipelines from LangChain users**, each with **3–11 historical prompt versions**, two authors iterating **4 times**. Result: two top-level categories — **Structural (35% of categories identified) and Content-Based (65%)** — with nine leaves: Response Format Instruction, Example Demonstration, Prompt Clarification (structural); Workflow Description, Data Integration, Quantity Instruction, Inclusion Instruction, Exclusion Instruction, Qualitative Criteria (content-based).

**GPT-4 classifies a delta into the taxonomy at F1 = 0.8135** (as of October 2023, against author-assigned ground-truth categories on all deltas from the 19 pipelines).

Generation is **two-step, deliberately** — the authors tried one-step in January 2024 and "observed several omitted assertions that clearly corresponded to categories in our taxonomy":
1. prompt GPT-4 for as many **natural-language criteria** as possible per delta, each aligned to a taxonomy category;
2. prompt GPT-4 to emit a **Python function** implementing each criterion (the function may itself call an LLM).

Every ΔP_i is analysed, not just the final prompt — because "developers often remove instructions from prompts to reduce costs while expecting the same behavior", and because a single complex prompt yields missed assertions.

**Component 2 — selection as an ILP.** Let E′ be a labelled set of runs, y_i ∈ {0,1} (1 = the LLM handled e_i successfully). F = {f_1…f_m} candidates. Select F′ ⊆ F.

- **Coverage(F′)** = (# actual failures caught by ≥1 f ∈ F′) / (# actual failures) — the set's **true-negative rate over failures**.
- **FFR(F′)** = (# non-failures flagged by ≥1 f ∈ F′) / (# non-failures) — the set's **false-alarm rate**.

Objective: `minimize |F′| s.t. Coverage(F′) ≥ α, FFR(F′) ≤ τ`. Decomposed with binary variables u_i (failure e_i covered), z_i (success e_i falsely failed), w_ij = M_ij·x_j. **"Trivially, the problem is NP-hard for τ = 0 and α = 1, via a simple reduction from set cover, and is in NP, since it can be stated in ILP form."** Solved with **PuLP / CBC**; ILPs are "thousands of variables"; measured runtimes **0.104 s – 1.197 s** across the nine pipelines. This solution is `spade_cov`.

**FFR interaction — the part the brief needs verbatim.** SPADE proves and uses the two-sided bound (Eq. 1):

```
max( FFR(S), FFR({f}) )  ≤  FFR(S ∪ {f})  ≤  FFR(S) + FFR({f})
```

i.e. **FFR is monotone non-decreasing under union and sub-additive.** Both halves are load-bearing: monotonicity means adding a check can never *reduce* the set's false-alarm rate, and sub-additivity gives the pruning rule — you need not test `{f_i} ⟹ f_j` if either FFR({f_i}) ≥ τ or FFR({f_j}) ≥ τ.

**Subsumption (`spade_sub`), the novel bit.** When E′ is too small to see all failure modes, coverage-on-E′ is a bad proxy for coverage. So SPADE adds: a set S subsumes f if the conjunction of S implies f. Build matrix K where K_ij = 1 iff f_i ⟹ f_j, via **GPT-4 pairwise implication prompting** (static analysis is impossible because assertions may contain LLM calls), pruned by (a) E′ counterexamples, (b) the FFR bound above, (c) transitivity of implication. Then `minimize |F′| + |G|` where G = non-subsumed excluded functions, subject to the same α, τ constraints.

**Without any examples**, the problem "is no longer NP-hard": subsumption relations form a DAG, and you take a **topological sort and pick the nodes with no incoming edges.** *This is the mode our L3 would run in on day one, before a clean corpus exists.*

**GPT-4 subsumption precision** (proportion of identified subsumed pairs that two authors confirmed; **recall deliberately not measured** — "impracticality of labeling possibly tens of thousands of assertion pairs per pipeline"): per-pipeline **0.68 – 0.90**, **average 0.82**.

### 2.2 The experiment, with denominators

9 pipelines: 8 from LangChain Hub (2 of them from SPADE's own Streamlit deployment), 1 proprietary (`fashion`, a startup, already in production at "tens of thousands of daily runs"). **3–16 prompt versions each. ~75 examples per pipeline on average.** For 6 of 9, examples were **synthetically generated with ChatGPT Pro (GPT-4) and manually reviewed**; 2 from Kaggle; `fashion` from the startup. Thresholds fixed at **α = 0.6, τ = 0.25** for all pipelines.

| Pipeline | # candidate assertions | good ex. | bad ex. | prompt versions | baseline FFR | spade_sub FFR | baseline frac. selected | spade_sub frac. selected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| codereviews | 44 | 60 | 16 | 8 | 0.117 ✓ | 0.117 ✓ | 0.456 (20) | 0.341 (15) |
| emails | 24 | 43 | 55 | 3 | 0 ✓ | 0 ✓ | 0.500 (12) | 0.458 (11) |
| fashion | **106** | 48 | 34 | 16 | **0.878 ✗** | 0.224 ✓ | 0.632 (67) | 0.377 (40) |
| finance | 47 | 48 | 52 | 5 | **0.667 ✗** | 0.208 ✓ | 0.787 (37) | 0.553 (26) |
| lecturesummaries | 70 | 27 | 22 | 14 | **0.528 ✗** | 0.194 ✓ | 0.457 (32) | 0.343 (24) |
| negotiation | 50 | 27 | 19 | 8 | **0.444 ✗** | 0.185 ✓ | 0.400 (20) | 0.340 (17) |
| sportroutine | 26 | 19 | 31 | 3 | 0.211 ✓ | 0 ✓ | 0.538 (14) | 0.308 (8) |
| statsbot | 15 | 39 | 31 | 3 | 0 ✓ | 0 ✓ | 0.467 (7) | 0.467 (7) |
| threads | 34 | 50 | 56 | 4 | 0 ✓ | 0 ✓ | 0.765 (26) | 0.589 (20) |
| **Total / mean** | **416** | | | | **mean 0.316** | **mean 0.103** | **mean 0.5558** | **mean 0.4196** |

All row values **V**. Totals and means **D** (my arithmetic over the paper's own table; 44+24+106+47+70+50+26+15+34 = 416).

**The two headline numbers, decoded.** The abstract says "reduces the number of assertions by 14% and decreases false failures by 21%". From the table: mean(baseline frac. selected) − mean(spade_sub frac. selected) = 0.5558 − 0.4196 = **0.1362 → the "14%" is 13.6 *percentage points of the candidate pool*, not a 14% relative reduction** (relatively it is 24.5% fewer assertions). Likewise mean(baseline FFR) − mean(spade_sub FFR) = 0.316 − 0.103 = **0.213 → the "21%" is 21.3 *percentage points of absolute false-failure rate***. **D.**

> **The brief currently reads "14% fewer assertions / 21% fewer false failures", which invites the weaker relative reading. Both are percentage-point deltas. Say so, or a reviewer who opens Table 4 will find the discrepancy.**

### 2.3 The three SPADE findings that matter most to us — and they are all negative results

**(a) The degenerate operating point, in SPADE's own words.** Verbatim, §4.2:

> "The simplest baseline involves generating candidate assertions and choosing all of them, but it proved ineffective, yielding **100% coverage and 100% FFR** due to at least one assertion failing all tests."

Take every check the model writes, and you flag every clean filing. This is the brief's Part 3.1 "≥95.3% of 43 clean statements" failure mode, reproduced inside the paper the brief proposes to reuse. **L4 test 2 (non-degeneracy) is not a precaution — it is a documented, reproduced failure of exactly this method.**

**(b) 44.4% of raw candidates individually blow a 25% FFR budget.** The `baseline` column is "select every f with FFR({f}) ≤ τ". Its mean selected fraction is 0.5558, so **mean 44.4% of LLM-generated candidate assertions individually flag more than a quarter of good outputs.** **D** from the paper's own fractions.

**(c) Individually-safe checks compose into an unsafe set.** Verbatim, §4.3: "in the fashion and lecturesummaries pipelines, where despite each of the 67 and 32 assertions meeting FFR constraints individually, the total FFR for baseline reaches **88% and 53%**, respectively." That is the sub-additivity bound biting. **A predicate registry that admits checks one at a time, each with an individually acceptable FFR, will silently drift to a flag-everything product.** **V**

**(d) Coverage is bought expensively.** `spade_cov` selects on average **5.5%** of candidates (mean of 0.045, 0.042, 0.028, 0.085, 0.014, 0.040, 0.077, 0.133, 0.029 = 0.0547) **D**, and excludes on average **44% of functions that are not subsumed by the selected set** — i.e. it throws away accurate, non-redundant checks because E′ (≈34 bad examples per task) cannot see their failure mode. **V**

### 2.4 Deployment reality — and a correction to the brief

- "over 2000 runs of the app for custom prompt templates", "across more than 10 sectors like finance, medicine, and IT". **V**
- **Only 48 of those 2000+ runs clicked "download assertions."** The paper notes copy-events were not measured, and "No users clicked the 'thumbs down' button—which is not to say that the generated assertions were perfect." **V**
- **Code: `github.com/shreyashankar/spade-experiments` — 17 stars, 1 fork, NO LICENSE FIELD, last push 2024-04-07** (GitHub REST API, 10 Aug 2026). **V**

> **CORRECTION TO THE BRIEF (§6.1 / ARCHITECTURE L3): "Reuse SPADE" cannot mean "reuse the repo."** The repo has been untouched for 28 months, has one fork, and **carries no licence — which under GitHub's terms means all rights reserved.** What is reusable is the *paper*: the ILP formulation (≈40 lines of PuLP), the FFR sub-additivity bound, the subsumption DAG topological sort, and the two-step criteria-then-code prompting. Write it fresh. The claim "SPADE is deployed in LangSmith over 2,000+ pipelines" describes a **Streamlit prototype released Nov 2023** plus a LangChain integration; I could not verify a live 2026 SPADE surface inside LangSmith and I am not going to assert one.

**Where SPADE fits:** **L3 candidate generation + L4 test 3 (FFR with interaction).** The ILP *is* the admission policy for the predicate registry.
**Where SPADE stops:** (i) its criterion source is prompt-edit history — an *inferred* record of what a developer noticed, not an *authoritative* one; the brief's substitution of statutory text is genuinely novel and genuinely untested. (ii) It has **no mutation testing** — nothing in SPADE asks "can this assertion fire on a seeded fault?", so L4 test 1 has no SPADE analogue. (iii) It optimises over a labelled E′ that we do not have (experiment 9.2). (iv) Selection is one-shot and offline; the authors list "automatically updating assertion sets in deployed pipelines" as open. (v) **Nothing in SPADE declares what it did not check.** Coverage is measured against observed failures, never against a schema. That absence is our L5/L7.

---

## PART 3 — EvalGen / "Who Validates the Validators?" — and the criteria-drift finding

**Shankar, Zamfirescu-Pereira, Hartmann, Parameswaran, Arawjo. arXiv:2404.12272 · UIST 2024 · doi:10.1145/3654777.3676450.** PDF downloaded and extracted. All **V**.

### 3.1 The finding, exactly

> "We observed a 'catch-22' situation: to grade outputs, people need to externalize and define their evaluation criteria; however, the process of grading outputs helps them to define that very criteria. **We dub this phenomenon criteria drift, and it implies that it is impossible to completely determine evaluation criteria prior to human judging of LLM outputs.** Even when participants graded first, we observed that they still refined their criteria upon further grading, even going back to change previous grades."

**Two mechanically distinct drifts** (§7.3.1), from 9 industry practitioners recruited via Twitter, think-aloud over Zoom, NER-on-tweets task, GPT-3.5-Turbo:
1. **New criteria on new failure types** (P2, P5, P6, P8, P9) — participants wanted to add criteria when they saw a new *kind* of bad output; EvalGen's UI made them restart.
2. **Reinterpretation of existing criteria to fit observed behaviour** (P2, P5, P6, P8, P9). The canonical example: a "proper noun" criterion initially meant *all* extracted entities must be proper nouns; after seeing outputs with varying counts, both P2 and P8 wanted it to mean *most*.

**The pre-emptive rebuttal to "just give them more time"** (§8.1, verbatim):

> "The reader might wonder when criteria 'settle.' Perhaps there was simply not enough time in our study... **There is reason to believe that this situation does not change with more time**—as we saw, the criteria participants refined changed to adapt to the behavior of the LLM outputs being evaluated—**a dependent, rather than independent assessment of quality.** In the real world, similar situations exist where criteria are never 'fully settled' as more inputs come in—consider the court of law."

**A third finding the brief should also carry** (§7.3.3): for **code-based** assertions, "EvalGen's interpretation of the criterion (i.e., GPT-4's interpretation) did not match what the participants expected. As such, **no matter how many grades the participant gave, all candidate assertions were similarly misaligned.**" P5 and P9 held *contradictory* readings of the same natural-language criterion ("no hashtag entities") and received the *same* generated assertion. **The formalisation gap is not closed by more labels.**

And (§7.3.2), P3 asked for **per-criterion FFR budgets** rather than one global τ: *"There are criteria where you can be okay with failing, and then there are other criteria where you are like, 'this must absolutely pass'."*

### 3.2 The quantitative arm (§5) — SPADE as the baseline

Two pipelines built from real data: **medical** (84 doctor–patient transcripts, extract fields without PII; **68% of outputs good**) and **product** (100 Amazon products, SEO descriptions; **51% good**). Two authors hand-labelled all outputs.

| | Medical: EvalGen | Medical: SPADE | Product: EvalGen | Product: SPADE |
|---|---:|---:|---:|---:|
| Dataset size | 84 | 84 | 100 | 100 |
| # bad outputs | 27 | 27 | 49 | 49 |
| # assertions | **3** | 5 | **4** | 9 |
| Coverage | 0.33 | 0.33 | **0.73** | 0.49 |
| FFR | 0.10 | 0.10 | 0.39 | 0.39 |
| Alignment (%) | 48.29 | 48.29 | **66.46** | 54.35 |

Alignment ≡ harmonic mean of Coverage and (1 − FFR) — "very similar to F1 score; however, we are concerned with the precision and recall of *failures*."

**Two numbers to carry into the pitch.** (i) On the medical pipeline, **at a 10% false-alarm budget the assertion set catches 33% of bad outputs.** (ii) Verbatim: *"We initially set both false failure rate thresholds to 10%. While SPADE met this threshold for the medical pipeline, **the product pipeline required adjusting the false failure rate to 40%** to find a viable assertion set."* Even a 40% false-alarm rate was needed for a *feasible* solution on a task with a 51% base rate.

**Where EvalGen fits:** it is the **direct successor to SPADE and the strongest argument for the brief's UX commitment.** Criteria drift says: a coverage fraction that is *inspectable and revisable* is not a nicety, it is the only honest interface, because the criteria themselves are not stable objects. It also validates the "unchecked panel as differentiator" and P3's request maps exactly onto **per-predicate FFR displayed in the report** — the brief's Screen 2.
**Where EvalGen stops:** it never leaves the LLM-pipeline setting. It has no mutation testing, no schema, no notion of an authoritative criterion source. **And it is a serious threat to L3's premise:** if criteria drift for a *human expert* on a task they designed, then "statutory text is an authoritative criterion source" is a claim about *statutes*, not about criteria in general — it is only true where the statute is arithmetically closed. Reg 27(1) ("NAV at such frequency") is closed. Third Schedule Part A(g) ("appropriate valuation") is *precisely* a criteria-drift object.

---

## PART 4 — THE TEST-ORACLE LINEAGE: TOGA, its two demolitions, and TOGLL

This is the most decision-relevant sequence in the lane, because it is the only case where a generated-oracle result was published, believed, and then measured properly by two independent groups.

### 4.1 TOGA — the claim (Dinella, Ryan, Mytkowicz, Lahiri. arXiv:2109.09262, ICSE 2022)

Neural (transformer) inference of exception + assertion oracles from the focal method, its docstring, and an EvoSuite test prefix. Claims, **V** from the PDF:
- **"96% overall accuracy on a held out test dataset that fits our grammar and constraints"**; **69% accuracy overall** (i.e. including out-of-vocabulary samples). Assertion model: 96% in-vocab / 69% overall. Exception model: 86%.
- **"finds 57 real world bugs"** on **Defects4J (835 bugs from 17 Java projects)**, "including **30 bugs that are not found by any other automated testing method** in the evaluation", at a reported **FPR of 25%**.

### 4.2 Demolition 1 — Liu, Liu, Xia, Yang, *Towards More Realistic Evaluation for Neural Test Oracle Generation*, ISSTA 2023 (arXiv:2305.17047). **V**

Three flaws named: ① test prefixes generated from **bug-fixed** program versions (unavailable in reality), ② FPR is an unrealistic metric, ③ no straightforward baseline.

| Evaluation method | BugFound | **Precision** | #TP | #FP |
|---|---:|---:|---:|---:|
| TEval@fixed (the original, unrealistic protocol) | 104.2 | 1.13% | 288.0 | 25,237.6 |
| **TEval@buggy** (realistic) | **64.4** | **0.38%** | 110.7 | **29,099.4** |
| **NoException** — degenerate baseline, no assertion at all | **44.4** | **0.77%** | 73.5 | 9,415.9 |

- **"unrealistically generating test prefixes from bug-fixed program versions inflates the number of bugs found by TOGA by 61.8%."**
- **"the Precision of TOGA is only 0.38%, which means developers need to check over 260 test cases that fail on the buggy program version to find a bug-revealing [one]."**
- **The degenerate baseline — literally "expect no exception", zero generated assertions — finds 68.9% of TOGA's bugs at TWICE TOGA's precision**, and finds on average 4.7 bugs TOGA misses. Root cause: *"for the generated test oracles which can find bugs, over 60% of them simply expect no exception raised."*
- **"to the best of our knowledge, no prior work has explicitly compared existing NTOG approaches with this baseline."**

### 4.3 Demolition 2 — Hossain, Filieri, Dwyer, Elbaum, Visser, *Neural-Based Test Oracle Generation: A Large-Scale Evaluation and Lessons Learned*, ESEC/FSE 2023 (arXiv:2307.16023). **V**

Scale: **25 real-world Java systems, 223,557 test prefixes** (202,475 needing an assertion oracle, 21,082 an exception oracle), **51,385 PIT-1.9.8 mutants** (strong mutators only).

- **24.1% overall oracle-type misclassification** (18.3% of assertion prefixes misclassified).
- Of correctly-classified assertion prefixes, **62% (102,606) produced NO assertion at all.**
- Of the **62,920** assertions actually generated, **29,320 = 47% are false positives** (fail on the *original*, correct program). Per type: `assertEquals` **74% FP** (16,059/21,735), `assertTrue` **56%** (9,543/17,025), `assertFalse` 34.7%, `assertNotNull` **9.9%** — but "this type of oracle has limited fault detection power". Worst artifact: **73% FP** (commons-numbers). Type-incorrect / non-compiling assertions were only **563 of 29,000+** — i.e. *the errors are semantic, not syntactic, and would survive a compile gate.*
- **Exception-oracle misclassification: 81% average, up to 94%.**
- **The mutation result — the one that maps onto L4 test 1.** Same prefixes, same number of assertions, three suites: TS1 (implicit oracle only) killed **20,597**; TS2 (EvoSuite assertions) added **9,814**, of which **3,026 unique**; TS3 (TOGA assertions) killed **6,893**, of which **105 unique**. Summary verbatim:

> "out of the 51,385 generated mutants, EvoSuite assertions killed 30,411 (59%) while **TOGA-generated assertions killed 105 additional mutants (0.3%)**."
> "TOGA detected **30% less faults and 96% less unique faults** than EvoSuite assertions."

- The authors' framing, which the brief should steal: *"more than 10% false positives waste developers time causing developers to lose trust in them and gradually abandon them"* — a threshold from the static-analysis adoption literature they cite.
- Their methodological ruling, which we must adopt: **bugs found by implicit oracles (uncaught exceptions) must be excluded from a generator's score**, because the generator did not earn them.

### 4.4 TOGLL — Hossain & Dwyer, arXiv:2405.03786v2 (10 Dec 2024). The state of the art. **V**

Fine-tuned **7 code LLMs × 6 prompts on 110 Java projects**; best pair = TOGLL; generalisation tested on **25 unseen** large projects. PIT-1.9.8, **69,793 strong mutants**.

- Correctness: **3.8× more correct assertion oracles and 4.9× more exception oracles than TOGA.**
- Mutation: EvoSuite **15,985** kills (3,690 unique); **TOGLL 13,318 kills (83% of EvoSuite's), 1,023 unique**; TOGA 43% of EvoSuite's, **105 unique**. So TOGLL is **9.7× TOGA on unique kills** and still **17% below EvoSuite**, despite using EvoSuite's own prefixes.
- Defects4J (374 samples: 304 assertion, 70 exception): TOGA generated assertions for **40% (121/304)**, detecting 26 bugs; **TOGLL for 97%**, detecting 37. Excluding implicit-oracle bugs, **TOGLL detects 64 bugs, 106.5% more than TOGA.** Table V "FP" column: **TOGA 0.45, TOGLL 0.42.**

> **The takeaway, and it is the single most important sentence in this lane: the best fine-tuned oracle generator on record still carries a ~42% false-positive rate and is beaten by a search-based dynamic tool that observes actual execution values.**

**Where the TOGA lineage fits:** it *is* L3+L4, run at industrial scale, four times, by three groups.
**Where it stops:** the oracle target is `assertEquals(expected, actual)` over an arbitrary Java object graph — the hardest possible version of the problem, because the model must *guess the expected value*. Our L1 removes precisely that: a predicate over a schema with 854 stable keys and 294 native formulas is not guessing a value, it is asserting a *relation among known cells*. TOGA's dominant failure (`assertEquals` at 74% FP, "TOGA uses the values 0 and 1 very frequently") **cannot occur in our formulation.** That is a real, defensible reason to expect better than 0.3% — and it is the reason to keep L3 alive long enough to run 9.1.

---

## PART 5 — nl2postcond: THE CLOSEST PUBLISHED ANALOGUE TO L3

**Endres, Fakhoury, Chakraborty, Lahiri. "Can Large Language Models Transform Natural Language Intent into Formal Method Postconditions?" arXiv:2310.01831v2 · PACMSE 1(FSE):1889–1912, July 2024 · Microsoft Research + U. Michigan.** PDF downloaded, full text extracted. All **V**.

This is the closest thing in print to "model writes a formal check from prose", and — critically — **it uses bug-catching as the metric, exactly like the brief's L4 test 1.**

### 5.1 The two metrics — copy these

**Test-set correctness.** Given example ⟨nl, r, T⟩ (natural language, reference impl, tests), a postcondition `post` is *test-set correct* if it holds for the reference implementation on every test in T. Reported as **accept@k** (probability that at least one of k samples is correct) — the pass@k estimator from Codex.

**bug-completeness-score.** For a set of code mutants CM:

```
bug-completeness-score(post, CM, T) = |{ c ∈ CM : ∃ i ∈ T . eval(post, (i, c(i))) == false }| / |CM|
```

= the fraction of mutants the (correct) postcondition kills. A postcondition with score 1 is *bug-complete*. Lifted to sets by union.

**The two metrics are explicitly necessary-and-not-sufficient**: correctness alone admits `return_val is not None`.

**Their own validation of the metric — the discipline to copy.** (a) They audited test-set correctness for false positives on 900 postconditions: **only 1.1% were spuriously "correct"** on EvalPlus (775 tests/problem), versus **7% if the weaker HumanEval suite were used**. (b) They separated **natural** mutants (real alternative buggy implementations) from **artificial** seeded faults and found completeness "consistently lower when only [natural bugs are used]", warning that **artificial faults inflate the metric**. This is *directly* the brief's §9.2 worry about a synthetic clean corpus, measured.

### 5.2 RQ1 — EvalPlus (164 Python problems, 775 tests/problem avg; 10 postconditions per problem per variant; **19,680 postconditions** total)

**Test-set correctness (accept@k):**

| Model | Prompt | ref code in prompt | @1 | @5 | @10 | problems with ≥1 correct (/164) |
|---|---|---|---:|---:|---:|---:|
| GPT-4 | simple | ✗ | **0.77** | **0.94** | **0.96** | **158** |
| GPT-4 | simple | ✓ | 0.76 | 0.92 | 0.96 | 157 |
| GPT-4 | base | ✓ | 0.71 | 0.89 | 0.91 | 150 |
| GPT-4 | base | ✗ | 0.63 | 0.83 | 0.88 | 144 |
| GPT-3.5 | simple | ✓ | 0.56 | 0.82 | 0.88 | 144 |
| StarChat | simple | ✗ | 0.25 | 0.69 | 0.85 | 139 |

**Bug-completeness:**

| Model | Prompt | ref | % postconds bug-complete | % problems with ≥1 bug-complete | % problems **union** bug-complete | avg score (natural bugs) | avg (all bugs) |
|---|---|---|---:|---:|---:|---:|---:|
| **GPT-4** | **base** | ✗ | **35.1** | **61.6** | **62.2** | **0.81** | **0.85** |
| GPT-4 | base | ✓ | 34.9 | 58.0 | 61.6 | 0.78 | 0.82 |
| GPT-4 | simple | ✓ | 8.9 | 29.3 | 36.0 | 0.47 | 0.56 |
| GPT-4 | simple | ✗ | 9.2 | 26.2 | 29.3 | 0.40 | 0.52 |
| GPT-3.5 | base | ✓ | 18.5 | 47.0 | 49.4 | 0.70 | 0.76 |
| StarChat | simple | ✓ | 3.0 | 17.1 | 17.7 | 0.23 | 0.36 |

> **THE CENTRAL TRADE-OFF, MEASURED.** The prompt that maximises *correctness* (simple, accept@1 = 0.77) collapses *completeness* (26.2% of problems get a bug-complete postcondition). The prompt that maximises completeness (base, 61.6%) is less correct (accept@1 = 0.63). **You cannot ask for both in one prompt.** "simple postconditions are significantly more likely to be correct with p = 0.008, a large effect (Cohen's d = 1.73)"; base postconditions have "up to a 30% difference" higher bug-completeness. **L3 must run at least two prompt regimes and let L4 arbitrate — a single prompt will sit on one horn.**

**Also:** including the reference solution in the prompt gives **no significant correctness gain** (p = 0.42). Natural-language intent alone is enough on EvalPlus. *(This matters: our L3 has statutory text but no "reference implementation" of a correct filing.)*

### 5.3 The taxonomy of what LLMs actually write — the degeneracy map

900 postconditions from 139 problems, hand-labelled by two authors. **33% are conjunctions** of atomic checks.

| Atomic category | Example | Prevalence % | avg bug-complete (natural / all) |
|---|---|---:|---:|
| **Type Check** | `isinstance(return_val, int)` | **47.4** (most common) | **0.14 / 0.27** (weakest) |
| Null Check | `return_val is not None` | 4.4 | 0.40 / 0.50 |
| Forall-Element | `all(ch.isalpha() for ch in rv)` | 8.3 | 0.23 / 0.44 |
| Arithmetic Bounds | `return_val >= 0` | 30.8 | 0.23 / 0.34 |
| Element Property | `return_val[0] % 2 == 0` | 12.6 | 0.39 / 0.53 |
| Format Check | `rv.startswith("ab")` | 11.2 | 0.43 / 0.57 |
| Container Property | `len(rv) > len(input)` | 27.0 | 0.45 / 0.57 |
| Implication | `(rv==False) if 'A' not in s` | 12.7 | 0.58 / 0.64 |
| **Arithmetic Equality** | `return_val[0] == 2*input_val` | 17.5 | **0.82 / 0.89** (strongest) |
| **Average** | | | **0.32 / 0.46** |

> **"the weakest postcondition type, Type Checks, killed only 14% of natural bugs on average while the strongest, Arithmetic Equality check, killed 82%, a 6× difference"** — and **Type Checks are the most prevalent category.** The model's *modal* output is its *weakest* output. This is the shape of the degeneracy L4 test 2 must catch, and it is now a labelled taxonomy we can reuse as a rejection list.

### 5.4 RQ2 — Defects4J, the real-bug arm (**this is the direct analogue of experiment 9.1's spirit**)

Setup: Defects4J 2.0 (835 bugs / 17 projects) restricted to the **525 bugs reproducible under Java 8**, **840 modified functions**, **33,600 postconditions** (2 models × 2 ablations × 10 samples × 840 functions). Natural language = the buggy function's **JavaDoc only** — no code summarisation, no external docs. Class/type context and call-graph methods added greedily via Tree-sitter until the context window fills.

**Bug-discriminating** ≡ passes all trigger + regression tests on the **fixed** version AND fails a trigger/regression test on the **buggy** version. *(This is a clean-corpus FFR gate and a mutation-kill gate, fused, and it is exactly the L4 shape.)*

| Model | buggy code in prompt | Compiles @1/@5/@10 | Test-set correct @1/@5/@10 | # distinguishable bugs (/525) |
|---|---|---|---|---:|
| GPT-4 | ✓ | 0.73 / 0.90 / **0.93** | 0.39 / 0.66 / **0.75** | **47 (9.0%)** |
| GPT-4 | ✗ | 0.65 / 0.86 / 0.89 | 0.32 / 0.57 / 0.66 | 35 (6.7%) |
| StarChat | ✓ | 0.29 / 0.72 / 0.84 | 0.12 / 0.39 / 0.56 | 24 |
| StarChat | ✗ | 0.25 / 0.68 / 0.83 | 0.11 / 0.38 / 0.55 | 19 |

**Union over all models and prompt variants: 70 buggy methods from 64 unique bugs = 12.2% of the 525 bugs considered.**

Unlike EvalPlus, **including the buggy code in the prompt DOES help on real code** — because JavaDoc comments are "not completely descriptive" and the objects are complex.

**Where nl2postcond fits:** it is the *methodological template* for experiment 9.1. Copy: (a) the correctness/completeness split, (b) accept@k with k = 10, (c) the mutant-based completeness denominator, (d) the manual audit of metric false positives, (e) the natural-vs-artificial-bug caveat, (f) the atomic-category taxonomy as a degeneracy screen.
**Where it stops:** the "prose" is a docstring written by the same person who wrote the code, describing *this function*. Statutory text is written by a regulator, describes a *class* of filings, contains provisos and cross-references, and has no accompanying implementation. Nobody has run nl2postcond's protocol on statutory text. **That is the gap 9.1 fills, and it is publishable on its own.**
**Assets:** `github.com/microsoft/intent-formalization` (formerly `nl-2-postcond`) — **MIT, 27★, 7 forks, last push 2026-03-18** (GitHub API, **V**). It is *artefacts and evaluation data*, not a runnable pipeline. Their metric definitions are worth transcribing directly.

---

## PART 6 — SPEC SYNTHESIS WHEN A CHECKER EXISTS: the 99.5% band, and why it does not transfer

There is a second literature where LLM-written specifications succeed spectacularly. **It succeeds because a sound automatic rejector exists.** Naming this explicitly reframes the whole L3/L4 question.

| System | Task | Benchmark (denominator) | Result | Warrant |
|---|---|---|---|---|
| **AutoSpec** (arXiv:2404.00762, SEFM/ICFEM-line) | C program specs (ACSL) verified by **Frama-C** | Frama-C-problems, **51 programs** | **31/51 = 60.8%** solved; avg 89.17 s/case; stable over 5 runs | S |
| **SpecGen** (arXiv:2401.08807, **ICSE 2025**, doi:10.1109/ICSE55347.2025.00129) | Java JML specs verified by **OpenJML**; conversational phase + 4 mutation operators (predicative, logical, comparative, arithmetic) + heuristic selection | SV-COMP + SpecGenBench, **385 programs** | **279/385 = 72.5%** verifiable, **+32 over AutoSpec**; avg success probability **59.97%** vs Conversational 35.95%, AutoSpec 46.13%; human-rated semantic quality **4.54/5.00** | S |
| **ClassInvGen** (arXiv:2502.18917v2, Stanford/MSR/Purdue) | C++ class invariants, **co-generated with tests** | 9 standard data structures | see below | **V** |
| Loop-invariant line (CLN2INV → LaM4Inv → NeuroInv/LimICE/InvWeaver) | loop invariants checked by an SMT solver | Code2Inv 124/133; LaM4Inv 316; multi-loop 82 | CLN2INV **124/124**; LaM4Inv **309/316**; NeuroInv reported **99.5%** avg success vs SpecGen 28.5% and ad-hoc prompting 66.4%; InvWeaver **72/82** on multi-loop | S |

### 6.1 ClassInvGen in detail — because it runs *our exact L4 protocol*

- **Invariant-only generation:** avg **25.22** invariants per benchmark, **24.56** compile, **19.44** pass the unit tests → **77.0% pass rate** (range 54.5% `heap` – 100% `queue`). **V**
- **With test co-generation:** filtering reduces to **17** per example, all correct; one refinement round grows it back to **22** (**+29%**) at a **100% pass rate**. **"ClassInvGen's invariant-test co-generation approach improves correctness from 77% to 100%."** **V**
- **Completeness by mutation:** `mutate_cpp`, **236–682 mutants per program**. **1,057** mutants survived the unit tests alone; ClassInvGen invariants killed **118 more = 11.16%** improvement (per-structure range **0.00%** `avl_tree` – **32.67%** `vector`). **V**
  - Per-unit reading, and this is the number closest to 9.1's shape: **8 of 9 data structures (89%) yielded at least one invariant that killed a mutant the tests missed.** **D**
- **Versus Daikon** (see Part 7): "each benchmark example has around 5 Daikon invariants"; of **40 correct Daikon invariants** across the 9 benchmarks, **27 are merely "class pointer is not null"** and **6 are "element count non-negative"**; **7 incorrect Daikon invariants passed unit-test validation.** Authors' diagnosis: *"Daikon... cannot differentiate between universally true invariants and those that hold only in specific test contexts."* **V**

> **THE STRUCTURAL LESSON OF PART 6.** Loop-invariant synthesis is at 99.5% because an SMT solver returns *sound* accept/reject for free, so generate-and-test converges. nl2postcond RQ2 is at 12.2% and AssertLLM2 at 5–19% because no such rejector exists and the "check" is scored against reality. **L4 is our rejector. The design question for 9.1 is therefore not "can the model write a check" — it is "is our rejector cheap, sound-enough, and fast enough that generate-and-test converges?"** Mutation kill + degeneracy screen + FFR-on-clean is a *sound-enough* rejector for the arithmetic class of obligations and an *unsound* one for the judgment class. That, not model capability, is what determines 9.1's outcome.

---

## PART 7 — INVARIANT MINING WITH NO MODEL AT ALL: Daikon, DIG

### 7.1 Daikon

- **What it is** (`plse.cs.washington.edu/daikon/`, **V**): *"an implementation of dynamic detection of likely invariants."* It **"runs a program, observes the values that the program computes, and then reports properties that were true over the observed executions."** Supports C, C++, C#, Eiffel, F#, Java, Perl, Visual Basic, **"in spreadsheet files; and in other data sources."**
- **Mechanism:** instantiate a fixed library of ~50+ **invariant templates** (unary/binary/ternary over scalars, sequences, strings — `EltLowerBound`, `EltUpperBound`, `EltOneOf`, linear relations, comparisons, `Comparable.compareTo` orderings) at every program point, then falsify them against observed traces. **"Daikon never outputs invariants that were ever false."** Survivors are filtered by a **statistical confidence test, `--conf_limit`, default 0.99**; each invariant class has its own confidence formula (e.g. `a<b` uses `1 − 1/2^numsamples`). **V**
- **Status, from the GitHub REST API on 10 Aug 2026 — this is a live tool, not a museum piece:** `codespecs/daikon`, **260 stars, 63 forks, last push 2026-08-08 (two days ago), not archived**, latest release **5.8.25 on 7 May 2026**. **V**
- **Licence:** `LICENSE.txt` is a **verbatim MIT-style permissive grant** ("Permission is hereby granted, free of charge... without restriction... to use, copy, modify, merge, publish, distribute, sublicense, and/or sell"), Copyright 1998–2025, with an added no-trademark-use clause. GitHub's classifier reports `NOASSERTION` because of that clause; the *terms* are MIT-equivalent. **V** (I fetched the raw file.)
- **`scripts/convertcsv.pl` exists on master (HTTP 200).** Daikon ships a **comma-separated-value front end.** **V**

**What Daikon would give us if pointed at a corpus of correctly-filled workbooks.** Flatten each filing to one CSV row keyed by L1's stable field keys; run `convertcsv.pl` → `.dtrace`; run the detector. Sketch:

```bash
# one row per filing, one column per L1 stable key
python3 flatten_workbook.py corpus/*.xlsx > filings.csv
perl $DAIKONDIR/scripts/convertcsv.pl filings.csv        # -> filings.dtrace + .decls
java daikon.Daikon --conf_limit 0.99 filings.decls filings.dtrace
```

Expected yield, by analogy to ClassInvGen's measurement: **linear equalities between numeric fields (the 35 SUM identities and the 181 cross-sheet carries would fall straight out as `a == b`), range bounds, one-of sets for the 3 list-validation vocabularies, orderings between the 15 date fields, and non-null/non-negative facts.** That is a *free, model-free, deterministic* first pass over precisely the decidable half of §4.3.

**The false-invariant problem, quantified.** From ClassInvGen §4.5 (**V**): 40 correct Daikon invariants across 9 benchmarks, **27 of them (67.5%) merely "pointer is not null"**, 6 "count non-negative"; and **7 spurious invariants survived unit-test validation** because "both the filtering tests and unit tests coincidentally constructed similar data structures." Daikon's own literature is explicit that likely invariants are "both incomplete and unsound in the general case, and hence incur both false negatives and false positives" (**S**). **On our corpus this is severe:** with ~40 hand-built clean filings (experiment 9.2's realistic ceiling), `--conf_limit 0.99` on `a<b` is satisfied at ~7 samples, so Daikon will emit dozens of relations that are true of *our synthetic corpus* and false of *the 868 real annual filings*. **Every Daikon-mined invariant must go through the same L4 gate as a model-written one, and its FFR must be labelled "measured on a synthetic clean corpus of n filings."**

**Where Daikon fits:** **an L3 alternative that costs nothing and needs no model** — and, better, **an L3 *baseline*: the degenerate-baseline arm of experiment 9.1.** If a model-synthesised predicate set does not beat Daikon-on-the-clean-corpus at mutation kill, L3 has earned nothing.
**Where it stops:** templates are fixed, so it can never express "scheme authorisation date ≤ period end **as required by reg X**" — it has no notion of a clause, no provenance to a statute, and therefore **cannot populate the predicate library's "clause" column**, which is the auditor-facing artefact. It also cannot see anything not varying in the corpus.

### 7.2 DIG

Nguyen, Kapur, Weimer, Forrest, *DIG: A Dynamic Invariant Generator for Polynomial and Array Invariants*, **ACM TOSEM 23(4), Art. 30, 2014** (**S** — I read the abstract and secondary descriptions, not the full PDF). Key difference from Daikon: **generative, not template-filtering** — it infers **nonlinear polynomial equalities and inequalities of arbitrary degree** and nested array relations directly from traces using equation solving, polyhedra construction and theorem proving. Later work extends it to disjunctive invariants (arXiv:1904.07463).

**Where DIG fits:** the fee-arithmetic and percentage-composition predicates in §4.3 are polynomial, and Daikon's linear templates will miss them. **Where it stops:** I did not verify a maintained repository, licence, or Python/CSV front end. **Treat as EVALUATE, not ADOPT.** Do not put it on a slide until someone opens the repo.

### 7.3 Learned invariants — brief, and a warning

CLN2INV (ICLR 2020) solved **124/124** Code2Inv problems, 40× faster than LoopInvGen (**S**). Modern LLM-hybrid work reports **LaM4Inv 309/316**, **InvWeaver 72/82** multi-loop, **NeuroInv ~99.5%** (**S — secondary only; I did not open these**). ClassInvGen's related-work section flags the trap directly: learned-invariant models whose "training data consists of Daikon-generated invariants... **inherit the limitations of Daikon**" (**V**). Do not build on a model trained on Daikon output and then claim independence from Daikon's false-invariant problem.

---

## PART 8 — ASSERTIONS FROM SPECIFICATION *DOCUMENTS*: AssertLLM and AssertLLM2

This is the transferable pattern the brief asked for, and **AssertLLM2 is the single most important new number in this lane.**

### 8.1 AssertLLM (arXiv:2402.00386, v1 1 Feb 2024, v3 4 Nov 2024; ASP-DAC 2025, doi:10.1145/3658617.3697756)

Three customised LLMs in sequence: extract structured specification → map signal definitions → generate SystemVerilog Assertions. Processes **complete specification files**, not engineer-extracted sentences. Abstract, verbatim (**V** via arXiv abstract page): *"Our evaluation of AssertLLM on a full design, encompassing 23 I/O signals, demonstrates that **89% of the generated assertions are both syntactically and functionally accurate**."* Secondary sources give the breakdown as **56 properties over 23 signals — 23 bit-width, 16 connectivity, 17 function** (**S**).

**Denominator discipline: 89% is one design, 56 assertions.** Do not quote it as a general rate.

### 8.2 AssertLLM2 (Wu, Fang, Wang, Li, Guo, Xie — HKUST, arXiv:2605.27472v1, 26 May 2026). **V** — PDF downloaded and read.

**83 real-world designs across 13 functional categories.** Each ships: a structured specification document, a **verified dependency-complete golden RTL**, and **systematically mutated buggy RTL variants** (PyVerilog AST-level mutation, single-mutation-per-mutant, feasibility-screened, deduplicated, reset/clock signals filtered out). Two settings: **bug-prevention** (assertions from the spec alone) and **bug-hunting** (buggy RTL in the input). Evaluation in **Cadence JasperGold**; FEC in Cadence Conformal. **6 models, 3 runs each**, reported as *average* and *union of the 3 runs*.

Metrics, verbatim: syntax = "proportion of generated assertion sets that are syntactically valid and cleanly elaborable"; FPV outcomes = Proven / CEX / Undetermined on golden RTL; COI, proof and formal coverage; and **"Mutation-Based Bug Kill Ratio. The fraction of valid, non-equivalent bugs killed by the generated assertions."** — note **"non-equivalent"**: they solve the equivalent-mutant denominator problem the brief flags in L4 test 1.

**Table 4 — the whole result:**

| Setting | Model | Syntax % | FPV P/T | COI cov. | Proof cov. | Formal cov. | **Bug Kill Ratio** |
|---|---|---:|---:|---:|---:|---:|---:|
| Average | Gemini-2.5-Pro | 88.29 | 13/20 | 62.47 | 20.19 | 19.16 | **9.76** |
| Average | Claude-Sonnet-4.5 | 93.04 | 21/38 | 65.65 | 23.30 | 22.38 | **11.69** |
| Average | GPT-5.2 | **95.00** | 22/30 | 61.69 | 22.46 | 21.18 | **10.19** |
| Average | DeepSeek-V3.2 | 88.94 | 13/22 | 58.70 | 16.75 | 15.73 | 9.20 |
| Average | Qwen3-Coder-Plus | 77.93 | 8/18 | 54.88 | 12.77 | 12.07 | 6.82 |
| Average | LLaMA-4-Maverick | 89.23 | 5/13 | 37.27 | 9.09 | 8.46 | 5.08 |
| **Union (3 runs)** | Gemini-2.5-Pro | 88.29 | 39/61 | 66.89 | 27.10 | 25.71 | **18.51** |
| **Union** | Claude-Sonnet-4.5 | 93.04 | 64/115 | 68.36 | 29.72 | 28.32 | **16.31** |
| **Union** | GPT-5.2 | 95.00 | 65/91 | 64.06 | 28.62 | 27.15 | **14.87** |
| **Union** | DeepSeek-V3.2 | 88.94 | 38/65 | 61.51 | 25.66 | 24.17 | 15.32 |
| **Union** | Qwen3-Coder-Plus | 77.93 | 25/53 | 55.96 | 19.72 | 18.55 | 12.18 |
| **Union** | LLaMA-4-Maverick | 89.23 | 15/38 | 49.36 | 13.64 | 12.69 | 8.04 |

**The authors' own summary, verbatim, and it is our thesis in someone else's words:**

> "Most models already exceed 80% syntax success, the strongest commercial models approach 95%, their functional correctness exceeds 70%, and even on the system-scale designs in AssertLLM2, leading models achieve over 60% COI coverage. **These results reveal a fundamental limitation of prior work: they often evaluate assertion generation only through easier metrics. Under these criteria, current models can appear highly capable.** However, AssertLLM2 shows that strong syntax success, basic provability, and broad structural reach do not translate into equally strong proof coverage or bug detection capability."

> "Although current LLMs are capable of producing well-formed and structurally relevant assertions, **they still struggle to synthesize assertions that are consistently behaviorally rigorous and functionally discriminative.**"

And a second finding that vindicates a *multi-metric* report over a single score: *"GPT-5.2 is more precision-oriented, generating fewer but more reliable assertions, whereas Claude-Sonnet-4.5 is more exploratory. **Under prior metrics alone, GPT-5.2 would appear uniformly superior, and this difference in generation strategy would be largely invisible.**"*

**One discrepancy I must flag rather than smooth over:** the prose says the bug kill ratio peaks "in the high-20% range even under the union setting", but **Table 4's maximum union bug kill ratio is 18.51%**; the high-20s figures are the *proof coverage* column (25.66–29.72). I take the table as authoritative and report **8.04–18.51% union / 5.08–11.69% average**. Anyone quoting the prose sentence will be quoting an internal inconsistency.

**Repo:** `github.com/hkust-zhiyao/AssertLLM2` — **11★, 2 forks, NO LICENSE, last push 2026-05-26** (GitHub API, **V**). The *benchmark construction* is the reusable artefact, not the code.

**Where AssertLLM2 fits:** it is the **closest measured analogue to the entire L3+L4 pipeline**: a *specification document* in, executable checks out, scored by syntax + provability + coverage + **mutation kill on non-equivalent mutants**. Its four-metric report is almost exactly the brief's L4 three tests plus a coverage number, and its **average-vs-union** convention is precisely how we should report accept@k in 9.1.
**Where it stops:** SystemVerilog with a formal engine (JasperGold) available as a rejector; hardware specs are far more precise than statutes; and there is no notion of false-failure rate on a *clean corpus of filled artefacts* — the golden RTL plays that role.

---

## PART 9 — REGULATORY TEXT → RULES: what actually exists

### 9.1 De Jure (Guliani, Gill, Landsman, Eshraghi, Kumar, Gondara — **The Vanguard Group**, arXiv:2604.02276v1, 2 Apr 2026). **V**

Fully automated, domain-agnostic, **no human annotation and no gold data**. Four stages: normalise source → Markdown; **LLM semantic decomposition into structured rule units**; **multi-criteria LLM-as-a-judge across 19 dimensions** (metadata, definitions, rule semantics); **iterative repair of low-scoring extractions within a bounded regeneration budget**, upstream components repaired before rule units are evaluated. Four models × three corpora (finance, healthcare, AI governance). *"reaching peak performance within at most three judge-guided iterations."* Downstream: compliance QA via RAG, **judge-LLM preference over prior work in 73.8% of cases at single-rule retrieval depth, rising to 84.0% under broader retrieval.**

**Where it fits:** the *ingestion and decomposition* half of L3 — turning a 102-page instrument into addressable rule units — is exactly our problem, and a large asset manager built it.
**Where it stops, and this is the whole point:** De Jure's rule units are **structured, not executable**. Nothing is run against a filing. And **every quality number is an LLM judging another LLM** — the brief's own Part 3.3 says an LLM judge detects false success at AUROC ≤ 0.65. **A 73.8% judge-preference rate is not an error rate.** De Jure is the state of the art in regulatory rule extraction and it does not produce a single quantity that could be printed next to a check in our predicate library.

### 9.2 NormBench / Span-Grounded Deontic Trees (Chen, Li, Wan, Yuan — HKUST-GZ + SYSU, arXiv:2606.08932v1, 8 Jun 2026, **KDD 2026**, CC-BY-4.0). **V**

**2,290 provisions** — Chinese laws and local policies, English (**U.S. tax law, GDPR**, corporate policies), and cross-lingual. Task: **defeasible scope parsing** — "identifying precisely which clause overrides which" — into **Span-Grounded Deontic Trees**, "a compiler-style intermediate representation that anchors every logical branch to source spans and requires explicit exclusion guards, enabling deterministic compilation and audit."

Failure class named: **Silent Scope Omission (SSO)** — *"a model applies a general rule but silently drops nested exceptions or counter-exceptions, producing outputs that appear compliant yet break on important edge cases."*

**Table 4, random split — this is the number that should govern our expectations for statutory obligations with provisos:**

| Model | Done rate | NodeSpan-F1 | **Edge-F1** | SpanFaith | Halluc ↓ | Tree-ES | DefRec | DefRec@Gold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Gemini-3-Pro-preview | 0.828 | 0.452 | **0.246** | 0.773 | 0.227 | 0.643 | 0.760 | 0.545 |
| GPT-5.2 (2025-12-11) | 0.841 | 0.420 | **0.215** | 0.793 | 0.207 | 0.629 | 0.776 | 0.569 |
| Claude-Opus-4.5 | 0.767 | 0.429 | **0.228** | 0.707 | 0.291 | 0.592 | 0.715 | 0.640 |
| ChatLaw (legal-domain) | 0.725 | 0.180 | 0.047 | — | — | — | — | — |
| LawGPT (legal-domain) | 0.763 | 0.158 | 0.048 | — | — | — | — | — |

Two named pathologies:
1. **Recursion Decay** — "performance drops sharply as defeater depth increases", "driven by logical depth, not context length. Even when controlling for token count, models struggle significantly more with [deeper defeaters]."
2. **The Auditability Trap** — verbatim: *"The drop from recovering nodes (NodeSpan-F1 ≈ 0.45) to correctly wiring them (Edge-F1 ≈ 0.24) indicates that models struggle [to assemble control flow]... Frontier models achieve high SpanFaith (0.77–0.79) and low [hallucination], [but] this grounding does not cash out into valid control flow."*
3. **The Domain Paradox** — legal-domain fine-tunes (ChatLaw, LawGPT) are **near-random** on structure (NodeSpan-F1 ≈ 0.18, Edge-F1 ≈ 0.04). *Do not reach for a "legal LLM".*

> **DIRECT IMPACT ON 9.1's SAMPLING FRAME.** Our source instrument is riddled with defeaters: **reg 39(1) has a half-yearly proviso for close-ended restricted schemes; regs 26(2)/38(2)/50(2) carry a fund-of-funds proviso; reg 51(1) ends "in such manner as specified by the Authority"** — an open delegation. NormBench says frontier models will read those spans correctly (SpanFaith 0.77–0.79) and **wire them into the predicate wrongly about three times in four (Edge-F1 ≈ 0.22)**. A predicate that implements reg 39(1) *without* the proviso will pass a mutation test and pass FFR on a clean corpus that contains no close-ended restricted scheme — **and be wrong in production.** L4 as specified does not catch this. See Part 12.

Repo: `github.com/AlexJJJChen/NormBench` — **0★, 1 fork, CC-BY-4.0, last push 2026-02-09** (**V**). New, unadopted, but the *dataset* is the asset.

### 9.3 "Confidently Wrong" (Simpson, Kozak, Doake — Aethis, arXiv:2607.23386v1, 25 Jul 2026). **V**

A **commercial preprint** — treat accordingly — but it is the closest thing in print to our architecture, arrived at independently, and it states the L3/L4 boundary better than the brief currently does.

Architecture: *"uses LLMs to author rules from authoritative sources, then executes those rules through an SMT-based deterministic evaluation layer."* Failure class documented: **exception chain collapse** on rules of the form "A is required UNLESS B, UNLESS C overrides B" — the same object as NormBench's SSO. Evidence: 225 scenarios / 4 regulatory domains; a 20-scenario adversarial construction-insurance extension (engine 20/20; **three of four frontier-LLM configurations fail the same coverage-gap edge case**); external validation on 9 LegalBench tasks / **949 held-out cases**, engine significantly more accurate than each of three frontier models (combined McNemar p ≤ 0.003, margins up to **+41 percentage points**).

**And the observation that should go straight into the brief's risk register:**

> "its empirical surface is unstable: between March and April 2026, several reported failure cells closed silently under the same model alias, with no version bump (**GPT-5.4 on construction insurance moved from 96.6% to 100% on the same prompt and harness**)... **frontier-model accuracy is a moving compliance boundary, and it moves without notice.**"

**Their three-level honesty, verbatim (§5.5) — this is our L0/L2/L3 vs L5 split, named:**

> "**Level 1 – Source text retrieval.** ... The system does not guarantee that all relevant source text was found and correctly parsed.
> **Level 2 – Rule formalisation.** LLMs generate rules from source material. An incorrectly formalised rule produces incorrect determinations, even if the execution is formally correct. This is the 'garbage in, garbage out' property stated precisely: **deterministic execution of incorrectly formalised rules produces incorrect but deterministic results.** The system addresses this through test-driven validation: subject matter experts define test cases... and authored rules must pass these test suites before deployment. Rules can also be reviewed by human experts, but **the primary quality gate is automated test-case validation, not manual review.**
> **Level 3 – Rule execution.** ... guaranteed by the execution semantics."

> "By solving Level 3 first, the system **reduces the trust problem to a single surface — rule formalisation quality**."

**Where it fits:** independent convergence on "model authors, program adjudicates". Cite it as prior art *and* as a competitor.
**Where it stops — and this is our wedge:** **their Level-2 gate is SME-hand-written test cases. Ours is mutation testing plus a degeneracy baseline plus an FFR on a clean corpus, and ours produces a number that goes on the artefact.** They reduce trust to one surface and then do not measure it. **We measure it and print it.** They also make no coverage declaration: nothing in the architecture says which obligations were *not* formalised.

### 9.4 The rest of the regulatory-NLP field, and what it proves by omission

- **RegNLP / RIRAG / ObliQA** (arXiv:2409.05677; COLING 2025 RegNLP workshop; `github.com/RegNLP/ObliQADataset`) — **27,869 questions** derived from **Abu Dhabi Global Market** financial regulation: **40 documents, ~640,000 words**, 30–100 pages each, with subsections, numbered clauses and cross-references. Evaluated with **RePASs**, a metric for whether generated *answers* capture obligations without contradiction. **S.**
  **This is the direct IFSC peer** — ADGM is GIFT City's closest comparator — and **the flagship benchmark for it stops at retrieval and answer generation, scored by a model.** Not one executable check. That is the absence, in the most favourable possible corpus.
- **CODE-ACCORD** (arXiv:2403.02231) — a corpus of building-regulatory data for rule generation toward automatic compliance checking. **S.** The *pattern* to imitate: a public, licensed corpus of clause→rule pairs is what makes a field measurable. Our 8,866 "shall" occurrences across 361 circulars is the raw material for the Indian analogue.
- **BIM automated compliance checking.** The mature version of our problem, 20 years old. Consistent finding: *"rule interpretation is one of the most complex stages... the main bottleneck is the automated conversion of human-readable rules into machine-readable formats."* A 2025 LLM result reports **97% F1 rule interpretation / 98% F1 execution** — **S, and I could not verify it: ScienceDirect returned HTTP 403.** **Do not put 97%/98% on a slide.** Note also that the metric is *interpretation F1*, not fault detection; per AssertLLM2's lesson, that is the "easier metric" class.
- **Related 2026 arXiv hits worth one read each, all UNVERIFIED beyond title/abstract-line:** arXiv:2604.20193 (LLM translates natural-language safety regulations into **executable predicates** for ISO 13849 robotics — closest formulation by wording); arXiv:2607.00015 (floor-plan compliance, building codes → executable rules); arXiv:2603.08806 (TDAD — behavioural specs compiled to executable tests).
- **Rules-as-code for finance remains dead**, per the brief's §7. Nothing in this lane contradicts that. NormBench's Table 1 makes the same point academically: *"LegalRuleML and Catala provide richer execution semantics but typically require manual predicate engineering and detach from source"*.

---

## PART 10 — LLM DATA-PROCESSING SYSTEMS WITH VALIDATION LOOPS

Live repo data from the GitHub REST API, 10 Aug 2026. All **V**.

| System | Repo | ★ | Forks | Licence | Last push | What it gives L3/L4 | Where it stops |
|---|---|---:|---:|---|---|---|---|
| **DocETL** | `ucbepic/docetl` | **3,961** | 421 | **MIT** | **2026-08-09** | VLDB 2025 (PVLDB 18 p.3035), arXiv:2410.12189. **Agentic query rewriting with 13 rewrite directives** for LLM operators + an **agent-guided plan evaluation mechanism that synthesises and orchestrates task-specific validation prompts**. Ships **gleaning**: `validate:` statements + `num_retries_on_validate_failure:` — LLM-validator-driven retry using the failure as context. Reports plans **21–80% more accurate** than well-engineered baselines on 4 tasks (**S** for the 21–80%). | The validators are **LLM prompts**, not programs — a model judging a model, the exact configuration the brief's Part 3.3 rules out as a final judge. No mutation testing, no FFR, no coverage declaration. **Use its rewrite-directive machinery and its retry plumbing; never let its validator be terminal.** |
| **LOTUS** | `lotus-data/lotus` | 1,658 | 149 | **Apache-2.0** | 2026-07-03 | Semantic operators (arXiv:2407.11418) with **model cascades and proxies** and, per its README, **statistical accuracy guarantees**. | Guarantees are about *approximating an expensive oracle operator cheaply*, not about whether the oracle is right. Orthogonal to L3. |
| **Palimpzest** | `mitdbg/palimpzest` | 233 | 49 | **MIT** | 2026-07-30 | The original semantic-operator optimiser; cost/quality trade-off across plans; PalimpChat (arXiv:2502.03368). | Same: plan optimisation, not check correctness. |
| **Aryn Sycamore** | `aryn-ai/sycamore` | — | — | **Apache-2.0** (partitioner + models, **S**) | — | Document segmentation/OCR/table extraction. **L0/L2 only.** | Not a validation loop at all. Belongs in the L2 lane, not here. |
| **Semantic Integrity Constraints** | Brown, arXiv:2503.00600v3 (7 Aug 2025) | — | — | — | — | **A declarative abstraction for correctness conditions over LLM outputs**: constraint types **grounding, soundness, exclusion**; **reactive and proactive enforcement**; constraint pushdown in the optimiser; and — the useful bit — *"the reliability of a constraint's implementation is defined as the precision and recall of detecting a violation. **A deterministic constraint is completely reliable (100% precision and recall) and requires no estimation**, while a stochastic [one]..."* with an **observability interface that displays the precision and recall of each constraint**. **V** | It is a **vision paper** — no benchmark, no code released that I found. But its vocabulary is *exactly* the brief's predicate-library screen, published a year earlier by a database group. **Cite it; do not claim novelty for "display each check's error rate" without it.** |

---

## PART 11 — WHAT TO PRE-REGISTER FOR EXPERIMENT 9.1

### 11.1 Build the reference class honestly

Per-unit success rate, where "unit" is the thing you get 10 of and "success" is closest to "survives an L4-shaped gate":

| Study | Unit | n | Gate | Rate | Warrant |
|---|---|---:|---|---:|---|
| nl2postcond RQ1 | EvalPlus problem (docstring + reference impl) | 164 | ≥1 test-set-correct postcondition @10 | **96%** | V |
| nl2postcond RQ1 | EvalPlus problem | 164 | ≥1 postcondition that kills **all** mutants (GPT-4 base) | **61.6%** | V |
| nl2postcond RQ1 | EvalPlus problem | 164 | **union** of correct postconditions is bug-complete | **62.2%** | V |
| ClassInvGen | C++ class (code available) | 9 | ≥1 invariant kills a mutant the tests missed | **8/9 = 89%** | D from V table |
| SpecGen | program (code + verifier) | 385 | verifiable specification produced | **72.5%** | S |
| AutoSpec | C program (code + Frama-C) | 51 | solved | **60.8%** | S |
| **AssertLLM2 bug-prevention** | **design (spec document only)** | **83** | mutation bug-kill ratio, union of 3 runs, best model | **18.5%** | **V** |
| AssertLLM2 | design | 83 | bug-kill ratio, single run, best model | **11.7%** | V |
| **nl2postcond RQ2** | **real bug (JavaDoc prose + real code)** | **525** | ≥1 bug-discriminating postcondition, union all models/prompts | **12.2%** | **V** |
| nl2postcond RQ2 | real bug | 525 | GPT-4 best single config | **9.0%** | V |
| TOGA (realistic) | mutant | 51,385 | marginal kill over the free baseline | **0.3%** | V |
| NormBench | statutory provision | 2,290 | Edge-F1 (correct override wiring) | **0.215–0.246** | V |

### 11.2 Where our task sits inside that class — the four adjustments, each with its sign

**Pushing our rate UP relative to nl2postcond-RQ2 / AssertLLM2:**
1. **L1 removes the hardest sub-problem.** TOGA's dominant failure is `assertEquals` at **74% FP** — guessing an expected *value*. Our predicates assert *relations among 854 named cells* on a schema induced deterministically from the blank template. We are in nl2postcond's **Arithmetic Equality** category (**bug-completeness 0.82/0.89**), not its **Type Check** category (0.14/0.27). Structurally, our decidable-17 list *is* the strong category.
2. **The mutants are ours.** Like AssertLLM2 and ClassInvGen, we seed the faults into an artefact we control. The Defects4J 12.2% is depressed by real bugs that no docstring mentions; our seeded faults are, by construction, faults in fields the regulation *does* speak to.
3. **Sampling.** Every result above improves 2–4× from @1 to @10/union. SPADE generates **15–106 candidates** per pipeline. Sampling k = 10 per obligation is free.

**Pushing our rate DOWN:**
4. **NormBench, and it is the biggest term.** Statutory prose with provisos gets wired correctly at **Edge-F1 ≈ 0.22**. AssertLLM2's spec documents are engineering documents; the IFSCA FM Regulations are not. And **§4.3's own classification says at most 17/24 = 71% of predicates on this artefact are script-settleable at all** — a *curated* 71%, chosen by someone already looking for checkable things. **10 obligations drawn from the Regulations, not from that curated list, will contain a lower decidable fraction.**

### 11.3 The estimate, decomposed

```
P(obligation survives L4)  =  P(the obligation admits an executable check at all)
                            × P(model writes one that fires | admissible)
                            × P(it is non-degenerate | fires)
                            × P(FFR acceptable on the clean corpus | non-degenerate)
```

| Term | Anchor | Estimate |
|---|---|---|
| admits a check at all | §4.3's 17/24 = 71%, discounted because 9.1 samples obligations, not curated predicates; NormBench proviso risk | **0.50 – 0.65** |
| fires on a seeded fault (k=10, any) | ClassInvGen 8/9; nl2postcond union bug-complete 62.2%; AssertLLM2 union 18.5% per-*bug* but far higher per-*design* | **0.65 – 0.85** |
| non-degenerate | nl2postcond: Type Check is 47.4% prevalent and near-degenerate; SPADE: select-all → 100% FFR; TOGA: NoException gets 68.9% for free | **0.60 – 0.80** |
| FFR acceptable on clean corpus | nl2postcond accept@10 = 0.75 on real code; SPADE baseline 55.6% of candidates individually pass τ=0.25 | **0.70 – 0.90** |
| **Product** | | **0.14 – 0.40, central ≈ 0.25–0.30** |

### 11.4 The arithmetic that kills the current pre-registration

Under the brief's design — **n = 10, delete L3 if fewer than 3 survive** — with X ~ Binomial(10, p):

| True p | P(delete L3) | P(keep L3) |
|---:|---:|---:|
| 0.10 | 0.930 | 0.070 |
| **0.15** | **0.820** | **0.180** |
| 0.20 | 0.678 | 0.322 |
| 0.25 | 0.526 | 0.474 |
| **0.30** | **0.383** | 0.617 |
| **0.35** | **0.262** | 0.738 |
| 0.50 | 0.055 | 0.945 |

(Computed by me, exact binomial, **D**.)

**Two failures, both large:**
- If L3 genuinely works at p = 0.35 — inside my central band — **there is a 26% chance the experiment deletes it.**
- If L3 is broken at p = 0.15 — the AssertLLM2/nl2postcond-RQ2 band — **there is an 18% chance the experiment keeps it.**
- A 95% Wilson interval at p̂ = 0.30 with n = 10 is **[0.108, 0.603]** — width 0.495. **The experiment cannot distinguish "one in ten" from "three in five".** It is an afternoon that buys almost nothing, and its cheapness is the entire reason it was specified at 10.

### 11.5 The recommendation — pre-register THIS

> **PRE-REGISTRATION FOR EXPERIMENT 9.1, v2. Written before running.**
>
> **Sampling frame.** **n = 20 obligations**, drawn by a stated rule from the IFSCA (Fund Management) Regulations 2025 as amended to 30 Jan 2026 — e.g. every k-th "shall" clause in Chapters covering scheme operation and reporting — **stratified and labelled in advance into two strata by a rule that does not look at any model output**:
> - **Stratum A — arithmetically closed** (the obligation names quantities, dates, counts, identifiers, or relations among fields present in the FME template's induced schema). Expected ≈ 12 of 20.
> - **Stratum B — judgment-bearing or externally-dependent** (adequacy, appropriateness, truthfulness, satisfaction, or data about entities the FME does not manage). Expected ≈ 8 of 20.
> Stratifying *first* is not a hedge: §2.4 already predicts the two strata behave differently, and a single blended number would hide the only structure we know is there.
>
> **Generation.** For each obligation, **k = 10 candidate predicates per prompt regime**, in **two regimes** — "base" (strong/complex) and "simple" — because nl2postcond measured that the correctness-maximising prompt is *not* the completeness-maximising prompt (p = 0.008, d = 1.73). Report **accept@1, accept@5, accept@10** and the **union**, following AssertLLM2's average-vs-union convention. Log every candidate; the discard pile is data.
>
> **Gate (an obligation "survives" iff at least one of its 20 candidates passes all four):**
> 1. **Executes** on the corpus without error, over keys that exist in the L1-induced schema. *(TOGA's semantic-not-syntactic FP lesson: this gate is nearly free and proves nothing.)*
> 2. **Mutation kill > 0** on non-equivalent seeded mutants — AssertLLM2's exact denominator convention — **AND strictly greater than the free baselines** (below).
> 3. **Non-degenerate:** it is not equivalent to a member of the published degeneracy list (type/null/existence checks — nl2postcond Table 3), and it does not flag > 50% of the clean corpus.
> 4. **FFR ≤ τ on the clean corpus, computed for the SET, not the predicate** — using SPADE's `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`. **τ = 0.10.** *(EvalGen needed τ = 0.40 to find any feasible set on one of two pipelines; if we must raise τ, that raise is itself the result and must be reported, not absorbed.)*
>
> **Three mandatory baselines, each run before the model** — because in this literature the free baseline beats the neural method more often than not:
> - **B0 — the native formulas.** The 38 of 294 formulas that already express a checkable relation (35 SUM + 3 COUNTIF). Free, deterministic, zero model.
> - **B1 — Daikon** on the clean corpus via `convertcsv.pl`, `--conf_limit 0.99`.
> - **B2 — the degenerate arm** (TOGA's `NoException` analogue): "no cell is blank and no cell errors." **If L3 does not beat B0 ∪ B1 ∪ B2 on mutation kill at equal FFR, it has produced nothing**, however many predicates survive.
>
> **Decision rule, pre-registered:**
> - **Stratum A ≥ 6/12 survive AND L3 beats B0∪B1∪B2 on marginal mutation kill → L3 is retained** as a *candidate generator whose output is inadmissible until gated*. Never as an authority.
> - **Stratum A ≤ 3/12 → L3 is deleted for Stratum A** and predicates are hand-authored from the 294 native formulas. The architecture is unaffected.
> - **4 or 5 of 12 → the result is "underpowered"; report the Wilson interval and either extend n or stop. Do not negotiate.**
> - **Stratum B: pre-register the expectation of 0–1 of 8, and pre-register that a Stratum-B survivor is treated as a suspected false positive requiring manual adjudication before it counts.** Per §2.4, a check that appears to settle a judgment obligation is more likely to be a degenerate check than a breakthrough.
>
> **Power, exact binomial (n = 20, threshold ≥ 6):** P(delete | p = 0.15) = **0.933**; P(delete | p = 0.20) = 0.804; P(delete | p = 0.30) = 0.416; P(delete | p = 0.35) = **0.245**. Wilson 95% CI at p̂ = 0.30, n = 20 = **[0.145, 0.519]** (width 0.374). Still not tight — **but the honest report is the interval, not the point estimate**, and the interval is what goes on the slide.
>
> **Whatever happens, report:** the Wilson interval; the per-stratum split; the accept@k curve; the four-gate attrition funnel (how many candidates die at each gate — this is the most reusable artefact of the whole experiment); the marginal kill over each baseline separately; and **the τ actually used.**

**And the sentence to write down now, before the result, because it is the one the standing bias will attack (Part 11 of the brief):**

> The criterion may change only by an argument that the old criterion was wrong. **"We should have sampled better obligations" is not such an argument** — the sampling rule is pre-registered. **"The clean corpus was synthetic" is not such an argument** — that limitation is known in advance and applies symmetrically to the baselines. **"Stratum B was always going to fail" is not such an argument** — that is why it is a separate stratum with its own pre-registered expectation.

### 11.6 The methodology to copy, ranked

1. **nl2postcond's two-metric split** — test-set correctness (necessary) and bug-completeness-score over mutants (sufficient), **plus their audit of the correctness metric's own false-positive rate** (they found 1.1% on 900 hand-checked). We must do the same audit on our clean corpus, and quote its n.
2. **nl2postcond's natural-vs-artificial-bug separation** — they measured that artificial faults *inflate* completeness. Our dirty corpus is entirely artificial. **Every mutation score we quote must carry that word.**
3. **AssertLLM2's four-metric report and average-vs-union convention** — syntax / provability / coverage / bug-kill, reported per-run and unioned. It is the only published protocol that runs a spec-document → assertion pipeline end to end and refuses to collapse to one score.
4. **AssertLLM2's "valid, non-equivalent bugs" denominator** — the operational answer to the brief's equivalent-mutant caveat.
5. **The FSE-2023 exclusion rule** — bugs found by implicit oracles (blank cells, `#REF!`, a file that will not open) **must be subtracted** from L3's score. Our analogue: anything B2 catches.
6. **SPADE's ILP with the FFR sub-additivity bound** — the admission policy for the predicate registry, and the only published treatment of assertion *interaction*.
7. **The degenerate baseline, always** — TOGA's `NoException`, SPADE's select-all. Two of the three demolitions in this lane are demolitions by baseline.
8. **PIT's "strong mutators only" setting** (used by both TOGLL and the FSE-2023 study) — the mutation-operator selection is a knob, and quoting a mutation score without naming the operator set is quoting nothing.

---

## PART 12 — WHAT THIS CHANGES ABOUT THE DESIGN

**1. L3 survives, but it is demoted from "predicate synthesis" to "candidate generation", and the brief should say so in the layer name.** Every measured system in this lane that works, works because a rejector exists (SMT solver → 99.5%; JasperGold → AssertLLM2; test suite → ClassInvGen 77%→100%). Every one that fails, fails because the rejector was absent or fake (TOGA's held-out accuracy; De Jure's LLM judge). **The brief's L4 is the rejector, and it is the actual product.** Rename L3 "candidate predicate proposal" and L4 "admission", and the architecture stops resting on a hypothesis.

**2. SPADE is a paper, not a dependency.** 17★, 1 fork, unlicensed, last push April 2024. Reimplement the ILP (≈40 lines of PuLP/CBC, runtimes measured at 0.1–1.2 s on thousands of variables). Delete "reuse SPADE" from the reusable-assets table and replace it with "reimplement SPADE's ILP + subsumption DAG". Add the FFR two-sided bound to the architecture document as a stated law of the registry.

**3. L4 needs a FOURTH test, and NormBench is why.** Tests 1–3 (fires / non-degenerate / low FFR) cannot detect a predicate that implements a rule **while silently dropping its proviso**. Frontier models ground the right spans (SpanFaith 0.77–0.79) and wire the exception structure wrong (Edge-F1 ≈ 0.22). Our instrument is full of provisos. Proposed **L4 test 0 — scope faithfulness**: every admitted predicate must carry (a) the exact character span of the clause it implements, (b) an explicit enumeration of every proviso, exception and cross-reference in that span, and (c) for each one, either an implementing branch in the code **or** an `UNCHECKED(scope: <proviso text>)` emission. **A predicate that neither implements nor declares a proviso is rejected.** This is cheap (it is a structural check on the pair, not a semantic one), it is exactly SG-DT's "explicit exclusion guards", and it turns the brief's most dangerous silent failure into a coverage line — which is the product's whole thesis applied to itself.

**4. Add Daikon as a first-class, model-free L3 alternative AND as a mandatory baseline.** MIT-equivalent licence, 260★, pushed two days ago, **ships a CSV front end**. It will mine the 35 SUM identities and 181 cross-sheet carries out of a clean corpus for free. It will also emit trivia (ClassInvGen: **27 of 40** correct Daikon invariants were "pointer not null") and spurious relations that survive test validation (**7** in that study). Both facts are useful: the trivia is the degeneracy list, and the spurious ones are a *measured demonstration on our own corpus* that a check whose error rate is unknown must not be admitted — which is the pitch.

**5. The report must show the attrition funnel, not just the coverage fraction.** AssertLLM2's finding that GPT-5.2 and Claude-Sonnet-4.5 differ in *strategy* invisibly under single-metric evaluation is the same finding as the brief's "no green tick". **Screen 3 (predicate library) should show, per obligation: candidates generated → executed → fired → non-degenerate → FFR-admitted.** A 20:1 attrition ratio displayed honestly is a stronger demo than a coverage bar, because no competitor will show it.

**6. Two new prior-art citations are now mandatory, and one novelty claim must be narrowed.** *Semantic Integrity Constraints* (Brown, arXiv:2503.00600v3, Aug 2025) already proposes an **observability interface displaying the precision and recall of each constraint** — the brief's Screen 2/3 in a database paper, a year early. *Confidently Wrong* (arXiv:2607.23386, Jul 2026) already proposes LLM-authors-rules + deterministic-execution and already names the Level-2 gap. **The brief's surviving novelty is narrower and better: (a) statutory text as the criterion source in place of prompt history, (b) mutation testing as the Level-2 gate in place of hand-written SME tests, and (c) the coverage declaration — the UNCHECKED vocabulary and the signed coverage fraction — which nobody in this lane has.** Claim those three and no more.

**7. The synthetic-clean-corpus weakness is worse than §9.2 states, and there is a measured citation for it.** nl2postcond measured that artificial faults inflate completeness relative to natural ones, and that a weaker test suite (HumanEval, 7% metric false positives) makes correctness look better than a stronger one (EvalPlus, 1.1%). **Our clean corpus is both synthetic and small, so it is the HumanEval of our setting.** Mitigation to add to the architecture: hold out a *structurally distinct* slice of the clean corpus (e.g. filings for a scheme type not represented in the fitting slice) and report FFR on the held-out slice separately. Without that, every FFR we print is an upper bound on our own optimism.

**8. Frontier-model drift is a compliance surface, and the attestation layer should absorb it.** *Confidently Wrong* documents a failure cell closing from 96.6% to 100% **under the same model alias with no version bump**. Our L7 already signs the predicate-set version and each predicate's measured error rates. **Add: the model identifier, the date, and the prompt hash used to synthesise each predicate.** Then a re-synthesis under a drifted model is a diff, not a mystery — and the registry's monotone-growth property is preserved by construction rather than by hope.

---

## PART 13 — CORRECTIONS AND CONFIRMATIONS AGAINST THE BRIEF

| Brief claim | Status | Evidence |
|---|---|---|
| SPADE "generates candidate assertions, selects minimal set on coverage + accuracy, filters by FFR, models FFR interaction" | **CONFIRMED** | ILP with Coverage ≥ α, FFR ≤ τ; NP-hard by reduction from set cover; interaction via `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`; subsumption DAG. **V** |
| "14% fewer assertions / 21% fewer false failures across 9 pipelines" | **QUALIFIED** | Both are **percentage-point deltas** (13.6 pp of the candidate pool; 21.3 pp of absolute FFR), not relative reductions. Denominator: **416 candidate assertions across 9 pipelines, α=0.6, τ=0.25**. **D from V table** |
| "in LangSmith, 2,000+ pipelines" | **QUALIFIED** | 2,000+ **runs of a Streamlit app** for custom prompt templates, released Nov 2023, across >10 sectors. **Only 48 runs clicked "download assertions."** I could not verify a live 2026 LangSmith SPADE surface. **V** for the run count |
| "Reuse SPADE" as an implementation dependency | **REFUTED** | `shreyashankar/spade-experiments`: **17★, 1 fork, no licence field, last push 2024-04-07**. Reuse the algorithm, not the repo. **V (GitHub API)** |
| L4 test 2 (degenerate baseline) is a needed precaution | **CONFIRMED, and stronger than stated** | SPADE §4.2: select-all-candidates yields **100% coverage and 100% FFR**. TOGA's `NoException` baseline gets **68.9% of TOGA's bugs at 2× the precision**. Two independent demolitions by degenerate baseline. **V** |
| L4 test 1 (mutation kill) is the right adequacy metric | **CONFIRMED** | It is the metric that overturned TOGA (**+0.3% marginal kill on 51,385 mutants**), established TOGLL (**1,023 unique of 69,793**), scored ClassInvGen (**+11.16% of 1,057 survivors**), and is one of AssertLLM2's four metrics ("valid, **non-equivalent** bugs"). **V** |
| Whether a model can write a correct executable check from a regulation is unmeasured | **CONFIRMED for regulation specifically; REFUTED for the general problem** | The general problem is measured extensively (Parts 4–6, 8). The *regulatory* instance is not: arXiv abstract index returns **0** for mutation-testing ∧ regulatory, **2** total for "false failure rate", **1** for mutation-testing ∧ compliance (not filings). Positive control passed. **V** |
| Pre-register "3 of 10; below that, delete L3" | **REFUTED as designed** | Exact binomial: P(delete \| p=0.35) = **0.262**; P(keep \| p=0.15) = **0.180**; Wilson 95% CI at p̂=0.30, n=10 = **[0.108, 0.603]**. Underpowered in both directions. Replace with the stratified n=20 design in §11.5. **D** |
| Rules-as-code is empty for finance | **CONFIRMED, with a new supporting citation** | NormBench Table 1: *"LegalRuleML and Catala provide richer execution semantics but typically require manual predicate engineering and detach from source."* The field's own diagnosis. **V** |
| §4.4's "clean, confident, well-formed output that was wrong" is the strongest pitch material | **CONFIRMED, and now has a published twin** | TOGA: **96% held-out accuracy → 0.38% precision → +0.3% marginal mutation kill.** Published at ICSE 2022, demolished at ISSTA 2023 and FSE 2023 independently. Use it beside the operator's own two false negatives. **V** |

---

## PART 14 — OPEN QUESTIONS I COULD NOT SETTLE

1. **Is SPADE still a live LangSmith feature in Aug 2026?** LangSmith now documents "custom code evaluators" and auto-run evaluators; I found no page naming SPADE. Answerable in five minutes by anyone with a LangSmith account. Until then the brief should say "2,000+ Streamlit runs (Nov 2023–2024)" and stop.
2. **The BIM 97%/98% F1 rule-interpretation numbers.** ScienceDirect 403'd. Unverified, and per AssertLLM2's lesson the metric class is suspect anyway.
3. **AssertLLM2's FPV `P/T` absolute counts** (e.g. Claude-Sonnet-4.5 average 21/38) look small for 83 designs and may be per-design normalised. I quote the ratios, not the counts, and flag the ambiguity. Also flagged: the prose's "high-20% range" bug-kill claim contradicts Table 4's 18.51% maximum.
4. **DIG's current repo, licence and whether it has a CSV/tabular front end.** Not verified. EVALUATE only.
5. **Does Daikon's `convertcsv.pl` handle ~85 numeric columns and mixed types cleanly, and what does `--conf_limit 0.99` yield on ~40 rows?** This is a one-hour experiment with a definite answer and it is the cheapest thing in the whole queue. **Run it before 9.1** — it sets the baseline that 9.1 must beat.
6. **Is there a maintained third-party SPADE reimplementation?** The paper mentions "an independently-written open-source re-implementation of spade" but the footnote target was not resolvable from the extracted text.
7. **arXiv:2604.20193** (LLM → executable predicates from natural-language safety regulations, ISO 13849) is the closest formulation *by wording* of anything I found. I read only the search-result summary line. **Open it.**
8. **What is the actual decidable fraction of 20 randomly-drawn "shall" clauses from the FM Regulations?** §4.3's 17/24 = 71% is over a *curated* predicate list. The stratification rule in §11.5 needs this number to be estimated first, from a pilot draw of ~10 clauses labelled by the operator with no model involved. **This is the real first afternoon, not 9.1.**

---

## APPENDIX — LOCAL ARTEFACTS

PDFs downloaded and text-extracted during this lane (kept for reproduction):
`/private/tmp/claude-501/-Users-abishaikc-Gift/894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad/papers/` — `spade.pdf/.txt/_raw.txt`, `evalgen.pdf/.txt`, `2109.09262` (TOGA), `2305.17047` (ISSTA'23 critique), `2307.16023` (FSE'23 critique), `2405.03786` (TOGLL), `nl2postcond.pdf/.txt`, `classinvgen.pdf/.txt`, `assertllm2.pdf/.txt`, `2606.08932` (NormBench), `2607.23386` (Confidently Wrong), `2604.02276` (De Jure), `2503.00600` (Semantic Integrity Constraints).

Primary URLs used:
- SPADE PDF: `https://www.vldb.org/pvldb/vol17/p4173-shankar.pdf` · arXiv:2401.03038
- EvalGen: `https://arxiv.org/abs/2404.12272` · doi:10.1145/3654777.3676450
- TOGA: arXiv:2109.09262 · ISSTA'23 critique arXiv:2305.17047 · FSE'23 critique arXiv:2307.16023 · TOGLL arXiv:2405.03786
- nl2postcond: arXiv:2310.01831 · `https://github.com/microsoft/intent-formalization`
- ClassInvGen arXiv:2502.18917 · SpecGen arXiv:2401.08807 · AutoSpec arXiv:2404.00762
- AssertLLM arXiv:2402.00386 · AssertLLM2 arXiv:2605.27472 · `https://github.com/hkust-zhiyao/AssertLLM2`
- NormBench arXiv:2606.08932 · `https://github.com/AlexJJJChen/NormBench`
- De Jure arXiv:2604.02276 · Confidently Wrong arXiv:2607.23386 · SIC arXiv:2503.00600
- Daikon: `https://plse.cs.washington.edu/daikon/` · `https://github.com/codespecs/daikon` · `scripts/convertcsv.pl`
- DocETL `https://github.com/ucbepic/docetl` · LOTUS `https://github.com/lotus-data/lotus` · Palimpzest `https://github.com/mitdbg/palimpzest`
- ObliQA/RIRAG arXiv:2409.05677 · `https://github.com/RegNLP/ObliQADataset`
