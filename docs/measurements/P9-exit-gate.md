# P9 · Exit gate — evaluated point by point, by someone who did not do the work

**Seven of nine criteria are met. Two are met in part, and both partial answers are published with
the reason, the repair and its blast radius.** A phase that reports nine of nine by narrowing what
the criteria asked is the failure this whole build is written against.

---

### 1. The ceiling is published with its per-sheet split and its command · **MET**

`docs/measurements/P9-template-diff-ceiling.md` publishes **957 of 3,747**, per sheet —
Portfolio 400 · Investors 368 · PMS 104 · Introduction 64 · Summary 20 · Compliance Status 1 —
reproducing `plan/05` §0.1 exactly. `make ceiling` re-derives it;
`test_golden__ceiling_is_957_of_3747` pins the count **and** the shared-dependent control
`'3. Portfolio'!O4 == "SUM(C4:N4)"`.

**It publishes a second number the plan did not have: 869 of 3,747.** The eight cells that are
unlocked *and* formula-bearing cannot be checked by the relation at all — overwriting one moves it
into the field surface, moves the fingerprint, and ends the run at `invalid.template_unbound` five
steps early. The plan calls a fixture over one of them *"a strictly stronger demonstration and the
one to show a reviewer"*; measured, it never reaches the relation.

### 2. The F11 pair is detected, and the zero-fire arm runs on a corpus we did not compute · **MET**

`formula-overwritten__pair-portfolio-O7-C182.xlsx` produces **2 `FAIL`s**, and it still binds — a
coordinated override that leaves every carry identity in the workbook satisfied.
`clean__independently-computed__fme-q1.xlsx`, whose derived cells LibreOffice computed, produces
**0 fires, 475 `PASS`, 30 `NOT_RUN`**. `test_nc__R08c` refuses a `TEMPLATE-COMPUTED` corpus id for
this criterion, so *"we will use what we have"* cannot quietly mean the corpus our own evaluator
wrote.

*The plan named this fixture `…-pair-portfolio-O7-summary`. `'2. Summary'` carries nothing at all
from `'3. Portfolio'` (MEASURED), so the fixture is named for the cell it actually pairs.*

### 3. `formula_source` published, F11 observable, `TEMPLATE_DIFF` admitted at G2 · **MET IN PART**

- **`formula_source` is published** — generated from `FORMULA_SOURCE_CONTRACT` into
  `EVALUATION-CONTRACT.md`, with an AST scan that fails on a computed argument, on an unlisted
  caller and on a table row with no caller. ✔
- **`test_f11_mutant_is_observable` is green.** ✔ This is the half that carries F19: without it
  `O` for F11 is 0 and any F11-claiming predicate dies at G2 with an arithmetic exception rather
  than a measured refusal.
- **`test_g2_admits_template_diff` is not green, and cannot be.** ✘

**Why, exactly.** `TEMPLATE_DIFF`'s oracle is the pinned blank's **formula graph**, recomputed by
`cdfc.calc` over the filed inputs. The admitted CEL subset cannot express that and was designed
not to: every construct it bans is banned because it defeats static key recovery, defeats
termination, or moves a check somewhere nobody qualified it. The envelope's `schema_keys` are
recovered from the expression's AST, so an expression the walker cannot parse has no declarable
read set.

**The route the design provides is a host function** — that is what `gstin_valid` and
`nav_interval` are. Taking it means adding a member to `ADMITTED_HOST_FNS`, a decided vocabulary,
in order to admit the relation whose author wants it admitted. **P9 does not widen a vocabulary to
fit its own flagship.** The work is named and costed: one host function, its registry entry, and
its row in the host-fn mutation harness.

### 4. Every relation holds on the clean filing and is violated by a targeted mutant · **MET IN PART**

The three convertible relations (R-02, R-03, R-07) reach the P4 envelope with **`schema_keys`
agreeing both ways**, with evaluation closures **disjoint from the corpus generator's**, and they
**do bind cells** — 10, 11 and 10 respectively, every one of them already bound by the harvest,
which is why every delta is zero. None reaches G2, and the measured reason is not the one this
document first asserted:

> **`qualify()` does not reject a relation. It raises**, at G0, before any gate arithmetic:
> *"`OBL-TEMPLATE-R-R-02` is not in the obligations table. A candidate whose obligation is missing
> does not take a skip at G0 — a gate stage that cannot fail is this product's own failure mode
> wearing a gate's clothes."*

