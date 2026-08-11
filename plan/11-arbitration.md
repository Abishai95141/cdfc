# 11 — ARBITRATION RULING

**Compiled 11 Aug 2026, by the session owner, after the repair pass introduced eight cross-document
contradictions and multiplied the catalogue-id collisions.**

**Why this document exists, stated plainly because it is the lesson.** The repair was run as four owners
editing disjoint document sets in parallel. Disjoint *files* are not disjoint *contracts*: four owners
repairing one coupled model produced eight new divergences, two of them on pre-registered constants, and
created two brand-new catalogue-id collisions inside the repair for catalogue-id collisions. **A coupled
specification admits exactly one writer at a time.** The plan's own P7 makes the same point about
predicates interacting; the process should have obeyed the design.

Every ruling below is binding. Where a ruling takes one side, the losing text is deleted, not softened.
Where a ruling takes neither side, it says so and gives the third thing.

---

## C1 — F3's pre-registered deviation threshold `d` · **RULED: neither. `d` is a frozen integer.**

> `02` L2754: `d = max(3, ceil(0.05 × |non-trivial|))` ≈ 11 · `05` L2676: `d = 25`

**Ruling.** `d = 11`, **an integer**, frozen in `experiments/G-EVAL/PREREGISTRATION.md` together with (a)
the formula `max(3, ceil(0.05 × |non-trivial|))` that produced it, (b) the corpus content hash it was
evaluated against, and (c) the date. `05`'s bare `25` is deleted; it has no stated basis anywhere.

**Why the formula does not survive as a formula.** A threshold that recomputes from the corpus it is
applied to *moves when the data moves* — which is F1's defect in another costume: the gate's strictness
becomes a function of the thing being gated, and no one sees it change. `02`'s derivation is the better
one and it is retained as the *derivation*; what is pre-registered is the number it produced.

**Consequence.** If the corpus changes, `d` does not silently follow. A new pre-registration is written,
with a recorded reason, and the old one is kept. The criterion may change only by an argument that the old
criterion was wrong.

---

## C2 — F9's disposition · **RULED: `04`'s branch, with `03`'s honesty requirement grafted on. This is strictly better than either.**

> `03`: `obligation_id` stays `None`, candidates take `SKIPPED_NOT_APPLICABLE` at G0
> `04`: mint `OBL-TEMPLATE-<sheet>-<ref>`, G0 runs for real, the skip branch rejected

**Ruling — three parts, all required.**

1. **Obligations get a `source` discriminator: `STATUTE | TEMPLATE`.** A harvested predicate implements a
   relation the *regulator's template* encodes, not a clause the *statute* states. Both are real
   obligations; they are not the same kind of thing, and collapsing them was what made this
   irreconcilable.
2. **`04` wins on mechanism.** Harvested candidates are minted `OBL-TEMPLATE-<sheet>-<ref>` with
   `source: TEMPLATE`, and **G0 runs for real** against the template relation: does this predicate
   faithfully implement the relation it claims to implement? That is a genuine, failable check, and
   `03`'s branch made G0 decorative for all 280 candidates — a gate stage that cannot fail is the
   product's own failure mode wearing a gate's clothes.
3. **`03` wins on disclosure.** The published figure becomes **two** numbers, never one:
   `predicates with a STATUTE obligation / 280` — **0 / 280 today** — and
   `predicates with a TEMPLATE obligation / 280` — **280 / 280 today**.

**What this fixes that neither branch did.** `07`'s published `0/280` was wrong by 280 under `04` and
misleading under `03`. Under this ruling both numbers are true, the honest statement survives verbatim —
*no harvested predicate yet implements a statutory clause* — and G0 stops being theatre.

---

## C3 — F13's retention mechanism · **RULED: `05`'s field, which `03` must read. The retention rule changes.**

> `03`: a new reason code `out_of_scope.precondition_degenerate` plus a `REMOVAL_BASIS` map
> `05`: a new field `scope_kind` on the existing reason code

