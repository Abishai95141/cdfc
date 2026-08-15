# P12 entry — what can be built, what cannot, and which of the plan's own failure branches each falls under

**Written before P12-B1, and it is the phase's most consequential document.** `plan/06` §P12 lists
six entry criteria and four builds. Three of the four builds are buildable in full on this tree.
**One artifact is structurally absent and two steps are outside what a build can do**, and each is
recorded here against the branch `plan/06` already pre-committed for it — because a blocker that
the plan anticipated is a *result*, and a blocker discovered while writing the close is an excuse.

---

## The four things that cannot be done here, and their pre-committed branches

### 1. THE POOL — no statutory instrument is pinned. **Structural, not configurational.**

`corpus/instruments/MANIFEST.json` carries **nine instruments, every one `kind: TEMPLATE`**, and
`statute_instruments: []`. There is no PDF anywhere in the tree, no PDF in the git history, and no
PDF library in `requirements.lock`.

This was decided at P7-B0 and is recorded in `docs/decisions/D-P7-01-no-statutory-instrument.md`:
the plan's entry criterion E7.6 asserted *"the regulation PDF and the 399-circular corpus are on
disk"* and **neither was**. The ruling was *build the harness; do not build the document*, and
**synthesising a plausible instrument was rejected outright** — every G0 figure is
`source_text.find(quote)` at a character span, and against an invented text `quote_not_located`
becomes a statement about our own fabrication while the attrition funnel's first stage measures
nothing.

`plan/06` §P12 "What it kills if it fails" pre-commits a branch for a pool that cannot be built:

> *"The pool cannot be built — the regulation's two extractions disagree so widely that fewer than
> 20 Stratum-A obligations survive. Then `PoolExhausted` fires, no model call is made, no money is
> spent, and the published result is `|A| < 20` with the disputed-region count and its page
> numbers — a measurement of the instrument, which is a legitimate outcome."*

**The case here is that branch's limiting form, and it is stronger rather than weaker.** The
extractions do not disagree; there is nothing to extract. `tools/e6/enumerate_shall.py` exits **2**
with the reason rather than 0 with an empty pool, because an empty pool is a measurement of the
*regulation* and an absent instrument is a measurement of *this repository*.

**What it blocks, in order, and every link is enforced by code rather than by convention:**

| | |
|---|---|
| no statute | → `enumerate_shall` has no instrument, and raises `NotAStatute` rather than returning `()` |
| no pool | → no `draw()`, so no `draw_sha256` |
| no draw hash | → `prereg.append()` would refuse it anyway: `PoolNotYetFixed` fires while `textsource_sha256` and `exclusion_rule_sha256` are absent |
| a partial lock | → `run.assert_ready()` raises `ArtefactHashesMissing`, **naming the five missing fields** |

The refusal chain terminates exactly where the missing artifact is. That is the property P12-B1 was
built to have, and it is observable: `make pool` and `make e6-status`.

### 2. THE RUN — 600 calls, real money, and a human's decision

`plan/06` budgets **≈ $13 (MODELED), $25 with re-runs, $51 including the extension reserve**, and
names the transport (Batch), the model (`claude-opus-5`) and the count (~600 calls).

**Three separate reasons it is not taken here, and only the third is about permission:**

1. `anthropic` is not installed and is **deliberately not in `requirements.lock`** — nothing on the
   verdict path may import a model client, so the SDK is part of taking the run rather than part of
   building the harness. `build_client()` raises `ModelClientUnavailable` and says so.
2. There is no credential in this environment.
3. **It spends the user's money and is irreversible.** Committing ~$13–51 of somebody's budget is
   not a step a build performs on its own initiative, whatever the harness is capable of.

**But the ordering never depended on the run.** `plan/06`'s own opening states the phase's
epistemic content:

> *"the epistemic content of P12 is that a five-gate criterion was specified, locked and hashed
> **before a model was called**"*

That is what P12-B1 through B4 deliver, and it is complete: `PREREGISTRATION.md` is generated,
hashed and locked; `beats_baselines` is arithmetic and the lock refuses a criterion `decide()`
cannot consume; `decide()` is exhaustively pinned over all 164 points of its input space. **The run
is a button, and every refusal in front of it has been observed.**

### 3. B1 AT ITS SPECIFIED STRENGTH — Daikon, and the switch trigger the plan wrote in advance

`plan/06` P12-B2 states the trigger before the fact:

