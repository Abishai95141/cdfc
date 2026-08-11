# L07 — CONFORMAL ABSTENTION FOR L2 KEY-BINDING
### Lane return: make L2 concrete and defensible, and repair it where the paper it rests on does not carry the weight assigned to it.

**Compiled 10 Aug 2026.** Every claim carries a warrant label:

- **VERIFIED-AT-SOURCE** — I opened the primary artifact (paper PDF/abstract page, arXiv API record, GitHub API record, licence file, or ran the computation myself).
- **SECONDARY** — a credible source describes it; I did not open the primary.
- **UNVERIFIED** — could not confirm. Stated as such, never smoothed over.
- **DERIVED** — arithmetic I performed. A derived number never claims a stronger warrant than its weakest input.

---

## PART 0 — HEADLINE, FOR THE IMPATIENT

1. **PASC (arXiv:2605.18812) exists.** The brief told me to assume it might not. It does — confirmed against the arXiv API with a working negative control. **But its warrant in the brief (ⓞ, "verified") is wrong**, and its Table 1 is internally inconsistent by an amount I can compute. Do not cite it on a slide. §2.
2. **Its central theorem is true, trivial, and older than the paper.** Conformal on the max-of-stages score gives simultaneous coverage in one line from exchangeability. It is a named class ("maximum nonconformity") in a refereed ICML 2025 taxonomy. We can implement the idea and cite the refereed anchor. §6.
3. **The bigger correction: L2 does not need a model for native template cells.** I measured it. Under a header-anchored geometric key, **154 of 3,755 unlocked cells (4.10%)** are ambiguous; under the plain address key, **0 of 3,755**. Key-binding on the prescribed workbook is a *lookup against L1*, not a prediction. Conformal belongs on the *cross-document* binding only. §9.1.
4. **At the architecture's own measured base error rate, conformal abstains on everything.** ARCHITECTURE Part 1 fact 5 says extraction gets "0% of the key". I derive the forced-abstention floor `r ≥ (μ−α)/(1−α)`; at μ=1.0 that is **100% abstention at every α**. Conformal cannot rescue a broken extractor. It can only price one. §9.5.
5. **"Abstain unless singleton" does not cost coverage — it changes which guarantee you hold.** The unconditional rate of *silently accepting a wrong key* stays ≤ α. The rate *conditional on having accepted* inflates to ≤ α/P(accept). At the best measured document-IE singleton rate I could find (**70%**, Rombach & Mehdiyev, IJDAR 2026), α=0.05 becomes a **7.14%** conditional error bound. §9.4.
6. **On a synthetic calibration set the guarantee is not void — it is degraded by a bounded, unmeasurable amount.** Barber, Candès, Ramdas & Tibshirani (*Annals of Statistics* 2023) give `Coverage gap ≤ Σᵢwᵢ·d_TV(R(Z),R(Zⁱ)) / (1+Σᵢwᵢ)`. The bound is on the *score* vector, not the raw data — which is what makes the repair buildable. §10.
7. **The fallback that survives is a three-part instrument**, all of which is worth building even with the guarantee void: weighted conformal under covariate shift, a conformal test martingale that *refuses to certify* when exchangeability is rejected, and a declared-population coverage statement. §11.

---

## PART 1 — METHOD, AND THE COVERAGE DENOMINATORS I AM ENTITLED TO

Before any absence claim in this document, here is exactly what I searched and what the search box actually indexes.

**Corpus A — arXiv API (`export.arxiv.org/api/query`).** This searches **metadata only** (title, abstract, authors, comments). It is **not** a full-text search. Any absence claim below is an absence *in abstracts*, not in papers.

| Query (field `abs:`) | totalResults | Warrant |
|---|---:|---|
| `"conformal prediction"` | **1,479** | VERIFIED-AT-SOURCE |
| `"conformal prediction" AND "medical imaging"` (**positive control**) | **38** | VERIFIED-AT-SOURCE |
| `"conformal prediction" AND "regulatory"` | **5** | VERIFIED-AT-SOURCE |
| `"conformal prediction" AND ("audit" OR "compliance" OR "financial statement")` | **18** | VERIFIED-AT-SOURCE |

**Negative control on the identifier check.** `id_list=2605.99999` returns `opensearch:totalResults = 0` with no entry. So when the same interface returns a populated entry for `2605.18812`, that is a real record and not an artefact of the fetch path. **VERIFIED-AT-SOURCE.**

**What the 5 + 18 hits actually are.** I listed all 23 titles. None is about *prescribed regulatory reporting workbooks, filing verification, or supervisory return extraction*. The two nearest:
- `FinAbstain: Uncertainty-Calibrated Multimodal RAG for Selective Financial Forecasting` (2026-07-27) — **forecasting**, not filing verification.
- `Conformal Tradeoffs: Operational Profiles Beyond Coverage` (arXiv:2602.18045v3) — domain-general, but the single most useful paper in the set for our UX. §7.

> **Defensible absence claim, with its denominator:** *across 1,479 arXiv abstracts containing "conformal prediction", the 23 that also mention regulatory/audit/compliance/financial-statement terms contain no application to prescribed regulatory reporting artifacts.* This is an abstract-field claim over a metadata index. It is **not** a claim that nobody has done it — a full-text search would be a different, larger corpus, and industry work is not on arXiv at all.

**Corpus B — GitHub REST API** (`api.github.com/repos/...`) for every library: licence, stars, forks, `pushed_at`, `archived`. All library facts in §8 are VERIFIED-AT-SOURCE against that endpoint on 10 Aug 2026.

**Corpus C — the artifact itself.** `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`, read with `openpyxl` under `/Users/abishaikc/Gift/.venv/bin/python`. All §9.1 measurements are mine, run today.

**Corpus D — papers I opened and extracted to text myself** (`pdftotext -layout`): Angelopoulos & Bates arXiv:2107.07511; Barber et al. arXiv:2202.13415; Phillips et al. arXiv:2603.21172.

---

## PART 2 — THE TWO CITATIONS THE BRIEF LEANS ON

### 2.1 `PASC — arXiv:2605.18812` — EXISTS, but the warrant is wrong

**RND-BRIEF §6.1 lists PASC with warrant ⓞ (verified by the operator at source) and calls it a "load-bearing paper." ARCHITECTURE L2 says PASC "does pipeline-aware conformal with joint coverage guarantees for exactly this."**

**What is true. VERIFIED-AT-SOURCE** (arXiv API, `id_list=2605.18812`):

- Title: *PASC: Pipeline-Aware Conformal Prediction with Joint Coverage Guarantees for Multi-Stage NLP and LLM Pipelines*
- `id`: `http://arxiv.org/abs/2605.18812v1`; `published`: 2026-05-12T08:23:12Z
- Author: **Varun Kotte** — sole author
- Subjects: cs.LG; cs.CL; cs.IR. **journal_ref: none. comments: none. versions: v1 only. code repository: none linked.**

**What is wrong with using it as authority.**

**(a) No independent review, no code, no venue.** v1, no journal ref, no comments field, no code/data availability statement. The paper says only that it uses public benchmarks and off-the-shelf checkpoints with reproducibility details in an appendix. **VERIFIED-AT-SOURCE.**

**(b) The same sole author also wrote the other paper that would conveniently support us.** I queried the arXiv API for `au:"Varun Kotte"`: **totalResults = 7**. **VERIFIED-AT-SOURCE.**

| # | Title | Published | journal_ref | comment |
|---|---|---|---|---|
| 1 | Retrieval Augmented Generation for Domain-specific Question Answering | 2024-04-23 | none | AAAI 2024 SDU **Workshop** |
| 2 | PromptPort: A Reliability Layer for Cross-Model Structured Extraction | 2026-01-06 | none | 12 pages |
| 3 | Not All Queries Need Rewriting… | 2026-03-02 | none | none |
| 4 | UCCI: Calibrated Uncertainty for Cost-Optimal LLM Cascade Routing | 2026-05-11 | none | code link present |
| 5 | **PASC** | **2026-05-12** | none | none |
| 6 | Two Wrongs, No Right: Auditing Social-Desirability Bias… | **2026-05-12** | none | none |
| 7 | **When Can Conformal Risk Control Certify LLM Outputs?** | **2026-06-27** | none | none |

Six preprints in seven months, two posted the same day on unrelated topics, one refereed venue among them and that a workshop. A personal site describes the author as a Staff ML Engineer at Adobe — **SECONDARY, not verified at source, and irrelevant to the warrant either way.** The point is not the person. The point is that **the brief has two independent-looking supports (PASC for joint coverage, and the CRC-certification bound) that are in fact one unreviewed source.**

**(c) Table 1 is internally inconsistent, and I can quantify by how much. DERIVED.**

Reproduced verbatim from the paper (**VERIFIED-AT-SOURCE**), caption: *"E2E coverage and average prediction set size at α=0.1, CoNLL-2003, 18-type entity typing. PASC achieves highest coverage at identical set size to Bonferroni (ncal=1000, ntest=500, 5 seeds)."*

| Method | E2E Cov. | Avg Set Size | Guarantee? |
|---|---|---|---|
| Indep CP | 0.865±0.005 | 1.083 | No |
| Bonferroni | 0.934±0.001 | 1.083 | Yes |
| MC Dropout | 0.902 | — | No |
| PASC (ours) | **0.964±0.000** | **1.083** | Yes |

The paper defines Avg Set Size (§4.6) as *"Mean |𝒞ₖ(x)| over test set and stages"* and constructs sets by a **shared threshold**: `𝒞ₖ(x) = {y : sₖ(x,y) ≤ q̂}`. Threshold sets are **nested** — a larger q̂ yields a superset.

Now the arithmetic. To move end-to-end coverage from 0.865 to 0.964 you must newly cover **≥ 9.9%** of test examples. Under nesting, an example can only become covered by *gaining at least one element* in at least one stage's set. With K=3 stages and the mean taken over test set **and** stages, adding one element for 9.9% of examples at one stage raises the reported mean by at least

```
0.099 / 3 = 0.033
```

