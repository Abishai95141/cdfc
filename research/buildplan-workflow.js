export const meta = {
  name: 'gift-build-plan',
  description: 'Produce the full phased development plan with functionality validation and negative controls for every build',
  phases: [
    { title: 'Foundations', detail: 'phase decomposition + dependency graph; and the validation methodology every phase must satisfy' },
    { title: 'Detail', detail: 'per-phase build specifications with acceptance tests and negative controls' },
    { title: 'Adversary', detail: 'where can a green build lie? plus assembly into one plan' },
  ],
}

const SPEC = '/Users/abishaikc/Gift/spec'
const OUT = '/Users/abishaikc/Gift/plan'

const CTX = `## CONTEXT — read before doing anything

You are planning the development of a system specified in full at /Users/abishaikc/Gift/spec/ .
Read with the Read tool, in this order:

1. ${SPEC}/00-executive.md   — what the thing is, the six load-bearing decisions, what the research killed
2. ${SPEC}/02-architecture.md — THE LAYERS, the verdict model, the predicate model, the report. Your primary source.
3. ${SPEC}/03-stack.md        — the technology decisions, the 15-step online flow, the 8 offline flows, the data model, the API and screens. Your other primary source.
4. ${SPEC}/04-path.md         — the EXISTING plan. It is dated against a hackathon (16 Aug application, 21-22 Aug build, Sep-Oct residency). **THAT CONSTRAINT IS GONE.** The user has no time limit and wants to start development properly. Mine it for content — the experiment queue, the do-not-build list, the demo script, the risk register, the twelve gaps, the seven open questions — but DISCARD its dates and its hackathon-shaped sequencing.
5. ${SPEC}/01-problem.md      — skim for the evidence base and the ban list only.
6. ${SPEC}/05-audit.md §V.7   — the post-audit resolutions. These are binding and recent.

Real artifacts already on disk that the plan must build against:
- Nine real IFSCA prescribed workbooks: /Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx
- Working measurement harnesses already written: /Users/abishaikc/Gift/research/scripts/ (wb_probe.py, predicate_harvest.py, l4_mutation_harness.py, true_coverage.py, verify_brief_43.py) and their outputs (predicates.json, l4_result.json)
- A python env at /Users/abishaikc/Gift/.venv/bin/python with openpyxl and lxml
- The repo root is /Users/abishaikc/Gift (git, no commits yet)

## THE GOVERNING PRINCIPLE OF THIS PLAN, AND IT IS NOT DECORATIVE

The product exists because **a silent pass is not information**. A deterministic program that returns a
clean, confident, well-formed wrong answer is the failure mode this system is built to refuse — and the
research corpus documents FIVE real instances, three of them committed by this project's own team, one of
them committed by the harness built to detect the others.

Therefore a build plan whose validation is "the test suite is green" would be self-refuting.

**Every acceptance test in this plan must ship with a NEGATIVE CONTROL: a specific, named, deliberately
broken build or input that the test MUST reject.** A test that has never been observed to fail is not
evidence. Where a negative control is impossible, say so explicitly and say what that costs.

This applies recursively: the test suite itself gets mutation-tested, and the phase gate reports the
mutation score of the tests over the code they claim to cover — with the equivalent-mutant caveat carried,
never a naive percentage.

## HOW TO WRITE A PHASE

Every phase in this plan has exactly these fields. No phase ships without all of them.

- **Phase ID and name**
- **What it settles** — the question this phase answers that no earlier phase could
- **Entry criteria** — what must be true before starting; which phases it depends on and why
- **Builds** — the phase decomposes into 1 to 4 numbered BUILDS. A build is a shippable increment that can be independently validated. Each build names: the exact files/modules created or changed, the public interface (function signatures, CLI, or endpoint), and the data it produces
- **Functionality validation, per build** — the concrete test set:
  - unit tests, named, with what each asserts
  - property tests where a property exists (state the property, and the generator)
  - golden/snapshot tests against the nine real workbooks, with which workbook and why that one
  - **negative controls** — the named broken build/input each test must reject
  - determinism check where output must be reproducible
  - performance budget where one exists, with the measured baseline it must not regress
- **The measurement this phase produces** — every phase must output at least one number that did not exist before, with its denominator and its warrant label
- **Exit gate** — a boolean. What must be true to proceed. Written so it can be evaluated by someone who did not do the work
- **What it kills if it fails** — the honest consequence, including "delete this layer and continue smaller" where that is the answer
- **Estimated effort** — in working days for one competent engineer, with the assumption stated. NOT dates

Write for the engineer who will build it. Name real paths, real module names, real test names, real
commands. No placeholder prose.
`

