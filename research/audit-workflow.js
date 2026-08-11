export const meta = {
  name: 'gift-spec-audit',
  description: 'Independent audit that the merged specification landed every reconciliation ruling and is internally consistent',
  phases: [{ title: 'Audit', detail: 'ruling-by-ruling check plus cross-part divergence hunt' }],
}

const S = '/Users/abishaikc/Gift/research/synthesis'
const OUT = '/Users/abishaikc/Gift/spec'

phase('Audit')

const audit = await agent(
  `You are the AUDITOR of a specification merged from three contradictory drafts under a binding
reconciliation ruling. Verify the merge landed. Do not be generous. Do not re-research anything.

Read:
- ${S}/D-reconciliation.md   — the BINDING instruction set: 31 contradictions each with a ruled
  "Replacement:" sentence, 9 surviving falsehoods, 11 unwarranted-confidence restatements, 12 blocking
  gaps, 3 innovation restorations.
- ${OUT}/01-problem.md, ${OUT}/02-architecture.md, ${OUT}/03-stack.md, ${OUT}/04-path.md

A mechanical pre-pass has already been run and found: (a) every banned string appears ONLY inside
withdrawal/ban tables where it is quoted as dead with its replacement — zero live violations;
(b) the headline triple 3,747 / 2,373 / 1,374 / 280 appears in all four parts; (c) G1 is decided as
the CELL and G3 as MILLI_USD_MILLION consistently; (d) all twelve gaps G1-G12 appear. Do not redo
those. Your job is the SEMANTIC pass the grep cannot do.

Check, using Bash grep and Read to quote evidence:
1. **Each of D's 31 contradictions (C1-C31).** Does the spec state D's ruled Replacement, or one of the
   two losing versions, or a NEW third version? Report per contradiction: LANDED / NOT-LANDED /
   NEW-DIVERGENCE, with the file, line and the quoted text you judged on. Pay particular attention to
   C1-C9 (the verdict model), C15-C17 (the settling experiment and the gates) and C18-C22 (component
   decisions taken in opposite directions).
2. **D's 11 unwarranted-confidence restatements (U1-U11).** Is the corrected phrasing used? U1 is the
   most important: the point that NONE of the 280 predicates is admissible under the spec's own gate,
   and that the currently defensible settled fraction is therefore 0%, must be present, prominent and
   used as an asset — not buried in a footnote and not quietly dropped.
3. **D's 3 innovation restorations (I1 undetectable-in-principle mutant class, I2 INVALID as a liveness
   proof, I3 the criterion-source substitution).** Present in the bolder-and-truer form D specifies, or
   sanded off again? Quote the sentence that carries each.
4. **Cross-part semantic divergence.** Any claim, number, name, enum value or decision that appears in
   two parts with two different values or two different meanings. This is the most serious class of
   finding. Check at minimum: item state count and names, reason-code count and families, the closure
   invariant terms, the five evaluation-contract rules and their emitted state+reason, the gate count
   and gate ORDER, the settling-experiment n and its retain/delete thresholds and its power figures,
   the predicate language decision, the structured-output decision, the signer decision, the licence
   warrant label on every component, and what is described as BUILT versus SPECIFIED.
5. **Warrant discipline.** Any number stated without a denominator or without a warrant label, in a
   document whose own thesis is that this must never happen. List the worst offenders with line refs.

Write the full audit to ${OUT}/05-audit.md.

Then FIX what can be fixed safely: for any NOT-LANDED or NEW-DIVERGENCE with an unambiguous correct
value under D, edit the offending file directly with the Edit tool. Surgical edits only — do not
rewrite sections, do not restructure, do not add new claims. Record every edit you make in the audit
file with before/after.

Return a compact summary: counts LANDED / NOT-LANDED / NEW-DIVERGENCE, the edits you made, the
problems you could NOT safely fix, and a one-line verdict on whether the specification is internally
consistent enough to hand to its owner.`,
  { label: 'audit', phase: 'Audit', effort: 'xhigh' },
)

return { audit }
