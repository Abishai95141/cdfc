# 04 — THE QUALIFICATION PHASES
## P6, P7 and P8, in full · build plan, part 4 · compiled 11 August 2026

**This document specifies P6, P7 and P8 and nothing else.** It uses the phase IDs, the build numbering,
the ordering, the gates and the effort figures of `plan/00-decomposition.md`, and it satisfies
`plan/01-validation-methodology.md` — whose test taxonomy (§1), negative-control catalogue (§2), mutation
regime (§3), Definition of Done (§4), CI pipeline (§5) and fixture strategy (§6) are referenced **by name**
here and never restated. Where this document adds a catalogue entry it says so and gives the entry's full
shape; where it relies on an existing one it names the id and stops.

**Why these three phases are written together.** They are the rejector. P6 manufactures ground truth,
P7 applies four of the five gates to it, P8 supplies the one input no amount of engineering substitutes
for and applies the fifth. Every number the product displays is a fraction whose denominator one of these
three phases computes, and the interlock is tight enough that removing any one makes the other two
decorative: without P6 there is no `O`, so `K/O` is undefined and G2 is a reach measurement; without P7 the
settled fraction is an assertion; without P8 no predicate is admissible at all and the defensible settled
fraction is 0%.

**The sentence this group exists to make true.** *A check is admitted only after somebody measured how
often it is wrong, on a corpus its authors did not write, and proved it is not the flag-everything
baseline.* Today that sentence is false in this project: the gate has **exactly one demonstrated
rejection**, on a workbook that is not the flagship, in one predicate class, and **no false-failure rate
has been measured for any of the 280 harvested predicates**. This group is where both change, or where the
failure is published.

---

## §0 — WHAT THIS DOCUMENT DECIDES BEFORE ANY BUILD BEGINS

Eight items are under-determined or implicit across the binding documents. Each is ruled on here, with its
reason, so that no build starts on an ambiguity.

### 0.1 Module paths — `src/cdfc/qualify/` is canonical · DECIDED

`plan/00-decomposition.md` §5 names `src/cdfc/fault/model.py`, `src/cdfc/fault/surgery.py`,
`observability.py`, `gates/g0.py`, `gates/g1.py`, `g3_proof.py`, `g3_empirical.py`, `gates/g4.py`,
`registry/store.py`, `merkle.py`, `ilp.py`, `admit.py`, `corpus/provenance.py`.
`plan/01-validation-methodology.md` §0.4 names one flat package:
`src/cdfc/qualify/ g0_scope.py g1_binds.py g2_kill.py g3_degeneracy.py g4_ffr.py mutants.py
observability.py wilson.py ilp.py`, plus `src/cdfc/predicates/registry.py`.

**Ruling: methodology §0.4 wins.** *Reason:* the negative-control catalogue, the mutation tier table
(§3.5, `qualify/` at Tier Q ≥ 0.85) and the validation-ledger example (`"produced_by":
"src/cdfc/qualify/g2_kill.py"`) all reference §0.4's paths **by string**. A path in a test fixture is an
assertion; changing it is a diff in the guard, not a rename. The decomposition's names are role names and
map onto §0.4 as follows. **This table is the only mapping; no build may invent a third.**

