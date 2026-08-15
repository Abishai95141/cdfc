# P12 exit gate — **G-SETTLE**, evaluated point by point

**Evaluable by someone who did not do the work.** Each of `plan/06` §P12's eight criteria is
restated, then answered with the command that produces the answer. Where a criterion **cannot be
evaluated**, it says so and names what is missing — and the distinction between *not met* and
*not evaluable* is kept, because their remedies differ.

**Result: 4 of 8 MET · 4 NOT EVALUABLE — and all four are downstream of one absent artifact.**

G-SETTLE's verdict is `RETAIN | DELETE | EXTEND`, and every branch requires a realised `k`. **There
is no `k`.** So this document does not report a G-SETTLE verdict; it reports which of the gate's
conditions are already true of the repository, and which await the run. `experiments/E6/DECISION.md`
is published at `status: PENDING` with the same boundary on its face.

---

### 1. `preregistration.lock.json` exists; its `h0` matches `PREREGISTRATION.md`; and the commits introducing `h0`, `draw_sha256`, `strata_sha256` and `baselines_sha256` are ALL git-ancestors of the commit introducing the first `runlog.jsonl` row

**PARTIALLY MET — the first half is met; the second is NOT EVALUABLE, and the machinery for it is
built and tested.**

| | |
|---|---|
| the lock exists | **yes** |
| `h0` matches the document | **yes** — `test_nc__M02a_h0_mismatch_fails_the_build`, and `PreregEditThreshold` has been observed to turn it red |
| `h0` cannot move | **yes** — a second `lock()` over an edited document raises `PreregistrationMismatch` |
| the ancestry chain | **NOT EVALUABLE — there is no `runlog.jsonl`, because no model call has been made** |

`assert_precedes_first_call` walks the object graph with `git merge-base --is-ancestor` rather than
comparing timestamps, and `ancestry_state()` currently returns
`UNVERIFIABLE (no runlog — no model call has been made)`.

**It never returns `VERIFIED` by default.** Three states are kept apart — `VERIFIED`,
`UNVERIFIABLE (…)`, `VIOLATED (…)` — because a violation is a finding about the experiment and an
unverifiable ancestry is a finding about the environment. Reporting the second as the first is the
collapse this project is named for, and the rule is inherited from `g2_kill.ancestry_state`.

```bash
make e6-status
```

---

### 2. `DECISION.md` exists, is dated, and cites the lock hash that matches

**MET.** It exists, it is dated 15 Aug 2026, it carries `status: PENDING`, and it names the lock
together with **the command that recomputes it** — which is DoD line J1's requirement, and the
distinction it draws is the point: *a hash a reviewer can recompute is evidence; a hash pasted into
a description is a claim.*

`plan/06` sanctions the `PENDING` state explicitly. Publishing it now rather than waiting for a
number is deliberate: `NC-M17`'s failure mode is not a wrong answer, it is **a result quietly not
published because nothing depended on it**, and a document that does not exist until there is a
number is exactly how that happens.

---

### 3. stage 1: `k_a ≥ 6` **OR** stage 2: pooled `k_a ≥ 12`

**NOT EVALUABLE. There is no `k`.**

The pool cannot be built: `corpus/instruments/MANIFEST.json` carries nine instruments, all
`kind: TEMPLATE`, and `statute_instruments: []`. `docs/decisions/D-P7-01-no-statutory-instrument.md`
records that this was found at P7-B0 and that **synthesising an instrument was rejected** — a span
into an invented text is not evidence, and it would make every G0 number meaningless while looking
exactly like progress.

`plan/06` pre-committed the branch: *"`PoolExhausted` fires, no model call is made, no money is
spent, and the published result is `|A| < 20`."* **This is that branch's limiting form** — the
extractions do not disagree, because there is nothing to extract.

```bash
make pool     # exits 2, naming the absence
```

**What IS met is everything the criterion is made of.** `decide()` is pinned at all 164 points of
`(k, stage, beats)`; every branch of the rule — including §0.5's *`k ≥ 6` without beating the
baselines is DELETE* — is asserted; `k = 0` returns `DELETE` with `[0.000, 0.161]`.

---

### 4. `beats_baselines(rows)` is True, where `beats_baselines` is the PURE FUNCTION of §0.6

