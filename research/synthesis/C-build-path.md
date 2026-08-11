# C — THE DEVELOPMENT PATH AND THE DELIVERABLE

**Authoritative build specification, section C. Compiled 10 Aug 2026.**
This section supersedes RND-BRIEF §9 (the experiment queue), ARCHITECTURE Part 5 (what to build), and
every dated plan that preceded it. Where it contradicts the brief, the contradiction is deliberate and
the lane that forced it is cited inline.

**Warrant key, used on every quantity in this document:**

| Mark | Meaning |
|---|---|
| **M** | MEASURED first-hand on the real artifact by a lane, with a re-runnable script |
| **V** | VERIFIED at primary source (paper PDF, spec file, regulator page opened and read) |
| **D** | DERIVED arithmetic; the inputs are stated and the result is never stronger than its weakest input |
| **S** | SECONDARY — a credible source describes it, nobody in this corpus opened the primary |
| **MOD** | MODELED — an assumption with the arithmetic shown |
| **REF** | REFUTED — recorded here only so that it is never said again |
| **NF** | NOT-FOUND — looked for, could not confirm; a legitimate answer |

**Two standing rules that govern everything below.** (1) A derived number never claims a stronger
warrant than its weakest input. (2) Before reporting an absence, run a positive control and declare the
denominator. Both earned their place: this corpus violated each of them, and the violations are now
part of the product's evidence base rather than being hidden.

---

## 0. WHAT THE LANES CHANGED, IN ONE PAGE, BEFORE ANY PLAN

Seven findings reorganise the whole development path. Everything in sections 1–7 is downstream of one
of them.

| # | Finding | Lane | Consequence for the plan |
|---|---|---|---|
| 1 | **The two-day build is already built.** L1→L5 runs end-to-end on the real published FME workbook in **~30 ms**, deriving **280 executable predicates** from the template's own structure with **zero model calls**; **515** across the nine prescribed workbooks. **M** | L14 §1.9–1.10 | The hackathon is an *assembly*, not a build. Both days go to the honesty machinery, not the parser. |
| 2 | **`3 of 10` is statistically incapable of settling anything.** At the true rate the reference class predicts, it deletes a working L3 26% of the time and keeps a broken one 18% of the time; the 95% Wilson interval at p̂ = 0.30, n = 10 is **[0.108, 0.603]**. **D** | L03 §11.4 | The settling experiment is re-specified (§1). The criterion changes *before* the run, on an argument that the old criterion was wrong — never after seeing a result. |
| 3 | **FFR measured on a corpus the predicate authors also wrote has expected value zero regardless of predicate quality.** It is not weak evidence; it carries none. **D, structural** | L13 Attack 4 | L4 has two working tests until a blind-fill firewall exists. `SELF-AUTHORED` FFR renders as the word *uninformative*, never as a number (§5.2). |
| 4 | **Coverage-as-a-fraction is Goodhart-broken.** The brief's 17/24 = 71% became **555/562 = 98.8%** in one afternoon under a different enumeration of the same file, without writing a single interesting check. **M** | L13 Attack 1 | The headline becomes two counts that cannot be traded against each other, plus the residue set. The fraction is subordinate and always carries its denominator's provenance. |
| 5 | **The system's own failure mode recurred four more times during this research**, three of them in deterministic programs, one of them in `openpyxl` — the ecosystem default — which reports the regulator's **anti-money-laundering sheet as having zero data validations when it has five**. **M** | L14 §1.6, L13 Part 1, L11 §9.2, L05 §0 | A new layer exists: **L6.5 self-check**, and a third verdict state, `INVALID`. This is now the strongest pitch asset in the corpus and it is not our code. |
| 6 | **L6 as specified is unbuildable and its five relations are wrong.** Metamorphic testing requires a re-executable system under test; a filed workbook is a record. The string `NAV` does not occur in any of the nine workbooks, in any XML part. Four of the five relations false-alarm on a correct filing; the fifth is vacuous. **M, V** | L13 §10.1, L06 §0, §8 | L6 is rescoped to differential and invariant probing over the workbook-as-program, renamed, and routed *through* L4. It moves ≈0 of the 7 undecidables and the plan says so. |
| 7 | **Two of the design's biggest claimed absences are refuted, and the replacements are stronger.** "Zero financial regulations encoded anywhere" is false (**≈14,819 distinct** executable EU supervisory rules, **V**), and "no analogue exists for a financial assertion" is false (ISA 705 ¶24; ISRS 4400 ¶30(j); XCCDF's nine per-item states). **V** | L04 §0, L10 §6 | The novelty claim relocates — and lands somewhere a domain expert cannot break in one click (§5.5). |

---

## 1. THE SETTLING EXPERIMENT

### 1.1 The decision

> **DECISION 1.1 — The pre-registered threshold is NOT "3 of 10". It is: 20 obligations in the
> arithmetically-closed stratum, retain L3 as a candidate generator if and only if ≥ 6 survive a
> five-gate admission test AND the surviving set beats the union of three free baselines on marginal
> kill at equal false-failure rate. Delete L3 for that stratum if ≤ 2 survive. 3–5 triggers exactly
> one pre-committed extension to n = 40 with a threshold of ≥ 12, and no further extension ever.**
>
> **Alternative it beat:** the brief's `n = 10, delete below 3`.
> **Reason:** the old criterion cannot distinguish the hypotheses it was written to distinguish.

The arithmetic, exact binomial, computed by L03 (**D**):

| True survival rate p | P(delete L3) at n=10, threshold 3 | P(delete L3) at n=20, threshold 6 |
|---:|---:|---:|
| 0.10 | 0.930 | — |
| 0.15 | 0.820 | **0.933** |
| 0.20 | 0.678 | 0.804 |
| 0.25 | 0.526 | — |
| 0.30 | 0.383 | 0.416 |
| 0.35 | **0.262** | **0.245** |
| 0.50 | 0.055 | — |

Two failures in the old design, both large. If L3 genuinely works at p = 0.35 — inside the central band
of the reference class — the brief's design deletes it **26% of the time**. If L3 is broken at p = 0.15
— the band the two closest published analogues sit in — the brief's design keeps it **18% of the time**.
The 95% Wilson interval at p̂ = 0.30 is **[0.108, 0.603]** at n = 10 and **[0.145, 0.519]** at n = 20
(**D**). Neither is tight. The n = 20 interval is what goes on the slide; the point estimate never does.

**This change is legitimate and here is the test it passes.** The brief's own Part 11 says the criterion
may change only by an argument that the old criterion was wrong, never by the discovery that it cannot
be met. The argument here is entirely *ex ante*: it is built from published rates in four adjacent
literatures (§1.2), it was made before a single model call, and it moves the threshold in the direction
that makes L3 **harder** to keep at low p (0.933 vs 0.820 deletion probability at p = 0.15), not easier.
A criterion revision that increases the chance of killing your favourite layer is not a rescue.

### 1.2 The reference class, built honestly

"Per-unit success rate" where the unit is the thing you get *n* of, and success is the closest available
analogue of "survives an L4-shaped gate". All rows **V** unless marked, from L03 §11.1.

| Study | Unit | n | Gate | Rate |
|---|---|---:|---|---:|
| nl2postcond RQ1 | EvalPlus problem (docstring + reference impl) | 164 | ≥1 test-set-correct postcondition @10 | 96% |
| nl2postcond RQ1 | EvalPlus problem | 164 | union of correct postconditions is bug-complete | 62.2% |
| ClassInvGen | C++ class, code available | 9 | ≥1 invariant kills a mutant the tests missed | 8/9 = 89% **D** |
| SpecGen | program + verifier | 385 | verifiable spec produced | 72.5% **S** |
| AutoSpec | C program + Frama-C | 51 | solved | 60.8% **S** |
| **AssertLLM2 bug-prevention** | **design, spec document only** | **83** | mutation bug-kill ratio, union of 3 runs, best model | **18.5%** |
| AssertLLM2 | design | 83 | bug-kill, single run, best model | 11.7% |
| **nl2postcond RQ2** | **real bug, JavaDoc prose + real code** | **525** | ≥1 bug-discriminating postcondition, union all models | **12.2%** |
| TOGA, realistic protocol | mutant | 51,385 | **marginal** kill over the free baseline | **0.3%** |
| NormBench | statutory provision | 2,290 | Edge-F1 — correctly wiring which clause overrides which | **0.215–0.246** |

**The single most instructive number in the whole corpus is TOGA's.** A neural test-oracle generator
reported **96% accuracy on a held-out set** at ICSE 2022, and was subsequently measured by two
independent replication groups at **0.38% precision** and **+0.3% marginal mutation kill** — 105 unique
kills out of 51,385 mutants — while a degenerate baseline that generates *no assertion at all* found
68.9% of TOGA's bugs at twice its precision (**V**, L03 §4.2–4.3). That is RND-BRIEF §4.4 — clean,
confident, well-formed output that was wrong — happening to a published state of the art, twice, with
the field not noticing for eighteen months. It is why the gate is the product and the generator is not.

**Four adjustments locate our task inside that class** (L03 §11.2):

*Pushing our rate up.* (i) L1 removes the hardest sub-problem: TOGA's dominant failure is `assertEquals`
at **74% false positives** — guessing an expected *value*. Our predicates assert relations among named
cells on a schema induced deterministically from the blank template, which places us in nl2postcond's
**Arithmetic Equality** category (bug-completeness 0.82) rather than its **Type Check** category (0.14) —
and Type Check is the model's *modal* output at 47.4% prevalence (**V**). (ii) The faults are ours, seeded
into an artifact we control. (iii) Sampling k = 10 is free and every result in the class improves 2–4×
from @1 to union.

*Pushing our rate down.* (iv) **NormBench, and it is the biggest term.** Frontier models ground the right
statutory spans (SpanFaith 0.77–0.79) and wire the exception structure wrong (**Edge-F1 ≈ 0.22**). Our
instrument is full of defeaters: reg 39(1) carries a half-yearly proviso for close-ended restricted
schemes; regs 26(2)/38(2)/50(2) carry a fund-of-funds proviso; reg 51(1) ends *"in such manner as
specified by the Authority"* — an open delegation (**V**, RND-BRIEF §6.3). A predicate that implements
reg 39(1) *without* its proviso will pass a mutation test and pass FFR on a clean corpus containing no
close-ended restricted scheme, and be wrong in production. That is why gate G0 exists (§1.4).

**Decomposed estimate** (L03 §11.3, all **MOD** with anchors named):

```
P(survives) = P(admits an executable check at all)  0.50–0.65
            × P(model writes one that fires | admissible)  0.65–0.85
            × P(non-degenerate | fires)  0.60–0.80
            × P(FFR acceptable | non-degenerate)  0.70–0.90
            = 0.14–0.40, central ≈ 0.25–0.30
```

### 1.3 The ten obligations — and why there are thirty

> **DECISION 1.3 — The sample is drawn by a stated rule, stratified by a human before any model runs,
> and the draw is continued until Stratum A holds 20 obligations. The number of draws required is
> itself the experiment's first result.**
>
> **Alternative it beat:** hand-picking 10 obligations from the 17 already classified decidable in
> RND-BRIEF §4.3.
> **Reason:** §4.3's 17/24 = 71% is a *curated* list, chosen by someone already looking for checkable
> things. Sampling from it would measure the curation, not the model. L03 §14 names this as the real
> first afternoon, and it is folded in here rather than run as a separate experiment.

