export const meta = {
  name: 'gift-spec-merge',
  description: 'Merge the three synthesis drafts into one authoritative specification, applying every reconciliation resolution',
  phases: [
    { title: 'Merge', detail: 'four part-writers apply the 31 resolutions, 9 deletions and 3 restorations' },
    { title: 'Audit', detail: 'independent check that every resolution landed and no banned string survived' },
  ],
}

const S = '/Users/abishaikc/Gift/research/synthesis'
const L = '/Users/abishaikc/Gift/research/lanes'
const OUT = '/Users/abishaikc/Gift/spec'

const PRE = `You are writing one part of THE authoritative specification for this program. It replaces three
overlapping drafts that contradict each other in 31 places.

READ THESE, in this order, with the Read tool. This is a merge-and-correct job, NOT new research —
do not run web searches, do not re-derive facts, do not add claims that are not already in these files:

1. ${S}/D-reconciliation.md  — READ THIS FIRST AND IN FULL. It is the instruction set. It lists 31
   contradictions with a ruled "Replacement" sentence for each, 9 surviving falsehoods to delete, 11
   unwarranted-confidence restatements, 12 blocking gaps, and 3 sanded-off innovations to restore.
   Every "Replacement:" line in D is BINDING. Where D rules that A is right, use A. Where D rules B is
   right, use B. Where D says a number must be deleted, it must not appear anywhere in your part.
2. ${S}/A-problem-and-architecture.md
3. ${S}/B-stack-and-flow.md
4. ${S}/C-build-path.md
5. Any lane file in ${L}/ you need to check a number against. Lane files beat the drafts.
   Note ${L}/L15-live-register-probe.md carries a CORRECTION banner at the top: its central conclusion
   was wrong and lane L08 §C.1-C.3 has the true finding. Use L08's version.

HARD RULES:
- **Every number carries its warrant and its denominator.** Use MEASURED / VERIFIED-AT-SOURCE /
  SECONDARY / DERIVED / UNVERIFIED. A derived number never claims a stronger warrant than its weakest
  input. If D flagged a number as unwarranted, use D's corrected phrasing verbatim.
- **The ban list is absolute.** These strings must not appear as live claims anywhere:
  "555", "562", "17 decidable predicates", "sixteen commercial products", "functional equivalence"
  attached to +37-54, "Hypothesis (MPL-2.0)" as bare fact, "Z3 (MIT)" as bare fact, "in-toto ...
  UNVERIFIED", "8.23% of 12,925", "two model calls both short", "zero financial regulations encoded
  anywhere", "no analogue exists for a financial assertion", "the registry grows monotonically",
  "the register does not resolve registration numbers", "46% staffing", "Fifth Schedule Part A(g)",
  "a 90%-per-step agent is 57% reliable", "PASC names financial documents as a target".
  Use the corrected replacements D gives.
- **No ambiguity.** Every decision is stated as a decision, with the alternative it beat and the
  reason. Where D lists a blocking gap, either TAKE the decision D's "smallest thing that unblocks it"
  column suggests and mark it DECIDED, or mark it explicitly OPEN — USER DECISION with the exact
  question. Never leave it implicit.
- **Do not sand off the innovation.** D section 5 lists three novel claims that were narrowed past
  accuracy (I1 the undetectable-in-principle mutant class, I2 INVALID as a liveness proof, I3 the
  criterion-source substitution). Restore each in D's bolder-and-truer wording where your part touches
  it. Also keep D's note on "the verification problem and the capability problem are the same problem".
- Write for an engineer who will build it and a judge who will challenge it, in the same document.
- Target 4,000-7,000 words. Dense, no filler, no restating the brief. Tables and code blocks where they
  carry more than prose would. Markdown, starting at heading level 2 (##) — the assembler supplies the
  document title and the part heading.

YOUR PART:
`

phase('Merge')
log('Merging three drafts into one spec under the reconciliation ruling')