So the mean set size must rise from 1.083 to **≥ 1.116**. The paper reports **1.083 for all three methods**. A rounding explanation fails by a factor of ~66: 0.033 is not hidden by a third decimal place.

> **Finding, DERIVED from the paper's own numbers and its own construction:** *Table 1 reports a 9.9-point end-to-end coverage spread across three nested-threshold methods at an identical mean prediction-set size. Under the paper's own set construction these cannot both be true; the mean set size would have to rise by ≥0.033. There is no code to adjudicate.*

**(d) And the headline claim inverts.** PASC sells itself as tight where Bonferroni is conservative (*"nearly tight up to a 1/(n+1) factor"*, Remark 7: *"PASC achieves the same ≥1−α guarantee with a single quantile q̂ that automatically assigns tighter budgets to stages whose scores tend to be low"*). At α=0.1 a tight method lands at ~0.90. **PASC reports 0.964 — i.e. it over-covers by 6.4 points, three points *more conservatively* than the Bonferroni it criticises.** VERIFIED-AT-SOURCE (numbers) + DERIVED (reading).

**Verdict: EVALUATE→REJECT as authority. The idea is fine; the citation is not.** §6 rebuilds the same result from first principles with a refereed anchor.

**Where it fits L0–L7:** would have been L2. **Where it stops:** it cannot be quoted, and it must not appear on a slide or in the application. Lane L01 should mark it QUALIFIED, not confirmed.

### 2.2 `Entropy Alone is Insufficient — arXiv:2603.21172` — CONFIRMED, and stronger than the brief uses it

**VERIFIED-AT-SOURCE** (arXiv API + I extracted the PDF myself).

- Title exactly as cited. `id`: `http://arxiv.org/abs/2603.21172v1`; published 2026-03-22T11:27:13Z.
- Authors: Edward Phillips, Fredrik K. Gustafsson, Sean Wu, Anshul Thakur, David A. Clifton. **Department of Engineering Science, University of Oxford** (+ Oxford Suzhou Centre). Five authors, named institution. Materially better warrant than PASC.

**Denominators, which the brief does not carry:** three QA benchmarks (**TriviaQA, BioASQ, MedicalQA** — note: *not* NaturalQuestions; one secondary summary I fetched got this wrong), **four model families** (Llama, Mistral/Ministral, Qwen, Gemma), all in the **3B–8B parameter range** — the paper states this as a limitation. Metrics: **E-AURC** and **TCE** (Target Calibration Error), TCE averaged over target risk levels **α ∈ [0.05, 0.3]**.

The named failure mode, quoted from the paper's own contribution list:

> "the **confidently wrong regime**, in which models produce low-entropy hallucinations."

And the deployment-facing claim, which is the one that matters for us:

> "strong AUROC does not imply reliable selective prediction at strict safety thresholds, and metrics such as AURC and TCE better reflect whether a system can be trusted to operate at a stated risk level."

And the mechanism, from §3.2 (Figure 2, Qwen/TriviaQA):

> "Many answers, both correct and hallucinated, collapse to SE = 0, yet receive distinct PC probe scores."

**Why this is worse news for us than the brief implies.** Structured extraction into a fixed template is *precisely* the low-entropy regime: constrained decoding collapses the output distribution by construction. Our L2 would live permanently inside the failure mode this paper names. Table A3 shows the cost concretely — Llama 3.2 3B on MedicalQA, Semantic Entropy **TCE = 0.332**, and the caption warns: *"In cases where coverage is zero over the whole operational range, we report TCE as the model base hallucination rate."* i.e. some configurations **abstain on everything** and the metric silently reports the base rate. **VERIFIED-AT-SOURCE.**

**Where it fits:** L2, as the *kill* argument against a confidence threshold. **Where it stops:** 3B–8B models, short-form QA. Whether the confidently-wrong regime transfers to long-form or structured generation is explicitly flagged by the authors as unknown. Do not extrapolate it to frontier models without saying so.

---

## PART 3 — FOUNDATIONS, STATED PRECISELY ENOUGH TO DEFEND

### 3.1 The assumption

Split (inductive) conformal prediction requires **exchangeability** of the calibration points together with the test point:

> `(Z₁, …, Z_n, Z_test)` is exchangeable — its joint distribution is invariant under every permutation of the n+1 indices, where `Zᵢ = (Xᵢ, Yᵢ)`.

i.i.d. is a strict special case. Exchangeability is weaker and is what the proof actually uses. Angelopoulos & Bates state Theorem 1 under i.i.d. and then note for full conformal (Theorem 5): *"More generally, the above holds for exchangeable random variables (X₁,Y₁),...,(X_{n+1},Y_{n+1}); the proof of Theorem 5 critically relies on the fact that the score s_{n+1} is exchangeable with s₁,...,s_n."* **VERIFIED-AT-SOURCE** (arXiv:2107.07511, extracted text, lines 1505–1513).

**The operative phrase is "exchangeable with".** Exchangeability is not a property of a dataset. It is a property of a *pair*: your calibration draw and the thing you will deploy on. This is the entire content of §10.

### 3.2 The recipe and the guarantee

From the same source (§1.1, steps 1–4, **VERIFIED-AT-SOURCE**):

1. Pick a heuristic uncertainty from the pretrained model.
2. Define `s(x,y) ∈ ℝ`. *"Larger scores encode worse agreement between x and y."*
3. `q̂` = the `⌈(n+1)(1−α)⌉ / n` quantile of `s₁,…,s_n`.
4. `C(X_test) = { y : s(X_test, y) ≤ q̂ }`.

**Theorem 1 (Conformal coverage guarantee; Vovk, Gammerman, Saunders), verbatim:**

> "Suppose (Xᵢ, Yᵢ)ᵢ₌₁,…,ₙ and (X_test, Y_test) are i.i.d. and define q̂ as in step 3 above and C(X_test) as in step 4 above. Then the following holds: P(Y_test ∈ C(X_test)) ≥ 1 − α."

**Both bounds, equation (1), verbatim:**

> `1 − α ≤ P(Y_test ∈ C(X_test)) ≤ 1 − α + 1/(n+1)`

with Theorem D.2 supplying the upper bound *"if the scores s₁,...,s_n have a continuous joint distribution."* **VERIFIED-AT-SOURCE.**

**Three properties that make this the right tool for a coverage-declaring product:**
- **Distribution-free.** No assumption on P.
- **Model-free.** Any black box. Our extractor can be swapped without re-deriving the guarantee.
- **Finite-sample.** Holds at n=22, not asymptotically. This matters enormously to us — §3.3.

**The property it does NOT have, and this is the one that will be attacked in a demo:** the guarantee is **marginal**, averaged over the calibration draw and the test point. It says nothing about coverage on any particular field, any particular sheet, or any particular filer. *"the marginal guarantee from normal conformal prediction can still be satisfied even if all errors happen in one group."* (A&B §4.1, **VERIFIED-AT-SOURCE**.) A supervisor will ask exactly this question. §4.3 is the answer.

### 3.3 How much calibration data — with the numbers, reproduced

Coverage *conditional on the calibration set* is itself random, and Vovk gives its exact law:

> `P(Y_test ∈ C(X_test) | {(Xᵢ,Yᵢ)}ⁿᵢ₌₁) ∼ Beta(n + 1 − l, l)`, where `l = ⌊(n+1)α⌋`

**VERIFIED-AT-SOURCE** (A&B §3.2). Their Table 1: calibration size `n(ε)` for coverage slack ε at δ=0.1, α=0.1:

| ε | 0.1 | 0.05 | 0.01 | 0.005 | 0.001 |
|---|---:|---:|---:|---:|---:|
| n(ε) | 22 | 102 | 2,491 | 9,812 | 244,390 |

**I reproduced this table independently** from the Beta law using `scipy.stats.beta` on the project venv. **DERIVED, and it matches exactly:**

```
n=     22  90% central interval = [0.8019, 0.9836]  max slack = 0.0981   (~0.1  ✓)
n=    102  90% central interval = [0.8511, 0.9458]  max slack = 0.0489   (~0.05 ✓)
n=  2,491  90% central interval = [0.8900, 0.9098]  max slack = 0.0100   ( 0.01 ✓)
n=  9,812  90% central interval = [0.8950, 0.9050]  max slack = 0.0050   (0.005 ✓)
n=244,390  90% central interval = [0.8990, 0.9010]  max slack = 0.0010   (0.001 ✓)
```

**At the α we would actually run (α = 0.05), for calibration sizes we could plausibly construct. DERIVED:**

| n | target | 90% central interval | worst slack |
|---:|---:|---|---:|
| 100 | 0.950 | [0.9108, 0.9801] | 0.0392 |
| 200 | 0.950 | [0.9228, 0.9726] | 0.0272 |
| 500 | 0.950 | [0.9332, 0.9650] | 0.0168 |
| 854 | 0.950 | [0.9382, 0.9624] | 0.0124 |
| 1,000 | 0.950 | [0.9382, 0.9608] | 0.0118 |
| 2,000 | 0.950 | [0.9418, 0.9578] | 0.0082 |
| 5,000 | 0.950 | [0.9448, 0.9550] | 0.0052 |

**Reading for the design:** ~1,000 calibration items buys ±1.2 points of calibration-conditional slack. **The sample-size problem is not the binding constraint for L2.** The binding constraint is *what population those items are a sample of* (§10) — which is a much less comfortable problem, because you cannot fix it by labelling harder.

---

## PART 4 — CLASSIFICATION VARIANTS: WHICH SCORE, AND WHY

Key-binding is a K-way classification (cell → template key). The score choice is the whole design.

### 4.1 LAC / THR — smallest sets, worst conditional behaviour

`s(x,y) = 1 − f̂(x)_y`. Yields provably smallest average set size; A&B note it *"tends to undercover hard subgroups and overcover easy ones."* **VERIFIED-AT-SOURCE.** Sometimes called the least-ambiguous set-valued classifier. **Useful property for us: it can return the EMPTY set** — a free, automatic abstention signal.

### 4.2 APS — Romano, Sesia & Candès, NeurIPS 2020

