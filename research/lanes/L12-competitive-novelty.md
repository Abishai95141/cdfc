# L12 — COMPETITIVE MAP, THE UNOCCUPIED CLAIM, AND THE ADVERSARIAL DEFENCE

**Lane run 10 Aug 2026.** Purpose: find who already sells something adjacent, establish precisely what is
unoccupied, and harden the claim so a judge cannot restate it as something that already exists.

---

## PART 0 — METHOD, WARRANT KEY, AND THE COVERAGE DENOMINATOR (read this before any absence claim below)

### 0.1 Warrant key used throughout

| Mark | Meaning |
|---|---|
| **ⓥ VERIFIED-AT-SOURCE** | I hold the raw artifact: file downloaded and parsed locally, PDF extracted with `pdftotext` and grepped, JSON schema parsed with `python3`, or the fetch returned verbatim quoted text from the primary URL. |
| **ⓟ PRIMARY-PAGE-READ** | The primary URL was fetched and read, and the fetch returned a *summary* rather than verbatim text. Positive statements from ⓟ are reliable; **absence statements from ⓟ mean only "not present on the page as read", never "the vendor does not do it".** |
| **ⓢ SECONDARY** | A credible third party describes it; I did not open the primary. |
| **ⓤ UNVERIFIED / NOT-CHECKED** | Stated, could not be confirmed in this lane. |

### 0.2 The instrument, and its failure — declare this before believing any absence in this lane

- I opened the two authoritative context files first (`RND-BRIEF.md`, `ARCHITECTURE.md`).
- `WebSearch` **exhausted its session budget at 200/200 calls** partway through this lane (the budget is
  shared across all lanes running in this session). Roughly six searches were mine; the rest were other lanes'.
- Fallback interface: `WebFetch` against **`lite.duckduckgo.com/lite/?q=…`**. This worked for three queries
  and then began returning an **image CAPTCHA** ("Select all squares containing a duck"). **I did not solve
  it and will not** — CAPTCHA bypass is prohibited. So the fallback search interface degraded to unusable.
- Remaining instrument: **direct `WebFetch` of primary URLs I could name**, the **arXiv API**
  (`export.arxiv.org/api/query`), **`curl` + local parsing**, and a **local re-read of the IFSCA register
  capture** in `/Users/abishaikc/Gift/research/probe/t24.json`.

**Consequence, stated plainly: this lane's coverage of the vendor list is partial, and the gap is large.**

| Named in the lane brief | Opened at a primary URL this lane | Not checked |
|---|---|---|
| Reg-reporting | Suade ⓟ, Regnology (supervisory hub) ⓟ, Confluence ⓟ, FundApps ⓢ(search snippet only) | AxiomSL/Nasdaq (**timeout**), Wolters Kluwer OneSumX (**HTTP 403**), Vermeg, Corlytics (**HTTP 403**), Ascent, Clausematch, Hexanika, Gresham |
| Fund/NAV | FundGuard ⓢ, Milestone pControl ⓥ(full validation catalogue), Clearwater ⓟ | SS&C, Northern Trust, BNY |
| Audit/assurance | MindBridge ⓟ, DataSnipper ⓟ, Fieldguide ⓟ, Numeric ⓟ | Trullion, Caseware IDEA, Klarity, AuditBoard, Basis, Bluecopa, **all Big Four in-house tools (EY Helix, Deloitte Omnia, KPMG Clara, PwC Aura/Halo)** |
| LLM eval | LangSmith ⓥ (docs index + 3 pages), Braintrust ⓟ ×2, promptfoo ⓟ, DeepEval ⓟ, Guardrails Hub ⓟ | Patronus AI, Arize Phoenix, Evidently, Giskard, Ragas |
| Data quality | Great Expectations ⓟ, Anomalo ⓟ, Monte Carlo ⓟ, Deequ ⓥ, dbt-coverage ⓥ | Soda, Sifflet, Bigeye, GX Cloud specifically |
| India / GIFT | IFSCA sandbox register ⓥ (63 rows, local capture), Lawrbit ⓟ, Gieom ⓟ | Signzy, ZignSec, Compliance Kart, the other 58 |

**So: every "nobody does X" in this document is scoped to the opened set, and the scope is written next to
the claim.** Where I could not check, the answer is NOT-CHECKED, not "no".

### 0.3 arXiv API — what its `all:` field actually searches

The arXiv API `all:` prefix searches **metadata** (title, abstract, authors, comments, journal-ref) — **not
full text**. Every arXiv absence below therefore reads: *"no arXiv record whose metadata contains both terms."*
A paper could apply metamorphic testing to a fund return in §5 without either phrase in its abstract and this
instrument would miss it.

**Positive control, run:** `all:"metamorphic testing"` alone → **`opensearch:totalResults` = 186**, first hits
"Evaluating Human Trajectory Prediction with Metamorphic Testing", "Metamorphic Testing with the Rashomon Set",
"Metamorphic Testing of a Deep Learning based Forecaster". ⓥ The query mechanism works; the zeroes below are
zeroes in a working instrument.

---

## PART 1 — THE TWO QUESTIONS, AND WHY THEY ARE THE RIGHT TWO

Every category was asked the same pair:

> **Q1.** Does the product publish, **PER RULE**, the measured rate at which that rule fires on **known-clean**
> inputs?
> **Q2.** Does the product declare, as a **first-class output**, what it **could NOT check** and **why**?

These are the right two because they are the only two that the architecture's L4 and L5 make *structurally
impossible to fake*. A vendor can always claim "high accuracy" and "comprehensive coverage". Neither claim
survives being asked for a number per rule with a denominator, or a machine-readable residue.

**Scoring convention used in the tables:** **NO** = opened the page, the quantity is absent. **NO ⓟ** = same,
but the read was a summary, so treat as "absent from the page as read". **PARTIAL** = something adjacent
exists and I say exactly how it falls short. **NOT-CHECKED** = I never opened it.

---

## PART 2 — THE COMPETITIVE MAP, CATEGORY BY CATEGORY

### 2.1 Regulatory reporting quality and controls

| Vendor | What it is | Q1 per-rule measured FPR on clean inputs | Q2 first-class "could not check" | Warrant |
|---|---|---|---|---|
| **Suade Labs** — `https://suade.org/solutions/` | End-to-end reg-reporting automation, "real-time validation… before submission" | **NO** — page carries only ISO-27001 / ISO-9001 / SOC 2 certifications, no product accuracy metric | **NO** | ⓟ |
| **Regnology (incl. Vizor supervisory side)** — `https://www.regnology.net/en/solutions/for-regulators/regnology-supervisory-hub/` | SupTech for central banks; "robust data quality control", "technical validation rules" | **NO** — no rule counts, no rates, claims are qualitative | **NO** | ⓟ |
| Regnology Reporting Hub "2,000+ pre-configured data controls and 10,000+ validation rules" | — | — | — | **ⓤ** — this figure came from a *search-result summary*, not from a page I opened. **Do not quote it.** |
| **Confluence (Unity NXT / Omnia)** — `https://www.confluence.com/solutions/regulatory-reporting/` | Fund regulatory filings: Form N-PORT, Form PF, Form 13F, Form ADV, AIFMD, KIID, APRA SRS, SFC. **"40+ countries", "90+ regimes"**, "up to 90% efficiency boost" | **NO** | **NO** | ⓟ |
| **FundApps** — "850+ pre-coded global rules… 100+ jurisdictions", "every rule is coded, validated, and continuously updated by an in-house regulatory team" | Shareholding-disclosure / position-limit monitoring | **NO** found | **NO** found | **ⓢ** (search-result summary of fundapps.co; the site itself was not opened this lane) |
| **AxiomSL / Adenza (Nasdaq)** | — | **NOT-CHECKED** (fetch timed out at 60 s) | **NOT-CHECKED** | ⓤ |
| **Wolters Kluwer OneSumX** | — | **NOT-CHECKED** (HTTP 403) | **NOT-CHECKED** | ⓤ |
| **Corlytics** | — | **NOT-CHECKED** (HTTP 403) | **NOT-CHECKED** | ⓤ |
| **Vermeg · Ascent · Clausematch · Hexanika · Gresham** | — | **NOT-CHECKED** | **NOT-CHECKED** | ⓤ |

**The category's own regulator is the best evidence, and it is not a vendor.**

> **European Banking Authority, press release 12 June 2025:** validation rules are deactivated **"either for
> incorrectness or for triggering IT problems"**, and competent authorities are told that **"data submitted in
> accordance with these ITS should not be formally validated against the set of deactivated rules."** ⓥ
> `https://www.eba.europa.eu/publications-and-media/press-releases/eba-issues-revised-list-validation-rules-supervisory-reporting`

Read this carefully, because it cuts both ways.

- **For us:** the body that *authors* the rules for European supervisory reporting publicly concedes, on a
  **quarterly** cadence, that some of its own rules are **wrong**. That is the strongest possible external
  confirmation that per-rule correctness is a real, live, unsolved quantity and not a novelty we invented.
- **Against a naive novelty claim:** the EBA already publishes *something* about rule quality. But what it
  publishes is a **binary kill-list with a two-value reason code** (incorrect / IT problem), published by the
  *rule author* after the fact. It is **not a measured rate**, it is **not per-rule on a clean corpus**, and it
  is **not attached to any individual firm's verdict**. It tells you a rule was withdrawn; it never tells you
  how often a *live* rule cries wolf.

**Category verdict: Q1 = NO across every vendor opened (4 opened / 12 named). Q2 = NO across every vendor
opened.** The one adjacent artifact is a regulator's binary deactivation list, not a rate.

*Where this fits L0–L7:* the EBA deactivation list is the **existence proof for L4**. It is what an FFR gate
looks like when you have no instrument: you ship the rule, discover it is wrong in production, and withdraw it.
**Where it stops:** post-hoc, binary, no rate, no clean corpus, author-side only.

---

### 2.2 Fund and NAV specific

| Vendor | What it is | Q1 | Q2 | Warrant |
|---|---|---|---|---|
| **Milestone Group pControl Oversight** — `https://www.milestonegroup.com/solutions/nav-oversight-validations` | The most complete public validation catalogue I found anywhere in this lane. Enumerated verbatim: *Data Integrity Checks · Standard Validations Library · Bottom Up Validations · Top Down Validations · Multi-Exception Clearance · Auto Clearance of Exceptions*; controls: *Expected vs Actual NAV · NAV Movement Analysis · Share Class Divergence · Benchmark and Sister Fund Divergence · Maker/Checker Review*; top-down: *Fund/Portfolio · Expected Price · Expected Fee · Share Class · Clean Price Analysis · Backup NAV*; bottom-up: *Holding · Transaction · Corporate Actions · Account Balance · Units and Capital Flow · Market Data · Data Consistency* | **NO** — "no stated false-positive or exception rates for any validation" | **NO** — "does not declare what the oversight cannot check" | ⓥ (list returned verbatim) |
| **FundGuard** | Cloud shadow-NAV running continuously alongside primary accounting; ML-based NAV discrepancy/exception detection; contingent NAV with Ultimus | **NO** found | **NO** found — material "focuses on what the platform can do rather than detailing its limitations" | ⓢ |
| **Clearwater Analytics** — `https://cwan.com/platform/` | Investment accounting/reconciliation; only quantified claim on the page is **"95% reduction in reporting time"** | **NO** | **NO** | ⓟ |
| **SS&C · Northern Trust · BNY oversight tooling** | — | **NOT-CHECKED** | **NOT-CHECKED** | ⓤ |

