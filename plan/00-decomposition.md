# 00 — PHASE DECOMPOSITION AND DEPENDENCY GRAPH
## The coverage-declaring filing checker · build plan, part 0 · compiled 11 August 2026

**This document is the skeleton.** It fixes the phase set, the phase IDs, the two orderings and their
reconciliation, the dependency graph, the critical path, the pre-registered gates with their failure
branches, and the one number each phase must produce. It does **not** contain per-phase detail: files,
signatures, test names and fixtures are written by the six detail documents named in §9, and every one of
them must use **these** phase IDs and **this** ordering.

**Dates are gone.** The hackathon constraint that shaped `spec/04-path.md` — 16 August application,
21–22 August build, September–October residency — no longer applies. Everything in that document that is
a *date* or a *hackathon-shaped sequence* is discarded here. Everything in it that is *content* — the
experiment queue, the do-not-build list, the acceptance criteria, the risk register, the twelve gaps, the
seven open questions — is carried forward, re-sequenced by dependency and by evidence.

---

## 0. THE RULE THAT GOVERNS EVERY PHASE IN THIS PLAN

The product exists because **a silent pass is not information.** A deterministic program that returns a
clean, confident, well-formed wrong answer is the failure this system refuses, and the research corpus
documents five real instances — three committed by this project's own team, one by the harness built to
detect the others.

A build plan whose validation is *"the test suite is green"* would therefore be self-refuting. Three rules
follow, and they are not decoration:

> **R1 — Every acceptance test ships with a named negative control.** A specific, on-disk, deliberately
> broken build or input that the test **must** reject. A test that has never been observed to fail is not
> evidence. Where a negative control is impossible, the phase says so explicitly and states what that
> costs.
>
> **R2 — The test suite is itself mutation-tested.** `mutmut 3.7.0` over `src/cdfc/` (our code, not the
> filings — mutating filings is gate G2 and is a different instrument). Every phase gate reports
> `killed / (mutants − timeouts)` for the modules that phase created, **with the equivalent-mutant caveat
> carried in the same sentence, never as a naive percentage.**
>
> **R3 — A phase that produces no number is not a phase.** Every phase below outputs at least one
> quantity that did not exist before, with its denominator and its warrant label
> (`MEASURED / DERIVED / MODELED / VERIFIED-AT-SOURCE / UNMEASURED`). Under this rule there is no
> "hardening phase", no "polish phase" and no "integration phase" in this plan; see §8.

**A fourth rule, specific to this project's history:** the four instrument-error classes that produced the
five documented silent false negatives — *namespace blindness*, *shared-formula invisibility*, *scope
truncation by hidden sheet*, and *shared numerator/denominator* — are each re-encoded as a permanent
negative-control fixture in `tests/fixtures/broken/`. The broken scripts are deleted; their **behaviour**
is preserved as tests that must fail.

---

## 1. THE STARTING STATE, STATED HONESTLY

**BUILT** (research scripts in `research/scripts/`, reproducing in ~30 ms, MEASURED):

| What | Where | Output on disk |
|---|---|---|
| Structural probe / partial L1 induction | `research/scripts/wb_probe.py` | `probe_out.json`, `probe_full.txt` |
| Predicate harvest, no model, 9 classes | `research/scripts/predicate_harvest.py` | `predicates.json` (280 FME / 515 across nine) |
| Arithmetic evaluation + fault seeding, first gate | `research/scripts/l4_mutation_harness.py` | `l4_result.json` (19,782 mutants, 2.5 s, 7,946/s) |
| The settled-fraction **denominator** | `research/scripts/true_coverage.py` | field surface 3,747 (FME) |
| The degenerate-bound rejection | inside the harness | five ALR `≥ −1e17` bounds refused over 1,428 cells |

**SPECIFIED AND NOT BUILT:** container guard · dual-reader agreement · template binding · predicate
selection · pre-flight key check · the eight-state / thirty-code verdict model · closure · the CEL
substrate · the five gates as a pipeline · the registry · the clean corpus · differential probes ·
run-time canaries · the residue set · attestation · `verify` · L1b · L3 · L2b · the watcher · every
surface.

**Two claims must never be restated without their real warrant, per the ban list:**
`"L1→L5 runs end-to-end"` is dead. `"zero model calls in the verdict path"` is a **design property with a
build gate specified and not yet written**; it becomes a system property on the day
`test_no_model_in_verdict_path` exists (P13-B0), and not before.

**Real artifacts the plan builds against:** nine IFSCA prescribed workbooks at
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx`; a Python environment at
`/Users/abishaikc/Gift/.venv/bin/python` with `openpyxl` and `lxml`; a git repository at
`/Users/abishaikc/Gift` with no commits.

**Package naming — DECIDED.** The package is `src/cdfc/` (coverage-declaring filing checker). *Alternative
it beat:* any name containing `check`, `valid`, `pass`, `clean` or `verify` — rejected because
`ci/no-green-tick.sh` greps identifiers as well as copy, and a package whose own name trips the honesty
gate forces the gate to carry an exception, and an exception in that gate is how the gate dies.

---

## 2. THE SIXTEEN PHASES

Each row: what it settles, and nothing else. Detail is in §5 and in the six documents of §9.

| ID | Phase | What it settles — the question no earlier phase can answer |
|---|---|---|
| **P0** | Repository, CI and the commitment gates | Whether this project's own honesty commitments can be **mechanised before there is code to violate them** — and what the two field observations say |
| **P1** | L0 — receipt, container guard, dual-reader ingest | Whether we can read the artifact at all without the class of silent under-count this project has committed five times |
| **P2** | L1 — schema induction, the field surface, stable keys | **The denominator every subsequent number is a fraction of**, computed twice, for all nine workbooks and not just one |
| **P3** | The two evaluation substrates — fact model and formula evaluator | Whether our recalculation reproduces the regulator's own cached values — the oracle on which every kill rate and the flagship check depend |
| **P4** | The predicate object, the CEL substrate, and the harvest | Whether the settled fraction is **derivable rather than estimated** — i.e. whether `schema_keys` machine-checks against the AST both ways |
| **P5** | L5 — run assembly, the verdict model, closure, the settled fraction | The product's core object: eight states, thirty reason codes, seven-term closure, and a runtime settled count that can fall below the static one |
| **P6** | The fault-seeding harness | Whether a kill rate over *our* operator mix means anything — the observability filter's own `U/G`, measured, not borrowed from the literature |
| **P7** | The five gates (minus G4), the registry, admission | Whether the rejector is real — the first five-gate attrition funnel over 280 harvested predicates on the FME workbook |
| **P8** | The clean corpus, G4, FFR, severity tiers | Whether **any** predicate in this system is admissible at all, and what the settled fraction is *after* the gate rather than before it |
| **P9** | L6 — differential and invariant probes | Whether the growth story is real, and whether the one check nothing else in the design can perform — formula-cell overwritten with a literal — works on the real artifact |
| **P10** | L6.5 — run-time canaries and the residue set | Whether a verdict can be conditioned on a proof obtained from the artifact under test in the same execution — and how large the provably-unkillable class is |
| **P11** | L7 — attestation, `verify`, byte identity | Whether a third party on another machine re-derives the report byte-for-byte. *If it does not reproduce, it does not ship* |
| **P12** | The settling experiment | How large the model's role is — `k of 20` obligations surviving a five-gate test specified before the model ran. **`k = 0` is a result** |
| **P13** | The model- and clause-bearing layers, sized by P12 | What L3, L1b, L2b and the instrument watcher look like at the size the experiment licenses — including the size zero |
| **P14** | The surfaces — report, screens, API, copy gates | Whether the no-green-tick commitment survives contact with a rendering surface, an API integration and an intern |
| **P15** | Transfer, version churn, operations, deployment | Whether this is a product or a paper about one workbook — the human cost per transferred predicate against a pre-registered threshold |

**Why sixteen and not twelve.** Four splits that look mergeable are load-bearing: P1/P2 (reading the file
and inducing the schema fail in *different* directions and need different negative controls); P3's two
substrates (the fact table is what predicates read; the evaluator is what decides observability — but both
are per-filing computations over the induced schema and both gate P6); P7/P8 (four gates need no corpus,
one needs the most expensive input in the programme); P12/P13 (the experiment must be able to delete the
layer it precedes, and a phase cannot gate itself).

---

## 3. THE TWO ORDERINGS, AND THE RECONCILIATION

### 3.1 The DEPENDENCY order — what cannot be built before what

```
P0 ─► P1 ─► P2 ─► P3 ─► P4 ─► P5 ─┬─► P6 ─► P7 ─┬─► P8 ─► P12 ─► P13
                                   │             ├─► P9
                                   ├─► P14·B1-B3 ├─► P10 ─► P11
                                   └─► P9·B1     └─► P15  (also needs P8, P14)

     ADDED BY THE ADVERSARY PASS:  P9·B4 ─► P10·B2      (P10·B1 still starts after P7)
```

**The edge that was missing, and it moves the schedule (F34).** `P9-B4 → P10-B2` is real and is argued in
`plan/05-phases-probes-attestation.md` P10's entry criteria: the residue is *"WRONG mutants that no
predicate **and no relation** rejects"*, so computing it before the relations are admitted **overstates
it**, which flatters us. This graph had P10 depending on P6 and P7 only. With the edge, P10-B2 cannot
start until P9 ends. §4.1 and §7 are recomputed against it, and **the `k = 0` re-route through
`P0→…→P7→P10→P11` is ten days longer than this document used to say.** A schedule that is wrong in the
failure branch is wrong exactly where it will be read under pressure.

Every edge is a real constraint:

- **P1 → P2**: the induction reads what the dual reader agreed on. Inducing from a single reader
  reintroduces the exact defect (openpyxl reports **35 of 54** validations and the AML-CFT sheet as
  **0 where it is 5**, MEASURED).
- **P2 → P3**: the fact table's keys and the evaluator's cell graph are both projections of the induced
  schema. A fact table keyed on coordinates instead of `(sheet, merged_header_path, row_label)` silently
  rebinds on a row insertion.
- **P3 → P4**: the harvest emits CEL envelopes over fact-model paths; the paths must exist first.
- **P4 → P5**: an evaluator cannot evaluate an envelope format that is not fixed, and pre-flight (rule 2)
  requires `schema_keys` to be exact — which is P4's both-ways AST check.
- **P5 → P6**: a mutant is "killed" iff a predicate FAILs on it, so the verdict model must exist before a
  kill rate can be defined.
- **P3 → P6**: the observability filter *recalculates* to decide whether a mutant changed any cell value.
  Without the evaluator there is no `O` and `K/O` is undefined.
- **P6 → P7**: G2 is the expensive gate and its harness is P6.
- **P7 → P8**: G4 is computed against the already-admitted set (`marginal_ffr`, `conditioned_on`), so it
  needs a registry.
- **P8 → P12**: an obligation "survives all five gates" is undefined until all five gates exist. Running
  the settling experiment before G4 exists would measure a curation, not a model.
- **P12 → P13**: **nothing of L3 may be written before the decision record exists.** CI enforces it.
- **P10 → P11**: the attestation carries `livenessProof{canariesRun, canariesPassed}`; there is nothing to
  sign until the canaries run.
- **P9-B4 → P10-B2** *(added by the adversary pass, F34)*: the residue set is *"WRONG mutants that no
  admitted predicate **and no admitted relation** rejects."* Relations are admitted at P9-B4. Computing
  `|RESIDUE|` before then produces a **larger** number than the truth — an error in the flattering
  direction, on the phase whose output is the publishable result.

### 3.2 The EVIDENCE order — what should be built first because it kills the design cheapest

Ranked by **blast radius per working day**. A negative result higher in this list deletes more of the plan
for less money.

| Rank | Item | Cost | What a negative result deletes |
|---|---|---|---|
| 1 | **E1 / E1b — the two field observations** (IFSCA Division of Investment Funds; KFin/CAMS/Basiz) | 20 min + 1 call, then wait | **The product framing, not the architecture.** Under a deadline these ranked joint-first because they could stop you spending the two days. With no deadline they cannot end the programme — they change what is *claimed*, and the claim is written last |
| 2 | **The dual-reader agreement across nine workbooks** (P1) | ~8 d | Every number downstream. This is where four of the five documented silent false negatives live |
| 3 | **The formula evaluator's cached-value positive control** (P3, = E11) | ~3 d inside P3 | **Three phases at once.** No observability filter ⇒ no `O` ⇒ no `K/O` ⇒ G2 is a reach measurement, not a quality measurement; and `TEMPLATE_DIFF`, predicate #1, is unbuildable |
| 4 | **The mechanical transfer arm across all nine workbooks** (P4-B4, = E4 arm 1) | ~1 d given P2+P4 | The claim to be a **product** rather than a paper about one workbook. Needs no model and no corpus |
| 5 | **The blind-fill corpus** (P8-B1, = E8) | 15–25 **person**-days of someone who is not the engineer | **Every FFR the product displays**, and with it the defensibility of the headline. Highest blast radius of anything that is not cheap. **Zero code dependencies** |
| 6 | **The formula-override differential end-to-end** (P9-B1, = E3) | ~2 d | Nothing, but load-bearing: it is the flagship, its oracle is the published blank, and it needs no corpus |
| 7 | **The free baselines B0 ∪ B1 ∪ B2** (P12-B2, = E5) | ~1 d | Nothing directly — but without them P12 is uninterpretable, because two of the three demolitions in this literature are demolitions by baseline |
| 8 | **The settling experiment** (P12, = E6) | 6 engineer-d + ~$13 | **L3 and only L3.** Ranked eighth deliberately: it can only tell us how large the model's role is, and the architecture survives its failure smaller |
| 9 | **The residue set** (P10-B3, = E7) | ~5 d + adjudication | Nothing — it *is* the publishable result, and it is graded structurally impossible to come back empty |
| 10 | **The conformal feasibility gate** (P13-B3, = E10) | ½ d on paper | The conformal machinery. Largely pre-settled: **0 of 3,755** unlocked cells are ambiguous under the address key |

**E0 is retired.** The portal check (`giftifih.getkruu.com/apply`, HTTP 404, applications closing 16 Aug)
was the only item that could end the programme, and the programme it could end no longer exists. It is
removed from the queue rather than deferred, so nobody spends ten minutes on it out of habit.

### 3.3 The six conflicts, and which ordering wins

> **Standing bias this reconciliation is written against:** *will pay any price to avoid believing
> something false, almost none to find out whether the thing is over.* Every conflict below is resolved in
> the direction that finds out sooner, except where finding out sooner would produce a number that is not
> yet interpretable.

**Conflict 1 — the blind-fill corpus. EVIDENCE WINS, decisively.**
Dependency says the corpus belongs in P8, after P7. Evidence says it decides whether *any* predicate is
admissible and it is bound by a human's calendar, not by a compiler.
**Ruling: P8-B1 is unbundled from P8 and starts at P0-time, in its own lane, in parallel with the entire
engineering track.** It has literally zero code dependencies — it needs the blank template (on disk), the
regulation (public) and a person who has never seen the predicate set. Starting it late is not a schedule
error, it is an *evidence* error: the firewall is easier to hold the earlier it starts, because there is
less predicate set in existence to leak. **The longest pole in this plan is not the code. It is the
corpus.**

**Conflict 2 — `TEMPLATE_DIFF`, the flagship. EVIDENCE WINS, partially.**
Dependency puts all 25 relations in P9, after P7, because relations pass the same five gates as any other
predicate. Evidence says the formula-override differential needs no corpus (its oracle is the regulator's
published blank), it is predicate #1, and it is demonstrable the day P3 and P5 land.
**Ruling: P9-B1 is authorised to run immediately after P5 as a spike with a stated non-admitted status.**
Its output is a *demonstration*, not an admission. It re-enters P9 to pass G0–G4 before it may settle a
single cell, and a test — `test_unqualified_relation_cannot_settle_a_cell` — asserts that a relation
without a `qualification` block contributes to `NO_PREDICATE`, never to `settled`. The discipline is
preserved and the evidence arrives twelve weeks earlier.

**Conflict 3 — the transfer measurement. EVIDENCE WINS for the mechanical arm.**
Dependency puts transfer late, because measuring *human cost per transferred predicate* requires the
qualification machinery. Evidence says the mechanical arm — induce and harvest across all nine, publish
the per-template field surface and the per-workbook distribution of the 515 figure — costs one day and
answers "product or paper" at the cheapest price in the plan.
**Ruling: the mechanical arm moves into P4-B4. P15 retains only the cost-bearing arm and the E4
threshold.** The spec already makes publishing the 515 distribution a build gate, because no research lane
published it; P4-B4 is where that debt is paid.

**Conflict 4 — the settling experiment. DEPENDENCY WINS, and the evidence order agrees.**
There is a standing temptation to run E6 early because it costs about thirteen dollars. Resist it.
**Ruling: P12 stays at P12, after P8.** The experiment's entire epistemic value is that *the gate was
specified before the model ran* — and a gate that does not exist cannot be the specified one. Run it
against four gates and a placeholder and you have measured a curation, not a model. **There is no version
of this experiment worth running before P8 completes.**

**Conflict 5 — the surfaces. SPLIT: dependency permits early, evidence gates the FFR-bearing half.**
P14 needs only P5. But a surface is exactly where an unqualified number leaks into a screenshot.
**Ruling: P14 splits at the corpus boundary.** B1–B3 (the self-contained report, the drop screen, the API)
may run in parallel from P5. **B4 — the predicate library with its FFR column and five-gate attrition
funnel, and the settled-fraction-over-time chart — is hard-gated on P8.** This is the task's rule *the
FFR-bearing surfaces cannot ship before a blind-filled corpus exists*, mechanised as gate **G-CORPUS**.

**Conflict 6 — the two field observations. NEITHER WINS OUTRIGHT; both run at P0 and gate nothing.**
Under the deadline the spec ranked E1 and E0 joint-first, because they were the only two things that could
tell you the project was over. E0 is retired. E1 survives with its blast radius *reduced*: if IFSCA already
validates on receipt, the filer-side product is reclassified as a convenience and the research result — the
residue set, the gate, the coverage declaration — becomes the headline. That reclassification changes
**phase priority** (P9, P10 and P11 rise; P14 and P15 fall) but not a single line of architecture.
**Ruling: E1 and E1b are P0-B4, with a named sender and a dated record in `docs/FIELD-OBSERVATIONS.md`.
They block no engineering phase.** If no reply exists when P14 starts, **the non-answer ships as a visible
open item on the report surface and in the claim register — never as silence.** That last clause is the
whole point: the failure mode here is not a wrong answer, it is a question quietly dropped because nothing
depended on it.

---

## 4. THE DEPENDENCY GRAPH

```
                          ┌──────────────────────────────────────────────────────┐
                          │ P0  REPO · CI · COMMITMENT GATES · FIELD OBSERVATIONS │  4 d
                          └───────────┬──────────────────────────────┬───────────┘
                                      │                              │
     ══════════════ ENGINEERING LANE ═╪══════════      ══ CORPUS LANE (calendar-bound) ══
                                      │                              │
                                      ▼                              ▼
                          ┌───────────────────────┐   ┌──────────────────────────────┐
                          │ P1  L0 INGEST      8 d│   │ P8·B1 BLIND-FILL CORPUS      │
                          │  ══ G-READERS ══      │   │  ≥30 workbooks · Person A    │
                          └───────────┬───────────┘   │  15–25 PERSON-days           │
                                      ▼               │  ZERO code dependencies      │
                          ┌───────────────────────┐   │  STARTS AT DAY 0             │
                          │ P2  L1 INDUCTION ·   │   └───────────────┬──────────────┘
                          │  FIELD SURFACE   10 d│                   │
                          │  ══ G-DENOM ══ ◄ BARRIER 1               │
                          └───────────┬───────────┘                   │
                                      ▼                               │
                          ┌───────────────────────┐                   │
                          │ P3  FACT MODEL +     │                   │
                          │  FORMULA EVALUATOR 12d│                   │
                          │  ══ G-EVAL ══  ◄ BARRIER 2                │
                          └───────────┬───────────┘                   │
                                      ▼                               │
                          ┌───────────────────────┐                   │
                          │ P4  PREDICATE OBJECT ·│                   │
                          │  CEL · HARVEST    14 d│                   │
                          │  ══ G-CELPY ══        │                   │
                          │  B4 ═► G-TRANSFER/mech│                   │
                          └───────────┬───────────┘                   │
                                      ▼                               │
                          ┌───────────────────────┐                   │
                          │ P5  RUN ASSEMBLY ·    │                   │
                          │  VERDICT · CLOSURE 12d│                   │
                          └──┬────────┬────────┬──┘                   │
              ┌──────────────┘        │        └──────────────┐        │
              ▼                       ▼                       ▼        │
   ┌────────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
   │ P9·B1 TEMPLATE_DIFF│  │ P6 FAULT SEEDING │  │ P14·B1–B3        │  │
   │  spike, NOT admitted│  │            10 d │  │  SURFACES        │  │
   │  (evidence pull-fwd)│  └────────┬─────────┘  │  report/drop/API │  │
   └────────────────────┘           ▼            │            12 d  │  │
                          ┌───────────────────────┐└────────┬─────────┘  │
                          │ P7  GATES G0/G1/G3 ·  │         │            │
                          │  REGISTRY · ADMIT 14 d│         │            │
                          │  ◄ BARRIER 3          │         │            │
                          └──┬────────┬────────┬──┘         │            │
              ┌──────────────┘        │        └───────┐    │            │
              ▼                       ▼                ▼    │            │
   ┌────────────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │
   │ P9  L6 PROBES  14 d│  │ P10 CANARIES +   │  │ P8  G4 · FFR ·      │◄┘
   │                    │  │  RESIDUE     10 d│  │  SEVERITY       8 d │
   │                    │  │ ══ G-LIVENESS ══ │  │ ══ G-CORPUS ══      │
   └────────────────────┘  └────────┬─────────┘  │      ◄ BARRIER 4    │
                                    ▼            └──┬───────────┬──────┘
                          ┌───────────────────────┐ │           │
                          │ P11 ATTESTATION ·     │ │           ▼
                          │  verify          10 d │ │  ┌──────────────────┐
                          │  ══ G-REPRO ══        │ │  │ P14·B4 FFR-BEARING│
                          └───────────────────────┘ │  │  SURFACES        │
                                                    │  └────────┬─────────┘
                                                    ▼           │
                                          ┌───────────────────────┐         │
                                          │ P12 SETTLING EXPT  6 d│         │
                                          │  ══ G-SETTLE ══       │         │
                                          │      ◄ BARRIER 5      │         │
                                          └───────────┬───────────┘         │
                                                      ▼                     ▼
                                          ┌───────────────────────┐ ┌───────────────────┐
                                          │ P13 L3 · L1b · L2b ·  │ │ P15 TRANSFER(cost)│
                                          │  WATCHER        16 d  │ │  CHURN · OPS ·    │
                                          │  ══ G-CONFORMAL ══    │ │  DEPLOY      10 d │
                                          └───────────────────────┘ └───────────────────┘
