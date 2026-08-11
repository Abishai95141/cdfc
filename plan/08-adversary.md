# 08 — THE ADVERSARY PASS
## Where a green build can lie · compiled against `plan/00`–`07` and `spec/02-architecture.md`

**One question only: WHERE CAN A GREEN BUILD LIE?**

This document is written against a plan that is unusually well defended. It already carries a
negative-control catalogue, a mutation regime, a residue declaration per phase, and — three separate times
— a *correction of a binding document found by reading rather than by testing* (`02` §0.2 N1, `05` §0.5,
`07` §6). Those are the marks of a plan that expects to be attacked. The findings below are therefore not
"you forgot the tests". They are the places where **the plan's own machinery would run green over a system
that does not work**, and most of them are reachable *because* of a decision the plan made deliberately.

**Nine findings are FATAL** — a broken system could ship and be believed. **Thirty are SERIOUS** — they
waste significant work or invalidate a published number. **Five are MINOR.**

**The three that matter most, stated at the top so they are not buried:**

> **1.** The qualification gate G2 lets a predicate choose its own denominator. `K/O ≥ 0.80` is computed
> *"on the fault classes the predicate claims to cover"*, and **no field of the predicate envelope declares
> a fault-class claim.** The claim exists only inside the `FaultWitness` that G2 itself selects, after the
> campaign has run. A predicate that kills one class of one operator and nothing else scores `1.00` and is
> admitted `BLOCKING`. This is NC-D02's mechanism — the numerator choosing its denominator — arriving at
> the gate that exists to catch it.
>
> **2.** The `TEMPLATE-COMPUTED` clean corpus is produced by the evaluator that the arithmetic predicates
> re-check. `P8-B2::synthesise` fills the input cells and *"lets the workbook's own 505 formula cells
> compute the rest via `src/cdfc/calc/`"*; `P9-B1::template_diff` then *"recomputes `c`'s template formula
> over the filed inputs using P3's evaluator"* and compares. The two are the same function. P5's exit
> criterion 1 (*clean filing ⇒ 0 FAIL*), P9's exit criterion 2 (*fires on zero template-computed clean
> filings*) and every arithmetic FFR at G4 are therefore **true by construction, at expected value zero
> regardless of predicate quality** — which is the plan's own definition of `SELF-AUTHORED`, wearing an
> admissible provenance label.
>
> **3.** The five-gate attrition funnel — P7's one number, and the plan's evidence that the rejector is
> real — is **undefined at its first gate**. G0 is a verbatim-quote guard over `clause.quote` and
> `clause.span`. The 280 harvested FME candidates are derived from formulas and data validations and carry
> `clause: None` (`03` P4-B1). Nothing in any document says what G0 does with them. If it rejects, the
> product has zero admitted predicates and D-REJECT is unreachable; if it skips, stage one of the funnel is
> decorative and its `280 → 280` row is a green number carrying no information.

---

## §0 — THE FIVE MECHANISMS, AND WHERE EACH RECURS

The corpus documents five silent false negatives. Each had a *mechanism*, and each mechanism reappears in
this plan at a level the plan's guards do not reach. Reading the findings against this table is faster than
reading them as a list.

| # | Mechanism | Its documented instance | Where it recurs **in this plan** |
|---|---|---|---|
| M1 | **The numerator picks its own denominator** | 99.2% settled from a denominator built out of the numerator | **G2's registry bar** (F1) · **G-SETTLE's `beats_baselines`** (F30) · **P0's `gates_live/gates_written`** (F8) · **P14's `surfaces_passing/len(SURFACES)`** (F11) |
| M2 | **The oracle and the system under test share a component** | a regex and openpyxl reach the identical wrong 35 by the identical mechanism | **`TEMPLATE-COMPUTED` corpus vs `calc/`** (F2) · **G-EVAL arm 2's human oracle** (F3) · **A vs A′ on four of eight agreement fields** (F20) |
| M3 | **Scope truncation — something is silently outside the count** | the hidden `Dropdown` sheet; `EncryptDId` null on 2,005 of 2,005 | **F11 mutants dropped from `O`** (F19) · **cells that leave `inScope` via `OUT_OF_SCOPE`/`INFORMATIONAL`** (F13, F14) · **`ci/no-green-tick.sh`'s scan set** (F28) |
| M4 | **A count is right and every body is wrong** | `<f[ >][^>]*>` matched 505 and swallowed 50 of 50 closing tags | **the sweep's "at least one guard fails"** (F4) · **`caught / active` counts entries, not guards** (F4) |
| M5 | **A clean, well-formed number with no information in it** | `MS = 100.1%`; the blank template's 505 cached zeros | **arm 2 with no failing condition against its one independent engine** (F3) · **`clean_corpus_independent_of_predicate`** (F5) |

---

## §1 — THE FINDINGS

### 1.1 A test could pass while the thing it claims to test is broken

---

#### **F1 — G2's registry bar computes `K/O` over a denominator the predicate chooses after the campaign** · **FATAL**

**Where.** P7-B3 (`qualify/g2_kill.py`, `KillBar.REGISTRY`), `04` §P7-B3; the envelope at P4-B1, `03`.