phase('Foundations')
log('Decomposing the build and designing the validation methodology')

const [decomp, method] = await parallel([
  () => agent(CTX + `
## YOUR TASK — THE PHASE DECOMPOSITION AND DEPENDENCY GRAPH

Write to ${OUT}/00-decomposition.md .

Produce the complete phase breakdown for building this system from the current state (schema induction,
predicate harvest, arithmetic evaluation and the settled-fraction denominator are BUILT and reproduce in
about 30 ms; template binding, pre-flight, closure, canaries, attestation and verify are SPECIFIED and NOT
BUILT) to a complete, validated, deployable system.

Requirements:
1. **Sequence by dependency and by what-decides-what, never by date.** Two orderings must be shown and
   reconciled: the DEPENDENCY order (what cannot be built before what) and the EVIDENCE order (what should
   be built first because it can kill the design cheapest). Where they conflict, say which wins and why.
   The spec's experiment queue ranks two field observations joint-first because they are the only things
   that can tell you the project is over — decide where they sit now that there is no deadline.
2. **10 to 16 phases**, each decomposing into 1 to 4 builds. Give each phase an ID (P0, P1, ...) and a
   one-line statement of what it settles.
3. **The dependency graph as ASCII**, showing which phases can run in parallel and where the hard barriers
   are.
4. **The critical path**, named, with its total estimated effort.
5. **Phase gating rules.** Which phases are GATED on an experiment result (notably: nothing of L3 should be
   built until the settling experiment runs; the FFR-bearing surfaces cannot ship before a blind-filled
   corpus exists). Show the gate, its pre-registered threshold, and the alternative branch if the gate
   fails — because the plan must be written so that a failed gate produces a smaller system, not a stalled
   one.
6. **What is explicitly NOT in the plan**, carried forward from the spec's do-not-build list plus anything
   the decomposition itself rules out, each with its reason.
7. For each phase, the **one number it produces** that did not exist before.

Do NOT write the per-phase detail — later agents do that. Produce the skeleton, the graph, the gates and
the ordering argument, in enough detail that another engineer can write the phase specs from it without
asking you a question.`, { label: 'plan:decomposition', phase: 'Foundations', effort: 'xhigh' }),

  () => agent(CTX + `
## YOUR TASK — THE VALIDATION METHODOLOGY EVERY PHASE MUST SATISFY

Write to ${OUT}/01-validation-methodology.md .

This is the document that makes "functionality validation of every single build" real rather than a
slogan. It is the standard every phase spec is written against.

Produce:
1. **The test taxonomy.** Every class of test this project uses, what each class can and cannot establish,
   and when each is required. At minimum: unit, property-based, golden/snapshot against real artifacts,
   differential (two implementations must agree), determinism/reproducibility, negative control,
   metamorphic/relational, performance regression, contract/schema, end-to-end. For each: the tool
   (name the actual library and say whether its licence was verified at source or only reported), the
   naming convention, where the files live, and how it runs in CI.
2. **THE NEGATIVE CONTROL CATALOGUE — the heart of this document.** For every kind of component this
   system contains, the specific way to break it and the test that must catch the break. Cover at minimum:
   a parser that silently under-reports (the openpyxl 35-of-54 case and the AML-CFT zero-of-five case are
   REAL and on disk — use them), a regex that cannot match a valid form of the thing it matches (the
   f-element case is real), a predicate that binds to zero cells and returns a vacuous pass, an evaluator
   that swallows an exception into a clean state, a denominator computed from the same wrong parser as its
   numerator (so the ratio is 1.0 and invisible), a scope truncation that drops hidden sheets from the
   denominator, a CEL expression exploiting the specification's own rule that a runtime error in an operand
   of the OR/AND operators is ignored, a canary that has gone silent, an attestation that can be made to
   express a pass, a report that does not re-derive. Each entry: the break, how to inject it mechanically,
   the test that must reject it, and where that test lives.
3. **Mutation testing OF OUR OWN TEST SUITE.** The tooling decision (mutmut vs cosmic-ray vs mutpy, with
   the reason and the licence warrant), the operator set, how the equivalent-mutant problem is handled and
   reported, the score format (always K/O with both integers plus U/G, never a naive percentage), and the
   per-phase threshold. State clearly the distinction the spec insists on: mutating CODE to evaluate the
   TEST SUITE is a different activity from seeding faults into DATA to evaluate the PREDICATE SET, and both
   exist in this system.
4. **The Definition of Done template**, as a checklist an engineer fills in per build, and which a reviewer
   can evaluate without having done the work.
5. **The CI pipeline.** Every gate, in order, what fails the build, expected wall-clock, and which gates
   are advisory vs blocking. Include the greps that enforce the design commitments the spec makes into
   system properties rather than preferences (no all-clear glyph reaching a user surface; the attestation
   schema having no result/status/pass field at any depth; no model client importable from the verdict
   path).
6. **The test-data strategy.** What fixtures exist, what must be created, how the blind-fill corpus is
   produced without contaminating it, how synthetic data is labelled so a measurement taken on it can never
   be quoted as a measurement of real filings, and the fixture naming scheme.
7. **What this methodology CANNOT establish** — stated plainly, because the project's own standard demands
   the residue be declared. Name the classes of defect that would survive this entire regime.`,
    { label: 'plan:validation-method', phase: 'Foundations', effort: 'xhigh' }),
])