**Ruling.** `05`'s `scope_kind` field is adopted, because a 31st reason code breaks a count pinned in four
places — the same category error already ruled on for the container guard, where run-level causes became
their own vocabulary rather than a 31st item-level code. `03` must **read** `scope_kind`; a field one
document writes and another ignores is not a repair, and that is precisely why F13's mechanism survived
its own fix.

**The retention rule, which is the actual repair:**

> **Only `scope_kind == DECLARED_CHARACTERISTIC` leaves the in-scope denominator.**
> `scope_kind == PREDICATE_PRECONDITION` **stays in the denominator** and is additionally flagged for G3
> re-qualification.

**Why.** A predicate whose `applicable` is degenerate is not telling you something about the filing. It is
telling you something about the predicate — and a degenerate precondition is exactly what G3 exists to
reject. Letting it remove a cell from the denominator lets a bad predicate shrink the thing it is measured
against. Under this rule the empty-filing attack closes: nothing a predicate does to itself can make the
settled fraction rise.

---

## C4 — P0's pre-registered gate set · **RULED: `02`.**

> `00`: "13 LIVE", `test_p0__pending_set_is_exactly_the_four_named_rows` · `02`: `LIVE = {1…13, 17, 18}`,
> `PENDING = {14, 15, 16}`, 15 of 18

**Ruling.** `02` owns P0 and its enumeration is explicit and closes arithmetically (15 + 3 = 18). `00`'s is
a summary that drifted from its source. `00` is corrected to **15 LIVE / 3 PENDING of 18**, and the test is
`02`'s `test_contract__live_set_is_pre_registered`. `00`'s
`test_p0__pending_set_is_exactly_the_four_named_rows` is **deleted**, not renamed — its name asserts a
count that is wrong.

---

## C5 — May `TEMPLATE-COMPUTED` be cited in a gate? · **RULED: `05`. It may not.**

**Ruling.** A `TEMPLATE-COMPUTED` corpus is generated by `src/cdfc/calc/`, the same function the arithmetic
predicates and the template differential re-check. Citing it in a gate is buying a gate pass from yourself,
which is F2 exactly. `TEMPLATE-COMPUTED` is a **smoke test only**: it may not be cited in a gate, in a
severity tier, or in any published rate. `03`'s exit criterion 1a is downgraded to a non-gating smoke check
and relabelled so nobody re-promotes it.

This is consistent with the corpus-provenance-to-severity table the verification pass called the
best-executed repair in the set, and it must not be allowed to disagree with it.

---

## C6 — the critical path · **RULED, THEN CORRECTED BY ITS OWN ARITHMETIC. The path is 127 working days.**

> **This ruling was wrong when first issued and is corrected here rather than quietly restated.** The
> original text is kept below so the correction is inspectable.

**The correction.** `02` §R11 does not merely disagree with `00` §7 — it **re-estimates two of the four
phases against their own build lists** and says so explicitly: *"`plan/00-decomposition.md` §7
pre-registered P0 4 · P1 8 · P2 10 · P3 12 = 34"*, revised to **P0 8 · P1 8 · P2 10 · P3 17 = 43**, with
the reason stated — *"the cheapest way to make a 7-day P3-B4 estimate come true is to skip arm 2, which is
the one thing in P3 that carries information."* A detail document that re-derives an estimate from the
build list it owns beats a summary figure pre-registered before that list existed.

**Ruling, final:**

1. **The critical-path row takes `02`'s revised figures**, and §7 now reads
   `8 · 8 · 10 · 17 · 14 · 12 · 10.5 · 16 · 9.5 · 6 · 16 = **127 working days**`. Applied.
2. **The total is the sum of the rows, always.** A displayed total that does not equal its parts is the
   shared-denominator error — the fifth silent false negative in this corpus, in a schedule. Add
   `test_plan__critical_path_total_equals_sum_of_rows` to the P0 gate set, parsing §7's row.