**The mechanism.** The registry bar is *"`K/O ≥ 0.80` on the fault classes the predicate **claims** to
cover"*. Every document repeats that sentence. **No field of `Candidate` or `Predicate` holds such a
claim.** `03` P4-B1's envelope is exhaustive — `id, version, kind, template, schema_keys, host_fns,
obligation_id, clause, rationale, applicable, expr, witness, reason_if_inapplicable, tolerance,
external_deps` — and there is no fault-class declaration in it. The only place a fault class appears is
`FaultWitness.fault_class`, described in `05` §0.2 as *"the class the predicate CLAIMS to cover"*, and the
witness set is **selected by `qualify/g2_kill.py` at admission, from mutants that already killed**.

**The failure scenario, concretely.** A `sum_identity` predicate over `'3. Portfolio'!O7` is run against a
14-class campaign. It kills F01 (sign flip) and F03 (off-by-one) on its own read set; it is structurally
blind to F10 (legal enum substitution), F12 (homoglyph), F13 (carry desync in the pair form) and F14
(vocabulary-gap). Overall `K/O = 0.21`. G2 selects three witnesses from the mutants that died — all F01/F03
— stamps `fault_class: F01` on them, and the registry bar is then evaluated over `{F01, F03}`, where
`K/O = 0.97`. The predicate is admitted. Its `qualification.g2` block reads `0.97`, the predicate library
prints `0.97`, and the attestation signs it. **Nothing in the plan is red.**

**Why the existing controls do not reach it.** NC-Q05 checks the *arithmetic* (`K ≤ O ≤ G`, `KR ≤ 1`).
NC-Q06 checks the *site universe*. Both are satisfied. The defect is in the *class partition* of the
campaign, and no control touches it.

**Repair.**
1. Add `claims_fault_classes: tuple[str, ...]` to `Candidate`, **required, non-empty**, inside
   `envelope_projection()` so it is part of `code_sha256` and cannot be edited post-hoc without a new
   identity.
2. `g2_kill.check()` computes the registry bar **only** over `cand.claims_fault_classes`, and **raises**
   if any claimed class has `O == 0` on this campaign (an unexercised claim is not a claim).
3. New negative control **NC-Q23 — `injectors/claims_from_kill_vector.py`**: derive `claims_fault_classes`
   from the classes that killed. Guard `test_nc__Q23_claims_precede_the_campaign` asserts the claim's
   commit is a git-ancestor of the campaign id's, exactly as `test_corpus__brief_predates_first_workbook`
   does for the fill brief. Admission-side twin: an honestly-declared predicate whose claimed classes all
   have `O > 0` is admitted.
4. The predicate library renders **both** `K/O` over the claimed set **and** `K/O` over all fourteen
   classes, side by side. A gap between them is the number a reviewer wants.

---

#### **F2 — the `TEMPLATE-COMPUTED` clean corpus is generated by the code under test** · **FATAL**

**Where.** P8-B2 (`qualify/corpus/template_computed.py::synthesise`), `04`; P3-B4 (`calc/evaluate.py`),
`02`; P9-B1 (`probes/template_diff.py`), `05`; P5 exit criterion 1, `03`; G4, `04` P8-B3.

**The mechanism.** `synthesise` fills only the input cells and *"let[s] the workbook's own 505 formula
cells compute the rest via `src/cdfc/calc/`"*. `template_diff` compares the filed value against *"the value
obtained by evaluating the template's formula over the filed inputs"* — using `src/cdfc/calc/`. The
`sum_identity`, `cross_sheet_equality` and `tally_identity` harvest classes (78 + 196 + 3 = 277 of the 515
predicates) assert exactly the identities `calc/` just enforced when it produced the file. **The oracle and
the system under test are the same function.** This is M2.

**The failure scenario.** Three of the plan's load-bearing acceptance conditions become tautologies:

- **P5 exit 1** — *"Clean filing ⇒ 0 FAIL. A predicate firing on a cell IFSCA's own artifact computed is a
  genuine false failure and must be investigated."* For the 227 arithmetic predicates it is arithmetically
  impossible to fire, because `calc/` wrote the values. The gate cannot detect a *wrong* arithmetic
  predicate; it can only detect a predicate that disagrees with itself.
- **P9 exit 2** — `test_rel__td_fires_on_zero_template_computed_clean_filings` is `x == x`. It is green on
  a `template_diff` implementation that always returns `[]`, and it is green on one whose tolerance is
  1,000×.
- **G4 (this is the fatal half).** `TEMPLATE-COMPUTED` is in `ADMISSIBLE`. `n ≥ 30` such filings with zero
  fires gives a Wilson upper bound of `0.1190` → `ADVISORY`; `n ≥ 189` gives `≤ 0.02` → **`BLOCKING`**. The
  corpus generator is deterministic from a seed, so `n = 189` costs one command. **The plan therefore
  permits a `BLOCKING` severity tier to be bought, in an afternoon, from a corpus the product generated
  about itself** — which is the exact thing `SELF-AUTHORED` renders `uninformative` to prevent.

`04` §7.6 declares a *related* residue ("that an FFR measured on `TEMPLATE-COMPUTED` transfers to real
filings"). That is a transfer question. **This is not a transfer question.** The expected FFR of an
arithmetic predicate on this corpus is zero regardless of the predicate's quality, which is the plan's own
one-line definition of an uninformative rate.

**Repair.**
1. **`TEMPLATE-COMPUTED` is inadmissible for any predicate whose AST reads a cell the generator computed.**
   Mechanised: `g4_ffr.check()` intersects `read_keys(cand)` with `synthesise`'s `computed_cells` set and
   **raises `UninformativeCorpusError`** on a non-empty intersection — the same exception, the same
   fail-closed shape, as `SELF-AUTHORED`.
2. It remains admissible for predicates that read only input cells (membership, bounds, dates,
   `conditional_required`) — which is a real and useful residual licence, and the narrow warrant is stated
   narrowly.
3. **P5 exit 1 and P9 exit 2 are re-founded on a corpus the product did not compute** — the blind-filled
   corpus, or, before it exists, `REGISTER-DERIVED` for the membership classes plus a **hand-filled**
   single filing whose derived cells were typed by a person from the formula text. One filing is enough to
   make the gate non-vacuous; zero is what the plan currently has.
4. New negative control **NC-Q24 — `injectors/tc_licenses_arithmetic.py`**, which re-enables the
   intersection. Guard: `test_nc__Q24_template_computed_cannot_license_an_arithmetic_ffr`. Admission-side
   twin: `test_nc__Q24b_template_computed_licenses_a_membership_ffr`.

---

#### **F3 — G-EVAL arm 2 has no failing condition against the only independent instrument, and no budget for a second author** · **FATAL**

**Where.** P3-B4, `02`; gate G-EVAL, `00` §6; `02` §Y open item 3.

**The mechanism.** `02` §0.2 N1 is the plan's best piece of work: it measured that the blank template's 505
cached values are 301 zeros and 204 `"NA"` strings, and that G-EVAL as originally written **cannot fail**.
Arm 2 was added to fix it. Arm 2's threshold is:

> *100% against (a) a **human-authored expectation file**, written from the formula text by a person who
> did not write the evaluator; disagreements against (b) the digest-pinned offline LibreOffice engine are
> **published, never silently resolved**.*

Two things follow, and both are fatal to the arm.

**(i) There is no failing condition against (b).** LibreOffice is the only *independent* instrument in the
pair. Its disagreements are written to the `engine_disagreement` table and published. A build whose
evaluator disagrees with LibreOffice on **every** non-trivial cell passes arm 2, provided it agrees with
the expectation file. The gate's independence therefore contributes nothing to its pass/fail.

**(ii) The expectation file's author is the evaluator's author.** The plan's effort model is explicit and
consistent: one competent engineer, ~6 productive hours a day, no context switching. Person-days of a
*different* person are enumerated everywhere they exist — corpus (P8-B1, 15–25), adjudication (P10-B2,
3–5), κ re-rate (P10-B3, 1), strata (P12-B1, 2+1), the proviso labeller (P7-B2, 0.5), the admission signer
(P7-B4, 0.25), the transfer operator (P15-B1, 4–6 h). **P3 has none.** So by the plan's own resource model
arm 2 resolves to `02` §Y's second branch: *"if no, it is a self-check and `docs/measurements/P3-evaluator.md`
says `SAME-AUTHOR — a weaker instrument`"*.

**The failure scenario.** The engineer implements `AGGREGATE(15,6,…)` with a subtly wrong tie-break, writes
the expectation file from the same mental model an hour later, and both agree. LibreOffice disagrees on 40
cells; those 40 are published in a table nobody's gate reads. G-EVAL is green. `O` is founded on that
evaluator, `K/O` is quotable, `TEMPLATE_DIFF` ships, and the barrier that `02` §0.2 N1 was written to
repair has been repaired into a different shape of the same defect. **This would be the sixth instance in
this corpus, committed inside the build that documented the fifth.**

**Repair.**
1. **Budget the second author.** 1.5–2 person-days of someone who has not read `calc/`, in P3's effort
   table, in the same column as every other second-person cost. If that person does not exist, the arm's
   status is `SAME-AUTHOR` and G-EVAL is recorded **`PASSED — NOT INDEPENDENT`** in `ci/GATES.md`, on the
   report surface, and beside every kill rate.
2. **Give arm 2 a failing condition against (b).** A pre-registered threshold on the LibreOffice
   disagreement set — e.g. *"disagreement on more than `d` non-trivial cells downgrades G2 to a reach
   measurement, on the same branch as arm 1's 25-cell rule"* — with `d` chosen before the first run and
   recorded in `docs/GATE-CHANGES.md`. A published disagreement that changes nothing is a log line, not a
   gate.
3. `test_arm_two_author_is_not_the_evaluator_author` — read both from `git blame` / a declared
   `authored_by` field; if equal, assert the measurement file carries the literal string `SAME-AUTHOR — a
   weaker instrument` and that the string is present on the surface that quotes the rate.

---

#### **F4 — the negative-control sweep asserts "at least one guard fails", so an entry can be caught by its weakest guard** · **FATAL**

**Where.** `01` §2.0 step 3; `02` P0-B3 (the sweep, restated); `test_nc_meta__every_injector_flips_its_guard`
(registry row 10).

**The mechanism.** The sweep's contract is: guards pass clean → apply injector → *"Re-run **only** the named
guard tests. Assert **at least one fails**, and record which."* Entries routinely name three to five guards.
NC-Q08 names five; NC-C01 names three; NC-A05 names two; NC-P01 names three including a golden and a
positive control.

**This is M4 — a count that is right while the bodies are wrong.** `caught / active` counts *entries*, not
*guards*. An entry is `caught` when any one of its guards goes red.

**The failure scenario.** `injectors/render_self_authored_ffr.py` is applied. `test_nc__Q08c_no_ffr_without_provenance_and_n`
goes red because the injected renderer also drops `corpus_id`. The sweep records NC-Q08 as `caught` and
prints `caught = 47 of 47`. **`test_nc__Q08a_renders_uninformative` — the assertion that no digit reaches
the FFR element, criterion A4, the one the whole provenance story rests on — was never exercised, and could
have been deleted three commits earlier.** `test_nc_meta__no_orphan_guard` does not catch this: the test
still exists and is still named in the catalogue. It is simply never observed red.

The plan's own thesis applied to the plan's own instrument: **a guard that has never been observed to fail
is not evidence, and the sweep as specified cannot tell you which guards those are.**

**Repair.**
1. Catalogue shape gains a per-guard expectation:
   ```yaml
   guard_tests:
     - path: tests/negative/test_nc_predicate.py::test_nc__Q08a_renders_uninformative
       flips: true
     - path: tests/golden/test_golden__ffr_render.py::test_golden__blind_filled_renders_digits
       flips: false        # a positive control; it must STAY GREEN under the injector
   ```
2. The sweep asserts the **exact** set: every `flips: true` guard is red under the injector, every
   `flips: false` guard is green, and it fails if either set differs. `flips: false` on every guard is a
   schema error.
3. `reports/negative-control-sweep.json` reports **three** integers: `entries_caught / entries_active` and
   **`guards_flipped / guards_expected_to_flip`**. The second pair is the number the DoD's line C4 is
   really about, and today nothing computes it.
4. New meta-test `test_nc_meta__every_expected_guard_flipped`, which is registry row 10's real form.

---

#### **F5 — `clean_corpus_independent_of_predicate` is a declared boolean that nothing computes** · **SERIOUS**

**Where.** `00` P8-B3; `01` §6.3 item 6; `04` P8-B3's `g4` record; `spec/02` §II.4.1.

Every admitted predicate carries `clean_corpus_independent_of_predicate: true`. **No build computes it, no
test asserts it, no negative control breaks it, and no gate reads it.** It is the field that would have
caught F2, and it is a string in a YAML file.

**Repair.** Make it derived, not declared:
`independent = corpus.generator_import_closure ∩ predicate.evaluation_import_closure == ∅ and corpus.provenance != SELF-AUTHORED`.
`g4_ffr.check()` raises when it is false. `test_nc__Q25_independence_is_computed_not_declared` asserts the
field cannot be hand-set (it is a property, not a constructor argument), with
`injectors/independence_hardcoded.py` as its break.

---

#### **F6 — NC-C03 passes on a build with no canary layer at all** · **SERIOUS**

**Where.** `05` §L.3, NC-C03.

NC-C03 asserts that a renamed sheet produces `invalid.template_unbound` and **not** `canary_silent`. That
assertion is satisfied by a system in which `selfcheck/` does not exist. The entry is honest about carrying
`injector: NONE`, and it names NC-C04 as its positive control — but the two are separate catalogue rows
that can be red and green independently, and a phase gate reading `caught == active` will not notice that
NC-C03 alone is vacuous.

**Repair.** Bind them: NC-C03's guard test asserts, in the same test body, that the canary loop **did run**
on a different fixture in the same session (`canariesRun > 0` on the reference fill) before asserting the
cause on the renamed-sheet fixture. A test that proves a layer did *not* fire must, in the same breath,
prove the layer exists.

---

#### **F7 — `ci/no-bare-absence.sh` is defeated by writing the words "positive control" on the line** · **SERIOUS**

**Where.** `01` §5.4; `02` P0-B3.

The gate greps `src/`, `tests/`, `docs/` for `does not occur`, `zero hits`, `not present in`,
`no occurrences` *"on a line that does not also name a positive control"*. "Names a positive control" is
implemented as a lexical co-occurrence. Any author who has read the gate can satisfy it in four words.

**Repair.** The gate should require a **resolvable reference**, not a phrase: a line asserting an absence
must cite a `reports/validation-ledger.jsonl` row id, and the gate resolves it and asserts the row's
`positive_control_count > 0`. `assert_absent` already writes both counts; the grep should read them.
Planted control: a line citing a ledger row whose control count is zero must fail.

---

#### **F8 — P0's exit gate is `x == x`** · **SERIOUS**

**Where.** `00` P0; `02` P0's measurement and exit gate.

The number is `gates_live / gates_written = 12 / 12`, denominator 16, with four rows `PENDING`. The exit
condition is `gates_live == gates_written`. **`gates_written` is defined as the gates whose subject exists,
which is decided by the same person deciding whether a gate can be demonstrated.** Any gate that resists
demonstration is moved to `PENDING` with a phase name attached — which the plan explicitly permits — and
the ratio becomes `11/11`. The gate cannot fail.

This matters more than it looks: P0's gate is the one that certifies the honesty machinery every later
phase's DoD depends on.

**Repair.** Pre-register the **set**, not the count. `ci/GATES.md` rows 1–13 are named in `02` §1 R5 as
demonstrable at P0. The exit gate becomes: *these thirteen row ids are `LIVE`; moving any of them to
`PENDING` fails the gate and requires an appended argument in `ci/GATES.md`, dated.* Same discipline as
`docs/HARVEST-DELTA.md`. And `test_p0__pending_set_is_exactly_the_four_named_rows`.

---

### 1.2 A phase gate could be satisfied by a system that does not work

---

#### **F9 — G0 over the harvested set is undefined, and P7's headline number depends on it** · **FATAL**

**Where.** P7-B2 (`qualify/g0_scope.py`), `04`; P4-B4 (the harvest), `03`; P7's measurement and exit gate.

**The mechanism.** G0's six closed rejection reasons all presuppose a clause: `g0.quote_not_located`,
`g0.quote_ambiguous`, `g0.span_mismatch`, `g0.proviso_undisposed`, `g0.proviso_arithmetic`,
`g0.declared_proviso_missing_emission`. `03` P4-B1 types the envelope's clause as `Clause | None` and its
obligation as `str | None`, and the harvest classes (`cross_sheet_equality`, `sum_identity`, `membership`,
`numeric_bound`, …) are derived from the workbook's own formulas and validations — **they cite no
regulation and have no verbatim quote.** Nothing maps a harvested predicate to an `OBL-nnn`.

**The failure scenario, both branches.**
- **G0 rejects clause-less candidates.** All 280 die at stage one. ALR's five `≥ −1e17` bounds never reach
  G3, so **D-REJECT — the plan's flagship demonstration that the gate is not decorative — is unreachable**,
  and the product has zero admitted predicates for a reason nobody planned for.
- **G0 skips clause-less candidates.** Stage one of the funnel reads `280 → 280`, the funnel's first column
  is a constant, and P7's one number opens with a row that carries no information. Worse, the *skip* is the
  vacuous pass at the gate level: a gate that does not apply to the population it is run over is reporting
  a pass it did not compute.

Neither branch is written down. Both pass their local tests: P4's `test_golden__harvest_count__fme` pins
280; P7's `test_golden__all_280_bind_nonzero` is a G1 test. **The two phases pass in isolation and the
funnel is broken.**

**Repair.**
1. Decide it, in `03` or `04`, with a record: a harvested candidate's `obligation_id` is
   `OBL-TEMPLATE-<sheet>-<ref>` referring to a **template-derived** obligation whose "instrument" is the
   pinned blank and whose "quote" is the formula or validation text, so `source.find(quote)` is meaningful
   and deterministic; **or** G0's outcome for `kind == "harvested"` is an explicit, counted
   `SKIPPED_NOT_APPLICABLE` row that renders in the funnel as its own column and **is never counted as a
   survivor**.
2. Either way: `test_g0__disposition_of_a_clauseless_candidate_is_specified_and_counted`, and the funnel
   renders `entered / skipped / survived` at stage one, three integers.
3. Publish `harvested_predicates_with_an_obligation / 280` as a P7 subordinate number. Today it is `0/280`
   and nobody has written that down.

---

#### **F10 — G-READERS gates only the three fields on which every instrument already agrees** · **SERIOUS**

**Where.** `00` §6 G-READERS; `02` P1-B3's competence matrix.

The gate is: A and B agree on `{n_sheets, sheet_names, hidden_sheets}` for 9 of 9. Those are exactly the
three fields where `COMPETENCE` admits all three instruments, and `02` §0.2 N3 has already measured them as
agreeing on the flagship workbook. The four fields where a disagreement is *known to exist* —
`n_cells`, `n_formula_cells`, `n_validations`, `n_defined_names` — are the four from which openpyxl has
been declared incompetent. The gate's FAIL branch (*exclude the workbook*) has no realistic path to firing.

A gate with a near-certain pass produces no information, and P1's exit gate spends a criterion on it.

**Repair.** Keep G-READERS as a floor, and add the gate that can actually fire: **`G-READERS-B` — for each
of the four `A`/`A′`-only fields, A and A′ agree on 9 of 9, and `test_nc__P09_mutating_A_moves_only_A` is
green for *that field's* extraction path, not only for the validation walk.** That is the only version of
the dual-reader claim that carries information for the fields the project's founding defect lives in.

---

#### **F11 — P14's exit gate compares a registry against itself** · **SERIOUS**

**Where.** `07` P14's measurement and exit gate criterion 1.

`surfaces_passing_all_four_gates == len(SURFACES)`, where `SURFACES` is the registry the same build wrote.
The plan declares the residue (NC-N09, *"k of the n surfaces we knew about"*), which is honest — but the
**gate** still has no floor, and a surface that cannot pass SG1–SG4 can be removed from `SURFACES` to make
the gate green. NC-A10 catches a surface that renders *through the known render paths*; it does not catch a
surface **deleted from the registry**.

**Repair.** `SURFACES` is append-only with a growth log, exactly like `catalogue.yaml`. Removing a row
requires a dated argument in `docs/measurements/P14-surface-audit.md`, and
`test_surface__registry_is_append_only` fails the build otherwise. The measurement additionally publishes
`|SURFACES|` as a time series, so a registry that shrinks the day before a gate is read is visible.

---

#### **F12 — G-CORPUS's `n ≥ 30` is satisfiable entirely from the corpus of F2** · **SERIOUS**

**Where.** `00` §6 G-CORPUS; `04` P8's exit gate criterion 1.

G-CORPUS requires `n ≥ 30` with `corpus_provenance ∈ {BLIND-FILLED, TEMPLATE-COMPUTED, REGISTER-DERIVED,
REAL-PARTNER, PUBLIC}`. `synthesise(..., n=30)` satisfies it in one command, with a corpus the product
generated about itself. **The gate whose entire purpose is to stop a self-authored FFR from shipping is
satisfiable without a single filing anyone outside this repository touched** — and its PASS branch says
*"G4 runs; predicates are admitted; the FFR-bearing surfaces ship"*.

**Repair.** Split the threshold by what each provenance can license:
`n_blind_or_real ≥ 30` for the *unrestricted* PASS branch; `TEMPLATE-COMPUTED` and `REGISTER-DERIVED`
satisfy only the **restricted** branch the plan already pre-decided (*"admit only the predicate classes the
ready-today corpora license"*), which is currently written as the FAIL branch's fallback. Make the fallback
a **named third outcome — `G-CORPUS: RESTRICTED`** — so that shipping it is a visible state rather than an
undetected pass.

---

### 1.3 A negative control is missing, is not negative, or is untestable as written

---

#### **F13 — nothing tests that the settled fraction cannot rise as a filing carries less information** · **FATAL**

**Where.** `spec/02` §3.3 (`inScope = cellsTotal − outOfScope − informational`); P5-B4
(`settled_fraction.py`), `03`; P9-B1's non-degeneracy precondition, `05`; NC-R01.

**The mechanism.** The plan guards the empty-filing attack **at the state level** and leaves it unguarded
**at the fraction level**. NC-R01 asserts that a partition relation returns `OUT_OF_SCOPE`, never `PASS`,
on an all-zero filing. Correct — and `OUT_OF_SCOPE` is **removed from `inScope`**, which is the settled
fraction's denominator. So the defence against the empty filing is a mechanism that *shrinks the
denominator*.

**The failure scenario.** Take a filing and delete values from it. Cells whose only binding evaluation was
a partition relation move `NO_PREDICATE → OUT_OF_SCOPE` and leave `inScope`. Cells still settled by
membership or bound predicates stay. `fraction = settled / inScope` **rises**. There is a filing shape —
sparse but lawful, exactly the shape `05` §0.3 built `CANARY_INAPPLICABLE_CEILING` for — on which a filer
who fills less gets a *better* settled fraction.

The plan has the right property test for the adjacent case
(`test_prop__settled_is_monotone_non_increasing_in_not_run`) and does not have this one. Every property in
`01` §1.2 is about closure *balancing*; none is about the fraction's *direction*.

**Repair.** Add the property that the design's central claim actually needs:

> **`test_prop__fraction_does_not_rise_as_the_filing_empties`** — for every filing `F` and every
> value-deletion transform `d`, `fraction(d(F)) ≤ fraction(F)`. Generator: value-deletion transforms over
> the reference fill (the same generator `05` P9-B2 already specifies for precondition monotonicity).

If it fails — and by inspection it will — the repair is a design decision that must be taken explicitly:
either `OUT_OF_SCOPE` from a *non-degeneracy precondition* stays in `inScope` (it is a statement about the
filing, not about applicability), or the surface renders the fraction with `inScope` and `cellsTotal`
side by side so a shrinking denominator is visible. **Both are defensible; silently doing neither is not.**

---

#### **F14 — `template_defects.yaml` can raise the settled fraction, and `05` states the opposite** · **SERIOUS**

**Where.** `05` P9-B1, `template_defects.yaml` ruling.

`05` writes: *"`INFORMATIONAL` is removed from the settled denominator (§II.3.3), so a template defect can
neither fail a filer nor inflate our coverage."* The first clause is right. **The second is arithmetically
wrong for the case that matters.**

For a cell also bound by a passing predicate, roll-up takes `PASS ≻ INFORMATIONAL` and nothing moves. But
for a cell whose **only** binding evaluation is the declared-defective `TEMPLATE_DIFF`, the cell moves from
`NO_PREDICATE` (in `inScope`, unsettled) to `INFORMATIONAL` (**out of `inScope`**). `fraction = s / (i−1) >
s / i`. Adding a row to `template_defects.yaml` raises the headline. The table is append-only with an
evidence command — which stops fabricated defects, not *convenient true* ones.

**Repair.** `test_defect_table_cannot_raise_the_settled_fraction` — for every entry added to
`template_defects.yaml`, recompute the reference run and assert `fraction' ≤ fraction`. If it rises, the
cell's disposition is `NO_PREDICATE(no_predicate.rule_ambiguous)` — which stays in the denominator — rather
than `INFORMATIONAL`. And correct the sentence in `05`.

