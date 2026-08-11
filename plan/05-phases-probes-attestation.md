# 05 — THE PROBE, SELF-CHECK AND ATTESTATION PHASES
## P9, P10 and P11, in full · build plan, part 5 · compiled 11 August 2026

**This document specifies P9, P10 and P11 and nothing else.** It uses the phase IDs, the build numbering,
the ordering, the gates and the effort figures of `plan/00-decomposition.md`, and it satisfies
`plan/01-validation-methodology.md` — whose test taxonomy (§1), negative-control catalogue (§2), mutation
regime (§3), Definition of Done (§4), CI pipeline (§5), fixture strategy (§6) and residue declaration (§7)
are referenced **by name** here and never restated. Where this document adds a catalogue entry it gives the
entry's full §2 shape; where it relies on an existing one it names the id and stops. Where it **corrects**
an existing entry it says so, gives the correction, and says what the old version would have proved.

**Why these three phases are written together.** They are the three layers that make a claim *about the
instrument* rather than about the filing, and they compose into exactly one sentence:

> L6 asks **what else is true of this artifact that no predicate asserted**; L6.5 asks **was the instrument
> alive on this artifact, and what can it provably never catch**; L7 asks **can a stranger re-derive every
> word of that, byte for byte, without us.**

Split any two of them and the third becomes decorative. A probe layer with no self-check inflates the
settled fraction with relations nobody proved were firing. A self-check with no attestation produces a
liveness proof that lives in a log file. An attestation over a run with no liveness proof is a signature
over an unfalsifiable claim — which is the artifact this project exists to refuse.

**P10 carries the design's boldest claim** — that the verdict is conditioned on a proof obtained from the
artifact under test, in the same execution, and withheld when that proof fails. §P10·L is therefore the
longest validation section in this plan, and it exists because that claim is the one a reviewer should
attack first.

---

## §0 — WHAT THIS DOCUMENT DECIDES, AND WHAT IT SURFACES, BEFORE ANY BUILD BEGINS

Seven details are under-determined, or determined inconsistently, across the binding documents. Four are
**DECIDED** here with the alternative each beat. Three are **SURFACED** — a defect in a binding document
that this document must not silently paper over. Two more are **OPEN** and are given a decision rule
instead of an invented answer (§5).

Measurements taken while writing this document are marked **MEASURED (11 Aug 2026)** and were produced
against
`/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx`
(`sha256 7d9a1960…`), which becomes `fixtures/prescribed/…` at P0-B2. **The four probe scripts are on disk
now**, so every figure below is re-runnable rather than remembered — methodology §4 line D4, applied to the
plan itself:

```
/Users/abishaikc/Gift/.venv/bin/python /Users/abishaikc/Gift/tools/probes/p9_precedents.py
    -> 957 of 3747, and the per-sheet split, with '3. Portfolio'!O4 = SUM(C4:N4) as its positive control
/Users/abishaikc/Gift/.venv/bin/python /Users/abishaikc/Gift/tools/probes/p9_unlocked_formulas.py
    -> 6757 cells / 505 formula / 3755 unlocked / 8 unlocked-and-formula / 3747 field surface
/Users/abishaikc/Gift/.venv/bin/python /Users/abishaikc/Gift/tools/probes/p9_fn_census.py
    -> the nine-function census and the single _xlfn.SINGLE cell
/Users/abishaikc/Gift/.venv/bin/python /Users/abishaikc/Gift/tools/probes/p9_d17_defect.py
    -> the D17 formula chain and the nine-member Dropdown!F3:F11 scheme-type vocabulary
```

P9-B1 moves them under `tools/probes/` inside the repository proper and pins their outputs as goldens; until
then they are the evidence for every MEASURED figure in §0.

---

### 0.1 What cell a `TEMPLATE_DIFF` finding settles — **DECIDED: its field-surface precedents**

**The problem, and it is fatal if it is met at implementation time rather than now.** The closure invariant
runs over the **field surface**, defined as *unlocked ∧ non-formula*. `TEMPLATE_DIFF` fires on a cell the
blank template declares to be a **formula** — which is, by that definition, **not in the field surface**.
So the design's flagship relation produces findings about cells that have no `run_cell` row, and there are
only two naive outcomes, both wrong:

- **(a)** the item is dropped, and predicate #1 settles nothing, ever — a flagship that silently contributes
  zero; or
- **(b)** the denominator is widened to `field_surface ∪ formula_cells` when the relation is admitted, which
  makes the denominator a function of the relation set. **That is NC-D02's mechanism arriving through a new
  door**: the numerator choosing its own denominator. Barrier 1 exists to make this impossible.

**MEASURED (11 Aug 2026), FME workbook:** 6,757 `<c>` elements · 505 formula-bearing cells · 3,755 unlocked
cells · **unlocked ∧ formula = 8** · **unlocked ∧ non-formula = 3,747**, reproducing the published field
surface and its per-sheet split exactly (Portfolio 1,698 · Investors 897 · PMS 480 · Introduction 371 ·
Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22 · Compliance Report 0 · Dropdown 0).
**497 of the 505 formula cells are locked.** The eight that are not are
`'4. Investors'!N5, N6, N7, N8, N14, N15, N16, N17`, every one of them a row total
(`SUM(C5:M5)` and its shared dependents; `SUM(C14:M14)` and its shared dependents), and every one carrying
a cached value.

**RULING.** A `TEMPLATE_DIFF` evaluation **binds the field-surface precedents of the formula cell** — the
cells the template's own formula reads that lie in the field surface — and its `witness` names the
overwritten formula cell. `cells_bound` is `|precedents ∩ field_surface|`. A template formula whose
precedent set does not intersect the field surface **binds zero cells** and is therefore refused at **G1**
with `cells_bound = 0`; it never reaches a run and never becomes an `ERROR` at run time.

*Reason.* The field surface is the set of cells **the filer may fill**, and the coverage claim is a claim
about those cells. Overwriting `'3. Portfolio'!O7` with a literal is a statement about the inputs `C7:N7`
— it asserts that their sum is something other than their sum. Attributing the finding to the inputs is
therefore not a workaround; it is what the finding *means*. It also keeps the denominator a pure function
of `styles.xml`, which is the property `test_nc__D02a_denominator_provenance` asserts.

*Alternative it beat:* widening the denominator to 4,252 (`3,747 + 505`). Rejected on three grounds: it
moves the published denominator without a parser reason; it makes the denominator relation-set-dependent;
and it would put cells the filer cannot edit into a coverage claim about what the filer filed.

**The consequence, MEASURED, and it is this build's headline number before a line is written.** Resolving
every one of the 505 formulas — including row-shifting all 211 shared dependents, with
`'3. Portfolio'!O4 → SUM(C4:N4)` as the positive control the spec names — and intersecting their referenced
ranges with the field surface:

> **957 of the 3,747 field-surface cells (25.5%) feed at least one formula the template declares.**
> Portfolio 400 · Investors 368 · PMS 104 · Introduction 64 · Summary 20 · Compliance Status 1 ·
> Complaints 0 · AML-CFT 0. **MEASURED, 11 Aug 2026, `tools/probes/p9_precedents.py`.**

Two things follow, and both are load-bearing for P9 and P10 respectively:

1. **957 is `TEMPLATE_DIFF`'s ceiling.** Not its yield — its ceiling. Any claim that predicate #1 covers
   more than 957 cells is arithmetically impossible, and P9-B1 publishes the ceiling *before* it publishes
   the delta, so the delta cannot be read as unbounded.
2. **2,790 field-surface cells feed no template formula at all.** They participate in no arithmetic relation
   the regulator encoded. Every recompute, carry and sum-identity predicate is structurally blind to them,
   and only bound, membership and date predicates can reach them. **This is a second, independent,
   *measured* structural argument that the residue set is non-empty** — one that does not depend on the
   coordinated-misstatement construction at all. P10-B4 exhibits from both families.

---

### 0.2 The `kill_case` is a replayable **witness**, not a stored workbook — **DECIDED**

**The inconsistency.** `spec/02-architecture.md` §II.4.1 stores
`liveness: {kill_case: "mutants/P-0041-kill.xlsx", pass_case: "clean/blind_fill_017.xlsx"}` — file paths.
`spec/02-architecture.md` §II.6.2's own pseudo-code does something a file cannot do:
`mutant = p.liveness.kill_case.apply(filing.facts)` — *apply this kill case to **this** filing's facts.*
A stored `.xlsx` is a mutant **of the corpus filing that was on disk at admission time**. Transplanting its
cell values into a different filing's fact table produces a fault that is either meaningless or, worse,
accidentally consistent with the filing under test.

**RULING — the witness is stored twice, and the two copies do different jobs.**

```python
# src/cdfc/selfcheck/witness.py
@dataclass(frozen=True, slots=True)
class FaultWitness:
    operator:   str            # a member of the versioned fault model, e.g. "zero_out", "off_by_one"
    target:     StableKey      # a key in the induced schema — NEVER a coordinate
    params:     Mapping[str, int]   # integer only. MILLI_USD_MILLION or a count. No floats.
    fault_class: str           # "F11", "F2", … — MUST be a member of the predicate's DECLARED
                               # claims_fault_classes. It is not a post-hoc label. See below.
    fault_model_version: str   # "v3"
```

**CONTRACT CHANGE, forced by the adversary pass (F1), and it is recorded here because this document owns
the field the defect hides in.** The gloss *"the class the predicate CLAIMS to cover"* was, as written, a
label **stamped at admission on mutants that had already died** — so a predicate that kills one class and is
structurally blind to thirteen scores `1.00` on a denominator it selected after the campaign. That is
NC-D02's mechanism arriving at the gate built to catch it.

> **The claim moves out of the witness and into the envelope.** `Candidate` / `Predicate` gains
> `claims_fault_classes: tuple[str, ...]` — **required, non-empty, inside `envelope_projection()` and
> therefore inside `code_sha256`**, so narrowing the claim after a campaign produces a *different predicate*.
> `qualify/g2_kill.py` computes the registry bar over **that declared set only** and **raises** when any
> claimed class has `O == 0` on this campaign. The envelope field and the `g2_kill` arithmetic are owned by
> `plan/03` P4-B1 and `plan/04` P7-B3; **this document's obligation is the consumer-side one and it is
> mechanised here**: `FaultWitness.__post_init__` raises `UndeclaredFaultClass` when
> `fault_class not in predicate.claims_fault_classes`, asserted by
> `tests/unit/test_witness.py::test_w__fault_class_is_a_declared_claim_not_a_post_hoc_label`.
> **Consequence for §0.3's diversity rule:** `MAX_WITNESSES` witnesses are chosen to be maximally diverse
> **within the declared claimed set**, never across classes the predicate never claimed — a witness set
> broader than the claim would make the canary loop attest to coverage the registry bar never measured.

- The **`FaultWitness`** — an operator, a stable key and integer parameters — is what **F10 replays at run
  time**, against the in-memory fact table of the filing under test. It is applicable to any filing that
  binds the same template because its target is a *key*, not a coordinate, and its effect is a
  *transformation*, not a value.
- The **content-addressed `.xlsx`** that actually killed the predicate at G2 is retained as
  `qualification.liveness.kill_case.artifact_sha256`, together with
  `admitted_against_filing_sha256`. It is what makes the **admission** auditable and re-runnable. **It never
  enters a run.** `test_nc__C05c_no_artifact_is_opened_during_the_canary_loop` asserts it.

So the stored block becomes:

```yaml
liveness:
  kill_cases:                       # ORDERED. See 0.3 for why it is a set and not one.
    - witness: {operator: zero_out, target: "portfolio.tbl31.row[7].total_value",
                params: {}, fault_class: F11, fault_model_version: v3}
      artifact_sha256: "sha256:…"
      admitted_against_filing_sha256: "sha256:…"
  pass_case:
    artifact_sha256: "sha256:…"     # a clean corpus member; see 0.4
    facts_sha256:    "sha256:…"     # the derived fact table, cached and rebuildable from the artifact
```

*Alternative it beat:* keeping the artifact as the run-time object and diffing it against the filing.
Rejected because it makes the canary loop open a second workbook per predicate — at openpyxl's **measured
202 ms** load that is 280 × 202 ms ≈ 57 s against a ~30 ms pipeline, which would not merely be slow: it
would be the reason someone later disables the canary loop, and a self-check that gets disabled under time
pressure is not a self-check. The `FaultWitness` path is arithmetic on an in-memory table and hits the
methodology's `PERF-CANARY` budget with room to spare.

---

### 0.3 A witness may be **inapplicable on this filing**, and that is not a silent canary — **DECIDED**

The spec's mechanism assumes every stored kill case can fire on every filing. It cannot. `zero_out` on a
cell that is already zero changes nothing; `off_by_one` on a blank count changes nothing. **A fault that
produces no observable change cannot test anything** — this is exactly `U`, the unobservable mutant, which
G2 already measures by recalculation. Three naive dispositions and why each is wrong:

| Disposition | Why it fails |
|---|---|
| Treat as **silent ⇒ INVALID** | A sparsely-filled but perfectly lawful filing would make almost every run `INVALID`. That converts *a finding about the filing* into *a finding about us*, inverting the exact distinction §II.3.2 draws between `INVALID` and `SETTLEMENT_INSUFFICIENT` |
| Treat as **passed** | The vacuous pass, one level up: liveness asserted from an execution that proved nothing. This is the failure the whole layer exists to catch, committed by the catcher |
| Emit a **31st reason code** | The vocabulary is frozen at 8 × 30 (spec G4). A phase that grows it has re-opened a decided question to make its own life easier |

**RULING, in three parts.**

1. **A predicate is admitted with an ordered witness *set*, not a single witness.** `MAX_WITNESSES = 3`,
   chosen at admission by `qualify/g2_kill.py` to be maximally diverse in **fault class** — because three
   witnesses of the same class fail together for the same reason and buy nothing.
2. **Applicability is decided by recalculation, exactly as `O = G − U` is decided at G2.** Apply the
   witness to a copy of the fact table, run P3's evaluator over the affected cells, diff the value grid.
   The first witness whose grid differs is *the* canary for this predicate on this run.
   - it **fires** (predicate returns `FAIL`) ⇒ live;
   - it is observable and **does not fire** ⇒ **silent canary ⇒ `run_state = INVALID`**,
     `invalid.canary_silent`, and the predicate is named.

   **Observability is THREE-VALUED here, not two, and the reason is the adversary pass's F18.** A cell the
   evaluator could not compute — an unimplemented function, a cycle, an excluded engine-disagreement cell —
   sits in `ValueGrid.not_run` and is **identical in both grids by construction**. Two-valued classification
   silently converts *"our evaluator cannot see this"* into *"this fault is invisible"*, which is a property
   of our apparatus wearing the label of a property of the fault. So:
   `Observability = Literal["OBSERVABLE", "UNOBSERVABLE", "INDETERMINATE"]`, where **`INDETERMINATE` means
   the recalculation touched a `not_run` cell**. An `INDETERMINATE` witness is **not** treated as
   unobservable and is **not** treated as a pass: it is its own counted population, it counts toward the
   §0.3 ceiling exactly as `inapplicable` does, and the run-level report carries
   `canariesIndeterminate` beside `canariesInapplicable` with the offending cells named.
   `tests/unit/test_witness.py::test_w__notrun_cell_yields_INDETERMINATE_not_UNOBSERVABLE`, injector
   `injectors/notrun_counts_as_identical.py`; admission-side twin: a witness propagating only through
   fully-evaluable cells is `OBSERVABLE`.
3. **If no stored witness is observable on this filing, liveness is not demonstrated, and the predicate
   settles nothing.** Its `run_check` row is written with its evaluated state, its `evaluations[]` vector is
   preserved on every cell it read (nothing is lost), **and each of those cells takes state
   `NOT_RUN(not_run.deactivated)`** with a pointer to the run's generated, content-addressed
   `canary_inapplicable[]` block. The run stays **`VALID`**. **The settled fraction falls.**

*Why `.deactivated` and not a new code.* Its definition is *"an admitted predicate deliberately switched off
for this run, with a pointer to the decision record — skipping is sometimes legitimate, and the moment it is
legitimate the report must be able to say so, or the skip becomes silent."* Ours is a **machine** decision
with a **machine-generated, hashed** decision record, which satisfies every clause of that definition except
the word *deliberately*. **This is a widening of the code's gloss, not of the vocabulary**, and it is
recorded as such: `docs/EVALUATION-CONTRACT.md`'s generator gains one sentence, `test_contract__thirty_reason_codes`
is unchanged, and `docs/REASON-GLOSS-CHANGES.md` records the widening with its date and its argument.
**If the owner prefers, the alternative is a `no_predicate.not_yet_requalified` disposition — rejected here
because that code says the predicate's identity changed, and it did not: the *filing* is the reason.**

**The escape-hatch guard, because this ruling creates one.** A break that made *every* witness unobservable
would now produce a `VALID` run with a collapsed settled fraction instead of an `INVALID` one.
`selfcheck/canary.py` therefore carries a run-level rule with a pre-registered threshold:

```
if (inapplicable + indeterminate) / canaries_attempted > CANARY_INAPPLICABLE_CEILING:   # = 0.25, pre-registered
    run_state = INVALID  with invalid.canary_silent
                and canary_failure_kind = WHOLESALE_INAPPLICABILITY
```

**`indeterminate` is inside that numerator deliberately.** A build whose evaluator quietly stopped computing
would otherwise present as a run full of *inapplicable* witnesses — a finding about the filing — when it is a
finding about us. The two are still reported as separate integers; they are pooled only for the ceiling, and
`tests/unit/test_thresholds.py::test_th__indeterminate_counts_toward_the_ceiling` pins that.

*Reason for 0.25 and not a higher number:* on the reference template-computed clean filing the measured
inapplicable count must be **0**, because the witness set was chosen from mutants that were observable on a
filing of the same template. Any non-trivial inapplicable population is therefore evidence about *us*, not
about the filing, until a corpus says otherwise.

**The narrow warrant under which `TEMPLATE-COMPUTED` may be used at all, restated here because the adversary
pass (F2) showed the corpus is generated by `src/cdfc/calc/` — the very evaluator the arithmetic predicates
re-check.** A `TEMPLATE-COMPUTED` filing is admissible as an **apparatus calibration surface** — witness
applicability, canary cost, `MAX_WITNESSES` (§5.1) — because those measurements are about the *evaluator's*
behaviour and the circularity is therefore the subject rather than a contaminant. It is **inadmissible as
the corpus behind any false-failure rate for a predicate whose read set intersects the cells the generator
computed** (`g4_ffr.check()` raises `UninformativeCorpusError`, `plan/04` P8-B3). Every use of a
template-computed filing in this document is labelled with which of the two it is, and
`docs/measurements/P10-canary-cost.md` carries the sentence *"calibration surface, not an FFR corpus"* on its
face. The threshold is pre-registered in
`selfcheck/thresholds.py` **before** the first run and may be moved only by an argument that the old value
was wrong, with a dated entry in `docs/SELFCHECK-THRESHOLDS.md` — the same rule the project applies to
`severity_tier` and to E6.

---

### 0.4 The `pass_case` is replayed too, and it proves a different thing — **DECIDED**

Spec §III.3.1 F10 replays only the kill case. Replaying only the kill case leaves one drift undetected and
it is the drift SPADE's own paper documents as the terminal state of an unguarded registry: **a predicate
that has drifted to flagging everything passes every kill-case canary, perfectly, forever.**

**RULING: F10 replays both, and the two claims are stated separately and never merged.**

| Replay | Runs against | Proves | Does **not** prove |
|---|---|---|---|
| **`kill_case` witness** | **this filing's** in-memory fact table | the predicate still binds cells in *this* artifact and still turns the fault it was admitted for into a `FAIL` | that the fact table is *this filing* (§4.1) |
| **`pass_case`** | a **pinned clean corpus member's** cached fact table | the predicate has not drifted to always-flag | anything about this filing |

The `pass_case` fact tables are content-addressed, built once, cached at `blobs/facts/<sha256>`, and
**rebuildable from the pinned artifact**, so no ninth entry joins the manifest's eight pins: the pass-case
artifacts are already pinned transitively through `registry_root`, and
`tests/determinism/test_det__pass_case_facts_rebuild_identically` asserts the cache is a cache and not an
input. The attestation reports the two counts separately —
`livenessProof{canariesRun, canariesPassed, antiCanariesRun, antiCanariesPassed, selfTestSilent}` —
because a single merged count would let a kill-case failure hide behind an anti-canary success.

Cost, DERIVED from the measured 7,946 fact-table mutations/s: 280 kill cases ≈ 35 ms, 280 anti-canaries
against cached fact tables ≈ 35 ms, **≈ 70 ms total against a ~30 ms baseline**. `PERF-CANARY` (baseline
~35 ms, fail above 80 ms) is superseded by `PERF-CANARY2` (baseline ~70 ms, fail above 160 ms, warn above
110 ms), appended to `perf/BUDGET-CHANGES.md` with this argument. **There is still no reason not to.**

---

### 0.5 **SURFACED** — the plan's headline canary control, as written, tests the wrong layer

`plan/01-validation-methodology.md` §2.5 NC-C01a and `plan/00-decomposition.md` P10 both use the same
fixture: **rename a sheet** (`fixtures/synthetic/renamed-sheet__portfolio.xlsx`, or `cdfc demo
--break-parser`) and assert `run_state == INVALID` with cause `error.canary_silent`.

**It will not reach the canary layer.** Template binding (F3, built in P5-B1) binds by **structural
fingerprint over `(sheet names + states, dimensions, merged-range set, defined-name list, unlocked mask)`**.
A renamed sheet changes the fingerprint. The run terminates at F3 with
**`invalid.template_unbound`** — five steps before F10 executes.

The consequence is precisely the failure mode this project is built to refuse: **the canary layer would be
credited, in CI and on stage, with a catch made by the template binder.** A green suite; a true `INVALID`;
an untested claim.

**CORRECTION, and it splits the control into three.** Recorded in `docs/CATALOGUE-CORRECTIONS.md` with this
argument; the superseded assertion keeps its row per `test_nc_meta__catalogue_growth_is_logged`.

**A correction that does not propagate is a second version of the same defect, and the adversary pass (F25)
found this one still live in two binding documents.** Correcting the mechanism *here* while
`plan/01-validation-methodology.md` §1.10, `plan/01` §2.5 NC-C01a and `plan/00-decomposition.md` P10 still
assert *"`cdfc demo --break-parser` (renames a sheet) → `INVALID`, **dead predicates named**"* leaves CI
reading an assertion that is **unsatisfiable**: a `template_unbound` run has no dead predicates to name,
because no predicate ran. **The amendments to those three sites are part of the same commit as this
document's correction, not a follow-up**, each with its `docs/CATALOGUE-CORRECTIONS.md` row. The mechanism
that makes this checkable rather than remembered is one grep and it is required at P0-B3:

> **`test_plan__no_binding_document_asserts_a_superseded_mechanism`** — for every row in
> `docs/CATALOGUE-CORRECTIONS.md`, the superseded assertion's distinguishing phrase must not appear in any
> file under `plan/` or `docs/` outside that row itself. It fails today on *"renames a sheet"* co-occurring
> with *"canary"*, and it must be observed red on that exact pair before it is allowed to go green.

| id | Break | Must produce | What it proves |
|---|---|---|---|
| **NC-C01** *(amended)* | the canary **loop** returns success unconditionally (`injectors/canaries_noop.py`) | `INVALID`, `canary_failure_kind = SELFTEST_NOT_SILENT` | the loop is not a stub |
| **NC-C03** *(new)* | a **renamed sheet** in the artifact | `INVALID(invalid.template_unbound)` — **and a test asserts the cause is NOT `canary_silent`** | the binder catches artifact drift, and the canary layer is not credited for it |
| **NC-C04** *(new)* | an **apparatus** break that leaves binding intact | `INVALID(invalid.canary_silent)`, dead predicates named | **the canary layer, and only the canary layer** |

**NC-C04's injectors matter more than its assertion**, so they are enumerated rather than described. Each
leaves the structural fingerprint untouched, so F3 binds, the readers agree, closure holds, and every other
guard in the system is silent:

- `injectors/keys_resolver_offbyone.py` — `schema/stable_keys.py` resolves each table row to the row below.
  Predicates still bind cells (`cells_bound > 0`), still evaluate, still return `PASS` on a clean filing.
  **Nothing else in the design notices.**
- `injectors/facts_trailing_space.py` — the fact table normalises a sheet-name key by stripping whitespace
  in one place and not another, so one predicate class binds an empty selection while `cells_bound` is
  computed from the *declared* keys rather than the *bound* cells. This is NC-Q01's mechanism hidden behind
  a correct-looking count.
- `injectors/celrt_short_circuits.py` — the CEL runtime returns `true` for any expression whose top-level
  operator is `&&` when the left operand is `true`, i.e. NC-E02's absorption promoted from the language to
  the runtime, *after* pre-flight has already passed.
- `injectors/tolerance_widened.py` — `τ(n) = 5n` becomes `τ(n) = 5000n`. Every arithmetic predicate still
  runs, still binds, still passes on clean data — and can no longer detect anything.

**Only `tolerance_widened` and `celrt_short_circuits` are catchable by any other layer** (mutation testing
of `facts/units.py`, and the CEL conformance run), and neither is caught *on the filing under test at run
time*, which is the whole claim. `test_liveness__only_cause_is_canary_silent` (§P10·L) asserts that under
each of the four injectors the run's `invalid` cause set is **exactly** `{canary_silent}` — because a
control that also trips `cells_bound_zero` proves nothing about canaries.

---

### 0.6 **SURFACED** — the FME workbook's function vocabulary is **nine**, not eight, and the ninth sits inside G-EVAL's own positive control

The spec fixes the evaluator's vocabulary at eight functions: `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`,
`ROW`, `ROWS`, `AGGREGATE(15,6,…)`. A census of all 505 materialised formulas
(`tools/probes/p9_fn_census.py`, **MEASURED 11 Aug 2026**) returns:

| Function | Cells |
|---|---:|
| `SUM` | 135 |
| `IFERROR` | 130 |
| `ROW` · `INDEX` · `_xlfn.AGGREGATE` · `ROWS` | 30 each |
| `IF` | 14 |
| `COUNTIF` | 3 |
| **`_xlfn.SINGLE`** | **1 — `'1. Introduction'!D92`** |

`_xlfn.SINGLE` is Excel's implicit-intersection operator. It appears exactly once, and **it appears inside
`'1. Introduction'!C92:E101` — the precise range spec §III.7 nominates as the positive control that must
pass before any kill rate may be quoted.** The cell is
`IFERROR(_xlfn.SINGLE(INDEX($D$54:$D$63, _xlfn.AGGREGATE(15,6,(ROW(...)-ROW($D$54)+1)/($N$54:$N$63="yes"), ROWS($D$92:D92)))), "NA")`.

**This is a P3 finding, reported here because it was measured while writing this document and because
P9-B1's entry criterion is G-EVAL.** It is not fixed here. The disposition rule is the spec's own: a
function outside the vocabulary makes its cells `NOT_RUN(not_run.source_unreadable)` and *a human decides*.
The decision this document records for the engineer is narrow and mechanical:

> **P3's vocabulary is nine functions, and `docs/measurements/P3-cached-value-reproduction.md` must state
> the census with its script. If `_xlfn.SINGLE` is not implemented, `'1. Introduction'!D92` is excluded from
> the observability filter's site set and from `TEMPLATE_DIFF`'s target set, and G-EVAL's threshold is
> restated as 504 of 504 with the exclusion named** — never as 505 of 505 with one cell quietly dropped.
> One excluded cell is 0.2% and costs nothing. **Excluding it silently would cost the positive control its
> meaning**, which is the whole reason the spec named that range.

The general lesson, which the engineer should carry into P9-B2's authoring review: **a vocabulary counted
by hand is an absence claim, and `src/cdfc/measure/absence.py::assert_absent` exists precisely so that this
class of claim cannot ship without a positive control.** The census is now that control, and it is a script.

---

### 0.7 **SURFACED** — the attestation carries floats, and byte-identity is hardest exactly there

`spec/02-architecture.md` §II.5.1's example payload carries `"rate": 0.021` and `"wilson": [0.006, 0.074]`.
`spec/03-stack.md` §4.5 states, normatively, *"There is no [floating point]. Money is `int64
MILLI_USD_MILLION`; tolerances are integers."* Both cannot hold in a signed payload, and the hardest part of
RFC 8785 canonicalisation — the one place two implementations most reliably diverge — is **number
serialisation of non-integers**.

**RULING: the normative statement wins over the illustrative example. No JSON number in the attestation
payload is anything other than an integer.** Rates are carried as their constituents plus a pre-rendered
string:

```jsonc
"ffr": { "fired": 2, "n": 96,
         "ratePpm": 20833, "wilsonLoPpm": 6000, "wilsonHiPpm": 74000,
         "display": "2 of 96 · 2.1% · [0.6%–7.4%]",
         "corpusId": "blind-fill-v2", "corpusProvenance": "BLIND-FILLED" }
```

`test_contract__no_json_float_in_the_payload` walks the canonicalised bytes and asserts no `.`, `e` or `E`
appears inside any JSON number token. *Alternative it beat:* keeping floats and pinning a JCS
implementation plus running the RFC's number test vectors. **Switch trigger, stated in advance:** if a
downstream consumer requires a float rate field, add it to a **projection** (which is already declared
lossy) and never to the normative payload.

---

## §0.8 — What these three phases do **not** touch

Named so that a reviewer can check for scope creep without reading the builds: no model client, no clause
graph, no corpus construction, no new reason code, no change to the eight item states or the eight
run-level `invalid.*` causes, no change to the published field surface, **no repair of any artifact**, and
no surface work beyond the two templates P10 owns and P14 renders (§P10·B1).

---
---

# P9 — L6: DIFFERENTIAL AND INVARIANT PROBES

**Effort: 12 engineer-days on the enumerated work** · B1 3 · B2 3 · B3 2 · B4 4 · **plus open scope**:
further relations at a measured ~0.35 engineer-days each under P9-B2 ruling (b), re-planned when the first
rate is measured. *(Was 14 with B2 at 5; B2's 5 days were an estimate over 18 unwritten rows — adversary
F42. The two days are not saved, they are moved into a lane that reports its own rate.)*
**Plus 2–3 person-days of a second person's calendar** for the relation-review signatures and **0.5
person-days** for the single `HAND-COMPUTED` clean filing F2's repair requires. **These are never added to
the engineer's total.**
*Assumption:* one competent engineer, ~6 productive hours/day, fluent in Python and raw OOXML, willing to
read the regulator's guidance notes closely enough to author a relation and then argue it down. No context
switching. **B2 is the largest build in the phase and it is mostly reading, not typing** — that is the
correct shape, and an engineer who finds B2 fast has probably authored relations the way the design
explicitly forbids.

## P9 · What it settles

**Whether the growth story is real — and whether the one check nothing else in the design can perform works
on the real artifact.**

Precisely, three sub-questions no earlier phase can answer:

1. **Does a formula-override survive every other check in the system?** Overwriting a formula cell with a
   literal deletes the inconsistency along with the formula. Every harvested predicate reads the *filed*
   values; the carry and sum identities are satisfied by construction, because the filer's literal is what
   the carry now carries. **Only a comparison against the pinned blank detects it**, and P9-B1 is that
   comparison.
2. **Can a relation be authored honestly, at scale, by a human, and then survive its own gate?** An earlier
   version of this design produced five relations of which **four false-alarm on a correct filing and the
   fifth is vacuous**. The failure mode is authoring, not execution, and B2's review protocol is the
   response.
3. **How much does the layer actually move?** The ceiling is stated in advance and published *with* the
   delta: this layer moves **≈ 0 of the 7** properties that are not settleable from the artifact at all.
   A relation that moves nothing is reported as moving nothing.

## P9 · Entry criteria

| Build | Requires | Why the edge is real |
|---|---|---|
| **B1** *(spike)* | **P5 complete** and **P3's G-EVAL evaluated** | `TEMPLATE_DIFF` *is* the evaluator pointed at a second input. Without a verified evaluator, a mismatch cannot be attributed to the filing rather than to us — the differential has no direction |
| **B1** *(spike)* | **G-EVAL's arm-2 independence status is RECORDED** in `docs/measurements/P3-evaluator.md` as either `INDEPENDENT` or the literal `SAME-AUTHOR — a weaker instrument`, and `ci/GATES.md` records G-EVAL as `PASSED` or `PASSED — NOT INDEPENDENT` accordingly. `test_arm_two_author_is_not_the_evaluator_author` green | **F3.** `TEMPLATE_DIFF`'s oracle *is* the evaluator. A same-author expectation file agreeing with a same-author evaluator is a self-check, and every number P9, P10 and P11 publish inherits it. **An unlabelled G-EVAL is not an entry condition that has been met; it is one that has not been evaluated** |
| **B1** *(spike)* | **`docs/EVALUATION-CONTRACT.md` publishes the `formula_source` rule** and `test_f11_mutant_is_observable` is green | **F19.** Two phases mean different things by "recalculate" and both pass in isolation. Entering B1 without the contract is entering it with the flagship provably unadmittable at G2 (see the ruling below) |
| **B1** *(spike)* | `docs/measurements/P3-cached-value-reproduction.md` published, **including the §0.6 census and any excluded cell** | A relation whose oracle contains an unimplemented function has an undeclared blind spot inside its own oracle |
| **B1** *(spike)* | `test_unqualified_relation_cannot_settle_a_cell` **written and green before the spike's first output is shown to anyone** | Conflict 2 authorises the pull-forward *on condition* that its non-admitted status is enforced by a test rather than by an intention |
| **B2, B3, B4** | **P7 complete** — the five gates, the registry, the `rejection` table | A relation is not self-validating. A violated relation means *the artifact is wrong* **or** *our relation is wrong*, and only the gate distinguishes them |
| **B4** | **P6 complete** — the fault-seeding harness and the observability filter | G2 for a relation needs targeted mutants and an `O` |
| **B2** (prior-period relations only) | **nothing** — and that is the finding | We hold **zero** real filed FME returns. The three prior-period relations and the one multi-instance relation are structurally un-runnable today and must report as such rather than be omitted |

**Not required, deliberately:** P8, P10, P11, P12. B1's spike output is a **demonstration** and says so in
its own rendered string.

## P9 · Builds

---

### BUILD P9-B1 — `TEMPLATE_DIFF`, THE FORMULA-OVERRIDE DIFFERENTIAL · 3 days · *spike-eligible after P5*

**What it produces.** One relation — **predicate #1** — and the two things that make it meaningful: a
**precedent map** from every template formula to its field-surface inputs, and a **ceiling** published
before any delta.

#### Files created

```
src/cdfc/probes/__init__.py
src/cdfc/probes/precedents.py        the template formula → field-surface precedent map
src/cdfc/probes/template_diff.py     the relation
src/cdfc/probes/degree.py            the degree map: money = 1; counts, dates, ratios, categoricals = 0
src/cdfc/probes/template_defects.yaml   per-template known defects in the ORACLE itself (see below)
tools/probes/p9_precedents.py        the re-runnable form of §0.1's measurement
tools/probes/p9_fn_census.py         the re-runnable form of §0.6's measurement
tools/probes/p9_unlocked_formulas.py the re-runnable form of §0.1's 8-cell finding
fixtures/synthetic/formula-overwritten__portfolio-O7.xlsx
fixtures/synthetic/formula-overwritten__investors-N5.xlsx
fixtures/synthetic/formula-overwritten__pair-portfolio-O7-summary.xlsx
docs/measurements/P9-template-diff-ceiling.md
```

#### Public interface, verbatim

```python
# src/cdfc/probes/precedents.py

@dataclass(frozen=True, slots=True)
class PrecedentMap:
    template_sha256: str
    by_formula_cell: Mapping[StableKey, frozenset[StableKey]]   # ALL precedents
    in_field_surface: Mapping[StableKey, frozenset[StableKey]]  # ∩ field surface — what binds
    unreachable: frozenset[StableKey]     # formula cells whose precedents miss the field surface entirely

def build_precedent_map(schema: TemplateSchema) -> PrecedentMap: ...
    # Materialises every shared dependent by row-shifting its master BEFORE resolving references.
    # A dependent resolved from unshifted master text is the NC-P02 defect wearing a new hat.

def ceiling(pm: PrecedentMap) -> tuple[int, int]:  ...
    # returns (|union of in_field_surface values|, |field_surface|)  ->  (957, 3747) on FME
```

```python
# src/cdfc/probes/template_diff.py

@dataclass(frozen=True, slots=True)
class DiffFinding:
    formula_cell: StableKey
    filed_value:  int | str | None      # int64 MILLI_USD_MILLION, a count, or a string
    recomputed:   int | str | None
    tau:          int                   # 5·n for degree-1 cells; 0 for counts, dates, categoricals
    bound_cells:  frozenset[StableKey]  # == pm.in_field_surface[formula_cell]

def template_diff(filing: FactTable, template: TemplateSchema, pm: PrecedentMap,
                  defects: TemplateDefectTable) -> list[DiffFinding]: ...

ScopeKind = Literal["IN_SCOPE", "DECLARED_CHARACTERISTIC", "PREDICATE_PRECONDITION"]   # C3 vocabulary

def applicable(filing: FactTable, formula_cell: StableKey, pm: PrecedentMap) -> ScopeKind: ...
    # THE NON-DEGENERACY PRECONDITION: at least one field-surface precedent is non-empty.
    # Not a bool.
    #   DECLARED_CHARACTERISTIC -> no field-surface precedent EXISTS: a fact about the pinned TEMPLATE or
    #                              about a declared filer/period attribute.  A claim about the INSTRUMENT.
    #                              (This member was called STRUCTURAL before arbitration C3.)
    #   PREDICATE_PRECONDITION  -> precedents exist and THIS FILING left them empty, so THIS PREDICATE's
    #                              own precondition is degenerate here.  A claim about the PREDICATE.
    #                              (This member was called DEGENERATE_INPUT before arbitration C3.)
    # Both emit OUT_OF_SCOPE(out_of_scope.not_applicable), never PASS.  They differ ONLY in the
    # denominator, and that difference is the whole of the F13 repair below.
    # NO NEW REASON CODE.  The item-level vocabulary stays at 30.
```

#### The relation, stated exactly

For every cell `c` the **pinned blank** declares to be a formula:

1. **Applicability.** If no field-surface precedent of `c` carries a value, return
   `OUT_OF_SCOPE(out_of_scope.not_applicable)` with `scope_kind = PREDICATE_PRECONDITION` (or
   `DECLARED_CHARACTERISTIC` when `c` has no field-surface precedent at all — the two are not the same
   claim, see the ruling below).
   **This is not optional and it is not cosmetic.** The blank's
   own cached grid is essentially zeros and `"NA"` strings — `'1. Introduction'!D17`, `D18`, `D19`, `D20`
   all cache `0`; `C92`, `D92`, `E92` all cache `"NA"` (**MEASURED**). Without the precondition, an unfilled
   or sparsely-filled filing scores a clean sweep through the flagship's door, which is NC-R01 and which is
   the same defect the all-zero partition case has.
2. **Recompute** `c`'s template formula over the **filed** inputs using P3's evaluator, called explicitly as
   `recalculate(schema, facts, formula_source="TEMPLATE")`. The argument is not a default and is not
   optional — see the contract ruling below.
3. **Compare** under `τ`: `τ(n) = 5n` units of `MILLI_USD_MILLION` where the cell's degree is 1 and `n` is
   the number of summands; **`τ = 0` for counts, dates, ratios and categoricals.** `'1. Introduction'!D17`
   is `SUM(D18:D20)` over three COUNTIF-bearing rows — **a count, therefore zero tolerance.** A person, and
   a scheme, is not a rounded quantity.
4. **On mismatch**, emit `FAIL` bound to `pm.in_field_surface[c]`, with `witness = [c]` and both values.
5. **`method = TEMPLATE_DIFF`**, `warrant = DETERMINISTIC`, `provenance = COMPUTED`.

#### The settled fraction must not rise as the filing empties — **DECIDED** (adversary F13, FATAL)

**The mechanism, and it is this document's own defence turned against it.** NC-R01 is right that a partition
relation or a `TEMPLATE_DIFF` on an all-zero filing must return `OUT_OF_SCOPE` and never `PASS`. But
`OUT_OF_SCOPE` is **removed from `inScope`** (spec §II.3.3, `inScope = cellsTotal − outOfScope −
informational`), and `inScope` is the settled fraction's **denominator**. So the defence against the empty
filing is a mechanism that *shrinks the denominator*: take a filing, delete values, and every cell whose only
binding evaluation was a precondition-guarded relation leaves `inScope`, while cells still settled by
membership and bound predicates stay. `fraction = settled / inScope` **rises**. There exists a sparse-but-
lawful filing — exactly the shape §0.3 built `CANARY_INAPPLICABLE_CEILING` for — **on which a filer who
fills in less gets a better settled fraction.** The plan has
`test_prop__settled_is_monotone_non_increasing_in_not_run` for one state transition and nothing for the
fraction's direction, which is the property the product's headline claim actually needs.

> **RULING, in two parts, and the second is not optional because the adversary's point is that doing
> *neither* silently is the failure.**
>
> **(1) THE RETENTION RULE (arbitration C3), and it is binding on `plan/03` as well as on this document:**
>
> > **Only `scope_kind == DECLARED_CHARACTERISTIC` leaves the in-scope denominator.**
> > **`scope_kind == PREDICATE_PRECONDITION` stays in the denominator** and is **additionally flagged for
> > G3 re-qualification.**
>
> So `inScope = cellsTotal − outOfScope[DECLARED_CHARACTERISTIC] − informational`. A cell that is out of
> scope *because this filer left its inputs empty* is a statement about **the predicate**, not about the
> filing — and a degenerate precondition is exactly what G3 exists to reject, so it does not merely stay
> counted, **it accuses the predicate that produced it**. A coverage denominator that shrinks when the
> filing carries less information is measuring the filer, not us. A cell that is out of scope *because no
> relation over this template could ever reach it* is a statement about **the instrument**, and that one
> legitimately leaves.
> **This changes no reason code and grows no vocabulary** — `out_of_scope.not_applicable` is unchanged and
> `test_contract__thirty_reason_codes` is untouched. **`plan/03`'s competing repair — a 31st reason code,
> `out_of_scope.precondition_degenerate` — is retired by C3**, because a 31st code breaks a count pinned in
> four places, the same category error already ruled on for the container guard. What changes is one term of
> the denominator formula and one field, `scope_kind`, on the evaluation record. It is the §0.3 pattern
> applied a second time: a gloss widened with a dated argument, in `docs/REASON-GLOSS-CHANGES.md`, not a
> code invented.
>
> **(2) The fraction never renders without `cellsTotal` beside `inScope`.** The six counts the surface
> already carries gain a seventh, so a denominator that moved for *any* reason is visible on the same line
> as the number it produced. `tests/contract/test_contract__fraction_renders_its_denominator_provenance`.

**The test that makes it a property rather than an intention, and it is §3 rank 3 of the adversary pass:**

> **`tests/property/test_prop_settled.py::test_prop__fraction_does_not_rise_as_the_filing_empties`** — for
> every filing `F` and every value-deletion transform `d`, `fraction(d(F)) ≤ fraction(F)`. Generator: the
> value-deletion transforms over the FME reference fill that P9-B2 already specifies for precondition
> monotonicity, so it costs a generator we are writing anyway. Companion, same module:
> `test_defect_table_cannot_raise_the_settled_fraction` (F14, above).

**Cross-document consequence — and under C3 it is no longer merely stated, it is accepted at the other
end.** `scope_kind` is produced here and **consumed** by `P5-B4 settled_fraction.py` (`plan/03` P5-B3/B4,
which now imports it, reads it in `in_scope(state, reason, scope_kind)`, and proves it does so with
`test_contract__scope_kind_is_read_not_ignored`) and by spec §II.3.3's formula. **The contract is: the
evaluation record carries `scope_kind: IN_SCOPE | DECLARED_CHARACTERISTIC | PREDICATE_PRECONDITION`,
required whenever `state == OUT_OF_SCOPE` with `out_of_scope.not_applicable` — absent, it raises
`MissingScopeKindError` rather than defaulting either way; and `settled_fraction.compute()` subtracts only
`DECLARED_CHARACTERISTIC`, while `PREDICATE_PRECONDITION` is retained and sets the G3 re-qualification
flag.** A build of P5-B4 that subtracts all `OUT_OF_SCOPE` fails
`test_prop__fraction_does_not_rise_as_the_filing_empties`, which is where the two documents meet.

> **This is the seam F13's first repair died in, so it is written as a seam.** The previous pass had this
> document writing a field and `plan/03` keying retention on a *different* mechanism it never read; composed
> as written, a degenerate-input cell arrived at `in_scope()` as `(OUT_OF_SCOPE,
> out_of_scope.not_applicable)`, was found in `REMOVAL_BASIS`, and **left the denominator** — F13's exact
> mechanism, restored by the two repairs that close it. **One mechanism, one writer, one reader.**

*Alternative it beat:* leaving the denominator alone and relying on part (2) — rendering `cellsTotal` beside
`inScope` — to make the shrinkage visible. Rejected as the *primary* repair because it converts a wrong
number into a wrong number with a footnote, and the number is the product's headline; kept as the
*secondary* repair because a reader who cannot see the denominator cannot check the arithmetic at all.

#### The `formula_source` contract — **DECIDED**, and without it the flagship is unadmittable

**The defect, stated exactly, because it is the most expensive one the adversary pass found (F19) and it is
invisible in every phase taken alone.** `recalculate(schema: TemplateSchema, facts: FactTable)` (P3-B4)
takes the **schema**, and the schema is induced from the **pinned blank**, whose formula content is fixed.
The observability filter (P6-B3) classifies a mutant by comparing two *recalculated* grids. An **F11**
mutant is *"a cell the pinned blank declares a formula carries a literal"* — so recalculating it through the
template's formula graph **overwrites the literal with the formula's value**, the two grids are identical,
and the design's flagship fault class is classified `UNOBSERVABLE` **by construction**. Three consequences,
each of which passes its own phase's tests:

- **P6** reports an inflated `U/G` and satisfies *"an entry for each of F01–F14"* with `O = 0` for F11;
- **P7** cannot admit `TEMPLATE_DIFF` at all — `Campaign.kill_rate()` raises `CampaignArithmeticError` on
  `O == 0`, so **predicate #1 dies at the third gate with an exception**;
- **P9** is nevertheless green, because `template_diff` does not use the observability filter: it compares
  the *filed* value against the recomputed one. **P9 proves the thing P7 cannot admit.**

> **RULING.** `recalculate` takes an explicit, non-defaulted
> `formula_source: Literal["TEMPLATE", "FILING"]`, and the rule is published in
> `docs/EVALUATION-CONTRACT.md` in one place:
>
> | Caller | `formula_source` | Because |
> |---|---|---|
> | **observability / `classify()`** (P6-B3), and `selfcheck/witness.py::observability()` at run time | **`FILING`** — the filing's own `<f>` elements, materialised; a cell the filing carries as a literal **stays** a literal | observability is a question about *the artifact under test*. Recalculating a filing through the blank's formulas asks whether the fault survives a repair we performed on it, which is not the question |
> | **`TEMPLATE_DIFF`** (P9-B1) | **`TEMPLATE`** — the pinned blank's formula graph over the filed inputs | the relation *is* the comparison of the two sources. This is the only caller for which `TEMPLATE` is correct |
>
> A call site that omits the argument is a `TypeError`, not a default, so the two meanings can never again
> be reconciled by whichever phase was written second.

*Alternative it beat:* leaving `recalculate` single-meaning and excluding F11 from the fault model. Rejected
because it deletes the class the product is built around in order to protect a function signature, and
because the exclusion would be invisible in `U/G` — the shape the adversary pass calls *"the measurement
error correlated with the quantity being measured, in the direction that flatters us."*

**Three tests carry it, and two of them belong to other phases but are named here because this document is
where the defect is legible:**

| Test | Owner | Asserts |
|---|---|---|
| `tests/negative/test_nc_probes.py::test_f11_mutant_is_observable` | P9-B1 (this build) | seed `formula-overwritten__portfolio-O7`; `classify(clean, mutant) == OBSERVABLE`, and the **distinguishing-cell set is non-empty at the overwritten cell**. Injector `injectors/observability_uses_template_formulas.py` |
| `tests/relational/test_rel__template_diff.py::test_g2_admits_template_diff` | P9-B4 | the flagship reaches G2 with `O > 0` and a **computed** `K/O`, and `TEMPLATE_DIFF`'s per-class vector has `O > 0` for F11 |
| `tests/contract/test_contract__formula_source_is_explicit` | P9-B1 | every call site of `recalculate` under `src/cdfc/` passes the argument literally; an AST scan, not a grep, and a missing argument fails the build |

**Without `test_g2_admits_template_diff` nobody discovers this until P9-B4 — twelve weeks in — and the
symptom presents as an arithmetic exception in a gate rather than as a contract disagreement in an
evaluator.** That is why it is an *entry* criterion above and an exit criterion below.

#### `template_defects.yaml` — because the oracle is authoritative and **not correct**

`TEMPLATE_DIFF`'s oracle is the regulator's published blank. **The blank is wrong in at least one measured
place**, and a relation that recomputes a defective formula reproduces the defect — so a filer who filled
the return *correctly* would be flagged, and a filer who reproduced the defect would pass. The measured
instance, first-hand today:

```
'1. Introduction'!D17 = SUM(D18:D20)                                    cached 0
  D18 = COUNTIF(G54:G63,"*Angel*") + COUNTIF(G54:G63,"*Venture*")       cached 0
  D19 = COUNTIF(G54:G63, "*Restricted*")                                cached 0
  D20 = COUNTIF(G54:G63,"*Retail*") + COUNTIF(G54:G63,"*Exchange Traded Fund*")   cached 0
```

and the scheme-type vocabulary the workbook's own validation offers, `Dropdown!F3:F11`, has **nine** members:
*Venture Capital Scheme · Angel Scheme · Restricted Scheme (Category I) · Restricted Scheme (Category II) ·
Restricted Scheme (Category III) · Retail Scheme · Exchange Traded Fund · Special Situation Fund · Family
Investment Fund.* The four COUNTIF patterns match **seven of nine**. **`Special Situation Fund` and `Family
Investment Fund` match none of them**, so `D17` — *"Total No. of Schemes of the FME authorised by IFSCA"* —
under-counts by exactly the number of such schemes declared. **MEASURED, 11 Aug 2026, first-hand.**

**RULING.** A cell listed in `template_defects.yaml` for this `template_sha256` emits
**`INFORMATIONAL`**, never `FAIL`, carrying the defect's description and both values. `INFORMATIONAL` is
**removed from the settled denominator** (§II.3.3), so a template defect can never fail a filer. Each entry
requires `{cell, template_sha256, description, evidence_command, declared_by, declared_at}`, and
`test_probes__every_declared_defect_has_a_reproducing_command` asserts the command re-derives the claim.
**A defect table without re-runnable evidence is a list of opinions**, and the list would grow to cover
every relation someone found inconvenient.

**CORRECTION (adversary F14) — the sentence this ruling used to carry, *"so a template defect can neither
fail a filer nor inflate our coverage"*, was arithmetically wrong in its second clause, and the case where
it is wrong is the case that matters.** For a cell also bound by a passing predicate, roll-up takes
`PASS ≻ INFORMATIONAL` and nothing moves — that is the case the sentence was written from. But for a cell
whose **only** binding evaluation is the declared-defective `TEMPLATE_DIFF`, the cell moves from
`NO_PREDICATE` (**in** `inScope`, unsettled) to `INFORMATIONAL` (**out of** `inScope`), and
`fraction = s/(i−1) > s/i`. **Adding a row to `template_defects.yaml` raises the headline.** Append-only
with an evidence command stops *fabricated* defects; it does nothing about *convenient true* ones, and the
convenient true ones are the ones a person under deadline pressure will find.

> **RULING, and it is a gate not a caution.** `test_defect_table_cannot_raise_the_settled_fraction` — for
> every entry added to `template_defects.yaml`, the reference run is recomputed and
> `fraction' ≤ fraction` is asserted. **If it would rise, the cell's disposition is
> `NO_PREDICATE(no_predicate.rule_ambiguous)` — which stays in the denominator — rather than
> `INFORMATIONAL`.** The two dispositions say different things and both are true of a defective oracle: the
> filer is not failed either way, and the cell is honestly counted as one we could not settle. The test runs
> in CI on every diff that touches the table, and the fallback is implemented in
> `probes/template_diff.py`, not left to the declarer's judgement.

