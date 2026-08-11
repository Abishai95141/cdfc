# THE COVERAGE-DECLARING FILING CHECKER
## Authoritative build specification · compiled 10 August 2026

**This document supersedes `RND-BRIEF.md`, `ARCHITECTURE.md` and the three intermediate drafts
(`research/synthesis/A`, `B`, `C`) wherever they conflict with it.** It was produced by fifteen research
lanes with adversarial verification on the load-bearing ones, reconciled against a ruling that resolved
31 contradictions between the drafts, and audited for whether that ruling landed. Where a lane opened a
primary source and the adversarial pass did not refute it, the lane wins.

**Read a number in this document with the label attached to it.** MEASURED (computed first-hand against
an artifact on disk, script named) · VERIFIED-AT-SOURCE (the primary document was opened and the clause
read off the page) · SECONDARY (a credible source describes it; the primary was not opened) · DERIVED
(arithmetic on stated inputs; carries the warrant of its weakest input) · MODELED (an assumption) ·
UNMEASURED / NOT-FOUND (we looked and could not settle it — a legitimate and required answer).

---

## THE ONE-PAGE VERSION

**The problem.** Every quarter each of the 217 fund managers licensed at GIFT City returns a spreadsheet
the regulator publishes. The only thing in it resembling a verdict is a Yes/No cell in which the manager
attests that its own valuations comply; nothing in the other 6,756 cells can contradict it. That is a
green tick with no denominator, and it is the general case — an audit opinion, a filing sign-off and a
sanctions disposition all end in *nothing wrong here*, and none of them says what was looked at.

The scarce quantity is not error detection. Detection is solved and cheap. The scarce quantity is **an
attributable, per-check, measured statement of how often that check is wrong, carried next to the finding
it produced, together with a computed declaration of what was not touched.** No product or published
system opened in this research prints either object for a regulated financial filing.

**What we are building.** A checker for a prescribed regulatory workbook that reports what it did not
check. It induces the field graph from the regulator's *blank* template — 505 formula-bearing cells, 54
data validations, a 3,747-cell filer-editable surface — harvests 280 executable predicates from what the
template already encodes, **with no model**, and admits a predicate to the active set only after
measuring its kill rate against seeded defects, proving it is not the flag-everything baseline, and
measuring its false-failure rate on a corpus its authors did not write. Every filing returns a signed
report carrying two counts of equal weight, a typed reason for every unsettled property, each firing
check's own error rate, and a replay proving the checks were alive on that document. **There is no field
in the schema where a downstream consumer could write "pass."**

**Why the parts need each other.** Each component alone is defeated by a measured fact, and each one's
failure mode is another's input. SPADE's own paper says its false-failure rate cannot be computed because
the example universe is unknown — seeded defects manufacture that universe with certain ground truth.
Seeded defects say nothing about properties with no oracle — differential relations over the
workbook-as-program settle some without one. Relations can be trivially true — the degeneracy gate
rejects them, and has already rejected five real predicates that assert only "this is a number" over
1,428 cells. The built path runs in **~30 ms** (MEASURED) and the verdict path is **specified to make zero
model calls, with the CI assertion listed as a build gate and not yet written** — so `pass^k` decay does
not apply to it by construction, but say "specified", not "does", until `test_no_model_in_verdict_path`
exists.

**What could kill it, in order.**
1. **The application portal returned HTTP 404** and nobody has seen the live form. Applications close
   **16 August**. Ten minutes in a browser settles it. This is the only item that can end the programme.
2. **IFSCA may already run these checks on receipt**, which makes the filer-side product a convenience
   rather than a gap. One email settles it and it is unsent.
3. **The headline 63.3% is computed from 280 predicates of which none is admissible under our own gate**,
   because no false-failure rate has been measured for any of them. A judge who connects those two facts
   wins — unless we say it first, which §IV.4.1 step 2 does, and which turns the objection into the
   strongest moment in the demo.
4. **The method may not transfer past one workbook.** Nine are already on disk to find out, and the
   measurement needs no model and no corpus.

**What to do first.** Open the portal and screenshot every field. Send the IFSCA email. Run the transfer
measurement. The settling experiment on whether a model can write a regulator-grade check costs about
thirteen dollars and belongs *after* all three, because it can only tell us how large the model's role is —
not whether anyone wants the thing.