*Classification with Valid and Adaptive Coverage*, Advances in NeurIPS 33; arXiv:2006.02544. **SECONDARY** (I confirmed title/venue/authors via NeurIPS proceedings listing and Semantic Scholar; I did not open the paper PDF). The score is stated and coded in A&B §2.1 (**VERIFIED-AT-SOURCE**):

> `s(x,y) = Σ_{j=1..k} f̂(x)_{π_j(x)}, where y = π_k(x)`

i.e. the cumulative softmax mass down to the true class in descending order, with `π` the sorting permutation. Reference implementation, quoted verbatim from A&B Figure 3:

```python
cal_pi = cal_smx.argsort(1)[:,::-1]
cal_srt = np.take_along_axis(cal_smx, cal_pi, axis=1).cumsum(axis=1)
cal_scores = np.take_along_axis(cal_srt, cal_pi.argsort(axis=1), axis=1)[range(n), cal_labels]
qhat = np.quantile(cal_scores, np.ceil((n+1)*(1-alpha))/n, interpolation='higher')
```

APS buys approximate conditional coverage at the cost of larger sets.

### 4.3 RAPS — Angelopoulos, Bates, Jordan & Malik, ICLR 2021

*Uncertainty Sets for Image Classifiers using Conformal Prediction*, **ICLR 2021 (Spotlight)** — confirmed on the ICLR virtual site and dblp (`conf/iclr/AngelopoulosBJM21`). **SECONDARY.** Regularises away the long tail of unlikely classes that inflates APS sets. **This matters directly for us:** our label space is large (§9.1 counts 488 distinct label strings; the geometric key space is 3,625). APS on a large, badly-tailed label space produces bloated sets; RAPS is the standard fix.

### 4.4 Mondrian / class-conditional — the answer to "does it hold for MY field?"

**Group-balanced coverage** (A&B §4.1, **VERIFIED-AT-SOURCE**), equation (8):

> `P(Y_test ∈ C(X_test) | X_test,1 = g) ≥ 1 − α` for all groups g

achieved by stratifying calibration scores by group and taking a per-group quantile:

> `q̂⁽ᵍ⁾ = Quantile(s₁⁽ᵍ⁾,…,s_{n⁽ᵍ⁾}⁽ᵍ⁾ ; ⌈(n⁽ᵍ⁾+1)(1−α)⌉ / n⁽ᵍ⁾)`, then `C(x) = {y : s(x,y) ≤ q̂⁽ˣ¹⁾}`

*"This choice of C satisfies (8), as was first documented by Vovk."* Mondrian conformal prediction is the general form: a **taxonomy** is a measurable map from examples to categories, and validity holds within each category *provided the data is exchangeable within each category*. **SECONDARY** (Vovk, *Conditional validity of inductive conformal predictors*, arXiv:1209.2673; and the eight-way U/T/O/L/OL/TL/TO conditional-validity taxonomy — described in secondary sources, primary not opened).

**The cost, and it is the binding one for us. DERIVED:** per-group validity needs per-group calibration. From §3.3, ±5 points of slack needs n⁽ᵍ⁾ ≈ 102 **per group**. Over a 3,625-key space that is ~370,000 labelled bindings — impossible. **Therefore: do not stratify by key. Stratify by a small, defensible taxonomy** — §9.3 proposes four categories, which needs ~408 labelled items, which is achievable.

### 4.5 Conformal Risk Control — Angelopoulos, Bates, Fisch, Lei & Schuster

arXiv:2208.02814, **ICLR 2024**, v1 2022-08-04 → v4 2025-06-13, code at `github.com/aangelopoulos/conformal-risk`. **VERIFIED-AT-SOURCE** (arXiv abstract page). Abstract verbatim:

> "We extend conformal prediction to control the expected value of any monotone loss function. The algorithm generalizes split conformal prediction together with its coverage guarantee. Like conformal prediction, the conformal risk control procedure is tight up to an 𝒪(1/n) factor."

**Why we need it and plain conformal is not enough.** Coverage is a 0/1 loss on one item. Our actual object is a *filing* with thousands of cells, and the loss we care about is "fraction of key-bindings wrong in this filing" or "at least one materially wrong binding in this filing." Those are monotone losses, not label coverage. CRC controls them and keeps the finite-sample guarantee. **This, not PASC, is the right primitive for a per-filing risk statement.**

### 4.6 Learn-then-Test — Angelopoulos, Bates, Candès, Jordan & Lei

arXiv:2110.01052, v1 2021-10-03 → v5 2022-09-29, code at `github.com/aangelopoulos/ltt`. **VERIFIED-AT-SOURCE** (arXiv abstract page). Reframes risk control as **multiple hypothesis testing** over a grid of configurations, giving finite-sample guarantees *without model refitting* and — critically — **for non-monotone risks**, which CRC cannot handle.

**Honest gap:** the abstract page did not state whether LTT needs i.i.d. or the weaker exchangeability. **UNVERIFIED — I did not open the full paper.** Assume i.i.d. until checked; the FWER-control machinery is generally stated under i.i.d.

**Why we need it:** the moment L2 has **two** knobs — an abstention threshold λ₁ and a set-size threshold λ₂ — and you tune both on the same calibration data, you have done multiple testing and plain split conformal no longer covers you. LTT is the correct instrument for tuning the pair.

---

## PART 5 — CONFORMAL FOR LLMs AND FOR STRUCTURED / IE OUTPUTS

### 5.1 Conformal Language Modeling — Quach, Fisch, Schuster, Yala, Sohn, Jaakkola & Barzilay

arXiv:2306.10193, **comment field reads exactly "ICLR 2024"**; v1 2023-06-16 → v2 2024-06-01. **VERIFIED-AT-SOURCE** (arXiv API). Calibrates two things jointly: a **stopping rule** (when to stop sampling) and a **rejection rule** (which candidates to drop), guaranteeing that the returned *set* of generations contains at least one acceptable answer with high probability.

**Where it fits:** conceptually L2, if L2 ever samples multiple candidate extractions. **Where it stops — and this is decisive:** it guarantees *the set contains an acceptable answer*. It does **not** tell you which. For key-binding that is the wrong shape: we need "this cell binds to key k, or I abstain," not "one of these five keys is right." **REJECT for L2's core. Note it if we ever add candidate generation.**

### 5.2 Conformal factuality — Mohri & Hashimoto, ICML 2024

*Language Models with Conformal Factuality Guarantees*, PMLR **v235, pp. 36029–36047**, 2024. **VERIFIED-AT-SOURCE** (PMLR proceedings page). Abstract verbatim, in part:

> "conformal prediction in language models corresponds to a back-off algorithm that provides high probability correctness guarantees by progressively making LM outputs less specific (and expanding the associated uncertainty sets). This approach applies to any black-box LM and requires very few human-annotated samples. Evaluations … show that our approach can provide 80-90% correctness guarantees while retaining the majority of the LM's original output."

**Why this is the most architecturally interesting paper in my lane.** The uncertainty set is the **entailment set** of the output, and the abstention mechanism is not a refusal — it is **back-off to a less specific claim that is still true**. That is a third option between PASS and UNCHECKED, and the brief's L5 vocabulary does not currently have it. §13.

**Where it stops:** requires an entailment/specificity ordering over outputs. For a numeric cell there is a natural one (exact value → bounded interval → order of magnitude → "present"); for a *key* there is one only if we build a key hierarchy (sheet → table → column-group → field). That is real work, and it is exactly the work L1 is already doing.

### 5.3 The closest real precedent to our task — Rombach & Mehdiyev, IJDAR 2026

*Beyond Accuracy: Understanding Model Confidence in Key Information Extraction with Conformal Prediction*, **International Journal on Document Analysis and Recognition (IJDAR)**, DOI `10.1007/s10032-026-00572-y`. **SECONDARY — the Springer page redirects to an auth endpoint and I could not open the full text; title, authors, journal, DOI and the abstract-level numbers below come from the Springer landing metadata surfaced in search, not from the article PDF.**

Reported results, with the denominators I could recover:
- Split conformal on **fine-tuned multimodal transformers**, held-out calibration set, **entity-level** prediction sets.
- **98.3% marginal coverage at α = 0.02** on unseen receipts.
- **70% of predictions are high-confidence singletons.**
- *"highly structured fields such as dates and prices yield small, singleton sets with near-perfect reliability, whereas rare or semantically ambiguous fields such as tips or generic keywords produce larger sets and lower coverage."*

**This is the single most useful empirical anchor in the lane.** It is the same problem shape as ours (document → field key → value, with a fixed schema), it is refereed, and it hands us the singleton rate that §9.4 needs. **It also independently reproduces our structural finding**: structured fields are easy and near-deterministic; the residual difficulty concentrates in semantically ambiguous fields. That is the boundary the whole product is about.

**Where it stops:** receipts, not protected regulated workbooks; and 98.3% coverage at α=0.02 is exactly-as-advertised marginal coverage, not per-field coverage. And I have not read the article.

### 5.4 The impossibility result — and why I re-derived it rather than cite it

`When Can Conformal Risk Control Certify LLM Outputs? Bounds, Impossibility, and Adaptation for Structured Generation`, arXiv:2606.29054, published 2026-06-27, cs.LG, v1 only, no journal_ref, no comments — **sole author Varun Kotte, the same author as PASC**. **VERIFIED-AT-SOURCE** (arXiv API).

Its claim: when base risk μ exceeds target α, *"any distribution-free method must abstain on at least ((μ−α)/(1−α)) examples"*, with reported certification rates of **47% for NER and 40% for QA** only once α is relaxed to **0.30–0.40**, and α=0.10 "uncertifiable" for those tasks.

**I do not cite this paper. I derived the bound independently, and it is elementary. DERIVED:**

Let the predictor err on event `E` with `P(E) = μ`. A selective policy accepts `A` with abstention rate `r = 1 − P(A)`. If the abstention signal carries no information about `E` (the worst case, which is what "distribution-free" buys you), the adversary puts errors on accepted items first:

```
P(E ∩ A) ≥ μ − r
```

Requiring selective risk `P(E ∩ A) / P(A) ≤ α`:

