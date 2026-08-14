# P10 exit gate — **G-LIVENESS**, evaluated point by point

**Evaluable by someone who did not do the work.** Each of `plan/05` §P10's eleven criteria is
restated verbatim, then answered with the command that produces the answer. Where a criterion is
**not met**, it says so and names what is missing; where it is met by a different mechanism from
the one the plan specified, the substitution is stated rather than absorbed.

**Result: 9 of 11 met, 1 met with a stated substitution, 1 NOT MET.**

---

### 1. All six deaths of §P10·L.1 produce `INVALID`, each naming the dead predicate(s), each with `settledFraction is None` and `verdict is None` — not zero, not omitted, `null`

**MET.**

| death | mechanism | control | produces |
|---|---|---|---|
| **D1** the predicate cannot fire | `expr` replaced by the literal `true` on a predicate with a valid stored witness | `test_nc__D1_a_check_that_cannot_fire_is_caught_and_named` | `INVALID` · `PREDICATE_DID_NOT_FIRE` · the id named · `settledFraction: null` |
| **D2** the witness cannot reach the predicate | a stored witness retargeted outside the predicate's read set | `test_nc__D2_a_witness_outside_the_read_set_is_a_distinct_kind` | `INVALID` · **`WITNESS_MISSES_READ_SET`** — a distinct kind |
| **D3** the apparatus is broken, binding intact | `keys_resolver_offbyone` · `celrt_short_circuits` · `apply_returns_clean_facts` | NC-C04 / C04b / C04c | `INVALID` · `PREDICATE_DID_NOT_FIRE` · cause set exactly `{canary_silent}` |
| **D4** the loop is a stub | `canaries_noop` | NC-C01 | `INVALID` · `SELFTEST_NOT_SILENT` |
| **D5** the counts are asserted, not counted | `canary_count_asserted` | NC-C01b | `INVALID` · `WHOLESALE_INAPPLICABILITY` on the filing where the counts diverge |
| **D6** the canary touches the file | `canary_reopens_file` | NC-C05c | the audit hook observes the open and the guard goes red |

**D3 is demonstrated by THREE mechanisms and the plan names four**, and the two substitutions are
recorded rather than counted:

- **`tolerance_widened` has no subject.** The CEL comparison is exact `==`; the only tolerance in
  the system is P9's `template_diff.agree()`, which is a relation, not a predicate. An injector
  widening a tolerance that does not exist would have been a fourth *name* for one of the other
  three, and the sweep would have counted it as a fourth mechanism.
- **`facts_trailing_space` was measured and flips no canary.** It was written as D3's fourth on the
  argument that membership predicates would stop matching their vocabulary; run against the sweep,
  no canary went silent — this population's witnesses are numeric, and a trailing space on an
  already-illegal value leaves it illegal. It is filed as **NC-C13** against the shared patcher,
  which is what it really breaks. That is a smaller claim and it is the true one.

`apply_returns_clean_facts` is its replacement, and its own predecessor (`apply_skips_the_target`)
was **withdrawn after measurement**: the loop moves on to the next stored witness when a predicate
cannot run, so a single mis-applied fault is absorbed. That robustness is correct and it makes the
injector useless as a control.

```bash
python -m pytest tests/negative/test_nc_selfcheck.py -q
```

---

### 2. `test_liveness__only_cause_is_canary_silent` is green for D1, D2 and D3's injectors: the `invalid` cause set is exactly `{canary_silent}`

**MET, and it is the single assertion a reviewer should look for first.**

A control that also trips `invalid.cells_bound_zero`, `invalid.template_unbound`,
`invalid.reader_structural_disagreement` or `invalid.closure_violated` proves nothing about
canaries — another layer caught it.

In the catalogue this guard carries **`flips: false`** under NC-C01, NC-C04, NC-C04b and NC-C04c,
which is the exact-set semantics doing real work: the sweep asserts it stays **green** under every
apparatus break, so cause isolation is a measurement and not a claim.

---

### 3. The three positive controls of §P10·L.2.2 are green

**MET.** Without these, all six deaths above are satisfied by a layer that returns `INVALID`
unconditionally.

| control | asserts | measured |
|---|---|---|
| `test_canary__healthy_run_is_VALID` | a healthy run is `VALID` with digits | 33/33 canaries · 33/33 anti-canaries · 0 inapplicable · self-test silent · fraction **0.5065** |
| `test_canary__a_real_fault_still_FAILs_and_the_run_stays_VALID` | a broken **filing** is not a broken **instrument** | `FAIL` on `P-0020`, `run_state == VALID`, fraction rendered |
| `test_canary__inapplicable_below_the_ceiling_stays_VALID` | inapplicability costs coverage, it does not invalidate | 9 of 47 inapplicable → `VALID`, fraction falls **0.5065 → 0.4155** |

The middle one is the load-bearing one: **a layer that cannot tell a broken instrument from a
broken filing has destroyed the distinction the whole product sells.**

