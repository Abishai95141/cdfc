# `docs/SELFCHECK-THRESHOLDS.md` — the liveness layer's pre-registered constants

**Append-only.** A constant is never edited in place: a change is a NEW ROW with its own date and
its own argument, and the superseded row stays byte-unchanged. A threshold whose history has been
rewritten cannot be shown to predate the number it judges.

`tests/unit/test_thresholds.py::test_th__ceiling_is_pre_registered` reads
`src/cdfc/selfcheck/thresholds.py::PRE_REGISTERED` and fails the build if a constant here and a
constant there disagree — in either direction. It reads the module's own map rather than a second
list in the test file, because a second list is the one that drifts.

## The rows

| constant | value | status | dated | argument |
|---|---:|---|---|---|
| `CANARY_INAPPLICABLE_CEILING` | `0.25` | **PRE-REGISTERED** | 14 August 2026 | `plan/05` §P10-B1's file list fixes it at 0.25 before any inapplicability rate was measured on this corpus. It is the fraction of canary ATTEMPTS that may be inapplicable **or** indeterminate before the run is `INVALID`. Above it, a majority of the instrument was not demonstrated on this filing and no coverage is declared over it. |
| `MAX_WITNESSES` | `3` | **PROVISIONAL** | 14 August 2026 | `plan/05` §5.1 is explicit: *"Nothing in the corpus argues for 3."* The constant ships labelled and `docs/measurements/P10-canary-cost.md` publishes the inapplicability curve at `MAX_WITNESSES ∈ {1, 3, 5}`. It is closed by that curve or it keeps rendering `PROVISIONAL`. |

## Why the ceiling's numerator is `inapplicable + indeterminate`

Adversary **F18**. The two are reported apart everywhere else and counted together here, and that
is the only combination that is honest in both directions.

- **Inapplicable** is a fact about the filing: every stored kill case for this predicate changes
  this document not at all, so the predicate cannot be asked to catch anything here.
- **Indeterminate** is a fact about **us**: the recalculation ran through a cell this evaluator
  cannot compute, so we cannot say whether the fault would have been visible.

Pooling only `inapplicable` would report our evaluator's coverage as the fault's invisibility. But
a run in which we cannot say whether a third of the checks work has not demonstrated liveness
either — so both count toward the ceiling, and `livenessProof` renders `canariesIndeterminate`
beside `canariesInapplicable` so a reader can always take them apart again.

## Why `rows == 0` exceeds the ceiling rather than passing it

A loop that attempted nothing has an undefined rate. Returning *"the ceiling was not exceeded"*
would let a build with **no canary layer at all** pass the disposition — which is adversary F6, the
same shape that made NC-C03 satisfiable by a system with no `src/cdfc/selfcheck/` in it.

## What is NOT pre-registered here, and why

**There is no threshold on Cohen's κ, and inventing one would be the invention this specification
refuses.** `plan/05` P10-B3 states the decision rule instead: if κ < 0.6 the two raters reconcile
in writing, the reconciliation is appended as round 3 with its own hash, and both the pre- and
post-reconciliation κ are published. Never a silent re-rate. See
`docs/measurements/P10-residue.md` for this build's κ, which is **UNMEASURED** with its blocker
named.