That refusal is P7's own and it is right. What it exposes is structural: **the obligations table
is generated from the template's quotable constructs, and a relation's licence is a reviewed
argument — often an argument about what the template does *not* say.** R-02's evidence is *"no
formula in the workbook reads AA21, G42 or any country cell"*, and **an absence has no span to
point at.** G0 asks *is your obligation located, verbatim, at the recorded span?* — the right
question for a harvested predicate and the wrong shape for a relation.

Two routes exist, both arbitration-level, both costed in
`docs/measurements/P9-relation-attrition.md`: mint `OBL-TEMPLATE-R-*` rows quoting the construct
the relation is *about* (which moves `coverage_pair()`'s published TEMPLATE count off 571), or give
`ObligationSource` a third member (which re-opens arbitration C2). Choosing either inside a probe
build would be deciding what an obligation *is* in the tail of a phase about relations.

*The first version of this section asserted a different mechanism — `cells_bound == 0` at G1 —
from plausibility rather than from a run. The guard test caught it. It is recorded here because
a phase document that quietly replaces a wrong reason with a right one has learned nothing.*

### 5. No relation settles a cell without passing all five gates · **MET**

No relation is admitted, so none settles anything.
`test_unqualified_relation_cannot_settle_a_cell` is green, and every catalogue row carries a
non-empty `claims_fault_classes` declared before any campaign — the loader refuses a row without
one, because a denominator chosen after the result is not a denominator.

### 6. The all-zero filing is `OUT_OF_SCOPE` everywhere, and the fraction does not rise · **MET**

`template_diff({})` returns 505 findings, **every one `OUT_OF_SCOPE`, none `PASS`**, and every one
`scope_kind = PREDICATE_PRECONDITION` — so they stay in the denominator and flag their own
predicate for G3 re-qualification. `test_prop__fraction_does_not_rise_as_the_filing_empties` is
green, and `test_nc__R09b` is the control that makes it mean something: a cell **no** relation over
this template could reach does leave the denominator, so the rule is not indistinguishable from one
that retains everything.

### 7. `P9-delta.md` carries both columns and the ≈ 0-of-7 sentence · **MET**

Every relation appears, including the zero-delta ones and the ones not admitted. Column (b) is
`PENDING — requires P10-B2, opened 2026-08-14` — a **dated** open item, never a blank cell: an
empty cell reads as *nothing to report* and a dated one reads as *not yet measured*.
`test_rel__pending_marginal_is_dated_not_blank` asserts it.

### 8. A declared defect never raises the settled fraction · **MET**

`test_defect_table_cannot_raise_the_settled_fraction` is green, and the fallback is in
`probes/template_diff.py` rather than in the declarer's judgement: where `INFORMATIONAL` would
remove a bound cell nothing else reaches, the disposition is
`NO_PREDICATE(no_predicate.rule_ambiguous)`, which stays counted.

### 9. Every NC-R entry caught per-guard, with its positive control green · **MET**

`make nc-sweep`: **96 / 96 entries caught · 160 / 160 guards flipped**, exact-set semantics — every
`flips: true` guard red under its injector and every `flips: false` guard green. `make gates`:
**74 of 74 live gates observed red.** Both reproduce in a fresh clone.

---

## What P9 found that it was not looking for

Three defects, none of them in the relation layer, all three surfaced by building it:

1. **`evaluator_arm1.py` had not run since a rename.** `KeyError: 'cells'`, no make target, so
   `docs/measurements/P3-evaluator.md` was an artifact of a version that no longer executed —
   publishing FME as 495 agree / 10 not-run when the truth after P6's `AGGREGATE` repair was
   475 / 30. **A measurement with no way to re-run it is a memory.**
2. **The structural fingerprint does not exclude formula content**, only formula *text*. Eight
   cells' overwrite unbinds the filing, and they are exactly the eight a filer can overwrite
   without stripping protection.
3. **Every harvested tolerance literal is 1,000× the tolerance it expresses.** `HALF_ULP = 5` is
   half a unit of `MILLI_USD_MILLION`; the tree the runner evaluates is unscaled. `P-0114` admits
   a 60 USD Million discrepancy on a row whose true total is 12. The error is correlated with the
   quantity measured but **in the direction that does not flatter us** — an arithmetic mutant
   smaller than the over-wide tolerance is `WRONG`, observable and not killed, so it *depresses*
   `K/O`. The published kill rate is a lower bound. NC-R12 pins both halves so a partial repair
   cannot land quietly.

## What P9 would have killed if it had failed

The plan's failure branch: *"if the relations cannot be authored honestly the layer is deleted and
the settled fraction becomes a ceiling rather than a growth curve."* It did not come to that — but
the honest replacement claim the ceiling licenses is already published and stands on its own:

> **957 of 3,747 cells feed a formula the regulator wrote, and 869 of them are all we could ever
> check against it.**
