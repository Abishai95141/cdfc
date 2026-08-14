# `perf/BUDGET-CHANGES.md` — every performance budget that moved, and the argument that moved it

**Append-only.** A budget is never edited in place. A change is a NEW ROW with its date, the old
figure, the new figure, and the argument — and the argument may not be *"the measurement came in
higher"*. A budget raised to fit its measurement is not a budget; it is a description of the
current implementation with a threshold drawn around it.

The one admissible argument for raising a budget is that **the old figure measured a different
quantity from the one the budget is about.** That is what happened to `PERF-CANARY2`, and the row
below says exactly which quantity.

---

## 2026-08-14 — `PERF-CANARY2`: ≈70 ms DERIVED → 4,200 ms MEASURED

| | old | new |
|---|---:|---:|
| baseline | ≈70 ms (**DERIVED**) | **4,200 ms (MEASURED)** |
| warn above | 110 ms | 6,000 ms |
| fail above | 160 ms | 9,000 ms |

**The old figure was derived from the wrong quantity, and the derivation is stated in `plan/05`
itself:** *"≈ 70 ms (DERIVED from the measured 7,946 mutations/s)"*. 7,946 mutations/s is the
throughput of **raw-zip surgery** — writing a mutant workbook. A canary is not a mutation. One
canary is:

1. two cone-restricted recalculations of the filing's formula graph (`observability`), memoised so
   `apply` reuses them;
2. a deep copy of the 3,747-cell fact tree with the fault patched into it (`apply`); and
3. **a full CEL evaluation of one predicate over a freshly-built `celtypes` activation.**

Step 3 dominates, and it is the step the old derivation did not contain at all. `p5_run`'s own
docstring already recorded the cost of that activation from the other side: *"rebuilding the
3,747-cell celtypes tree 351 times exhausted memory and the run was killed."* Every canary builds
one, because `apply()` returns a new `FactSet` by construction — that is the whole point of it
returning a COPY, and it is not negotiable.

**Measured: 4,063 ms for 66 executions on the reference fill — 33 canaries and 33 anti-canaries.**
About 62 ms per execution. The new baseline is 4,200 ms with the warn and fail thresholds set at
roughly 1.5× and 2× that, which is the same shape as the budget it replaces.

### What this costs the plan's argument, stated rather than absorbed

`plan/05` P10-B1 concludes: *"Against a ~30 ms deterministic core and a ≈450 ms complete online
run, **there is still no reason not to**."* **That sentence is superseded by measurement.** At
4 seconds the canary loop is roughly nine times the complete online run, not a seventh of it.

The layer still ships, and the argument for it is now a different one and a weaker one:

> A quarterly regulatory filing is checked offline, once, by a reviewer who is not waiting on a
> progress bar. Four seconds to establish that every check was working *on this document* is
> affordable there. It would **not** be affordable in an interactive path, and this measurement is
> the reason to say so before someone puts it in one.

The optimisation that would close most of the gap is real and is **not taken**: the CEL activation
could be built once and mutated in place per canary. It is refused because `apply()` returning a
COPY is what makes `test_w__apply_returns_a_copy` assertable by identity, and *"the received
artifact is never touched"* is the property this layer exists to demonstrate. Trading it for
latency in the layer whose subject is trustworthiness would be the wrong trade, and it is recorded
here so that a later reader knows it was considered.

### Superseded

`PERF-CANARY` (~35 ms) was superseded by `PERF-CANARY2` when §0.4 added the anti-canary, which
doubles the loop. That change is inherited by the row above.
