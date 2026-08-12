# D-P4-04 — the CEL agreement claim is a DIFFERENTIAL, not a CONFORMANCE run

**Question the spec leaves open.** How is the CEL conformance claim obtained if the official suite
cannot be driven against `celpy` inside the phase budget?

**Decision. Fall back to a two-runtime differential harness, and label it
`DIFFERENTIAL, not CONFORMANCE` everywhere the number appears** — in the measurement file, in
G-CELPY's record, and on any surface that quotes it.

## Why the fallback was taken

The official suite is a set of textproto files driven through a conformance server; wiring that to
a Python library is a build-system exercise, and D-P4-04 caps the attempt at two days by
construction. The fallback was taken.

## What was built instead

`tools/cel_conformance.py` runs every expression in the admitted grammar's coverage set through
**both** runtimes and diffs the results, in two slices reported separately.

| runtime | role |
|---|---|
| **`cel-python` (`celpy`)** | the runtime the registry root is qualified against; recorded in `qualified_against.evaluator_version` on every predicate envelope |
| **`cel-expr-python`** | the check on it — **Google's own CEL runtime with the C++ core**, i.e. the reference implementation rather than a second Python interpretation of the spec |

That second arm is stronger than the plan assumed was available. An agreement between a third-party
port and the reference implementation is much better evidence than an agreement between two ports.
**It does not turn a differential into a conformance run**, and the label does not change.

## Why it is weaker, stated rather than implied

**Two implementations wrong the same way are invisible to a differential**, and that is not
hypothetical in this project: two of its own readers agreed on a formula-cell count while
disagreeing about the formulas. What this harness establishes is that `celpy` does not diverge from
the reference on the constructs we admit. What it cannot establish is that the CEL specification
means what both of them do.

## The error-semantics slice, and why it is reported on its own

The CEL specification says an operand error in `&&`/`||` *"will be ignored"* when the other operand
determines the result. **If the two runtimes differ there specifically, the pre-flight guard's
necessity argument behaves differently between them** — the guard exists because an absent key
becomes an error, and whether that error is absorbed decides whether a predicate can return `PASS`
over a key nobody checked was present.

A single blended percentage would hide the one disagreement that changes a design decision. So the
file publishes two figures and never their average, and the left-operand cases
(`(1/0 == 1) || true`) are in the set because the right-operand ones are satisfied by
short-circuiting alone and prove much less.

## Why the reference runtime is not on the verdict path

It is a native extension. A verdict path that depends on a wheel building for the target platform
is a verdict path that can vanish, and the predicates' qualification records name `celpy` for that
reason. `cel-expr-python` is pinned in `requirements.lock` as a **test** dependency and appears in
no runtime licence row.

## If the fallback had failed

Recorded because it did not, and a reader is entitled to know what the branch was: if neither
runtime were sound on error semantics, the repair is to **ban `&&` and `||` at the top level of
`expr` entirely**. Conjunction then lives in the harvest — two predicates instead of one — the
settled numerator is unaffected, and the pre-flight guard's argument stops depending on a runtime
behaviour nobody could verify.