```

**Durations corrected by the adversary pass, since the boxes above are drawn and not recomputed.**
**P6 = 10.5** (F18's three-way observability, F19's `formula_source`) · **P7 = 16** (P7-B0's instrument
text source moved here from P12-B1 — F35 — plus F9's template instrument) · **P8 = 9.5** (F2's
`derived_by` split and foreign-engine path, F16's signed contamination result, F36's mask check).
**The box art is not authoritative; §7's table is.**

### 4.1 What can run in parallel

| Lane | Phases | Earliest start | Notes |
|---|---|---|---|
| **Corpus lane** | P8-B1 | day 0 | Different person. Never merge into the engineering lane's day count |
| **Spine** | P0→P1→P2→P3→P4→P5→P6→P7→P8 | serial | Every edge in §3.1 is real |
| **Flagship spike** | P9-B1 | after P5 (day 60) | Non-admitted status enforced by test |
| **Surfaces (non-FFR)** | P14-B1–B3 | after P5 (day 60) | Renders from `run.jsonl`; needs nothing from P6–P8 |
| **Probes** | P9-B2–B4 | after P7 (day 86) | ∥ P8 and P10-B1 |
| **Self-check** | P10-B1 | after P7 (day 86) | ∥ P8 and P9 |
| **Self-check** | **P10-B2–B4** | **after P9-B4 (day 100)** | **F34: the residue needs the admitted relations. This is the edge that moves P11** |
| **Attestation** | P11 | after P10 (day ~106) | **no longer ∥ P12 in the `k = 0` branch — it is the critical path there** |
| **Ops / transfer(cost)** | P15 | after P8 + P14-B4 (day 97) | ∥ P12, P13 |

### 4.2 The five hard barriers

A barrier is a point past which a class of work is **forbidden**, not merely inadvisable. Each is enforced
by a test, not by a convention.

| # | Barrier | Enforced by |
|---|---|---|
| **1** | **No fraction may be computed before the denominator exists and has been computed twice by independent code paths.** | `test_denominator_provenance` (asserts the denominator derives from the `styles.xml` unlocked mask, never from the predicate set) + `invalid.denominator_disagreement` |
| **2** | **No kill rate, no observability filter and no `TEMPLATE_DIFF` before the evaluator reproduces the regulator's own cached values.** | Gate **G-EVAL**; the renderer refuses to print `K/O` when `qualification.g2.harness` was qualified against an unverified evaluator |
| **3** | **No predicate may be evaluated against a filing unless it loaded from the registry with a `qualification` block.** | The loader: *a predicate row with no qualification row does not load*, plus `test_unmeasured_predicate_rejected` which attempts the admission and asserts the rejection |
| **4** | **No FFR digit reaches any surface, API response or attestation before a non-`SELF-AUTHORED` corpus exists *and the corpus's independence of that predicate has been computed rather than declared*.** (F2/F5: a corpus label is not independence. `TEMPLATE-COMPUTED` was `ADMISSIBLE` while being produced by the very evaluator the arithmetic predicates re-check) | Gate **G-CORPUS**; `test_ffr_provenance`; `SELF-AUTHORED` renders the word `uninformative` and no digits; **`g4_ffr.independent()` raises `UninformativeCorpusError` when a predicate reads a cell the corpus generator computed** (`plan/04` P8-B3), and `test_clean_corpus_is_not_produced_by_the_code_under_test` is its guard |
| **5** | **No line of L3 code is written before the settling experiment's decision record exists.** | CI: presence of `src/cdfc/model/propose.py` without `experiments/E6/DECISION.md` fails the build |

---

## 5. THE PHASES

Each entry gives: what it settles · entry criteria · the 1–4 builds with their primary module · **the one
number the phase produces** with denominator and warrant · the headline negative control · the exit gate ·
what a failure kills · effort. Per-build test sets, signatures and fixture names are the detail documents'
job (§9).

---

### P0 — REPOSITORY, CI, AND THE COMMITMENT GATES · 4 days

**Settles.** Whether this project's own commitments can be enforced by a machine *before* there is code to
violate them — and what the two field observations say.

**Entry.** None. This is the root.

**Builds.**
1. **Repo skeleton and licence.** `LICENSE` (Apache-2.0, first file created — it carries a patent grant
   and every core dependency chosen is compatible), `pyproject.toml`, `src/cdfc/` package tree, `Makefile`,
   `.github/workflows/ci.yml`. Pinned toolchain: Python, `lxml` 6.1.1, `openpyxl` 3.1.5, `celpy`, `z3`,
   `mutmut` 3.7.0 — by name **and wheel hash** (two different projects live at a path called `cel-python`).
2. **The corpus of real artifacts, vendored and content-addressed.** The nine workbooks copied into
   `corpus/templates/` with `sha256`, `origin_uri`, `retrieved_at` recorded in `corpus/MANIFEST.json`.
   `make corpus-verify` re-hashes and fails on drift.
3. **The commitment gates, written first and demonstrated to fail.** `ci/no-green-tick.sh`;
   `ci/licence-gate.sh` over the dependency tree; the negative-control harness `tests/negative/` and its
   runner; `tools/mutation.sh` (mutmut over `src/cdfc/`); the stub tests named in the spec's build-gate
   list, each committed **red** with a named broken build in `tests/fixtures/broken/`.
   **And three registry disciplines, which must exist before the first entry is written** (adversary test
   10, F8/F11/F27): `tests/negative/catalogue.yaml`, `surface/labels.py::SURFACES` and `REQUIRED_NUMBERS`
   are **append-only with a growth log**; a removal requires a dated argument in the owning measurement
   file; each publishes **its cardinality as a time series**, so a registry that shrinks the day before a
   gate is read is visible. Guards: `test_nc_meta__catalogue_is_append_only`,
   `test_nc_meta__ids_are_unique`, `test_nc_meta__id_is_inside_its_document_range`,
   `test_surface__registry_is_append_only`, and `ci/catalogue-ids.sh`. **Every gate in this plan whose form
   is `k of n` where we also write `n` is one refactor away from being `n of n`** — the plan already
   mechanises this discipline for `docs/HARVEST-DELTA.md` and `docs/GATE-CHANGES.md` and had not applied it
   to the denominators of its own gates.
4. **The field observations.** `docs/FIELD-OBSERVATIONS.md`: E1 (IFSCA Division of Investment Funds —
   are these checks run on receipt? how often is an FME return sent back? are filed returns obtainable?)
   and E1b (KFin / CAMS / Basiz — the written house NAV tolerance question, verbatim from spec §IV.1.2).
   Named sender, date sent, date of reply or the standing absence.
   Also `docs/ABSENCE-SCOPE.md`, the written inclusion rule that closes risk R13 — **no absence claim ships
   with a count until this exists.**

**The number.** `gates_live / gates_written` — the fraction of CI commitment gates that have been
**demonstrated to fail** against a named broken build, denominator = the **18** build-gate rows `plan/02`
§1 R5 enumerates (arbitration **C4**; `plan/02` owns P0, and its enumeration closes arithmetically —
15 `LIVE` + 3 `PENDING` = 18. The "16 gates" summary this line previously carried had drifted from its
source and counted the predicate-loader admission twin, which R5 rules is not a row). Warrant **MEASURED**.
This number does not exist anywhere today: the spec lists the gates; none has been observed to fail.

**Negative control.** A commit adding the string `✅ All clear` to `src/cdfc/surface/templates/report.html.j2`
— `ci/no-green-tick.sh` must exit non-zero. A commit adding a GPL-3.0 dependency — `ci/licence-gate.sh`
must fail. A predicate YAML with no `qualification` block — the loader stub must refuse.

**Exit gate — restated, because `gates_live == gates_written` is `x == x` (F8).** `gates_written` was
defined as *the gates whose subject exists*, which is decided by the same person deciding whether a gate
can be demonstrated: any gate that resists demonstration moves to `PENDING` with a phase name attached —
which this plan explicitly permits — and the ratio becomes `n/n`. **The gate could not fail, and it is
the gate that certifies the honesty machinery every later phase's DoD depends on.**

> **The set is pre-registered, not the count.** `ci/GATES.md` rows **`{1…13, 17, 18}`** are named in
> `plan/02-phases-foundation.md` §1 R5 as demonstrable at P0 — **15 `LIVE` of 18**. **P0 exits iff those
> fifteen row ids are `LIVE`**, each with its failure observed in CI logs and recorded in
> `docs/GATE-LIVENESS.md`, **and the `PENDING` set is exactly `{14 → P2, 15 → P11, 16 → P13-B0}` — three
> rows.** Moving any of the fifteen to `PENDING` **fails the gate** and requires an appended, dated argument
> in `ci/GATES.md` — the same discipline as `docs/HARVEST-DELTA.md`. Guard:
> `test_contract__live_set_is_pre_registered`, which asserts both sets as literals. A gate that has never
> been red still does not count.
>
> *(Arbitration **C4**. This box previously read "rows 1–13", "thirteen row ids" and "the `PENDING` set is
> exactly the four named rows", guarded by `test_p0__pending_set_is_exactly_the_four_named_rows`. `plan/02`
> owns P0; its enumeration is explicit and closes arithmetically (15 + 3 = 18); this one was a summary that
> drifted from its source. **The old guard is DELETED, not renamed — its name asserts a count that is
> wrong**, and a test name that carries a false number survives every rename that only changes the code.)*

**Kills if it fails.** Nothing structural, but it kills the plan's own claim to discipline. If a commitment
cannot be mechanised, it is downgraded to a documented preference **in writing**, and the count of
un-mechanised commitments is published on the report surface.

---

### P1 — L0: RECEIPT, CONTAINER GUARD, DUAL-READER INGEST · 8 days

**Settles.** Whether the artifact can be read without the class of silent under-count this project has
committed five times — and what the two readers actually disagree about, on the real corpus.

**Entry.** P0 complete; the nine workbooks vendored and hashing stably.

**Builds.**
1. **Receipt and content addressing.** `src/cdfc/ingest/receipt.py` — `sha256` over exact received bytes,
   lowercase hex, `blobs/sha256/<aa>/<rest>`; per-sheet hash of every `xl/worksheets/sheetN.xml`;
   `run` row. Over cap → `413`, non-zip → `415`, **no run row**. RFC 8785 for every hashed JSON object.
2. **The container guard.** `src/cdfc/ingest/guard.py` — entry count, per-entry uncompressed size, total
   ratio, media types, required parts, **all before any XML is parsed**. `lxml` with
   `resolve_entities=False`, no DTD, no network. Any trip → run-level `invalid.container_guard_tripped`
   (the run-level vocabulary, *not* an item reason code — spec §V.7.3).
   Sandbox: gVisor `runsc` + `seccomp` + `--network=none` + read-only rootfs + RLIMIT + wall-clock kill.
3. **The two readers and the agreement vector.** `reader_lxml.py` (authoritative: raw `zipfile` + `lxml`,
   namespace-aware, `extLst`/`x14`, `styles.xml`, `sharedStrings.xml`) and `reader_openpyxl.py`
   (formula text with shared-formula row-shifting; `data_only=True` cached values — **never for
   validations, never to re-serialise**). `agreement.py` compares
   `{n_sheets, sheet_names, hidden_sheets, n_cells, n_formula_cells, n_validations, n_defined_names,
   merged_ranges}`. Disagreement on the first three → `invalid.reader_structural_disagreement`.
   Elsewhere → those fields marked, and every predicate reading them later returns
   `NOT_RUN(not_run.extractor_disagreement)`.
4. **The extraction manifest as a first-class output.** `manifest.py` — parts read, parts skipped,
   namespaces seen, constructs not understood. Not a log.

**The number.** The **reader-agreement vector** — agreeing fields / (8 fields × 9 workbooks) = **/72** —
plus, for each disagreeing cell of that matrix, the field, the two values and the mechanism. Warrant
**MEASURED**. Today only one disagreement is known (35 vs 54 validations on the FME workbook); the other 71
cells are unmeasured.

**Negative control.** `tests/fixtures/broken/reader-disagree.xlsx` — a workbook whose `workbook.xml`
declares a sheet the parts do not contain: the run must be `INVALID`, loudly.
`test_regex_reader_undercounts_and_is_rejected` — the historical `<f[ >][^>]*>` regex is re-encoded as a
fixture reader and must report **294** where truth is **505**; the test asserts the agreement check
catches it. (The superseded script itself is deleted, not kept beside the correct one.)
`test_openpyxl_never_writes_the_artifact` — an openpyxl round-trip fixture must show
**3,663,391 → 65,877 bytes** and 19 lost `x14` validations, and any code path that writes the artifact
back fails the build.

**Exit gate.** All nine workbooks ingest; the agreement vector is published in
`docs/measurements/P1-agreement.md` with every disagreement's mechanism named; the container guard trips
on each of five crafted hostile fixtures; no code path re-serialises a received filing.

**Kills if it fails.** If the readers cannot be reconciled on a workbook, **that workbook is excluded from
the corpus with a stated reason and its field surface is `null`** — the corpus shrinks, the plan continues.
If they cannot be reconciled on the FME workbook specifically, P2's denominator is unfounded and the whole
plan halts at barrier 1 until one reader is proven right by a third, offline, digest-pinned reader.

---

### P2 — L1: SCHEMA INDUCTION, THE FIELD SURFACE, STABLE KEYS · 10 days

**Settles.** The denominator every subsequent number is a fraction of — for **all nine** workbooks, not
one, computed twice by independent code paths.

**Entry.** P1 complete; the agreement vector published.

**Builds.**
1. **Induction from the blank template, pinned by hash.** `src/cdfc/schema/induce.py` — all sheets
   including `state="hidden"`; `extLst`/`x14` data validations; shared formulas materialised
   (`<f t="shared" si="N"/>` has no text node — 211 of 505 on the FME workbook, **825 of 1,495 = 55.2%**
   across the nine); merged ranges; defined names including the **4 pointing at `#REF!` in the regulator's
   own published blank**; protection state per sheet; the 15 vocabularies on the hidden `Dropdown` sheet.
   **Vocabularies resolve from the pinned blank, never from the filed artifact** — `Dropdown` is hidden
   *and* the only unprotected sheet.
2. **The unlocked-cell mask and the field surface, computed twice.** `src/cdfc/schema/mask.py` —
   `cellXfs → <protection locked="0"/>`. Two independent implementations; disagreement →
   `invalid.denominator_disagreement`. For a template shipping no protection mask,
   `field_surface = null` and `denominator.source = "not derivable — template ships no protection mask"`.
3. **Stable keys and the resolution state.** `src/cdfc/schema/keys.py` —
   `(sheet_name, merged_header_path, row_label)` with coordinates as a *resolved attribute*, plus the row
   ordinal that disambiguates (under a naive `(sheet, label-above, label-left)` key **1,749 of 1,953 cells
   are ambiguous — 89.6%**). Unresolvable keys enter `UNRESOLVED` and **block** their predicates.
4. **The structural fingerprint.** `src/cdfc/schema/fingerprint.py` — over
   `(sheet names + states, dimensions, merged-range set, defined-name list, unlocked mask)`.
   **Formula content is deliberately excluded**, so that a filer who overwrote a formula with a literal
   fails a *predicate*, not the *binding*.

