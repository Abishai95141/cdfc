# BUILD PLAN — the coverage-declaring filing checker

**The front door. Compiled 11 August 2026.** The specification is [SPEC.md](SPEC.md); this is how it gets
built. Sixteen phases, ~60 builds, every build with its own functionality validation and a **negative
control** — a named, deliberately broken build or input that the test must reject.

**Why the negative controls are not ceremony.** This product exists because a deterministic program can
return a clean, confident, well-formed wrong answer. The corpus documents five real instances, three
committed by this project's own team and one by the harness built to detect the others. A build plan
validated by "the tests are green" would be self-refuting. **A test that has never been observed to fail is
not evidence.**

---

## THE DOCUMENTS

| # | Document | What it is |
|---|---|---|
| 00 | [Decomposition](plan/00-decomposition.md) | The sixteen phases, both orderings and their reconciliation, the dependency graph, the gates, the critical path |
| 01 | [Validation methodology](plan/01-validation-methodology.md) | The test taxonomy, **the canonical negative-control registry**, mutation testing of our own tests, the Definition of Done, the CI pipeline |
| 02 | [P0–P3 · Foundation](plan/02-phases-foundation.md) | Repo and commitment gates · ingest · schema induction · the evaluation substrates |
| 03 | [P4–P5 · Verdict](plan/03-phases-verdict.md) | The predicate object, the CEL substrate, the harvest, the verdict model |
| 04 | [P6–P8 · Qualification](plan/04-phases-qualification.md) | Fault seeding · the five gates · the registry · the clean corpus and the false-failure rate |
| 05 | [P9–P11 · Probes & attestation](plan/05-phases-probes-attestation.md) | Differential probes · run-time canaries and the residue · attestation and `verify` |
| 06 | [P12–P13 · Model & clause](plan/06-phases-model-and-clause.md) | The settling experiment, and the model-bearing layers sized by its result |
| 07 | [P14–P15 · Surface & transfer](plan/07-phases-surface-and-transfer.md) | The report, the screens, the API, transfer across the nine workbooks, operations |
| 08 | [Adversary](plan/08-adversary.md) | *Where can a green build lie?* 44 findings — 9 FATAL, 30 SERIOUS, 5 MINOR |
| 09 | [Operating manual](plan/09-operating-manual.md) | The per-build loop, the state of the world, the first week, the measurement ledger, the decision log |
| 10 | [Repair verification](plan/10-repair-verification.md) | Independent check of the repair pass |
| 11 | [Arbitration ruling](plan/11-arbitration.md) | The nine seams the repair opened, decided |
| 12 | [Arbitration confirmed](plan/12-arbitration-confirmed.md) | Independent confirmation, 8 PASS / 1 FAIL |