*Alternative it beat:* forbidding defect entries on cells with no other binding evaluation. Rejected because
it makes the *most* defective cells — the ones nothing else reaches — the ones we may not declare, which is
the wrong direction on the only axis that matters.

#### Fixtures, and why there are three

| Fixture | How it is made | Why it exists |
|---|---|---|
| `formula-overwritten__portfolio-O7.xlsx` | raw-zip surgery: copy every part byte-for-byte, rewrite one worksheet XML so `O7` carries a literal ≠ `SUM(C7:N7)`. `'3. Portfolio'!O4 = SUM(C4:N4)` is the shared-formula translation positive control | The methodology's named flagship fixture. `O7` is **locked** in the blank, so the fixture models a filer who stripped protection — the design's standing assumption |
| `formula-overwritten__investors-N5.xlsx` | the same surgery on `'4. Investors'!N5` | **`N5` is one of the 8 cells that are unlocked *and* formula-bearing (MEASURED).** This filer needed no zip edit and no adversarial intent — **Excel alone will do it.** It is a strictly stronger demonstration and it is the one to show a reviewer |
| `formula-overwritten__pair-portfolio-O7-summary.xlsx` | overwrite `O7` **and** the Summary cell that carries it, consistently | The **F11 pair** the spec's E3 threshold names: a coordinated override that leaves every carry identity satisfied. If `TEMPLATE_DIFF` cannot detect this, the flagship detects only careless overrides |

All three carry `CDFC_SYNTHETIC = true` and `CDFC_PROVENANCE` in `/docProps/custom.xml` per methodology
§6.4, and match the §6.5 naming grammar.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_precedents.py::test_precedents__shared_dependents_are_row_shifted` | `'3. Portfolio'!O4 → SUM(C4:N4)`; a dependent resolved from **unshifted** master text is rejected. Paired **value** assertion per R-GOLD-2 |
| `tests/unit/test_precedents.py::test_precedents__cross_sheet_references_resolve_to_the_named_sheet` | `'2. Summary'` formulas referencing `'1. Introduction'!C54` bind on `1. Introduction`, not on the referring sheet |
| `tests/unit/test_precedents.py::test_precedents__unreachable_formula_binds_zero` | a formula whose precedents are all locked returns `∅`, is listed in `pm.unreachable`, and is **refused at G1**, not raised at run time |
| `tests/unit/test_template_diff.py::test_td__applicability_is_false_on_an_empty_precedent_set` | `OUT_OF_SCOPE(out_of_scope.not_applicable)`, never `PASS` |
| `tests/unit/test_template_diff.py::test_td__scope_kind_distinguishes_declared_from_precondition` | a formula with **no** field-surface precedent ⇒ `DECLARED_CHARACTERISTIC`; one whose precedents exist and are empty **on this filing** ⇒ `PREDICATE_PRECONDITION` (C3 names). A single `OUT_OF_SCOPE(out_of_scope.not_applicable)` with no `scope_kind` fails to construct |
| `tests/unit/test_template_diff.py::test_td__defect_that_would_raise_the_fraction_becomes_rule_ambiguous` | the F14 fallback, in code: a declared defect on a cell with no other binding evaluation emits `NO_PREDICATE(no_predicate.rule_ambiguous)`, not `INFORMATIONAL` |
| `tests/contract/test_contract__formula_source_is_explicit` | an AST scan over `src/cdfc/`: every `recalculate(...)` call site passes `formula_source` **literally**; a missing or computed argument fails the build |
| `tests/unit/test_template_diff.py::test_td__count_cells_get_zero_tolerance` | `'1. Introduction'!D17` has `tau == 0` |
| `tests/unit/test_template_diff.py::test_td__money_cells_get_tau_5n` | a `SUM` over 12 money cells has `tau == 60` units |
| `tests/unit/test_template_diff.py::test_td__declared_defect_is_INFORMATIONAL` | `D17` under a declared defect emits `INFORMATIONAL`, is removed from the denominator, and carries both values |
| `tests/unit/test_degree.py::test_degree__categoricals_are_degree_zero` | scheme type, open/closed, jurisdiction ⇒ degree 0 |

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **Binding is a subset of the denominator.** For every finding, `bound_cells ⊆ field_surface` and `bound_cells ≠ ∅` | random subsets of the 505 formula cells over the real FME schema | `probes/template_diff.py` |
| **The ceiling is monotone and bounded.** `|⋃ bound_cells| ≤ 957` for every subset of relations over this template | the same | `probes/precedents.py` |
| **Idempotence.** Running `template_diff` twice over the same fact table yields identical findings in identical order | random fact tables | `probes/template_diff.py` |
| **Tolerance is one-sided in the safe direction.** For degree-1 cells, a difference of exactly `τ` does **not** fire; `τ + 1` does | integer difference sweeps | `probes/template_diff.py` |
| **The fraction does not rise as the filing empties.** `fraction(d(F)) ≤ fraction(F)` for every value-deletion transform `d` (F13) | value-deletion transforms over the FME reference fill — the generator P9-B2 specifies for precondition monotonicity | `verdict/settled_fraction.py` ⊕ `probes/template_diff.py` |
| **A declared defect never raises the fraction.** For every subset of `template_defects.yaml`, `fraction(with) ≤ fraction(without)` (F14) | random subsets of the declared defect table over the reference run | `probes/template_diff.py` |

#### Validation — golden, against the nine real workbooks

| Golden | Workbook | Why that one |
|---|---|---|
| `tests/golden/test_golden__precedent_ceiling__fme.py::test_golden__ceiling_is_957_of_3747` | FME `7d9a1960…` | The published ceiling. **Paired value assertion:** the per-sheet split `Portfolio 400 · Investors 368 · PMS 104 · Introduction 64 · Summary 20 · Compliance Status 1`, and `'3. Portfolio'!O4 == "SUM(C4:N4)"` — count *and* body, per R-GOLD-2 |
| `tests/golden/test_golden__unlocked_formulas__fme.py::test_golden__eight_unlocked_formula_cells` | FME | Pins the eight overwritable-in-Excel cells **by name**: `'4. Investors'!N5,N6,N7,N8,N14,N15,N16,N17`. A change here is a parser regression or a new template version, and both must be loud |
| `tests/golden/test_golden__template_diff__zero_formula.py::test_golden__zero_formula_template_yields_no_relation` | `EDR_1` and `IFSCA_Annual_Reporting_Format` | **Zero formula cells, MEASURED.** `TEMPLATE_DIFF` must produce an empty relation set and say so — not crash, not silently succeed, and **not** report a ceiling of `0/0` |
| `tests/golden/test_golden__template_diff__alr.py::test_golden__alr_has_the_worst_shared_share` | `ALR_V2_3` | **399 of 645 formula cells are shared dependents** — the corpus's worst text-matching loss. If the precedent map is built from formula *text*, ALR is where it fails first and hardest |
| `tests/golden/test_golden__fn_census__fme.py::test_golden__nine_functions_not_eight` | FME | §0.6. Pins `{SUM:135, IFERROR:130, ROW:30, INDEX:30, _xlfn.AGGREGATE:30, ROWS:30, IF:14, COUNTIF:3, _xlfn.SINGLE:1}` and the cell `'1. Introduction'!D92`. **The absence claim "the vocabulary is eight" is now a script with a positive control** |

#### Validation — determinism

`tests/determinism/test_det__template_diff_findings_are_ordered` — findings sort by
`(sheet_index, row, column)`, never by dict or set iteration. Injector: `unsorted_rollup` (existing, NC-A03).
`make determinism`'s four varied dimensions apply unchanged.

#### Validation — negative controls

*Existing entries relied on, named and not restated:* **NC-D02** (denominator provenance — `template_diff`
must not reach `cdfc.predicates` and must not widen the field surface), **NC-E08** (tolerance applied to
counts), **NC-P02** (shared-formula invisibility, which is `precedents.py`'s primary hazard), **NC-E07**
(floating-point money).

*New entries.* Appended to `tests/negative/catalogue.yaml` in the §2 shape, `ACTIVE` from the day B1 merges.

```yaml
- id: NC-R01
  component: probes
  break: "a relation returns PASS on a filing that satisfies it only because the filing is empty"
  measured_instance: "the FME blank's own cached grid: D17/D18/D19/D20 all cache 0 and C92/D92/E92 all cache 'NA' (MEASURED 11 Aug 2026)"
  injector: relation_no_precondition
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_nc__R01a_all_zero_filing_is_OUT_OF_SCOPE
    - tests/relational/test_rel__template_diff.py::test_rel__td_precondition_holds
  positive_control: tests/relational/test_rel__template_diff.py::test_rel__td_fires_on_the_overwritten_pair
  status: ACTIVE

- id: NC-R02
  component: probes
  break: "a TEMPLATE_DIFF finding binds the formula cell itself, which is not in the field surface"
  measured_instance: "497 of 505 FME formula cells are locked, therefore outside the 3,747-cell field surface (MEASURED 11 Aug 2026)"
  injector: td_binds_the_formula_cell
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_nc__R02a_binding_outside_the_denominator_aborts_closure
    - tests/property/test_prop_template_diff.py::test_prop__binding_is_a_subset_of_the_denominator
  positive_control: tests/golden/test_golden__precedent_ceiling__fme.py::test_golden__ceiling_is_957_of_3747
  status: ACTIVE

- id: NC-R03
  component: probes
  break: "a relation with no qualification block settles a cell"
  measured_instance: null
  injector: relation_without_qualification
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_unqualified_relation_cannot_settle_a_cell
  positive_control: tests/negative/test_nc_probes.py::test_nc__R03b_qualified_relation_does_settle
  status: ACTIVE

- id: NC-R04
  component: probes
  break: "the oracle is defective and the relation reports the regulator's own defect as the filer's failure"
  measured_instance: "'1. Introduction'!D17 = SUM(D18:D20) over four COUNTIF patterns matching 7 of the 9 scheme types in Dropdown!F3:F11; Special Situation Fund and Family Investment Fund match none (MEASURED 11 Aug 2026)"
  injector: defect_table_ignored
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_nc__R04a_declared_defect_is_INFORMATIONAL_not_FAIL
    - tests/unit/test_template_diff.py::test_td__declared_defect_is_INFORMATIONAL
  positive_control: tests/negative/test_nc_probes.py::test_nc__R04b_an_undeclared_cell_still_FAILs
  status: ACTIVE

- id: NC-R08
  component: probes
  break: "the observability filter recalculates a mutant through the TEMPLATE's formulas, so an F11 formula-override is identical to clean and the flagship fault class is discarded from O"
  measured_instance: "recalculate() takes the schema induced from the pinned blank; an F11 mutant is a cell the blank declares a formula carrying a literal, so the recalculation overwrites the fault (adversary F19)"
  injector: observability_uses_template_formulas
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_f11_mutant_is_observable
    - tests/relational/test_rel__template_diff.py::test_g2_admits_template_diff
    - tests/contract/test_contract__formula_source_is_explicit
  positive_control: tests/relational/test_rel__template_diff.py::test_rel__td_fires_on_the_overwritten_pair
  status: ACTIVE

- id: NC-R09
  component: probes
  break: "a value-deletion transform raises the settled fraction, because precondition-driven OUT_OF_SCOPE leaves the denominator"
  measured_instance: "inScope = cellsTotal - outOfScope - informational (spec II.3.3); NC-R01's defence against the empty filing is a mechanism that shrinks the denominator (adversary F13)"
  injector: degenerate_scope_leaves_the_denominator
  why_impossible: null
  guard_tests:
    - tests/property/test_prop_settled.py::test_prop__fraction_does_not_rise_as_the_filing_empties
    - tests/unit/test_template_diff.py::test_td__scope_kind_distinguishes_declared_from_precondition
  positive_control: tests/negative/test_nc_probes.py::test_nc__R09b_a_structurally_unreachable_cell_does_leave_the_denominator
  status: ACTIVE

- id: NC-R10
  component: probes
  break: "adding a row to template_defects.yaml raises the settled fraction, because the cell moves from NO_PREDICATE (in scope) to INFORMATIONAL (out of scope)"
  measured_instance: "'1. Introduction'!D17 is bound by TEMPLATE_DIFF alone under the nine-member scheme vocabulary (MEASURED 11 Aug 2026); declaring it moves it out of inScope (adversary F14)"
  injector: defect_moves_a_sole_evaluation_out_of_scope
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_defect_table_cannot_raise_the_settled_fraction
    - tests/unit/test_template_diff.py::test_td__defect_that_would_raise_the_fraction_becomes_rule_ambiguous
  positive_control: tests/unit/test_template_diff.py::test_td__declared_defect_is_INFORMATIONAL
  status: ACTIVE
```

**Injectors created.** `relation_no_precondition.py` (drops the `applicable` call) ·
`td_binds_the_formula_cell.py` (`bound_cells = {formula_cell}`) ·
`relation_without_qualification.py` (loads a relation envelope with the block removed) ·
`defect_table_ignored.py` (`template_defects.yaml` is read and discarded) ·
`observability_uses_template_formulas.py` (`classify()` recalculates with `formula_source="TEMPLATE"`) ·
`degenerate_scope_leaves_the_denominator.py` (`settled_fraction` subtracts every `OUT_OF_SCOPE`, ignoring
`scope_kind`) · `defect_moves_a_sole_evaluation_out_of_scope.py` (the F14 fallback to
`no_predicate.rule_ambiguous` is removed).

**The admission-side positive controls, per methodology §2.3's standing rule and DoD line C5.** A relation
layer that emits nothing scores perfectly on all four negative controls. `test_rel__td_fires_on_the_overwritten_pair`
(the F11 pair **is** detected), `test_nc__R04b` (an undeclared mismatch **does** `FAIL`), and
`test_golden__ceiling_is_957_of_3747` (the relation **does** bind cells) are the three that stop it.

#### Validation — relational, and the E3 threshold as a test

`tests/relational/test_rel__template_diff.py` — the spec's pre-registered E3 threshold, mechanised:

- `test_rel__td_fires_on_the_overwritten_pair` — the F11 pair fixture must produce **≥ 1 `FAIL`**, with the
  overwritten cell in `witness` and its precedents in `bound_cells`.
- `test_rel__td_fires_on_the_excel_only_override` — the `investors-N5` fixture, which required no zip edit.
- **`test_rel__td_fires_on_zero_clean_filings_the_product_did_not_compute`** — **fires on zero** of a clean
  corpus **whose derived cells our evaluator did not write**. *(Supersedes
  `test_rel__td_fires_on_zero_template_computed_clean_filings`, which was `x == x`; see the correction
  immediately below. The superseded name keeps its row in `docs/CATALOGUE-CORRECTIONS.md`.)*
- `@example` pinning is required for every real defect found in review, per methodology §1.2.

**CORRECTION (adversary F2, FATAL) — P9's second exit criterion was a tautology, and it is the exact defect
this project exists to refuse, committed by this document.** `P8-B2::synthesise` builds the
`TEMPLATE-COMPUTED` corpus by filling the input cells and *"letting the workbook's own 505 formula cells
compute the rest via `src/cdfc/calc/`"*. `template_diff` then *"recomputes `c`'s template formula over the
filed inputs using P3's evaluator"* — **`src/cdfc/calc/`**. The oracle and the system under test are the
same function, so *"fires on zero template-computed clean filings"* is **green on a `template_diff` that
always returns `[]` and green on one whose tolerance is 1,000×.** It is not a transfer question and
`plan/04` §7.6's residue does not cover it: the expected fire rate is zero **regardless of the relation's
quality**, which is this plan's own one-line definition of an uninformative number.

> **RULING.** The criterion is re-founded on a corpus the product did not compute, and the acceptable
> corpora are named in priority order so that "we will use what we have" cannot quietly mean
> `TEMPLATE-COMPUTED`:
>
> 1. **`BLIND-FILLED`** (P8-B1) — the intended corpus, and the only one that also licenses an FFR.
> 2. **`REGISTER-DERIVED`** — genuinely independent of our evaluator, and sufficient for the membership,
>    bounds and date classes.
> 3. **One `HAND-COMPUTED` filing** — a single workbook whose derived cells were **typed by a person from
>    the formula text**, `CDFC_PROVENANCE = HAND-COMPUTED`, its author recorded, checked in as
>    `fixtures/clean/hand-computed-001.xlsx`. **This is the fallback that must exist before P9 exits**, and
>    it is deliberately cheap: *one* filing makes the criterion non-vacuous, and **zero is what the plan
>    had.** Costed at 0.5 person-days of the second person's calendar in P9-B2's effort table.
>
> `TEMPLATE-COMPUTED` remains admissible in this build for exactly one purpose — **a smoke check that
> `template_diff` runs end-to-end without raising** — and that test is named
> `test_rel__td_runs_on_a_template_computed_filing_SMOKE_ONLY`, carries the literal string
> `UNINFORMATIVE BY CONSTRUCTION — see P9-B1` in its docstring, and **may not be cited in an exit gate or
> in any published rate.** `test_nc__R08c_template_computed_cannot_found_the_zero_fire_claim` asserts that
> the exit-gate evaluator refuses a `TEMPLATE-COMPUTED` corpus id for criterion 2.

#### Validation — performance

| Budget id | Subject | Baseline | Fail above | Warn above |
|---|---|---:|---:|---:|
| `PERF-PRECED` | `build_precedent_map` over 505 formulas, cold | to be recorded on first green run | 250 ms | 150 ms |
| `PERF-TD` | `template_diff` over 505 cells against a built fact table | to be recorded | 40 ms | 25 ms |

`PERF-PRECED` is a **per-template** cost and is cached by `template_sha256`, so it sits outside
`PERF-ONLINE`; `PERF-TD` sits inside it. `PERF-ONLINE` (≈450 ms, fail above 900 ms) must not regress.

#### Mutation, per methodology §3.5 — and `probes/` has no tier yet, so this document assigns one

**`src/cdfc/probes/` appears in no row of the methodology's §3.5 tier table.** An unassigned module is
scored by nothing, which is the same defect as an unregistered surface (NC-A10) one level down. **This
document assigns it, for the whole phase, with the argument `docs/MUTATION-THRESHOLDS.md` requires:**

| Module | Tier | `K/V` | Blocking from | Argument |
|---|---|---:|---|---|
| `probes/precedents.py` | **V** | 0.90 | **P9** | A surviving mutant is a silently wrong *binding set for a relation* — NC-D02's mechanism wearing a probe's clothes |
| `probes/degree.py` | **V** | 0.90 | **P9** | A surviving mutant is a tolerance applied to a count. **A person is not a rounded quantity** (NC-E08) |
| `probes/template_diff.py`, `probes/relations/`, `probes/qualify.py` | **Q** | 0.85 | **P9** | They admit and score checks that settle regulated cells; that is qualification work, whatever directory it lives in |
| `probes/driver.py` | **S** | 0.70 | P9 + 2 | A search harness. Its determinism is guarded by `test_det__probe_results_are_seed_stable`, which mutation would not reach anyway |

Thresholds are **raised** relative to the unassigned default, never lowered, so §3.5's rule is satisfied.
The phase gate prints, in this exact form:
`probes/precedents.py: K/V = <k>/<v> (floor) · K/(V−E) = <k>/<v−e> with E = <e> adjudicated, arguments in
reports/mutation/probes_precedents.ledger.jsonl · I = <i>, T = <t> (ids listed)`. **A phase gate quoting a
bare percentage fails its own review.**

---

### BUILD P9-B2 — THE RELATION SET THE CORPUS GROUNDS, AND ITS AUTHORING PROTOCOL · 3 days enumerated + open scope

**What it produces.** A registry of **the relations the corpus grounds**, each with its evidence, its class,
its preconditions and its review record — and, as importantly, the **refusals**: relations that were drafted
and rejected at authoring review, kept with their reason.

**This document specifies the registry, the classes, the protocol, the review gate and the named relations
that the corpus actually grounds. It does not invent twenty-two relations.** Inventing them here would be
the exact failure this build exists to prevent — model-generated and desk-generated relations *"score
markedly low on novelty and recapitulate the textbook classes"*, which is how an earlier version arrived at
five relations of which four false-alarm on a correct filing.

**CORRECTION (adversary F32 / F42) — the number 25 is deleted from this build, from its gate and from every
denominator downstream of it.** The previous shape was *"a 5-day build with a 25-row deliverable of which 7
rows are named"* — i.e. **18 rows of unspecified content and an estimate over content nobody has written**,
which is a placeholder that will be defended as a commitment. And its exit condition, *"every relation holds
on the clean filing and is violated by a targeted mutant"*, was satisfiable **by construction** for any
arithmetic relation on the `TEMPLATE-COMPUTED` corpus (F2).

> **RULING, three parts.**
>
> **(a) The deliverable is `docs/RELATION-REVIEW.md`'s two counts — admitted and refused — not a target.**
> `|catalogue|` is a **measurement**, published on the day the catalogue is written, and every downstream
> denominator reads it from `probes.relations.registry.CATALOGUE_SIZE` rather than from the literal `25`.
> The phase's own failure branch already says the refusal rows are the more interesting result; this makes
> the document agree with itself.
>
> **(b) Effort is quoted for the enumerated work and the remainder is open scope with a decision rule.**
> **3 engineer-days** buys: the registry and its loader, the seven named relations (R-01…R-07), the
> partition machinery, the basis guard, the review protocol and this build's tests. Further relations are
> authored **one at a time, each through the protocol, each with its own review row**, at a measured
> ~0.35 engineer-days each on the first three; the phase re-plans when
> `docs/measurements/P9-relation-runnability.md` first publishes a measured rate. *Decision rule for
> stopping:* authoring stops when three consecutive candidates are **refused** at step 1 for want of an
> artifact fact — that is the corpus telling us the ground is exhausted, and it is a publishable finding.
>
> **(c) The second reviewer is budgeted, in person-days, like every other human step in this plan.**
> **2–3 person-days of a second person's calendar** for the review signatures across the enumerated
> relations, plus **0.5 person-days** for the single `HAND-COMPUTED` clean filing that F2's repair requires.
> **These are never added to the engineer's total.** *If no second person exists*, step 7's two signatures
> become one, `docs/RELATION-REVIEW.md` carries the literal string `SINGLE-SIGNER — a weaker review` on
> every affected row, and that string renders beside every relation-derived number on the report surface —
> the same discipline §P9's G-EVAL entry criterion applies to arm 2. **What is not available is a second
> signature that nobody's calendar contains.**

#### Files created

```
src/cdfc/probes/relations/__init__.py
src/cdfc/probes/relations/registry.py       the RelationSpec record and the loader
src/cdfc/probes/relations/catalogue.yaml    one row per admitted relation, each with its evidence and its
                                            review record. THE ROW COUNT IS A MEASUREMENT, NOT A TARGET
src/cdfc/probes/relations/partition.py      the partition family and its non-degeneracy machinery
src/cdfc/probes/relations/basis.py          the direct-investment / look-through basis guard
src/cdfc/probes/relations/prior_period.py   the three relations needing two consecutive filings
src/cdfc/probes/relations/selftest.py       the two checker self-tests, never shown to the filer
docs/RELATION-REVIEW.md                     append-only: every relation drafted, admitted or refused
docs/measurements/P9-relation-runnability.md
```

#### Public interface, verbatim

```python
# src/cdfc/probes/relations/registry.py

Necessity = Literal["NECESSARY", "EXPECTED"]     # NECESSARY ⇒ FAIL; EXPECTED ⇒ INFORMATIONAL
Inputs    = Literal["FILING_ONLY", "FILING_AND_BLANK", "TWO_CONSECUTIVE", "MANY_INSTANCES", "SELF_TEST"]

@dataclass(frozen=True, slots=True)
class RelationSpec:
    id: str                       # "R-07"
    title: str
    necessity: Necessity
    inputs: Inputs
    degree: Mapping[StableKey, int]      # money = 1; counts, dates, ratios, categoricals = 0
    precondition: str                    # CEL. Non-degeneracy. Unmet ⇒ OUT_OF_SCOPE, never PASS
    expr: str                            # CEL
    witness: str                         # CEL
    bases: frozenset[str]                # e.g. {"DIRECT_INVESTMENT"} or {"LOOK_THROUGH"}
    evidence: str                        # the artifact fact or guidance note that licenses it
    reviewed_by: str
    reviewed_at: date
    reported_to_filer: bool              # False for SELF_TEST
    claims_fault_classes: tuple[str, ...]   # REQUIRED, NON-EMPTY. The fault classes this relation
                                            # CLAIMS to cover, declared at authoring time and carried
                                            # into the predicate envelope by P9-B4's to_envelope().
                                            # G2 scores K/O over THIS set and raises if any member
                                            # has O == 0.  Declared before the campaign or it is not
                                            # a claim (adversary F1).