**The number.** **The field surface for all nine workbooks**, with `computedTwiceAgreed` per workbook and
the count of templates for which no mask is derivable. Denominator: 9 workbooks. Warrant **MEASURED**.
Today exactly one of the nine is measured (FME = 3,747; per sheet Portfolio 1,698 · Investors 897 ·
PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22). The spec
asserts two of the nine ship no mask — **that is an assertion this phase converts to a measurement.**

**Negative control.** `tests/fixtures/broken/inducer_visible_sheets_only.py` — an inducer variant
iterating visible sheets only. The vocabulary set is then empty and `all(v in vocab …)` passes vacuously;
the phase gate must detect the empty vocabulary and refuse.
`test_denominator_provenance` — a denominator computed as `union(predicate graph, validation cells)`
must be rejected; this is the circular 99.2% that was produced twice in one afternoon by the person
hunting for it.
`test_schema_constants` pins **505 / 294 / 211 / 54 / 22 / 20 / 252 / 3747** — properties of the published
file, where a change is a parser regression. Split from `test_harvest_count` (P4) deliberately: a
regression test that fails on correct behaviour gets deleted.

**Exit gate.** `test_schema_constants` green; the field surface computed twice and agreeing on every
workbook that has a mask; the parse round-trip reproduces all 505 formula cells, all 54 validations, all
252 merged ranges, the hidden sheet and its 15 vocabularies; `docs/measurements/P2-field-surface.md`
published with all nine rows including the `null` ones.

**Kills if it fails.** If the mask is not recoverable for a workbook, that workbook has **no settled
fraction, ever** — `settledFraction: null`, published as such. If it is not recoverable for the FME
workbook, the headline triple 2,373 / 1,374 / 3,747 is withdrawn and the product's primary claim becomes a
count of failures with no denominator, which is a strictly smaller and still honest product.

---

### P3 — THE TWO EVALUATION SUBSTRATES: FACT MODEL AND FORMULA EVALUATOR · 12 days

**Settles.** Whether our recalculation reproduces the regulator's own cached values — the oracle on which
the observability filter, every kill rate, and the flagship `TEMPLATE_DIFF` all depend. **This is
experiment E11 and it is the highest evidence-per-day item in the engineering plan.**

**Entry.** P2 complete; the field surface published.

**Builds.**
1. **The two-document fact model.** `src/cdfc/facts/table.py` — exactly two bound names, `filing` and
   `template`. No clock, no network, no filesystem. Every leaf carries `__cell__`.
2. **Units and tolerance.** `src/cdfc/facts/units.py` — `MILLI_USD_MILLION`, `int64`, 1 unit = USD 1,000,
   `12.34 → 12340`, half-ulp 5 units, `τ(n) = 5n`, `ROUND_HALF_UP`. **Counts get zero tolerance — a person
   is not a rounded quantity.** There is no floating point anywhere below this line.
3. **The provenance anchor union.** `src/cdfc/facts/anchors.py` — Docling's `ProvenanceItem` verbatim for
   the PDF class, extended with `xlsx_cell` (carrying
   `formula.encoding ∈ {TEXT, SHARED_MASTER, SHARED_DEPENDENT, ARRAY, NONE}`) and `register_record`
   (carrying **both** `raw_value` and `normalised_value` plus the transformation list — one live entity's
   registration number contains `U+2011`, visually identical and byte-wise different).
4. **The formula evaluator and its positive control.** `src/cdfc/calc/` — topological sort over the induced
   cell graph in `Decimal`; eight functions exactly: `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`,
   `ROWS`, `AGGREGATE(15,6,…)`. **The positive control is the phase:** recalculate the blank template and
   compare against the cached values present on **505 of 505** formula cells, including `_xlfn.AGGREGATE`
   at `'1. Introduction'!C92:E101`. A function outside the vocabulary makes its cells
   `NOT_RUN(not_run.source_unreadable)` — a human decides whether to implement it or promote the pinned
   offline engine.

**The number.** **The cached-value reproduction rate**: cells reproduced exactly / 505 (FME) and
/ 1,495 (all formula cells across the nine). Every non-reproducing cell listed with its cause. Warrant
**MEASURED**. This number does not exist; the spec lists it under "measurements before any number is
quoted" and states plainly that *no kill rate may render before it passes*.

**Negative control.** An evaluator variant that treats `AGGREGATE(15,6,…)` as plain `SUM` — must produce a
mismatch at `'1. Introduction'!C92:E101` and be caught by the positive control. A tolerance implemented as
a fixed epsilon instead of `τ(n) = 5n` — must produce a false failure on a template-computed clean filing.
A fact table built with `float` instead of `int64` — `test_no_float_in_money_path` must fail the build.

**Exit gate — this is gate G-EVAL (§6).** Reproduction is **exact on 505 of 505** for the FME workbook, or
every non-reproducing cell is named, its cause identified, and it is excluded from the observability
filter's site set and flagged `INDETERMINATE(indeterminate.engine_disagreement)` from a pinned per-template
table. If more than 25 cells (5%) fail, **G2 is downgraded to a reach measurement and says so** — see §6.

**Arm 2 gains a failing condition and an author test (F3).** As written, arm 2 required 100% agreement
with a **human-authored expectation file** and merely *published* disagreements against the offline
digest-pinned engine — so **the only independent instrument in the pair contributed nothing to pass/fail**,
and a build disagreeing with it on every non-trivial cell passed. Two changes, both pre-registered:

- **A threshold on the disagreement set.** **`d = 11`, a frozen integer** (arbitration C1), chosen
  **before the first run** and pre-registered in `experiments/G-EVAL/PREREGISTRATION.md` together with its
  derivation `max(3, ceil(0.05 × |non-trivial cells|))`, the content hash of the corpus it was evaluated
  against, and the date: disagreement on more than `d` non-trivial cells **downgrades G2 to a reach
  measurement**, on the same branch as arm 1's 25-cell rule. *A published disagreement that changes
  nothing is a log line, not a gate.* **`d` does not recompute when the corpus moves** — a threshold that
  is a function of the thing it gates is F1 in another costume.
- **`test_arm_two_author_is_not_the_evaluator_author`.** Read the expectation file's author and `calc/`'s
  from a declared `authored_by` field cross-checked against `git blame`. If they are the same person,
  `docs/measurements/P3-evaluator.md`, `ci/GATES.md` **and every surface quoting a kill rate** must carry
  the literal string `SAME-AUTHOR — a weaker instrument`, and G-EVAL is recorded
  **`PASSED — NOT INDEPENDENT`**. There is no third option and no silent one; this test is what makes the
  third option unreachable. The 1.5–2 person-days of a second author belong in P3's effort table alongside
  every other second-person cost (`plan/02-phases-foundation.md` owns that edit); if that person is not
  funded, the `SAME-AUTHOR` branch is the state that ships — see §7's staffing model.

**Kills if it fails.** A total failure kills the observability filter, hence `K/O`, hence every quotable
kill rate, hence gate G2's *quality* interpretation; and it kills `TEMPLATE_DIFF`. The system that survives
is: harvest + verdict model + closure + canaries + FFR, with kill rates reported as `K/G` and explicitly
labelled *reach, not quality*. That is smaller and still shippable.

---

### P4 — THE PREDICATE OBJECT, THE CEL SUBSTRATE, AND THE HARVEST · 14 days

**Settles.** Whether the settled fraction is **derivable rather than estimated** — which is the entire
reason CEL beat Python — and what the harvest actually yields across all nine workbooks.

**Entry.** P3 complete; the fact model stable and the key set frozen for the FME template.

**Builds.**
1. **The predicate envelope.** `src/cdfc/predicate/envelope.py` — the record of spec §II.4.1 verbatim:
   `id, version, kind, template, schema_keys, host_fns, obligation_id, clause{instrument, eId, span,
   quote, provisos[]}, rationale, applicable, expr, witness, reason_if_inapplicable, tolerance,
   severity_tier, external_deps, qualification, qualified_against, state, withdrawn_reason` —
   **plus `claims_fault_classes: tuple[str, ...]`, required and non-empty, added by the adversary pass
   (F1).** Content address = `sha256` of the **RFC 8785** canonical serialisation, **and
   `claims_fault_classes` is inside that serialisation**, so narrowing the claim after a campaign produces
   a *different predicate*, not a better score. **A predicate with no `qualification` block does not
   load**; a candidate with no declared fault-class claim does not load either.

   > **Why the field exists, in one line:** G2's registry bar is *"`K/O ≥ 0.80` on the fault classes the
   > predicate **claims** to cover"*, and until this pass **no field held the claim** — so the classes were
   > read off the witnesses G2 itself selects, *after* the campaign, and every admitted predicate chose the
   > denominator of its own quality score. That is this project's founding defect (a denominator built out
   > of the numerator, committed twice in one afternoon) arriving at the gate built to catch it. The
   > consuming gate, its `O == 0` refusal, its git-ancestry check and NC-Q57 are specified in
   > `plan/04-phases-qualification.md` §0.8(f) and P7-B3.
2. **The admitted CEL subset and the AST walker.** `cel_profile.py` + `ast_walk.py` — a ~20-production
   grammar with enumerable operators; excluded by the walker at admission: nested comprehensions (the only
   route to exponential blow-up the CEL specification names), `filter()` outside `witness`, `map()` outside
   `sum()`, protobuf, `bytes`, `uint`, `type()`, `dyn()`. **`schema_keys` machine-checked against the AST
   both ways** — reads an undeclared key ⇒ REJECT; declares an unread key ⇒ REJECT. *This build is what
   makes the settled fraction exact rather than an estimate.*
3. **The runtime, the conformance run, and the host-function registry.** `runtime.py` over `celpy`, pinned
   by PyPI name and wheel hash, under a step-count budget and a wall-clock kill. **Run the official CEL
   conformance suite against both `celpy` and `cel-expr-python` and record which one the registry root is
   qualified against** — with particular attention to error semantics, because the specification says an
   operand error in `&&`/`||` "will be ignored" and the pre-flight guard's necessity rests on it.
   `hostfn/` — the closed, versioned set: `reg_resolves(kind, number)` (tri-state; **never resolves live at
   verdict time**), `gstin_valid(s)`, `template_current(hash)`, `nav_interval(...)` which **must be able to
   return `UNDERSPECIFIED`**. A host function is added only by a human, never generated by a model.
4. **The harvest into envelopes, across all nine workbooks.** `src/cdfc/harvest/` — nine classes:
   `cross_sheet_equality` 181, `sum_identity` 35, `membership` 20, `numeric_bound` 13, `integer_bound` 11,
   `same_sheet_equality` 11, `date_bound` 6, `tally_identity` 3, `conditional_required` 0. This step
   cannot fail, only under-produce. **This build also carries the mechanical arm of the transfer
   measurement (E4 arm 1)** — see conflict 3.

**The number.** Two, and both are new. **(a)** `schema_keys` both-ways agreement — predicates whose
declared keys equal their AST-read key set / 280 (FME), warrant **MEASURED**; a shortfall here is the
measured size of the gap between "derivable" and "estimated". **(b)** **The per-workbook distribution of
the 515 figure**, denominator 9 workbooks — which the spec makes a build gate precisely because *no
research lane published it*, and because two of the nine workbooks have zero formulas and one has zero
validations as well.

**Negative control.** A predicate reading `filing.x` while declaring `schema_keys: []`, and its mirror
declaring a key it never reads — **both must be REJECTED**. A CEL expression containing a nested
comprehension — refused by the walker. A predicate whose verbatim clause quote does not satisfy
`source_text.find(quote)` — refused at the boundary, at zero model cost. A predicate referencing an
unregistered host function — refused.

**Exit gate.** `test_harvest_count` pins **280 / 515** *with the per-workbook distribution attached* — a
property of our code, **allowed to move with a recorded reason**, since the first thing the gate does is
reject predicates. Both-ways AST check green on 280 of 280. The conformance result recorded in
`docs/measurements/P4-cel-conformance.md`. Gate **G-CELPY** decided (§6).

**Kills if it fails.** If the both-ways check cannot be made exact, **the settled fraction becomes an
estimate and must be relabelled as one everywhere** — a strictly weaker product that still ships, but the
spec's headline argument for CEL over Python is gone and the language decision is re-opened with the
measurement attached. If neither CEL runtime passes on error semantics, the admitted subset is narrowed to
ban `&&`/`||` at the top level of `expr` entirely: a smaller grammar with the same guarantee.

---

### P5 — L5: RUN ASSEMBLY, THE VERDICT MODEL, CLOSURE, THE SETTLED FRACTION · 12 days

**Settles.** The product's core object — and specifically whether the **runtime** settled count falls below
the static harvest figure when a predicate does not run, which is the behaviour the post-audit precedence
resolution exists to produce.

**Entry.** P4 complete; envelopes loading; the evaluator's transition table specified.

**Builds.**
1. **Run assembly.** `template binding` by structural fingerprint (F3 — no match →
   `invalid.template_unbound`, **which escalates**: it is also the signal that a new template version was
   published); `predicate selection` against the pinned registry root (F6 — a predicate qualified against a
   different template is not evaluated and its cells land in
   `NO_PREDICATE(no_predicate.not_yet_requalified)`; a `PROVISIONAL` predicate **still runs** but does not
   count in the numerator); `pre-flight` (F7 — every declared key tested for presence and type **before**
   `expr` is evaluated; exact, not an estimate, because of P4-B2).
2. **The evaluation contract, generated.** `docs/EVALUATION-CONTRACT.md` **generated** by
   `tools/gen_contract.py` from the five rules of spec §II.3.4 — `applicable` · pre-flight · `expr` ·
   warrant composition · `cells_bound` — and a CI test asserting the evaluator's transition table **equals**
   that file. One file. Three drafts gave three different fives; a build cannot satisfy two.
3. **The state and reason vocabulary, and the run-level vocabulary that is separate from it.**
   `verdict/states.py` (8 item states), `verdict/reasons.py` (30 namespaced codes, five families; required
   iff the state is not `PASS`/`FAIL`, forbidden when it is), and `verdict/invalid.py` — the **eight
   run-level `invalid.*` causes**, which are their own closed vocabulary because a container guard trip, a
   reader disagreement, an unbound template and a denominator disagreement are **not properties of any
   cell** (spec §V.7.3). Where a run-level cause has an item-level analogue, both are carried; they are
   not alternatives.
4. **Roll-up, closure, and the settled-fraction object.** `rollup.py` — precedence
   `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`, **a cell is clean only
   if every predicate binding it passed**, `NO_PREDICATE` outside the order as the empty-evaluation-set
   state (spec §V.7.1, binding). `closure.py` — the seven-term invariant
   `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface`,
   one `GROUP BY` over `run_cell`; **a cell landing in no bucket aborts report generation.**
   `settled.py` — the object of spec §III.4.3, never a bare fraction. Output: `run.jsonl` (NDJSON, one line
   per evaluation) and the run manifest's eight pins.

**The number.** The **runtime seven-term closure partition** on a real filing, and specifically the
**runtime settled count and its delta from the static 2,373**. Denominator: the 3,747-cell field surface.
Warrant **MEASURED**. The static figure counts cells reachable by at least one harvested predicate,
computed before any evaluation; the runtime figure is what a filing actually produces, and under the
binding precedence order it can be lower. **Nobody has this number.**

**Negative control.** The six failure modes of spec §II.1.8 as fixtures, each of which must be caught:
(1) `check_all_percentages_sum_to_100` whose selector misses a renamed sheet — `group()` returns `[]`,
`all([])` is `True` — must yield `ERROR(error.cells_bound_zero)` and `run_state = INVALID`, never `PASS`;
(2) empty-set arithmetic `sum([]) == 0`; (3) selector drift over OOXML; (4) scope truncation by hidden
sheet; (5) shared numerator/denominator; (6) a swallowed exception. Plus `test_error_absorption`: a
predicate written `true || <unreadable>` must return `NOT_RUN`, **never** `PASS` (criterion A13). Plus
`test_predicate_raise_is_error`: a runtime error in `expr` is `ERROR(error.predicate_raised)` and the run
is `INVALID`, not `NOT_RUN(source_unreadable)` — the two have opposite remedies.

**Exit gate.** Clean filing → 0 FAIL — **on a clean filing whose derived cells `src/cdfc/calc/` did not
compute** (F2: on the `TEMPLATE-COMPUTED`-by-`calc` corpus this criterion is arithmetically impossible to
violate for the 227 arithmetic predicates, because `calc/` wrote the values the predicates re-check; the
criterion could detect only a predicate that disagrees with itself. It is re-founded on
`derived_by ∈ {FOREIGN_ENGINE, NONE}` or a blind-filled workbook — see `plan/04` P8-B2 — and **one such
filing makes it non-vacuous; zero is what the plan had**). One seeded fault → exactly the predicates
reading that cell FAIL. `cells_bound == 0 ⇒ ERROR ⇒ INVALID` demonstrated. Closure holds on all nine
workbooks that have a mask, or report generation aborts. `test_settled_fraction_falls_on_not_run` green —
a cell read by one passing and one not-run predicate is **unsettled**.

**Two additions from the adversary pass, both about the direction the headline can move.**

- **`test_prop__fraction_does_not_rise_as_the_filing_empties` (F13, FATAL).** For every filing `F` and
  every value-deletion transform `d`, `fraction(d(F)) ≤ fraction(F)`. The plan guarded the empty-filing
  attack at the *state* level (NC-R01: a partition relation returns `OUT_OF_SCOPE`, never `PASS`) and left
  it unguarded at the *fraction* level — and `OUT_OF_SCOPE` is **removed from `inScope`**, the fraction's
  denominator. So the defence against the empty filing is a mechanism that shrinks the denominator, and
  there is a sparse-but-lawful filing shape on which **a filer who fills less scores better**.
  **DECIDED, so that the property can hold rather than merely be measured:** `OUT_OF_SCOPE` arising from a
  **non-degeneracy precondition** stays in `inScope` — it is a statement about *this filing*, not about
  *applicability* — **and** every surface renders `inScope` beside `cellsTotal` so a shrinking denominator
  is visible. *Alternative it beat:* rendering only, with the property left failing — rejected because a
  visible wrong direction is still a wrong direction. Companion, owned by `plan/05`:
  `test_defect_table_cannot_raise_the_settled_fraction` (F14).
- **The static `2,373` is computed, not pinned (F22).** P5's delta is measured against
  `static_settled_cells(schema, registry)` **computed from the emitted envelopes**, reconciled in writing
  against 2,373 in `docs/measurements/P4-harvest-distribution.md`; a divergence is a finding, and the
  literal moves into `docs/HARVEST-DELTA.md`. **The first thing the gate does is reject predicates, which
  lowers the reachable set — so a pinned literal would fail on correct behaviour and be quietly updated,
  which is how a golden test launders a warrant.**

**Kills if it fails.** If closure cannot be made to hold, the report cannot be generated at all — that is
the design's `DISALLOW *` and it is not negotiable. There is no degraded report. The failure branch is to
narrow the field surface to the sheets where closure does hold, publish the excluded sheets by name, and
carry the exclusion on the surface.

---

### P6 — THE FAULT-SEEDING HARNESS · 10.5 days

**Settles.** Whether a kill rate over *our* operator mix means anything — by measuring our own `U/G`
rather than assuming the literature's 46.8%.

**Entry.** P5 complete; **P3's G-EVAL passed** (barrier 2 — without the evaluator there is no `O`).