**This is the single most important table in the lane**, because Milestone's catalogue is the *direct*
competitor to our predicate registry — same artifact class (a fund's NAV and its supporting data), same shape
(a library of validations run over it), same user (oversight of an outsourced administrator). And the two
columns that would make it a coverage-declaring system are **both empty**.

Note also the structural difference in what "oversight" means: pControl's headline controls are
**divergence-based** — *Expected vs Actual NAV*, *Share Class Divergence*, *Benchmark and Sister Fund
Divergence*, *Backup NAV Calculations*. That is **an independent recomputation compared against the filed
number**. It is the *strongest possible oracle* — and it is available only because a NAV is recomputable from
holdings and prices. It says nothing about the 7 predicates in §4.3 of the brief that have no oracle at all
(*is the disclosed portfolio composition accurate*, *is the valuation appropriate*, *is the reg 119(3)(e)
rationale adequate*).

*Where this fits L0–L7:* pControl's top-down "Expected NAV" is an **L5 oracle-bearing predicate** of exactly
the kind we would admit, and its bottom-up list is a ready-made **candidate predicate vocabulary for L3 to
aim at** (a free prior on what a fund-domain expert thinks is checkable). **Where it stops:** no L4 (no
measured error rate, no admission gate), no L5 UNCHECKED class, no L6, no L7 attestation, and it is sold into
the *administrator/asset-owner* oversight seat, not the *regulator-facing filing* seat.

---

### 2.3 Audit and assurance AI

| Vendor | What it is | Q1 | Q2 | Warrant |
|---|---|---|---|---|
| **MindBridge** — `https://www.mindbridge.ai/` | "Statistical models, business rules, and unsupervised machine learning"; **"Full Population Analysis"**; "Explainable AI"; "Understand why risks are identified through transparent, evidence-based reasoning" | **NO** — "no numerical denominators, false positive rates, precision/recall statistics" | **NO** — "no explicit declarations of analytical limitations" | ⓟ |
| **DataSnipper** — `https://www.datasnipper.com/` | Agentic audit automation inside Excel; extraction, tests of detail, evidence tracing. Only number on the page: **"85% Time saved in high volume testing scenarios"** (FGMK case study) | **NO** | **NO** | ⓟ |
| **Fieldguide** — `https://www.fieldguide.io/` | AI-native audit/advisory; "automate up to 70% of testing"; **"an error rate of less than 1% versus manual processes"** for substantive testing agents; "95% reduction in manual testing time"; "32% reduction in engagement hours" | **PARTIAL — and it is the closest any vendor got.** A single aggregate error-rate claim exists. But it is **one number for the whole agent, not per check**; it has **no denominator**, **no described corpus**, **no clean/dirty split**, and it is **benchmarked against "manual processes"**, i.e. against another unmeasured baseline | **NO** | ⓟ |
| **Numeric** — `https://www.numeric.io/` | Close automation, flux analysis, transaction monitors. Numbers: "Automate 90%+ of your bank recs", "80% flux first drafts written by AI", "33% reduction in close timeline" | **NO** — all quantities are automation volume / time saved | **NO** | ⓟ |
| **Trullion · Caseware IDEA · Klarity · AuditBoard · Basis · Bluecopa · Big Four in-house (Helix/Omnia/Clara/Aura)** | — | **NOT-CHECKED** | **NOT-CHECKED** | ⓤ |

**The category's own standard is the real competitor, and it is 40 years old.** This is the objection a judge
will actually raise, so it gets a primary source.

**ASA 705 (compiled, March 2023) — the Australian adoption of ISA 705 (Revised), *Modifications to the Opinion
in the Independent Auditor's Report*.** ⓥ (PDF downloaded from `https://www.auasb.gov.au/media/ulnavf0z/asa705_03-23.pdf`,
extracted with `pdftotext -layout`, quoted from the extraction):

> **¶20.** "When the auditor modifies the opinion on the financial report, the auditor shall, in addition to the
> specific elements required by ASA 700: (a) Amend the heading "Basis for Opinion" required by paragraph 28 of
> ASA 700 to "Basis for Qualified Opinion," "Basis for Adverse Opinion," or "Basis for Disclaimer of Opinion,"
> as appropriate; and (b) **Within this section, include a description of the matter giving rise to the
> modification.**"

> **¶24.** "**If the modification results from an inability to obtain sufficient appropriate audit evidence, the
> auditor shall include in the Basis for Opinion section the reasons for that inability.**"

That is, verbatim, a **required declaration of what could not be checked and why**. It is the strongest
"this already exists" in the entire lane. Its precise limits are in Part 6, Objection 2 — and they are decisive.

*Where this fits L0–L7:* ASA/ISA 705 ¶24 is the **institutional legitimation of L5's UNCHECKED(reason)**. When
a judge asks "who would ever want a panel of things you didn't check", the answer is: *the auditing profession
has mandated exactly that output since ISA 705, and every Big Four partner signs one.* **Where it stops:**
it fires **only on a modified opinion**, it is **English prose per engagement**, it is **not per-predicate**,
it is **not machine-readable**, it **carries no error rate for any procedure**, and no fraction is computed
from it.

---

### 2.4 LLM evaluation and assertion tooling — including the SPADE-in-LangSmith check the lane brief demanded

This is the category where Q1 was most likely to be YES, because SPADE *invented* the metric. The result is
more interesting than a yes or a no.

#### 2.4.1 SPADE, read at source

I downloaded the PVLDB PDF (`https://www.vldb.org/pvldb/vol17/p4173-shankar.pdf`, 1.3 MB), extracted it with
`pdftotext -layout` to 1,055 lines, and grepped it. Everything below is **ⓥ verbatim from that extraction.**

**The FFR definition (Definition 3.2):**
> "**False Failure Rate (FFR)** for a set 𝐹′ is the fraction of examples that 𝐹′ incorrectly evaluates as
> failures (ŷᵢ = 0) when they are actually successful (yᵢ = 1)"

**The admission that stops SPADE being a general instrument — and this sentence is the single most valuable
line in the paper for us:**
> "In practice, **coverage and FFR are impossible to compute since the universe of examples 𝐸 is unknown.** So,
> for now, we assume access to a subset 𝐸′ ⊂ 𝐸 of labeled LLM responses, where 𝐸′ is a manually provided set of
> example runs and may not contain [all failure modes]"

**The size of that labelled set:**
> "each task has only **34 bad (i.e., failure) examples on average**"

**The results, with their denominators:**
> "All three approaches respect the 𝐸′ coverage constraint, but **baseline violates the FFR constraint in 4 out
> of 9 pipelines**. For our workloads, spade_sub opts for approximately **14% fewer assertions** compared to
> baseline and shows a significantly lower FFR, **reducing it by about 21%** relative to baseline. spade_cov
> excludes, on average, about **44% of functions that are not subsumed** by 𝐹′."
> "all **9** LLM pipelines yielded feasible solutions with **𝛼 = 0.6 and 𝜏 = 0.25**."

**What actually shipped, and this is the correction the lane brief asked for:**
> "**With LangChain, we publicly release this component of spade** — which has been subsequently used for over
> **2000 pipelines** across more than 10 sectors like finance, medicine, and IT"

"**this component**" is **Component 1 — candidate assertion generation from prompt-version deltas.** Component 2
(the FFR filtering and ILP selection) is described immediately afterwards as a separate component and is not
what the sentence releases. §2.4 confirms the delivery vehicle:
> "**2.4 Initial Deployment.** To assess the potential of our auto-generated assertions, in **November 2023**, we
> released an **early prototype** of spade's candidate assertion generation framework **via a Streamlit
> application**" — footnote 4: `https://spade-beta.streamlit.app/`

