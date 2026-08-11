# LANE L01 — Verification of the four unopened arXiv identifiers

**Run 10 Aug 2026.** Task: open, at source, the four arXiv IDs that entered `RND-BRIEF.md` from a
research agent and were never personally read. Report actual title/authors/date/abstract, check every
attributed number against the paper with its denominator, and — where an attribution fails — find the
real work that repairs the claim rather than merely deleting it.

**Headline: all four identifiers are REAL and resolve. None is a hallucinated ID.** Three of the four
attributions are substantially correct. **One (PASC) carries a materially false attribution.** More
importantly, three of the four papers contain load-bearing results the brief *did not extract*, and one
of those results — the dual-control finding in 2606.09863 — is the single strongest piece of external
evidence for the architecture that exists in the corpus, and the brief currently omits it.

**Warrant key used throughout:** `VERIFIED-AT-SOURCE` = I opened the arXiv abstract page and/or the
full HTML text and read the sentence. `SECONDARY` = a credible third-party index describes it.
`UNVERIFIED` = could not confirm.

---

## PART 0 — METHOD AND CONTROLS

Everything below rests on the arXiv API discriminating real identifiers from fake ones. That was tested
before any conclusion was drawn.

### 0.1 Interfaces used

| Interface | URL form | What it is |
|---|---|---|
| arXiv abstract pages | `https://arxiv.org/abs/<id>` | primary source, publisher-hosted |
| arXiv full text | `https://arxiv.org/html/<id>v1` | primary source, full body + appendices |
| arXiv Atom API | `http://export.arxiv.org/api/query?id_list=…` | structured metadata, batch |
| arXiv identifier spec | `https://info.arxiv.org/help/arxiv_identifier.html` | the numbering grammar itself |
| general web index | `WebSearch` | independent corroboration, non-arxiv.org hosts |

Semantic Scholar (`api.semanticscholar.org`) was attempted twice as a fourth, fully independent
channel and returned **HTTP 429 Too Many Requests** both times. **That check did not run.** It is not
evidence either way.

### 0.2 NEGATIVE CONTROL — does the API refuse fake IDs? (the control that makes everything else mean something)

Query: `id_list=2606.99999,2612.00001,2699.12345,2606.30000,2606.09863`

| Requested ID | Returned? | Interpretation |
|---|---|---|
| `2606.99999` | **ABSENT** | sequence number beyond the month's actual volume |
| `2612.00001` | **ABSENT** | December 2026 — a *future* month on 10 Aug 2026 |
| `2699.12345` | **ABSENT** | year 2099, nonsense |
| `2606.30000` | **PRESENT** — "Adaptive nonparametric regression from repeated measurements under commo…" | real |
| `2606.09863` | **PRESENT** — "From Confident Closing to Silent Failure…" | real |

`opensearch:totalResults` = **2** for a 5-ID request. **The API discriminates.** It returns entries
only for identifiers that exist and silently omits those that do not (it emits no error text for a
well-formed-but-nonexistent ID). Therefore a returned entry is positive evidence of existence.
`VERIFIED-AT-SOURCE`.

### 0.3 POSITIVE CONTROL — independent index, searched by phrase not by ID

For each paper I ran a `WebSearch` seeded with *distinctive content phrases*, never the arXiv number,
to see whether an index outside arxiv.org independently surfaces the same work.

| Paper | Query seeded with | Independent hits |
|---|---|---|
| 2606.09863 | `"false success" LLM agents tau2-bench AppWorld TF-IDF detector` | arxiv.org/abs + `github.com/benchflow-ai/awesome-evals` (third-party curated list) + `bymachine.news` + an X/Twitter post |
| 2603.21172 | `"Entropy Alone is Insufficient…" Phillips Gustafsson Clifton` | arxiv.org + **`fregu856.com`** — co-author Fredrik K. Gustafsson's own personal site, listed as "Postdoc in Oxford" |
| 2605.18812 | `"PASC" "Pipeline-Aware" conformal … Kotte` | arxiv.org + `arxiv.org/catchup/cs.LG/2026-05-20` (independent announcement listing) |
| 2606.03031 | `FinAuditing benchmark XBRL FinMR financial audit LLM dataset` | surfaced **organically**, unprompted by title or ID |

**Coverage denominator declared:** this is a general web index (the `WebSearch` tool, US region), not a
bibliographic database. It does not prove peer review, citation, or quality. It proves the documents
are indexed outside their publisher. That is the claim I make and no more.

### 0.4 THE ID-GRAMMAR QUESTION — is `2606.xxxxx` even possible on 10 Aug 2026?

**Answer: yes, comfortably, and the specific sequence numbers are all in range.**

From `https://info.arxiv.org/help/arxiv_identifier.html` — `VERIFIED-AT-SOURCE`:

> "From 1501 on it is 5-digits, starting at `00001`. 5-digits permits up to `99999` submissions per month."

> "YY is the two-digit year (07=2007 through 99=2099…)" · "MM is the two-digit month number (01=Jan,…12=Dec)."

Canonical form since January 2015 is `arXiv:YYMM.NNNNN`, zero-padded, sequential within the month.

**Date check.** Today is 10 Aug 2026 = `2608`. The four IDs are `2606` (June 2026), `2606`, `2605`
(May 2026), `2603` (March 2026). **All three months are strictly in the past.** There is nothing
anachronistic about a 2606 identifier today. A `2609` identifier would have been the red flag; none of
the four is one.