---

#### **F15 — there is no negative control on the protection-resolution rule itself** · **SERIOUS**

**Where.** P2-B2, `docs/PROTECTION-RESOLUTION.md`, `02`.

The rule that produces 3,747 is written by us, before either path is coded, and both paths implement it.
NC-D02c/d prove the paths are two implementations rather than one called twice. NC-D05 proves that
*one specific misreading* (absence ⇒ unlocked, giving 6,249) is caught. **Nothing can falsify the rule.**
`02` §Z item 2 declares this honestly. But the plan then ships every fraction it will ever print as a
fraction of that number, and never revisits it — see F36 for the cheap external falsifier it already has
the data for.

**Repair.** In `docs/PROTECTION-RESOLUTION.md`, record the three lawful readings and their measured field
surfaces (**3,747 / 3,755 / 6,249**) as a table, and require every surface that prints the settled fraction
to print `denominator.generator_rule` beside it. Then run the falsifier of F36.

---

#### **F16 — the corpus firewall test cannot run under the firewall it tests** · **SERIOUS**

**Where.** `04` P8-B1: `tests/test_corpus_firewall.py::test_corpus_is_not_importable` versus
`tests/e2e/test_e2e__corpus_firewall`.

The first asserts that nothing under `src/` or `tests/` reads `corpus/` except through
`fixtures/corpus_manifest.json`. The second *"greps the corpus repo's tree for any predicate id, any CEL
fragment, or any gate output string"* — which requires the corpus repository to be present in the CI
working tree. The two cannot both hold in one CI job.