```

#### The five input classes, with their counts and their consequence

| Class | Count among the **seven enumerated** relations | Consequence for a single-filing run today |
|---|---:|---|
| `FILING_ONLY` | 2 (R-02, R-03) | runnable |
| `FILING_AND_BLANK` | 2 (R-01, R-04) | runnable — the oracle is the pinned blank, so no corpus is needed. `TEMPLATE_DIFF` is one of these |
| `TWO_CONSECUTIVE` | 1 (R-07) | **`NOT_RUN(not_run.input_unavailable.prior_period)` on every run today** |
| `MANY_INSTANCES` | 0 | **`NOT_RUN(not_run.input_unavailable.counterparty)` on every run today**, if one is ever authored |
| `SELF_TEST` | 2 (R-05, R-06) | runs, never reported to the filer, feeds P10 |

> **The number this table produces, and it is a phase number: `un-runnable / |catalogue|` — today
> `1 of 7` — because no real filed FME return is public.** **Both integers are computed from
> `catalogue.yaml` at render time and neither is a literal anywhere** (F32; and F22's lesson about pinned
> literals, applied before it is committed). Published in `docs/measurements/P9-relation-runnability.md`
> **on the day the catalogue is written**, not discovered later. A layer that quietly ships `n − k`
> relations while claiming `n` is the coverage lie in miniature — and a layer that claims a round number it
> chose before authoring anything is the same lie, one document earlier.

#### The relations the corpus grounds, named

These are authored against measured facts and are the ones an engineer can begin on day one. The remaining
rows are authored under the protocol below.

| id | Relation | Class | Necessity | Evidence |
|---|---|---|---|---|
| **R-01** | `TEMPLATE_DIFF` — filed value versus the template's own formula over filed inputs | `FILING_AND_BLANK` | NECESSARY | P9-B1. 505 formula cells all carry cached values (MEASURED); ceiling 957 of 3,747 |
| **R-02** | **Four-way funds-raised partition** — funds raised by investor category, by country, by accreditation status, and via the Summary carry must agree | `FILING_ONLY` | NECESSARY | **The workbook enforces agreement between none of them: Tables 4.2 and 4.3 contain zero formulas (MEASURED).** The highest-value relation in the design and it is not in the brief |
| **R-03** | **Scheme-total consistency** — `'1. Introduction'!D17` versus a count of declared scheme types in `G54:G63` under the full nine-member vocabulary | `FILING_ONLY` | **EXPECTED** | The regulator's own COUNTIFs match 7 of 9 (MEASURED, §P9-B1). **`EXPECTED`, therefore `INFORMATIONAL`** — the disagreement is a property of the template, not of the filer |
| **R-04** | **Vocabulary closure under the pinned blank** — every categorical cell holds a term from `Dropdown`, resolved from the **blank**, never the filing | `FILING_AND_BLANK` | NECESSARY | `Dropdown` is `state="hidden"` **and the only unprotected sheet** (MEASURED). A relation resolving from the filing validates the filer against a list the filer can edit |
| **R-05** | **Denominator self-agreement** — the two independent field-surface computations agree | `SELF_TEST` | NECESSARY | Barrier 1. `reported_to_filer = False` |
| **R-06** | **Canary-population self-agreement** — `canaries_run` equals the number of canary rows written to `run.jsonl` | `SELF_TEST` | NECESSARY | §0.4 and P10-B1. `reported_to_filer = False` |
| **R-07** | **Prior-period opening/closing continuity** | `TWO_CONSECUTIVE` | NECESSARY | Un-runnable today; reports `NOT_RUN(not_run.input_unavailable.prior_period)` |

#### The authoring protocol — the part that is reading, not typing

Each candidate relation passes this before it is written into the catalogue. **`docs/RELATION-REVIEW.md` is
append-only and records every candidate, admitted or refused, with its reason** — because the refusals are
the evidence that the protocol did anything.

1. **Name the artifact fact that licenses it.** A cell range, a formula, a guidance note, or a validation.
   *"It seems like it should hold"* is a refusal.
2. **Classify `NECESSARY` or `EXPECTED`.** `NECESSARY` violations `FAIL`. `EXPECTED` violations are
   `INFORMATIONAL` and carry the guidance note that makes the exception lawful. **If you cannot name the
   note, it is not `EXPECTED`; it is unfinished.**
3. **Write the non-degeneracy precondition first, before `expr`.** Written second, it is written to make
   the relation pass.
4. **Declare the basis set.** **No relation may combine a Table 3.x quantity (direct-investment basis) with
   a Table 5.6 quantity (look-through basis)** — Portfolio note 7 against the PMS note. Asserted by
   `tests/relational/test_rel__basis_contamination_guard`.
5. **Declare the degree map, and the fault-class claim.** Money = 1, everything else 0. And
   `claims_fault_classes` — **written into the review row, dated and signed, before any campaign is run**
   (F1). *"Whichever classes it turns out to kill"* is a refusal. The claim is the denominator of the
   relation's own quality score, and a denominator chosen after the result is not a denominator.
6. **Check for redundancy against the harvested set.** A relation equivalent to a harvested predicate
   inflates the before/after delta with a rename. Z3's subsumption arm (`P₁ ∧ ¬P₂` UNSAT ⇒ `P₂` redundant)
   decides it, and **the removal is recorded, not silent** (NC-Q07d).
7. **Two humans sign the review row.** Relation authoring is one of the twelve places the spec requires a
   human, and one signature is a preference. **Budgeted at 2–3 person-days of a second person's calendar
   (ruling (c) above), which is the only form in which a second signature is a plan rather than a hope.**
   `tests/unit/test_relation_registry.py::test_reg__two_signatures_or_the_weaker_label` — a row with one
   signer loads **only** if it carries `SINGLE-SIGNER — a weaker review`, and that string is asserted
   present on every surface that quotes a relation-derived number.

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_relation_registry.py::test_reg__necessity_drives_the_state` | `NECESSARY` violation ⇒ `FAIL`; `EXPECTED` ⇒ `INFORMATIONAL`; **no third path exists in the code** |
| unit | `…::test_reg__every_relation_has_a_precondition` | a `RelationSpec` with an empty `precondition` fails to load |
| unit | `…::test_reg__every_relation_has_evidence_and_two_reviewers` | loader refusal, not a warning |
| unit | `…::test_reg__self_tests_are_never_reported_to_the_filer` | `reported_to_filer=False` ⇒ absent from the filer-facing item list and from `settledFraction` |
| property | **Precondition monotonicity** — if a relation is `OUT_OF_SCOPE` on filing `F`, it is `OUT_OF_SCOPE` on every filing obtained from `F` by deleting values. Generator: value-deletion transforms over the FME reference fill | `probes/relations/partition.py` |
| property | **Basis disjointness** — for every relation, `bases` is a singleton or the relation is refused. Generator: random key subsets tagged by basis | `probes/relations/basis.py` |
| relational | `tests/relational/test_rel__basis_contamination_guard` | a drafted relation summing a 3.x and a 5.6 quantity is **refused at authoring review by a named test**, not caught in production |
| relational | `tests/relational/test_rel__all_zero_filing.py::test_rel__every_partition_is_OUT_OF_SCOPE` | over **all** partition relations. Without it, an empty filing scores 100% through the L6 door |
| golden | `tests/golden/test_golden__relation_runnability.py::test_golden__runnability_split_matches_the_catalogue` | the per-class split is asserted **equal to the split computed from `catalogue.yaml`**, never to a literal; the current values live in `docs/measurements/P9-relation-runnability.md` and move only with a dated row there (the `docs/HARVEST-DELTA.md` discipline). Asserts every un-runnable relation reports `NOT_RUN` with the correct `input_unavailable.*` code — **not absence** |
| relational | `tests/relational/test_rel__corpus_independence.py::test_rel__every_admitted_relation_was_violated_by_a_mutant_on_a_corpus_the_relation_did_not_generate` | **the F2 repair applied to this build's own gate.** For every admitted relation: the clean-filing arm ran on a corpus whose generator import closure is **disjoint** from the relation's evaluation closure, and the mutant arm's targeted mutant was seeded into *that* filing. A relation whose only clean-filing evidence is `TEMPLATE-COMPUTED` **fails to be admitted**, with reason `uninformative_corpus` — the same `UninformativeCorpusError` shape as `SELF-AUTHORED`, not a second code path |
| determinism | `tests/determinism/test_det__relation_order_is_catalogue_order` | relations execute and report in `catalogue.yaml` order, never in dict or filesystem-glob order. A relation set enumerated by `Path.glob` is ordered by the filesystem, which differs between the two CI runner images and would break `verify` for reasons nobody would look for |

**Performance.** No new budget. The relation set runs inside `PERF-ONLINE` (≈450 ms, fail above 900 ms);
spec §III.5 attributes ~160 ms (DERIVED) to the probe layer, and `docs/measurements/P9-delta.md` records the
first **measured** figure against it on the first green run.

*New catalogue entry:*

```yaml
- id: NC-R05
  component: probes
  break: "a relation drafted across two accounting bases is admitted"
  measured_instance: "Portfolio note 7 puts Tables 3.1/3.2 on a direct-investment basis; the PMS note puts Table 5.6 on a look-through basis"
  injector: basis_guard_disabled
  why_impossible: null
  guard_tests:
    - tests/relational/test_rel__basis_contamination_guard.py::test_rel__cross_basis_relation_is_refused
    - tests/unit/test_relation_registry.py::test_reg__every_relation_has_evidence_and_two_reviewers
  positive_control: tests/relational/test_rel__basis_contamination_guard.py::test_rel__single_basis_relation_is_admitted
  status: ACTIVE
```

---

### BUILD P9-B3 — THE EXECUTION VEHICLE · 2 days

**What it produces.** A driver in which the `FAIL` / `INFORMATIONAL` split is enforced **by the library**
rather than by our convention, and in which every real defect ever found is pinned forever.

#### Files created

```
src/cdfc/probes/driver.py
src/cdfc/probes/examples.py          @example pins, append-only, one per real defect ever found
tests/relational/conftest.py         the Hypothesis profiles for this suite
```

#### Public interface

```python
# src/cdfc/probes/driver.py
class ProbeMachine(RuleBasedStateMachine):
    """@invariant for NECESSARY relations (violation ⇒ FAIL);
       in-rule assertions for EXPECTED (violation ⇒ INFORMATIONAL).
       The split is the library's, not ours: an @invariant that fails is a falsifying example;
       an in-rule assertion that fails is a recorded observation."""

def run_probes(filing: FactTable, template: TemplateSchema,
               relations: Sequence[RelationSpec], *, max_examples: int = 50
               ) -> list[ProbeResult]: ...
```

`max_examples = 50`, the spec's decided budget: **55% of mutations are found with a single input and 76%
within the first 20**, and this input space is small and fixed. Profiles: `fast` (50, CI stage 5), `deep`
(1,000, nightly, advisory).

#### Validation

| Test | Asserts |
|---|---|
| `tests/unit/test_driver.py::test_driver__invariant_maps_to_FAIL` | a violated `@invariant` produces `FAIL`, with the shrunk counterexample as `witness` |
| `tests/unit/test_driver.py::test_driver__in_rule_assertion_maps_to_INFORMATIONAL` | and **never** to `FAIL` |
| `tests/unit/test_driver.py::test_driver__budget_exhaustion_is_NOT_RUN` | `NOT_RUN(not_run.budget_exhausted)`, never `FAIL`. A probe that ran out of time has told us nothing about the filing |
| `tests/unit/test_examples.py::test_examples__every_real_defect_is_pinned` | `examples.py` is append-only; a removed `@example` fails the build |
| determinism | `tests/determinism/test_det__probe_results_are_seed_stable` | the Hypothesis seed is an input recorded in the manifest, not drawn from entropy. **Without this, `verify` cannot re-derive a probe result at all** |

**The determinism test is the one that matters here** and it is easy to miss: Hypothesis is a *search*, and
a search with an unpinned seed makes the report irreproducible in exactly the way P11 must refuse. The seed
is written into `run.manifest.probe_seed` and replayed by `verify`.

*New catalogue entry:*

```yaml
- id: NC-R06
  component: probes
  break: "the probe search draws its seed from entropy, so the report cannot be re-derived"
  measured_instance: null
  injector: probe_seed_from_entropy
  why_impossible: null
  guard_tests:
    - tests/determinism/test_det__probe_results_are_seed_stable
    - tests/e2e/test_e2e__verify.py::test_e2e__VERIFY_byte_identical
  positive_control: tests/determinism/test_det__probe_results_differ_under_a_different_seed
  status: ACTIVE
```

The positive control is the interesting half: a seed that changes **must** change the search, or the seed is
not doing anything and the determinism test is vacuously green.

---

### BUILD P9-B4 — ROUTING EVERY RELATION THROUGH THE FIVE GATES · 4 days

**What it produces.** The property that makes the layer honest: **a relation is a predicate.** It passes
G0 → G1 → G3-proof → G2 → G3-empirical → G4 in that order, is stored in the same registry, carries the same
`qualification` block, and **may not settle a single cell until it does.**

#### Files created

```
src/cdfc/probes/qualify.py           the adapter: RelationSpec -> the P4 predicate envelope
src/cdfc/probes/mutants.py           targeted mutant generation per relation (uses P6's harness)
docs/measurements/P9-relation-attrition.md
docs/measurements/P9-delta.md        the before/after settled-count delta, per relation
```

#### Public interface

```python
# src/cdfc/probes/qualify.py
def to_envelope(r: RelationSpec, schema: TemplateSchema) -> Predicate: ...
    # kind = "relation".  schema_keys machine-checked against the CEL AST BOTH WAYS (P4-B2).
    # A relation that reads an undeclared key, or declares an unread one, is REJECTED —
    # the same rejection, in the same code path, as a harvested predicate.

def targeted_mutants(r: RelationSpec, filing: FactTable, model: FaultModel) -> list[Mutant]: ...
    # G2 for a relation: mutants aimed at the relation's read set, PLUS the 10% control sample
    # of fields it does NOT read.  Without the control arm a flag-everything relation scores perfectly.
```

#### The delta, and the ceiling it is published against

`docs/measurements/P9-delta.md` publishes, per relation and in this order:

1. **the ceiling**, from B1's precedent map where the relation is `FILING_AND_BLANK`, or from the relation's
   own read set otherwise;
2. **the before count** — settled cells with the relation absent;
3. **the after count** — settled cells with the relation admitted;
4. **the delta**, which may be **zero**, and **a relation that moved nothing is reported as moving nothing**;
5. **the marginal kill** — `|WRONG mutants this relation rejects that no admitted predicate rejects|` over
   the P10-B2 residue population, on the **same shared `O`** that `experiment/baselines/marginal.py`
   computes for the P12 baselines. See the ruling below; it is not optional and it is not a supplement;
6. **the gate that rejected it**, where it was rejected, with the measured number — a `rejection` row, which
   *is* `no_predicate.failed_qualification` and the report's `counterEvidence[]`.

**Why the delta alone systematically under-measures the most important relation in the design (adversary
F21).** `TEMPLATE_DIFF`'s ceiling is 957 field-surface cells, and on FME those cells are **largely already
bound** by the 181 `cross_sheet_equality` and 35 `sum_identity` harvested predicates, which read the same
precedent ranges. So the flagship's **settled-count delta is near zero by construction**, while its
**detection power** — it is the only check in the entire design that sees a formula overwritten with a
literal — is untouched by that fact. Publishing the delta alone and writing *"a relation that moved nothing
is reported as moving nothing"* presents a **finding about the metric** as a finding about the relation.

> **RULING.** Every relation publishes **two** numbers, side by side, in this order, and neither may be
> rendered without the other:
> **(a)** settled-count delta, and **(b)** marginal kill over the residue population.
> `tests/relational/test_rel__delta.py::test_rel__delta_and_marginal_are_both_published` fails the build if
> `P9-delta.md` carries one column and not the other. For `TEMPLATE_DIFF` specifically, (b) is the number
> that goes on the slide and (a) is the footnote; for a carry relation over unbound cells it is the reverse.
> **The document does not choose which is the headline per relation — it prints both and lets the reader.**
>
> *Ordering consequence:* (b) needs the P10-B2 residue population, so `P9-delta.md` is **completed** after
> P10-B2 rather than at P9-B4. B4 writes the file with column (b) as `PENDING — requires P10-B2` and the
> date; `test_rel__pending_marginal_is_dated_not_blank` asserts the placeholder is a dated open item and
> never an empty cell. This is the `P9-B4 → P10-B2` edge (F34) travelling in the other direction, and it is
> the reason both edges must appear in `plan/00` §3.1.

**And the ceiling that goes on the same page, stated in advance:** this layer moves **≈ 0 of the 7**
properties that are not settleable from the artifact at all. The relation layer grows the *settled* count;
it does not touch the *undecidable* floor, and a page that shows growth without the floor is a growth chart
with the asymptote cropped.

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_probe_qualify.py::test_pq__relation_is_a_predicate` | `to_envelope` output loads through **the same** registry loader; a divergent code path fails the test |
| unit | `…::test_pq__schema_keys_checked_both_ways` | reads-undeclared **and** declares-unread are rejected with **distinct** reasons (NC-Q04's rule applied to relations) |
| unit | `…::test_pq__relation_without_qualification_does_not_load` | the loader invariant, unchanged |
| golden | `tests/golden/test_golden__relation_attrition.py::test_golden__funnel_has_every_stage` | the funnel prints six integers — generated → G0 → G1 → G3ᵖ → G2 → G3ᵉ → G4 — and each rejection names its gate and its measured number |
| relational | `tests/relational/test_rel__delta.py::test_rel__zero_delta_is_reported` | a relation with delta 0 appears in `P9-delta.md` **with 0**, not omitted |
| relational | `tests/relational/test_rel__delta.py::test_rel__delta_and_marginal_are_both_published` | F21. `P9-delta.md` carries **both** columns for **every** relation; one column present and the other absent fails the build |
| relational | `tests/relational/test_rel__template_diff.py::test_g2_admits_template_diff` | **F19's exit-side assertion.** `TEMPLATE_DIFF` reaches G2 with `O > 0`, its per-class vector has `O > 0` for F11, and `K/O` is a computed number rather than a `CampaignArithmeticError` |
| unit | `…::test_pq__claims_fault_classes_is_carried_through_to_envelope` | F1's consumer side: `to_envelope` copies the relation's declared `claims_fault_classes` into the predicate envelope, and a relation with an empty claim set **fails to convert** |
| negative | `tests/negative/test_nc_probes.py::test_unqualified_relation_cannot_settle_a_cell` | NC-R03. **The B1 spike's output is a demonstration, not an admission**, and this is the test that says so |

*New catalogue entry:*

```yaml
- id: NC-R07
  component: probes
  break: "a relation duplicates a harvested predicate, so the before/after delta counts the same cell twice"
  measured_instance: "181 cross-sheet equalities and 35 sum identities are already harvested; a carry relation restates them"
  injector: subsumption_check_disabled
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_probes.py::test_nc__R07a_redundant_relation_is_removed_and_the_removal_is_recorded
    - tests/relational/test_rel__delta.py::test_rel__delta_counts_cells_not_evaluations
  positive_control: tests/negative/test_nc_probes.py::test_nc__R07b_a_genuinely_new_relation_moves_the_count
  status: ACTIVE
```

---

## P9 · The measurement this phase produces

**Primary — the per-relation pair: before/after settled-count delta AND marginal kill over the residue
population, for every relation including the ones that moved nothing.** Denominator: **`|catalogue|`
relations / 3,747 cells**, where `|catalogue|` is read from `probes.relations.registry.CATALOGUE_SIZE` and
is never a literal (F32). Warrant **MEASURED**. Published with the ceiling above it, and with the marginal
column beside the delta column (F21) — **a delta published alone is not this measurement.**

**Every number in this section, and in P10's and P11's, carries the G-EVAL independence label.** If
`docs/measurements/P3-evaluator.md` records `SAME-AUTHOR — a weaker instrument`, that literal string renders
beside every figure derived from `src/cdfc/calc/` — which is every `TEMPLATE_DIFF` number, every kill rate,
and the 957 ceiling itself. `tests/contract/test_contract__geval_label_travels_with_the_numbers` asserts it
on the rendered surface, not in a footnote (F3).

**Three supporting numbers that do not exist anywhere today, two of them already measured by this document
and re-runnable from `tools/probes/`:**

| Number | Value | Denominator | Warrant |
|---|---|---|---|
| Field-surface cells feeding ≥ 1 template formula — **`TEMPLATE_DIFF`'s ceiling** | **957** | 3,747 field-surface cells | **MEASURED, 11 Aug 2026** |
| Field-surface cells feeding **no** template formula — the recompute-blind set | **2,790** | 3,747 | **MEASURED**, and it is P10's second residue argument |
| Formula cells a filer can overwrite **without stripping protection** | **8** (`'4. Investors'!N5:N8, N14:N17`) | 505 formula cells | **MEASURED** |
| Relations structurally un-runnable on any obtainable filing | computed (**1** among the seven enumerated) | `\|catalogue\|`, computed | MEASURED at catalogue time; **both integers computed, neither pinned** (F32) |
| Relations drafted and **refused** at authoring review | computed | candidates drafted | MEASURED — the refusal log is the evidence that the protocol did anything |
| Function vocabulary of the FME workbook | **9**, not 8 (`_xlfn.SINGLE` at `'1. Introduction'!D92`) | 505 formula cells | **MEASURED, 11 Aug 2026** |

Every row is appended to `reports/validation-ledger.jsonl` with all nine fields, per methodology §5.5.

## P9 · Exit gate

A boolean, evaluable by someone who did not do the work:

1. `docs/measurements/P9-template-diff-ceiling.md` publishes **957 of 3,747** with its per-sheet split and
   the command that re-derives it; `test_golden__ceiling_is_957_of_3747` is green.
2. **`TEMPLATE_DIFF` detects the seeded F11 *pair*** (`formula-overwritten__pair-portfolio-O7-summary.xlsx`)
   **and fires on zero clean filings of a corpus the product did not compute** — `BLIND-FILLED`,
   `REGISTER-DERIVED`, or at minimum the one `HAND-COMPUTED` filing. **A `TEMPLATE-COMPUTED` corpus id is
   refused by the gate evaluator** (`test_nc__R08c`). This is spec E3's pre-registered threshold with its
   corpus corrected — the threshold has not moved; the thing it is measured on has (F2).
3. **`test_f11_mutant_is_observable` and `test_g2_admits_template_diff` are green**, and
   `docs/EVALUATION-CONTRACT.md` publishes the `formula_source` rule. **Without this criterion the flagship
   relation is unadmittable at G2 and nobody finds out until P9-B4** (F19).
4. **Every relation holds on the clean filing and is violated by a targeted mutant** — both, per relation,
   in `docs/measurements/P9-relation-attrition.md` — **and the clean-filing arm ran on a corpus whose
   generator is import-disjoint from the relation's evaluator**
   (`test_rel__every_admitted_relation_was_violated_by_a_mutant_on_a_corpus_the_relation_did_not_generate`).
5. **Every relation that settles a cell has passed all five gates**, and
   `test_unqualified_relation_cannot_settle_a_cell` is green; every one carries a **non-empty
   `claims_fault_classes` declared before its campaign** (F1).
6. The all-zero filing returns `OUT_OF_SCOPE` from **every** partition relation
   (`test_rel__every_partition_is_OUT_OF_SCOPE`), **and
   `test_prop__fraction_does_not_rise_as_the_filing_empties` is green** — the second is the one that makes
   the first mean something, because `OUT_OF_SCOPE` is how a filing leaves the denominator (F13).
7. `docs/measurements/P9-delta.md` exists, lists **every** relation including the zero-delta ones, carries
   **both** the delta and the marginal-kill columns (F21), and carries the ≈ 0-of-7 ceiling sentence on the
   same page.
8. `test_defect_table_cannot_raise_the_settled_fraction` is green for every row of
   `template_defects.yaml` (F14).
9. `make nc-sweep` shows every NC-R entry caught by its injector — **per-guard, not "at least one guard"
   (F4)** — with every positive control green.

## P9 · What it kills if it fails

- **If the relations cannot be authored honestly** — the failure mode that produced five relations of which
  four false-alarm — **the layer is deleted and the settled fraction becomes a ceiling rather than a growth
  curve.** That is a real loss and it is survivable: the harvest, the gate, closure, the canaries and the
  residue set are untouched. `docs/RELATION-REVIEW.md`'s refusal rows become the published result, which is
  a smaller and more interesting paper than the one where a round number of relations shipped unexamined.
- **If `TEMPLATE_DIFF` fails specifically** — either because G-EVAL did not found the evaluator, or because
  the precedent map cannot be built reliably across shared dependents — **the design's flagship dies and the
  demo loses its best moment.** Everything else stands. The honest replacement claim is the one the ceiling
  already licenses: *957 of 3,747 cells feed a formula the regulator wrote, and we cannot check any of them
  against it.* That sentence is worth publishing on its own.
- **If the precedent map is right but the ceiling is far smaller than 957 in practice** (because most
  formulas are `IFERROR`-wrapped lookups rather than arithmetic over filer inputs), the delta is small and
  **is published small**. A small measured delta beats a large asserted one; the ceiling is published first
  precisely so that a small delta reads as a measurement rather than as a disappointment.

---
---

# P10 — L6.5: RUN-TIME CANARIES AND THE RESIDUE SET

**Effort: 10.5 engineer-days** · B1 **4.5** · B2 3 · B3 2 · B4 1
*(B1 was 4 and excluded the `MAX_WITNESSES ∈ {1,3,5}` calibration §5.1 requires — three campaigns over the
clean corpus are not free. The extra 0.5 buys the curve, and its deliverable is named in B1's file list:
`docs/measurements/P10-canary-cost.md`'s inapplicability-versus-`MAX_WITNESSES` curve. Adversary F44.)*
**Plus 3–5 person-days of a second person's calendar** for INNOCUOUS/WRONG adjudication (B2) and 1 further
person-day for the 20% re-adjudication that produces Cohen's κ (B3). **These are never added to the
engineer's total** and they are the reason B2 cannot be compressed.

## P10 · What it settles

**Whether a verdict can be conditioned on a proof obtained from the artifact under test, in the same
execution, and withheld when that proof fails — and how large the provably-unkillable class is.**

The claim, at full strength, and it is falsifiable:

> **No assurance artifact in existence carries evidence that the instrument that produced it was working on
> the specific document it examined. A clean audit opinion does not. An SBOM does not. A validation report
> does not. Ours refuses to issue a verdict unless every check has just demonstrated, on your file, that it
> can still catch the fault it was admitted for.**

**This is the design's boldest claim, so its validation is the most important in the plan**, and §P10·L is
written to be attacked. The mechanism itself claims no novelty — it is two extra executions per predicate —
and it needs no citation. The nearest named prior art is SRE synthetic monitoring and hardware built-in
self-test, not anything in the testing literature. *A formal-methods citation for vacuity detection is
**UNVERIFIED** and must not be asserted.*

## P10 · Entry criteria

| Build | Requires | Why the edge is real |
|---|---|---|
| **B1** | **P7 complete** — liveness witnesses stored at admission | There is nothing to replay until admission stores something replayable, and §0.2 changes *what* is stored, so P7's `admit.py` must already write `FaultWitness` records |
| **B1** | **P6 complete** — the fault model at v3, the observability filter | Witness applicability is decided by recalculation, which **is** the observability filter (§0.3) |
| **B1** | **P5 complete** — the eight run-level `invalid.*` causes exist as their own vocabulary | `invalid.canary_silent` is a run-level cause, not a per-cell reason code |
| **B2** | **P9-B4 complete** — every admitted relation is in the registry | The residue is *"WRONG mutants that no predicate **and no relation** rejects"*. Computing it before the relations are admitted overstates the residue, which flatters us in the direction of a bigger publishable number — the one direction to be most suspicious of. **This edge is absent from `plan/00` §3.1's dependency graph and it is not free (adversary F34): with it, `P7 ends 86 → P9 ends 100 → P10-B2 starts 100 → P10 ends ~106 → P11 ends ~116`, so at `k = 0` the critical path re-routes through the attestation spine and is **~118 days, not ~104** (arbitration **C6**; the `~114` this row previously carried was computed before `plan/02` R11 revised P0 to 8 and P3 to 17, and is retired). `plan/00` §7 is the arithmetic of record and carries the number; `plan/00` §3.1/§4/§4.1 carry the edge; this document argued the edge, so this document states its cost and cites rather than restates the total** |
| **B2** | **P8 evaluated, either way** | On G-CORPUS's FAIL branch the admitted set is empty and the residue is computed over an empty rejector set. **That is still a result** and it is a *ceiling* on the residue, published as such |
| **B3** | a **second adjudicator** who is not the first | κ needs two raters. One rater produces a number with an unquantified error and no way to see it |

## P10 · Builds

---

### BUILD P10-B1 — THE CANARY LOOP · 4 days

**What it produces.** The property that a verdict is withheld when liveness is not demonstrated — and the
counts that prove the loop ran.

#### Files created

```
src/cdfc/selfcheck/__init__.py
src/cdfc/selfcheck/witness.py        FaultWitness, apply(), observability by recalculation
src/cdfc/selfcheck/canary.py         the loop, the anti-canary, the run-level disposition
src/cdfc/selfcheck/selftest.py       P-SELFTEST-DEAD — always on, never behind a flag
src/cdfc/selfcheck/thresholds.py     CANARY_INAPPLICABLE_CEILING = 0.25, pre-registered
src/cdfc/selfcheck/timings.py        writes reports/perf/<run_id>.jsonl — OUTSIDE the hashed payload,
                                     outside run.jsonl, and outside everything `verify` compares