**Sampling rule, fixed before the draw.** Source instrument: *IFSCA (Fund Management) Regulations 2025
as amended to 30 January 2026*, 102 pp, published 07/05/2026 (**V**). Enumerate every occurrence of
`shall` in the chapters governing scheme operation, valuation, and periodic reporting. Order them by
(regulation number, sub-clause). Seed a PRNG with a value written into the pre-registration file. Draw
without replacement. For each drawn clause, a human — not a model — assigns a stratum using this test
and records the assignment before generation:

- **Stratum A — arithmetically closed.** The obligation names quantities, dates, counts, identifiers, or
  relations among fields present in the FME template's L1-induced schema.
- **Stratum B — judgment-bearing or externally dependent.** Adequacy, appropriateness, truthfulness,
  satisfaction, or data about entities the FME does not manage.

Draw until **|A| = 20**. Stop Stratum B at the first **10**. Record `|drawn|`, and report
`|A| / |drawn|` as the **measured decidable fraction of the instrument** — a number nobody has, and the
honest replacement for the curated 71%.

**Ten worked examples, to make the frame concrete.** These are the shape of Stratum A, drawn from the
predicate families the artifact and the regulation already support (**M** for the cell references,
**V** for the clause references):

| # | Obligation, in the instrument's own terms | Fields it touches |
|---|---|---|
| A-1 | NAV computation frequency owed under regs 27(1)/39(1)/51(1), with 39(1)'s half-yearly proviso | `'1. Introduction'!G54:G63` (scheme type), `H54:H63` (open/close-ended), `'3. Portfolio'!E178:E187` (date of latest valuation), `F178:F187` (previous) |
| A-2 | Independent valuer required unless the fund-of-funds proviso to regs 26(2)/38(2)/50(2) applies | `K54:K63` (FoF flag), `L75:L84` (valuer), `M75:M84` (valuer registration) |
| A-3 | Scheme authorisation date must not post-date the reporting period end | `'1. Introduction'!D2`, `D3`, per-scheme authorisation dates |
| A-4 | FME registration date must not post-date any scheme authorisation date | Intro registration block vs Table 1.5 |
| A-5 | Declared scheme count equals the number of authorised schemes reported | `D17`, `D18:D20`, `G54:G63` |
| A-6 | Every declared scheme type is a permitted type | `G54:G63` against `Dropdown!$F$3:$F$11` |
| A-7 | Principal Officer and Compliance Officer must be different persons | Intro KMP block |
| A-8 | Funds raised must reconcile across the partitions in which they are reported | `'4. Investors'!AA`, `AB`, Tables 4.2 and 4.3, `'2. Summary'!K`/`Q`/`H` |
| A-9 | The filing must be made on the template version currently published | template `sha256` vs the published manifest |
| A-10 | Every percentage composition disclosed must sum to 100 | Portfolio composition blocks |

Stratum B's expected members are the seven the corpus already knows are undecidable — portfolio
composition accuracy, valuation appropriateness (Third Schedule Part A(g), p.90 — **not** Fifth
Schedule, which is the Advertisement Code and has no Parts, **REF**), reg 119(3)(e) rationale adequacy,
AML-CFT truthfulness, complaint resolution satisfaction, "infrastructure" classification, look-through
data about other managers' schemes.

### 1.4 The protocol

**Target language.** Predicates are **CEL** (Common Expression Language) in a mandatory three-slot
envelope `applicable` / `expr` / `witness`, evaluated by a Python host over a flat typed fact table
derived by L1 (L09 Part 0, **decision**). Chosen over plain Python because CEL terminates by language
design, is safe to evaluate without a container, is a *string* — therefore content-addressable,
diffable, and mechanically mutable — and, decisively, because **field references are statically
extractable, which is the only reason the coverage number is a derived quantity rather than an
assertion.** Four of the seventeen decidable predicates need capabilities CEL lacks (live register
lookup, GSTIN check digit, template-hash comparison, regulation-date arithmetic); these become named,
individually versioned, individually mutation-tested **host functions**. No predicate ever contains
model-generated Python.

*Open risk, stated:* whether a model writes CEL as well as it writes Python is unmeasured (L09 Part F).
**Decision:** CEL is the pre-registered primary arm; a Python arm runs alongside as a *secondary,
exploratory* measurement, reported separately, and it may never be used to change the CEL decision.

**Generation.** For each obligation, **k = 10** candidates per prompt regime, in **two regimes**:

- **`base`** — the strong, complex regime, given the full clause text with its provisos, the L1-induced
  schema for the fields the clause plausibly touches, and the template's own native formulas over those
  fields as I/O constraints.
- **`simple`** — the minimal regime, clause text and field list only.

Two regimes, not one, because nl2postcond measured that the prompt maximising *correctness* is not the
prompt maximising *completeness* (p = 0.008, Cohen's d = 1.73; the simple regime reaches accept@1 = 0.77
but only 26.2% of problems get a bug-complete postcondition, while the base regime reaches 61.6%
bug-complete at accept@1 = 0.63) (**V**). **A single prompt sits on one horn by construction.**

Feeding L1's induced schema in as an explicit I/O constraint is not a stylistic choice: it is the single
measured intervention that most improves this exact task in the only paper that has measured it —
**+37 to +54 percentage points** of functional equivalence when generating executable decision models
from Dutch statute (arXiv:2604.17153, **V** via L04's adversarial pass).

Model: `claude-opus-5` via the Batch API with a cached schema prefix (§3.3 for the cost). Log **every**
candidate. The discard pile is data; the attrition funnel is the most reusable artefact the experiment
produces.

**The five gates. An obligation survives iff at least one of its 20 candidates passes all five.**

| Gate | Test | Why it exists |
|---|---|---|
| **G0 — scope faithfulness** | The candidate carries the exact character span of the clause it claims to implement, `source.find(quote)` succeeds deterministically, and every proviso, exception and cross-reference inside that span is either implemented by a branch **or** emitted as `UNCHECKED(scope: <proviso text>)`. Neither ⇒ reject. | NormBench: models ground spans right (0.77–0.79) and wire overrides wrong (**Edge-F1 ≈ 0.22**). Gates 1–4 cannot see a silently dropped proviso. This is a structural check on a pair, not a semantic one — it is cheap, and it converts the most dangerous silent failure into a coverage line. **New; not in the brief.** |
| **G1 — executes and binds** | Runs on the corpus without error; every key it reads exists in the L1-induced schema; **`cells_bound > 0`**. Binding to zero cells is `ERROR`, never `PASS`. | TOGA's lesson: only **563 of 29,000+** bad assertions were type-incorrect or non-compiling — the errors are semantic and survive a compile gate (**V**). This gate is nearly free and proves nothing on its own; it is here to make that explicit. |
| **G2 — kills** | `K/O > 0` on **observable** seeded defects (§1.5), **and** marginal kill strictly greater than `B0 ∪ B1 ∪ B2`. | Two of the three demolitions in this literature are demolitions by baseline. |
| **G3 — non-degenerate** | Not equivalent to a member of the published degeneracy list (type / null / existence checks — nl2postcond Table 3); flags ≤ 50% of the clean corpus; spurious firing on the 10% control sample below threshold; and `degenerate_floor` margin > 0. | SPADE's own paper: taking every candidate the model writes yields **100% coverage and 100% FFR** (**V**). And the peer-reviewed exhibit: CLAUSE's best F1 across an 80-cell table is **65.4** on a ~49.5%-positive split where a constant always-flag classifier scores **66.2**, with a full-text positive control confirming **zero** occurrences of "majority baseline", "constant classifier", "random baseline", "trivial baseline" or "degenerate" in the camera-ready (**V**, **D** for the 66.2). |
| **G4 — false-failure rate** | `FFR ≤ τ = 0.10` computed **for the set, not the predicate**, using SPADE's bound `max(FFR(S), FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S) + FFR(f)`; reported as a Wilson interval with `n`; **and `corpus_provenance ≠ SELF-AUTHORED`**. | 44.4% of raw LLM candidates individually blow a 25% FFR budget, and in two of SPADE's nine pipelines assertions that each individually met the budget composed to **88% and 53%** total FFR (**V**, **D**). A registry that admits one at a time drifts silently to flag-everything. |

**On G4 and the corpus problem.** L13's Attack 4 is correct and it constrains this experiment: a clean
corpus written by the same people who wrote the predicates measures nothing. For 9.1, G4 is computed on
corpora in this priority order, and the provenance travels with every number:

1. **`TEMPLATE-COMPUTED`** — fill the input cells, let the workbook's own 505 formula-bearing cells
   compute the derived ones. Any predicate that fires on a cell **IFSCA's own artifact computed** is a
   genuine false failure, because the ground truth was authored by the regulator (**M**: all 505 carry
   cached values). Covers the arithmetic families.
2. **`REAL-REGISTER`** — for identity predicates, the clean corpus is the regulator's live register, and
   it needs no synthesis at all. **228 of 228 live FMEs carry a non-empty `RegistrationNumber`** via the
   detail endpoint (**M**, coverage 99.6% of 229). This is a *real, non-synthetic* FFR and the
   synthetic-corpus caveat does not apply to it.
3. **`BLIND-FILLED`** — Person A fills workbooks from the template and regulation only, having never
   seen the predicate set; Person B authors predicates having never seen A's workbooks. Minimum bar
   below which no FFR may be printed anywhere in the product.
4. **`SELF-AUTHORED`** — renders as `—` and the word **uninformative**. Not a number. The report schema
   forbids it.

### 1.5 The fault set

> **DECISION 1.5 — L4 test 1 is renamed and re-specified. It is not mutation testing and the tools the
> brief names are a category error.**
>
> **Alternative it beat:** `mutmut` / PIT / Stryker with `MS = |killed| / (|mutants| − |equivalent|)`.
> **Reason:** those three mutate *source code* and ask whether *your tests* fail. L4 mutates *data* and
> asks whether *the predicate set* fails. The subject, the mutant and the denominator are all different.
> The correct name is **seeded-defect adequacy**; the right citation is **Abraham & Erwig, "Mutation
> Operators for Spreadsheets", IEEE TSE 35(1):94–108, 2009** (**V**), whose 17 operators are, verbatim,
> a fault taxonomy for exactly this artifact class — including **FRC, "Formula Replacement with
> Constant"**, which is literally the brief's "formula overwritten by a constant".

**The fourteen fault classes** (L09 §C.3; F1–F11 map onto Abraham & Erwig operators and the
Panko–Halverson mechanical/logic/omission taxonomy; F12–F14 were added by measurement on this artifact):

| # | Fault | Generator | Observable iff |
|---|---|---|---|
| F1 | Digit transposition | swap adjacent digits; reject if value unchanged | the cell feeds a total or a cross-sheet carry |
| F2 | Sign flip | negate a numeric cell | a downstream identity or a `≥ 0` validation exists |
| F3 | Off-by-one row shift | shift a row's values within its table | the row is keyed, so key/value binding breaks |
| F4 | Unit confusion | ×1e5 / 1e7 / 1e6 / 1e-6 on a declared-unit column | a cross-table relation in another unit exists |
| F5 | Stale carry-forward | replace a period-end value with the prior period's | a prior filing exists, or an open/close identity does |
| F6 | Duplicated row | copy a table row into a free row | a count, total, or cross-table identity |
| F7 | Dropped row | blank a populated row | same |
| F8 | Date off-by-period | shift a date ±1 quarter / ±1 year | a date-ordering predicate exists |
| F9 | Currency mislabel | change a currency label without rescaling | a magnitude or declared-unit predicate exists |
| F10 | Rounding drift | perturb components by ±0.005 so a 2dp total stops reconciling | **this is the fault that calibrates the tolerance** |
| F11 | Formula overwritten by a constant | replace a formula with its value, **then perturb an input it depended on** | the perturbation would have moved the formula's value |
| F12 | Vocabulary drift | write a scheme type outside `Dropdown!$F$3:$F$11`, or edit the Dropdown sheet | only if the predicate resolves the vocabulary from the **pinned blank template** |
| F13 | Carry desynchronisation | change a destination of one of the 195 cross-sheet carries without its source | always, if the carry family is admitted |
| F14 | Vocabulary-gap exploitation | declare every scheme `Special Situation Fund` | **only if the predicate does NOT reproduce the template's own COUNTIF** |

**F11 must be generated as a pair.** Overwriting `=SUM(C3:N3)` with its current value changes nothing
observable; it becomes observable only when a component is subsequently perturbed and the frozen total
fails to move. A harness that generates F11 as a single edit reports a spuriously low kill rate.

**F14 is the taxonomy's payoff and it is a live defect in a regulatory return currently in use.**
`'1. Introduction'!D17`, labelled *"Total No. of Schemes of the FME authorised by IFSCA"*, is
`SUM(D18:D20)` where `D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")`,
`D19 = COUNTIF(G54:G63,"*Restricted*")`, `D20 = COUNTIF(G54:G63,"*Retail*") +
COUNTIF(G54:G63,"*Exchange Traded Fund*")`. The `x14` list validation on `G54:G63` permits **nine**
values, of which **`Special Situation Fund` and `Family Investment Fund` match none of the five
patterns.** A filing declaring either reports a total that is silently short by one per such scheme, the
value is legal under the template's own validation, and no cell in the workbook flags it (**M**,
CONFIRMED by an adversarial re-derivation from raw OOXML). **A rule set mined from the template is blind
by construction to a fault class the template creates** — which is precisely why L4 is load-bearing
rather than decorative.

