# LANE L02 — PAPERS, BENCHMARKS, IDENTIFIERS, NUMBERS AND DENOMINATORS

**Run 10 Aug 2026.** Task: verify the rest of the evidence base. Re-check the four numbered arXiv IDs;
find or declare NOT-FOUND for every named-but-unnumbered claim; report exact numbers with exact
denominators; flag any number the brief states more strongly than its source supports.

**Warrant key used throughout:**
- **VERIFIED-AT-SOURCE** — I opened the primary artifact (arXiv abs page, paper PDF/HTML extracted to
  text on this machine, regulator's own release, the repository itself) and read the number off it.
- **SECONDARY** — a credible source describes it; I did not open the primary.
- **UNVERIFIED** — could not confirm. This is a legitimate answer and appears below several times.
- **DERIVED** — computed by me from source numbers; carries the weakest input's warrant.

**Tooling note.** `Bash` in this session had **no network egress** (`curl` to `export.arxiv.org`
returned empty, twice). All retrieval went through `WebFetch`/`WebSearch`. Where `WebFetch` returned
"binary content" for a PDF, the PDF was written to disk by the harness and I extracted it locally with
`pdftotext -layout` and grepped it myself. **Every "verbatim" quote below marked
VERIFIED-AT-SOURCE was read off a local text extraction or the paper's own HTML, not off a
summarizer.** Local extractions live in
`/private/tmp/claude-501/-Users-abishaikc-Gift/894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad/`
(`finverbench.txt`, `clause.txt`, `taubench.txt`, `tac.txt`, `ccaf.txt`, `nanda.txt`, `krishna.txt`).

---

## 0. THE HEADLINE, BEFORE THE DETAIL

Three things came out of this lane that change what can be said on a slide.

**(1) Five separately-tabulated rows of the brief are one paper.** Brief §3.1 row 1, §3.1 row 3,
§3.2 rows 1, 2 and 3, and Part-1 fact #1 of `ARCHITECTURE.md` all trace to **arXiv:2605.29586
(FinVerBench)** — a **37-page, single-author arXiv preprint**, no institutional affiliation on the
paper, no peer review, **code not released in v1**, whose clean split is **43 instances** and whose
headline 0% FPR carries a **95% Wilson upper bound of 8.2%** *by the paper's own admission*. The
warrant key (ⓐ per row) hides the correlation: those rows do not corroborate each other, they
co-vary perfectly.

**(2) The strongest counter-evidence to the brief's central claim is inside the brief's own best
source, and the brief does not cite it.** In the same table that produces "9 of 14 runs flag ≥95.3%
of 43 clean statements," **Claude Sonnet 4 scores Acc 100.0 / Prec 100.0 / Rec 100.0 / F1 100.0 /
FPR 0.0 on n=105 (43 clean, 62 error)** — under the *same* prompt, on the *same* instances. On the
harder rounded rendering it holds **0% FPR at 79.0% recall**. §2.1 of the brief ("no measured system
can say 'this one is clean'") is refutable in one move by anyone who opens the citation.

**(3) The single most defensible claim in the whole evidence base is the one the brief derives
rather than quotes.** The contract-discrepancy result is **CLAUSE**, and it is *peer-reviewed*
(EACL 2026 Findings). The best F1 in its entire 80-cell binary-detection table is **65.4**; the
CUAD split is **~49.5% positive** (derived, six independent internal-consistency checks agreeing);
a constant "always flag" classifier therefore scores **66.2**. The brief's arithmetic is **correct**.
And a full-text positive control over the camera-ready found **zero** occurrences of "majority
baseline", "constant classifier", "random baseline", "trivial baseline", "always-predict" or
"degenerate". **L4 test 2 has a verified, peer-reviewed exhibit.**

---

## PART A — THE FOUR NUMBERED IDs (re-checked, as instructed)

All four are **real, correctly numbered, correctly titled, and correctly attributed.** Two carry
qualifications the brief does not state.

### A.1 arXiv:2401.03038 — SPADE ✅ CONFIRMED

- **Title (exact):** *SPADE: Synthesizing Data Quality Assertions for Large Language Model Pipelines*
- **Authors:** Shreya Shankar, Haotian Li, Parth Asawa, Madelon Hulsebos, Yiming Lin,
  J.D. Zamfirescu-Pereira, Harrison Chase, Will Fu-Hinthorn, Aditya G. Parameswaran, Eugene Wu
- **Venue:** PVLDB **vol. 17, issue 12, pp. 4173–4186, 2024**. DOI `10.14778/3685800.3685835`.
  Primary PDF: `https://www.vldb.org/pvldb/vol17/p4173-shankar.pdf` — **the filename itself carries
  the page number**, which independently confirms the brief's "PVLDB 17 p.4173".
- **Numbers, from the abstract:** "**14%** reduction in assertions"; "**21%** decrease in false
  failures"; "nine real-world LLM pipelines"; deployed in **LangSmith**; assertions generated for
  "**over 2000 pipelines** across a spectrum of industries."
- **Warrant:** VERIFIED-AT-SOURCE (arXiv abs page + VLDB vol-17 PDF URL + DL listing).
- **Faithfulness:** the brief's §6.1 row is faithful in every number.
- **One unverified sub-claim:** the brief's parenthetical "(UC Berkeley/HKUST/LangChain/Columbia)".
  I did not open the affiliation block. **UNVERIFIED** — plausible from the author list (Shankar and
  Parameswaran = Berkeley, Chase and Fu-Hinthorn = LangChain, Wu = Columbia, Li = HKUST) but I did
  not read it off the page. Do not put it on a slide without one more click.

**Where it fits:** L3 (candidate predicate generation) + L4 test 3 (FFR filtering, and specifically
SPADE's modelling of how FFR *compounds across interacting assertions* — that is the part of L4 that
is hardest to invent and is already published). **Where it stops:** SPADE's criterion source is
*prompt-version history*. The substitution to statutory text + the template's 294 native formulas is
the brief's own stated novelty and remains **unmeasured** (§9.1).

### A.2 arXiv:2406.12045 — τ-bench ✅ CONFIRMED, with a denominator the brief omits

- **Title (exact):** *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*
- **Authors:** Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra).
- **Task counts, read off Table 1 of the paper:** **τ-retail = 115 tasks. τ-airline = 50 tasks.**
- **Verbatim, §1:** "state-of-the-art LMs like gpt-4o achieve low task success rates (pass^1) using
  function calling (**∼61% on τ-retail and ∼35% on τ-airline**). With increasing k, the chance of
  consistently solving a task drops rapidly, to as low as **∼25% for pass^8 on τ-retail** for the
  same model."
- **Verbatim, §5.1:** "Even for the best-performing gpt-4o function calling agent which has a
  **> 60% average task success, pass^8 drops to < 25%**."
- **Warrant:** VERIFIED-AT-SOURCE (`taubench.txt`, lines 22–25, 99–109, 245–250, 397–401).
- **Faithfulness:** the brief's "~60% at k=1 → ~25% at k=8" is **CONFIRMED**. But it must be quoted
  as: **gpt-4o with function calling, τ-retail only, n = 115 tasks.** The airline domain never
  reaches 60% at k=1 (∼35%), so the curve is domain-specific.
- **Bonus datum for the brief's §4.4 self-demonstration:** the paper's own failure audit —
  "We sample 115 gpt-4o FC agent trajectories in τ-retail (1 trial per task), out of which 40 tasks
  have failed (pass^1=65.2%). Upon manual examination of these failures, **4 of them are caused by
  user instruction typo or ambiguity (and then fixed)**." The benchmark authors found 10% of their
  own observed failures were instrument defects. That is the brief's thesis, stated by a benchmark
  author about their own benchmark.

### A.3 arXiv:2102.11378 — Practical Mutation Testing at Scale ✅ CONFIRMED

- **Title (exact, as printed on the arXiv PDF's first page):** *Practical Mutation Testing at Scale:
  A view from Google*. The brief's title is right; the arXiv **abstract page** truncates the
  subtitle, which is why a quick check can look like a mismatch.
- **Authors:** Goran Petrović, Marko Ivanković, Gordon Fraser, René Just.
- **Venue:** IEEE Transactions on Software Engineering, 2021. DOI `10.1109/TSE.2021.3107634`. Also
  listed at `research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/`.
- **Scale numbers from the abstract:** "**over 24,000 developers**", "**more than 1,000 projects**",
  Google context of ~2 billion LoC and 500M+ tests/day.
- **Warrant:** VERIFIED-AT-SOURCE (arXiv abs + arXiv PDF title line + IEEE/ACM DOI listing).
- **Where it fits:** L4 test 1. It is the production-scale precedent for mutation score as an
  adequacy metric, and — more usefully for us — for the three tricks that make it affordable:
  mutate only changed code, filter irrelevant mutants, select operators by historical performance.
  **Where it stops:** the equivalent-mutant problem is not solved by it; the brief already carries
  that caveat correctly, and `MS = |killed| / (|mutants| − |equivalent|)` remains uncomputable in
  general because `|equivalent|` is undecidable. Our L4 must therefore report mutation score
  **with the seeded-mutant catalogue attached**, not as a bare percentage.

### A.4 arXiv:2202.01602 — The Disagreement Problem ✅ CONFIRMED VERBATIM

- **Title (exact):** *The Disagreement Problem in Explainable Machine Learning: A Practitioner's
  Perspective*
- **Authors:** Satyapriya Krishna, Tessa Han, Alex Gu, Steven Wu, Shahin Jabbari, Himabindu Lakkaraju.
- **Venue:** **Published in Transactions on Machine Learning Research (06/2024)** — the running
  header on the PDF. So this is peer-reviewed, not just a preprint. The brief marks it ⓞ; correct.
- **The load-bearing sentence, verbatim (`krishna.txt` line 259):**
  > "**24 out of 25 participants (96%) opine that feature importance values output by different
  > explanation methods are not directly comparable.**"
- **Warrant:** VERIFIED-AT-SOURCE. The brief's "24 of 25 practitioners said feature-importance
  values are not directly comparable" is **word-for-word correct**.
- **Denominator detail the brief flattens (worth knowing, not worth fixing):** there are **two
  separate cohorts of 25**. Semi-structured interviews with 25 data scientists (§3.1), and an online
  user study with **another set of 25** (§5), of whom **12 (48%) also took part in the interviews**.
  The 24/25 figure is from the *interview* cohort. Other interview figures: 88% almost always use
  explanation methods; 84% have run into disagreement; 84% cite differing top-feature sets;
  72% ordering; 76% direction; 64% relative ordering.
- **Where it fits:** it is the reason the credit-explainability lane is `incentive` not
  `verification`, and it is the reason **L7 must attest to the predicate set and its measured error
  rates rather than to an explanation**. Post-hoc attributions are not a substrate you can sign over.

---

## PART B — THE NAMED-BUT-UNNUMBERED CLAIMS

Every one of them is **real**. None is NOT-FOUND. Several are stated more strongly than their source
supports; those are marked ⚠.

---

### B.1 "9 of 14 complete frontier-model runs raise an error on ≥95.3% of 43 CLEAN financial statements"

**FOUND. This and four other brief rows are the same paper.**

- **Identifier:** **arXiv:2605.29586**
- **Title:** *FinVerBench: Benchmark Validity and Calibration in Large Language Model Financial
  Statement Verification*
- **Author:** **Silu Panda** — *single author*. Contact is a gmail address; **no institutional
  affiliation appears on the paper**. (GitHub profile `SiluPanda` describes a CS graduate of
  IIT Bombay — **SECONDARY**, and not on the paper.)
- **Submitted:** 28 May 2026. 37 pages, 9 figures. cs.AI. **arXiv preprint, not peer-reviewed.**
- **Code/data:** the paper says the artifacts "are publicly available at the repository URL specified
  in the **camera-ready**" — i.e. **not released in v1**. Treat as unavailable today.

**Corpus construction (VERIFIED-AT-SOURCE, `finverbench.txt`):**
- Built from **SEC 10-K XBRL filings for 43 S&P 500 companies**.
- Four-category, twelve-subtype error taxonomy (arithmetic AE, cross-statement linkage CL,
  year-over-year YoY, magnitude MR).
- Full corpus: 1,866-instance observable set (**43 clean and 1,823 observable errors**); rule-verifier
  table evaluated over **1,942** injected errors.
- **The LLM comparison uses a 105-instance observable diagnostic subset: 43 clean, 62
  error-injected** (from an attempted 108, minus 3 relabelled *not-enough-information*).

**Definition of "clean" (VERIFIED-AT-SOURCE):** clean instances are the *unperturbed* rendered
statements; "**All 43 clean instances satisfy these**" [the checked identities], and the rule
verifier "checks **15 accounting relationships that are guaranteed consistent in our clean data by
construction** (e.g., Assets = Liabilities + Equity, IS net income = CFS net income)." **This
matters — see B.4.**

**The 9-of-14 sentence, verbatim (Finding 1, §5.6):**
> "Claude Sonnet 4 correctly identifies all 62 observable injected errors and produces no false
> alarms on the 43 clean instances. At the opposite extreme, **seven complete runs — GPT-5.5,
> GPT-5.4, GPT-5.2, Claude Opus 4.6, Claude Sonnet 4.6, DeepSeek V3.2, and MiniMax M2.5 — flag every
> clean instance as erroneous. GPT-4.1 and DeepSeek R1 are only slightly less extreme, each
> misclassifying 41 of 43 clean examples (95.3% FPR).** Between these poles, Gemma 3 27B, Llama 4
> Maverick, Qwen 3 235B, and Llama 4 Scout occupy progressively less selective operating points,
> with false positive rates of **20.9%, 51.2%, 74.4%, and 83.7%**, respectively. Thus **nine of
> fourteen complete LLM runs** exhibit severe error-detection bias under this prompt."

**Model list (all 14 complete runs):** Claude Sonnet 4, Claude Opus 4.6, Claude Sonnet 4.6, GPT-4.1,
GPT-5.5, GPT-5.4, GPT-5.2, DeepSeek R1, DeepSeek V3.2, Qwen 3 235B, Llama 4 Maverick, Llama 4 Scout,
Gemma 3 27B, MiniMax M2.5. One **incomplete Gemini 2.5 Pro** run excluded (40/108 gateway failures).

**Table 6 in full (n = 105 for every row; 43 clean + 62 observable errors), VERIFIED-AT-SOURCE:**

| System | Acc | Prec | Rec | F1 | **FPR** |
|---|---:|---:|---:|---:|---:|
| Rule-based (τ = 0.01%) | 71.4 | 100.0 | 51.6 | 68.1 | **0.0** |
| **Claude Sonnet 4** | **100.0** | **100.0** | **100.0** | **100.0** | **0.0** |
| Gemma 3 27B | 61.9 | 77.5 | 50.0 | 60.8 | 20.9 |
| Qwen 3 235B | 65.7 | 64.4 | 93.5 | 76.3 | 74.4 |
| GPT-4.1 | 61.0 | 60.2 | 100.0 | 75.2 | 95.3 |
| GPT-5.5 / 5.4 / 5.2 (Codex CLI) | 59.0 | 59.0 | 100.0 | 74.3 | **100.0** |
| DeepSeek R1 | 60.0 | 59.8 | 98.4 | 74.4 | 95.3 |
| Claude Opus 4.6 | 59.0 | 59.0 | 100.0 | 74.3 | **100.0** |
| Claude Sonnet 4.6 | 59.0 | 59.0 | 100.0 | 74.3 | **100.0** |
| DeepSeek V3.2 | 59.0 | 59.0 | 100.0 | 74.3 | **100.0** |
| Llama 4 Maverick | 59.0 | 65.1 | 66.1 | 65.6 | 51.2 |
| Llama 4 Scout | 58.1 | 60.0 | 87.1 | 71.1 | 83.7 |
| MiniMax M2.5 | 59.0 | 59.0 | 100.0 | 74.3 | **100.0** |

**Verdict on the brief's phrasing: CONFIRMED, and faithfully worded.** "≥95.3% of 43 clean" is
exactly right (7 runs at 43/43, 2 runs at 41/43 = 95.3%).

**⚠ What must be added when it is quoted:**
1. **n = 43 clean.** The paper itself: "an observed **0% FPR over 43 clean instances has a 95%
   Wilson upper bound of 8.2%**." Every FPR figure here — including the 0% one — is a 43-denominator
   estimate.
2. **The paper does not claim these FPRs are prompt-invariant**, verbatim: "**We therefore do not
   claim that the observed FPRs are prompt-invariant.**"
3. **The paper's own framing is calibration, not incapacity:** "the key observed challenge is not
   error detection per se (**twelve of fourteen complete runs achieve ≥87% recall**) but
   calibration". And: "**Claude Sonnet 4's 0% observed false positive rate demonstrates that this
   calibration is achievable on the current sample.**"
4. **Construct-validity caveat, the author's own:** "Our benchmark injects **single, isolated errors**
   via random perturbation. Real financial misstatements often involve multiple coordinated errors…
   Our single-error design **simplifies the task** relative to real-world fraud detection and **may
   overestimate practical verification capability**." And the statements are "presented as
   **formatted text rather than the complex layouts (PDFs with tables, footnotes, charts) used in
   actual filings**."
5. **Contamination:** "All evaluated models are trained on large internet corpora that likely include
   SEC filings… we cannot definitively distinguish memorization from reasoning."

**Where this fits:** L4 (this is the FFR-on-clean-corpus measurement, done by someone else, on a real
artifact class). **Where it stops:** 43 clean instances, single-injected errors, plain-text
rendering, no released code, one author, no peer review, and a counter-example inside the table.

---

### B.2 The contract-discrepancy benchmark — F1 65.4, ~49.5% positive, no constant baseline

**FOUND, and it is peer-reviewed — the strongest single item in the whole evidence base.**

- **Identifier:** **arXiv:2511.00340** (v1 1 Nov 2025, v2 7 Jan 2026), *also* published as
  **ACL Anthology `2026.findings-eacl.305`** — **EACL 2026 Findings, peer-reviewed.**
- **Title:** *Better Call CLAUSE: A Discrepancy Benchmark for Auditing LLMs Legal Reasoning
  Capabilities*
- **Authors:** Manan Roy Choudhury, Adithya Chandramouli, Mannan Anand, Vivek Gupta.
- **Corpus:** "over **7500** real-world perturbed contracts" built from **CUAD** and **ContractNLI**,
  **10 anomaly categories**, RAG-validated against statutes.
- **Models evaluated — and this is a material qualification the brief omits: only FOUR, and none is
  a frontier model.** GPT-4o-**mini**, Gemini **2.0 Flash**, Gemini **2.5 Flash**, LLaMa 3.3 70B
  Instruct. No GPT-5.x, no Claude, no Gemini Pro.

**The 65.4 (VERIFIED-AT-SOURCE, Table 3, `clause.txt` line 309):** Gemini-2.5 Flash, CUAD split,
category `Omission_inText`:

| | Acc | Pre | Rec | **F1** |
|---|---:|---:|---:|---:|
| Gemini-2.5, CUAD, Omission_inText | 49.8 | **49.6** | **95.8** | **65.4** |

I checked every cell of Table 3 (4 models × 10 categories × 2 datasets = 80 F1 values). **65.4 is
the maximum.** Nearest competitors: 64.6 (Gemini-2.0, CUAD StrFlaw_inText), 64.2, 63.8×several.
So "**best contract-discrepancy model F1 65.4**" is **CONFIRMED as the maximum measured cell**,
with the caveat that Table 3 is a *per-category* binary task, not one pooled F1.

**The class balance — DERIVED, and it replicates.** The paper never states prevalence. I recovered it
from the internal consistency of each (Acc, Prec, Rec) triple:

```
Given precision P, recall R, accuracy A on a binary set with positive prevalence p:
    TP/N = R·p          FP/N = R·p·(1/P − 1)          FN/N = p·(1−R)
    A = R·p + (1 − p) − R·p·(1/P − 1)
  ⇒ p = (A − 1) / ( R − 1 − R·(1/P − 1) )
```

Applied to six independent CUAD rows spanning all four models:

| Row | F1 recomputed from P,R | **implied prevalence** | constant-positive F1 |
|---|---:|---:|---:|
| GPT-4o-mini · Amb_Legal | 41.3 (paper: 41.2) | **49.5%** | 66.2 |
| Gemini-2.0 · Amb_Legal | 60.8 (paper: 60.8) | **49.4%** | 66.1 |
| Gemini-2.5 · Amb_Legal | 63.6 (paper: 63.7) | **49.5%** | 66.2 |
| **Gemini-2.5 · Omis_inText** | **65.4** (paper: 65.4) | **49.4%** | **66.2** |
| Gemini-2.0 · StrFlaw_inText | 64.6 (paper: 64.6) | **49.7%** | 66.4 |
| LLaMa-3.3 · Amb_inText | 54.6 (paper: 54.7) | **49.5%** | 66.2 |

Six rows, four different models, three different categories, all landing at **49.4–49.7%**. That is
not a coincidence; the CUAD binary splits are ~half positive by construction (each perturbed contract
paired against its original). **The brief's "~49.5%-positive set" is CONFIRMED (DERIVED, but with a
six-way internal replication).**

**The arithmetic the task asked me to adjudicate — IT IS RIGHT.**

```
constant-positive classifier on a p-positive set:
    precision = p,  recall = 1.0
    F1 = 2·p·1 / (p + 1) = 2p/(1+p)
  p = 0.495  →  F1 = 0.99 / 1.495 = 0.66221  =  66.2
```

| p | precision | recall | **F1** |
|---:|---:|---:|---:|
| 0.494 | 49.4 | 100 | **66.13** |
| **0.495** | **49.5** | **100** | **66.22** |
| 0.496 | 49.6 | 100 | 66.31 |
| 0.500 | 50.0 | 100 | 66.67 |

**`2 × 0.495 / 1.495 = 0.662` is correct.** And **65.4 < 66.2**: the best measured cell in the paper
sits **0.8 F1 points below a classifier that returns "discrepancy" unconditionally.**

**Positive control on the absence — declared coverage.** Corpus searched: the **complete
`pdftotext -layout` extraction of the ACL Anthology camera-ready PDF (`2026.findings-eacl.305`),
2,466 lines**, i.e. the whole paper including appendices. Not a search box — the text itself.
- `grep -ci "baseline"` → **4 hits**, all of the form "the baseline performance of current LLMs",
  "a powerful baseline", "crucial baseline for the out-of-the-box reasoning" — i.e. *the LLMs are the
  baseline*.
- `grep -iE "majority (class|baseline)|random baseline|trivial baseline|constant (classifier|baseline)|always[- ]predict|all-positive|degenerate"` → **zero hits.**

**"No constant baseline appears in the paper" is CONFIRMED with a declared corpus.**

**The paper saw the shape and did not compute the floor** — verbatim §5.1:
> "Gemini-2.5's top performance is driven by a distinct **high-recall (90%+), low-precision
> strategy**, whereas other models exhibit a more balanced profile."

They named the degenerate behaviour and reported it as leadership.

**⚠ Two restrictions the brief must add:**
1. **The result holds on CUAD, not on ContractNLI.** I ran the same derivation on the NLI rows:
   implied prevalence **28.6–33.8%**, so the constant-positive floor there is **44.4–50.5**, and the
   best NLI cell is **55.8** — *above* the floor. Say "on the ~49.5%-positive CUAD split."
2. **"Best model" means best of four small/fast models.** No frontier model was evaluated. The
   result is "the best of GPT-4o-mini / Gemini 2.0 Flash / Gemini 2.5 Flash / LLaMa-3.3-70B", not
   "the state of the art."

**Where this fits:** **L4 test 2 — this is the exhibit.** It is a peer-reviewed benchmark where the
published leader is below a one-line classifier and nobody computed the one line.
**Where it stops:** it is contracts, not financial returns; and the degenerate-baseline check is
trivial to *run* — the intellectual work is in making it a **gate** (nothing admitted without it),
which is L4's job, not CLAUSE's.

---

### B.3 "FinVerBench — rule verifier, 0% false alarms, misses 47%"

**FOUND — same paper as B.1 (arXiv:2605.29586).** CONFIRMED, with a circularity the brief must carry.

**Table 4, verbatim (full corpus, 1,942 injected errors):**

| τ | Acc | Prec | **Recall** | F1 | **FPR** |
|---:|---:|---:|---:|---:|---:|
| **0.01%** | 53.8 | 100.0 | **52.8** | 69.1 | **0.0** |
| 0.1% | 53.5 | 100.0 | 52.5 | 68.8 | 0.0 |
| 1.0% | 40.0 | 100.0 | 38.6 | 55.7 | 0.0 |
| 5.0% | 23.2 | 100.0 | 21.5 | 35.4 | 0.0 |
| 10.0% | 14.9 | 100.0 | 13.0 | 23.0 | 0.0 |
| 20.0% | 5.8 | 100.0 | 3.7 | 7.1 | 0.0 |

Verbatim §5.1: "even at the tightest threshold (τ = 0.01%), recall is only **52.8%** — meaning
**47% of injected errors go entirely undetected**."

By category at τ=0.01% (Table 5): **cross-statement linkage 100.0% (738/738)**, arithmetic **31.0%
(160/516)**, magnitude **32.0% (55/172)**, year-over-year **14.2% (73/516)**. Overall
**1,026 / 1,942 = 52.8%**. Localization accuracy among detected errors: **62.6%**.

**⚠ The 0% FPR is TRUE BY CONSTRUCTION and the brief does not say so.** Verbatim: the verifier
"achieves perfect precision (0% FPR) at all thresholds **when restricted to relationships that hold
exactly in the clean data**", and those relationships "are **guaranteed consistent in our clean data
by construction**." The clean corpus was generated so that the 15 checked identities hold. That is
precisely the failure L4 test 3 exists to catch: an FFR measured against a corpus built to satisfy
the predicate. **On real filings the same 15 rules would fire on rounding, restatements, unmapped
line items and taxonomy drift, and the FPR would not be 0.**

The paper is honest about the mechanism elsewhere — §6.1: "simplified summation relationships
(e.g., 'capital expenditures = cash from investing') can **diverge by over 1,000% from reality**
because of unmodeled components (acquisitions, divestitures, investment sales). Any verifier —
rule-based or LLM — must reason about what it cannot see."

**Design consequence:** L4 must record, per predicate, a boolean
`clean_corpus_independent_of_predicate`. An FFR measured on a corpus generated to satisfy the
predicate is not an FFR; it is a tautology, and it must not be printed next to a real one.

**Where it fits:** L4 test 3 + L5 (the "verification gap" the paper names is exactly our
UNCHECKED(reason) vocabulary — *no oracle exists* / *rule ambiguous*). **Where it stops:** 15
hand-written rules, one XBRL taxonomy, synthetic single errors, no released code.

---

### B.4 "Add a checklist → 100% FPR"  ⚠ QUALIFIED

**Same paper (arXiv:2605.29586).** The number exists; the causal reading does not survive.

- **7 of 14** complete runs sit at exactly **100.0% FPR** under the guided-checklist prompt.
  9 of 14 sit at **≥95.3%**.
- **Under the same checklist prompt, Claude Sonnet 4 sits at 0.0% FPR with 100.0% recall.** And the
  rule-based verifier is also at 0.0%. So the checklist does not *cause* 100% FPR; it fails to
  suppress it in most models.
- The paper's own mechanism (Finding 4, verbatim): "the checklist includes **simplified subtotal
  relationships** and can encourage models to treat **omitted line items as evidence of
  inconsistency**… false positives are usually **arithmetically correct but semantically
  miscalibrated**."
- And, verbatim: "**We therefore do not claim that the observed FPRs are prompt-invariant.**"
- Single-model prompt ablation only: MiniMax reproduced 100% FPR under zero-shot and few-shot as
  well — "but this single-model result does not substitute for a cross-model prompt ablation."

**Restatement that survives:** *A guided checklist of simplified subtotal relations drove 7 of 14
frontier runs to flag 43 of 43 clean statements — because an incomplete checklist teaches the model
to read omissions as inconsistencies. One run out of fourteen was calibrated under the same prompt.*

That restatement is **more useful to us**, not less: it says the failure is a *specification*
failure (the checklist under-specifies what is not visible), which is exactly what L1's induced
schema + L5's `UNCHECKED(requires counterparty data)` is for.

---

### B.5 "Deterministic rules → 0% FPR at 53% recall"

**CONFIRMED numerically** (52.8% recall at τ=0.01% over 1,942 injected errors; 51.6% recall on the
105-instance observable subset). **Same paper.** See B.3 for the by-construction caveat, which is the
whole story. Brief's "53%" rounds 52.8% — fine.

---

### B.6 "Rounding tolerance → 21-point recall loss, exactly the price of the FP suppression"  ⚠ REFUTED as framed

**Same paper. The number is exactly right. The causal story is contradicted by the source.**

**Table 11, verbatim** (Claude Sonnet 4, the same 105-instance observable subset):

| Condition | Acc | **Prec** | **Rec** | F1 | **FPR** |
|---|---:|---:|---:|---:|---:|
| Rounded realistic rendering | 87.6 | **100.0** | **79.0** | 88.3 | **0.0** |
| Unrounded diagnostic rendering | 100.0 | **100.0** | **100.0** | 100.0 | **0.0** |
| **Δ (rounded − unrounded)** | −12.4 | **0.0** | **−21.0** | −11.7 | **0.0** |

**Precision is unchanged at 100.0. FPR is unchanged at 0.0.** Nothing was traded. Verbatim §6.5:
"recall drops from 100.0% to 79.0% (−21.0pp), confirming that **decimal-format artifacts substantially
inflate detection rates** in the unrounded diagnostic rendering. Second, **precision remains at 100%
and FPR at 0%: the main effect of rounding is on recall rather than specificity for this model.**"

**What actually happened:** the error injector perturbed raw values, producing figures like
`$534.66M` inside statements otherwise reported in whole millions. The model was partly detecting
*the decimal anomaly*, not the accounting error. Rounding the injected values to reporting precision
removed that tell. This is a **benchmark-rendering artifact**, not a tolerance knob and not a
precision/recall tradeoff.

**⚠ The brief's row must be deleted or restated.** "Allow rounding tolerance → the recall loss is
exactly the price of the FP suppression" asserts a tradeoff the source explicitly denies. An
adversarial reader with Table 11 open ends that row in ten seconds.

**But it converts into something better — a free L6 relation with a published effect size.**
Re-render the same artifact at its declared reporting precision and re-run every predicate. Any
verdict that changes is **presentation-sensitive**, and the measured magnitude of that sensitivity in
the one published instance is **21 recall points on n=105**. That is a metamorphic relation
(*presentation-precision invariance*) with prior art, before we author a single line.

Model-dependence, verbatim: "Qwen drops from 93.5% to 83.9% recall with unchanged 74.4% FPR…
while Llama 4 Maverick remains at 66.1% recall and 51.2% FPR."

---

### B.7 "FinBalance — ledger feedback WORSENED inconsistency detection by 13–52pp"

**FOUND. CONFIRMED — and materially incomplete as stated.** ⚠

- **Identifier:** **arXiv:2606.15949**, submitted **14 Jun 2026**.
- **Title:** *FinBalance: A Multi-Document Accounting Reconciliation Benchmark*
- **Authors:** Sasank Tumpati, Devansh Agarwal, Ayush Kedia, Arjun Neekhra, Murari Mandal,
  Krishna Garg, Yash Sinha, Suman Gupta, Dhruv Kumar (BITS Pilani, KIIT Bhubaneswar, Oxford).
- **Warrant:** SECONDARY-to-VERIFIED — retrieved from the arXiv HTML via WebFetch; I did not extract
  the PDF locally. Numbers below are as returned from the HTML.
- **Denominators:** **710-record evaluation split** (480 standard + 230 forced-inconsistency);
  **6 models** — Gemini 3 Flash, GPT-5, Claude Haiku 4.5, Grok-4.3, DeepSeek Chat, Qwen 3 235B;
  eight industries, three period types, five difficulty levels; 23 inconsistency-code labels emitted
  by a **deterministic generator**.
- **Ceiling:** "six contemporary LLMs reach **at most 46% exact final-balance-sheet accuracy**."
  Four models show a **26–41pp gap** between the balance sheet they report and the one obtained by
  replaying their own journal entries through the ledger. *(That gap is itself a beautiful
  false-success measurement — the model's stated answer disagrees with its own work.)*
- **The 13–52pp:** "Gemini 3 Flash loses **−13 pp (not significant)**, while Qwen 3 235B loses
  **−17 pp** and Claude Haiku 4.5 loses **−52 pp**."

**⚠ Two things the brief drops:**
1. **The −13pp is explicitly not statistically significant.** Quoting the range as "13–52pp" gives a
   non-significant point the same standing as a −52pp one.
2. **The same intervention improved the primary metric by +30 to +33pp.** Ledger feedback
   substantially raised reported balance-sheet accuracy while costing inconsistency-code detection.
   That is a **trade-off**, not a "worsening" — and the trade-off has the *same sign* as AUDITFLOW's
   result (deterministic structure helps the main task), which **weakens §9.4's "three papers
   disagree" framing**. See §9.4 restatement in "What this changes."
3. Only **3 of 6** models are named with a delta.

**Where it fits:** **L4 / §9.2 clean-corpus generation — this is the most directly reusable asset in
the lane.** FinBalance ships *a deterministic generator whose ledger produces journal entries,
balance sheets and 23 inconsistency-code labels* from human-authored scenarios. That is exactly the
machinery §9.2 says we must build (mutation generates the dirty half; the clean half must be
constructed). **Where it stops:** US-GAAP-shaped accounting reconciliation, not an IFSCA prescribed
workbook; and licence/availability unverified.

---

### B.8 "AgentAbstain — 59.5% paired accuracy, 263 pairs, 42 environments, 17 models"

**FOUND. CONFIRMED exactly. But the second half of that brief row belongs to a different paper.** ⚠

- **Identifier:** **arXiv:2607.10059** (v1, **11 Jul 2026**). Project site `agentabstain.github.io`.
- **Title:** *AgentAbstain: Do LLM Agents Know When Not to Act?*
- **Authors:** Xun Liu, Yi Evie Zhang, Vira Kasprova, Parisa Rabbani, Pardis Sadat Zahraei,
  Tianyu Zhang, Ali Ebrahimpour-Boroojeny, Varun Chandrasekaran — **University of Illinois
  Urbana-Champaign**. **Preprint**, no venue stated.
- **Denominators:** **263 paired tasks (526 individual tasks)**, **42 executable sandbox
  environments**, **17 frontier models**, **4 agent harnesses**, 8 abstention scenarios.
- **Verbatim:** "the best model (**Gemini 3.1 Pro**) achieves only **59.5% paired accuracy**."
  Project page: "**No model clears 60%**"; the act–abstain gap is **mean act accuracy 80.6% vs
  abstain 59.1%**; "Capability isn't restraint."
- **Warrant:** VERIFIED-AT-SOURCE (paper HTML + project page).
- **Faithfulness:** all four numbers in the brief are **CONFIRMED**.

**⚠ "Reasoning fine-tuning makes abstention 24% worse" is NOT in AgentAbstain.** Positive control:
I asked for every mention of reasoning fine-tuning / reasoning-tuned models / thinking modes / any
24% figure across (a) the full paper HTML `arxiv.org/html/2607.10059v1` and (b) the project page
`agentabstain.github.io`. **Zero occurrences in both.**

---

### B.9 "Reasoning fine-tuning makes abstention 24% worse" — the real source

**FOUND — it is a different paper, and the brief never names it.**

- **Identifier:** **arXiv:2506.09038**
- **Title:** *AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions*
- **Authors:** Polina Kirichenko, Mark Ibrahim, Kamalika Chaudhuri, Samuel J. Bell (Meta / FAIR).
  Submitted **10 Jun 2025**. Also on OpenReview.
- **Abstract, verbatim:** "we introduce AbstentionBench, a large-scale benchmark for holistically
  evaluating abstention across **20 diverse datasets**… **Evaluating 20 frontier LLMs** reveals
  abstention is an unsolved problem, and one where scaling models is of little use… we find that
  **reasoning fine-tuning degrades abstention (by 24% on average)**, even for math and science
  domains on which reasoning models are explicitly trained."
- **Warrant:** VERIFIED-AT-SOURCE.

**⚠ The denominator of the 24% is TWO model pairs, not 20 models.** Body, verbatim:
> "reasoning models **DeepSeek R1 (Distill Llama 70B) and s1** show an **average of 24% drop in
> abstention** compared to their **non-reasoning counterparts**"

i.e. R1-Distill-Llama-70B vs Llama-3.3-70B-Instruct, and s1.1-32B vs Qwen-2.5-32B-Instruct. Two
open-weight distillation pairs. The brief's row implies a *capability trend across the frontier*;
the measurement is two pairs of open-weight models.

**⚠ Relative or absolute? UNRESOLVED.** The paper says "24% drop in abstention" without specifying
whether that is a relative reduction in abstention recall or an absolute percentage-point drop.
I could not settle it from the text I retrieved. **Record it as "24% (paper does not state whether
relative or pp)" — "could not check" is the honest answer here.**

**Where it fits:** L2 abstention. AbstentionBench also supplies the argument *against* relying on a
system prompt: "while a carefully crafted system prompt can boost abstention in practice, it does
not resolve models' fundamental inability to reason about uncertainty." That is a direct citation
for why L2 uses **conformal prediction sets** rather than instructions.
**Where it stops:** QA-shaped unanswerability, not key-binding in a spreadsheet.

---

### B.10 "Adding memory made all 10 models worse at long horizons"  ⚠ REFUTED as stated

- **Identifier:** **arXiv:2603.29231**
- **Title:** *Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents*
- **Authors:** Aaditya Khanal, Yangyang Tao, Junxiu Zhou — **Northern Kentucky University**.
  Submitted **31 Mar 2026**. Preprint.
- **Metric:** **GDS = Graceful Degradation Score** — weighted partial subtask completion,
  `Σᵢ wᵢ·𝟙[subtask sᵢ completed correctly]`, weights summing to 1, range 0–1.
- **The actual finding, verbatim:** "**6 models are hurt, 4 are neutral (within ±0.03 GDS)**." No
  model gained. Largest penalties **Kimi K2.5 (−0.14)** and **Mistral 24B (−0.13)**; the effect is
  concentrated in the mid-capability tier.
- **The 10 models — all open-weight:** Llama 3.1 8B, Mistral Nemo, Mistral Small 3.2, Qwen3 30B,
  Qwen3 32B, Llama 3.3 70B, MiniMax M2.5, GLM-4.5 Air, Kimi K2.5, DeepSeek V3.
- **Warrant:** VERIFIED-AT-SOURCE (paper HTML).

**Two corrections:**
1. **"All 10 worse" is false.** Correct: *the memory scaffold never helped — 6 of 10 were hurt, 4
   were unchanged within ±0.03 GDS.* "Never helps" is still a strong claim and is the one to make.
2. **No frontier model was tested.** The brief uses this row under "the capability trend runs against
   the fix" (§2.3 property 3). Ten open-weight models cannot support a claim about the frontier.

Also: this is **one specific scaffold** (a scratchpad) on **one** benchmark from a small group. It is
sufficient to justify "we did not build a memory loop"; it is not sufficient to assert "memory
degrades agents."

---

### B.11 CMU TheAgentCompany — 175 tasks, best agent 30%, Finance lowest

**FOUND. Numbers CONFIRMED. The "Finance lowest" claim needs its denominator or it will be
challenged.** ⚠

- **Identifier:** **arXiv:2412.14161**; published **NeurIPS 2025 Datasets & Benchmarks Track**
  (proceedings PDF `papers.nips.cc/.../0d744742f6fac4d1134c019b7cef3c8a-Paper-Datasets_and_Benchmarks_Track.pdf`).
- **Warrant:** VERIFIED-AT-SOURCE (NeurIPS PDF extracted locally to `tac.txt`).
- **Denominators:** **175 tasks**; **twelve LLM backbones**; all run in the **OpenHands** harness.
- **Verbatim:** "the best performing model, **Gemini 2.5 Pro** was able to autonomously perform
  **30.3%** of the provided tests to completion, and achieve a score of **39.3%** on our metric that
  provides extra credit for partially completed tasks."

**Per-category task counts:** SWE **69**, PM **28**, DS **14**, Admin **15**, HR **29**,
**Finance 12**, Other **8**.

**Gemini-2.5-Pro by category (Success % / Score %), Table 3:**

| SWE | PM | DS | Admin | HR | **Finance** | Other |
|---:|---:|---:|---:|---:|---:|---:|
| 37.68 / 45.05 | 39.29 / 52.61 | 14.29 / 20.06 | 13.33 / 19.17 | 34.48 / 44.98 | **8.33 / 21.56** | 12.50 / 20.16 |

**⚠ Three qualifications:**
1. **Finance is 12 tasks. 8.33% = exactly 1 task of 12.** The gap between "lowest" (Finance, 8.33%)
   and "second lowest" (Other, 12.50%) is one task.
2. **On the partial-credit Score, Finance is NOT lowest** — 21.56 beats Admin 19.17, DS 20.06 and
   Other 20.16.
3. **The paper's own sentence does not single out Finance**, verbatim: "**DS, Admin, and Finance
   tasks are the lowest**, with many LLMs completing none of the tasks successfully."

**Safe restatement:** *"On CMU's TheAgentCompany (NeurIPS 2025 D&B, 175 tasks), the best agent
completed 30.3% autonomously; the three lowest-scoring role categories were data science,
administration and finance — the best agent finished 1 of the 12 finance tasks."*
That is stronger rhetorically **and** correct.

---

### B.12 Vals AI Finance Agent v2 — 927 questions, 26 models, 58.63% / 47.71% / 34.14%

**FOUND. It is a LIVE LEADERBOARD and the brief's snapshot is already stale.** ⚠

- **Source:** `https://www.vals.ai/benchmarks/fabv2`. Repo `github.com/vals-ai/finance-agent-v2`.
  **Page last-updated stamp: 8/6/2026** — four days before the brief was compiled.
- **CONFIRMED:** **927 expert-reviewed questions** across public / private-validation / held-out-test
  splits. Builds on Finance Agent v1.1 (v1 has its own paper, arXiv:2508.00828).
- **State as of this lane's run (10 Aug 2026):**
  - Top accuracy: **Muse Spark 1.2 at 60.60%** (brief's headline was 58.63%).
  - Strict "all-pass": **Muse Spark 1.2 at 50.88%** (brief's headline was 47.71%).
  - Claude Opus 5: **58.63%** — this is where the brief's number came from; it is now #2-or-lower.
  - Financial Modeling, best model: **34.52%** (brief: 34.14%). Precedents: 36.37%.
- **"26 models": UNVERIFIED.** The page enumerates **at least 16 organisations** (Alibaba, Ant Group,
  Anthropic, DeepSeek, Google, Meta, MiniMax, Mistral, Moonshot, NVIDIA, OpenAI, Poolside, SpaceXAI,
  Thinking Machines, Xiaomi, zAI). I could not confirm a model count of 26 at source.

**⚠ Rule for this citation:** a live leaderboard is a **withdrawn number with a delay fuse**. Either
quote it with an explicit as-of date and the model name — *"Vals AI Finance Agent v2, 927 questions,
as of 6 Aug 2026: best 60.60%, best strict all-pass 50.88%, Financial Modeling ceiling 34.52%"* —
or drop it. The *shape* is the durable claim and it has survived every refresh: **no model clears
51% when every required detail must be correct.** That sentence is what the brief actually needs.

---

### B.13 MIT NANDA GenAI Divide — 60% / 20% / 5% vs 40%

**FOUND. The exhibit is exact. The report's own limitations paragraph destroys the warrant level the
brief assigns it.** ⚠

- **Source:** *The GenAI Divide: State of AI in Business 2025*, MIT Project NANDA. PDF metadata
  author **Aditya Challapally**. Copy read: `cloudelligent.com/wp-content/uploads/2026/02/v0.1_State_of_AI_in_Business_2025_Report.pdf`
  (v0.1; a second identical copy at `mlq.ai`). **Warrant: VERIFIED-AT-SOURCE** — extracted locally to
  `nanda.txt` and read.

**The exhibit, verbatim (p.6):**
> "Exhibit: The steep drop from pilots to production for task-specific GenAI tools reveals the GenAI
> divide
> General-Purpose LLMs / Embedded or Task-Specific GenAI
> **80% … 60% … 50% … 20% … 40% … 5%**
> Investigated / Piloted / Successfully Implemented"

i.e. **General-purpose 80 → 50 → 40; task-specific 60 → 20 → 5.**
**The brief's "60% investigated → 20% piloted → 5% implemented (vs 40% for general-purpose)" is
CONFIRMED exactly.**

Executive summary, verbatim: "**Sixty percent of organizations evaluated such tools, but only 20
percent reached pilot stage and just 5 percent reached production.**"

**⚠ The report disclaims its own numbers, verbatim, immediately above the exhibit:**
> "**Research Limitations: These figures are directionally accurate based on individual interviews
> rather than official company reporting. Sample sizes vary by category, and success definitions may
> differ across organizations.**"

And the definition of the terminal state, verbatim:
> "**Research Note: We define successfully implemented for task-specific GenAI tools as ones users or
> executives have remarked as causing a marked and sustained productivity and/or P&L impact**"

That is a **self-reported impression**, not a measurement. Methodology: "our interviews, surveys, and
analysis of **300 public implementations**" (widely reported as 52 organisational interviews +
153 executives surveyed — **SECONDARY**). Not peer-reviewed; issued as preliminary findings; publicly
disputed on methodology (e.g. Futuriom, Aug 2025, calling for release of underlying data or
retraction). **I found no evidence of formal withdrawal.**

**Verdict:** the number is real and quotable **as an industry survey**, labelled **ASSERTED**, never
MEASURED. In a brief whose first working rule is "label every quantity," carrying a
self-disclaimed interview statistic at the same visual weight as a PCAOB inspection rate is exactly
the failure mode the brief exists to attack.

---

### B.14 Cambridge CCAF 2026 — 628 / 151 / 52% / 23% / 55% / 43% / 53%

**FOUND. All five percentages CONFIRMED VERBATIM. One framing inversion.** ⚠

- **Source:** *The 2026 Global AI in Financial Services Report: Adoption, Impact and Risks*, Cambridge
  Centre for Alternative Finance / Cambridge Judge Business School. PDF
  `jbs.cam.ac.uk/wp-content/uploads/2026/05/ccaf-2026-04-28-global-ai-in-financial-services-report-2.pdf`.
  Published ~28 Apr 2026; fieldwork Oct 2025 – Jan 2026. SSRN abstract 6674099.
  **Warrant: VERIFIED-AT-SOURCE** — extracted locally to `ccaf.txt` (7,910 lines) and grepped.
- **Denominators CONFIRMED:** "**628 respondent**" organisations across "**151 jurisdictions**"
  (lines 97, 219, 498, 614, 7402). Composition — **203 fintechs, 149 financial incumbents, 146 AI
  vendors, 130 central banks and other regulators** (SECONDARY, from the JBS news page; the PDF
  confirms 628 and 151).

**The five figures, verbatim:**

| Brief's claim | Source sentence | Verdict |
|---|---|---|
| 52% report agentic adoption | "agentic AI is already in active adoption among **52% of industry respondents**" | CONFIRMED |
| only 23% at scaling | "**23% of industry respondents are at more mature stages (Scaling or Transforming)** of adopting agentic AI, while 29% remain in piloting" | CONFIRMED |
| 55% find AI value hard to measure | "**55% of industry respondents and 63% of surveyed regulators find it difficult to measure the value of AI deployment, rising to 76% among large financial institutions**" | CONFIRMED — and the **76%** for large FIs is a stronger number the brief omits |
| 43% no change in profitability | "**40% of respondents report increased profitability from AI, while 43% report no change**" | CONFIRMED |
| 53% spend <$100k/yr | "**53% of surveyed industry respondents spend under USD 100,000 annually on AI** yet still report high maturity in GenAI and agentic AI" | CONFIRMED — ⚠ see below |

**⚠ Framing inversion on the 53%.** The report's clause continues "**yet still report high maturity
in GenAI and agentic AI**" — the source presents this as **capital efficiency**, evidence that
maturity is cheap. The brief uses it as evidence of **shallow investment**. Both readings fit the
number; only one is the source's. If a judge opens p.7, the brief looks like it clipped a clause.

**⚠ Denominator note.** "Industry respondents" ≠ 628. Figure 1.6's agentic-maturity panel is
n = 140 traditional FIs + 199 fintechs = **339**. Quote "52% of ~339 surveyed industry respondents",
not "52% of 628."

**Also useful and unused:** fintechs 57% vs traditional FIs 45% on agentic adoption; 81% of industry
expect agentic AI meaningfully achieved by 2030; 69% of industry / 79% of regulators rank **clearer
regulatory guidance** a top priority. That last one is the demand-side sentence for a GIFT City pitch.

---

### B.15 PCAOB 2024 — 20% of inspected Big Four audits

**CONFIRMED at the regulator's own release, with one part downgraded to SECONDARY.**

- **Source:** PCAOB news release, **"PCAOB Posts Report Detailing Significant Improvements Across
  Largest Firms, Alongside Inspection Results In Record Time," 31 March 2025**, `pcaobus.org`.
- **Verbatim:** "The aggregate **Part I.A deficiency rate for the Big Four U.S. firms** … decreased
  to **20% in 2024, from 26% in 2023.**"
- **Warrant:** VERIFIED-AT-SOURCE for **20% (2024) and 26% (2023)**.
- **⚠ SECONDARY:** the brief's "**and 2022**" (i.e. 26% in both 2023 and 2022) was **not** in the
  release I opened. Thomson Reuters and CFO Brew both report 26% for 2022. Label it SECONDARY or
  open the 2022 report before it reaches a slide.
- **⚠ SECONDARY:** the brief's gloss "**lacked sufficient appropriate evidence to support the opinion
  issued**" is the standard PCAOB definition of a Part I.A deficiency, but **it does not appear in
  the release I opened**. The release uses the term "Part I.A deficiency rate" without defining it.
  Cite the definition from the PCAOB staff guidance, not from this release.
- Companion datum: the six global network firms fell **34% → 26%**, −8pp (SECONDARY).

**Why this one matters more than its size suggests:** it is the only number in the brief's §3.4 that
is a *regulator measuring a human control at a declared denominator*. It is the "absent arm"
baseline. Keep it. Get the 2022 figure and the definition from primary sources.

---

### B.16 "One 50-task airline benchmark found to contain 75+ task defects"  ⚠ MISATTRIBUTED

**The defects are real and larger in proportion than the brief implies — but the 75+ figure does not
belong to the airline set.**

- **τ²-bench** (`github.com/sierra-research/tau2-bench`) README headline references **"75+ task
  fixes"**, described verbatim as: "Removed incorrect expected actions, clarified ambiguous
  instructions, fixed impossible constraints, and added missing fallback behaviors **across airline,
  retail, and banking domains**. Based on analysis from **SABER (Cuadron et al., 2025)**."
  → **Three domains, not one.**
- **τ³-bench** (`taubench.com/blog/tau3-task-fixes.html`, Feb 2026, Victor Barres & Ben Shi, Sierra)
  audited **50+ tasks** and reports **"27 airline tasks fixed"** out of the original **50 airline
  tasks**, and **"26 retail tasks fixed"** of **114**.
  → **27 of 50 = 54% of the airline tasks were rewritten.**
- Effect: airline **pass^1 increased by +14.0 to +20.0 points** depending on model after the fixes;
  pass^4 gains up to +22 points.
- Original τ-bench tasks are **frozen**; Sierra points evaluation at τ²/τ³.
- **SECONDARY** (from a search summary, not opened): excluding erroneous/ambiguous tasks roughly
  **doubled average pass rate, 20.8% → 40.0%**. Do not quote until the primary is opened.
- **Warrant:** VERIFIED-AT-SOURCE for the τ³ blog numbers and the τ²-bench README text.

**Safe restatement, and it is a better sentence:** *"When Sierra audited its own airline benchmark
for τ³-bench, 27 of the 50 tasks needed fixing — incorrect expected actions, impossible constraints,
ambiguous instructions — and model pass^1 rose 14–20 points once they were corrected. Half the
benchmark was measuring the instrument."*

---

### B.17 AUDITFLOW (arXiv:2606.03031) — the +64 is not what the brief uses it for ⚠

Not on my assigned list, but it is the sole ⓐ support for §3.2's "wrap in deterministic checks —
**works**", and §9.4 quotes it as "+64pts". It needed opening.

- **Title:** *AUDITFLOW: Executable Symbolic Environments for Structured Financial Reporting
  Verification*. **Submitted 2 Jun 2026.**
- **Authors:** Yan Wang, Xuguang Ai, Jaisal Patel, Xueqing Peng, Fengran Mo, Yupeng Cao, Haohang Li,
  Mingyu Cao, Lingfei Qian, Víctor Gutiérrez-Basulto.
- **Denominator CONFIRMED:** "We evaluate AuditFlow on a **67-instance subset of the FinMR task from
  FinAuditing**." The brief's n=67 is right.
- **Numbers:** **82.09%** joint audit accuracy under **GPT-5.5**; ablation removing deterministic
  checks → **17.91%**; **invalid outputs rise from 1.49% to 35.82%**.
- **The number the brief should be using:** "outperforming the **strongest baseline by 14.93
  points**" — the strongest baseline (Single Agent, GPT-5.5) scores **67.16%**.

**⚠ `82.09 − 17.91 = 64.18` is a SELF-ABLATION of a symbolic-first system, not a demonstration that
adding a symbolic layer beats a strong baseline.** Deleting the verification core of a system whose
architecture *is* the verification core will always produce a large delta; and **a third of the
collapse is malformed output** (invalid outputs 1.49% → 35.82%), so part of the 64 points measures
output validity rather than verification quality. The like-for-like number for "does the symbolic
layer help" is **+14.93 points on n = 67**.

**Where it fits:** L5/L6 — its two-graph symbolic environment (static US-GAAP taxonomy graph ×
dynamic XBRL filing graph, exposed through typed tools) is a working instance of "recompute the
expected value from structured evidence before applying the rule." **Where it stops:** n=67, US-GAAP
XBRL, one LLM (GPT-5.5), preprint.

---

### B.18 False-success detection (arXiv:2606.09863) — CONFIRMED, with an omitted datum that helps us

- **Title:** *From Confident Closing to Silent Failure: Characterizing False Success in LLM Agents*
- **Author:** **Laksh Advani** — single author. **Submitted 1 Jun 2026.** Preprint.
- **Denominators:** **9,876 τ²-bench trajectories from 8 model families**; **1,879 AppWorld
  trajectories from 4 model families** with text-independent ground truth.
- **Verbatim:** "False success is common but varies by setting: **45–48% of failures in single-control
  tau2-bench domains, 3% in dual-control telecom, and 75.8% among AppWorld self-assessing
  coding-agent trajectories** with explicit status claims."
- **Verbatim:** "no configuration across **5 judges, 5 prompt strategies**, and full task
  specifications exceeds **AUROC 0.65** on tau2-bench, and the same judges reach only **0.54 AUROC**
  on AppWorld API-call traces."
- **Verbatim (body):** "**At a 10% flag rate, the detector recovers 72% of false successes
  [95% CI 63–80%], while the strongest judge recovers 13% [8–17%].**"
- **Verbatim:** "Lightweight TF-IDF detectors achieve task-disjoint AUROC **0.83** on tau2-bench and
  **0.95** on AppWorld… **3,300× lower latency**." Precise figures **0.825** and **0.953**; detector
  is **TF-IDF + XGBoost** (logistic-regression variants also evaluated).
- **Warrant:** VERIFIED-AT-SOURCE (abs page + paper HTML).
- **Every number the brief quotes from this paper — 45–48%, 75.8%, AUROC ≤0.65, 13% recall at 10%
  flag rate, 0.825–0.953, 72% recall, 3,300× — is CONFIRMED.** This is the cleanest ⓐ row in the
  brief.

**⚠ One omission, and it argues FOR the architecture:** **3% false success in the dual-control
telecom domain** vs 45–48% single-control — a ~15× reduction. Dual control means a second party can
observe and act on environment state. That is the *measured* version of L5's "a model may never be
the final judge," and the brief currently states it as a principle instead.

**And the labels are the crux, verbatim:** τ²-bench labels came from **regex over closing messages**;
AppWorld labels came from **"a structured database field"** documenting agent status writes,
"**entirely independent of the agent's natural language**." The working detector needed a
programmatic environment oracle — **§2.3 property 4 is confirmed by the primary source, explicitly.**

---

### B.19 Two more §6.1 entries marked ⓞ that do not survive the check

**PASC — arXiv:2605.18812 ⚠ REFUTED on the finance claim.**
- **Actual title:** *PASC: Pipeline-Aware Conformal Prediction with Joint Coverage Guarantees for
  Multi-Stage **NLP and LLM** Pipelines*. Author: **Varun Kotte**, single author, **12 May 2026**.
- **The brief (§6.1, marked ⓞ) says it "names financial documents as a target." It does not.**
  Positive control: I asked for every occurrence of *financial, finance, invoice, document AI, KYC,
  regulatory* across the full paper HTML `arxiv.org/html/2605.18812v1`. **Zero occurrences of any of
  them.** Datasets: **CoNLL-2003** (1,000 calibration / 500 test), **WNUT-17** (500 test),
  **WikiNEuRal** (500 English test). News, Twitter, Wikipedia. No financial data anywhere.
- Its actual numbers: three-stage NER→NED→typing, **96.4%** end-to-end coverage vs **93.4%**
  Bonferroni vs **86.5%** independent CP at identical average set size **1.083**; under shift,
  independent CP **collapses to 59%**; **1.7×** faster than Bonferroni; at **K = 6** stages
  independent CP drops to **0.53**.
- **Verdict:** the *method* is reusable and the joint-coverage argument is exactly right for a
  multi-stage extraction pipeline. The *domain-fit* sentence must be deleted. And note it is a
  single-author preprint, so it is not the kind of citation that carries an ⓞ.

**Entropy Alone is Insufficient — arXiv:2603.21172 ✅ CONFIRMED, slightly over-read.**
- **Title exact:** *Entropy Alone is Insufficient for Safe Selective Prediction in LLMs*.
  Authors: Edward Phillips, Fredrik K. Gustafsson, Sean Wu, Anshul Thakur, David A. Clifton.
  **22 Mar 2026.**
- Finding: "a **model-dependent** failure mode of entropy-based uncertainty methods that leads to
  unreliable abstention behaviour", **fixed** by combining entropy with a correctness-probe signal.
  Benchmarks: **TriviaQA, BioASQ, MedicalQA**; **four model families**.
- The brief says it "**kills** the naive confidence-threshold version of abstention." Slightly strong:
  it kills *entropy-alone*, on QA, and offers a repair. Restate as "entropy alone is insufficient;
  the paper's own fix is entropy + a correctness probe."

**Barr et al. oracle survey ✅ CONFIRMED.** *The Oracle Problem in Software Testing: A Survey*,
Barr, Harman, McMinn, Shahbaz, Yoo — **IEEE TSE, vol. 41, no. 5, pp. 507–525, May 2015**,
DOI `10.1109/TSE.2014.2372785`. Brief's citation exact.

**QuantMind ✅ CONFIRMED with drift.** `github.com/LLMQuant/quant-mind` — **2.3k stars** (brief: 2.3k ✓),
**407 forks** (brief: 405 — normal drift; do not quote fork counts), **MIT** ✓, Python, description
"QuantMind is an agent-native knowledge extraction and retrieval framework for quantitative finance."
README: "Our paper Quant-Mind has been accepted to the **NeurIPS 2025 GenAI in Finance Workshop**",
**arXiv:2509.21507**. Brief's row is accurate. **Where it stops** — unchanged from the brief: its
typed shapes are research artifacts (Papers/News/Earnings/Factors/Theses); extension to a protected
xlsx with merged headers is still **UNVERIFIED** (§9.7).

---

## PART C — CORRECTIONS SUMMARY

| # | Brief's claim | Status | Strongest defensible restatement |
|---|---|---|---|
| 1 | 9/14 runs ≥95.3% FPR on 43 clean | **CONFIRMED** | Add: n=43 clean; 0% FPR has 95% Wilson upper bound 8.2%; the paper does not claim prompt-invariance; **one run (Claude Sonnet 4) scored 0% FPR at 100% recall on the same instances** |
| 2 | Best contract model F1 65.4 vs ≈66.2 flag-everything | **CONFIRMED**; arithmetic **correct** | Restrict to the **~49.5%-positive CUAD split**; "best" = best of **four non-frontier models**; the derived prevalence replicates across six rows |
| 3 | No constant baseline in that paper | **CONFIRMED** (positive control on full EACL camera-ready text; "baseline" ×4, all meaning LLM baseline; zero majority/constant/random/trivial hits) | Keep as is; state the corpus searched |
| 4 | Rule verifier 0% FA / misses 47% | **QUALIFIED** | The 0% FPR is **true by construction** — the 15 rules "are guaranteed consistent in our clean data by construction". Not a measurement of rule precision on real filings |
| 5 | Checklist → 100% FPR | **QUALIFIED** | **7 of 14** runs at exactly 100%; 9 of 14 at ≥95.3%; **one run at 0% under the same prompt**; author explicitly disclaims prompt-invariance |
| 6 | Rounding tolerance → 21pt recall loss = the price of FP suppression | **REFUTED as framed** | −21.0pp recall is **correct**, but **precision stayed 100.0 and FPR stayed 0.0**. It is a rendering artifact, not a tradeoff. Convert it into an **L6 presentation-precision relation** |
| 7 | FinBalance: ledger feedback worsened detection 13–52pp | **CONFIRMED, incomplete** | −13pp is **not significant**; only 3 of 6 models named; the **same feedback improved balance-sheet accuracy +30 to +33pp**. It is a trade-off |
| 8 | AgentAbstain 59.5% / 263 / 42 / 17 | **CONFIRMED** | Add: best = **Gemini 3.1 Pro**; act 80.6% vs abstain 59.1%; UIUC preprint |
| 9 | Reasoning fine-tuning → abstention 24% worse | **CONFIRMED but mis-cited & over-generalised** | Source is **AbstentionBench arXiv:2506.09038 (Meta)**, absent from §6.1. The 24% is over **two open-weight model pairs** (R1-Distill-Llama-70B, s1), **not** 20 models. Relative-vs-pp **UNRESOLVED** |
| 10 | Adding memory made all 10 models worse | **REFUTED** | "The memory scaffold **never helped**: **6 of 10 hurt, 4 neutral within ±0.03 GDS**" — and all ten are **open-weight**, so it cannot support a frontier-trend claim |
| 11 | TheAgentCompany: 175 tasks, 30%, Finance lowest | **CONFIRMED / QUALIFIED** | 30.3% (Gemini-2.5-Pro), 12 model backbones. **Finance = 12 tasks; 8.33% = 1 task.** Paper says "DS, Admin, and Finance are the lowest". Finance is **not** lowest on partial-credit score |
| 12 | Vals AI: 58.63 / 47.71 / 34.14, 927 q, 26 models | **STALE** | 927 questions ✓. As of 6 Aug 2026: top **60.60%**, all-pass **50.88%**, Financial Modeling **34.52%**. **"26 models" UNVERIFIED.** Quote the shape ("no model clears 51% strict"), not the leader |
| 13 | MIT NANDA 60/20/5 vs 40 | **CONFIRMED verbatim** | But the report self-labels: "**directionally accurate based on individual interviews rather than official company reporting**"; "implemented" = executives *remarked* on impact. Label **ASSERTED** |
| 14 | CCAF: 628/151, 52/23/55/43/53 | **CONFIRMED verbatim ×5** | Add **76%** for large FIs; denominator for "industry" is ~339, not 628; the **53% <$100k** clause continues "**yet still report high maturity**" — the source reads it as efficiency |
| 15 | PCAOB 20% (from 26% in 2023 and 2022) | **CONFIRMED (2024, 2023)** | 2022=26% and the "sufficient appropriate evidence" definition are **SECONDARY** — not in the 31 Mar 2025 release |
| 16 | 50-task airline benchmark, 75+ defects | **MISATTRIBUTED** | "75+ task fixes" spans **airline, retail and banking** (τ²-bench). Airline-specific: **27 of 50 tasks fixed** in τ³-bench; pass^1 rose **+14 to +20 points** after fixing |
| 17 | AUDITFLOW +64pts (§9.4) | **MISLEADING** | 64.18 is a **self-ablation** of a symbolic-first system, and **invalid outputs went 1.49% → 35.82%**. Versus the strongest baseline it is **+14.93 points on n=67** |
| 18 | PASC "names financial documents as a target" (marked ⓞ) | **REFUTED** | **Zero** occurrences of financial/finance/invoice/KYC/regulatory in the full paper. Datasets are CoNLL-2003, WNUT-17, WikiNEuRal |
| 19 | SPADE PVLDB 17 p.4173 | **CONFIRMED** | vol. 17, **issue 12, pp. 4173–4186**, 2024. Affiliation parenthetical **UNVERIFIED** |
| 20 | τ-bench ~60% k=1 → ~25% k=8 | **CONFIRMED** | gpt-4o function-calling, **τ-retail only, n=115 tasks**. τ-airline (n=50) never reaches 60% at k=1 (~35%) |
| 21 | Krishna 24/25 practitioners | **CONFIRMED VERBATIM** | Also: published in **TMLR 06/2024**, so peer-reviewed; two separate cohorts of 25 |
| 22 | Practical Mutation Testing at Scale, Google | **CONFIRMED** | arXiv:2102.11378 → IEEE TSE 2021, DOI 10.1109/TSE.2021.3107634; >24,000 developers, >1,000 projects |
| 23 | 45–48% / 75.8% false success; judge ≤0.65; TF-IDF 0.825–0.953, 72% recall, 3,300× | **CONFIRMED entirely** | Add the omitted **3% in dual-control telecom** — it is the measured case *for* deterministic adjudication |

---

## PART D — REUSABLE ASSETS, WITH L0–L7 FIT AND WHERE EACH STOPS

| Asset | Identifier / access | Fits | Verdict | Where it stops |
|---|---|---|---|---|
| **SPADE** | arXiv:2401.03038 · PVLDB 17(12):4173–4186 | **L3 + L4 test 3** | **ADOPT** | Criterion source is prompt-version history; substitution to statutory text is unmeasured (§9.1) |
| **CLAUSE Table 3** | arXiv:2511.00340 · `2026.findings-eacl.305` | **L4 test 2 — the exhibit** | **ADOPT (as evidence)** | Contracts, not returns; 4 non-frontier models; result holds on the CUAD split |
| **Practical Mutation Testing at Scale** | arXiv:2102.11378 · TSE 2021 | **L4 test 1** | **ADOPT** | Equivalent-mutant problem unsolved; report the mutant catalogue, not a bare % |
| **Barr et al. oracle survey** | IEEE TSE 41(5):507–525 | **L6 framing** | **ADOPT** | A survey — supplies vocabulary and the metamorphic route, no code |
| **TF-IDF + XGBoost false-success detector** | arXiv:2606.09863 | **L5** (cheap secondary check on model-bearing steps) | **ADOPT** | Needs oracle labels to train — on our artifact that means L1's schema + L5's verdicts *are* the label source. Bootstraps only after L5 exists |
| **FinBalance deterministic ledger generator** | arXiv:2606.15949 | **§9.2 clean/dirty corpus, feeding L4** | **EVALUATE — highest-value unexplored item** | US-GAAP reconciliation, not an IFSCA workbook; licence/availability unverified |
| **FinVerBench taxonomy + rule verifier** | arXiv:2605.29586 | **L4 (FFR precedent), L6 (rendering ablation)** | **EVALUATE** | Code **not released in v1**; n=43 clean; single-author, unreviewed; 0% FPR by construction |
| **AUDITFLOW symbolic environment** | arXiv:2606.03031 | **L5/L6** — typed tools over a taxonomy graph × filing graph | **EVALUATE** | n=67; XBRL/US-GAAP; one model; the headline delta is a self-ablation |
| **AbstentionBench** | arXiv:2506.09038 (Meta) | **L2 abstention evaluation** | **EVALUATE** | QA-shaped unanswerability, not key-binding; the 24% rests on 2 model pairs |
| **PASC (method only)** | arXiv:2605.18812 | **L2 joint conformal coverage across L2's stages** | **EVALUATE** | **No financial content whatsoever**; single-author preprint; transfer to xlsx key-binding unmeasured |
| **Entropy-alone-insufficient** | arXiv:2603.21172 | **L2** — kills the naive threshold, supplies the repair (entropy + correctness probe) | **ADOPT (as constraint)** | QA benchmarks; needs a labelled correctness probe we do not have yet |
| **AgentAbstain** | arXiv:2607.10059 | Framing for the "capability won't save you" line | **ADOPT (citation)** | Sandbox agent tasks; preprint |
| **τ³-bench / SABER audit method** | `taubench.com/blog/tau3-task-fixes.html`; τ²-bench README | **Meta — how to audit our own predicate set** | **EVALUATE** | It is a fix-list, not a tool. But "27 of 50 tasks were wrong" is the template for auditing *our* mutant catalogue |
| **QuantMind** | `LLMQuant/quant-mind` · MIT · 2.3k★ · NeurIPS'25 GenAI-in-Finance ws · arXiv:2509.21507 | **L0** | **EVALUATE** | Shapes are research artifacts; protected-xlsx extension **UNVERIFIED** (§9.7) |
| **Vals AI Finance Agent v2** | `vals.ai/benchmarks/fabv2` · `vals-ai/finance-agent-v2` | Framing only | **EVALUATE** | Live leaderboard — quote with a date or not at all |

---

## What this changes about the design

**1. L4 test 2 is now the best-evidenced component in the architecture — promote it.**
CLAUSE is peer-reviewed (EACL 2026 Findings), its best of 80 measured cells is **65.4** against a
one-line constant classifier's **66.2**, and a full-text positive control found **zero** mentions of a
majority/constant/random/trivial baseline. That is not a hunch about the field; it is a verified
absence in a specific camera-ready. The gate is also trivially implementable, and the implementation
should ship in the two-day build:

```python
def degenerate_floor(acc, prec, rec):
    """Recover positive prevalence from a reported (Acc, Prec, Rec) triple and
    return the F1 of a constant always-positive classifier on that set.
    Any predicate scoring at or below this floor is REJECTED at L4 test 2."""
    P, R, A = prec, rec, acc
    denom = R - 1 - R * (1 / P - 1)          # d(Acc)/d(prevalence)
    p = (A - 1) / denom                       # implied positive prevalence
    return p, 2 * p / (1 + p)                 # (prevalence, constant-positive F1)

# CLAUSE, Gemini-2.5 Flash, CUAD Omission_inText: (49.8, 49.6, 95.8)
#   -> prevalence 0.494, floor F1 66.2  vs  reported F1 65.4  -> REJECT
```

Every admitted predicate carries `(prevalence, floor_f1, measured_f1, margin)`. A negative margin is
an automatic rejection, not a discussion.

**2. Delete the "no measured system can say clean" absolute, before 16 August.** Claude Sonnet 4
scored **100/100/100/100 at 0% FPR on 105 instances (43 clean)** in the brief's own most-cited
source, and **79.0% recall at 0% FPR** on the harder rounded rendering. The claim that survives — and
it is still the whole product — is narrower and better:

> *A model can be calibrated on 43 clean statements. What no system does is **declare the boundary of
> what it checked**, at a measured error rate per check, on a real regulated filing. Nine of fourteen
> frontier runs were uncalibrated on the same 43; nothing in their output distinguished the
> calibrated run from the rest.*

That is the FinVerBench author's own conclusion ("the key observed challenge is not error detection
per se… but calibration"), it is unrefutable from the paper, and it points at L4/L5/L7 rather than at
a capability claim that a judge can break by clicking one link.

**3. Break the evidence concentration, or declare it.** Six brief rows co-vary with one 37-page
single-author unreviewed preprint with unreleased code. Two options, and the brief's own rules
require one of them: (a) run the FinVerBench conditions ourselves on the FME workbook — the rule
verifier is 15 relations and we already have 38 checkable ones from the 294 native formulas; or
(b) add a **Warrant** column to §3.1/§3.2 naming the paper, so the reader can see that rows 1–5
are one instrument. **(b) costs ten minutes and is non-negotiable before submission.**

**4. Add `clean_corpus_independent_of_predicate: bool` to the L4 predicate record.** FinVerBench's
0% FPR is achieved on relationships "guaranteed consistent in our clean data by construction." Our
§9.2 clean corpus will be constructed by our own team, from the same templates our predicates are
induced from — **structurally the same circularity**. If L4 does not record which side of that line
each FFR came from, our coverage numbers inherit the exact defect we are selling against. Two FFR
fields, not one: `ffr_constructed_corpus` and `ffr_independent_corpus`, the second usually null and
visibly so.

**5. L6 gains its first relation with a published effect size — for free.**
*Presentation-precision invariance*: re-render the filing at its declared reporting unit and re-run
every predicate; any verdict that changes is presentation-sensitive. FinVerBench measured that
sensitivity at **21 recall points on n=105** for the best model. Add it to the §9.3 list of ~10
relations, at the top, because it is the only one with prior measurement. It also generalises: our
FME workbook declares reporting units, and 84 of its fields are numeric/amount.

**6. Restate §9.4. The three papers disagree less than the brief says.**
- AUDITFLOW: deterministic structure **+14.93** over the strongest baseline on the primary metric
  (n=67). *(The +64 is a self-ablation and a third of it is malformed output.)*
- FinBalance: deterministic ledger feedback **+30 to +33pp** on the primary metric (balance-sheet
  accuracy), **−13 to −52pp** on a *secondary* metric (inconsistency-code detection), n=710.
- FinVerBench: deterministic rules **0% FPR / 52.8% recall** (n=1,942 errors), FPR true by
  construction.

All three agree that deterministic structure helps the primary task. **The disagreement is confined
to what it costs the secondary detection metric** — and FinBalance's mechanism is named: ledger
feedback pushes models to *reconcile* contradictory documents rather than report them. That is a
specific, testable claim, and it is a warning aimed squarely at us: **a deterministic layer that
"fixes" the artifact suppresses the signal we are trying to surface. L5 must never repair; it must
only adjudicate and report.** That is a real architectural constraint recovered from this lane, and
it is worth more than the unresolved "contradiction."

**7. Two evidence rows must be re-sourced or dropped from §2.3 property 3 ("the capability trend runs
against the fix").** The memory result is 10 **open-weight** models with "6 hurt, 4 neutral", and the
24% abstention result is **two open-weight distillation pairs**. Neither can carry a claim about
where the frontier is heading. **AgentAbstain alone can**: 17 frontier models, 42 environments, best
59.5% paired accuracy, act 80.6% vs abstain 59.1%. Let that row stand alone and property 3 survives.

**8. The false-success evidence contains the architecture's own argument, measured.** 45–48% false
success in single-control domains vs **3% in dual-control** — a second observer of environment state
cuts silent failure ~15×. And the only detector that worked was trained on labels from a structured
database field "entirely independent of the agent's natural language." §2.3 property 4 is not a
principle; it is a finding, and it should be quoted as one.

**9. Housekeeping that will otherwise cost a judge's confidence:** delete "PASC names financial
documents as a target" (zero occurrences); fix the τ-airline defect attribution to "27 of 50 tasks
fixed"; date-stamp or drop the Vals AI leaderboard; label MIT NANDA ASSERTED and quote its own
limitations sentence; get the PCAOB 2022 figure and the Part I.A definition from primary sources;
add the 76% (large FIs cannot measure AI value) and drop or restate the 53%-spend clause; and add
**AbstentionBench arXiv:2506.09038** to §6.1, since it is currently an uncited load-bearing source.

---

## Open questions this lane could not settle

1. **Is AbstentionBench's "24% drop in abstention" relative or absolute percentage points?** The
   paper does not say. Needs Figure 6(a) read off the PDF.
2. **FinVerBench artifacts.** v1 defers release to camera-ready. Is there a v2 or a repo now? Without
   it we cannot re-run the 15-rule verifier or reuse the taxonomy.
3. **FinBalance's licence and generator availability.** It is the closest published thing to §9.2's
   clean-corpus machinery, and I did not open the repo or licence.
4. **CLAUSE's stated class balance.** My ~49.5% is DERIVED (six-way replicated) but the paper never
   prints prevalence. Table 1 may state per-category instance counts that settle it directly.
5. **PCAOB 2022 Big Four Part I.A rate** and the authoritative definition text — both currently
   SECONDARY.
6. **"26 models" on Vals AI Finance Agent v2** — could not confirm a model count at source.
7. **The τ-bench "20.8% → 40.0% when flawed tasks are excluded" figure** — SECONDARY only; the
   primary (SABER, Cuadron et al. 2025) was not opened.
8. **SPADE's author affiliations** — the brief's parenthetical is unverified.
9. **Has anyone in the financial-verification literature *ever* reported a constant/majority
   baseline?** I positively controlled the absence inside CLAUSE only. A survey across
   FinVerBench / FinBalance / AUDITFLOW / FinAuditing / BizFinBench would turn a single-paper
   observation into a field-level claim — and that is a publishable result in its own right, cheap
   to run, and directly the thing L4 test 2 sells.

---

## Adversarial verification (independent pass)

**Run 10 Aug 2026, by a separate verifier instructed to refute.** I did not accept any citation in
this lane as evidence for itself. For each claim below I opened the primary artifact myself — the
arXiv abstract page, the paper's own HTML, the ACL Anthology record, the vendor's live page — and
re-derived the number. Where I could not reach the primary, the verdict is UNVERIFIABLE and says so.
Two independent-pass constraints applied throughout: an identifier that does not resolve is
NOT-FOUND rather than "probably fine", and a percentage quoted without its denominator is
UNVERIFIABLE rather than confirmed.

**Selection rule:** I picked the claims whose *falsity* would do the most structural damage — the
ones that, if wrong, delete a layer of the architecture or invert an argument in the brief. Ten
claims, plus one arithmetic re-derivation I ran myself.

### Method note on tooling

`WebFetch` against primary hosts; the session's `WebSearch` budget was exhausted mid-pass (200/200),
which is why the PCAOB item below could not be closed. Numeric sensitivity was computed locally in
Python, not read off any source.

### Verdicts

**1. arXiv:2605.29586 (FinVerBench) is a real paper with the stated identity — CONFIRMED.**
Opened `arxiv.org/abs/2605.29586` directly. Title *FinVerBench: Benchmark Validity and Calibration in
Large Language Model Financial Statement Verification*; author **Silu Panda**; submitted **28 May
2026**. The abstract independently corroborates three separate lane claims without my having to read
the body: SEC 10-K filings of **43 S&P 500 companies**; the four-category error taxonomy
(arithmetic / cross-statement linkage / year-over-year / magnitude); **"95–100% false positive rates
on clean statements, with one exception achieving 0% observed false positives"**; and **"recall
varying from 79% to 100% depending on numerical formatting."** This is the single highest-stakes
identifier in the lane — five brief rows co-vary with it — and it resolves.

**2. The Claude Sonnet 4 counter-example is real — CONFIRMED at source.**
Opened `arxiv.org/html/2605.29586v1` and pulled Table 6 myself. Claude Sonnet 4 row reads
**105 | 100.0 | 100.0 | 100.0 | 100.0 | 0.0**. Rule-based (τ=0.01%) row reads
**105 | 71.4 | 100.0 | 51.6 | 68.1 | 0.0**. Composition confirmed verbatim: *"n=105 for all rows: 43
clean statements and 62 observable error statements after excluding 3 not-enough-information
positives."* The "nine of fourteen" sentence is present verbatim. The Wilson bound is present:
**"The 0% FPR [95% Wilson upper bound: 8.2%] vs. 95.3%."**
→ The lane's headline (2) survives an independent read. **§2.1 of the brief — "no measured system can
say this one is clean" — is refutable from the brief's own most-cited source, and the deletion the
lane demands before 16 August is correctly demanded.** I found no way to rescue the absolute.

**3. CLAUSE is peer-reviewed — CONFIRMED, independently, at the anthology.**
This is the load-bearing warrant claim for L4 test 2 and I checked it without going through arXiv.
`aclanthology.org/2026.findings-eacl.305/` resolves to *Better Call CLAUSE: A Discrepancy Benchmark
for Auditing LLMs Legal Reasoning Capabilities*, Choudhury / Chandramouli / Anand / Gupta, venue
**Findings of the Association for Computational Linguistics: EACL 2026**, **March 2026**. The arXiv
record `2511.00340` independently gives v1 1 Nov 2025 / v2 7 Jan 2026 and confirms "over 7500
real-world perturbed contracts", CUAD, ContractNLI, and 10 anomaly categories.
→ The one *peer-reviewed* exhibit in the evidence base is genuinely peer-reviewed.

**4. F1 65.4 is the table maximum, and the models are non-frontier — CONFIRMED.**
Independent read of Table 3 in the paper HTML: highest F1 anywhere in the table is **65.4**,
Gemini-2.5 Flash, CUAD, `Omission_inText`, with **Acc 49.8 / Pre 49.6 / Rec 95.8 / F1 65.4** — cell
for cell what this lane reports. Four models only: GPT-4o-mini, Gemini-2.0 Flash, Gemini-2.5 Flash,
LLaMa-3.3 70B Instruct. An independent check for a majority-class / random / constant / always-predict
baseline in the paper returned **none**.
→ Both the number and the qualification the lane adds ("best of four non-frontier models") hold.

**5. The degenerate-floor arithmetic — CONFIRMED, and I am strengthening it.**
I re-derived the prevalence identity from scratch rather than checking the lane's algebra:
`A = R·p + (1−p) − R·p·(1/P − 1)` ⇒ `p = (A−1) / (R − 1 − R·(1/P − 1))`. Correct as printed.
Point estimate on (49.8, 49.6, 95.8): prevalence **0.49436**, floor F1 **0.6616**, and F1
recomputed from (P, R) = **0.6536**, matching the paper's printed 65.4 to the decimal.

**The lane reports the comparison as a point estimate. That is the weakest form of the claim, and it
is the form an adversary attacks.** The inputs are printed to one decimal place, so each is only
known to ±0.05pp — and the floor is a *derived* quantity, so rounding error propagates into it. I
swept the full ±0.0005 box on all three inputs:

| Quantity | Range over the rounding box |
|---|---|
| implied prevalence | 0.4929 – 0.4958 |
| constant-classifier floor F1 | **66.03 – 66.29** |
| measured F1 (from P, R) | **65.31 – 65.42** |
| **margin (floor − measured)** | **+0.62 to +0.99 F1 points — strictly positive everywhere** |

→ The exhibit does not depend on a favourable rounding. The intervals do not overlap at any corner
of the box. **Quote it as "the floor exceeds the measured maximum by 0.6–1.0 F1 points across the
full rounding interval", not as "66.2 vs 65.4".** The interval version is the one that survives
contact with a hostile reader, and the lane should have computed it.
*Residual risk I could not eliminate:* the derivation assumes Acc, Prec and Rec are reported over the
same denominator. If the paper computed precision over only parseable outputs, `p` is wrong. The
six-way replication at 49.4–49.7% is strong evidence against that, but it is evidence, not proof.

**6. FinBalance arXiv:2606.15949 — CONFIRMED, and the lane's open question #3 is now closed
in the design's favour.**
Abstract confirms verbatim: *"On a 710-record evaluation split, six contemporary LLMs reach at most
46% exact final-balance-sheet accuracy"* and *"Four models show a 26–41 pp gap between BS_exact …
and BS_recon."* Body confirms **"BS_exact rises by +30 to +33 pp across three model families"**
alongside the detection losses **Gemini 3 Flash −13 pp (not significant), Qwen 3 235B −17 pp,
Claude Haiku 4.5 −52 pp** — so the lane's trade-off restatement of §9.4 is correct and the brief's
one-directional "worsened by 13–52pp" is not.
**New at source, and it matters:** the paper states the **generator and code are released under
Apache-2.0** and the **benchmark records under CC BY 4.0 (commercial use with attribution)**. This
lane listed FinBalance as "licence/availability unverified" and as the highest-value unexplored item
for §9.2. It is licence-clear for our use. That upgrade should propagate to Part D.
*Still open:* no explicit repository URL was visible in the retrieved text, so "released" is a claim
by the authors that I have not confirmed by cloning anything.

**7. AgentAbstain arXiv:2607.10059 — CONFIRMED exactly.**
`arxiv.org/abs/2607.10059`, submitted **11 Jul 2026**, Liu et al. Abstract gives **263 paired tasks
across 42 executable sandbox environments**, **17 frontier LLMs in 4 agent harnesses**, and
*"only 59.5% paired accuracy (correct on both the act and abstain sides of each paired task)"* for
**Gemini 3.1 Pro**. All four brief numbers confirmed without recourse to this lane.
→ The lane's recommendation #7 — let AgentAbstain carry §2.3 property 3 alone — is supportable. It
is the only one of the three property-3 rows measured on frontier models.

**8. AUDITFLOW +14.93 — CONFIRMED in the abstract; the baseline's *identity* is QUALIFIED.**
Abstract verbatim: *"AuditFlow reaches 82.09% joint audit accuracy under GPT-5.5, outperforming the
strongest baseline by 14.93 points. Removing deterministic checks drops accuracy to 17.91%."* So the
lane's central correction — that +64 is a self-ablation and +14.93 is the like-for-like number — is
right, and §9.4's restatement is sound.
**But:** the lane states the strongest baseline is "Single Agent, GPT-5.5, **67.16%**". 67.16 is
exactly 82.09 − 14.93. That number is *arithmetically implied*, not read off the abstract, and I did
not find it stated. Its identity as "Single Agent" is likewise not in the abstract. Mark the 67.16
and the "Single Agent" label **DERIVED/UNVERIFIED** until someone opens Table 2. The +14.93 itself is
safe.

**9. PASC arXiv:2605.18812 — the lane's REFUTATION of the brief is itself CONFIRMED.**
`arxiv.org/abs/2605.18812`, *PASC: Pipeline-Aware Conformal Prediction with Joint Coverage Guarantees
for Multi-Stage NLP and LLM Pipelines*, **Varun Kotte**, single author, 12 May 2026. Independent
check for finance / financial documents / invoices / KYC / regulatory in the abstract and subject
listing: **none**. Datasets: **CoNLL-2003, WNUT-17, WikiNEuRal** — news, Twitter, Wikipedia.
→ Delete "names financial documents as a target" from §6.1. The brief marks this row ⓞ
(operator-verified at source), which is the worst possible label for it to carry.

**10. The memory result — the lane over-refuted. NEW FINDING: the source contradicts itself.**
This is the one place where my pass disagrees with this lane.
The lane marks the brief's "**all 10 models worse**" as **REFUTED**, correcting it to "6 hurt, 4
neutral". I opened both the abstract page and the body.

- **Abstract**, `arxiv.org/abs/2603.29231`: *"memory scaffolds **universally hurt** long-horizon
  performance **across all 10 models**"* — 10 models across 23,392 episodes.
- **Body**, §6.5 and Table 13 caption: *"The memory scaffold never helps: **6 models are hurt, 4 are
  neutral (within ±0.03 GDS)**."*

The two statements are **not compatible**. The brief was quoting the abstract faithfully; the lane
was quoting the body faithfully; the paper is the thing that is wrong.
→ **Correct verdict: QUALIFIED, not REFUTED.** And the correct action is stronger than a reword: a
preprint whose abstract overstates its own body is a source to *downgrade*, not merely to re-quote.
The brief's §5.3 currently justifies "no cross-step memory" partly on this paper. That justification
now rests on a body sentence that the same paper's abstract contradicts, measured on **ten
open-weight models** (Llama 3.1 8B, Mistral Nemo, Mistral 24B, Qwen3 30B, Qwen3 32B, Llama 3.3 70B,
MiniMax M2.5, GLM-4.5 Air, Kimi K2.5, DeepSeek V3 — no frontier model), with one scaffold, from a
three-author group. **Keep the architectural choice; drop this citation to a footnote, or cite it for
"never helped" and state that the paper's abstract and body disagree.** If a judge opens the abstract
after we have quoted the body, we look like we clipped it — the exact failure the lane catches CCAF
for at §B.14.

**11. AbstentionBench's 24% — denominator CONFIRMED as two pairs; relative-vs-pp remains
UNVERIFIABLE.**
Abstract (arXiv:2506.09038, 10 Jun 2025, Kirichenko / Ibrahim / Chaudhuri / Bell) verbatim: *"20
diverse datasets… Evaluating 20 frontier LLMs… reasoning fine-tuning degrades abstention (by 24% on
average)."* Body verbatim: *"reasoning models DeepSeek R1 (Distill Llama 70B) and s1 show an average
of 24% drop in abstention compared to their non-reasoning counterparts"* — i.e. R1-Distill-Llama-70B
vs Llama-3.3-70B-Instruct and s1.1-32B vs Qwen-2.5-32B-Instruct.
→ The lane is right that the abstract's placement invites the reader to attach 24% to the 20-model
sweep when the body computes it over **two open-weight distillation pairs**. On relative-vs-percentage
points I decline to upgrade the lane's UNRESOLVED: the retrieved text supports "relative" only by
inference, and inference is what working rule 3 forbids. **UNVERIFIABLE. Needs Figure 6(a) off the
PDF, as the lane's open question #1 says.**

**12. τ³-bench "27 of 50 airline tasks fixed" — CONFIRMED at the primary.**
`taubench.com/blog/tau3-task-fixes.html`, Victor Barres & Ben Shi, February 2026: **27 of 50 airline
tasks fixed**, **26 of 114 retail**, airline pass^1 **+14.0 to +20.0 points depending on the model**,
and a **+22 point** pass^4 gain for GPT-5.2 (high), 50.0% → 72.0%. Retail is **−0.4 to +5.5** on
pass^1 — a datum the lane omits and which slightly weakens the "half the benchmark was measuring the
instrument" line if it is generalised beyond airline.
→ The lane's MISATTRIBUTED verdict on the brief's "75+ defects in one 50-task airline benchmark"
holds, and its safe restatement is accurate.

**13. Vals AI — CONFIRMED stale; "26 models" is UNVERIFIABLE at source.**
Live page, read today: **927 expert-reviewed questions**; **"Muse Spark 1.2 tops both metrics —
60.60% Partial Credit and 50.88% All-Pass"**; Financial Modeling **"even the best model reaches only
34.52%"**; page stamp **"Updated: 8/6/2026"**. The brief's 58.63 / 47.71 / 34.14 are all superseded.
**No model count is published anywhere I could reach.** Per the denominator rule, "26 models" is
UNVERIFIABLE, not "probably fine" — and it should be struck from §3.5 rather than carried.

**14. PCAOB 20% — UNVERIFIABLE in this pass. NOT closed.**
I could not re-derive this at the regulator. The constructed news-release URL returned **HTTP 404**;
the 2024 inspection-observations Spotlight PDF path returned **HTTP 404**; `pcaobus.org/news-events/
news-releases` renders its listing client-side and served no releases; and the session's WebSearch
budget was exhausted before I could locate the correct path.
→ I am **not** confirming this lane's VERIFIED-AT-SOURCE marking on the 20%/26% figures. It may well
be right — but I did not see the release, and this pass does not launder someone else's reading.
**This is the brief's §3.4 "absent arm" and the only regulator-measured human-control baseline in the
whole document.** It is now the single most important unclosed item in the evidence base, ahead of
the lane's own open questions, because it is the one number a GIFT judge is most likely to recognise
and check. Open `pcaobus.org` and read the release before 16 August; get 2022 and the Part I.A
definition at the same time.

### What this pass changes

**The spine holds.** Every identifier I could reach resolved, at the stated title, author and date —
including all four 26xx IDs I checked (2605.29586, 2606.15949, 2607.10059, 2603.29231, 2606.03031,
2605.18812). The brief's §6.1 warning that "several carry 26xx IDs… plausible for the date but
unverified" can be retired for these six. **Nothing here is fabricated.** The two structurally
load-bearing artifacts — FinVerBench's Table 6 and CLAUSE's Table 3 — read exactly as this lane
reports them, cell for cell, and I read them independently.

**Three changes to make:**

1. **Promote the CLAUSE exhibit from a point comparison to an interval.** The floor exceeds the
   measured maximum by **0.62–0.99 F1 points across the entire ±0.05pp rounding box**. Ship that
   sentence, and ship the interval alongside `degenerate_floor()` in the L4 gate — a gate that
   rejects on a point estimate is a gate an adversary tunes around. Add the residual assumption
   (same-denominator reporting) as a documented precondition of the function.

2. **Downgrade arXiv:2603.29231, and record *why*.** Its abstract says "universally hurt across all
   10 models"; its body says "6 hurt, 4 neutral within ±0.03 GDS". That is a source defect, not a
   quoting defect, and it is the second time in this corpus that a summary claimed more than its own
   measurement supported. It belongs in the brief's §4.4 self-demonstration as a *third* exhibit —
   found in someone else's paper this time — rather than as a supporting citation for §5.3.

3. **PCAOB is now the top unclosed item.** Not because it is doubtful, but because it is the only
   place where this pass could not do the thing the brief's working rule 3 requires: open the
   instrument and read the clause off the page.

**One upgrade the design gets for free:** FinBalance's generator is **Apache-2.0** and its records
**CC BY 4.0**. §9.2's clean-corpus machinery — named in the brief as "the design's largest structural
weakness" — has a licence-clear published starting point. That is worth more to the build than any
correction in this section.