**THE FUNCTION IS MET IN FULL. ITS VALUE IS NOT EVALUABLE.**

This is adversary **F30**'s repair and it is the criterion most worth checking, because it was
locked and hashed **in a state that could not be evaluated**: *"marginal kill strictly greater than
B0"* compares a count to **what**? Three readings, three different gates, and the weakest —
`|K_c \ K_B2| > 0` — is true of any predicate that kills anything the two degenerate envelopes do
not, which is most of them.

| | |
|---|---|
| a pure function, integer arithmetic | **yes**, `cdfc/experiment/marginal.py` |
| all three terms | **yes** — every row comparable, marginal > 0 against each baseline separately, and the union floor |
| the union floor is `1/10` of `observable`, not `> 0` | **yes**, and both rejected alternatives are recorded with their reasons |
| §0.6's FFR precondition | **yes** — `NOT COMPARABLE — candidate FFR upper bound exceeds baseline` renders as a **string, not a number** |
| §0.6's corpus precondition (F2) | **yes** — `FFR CORPUS UNINFORMATIVE FOR BOTH ARMS`, computed with the intersection **imported from `g4_ffr`**, never re-implemented |
| exhaustively pinned | **yes** — `test_decide__beats_baselines_is_arithmetic_not_prose` walks the `MarginalKill` tuple space including the floor's exact boundary at `10 · marginal == observable` |
| a prose criterion is unreachable | **yes** — `lock()` parses the criterion block and **refuses before writing anything**; the lock file is asserted absent after the refusal |

**A prose reading of this line is a build failure, not an interpretation.**

---

### 5. `funnel.json` stage 0 entered == 600, discards included

**NOT EVALUABLE (no run). The invariant is MET and enforced structurally.**

`funnel()` **refuses to build** from a `records` sequence whose length is not
`|obligations| × |regimes| × k`, so a caller that had already filtered its discards gets an
exception rather than a tidier-looking funnel. `FunnelDropsDiscards` has been observed to turn the
guard red, and `RejectionRow` cannot be constructed without its measured number — *"rejected at
G2"* is not a finding; *"rejected at G2 with `K/O = 0.05` against a bar of 0.80"* is.

---

### 6. No third stage exists

**MET.** `decide()` raises `CriterionExhausted` at `stage > 2` and `extend()` raises
`ExtensionAlreadyTaken` on a draw already at stage 2 — and additionally refuses an extension drawn
from a pool whose hash differs from stage 1's, because "continuing the same permutation" over a
re-curated pool is NC-M34 wearing the extension's clothes. `ThirdStage` observed red.

---

### 7. The campaign publishes SIX integers — `G · U · I · O · R · K` — and `DECISION.md` prints `I` beside `U/G` wherever either appears

**NOT EVALUABLE for this experiment's campaign (there are no candidates), and MET upstream.**

`I` — indeterminate observability — is P6's, and it is published: the pinned figures are
`K/O 189/739, I = 22, U = 12`. Adversary F18's point stands and is inherited: **`U/G` alone reports
our evaluator's coverage under the name of the fault model's observability**, and every mutant
wrongly moved into `U` *raises* `K/O` — measurement error correlated with the quantity measured, in
the flattering direction. The `DECISION.md` contents list carries the requirement for the run.

---

### 8. The pool's exclusion set and the extractor configuration are inside the lock, and the commits introducing them are git-ancestors of the draw commit

**THE MECHANISM IS MET. THE INSTANCE IS NOT EVALUABLE.**

`prereg.append()` raises `PoolNotYetFixed` if `draw_sha256` arrives while `textsource_sha256` or
`exclusion_rule_sha256` is absent, and `assert_precedes_first_call` checks the same two edges by
git ancestry — because an ordering enforced only inside `append()` is enforced only for people who
use `append()`. `ExclusionsEditedAfterTheDraw` reorders `APPENDABLE` **without touching the `if`
that reads it**, which is what makes it a realistic edit, and it has been observed to turn the
guard red with the admission-side twin holding.

The instance is not evaluable because there is no pool to exclude anything from.

---

## The controls, and the two that had to be rebuilt

**Nine catalogue entries, nine injectors, nine registry rows — all LIVE, all observed red, every
positive control holding.** The sweep reports **211 of 211 guards flipped**.