*Exposure is UNMEASURED.* How many of the 360 authorised schemes are of these two types requires the
IFSCA scheme register broken down by type, which this corpus does not have. **Do not claim an exposure
figure.** The defect is real whether the exposure is 0 or 60.

**Scoring — three numbers, never one** (L09 §C.5):

```
G  = mutants generated
U  = mutants whose recalculated value grid is identical to clean   (UNOBSERVABLE)
O  = G − U                                                          (OBSERVABLE)
R  = observable mutants touching no field any admitted predicate reads
K  = observable mutants for which at least one predicate returned FAIL

KILL RATE            KR  = K / O          <- the headline; NEVER K/G
REACHABLE KILL RATE  RKR = K / (O − R)    <- adequacy of the rules we actually have
UNOBSERVABLE RATE    UR  = U / G          <- a property of the OPERATOR MIX, always reported
```

**The observability filter is the step the brief does not have, and it is what makes the number mean
anything.** Abraham & Erwig measured **3,512 of 7,500 (46.8%)** of comparable spreadsheet mutants as
*irreversible* — they evaluate to the same value as the original and cannot produce any observable
failure (**V**). A kill rate over *generated* mutants understates every predicate by roughly half,
variably by operator mix. Our substitution — `K/O`, where observability is *measured by recalculation* —
is available only because our mutants are data: "observable" is a diff, whereas "equivalent" is a
theorem. That is the single largest practical improvement available to L4 and it removes an undecidable
term from the denominator.

**The control arm.** Seed **only** into fields the predicate reads and a flag-everything predicate scores
a perfect kill rate. Therefore: seed a **10% control sample into fields the predicate does not read** and
count spurious firings. This is G3 done empirically alongside the static check.

**Suppression is logged or it is a coverage lie.** Google took unproductive mutants from **85% to 11%**
via feedback-derived suppression heuristics over 2 million reported mutants (**V**) — the structure
transfers even though the numbers do not. Any operator/target combination we stop generating is recorded
with its reason in the harness manifest.

**A caveat that ships with every kill rate we ever quote.** In code mutation testing the bridge from
seeded faults to real faults is the *coupling effect*. **There is no coupling study for financial filing
data** (L13 Attack 2; L09 open Q). So `KR = 0.82` licenses exactly one sentence: *"rejects 82% of the N
defects I seeded, under fault model v3, of which U were discarded as unobservable."* It does **not**
license *"detects 82% of real filing errors."* That bridge does not exist and must not be walked across.

### 1.6 The three mandatory baselines, each run **before** the model

| ID | Baseline | What it is |
|---|---|---|
| **B0** | **The native formulas** | The template's own checkable relations: **35 SUM identities + 3 COUNTIF tallies = 38 of 294 authored expressions**, which per *evaluated cell* is **138 of 505 = 27.3%** (**M**; both are true statements about different quantities and the plan states which). Free, deterministic, zero model. |
| **B1** | **Daikon** | Dynamic likely-invariant detection over the clean corpus flattened to one row per filing via `scripts/convertcsv.pl`, `--conf_limit 0.99`. MIT-equivalent licence, 260★, last push 2026-08-08, ships a CSV front end (**V**). Expected to recover the SUM identities, the cross-sheet carries as `a == b`, one-of sets, and date orderings — for free, with no model. |
| **B2** | **The degenerate arm** | TOGA's `NoException` analogue: *"no cell is blank and no cell errors."* |

> **If the model's admitted set does not beat `B0 ∪ B1 ∪ B2` on marginal kill at equal FFR, L3 has
> produced nothing, however many obligations "survive".**

Daikon must be run first — it is a one-hour experiment with a definite answer and it *sets the bar 9.1
has to clear*. Expect it to also emit trivia: in ClassInvGen's measurement, **27 of 40** correct Daikon
invariants were merely "pointer is not null" and **7 spurious invariants survived unit-test validation**
(**V**). Both facts are useful — the trivia populates the degeneracy list, and the spurious ones are a
measured demonstration *on our own corpus* that a check whose error rate is unknown must not be admitted.

### 1.7 What gets written down before the run

A file `experiments/9.1/PREREGISTRATION.md`, committed, content-addressed, and its `sha256` published in
the repo README **before the first API call**. It contains, and nothing may be added after:

1. The sampling rule, the PRNG seed, and the enumeration of `shall` clauses it draws from.
2. The stratum assignment for all 30 obligations, made by a named human, dated, before generation.
3. `|drawn|` and the resulting decidable fraction.
4. The two prompts, verbatim, and their `sha256`.
5. Model identifier, API date, `k`, temperature, and the Batch job id.
6. `τ = 0.10`; the fault model version and its operator list; the code hashes of B0, B1, B2.
7. The five gates, in the exact form above.
8. The decision rule and its power table.
9. The corpus provenance of every FFR that will be computed.
10. **The list of arguments that will not be accepted as grounds for changing the criterion**, written
    out in full:
    - *"We should have sampled better obligations"* — the sampling rule is pre-registered.
    - *"The clean corpus was synthetic"* — known in advance, and it applies symmetrically to the baselines.
    - *"Stratum B was always going to fail"* — that is why it is a separate stratum with its own
      pre-registered expectation of 0–1 of 10.
    - *"The language was wrong"* — the Python arm is exploratory and cannot change the CEL decision.
11. A commitment to publish, whichever way it goes: the Wilson interval, the per-stratum split, the
    accept@k curve, the five-gate attrition funnel, the marginal kill over each baseline **separately**,
    the unobservable rate `U/G`, and the `τ` actually used.

**And the framing that makes the experiment unfailable in the only sense that matters.** The deliverable
of 9.1 is not "L3 works". It is a number: *of N model-proposed regulatory checks, k survived a five-gate
admission test specified before the model ran.* **k = 0 is a result** — it would be the first measurement
anyone has of whether a frontier model can write a regulator-grade executable check, and the search
establishing that the space is empty is in this corpus with its positive control (L03 §1: across the
arXiv abstract index on 10 Aug 2026, **zero** papers report a false-failure rate or a mutation kill rate
for an executable predicate synthesised from regulatory text; the control query returns the known-present
paper). The experiment cannot fail. It can only return a small k.

---

## 2. THE EXPERIMENT QUEUE, RE-ORDERED BY WHAT ACTUALLY DECIDES THE DESIGN

The brief's queue was ordered by what was interesting. This one is ordered by **blast radius per rupee**:
an experiment ranks higher if a negative result deletes more of the plan. Two consequences are
uncomfortable and both are deliberate — the settling experiment drops from first to sixth, and a
twenty-minute email is joint-first.