3. **`02` §R11's range travels with the point estimate**: P0 8–10, P3 15–20; the row takes the low end of
   each, so **127 is a floor, not a midpoint**, and must be quoted that way.
4. **NOT RE-DERIVED HERE, and named rather than silently patched:** the serial one-engineer total (stated
   170) and the `k = 0` re-routed path both depend on per-phase figures I have not individually verified
   against their detail documents. **They are stale by at least the same +9 and must be recomputed by
   whoever owns them before either is quoted.** Publishing a corrected number I have not computed would
   reproduce the defect this ruling exists to fix.

---

### The original ruling, superseded — kept for inspection

**RULED: `00`. ~118 working days.**

**Ruling.** `00` recomputed the path from `02`'s revised phase efforts (P0 = 8, P3 = 17). `05` and `06`
carry `~114`, the pre-revision figure, and `06` additionally instructs `00` to carry the stale number.
Arithmetic beats citation: **~118**, and `05` and `06` are corrected.

**Note for whoever reads this under pressure.** This is the `k = 0` branch — the one taken when the
settling experiment fails. A schedule that is wrong specifically in the branch you reach on bad news is the
worst place for a stale number, which is why this ranks above its size.

---

## C7 — the arm-2 author test name · **RULED: `test_arm_two_author_is_not_the_evaluator_author`.**

Carried by `00`, `01` and `05`, including `01`, which owns the test taxonomy. `02`'s
`test_arm_two_oracle_is_a_different_author` is renamed. One name, one test, no orphan guard.

---

## C8 — two naming splits · **RULED separately.**

**(a) The pre-registration test.** `test_contract__preregistration_criterion_is_machine_evaluable` wins,
per `01`'s naming convention: `test_contract__` is the taxonomy prefix for a property of a contract, and
this asserts a contract property. `test_e6__…` in `00` and `06` is renamed.

**(b) The documentation path.** `docs/EVALUATION-CONTRACT.md` is the single home of the evaluation
contract, including the `formula_source` rule, because `formula_source` is a rule of that contract.
**`docs/RECALCULATION-SOURCE.md` is deleted as a separate artifact**; `02`'s cross-reference is repointed.
Two files, one of which is generated from the other, is how the contract came to have two versions in the
first place.

---

## C9 (new) — THE CATALOGUE IDS · **RULED: one canonical registry, one writer, mechanical renumbering.**

The repair pass turned 5 colliding id-groups into 10 live duplicate definitions, created two new collisions
(`NC-Q45`, `NC-Q46`) inside the repair for collisions, produced four mutually inconsistent band tables, and
left eight orphan ranges. Band-conformance now fails for `04`, `05`, `06` and `07`.

**Ruling.**

1. **`01-validation-methodology.md` is the sole registry.** No other document may *define* an `NC-` id.
   Every other document *references* one. This is enforced by `test_nc_meta__ids_are_defined_in_the_registry`.
2. **One band table, in `01`.** The four competing tables are deleted and replaced by a single allocation,
   with a reserved unallocated range per band so a future document never needs to invent one.
3. **Renumber mechanically, never by judgement.** Where two documents define the same id with different
   content, both get **new** ids; neither keeps the contested one, and the contested id is **retired
   permanently** rather than reassigned. A retired id that later resolves to something is how a stale
   reference becomes a silent wrong reference.
4. **Publish the full old-to-new mapping** in `01`, and update every reference in every document in the
   same pass.
5. **Orphans are errors, not debris.** `test_nc_meta__no_orphan_guard` and
   `test_nc_meta__no_dangling_reference` both fail the build.

---

## WHAT THIS RULING DOES NOT SETTLE

- **F27** remains the one SERIOUS finding not closed. It stays open, named, with its owner.
- **F37 and F43** were closed with an explicit `OPEN — USER DECISION`. Those decisions are still the
  user's and are listed in the operating manual.
- The **`K` and `T` pervasiveness-policy constants** still render the literal string `PLACEHOLDER` and
  still have no argued basis anywhere in the corpus. That is correct and must not be quietly filled in.