log('Foundations complete. Writing per-phase specifications.')
phase('Detail')

const GROUPS = [
  {
    key: '02-phases-foundation',
    label: 'detail:foundation',
    body: `THE FOUNDATION PHASES — repo, ingest, schema induction, and the fact model.

Cover every phase in the decomposition that concerns: repository and CI setup; content addressing and the
receipt path; the container guard; dual-reader ingest and the structural agreement check; L1 schema
induction from raw OOXML (all sheets including hidden, extLst and x14 namespaces, shared formulas
materialised, merged ranges, defined names, protection state, the unlocked-cell mask that defines the
field surface); stable key generation; and the two-document fact model.

This group carries the project's highest-value negative controls because the real failures are on disk:
openpyxl 3.1.5 seeing 35 of 54 validations and reporting the AML-CFT sheet as having zero when it has
five; the f-element regex; the hidden-sheet scope truncation; the shared-denominator error. Build the
tests around the real artifacts, not around invented ones.`,
  },
  {
    key: '03-phases-verdict',
    label: 'detail:verdict',
    body: `THE VERDICT PHASES — predicate harvest, the predicate object, the CEL runtime, and the verdict model.

Cover every phase concerning: harvesting predicates from the blank template with no model; the predicate
data structure and its three-slot envelope; the CEL admitted subset, its runtime, and the pre-flight key
check that exists because the CEL specification says a runtime error in an operand of the OR/AND operators
is ignored; the five-rule evaluation contract and its generated single source of truth; the eight item
states and thirty namespaced reason codes; the run-level invalid vocabulary that is separate from them;
the cell roll-up precedence order and the closure invariant; and the settled-fraction object.

Note the post-audit resolutions in ${SPEC}/05-audit.md §V.7 are binding here: the precedence order is
ERROR then FAIL then INDETERMINATE then NOT_RUN then PASS then INFORMATIONAL then OUT_OF_SCOPE, a cell is
clean only if every predicate binding it passed, and the run-level invalid causes are their own closed
vocabulary. Validation must include a test that the settled fraction FALLS rather than silently succeeding
when a predicate goes not-run.`,
  },
  {
    key: '04-phases-qualification',
    label: 'detail:qualification',
    body: `THE QUALIFICATION PHASES — fault seeding, the five gates, the registry, and the clean corpus.

Cover every phase concerning: the fault-seeding harness and its fault taxonomy for a financial reporting
workbook; the observability filter and the control arm; the five qualification gates in their decided order
(G0 scope faithfulness, G1 executes and binds, G3 proof arm, G2 seeded-defect kill with marginal kill over
the free baselines, G3 empirical arm, G4 false-failure rate); the degenerate-baseline rejection; the
predicate registry and its admission record; corpus provenance and its six values; the Wilson interval and
the rule that a self-authored corpus yields an uninformative rather than a small FFR; and the blind-fill
corpus programme including the firewall that keeps it uncontaminated.

This group produces the numbers the whole product rests on. Its validation must include: a demonstration
that the gate rejects something real (five bound predicates asserting only a lower bound of negative 1e17
over 1,428 cells are on disk and are the worked example), a negative control in which a deliberately
degenerate predicate is fed to the gate and must be refused, and a test that no FFR renders without its
provenance and its n.`,
  },
  {
    key: '05-phases-probes-attestation',
    label: 'detail:probes+attest',
    body: `THE PROBE, SELF-CHECK AND ATTESTATION PHASES.

Cover every phase concerning: L6 differential and invariant probes, including the template-differential
that detects a formula cell overwritten with a literal, which is the check nothing else in the design can
perform; L6.5 run-time canaries that replay each admitted predicate's stored kill-witness against THIS
filing in the same execution, and the rule that a silent canary makes the run invalid; the residue set and
its human adjudication step; L7 attestation as a DSSE/in-toto Statement whose top-level object is scope and
which has no result, status or pass field at any depth; and the verify command that proves byte-identical
re-derivation.

The self-check layer is the design's boldest claim — that the verdict is conditioned on a proof obtained
from the artifact under test, in the same execution, and withheld when that proof fails. Its validation is
therefore the most important in the plan: specify exactly how you prove the canary layer actually catches a
dead predicate, including the negative control where a predicate is deliberately made unable to fire and
the run must return invalid rather than a settled fraction.`,
  },
  {
    key: '06-phases-model-and-clause',
    label: 'detail:model+clause',
    body: `THE MODEL-BEARING AND CLAUSE-GRAPH PHASES — and the experiment that decides whether they exist.

Cover: the settling experiment that decides whether a model can write a regulator-grade executable check
(the spec pre-registers n, the retain threshold, the delete threshold and one pre-committed extension —
carry them exactly and show the binomial power figures with the n they belong to); the L3 candidate-proposal
layer, which must not be built until that experiment runs; the L1b clause graph and the hand-maintained
obligations table that stands in for it until it exists; the L2 extraction split and its abstention design;
and the instrument watcher that quarantines a predicate when its clause moves.

Two things this group must get right. First, the plan must be written so that a failed settling experiment
produces a SMALLER system that still ships, not a stalled one — state exactly what the system looks like at
k=0 and what still gets published. Second, every model-bearing build needs a validation strategy that does
not itself depend on a model judge, since the spec establishes that a model may never be the final
adjudicator (false-success detection at AUROC at most 0.65, 13% recall at a 10% flag rate).`,
  },
  {
    key: '07-phases-surface-and-transfer',
    label: 'detail:surface+transfer',
    body: `THE SURFACE, TRANSFER AND OPERATIONS PHASES.

Cover: the API surface; the report renderer and the screens (Drop, Report with its two equal-weight counts,
the Unchecked panel, the Predicate library with its five-gate attrition funnel, and settled-fraction over
time); the CI enforcement of the no-all-clear commitment at the level of pixels and copy; the transfer
measurement across the other eight prescribed workbooks, which needs no model and no corpus and is the
cheapest test of whether the method generalises; template version churn and predicate re-qualification;
deployment and reproducibility of a published report; and the operational concerns including the register
snapshot policy, its staleness bound, and the requirement to read IFSCA's terms of use before any scheduled
polling.

Validation here is mostly about surfaces that can lie. Specify the tests that prove: a report opens from a
file URL with networking off and renders every number; no all-clear glyph or phrase can reach a user
surface; a settled count cannot render without the admission state of the predicate set that produced it;
and the settled fraction can fall when a template version bumps.`,
  },
]

