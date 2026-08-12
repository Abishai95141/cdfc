# D-P4-01 — there is no `REJECTED` predicate state

**Question the spec leaves open.** Audit §V.7.5 says *"confirm before the schema is written"*, and
the decomposition makes P4-B1 the confirming build.

**Decision. `PredicateState` stays four-valued: `ACTIVE`, `PROVISIONAL`, `QUARANTINED`,
`WITHDRAWN`.**

A rejected candidate never acquires a `predicate_id`. It becomes a **rejection row keyed by
`candidate_sha256`** with `predicate_id NULL`. A re-submitted candidate gets a new
`candidate_sha256`, and ids are never reused.

**Why.** A `REJECTED` state would require a rejected thing to have a predicate identity — and a
predicate identity is what the registry admits. The moment a rejection carries a `predicate_id`,
two things become possible that must not be: a rejected predicate can be counted in a library
total, and a re-submission can silently inherit the id (and therefore the admission record) of the
thing that was rejected. Keying the rejection on the *candidate* digest keeps the two populations
disjoint by construction rather than by a status filter somebody has to remember to apply.

**Alternative it beat.** Five states with a `REJECTED` member and every query filtering it out.
Rejected because "every query filters it out" is a discipline, and a discipline that is load-bearing
for a published count is the thing this project is about.

**Mechanised by**
- `tests/unit/test_envelope.py::test_predicate_state__has_exactly_four_members`
- `tests/contract/test_contract__predicate_schema.py::test_contract__rejection_has_no_predicate_id`