---

## THE SIX DECISIONS THAT DETERMINE EVERYTHING DOWNSTREAM

| # | Decision | Beat | Because |
|---|---|---|---|
| 1 | **The unit of the denominator, of closure and of the settled fraction is the CELL** — the filer-editable, unlocked, non-formula cell | the `(field × obligation)` pair | Every quantity actually measured is a cell count. The pair model's `obligationsTotal` and `pairsTotal` had no derivation anywhere in the corpus and appeared with three mutually incompatible values |
| 2 | **The predicate language is CEL, admitted subset only, inside a three-slot envelope** (`applicable` / `expr` / `witness`) | generated Python; Rego; VTL; Great Expectations | Non-Turing-complete and terminating, so a confused model cannot write a predicate that hangs or reaches the filesystem; readable by an auditor; mechanically mutable; and the sandbox problem disappears rather than being contained |
| 3 | **L3 — the model — runs at build time, per template version, never per filing** | a model in the request path | Per-filing model cost is $0.00 and the report re-derives byte-identically. The verdict path is *specified* to make zero model calls so that `pass^k` decay cannot apply to it; that becomes a property of the system on the day the CI gate is written, and not before |
| 4 | **A predicate with no qualification record does not load** | admitting hand-authored checks and measuring later | The settled-fraction claim is then true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement. It is also why the currently defensible settled fraction is 0% and we say so on stage |
| 5 | **The verdict has eight closed item states and thirty namespaced reason codes; `cells_bound == 0` is an `ERROR` that makes the run `INVALID`, never a `PASS`** | the brief's single `UNCHECKED` token | A predicate that bound to nothing is the vacuous-pass failure the whole design exists to catch. Collapsing it into "unchecked" puts it in the same bucket as a rate-limited register |
| 6 | **The attestation's top-level object is `scope`, and the schema has no `result`, `status` or `pass` field at any depth** | signing a verdict | A surface that can render all-clear will eventually render it wrongly. Prohibiting it in the schema, and grepping for it in CI, is the only version of that commitment that is a system property rather than a preference |

---

## WHAT IS GENUINELY NEW, STATED AT SURVIVABLE STRENGTH

> **No product or published system, for any regulated financial filing, (a) admits a check into its
> active set only after measuring that check's own false-failure rate on a declared clean corpus and its
> kill rate against seeded defects, and (b) returns, alongside the verdict and signed with it, a computed
> per-field machine-readable declaration of which correctness propositions were not settled and why.**

For a slide: *everyone ships rules; nobody ships each rule's error rate, and nobody ships the residue.
We make both a product surface, and sign them.*

Three further claims are novel in their own right and were nearly lost to over-hedging. They are restored
in §I.5.1 and each is falsifiable:

- **The residue is a theorem, not a coverage gap.** A prescribed return is a closed arithmetic system. We
  can construct and exhibit a family of filings that are internally perfect under every relation the
  regulator's own template encodes and every relation we add — and materially false. In code mutation
  testing a mutant that changes behaviour is in principle killable by some test; here a mutant can change
  the *truth* of the artifact and be **provably unkillable by any predicate over the artifact alone**.
  That family is non-empty by construction and its size is measurable.
- **`INVALID` is a liveness proof, not a self-test.** No assurance artifact in existence carries evidence
  that the instrument that produced it was working on the specific document it examined. A clean audit
  opinion does not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict
  unless every check has just demonstrated, on your file, that it can still catch the fault it was
  admitted for.
- **The criterion source is citable, versionable and watchable — not more authoritative.** SPADE infers
  what correctness meant from the traces of a developer changing their mind. We do not have to infer it.
  The criterion is a published instrument with a version, an amendment chain machine-followable in 76 of
  82 cases, and a blank template with a content hash. It is *not* more authoritative — the regulator's own
  template computes a scheme total that misses two of its own nine legal values — but it can be cited,
  re-qualified when the clause moves, and quarantined the day a circular changes the rule.

**The honest limit, which stays permanently on the report surface:** *this system detects error, not
deception. Every check here is a consistency check over a self-reported document. A coherent liar passes
all of them.*