**Volume check (does the sequence number fit the month's actual traffic?).** I probed the API for
high sequence numbers in each relevant month:

| Probe | Result | Implies |
|---|---|---|
| `2603.30000` | **exists**, `<published>` 2026-03-31T16:57:33Z | March 2026 received **≥30,000** submissions |
| `2606.30000` | **exists** | June 2026 received **≥30,000** submissions |
| `2606.25000` | exists, 2026-06-23 | consistent |
| `2606.99999` | absent | month did not reach 99,999 — sanity holds |

arXiv's own stats page reports **"Total number of submissions as of August 10, 2026 = 3,128,807"**
(`VERIFIED-AT-SOURCE`, `arxiv.org/stats/monthly_submissions`); the per-month table did not render for
me, so I use the probe result, not the site's table, as my denominator source.

Against a floor of ≥30,000/month, all four quoted sequence numbers — `21172`, `18812`, `09863`,
`03031` — are unremarkable. **The grammar objection dissolves.**

**Monotonicity probe, and one anomaly worth naming so nobody re-discovers it as a scandal.** Sequence
number tracks submission date cleanly within March 2026:

```
2603.21172 -> 2026-03-22T11:27:13Z
2603.24000 -> 2026-03-25T07:00:10Z
2603.26000 -> 2026-03-27T01:34:01Z
2603.28000 -> 2026-03-30T03:43:36Z
2603.30000 -> 2026-03-31T16:57:33Z
```

June 2026 is monotonic too — **except for our paper**:

```
2606.00001 -> 2026-03-24T20:12:00Z   <-- v1 submitted THREE MONTHS before its June number
2606.05000 -> 2026-06-03T15:17:26Z
2606.09863 -> 2026-06-01T00:13:23Z   <-- lower date, HIGHER number than 05000
2606.15000 -> 2026-06-12T22:42:43Z
2606.20000 -> 2026-06-18T09:35:38Z
2606.25000 -> 2026-06-23T16:20:01Z
2605.00001 -> 2026-01-20T15:06:20Z   <-- v1 submitted FOUR MONTHS before its May number
```

`2606.09863` looks out of order. **It is not a forgery signal.** The `<published>` field is the v1
*submission* timestamp; the identifier is assigned at *announcement*. Papers held in moderation
retain the early submission time and receive a later number. The pattern is visible in its extreme
form at `2606.00001` (submitted 24 Mar, numbered June) and `2605.00001` (submitted 20 Jan, numbered
May) — both indisputably genuine arXiv records. `2606.09863` is a mild instance of the same
mechanism. `VERIFIED-AT-SOURCE` (the probe), interpretation `SECONDARY`.

---

## PART 1 — arXiv:2606.09863 · VERDICT: **VERIFIED**

### 1.1 What the identifier actually resolves to

- **URL:** `https://arxiv.org/abs/2606.09863` — resolves. `VERIFIED-AT-SOURCE`
- **Title:** *From Confident Closing to Silent Failure: Characterizing False Success in LLM Agents*
- **Author:** **Laksh Advani** — single author, **no affiliation stated anywhere in the paper**
- **v1 submitted:** 2026-06-01T00:13:23Z · **primary category:** cs.LG
- **Comments field:** none. **No venue. No code or data release.** `VERIFIED-AT-SOURCE`

### 1.2 The attributed numbers, checked line by line

| Brief's claim | Paper says | Denominator | Verdict |
|---|---|---|---|
| 45–48% of failures in single-control domains are false successes | abstract: "45--48% of failures in single-control tau2-bench domains"; body: **airline 45%, retail 47%** | airline **393** failures, retail **895** failures | **CONFIRMED** |
| 75.8% on AppWorld | "75.8% among AppWorld self-assessing coding-agent trajectories with explicit status claims" | **1,425 false success / 1,879** trajectories with explicit completion claims = 75.84% | **CONFIRMED — but the denominator is narrower than the brief implies** |
| LLM judge AUROC ≤0.65 | "no configuration across **5 judges, 5 prompt strategies**, and full task specifications exceeds AUROC 0.65 on tau2-bench"; **0.54** on AppWorld API traces | as stated | **CONFIRMED** |
| 13% recall at a 10% flag rate | "the detector recovers 72% of false successes [95% CI 63–80%], while **the strongest judge recovers 13% [8–17%]**" | tau2-bench, 10% flag rate | **CONFIRMED, with CI** |
| TF-IDF + XGBoost 0.825–0.953 AUROC | tau2-bench task-disjoint **"TF-IDF + XGBoost 0.825 ±0.025"**; AppWorld task-disjoint **0.953** | two different benchmarks | **CONFIRMED** |
| 72% recall | 72% [95% CI 63–80%] at 10% flag rate on tau2-bench | 616 labelled false successes | **CONFIRMED** |
| 3,300× faster | "A single XGBoost inference on CPU takes **1.19 ms**; an LLM judge API call takes approximately **4,000 ms**. The structural detector runs **3,364×** faster." | — | **CONFIRMED, but see §1.4** |

**Full trajectory denominators** (`VERIFIED-AT-SOURCE`, full text):
`9,876` tau2-bench trajectories from 8 model families → `8,146` successful, **`1,730` failures**
(airline 393 + retail 895 + telecom 442 = 1,730 ✓). **616 false successes labelled in total.**
AppWorld: `1,879` trajectories from 4 model families → 1,425 false success + 454 honest failure.

**Derived, and the brief should carry it:** the *pooled* tau2-bench false-success rate is
**616 / 1,730 = 35.6%**, not 45–48%. The 45–48% figure is the per-domain rate in the two single-control
domains only. `VERIFIED-AT-SOURCE` inputs, arithmetic mine — label ⓧ.

### 1.3 THE FINDING THE BRIEF MISSED — and it is the best evidence in the corpus for this architecture

The abstract contains a third number the brief never carried: **"3% in dual-control telecom."**

Full text, `VERIFIED-AT-SOURCE`:

> "In telecom, a **dual-control domain where the user simulator can independently verify state**,
> false success drops to **3% of failures**"

Denominator: 442 telecom failures → roughly 13 false successes. And in the Limitations section the
author generalises it himself:

> "The environment-structure finding suggests that **any benchmark with independent state-verification
> will suppress false success**, but the qualitative phenomenon should persist wherever agents emit
> completion claims **without verifiable grounding**."

**This is a ~15× collapse in silent failure (45–47% → 3%) produced by nothing more than adding an
independent verifier of environment state.** That is exactly what L4/L5 are. The brief cites this
paper three times and quotes only the frightening halves of it, while the paper's own strongest
design-relevant result is the one that says *the fix works, and here is the measured size of the
effect.* This is the standing bias in Part 11 of the brief operating on evidence selection: the
alarming number was retained, the number that says "the thing may be tractable" was dropped.

### 1.4 What the brief must ALSO carry from this paper (limitations, quoted)

Five qualifications, all `VERIFIED-AT-SOURCE` from the Limitations section, and several of them cut
against the brief's own use of the paper:

1. **Precision at the operating point is 50%.** > "At a 10% flag rate, **precision is 50%**: half of
   flagged trajectories are false alarms." The brief's entire thesis is *precision is the scarce
   quantity*. The detector it holds up as the working alternative to the LLM judge **is itself at 50%
   precision.** The brief quotes its recall (72%) and never its precision. This must be fixed before
   it reaches a slide, because an adversary will find it in one minute.
2. **The tau2-bench ground truth is a regex, not an oracle.** > "A trajectory is labelled False Success
   if `FS_ASSERT_RE` matches and `HONEST_FAILURE_RE` does not…" — validated against human annotation at
   **κ=0.86**. Only **AppWorld** uses a genuine programmatic oracle: > "AppWorld agents write a status
   field … directly to a supervisor database … This field is entirely independent of the agent's
   natural language." So `ARCHITECTURE.md` Part 1 fact #4 ("the working detector needs labels from a
   programmatic environment oracle") is **true for the AppWorld arm and only κ=0.86-human-validated
   regex for the tau2 arm.** The fact survives; its warrant is mixed and should say so.
3. **The 75.8% covers 2 of 4 AppWorld architectures.** > "the AppWorld FS rate of 75.8% **applies to a
   subset of trajectories, not the full benchmark**" — the other two architectures always write
   `status=success`, making the field uninformative.
4. **The detector does not transfer for free.** Zero-shot leave-one-domain-out transfer is AUROC
   **0.69** (vs 0.825 in-domain); **50–100 labelled examples per class** are needed to reach 0.79–0.83.
5. **It is adversarially fragile.** > "A preliminary rewrite test … flips both detectors and judges on
   roughly **20–25% of cases** when honest-failure closing messages are rewritten in confident-completion
   style." The detector reads *surface style*, not state.

Also worth stating plainly: the **3,364×** is `1.19 ms` local CPU inference versus a `~4,000 ms` **API
call including network round-trip**. It is a wall-clock deployment comparison, not a compute
comparison. Quotable, but quote it as what it is.

Minor: on tau2-bench, **TF-IDF + Logistic Regression (0.849) beats TF-IDF + XGBoost (0.825)**. Saying
"XGBoost" is fine but it is not the best simple model on that arm.

### 1.5 Where this fits in L0–L7, and where it stops

**Fits:** Part 2.2 of the brief (the agentic framing) and `ARCHITECTURE.md` Part 1 facts **#3** and
**#4**. The dual-control result is direct external support for the **L4→L5 boundary**: the design
claim "a model may never be the final judge; every model output is adjudicated by a deterministic
layer" now has a measured effect size attached to it (45–47% → 3%) from an independent benchmark.
Reuse the 50%-precision-at-10%-flag-rate figure in the **L4 test 3 (FFR)** discussion as evidence that
even the good detector needs an FFR declared next to it.

**Where it stops:** customer-service and app-automation simulators with programmatic rewards; the
author says extension to unstructured settings "remains open." **No code, no data, no venue, single
unaffiliated author.** It cannot bear weight as a *citation of authority* — only as a *reported
measurement whose method is described*. Nothing here is about financial filings.

---

## PART 2 — arXiv:2606.03031 · VERDICT: **VERIFIED (numbers), but the brief's USE of them is wrong**

### 2.1 What the identifier actually resolves to

- **URL:** `https://arxiv.org/abs/2606.03031` — resolves. `VERIFIED-AT-SOURCE`
- **Title:** *AuditFlow: Executable Symbolic Environments for Structured Financial Reporting Verification*
- **Authors:** Yan Wang, Xuguang Ai, Jaisal Patel, Xueqing Peng, Fengran Mo, Yupeng Cao, Haohang Li,
  Mingyu Cao, Lingfei Qian, Víctor Gutiérrez-Basulto
- **v1:** Tue, 2 Jun 2026 02:14:42 UTC (9,452 KB) · **cs.AI; cs.MA; cs.SC** · no comments/venue field

The brief spells it "AUDITFLOW"; the paper styles it "AuditFlow". Trivial, but fix it.

### 2.2 The attributed numbers

| Brief's claim | Paper says | Verdict |
|---|---|---|
| 82.09% → 17.91% on ablation of the deterministic layer | abstract: "AuditFlow reaches **82.09%** joint audit accuracy under GPT-5.5 … **Removing deterministic checks drops accuracy to 17.91%**" | **CONFIRMED verbatim** |
| n=67 | "We evaluate AuditFlow on a **67-instance subset** of the FinMR task from FinAuditing" | **CONFIRMED** |

**The ablation table** (`VERIFIED-AT-SOURCE`, Figure 4(a)):

| Condition | Joint ACC | Invalid outputs |
|---|---:|---:|
| Full AuditFlow (GPT-5.5) | **82.09%** | 1.49% |
| **− deterministic checks** | **17.91%** | **35.82%** |
| − required-tool gate | 74.63% | 17.91% |
| − ER fusion | 77.61% | — |
| Single Agent (strongest baseline) | **67.16%** | — |

### 2.3 THREE CORRECTIONS the brief needs — the numbers are right, the inference is not

**(a) "+64pts" is a self-ablation, not a method comparison — and §9.4 uses it as one.**
`RND-BRIEF.md` §3.3 and §9.4 line AuditFlow's "+64pts" up against FinVerBench's "0% FA / 47% miss" and
FinBalance's "worsened 13–52pp" as three comparable results that "disagree." They are not commensurable.
82.09 − 17.91 = 64.18 points measures *what happens when you remove a load-bearing component from
AuditFlow*. The paper's own comparison to the best alternative method is **14.93 points** (67.16% Single
Agent → 82.09%). **Any adversary reads the abstract and finds this in thirty seconds.** The honest
sentence is: *"AuditFlow beats its strongest baseline by 14.93 points on 67 instances; ablating its
deterministic checkers costs it 64.18 points, showing the checkers rather than the agent scaffolding
carry the result."*

