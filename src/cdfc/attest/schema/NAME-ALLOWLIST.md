# `NAME-ALLOWLIST.md` — every property name that trips the advisory scan, with its argument

**The blocking rule is an EXACT, case-insensitive match** on
`result | status | pass | passed | passing | compliant | conformant | ok | success | clean`.
A property with any of those names fails the build at any depth.

**The advisory rule is a SUBSTRING scan over the same words**, and it does not block. It exists so
that `overallStatus` cannot arrive unseen. Its hits are listed here, each with a written argument,
and `tests/contract/test_contract_attestation.py::test_contract__every_advisory_hit_is_allowlisted_with_an_argument`
asserts the hit set and this table's key set are **equal in both directions**:

- a hit that is not here **fails the build** — a name nobody justified;
- an entry here that is not a hit **also fails the build** — a justification for a name that is no
  longer in the schema is a permission left lying around, and the next name that matches it inherits
  the argument.

**An entry with no argument is refused by the loader** (`schema_walk.allowlist()` raises below 40
characters). Same rule as `docs/EQUIVALENT-MUTANTS.md`, and for the same reason: a list of exceptions
is only worth having if each one had to be argued.

## The entries

| property | argument |
|---|---|
| `canariesPassed` | A count of executions of OUR OWN INSTRUMENT, bounded above by `canariesRun`. It cannot be read as a verdict about the filing, because a run in which it EQUALS `canariesRun` is exactly a run in which we have made no claim about the filing at all — it says every check demonstrated itself, and says nothing whatever about whether the document is correct. |
| `antiCanariesPassed` | The same quantity for the anti-canary arm: the count of admitted checks that did NOT fire on a filing known to be correct. High is the absence of a defect in the instrument, not the presence of a virtue in the filing, and it is bounded by `antiCanariesRun` in the same way. |
| `antiCanariesNotPass` | A count of what OUR OWN INSTRUMENT returned on a filing known to be correct, under the weaker of two readings. `plan/05` writes the anti-canary as `state != PASS`; this build turns the DISPOSITION on `state == FAIL` and publishes both counts so the weaker reading is not taken quietly. The name has to carry `Pass` because the reading it names is literally *not PASS* — and like its two neighbours it is bounded by `antiCanariesRun` and says nothing whatever about the filing. |

## What is NOT here, and why the list is short

The schema declares no `result`, `status`, `verdict.pass`, `compliant` or `clean` property at any
depth, so the blocking scan finds nothing at all. The three entries above are the entire advisory
surface, and all three are counts of what the **instrument** did — never of what the **filing** is.

That distinction is the whole content of the rule. A property may be named for something that
passed, provided the thing that passed is ours.