**Two were wrong on first observation, and both are worth reading.**

**Row 104's guard was checking nothing.** The import closure was seeded with the package name, and
`cdfc/qualify/__init__.py` imports almost nothing — so the walk never reached `g2_kill`, the
injected model client sat there undetected, and the control **reported itself caught**. This is the
project's own recurring defect — a gate that reports OK having looked at nothing — occurring inside
the gate written to catch it. The fix seeds the walk with every module *file* under each root,
which is also the stronger rule.

**Row 100's injector broke the harness rather than the measurement.** Truncating `stratum_b_all` at
construction is refused by `Draw.__post_init__`, so `draw()` raised and *every* guard went red
including the positive control. That the invariant catches the constructional form is a real
property; the injector now attacks the reporting path, which is the version that would survive
review.

**And a third defect was found by the controls rather than by review.** `AddGateRow` — a control
from P0 — injects a duplicate registry row, and its id had been moved from 19 to 99 the last time a
real row caught up with it. **Row 99 was registered at P12 and the identical failure recurred, in
the identical form, against a comment describing it.** The sentinel is now `9_999_999` and
`test_contract__registry_ids_are_below_the_injector_sentinel` asserts the property instead of
leaving it to be rediscovered a third time.

## Two defects the test-writing pass found in code that already looked right

- **`extend()` froze the Stratum-B generation cap at stage 1's realised count.** When stage 1 turned
  up fewer than ten Stratum-B obligations, the pooled experiment could never reach ten however many
  stage 2 drew. `|drawn|` was never affected, so §0.4's invariant held and **NC-M03 could not see
  it** — it only ever shrank the arm whose entire job is to tell us whether the human stratification
  carried information.
- **`retain_probability_fresh40`'s docstring quoted 0.926 and 0.060 as though they were retain
  probabilities.** They are `P(delete)`, the complement of what the function returns. The figures
  were right and the sentence invited a reader to compare a retain probability against a delete one.

## Mutation, per methodology §3.5

`experiment/power.py`, `experiment/decide.py` and `experiment/marginal.py` are Tier **V**
(`K/V ≥ 0.90`) — they are pure arithmetic on the criterion path. `experiment/prereg.py` and
`experiment/criterion.py` are Tier **Q** (0.85). `experiment/draw.py`, `enumerate_shall.py`,
`parse.py` and `funnel.py` are Tier **S** (0.70). **The mutation run has not been performed**, and
this phase does not claim it: `make mutation-pr` still prints that mutation testing arrives with
the code it measures. Recording the tier assignment without the run is the honest half — a phase
gate quoting a bare percentage would fail its own review, and one quoting no number should say so.

---

## The fresh clone, and the two defects it found

Every phase closes with a fresh clone, because a measurement that only re-derives in the tree that
produced it is a screenshot. **P12's clone run found two things, and one of them is a hole in a
contract test that had been reporting green.**

**One — the committed pre-registration had drifted from its generator, and the contract test could
not see it.** `test_e6__power_table_matches_preregistration` compares the power *tables*, and it
passed while three sentences of prose in `tools/e6/preregister.py` had been edited (to clear
`ci/no-bare-rate.sh`) and never regenerated on disk. Nothing in the tree caught it. The clone did,
immediately and by construction: re-running the generator produced a different `h0`, and `lock()`
**refused with `PreregistrationMismatch`** — the refusal working exactly as designed, and finding a
real drift rather than a hypothetical one.

*A partial contract test is worse than none here*, because it reports that a generated document
equals its generator while checking a fifth of it — and the fifth it checked was the part nobody
would ever edit by hand. `test_e6__the_committed_preregistration_equals_its_generator_byte_for_byte`
now compares the whole file. **The lock was re-taken on the regenerated document**, which is
legitimate and is stated rather than quietly done: no run has occurred, no `runlog.jsonl` exists,
and `run_may_proceed` is `False`, so nothing depended on the old hash. After the run, that same
refusal is what makes the hash mean something.