> *"if Daikon cannot be pinned or licensed, **B1 does not run** and `beats_baselines` evaluates its
> B1 term as `False`. It does not fall back to a hand-written weaker detector, because a weaker
> baseline makes L3 easier to beat, and a fallback that moves the result in the direction we would
> like is not a fallback."*

**This was already resolved at P7-B3, and in the honest direction.**
`src/cdfc/qualify/baselines/b1_invariants.py` is a local invariant miner, and its module constant
`NOT_DAIKON` travels with every figure it produces:

> *"B1 is a local invariant miner, NOT Daikon: four single-variable templates at confidence 1.0, no
> inter-variable relations. Marginal kill over it OVERSTATES marginal kill over Daikon."*

Docker and Java are both present on this machine, so the blocker is not the runtime — it is that
Daikon is not pinned by digest and its licence is recorded unopened. **The claim narrows; it does
not soften.** Any `DECISION.md` produced here must carry *"beats B0 ∪ B2; declines to claim it
beats B1, which did not run at its specified strength"* in its headline sentence.

### 4. THE TWO HUMANS — the stratification, and κ

The stratum assignment is a **named human** judgment, and `NC-M05` asserts `assigned_by` is a
person. A second named human re-assigns a random 20% and **Cohen's κ is published with its `n`**.

Neither is available here, and κ is the one blocker in this whole programme with **no mechanical
substitute at all** — the same finding P10 exit criterion 7 recorded as NOT MET. `TableOracle`
raises `LookupError` on an unassigned obligation rather than defaulting to either stratum, which is
the right refusal: defaulting would turn the one human judgment the entire `n = 20` rests on into a
fallback.

---

## What IS built, in full, and it is most of the phase

| Build | Status | Notes |
|---|---|---|
| **B1** `power.py` | **COMPLETE** | Exact rational binomial. All three of `plan/06`'s tables reproduce **exactly**, including the §0.2 correction: `P(X ≤ 2 \| n=20, p=0.30)` is `0.035483…` → **0.035**, and the specification's `0.036` is wrong |
| **B1** `draw.py` | **COMPLETE** | Keyed-sort permutation, the §0.4 cap-never-truncates-the-denominator invariant asserted **at construction**, `extend()` with one stage and no third |
| **B1** `enumerate_shall.py` | **COMPLETE**, unexercised on a statute | Tested against a constructed instrument; refuses a TEMPLATE, refuses an inexact chapter, refuses an undeclared heading |
| **B1** `prereg.py` + `criterion.py` | **COMPLETE** | Append-only, ordered, git-ancestry; `lock()` refuses a prose criterion **before writing anything** |
| **B2** the three baselines | **COMPLETE** (B0, B2 at strength; B1 declared) | Already existed from P7-B3; P12 adds `marginal.py` |
| **B2** `beats_baselines` | **COMPLETE** | The F30 repair: a pure function, integer arithmetic, exhaustively pinned |
| **B3** `parse.py` / `run.py` / `client.py` / prompts | **COMPLETE except the call** | Every refusal observed. Both prompts are files, verbatim and hashed |
| **B4** `decide.py` / `funnel.py` | **COMPLETE** | `decide()` pinned at all 164 points; the funnel's stage 0 is the planned count, discards included |

---

## The measured entry facts

| Fact | Value | How to re-derive |
|---|---|---|
| instruments pinned | **9**, all `kind: TEMPLATE` | `make pool` |
| statutory instruments pinned | **0** | `make pool` |
| pre-registration `h0` | recorded in `experiments/E6/preregistration.lock.json` | `shasum -a 256 experiments/E6/PREREGISTRATION.md` |
| lock fields present | **2 of 7** — `h0`, `committed_at` | `make e6-status` |
| lock fields missing | **5** — `textsource_sha256`, `exclusion_rule_sha256`, `draw_sha256`, `strata_sha256`, `baselines_sha256` | `make e6-status` |
| `run_may_proceed` | **False** | `make e6-status` |
| ancestry state | `UNVERIFIABLE (no runlog — no model call has been made)` | `make e6-status` |
| model spend to date | **$0.00** | there is no `runlog.jsonl` |

**`ancestry_state()` never returns `VERIFIED` by default**, and the three states are kept apart
because their remedies differ: a violation is a finding about the experiment, and an unverifiable
ancestry is a finding about the environment. That rule is inherited from
`g2_kill.ancestry_state`, where an unverifiable claim ancestry has always been reported as
`UNVERIFIABLE (no git history)` rather than as a pass.
