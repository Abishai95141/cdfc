export const meta = {
  name: 'gift-plan-arbitrate',
  description: 'Apply the arbitration ruling serially across the plan and renumber the negative-control catalogue',
  phases: [
    { title: 'Apply', detail: 'one writer applies C1-C9 across all documents, then renumbers the catalogue' },
    { title: 'Confirm', detail: 'independent confirmation that every seam is closed and no reference dangles' },
  ],
}

const P = '/Users/abishaikc/Gift/plan'

phase('Apply')
log('Serial arbitration pass — one writer, all documents')

const applied = await agent(
  `You are the SOLE WRITER for this pass. The previous repair used four parallel owners on a coupled
document set and produced eight new contradictions plus two brand-new id collisions inside the repair for
id collisions. **A coupled specification admits exactly one writer at a time. You are it.** Work serially,
document by document, and do not parallelise.

READ, IN THIS ORDER:
1. ${P}/11-arbitration.md — THE BINDING RULING. Nine arbitrations, C1 through C9. Every one is decided.
   You are not re-opening any of them. Your job is to make the documents say what the ruling says.
2. ${P}/10-repair-verification.md — especially section 3 (the eight contradictions, with file and line
   references) and section 4 (the full catalogue-id enumeration: the ten live duplicates, the four
   competing band tables, the orphan ranges, and which documents fail band conformance).
3. The documents you will edit: ${P}/00-decomposition.md, ${P}/01-validation-methodology.md,
   ${P}/02-phases-foundation.md, ${P}/03-phases-verdict.md, ${P}/04-phases-qualification.md,
   ${P}/05-phases-probes-attestation.md, ${P}/06-phases-model-and-clause.md,
   ${P}/07-phases-surface-and-transfer.md, ${P}/09-operating-manual.md

## YOUR TASK, IN TWO PARTS AND IN THIS ORDER

### PART 1 — APPLY C1 THROUGH C8

For each arbitration, find EVERY occurrence of the losing text across ALL documents and change it. Use
Bash grep to enumerate occurrences before editing, so you do not miss one; a ruling applied in four of five
places is worse than one applied nowhere, because it looks settled.

Specific care:
- **C2 is the largest change.** It adds a "source: STATUTE | TEMPLATE" discriminator to the obligation
  model, makes G0 run for real against template-derived obligations, and replaces every published
  "0/280" with the two-number form. Touch the envelope definition, the G0 gate definition, the P7 funnel,
  and every place a harvest-obligation count is published.
- **C3 changes a retention rule that other numbers depend on.** After applying it, check that no document
  still claims a scope removal that the new rule forbids.
- **C1 and C6 are pre-registered constants.** After applying, grep for the losing values (25, 114) and
  confirm every survivor is a legitimate different quantity, not the retired one.
- **C4 deletes a test rather than renaming it.** Confirm no reference to the deleted name survives.

### PART 2 — RENUMBER THE CATALOGUE (C9)

Only after Part 1 is complete and verified by grep.

1. Enumerate every "NC-" id defined or referenced in every plan document, with its file, line and content.
2. Build the canonical registry in ${P}/01-validation-methodology.md: one band table with a reserved
   unallocated range per band, and every entry defined exactly once.
3. Where two documents define the same id with different content, **both get new ids and the contested id
   is retired permanently** — never reassigned. Maintain an explicit RETIRED list.
4. Rewrite every reference in every document to the new ids.
5. Publish the complete old-to-new mapping plus the retired list in "01".
6. Delete the three non-canonical band tables.
7. Add the meta-tests named in the ruling: "test_nc_meta__ids_are_unique",
   "test_nc_meta__ids_are_defined_in_the_registry", "test_nc_meta__no_orphan_guard",
   "test_nc_meta__no_dangling_reference".

## RULES

- **Surgical edits only.** Do not restructure, do not renumber phases, do not rewrite sections that the
  ruling does not touch.
- **Never resolve a collision by silently picking a winner.** The ruling says both contested definitions
  get new ids. Follow it. A silent rename that hides a collision is itself the defect being repaired.
- **Verify with grep after each arbitration**, not at the end.
- Append to each document you edit a section "## ARBITRATION APPLIED (C1-C9)" listing which rulings touched
  it and where.

Return a compact summary: per arbitration, the number of occurrences changed and the files touched; the
catalogue statistics before and after (defined ids, duplicates, orphans, dangling references, retired
ids); and anything the ruling did not cover that you had to decide, flagged explicitly.`,
  { label: 'arbitrate', phase: 'Apply', effort: 'xhigh' },
)

phase('Confirm')

const confirmed = await agent(
  `You are confirming an arbitration pass. Be mechanical and be hard. Do not accept a claim without
running the check yourself.

Read ${P}/11-arbitration.md (the ruling) and ${P}/10-repair-verification.md section 3 and section 4 (the
original defects). Then verify against the actual documents in ${P}/ .

Run these checks with Bash and report each as PASS or FAIL with the evidence:

1. **C1** — grep every plan document for the retired deviation threshold value and for the formula form.
   The frozen integer must appear with its derivation, its corpus hash and its date. PASS only if no
   document still states the threshold as a live formula or as the retired value.
2. **C2** — the obligation "source" discriminator exists; G0 is defined as a real, failable check; every
   published harvest-obligation count is in the two-number form. Grep for the bare single-number form and
   confirm every hit is either the STATUTE count or the TEMPLATE count, correctly labelled.
3. **C3** — the retention rule appears in exactly one normative place and every document that removes an
   item from the denominator obeys it. Confirm the field is both written AND read.
4. **C4** — the deleted test name appears nowhere; the surviving enumeration closes arithmetically.
5. **C5** — no gate, severity tier or published rate anywhere cites the synthetic corpus class.
6. **C6** — the retired figure does not survive as a critical-path number in any document.
7. **C7, C8** — one name each, no orphan guards, and the deleted documentation path is gone.
8. **C9 — THE CATALOGUE, and this is the one that has failed twice.** Enumerate with Bash every "NC-" id
   across every plan document. Report: total defined, total referenced, duplicates (must be 0), orphans
   (defined but never referenced — must be 0), dangling (referenced but never defined — must be 0),
   retired ids (must never be redefined), and how many band tables exist (must be 1).
   **Write the enumeration script into ${P}/scripts/catalogue_check.py so the check is reproducible**, and
   report its output verbatim.
9. **A NUL-byte and encoding scan of every plan document, with a positive control**, because a raw NUL
   previously made grep skip an entire file and would have made the id-collision CI gate run green over
   the largest instance of the problem. Use a binary read, not a shell pattern — a shell cannot pass a NUL
   as an argument, so the obvious test matches everything and reports a false positive on every file. Show
   the positive control.

Write the confirmation to ${P}/12-arbitration-confirmed.md . Fix any dangling reference yourself where the
correct target is unambiguous under the ruling, and record what you changed.

Return: the count of PASS and FAIL, the catalogue statistics, and a one-line verdict on whether the plan is
now internally consistent enough to build from.`,
  { label: 'confirm', phase: 'Confirm', effort: 'xhigh' },
)

return { applied, confirmed }