**Instruments:** [`plan/scripts/nc_audit.py`](plan/scripts/nc_audit.py) (independent catalogue audit, carries
its own positive control) and `plan/scripts/catalogue_check.py` (the registry's own check). Two instruments
by design — a check written by the pass that did the repair is a self-check.

---

## THE SIXTEEN PHASES

| Phase | What it settles |
|---|---|
| **P0** | Whether this project's own honesty commitments can be mechanised before there is code to break them |
| **P1** | Whether we can read the artifact at all without the class of silent under-reporting already measured |
| **P2** | **The denominator every subsequent number is a fraction of**, computed rather than asserted |
| **P3** | Whether our recalculation reproduces the regulator's own cached values — the positive control under every kill rate |
| **P4** | Whether the settled fraction is derivable rather than estimated |
| **P5** | The product's core object: eight states, thirty reason codes, closure |
| **P6** | Whether a kill rate over our operator mix means anything |
| **P7** | Whether the rejector is real — the first five-gate attrition funnel |
| **P8** | Whether **any** predicate in this system is admissible at all |
| **P9** | Whether the growth story is real, and the one check nothing else in the design can perform |
| **P10** | Whether a verdict can be conditioned on a proof obtained from the artifact under test |
| **P11** | Whether a third party on another machine re-derives the report byte-for-byte |
| **P12** | How large the model's role is — `k of 20` obligations surviving a test specified before the model ran |
| **P13** | What the model-bearing layers look like at the size P12 licenses |
| **P14** | Whether the no-green-tick commitment survives contact with a rendering surface |
| **P15** | Whether this is a product or a paper about one workbook |

**Critical path — the qualification spine.** `P0→P1→P2→P3→P4→P5→P6→P7→P8→P12→P13` =
`8·8·10·17·14·12·10.5·16·9.5·6·16` = **127 working days**, one competent engineer at ~6 productive hours a
day, off-path phases parallelised. **127 is a floor, not a midpoint** — P0 is estimated 8–10 and P3 15–20,
and the row takes the low end of each.

> **The longest pole is not the code. It is the corpus.** The blind-filled clean corpus needs 15–25
> **person**-days of someone who has never seen the predicate set, has **zero code dependencies**, and
> starts on day one in its own lane. Defer it past roughly day 70 and it becomes the critical path.

---

## THE GATES

Every gate is a pre-registered boolean with a named threshold and a named failure branch. **No gate in
this plan produces a stall; every failure branch produces a smaller system that still ships.**

| Gate | Threshold | If it fails |
|---|---|---|
| **G-READERS** | Two independent readers agree on sheet structure, 9 of 9 workbooks | The disagreeing workbook is excluded with a stated reason; corpus shrinks, plan continues |
| **G-DENOM** | The field surface computed twice by independent code paths, agreeing | That workbook has **no settled fraction, ever** — published as such |
| **G-EVAL** | Our evaluator reproduces 505 of 505 cached values | Above 25 failures, the kill rate is downgraded to a *reach* measurement and labelled so; the template differential is deleted |
| **G-CELPY** | The CEL conformance suite passes on the admitted subset, **specifically on `&&`/`\|\|` error semantics** | Narrow the grammar to ban them at the top level — smaller language, same guarantee |
| **G-CORPUS** | `n ≥ 30` with provenance that is not self-authored, fill brief hashed **before** the first workbook was filled | **No predicate is admitted, every rate renders `uninformative`, the settled fraction is `null`.** Ships in that state |
| **G-LIVENESS** | A deliberately dead predicate produces `INVALID` and no settled fraction of any kind | The self-check layer is deleted and the surfaces say liveness is not demonstrated |
| **G-REPRO** | A third party on another machine gets a byte-identical re-derivation | Name the non-determinism; drop to a field-level claim, labelled weaker |
| **G-SETTLE** | **≥ 6 of 20** obligations survive all five gates and beat the free baselines. **≤ 2 ⇒ delete.** 3–5 ⇒ one extension to n = 40 at ≥ 12, never again | **L3 is deleted and only L3.** Predicates become hand-authored. `k = 0` is published on the date it is taken |

Two rules are enforced at build level rather than by discipline: **nothing of the model layer is written
until the settling experiment's decision record exists** (CI fails on the file's presence without it), and
**no rate-bearing surface ships before a blind-filled corpus exists.**

---

## WHAT IS ALREADY TRUE

Verified by re-running the harnesses this session; all three reproduce **byte-identically** across runs.

| Harness | Output | Time |
|---|---|---|
| `predicate_harvest.py` | 515 predicates across nine workbooks; 280 for the FME return | 0.37 s |
| `true_coverage.py` | 3,747-cell field surface · 2,373 touched · 1,374 residue | 0.12 s |
| `l4_mutation_harness.py` | 19,782 mutants · 3,574 killed · 22 equivalent · 2,826 sites | 1.64 s |

**Two reach numbers are live, and neither is a quality measure.** 2,373 of 3,747 cells (63.3%) are *read*
by a predicate; 511 of 2,826 numeric fault sites (18.1%) sit inside the arithmetic predicate graph. Six of
the seven fault operators kill exactly 511 — a site dies iff it is in the graph, whatever perturbation is
applied — so the second number measures reach at a different granularity, not discrimination. **No hero
number is claimed until a false-failure rate exists**, which under this plan's own admission rule means the
currently defensible settled fraction is **0%**.

**Honest status:** schema induction, predicate harvest, arithmetic evaluation and the settled-fraction
denominator are built. Template binding, pre-flight, closure, canaries, attestation and `verify` are
specified and not built. Zero commits exist in the repository. Zero of the sixteen phase numbers exist yet.