**Builds.**
1. **The fault model, versioned.** `src/cdfc/fault/model.py` — Abraham & Erwig's 17 spreadsheet mutation
   operators (IEEE TSE 35(1):94–108, 2009) plus **F12 vocabulary drift, F13 carry desync, F14
   vocabulary-gap exploitation**. Versioned as `v3`; every quoted kill rate carries the version.
2. **Raw-zip surgery.** `src/cdfc/fault/surgery.py` — copy every part byte-for-byte, rewrite exactly one
   worksheet XML. MEASURED property to preserve: one part differs, the 3.55 MB data model and all 19 `x14`
   validations survive byte-identical.
3. **The observability filter.** `observability.py` — recalculate via P3's evaluator **with
   `formula_source="FILING"`**, diff the value grid, **exclude mutants no cell value distinguishes**.
   `O = G − U − I`. The discard is high and variable by operator mix; **we report our own figure every run
   rather than assuming a published one.** Two corrections from the adversary pass, both FATAL and both
   specified in `plan/04-phases-qualification.md` P6-B3:
   - **Three-way, not two (F18).** A cell our evaluator could not compute is identical in both grids *by
     construction*, so under a two-way filter every mutant propagating only through such a cell was banked
     as `UNOBSERVABLE`, left `O`, and **raised** `K/O`. `INDETERMINATE_OBSERVABILITY` is its own class and
     its own published integer `I`, with the cells named; **`U/G` never renders without `I` beside it.**
   - **`formula_source` is explicit (F19).** Recalculating a mutant through the *template's* formula graph
     overwrites an F11 literal with the formula's value, so the flagship fault class classified
     `UNOBSERVABLE` with `O = 0` — and `kill_rate()` raises when `O == 0`, meaning **`TEMPLATE_DIFF`, the
     relation this design is built around, could never be admitted at G2** while P9 stayed green because it
     does not use this filter. Observability uses `FILING`; `TEMPLATE_DIFF` uses `TEMPLATE`; the rule is
     published in `docs/EVALUATION-CONTRACT.md` and asserted by `test_f11_mutant_is_observable` and
     `test_g2_admits_template_diff`.
4. **The site set and the control arm.** Seeding targets the fields `schema_keys` reads **plus a 10%
   control sample of fields no predicate reads**. Without the control arm a flag-everything predicate
   scores perfectly.

**The number.** **`U/G` for our operator mix**, and `K/O` per fault class, both integers, both published
per run. Denominator: generated mutants `G`. Warrant **MEASURED**. Today the harness reports
19,782 mutants / 3,574 killed / 22 equivalent — a naive `MS = 18.09%` computed as `K/(G − equivalent)`,
which is **the wrong denominator under this specification** and which the caution in spec §II.4.3 explains:
every arithmetic operator killed at exactly 18.1%, identical to the fraction of sites inside the field
graph, so for identity predicates **kill rate is measuring predicate *reach*, not predicate *quality***.
P6 replaces that figure with `K/O` and says which it is showing.

**Negative control.** A site set sampled from the **predicate graph** instead of the field surface — a test
asserts the site set **is** the field surface, because sampling from the cells the predicates already read
is the second of the two shared-denominator errors committed in one afternoon. A mutant that no cell value
distinguishes, counted as *unkilled* rather than discarded — must be caught by the observability filter's
own test. An undeclared suppression — every suppression is logged with its reason; an undeclared one is a
coverage lie and fails the build.

**Exit gate.** `K/O`, `U/G`, **`I/G`** and the per-fault-class vector reproduce on the real FME artifact
within the measured throughput envelope (baseline **7,946 mutants/s**, MEASURED, must not regress by more
than 2×). **The per-class vector's F11 row has `O > 0`** — an F11 row with `O = 0` fails this gate rather
than passing with a note (F19). The renderer refuses a bare percentage (criterion A9) and refuses `U/G`
without `I` (F18). `docs/measurements/P6-fault-model-v3.md` published.

**Kills if it fails.** If the observability filter cannot be founded (G-EVAL failed at P3), the phase ships
`K/G` labelled **reach, not quality**, and every downstream gate G2 threshold is restated against `G`
with the caveat printed beside it. Smaller, honest, still a rejector.

---

### P7 — THE FIVE GATES (MINUS G4), THE REGISTRY, ADMISSION · 16 days

**Settles.** Whether the rejector is real — the first five-gate attrition funnel over 280 harvested
predicates on the FME workbook. Today the gate has **exactly one demonstrated rejection** (five ALR bounds
asserting only `≥ −1e17` over 1,428 cells), and whether it rejects anything on the FME workbook is
**unmeasured**, because 19 of that workbook's 24 bounds are a real `≥ 0`.

**Entry.** P6 complete; the fault model at v3; the obligations table seeded.

**Builds.**
0. **The instrument text source, moved here from P12-B1** *(F35)*. `qualify/textsource.py` — two
   independent extractions of the pinned regulation, a normalised text with **stable character offsets**,
   a disputed-region exclusion rule with page numbers, and an `ExtractionManifest`. **G0's whole mechanism
   is `source_text.find(quote)` at an exact span; no build before P12-B1 created a text to hold spans**,
   five phases downstream of the only consumer. 1.5 days, and it is the D5 differential
   `plan/01-validation-methodology.md` §1.4 already requires.
1. **The obligations table.** `obligations.yaml` — hand-maintained, `ingest_source='hand'`
   (`OBL-nnn → {source, instrument_id, frbr_uri, eId, verbatim_quote, char_span}`), because **nothing of L1b
   is built and a day-one answer that depends on an unbuilt layer is not an answer**. It flips to
   `ingest_source='l1b'` when P13-B2 produces `eId`s, and the ids are preserved.
   **`source ∈ {STATUTE, TEMPLATE}` is new and is the F9 repair as arbitrated by C2** (see the note under
   build 2): a harvested predicate's obligation has `source: TEMPLATE`, its instrument is the **pinned
   blank** rendered as an addressable text by `qualify/template_instrument.py`, and its quote is the formula
   or validation text the harvester read. **A `TEMPLATE` obligation is a provenance chain to the regulator's
   artifact and is not a statutory grounding; the two counts are never added, and neither is ever published
   without the other.** *(`source` is the discriminator; `ingest_source` — `hand | l1b | harvest` — is the
   separate question of how the row got into the file. C2 needed the name `source` for the discriminator,
   so the provenance field was renamed rather than overloaded.)*
2. **G0 and G1.** **What G0 does with a clause-less harvested candidate was undefined, and P7's headline
   number depended on it (F9, FATAL).** All six G0 rejection reasons presuppose a clause; the 280 harvested
   FME candidates are derived from formulas and validations and carry `clause: None`. If G0 rejected them,
   **all 280 died at stage one and D-REJECT — the flagship demonstration that the gate is not decorative —
   was unreachable**; if it skipped them, stage one read `280 → 280`, *a gate reporting a pass it did not
   compute*. **DECIDED, then ARBITRATED (C2):** obligations carry a **`source: STATUTE | TEMPLATE`**
   discriminator; every candidate carries an obligation, a harvested one carrying
   `OBL-TEMPLATE-<sheet>-<ref>` with `source: TEMPLATE`, and **G0 runs over it for real** — it asks whether
   the predicate faithfully implements the relation it claims to implement — so `find(quote)` is meaningful
   **and falsifiable**: a candidate whose recorded construct is not in the pinned blank at the recorded
   offset is rejected, which is also the template-churn regression check. **Stage one of the funnel renders
   three integers — `entered / skipped / survived` — and `skipped` is never counted as a survivor**, and
   **BOTH obligation-coverage numbers are published together, never one alone**:
   `predicates_with_a_STATUTE_obligation / 280` = **`0 / 280`**, and
   `predicates_with_a_TEMPLATE_obligation / 280` = **`280 / 280`**. Guards:
   `test_g0__disposition_of_a_clauseless_candidate_is_specified_and_counted` (NC-Q48) and
   `test_p7__both_obligation_counts_render_or_neither_does`.
   `gates/g0.py` — the verbatim-quote provenance guard (`source.find(quote)` must succeed),
   the exact character span, and **every proviso, exception and cross-reference in that span either
   implemented as a branch or declared as a `NO_PREDICATE(no_predicate.not_yet_synthesised)` emission**
   carrying the proviso's verbatim text and span. Neither ⇒ REJECT.
   `gates/g1.py` — executes without error, every key exists in the induced schema, `cells_bound > 0`.
   Free, proves nothing alone, and **is precisely the condition whose absence produces the vacuous pass.**
3. **G3, both arms.** `g3_proof.py` — Z3: trivially-true iff `¬P` is UNSAT; always-flag iff `P` is UNSAT;
   redundant iff `P₁ ∧ ¬P₂` is UNSAT. Host functions are uninterpreted; **`unknown` is treated as
   *unproven*, never as *non-degenerate*.** `g3_empirical.py` — spurious firing on the 10% control sample
   below threshold; flags ≤ 50% of the clean corpus; hypergeometric random-flagger adjusted precision; not
   equivalent to a published degeneracy-list member.
   **Order is fixed and is a decision:** G0 → G1 → G3-proof → G2 → G3-empirical → G4. Nothing expensive
   runs behind something free, and a predicate Z3 proves unfalsifiable never consumes a mutation budget.
4. **The registry and admission.** `registry/store.py` (append-only; supersession is a new row),
   `merkle.py` (registry root over sorted `code_sha256`, leaf `sha256(0x00 ‖ h)`, internal
   `sha256(0x01 ‖ l ‖ r)`, odd node promoted — **domain separation is not decoration**),
   `ilp.py` (SPADE's ILP **reimplemented** in ~40 lines of PuLP/CBC with the interaction bound
   `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`; the SPADE repository is 17★, 1 fork, **no licence
   field** — reuse the algorithm, not the repository), `admit.py` (stores the **liveness witnesses**
   `kill_case` and `pass_case` with the predicate; **a human signs the batch**). Every rejection becomes a
   `rejection` row carrying the gate, the measured number, the cells it would have covered and the
   obligation it claimed — that row **is** `no_predicate.failed_qualification` and the report's
   `counterEvidence[]`.

**The number.** **The five-gate attrition funnel over the 280 harvested FME predicates** —
generated → G0 → G1 → G3-proof → G2 → G3-empirical survivors, each stage with its integer count and the
named reason for each rejection. Denominator: 280. Warrant **MEASURED**. Today one rejection exists, on a
different workbook, in one predicate class. **Stage one carries three integers, not one** (F9), and three
subordinate numbers ship beside the funnel and are not optional:
**`predicates_with_a_STATUTE_obligation / 280 = 0 / 280`** and
**`predicates_with_a_TEMPLATE_obligation / 280 = 280 / 280`**, which render together or not at all
(F9, arbitration **C2** — an unqualified single obligation count is wrong by 280 in one direction and
conceals the ungrounded state in the other); and, for every candidate
reaching G2, **`kr_claimed` and `kr_all_classes` side by side with the declared class set printed** (F1) —
*the gap between those two columns is the number a reviewer wants.*

**Negative control.** The five ALR `≥ −1e17` bounds over 1,428 cells — **must be REJECTED at G3**, and the
ALR settled fraction must recompute *downward*. A flag-everything predicate (`expr: false`) — must be
rejected at G3-empirical; SPADE's own paper records that selecting **all** generated candidates yields
100% coverage at 100% FFR. A predicate with a proviso in its span neither implemented nor declared — must
be rejected at G0, because gates 1–4 cannot see a silently dropped proviso (models ground spans well,
SpanFaith 0.77–0.79, and wire exception structure badly, Edge-F1 ≈ 0.22 over 2,290 provisions).
`test_unmeasured_predicate_rejected` — admitting a predicate whose error rate is unknown must **raise**,
and the test asserts the rejection.

**Exit gate.** The funnel is published with every rejection's gate and measured number, **with stage one's
three integers and both obligation-coverage numbers beside it — `0/280` STATUTE and `280/280` TEMPLATE,
together or not at all** (F9, C2). **FME's 19 real `≥ 0` bounds are admitted; ALR's five
degenerate bounds are refused.** The registry root is reproducible and the loader refuses a predicate with
no qualification row. Gate order is enforced by the pipeline's shape, not by a comment. **And G2's
denominator is the declared one** (F1): for every candidate reaching G2 the registry bar is computed over
`claims_fault_classes`, the claim's commit is a git-ancestor of the campaign's, no admitted predicate
claims a class with `O == 0`, and both ratios are stored and rendered.

**Kills if it fails.** If the gates reject nothing on the FME workbook, that is **a publishable
measurement, not a failure** — it means the harvest is clean on this artifact and the gate's demonstrated
work remains one workbook, one class, five predicates, and the surfaces say exactly that. If G3's proof arm
cannot be encoded (CEL→SMT-LIB mapping breaks on some class), Z3 is dropped, the empirical arm runs alone,
and the library loses the counterexample witness — the gate survives, the evidence weakens, and the
predicate library says which predicates carry a proof and which do not.

---

### P8 — THE CLEAN CORPUS, G4, FFR, SEVERITY TIERS · 9.5 engineer-days (+ 15–25 person-days, parallel lane)

**Settles.** Whether **any** predicate in this system is admissible at all — and what the settled fraction
is *after* the gate rather than before it. **That delta is the product.**

**Entry.** P7 complete for B2–B4. **B1 has no entry criteria and starts at day 0.**

**Builds.**
1. **The blind-fill corpus and its firewall** *(parallel lane, from day 0)*. `corpus/blindfill/` —
   ≥ 30 correctly-filled workbooks by **Person A**, who has never seen the predicate set, working from the
   template and the regulation alone. If the audited second-model-instance route is used instead, the
   **predicate-free fill prompt is hashed and published before the first workbook is filled**, and the
   record says the fallback is weaker than a human. Firewall: separate directory, separate reviewer, a
   contamination test that fails the build if any predicate id, CEL source or gate output appears in the
   corpus lane's inputs.
2. **The three corpus-free oracles.** `TEMPLATE-COMPUTED` — fill the inputs and let the workbook's own 505
   formula cells compute the rest, **ready today** — **but *which program executes those formulas* is now a
   recorded, gated choice, and this is the F2 repair (FATAL)**:

   > The corpus was generated by `src/cdfc/calc/`, and `src/cdfc/calc/` is what the arithmetic predicates
   > and `TEMPLATE_DIFF` re-check. **The oracle and the system under test were the same function.** The
   > false-failure rate of the 277 identity predicates on that corpus is zero *regardless of predicate
   > quality* — which is this plan's own definition of an uninformative rate — and because the generator is
   > deterministic from a seed, `n = 189` was one command, so **a `BLOCKING` severity tier could be bought
   > in an afternoon from a corpus the product generated about itself.** `synthesise` now takes
   > `derived_by ∈ {CALC, FOREIGN_ENGINE, NONE}` and records `computed_cells`; **`CALC` licenses an FFR
   > only for predicates that read no computed cell** (membership, bounds, dates, `conditional_required` —
   > the residual licence is real and is kept as a positive control); **`FOREIGN_ENGINE`** — a
   > digest-pinned offline engine sharing no module with `src/cdfc/`, exporting a value table that
   > raw-zip surgery writes back — licenses all classes, labelled with the engine digest; **`NONE`** is an
   > execution substrate only. Full mapping and enforcement: `plan/04-phases-qualification.md` P8-B2/B3.

   `REGISTER-DERIVED` (**MEASURED**: 228 of 228 live FMEs return a
   non-empty `RegistrationNumber` via the detail endpoint; and the worked example — the obvious regex
   `^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$` **fires on 87 of 228, a 38.2% false-failure rate**, which is
   why the admitted predicate is set membership against a snapshotted register under a declared
   normalisation, never a format grammar); cross-format.
3. **G4 and the interval statistics.** `gates/g4.py` — FFR on a corpus whose provenance ≠ `SELF-AUTHORED`,
   with `n`, a two-sided **Wilson** interval, **`clean_corpus_independent_of_predicate` — which is now
   `g4_ffr.independent()`'s COMPUTED result and no longer a declared boolean (F5: every admitted predicate
   carried `true`, and no build computed it, no test asserted it, no negative control broke it and no gate
   read it; it is the field that would have caught F2)** — a structurally
   distinct held-out slice reported separately, and the **marginal** FFR conditioned on the already-admitted
   set. `corpus/provenance.py` — the six values `SELF-AUTHORED · BLIND-FILLED · TEMPLATE-COMPUTED ·
   REGISTER-DERIVED · REAL-PARTNER · PUBLIC`. **`SELF-AUTHORED` renders as `—` and the word
   *uninformative*; the schema forbids a number.**
4. **Severity tiers, pre-registered.** `FFR Wilson **upper bound** ≤ 0.02 **and ≥ 30 non-synthetic
   filings** ⇒ BLOCKING · 0.02 < ≤ 0.10 ⇒ ADVISORY · > 0.10 ⇒ NOT ADMITTED`. **The second conjunct is new
   (F2/F12):** `BLOCKING_MIN_NON_SYNTHETIC = 30` filings whose provenance is `BLIND-FILLED`,
   `REAL-PARTNER` or `PUBLIC`, whatever the total `n` — because an interval is a statement about a sample,
   and a sample the product generates is unbounded in `n` at a cost of one command. **No synthetic corpus
   of any mode can reach `BLOCKING`.** The upper bound, never the point estimate: `0 fires / 4 filings` has
   a point estimate of 0.000 and an interval of `[0.000, 0.490]`, and a rule keyed on the point estimate
   would let a sample of four buy `BLOCKING`. **Consequence, stated so nobody is surprised: on day one
   almost nothing is BLOCKING** — a predicate needs roughly `n ≥ 185` clean non-self-authored filings with
   zero fires to clear 0.02 on the upper bound.

**The number.** **The first false-failure rate in this system measured on a corpus its authors did not
write**, as `(fired, n, wilson_lo, wilson_hi, corpus_id, corpus_provenance)` per predicate — and the
aggregate that follows: **the post-gate settled count against the pre-gate 2,373**, with the admitted count
by severity tier. Denominator: 3,747 cells / 280 predicates / `n` filings. Warrant **MEASURED**.
Today this number is **0 predicates admitted and a defensible settled fraction of 0%**, and the spec says
so on stage.

**Negative control.** A predicate whose only FFR is `SELF-AUTHORED` — must render `uninformative` and **no
digits** (criterion A4), and must not be admitted. `0 fires / 4 filings` — must **not** buy `BLOCKING`.
A corpus lane input containing a predicate id — the contamination test must fail the build. Two predicates
each individually inside a 25% FFR budget whose union exceeds it — the sub-additivity bound must catch it,
because **FFR is monotone non-decreasing under union and a registry that admits one at a time drifts
silently to a flag-everything product** (in two of SPADE's nine pipelines, sets whose every member met the
constraint reached composite FFR of 88% and 53%).

