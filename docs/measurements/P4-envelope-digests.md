# P4-B1 — envelope digests

`code_sha256(c) = sha256(jcs(envelope_projection(c)))`, lowercase hex. RFC 8785 canonical JSON,
UTF-16 code-unit key ordering, floats refused. The projection is generated from
`dataclasses.fields()` at runtime, so it covers every field of the record by construction —
`tests/property/test_prop_envelope.py::test_prop__every_envelope_field_is_covered_by_the_digest`
perturbs each field in turn and asserts the digest moves.

**BOTH DIGESTS MOVED AT P7-B1, dated 13 Aug 2026, and the reason is a defect.** `obligation_id`
gained a construct-kind discriminator — `OBL-TEMPLATE-<F|V>-<sheet>-<ref>` — because without it a
cell carrying BOTH a formula and a data validation minted ONE id for TWO different obligations.
FME's `1. Introduction!D17` is exactly that cell: `=SUM(D18:D20)` and a `whole >= 0` validation.
The obligation's verbatim quote would have been whichever harvest class ran last, and one of the
two predicates would have been checked at G0 against a construct it was not derived from. One
instance across all nine workbooks, found by an equality assertion in `harvest()`. `obligation_id`
is inside `envelope_projection()`, so every affected candidate is correctly a DIFFERENT predicate.

**Warrant: MEASURED.** Produced by `src/cdfc/predicates/canonical.py` from the committed fixtures.
These are properties of *our code* — they may move, with a recorded reason. Moving one without
recording it fails `tests/golden/test_predicate_envelope.py`.

| fixture | type | `code_sha256` |
|---|---|---|
| `fixtures/predicates/good/P-0041__scheme-type-membership.yaml` | `Candidate` | `cfa3792f3157be6b93d0355778c3ab4be48fc8b7b5d48fb16668fbbab1c6a42f` |
| `fixtures/predicates/good/P-0007__intro-D17-integer-bound.yaml` | `Predicate` | `5848bc8a15234c2c73a620603d97d2a9f243fee9f324176571b6a04405decce3` |

Both are bound to template `7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39`
(Reporting Format for Fund Management Entities).

## What the digest covers, and why the type is inside it

The projection carries `__envelope_type__`. A `Candidate` and a `Predicate` whose common fields
are identical are **different things**: one has been through the gates and one has not. A digest
that could not tell them apart would let an unqualified envelope inherit a qualified one's
admission record, which is the barrier the two types exist to enforce.

## What it does not license

That either predicate means what its clause means. Neither cites a clause: both are
`obligation_source: TEMPLATE`, and the published pair for the harvest is
`predicates_with_a_STATUTE_obligation / N` beside `predicates_with_a_TEMPLATE_obligation / N`. A
digest says an envelope did not change. It says nothing about whether the relation it encodes is
the relation a regulation requires — **NC-N01**, where a negative control is impossible.