**Two — an injector was left applied to `src/cdfc/qualify/surgery.py`.** `make verify`'s shell was
reaped while its sweep was mid-injection, and the openpyxl round-trip stayed in the working tree.
`ci/no-openpyxl-writer.sh` was red in the clone and in the tree. This is a **process** defect rather
than a code one, and the process rule it broke is already written down: run the sweep detached and
**do nothing else in the tree while it runs**. Two injectors leaked earlier in this phase for the
same reason — `ci/GATES.md` lost nine rows and `src/cdfc/cli.py` had `EXIT_NOT_IMPLEMENTED` left at
`0` — because a second `inject()` context was opened concurrently and its `_save` captured the
first one's injected state. The digest check inside `inject()` cannot see that: it compares before
and after within its own context, and both were consistent.

### What the clone verified

| | |
|---|---|
| grep gates | **14 of 14 OK** |
| contract, unit, property, determinism, and P12's negative controls | **all pass** |
| `make pool` | **exit 2**, naming the absent instrument |
| `make preregister` | regenerates **the same `h0`** — `e7e1099209a5523a…` |

`make verify` in full was run **in the tree**, not in the clone: it contains the 20-minute sweep,
and the sweep mutates the tree it runs in. The clone ran everything else. **In-tree totals: 107 of
107 live gates observed red, 0 PENDING, 130 of 130 catalogue entries caught, 211 of 211 guards
flipped, 0 errors, 0 leaks.**

## What P12 contributes to `reports/validation-ledger.jsonl`: nothing, and that is correct

P12's measurements are `k of 20`, `|A|/|drawn|`, the campaign's six integers, the per-baseline
marginal kill, and the stratification's discriminative value. **None of them exists**, because none
survives the absent instrument. A ledger row for a number nobody measured would be the defect the
ledger's eleven required fields and its 60-character caveat rule exist to prevent.

---

## `make verify` is GREEN — and it was green **1 run in 3**, which is itself a finding

**The final run exits 0:** `130/130 entries caught · 211/211 guards flipped · 107 of 107 live
gates observed red · "every gate green, every negative control caught"`.

**It is recorded here that it took three attempts, because a control suite that is intermittently
green is a control suite you cannot rely on, and this project does not get to describe that as
noise.**

| run | outcome |
|---|---|
| `make verify` #1 | **RC=2** — its sweep reported `NC-Q61: guards not green before injection` |
| `make verify` #2 | **RC=2** — `NC-Q30` **leaked**; `NC-Q31` and `NC-Q61` failed as collateral behind it |
| `make verify` #3 | **RC=0** — clean |
| standalone `tools/nc_sweep.py` | **130/130 · 211/211**, three times, no errors, no leaks |
| full `pytest tests` | **green** |
| fresh clone | **green** |

### What was ruled out, by experiment rather than by argument

| hypothesis | test | result |
|---|---|---|
| `NC-Q30`'s injector restores badly | inject → restore → re-run its two guards, in isolation | **no leak** |
| the guards share an on-disk artifact | read the tests | all use `tmp_path`; no shared state |
| a LibreOffice profile lock | grep the observability path for `soffice` | **no LibreOffice on this path at all** |
| a sweep subprocess timeout | grep `nc_sweep.py`; time the guards | **no timeout**; the three run in 0.06–0.12 s |
| cumulative `mtime + 1` drift into the future from `_purge_bytecode` | stat the touched files against the clock | **no future mtimes** |
| the full `pytest tests` run that precedes the sweep inside `make verify` poisons it | run the full suite, then the three guards, then `NC-Q30` through `inject()` | **all green; no leak** |

**The mechanism was not identified at the time of writing. A REAL CONTAMINATION WAS FOUND
AFTERWARDS AND IS FIXED — see the section at the end of this document — but it cannot have caused
these three, and that is stated there rather than glossed.** What is established is the shape: the three affected controls
are **`NC-Q30`, `NC-Q31` and `NC-Q61`, all of which call `seed_mutant`**, all P6-era, and **none of
them touched by P12** — this phase added no code under `qualify/surgery.py`, `qualify/observability.py`
or `tests/negative/test_nc_campaign.py`. Each failure appeared on a different entry, and every one
of them is green in isolation, green after a full suite run, and green now.

### Why this is written down rather than absorbed