**The finance share of that deployment.** Figure 5 ("Prompts submitted to the spade Streamlit application span
a variety of fields") gives: Others 4.2 · Marketing 4.2 · **Finance 4.2** · Cooking 8.3 · Sports and
Entertainment 8.3 · Education 8.3 · Customer Support 12.5 · Project Management 12.5 · IT and Programming 16.7 ·
Health 20.8. **Every value is an integer multiple of 4.1667% = 1/24**, so the chart's denominator is **24**
(ⓥ for the percentages as printed; **derived/ⓧ** for the inferred denominator of 24). On that reading,
**Finance = 1 of 24 submitted prompts.**

#### 2.4.2 Is SPADE in LangSmith *today* (Aug 2026)? — the check, with its positive control

- I fetched the LangChain docs index **`https://docs.langchain.com/llms.txt`**, which enumerates the doc tree.
  **Positive control: it returned 40+ evaluation-related pages** — `evaluation-concepts`, `evaluation-types`,
  `evaluators`, `llm-as-judge`, `code-evaluator-sdk`, `composite-evaluators-*`, `online-evaluations-*`,
  `audit-evaluator-scores`, `improve-judge-evaluator-feedback`, `create-few-shot-evaluators`, and — notably —
  **`/langsmith/assertions.md`**. The index is real and populated.
- **Searched that index: no "SPADE", no "false failure rate", no "assertion synthesis".** ⓥ
- **`https://docs.langchain.com/langsmith/assertions.md`** ⓟ: assertions are **written by a human during
  review** — *"Assertions turn a reviewer's English-language standards into an automated check. They are short,
  free-form claims about what a correct answer should or shouldn't include."* Auto-generation exists but in a
  different shape: *"LangSmith Engine can auto-propose assertions for production traces flagged as recurring
  issues."* **No FFR anywhere on the page.**
- **`https://docs.langchain.com/langsmith/audit-evaluator-scores.md`** ⓟ: *"LLM-as-a-judge evaluators don't
  always get it right. Because of this, it is often useful for a human to manually audit the scores left by an
  evaluator and correct them where necessary."* — a **correction workflow**, no computed rate.
- **`https://docs.langchain.com/langsmith/improve-judge-evaluator-feedback.md`** ⓟ: **this is the one hit.**
  LangSmith documents an **alignment score**, defined as *"the percentage of examples where the evaluator's
  judgment matches that of the human expert."*

**Verdict on the brief's claim "SPADE shipped in LangSmith":** it must be **QUALIFIED, in three ways at once.**
(i) What shipped publicly with LangChain in Nov 2023 was the **candidate generator**, as a **Streamlit
prototype**, not the FFR-filtered selection; (ii) the "2,000+ pipelines" number attaches to **that generator**,
not to FFR-based admission; (iii) **as of today, LangSmith's documentation contains no false-failure-rate
concept at all** across 40+ evaluation pages. What LangSmith ships instead is a **per-evaluator alignment
score against human labels** — which is agreement, aggregate, computed privately by the developer on their own
data, and never surfaced to whoever consumes the verdict.

#### 2.4.3 The rest of the category

| Tool | Auto-generates checks? | Q1 per-rule measured FPR on clean inputs | Q2 declares what it could not check | Warrant |
|---|---|---|---|---|
| **LangSmith** | Partly — "LangSmith Engine can auto-propose assertions for production traces flagged as recurring issues" | **PARTIAL** — *alignment score* = "percentage of examples where the evaluator's judgment matches that of the human expert". Aggregate agreement, not per-rule FPR on a **clean** corpus; developer-private; not published; **does not gate** whether the evaluator may be used | **NO** | ⓥ/ⓟ |
| **Braintrust** | **Yes** — "Loop… Generate and improve scorers and classifiers"; scorer families = Autoevals, LLM-as-judge, custom code | **NO** — "does not provide information about per-scorer false positive rates or agreement-with-human metrics" | **NO** | ⓟ |
| **promptfoo** — `https://www.promptfoo.dev/docs/configuration/expected-outputs/` | **NO** — "no information about automatic assertion generation" | **NO** — "no mention of false positive rate measurement or reporting for individual assertions". (Deterministic set: equals, contains, regex, is-json, is-sql, javascript, python, levenshtein, rouge-n, bleu…; model-graded: llm-rubric, g-eval, factuality, context-faithfulness…) | **NO** | ⓟ |
| **DeepEval** — `https://deepeval.com/docs/metrics-introduction` | Via G-Eval / DAG authoring | **NO** — reliability is argued by assertion: "research-backed LLM-as-a-Judge (GEval)", "20 million+ daily evaluations", "deterministic metric scores possible (when using DAGMetric)". **"No empirical validation studies, false positive/negative rates, or comparative accuracy data"** | **PARTIAL, and only as a disclaimer:** "We **CANNOT** guarantee that evaluations will work as expected when using a custom model" | ⓟ |
| **Guardrails AI Hub** — `https://guardrailsai.com/hub` | No | **NO** — validators (Ban List, Detect PII, Logic Check, Toxic Language LLM) carry functional descriptions and tags only; **"No section containing performance metrics… appears anywhere on the page"** | **NO** | ⓟ |
| **Patronus AI · Arize Phoenix · Evidently · Giskard · Ragas** | — | **NOT-CHECKED** | **NOT-CHECKED** | ⓤ |

**Category verdict: Q1 = NO everywhere opened except LangSmith's alignment score, which is a different
quantity. Q2 = NO everywhere opened.** And a term-frequency check: **arXiv metadata containing the exact
phrase "false failure rate" → `totalResults` = 2** (arXiv:2602.11305, arXiv:2605.30695), *neither of them
SPADE* (SPADE's abstract says "false failures", not the full phrase). ⓥ The metric is essentially unused
outside its originating paper.

---

### 2.5 Data quality

| Tool | What it is | Q1 | Q2 | Warrant |
|---|---|---|---|---|
| **Great Expectations** — `https://docs.greatexpectations.io/docs/core/introduction/gx_overview` | "a verifiable assertion about data" (Expectation); Validation Results "tell you how your data corresponds to what you expected of it" | **NO** — no per-Expectation FPR | **NO** — no declaration of unchecked conditions | ⓟ |
| **AWS Deequ** — `https://github.com/awslabs/deequ` | **Apache 2.0, 3.6k stars.** README features include **"Automatic suggestion of constraints for large datasets"** and "Anomaly detection on data quality metrics over time" | **NO** — README does not discuss per-constraint false positive rates | **NO** | ⓥ |
| **dbt-coverage** — `https://github.com/slidoapp/dbt-coverage` | **MIT, 241 stars.** "checks your dbt project for missing documentation and tests"; measures **documentation coverage** and **test coverage**; explicitly analogous to `coverage.py` | **NO** | **PARTIAL — the nearest thing to a coverage declaration in this whole lane.** But it measures **presence only**: which columns have a test versus which do not. It "does not measure rule error rates, test quality, or test result accuracy" and attaches **no reason** to an uncovered column | ⓥ |
| **Monte Carlo** — `https://montecarlo.ai/product/` | Data observability; "automatic baseline coverage", "AI-powered rules". Only number: "Reduce downtime by 80% YoY" | **NO** | **NO** — no declared coverage gaps | ⓟ |
| **Anomalo** — `https://www.anomalo.com/` | Agents that "know the difference between noise and something that actually matters" | **NO** — no quantified FP metrics | **NO** — no declared limitations | ⓟ |
| **Soda · Sifflet · Bigeye · GX Cloud** | — | **NOT-CHECKED** | **NOT-CHECKED** | ⓤ |

**The distinction that matters here, and it is easy to blur:** Great Expectations, Deequ and dbt all report
**how the data scored against the rules**. None reports **how the rules scored against known-good data**. GX's
`unexpected_percent` is a property of the dataset, not of the Expectation. This is precisely the inversion the
architecture's L4 performs — and Deequ's automatic constraint suggestion proves the *generation* half is a
solved, non-LLM, Apache-2.0 commodity, which is a useful thing to concede early.

*Where these fit L0–L7:* **GX / pandera / Soda Core / Deequ are the L5 execution substrate — do not rebuild
them.** Deequ's constraint suggestion is a **free non-LLM baseline for L3** that L4 must beat (if a data-profile
suggester passes the qualification gate as often as the model does, L3 gets deleted and nobody loses anything).
dbt-coverage is the **UI precedent for the coverage meter**. **Where they stop:** all assertions are
hand-authored or profile-derived, none carries a measured error rate, none emits a typed residue.

---

### 2.6 Indian RegTech, GIFT City, and the IFSCA sandbox

**Corpus and denominator, measured at source.** I re-read the live capture of the IFSCA public register taken
today by lane L15 (`/Users/abishaikc/Gift/research/probe/t24.json`, `ParentTypeId=24` = *Fintech Sandbox
Entities*). ⓥ **63 rows.** Every field except `Title` is null (that is L15's finding, not a new one), so this
is a **name list** — I can enumerate who is there, not what they do, from the register alone.

**Compliance-adjacent entries: 4 of 63 (6.3%)** by name inspection —
`Compliance Kart Private Limited` · `Lawrbit Lextech India Private Limited` ·
`Gieom Business Solutions Private Limited (FIS-01)` · `Gieom Business Solutions Private Limited (FRS-01)`.
Adjacent-but-different: `Signzy Technologies` and `ZignSec AB` (KYC/onboarding), `Webnyay` (online dispute
resolution), `Vettedcode Technologies` (name suggests code review; unverified). The rest are payments,
tokenisation, insurance, quantum, accelerators, and two banks (`JPMorgan Chase Bank NA`, `Edgeverve`).

| Entity | What it sells | Q1 | Q2 | Warrant |
|---|---|---|---|---|
| **Lawrbit** — `https://www.lawrbit.com/` | Global Compliance Management System; Compliance Audit Management; Risk & Control; Internal Financial Control. Coverage claims: **"Regulatory Intelligence from 70+ countries"**, **"2,000+ Central, States & Municipal Laws"**, **"65,000+ Compliance"**, newsletter over "2,600+ Central, State & Municipal Acts & Rules" | **NO** | **NO** — "does not explicitly state whether Lawrbit… verifies filings… publishes false positive rates… discloses coverage limitations". It is an **obligation-tracking and calendar** product, not a filing verifier | ⓟ |
| **Gieom** — `https://www.gieom.com/` | Risk Central, Digital Blueprint (policy/procedure digitisation), TPRM, BCM, Digital/Video KYC. Frameworks: DORA, UK Operational Resilience, APRA CPS 230, NIST, NIS2, Indian banking regs | **NO** — "does not publish measured rule error rates or coverage declarations" | **NO** | ⓟ |
| **Compliance Kart · Signzy · ZignSec · the other 58** | — | **NOT-CHECKED** | **NOT-CHECKED** | ⓤ |

**Category verdict:** the GIFT sandbox **does** contain regulatory-compliance software vendors — so "nobody at
GIFT does compliance" would be false and a judge from the ecosystem would know it. What it does not contain, in
the two I opened, is **anything that verifies a filed artifact against the template and the regulation and
returns a measured verdict.** Lawrbit tells you *that* an obligation exists and *when* it is due. It does not
open the workbook.

That distinction — **obligation tracking vs artifact verification** — is the sentence to have ready. It is also
the sentence that positions us as complementary to the incumbent rather than competitive with it.

**And the supervisor-side seat is already sold** (from `RND-BRIEF.md` PART 7, ⓞ operator-verified, restated here
because it constrains the go-to-market): **NEC Corporation India, awarded 27 Jan 2026, ₹39,57,36,115.52**, scope
including an RE-facing portal. The entity-facing seat is the one that is open.

---

## PART 3 — THE DIRECT COMBINATION SEARCHES

Each row states the instrument, the query, the result, and the denominator. All arXiv rows are **ⓥ** (I read
the API response).

| Combination we claim | Instrument | Result | Reading |
|---|---|---|---|
| **LLM-synthesised validation rules for regulatory returns** | arXiv API, `all:"regulatory reporting" AND all:"large language model"` | **`totalResults` = 5** | The entire arXiv metadata intersection is 5 papers. Nearest: **RKEFino1** (arXiv:2506.05700, 6 Jun 2025) — a *fine-tuned model* for Digital Regulatory Reporting QA over XBRL/CDM/MOF, plus a Numerical NER task. It **answers questions about** reporting; it does not **synthesise executable checks** for a return. |
| same | arXiv API, `abs:"validation rules" AND abs:"LLM"` | **`totalResults` = 9**, none financial-regulatory (NIDS rules, Linux patches, kernel generation, clinical decision rules, customs tariff classification) | The phrase-pair barely exists, and where it exists it is not our domain. |
| **Metamorphic testing applied to financial reports or fund NAV** | arXiv API, `all:"metamorphic testing" AND all:"financial"` | **`totalResults` = 3** — FHE frameworks (2606.22519), machine translation (2401.00751), zero-knowledge circuits (2411.02077). **All three mention "financial" only as consequence language ("financial losses", "financial and reputational damage").** | **Zero** apply metamorphic testing to a financial report, a fund NAV, or a regulatory filing. |
| same | arXiv API, `all:"metamorphic relation" AND all:"accounting"` | **`totalResults` = 4** — and **two are the real prior art**: **arXiv:2205.04998**, *Metamorphic Testing and Debugging of Tax Preparation Software* (ICSE-SEIS 2023), and **arXiv:2409.16140**, *Metamorphic Debugging for Accountable Software* | **This is the closest published relative of L3+L6 combined, and it must be cited, not hidden.** See Part 4.1. |
| **Metamorphic testing on spreadsheets** | arXiv API, `all:"metamorphic testing" AND all:"spreadsheet"` | **`totalResults` = 0** | Zero in a working instrument (positive control = 186 for the term alone). The *artifact class* is untouched. |
| **Mutation testing on financial rules** | arXiv API, `all:"mutation testing" AND all:"financial"` | **`totalResults` = 2** — a Remix IDE plugin for smart contracts (2603.23441) and a unit-test-generation literature review (2504.20357). Neither concerns financial rules, accounting, or filings | Mutation testing has never been pointed at a financial correctness rule in the arXiv metadata corpus. |
| **Per-rule false-positive publication in a compliance product** | Direct primary fetches, 16 vendor pages across §2.1–§2.6 | **0 of 16 opened pages** publish a per-rule measured FPR. Closest: Fieldguide's undenominated "<1% error rate versus manual processes" | **Absence claim scoped to 16 opened pages; 20+ named vendors not checked.** |
| **Coverage declaration for a compliance verdict** | Same 16 pages + CycloneDX schema + ASA 705 | **0 of 16** vendor pages. Two non-vendor precedents exist and are both outside finance: **CycloneDX `compositions.aggregate`** (software) and **ASA/ISA 705 ¶24** (audit prose) | See Part 4.3 and 4.4. |
| **Measured false-failure rate as a shipped product feature** | LangChain docs index (40+ eval pages) + 5 eval vendors | **Not shipped anywhere I opened.** LangSmith ships *alignment score* instead | The metric exists in one paper and in no product documentation I opened. |

---

## PART 4 — THE NEAREST NEIGHBOURS, RANKED BY HOW DANGEROUS THEY ARE

Ranked by how much of our claim each one takes away.

### 4.1 **PROVE** — arXiv:2607.28218, 30 July 2026 — *eleven days old, and it is our design thesis in another regulated domain*

Zhaohua Lu, Cheng Zheng, Yuanyuan Han, *"Bridging Probabilistic LLMs and Deterministic Statistical Validation:
The PROVE Multi-Agent Framework for Clinical Trial Reporting"*. ⓥ (abstract read at
`https://arxiv.org/abs/2607.28218`, quoted verbatim below.)

> "Large language models (LLMs) can help interpret varied table language and navigate lengthy study documents,
> but they are **not reliable substitutes for programmed statistical checks**. We introduce PROVE… an auditable
> framework that uses optional LLM and retrieval support for table interpretation while **reserving numerical
> and logical decisions for programmed validators**."

> "We evaluated PROVE using **ten replicated synthetic oncology reporting packages**… with **paired clean and
> discrepancy-injected packages; each replicate included 15 randomly injected discrepancies**… **Within the
> implemented rule classes**, all automated PROVE variants achieved perfect classification in the exact-label
> setting. In the label-variation setting, LLM-assisted semantic matching improved overall recall from **0.588
> to 0.993** and overall F1 from **0.735 to 0.996**…"

**What this takes from us.** Read `ARCHITECTURE.md` §Design thesis — *"put the model only where generation is
hard and verification is cheap, adjudicate it with programs"* — and then read PROVE's abstract. They are the
same sentence. As of 30 Jul 2026, **"LLM interprets, programs adjudicate, for a regulatory submission" is no
longer novel.** It is published, in a regulated reporting domain (clinical TFLs for FDA/ICH submission), with
a fault-injection evaluation that is structurally our L4 test 1, and a synthetic paired clean/dirty corpus
that is structurally our §9.2 mitigation — **including the same weakness, which they also carry (synthetic).**

**What it leaves.** Four things, precisely:
1. **No per-check false-failure rate.** They report aggregate recall and F1 over 150 injected discrepancies
   (10 × 15). No rule carries its own number.
2. **No coverage declaration.** The abstract's own hedge — **"Within the implemented rule classes"** — is
   exactly the residue our L5 turns into a typed output. They state it as a caveat in prose; we compute it,
   per field, with a reason code.
3. **No admission gate.** Nothing prevents a validator with a terrible FFR from being in the set.
4. **No metamorphic layer.** Their oracle is *cross-output consistency* (one table must agree with another) —
   powerful, but it is still an oracle-bearing check, and it dies where no second output exists.

**Use it, don't hide it.** In a pitch, PROVE is the best evidence available that the thesis is *right*: an
independent group in a different regulated industry converged on it eleven days ago. Convergence is
corroboration. What it forces is that our claim must be stated as the **gate and the residue**, never as the
architecture.

*Where this fits L0–L7:* PROVE is an existence proof for **L2+L5 together** and a citable precedent for the
whole deterministic-adjudication stance. **Where it stops:** L4 and the L5 UNCHECKED vocabulary and L6.

### 4.2 **Metamorphic Testing and Debugging of Tax Preparation Software** — arXiv:2205.04998, ICSE-SEIS 2023

Tizpaz-Niari, Monjezi, Wagner, Darian, Reed, Trivedi. ⓥ abstract read at source.

> "The key barriers in developing debugging aids for tax preparation systems are the **unavailability of
> explicit specifications and the difficulty of obtaining oracles**… In collaboration with legal and tax
> experts, we **explicated metamorphic relations for a set of challenging properties from various US Internal
> Revenue Services (IRS) publications** including Publication 596 (Earned Income Tax Credit), Schedule 8812…
> and Form 8863… Our tool uncovered several accountability bugs… ranging from non-robust behavior in
> corner-cases (unreliable behavior when tax returns are close to zero) to missing eligibility conditions."

**This is the single closest published precedent for the L3→L6 combination**: metamorphic relations **derived
from statutory publications** and applied to a **regulated financial computation over a filed return**. If a
judge finds one paper, this is the one, and I would rather we cite it first.

**What it leaves.** (a) The relations were **hand-explicated with legal and tax experts** — no model
synthesised them, so our L3 hypothesis is untouched and, if anything, this paper is evidence that
hand-authoring works, i.e. it de-risks the §9.1 kill. (b) No FFR, no mutation score, no admission gate.
(c) No coverage declaration; the abstract reports bugs found, never propositions left unsettled. (d) Different
artifact class: a *tax program*, not a *prescribed reporting workbook*, and no jurisdictional overlap.

*Where this fits L0–L7:* it is the **methodological citation for L6** and the proof that "relations from
statute" is a real technique, not a hopeful analogy. **Where it stops:** manual authorship, no L4, no L5
residue.

### 4.3 **CycloneDX `compositions.aggregate`** — the completeness enum, verified byte-for-byte

I downloaded `https://raw.githubusercontent.com/CycloneDX/specification/master/schema/bom-1.6.schema.json` and
parsed it with `python3`. ⓥ

`aggregate` is a **required** property of `compositions`, described as *"Specifies an aggregate type that
describes how complete a relationship is."* The `aggregateType` enum has **exactly 10 values**, with these
`meta:enum` definitions, verbatim:

```
complete                                  "The relationship is complete. No further relationships including
                                           constituent components, services, or dependencies are known to exist."
incomplete                                "The relationship is incomplete. Additional relationships exist…"
incomplete_first_party_only               "…Only relationships for first-party components… are represented."
incomplete_first_party_proprietary_only   "…limited specifically to those that are proprietary."
incomplete_first_party_opensource_only    "…limited specifically to those that are opensource."
incomplete_third_party_only               "…Only relationships for third-party components…"
incomplete_third_party_proprietary_only   "…"
incomplete_third_party_opensource_only    "…"
unknown                                   "The relationship may be complete or incomplete. This usually signifies
                                           a 'best-effort' … but the completeness is inconclusive."
not_specified                             "The relationship completeness is not specified."   [default]
```

`compositions` attaches to `assemblies`, `dependencies`, `vulnerabilities`, and may carry a `signature` (JSF).

**The brief's claim is CONFIRMED, and it is stronger than stated:** `aggregate` is **required** when a
composition is declared, and the default is `not_specified` — i.e. the standard's authors deliberately made
"I am not telling you how complete this is" an explicit, nameable state rather than a silence. That is the
exact design commitment of our L5.

**What it leaves.** The enum declares the completeness of an **inventory relationship**, not of a **set of
correctness propositions**. There is no per-item reason, no per-rule error rate, no notion of a check that
*could* have run but was not warranted. And it is software-only. **No financial analogue found** — scope of
that absence: the 16 vendor pages opened in Part 2 plus the arXiv queries in Part 3.

*Where this fits L0–L7:* **L7, and it is the citation that makes the coverage field look like engineering
rather than invention.** **Where it stops:** software supply chain only; no reasons; no rates.

### 4.4 **ASA/ISA 705 ¶24** — covered at §2.3. The audit profession's mandated "reasons for that inability".

### 4.5 **EBA quarterly deactivation of its own validation rules** — covered at §2.1.

### 4.6 **dbt-coverage** — MIT, 241★, coverage-as-presence. Covered at §2.5.

### 4.7 **Deequ automatic constraint suggestion** — Apache 2.0, 3.6k★. The non-LLM baseline L3 must beat.

---

## PART 5 — THE UNOCCUPIED CLAIM

### 5.1 The sentence

> **No product or published system, for any regulated financial filing, (a) admits a check into its active set
> only after measuring that check's own false-failure rate on a declared clean corpus and its kill rate against
> seeded faults, and (b) returns, alongside the verdict and signed with it, a computed per-field
> machine-readable declaration of which correctness propositions were not settled and why.**

### 5.2 The denominator that must travel with it, in the same breath

*Established against: 16 vendor/product pages opened at primary URLs across regulatory reporting, fund/NAV
oversight, audit AI, LLM-evaluation and data-quality tooling (§2.1–§2.6, with 20+ further named vendors
**not checked**); the arXiv metadata corpus via seven queries with a 186-result positive control (§3);
the LangChain documentation index of 40+ evaluation pages; the CycloneDX 1.6 JSON schema; ASA 705; and the
63-row IFSCA Fintech Sandbox register.*

### 5.3 The adversarial reading, clause by clause — where each word is load-bearing

| Clause | Why it is there | What it defends against |
|---|---|---|
| "regulated financial filing" | Excludes tax-prep software (arXiv:2205.04998 — metamorphic from statute, but no FFR, no coverage) and clinical-trial TFLs (PROVE — deterministic adjudication, but no FFR, no coverage) | "Someone already did metamorphic testing from statute" / "PROVE already does this" |
| "admits… only after measuring" | It is an **admission gate**, not a report. SPADE *selects* by FFR inside one pipeline's build; nothing keeps a permanent registry where an unmeasured check is inadmissible | "SPADE already filters by FFR" |
| "its own false-failure rate" | Per-rule, not per-system. Fieldguide's "<1% error rate" is one number for the whole agent; LangSmith's alignment score is one number per evaluator against human labels on private data | "Vendors already publish accuracy" |
| "on a declared clean corpus" | The corpus must be named, and **ours will initially be synthetic** (`ARCHITECTURE.md` risk 2). Declaring it is the honesty; hiding it is the failure mode | An honest judge asking "measured on what?" |
| "and its kill rate against seeded faults" | Mutation testing. Zero arXiv records apply it to financial rules. It is what supplies the *dirty* half when no labelled corpus exists — the exact gap SPADE names as unfillable ("the universe of examples 𝐸 is unknown") | "You can't measure FFR without labelled data" |
| "computed… declaration" | **Computed, not authored.** ASA 705 ¶24 is authored prose; CycloneDX is an authored enum value; ours is `N in scope, M settled, K unchecked by reason`, derived from the registry | "Auditors already declare scope limitations" |
| "per-field machine-readable" | Not a paragraph in a PDF. A supervisor triaging ~868 filings/year sorts by it | Same |
| "signed with it" | L7 binds the coverage claim to the template hash, filing hash and predicate-set version, so the boundary is auditable by a third party and cannot be restated later | "Coverage is just marketing" |

### 5.4 The one-line version for a slide

> **Everyone ships rules. Nobody ships each rule's error rate, and nobody ships the residue. We make both a
> product surface, and sign them.**

---

## PART 6 — THE THREE STRONGEST "THIS ALREADY EXISTS" OBJECTIONS, AND THE EXACT REBUTTALS

### Objection 1 — *"This is SPADE. Berkeley published it in 2024, LangChain shipped it, 2,000+ pipelines. You've re-skinned an existing product."*

**This is the most dangerous objection because the brief itself says "Reuse SPADE."** Concede the reuse
immediately and then be more precise about SPADE than the objector is.

**Rebuttal, four points, all ⓥ from the PVLDB PDF I extracted:**

1. **SPADE's criterion source is prompt-version history.** *"we can mine prompt version histories to identify
   assertion criteria… since developers implicitly embed data quality requirements through changes to the
   prompt."* Our criterion source is **statutory text plus the template's own 294 native formulas** — an
   authoritative source, not an inferred one. A regulation does not have a prompt-diff history.
2. **SPADE's own paper says the metric cannot be computed in general.** *"In practice, coverage and FFR are
   impossible to compute since the universe of examples 𝐸 is unknown. So, for now, we assume access to a subset
   𝐸′ ⊂ 𝐸 of labeled LLM responses… manually provided."* And that subset is small: *"each task has only 34 bad
   (i.e., failure) examples on average."* **Mutation testing is the answer to the sentence SPADE could not
   answer** — seeded faults manufacture the dirty half by construction, at any n, with a known ground truth.
   That is not a re-skin; it is the missing input.
3. **What shipped is not what the objection claims.** The public release with LangChain is *"this component"* —
   **Component 1, candidate assertion generation** — delivered in **November 2023 as an early prototype via a
   Streamlit application** (`spade-beta.streamlit.app`). The 2,000+ pipelines attach to that generator.
   **Today (10 Aug 2026), the LangChain documentation index lists 40+ evaluation pages and contains no
   "SPADE", no "false failure rate", and no assertion-synthesis feature; `assertions.md` describes assertions
   written by a human reviewer.** What LangSmith actually ships is an **alignment score** — *"the percentage of
   examples where the evaluator's judgment matches that of the human expert"* — which is aggregate agreement
   against human labels, not a false-failure rate against clean inputs.
4. **SPADE has no residue.** It selects a set of assertions. It never emits *what it could not assert*. Our L5
   UNCHECKED vocabulary and the computed coverage fraction have no counterpart anywhere in the paper or the
   product.

**Optional closer, and it is fair game:** SPADE's deployment sample (Figure 5) shows **Finance at 4.2%** —
one submission in a chart whose values are all multiples of 1/24. The technique's exposure to regulated
finance is, on the paper's own evidence, one prompt.

---

### Objection 2 — *"Auditors have declared what they couldn't check for decades. ISA 705. Qualified opinions. Emphasis of matter. You've rebuilt the audit report."*

**Concede the concept loudly — it is our best legitimising precedent — then show the three places it fails.**

**Rebuttal, with the primary text (ⓥ, ASA 705 compiled Mar 2023, `auasb.gov.au/media/ulnavf0z/asa705_03-23.pdf`):**

1. **It fires only on modification.** ¶20 begins *"**When the auditor modifies the opinion** on the financial
   report…"*, and ¶24 conditions on *"**If the modification results from** an inability to obtain sufficient
   appropriate audit evidence…"*. **An unmodified opinion carries no statement of what was not checked.** The
   clean audit report is the canonical silent all-clear — the exact artifact this project exists to abolish.
   The standard declares the boundary only in the cases where the boundary was already conceded.
2. **The mechanism demonstrably fails to fire when it should, at a measured rate.** **PCAOB: 20% of inspected
   Big Four audits in 2024 lacked sufficient appropriate evidence to support the opinion issued** (down from
   26% in 2023 and 2022) — `RND-BRIEF.md` §3.4, ⓞ operator-verified. In one inspected engagement in five, the
   evidence was insufficient *and the opinion was issued anyway*. A declaration that depends on a human
   noticing they should declare is not a coverage guarantee; it is a hope. **Our version is true by
   construction: a predicate whose error rate is unknown is not admitted, so it appears in the residue
   automatically rather than by anyone's virtue.**
3. **It is prose, per engagement, with no rate and no arithmetic.** ¶20(b) asks for *"a description of the
   matter giving rise to the modification"* — a paragraph, in English, once per audit, naming no procedure,
   carrying no false-positive rate, and yielding no fraction. You cannot sort 868 filings by it. You cannot
   diff it between quarters. You cannot verify it cryptographically. Ours is `PASS / FAIL /
   UNCHECKED(reason)` per (field × predicate), from a closed vocabulary, aggregated into a computed coverage
   fraction, signed over the template hash and the predicate-set version.

**One-line form:** *ISA 705 declares the boundary when the auditor already knows they hit one. We declare it
every time, per field, as a number, whether or not anyone noticed.*

---

### Objection 3 — *"Reg-reporting vendors ship thousands of validation rules — AxiomSL, OneSumX, Regnology, Confluence, FundApps. This is a mature, crowded category."*

**Concede the crowding. Attack the metric.** The category competes on **rule count and regime count**, and
those are the wrong axes.

**Rebuttal, five points:**

1. **Every vendor page I opened states counts, never quality.** Confluence: **"40+ countries", "90+ regimes"**;
   FundApps: **"850+ pre-coded global rules… 100+ jurisdictions"** (ⓢ). Milestone's pControl publishes the most
   complete validation catalogue in the lane — ~25 named validation families — and **"no stated false-positive
   or exception rates for any validation"** and **"does not declare what the oversight cannot check."** Scope
   of this absence claim: **4 of 12 named reg-reporting vendors + 3 of 6 named fund/NAV vendors opened; the
   rest NOT-CHECKED.**
2. **The rule authors themselves publish that their rules are wrong.** The **EBA deactivates validation rules
   quarterly "either for incorrectness or for triggering IT problems"** and instructs authorities that
   submissions **"should not be formally validated against the set of deactivated rules."** ⓥ If a rule count
   were a quality signal, the EBA would not need a kill-list. This is the positive control that the missing
   quantity is real, needed, and currently supplied only in binary form, after the damage, by the regulator.
3. **On the actual target artifact, the count is worse than anyone assumes.** Operator-measured on
   `Reporting_Format_for_Fund_Management_Entities_02012026`: **294 formulas, of which 38 (13%) express a
   checkable relationship and 181 (62%) are pure cross-sheet carry-forward** — the workbook moves numbers
   between sheets and the motion is counted as validation. **IBU Operations Report: 7 formulas across 961
   cells.** (`RND-BRIEF.md` §4.3, ⓞ.) The incumbent rule inventory for *this* artifact class is not thousands.
4. **Count says nothing about the residue.** Of 24 candidate correctness predicates on this return,
   **17 are script-settleable and 7 are not** — and the two sets are nearly disjoint (§2.4/§4.3, ⓞ). A vendor
   with 10,000 rules and no residue declaration is asserting, by silence, that the 7 do not exist.
   *(And per lane L15, the 17 is now strictly **15 exact + 2 approximate**, because the IFSCA register resolves
   names but not registration numbers — a live example of a check that must carry a non-zero FFR by
   construction or not be admitted.)*
5. **We are not competing with the category; we are supplying the column it does not have.** The natural end
   state is that a predicate registry with mutation scores and FFRs is something Confluence or Regnology would
   want to consume. That is a better answer to "crowded category" than claiming they are all wrong.

---

### Objection 4 (bonus — cheap to raise, cheap to kill) — *"MindBridge already does 100% coverage: Full Population Analysis."*

**Population coverage is not predicate coverage.** Scoring every transaction against a fixed set of models
answers *"which rows look unusual"*. It does not answer *"which correctness propositions about this filing have
been settled, and which cannot be."* MindBridge's own page publishes **no false positive rate and no
declaration of analytical limitations** (ⓟ). A risk score over 100% of rows with an unknown error rate is
exactly the operating point the evidence base rules out: `RND-BRIEF.md` §3.1 — **9 of 14 complete frontier-model
runs raise an error on ≥95.3% of 43 clean financial statements**, and a flag-everything classifier scores
≈66.2 against the best contract-discrepancy model's F1 of 65.4.

---

## PART 7 — WHAT IS GENUINELY NEW versus WHAT IS ASSEMBLY

### 7.1 Assembly — every one of these parts exists, is documented, and should be cited rather than claimed

| Part | Prior art | Warrant |
|---|---|---|
| LLM → executable assertions | **SPADE** (arXiv:2401.03038 / PVLDB 17 p.4173) | ⓥ |
| Non-LLM automatic rule synthesis | **Deequ** "Automatic suggestion of constraints for large datasets", Apache 2.0, 3.6k★ | ⓥ |
| Auto-proposed checks in a shipping product | **LangSmith Engine** "auto-propose assertions for production traces flagged as recurring issues"; **Braintrust Loop** "Generate and improve scorers and classifiers" | ⓟ |
| False-failure rate as a selection criterion | **SPADE Definition 3.2**, ILP with `Coverage(F′) ≥ α, FFR(F′) ≤ τ` | ⓥ |
| Evaluator-vs-human agreement in a product | **LangSmith alignment score** | ⓟ |
| Mutation testing as adequacy | Google, arXiv:2102.11378 (cited in `ARCHITECTURE.md`) | ⓢ (not re-opened this lane) |
| Metamorphic relations derived from statute | **arXiv:2205.04998**, IRS Pub 596 / Sch 8812 / Form 8863 | ⓥ |
| Deterministic adjudication of LLM output for a regulatory submission | **PROVE**, arXiv:2607.28218, 30 Jul 2026 | ⓥ |
| Fault-injection evaluation with paired clean/dirty packages | **PROVE**: 10 replicates × 15 injected discrepancies | ⓥ |
| Completeness declared as a required enum | **CycloneDX 1.6** `aggregateType`, 10 values, `not_specified` default | ⓥ |
| Coverage as a shipped metric | **dbt-coverage**, MIT, 241★ — presence of tests per column | ⓥ |
| Declaring reasons you could not check | **ASA/ISA 705 ¶24** | ⓥ |
| A rule author publishing that its rules are wrong | **EBA quarterly deactivation list** | ⓥ |
| Signed attestation over a build | in-toto / Sigstore | ⓢ |
| Authored statements of out-of-scope use | Model cards (Mitchell et al.) | ⓢ |

**That is a long list, and it should be shown, not hidden.** A judge who finds one of these after the pitch
discounts everything; a judge who is handed all fifteen upfront reads the team as competent.

### 7.2 New — nothing found, with the scope of the search attached

1. **A permanent predicate registry in which measurement is the admission condition.** Not "we measured our
   rules", but *"a rule with no measured error rate is inadmissible, therefore the coverage claim is true by
   construction."* Nothing in the 16 opened products, in SPADE, in PROVE, or in the audit standards has an
   admission gate.
2. **The per-rule FFR rendered on the verdict surface, next to the failure it caused.** *"This check fired on
   2.1% of 340 clean filings."* SPADE computes the number and consumes it internally; no product I opened
   displays it to whoever must act on the alert.
3. **UNCHECKED as a typed, closed-vocabulary, per-field, computed output for a financial artifact.** ASA 705
   has the concept in prose on modification; CycloneDX has the enum for software inventories; **the join —
   per-field, per-predicate, with reasons, computed, in finance — is empty across everything searched.**
4. **Coverage as a measured, growing quantity, with metamorphic relations as the mechanism that grows it.**
   The novel operational claim is not "we have coverage" but *"coverage moved from 15/24 to 19/24 because these
   four relations were admitted, each with its kill rate and FFR."* `metamorphic testing × spreadsheet` = **0**
   on arXiv; `metamorphic testing × financial` = **3**, none on a financial report; `mutation testing ×
   financial` = **2**, neither on financial rules.
5. **Binding the coverage fraction cryptographically to the template hash, filing hash and predicate-set
   version.** CycloneDX allows a signature over a composition; no financial analogue found.

### 7.3 Why the assembly is itself the contribution — the argument, not the assertion

The honest position is that **four of the five "new" items are joins, not inventions.** The argument that the
join is a contribution has to be structural, and here it is:

**Each part, alone, is defeated by a measured fact in `ARCHITECTURE.md` Part 1. The parts are chosen so that
each one's failure mode is another one's input.**

- **SPADE alone fails on fact 2 and on its own admission.** Its FFR needs labelled data; its paper states the
  labelled universe is unknowable and its own tasks average **34 bad examples**. → **Mutation testing supplies
  labelled dirty data by construction, at arbitrary n, with certain ground truth.** The seeded fault *is* the
  label. This is the load-bearing join and it is the reason the architecture is not a mashup.
- **Mutation testing alone fails on fact 8.** It measures whether a check can fire; it says nothing about the
  7 predicates with no oracle. → **Metamorphic relations settle a subset of those without an oracle**, and
  every relation admitted moves the 15/24 boundary — so the boundary becomes a *measured, movable* quantity
  rather than a philosophical limit.
- **Metamorphic relations alone fail on fact 1.** A relation can be trivially satisfiable or trivially
  violated; unqualified, it lands on the degenerate operating point where a flag-everything classifier
  (≈66.2) beats the state of the art (F1 65.4). → **The L4 degenerate-baseline test rejects it.**
- **All of them together still fail on fact 3** — 45–76% of agent failures are false successes and an LLM judge
  detects them at AUROC ≤0.65 — **unless the residue is emitted.** A system that silently drops what it could
  not check has produced a false success by definition. → **L5's UNCHECKED vocabulary and the computed coverage
  fraction are the only outputs that make a false success structurally impossible to render**, because there is
  no green tick to render.
- **And the whole thing is worthless without fact 6** — `pass^k` collapse and `0.9⁸ = 0.4305` — which is why
  there are exactly **two short model calls and no agent loop**, and why the registry, not the model, is the
  durable asset.

**The test of whether an assembly is a contribution: can you remove one part and keep the claim?** Remove
mutation testing → FFR is uncomputable and the gate is decorative. Remove the gate → coverage is an assertion
and we are Milestone with better copy. Remove metamorphic → coverage is a ceiling, not a growth curve, and the
demo has no second act. Remove UNCHECKED → it is a linter. **No part is removable. That is what makes it a
design rather than a stack.**

**The single strongest defensive framing:** *the contribution is not any layer — it is that the coverage claim
is true by construction rather than by discipline.* Every competitor's coverage claim depends on someone having
done their job. Ours depends on a rule being inadmissible without a number.

---

## PART 8 — ASSET-BY-ASSET: WHERE IT FITS L0–L7, AND WHERE IT STOPS

| Asset | Licence / status | Fits | Where it stops |
|---|---|---|---|
| **SPADE** (arXiv:2401.03038; PVLDB 17 p.4173) | Academic; Component 1 released via LangChain as a Streamlit prototype, Nov 2023 | **L3 + L4 test 3.** The ILP formulation `min Σxⱼ s.t. Coverage ≥ α, FFR ≤ τ` and the interaction bound `max(FFR(S),FFR({f})) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR({f})` are directly reusable for admitting interacting predicates | FFR needs a labelled `E′` the paper says cannot exist in general; 34 bad examples/task; criterion source is prompt deltas; **no coverage declaration, no UNCHECKED class, no FFR in LangSmith today** |
| **PROVE** (arXiv:2607.28218) | Academic, 30 Jul 2026 | **Citation for L2+L5 stance**; its cross-output consistency checks are a candidate predicate family | Synthetic corpus (10 packages); aggregate recall/F1 only; "within the implemented rule classes" is a prose caveat, not an output; no gate; no metamorphic layer |
| **Tax-prep metamorphic testing** (arXiv:2205.04998) | Academic, ICSE-SEIS 2023 | **Method citation for L6**; proof that statute→relation is a real technique | Relations hand-explicated with legal/tax experts; no FFR; no mutation score; no coverage output; tax program ≠ prescribed workbook |
| **Milestone pControl validation catalogue** | Commercial | **L3 target vocabulary + L5 predicate families** for fund artifacts (expected NAV, share-class divergence, holding/transaction/corporate-action/market-data validations) | No rates, no residue, no attestation; oversight seat not filing seat |
| **CycloneDX 1.6 `aggregateType`** | ECMA-424 / open standard | **L7 report schema.** Copy the design commitment: completeness is a *required* field with an explicit `not_specified` state | Software inventories only; no reasons; no per-rule rates; no financial analogue |
| **ASA/ISA 705 ¶20, ¶24** | Auditing standard | **L5 legitimation.** The sentence that makes an "unchecked panel" sound like practice rather than novelty | Modified opinions only; prose; per engagement; no rates; not machine-readable |
| **EBA quarterly deactivated-rules list** | Regulator publication | **L4 existence proof and demo prop.** "Even the EBA has to withdraw rules for incorrectness — with no rate attached" | Binary, post-hoc, author-side, no clean corpus |
| **Deequ** | Apache 2.0, 3.6k★ | **L3 non-LLM baseline** the model must beat under L4; **L5 substrate** | Constraint suggestion is profile-driven, not statute-driven; no per-constraint FPR |
| **Great Expectations / pandera / Soda Core** | OSS | **L5 execution substrate — do not rebuild** | Hand-authored assertions; results describe the data, not the rule |
| **dbt-coverage** | MIT, 241★ | **L5/UX precedent for the coverage meter** | Presence-only; no reasons; no rates |
| **LangSmith alignment score** | Commercial | **UX precedent** for showing an evaluator's agreement number in-product | Aggregate agreement vs human labels; not per-rule; not on clean inputs; private; non-gating |
| **Lawrbit / Gieom (in the GIFT sandbox)** | Commercial | **Channel and complement, not competitor.** Obligation inventory upstream of our verification | Neither opens the filed artifact; no rates; no residue |
| **IFSCA Fintech Sandbox register** (63 rows) | Public register | **Go-to-market denominator + eligibility evidence** | Name-list only (all fields but `Title` null — lane L15); includes exits, so 63 ≠ current cohort |

---

## PART 9 — WHAT THIS CHANGES ABOUT THE DESIGN

Nine changes. Five are corrections to claims; four are additions.

1. **Stop saying "SPADE shipped in LangSmith" without the qualifier.** The defensible form: *"SPADE's candidate
   generator was released with LangChain in Nov 2023 as a Streamlit prototype and has been used on 2,000+
   pipelines; the FFR-based selection is the paper's Component 2, and LangSmith's current documentation — 40+
   evaluation pages — contains no false-failure-rate concept."* Anyone who checks the docs will find this in
   two minutes, and the unqualified version is the kind of claim that loses a room.

2. **Cite PROVE (arXiv:2607.28218) on the slide that states the design thesis, as corroboration.** Independent
   convergence eleven days earlier in clinical-trial regulatory reporting is the best evidence the thesis is
   right, and pre-empting it costs one line. **And move the novelty claim off the thesis and onto the gate and
   the residue** — the thesis is now shared prior art.

3. **Cite arXiv:2205.04998 in L6.** Metamorphic relations from IRS publications is the existing precedent for
   relations-from-statute; it also **de-risks §9.1**, because it shows hand-authored relations from statutory
   text work when the model route fails. If §9.1 kills L3, L6 does not die with it.

4. **Adopt CycloneDX's design commitment literally in the L7 schema, including the default.** Make the coverage
   field **required**, and make `not_specified` an explicit representable state rather than an absence. A
   report that omits coverage must be invalid against the schema, not merely impolite.

5. **Add `rule_withdrawn` to the closed UNCHECKED vocabulary,** modelled on the EBA deactivation list: a
   predicate previously admitted whose FFR later exceeded threshold, or whose clause was amended. The brief's
   §4.2 measured that **90 of 389 circulars (23.1%) amend an earlier instrument** and **76 of 82 (92.7%) cite a
   resolvable target** — so predicates *will* be invalidated by amendment, mechanically and often. A registry
   that grows monotonically without a withdrawal state will silently carry dead checks. *(This joins lane
   L15's `external_source_lacks_field` and `external_source_unavailable`.)*

6. **Add a `degenerate_baseline_score` field to the predicate record, and show it in the library UI.** The
   competitive evidence says every adjacent product competes on rule *count*; the only cheap way to make a
   judge feel the difference is to display, per rule, what a flag-everything rule would have scored. It is the
   `65.4 vs 66.2` result rendered as a product surface.

7. **Reposition against the fund/NAV incumbents specifically, not against "RegTech".** Milestone pControl is
   the real neighbour: same artifact, same validation shape, no rates, no residue, and sold to the *oversight*
   seat. Our seat is the **filing** seat (the FME's compliance officer pre-submission), and the supervisory
   seat at IFSCA is already procured (NEC, 27 Jan 2026). Say "the filer's seat" explicitly and early.

8. **Position against Lawrbit and Gieom as complementary, in one sentence, before anyone asks.** *"Obligation
   tracking tells you a filing is due. We open the workbook."* Both are in the sandbox; a GIFT-ecosystem judge
   will know them.

9. **Build the two-day demo around the FFR column, not the coverage meter.** The competitive map says
   **coverage-as-presence already ships** (dbt-coverage, MIT, 241★) and **population coverage is a standard
   audit-analytics claim** (MindBridge "Full Population Analysis"). What ships nowhere is *the per-rule error
   rate next to the failure it caused.* Lane L15 already identified the perfect first instance: the register
   name-match predicate, fuzzy by construction, whose FFR can be measured against deliberately perturbed names
   in an afternoon. **That single screen is the whole differentiation.**

---

## PART 10 — CODE SKETCHES: THE TWO OBJECTS NOBODY ELSE SHIPS

These exist to make the claim concrete enough to defend. They are the shape of the differentiation, not an
implementation.

### 10.1 The predicate record — the admission gate as a data structure

```python
@dataclass(frozen=True)
class Predicate:
    key: str                     # stable id, e.g. "FME.T1_5.rowcount_matches_declared"
    clause: ClauseRef            # statutory anchor OR native-formula anchor (the L3 criterion source)
    reads: tuple[FieldKey, ...]  # L1-induced schema keys ONLY; anything else is rejected deterministically
    code: str                    # executable, content-addressed
    external_deps: tuple[ExternalSource, ...]   # from lane L15: endpoint + field, so a schema change
                                                # degrades to UNCHECKED loudly, never silently
    # ---- L4: the three tests. A predicate WITHOUT these is not representable, not merely not admitted.
    mutation_score: MutationScore     # |killed| / (|mutants| - |equivalent|); carries the equivalent-mutant caveat
    degenerate_score: float           # what flag-everything scores on the same set (the 65.4-vs-66.2 defence)
    ffr: MeasuredRate                 # value, n_clean, corpus_id, corpus_is_synthetic: bool  <-- the honesty
    admitted_on: date
    withdrawn_on: date | None         # NEW (Part 9 §5): EBA-style deactivation, with reason
```

**`ffr: MeasuredRate` is the field no competitor has.** Not `ffr: float` — the record carries the denominator
and whether the corpus was synthetic, because a rate without a denominator is the failure mode the brief's
Part 0 rule 1 exists to prevent.

### 10.2 The verdict — coverage computed, residue typed, and both signed

```json
{
  "template": {"sha256": "…", "version": "FME_02012026"},
  "filing":   {"sha256": "…"},
  "predicate_set": {"version": "2026.08.10+build.41", "n_admitted": 19},
  "coverage": {
    "aggregate": "incomplete",                    // required field, CycloneDX-style; "not_specified" is representable
    "in_scope": 24, "settled": 19, "unsettled": 5,
    "fraction": 0.7917
  },
  "results": [
    {"field": "T1.5.row_count", "predicate": "FME.T1_5.rowcount_matches_declared",
     "verdict": "FAIL",
     "ffr": {"value": 0.021, "n_clean": 340, "corpus_is_synthetic": true}},   // <-- shown next to the failure
    {"field": "FME.registration_number", "predicate": "FME.reg.resolves_in_register",
     "verdict": "UNCHECKED", "reason": "external_source_lacks_field",
     "what_would_make_it_checkable": "IFSCA DirectoryGetList must populate RegistrationNumber (0/650 today)"},
    {"field": "Sch3.valuation_appropriateness", "predicate": null,
     "verdict": "UNCHECKED", "reason": "requires_judgment",
     "clause": "FM Regs Third Schedule Part A(g), p.90"}
  ],
  "attestation": {"scheme": "in-toto/sigstore", "signature": "…"}
}
```

**Every element of this document except `ffr` and `reason` has a precedent named in Part 4.** Those two fields,
in this artifact class, are the claim.

---

## PART 11 — OPEN QUESTIONS THIS LANE COULD NOT CLOSE

1. **Twenty-plus named vendors were never opened** (AxiomSL/Nasdaq timeout, OneSumX 403, Corlytics 403, Vermeg,
   Ascent, Clausematch, Hexanika, Gresham, SS&C, Northern Trust, BNY, Trullion, Caseware IDEA, Klarity,
   AuditBoard, Basis, Bluecopa, Patronus, Arize Phoenix, Evidently, Giskard, Ragas, Soda, Sifflet, Bigeye, all
   Big Four in-house tools). **Any of them could publish a per-rule FPR and I would not know.** This is the
   lane's largest weakness and it must be re-run with a working search budget before the claim is put on a
   slide as an absolute.
2. **SR 11-7 / OCC 2011-12 (model risk management) could not be opened** — federalreserve.gov returned 404 on
   two URLs, occ.gov returned 404, and the fallback search served a CAPTCHA I did not solve. Banks operating
   under it already owe documented model limitations and outcomes analysis. **If a judge raises SR 11-7, I do
   not currently have the primary text.** Get it. The likely rebuttal shape — model risk documentation is
   *institution-internal governance prose about a model*, not a *per-rule rate travelling with a verdict* — is
   plausible but **UNVERIFIED**.
3. **XBRL Assertion Severity: NOT-FOUND.** `specifications.xbrl.org/specifications.html` and
   `spec-group-index-formula.html` were opened (positive control: they list "Formula 1.0" and "Rules and Query
   3.0", so the index is real and populated) and **no Assertion Severity specification appeared**. Do not
   assert it exists from memory. Whether XBRL formula assertions carry a severity or error-rate concept is
   **open** and matters, because Confluence/Regnology-class products execute XBRL assertions.
4. **Whether any regulator anywhere publishes a per-rule misfire rate** (as opposed to the EBA's binary
   deactivation) — unresolved. ESMA's rejection rates (1–2.5%) are a *submission* statistic, not a *rule*
   statistic.
5. **PROVE's full text was not read** — abstract only. Its §"implemented rule classes" may contain a coverage
   table that would narrow item 3 of Part 7.2. **Read it before the pitch.**
6. **Whether FundGuard's ML NAV-exception models publish any precision figure** in a source other than the
   marketing pages — not checked at a primary technical source.
7. **`spade-beta.streamlit.app` liveness** — the fetch redirected to a Streamlit auth URL and was not followed.
   Whether the Nov 2023 prototype still runs is unknown and mildly relevant to Objection 1 point 3.

---

## Adversarial verification (independent pass)

**Run 10 Aug 2026 by a separate verifier whose instruction was to REFUTE, not to agree.** Method: I did not
accept any citation in this lane as evidence. Every claim below was re-derived from the primary artifact —
the arXiv API queried myself, the PVLDB PDF downloaded and `pdftotext`-extracted myself, the CycloneDX schema
parsed with `python3` myself, the AUASB PDF downloaded and grepped myself, the LangChain docs fetched with
`curl` myself, the GitHub API queried myself, the IFSCA capture re-parsed myself. `WebSearch` was already at
200/200 for the session, so everything is direct `curl`/`WebFetch` of named primary URLs. Where I could not
reach the primary, the verdict is UNVERIFIABLE, not "probably fine".

### Summary

| # | Claim tested | Verdict |
|---|---|---|
| 1 | PROVE = arXiv:2607.28218, 30 Jul 2026, quoted abstract | **CONFIRMED** |
| 2 | Tax-prep metamorphic testing = arXiv:2205.04998, ICSE-SEIS 2023 | **CONFIRMED** |
| 3 | SPADE at PVLDB: FFR Def 3.2, "impossible to compute", 34 bad examples, Component 1 released Nov 2023 via Streamlit, 2000+ pipelines | **CONFIRMED** |
| 4 | SPADE Figure 5 ⇒ "Finance = 1 of 24 prompts / the technique's finance exposure is one prompt" | **REFUTED as stated** |
| 5 | CycloneDX 1.6: `aggregate` required, 10-value enum, `not_specified` default | **CONFIRMED** |
| 6 | ASA 705 ¶20 and ¶24 verbatim | **CONFIRMED** |
| 7 | EBA 12 Jun 2025: "incorrectness or … IT problems", "should not be formally validated" | **CONFIRMED** |
| 8 | All seven arXiv counts, including the two "false failure rate" IDs | **CONFIRMED** (every number reproduces exactly) |
| 9 | LangSmith today: no SPADE, no FFR; alignment score definition | **CONFIRMED** |
| 10 | Milestone pControl catalogue + no rates + no limitations | **CONFIRMED** |
| 11 | Fieldguide "<1% error rate versus manual processes", undenominated | **CONFIRMED** |
| 12 | Deequ Apache-2.0 3.6k★ · dbt-coverage MIT 241★ | **CONFIRMED** (3,638 / 241) |
| 13 | **Part 11 §3: "XBRL Assertion Severity: NOT-FOUND"** | **REFUTED** |
| 14 | `t24.json`: 63 rows, "every field except `Title` is null" | **QUALIFIED** |
| 15 | The lane's own coverage denominator: "16 opened pages" | **QUALIFIED — does not reconcile with Part 2** |
| 16 | PCAOB "20% of inspected Big Four audits in 2024" | **UNVERIFIABLE this pass** |
| 17 | Part 11 §7: `spade-beta.streamlit.app` liveness | **RESOLVED — not publicly reachable** |

### The two that change something

**13 — XBRL Assertion Severity exists. It is a Recommendation, and it has existed since 2016.**
Part 11 §3 records NOT-FOUND after opening `specifications.html` and `spec-group-index-formula.html`. I
reproduced both reads exactly — the formula group index does list only *Formula 1.0* and *Rules and Query
3.0*, so the lane's observation was accurate. But the third index page, `specifications-full-index.html`
(46 work products), carries it:

- **Assertion Severity**, REC **19 Apr 2016** — `https://www.xbrl.org/Specification/assertion-severity/REC-2016-04-19/assertion-severity-REC-2016-04-19.html`
- **Assertion Severity 2.0**, REC **21 Jul 2022** — `https://www.xbrl.org/Specification/assertion-severity/REC-2022-07-21/assertion-severity-REC-2022-07-21.html`
- **Assertion Severity Requirements 2.0**, REQ 7 Jul 2021
- also present: *Consistency Assertions*, *Existence Assertions*, *Value Assertions* (all REC 2009-06-22)

This is the lane's own failure mode from `RND-BRIEF.md` Part 0 rule 2 — a search interface mistaken for the
corpus it searches. Two pages were opened, both with a passing positive control, and the absence was still
wrong. **Correct Part 11 §3 from OPEN to KNOWN.**

*How much damage:* limited, and the damage is to the pitch rather than to the design. Assertion Severity 2.0
defines exactly three levels — **ERROR / WARNING / OK** — assignable statically or by a `<sev:expression>`.
I read the REC and confirm: **it contains no measured error rate, no false-positive rate, and no accuracy
statistic.** It classifies the *importance the rule author assigned* to an unsatisfied assertion; it never
says how often the assertion is wrong. So §5.1's sentence survives intact. What does not survive is the
lane's ability to say the space is empty of per-rule metadata. **A new objection must be pre-built**, because
Confluence/Regnology-class products execute XBRL formula assertions and a judge from that world will raise it
in the exact form *"XBRL assertions have carried severity since 2016."* The rebuttal is one line and it is
strong: *severity is declared by the rule's author before anyone runs it; FFR is measured against a corpus
after. One is intent, the other is evidence — and the EBA's own deactivation list is what happens when you
only have the first.* Add Assertion Severity 2.0 to Part 7.1 as assembly/prior art, alongside CycloneDX.

**4 — the Objection 1 "optional closer" is the weakest sentence in the lane, and it is the one most likely
to be said out loud.** §2.4.1 and §6 close with *"Finance = 1 of 24 submitted prompts"* and *"the technique's
exposure to regulated finance is, on the paper's own evidence, one prompt."* I extracted the same figures
from the same PDF — Others 4.2 · Marketing 4.2 · Finance 4.2 · Cooking 8.3 · Sports 8.3 · Education 8.3 ·
Customer Support 12.5 · Project Management 12.5 · IT 16.7 · Health 20.8, summing to 100.0, every value a
multiple of 1/24. The arithmetic is right. **The reading is wrong**, because the paper's own body text
frames that chart as a breakdown of the deployment, not of a 24-item sample (p.4176, verbatim):

> "there have been over 2000 runs of the app for custom prompt templates (i.e., not the sample default
> prompt template in app). These runs span many fields, including medicine, education, cooking, and finance…
> **Figure 5 shows a rough breakdown of the use cases people wanted to generate assertions for**; however,
> it's important to note that some runs may not cleanly fit into a single category"

The paper never states n = 24. On its face, Figure 5 apportions the 2,000+ runs, which puts finance at
~4.2% **of 2,000+**, i.e. order-80 pipelines — and the abstract-adjacent sentence at p.4174 says the released
component "has been subsequently used for over 2000 pipelines across more than 10 sectors **like finance**,
medicine, and IT." A judge holding the PDF turns "one prompt" into "you misread a figure to make your
competitor look small," and everything else in the lane gets discounted with it. **Delete the closer.** The
defensible replacement, which is still enough: *SPADE's evaluation set contains one finance pipeline —
summarising earnings-call transcripts, examples taken from Kaggle (Table 3, `finance`, 48/52/5) — and no
regulated filing anywhere in the paper.* That is ⓥ and unattackable.

### The two housekeeping corrections

**14 — `t24.json` is 63 rows (confirmed by re-parse), but "every field except `Title` is null" is false as
written.** Non-null across all 63: `SrNo`, `DfID`, `Title`, `DirParentCategoryName`, `DirSubCategoryName`,
plus ~20 session/boolean fields. **Null across all 63, and these are the ones that matter:**
`RegistrationNumber` **0/63**, `DateOfRegistration` 0/63, `Website` 0/63, `Email` 0/63, `Description` 0/63,
`RegisteredAddress` 0/63. The load-bearing conclusion — the register resolves names but not registration
numbers, so the reg-number predicate must carry a non-zero FFR or not be admitted — **is confirmed**. Only
the sweeping form of the sentence is wrong. Say "every descriptive field", not "every field".

**15 — "16 opened pages" does not reconcile with the lane's own Part 2 tables.** Counting products the lane
itself marks ⓥ or ⓟ: §2.1 → 3 (Suade, Regnology, Confluence); §2.2 → 2 (Milestone, Clearwater); §2.3 → 4
(MindBridge, DataSnipper, Fieldguide, Numeric); §2.4 → 5 tools / 6 pages (LangSmith, Braintrust ×2,
promptfoo, DeepEval, Guardrails); §2.5 → 5 (GX, Deequ, dbt-coverage, Monte Carlo, Anomalo); §2.6 → 2
(Lawrbit, Gieom). **That is 21 products, not 16**, and no stated rule (excluding OSS, excluding docs pages)
lands on 16 either. For an absence claim a larger denominator is *stronger*, so this understates the lane's
own case — but in a document whose entire method is denominator discipline, an unreconciled denominator is
the first thing an adversary will pull. Recompute it and show the derivation inline.

### What I could not close

**16 — the PCAOB 20%.** `pcaobus.org` returned 404 on the staff-spotlight and news-release paths I could
name, `assets.pcaobus.org` 404 on two document paths, and the session's WebSearch budget was already
exhausted at 200/200, so I could not reach a primary. It stays **UNVERIFIABLE in this pass** — note that
`RND-BRIEF.md` marks it ⓞ, so this is a re-verification failure, not a contradiction. Separately, a
denominator objection applies whoever verifies it: **PCAOB selects engagements for inspection on a
risk-targeted basis, not at random**, so "20% of *inspected* Big Four audits" cannot be restated as "20% of
Big Four audits". Objection 2 point 2 is already worded correctly ("inspected"); keep it that way, and never
let it drift on a slide.

### What held up, and it is most of the lane

Every load-bearing external artifact reproduced **exactly**, several to the character:

- **PROVE** resolves at `arxiv.org/abs/2607.28218`, 30 Jul 2026, Lu/Zheng/Han, and the abstract contains
  verbatim *"not reliable substitutes for programmed statistical checks"*, *"reserving numerical and logical
  decisions for programmed validators"*, *"ten replicated synthetic oncology reporting packages"*, *"each
  replicate included 15 randomly injected discrepancies"*, *"Within the implemented rule classes"*, and
  0.588→0.993 recall / 0.735→0.996 F1. The lane's most dangerous nearest neighbour is real and correctly read.
- **SPADE**: PDF is 6 pages, 1,055 extracted lines — matching the lane. Definition 3.2 at line 496; *"coverage
  and FFR are impossible to compute since the universe of examples 𝐸 is unknown"* at 509; *"each task has only
  34 bad (i.e., failure) examples on average"* at 828–829; α = 0.6, τ = 0.25 across all 9 pipelines; *"baseline
  violates the FFR constraint in 4 out of 9 pipelines"*; 14% / 21% / 44%. And the Component reading is right:
  the heading **"Component 1: Prompt Deltas for Candidate Assertion Generation"** precedes *"With LangChain, we
  publicly release this component of spade"*, with **"Component 2: Filtering Candidate Assertions with Limited
  Data"** starting after it. §2.4 *"in November 2023, we released an early prototype … via a Streamlit
  application"*, footnote 4 `spade-beta.streamlit.app`. All ⓥ.
- **CycloneDX 1.6** (`bom-1.6.schema.json`, 262,666 bytes): `compositions.required = ["aggregate"]`;
  `aggregateType` enum length **exactly 10**, the ten values as printed; `default: "not_specified"`;
  `signature` present on `compositions`. Byte-for-byte as claimed.
- **ASA 705** (`auasb.gov.au/media/ulnavf0z/asa705_03-23.pdf`, 33 pp, compiled 22 Mar 2023): ¶20 at line 424
  and ¶24 at line 445 of my own extraction, both word-for-word as quoted.
- **EBA**: both quoted strings present on the 12 Jun 2025 press release.
- **arXiv, re-run with my own positive control (`all:"metamorphic testing"` → 186, same three head titles):**
  spreadsheet **0** · financial **3** (2606.22519, 2401.00751, 2411.02077 — identical IDs) · `metamorphic
  relation` × accounting **4** (including 2205.04998 and 2409.16140) · mutation × financial **2** (2603.23441,
  2504.20357) · `"false failure rate"` **2** (2602.11305 *Are Aligned Large Language Models Still Misaligned?*
  and 2605.30695 *Primitive Subspaces Mediate Few-Shot Transfer in VLAs* — neither SPADE, exactly as claimed)
  · regulatory reporting × LLM **5** · `abs:"validation rules"` × `abs:"LLM"` **9**. **Seven for seven.**
  One footnote: PROVE itself is inside the 5-result reg-reporting set, so "Nearest: RKEFino1" understates —
  the nearest is PROVE, which the lane already treats as §4.1.
- **LangSmith**: `llms.txt` = 99,944 bytes, 960 lines, **57** lines matching "eval" (so "40+" is safe);
  `grep -ci spade` → **0**; `grep -ci "false failure"` → **0**. `assertions.md`: *"Assertions turn a reviewer's
  English-language standards into an automated check…"* and *"LangSmith Engine can auto-propose assertions for
  production traces flagged as recurring issues"*, zero FFR mentions. `improve-judge-evaluator-feedback.md`
  line 80: *"The alignment score is the percentage of examples where the evaluator's judgment matches that of
  the human expert."* Verbatim match.
- **Milestone pControl**: I re-fetched and got the same catalogue in the same order, and the same two
  answers — no rate of any kind, no limitations section. The only number on the page is "three options".
- **Fieldguide**: *"error rate of less than 1% versus manual processes"* present; no denominator, no sample
  size, no corpus, no per-check breakdown. The lane's PARTIAL is the right grade.
- **GitHub**: `awslabs/deequ` → **3,638★**, **Apache-2.0**, not archived, pushed 21 Jul 2026, README lines
  133–134 carry "Anomaly detection…" and "Automatic suggestion of constraints for large datasets".
  `slidoapp/dbt-coverage` → **241★**, **MIT**, README line 18 makes the `coverage.py` analogy explicitly.

**17 — Part 11 §7 closes.** `https://spade-beta.streamlit.app/` now 303-redirects into a Streamlit
`/-/login?payload=…` loop that exhausts 50 redirects. **The Nov 2023 prototype is not publicly reachable
today.** That strengthens Objection 1 point 3: the thing that "shipped" was a prototype that no longer
answers, and the FFR selection was never in it.

### Verdict on the design

**Nothing I found touches §5.1.** The unoccupied claim needs (a) admission-by-measured-FFR and (b) a computed,
typed, signed residue. XBRL Assertion Severity is authored intent; CycloneDX `aggregate` is an authored
inventory enum; ASA 705 ¶24 is authored prose on modification; LangSmith's alignment score is aggregate
private agreement; Fieldguide's <1% is undenominated and per-agent; PROVE's "within the implemented rule
classes" is a prose caveat. **No primary artifact I opened contains a per-rule measured false-failure rate on
a declared clean corpus, or a computed machine-readable residue.**

What must change, in order of urgency: **(i)** delete the SPADE "one prompt" closer and replace it with the
Table-3 finance-pipeline fact; **(ii)** flip Part 11 §3 to KNOWN, add Assertion Severity 2.0 to Part 7.1, and
write the intent-vs-evidence rebuttal before the pitch; **(iii)** recompute the "16 pages" denominator and
show the derivation; **(iv)** soften "every field is null" to "every descriptive field"; **(v)** re-verify the
PCAOB figure at a PCAOB URL and keep the word "inspected" attached to it permanently.