**(b) Roughly half the 64-point collapse is well-formedness, not wrongness.**
Invalid outputs go **1.49% → 35.82%**. On n=67 that is 1 → 24 instances. Correct goes 55 → 12. So of
the 43 instances lost, **~23 became unparseable output and ~20 became well-formed-but-wrong.** The
ablation therefore partly measures *"the model cannot emit a valid answer without the tool scaffolding"*
— which is a weaker and different claim than *"the deterministic layer is the verification capability."*
The paper's own sentence is the defensible one: > "the symbolic environment performs the verification
step that the model cannot reliably replace." Quote that, not the arithmetic.

**(c) n=67, and the paper reports the CI — so quote it.**
Appendix G, Table 10 (`VERIFIED-AT-SOURCE`): **"GPT-5.5: 82.09%, 95% CI [75.8, 90.2]"**, B=10⁴ bootstrap
resamples over 67 cases. A ±7pp interval on the headline number means the 14.93-point baseline gap
(10 instances out of 67) is **not** established as significant by anything reported. The 64-point
ablation delta is large enough to survive; the baseline comparison is not.

### 2.4 Two provenance facts the brief should know

**Self-evaluation.** FinAuditing is **arXiv:2510.08886** (submitted 10 Oct 2025, last revised 17 May
2026), *"FinAuditing: A Financial Taxonomy-Structured Multi-Document Benchmark for Evaluating LLMs"*,
**1,102 annotated instances** across three subtasks (FinSM semantic, FinRE relational, **FinMR
numerical**), built from real US-GAAP XBRL filings, hosted at
`huggingface.co/collections/TheFinAI/finauditing`. `VERIFIED-AT-SOURCE`.
**Author overlap is heavy** — Yan Wang, Jaisal Patel, Xueqing Peng, Fengran Mo, Lingfei Qian and
Víctor Gutiérrez-Basulto appear on **both** papers. AuditFlow is the same group evaluating its own
method on a 67-instance slice of its own benchmark. Not disqualifying; must be disclosed.

**The subset is rule-defined, and the parent set's size is never stated.** > "The 67 instances include
**22 DQC.US.0015 cases, 24 DQC.US.0117 cases, and 21 DQC.US.0126 cases.**" The paper does not state
how large FinMR is in full, so **the sampling fraction is unknown**. Its own Limitations section says:
> "Our evaluation is limited to a 67-instance subset of the FinMR task from FinAuditing and three DQC
> rule families … they do not represent the full range of XBRL audit rules, filing types, companies, or
> reporting years."
**No code or data released:** > "We do not redistribute raw SEC filing packages or proprietary model
outputs as part of this paper."

Context worth carrying: the FinAuditing paper reports the best model reaching only **13.86%** accuracy
on FinMR (`SECONDARY` — from the search-index summary of 2510.08886, not read in the paper body).
AuditFlow's 82.09% on a 67-instance three-rule slice is therefore a very large jump over the parent
benchmark's reported ceiling, which is *either* the strength of the method *or* an artifact of the
slice. **Unresolved. Do not present the 82.09% without the slice.**

### 2.5 THE REUSABLE ASSET HIDING INSIDE THIS PAPER — the DQC ruleset

AuditFlow's "deterministic checks" are not bespoke. They are three named rules from the **XBRL US Data
Quality Committee** ruleset (`VERIFIED-AT-SOURCE`, full text):

| Checker | Rule | What it does |
|---|---|---|
| `check_sign` | **DQC.US.0015** | sign consistency |
| `check_calc_tree` | **DQC.US.0126** | calculation-tree consistency + expected-value computation |
| `check_dim_consistency` | **DQC.US.0117** | dimensional aggregation |

They return "the triggered rule, reported value, expected value when available, supporting facts" — a
**structured finding object with an expected value**, which is precisely L5's PASS/FAIL payload shape.

I then went to the ruleset itself:

- **Repo:** `https://github.com/DataQualityCommittee/dqc_us_rules` — `VERIFIED-AT-SOURCE`.
  **31 stars, 39 forks, 6,309 commits on master, primary language Python.**
- **Execution model:** > "The DQC rules are run using an **Arelle** plugin written in an XBRL rule syntax
  called **Xule**" — assertions evaluated "against an XBRL instance, a taxonomy or an extension
  taxonomy, creating validation messages."
- **Licence (`License.md`, read at source):** a **custom licence**, © 2015–present **AICPA, Calcbench
  Inc., Toppan Merrill LLC, Workiva Inc., XBRL US Inc.** It permits copying, distribution and
  derivative works that "comment on or otherwise explain it or assist in its implementation" with the
  copyright notice retained; **the document itself may not be altered except for translation**;
  provided "AS IS". **It is NOT OSI-approved and NOT MIT/Apache.** Commercial use is not explicitly
  forbidden but this is a bespoke document licence, not a software licence — **do not put it in a
  dependency list without reading it in full first.**
- Third-party report of a **20th rule set** having been published (`SECONDARY`, xbrl.org news item).
  **I did not confirm the current version number or the total rule count at source. UNVERIFIED.**

**Why this matters more than the paper does:** the DQC ruleset is a **real, versioned, publicly
maintained, decade-old registry of executable validation predicates over regulated financial filings,
each with a stable identifier.** That is *the thing the brief's L3/L4 predicate registry is trying to
become.* Its existence is simultaneously (a) proof the concept is viable and institutionally durable,
and (b) a hit on the novelty claim — the brief's `PART 6.2` asserts rules-as-code is "DEAD FOR FINANCE
… zero financial regulations encoded anywhere." That claim is about **Catala/OpenFisca/Blawx**, and
within that denominator it may hold. **But DQC.US.* is 6,309 commits of executable financial-filing
validation rules and it must be named**, or the first XBRL-literate judge in the room kills the claim.
The defensible restatement is in Part 6 below.

### 2.6 The §9.4 "none cites the others" claim — CHECKED, and it holds

I read AuditFlow's bibliography directly. `VERIFIED-AT-SOURCE`:

- Cites **FinVerBench** (arXiv:2605.29586)? **NO.**
- Cites **FinBalance**? **NO.**
- Cites **FinAuditing** (arXiv:2510.08886)? **YES** (Wang et al., 2026).

So for the AuditFlow → {FinVerBench, FinBalance} direction, `RND-BRIEF.md` §3.3's claim that the three
papers "disagree and none cites the others" is **CONFIRMED**. The other two directions were not
checked in this lane.

Its actual neighbourhood, for anyone building the §9.4 shared instance set — all pulled from
AuditFlow's own reference list, `VERIFIED-AT-SOURCE` as *references that exist in that bibliography*,
`UNVERIFIED` as papers I opened:

| Reference | arXiv |
|---|---|
| Herculean: An agentic benchmark for financial intelligence | 2605.14355 |
| FinRule-Bench: joint reasoning over financial tables and principles | 2603.11339 |
| FinReporting: agentic workflow for cross-jurisdiction disclosures | 2604.05966 |
| FinVault: benchmarking financial agent safety in execution-grounded environments | 2601.07853 |
| Guideline-grounded evidence accumulation for high-stakes agent verification | 2603.02798 |
| XBRL Agent: LLMs for financial report analysis (Han et al., 2024) | — |

### 2.7 Where this fits in L0–L7, and where it stops

**Fits:** it is the closest published analogue to the whole system. **L1** ↔ its static US-GAAP taxonomy
graph + dynamic XBRL filing graph built from the artifact. **L4/L5** ↔ its typed deterministic checkers
returning verdict + reported value + expected value + evidence trail. It even emits a "trustworthiness
score," which is a weaker cousin of the coverage fraction. Cite it as **"an independent group converged
on the same generation/verification split, and measured that the deterministic half carries the
result."**

**Where it stops:** US-GAAP XBRL only — a machine-readable taxonomy with a pre-existing public
ruleset. **The IFSCA FME workbook has none of that**: no taxonomy, no rule identifiers, no calculation
linkbase — it has 294 native formulas of which the operator measured only 38 to express a checkable
relationship. AuditFlow gets to *traverse* a calculation tree; L1 has to *induce* one. It also stops at
n=67, three rule families, one filing type, no code, no released data, self-benchmarked.

---

## PART 3 — arXiv:2605.18812 · VERDICT: **VERIFIED ID / MISMATCHED ATTRIBUTION**

### 3.1 What the identifier actually resolves to

- **URL:** `https://arxiv.org/abs/2605.18812` — resolves. `VERIFIED-AT-SOURCE`
- **Title (exact):** *PASC: Pipeline-Aware Conformal Prediction with Joint Coverage Guarantees for
  **Multi-Stage NLP and LLM Pipelines***
- **Author:** **Varun Kotte** — single author, no affiliation, no venue/comments field
- **v1:** 12 May 2026 08:23:12Z · cs.LG; cs.CL; cs.IR

### 3.2 The attributions, checked