---

## WHAT THE RESEARCH KILLED

Recorded here because re-exploring any of it is wasted work, and because two of these were the brief's
own headline claims.

| Killed | By what observation |
|---|---|
| *"No measured system can say 'this one is clean'"* | Refuted from inside the brief's most-cited source. On FinVerBench's 43 clean statements Claude Sonnet 4 scored FPR **0.0%**, precision 100, recall 100, under the same guided-checklist prompt where seven of fourteen other complete runs flagged 43 of 43. The surviving statement is narrower and better: **a machine can be calibrated, and nothing in its output says whether it was** |
| *"Zero financial regulations encoded anywhere"* | EBA publishes 12,925 rule-instances (8,052 distinct), EIOPA 6,767, ESMA 68, XBRL US DQC ~196, FINOS CDM 640 named conditions. What is empty is the *civic* rules-as-code shelf — Catala and OpenFisca are entirely tax, benefit and pension, positive controls passed |
| *"No analogue exists for a financial assertion"* | ISA 705 ¶24 and ISRS 4400 ¶30(j) are financial and mandatory; ESMA publishes a per-rule `Automatable: Yes/No`, 8 of 68 declared No, six of them `MUST`; XCCDF Table 26 has nine per-item result states |
| *"CycloneDX `compositions.aggregate` — a ten-state enum since 1.2"* | The field first appears in **1.3 with six states**; the ten-state form arrives in 1.5. It is *aggregate*, not per-item |
| **The NAV-error wedge** | The string `NAV` does not occur in any XML part of any of the nine prescribed workbooks (MEASURED, positive controls: `Scheme` 123, `USD Million` 31, `Portfolio` 25, `valuation` 6). No NAV per unit, no units outstanding, no dealing price. Every NAV-error rule on earth operates on exactly those quantities. The *domain fact* — that CSSF publishes thresholds and IFSCA publishes none — stays as framing. The *product* does not |
| **The supervisor as a user** | That seat is procured: NEC Corporation India, 27 January 2026, ₹39,57,36,115.52, RE-facing portal explicitly in scope. The supervisor is not the buyer; the supervisor is why the filer cares |
| **The five original metamorphic relations** | Row reorder, zero-holding insertion, duplicate consolidation, unit scaling and currency round-trip all require NAV-shaped quantities the workbook does not contain. Replaced by differential probes over the workbook-as-program, including one nothing else in the design can do: detecting a formula cell overwritten with a literal |

Nine further withdrawn numbers, each with the evidence that moved it, are in §I.6 — **the ban list, which
is the section to read before a pitch.**

---

## HOW THIS DOCUMENT IS ORGANISED

| Part | What it settles |
|---|---|
| **I — The problem, the evidence, and the claim** | What the problem is and who has it; every load-bearing quantity with its warrant and denominator; what we are building and what it is not; the domain grounding; what is genuinely novel and the three strongest objections with their rebuttals; the ban list |
| **II — The architecture** | The layers with exact input and output types, which contain a model, their failure modes and their self-checks; the corrected data flow; the verdict model (eight states, thirty reason codes, the seven-term closure invariant, the five-rule evaluation contract); the predicate model and the five qualification gates; the report and its signing envelope |
| **III — The technology stack and the backend flow** | Every technology decision with the runner-up it beat and the condition to switch; the adopted open-source ledger with licences at their real warrant; the fifteen-step online flow and the eight offline flows; the data model and re-derivation proof; performance and cost; the API and the screens |
| **IV — The path, the deliverable, and what is open** | The experiment queue with pre-registered thresholds; the dated plan to 16 August, 21–22 August and the residency; the do-not-build list; the demo script line by line with every on-screen number's provenance; the acceptance criteria as CI tests; the risk register; twelve engineering gaps each decided or explicitly open; **seven questions only you can answer** |
| **V — Audit** | The independent check that the reconciliation ruling landed, with every edit made |

Supporting research is in `research/lanes/` (fifteen lanes, ~200,000 words, several carrying an appended
adversarial-verification pass), `research/synthesis/` (the superseded drafts and the reconciliation
ruling), and `research/scripts/` (the harnesses that produced every MEASURED number here).

---
