# 06 — THE MODEL-BEARING AND CLAUSE-BEARING PHASES
## P12 and P13, in full · build plan, part 6 · compiled 11 August 2026

**This document specifies P12 and P13 and nothing else.** It uses the phase IDs, the build numbering, the
ordering, the gates and the effort figures of `plan/00-decomposition.md`, and it satisfies
`plan/01-validation-methodology.md` — whose test taxonomy (§1), negative-control catalogue (§2), mutation
regime (§3), Definition of Done (§4), CI pipeline (§5) and fixture strategy (§6) are referenced **by name**
here and never restated. Where this document adds a catalogue entry it says so and gives the entry's full
shape; where it relies on an existing one it names the id and stops.

**Why these two phases are written together, and why they are two and not one.** P12 is an experiment whose
only product is a number. P13 is the construction that number sizes. They are separated because **a phase
cannot gate itself**: the epistemic content of P12 is that a five-gate criterion was specified, locked and
hashed *before a model was called*, and a phase that both ran the model and decided what counted would have
nothing to offer. The seam is exactly one file — `experiments/E6/DECISION.md` — and CI enforces it: the
presence of `src/cdfc/model/propose.py` without that file fails the build (barrier 5).

**The two things this group is written to get right, stated at the top because everything below serves
them.**

> **One.** A failed settling experiment must produce a **smaller system that ships**, not a stalled one.
> §2 of this document states the `k = 0` system in full — what exists, what is published, what is lost, and
> what the surfaces say — so that the failure branch is a specification and not an improvisation.
>
> **Two.** Every model-bearing build is validated by something that is **not a model**. The spec establishes
> that a model may never be the final adjudicator: LLM judges detect false success at **AUROC ≤ 0.65 and
> 13% recall at a 10% flag rate**. §1 is the standing table of every model-produced artifact in these two
> phases and the deterministic or human instrument that adjudicates it — with the residue named.

---

## §0 — NINE THINGS THIS DOCUMENT DECIDES BEFORE IT BEGINS

Nine details are under-determined, in tension, or arithmetically wrong across the binding documents. Each is
decided here, with its reason, so that no build starts on an ambiguity. Where the spec is genuinely open,
the decision rule is given rather than an invented answer.

### 0.1 The experiment directory is `experiments/E6/` — DECIDED

`spec/04-path.md` §1.1 writes `experiments/9.1/PREREGISTRATION.md`; `plan/00-decomposition.md` §5 P12 and
barrier 5 both write `experiments/E6/`. **Ruling: `experiments/E6/`.** *Reason:* the decomposition is
binding on IDs and its barrier-5 CI check names that literal path; a build gate and the artifact it guards
must agree on a string, and `9.1` is a section number in a superseded document, not an experiment id. The
conformal feasibility decision (E10) gets the sibling `experiments/E10/`.

### 0.2 The power table is recomputed exactly, and one published figure is corrected — DECIDED

`spec/04-path.md` §1.1 prints `P(X ≤ 2 | n = 20, p = 0.30) = 0.036`. The exact binomial value is
**0.035483…, which is 0.035 to three decimal places** (MEASURED — `research/scripts/e6_power.py`, exact
integer binomial, no RNG, no normal approximation, run 11 Aug 2026). Every other figure in that table
reproduces exactly.

**Ruling: the corrected table below is normative and is what `PREREGISTRATION.md` carries.** The correction
is recorded in `experiments/E6/PREREGISTRATION.md` §"corrections to the source table" with the spec section
it corrects, so that a reader who has the spec open does not conclude the pre-registration was edited.
*Reason:* a pre-registration containing a wrong number is a pre-registration nobody can check, and the
correction moves a *delete* probability, which is the direction where a reader is entitled to be suspicious
of us.

### 0.3 "Exactly one extension to `n = 40`" means a **pooled** 40, and arithmetic settles it — DECIDED

`spec/04-path.md` §1.1 leaves it ambiguous whether the extension draws 20 more Stratum-A obligations
evaluated over the pooled 40, or a fresh independent sample of 40. The same section states two consequences
of the rule: it deletes L3 **92.9%** of the time at `p = 0.15` and wrongly deletes it **13.4%** of the time
at `p = 0.35`.

| Interpretation | P(delete) at p = 0.15 | P(delete) at p = 0.35 |
|---|---:|---:|
| **A — draw 20 more; evaluate `X + Y ≥ 12` over the pooled 40** | **0.929** | **0.134** |
| B — a fresh independent `n = 40` sample at `≥ 12` | 0.926 | 0.060 |

**Ruling: interpretation A.** *Reason:* it reproduces both published figures exactly and B reproduces
neither. This is settled by arithmetic, not by preference, and the arithmetic is in
`research/scripts/e6_power.py::retain_pooled` / `retain_fresh40`, reproduced by
`src/cdfc/experiment/power.py` at P12-B1. **Consequence for the draw:** the extension consumes the *same*
enumerated pool under the *same* PRNG stream, continuing without replacement from where stage 1 stopped —
so it is one draw with a stopping rule, not two experiments.

### 0.4 The Stratum-B cap is a cap on **generation**, never on the denominator — DECIDED

`spec/04-path.md` says *"Draw until `|A| = 20`; cap Stratum B at 10; ≈30 drawn in total"*, and separately
makes `|A| / |drawn|` — the measured decidable fraction of the instrument — a headline result. Those two
sentences are in tension: a cap that stops the draw truncates the denominator of the very fraction being
measured.

