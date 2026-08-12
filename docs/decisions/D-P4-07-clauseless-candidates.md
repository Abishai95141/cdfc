# D-P4-07 — a candidate with no statutory clause declares why (re-keyed by arbitration C2)

**The defect.** `clause: Clause | None` is typed optional, and the harvest makes it `None` for
every harvested candidate: their relations are derived from the workbook's own formulas and
validations and cite no regulation. G0's six rejection reasons (`g0.quote_not_located`,
`g0.quote_ambiguous`, `g0.span_mismatch`, `g0.proviso_undisposed`, `g0.proviso_arithmetic`,
`g0.declared_proviso_missing_emission`) **all presuppose an instrument to locate a quote in**, and
nothing said what G0 does with a candidate that cites no regulation. Both available branches were
broken: **reject**, and ALR's five `>= -1e17` bounds never reach G3, so D-REJECT — the flagship
demonstration that the gate is not decorative — is unreachable; **skip**, and the funnel's first
stage reports a pass it did not compute.

**Decision (arbitration C2) — the third thing, and it is strictly better than either branch.**

Obligations gain a **`source: STATUTE | TEMPLATE`** discriminator. A harvested predicate implements
a relation the **regulator's template** encodes; a hand-authored one implements a clause the
**statute** states. Both are real obligations; they are not the same kind of thing, and collapsing
them is what made this irreconcilable.

- Harvested candidates are minted `OBL-TEMPLATE-<sheet>-<ref>` with `source: TEMPLATE`, and **G0
  runs for real** against the template relation. The earlier ruling — `obligation_id` stays `None`,
  candidates take `SKIPPED_NOT_APPLICABLE` at G0 — is **deleted**. It made G0 decorative for every
  harvested candidate, and *a gate stage that cannot fail is this product's own failure mode wearing
  a gate's clothes.*
- The published figure is **two numbers, never one**:
  `predicates_with_a_STATUTE_obligation / N` and `predicates_with_a_TEMPLATE_obligation / N`.
  Publishing either alone is wrong: the first alone conceals that these predicates are grounded in
  a real regulator artifact; the second alone conceals that **not one of them is grounded in the
  statute.**

**The envelope owns the field that makes the disclosure checkable.** `clause_absent_reason` is
required and non-empty **iff the candidate's obligation has `source == TEMPLATE`** — equivalently
iff `clause is None`, since only a STATUTE obligation carries a `Clause` — from a closed
three-member vocabulary (`derived_from_template_formula`, `derived_from_data_validation`,
`derived_from_template_constant`), and it is inside `envelope_projection()` so it cannot be added
or changed without a new identity.

**Note what C2 does to this field: it gives it one instance per harvested candidate instead of
zero.** Under the other branch every candidate would have had an obligation, `clause is None` would
have been read as "nothing to explain", and the guard would have been a required field with no
instances — *this project's own definition of a green test with no information in it.* Re-keyed on
`source`, it fires on every harvested candidate and asks the question that is actually live: **why
does this predicate cite no statute?**

**The objection to minting an obligation, answered rather than dismissed.** The worry was that the
quote would be the reader's own parse and `find(quote)` would succeed by construction. The quote is
the **verbatim formula or data-validation text**, located in a content-addressed rendering of the
pinned blank — so the check catches **a harvest run against a different template version**, which
is a real failure mode with a real reject path.

**Mechanised by**
- `test_envelope__clauseless_candidate_declares_why` — both directions.
- `test_envelope__a_cited_clause_may_not_also_carry_an_absence_reason` — the field explains an
  absence; it is not an annotation.
- `test_harvest__obligation_coverage_is_published` — both ratios render or neither does.