src/cdfc/surface/templates/_invalid_canary.html.j2    the INVALID replacement fragment (P14 renders it)
docs/SELFCHECK-THRESHOLDS.md
docs/measurements/P10-canary-cost.md   the measured wall-clock AND the §5.1 calibration curve:
                                       inapplicability rate at MAX_WITNESSES ∈ {1, 3, 5}, labelled
                                       "calibration surface, not an FFR corpus" (§0.3, F2/F44)
```

#### Public interface, verbatim

```python
# src/cdfc/selfcheck/witness.py
def apply(w: FaultWitness, facts: FactTable) -> FactTable: ...
    # returns a COPY. The received artifact is never touched, never re-serialised, never reopened.

def observability(w: FaultWitness, facts: FactTable, ev: Evaluator) -> Observability: ...
    # recalculate the affected cells with formula_source="FILING" (P9-B1's contract ruling):
    #   grids differ                                  -> OBSERVABLE
    #   grids identical, no not_run cell was touched   -> UNOBSERVABLE
    #   grids identical, a not_run cell WAS touched    -> INDETERMINATE   (adversary F18)
    # This is G2's O = G − U − I, applied to one mutant, at run time. It returns a three-valued
    # enum and NOT a bool, because a bool is where "we cannot see it" becomes "it is not there".

# src/cdfc/selfcheck/canary.py
CanaryFailureKind = Literal["PREDICATE_DID_NOT_FIRE", "WITNESS_MISSES_READ_SET",
                            "SELFTEST_NOT_SILENT", "WHOLESALE_INAPPLICABILITY",
                            "ANTI_CANARY_FIRED"]

Observability = Literal["OBSERVABLE", "UNOBSERVABLE", "INDETERMINATE"]   # §0.3, adversary F18

@dataclass(frozen=True, slots=True)
class CanaryRow:
    predicate_id: str
    witness_digest: str          # sha256 of the canonical FaultWitness
    observability: Observability # NOT a bool. INDETERMINATE == the recalculation touched a not_run cell
    intersects_read_set: bool
    fired: bool
    # NO DURATION FIELD. NO TIMESTAMP. NO perf_counter-DERIVED VALUE. EVER. See the ruling below.

@dataclass(frozen=True, slots=True)
class CanaryReport:
    rows: tuple[CanaryRow, ...]              # ONE PER ATTEMPT. The counts are len(), never a variable.
    anti_rows: tuple[CanaryRow, ...]
    inapplicable: tuple[str, ...]            # predicate ids with no observable witness on this filing
    indeterminate: tuple[str, ...]           # predicate ids whose only witnesses hit not_run cells
    silent: tuple[str, ...]
    selftest_silent: bool
    failure_kind: CanaryFailureKind | None

def run_canaries(filing: FactTable, predicates: Sequence[Predicate],
                 ev: Evaluator, passcase_facts: Mapping[str, FactTable]) -> CanaryReport: ...

def disposition(cr: CanaryReport) -> RunDisposition: ...
    # INVALID(invalid.canary_silent) if cr.silent or not cr.selftest_silent
    #        or cr.failure_kind == "ANTI_CANARY_FIRED"
    #        or (len(cr.inapplicable) + len(cr.indeterminate))/len(cr.rows)
    #            > CANARY_INAPPLICABLE_CEILING
    # else VALID, with the inapplicable AND indeterminate predicates' cells
    #             -> NOT_RUN(not_run.deactivated)
```

#### Timings live outside the hashed payload, and the evidence of execution stays inside it — **DECIDED**

**The defect (adversary F23, FATAL, and it would have fired on the first green run of P11).** `CanaryRow`
carried `elapsed_us: int` — a **wall-clock duration** — inside a structure whose canonicalised digest a
property test asserts to be order-invariant and whose contents feed `livenessProof` and `run.jsonl`. Two
runs produce different microsecond counts, therefore different bytes, therefore **`E2E-VERIFY` fails
permanently**. `plan/01` §1.5's enumeration of non-determinism sources — register, clock, iteration order,
float — does not contain *"durations we measured ourselves"*, and `ci/no-clock-in-core.sh` greps for
`datetime.now()`, `time.time()` and `TZ`, **not** for `perf_counter`.

**And the obvious fix is the dangerous one.** Deleting the field from the hash silently removes the evidence
that the canary loop *executed* rather than being replayed from a cache — which is death **D5**'s entire
concern, in the layer whose whole claim is that it ran.

> **RULING, and it keeps both halves.**
>
> 1. **Timings leave the payload entirely.** `selfcheck/timings.py` writes them to
>    `reports/perf/<run_id>.jsonl`, which is **not** in `run.jsonl`, **not** in the attestation, and **not**
>    in `make determinism`'s or `verify`'s comparison set. `PERF-CANARY2` reads them there.
> 2. **The evidence of execution stays, and it is deterministic.** `CanaryRow` retains `witness_digest`,
>    `observability`, `intersects_read_set` and `fired` — four fields, every one a function of the inputs —
>    and `canariesRun == len(cr.rows)` remains the assertion that answers D5. **A count of rows produced by
>    executions is stronger evidence of execution than a duration is**, because a cached replay can carry a
>    duration and cannot carry a per-witness digest it did not compute.
> 3. **The prohibition is structural, not a convention.**
>    `tests/contract/test_contract__no_duration_field_in_a_hashed_object` walks **every** dataclass that
>    reaches `canonical_json`, asserts no field name matches `(elapsed|duration|_us|_ms|_ns|seconds)`
>    case-insensitively, and asserts no field's value derives from `time.perf_counter`, `time.monotonic` or
>    `time.process_time`. **`ci/no-clock-in-core.sh`'s pattern set is extended to those three names** — the
>    grep that would have caught this and did not.
>
> *Alternative it beat:* keeping `elapsed_us` and quantising it (to milliseconds, or to a bucket). Rejected
> because a quantised duration is still a clock read, still varies across machines at the bucket boundary,
> and buys a number nobody needs inside a signature.

#### The loop, stated exactly

```
for each ACTIVE or PROVISIONAL predicate P (relations included — a relation is a predicate):
    for w in P.liveness.kill_cases:      # ordered, ≤ 3, diverse WITHIN P.claims_fault_classes (§0.2)
        obs = observability(w, filing.facts, evaluator)   # OBSERVABLE | UNOBSERVABLE | INDETERMINATE
        if obs != "OBSERVABLE":
            record CanaryRow(observability=obs); continue
        mutant = apply(w, filing.facts)                   # a COPY of the in-memory fact table
        fired  = (evaluate(P, mutant).state == "FAIL")
        record CanaryRow(observability="OBSERVABLE",
                         intersects_read_set = (w.target in P.read_set),
                         fired = fired)
        break                                             # the first observable witness is THE canary
    # anti-canary: the predicate must PASS on its pinned clean pass_case
    record anti CanaryRow(fired = (evaluate(P, passcase_facts[P.pass_case]).state != "PASS"))

silent          = {P : an observable witness was found and it did not fire}
inapplicable    = {P : every stored witness was UNOBSERVABLE on this filing}
indeterminate   = {P : no witness was OBSERVABLE and at least one was INDETERMINATE}
anti_fired      = {P : the predicate FAILed its own clean pass_case}
selftest_silent = (P-SELFTEST-DEAD ∈ silent)              # EXPECTED. Its absence is the alarm.
# NOTHING IN THIS LOOP READS A CLOCK. Timings are emitted by selfcheck/timings.py to
# reports/perf/<run_id>.jsonl, outside every hashed object (F23).
```

**Dispositions, complete:**

| Condition | Run state | Cause | `failure_kind` | Settled fraction |
|---|---|---|---|---|
| `silent ⊋ {P-SELFTEST-DEAD}` | **`INVALID`** | `invalid.canary_silent` | `PREDICATE_DID_NOT_FIRE` (or `WITNESS_MISSES_READ_SET` when `intersects_read_set` is false) | **`null`** |
| `not selftest_silent` | **`INVALID`** | `invalid.canary_silent` | `SELFTEST_NOT_SILENT` | **`null`** |
| `anti_fired ≠ ∅` | **`INVALID`** | `invalid.canary_silent` | `ANTI_CANARY_FIRED` | **`null`** |
| `(|inapplicable| + |indeterminate|) / |rows| > 0.25` | **`INVALID`** | `invalid.canary_silent` | `WHOLESALE_INAPPLICABILITY` | **`null`** |
| otherwise, `indeterminate ≠ ∅` | `VALID` | — | — | computed; those cells are `NOT_RUN(not_run.deactivated)`, **the fraction falls**, and `canariesIndeterminate` renders with the offending cells named. **It is never folded into `canariesInapplicable`**: one is a fact about the filing, the other a fact about our evaluator (F18) |
| otherwise, `inapplicable ≠ ∅` | `VALID` | — | — | computed; those cells are `NOT_RUN(not_run.deactivated)` and **the fraction falls** |
| otherwise | `VALID` | — | — | computed |

**`settledFraction` is `null` on every `INVALID` row above — not zero, not omitted, `null`.** Zero is a
finding about the filing; `null` is a finding about us, and the two must never be allowed to look alike.
`verdict` is `null` for the same reason: `SETTLEMENT_INSUFFICIENT` is a statement about the filing's residue
and this is a statement about our instrument.

#### `P-SELFTEST-DEAD` — always on, never behind an environment variable

`plan/01-validation-methodology.md` §2.5 NC-C01b seeds a dead predicate *"under `CDFC_CANARY_SELFTEST=1`"*.
**RULING: the flag is removed.** A self-test that runs only when a flag is set is a self-test that is off in
production, which is the failure this layer exists to catch, one level up.

```python
# src/cdfc/selfcheck/selftest.py
P_SELFTEST_DEAD = Predicate(
    id="P-SELFTEST-0001", kind="selftest",
    expr="true",                       # cannot be made to FAIL by any fault, by construction
    ...)
# Registry member. kind='selftest' => excluded from the settled numerator AND from every filer-facing
# surface. It settles no cell and appears in no item list. It exists to be silent.
```

Its expected outcome is **inverted**: the loop asserts it *is* silent. `silent == {P-SELFTEST-0001}` is
health; `silent ⊋ {…}` means a real predicate died; `silent ⊉ {…}` means **the loop is lying**, because a
predicate whose `expr` is `true` cannot fire and a loop that says it did is not running.

The attestation reports it separately so that a healthy run still shows `canariesRun == canariesPassed`:

```jsonc
"livenessProof": { "canariesRun": 280, "canariesPassed": 280,
                   "antiCanariesRun": 280, "antiCanariesPassed": 280,
                   "canariesInapplicable": 0, "canariesIndeterminate": 0,
                   "selfTestSilent": true }
// Every value is an integer computed as len() of a row set. There is no duration anywhere in this
// object, in run.jsonl, or in anything `verify` compares (F23).
```

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_witness.py::test_w__apply_returns_a_copy` | the input `FactTable` is unchanged after `apply`; identity comparison, not equality |
| `tests/unit/test_witness.py::test_w__observability_is_decided_by_recalculation` | a witness whose recalculated grid is identical **and touched no `not_run` cell** returns `UNOBSERVABLE`; the test uses a real FME cell that is 0 in the reference fill |
| `tests/unit/test_witness.py::test_w__notrun_cell_yields_INDETERMINATE_not_UNOBSERVABLE` | F18. A witness whose propagation path runs through `'1. Introduction'!D92` (the `_xlfn.SINGLE` cell, §0.6) returns `INDETERMINATE` and names the cell. Injector `injectors/notrun_counts_as_identical.py`; admission-side twin: a fully-evaluable path returns `OBSERVABLE` |
| `tests/unit/test_witness.py::test_w__fault_class_is_a_declared_claim_not_a_post_hoc_label` | F1. `FaultWitness(fault_class=...)` raises `UndeclaredFaultClass` when the class is not in the predicate's `claims_fault_classes`; and a witness set may not contain a class the predicate never claimed |
| `tests/unit/test_witness.py::test_w__observability_uses_filing_formulas` | F19. `observability()` calls `recalculate(..., formula_source="FILING")`; the `TEMPLATE` variant is asserted **absent** from `selfcheck/`'s call sites by the same AST scan as `test_contract__formula_source_is_explicit` |
| `tests/unit/test_witness.py::test_w__target_is_a_stable_key_not_a_coordinate` | a `FaultWitness` constructed with `"O7"` raises; only `StableKey` is accepted. **A coordinate witness silently rebinds on a row insertion (NC-D04's mechanism inside the self-check)** |
| `tests/unit/test_canary.py::test_c__counts_are_row_counts_not_variables` | `canariesRun == len(cr.rows)`; a hard-coded count fails |
| `tests/unit/test_canary.py::test_c__first_observable_witness_is_the_canary` | the loop stops at the first observable witness and records the skipped ones |
| `tests/unit/test_canary.py::test_c__witness_missing_the_read_set_is_a_distinct_kind` | `WITNESS_MISSES_READ_SET` ≠ `PREDICATE_DID_NOT_FIRE`. **Different remedies: fix the admission, versus fix the code.** Merging them is the SPDX `NOASSERTION` collapse in miniature |
| `tests/unit/test_selftest.py::test_st__selftest_settles_no_cell` | absent from `run_cell`, from `settledFraction`, and from every filer-facing surface |
| `tests/unit/test_thresholds.py::test_th__ceiling_is_pre_registered` | `CANARY_INAPPLICABLE_CEILING == 0.25` and a change without a `docs/SELFCHECK-THRESHOLDS.md` entry fails the build |
| `tests/unit/test_thresholds.py::test_th__indeterminate_counts_toward_the_ceiling` | the ceiling numerator is `inapplicable + indeterminate`; a build that pools only `inapplicable` fails (F18) |
| `tests/contract/test_contract__no_duration_field_in_a_hashed_object` | **F23, and it is the phase's cheapest structural gate.** Walk every dataclass reachable from `canonical_json`; no field name matches `(elapsed\|duration\|_us\|_ms\|_ns\|seconds)` case-insensitively, and no field value derives from `perf_counter` / `monotonic` / `process_time`. Companion: `ci/no-clock-in-core.sh` gains those three names to its pattern set |
| `tests/unit/test_timings.py::test_tim__timings_are_written_outside_the_payload` | `reports/perf/<run_id>.jsonl` exists and is non-empty after a run, **and** no byte of it appears in `run.jsonl`, `attestation.json` or `report.html`. **This is the half of the repair that keeps the evidence** — deleting the field without this test is how the timing data disappears entirely |

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **A silent canary is never absorbed.** For every multiset of `CanaryRow`s, `disposition` returns `INVALID` iff the silent set differs from `{P-SELFTEST-0001}`, or an anti-canary fired, or **`(inapplicable + indeterminate) / rows`** exceeds the ceiling | random `CanaryReport`s over 0–500 predicates, with the observability field drawn over all **three** values | `selfcheck/canary.py` |
| **No hashed object carries a clock reading.** For every generated `CanaryReport`, canonicalising it twice under different wall-clock times yields identical bytes; and the same report constructed on two machines yields identical bytes | random `CanaryReport`s, with `time.perf_counter` monkeypatched to a divergent stub | `selfcheck/canary.py` ⊕ `attest/canon.py` (F23) |
| **`INVALID` implies no fraction.** For every `INVALID` disposition, `settledFraction is None` **and** `verdict is None` | the same | `selfcheck/canary.py` |
| **Inapplicability lowers the fraction, monotonically.** Moving one predicate from applicable to inapplicable never raises the settled count | random runs with a fixed cell/predicate incidence matrix | `verdict/rollup.py` |
| **The loop is order-independent.** Shuffling the predicate order does not change the disposition or the digest of the canonicalised `CanaryReport` | random permutations | `selfcheck/canary.py` |

#### Validation — performance

| Budget id | Subject | Baseline | Fail above | Warn above |
|---|---|---:|---:|---:|
| `PERF-CANARY2` | 280 kill-case canaries **and** 280 anti-canaries over in-memory fact tables | **≈ 70 ms** (DERIVED from the measured 7,946 mutations/s) | 160 ms | 110 ms |

Supersedes `PERF-CANARY` (~35 ms), with the reason recorded in `perf/BUDGET-CHANGES.md`: the anti-canary was
added in §0.4 and doubles the loop. Against a ~30 ms deterministic core and a ≈450 ms complete online run,
**there is still no reason not to**, and `docs/measurements/P10-canary-cost.md` publishes the measured
figure rather than the derived one on the first green run.

---

### BUILD P10-B2 — THE RESIDUE PROCEDURE · 3 days (+3–5 person-days adjudication, parallel)

**What it produces.** `|RESIDUE|` — *the first quantitative statement anyone has made about the limit of
document-level verification for a regulated filing.*

#### Files created

```
src/cdfc/selfcheck/residue.py
src/cdfc/selfcheck/adjudication.py      the record format and its loader
src/cdfc/selfcheck/exhibit.py           survivor construction and rendering
cli: cdfc residue --filing <sha> --fault-model v3 --adjudication <sha>
docs/measurements/P10-residue.md
```

#### The procedure, verbatim from the spec, with the one thing the spec leaves implicit made explicit

```
1. Take the filing under test, F.
2. Generate mutants of F under the declared, versioned fault model (P6's harness, raw-zip surgery).
3. Adjudicate each INNOCUOUS or WRONG.                              <- THE ONLY HUMAN STEP
4. Run the full admitted predicate set AND every admitted relation over every WRONG mutant.
5. RESIDUE := { WRONG mutants that no predicate and no relation rejects }
6. Report |RESIDUE| and, per survivor, the class of falsehood it represents.
```

**Made explicit: step 4 runs the rejector set *as it is on the day the residue is computed*, and that set is
part of the result.** `|RESIDUE| = 12` against an empty admitted set and `|RESIDUE| = 12` against 280
admitted predicates are utterly different claims. The residue record therefore carries
`{fault_model_version, adjudication_record_sha256, registry_root, n_admitted_predicates,
n_admitted_relations}`, and **the renderer refuses to print `|RESIDUE|` without all five.**

#### Public interface

```python
# src/cdfc/selfcheck/residue.py
Verdict = Literal["INNOCUOUS", "WRONG"]

@dataclass(frozen=True, slots=True)
class ResidueResult:
    survivors: tuple[MutantId, ...]
    wrong_total: int                 # THE DENOMINATOR
    innocuous_total: int
    registry_root: str
    n_admitted_predicates: int
    n_admitted_relations: int
    fault_model_version: str
    adjudication_record_sha256: str

def compute_residue(filing: FactTable, mutants: Sequence[Mutant],
                    adjudication: AdjudicationRecord,
                    predicates: Sequence[Predicate]) -> ResidueResult: ...
```

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_residue.py::test_res__innocuous_leaves_the_denominator` | `wrong_total` excludes INNOCUOUS mutants. **They cannot be killed and must not be counted**, exactly as equivalent mutants must leave the code-mutation denominator |
| unit | `…::test_res__unadjudicated_mutant_raises` | a mutant with no adjudication row **raises**; it is never defaulted to either value |
| unit | `…::test_res__renderer_refuses_without_all_five_fields` | printing `|RESIDUE|` without the registry root or the adjudication hash fails |
| property | **Adding predicates cannot grow the residue.** For any predicate set `S ⊆ S'`, `RESIDUE(S') ⊆ RESIDUE(S)`. Generator: random rejector subsets over a fixed mutant population | `selfcheck/residue.py` |
| relational | `tests/relational/test_rel__residue_not_inflatable.py::test_residue_not_inflatable` | **adding 505 recompute predicates does not shrink the residue** — because the residue is populated by falsehoods consistent with every arithmetic relation in the file. The spec's own claim, mechanised |
| negative | **NC-C02** (existing) `test_nc__C02_coordinated_misstatement_survives` | the constructed survivor is rejected by nothing. **Its failure message must not say "assertion failed"; it must say: either the construction is wrong or a relation is stronger than we believed — investigate which, because both are findings** |
| determinism | `tests/determinism/test_det__residue_is_reproducible_from_three_hashes` | two runs from `{fault_model_version, adjudication_record_sha256, registry_root}` on different machines produce the **same survivor id set**, and the mutant population is regenerated deterministically from `{seed, fault_model_version, harness_version}` rather than read from a directory (methodology §6.2: mutants are not committed) |

**Performance.** The residue campaign is **offline**, per filing under adjudication, and is budgeted against
the measured harness throughput: `PERF-MUT` (7,946 mutants/s, fail below 5,000/s) applies unchanged. The
19,782-mutant campaign is **2.5 s (MEASURED)**; the human step is 3–5 person-days and is the real cost.

*New catalogue entry, and it is the one that keeps the human step honest:*

```yaml
- id: NC-C07
  component: selfcheck
  break: "|RESIDUE| is reported against a rejector set that is not named, so an empty registry looks like a strong result"
  measured_instance: "on G-CORPUS's FAIL branch the admitted set is empty and every WRONG mutant survives by construction"
  injector: residue_without_registry_root
  why_impossible: null
  guard_tests:
    - tests/unit/test_residue.py::test_res__renderer_refuses_without_all_five_fields
    - tests/negative/test_nc_selfcheck.py::test_nc__C07a_empty_registry_residue_is_labelled_a_ceiling
  positive_control: tests/negative/test_nc_selfcheck.py::test_nc__C07b_full_registry_residue_renders_the_root
  status: ACTIVE