const parts = await parallel([
  () => agent(PRE + `## PART I — THE PROBLEM, THE EVIDENCE, AND THE CLAIM

Write to ${OUT}/01-problem.md :

1. **The problem**, stated so it is unambiguous and falsifiable. Who has it, what it costs them, how it
   is handled today, what specifically is absent. Use D section 6's executive verdict paragraph 1 as the
   spine but expand it. Include the general case (audit opinion / filing sign-off / sanctions
   disposition all end in "nothing wrong here") and the specific case (the FME quarterly return).
2. **The evidence base, corrected.** One table of every load-bearing quantity that survives, with:
   claim, exact number, denominator, source (arXiv id / URL / instrument), warrant label. This must
   reflect what lanes L01 and L02 actually verified — including the papers that turned out REAL, the
   attributions that were REFUTED, and the single-instrument concentration D flags in U4. State plainly
   which brief-era claims are now dead and why. Include the EBA deactivation figure with D's C13
   denominator, and the AuditFlow figure with D's ruled restatement.
3. **What we are actually building** — one paragraph a non-specialist understands, then one paragraph
   an engineer can implement against. Then the scope boundary: what it is NOT.
4. **The domain grounding.** What the rest of the world specifies for NAV-error materiality and what
   IFSCA does not — but carry D's ruling that the NAV-error WEDGE was correctly deleted with five
   measured reasons. The domain fact stays; the product framing does not. Be explicit about that split
   so nobody re-opens it.
5. **WHAT IS GENUINELY NOVEL.** Restore I1, I2, I3 in D's wording. Then state the single defensible
   novelty sentence that survives an adversarial reading. Then the three strongest "this already
   exists" objections a judge could raise and the exact rebuttal to each, with the source. Be honest
   about what is assembly of known parts, and argue why the assembly is the contribution if it is.
6. **The ban list** as a short closing table: dead string, why it died, what to say instead. This is
   the section the team reads before a pitch.`, { label: 'spec:problem', phase: 'Merge', effort: 'xhigh' }),

  () => agent(PRE + `## PART II — THE ARCHITECTURE

Write to ${OUT}/02-architecture.md :

1. **The layers, revised.** For each layer: exact input type, exact output type, whether it contains a
   model, its failure modes, its self-check, and the named component it reuses with the reason that
   component beat its runner-up. Apply every repair the adversary lane established. Say clearly which
   layers are BUILT, PARTIALLY BUILT and SPECIFIED — use D's C29 ruling verbatim on what is actually
   built, not C's overstatement.
2. **The corrected data-flow diagram** in ASCII, showing where the deterministic boundary is and where
   the (few) model calls sit. Note honestly how many model calls an honest implementation needs — D
   bans "two model calls, both short".
3. **THE VERDICT MODEL — this is the product's core object and the drafts disagreed most here.**
   Resolve per D C1-C9 exactly:
   - the **eight** closed item states, with the rule for each
   - the **30** reason codes across five state families, listed in full, namespaced
   - the closure invariant in B's **seven-term** form
   - the five-rule evaluation contract (applicable-false, expr-raises, budget-exceeded, cells_bound==0,
     declared-but-unimplemented proviso) with D's ruled state+reason for each
   - "method" (nine values incl. TEMPLATE_DIFF and DIFFERENTIAL), "warrant" (the runtime provenance
     lattice DETERMINISTIC/MODEL_EXTRACTED/DERIVED, composing by weakest input), "provenance"
     (COMPUTED/DECLARED), and "corpus_provenance" (six values, REGISTER-DERIVED spelling)
   - resolve D's G1: state whether the unit of the denominator is the CELL or the (field x obligation)
     PAIR, take the decision, and make every other number in the spec consistent with it.
4. **THE PREDICATE MODEL.** The full data structure. The language (take the execution-substrate lane's
   recommendation and say what it beat). The FIVE gates in D's C16 ruling with D's C7 ordering from G7,
   and D's C17 ruling that the experiment threshold and the registry threshold are DIFFERENT tests —
   state both. What a predicate carries permanently. How it is versioned when the template changes and
   what happens when a predicate silently becomes untestable. Resolve G2 (the FFR-to-severity
   thresholds) by pre-registering numbers.
5. **THE REPORT.** The output object schema, the signing envelope, and its exact relationship to OSCAL
   assessment-results, ISRS 4400 agreed-upon procedures, in-toto/DSSE and CycloneDX. Include the verdict
   state name that replaces the green tick. Show a worked example JSON with the MEASURED triple, never
   the deleted enumeration.
6. **The self-check layer** — restore I2 in D's wording: the verdict is conditioned on a proof obtained
   from the artifact under test in the same execution and withheld when that proof fails. Specify the
   mechanism (canaries / replay), its cost, and what makes the run INVALID.`, { label: 'spec:architecture', phase: 'Merge', effort: 'xhigh' }),

  () => agent(PRE + `## PART III — THE TECHNOLOGY STACK AND THE BACKEND FLOW

Write to ${OUT}/03-stack.md :

1. **The decision table.** Every technology choice: component, the layer it serves, the DECISION, the
   runner-up it beat, the evidence for the choice, the licence WITH ITS WARRANT LABEL (apply D's C20,
   F3, F4, F5 exactly — some licences were read at source, some only reported, and the difference must
   show), and the condition under which we would switch. Cover at minimum: workbook parsing, schema
   induction, formula evaluation/cross-check, regulation-text parsing and clause citation, the predicate
   language and its runtime, sandboxing, the fault-seeding harness, differential/relation execution,
   conformal/abstention, model provider and model per model-bearing step, data-validation substrate,
   storage and content addressing, attestation and signing, API framework, frontend, deployment.
   Apply D's C18 ruling on structured output and D's C19 ruling on the URI grammar.
2. **For each ADOPTED open-source project**: what exactly we use it for, what we explicitly do NOT use
   it for, licence implications for a commercial product, maintenance risk, and the fallback if it is
   abandoned. Be exact about the ones whose licence is not OSI-approved.
3. **THE BACKEND FLOW.** The online path end to end — a filing arrives, ... , a signed report exists —
   naming every step, its input, its output, whether it is deterministic, its failure handling, and
   where a human is required. Then the OFFLINE paths: predicate harvest, predicate synthesis,
   qualification, registry admission, re-qualification on template version change, and the instrument
   watcher that quarantines a predicate when its clause moves.
4. **The data model.** Tables/collections with columns, the content-addressing scheme, the registry
   schema, and exactly how a report is proven to re-derive. Apply D's G3 ruling on the money scale
   (one name, one definition, everywhere) and D's G12 ruling on the toolchain pin and LibreOffice.
5. **Performance and cost.** Measured runtime where measured, model token cost per filing with the
   model actually chosen, and what changes at 868 filings a year and at 100x.
6. **The interfaces.** The API surface (paths, methods, request/response shapes) and the screens,
   described precisely enough to build from without further questions. Apply D's C12 rename
   (settled fraction vs coverage) consistently in every path, key and label, and D's C23 ruling on who
   the surfaces are for.`, { label: 'spec:stack', phase: 'Merge', effort: 'xhigh' }),

  () => agent(PRE + `## PART IV — THE PATH, THE DELIVERABLE, AND WHAT IS STILL OPEN

Write to ${OUT}/04-path.md :

1. **The experiment queue**, re-ordered by what actually decides the design. For each: what it settles,
   its cost, its pre-registered threshold written before the run, and what it kills if it fails.
   The settling experiment must use D's C15 ruling exactly — the n, the retain threshold, the delete
   threshold, the single pre-committed extension and its threshold — because the drafts halved the
   sample while keeping the power table. Show the binomial power figures with the n they belong to.
   Include the two field observations (the IFSCA email; and resolve D's C31 on the administrator call
   by either scheduling it with its exact question text or recording that it was retired with the NAV
   wedge).
2. **THE DATED BUILD PLAN**, dependency-ordered: by 16 Aug (the application and the one link it needs),
   21-22 Aug (the two-day build with a hard cut line), 1 Sep - 30 Oct (the residency, milestone by
   milestone, each with a measurable acceptance test). Be honest per D's C29 about what is already
   built versus specified.
3. **THE DO-NOT-BUILD LIST** with the reason for each exclusion, including the things the research
   killed (the NAV-error wedge, the five original metamorphic relations, the supervisor as a user, and
   anything else D marks "correctly not restored").
4. **WHAT THE FINAL PROTOTYPE DELIVERS** — unambiguous. The exact demo script: what is on screen, in
   what order, what the operator says. The acceptance criteria that make the demo honest. Every number
   that will be on screen and where each one comes from, with its warrant. And the single sentence a
   judge should be able to repeat afterwards.
   CRITICAL: apply D's U1 ruling. The headline settled fraction is computed from predicates that are
   NOT YET ADMISSIBLE under our own gate, and D gives the corrected phrasing that turns this from a
   fatal objection into the strongest moment in the demo. Use it. Do not hide it.
5. **THE RISK REGISTER.** Every risk: probability, blast radius, early-warning signal, mitigation, and
   whether the research already retired it.
6. **THE TWELVE BLOCKING GAPS (D section 4.1).** For each: state the DECISION taken (use D's "smallest
   thing that unblocks it" column) and mark it DECIDED, or mark it OPEN — USER DECISION with the exact
   question and the deadline by which it must be answered. Nothing may remain implicit.
7. **THE SEVEN QUESTIONS ONLY THE USER CAN ANSWER (D section 4.2)**, verbatim in substance, ordered by
   deadline, each with what changes depending on the answer. Lead with the portal check — D grades it
   the only item that can end the programme and it costs ten minutes.`, { label: 'spec:path', phase: 'Merge', effort: 'xhigh' }),
])