The first two failures were also the mechanism by which **three injector leaks** reached the working
tree earlier in this phase — `ci/GATES.md` lost nine freshly-appended rows, `src/cdfc/cli.py` was
left with `EXIT_NOT_IMPLEMENTED = 0`, and `src/cdfc/qualify/surgery.py` kept an openpyxl round-trip
that only the **fresh clone** caught. Two of those were my own fault for working in the tree while a
detached sweep ran; the third came from a `make verify` whose shell was reaped mid-injection.

**`inject()`'s own self-check cannot see any of this.** It digests the source before and after
within its own context, and both are self-consistent — the same blind spot its docstring already
records for bytecode, one level out. `docs/measurements/P12-exit-gate.md` is therefore the honest
place for it: **an intermittently-green control suite is an OPEN finding**, its blast radius is
"an interrupted sweep leaves the tree silently broken", and the mitigation until it is understood
is procedural — run the sweep detached, touch nothing while it runs, and `git status` afterwards.

---

## The contamination the sweep could not see — FOUND AND FIXED

The intermittency above was chased to a real defect, though **not to the one that explains it.**
Both halves are recorded because reporting only the fix would leave a reader believing the
flakiness is closed.

### What was found

**`NC-CI14` was changing a file its injector never declared.** `NulByteInPlanDoc` declares
`plan/00-decomposition.md`. Its guard runs `ci/catalogue-ids.sh`, which runs
`plan/scripts/nc_audit.py`, which **writes `plan/scripts/nc_audit_result.json`** — from a plan
document carrying an injected NUL byte. The corrupted artifact **survived the restore** and stayed
in the tree for every entry that followed.

**`inject()` could not see it.** Its digest is scoped to `touches`, so it verifies exactly what it
was told about — the same shape of defect this harness exists to catch, occurring inside the
harness, one level out from the bytecode blind spot its own docstring already records.

> **The rule that was wrong: `touches` is not "what `apply()` edits". It is EVERYTHING THE ENTRY
> CAN CHANGE, guard tests included** — because the guards run inside the injected tree, and a
> producer they invoke writes real repository artifacts from broken input.

### How it was found

By digesting the **whole tracked tree** around every entry rather than trusting each injector's
declaration — 1,220 files, once per entry. That is too slow for the shipped sweep, so the shipped
version takes `git status --porcelain` around each entry and **hashes the paths git already lists**.

### What was changed

| | |
|---|---|
| `NulByteInPlanDoc` | declares `nc_audit_result.json`, with the reasoning at the declaration |
| `tools/nc_sweep.py` | records `contaminated` per entry — every path it changed and did not declare. It enters `caught`, it prints, and the sweep **exits non-zero** |
| `tools/nc_sweep.py` | a leak now carries its **assertion text**. It was discarded — `(ok, _)` — so `leaked: [...]` said *which* guard was still red and never *why* |
| `tests/negative/test_nc_sweep.py` | `test_sweep__no_entry_changes_a_path_it_does_not_declare` and `test_sweep__a_leak_carries_its_assertion_text` |

### The positive control earned its place twice

**The first detector compared git STATUS CODES**, so a file going from modified-with-content-A to
modified-with-content-B carried the same two characters both times and read as unchanged — it
reported a clean tree over the very contamination it was written to find. The control caught it,
and the digest is content-based now.

**The control's own first version was also wrong**: it removed the path from the *comparison set*
while leaving it in `touches`, so `inject()` still restored the file and there was nothing to
detect. It reported the detector blind when the detector had simply never been given anything to
see. A control that cannot fail is not a control, and that took two attempts to get right.

### What this does NOT claim

**`plan/scripts/nc_audit_result.json` is read by nothing at runtime.** The contamination was real
and **inert for other controls** — it dirtied the tree and nothing consumed it. **It therefore
cannot be the cause of the `NC-Q30` / `NC-Q31` / `NC-Q61` intermittency**, and that finding stays
**OPEN**.

What has changed is that the next occurrence is **diagnosable**: it will arrive with its
post-restore assertion text and a contamination list attached, instead of as a bare list of node
ids that costs a 20-minute reproduction to interpret.

**Since the fix: `make verify` green 2 of 2**, with `contaminated_count 0` on both, plus a
standalone sweep at `130/130 · 211/211 · contaminated 0`. Before the fix it was green 1 of 3. Two
successes are evidence, not proof, and the sample is stated so nobody reads it as more.
