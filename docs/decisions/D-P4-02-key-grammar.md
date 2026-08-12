# D-P4-02 — the `schema_keys` grammar

**Question the spec leaves open.** §II.4.1's example writes `intro.tbl15.row[*].scheme_type` while
the `expr` beside it reads `filing.intro.tbl15.rows` — root dropped, segment pluralised
differently.

**Decision. Keys are written in full: root included, segments verbatim from the P3 fact model,
`[*]` for a comprehension-bound repeated node.**

    filing.intro.tbl15.rows[*].scheme_type
    template.vocab.scheme_type

**Why.** A key grammar that cannot say **which document** it read cannot express the defect
NC-D01c exists to catch: a vocabulary resolved from `filing` instead of `template`. Under the
root-dropped form, `vocab.scheme_type` is the same key whichever document supplied it, and a filer
who edits a vocabulary and then satisfies a membership check against their own edited vocabulary
is invisible to every gate downstream.

The `[*]` marker is not decoration either. It is what distinguishes *the column* from *one cell of
it*, and `bound_cells` — the static upper bound on what a predicate settles — reads it.

**Consequence, stated because it changes a named artifact.** The fixture rewrites the spec's
example with the root restored. Where this document and the spec's illustrative block differ, this
one is normative and the difference is deliberate.

**Mechanised by**
- `tests/golden/test_predicate_envelope.py::test_golden__envelope__P0041_digest` — the value
  assertion beside the digest is the key tuple itself.
- `tests/property/test_prop_ast_walker.py::test_prop__declared_key_grammar_roundtrips`