```

---

### BUILD P10-B3 — THE ADJUDICATION RECORD AND ITS SECOND RATER · 2 days (+1 person-day)

**What it produces.** The property that makes `|RESIDUE|` reproducible by a stranger: *reproducible given
the published fault model **and the published adjudication record**, both content-addressed.* Saying "a
third party can re-run it" without naming the adjudication record would repeat the error this whole
specification exists to correct.

#### The record

```jsonc
// adjudication/<fault_model_version>/<filing_sha8>.jsonl   — one line per mutant, sorted by mutant_id
{"mutant_id":"sha256:…","verdict":"WRONG","argument":"scales one connected component of the carry graph
 by 1.10; every SUM identity and every cross-sheet carry remains satisfied; the reported total assets are
 materially overstated","adjudicated_by":"…","adjudicated_at":"2026-__-__","round":1}
```

`adjudication_record_sha256` is the RFC 8785 digest of the sorted file. **A verdict with no `argument`
is refused by the loader** — the same rule as `docs/EQUIVALENT-MUTANTS.md`, and for the same reason: an
adjudication without an argument is an opinion wearing a schema.

#### The κ arm, which is a *substitute measurement* and not a test

**NC-N02 records that the INNOCUOUS/WRONG adjudication cannot be negatively controlled** — injecting a wrong
label is trivial, but the *correct* label is the human's. The methodology's prescribed substitute is
implemented here: **a second adjudicator re-rates a random 20% and Cohen's κ is published with its `n`.**

- The 20% sample is drawn by a **seeded PRNG whose seed is written into the record before round 1 begins**.
  Drawn afterwards, the sample is a choice.
- `selfcheck/adjudication.py::cohens_kappa(round1, round2) -> tuple[float, int]` returns κ and `n`.
- **κ is published with `n` and never alone**, and `|RESIDUE|` renders beside it. A residue computed under
  κ = 0.4 is a different object from one computed under κ = 0.9, and the reader is entitled to know which.
- **There is no threshold on κ, and inventing one here would be the invention this document refuses.** The
  decision rule instead: *if κ < 0.6, the two raters reconcile in writing, the reconciliation is appended as
  round 3 with its own hash, and both the pre- and post-reconciliation κ are published.* Never a silent
  re-rate.

#### Validation

| Test | Asserts |
|---|---|
| `tests/unit/test_adjudication.py::test_adj__verdict_without_argument_is_refused` | loader raises |
| `tests/unit/test_adjudication.py::test_adj__record_is_content_addressed_over_sorted_lines` | shuffling line order does not change the digest (RFC 8785 + explicit sort) |
| `tests/unit/test_adjudication.py::test_adj__sample_seed_precedes_round_one` | from the record's own timestamps, exactly as `test_corpus__brief_predates_first_workbook` does for the fill brief. **A commitment made after seeing the result is not a commitment** |
| `tests/unit/test_kappa.py::test_kappa__perfect_agreement_is_one` and `::test_kappa__chance_agreement_is_zero` | the standard pair, with hand-computed vectors |
| negative | **NC-C02b** (existing) `test_nc__C02b_adjudication_record_is_content_addressed` | a residue reported without the record's hash fails to render |

---

### BUILD P10-B4 — THE DEMONSTRATED SURVIVORS · 1 day

**What it produces.** Exhibits, not reasons. The Unchecked panel's strongest row.

**Two families, and the second is this document's contribution.**

| Family | Construction | Why it is unkillable |
|---|---|---|
| **E1 — the coordinated misstatement** | scale every quantity in one connected component of the carry graph by the same factor | Internally perfect under **all 181 cross-sheet carries and all 35 SUM identities**. In code mutation a mutant that changes behaviour is in principle killable by *some* test; **here a mutant changes the *truth* of the artifact and is provably unkillable by any predicate over the artifact alone** |
| **E2 — the categorical swap inside the vocabulary** | change a categorical cell to another **legal** member of its own controlled vocabulary — e.g. `Dropdown!I3:I4 = {Open-Ended, Close-Ended}`, a **two-value** vocabulary | Passes every membership predicate **by construction**. And it lands in the **2,790 field-surface cells that feed no template formula at all (MEASURED, §0.1)**, so no recompute, carry or sum identity can reach it either. **A one-character edit that changes what the scheme *is* and that nothing in the artifact contradicts** |

E2 matters because E1 is a construction and E2 is a *measurement*: the 2,790-cell recompute-blind set was
computed from the regulator's own formula graph, and the swap is legal by the regulator's own validation.
The exhibit is hashed, carries `CDFC_SYNTHETIC = true`, and renders in the Unchecked panel as an exhibit
with its content hash — never as a reason.

#### Validation

| Test | Asserts |
|---|---|
| `tests/relational/test_rel__exhibit_e2.py::test_e2__categorical_swap_survives_every_admitted_check` | the full admitted set **and** every admitted relation return no rejection |
| `tests/relational/test_rel__exhibit_e2.py::test_e2__the_swap_is_legal_under_the_blank` | the swapped value **is** in the pinned blank's vocabulary — otherwise it would be killed by R-04 and the exhibit would be a bug report, not a residue member |
| `tests/golden/test_golden__recompute_blind_set.py::test_golden__2790_cells_feed_no_formula` | pins 2,790 of 3,747 with its per-sheet split; **paired value assertion**: a named cell in the set, and a named cell outside it |
| `tests/unit/test_exhibit.py::test_ex__exhibits_render_as_exhibits_not_reasons` | the Unchecked panel's exhibit block contains a content hash and a construction description, and **no reason code** |

---

## P10 · L — HOW WE PROVE THE CANARY LAYER ACTUALLY CATCHES A DEAD PREDICATE

**This section is the most important validation in the plan**, because the canary layer's entire claim is
that it catches this, and a test that has never been observed to fail is not evidence.

### L.1 The six deaths

Six mechanically injectable deaths, each a **different mechanism**, each with its own injector, each
producing `INVALID`. `make nc-sweep` asserts every one turns its guard red.

| # | Death | Injector / fixture | Must produce | What it proves that the others do not |
|---|---|---|---|---|
| **D1** | **The predicate cannot fire.** An admitted-shaped envelope whose `expr` is `true`, with a valid stored witness | `fixtures/predicates/broken/P-NC-C04a__cannot-fire.yaml` | `INVALID`, `PREDICATE_DID_NOT_FIRE`, the id named, `settledFraction is None` | that a dead *check* is caught |
| **D2** | **The witness cannot reach the predicate.** A healthy predicate whose stored witness targets a key outside its read set | `fixtures/predicates/broken/P-NC-C04b__witness-misses.yaml` | `INVALID`, **`WITNESS_MISSES_READ_SET`** — a **distinct** kind | that a dead *witness* is distinguished from a dead check. **Different remedies: re-qualify versus fix the code** |
| **D3** | **The apparatus is broken and binding is intact.** Four injectors, §0.5 | `keys_resolver_offbyone` · `facts_trailing_space` · `celrt_short_circuits` · `tolerance_widened` | `INVALID`, `PREDICATE_DID_NOT_FIRE`, **and the `invalid` cause set is exactly `{canary_silent}`** | **that the canary layer, and only the canary layer, made the catch** |
| **D4** | **The loop is a stub.** `canaries_passed == canaries_run` unconditionally | `injectors/canaries_noop.py` (NC-C01, amended) | `INVALID`, `SELFTEST_NOT_SILENT` | that the loop is running at all. **This is the canary for the canary loop** |
| **D5** | **The counts are asserted, not counted.** `canariesRun := len(predicates)` rather than `len(rows)` | `injectors/canary_count_asserted.py` | the run-level self-test relation **R-06** fails ⇒ `INVALID` | that the *numbers in the attestation* came from executions. A loop that runs and reports a number it did not compute is a lie with a true premise |
| **D6** | **The canary touches the file.** the loop re-opens or re-serialises the artifact | `injectors/canary_reopens_file.py` | `test_nc__C01c` red; the import-closure walk fails the build | that liveness is proved **on the in-memory fact table**, so the attested hash still hashes the filing (ties to NC-P04) |

### L.2 The two properties that make the six mean something

**L.2.1 — Cause isolation.** `tests/negative/test_nc_selfcheck.py::test_liveness__only_cause_is_canary_silent`
runs each of D1, D2 and D3's four injectors and asserts the run's `invalid` cause set is **exactly**
`{canary_silent}`. A control that also trips `invalid.cells_bound_zero`, `invalid.template_unbound`,
`invalid.reader_structural_disagreement` or `invalid.closure_violated` **proves nothing about canaries** —
another layer caught it. This is the mechanised form of §0.5's correction, and it is the single assertion a
reviewer should look for first.

**L.2.2 — The admission-side positive control, without which all six are satisfied by a layer that returns
`INVALID` unconditionally.** `tests/relational/test_rel__canary_positive.py`:

- `test_canary__healthy_run_is_VALID` — the FME reference fill against the real registry yields `VALID`,
  `canariesPassed == canariesRun == n`, `antiCanariesPassed == antiCanariesRun == n`,
  `canariesInapplicable == 0`, `selfTestSilent == true`, and a **rendered settled fraction with digits**.
- `test_canary__a_real_fault_still_FAILs_and_the_run_stays_VALID` — a filing with one seeded fault yields
  `FAIL` on exactly the predicates reading that cell **and `run_state == VALID`**. **A layer that cannot
  tell a broken instrument from a broken filing has destroyed the distinction the whole product sells.**
- `test_canary__inapplicable_below_the_ceiling_stays_VALID` — a sparsely-filled but lawful filing with
  inapplicable canaries below 0.25 returns `VALID` with a **lower** settled fraction, not `INVALID`.

### L.3 The negative-control catalogue entries this section creates

```yaml
- id: NC-C03
  component: selfcheck
  break: "a renamed sheet is credited to the canary layer when the template binder actually caught it"
  measured_instance: "F3 binds by structural fingerprint over (sheet names + states, dimensions, merged ranges, defined names, unlocked mask); a renamed sheet changes the fingerprint five steps before F10 runs"
  injector: NONE
  why_impossible: "the fixture is the artifact and the binder is correct; there is nothing to break. The control is an ASSERTION about which cause fires, not an injection"
  guard_tests:
    - tests/negative/test_nc_selfcheck.py::test_nc__C03_renamed_sheet_is_template_unbound_not_canary_silent
  positive_control: tests/negative/test_nc_selfcheck.py::test_nc__C04a_apparatus_break_is_canary_silent
  layer_exists_assertion: "IN THE SAME TEST BODY, before the renamed-sheet assertion: run the FME reference
    fill and assert canariesRun > 0. NC-C03 asserts a layer did NOT fire; it must therefore prove, in the
    same breath, that the layer exists (adversary F6)"
  status: ACTIVE

- id: NC-C04
  component: selfcheck
  break: "an apparatus break that leaves template binding, reader agreement, closure and cells_bound intact goes undetected"
  measured_instance: null
  injector: keys_resolver_offbyone
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_selfcheck.py::test_nc__C04a_apparatus_break_is_canary_silent
    - tests/negative/test_nc_selfcheck.py::test_liveness__only_cause_is_canary_silent
  positive_control: tests/relational/test_rel__canary_positive.py::test_canary__healthy_run_is_VALID
  status: ACTIVE

- id: NC-C05
  component: selfcheck
  break: "a stored kill case is a workbook that is transplanted into another filing's fact table"
  measured_instance: "spec §II.4.1 stores a path; spec §II.6.2's mechanism applies the kill case to THIS filing's facts. The two cannot both be right"
  injector: witness_from_artifact
  why_impossible: null
  guard_tests:
    - tests/unit/test_witness.py::test_w__target_is_a_stable_key_not_a_coordinate
    - tests/negative/test_nc_selfcheck.py::test_nc__C05c_no_artifact_is_opened_during_the_canary_loop
  positive_control: tests/unit/test_witness.py::test_w__observability_is_decided_by_recalculation
  status: ACTIVE

- id: NC-C06
  component: selfcheck
  break: "an inapplicable witness is scored as a passed canary"
  measured_instance: null
  injector: inapplicable_counts_as_pass
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_selfcheck.py::test_nc__C06a_inapplicable_is_not_a_pass
    - tests/property/test_prop_canary.py::test_prop__inapplicability_lowers_the_fraction
  positive_control: tests/relational/test_rel__canary_positive.py::test_canary__inapplicable_below_the_ceiling_stays_VALID
  status: ACTIVE

- id: NC-C08
  component: selfcheck
  break: "the predicate has drifted to flagging everything, and every kill-case canary still fires"
  measured_instance: "SPADE: selecting ALL generated candidates yields 100% coverage and 100% FFR"
  injector: anticanary_skipped
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_selfcheck.py::test_nc__C08a_always_flag_predicate_fails_its_pass_case
    - tests/unit/test_canary.py::test_c__counts_are_row_counts_not_variables
  positive_control: tests/relational/test_rel__canary_positive.py::test_canary__healthy_run_is_VALID
  status: ACTIVE

- id: NC-C09
  component: selfcheck
  break: "the canary self-test is behind an environment variable, so it is off in production"
  measured_instance: "plan/01-validation-methodology.md §2.5 NC-C01b specifies CDFC_CANARY_SELFTEST=1"
  injector: selftest_behind_a_flag
  why_impossible: null
  guard_tests:
    - tests/negative/test_nc_selfcheck.py::test_nc__C09a_selftest_runs_with_no_environment_set
    - tests/unit/test_selftest.py::test_st__selftest_settles_no_cell
  positive_control: tests/relational/test_rel__canary_positive.py::test_canary__healthy_run_is_VALID
  status: ACTIVE

- id: NC-C10
  component: selfcheck
  break: "a wall-clock duration is inside a canonicalised, hashed object, so byte-identity is unreachable -- and the quiet repair deletes the evidence that the loop executed"
  measured_instance: "CanaryRow carried elapsed_us: int inside the structure whose digest feeds livenessProof and run.jsonl; ci/no-clock-in-core.sh greps datetime.now/time.time/TZ and not perf_counter (adversary F23)"
  injector: elapsed_us_in_canary_row
  why_impossible: null
  guard_tests:
    - tests/contract/test_contract__no_duration_field_in_a_hashed_object
    - tests/determinism/test_det__attestation_bytes_identical
    - tests/unit/test_timings.py::test_tim__timings_are_written_outside_the_payload
  positive_control: tests/unit/test_canary.py::test_c__counts_are_row_counts_not_variables
  status: ACTIVE

- id: NC-C11
  component: selfcheck
  break: "a witness whose propagation path runs through a cell the evaluator cannot compute is scored UNOBSERVABLE, so our evaluator's coverage is reported as the fault's invisibility"
  measured_instance: "'1. Introduction'!D92 carries _xlfn.SINGLE, which is outside the eight-function vocabulary the spec fixes; it sits inside G-EVAL's own positive-control range (MEASURED 11 Aug 2026, §0.6)"
  injector: notrun_counts_as_identical
  why_impossible: null
  guard_tests:
    - tests/unit/test_witness.py::test_w__notrun_cell_yields_INDETERMINATE_not_UNOBSERVABLE
    - tests/unit/test_thresholds.py::test_th__indeterminate_counts_toward_the_ceiling
  positive_control: tests/unit/test_witness.py::test_w__observability_is_decided_by_recalculation
  status: ACTIVE
```

**`NC-C03` carries `injector: NONE` with a mandatory `why_impossible`, and the sweep reports it in the
`NONE` column rather than silently.** It is not an injection; it is an assertion about *which* cause fires,
and pretending otherwise would inflate the `caught / active` figure with an entry that catches nothing.

**And NC-C03 needed one more thing, which the adversary pass (F6) supplied: as written it is satisfied by a
build in which `src/cdfc/selfcheck/` does not exist at all.** *"The renamed sheet produced
`template_unbound` and not `canary_silent`"* is trivially true of a system with no canary layer. Naming
NC-C04 as its positive control is not enough, because the two are separate catalogue rows that go red and
green independently, and a phase gate reading `caught == active` will not notice that NC-C03 alone is
vacuous.

> **RULING.** `test_nc__C03_renamed_sheet_is_template_unbound_not_canary_silent` **runs the FME reference
> fill first, in the same test body, and asserts `livenessProof.canariesRun > 0`** before it touches the
> renamed-sheet fixture. A test that proves a layer did *not* fire must, in the same breath, prove the layer
> exists. The catalogue shape carries this as `layer_exists_assertion`, and
> `test_nc_meta__none_injector_entries_carry_a_layer_exists_assertion` requires the field on **every**
> `injector: NONE` row whose claim is that some layer did not fire — which is the general form, and it is
> two lines of meta-test.

### L.4 Where the recursion stops, stated rather than hidden

`P-SELFTEST-DEAD` is the canary for the canary loop. **Nothing watches the seeding of `P-SELFTEST-DEAD`
itself.** If the registry loader silently drops `kind='selftest'` members, the loop reports
`selftest_silent == false`... and that is caught, because the disposition treats a non-silent self-test as
`INVALID`. If instead the loader drops it *and* the disposition's expected set is computed from the loaded
registry rather than from a constant, the expected set becomes empty, the observed set is empty, and the run
goes green. **That specific hole is closed by one line and no more:** the expected-silent set is a
**module-level constant**, `EXPECTED_SILENT = frozenset({"P-SELFTEST-0001"})`, never derived from the loaded
registry, asserted by `tests/unit/test_selftest.py::test_st__expected_set_is_a_constant`.

**One more layer would move the problem one layer, and we stop here deliberately and say so**, rather than
adding a layer and implying the regress is closed. §4.2 states what that costs.

---

## P10 · The measurement this phase produces

**Primary — `|RESIDUE|`:** the count of WRONG mutants that no admitted predicate and no admitted relation
rejects, with its **fault-model version**, its **adjudication-record hash**, its **registry root**, the
**count of admitted predicates and relations** it was computed against, and **each survivor's class of
falsehood.** Denominator: **the WRONG mutants generated.** Warrant **MEASURED**.

*This is the first quantitative statement anyone has made about the limit of document-level verification for
a regulated filing.*

**Supporting numbers, none of which exist today:**

| Number | Denominator | Warrant |
|---|---|---|
| Cohen's κ between two adjudicators on a pre-seeded 20% sample | mutants re-rated | MEASURED |
| Measured canary + anti-canary wall-clock on the reference run | ms, against a ~30 ms core | MEASURED, replacing the ≈70 ms DERIVED figure |
| Canary inapplicability rate on the reference template-computed clean filing — **a calibration surface, explicitly not an FFR corpus (§0.3, F2)** | canaries attempted | MEASURED — **expected 0**, and any other value is evidence about us |
| **Canary *indeterminacy* rate** — witnesses whose observability could not be decided because the recalculation touched a `not_run` cell, with those cells named | canaries attempted | MEASURED — **a property of our evaluator, published as one and never pooled into inapplicability** (F18) |
| `MAX_WITNESSES` calibration curve — inapplicability at `MAX_WITNESSES ∈ {1, 3, 5}` | canaries attempted, per setting | MEASURED — §5.1's decision rule, budgeted in B1's 0.5 extra day (F44) |
| Deaths caught / deaths injected | **6** | MEASURED — and it is the number the whole layer's claim rests on |

## P10 · Exit gate — this is gate **G-LIVENESS**

Evaluable by someone who did not do the work:

1. **All six deaths of §P10·L.1 produce `INVALID`**, each naming the dead predicate(s), each with
   `settledFraction is None` and `verdict is None` — **not zero, not omitted, `null`.**
2. **`test_liveness__only_cause_is_canary_silent` is green** for D1, D2 and D3's four injectors: the
   `invalid` cause set is exactly `{canary_silent}`.
3. **The three positive controls of §P10·L.2.2 are green** — a healthy run is `VALID` with digits; a seeded
   fault `FAIL`s and the run stays `VALID`; sub-ceiling inapplicability stays `VALID` with a lower fraction.
4. `test_nc__C03` is green: **the renamed-sheet fixture is `invalid.template_unbound`**, and the canary
   layer is not credited for it.
5. **`|RESIDUE| > 0`**, with **at least one survivor from each of the two exhibit families** (E1 the
   coordinated misstatement, E2 the categorical swap), each content-addressed and rendered as an exhibit.
6. `test_residue_not_inflatable` green — adding 505 recompute predicates does not shrink the residue.
7. κ published with its `n`; if κ < 0.6, the written reconciliation exists and both κ values are published.
8. `PERF-CANARY2` measured and recorded in `perf/baseline.ci.json`, **read from `reports/perf/<run_id>.jsonl`
   and not from any hashed object**; `test_contract__no_duration_field_in_a_hashed_object` and
   `test_tim__timings_are_written_outside_the_payload` are both green (F23).
9. `canariesIndeterminate` is rendered beside `canariesInapplicable` in `livenessProof`, and
   `test_th__indeterminate_counts_toward_the_ceiling` is green (F18).
10. `test_nc__C03` proves the canary layer **exists** (`canariesRun > 0` on the reference fill) in the same
    test body in which it proves the layer did not fire (F6).
11. `docs/measurements/P10-canary-cost.md` publishes the `MAX_WITNESSES ∈ {1,3,5}` curve, and
    `MAX_WITNESSES` is either closed by it or still renders `PROVISIONAL` in code (§5.1, F44).

## P10 · What it kills if it fails

- **If the canaries cannot be demonstrated to catch a dead predicate, the design's boldest claim is false
  and L6.5 is deleted.** The report carries no `livenessProof`; the attestation drops the field (and its
  JSON Schema drops it, so nothing can write it back); and the surfaces say plainly, in words, that **the
  instrument's liveness on this document is not demonstrated**. *The rest of the system is unaffected* —
  harvest, gate, closure, residue, probes, attestation and `verify` all stand. It is a smaller product and
  it is still the only one in its category that declares its own residue.
- **If the residue comes back empty**, that contradicts a structural argument and means **the fault model is
  too weak — not that the class is empty.** The response is to strengthen the fault model, and the report
  says `|RESIDUE| = 0 under fault model v3` **with the operator list attached**, never `|RESIDUE| = 0`.
  §0.1's 2,790-cell recompute-blind measurement makes an empty residue very hard to reach honestly, which is
  the point of having measured it before the campaign ran.
- **If κ is low and the raters cannot reconcile**, `|RESIDUE|` ships **with κ printed beside it** and a
  sentence saying the count inherits an adjudication disagreement of that size. A number with a declared
  weakness is admissible; a number with an undeclared one is the thing we are against.
- **If the anti-canary proves unaffordable** (the pass-case fact-table cache cannot be made deterministic),
  drop the anti-canary, keep the kill-case canary, and **state in the attestation that always-flag drift is
  not checked at run time.** The `livenessProof` object then omits the `antiCanaries*` fields — omission is a
  schema violation elsewhere, so here the fields become explicitly `null`, meaning *we make no claim*.

---
---

# P11 — L7: ATTESTATION, `verify`, BYTE IDENTITY

**Effort: 10 engineer-days** · B1 4 · B2 4 · B3 2
*Assumption:* one competent engineer, ~6 productive hours/day, comfortable with JSON Schema, RFC 8785 and
Ed25519, and willing to treat "byte-identical" as a claim to be broken rather than a box to tick.

## P11 · What it settles

**Whether a third party on another machine re-derives the report byte-for-byte.** *If it does not reproduce,
it does not ship.*

And a second thing, which is a property of the schema rather than of the run: **whether an all-clear can be
made unwritable.** A surface that can render all-clear will eventually render it wrongly, and prohibiting it
in the schema is the only version of that commitment that is a system property rather than a preference.

## P11 · Entry criteria

| Build | Requires | Why the edge is real |
|---|---|---|
| **B1** | **P10 complete** | The statement carries `livenessProof{canariesRun, canariesPassed, antiCanariesRun, antiCanariesPassed, canariesInapplicable, selfTestSilent}`. **There is nothing to sign until the canaries run** |
| **B1** | **P8 evaluated, either way** | The FFR fields are `null` with `corpusProvenance: "SELF-AUTHORED"` on the FAIL branch. That is a *schema* requirement, not a rendering one, and it must be in the schema before the first envelope is signed |
| **B1** | **P9 complete** | `counterEvidence[]` carries relation rejections; `residue` carries P10-B2's five fields |
| **B2** | **B1 complete** and **P5's manifest stable** | `verify` re-runs the pipeline from the manifest's eight pins. A moving manifest is a moving acceptance test |
| **B3** | **B1 complete** | A projection projects a statement |

## P11 · Builds

---

### BUILD P11-B1 — THE STATEMENT, THE SCHEMA AND THE ENVELOPE · 4 days

#### Files created

```
src/cdfc/attest/__init__.py
src/cdfc/attest/canon.py                      RFC 8785 canonicalisation, integers only
src/cdfc/attest/statement.py                  the in-toto Statement v1 builder
src/cdfc/attest/dsse.py                       DSSE, local Ed25519, keyed mode
src/cdfc/attest/schema/attestation.schema.json
src/cdfc/attest/schema/NAME-ALLOWLIST.md      every admitted near-banned property name, with its argument
tests/contract/schema_walk.py                 the recursive walker (methodology §1.9)
docs/measurements/P11-byte-identity.md
```

#### The statement, and the fields that are absent by design

`_type: https://in-toto.io/Statement/v1` · `subject[] = filing ⊕ template` — **both**, because a verdict
against template v3 is meaningless if the entity filed on v4 · `predicateType:
https://<ns>/filing-settlement-attestation/v1`.

**The top-level object of the predicate is `scope`. There is no `result`, no `status` and no `pass` field at
any depth, and there never will be.** The four statement fields — bounded silence, purpose,
`summaryIsNotSubstitute`, and the detection boundary — are **`required` by schema**, not template strings:
making a disclaimer a mandatory field rather than a template string is the cheapest possible way to
guarantee it survives contact with a marketing page.

`NONE ≠ NOASSERTION ≠ absent` is enforced by the schema: **`[]` means *we determined there are none*,
`null` means *we make no claim*, and an omitted field is a violation the validator rejects.**

#### The name prohibition, and the precision it needs — **DECIDED**

The recursive walker forbids a property named
`result | status | pass | passed | passing | compliant | conformant | ok | success | clean` at any depth,
case-insensitive, descending `properties`, `$defs`, `definitions`, `allOf`, `anyOf`, `oneOf`, `not`,
`items`, `prefixItems`, `patternProperties`, `additionalProperties` and `propertyNames`.

**The spec's own payload contains `canariesPassed`.** A substring matcher rejects the specification. An
exact matcher admits `overallStatus`. Neither is acceptable, so the rule has three parts:

1. **Exact, case-insensitive match on the property name** is the **blocking** gate.
2. **A substring scan over every property name is ADVISORY and prints its hits** on every run, so
   `overallStatus` cannot arrive unseen.
3. **Every advisory hit must appear in `NAME-ALLOWLIST.md` with a written argument, or the build fails.**
   The argument for the only current entry: *`canariesPassed` is a count of executions of our own
   instrument. It cannot be read as a verdict about the filing, because it is bounded by `canariesRun` and a
   run in which it equals `canariesRun` is exactly a run in which we have made **no** claim about the filing
   at all.* Same discipline as `docs/EQUIVALENT-MUTANTS.md`: an allowlist entry without an argument is
   refused by the loader.

#### Signing

**The filer signs, with a detached Ed25519 key, over the canonicalised payload. The vendor signs nothing and
appears only as `assessor.id` with `thirdParty: false`.** `--tlog-upload=false` is asserted in a test and the
keyless code path is unreachable — a keyless signature puts *the fact and timing of a named FME running a
pre-submission compliance check* into a permanent public transparency log.

**Until the open legal review returns (spec §III.7 C21), the demo signs a synthetic filing with a demo key
and the report says so on its face** — rendered from `surface/openitems.py`, with its age, not as silence.

#### Validation — contract, and this is the phase's centre of gravity

| Test | Asserts |
|---|---|
| `tests/contract/test_contract__attestation_cannot_express_a_pass` | the recursive walk finds no banned name at any depth (NC-A01) |
| `tests/contract/test_contract__banned_names_are_exact_not_substrings` | `canariesPassed` validates; a property literally named `passed` does not |
| `tests/contract/test_contract__every_advisory_hit_is_allowlisted_with_an_argument` | the advisory scan's hit set equals `NAME-ALLOWLIST.md`'s key set, and every entry has a non-empty argument |
| `tests/contract/test_contract__additional_properties_false_everywhere` | **every** object schema, including inside `$defs` |
| `tests/contract/test_contract__top_level_is_scope` | and `test_contract__four_statements_required` |
| `tests/contract/test_contract__absent_empty_null_are_distinct` | `[]` vs `null` vs omitted, per field |
| `tests/contract/test_contract__no_json_float_in_the_payload` | §0.7. No `.`, `e` or `E` inside any JSON number token of the canonicalised bytes |
| `tests/contract/test_contract__invalid_carries_a_null_not_an_absence` | **F24, and it replaces `test_contract__invalid_run_carries_no_fraction`, which asserted the opposite of what `plan/03` P5-B4 and `plan/01` §1.9 assert.** See the ruling immediately below |

#### `settledFraction` on an `INVALID` run — one rule, stated once — **DECIDED**

**Three documents asserted three different things about one field in one state (adversary F24).** `plan/03`
P5-B4 returns `SettledFraction | None`, i.e. the property is **present and `null`**. This build's contract
test said the schema **forbids** the property. `plan/01` §1.9 says an **omitted** field is a schema
violation. `null`, `forbidden` and `omitted` are three different things; P5 and P11 each pass their own
contract test and the integration produces an attestation that either fails validation or drops the `null`
that `E2E-INVALID` exists to assert.

> **RULING: on `INVALID`, `settledFraction` is PRESENT and `null`. Same for `verdict`.** The JSON Schema
> `if/then` is written as a **constraint on the value**, never as a prohibition on the property:
>
> ```jsonc
> { "if":   { "properties": { "runState": { "const": "INVALID" } }, "required": ["runState"] },
>   "then": { "properties": { "settledFraction": { "const": null },
>                             "verdict":         { "const": null } },
>             "required": ["settledFraction", "verdict"] } }
> ```
>
> *Reason:* the plan's own `NONE ≠ NOASSERTION ≠ absent` rule already fixes the meanings — `null` is *we
> make no claim*, and an absent field is a violation. **`INVALID` is precisely the state in which we make no
> claim**, so `null` is the only value that says the true thing, and forbidding the property would make the
> one state we most need to express indistinguishable from a malformed statement. Zero is a finding about
> the filing; `null` is a finding about us; **absence is a bug.**
>
> `test_contract__invalid_carries_a_null_not_an_absence` asserts all three legs: the property is present,
> its value is `null`, and a statement omitting it **fails** validation. `E2E-INVALID` asserts the same
> three on a real run.

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **Canonicalisation is order-invariant.** Shuffling dict insertion order does not change the digest | random JSON trees over the payload's type set (integers, strings, arrays, objects, `null`, booleans) | `attest/canon.py` |
| **Canonicalisation is injective on our payload set.** Two structurally different statements never canonicalise to the same bytes | random statements | `attest/canon.py` |
| **Ed25519 is deterministic.** The same payload and key produce the same 64 signature bytes | random payloads | `attest/dsse.py` |
| **`expires` is a pure function of `timeVerified`.** For every input, `expires == timeVerified + POLICY_VALIDITY` and **no clock is read** | random ISO-8601 instants | `attest/statement.py` |

**The `expires` property is easy to under-rate and is a real byte-identity hazard**: `timeVerified` is an
*input recorded in the manifest*, and `expires` must be derived from it, never from `datetime.now()`. The
spec's own example (`2026-08-14 → 2026-11-14`) implies a 92-day policy constant; the constant lives in
`attest/policy.py` and is pinned in the manifest through `code_git_sha`.

#### Validation — negative controls

*Existing entries relied on:* **NC-A01** (the attestation can be made to express a pass, with its
`schema_status_deep` injector that plants `status` inside a `$defs` entry referenced from an `allOf` two
levels down), **NC-A04** (a model client importable from the verdict path — `test_no_model_in_verdict_path`
covers `cdfc.attest`), **NC-A03** (the report does not re-derive).

*New entries:*

```yaml
- id: NC-A16
  component: attest
  break: "a float in the payload makes the canonicalisation implementation-dependent"
  measured_instance: "spec §II.5.1's example payload carries rate 0.021 and wilson [0.006, 0.074] while spec §III.4.5 states there is no floating point"
  injector: float_rate_in_payload
  why_impossible: null
  guard_tests:
    - tests/contract/test_contract__no_json_float_in_the_payload
    - tests/property/test_prop_canon.py::test_prop__canonicalisation_is_order_invariant
  positive_control: tests/contract/test_contract__ffr_renders_from_integers
  status: ACTIVE

- id: NC-A17
  component: attest
  break: "the name prohibition is implemented as a substring scan and rejects canariesPassed, or as an exact scan and admits overallStatus"
  measured_instance: "the spec's own livenessProof object contains canariesPassed"
  injector: banned_names_substring_only
  why_impossible: null
  guard_tests:
    - tests/contract/test_contract__banned_names_are_exact_not_substrings
    - tests/contract/test_contract__every_advisory_hit_is_allowlisted_with_an_argument
  positive_control: tests/contract/test_contract__attestation_cannot_express_a_pass
  status: ACTIVE

- id: NC-A18
  component: attest
  break: "expires is computed from the wall clock instead of from timeVerified"
  measured_instance: null
  injector: expires_from_now
  why_impossible: null
  guard_tests:
    - tests/property/test_prop_statement.py::test_prop__expires_is_a_function_of_time_verified
    - tests/determinism/test_det__attestation_bytes_identical
  positive_control: tests/unit/test_statement.py::test_stmt__expires_is_92_days_after_time_verified
  status: ACTIVE
```

---

### BUILD P11-B2 — `verify`, AND BYTE IDENTITY · 4 days

**What it produces.** The programme's acceptance test, as a command.

#### Files created

```
src/cdfc/attest/verify.py
cli: cdfc verify <report.html | attestation.json> [--blobs <dir>]
docs/measurements/P11-byte-identity.md
docs/NON-DETERMINISM.md      the enumerated sources, and which are removed
```

#### Public interface

```python
# src/cdfc/attest/verify.py
@dataclass(frozen=True, slots=True)
class VerifyResult:
    reproduced: bool
    diffs: tuple[Diff, ...]          # (artifact, byte_offset, expected, actual) — NAMED, never a bool
    signature_valid: bool | None     # None when no public key is present in the envelope
    manifest_pins_checked: tuple[str, ...]

def verify(artifact: Path, blobs: BlobStore) -> VerifyResult: ...
```

#### What `verify` re-derives, and what it cannot

It re-runs the pipeline pinned to the manifest's **eight** things:
`{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha, evaluator_version,
fault_model_version, tool_versions{python, lxml, openpyxl, celpy, z3}}` — plus the two run-level inputs the
probe layer added, `probe_seed` and `timeVerified`, both of which are **inputs recorded in the manifest**
rather than values read at run time.

**`libreoffice` is deliberately absent from that list because it is not on the verdict path**, and
`test_no_libreoffice_online` asserts it.

**The precision that must not be lost:** a third party does **not** have the filer's private key, so
`verify` proves two different things and reports them separately:

| Claim | How | Reported as |
|---|---|---|
| the **payload** re-derives byte-identically | re-run and compare | `reproduced: true/false` with named diffs |
| the **signature** is valid over that payload | Ed25519 verify against the public key in the envelope | `signature_valid: true/false/null` |

**`verify` never re-signs.** A tool that re-signs to compare signatures would report a mismatch whenever the
key differs and a match whenever it does not, and neither answer is about the report.

#### The four sources of non-determinism, removed rather than tolerated

| Source | Removal | Test | Injector |
|---|---|---|---|
| the mutable register | `register_snapshot_sha256`; the host function never resolves live at verdict time | `test_det__register_from_snapshot_only` | `live_register` |
| wall-clock | every timestamp is an input in the manifest; CEL binds no clock; `expires` derives from `timeVerified` | `test_det__no_clock_in_verdict` | `now_in_renderer`, `expires_from_now` |
| iteration order | RFC 8785 for hashes, explicit sort keys everywhere, findings sorted by `(sheet_index, row, column)` | `test_det__hash_seed_invariant` | `unsorted_rollup` |
| floating point | there is none — money is `int64 MILLI_USD_MILLION`, tolerances are integers, **and rates are integer ppm (§0.7)** | `test_det__no_float_on_verdict_path` | `float_money`, `float_rate_in_payload` |
| **durations we measured ourselves** *(added by the adversary pass, F23)* | no hashed object carries a duration, a timestamp or a `perf_counter`-derived value; timings are written to `reports/perf/<run_id>.jsonl`, outside `run.jsonl`, the attestation, the report and `verify`'s comparison set | `test_contract__no_duration_field_in_a_hashed_object`, `test_tim__timings_are_written_outside_the_payload` | `elapsed_us_in_canary_row` |

**A fifth, added by P9 and easy to miss:** the probe layer is a *search*. `probe_seed` is an input.
`test_det__probe_results_are_seed_stable` (P9-B3) is therefore a P11 dependency.

**A sixth, and it is the one the enumeration itself missed.** `plan/01` §1.5 lists register, clock,
iteration order and float; **it does not list durations we measured ourselves**, and
`ci/no-clock-in-core.sh` greps `datetime.now()`, `time.time()` and `TZ` but not `perf_counter`,
`monotonic` or `process_time`. `CanaryRow.elapsed_us` therefore sat inside the canonicalised payload
through six phases of review and would have failed `E2E-VERIFY` on the **first green run of P11**. The three
names are added to the grep's pattern set at P0 (`ci/GATES.md` records the widening with its date), and
`docs/NON-DETERMINISM.md` lists **six** sources enumerated and six removed. **An enumeration that was
complete until someone measured something is the standing hazard here, which is why the *contract* test —
"no duration field in a hashed object" — is the load-bearing artifact rather than the grep.**

#### Validation — end-to-end

| Flow | Command | Asserts |
|---|---|---|
| `E2E-VERIFY` | `cdfc verify reports/<run>/report.html` on a **second runner image** | `REPRODUCED`, byte-identical `report.html`, `attestation.json` and `run.jsonl` |
| `E2E-TAMPER` | flip one byte of the filing, re-verify | **a named diff, not `REPRODUCED`** — and the diff names the artifact and the offset |
| `E2E-INVALID` | `cdfc demo --break-parser` (now an **apparatus** break per §0.5, not a renamed sheet) | `INVALID`, dead predicates named, **`settledFraction` is `null`** — not 0, not omitted |
| `E2E-TAMPER-ATTEST` | flip one byte of `attestation.json` | `signature_valid: false` **and** `reproduced: false`, reported as two separate facts |

`make determinism` runs the FME pipeline twice under `TZ=Pacific/Kiritimati` vs `TZ=UTC`,
`PYTHONHASHSEED=0` vs `1`, `LC_ALL=C` vs `en_IN.UTF-8` and two working directories, then CI runs
`cdfc verify` on a second runner image.

*New catalogue entry:*

```yaml
- id: NC-A19
  component: attest
  break: "verify re-signs the payload instead of verifying the stored signature, so a key change reads as a report change"
  measured_instance: null
  injector: verify_resigns
  why_impossible: null
  guard_tests:
    - tests/e2e/test_e2e__verify.py::test_e2e__TAMPER_ATTEST_separates_signature_from_payload
    - tests/unit/test_verify.py::test_v__verify_never_calls_sign
  positive_control: tests/e2e/test_e2e__verify.py::test_e2e__VERIFY_byte_identical
  status: ACTIVE
```

---

### BUILD P11-B3 — THE DECLARED-LOSSY PROJECTIONS · 2 days

#### Files created

```
src/cdfc/attest/projections/__init__.py
src/cdfc/attest/projections/oscal.py       Assessment Results + POA&M
src/cdfc/attest/projections/rocrate.py     the evidence crate
docs/PROJECTION-LOSS.md
```

#### The projection rule, and the one case that is not representable

`PASS → satisfied` · `FAIL → not-satisfied` · `INDETERMINATE / NOT_RUN / NO_PREDICATE →` an `observation`
with our reason as a `prop`, **no finding**, plus an `exclude-controls[]` entry · `OUT_OF_SCOPE →` an
`exclude-controls[]` entry only · **`INVALID` → not representable at all.**

**Every projection carries a mandatory `metadata.prop` flagging it as lossy and naming the URI of the
normative artifact — in the file, not in a README.** Any party reading only the projection sees a smaller,
cleaner report than the truth. That is the point of saying so inside the file.

**The `INVALID` case is the one to get right**, and it is the one a naive projector gets wrong in the most
dangerous possible direction: OSCAL's `finding-target.status.state` is a **closed two-value enum
`{satisfied, not-satisfied}`**, and an OSCAL Assessment Result with zero findings is schema-valid and means
nothing in particular. **A projector that emits an empty AR for an `INVALID` run has published a clean
assurance document for a run in which we could not demonstrate our instrument was working.**

**RULING: `project_oscal(statement)` raises `NotRepresentable` when `runState == "INVALID"`.** It does not
emit a degraded document, it does not emit an empty one, and there is no flag to make it. The CLI prints the
`invalid.*` cause and exits non-zero.

#### Validation

| Test | Asserts |
|---|---|
| `tests/unit/test_oscal.py::test_oscal__invalid_raises_not_representable` | and **no file is written** |
| `tests/unit/test_oscal.py::test_oscal__every_unsettled_state_becomes_an_observation_and_an_exclusion` | table-driven over all four unsettled states; **no finding is emitted for any of them** |
| `tests/unit/test_oscal.py::test_oscal__lossy_prop_is_in_the_file` | the `metadata.prop` exists and names the normative artifact's URI |
| `tests/unit/test_rocrate.py::test_rocrate__every_referenced_blob_is_present` | the crate is self-contained or it fails |
| contract | `tests/contract/test_contract__projection_never_gains_a_state` | the projection's state set is a **function** of ours; a projection state with no pre-image fails |
| determinism | `tests/determinism/test_det__projections_are_byte_identical` | both projections join `report.html`, `attestation.json` and `run.jsonl` in `make determinism`'s comparison set. **A lossy projection that is also non-deterministic is a second artifact a consumer could diff and mis-read** |

**Performance.** No new budget; both projections are pure functions of an in-memory statement and sit inside
`PERF-RENDER` (~20 ms baseline, fail above 60 ms).

*New catalogue entry:*

```yaml
- id: NC-A20
  component: attest
  break: "an INVALID run is projected to an OSCAL Assessment Result with zero findings, which is schema-valid and reads as clean"
  measured_instance: "OSCAL's finding-target.status.state is a closed two-value enum and findings became optional in 2021"
  injector: oscal_projects_invalid
  why_impossible: null
  guard_tests:
    - tests/unit/test_oscal.py::test_oscal__invalid_raises_not_representable
    - tests/e2e/test_e2e__invalid.py::test_e2e__INVALID_shows_no_fraction_of_any_kind
  positive_control: tests/unit/test_oscal.py::test_oscal__valid_run_projects_and_declares_its_loss
  status: ACTIVE
```

---

## P11 · Mutation, per methodology §3.5

The methodology's §3.5 table names **`attest/render`** as Tier S and says nothing about the rest of
`attest/`. **This document assigns the rest**, with its argument:

| Module | Tier | `K/V` | Blocking from | Argument |
|---|---|---:|---|---|
| `attest/canon.py` | **V** | 0.90 | **P11** | A surviving mutant is a byte-identity claim that is false for inputs nobody generated. The canonicaliser is the one module where a wrong answer is *silent by construction*, because both sides are hashes |
| `attest/verify.py` | **V** | 0.90 | **P11** | A surviving mutant is *"if it does not reproduce, it does not ship"* implemented as *"if it does not reproduce, we do not notice"* |
| `attest/statement.py`, `attest/dsse.py` | **Q** | 0.85 | **P11** | They decide what a signature is over |
| `attest/projections/` | **S** | 0.70 | P11 + 2 | Declared-lossy by construction; the `NotRepresentable` path is guarded by a contract test rather than by mutation |

**`selfcheck/` is already Tier V (`K/V ≥ 0.90`) in the methodology's own table and needs no assignment.**
Note that `mutmut`'s `and ↔ or` operator on `selfcheck/canary.py::disposition` is, for this phase, what
`evaluate/preflight.py` is for P5: **the single most important mutant in the module**, because
`silent or not selftest_silent or anti_fired` mutated to `and` produces a loop that reports `VALID` unless
*everything* is wrong. It must be killed.

The phase gate prints, in this exact form:
`attest/canon.py: K/V = <k>/<v> (floor) · K/(V−E) = <k>/<v−e> with E = <e> adjudicated, arguments in
reports/mutation/attest_canon.ledger.jsonl · I = <i>, T = <t> (ids listed)`. **A phase gate quoting a bare
percentage fails its own review.**

## P11 · The measurement this phase produces

**Primary — the byte-identity result on a second machine:** bytes differing / bytes in the report, **target
0**, across all three artifacts (`report.html`, `attestation.json`, `run.jsonl`), together with **the count
of non-determinism sources enumerated and the count removed** — now **six and six**, the fifth being the
probe seed and the sixth self-measured durations (F23). Warrant **MEASURED**.

**Supporting:**

| Number | Denominator | Warrant |
|---|---|---|
| Property names in the schema that trip the **advisory** substring scan, and how many are allowlisted with an argument | all property names at any depth | MEASURED |
| Item states representable in the OSCAL projection | 8 item states | MEASURED — **the declared loss, as a count** |
| Manifest pins checked by `verify` | 8 + 2 run-level inputs | MEASURED |

## P11 · Exit gate — this is gate **G-REPRO**

1. **A third party clones the repo and runs `cdfc verify` on a different machine and gets a byte-identical
   re-derivation.** `E2E-VERIFY` green on the second runner image.
2. `E2E-TAMPER` produces a **named diff**, not a boolean.
3. `E2E-TAMPER-ATTEST` reports `signature_valid` and `reproduced` as **two separate facts**.
4. The attestation validates against its JSON Schema with `additionalProperties: false` everywhere, the
   recursive walk finds no banned name at any depth, and the advisory scan's hits are fully allowlisted with
   arguments.
5. `test_contract__no_json_float_in_the_payload` green.
6. `test_no_libreoffice_online`, `test_no_tlog` and `test_no_model_in_verdict_path` green.
7. `project_oscal` **raises** on an `INVALID` run and writes nothing.
8. `docs/NON-DETERMINISM.md` lists **six** sources enumerated and six removed, each with its test and its
   injector, the sixth being self-measured durations (F23).
9. `test_contract__invalid_carries_a_null_not_an_absence` is green, and `E2E-INVALID` asserts the property is
   **present**, is `null`, and that an omission fails validation (F24).
10. `test_contract__no_duration_field_in_a_hashed_object` is green, and `ci/no-clock-in-core.sh`'s pattern
    set contains `perf_counter`, `monotonic` and `process_time` (F23).

## P11 · What it kills if it fails

- **If byte identity cannot be achieved**, the non-determinism is **named** and, if it cannot be removed,
  **the attestation drops the byte-identity claim and carries a weaker field-level re-derivation claim
  instead** (*the named fields are equal*), **explicitly labelled as weaker on the report surface.** The
  programme's headline acceptance test is downgraded, published as downgraded, and the system ships. The
  field list is not negotiable: `{settledFraction.*, items[].state, items[].reason, livenessProof.*,
  residue.*, verdict.state}`.
- **If the name prohibition cannot be made both exact and safe**, fall back to the **substring** matcher and
  **rename `canariesPassed` to `canariesFired`** — losing a small readability, keeping the stronger gate.
  The rename is cheap and the gate is not, and that trade is recorded rather than argued each time.
- **If the projections cannot be made honestly lossy**, they are **deleted**, not excepted. An OSCAL AR that
  cannot express `INVALID` and does not refuse to try is worse than no OSCAL AR, because it is the one
  artifact a downstream tool would ingest without reading.

---
---

## §4 — WHAT THESE THREE PHASES CANNOT ESTABLISH

The project's own standard demands the residue be declared. These survive every gate in this document
green, every negative control caught, and the mutation thresholds met.

**4.1 The canary proves the apparatus *above the fact table* is live. It does not prove the fact table is
the filing.** The loop applies a witness to the in-memory fact table and asserts the predicate turns it into
a `FAIL`. A fact table that is internally consistent but populated from the wrong values — a stale cache, a
cross-run bleed, a key resolver that binds the right shape to the wrong rows *uniformly* — still lets every
canary fire. What guards *that* is the receipt hash, the dual-reader agreement, `TEMPLATE_DIFF` and the
anti-canary's clean pass case; **it is not the canary, and the canary must never be quoted as if it were.**
The honest sentence is: *every check demonstrated, on this document's facts, that it can still catch the
fault it was admitted for.* Not: *this document was read correctly.*

**4.2 The recursion stops at `P-SELFTEST-DEAD`.** §P10·L.4 closes the one hole a constant closes. Nothing
watches the constant. One more layer would move the problem one layer, and we stop deliberately.

**4.3 A relation can be perfectly implemented and wrong.** A violated relation means *the artifact is wrong*
**or** *our relation is wrong*. The five gates measure a relation's kill rate and false-failure rate; **no
test in this document establishes that a relation means what its author thought it meant.** NC-N01's cost
applies here unchanged, and `docs/RELATION-REVIEW.md`'s two signatures are a procedure, not a measurement.

**4.4 `TEMPLATE_DIFF`'s oracle is authoritative and not correct.** The regulator's own template computes a
scheme total that misses two of its own nine legal scheme types (**MEASURED, first-hand, §P9-B1**).
`template_defects.yaml` handles the defects **we found**. A defect nobody found is a false failure charged
to a filer, and the only instrument against it is that the finding is `INFORMATIONAL`-able after the fact
and that every mismatch renders both values so a human can see which side is wrong.

**4.5 `|RESIDUE|` is measured under one fault model and inherits one human judgment.** `KR` and `|RESIDUE|`
both license exactly one sentence each about *the defects we seeded under fault model v3*. **There is no
coupling study for financial filing data**, so the bridge from seeded to real faults does not exist and must
not be walked across. And the INNOCUOUS/WRONG call is a human's; κ measures the disagreement, it does not
remove it.

**4.6 Byte identity is not correctness.** A deterministically wrong pipeline reproduces perfectly.
`verify` establishes that the report is a function of its named inputs — nothing more, and the report's
own copy must not imply more.

**4.7 The catalogue's denominator is still ours.** §P10·L injects six deaths *we imagined*. A seventh
mechanism nobody imagined is invisible to the sweep by construction, and the only instrument is the
catalogue's append-only growth log. **Report the rate at which new mechanisms are discovered; do not claim
it converges.** §0.5 is itself an instance: a mechanism that was mis-attributed in a binding document and
was found by reading, not by testing.

**4.8 Deception.** Every check here is a consistency check over a self-reported document. **A coherent liar
passes all of them.** The sentence stays permanently on the report surface, and the residue set is the
measurement of the same boundary from the other side.

### New `injector: NONE` catalogue rows created by these phases

**ID RANGES, and they are re-keyed here because four documents collided (adversary F27, and it is a
green-build lie rather than a bookkeeping nit: the catalogue loads into a dict keyed by `id`, so the later
document's entry silently REPLACES the earlier one and the sweep still reports `caught == active`).**
`plan/04` §4.4 allocated `NC-N11`/`NC-N12`; `plan/06` P13-B2 allocated `NC-N11`; this document allocated
`NC-N11`–`NC-N14`. Three different entries under two ids.

> **THE `N`-FAMILY PARTITION THAT STOOD HERE IS DELETED. Arbitration C9.** It was one of four mutually
> inconsistent band tables (`02` R5a, `04` §0.8, this one, `07` §3), and the range it claimed for this
> document — `N20–N29` — **collided with `04`'s `NC-N20`/`NC-N21` in the same commit.** The single
> allocation now lives in **`plan/01-validation-methodology.md` §2, THE CANONICAL NC- REGISTRY**, the sole
> place an `NC-` id may be *defined*. This document *references* ids; it does not allocate them.
>
> **What C9 renumbered here:** this document's `NC-N20` (*impossible:* the fact table holds this filing's
> values) → **`NC-N25`**, and its `NC-N21` (*impossible:* a relation encodes its author's intent) →
> **`NC-N26`**. `04`'s two entries of the same numbers became `NC-N50`/`NC-N51`. **`NC-N20` and `NC-N21` are
> RETIRED PERMANENTLY and are never reassigned** — neither side keeps a contested id. Superseded ids keep
> their rows in `docs/CATALOGUE-CORRECTIONS.md`.
>
> **Ids whose detail lives in this document:** `NC-C01`–`C11`, `NC-R01`–`R10`, `NC-A16`–`A20`,
> `NC-N11`–`N14`, `NC-N22`–`N26`. Their *rows* are in `01`'s registry; their *shapes* are below.
> *Alternative the original ruling beat:* partitioning `catalogue.yaml` per component, which would make the
> collisions harmless — rejected because the four meta-tests are written over one file. That reasoning
> stands; what C9 changes is **who allocates**, not how the file is shaped.
>
> Two gates enforce it, both cheap, both required **at P0-B3, before the first entry is written**:
> `test_nc_meta__ids_are_unique` (trivial, and its absence is why this went unnoticed) and
> **`ci/catalogue-ids.sh`** — a grep over `plan/*.md` asserting every `NC-` id appears as a *definition* in
> exactly one document, and that each id falls inside its owning document's declared range.

| id | What we cannot break mechanically | What it costs |
|---|---|---|
| **NC-N25** *(was NC-N11 — re-keyed, F27)* | **That the fact table holds this filing's values.** Every injection we can write either breaks a hash (caught by receipt) or breaks a shape (caught by the readers). A *uniform* value substitution that preserves shape and hash is not constructible without breaking the hash | §4.1's boundary. Substitute instrument, not a test: `TEMPLATE_DIFF` and the dual-reader agreement vector, both of which are measurements |
| **NC-N26** *(was NC-N12 — re-keyed, F27)* | **That a relation encodes the property its author intended.** Same class as NC-N01, applied to relations | A relation can pass all five gates and be about something else. Substitute: two signatures on `docs/RELATION-REVIEW.md` and the published refusals — **or, where the second signer does not exist, the literal `SINGLE-SIGNER — a weaker review` beside every relation-derived number** (P9-B2 ruling (c)) |
| **NC-N22** *(was NC-N13 — re-keyed, F27)* | **That `template_defects.yaml` is complete.** We can prove each declared defect; we cannot prove there are no others | A filer can be failed for the regulator's mistake. Substitute: both values render on every `TEMPLATE_DIFF` finding, and the defect table is append-only with evidence commands **and cannot raise the settled fraction** (F14) |
| **NC-N23** *(was NC-N14 — re-keyed, F27)* | **That the residue's fault model is rich enough.** A survivor class the operators cannot generate is invisible | `|RESIDUE|` is a lower bound on the unkillable class and must be quoted as one, always with `under fault model v3` and the operator list |
| **NC-N24** *(new, F3)* | **That G-EVAL's arm-2 expectation file was written by a mind independent of `src/cdfc/calc/`.** `git blame` and a declared `authored_by` establish a *different name*, never a different mental model; and if the name is the same, nothing mechanical can supply independence | **Every number in P9, P10 and P11 rests on the evaluator.** Substitute: the literal string `SAME-AUTHOR — a weaker instrument` travelling with each of them, G-EVAL recorded as `PASSED — NOT INDEPENDENT`, and the LibreOffice disagreement set published with a **pre-registered** threshold above which G2 is downgraded to a reach measurement. See the OPEN item in §5.3 |

---

## §5 — WHAT IS GENUINELY OPEN IN THESE THREE PHASES, WITH ITS DECISION RULE

Two items were open when this document was written. **The adversary pass added a third, and unlike the other
two it does block a build** — it is the entry criterion of P9-B1.

**5.1 `MAX_WITNESSES` and the witness-diversity rule.** §0.2 sets 3 and *"maximally diverse in fault
class"*. **Nothing in the corpus argues for 3.** *Decision rule:* run P10-B1 with `MAX_WITNESSES ∈ {1, 3,
5}` over the template-computed clean corpus, measure the **inapplicability rate** at each, and pick the
smallest value at which inapplicability is 0 on the reference fill. Publish the curve in
`docs/measurements/P10-canary-cost.md`. Until it is run, 3 renders in code as
`MAX_WITNESSES = 3  # PROVISIONAL — see docs/SELFCHECK-THRESHOLDS.md`, and the number is not quoted
anywhere else.

**5.2 The 92-day `expires` constant.** Derived from the spec's example (`2026-08-14 → 2026-11-14`), which
never claimed to be a policy. *Decision rule:* an attestation expires when the thing it is a claim about can
have moved. The two things that can move are the **template** and the **instrument stream**, and the
instrument stream moves on no schedule at all. So `expires` should be **the earlier of** a fixed horizon and
the next known instrument event — and until the watcher (P13-B4) exists there is no such event to read.
**Until then, `POLICY_VALIDITY_DAYS = 92` renders in the attestation with the literal string
`PROVISIONAL — no argued basis`, exactly as `K` and `T` render `PLACEHOLDER`.** This is the same discipline,
applied to our own field rather than to someone else's.

**5.3 G-EVAL arm 2's second author — OPEN, USER DECISION, and it blocks P9-B1's entry criterion.**
Adversary F3: arm 2 requires *"a human-authored expectation file, written from the formula text by a person
who did not write the evaluator"*, and **P3 has no person-days for a second person in its effort table** —
while every other second-person cost in this plan is enumerated (corpus 15–25, adjudication 3–5, κ 1,
strata 2+1, proviso labeller 0.5, admission signer 0.25, transfer operator 4–6 h, and now this document's
relation reviewers 2–3). By the plan's own resource model, arm 2 therefore resolves to a **self-check**, and
`TEMPLATE_DIFF`'s oracle *is* that evaluator — so P9, P10 and P11 inherit it entirely.

> **THE QUESTION, exactly, and only the owner can answer it:** *is there 1.5–2 person-days of a second
> person — someone who has not read `src/cdfc/calc/` — available to author the G-EVAL arm-2 expectation file
> for the 505 (or 504, §0.6) FME formula cells?*
>
> **Blocks:** P3's effort table, and therefore P9-B1's entry criterion. It does **not** block starting P9-B1:
> it determines which of two labels ships with every number these three phases publish.
>
> **DECIDED here, whichever way the answer goes, so that there is no third and no silent option:**
> - **Yes** ⇒ 1.5–2 person-days enter P3's effort table in the second-person column;
>   `docs/measurements/P3-evaluator.md` records `INDEPENDENT` with both `authored_by` fields;
>   `test_arm_two_author_is_not_the_evaluator_author` passes on the strong branch.
> - **No** ⇒ `docs/measurements/P3-evaluator.md` records the literal `SAME-AUTHOR — a weaker instrument`,
>   `ci/GATES.md` records G-EVAL as **`PASSED — NOT INDEPENDENT`**, and that string renders **beside every
>   kill rate and every `TEMPLATE_DIFF` number on every surface** —
>   `test_contract__geval_label_travels_with_the_numbers`. **What it costs, stated plainly: the 957 ceiling,
>   every `K/O`, and the whole of `TEMPLATE_DIFF` become claims checked against a second expression of one
>   person's understanding of Excel's semantics. That is a real weakening and it is survivable; concealing
>   it is not.**
>
> **And arm 2 gains a failing condition against the one genuinely independent instrument, in either branch.**
> A published LibreOffice disagreement set that changes nothing is a log line, not a gate. **`d = 11`, a
> frozen integer, pre-registered by `plan/02` — this document references it and does not restate it**
> (arbitration **C1**). Above `d`, **G2 is downgraded to a reach measurement (`K/G`, not `K/O`)** on the same
> branch arm 1 already has. The constant, its derivation `max(3, ceil(0.05 × |non-trivial cells|))` on the
> 204 non-trivial cells `plan/02` §0.2 N1 measured, the corpus content hash and the date live in
> `experiments/G-EVAL/PREREGISTRATION.md`, written **before the first run**;
> `test_geval__disagreement_above_d_downgrades_g2` is its test.
> *Alternative it beat:* leaving `d` to be chosen after seeing the disagreement count — the
> criterion-after-the-result failure this plan refuses everywhere else. **A bare `d = 25` was previously
> asserted here with no stated basis; it is deleted, not softened.** `d` has one value, in one place, and
> this document is not that place.

---

## §6 — THE DEFINITION-OF-DONE DELTAS FOR THESE PHASES

`docs/DOD-TEMPLATE.md` applies unchanged. **Six** lines are added for these three phases only, and they are
added because each names a way a build here could pass every existing line and still be wrong.

```markdown
## J. Probe, self-check and attestation deltas
- [ ] J1  If this build adds a RELATION: its evidence sentence, its necessity class, its non-degeneracy
          precondition, its basis set, its declared claims_fault_classes (dated BEFORE any campaign),
          and the two reviewer signatures in docs/RELATION-REVIEW.md -- or the literal
          SINGLE-SIGNER — a weaker review. If it was refused, the refusal row exists and this line names it.
- [ ] J2  If this build touches the canary loop: which of the SIX DEATHS (§P10·L.1) it was run against, and
          THE PATH TO THE EVIDENCE, not a paste: reports/negative-control-sweep.json's row for the entry,
          at commit <sha>, whose captured assertion text and pytest node id the sweep wrote for every
          flipped guard.  [adversary F31: a pasted assertion line in a PR description is verifiable only
          by its author, which is the one thing the DoD's own standard forbids.]
- [ ] J3  If this build emits a number that is a CEILING (a maximum reach, an upper bound, a lower bound):
          the ceiling is published BEFORE the delta on the same page, and this line gives both paths.
- [ ] J4  If this build touches the attestation schema: the recursive-walk output, the ADVISORY substring
          scan output, and the NAME-ALLOWLIST.md diff with its argument.
- [ ] J5  If this build emits a FALSE-FAILURE RATE or a "fires on zero clean filings" claim: the corpus id,
          its provenance, and the computed independence result -- generator import closure ∩ evaluation
          import closure == ∅ AND read_keys ∩ corpus.computed_cells == ∅. A TEMPLATE-COMPUTED corpus id on
          this line fails the build.  [adversary F2]
- [ ] J6  If this build calls recalculate(): the formula_source argument at every call site it added, and
          the reason. TEMPLATE is correct for exactly one caller (TEMPLATE_DIFF); everything else is
          FILING.  [adversary F19]
```

**J3 is the one to enforce hardest.** `957 of 3,747`, `2,790 of 3,747`, `un-runnable / |catalogue|` and `|RESIDUE|` are all
bounds, and a bound published after its delta reads as an excuse while the same bound published before it
reads as a measurement. The difference is entirely in the ordering, and the ordering is checkable.

---

## §7 — THE CLOSING CHECK ON THESE THREE PHASES

Three properties to verify if this document drifts.

**One. Every claim in these phases is about the instrument, and each says which part of the instrument.**
P9 says *what else is true of this artifact*; P10 says *the checking apparatus was alive on this artifact's
facts* — **not** that the facts are the artifact (§4.1); P11 says *this document is a function of its named
inputs* — **not** that it is right (§4.6). If a sentence in a report, a README or a slide merges any two of
those three, it has claimed something no test in this plan supports.

**Two. Every gate here fails into a smaller system that ships.** G-LIVENESS fails ⇒ `livenessProof` is
dropped and the surfaces say liveness is not demonstrated. G-REPRO fails ⇒ a field-level re-derivation
claim, labelled weaker. P9 fails ⇒ the settled fraction becomes a ceiling rather than a growth curve.
**None of the three produces a stall**, and a gate that stalls is a gate that will be renegotiated under
pressure.

**Three. The document's own correction is the evidence that its method works.** §0.5 found that the plan's
headline canary control, as written in a *binding* document, would have been caught by the template binder —
a green suite, a true `INVALID`, and an untested claim. It was found by reading the fingerprint definition
next to the fixture, which is exactly the *"name the specific broken build that would make this test go
red"* discipline of the methodology's appendix, applied to a test that already existed. **If a future
revision of this document contains no correction of that kind, that is a signal about the revision, not
about the plan.**

---
---

## REPAIRS APPLIED (adversary pass)

Against `plan/08-adversary.md`, dated 11 August 2026. Every finding that touches P9, P10 or P11 is listed,
including the ones whose repair belongs to another document, so that a reviewer can check this document's
work without re-deriving the finding. **A repair here is a test, a negative control, a changed gate
threshold, a new required field or a changed contract. There is no row whose repair is a paragraph.**

| Finding | Sev | The finding, in one line | What changed here | Where |
|---|---|---|---|---|
| **F1** | FATAL | G2's registry bar computes `K/O` over a denominator the predicate chooses after the campaign; `FaultWitness.fault_class` was the only place the "claim" existed | `claims_fault_classes` becomes a **required, non-empty envelope field inside `code_sha256`**; `FaultWitness.__post_init__` raises `UndeclaredFaultClass` when its class is not in that set; witness diversity is drawn **within** the claimed set; `RelationSpec` gains the field; authoring-protocol step 5 requires it dated before any campaign | §0.2 (contract-change block) · §0.3 · P9-B2 `RelationSpec` + protocol step 5 · P9-B4 `test_pq__claims_fault_classes_is_carried_through_to_envelope` · P10-B1 `test_w__fault_class_is_a_declared_claim_not_a_post_hoc_label` · P9 exit gate 5 |
| **F2** | FATAL | The `TEMPLATE-COMPUTED` clean corpus is produced by `calc/`, the code the arithmetic predicates re-check; P9 exit 2 was `x == x` | Exit criterion 2 **re-founded** on `BLIND-FILLED` / `REGISTER-DERIVED` / one **`HAND-COMPUTED`** filing (budgeted, 0.5 person-days); `TEMPLATE-COMPUTED` demoted to a named smoke test that may not be cited in a gate; `test_nc__R08c` refuses the corpus id at the gate evaluator; new relational test that every admitted relation's clean arm ran on an **import-disjoint** corpus; narrow calibration warrant stated in §0.3; DoD line **J5** | P9-B1 relational block (CORRECTION) · §0.3 · P9-B2 validation table · P9 exit gate 2 & 4 · §6 J5 |
| **F3** | FATAL | G-EVAL arm 2 has no failing condition against LibreOffice and no budgeted second author, so it resolves to a self-check that every number here inherits | New **P9-B1 entry criterion**: G-EVAL's arm-2 status must be *recorded* as `INDEPENDENT` or `SAME-AUTHOR — a weaker instrument`, with `ci/GATES.md` carrying `PASSED — NOT INDEPENDENT`; the label is asserted onto the surface by `test_contract__geval_label_travels_with_the_numbers`; **arm 2 gains a pre-registered failing condition against LibreOffice, `d = 11` cells (frozen integer, pre-registered by `plan/02` in `experiments/G-EVAL/PREREGISTRATION.md`, C1) ⇒ G2 downgraded to a reach measurement**; new residue row NC-N24; **OPEN — USER DECISION** with the exact question and what each branch costs | P9 entry criteria · P9 measurement · §4 NC-N24 · **§5.3** |
| **F6** | SERIOUS | NC-C03 passes on a build with no canary layer at all | NC-C03 gains `layer_exists_assertion`: the same test body runs the reference fill and asserts `canariesRun > 0` **before** asserting the cause on the renamed-sheet fixture; generalised by `test_nc_meta__none_injector_entries_carry_a_layer_exists_assertion` | §P10·L.3 (NC-C03 + ruling) · P10 exit gate 10 |
| **F13** | FATAL | Nothing tests that the settled fraction cannot rise as a filing carries less information; the defence against the empty filing shrinks the denominator | `applicable()` returns `ScopeKind` instead of `bool`; **only `scope_kind == DECLARED_CHARACTERISTIC` leaves `inScope`, `PREDICATE_PRECONDITION` stays and is flagged for G3 re-qualification** (arbitration **C3**, which also retires `plan/03`'s competing 31st reason code and requires `plan/03` to *read* this field); the fraction never renders without `cellsTotal` beside `inScope`; **`test_prop__fraction_does_not_rise_as_the_filing_empties`**; NC-R09 with injector `degenerate_scope_leaves_the_denominator`; the `scope_kind` contract is **accepted** by `P5-B4` (`test_contract__scope_kind_is_read_not_ignored`) and by spec §II.3.3 | P9-B1 (`applicable` signature, relation step 1, the F13 ruling) · property table · NC-R09 · P9 exit gate 6 |
| **F14** | SERIOUS | `template_defects.yaml` can raise the settled fraction and this document asserted the opposite | The wrong clause is **deleted and corrected in place**; `test_defect_table_cannot_raise_the_settled_fraction`; the fallback is implemented, not advised — a defect on a cell with no other binding evaluation emits `NO_PREDICATE(no_predicate.rule_ambiguous)`, which stays in the denominator; NC-R10; property over defect-table subsets | P9-B1 `template_defects.yaml` CORRECTION · unit + property tables · NC-R10 · P9 exit gate 8 |
| **F18** | FATAL | `U/G` measures the evaluator's coverage, not the operator mix, because `not_run` cells are identical in both grids | Observability is **three-valued** at run time: `OBSERVABLE / UNOBSERVABLE / INDETERMINATE`; `CanaryRow.observability` replaces `observable: bool`; `CanaryReport.indeterminate`; `canariesIndeterminate` in `livenessProof`, **never pooled into `canariesInapplicable`**; indeterminate counts toward the §0.3 ceiling; NC-C11 with `notrun_counts_as_identical` | §0.3 · P10-B1 `observability()`, `CanaryRow`, the loop, the disposition table · NC-C11 · P10 exit gate 9 |
| **F19** | FATAL | F11 mutants are unobservable by construction, so the flagship class leaves `O` and `TEMPLATE_DIFF` can never clear G2 | **`recalculate(..., formula_source: Literal["TEMPLATE","FILING"])`, non-defaulted**, published in `docs/EVALUATION-CONTRACT.md`; observability and `selfcheck` use `FILING`, `TEMPLATE_DIFF` uses `TEMPLATE`; `test_f11_mutant_is_observable`, `test_g2_admits_template_diff`, `test_contract__formula_source_is_explicit` (AST scan, missing argument fails the build); NC-R08; entry **and** exit criteria; DoD line **J6** | P9-B1 (`formula_source` contract ruling) · P9 entry criteria · P9-B4 validation · P10-B1 `test_w__observability_uses_filing_formulas` · NC-R08 · P9 exit gate 3 · §6 J6 |
| **F21** | SERIOUS | P9's one number systematically under-measures `TEMPLATE_DIFF`, whose delta is near zero by construction | Every relation publishes **two** numbers: settled-count delta **and** marginal kill over the P10 residue population on the shared `O`; `test_rel__delta_and_marginal_are_both_published` fails a one-column page; the P10-B2 ordering consequence is stated with a dated `PENDING` placeholder test | P9-B4 delta ruling · P9-B4 validation · P9 measurement · P9 exit gate 7 |
| **F23** | FATAL | `CanaryRow.elapsed_us` sits inside the canonicalised evidence, so G-REPRO cannot hold — and deleting it destroys the evidence the loop ran | `elapsed_us` **removed from the row**; timings move to `reports/perf/<run_id>.jsonl` via `selfcheck/timings.py`, outside `run.jsonl`, the attestation and `verify`'s comparison set; the four deterministic evidence fields stay and `canariesRun == len(rows)` still answers D5; `test_contract__no_duration_field_in_a_hashed_object` + `test_tim__timings_are_written_outside_the_payload`; `ci/no-clock-in-core.sh` gains `perf_counter`/`monotonic`/`process_time`; non-determinism sources go **five → six** | P10-B1 (`CanaryRow`, the timing ruling, unit table, `livenessProof`) · P11-B2 non-determinism table · NC-C10 · P10 exit gate 8 · P11 exit gate 8 & 10 |
| **F24** | SERIOUS | Three contracts for `settledFraction` on `INVALID`: `null`, forbidden, and omitted | **One rule: present and `null`.** The JSON Schema `if/then` becomes a `const: null` **plus** `required`; the contract test is renamed `test_contract__invalid_carries_a_null_not_an_absence` and asserts all three legs | P11-B1 (contract table + ruling) · P11 exit gate 9 |
| **F25** | SERIOUS | §0.5's correction did not propagate; `plan/01` §1.10, `plan/01` §2.5 NC-C01a and `plan/00` P10 still assert an unsatisfiable mechanism | Propagation made an **obligation of the same commit**, each with a `docs/CATALOGUE-CORRECTIONS.md` row, plus `test_plan__no_binding_document_asserts_a_superseded_mechanism` — one grep over the corrections file, **required to be observed red on the "renames a sheet" + "canary" pair first** | §0.5 (propagation block) |
| **F27** | SERIOUS | Colliding catalogue ids across four documents; the later entry silently replaces the earlier in a dict keyed by `id`. **This document's own repair — claiming the `N20–N29` range — collided with `04` in the same commit** | **CLOSED BY ARBITRATION C9.** The self-declared range table here is **deleted**, with the three others that disagreed with it; **`plan/01` §2 is the sole registry and the sole allocator**. This document's `NC-N11`–`N14` keep their previous re-key; its `NC-N20`/`NC-N21` become **`NC-N25`/`NC-N26`**, `04`'s become `NC-N50`/`NC-N51`, and **`NC-N20`/`NC-N21` are RETIRED permanently** — neither side keeps a contested id. Superseded ids keep rows in `docs/CATALOGUE-CORRECTIONS.md`. Four meta-tests (`ids_are_unique`, `ids_are_defined_in_the_registry`, `no_orphan_guard`, `no_dangling_reference`) and `ci/catalogue-ids.sh` required **at P0-B3** | §4 (the deletion note + re-keyed rows) |
| **F31** | SERIOUS | DoD line C4 is verifiable only by its author — a pasted assertion in a PR description | DoD line **J2** replaces the paste with a **path**: `reports/negative-control-sweep.json`'s row for the entry at commit `<sha>`, whose captured assertion text and pytest node id the sweep writes per flipped guard | §6 J2 |
| **F32** | SERIOUS | P9-B2's only gate is an authoring protocol over 18 relations the document declines to enumerate, with an unstaffed second signer and an exit gate satisfiable by construction | The number **25 is deleted** from the build, the gate and every downstream denominator; `|catalogue|` is read from `CATALOGUE_SIZE`; the deliverable is the admitted/refused counts; the second signer is **budgeted at 2–3 person-days** with `SINGLE-SIGNER — a weaker review` as the stated fallback; the F2 corpus-independence test is added to the build's own gate; the golden stops pinning the split as a literal | P9-B2 (title, CORRECTION ruling (a)–(c), class table, protocol step 7, validation table) · P9 measurement · P9 effort |
| **F34** | SERIOUS | The `P9-B4 → P10-B2` edge is absent from `plan/00`'s graph and puts P11 on the `k = 0` critical path | The cost is **stated in the entry criterion where the edge is argued**, with the recomputed chain, and the repair is named for `plan/00` §3.1/§4/§4.1/§7 and `plan/06` §2.7 (the latter is repaired in `plan/06`, this pass). **The total is `plan/00`'s to publish: ~118 days** (arbitration **C6**; `~114` retired) | P10 entry criteria · P9-B4 delta ruling (the reverse edge) |
| **F42** | SERIOUS | P9-B2 at 5 days for 25 relations of which 18 are unenumerated | Effort quoted for the **enumerated** work (3 days) with the remainder as **open scope with a decision rule** (stop after three consecutive step-1 refusals); phase total 14 → 12 enumerated + open scope + a named person-day column | P9 effort header · P9-B2 ruling (b) |
| **F44** | MINOR | P10-B1 at 4 days excludes the `MAX_WITNESSES` calibration §5.1 requires | B1 4 → **4.5 days**, phase 10 → 10.5, and the deliverable is **named in the file list**: the inapplicability-versus-`MAX_WITNESSES` curve in `docs/measurements/P10-canary-cost.md` | P10 effort header · P10-B1 file list · P10 measurement · P10 exit gate 11 |
| **F4** | SERIOUS | The sweep asserts "at least one guard fails", so an entry can be caught by its weakest guard | **Not this document's repair** (`plan/01` §2.0, `plan/02` P0-B3), but **consumed here**: P9's exit gate now requires the sweep to be per-guard rather than per-entry, so a green NC-R block cannot be bought with one flipped guard | P9 exit gate 9 |
| **F33** | MINOR | Equivalent-mutant adjudication is prose by the person being scored | No repair proposed by the adversary beyond keeping `E` visible; this document's two mutation-tier tables already print `K/(V−E)` with `E` and the ledger path, and a bare percentage fails the phase gate | P9-B1 and P11 mutation tables (unchanged, verified) |

**Findings raised against P9–P13 whose repair is owned elsewhere and is *not* attempted here:** F5, F8, F9,
F10, F11, F12, F15, F16, F17, F20, F22, F26 (repaired in `plan/06`), F28, F29, F30 (repaired in `plan/06`),
F35 (repaired in `plan/06`), F36, F37, F38, F39, F40, F41 (repaired in `plan/06`), F43. Where one of them
constrains a P9–P11 gate, the constraint is written into the gate above rather than assumed.

**What this pass did not repair, stated because the plan's own standard requires it.** The `scope_kind`
denominator change (F13) and the `formula_source` argument (F19) are **contract changes that other documents
must consume** — `plan/03` P5-B4 and spec §II.3.3 for the first, `plan/02` P3-B4 and `plan/04` P6-B3 for the
second. This document states the contract, names the tests that fail when the other side does not implement
it, and cannot make the other side implement it. **If `plan/03` and `plan/02` are not amended in the same
pass, the tests named here fail — which is the intended failure mode, and is why each was written as a test
rather than as a note.**

> **UPDATE (arbitration C3): the `scope_kind` half is now consumed, and the failure mode it anticipated
> actually happened.** `plan/03` *was* amended in the same pass — but with a **different mechanism** (a 31st
> reason code), which is the one case this paragraph did not anticipate: not an un-amended reader, but a
> reader that repaired the same defect its own way and never read the field. Composed as written, the two
> repairs restored F13. C3 retires the 31st code, adopts `scope_kind`, and requires `plan/03` to read it —
> proved by `test_contract__scope_kind_is_read_not_ignored`, an AST scan, because a behavioural test that
> never constructs a `PREDICATE_PRECONDITION` record is green under both mechanisms. **The lesson is the
> pass's own: a coupled specification admits exactly one writer at a time.**

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C1** — `d` is a frozen integer | **the bare `d = 25` is deleted, not softened** — it had no stated basis anywhere; this document now references `plan/02`'s frozen `d = 11` and does not restate it | P9 §5.3 arm-2 box · F3 row |
| **C3** — F13's retention · *this document's field wins* | `ScopeKind` takes the ruling's vocabulary — `IN_SCOPE \| DECLARED_CHARACTERISTIC \| PREDICATE_PRECONDITION` (formerly `STRUCTURAL` / `DEGENERATE_INPUT`); the retention rule is stated in the ruled form, with **G3 re-qualification** added; the cross-document contract is now *accepted* at the other end rather than merely stated, and the paragraph that anticipated the failure records that the failure actually happened | P9-B1 `applicable()` · relation step 1 · the F13 ruling box · the cross-document contract · the unit table · F13 row · §residue |
| **C6** — the `k = 0` critical path | `~114` retired; `plan/00` §7 named as the arithmetic of record | P10 entry criterion B2 · F34 row |
| **C9** — the catalogue | **this document's `N`-family partition is deleted** — the `N20–N29` range it claimed collided with `04` in the same commit. `NC-N20`/`N21` → **`NC-N25`/`N26`**; both old ids **RETIRED**; this document allocates nothing | §4 (the deletion note) · §4 rows · F27 row |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