const details = await pipeline(GROUPS, (g) =>
  agent(CTX + `

ALSO READ, and treat as binding, the two foundation documents just produced:
- ${OUT}/00-decomposition.md — the phase breakdown, IDs, dependency graph and gates. Use ITS phase IDs and
  ITS ordering. Do not invent a different decomposition.
- ${OUT}/01-validation-methodology.md — the test taxonomy, the negative control catalogue, the Definition
  of Done template and the CI pipeline. Every phase you write must satisfy it, and must reference its
  catalogue entries by name rather than restating them.

## YOUR TASK

Write to ${OUT}/${g.key}.md the FULL per-phase specification for this group of phases, using the phase
template given above (what it settles · entry criteria · builds with exact files and interfaces ·
functionality validation per build with negative controls · the measurement it produces · exit gate · what
it kills if it fails · effort in engineer-days).

${g.body}

Be concrete to the level of file paths, module names, function signatures, test function names, CLI
commands and fixture names. An engineer should be able to open your document and start typing. Where the
spec leaves something genuinely open, say so and give the decision rule rather than inventing an answer.`,
    { label: g.label, phase: 'Detail', effort: 'xhigh' },
  ),
)

log("${details.filter(Boolean).length} of ${GROUPS.length} phase groups written. Running the adversary.")
phase('Adversary')