The seeded cell is **computed** from the fixture rather than read off its filename, and that is not
pedantry: `mutant__f11-formula-override__portfolio-O7.xlsx` seeds `'1. Introduction'!C54`, not
`'3. Portfolio'!O7`. Its provenance file names no cell, so the filename was the only record and the
filename is wrong.

---

### 4. `test_nc__C03` is green: the renamed-sheet fixture is `invalid.template_unbound`, and the canary layer is not credited for it

**MET, with a stated substitution.** The plan says *renamed sheet*; this build uses
`row-inserted__portfolio-r7.xlsx`, which changes the **dimensions**. The binder works by structural
fingerprint over *(sheet names + states, dimensions, merged ranges, defined names, unlocked mask)* —
both inputs move the same fingerprint, five steps before the canary loop runs, and the fixture that
exists is the row-inserted one.

Measured: `invalid_causes == (TEMPLATE_UNBOUND,)`, `CANARY_SILENT` absent, and
`livenessProof: null` — **absence rendered in words, never as zeros.** `canariesRun: 0` says the
loop ran and found nothing to do; `null` says nobody asked.

The same body asserts a lawful filing **does** bind against this catalogue, so the refusal is about
the fixture and not about the catalogue.

---

### 5. `|RESIDUE| > 0`, with at least one survivor from each of the two exhibit families, each content-addressed and rendered as an exhibit

**MET.** Both drawn from the campaign's own survivor set, not built for the page.

```
|RESIDUE| = 517 of 517 WRONG mutants   ADMITTED (empty)  -> CEILING
|RESIDUE| = 374 of 517 WRONG mutants   PRE-GATE (348 candidates)
```

| family | operator | cells | why unkillable |
|---|---|---|---|
| **E1** coordinated misstatement | `F13.b` | `3. Portfolio!L5`, `1. Introduction!G56` | both ends of a cross-sheet carry moved by the same amount, so the carry identity is still satisfied |
| **E2** categorical swap | `F10.a` | `3. Portfolio!K76` | legal by the regulator's own validation, **and** the cell feeds no template formula |

**E1 is a construction and E2 is a measurement.** E2's second half is pinned:
`test_golden__2790_cells_feed_no_formula` — 2,790 of 3,747 field-surface cells feed no template
formula at all, with its per-sheet split and a **paired value assertion** (`6. Complaints!C10`
inside the set, `3. Portfolio!C7` outside it).

**The first number is the honest headline and it is a CEILING**: P7 admits 0 of 348 and P9 admits
0 relations, so the rejector set on the day is empty and every WRONG mutant survives by
construction. NC-C07 is the control that stops a ceiling being read as a measurement.

```bash
make residue
```

---

### 6. `test_residue_not_inflatable` green — adding 505 recompute predicates does not shrink the residue

**MET**, and mechanised rather than argued. `TEMPLATE_DIFF` binds the field-surface precedents of
every formula cell — 957 of them. The E2 exhibit's cell is in the **complement** of exactly that
set, so no recompute predicate can bind it and adding arithmetic cannot reach it.

---

### 7. κ published with its `n`; if κ < 0.6, the written reconciliation exists and both κ values are published

**NOT MET.** Published as **κ: UNMEASURED, n = 0**, with the blocker named.

**There is no second adjudicator on this project, and κ has no mechanical substitute.** Everything
else this build lacked a human for had a stand-in that was weaker in a stateable way — LibreOffice
for an independent evaluator, a foreign engine for arm 2, `SINGLE-SIGNER` for a second reviewer. κ
measures agreement between two *minds*, and the two things a machine could do here are both worse
than nothing:

- re-running the same rules gives κ = 1.0 **by construction**, which is a lie with a number on it;
- running a *second rule set* and calling its agreement κ dresses a mechanical agreement as an
  adjudication agreement — the *"a count agreeing with a pin is evidence about the count"* defect
  this project has now found seven times.

`cohens_kappa` is built and tested in both directions against hand-computed vectors — perfect
agreement is 1, chance agreement is 0, total disagreement is −1, one label returns `None` and not
zero. The seeded 20-in-100 sample is drawn deterministically and its seed is inside the record
digest and dated **before** round 1. **It is the input that does not exist, not the instrument.**

---

### 8. `PERF-CANARY2` measured and recorded, read from `reports/perf/<run_id>.jsonl` and not from any hashed object; `test_contract__no_duration_field_in_a_hashed_object` and `test_tim__timings_are_written_outside_the_payload` both green

**MET, and the budget moved.**

| | |
|---|---:|
| measured | **4,082 ms** for 66 executions (33 canaries + 33 anti-canaries) |
| written to | `reports/perf/aeedbfe18c803061.jsonl` |
| old baseline | ≈70 ms, **DERIVED** |
| new baseline | 4,200 ms, **MEASURED** |

