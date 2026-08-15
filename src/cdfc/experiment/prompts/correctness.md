You are proposing a single executable check over one prescribed regulatory reporting template.

You will be given:

1. `CLAUSE` — one verbatim sentence from a pinned statutory instrument, with its character span.
2. `SCHEMA` — the induced schema of the template: every field key, its type, and its sheet and
   cell address. This is the complete set of names you may read. There are no others.
3. `HOST_FUNCTIONS` — the closed set of host functions you may call, with their signatures.

Produce **one YAML predicate envelope** and nothing else. No prose before it, no prose after it,
no code fence.

## The regime you are in

This is the **correctness** regime. Propose the check that establishes the clause is **satisfied
by the values in the filing**. Prefer a check that would fire on a filing that violates the
clause, and would not fire on one that complies.

## Rules that make a proposal admissible

- `expr` is a CEL expression. It must evaluate to a boolean. Python is not accepted and is not
  executed.
- Every key you read must appear in `schema_keys`, and every key in `schema_keys` must be read by
  one of `applicable`, `expr` or `witness`. This is checked by a static walk of your expression in
  both directions, and a mismatch in either direction is a rejection.
- `clause.quote` must be **the exact substring** of the instrument you were given, character for
  character, and `clause.span` must be the span at which it occurs. It is checked by string search
  and it must locate **uniquely**.
- Every host function you call must be in `HOST_FUNCTIONS`. There are no others available.
- If the clause carries a proviso or an exception, either implement it or declare it in
  `clause.provisos` with its disposal. A predicate that implements the main rule and silently
  omits the exception is rejected.
- `claims_fault_classes` must name the fault classes this check claims to reject. It is measured
  against a mutation campaign, and a claim you do not meet is a rejection rather than a discount.

## What will happen to your proposal

It is put through five gates in a fixed order: the clause locates and its provisos are disposed of;
the expression parses, binds and executes; a satisfiability proof arm; a mutation kill rate over
seeded faults verified observable by recalculation; a degeneracy check; and a false-failure rate
over a clean corpus. Roughly one candidate in twenty is expected to survive. **A proposal that is
rejected is recorded with the gate that rejected it and the number that decided it.**

Do not attempt to make a proposal that survives by being trivially true or trivially narrow. A
predicate that cannot fire is caught by the degeneracy arm, and one that always fires is caught by
the false-failure rate.

If you cannot produce an admissible envelope for this clause, produce an envelope with
`kind: no_predicate` and a `rationale` naming what makes it undecidable over this schema. That is a
useful answer and it is counted as one.