```
(μ − r)/(1 − r) ≤ α
⟺  μ − α ≤ r(1 − α)
⟺  r ≥ (μ − α)/(1 − α)
```

Numerically checked — at `r = r_min` the selective risk equals α exactly, for (μ,α) = (0.2,0.05), (0.3,0.1), (0.5,0.05):

| base risk μ | α=0.01 | α=0.05 | α=0.10 |
|---:|---:|---:|---:|
| 0.05 | 4.0% | — | — |
| 0.10 | 9.1% | 5.3% | — |
| 0.20 | 19.2% | 15.8% | 11.1% |
| 0.30 | 29.3% | 26.3% | 22.2% |
| 0.50 | 49.5% | 47.4% | 44.4% |
| **1.00** | **100%** | **100%** | **100%** |

**Two things follow, and both are load-bearing.**

1. **It is a worst-case bound, tight only when the abstention score is uninformative about correctness.** That makes it a *design test*, not a doom statement: it says our nonconformity score must be genuinely informative about key-binding correctness, or abstention degenerates to refusing everything. Good news — this is measurable on our own data.
2. **§9.5 applies it to the architecture's own measured number, and the answer is bad.**

Because I derived it, we own it. No dependency on an unreviewed preprint.

---

## PART 6 — JOINT COVERAGE ACROSS A PIPELINE, REBUILT WITHOUT PASC

Our pipeline is genuinely multi-stage: **parse → locate → bind key → normalise value**. An error at any stage is an error. Three options.

### 6.1 Independent per-stage conformal — WRONG, and known to be wrong

Calibrate each stage at 1−α. Joint coverage is not controlled and empirically collapses. Even PASC's own (suspect) table has independent CP at 0.865 against a 0.90 target, and 0.53 at K=6.

### 6.2 Bonferroni — correct, conservative, one line

Run each stage at `α/K`. By the union bound `P(any stage misses) ≤ Σ α/K = α`. **This is provably valid and needs no new paper.** It costs set size, and the cost is mild: at K=4 and α=0.05 you calibrate each stage at 0.0125, which by §3.3's Beta law needs a somewhat larger n but nothing exotic.

### 6.3 The max-score reduction — true, one line, and NOT novel to PASC

Define the joint score `S = max_k s_k`. Compute `q̂` = the `⌈(n+1)(1−α)⌉/n` quantile of the calibration `S` values. Then:

```
P(S_test ≤ q̂) ≥ 1 − α
⟺  P( ∀k : s_k(x_test, y_k,test) ≤ q̂ ) ≥ 1 − α
```

The first line is **Theorem 1 applied to the scalar S**. The second is the definition of max. That is the entire proof. PASC's Theorem 6 states exactly this:

> "If (X₁,Y₁),…,(X_{n+1},Y_{n+1}) are exchangeable, then for q̂ defined by Equation 1: ℙ(⋂_{k=1}^K {s_k(x_{n+1},y_{k,n+1}) ≤ q̂}) ≥ 1−α."

**VERIFIED-AT-SOURCE.** The theorem is correct. It is also a special case of a **named, pre-existing class**.

**The refereed anchor to cite instead. VERIFIED-AT-SOURCE / SECONDARY:** Dheur, Fontana, Estievenart, Desobry & Ben Taieb, *A Unified Comparative Study with Generalized Conformity Scores for Multi-Output Conformal Regression*, **arXiv:2501.10533, ICML 2025, PMLR v267** (`proceedings.mlr.press/v267/dheur25a.html`; OpenReview `G8R3ni0MI4`; 32 tabular datasets). Their taxonomy names five classes of multi-output conformal method — **statistically corrected, maximum nonconformity, copula-based, ellipsoidal, density-based**. The max-score reduction is the *maximum nonconformity* class. **SECONDARY on the five-class taxonomy** (from the survey description; I did not open the ICML PDF); VERIFIED-AT-SOURCE on the paper's existence, venue and volume.

**The requirement everyone glosses over, and it is our real constraint:** the max-score reduction needs **per-stage ground truth on every calibration item**. PASC's own algorithm states it — `for (x_i, {y_k,i}) in D_cal: run pipeline to obtain per-stage outputs and scores s_k,i`. **VERIFIED-AT-SOURCE.** So a calibration filing must be annotated at *parse*, *locate*, *bind* and *normalise* — four labels per cell, not one. That multiplies annotation cost fourfold and it is the reason §12 recommends starting with a single stage.

### 6.4 Recommendation

**Use Bonferroni for v1.** It is valid, needs no new machinery, costs a little set size, and cannot be attacked. **Add the max-score reduction only when per-stage labels exist**, and cite Dheur et al. and the one-line proof, never PASC.

---

## PART 7 — THE PAPER THAT SHOULD CHANGE THE UX

`Conformal Tradeoffs: Operational Profiles Beyond Coverage`, **arXiv:2602.18045v3**, Petrus H. Zwart, published 2026-02-20, at **v3** (revised twice). **VERIFIED-AT-SOURCE** (arXiv API, full abstract). Abstract, in the part that matters:

> "Conformal prediction gives exact finite-sample coverage guarantees under exchangeability, but deployed systems are judged by more than coverage alone. … stakeholders also care about deployment-facing quantities such as **commitment frequency, deferral, and decisive error exposure**. These are not determined by coverage: **calibration choices with similar coverage can still induce materially different operational profiles**."

It contributes **SSBC (Small-Sample Beta Correction)** — inverting the Beta/Beta-Binomial law of §3.3 to map a user request `(α*, δ)` to the least conservative calibration grid point with **calibration-conditional PAC semantics** — and **Calibrate-and-Audit**, which fixes the rule on calibration data and then uses an **independent audit split** to estimate a region×class label table from which deployment KPIs follow by projection.

**Why this lands directly on ARCHITECTURE Part 4.** The brief's one design commitment is *"The headline is always a coverage fraction."* Zwart's result is that **a coverage fraction does not determine the operational profile** — two calibrations with the same coverage can defer at very different rates and expose very different decisive-error rates. The commitment is right in spirit (no green tick) and **underspecified in fact**. The headline needs to be a triple: **coverage · deferral rate · decisive error exposure**.