**Repair.** The contamination grep runs **in the corpus repository's own CI**, over its own tree, and
publishes a signed result whose hash enters `fixtures/corpus_manifest.json`. The main repo asserts the
hash. This also removes the temptation to check the corpus out where the predicate set lives, which is the
contamination the whole firewall exists to stop.

---

#### **F17 — `NC-Q22b` has no catalogue id of its own** · **MINOR**

`04` P8-B3 defines *"NC-Q22b (new, under NC-Q22's entry)"* with its own break, injector and guard.
`test_nc_meta__catalogue_schema` requires one entry per id and `test_nc_meta__no_orphan_guard` requires
every test under `tests/negative/` to appear in the catalogue. `test_nc__Q22b_wilson_is_decimal` belongs to
an entry that does not exist. **Repair:** allocate `NC-Q23` (or the next free id after F1's) and give it a
row.

---

### 1.4 A measurement that is an artifact of the measuring apparatus

---

#### **F18 — `U/G` measures the evaluator's coverage, not our operator mix** · **FATAL**

**Where.** P6-B3 (`qualify/observability.py`), `04`; P3-B4 (`calc/`), `02`.

**The mechanism.** `classify(clean, mutant)` compares two **recalculated** grids and marks a mutant
`UNOBSERVABLE` when they are identical. `ValueGrid` carries a `not_run` map for cells the evaluator could
not compute (unimplemented function, cycle, excluded engine-disagreement cell). **A cell in `not_run` is
identical in both grids by construction.** So every mutant whose only propagation path runs through a cell
our evaluator cannot compute is classified `UNOBSERVABLE`, removed from `O`, and removed from the kill
rate's denominator.

`U/G` is therefore *"the fraction of our mutants whose effect our evaluator cannot see"* — a property of
**our apparatus** — and it is published as *"`U/G` for our operator mix"*, a property of the **fault
model**. And because `O = G − U`, every excluded mutant **raises** `K/O`. The measurement error is
correlated with the quantity being measured, in the direction that flatters us. That is the exact shape
`01` §2.1 NC-P02 calls *"the most dangerous shape a parser error can take"*.

**Repair.**
1. Three-way classification, not two: `OBSERVABLE` · `UNOBSERVABLE` · **`INDETERMINATE_OBSERVABILITY`**
   (the recalculation touched a `not_run` cell). The third is excluded from `O` **and reported as its own
   integer**, with the cells named.
2. `Campaign.render()` prints `G · U · I · O · R · K` — six integers — and the exit gate requires
   `I` to be published beside `U/G` every time either renders.
3. `test_nc__Q26_unevaluable_cells_do_not_become_unobservable` with
   `injectors/notrun_counts_as_identical.py`; admission-side twin: a mutant propagating only through
   fully-evaluable cells is `OBSERVABLE`.

---

#### **F19 — F11 formula-override mutants are unobservable by construction, so the flagship class is discarded from `O` and `TEMPLATE_DIFF` can never clear G2** · **FATAL, and it is also a phase-contract mismatch**

**Where.** P3-B4 `recalculate(schema: TemplateSchema, facts: FactTable)`, `02`; P6-B3
`classify(clean: ValueGrid, mutant: ValueGrid)`, `04`; P9-B1 `template_diff`, `05`; P6's exit gate; P9's
exit gate; P7's G2.

**The mechanism, exactly.** `recalculate` takes the **schema** — and the schema is induced from the
**pinned blank template**, whose formula content is fixed. An F11 mutant is *"a cell the pinned blank
declares a formula carries a literal"*. Recalculating that mutant through the template's formula graph
**overwrites the literal with the formula's value**. The clean grid and the mutant grid are therefore
identical, and the observability filter classifies the plan's flagship fault class as `UNOBSERVABLE`.

Three consequences, each of which passes its own phase's tests:

- **P6.** `U/G` is inflated by the entire F11 population, and the exit gate's requirement that *"the
  per-fault-class vector has an entry for each of F01–F14"* is met with `O = 0` for F11.
- **P7.** `Campaign.kill_rate()` *"raises `CampaignArithmeticError` if `O == 0`"`. **`TEMPLATE_DIFF` —
  predicate #1, the relation the design is built around — cannot be admitted at G2 at all.** P9-B4 routes
  every relation through the five gates; this one dies at the third with an exception.
- **P9.** `TEMPLATE_DIFF` nonetheless "detects the seeded F11 pair" in P9's exit gate, because it does not
  use the observability filter — it compares the **filed** value against the recomputed one. So P9 is green
  while P7 cannot admit the thing P9 proved.

**Two phases assume different meanings of the word "recalculate", both pass in isolation, and the
integration is broken.**

**Repair.**
1. Fix the contract in one place: `recalculate` takes an explicit `formula_source: Literal["TEMPLATE",
   "FILING"]`. Observability recalculates with `FILING` (the filing's own `<f>` elements, materialised);
   `TEMPLATE_DIFF` recalculates with `TEMPLATE`. Publish the rule in `docs/EVALUATION-CONTRACT.md`.
2. `test_f11_mutant_is_observable` — seed `formula-overwritten__portfolio-O7`, assert
   `classify(...) == OBSERVABLE` and that the distinguishing-cell set is non-empty **at the overwritten
   cell**. Injector: `injectors/observability_uses_template_formulas.py`.
3. `test_g2_admits_template_diff` — the flagship reaches G2 with `O > 0` and a computed `K/O`. Without this
   the plan's headline relation is unadmittable and nobody finds out until P9-B4, twelve weeks in.

---

#### **F20 — P1's agreement vector is half apparatus, and the competence matrix is fixed from one workbook** · **SERIOUS**

**Where.** P1-B3 (`ingest/competence.py`), `02`; P1's measurement (the 8 × 9 = 72-cell matrix).

`COMPETENCE` admits all three instruments for four fields and only `A`/`A′` — **both ours, both by the same
author** — for the other four. Those four are precisely the fields where the project's founding measurement
lives (openpyxl 35 of 54). The resolution converts the one *external* disagreement the project has into a
`BLIND_CONTROLS` constant that is expected and green.

Worse: the matrix is written at P1-B3 from measurements taken on **FME alone** (`02` §0.2 N3 measures eight
fields on one workbook), and is then used to classify the remaining 64 cells of the 72-cell matrix. A
competence judgment made on `n = 1` becomes the classifier for `n = 9`.

NC-P07 guards *narrowing* competence later. Nothing guards the initial width.

**Repair.**
1. `docs/READER-COMPETENCE.md` records, per field, **the workbooks the incompetence was measured on**, and
   `test_competence__incompetence_is_measured_on_every_workbook_it_classifies` fails when a field's
   competence set is applied to a workbook where the exclusion was never measured.
2. P1's number is published as **two** vectors, never one: `agreement over three-party fields (/36)` and
   `agreement over our-two-implementations fields (/36)`, with the second labelled
   `SAME-AUTHOR — see §7.5`.
3. `BLIND_CONTROLS` grows to cover **all nine workbooks** before it is trusted; today it pins three.

---

#### **F21 — P9's one number systematically under-measures its most important build** · **SERIOUS**

**Where.** P9-B4 (`docs/measurements/P9-delta.md`), `05`; P9's measurement.

The phase's number is *"the per-relation before/after settled-count delta"*. `TEMPLATE_DIFF`'s ceiling is
957 field-surface cells — and on FME those cells are largely already bound by the 181 `cross_sheet_equality`
and 35 `sum_identity` harvested predicates, which read the same precedent ranges. So the flagship's
**delta** is near zero *by construction*, while its **detection power** (the only check in the design that
sees a formula overwritten with a literal) is unaffected.

The plan then publishes *"a relation that moved nothing is reported as moving nothing"* as a finding about
the relation. It is a finding about the metric.

**Repair.** P9 publishes **two** numbers per relation, and the second is the one that matters for
`TEMPLATE_DIFF`: (a) settled-count delta, and (b) **`|WRONG mutants this relation rejects that no admitted
predicate rejects|` over the P10 residue population** — a marginal-kill figure over the same shared `O`
that P12's `marginal.py` already computes for baselines. `test_rel__delta_and_marginal_are_both_published`.

---

#### **F22 — the headline `2,373` and the harvest do not reconcile** · **SERIOUS**

**Where.** `02` §0.2 N3 (*"2,329 of the FME workbook's 2,373 settled cells (98.1%) come from the **53
validation predicates**"*); `03` §0.4 (FME harvest v0: **20** membership predicates of 280); `07` P14-B1
(the hero pins `S = 2,373` as **MEASURED** and as a literal).

The FME workbook has 54 validations, of which 22 are list-type and 20 resolve. The harvest emits **20**
membership predicates. The claim that 2,329 of 2,373 settled cells come from *53 validation predicates*
therefore rests on a predicate set the harvest does not produce. Either 2,373 was computed from a different
enumeration than the one P4-B4 will ship, or the "53" is wrong. **Neither document reconciles them, and the
number is the product's headline.**

Compounding it: `07` pins `S = 2,373` and `U = 1,374` as **literals** in
`test_golden__report_hero__fme`, labelled MEASURED. Under `01` §1.3's normative split these are
**properties of our code**, not of the published file — they belong in `test_harvest_count`'s regime, which
is allowed to move with a `HARVEST-DELTA.md` entry. `07` §6 warns beautifully about exactly this
("a golden test launders a warrant") for the illustrative `12`, and then does it for 2,373. The first thing
P7's G3 does is reject predicates, which lowers the reachable set — so the pinned literal will fail on
correct behaviour, and will be quietly updated.

**Repair.**
1. P4-B4 publishes `static_settled_cells` **computed from the emitted envelopes**, and
   `docs/measurements/P4-harvest-distribution.md` reconciles it against 2,373 in writing. A divergence is a
   finding.
2. `test_golden__report_hero__fme` asserts `S == len(static_settled_cells(schema, registry))` and
   `S + U == inScope`; the literal `2,373` moves into `docs/HARVEST-DELTA.md`.
3. `ci/golden-asserts-values.sh` gains a sibling that would have caught both this and the `12`:
   **`ci/golden-literals-are-traceable.sh`** — every integer literal compared in `tests/golden/` must
   appear in `01` §0.3's table or in `reports/validation-ledger.jsonl`. `07` §6 names this as
   *"a review obligation ... the fourth impossible control"*. **It is not impossible; it is a grep over a
   ledger.**

---

### 1.5 Two phases assume different contracts for one interface

F19 above is the most expensive instance. Four more:

---

#### **F23 — `CanaryRow.elapsed_us` is inside the canonicalised evidence, and G-REPRO cannot hold** · **FATAL**

**Where.** P10-B1 `CanaryRow(..., elapsed_us: int)` and *"the digest of the canonicalised `CanaryReport`"*,
`05`; P11's byte-identity gate and `make determinism`, `05`/`01` §1.5.

A wall-clock duration is inside a structure whose digest a property test asserts to be order-invariant, and
whose contents feed `livenessProof` and `run.jsonl`. Two runs produce different microsecond counts →
different bytes → **`E2E-VERIFY` fails, permanently, on the first green run of P11.** `01` §1.5's
enumeration of non-determinism sources (register, clock, iteration order, float) does not contain
"durations we measured ourselves", and `ci/no-clock-in-core.sh` greps for `datetime.now()`, `time.time()`
and `TZ` — not for `perf_counter`.

The dangerous repair is the obvious one: drop `elapsed_us` from the hash. That silently removes the
evidence that the canary loop *executed* rather than being replayed from a cache, which is death D5's whole
concern.

**Repair.**
1. Timings live in `reports/perf/<run_id>.jsonl`, **outside** the hashed payload and outside `run.jsonl`.
   `PERF-CANARY2` reads them there.
2. `test_contract__no_duration_field_in_a_hashed_object` — walk every dataclass that reaches
   `canonical_json`, assert no field name matches `(elapsed|duration|_us|_ms|_ns|seconds)`, and assert no
   field's value is derived from `time.perf_counter`. Extend `ci/no-clock-in-core.sh`'s pattern set to
   `perf_counter`, `monotonic`, `process_time`.
3. Keep the *evidence of execution* without the *timing*: `CanaryRow` retains `witness_digest`,
   `observable`, `intersects_read_set`, `fired` — all deterministic — and `canariesRun == len(rows)` stays
   the assertion of death D5.

---

#### **F24 — three contracts for `settledFraction` on an `INVALID` run** · **SERIOUS**

**Where.** P5-B4 `compute() -> SettledFraction | None` (i.e. `settledFraction: null`), `03`; P11-B1
`test_contract__invalid_run_carries_no_fraction` — *"the schema **forbids** a `settledFraction` object when
`runState == "INVALID"` (a JSON Schema `if/then`)"*, `05`; and `01` §1.9's rule that **an omitted field is
a schema violation**.

`null` (we make no claim), `forbidden` (the property must be absent) and `omitted` (a violation) are three
different things, and the plan asserts all three for the same field in the same state. P5 and P11 each pass
their own contract test; the integration produces an attestation that either fails validation or drops the
`null` that E2E-INVALID exists to assert.

**Repair.** One rule, stated once: **on `INVALID`, `settledFraction` is present and `null`.** The `if/then`
becomes `{"if": {"runState": "INVALID"}, "then": {"properties": {"settledFraction": {"const": null}},
"required": ["settledFraction"]}}`. `test_contract__invalid_carries_a_null_not_an_absence`.

---

#### **F25 — `E2E-INVALID` asserts "dead predicates named" on a fixture that never reaches the predicate layer** · **SERIOUS**

**Where.** `01` §1.10 and `00` P10's negative control (*"`cdfc demo --break-parser` (renames a sheet) →
`INVALID`, dead predicates named, `settledFraction` is `null`"*); `05` §0.5's correction.

`05` proves — correctly, and it is the plan's best catch — that a renamed sheet terminates at F3 with
`invalid.template_unbound`, five steps before the canary loop. A `template_unbound` run has **no dead
predicates to name**, because no predicate ran. So the assertion in the methodology's own E2E table is
unsatisfiable. `05` fixes it inside `05` (*"now an apparatus break per §0.5"*) and **the binding document
is left wrong**, along with `00` P10's negative-control text and `01` §2.5 NC-C01a.

This is the plan's own version-churn failure: a correction that does not propagate to the document CI reads.

**Repair.** Amend `01` §1.10 and `00` P10 in the same commit as `05`'s correction, with a
`docs/CATALOGUE-CORRECTIONS.md` row (the mechanism `05` already created). Add
`test_plan__no_binding_document_asserts_a_superseded_mechanism` if that sounds excessive — it is one grep
over the corrections file's superseded assertions.

---

#### **F26 — `μ` is an accuracy in `00` and an error rate in `06`, and G-CONFORMAL's thresholds invert between them** · **SERIOUS**

**Where.** `00` §6 G-CONFORMAL and §10 (*"`μ`, the key-binding **accuracy** on population P1"*, thresholds
`μ ≤ 0.30`, `μ ≤ 0.10 ⇒ build`); `06` P13-B3 (`mu: float  # a BASE ERROR RATE, not an accuracy — the floor
formula only closes that way`).

Under `00`'s reading, *build the layer when accuracy ≤ 10%*. Under `06`'s, *build when the error rate ≤
10%*. `06` is right and says why. `00` is the binding skeleton, is what `ci/GATES.md` will be transcribed
from, and is where a reader who has not opened `06` will look.

**Repair.** Rename the field `mu_base_error_rate` everywhere, correct `00` §6 and §10 in the same commit,
and add `test_contract__mu_is_an_error_rate` asserting `decision == DO_NOT_BUILD` at `mu = 0.9` (which is
90% *accuracy* under the wrong reading and would build).

---

#### **F27 — the negative-control catalogue has colliding ids across four documents** · **SERIOUS**

The catalogue is keyed by `id`, append-only, and its meta-tests assume uniqueness. Four collisions exist,
each between documents written independently against `01`:

| id | Claimed by | …and by | …and by |
|---|---|---|---|
| **NC-E10** | `02` §X — *a vocabulary resolved from the filed artifact* | `03` §6 — *`run_cell` materialised from the evaluations* | — |
| **NC-E11** | `02` §X — ***the positive control gating every kill rate has no information in it*** | `03` §6 — *an `INVALID` run emits `0` instead of `null`* | — |
| **NC-E12** | `02` §X — *an unimplemented function is swallowed by `IFERROR`* | `03` §6 — *a run-level cause written into an item's reason field* | — |
| **NC-Q12 … Q16** | `03` §6 (digest coverage, permissive walker, lexical keys, total-without-distribution, weak pile) | `04` §0.8(e) + §4.4 (openpyxl mutant writer, cached-grid observability, control-arm cone, digest constant, gate order) | — |
| **NC-N07** | `02` P0-B4 — *a field observation quietly dropped* | `07` §3 — *an all-clear mark drawn as vector paths* | — |
| **NC-N11 / N12** | `04` §4.4 (taxonomy completeness; domain policy) | `05` §4 (the fact table holds this filing's values; relation intent) | `06` P13-B2 (*both OCR engines wrong the same way*) |

Two documents assert the collision away rather than checking: `03` §6 states *"`NC-Q11` and `NC-E08` are
the current maxima"* (false — `02` allocated `NC-E10`–`E13`), and `04` §0.8(e) states *"the Q family is
free from `NC-Q12`"* (false — `03` allocated `NC-Q12`–`Q16`).

**Why this is a green-build lie and not a bookkeeping nit.** If the catalogue loads into a dict keyed by
id, **the later document's entry silently replaces the earlier one**. `02`'s `NC-E11` — the entry that
permanently encodes the discovery that G-EVAL arm 1 is inert, the single most important row in the whole
catalogue — is replaced by `03`'s `NC-E11` about `null`-versus-zero. The sweep then reports `caught ==
active`, `test_nc_meta__no_orphan_guard` is satisfied because `test_nc__E11a_null_evaluator_passes_arm_one`
is named by *an* entry, and the guard that was supposed to keep arm 2 from being deleted as redundant is no
longer in the register anyone reads.

**Repair.**
1. `test_nc_meta__ids_are_unique` — trivial, and it must exist *before* the first entry is written, at
   P0-B3.
2. A pre-code reconciliation pass: allocate id ranges per document in `01` §2 (e.g. `02` → `E10–E19`,
   `03` → `E20–E29`, `04` → `Q30–Q49`, …), and add
   **`ci/catalogue-ids.sh`** — a grep over `plan/*.md` asserting each `NC-` id appears in exactly one
   document as a *definition*. It is thirty lines and it is the cheapest gate in the plan.

---

#### **F28 — `ci/no-green-tick.sh`'s scan set names three directories P0 does not create, and R5 makes a missing scan root a failure** · **SERIOUS**

**Where.** `01` §5.4 (`src/ templates/ locales/ static/`); `02` §1 R5 (*"every grep gate exits non-zero if
its scan root does not exist"*) and P0-B1's file list; `07` P14 SG1 (*"takes its directory list from
`labels.SURFACES` and `render.TEMPLATE_DIR`, never from a literal"*).

P0-B1 creates `src/cdfc/**` and `src/cdfc/surface/templates/report.html.j2`. There is no top-level
`templates/`, `locales/` or `static/`. Under R5 the gate exits non-zero from the first commit — so it will
be "fixed" by narrowing the scan set to `src/`, which is NC-D01's mechanism applied to the honesty gate
itself, on day one, in the phase that exists to prevent it. Meanwhile `07` gives SG1 a *third* scan set
derived from `render.TEMPLATE_DIR`, which does not exist until P14.

**Repair.** One source of truth from P0: `ci/no-green-tick.sh` reads its roots from
`src/cdfc/surface/labels.py::SCAN_ROOTS`, which at P0 is a stub containing `("src/cdfc",)` and which P14
extends. `test_nc__CI01c_scan_root_list_is_not_a_literal` asserts the script contains no directory literal.
Record the narrowing (from `01` §5.4's four names to the real tree) in `ci/GATES.md` with a reason — **a
scan set that shrinks silently is the defect; a scan set that shrinks with a diff is housekeeping.**

---

#### **F29 — P15-B1's entry criterion names a file P4-B4 does not create** · **MINOR**

`07` P15-B1 requires `docs/measurements/P4-transfer-mechanical.md` published. `03` P4-B4 produces
`docs/measurements/P4-harvest-distribution.md`. **Repair:** one name, chosen in `03`, referenced from `07`
via a module constant per `06` §0.9's rule.

---

### 1.6 Exit gates that are subjective, unfalsifiable, or evaluable only by the person who did the work

---

#### **F30 — G-SETTLE's central condition is not evaluable as written, and it is hashed before the run** · **SERIOUS**

**Where.** `00` §6 G-SETTLE; `06` P12's exit gate criterion 4: *"`beats_baselines` is True: marginal kill
strictly greater than B0, than B1 (or B1 declared not-run), than B2, and than the union"*.

`MarginalKill.killed_by_candidate_only` is `|K_c \ K_b|` — a count of mutants the candidate killed that the
baseline did not. **"Greater than B0" compares that count to what?** To zero? To
`killed_by_baseline(B0)`? To the baseline's own marginal over the candidate? Three readings, three
different gates, and the wrong one is trivially satisfiable (`|K_c \ K_B2| > 0` is true for any predicate
that kills anything B2 does not, which is most of them).

This ambiguity sits inside the artifact whose entire epistemic value is that it was **specified, locked and
hashed before the model ran**. A criterion that has to be interpreted after the result is not a criterion,
and `06` §0.5 says so about a different clause of the same rule.

**Repair.** State it as arithmetic in `PREREGISTRATION.md`:
`beats_baselines := all(m.killed_by_candidate_only > 0 and m.comparable for m in per_baseline)` **and**
`union_row.killed_by_candidate_only ≥ ceil(0.10 * union_row.observable)` — or whatever floor is argued;
the point is that a floor must exist and be a number. Add
`test_decide__beats_baselines_is_arithmetic_not_prose`, exhaustive over the `MarginalKill` tuple space, and
`test_e6__preregistration_criterion_is_machine_evaluable` — the lock refuses to write a criterion that
`decide()` cannot consume.

---

#### **F31 — DoD line C4 is the plan's load-bearing evidence and is verifiable only by its author** · **SERIOUS**

**Where.** `01` §4 (*"C4 is the load-bearing line — an engineer who cannot paste the assertion that went
red has not built a negative control"*), repeated as a gate criterion in every phase.

The pasted assertion line is prose in a PR description. Nothing re-derives it. A reviewer who did not do
the work cannot distinguish a real paste from a plausible one, and the plan's own standard for a DoD line
is *"an artifact path or a command whose output a reviewer can read without having done the work"* — which
C4 alone does not meet.

**Repair.** The sweep already produces the evidence; make it the artifact. `tools/nc_sweep.py` writes, per
entry per guard, the **captured assertion text and the pytest node id** into
`reports/negative-control-sweep.json`. C4 becomes *"the sweep report's row for `<NC-id>`, at commit
`<sha>`"* — a path, not a paste. `test_sweep__records_the_failing_assertion_text` asserts the field is
non-empty for every flipped guard.

---

#### **F32 — P9-B2's only gate on the relation set is an authoring protocol, over relations the document declines to enumerate** · **SERIOUS**

**Where.** `05` P9-B2: 25 relations, of which **7 are named**; the other 18 are governed by a seven-step
protocol ending in *"two humans sign the review row"*.

The plan is right to refuse to invent them (`05` says so explicitly, and the refusal is the correct
instinct). But the consequence is that a 5-day build with a 25-row deliverable has **18 rows of
unspecified content, one unstaffed second signer, and an exit gate that reads "every relation holds on the
clean filing and is violated by a targeted mutant"** — which, per F2, is satisfiable on the
`TEMPLATE-COMPUTED` corpus by construction for any arithmetic relation.

**Repair.**
1. The deliverable is *"the relations the corpus grounds, and the refusal log"*, not *"25"*. Delete the
   number from the phase and let `docs/RELATION-REVIEW.md`'s admitted/refused counts be the measurement —
   which is what the phase's own failure branch already says is the more interesting result.
2. Budget the second signer in person-days, as every other human step is budgeted.
3. `test_rel__every_admitted_relation_was_violated_by_a_mutant_on_a_corpus_the_relation_did_not_generate`
   — the F2 repair applied to P9's exit gate.

---

#### **F33 — equivalent-mutant adjudication is prose by the person being scored** · **MINOR**

Declared at `01` §7.8 and mitigated by making `K/V` the headline. Recorded here only so the count is
complete; the mitigation is correct and no repair is proposed beyond keeping `E` visible, which the plan
already does.

---

### 1.7 The ordering hides a dependency

---

#### **F34 — the `P9-B4 → P10-B2` edge is absent from `00`'s graph, and it moves P11 from day 104 to ~114** · **SERIOUS**

**Where.** `00` §3.1, §4, §4.1 and §7; `05` P10's entry criteria (*"**B2** | P9-B4 complete — every
admitted relation is in the registry | The residue is 'WRONG mutants that no predicate **and no relation**
rejects'"*).

`00`'s dependency graph has P10 depending on P6 and P7 only, with P9 running in parallel, and its off-path
table reads *"P10 ends ~94 · P11 ends ~104"*. `05` adds a real, well-argued edge: computing the residue
before the relations are admitted **overstates it**, which flatters us. With that edge:

```
P7 ends 84 → P9 ends 98 → P10-B2 starts 98 → P10 ends ~104 → P11 ends ~114
```

P11 is therefore **on** the critical path, tied with the spine, and the plan's stated **`k = 0` re-route
through `P0→…→P7→P10→P11` at ~104 days is wrong by ten days** — in the branch `06` §2 says the plan is
written for.

**Repair.** Add the edge to `00` §3.1 and §4, recompute §4.1 and §7, and state that at `k = 0` the critical
path is the attestation spine at ~114 days rather than ~104. A schedule that is wrong in the failure branch
is wrong exactly where it will be read under pressure.

---

#### **F35 — P7's G0 needs a pinned, span-addressable regulation text that P12-B1 builds** · **SERIOUS**

**Where.** `04` E7.6 (*"The regulation PDF and the 399-circular corpus are on disk and content-addressed"*)
and `test_obligations__span_matches_quote` (`instrument_text[span] == quote`); `06` P12-B1
(`experiment/textsource.py`, `corpus/instruments/fm-regulations-2025.text.json`, the **D5** dual-extraction
differential).

G0's whole mechanism is `source_text.find(quote)` at an exact character span. That requires an
**authoritative normalised text with stable offsets**, produced by a dual-extraction agreement harness with
a disputed-region exclusion rule. **No build before P12-B1 creates it.** P7 is five phases earlier and E7.6
asserts it as a precondition without naming the build that satisfies it.

**Repair.** Move `experiment/textsource.py` (and D5) out of P12-B1 into a new **P7-B0**, 1–1.5 days, where
its consumer is. `06` §0.9 already establishes the pattern for deferring paths to their owning document;
this is the same move for a *build*. P12-B1 then references the artifact instead of creating it, and its
2-day estimate becomes plausible (see F41).

---

#### **F36 — the denominator ships at day 22 and nothing ever validates it, though the plan buys the data that could** · **SERIOUS**

**Where.** P2 (day ~22 on the spine); P8-B1's corpus manifest (`cells_left_blank[]`, per workbook).

The 3,747 field surface is validated by two code paths agreeing on one written rule (F15). The *first
external artifact that could falsify it* arrives at P8: **≥ 30 workbooks filled by a competent person who
has never seen the predicate set.** The set of cells Person A actually wrote into is a direct, cheap,
independent measurement of "the cells a filer may fill" — the exact thing the mask is a proxy for. The plan
collects this data and never uses it for this purpose.

**Repair.** `test_mask_matches_what_a_competent_filler_filled` (see §2, rank 7). Two published integers:
cells Person A wrote that are **outside** the mask (a mask that is too small — the dangerous direction) and
cells inside the mask that **no filler in the corpus ever wrote** (a mask that is too large — the direction
that understates the settled fraction). Denominator 3,747, warrant MEASURED, and it costs one script over
data the corpus lane already produces.

---

#### **F37 — the corpus lane is sized for the gate, not for the product** · **SERIOUS**

**Where.** `00` §7 and §11 (*"the longest pole in this plan is ... the corpus"*, 15–25 person-days); `04`
§0.9 (`hi(0,189) = 0.019920` — **`n ≥ 189` for `BLOCKING` at zero fires**); G-CORPUS's `n ≥ 30`.

30 blind-filled workbooks satisfy G-CORPUS and license `ADVISORY` (`hi(0,30) = 0.1139`). **189 are needed
before a single predicate can be `BLOCKING`.** The plan states the consequence honestly (*"on day one
almost nothing is BLOCKING"*) but budgets the lane at the gate's number, and then names that budget as the
programme's longest pole. At 15–25 person-days for 30 workbooks, 189 workbooks is **95–160 person-days** —
four to seven months of one person, which dwarfs the 114-day engineering path and is the real critical path
of the *product*, as opposed to the *paper*.

**Repair.** Publish both numbers in `00` §7: *the gate needs 30; the severity axis needs 189; at the
measured fill rate those are X and Y person-days.* Then take the decision explicitly — ship with everything
`ADVISORY` and say so (defensible, and the plan already argues it), or fund the larger corpus. **What is
not defensible is a schedule that shows the corpus finishing while the severity tier it exists to produce
remains permanently undefined.**

---

#### **F38 — NC-Q02 is green for four phases while proving nothing** · **MINOR**

`02` §1 R5 ships `registry.py::load_or_refuse()` refusing **unconditionally** at P0, with
`test_nc__Q02_unqualified_predicate_does_not_load` green from P0 to P4. The plan declares this
(*"a stub that refuses everything is admissible only because its admission-side twin is impossible until
P4 — recorded in the DoD's line C5"*), which is exactly right. Recorded here only so the count is complete:
the catalogue's `caught / active` figure carries a green entry with no information in it for four phases,
and the sweep should report it in a **third** column (`PROVISIONAL — no admission-side twin yet`) rather
than in `caught`.

---

### 1.8 Effort estimates that will distort sequencing

The plan's estimates share one assumption — *one competent engineer, ~6 productive hours a day, no context
switching* — and are internally consistent with each other. They are not consistent with the work.

---

#### **F39 — P0 at 4 days** · **SERIOUS**

P0-B1 through B4 deliver: a hash-pinned lockfile; a 13-stage CI pipeline; **nine** shell gates plus an AST
scan gate; the negative-control catalogue schema, the `Injector` protocol, nine injectors, the sweep and
**four meta-tests**; an AST import-closure walker reused by three later phases; a two-platform test census;
the validation-ledger schema and its test; a licence resolver with a denylist; the corpus vendored with an
integrity golden carrying a *value* assertion per workbook; the foundation probe with eight measurements;
and **twelve gates observed red with their assertions recorded**. Four days is 24 productive hours.

The realistic figure is **8–10 days**. This matters beyond the number: P0 is where every later phase's
evidence machinery comes from, and an underestimated P0 is the phase that gets compressed, which turns the
sweep into a shell script and the catalogue into a list.

---

#### **F40 — P3-B4 at 7 days, on the critical path, gating P6, P7, P9 and P12** · **SERIOUS**

Seven days delivers: a topological evaluator over `carry_edges` with cycle detection; **nine** Excel
functions including `AGGREGATE(15,6,…)` (k-th smallest **ignoring error values**, over an array),
`COUNTIF` with Excel wildcard semantics (`*`, `?`, `~` escaping, case-insensitivity), `INDEX`/`ROW`/`ROWS`
array forms, `_xlfn.SINGLE` implicit intersection, and element-wise array division producing `#DIV/0!`; six
`ExcelError` types with `IFERROR` interaction; `Decimal` under a pinned context with no float anywhere; a
seeded discriminating-fixture generator that drives six named semantics onto non-trivial branches; a
human-authored expectation file; **and a digest-pinned offline LibreOffice differential with an
`engine_disagreement` table**.

Any one of the last three is a day. The array semantics alone are two. A realistic figure is **12–15
days**, and P3 is barrier 2 — nothing downstream can quote a kill rate until it lands. An underestimate
here does not slip the schedule evenly; it slips the *evidence order*, because the cheapest way to make a
7-day estimate come true is to skip arm 2 (F3).

---

#### **F41 — P12-B1 at 2 days including a dual-extraction PDF differential** · **SERIOUS**

Day 1 of B1 is *"`textsource`, `enumerate_shall`, the pool and its golden"* — i.e. **two independent PDF
extractions with a normalised-sentence agreement check, a disputed-region exclusion rule with page
numbers, an `ExtractionManifest`, a `shall` enumerator with an exact chapter-title match that raises, and a
golden over a pinned regulation with first/median/last value assertions.** That is the D5 differential,
which `06` itself adds to `01` §1.4's table of four required differentials. It is 3–4 days on its own.

**Repair:** F35's move (textsource → P7-B0) fixes both findings at once and makes the remaining B1 — draw,
power, prereg, lock — a genuine 2 days.

---

#### **F42 — P9-B2 at 5 days for 25 relations of which 18 are unenumerated** · **SERIOUS**

See F32. An estimate over unspecified content is not an estimate; it is a placeholder that will be defended
as a commitment. The estimate should be given for the enumerated work (the 7 named relations, the registry,
the partition machinery, the basis guard, the review protocol) and the remainder recorded as **open scope
with a decision rule**, which is the discipline every other open item in this plan receives.

---

#### **F43 — the 114-day critical path assumes 2–3 engineers, and every independence claim assumes one author** · **SERIOUS**

`00` §7: *"Critical path, off-path phases parallelised — 114 — requires ~2–3 engineers to realise"*, while
every per-phase effort table states *one competent engineer, no context switching*. Both cannot hold: with
2–3 engineers the estimates are invalid (they contain no coordination cost, no review cost, no
integration cost); with one engineer the serial total is 170 and 114 is unreachable.

More seriously, **the plan's independence claims all require a second *author*, and no budget contains
one**: `reader_lxml_b.py` (A′), `styles_mask_b.py` (path B), G-EVAL arm 2's expectation file, and the
second signature on `docs/RELATION-REVIEW.md`. NC-D02d and NC-P09 prove *two code paths*; `01` §7.5 admits
they cannot prove *two minds*. With a single engineer, every differential in this plan is a same-author
differential, and the one place a genuinely foreign instrument existed (openpyxl) has been declared
incompetent for the fields where it disagreed (F20).

**Repair.** State the staffing model once, at the top of `00` §7, and derive both numbers from it. If it is
one engineer: 170 days, and every same-author differential is labelled `SAME-AUTHOR` on the surface that
quotes it. If it is 2–3: re-estimate with coordination cost, and **assign the second author to A′, mask
path B and the arm-2 expectation file explicitly**, because those three are the only places where a second
person buys evidence rather than throughput.

---

#### **F44 — P10-B1 at 4 days excludes the calibration `05` §5.1 requires** · **MINOR**

`05` §5.1 makes `MAX_WITNESSES` an open item to be closed by *"run P10-B1 with `MAX_WITNESSES ∈ {1, 3, 5}`
over the template-computed clean corpus, measure the inapplicability rate at each, and publish the curve"*.
Three campaigns over the corpus are not in the 4 days. **Repair:** add 0.5 days and name the deliverable
(`docs/measurements/P10-canary-cost.md`'s curve) in B1's file list.

---

## §2 — SEVERITY COUNTS

| Severity | Count | Findings |
|---|---:|---|
| **FATAL** — a broken system could ship and be believed | **9** | F1, F2, F3, F4, F9, F13, F18, F19, F23 |
| **SERIOUS** — wastes significant work or invalidates a published number | **30** | F5, F6, F7, F8, F10, F11, F12, F14, F15, F16, F20, F21, F22, F24, F25, F26, F27, F28, F30, F31, F32, F34, F35, F36, F37, F39, F40, F41, F42, F43 |
| **MINOR** | **5** | F17, F29, F33, F38, F44 |
| **Total** | **44** | |

**By question category:** (1) test passes while the thing is broken — 8 · (2) gate satisfiable by a broken
system — 5 · (3) missing or non-negative control — 5 · (4) measurement is an apparatus artifact — 5 ·
(5) two phases, two contracts — 6 · (6) subjective or self-evaluable gate — 4 · (7) ordering hides a
dependency — 5 · (8) effort estimates — 6. (Several findings sit in two categories; each is counted once,
under its dominant one.)

---

## §3 — THE TEN TESTS THIS PLAN MOST NEEDS AND DOES NOT HAVE

Ranked by **how much wrong belief the absence of each permits**, not by cost. Six of the ten are under a
day.

---

### 1. `test_g2_denominator_is_declared_before_the_campaign` — *the fault-class claim*

**Kills:** F1. **The belief it prevents:** *"this check rejects 97% of the defects it is meant to catch."*

`claims_fault_classes` becomes a required, content-addressed field of the envelope. The test asserts
(a) the field is non-empty and inside `code_sha256`; (b) the commit introducing it is a **git-ancestor** of
the campaign id it is scored against; (c) `g2_kill.check()` raises when any claimed class has `O == 0`;
(d) narrowing the claim after a campaign produces a **new** `code_sha256`, i.e. a different predicate.
Injector: `injectors/claims_from_kill_vector.py`. Admission-side twin: an honestly-declared predicate with
all claimed classes exercised is admitted.

**Without it, the plan's central gate lets every admitted predicate choose the denominator of its own
quality score** — which is the one error this project's corpus documents twice, in one afternoon, by the
person hunting for it.

---

### 2. `test_clean_corpus_is_not_produced_by_the_code_under_test` — *corpus independence, computed*

**Kills:** F2, F5, F12, and the vacuous halves of P5's and P9's exit gates.
**The belief it prevents:** *"0 false failures across 189 clean filings."*

For every `qualification.g4` record: assert the corpus generator's import closure is **disjoint** from the
predicate's evaluation closure, and that `read_keys(predicate) ∩ corpus.computed_cells == ∅`. Violation
raises `UninformativeCorpusError` — the same fail-closed shape as `SELF-AUTHORED`, in the same function, so
there is no second code path to forget. `clean_corpus_independent_of_predicate` becomes the **computed**
result, not a declared boolean.

**Positive control, and it is what stops this from being reject-everything:**
`test_register_derived_licenses_a_membership_ffr` — `REGISTER-DERIVED` is genuinely independent of our
evaluator and must still license an FFR for the identity classes.

---

### 3. `test_prop__fraction_does_not_rise_as_the_filing_empties` — *monotonicity in the direction that matters*

**Kills:** F13, F14. **The belief it prevents:** *"63.3% settled"* on a filing that carries less
information than the one that scored lower.

Property: for every filing `F` and every value-deletion transform `d`,
`fraction(d(F)) ≤ fraction(F)`. Generator: the value-deletion transforms `05` P9-B2 already specifies.
Companion: `test_defect_table_cannot_raise_the_settled_fraction`.

The plan has `test_prop__settled_is_monotone_non_increasing_in_not_run` — the same statement for one state
transition. **This is the general form, and it is the one the product's headline claim actually needs**,
because `OUT_OF_SCOPE` and `INFORMATIONAL` leave `inScope` and are both reachable by making the filing
worse.

---

### 4. `test_f11_mutant_is_observable` — *the flagship must reach the denominator*

**Kills:** F19, and half of F18. **The belief it prevents:** *"`K/O = 0.82` under fault model v3"*, computed
over a population from which the design's most important fault class was silently removed.

Seed `formula-overwritten__portfolio-O7.xlsx`; assert `classify(clean, mutant) == OBSERVABLE` and that the
distinguishing-cell set contains the overwritten cell. Companion:
`test_g2_admits_template_diff` — the flagship relation reaches G2 with `O > 0` and a computed `K/O`.
Injector: `injectors/observability_uses_template_formulas.py`.

This is also the test that forces the `formula_source: TEMPLATE | FILING` contract into
`docs/EVALUATION-CONTRACT.md`, where two phases currently disagree in silence.

---

### 5. `test_nc_meta__every_expected_guard_flipped` — *the sweep's real form*

**Kills:** F4, and it is the only finding here that is about the **instrument that finds the others**.
**The belief it prevents:** *"caught = 47 of 47 active"*, over a catalogue in which the guards that matter
were never observed red.

Per-guard `flips: true|false` in the catalogue; the sweep asserts the **exact** set, not "at least one";
`reports/negative-control-sweep.json` publishes `guards_flipped / guards_expected_to_flip` beside
`entries_caught / entries_active`.

**This is the plan's own thesis applied to the plan's own apparatus**, and the plan currently has the
weaker version of the assertion it demands from everyone else.

---

### 6. `test_g0__disposition_of_a_clauseless_candidate_is_specified_and_counted`

**Kills:** F9. **The belief it prevents:** a funnel whose first stage reads `280 → 280` and means nothing —
or a P7 that rejects everything for a reason nobody planned.

Assert that a harvested candidate with `clause is None` has exactly one specified outcome; that the outcome
is a **counted** column in `docs/measurements/P7-attrition.md`; and that
`harvested_predicates_with_an_obligation / 280` is published. Today the answer is `0 / 280` and no document
contains it.

---

### 7. `test_mask_matches_what_a_competent_filler_filled` — *the only external check on the denominator*

**Kills:** F15, F36. **The belief it prevents:** every fraction in the product, silently, forever.

Over the blind-fill corpus: for every workbook, compute the set of cells Person A wrote. Publish two
integers — **cells written outside the 3,747 mask** (the mask is too small: the dangerous direction, and
the one that would make every settled fraction an overstatement of coverage) and **cells inside the mask
that no filler ever wrote** (the mask is too large). Denominator 3,747, warrant MEASURED.

**It costs one script over data the corpus lane already produces**, and it is the only instrument in the
entire plan that could falsify the number under every other number. `02` §Z item 2 declares the gap
honestly and then leaves it open; this closes it with the plan's own data.

---

### 8. `test_contract__no_duration_field_in_a_hashed_object`

**Kills:** F23. **The belief it prevents:** *"byte-identical on a second machine"* — and, more insidiously,
the quiet repair in which `elapsed_us` is dropped from the hash and the evidence that the canary loop
executed goes with it.

Walk every dataclass reaching `canonical_json`; assert no field name matches
`(elapsed|duration|_us|_ms|_ns|seconds)` and no value derives from `perf_counter` / `monotonic` /
`process_time`. Extend `ci/no-clock-in-core.sh`'s pattern set to those three. Timings move to
`reports/perf/<run_id>.jsonl`, outside the payload, where `PERF-CANARY2` reads them.

---

### 9. `test_arm_two_oracle_is_a_different_author`

**Kills:** F3. **The belief it prevents:** *"our evaluator reproduces the regulator's own values"* — the
sentence under every kill rate in the programme.

Read the expectation file's author and `calc/`'s author from a declared `authored_by` field cross-checked
against `git blame`. If they are the same person, assert that `docs/measurements/P3-evaluator.md`,
`ci/GATES.md` and every surface quoting a kill rate carry the literal string
**`SAME-AUTHOR — a weaker instrument`**, and that G-EVAL is recorded as `PASSED — NOT INDEPENDENT`.

`02` §Y already writes the rule (*"there is no third option and no silent one"*). **This is the test that
makes the third option unreachable**, and it is the difference between an honest degradation and a green
gate.

---

### 10. `test_gate_denominators_cannot_shrink_to_make_a_gate_pass`

**Kills:** F8, F11, and the general form of M1 at the *gate* level.

Two assertions, both cheap:
- `ci/GATES.md` rows 1–13 are `LIVE` at P0; moving any to `PENDING` fails the build without an appended,
  dated argument. (`test_p0__pending_set_is_exactly_the_four_named_rows`.)
- `SURFACES`, `REQUIRED_NUMBERS` and `catalogue.yaml` are **append-only with growth logs**; a removal
  requires a dated argument, and each registry publishes its cardinality as a time series.
  (`test_surface__registry_is_append_only`, `test_nc_meta__catalogue_is_append_only`,
  `test_nc_meta__ids_are_unique`.)

Every gate in this plan whose form is `k of n` where we also write `n` is one refactor away from being
`n of n`. The plan mechanises this discipline beautifully for `docs/HARVEST-DELTA.md` and for
`docs/GATE-CHANGES.md`, and does not apply it to the denominators of its own gates.

---

## §4 — WHAT THIS PASS COULD NOT CHECK

Stated because the plan's own standard requires it, and because a residue-free adversary report is the
thing this project exists to refuse.

1. **I did not run anything.** Every finding is derived from reading `plan/00`–`07` and
   `spec/02-architecture.md` against each other. Findings F19, F13 and F14 are arithmetic arguments about
   specified behaviour and would be settled in minutes by the tests named; if any is wrong, the test is
   still worth having and will say so.
2. **I did not read `spec/00`, `01`, `03`, `04` or `05` in full.** Where a plan document cites the spec I
   took the citation at face value, except for `spec/02`, which I read. A contradiction between a plan
   document and an unread spec section is invisible to this pass.
3. **The catalogue-collision finding (F27) assumes the six documents are merged into one
   `catalogue.yaml`.** If a later decision partitions the catalogue per component, the collisions become
   harmless and F27 downgrades to MINOR — but nothing in `01` §2 suggests a partition, and the meta-tests
   are written over one file.
4. **Effort findings are judgment, not measurement.** They are stated as ranges and as *directions*, and
   the direction is the load-bearing part: P0, P3-B4 and P12-B1 are under-estimated, and all three are on
   or immediately adjacent to the critical path.
5. **The self-referential denominator applies here too.** These are 44 mechanisms *I* imagined, found by
   reading. A forty-fifth arriving by a mechanism nobody imagined is invisible to this pass by
   construction, and the only instrument against it is that this document is dated, is one pass, and should
   be re-run by someone else against the repaired plan. **Report the rate at which new mechanisms are
   found. Do not claim it converges.**