| `00-decomposition.md` role name | Canonical path in this plan |
|---|---|
| `fault/model.py` | `src/cdfc/qualify/fault_model.py` |
| `fault/surgery.py` | `src/cdfc/qualify/surgery.py` |
| `observability.py` | `src/cdfc/qualify/observability.py` |
| (site set + control arm) | `src/cdfc/qualify/sites.py` |
| `gates/g0.py` | `src/cdfc/qualify/g0_scope.py` |
| `gates/g1.py` | `src/cdfc/qualify/g1_binds.py` |
| (the G2 gate over P6's campaign) | `src/cdfc/qualify/g2_kill.py` |
| `g3_proof.py` + `g3_empirical.py` | `src/cdfc/qualify/g3_degeneracy.py` (two entry points, one module) |
| `gates/g4.py` | `src/cdfc/qualify/g4_ffr.py` |
| `registry/store.py` + `merkle.py` + `admit.py` | `src/cdfc/predicates/registry.py` |
| `ilp.py` | `src/cdfc/qualify/ilp.py` |
| `corpus/provenance.py` | `src/cdfc/qualify/corpus/provenance.py` |

Three sub-packages are new and are entered in methodology §0.4 by the build that creates them:
`src/cdfc/qualify/faults/` (one module per fault class, P6-B1), `src/cdfc/qualify/baselines/` (B0/B1/B2,
P7-B3), `src/cdfc/qualify/corpus/` (provenance, oracles, firewall manifest, P8-B2).

### 0.2 The three free baselines are **built** at P7-B3 and **run** at P12-B2 · DECIDED

`plan/00-decomposition.md` places B0 ∪ B1 ∪ B2 in P12-B2. But G2's definition includes *"plus marginal
kill over `B0 ∪ B1 ∪ B2`"* (spec §II.4.3, §III.3.5) and G3's empirical arm requires *"not equivalent to a
published degeneracy-list member"*, whose list **is** B1's Daikon trivia output. Neither is computable at
P7 if the baselines do not exist.

**Ruling: the baseline *code* is a P7-B3 deliverable; the baseline *run under pre-registration* stays at
P12-B2.** *Reason, and it is decisive rather than convenient:* the P12 pre-registration is required to
contain **the code hashes of B0/B1/B2** (spec §IV.1.1). A hash of code that does not yet exist cannot be
written into a file that must precede the first model call. The baselines therefore **must** exist before
P12 begins, and P7 is the first phase whose gate arithmetic needs them. Building them earlier does not
weaken the pre-registration; it is the only order under which the pre-registration is writable.

**Cross-document obligation.** `plan/06-phases-model-and-clause.md` specifies P12-B2's *run*, its
pre-registration and the interpretation of the bar. It must not restate the module interfaces given here,
and this document must not state the experiment's threshold. Neither may quote the other's numbers.

### 0.3 P8-B2's `TEMPLATE-COMPUTED` arm is an **entry criterion of P7-B3** · DECIDED

G1 must execute a candidate against a filing. G3's empirical arm must measure *"flags ≤ 50% of the clean
corpus"*. Neither is possible without at least one clean filing, and `plan/00-decomposition.md` P7's entry
criteria do not name one.

**Ruling: the `TEMPLATE-COMPUTED` oracle is unbundled from P8-B2 in the same way P8-B1 is unbundled from
P8, and becomes an entry criterion of P7-B3.** It is specified in P8-B2 below, where it belongs; P7-B3's
entry criteria name it. *Reason:* it is the one clean corpus that is **ready today** — fill the input cells
and let the workbook's own 505 formula cells compute the derived ones — it needs no human and no calendar,
and a gate that cannot run for want of an input that exists is a scheduling error, not a dependency.

**This does not weaken G4 — and after the adversary pass it no longer strengthens it either (F2).** Using
`TEMPLATE-COMPUTED` at G1 and G3ᵉ is using it as an **execution substrate**, which is legitimate and is the
whole of what §0.3 licenses.

> **The sentence that used to close this ruling was wrong in the direction that flatters us.** It read
> *"`TEMPLATE-COMPUTED` licenses an FFR for arithmetic predicates only"*. For the mode this document
> originally specified — `synthesise` fills the inputs and **`src/cdfc/calc/` computes the derived cells** —
> the truth is the exact opposite: **arithmetic predicates are the one class it cannot license**, because
> the code that produced the derived values is the code that re-checks them. `sum_identity`,
> `cross_sheet_equality` and `tally_identity` (78 + 196 + 3 = 277 of the 515 predicates) assert exactly the
> identities `calc/` enforced when it wrote the file, so their false-failure rate on that corpus is zero by
> construction, at expected value zero **regardless of predicate quality** — which is this plan's own
> one-line definition of an uninformative rate, and the definition under which `SELF-AUTHORED` renders no
> digits. What it licenses now is decided in **P8-B2** (`derived_by`, and the foreign-engine mode) and
> enforced in **P8-B3** (independence as a *computed* property, not a declared boolean).

### 0.4 The site universe, the primary arm and the control arm are three different sets · DECIDED

`plan/01-validation-methodology.md` NC-Q06a asserts `sites ⊇ field_surface`, structurally against
`schema/styles_mask.py`. Spec §III.3.5 says seeding *"targets the fields `schema_keys` reads plus a 10%
control sample of fields it does not."* Read as one set these contradict.

**Ruling: they are three sets and the contradiction dissolves.**

```
universe(schema)   == field_surface(schema)            # computed by the mask, NEVER by the predicate set
primary(p)         := universe ∩ read_set(p)           # what a kill rate for p is a rate over
control(p)         := sample(universe \ upstream_closure(read_set(p)))
                      with |control(p)| >= ceil(0.10 * |primary(p)|)
```

Two consequences that are load-bearing.

**(a) `universe` is computed without reference to any predicate.** `site_universe()` takes no `Predicate`
parameter and its import closure does not reach `cdfc.predicates`. That is NC-Q06a's structural assertion
in its exact form, and it is the second of the two shared-denominator errors committed in one afternoon.

**(b) The control arm excludes the *upstream closure*, not merely the read set.** A mutation seeded at a
cell that feeds a cell the predicate reads changes the predicate's input after recalculation. Excluding
only the read set would make legitimate propagation look like a spurious fire, and the control arm's
threshold would then have to be a fudge factor. Excluding the upstream cone makes the correct threshold
**exactly zero** — see P7-B3.

### 0.5 Mutants are written by raw-zip surgery only; `openpyxl` never writes a mutant · DECIDED

Spec §II.1.2 retains openpyxl *"for row-shifting shared formulas … and for writing mutants."*
`plan/01-validation-methodology.md` §6.2 requires raw-zip surgery and says **"Never openpyxl round-trip."**

**Ruling: raw-zip surgery only.** *Reason, MEASURED:* an openpyxl load-and-save of the FME workbook takes
it from **3,663,391 → 65,877 bytes**, deletes 24 parts including a 3.55 MB data model, and removes all 19
`x14` validations. A mutant written that way differs from clean in 24 parts, so the observability filter's
diff is a diff of the *writer*, not of the *fault* — every mutant would classify OBSERVABLE and `U/G` would
be 0 for the same reason the harness's first kill rate was 100.0%. openpyxl's retained uses are unchanged:
row-shifting shared formulas on read, and cached-value convenience reads. Enforced by **NC-Q30**.

### 0.6 Z3 runs under a deterministic resource limit, never a wall clock · DECIDED

G3's proof verdict lands in `qualification.g3` and therefore inside the signed attestation and inside
P11's byte-identity acceptance test. `z3.Solver.set('timeout', ms)` is wall-clock and produces `unknown`
non-deterministically across machines and loads.

**Ruling: `solver.set('rlimit', N)`** — Z3's internal, machine-independent resource counter — with `N`
pinned in `qualify/g3_degeneracy.py` and recorded in `qualified_against`. A wall-clock timeout anywhere
under `src/cdfc/qualify/` fails `ci/no-wallclock-z3.sh` (new grep, §0.8). Test:
`tests/determinism/test_det__z3_unknown_is_reproducible`.

### 0.7 An unobservable mutant is **excluded from `O` and retained on disk**, not destroyed · DECIDED

`plan/00-decomposition.md` P6-B3 says *"discard mutants no cell value distinguishes."* Discarding them
makes `U/G` unauditable and destroys P10's feedstock.

**Ruling: excluded from the denominator, retained with its reason.** Each unobservable mutant is written to
`reports/campaigns/<campaign_id>/unobservable.jsonl` as
`{mutant_sha256, operator_id, site, reason: "recalculated grid identical to clean", clean_grid_sha256}`.
*Reason:* (a) `U/G` is a published number and a published number whose members were deleted cannot be
re-derived; (b) an F11 override whose literal happens to equal *this quarter's* computed value is
unobservable today and a latent defect next quarter, and P10's INNOCUOUS/WRONG adjudication is entitled to
see it. Every suppression is logged with its reason; an undeclared suppression is a coverage lie and fails
the build. Enforced by **NC-Q37**.

### 0.8 The registry deltas these three phases owe back to the methodology

An addition not entered in the methodology's registries is an unscanned surface. Each delta is a required
edit made in the build that introduces it, and each is a DoD line-G item.

**(a) Source tree** — `plan/01-validation-methodology.md` §0.4 gains `qualify/faults/`,
`qualify/baselines/`, `qualify/corpus/`, `qualify/fault_model.py`, `qualify/surgery.py`,
`qualify/sites.py`, `qualify/domain.py`, `qualify/cel_smt.py`, `qualify/random_flagger.py`,
`qualify/set_ffr.py`, `qualify/pipeline.py`, `qualify/result.py`, **`qualify/textsource.py` (P7-B0, F35)**
and **`qualify/template_instrument.py` (P7-B1, F9)**. *An addition not entered in the registry is an
unscanned surface, and these two are new surfaces.*

**(b) Test tree** — one new directory, **`tests/campaign/`**, for tests that need a full mutation campaign
(minutes, not seconds). It is separate from `tests/unit/` because methodology §1.1 budgets the whole unit
class at 30 s. One `Makefile` entry point, **`make campaign`**, CI stage 10.5, and it is added to
`tests/test_suite_census.py`'s collected set so it cannot silently shrink.

**(c) Mutation tiers** — `docs/MUTATION-THRESHOLDS.md` gains four rows. Every one is a raise or a
same-level assignment; §3.5's "lowered only by an argument that the old one was wrong" is not engaged.

| Module | Tier | `K/V` floor | Argument |
|---|---|---:|---|
| `qualify/` (rest) | Q | 0.85 | Methodology §3.5's existing row, unchanged |
| `qualify/observability.py`, `qualify/sites.py` | **V** | **0.90** | Promoted. They decide the denominator of every kill rate. A survivor here reproduces NC-Q05/NC-Q06 — the two errors already committed |
| `qualify/wilson.py`, `qualify/set_ffr.py` | **V** | **0.90** | Promoted. They decide `severity_tier`, and a boundary mutant here is exactly NC-Q09 |
| `qualify/corpus/provenance.py` | **V** | **0.90** | Promoted. It is the single choke point that refuses a `SELF-AUTHORED` number |

**(d) CI greps** — `ci/GATES.md` and methodology §5.4 gain three rows. Each has a planted control in
`tests/negative/test_nc_ci.py` asserting a non-zero exit, as §5.4 requires.

| Script | Introduced by | Scans | Forbids | Planted control |
|---|---|---|---|---|
| `ci/no-wallclock-z3.sh` | P7-B3 | `src/cdfc/qualify/` | `set('timeout'`, `set_param('timeout'`, `Tactic(...).try_for(` | `test_nc__CI4_wallclock_z3_is_caught`, injector `injectors/z3_wallclock.py` (new) |
| `ci/no-bare-rate.sh` | P6-B3 | `src/`, `docs/`, `templates/` | a `%`-formatted rate on a line that does not also name both integers of its fraction | `test_nc__CI5_bare_rate_is_caught`, injector `injectors/render_bare_kr.py` (new) |
| `ci/no-openpyxl-writer.sh` | P6-B2 | `src/cdfc/qualify/` | `Workbook.save`, `.save(`, `ZipFile(..., 'w')` outside `surgery.py`'s declared writer | `test_nc__CI6_openpyxl_mutant_writer_is_caught`, injector `injectors/mutant_via_openpyxl.py` (new) |
| `ci/catalogue-ids.sh` | **P0-B3** (moved earlier: it must exist before the first entry is written) | `plan/*.md`, `tests/negative/catalogue.yaml` | any `NC-` id that appears as a **definition** in more than one document, or twice in the catalogue | `test_nc__CI7_duplicate_catalogue_id_is_caught`, injector `injectors/duplicate_catalogue_id.py` (new) |

**(e) Catalogue ids allocated by this document — CORRECTED, and the correction is a finding (F27).**

> **The sentence this paragraph used to open with was false.** It read *"the Q family is free from
> `NC-Q12`"*. `plan/03-phases-verdict.md` §6 had already allocated the ids then called **`NC-Q12` … `NC-Q16`**
> *(all five are now **RETIRED** under C9; `03`'s content is at `NC-Q70`–`NC-Q74` — the numbers are quoted
> here only as history and resolve to nothing)*, and
> `plan/02-phases-foundation.md` §X had already allocated **NC-E10 … NC-E13** against `03`'s §6 claim that
> *"`NC-Q11` and `NC-E08` are the current maxima"*. **Two documents asserted the collision away rather than
> checking it.** The catalogue loads into a dict keyed by `id`; a collision silently replaces the earlier
> entry, `test_nc_meta__no_orphan_guard` stays green because the guard is still *named by an* entry, and
> the sweep still reports `caught == active`. That is a green build over a register nobody reads.

**DECIDED — id ranges are allocated per document, and the allocation is mechanised.** *Alternative it beat:*
"first writer wins, later writers check the other documents" — rejected because it is exactly the
manual-reconciliation discipline that produced four collisions across four documents written to the same
methodology.

> **THE BAND TABLE THAT STOOD HERE IS DELETED. Arbitration C9.** It was one of four mutually inconsistent
> tables — `02` R5a, this one, `05` §4 and `07` §3 — each written against `01` §2 and none agreeing with any
> other. **The single allocation now lives in `plan/01-validation-methodology.md` §2, THE CANONICAL NC-
> REGISTRY**, which is the sole place an `NC-` id may be *defined*. This document *references* ids and does
> not allocate them.

**What this document owns, and how it got here.** An earlier pass renumbered these entries into a range it
declared for itself: `Q12→Q30 · Q13→Q31 · Q14→Q32 · Q15→Q33 · Q16→Q34 · Q17→Q35 · Q18→Q36 · Q19→Q37 ·
Q20→Q38 · Q21→Q39 · Q22→Q40 · Q22b→Q41 · N11→N20 · N12→N21`. **Seven of those targets collided with `03`
and two with `05`, in the same commit, inside the repair for id collisions**, so C9 renumbered again —
mechanically, and this time against a registry rather than against a self-declared range:

| Old id (this document) | **New id** | Entry, in one line |
|---|---|---|
| `NC-Q40` | **`NC-Q55`** | an admission batch is written without a human signature |
| `NC-Q41` *(the former `NC-Q22b`)* | **`NC-Q56`** | the Wilson bound is computed in `float` (F17) |
| `NC-Q42` | **`NC-Q57`** | `claims_fault_classes` derived from the kill vector (F1) — **and `03`'s former `NC-Q45` was the same break under a second id; C9 merges them into this one entry** |
| `NC-Q43` | **`NC-Q58`** | `TEMPLATE-COMPUTED` licenses an arithmetic FFR (F2) |
| `NC-Q44` | **`NC-Q59`** | independence is hand-set instead of computed (F5) |
| `NC-Q45` | **`NC-Q60`** | a `not_run` cell is banked as unobservable (F18) |
| `NC-Q46` | **`NC-Q61`** | observability recalculates with template formulas (F19) |
| `NC-N20` | **`NC-N50`** | *impossible:* the fault taxonomy is complete |
| `NC-N21` | **`NC-N51`** | *impossible:* `domain-policy-v1.json`'s magnitude bound is right |

**`NC-Q40`–`NC-Q46`, `NC-N20` and `NC-N21` are RETIRED PERMANENTLY and are never reassigned** — neither
side keeps a contested id, because a retired id that later resolves to something is how a stale reference
becomes a silent wrong reference. Allocated to this document in total: **NC-Q30–Q39, NC-Q47, NC-Q48,
NC-Q55–Q61, NC-N50, NC-N51**. Full shapes are in §4.4.

*(**`NC-Q22` removed from this line by the confirmation pass**, `plan/12`. It was listed as allocated here
and **defined nowhere**: this document's `NC-Q22` entry became `NC-Q40` in the earlier pass and `NC-Q55`
under C9, so the number had been vacated twice while still being claimed. Re-issuing a vacated id is the
mechanism C9.3 exists to stop, so `NC-Q22` joins §2.2's RETIRED list rather than staying allocated. The one
surviving mention — inside `NC-Q56`'s entry, recording that F17's break was once filed "under `NC-Q22`'s
entry" — is a history note and stays.)*

**Cross-document obligation (owed to `plan/01-validation-methodology.md` §2).** The table above is entered
in `01` §2 as the normative allocation, and two meta-tests are added there, **both of which must exist at
P0-B3, before the first entry is written**: `test_nc_meta__ids_are_unique` (the catalogue's ids are a set)
and `test_nc_meta__id_is_inside_its_document_range` (an id defined in document *D* lies in *D*'s range).
`ci/catalogue-ids.sh` is the grep form of the same assertion over `plan/*.md`, and it is thirty lines.

**(f) The envelope delta these phases owe back to `plan/03-phases-verdict.md` P4-B1 — F1, and it is the
worst finding in the plan.** G2's registry bar is *"`K/O ≥ 0.80` on the fault classes the predicate
**claims** to cover"*. **No field of `Candidate` held such a claim.** The only place a fault class appeared
was `FaultWitness.fault_class` — and the witness set is *selected by `g2_kill.check()` at admission, from
the mutants that already killed.* A `sum_identity` predicate that kills F01 and F03 and is structurally
blind to F10, F12, F13 and F14 has `K/O = 0.21` over the campaign; G2 stamps its three surviving witnesses
`F01`/`F03`, evaluates the bar over `{F01, F03}`, gets `0.97`, admits it `BLOCKING`, and **nothing in the
plan is red.** That is the numerator choosing its own denominator, arriving at the gate that exists to
catch it. NC-Q05 checks the arithmetic and NC-Q06 checks the site universe; both stay green.

**Required edit to `plan/03-phases-verdict.md` P4-B1, and it is a change to the content address:**

```python
@dataclass(frozen=True, slots=True)
class Candidate:
    ...
    claims_fault_classes: tuple[str, ...]     # REQUIRED, NON-EMPTY, ids from FAULT_CLASSES.
                                              # Inside envelope_projection() and therefore inside
                                              # code_sha256: narrowing the claim after a campaign
                                              # produces a DIFFERENT PREDICATE, not a better score.
```

`EnvelopeSchemaError` at load when it is absent, empty, or names an id outside
`qualify/fault_model.FAULT_CLASSES`. **This document depends on the field; it does not own it.** The
consuming gate, its `O == 0` refusal and its negative control are specified at P7-B3.

---

## §0.9 — MEASUREMENTS TAKEN WHILE WRITING THIS DOCUMENT

Re-run so this document rests on artifacts rather than on the spec's summary of them.
Script: ad-hoc reads of `research/scripts/predicates.json` and `l4_result.json` plus a `Decimal` Wilson
implementation, `/Users/abishaikc/Gift/.venv/bin/python`, 11 Aug 2026. These are the fixture facts §4 pins.

| Quantity | Value | Warrant |
|---|---|---|
| `ALR_V2_3` numeric bounds with `formula1 == "-100000000000000000"` | **5**, covering `Assets!B7:J93` 783 · `Liabilities!B7:J65` 531 · `Other products!B7:J17` 99 · `Off BS Exposure!C8:C15 G13` 9 · `Reconciliation!E13 C27 E20 C13 C20 E27` 6 = **1,428 cells** | MEASURED — reproduces the spec's figure exactly |
| `ALR_V2_3`'s sixth bound | `integer_bound`, `Reconciliation`, 54 cells, `formula1 == "0"` — **a real bound, and the admission-side twin** | MEASURED |
| FME bounds, total | **24** = 13 `numeric_bound` + 11 `integer_bound` (the 6 `date_bound` are counted separately) | MEASURED |
| FME bound `formula1` distribution | `"0"` × **19** · `"-5000000"` × 2 · `"9.99999999999999E+26"` × 1 · `"9.99999999999999E+21"` × 1 · `"-9999999999"` × 1 | MEASURED — **new** |
| **The five non-`0` FME bounds, and they are unclassified anywhere in the corpus** | `2. Summary!U5:U14` (10 cells, `9.99999999999999E+26`) · `3. Portfolio!J17:N26` (50, `9.99999999999999E+21`) · `3. Portfolio!E27:F27` (2, `-5000000`) · `5. PMS!D10:E11` (4, `-5000000`) · `5. PMS!C10:C11` (2, `-9999999999`) — **68 cells** | MEASURED — **new** |
| Per-workbook harvest distribution summing to 515 | FME **280** · CMI quarterly **163** · ITFS **26** · ALR **19** · AL_monthly **16** · IBU **10** · EDR_1 **1** · Draft_ACAC **0** · IFSCA_Annual **0** | MEASURED — **new**; the spec makes publishing this a build gate and records that no research lane published it |
| Non-empty harvests | **7 of 9** — G-TRANSFER(mech)'s `≥ 5 of 9` bar is already cleared by the v0 harvest | DERIVED from the row above |
| Wilson upper bound, `z = 1.959963984540054`, `Decimal(prec=28)` | `hi(0,4) = 0.489891` · `hi(2,96) = 0.072807` (`lo = 0.005732`) · `hi(0,185) = 0.020342` · `hi(0,188) = 0.020024` · **`hi(0,189) = 0.019920`** · `hi(0,340) = 0.011172` | DERIVED (exact arithmetic) |
| **The exact `BLOCKING` threshold at zero fires is `n = 189`, not the spec's "roughly 185"** | `hi(0,188) = 0.020024 > 0.02 ≥ hi(0,189) = 0.019920` | DERIVED — **new**, and it is published as a correction rather than absorbed |
| Wilson `lo` at `k = 0` rounds to `-0.000000` | The lower bound **must be clamped to `[0, 1]`**, or a negative rate reaches a surface | MEASURED — **new** |

**The last three rows are the most useful things measured for this document.** The severity threshold is a
property of a function, not of prose; the plan must state that the module computes it and the test pins
whatever the module computes, with the arithmetic published in `docs/measurements/P8-severity.md`. And a
lower bound that renders `-0.0%` is a small, plausible, confident, wrong number — the shape this project
exists to refuse.

---

# P6 — THE FAULT-SEEDING HARNESS · 10.5 engineer-days

### What it settles

**Whether a kill rate over *our* operator mix means anything.** Concretely, three questions no earlier
phase can answer:

1. **What is our own `U/G`** — the fraction of generated mutants that no cell value distinguishes after
   recalculation? The literature's comparable figure is **3,512 of 7,500 = 46.8%**; it is a property of
   *that* operator suite and must not be assumed for ours.
2. **What is `K/O` per fault class**, where "killed" means *a predicate returned `FAIL` under the P5
   verdict model* — a term that did not exist until P5 shipped, and which the v0 harness approximated with
   a print statement.
3. **Is a kill rate measuring predicate *quality* or predicate *reach*?** In the first real run every
   arithmetic operator killed at exactly **18.1%**, identical to the fraction of sites inside the field
   graph. For identity predicates that number is reach, and the report must say which it is showing.

The v0 harness produced `MS = 3,574 / (19,782 − 22) = 18.09%`. Under this specification that is **the wrong
denominator**: `E` (equivalence) is a theorem, `U` (unobservability) is a diff. P6 replaces it and publishes
both, with the mechanism of the difference.

### Entry criteria

| # | Must be true | Why |
|---|---|---|
| E6.1 | **P5 complete.** `src/cdfc/evaluate/` emits one `run_check` row per predicate with a state from the closed 8, and `verdict/closure.py` holds the seven-term invariant | A mutant is *killed* iff a predicate returns `FAIL`. Before P5 there is no `FAIL` — only a boolean, which is what v0 had |
| E6.2 | **P3's G-EVAL passed** (barrier 2) | The observability filter *recalculates*. Without the evaluator there is no `O` and `K/O` is undefined. If G-EVAL passed in its degraded form (≤ 25 non-reproducing cells, pinned and excluded), those cells are excluded from the site universe and the exclusion list is an input to P6-B4 |
| E6.3 | `fixtures/prescribed/` byte-identical with `MANIFEST.json`, `tests/golden/test_fixture_integrity.py` green | A campaign is content-addressed against the base workbook |
| E6.4 | `fixtures/baselines/l4-v0.json` frozen with its README recording v0's two known defects | The baseline is kept because it is the evidence, not because it is right |
| E6.5 | `tests/negative/catalogue.yaml` exists and `make nc-sweep` runs | Every build below adds entries to it |

### Builds

---

#### P6-B1 — The fault model, versioned as `v3`

**Files created.**

```
src/cdfc/qualify/fault_model.py          the operator table, its digest, and the version constant
src/cdfc/qualify/faults/__init__.py      registry: FAULT_CLASSES: tuple[FaultClass, ...]
src/cdfc/qualify/faults/f01_sign.py      … one module per class, F01–F14
src/cdfc/qualify/faults/f14_vocab_gap.py
tools/gen_fault_model_doc.py             generates docs/FAULT-MODEL-v3.md from the table
docs/FAULT-MODEL-v3.md                   GENERATED. never hand-edited
docs/PROVISO-MARKERS-v1.md               (consumed by P7-B2; the file is created here because the
                                          fault model's F12/F14 share its normalisation table)
fixtures/baselines/fault-model-v3.json   the frozen operator table + its digest
```

**Public interface.**

```python
# src/cdfc/qualify/fault_model.py
FAULT_MODEL_VERSION: Final[str] = "v3"

class Arity(StrEnum):
    CELL = "cell"      # one cell edited
    PAIR = "pair"      # two cells edited so the artifact stays self-consistent
    RANGE = "range"    # a contiguous block (row insert/delete)

@dataclass(frozen=True)
class FaultClass:
    id: str                                   # "F11"
    name: str                                 # "formula_override"
    applies_to: frozenset[Dtype]              # MILLI_USD_MILLION | COUNT | DATE | TEXT | ENUM
    arity: Arity
    source: Literal["abraham_erwig_2009", "cdfc"]
    citation: str                             # verbatim, with page; "" only when source == "cdfc"
    operators: tuple[FaultOperator, ...]

@dataclass(frozen=True)
class FaultOperator:
    id: str                                   # "F11.a"
    def sites(self, schema: TemplateSchema, facts: FactTable) -> Iterator[Site]: ...
    def apply(self, base: WorkbookBytes, site: Site, rng: Random) -> tuple[CellEdit, ...]: ...

def operators(version: str = FAULT_MODEL_VERSION) -> tuple[FaultOperator, ...]: ...
def model_digest(version: str = FAULT_MODEL_VERSION) -> str:
    """sha256 over the RFC 8785 canonical serialisation of the operator table.
    Enters every qualification record and every campaign manifest."""
```

**The taxonomy — fourteen classes for a financial reporting workbook.** Classes F01–F11 are populated by
Abraham & Erwig's 17 spreadsheet mutation operators (IEEE TSE 35(1):94–108, 2009); several classes hold
more than one operator, which is why 17 operators map to 11 classes. F12–F14 are ours. Every class names
the artifact feature that makes it a real fault here, so that nobody has to take the taxonomy on faith.

| id | Class | What it perturbs | Dtypes | Arity | Why this artifact has it |
|---|---|---|---|---|---|
| **F01** | sign flip | `v → −v` | MONEY, COUNT | cell | In v0; the operator that kills a `≥ 0` bound and does **not** kill a `≥ −1e17` bound |
| **F02** | scale error | `×10`, `÷10`, `×1000` | MONEY | cell | The sheet's unit is USD Million; a filer entering USD is the modal unit slip |
| **F03** | off-by-one | `±1` unit `MILLI_USD_MILLION`; `±1` on a count | MONEY, COUNT | cell | Boundary. Counts get **zero tolerance** — a person is not a rounded quantity |
| **F04** | digit transposition | `12340 → 13240` | MONEY | cell | Keying error; survives a magnitude check |
| **F05** | zero-out / blank | `v → 0`, and separately `v → <empty cell>` | all | cell | **Two operators, not one.** `0` and blank are different facts and `sum([]) == 0` is NC-Q01 |
| **F06** | round to integer | drop the 2-dp quantum | MONEY | cell | Produced all 22 of v0's "equivalents"; it is the `τ(n) = 5n` straddle generator and the source of `indeterminate.tolerance_straddle` |
| **F07** | row omission | delete one data row from a table body | all | range | Where a missing investor or holding hides |
| **F08** | row duplication | duplicate one data row | all | range | Double count; the tally identities exist for this |
| **F09** | date shift | `±1 day`, `±1 quarter`, `DD↔MM` swap | DATE | cell | FME carries 6 date bounds; `D11 ≥ 32874`, `D41 ≥ 40179`, `E54:E63 ≥ 40179` |
| **F10** | enum substitution | one **legal** vocabulary term for another | ENUM | cell | 20 resolving vocabularies. A membership predicate **cannot** see this, by construction — it is a designed miss and it belongs in the residue |
| **F11** | **formula override** | a cell the pinned blank declares a formula carries a literal | MONEY, COUNT | cell **and pair** | **The flagship.** The pair form — override plus a consistent input change — leaves the filing perfectly self-consistent because the inconsistency was deleted with the formula. `TEMPLATE_DIFF` is the only thing in the design that detects it, and P9's exit gate names *"a seeded F11 pair"* |
| **F12** | vocabulary drift | a term outside the pinned vocabulary; **and** a homoglyph or whitespace variant of a legal one (`U+2011`, NBSP, trailing space, NFKC-distinct) | ENUM, TEXT | cell | MEASURED: one live regulated entity's registration number carries `U+2011 NON-BREAKING HYPHEN` — visually identical, byte-wise different, invisible in any screenshot |
| **F13** | carry desync | a cross-sheet carry **target** changed while its source is untouched, or the reverse | MONEY, COUNT | cell **and pair** | 181 cross-sheet equalities on FME. This is the class they exist for, and the pair form is the coordinated-misstatement seed |
| **F14** | vocabulary-gap exploitation | a value legal under the template's **own defective logic** but outside the regulation | ENUM | cell | The regulator's template computes a scheme total with three COUNTIFs that between them **miss two of its nine legal Type-of-Scheme values**. A filing exploiting that gap is undetectable by any relation the template encodes — this class is P10's residue feedstock |

**Numbering, and the one hard constraint.** The corpus quotes `F02`, `F05`, `F11` and `F12` in
illustrative blocks. Only one is load-bearing: **`F11` is the formula-override class**, because P9's exit
gate and experiment E3 both name a seeded `F11` pair. The rest are illustrative. **Decision rule if the
mapping from Abraham & Erwig's 17 operators yields a different number of classes:** the ids shift, `F11`
stays the formula-override class by renumbering the others around it, and `docs/FAULT-MODEL-v3.md` carries
a migration table from every id quoted anywhere in the corpus to its class. *The ids are not sacred; the
requirement is that a quoted id resolves to exactly one class and that the mapping is published.*

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_fault_model.py::test_fault_model__fourteen_classes` | `len(FAULT_CLASSES) == 14`; every id matches `^F\d{2}$`; ids are unique and contiguous |
| unit | `…::test_fault_model__every_class_cites_its_source` | `source == "abraham_erwig_2009" ⇒ citation` is non-empty and contains a page reference; `source == "cdfc" ⇒ citation == ""` and a `rationale` is non-empty |
| unit | `…::test_fault_model__f11_is_formula_override` | The hard constraint above, asserted as a constant |
| unit | `…::test_fault_model__f05_is_two_operators` | `zero` and `blank` are distinct operators. A single operator here would make `0` and `<empty>` the same fault, which is NC-Q01's arithmetic |
| unit | `…::test_fault_model__counts_never_receive_f06` | `Dtype.COUNT not in F06.applies_to`. Positive control: `Dtype.MILLI_USD_MILLION in F06.applies_to` |
| property | `tests/property/test_prop_fault_model.py::test_prop__sites_are_within_the_field_surface` | Property: for every class and every induced schema, `set(op.sites(schema, facts)) ⊆ field_surface(schema)`. Generator: the nine prescribed schemas × the 14 classes |
| golden | `tests/golden/test_fault_model_digest.py::test_golden__fault_model_v3_digest` | `model_digest("v3")` equals the value in `fixtures/baselines/fault-model-v3.json`. **Value assertion accompanying it (rule R-GOLD-2):** the serialised table's `F11` entry equals the pinned JSON fragment verbatim, not merely the digest |
| contract | `tests/contract/test_contract__fault_model_doc_is_generated` | Regenerate `docs/FAULT-MODEL-v3.md` from the table and assert byte-identity. A hand edit fails the build |

**Negative controls.**

| id | Break | Injector | Guard that must go red |
|---|---|---|---|
| **NC-E08** (existing) | `τ(n) = 5n` applied to a `COUNT` cell | `injectors/tolerance_on_counts.py` | `test_nc__E08_counts_get_zero_tolerance` — an F03 mutant changing an investor count by 1 must be **killed**; under injection it survives. Admission-side twin: `test_nc__E08b_money_gets_tau` — an F06 mutant inside `τ(n)` on a money cell must **not** fire |
| **NC-Q33** (new) | The fault model is version-pinned in name only: `model_digest` ignores the operator table and returns a constant, so a silently edited operator keeps its `v3` label and every quoted kill rate is qualified against a model that no longer exists | `injectors/fault_digest_constant.py` | `tests/negative/test_nc_predicate.py::test_nc__Q33_operator_edit_moves_the_digest` — mutate one operator's `applies_to`; assert `model_digest` changes and that a qualification record carrying the old digest fails to load |
| **NC-N50** (new, `injector: NONE`) | *That the taxonomy is complete for a financial reporting workbook.* `why_impossible`: completeness of a fault taxonomy is a claim about the population of real filing errors, and **no filed FME return is public** — the denominator does not exist. **What it costs:** every `K/O` is a statement about our operator mix and nothing else; the bridge from seeded to real faults is the coupling effect and **there is no coupling study for financial filing data.** The only available instrument is the catalogue's append-only growth log |

**Effort.** 3 engineer-days.

---

#### P6-B2 — Raw-zip surgery

**Files created.**

```
src/cdfc/qualify/surgery.py             the only sanctioned mutant writer
tools/fixtures/make_mutant.py           CLI wrapper, deterministic from a seed
ci/no-openpyxl-writer.sh                §0.8(d)
```

**Public interface.**

```python
# src/cdfc/qualify/surgery.py
@dataclass(frozen=True)
class CellEdit:
    sheet_name: str
    ref: str                    # "O7"
    old_xml: str                # the <c> element as found, verbatim
    new_xml: str                # the <c> element as written
    operator_id: str

@dataclass(frozen=True)
class MutantRecord:
    mutant_sha256: str
    base_sha256: str
    fault_class: str            # "F11"
    operator_id: str            # "F11.a"
    edits: tuple[CellEdit, ...]
    seed: int
    harness_version: str
    fault_model_version: str
    parts_changed: tuple[str, ...]      # MUST be exactly one worksheet part

def seed_mutant(base: Path, edits: Sequence[CellEdit], out: Path) -> MutantRecord:
    """Copy every zip entry byte-for-byte with its original compression parameters,
    rewriting exactly one xl/worksheets/sheetN.xml. Never re-serialises any other part.
    Raises MultiPartEditError if edits span more than one worksheet."""
```

**The property to preserve, and it is MEASURED:** exactly one part differs; the 3.55 MB data model part and
all 19 `x14` validations survive byte-identical. That is why raw-zip surgery is the method and not a
convenience.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_surgery.py::test_surgery__exactly_one_part_differs` | Zip-entry-wise diff of base vs mutant: `len(differing) == 1` and it is an `xl/worksheets/sheetN.xml` |
| unit | `…::test_surgery__x14_validations_survive` | Re-induce the mutant; `n_validations == 54` (35 main + 19 `x14`). **This is the openpyxl round-trip's exact failure, asserted on our own writer** |
| unit | `…::test_surgery__data_model_part_is_byte_identical` | The 3.55 MB part's bytes are equal |
| unit | `…::test_surgery__rejects_multi_part_edits` | `MultiPartEditError`, not a silent second rewrite |
| golden | `tests/golden/test_surgery_bytes.py::test_golden__f11_override_portfolio_O7` | Seed the flagship fixture `mutant__f11-formula-override__portfolio-O7__seed20260810.xlsx`; assert its `sha256` equals the pinned value **and** (R-GOLD-2 value assertion) that `'3. Portfolio'!O7` reads as a literal while the pinned blank declares `=SUM(C7:N7)` |
| determinism | `tests/determinism/test_det__mutant_reproduces_from_seed` | Two runs at different `TZ`, `PYTHONHASHSEED`, locale and cwd produce byte-identical mutants from `{seed, fault_model_version, harness_version}` |
| perf | `tests/perf/test_perf__PERF_MUT_SEED` | See the budget note below |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-P04** (existing) | Any code path re-serialises the received artifact | `injectors/openpyxl_save.py` | `test_nc__P04_artifact_never_reserialised`, three teeth. **The import-closure walk's banned set gains `cdfc.qualify` for `Workbook.save`, with `surgery.py`'s raw `zipfile.ZipFile(..., 'w')` as the one declared exception** — declared in the test, so widening it is a visible diff |
| **NC-Q30** (new) | **Mutants written by openpyxl instead of raw-zip surgery.** The mutant loses 24 parts and 19 `x14` validations, so the observability diff is a diff of the writer, not of the fault, and `U/G` collapses to 0 | `injectors/mutant_via_openpyxl.py` — swaps `seed_mutant` for a `load_workbook` / `wb.save` pair | `tests/negative/test_nc_predicate.py::test_nc__Q30_mutant_writer_is_raw_zip` — assert the mutant is `3,663,391 ± edit` bytes and not `65,877`; assert `n_validations == 54`; assert `len(parts_changed) == 1`. **Admission-side twin:** `test_nc__Q30b_surgery_writes_a_usable_mutant` — the surgery-written mutant loads, re-induces to the same schema constants, and its edited cell reads the new value |

**Performance budget — `PERF-MUT` is re-baselined here, and the reason is published.** The methodology's
`PERF-MUT` budget of **7,946 mutants/s** was measured by the v0 harness, **which had no observability
filter**. A per-mutant full recalculation over 505 formula cells will not sustain it. The budget therefore
splits, with an entry in `perf/BUDGET-CHANGES.md` carrying this reason and the date:

| Budget id | Subject | Baseline | Fail above / below |
|---|---|---|---|
| `PERF-MUT-SEED` | `surgery.seed_mutant` throughput | **7,946 mutants/s** (inherited, MEASURED) | below 5,000/s |
| `PERF-MUT-OBS` | observability filter throughput | **recorded at P6-B3; no budget until it exists** | first CI run after P6-B3 sets it; ±20% thereafter |

The optimisation that makes `PERF-MUT-OBS` tractable is named in advance so it is not discovered under
pressure: **recalculate only the transitive downstream cone of the edited cell** over the 505-node DAG,
not the whole grid. It is exact, not an approximation, because a cell outside the cone cannot change.
`tests/campaign/test_cone_recalculation_equals_full.py` asserts the cone result equals the full-grid result
on 200 randomly seeded mutants — a differential test between an optimisation and its specification.

**Effort.** 1.5 engineer-days.

---

#### P6-B3 — The observability filter

**Files created.**

```
src/cdfc/qualify/observability.py
src/cdfc/qualify/campaign.py             the Campaign record and its arithmetic
ci/no-bare-rate.sh                       §0.8(d)
reports/campaigns/<campaign_id>/         manifest.json · killed.jsonl · unobservable.jsonl ·
                                         indeterminate.jsonl (F18; each row names the not_run cells) ·
                                         unreachable.jsonl
```

**Public interface.**

```python
# src/cdfc/qualify/observability.py
class Observability(StrEnum):
    OBSERVABLE = "OBSERVABLE"
    UNOBSERVABLE = "UNOBSERVABLE"
    INDETERMINATE_OBSERVABILITY = "INDETERMINATE_OBSERVABILITY"   # F18. See below.

def classify(clean: ValueGrid, mutant: ValueGrid) -> tuple[Observability, frozenset[CellRef]]:
    """clean and mutant are the RECALCULATED grids produced by src/cdfc/calc/ under
    formula_source=FILING (see below), never the workbook's cached values.
    Returns the classification and the set of distinguishing cells.

    THREE-WAY, NOT TWO (F18):
      OBSERVABLE                   at least one cell value differs
      UNOBSERVABLE                 every cell value is equal AND no cell of the recalculation
                                   touched either grid's `not_run` map
      INDETERMINATE_OBSERVABILITY  the two grids are equal but the recalculation traversed a cell
                                   our evaluator could not compute (unimplemented function, cycle,
                                   pinned engine-disagreement exclusion). Excluded from O and
                                   REPORTED AS ITS OWN INTEGER `I`, with the cells named."""

# src/cdfc/qualify/campaign.py
@dataclass(frozen=True)
class ClassTally:
    G: int; U: int; I: int; O: int; R: int; K: int      # O = G - U - I

@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    by_fault_class: Mapping[str, ClassTally]
    fault_model_version: str
    fault_model_digest: str
    harness_version: str
    site_set_digest: str
    evaluator_version: str

    @property
    def totals(self) -> ClassTally: ...
    def kill_rate(self) -> Fraction:            # K/O.  raises CampaignArithmeticError if O == 0
    def reachable_kill_rate(self) -> Fraction:  # K/(O-R). raises if O == R
    def unobservable_rate(self) -> Fraction:    # U/G
    def indeterminate_rate(self) -> Fraction:   # I/G. F18: OUR APPARATUS, not the fault model
    def render(self) -> str:
        """SIX integers — G, U, I, O, R, K — plus U/G, plus I/G, plus the per-fault-class
        vector. NEVER a bare percentage, and NEVER U/G without I beside it: a build that
        cannot evaluate a cell would otherwise bank that cell's mutants as `unobservable`
        and RAISE its own K/O, because O = G - U - I is the denominator."""
```

**F18 — why the third value exists, and it is a FATAL repair.** `ValueGrid` carries a `not_run` map for
cells the evaluator could not compute. **A cell in `not_run` is identical in both grids by construction**,
so under the two-way classification every mutant whose only propagation path runs through such a cell was
marked `UNOBSERVABLE`, removed from `O`, and removed from the kill rate's denominator. `U/G` was then
published as *"the fraction of our mutants whose effect is invisible"* — a property of the **fault model** —
while it actually measured *"the fraction our evaluator cannot see"* — a property of **our apparatus**. And
because `O = G − U`, every such exclusion **raises** `K/O`: the measurement error was correlated with the
quantity being measured, in the direction that flatters us. **`I` is published beside `U/G` every time
either renders**, with the offending cells named, and the exit gate requires it.

**F19 — `formula_source`, the contract two phases were reading differently, in silence.** `recalculate`
induces its cell graph from a schema, and the schema is induced from the **pinned blank template**. An F11
mutant is *a cell the pinned blank declares a formula carrying a literal*; recalculating it **through the
template's formula graph overwrites the literal with the formula's value**, so clean and mutant grids are
identical and the plan's flagship fault class classifies `UNOBSERVABLE` — `O = 0` for F11, and
`Campaign.kill_rate()` then *raises* for `TEMPLATE_DIFF`, meaning **predicate #1 could never be admitted at
G2** while P9's exit gate stayed green because P9 does not use the observability filter. Two phases, two
meanings of "recalculate", both green in isolation.

> **DECIDED — `recalculate` takes an explicit `formula_source: Literal["TEMPLATE", "FILING"]`, and it is a
> required keyword with no default.** *Alternative it beat:* two functions with different names, rejected
> because a caller who wants the wrong one would simply call it. **Observability recalculates with
> `FILING`** — the filing's own `<f>` elements, materialised, so a cell carrying a literal stays a literal
> and its wrongness propagates. **`TEMPLATE_DIFF` recalculates with `TEMPLATE`** — that difference *is* the
> check. **Cross-document obligation:** the rule is published in `docs/EVALUATION-CONTRACT.md`, which
> `plan/03-phases-verdict.md` P5-B2 generates from `tools/gen_contract.py`; that document adds
> `formula_source` to the generated contract and its equality test, and `plan/02-phases-foundation.md`
> P3-B4 adds the parameter to `recalculate`'s signature. **A `recalculate` call under `src/cdfc/qualify/`
> that omits `formula_source` is a build error, asserted by `test_contract__formula_source_is_explicit`.**

**The single most important implementation note in P6.** The grid compared is the **recalculated** grid,
not the mutant file's cached values. A raw-zip edit does not update Excel's cached values, so a filter
reading cached values reports a difference at exactly the edited cell and nowhere else — it would measure
*the edit*, not *its propagation*, and would return `U = 0` on every campaign. `U/G` would then be a
plausible, confident, wrong number, and every `K/O` computed through it would be wrong in the direction
that flatters us. **NC-Q31 is this break.**

**The arithmetic, stated once.**

```
GENERATED   G
UNOBSERVABLE U   recalculated grid identical to clean, NO not_run cell traversed
                                                              — EXCLUDED from O, RETAINED on disk (§0.7)
INDETERMINATE I  recalculated grid identical to clean, but a not_run cell WAS traversed
                                                              — EXCLUDED from O, RETAINED, CELLS NAMED (F18)
OBSERVABLE  O = G − U − I
UNREACHABLE R    observable, but no distinguishing cell lies in any admitted predicate's read set
KILLED      K    at least one predicate returned FAIL on the mutant, under the P5 verdict model
KILL RATE   KR = K/O          ← the headline. NEVER K/G. NEVER K/(G−E). NEVER K/(G−U) with I folded in.
REACHABLE   RKR = K/(O − R)
UNOBS RATE  UR = U/G          ← a property of OUR operator mix, reported every run
INDET RATE  IR = I/G          ← a property of OUR EVALUATOR, reported every run beside UR (F18)
```

`MS = |killed| / (|mutants| − |equivalent|)` requires `|equivalent|`, which is undecidable in general.
`K/O` needs no such term **because our mutants are data: "observable" is a diff, measured by
recalculation, whereas "equivalent" is a theorem.**

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_campaign.py::test_campaign__kill_rate_is_over_observable` | `Campaign(G=100,U=40,I=0,O=60,R=0,K=30).kill_rate() == Fraction(1,2)`, not `30/100` |
| unit | `…::test_campaign__zero_observable_raises` | `O == 0 ⇒ CampaignArithmeticError`. A campaign in which nothing was observable has told us nothing and must not print `0.0` |
| unit | `…::test_campaign__render_never_bare` | `render()` output contains all six integers, `U/G`, `I/G` and the per-class vector; a regex for a lone `\d+(\.\d+)?%` finds none |
| **unit** | **`…::test_campaign__render_never_shows_UG_without_I`** | **F18.** Every rendering path that emits `U/G` emits `I` in the same string. Table-driven over `render()`, the measurement doc generator, and the library row |
| property | `tests/property/test_prop_g2_kill.py::test_prop__kill_rate_arithmetic` | Property: `K ≤ O ≤ G`, `U + I = G − O`, `R ≤ O`, `KR ∈ [0,1]` — **never > 1**. Generator: random campaign tallies including degenerate ones (`G=0`, `O=0`, `I=G`, `K=O`) |
| **unit** | **`tests/unit/test_observability.py::test_f11_mutant_is_observable`** | **F19, and it is the test the plan most needed and did not have.** Seed `mutant__f11-formula-override__portfolio-O7__seed20260810.xlsx`; assert `classify(...)[0] == OBSERVABLE` and that the distinguishing-cell set **contains `'3. Portfolio'!O7` itself**. Fails on any build whose observability recalculation uses `formula_source=TEMPLATE` |
| **unit** | **`…::test_observability_recalculates_with_filing_formulas`** | `classify` is unreachable from any call site passing `formula_source="TEMPLATE"`; asserted on the call graph, not on a comment |
| **unit** | **`…::test_indeterminate_is_not_unobservable`** | A mutant whose only propagation path crosses a pinned engine-disagreement cell classifies `INDETERMINATE_OBSERVABILITY`, appears in `indeterminate.jsonl` with that cell named, and is **absent** from both `O` and `U` |
| golden | `tests/golden/test_campaign_v0_delta.py::test_golden__v0_naive_score_is_restated` | Load `fixtures/baselines/l4-v0.json` (19,782 / 3,574 / 22); assert the module **refuses** to compute `K/(G−E)` and that the restatement note names the mechanism. R-GOLD-2 value assertion: the per-operator table's `round_to_int` row is the only one with `equivalent > 0`, and equals `22` |
| differential | `tests/differential/test_diff__cone_vs_full_recalculation.py` | The downstream-cone optimisation equals the full-grid recalculation on 200 seeded mutants |
| campaign | `tests/campaign/test_campaign__fme_v3_reproduces.py` | A full FME campaign under `v3` reproduces `U/G` and `K/O` per class to the integer across two runs |
| perf | `tests/perf/test_perf__PERF_MUT_OBS` | Sets the baseline at P6-B3 and enforces ±20% thereafter |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q05** (existing) | `MS = killed/(mutants − equivalent)` with equivalents excluded from both terms. **REAL: the harness v1 printed 100.1%** | `injectors/kr_over_generated.py`, `injectors/kr_double_exclusion.py` | `test_nc__Q05a_impossible_score_raises` against `fixtures/baselines/harness-v1-impossible.json`; `test_nc__Q05b_never_a_bare_percentage`; `test_nc__Q05c_observability_filter_reports_its_own_rate` |
| **NC-Q31** (new) | **The observability filter reads the mutant's cached values instead of recalculating.** Returns `U = 0` on every campaign; every `K/O` becomes `K/G` wearing the wrong label | `injectors/observability_cached_grid.py` | `tests/negative/test_nc_predicate.py::test_nc__Q31_filter_recalculates` — run a campaign whose true `U > 0` (F06 round-to-integer inside `τ(n)` guarantees members); assert `U > 0` un-injected and `U == 0` injected, and assert the classification's distinguishing-cell set is non-empty **downstream** of the edit, not only at it |
| **NC-Q37** (new) | **An unobservable mutant is destroyed rather than retained with its reason.** `U/G` becomes unauditable and P10 loses its feedstock | `injectors/discard_unobservable.py` | `tests/negative/test_nc_predicate.py::test_nc__Q37_unobservable_are_retained` — assert `reports/campaigns/<id>/unobservable.jsonl` has exactly `U` rows, each carrying `mutant_sha256`, `operator_id`, `site` and a non-empty `reason`; assert the file's row count equals the manifest's `U` |
| **NC-Q60** (new, **F18**) | **A cell our evaluator could not compute is counted as evidence that the mutant is invisible.** `not_run` cells are identical in both grids by construction, so the mutant is banked as `UNOBSERVABLE`, leaves `O`, and **raises** `K/O`. The published `U/G` then describes our apparatus while claiming to describe the fault model | `injectors/notrun_counts_as_identical.py` — folds `INDETERMINATE_OBSERVABILITY` back into `UNOBSERVABLE` | `tests/negative/test_nc_predicate.py::test_nc__Q60_unevaluable_cells_do_not_become_unobservable` — build a campaign with at least one pinned engine-disagreement cell on a propagation path; assert un-injected that `I > 0`, that those mutants are absent from `U`, and that `render()` shows `I`; assert injected that `I == 0`, `U` grew by exactly that count and `K/O` rose. **Admission-side twin:** `test_nc__Q60b_fully_evaluable_propagation_is_observable` — a mutant propagating only through evaluable cells is `OBSERVABLE`, never `INDETERMINATE` |
| **NC-Q61** (new, **F19**) | **Observability recalculates with the TEMPLATE's formulas**, so an F11 formula-override mutant is overwritten by the very formula it deleted, the flagship class classifies `UNOBSERVABLE` with `O = 0`, and `TEMPLATE_DIFF` becomes unadmittable at G2 — twelve weeks before anyone finds out | `injectors/observability_uses_template_formulas.py` — flips `formula_source` to `TEMPLATE` inside `classify` | `tests/negative/test_nc_predicate.py::test_nc__Q61_observability_uses_filing_formulas` — assert un-injected `classify(f11_pair) == OBSERVABLE` with `'3. Portfolio'!O7` in the distinguishing set and `by_fault_class["F11"].O > 0`; assert injected `UNOBSERVABLE` and `O == 0`. **Admission-side twin:** `tests/campaign/test_g2_admits_template_diff.py` — `TEMPLATE_DIFF` reaches G2 with `O > 0` and a computed `K/O` rather than a `CampaignArithmeticError` |

**Effort.** **3.5 engineer-days** (3 as originally estimated, +0.5 for the three-way classification, the
`indeterminate.jsonl` writer and the `formula_source` plumbing — F18 and F19).

---

#### P6-B4 — The site universe, the primary arm and the control arm

**Files created.**

```
src/cdfc/qualify/sites.py
```

**Public interface.**

```python
# src/cdfc/qualify/sites.py
@dataclass(frozen=True)
class SiteSet:
    universe: frozenset[StableKey]
    primary: frozenset[StableKey]
    control: frozenset[StableKey]
    control_fraction: Fraction
    rng_seed: int
    digest: str            # sha256 over RFC 8785 of the three sorted key lists

def site_universe(schema: TemplateSchema) -> frozenset[StableKey]:
    """== schema.field_surface(), minus P3's pinned engine-disagreement exclusions.
    Takes NO predicate parameter. Its import closure does not reach cdfc.predicates."""

def partition(universe: frozenset[StableKey], p: AdmittedPredicate | PredicateEnvelope,
              schema: TemplateSchema, *, control_fraction: Fraction = Fraction(1, 10),
              rng_seed: int) -> SiteSet:
    """primary := universe ∩ read_set(p)
       control := deterministic sample of universe \\ upstream_closure(read_set(p)),
                  |control| >= ceil(control_fraction * |primary|)"""
```

**Why the control arm excludes the upstream closure and not merely the read set** is §0.4(b), and it is
what makes the correct spurious-fire threshold **exactly zero** rather than a fudge factor.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_sites.py::test_sites__universe_equals_field_surface` | `site_universe(fme) == styles_mask.field_surface(fme)` as sets, and `len(...) == 3747` when no engine-disagreement exclusions are pinned |
| unit | `…::test_sites__universe_takes_no_predicate` | `inspect.signature(site_universe).parameters.keys() == {"schema"}` |
| unit | `…::test_sites__control_excludes_upstream_cone` | `control ∩ upstream_closure(read_set(p)) == ∅` for all 280 FME predicates |
| unit | `…::test_sites__control_is_at_least_ten_percent` | `len(control) >= ceil(0.10 * len(primary))`, and `> 0` whenever `primary` is non-empty |
| property | `tests/property/test_prop_sites.py::test_prop__partition_is_disjoint_and_bounded` | Property: `primary ∩ control == ∅`, `primary ∪ control ⊆ universe`. Generator: random `read_set` subsets of the FME field surface, sizes 1…3,747 |
| determinism | `tests/determinism/test_det__site_set_reproduces_from_seed` | Same `rng_seed` ⇒ same `digest` across TZ, hash seed, locale, cwd |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q06** (existing) | **Mutation sites sampled from the predicates' read set. REAL: 100.0% on 3,574 mutants — the degenerate-baseline failure, committed by the harness built to detect it** | `injectors/sites_from_read_set.py` | `test_nc__Q06a_site_set_is_the_field_surface` — restated in its exact form by §0.4: the *universe* equals the mask's field surface and `site_universe`'s import closure does not reach `cdfc.predicates`. `test_nc__Q06b_control_arm_exists`. `test_nc__Q06c_flag_everything_fails_the_control_arm` |
| **NC-Q32** (new) | **The control arm draws sites from inside the predicate's upstream cone**, so legitimate propagation is counted as a spurious fire and the threshold has to be softened to a fudge factor — which then hides a real flag-everything predicate | `injectors/control_from_read_set_complement.py` — excludes only the read set, not the cone | `tests/negative/test_nc_predicate.py::test_nc__Q32_control_excludes_the_cone` — take a cross-sheet-equality predicate reading `'2. Summary'!F5`; seed an F13 mutant at its upstream source on `'3. Portfolio'`; assert un-injected that the site is **not** in `control`, and injected that it **is** and produces a spurious fire. **Admission-side twin:** `test_nc__Q32b_a_genuine_outside_site_is_in_control` — a Complaints-sheet cell with no path to the predicate is in `control` |

**Effort.** 1.5 engineer-days. Remaining 1 day: the measurement, `docs/measurements/P6-fault-model-v3.md`,
the ledger row and the DoD.

---

### The measurement P6 produces

| Field | Value |
|---|---|
| **Metric** | `U/G` for our operator mix, and `K/O` per fault class — both as integer pairs, plus `R` **and plus `I/G`, the fraction our own evaluator could not adjudicate (F18). `U/G` never renders without `I` beside it** |
| **Denominator** | generated mutants `G` (per class and total), over the FME field surface of 3,747 cells |
| **Warrant** | **MEASURED** |
| **Produced by** | `src/cdfc/qualify/campaign.py` |
| **Command** | `cdfc seed --template 7d9a1960 --fault-model v3 --seed 20260810 && cdfc qualify --gate G2 --campaign <id>` |
| **Caveat that ships with it** | *"rejects K of O observable defects seeded under fault model v3, of which U of G were discarded as unobservable."* It does **not** license *"detects X% of real filing errors"* — the bridge is the coupling effect and there is no coupling study for financial filing data |
| **What did not exist before** | `U/G` for our operator mix. The literature's 46.8% is a property of a different suite. And `K/O` per class where "killed" means a `FAIL` under the eight-state verdict model, rather than a boolean |

A second row is published beside it and is not optional: **the restatement of v0's `18.09%`** — the
mechanism by which `K/(G − E)` and `K/O` differ, and the observation that every arithmetic operator killed
at exactly 18.1%, identical to the fraction of sites inside the field graph. For identity predicates
**kill rate measures predicate *reach*, not predicate *quality*, and the report says which it is showing.**

### Exit gate — a boolean, evaluable by someone who did not do the work

```
P6 EXITS iff ALL of:
  1. `make campaign` produces a Campaign over the FME workbook under fault model v3 in which
     O > 0, U > 0 and K > 0, and the per-fault-class vector has an entry for each of F01–F14
     — AND, F19: by_fault_class["F11"].O > 0, so that the flagship class reaches the
     denominator at all. An F11 row with O == 0 fails this gate; it does not pass with a note.
  2. reports/campaigns/<id>/unobservable.jsonl has exactly U rows, each with a non-empty reason,
     AND indeterminate.jsonl has exactly I rows, each naming the not_run cells that produced the
     classification (F18). G == U + I + O on every class row and on the totals.
  3. `PERF-MUT-SEED` >= 5,000 mutants/s on perf/baseline.ci.json; `PERF-MUT-OBS` baseline recorded.
  4. `make nc-sweep` reports NC-Q05, NC-Q06, NC-Q30, NC-Q31, NC-Q32, NC-Q33, NC-Q37, NC-Q60,
     NC-Q61 and NC-E08 as caught — and reports `guards_flipped == guards_expected_to_flip` for
     those entries, not merely `entries_caught` (F4: an entry caught by its weakest guard is an
     entry whose load-bearing guard was never observed red). For each, DoD line C4 cites the
     sweep report's row — `reports/negative-control-sweep.json` at commit <sha>, which carries
     the captured assertion text and the pytest node id — rather than a pasted quotation (F31).
  5. `make mutation-pr` reports K/V >= 0.90 for qualify/observability.py and qualify/sites.py
     (Tier V, §0.8(c)) and >= 0.85 for the rest of qualify/, with E printed and every argument
     linked, and mutmut's own I (incompetent) and T (timeout) counts listed with T's mutant ids
     named. (mutmut's I is not the campaign's INDETERMINATE_OBSERVABILITY; the two never render
     in the same table.)
  6. docs/measurements/P6-fault-model-v3.md published, containing U/G, I/G, K/O per class, R, the
     named cells behind every I, and the v0 restatement with its mechanism.
  7. `ci/no-bare-rate.sh` and `ci/no-openpyxl-writer.sh` are in ci/GATES.md and have each been
     observed red against their planted control.
```

### What it kills if it fails

**If the observability filter cannot be founded** — because P3's G-EVAL failed past its 25-cell tolerance —
the phase ships `K/G` **labelled reach, not quality**, every downstream G2 threshold is restated against
`G`, and the caveat prints beside every number. Smaller, honest, still a rejector. The renderer already
refuses a bare percentage, so the label cannot be dropped in transit.

**If `PERF-MUT-OBS` makes a full campaign impractical** (the realistic failure: 19,782 mutants × a
505-cell recalculation), the response is the downstream-cone optimisation, then **stratified sampling of
the site universe with the sampling rule published and the sample size in every quoted denominator** — not
a smaller fault model. Reducing the operator set to make the number look better is the manipulation this
project bans; reducing the sample and saying so is arithmetic.

**If the fault model cannot be authored honestly** — the failure mode is a taxonomy whose classes are
chosen because they are easy to seed — the mitigation is structural and already in place: F10, F12 and F14
are classes our own predicates *cannot* catch, and a taxonomy containing none of them would be visible as
a per-class kill vector with no zeroes in it. **A per-class vector that is uniformly high is evidence the
model is too weak, not that the predicates are good.**

### Effort

**10.5 engineer-days** (was 10; +0.5 at B3 for F18's three-way classification and F19's `formula_source`
plumbing). Assumption: one competent engineer, fluent in Python, comfortable with raw OOXML,
working from this document, ~6 productive hours a day, no context switching, with P3's evaluator and P5's
verdict model already green. Split: B1 3 · B2 1.5 · B3 **3.5** · B4 1.5 · measurement, doc, ledger and
DoD 1.

---

# P7 — THE FIVE GATES (MINUS G4), THE REGISTRY, ADMISSION · 16 engineer-days

### What it settles

**Whether the rejector is real.** The first five-gate attrition funnel over the 280 harvested FME
predicates, with every rejection's gate and measured number published.

Stated at its true current strength: **the gate has exactly one demonstrated rejection** — five of ALR's
six bound predicates assert only `≥ −1e17` over 1,428 cells and are refused — **and whether it rejects
anything on the FME workbook is unmeasured**, since 19 of that workbook's 24 bounds are a real `≥ 0`.
P7 converts that into a measurement, and it also disposes of a set nobody has looked at: **the five FME
bounds whose `formula1` is not `0`, covering 68 cells** (§0.9). *If the funnel rejects nothing on FME,
that is a publishable measurement and the surfaces say exactly that.*

### Entry criteria

| # | Must be true | Why |
|---|---|---|
| E7.1 | **P6 complete.** A `Campaign` reproduces on the FME workbook; the fault model is at `v3` with a stable digest | G2 is the expensive gate and its harness is P6 |
| E7.2 | **P4 complete.** `schema_keys` machine-checked against the CEL AST **both ways** on 280 of 280; `celpy` (or `cel-expr-python`) pinned by wheel hash with G-CELPY decided | G1's key check and G3's SMT translation both read the AST. An inexact `schema_keys` makes the pre-flight set an estimate and G1 a guess |
| E7.3 | **P4-B1 has confirmed the absence of a `REJECTED` predicate state** (audit V.7.5). Rejected candidates live in the `rejection` table with `predicate_id NULL` | The schema is written in this phase and cannot be written on an unconfirmed belief |
| E7.4 | `obligations.yaml` seeded — P7-B1 | G0 needs a `verbatim_quote` and a `char_span` per obligation |
| E7.5 | **The `TEMPLATE-COMPUTED` oracle exists** (§0.3, specified at P8-B2) — required before **P7-B3** only | G1 must execute against a filing; G3ᵉ must measure firing on a clean corpus |
| E7.6 | The regulation PDF and the 399-circular corpus are on disk and content-addressed, with the 10 scanned images declared | G0's `source.find(quote)` runs against normative text, not against a summary of it |
| **E7.7** | **`corpus/instruments/fm-regulations-2025.text.json` exists — an authoritative normalised text with stable character offsets, produced by the dual-extraction agreement harness. This is built by P7-B0 below, not assumed (F35).** Before this pass, E7.6 asserted the artifact as a precondition and **no build before P12-B1 created it**: G0's whole mechanism is a character span into a normalised text, five phases before the phase that produced one | An offset into a text nobody pinned is not a span. `test_obligations__span_matches_quote` is unrunnable without it |
| **E7.8** | **Every candidate entering the pipeline carries a non-empty `claims_fault_classes`, inside `envelope_projection()` and therefore inside `code_sha256`** (F1; the field is added by `plan/03-phases-verdict.md` P4-B1 — see §0.8(f)) | G2's registry bar is computed over the classes the predicate claims. Without the field the claim is read off the witnesses G2 itself selects **after** the campaign has run, and the predicate chooses the denominator of its own quality score |

### Builds

---

#### P7-B0 — The instrument text source, with stable offsets · NEW, moved here from P12-B1 (F35)

**Why it moved, stated as the finding.** G0's entire mechanism is `source_text.find(quote)` at an exact
character span. That requires an **authoritative normalised text with stable offsets**, produced by a
dual-extraction agreement harness with a disputed-region exclusion rule — the **D5 differential**. It was
specified at `plan/06-phases-model-and-clause.md` P12-B1, **five phases downstream of its only consumer**,
and this document's E7.6 asserted the artifact as a precondition without naming the build that satisfies
it. **DECIDED: the build moves to its consumer.** *Alternative it beat:* leaving it at P12-B1 and having
P7 hand-transcribe spans from a PDF viewer — rejected because a span nobody can re-derive is not evidence,
and because it would leave `test_obligations__span_matches_quote` unrunnable for five phases.
`plan/06-phases-model-and-clause.md` P12-B1 **references** the artifact instead of creating it, which is
also what makes its 2-day estimate plausible (F41).

**Files created.**

```
src/cdfc/qualify/textsource.py                   two extractions + agreement + disputed-region exclusion
corpus/instruments/fm-regulations-2025.text.json normalised text, char offsets, per-page map, GENERATED
corpus/instruments/MANIFEST.json                 sha256 of each source PDF and of each extraction
docs/measurements/P7-textsource.md               the agreement rate and the excluded regions
```

**Contract.** Two independent extractions of the pinned regulation PDF; normalise (NFKC, whitespace
collapse, ligature expansion) with the transformation list recorded; compare sentence-wise. **A region on
which the two extractions disagree is EXCLUDED from the addressable text and listed with its page number**,
and a quote landing in an excluded region is `g0.quote_in_disputed_region` — a **sixth** closed G0 reason,
not a silent failure to locate. `ExtractionManifest` carries `{extractor, version, sha256, n_sentences,
n_disputed}`.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| differential | `tests/differential/test_diff__two_extractions_agree.py` | The D5 differential: sentence-level agreement rate published, never assumed; disagreements enumerated with page numbers |
| unit | `tests/unit/test_textsource.py::test_textsource__offsets_are_stable_under_regeneration` | Regenerating from the same PDF digest reproduces byte-identical offsets |
| unit | `…::test_textsource__disputed_region_is_not_addressable` | A span intersecting a disputed region raises rather than returning text |
| golden | `tests/golden/test_textsource_pins.py` | First, median and last sentence pinned by value (R-GOLD-2), plus `n_disputed` |

**Negative control.** **NC-Q47** (new) — *the disputed-region exclusion is dropped and the first
extraction is used alone*, so a span resolves against text the second extractor never saw. Injector
`injectors/textsource_single_extraction.py`. Guard
`tests/negative/test_nc_predicate.py::test_nc__Q47_disputed_regions_are_excluded` — assert un-injected that
a quote inside a known disputed region is refused with `g0.quote_in_disputed_region`, and injected that it
is accepted. **Admission-side twin:** a quote in an agreed region locates and passes.

**Effort.** **1.5 engineer-days.** It is the D5 differential, and `plan/08-adversary.md` F41 measures it at
3–4 days when bundled with the draw, the power table and the pre-registration; alone, with no experiment
attached, 1.5 is the honest figure and the risk is stated: if the two extractors disagree on more than 5%
of sentences, the excluded set becomes large enough that **G0's addressable text is published as a fraction
of the instrument** and that fraction ships beside every G0 attrition figure.

---

#### P7-B1 — The obligations table, the candidate loader, and the rejection record

**Files created.**

```
obligations.yaml                              hand-maintained, source='hand'
src/cdfc/predicates/obligations.py            loader + validator
src/cdfc/qualify/template_instrument.py       GENERATES the template-derived instrument text (F9)
corpus/instruments/template-<sha8>.text.json  the pinned blank as an addressable instrument, GENERATED
src/cdfc/qualify/result.py                    GateId, GateOutcome, RejectionRow, QualificationRecord
src/cdfc/qualify/errors.py                    the closed error hierarchy
migrations/00X_qualification.sql              predicate · qualification · rejection · host_function
                                              · registry_root, exactly as spec §III.4.2
```

**Public interface.**

```python
# src/cdfc/predicates/obligations.py
#
# ARBITRATION C2 -- THE `source` DISCRIMINATOR.  A harvested predicate implements a relation the
# REGULATOR'S TEMPLATE encodes; a hand-authored one implements a clause the STATUTE states.  BOTH ARE REAL
# OBLIGATIONS.  They are not the same kind of thing, and collapsing them is what made F9 irreconcilable.
class ObligationSource(StrEnum):
    STATUTE  = "STATUTE"    # a `shall` in an instrument the Authority issued
    TEMPLATE = "TEMPLATE"   # a relation the regulator's own PINNED BLANK encodes (F9)

@dataclass(frozen=True)
class Obligation:
    obligation_id: str          # "OBL-014"  |  "OBL-TEMPLATE-3-Portfolio-O7"
    source: ObligationSource    # REQUIRED. There is no default and no None.  C2.
    instrument_id: str          # "fm-regulations-2025" | "template-7d9a1960"
    frbr_uri: str | None        # None until L1b ships (P13-B2); always None for source=TEMPLATE
    eId: str | None
    quote: str                  # VERBATIM
    span: tuple[int, int]       # exact character span into that instrument's normalised text
    ingest_source: Literal["hand", "l1b", "harvest"]   # HOW THE ROW GOT HERE -- not what it IS.
    # ^ renamed from `source` by C2, which needs that name for the STATUTE|TEMPLATE discriminator.
    #   Two different questions; one of them was about to be answered by a field name.

def load(path: Path = Path("obligations.yaml")) -> Mapping[str, Obligation]: ...

# src/cdfc/qualify/template_instrument.py
def emit(schema: TemplateSchema) -> InstrumentText:
    """Render the PINNED BLANK as an addressable instrument, deterministically:
    one line per formula cell   '<sheet>!<ref>\\t<formula text>'
    one line per validation     '<sheet>!<sqref>\\t<type>\\t<formula1>'
    sorted by (sheet ordinal, row, column). Content-addressed; the digest enters
    qualified_against. This is what makes source.find(quote) MEANINGFUL for a
    harvested candidate, whose 'quote' is the construct it was derived from."""

# src/cdfc/qualify/result.py
class GateId(StrEnum):
    G0 = "G0"; G1 = "G1"; G3P = "G3p"; G2 = "G2"; G3E = "G3e"; G4 = "G4"

GATE_ORDER: Final[tuple[GateId, ...]] = (GateId.G0, GateId.G1, GateId.G3P,
                                         GateId.G2, GateId.G3E, GateId.G4)

@dataclass(frozen=True)
class GateOutcome:
    gate: GateId
    passed: bool
    measured: Mapping[str, object]     # written verbatim into qualification.g<n>
    reason: str | None                 # required iff not passed; from the closed reason set below
    evidence_sha256: str | None        # a Z3 witness, a campaign id, a corpus id

@dataclass(frozen=True)
class RejectionRow:
    candidate_sha256: str
    predicate_id: str | None           # NULL — there is no REJECTED predicate state (E7.3)
    obligation_id: str
    rejecting_gate: GateId
    measured: Mapping[str, object]
    cells_would_have_covered: int
    rejected_at: datetime
```

**F9 — what G0 does with a harvested candidate. DECIDED, because the plan did not say, and P7's headline
number depends on it.**

> **The hole.** G0's six closed rejection reasons all presuppose a clause. `plan/03-phases-verdict.md`
> P4-B1 types the envelope's `clause` as `Clause | None` and its `obligation_id` as `str | None`, and the
> nine harvest classes are derived from the workbook's own formulas and validations — **they cite no
> regulation and have no verbatim quote.** Nothing in any document said what G0 does with them. Both
> branches are broken and both pass their local tests: **if G0 rejects them, all 280 die at stage one, ALR's
> five bounds never reach G3, and D-REJECT — the flagship demonstration that the gate is not decorative — is
> unreachable.** If G0 skips them, stage one of the funnel reads `280 → 280`, which is a green number
> carrying no information, and *a gate that does not apply to the population it is run over is reporting a
> pass it did not compute.*

**DECIDED — a harvested candidate gets a template-derived obligation, and G0 runs over it for real.**
Its `obligation_id` is `OBL-TEMPLATE-<sheet>-<ref>`, its `source` is **`TEMPLATE`**, its `instrument_id` is
the pinned blank's `template-<sha8>`, its `quote` is the **verbatim formula or data-validation text** the
harvester read, and its `span` is that text's exact offset into `template_instrument.emit(schema)`.
`instrument_text.find(quote)` is then meaningful, deterministic and **falsifiable**: a candidate whose
recorded construct is not present in the pinned blank at the recorded offset is rejected
`g0.quote_not_located`, which is precisely the check that catches a harvest run against a different template
version.

**G0 runs for real, and the question it asks is a real question.** Against a `source: TEMPLATE` obligation
G0 asks: **does this predicate faithfully implement the relation it claims to implement?** That is a genuine,
failable check. The rejected alternative — `03`'s `SKIPPED_NOT_APPLICABLE` branch — **made G0 decorative for
all 280 candidates, and a gate stage that cannot fail is this product's own failure mode wearing a gate's
clothes.**

*Alternative it beat:* the counted `SKIPPED_NOT_APPLICABLE` column. Rejected because it buys the funnel an
honest first row at the price of leaving 280 of 280 predicates with **no provenance chain to any artifact
at all** — and because the skip is the vacuous pass in its purest form. The counting discipline that branch
would have bought is kept anyway: **stage one of the funnel renders three integers — `entered / skipped /
survived` — and `skipped` is never counted as a survivor**, whatever its value (it is `0` under this
ruling, and the column exists so that a future source cannot enter the funnel silently).

**Two consequences that must be published rather than absorbed.**

1. **THE PUBLISHED FIGURE IS TWO NUMBERS, NEVER ONE (arbitration C2, `03`'s honesty requirement grafted
   onto this branch — and it is strictly better than either branch alone).** A P7 subordinate measurement
   (see *The measurement P7 produces*) renders **both**, on the same line, or neither:

   | Published number | Today |
   |---|---|
   | `predicates_with_a_STATUTE_obligation / 280` | **`0 / 280`** |
   | `predicates_with_a_TEMPLATE_obligation / 280` | **`280 / 280`** |

   **The honest statement survives verbatim: *no harvested predicate yet implements a statutory clause.***
   Under `04`'s branch alone the old single figure `0/280` was **wrong by 280**; under `03`'s branch alone it
   was misleading. Under the two-number form both numbers are true and neither can be read as the other.
   A template-derived obligation is a real provenance chain to the regulator's own artifact and it is
   **not** a statutory grounding; **the surfaces must never add the two counts together**, and must never
   render one without the other — `test_p7__both_obligation_counts_render_or_neither_does`.
2. **`source` scopes the uniformity guard.** NC-Q35 raises `SuspiciousUniformityError` when G0
   reports `provisos_total == 0` across all candidates — correct for statutory prose, and **wrong for
   template-derived obligations, where zero provisos is the truth.** The guard applies to
   `source == STATUTE` only, and its own test asserts that scoping, so a build cannot silence it by
   relabelling.

**`cells_would_have_covered` is not optional and is not cosmetic.** It is what turns a rejection into
`no_predicate.failed_qualification` and into the report's `counterEvidence[]`. *We were going to discard
exactly the information an audit-documentation standard makes mandatory.*

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_obligations.py::test_obligations__span_matches_quote` | For every row, `instrument_text[span[0]:span[1]] == quote`, resolved against the row's own `instrument_id`. A row that does not is a data error and fails at load |
| unit | `…::test_obligations__ids_are_stable_across_ingest_source_flip` | Setting `ingest_source='l1b'` and populating `eId` preserves every `obligation_id` |
| **unit** | **`…::test_obligations__source_is_required_and_closed`** | **F9 / C2.** `ObligationSource` has exactly two members, `STATUTE` and `TEMPLATE`; a row without `source` fails at load; `source == TEMPLATE ⇒ frbr_uri is None` and `instrument_id.startswith("template-")`; `source` and `ingest_source` are **distinct fields** and neither is derived from the other |
| **unit** | **`…::test_p7__both_obligation_counts_render_or_neither_does`** | **C2.** `predicates_with_a_STATUTE_obligation / 280` and `predicates_with_a_TEMPLATE_obligation / 280` render **together or not at all**; raises `UnpairedObligationCount` otherwise. *One number alone is the defect C2 exists to close, in either direction* |
| **unit** | **`tests/unit/test_template_instrument.py::test_ti__every_harvested_candidate_locates`** | For all 280 FME harvested candidates, `emit(schema)` contains the candidate's recorded construct at its recorded span. **Admission-side twin of the rejection below** |
| **unit** | **`…::test_ti__a_stale_construct_is_not_located`** | Re-point a candidate at a formula the pinned blank does not carry; assert `g0.quote_not_located`. **This is the reject path that branch (a) had to make reachable, and it is the template-churn regression check** |
| **determinism** | **`tests/determinism/test_det__template_instrument_reproduces`** | `emit(schema)` is byte-identical across TZ, hash seed, locale, cwd; its digest enters `qualified_against` |
| contract | `tests/contract/test_contract__no_rejected_predicate_state` | The `predicate.state` enum is exactly `{ACTIVE, PROVISIONAL, QUARANTINED, WITHDRAWN}`; `rejection.predicate_id` is nullable. This is E7.3 asserted rather than believed |
| contract | `tests/contract/test_contract__gate_order_is_the_decided_order` | `GATE_ORDER == (G0, G1, G3p, G2, G3e, G4)`. **A tuple, not a comment** |
| unit | `…::test_rejection__cells_would_have_covered_is_required` | A `RejectionRow` without it raises at construction |

**Negative control.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q48** (new, **F9**) | **A clause-less candidate is waved through G0** — the gate returns `passed=True` without computing anything, and stage one of the funnel reads `280 → 280`, a constant wearing the shape of a measurement | `injectors/g0_skips_clauseless.py` — returns a passing `GateOutcome` when `cand.clause is None` | `tests/negative/test_nc_predicate.py::test_nc__Q48_disposition_of_a_clauseless_candidate_is_specified_and_counted` — assert un-injected that **every** candidate has exactly one G0 disposition drawn from the closed set, that `entered == skipped + rejected + survived` at stage one, that `skipped` is never added to survivors, and that `docs/measurements/P7-attrition.md` renders all three integers; assert injected that a candidate reaches G1 with no `g0` block in its qualification record. **Admission-side twin:** a template-derived candidate whose construct locates passes G0 with `provisos_total == 0` and no error |
| **NC-Q34** (new) | **The gate pipeline runs out of order** — G2's mutation budget is spent before G0's free structural check, so a candidate with an undeclared proviso consumes a campaign, and worse, a candidate Z3 would have proved unfalsifiable is admitted on an expensive number | `injectors/gate_order_shuffled.py` — reverses `GATE_ORDER` | `tests/negative/test_nc_predicate.py::test_nc__Q34_order_is_enforced_by_shape` — feed a candidate that fails G0 **and** would consume a campaign; assert un-injected that **zero mutants were generated** (spy on `surgery.seed_mutant`), and injected that the spy fired. **Asserting on the spy rather than on the outcome is the point: the outcome is the same either way, and the cost is the thing being gated** |

**Effort.** **2.5 engineer-days** (was 2; +0.5 for `template_instrument.py`, the `ObligationSource` split (C2) and
their tests — F9).

---

#### P7-B2 — G0 scope faithfulness, and G1 executes and binds

**Files created.**

```
src/cdfc/qualify/g0_scope.py
src/cdfc/qualify/g1_binds.py
src/cdfc/qualify/provisos.py          the deterministic marker detector
docs/PROVISO-MARKERS-v1.md            versioned marker list + normalisation table
fixtures/predicates/broken/P-NC11a__undeclared-proviso.yaml     (existing catalogue fixture)
fixtures/predicates/broken/P-NC11b__quote-not-verbatim.yaml     (existing catalogue fixture)
fixtures/predicates/broken/P-NC17a__quote-ambiguous.yaml        (new)
fixtures/predicates/broken/P-NC21a__unresolved-key.yaml         (new)
fixtures/predicates/good/                                       the admission-side twins
```

**Public interface.**

```python
# src/cdfc/qualify/g0_scope.py
def check(cand: PredicateEnvelope, instruments: InstrumentStore) -> GateOutcome: ...

# src/cdfc/qualify/provisos.py
@dataclass(frozen=True)
class DetectedProviso:
    kind: Literal["proviso", "exception", "cross_reference", "explanation", "delegation"]
    text: str
    span: tuple[int, int]
    marker: str          # the marker that matched, for auditability

def detect(span_text: str, offset: int, markers_version: str = "v1") -> tuple[DetectedProviso, ...]: ...

# src/cdfc/qualify/g1_binds.py
def check(cand: PredicateEnvelope, schema: TemplateSchema, facts: FactTable,
          runtime: CelRuntime, hostfns: HostFunctionRegistry) -> GateOutcome: ...
```

**G0's closed rejection reasons.** Each implies a different remedy, which is the admission test for a
reason code.

| Reason | Condition | Remedy |
|---|---|---|
| `g0.quote_not_located` | `source_text.find(quote) == -1` | Fix the quote. Zero model cost, at the boundary |
| `g0.quote_ambiguous` | `source_text.count(quote) > 1` **and** the declared span does not select one occurrence | Widen the quote or fix the span. *"`find` succeeds" is not "locates deterministically"* |
| `g0.span_mismatch` | `source_text[span[0]:span[1]] != quote` | The span and the quote disagree; one is a lie |
| `g0.proviso_undisposed` | a `DetectedProviso` in the span with `disposal ∉ {IMPLEMENTED, DECLARED}` | Implement the branch or declare the emission |
| `g0.proviso_arithmetic` | `provisos_total != provisos_implemented + provisos_declared` | The record does not sum; it is not a record |
| `g0.declared_proviso_missing_emission` | `disposal == DECLARED` with no `emits` | A declaration that emits nothing is a silent drop wearing a label |
| **`g0.quote_in_disputed_region`** | the span intersects a region the two extractions of P7-B0 disagree on | Re-quote from an agreed region, or accept that this obligation is not addressable and record it. **A span into text one extractor never saw is not a span** |

**Every reason above resolves against the candidate's own `instrument_id`** — the regulation's normalised
text for `source == STATUTE`, the pinned blank's `template_instrument.emit(schema)` for
`source == TEMPLATE` (F9, C2). **There is no seventh outcome and no skip.** `check()` raises
`UnsourcedObligationError` on a candidate whose obligation is missing or whose `source` is unset, so a future
predicate kind cannot enter the funnel by defaulting into a pass.

**The marker list is lexical, versioned, and its recall is measured — not assumed.** Markers for Indian
statutory drafting: `Provided that` · `Provided further that` · `Provided also that` · `Notwithstanding` ·
`subject to` · `except` · `unless` · `save as` · `Explanation` · `as may be specified` ·
`in such manner as specified by the Authority` (the reg 51(1) delegation hook), plus cross-reference
patterns over `regulation \d+`, `sub-regulation \(\d+\)`, `clause \(\w+\)`, `Schedule`.

Two things to say plainly. **(a) Regex over statutory text is the right tool and is not what
`ci/no-regex-over-xml.sh` forbids** — that gate scans `src/cdfc/ingest/` and `src/cdfc/schema/` and exists
because a lexical matcher over XML is a build error. Normative prose is not XML. **(b) The detector's
recall is below 1 and the phase measures it**: 50 spans hand-labelled by a named person, dated, in
`fixtures/predicates/proviso-labels.json`; `g0_marker_recall` published in
`docs/measurements/P7-attrition.md` with its denominator. A detector whose recall is unmeasured is exactly
the instrument this project refuses to ship.

**G1's closed rejection reasons.**

| Reason | Condition |
|---|---|
| `g1.key_not_in_schema` | a declared key absent from `TemplateSchema.fields` |
| `g1.key_unresolved` | a declared key whose `resolution_state == UNRESOLVED`. **It blocks; it never degrades to a guess** |
| `g1.host_fn_unregistered` | a host-function reference outside the closed registry (admission rule R2) |
| `g1.raised` | evaluation of `applicable` or `expr` raised |
| `g1.budget_exhausted` | the step-count budget or the wall-clock kill fired during the admission run |
| `g1.cells_bound_zero` | `cells_bound == 0` — **the condition whose absence produces the vacuous pass** |

**Validation — G0.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_g0_scope.py::test_g0__verbatim_quote_required` | `find` must succeed deterministically; the `U+002D → U+2011` homoglyph variant is rejected |
| unit | `…::test_g0__ambiguous_quote_rejected` | A quote occurring twice with a span selecting neither ⇒ `g0.quote_ambiguous`. **Admission-side twin:** the same quote with a span selecting one occurrence passes |
| unit | `…::test_g0__proviso_arithmetic_must_sum` | `provisos_total != implemented + declared` ⇒ reject |
| unit | `tests/unit/test_provisos.py::test_provisos__each_marker_fires_once` | Table-driven over the 15 markers; each matches its exemplar and nothing else |
| golden | `tests/golden/test_g0_marker_recall.py::test_golden__marker_recall_on_50_labelled_spans` | Recall against the hand-labelled set is **published**, not thresholded — the number is the deliverable. R-GOLD-2 value assertion: the reg 51(1) delegation span is detected and its `kind == "delegation"` |
| property | `tests/property/test_prop_g0.py::test_prop__span_slice_equals_quote` | Property: for every candidate that passes G0, `text[span] == quote`. Generator: the harvested set plus mutated spans |

**Validation — G1.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_g1_binds.py::test_g1__zero_bind_rejected` | `fixtures/predicates/broken/P-NC01__zero-bind.yaml` ⇒ `g1.cells_bound_zero`, and it never reaches a run |
| unit | `…::test_g1__unresolved_key_blocks` | `P-NC21a__unresolved-key.yaml` ⇒ `g1.key_unresolved`, not a resolution attempt |
| unit | `…::test_g1__unregistered_host_fn_rejected` | Admission rule R2 |
| unit | `…::test_g1__raise_is_a_gate_failure_not_an_item_state` | A raising candidate produces `g1.raised` at admission — **distinct from the run-time `ERROR(error.predicate_raised)`**, because a candidate that raises is never admitted and a run-time raise is an apparatus failure |
| golden | `tests/golden/test_g1_binds_fme.py::test_golden__all_280_bind_nonzero` | All 280 harvested FME predicates bind `> 0` cells against the `TEMPLATE-COMPUTED` reference filing. R-GOLD-2 value assertion: `P-0041`'s `cells_bound` equals its pinned integer, not merely `> 0` |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q11** (existing) | **G0 lets a proviso through.** Frontier models ground clause spans well (SpanFaith 0.77–0.79) and wire exception structure badly (Edge-F1 0.215–0.246 over 2,290 provisions), and **the empirical gates cannot see a dropped proviso** | `P-NC11a__undeclared-proviso.yaml`, `P-NC11b__quote-not-verbatim.yaml` | `test_nc__Q11a_undeclared_proviso_rejected`; `test_nc__Q11b_verbatim_quote_required`; `test_nc__Q11c_declared_proviso_emits_a_record` — the admission-side twin: a declared proviso caps the predicate at `ADVISORY`, stamps `scopeIncomplete[]`, and emits one `NO_PREDICATE(no_predicate.not_yet_synthesised)` into `scopeCaveats[]` with the verbatim text and span |
| **NC-Q01** (existing) | A predicate binds zero cells and returns a vacuous pass | `P-NC01__zero-bind.yaml` | `test_nc__Q01c_G1_rejects_at_admission` is the P7-side tooth |
| **NC-Q35** (new) | **The proviso detector is disabled or its marker list is emptied**, so G0 reports `provisos_total == 0` for every candidate and passes everything. *This is scope truncation applied to the gate that exists to catch scope truncation* | `injectors/proviso_markers_empty.py` | `tests/negative/test_nc_predicate.py::test_nc__Q35_empty_marker_list_is_detected` — assert that a G0 run reporting `provisos_total == 0` across **all candidates whose `obligation.source == STATUTE`** raises `SuspiciousUniformityError` rather than passing, because the FME instrument is measurably full of provisos. **The scoping is asserted, not assumed:** `test_nc__Q35c_uniformity_guard_is_scoped_to_statute` fails the build if the guard reads the whole candidate set, because under F9's ruling all 280 harvested candidates are `source: TEMPLATE` with a legitimate `provisos_total == 0` and an unscoped guard would fire on a correct build — and would then be "fixed" by deleting it. **Admission-side twin:** `test_nc__Q35b_a_proviso_free_clause_is_allowed` — a single hand-picked statutory clause with genuinely no proviso passes with `provisos_total == 0` and no error |
| **NC-Q39** (new) | **G1 admits a predicate whose declared key is `UNRESOLVED`**, so a version bump silently rebinds it to a different row of the same table | `injectors/g1_ignores_unresolved.py` | `test_nc__Q39_unresolved_key_blocks_admission` — pair with `test_nc__D04a_row_insertion_does_not_rebind` so the same defect is caught at induction and at admission |

**Effort.** 4 engineer-days (G0 with its detector and the labelled sample: 2.5; G1: 1.5).

---

#### P7-B3 — G2 the kill gate, G3 both arms, and the three free baselines

**Files created.**

```
src/cdfc/qualify/g2_kill.py
src/cdfc/qualify/g3_degeneracy.py          proof_arm() and empirical_arm()
src/cdfc/qualify/cel_smt.py                the CEL→SMT-LIB translator, admitted subset only
src/cdfc/qualify/domain.py                 CellDomain and the versioned domain policy
src/cdfc/qualify/random_flagger.py         hypergeometric adjusted precision
src/cdfc/qualify/baselines/__init__.py
src/cdfc/qualify/baselines/b0_template.py  the template's own 138 checkable relations
src/cdfc/qualify/baselines/b1_daikon.py    Daikon at --conf_limit 0.99; its trivia IS the degeneracy list
src/cdfc/qualify/baselines/b2_degenerate.py  "no cell is blank and no cell errors"
domain-policy-v1.json                      versioned, hashed into qualified_against
ci/no-wallclock-z3.sh                      §0.8(d)
fixtures/predicates/broken/P-NC07a__trivially-true.yaml   (existing)
fixtures/predicates/broken/P-NC07b__always-flag.yaml      (existing)
```

**Public interface.**

```python
# src/cdfc/qualify/g2_kill.py
class KillBar(StrEnum):
    EXPERIMENT = "experiment"     # K/O > 0 AND marginal kill > B0 ∪ B1 ∪ B2
    REGISTRY   = "registry"       # K/O >= 0.80 over cand.claims_fault_classes — the DECLARED set,
                                  # read from the envelope, never from the witnesses G2 selects

class UnexercisedClaimError(RuntimeError): ...
class ClaimPostdatesCampaignError(RuntimeError): ...

def check(cand, campaign: Campaign, baselines: BaselineResult, *, bar: KillBar) -> GateOutcome:
    """F1. Under bar=REGISTRY the ratio is computed ONLY over cand.claims_fault_classes:

        claimed = cand.claims_fault_classes                    # non-empty, inside code_sha256
        for c in claimed:
            if campaign.by_fault_class[c].O == 0:
                raise UnexercisedClaimError(cand.id, c)        # an unexercised claim is not a claim
        K = sum(campaign.by_fault_class[c].K for c in claimed)
        O = sum(campaign.by_fault_class[c].O for c in claimed)

    and BOTH ratios are stored in qualification.g2: `kr_claimed = K/O` over the declared set and
    `kr_all_classes` over all fourteen. The gap between them is the number a reviewer wants, and
    the predicate library renders them side by side.

    check() ALSO refuses a claim that post-dates its evidence: the commit introducing
    cand.claims_fault_classes must be a git-ancestor of the campaign id's commit, exactly as
    test_corpus__brief_predates_first_workbook requires of the fill brief. Otherwise
    ClaimPostdatesCampaignError."""

# src/cdfc/qualify/g3_degeneracy.py
class DegeneracyVerdict(StrEnum):
    NON_DEGENERATE = "non_degenerate"
    TRIVIALLY_TRUE = "trivially_true"
    ALWAYS_FLAG    = "always_flag"
    REDUNDANT      = "redundant"
    UNKNOWN        = "unknown"            # UNPROVEN. Never "non_degenerate".

def proof_arm(cand, schema: TemplateSchema, admitted: Sequence[AdmittedPredicate],
              domain: DomainPolicy) -> GateOutcome: ...
def empirical_arm(cand, corpus: CleanCorpus, campaign: Campaign,
                  sites: SiteSet, degeneracy_list: DegeneracyList) -> GateOutcome: ...

# src/cdfc/qualify/random_flagger.py
def adjusted_precision(flagged: int, true_defective: int, n: int) -> Decimal:
    """(observed_precision - d/n) / (1 - d/n). A random flagger scores 0.
    Decimal with the pinned context; no float."""
```

**Two thresholds for one gate, and they are different tests.** Both are computed, both are stored, and a
document quoting one attrition figure has quoted the wrong one.

| Bar | Threshold | Question |
|---|---|---|
| `KillBar.EXPERIMENT` | `K/O > 0` **and** marginal kill strictly greater than **each of** `B0`, `B1`, `B2` **and** their union, per `plan/00-decomposition.md` §6's arithmetic form of `beats_baselines` | *Can a candidate fire at all, and does it beat the free baselines?* |
| `KillBar.REGISTRY` | `K/O ≥ 0.80` computed **over `cand.claims_fault_classes`, the set declared in the envelope before the campaign ran**, with `UnexercisedClaimError` if any claimed class has `O == 0` | *Is this check good enough to apply to a regulated filing?* |

**F1 — the registry bar's denominator, and why this is a changed contract rather than a clarification.**

> Every document repeated the sentence *"on the fault classes the predicate **claims** to cover"*, and
> **no field held the claim.** The only place a fault class appeared was `FaultWitness.fault_class`, and
> the witness set is selected by this function, at admission, **from the mutants that already killed.** A
> predicate that kills F01 and F03 on its own read set and is structurally blind to F10 (legal enum
> substitution), F12 (homoglyph), F13 (carry desync, pair form) and F14 (vocabulary-gap) has `K/O = 0.21`
> over the campaign; the witnesses are all F01/F03; the bar is evaluated over `{F01, F03}`; the record
> reads `0.97`; the library prints `0.97`; the attestation signs it. **This is NC-Q06's mechanism — the
> numerator choosing its denominator — arriving at the gate that exists to catch it, and neither NC-Q05
> (the arithmetic) nor NC-Q06 (the site universe) can see it, because the defect is in the campaign's
> class partition.**

**Three properties make the claim evidence rather than a label, and each is asserted:**

1. **It is content-addressed.** `claims_fault_classes` is inside `envelope_projection()` (§0.8(f)), so
   narrowing the claim after seeing the campaign produces a **different `code_sha256` — a different
   predicate**, not a better score. A registry that already admitted the old id keeps the old row; the
   append-only store makes the narrowing visible as a supersession with a reason.
2. **It precedes its evidence.** The claim's commit must be a git-ancestor of the campaign's. This is the
   same instrument, in the same shape, as the fill brief's commit-order test — the plan already trusts it
   for the corpus and simply had not applied it here.
3. **It must be exercised.** A claimed class with `O == 0` on this campaign raises. Claiming F11 while the
   observability filter reports `O == 0` for F11 is exactly the F19 failure, and after that repair it is
   the *symptom* by which F19 would be caught again if it regressed.

**And both ratios are published.** `qualification.g2` stores `kr_claimed`, `kr_all_classes`, the claimed
set, and the per-class vector. **A document quoting `kr_claimed` without `kr_all_classes` beside it has
quoted half of a measurement**; the predicate library renders both columns, and `ci/no-bare-rate.sh`'s
sibling assertion (`test_g2__both_ratios_render_together`) fails a surface that carries one alone.

**G3's proof arm — the SMT translation, and why it is tractable.**

`cel_smt.py` translates the admitted CEL subset to SMT-LIB over linear integer arithmetic. The construct
that looks hard is the comprehension, and it is not: **the row count of every table is a property of the
pinned blank template**, so `filing.t.rows.all(r, φ(r))` compiles to a finite unrolling
`⋀_{i<N} φ(r_i)` — a conjunction, not a quantifier. That is why Z3 decides these problems.

For degeneracy specifically there is a sound shortcut worth naming because it changes the runtime by
orders of magnitude: **trivially-true is decidable on the single-row abstraction.** If `¬φ(r)` is UNSAT for
a *symbolic* row `r`, it is UNSAT for every unrolling. The shortcut is sound for `trivially_true` and
`always_flag`; it is **not** sound for `redundant`, because subsumption can couple rows across predicates.
`tests/unit/test_cel_smt.py::test_smt__single_row_abstraction_is_sound_for_triviality` asserts the
shortcut and the full unrolling agree on 280 candidates, and
`test_smt__abstraction_is_not_used_for_subsumption` asserts the code path.

- **trivially true** iff `¬P ∧ domain` is UNSAT ⇒ reject
- **always flag** iff `P ∧ domain` is UNSAT ⇒ reject
- **redundant** iff `P₁ ∧ ¬P₂ ∧ domain` is UNSAT ⇒ `P₂` is implied; the ILP removes it and **records the
  removal**
- **host functions are uninterpreted** ⇒ typically `unknown`
- **`unknown` is *unproven*, never *non-degenerate*.** The empirical arm must then decide.
- **`rlimit`, never a wall clock** (§0.6).

**`domain-policy-v1.json` — DECIDED as to form, OPEN as to value, with the decision rule.** `≥ −1e17` is
not trivially true over the unconstrained integers: Z3 finds a counterexample at `−1e18` and the naive
proof arm admits the predicate. **The ALR bounds are degenerate only relative to the range of values a
money cell in a regulatory filing can carry.** So the proof arm asks `¬(P ∧ domain)` where `domain` is a
declared, versioned, per-dtype bound.

> **The value has no argued basis anywhere in the corpus and this document does not invent one.**
> `domain-policy-v1.json` renders the literal string `PLACEHOLDER` for `implausible_magnitude` until an
> argument exists, exactly as `pervasiveness-policy-v1.json` does for `K` and `T`. **Decision rule:** while
> the policy is `PLACEHOLDER`, `proof_arm` returns `UNKNOWN` for every pure-bound predicate and routes it
> to the empirical arm. **The ALR rejection does not need the policy** — see the next paragraph — so the
> open item blocks nothing. The exact question, for whoever settles it: *what is the largest value a
> `MILLI_USD_MILLION` cell in an IFSCA prescribed return can lawfully carry, on what argument, and does
> the argument survive a sovereign wealth fund?*

**How the ALR rejection is actually demonstrated, and it is a measurement rather than a policy.** The five
`≥ −1e17` bounds are refused on two independent, fully measurable grounds:

1. **G2.** Seed F01 (sign flip), F02 (scale), F03 (off-by-one), F04 (transposition) and F05 (zero-out) into
   the 1,428 cells the five bounds cover. **No mutation of a financial figure reaches `−1e17`**, so
   `K = 0` over every observable mutant: `K/O = 0`, which fails the registry bar (`≥ 0.80`) *and* the
   experiment bar (`> 0`). **Under F1's repair the five bounds must each declare
   `claims_fault_classes` — a `numeric_bound` harvested from `formula1` claims `("F01","F02","F03","F04","F05")`,
   the classes a bound can in principle catch — and all five classes have `O > 0` on this campaign, so
   `UnexercisedClaimError` does not fire and the rejection is computed over the declared set rather than
   over the empty witness set. A predicate that declared *no* class would not reach G2 at all: the field is
   required and non-empty at load.**
2. **G3 empirical.** Marginal kill over `B2` — the degenerate arm, *"no cell is blank and no cell errors"* —
   is **0**. `degenerate_floor` margin is not positive, so the predicate is not distinguishable from the
   flag-nothing baseline.

The admission-side twin is on the same disk: **FME's 19 real `≥ 0` bounds**. F01 on a positive money cell
yields a negative value, the bound fires, the mutant dies, `K/O > 0`. **Without that twin the gate is
indistinguishable from reject-everything, which would score perfectly on the negative control alone.**

**G3's empirical arm — four tests, and the third is the one nothing else does.**

| Test | Threshold | Note |
|---|---|---|
| Clean-corpus firing | flags `≤ 50%` of the clean corpus | **REJECT-ONLY against `TEMPLATE-COMPUTED` at P7 — see the C5 note below. Admission on this criterion waits for `BLIND-FILLED` at P8.** |
| Degeneracy-list membership | not equivalent to a published degeneracy-list member | The list **is** B1's Daikon trivia output at `--conf_limit 0.99` |
| **Control-arm spurious fires** | **exactly `0`** | See below |
| Random-flagger adjusted precision | `> 0` | The hypergeometric baseline; a random flagger scores exactly 0 |

**Why the control-arm threshold is exactly zero, and why that is derived rather than chosen.** The control
sites lie outside `upstream_closure(read_set(p))` (§0.4). A mutation there cannot change any input the
predicate reads after recalculation. So a fire on a control mutant means one of exactly two things: the
predicate reads a key it did not declare — impossible, because P4's both-ways AST check rejects that at
admission — or the fact table is leaking between cells. **Both are apparatus failures, not predicate-quality
findings.** Therefore a non-zero control-arm count raises `ApparatusError` and **blocks the whole admission
batch**, and the number is not softened into a tolerance. *A threshold that is derivable from the
architecture beats a threshold that is negotiated.*

**The random-flagger exhibit, pinned as a regression test.** CLAUSE's best F1 over an 80-cell table is
**65.4** on a ~49.5%-positive split where a constant always-flag classifier scores **66.2**.
`tests/unit/test_random_flagger.py::test_random_flagger__clause_exhibit` reproduces both numbers from the
module and asserts `adjusted_precision(...) <= 0` for the constant classifier. **A degeneracy module that
cannot reproduce the published exhibit of the failure it exists to catch is not a degeneracy module.**

**The three baselines, built here and run under pre-registration at P12-B2** (§0.2).

| Baseline | What it is | Interface |
|---|---|---|
| **B0** | the template's own **138** checkable relations of 505 evaluated cells (35 SUM identities + 3 COUNTIF tallies = 38 of 294 authored expressions) | `b0_template.relations(schema) -> tuple[Relation, ...]` |
| **B1** | **Daikon** over the clean corpus at `--conf_limit 0.99`. **Its trivia output doubles as the degeneracy list** | `b1_daikon.invariants(corpus) -> DegeneracyList` |
| **B2** | the degenerate arm: *"no cell is blank and no cell errors"* — the analogue of the `NoException` baseline that found **68.9%** of a published neural oracle's bugs at **twice** its precision | `b2_degenerate.predicate() -> PredicateEnvelope` |

`BaselineResult` carries each baseline's own `Campaign` over the same `SiteSet`, so *marginal kill* is a
difference of two integers over the same denominator and not a comparison of two studies. **The marginal
kill is reported against each baseline separately, never against the union alone** — a union figure hides
which baseline did the work.

**Licence note, because the gate scans it.** Daikon's licence is **not opened**; it enters
`docs/LICENCES.md` as a **dev-time / offline-analysis** dependency with `warrant: SECONDARY` and
`opened_by` blank, and §5.2's Phase-2 blocking rule applies to *runtime* dependencies. It must be opened
before the code ships, like every other SECONDARY row. **If Daikon's licence turns out to be
distribution-hostile, B1 degrades to "no published degeneracy list" and the empirical arm loses one of its
four tests — the arm survives, the evidence weakens, and the predicate library says which predicates were
checked against a degeneracy list and which were not.**

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_g3_degeneracy.py::test_g3__trivially_true_rejected` | `expr: "true"` ⇒ `¬P` UNSAT ⇒ `TRIVIALLY_TRUE` (NC-Q07a) |
| unit | `…::test_g3__always_flag_rejected` | `expr: "false"` ⇒ `P` UNSAT ⇒ `ALWAYS_FLAG` (NC-Q07b) |
| unit | `…::test_g3__unknown_is_unproven` | A candidate calling `nav_interval(...)` (uninterpreted) ⇒ `UNKNOWN`; the predicate does **not** clear the proof arm (NC-Q07c) |
| unit | `…::test_g3__subsumption_removal_is_recorded` | `P₁ ∧ ¬P₂` UNSAT ⇒ `P₂` removed **and the removal appears in the registry's decision log** (NC-Q07d) |
| unit | `tests/unit/test_g2_kill.py::test_g2__two_bars_are_two_numbers` | The same campaign yields `EXPERIMENT: pass`, `REGISTRY: fail` at `K/O = 0.05`, and both are stored |
| **unit** | **`…::test_g2_denominator_is_declared_before_the_campaign`** | **F1, and it is test 1 of the adversary's ten.** (a) `claims_fault_classes` is non-empty and appears in `envelope_projection()`; (b) the commit introducing it is a git-ancestor of the campaign id's commit, else `ClaimPostdatesCampaignError`; (c) a claimed class with `O == 0` raises `UnexercisedClaimError`; (d) narrowing the claim yields a **different** `code_sha256` |
| **unit** | **`…::test_g2__registry_bar_ignores_the_witness_set`** | Construct a campaign where `kr_claimed = 0.21` and the killing witnesses are all F01/F03; assert the stored `kr_claimed` is `0.21`, **not** `0.97`, and that `g2_kill` never reads `FaultWitness.fault_class` to build a denominator — asserted on the call graph |
| **unit** | **`…::test_g2__both_ratios_render_together`** | Every render path emitting `kr_claimed` emits `kr_all_classes` in the same string |
| **campaign** | **`tests/campaign/test_g2_admits_template_diff.py::test_g2_admits_template_diff`** | **F19's companion.** `TEMPLATE_DIFF` — predicate #1 — reaches G2 with `by_fault_class["F11"].O > 0` and a **computed** `K/O`, rather than a `CampaignArithmeticError`. Without this the plan's headline relation is unadmittable and nobody finds out until P9-B4 |
| **golden** | **`tests/golden/test_vacuous_bound_rejection.py::test_golden__alr_five_bounds_rejected`** | **The worked example.** On `ALR_V2_3` (`a414d8d3…`): exactly **5 of 6** bound predicates rejected; each produces a `rejection` row with `rejecting_gate ∈ {G2, G3e}`, the measured `K/O = 0/O`, and `cells_would_have_covered` summing to **1,428**. R-GOLD-2 value assertions: the five `sqref` strings and the per-sheet cell counts `783 / 531 / 99 / 9 / 6` |
| **golden** | **`tests/golden/test_real_bound_admission.py::test_golden__fme_nineteen_real_bounds_admitted`** | **The admission-side twin.** On FME: **19 of 24** bounds have `formula1 == "0"` and clear G2 with `K/O > 0`. Without this the gate is a reject-everything baseline |
| **golden** | **`tests/golden/test_fme_nonzero_bounds_disposed.py`** (new) | The five FME bounds whose `formula1` is not `0` — `2. Summary!U5:U14`, `3. Portfolio!J17:N26`, `3. Portfolio!E27:F27`, `5. PMS!D10:E11`, `5. PMS!C10:C11`, **68 cells** — each has a recorded disposition and a measured `K/O`. **The test asserts a disposition exists, not what it is**, because the disposition is this phase's finding |
| golden | `tests/golden/test_alr_settled_falls.py::test_golden__settled_fraction_falls_on_rejection` | ALR's settled fraction recomputes **downward** after the five rejections, and the `docs/HARVEST-DELTA.md` entry exists with a non-empty reason and a date (NC-Q03c) |
| property | `tests/property/test_prop_g3.py::test_prop__unknown_never_becomes_non_degenerate` | Property: for every candidate, `proof_arm(...).measured["verdict"] == UNKNOWN ⇒ passed is False`. Generator: candidates with 0–4 uninterpreted host-function calls |
| determinism | `tests/determinism/test_det__z3_unknown_is_reproducible` | Same candidate, two runs under different TZ/hash seed/locale/cwd and on the second CI runner image ⇒ identical verdict. This is why `rlimit` and not `timeout` |
| campaign | `tests/campaign/test_g2_marginal_kill_over_baselines.py` | Marginal kill is reported against B0, B1 and B2 **separately**, over the same `SiteSet` |
| perf | `tests/perf/test_perf__PERF_G3P` | Proof arm over 280 candidates; baseline recorded at P7, ±20% thereafter |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q03** (existing) | **A degenerate predicate is admitted. REAL, ON DISK: `ALR_V2_3`'s five `≥ −1e17` bounds over 1,428 cells** | `injectors/g3_disabled.py` — G3 returns `non_degenerate` unconditionally | `test_nc__Q03a_alr_vacuous_bounds_rejected` · `test_nc__Q03b_fme_real_bounds_admitted` · `test_nc__Q03c_settled_fraction_falls_on_rejection`. **This is demonstration D-REJECT and D-DEGENERATE (§4.1, §4.2)** |
| **NC-Q07** (existing) | A degenerate or always-flagging predicate passes the proof arm because `unknown` is read as `non_degenerate` | `injectors/z3_unknown_is_ok.py` | `test_nc__Q07a` … `test_nc__Q07d` above |
| **NC-Q06c** (existing) | A flag-everything predicate (`expr: "false"`) scores perfectly on the kill rate | `fixtures/predicates/broken/P-NC07b__always-flag.yaml` | `test_nc__Q06c_flag_everything_fails_the_control_arm` — it must be rejected by the control arm's spurious-fire count, **and** by the proof arm (`P` UNSAT), **and** by the random-flagger adjusted precision (`≤ 0`). Three independent teeth, because SPADE's own paper records that selecting **all** generated candidates yields 100% coverage at 100% FFR |
| **NC-Q57** (new, **F1**) | **`claims_fault_classes` is derived from the kill vector** — the loader or the gate fills the field from the classes that killed, so the claim is a transcript of the result and `K/O` over it is `1.00` by construction. This is the plan's own founding defect (a denominator built out of the numerator) committed at the gate built to catch it | `injectors/claims_from_kill_vector.py` — populates `claims_fault_classes` post-campaign from `killed_by_class.keys()` | `tests/negative/test_nc_predicate.py::test_nc__Q57_claims_precede_the_campaign` — assert un-injected that the claim's commit is a git-ancestor of the campaign's and that a claimed-but-unexercised class raises `UnexercisedClaimError`; assert injected that `kr_claimed == 1.00` while `kr_all_classes` is unchanged, and that the build **fails** on the ancestry check. **Admission-side twin:** `test_nc__Q57b_an_honest_claim_is_admitted` — a predicate declaring `("F01","F03")` before the campaign, with `O > 0` on both, is admitted with `kr_claimed` computed over exactly those two |
| **NC-Q36** (new) | **The ILP drops a predicate without recording the removal**, so a subsumed predicate vanishes from the registry and the settled fraction moves with no cause on the chart | `injectors/ilp_silent_removal.py` | `tests/negative/test_nc_predicate.py::test_nc__Q36_removal_is_recorded` — assert every ILP-removed candidate has a `rejection` row with `rejecting_gate = G3p`, the subsuming predicate id in `measured`, and `cells_would_have_covered` populated. **Admission-side twin:** a non-subsumed predicate is retained and no rejection row is written |
| **NC-N51** (new, `injector: NONE`) | *That `domain-policy-v1.json`'s magnitude bound is right.* `why_impossible`: the bound is a claim about lawful values in a population of filings that is not public. **What it costs:** while the policy is `PLACEHOLDER`, every pure-bound predicate reaches G3's proof arm as `UNKNOWN` and is decided empirically — which is slower, needs a corpus, and is *the reason the ALR rejection is demonstrated at G2 and G3ᵉ rather than by proof* |

**Effort.** 5 engineer-days. The risk sits in `cel_smt.py`; the single-row abstraction is what keeps it
inside the estimate. **Switch trigger, stated in advance:** if the translation breaks on a construct class
the admitted subset permits, **narrow the admitted subset rather than widening the translator**, record the
narrowing in `docs/measurements/P4-cel-conformance.md`, and re-run P4's both-ways AST check. If it breaks
irrecoverably, **Z3 is dropped, the empirical arm runs alone, and the library loses the counterexample
witness** — the gate survives, the evidence weakens, and the predicate library says which predicates carry
a proof and which do not.

---

#### P7-B4 — The pipeline, the registry, the ILP, and admission

**Files created.**

```
src/cdfc/qualify/pipeline.py           the five gates in GATE_ORDER, free before cheap before expensive
src/cdfc/qualify/ilp.py                SPADE's ILP REIMPLEMENTED, ~40 lines of PuLP/CBC
src/cdfc/predicates/registry.py        append-only store + Merkle root + admit/load
src/cdfc/cli.py                        `cdfc qualify`, `cdfc admit` subcommands
docs/measurements/P7-attrition.md      the funnel
```

**Public interface.**

```python
# src/cdfc/qualify/pipeline.py
def qualify(cand: PredicateEnvelope, ctx: QualificationContext,
            *, through: GateId = GateId.G4) -> Admission | Rejection:
    """Runs GATE_ORDER in order and STOPS AT THE FIRST FAILURE.
    The stop is the cost control and the evidence: a rejection carries exactly one gate."""

# src/cdfc/predicates/registry.py
class UnqualifiedPredicateError(RuntimeError): ...

def admit(cand: PredicateEnvelope, q: QualificationRecord, *,
          signer: str, signature: bytes, batch_manifest_sha256: str) -> AdmittedPredicate:
    """R5 append-only: supersession is a new row, never an update.
    R7: raises UnsignedAdmissionError without a valid detached signature over the batch manifest."""

def load(predicate_id: str, version: int) -> AdmittedPredicate:
    """Raises UnqualifiedPredicateError if no qualification row exists.
    THIS IS BARRIER 3 AND IT IS A RUNTIME INVARIANT, NOT A LINT."""

def reject(cand, outcome: GateOutcome, *, obligation_id: str,
           cells_would_have_covered: int) -> RejectionRow: ...

def registry_root(as_of: datetime | None = None) -> str:
    """Merkle over sorted code_sha256.
    leaf     = sha256(b'\\x00' + h)
    internal = sha256(b'\\x01' + left + right)
    odd node promoted. DOMAIN SEPARATION IS NOT DECORATION."""
```

**The ILP at P7 runs with the subsumption constraint only.** The set-FFR constraint
`max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)` requires an FFR, which arrives at P8. State this in the
build rather than discovering it: `ilp.select(candidates, constraints=[SUBSUMPTION])` at P7,
`constraints=[SUBSUMPTION, SET_FFR]` at P8-B3. `tests/unit/test_ilp.py::test_ilp__ffr_constraint_absent_at_p7`
asserts the P7 configuration and its reason string, so the omission is a declared state rather than a gap.

**Reuse the algorithm, not the repository.** The SPADE repository is 17★, 1 fork, **no licence field**,
last push 2024-04-07. `ilp.py` is ~40 lines of PuLP/CBC; measured runtimes in the source paper are
0.104–1.197 s on thousands of variables, so the reimplementation is not a performance risk.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_registry.py::test_registry__merkle_domain_separation` | Leaf and internal prefixes differ; a two-leaf tree's root differs from `sha256(l ‖ r)` |
| unit | `…::test_registry__odd_node_promoted` | A 5-leaf tree's root matches the pinned value |
| unit | `…::test_registry__append_only` | Supersession writes a new row; the old row is byte-unchanged |
| unit | `…::test_admission_requires_a_signature` | `admit` without a valid detached signature raises `UnsignedAdmissionError` (R7) |
| property | `tests/property/test_prop_registry.py::test_prop__root_is_order_invariant` | Property: shuffling the input candidate order does not change `registry_root` (the sort is explicit). Generator: random permutations of 1–300 `code_sha256` values |
| golden | `tests/golden/test_registry_root.py::test_golden__fme_registry_root` | The root over the admitted FME set equals its pinned value. R-GOLD-2 value assertion: the sorted leaf list's first and last `code_sha256` are pinned, not only the root |
| determinism | `tests/determinism/test_det__registry_root_reproduces` | Byte-identical root across TZ/hash seed/locale/cwd/machine |
| contract | `tests/contract/test_contract__qualification_row_required` | A `predicate` row without a `qualification` row fails at load, not at use |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q02** (existing) | **A predicate with no qualification record loads**, and the settled-fraction claim silently becomes an assertion | `fixtures/predicates/broken/P-NC02__no-qualification.yaml` | `test_nc__Q02_unqualified_predicate_does_not_load` — attempt admission; assert it **raises**; assert the predicate is absent from the computed root; assert the root is **unchanged**. This is barrier 3 and spec §III.3.6 R7 requires exactly this test |
| **NC-Q38** (new) | **The registry root is computed without domain separation** — leaf and internal prefixes dropped — so a second-preimage construction lets two different admitted sets share a root, and the attestation's `registryRoot` stops identifying what ran | `injectors/merkle_no_domain_sep.py` | `tests/negative/test_nc_predicate.py::test_nc__Q38_domain_separation_is_load_bearing` — construct the classic two-leaf/one-internal collision; assert un-injected the roots differ and injected they are equal |
| **NC-Q55** (new) | **An admission batch is written without a human signature.** R7 exists because the gate is mechanical and shipping a check that will be applied to a regulated filing is not | `injectors/admit_autosign.py` | `tests/negative/test_nc_predicate.py::test_nc__Q55_admission_requires_a_human` — assert `UnsignedAdmissionError`, and assert the batch manifest's `signer` is not a constant or an environment default. **Admission-side twin:** a correctly signed batch admits and the signer appears in `qualified_against` |

**Effort.** 3 engineer-days.

---

### The measurement P7 produces

| Field | Value |
|---|---|
| **Metric** | **The five-gate attrition funnel over the 280 harvested FME predicates** — `generated → G0 → G1 → G3ᵖ → G2 → G3ᵉ` survivors, each stage with its integer count and the named reason for every rejection. **Stage one renders three integers, `entered / skipped / survived`, and `skipped` is never counted as a survivor** (F9) |
| **Denominator** | 280 harvested FME predicates (and, published beside it, 19 for ALR) |
| **Warrant** | **MEASURED** |
| **Produced by** | `src/cdfc/qualify/pipeline.py` |
| **Command** | `cdfc qualify --template 7d9a1960 --through G3e --campaign <id> --out docs/measurements/P7-attrition.md` |
| **What did not exist before** | Today **one** rejection exists, on a different workbook, in one predicate class. After P7 there is a funnel |

**Six** subordinate numbers ship with it and none is optional:

1. **`g0_marker_recall`** — the proviso detector's recall on 50 hand-labelled spans, with its denominator
   and the labeller's name and date. *A detector whose recall is unmeasured is the instrument this project
   refuses to ship.*
2. **The disposition of the five non-`0` FME bounds** (68 cells), each with its measured `K/O`. Nobody has
   looked at these; the spec's "19 of 24" leaves them unclassified.
3. **The per-baseline marginal kill** for every candidate that reaches G2, against B0, B1 and B2
   **separately**.
4. **THE OBLIGATION COVERAGE PAIR (F9, arbitration C2) — two numbers, always both:**
   **`predicates_with_a_STATUTE_obligation / 280` = `0 / 280` today**, and
   **`predicates_with_a_TEMPLATE_obligation / 280` = `280 / 280` today.**
   Every harvested candidate's obligation carries `source: TEMPLATE`: a real provenance chain to the
   regulator's own pinned artifact, and **not** a statutory grounding. The two counts are never added
   together, never rendered singly, and never abbreviated to one of them, on any surface
   (`test_p7__both_obligation_counts_render_or_neither_does`). **The sentence that must survive verbatim
   beside them: *no harvested predicate yet implements a statutory clause.*** *One number alone was the
   defect: `0/280` alone is wrong by 280 under this ruling's mechanism, and `280/280` alone conceals that
   nothing here is grounded in the statute.*
5. **`kr_claimed` and `kr_all_classes` for every candidate that reaches G2, side by side** (F1), with the
   declared class set printed. **The gap between the two columns is the number a reviewer wants**, and a
   large gap on an admitted predicate is a finding of this phase, not an embarrassment to be smoothed.
6. **`I` and `I/G` from P6's campaign, carried onto the attrition page** (F18), so that a funnel computed
   over a denominator our own evaluator could not fully adjudicate says so where the funnel is read.

### Exit gate

```
P7 EXITS iff ALL of:
  0. EVERY candidate has exactly one G0 disposition from the closed reason set, stage one renders
     `entered / skipped / survived` as three integers with entered == skipped + rejected + survived,
     and BOTH obligation-coverage numbers are published TOGETHER (F9, C2):
         predicates_with_a_STATUTE_obligation  / 280   -- 0   / 280 today
         predicates_with_a_TEMPLATE_obligation / 280   -- 280 / 280 today
     Publishing either one alone FAILS this gate (test_p7__both_obligation_counts_render_or_neither_does).
     G0 runs FOR REAL against every source=TEMPLATE obligation -- it asks whether the predicate
     faithfully implements the relation it claims to implement -- and a G0 that cannot fail over the
     harvested population fails this gate. A funnel whose first row is `280 -> 280` fails this gate.
  0b. G2's registry bar is computed over `claims_fault_classes` for every candidate that reaches it;
     `kr_claimed` AND `kr_all_classes` are both stored and both rendered; the claim's commit is a
     git-ancestor of the campaign's for every admitted predicate; no admitted predicate claims a
     class with O == 0 (F1).
  1. docs/measurements/P7-attrition.md is published with every rejection's gate and measured number,
     and every rejection has a `rejection` row carrying cells_would_have_covered.
  2. FME's 19 real `>= 0` bounds are ADMITTED (K/O > 0) and ALR's five degenerate bounds are REFUSED
     (K/O = 0 at G2; marginal kill over B2 = 0 at G3e), with ALR's settled fraction recomputed
     DOWNWARD and a docs/HARVEST-DELTA.md entry carrying a reason and a date.
  3. Each of the five non-`0` FME bounds has a recorded disposition with a measured number.
  4. `registry_root` is reproducible across two machines; `load()` raises on a predicate with no
     qualification row; `admit()` raises without a human signature.
  5. Gate order is enforced by the pipeline's SHAPE, not by a comment: NC-Q34's spy assertion is green.
  6. Control-arm spurious fires == 0 across every candidate that reaches G3e, or the batch is blocked
     with an ApparatusError naming the predicate and the leaking cell.
  7. `make nc-sweep` reports NC-Q01, NC-Q02, NC-Q03, NC-Q06c, NC-Q07, NC-Q11, NC-Q34, NC-Q35, NC-Q36,
     NC-Q38, NC-Q39, NC-Q55, NC-Q57, NC-Q47, NC-Q48 as caught, AND reports
     `guards_flipped == guards_expected_to_flip` over those entries (F4). DoD line C4 cites the sweep
     report row — path and commit — never a pasted quotation (F31).
  8. `make mutation-pr` reports K/V >= 0.85 for qualify/ and predicates/registry.py, with the
     equivalent-mutant caveat carried in the same sentence and never as a naive percentage.
  9. `ci/no-wallclock-z3.sh` in ci/GATES.md and observed red against its planted control.
```

### What it kills if it fails

**If the gates reject nothing on the FME workbook**, that is **a publishable measurement, not a failure.**
It means the harvest is clean on this artifact, the gate's demonstrated work remains *one workbook, one
class, five predicates*, and every surface says exactly that. Note this is the *likely* outcome for a
harvest derived mechanically from the template's own constructs — the harvest cannot invent a proviso it
never read — and it is why the settling experiment (P12) is where the gate's rejection power is really
tested.

**If G3's proof arm cannot be encoded** — the CEL→SMT-LIB mapping breaking on a construct class — Z3 is
dropped, the empirical arm runs alone, and the predicate library loses the counterexample witness. The gate
survives, the evidence weakens, and the library **says which predicates carry a proof and which do not**.

**If the control-arm threshold cannot be held at zero**, the finding is an apparatus defect — an undeclared
key read, or a leak in the fact table — and it is fixed at P4 or P3, not softened here. **Softening it is
how the flag-everything predicate gets in**, and the flag-everything predicate is the thing SPADE's own
paper measured at 100% coverage and 100% FFR.

**If admission cannot be made to require a human signature** — no signer exists — the batch is admitted
with `signer: "UNSIGNED"` and **every surface renders the admitted set with the literal string
`UNSIGNED BATCH`** beside its count. Ships, visibly weaker.

### Effort

**16 engineer-days** (was 14). Same assumption as P6, plus: comfortable with SMT and with reading normative
text. Split: **B0 1.5** (the instrument text source, moved here from P12-B1 — F35) · B1 **2.5** (+0.5 for
the template-derived instrument and `ObligationSource` — F9/C2) · B2 4 · B3 5 · B4 3. **The two days are not
new work; one is work that was scheduled five phases downstream of its consumer, and half a day is work the
plan assumed was free.**

---

# P8 — THE CLEAN CORPUS, G4, FFR AND SEVERITY TIERS · 9.5 engineer-days (+ 15–25 person-days, parallel lane)

### What it settles

**Whether any predicate in this system is admissible at all** — and what the settled fraction is *after*
the gate rather than before it. **That delta is the product.**

Today the answer is: **0 predicates admitted, and a defensible settled fraction of 0%.** The headline
`2,373 / 3,747 = 63.3%` is computed from 280 predicates **of which none is admissible under this
specification's own gate**, because no false-failure rate has been measured for any of them. A reviewer who
connects those two facts wins — unless we say it first, which is what `PRE-GATE` and P14's A11 mechanise
and what this phase converts into a number.

### Entry criteria

| # | Must be true | Why |
|---|---|---|
| **E8.1** | **B1 has NO entry criteria. It starts at day 0, in its own lane, in parallel with the entire engineering track.** | **Stated plainly because `plan/00-decomposition.md` §9 makes it a cross-document obligation.** B1 needs the blank template (on disk), the regulation (public) and a person who has never seen the predicate set. **Starting it late is not a schedule error, it is an evidence error**: the firewall is easier to hold the earlier it starts, because there is less predicate set in existence to leak. **The longest pole in this plan is not the code. It is the corpus.** It becomes the critical path the moment it is deferred past day ~70 |
| E8.2 | **P7 complete** — for B3 and B4 only | G4's `marginal_ffr` and `conditioned_on[]` are computed against the already-admitted set, so a registry must exist |
| E8.3 | B2's `TEMPLATE-COMPUTED` arm is delivered **before P7-B3** (§0.3), not at P8 | G1 and G3ᵉ need a clean filing |

### Builds

---

#### P8-B1 — The blind-fill corpus and its firewall *(parallel lane, from day 0)*

**This build has no code dependency on any other phase and does not wait on P7.**

**Files and repositories created.**

```
corpus/                                   A SEPARATE GIT REPOSITORY
corpus/FILL-BRIEF.md                      hashed and published BEFORE the first workbook is filled
corpus/SLICES.md                          the held-out slice, DECLARED BEFORE the corpus exists
corpus/filled/clean__blind-filled__fme-001__<sha8>.xlsx …
corpus/MANIFEST.json                      per workbook: sha256, filler_id, elapsed_minutes,
                                          cells_written[] (F36), cells_left_blank[], blank_reasons[]
fixtures/corpus_manifest.json             the main repo's ONLY reference: {repo_url, commit_sha,
                                          manifest_sha256, brief_sha256, slices_sha256,
                                          person_a_kind, contamination_result_sha256}
tools/corpus/contamination_probe.py       ADVISORY — cannot establish blindness
tools/corpus/mask_vs_filler.py            F36: what Person A actually wrote, against the 3,747 mask
tests/test_corpus_firewall.py
```

**F16 — the contamination grep cannot run inside the firewall it tests, and the two tests as written
contradict each other.** `test_corpus_is_not_importable` asserts that nothing under `src/` or `tests/`
reads `corpus/` except through `fixtures/corpus_manifest.json`; `test_e2e__corpus_firewall` greps *the
corpus repository's tree* for predicate ids, which requires that tree to be checked out in the CI working
tree beside the predicate set. **Both cannot hold in one job**, and the way that contradiction resolves
itself under time pressure is that somebody checks the corpus out next to the predicates — which is the
contamination the firewall exists to prevent.

> **DECIDED — the contamination grep runs in the corpus repository's own CI, over its own tree, and
> publishes a signed result whose digest enters `fixtures/corpus_manifest.json`; the main repo asserts the
> digest and never sees the tree.** *Alternative it beat:* a shallow throwaway checkout in a separate CI
> job of the main repo — rejected because "separate job, same runner, same workspace root" is a procedural
> boundary, and this plan's own standard is that a boundary which leaves no artifact is not a boundary.
> The signed result carries `{corpus_commit_sha, patterns_sha256, hits: 0, positive_control_hits: 1,
> run_at, signer}`; **`positive_control_hits` must be non-zero or the grep proved nothing**, and
> `test_corpus__contamination_result_is_signed_and_current` fails when the result's `corpus_commit_sha`
> is not the manifest's `commit_sha`.

**The firewall, mechanised wherever the procedure leaves a trace.**

| # | Rule | Mechanised by |
|---|---|---|
| 1 | **Two repositories.** Nothing under `src/` or `tests/` reads `corpus/` except through `fixtures/corpus_manifest.json` | `tests/test_corpus_firewall.py::test_corpus_is_not_importable` |
| 2 | **What Person A receives**: the blank template, the regulation PDF, and the fill brief. **What Person A never receives**: `src/cdfc/predicates/`, `predicates.json`, any report, any list of checks, any member of the plan or spec | Procedural. NC-N03 |
| 3 | **The fill brief is hashed and published before the first workbook is filled** | `test_corpus__brief_hash_matches` (recorded hash equals the file) and `test_corpus__brief_predates_first_workbook` (the brief commit is an **ancestor** of the first workbook commit, read from the corpus repo's git history). **A commitment made after seeing the result is not a commitment, and here the git history is the evidence** |
| 4 | **The held-out slice is declared before the corpus exists**, in `corpus/SLICES.md`, hashed with the brief | `test_corpus__slice_declared_before_fill` — a plain firewall test, not a catalogue entry, because the break is procedural and its injector would be a rewritten git history. A slice chosen after the corpus is filled is a **subgroup analysis** and is labelled one on every surface |
| 5 | **If the fallback fires** (no human Person A ⇒ the audited second-model-instance route), the fill prompt is hashed and published **before** the first workbook; `corpus_provenance` stays `BLIND-FILLED` **only if** the instance was never shown the predicate set; the record carries `person_a_kind: "model-instance"`, **which renders wherever the FFR renders**. **The fallback is weaker than a human and the record says so** | `test_corpus__person_a_kind_renders_with_the_ffr` |
| 6 | **The contamination probe, with its weakness stated in its own output.** Compares the value-distribution entropy of cells the predicate set reads against cells it does not, across A's workbooks, with a permutation p-value. It can detect a gross correlation; it cannot detect a subtle one; **a null result is not evidence of blindness** | The probe's own output carries the literal string `ADVISORY — cannot establish blindness` |
| 7 | **The exchangeable unit is the FILING.** `n = F`, never `n = 3,755·F` | `test_nc__Q08d_n_is_filings_not_cells` |

**What the fill brief must contain, and one instruction that is not obvious.** The workbook (FME
`7d9a1960…`), the count (**≥ 30**), the declared strata so the held-out slice pre-exists, the instruction
to fill **correctly** per the regulation, the ban on consulting anyone on the build team, and a stopwatch
record per workbook. And this, which is a measurement rather than housekeeping:

> **Person A records every cell they could not fill, and why.** A cell a competent filler cannot complete
> from the template and the regulation alone is **evidence about the instrument**, not noise. Those rows
> feed `no_predicate.rule_ambiguous` and `no_predicate.no_obligation_specified`, and they are the only
> independent read anyone in this project will get on which parts of the return are underspecified.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_corpus_manifest.py::test_manifest__every_workbook_has_a_provenance_token` | Every filename matches §6.5's grammar and carries `blind-filled`; the in-file `CDFC_PROVENANCE` custom property agrees |
| contract | `tests/contract/test_contract__corpus_manifest_shape` | `fixtures/corpus_manifest.json` has all **seven** keys; a missing `brief_sha256`, `slices_sha256` or `contamination_result_sha256` fails the build |
| e2e | `tests/e2e/test_e2e__corpus_firewall` | **Runs in the CORPUS repository's CI** (F16): a grep of that tree for any predicate id (`P-\d{4}`), any CEL fragment from `predicates.json`, or any gate output string returns zero hits **with a positive control** — the grep finds a planted marker in a scratch file, and `positive_control_hits > 0` is asserted, not assumed. The signed result is published as an artifact |
| **contract** | **`tests/contract/test_corpus__contamination_result_is_signed_and_current`** | **The main repo's half of F16.** The manifest's `contamination_result_sha256` resolves to a signed result whose `corpus_commit_sha == manifest.commit_sha`, whose `hits == 0` and whose `positive_control_hits > 0`. A stale or unsigned result fails the build. **The main repo never checks the corpus tree out** — asserted by `test_corpus_is_not_importable`, which now has nothing contradicting it |
| **measurement** | **`tests/campaign/test_mask_matches_what_a_competent_filler_filled.py`** | **F36 — the only external instrument in the plan that can falsify the 3,747 denominator, and it costs one script over data the corpus lane already produces.** From `corpus/MANIFEST.json`'s per-workbook written-cell sets, publish **two integers**: cells Person A wrote that lie **outside** the mask (the mask is too small — the dangerous direction, under which every settled fraction overstates coverage) and cells inside the mask that **no filler ever wrote** (the mask is too large — the direction that understates it). Denominator 3,747, warrant MEASURED, published in `docs/measurements/P8-mask-external-check.md`. **The test asserts the two integers are computed and published, not that they are zero** — a non-zero first integer is a finding against P2's denominator and is escalated there, not absorbed here |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q08** (existing) | A `SELF-AUTHORED` FFR renders as a number | `injectors/render_self_authored_ffr.py` | `test_nc__Q08a_renders_uninformative` · `Q08b_api_returns_null` · `Q08c_no_ffr_without_provenance_and_n` · `Q08d_n_is_filings_not_cells`. **This is demonstration D-FFR-PROVENANCE (§4.3)** |
| **contamination** (existing, P8's headline control) | A corpus-lane input contains a predicate id | a planted `P-0041` string in a corpus-repo file | `test_e2e__corpus_firewall` must **fail the build**, with its positive control proving the grep works |
| **NC-N03** (existing, `injector: NONE`) | *That the blind-fill corpus is genuinely blind.* Blindness is a property of a person's history, not of an artifact | — | **What it costs:** every `BLIND-FILLED` FFR rests on a procedure, not a test. It is **the single largest unverifiable input to the product's headline claim** — and it is why `SELF-AUTHORED` renders the word `uninformative` rather than a number: we would rather print nothing than print a number whose shape is evidence and whose content is zero |

**Effort.** **15–25 person-days of a different person**, plus **1.5 engineer-days** for the firewall tests,
the manifest, the signed-contamination-result contract (F16) and `mask_vs_filler.py` (F36). **Never added
to the engineer's total.**

**And the number this build is sized against, published rather than assumed (F37).** 30 blind-filled
workbooks satisfy G-CORPUS and license `ADVISORY` (`hi(0,30) = 0.1139`). **189 are needed before a single
predicate can be `BLOCKING` at zero fires** (§0.9). At the 15–25 person-days measured for 30, **189 is
95–160 person-days — four to seven months of one person**, which dwarfs the engineering path and is the
real critical path of the *product* as opposed to the *paper*. See §5 O5 for the decision taken and the
one question that is the user's.

---

#### P8-B2 — The three corpus-free oracles

**Files created.**

```
src/cdfc/qualify/corpus/__init__.py
src/cdfc/qualify/corpus/template_computed.py    ← DELIVERED BEFORE P7-B3 (§0.3)
src/cdfc/qualify/corpus/register_derived.py
src/cdfc/qualify/corpus/cross_format.py
fixtures/clean/clean__template-computed-calc__fme-*__<sha8>.xlsx      derived_by=CALC
fixtures/clean/clean__template-computed-foreign__fme-*__<sha8>.xlsx   derived_by=FOREIGN_ENGINE (F2)
fixtures/clean/clean__template-computed-none__fme-*__<sha8>.xlsx      derived_by=NONE, substrate only
```

**The filename carries `derived_by` because the provenance token alone no longer determines what the
corpus licenses** (§6.5's grammar gains the segment), and because a fixture whose licence you cannot read
off its name is a fixture somebody will reuse in the wrong gate. Note also that `synthesise` **no longer
takes a `FormulaEvaluator` argument**: the generator selects its derivation engine from `derived_by`, so
handing it our evaluator is no longer something a caller can do by habit.

**Public interface.**

```python
# src/cdfc/qualify/corpus/template_computed.py
class DerivedBy(StrEnum):
    CALC           = "CALC"            # src/cdfc/calc/ computed the derived cells — OUR CODE
    FOREIGN_ENGINE = "FOREIGN_ENGINE"  # the digest-pinned offline engine computed them, in a
                                       # subprocess, sharing no module with src/cdfc/
    NONE           = "NONE"            # inputs only; derived cells carry no value

@dataclass(frozen=True)
class CleanFiling:
    path: Path
    sha256: str
    provenance: CorpusProvenance
    derived_by: DerivedBy
    derived_engine_digest: str | None      # required iff derived_by == FOREIGN_ENGINE
    computed_cells: frozenset[StableKey]   # THE CELLS A PROGRAM DERIVED. Empty iff derived_by == NONE
    generator_import_closure: frozenset[str]   # module names, computed by the AST walker, not declared

def synthesise(schema: TemplateSchema, *, seed: int, n: int,
               derived_by: DerivedBy) -> tuple[CleanFiling, ...]:
    """Fill only the INPUT cells (field surface minus formula cells) from a declared
    distribution. What fills the DERIVED cells is now an explicit, recorded choice:

      CALC            src/cdfc/calc/ computes them. Ready today, needs nothing, and
                      licenses an FFR ONLY for predicates whose read set is disjoint
                      from computed_cells (F2). Its import closure contains cdfc.calc.
      FOREIGN_ENGINE  the pinned offline engine recalculates and EXPORTS A VALUE TABLE;
                      the values are written back by qualify/surgery.py (raw-zip, §0.5).
                      The engine never re-serialises the workbook — it would destroy parts
                      exactly as openpyxl does. Its import closure contains NO cdfc.calc.
      NONE            derived cells left valueless; an execution substrate only.

    Every output carries CDFC_SYNTHETIC=true, CDFC_PROVENANCE=TEMPLATE-COMPUTED,
    CDFC_DERIVED_BY and, for FOREIGN_ENGINE, the engine digest."""
```

**F2 — the corpus was generated by the code under test, and this is the repair. FATAL.**

> `synthesise` filled the inputs and *"let the workbook's own 505 formula cells compute the rest via
> `src/cdfc/calc/`"*. `P9-B1::template_diff` then *"recomputes `c`'s template formula over the filed
> inputs using P3's evaluator"* and compares. **The oracle and the system under test are the same
> function.** Three load-bearing acceptance conditions were therefore tautologies: P5's exit criterion 1
> (*clean filing ⇒ 0 FAIL*) is arithmetically impossible to violate for the 227 arithmetic predicates;
> P9's exit criterion 2 (*fires on zero template-computed clean filings*) is `x == x`, green on a
> `template_diff` that always returns `[]` **and** on one whose tolerance is 1,000×; and at G4,
> `TEMPLATE-COMPUTED` being `ADMISSIBLE` meant **`n = 189` — one command, one afternoon, deterministic
> from a seed — bought a `BLOCKING` severity tier from a corpus the product generated about itself.**
> `§7.6` declared a *transfer* residue for this corpus. **This was never a transfer question.** The
> expected FFR of an arithmetic predicate here is zero regardless of the predicate's quality, which is
> this plan's own definition of an uninformative rate and the exact condition under which
> `SELF-AUTHORED` is refused a number.

**The new mapping, stated explicitly, because "what licenses what" is the contract that changed.**

| Corpus | Derived cells produced by | Licenses an FFR for | Highest reachable severity |
|---|---|---|---|
| `SELF-AUTHORED` | anything | **nothing** — `g4_ffr.check()` raises | none |
| `TEMPLATE-COMPUTED`, `derived_by=CALC` | **us** (`src/cdfc/calc/`) | **only predicates whose read set is disjoint from `computed_cells`** — membership, numeric/integer/date bounds, `conditional_required`. **Never `sum_identity`, `cross_sheet_equality`, `tally_identity` or `TEMPLATE_DIFF`**: `UninformativeCorpusError` | `ADVISORY` |
| `TEMPLATE-COMPUTED`, `derived_by=FOREIGN_ENGINE` | a pinned engine sharing no code with `src/cdfc/` | **all classes, arithmetic included** — the oracle is independent — labelled `foreign-engine:<digest>` wherever the rate renders | `ADVISORY` |
| `TEMPLATE-COMPUTED`, `derived_by=NONE` | nobody | nothing; it is an **execution substrate** for G1 and G3ᵉ, which is all §0.3 ever needed | none |
| `REGISTER-DERIVED` | not applicable — the values are the register's | membership / identity, unchanged. **This is the positive control that stops the repair from being reject-everything** | `ADVISORY` |
| `BLIND-FILLED` · `REAL-PARTNER` · `PUBLIC` | a person, or the world | all classes | **`BLOCKING`** (P8-B4: `hi ≤ 0.02` **and** ≥ 30 non-synthetic filings) |

**No synthetic corpus of any mode can reach `BLOCKING`** — that is P8-B4's `NON_SYNTHETIC` floor, and it is
the half of F2 that closes the "buy a severity tier in an afternoon" hole even when the oracle is foreign.

**The `FOREIGN_ENGINE` fallback branch, pre-decided.** If the pinned engine cannot be run offline and
deterministically, `derived_by=FOREIGN_ENGINE` is unavailable, **the arithmetic classes have no admissible
corpus until the blind fill lands**, and that is the state the funnel reports — `NOT ADMITTED` for want of
a corpus, which is a measurement, not a stall. **What is not permitted is the previous behaviour:
arithmetic predicates drawing a zero FFR from cells our own evaluator wrote.**

**And the exit criteria that were tautologies are re-founded** — cross-document obligation, since the
criteria live elsewhere: `plan/03-phases-verdict.md` P5's exit criterion 1 and
`plan/05-phases-probes-attestation.md` P9's exit criterion 2 must both name a clean filing whose derived
cells `src/cdfc/calc/` did **not** compute (`derived_by ∈ {FOREIGN_ENGINE, NONE}`, or a blind-filled
workbook). **One such filing makes each gate non-vacuous; zero is what the plan had.**

**What each oracle licenses, stated narrowly because a narrow warrant stated broadly is the error.**

| Oracle | Warrant | Licenses an FFR for | MEASURED facts it rests on |
|---|---|---|---|
| `TEMPLATE-COMPUTED` | The regulator authored the *formulas*; **a program executed them, and which program is now recorded** | **`derived_by=CALC`: only predicates that read no computed cell. `derived_by=FOREIGN_ENGINE`: all classes, labelled with the engine digest. Never `BLOCKING` either way** — see the mapping table above (F2) | All 505 FME formula cells carry cached values; our evaluator reproduces them (G-EVAL). **The warrant that was wrong: "the regulator authored the ground truth for the derived cells" is false when we computed them — the regulator authored the rule, we computed the answer, and a predicate that re-checks our answer against our answer has measured nothing** |
| `REGISTER-DERIVED` | **Every entity in the register is validly registered, so a predicate asserting *membership* cannot have a true positive there** | **membership / identity** predicates only | **228 of 228** live FMEs return a non-empty `RegistrationNumber` via the detail endpoint. The worked counter-example: the obvious regex `^IFSCA/FME/(I\|II\|III)/\d{4}-\d{2}/\d+$` **fires on 87 of 228 — a 38.2% false-failure rate**, which is why the admitted predicate is **set membership against a snapshotted register under a declared normalisation (NFKC, `U+2011 → U+002D`, strip, case-fold), never a format grammar** |
| cross-format | The same fact appearing in two prescribed returns must agree | **cross-document** predicates | Deferred; the population is small and is published as a count, not a rate |

**The 87-of-228 regex is the single best artifact this project has for showing a reviewer why the FFR
column exists**, and it is `counterEvidence[]`'s worked example. It ships as a fixture, not as an anecdote:
`fixtures/baselines/register-regex-ffr.json`.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_template_computed.py::test_tc__only_input_cells_are_filled` | No formula cell is written directly; every derived value comes from the engine named by `derived_by` |
| unit | `…::test_tc__every_output_is_labelled` | `CDFC_SYNTHETIC=true`, `CDFC_PROVENANCE=TEMPLATE-COMPUTED` and `CDFC_DERIVED_BY` in `/docProps/custom.xml`, and a `.prov.json` sidecar whose `may_be_quoted_as` is a sentence |
| **unit** | **`…::test_tc__computed_cells_are_recorded_and_exact`** | **F2.** `filing.computed_cells` equals the set of cells the generator actually wrote a derived value into — asserted by diffing against the input-cell set, not by trusting the caller. An empty `computed_cells` with `derived_by != NONE` fails |
| **unit** | **`…::test_tc__foreign_engine_closure_excludes_calc`** | `cdfc.calc` is absent from `generator_import_closure` under `FOREIGN_ENGINE`, computed by the AST import walker P0 already ships. **Present under `CALC`** — the positive control, because a check that cannot detect the case it exists for is not a check |
| **unit** | **`…::test_tc__foreign_engine_never_reserialises`** | The engine's output is a **value table**; the workbook is written by `qualify/surgery.py` and exactly one worksheet part per write differs (§0.5). A path that saves the workbook from the engine fails, for the same measured reason openpyxl does |
| **determinism** | **`…::test_det__foreign_engine_corpus_is_pinned`** | The generated corpus is content-addressed once and pinned in `fixtures/corpus_manifest.json`; regeneration is checked against the pinned digest, so engine drift is a **failing test** rather than a silently different corpus |
| golden | `tests/golden/test_register_regex_ffr.py::test_golden__format_regex_fires_on_87_of_228` | Both integers pinned. R-GOLD-2 value assertion: the three "neither-scheme" registration numbers are listed and one of them is byte-distinguishable from its `U+002D` twin |
| golden | `tests/golden/test_register_membership_admits.py` | **Admission-side twin:** set membership under the declared normalisation fires on **0 of 228** |
| determinism | `tests/determinism/test_det__template_computed_reproduces_from_seed` | Byte-identical corpus from `{seed, template_sha256, evaluator_version}` |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-X03** (existing) | Normalisation destroys the evidence that normalisation was load-bearing | `injectors/store_normalised_only.py` | `test_nc__X03_raw_and_normalised_both_stored` · `test_nc__X03b_membership_not_format` |
| **NC-Q08e** (existing) | A synthetic rate renders without the word `synthetic` | removes the renderer check | `test_nc__Q08e_synthetic_rate_carries_the_word` |
| **NC-X01** (existing) | A host function resolves live at verdict time | `injectors/live_register.py` | `test_nc__X01_host_fn_reads_the_snapshot_only` |

**Effort.** **3 engineer-days** (`template_computed.py` **2** — the `derived_by` split, the foreign-engine
export-and-write-back path and the closure computation are +1 over the original estimate, and they are the
F2 repair — `register_derived.py` 1). Cross-format is deferred and the deferral is recorded.

---

#### P8-B3 — G4, the interval statistics, and the six-value provenance

**Files created.**

```
src/cdfc/qualify/g4_ffr.py
src/cdfc/qualify/wilson.py
src/cdfc/qualify/set_ffr.py
src/cdfc/qualify/corpus/provenance.py
docs/measurements/P8-severity.md
```

**Public interface.**

```python
# src/cdfc/qualify/wilson.py
WILSON_Z: Final[Decimal] = Decimal("1.959963984540054")   # two-sided 95%; a module constant with a test
WILSON_CTX: Final[Context] = Context(prec=28, rounding=ROUND_HALF_EVEN)

def wilson(k: int, n: int, z: Decimal = WILSON_Z) -> tuple[Decimal, Decimal, Decimal]:
    """(point, lo, hi), each quantised to 6 dp. lo and hi are CLAMPED to [0, 1].
    Decimal throughout with the pinned context and Decimal.sqrt — NEVER math.sqrt,
    because this value lands in a byte-identical attestation (P11 / G-REPRO).
    Raises ZeroSampleError on n == 0: a rate over no filings is not a small rate."""

# src/cdfc/qualify/set_ffr.py
def set_ffr(members: Sequence[PredicateId], fires: FireMatrix) -> Fraction:
    """THE DEFINITION, stated because an implementation as a MEAN was the injected break:
    the fraction of clean filings on which AT LEAST ONE member fires.
    This is what makes FFR monotone non-decreasing under union and what satisfies
        max(FFR(S), FFR(f)) <= FFR(S ∪ {f}) <= FFR(S) + FFR(f)."""

def marginal_ffr(existing: Sequence[PredicateId], f: PredicateId,
                 fires: FireMatrix) -> tuple[Fraction, tuple[PredicateId, ...]]:
    """Returns (FFR(S ∪ {f}) - FFR(S), sorted(S)) -> (marginal_ffr, conditioned_on)."""

# src/cdfc/qualify/corpus/provenance.py
class CorpusProvenance(StrEnum):
    SELF_AUTHORED    = "SELF-AUTHORED"
    BLIND_FILLED     = "BLIND-FILLED"
    TEMPLATE_COMPUTED= "TEMPLATE-COMPUTED"
    REGISTER_DERIVED = "REGISTER-DERIVED"
    REAL_PARTNER     = "REAL-PARTNER"
    PUBLIC           = "PUBLIC"

ADMISSIBLE: Final[frozenset[CorpusProvenance]] = frozenset(CorpusProvenance) - {CorpusProvenance.SELF_AUTHORED}
NON_SYNTHETIC: Final[frozenset[CorpusProvenance]] = frozenset({          # F2 / F12: what a person
    CorpusProvenance.BLIND_FILLED, CorpusProvenance.REAL_PARTNER,        # or the world produced,
    CorpusProvenance.PUBLIC})                                            # not what we generated

class UninformativeCorpusError(RuntimeError): ...

# src/cdfc/qualify/g4_ffr.py
def independent(corpus: CleanCorpus, cand) -> bool:
    """COMPUTED, NEVER DECLARED (F5). Both conjuncts, in this order:

      (1) read_keys(cand) & corpus.computed_cells == frozenset()
          -- the predicate does not re-check a cell the corpus generator derived; OR
          corpus.derived_by is FOREIGN_ENGINE and
          corpus.generator_import_closure & evaluation_import_closure(cand) == frozenset()
          -- the derivation shares no module with the thing that re-checks it.
      (2) corpus.provenance is not SELF_AUTHORED.

    read_keys() comes from P4's both-ways AST check, so it is exact rather than an estimate.
    evaluation_import_closure() and generator_import_closure use P0's import walker.
    THERE IS NO SETTER. `clean_corpus_independent_of_predicate` is the RESULT of this call."""

def check(cand, corpus: CleanCorpus, admitted: Sequence[AdmittedPredicate]) -> GateOutcome:
    """Raises UninformativeCorpusError when corpus.provenance is SELF-AUTHORED,
    AND — the same exception, the same fail-closed shape, in the same function, so there is
    no second code path to forget — when independent(corpus, cand) is False (F2, F5).
    NOT 'returns 0'. NOT 'returns a rate with a caveat'. RAISES —
    so that no code path can carry an uninformative number forward.

    The GateOutcome records which conjunct failed, the intersecting cells (capped and
    sorted) and the intersecting modules, because a rejection whose reason is not
    reconstructible is not a rejection."""
```

**Six values, and the one that is not a number.** `SELF-AUTHORED` renders as `—` and the word
*uninformative*, **and the schema forbids a number**, because an FFR measured on a corpus its authors also
wrote has expected value zero regardless of predicate quality. Printing *"0.0% false failures across 340
clean filings"* is worse than printing nothing, because **it has the shape of evidence**. The two Wilson
intervals that must never be allowed to look alike are `0/340 → [0.000, 0.011]` and `0/4 → [0.000, 0.490]`.

**The record every admitted predicate carries.** Absent any field, the predicate does not load.

```yaml
g4:
  fired: 2
  n: 96                                # FILINGS. never cells.
  rate: 0.020833
  wilson: [0.005732, 0.072807]         # two-sided, clamped, 6 dp, Decimal
  corpus_id: "blind-fill-v2"
  corpus_provenance: "BLIND-FILLED"
  corpus_derived_by: "NONE"            # CALC | FOREIGN_ENGINE | NONE — F2. Absent field ⇒ does not load
  corpus_derived_engine_digest: null   # required iff corpus_derived_by == FOREIGN_ENGINE
  n_non_synthetic: 96                  # filings whose provenance is in NON_SYNTHETIC. Gates BLOCKING
  person_a_kind: "human"               # or "model-instance" — renders wherever the FFR renders
  clean_corpus_independent_of_predicate: true    # COMPUTED by g4_ffr.independent(). Not settable.
                                                 # The loader REFUSES a record in which this field
                                                 # disagrees with a recomputation (F5)
  heldout: {fired: 1, n: 22, wilson: [...], slice: "close-ended restricted schemes",
            declared_at: "corpus/SLICES.md@<sha>"}     # or null, with a reason
  marginal_ffr: 0.010417
  conditioned_on: ["P-0007", "P-0019"]
```

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_wilson.py::test_wilson__zero_of_four_upper_bound_is_0490` | `hi(0,4) == Decimal("0.489891")` |
| unit | `…::test_wilson__two_of_96_matches_the_spec_example` | `(lo, hi) == (0.005732, 0.072807)` |
| unit | `…::test_wilson__zero_of_340_upper_is_0011` | `hi(0,340) == Decimal("0.011172")` — the interval that must not look like `0/4`'s |
| unit | `…::test_wilson__lower_bound_is_clamped_to_zero` | `lo(0,340) == 0`, **not `-0.000000`.** A negative rate must never reach a surface |
| unit | `…::test_wilson__zero_sample_raises` | `n == 0 ⇒ ZeroSampleError` |
| unit | `…::test_wilson__z_is_a_pinned_constant` | `WILSON_Z` equals the two-sided 97.5th percentile to 15 dp; a different `z` is a different gate |
| **unit** | **`…::test_wilson__blocking_threshold_is_n_189_at_zero_fires`** | `hi(0,188) > Decimal("0.02") >= hi(0,189)`. **The spec's "roughly n ≥ 185" is DERIVED and off by four; the module computes the threshold and `docs/measurements/P8-severity.md` publishes the correction** |
| property | `tests/property/test_prop_wilson.py::test_prop__wilson_brackets_the_point` | Property: `lo ≤ k/n ≤ hi` for all `0 ≤ k ≤ n ≤ 10⁶`; width strictly decreasing in `n` at fixed `k/n`. Generator: integer pairs |
| property | `tests/property/test_prop_set_ffr.py::test_prop__set_ffr_subadditivity` | Property: `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`. Generator: random predicate fire-vectors over a corpus of `n` filings. **The mean implementation violates the lower bound on a crafted pair** |
| determinism | `tests/determinism/test_det__wilson_is_byte_identical` | The 6-dp strings are identical across TZ/hash seed/locale/cwd and on the second runner image. Guards G-REPRO |
| contract | `tests/contract/test_contract__six_corpus_provenances` | Exactly 6; the register value spelled `REGISTER-DERIVED`; `NON_SYNTHETIC` is exactly `{BLIND-FILLED, REAL-PARTNER, PUBLIC}` |
| contract | `tests/contract/test_contract__g4_record_is_complete` | A `qualification.g4` missing `corpus_id`, `corpus_provenance`, `corpus_derived_by`, `n`, `n_non_synthetic`, `wilson`, `marginal_ffr` or `conditioned_on` fails to load |
| **unit** | **`tests/unit/test_g4_ffr.py::test_clean_corpus_is_not_produced_by_the_code_under_test`** | **F2 / F5, and it is test 2 of the adversary's ten.** For a `sum_identity` predicate over `'3. Portfolio'!O7` against a `derived_by=CALC` corpus: `read_keys ∩ computed_cells != ∅` ⇒ `UninformativeCorpusError`, **not a rate of 0.000**. For the same predicate against `derived_by=FOREIGN_ENGINE`: admitted, and the record carries the engine digest |
| **unit** | **`…::test_register_derived_licenses_a_membership_ffr`** | **The positive control, and it is what stops this from being reject-everything.** `REGISTER-DERIVED` is independent of our evaluator by construction and **must still license** an FFR for the membership/identity classes. A repair that fails this test has replaced a false number with no number |
| **unit** | **`…::test_template_computed_licenses_a_membership_ffr`** | Second positive control: on a `derived_by=CALC` corpus a membership predicate reading only input cells is admitted, because its read set never touches `computed_cells` |
| **contract** | **`tests/contract/test_contract__independence_is_a_property_not_a_field`** | `clean_corpus_independent_of_predicate` has **no setter and no constructor argument**; the loader recomputes it and refuses a record whose stored value disagrees. This is the field that would have caught F2 and that, before this pass, **no build computed, no test asserted, no negative control broke and no gate read** |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q08** (existing) | A `SELF-AUTHORED` FFR renders as a number | `injectors/render_self_authored_ffr.py` | `Q08a`–`Q08e` above. **D-FFR-PROVENANCE** |
| **NC-Q10** (existing) | Set-level FFR ignored; the registry drifts to flag-everything one admission at a time. **In two of SPADE's nine pipelines, sets whose every member individually met the constraint reached composite FFR of 88% and 53%** | `injectors/set_ffr_is_mean.py` | `test_prop__set_ffr_subadditivity` · `test_nc__Q10_marginal_ffr_is_recorded` — a predicate admitted without `marginal_ffr` and `conditioned_on[]` **fails to load** |
| **NC-Q58** (new, **F2**) | **`TEMPLATE-COMPUTED` licenses an arithmetic FFR again** — the intersection check is removed, so the 277 identity predicates draw a zero false-failure rate from cells `src/cdfc/calc/` wrote, and `n = 189` buys `BLOCKING` in an afternoon | `injectors/tc_licenses_arithmetic.py` — makes `independent()` ignore conjunct (1) | `tests/negative/test_nc_predicate.py::test_nc__Q58_template_computed_cannot_license_an_arithmetic_ffr` — assert un-injected `UninformativeCorpusError` with the intersecting cells named; assert injected that a `sum_identity` predicate is admitted with `fired = 0, n = 189` and reaches a severity tier. **Admission-side twin:** `test_nc__Q58b_template_computed_licenses_a_membership_ffr` |
| **NC-Q59** (new, **F5**) | **Independence is hand-set back to `true`** in the YAML, or a constructor argument is reintroduced, so the field returns to being a string in a file that nothing computes | `injectors/independence_hardcoded.py` | `tests/negative/test_nc_predicate.py::test_nc__Q59_independence_is_computed_not_declared` — assert un-injected that setting the field by hand raises at load and that the recomputed value governs; assert injected that a corpus failing `independent()` loads with `true` and passes G4 |
| **NC-Q56** (new, **its own catalogue row now — F17**; it was defined *"under NC-Q22's entry"*, with an injector and a guard but no id, which `test_nc_meta__catalogue_schema` and `test_nc_meta__no_orphan_guard` cannot both satisfy) | **The Wilson bound is computed in `float` via `math.sqrt`**, so two machines produce two 6-dp strings and the attestation stops re-deriving | `injectors/wilson_float.py` | `tests/negative/test_nc_predicate.py::test_nc__Q56_wilson_is_decimal` — assert `math` is absent from `qualify/wilson.py`'s import closure and that the two-runner determinism test goes red under injection |

**Effort.** 3 engineer-days.

---

#### P8-B4 — Severity tiers, pre-registered

**Files created.**

```
src/cdfc/qualify/severity.py
experiments/P8/PREREGISTRATION.md      committed and hashed BEFORE the first G4 run
docs/measurements/P8-ffr.md
```

**Public interface.**

```python
# src/cdfc/qualify/severity.py
BLOCKING_MAX: Final[Decimal] = Decimal("0.02")
ADVISORY_MAX: Final[Decimal] = Decimal("0.10")
BLOCKING_MIN_NON_SYNTHETIC: Final[int] = 30      # F2 / F12. Pre-registered with the two above.

def tier(g4: G4Record) -> Severity:
    """Keyed on the WILSON UPPER BOUND, never the point estimate.
      hi <= 0.02 AND g4.n_non_synthetic >= 30   -> BLOCKING
      hi <= 0.10                                -> ADVISORY
      hi  > 0.10                                -> NOT ADMITTED   (this IS gate G4)
    Raises UninformativeCorpusError if g4.corpus_provenance is SELF-AUTHORED, or if
    g4.clean_corpus_independent_of_predicate is False: severity_tier is UNDEFINED,
    not defaulted."""
```

**Why the upper bound and not the point estimate.** `0 fires / 4 filings` has a point estimate of `0.000`
and an interval of `[0.000, 0.490]`. **A rule keyed on the point estimate would let a sample of four buy
`BLOCKING`.** The upper bound makes the tier a statement about *evidence* rather than about *luck*.

**Why the upper bound alone was still not enough, which is the second half of F2. DECIDED.** The interval
is a statement about a *sample*, and a sample the product generates is unbounded in `n` at a cost of one
command: `synthesise(..., n=189)` clears `hi ≤ 0.02` in an afternoon. **`BLOCKING` therefore additionally
requires `n_non_synthetic ≥ 30`** — at least thirty filings a person or the world produced, whatever the
total `n`. *Alternative it beat:* forbidding synthetic filings from the FFR denominator entirely —
rejected because a foreign-engine corpus is genuinely informative about arithmetic predicates and
discarding it would cost real evidence; the floor keeps the evidence and refuses the *tier*. Consequence,
stated in advance: **until the blind-fill lane delivers 30 workbooks, the `BLOCKING` count is `0` by
construction, and `docs/measurements/P8-ffr.md` prints the reason beside the zero** — not as an absence,
but as *"`BLOCKING` requires 30 non-synthetic filings; we have `k`"*.

**The consequence, stated in advance so nobody is surprised.** On day one **almost nothing is `BLOCKING`**:
a predicate needs `n ≥ 189` clean, non-self-authored filings with zero fires to clear `0.02` on the upper
bound (§0.9). Everything enters as `ADVISORY` **with its interval printed beside it**. That is the EBA's
warnings-first convention with the measurement put back in, and it is defensible to a downstream reviewer
on day one because they already run the unmeasured version.

**Validation.**

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_severity.py::test_severity__uses_wilson_upper` | Table-driven: `(0,4) → hi 0.490 → NOT ADMITTED`; `(2,96) → [0.006, 0.073] → ADVISORY`; `(0,189)` with `n_non_synthetic ≥ 30` → `hi ≤ 0.02` → `BLOCKING` |
| **unit** | **`…::test_severity__synthetic_corpus_cannot_buy_blocking`** | **F2 / F12.** `(0, 189)` with `n_non_synthetic = 0` → **`ADVISORY`, never `BLOCKING`**, and the record carries the reason. The adversary's one-command attack, asserted as a test |
| unit | `…::test_severity__thresholds_are_constants` | `BLOCKING_MAX == 0.02`, `ADVISORY_MAX == 0.10`, `BLOCKING_MIN_NON_SYNTHETIC == 30`, asserted as constants so a change is a diff — and all three are inside `experiments/P8/PREREGISTRATION.md`'s hash |
| unit | `…::test_severity__self_authored_is_undefined_not_advisory` | `UninformativeCorpusError`, not a default |
| **unit** | **`…::test_severity__non_independent_corpus_is_undefined`** | A `g4` record whose recomputed `clean_corpus_independent_of_predicate` is `False` raises rather than tiering (F5) |
| golden | `tests/golden/test_day_one_blocking_count.py::test_golden__day_one_has_almost_nothing_blocking` | Over the current corpus, the `BLOCKING` count is **0**, and the report says so |

**Negative controls.**

| id | Break | Injector | Guard |
|---|---|---|---|
| **NC-Q09** (existing) | Severity keyed on the point estimate | `injectors/severity_point_estimate.py` | `test_nc__Q09_severity_uses_wilson_upper` · `test_nc__Q09b_day_one_has_almost_nothing_blocking` |

**Effort.** 1 engineer-day. Remaining 1 day: the measurement, `docs/measurements/P8-ffr.md`, the ledger
rows and the DoD.

---

### The measurement P8 produces

| Field | Value |
|---|---|
| **Metric** | **The first false-failure rate in this system measured on a corpus its authors did not write**, per predicate, as `(fired, n, wilson_lo, wilson_hi, corpus_id, corpus_provenance, person_a_kind)` |
| **And the aggregate that follows** | **The post-gate settled count against the pre-gate 2,373**, with the admitted count by severity tier |
| **Denominator** | `n` filings (never cells) · 3,747 cells · 280 predicates |
| **Warrant** | **MEASURED** |
| **Produced by** | `src/cdfc/qualify/g4_ffr.py` |
| **Command** | `cdfc qualify --template 7d9a1960 --through G4 --corpus blind-fill-v2 --out docs/measurements/P8-ffr.md` |
| **What did not exist before** | Today: **0 predicates admitted and a defensible settled fraction of 0%**, and the spec says so on stage. **The delta between the pre-gate and post-gate settled count is the product** |

### Exit gate — this is gate G-CORPUS

```
P8 EXITS iff ALL of:
  1. G-CORPUS resolves to one of THREE NAMED OUTCOMES, and which one is recorded in
     ci/GATES.md and rendered on every FFR-bearing surface (F12):
       PASS       n_non_synthetic >= 30 (BLIND-FILLED | REAL-PARTNER | PUBLIC).
                  The unrestricted branch: every predicate class may be admitted and
                  BLOCKING is reachable.
       RESTRICTED n >= 30 but n_non_synthetic < 30, i.e. the corpus is TEMPLATE-COMPUTED
                  and/or REGISTER-DERIVED. Admit ONLY the classes those corpora license
                  under P8-B2's mapping table; EVERY tier is capped at ADVISORY; the
                  surfaces carry the literal string `G-CORPUS: RESTRICTED`.
                  This was the old FAIL branch's fallback, and leaving it unnamed meant
                  shipping it was an undetected pass.
       FAIL       neither. No predicate is admitted; every FFR renders `uninformative`.
     `test_gcorpus__outcome_is_one_of_three_and_is_rendered` asserts the trichotomy and
     that the outcome string reaches the surface.
  2. The fill instructions AND the held-out slice were hashed and published BEFORE the first
     workbook was filled — proven from the corpus repo's commit graph, not asserted.
  3. The contamination test is green, with its positive control demonstrating the grep works.
  4. Every FFR renders with its provenance, its n and its interval, or the build fails.
  5. severity_tier is set from the Wilson UPPER bound for every admitted predicate; is UNDEFINED
     (not defaulted) wherever the provenance is SELF-AUTHORED or independence is False; and is
     never BLOCKING where n_non_synthetic < 30 (F2).
  5b. For EVERY admitted predicate, `clean_corpus_independent_of_predicate` was COMPUTED by
     g4_ffr.independent() and agrees with a recomputation at load; no admitted arithmetic
     predicate rests on a corpus whose derived cells src/cdfc/calc/ computed (F2, F5).
  6. docs/measurements/P8-ffr.md publishes the post-gate settled count beside the pre-gate 2,373,
     docs/measurements/P8-severity.md publishes the n=189 correction with its arithmetic, and
     docs/measurements/P8-mask-external-check.md publishes F36's two integers against 3,747.
  7. `make nc-sweep` reports NC-Q08, NC-Q09, NC-Q10, NC-Q56, NC-Q58, NC-Q59, NC-X01, NC-X03 and
     the contamination control as caught, AND reports `guards_flipped == guards_expected_to_flip`
     over them (F4), with DoD line C4 citing the sweep report row rather than a paste (F31);
     NC-N03 and NC-N50/N21 are reported separately with their why_impossible text and what each
     costs.
  8. `make mutation-pr` reports K/V >= 0.90 for qualify/wilson.py, qualify/set_ffr.py and
     qualify/corpus/provenance.py (Tier V, §0.8(c)).
```

### What it kills if it fails

**This is the gate whose failure the plan must survive, and it does.**

If no non-self-authored corpus can be produced: **no predicate is admitted at G4; every FFR renders
`uninformative`; `severity_tier` is undefined; the report carries `settledFraction: null` with an explicit
statement that the admissible predicate set is empty.** What still ships: the harvest, the verdict model,
the closure invariant, the Unchecked panel, the canaries, the residue set, `verify` and the attestation.

**Fallback branch, pre-decided and CORRECTED by F2 — it is now the named `G-CORPUS: RESTRICTED` outcome,
not an unnamed fallback:** admit only the predicate classes the ready-today corpora license —
**membership/identity via `REGISTER-DERIVED`; arithmetic via `TEMPLATE-COMPUTED` *only* in
`derived_by=FOREIGN_ENGINE` mode, and never via the `CALC` mode this document originally specified** — cap
every tier at `ADVISORY`, and publish the restricted admissible set with its narrow warrant stated
narrowly: *every entity in the register is validly registered, so a predicate asserting membership cannot
have a true positive there.* **Smaller, not stalled — and now visible**, because `G-CORPUS: RESTRICTED`
renders on every FFR-bearing surface instead of looking like a pass.

**If Person A is a model instance rather than a human**, `person_a_kind: "model-instance"` renders wherever
the FFR renders, and the record says the fallback is weaker than a human. It does not silently become a
`BLIND-FILLED` number that looks like a human's.

### Effort

**9.5 engineer-days** (was 8), plus **15–25 person-days of a different person** for B1 and **never added to
the engineer's total**. Split: B1 firewall **1.5** (F16's signed contamination result, F36's mask check) ·
B2 **3** (F2's `derived_by` split and the foreign-engine path) · B3 3 · B4 1 · measurement, docs, ledger
and DoD 1.

---

# §4 — THE THREE DEMONSTRATIONS THIS GROUP MUST PRODUCE

The task these phases answer to names three things that must be shown, not asserted. Each is specified
here as a command, a fixture and an assertion, so that a reviewer who did not do the work can run it.

### 4.1 D-REJECT — the gate rejects something real

**The claim.** *The qualification gate is not decorative: it refuses a predicate that is on disk, that a
mechanical harvest of a regulator's own published workbook produced, and that would have inflated the
settled fraction by 1,428 cells.*

**The artifact.** `fixtures/prescribed/ALR_V2_3_20250808_1024.xlsx`, `sha256 a414d8d3…`. Its harvest
contains **six** bound predicates. **Five** are `numeric_bound` with `formula1 == "-100000000000000000"`,
covering `Assets!B7:J93` (783 cells) · `Liabilities!B7:J65` (531) · `Other products!B7:J17` (99) ·
`Off BS Exposure!C8:C15 G13` (9) · `Reconciliation!E13 C27 E20 C13 C20 E27` (6) = **1,428 cells**. They
assert only *"this is a number"*.

**The command.**

```
cdfc qualify --template a414d8d3 --through G3e --campaign fme-v3-<seed> \
             --out docs/measurements/P7-attrition.md
```

**The assertions.** `tests/golden/test_vacuous_bound_rejection.py::test_golden__alr_five_bounds_rejected`

1. Exactly **5 of 6** ALR bound predicates are rejected.
2. Each carries `rejecting_gate ∈ {G2, G3e}` and a **measured** number: `K/O = 0/O` at G2 (no mutation of
   a financial figure under fault model v3 reaches `−1e17`), and marginal kill over baseline **B2** of `0`
   at G3ᵉ.
3. Each produces a `rejection` row with `cells_would_have_covered`, summing to **1,428**.
4. ALR's settled fraction recomputes **downward**, and `docs/HARVEST-DELTA.md` gains an entry with a
   non-empty reason and a date.

**The admission-side twin, and it is not optional.**
`tests/golden/test_real_bound_admission.py::test_golden__fme_nineteen_real_bounds_admitted` — FME's **19 of
24** bounds with `formula1 == "0"` are admitted with `K/O > 0`. **Without it, a reject-everything gate
scores perfectly on D-REJECT alone**, and every rejection-side control in this document carries an
admission-side twin for the same reason.

**And the honest limit, carried on the predicate-library screen.** After P7, the gate's demonstrated
rejections on the *flagship* workbook are whatever the funnel found — possibly none. *If the gates reject
nothing on FME, that is a publishable measurement, and the surfaces say exactly that.*

### 4.2 D-DEGENERATE — a deliberately degenerate predicate is fed to the gate and refused

**The claim.** *The gate refuses degeneracy by construction, not by the accident of what the harvest
produced.*

**The fixtures.** `fixtures/predicates/broken/P-NC07a__trivially-true.yaml` (`expr: "true"`) and
`P-NC07b__always-flag.yaml` (`expr: "false"`).

**The command.** `make nc-sweep` — which for these entries: asserts the guards pass un-injected; applies
`injectors/g3_disabled.py`; re-runs **only** the named guards; asserts at least one fails; removes the
injector; asserts the guards pass again.

**The assertions.**

| Fixture | Refused by | Assertion |
|---|---|---|
| `expr: "true"` | G3 proof arm | `¬P` UNSAT ⇒ `TRIVIALLY_TRUE` (`test_nc__Q07a`) |
| `expr: "false"` | **three independent teeth** | (i) G3 proof arm: `P` UNSAT ⇒ `ALWAYS_FLAG` (`test_nc__Q07b`); (ii) G3 empirical: control-arm spurious fires `> 0` where the required value is `0` (`test_nc__Q06c`); (iii) `random_flagger.adjusted_precision(...) ≤ 0` |
| both | the sweep's meta-test | `test_nc_meta__every_injector_flips_its_guard` — under `g3_disabled` the guards go **red**. **This is the mechanised form of *a test that has never been observed to fail is not evidence*** |

**Why three teeth for `expr: "false"`.** SPADE's own paper records that selecting **all** generated
candidates yields **100% coverage and 100% FFR**. A single tooth against the degenerate operating point is
a single point of failure in the one place the product cannot afford one.

### 4.3 D-FFR-PROVENANCE — no FFR renders without its provenance and its `n`

**The claim.** *An error rate without its corpus, its `n` and its interval cannot leave this system, and a
self-authored one renders no digits at all.*

**The command.** `make nc-sweep` for NC-Q08, plus `make contract`.

**The assertions.**

| Test | Asserts |
|---|---|
| `test_nc__Q08a_renders_uninformative` | Render a predicate with `corpus_provenance: SELF-AUTHORED`; the output contains the word `uninformative` and **`re.search(r"\d", ffr_fragment) is None`** |
| `test_nc__Q08b_api_returns_null` | `GET /v1/predicates` returns `ffr: null` with `g4_corpus_provenance: "SELF-AUTHORED"`, so a client cannot display it either |
| `test_nc__Q08c_no_ffr_without_provenance_and_n` | Any FFR lacking `corpus_id`, `corpus_provenance` or `n` **fails render** |
| `test_nc__Q08d_n_is_filings_not_cells` | `n = F`, never `n = 3,755·F`. The exchangeable unit is the FILING |
| `test_contract__g4_record_is_complete` | A `qualification.g4` missing any required field **does not load** — the data-side twin of the render-side test |
| `test_nc__Q56_wilson_is_decimal` | The interval is reproducible byte-for-byte, so *"with its interval"* is not satisfied by a number that differs between machines |

**The injector that makes these evidence rather than assertion**: `injectors/render_self_authored_ffr.py`
formats the rate anyway. The sweep asserts the flip.

### 4.4 The catalogue entries this document adds, in full

Added to `tests/negative/catalogue.yaml`, append-only, each satisfying
`test_nc_meta__every_entry_has_an_injector_or_a_reason`.

| id | component | break (one sentence) | injector | build |
|---|---|---|---|---|
| NC-Q30 | qualify | Mutants are written by a re-serialising writer instead of raw-zip surgery, so the observability diff measures the writer | `mutant_via_openpyxl` | P6-B2 |
| NC-Q31 | qualify | The observability filter reads the mutant's cached values instead of recalculating, returning `U = 0` on every campaign | `observability_cached_grid` | P6-B3 |
| NC-Q32 | qualify | The control arm draws sites from inside the predicate's upstream cone, so propagation counts as a spurious fire | `control_from_read_set_complement` | P6-B4 |
| NC-Q33 | qualify | `model_digest` ignores the operator table, so an edited operator keeps its `v3` label | `fault_digest_constant` | P6-B1 |
| NC-Q34 | qualify | The gate pipeline runs out of the decided order, so expensive gates run behind free ones | `gate_order_shuffled` | P7-B1 |
| NC-Q35 | qualify | The proviso marker list is emptied, so G0 reports `provisos_total == 0` for everything | `proviso_markers_empty` | P7-B2 |
| NC-Q36 | qualify | The ILP drops a subsumed predicate without recording the removal | `ilp_silent_removal` | P7-B3 |
| NC-Q37 | qualify | Unobservable mutants are destroyed rather than retained with their reason | `discard_unobservable` | P6-B3 |
| NC-Q38 | predicates | The Merkle root is computed without domain separation | `merkle_no_domain_sep` | P7-B4 |
| NC-Q39 | qualify | G1 admits a predicate whose declared key is `UNRESOLVED` | `g1_ignores_unresolved` | P7-B2 |
| NC-Q55 | predicates | An admission batch is written without a human signature | `admit_autosign` | P7-B4 |
| **NC-Q56** | predicates | The Wilson bound is computed in `float` via `math.sqrt`, so two machines produce two 6-dp strings | `wilson_float` | P8-B3 |
| **NC-Q57** | qualify | `claims_fault_classes` is derived from the kill vector, so G2's registry bar scores a denominator built out of its own numerator (**F1**) | `claims_from_kill_vector` | P7-B3 |
| **NC-Q58** | qualify | `TEMPLATE-COMPUTED` licenses an FFR for a predicate that re-checks a cell the corpus generator computed (**F2**) | `tc_licenses_arithmetic` | P8-B3 |
| **NC-Q59** | qualify | `clean_corpus_independent_of_predicate` is hand-set instead of computed (**F5**) | `independence_hardcoded` | P8-B3 |
| **NC-Q60** | qualify | A cell the evaluator could not compute is banked as evidence that the mutant is unobservable, shrinking `O` and raising `K/O` (**F18**) | `notrun_counts_as_identical` | P6-B3 |
| **NC-Q61** | qualify | Observability recalculates with the template's formulas, so the flagship F11 class is unobservable and `TEMPLATE_DIFF` cannot clear G2 (**F19**) | `observability_uses_template_formulas` | P6-B3 |
| **NC-Q47** | qualify | The instrument text's disputed-region exclusion is dropped and one extraction is used alone (**F35**) | `textsource_single_extraction` | P7-B0 |
| **NC-Q48** | qualify | A clause-less candidate is waved through G0, so stage one of the funnel is a constant (**F9**) | `g0_skips_clauseless` | P7-B2 |
| NC-N50 | qualify | *Impossible:* that the fault taxonomy is complete for a financial reporting workbook | NONE | P6-B1 |
| NC-N51 | qualify | *Impossible:* that `domain-policy-v1.json`'s magnitude bound is right | NONE | P7-B3 |

---

# §5 — WHAT THIS GROUP LEAVES OPEN, AND THE DECISION RULE FOR EACH

**Six** items are genuinely open in the binding documents. None is invented here; each gets a rule. **O5 and
O6 are added by the adversary pass, and O5 is the only item in this document marked OPEN — USER DECISION.**

| # | Open item | Decision rule |
|---|---|---|
| **O1** | **`domain-policy-v1.json`'s `implausible_magnitude` per dtype.** No argued basis exists anywhere in the corpus | Renders the literal string `PLACEHOLDER`. While it does, `proof_arm` returns `UNKNOWN` for every pure-bound predicate and routes it to the empirical arm. **It blocks nothing**, because D-REJECT is demonstrated at G2 and G3ᵉ. Exact question: *what is the largest value a `MILLI_USD_MILLION` cell in an IFSCA prescribed return can lawfully carry, on what argument?* |
| **O2** | **The disposition of the five non-`0` FME bounds** (68 cells): `9.99999999999999E+26`, `9.99999999999999E+21`, `-5000000` ×2, `-9999999999`. Unclassified anywhere in the corpus | **This phase measures rather than assumes.** `test_golden__fme_nonzero_bounds_disposed` asserts a disposition **exists** with a measured `K/O`, not what it is. The two `E+2x` bounds are degenerate by the same argument as ALR's `-1e17` and will fail G2 if that argument holds; the two `-5000000` bounds and the `-9999999999` bound are plausible-but-weak and may pass. **The result is a finding of this phase and belongs in `docs/measurements/P7-attrition.md`** |
| **O3** | **The fault-class id numbering** where Abraham & Erwig's 17 operators map to a different class count | The ids shift, `F11` stays the formula-override class, and `docs/FAULT-MODEL-v3.md` carries a migration table from every id quoted anywhere in the corpus to its class. *The ids are not sacred; a quoted id must resolve to exactly one class and the mapping must be published* |
| **O4** | **Person A** — spec G10, a user decision | Every FFR in the product depends on it. **Decided fallback:** the audited second-model-instance route, with the predicate-free fill prompt hashed and published **before** the first workbook is filled, `person_a_kind: "model-instance"` rendering wherever the FFR renders, and the record stating the fallback is weaker than a human. **Without one of the two, the product has no admissible predicate at all** — which is G-CORPUS's fail branch, and it ships |
| **O5** | **The corpus is sized for the gate, not for the product (F37).** 30 blind-filled workbooks satisfy G-CORPUS and license `ADVISORY`; **189 are needed before one predicate can be `BLOCKING`**, which at the measured fill rate is **95–160 person-days** — four to seven months of one person, against the **~118**-day engineering path `plan/00` §7 publishes (C6). The plan budgeted 15–25 and then called that budget the programme's longest pole | **DECIDED, default:** build to **30** and **ship with everything capped at `ADVISORY`, saying so** — the severity axis's top tier is declared *structurally unreachable at this corpus size*, and `docs/measurements/P8-ffr.md` prints `BLOCKING: 0 — requires 30 non-synthetic filings at hi ≤ 0.02; corpus has k` rather than an unexplained zero. *Alternative it beat:* silently scheduling 30 and leaving `BLOCKING` permanently undefined while the surfaces imply it is attainable — which is a schedule that shows the corpus finishing while the thing it exists to produce never arrives. **OPEN — USER DECISION:** *fund the 189-workbook corpus (95–160 person-days beyond the 30) or accept an `ADVISORY`-only product?* **It blocks nothing** — P8 ships either way — but it decides whether `BLOCKING` ever exists, and the answer belongs in `docs/measurements/P8-ffr.md` on the day it is taken |
| **O6** | **Which offline engine is pinned as the `FOREIGN_ENGINE` corpus generator** (F2's repair depends on one existing) | **DECIDED as to form:** the digest-pinned offline engine already named in `plan/00-decomposition.md` §8.2 and in G-EVAL's arm 2, run headless, exporting a **value table** only — never re-serialising the workbook. **OPEN as to the binary's version pin**, which is `plan/02-phases-foundation.md` P3's to make, since that document pins it for G-EVAL. **Decision rule:** if no engine can be pinned deterministically and offline, `derived_by=FOREIGN_ENGINE` is unavailable, the arithmetic classes have **no admissible corpus until the blind fill lands**, and the funnel reports them `NOT ADMITTED — no independent corpus`, which is a measurement |

---

# §6 — EFFORT SUMMARY

**Assumption, stated once.** One competent engineer: fluent in Python, comfortable with raw OOXML and with
SMT, working from this document with `plan/00-decomposition.md` and `plan/01-validation-methodology.md`
open, ~6 productive hours a day, no context switching, with P3's evaluator, P4's AST checker and P5's
verdict model already green. **Not dates.**

| Phase | Build | Engineer-days | Person-days (different person) |
|---|---|---:|---:|
| **P6** | B1 fault model v3 | 3 | — |
| | B2 raw-zip surgery | 1.5 | — |
| | B3 observability filter (**+0.5**: F18 three-way, F19 `formula_source`) | **3.5** | — |
| | B4 site universe + control arm | 1.5 | — |
| | measurement, doc, ledger, DoD | 1 | — |
| | **P6 total** | **10.5** | — |
| **P7** | **B0 instrument text source + D5 differential (moved from P12-B1 — F35)** | **1.5** | — |
| | B1 obligations, loader, rejection record (**+0.5**: template-derived instrument, `ObligationSource` — F9/C2) | **2.5** | — |
| | B2 G0 + G1 (incl. 50 labelled spans) | 4 | 0.5 (the labeller) |
| | B3 G2, G3 both arms, three baselines | 5 | — |
| | B4 pipeline, registry, ILP, admission | 3 | 0.25 (the admission signer) |
| | **P7 total** | **16** | **~0.75** |
| **P8** | B1 corpus firewall + manifest (**+0.5**: F16 signed result, F36 mask check) | **1.5** | **15–25 (Person A)** |
| | B2 three corpus-free oracles (**+1**: F2's `derived_by` and the foreign-engine path) | **3** | — |
| | B3 G4, Wilson, set-FFR, provenance | 3 | — |
| | B4 severity tiers | 1 | — |
| | measurement, docs, ledger, DoD | 1 | — |
| | **P8 total** | **9.5** | **15–25** |
| | **GROUP TOTAL** | **36 engineer-days** (was 32) | **~16–26 person-days** |

**Where the four extra days went, since a schedule that grows without a reason is a schedule nobody
believes.** 1.5 of them are P12-B1's work, moved to the phase that consumes it (F35) — the programme's
total is unchanged by that move, only its position. 0.5 is F9's template-derived instrument, which the plan
assumed was free and which is the difference between a funnel with a first row and a funnel without one.
The remaining 2 are the two FATAL repairs that are genuinely new code: the three-way observability
classification with `formula_source` (F18, F19) and the `derived_by` split with its foreign-engine path
(F2). **All four buy a number that would otherwise have been wrong in the direction that flatters us.**

**The scheduling fact that matters more than the total.** P8-B1's 15–25 person-days start at **day 0**, in
parallel with P0. They are not on the engineering critical path *provided they start at day 0*, and they
**become** the critical path the moment they are deferred past day ~70. If a revision quietly moves P8-B1
later, that revision has moved the critical path and should say so.

**Where the estimate is tight, honestly.** `cel_smt.py` (P7-B3) is the one item that could overrun; the
single-row abstraction and the finite unrolling are what keep it inside 5 days, and the switch trigger —
narrow the admitted subset rather than widen the translator, and drop Z3 entirely if it breaks — is stated
in advance so it is not negotiated under pressure. `PERF-MUT-OBS` (P6-B3) is the second: if the cone
optimisation is insufficient, the response is stratified sampling with the sampling rule published, never
a smaller fault model.

---

# §7 — WHAT THIS GROUP CANNOT ESTABLISH

The project's own standard demands the residue be declared. These survive every gate in this group being
green, every negative control caught, and the mutation score at threshold. They are stated here rather
than left to `plan/01-validation-methodology.md` §7 because three of them are specific to qualification.

**7.1 That a predicate encodes the obligation it claims to.** G0 proves the quote locates deterministically
and every proviso is implemented or declared. **Nothing here proves the CEL *means* the clause.** The only
published study of statute→executable-model generation reaches **51–53% outcome equivalence**, and its own
caveat is that structural similarity does not guarantee outcome equivalence or the reverse. **A predicate
can clear all five gates and enforce a rule that does not exist.** (NC-N01.)

**7.2 Any defect the fault model does not contain.** `KR = 0.82` licenses exactly one sentence: *"rejects
82% of the N defects I seeded **in the classes this predicate declared before the campaign ran**, under
fault model v3, of which U were discarded as unobservable and I as unadjudicable by our own evaluator."* The
bridge from seeded to real faults is the coupling effect and **there is no coupling study for financial
filing data.** The bridge does not exist and must not be walked across. (NC-N50.)

**7.3 That the proviso detector's recall is adequate.** P7 measures it on 50 hand-labelled spans. Fifty
spans labelled by one person is a small, self-referential denominator: the labeller and the marker-list
author are likely the same person, and the marker list lists only what we knew to look for. **The
measurement is worth having and it is not a guarantee**; the mitigation is that the recall number is
published beside every G0 attrition figure, so a reader can discount it.

**7.4 That the site universe covers the faults a filer actually makes.** The universe is the unlocked-cell
mask. A defect expressed by *not filling* a cell that a competent filer would fill is outside every
operator in the model except F05-blank, and a defect expressed in an attachment is outside the artifact
entirely. **The `U/G` and `K/O` numbers are statements about perturbations of a filled workbook.**

**7.5 That the blind-fill corpus is blind.** §6.3's mechanisms cover everything that leaves a trace — the
pre-published brief hash, the commit-order test, the manifest firewall. **None of it establishes that
Person A never saw a predicate.** Every `BLIND-FILLED` FFR in the product rests on that. It is the single
largest unverifiable input to the product's headline claim, and it is why `SELF-AUTHORED` renders as the
word `uninformative` rather than as a number: **we would rather print nothing than print a number whose
shape is evidence and whose content is zero.** (NC-N03.)

**7.6 That an FFR measured on `TEMPLATE-COMPUTED` or `REGISTER-DERIVED` data transfers to real filings.**
Both are real oracles with narrow warrants, and the warrants are stated narrowly wherever the numbers
render. Neither is a sample from the population of real FME quarterly returns, **because no such sample is
public.** A Wilson interval on a non-representative sample is a precise statement about the wrong
population, and the `corpus_provenance` field exists so that nobody can quote the interval without the
label.

> **Corrected after the adversary pass (F2), because this paragraph used to do work it could not do.** It
> declared a *transfer* residue and was cited as though it covered the case where **the corpus generator
> and the predicate are the same function**. It does not, and no residue declaration can: a rate whose
> expected value is zero *regardless of predicate quality* is not a rate that transfers badly, it is not a
> rate at all. That case is now refused by `g4_ffr.check()` rather than declared here (P8-B2, P8-B3). What
> **remains** in this residue, honestly, is two things: (a) even in `derived_by=FOREIGN_ENGINE` mode the
> arithmetic FFR measures *our agreement with a second calculator on inputs we drew from a distribution we
> chose*, not the rate at which a real filer trips the check — which is why no synthetic corpus can reach
> `BLOCKING` (P8-B4); and (b) `REGISTER-DERIVED`'s population is the live register, not the filings.

**7.7 That the gate's attrition figure means the gate is good.** A funnel that rejects nothing may mean the
harvest is clean or may mean the gate is asleep; a funnel that rejects everything may mean the gate is
strict or may mean it is broken. **The only thing that distinguishes them is the admission-side positive
control**, which is why every rejection-side control in this document carries a twin, and why
`test_golden__fme_nineteen_real_bounds_admitted` is as load-bearing as
`test_golden__alr_five_bounds_rejected`.

**7.8 That `severity_tier` means what a reader will assume it means.** `BLOCKING` means *the Wilson upper
bound of this check's false-failure rate on a declared non-self-authored corpus **of which at least 30
filings a person or the world produced** is at or below 0.02.* It does **not** mean the check is important,
nor that a failure is material. The report renders the interval beside the tier for exactly this reason,
and on day one the `BLOCKING` count is **0**.

---

## REPAIRS APPLIED (adversary pass)

Compiled against `plan/08-adversary.md`. One row per finding this document owns or shares. **Every FATAL
that touches P6, P7 or P8 is closed by a named artifact — a test, a negative control, a changed contract or
a changed threshold — never by a paragraph.** Where a repair required a decision the plan did not contain,
the decision is marked **DECIDED** with the alternative it beat; one item is **OPEN — USER DECISION**.

| id | Sev | The finding, in one line | What changed here | Where |
|---|---|---|---|---|
| **F1** | FATAL | G2's registry bar computes `K/O` over a denominator the predicate chooses after the campaign, because no envelope field holds the fault-class claim | `claims_fault_classes` made a **required, non-empty, content-addressed** envelope field (delta owed to `03` P4-B1); `g2_kill.check()` computes the bar **only** over it, raises `UnexercisedClaimError` on a claimed class with `O == 0` and `ClaimPostdatesCampaignError` unless the claim's commit is a git-ancestor of the campaign's; **both** `kr_claimed` and `kr_all_classes` stored and rendered; new **NC-Q57** with `injectors/claims_from_kill_vector.py` and an admission-side twin | §0.8(f) · P7-B3 interface, the two-bars table, four new validation rows · P7 measurement subordinate №5 · P7 exit criterion 0b · §4.1 · §4.4 |
| **F2** | FATAL | The `TEMPLATE-COMPUTED` clean corpus is generated by the code the arithmetic predicates re-check, making every arithmetic FFR zero by construction and letting a self-generated corpus buy `BLOCKING` | `synthesise` gains **`derived_by ∈ {CALC, FOREIGN_ENGINE, NONE}`** and returns `computed_cells` + `generator_import_closure`; `g4_ffr.check()` **raises `UninformativeCorpusError`** when a predicate reads a cell the generator computed (unless the generator is a pinned foreign engine sharing no module with `src/cdfc/`); the licensing mapping is restated as a table; **no synthetic corpus of any mode can reach `BLOCKING`** (`BLOCKING_MIN_NON_SYNTHETIC = 30`); the `REGISTER-DERIVED` and input-cell membership licences are kept as **positive controls**; new **NC-Q58** | §0.3 · P8-B2 (interface, mapping table, five new tests) · P8-B3 (`independent()`, record fields, three new tests) · P8-B4 · P8 exit 1/5/5b · §7.6 |
| **F9** | FATAL | The five-gate funnel is undefined at G0 for the 280 clause-less harvested candidates: either all die at stage one or stage one is decorative | **DECIDED, then ARBITRATED (C2)** — obligations gain the **`source: STATUTE \| TEMPLATE`** discriminator; harvested candidates carry `OBL-TEMPLATE-<sheet>-<ref>` with `source: TEMPLATE` against a generated, content-addressed **template instrument** whose quote is the formula or validation text, so `find(quote)` is meaningful *and falsifiable* and **G0 runs for real** (*does this predicate faithfully implement the relation it claims to implement?*); stage one renders **three integers** and `skipped` is never a survivor; **the published figure is TWO numbers, never one** — `predicates_with_a_STATUTE_obligation / 280 = 0/280` **and** `predicates_with_a_TEMPLATE_obligation / 280 = 280/280`, rendered together or not at all; NC-Q35's uniformity guard **scoped to `source == STATUTE`** (an integration bug the ruling would otherwise have created); new **NC-Q48** | P7-B1 (F9 block, `template_instrument.py`, five tests) · P7-B2 (G0 reason table, `UnsourcedObligationError`) · P7 measurement №4 · P7 exit criterion 0 · §4.4 |
| **F18** | FATAL | `U/G` measures the evaluator's coverage, not the operator mix: a `not_run` cell is identical in both grids, so its mutants leave `O` and **raise** `K/O` | Three-way classification with **`INDETERMINATE_OBSERVABILITY`**; `O = G − U − I`; `Campaign.render()` prints **six integers**; `indeterminate.jsonl` names the offending cells; `U/G` may never render without `I`; new **NC-Q60** with an admission-side twin | P6-B3 interface, arithmetic block, three new tests · P6 measurement · P6 exit 1/2/6 |
| **F19** | FATAL | F11 formula-override mutants are unobservable by construction, so the flagship class is discarded from `O` and `TEMPLATE_DIFF` can never clear G2 | **DECIDED** — `recalculate` takes a required `formula_source: Literal["TEMPLATE","FILING"]`; observability uses `FILING`, `TEMPLATE_DIFF` uses `TEMPLATE`; `test_f11_mutant_is_observable` and `tests/campaign/test_g2_admits_template_diff.py`; P6 exit gate now **fails** on `F11.O == 0`; new **NC-Q61**; cross-document obligation on `02` P3-B4 and `03` P5-B2's generated contract | P6-B3 (F19 block, three tests) · P6 exit 1 · P7-B3 validation |
| **F5** | SERIOUS | `clean_corpus_independent_of_predicate` is a declared boolean nothing computes | Made a **computed property** (`g4_ffr.independent()`), no setter, loader refuses a record disagreeing with a recomputation; new **NC-Q59** | P8-B3 |
| **F12** | SERIOUS | G-CORPUS's `n ≥ 30` is satisfiable entirely from the self-generated corpus | **G-CORPUS: RESTRICTED** made a *named third outcome* rendered on every FFR-bearing surface; PASS now requires `n_non_synthetic ≥ 30` | P8 exit 1 · "what it kills" · (gate table repaired in `00` §6) |
| **F16** | SERIOUS | The corpus firewall test cannot run under the firewall it tests | **DECIDED** — the contamination grep runs in the corpus repo's own CI and publishes a **signed result** whose digest enters `fixtures/corpus_manifest.json`; the main repo asserts the digest and never checks the tree out; `positive_control_hits > 0` asserted; manifest grows to seven keys | P8-B1 |
| **F17** | MINOR | the Wilson-bound break wore a guard suffix (`NC-Q22b`) instead of having a row, and was then closed under two ids | Given its own row as **NC-Q56** (arbitration C9; `NC-Q22b` and `NC-Q27` are both **RETIRED**) | P8-B3 · §4.4 |
| **F27** | SERIOUS | Colliding negative-control ids across four documents; two documents assert the collision away | The false claim is quoted and corrected; **per-document id ranges decided and tabulated**; this document renumbered into `Q30–Q49` / `N20–N29` one-to-one; `ci/catalogue-ids.sh` + `test_nc_meta__ids_are_unique` + `test_nc_meta__id_is_inside_its_document_range` required **at P0-B3** | §0.8(d), §0.8(e) |
| **F31** | SERIOUS | DoD line C4 is a prose paste only its author can verify | Every exit gate now cites the **sweep report row** (path + commit, carrying the captured assertion text and node id) instead of a paste | P6, P7, P8 exit gates |
| **F35** | SERIOUS | P7's G0 needs a pinned, span-addressable regulation text that only P12-B1 builds | **New build P7-B0** (1.5 d) with the D5 dual-extraction differential, the disputed-region exclusion, a sixth G0 reason `g0.quote_in_disputed_region`, and **NC-Q47**; `06` P12-B1 now references the artifact | P7-B0 · E7.7 · §6 |
| **F36** | SERIOUS | The 3,747 denominator is never validated, though the corpus lane buys the data that could | `cells_written[]` added to the corpus manifest; `tools/corpus/mask_vs_filler.py` and `test_mask_matches_what_a_competent_filler_filled` publish **two integers** against 3,747 in `docs/measurements/P8-mask-external-check.md`; a non-zero "written outside the mask" is escalated to P2, not absorbed | P8-B1 · P8 exit 6 |
| **F37** | SERIOUS | The corpus lane is sized for the gate (30) and not for the severity axis (189) | Both numbers published with their person-day cost; **DECIDED** default = build 30 and ship `ADVISORY`-capped, printing the reason beside `BLOCKING: 0`; **OPEN — USER DECISION** on funding the 189 | P8-B1 effort · §5 O5 |
| **F4** | FATAL (owned by `01`/`02`) | The sweep asserts "at least one guard fails" | This document's three exit gates additionally require `guards_flipped == guards_expected_to_flip` over their entries, so the repair binds here even if it lands late in `01` | P6, P7, P8 exit gates |
| **F3, F8, F10, F11, F13, F22, F23, F25, F26, F30, F34, F43** | — | Findings against the skeleton's gate table, P0/P5/P10/P11/P14 entries, the dependency graph and the staffing model | Repaired in `plan/00-decomposition.md`, which this document does not restate | `00` §3.1, §4, §5, §6, §7, §11 |
| **F6, F7, F14, F15, F20, F21, F24, F28, F29, F32, F33, F38, F39, F40, F41, F42, F44** | — | Not attributed to P6, P7 or P8 | Untouched here; owned by `01`, `02`, `03`, `05`, `06`, `07` | — |

**One residue of this repair pass, declared because the standard requires it.** Every closure above is a
test *specified*, not a test *run*. The three FATAL circularities were found by reading, and the instrument
that found them was one adversarial pass by one reader. **The rate at which new mechanisms are found is
itself a number this project should publish and must not claim converges** — `catalogue.yaml`'s growth log
is the only place it can come from, and after this pass that log gains nineteen rows in one commit, which
is data about the pass and not about the plan's convergence.

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C2** — F9's disposition · *this document's mechanism wins* | `ObligationKind` becomes **`ObligationSource = STATUTE \| TEMPLATE`**; the pre-existing `source: hand\|l1b\|harvest` field is renamed **`ingest_source`** so the discriminator can take the name the ruling gives it; **G0 runs for real** against the template relation; `03`'s honesty requirement is grafted on as **two published numbers, together or not at all** (`test_p7__both_obligation_counts_render_or_neither_does`, `UnpairedObligationCount`); NC-Q35's uniformity guard rescoped to `source == STATUTE` | P7-B1 public interface · the F9 DECIDED block · P7-B1 validation table · P7 measurement №4 · P7 exit criterion 0 · NC-Q35 · F9 row |
| **C6** — the `k = 0` critical path | §5 O5's "~116-day engineering path" repointed to `00` §7's **~118** | §5 O5 |
| **C9** — the catalogue | **this document's band table is deleted.** `NC-Q40`–`Q46` → **`NC-Q55`–`Q61`**, `NC-N20`/`N21` → **`NC-N50`/`N51`**; all nine old ids **RETIRED**. F17 now closes under the single id `NC-Q56` (the retired `NC-Q22b`/`NC-Q27` are both gone). Guard slugs moved with their entries | §0.8 (the deletion note + the renumber table) · §4.4 · P7-B1/B3 · F17 row · F9 row |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.

---

## C5 APPLIED — the one-sided rule for `TEMPLATE-COMPUTED`

**The defect the confirmation pass found.** G3's empirical arm gated its clean-corpus-firing threshold
(`flags ≤ 50%`) against the `TEMPLATE-COMPUTED` corpus at P7. Arbitration C5 ruled that this corpus class
may not be cited in a gate, a severity tier, or any published rate. This document held the second instance
and never opened the ruling, because C5 was written as a ruling about `03`. **That is how a ruling applied
in four of five places becomes worse than one applied nowhere: it looks settled.**

**Why it was fatal rather than untidy.** §0.3 of this document contains the argument that condemns its own
row: on a `TEMPLATE-COMPUTED` corpus the 277 arithmetic predicates have a false-failure rate of *"zero by
construction… regardless of predicate quality"*, because the corpus generator and the predicates are the
same function. A gate that a predicate passes by construction is not a gate.

**The ruling, refined — and the refinement is what keeps P7 runnable.**

> **`TEMPLATE-COMPUTED` may REJECT a predicate. It may never ADMIT one.**

This is one-sided evidence, and the asymmetry is real rather than a compromise:

- A predicate that flags **more than 50%** of a corpus built to be internally consistent is degenerate,
  and that conclusion needs no independent oracle. The synthetic corpus is a valid *upper* bound on
  quality. **Rejections stand.**
- A predicate that flags **0%** of that corpus has demonstrated nothing, because for the arithmetic
  classes the rate is zero whatever the predicate does. The synthetic corpus is **not** a lower bound.
  **Admissions do not stand.**

**Consequences, all three of them:**

1. G3ᵉ's clean-corpus-firing test runs at P7 as specified, and its result is admissible **only in the
   reject direction**. A predicate cannot clear this criterion until `BLIND-FILLED` exists at P8.
2. P7's exit gate is amended: it no longer asserts that G3ᵉ has been *satisfied*, only that it has been
   *run and its rejections applied*. **P7 can still exit.** Blocking P7 on the corpus was the alternative
   and it was rejected — it would have moved a 16-day phase behind a 15-to-25 person-day human lane for
   evidence that only ever removes predicates.
3. `test_g3e__template_computed_cannot_admit` — a predicate with a 0% firing rate on `TEMPLATE-COMPUTED`
   and no `BLIND-FILLED` evidence must not reach `ACTIVE`. Its negative-control twin: a predicate flagging
   80% of the same corpus **must** be rejected, so the reject direction is proved live rather than assumed.

**Generalised, because this will recur.** Evidence from a corpus produced by the code under test is
admissible **only in the direction that can remove a predicate from the active set, never in the direction
that adds one.** Monotone-safe by construction: a self-generated corpus can shrink the admitted set and can
never grow it.