**Warrant caution:** single author, arXiv-only, no journal_ref. But it is at v3, the author is a real scientist (Lawrence Berkeley National Laboratory — **SECONDARY, from the author's public identity, not verified at source**), and — decisively — **SSBC is just the inverse of the Beta law I independently reproduced in §3.3.** We can implement it without depending on the paper. **EVALUATE, implement independently, cite as motivation.**

---

## PART 8 — LIBRARIES: LICENCE, ACTIVITY, AND WHETHER THEY TAKE A CUSTOM SCORE

All rows **VERIFIED-AT-SOURCE** against `api.github.com/repos/...` on 10 Aug 2026, except the capability columns where noted.

| Library | Licence | ★ | Forks | Last push | Archived | Custom nonconformity? | Mondrian / class-cond.? |
|---|---|---:|---:|---|---|---|---|
| **MAPIE** `scikit-learn-contrib/MAPIE` | **BSD-3-Clause** | 1,578 | 148 | **2026-08-05** | no | **Yes** — `conformity_score=` accepts `"lac"/"top_k"/"aps"/"raps"` or a subclass of `BaseClassificationScore` ᴬ | "Conditional Conformal Prediction" section in v1 docs ᴬ |
| **crepes** `henrikbostrom/crepes` | **BSD-3-Clause** | 581 | 46 | 2026-07-08 | no | **Yes** — *"users can employ their own implementations for difficulty estimates, non-conformity scores, and Mondrian categories"* ᴮ | **Yes, first-class** — `MondrianCategorizer`, Mondrian classifiers/regressors/predictive systems ᴮ |
| **TorchCP** `ml-stat-Sustech/TorchCP` | **LGPL-3.0 ⚠** | 475 | 51 | **2026-08-05** | no | Yes — LAC, APS, SAPS, RAPS, KNN, Margin ᴮ | **Yes** — class-conditional/Mondrian, Cluster, **Weighted (covariate shift)** ᴮ |
| **puncc** `deel-ai/puncc` | **MIT** ᶜ | 402 | 19 | 2026-07-10 | no | Yes (per README) — **UNVERIFIED in detail** | UNVERIFIED |
| **nonconformist** `donlnz/nonconformist` | MIT | 478 | 98 | **2021-03-20** | no | Yes | Yes (Mondrian) |
| **Fortuna** `awslabs/fortuna` | Apache-2.0 | 929 | 54 | 2025-04-23 | **ARCHIVED ⚠** | — | — |
| **venn-abers** `ip200/venn-abers` | MIT | 207 | 17 | 2026-05-08 | no | n/a (calibration, not sets) | n/a |

ᴬ MAPIE capability: **SECONDARY**, from `mapie.readthedocs.io` v1.2.0 docs surfaced in search; the theoretical-description page 404'd on both `/stable/` and `/latest/`, so I did not read the score definitions off MAPIE's own page.
ᴮ crepes / TorchCP capabilities: **VERIFIED-AT-SOURCE** from each repo's `README.md` via `raw.githubusercontent.com`.
ᶜ puncc licence: the GitHub API returns `license: null` and `/license` 404s (there is a `LICENSES/` directory whose only child is an empty `headers` dir). **I confirmed MIT by opening `pyproject.toml`: `license = { text = "MIT" }` plus the classifier `"License :: OSI Approved :: MIT License"`. VERIFIED-AT-SOURCE.** Note the repo does not ship a root LICENSE file — flag this to whoever does licence review.

**Two decisions fall straight out.**

1. **TorchCP is LGPL-3.0. ⚠** For a product that may ship as a hosted service this is probably fine, but if any part is ever distributed as a binary or embedded, LGPL imposes relinking/source obligations that BSD/MIT do not. **Do not make TorchCP a core dependency without a licence decision.** MAPIE (BSD-3) and crepes (BSD-3) carry no such condition.
2. **nonconformist is dead** (no push since 2021-03-20, five years) and **Fortuna is archived** by AWS. Neither should be adopted.

**Recommendation: crepes for the calibration core, MAPIE for the sklearn-shaped surface.** crepes wins on the two things we actually need — a genuinely pluggable nonconformity function and first-class Mondrian categories, which is how §9.3's taxonomy gets implemented. Both are BSD-3.

**Also relevant, and it may be the most valuable single library feature in this lane:** MAPIE ships an **`OnlineMartingaleTest`** — a conformal test martingale that converts each new observation to a conformal p-value and accumulates evidence against exchangeability, **rejecting when the martingale exceeds `1/test_level`**, with false-alarm probability controlled by `test_level`. Documented at `contrib.scikit-learn.org/MAPIE/1.4.0/generated/exchangeability_testing/...`. **SECONDARY** (docs page surfaced in search, page itself not opened). This is the instrument §11.2 is built on.

---

## PART 9 — THE DESIGN: L2 KEY-BINDING ABSTENTION, CONCRETE

### 9.1 First, the measurement that repositions L2 — and shrinks it

**ARCHITECTURE L2 says: "conformal prediction on the key-binding step … abstain when it is not a singleton", with a hard guard rejecting any key not in L1's schema.** Before designing that, I asked whether the key-binding step is a prediction problem at all.

**Measured on the real FME workbook, today, with `openpyxl`. All numbers DERIVED by me, method stated.**

The blank template, 10 sheets, 9 of 10 protected:

| Quantity | Value |
|---|---:|
| Non-empty cells | 3,740 |
| String (label) cells | 1,249 |
| Distinct label strings | 488 |
| Formula-valued cells (openpyxl, expanded) | 504 |
| Data-validation objects | **35** |
| **Unlocked (fillable) cells in used ranges** | **3,755** |

> **Denominator note, so this does not read as a contradiction of the brief.** RND-BRIEF §4.3 reports 6,757 cells / 494 distinct strings / 854 label instances / 294 formulas. My 3,740 counts **non-empty** cells only; the brief appears to count the full used range including empty styled cells. My 504 formula cells counts openpyxl's **expanded** formulas; the brief's 294 counts raw `<f>` elements in the OOXML, and shared formulas are stored once over a range. **Both are right under their own definitions.** The one number that matches exactly is **35 data validations**, which is reassuring. I am not correcting §4.3; I am measuring something slightly different and saying which.

**Now the decisive test — is the key determined by geometry?** Three candidate key functions over the same 3,755 unlocked cells:

| Key function | Cells under an ambiguous key | % |
|---|---:|---:|
| **(sheet, nearest-label-above, nearest-label-left)** — the "semantic" key | 1,749 of 1,953 that have both labels | **89.6%** |
| **(sheet, column, header-row anchor, ordinal offset below header)** — the geometric key | 154 of 3,755 | **4.10%** |
| **(sheet, row, column)** — the address key | 0 of 3,755 | **0.00%** |

Distinct geometric keys: **3,625**; only **24** of them map to more than one cell.

And the reason the semantic key fails is not semantics — it is **structural repetition**. The worst collisions are all fixed-size tables:

```
216x  sheet='3. Portfolio'  above='NA'                                left='NA'
100x  sheet='3. Portfolio'  above='Nature of "X"'                     left='NA'
100x  sheet='3. Portfolio'  above='Amount Invested (USD Million) "AI"' left='NA'
100x  sheet='4. Investors'  above='Funds raised (USD Million)'         left='NA'
```

Those are 100-row portfolio/investor tables. The label pair is genuinely identical across the 100 rows; the **row ordinal** disambiguates completely, and the row ordinal is not a prediction — it is arithmetic.

Also measured: **52.0%** of unlocked cells have both a label above and a label to the left; **46.8%** have only one; **1.2%** (46 cells) have neither.

> **Finding. DERIVED, mine, 10 Aug 2026.** *On the prescribed FME workbook, the map from cell to template key is deterministic from template geometry: 0 of 3,755 unlocked cells are ambiguous under the address key, and 154 (4.10%) under a header-anchored key that generalises across row counts. There is no learning problem here.*

**What this means for L2.** The brief's hard guard — *"any key not in L1's induced schema is rejected deterministically"* — is not a guard on a model's output. **On the native workbook it is the whole answer.** Running a model to predict something L1 already computes, then conformalising the model, then abstaining, would be an elaborate way to reintroduce uncertainty that the artifact does not contain. It would also be exactly the failure the brief warns about in §2.4: *where a deterministic oracle exists, the oracle is the answer and no model is warranted.*

### 9.2 So where does conformal abstention actually belong?

Four populations, and only these four, where the key binding is genuinely uncertain:

| Population | Why the key is uncertain | Est. share of the work |
|---|---|---|
| **P1 — cross-document binding** | A value in an attached PDF (valuation report, bank statement, auditor's letter) must be bound to a template key. No geometry connects them. | The real target |
| **P2 — template-version drift** | Filing submitted on an older template whose geometry does not match the current L1 schema. RND-BRIEF §4.2: **23.1% of circulars amend an earlier instrument**, so version drift is the normal case, not the exception. | Recurring |
| **P3 — filer deviation** | Inserted rows, renamed labels, merged cells, a table run past its 100-row allowance. Breaks the geometric key. | Unknown — **UNVERIFIED**, needs real filings to measure |
| **P4 — free-text fields** | Reg 119(3)(e) rationale, complaint narratives, AML-CFT explanations. There may be no key at all. | Small but high-stakes |

**Design consequence, and it is a simplification:** L2's conformal layer runs **only on P1–P4**, and every cell it does not touch is settled by L1 lookup with a *deterministic* provenance stamp. That makes the calibration set small enough to build, and it makes the coverage declaration sharper — the report can say "3,601 of 3,755 cells bound deterministically from template geometry; 154 bound by model under conformal abstention at α=0.05" instead of putting a probabilistic hedge on the entire workbook.

### 9.3 The nonconformity score, and the calibration set

**Unit of prediction.** One **binding decision**: a located value `v` in a source `d` at position `p`, and a candidate template key `k ∈ 𝒦` where `𝒦` is L1's induced key set (|𝒦| = 3,625 for this template, and this is a *hard* restriction — the guard).

**Score.** Start with RAPS over the constrained key set, not APS: |𝒦| is large and the tail is long, which is the exact condition RAPS was built for.

```python
# L2 key-binding nonconformity. Score convention: LARGER = WORSE (A&B step 2).
#
#   f(v, p, d) -> probability vector over K, renormalised over L1's key set ONLY.
#   Keys outside L1's schema get mass 0 by construction -- the hard guard is in the
#   support of the distribution, not a post-hoc filter.

def raps_score(probs, key_idx, lam, k_reg):
    order = np.argsort(probs)[::-1]
    csum  = np.cumsum(probs[order])
    rank  = int(np.where(order == key_idx)[0][0])          # 0-indexed
    return csum[rank] + lam * max(0, (rank + 1) - k_reg)   # APS mass + tail penalty

# calibration
cal_scores = np.array([raps_score(p_i, y_i, lam, k_reg) for p_i, y_i in cal])
n = len(cal_scores)
qhat = np.quantile(cal_scores, np.ceil((n + 1) * (1 - alpha)) / n, method="higher")

# deployment
def predict_set(probs):
    return {k for k in range(len(probs)) if raps_score(probs, k, lam, k_reg) <= qhat}
```

**Mondrian taxonomy — four categories, not 3,625.** From §4.4, per-category validity needs ~102 items per category for ±5 points. Four categories → **~408 labelled bindings**, achievable. Proposed taxonomy (this is a design choice, not a measurement):

| Category | Definition | Why it is its own category |
|---|---|---|
| `NUMERIC_TABLE` | value lands in a repeated table column | Rombach & Mehdiyev: structured fields → near-perfect singletons |
| `SCALAR_HEADER` | one-off named field on Introduction/Summary | Different error profile; no ordinal to key on |
| `CATEGORICAL` | key is one of the 35 data-validation vocabularies | Closed vocabulary — should be the easiest |
| `FREE_TEXT` | P4 above | Expect large sets; expect to abstain most of the time, and *say so* |

Implement with crepes' `MondrianCategorizer`.

**The calibration set — this is the honest part, stated here and dissected in §10.** It is a set of `(source document, located value, TRUE template key)` triples over P1–P4, **constructed by our team** by filling templates correctly and attaching plausible source documents. It is not a sample of filed returns. Filed returns are not public. RND-BRIEF §9.2 already names this as *"the design's largest structural weakness."* It is.

**Exchangeability unit — and the brief does not currently get this right.** The template has 3,755 fillable cells. It is extremely tempting to treat one filled workbook as 3,755 calibration points and declare `n = 3,755`. **That is wrong and it would inflate every guarantee we quote.** Cells within one workbook share a filer, a period, a reporting convention, a template version and — if a filer misunderstands a definition — a correlated error. They are not exchangeable with each other.

> **Rule for the build: the exchangeable unit is the FILING, not the cell.** If we have F distinct filings, the effective n for any statement quantified over filings is F, not 3,755·F. To make per-cell statements at all, use **conformal risk control** (§4.5) with a per-filing loss — e.g. *fraction of bindings wrong in this filing* — which is exactly the monotone-loss shape CRC controls. Report `n = F` next to every number.

This single rule is the difference between a defensible instrument and a number that dissolves under the first competent question.

### 9.4 What "abstain unless the prediction set is a singleton" costs

**It does not cost coverage. It changes which guarantee you hold.** Three quantities, and conflating them is how a compliance product ships a false claim.

Let `C(x)` be the conformal set, `A = {|C(x)| = 1}` the accept event, `c = P(A)`.

**(i) The unconditional silent-error rate — the one that matters for "can I rely on this system's silence?"**

```
P(accept AND wrong)  =  P(|C(x)|=1, Y ∉ C(x))  ≤  P(Y ∉ C(x))  ≤  α
```

**This is the product claim, and it survives the singleton rule untouched.** Emitting a binding only on singletons can never *increase* the rate of silently-accepted wrong bindings, because every accepted-and-wrong case is already a coverage miss. **DERIVED, elementary.**

**(ii) The conditional error rate — the one a user will read off the screen.**

```
P(wrong | accept)  =  P(E ∩ A)/P(A)  ≤  α / c
```

**DERIVED.** Tabulated:

| α ↓ / accept rate → | 95% | 90% | 80% | **70%** | 50% |
|---|---:|---:|---:|---:|---:|
| 0.01 | 1.05% | 1.11% | 1.25% | **1.43%** | 2.00% |
| 0.02 | 2.11% | 2.22% | 2.50% | **2.86%** | 4.00% |
| 0.05 | 5.26% | 5.56% | 6.25% | **7.14%** | 10.00% |
| 0.10 | 10.53% | 11.11% | 12.50% | **14.29%** | 20.00% |

At the only measured document-IE singleton rate I could find — **70%**, Rombach & Mehdiyev (SECONDARY) — running α = 0.05 gives a **worst-case 7.14%** conditional error on accepted bindings. Not 5%. **If the UI says "5%" anywhere near an accepted binding, it is wrong.**

**(iii) Abstention rate = 1 − c.** Conformal does **not** control this. Nothing in Theorem 1 bounds `c` from below; a valid procedure may abstain on everything. This is precisely Zwart's point (§7) and precisely the degenerate case Phillips et al.'s Table A3 caption describes.

> **Therefore: `c` must be a separately certified quantity.** The right instrument is a **Clopper–Pearson lower bound on acceptance** on a held-out audit split, run alongside the risk bound. `Selective Conformal Risk Control` (Xu, Guo & Wei, arXiv:2512.12844, v1 2025-12-14 → v2 2026-04-27, **VERIFIED-AT-SOURCE**) is the framework that does risk and selection jointly: a two-stage procedure with λ₁ for sample selection and λ₂ for set size, in variants **SCRC-T** (transductive, *"preserves exchangeability by computing thresholds jointly over calibration and test samples, offering exact finite-sample guarantees"*) and **SCRC-I** (calibration-only, PAC-style, cheaper). This is the correct primitive for "abstain unless singleton" done properly.

**Empty sets are a gift.** With a LAC-style score, `C(x) = ∅` occurs when no key clears the threshold. That is an unambiguous abstention with no extra machinery, and it should map straight to **`UNCHECKED(source unreadable)`** or a new reason code in L5's closed vocabulary. Do not suppress empty sets; they are the layer working.

### 9.5 The number that decides whether any of this runs

**ARCHITECTURE Part 1, measured fact 5: "Extraction gets 100% of digits and 0% of the key."**

Feed that into §5.4's bound. Base risk on key-binding μ = 1.0:

```
r ≥ (1.0 − α)/(1 − α) = 1.0   for every α ∈ [0,1)
```

> **At the architecture's own measured key accuracy, a distribution-free selective predictor must abstain on 100% of bindings, at every risk target.** DERIVED, from an ARCHITECTURE number I did not re-verify (**SECONDARY** on μ; the bound is mine).

This is not an argument against conformal. It is conformal doing its job: **pricing the extractor honestly instead of hiding it.** But it means the ordering in the brief's residency plan is wrong. Building L2's conformal layer before the extractor's key accuracy is measured produces a layer that abstains on everything and looks broken.

**The bound also gives a pre-registerable go/no-go, which is what this program's own discipline demands:**

> **L2 gate, written before running.** Measure key-binding accuracy on P1 (cross-document binding) over the constructed calibration set. **If μ > 0.30, do not build the conformal layer** — at α=0.05 it would force ≥26.3% abstention purely from base error, before any adaptivity, and the honest product is "L2 is deterministic-only; cross-document binding is UNCHECKED(requires judgment)." **If μ ≤ 0.10**, conformal buys real selectivity (≥5.3% forced abstention at α=0.05) and is worth building. Between 0.10 and 0.30, build it but ship the abstention rate as the headline number, not coverage.

Cost to run the gate: the same afternoon as experiment 9.1 in the brief.

---

## PART 10 — THE HONEST SECTION: WHAT A SYNTHETIC CALIBRATION SET DOES TO THE GUARANTEE

This is the part the lane was commissioned for. I will not soften it.

### 10.1 Exchangeability with *what*?

Theorem 1 does not say "the calibration data must be representative." It says `(Z₁,…,Z_n, Z_test)` is exchangeable — **the joint distribution of the calibration points together with the test point is permutation-invariant.**

Our situation:

- `Z₁,…,Z_n` = binding decisions on workbooks **our team filled**, with source documents **our team wrote or selected**, labelled with keys **our team assigned**.
- `Z_test` = a binding decision on a workbook **an FME filed**, from source documents **an auditor or administrator produced**, in a real reporting period, under commercial and supervisory pressure.

**Is the sequence permutation-invariant?** Swap our 47th synthetic filing with a real one from a Category III AIF. Does the joint distribution stay the same? **No.** We would have to believe our team independently reproduced the distribution of filer behaviour: which fields get misread, which conventions differ between administrators, what an actual valuation report looks like, how a filer handles a definition they do not understand, what a 100-row portfolio table looks like when a fund holds 137 positions.

> **Verdict, stated plainly: exchangeability between a team-constructed calibration set and real filings is FALSE, not merely unverified. The 1−α coverage guarantee, as a statement about real filings, is VOID.**

Not weakened. Void — because the guarantee is *conditional on an assumption we know to be false*.

Anyone who quotes "95% coverage" from a synthetic calibration set to a regulator has done exactly what this whole program exists to prevent: produced clean, confident, well-formed output that is wrong, with nothing in the output to distinguish it from a correct answer. **This is RND-BRIEF §4.4's self-demonstration, committed a third time, in the layer that was supposed to prevent it.**

### 10.2 But "void" is not the end of the sentence — the gap is bounded

The exact result. Barber, Candès, Ramdas & Tibshirani, **"Conformal prediction beyond exchangeability," *Annals of Statistics* 51(2):816–845, April 2023**, DOI `10.1214/23-AOS2276`, arXiv:2202.13415. **VERIFIED-AT-SOURCE — I extracted the PDF and read the statements off the page.**

Definition, verbatim:

> "define the coverage gap as the loss in coverage compared to what is achieved under exchangeability. For example, in split conformal prediction, Coverage gap = (1 − α) − P{Y_{n+1} ∈ Ĉ_n(X_{n+1})}"

With `Z = (Z₁,…,Z_{n+1})` and `Zⁱ` the sequence with the test point swapped into position i:

> `Zⁱ = (Z₁, …, Z_{i−1}, Z_{n+1}, Z_{i+1}, …, Z_n, Z_i)`   … (2)

**Equation (3), verbatim:**

```
                    Σⁿᵢ₌₁ wᵢ · d_TV(Z, Zⁱ)
Coverage gap  ≤    ─────────────────────────
                       1 + Σⁿᵢ₌₁ wᵢ
```

> "where d_TV denotes the total variation distance between distributions. Notably, we do not make any assumption on the joint distribution of the n + 1 points—but, of course, the result will be meaningful only if we can select fixed (non-data-dependent) weights wᵢ such that this upper bound is likely to be small"

**Equation (4) — the stronger, and for us the *operational*, form:**

```
                    Σⁿᵢ₌₁ wᵢ · d_TV(R(Z), R(Zⁱ))
Coverage gap  ≤    ────────────────────────────────
                        1 + Σⁿᵢ₌₁ wᵢ
```

where `R(Z)` is the vector of **residuals / nonconformity scores**. The authors note (4) is *"strictly stronger than (3), since the total variation distance between any function applied to each of Z and Zⁱ cannot be larger than d_TV(Z, Zⁱ) itself—and in many cases, the bound in (4) may be substantially tighter."*

And **Lemma 1**, verbatim:

> "If Z₁, …, Z_{n+1} are independent, then d_TV(Z, Zⁱ) ≤ 2 d_TV(Zᵢ, Z_{n+1}) − d_TV(Zᵢ, Z_{n+1})² ≤ 2 d_TV(Zᵢ, Z_{n+1})."

They also note the result applies to *standard* conformal: *"for wᵢ ≡ 1 and with a symmetric algorithm, the proposed weighted methods will reduce to the usual conformal … Thus, the result (3) also quantifies the degradation in coverage of standard methods in nonexchangeable settings."*

**What this buys us. DERIVED from the above:** with uniform weights `wᵢ ≡ 1`, the denominator is `n+1`, so

```
Coverage gap  ≤  (n/(n+1)) · d̄  ≈  d̄        where d̄ = mean_i d_TV(Z, Zⁱ)
```

and under independence, `d̄ ≤ 2 · d_TV(synthetic item, real item)`. So:

> **If our synthetic calibration items differ from real filings by total variation d in the score-generating distribution, we lose at most ≈2d of coverage. Running α = 0.05 with d = 0.10 means true coverage ≥ 0.75, not 0.95.**

### 10.3 The part that is genuinely load-bearing: the gap is on the SCORES

Equation (4) says the bound depends on `d_TV(R(Z), R(Zⁱ))` — total variation between **nonconformity-score vectors**, not between raw filings.

**This is the difference between an impossible requirement and a hard one.** We do not need our synthetic filings to be indistinguishable from real filings *in every respect*. Our fake FME does not need a plausible name, a realistic AUM, or a convincing complaints history. We need **the distribution of the model's binding-difficulty scores** on synthetic items to match that on real items.

That is still a strong requirement, and here is why it is the one that will bite: our team will construct calibration items **that we know how to fill**. We will unconsciously generate items the extractor finds easy. The score distribution will be shifted toward low nonconformity, `q̂` will be too small, prediction sets will be too tight, and **coverage on real filings will be below target in exactly the direction that produces silent false confidence.** This is not a hypothetical failure mode; it is the predictable one, and it is the same mechanism as RND-BRIEF §4.4's two self-inflicted false negatives.

### 10.4 Bottom line, in the form it must appear in the product

> **`d_TV` between our synthetic score distribution and the real one is UNKNOWN and UNBOUNDED without real filings. Therefore any coverage number computed on the synthetic calibration set is a coverage number ABOUT THE SYNTHETIC POPULATION, and about nothing else.**

The permitted sentence, and it is the only one:

> *"Under conformal calibration on **N = \_\_ synthetic filings constructed by this team on template version \<hash\>**, the key-binding layer covers the true key in ≥95% of bindings **drawn from that same constructed population**. No coverage claim is made for filed returns. The gap is bounded by twice the total-variation distance between the two score distributions (Barber et al., Ann. Statist. 2023, eq. 4); that distance is currently **unmeasured**, because filed returns are not public."*

That sentence is defensible in front of a regulator, a statistician, and a hostile judge. "95% coverage" is not.

**And note what that sentence *is*: it is the product.** A system whose headline output is a declared boundary, and whose calibration layer declares its own boundary in the same grammar, is coherent. A system that hides the calibration boundary while advertising the verdict boundary is not.

---

## PART 11 — THE FALLBACK, WHICH IS STILL WORTH BUILDING

Three components. Each is buildable now, each survives the guarantee being void, and each *increases* in value the moment any real filings arrive.

### 11.1 Weighted conformal under covariate shift — the principled repair

**Tibshirani, Foygel Barber, Candès & Ramdas, "Conformal Prediction Under Covariate Shift," NeurIPS 2019** (Advances in NeurIPS 32; arXiv:1904.06019). **SECONDARY** — I confirmed authors/venue/arXiv id via the NeurIPS proceedings listing; I did not open the paper. It shows a *weighted* conformal procedure gives valid distribution-free intervals when test and calibration covariate distributions differ but the **likelihood ratio is known or estimable from a large set of unlabelled test covariates**, under a notion of **weighted exchangeability**.

**Why this fits our situation almost exactly.**

- Covariate shift means `P(X)` changes but `P(Y|X)` does not.
- For key-binding on a **fixed template version**, `P(Y|X)` is close to a point mass: given the source context and the template, the correct key is determined. §9.1 measured this — it is a deterministic function of geometry on the native workbook, and for cross-document binding it is determined by the semantics of the field, not by who filed it.
- **So the shift between synthetic and real filings is plausibly *pure covariate shift* — the very case this method handles.** That is a real argument, not a hope. It is also **UNVERIFIED**, and it is testable the moment we hold real filings.
- **The likelihood ratio needs only UNLABELLED real filings.** Train a discriminator to separate synthetic-calibration contexts from real-filing contexts; its odds are the weights. **We do not need ground-truth key labels on real filings to do this.** That is the crucial asymmetry: labels are what we cannot get; raw filings are merely hard to get.

**Implementation: TorchCP ships a Weighted predictor for covariate shift** (**VERIFIED-AT-SOURCE**, README) — subject to the LGPL note in §8. The weighted quantile is ~20 lines regardless.

### 11.2 A conformal test martingale — the component that makes the system refuse to certify

This is the piece I would build first, because it converts an unverifiable assumption into a **monitored, falsifiable** one, and it is the same move the rest of the architecture makes everywhere else.

A conformal test martingale converts each new observation into a conformal p-value and accumulates evidence against exchangeability; **when the martingale exceeds `1/test_level`, exchangeability is rejected with false-alarm probability controlled by `test_level`.** MAPIE ships this as `OnlineMartingaleTest` (**SECONDARY** — docs at `contrib.scikit-learn.org/MAPIE/1.4.0/generated/exchangeability_testing/...`, page not opened). The underlying theory is Vovk's — *Testing exchangeability on-line* (ICML 2003), and the **second edition of Vovk, Gammerman & Shafer, *Algorithmic Learning in a Random World*, Springer 2022**, whose three new chapters cover conformal predictive distributions, **the efficiency of testing the randomness assumption via conformal prediction**, and **protecting ML algorithms against changes in the data distribution** (**SECONDARY**, from the publisher's description; I did not open the book).

**How it enters the product.** Every real filing processed produces conformity scores. Feed them into the martingale in arrival order. Then:

| Martingale state | System behaviour |
|---|---|
| below threshold | L2 emits bindings with its stated (still synthetic-population) coverage, and says so |
| **exceeds `1/test_level`** | **L2 stops emitting model-bound facts.** Every P1–P4 binding becomes `UNCHECKED(calibration no longer exchangeable with input)` |

> **This is the single most defensible thing in my lane.** It is a system that *detects that its own guarantee has stopped applying and withdraws the claim*, rather than continuing to emit confident output. It is the direct answer to RND-BRIEF §4.4 — a deterministic program producing clean, confident, wrong output with nothing to distinguish it from a correct answer. Here there *is* something to distinguish it, and the something is a martingale.

**Add a new reason code to L5's closed vocabulary.** The current six (*no oracle exists · requires counterparty data · requires judgment · source unreadable · rule ambiguous · predicate not yet synthesised*) cannot express this. Add:

> **`calibration not exchangeable with input`** — the abstention layer's own guarantee has lapsed for this artifact.

### 11.3 Audited Conformal Prediction — the upgrade path once a few real labels exist

`Audited Conformal Prediction for Classification under Unknown Distribution Shift`, **arXiv:2606.14909**, Yanfei Zhou, Rizal Fathony, Nam H. Nguyen, **Matteo Sesia** (co-author of APS), published 2026-06-12. **VERIFIED-AT-SOURCE** (arXiv API, full abstract). Abstract, verbatim in part:

> "We propose Audited Conformal Prediction (ACP), a method that leverages a **small labeled dataset from the target population** to train an auxiliary audit model identifying inputs where the legacy model is likely to fail. By integrating the audit model's outputs into the conformal prediction framework, ACP produces prediction sets that guarantee marginal coverage while achieving substantially higher conditional coverage in practice … one targeting marginal coverage with improved conditional performance, the other providing explicit group-conditional coverage guarantees"

**This is our exact configuration**: a large synthetic calibration set plus a *small* number of real labelled bindings — which is a plausible ask of one cooperative FME or of IFSCA itself (RND-BRIEF §9.6 already proposes contacting the Division of Investment Funds). Multi-author, includes a serious conformal researcher. v1, no venue yet — **EVALUATE, do not treat as settled.**

### 11.4 What the fallback stack delivers, honestly

| Component | Guarantee it carries | Buildable now? |
|---|---|---|
| Split conformal on synthetic calibration | 1−α **over the synthetic population only** | Yes |
| Barber et al. gap bound | coverage ≥ 1−α−2d, **d unmeasured** | Yes (the statement) |
| Conformal test martingale | detects and **declares** exchangeability failure | **Yes — build first** |
| Weighted conformal (covariate shift) | restores validity **if** shift is pure covariate shift | Needs unlabelled real filings |
| ACP | marginal + group-conditional coverage on the real population | Needs a **small** labelled real set |
| SCRC + Clopper–Pearson on acceptance | selective risk **and** a certified acceptance floor | Yes |

**Nothing in this stack requires us to pretend the synthetic calibration set is a sample of real filings.** That is the test it had to pass.

---

## PART 12 — SELECTIVE PREDICTION WITHOUT CONFORMAL, AND WHY NONE OF IT SUFFICES ALONE

| Method | What it is | Measured status | Verdict for L2 |
|---|---|---|---|
| **Semantic entropy** — Farquhar, Kossen, Kuhn & Gal, ***Nature* 630(8017):625–630, 2024**, DOI `10.1038/s41586-024-07421-0`, **CC BY** | Entropy over *semantic clusters* of sampled generations rather than token sequences; detects "confabulations". Includes a discrete variant needing no token probabilities | **VERIFIED-AT-SOURCE** on title/authors/venue/pages/DOI/licence (Oxford ORA record). **The headline AUROC numbers I could NOT verify** — the Nature page redirects to an auth endpoint and the authors' own blog states only *"better scores than all baselines across a range of datasets and models"* with no figures. **UNVERIFIED on all numerics.** | Useful **as a score fed into conformal**, never as the abstention rule. No finite-sample guarantee. And see the next row. |
| **Entropy alone** | thresholding any entropy signal | Phillips et al. (§2.2): **"confidently wrong regime, in which models produce low-entropy hallucinations"**; *"Many answers, both correct and hallucinated, collapse to SE = 0"*; *"strong AUROC does not imply reliable selective prediction at strict safety thresholds"*. 3 benchmarks, 4 families, 3B–8B. **VERIFIED-AT-SOURCE** | **KILLED as a standalone rule.** Constrained decoding puts us permanently in the low-entropy regime. |
| **P(True)** — ask the model whether its own answer is true (Kadavath et al. 2022, cited by Phillips et al.) | self-evaluation probability | Phillips et al. class it with "correctness-based methods … learn a supervised factuality signal from model activations" and find entropy and correctness signals *"only moderately correlated"*, so combinations beat either. **SECONDARY** (via Phillips et al.'s citation; Kadavath not opened) | Useful **as a second feature**. Complementary to entropy — that complementarity is the paper's main practical result. |
| **Self-consistency** | sample k times, take the majority | No finite-sample guarantee; and RND-BRIEF §3.2 already records that retry is what `pass^k` penalises by construction | Do not build. Its cost is `k` model calls against ARCHITECTURE Part 3's "two model calls, both short." |
| **Verbalised confidence** | ask the model for a number | Consistently miscalibrated; *"verbalized confidence is often miscalibrated, a problem that post-training and RLHF can further exacerbate"*; reward models *"exhibit a bias toward high-confidence responses, regardless of their actual correctness."* **SECONDARY** — I did not open a primary calibration study with numbers. **I could not verify a specific ECE figure and will not quote one.** | **Do not use.** And note this is ARCHITECTURE fact 7's *"do not rely on model self-confidence for abstention"*, independently supported. |

**The synthesis, and it is the design:** conformal is a **wrapper**, not a competitor. A&B state it exactly — *"conformal prediction can be seen as a method for taking any heuristic notion of uncertainty from any model and converting it to a rigorous one."* **VERIFIED-AT-SOURCE.** So the right L2 is: **combine softmax mass + semantic entropy + a correctness probe into one scalar heuristic, then conformalise that scalar.** Phillips et al. give the evidence that the combination beats either component; conformal gives the finite-sample guarantee that neither has. Nothing is lost by combining and the guarantee is unaffected by how bad the heuristic is — only the *set size* depends on that.

---

## PART 13 — WHERE EACH ASSET FITS L0–L7, AND WHERE IT STOPS

| Asset | Fits | Where it stops |
|---|---|---|
| **crepes** (BSD-3, 581★, 2026-07-08) | **L2** calibration core. Pluggable nonconformity + `MondrianCategorizer` for §9.3's four categories | Not deep-learning-native; you supply the probability vectors |
| **MAPIE** (BSD-3, 1,578★, 2026-08-05) | **L2** sklearn-shaped surface; **L2/L7** `OnlineMartingaleTest` (§11.2) | Score-definition docs 404'd for me; capability claims are SECONDARY |
| **TorchCP** (**LGPL-3.0**, 475★, 2026-08-05) | **L2** if PyTorch-native; ships the **Weighted** predictor for §11.1 | **Licence decision required before it becomes a core dependency** |
| **puncc** (MIT via pyproject, 402★) | L2 alternative | No root LICENSE file; capability unverified |
| **nonconformist** / **Fortuna** | — | **Dead (2021) / ARCHIVED. Do not adopt.** |
| **Conformal Risk Control** (ICLR 2024, code) | **L2 + L5.** Per-filing monotone loss — the right object when the unit is a filing, not a cell | Monotone losses only; non-monotone needs LTT |
| **Learn-then-Test** (code) | **L2 + L4.** Tuning λ₁ (abstain) and λ₂ (set size) jointly without invalidating the guarantee. **Also the natural formal frame for L4's three-test gate**, which is multiple testing over candidate predicates whether or not it is currently written that way | i.i.d. assumption **UNVERIFIED**; grid-based |
| **SCRC** (arXiv:2512.12844, v2) | **L2.** Joint selective-risk + set-size control — the correct primitive for "abstain unless singleton" | Two public datasets; not refereed at a named venue |
| **ACP** (arXiv:2606.14909) | **L2 upgrade** once a small real labelled set exists (§11.3) | v1, unrefereed |
| **Conformal factuality** (ICML 2024) | **L2 + L5.** Back-off to a less specific true claim = a third verdict between PASS and UNCHECKED | Needs a specificity ordering; for keys that means a key hierarchy L1 must emit |
| **Conformal Tradeoffs / SSBC** (arXiv:2602.18045v3) | **L7 + UX.** Coverage · deferral · decisive-error-exposure as the reported triple; audit split → KPI table | Single author, arXiv-only; implement independently from the Beta law |
| **Barber et al. 2023** (*Ann. Statist.*) | **L2 + L7.** The gap bound is the *sentence* the attestation must carry (§10.4) | The bound is unmeasurable without real filings — that is the point, not a defect |
| **Tibshirani et al. 2019** (NeurIPS) | **L2.** Weighted conformal repair | Pure covariate shift only — assumption **UNVERIFIED** for us |
| **Vovk, Gammerman & Shafer, 2nd ed. 2022** | **L2 theory + L7.** Conformal testing of the randomness assumption | Book; SECONDARY |
| **Rombach & Mehdiyev, IJDAR 2026** | **L2.** The empirical anchor: 98.3% coverage at α=0.02, **70% singletons** | Receipts, not workbooks; **I could not open the article** |
| **Phillips et al., arXiv:2603.21172** | **L2.** Kills the entropy-threshold design; supplies E-AURC/TCE as the honest metrics | 3B–8B models, short-form QA |
| **Farquhar et al., *Nature* 2024** | **L2.** A component score inside the conformal wrapper | **Numerics UNVERIFIED**; do not quote an AUROC |
| **PASC (arXiv:2605.18812)** | Would have been L2 | **Do not cite.** §2.1 |
| **Kotte, arXiv:2606.29054** | Would have been L2 | **Do not cite.** The bound is re-derived in §5.4 and is ours |

---

## PART 14 — WHAT THIS CHANGES ABOUT THE DESIGN

Seven changes. The first three are structural.

**1. L2 shrinks, and the shrinkage is a win.** Key-binding on the native prescribed workbook is a **deterministic lookup against L1**, measured today: 0 of 3,755 unlocked cells ambiguous under the address key, 154 (4.10%) under a header-anchored key, versus 89.6% under a naive label-pair key. The conformal layer applies only to **P1 cross-document binding, P2 template-version drift, P3 filer deviation, P4 free text**. This makes the calibration set small enough to actually build, and it makes the report sharper: *"3,601 of 3,755 bound deterministically; 154 bound by model under conformal abstention at α=0.05"* beats a probabilistic hedge smeared over the whole workbook. **It also removes an instance of the brief's own §2.4 failure — running a model where a deterministic oracle already exists.**

**2. Run the L2 gate before building L2.** Measure key-binding accuracy μ on P1 first. **μ > 0.30 → do not build the conformal layer**; at α=0.05 the forced-abstention floor `(μ−α)/(1−α)` already exceeds 26.3%, and the honest product is "cross-document binding is UNCHECKED." At the architecture's own stated μ = 1.0 ("0% of the key"), the floor is **100% at every α**. This gate is pre-registerable, costs an afternoon, and sits alongside the brief's 9.1 in the same queue.

**3. The exchangeable unit is the FILING, not the cell.** Treating 3,755 cells as 3,755 calibration points inflates every quoted guarantee, because cells within a workbook share a filer, a period, a convention and correlated errors. Every conformal number must carry `n = F` (number of distinct filings). Per-cell statements go through **conformal risk control** with a per-filing monotone loss. Without this rule, L2's numbers dissolve under the first competent question — and this program has already been burned twice by exactly that.

**4. The UX headline must be a triple, not a fraction.** ARCHITECTURE Part 4 commits to *"the headline is always a coverage fraction."* Zwart's result is that **coverage does not determine the operational profile** — same coverage, materially different deferral and decisive-error rates. Report **coverage · deferral rate · decisive error exposure**. And nowhere may the UI print α next to an accepted binding: at a 70% singleton rate, α=0.05 means a worst-case **7.14%** conditional error on accepted bindings, not 5%.

**5. L5's closed vocabulary needs two more reason codes.** Add **`calibration not exchangeable with input`** (fired by the conformal test martingale, §11.2) and a **back-off** verdict between PASS and UNCHECKED (Mohri & Hashimoto: a less specific claim that is still true — "this value belongs to the Portfolio table, exact key not resolved"). The current six reasons cannot express either, and both are things the system will genuinely need to say.

**6. Two of the brief's "load-bearing" citations are one unreviewed source.** PASC (arXiv:2605.18812) and the CRC-certification impossibility paper (arXiv:2606.29054) share a sole author with 7 arXiv papers, 6 posted in 2026, one refereed venue among them and that a workshop. PASC's Table 1 is internally inconsistent by ≥0.033 in mean set size, and its "tightness" claim inverts against its own numbers. **Both papers must be struck from §6.1 as authority.** The useful content of each is reconstructible in one line and I have reconstructed both (§5.4, §6.3) — so nothing is lost except a footnote we could not have defended.

**7. Build the conformal test martingale FIRST — before the conformal predictor.** It is the only component whose value does not depend on the calibration set being valid, and it is the component most aligned with the product thesis: a system that detects that its own guarantee has lapsed and withdraws the claim. Everything else in L2 is a coverage number about a synthetic population. The martingale is the thing that stops that number from being quoted after it has stopped meaning anything.

**And one thing that does not change.** The brief's instinct to put conformal at L2 is right. The reason is not that it makes the extractor better — it does not — but that **it is the only mechanism in the whole architecture that converts a model's confidence into a quantity with a finite-sample, distribution-free, model-agnostic meaning**, and therefore the only one that can be *declared* rather than asserted. That is the same move L4 makes for predicates and L7 makes for the report. L2's conformal layer is the abstention layer's version of the program's one idea.

---

## PART 15 — OPEN QUESTIONS, RANKED

1. **What is μ, the key-binding base error rate on P1 (cross-document binding)?** Everything in §9.5 hangs on it, and ARCHITECTURE's "0% of the key" would forbid the layer entirely. **Until measured, L2's conformal layer is a hypothesis in exactly the sense L3 is.**
2. **Can we obtain ANY real filed FME returns — even unlabelled?** Unlabelled ones unlock weighted conformal (§11.1); a small labelled set unlocks ACP (§11.3). This is a *sourcing* question, not a research question, and it is worth more than any further reading. RND-BRIEF §9.6's email to the Division of Investment Funds should ask for this explicitly.
3. **Is the synthetic→real shift pure covariate shift?** If `P(key | context)` is stable and only `P(context)` moves, §11.1 restores validity exactly. Plausible for a fixed template, **UNVERIFIED**, and testable the day question 2 is answered.
4. **What is the singleton rate on OUR task?** Rombach & Mehdiyev's 70% is on receipts (**and I could not open the article**). Our number could be far higher — structured template cells should be easy — or far lower for P4 free text. It is the denominator of the entire §9.4 table.
5. **Does Learn-then-Test require i.i.d. or exchangeability?** **UNVERIFIED** — I did not open arXiv:2110.01052 beyond its abstract page. It matters because LTT is how λ₁ and λ₂ get tuned without invalidating everything.
6. **Should L4's three-test predicate gate be reframed as Learn-then-Test?** L4 selects a configuration (which predicates to admit) by testing many candidates on shared data. That is multiple hypothesis testing, and mutation score / degeneracy / FFR are three risks over a grid. **If nobody has applied LTT to test-suite admission, that is a genuinely publishable connection** — and it is a bigger idea than anything else in my lane. Not verified as novel; I did not search for it.
7. **Can the RAPS regularisation parameters (λ, k_reg) be chosen without a second data split?** Standard practice tunes them on calibration data, which strictly speaking invalidates the guarantee. LTT is the clean answer; I did not confirm anyone has done it for RAPS specifically.
8. **What are semantic entropy's actual AUROC numbers?** The *Nature* paper is CC BY but the page redirects to an auth endpoint for me. Someone should open the PDF and record the figures with denominators before any of it reaches a slide.