| Brief's claim | Reality | Verdict |
|---|---|---|
| Title *"PASC: Pipeline-Aware Conformal Prediction"* | correct as a short form; full title ends **"for Multi-Stage NLP and LLM Pipelines"** | **CONFIRMED** |
| "joint coverage guarantees for multi-stage information-extraction pipelines" | the paper says **"NLP and LLM Pipelines"**; its worked pipeline is NER → NED → entity typing, which *is* an IE pipeline. Paraphrase is defensible. | **QUALIFIED** |
| **"names financial documents as a target"** | **The word "financial" appears exactly ONCE in the entire paper**, in the Introduction, in a list of application areas: > "powering applications in biomedical text mining, **financial document analysis**, and knowledge-graph population". "finance" — absent. "invoice" — absent. "table extraction" — absent. Nothing financial in the experiments, baselines, datasets or future work. | **REFUTED as written** |

**Datasets actually used** (`VERIFIED-AT-SOURCE`): **CoNLL-2003** (1,000 calibration + 500 test),
**WNUT-17** (500 test, shift), **WikiNEuRal** (500 test, shift). All newswire/Twitter/Wikipedia NER.
**Zero financial documents.**

This is the lane's clearest failure. `RND-BRIEF.md` §6.1 lists this paper as **ⓞ — "verified by the
operator at source."** It was not. And the ⓞ mark sits on the one row in the table containing a claim
that does not survive contact with the paper. That is the brief's own working rule #3 —
*"open the instrument and read the clause off the page"* — failing on the brief's own reference table.
**It belongs in §4.4 as a third self-demonstration**, and it is a better one than the two already
there, because the false claim was *warranted at the highest level in the document.*

### 3.3 What the paper actually delivers — which is stronger than the brief knew

All `VERIFIED-AT-SOURCE`:

**Theorem 6 (PASC Joint Coverage Guarantee):**
> "Let {(xᵢ,{yₖ,ᵢ})}ᵢ₌₁ⁿ⁺¹ be exchangeable. Let q̂ be the PASC quantile … Then:
> ℙ(⋂ₖ₌₁ᴷ{sₖ(xₙ₊₁,yₖ,ₙ₊₁)≤q̂}) ≥ 1−α. Moreover, the guarantee is nearly tight:
> ℙ(⋯) ≤ 1−α+1/(n+1)"

Mechanism: reduce K-stage joint coverage to **one scalar conformal problem on the joint maximum
nonconformity score** — one quantile computation, not K.

| Result | Value | Denominator |
|---|---|---|
| End-to-end coverage, 3-stage NER→NED→typing, CoNLL-2003 | **96.4%** | 1,000 cal / 500 test |
| vs Bonferroni union bound | 93.4% | same |
| vs independent per-stage CP | 86.5% | same |
| average prediction set size | **1.083, identical across methods** | — |
| under shift (WNUT-17 / WikiNEuRal) | PASC holds target; **independent CP collapses to 59%** | 500 test each |
| at K = 6 stages | independent CP drops to **0.53** end-to-end coverage | — |
| calibration speed vs Bonferroni | **1.7× faster** | — |

The "identical set size at higher coverage" result is the useful one for L2: joint coverage is bought
without widening the prediction set, i.e. **without increasing the abstention rate**. That is a real
argument for using PASC's reduction rather than Bonferroni in L2.

### 3.4 THE SAME AUTHOR'S SECOND PAPER — and it may matter more than PASC

Found while searching for corroboration: **arXiv:2606.29054**, *"When Can Conformal Risk Control
Certify LLM Outputs? Bounds, Impossibility, and Adaptation for Structured Generation"*, **Varun Kotte**,
submitted 27 Jun 2026. `VERIFIED-AT-SOURCE` (abstract page).

> "when the base risk (μ > α), any distribution-free method must abstain on at least
> **((μ−α)/(1−α))** examples"

Reported consequences: at **α = 0.10**, "hard NER/QA/CLS configurations are **uncertifiable**";
"relaxing to α = 0.30–0.40 unlocks practical certification (**47% NER, 40% QA, 60% CLS**)"; heuristic
abstention policies miss user-specified risk targets by **7.5–12.5%**; the framework cuts risk
violations from **71% to 21%** under distribution shift, with "residual failures concentrated exactly
where the impossibility bound predicts."

**This is directly load-bearing on L2 and it is good news dressed as bad news.** It gives a
**closed-form pre-deployment feasibility test**: given the extractor's base error rate μ and the target
risk α, you can compute *before building anything* the minimum fraction of the artifact that must go to
`UNCHECKED`. That is not an obstacle to the design — **it is the design**. The brief's central product
claim is "declare the boundary of what you checked"; this paper says the boundary has a
**distribution-free lower bound you can compute in advance**, and that at strict risk targets the
honest answer is "this cannot be certified at α=0.10, only at α=0.30." A system that says that is
exactly the system the brief describes.

**Caveat, stated plainly:** both PASC and this are **single-author, unaffiliated, unrefereed preprints
by the same person**, and the brief has already miscited one of them. Treat the *theorem statements* as
things to re-derive rather than to cite. The impossibility bound (μ−α)/(1−α) is elementary enough to
verify by hand in an afternoon — **do that before it reaches a slide.**

### 3.5 Real, refereed prior art for the same L2 role — so the brief is not dependent on one preprint

| Work | Status | Role |
|---|---|---|
| **Mohri & Hashimoto, "Language Models with Conformal Factuality Guarantees"**, arXiv:2402.10978, **ICML 2024** (`proceedings.mlr.press/v235/mohri24a.html`) | `SECONDARY` (search + PMLR listing seen; paper not opened in this lane) | The refereed anchor for conformal-style correctness guarantees on LM output. Back-off algorithm: progressively make outputs *less specific* until the guarantee holds. **This is the citation to lead with, not PASC.** |
| **"Decomposition-Based Modular Conformal Prediction for Two-Stage Modeling"**, arXiv:2510.04406 | `UNVERIFIED` (search hit only) | Independent multi-stage conformal work; a second opinion on PASC's problem |
| **"A Multistage Extraction Pipeline for Long Scanned Financial Documents: An Empirical Study in Industrial KYC Workflows"**, arXiv:2604.26462 (Han, Zhang, Wang, Jin, Ke, Zhao; 29 Apr 2026) | `VERIFIED-AT-SOURCE` | **The financial-document IE evidence PASC does not provide.** 4 stages (preprocess → multilingual OCR → hybrid page retrieval → compact VLM extraction) on **120 production KYC documents, ~3,000 scanned pages**; **+31.9 percentage points** field-level accuracy; best config **87.27%** (PaddleOCR + MiniCPM2.6). **Reports field-level accuracy, and — consistent with the brief's §6.2 finding — does not report per-cell numeric error.** |

**If the brief wants a sentence about conformal abstention in financial document pipelines, build it
from Mohri & Hashimoto (refereed) + 2604.26462 (real financial documents, real denominators) and use
PASC only for the joint-coverage-across-K-stages mechanism.**

### 3.6 Where this fits in L0–L7, and where it stops

**Fits:** **L2** exactly — "emit a prediction set, abstain when not a singleton" across the
extraction→key-binding chain. PASC's contribution is that the abstention budget can be spent *once,
jointly*, rather than per-stage with a Bonferroni penalty. 2606.29054 supplies the feasibility test
that tells you whether L2's target risk is reachable at all.

**Where it stops:** newswire NER. No financial document, no spreadsheet, no merged-header workbook, no
numeric cell. Exchangeability is assumed — **a filing corpus that drifts across template versions is
not exchangeable**, and the brief's own §4.2 finding that 23.1% of circulars amend an earlier
instrument is precisely a drift generator. Calibration needs labelled key-bindings, which
`ARCHITECTURE.md` Part 5 already lists as risk #3 and which do not exist yet.

---

## PART 4 — arXiv:2603.21172 · VERDICT: **VERIFIED (title incomplete; claim under-read)**

### 4.1 What the identifier actually resolves to

- **URL:** `https://arxiv.org/abs/2603.21172` — resolves. `VERIFIED-AT-SOURCE`
- **Title (exact):** *Entropy Alone is Insufficient for Safe Selective Prediction **in LLMs*** — the
  brief drops the last two words.
- **Authors:** **Edward Phillips, Fredrik K. Gustafsson, Sean Wu, Anshul Thakur, David A. Clifton**
  — Department of Engineering Science, **University of Oxford** (`SECONDARY`: co-author Gustafsson's
  own site, `fregu856.com`, "Postdoc in Oxford").
- **v1:** 22 Mar 2026 11:27:13Z · cs.CL · no venue/comments field.