| # | Experiment | Cost | Pre-registered threshold | What it kills if it fails |
|---:|---|---|---|---|
| **E1** | **Demand-side settling: one email to IFSCA's Division of Investment Funds — are these checks already run on receipt? And are any filed FME returns obtainable?** | 20 min + wait | *If IFSCA already runs arithmetic validation on receipt*, the entity-facing product is a convenience, not a gap. | The **product**, not the research. Promoted from 6th to joint-first because it is the only experiment that can tell you the thing is over, and the standing bias is to run engineering first. The NEC SupTech award (27 Jan 2026, ₹39,57,36,115.52, scope **includes an RE-facing portal**, **V**) makes it urgent. |
| **E2** | **Decidability pilot: draw and stratify `shall` clauses until Stratum A = 20** (folded into §1.3) | ½ day, no model | Report `|A|/|drawn|`. No kill threshold — this **is** the denominator 9.1 needs. | Nothing. It prevents 9.1 from measuring a curation instead of a model. |
| **E3** | **Formula-override detection, end-to-end** — diff the filed workbook against the pinned blank template; any cell carrying a formula in the template and a literal in the filing is an overwritten formula | 1 day | Must detect a seeded F11 pair on the real artifact and fire on zero template-computed clean filings. | Nothing — but its success is load-bearing: **it needs no corpus at all**, its oracle is the published blank template, and it is the classic route by which a wrong number is made to look computed. It should be predicate #1. |
| **E4** | **Cross-format transfer over the nine prescribed workbooks already on disk** | 2 days | **Pre-register: if the human cost per transferred predicate is not materially below the cost of authoring one from scratch, the method does not generalise.** | The claim that this is a **product** rather than a paper about one workbook. R7.6: exactly one thing has to be true for this to matter beyond one regulator — schema induction plus predicate qualification must transfer at bounded human cost. |
| **E5** | **Daikon + native-formula baseline (B0 ∪ B1)** | 1 hour | No threshold; the output *is* the bar 9.1 must clear. | Runs before E6 or E6 is uninterpretable. |
| **E6** | **The settling experiment (§1)** | 1–2 weeks human, **≈$20 model** | ≥6 of 20 in Stratum A **and** beats B0∪B1∪B2 | **L3.** Architecture survives without it, smaller: predicates are hand-authored from the 294 native expressions, the 22 vocabularies and the statute. Nothing else changes. |
| **E7** | **The residue set on the FME workbook** — generate mutants, adjudicate INNOCUOUS/WRONG, run the entire admitted set, report what survives | 1 week | No threshold; **|RESIDUE| ≠ 0 is expected and is the finding.** | Nothing — it is the publishable result. It repairs Attacks 1, 2, 4 and 9 at once because it cannot be inflated by adding boring checks, it runs on the artifact under test, and a third party can re-run it. |
| **E8** | **Blind-fill corpus (the brief's 9.2, rewritten)** — ≥30 correctly-filled workbooks by a person who has never seen the predicate set | 2–3 weeks human | Any predicate whose only FFR is `SELF-AUTHORED` cannot be admitted. | **Every FFR the product displays**, and with it the UX differentiator. Without the firewall this experiment measures nothing at all. |
| **E9** | **Differential and invariant relations, rescoped (the brief's 9.3)** — 25 candidate relations, of which **15 need nothing but the filing** | 2 weeks | Each relation passes L4 like any other predicate; publish the before/after settled-count delta and **the relations that moved nothing, as moving nothing**. | The growth story on Screen 4. Note the honest ceiling: this moves **≈0 of the 7** undecidables. It adds high-value boring checks and the plan says so. |
| **E10** | **L2 feasibility gate** — measure μ, the key-binding base error rate on cross-document binding, then apply the forced-abstention floor `r ≥ (μ−α)/(1−α)` | ½ day, on paper | **μ > 0.30 ⇒ do not build the conformal layer**; at α = 0.05 the floor already exceeds 26.3%. | **L2's conformal machinery.** Already largely settled: **0 of 3,755** unlocked cells are ambiguous under the address key and **154 of 3,755 (4.10%)** under a header-anchored key (**M**), so key-binding on the native workbook is a *lookup against L1*, not a prediction. |
| **E11** | **Characterise the LibreOffice normalisation defect** — `soffice --convert-to xlsx` migrates 19 `x14` validations into the main namespace and expands 294 → 505 formulas in 3.9 s, but writes **53** main-namespace validations where 35 + 19 = 54 | 2 hours | The missing validation must be identified before normalisation ships in L0. | The normalisation step itself — which is otherwise the cheapest fix in the stack. **A one-validation silent loss in the tool we adopt to fix a silent loss is exactly the failure this product exists to prevent.** |
| **E12** | The brief's 9.4 — the three-paper checker contradiction | 1 week | — | **Demoted to optional.** L02 dissolved most of it: all three agree deterministic structure helps the *primary* task; the disagreement is confined to a *secondary* detection metric, and FinBalance's mechanism is named — ledger feedback pushes models to *reconcile* contradictory documents rather than report them. That yields a real architectural constraint instead: **L5 must never repair; it must only adjudicate and report.** |
| **E13** | The brief's 9.5 — open every unopened arXiv identifier | — | — | **Substantially discharged** by L01 and L02. Residue is listed in §6. |
| **E14** | The brief's 9.7 — QuantMind on a protected xlsx | — | — | **Moot for the build.** L0/L1 is ~200 lines of `lxml` measured at 28 ms. Do not adopt a 2.3k-star dependency to save 200 lines. Protection is not an obstacle (it is advisory; every reader tested reads straight through it); merged headers are recovered identically by three independent readers (252 ranges, three-way agreement). **The real obstacle was neither — it was the extension namespace.** |

---

## 3. THE DATED BUILD PLAN

### 3.1 By 16 August 2026 — the application and the one link

**The link is a public GitHub repository whose README is the pitch.**

> **DECISION 3.1** — one URL, a public repo, MIT or Apache-2.0.
> **Alternatives it beat, each on its merits:**
> - **Demo video** — best on presentation quality alone, worst on feasibility and team capability. A
>   judge cannot distinguish a real pipeline from a screen recording of a mock, and *that distinction is
>   the entire subject of this project.* Losing it in the artifact would be self-refuting. Put a
>   60-second capture **inside** the README instead; it costs no URL.
> - **Deck** — every applicant sends a deck; it is the weakest possible evidence of capability and
>   cannot show that a number was computed rather than authored.
> - **Figma** — signals a design exercise. The differentiator is measurement, not layout.
> - **Website** — another deploy target, another thing to be down at 09:00 on the 16th, and it reveals
>   less than the repo.
> - **MVP behind a login** — judges will not create accounts.
>
> A repo discharges four of the five judging criteria simultaneously (§7), and GitHub renders README.md
> as a formatted page: a deck that happens to be executable.

**Day by day.**

| Date | Work | Done means |
|---|---|---|
| **Mon 11 Aug** | **(a)** Open `giftifih.getkruu.com/apply` in a real browser and confirm the form is live and its fields match the recorded spec — WebFetch returned **HTTP 404** and the root served only an SPA shell, which does **not** establish that applications have closed but does mean nobody in this corpus has seen the live form. **(b)** Repo skeleton, licence, CI. **(c)** L0 ingest: fetch the nine workbooks, content-address by `sha256`, write the manifest. **(d)** Retire `an.py` — the script that still reports `xsheet=0` on all ten sheets sits beside the corrected one with nothing marking which is authoritative. | Form confirmed live with a screenshot; `ingest.py` run twice produces byte-identical manifests; every `sha256` matches the recorded value; the broken script is deleted, not patched around. |
| **Tue 12 Aug** | L1 schema induction, `lxml` only, **all** sheets including hidden, `extLst`/`x14` parsed, shared formulas materialised, keys label-anchored `(sheet, header_path, row_label)` with coordinates as a resolved attribute. Predicate harvest. | A test asserts the constants **505 formula cells, 54 validations, 22 list-type, 20 resolving to a real vocabulary, 3,747 field-surface cells, 280 predicates (FME), 515 (all nine)** against the checked-in workbook hash. A regression is loud, not silent. |
| **Wed 13 Aug** | L5 execution with the state axis (`PASS / FAIL / INDETERMINATE / NOT_RUN / NO_PREDICATE / OUT_OF_SCOPE / INFORMATIONAL`), `cells_bound` per predicate, coverage against the **unlocked-cell field surface** from `styles.xml`, self-contained HTML report. | Clean filing → 0 FAIL; single seeded fault → exactly the predicates reading that cell FAIL; a unit test asserts the denominator is derived from the unlocked mask and **not** from the predicate set; the report opens from `file://` with networking off. |
| **Thu 14 Aug** | Seeded-defect harness with the observability filter and the control arm; L4 test 2 rejecting near-vacuous bounds; register snapshot + the name-match predicate. | `KR = K/O` printed with both integers and `U/G`; **ALR's five `-1e17` bounds are rejected** and its coverage recomputes downward; **FME's 19 `≥ 0` bounds are admitted**; the register predicate ships with its **measured 38.2% (87 of 228) regex false-failure rate** as the worked example of why the FFR column exists. |
| **Fri 15 Aug** | README as pitch; `make demo`; `verify`; 60-second asciinema capture; write the ~1,100 words. | `make demo` reproduces every number in the README on a clean clone; `grep` for banned all-clear glyphs and phrases fails the build. |
| **Sat 16 Aug** | Submit in the morning. Freeze and tag. | Repo tagged `v0.1-application` with its commit sha in the application text. |

**The README, in order** (this ordering is the argument, not decoration):

1. One sentence: *A regulated filing checker that reports what it did **not** check.*
2. **The four silent failures, in a table, leading with the one that is not our code:**

   | # | Instance | Effect |
   |---|---|---|
   | 1 | **`openpyxl` 3.1.5 — the ecosystem default** — sees **35 of 54** data validations and reports the **AML-CFT sheet as having zero** when it has **five** | A compliance tool built on it reports full validation coverage of the anti-money-laundering section while checking none of it |
   | 2 | Operator's addressee parser: reported 64.5% coverage; true 79.9% | Nearly published *"35.5% of circulars don't say who they bind"* |
   | 3 | Operator's formula regex `<f[ >][^>]*>`, which cannot match `<f>SUM(...)</f>` | Reported **zero** cross-sheet formulas in every workbook; true: **195 of 294** in the FME workbook alone |
   | 4 | Our own L4 harness, v1 | Printed a mutation score of **100.1%** — arithmetically impossible — cleanly and confidently, from two independent defects, one of which was the degenerate-baseline failure committed by the harness built to detect it |

   All four are deterministic programs. All four produced clean, confident, well-formed wrong output.
   **This is no longer an anecdote; it is a pattern with a sample size and a taxonomy.**
3. The measured result, as a fenced block of real program output: 280 predicates, **63.3% of 3,747
   fields settled, 1,374 declared unchecked**, ~30 ms, zero model calls.
4. A screenshot of the report showing the two-count hero and the Unchecked panel. **No green tick
   anywhere.**
5. `make demo` — clone, run, reproduce, against the workbook as published on `ifsca.gov.in`.
6. **What is not built yet**, named plainly — the do-not-build list in §4. A do-not-build list in a
   README is itself evidence of the discipline being pitched.
7. The 60-second capture.

**Application field spec** (~1,100 words total, caps enforced by the portal):

| Field | Cap | What must be in it |
|---|---|---|
| Solution Title | — | Names the *boundary*, not the AI. |
| Elevator Pitch | 150 w | The verdict is the product; finding the error is the automated half; nobody ships the residue or the per-rule error rate. One number: 63.3% of 3,747, 1,374 unchecked, computed in 30 ms with no model. |
| Problem Statement | 250 w | Must cover all four prompts: *what problem / who experiences it / why it matters / how it is currently addressed.* Lead with the AML-CFT blind spot — it is checkable by the judge in ninety seconds and it is not our code. Then the workbook's own scheme-count total that is silently wrong for two of its own nine legal values. |
| Proposed Solution | 250 w | Solution, **uniqueness**, tech enablers, expected impact. Uniqueness = the three claims in §5.5 and no more. |
| Current Stage | — | **Prototype** |
| Have you built anything? | — | **Prototype** |
| Demo / Deck URL | — | The repo. |
| Focus Area | — | **Theme 1 → Fraud, Risk & Compliance** (alternative: *Autonomous Banking*, which matches the agentic framing better but has less workflow density). |
| Why Fintech / GIFT City? | 200 w | The India asymmetry, evidenced: EBA publishes **12,925** rule-instances (**8,052 distinct**) quarterly; EIOPA **6,767**; ESMA ships a per-rule `Automatable Yes/No` column; **RBI's validation-rules trail dead-ends at a 3,254-byte login shell** (**V**). There is no rule corpus to inherit in this jurisdiction — which is exactly why a *generator plus a gate* is the right thing to build here and the wrong thing to build in Frankfurt. |
| Future Potential | 250 w | The dated residency plan in §3.3, with M1 named as an experiment that is allowed to fail. |

**Claims permitted in the application, and no others.** Every one is measured or verified and every one
carries its denominator: the 63.3%/3,747/1,374 triple; 280 and 515 predicates; ~30 ms; 505 formula
cells; 54 validations of which 22 list-type and 20 resolving; `openpyxl`'s 35-of-54 and the AML-CFT
zero-of-five; the `Special Situation Fund` / `Family Investment Fund` COUNTIF gap; the 38.2%-of-228
register regex FFR; 217 FMEs and 360 schemes **as at the Q4 FY2025-26 bulletin date**; ~868 filings/year
**labelled MODELED (217 × 4)**.

### 3.2 21–22 August 2026 — the two-day build, with a hard cut line

**Scope thesis:** the surfaces and the honesty machinery, not the parser. Everything above the cut line
is the demo; everything below is optional and must be abandoned without hesitation if the line is
reached. Dependency-ordered; every task has an acceptance test that can fail.

**Day 1 — the pipeline and the artifact**

| # | Task | Depends on | Acceptance test |
|---|---|---|---|
| T1 | **L0 ingest**, content-addressed, with **dual-parser differential ingest**: two independent implementations; disagreement on sheet count, cell count, formula-cell count, validation count, defined names or hidden sheets **fails the run, loudly** | — | Feed it a file where the two parsers disagree and assert the run aborts. *This lane is the proof it works: three implementations gave 244 / 294 / 505 on the same file, and two of them were already sitting in the same directory undetected.* |
| T2 | **L1 schema induction** (§3.1 Tue) + an **extraction manifest**: parts read, parts skipped, namespaces encountered, constructs not understood | T1 | The asserted constants; and where the readers disagree, the affected fields are `NOT_RUN(source_unreadable)` **by construction**, never silently absent |
| T3 | **Predicate harvest** — nine classes, 280 / 515 | T2 | Every predicate serialises to JSON and round-trips; vocabularies resolve from the **pinned blank template**, never from the artifact under test |
| T4 | **L5 execution** with the 7-state axis, the 19-code namespaced reason vocabulary, `cells_bound`, and weakest-input provenance | T3 | Clean → 0 FAIL; seeded fault → exactly the reading predicates FAIL; `cells_bound == 0` ⇒ `NOT_RUN(predicate_error)`, never `PASS` |
| T5 | **Coverage against the field surface**, computed **twice by independent code paths** | T2, T4 | Prints `63.3% of 3,747`; the two computations must agree or the run is `INVALID`; a test asserts the denominator's provenance |
| T6 | **Run manifest + content addressing** — `{template_sha, filing_sha, predicate_set_root, code_git_sha, python_version, tool_versions, register_snapshot_sha}` | T4 | `verify` re-derives the report from the manifest and byte-matches |
| T7 | **Self-contained HTML report** — one file, inline CSS/JS, no external requests | T4, T5, T6 | Opens from `file://` with networking off; renders on a phone; the CI grep for `✓ ✔ ✅ 🟢 "all clear" "no issues" "looks good" "verified clean" "compliant" "passed all" "fully checked"` fails the build |

**Day 2 — the honesty machinery**

| # | Task | Depends on | Acceptance test |
|---|---|---|---|
| T8 | **Seeded-defect harness** with the observability filter, the 10% control arm, per-fault-class kill vector, `K/O` + `U/G` | T4 | Reproduces on the real artifact; a test asserts the site set is the **field surface** and **not** the predicate graph |
| T9 | **L4 test 2 gate** — degenerate-floor rejection; every admitted predicate carries `mutation_score`, `ffr`, `ffr_corpus_n`, `ffr_corpus_kind`, `admitted_at` | T8 | ALR's five `-1e17` bounds rejected; FME's 19 `≥ 0` bounds admitted; **attempting to admit a predicate with an unknown error rate raises, and the test asserts the rejection** |
| T10 | **L6.5 self-check — run-time seeded canaries.** For every admitted predicate, instantiate its stored kill-witness against **this** filing and re-run. Any predicate that fails to fire on a fault it is known to detect ⇒ verdict state **`INVALID`** | T8, T9 | Break the parser deliberately (rename a sheet) and assert the run returns `INVALID` with the dead predicates named — **not** a clean report |
| — | **====== HARD CUT LINE — the demo is complete above this ======** | | |
| T11 | Drop screen — one control | T7 | Works from a phone browser on venue wifi |
| T12 | Predicate library screen — clause, code, kill vector, FFR + interval + corpus kind, admission date, **and the five-gate attrition funnel per obligation** | T9 | 280 rows in <200 ms, no virtualisation library |
| T13 | Settled-count-over-time — replay admission in order, **able to step down** | T9 | Renders from a static JSON log; a synthetic template-version bump makes the line fall |
| T14 | L7 attestation stub — scope-only schema, no `result` field anywhere | T6 | Tampering with one cell changes the report sha and `verify` fails |
| T15 | Three differential relations (formula-override, cross-format agreement, four-way funds-raised partition) | T4, T9 | Each holds on the clean filing and is violated by a targeted mutant, **and each passes L4 first** |

**Cut-line discipline.** T1–T10 is the whole demo: the pipeline runs, the report renders, the coverage is
computed twice, the gate visibly rejects bad predicates, and the system proves it was alive. If Day 2
morning is lost to a venue problem, ship T1–T10 and present from the HTML file and the terminal.

**The relations (T15) are deliberately below the line.** Two days is not enough to author metamorphic
relations honestly — four of the brief's five false-alarm on a correct filing and the fifth is vacuous —
and doing it badly would poison the most publishable component.

**Explicitly not in the two days:** any model call, any database, any auth, any deploy pipeline, any
queue, any framework.

### 3.3 1 September – 30 October 2026 — the residency

Eight and a half weeks. Five funded milestones plus a pre-residency week, each with a **measurable
acceptance test that can fail**. Milestone 1 is the settling experiment, because the brief's Part 11 is
explicit that the standing bias is to elaborate rather than to find out whether the thing is over.

**M0 — pre-residency (23–31 Aug), unfunded.**
- Send the E1 email (demand-side settling), including an explicit ask for any obtainable filed returns,
  even unlabelled, and a question about whether the register's null descriptive fields are a privacy
  posture or a defect.
- Run E2 (decidability pilot) and E4 (cross-format transfer over the nine workbooks).
- Write and commit `experiments/9.1/PREREGISTRATION.md`; publish its `sha256` in the README.
- **Acceptance:** the pre-registration hash is public **before 1 September** and no model has been called
  against the 9.1 prompts. If the hash is late, the experiment is downgraded to exploratory and says so.

**M1 — Weeks 1–2 (1–14 Sep): run the settling experiment and let it decide L3.**
- Run E5 (baselines) then E6 (§1). Publish raw model outputs, scores, and the decision on the date it
  was taken, whichever way it goes.
- Also inside M1: the open-weight comparison, run as *admitted predicates per rupee* and *admitted per
  100 candidates* on the identical prompt set — converting an unanswerable question ("which model is
  best?") into a measurable one. **L4 adjudicates every candidate deterministically, so L3 model choice
  cannot affect correctness, only yield.**
- **Acceptance:** `experiments/9.1/` contains inputs, every candidate including the discards, the
  five-gate attrition funnel, the Wilson interval, the per-stratum split, the marginal kill over each
  baseline separately, the unobservable rate, and a dated `DECISION.md`.
- **Failure is a valid, funded outcome.** Say this to the mentors in week 1 so the result cannot be
  renegotiated in week 6.

**M2 — Weeks 2–4 (8–28 Sep): the corpus, and its declared weakness.**
- Blind-fill firewall (E8): ≥30 correctly-filled FME workbooks by a person who has never seen the
  predicate set, with an auditable, predicate-free fill prompt if a second model instance is used as
  Person A.
- Build the three corpus-free oracles: template-computed, real-register, cross-format.
- Publish a **per-template** coverage table. This will be embarrassing for `EDR_1` (zero formulas) and
  `IFSCA_Annual_Reporting_Format` (zero formulas *and* zero validations, so mechanically derivable
  coverage 0%). Publish it anyway. **Coverage is a per-template property and must never be averaged.**
- **Acceptance:** a unit test fails the build if any FFR is rendered without its corpus provenance and
  `n`, and a second test asserts that `corpus_provenance == SELF-AUTHORED` renders the string
  `uninformative` rather than a number. *Discipline that is not mechanised does not survive week 6.*

**M3 — Weeks 4–6 (22 Sep – 12 Oct): L4 as a product.**
- Harden the admission gate: all five tests, the SPADE ILP with the FFR sub-additivity bound and the
  subsumption DAG (**reimplemented, ~40 lines of PuLP/CBC — the SPADE repo is 17★, 1 fork, no licence
  field, last push 2024-04-07, which under GitHub's terms means all rights reserved**).
- Qualification records: `qualified_against{template_sha, regulation_version, circular_corpus_snapshot,
  circulars_unreadable, corpus_id, corpus_provenance, n}`, plus the model id, date and prompt hash used
  to synthesise each predicate — so a re-synthesis under a drifted model is a diff, not a mystery.
- The `PROVISIONAL` state and the instrument-stream watcher (daily content-hash of IFSCA's circular and
  Authority-meeting pages).
- **Acceptance (three tests):** (a) a predicate with an unknown error rate cannot be admitted; (b)
  bumping the template hash moves affected predicates to `PROVISIONAL`, hides their numbers, and
  **coverage falls**; (c) a predicate whose stored kill-case stops dying is quarantined automatically.

**M4 — Weeks 6–8 (6–24 Oct): the residue set and the relations.**
- E7 (residue set) — the publishable component.
- E9 (differential and invariant relations, rescoped) — including the four-way funds-raised partition,
  which is the single highest-value relation in the design and is not in the brief: the FME workbook
  reports funds raised by investor category, by country, by accreditation status, and via the Summary
  carry, and **enforces agreement between none of them** — Tables 4.2 and 4.3 contain zero formulas
  (**M**).
- **Acceptance:** publish the before/after settled-count delta with the relation that moved each item; a
  relation that moves nothing is reported as moving nothing; and the residue set's size, fault-model
  version, and at least one **demonstrated survivor** rendered in the Unchecked panel.

**M5 — Weeks 8–8.5 (20–30 Oct): attestation, reproduction, demo-day artifact.**
- L7 with the scope-only schema (no `result` or `status` field exists to write a pass into), DSSE +
  in-toto statement, **detached key signing rather than Sigstore keyless** — a keyless signature puts
  the fact that a named FME ran a pre-submission check into a permanent public transparency log.
- **Acceptance:** a third party clones the repo, runs `verify <report.html>`, and gets a byte-identical
  re-derivation on a different machine. **If it does not reproduce, it does not ship.**

**Milestone-to-funding mapping** (₹1,00,000 in five objectively checkable tranches, so no tranche can be
argued): M1 = experiment run and decision recorded · M2 = corpus published with mechanised provenance
strings · M3 = gate provably rejects unmeasured predicates and coverage provably falls on version churn
· M4 = before/after delta and residue set published · M5 = third-party reproduction succeeds.

**Model cost across the whole residency** (**MOD**, arithmetic shown, token counts are estimates and the
Opus-5-family tokenizer produces ~30% more tokens for the same text, so re-baseline with `count_tokens`
before quoting): L3 runs **once per template version**, not per filing — ~$0.0218 per candidate with a
cached schema prefix and the Batch API's 50% discount, ≈$0.55 per template version, **under $6 for the
entire nine-template prescribed-format corpus**. L2 is needed only for unstructured attachments; the
annual bill to process all ~868 modelled filings is **under $200** even routing every attachment through
Opus 5. **Marginal model cost per filing on the workbook path: $0.00.** Deployment: one container,
512 MB ≈ **$3.32/month** (**V**; note new accounts get no free allowance). *The expensive input is not
inference. It is the human-built blind-filled corpus, and no amount of model spend substitutes for it.*

---

## 4. THE DO-NOT-BUILD LIST

Ranked by how likely each is to be built anyway.

| # | Do not build | Reason |
|---|---|---|
| 1 | **An agent loop, cross-step memory, or retry-until-it-passes** | `pass^k` collapses ~60% → ~25% over 8 attempts on τ-retail (n=115); `0.9⁸ = 0.4305`. Two short stateless calls, both adjudicated by programs. *If a demo needs an agent to be impressive, the demo is wrong.* |
| 2 | **A green tick, an "all clear", or a PASS summary badge** | The single design commitment. Mechanised as a build-time grep, **and** at the schema level: the attestation has no `result` or `status` field, so there is nowhere for a downstream consumer to read one. Schema-level prohibition survives the screenshot, the API integration and the intern; copy discipline does not. |
| 3 | **A coverage percentage as the hero number** | 71% → 98.8% in one afternoon under a different enumeration of the same file. Two counts, equal weight, same ink, side by side. And **100% must be structurally unreachable** — the denominator includes the known-uncheckable and the residue count, which is never zero. |
| 4 | **A coverage denominator derived from the predicate set** | This mistake was made twice in one afternoon by the person hunting for it. The honest denominator is the unlocked-cell field surface from `styles.xml`. Assert its provenance in a test. |
| 5 | **`openpyxl` anywhere in the L1 path — ever** | Sees 35 of 54 validations, blanks the AML-CFT sheet, and its round-trip destroys the file: **3,663,391 → 65,877 bytes**, 24 parts deleted including a 3.55 MB data model that is 96.9% of the workbook (**M**). Convenience reads and mutant writing only; never schema derivation, never re-serialisation. |
| 6 | **`mutmut` / PIT / Stryker for L4 test 1** | Wrong tool class. They mutate code; L4 mutates data. ~200 lines of our own, measured at 7,946 mutants/second. (They *are* the right tools one level up, for mutating our host functions and our schema inducer — which is where the silent failures live.) |
| 7 | **An LLM as judge anywhere in the verdict path** | LLM judges detect false success at AUROC ≤ 0.65 with 13% recall at a 10% flag rate. A model may never be the final adjudicator. |
| 8 | **A NAV recomputation engine, or NAV-per-unit in any data model** | The string `NAV` does not occur in any of the nine workbooks, in any XML part (**M**, with positive controls). There is no NAV per unit, no units outstanding, no dealing price and no dealing date. Every NAV-error rule on earth operates on exactly those quantities. **You cannot build a NAV-error checker for an artefact that does not contain a NAV.** |
| 9 | **A NAV-error materiality regime as the pitch** | It is a policy proposal and you cannot ship a policy. Ireland — second-largest fund domicile — still has none as of S.I. 316 of 2026 (**V**). The set of jurisdictions with a prescribed regime is roughly {Luxembourg, UK} and they disagree with each other. "IFSCA lacks this" is the majority position, not a scandal. *Keep exactly one NAV-shaped predicate: valuation staleness against regs 27(1)/39(1)/51(1).* |
| 10 | **The brief's five metamorphic relations** | Four false-alarm on a correct filing as written; the fifth (currency round-trip) is vacuous because guidance C110 mandates per-transaction historical rates. And metamorphic testing needs a re-executable system under test; a filed workbook is a record. Delete them; build differential probes over the workbook-as-program instead. |
| 11 | **A queue, Redis, Celery, or a worker pool** | The job is ~30 ms. The whole 19,782-mutant campaign is 2.5 s. Offline batches go to the Batch API plus a Makefile. |
| 12 | **Postgres, an ORM, migrations** | Single writer, dataset well under 10 MB. **SQLite is a file, so it can be hashed and named in the run manifest** — which is exactly what L7 needs. A Postgres cluster cannot be content-addressed. |
| 13 | **React, Next.js, shadcn/ui, any component library** | It becomes the project. The deliverable is a *file*: it survives the venue, renders on a phone, is emailable, and is the only form of the report that can be hashed and signed. A single-page app cannot be content-addressed. That is an architectural argument, not a preference. |
| 14 | **Auth, multi-tenancy, user accounts** before 30 October | Judges will not sign up. |
| 15 | **Rebuilding Great Expectations / pandera / Soda Core / dbt / Deequ** | They are the check-library substrate. But note two things: **none of them has a third verdict value** (Great Expectations actively converts *could-not-check* into *failed*), and **Soda Core is Elastic License 2.0** and cannot be embedded in a hosted product at all. *The check library need not be rebuilt; the verdict model must be, because it does not exist anywhere in the ecosystem.* |
| 16 | **A rules-as-code framework** (Catala, OpenFisca, Blawx) | 16★, no commit since 5 Jun 2024, and the field's own diagnosis is that they *"require manual predicate engineering and detach from source"*. But **do not repeat "zero financial regulations encoded anywhere"** — that is refuted (item 4 of §5.5's corrections). |
| 17 | **An FFR without its corpus provenance, `n`, and interval** | Enforced by a failing test, not by remembering. `0 fires / 340 self-authored` and `0 fires / 4 real` must not look alike: the Wilson intervals are `[0.000, 0.011]` and `[0.000, 0.490]`. |
| 18 | **Sigstore keyless for filer-side attestations** | Signing identity lands in a permanent public transparency log; the *fact* that a named FME ran a pre-submission check becomes world-readable and correlatable. Detached key signing; a private log only if the supervisor operates it. |
| 19 | **Any predicate whose validity depends on a range being protected, or on a vocabulary read from the filed artifact** | `sheetProtection` is an application-level flag with a SHA-512 hash, not encryption — every byte is readable and a filer can strip it with a zip edit. The `Dropdown` sheet holding 15 controlled vocabularies is **hidden and the only unprotected sheet**. Pin vocabularies from the blank template's content hash. |
| 20 | **The ESEF conformance suite as a free L4 benchmark** | The summary file is a 68-row index whose test-case cells contain free-text English descriptions — no valid/invalid flag and no expected-error-code column. It **names** 212 test cases living in an archive nobody in this corpus has opened. Candidate corpus, not a benchmark, until someone opens it. |
| 21 | **Anything that repairs the artifact** | FinBalance's mechanism: deterministic ledger feedback pushed models to *reconcile* contradictory documents rather than report them, costing 13–52pp on inconsistency detection while gaining 30–33pp on the primary task. **L5 must never repair. It adjudicates and reports.** |

---

## 5. WHAT THE FINAL PROTOTYPE DELIVERS

### 5.1 The demo script — four minutes, wifi off, laptop only

The deployed URL is for the judges who read the application. **The demo runs from disk.**

| # | On screen | What the operator says |
|---|---|---|
| 0 | Terminal. `python -c "import openpyxl; ..."` against the regulator's published workbook, printing `AML-CFT: 0 data validations`. Then the raw OOXML parse printing `AML-CFT: 5`. | *"This is the standard Python spreadsheet library, reading the regulator's own published reporting format. It says the anti-money-laundering sheet has no validation rules. It has five. No error, no warning — a clean, confident, well-formed wrong answer. That is the problem. It is not that machines can't find errors. It is that when they find nothing, you learn nothing."* |
| 1 | Drop screen: one control. Drag `Reporting_Format_for_Fund_Management_Entities_02012026_…xlsx` — the file as published on `ifsca.gov.in`, `sha256 7d9a1960085785ee…`, filled, with one deliberately corrupted cell. | *"This is the real prescribed quarterly return for a GIFT City fund manager. Two hundred and seventeen of them file it. I have filled it and broken exactly one cell."* |
| 2 | Report renders in under a second. Hero is **two counts, same size, same ink, no colour on either**: `2,373 fields settled across 280 checks` · `1,374 fields were not checked`. Below, a hatched stacked band. **No percentage in the hero, no ring, no green anywhere.** | *"There is no green tick in this product and there never will be. A surface that can say 'all clear' will eventually say it wrongly, and nothing in the output would tell you which time."* |
| 3 | Expand the single FAIL. It shows both cells — the corrupted one and the one it disagrees with — the clause the check implements, the check's kill vector by fault class, and its false-failure rate with its Wilson interval **and the words** *"measured on 34 blind-filled workbooks; not a measurement of real filings."* | *"Every check here carries how often it cries wolf, measured, with the corpus it was measured on and how big that corpus was. No compliance product tells you that. Neither does any auditing standard."* |
| 4 | Open the **Unchecked panel**. 1,374 fields, grouped by reason from a closed 19-code vocabulary. Point at `no_predicate.undecidable_by_construction` — *is the disclosed valuation appropriate (Third Schedule Part A(g), p.90)* — and read the "what would make it checkable" text: *"a materiality threshold by scheme class, of the kind CSSF Circular 24/856 Tables 1–3 specify, plus a compensation-direction rule of the kind its Tables 4–5 specify."* | *"This panel is the product. Not the failure — the panel. It says what could not be settled, why, and exactly what instrument would move each one across the line. One regulator in the world publishes, in advance, what it will and will not treat as a finding. We compute the equivalent per filing, for a jurisdiction that has neither."* |
| 5 | Open the **Predicate library**. 280 rows. Filter to the five ALR bounds the gate **rejected** for being satisfiable by any number at all — `-100000000000000000` over 1,428 cells. Show the five-gate attrition funnel for one obligation: candidates generated → executed → fired → non-degenerate → FFR-admitted. | *"A check whose error rate we could not measure is not in this list. That is why the coverage number means something. And here is what the gate threw away — including five rules the regulator's own template ships that assert only 'this is a number'."* |
| 6 | Run `demo --break-parser` (renames a sheet). The report comes back **`INVALID`**, naming the predicates that failed to fire on faults they are known to detect. | *"That is the third verdict state, and it is the one nobody else has. Every report carries proof that the checker was alive when it ran — on your document, not on a benchmark. When it cannot prove that, it refuses to give you a verdict at all."* |
| 7 | Terminal: `verify report.html` → byte-identical re-derivation. Then, in Excel, type `Special Situation Fund` into `'1. Introduction'!G54` and show `D17` — *"Total No. of Schemes authorised by IFSCA"* — failing to increment. | *"Two facts. Not one model was called in anything you just saw. And the regulator's own workbook computes its own scheme total with three COUNTIFs that between them miss two of the nine scheme types it permits. You can check that yourself in thirty seconds. That is the class of confident, well-formed, wrong answer this exists to make impossible to give."* |

### 5.2 The acceptance criteria that make the demo honest

Each is a **test in CI**, not a value. A design commitment that is not tested is a preference.

| # | Criterion | How it is enforced |
|---|---|---|
| A1 | No all-clear glyph or phrase reaches a user-facing surface | `ci/no-green-tick.sh` greps `src/ templates/ locales/` for `✓ ✔ ✅ 🟢 all clear / all-clear / no issues / looks good / verified clean / compliant / passed all / fully checked` and exits non-zero |
| A2 | The attestation cannot express a pass | JSON Schema: the top-level object is `scope`; there is no `result` or `status` property, and additional properties are rejected |
| A3 | The coverage denominator is not derived from the predicate set | Unit test asserts it comes from the `styles.xml` unlocked mask, and a second, independent code path recomputes it; disagreement ⇒ `INVALID` |
| A4 | No FFR renders without provenance and `n` | Test renders a predicate with `corpus_provenance = SELF-AUTHORED` and asserts the output contains `uninformative` and no digits |
| A5 | No predicate binding to zero cells returns PASS | Test asserts `cells_bound == 0` ⇒ `NOT_RUN(predicate_error)` and the run state ⇒ `INVALID` |
| A6 | Zero model calls in the verdict path | Test runs a filing with the network namespace closed and asserts success; asserts no socket to a model endpoint is opened |
| A7 | The report re-derives byte-identically on another machine | `verify` in CI on a second runner image |
| A8 | Coverage can fall | Test bumps the template hash and asserts affected predicates go `PROVISIONAL`, their numbers hide, and the settled count decreases |
| A9 | Every seeded-defect number is `K/O` with both integers plus `U/G` | Test asserts the renderer refuses a bare percentage |
| A10 | The demo runs offline | Report opens from `file://` with wifi off; the register response is read from its content-addressed snapshot, never live |

**And one sentence permanently on the report surface**, because it is the honest limit and it costs
nothing: *"This system detects error, not deception. Every check here is a consistency check over a
self-reported document. A coherent liar passes all of them."*

### 5.3 Every number on screen, and where it comes from

| Number on screen | Value | Warrant | Denominator / provenance |
|---|---|---|---|
| Fields settled | **2,373** | **M** | Union of 280 admitted predicates over the field surface |
| Fields not checked | **1,374** | **M** | `3,747 − 2,373` |
| Field surface | **3,747** | **M** | Unlocked, non-formula cells, from `styles.xml` `cellXfs → <protection locked="0"/>`; 105 unlocked style ids; 9 of 10 sheets protected |
| Settled fraction (subordinate) | **63.3%** | **D** | `2,373 / 3,747`; **per-template, never averaged across templates** |
| Checks in the active set | **280** (FME) · **515** (all nine workbooks) | **M** | Derived from the blank template's own OOXML: 181 cross-sheet equalities, 35 SUM identities, 20 membership, 13 numeric bounds, 11 integer bounds, 11 same-sheet equalities, 6 date bounds, 3 tallies |
| Formula-bearing cells | **505** (294 authored expressions, 211 shared-formula dependents) | **M** | Both figures true of different quantities; state which |
| Data validations | **54** (35 main-namespace + 19 `x14`), **22** list-type, **20** resolving to a real vocabulary | **M** | Replaces the brief's 35 / 3 — **REF** |
| Run time | **~30 ms** | **M** | L1 28–44 ms + synthesis 1 ms + L5 sub-ms, cold, single process |
| Seeded-defect campaign | **19,782 mutants, 2.5 s, 7,946/sec** | **M** | 2,826 sites × 7 numeric operators; **kill rate must be quoted as `K/O` with `U/G` alongside** |
| Register regex false-failure rate | **38.2% (87 of 228)** | **M** | 228 of 229 live FMEs, detail endpoint, 10 Aug 2026; the clean corpus here is the regulator's own register, so no synthetic caveat applies |
| Population | **217 FMEs, 360 schemes** as at the Q4 FY2025-26 bulletin; **650** Fund Management register rows and **229** live FMEs as at 10 Aug 2026 | **V / M** | **Never blend the two denominators in one sentence.** |
| Filings per year | **~868** | **MOD** | `217 × 4`, assuming every FME files every quarter including those registered mid-year. Label it. |
| Per-filing model cost | **$0.00** | **D** | The workbook path calls no model |

### 5.4 The sentence a judge should be able to repeat

> **"They built the compliance checker that tells you what it did *not* check — every rule carries its
> own measured error rate, and the report proves the checks were alive on *your* document."**

If only half a sentence survives the walk to the next table, the half that must survive is: **"it tells
you what it didn't check."**

### 5.5 The novelty ledger — plainly, with what would falsify each claim

**Do not hide the assembly.** Fifteen components of this design are prior art with named sources: SPADE
(LLM → executable assertions, FFR as a selection criterion, the ILP, the sub-additivity bound); Deequ
(non-LLM constraint suggestion); mutation testing as adequacy (Google, TSE 2021); Abraham & Erwig's 17
spreadsheet mutation operators; metamorphic relations derived from statute (arXiv:2205.04998, IRS
publications); PROVE (deterministic adjudication of LLM output for a regulatory submission, 30 Jul
2026); ExceLint's hypergeometric random-flagger baseline — **which is a published precedent for the
degenerate-baseline test the brief presents as new**; CycloneDX's `aggregateType`; XBRL Assertion
Severity 2.0 (REC, 21 Jul 2022); ISA 705 ¶24 and ISRS 4400 ¶30(j); XCCDF's nine per-item result states
(NIST, 2012); the EBA's quarterly deactivated-rules list; OSCAL's POA&M; in-toto/Sigstore; and Brown's
*Semantic Integrity Constraints*, which proposed **an observability interface displaying the precision
and recall of each constraint** a year before this brief did. *A judge who finds one of these after the
pitch discounts everything. A judge handed all fifteen upfront reads the team as competent.*

**Three claims survive, and they are enough.**

| # | The claim | What makes it novel | What would falsify it |
|---|---|---|---|
| **N1** | **Measurement is the admission condition.** A predicate with no measured seeded-defect kill rate, no degenerate-baseline margin, and no false-failure rate on a corpus whose provenance is not `SELF-AUTHORED` **cannot enter the active set.** | SPADE *selects* by FFR inside one pipeline's build and never keeps a registry. The assurance profession's most coverage-honest report form, ISRS 4400 ¶30(h), **expressly disclaims any representation about whether the procedures were the right ones** — which is precisely the question this gate answers with a number. The EBA, with ~20,500 expert-authored rules and a decade of EU-wide consultation, has deactivated **8.23%** of them at least once, **343 of the still-withdrawn ones being hard-blocking `error` severity** — and finds out from the field. **L4 is the proposition that you can find out before you ship.** | Any shipping product or published system that refuses to admit a rule until its own error rate is measured. Scope of the search: 21 vendor/product pages opened at primary URLs, ~20 named vendors **not** checked; the arXiv metadata index with a 186-result positive control; the LangChain documentation index (57 evaluation lines, `grep -ci spade` → 0, `grep -ci "false failure"` → 0). |
| **N2** | **Statutory text plus the template's own native formulas as the criterion source, with mutation supplying the labels.** | SPADE mines *prompt-version history* — an inferred record of what a developer noticed. SPADE's own paper states that coverage and FFR are *"impossible to compute since the universe of examples 𝐸 is unknown"*, and its tasks average **34 bad examples**. **Seeded defects manufacture the dirty half by construction, at any n, with certain ground truth.** That is not a re-skin; it is the input SPADE says it does not have. | Experiment E6 itself: if fewer than 6 of 20 arithmetically-closed obligations survive the gate, **this claim is dead and the plan says so in advance.** The architecture survives; predicates are hand-authored. |
| **N3** | **A computed, typed, per-field, signed residue.** `N in scope, M settled, K unchecked by reason` from a closed 19-code vocabulary, bound cryptographically to the template hash, the filing hash, and the predicate-set version — **plus the residue set: the falsehoods demonstrated to survive every check we have.** | ISA 705 ¶24 declares the boundary in prose, once per report, and **only on modification** — an unmodified opinion carries no statement of what was not checked, and PCAOB inspection found **20% of inspected Big Four audits in 2024** lacked sufficient appropriate evidence for the opinion issued. ESMA's `Automatable Yes/No` and CycloneDX's `aggregate` are **static properties of the rulebook**, declared by an author before anyone runs anything. Nobody computes it per filing, from a denominator induced from the regulator's own artifact, and signs it. | A financial reporting product that emits a machine-readable per-field residue. Also falsified in part if the residue set turns out to be empty on the FME workbook — which would mean the boundary this project exists to measure does not exist in this artifact. **That is a real risk and E7 is how we find out.** |

**And the sharpest form of the whole thing, in one line:** *everyone ships rules; nobody ships each
rule's error rate, and nobody ships the residue. We make both a product surface, and sign them.*

---

## 6. RISK REGISTER

**P** = probability over the period to 30 Oct 2026. **Blast radius** = what breaks. Rows marked
**RETIRED** were live risks in the brief and have been closed by a lane measurement.

| # | Risk | P | Blast radius | Early-warning signal | Mitigation | Status |
|---|---|---|---|---|---|---|
| R1 | **The application portal is not live, or the form differs from the recorded spec** | Low–Med | The entire programme; there is no second entry | WebFetch to `giftifih.getkruu.com/apply` returned **HTTP 404** and the root served only an SPA shell titled *"KYF Programme"* | **First task on 11 Aug**: open the form in a real browser, screenshot every field, submit a draft early. Do not rely on any cached spec. | **OPEN — highest urgency** |
| R2 | **L3 does not work** | Med (central p ≈ 0.25–0.30) | L3 only. Predicates become hand-authored; **the rest of the architecture is unaffected** | E6's five-gate attrition funnel collapsing at G2 or G3 | Pre-registered kill criterion written before the run (§1.7); k = 0 is a publishable result; B0∪B1 already yield 280 predicates with no model | Managed |
| R3 | **No labelled clean corpus of real filings exists** | High (near-certain) | Every FFR the product displays; the UX differentiator; L2's conformal guarantee | Already realised — filed FME returns are not public | Four-tier corpus hierarchy with provenance in the record (§1.4); blind-fill firewall; template-computed oracle; **the register, which is a real clean corpus for the identity class**; Wilson intervals so `n = 4` and `n = 340` cannot look alike | Managed, not solved |
| R4 | **Our own silent false negative ships** | High if unmitigated | Everything — the product would be committing the failure it sells against | Four instances already found in this corpus, three in deterministic programs; all four under-counted **in the direction that supports the thesis** | L6.5 run-time canaries (`INVALID` state) · dual-parser differential ingest that fails the run on disagreement · `cells_bound == 0 ⇒ ERROR` · denominator computed twice by independent code paths | Mitigated by design; T1/T10 are above the cut line |
| R5 | **Version churn silently invalidates a predicate** | High | Individual predicates return confident verdicts against rules that no longer exist | **Already realised**: the 29th IFSCA Authority Meeting, 24 Jul 2026, allows close-ended Restricted Schemes to move NAV computation from semi-annual to annual with 75% investor approval by value — a fact **the workbook does not collect** — and relaxes independent valuation for underlyings valued by an independent entity | Qualification records; `PROVISIONAL` state that keeps detection but hides numbers and drops out of the numerator; liveness witnesses; **daily content-hash watcher on the circular and Authority-meeting streams**; `reg 51(1)` ends *"in such manner as specified by the Authority"*, so watching the regulation is insufficient | **OPEN — M3 deliverable** |
| R6 | **The 10 unreadable circulars hide a NAV-error provision** | Low | Predicate A-1's correctness rests on a negative search result over **389 of 399** bodies | The gap is known and is 2.5% of the corpus | Carry `coverage_gap: 10/399 sources unread (scanned images)` on every predicate that depends on the §4.1 negative result — or OCR them, which is an afternoon | Declared |
| R7 | **The product has no buyer** | Med | The product, not the research | E1's answer; the NEC SupTech award (₹39.57 crore, 27 Jan 2026) explicitly scopes an **RE-facing portal** | E1 promoted to joint-first; **the supervisor user is deleted** (*"the supervisor is not the buyer; the supervisor is why the filer cares"*); the unit of value is named as the avoided deficiency and labelled **UNMEASURED**; and the IFSCA workbook is named for what it is — the **testbed**, not the market | Partially retired: the contradiction is removed; the demand question is open |
| R8 | **The method does not transfer beyond one workbook** | Med | The claim to be a product rather than a paper | E4's transfer cost per predicate; two of the nine templates have **zero formulas**, one has **zero validations too** | E4 pre-registered with a threshold, runnable today on nine workbooks already on disk; publish per-template coverage including the 0% cases | **OPEN — M0 deliverable** |
| R9 | **The residue set is empty** | Low | Claim N3's second half, and the publishable result | E7 returns no surviving WRONG mutants | A coordinated misstatement propagated through all 181 carries and all 135 SUM relations is **provably unkillable by any predicate over the artifact alone** — so the class is non-empty by construction; the open question is its size | Structurally mitigated |
| R10 | **A judge knows the prior art we claimed did not exist** | Was High | Credibility of everything else in the pitch | Two absence claims already refuted by lanes | Both corrected before the application: "zero financial regulations encoded anywhere" → **≈14,819 distinct EU supervisory rules**; "no analogue exists for a financial assertion" → ISA 705 ¶24, ISRS 4400 ¶30(j), XCCDF, C2PA, ESMA `Automatable`. Fifteen prior-art items are handed over upfront (§5.5) | **RETIRED by L04, L10, L12** |
| R11 | **"No measured system can say clean" is refuted on stage** | Was High | The problem statement's opening sentence | In the brief's own most-cited source, **Claude Sonnet 4 scored Acc/Prec/Rec/F1 = 100 at 0% FPR on n = 105 (43 clean, 62 error)** under the same prompt on the same instances, and 0% FPR at 79.0% recall on the harder rendering | Claim restated before submission: *a model can be calibrated on 43 clean statements; nine of fourteen frontier runs were not, on the same 43, and nothing in their output distinguished the calibrated run from the rest.* That is the FinVerBench author's own conclusion and it points at L4/L5/L7 rather than at a capability claim a judge can break by clicking one link | **RETIRED by L02** |
| R12 | **The evidence base is more concentrated than it looks** | Was High | Five separately-tabulated rows of the brief | Five rows and one architecture fact all trace to **one 37-page single-author unreviewed preprint with unreleased code, whose clean split is 43 instances** | Add a Warrant column naming the paper so a reader can see rows 1–5 are one instrument. Ten minutes, non-negotiable before submission | **RETIRED by L02, action pending** |
| R13 | **L2's conformal guarantee is void, not merely degraded** | Was High | L2's whole justification | Split conformal requires exchangeability between calibration and deployment; a team-authored calibration set against real filings is a known shift, and quoting a *theorem* under a violated assumption is a worse error than a loose FFR | L2 leaves the critical path entirely: **0 of 3,755** unlocked cells ambiguous under the address key. L2 is a contingency for unstructured attachments. Build the conformal **test martingale** — which detects that the guarantee has lapsed and withdraws the claim — before building the predictor | **RETIRED by L07/L08** (native xlsx needs no model) |
| R14 | **L6 is unbuildable as specified** | Was High | The layer the design leaned on hardest | No re-executable SUT; `NAV` absent from all nine workbooks | Rescoped to differential/invariant probing over the workbook-as-program (505 recomputable cells with cached baselines), renamed, routed through L4, and the honest claim stated: **it moves ≈0 of the 7** | **RETIRED by L06/L13** |
| R15 | **A licence trap ships inside the product** | Med | Distribution | `formulas` is EUPL 1.1+; `pycel` is GPL-3.0; CheckCell/DataDebug is GPL-2.0; Soda Core is Elastic 2.0; the SPADE repo has **no licence field** (all rights reserved); FINOS CDM is Community Specification License 1.0, *"not intended for source code"*; the DQC ruleset *"may not be modified in any way"*; FUSE is **CC BY 4.0**, not unencumbered | A licence gate in CI over the dependency tree before any hosted deployment; reimplement SPADE's ILP rather than importing it | **OPEN** |
| R16 | **The LibreOffice normalisation step loses data** | Med | The fix we adopt to prevent silent loss | Measured: `soffice` writes **53** main-namespace validations where 35 + 19 = 54 | E11 characterises it before it ships; until then, normalise **for analysis only** and content-address the artifact **as delivered** for signing | **OPEN — E11** |
| R17 | **Frontier-model drift moves a measured result under a fixed alias** | Med | Any quoted L3 yield | Documented: a failure cell moved from 96.6% to 100% on the same prompt and harness under the same model alias, with no version bump | L7 signs the model identifier, the date and the prompt hash used to synthesise each predicate, so re-synthesis is a diff rather than a mystery | Mitigated |
| R18 | **Who signs the attestation** is undecided | Med | Legal exposure. If an FME shows an inspector a signed attestation over a filing that was wrong, the signature is the first exhibit | Nobody has raised it yet | Decide before L7 is built. Interim: the scope-only schema (no `result` field) plus `assessor.thirdParty: false` — we are a self-assessment tool and saying so is required honesty | **OPEN — M5 gate** |
| R19 | **A stray demo dependency on the network** | Low | Demo day | Any external fetch in the report | A2/A10 tests; the report is a single self-contained file; the register is read from its content-addressed snapshot | Mitigated |
| R20 | **Team bandwidth: two days plus eight weeks, four people maximum** | Med | Scope | The cut line being crossed | The hard cut line (§3.2); the do-not-build list (§4); and the reallocation the lanes made possible — the parser is done, so the scarce resource goes to the honesty machinery | Managed |

---

## 7. THE TEAM-CAPABILITY AND FEASIBILITY STORY

Judging is on **problem relevance, innovation and creativity, solution feasibility, team capability, and
presentation and pitch quality**. The story is the same for all five, told from a different angle each
time, and every angle is inspectable.

**Problem relevance.** The problem was not chosen from a theme list; it was found by measurement, in the
jurisdiction the programme sits in. All 399 IFSCA circulars were downloaded (129 MB), extracted with
`pdftotext -layout` (7.3 MB), and grepped body by body — **389 of 399 readable**, positive controls
passed (`Aadhaar` → 3, `V-CIP` → 4, `FIPS 203` → exactly 1, the MII Cyber Guidelines). The prescribed
reporting workbook was parsed cell by cell. The public register was enumerated: 2,005 entities in one
request. Two defects were found in the regulator's own published artefacts, both reproducible by a judge
in under a minute: the scheme-count total that silently misses two of its own nine permitted scheme
types, and `'8. Compliance Status'!C11` — **a Yes/No box asserting compliance with the Sixth Schedule
valuation norms, which nothing in the other 6,756 cells can contradict.** *The prescribed return already
ships a green tick. We do not add a better tick; we remove it and print the boundary.*

**Innovation and creativity.** Stated as three claims, not a category (§5.5), each with what would
falsify it — and fifteen prior-art items handed over before anyone has to find them. The genuinely new
objects are: an admission gate where measurement is the condition of entry; seeded defects as the source
of labels for a corpus that cannot otherwise exist; and a computed, typed, signed residue with a third
verdict state, `INVALID`, that says *"this system could not demonstrate it was working here."* **The
innovation is not the LLM. The model's role is small, honest, and is itself the thing being measured.**

**Solution feasibility.** The strongest available answer is that it already runs. L1→L5 executes
end-to-end on the real published workbook in ~30 ms, deriving 280 predicates with zero model calls, and
`make demo` reproduces every number on a judge's laptop. The whole stack is Python + `lxml` + SQLite +
one container at ₹290/month; there is no queue, no ORM, no framework, and no model on the verdict path.
Marginal model cost per filing: **$0.00**. The one genuinely expensive input — a blind-filled clean
corpus — is named as such, scheduled as M2, and carries a mechanised caveat that fails the build if
anyone forgets it.

**Team capability.** The repository is the evidence, and it is the only item on the submission list that
is inspectable. What it shows is not that the team writes code — it shows that the team *finds its own
errors and keeps them in the record*. Four silent false negatives are documented in the README, two of
them the team's own, one of them committed by the very harness built to detect that class of failure.
Three separate independent verification passes over this corpus were run with instructions to refute
rather than agree; they overturned a threshold, killed a layer's specification, refuted two absence
claims and corrected a dozen numbers, and all of that is in the record too. **A team that publishes its
own attrition funnel is making a claim about its method that a polished deck cannot make.**

**Presentation and pitch quality.** The report is a single self-contained HTML file: it opens with the
wifi off, renders on a phone, can be emailed, and — uniquely among the options — can be hashed and
signed, which is what L7 requires. The demo runs from disk in four minutes with a scripted sequence that
starts with a bug in a library the audience uses and ends with a defect in a regulation the audience
files under. And the honest limit is on the screen the whole time, because the sentence that makes the
rest believable is: *this system detects error, not deception.*

**T&C readiness.** If selected, a legal entity must be incorporated — **or incorporation shown to have
been initiated** — within 60 days; the FAQ separately confirms no company is required to participate.
Plan for the "initiated" route and keep the evidence.

---

### Closing note on discipline

The brief's Part 11 names the standing bias: *you will pay any price to avoid believing something false,
and almost no price to find out whether the thing is over.* This section is written against it in three
concrete places, and they are the three places to check if the plan starts drifting.

1. **E1 — a twenty-minute email — is joint-first**, ahead of every engineering experiment, because it is
   the only one that can tell you the thing is over.
2. **The settling experiment's criterion was tightened, not loosened**, before the run, from published
   reference-class rates — and the list of arguments that will not be accepted as grounds for changing
   it again is written into the pre-registration file and hashed.
3. **k = 0 is a funded, publishable outcome**, and M1 ships the decision on the date it is taken
   whichever way it goes.

If in October the answer is "the model cannot write a regulator-grade check, and here is the measured
attrition funnel showing exactly where the twenty candidates per obligation died" — that is the first
such measurement anyone has, the architecture survives it smaller, and the coverage declaration, the
qualification gate and the residue set were never the parts that depended on it.