**Exit gate — this is gate G-CORPUS (§6), and it now has THREE named outcomes (F12).** `PASS` requires
**`n_non_synthetic ≥ 30`** — `BLIND-FILLED`, `REAL-PARTNER` or `PUBLIC`. **`RESTRICTED`** is `n ≥ 30` made
up of `TEMPLATE-COMPUTED` and/or `REGISTER-DERIVED` filings: admit only the classes those corpora license,
cap every tier at `ADVISORY`, and render the literal string `G-CORPUS: RESTRICTED` on every FFR-bearing
surface. `FAIL` is neither. **Naming the middle outcome is the repair**: `synthesise(..., n=30)` satisfied
the old threshold in one command, so *the gate whose entire purpose is to stop a self-authored FFR from
shipping was satisfiable without a single filing anyone outside this repository touched* — and its PASS
branch said *"the FFR-bearing surfaces ship"*. In every outcome: the fill instructions **and** the held-out
slice hashed and published **before** the first workbook was filled, the contamination test green **via the
corpus repo's own signed result** (F16), and every FFR rendering with its provenance, `n`, interval and
computed independence or the build fails.

**Kills if it fails.** **This is the gate whose failure the plan must survive, and it does.** If no
non-self-authored corpus can be produced: no predicate is admitted at G4; every FFR renders
`uninformative`; `severity_tier` is undefined; the report carries `settledFraction: null` with an explicit
statement that **the admissible predicate set is empty**. What still ships: the harvest, the verdict model,
the closure invariant, the Unchecked panel, the canaries, the residue set, `verify` and the attestation.
**Fallback branch, pre-decided — and it is now the named `G-CORPUS: RESTRICTED` outcome rather than an
unnamed fallback:** admit only the predicate classes the ready-today corpora can license —
membership/identity via `REGISTER-DERIVED`; **arithmetic via `TEMPLATE-COMPUTED` only in
`derived_by=FOREIGN_ENGINE` mode, never via the mode in which our own evaluator computed the cells the
predicate re-checks (F2)** — cap every tier at `ADVISORY`, and publish the restricted
admissible set with its narrow warrant stated narrowly (*every entity in the register is validly
registered, so a predicate asserting membership cannot have a true positive there*). Smaller, not stalled,
**and visible**.

---

### P9 — L6: DIFFERENTIAL AND INVARIANT PROBES · 14 days

**Settles.** Whether the growth story is real — and whether the one check nothing else in the design can
perform works on the real artifact.

**Entry.** B1 after P5 (evidence pull-forward, conflict 2). B2–B4 after P7.

**Builds.**
1. **`TEMPLATE_DIFF` — the formula-override differential** *(spike-eligible after P5)*.
   `probes/template_diff.py` — for every cell the blank template declares to be a formula, compare the
   filed value against the value obtained by evaluating the template's formula over the filed inputs.
   **This is the only thing in the design that detects a filer overwriting a formula cell with a literal**
   — a defect that leaves the filing perfectly self-consistent, because the inconsistency was deleted along
   with the formula. Its oracle is the published blank, so it needs no corpus. It is **predicate #1** and
   its `method` value is `TEMPLATE_DIFF`.
2. **The relation set — 25, authored by a human.** `probes/relations/` — 15 need the filing alone, 4 the
   filing plus the pinned blank, 3 two consecutive filings, 1 multiple instances, 2 are checker self-tests
   never reported to the filer. **No model.** Model-generated metamorphic relations score *"markedly low"*
   on novelty and recapitulate the textbook classes — which is exactly how an earlier version of this
   design arrived at five relations of which four false-alarm on a correct filing and the fifth is vacuous.
   Includes the **four-way funds-raised partition**: the workbook reports funds raised by investor
   category, by country, by accreditation status and via the Summary carry, and **enforces agreement
   between none of them** — Tables 4.2 and 4.3 contain zero formulas (MEASURED).
3. **The execution vehicle.** `probes/driver.py` over Hypothesis `RuleBasedStateMachine` — `@invariant` for
   *necessary* relations (⇒ FAIL) and in-rule assertions for *expected* (⇒ `INFORMATIONAL`), so the split
   is enforced by the library rather than by our convention. `max_examples = 50` (55% of mutations are
   found with a single input and 76% within the first 20; the input space is small and fixed). Every real
   defect pinned as an `@example`.
4. **Routing every relation through the five gates.** A relation is not self-validating: a violated
   relation means *the artifact is wrong* **or** *our relation is wrong*. Each carries a **degree map**
   (money = 1; counts, dates, ratios, categoricals = 0), a necessary/expected flag, and a
   **non-degeneracy precondition**.

**The number.** **The before/after settled-count delta attributable to each relation**, and the count of
relations that **moved nothing, reported as moving nothing**. Denominator: 25 relations / 3,747 cells.
Warrant **MEASURED**. The ceiling is stated in advance and must be published with the delta: this layer
moves **≈ 0 of the 7** properties that are not settleable from the artifact at all.

**Negative control.** An **all-zero filing** — every partition relation must return `OUT_OF_SCOPE` on its
non-degeneracy precondition, never `PASS`; without this an empty filing scores 100% through the L6 door.
A relation adding a Table 3.x quantity (direct-investment basis) to a Table 5.6 quantity (look-through
basis) — **cross-basis contamination**, invalid by the artifact's own notes, must be rejected at authoring
review with a named test. `test_unqualified_relation_cannot_settle_a_cell` — the B1 spike's output is a
demonstration, not an admission.

**Exit gate.** Each relation holds on the clean filing, is violated by a targeted mutant **on a corpus the
relation did not generate**, **and passes the five gates before it may settle a cell.** `TEMPLATE_DIFF`
detects a seeded F11 pair and fires on **zero clean filings whose derived cells `src/cdfc/calc/` did not
compute** — `derived_by ∈ {FOREIGN_ENGINE, NONE}` or blind-filled.

> **Why that clause changed (F2).** *"Fires on zero template-computed clean filings"* was `x == x`:
> `template_diff` recomputes the template's formula with P3's evaluator and the corpus's derived cells were
> written by P3's evaluator, so the criterion is green on an implementation that always returns `[]` **and**
> on one whose tolerance is 1,000×. One filing the product did not compute makes it non-vacuous.
> **And `TEMPLATE_DIFF` must additionally be admissible at G2** — see F19 under P6 build 3; before that
> repair the flagship relation was green here and unadmittable there, and nobody would have found out
> until P9-B4.

**Kills if it fails.** If the relations cannot be authored honestly — the failure mode that produced five
relations of which four false-alarm — **the layer is deleted and the settled fraction becomes a ceiling
rather than a growth curve.** That is a real loss and it is survivable; the harvest, gate, closure and
residue set are untouched. `TEMPLATE_DIFF` failing separately kills the design's flagship and the demo
loses its best moment; the rest stands.

---

### P10 — L6.5: RUN-TIME CANARIES AND THE RESIDUE SET · 10 engineer-days (+ 3–5 person-days adjudication)

**Settles.** Whether a verdict can be conditioned on a proof obtained from the artifact under test, **in
the same execution**, and withheld when that proof fails — and how large the provably-unkillable class is.

**Entry.** P6 (mutation machinery) and P7 (liveness witnesses stored at admission) complete.

**Builds.**
1. **The canary loop.** `selfcheck/canary.py` — for every admitted predicate, instantiate its stored
   `kill_case` against **this filing's cells, in the in-memory fact table** — never against the file, never
   re-serialising it — re-evaluate, and confirm it fires. Any survivor ⇒ `run_state = INVALID`,
   `error.canary_silent` / `invalid.canary_silent`, `settledFraction: null` (**not zero, not omitted —
   null**) and `verdict: null`. Cost: at the measured 7,946 mutants/s, 280 canaries ≈ **35 ms** against a
   ~30 ms baseline. *There is no reason not to.*
2. **The residue procedure.** `selfcheck/residue.py` — take the filing `F`; generate mutants under the
   versioned fault model; **adjudicate each INNOCUOUS or WRONG — the only human step**; run the full
   admitted predicate set and every admitted relation over every WRONG mutant;
   `RESIDUE := {WRONG mutants nothing rejects}`.
3. **The adjudication record.** Content-addressed, per mutant, so the residue is
   *reproducible given the published fault model **and** the published adjudication record* — both hashed.
   Saying "a third party can re-run it" without naming the adjudication record would repeat the error this
   whole specification exists to correct.
4. **The demonstrated survivor.** At least one exhibit: a coordinated misstatement propagated through all
   181 cross-sheet carries and all 35 SUM identities, which every admitted check passes. The Unchecked
   panel lists **exhibits, not reasons**.

**The number.** **`|RESIDUE|`** — the count of WRONG mutants no admitted predicate and no admitted relation
rejects — with its fault-model version, its adjudication-record hash, and each survivor's class of
falsehood. Denominator: the WRONG mutants generated. Warrant **MEASURED**. This is *the first quantitative
statement anyone has made about the limit of document-level verification for a regulated filing.*

**Negative control — CORRECTED, because this document asserted a mechanism `plan/05` had already
superseded (F25).** A predicate deliberately made unable to fire — **its `kill_case` neutered** — must
return `INVALID`, **name the dead predicates**, and show no settled fraction of any kind. **The renamed
sheet is a different control and asserts a different thing:** `plan/05` §0.5 proves that
`demo --break-parser` terminates at F3 with `invalid.template_unbound`, **five steps before the canary
loop**, so **a `template_unbound` run has no dead predicates to name** and the assertion *"dead predicates
named"* was unsatisfiable on that fixture. It is an **apparatus break**, and its control asserts `INVALID`
with `invalid.template_unbound` and `settledFraction: null` — *not* a named predicate list. The same
correction is owed to `plan/01-validation-methodology.md` §1.10's E2E table and §2.5 NC-C01a, in the same
commit, with a row in `docs/CATALOGUE-CORRECTIONS.md`; guard:
`test_plan__no_binding_document_asserts_a_superseded_mechanism`, which is one grep over that file's
superseded assertions. **A correction that does not propagate to the document CI reads is the plan's own
version-churn failure.** A canary that operates on the file rather than the in-memory fact table — must
fail `test_canary_never_touches_the_artifact`.

**Exit gate — this is gate G-LIVENESS (§6).** The deliberately-dead-predicate fixture produces `INVALID`
with the predicate named, `settledFraction: null` and `verdict: null`. `|RESIDUE| > 0` with at least one
survivor exhibited and hashed. `test_residue_not_inflatable` — adding 505 recompute predicates does not
shrink the residue.

**Kills if it fails.** If canaries cannot be demonstrated to catch a dead predicate, **the design's boldest
claim is false and L6.5 is deleted**: the report then carries no `livenessProof`, the attestation drops
that field, and the surfaces say plainly that the instrument's liveness on this document is not
demonstrated. The rest of the system is unaffected. If the residue comes back empty, that contradicts a
structural argument and means the fault model is too weak — **not** that the class is empty; the response is
to strengthen the fault model, and the report says the residue is `0` *under fault model v3* with the
operator list attached.

---

### P11 — L7: ATTESTATION, `verify`, BYTE IDENTITY · 10 days

**Settles.** Whether a third party on another machine re-derives the report byte-for-byte. *If it does not
reproduce, it does not ship.*

**Entry.** P10 complete (the attestation carries `livenessProof`); P8 complete for the FFR fields.

**Builds.**
1. **The statement and the envelope.** `attest/statement.py` — in-toto Statement v1,
   `subject[] = filing ⊕ template` (a verdict against template v3 is meaningless if the entity filed on
   v4), `predicateType: …/filing-settlement-attestation/v1`. **The top-level object of the predicate is
   `scope`. There is no `result`, no `status` and no `pass` field at any depth, and there never will be.**
   The four statement fields — bounded silence, purpose, `summaryIsNotSubstitute`, and the detection
   boundary — are **required by schema**, not template strings. `NONE ≠ NOASSERTION ≠ absent` enforced by
   the JSON Schema: `[]` means *we determined there are none*, `null` means *we make no claim*, an omitted
   field is a violation.
   `attest/dsse.py` — DSSE, local Ed25519, keyed mode, **`--tlog-upload=false` asserted in a test**.
   The **filer** signs; the vendor signs nothing and appears only as `assessor.id` with
   `thirdParty: false`.
2. **`verify`.** `attest/verify.py` — re-runs the pipeline pinned to `{template_sha256, filing_sha256,
   registry_root, register_snapshot_sha256, code_git_sha, evaluator_version, fault_model_version,
   tool_versions{python, lxml, openpyxl, celpy, z3}}` and asserts a byte-identical report.
   **`libreoffice` is deliberately absent from that list because it is not on the verdict path.**
   The four non-determinism sources are *removed*, not tolerated: the mutable register is pinned by
   snapshot hash and the host function never resolves live at verdict time; wall-clock time is an input
   recorded in the manifest and CEL binds no clock; iteration order is fixed by RFC 8785 and explicit sort
   keys; **there is no floating point.**
3. **The declared-lossy projections.** `attest/projections/` — OSCAL AR / POA&M and RO-Crate, each
   carrying a **mandatory `metadata.prop` flagging it as lossy and naming the URI of the normative
   artifact — in the file, not in a README.** Projection rule: `PASS → satisfied`; `FAIL → not-satisfied`;
   `INDETERMINATE / NOT_RUN / NO_PREDICATE →` an observation with our reason as a prop, **no finding**,
   plus an `exclude-controls[]` entry; `OUT_OF_SCOPE →` an `exclude-controls[]` entry only;
   **`INVALID` → not representable at all.**

**The number.** **The byte-identity result on a second machine** — bytes differing / bytes in the report,
target 0 — together with the count of non-determinism sources enumerated and the count removed.
Warrant **MEASURED**.

**Negative control.** A report with one byte changed — `verify` must fail and name the diff. An attestation
carrying a `status` field — `test_attestation_has_no_status_field` and the JSON Schema's
`additionalProperties: false` must reject it. A signing run with `--tlog-upload` unset — `test_no_tlog`
must fail the build. A `verify` run that re-calls the model instead of replaying the pinned facts — must
fail; **a model output is an input to the verdict, not a step of it.**

**Exit gate — this is gate G-REPRO (§6).** A third party clones the repo, runs `verify` on a different
machine, and gets a byte-identical re-derivation. The attestation validates against its JSON Schema with
`additionalProperties: false`. `test_no_libreoffice_online` green. **And no hashed object contains a
duration (F23):** `test_contract__no_duration_field_in_a_hashed_object` walks every dataclass reaching
`canonical_json` and asserts no field name matches `(elapsed|duration|_us|_ms|_ns|seconds)` and no value
derives from `perf_counter` / `monotonic` / `process_time`; `ci/no-clock-in-core.sh`'s pattern set is
extended to those three. **`CanaryRow.elapsed_us` was inside the canonicalised evidence, so G-REPRO could
never hold** — two runs, two microsecond counts, two digests, and `E2E-VERIFY` fails permanently on the
first green run of P11. Timings move to `reports/perf/<run_id>.jsonl`, **outside** the hashed payload and
outside `run.jsonl`, where `PERF-CANARY2` reads them. **The evidence of execution stays where it was:**
`witness_digest`, `observable`, `intersects_read_set`, `fired` and `canariesRun == len(rows)` are all
deterministic, so the dangerous repair — dropping `elapsed_us` and losing with it the proof that the canary
loop ran rather than replayed — is not the repair taken. Also `settledFraction` on an `INVALID` run is
**present and `null`** — one rule, stated once, against the three the plan carried (F24): the schema's
`if/then` requires the property and constrains it to `const: null`, guarded by
`test_contract__invalid_carries_a_null_not_an_absence`.

**Kills if it fails.** If byte identity cannot be achieved, the non-determinism is named and — if it cannot
be removed — **the attestation drops the byte-identity claim and carries a weaker field-level
re-derivation claim instead** (`the named fields are equal`), explicitly labelled as weaker on the report
surface. The programme's headline acceptance test is downgraded, published as downgraded, and the system
ships.

---

### P12 — THE SETTLING EXPERIMENT · 6 engineer-days (+ 4–6 person-days human stratification and adjudication) + ≈ $13 model

**Settles.** How large the model's role is. The deliverable is not *"L3 works"* but a number: **of `N`
model-proposed regulatory checks, `k` survived a five-gate admission test specified before the model ran.**
**`k = 0` is a result** — the first measurement anyone has of whether a frontier model can write a
regulator-grade executable check.

**Entry.** **All five gates exist and run (P7 + P8).** Running this experiment against four gates and a
placeholder measures a curation, not a model. See conflict 4.

**Builds.**
1. **The pre-registration and the decidability pilot (E2).** `experiments/E6/PREREGISTRATION.md`,
   committed, content-addressed, hash published **before the first API call**, nothing added afterwards:
   the sampling rule and PRNG seed; the stratum assignment for all ~30 obligations **by a named human,
   dated**; `|drawn|`; both prompts verbatim with hashes; model id, API date, `k`, temperature, Batch job
   id; `τ = 0.10`; the fault-model version and operator list; the code hashes of B0/B1/B2; the five gates
   and their order; the decision rule and its power table; the corpus provenance of every FFR that will be
   computed; a commitment to publish either way; and **the arguments that will not be accepted as grounds
   for changing the criterion.**
   The draw: enumerate every `shall` in the chapters of the *IFSCA (Fund Management) Regulations 2025 as
   amended to 30 January 2026* governing scheme operation, valuation and periodic reporting; order by
   (regulation number, sub-clause); seed the PRNG from the pre-registration file; draw without replacement.
   Stratum A = arithmetically closed; Stratum B = judgment-bearing or externally dependent. Draw until
   `|A| = 20`; cap Stratum B at 10.
2. **The three free baselines (E5), run BEFORE the model.** B0 the template's own **138** checkable
   relations (of 505 evaluated cells; 35 SUM identities + 3 COUNTIF tallies = 38 of 294 authored
   expressions); B1 **Daikon** over the clean corpus at `--conf_limit 0.99`, whose trivia output **doubles
   as the degeneracy list**; B2 the degenerate arm — *"no cell is blank and no cell errors"*, the analogue
   of the `NoException` baseline that found 68.9% of a published neural oracle's bugs at twice its
   precision. **The output is the bar.**