**Ruling: the draw continues until `|A| = 20` regardless of how many Stratum-B obligations it turns up.
Every drawn obligation is recorded in `strata.csv` with its stratum and enters `|drawn|`. The cap of 10
applies only to how many Stratum-B obligations are carried forward into candidate generation.**
*Reason:* this is scope truncation (NC-D01's mechanism) applied to our own headline, and it moves the
decidable fraction in the flattering direction — exactly the shape of error `test_denominator_provenance`
exists to catch one layer down. It gets its own negative control, **NC-M03**.

**And the estimator, because the stopping rule is not simple random sampling.** Drawing until a fixed number
of successes is **inverse (negative-binomial) sampling**, under which `a/n` is biased upward and the
unbiased estimator is `(a − 1)/(n − 1)`. **Ruling: publish the two integers first — `|A|` and `|drawn|` —
then both point estimates, each labelled, and label any binomial confidence interval computed on them
`APPROXIMATE — inverse sampling, interval not exact`.** A Wilson interval is not exact here and we say so
rather than printing it bare. Negative control **NC-M04**.

### 0.5 The retain condition is a conjunction, and its failure at `k ≥ 6` is DELETE — DECIDED, and it must be locked before the run

The rule is *"retain iff **≥ 6 of 20** survive all five gates **and** the surviving set beats `B0 ∪ B1 ∪ B2`
on marginal kill at equal FFR"*. Nothing states the outcome when `k ≥ 6` and the baselines are **not**
beaten.

**Ruling: DELETE.** *Reason:* the extension exists to resolve a *sample-size* ambiguity in the 3–5 band. A
`k ≥ 6` result that does not beat free work is not a sample-size problem — it is a measurement that the
model reproduced work the template and Daikon already do for nothing, and extending would be re-rolling a
criterion that was already satisfied on the axis the extension addresses. The decision record's headline in
that case is *"the model produced `k` checks that survive the gate and none that the free baselines did not
already produce"*, which is a stronger and more publishable sentence than "inconclusive". The same rule
applies at stage 2: pooled `≥ 12` without beating the baselines is DELETE.

**This ruling is a criterion. It goes into `PREREGISTRATION.md` at P12-B1, before the draw and before the
first API call — not into `DECISION.md` at P12-B4.** A criterion discovered while reading a result is not a
criterion, and this document exists partly so that this particular one is not discovered late.

### 0.6 "Equal FFR" is a comparability precondition, not a tuning knob — DECIDED

Predicates here are boolean and carry no threshold, so there is no free parameter with which to equalise two
false-failure rates. **Ruling: the marginal-kill comparison is admissible only when the candidate set's FFR
**Wilson upper bound** does not exceed the baseline union's Wilson upper bound on the *same* corpus and the
*same* observable mutant set `O`. When it does, the marginal kill is reported as the literal string
`NOT COMPARABLE — candidate FFR upper bound exceeds baseline` and `beats_baselines` is `False`.**
*Reason:* a candidate that kills more because it flags more has not beaten a baseline, it has moved along
the same trade-off, and the whole literature this project draws on is a record of that confusion. Fail-closed
is the direction that makes L3 harder to keep.

**AND `beats_baselines` IS NOW ARITHMETIC, BECAUSE AS WRITTEN IT WAS NOT EVALUABLE — adversary F30, and it
sat inside the one artifact whose entire epistemic value is that it was specified, locked and hashed before
the model ran.** `MarginalKill.killed_by_candidate_only` is `|K_c \ K_b|`, a count. *"Marginal kill strictly
greater than B0"* compares that count **to what?** To zero? To `killed_by_baseline(B0)`? To the baseline's
own marginal over the candidate? Three readings, three different gates, and **the weakest is trivially
satisfiable** — `|K_c \ K_B2| > 0` is true for any predicate that kills anything the two degenerate
envelopes do not, which is most of them. A criterion that has to be interpreted after the result is not a
criterion, and §0.5 says exactly that about a different clause of the same rule.

> **RULING — `beats_baselines` is a pure function with this body, written into `PREREGISTRATION.md` at
> P12-B1 in this form, before the draw:**
>
> ```python
> # src/cdfc/experiment/baselines/marginal.py
> MARGINAL_FLOOR_NUM, MARGINAL_FLOOR_DEN = 1, 10        # 10% -- locked at B1, see the argument below
>
> def beats_baselines(rows: tuple[MarginalKill, ...]) -> bool:
>     per_baseline = tuple(r for r in rows if r.baseline_id != "B0|B1|B2")
>     union        = next(r for r in rows if r.baseline_id == "B0|B1|B2")
>     if not all(r.comparable for r in rows):            # §0.6's precondition, fail-closed
>         return False
>     if not all(r.killed_by_candidate_only > 0 for r in per_baseline):
>         return False                                   # B1-not-run contributes a row with
>                                                        # killed_by_baseline = 0, so this term is
>                                                        # satisfied by any candidate that kills at all,
>                                                        # which is the honest reading of "declared not-run"
>     return (union.killed_by_candidate_only * MARGINAL_FLOOR_DEN
>             >= MARGINAL_FLOOR_NUM * union.observable)  # integer arithmetic; no float on this path
> ```
>
> **The floor is `10%` of the union's observable set, and it is a number rather than "strictly greater than
> zero" for one reason:** against the *union* of three free baselines, a single marginal kill is
> indistinguishable from noise in a campaign of thousands of mutants, and a retain decision resting on it
> would be a retain decision resting on one mutant. **DECIDED at 10%**, locked at B1.
> *Alternative it beat:* `union.killed_by_candidate_only > 0`, the reading the prose most naturally
> supports — rejected because it makes criterion 4 of G-SETTLE satisfiable by any candidate that kills one
> mutant the free work missed, which is not "beats free work", it is "is not identical to free work".
> *Second alternative it beat:* a floor expressed as a fraction of `killed_by_baseline(union)` — rejected
> because it is undefined when the union kills nothing, which is exactly the `EDR_1` case B2's golden
> already pins.
>
> **Two tests, and the second is the one that stops this recurring:**
> - `tests/unit/test_decide.py::test_decide__beats_baselines_is_arithmetic_not_prose` — **exhaustive** over
>   the `MarginalKill` tuple space at small `observable`, asserting the function's value at every point,
>   including every `comparable = False` combination.
> - `tests/contract/test_contract__e6_criterion_is_machine_evaluable.py::test_contract__preregistration_criterion_is_machine_evaluable`
>   — **`prereg.lock()` refuses to write a criterion `decide()` cannot consume.** The lock parses the
>   criterion section of `PREREGISTRATION.md` and asserts every threshold in it resolves to a value the
>   pure function reads. A criterion that is prose does not lock, and therefore the experiment does not run.

**AND THE FFR ARM HAS A CORPUS PRECONDITION, added because the adversary pass (F2) showed the
`TEMPLATE-COMPUTED` corpus is generated by the very evaluator the arithmetic predicates re-check.** "Equal
FFR" is vacuous when **both** arms' FFRs are structurally zero: on a corpus our own `calc/` computed, an
arithmetic candidate and an arithmetic baseline both fire zero times regardless of quality, so the
comparability precondition passes and tells you nothing.

> **RULING.** `marginal_kill(...)` sets `comparable = False` with
> `incomparable_reason = "FFR CORPUS UNINFORMATIVE FOR BOTH ARMS"` whenever the FFR corpus is
> `TEMPLATE-COMPUTED` **and** either arm's `read_keys` intersects the generator's `computed_cells` — the
> same intersection `g4_ffr.check()` computes, imported rather than re-implemented. `beats_baselines` is
> then `False` by the first clause above, and `DECISION.md`'s headline sentence carries the reason. **This
> is fail-closed in the direction that makes L3 harder to keep**, consistent with the rest of this section:
> a comparison we cannot make is not a comparison we won.
> `tests/unit/test_marginal.py::test_marginal__uninformative_corpus_is_incomparable`, and its admission-side
> twin `test_marginal__register_derived_corpus_is_comparable_for_membership_candidates`.

### 0.7 The instrument watcher lives at `src/cdfc/watch/`, not `src/cdfc/model/watcher.py` — DECIDED

`plan/00-decomposition.md` P13-B4 names `model/watcher.py`. The watcher **contains no model**: it is a daily
content hash and a diff, and the spec is explicit that it is *"diff-and-flag, not an NLP problem"*.

**Ruling: `src/cdfc/watch/`.** *Reason:* P13-B0's guard bans the package `cdfc.model` from the verdict-path
import closure as a single, uniform rule — cheaper and stronger than enumerating vendor client names. Putting
a model-free module inside `cdfc.model` forces that rule to carry an exception, and **an exception in that
gate is how the gate dies** — the identical argument `plan/00-decomposition.md` §1 uses to reject a package
name containing `check`, `valid`, `pass`, `clean` or `verify`. The decomposition groups the watcher under
P13 because the *phase* is the clause-bearing phase, not because the watcher bears a model.
**Consequence:** `cdfc.watch` gets its own offline-only structural test
(`tests/unit/test_watch_imports.py::test_watch__is_not_in_the_online_closure`), and `cdfc.model` stays
uniformly banned with no carve-out.

### 0.8 The extension's cost is quoted in its **form**, never as an integer — DECIDED

`spec/04-path.md` budgets *"$26 more if the extension fires"*. At the pre-registered unit price
(`$0.0218/candidate`, MODELED) the extension's 20 additional Stratum-A obligations × 2 regimes × 10
candidates = **400 candidates ≈ $8.67**, not $26. `$26` is reconcilable only with a full re-draw of ~30
obligations (600 candidates). The corpus does not state which.

**Ruling: the extension is quoted in its form — `20 additional Stratum-A obligations × 2 prompt regimes ×
10 candidates = 400 candidates` — and its cost is never quoted as an integer until a run records one in
`experiments/E6/runlog.jsonl`. The reserve is budgeted at the larger figure ($26) so a surprise cannot stop
the run.** *Reason:* this is exactly the rule audit §V.7.4 applied to the withdrawn `2,235 register GETs`
figure, applied to us. Two irreconcilable arithmetics and no stated `N` is the condition under which the
form, not the integer, is the honest quote.

### 0.9 Paths owned by other documents are deferred to, not re-fixed — DECIDED

Three artifacts this document references are created by phases specified elsewhere:
`registry/obligations.yaml` (P7-B1, `plan/04-phases-qualification.md`), `src/cdfc/predicates/ast_walker.py`
(P4, `plan/03-phases-verdict.md`) and the clean corpus manifest (P8-B1, `plan/04-…`). **Ruling: where this
document names such a path it is naming P07/P04's artifact, and if that document fixes a different path,
this document's references follow it.** Every test here that touches one takes the path from a module
constant (`cdfc.predicates.registry.OBLIGATIONS_PATH`) rather than a literal, so a path change is a
one-line diff and never a silently-passing test over a file that no longer exists.

---

## §1 — THE STANDING CONSTRAINT: NOTHING A MODEL PRODUCES IS ADJUDICATED BY A MODEL

The spec's boundary is architectural: *"Every model output crosses this line as DATA that a program has
already adjudicated. Nothing below opens a socket to a model endpoint."* The empirical warrant is that a
model is a poor judge of exactly the failure this product is about — **false-success detection at
AUROC ≤ 0.65, 13% recall at a 10% flag rate** — so a model judge would fail silently in the same direction
as the thing it is judging.

This table is normative for both phases. Every row is a model-produced artifact in P12 or P13; every
adjudicator is a deterministic program or a named human step; the last column is what that adjudicator
**cannot** establish, so no row is read as closure.

| Model-produced artifact | Adjudicator | Kind | Where | What it cannot establish |
|---|---|---|---|---|
| Candidate envelope, syntax | envelope schema + CEL parser; malformed ⇒ a **counted discard row**, never a retry | deterministic grammar | `experiment/parse.py`, `model/propose.py` | that the CEL means the clause — **NC-N01** |
| The clause quote | `source.find(quote)` must succeed **exactly once** at the declared span over a pinned text blob | string search | `model/guard.py::verbatim_guard` | that the located clause is the *right* clause |
| Declared `schema_keys` | AST walk, **both ways**: reads-undeclared ⇒ reject, declares-unread ⇒ reject | static analysis | `predicates/ast_walker.py` (P4) | — |
| Provisos and exceptions in the span | fail-closed detector: an unrecognised marker returns `UNDECIDED` and the candidate is **rejected** | deterministic + human annotation set | `qualify/g0_scope.py` (P7) | recall against marker forms nobody has seen |
| "Does it fire?" | `KR = K/O` over mutants verified observable **by recalculation of the workbook-as-program** | arithmetic over the artifact | `qualify/g2_kill.py` (P6/P7) | any defect the fault model does not contain — **§7.2** |
| "Is it degenerate?" | Z3 proof arm + hypergeometric control arm; `unknown` is **unproven**, never "non-degenerate" | SMT + counting | `qualify/g3_*.py` (P7) | anything Z3 returns `unknown` on |
| "Does it false-fail?" | count of fires over a corpus with `corpus_provenance ≠ SELF-AUTHORED`, Wilson interval, `n` | counting | `qualify/g4_ffr.py` (P8) | the corpus's blindness — **§7.12, NC-N03** |
| "Does it beat free work?" | set difference against `B0 ∪ B1 ∪ B2` over a shared `O`, at the §0.6 comparability precondition | set arithmetic | `experiment/baselines/marginal.py` | that the baselines were strong (hence the B0 positive control) |
| The retain/delete decision | `decide()` — a **pure function** of `(k, stage, beats_baselines)` and the locked thresholds | pure function over a hashed lock | `experiment/decide.py` | that the threshold was the right threshold (it is pre-registered, not proven) |
| Stratum A / B assignment | a **named human**, dated, before generation; a second human re-assigns a random 20% and Cohen's κ is published with `n` | human + agreement statistic | `experiments/E6/strata.csv` | correctness — κ measures agreement, not truth |
| OCR'd clause text (the 10 scanned circulars) | **the human is the adjudicator; dual-engine agreement is a SCREEN, not an adjudication** — confirmation against the page image, with an actor id, is required for every clause a predicate cites, and admission without that row is refused by the loader | **human** (the screen is two models and is labelled as such) | `clause/ingest.py` | a misconception shared by both OCR engines — **§7.5**, `NC-N30`. **The screen cannot establish anything the two engines are wrong about together, which is why it may not appear in this column alone** |
| L2b bound key | `Literal[*L1_KEYS]` at generation **and** a post-hoc deterministic key check that is kept though redundant | enum membership | `model/extract/postcheck.py` | that the extracted *value* is right |
| Admission of any predicate | R7 — **a human signs the batch** | human | `registry/admit.py` (P7) | — |

**Three properties of this table are load-bearing.**

1. **`decide()` takes no argument that can override a threshold.** The four inadmissible arguments named in
   the spec are hashed into `PREREGISTRATION.md`; the function's signature makes them unrepresentable rather
   than merely disallowed.
2. **Nowhere does a human or a model adjudicate a `PASS`.** Humans appear at the strata, at R7, at
   INNOCUOUS/WRONG, at clearing a `PROVISIONAL`, and at confirming an OCR'd quote. The verdict itself is
   never negotiated.
3. **The residue is declared, not hidden.** Row 1's last column is `NC-N01`, and it is the largest hole in
   both phases: *a predicate can clear all five gates and enforce a rule that does not exist.* §4 states
   what that costs.

---

# P12 — THE SETTLING EXPERIMENT

**Effort: 6 engineer-days** · B1 2 · B2 1 · B3 1 · B4 2
**Plus 4–6 person-days of a different person** — stratum assignment (2), second-annotator re-assignment for
κ (1), candidate and rejection review (1–3). Never added to the engineer's total.
**Plus ≈ $13 of model spend (MODELED)**, budget $25 with re-runs, reserve $26 for the extension (see §0.8).
*Assumption:* one competent engineer, ~6 productive hours/day, fluent in Python, comfortable with exact
binomial arithmetic and with a Batch API, working from this document. No context switching.

## P12 · What it settles

**How large the model's role is.** The deliverable is not *"L3 works"* — that is unfalsifiable — but a
number: **of `N` model-proposed regulatory checks, `k` survived a five-gate admission test specified before
the model ran.**

Three sub-questions no earlier phase can answer:

1. **Can a frontier model write an executable check that survives a rejector built to catch the failure
   modes this literature documents?** Every measured system here that works, works because a rejector
   exists; every one that fails, failed because the rejector was absent or fake. P7 and P8 built the
   rejector. P12 is the first time anything is put through it that a model wrote.
2. **Does the surviving set beat work that is free?** Two of the three demolitions in this literature are
   demolitions by baseline. Without B0 ∪ B1 ∪ B2 the result is uninterpretable however many predicates
   survive.
3. **What fraction of the instrument is arithmetically closed at all?** `|A| / |drawn|` — the measured
   decidable fraction of the *IFSCA (Fund Management) Regulations 2025 as amended to 30 January 2026* — is a
   number nobody has, and it is produced by the draw whether or not a single candidate survives.

**`k = 0` is a result.** It would be the first measurement anyone has of whether a frontier model can write
a regulator-grade executable check, and the search establishing that the space is empty is in this corpus
*with its positive control*: across the arXiv abstract index on 10 Aug 2026, zero papers report a
false-failure rate or a mutation kill rate for an executable predicate synthesised from regulatory text, and
the control query returns the known-present paper.

## P12 · Entry criteria

| Build | Requires | Why the edge is real |
|---|---|---|
| **All** | **P7 complete** — G0, G1, G3 both arms, the registry, `admit.py`, the rejection table | An obligation "survives all five gates" is undefined until all five exist. Running against four gates and a placeholder measures a curation, not a model (conflict 4) |
| **All** | **P8 complete — G4 exists and has been *evaluated*, either branch of G-CORPUS** | `beats_baselines` is defined at equal FFR (§0.6), which requires an FFR. **On G-CORPUS's FAIL branch P12 still runs**, using `REGISTER-DERIVED` — and `TEMPLATE-COMPUTED` **only for candidates whose read set does not intersect the generator's computed cells** (§0.6's corpus precondition, adversary F2). A candidate outside that licence gets `comparable = False` and `beats_baselines = False`, and `DECISION.md` carries the qualifier in its headline sentence. What is forbidden is running against a `SELF-AUTHORED` FFR, which the loader refuses anyway — **and, now, against a `TEMPLATE-COMPUTED` FFR that is zero by construction for both arms**, which is the same defect with an admissible provenance label |
| **All** | **P6 complete** — the fault-seeding harness at fault model v3, with its own measured `U/G` **and its `I`, the indeterminate-observability count** | G2's `K/O` is undefined without the observability filter, and `K/G` is a reach measurement, not a quality measurement. **And `U` without `I` is our evaluator's coverage wearing the fault model's name (F18): a mutant whose only propagation path runs through a cell the evaluator cannot compute is not unobservable, it is unmeasured, and pooling the two raises every `K/O` in the direction that flatters us** |
| **All** | **P7-B0 complete** — `textsource`, the pinned regulation blob and D5 | The pool is enumerated over that blob's spans. Moved here from P12-B1 (F35/F41); a build that enumerates `shall` over an unpinned or singly-extracted text is enumerating over a curation |
| **All** | **P4 complete** — the CEL substrate, the envelope, `ast_walker.py` both-ways | A candidate that cannot be parsed cannot be rejected *for the right reason*; it becomes a discard, and the discard pile must be small for the funnel to say anything |
| **B2** | **A clean corpus of some admissible provenance exists** (P8-B1 or the fallback oracles) | Daikon needs a corpus. Its provenance is recorded and is the same corpus the FFRs are computed on, or the comparison is not at equal FFR |
| **B3** | **B1 locked and B2 frozen**, both hashes in `preregistration.lock.json` | This is the whole experiment. A baseline computed after seeing the candidates is not a baseline |

**Not required, deliberately:** P9, P10, P11, P14. The experiment produces a decision record and a funnel,
not a report.

**Explicitly forbidden before this phase:** any line of `src/cdfc/model/propose.py`. Barrier 5, enforced by
`ci/barrier5.sh` from P0.

## P12 · Builds

---

### BUILD P12-B1 — THE PRE-REGISTRATION AND THE DECIDABILITY PILOT (E2) · 2 days

**What it produces.** A content-addressed, committed, hash-published criterion that cannot be edited
afterwards, and the first measurement of how much of the instrument is arithmetically closed.

#### Files created

```
experiments/E6/PREREGISTRATION.md          the criterion. Locked at H0 before the draw
experiments/E6/preregistration.lock.json   {h0, committed_at, git_commit, textsource_sha256,
                                            exclusion_rule_sha256, draw_sha256, strata_sha256,
                                            baselines_sha256, published_in}   APPEND-ONLY
                                            The first two are appended BEFORE draw_sha256 (NC-M34)
experiments/E6/draw.json                   the realised draw: pool hash, seed, ordering rule, indices
experiments/E6/strata.csv                  one row per drawn obligation: ordinal, stratum, assigned_by,
                                           assigned_at, rubric_version, second_assigner, second_stratum
src/cdfc/experiment/__init__.py            module-level assertion: this package is OFFLINE ONLY
src/cdfc/experiment/draw.py
src/cdfc/experiment/prereg.py
src/cdfc/experiment/power.py               exact binomial; supersedes research/scripts/e6_power.py
tools/e6/enumerate_shall.py
docs/measurements/P12-decidability.md

CONSUMED HERE, CREATED AT P7-B0 (see the ruling below) — this build references them and does not build them:
corpus/instruments/fm-regulations-2025.pdf        pinned, content-addressed
corpus/instruments/fm-regulations-2025.text.json  the authoritative extraction + its manifest
src/cdfc/experiment/textsource.py                 dual-extraction agreement over the regulation PDF,
                                                  and the D5 differential
```

#### `textsource` is built at **P7-B0**, five phases earlier, where its first consumer is — **DECIDED**

**Two findings, one move (adversary F35 and F41).** G0's whole mechanism is `source_text.find(quote)` at an
exact character span, and `test_obligations__span_matches_quote` asserts `instrument_text[span] == quote`.
That requires **an authoritative normalised text with stable offsets**, produced by a dual-extraction
agreement harness with a disputed-region exclusion rule. **P7 is five phases before P12, and `plan/04` E7.6
asserts the artifact as a precondition without naming the build that creates it.** Meanwhile this build's
day-1 estimate — *"`textsource`, `enumerate_shall`, the pool and its golden"* — bundles two independent PDF
extractions, a normalised-sentence agreement check, a disputed-region exclusion rule with page numbers, an
`ExtractionManifest`, a `shall` enumerator with an exact chapter-title match that raises, **and** a golden
with first/median/last value assertions, into one day. The extraction half alone is 3–4 days.

> **RULING.** `src/cdfc/experiment/textsource.py`, `corpus/instruments/fm-regulations-2025.pdf`,
> `corpus/instruments/fm-regulations-2025.text.json` and **differential D5** move to a new **P7-B0**,
> **1.5 days**, in `plan/04-phases-qualification.md`, where G0 consumes them. This document then **references
> the artifact under §0.9's deferral rule** — every test here takes the path from
> `cdfc.experiment.textsource.TEXT_SOURCE_PATH`, never a literal — and P12-B1's remaining work (`draw`,
> `power`, `prereg`, the lock, `enumerate_shall`, the negative controls) is **a genuine 2 days**.
>
> *Reason:* a build gate and the artifact it guards must be in the same phase or the earlier one, and G0 is
> the earlier one. *Alternative it beat:* leaving `textsource` at P12-B1 and giving P7's G0 a stub text
> source — rejected because a stub means G0's span check is not exercised on the real instrument until P12,
> which is the *"running against four gates and a placeholder measures a curation, not a model"* failure
> this phase's own entry criteria name.
>
> **`enumerate_shall` stays here**, because the `shall` enumeration is the experiment's *pool*, not G0's
> text, and P7 has no use for it.

#### Public interface, verbatim

```python
# src/cdfc/experiment/draw.py

@dataclass(frozen=True, slots=True)
class Obligation:
    ordinal: int                    # position in the canonical ordering, 0-based
    reg_no: int                     # 51
    sub_clause: tuple[int | str, ...]   # ("1", "a") -- parsed, so ordering is arithmetic not lexical
    quote: str                      # the verbatim sentence containing the `shall`
    char_span: tuple[int, int]      # into the pinned text blob
    source_sha256: str              # the text blob this span indexes into

def enumerate_shall(source: TextSource, *, chapters: frozenset[str]) -> tuple[Obligation, ...]: ...
    # Canonical ordering: (reg_no, sub_clause, char_span[0]). Deterministic.
    # Chapters = those governing scheme operation, valuation and periodic reporting, named
    # verbatim in PREREGISTRATION.md. A chapter title that does not match exactly RAISES;
    # there is no fuzzy chapter match, because a silently-missed chapter is a silently-shrunk
    # denominator and this project has done that four times.

@dataclass(frozen=True, slots=True)
class Draw:
    pool_sha256: str
    seed: int
    order: tuple[int, ...]          # the full PRNG permutation, recorded whole
    drawn: tuple[int, ...]          # the prefix consumed, in order
    stratum_a: tuple[int, ...]      # |A| == 20
    stratum_b_all: tuple[int, ...]  # EVERY B drawn -- the denominator (§0.4)
    stratum_b_generated: tuple[int, ...]   # the first 10 of stratum_b_all -- the generation cap
    stage: Literal[1, 2]

def draw(pool: tuple[Obligation, ...], *, seed: int, strata: StratumOracle,
         target_a: int = 20, generate_cap_b: int = 10, stage: Literal[1, 2] = 1) -> Draw: ...
    # Consumes the PRNG permutation in order, asking `strata` for each drawn obligation, until
    # |A| == target_a. The B cap NEVER stops the draw (§0.4).
    # RAISES PoolExhausted if the pool runs out before |A| == target_a. It never returns short.

def extend(stage1: Draw, *, strata: StratumOracle) -> Draw: ...
    # Continues the SAME permutation without replacement from where stage 1 stopped, until a
    # further 20 Stratum-A obligations are drawn. RAISES ExtensionAlreadyTaken if
    # experiments/E6/EXTENSION/ already exists. There is no third stage (§0.5, NC-M13).
```

```python
# src/cdfc/experiment/power.py    -- exact rational arithmetic; there is no float on this path

N1, RETAIN1, DELETE1 = 20, 6, 2
N2, RETAIN2 = 40, 12
P_GRID: Final = (Fraction(3,20), Fraction(1,5), Fraction(1,4), Fraction(3,10), Fraction(7,20))

def pmf(k: int, n: int, p: Fraction) -> Fraction: ...
def cdf(k: int, n: int, p: Fraction) -> Fraction: ...          # P(X <= k)
def sf(k: int, n: int, p: Fraction) -> Fraction: ...           # P(X >= k)
def retain_probability(p: Fraction) -> Fraction: ...           # two-stage OC, interpretation A (§0.3)
def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]: ...
def power_table() -> PowerTable: ...
    # The exact object rendered into PREREGISTRATION.md. A markdown round-trip test asserts
    # the committed table equals this function's output (contract class, §1.9).
```

```python
# src/cdfc/experiment/prereg.py

def lock(path: Path = Path("experiments/E6/PREREGISTRATION.md")) -> Lock: ...
    # Writes preregistration.lock.json with h0. Refuses if the lock exists and h0 differs.

def append(lock_path: Path, **artefact_hashes: str) -> Lock: ...
    # APPEND-ONLY. Adding textsource_sha256/exclusion_rule_sha256/draw_sha256/strata_sha256/
    # baselines_sha256 is permitted; changing or removing any existing field RAISES
    # LockIsAppendOnly. h0 can never move (§0.6 of the lock).
    # ORDERING IS ENFORCED, not conventional: appending draw_sha256 while textsource_sha256 or
    # exclusion_rule_sha256 is absent RAISES PoolNotYetFixed.  A draw over a pool that can still
    # be re-curated is a draw over a curation.  [NC-M34]

def assert_precedes_first_call(lock_path: Path, runlog: Path) -> None: ...
    # Uses GIT ANCESTRY, not mtimes: the commit introducing every lock field must be an ancestor
    # of the commit introducing the first runlog.jsonl row. Same technique as
    # test_corpus__brief_predates_first_workbook (methodology §6.3 item 3).
    # ADDITIONALLY: the commits introducing textsource_sha256 and exclusion_rule_sha256 must be
    # ancestors of the commit introducing draw_sha256.  [NC-M34]
```

```python
# src/cdfc/experiment/textsource.py   — BUILT AT P7-B0, not here. Reproduced for the consumer, and
#                                       because the exclusion rule below is a P12 pre-registration item.

TEXT_SOURCE_PATH: Final = Path("corpus/instruments/fm-regulations-2025.text.json")   # §0.9: a constant,
                                                                                     # never a literal

@dataclass(frozen=True, slots=True)
class TextSource:
    pdf_sha256: str
    text: str                                   # extractor A's output -- the AUTHORITATIVE spans
    agreement: TextAgreement                    # A vs B over the normalised sentence set
    manifest: ExtractionManifest                # pages read, pages skipped, constructs not understood

def load(pdf: Path) -> TextSource: ...
    # TWO independent extractions. Sentences present in exactly one are recorded in
    # agreement.disputed[] with their page numbers, and every obligation whose span falls inside a
    # disputed region is EXCLUDED FROM THE POOL WITH A STATED REASON and counted.
    # Silently dropping one is the four-times-committed defect, one document class up.
    #
    # THE EXCLUSION RULE AND BOTH EXTRACTOR CONFIGURATIONS ARE INSIDE THE LOCK, and the commits
    # introducing them must be GIT-ANCESTORS of the draw commit.  An exclusion set chosen after
    # seeing which obligations are hard turns `k of 20` into a measurement of OUR CURATION, which
    # is the same result shape as a measurement of the model and is indistinguishable from it in
    # the published number.  [NC-M34]
```

**The pool must be a pool, not a selection — and this is the difference between measuring a model and
measuring ourselves.** Three things decide which obligations the model is asked about: the **named
chapters**, the **canonical ordering**, and the **disputed-region exclusion set**. The first two are already
locked and `enumerate_shall` already raises on an inexact chapter title. **The third was not**, and it is the
one produced by an instrument we wrote, over a document we chose, with a normalisation we defined. If the
exclusion set can move after the draw — or if the extractors can be reconfigured until the pool looks
tractable — then `k of 20` measures the pool's construction and reports it as a property of the model.

> **RULING.** `prereg.append()` carries `textsource_sha256` and `exclusion_rule_sha256`, both appended
> **before** the draw hash and therefore before the first API call, and
> `assert_precedes_first_call` is extended to check them by **git ancestry** exactly as it checks `h0`.
> **`experiments/E6/PREREGISTRATION.md` publishes the excluded-obligation count and its page numbers as part
> of the pre-registration, not as part of the result** — so the reader sees the size of the exclusion before
> the size of the finding. New negative control **NC-M34**, injector
> `exclusions_edited_after_the_draw.py`; admission-side twin: a correctly ordered pair passes.
> **`|drawn|` in the decidable fraction is the pool *after* exclusion, and the excluded count travels with
> it as a third integer** — never folded in, never dropped, per §0.4's rule about caps and denominators.

#### The stratification, and how it is kept honest without a model

The stratum assignment is a **human** judgment and it is load-bearing: it defines Stratum A, which is the
`n = 20` the entire decision rule is written over. Three mechanisations, none of which is a model:

1. **The rubric is written and hashed before the draw.** `PREREGISTRATION.md` §"stratification rubric"
   defines Stratum A as *arithmetically closed — quantities, dates, counts, identifiers or relations among
   fields in the L1-induced schema* and Stratum B as *judgment-bearing or externally dependent*, with three
   worked examples of each drawn from clauses **outside** the chapters being sampled.
2. **The assignment is recorded per obligation with `assigned_by` and `assigned_at`** and is committed
   before the first API call. `strata.csv` rows are append-only.
3. **A second named human independently re-assigns a random 20% of the drawn set** (seeded from the lock)
   and **Cohen's κ is published with its `n`**. This is the substitute measurement methodology §2.8 NC-N02
   prescribes for a human judgment that cannot be negatively controlled, applied here.

**And the check on the stratifier that costs nothing:** Stratum B carries a pre-registered expectation of
**0–1 survivors of 10**. If `k_B/10` is not materially below `k_A/20`, the stratification carried no
information — which is a finding about the human step, is published, and is stated in `DECISION.md`
regardless of what `k_A` was.

#### The power table — normative, exact binomial, and it belongs to `n = 20` and no other `n`

**Stage 1, `n = 20`, retain at `≥ 6`, delete at `≤ 2`:**

| True per-obligation survival rate `p` | `P(X ≤ 5)` retain threshold not met | `P(X ≤ 2)` outright delete | `P(3 ≤ X ≤ 5)` extension fires | `P(X ≥ 6)` retain |
|---:|---:|---:|---:|---:|
| 0.15 | **0.933** | 0.405 | **0.528** | 0.067 |
| 0.20 | 0.804 | 0.206 | **0.598** | 0.196 |
| 0.25 | 0.617 | 0.091 | **0.526** | 0.383 |
| 0.30 | 0.416 | **0.035** ← corrected from 0.036 (§0.2) | 0.381 | 0.584 |
| 0.35 | **0.245** | 0.012 | 0.233 | 0.755 |

**The extension branch — given stage-1 `X ∈ {3,4,5}`, draw 20 more and retain iff `X + Y ≥ 12`:**

| `p` | `X = 3` | `X = 4` | `X = 5` |
|---:|---:|---:|---:|
| 0.15 | 0.001 | 0.006 | 0.022 |
| 0.20 | 0.010 | 0.032 | 0.087 |
| 0.25 | 0.041 | 0.102 | 0.214 |
| 0.30 | 0.113 | 0.228 | 0.392 |
| 0.35 | 0.238 | 0.399 | 0.583 |

**The two-stage operating characteristic (interpretation A) — the numbers that go on a slide:**

| `p` | `P(retain L3)` | `P(delete L3)` |
|---:|---:|---:|
| 0.15 | 0.071 | **0.929** |
| 0.20 | 0.220 | 0.780 |
| 0.25 | 0.451 | 0.549 |
| 0.30 | 0.692 | 0.308 |
| 0.35 | 0.866 | **0.134** |

**What "the extension is sharper" means, stated precisely rather than loosely.** The pooled `≥ 12 of 40`
threshold has *lower* retain probability than `≥ 6 of 20` at low `p` (**0.012 vs 0.067** at `p = 0.15`) and
*higher* at high `p` (**0.795 vs 0.755** at `p = 0.35`); the crossover lies between `p = 0.30` and
`p = 0.35`. It discriminates better in both directions — it is not uniformly harder, and saying so would be
wrong.

**Three consequences that must be written into the pre-registration, not discovered later.**

- **The extension is the modal path** at `p = 0.15–0.25`: it fires 0.528, 0.598 and 0.526 of the time. It is
  budgeted as the expected case (§0.8), not as a contingency.
- **The celebrated figures are `P(X ≤ 5)`, not `P(delete)`.** 0.933 at `p = 0.15` is the probability the
  *retain* threshold is not met. Outright deletion at stage 1 is `P(X ≤ 2) = 0.405`.
- **The revision from the brief's `n = 10, delete below 3` is legitimate because it is entirely *ex ante*
  and moves the threshold in the direction that makes L3 harder to keep** (0.929 vs the old 0.820 at
  `p = 0.15`). *A criterion revision that increases the chance of killing your favourite layer is not a
  rescue.*

**Wilson intervals for the results that can actually be reported.** The interval goes on the slide; the
point estimate never.

| Result | 95% Wilson | Note |
|---|---|---|
| `0/20` | `[0.000, 0.161]` | **`k = 0` is a publishable result, and this is its interval** |
| `2/20` | `[0.028, 0.301]` | the delete boundary |
| `6/20` | `[0.145, 0.519]` | the retain boundary |
| `12/40` | `[0.181, 0.454]` | the extension's retain boundary — half the width at the same rate |

#### What `PREREGISTRATION.md` contains, exhaustively

Nothing is added after `lock()`; the only permitted subsequent write is `append()` of the three artefact
hashes, and that append must itself precede the first API call.

1. The sampling rule: the named chapters, verbatim; the canonical ordering `(reg_no, sub_clause, span)`;
   the PRNG algorithm and the **seed as a literal integer**.
2. The stratification rubric with its six worked examples, and the second-assigner protocol.
3. `k = 10` candidates per obligation per regime; both prompts **verbatim** with their sha256; the model id
   `claude-opus-5`; temperature; the Batch API and prompt-caching configuration.
4. `τ = 0.10`, the fault-model version `v3` and its operator list, the harness version, and the code hashes
   of B0/B1/B2 (appended at B2).
5. The five gates and their fixed order `G0 → G1 → G3-proof → G2 → G3-empirical → G4`.
6. The decision rule, **including the §0.5 conjunction ruling, the §0.6 comparability precondition and the
   verbatim body of `beats_baselines()` with `MARGINAL_FLOOR_NUM/DEN = 1/10`**, with the power tables above.
   `test_contract__preregistration_criterion_is_machine_evaluable` refuses to lock a criterion `decide()` cannot
   consume, so **a prose threshold cannot reach this list** (F30).
7. The corpus provenance of every FFR that will be computed, the statement that a `SELF-AUTHORED` FFR cannot
   be used, **and the statement that a `TEMPLATE-COMPUTED` FFR cannot found a comparison for a candidate
   whose read set intersects the generator's computed cells** — the §0.6 corpus precondition, pre-registered
   rather than discovered when the corpus turns out to be the only one available (F2).
7b. **The pool's construction, in full: the named chapters verbatim, the canonical ordering, both extractor
   configurations, the disputed-region exclusion rule, and the excluded-obligation count with its page
   numbers.** Published as part of the pre-registration, before the result (NC-M34).
8. A commitment to publish `DECISION.md` either way, with a date.
9. **The arguments that will not be accepted as grounds for changing the criterion**, hashed with the rest:
   *"we should have sampled better obligations"* (the rule is pre-registered); *"the clean corpus was
   synthetic"* (known in advance and symmetric with the baselines); *"Stratum B was always going to fail"*
   (hence a separate stratum with a pre-registered expectation of 0–1 of 10); *"the language was wrong"*
   (the Python arm is exploratory, is never executed, and may not change the CEL decision — §P12-B3).
10. The §0.2 correction notice, naming the spec section corrected.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_experiment_draw.py::test_draw__stops_at_twenty_stratum_a` | over a synthetic pool with a known stratum map, `len(draw.stratum_a) == 20` exactly |
| `tests/unit/test_experiment_draw.py::test_draw__b_cap_does_not_stop_the_draw` | a pool where B outnumbers A 5:1 still yields `|A| == 20`, and `len(stratum_b_all) > 10` while `len(stratum_b_generated) == 10` |
| `tests/unit/test_experiment_draw.py::test_draw__pool_exhausted_raises_never_returns_short` | `PoolExhausted` is raised; a 19-obligation return is impossible |
| `tests/unit/test_experiment_draw.py::test_draw__ordering_is_arithmetic_not_lexical` | reg 9 sorts before reg 51; sub-clause `(10)` sorts after `(9)` |
| `tests/unit/test_experiment_draw.py::test_extend__continues_the_same_permutation` | the stage-2 draw's indices are disjoint from stage 1's and are the next prefix of the same `order` |
| `tests/unit/test_experiment_draw.py::test_extend__second_extension_raises` | `ExtensionAlreadyTaken` |
| `tests/unit/test_experiment_power.py::test_power__cdf_at_n_is_exactly_one` | `cdf(n, n, p) == Fraction(1)` — exact, not `1.0 - 1e-16` |
| `tests/unit/test_experiment_power.py::test_power__delete_boundary_at_p030_is_0035` | `round(float(cdf(2, 20, Fraction(3,10))), 3) == 0.035` — the §0.2 correction, pinned |
| `tests/unit/test_experiment_power.py::test_power__pooled_interpretation_reproduces_the_spec` | `1 − retain_probability(0.15) == 0.929` and `1 − retain_probability(0.35) == 0.134` to 3 dp; the fresh-40 interpretation does not |
| `tests/unit/test_experiment_prereg.py::test_lock__h0_cannot_move` | a second `lock()` with different content raises |
| `tests/unit/test_experiment_prereg.py::test_append__removing_a_field_raises` | `LockIsAppendOnly` |
| `tests/unit/test_experiment_textsource.py::test_load__disputed_region_excludes_and_counts` | an obligation whose span falls in a disputed region is absent from the pool **and** present in `manifest.excluded[]` with a reason |

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **The draw is reproducible from the seed alone.** Same `(pool_sha256, seed, strata)` ⇒ byte-identical `draw.json`; a different seed ⇒ a different permutation | random pools of 40–400 obligations, random stratum maps, random seeds | `experiment/draw.py` |
| **`cdf` is non-decreasing in `k` and `sf` non-increasing**, and `cdf(k) + sf(k+1) == 1` exactly for all `0 ≤ k < n` | `n ∈ [1, 60]`, `p ∈` random `Fraction`s in `(0,1)` | `experiment/power.py` |
| **`retain_probability` is non-decreasing in `p`** — a rule that could retain more often at a lower true rate is broken | ordered pairs of `Fraction`s in `(0,1)` | `experiment/power.py` |
| **Stage 2 is narrower.** `width(wilson(12,40)) < width(wilson(6,20))` and, generally, `width(wilson(2k, 2n)) < width(wilson(k, n))` for `0 < k < n` | integer pairs `k < n ≤ 500` | `experiment/power.py` |
| **The B cap never touches the denominator.** For every pool and stratum map, `len(drawn) == len(stratum_a) + len(stratum_b_all)` | as row 1 | `experiment/draw.py` |

Per §7.9: at `max_examples = 50` these explore a small space. Every real defect found in review is pinned as
an `@example` — required, not optional.

#### Validation — golden

**There is no golden against the nine workbooks in this build, and the reason is worth stating:** B1's
subject is the *regulation*, not a workbook. The golden it does have is over the pinned regulation blob.

| Golden test | Subject | Why, and the paired value assertion (R-GOLD-2) |
|---|---|---|
| `tests/golden/test_golden__shall_enumeration.py::test_golden__shall_enumeration__fm_regulations_2025` | `corpus/instruments/fm-regulations-2025.pdf`, pinned by sha256 | The `shall` count over the named chapters is a property of a published file and must never move silently. **Paired value assertion:** the verbatim quote and char span of the first, median and last obligation in canonical order, and the count of chapters matched (which must equal the number named in `PREREGISTRATION.md`) |
| `tests/golden/test_golden__shall_enumeration.py::test_golden__extraction_agreement__fm_regulations_2025` | the same PDF, both extractors | The disputed-sentence count and the excluded-obligation count are pinned with their page numbers. **A disputed count of zero is not assumed to be good news** — a paired positive control asserts the agreement checker fires on a deliberately corrupted second extraction |

The enumerated count is recorded in `docs/measurements/P12-decidability.md` on the first green run; it is
**not** predicted here, because no lane has measured it and inventing it would be exactly the failure this
plan is written against.

#### Validation — differential

**New differential D5**, added to methodology §1.4's table of four. **It is built and blocking at P7-B0
(F35), not here; this build consumes its result and asserts its hash:**

| # | A | B | Disagreement means | Blocking? |
|---|---|---|---|---|
| **D5** | `textsource.load` extractor A (authoritative spans) | extractor B, independently written/configured | The sentence is recorded in `agreement.disputed[]` with its page; obligations inside are excluded from the pool with a stated reason and counted. **Never a silent drop.** | **Yes**, from **P7-B0** (moved: G0's `source.find(quote)` is its first consumer, five phases earlier) |

The two extractors must not share a code path (`test_diff__textsource_paths_are_independent`, the structural
technique of NC-D02c). §7.5's residue applies in full and is stated in `docs/measurements/P12-decidability.md`:
two extractors written by the same person reading the same PDF specification can be wrong the same way.

#### Validation — determinism

`draw.json`, `strata.csv` (modulo the human columns) and the rendered power table must be byte-identical
across `TZ`, `PYTHONHASHSEED`, locale and working directory. `tests/determinism/test_det__draw_bytes_identical`
and `tests/determinism/test_det__power_table_bytes_identical`. **`power.py` uses `Fraction` throughout and
formats through the surface's `fmt()` discipline; there is no float on the path that produces the committed
table.**

#### Validation — negative controls

*Existing catalogue entries relied on, named and not restated:* **NC-D01** (scope truncation drops a
population from the denominator — the mechanism NC-M03 instantiates one level up), **NC-X02** (an absence
reported without a positive control — `assert_absent` is the only sanctioned way to record the disputed-region
count as zero).

*New catalogue entries added by this build*, each appended to `tests/negative/catalogue.yaml` in the §2
shape, `ACTIVE` from the day B1 merges. **`tests/negative/test_nc_model.py` is a new file** and is
registered so `test_nc_meta__no_orphan_guard` sees it.

```yaml
- id: NC-M01
  component: experiment
  break: "the pre-registration hash is published after the first model call, so the criterion could have been written to fit"
  measured_instance: null
  injector: prereg_after_first_call
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M01_preregistration_precedes_first_call
  positive_control: tests/negative/test_nc_model.py::test_nc__M01b_correctly_ordered_pair_passes
  status: ACTIVE

- id: NC-M02
  component: experiment
  break: "PREREGISTRATION.md is edited after the run -- a threshold, a gate, or one of the four inadmissible arguments"
  measured_instance: null
  injector: prereg_edit_threshold
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M02a_h0_mismatch_fails_the_build
    - tests/negative/test_nc_model.py::test_nc__M02b_decision_cites_the_lock_hash
  positive_control: tests/negative/test_nc_model.py::test_nc__M02c_appending_an_artefact_hash_is_allowed
  status: ACTIVE

- id: NC-M03
  component: experiment
  break: "the decidable fraction is computed over a denominator truncated by the Stratum-B generation cap"
  measured_instance: "the same mechanism as NC-D01: a cap on what is processed silently becomes a cap on what is counted"
  injector: truncate_b_denominator
  why_impossible: null
  guard_tests:
    - tests/property/test_prop_experiment_draw.py::test_prop__b_cap_never_touches_the_denominator
    - tests/negative/test_nc_model.py::test_nc__M03_decidable_fraction_uses_all_drawn
  positive_control: tests/unit/test_experiment_draw.py::test_draw__b_cap_does_not_stop_the_draw
  status: ACTIVE

- id: NC-M04
  component: experiment
  break: "|A|/|drawn| is reported as an unbiased estimate, and a Wilson interval on it as exact, under inverse sampling"
  measured_instance: null
  injector: naive_ratio_estimator
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M04a_both_estimators_are_reported_and_labelled
    - tests/negative/test_nc_model.py::test_nc__M04b_interval_carries_the_approximate_label
  positive_control: tests/unit/test_experiment_power.py::test_power__inverse_sampling_estimator_is_a_minus_one_over_n_minus_one
  status: ACTIVE

- id: NC-M05
  component: experiment
  break: "the stratum assignment is made by a model, or by a human after seeing the candidates"
  measured_instance: null
  injector: strata_assigned_by_model
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M05a_assigned_by_must_be_a_person
    - tests/negative/test_nc_model.py::test_nc__M05b_strata_commit_precedes_the_first_call
  positive_control: tests/negative/test_nc_model.py::test_nc__M05c_kappa_is_published_with_its_n
  status: ACTIVE

- id: NC-M34
  component: experiment
  break: "the pool's exclusion set or an extractor configuration is edited after the draw, so k of 20 measures our curation of the instrument and reports it as a property of the model"
  measured_instance: "the disputed-region exclusion rule is produced by an instrument we wrote, over a document we chose, under a normalisation we defined; nothing ordered it before the draw (adversary: the settling experiment must not measure a curation)"
  injector: exclusions_edited_after_the_draw
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M34a_textsource_and_exclusion_hashes_precede_the_draw
    - tests/negative/test_nc_model.py::test_nc__M34b_excluded_count_and_pages_are_in_the_preregistration
  positive_control: tests/negative/test_nc_model.py::test_nc__M34c_a_correctly_ordered_exclusion_and_draw_pair_passes
  status: ACTIVE
```

**Injectors created.** `tests/negative/injectors/prereg_after_first_call.py` (rewrites the git-ancestry
fixture so the lock commit descends from the runlog commit) · `prereg_edit_threshold.py` (changes `6` to `4`
in the locked file) · `truncate_b_denominator.py` (`draw()` returns `stratum_b_generated` as
`stratum_b_all`) · `naive_ratio_estimator.py` (reports only `a/n`, drops the label) ·
`strata_assigned_by_model.py` (writes a model id into `assigned_by`) ·
`exclusions_edited_after_the_draw.py` (rewrites the git-ancestry fixture so the exclusion-rule commit
descends from the draw commit).

**The admission-side positive controls**, because a reject-everything pre-registration checker passes every
negative control: `test_nc__M01b` (a correctly ordered lock/runlog pair must pass), `test_nc__M02c` (a
legitimate `append()` of `draw_sha256` must be accepted — the lock is append-only, not frozen), and
`test_draw__b_cap_does_not_stop_the_draw` (a draw with many Bs must still return 20 As rather than failing).

#### Validation — contract

| Contract | Assertion | Test |
|---|---|---|
| The power table in the pre-registration equals its generator | parse the markdown table out of `PREREGISTRATION.md`, compare set-equal to `power.power_table()` | `tests/contract/test_contract__e6_power.py::test_e6__power_table_matches_preregistration` |
| Discard reasons are closed at six | `DISCARD_REASONS` has exactly six values, and a discard with an unlisted reason is rejected at write time | `tests/contract/test_contract__six_discard_reasons` |
| The lock's field set is closed and append-only | adding an unknown key raises; removing any known key raises | `tests/contract/test_contract__lock_field_set` |

`test_e6__power_table_matches_preregistration` is the function name
`research/scripts/e6_power.py` already cites in its own docstring; this document keeps that name and places
the test in the **contract** class, where "a generated document equals its generator's source" belongs.
**One correction to that script's docstring is recorded here rather than silently:** it says it is superseded
"at P12-B4". The power table is *inside* the pre-registration, so `src/cdfc/experiment/power.py` must exist
at **B1**; B4 re-runs it against the realised `k`.

**Effort: 2 days, and it is a genuine 2 now that `textsource` has moved (F35/F41).** Day 1:
`enumerate_shall` over the **P7-B0 artifact**, the pool, its golden, and the exclusion-hash appends to the
lock. Day 2: `draw`, `power`, `prereg`, the lock, the negative controls. **`textsource`, the two extractions
and D5 are 1.5 days at P7-B0 and are not in this figure** — the work has not disappeared, it has moved to
the phase whose gate needs it. The human stratum assignment runs in parallel on the other person's calendar
and is not in the 2 days.

---

### BUILD P12-B2 — THE THREE FREE BASELINES (E5), RUN BEFORE THE MODEL · 1 day

**What it produces.** The bar. `B0 ∪ B1 ∪ B2`, frozen, content-addressed, hashes appended to the lock
**before the first API call**. Without this build P12 is uninterpretable, because two of the three
demolitions in this literature are demolitions by baseline.

#### Files created

```
src/cdfc/experiment/baselines/__init__.py
src/cdfc/experiment/baselines/b0_native.py       the template's own checkable relations
src/cdfc/experiment/baselines/b1_daikon.py       Daikon at --conf_limit 0.99, container-digest pinned
src/cdfc/experiment/baselines/b2_degenerate.py   "no cell is blank and no cell errors"
src/cdfc/experiment/baselines/marginal.py        marginal kill, per baseline AND for the union
experiments/E6/baselines/B0.json B1.json B2.json  frozen, content-addressed
experiments/E6/baselines/B1.trivia.json           Daikon's trivia output == the degeneracy list
docs/measurements/P12-baselines.md
```

#### Public interface, verbatim

```python
# src/cdfc/experiment/baselines/b0_native.py
def b0_native(schema: TemplateSchema) -> tuple[PredicateEnvelope, ...]: ...
    # The template's OWN checkable relations, emitted as ordinary CEL envelopes with
    # kind='relation'. FME reference: 138 of 505 evaluated cells express a checkable
    # relationship; 35 SUM identities + 3 COUNTIF tallies = 38 of 294 authored expressions.

# src/cdfc/experiment/baselines/b1_daikon.py
def b1_daikon(corpus: CleanCorpus, *, conf_limit: float = 0.99) -> DaikonResult: ...
    # Returns BOTH admitted invariants AND the trivia list. THE TRIVIA LIST IS THE DEGENERACY
    # LIST consumed by G3 (spec II.1.6) -- it is an output of this build, not a by-product.
    # Runs offline in a container pinned BY DIGEST, like LibreOffice and for the same reason.

# src/cdfc/experiment/baselines/b2_degenerate.py
def b2_degenerate(schema: TemplateSchema) -> tuple[PredicateEnvelope, ...]: ...
    # Exactly two envelopes: "no field-surface cell is blank", "no cell carries an error value".
    # The analogue of the NoException baseline that found 68.9% of a published neural oracle's
    # bugs at TWICE its precision. It is in the set BECAUSE it is embarrassing.

# src/cdfc/experiment/baselines/marginal.py
@dataclass(frozen=True, slots=True)
class MarginalKill:
    baseline_id: Literal["B0", "B1", "B2", "B0|B1|B2"]
    observable: int                     # the SHARED denominator O
    killed_by_baseline: int
    killed_by_candidate: int
    killed_by_candidate_only: int       # |K_c \ K_b| -- THE marginal number
    comparable: bool                    # False => the string below renders instead of a number
    incomparable_reason: str | None     # "candidate FFR upper bound exceeds baseline" (§0.6)

def marginal_kill(candidate: AdmittedPredicate, baselines: Baselines,
                  campaign: Campaign, ffr: FfrPair) -> tuple[MarginalKill, ...]: ...
    # Returns FOUR rows: one per baseline AND the union. Reporting only the union is NC-M07.
    # comparable is False, with incomparable_reason set, when EITHER §0.6 precondition fails:
    #   "candidate FFR upper bound exceeds baseline"        (the original)
    #   "FFR CORPUS UNINFORMATIVE FOR BOTH ARMS"            (adversary F2)

MARGINAL_FLOOR_NUM, MARGINAL_FLOOR_DEN = 1, 10        # 10%. Locked into the lock at B1, §0.6

def beats_baselines(rows: tuple[MarginalKill, ...]) -> bool: ...
    # THE ARITHMETIC OF G-SETTLE CRITERION 4, as a pure function of the four rows and nothing else.
    # Body is stated verbatim in §0.6 and in PREREGISTRATION.md; integer arithmetic throughout.
    # decide() takes its VALUE, never the rows, so no argument can enter through this door.
    # [adversary F30: as prose, "greater than B0" had three readings and the weakest was trivial.]
```

#### Two design points that decide whether this build is honest

**B0 is not a straw man, and that is provable.** B0 is a *subset of what the harvest already ships* — the
same 35 `sum_identity` and 3 `tally_identity` predicates. Beating B0 therefore means the model produced
something our own free, model-free harvest did not. A baseline the product already contains cannot be
accused of being built to lose.

**If B1 cannot be run at its specified strength, the claim over B1 is withheld, not softened.** Daikon is
Java, therefore a subprocess, therefore offline-only and container-digest-pinned; its licence is **reported
MIT, LICENSE not opened (SECONDARY)** and it enters `docs/LICENCES.md` as an offline dev-time dependency
with `opened_by` blank. *Switch trigger, stated in advance:* if Daikon cannot be pinned or licensed, **B1
does not run and `beats_baselines` evaluates its B1 term as `False`.** It does **not** fall back to a
hand-written weaker detector, because a weaker baseline makes L3 easier to beat, and a fallback that moves
the result in the direction we would like is not a fallback. `DECISION.md` then states *"beats B0 ∪ B2;
declines to claim it beats B1, which did not run"*.

**The corpus B1 runs on is the corpus the FFRs are computed on**, or the comparison is not at equal FFR.
Its `corpus_id` and `corpus_provenance` are recorded in `B1.json` and asserted equal to G4's by
`test_e6__b1_corpus_matches_g4_corpus`.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_b0_native.py::test_b0__emits_valid_cel_envelopes` | every emitted envelope parses, passes the AST both-ways check, and binds > 0 cells |
| `tests/unit/test_b0_native.py::test_b0__is_a_subset_of_the_harvest` | every B0 envelope's `code_sha256` appears in the harvested set — the anti-straw-man assertion |
| `tests/unit/test_b1_daikon.py::test_b1__trivia_is_returned_not_discarded` | `DaikonResult.trivia` is non-empty on the reference corpus and is written to `B1.trivia.json` |
| `tests/unit/test_b1_daikon.py::test_b1__runs_in_a_digest_pinned_container` | the invocation carries an image digest, not a tag |
| `tests/unit/test_b2_degenerate.py::test_b2__is_exactly_two` | cardinality 2; the set is closed |
| `tests/unit/test_marginal.py::test_marginal__returns_four_rows` | three baselines plus the union, always |
| `tests/unit/test_marginal.py::test_marginal__incomparable_renders_a_string_not_a_number` | when `comparable is False`, `killed_by_candidate_only` is not rendered at all |
| `tests/unit/test_marginal.py::test_marginal__uninformative_corpus_is_incomparable` | **F2.** A `TEMPLATE-COMPUTED` FFR corpus whose `computed_cells` intersect either arm's `read_keys` ⇒ `comparable is False`, reason `FFR CORPUS UNINFORMATIVE FOR BOTH ARMS`, `beats_baselines` `False`. The intersection is **imported from `g4_ffr`**, not re-implemented |
| `tests/unit/test_marginal.py::test_marginal__register_derived_corpus_is_comparable_for_membership_candidates` | the admission-side twin — without it the precondition is a reject-everything rule and no comparison is ever admissible |
| `tests/unit/test_decide.py::test_decide__beats_baselines_is_arithmetic_not_prose` | **F30.** Exhaustive over the `MarginalKill` tuple space at small `observable`: the function's value is asserted at **every** point, including every `comparable = False` combination and the union floor's boundary at exactly `10 · killed_by_candidate_only == observable` |

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **Marginal kill is bounded and is a set difference.** `0 ≤ killed_by_candidate_only ≤ killed_by_candidate ≤ observable`, and `killed_by_candidate_only == len(K_c − K_b)` | random pairs of kill-sets over a mutant id space of 1–5,000 | `baselines/marginal.py` |
| **The union dominates its members.** `killed_by_baseline(B0|B1|B2) ≥ max` over the three | as above | `baselines/marginal.py` |
| **Marginal kill is monotone non-increasing as the baseline grows.** Adding a baseline never increases a candidate's marginal | random baseline subsets | `baselines/marginal.py` |

#### Validation — golden

| Golden test | Workbook | Why that one |
|---|---|---|
| `tests/golden/test_golden__baselines.py::test_golden__b0_count__fme` | FME `7d9a1960…` | The only workbook with all five features live at once, and the one the `138 / 505` and `38 / 294` figures were measured on. **Paired value assertion (R-GOLD-2):** the cell refs of the 3 COUNTIF tallies and of 5 named SUM identities, not only their counts |
| `tests/golden/test_golden__baselines.py::test_golden__b0_is_empty__edr1` | `EDR_1` | Zero formula cells ⇒ B0 is **empty**, and an empty baseline must be published as empty rather than special-cased. It is the case in which "beats the baselines" is trivially true and the decision record must say so |

#### Validation — negative controls

```yaml
- id: NC-M06
  component: experiment
  break: "a baseline is computed, or altered, after the candidates are seen"
  measured_instance: null
  injector: baseline_after_candidates
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M06_baseline_hashes_are_in_the_lock
  positive_control: tests/negative/test_nc_model.py::test_nc__M06b_frozen_baseline_passes
  status: ACTIVE

- id: NC-M07
  component: experiment
  break: "marginal kill is reported only against the union, hiding that one baseline already killed everything"
  measured_instance: null
  injector: marginal_union_only
  why_impossible: null
  guard_tests:
    - tests/unit/test_marginal.py::test_marginal__returns_four_rows
    - tests/negative/test_nc_model.py::test_nc__M07_decision_record_carries_per_baseline_rows
  positive_control: tests/unit/test_marginal.py::test_marginal__union_dominates_members
  status: ACTIVE

- id: NC-M08
  component: experiment
  break: "B2, the degenerate arm, is dropped as trivial -- or its kill count is suppressed because it is high"
  measured_instance: "the NoException baseline found 68.9% of a published neural oracle's bugs at twice its precision"
  injector: drop_b2
  why_impossible: null
  guard_tests:
    - tests/unit/test_b2_degenerate.py::test_b2__is_exactly_two
    - tests/negative/test_nc_model.py::test_nc__M08_b2_kill_count_is_rendered_whatever_its_value
  positive_control: tests/negative/test_nc_model.py::test_nc__M08b_high_b2_kill_is_rendered_not_footnoted
  status: ACTIVE

- id: NC-M09
  component: experiment
  break: "the baselines are straw men -- B0 does not kill a defect it obviously should"
  measured_instance: null
  injector: b0_weakened
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M09_b0_kills_the_seeded_sum_break
  positive_control: tests/negative/test_nc_model.py::test_nc__M09_b0_kills_the_seeded_sum_break
  status: ACTIVE
```

**`NC-M09` is the most important negative control in P12 and it is a positive control wearing a negative
control's clothes.** `test_nc__M09_b0_kills_the_seeded_sum_break` seeds an F-class mutant that breaks one of
the 35 SUM identities on the FME workbook and asserts **B0 kills it**. If B0 does not, every "beats the
baselines" claim in this experiment is manufactured by a broken bar, and the result is void. The entry is
listed with `positive_control` equal to `guard_tests` deliberately: here the *rejection-side* control is the
weakened-baseline injector and the *admission-side* control is the same assertion, which is the only
configuration in the catalogue where that is correct.

**Effort: 1 day.** B0 and B2 are thin functions over the induced schema; B1 is a pinned container
invocation and a parser for its output.

---

### BUILD P12-B3 — THE RUN · 1 day

**What it produces.** 600 candidate envelopes, content-addressed, **including every discard**, and a run log
that makes the whole thing reproducible as a gate campaign even though the generation is not.

#### Files created

```
src/cdfc/experiment/run.py                  the Batch driver. OFFLINE. Never in a request path
src/cdfc/experiment/prompts/correctness.md  verbatim, hashed
src/cdfc/experiment/prompts/completeness.md verbatim, hashed
src/cdfc/experiment/schema_prefix.py        the induced schema as an explicit I/O constraint; cached prefix
src/cdfc/experiment/parse.py                envelope parsing; malformed => a counted discard row
src/cdfc/experiment/client.py               the ONLY module in cdfc/experiment that imports a model client
experiments/E6/runlog.jsonl                 one row per call, written BEFORE and after
experiments/E6/candidates/<sha256>.yaml     600 envelopes, discards included
docs/measurements/P12-run.md
```

#### Public interface, verbatim

```python
# src/cdfc/experiment/run.py

Regime = Literal["correctness", "completeness"]

DISCARD_REASONS: Final = ("not_yaml", "envelope_schema_invalid", "missing_clause_span",
                          "cel_parse_error", "unknown_host_fn", "duplicate_of_earlier_candidate")

@dataclass(frozen=True, slots=True)
class CandidateRecord:
    candidate_sha256: str
    obligation_ordinal: int
    regime: Regime
    draw_index: int                       # 0..9 within the regime
    model_id: str                         # "claude-opus-5"
    model_identity_reported: str | None   # what the API echoed back -- risk R19, alias drift
    prompt_sha256: str
    api_batch_id: str
    requested_at: str
    envelope: PredicateEnvelope | None    # None == malformed
    discard_reason: str | None            # in DISCARD_REASONS iff envelope is None

def propose(draw: Draw, *, k: int = 10, regimes: Sequence[Regime], model_id: str,
            lock: Lock) -> tuple[CandidateRecord, ...]: ...
    # RAISES PreregistrationMissing   if experiments/E6/preregistration.lock.json is absent
    # RAISES PreregistrationMismatch  if h0 does not match the file on disk
    # RAISES ArtefactHashesMissing    if draw/strata/baselines hashes are not in the lock
    # NEVER RETRIES. There is no attempt parameter and the client is built with max_retries=0.
    # A malformed candidate is a discard ROW. The discard pile is data (spec III.3.4).
```

#### Two prompt regimes, and why L4 arbitrates rather than a person choosing

The correctness prompt is not the completeness prompt (`p = 0.008`, Cohen's `d = 1.73`). Both run; the
**gate** decides which produced anything, and the per-regime split is a published result. Feeding the
induced schema in as an explicit I/O constraint is the dominant lever on **structural similarity
(+37–54 percentage points)** in the only published study of statute→executable-model generation
(arXiv:2604.17153, VERIFIED-AT-SOURCE); **that study's *outcome* equivalence tops out at 51–53%**, and its
own caveat is that structural similarity does not guarantee outcome equivalence or the reverse. The
pre-registration carries that caveat verbatim so the intervention is not oversold in the decision record.

#### The optional Python arm, and why it can never change anything

The pre-registration's fourth inadmissible argument is *"the language was wrong"*. **DECIDED: an exploratory
Python arm may be generated, is off by default, is **never executed**, and its output may not be cited in
`DECISION.md`'s decision section.** *Reason:* executing model-written Python is precisely the problem CEL was
chosen to delete rather than contain, and this design has no sandbox for it. The arm's only permitted product
is a structural diff against the CEL arm, published in `docs/measurements/P12-run.md` under the heading
`EXPLORATORY — not executed, not admissible`. `ci/no-python-predicates.sh` (new, stage 2) forbids `exec(`,
`eval(` and `compile(` anywhere under `src/cdfc/`.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_run.py::test_propose__refuses_without_a_lock` | `PreregistrationMissing` |
| `tests/unit/test_run.py::test_propose__refuses_on_h0_mismatch` | `PreregistrationMismatch` |
| `tests/unit/test_run.py::test_propose__has_no_attempt_parameter` | introspect the signature; `max_retries == 0` on the constructed client |
| `tests/unit/test_parse.py::test_parse__malformed_becomes_a_discard_row` | each of the six discard reasons is produced by a crafted input, and none raises |
| `tests/unit/test_parse.py::test_parse__discard_reasons_are_closed` | an unlisted reason is rejected at write time |
| `tests/unit/test_run.py::test_propose__records_the_reported_model_identity` | `model_identity_reported` is populated when the API supplies it and is `null`, never the requested alias, when it does not |

#### Validation — determinism

**Generation is not deterministic and does not need to be** — a weaker model proposes more rejects and cannot
smuggle an unqualified predicate past a gate that requires a measured kill rate and a measured FFR. What
**is** deterministic, and is tested, is everything downstream of the frozen candidates:

`tests/determinism/test_det__gate_run_reproducible_from_frozen_candidates` — running G0→G4 twice over
`experiments/E6/candidates/` produces byte-identical `funnel.json` and `attrition.csv` under varied `TZ`,
`PYTHONHASHSEED`, locale and cwd.

#### Validation — negative controls

```yaml
- id: NC-M10
  component: experiment
  break: "a malformed candidate is silently re-prompted, so the discard rate is understated and the funnel starts from a curated set"
  measured_instance: null
  injector: propose_retry
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M10a_call_count_equals_the_planned_count
    - tests/unit/test_run.py::test_propose__has_no_attempt_parameter
  positive_control: tests/negative/test_nc_model.py::test_nc__M10b_a_malformed_candidate_appears_as_a_discard
  status: ACTIVE

- id: NC-M11
  component: experiment
  break: "the discard pile is dropped from the attrition funnel, so stage 0 reads 600 minus discards"
  measured_instance: null
  injector: funnel_drops_discards
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M11_funnel_stage_zero_equals_the_planned_count
  positive_control: tests/negative/test_nc_model.py::test_nc__M11b_a_run_with_zero_discards_still_reports_the_row
  status: ACTIVE

- id: NC-M12
  component: experiment
  break: "the model alias resolves to a different underlying model mid-batch and the split is not recorded"
  measured_instance: "risk R19: a failure cell moved from 96.6% to 100% on the same prompt and harness under the same alias, with no version bump"
  injector: alias_drift_midbatch
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M12_alias_change_is_flagged_and_split
  positive_control: tests/unit/test_run.py::test_propose__records_the_reported_model_identity
  status: ACTIVE

- id: NC-M13
  component: experiment
  break: "a model is called from anywhere in the qualification path, so the gate adjudicates using the thing it is adjudicating"
  measured_instance: "LLM judges detect false success at AUROC <= 0.65 and 13% recall at a 10% flag rate"
  injector: model_client_in_qualify
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M13a_qualify_import_closure_has_no_model_client
    - tests/negative/test_nc_model.py::test_nc__M13b_gates_run_with_the_socket_blocked
  positive_control: tests/negative/test_nc_model.py::test_nc__M13c_run_module_may_import_the_client
  status: ACTIVE
```

**NC-M13 is P12's instance of NC-A04, moved one phase earlier**, because the qualification path is where a
model judge would do the most damage and it exists from P7. The positive control matters: `experiment/run.py`
*must* be able to import the client, or the guard is banning the wrong thing.

**Effort: 1 day.** The driver is thin; the prompts are written during B1's human lane; the parser reuses
P4's envelope schema.

---

### BUILD P12-B4 — THE DECISION RECORD, THE FUNNEL, AND THE `k = 0` BRANCH · 2 days

**What it produces.** `experiments/E6/DECISION.md`, dated, **published either way**, and the first five-gate
attrition funnel over model-proposed candidates that anyone has published.

#### Files created

```
experiments/E6/DECISION.md         status: FINAL | PENDING(date); cites the lock hash
experiments/E6/funnel.json         stage counts, both strata, both regimes, discards included
experiments/E6/attrition.csv       one row per candidate: gate reached, rejection reason, measured number
experiments/E6/EXTENSION/          created ONLY if stage 2 fires; same shape, one level down
src/cdfc/experiment/decide.py
src/cdfc/experiment/funnel.py
docs/measurements/P12-decision.md
```

#### Public interface, verbatim

```python
# src/cdfc/experiment/decide.py

Verdict = Literal["RETAIN", "DELETE", "EXTEND"]

@dataclass(frozen=True, slots=True)
class SettlingResult:
    k_a: int; n_a: int                      # stage 1: 20;  stage 2: 40 POOLED (§0.3)
    k_b: int; n_b: int                      # the generated Stratum-B cap, <= 10
    wilson_a: tuple[float, float]
    beats_baselines: bool                   # per baseline AND union, under the §0.6 precondition
    per_baseline: tuple[MarginalKill, ...]
    stage: Literal[1, 2]

def decide(result: SettlingResult, *, lock: Lock) -> Decision: ...
    # A PURE FUNCTION of (k_a, stage, beats_baselines) and the thresholds inside `lock`.
    #   stage 1: k_a >= 6 and beats_baselines -> RETAIN
    #            k_a >= 6 and not beats       -> DELETE          (§0.5, locked at B1)
    #            3 <= k_a <= 5                -> EXTEND
    #            k_a <= 2                     -> DELETE
    #   stage 2: k_a >= 12 and beats_baselines -> RETAIN ; otherwise DELETE
    # RAISES CriterionExhausted if stage > 2. There is no third extension, ever.
    # There is NO parameter through which an argument, a rationale or an override can enter.
```

```python
# src/cdfc/experiment/funnel.py

@dataclass(frozen=True, slots=True)
class FunnelStage:
    name: Literal["generated", "parsed", "G0", "G1", "G3_proof", "G2", "G3_empirical", "G4"]
    entered: int
    survived: int
    rejections: tuple[RejectionRow, ...]     # gate, reason, measured number, cells it would have covered

def funnel(records: Sequence[CandidateRecord], campaign: Campaign) -> Funnel: ...
    # INVARIANT, asserted: funnel.stages[0].entered == len(records) == |obligations| * |regimes| * k.
    # Discards enter at "generated" and die at "parsed". Nothing is filtered before stage 0.
```

#### The two attrition numbers, always published side by side

The experiment's bar and the registry's bar are **different tests**, and a document that quotes one has
quoted the wrong one:

| Test | Threshold | Question it answers |
|---|---|---|
| **The settling experiment (G-SETTLE)** | `K/O > 0` **and** marginal kill strictly greater than `B0 ∪ B1 ∪ B2` at the §0.6 precondition | *Can a model-proposed candidate fire at all, and does it beat free work?* |
| **Registry admission** | `K/O ≥ 0.80` on the fault classes the predicate **claims** to cover | *Is this check good enough to be applied to a regulated filing?* |

A predicate at `K/O = 0.05` **survives the experiment and fails the registry**. `funnel.json` carries both
counts and `DECISION.md` prints both in the same paragraph.

#### What `DECISION.md` contains, exhaustively

Inputs and their hashes (lock, draw, strata, baselines, candidates directory) · the five-gate funnel with
every stage's integers · **every candidate including discards** · the Wilson interval at the realised
`(k, n)` · the per-stratum split and the stratification's discriminative value `k_A/20` vs `k_B/10` · the
per-regime split · **the marginal kill over each baseline separately and over the union, with
`beats_baselines`'s arithmetic evaluated term by term so a reader can recompute the boolean** · **the
campaign's SIX integers `G · U · I · O · R · K`, with `I` (indeterminate observability) printed beside
`U/G` wherever either appears** (F18 — `U/G` alone is a measurement of our evaluator presented as a
measurement of the fault model) · **the pool's construction and its excluded-obligation count with page
numbers** (NC-M34) · both attrition numbers · the decision, the date, and the named person who ran it · and
the sentence *"this result is one model, on one instrument, at one date"*.

**On a `DELETE`, the document is identical in shape.** Nothing about the failure branch is thinner: the
funnel is the deliverable and it is more informative when nothing survives, because it says *where* the
candidates died.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_decide.py::test_decide__is_a_pure_function` | called twice with equal inputs, byte-identical output; the signature admits no override |
| `tests/unit/test_decide.py::test_decide__k6_not_beating_baselines_is_delete` | the §0.5 ruling, pinned |
| `tests/unit/test_decide.py::test_decide__three_to_five_extends` | `EXTEND` for `k ∈ {3,4,5}` at stage 1 |
| `tests/unit/test_decide.py::test_decide__stage_three_raises` | `CriterionExhausted` |
| `tests/unit/test_decide.py::test_decide__k_zero_is_delete_and_returns_an_interval` | `DELETE`, `wilson_a == (0.000, 0.161)` to 3 dp |
| `tests/unit/test_funnel.py::test_funnel__stage_zero_is_the_planned_count` | `entered == |obligations| × |regimes| × k`, discards included |
| `tests/unit/test_funnel.py::test_funnel__every_rejection_carries_its_measured_number` | a rejection row with a null measured number fails to construct |

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **The funnel is monotone.** `stages[i].survived >= stages[i+1].entered` is an equality, and `survived <= entered` at every stage | random stage tallies including degenerate all-zero and all-survive cases | `experiment/funnel.py` |
| **`decide` partitions the outcome space.** For every `(k, stage, beats)` in range exactly one of RETAIN/DELETE/EXTEND is returned and no input raises except `stage > 2` | exhaustive over `k ∈ [0,40] × stage ∈ {1,2} × beats ∈ {T,F}` | `experiment/decide.py` |

This second property is **exhaustive rather than sampled** — the input space is 164 points and a property
test that could have been exhaustive and was not is a weaker test than it needed to be.

#### Validation — negative controls

```yaml
- id: NC-M14
  component: experiment
  break: "a third extension is taken, or the extension is re-run after an unwelcome result"
  measured_instance: null
  injector: third_stage
  why_impossible: null
  guard_tests:
    - tests/unit/test_decide.py::test_decide__stage_three_raises
    - tests/unit/test_experiment_draw.py::test_extend__second_extension_raises
  positive_control: tests/unit/test_experiment_draw.py::test_extend__continues_the_same_permutation
  status: ACTIVE

- id: NC-M15
  component: experiment
  break: "the candidate set is selected by 'take all', reproducing SPADE's degenerate operating point"
  measured_instance: "selecting all generated candidates yields 100% coverage and 100% FFR (VERIFIED-AT-SOURCE)"
  injector: select_all_candidates
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M15a_take_all_reproduces_100_100
    - tests/negative/test_nc_model.py::test_nc__M15b_take_all_is_refused_by_the_ilp
  positive_control: tests/negative/test_nc_model.py::test_nc__M15c_the_ilp_selects_a_non_empty_set_when_one_qualifies
  status: ACTIVE

- id: NC-M16
  component: experiment
  break: "a criterion is revised after the result, or DECISION.md cites a lock hash that is not the file's"
  measured_instance: null
  injector: decision_cites_stale_lock
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M16a_decision_lock_hash_matches
    - tests/negative/test_nc_model.py::test_nc__M16b_inadmissible_arguments_cannot_enter_decide
  positive_control: tests/unit/test_decide.py::test_decide__is_a_pure_function
  status: ACTIVE

- id: NC-M17
  component: experiment
  break: "the model ran and DECISION.md was never published -- the publication commitment quietly lapses"
  measured_instance: null
  injector: suppress_decision
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M17a_runlog_without_decision_fails_ci
    - tests/negative/test_nc_model.py::test_nc__M17b_pending_decision_renders_as_an_overdue_open_item
  positive_control: tests/negative/test_nc_model.py::test_nc__M17c_a_delete_decision_publishes_the_same_shape
  status: ACTIVE
```

**`NC-M17` is the one that protects the failure branch.** CI fails if `experiments/E6/runlog.jsonl` exists
and `experiments/E6/DECISION.md` does not. A `DECISION.md` may carry `status: PENDING` with a date, and a
PENDING past the pre-registered publication date renders as an **overdue open item on the report surface**
via P14's `surface/openitems.py` — with its age, never as silence. The failure mode here is not a wrong
answer; it is a result quietly not published because nothing depended on it.

#### Validation — performance

| Budget id | Subject | Baseline | Fail above | Warn above |
|---|---|---|---:|---:|
| `PERF-E6-GATE` | the full five-gate campaign over the frozen 600 candidates | recorded on first green run | baseline + 50% | baseline + 25% |

**The arithmetic that says this is not a problem:** G0, G1 and G3-proof are free-to-cheap and run first, so
few candidates reach G2; the seeding harness runs at **7,946 mutants/second (MEASURED)**, so even a campaign
of 300,000 mutants is ~38 s. The budget exists to catch an ordering regression — a build in which G2 runs
before G0 would show up here as a tenfold blow-out — not because the campaign is expensive.

**Effort: 2 days.** Day 1: `decide`, `funnel`, the exhaustive property, the negative controls. Day 2: the
decision record, the measurements document, the funnel's hand-off shape for P14-B4's Rejected tab.

---

## P12 · The measurement this phase produces

**`k of 20`** — the number of Stratum-A obligations for which at least one of 20 candidates (10 per regime ×
2 regimes) passes all five gates — **with its Wilson interval**. Denominator: 20 Stratum-A obligations.
Warrant **MEASURED**. The interval goes on the slide; the point estimate never.

Four further numbers, none of which exists today:

| Number | Denominator | Warrant | Why it matters |
|---|---|---|---|
| **`\|A\| / \|drawn\|`** — the decidable fraction of the instrument, reported as **three** integers (`\|A\|`, `\|drawn\|`, and the **excluded-obligation count** with its page numbers) plus both estimators under §0.4's inverse-sampling label | `\|drawn\|`, the **full** draw including all Stratum-B | MEASURED | Nobody has measured what fraction of a financial regulation is arithmetically closed. It is produced whether or not a single candidate survives. **The excluded count is never folded in and never dropped** — it is the size of our curation of the instrument, and a reader is entitled to it beside the fraction (NC-M34) |
| **`G · U · I · O · R · K` for the campaign**, with `I` printed beside `U/G` wherever either appears | the generated mutant population `G` | MEASURED | `U/G` alone reports **our evaluator's coverage** under the name of the fault model's observability, and every mutant wrongly moved into `U` **raises** `K/O` — the measurement error correlated with the quantity measured, in the flattering direction (F18) |
| **The five-gate attrition funnel**, stage by stage, discards included | 600 candidates | MEASURED | The first published attrition funnel for model-proposed regulatory checks. **A 20:1 attrition displayed honestly is a stronger demonstration than a settled-fraction bar, because no competitor will show it** |
| **Marginal kill over each baseline separately and over the union**, at the §0.6 precondition | the shared observable set `O` | MEASURED | Two of three demolitions in this literature are demolitions by baseline |
| **The stratification's discriminative value**, `k_A/20` vs `k_B/10` against the pre-registered expectation of 0–1 of 10 | 20 and 10 | MEASURED | It validates the one human judgment the experiment rests on, without a model |

Every one is appended to `reports/validation-ledger.jsonl` with its nine required fields and, being rates,
with `corpus_id`, `corpus_provenance` and `n`.

## P12 · Exit gate — this is gate **G-SETTLE**

Evaluable by someone who did not do the work, by reading `experiments/E6/` after a green CI run:

```
G-SETTLE passes (verdict RETAIN) iff ALL of:
  1. preregistration.lock.json exists; its h0 matches PREREGISTRATION.md; and the commits
     introducing h0, draw_sha256, strata_sha256 and baselines_sha256 are ALL git-ancestors of the
     commit introducing the first runlog.jsonl row.          [test_nc__M01, test_nc__M02a]
  2. DECISION.md exists, is dated, and cites the lock hash that matches.      [test_nc__M16a]
  3. stage 1: k_a >= 6      OR      stage 2: pooled k_a >= 12.
  4. beats_baselines(rows) is True, where beats_baselines is the PURE FUNCTION of §0.6:
        every row comparable (§0.6's FFR precondition AND its corpus precondition), AND
        killed_by_candidate_only > 0 against B0, B1 (or B1 declared not-run) and B2, AND
        union.killed_by_candidate_only * 10 >= 1 * union.observable      i.e. a 10% floor.
     A prose reading of this line is a build failure, not an interpretation.
                                          [test_decide__beats_baselines_is_arithmetic_not_prose,
                                           test_contract__preregistration_criterion_is_machine_evaluable]
  5. funnel.json stage 0 entered == 600, discards included.                   [test_nc__M11]
  6. No third stage exists.                                                   [test_nc__M14]
  7. The campaign publishes SIX integers -- G, U, I, O, R, K -- and DECISION.md prints I beside
     U/G wherever either appears. I is INDETERMINATE_OBSERVABILITY: mutants whose recalculation
     touched a cell the evaluator could not compute, which are excluded from O and are a property
     of OUR APPARATUS, not of the fault model.  A U/G published without I is a measurement of our
     evaluator wearing the label of a measurement of the operator mix.   [adversary F18]
  8. The pool's exclusion set (extractor-disputed regions) and the extractor configuration are
     inside the lock, and the commits introducing them are git-ancestors of the draw commit.
     A pool curated after the draw makes k of 20 a measurement of the curation.  [test_nc__M34]

G-SETTLE fails (verdict DELETE) at:  stage 1 k_a <= 2  |  stage 1 k_a >= 6 without (4)
                                  |  stage 2 pooled k_a < 12  |  stage 2 without (4)
Verdict EXTEND at stage 1 k_a in {3,4,5}: exactly one extension, never again.
```

**In every branch, `DECISION.md` is published on the date the decision was taken.** Publication is not part
of the pass condition; it is part of the gate's *evaluability*, and `NC-M17` fails the build without it.

## P12 · What it kills if it fails

**L3, and only L3.** Nothing above it moves. The gate, the coverage declaration, the closure invariant, the
canaries, the residue set, the probes, the attestation and `verify` are untouched, because none of them ever
depended on a model producing anything. §2 states the resulting system in full.

Two secondary failure branches, each with its smaller system:

- **The pool cannot be built** — the regulation's two extractions disagree so widely that fewer than 20
  Stratum-A obligations survive the disputed-region exclusion. Then `PoolExhausted` fires, no model call is
  made, no money is spent, and the published result is **`|A| < 20` with the disputed-region count and its
  page numbers** — a measurement of the *instrument*, which is a legitimate outcome for a project whose
  thesis is that instruments under-report silently.
- **B1 cannot be run** — `beats_baselines` evaluates its B1 term `False`, `DECISION.md` declines to claim
  L3 beats Daikon, and the decision is made on `B0 ∪ B2` alone with the omission stated in the headline
  sentence. **The claim narrows; it does not soften.**

## P12 · Effort

| Build | Engineer-days | Person-days (other) | Model spend |
|---|---:|---:|---:|
| B1 pre-registration + decidability pilot | 2 | 2 (stratum assignment) + 1 (second assigner, κ) | — |
| B2 the three free baselines | 1 | — | — |
| B3 the run | 1 | — | ≈ $13 (MODELED), budget $25 |
| B4 decision record + funnel | 2 | 1–3 (candidate and rejection review) | reserve $26 if the extension fires (§0.8) |
| **Total** | **6** | **4–6** | **≈ $13, budget $51 including the reserve** |

*Assumption:* one competent engineer as stated at the head of the phase. The person-day column is a
different person's calendar and is never added to the engineer's total. **The extension is the modal path at
`p = 0.15–0.25` and adds ~1 engineer-day and the reserve, not a new phase.**

**`textsource`, the two extractions and D5 are NOT in this table.** They are **1.5 engineer-days at P7-B0**
(§P12-B1's ruling, adversary F35/F41), where G0 consumes them five phases earlier. The 6 days above are
therefore a genuine 6 rather than a 6 containing a hidden 3–4, **and the total programme cost did not fall —
it moved to the phase that needs it, where it is also on the critical path and therefore visible.**

---

# P13 — THE MODEL- AND CLAUSE-BEARING LAYERS, SIZED BY P12

**Effort: 16 engineer-days at full size** · B0 1 · B1 4 · B2 6 · B3 3 · B4 2
**4 engineer-days at `k = 0`** · B0 1 · B3 at its fail-closed size 1 · B4 2 · **B1 does not exist** ·
**B2 deferred** under the trigger in §P13-B2.
*Assumption:* one competent engineer as above, additionally comfortable with document-AI pipelines and with
a legal-XML schema. No context switching.

## P13 · What it settles

**What L3, L1b, L2b and the instrument watcher look like at the size the settling experiment licenses —
including the size zero.**

Four sub-questions:

1. **Can the model-free claim become a property of a running system rather than a design intention?**
   The spec lists `test_no_model_in_verdict_path` as a build gate and records it as **not yet written**.
   B0 writes it, and the claim moves from *specified* to *a property of a running system* on the day it
   lands — and not before.
2. **Is the criterion source citable, versionable and watchable, or only claimed to be?** That is L1b plus
   the watcher, and the watcher is testable against a **realised** event: the 29th IFSCA Authority Meeting
   of 24 July 2026.
3. **Is there a learning problem in the workbook at all?** `mu_base_error_rate`, the key-binding **error
   rate** on population P1 (**not** an accuracy — see P13-B3's name correction and adversary F26),
   decides whether the conformal abstention layer is built — and the prior is that there is not:
   **0 of 3,755** unlocked cells are ambiguous under the address key.
4. **What does a model actually buy, per 100 candidates and per rupee?** Because the gate adjudicates every
   candidate deterministically, **model choice affects yield, never correctness** — which converts an
   unanswerable question into a measurement.

## P13 · Entry criteria

| Build | Requires | Why the edge is real |
|---|---|---|
| **B0** | **P0** (`ci/barrier5.sh` exists and has been observed red) and **P11** for the attestation half of the import closure | B0 is build **zero** because this phase is where a model first enters the codebase and **the guard must precede the thing it guards** |
| **B1** | **`experiments/E6/DECISION.md` exists, is dated, and its verdict is `RETAIN`** | Barrier 5. CI fails the build if `src/cdfc/model/propose.py` exists without the decision record — and, added here, if it exists with a `DELETE` decision record |
| **B2** | **P1 + P2** (the dual-reader discipline and the extraction manifest, reused for the circular corpus) | 399 PDFs are the same class of artifact as nine workbooks: an under-reporting extractor is the failure mode, and the manifest is a first-class output, not a log |
| **B2** | **Not gated on G-SETTLE.** L1b is independently valuable and may be built at either outcome | Its consumers are `obligations.yaml`'s provenance and the watcher's citation resolution, neither of which is L3 |
| **B3** | **A population P1 exists** — real attachments that bind to template keys | **Today it does not.** See the fail-closed default below |
| **B4** | **P7** (the registry, `predicate.state`, the `PROVISIONAL` transition) | The watcher's only output is a state transition on a predicate row |

## P13 · Builds

---

### BUILD P13-B0 — `test_no_model_in_verdict_path`, WRITTEN FIRST · 1 day

**What it produces.** Criterion A6: the gate that turns a design property into a system property. It is
build zero of this phase, before any line of L3, L2b or the watcher.

#### Files created

```
src/cdfc/model/__init__.py           EMPTY of client imports; carries only the package marker
tests/negative/importgraph.py        the AST import-closure walker (shared with P14's surface tests)
tests/negative/test_nc_attest.py     ::test_nc__A04a_no_model_import_reachable
                                     ::test_nc__A04b_verdict_runs_with_no_network
ci/no-model-in-verdict.sh            the cheap grep companion, stage 2
ci/barrier5.sh                       extended: a RETAIN decision is also required for propose.py
docs/GATE-LIVENESS.md                the A6 row, with the date the gate was first observed red
```

#### Public interface, verbatim

```python
# tests/negative/importgraph.py

def import_closure(root: str, *, src: Path) -> frozenset[str]: ...
    # AST-only. Follows `import x`, `from x import y`, and importlib.import_module("<literal>").
    # A NON-LITERAL importlib argument is a HARD ERROR, not a skip: an unresolvable dynamic
    # import is exactly where a client would hide, and skipping it is the swallowed-exception
    # failure (NC-E01) applied to our own guard.  [NC-M18]

BANNED_IN_VERDICT: Final = frozenset({
    "anthropic", "openai", "httpx", "requests", "urllib.request", "http.client", "socket",
    "cdfc.model",                 # the package itself -- one rule, no per-vendor enumeration
})
VERDICT_ROOTS: Final = ("cdfc.evaluate", "cdfc.verdict", "cdfc.probes",
                        "cdfc.selfcheck", "cdfc.attest", "cdfc.surface")
```

#### Why two tests, and why neither is sufficient alone

- **`test_nc__A04a_no_model_import_reachable`** builds the AST import closure of every verdict root and
  asserts `BANNED_IN_VERDICT` is absent. This catches the static import that no test input happens to
  exercise.
- **`test_nc__A04b_verdict_runs_with_no_network`** monkeypatches `socket.socket` to raise and runs a full
  FME filing, asserting `run_state == VALID`. This catches the dynamic call the static walk cannot see —
  `injectors/dynamic_http_in_host_fn.py` puts an `httpx.get` inside a host function precisely to prove the
  static test alone would pass.

**Banning the package `cdfc.model` rather than enumerating vendor clients is the decision that makes the
guard survive contact with a new SDK.** It is also why the watcher moved to `src/cdfc/watch/` (§0.7): with a
uniform rule there is no exception, and an exception in this gate is how this gate dies.

#### Validation — negative controls

*Existing entries relied on, named and not restated:* **NC-A04** in full, with both injectors
(`import_model_client.py`, `dynamic_http_in_host_fn.py`) and its companions `test_no_libreoffice_online`
and `test_no_tlog`.

*New entries added by this build:*

```yaml
- id: NC-M18
  component: model
  break: "a computed importlib.import_module(name) defeats the static import walk, and the walker skips it"
  measured_instance: null
  injector: dynamic_importlib_name
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M18_nonliteral_importlib_is_a_hard_error
  positive_control: tests/negative/test_nc_model.py::test_nc__M18b_literal_importlib_resolves
  status: ACTIVE

- id: NC-M19
  component: model
  break: "L3 source is merged before the decision record exists, or with a DELETE decision record"
  measured_instance: null
  injector: propose_without_decision
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_ci.py::test_nc__M19a_barrier5_fails_without_a_decision
    - tests/negative/test_nc_ci.py::test_nc__M19b_barrier5_fails_on_a_delete_decision
  positive_control: tests/negative/test_nc_ci.py::test_nc__M19c_barrier5_passes_on_a_retain_decision
  status: ACTIVE
```

#### The honesty note this build must carry, verbatim, in `docs/GATE-LIVENESS.md`

> `test_no_model_in_verdict_path` establishes that **no model is called during a verdict**. It does **not**
> establish that the verdict is model-free: if L3 is retained, the predicates were *proposed* by a model at
> build time, and **the gate — not this test — is the boundary**. Anyone quoting "zero model calls" must
> quote it as *zero model calls on the verdict path per filing*, never as *no model influenced this
> verdict*. (Methodology §7.13.)

**This build is required at `k = 0` too.** At `k = 0` there is no L3, but L2b may still exist and the
watcher does; the guard is what keeps `cdfc.model` out of the verdict closure regardless of what is inside
it.

**Effort: 1 day.**

---

### BUILD P13-B1 — L3 CANDIDATE PROPOSAL, AT THE LICENSED SIZE · 4 days · **gated on G-SETTLE**

**What it produces.** The production proposer: the experiment's `run.py` promoted, hardened at the boundary,
and wired to the registry so that every proposed predicate carries its `proposer` record.

**At `k = 0` this build does not exist.** `src/cdfc/model/propose.py` is absent, `ci/barrier5.sh` enforces
its absence, and `src/cdfc/model/` contains only `__init__.py`, `client.py` (reachable from nothing in the
verdict closure) and, if B3's gate said build, `extract/`.

#### Files created

```
src/cdfc/model/propose.py         the production proposer; OFFLINE, Batch, cached prefix
src/cdfc/model/prompts/           the two regimes, versioned and hashed, promoted from experiment/
src/cdfc/model/guard.py           the verbatim-quote provenance guard and the envelope boundary
src/cdfc/model/client.py          the ONLY module under src/cdfc/ that imports a model client
docs/measurements/P13-yield.md
```

#### Public interface, verbatim

```python
# src/cdfc/model/propose.py

def propose(template: TemplateSchema, obligations: Sequence[Obligation], *,
            model_id: str, k: int, regimes: Sequence[Regime], batch: bool = True) -> ProposalBatch: ...
    # NEVER called from a request path. A module-level assertion at import time raises
    # OnlinePathViolation if cdfc.model is reachable from any VERDICT_ROOTS closure.
    # ~600 calls per TEMPLATE VERSION, offline, once. Never per filing.
    # Determinism: none, and none is needed -- a weaker model proposes more rejects and cannot
    # smuggle an unqualified predicate past a gate that requires a measured kill rate and a
    # measured FFR.

# src/cdfc/model/guard.py

def verbatim_guard(candidate: PredicateEnvelope, *, source: str) -> None: ...
    # RAISES VerbatimQuoteNotFound  -- source.find(quote) == -1
    #        QuoteAmbiguous         -- the quote occurs more than once: it does not LOCATE
    #        SpanMismatch           -- the occurrence is not at candidate.clause.span
    # Zero model cost, at the boundary. "Locates deterministically" means UNIQUELY.

def boundary_checks(candidate: PredicateEnvelope, schema: TemplateSchema) -> None: ...
    # 1. verbatim_guard
    # 2. cdfc.predicates.ast_walker.check_both_ways(candidate)   -- P4, reused not rewritten
    # 3. host-function references against the CLOSED registry
    # 4. provisos: cdfc.qualify.g0_scope.provisos(span) must not return UNDECIDED  [fail-closed]
    # Each failure is a DISCARD ROW with a reason, never an exception that ends the batch.
```

#### The four boundary guards, and why each is not a model

This is the local instance of §1. Every guard is a program:

| Guard | Instrument | Cost | What it cannot establish |
|---|---|---|---|
| Verbatim quote locates **uniquely** at the declared span | `str.find` over a pinned blob, twice (to detect a second occurrence) | zero | that the located clause is the right clause |
| `schema_keys` both ways against the CEL AST | `ast_walker` (P4) | zero | — |
| Host functions in the closed registry | set membership | zero | — |
| Provisos implemented **or** declared, **fail-closed on `UNDECIDED`** | the deterministic proviso detector, plus a human-annotated marker set | cheap | recall against marker forms nobody has seen |

**The fail-closed proviso rule is the one that matters.** Frontier models ground clause spans well
(SpanFaith **0.77–0.79**) and wire exception structure badly (Edge-F1 **0.215–0.246** over 2,290
provisions), and **the empirical gates cannot see a dropped proviso** — G1 through G4 all pass a predicate
that implements the main rule and silently omits the exception. A proviso detector that returned "no
provisos found" on an unrecognised marker would therefore fail open in exactly the place the whole gate
order was designed around. `provisos(span) -> Provisos | UNDECIDED`, and `UNDECIDED ⇒ REJECT`.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_guard.py::test_verbatim__missing_quote_raises` | `VerbatimQuoteNotFound` |
| `tests/unit/test_guard.py::test_verbatim__duplicate_quote_raises` | `QuoteAmbiguous` — a quote occurring twice does not locate |
| `tests/unit/test_guard.py::test_verbatim__homoglyph_is_rejected` | the `U+002D → U+2011` variant fails; this is NC-Q11b's fixture, reused |
| `tests/unit/test_guard.py::test_boundary__undecided_proviso_rejects` | fail-closed |
| `tests/unit/test_guard.py::test_boundary__a_correct_handwritten_candidate_passes` | **the admission-side positive control** — without it the guard is indistinguishable from reject-everything |
| `tests/unit/test_propose.py::test_propose__is_not_reachable_from_a_verdict_root` | `OnlinePathViolation` under an injected import |
| `tests/unit/test_propose.py::test_propose__records_the_proposer_block` | every candidate carries `proposer{model_id, date, prompt_sha256}`; the loader refuses one that does not |

#### Validation — negative controls

*Existing entries relied on:* **NC-Q11** (G0 lets a proviso through — all three tests), **NC-Q04** (declared
keys diverge from the AST), **NC-Q02** (a predicate with no qualification record loads), **NC-A04**.

*New entries:*

```yaml
- id: NC-M20
  component: model
  break: "the proposer emits Python instead of CEL, and something somewhere executes it"
  measured_instance: null
  injector: propose_python_arm
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M20a_python_candidate_is_a_discard
    - tests/negative/test_nc_ci.py::test_nc__M20b_no_exec_eval_compile_under_src
  positive_control: tests/unit/test_guard.py::test_boundary__a_correct_handwritten_candidate_passes
  status: ACTIVE

- id: NC-M21
  component: model
  break: "a proposed predicate is admitted without proposer{model_id, date, prompt_sha256}, so a re-synthesis under a drifted model is a mystery rather than a diff"
  measured_instance: "risk R19: a failure cell moved 96.6% -> 100% on the same prompt and harness under the same alias, no version bump"
  injector: strip_proposer_block
  why_impossible: null
  guard_tests:
    - tests/unit/test_propose.py::test_propose__records_the_proposer_block
    - tests/negative/test_nc_model.py::test_nc__M21_loader_refuses_a_proposed_predicate_without_a_proposer
  positive_control: tests/negative/test_nc_model.py::test_nc__M21b_a_harvested_predicate_needs_no_proposer
  status: ACTIVE
```

`NC-M21`'s positive control is the subtle one: a **harvested** predicate legitimately has
`proposer: null`, and a loader that demanded the block from everything would reject the 280 predicates the
product actually ships.

#### Mutation regime

`src/cdfc/model/guard.py` is **Tier Q** (`K/V ≥ 0.85`) and blocking from this phase, because it is the
rejector's boundary. `src/cdfc/model/propose.py` is **Tier S** (`≥ 0.70`) — it is a driver, and mutating a
driver mostly produces timeouts. The phase gate reports both in the required form:
`K/V = a/b (floor) · K/(V−E) = a/(b−E) with E = n adjudicated, arguments in reports/mutation/model.ledger.jsonl · I = i, T = t (ids listed)`.
**A bare percentage fails the review.**

**Effort: 4 days.** Day 1 the boundary guards and their positive control; day 2 promoting the driver and the
`proposer` record; day 3 the negative controls and the mutation triage; day 4 the yield measurement and
`docs/measurements/P13-yield.md`.

---

### BUILD P13-B2 — L1b, THE CLAUSE GRAPH · 6 days · not gated on G-SETTLE

**What it produces.** 399 circulars and the FM Regulations as Akoma Ntoso with an `eId` per clause and an
FRBR URI per instrument; a dated cross-reference extractor; the amendment graph; and the flip of
`registry/obligations.yaml` from `source='hand'` to `source='l1b'` **with ids preserved**.

**At `k = 0` this build is DEFERRED, not deleted, and the trigger for un-deferring it is stated in
advance:** build L1b when the hand-maintained obligations table **exceeds 60 rows** or when **a second
instrument enters the corpus**. *Reason:* L1b's principal consumer at full size is L3's clause-grounded
proposal; its remaining consumers — obligation provenance and the watcher's citation resolution — are served
adequately by a hand table at ~30 obligations, and below that threshold the promoter costs more than it
saves. Above it, hand maintenance is the more expensive and less auditable option. The trigger is recorded
in `docs/OPEN-ITEMS.md` and renders on the report surface as a standing open item with its current row
count, so the deferral is visible rather than forgotten.

#### Files created

```
src/cdfc/clause/__init__.py
src/cdfc/clause/ingest.py        Docling over the native-text circulars; PaddleOCR-VL over the scanned,
                                 run ONCE, offline, frozen and content-addressed
src/cdfc/clause/promoter.py      DETERMINISTIC promotion, no model
src/cdfc/clause/frbr.py          the FRBR URI grammar, ~100 lines, ours
src/cdfc/clause/eid.py           eId minting, stable across re-runs
src/cdfc/clause/xref.py          the dated cross-reference extractor
src/cdfc/clause/amendment.py     the amendment graph
src/cdfc/clause/obligations.py   the hand -> l1b flip, ids PRESERVED
corpus/instruments/MANIFEST.json 399 circulars, content-addressed, with origin_uri and retrieved_at
docs/measurements/P13-promoter-recall.md
```

#### Public interface, verbatim

```python
# src/cdfc/clause/promoter.py

def promote(doc: DoclingDocument, *, frbr: FrbrUri) -> PromotionResult: ...
    # DETERMINISTIC, no model:
    #   numbered headings          -> <section>
    #   (1) / (a) / (i)            -> nested <paragraph>
    #   "Provided that"            -> <proviso>
    # An UNPROMOTABLE region is recorded with its page span in PromotionResult.unpromotable[],
    # and every obligation inside it becomes NO_PREDICATE(no_predicate.rule_ambiguous) until a
    # HUMAN promotes it. It is never dropped and never guessed.

# src/cdfc/clause/frbr.py

def frbr_uri(*, country: str, institution: str, doctype: str, subtype: str,
             year: int, name: str, lang: str, as_at: date) -> FrbrUri: ...
    # "/akn/in-ifsca/act/regulation/2025/fund-management/eng@2026-01-30"
    # Implemented HERE, ~100 lines. `cobalt`/`indigo` report NOASSERTION and are not adopted;
    # `bluebell` is GPL-3.0 (VERIFIED) and is on the hard denylist -- ci/licence-gate.sh.

# src/cdfc/clause/obligations.py

def flip_to_l1b(hand: Path, graph: ClauseGraph) -> FlipResult: ...
    # IDS ARE PRESERVED. An OBL-nnn whose clause the graph cannot locate STAYS source='hand'
    # and appears in FlipResult.unlocated[] -- it is reported, never dropped, never renumbered.
```

#### The recall denominator, and the discrepancy that must be surfaced rather than squashed

The spec gives **8,866 `shall` occurrences across 361 circulars** as the regression denominator, and
separately describes **389 native-text circulars** of 399 (10 scanned). **361 ≠ 389**, and no document says
what the other 28 are.

**Ruling: the denominator is recomputed at B2 against the pinned corpus manifest and published in the form
`<shall_count> across <n> circulars of 399, of which <m> yielded zero and <p> are scanned`.** The
8,866 / 361 figure is carried in `docs/measurements/P13-promoter-recall.md` as the **prior measurement, with
its warrant**, and the two are reconciled in writing. **A divergence is a finding, not a bug to be
squashed** — under this project's own rule, a recount that disagrees with a published count is exactly the
event that must be investigated rather than aligned.

The regression test is then: **a promoter that loses `shall` clauses is losing obligations**, and the count
is the test.

#### OCR, which is a model, and how it is contained

PaddleOCR-VL is a vision-language model. It is the **only** model in this build, it runs **once, offline,
and its output is frozen and content-addressed**, and it is contained by three rules:

1. **Dual-engine agreement, and it is a SCREEN, not an adjudication.** A second OCR engine runs over the
   same 10 documents; a region on which they disagree after a declared normalisation becomes `unpromotable`
   and its obligations are `NO_PREDICATE(no_predicate.rule_ambiguous)`. **Agreement between two models
   establishes nothing about the text** — it removes the regions where at least one is visibly wrong, which
   is a filter, and calling it an adjudicator would make a model the final judge of a model's output, which
   §1 forbids on measured grounds. §1's table is corrected accordingly (this pass): the **Kind** column for
   this row reads `human`, and the screen is named as a screen.
2. **Human confirmation at the point of use, and it is the adjudicator.** A predicate whose clause locates
   only in an OCR'd instrument requires a **human** to confirm the verbatim quote against the page image,
   recorded with an actor id. Not a model — the model produced the text being checked. **The loader refuses
   an admitted predicate whose clause is `source_ocr: true` and which carries no confirmation row**:
   `tests/negative/test_nc_clause.py::test_nc__M25d_an_ocr_clause_without_a_human_confirmation_row_cannot_be_admitted`,
   injector `ocr_confirmation_row_optional.py`; admission-side twin
   `test_nc__M25e_a_confirmed_ocr_clause_is_admitted_at_ADVISORY`. **Without this the containment is a
   convention, and a convention under deadline pressure is the thing the whole §1 table exists to replace.**
3. **A capped severity and an inherited gap.** Such a predicate is admitted at `ADVISORY` at most and
   carries `source_ocr: true`; every predicate whose correctness rests on a **negative full-text search
   result** inherits `circulars_unreadable: 10/399` until the OCR pass is verified, and that field renders
   wherever the predicate renders.

**The residue is named:** if both OCR engines are wrong the same way, none of this catches it. That is
§7.5's shared-misconception class and it is recorded as **NC-N30** with `injector: NONE`.

#### Validation — golden

| Golden test | Subject | Why, with the paired value assertion |
|---|---|---|
| `tests/golden/test_golden__promoter.py::test_golden__shall_preserved__circular_corpus` | the pinned 399-circular manifest | A promoter that loses `shall` clauses is losing obligations. **Value assertion (R-GOLD-2):** the verbatim text and `eId` of five named clauses spanning a section, a nested `(1)(a)(i)`, a proviso, a cross-reference and an amendment target |
| `tests/golden/test_golden__promoter.py::test_golden__amendment_chain_resolves__76_of_82` | the 82 amending circulars | **76 of 82 cite a resolvable target (92.7%, MEASURED)**. The **6 unresolved are asserted to be present and declared**, not absent — a promoter that "fixed" them by guessing would pass a count-only test |
| `tests/golden/test_golden__frbr.py::test_golden__frbr_uri_grammar` | 12 hand-written URI cases | The grammar is ours; the cases include the exact URI in the spec's predicate example |

#### Validation — negative controls

```yaml
- id: NC-M22
  component: clause
  break: "the promoter silently loses `shall` clauses -- it is losing obligations"
  measured_instance: "the prior measurement is 8,866 across 361 circulars; the recount denominator is published in the form (§P13-B2)"
  injector: promoter_drops_provisos
  why_impossible: null
  guard_tests:
    - tests/golden/test_golden__promoter.py::test_golden__shall_preserved__circular_corpus
    - tests/negative/test_nc_clause.py::test_nc__M22_dropped_shall_fails_the_count
  positive_control: tests/negative/test_nc_clause.py::test_nc__M22b_a_correct_promotion_matches_the_count
  status: ACTIVE

- id: NC-M23
  component: clause
  break: "an unpromotable region is dropped instead of recorded, so its obligations vanish rather than becoming rule_ambiguous"
  measured_instance: null
  injector: promoter_drops_unpromotable
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_clause.py::test_nc__M23a_unpromotable_region_is_recorded_with_its_page_span
    - tests/negative/test_nc_clause.py::test_nc__M23b_its_obligations_are_rule_ambiguous
  positive_control: tests/negative/test_nc_clause.py::test_nc__M23c_a_fully_promotable_instrument_has_an_empty_list
  status: ACTIVE

- id: NC-M24
  component: clause
  break: "the hand->l1b flip loses an OBL id, renumbers one, or rebinds one to a different clause"
  measured_instance: null
  injector: flip_renumbers
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_clause.py::test_nc__M24a_every_hand_id_survives_the_flip
    - tests/negative/test_nc_clause.py::test_nc__M24b_unlocated_ids_stay_hand_and_are_reported
  positive_control: tests/negative/test_nc_clause.py::test_nc__M24c_a_located_id_flips_and_keeps_its_quote
  status: ACTIVE

- id: NC-M25
  component: clause
  break: "an OCR'd clause is treated as equal-warrant: no source_ocr flag, no capped severity, no inherited gap"
  measured_instance: "10 of 399 circulars are scanned images -- a permanent declared gap"
  injector: ocr_warrant_erased
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_clause.py::test_nc__M25a_ocr_clause_caps_severity_at_advisory
    - tests/negative/test_nc_clause.py::test_nc__M25b_negative_search_predicates_inherit_the_gap
    - tests/negative/test_nc_clause.py::test_nc__M25d_an_ocr_clause_without_a_human_confirmation_row_cannot_be_admitted
  positive_control: tests/negative/test_nc_clause.py::test_nc__M25c_a_native_text_clause_is_not_capped
  status: ACTIVE

- id: NC-M26
  component: clause
  break: "a GPL-3.0 or NOASSERTION legal-XML library is linked -- bluebell, cobalt or indigo"
  measured_instance: "bluebell is GPL-3.0 (VERIFIED); cobalt and indigo report NOASSERTION"
  injector: import_bluebell
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_licence.py::test_nc__M26_denylisted_legal_xml_fails_the_gate
    - tests/negative/test_nc_clause.py::test_nc__M26b_clause_import_closure_is_clean
  positive_control: tests/negative/test_nc_licence.py::test_nc__L01_gate_fails_against_the_research_venv
  status: ACTIVE
```

**Effort: 6 days.** Day 1 the corpus manifest and Docling ingest with its extraction manifest; days 2–3 the
promoter and its golden; day 4 FRBR, `eId` minting and the flip; day 5 xref and the amendment graph; day 6
the OCR containment, the negative controls and the recall document.

---

### BUILD P13-B3 — L2b ATTACHMENT EXTRACTION AND ITS FEASIBILITY GATE · 3 days full, 1 day fail-closed

**What it produces.** The bound-key extractor for unstructured attachments, its post-hoc deterministic key
check, and **the decision, with its arithmetic, about whether the conformal abstention layer exists at all**.

#### Files created

```
src/cdfc/model/extract/__init__.py
src/cdfc/model/extract/bind.py       provider-native structured output; key: Literal[*L1_KEYS]
src/cdfc/model/extract/postcheck.py  the post-hoc deterministic key check -- KEPT though redundant
src/cdfc/model/extract/mu.py         the key-binding accuracy measurement on population P1
src/cdfc/model/extract/abstain.py    the conformal layer -- EXISTS ONLY IF the gate says BUILD
experiments/E10/DECISION.md          the conformal feasibility decision, dated, published either way
docs/measurements/P13-mu.md
```

#### Public interface, verbatim

```python
# src/cdfc/model/extract/mu.py

@dataclass(frozen=True, slots=True)
class MuResult:
    correct: int
    n_bindings: int
    n_filings: int                 # THE exchangeable unit. n = F, NEVER 3755*F.
    mu_base_error_rate: float      # A BASE ERROR RATE, NOT AN ACCURACY -- the floor formula only
                                   # closes that way.  THE FIELD IS NAMED FOR WHAT IT IS, because
                                   # `mu` alone was read as an accuracy in plan/00 §6 and §10 and
                                   # the two readings INVERT the gate (adversary F26).
                                   # There is no field named `mu` anywhere; the rename is the fix.
    floor_at_alpha_005: float      # max(0.0, (mu_base_error_rate - 0.05) / 0.95)
    decision: Literal["BUILD", "BUILD_AND_HEADLINE_ABSTENTION", "DO_NOT_BUILD", "NOT_MEASURABLE"]

def measure_mu(population_p1: Sequence[AttachmentCase]) -> MuResult: ...
    # RETURNS decision="NOT_MEASURABLE" and mu_base_error_rate=nan when len(population_p1) == 0.
    # NOT_MEASURABLE resolves the gate to DO_NOT_BUILD (fail-closed). See below.
    # test_contract__mu_is_an_error_rate asserts decision == "DO_NOT_BUILD" at 0.9, which is 90%
    # ACCURACY under the misreading and would BUILD.  One assertion; it is the whole gate.  [F26]

# src/cdfc/model/extract/bind.py

def bind(attachment: bytes, keys: frozenset[str], *, model_id: str) -> Fact | Abstention: ...
    # RETRY IS IMPOSSIBLE, NOT MERELY BANNED: the function takes no attempt parameter and the
    # client is constructed with max_retries=0. A Fact produced on attempt k>1 cannot exist.
    # A transient failure yields NOT_RUN(not_run.source_unreadable), never a second call.
    # Skipped ENTIRELY when a filing has no attachment -- the normal case, marginal cost $0.00.
```

#### The gate, its arithmetic, and its fail-closed default

**G-CONFORMAL:** measure `mu_base_error_rate`, apply the forced-abstention floor `r ≥ (μ − α)/(1 − α)` at
`α = 0.05`:

**NAME CORRECTION, and it inverts the gate (adversary F26).** `plan/00-decomposition.md` §6 and §10 call
`μ` *"the key-binding **accuracy** on population P1"* and set the thresholds `μ ≤ 0.30`, `μ ≤ 0.10 ⇒ build`.
Under that reading the rule says **build the layer when accuracy is at most 10%**, which is the opposite of
the intent and of the arithmetic below — the floor formula `r ≥ (μ − α)/(1 − α)` only closes when `μ` is an
error rate. **`06` is right and `00` is what `ci/GATES.md` will be transcribed from**, and a reader who has
not opened this document will look there.

> **RULING: the field is `mu_base_error_rate` everywhere — code, gate table, `docs/measurements/P13-mu.md`,
> `experiments/E10/DECISION.md` and `plan/00` §6 and §10, corrected in the same commit.** The name carries
> the semantics so the gate cannot be transcribed backwards. Its test is
> `tests/contract/test_contract__mu_is_an_error_rate` — **assert `decision == "DO_NOT_BUILD"` at
> `mu_base_error_rate = 0.9`**, which is 90% *accuracy* under the wrong reading and would `BUILD`. One
> assertion, and it is the only thing standing between a transcription error and a shipped abstention layer
> built on a 90% error rate.

| `mu_base_error_rate` (base error rate) | Floor `r` | Decision |
|---:|---:|---|
| 0.05 | 0.0000 | **BUILD** |
| 0.10 | **0.0526** | **BUILD** (the boundary) |
| 0.20 | 0.1579 | **BUILD AND SHIP THE ABSTENTION RATE AS THE HEADLINE** |
| 0.30 | **0.2632** | boundary: at `μ > 0.30`, **DO NOT BUILD** |
| 0.40 | 0.3684 | DO NOT BUILD |

**The input does not exist today, and the plan says so.** Population P1 is *a value in an attached PDF that
must bind to a template key*, and it requires real filings with real attachments. **No real filed FME return
is public**, and P3 (filer deviation) is `UNMEASURED` for the same reason.

**Ruling: `NOT_MEASURABLE` resolves the gate to `DO_NOT_BUILD`.** The honest product statement is
*"cross-document binding is unchecked"*, it appears in the Unchecked panel with its reason code, and
`experiments/E10/DECISION.md` is published with `decision: DO_NOT_BUILD, basis: NOT_MEASURABLE` and a dated
statement of **what would make it measurable: a `REAL-PARTNER` corpus** — which is the same open item as
Person A (spec G10). *Reason:* the alternative is building a distribution-free machinery whose coverage
guarantee is **void, not degraded**, under a known-violated exchangeability assumption — and quoting a
finite-sample guarantee under a violated assumption is a **stronger error than a loose FFR, because it
borrows a theorem**.

**This is why B3 is 1 day at the fail-closed size and 3 days at full size**, and the difference is not a
matter of effort estimation: 1 day builds `bind`, `postcheck`, the skip path and the decision record; the
extra 2 days build `abstain.py`, which is only reachable when a corpus that does not exist arrives.

#### The two key checks, both kept

Provider-native structured output types `key` as `Literal[*L1_KEYS]`, so an off-schema key is outside the
reachable token space at generation. The post-hoc deterministic key check is **kept anyway**, and the reason
is not redundancy: **whether provider-native constraint is guaranteed or best-effort is UNVERIFIED**, and
the post-hoc guard is *the one you can prove to a reviewer*. `postcheck.py` is a set-membership test in four
lines and it is the version that appears in the audit trail.

#### Validation — contract

| Contract | Assertion | Test |
|---|---|---|
| `mu` is an **error rate**, and no transcription can invert the gate | `measure_mu` on a population with `mu_base_error_rate == 0.9` returns `decision == "DO_NOT_BUILD"`; and the field name `mu` (bare) does not exist in `src/cdfc/model/extract/` | `tests/contract/test_contract__mu_is_an_error_rate` (F26) |
| The gate table in `docs/measurements/P13-mu.md` equals its generator | parse the markdown table, compare set-equal to the floor function evaluated on the same grid | `tests/contract/test_contract__conformal_floor_table_matches_its_generator` |

#### Validation — negative controls

*Existing entries relied on:* **`test_contract__model_extract_cannot_pass`** (`method='MODEL_EXTRACT' AND
state='PASS'` rejected at write time), **`test_nc__Q08d_n_is_filings_not_cells`**.

```yaml
- id: NC-M27
  component: model
  break: "retry is enabled in L2b -- silent retry manufactures exactly the clean verdict this product refuses"
  measured_instance: null
  injector: extract_retry
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M27a_bind_has_no_attempt_parameter
    - tests/negative/test_nc_model.py::test_nc__M27b_transient_failure_yields_NOT_RUN
  positive_control: tests/negative/test_nc_model.py::test_nc__M27c_a_first_attempt_success_returns_a_fact
  status: ACTIVE

- id: NC-M28
  component: model
  break: "the post-hoc key check is removed because constrained decoding 'guarantees' the key"
  measured_instance: "whether provider-native constraint is guaranteed or best-effort is UNVERIFIED"
  injector: drop_postcheck
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M28_offschema_key_is_rejected_after_generation
  positive_control: tests/negative/test_nc_model.py::test_nc__M28b_an_onschema_key_survives_the_postcheck
  status: ACTIVE

- id: NC-M29
  component: model
  break: "mu is computed over cells, so n reads 3,755 x F and the interval collapses"
  measured_instance: "the exchangeable unit is the FILING"
  injector: mu_over_cells
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M29_mu_reports_n_filings
  positive_control: tests/negative/test_nc_model.py::test_nc__M29b_n_bindings_is_reported_separately
  status: ACTIVE

- id: NC-M30
  component: model
  break: "an unmeasurable mu resolves the gate to BUILD, or to silence, instead of to DO_NOT_BUILD"
  measured_instance: "population P1 requires real filed returns with attachments; none is public"
  injector: mu_unmeasurable_builds
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_model.py::test_nc__M30a_not_measurable_is_do_not_build
    - tests/negative/test_nc_model.py::test_nc__M30b_e10_decision_is_published_with_its_basis
  positive_control: tests/negative/test_nc_model.py::test_nc__M30c_a_measured_low_mu_builds
  status: ACTIVE
```

**Effort: 3 days full, 1 day fail-closed.** The fail-closed day: `bind`, `postcheck`, the skip path, the
`NOT_MEASURABLE` branch, `experiments/E10/DECISION.md`, and the Unchecked-panel entry.

---

### BUILD P13-B4 — THE INSTRUMENT-STREAM WATCHER · 2 days

**What it produces.** The only mechanism in the design that would have caught **24 July 2026** — and a
measurement of its own coverage, including its gaps.

#### Files created

```
src/cdfc/watch/__init__.py        NOT under model/ -- the watcher uses no model (§0.7)
src/cdfc/watch/fetch.py           daily content hash of three endpoints, redirect-aware
src/cdfc/watch/diff.py            diff-and-flag. Never NLP
src/cdfc/watch/cite.py            does a new instrument cite a regulation a predicate claims?
src/cdfc/watch/quarantine.py      PROVISIONAL transitions. NEVER re-admits
src/cdfc/cli.py                   `cdfc watch` subcommand
fixtures/synthetic/watch/          before/after page snapshots for the 24 July 2026 replay
docs/measurements/P13-watch-coverage.md
```

#### Public interface, verbatim

```python
# src/cdfc/watch/fetch.py

WATCHED: Final[tuple[WatchTarget, ...]]     # the circular list, the Authority-meeting page, the
                                            # download page. Exact URIs resolved at P13 and recorded
                                            # in the run manifest.

@dataclass(frozen=True, slots=True)
class Observation:
    observed_at: str
    endpoint: str
    final_url: str | None            # AFTER redirects -- a changed final_url is a GAP, not a change
    content_sha256: str | None       # None == the fetch FAILED
    changed: bool | None             # None == UNKNOWN, because the fetch failed
    gap_since: str | None
    predicates_flagged: tuple[str, ...]

    def __post_init__(self) -> None:
        # STRUCTURAL: "no change" is UNREPRESENTABLE on a failed fetch.
        if self.content_sha256 is None and self.changed is not None:
            raise UnobservedDayIsNotAQuietDay

def observe(now: datetime) -> tuple[Observation, ...]: ...

# src/cdfc/watch/quarantine.py

def flag(obs: Observation, registry: Registry) -> tuple[str, ...]: ...
    # Any new instrument citing a regulation a predicate claims to implement -> PROVISIONAL,
    # AUTOMATICALLY AND PESSIMISTICALLY.
    # PESSIMISM RULE: an instrument whose citations CANNOT BE PARSED flags EVERY predicate
    # citing that instrument's own regulation family, not zero.  [NC-M33]
    # There is NO code path in this module that sets state=ACTIVE. Clearing requires
    # `cdfc admit --clear` with a human actor id and a decision-record hash. THE WATCHER
    # NEVER RE-ADMITS.
```

#### The type-level trick, and why it is the build's core

`Observation.__post_init__` makes `changed = False` **unconstructible** on a failed fetch. A fetch failure is
therefore a **gap with a duration**, never a quiet day, and the guarantee is structural rather than a
convention someone must remember. This is the same move as P14's `Hero` dataclass with no default for
`admission`, applied to the one place where a silent absence is a compliance event.

The **redirect rule** is the same defect one level over: a `200` served after a redirect to a *different*
page is not evidence about the page we meant to watch. The project's own near-miss is the shape —
`EncryptDId` returned HTTP 302 on every record forever and yielded an honest-looking absence.

#### The 24 July 2026 replay — this build's headline validation, and it needs no model

**`tests/negative/test_nc_clause.py::test_nc__X05d_july_2026_would_have_fired`**: given a before/after
snapshot pair spanning the 29th IFSCA Authority Meeting — which decided that NAV periodicity for close-ended
Restricted Schemes *"may be enhanced by the FME from semi-annual to annual, subject to prior approval of at
least 75% of the investors in the scheme by value of their investments"* — the watcher must move the
NAV-frequency predicate to `PROVISIONAL`.

**If the two dated pages cannot be retrieved, the fixture is RECONSTRUCTED and labelled.** It is built from
the recorded decision text (VERIFIED-AT-SOURCE in the spec), carries `CDFC_SYNTHETIC = true` and
`CDFC_PROVENANCE` in `/docProps` or its sidecar per methodology §6.4, its filename carries the token
`reconstructed`, and the test's own name and output carry the word. **It is never presented as an archival
capture.**

**Its companion is the existing `test_nc__X05c_V5_alone_does_not_catch_a_rule_change`**, which asserts the
NAV-frequency predicate's `kill_case`, built against the semi-annual rule, **still passes** after the rule
change — because the mutant and the predicate moved together. Together the two tests say the thing that
matters: **V5 catches "the artifact moved under us"; V6 catches "the rule moved under us"; neither alone is
sufficient, and the residual class — the rule moved *and* the witness moved with it — is caught by neither
and is named.** A test that documents a limit is worth more than a test that hides it.

#### Validation — negative controls

*Existing entries relied on, in full:* **NC-X05** with `test_nc__X05a` (a template hash bump moves affected
predicates to `PROVISIONAL`, they still run, their numbers are hidden, they leave the settled numerator, and
the settled fraction **falls**), `test_nc__X05b` (a watch gap is not "no change"), `test_nc__X05c` (V5 alone
is insufficient), and its two injectors.

```yaml
- id: NC-M31
  component: watch
  break: "the watcher re-admits -- it clears a PROVISIONAL it set, so the pessimism is undone by the same job that applied it"
  measured_instance: null
  injector: watcher_clears_provisional
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_clause.py::test_nc__M31a_watch_import_closure_excludes_admit
    - tests/negative/test_nc_clause.py::test_nc__M31b_no_code_path_sets_state_active
  positive_control: tests/negative/test_nc_clause.py::test_nc__M31c_cdfc_admit_clear_with_an_actor_id_works
  status: ACTIVE

- id: NC-M32
  component: watch
  break: "the endpoint redirects to a different page and the 200 is recorded as a successful unchanged observation"
  measured_instance: "the register's EncryptDId key returned HTTP 302 on every record forever and yielded an honest-looking absence"
  injector: watch_follows_redirect_silently
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_clause.py::test_nc__M32_changed_final_url_is_a_gap
  positive_control: tests/negative/test_nc_clause.py::test_nc__M32b_same_final_url_records_a_normal_observation
  status: ACTIVE

- id: NC-M33
  component: watch
  break: "the citation detector is too clever: an instrument whose citations cannot be parsed flags nothing"
  measured_instance: null
  injector: cite_parser_fails_open
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_clause.py::test_nc__M33_unparseable_instrument_flags_the_family
  positive_control: tests/negative/test_nc_clause.py::test_nc__M33b_an_unrelated_instrument_flags_nothing
  status: ACTIVE
```

`NC-M33`'s positive control is what stops the pessimism rule from degenerating into flag-everything: an
instrument that cites a regulation **no predicate claims** must flag nothing. Without it, the watcher is the
flag-everything baseline the whole design exists to reject, wearing a different hat.

#### Validation — determinism and performance

`observe()` takes `now` as a parameter and binds no clock internally; two runs at different wall-clock times
over the same fixture snapshots produce identical `Observation` rows except `observed_at`, which is an
**input** recorded in the manifest. `tests/determinism/test_det__watch_observation_is_a_function_of_its_inputs`.

No performance budget: three HTTP fetches a day is not a hot path, and a budget that cannot fail is not a
budget.

**Effort: 2 days.** Day 1 `fetch`/`diff`/`cite`/`quarantine` and the type-level guarantee; day 2 the
24 July replay fixture, the negative controls and the coverage measurement.

---

## P13 · The measurement this phase produces

| Number | Denominator | Warrant | Note |
|---|---|---|---|
| **Admitted predicates per 100 candidates, and per rupee, by model** | 600 candidates | MEASURED | Converts an unanswerable question — *which model is better here?* — into a measurement, because the gate adjudicates every candidate deterministically, so **model choice affects yield, never correctness**. **At `k = 0` this is `0 per 100` and `0 per rupee`, and it is published** |
| **`mu_base_error_rate`**, the key-binding **error rate** on population P1, with its forced-abstention floor | `n = F` filings, never `3,755·F` | MEASURED, or **`NOT_MEASURABLE`** with the reason and what would fix it | Decides whether the conformal layer exists. Fail-closed. **Never quoted as an accuracy** (F26) |
| **Promoter `shall` recall** against the recomputed denominator | `<n>` circulars of 399, published in the form of §P13-B2 | MEASURED | Includes the reconciliation with the prior 8,866 / 361 figure |
| **Watch coverage** — observed days / elapsed days, with each gap's duration | elapsed days since watch start | MEASURED | The watcher's own honesty metric. **An unobserved day is not a quiet day**, and this number is where that shows |

## P13 · Exit gate

Evaluable by someone who did not do the work:

```
1. test_no_model_in_verdict_path is GREEN, both halves (static closure and blocked socket),
   and docs/GATE-LIVENESS.md records the date it was first observed RED.   [criterion A6]
2. ci/barrier5.sh has been observed to fail on (a) propose.py without a decision record and
   (b) propose.py with a DELETE decision record.                           [NC-M19]
3. If L3 is RETAINED: every proposed predicate carries proposer{model_id, date, prompt_sha256},
   and the loader refuses one that does not.                               [NC-M21]
   If L3 is DELETED: experiments/E6/DECISION.md is published, the five-gate attrition funnel is
   on the predicate-library screen, and src/cdfc/model/propose.py does not exist.
4. experiments/E10/DECISION.md exists with its basis, whichever branch fired. [NC-M30]
   AND test_contract__mu_is_an_error_rate is green: decision == DO_NOT_BUILD at
   mu_base_error_rate = 0.9, and no field named bare `mu` exists under model/extract/.  [F26]
5. The 24 July 2026 replay fires, and its companion X05c shows V5 alone does not.
6. Every Observation with a failed fetch carries gap_since and no `changed` value.  [NC-M32]
6b. If L1b was built: no OCR-sourced clause is admitted without a human confirmation row carrying an
   actor id, and §1's table records the human -- not the dual-engine agreement -- as the
   adjudicator for that row.                                        [NC-M25, test_nc__M25d]
7. If L1b was built: obligation ids are preserved across the flip and unlocated ids are
   reported as source='hand'.   If deferred: docs/OPEN-ITEMS.md carries the trigger and the
   current hand-table row count, and it renders on the report surface.
```

## P13 · What it kills if it fails

**Nothing above it.** Each build fails into a smaller, stated system:

| Build fails | The smaller system |
|---|---|
| **B0** — the guard cannot be written (a dynamic import that cannot be resolved statically, in our own code) | **The claim is withdrawn, not weakened.** "Zero model calls in the verdict path" reverts to a *design intention* on every surface and in the claim register, the un-mechanised commitment is counted and published per P0's rule, and the blocked-socket half ships alone with its limit stated |
| **B1** — L3 cannot be built at the licensed size | See §2. The `k = 0` system, which is the same system minus a scaling story |
| **B2** — the promoter cannot reach the `shall` denominator | **L1b is deferred and `obligations.yaml` stays `source='hand'` permanently.** The cost is that obligation identity is a hand-maintained artifact rather than a generated one; the *watcher still works*, because it flags on citation text, not on a promoted graph. The claim narrows from *"the criterion source is machine-followable"* to *"the criterion source is citable and watchable; the amendment chain is followed by hand"* |
| **B3** — `μ` is unmeasurable or above 0.30 | **The conformal layer does not exist and the product says so**: *"cross-document binding is unchecked"*, with its reason code, in the Unchecked panel. Largely pre-settled anyway: **0 of 3,755** unlocked cells are ambiguous under the address key. There is no learning problem in the workbook |
| **B4** — the watcher cannot be built or the endpoints cannot be watched | **The most expensive failure in this phase, and it must be said plainly.** V6 is the only mechanism that catches a rule change, and V5 provably does not (X05c). Without it, every predicate's `qualified_against.regulation_version` is checked **only** at re-qualification, the re-qualification cadence becomes a manual calendar item recorded in `docs/OPEN-ITEMS.md`, and the report surface carries the sentence *"changes to the instrument stream are not monitored; predicate qualification reflects the circular corpus as at `<date>`"* — permanently, with its age |

## P13 · Effort

| Build | Full | At `k = 0` | Note |
|---|---:|---:|---|
| B0 the guard, written first | 1 | 1 | Required in both branches |
| B1 L3 at the licensed size | 4 | **0** | Does not exist; `ci/barrier5.sh` enforces its absence |
| B2 L1b, the clause graph | 6 | **0 (deferred)** | Trigger: hand table > 60 rows, or a second instrument |
| B3 L2b + G-CONFORMAL | 3 | 1 | 1 day is the fail-closed size, which is the expected case today |
| B4 the instrument watcher | 2 | 2 | Required in both branches; it is what makes the criterion source *watchable* |
| **Total** | **16** | **4** | Matches `plan/00-decomposition.md` §5 exactly |

---

## §2 — THE `k = 0` SYSTEM, IN FULL

**This section exists so that the failure branch is a specification and not an improvisation.** It is
written to be readable on the day `decide()` returns `DELETE`, by someone who needs to know what to build
next and what to say.

### 2.1 What is in the repository

| | At `k = 0` |
|---|---|
| `src/cdfc/model/propose.py` | **Does not exist.** `ci/barrier5.sh` fails the build if it appears |
| `src/cdfc/model/prompts/`, `guard.py` | Do not exist |
| `src/cdfc/model/__init__.py`, `client.py` | Exist, reachable from nothing in the verdict closure; `client.py` is used only by `cdfc/experiment/` and, if B3 built, `model/extract/` |
| `src/cdfc/model/extract/` | Exists at its fail-closed size: `bind`, `postcheck`, the skip path. `abstain.py` does not exist |
| `src/cdfc/clause/` | **Deferred**, with a stated trigger. `registry/obligations.yaml` stays `source='hand'` |
| `src/cdfc/watch/` | **Exists in full.** It is not gated on `k` |
| `experiments/E6/` | Complete: pre-registration, lock, draw, strata, baselines, 600 candidates including discards, runlog, funnel, attrition, **`DECISION.md` dated and published** |
| Everything P0–P11 | **Untouched.** Not one line of the qualification spine depended on a model producing anything |

### 2.2 What the predicate set is

- **280 harvested predicates on the FME workbook and 515 across the nine**, with no model — the
  `cross_sheet_equality` 181, `sum_identity` 35, `membership` 20, `numeric_bound` 13, `integer_bound` 11,
  `same_sheet_equality` 11, `date_bound` 6, `tally_identity` 3 classes — always published with the
  per-workbook distribution attached, never alone.
- **Hand-authored predicates** from the 294 native formula expressions, the 20 resolving vocabularies and
  the statute, entering the registry through the same five gates as anything else.
- **The 25 L6 relations**, human-authored from the artifact's own formula graph, including `TEMPLATE_DIFF` —
  the formula-override differential, **predicate #1**, whose oracle is the regulator's published blank and
  which needs no corpus and no model.
- **Four host functions**, hand-authored, versioned, each with published test vectors and its own mutation
  score.

### 2.3 What still ships, in full

The gate (all five, in order) · the registry with its Merkle root · the eight item states, thirty reason
codes and eight run-level `invalid.*` causes · the seven-term closure invariant · the settled fraction with
its six counts and never as a bare number · the twice-computed denominator · run-time canaries and the
`INVALID` state · **the residue set** · the differential and invariant probes · the attestation, `verify`
and byte identity · the report, the Unchecked panel, the drop screen, the API, the predicate library with
its FFR column and its Rejected tab · the instrument watcher · the transfer measurement across the nine.

**Every one of the three novelty claims survives intact**, because none of them was ever about L3:

1. *No product admits a check into its active set only after measuring its own false-failure rate and its
   kill rate* — that is P7 and P8.
2. *The residue is a theorem, not a coverage gap* — that is P10.
3. *`INVALID` is a liveness proof, not a self-test* — that is P10.

### 2.4 What is lost, stated without softening

**The scaling story for new instruments.** The claim narrows from *"predicates can be proposed for any
instrument and filtered by the gate"* to *"predicates are harvested mechanically from a prescribed template
and authored by hand from its statute, and the gate filters both."* Concretely:

- New obligations that are **not** latent in a template's formulas or validations require human authoring.
  P15's transfer measurement (E4, cost arm) becomes the operative economics of the product, and its
  threshold — human cost per transferred predicate ≤ 0.5× from-scratch authoring — becomes the load-bearing
  number rather than a supporting one.
- L1b's principal consumer is gone, which is why B2 is deferred rather than built.
- The `~600 calls per template version` line disappears from the cost model, and the **model spend of the
  entire product becomes $0.00 per filing and $0.00 per template version** — which is a smaller claim and a
  cleaner one.

### 2.5 What gets published, and it is the point

`experiments/E6/DECISION.md`, on the date the decision was taken, containing:

> **Of 600 candidate regulatory checks proposed by `claude-opus-5` over 20 arithmetically-closed obligations
> drawn under a rule pre-registered and hashed before the first API call, `k = 0` survived a five-gate
> admission test specified before the model ran. 95% Wilson interval `[0.000, 0.161]`.**

Travelling with it, in the same document and on the predicate-library screen's funnel tab:

- **The five-gate attrition funnel**, stage by stage, discards included — *where* the candidates died, which
  is the informative content and is more informative when nothing survives.
- **`|A| / |drawn|`**, the measured decidable fraction of the *IFSCA (Fund Management) Regulations 2025* —
  a number nobody has, produced by the draw and unaffected by the model's failure.
- **The per-baseline marginal kill**, showing exactly which free baseline already did the work.
- **The stratification's discriminative value**, `k_A/20` vs `k_B/10`.
- **Both attrition numbers** — the experiment's bar and the registry's bar — which are different tests.
- The positive control for the novelty of the measurement itself: across the arXiv abstract index on
  10 Aug 2026, zero papers report a false-failure rate or a mutation kill rate for an executable predicate
  synthesised from regulatory text, **and the control query returns the known-present paper**.

**That is a funded, publishable outcome and this plan is written for it.** A 20:1 attrition displayed
honestly is a stronger demonstration than a settled-fraction bar, because no competitor will show it — and a
`600:0` attrition displayed honestly is stronger still.

### 2.6 What the surfaces say

- The predicate library's `kind` column shows no `proposed` rows. **It does not hide the column.**
- The funnel tab renders the experiment's funnel with a header naming the decision, its date and the lock
  hash.
- The settled-fraction-over-time chart is **unaffected** — it never carried a model-proposed predicate.
- The report's strap line, the API's `/v1/predicates` response and the attestation's
  `assessor.components.extractorModel` all carry `null` for the proposer, and `/v1/rejections` returns the
  600 candidates with their rejecting gates.
- `docs/OPEN-ITEMS.md` carries the L1b deferral trigger with the hand table's current row count, and it
  renders with its age.

### 2.7 What it costs the schedule

`plan/00-decomposition.md` §7: at `k = 0` the critical path **re-routes** through the self-check and
attestation spine, and P13 collapses from 16 days to 4.

**CORRECTED, twice, by the adversary pass, and both corrections move the number in the same direction.**

**(a) The spine is ~118 working days, not ~104 (F34).** `plan/05` P10's entry criteria add a real,
well-argued edge that `plan/00` §3.1's graph does not carry: **P10-B2 requires P9-B4 complete**, because
computing the residue before the relations are admitted *overstates* it, which flatters us. With that edge
the chain is `P7 ends 86 → P9 ends 100 → P10-B2 starts 100 → P10 ends ~106 → P11 ends ~116`, tied with the
spine at **~118**, and **P11 is on the critical path rather than off it.** `plan/00` §3.1, §4, §4.1 and §7
carry the edge and the number, and **`plan/00` is the arithmetic of record: this section cites it and does
not restate it.** *(Arbitration **C6**. This section previously read `~114` — the figure computed before
`plan/02` R11 revised the phase efforts to P0 = 8 and P3 = 17. `plan/00` recomputed; arithmetic beats
citation; **~114 is retired**, and the instruction that once stood here telling `plan/00` to carry `~114` is
deleted, because a stale number propagated by instruction is worse than a stale number held alone.)*
*A schedule that is wrong in the failure branch is wrong exactly where it will be read under pressure*, and
this section **is** the failure branch.

**(b) The corpus lane is longer than its own budget says, and by a lot (F37).** *"15–25 person-days,
unchanged, and the longest pole"* is the budget for **30** blind-filled workbooks, which is what `G-CORPUS`
requires and which licenses `ADVISORY` only (`hi(0,30) = 0.1139`). **A single predicate cannot be
`BLOCKING` until `n ≥ 189`** (`hi(0,189) = 0.019920`, `plan/04` §0.9). At the same fill rate that is
**95–160 person-days — four to seven months of one person — which dwarfs the ~118-day engineering path and is
the real critical path of the *product* as opposed to the *paper*.** Both numbers go in `plan/00` §7, side
by side, and then the decision is taken explicitly: **ship with everything `ADVISORY` and say so** (which is
defensible, and which this plan already argues), **or fund the larger corpus**. What is not defensible is a
schedule that shows the corpus finishing while the severity tier it exists to produce remains permanently
undefined. **At `k = 0` this is the only pole that matters, and it does not move with `k`.**

---

## §3 — INDEX OF CATALOGUE ENTRIES ADDED BY THIS DOCUMENT

All entries are appended to `tests/negative/catalogue.yaml` in the methodology §2 shape and are covered by
the four meta-tests. **Two new test files are added and registered so `test_nc_meta__no_orphan_guard` sees
them: `tests/negative/test_nc_model.py` and `tests/negative/test_nc_clause.py`.**

| id | Component | Break, in one line | Build |
|---|---|---|---|
| NC-M01 | experiment | the pre-registration hash is published after the first model call | P12-B1 |
| NC-M02 | experiment | `PREREGISTRATION.md` is edited after the run | P12-B1 |
| NC-M03 | experiment | the decidable fraction is computed over a truncated denominator | P12-B1 |
| NC-M04 | experiment | inverse-sampling estimates and intervals are reported as if exact | P12-B1 |
| NC-M05 | experiment | the strata are assigned by a model, or after seeing the candidates | P12-B1 |
| NC-M06 | experiment | a baseline is computed or altered after the candidates are seen | P12-B2 |
| NC-M07 | experiment | marginal kill is reported only against the union | P12-B2 |
| NC-M08 | experiment | B2, the degenerate arm, is dropped or its high kill count suppressed | P12-B2 |
| NC-M09 | experiment | **the baselines are straw men — B0 does not kill a seeded SUM break** | P12-B2 |
| NC-M10 | experiment | a malformed candidate is silently re-prompted | P12-B3 |
| NC-M11 | experiment | the discard pile is dropped from the funnel | P12-B3 |
| NC-M12 | experiment | model alias drift mid-batch is not recorded or split | P12-B3 |
| NC-M13 | experiment | a model is called from anywhere in the qualification path | P12-B3 |
| NC-M14 | experiment | a third extension is taken | P12-B4 |
| NC-M15 | experiment | "take all" selection reproduces SPADE's 100%/100% point | P12-B4 |
| NC-M16 | experiment | a criterion is revised after the result | P12-B4 |
| NC-M17 | experiment | **the model ran and `DECISION.md` was never published** | P12-B4 |
| NC-M18 | model | a computed `importlib` name defeats the static import walk | P13-B0 |
| NC-M19 | model | L3 source merged without, or against, the decision record | P13-B0 |
| NC-M20 | model | the proposer emits Python and something executes it | P13-B1 |
| NC-M21 | model | a proposed predicate is admitted with no `proposer` block | P13-B1 |
| NC-M22 | clause | the promoter silently loses `shall` clauses | P13-B2 |
| NC-M23 | clause | an unpromotable region is dropped instead of recorded | P13-B2 |
| NC-M24 | clause | the hand→l1b flip loses, renumbers or rebinds an `OBL` id | P13-B2 |
| NC-M25 | clause | an OCR'd clause is treated as equal-warrant | P13-B2 |
| NC-M26 | clause | a GPL-3.0 or NOASSERTION legal-XML library is linked | P13-B2 |
| NC-M27 | model | retry is enabled in L2b | P13-B3 |
| NC-M28 | model | the post-hoc key check is removed as redundant | P13-B3 |
| NC-M29 | model | `μ` is computed over cells rather than filings | P13-B3 |
| NC-M30 | model | an unmeasurable `μ` resolves to BUILD, or to silence | P13-B3 |
| NC-M31 | watch | the watcher re-admits | P13-B4 |
| NC-M32 | watch | a silent redirect is recorded as an unchanged observation | P13-B4 |
| NC-M33 | watch | the citation detector fails open on an unparseable instrument | P13-B4 |
| NC-M34 | experiment | **the pool's exclusion set or extractor configuration is edited after the draw, so `k of 20` measures our curation** | P12-B1 |

**New `injector: NONE` entries.** They were numbered `NC-N11`–`NC-N14`, *"continuing methodology §2.8's
numbering past `07`'s NC-N07…N10"* — a sentence arbitration **C9** retires along with the practice, since
`NC-N07` is itself now a **RETIRED** id (`07`'s entry became `NC-N40`, `02`'s became `NC-N16`) and **ids are
no longer allocated by continuing past somebody else's block: `01` §2 is the sole registry.** This
document's entries are `NC-N30`–`N34` and it references rather than allocates —
**and so were `plan/04` §4.4's and `plan/05` §4's, independently, which
is adversary finding F27 and is a green-build lie rather than a bookkeeping nit: `catalogue.yaml` loads into
a dict keyed by `id`, so the later document's entry silently REPLACES the earlier one while the sweep still
reports `caught == active` and `test_nc_meta__no_orphan_guard` stays satisfied.**

> **DECIDED — the `N` family is partitioned by owning document, as a table in `plan/01` §2:**
> `02` → `N01–N06` · `07` → `N07–N10` · `04` → `N11–N19` · `05` → `N20–N29` · **`06` (this document) →
> `N30–N39`.** The four rows below are **re-keyed from `N11`–`N14` to `N30`–`N33`**, and the superseded ids
> keep their rows in `docs/CATALOGUE-CORRECTIONS.md`. This document additionally claims **`NC-M01–M39`** and
> asserts no other document may define them. Enforced by `test_nc_meta__ids_are_unique` and
> **`ci/catalogue-ids.sh`** — a grep over `plan/*.md` asserting every `NC-` id is *defined* in exactly one
> document and falls inside that document's declared range — both required **at P0-B3, before the first
> entry is written**. *Alternative it beat:* partitioning `catalogue.yaml` per component, which would make
> the collisions harmless; rejected because the four meta-tests are written over one file.

| id | The thing we cannot break mechanically | What it costs |
|---|---|---|
| **NC-N30** | **That two OCR engines do not share a misconception on the 10 scanned circulars.** Both are trained on overlapping data and both may hallucinate the same plausible legal text | Every predicate whose clause locates only in an OCR'd instrument rests on an unquantified extraction error. Mitigations, all partial: capped at `ADVISORY`, `source_ocr: true`, human confirmation against the page image at the point of use, and the permanent `circulars_unreadable: 10/399` gap |
| **NC-N31** | **That the human stratum assignment is correct.** A wrong assignment moves an obligation into or out of the `n = 20` the whole decision rule is written over | `k of 20` inherits an unquantified stratification error. Substitute measurement, not a test: a second named human re-assigns a random 20% and **Cohen's κ is published with its `n`**. κ measures agreement, not truth |
| **NC-N32** | **That the model's proposal distribution is stable enough for `k of 20` to be a property of *models* rather than of *this model on this day*.** Risk R19 is the realised instance: a failure cell moved 96.6% → 100% under the same alias with no version bump | The result is one model, on one instrument, at one date, and `DECISION.md` says so in that sentence. `model_identity_reported` records what the API echoed back; a re-run under a drifted model is then a **diff, not a mystery** — which is containment, not measurement |
| **NC-N34** *(new, this pass)* | **That the pool is the instrument and not our reading of it.** D5 establishes that two extractions agree; it cannot establish that both are right, and the excluded regions, the chapter set and the normalisation are all ours. `k of 20` is therefore a measurement of *the model on the pool we built* | The mechanised part is done — the exclusion rule, both extractor configurations and the chapter list are hashed into the lock **before** the draw, and the excluded count travels with `\|drawn\|` as a third integer (NC-M34). What remains unmechanisable is that the pool is a faithful reading. Substitute: publish the excluded count and its page numbers **in the pre-registration**, so a reader sizes the curation before seeing the finding |
| **NC-N33** | **That the watcher's three endpoints are the right three.** An instrument published somewhere we do not watch is invisible, and its absence is indistinguishable from a quiet day | Watch coverage is measured over *watched* endpoints, which is a self-referential denominator (§7.6 applied to the watcher). The only available instrument is the growth log of `WATCHED`: if endpoints keep being added late, the set is incomplete and the rate is visible. Report it; do not claim it converges |

---

## §4 — WHAT P12 AND P13 CANNOT ESTABLISH

Referenced by name from `plan/01-validation-methodology.md` §7 where the class already exists, and stated
here where it is specific to these two phases.

**Carried from §7, in full force:**

- **§7.1 — a predicate perfectly implemented that encodes the wrong obligation.** G0 proves the quote
  locates uniquely and every proviso is implemented or declared; **nothing here proves the CEL means the
  clause**. The only published study of statute→executable-model generation reaches **51–53% outcome
  equivalence**. This is the largest hole in both phases, it is `NC-N01`, and it means **a predicate can
  clear all five gates and enforce a rule that does not exist.** Only human review at R7 and the attrition
  funnel address it, and neither is a measurement of correctness.
- **§7.2 — any defect the fault model does not contain.** `K/O` licenses exactly one sentence: *"rejects
  `K` of `O` observable defects seeded under fault model v3."* There is **no coupling study for financial
  filing data**; the bridge to real faults does not exist and must not be walked across.
- **§7.13 — the boundary of the model-free claim.** `test_no_model_in_verdict_path` establishes zero model
  calls *during a verdict*. If L3 is retained, the predicates were proposed by a model at build time, and
  **the gate — not the test — is the boundary.**

**Specific to these phases:**

1. **`k of 20` is one model, on one instrument, at one date.** It is not a property of models, of frontier
   models, or of this model next month. Anyone quoting it must quote it with the model id, the API date and
   the instrument. `NC-N32`.
2. **The stratification is a human judgment.** κ measures agreement between two humans, not agreement with
   the world. `NC-N31`.
3. **The decidable fraction is measured over one instrument's named chapters**, under an inverse-sampling
   stopping rule whose interval is approximate, and after excluding obligations in extractor-disputed
   regions. All three qualifiers travel with the number.
4. **The watcher catches *citations*, not *effects*.** An instrument that changes a rule without citing the
   regulation a predicate claims is missed entirely — and in that case the residual class (the rule moved
   *and* the witness moved with it) is caught by neither V5 nor V6. The pessimism rule reduces the class; it
   does not close it.
5. **The 10 scanned circulars are a permanent declared gap** until OCR'd, verified and frozen, and their
   OCR is itself a model output with no deterministic adjudicator (`NC-N30`).
6. **`μ` may be structurally unmeasurable, not merely unmeasured**, because population P1 needs real filed
   returns with attachments and none is public. `NOT_MEASURABLE` is a published state, not a blank.
7. **The negative-control catalogue for these phases was written by the person who wrote the code.**
   §7.6 applies without relief: its denominator is self-referential, and the only instrument is the
   catalogue's append-only growth log.

---

## §5 — DEFINITION-OF-DONE DELTAS FOR THESE TWO PHASES

`docs/DOD-TEMPLATE.md` is filled once per **build**. Four lines need phase-specific instruction, and **three**
new lines are added (two of them by the adversary pass).

| Line | Instruction specific to P12/P13 |
|---|---|
| **B3 (golden: which workbook and why)** | P12-B1 and P12-B2's goldens are over the **regulation** and the **circular corpus**, not the nine workbooks. Write *"n/a — the subject is an instrument, not a template"* and name the instrument golden instead. P12-B2's `test_golden__b0_is_empty__edr1` is the one that does use a workbook, and the reason is that an **empty** baseline must be publishable |
| **C5 (every rejection-side control has an admission-side positive control)** | **The blocking line for these phases.** `NC-M09` (B0 kills a seeded SUM break), `test_boundary__a_correct_handwritten_candidate_passes`, `NC-M21b` (a harvested predicate needs no proposer), `NC-M33b` (an unrelated instrument flags nothing) and `NC-M30c` (a measured low `μ` builds) are each the admission-side twin of a rejection-side control. A build that ships one without the other has built a reject-everything gate |
| **D7 (rates carry corpus_id, provenance, n and a Wilson interval)** | Add: **an inverse-sampling estimate carries the label `APPROXIMATE — inverse sampling, interval not exact`** and both point estimators (§0.4). A bare `20/n` fails the line |
| **H3 (spec claims this build moves from SPECIFIED to BUILT)** | P13-B0 moves *"zero model calls in the verdict path"* from **specified with a gate not yet written** to **a property of a running system**. It is the only place in the whole plan where that sentence may change tense, and the DoD must say so with the date |
| **NEW — J1 (pre-registration integrity)** | For every P12 build: *the lock hash on the day of this build, the git commit that introduced it, **and the command that recomputes the hash from the file***. A hash a reviewer can recompute is evidence; a hash pasted into a PR description is a claim (F31's lesson applied here). A P12 build whose DoD cannot produce both has not established the property the whole experiment rests on |
| **NEW — J2 (the criterion is machine-evaluable, and the pool preceded the draw)** | For every P12 build: `test_contract__preregistration_criterion_is_machine_evaluable` green — **no threshold in `PREREGISTRATION.md` is prose** (F30) — and the git-ancestry chain `textsource_sha256 → exclusion_rule_sha256 → draw_sha256 → first runlog row`, with the four commit shas. A build that cannot show the chain has drawn from a pool that could still be re-curated (NC-M34) |
| **NEW — J3 (no rate rests on a corpus the product computed)** | For every FFR or comparison this phase quotes: the corpus id, its provenance, and the computed `read_keys ∩ computed_cells` result. A `TEMPLATE-COMPUTED` corpus with a non-empty intersection fails the line, and `beats_baselines` must already be `False` (F2, §0.6) |

---

## §6 — THE CLOSING CHECK

Three properties of this document to verify if it drifts.

**One.** **Every model-produced artifact in §1's table has a non-model adjudicator, and the residue column is
non-empty for the rows where it should be.** If a revision adds a model-produced artifact without adding a
row — or fills a residue cell with "none" — it has quietly made a model the final adjudicator, which the
spec forbids on measured grounds (AUROC ≤ 0.65, 13% recall at a 10% flag rate).

**Two.** **The `k = 0` branch is specified to the same depth as the `k ≥ 6` branch.** §2 names the files that
exist, the predicate set, what still ships, what is lost, what is published, what the surfaces say and what
it costs the schedule. If a revision shortens §2, it has converted a pre-committed failure branch into an
improvisation — and *a criterion whose failure branch is improvised is a criterion that will be
renegotiated under pressure.*

**Three.** **Every threshold in this document was written before the thing it judges, and every one of them
is a number a program can read.** `≥ 6 of 20`; `≤ 2 of 20`; one extension at `≥ 12 of 40`;
`mu_base_error_rate > 0.30 ⇒ do not build`; `K/O ≥ 0.80` for the registry; `K/O > 0` plus marginal kill for
the experiment; **the marginal-kill union floor at `1/10` of `observable`**; the §0.5 conjunction ruling;
the §0.6 comparability precondition **and its corpus precondition**; the hand-table trigger of 60 rows for
un-deferring L1b. If a revision moves one, it must move it **in `PREREGISTRATION.md` before the run, with an
argument that the old threshold was wrong, dated** — never by the discovery that it cannot be met. *A
criterion revised after seeing the result is not a criterion.*

**And the second clause of that sentence is new, and it is the adversary pass's contribution (F30).** It is
not enough that a threshold be early; it must be **arithmetic**. `beats_baselines` was written early, hashed
early, and had three readings, of which the weakest was trivially satisfiable — so the lock protected a
sentence rather than a criterion. `test_contract__preregistration_criterion_is_machine_evaluable` makes the prose
form unreachable: **`lock()` refuses to write a criterion `decide()` cannot consume.** If a future revision
of this document introduces a threshold that reads well and does not evaluate, that test is what catches
it, and its absence is what let this one through.

---
---

## REPAIRS APPLIED (adversary pass)

Against `plan/08-adversary.md`, dated 11 August 2026. Every finding that touches P12 or P13 is listed, so a
reviewer can check this document's work without re-deriving the finding. **Every repair below is a test, a
negative control, a changed gate threshold, a new required field or a changed contract.**

| Finding | Sev | The finding, in one line | What changed here | Where |
|---|---|---|---|---|
| **F30** | SERIOUS | G-SETTLE's `beats_baselines` is not evaluable as written — *"greater than B0"* has three readings and the weakest is trivially satisfiable — and it was locked and hashed in that state | **`beats_baselines()` is a pure function with a verbatim body**, integer arithmetic, `all(comparable)` ∧ `all(killed_by_candidate_only > 0)` ∧ a **union floor of `1/10 · observable`** (DECIDED; it beat `> 0` and beat a fraction-of-baseline form that is undefined when the union kills nothing). Criterion 4 of G-SETTLE is restated as that arithmetic; `test_decide__beats_baselines_is_arithmetic_not_prose` is **exhaustive** over the tuple space; **`test_contract__preregistration_criterion_is_machine_evaluable` makes `lock()` refuse a criterion `decide()` cannot consume**, so the prose form is unreachable | §0.6 (ruling + body) · P12-B2 `marginal.py` interface · P12-B2 unit table · **G-SETTLE criterion 4** · `PREREGISTRATION.md` contents item 6 · §6 "Three" |
| **F35** | SERIOUS | P7's G0 needs a pinned, span-addressable regulation text that no build before P12-B1 creates | **`experiment/textsource.py`, the pinned PDF, the text blob and differential D5 move to a new `P7-B0` (1.5 days)** where G0 consumes them; this document **references** them under §0.9's deferral rule via `TEXT_SOURCE_PATH`; D5's "Blocking?" column reads *from P7-B0*; P12 gains a `P7-B0 complete` entry criterion | P12-B1 file list + ruling · `textsource` interface block · differential D5 table · P12 entry criteria |
| **F41** | SERIOUS | P12-B1 at 2 days including a dual-extraction PDF differential that is 3–4 days on its own | Same move. Day 1 is now `enumerate_shall`, the pool, its golden and the lock appends; day 2 is `draw`/`power`/`prereg`/controls. **The work did not vanish — it is 1.5 days at P7-B0 and the effort table says so** | P12-B1 effort · P12 effort table note |
| **F26** | SERIOUS | `μ` is an accuracy in `plan/00` and an error rate in `06`, and G-CONFORMAL's thresholds **invert** between them | Field renamed **`mu_base_error_rate`** everywhere — dataclass, gate table, measurement table, P13 sub-question 3, §6's threshold list — with the correction stated in place and `plan/00` §6 and §10 named for the same commit. **`test_contract__mu_is_an_error_rate`: `decision == DO_NOT_BUILD` at `0.9`**, which is 90% accuracy under the wrong reading and would `BUILD`. Plus a contract test that the floor table equals its generator | P13-B3 (name correction, gate table, new contract table) · P13 what-it-settles 3 · P13 measurement · P13 exit gate 4 · §6 |
| **F27** | SERIOUS | Colliding `NC-N` ids across `04`, `05` and `06`; the later document's entry silently replaces the earlier in a dict keyed by `id` | **`NC-N11`–`N14` re-keyed to `NC-N30`–`N33`** throughout (including the in-text references in P13-B2 and §4); the `N` family is **partitioned by owning document** with `06` claiming `N30–N39` and `M01–M39`; `test_nc_meta__ids_are_unique` and `ci/catalogue-ids.sh` required **at P0-B3** | §3 `injector: NONE` block (range ruling + re-keyed rows) · P13-B2 OCR residue · §4 items 1, 2, 5 |
| **F34** | SERIOUS | The `P9-B4 → P10-B2` edge is absent from `plan/00`'s graph, and it moves P11 off the off-path list — in the branch this document is written for | §2.7 corrected: **the `k = 0` spine is ~118 working days, not ~104** (arbitration **C6**; `~114` was the pre-R11 figure and is retired), with the chain written out and `plan/00` §7 named as the arithmetic of record rather than instructed to carry a number computed here. *The failure branch is exactly where a wrong schedule gets read under pressure, and §2.7 **is** the failure branch* | §2.7 (a) |
| **F37** | SERIOUS | The corpus lane is sized for the gate (30 workbooks ⇒ `ADVISORY`) and not for the product (189 ⇒ `BLOCKING`), while being named the longest pole | §2.7 corrected: **both numbers published — 15–25 person-days for `n = 30`, 95–160 for `n = 189`** — and the decision stated as an explicit either/or (ship everything `ADVISORY` and say so, **or** fund the larger corpus). A schedule showing the corpus finishing while the severity tier it exists to produce stays undefined is named as the thing that is not defensible | §2.7 (b) |
| **F2** | FATAL | The `TEMPLATE-COMPUTED` corpus is generated by the code under test, so an FFR over it is zero regardless of quality — which makes "equal FFR" vacuous for **both** arms of the P12 comparison | §0.6 gains a **corpus precondition**: `comparable = False`, reason `FFR CORPUS UNINFORMATIVE FOR BOTH ARMS`, whenever the FFR corpus is `TEMPLATE-COMPUTED` and either arm's `read_keys` intersects the generator's `computed_cells` — **the same intersection `g4_ffr` computes, imported not re-implemented** — and `beats_baselines` is then `False`. Pre-registered (contents item 7) rather than discovered. Two tests, rejection and admission side. New DoD line **J3** | §0.6 (corpus ruling) · P12 entry criteria (P8 row) · P12-B2 unit table · `PREREGISTRATION.md` item 7 · §5 J3 |
| **F18** | FATAL | `U/G` measures the evaluator's coverage, not the operator mix; every mutant wrongly moved into `U` **raises** `K/O` | P12's entry criterion now requires P6 to publish **`I`**, the indeterminate-observability count, beside `U/G`; **G-SETTLE criterion 7** requires the campaign's **six** integers `G · U · I · O · R · K`; `DECISION.md`'s contents and P12's measurement table carry them. *(The run-time half of this finding is repaired in `plan/05` §0.3 and P10-B1.)* | P12 entry criteria (P6 row) · G-SETTLE criterion 7 · `DECISION.md` contents · P12 measurement |
| **"the experiment must not measure a curation"** | — | The pool's disputed-region exclusion set, the extractor configurations and the normalisation are all ours, and nothing ordered them before the draw | **`textsource_sha256` and `exclusion_rule_sha256` enter the lock BEFORE `draw_sha256`**; `append()` raises `PoolNotYetFixed` if the draw hash arrives first; `assert_precedes_first_call` checks the extra git-ancestry edges; the **excluded count and its page numbers are published in the pre-registration**, before the result; `\|drawn\|` carries the excluded count as a **third integer**, never folded in. New control **NC-M34** with injector `exclusions_edited_after_the_draw.py` and an admission-side twin; new residue row **NC-N34**; new DoD line **J2**; **G-SETTLE criterion 8** | `textsource` block (ruling) · lock field list · `prereg.append` / `assert_precedes_first_call` · `PREREGISTRATION.md` item 7b · NC-M34 · NC-N34 · §5 J2 · G-SETTLE criterion 8 |
| **"no model-bearing build is validated by a model judge"** | — | §1's table listed **dual-engine OCR agreement** as a *"deterministic + human"* adjudicator; agreement between two models is not a deterministic adjudication, and both engines can be wrong the same way | §1's row is corrected: **Kind is `human`**, the dual-engine agreement is named a **screen**, and the human confirmation becomes **enforced rather than conventional** — the loader refuses an admitted predicate whose clause is `source_ocr: true` with no confirmation row (`test_nc__M25d`, injector `ocr_confirmation_row_optional.py`, admission-side twin `test_nc__M25e`). Added to NC-M25's guard set and to P13's exit gate | §1 table (OCR row) · P13-B2 OCR containment 1–2 · NC-M25 · P13 exit gate 6b |

**Findings raised elsewhere that constrain P12/P13 and are *not* repaired here:** F1 (the `claims_fault_classes`
envelope field — `plan/03` P4-B1 and `plan/04` P7-B3; P12's registry-bar row in the two-attrition-numbers
table quotes the claim and inherits the repair), F9 (G0's disposition of clause-less candidates — `plan/04`),
F19 (the `formula_source` contract — repaired in `plan/05`; P12's `O` depends on it), F31 (DoD line C4 —
`plan/01`), F43 (the staffing model — `plan/00` §7). Where one of them constrains a gate above, the
constraint is written into the gate rather than assumed.

**What this pass did not repair, stated because the plan's own standard requires it.** Three of the changes
above are **cross-document contracts this document cannot land alone**: the `P7-B0` build must be created in
`plan/04`; `plan/00` §6 and §10 must take the `mu_base_error_rate` rename in the same commit or the gate
ships inverted in the document CI transcribes from; and `plan/00` §7 must take both the **~118**-day path
(C6) and the two corpus numbers. **Each is written here as a named test or a named section that fails when the other
side is absent** — `test_contract__mu_is_an_error_rate` is green in this document and says nothing about
`plan/00`, which is precisely why the rename, and not the test, is the repair.

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C6** — the `k = 0` critical path | **`~114` → `~118`**, and **the instruction telling `00` to carry `~114` is deleted rather than corrected** — a stale number propagated by instruction is worse than one held alone; `00` §7 is named as the arithmetic of record | §2.7 (a) · §2.7 (b) · §residue · F34 row |
| **C8(a)** — prereg test name | `test_e6__preregistration_criterion_is_machine_evaluable` → `test_contract__preregistration_criterion_is_machine_evaluable`, **6 occurrences** | §0.6 ruling box · P12-B1 · P12 file list · DoD J2 · §6 · F30 row |
| **C9** — the catalogue | the *"continuing past `07`'s `NC-N07`…`N10`"* allocation sentence is retired with the practice; `NC-N07` is a **RETIRED** id (`07`'s entry → `NC-N40`); this document's entries are `NC-N30`–`N34` and it references rather than allocates | P13-B2 `injector: NONE` block |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