**The ≈70 ms was derived from the wrong quantity** — from raw-zip mutation throughput
(7,946 mutants/s), which does not contain the step that dominates a canary: a full CEL evaluation
over a freshly-built 3,747-cell activation. `perf/BUDGET-CHANGES.md` carries the dated row and the
argument, **and states what it costs the plan's own conclusion**: *"against a ~30 ms deterministic
core and a ≈450 ms complete online run, there is still no reason not to"* is superseded by
measurement. At 4 seconds the loop is nine times the online run, not a seventh of it. The layer
still ships and the argument for it is now weaker and different: four seconds is affordable in an
offline quarterly review and would not be in an interactive path.

The optimisation that would close most of the gap — building the CEL activation once and mutating
it in place — is **refused**, and the refusal is recorded: `apply()` returning a COPY is what makes
*"the received artifact is never touched"* assertable by identity, and trading that for latency in
the layer whose subject is trustworthiness is the wrong trade.

Both timing tests are green, and the shell gate and its AST twin now police the **same scope** —
they disagreed the moment this phase wrote the module the F23 ruling asked for.

---

### 9. `canariesIndeterminate` is rendered beside `canariesInapplicable` in `livenessProof`, and `test_th__indeterminate_counts_toward_the_ceiling` is green

**MET.** They are **counted together** in the ceiling's numerator and **reported apart**
everywhere else, which is the only combination that is honest in both directions (adversary F18).
One is a fact about the filing; the other is a fact about our evaluator.

```jsonc
"livenessProof": { "rowsTotal": 34, "canariesRun": 33, "canariesPassed": 33,
                   "antiCanariesRun": 33, "antiCanariesPassed": 33,
                   "canariesInapplicable": 0, "canariesIndeterminate": 0,
                   "canariesUnresolved": 0, "antiCanariesFired": 0,
                   "antiCanariesNotPass": 0, "selfTestSilent": true, "maxWitnesses": 3 }
```

Every value is an integer computed as `len()` of a row set. There is no duration anywhere in this
object, in `run.jsonl`, or in anything `verify` compares.

---

### 10. `test_nc__C03` proves the canary layer **exists** (`canariesRun > 0` on the reference fill) in the same test body in which it proves the layer did not fire

**MET, and generalised.** As written without it, NC-C03 is satisfied by a build in which
`src/cdfc/selfcheck/` does not exist at all.

The `layer_exists_assertion` runs **first, in the same body**. And the requirement is enforced in
its **general form** rather than on the one instance:
`test_nc_meta__none_injector_entries_carry_a_layer_exists_assertion` requires the field on every
`injector: NONE` row whose claim is that some layer did not fire, and requires it to name a
**positive quantity** and to say it runs **before** the absence claim — because *"the layer
exists"* is not checkable and *"canariesRun > 0"* is.

---

### 11. `docs/measurements/P10-canary-cost.md` publishes the `MAX_WITNESSES ∈ {1,3,5}` curve, and `MAX_WITNESSES` is either closed by it or still renders `PROVISIONAL` in code

**MET.** The curve is published and **it does not close the constant**, so `MAX_WITNESSES = 3`
keeps rendering `PROVISIONAL — see docs/measurements/P10-canary-cost.md` in
`selfcheck/thresholds.py`, which is exactly what §5.1's decision rule says to do when the curve
does not decide.

What the curve *does* establish is that raising the cap buys nothing on this surface, so the
shipped value is not costing coverage. And the document carries, on its own face:
**CALIBRATION SURFACE, NOT AN FFR CORPUS** — these filings were generated by this project, so the
curve says what *our* filings can demonstrate about the instrument and nothing about what a filer's
return would.

---

## What P10 found in the phases below it

A liveness layer replays admission evidence, so the first thing it does is audit the evidence. It
found three defects, all in shipped code, all repaired, and **every number they moved went against
us**:

| finding | where | effect |
|---|---|---|
| `_coerce(None)` returned the string `"None"`, and an equality over it returns false | `facts/build.py`, via `p6_kill._patch` | **68 of 257 recorded kills were coercion artifacts.** `K` 257 → **189**; `F07` 34 → **0**; the funnel's kill stage 125 → **33** |
| the fact-tree patcher could not CREATE a cell the filing left blank | `facts/patch.py` | a fault that writes into an empty cell had nothing to rewrite — 20 of 33 canaries wrongly silent on a sparse filing |
| the campaign wrote no bucket for its own survivors | `qualify/runner.py` | `killed`/`unobservable`/`indeterminate`/`unreachable` — an observable, reachable, unkilled mutant landed in **no file**, and that population **is** the residue. `survived.jsonl` now carries 494 rows |

The first is `docs/decisions/D-P10-01-none-is-not-a-value.md`. The third is the sharpest: the
campaign's own docstring said unobservable mutants are retained *"so P10 has its residue
feedstock"* — the reasoning was right and the bucket list was incomplete, and nothing noticed until
something asked for the rows.
