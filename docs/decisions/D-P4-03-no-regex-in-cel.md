# D-P4-03 — `matches()` is not in the admitted subset

**Decision: banned.** A format check routes to a **host function**, which cannot be registered
without published test vectors and a mutation score.

## The stated reason was wrong for the pinned runtime, and this is the correction

The plan gave the reason as: *"`celpy` uses Python `re`, not RE2; a step-count budget does not
bound backtracking, so the only guard would be the wall-clock kill."* **That is false for
`cel-python==0.5.0`, the version pinned in `requirements.lock`.** It calls `re2.search` from
`google-re2`; `import re2` is at `celpy/evaluation.py:83` and `matches()` is implemented at
`evaluation.py:410`.

**MEASURED, 12 Aug 2026**, on the classic catastrophic-backtracking pattern `^(a+)+$` against
`"a"*n + "!"`, evaluated through `celpy`:

| n | via `celpy` (`re2`) | Python `re` |
|---:|---:|---:|
| 10 | 0.42 ms | — |
| 16 | 0.15 ms | — |
| 20 | 0.13 ms | — |
| 24 | 0.12 ms | 706 ms |

The engine is linear-time. **The plan's re-open rule — *"admit `matches()` only if the pinned
runtime's regex engine is proven linear-time and a pathological-pattern benchmark is recorded"* —
is therefore satisfied on the engine half.** It is recorded here rather than quietly dropped.

## The ban stands, on the reason that was always load-bearing

A regex inside an envelope is **a check nobody qualified**. It has no test vectors, no mutation
score and no author. Everything else that decides whether a filing is admissible in this system
carries all three; a regex would be the single exception, and it would be the one deciding
identity.

**And the cost is measured, not hypothesised: the obvious registration-number regex fires on 87 of
228 live FMEs.** A pattern that rejects 38% of really-registered entities would have been written
into an envelope, admitted `BLOCKING`, and printed as a finding — with nobody having measured it,
because the envelope has no place to put a measurement of a regex.

A host function has somewhere to put it. `HostFn` carries `test_vector_sha256` and
`mutation_score_json`, `HostFnRegistry.register` refuses one without them, and
`test_nc__X04c_a_host_function_without_vectors_does_not_load` is the control.

**Two smaller reasons, recorded but not load-bearing.** `google-re2` is a native extension, so a
predicate's admissibility would depend on a wheel building on the target platform. And RE2's
syntax is a subset of Python's, so a pattern authored against `re` semantics can behave
differently — a difference that would surface as a changed verdict, not as an error.

## Re-open rule, restated

Admit `matches()` only when a format check inside an envelope can carry **its own test vectors and
its own mutation score**. Until the envelope has fields for those, the correct home for a format
check is the host-function registry, which already has them. The engine question is settled and is
not the barrier.