**This is the most credible of the four by provenance** — five named authors, an identifiable
established group (Clifton's Oxford lab), and an independently verifiable author homepage. The other
three are single-author unaffiliated preprints.

### 4.2 The attribution, checked

The brief's §6.1 says only: *"Kills the naive confidence-threshold version of abstention."*
**Directionally CONFIRMED, but it is half the paper**, and the half it drops is the useful half.

Abstract, verbatim:
> "We identify a **model-dependent failure mode** of entropy-based uncertainty methods that leads to
> unreliable abstention behaviour, **and address it by combining entropy scores with a correctness
> probe signal.** We find that across three QA benchmarks (TriviaQA, BioASQ, MedicalQA) and four model
> families, the combined score generally improves both the risk--coverage trade-off and calibration
> performance relative to entropy-only baselines."

**The failure mode, precisely** (`VERIFIED-AT-SOURCE`, full text):
> "Many answers, both correct and hallucinated, **collapse to SE=0**, yet receive distinct PC probe
> scores."
Severe in Qwen, where "a substantial fraction of questions are assigned near-zero semantic entropy"
despite being incorrect. The authors name this the **"confidently wrong regime"** — low-entropy
hallucinations. Entropy-only methods exhibit **risk floors that prevent operating at strict safety
targets** at all.

**The repair:** a **"correctness probe" (PC)** — a *logistic regression classifier* over prompt
representations, trained on binary correctness labels derived from LLM-as-judge assessment.

**Experimental denominators** (`VERIFIED-AT-SOURCE`): **1,000 examples per dataset, split 70:15:15**
(train/calibration/test), three benchmarks, four model families (Llama 3.2 3B, Qwen3 4B, Gemma 3 4B,
Ministral 8B). Target risk levels **α ∈ [0.05, 0.30]**.

Selected numbers: semantic-entropy AUROC on TriviaQA — **Llama 3.2 3B 0.884, Qwen3 4B 0.844, Gemma 3
4B 0.752, Ministral 8B 0.823**. Combined PC+SE on BioASQ / Ministral 8B: **E-AURC 0.114, TCE 0.061**.
MedicalQA base accuracy ranged **17.3% (Gemma) to 23.3% (Qwen, Ministral)** — note how low that is;
these are small models on a hard task.

### 4.3 Two things the brief should change

1. **The paper is constructive, not purely destructive.** It does not merely kill entropy-thresholding;
   it offers a cheap, deterministic-to-run repair — **entropy + a logistic-regression correctness probe
   over prompt representations**. That is a *component for L2*, not just a warning. And it rhymes with
   2606.09863's finding: in both papers a **small supervised classifier over cheap features beats the
   model's own self-assessment.** Two independent papers, two different domains, same shape of answer.
   That is a pattern worth stating in the brief as a design principle rather than two isolated facts.
2. **The probe needs labels.** Its correctness labels come from **LLM-as-judge** — and the brief's own
   Part 1 fact #3 says LLM judges detect false success at AUROC ≤0.65. Using an LLM judge to label the
   training set of the thing that fixes the LLM's self-assessment is not fatal (the tasks differ: QA
   correctness vs agent-trajectory false success) but **it must be declared**, because it is exactly
   the circularity the brief's §2.3 point 4 names as the crux.

### 4.4 Where this fits in L0–L7, and where it stops

**Fits: L2 only.** It kills the naive `confidence > τ → assert` design and supplies the alternative
(auxiliary probe + conformal-style calibration on a held-out set), plus the concrete phenomenon —
the confidently-wrong regime — that explains *why* self-reported confidence cannot gate a filing
assertion. Pairs with 2606.29054's feasibility bound: entropy gives you no usable risk floor, and the
impossibility result tells you what floor is achievable at all.

**Where it stops:** free-form QA with 3B–8B open models, 1,000 examples per dataset, no structured
extraction, no numeric fields, no finance, no regulated artifact. The probe is trained per
model/dataset — **it does not transfer.** And "generally improves" is the paper's own hedge; it is not
a uniform win.

---

## PART 5 — SUMMARY TABLE

| ID | Resolves? | Title as attributed? | Numbers check out? | Verdict |
|---|---|---|---|---|
| **2606.09863** | **YES** | n/a (no title given in brief) | **All six numbers CONFIRMED with denominators** | **VERIFIED** |
| **2606.03031** | **YES** | "AUDITFLOW" → *AuditFlow* (styling) | **82.09 / 17.91 / n=67 all CONFIRMED** — but the brief's **"+64pts"** framing is a self-ablation misused as a method comparison; the real baseline gap is **14.93pts**; ~half the collapse is invalid outputs; 95% CI **[75.8, 90.2]** | **VERIFIED (numbers) / MISUSED (inference)** |
| **2605.18812** | **YES** | title truncated: full title is "…Multi-Stage **NLP and LLM** Pipelines" | joint-coverage claim CONFIRMED and stronger than stated; **"names financial documents as a target" REFUTED** — one passing mention in the Introduction, zero financial experiments | **MISMATCHED ATTRIBUTION** |
| **2603.21172** | **YES** | title missing "**in LLMs**" | claim directionally CONFIRMED but **under-read** — the paper supplies a repair the brief omits | **VERIFIED (incomplete)** |

**Provenance quality, which the brief does not currently record anywhere:**

| ID | Authors | Affiliation | Venue | Code/data |
|---|---|---|---|---|
| 2606.09863 | 1 (Laksh Advani) | **none stated** | none | **none** |
| 2606.03031 | 10 | not extracted | none stated | **none** ("we do not redistribute…") |
| 2605.18812 | 1 (Varun Kotte) | **none stated** | none | not found |
| 2603.21172 | 5 | **Oxford** (`SECONDARY`) | none stated | not found |

**Three of four are unrefereed preprints with no code and no released data.** Two of those three are
single-author with no stated affiliation. This does not make them wrong — 2606.09863's method section
is unusually careful and its Limitations section is more honest than most published work — but it does
mean **none of them can be cited as authority.** They can be cited as *reported measurements whose
method is described and whose denominators are stated*, which is what the brief's own warrant
discipline demands anyway.

---

## PART 6 — REPAIRS TO MAKE IN THE BRIEF (concrete text)

**§6.1, PASC row — replace the "Verified" mark and the description.**
Current: `ⓞ | L2 abstention with joint coverage guarantees for multi-stage IE pipelines; names financial documents as a target`
Replace with:
> `ⓞ` *(now genuinely opened)* | **PASC**, arXiv:2605.18812 — joint conformal coverage across K pipeline
> stages via a joint-maximum nonconformity score; 96.4% vs 93.4% Bonferroni vs 86.5% independent CP at
> identical set size 1.083, on CoNLL-2003 NER→NED→typing. **Evaluated on newswire NER only; finance
> appears once, in the Introduction, as a motivating application. Single-author preprint, no venue.**

**§6.1, AUDITFLOW row.**
> **AuditFlow**, arXiv:2606.03031 — **82.09% joint audit accuracy, 95% CI [75.8, 90.2], n=67**
> (22×DQC.US.0015 + 24×DQC.US.0117 + 21×DQC.US.0126), **+14.93pts over the strongest baseline**;
> ablating the deterministic checkers drops it to 17.91% **and raises invalid outputs from 1.49% to
> 35.82%**. Same group as the FinAuditing benchmark it evaluates on. No code or data released.

**§3.2, "Wrap in deterministic checks" row.** Replace `AUDITFLOW 82.09% → 17.91% on ablation (n=67)`
with: `AuditFlow: removing the deterministic checkers costs 64.18pts on n=67 (82.09%→17.91%), about
half of it as unparseable output; the method's advantage over the best baseline is 14.93pts`.

**§3.3, add a row — the missing evidence:**
> **Dual-control collapses silent failure: 45–47% → 3%** when the environment can independently verify
> state (arXiv:2606.09863, telecom domain, 442 failures). The author generalises: *"any benchmark with
> independent state-verification will suppress false success."* ⓞ

**§3.3, add the precision qualifier:**
> The TF-IDF detector's **precision at a 10% flag rate is 50%** — half of flagged trajectories are
> false alarms; it degrades to AUROC 0.69 zero-shot across domains and **flips on 20–25% of cases under
> a stylistic rewrite attack.** ⓞ

**§4.4, add a third self-demonstration:**
> 3. **A reference row marked ⓞ ("verified at source") carried a claim that is not in the paper.**
>    PASC (arXiv:2605.18812) was recorded as naming financial documents as a target. The word
>    "financial" occurs once, in the Introduction, in a list of motivating domains; every experiment is
>    newswire NER. **The false claim carried the document's highest warrant mark.** Third instance of
>    clean, confident, well-formed output that was wrong.

**§6.2, rules-as-code row — the claim needs its denominator.**
Current: *"zero financial regulations encoded anywhere."* Defensible restatement:
> **Within the general-purpose rules-as-code ecosystem (Catala, OpenFisca, Blawx, finos/open-reg-tech-us-lcr),
> zero financial regulations are encoded, and the FINOS demonstrator sits at 16★ with no commit since
> 5 Jun 2024.** **But domain-specific filing-validation rulesets do exist and are institutionally
> durable:** XBRL US's **DQC ruleset** (`github.com/DataQualityCommittee/dqc_us_rules`, **31★, 39 forks,
> 6,309 commits**, Python + the Xule rule language on the Arelle processor, custom AICPA/XBRL-US
> licence) is a maintained registry of executable validation predicates over US-GAAP and IFRS filings,
> each with a stable rule identifier. **The gap is not that nobody writes executable filing checks — it
> is that nobody publishes a coverage declaration or a per-rule false-failure rate alongside them.**

That last sentence is a **stronger** pitch than the current one, because it survives contact with an
XBRL-literate judge and it relocates the novelty from "we encode rules" (someone already does) to
"we declare what the rules do not cover, with measured error rates" (nobody does).

---

## PART 7 — WHAT THIS CHANGES ABOUT THE DESIGN