3. **The run.** `claude-opus-5`, Batch API, prompt caching on the schema prefix, offline, once. Two prompt
   regimes (correctness ≠ completeness: p = 0.008, Cohen's d = 1.73) and L4 arbitrates. ~30 obligations ×
   2 regimes × k = 10 = 600 candidates ≈ **$13 (MODELED)**, budget $25 with re-runs, **$26 more if the
   extension fires**. Feeding the induced schema in as an explicit I/O constraint is the dominant lever on
   *structural similarity* (+37–54 pp) in the only published study of statute→executable-model generation
   (arXiv:2604.17153) — **that study's outcome equivalence tops out at 51–53%**, and its own caveat is that
   structural similarity does not guarantee outcome equivalence.
4. **The decision record and the `k = 0` branch.** `experiments/E6/DECISION.md`, dated, published either
   way, containing: inputs, **every candidate including discards** (the discard pile is data and appears in
   the attrition funnel), the five-gate attrition funnel, the Wilson interval, the per-stratum split, the
   marginal kill over each baseline **separately**, `U/G`, and **both attrition numbers** — the experiment's
   bar (`K/O > 0` plus marginal kill) and the registry's bar (`K/O ≥ 0.80`), which are different tests.

**The number.** **`k of 20`** — Stratum A obligations for which at least one of 20 candidates passes all
five gates — with its Wilson interval, plus **`|A|/|drawn|`, the measured decidable fraction of the
instrument, which nobody has.** Warrant **MEASURED**. The 95% Wilson interval at `p̂ = 0.30, n = 20` is
`[0.145, 0.519]`; **the interval goes on the slide, the point estimate never.**

**Negative control.** A pre-registration hash published *after* the first model call — the
`test_preregistration_precedes_first_call` check must fail the build and the experiment is downgraded to
exploratory **and says so**. A candidate set selected by "take all" — must be shown to reproduce SPADE's
degenerate operating point (100% coverage, 100% FFR) and be refused. A criterion revision proposed *after*
seeing the result — the four named inadmissible arguments are hashed into the pre-registration and the
review rejects them mechanically.

**Exit gate — this is gate G-SETTLE (§6).** Retain L3 iff **≥ 6 of 20** survive all five gates **and** the
surviving set beats `B0 ∪ B1 ∪ B2` on marginal kill at equal FFR. Delete at **≤ 2 of 20**. A result of
**3–5** triggers exactly **one** pre-committed extension to `n = 40` at a threshold of **≥ 12**, and no
further extension ever. Exact binomial tails for `n = 20`: `P(X ≤ 5) = 0.933` at `p = 0.15` and `0.245` at
`p = 0.35`; `P(X ≤ 2) = 0.405` and `0.012`; **the extension zone fires more than half the time at
p = 0.15–0.25, so the n = 40 extension is the modal path and is budgeted as such.**

**Kills if it fails.** **L3, and only L3.** Predicates become hand-authored from the 294 native
expressions, the 20 resolving vocabularies and the statute. The gate, the coverage declaration, the closure
invariant, the canaries and the residue set are untouched. See P13's `k = 0` branch for exactly what still
ships.

---

### P13 — THE MODEL- AND CLAUSE-BEARING LAYERS, SIZED BY P12 · 16 days full · 4 days at `k = 0`

**Settles.** What L3, L1b, L2b and the instrument watcher look like at the size the settling experiment
licenses — **including the size zero.**

**Entry.** `experiments/E6/DECISION.md` exists and is dated. **CI fails the build if
`src/cdfc/model/propose.py` exists without it.** (Barrier 5.)

**Builds.**
0. **`test_no_model_in_verdict_path`, written first.** A static check that no import of the model client is
   reachable from L5/L6/L7, plus a run with the network namespace closed. **This is criterion A6 and it is
   the gate that turns a design property into a system property.** It is build zero of this phase because
   the phase is where a model first enters the codebase, and the guard must precede the thing it guards.
1. **L3 candidate proposal, at the licensed size** *(gated on G-SETTLE)*. `model/propose.py` — CEL
   envelopes only, never Python; the verbatim-quote provenance guard at the boundary; `schema_keys`
   machine-checked against the AST both ways; ~600 calls per template version, offline, Batch, cached
   prefix, **never in a request path**. Determinism: none, and it does not need any — a weaker model
   proposes more rejects and cannot smuggle an unqualified predicate past a gate that requires a measured
   kill rate and a measured FFR. **At `k = 0` this build does not exist and `model/` contains only the
   guard from B0 and the decision record.**
2. **L1b — the clause graph** *(optional, independently valuable)*. 389 native-text circulars → Docling;
   the 10 scanned → PaddleOCR-VL, run once offline and frozen; both into a **deterministic promoter**
   (numbered headings → `<section>`; `(1)/(a)/(i)` → nested `<paragraph>`; "Provided that" → `<proviso>`)
   → Akoma Ntoso with `eId` per clause and an FRBR URI per instrument (**grammar implemented ourselves,
   ~100 lines** — `cobalt`/`indigo` report NOASSERTION and `bluebell` is GPL-3.0 and must never be linked),
   plus the dated cross-reference extractor and the amendment graph. Recall is checked against a declared
   denominator: **8,866 `shall` occurrences across 361 circulars** — a promoter that loses `shall` clauses
   is losing obligations and the count is the regression test. On completion, `obligations.yaml` flips from
   `source='hand'` to `source='l1b'` with ids preserved.
3. **L2b — attachment extraction, and its feasibility gate.** `model/extract/` — provider-native structured
   output with `key` typed `Literal[*L1_KEYS]` **plus** the post-hoc deterministic key check (kept though
   redundant, **because this is the one you can prove to a reviewer**; whether provider-native constraint
   is guaranteed or best-effort is UNVERIFIED). **Retry is banned.** Skipped entirely when a filing has no
   attachment — the normal case, marginal model cost exactly $0.00. The conformal abstention layer is
   **gated**: measure the key-binding **base error rate `mu_base_error_rate`** on population P1, apply the
   forced-abstention floor `r ≥ (μ−α)/(1−α)`; **`μ > 0.30 ⇒ do not build it.`** The exchangeable unit is
   **the FILING**: report `n = F`, never `n = 3,755·F`.

   > **The field is renamed everywhere, and the rename is the repair (F26).** This document called `μ`
   > *"the key-binding **accuracy**"* while `plan/06-phases-model-and-clause.md` P13-B3 types it
   > *"a BASE ERROR RATE, not an accuracy — the floor formula only closes that way"*. Under the accuracy
   > reading the gate says *build the layer when accuracy ≤ 10%*, which is the opposite of the intent, and
   > **this document is the binding skeleton `ci/GATES.md` is transcribed from and where a reader who has
   > not opened `06` will look.** `06` is right. Guard: `test_contract__mu_is_an_error_rate` asserts
   > `decision == DO_NOT_BUILD` at `mu = 0.9` — which is 90% *accuracy* under the wrong reading and would
   > build.
4. **The instrument-stream watcher.** `model/watcher.py` — a daily content hash of IFSCA's circular list,
   Authority-meeting page and download page, diffed against the last snapshot. Any new instrument citing a
   regulation a predicate claims to implement moves that predicate to `PROVISIONAL` **automatically and
   pessimistically**; only a human clears it; **the watcher never re-admits**. A fetch failure is recorded
   as **a gap in the watch log with its duration**, never as "no change" — an unobserved day is not a quiet
   day. This is diff-and-flag, not NLP, and **it is the only mechanism that would have caught 24 July
   2026**, when the 29th IFSCA Authority Meeting let close-ended Restricted Schemes move NAV periodicity
   from semi-annual to annual with 75% investor approval by value — a fact the workbook does not collect.

**The number.** **Admitted predicates per 100 candidates, and per rupee, by model** — converting an
unanswerable question ("which model is better here?") into a measurement, because the gate adjudicates
every candidate deterministically, so **model choice affects yield, never correctness**. Plus
**`mu_base_error_rate`**, the key-binding **base error rate** on population P1 (**not** an accuracy — F26),
which decides whether the conformal layer exists. Warrant **MEASURED**.

**Negative control.** L3 source merged before the decision record exists — CI must fail. A model call
reachable from L5/L6/L7 — `test_no_model_in_verdict_path` must fail. A retry enabled in L2b — must fail;
silent retry manufactures exactly the clean verdict this product refuses. A watcher fetch failure logged as
"no change" — must fail. A promoter run that loses `shall` clauses against the 8,866 denominator — must
fail.

**Exit gate.** `test_no_model_in_verdict_path` green (criterion A6). If L3 is retained, every proposed
predicate carries `proposer{model_id, date, prompt_sha256}` so that a re-synthesis under a drifted model is
**a diff, not a mystery** (risk R19: a failure cell moved from 96.6% to 100% on the same prompt and harness
under the same alias, with no version bump). If L3 is deleted, `experiments/E6/DECISION.md` is published,
the attrition funnel is on the predicate-library screen, and `model/propose.py` does not exist.

**Kills if it fails.** Nothing above it. **The `k = 0` system, named explicitly so it is not a surprise:**
harvest (280 FME / 515 across nine, no model) + hand-authored predicates from the 294 native expressions
and the statute + all five gates + closure + canaries + residue + probes + attestation + `verify` +
surfaces. What is lost is the *scaling* story for new instruments; what is gained is the first published
attrition funnel showing exactly where the candidates died. **That is a funded, publishable outcome and
this plan is written for it.**

---

### P14 — THE SURFACES: REPORT, SCREENS, API, COPY GATES · 12 days

**Settles.** Whether the no-green-tick commitment survives contact with a rendering surface, an API
integration and an intern.

**Entry.** B1–B3 after P5. **B4 hard-gated on P8 (G-CORPUS).**

**Builds.**
1. **The report — one self-contained HTML file.** `surface/render.py` + `templates/` — inline CSS and JS,
   **no external requests**, server-generated. It opens from `file://` with the wifi down, is phone-safe
   with no build target, is emailable, and **decisively it is the attested artifact: a file has a hash, a
   single-page app does not.** The hero is **two counts of equal weight, same type size, same ink, no
   colour on either**: `<F> failures across <S> checks` and `<U> fields were not checked`. Label registry
   fixes the binding so it cannot drift: `<F>` = failing cells; `<S>` = settled cells; `<U>` = unsettled
   cells. **The predicate count belongs to the strap line and never to the hero.** A fixed-height stacked
   band labelled by absolute count, with the unchecked segment **hatched, not muted** — muted reads as
   "resolved, minor"; hatched reads as "not filled in", which is the truth. **The band never fills.**
   Nothing renders green; passing checks take body-text ink; only failures take colour — *the absence of
   colour is not the presence of green.* When the run is `INVALID` the whole screen is replaced by the
   reason, the dead predicates, and no settled fraction of any kind.
2. **The Unchecked panel.** Not an appendix — it sits on the report screen, above the fold, **and it is the
   differentiator.** Grouped by reason code with counts, and per entry **"what would make this checkable"**,
   specific rather than generic. Beneath the reasons: **demonstrated survivors from P10 — exhibits, not
   reasons.**
3. **The drop screen and the API.** One control, no settings, no account. `surface/api.py` — FastAPI,
   `/v1`, ~18 paths, synchronous request/response (**no queue, no broker, no workers** — the deterministic
   core is ~30 ms and the whole 19,782-mutant campaign is 2.5 s). **Two prohibitions enforced by schema and
   by test:** no endpoint returns a boolean pass/fail, a `status: "clean"`, or a bare settled fraction —
   every figure comes inside the object of spec §III.4.3 with all six counts; and `ffr` renders as `null`
   with `g4_corpus_provenance: "SELF-AUTHORED"`.
4. **The FFR-bearing surfaces** *(gated on G-CORPUS, and rendering its outcome — `PASS` or
   `RESTRICTED` — as a literal string)*. The **predicate library** — every admitted check,
   filterable, a plain `<table>`, ≤ 515 rows, with `KR = K/O` **rendered as two columns side by side,
   `kr_claimed` over the predicate's declared fault classes and `kr_all_classes` over all fourteen (F1) —
   the gap between them is the number a reviewer wants** — both integers **and** the per-fault-class
   vector **and `I`, the mutants our own evaluator could not adjudicate (F18)**,
   the degeneracy verdict with its Z3 witness, FFR with corpus provenance / `n` / Wilson interval /
   `derived_by` /`n_non_synthetic`,
   severity tier, liveness witnesses, **and beside each rule what a flag-everything rule would have
   scored.** Two tabs the category does not have: **Rejected**, and **the five-gate attrition funnel** per
   obligation. And **settled fraction over time**, rendering from a static JSON log, **which must be able
   to step down**, every step-down labelled with its cause.

**The number.** **The count of user-facing surfaces that pass all four surface gates** — the no-all-clear
grep, the FFR-provenance render test, the admission-state test (A11: no settled count renders without the
admission state of the predicate set that produced it), and the equal-weight-hero audit — denominator: the
total number of rendering surfaces enumerated in `surface/labels.py`. Warrant **MEASURED**. This is an
audit, not an assertion: the equal-type-size property is checked by rendering and measuring, not by reading
the stylesheet.

> **The denominator is a registry this build writes, so it is pinned like one (F11, adversary test 10).**
> `surfaces_passing_all_four_gates == len(SURFACES)` has no floor: **a surface that cannot pass SG1–SG4 can
> be removed from `SURFACES` to make the gate green**, and NC-A10 catches a surface that renders through a
> known path, not one deleted from the register. **`SURFACES` is append-only with a growth log, exactly
> like `catalogue.yaml`** (P0 build 3); removing a row requires a dated argument in
> `docs/measurements/P14-surface-audit.md`; `test_surface__registry_is_append_only` fails the build
> otherwise; and the measurement **publishes `|SURFACES|` as a time series**, so a registry that shrinks
> the day before a gate is read is visible.

**Negative control.** A surface rendering a bare settled fraction without the six counts — must fail. A
settled count rendered without `PRE-GATE` when the producing set is unqualified — must fail (A11, the
mechanised form of the demo's strongest moment). A `SELF-AUTHORED` predicate rendered — output must contain
`uninformative` and **no digits** (A4). Any of the banned strings —
`✓ ✔ ✅ 🟢 / all clear / no issues / looks good / verified clean / compliant / passed all / fully checked` —
**in every root named by `surface/labels.py::SCAN_ROOTS`** must fail `ci/no-green-tick.sh`.

> **The scan set has one source of truth, and it is not a literal (F28).** `plan/01` §5.4 gives the gate
> `src/ templates/ locales/ static/`; **P0-B1 creates none of the last three** (the tree is `src/cdfc/**`
> with `src/cdfc/surface/templates/`), and `plan/02` §1 R5 makes *a missing scan root a non-zero exit* — so
> the gate fails from the first commit and gets "fixed" by narrowing the set, **which is NC-D01's mechanism
> applied to the honesty gate itself, on day one, in the phase that exists to prevent it.** `SCAN_ROOTS`
> is a stub containing `("src/cdfc",)` at P0 and is **extended** by P14; `ci/no-green-tick.sh` reads it;
> `test_nc__CI01c_scan_root_list_is_not_a_literal` asserts the script contains no directory literal; and
> the narrowing from `01` §5.4's four names to the real tree is recorded in `ci/GATES.md` with a reason.
> **A scan set that shrinks silently is the defect; a scan set that shrinks with a diff is housekeeping.**

**Exit gate.** The report opens from `file://` with networking off and renders every number (A10). 280 rows
render in under 200 ms with no virtualisation library. All four surface gates green on every enumerated
surface. The verdict state name is `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` at its best — **there is no
state whose name means "clean"**, and the no-green-tick commitment is delivered *by naming*, which travels
with the claim in a way an icon does not.

**Kills if it fails.** A surface that cannot be made to obey the gates is **removed**, not excepted. If the
report cannot be made self-contained, the attestation loses its subject and the product loses its
emailable artifact — the fallback is a signed JSON with a printable projection, weaker and still shippable.
`K` and `T` in `pervasiveness-policy-v1.json` render the literal string `PLACEHOLDER` in every example and
every screen **until an argument for the numbers exists**; this is an open item (spec §III.7 C22) and it
does not block the phase.

---

### P15 — TRANSFER (COST ARM), VERSION CHURN, OPERATIONS, DEPLOYMENT · 10 days

**Settles.** Whether this is a **product** or a **paper about one workbook** — and whether the settled
fraction actually falls when the world moves.

**Entry.** P7 (re-qualification machinery), P8 (cost is measured over qualification), P14-B4.

**Builds.**
1. **The transfer measurement, cost arm (E4 arm 2).** Take a second prescribed workbook; measure, on a
   stopwatch, the human minutes to carry ≥ 10 predicates across — key re-resolution, clause re-binding,
   re-qualification — against the human minutes to author an equivalent predicate from scratch. Publish
   **per-template settled fractions including the zero cases**, and never average them: the settled
   fraction is a **per-template property**.
2. **Version churn and re-qualification.** The seven rules V1–V7 as code: label-anchored keys so a version
   bump is a **re-resolution, not a rewrite**; `qualified_against` as part of the predicate's **identity**;
   any change moves the predicate to `PROVISIONAL` — **it still runs, so detection is not lost**, but its
   numbers are hidden and **it does not count in the settled numerator**; liveness witnesses replayed and a
   predicate whose `kill_case` stops dying **quarantined automatically**; `withdrawn_on` /
   `withdrawn_reason` on every predicate. **Therefore the settled fraction falls when the template
   changes. That is correct** — a system whose coverage silently persists across a version boundary is
   lying, and the step-downs are the most credible thing on the chart.
3. **Register snapshot policy and operations.** Content-addressed snapshot; the fetch plan quoted in its
   **form** — `1 list request + N detail requests, N = |records|` — and **never as an integer** until a
   re-fetch records one in the manifest (the drafts' 2,235 is withdrawn to UNRECONCILED). A staleness bound
   past which the host function degrades to `NOT_RUN(not_run.input_unavailable.register)`. **IFSCA's terms
   of use for the register API must be read before any scheduled polling — a gap in conduct, not in code,
   and it is open.** Observability: the run manifest, content addressing end to end, `run.jsonl`, and
   `verify`. No OpenTelemetry; at sub-second and single-node, tracing would be theatre.
4. **Deployment.** One Docker container, `shared-cpu-1x` / 512 MB, ≈ $3.32/month. **The laptop is the demo
   path and is mandatory as the fallback.** `make demo` runs `ingest → induce → harvest → run` offline
   after the fetch. Storage ~3.4 GB/yr. What breaks first at 100× scale, in order: blob storage
   (→ object storage on the identical `sha256` path, the scheme unchanged, **which is the point of choosing
   it**); SQLite's single writer, triggered by **concurrent uploads, not row count** (→ Postgres, **losing
   content-addressability, so the manifest must then name a logical snapshot id instead of a file hash**);
   the register snapshot; and **the qualification corpus, which is the real one — it does not scale with
   filings at all, it scales with templates.**

**The number.** **Human minutes per transferred predicate on a second workbook**, against the from-scratch
authoring baseline, denominator ≥ 10 predicates. Warrant **MEASURED**. Plus the **per-template settled
fraction table for all nine**, including the zeroes (`EDR_1` has zero formulas;
`IFSCA_Annual_Reporting_Format` has zero formulas *and* zero validations, so its mechanically derivable
settled fraction is 0% — **publish it anyway**).

**Negative control.** A template hash bump that does **not** move affected predicates to `PROVISIONAL`, or
that does not make the settled fraction fall — must fail (criterion A8). A watcher fetch failure recorded
as "no change" instead of a gap with its duration — must fail. A settled fraction averaged across templates
— must fail. A register host function that resolves **live** at verdict time — must fail `verify`.

**Exit gate — this is gate G-TRANSFER, cost arm (§6).** Human cost per transferred predicate is at most
**0.5×** the median from-scratch authoring time, measured over ≥ 10 predicates on a second workbook.
Bumping the template hash demonstrably makes the settled count decrease. A deployed report re-derives
byte-identically from a clean clone.

**Kills if it fails.** If transfer is not materially cheaper than authoring, **the product claim narrows
from "a method for prescribed regulatory returns" to "an instrument for the FME quarterly return"** — the
negative result is published, `P15-B1` becomes the paper's central table, and the multi-template surfaces
are dropped. The research contribution — the gate, the coverage declaration, the residue set — is
unaffected. **Smaller, not stalled.**

---

## 6. THE PHASE GATES

A gate is a **pre-registered boolean with a named threshold and a named failure branch**. Every failure
branch produces a *smaller system that still ships*. No gate in this plan produces a stall.

| Gate | Phase | Pre-registered threshold | PASS branch | FAIL branch — the smaller system |
|---|---|---|---|---|
| **G-READERS** | P1 | Readers A and B agree on `{n_sheets, sheet_names, hidden_sheets}` for **9 of 9** workbooks | Full corpus | The disagreeing workbook is **excluded with a stated reason** and its field surface is `null`. Corpus shrinks; plan continues |
| **G-READERS-B** *(new — F10)* | P1 | **For each of the four `A`/`A′`-only fields — `n_cells`, `n_formula_cells`, `n_validations`, `n_defined_names` — A and A′ agree on 9 of 9, AND `test_nc__P09_mutating_A_moves_only_A` is green *for that field's extraction path*, not only for the validation walk** | The dual-reader claim carries information for the four fields the project's founding defect actually lives in | Those fields are marked on that workbook and every predicate reading them returns `NOT_RUN(not_run.extractor_disagreement)` — the same branch P1 already specifies |
| | | **Why the floor was not enough:** G-READERS gates exactly the three fields where `COMPETENCE` admits all three instruments and where `plan/02` §0.2 N3 has *already measured agreement*. The four fields where a disagreement is **known to exist** are the four from which openpyxl has been declared incompetent, so the FAIL branch had no realistic path to firing. **A gate with a near-certain pass produces no information**, and P1's exit gate spent a criterion on it | | |
| **G-DENOM** | P2 | The field surface is computed by two independent code paths and they agree, per workbook | Denominator published | That workbook has **no settled fraction, ever** — `settledFraction: null`, `denominator.source` states why. Published as such |
| **G-EVAL** | P3 | **Arm 1:** our evaluator reproduces **505 of 505** cached values exactly, incl. `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101`. **Arm 2 (F3): 100% against the human-authored expectation file AND at most `d = 11` non-trivial-cell disagreements against the digest-pinned offline engine, `d` a frozen integer pre-registered in `experiments/G-EVAL/PREREGISTRATION.md` before the first run (C1)** | Observability filter is founded; `K/O` is quotable — **and if the expectation file's author is `calc/`'s author, the gate is recorded `PASSED — NOT INDEPENDENT` and `SAME-AUTHOR — a weaker instrument` renders beside every kill rate** | ≤ 25 failures (5%): those cells are excluded from the site set and flagged `INDETERMINATE(engine_disagreement)` from a pinned table. **> 25, or > `d` engine disagreements: G2 is downgraded to a *reach* measurement reported as `K/G` and labelled as such.** `TEMPLATE_DIFF` is deleted |
| | | **Why arm 2 needed a failing condition:** disagreements against the offline engine were *published, never silently resolved* — and **published is not a gate.** The engine is the only independent instrument in the pair, so a build disagreeing with it on every non-trivial cell passed arm 2 provided it agreed with an expectation file the evaluator's own author wrote. *A published disagreement that changes nothing is a log line* | | |
| **G-CELPY** | P4 | The official CEL conformance suite passes on the admitted subset, **specifically on error semantics for `&&`/`\|\|`** | `celpy` pinned; registry root qualified against it | Switch to `cel-expr-python` (accept a C++ build). If **neither** passes on error semantics, **narrow the admitted subset to ban `&&`/`\|\|` at the top level of `expr`** — smaller grammar, same guarantee |
| **G-TRANSFER (mech)** | P4-B4 | The harvest produces a non-empty predicate set on **≥ 5 of 9** workbooks | The method is not workbook-specific | The claim narrows to the workbooks where it works; the per-workbook distribution is published including the zeroes |
| **G-CORPUS** | P8 | **THREE OUTCOMES (F12). `PASS`: `n_non_synthetic ≥ 30` — `BLIND-FILLED`, `REAL-PARTNER` or `PUBLIC`. `RESTRICTED`: `n ≥ 30` but made of `TEMPLATE-COMPUTED` / `REGISTER-DERIVED` filings. `FAIL`: neither.** In all three: fill instructions **and** held-out slice hashed and published **before** the first workbook was filled, proven from the corpus repo's commit graph; contamination test green via the corpus repo's own **signed** result (F16); every FFR carrying provenance, `n`, interval and **computed** independence (F2/F5) | **`PASS`** — G4 runs unrestricted; predicates are admitted; `BLOCKING` is reachable; the FFR-bearing surfaces ship. **`RESTRICTED`** — admit only the classes those corpora license, **every tier capped at `ADVISORY`**, and the literal string `G-CORPUS: RESTRICTED` renders on every FFR-bearing surface | **No predicate is admitted. Every FFR renders `uninformative`. `severity_tier` is undefined. `settledFraction: null` with "the admissible predicate set is empty". Ships** |
| | | **Why the old threshold was satisfiable by the thing it existed to stop:** `n ≥ 30` accepted `TEMPLATE-COMPUTED`, and `synthesise(..., n=30)` is one command over a corpus the product generated about itself — so *the gate whose entire purpose is to stop a self-authored FFR from shipping needed no filing anyone outside this repository touched*, and its PASS branch said "the FFR-bearing surfaces ship". The old fallback was written into the FAIL branch, where **shipping it was an undetected pass** | | |
| **G-LIVENESS** | P10 | The deliberately-dead-predicate fixture produces `INVALID`, names the dead predicates, and shows **no settled fraction of any kind** | `livenessProof` ships in the attestation | **L6.5 is deleted.** The report carries no `livenessProof`, the attestation drops the field, and the surfaces say plainly that instrument liveness on this document is not demonstrated |
| **G-REPRO** | P11 | A third party on a different machine gets a **byte-identical** re-derivation | The programme's acceptance test passes | Name the non-determinism. If it cannot be removed, the attestation drops byte-identity for a **field-level re-derivation claim**, labelled weaker on the surface |
| **G-SETTLE** | P12 | **≥ 6 of 20** Stratum-A obligations survive all five gates **and `beats_baselines` is TRUE, where that term is now arithmetic and not prose (F30):** `beats_baselines := all(m.killed_by_candidate_only > 0 and m.comparable for m in per_baseline) and union_row.killed_by_candidate_only ≥ ceil(0.10 * union_row.observable)` — evaluated over the same `SiteSet`, at equal FFR. **≤ 2 ⇒ delete.** **3–5 ⇒ exactly one extension to n = 40 at ≥ 12, never again** | L3 is built at the licensed size | **L3 is deleted and only L3.** Predicates become hand-authored from the 294 native expressions, the 20 resolving vocabularies and the statute. `k = 0` is published on the date it is taken |
| | | **Why the arithmetic had to be written down:** *"marginal kill strictly greater than B0"* compares a **count** (`\|K_c \ K_b\|`) to *what* — zero, the baseline's own kill, or the baseline's marginal over the candidate? **Three readings, three different gates**, and the loosest (`> 0`) is true for any predicate that kills anything B2 does not, which is most of them. **A criterion that must be interpreted after the result is not a criterion**, and this one sits inside the artifact whose entire epistemic value is that it was specified, locked and hashed *before* the model ran. The floor is a number and it is `0.10`; guards: `test_decide__beats_baselines_is_arithmetic_not_prose` (exhaustive over the `MarginalKill` tuple space) and `test_contract__preregistration_criterion_is_machine_evaluable` (the lock refuses a criterion `decide()` cannot consume) | | |
| **G-CONFORMAL** | P13-B3 | **Key-binding BASE ERROR RATE `mu_base_error_rate ≤ 0.30`** — an error rate, **never an accuracy** (F26; the field is renamed everywhere and `test_contract__mu_is_an_error_rate` asserts `DO_NOT_BUILD` at `mu = 0.9`, which is 90% *accuracy* under the wrong reading and would build); at `α = 0.05` the forced-abstention floor `(μ−α)/(1−α)` already exceeds 26.3% at `μ = 0.30` | `μ ≤ 0.10` ⇒ build. `0.10 < μ ≤ 0.30` ⇒ build and **ship the abstention rate as the headline** | **Do not build the conformal layer.** The honest product is *"cross-document binding is unchecked"*. Largely pre-settled: **0 of 3,755** unlocked cells are ambiguous under the address key |
| **G-TRANSFER (cost)** | P15 | Human minutes per transferred predicate **≤ 0.5×** the median from-scratch authoring time, over ≥ 10 predicates on a second workbook | The product claim stands | The claim narrows to **"an instrument for the FME quarterly return"**; the negative result becomes the paper's central table; multi-template surfaces are dropped |

**Two gating rules stated separately because the task names them.**

1. **Nothing of L3 is built until the settling experiment runs.** Enforced at build level: the presence of
   `src/cdfc/model/propose.py` without `experiments/E6/DECISION.md` fails CI. This is barrier 5.
2. **The FFR-bearing surfaces cannot ship before a blind-filled corpus exists** — **and under
   `G-CORPUS: RESTRICTED` they ship carrying that literal string, with every tier capped at `ADVISORY` and
   with no arithmetic FFR drawn from a corpus our own evaluator computed** (F2/F12). Enforced by G-CORPUS at
   P8 and by the P14-B4 entry criterion. `test_ffr_provenance` fails the build if any FFR renders without
   its corpus provenance, its `n` and its interval; `0 fires / 340 self-authored` and `0 fires / 4 real`
   must not be allowed to look alike — the Wilson intervals are `[0.000, 0.011]` and `[0.000, 0.490]`.

**Two open items that are not gates and must not become blockers.** `K` and `T` in
`pervasiveness-policy-v1.json` have **no argued basis anywhere in the corpus** and render the literal
string `PLACEHOLDER` until one exists (spec §II.3.7). And the legal review of the filer-signs decision is a
residual item on a decision already taken (spec §III.7 C21) — until it returns, the demo signs a synthetic
filing with a demo key and **says so out loud**.

---

## 7. THE CRITICAL PATH

**Named: THE QUALIFICATION SPINE.**

```
P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P12 → P13
 8    8    10   17   14   12  10.5  16   9.5    6     16    =  127 working days
```

**Effort assumption.** One competent engineer: fluent in Python, comfortable with raw OOXML and with SMT,
working from this specification, ~6 productive hours a day, no context switching. **Human-latency items are
counted separately, in person-days of a different person, and are never added to the engineer's total:**
the blind-fill corpus (15–25 person-days, P8-B1), INNOCUOUS/WRONG adjudication (3–5, P10), stratum
assignment and candidate review (4–6, P12).

> **THE STAFFING MODEL, STATED ONCE, BECAUSE THE TWO NUMBERS BELOW CANNOT BOTH COME FROM THE SAME ONE
> (F43). DECIDED.** This plan is written for **one engineer**, and **174 days is the honest number**. The
> parallelised figure is what 2–3 engineers could reach *if the estimates carried coordination, review and
> integration cost, and they do not* — it is quoted as a ceiling, never as a plan. *Alternative it beat:*
> re-estimating everything for a team, which would replace measured single-author estimates with modelled
> team ones and lose the only calibration the plan has.
>
> **The consequence that matters is not the schedule; it is the evidence.** Every independence claim in
> this plan requires a second *author*, and no budget contains one: `reader_lxml_b.py` (A′),
> `styles_mask_b.py` (path B), **G-EVAL arm 2's expectation file**, and the second signature on
> `docs/RELATION-REVIEW.md`. NC-D02d and NC-P09 prove *two code paths*; `plan/01` §7.5 admits they cannot
> prove *two minds*. **Under the one-engineer model every differential in this plan is a same-author
> differential and must render `SAME-AUTHOR` on the surface that quotes it** — G-EVAL's arm-2 test makes
> that unavoidable rather than optional. **OPEN — USER DECISION:** *fund a second author for the three
> places where a second person buys evidence rather than throughput — A′, mask path B, and the arm-2
> expectation file (≈ 1.5–2 person-days each)?* It blocks no phase; it decides whether the word
> `SAME-AUTHOR` ships beside the kill rates.

| Total | Days | Meaning |
|---|---|---|
| **Serial total, one engineer, everything built** | **174** | The sum of all sixteen phases (was 170; +2 P7, +0.5 P6, +1.5 P8 from the adversary repairs, of which 1.5 is P12-B1 work relocated to P7-B0 and not new). **This is the honest number for a solo build** |
| **Critical path, off-path phases parallelised** | **118** | The longest chain of dependent phases. **Requires ~2–3 engineers to realise, and the estimates do not contain their coordination cost** — see the staffing note above |
| **Critical path if `k = 0`** | **~118, not ~104** (F34) | P13 collapses to 4 days and the path re-routes through `P0→…→P7→P9→P10→P11` — **because P10-B2 needs P9-B4's admitted relations**. `P7 ends 86 → P9 ends 100 → P10 ends ~106 → P11 ends ~116`, tied with the spine. **The old ~104 was wrong by ten days in exactly the branch `plan/06` says the plan is written for**, and a schedule that is wrong in the failure branch is wrong where it will be read under pressure |
| **Corpus lane, for the GATE** | **15–25 person-days** for 30 workbooks, starting day 0 | Not on the engineering critical path *provided it starts at day 0*. **It becomes the critical path the moment it is deferred past day ~70** |
| **Corpus lane, for the SEVERITY AXIS** | **95–160 person-days** for 189 workbooks (F37) | **`ADVISORY` needs 30; `BLOCKING` needs 189 clean non-self-authored filings at zero fires** (`hi(0,189) = 0.019920`). At the measured fill rate that is four to seven months of one person — **the real critical path of the *product*, as opposed to the *paper*.** The plan budgeted the gate's number and then called that budget the programme's longest pole. **DECIDED default: build 30, ship `ADVISORY`-capped, and print `BLOCKING: 0 — requires 30 non-synthetic filings at hi ≤ 0.02` rather than an unexplained zero.** The funding question is `plan/04` §5 O5, and it is the user's |

**Off-path finish times** (earliest start under the graph in §4, recomputed with the `P9-B4 → P10-B2` edge
and with P6/P7/P8 at their repaired lengths): P14-B1–B3 ends ~day 69 · **P9 ends ~100** · **P10-B1 ends
~90, P10-B2–B4 end ~106** · **P11 ends ~116** · P14-B4 ends ~97 · P15 ends ~107. All are at or under 118 —
but **P11 is now within two days of the spine, and in the `k = 0` branch it *is* the spine.** The claim
that the attestation lane has ten days of slack is withdrawn.

**The one thing that most often turns this plan into a 200-day plan** is deferring P8-B1. It has no code
dependency, it is the only input no amount of engineering substitutes for, and the spec says so plainly:
*the expensive input is not inference — it is the human-built blind-filled corpus.*

---

## 8. WHAT IS EXPLICITLY NOT IN THIS PLAN

### 8.1 Carried forward from the specification's do-not-build list

Ranked, as there, by how likely each is to be built anyway.

| Not built | Reason, in one line |
|---|---|
| An agent loop, cross-step memory, or retry-until-it-passes | `pass^k` decay; `0.9⁸ = 0.4305`. The model appears exactly twice in this design and both are offline |
| A green tick, an "all clear", or a PASS summary badge | Mechanised twice: a build-time grep **and** a schema with no `result`/`status`/`pass` at any depth |
| A settled-fraction percentage as the hero number | 71% → 98.8% in one afternoon under a different enumeration of the same file. **100% must be structurally unreachable** |
| A denominator derived from the predicate set | Committed twice in one afternoon by the person hunting for it; the first coverage figure produced in this research was 99.2% and circular |
| `openpyxl` anywhere in the schema-induction path | 35 of 54 validations; AML-CFT blanked; round-trip destroys 3,663,391 → 65,877 bytes. Convenience reads and mutant writing only |
| `mutmut` / PIT / Stryker as the seeded-defect harness | Category error. They **are** right one level up — mutating our own code, which is rule R2 |
| A model as judge anywhere in the verdict path | LLM judges detect false success at AUROC ≤ 0.65, 13% recall at a 10% flag rate |
| A NAV recomputation engine, or NAV-per-unit in any data model | Whole-word `NAV` occurs **0 times** across all nine workbooks, positive controls passing. You cannot check a NAV that is not there |
| A valuation-error materiality regime as the pitch | You cannot ship a policy. The Luxembourg 1.72% may never be imported as an FFR prior |
| The brief's five metamorphic relations | Four false-alarm on a correct filing; the fifth is vacuous. **Do not restore.** Differential probes over the workbook-as-program instead |
| The supervisor as a user or a buyer | The supervisory seat is procured (NEC, 27 Jan 2026). Say **a downstream reviewer** |
| A queue, Redis, Celery, a worker pool | The job is ~30 ms; the whole mutation campaign is 2.5 s |
| Postgres, an ORM, migrations | **SQLite is a file, so it can be hashed and named in the run manifest.** A Postgres cluster cannot be content-addressed |
| React, Next.js, any component library | The deliverable is a *file*. It survives the venue, renders on a phone, is emailable, and can be hashed and signed |
| Auth, multi-tenancy, user accounts | Each adds a failure mode to a system whose demo must run offline from a file |
| Rebuilding Great Expectations / pandera / Soda Core / dbt / Deequ | Do not rebuild the check **library**; you **must** build the **verdict model**, because none of them has a third value |
| A rules-as-code framework (Catala, OpenFisca, Blawx) | Entirely tax/benefit/pension; and do not repeat the refuted absence claim |
| `bluebell`; and `cobalt` until someone opens its LICENSE | `bluebell` is GPL-3.0, confirmed. Implement the FRBR URI grammar ourselves |
| An FFR without its corpus provenance, `n` and interval | Enforced by a failing test, not by remembering |
| Keyless signing for filer-side attestations | The signing identity lands in a permanent public transparency log |
| Any predicate whose validity depends on a range being protected, or on a vocabulary read from the filed artifact | `sheetProtection` is an application flag; the `Dropdown` sheet is hidden **and the only unprotected one** |
| The ESEF conformance suite as a free benchmark | A 68-row index of free-text descriptions; no valid/invalid flag |
| Anything that repairs the artifact | **L5 must never repair. It adjudicates and reports** |
| A hosted spreadsheet cell store on the verdict path | The Grist "Cellbreak" escape, `GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, escaped Pyodide by three independent routes |

### 8.2 Additionally ruled out by this decomposition

| Not a phase | Reason |
|---|---|
| **Any hackathon phase** — application, submission, deck, demo video, portal check (E0) | The deadline is gone. The README-as-pitch survives as a P14 build; the 60-second capture survives as an optional asset; **E0 is retired outright** so nobody spends ten minutes on it out of habit |
| **An "integration" or "end-to-end test" phase** | Every phase carries its own acceptance test with its own named negative control. A terminal test phase would be exactly the *"the suite is green"* validation rule R1 forbids |
| **A "hardening" or "polish" phase** | It would produce no number. Under rule R3 that disqualifies it as a phase; hardening is a property of each phase's exit gate |
| **A performance-optimisation phase** | The measured budget is ~30 ms core and ≈ 450 ms complete run against a **3.4-filings-per-working-day** population. An optimisation phase would produce no number that changes a decision. Performance appears only as a non-regression budget inside phases that touch the hot path |
| **A second recalculation engine on the verdict path** | LibreOffice writes **53** main-namespace validations where 35 + 19 = 54 — one loss, unexplained, in the step recommended to fix a silent loss. It is offline only, digest-pinned, and its output is a **table** the online path reads |
| **The conformal abstention layer as a default** | It is a *gated sub-build* of P13-B3 and is likely dead on arrival: 0 of 3,755 unlocked cells are ambiguous under the address key. **There is no learning problem in the workbook** |
| **OCR of the 10 scanned circulars as a blocking item** | It is a **declared permanent gap** carried on every predicate whose correctness rests on a full-text negative search result — `circulars_unreadable: 10/399` — until an optional half-day build inside P13-B2 clears it |
| **A `REJECTED` predicate state** | Rejected candidates live in the `rejection` table with `predicate_id NULL`. Spec §V.7.5 flags this as unconfirmed — **P4-B1 must confirm it before the schema is written**, and this line is the reminder |
| **Averaging the settled fraction across templates** | It is a per-template property. Any code path that averages it fails a test in P15 |

---

## 9. HOW THE SIX DETAIL DOCUMENTS PARTITION THESE PHASES

Every detail document uses **these** phase IDs and **this** ordering. No document may re-decompose.

| Document | Phases it specifies in full |
|---|---|
| `plan/02-phases-foundation.md` | **P0, P1, P2, P3** |
| `plan/03-phases-verdict.md` | **P4, P5** |
| `plan/04-phases-qualification.md` | **P6, P7, P8** |
| `plan/05-phases-probes-attestation.md` | **P9, P10, P11** |
| `plan/06-phases-model-and-clause.md` | **P12, P13** |
| `plan/07-phases-surface-and-transfer.md` | **P14, P15** |

**Three cross-document obligations**, because three builds live in one phase and are argued in another:

1. **P4-B4 carries the mechanical transfer measurement** (conflict 3). `07` describes the E4 threshold and
   the cost arm; `03` specifies the build that produces the mechanical number. Neither may restate the
   other's numbers.
2. **P9-B1 is spike-eligible after P5** (conflict 2). `05` specifies it, and must specify
   `test_unqualified_relation_cannot_settle_a_cell` as its guard.
3. **P8-B1 runs in its own lane from day 0** (conflict 1). `04` specifies it, and must state plainly that
   its start does not wait on P7.

**Five more, added by the adversary pass, because each repair lands in one document and binds another.**

4. **`claims_fault_classes` on the envelope** (F1). `03` P4-B1 adds the field — required, non-empty, inside
   `envelope_projection()` and therefore inside `code_sha256`. `04` P7-B3 consumes it, refuses a claimed
   class with `O == 0`, and refuses a claim that post-dates its campaign. **Neither document may treat the
   field as optional; a candidate without it does not load.**
5. **`formula_source: TEMPLATE | FILING`** (F19). `02` P3-B4 adds the required keyword to `recalculate`;
   `03` P5-B2's `tools/gen_contract.py` publishes the rule in `docs/EVALUATION-CONTRACT.md` and asserts the
   transition table against it; `04` P6-B3 uses `FILING`; `05` P9-B1 uses `TEMPLATE`. **Two phases were
   reading one word two ways and both passed in isolation.**
6. **The clean-filing exit criteria are re-founded on a corpus the product did not compute** (F2). `04`
   P8-B2 provides `derived_by`; `03` P5's exit criterion 1 and `05` P9's exit criterion 2 must each name a
   filing whose derived cells `src/cdfc/calc/` did not write. **One such filing makes each gate
   non-vacuous.**
7. **`textsource.py` moves from `06` P12-B1 to `04` P7-B0** (F35). `06` references the artifact rather than
   creating it; `04` builds it where its consumer is. Neither restates the other's estimate.
8. **Negative-control id ranges are allocated per document** (F27), tabulated in `04` §0.8(e) and entered
   in `01` §2 as normative, with `ci/catalogue-ids.sh`, `test_nc_meta__ids_are_unique` and
   `test_nc_meta__id_is_inside_its_document_range` **required at P0-B3, before the first entry is
   written.** Four collisions existed across four documents, and two documents asserted the collision away
   rather than checking it.

---

## 10. THE ONE NUMBER EACH PHASE PRODUCES — SUMMARY

Rule R3 in one table. Every entry is a quantity that does not exist today.

| Phase | The number | Denominator | Warrant |
|---|---|---|---|
| **P0** | CI commitment gates demonstrated to fail against a named broken build — **against the pre-registered set `LIVE = {1…13, 17, 18}`, not against a count the same person may re-partition** (F8; enumeration per `plan/02` R5, arbitration C4) | **18** build-gate rows, of which **15 named `LIVE`** and exactly **3 named `PENDING`** (`{14, 15, 16}`) | MEASURED |
| **P1** | The reader-agreement vector | 8 fields × 9 workbooks = 72 | MEASURED |
| **P2** | The field surface for **all nine** workbooks + templates with no derivable mask | 9 workbooks | MEASURED |
| **P3** | Cached-value reproduction rate (E11's positive control) | 505 (FME) / 1,495 (all nine) | MEASURED |
| **P4** | `schema_keys` both-ways agreement · **and** the per-workbook distribution of the 515 figure | 280 predicates / 9 workbooks | MEASURED |
| **P5** | The **runtime** closure partition and the runtime settled count's delta from the static 2,373 | 3,747 cells | MEASURED |
| **P6** | **`U/G` for our own operator mix**, `K/O` per fault class, **and `I/G` — the mutants our own evaluator could not adjudicate, published beside `U/G` every time either renders (F18)** | generated mutants `G` | MEASURED |
| **P7** | The five-gate attrition funnel over the harvested set — **stage one as three integers, plus the obligation-coverage PAIR `predicates_with_a_STATUTE_obligation` **and** `predicates_with_a_TEMPLATE_obligation` (F9, C2) and `kr_claimed` vs `kr_all_classes` (F1)** | 280 predicates | MEASURED |
| **P8** | The first FFR on a corpus we did not write **and did not compute** (F2), with `n`, `n_non_synthetic`, a Wilson interval and a **computed** independence property; the **post-gate** settled count; and **F36's two integers of the mask against what a competent filler actually filled** | `n` filings / 3,747 cells | MEASURED |
| **P9** | Per-relation before/after settled-count delta, incl. relations that moved nothing | 25 relations | MEASURED |
| **P10** | **`\|RESIDUE\|`** with its fault-model version and adjudication-record hash | WRONG mutants generated | MEASURED |
| **P11** | Byte-identity result on a second machine; non-determinism sources enumerated vs removed | bytes in the report | MEASURED |
| **P12** | **`k of 20`** with its Wilson interval; and **`\|A\|/\|drawn\|`**, the decidable fraction of the instrument | 20 Stratum-A obligations | MEASURED |
| **P13** | Admitted predicates per 100 candidates and per rupee, by model; and **`mu_base_error_rate`, an ERROR RATE (F26)** | 600 candidates / population P1 | MEASURED |
| **P14** | Surfaces passing all four surface gates, **plus `\|SURFACES\|` as a time series over an append-only registry (F11)** | enumerated rendering surfaces | MEASURED |
| **P15** | Human minutes per transferred predicate vs from-scratch authoring; per-template settled fractions | ≥ 10 predicates / 9 templates | MEASURED |

---

## 11. THE CLOSING CHECK

Three properties of this decomposition to verify if it drifts.

**One.** The plan's longest pole is a **human calendar**, not a compiler, and the plan says so in three
places (§3.3 conflict 1, §4.1, §7). If a revision quietly moves P8-B1 later, that revision has moved the
critical path and should say so.

**Two.** Every gate in §6 has a **failure branch that ships something**. There is no gate whose failure
produces a stall. Check any new gate against that rule before adding it; a gate that stalls is a gate that
will be renegotiated under pressure, and *a criterion revised after seeing the result is not a criterion*.

**Three.** No part of the assembly is removable without another part becoming decorative. Remove seeded
defects (P6) and the FFR is uncomputable and the gate is decorative. Remove the gate (P7, P8) and the
settled fraction is an assertion. Remove relations (P9) and it is a ceiling rather than a growth curve.
Remove typed non-settlement (P5) and the whole thing is a linter. **That interlock is the test of whether
this is a design rather than a stack** — and it is the reason the phase order above is a dependency graph
and not a backlog.

**Four, added by the adversary pass and the most useful of the four.** *Every gate of the form `k of n`
where this plan also writes `n` must say who may change `n`, and how visibly.* Three gates failed that test
— `gates_live == gates_written`, `surfaces_passing == len(SURFACES)`, and `K/O ≥ 0.80` over a class set the
gate itself selected — and each failed the same way: **the thing being measured was allowed to choose its
own denominator.** That is the mechanism this product exists to detect, committed three times inside the
plan built to prevent it. Check any new gate against it before adding it.

---

## REPAIRS APPLIED (adversary pass)

Compiled against `plan/08-adversary.md`. One row per finding this document owns or shares. Where a repair
required a decision the plan did not contain, the decision is marked **DECIDED** with the alternative it
beat; two are **OPEN — USER DECISION** and neither blocks a phase.

| id | Sev | The finding, in one line | What changed here | Where |
|---|---|---|---|---|
| **F1** | FATAL | G2's registry bar computes `K/O` over a denominator the predicate chooses after the campaign | `claims_fault_classes` added to the envelope field list as **required, non-empty and inside the content address**, with the mechanism stated; P7's number and exit gate now require both `kr_claimed` and `kr_all_classes`; P14-B4's library renders the two columns side by side | §5 P4 build 1 · §5 P7 number + exit gate · §5 P14 build 4 · §9 obligation 4 |
| **F2** | FATAL | The `TEMPLATE-COMPUTED` clean corpus is generated by the code the arithmetic predicates re-check | P8 build 2 now records **`derived_by ∈ {CALC, FOREIGN_ENGINE, NONE}`** and states what each licenses; barrier 4 requires **computed** independence; severity gains `BLOCKING_MIN_NON_SYNTHETIC = 30`; P5's and P9's clean-filing exit criteria re-founded on a corpus the product did not compute; the P8 fallback branch corrected | §4.2 barrier 4 · §5 P5 exit · §5 P8 builds 2/3/4, exit gate, fallback · §5 P9 exit · §6 G-CORPUS |
| **F9** | FATAL | The five-gate funnel is undefined at G0 for 280 clause-less harvested candidates | **DECIDED, then ARBITRATED (C2)** — the **`source: STATUTE \| TEMPLATE`** discriminator, and a template-derived obligation against the pinned blank rendered as an addressable instrument, with **G0 running for real** over it; stage one renders **three integers**; **the published figure is two numbers, `0/280` STATUTE and `280/280` TEMPLATE, together or not at all**; guards named | §5 P7 builds 1 and 2, number, exit gate |
| **F13** | FATAL | Nothing tests that the settled fraction cannot **rise** as a filing carries less information | `test_prop__fraction_does_not_rise_as_the_filing_empties` added to P5's exit gate, **plus the DECIDED design change that makes it hold**: `OUT_OF_SCOPE` from a non-degeneracy precondition stays in `inScope`, and every surface renders `inScope` beside `cellsTotal` | §5 P5 exit gate |
| **F18** | FATAL | `U/G` measures the evaluator's coverage, not the operator mix | P6 build 3 rewritten to three-way classification with `I`; P6's exit gate and §10's row require `I` beside `U/G` | §5 P6 build 3, exit gate · §10 |
| **F19** | FATAL | F11 mutants are unobservable by construction, so `TEMPLATE_DIFF` can never clear G2 | `formula_source` made explicit and published in `docs/EVALUATION-CONTRACT.md`; P6's exit gate **fails** on `F11.O == 0`; P9's exit gate cross-references admissibility at G2 | §5 P6 build 3, exit gate · §5 P9 exit gate · §9 obligation 5 |
| **F23** | FATAL | `CanaryRow.elapsed_us` is inside the canonicalised evidence, so G-REPRO cannot hold | P11's exit gate gains `test_contract__no_duration_field_in_a_hashed_object`, the extended `ci/no-clock-in-core.sh` pattern set, and the rule that timings live outside the payload **while the evidence of execution stays inside** | §5 P11 exit gate |
| **F3** | SERIOUS | G-EVAL arm 2 has no failing condition against its only independent instrument | Gate row gains a **pre-registered `d`** on engine disagreements and the `PASSED — NOT INDEPENDENT` recording; P3's exit gate gains `test_arm_two_author_is_not_the_evaluator_author` and points at the staffing decision | §5 P3 exit gate · §6 G-EVAL |
| **F8** | SERIOUS | P0's exit gate is `x == x` | Exit gate restated over the **pre-registered sets `LIVE = {1…13, 17, 18}` / `PENDING = {14, 15, 16}` — 15 of 18** with **`test_contract__live_set_is_pre_registered`** (`plan/02`'s test and `plan/02`'s enumeration; arbitration C4 — the summary "13 `LIVE`" and the guard `test_p0__pending_set_is_exactly_the_four_named_rows` are deleted); §10's denominator restated | §5 P0 exit gate · §10 |
| **F10** | SERIOUS | G-READERS gates only the three fields on which every instrument already agrees | **New gate `G-READERS-B`** over the four `A`/`A′`-only fields, with the per-field mutation guard | §6 |
| **F11** | SERIOUS | P14's exit gate compares a registry against itself | `SURFACES` made append-only with a growth log, a dated-argument removal rule, `test_surface__registry_is_append_only`, and `\|SURFACES\|` as a time series | §5 P0 build 3 · §5 P14 number · §10 |
| **F12** | SERIOUS | G-CORPUS's `n ≥ 30` is satisfiable entirely from the self-generated corpus | **`G-CORPUS: RESTRICTED`** made a named third outcome in the gate table and in P8's exit gate | §5 P8 exit gate · §6 G-CORPUS |
| **F22** | SERIOUS | The headline `2,373` is pinned as a literal in a golden test | P5's exit gate requires it **computed from the emitted envelopes** and reconciled in writing; the literal moves to `docs/HARVEST-DELTA.md` | §5 P5 exit gate |
| **F24** | SERIOUS | Three contracts for `settledFraction` on an `INVALID` run | One rule, stated once: **present and `null`**, with the JSON-Schema `if/then` and its guard | §5 P11 exit gate |
| **F25** | SERIOUS | `E2E-INVALID` asserts "dead predicates named" on a fixture that never reaches the predicate layer | P10's negative control **split into two controls with two different assertions**, with the correction propagated to `01` §1.10 / §2.5 in the same commit and a `docs/CATALOGUE-CORRECTIONS.md` row | §5 P10 negative control |
| **F26** | SERIOUS | `μ` is an accuracy here and an error rate in `06`, and the thresholds invert | Field renamed `mu_base_error_rate` in §5 P13, §6 and §10, with `test_contract__mu_is_an_error_rate` | §5 P13 · §6 G-CONFORMAL · §10 |
| **F27** | SERIOUS | Colliding negative-control ids across four documents | Per-document id ranges made a cross-document obligation; the three meta-tests and `ci/catalogue-ids.sh` required **at P0-B3** | §5 P0 build 3 · §9 obligation 8 |
| **F28** | SERIOUS | `ci/no-green-tick.sh`'s scan set names three directories P0 does not create | Scan roots read from `surface/labels.py::SCAN_ROOTS`; `test_nc__CI01c_scan_root_list_is_not_a_literal`; the narrowing recorded in `ci/GATES.md` | §5 P14 negative control |
| **F30** | SERIOUS | G-SETTLE's `beats_baselines` is not evaluable as written, and it is hashed before the run | The criterion restated **as arithmetic with a numeric floor**, plus the two guards that keep it machine-evaluable | §6 G-SETTLE |
| **F34** | SERIOUS | The `P9-B4 → P10-B2` edge is absent, and it moves P11 by ten days | Edge added to §3.1 with its argument; §4.1 and §7 recomputed; **the `k = 0` critical path corrected from ~104 to ~118** | §3.1 · §4.1 · §7 |
| **F37** | SERIOUS | The corpus lane is sized for the gate (30), not for the severity axis (189) | Both numbers and both person-day costs published in §7; **DECIDED** default is ship `ADVISORY`-capped and print the reason; funding is **OPEN — USER DECISION** (`plan/04` §5 O5) | §7 |
| **F43** | SERIOUS | The parallelised critical path (now **118** days, C6) assumes 2–3 engineers while every estimate assumes one author | **Staffing model stated once and both numbers derived from it**; the three places where a second author buys *evidence* named; `SAME-AUTHOR` labelling required; funding is **OPEN — USER DECISION** | §7 |
| **F4, F5, F16, F17, F31, F35, F36** | — | Sweep semantics, computed independence, the corpus firewall, the Wilson-bound entry's id (**`NC-Q56`**, C9 — the former `NC-Q22b`, which is retired), DoD line C4, the instrument text source, the mask's external check | Repaired in `plan/04-phases-qualification.md`, which this document does not restate; §5 P7/P8 and §9 carry only the consequences | `04` |
| **F6, F7, F14, F15, F20, F21, F29, F32, F33, F38, F39, F40, F41, F42, F44** | — | Not attributed to this document | Owned by `01`, `02`, `03`, `05`, `06`, `07` | — |

**The residue of this pass, declared because §0's own rule requires it.** Everything above is a repair
*specified*, not a repair *run*: no test in this table has been executed, because none of the code exists.
Three of the nine FATAL findings were circularities inside the plan's own validation machinery, found by
reading — which is the same instrument that produced them. **The rate at which new mechanisms are found is
a number this project should publish and must never claim converges**, and the only place it can come from
is `catalogue.yaml`'s growth log. This pass added nineteen rows to it in one commit; that is data about
the pass, not evidence about the plan.

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C1** — `d` is a frozen integer | `d = 11`, pre-registered in `experiments/G-EVAL/PREREGISTRATION.md` with its derivation, the corpus content hash and the date; `d` no longer recomputes from the corpus it gates | §5 P3 arm-2 bullet · §6 G-EVAL row |
| **C2** — F9's disposition | the **`source: STATUTE \| TEMPLATE`** discriminator replaces `ObligationKind`; the obligations-table build renamed its provenance field to `ingest_source`; **G0 runs for real**; every published harvest-obligation count became **two numbers** (`0/280` STATUTE **and** `280/280` TEMPLATE, together or not at all) | §5 P7 build 1 · §5 P7 build 2 · P7 number · P7 exit gate · §10 P7 row · F9 repair row |
| **C4** — P0's gate set | `15 LIVE / 3 PENDING of 18`, sets `{1…13,17,18}` / `{14,15,16}` as literals; guard is `test_contract__live_set_is_pre_registered`; **`test_p0__pending_set_is_exactly_the_four_named_rows` deleted, not renamed** | §5 P0 number · P0 exit-gate box · §10 P0 row · F8 repair row |
| **C6** — the `k = 0` critical path | **~118** stands as the arithmetic of record; the F43 row no longer names a retired figure | §7 · F43 repair row |
| **C8(a)** — prereg test name | `test_e6__…` → `test_contract__preregistration_criterion_is_machine_evaluable` | §6 G-SETTLE note |
| **C9** — the catalogue | `NC-Q42` → **`NC-Q57`** (F1, the merged entry); the F17 row now names **`NC-Q56`** rather than the retired `NC-Q22b`; this document allocates no ids and references `01` §2 | §5 P4 note · §10 repairs row |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