const [adversary, assembly] = await parallel([
  () => agent(`You are the ADVERSARY on a build plan. Your question is exactly one thing:

**WHERE CAN A GREEN BUILD LIE?**

Read:
- ${OUT}/00-decomposition.md
- ${OUT}/01-validation-methodology.md
- ${OUT}/02-phases-foundation.md, ${OUT}/03-phases-verdict.md, ${OUT}/04-phases-qualification.md,
  ${OUT}/05-phases-probes-attestation.md, ${OUT}/06-phases-model-and-clause.md,
  ${OUT}/07-phases-surface-and-transfer.md
- ${SPEC}/02-architecture.md for the layer contracts

This project exists because a deterministic program can return a clean, confident, well-formed wrong
answer. Its own corpus documents five real instances, three committed by the team, one by the harness built
to detect the others. So find, in THIS PLAN, every place where:

1. A test could pass while the thing it claims to test is broken. Name the specific mechanism.
2. A phase gate could be satisfied by a system that does not work. Name the specific hole.
3. A negative control is missing, is not actually negative (it would also pass on a correct build), or is
   untestable as written.
4. A measurement the plan produces could be an artifact of the measuring apparatus rather than a property
   of the system — the failure that has already happened five times in this corpus.
5. Two phases assume different contracts for the same interface, so both pass in isolation and the
   integration is broken.
6. A phase's exit gate is subjective, unfalsifiable, or evaluable only by the person who did the work.
7. The plan's own ordering hides a dependency — something built in phase N that cannot actually be
   validated until phase N+k, meaning phase N ships unvalidated and nobody notices.
8. Effort estimates that are obviously wrong in a way that will distort sequencing decisions.

For each finding: the phase and build it affects, the exact failure scenario, its severity (FATAL if a
broken system could ship and be believed / SERIOUS if it wastes significant work / MINOR), and the specific
repair — a named test, a named negative control, or a changed gate.

Then write, as the closing section, **THE TEN TESTS THIS PLAN MOST NEEDS AND DOES NOT HAVE**, ranked.

Write everything to ${OUT}/08-adversary.md and return a compact summary with the counts by severity and
the ten tests.`, { label: 'adv:green-build-lies', phase: 'Adversary', effort: 'xhigh' }),

  () => agent(`You are writing the front matter and the operating manual for a phased build plan.

Read:
- ${OUT}/00-decomposition.md and ${OUT}/01-validation-methodology.md
- all six phase-detail files in ${OUT}/ (list with Bash ls)
- ${SPEC}/00-executive.md for what the system is

Write to ${OUT}/09-operating-manual.md :

1. **How to use this plan.** The daily and per-build loop: what an engineer does from picking up a build to
   closing it, including where the Definition of Done lives and who evaluates the exit gate.
2. **The state of the world right now** — what is built, what is specified, what is measured, stated
   honestly per the spec's own ruling, with the file paths of the existing harnesses and what each already
   produces.
3. **The first week, concretely** — the first three builds in dependency order, with the exact commands to
   run, so there is no ambiguity about where development starts. No dates; just order.
4. **The measurement ledger** — a single table listing every number the plan will produce, in phase order,
   with its denominator, its warrant label once produced, and which phase produces it. This is the
   project's own coverage declaration applied to itself.
5. **The decision log template**, and the initial entries for the decisions already taken (they are in the
   spec's six load-bearing decisions and the post-audit resolutions in ${SPEC}/05-audit.md §V.7).
6. **The open questions that block phases**, carried forward from the spec, each mapped to the phase it
   blocks and the decision rule if no answer arrives.
7. **Repository layout** — the full directory tree as it should exist when the plan is complete, with a
   one-line purpose for each top-level entry.

Return a compact summary.`, { label: 'plan:manual', phase: 'Adversary', effort: 'xhigh' }),
])

return {
  decomposition: !!decomp,
  methodology: !!method,
  detailGroups: details.filter(Boolean).length,
  adversary,
  assembly,
}