**1. The architecture just acquired its first external effect size, and it is large.**
Until now, the claim "adjudicate every model output with a deterministic layer" was a design principle
justified by the *absence* of a working alternative. The dual-control result in 2606.09863 makes it a
**measured intervention**: independent state verification took false success from 45–47% to **3%** of
failures, a ~15× reduction, on 442 failures in a domain the authors did not construct for this purpose.
**Put this on the slide.** It is the only number in the entire corpus that says the proposed fix works
rather than that the alternatives fail.

**2. L2 gains a pre-deployment feasibility test, and the honest answer may be "α=0.10 is impossible."**
arXiv:2606.29054's bound — abstain on at least **(μ−α)/(1−α)** when base risk μ exceeds target α —
converts L2's abstention rate from a tuning outcome into a **computable lower bound known before any
code is written**. Two consequences. (a) It should be run *first*, on paper, using the operator's own
§4.3 numbers, because it may say the L2 conformal step is infeasible at any risk level a regulator
would accept — which would be a genuine, cheap, pre-registered kill. (b) If it says α=0.30 is the
reachable target, **that is not a failure of the product, it is the product**: a system whose headline
is "I can certify at 30% risk and here is what I could not touch" is the coverage-declaring artifact
the brief describes. The impossibility result is the strongest theoretical support the design has.

**3. "Precision is the scarce quantity" now cuts against the brief's own preferred detector.**
The TF-IDF detector runs at **50% precision at a 10% flag rate**. The brief cannot hold up 72% recall
as the answer to the LLM judge's 13% without also stating that half the flags are wrong — that is the
exact failure mode §2.3 point 1 is about. **This strengthens rather than weakens L4:** it is a
concrete, external instance of why every admitted predicate must carry its own measured false-failure
rate, which is precisely L4 test 3. Use it as the worked example.

**4. A repeated empirical shape has emerged and should be promoted to a design principle.**
2606.09863: TF-IDF + a small supervised classifier (0.825–0.953 AUROC) beats every LLM-judge
configuration (≤0.65) at 3,364× lower latency. 2603.21172: entropy + a **logistic-regression**
correctness probe beats entropy-only self-assessment. Two independent papers, two unrelated domains,
same answer: **a cheap supervised classifier over surface features beats the model's own
self-assessment.** The design already refuses to let a model be the final judge; it should also state
positively that **where a judgement signal is needed, the first thing to try is a small trained
classifier, not a bigger prompt.** That is a testable, afternoon-scale claim, and it is cheap enough to
run inside L4 as a fourth qualification test.

**5. AuditFlow is the strongest "someone already did an adjacent version" signal in the corpus — and
its stopping point is exactly our opening.** It has a taxonomy, a rule identifier scheme, a
calculation linkbase, and a published ruleset (DQC) to draw checks from. **The IFSCA FME workbook has
none of these.** So the AuditFlow result — that the deterministic layer carries the verification — is
*evidence for our thesis*, while the thing that makes AuditFlow possible is *the thing L1 has to
manufacture from a protected .xlsx.* That contrast is a better answer to "why hasn't this been done"
than anything currently in the brief: **it has been done, in the one jurisdiction and format where a
machine-readable taxonomy already exists.**

**6. The novelty claim must move, and it survives the move intact.**
"No executable financial rules exist" is false in the XBRL/DQC world and will be challenged. "No
system publishes a coverage declaration and a per-rule false-failure rate alongside its checks" is
still true — DQC publishes rules but not their FFR; CycloneDX declares completeness but only for
software. **L4 + L5 + L7 (measured error rate per predicate, closed-vocabulary UNCHECKED reasons,
signed coverage) remain unoccupied.** Move the novelty claim there and it becomes defensible against a
domain expert instead of dependent on one not being in the room.

**7. Warrant hygiene: the ⓐ/ⓞ marks in §6.1 are not reliable and should be re-audited.**
Two of these four IDs carried **ⓞ** in §6.1 despite never having been opened, and the false attribution
was on one of them. §9.5 asked for all ⓐ papers to be verified; **the ⓞ rows need the same treatment**,
because the mark is currently being assigned by confidence rather than by act. Cheapest possible fix:
any row whose ⓞ cannot be traced to a specific opened URL gets demoted to ⓐ today.

---

## PART 8 — WHAT DID NOT GET CHECKED (declared gaps)

1. **Semantic Scholar was never reached** — HTTP 429 on both attempts. The four papers therefore have
   **no citation counts and no independent bibliographic-database confirmation.** `UNVERIFIED`.
2. **Peer-review status of all four is unknown.** None has a `Comments:` venue field. Absence of a
   venue field is not proof of non-publication. `UNVERIFIED`.
3. **FinMR's full size** — AuditFlow's 67-instance sampling fraction cannot be computed. FinAuditing
   totals 1,102 instances across three subtasks; the FinMR-specific count was not obtained.
4. **FinAuditing's "13.86% best model on FinMR"** is `SECONDARY` (search-index summary of 2510.08886),
   not read in the paper body.
5. **DQC current rule-set version and total rule count** — `UNVERIFIED`. A third party reports a "20th
   Rule Set"; I did not confirm at source. The **licence I did read at source**; the version I did not.
6. **The two other legs of the §9.4 contradiction.** I confirmed AuditFlow cites neither FinVerBench
   nor FinBalance. I did **not** check whether FinVerBench or FinBalance cite the others.
7. **arXiv:2606.29054's impossibility proof was not verified** — I read the abstract, not the proof.
   The bound is simple enough to re-derive; **do that before quoting it.**
8. **Mohri & Hashimoto (2402.10978) was not opened in this lane** — `SECONDARY` via search + a PMLR
   v235 listing. It is the refereed anchor and deserves a first-hand read.
9. **`huggingface.co/papers/2606.09863` returned 404.** This is **not** evidence of non-existence — HF
   Papers indexes only submitted papers, so it is a different corpus from arXiv. Recorded so nobody
   later mistakes it for a failed resolution.

---

## PART 9 — BONUS: ADJACENT IDs SURFACED, ALL RESOLVED AT SOURCE

Found while running corroboration searches. Each of these is a real, resolving arXiv record; the
annotations are from abstract pages unless marked.

| ID | Title | Why it matters |
|---|---|---|
| **2510.08886** | FinAuditing: A Financial Taxonomy-Structured Multi-Document Benchmark for Evaluating LLMs | The parent benchmark. **1,102 instances**, real US-GAAP XBRL, three subtasks, HF-hosted. The realistic evaluation substrate for an L5 analogue. |
| **2605.29586** | FinVerBench: Benchmark Validity and Calibration in LLM Financial Statement Verification | **Confirms two of the brief's §3.1/§3.2 numbers at source:** "nine of fourteen complete LLM runs produce 95-100% false positives on clean statements"; **105-instance observable diagnostic subset (43 clean, 62 error-injected)**; rounded variant recall **79.0% at 0% observed FPR vs 100.0%** unrounded — **the 21-point recall loss the brief cites.** Single author (Silu Panda). |
| **2606.29054** | When Can Conformal Risk Control Certify LLM Outputs? Bounds, Impossibility, and Adaptation | The L2 feasibility bound. See §3.4. |
| **2604.26462** | A Multistage Extraction Pipeline for Long Scanned Financial Documents (KYC) | 120 production documents / ~3,000 pages; +31.9pp field accuracy; 87.27% best. Real financial-document IE denominators. |
| **2505.00212** | Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems | The **Who&When** benchmark: 127 multi-agent systems' failure logs. Best method **53.5%** at identifying the responsible agent, **14.2%** at the decisive step. `SECONDARY` — independent corroboration that failure attribution runs near chance. |
| **2606.08345** | AuditFraudBench: Benchmarking Audit Judgment in Detecting Fraudulent Misstatements | Marked "Work in progress"; **no quantitative results published yet.** Watch, don't cite. |
| **2604.22708** · **2606.02060** · **2509.08682** | Failure-attribution benchmarks & span-level error localization in agent trajectories | The live research front on exactly the brief's §2.2 framing. `UNVERIFIED` beyond search listings. |

---

## Adversarial verification (independent pass)

**Run 10 Aug 2026, by a separate agent instructed to refute rather than to agree.** Nothing below was
taken from this lane's citations. Every identifier was re-resolved through `export.arxiv.org/api/query`
and every quoted sentence was re-read in the paper's own `arxiv.org/html/<id>v1` full text, pulled
fresh. Repository statistics and the DQC licence were read on GitHub, not from this lane's summary of
them. Where this lane and I agree, I re-derived the number rather than checking it off.

**Bottom line: this lane's factual spine holds. Its editorial spine does not, in one specific place.**
Every identifier resolves. Every number I could reach is in the paper, at the stated denominator, and
several are verbatim. Two claims are refuted — one trivial, one that matters — and the one that matters
is the lane's own headline recommendation.

### V.1 — REFUTED: "no venue, none refereed, none can be cited as authority"

The lane states at §1.1, marked `VERIFIED-AT-SOURCE`: *"**Comments field:** none. **No venue.**"* for
arXiv:2606.09863. It repeats this in the Part 5 provenance table (venue: "none" for all four) and again
in Part 8 declared-gap #2: *"None has a `Comments:` venue field."*

The abstract page carries a Comments field. Read at source, `arxiv.org/abs/2606.09863`, and independently
in the Atom API as `<arxiv:comment>`:

> **Accepted to FAGEN@ICML2026**

So the paper the lane calls the corpus's strongest external evidence is *workshop-accepted at ICML 2026*,
not an unrefereed orphan. The same error appears in Part 9: FinAuditing (2510.08886) carries
`Accepted by SIGIR 2026 Resource Track. Pre-camera-ready version`, which the lane's annotation omits.

Two knock-on corrections:

- Part 5's conclusion — *"Three of four are unrefereed preprints... **none of them can be cited as
  authority**"* — is built on a field the lane did not read. The correct count is **two** of four with
  no venue field (2605.18812, 2603.21172); 2606.09863 has one, and 2606.03031 does not.
- Part 8 gap #2 should be struck, not softened.

**This is the same failure the lane diagnoses in the brief at §3.2, one level up.** The lane's §4.4
repair text tells the brief that a row marked ⓞ carried a claim not in the paper. The lane then marks
`VERIFIED-AT-SOURCE` on a metadata field whose value contradicts it. Part 7 item 7 ("the ⓞ marks are
being assigned by confidence rather than by act") applies to this document.

### V.2 — QUALIFIED, and the qualification guts the recommendation: the dual-control result

This is the most consequential finding of my pass, because Part 7 item 1 says **"Put this on the slide"**
and calls it *"the only number in the entire corpus that says the proposed fix works."*

The number is real. §4.1 of the paper, re-read at source, says exactly what the lane quotes. But the
**next two sentences**, which appear nowhere in this lane, are:

> "**We treat this as an observation rather than a causal claim: only one dual-control domain is
> available, with 15 FS cases, which is insufficient to isolate environment structure from other domain
> differences.** The pattern is consistent with an independent verification mechanism suppressing the
> failure mode, **but confounds remain. We flag this as a hypothesis warranting future study across
> multiple dual-control environments.**"

Three separate problems follow.

1. **The denominator is wrong by presentation.** Part 7 item 1 says the effect was measured *"on 442
   failures."* 442 is the telecom failure count. The effect is carried by **15 false-success events**.
   Quoting 442 next to a 15-event effect is the precise move the brief's own working rule #2 forbids,
   and this lane exists to enforce that rule.
2. **The lane's derived count is wrong.** §1.3 computes *"442 telecom failures → roughly 13 false
   successes."* The paper states **15**, twice (§4.1 and the LODO note in §4.2). A derived number that
   disagrees with the paper's stated number should never have shipped from a lane whose job is to read
   the paper.
3. **The author refuses the causal reading; the lane supplies it.** §1.3 calls it *"a ~15× collapse in
   silent failure produced by nothing more than adding an independent verifier"* and Part 7 upgrades it
   to *"a measured intervention."* It is neither an intervention nor a controlled comparison. It is one
   observational domain difference, n=15, confounded by the author's own admission, in a benchmark where
   telecom also differs in task mix, tool schema and difficulty. The paper's Limitations section adds
   that the **airline↔retail LODO** result was reported in the main body precisely *because* "telecom
   has only 15 FS cases."

The lane also notices, correctly, that the brief kept the alarming halves of this paper and dropped the
reassuring half, and attributes that to the standing bias in Part 11. **The selection ran in the
opposite direction here.** The reassuring half was retained and its disclaimer dropped. Same mechanism,
mirrored.

**What survives:** a hypothesis, explicitly labelled as such by its author, that independent state
verification suppresses false success, with a suggestive but confounded n=15 observation attached. That
is still worth carrying — it is genuinely the closest thing in the corpus to evidence *for* the design.
It is not a measured effect size and it must not go on a slide as one. An XBRL-literate judge would not
catch this; a statistician would, in about ninety seconds, and the recovery is ugly because the lane
recommended the slide.

**Replacement text for Part 7 item 1:**
> The architecture has its first external result pointing the right way, and it is a hypothesis, not an
> effect size. In tau2-bench, false success runs 45–47% of failures in the two single-control domains
> and 3% in the one dual-control domain where the user simulator can independently verify state
> (arXiv:2606.09863 §4.1). **The author declines to call this causal: one domain, 15 false-success
> cases, confounds unresolved, flagged as "warranting future study."** Carry it as the paper carries
> it. It is directionally the best support the design has and it is not yet a number.

### V.3 — CONFIRMED: all four identifiers, and the method that established them

Re-run independently, not read off this lane.

| ID | Resolves | Title matches lane | Date matches |
|---|---|---|---|
| 2606.09863 | yes | yes | 2026-06-01T00:13:23Z ✓ |
| 2606.03031 | yes | see V.6 | 2026-06-02T02:14:42Z ✓ |
| 2605.18812 | yes | yes | 2026-05-12T08:23:12Z ✓ |
| 2603.21172 | yes | yes | 2026-03-22T11:27:13Z ✓ |

The negative control replicates exactly. Requesting six IDs
(`2606.99999, 2612.00001, 2699.12345, 2606.30000, 2603.30000, 2606.25000`) returns
`opensearch:totalResults = 3`: the three real ones present, the three impossible ones silently absent.
A single-ID query for `2606.99998` returns `totalResults = 0`. **The API discriminates. The lane's
Part 0 is sound and its conclusion is earned.**

The ID-grammar and volume probes also replicate: `2603.30000` → 2026-03-31, `2606.30000` → 2026-06-29,
`2606.25000` → 2026-06-23; `2606.00001` → 2026-03-24 and `2605.00001` → 2026-01-20, confirming the
announce-vs-submit gap that explains the 2606.09863 ordering anomaly. arXiv's own stats page returns
*"Total number of submissions as of August 10, 2026 = 3,128,807"* verbatim. Nothing anachronistic
anywhere in the set.

### V.4 — CONFIRMED verbatim: the 50%-precision correction

The lane's §1.4 item 1 is the correction most likely to be challenged, so I read it twice. It is
verbatim, and it appears **twice** in the paper (§4.4 Deployment scoping, and again in §5 Limitations):

> "The detector is a triage signal, not an autonomous monitor. At a 10% flag rate, precision is 50%:
> half of flagged trajectories are false alarms."

Table 6 gives the full operating curve with bootstrap CIs, which the lane does not carry and should:

| Flag rate | Detector recall | Detector precision | Judge recall | Judge precision |
|---|---|---|---|---|
| 5% | 51% [43,59] | **72% [57,86]** | 6% [3,10] | 56% [22,89] |
| 10% | 72% [63,80] | **50% [40,60]** | 13% [8,17] | 58% [32,79] |
| 20% | 89% [82,95] | **31% [24,38]** | 25% [18,31] | 55% [39,71] |

**Note what this table does to the brief's thesis, harder than the lane states.** The *judge's* precision
is 55–58% at every flag rate — flat, and at 10% and 20% it is **higher than the detector's**. The
detector wins on recall by 4–8× and loses or ties on precision. If "precision is the scarce quantity"
(§2.3 point 1), the honest reading is that **neither method supplies it, and the detector's advantage is
entirely on the axis the brief calls free.** That is a sharper version of the lane's point and it should
replace it.

Also confirmed at source, all as the lane reports: 3,364× (1.19 ms CPU vs ~4,000 ms API call, §4.4);
TF-IDF+LR 0.849 > XGBoost 0.825±0.025 task-disjoint; LODO 0.69 zero-shot; **50–100 labeled examples per
class → 0.79–0.83**; the adversarial rewrite flip. One denominator the lane dropped: the rewrite test is
**11/45 = 24%** of trajectories with explicit failure markers, n=45. Quote the 45.

### V.5 — REFUTED (warrant, not fact): the 35.6% is not derived, it is stated

§1.2 of this lane presents *"the pooled tau2-bench false-success rate is 616 / 1,730 = 35.6%"* as
*"`VERIFIED-AT-SOURCE` inputs, arithmetic mine — label ⓧ."* The paper states it directly, §3.3:

> "This yields 616 false successes (**35.6% of failures**), 753 honest failures (43.5%), and 361
> ambiguous (20.9%)."

The correct mark is ⓞ. Small in itself; not small in a document whose Part 7 item 7 is about marks being
assigned by confidence rather than by act. A warrant that is *too weak* is still a wrong warrant, and it
means the lane re-derived a number it could have read, which is evidence the full text was skimmed in
places it claims to have been read.

### V.6 — CONFIRMED, with one reversal: AuditFlow

Every number checks out at source, including the ones the lane treats as its own discoveries:

- **95% CI [75.8, 90.2]** — Appendix G, Table 10, exactly where the lane says. Full row:
  `GPT-5.5 | 82.09 | 55/67 | [75.8, 90.2]`, B=10⁴ percentile bootstrap over 67 cases. ✓
- **22 × DQC.US.0015 + 24 × DQC.US.0117 + 21 × DQC.US.0126 = 67** ✓, plus a detail the lane missed and
  should carry: **29 10-K + 38 10-Q filings across 47 unique tickers.**
- **+14.93 points over Single Agent (67.16% → 82.09%)** — and the lane is right that this is *in the
  abstract*. Table 7 confirms: Single Agent 67.16, Herculean 65.67, TreeRAG 43.28, GraphRAG 48.39. ✓
- **1.49% → 35.82% invalid outputs on ablation** ✓. The lane's decomposition is arithmetically sound:
  55→12 correct, 1→24 invalid, so of 43 instances lost ~23 became unparseable and ~20 well-formed-wrong.
- **"We do not redistribute raw SEC filing packages or proprietary model outputs as part of this paper"**
  — verbatim, in "Artifact Use and Licensing" ✓.
- **Cites neither FinVerBench nor FinBalance** — zero occurrences of either string in the full text ✓.
  Cites FinAuditing 23 times ✓.

**The reversal.** §2.1 of this lane says: *"The brief spells it 'AUDITFLOW'; the paper styles it
'AuditFlow'. Trivial, but fix it."* arXiv's canonical title record — the `<title>` returned by the API
and shown on the listing — is:

> **AUDITFLOW: Executable Symbolic Environments for Structured Financial Reporting Verification**

All caps. The body styles it *AuditFlow* (57 occurrences, 0 of `AUDITFLOW`), so both forms are defensible
and **the brief was already citing it as arXiv records it.** Do not make this "correction."

**One over-reach to trim.** §2.3(c) says the 14.93-point gap *"is **not** established as significant by
anything reported."* The paper does report paired bootstrap significance machinery — Appendix G, Table 11,
recentred bootstrap p-values following Berg-Kirkpatrick et al. (2012). It applies it to **backbone**
comparisons only, not to AuditFlow-vs-baseline. So the lane's substance survives, but the sentence as
written is falsifiable in one click. Correct form: *"the paper significance-tests backbone differences
and does not significance-test the method-vs-baseline gap; on n=67, 14.93 points is 10 instances."*

### V.7 — CONFIRMED: the PASC refutation, at exactly the strength claimed

Counted mechanically over the full text of 2605.18812:

| String | Occurrences |
|---|---|
| `financial` | **1** |
| `finance` | 0 |
| `XBRL` | 0 |
| `invoice` | 0 |

The single occurrence, Introduction, is precisely the sentence the lane quotes — IE pipelines "powering
applications in biomedical text mining, **financial document analysis**, and knowledge-graph population."
Every experiment is CoNLL-2003 / WNUT-17 / WikiNEuRal NER. **The brief's §6.1 claim that PASC "names
financial documents as a target" is refuted, and the lane's §4.4 repair text should go in as written.**
This is the lane's best work and it survives adversarial re-check intact.

### V.8 — CONFIRMED: the DQC ruleset and its licence

Read on GitHub, not from this lane. `github.com/DataQualityCommittee/dqc_us_rules`:
**31 stars · 39 forks · 6,309 commits · primary language Python**, Arelle plugin, Xule rule syntax — all
four figures match to the digit. The licence, read at `License.md`:

> Copyright © 2015-present, **American Institute of CPAs (AICPA)** · **Calcbench, Inc.** · **Toppan
> Merrill LLC** · **Workiva Inc.** · **XBRL US, Inc.**
> "…derivative works that comment on or otherwise explain it or assist in its implementation may be
> prepared, copied, published and distributed… **This document itself may not be modified in any way**…"

**Not OSI-approved. Not MIT, not Apache.** The lane's warning — a bespoke *document* licence, not a
software licence, read it in full before it enters a dependency list — is correct and load-bearing, and
Part 6's restated §6.2 novelty claim rests on facts that hold.

One thing to add: **AuditFlow's own footnote for DQC points to `fasb.org/projects/fasb-taxonomies/
dqc-rules-taxonomy`, not to the XBRL US repository.** The repo is this lane's find, not the paper's.
That strengthens the lane's §2.5 point rather than weakening it, but the provenance should say so.

### V.9 — CONFIRMED at abstract level; proof still unread (as the lane declares)

arXiv:2606.29054 resolves; abstract re-read at source. Every quantity the lane attributes is present
verbatim: the bound **(μ−α)/(1−α)**; heuristic abstention missing risk targets by **7.5–12.5%**;
ACI cutting violations **71% → 21%**; **uncertifiable at α=0.10**, and **47% NER / 40% QA / 60% CLS**
certified at α=0.30–0.40. Also present and worth carrying: *"six open-weight models (3B–72B), eight
datasets, four tasks, six nonconformity scores"* — the denominators the lane omits — and a
Hoeffding→Bernstein gain of **+37% certified configurations**.

**The proof remains UNVERIFIABLE in this pass too.** The lane's instruction to re-derive it before
quoting stands, and I did not re-derive it either. Do not let two agents' agreement that the abstract
says something become evidence that the theorem is true.

Adjacent confirmations, all re-resolved independently: **2510.08886** FinAuditing (16 authors, SIGIR 2026
Resource Track); **2605.29586** FinVerBench (Silu Panda, 37 pp) — and its numbers are exact:
*"nine of fourteen complete LLM runs produce 95–100% false positives on clean statements"*, the
**105-instance observable subset (43 clean, 62 error-injected)**, rounded recall **79.0% at 0% FPR vs
100.0%** unrounded (**−21.0pp**), and the rule verifier at **52.8% recall / 0% FPR**, i.e. the 47% miss.
**The brief's §3.1 and §3.2 top rows are sound at source.** **2604.26462** KYC pipeline; **2606.08345**
AuditFraudBench ("Work in progress"); **2402.10978** Mohri & Hashimoto, *"Proceedings of the 41st
International Conference on Machine Learning, PMLR 235:36029–36047, 2024"* — the refereed anchor is real
and the lane's advice to lead with it rather than with PASC is well founded.

### V.10 — One under-warranted mark, in the lane's favour

§4.1 marks the Oxford affiliation of 2603.21172 as `SECONDARY`, sourced to co-author Gustafsson's
personal site. It is stated in the paper itself, first page:

> Edward Phillips¹, Fredrik K. Gustafsson¹, Sean Wu¹, Anshul Thakur¹, David A. Clifton^{1,2}
> ¹ **Department of Engineering Science, University of Oxford** · ² Oxford Suzhou Centre for Advanced
> Research, University of Oxford, Suzhou · Correspondence: `edward.phillips@eng.ox.ac.uk`

That is `VERIFIED-AT-SOURCE`. Similarly, Part 5's provenance table records AuditFlow's affiliation as
"not extracted"; it is on the paper's first page (**The Fin AI, USA**, + Rensselaer and five others).
Both marks are too weak rather than too strong — the opposite of V.1 and V.5, and together they say the
marks in this lane were assigned by recollection at write-up time rather than by act at read time.

Everything else in 2603.21172 checks out: 1,000 examples per dataset, **70:15:15** stratified split,
α ∈ [0.05, 0.30], the four TriviaQA SE AUROCs (0.884 / 0.844 / 0.752 / 0.823), the *"confidently wrong
regime"* naming, the SE=0 collapse figure, and correctness labels from an **LLM-as-judge** pipeline
(Kossen et al. 2024) — so the lane's circularity warning at §4.3 item 2 is well placed.

### V.11 — What this pass did NOT check

1. **The impossibility proof of 2606.29054** — abstract only, same as the lane. Still unverified by anyone.
2. **Citation counts / peer-review status beyond the Comments field** — no bibliographic database reached.
   The venue facts in V.1 come from arXiv's own metadata, which records author-supplied claims of
   acceptance. **I confirmed the field exists and its content; I did not confirm with ICML that the paper
   was accepted.** An author-supplied comment is not proof of acceptance.
3. **FinMR's full size** — still unobtainable; AuditFlow's 67-instance sampling fraction remains unknown.
4. **FinBalance** — never resolved to an identifier by either pass. It is cited in the brief's §3.2, §3.3
   and §9.4 as one of three legs of the central contradiction and **it has no arXiv ID anywhere in this
   lane.** That is a larger gap than anything above: one third of experiment 9.4 is currently
   unidentified. Resolve it before 9.4 is scheduled.
5. **DQC current rule-set version and total rule count** — unverified here too.
6. **Whether FinVerBench or FinBalance cite the others** — unchecked, as the lane declares.

### V.12 — Net effect on the design

- **L4/L5 (deterministic adjudication) is unharmed and slightly better supported.** AuditFlow's numbers
  survive completely, including the CI and the 14.93-point honest baseline gap.
- **The claimed external effect size for the L4→L5 boundary is downgraded from measurement to
  hypothesis.** The design is not damaged; the *slide* is. Part 7 item 1 must be rewritten before it is
  presented, and this is the single actionable output of this pass.
- **L2 is unchanged.** PASC's refutation holds, the conformal feasibility bound holds at abstract level,
  and Mohri & Hashimoto is a genuine refereed anchor.
- **The §6.2 novelty relocation holds.** DQC is real, maintained, non-OSI-licensed and exactly as
  described; "nobody publishes a coverage declaration or a per-rule false-failure rate" survives.
- **Warrant hygiene is now a two-document problem.** Part 7 item 7 asked for the brief's ⓞ marks to be
  re-audited. This lane's `VERIFIED-AT-SOURCE` marks need the same audit, and V.1, V.5 and V.10 are the
  three worked examples. The cheapest fix is the one the lane itself proposed: any mark that cannot be
  traced to a specific opened URL and a quoted line gets demoted the day it is written.