phase('Audit')

const audit = await agent(
  `You are the AUDITOR. An authoritative specification has just been merged from three contradictory
drafts under a reconciliation ruling. Verify the merge landed. Do not be generous.

Read:
- ${S}/D-reconciliation.md  (the binding instruction set)
- ${OUT}/01-problem.md, ${OUT}/02-architecture.md, ${OUT}/03-stack.md, ${OUT}/04-path.md

Check, mechanically, and use Bash grep over ${OUT}/ for the string checks:
1. **Every one of D's 31 contradictions**: does the merged spec state D's ruled Replacement, or does it
   still carry one of the two losing versions, or a third new version? Report per contradiction:
   LANDED / NOT-LANDED / NEW-DIVERGENCE.
2. **Every one of D's 9 surviving falsehoods**: grep for the banned string. Report each as ABSENT or
   STILL-PRESENT with file and line.
3. **D's 11 unwarranted-confidence restatements**: is the corrected phrasing used? Especially U1 — the
   admissible-predicate-set-is-empty point must be present and used, not buried.
4. **D's 3 innovation restorations (I1, I2, I3)**: present, in the bolder-and-truer form, or sanded off
   again?
5. **D's 12 blocking gaps**: is each one either DECIDED with a stated decision, or explicitly marked
   OPEN — USER DECISION? List any left implicit.
6. **Internal consistency of the merged spec itself**: do the four parts agree with each other on the
   state count, the reason-code count, the denominator unit, the money scale, the gate count, the
   settling-experiment n, the headline triple, and every licence warrant label? Any number that appears
   in two parts with two values is a NEW-DIVERGENCE and is the most serious class of finding.
7. **Warrant discipline**: any number stated without a denominator or without a warrant label.

Write the full audit to ${OUT}/05-audit.md. Then FIX what you can fix safely: for any NOT-LANDED or
NEW-DIVERGENCE item that has an unambiguous correct value under D, edit the offending file directly
with the Edit tool to make it correct, and record in the audit exactly what you changed. Do not
rewrite whole sections; make surgical edits.

Return a compact summary: counts of LANDED / NOT-LANDED / NEW-DIVERGENCE, the list of edits you made,
the list of problems you could NOT safely fix, and a one-line verdict on whether the spec is
internally consistent enough to hand to the user.`,
  { label: 'audit', phase: 'Audit', effort: 'xhigh' },
)

return { parts: parts.filter(Boolean).length, audit }