---

## HOW THIS PLAN WAS STRESSED, AND WHAT THAT FOUND

The plan was written, then attacked, then repaired, then arbitrated, then confirmed — and **every stage
found the plan committing the failure mode the product exists to refuse.**

- **The adversary pass** found 9 FATAL findings. The worst three: a qualification gate whose denominator
  the predicate chooses *after* the campaign runs (a predicate with true `K/O = 0.21` admitted at `0.97`,
  signed, nothing red); a clean corpus generated by the same function 277 of the 515 predicates re-check,
  letting a `BLOCKING` severity tier be bought in an afternoon from a corpus the product generated about
  itself; and a gate stage that was either impossible or decorative.
- **The repair pass** closed six of nine — and, run as four parallel owners over a coupled document set,
  introduced eight new contradictions and created two brand-new ID collisions *inside the repair for ID
  collisions*. **A coupled specification admits exactly one writer at a time.** That was a process error,
  and it is recorded rather than smoothed over.
- **A raw NUL byte** in one document made `grep` skip the entire file — so the CI gate designed to catch ID
  collisions would have run green over the largest instance of the problem.
- **The arbitration** ([11](plan/11-arbitration.md)) decided the nine seams serially. One ruling —
  the critical path — **was wrong when issued and is corrected in place with the original kept visible**,
  because a detail document that re-derives an estimate from the build list it owns beats a summary figure
  pre-registered before that list existed.
- **The independent catalogue instrument was wrong four separate ways** before it agreed with the
  registry's own checker: it counted report documents as definitions, credited every ID on a line,
  counted a document's own summary index as a second definition, and was blind to two-letter ID families.
  It took four corrections to write a correct checker for a naming convention this simple — which is the
  argument for the plan's rule that the registry be machine-checkable **by construction** rather than by
  heuristic.

**Current state: 0 duplicate catalogue definitions across documents, confirmed by two independent
instruments. One band table. 33 retired IDs, none redefined. No NUL bytes, verified by binary read with a
positive control.** Residual: 17 orphan and 56 dangling references remain under my instrument's stricter
rule, most of which are retired IDs appearing legitimately in retirement records; the registry's own
checker exempts those and reports zero. **That disagreement is unresolved and is named rather than
averaged away.**

---

## WHERE DEVELOPMENT STARTS

Three builds, in dependency order, from [09 §3](plan/09-operating-manual.md):

1. **P0-B1** — repository skeleton, `LICENSE` (Apache-2.0, for the patent grant), hash-pinned lockfile, CI
   harness.
2. **P0-B2** — content-addressed ingest of the nine workbooks; run it twice and assert byte-identical
   manifests.
3. **P0-B3** — the commitment gates. **This cannot go first**: a grep over a missing scan root passes
   trivially, which is the plan's own thesis applied to its first commit.

In parallel from day one, in their own lanes: the **blind-fill corpus** (the real longest pole) and the
**field observation** to IFSCA's Division of Investment Funds.

---

## WHAT IS STILL OPEN

| Item | Blocks | Decision rule if unanswered |
|---|---|---|
| **Who is Person A?** The blind-fill corpus needs someone who has never seen the predicate set | P8 · G-CORPUS · **every rate the product displays** | The audited second-model-instance route, with the fill brief hashed and published before the first workbook is filled |
| **gVisor licence and the SECONDARY runtime licences** (Z3, Hypothesis reported but not read at source) | P1, then a hard block from P2 | Open the LICENSE files before the dependency is pinned; a licence nobody opened is not a licence |
| **F27** — the one SERIOUS adversary finding not closed | — | Named, with its owner |
| **`K` and `T` in the pervasiveness policy** | — | Render the literal string `PLACEHOLDER`. They have no argued basis anywhere in the corpus and **must not be quietly filled in** |
| **The serial and `k = 0` totals** | Any schedule claim | Stale by at least +9 after the P0/P3 re-estimate. **Recompute before quoting**; they are not corrected here because I did not verify every phase's revised figure, and publishing a number I have not computed would reproduce the defect the correction exists to fix |
