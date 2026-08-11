# 03 — THE VERDICT PHASES
## P4 · the predicate object, the CEL substrate, the harvest — and P5 · run assembly, the verdict model, closure, the settled fraction

**Compiled 11 August 2026 · binds `plan/00-decomposition.md` (phase ids, ordering, gates) and
`plan/01-validation-methodology.md` (test taxonomy, negative-control catalogue, DoD, CI) · sources
`spec/00`–`05`, with `spec/05-audit.md §V.7` treated as binding and recent · no dates**

---

## 0. HOW TO READ THIS DOCUMENT

### 0.1 What it covers, and what it deliberately does not

This document specifies **P4** and **P5** in full — the two phases in which the product's core object comes
into existence. Nothing else. Where a build here is argued in another document, that document owns the
argument and this one owns the code:

| Thing | Argued in | Built here |
|---|---|---|
| The E4 transfer threshold and the cost arm | `07-phases-surface-and-transfer.md` (P15) | **P4-B4** produces the *mechanical* arm's number (decomposition §9, cross-obligation 1). Neither document restates the other's figures |
| `TEMPLATE_DIFF`, spike-eligible after P5 | `05-phases-probes-attestation.md` (P9-B1), including `test_unqualified_relation_cannot_settle_a_cell` | Nothing. P5 must merely not make the spike impossible — see §P5-B1, `RunProfile.spike` |
| The blind-fill corpus, from day 0 in its own lane | `04-phases-qualification.md` (P8-B1) | Nothing. P4 and P5 have **no corpus dependency at all**, which is why they sit on the spine |
| The five gates, the registry, admission | `04-phases-qualification.md` (P6–P8) | P4 defines the *record* a gate writes into and the *loader invariant* that refuses a record without it. It does not run a gate |

**Three prohibitions this document inherits and does not renegotiate.** No fraction before the denominator
exists and has been computed twice (barrier 1, P2). No kill rate before the evaluator reproduces the
cached values (barrier 2, P3). **No predicate may be evaluated against a filing unless it loaded from the
registry with a `qualification` block** (barrier 3) — P4-B1 makes that a *type* distinction as well as a
runtime check, so that a violation is a `TypeError` at the call site rather than a policy someone
remembered.

### 0.2 Path reconciliation — normative, because the two foundation documents differ

`00-decomposition.md` §5 names primary modules loosely; `01-validation-methodology.md` §0.4 gives a full
repository layout and states that every phase specification names paths inside it. **§0.4 wins.** The
mapping is fixed here once so that no later document re-derives it:

| `00-decomposition` name | Normative path (this document, per `01` §0.4) |
|---|---|
| `src/cdfc/predicate/envelope.py` | `src/cdfc/predicates/envelope.py` |
| `cel_profile.py` | `src/cdfc/predicates/cel_profile.py` |
| `ast_walk.py` | `src/cdfc/predicates/ast_walker.py` |
| `runtime.py` (the CEL runtime) | `src/cdfc/evaluate/celrt.py` |
| `hostfn/` | `src/cdfc/predicates/host_fns/` |
| `src/cdfc/harvest/` | `src/cdfc/predicates/harvest.py` + `src/cdfc/predicates/harvest_classes/` |
| `rollup.py` | `src/cdfc/evaluate/rollup.py` |
| `settled.py` | `src/cdfc/verdict/settled_fraction.py` |
| `verdict/invalid.py` | `src/cdfc/verdict/invalid.py` — **an addition to `01` §0.4**, required by audit §V.7.3 |
| `docs/EVALUATION-CONTRACT.md` | `EVALUATION-CONTRACT.md` at the repository root (`01` §0.4). One file, one path |

**Two further additions to `01` §0.4, each with its reason.** `src/cdfc/store/` (`schema.sql`, `db.py`) —
P5 is the first phase that must persist a run, closure is specified as *one `GROUP BY` over `run_cell`*,
and SQLite is chosen precisely because **it is a file, so it can be hashed and named in the run manifest**
(spec do-not-build list: "a Postgres cluster cannot be content-addressed"). And
`src/cdfc/predicates/schema/predicate.schema.json` — the envelope's JSON Schema, sibling to
`attest/schema/attestation.schema.json`.

### 0.3 Decisions taken in this document

The spec leaves seven things genuinely open at this layer. Each is decided below with its argument and its
alternative, and each gets a one-page record under `docs/decisions/`. **Where the decision contradicts a
named artifact in `00` or `01`, that is called out, not glossed.**

| id | Question the spec leaves open | Decision | Record |
|---|---|---|---|
| **D-P4-01** | Is there a `REJECTED` predicate state? (audit §V.7.5: *"confirm before the schema is written"*, and decomposition §8.2 makes P4-B1 the confirming build) | **No.** `PredicateState` stays four-valued. A rejected candidate never acquires a `predicate_id`; it becomes a `rejection` row keyed by `candidate_sha256` with `predicate_id NULL`. A re-submitted candidate gets a **new** `candidate_sha256`; ids are never reused | `docs/decisions/D-P4-01-no-rejected-state.md` |
| **D-P4-02** | The `schema_keys` grammar. §II.4.1's example writes `"intro.tbl15.row[*].scheme_type"` while its `expr` reads `filing.intro.tbl15.rows` — root dropped, segment pluralised differently | **Keys are written in full, root included, segments verbatim from the P3 fact model, `[*]` for a comprehension-bound repeated node**: `filing.intro.tbl15.rows[*].scheme_type`, `template.vocab.scheme_type`. *Reason:* a key grammar that cannot say **which document** it read cannot express the defect NC-D01c exists to catch — a vocabulary resolved from `filing` instead of `template`. The fixture rewrites the spec's example with the root restored | `docs/decisions/D-P4-02-key-grammar.md` |
| **D-P4-03** | Is `matches()` in the admitted subset? | **Banned.** `celpy` uses Python `re`, not RE2; a step-count budget does not bound backtracking, so the only guard would be the wall-clock kill. Format checks route to **host functions** with their own test vectors and mutation scores — which is what the spec already requires of identity checks (the obvious registration-number regex fires on **87 of 228** live FMEs). *Re-open rule:* admit `matches()` only if the pinned runtime's regex engine is proven linear-time and a pathological-pattern benchmark is recorded | `docs/decisions/D-P4-03-no-regex-in-cel.md` |
| **D-P4-04** | How is the CEL conformance claim obtained if the official suite cannot be driven against `celpy` inside the phase budget? | **Fallback to a two-runtime differential harness**, and label it `DIFFERENTIAL, not CONFORMANCE` in every place the number appears, including G-CELPY's record. It is weaker for the reason `01` §7.5 gives: two implementations wrong the same way are not detected | `docs/decisions/D-P4-04-conformance-fallback.md` |
| **D-P4-05** | Mutation tier for the four modules `01` §3.5 does not assign | `predicates/envelope.py` and `predicates/cel_profile.py` → **Tier V (≥ 0.90)** (the envelope digest *is* registry identity; the profile is what keeps the runtime terminating). `predicates/harvest.py` and `harvest_classes/` → **Tier Q (≥ 0.85)** (a harvest defect is caught downstream by a gate; a gate defect is not). `evaluate/celrt.py` is already Tier V by directory | append to `docs/MUTATION-THRESHOLDS.md` |
| **D-P5-01** | When is `cells_bound` computed — the spec numbers it rule 5, after rule 3 | **Before `expr` is evaluated, and `cells_bound == 0` short-circuits to `ERROR(error.cells_bound_zero)` without compiling or running the program.** *Reason:* `all([])` is `True`; a design that lets the vacuous pass be *produced and then corrected* is trusting itself to overwrite a `PASS`. The vacuous pass must be **unreachable, not repaired**. The spec's rule numbering is conceptual; the generated contract records **evaluation order** as a separate, explicit field | `docs/decisions/D-P5-01-binding-precedes-evaluation.md` |
| **D-P5-02** | `INFORMATIONAL` requires a reason code (state ∉ {PASS, FAIL}) but has **no family** — the 30 codes span exactly five families and `INFORMATIONAL` is the sixth non-PASS/FAIL state | **The reason requirement is `state ∉ {PASS, FAIL, INFORMATIONAL}`.** An `INFORMATIONAL` item carries a mandatory `informational_note` and the producing relation's `necessary_or_expected` flag instead. *Reason:* the spec's own admission test for a code is *"two reasons are distinct iff they imply different remedies"* — an informational item implies no remedy, and "five families" is only true under this reading. **Consequence, stated because it changes a named artifact:** `01` §1.9's `test_contract__reason_code_required_iff_state_not_pass_or_fail` is renamed `test_contract__reason_code_required_iff_state_not_pass_fail_or_informational` and its exhaustive product becomes 8 × 31 (**30 codes plus `None`** — D-P5-05 adds **no** code; C3 rules that the degenerate-precondition distinction is carried by `scope_kind`) with an explicit `INFORMATIONAL` row asserting `reason is None and informational_note is not None` | `docs/decisions/D-P5-02-informational-carries-no-reason.md` |
| **D-P5-03** | Pre-flight tests "presence **and type**" — but no expected type is declared anywhere | **Type is inferred locally from the AST** (comparison against a string literal ⇒ `STRING`; arithmetic or tolerance comparison ⇒ `INT`; right operand of `in` ⇒ `LIST`; `has()` ⇒ presence only). Where inference is ambiguous the key is **presence-checked only** and the run records `type_checked: false` for that key. **A type check that did not happen is never reported as one.** The run emits `keys_type_checked / keys_preflighted` | `docs/decisions/D-P5-03-preflight-type-inference.md` |
| **D-P5-04** | `verdict` is `null` on an `INVALID` run *and* `null` while `K`/`T` are `PLACEHOLDER` — two different nulls, which is exactly the `absent ≠ empty ≠ null` failure | The `verdict` **object is always present**; `verdict.state` may be `null`; when it is, `verdict.stateWithheldBecause ∈ {"run_invalid", "policy_placeholder"}` is **required by schema** | `docs/decisions/D-P5-04-two-nulls.md` |
| **D-P4-06** *(adversary F1)* | The registry bar at G2 is `K/O ≥ 0.80` *"on the fault classes the predicate **claims** to cover"* — and **no field of the envelope holds such a claim.** The claim exists only inside the `FaultWitness` that G2 itself selects, **after** the campaign has run, from mutants that already killed | **`claims_fault_classes: tuple[str, ...]` becomes a required, non-empty field of `Candidate`, inside `envelope_projection()`** — so it is part of `code_sha256` and narrowing it after a campaign produces a *different predicate*. Declared per harvest class in a table committed before the first campaign. `g2_kill.check()` computes the bar **only** over the claimed set and **raises** when a claimed class has `O == 0` (an unexercised claim is not a claim) | `docs/decisions/D-P4-06-fault-class-claims.md` |
| **D-P4-07** *(adversary F9)* | G0's six rejection reasons all presuppose a clause; **280 of 280 harvested candidates carry `clause: None`**, and no document says what G0 does with them. If it rejects, D-REJECT is unreachable; if it skips, the funnel's first stage reads `280 → 280` and carries no information | **ARBITRATED (C2), and the ruling is the third thing.** Obligations gain a **`source: STATUTE \| TEMPLATE`** discriminator (`plan/04`). Harvested candidates are minted `OBL-TEMPLATE-<sheet>-<ref>` with `source: TEMPLATE` and **G0 runs for real** over them; the `SKIPPED_NOT_APPLICABLE` branch this row originally took is **deleted**, because it made G0 decorative for all 280. **A candidate with no statutory clause must still *declare* why:** `clause_absent_reason: str \| None` is a field of `Candidate`, **required and non-empty iff its obligation has `source == TEMPLATE`**, from a closed three-member vocabulary, inside `envelope_projection()` — which gives it **280 instances rather than zero**. The published figure is **two numbers, never one**: `predicates_with_a_STATUTE_obligation / 280 = 0 / 280` **and** `predicates_with_a_TEMPLATE_obligation / 280 = 280 / 280` | `docs/decisions/D-P4-07-clauseless-candidates.md` |
| **D-P5-05** *(adversary F13, F14)* | `inScope = cellsTotal − outOfScope − informational`, and both `OUT_OF_SCOPE` and `INFORMATIONAL` are **reachable by making the filing worse**. Deleting values can therefore make the settled fraction **rise** | **A cell may leave `inScope` only for a reason that is a function of the template, the selection, or a declared filer/period characteristic — never a function of the filing's cell values.** Mechanised as `REMOVAL_BASIS`, **`plan/05`'s `scope_kind` field read here** (arbitration **C3** — *not* a 31st reason code; the vocabulary stays at 30), two closure sub-counts, and one property test. **Only `scope_kind == DECLARED_CHARACTERISTIC` leaves; `PREDICATE_PRECONDITION` stays and is flagged for G3 re-qualification.** Full statement at P5-B4 | `docs/decisions/D-P5-05-inscope-removals-are-value-independent.md` |
| **D-P5-06** *(adversary F24)* | Three contracts for one field: P5 returns `SettledFraction \| None` (⇒ `null`), P11 asserts the schema **forbids** the property on `INVALID`, and `01` §1.9 rules an omitted field a schema violation | **On `INVALID`, `settledFraction` is PRESENT and `null`.** One rule, stated once. `compute()` still returns `None`; the **serialiser emits the key with a JSON null and may never omit it**. The JSON Schema `if/then` becomes `required: ["settledFraction"]` with `const: null` — `05` must change its `forbids` wording to match | `docs/decisions/D-P5-06-invalid-carries-a-null.md` |

### 0.4 Measurements taken while writing this document

Re-run against the artifacts on disk so this document rests on files rather than on the spec's summary of
them. Script: ad-hoc `json` read of `research/scripts/predicates.json` (harvest **v0**),
`/Users/abishaikc/Gift/.venv/bin/python`, 11 Aug 2026. **These are the v0 baseline P4-B4 must reproduce or
explain, not an authority** — v0 is from the same script family that produced two of this project's
documented silent false negatives, and it is frozen as evidence, not as truth.

**The per-workbook distribution of the 515 figure — MEASURED, v0, and it exists nowhere in the corpus:**

| Workbook (sha8) | n | by class |
|---|---:|---|
| `Reporting_Format_for_Fund_Management_Entities` `7d9a1960` | **280** | xseq 181 · sum 35 · memb 20 · numb 13 · intb 11 · sseq 11 · date 6 · tally 3 · cond 0 |
| `Updated___Quarterly_..._Capital_Market_Intermediaries` `82dd291f` | **163** | memb 52 · intb 32 · numb 29 · sum 23 · date 17 · cond 10 |
| `ITFS_Monthly_report` `446b811a` | **26** | sum 13 · memb 8 · xseq 1 · cond 1 · intb 1 · numb 1 · date 1 |
| `ALR_V2_3` `a414d8d3` | **19** | xseq 8 · numb 5 · sseq 3 · memb 1 · sum 1 · intb 1 |
| `AL_monthly_report` `79e43a7f` | **16** | memb 9 · sum 6 · cond 1 |
| `IBU_Operations_Report` `bf6bbf6b` | **10** | xseq 6 · memb 4 |
| `EDR_1__Exposure_Data_Report_1` `230a6f0c` | **1** | memb 1 |
| `Draft_ACAC_Format` `74ba7b89` | **0** | — |
| `IFSCA_Annual_Reporting_Format` `4b2d4a2b` | **0** | — |
| **total** | **515** | xseq 196 · memb 95 · sum 78 · numb 48 · intb 45 · date 24 · sseq 14 · cond 12 · tally 3 |

Four consequences that shape P4-B4 and are not optional:

1. **Non-empty on 7 of 9.** Gate **G-TRANSFER (mech)** requires ≥ 5 of 9. It is met by v0 — so the phase's
   job is to *reproduce it under the envelope format and publish the distribution*, not to discover
   whether it passes. A reproduction that lands on a different set of workbooks is a finding either way.
2. **The distribution is concentrated: 443 of 515 come from two workbooks.** Publishing 515 alone is
   banned in the spec and is mechanised here as NC-Q73.
3. **The `weak` pile is 389 records across the nine** (ALR 234 · FME 68 · AL 43 · ITFS 22 · CMI 12 ·
   ACAC 9 · IBU 1 · EDR 0 · Annual 0), typed
   `{iferror_wrapper, if_conditional_carry, other_formula, list_unresolved, dv_no_type}`. **An undeclared
   suppression is a coverage lie** — the pile becomes typed `SkipRecord`s, counted, and rendered. NC-Q74.
4. **The v0 FME numbers reconcile with `test_schema_constants` exactly**, which is the positive control
   that the v0 baseline is worth freezing: 20 membership predicates and **2 `list_unresolved` weak
   records** account for the pinned `22 list-type / 20 resolving` split, and 13 + 11 = **24 bounds** of
   which 19 carry a real `0` — the figure P7's positive control `test_nc__Q03b` depends on.

---

# P4 — THE PREDICATE OBJECT, THE CEL SUBSTRATE, AND THE HARVEST

**14 engineer-days.** Critical path. Depends on P3; gates P5.

## P4.0 What it settles

**Whether the settled fraction is *derivable* rather than *estimated*.** That is the entire reason CEL beat
plain Python plus a data-validation framework: you cannot statically determine which fields a Python
function reads, so a coverage claim over Python predicates is an inference. The claim becomes true — or
measurably false — the day `schema_keys` is machine-checked against the CEL AST **both ways** and the
shortfall is counted. Nothing before P4 can answer it, and everything after P4 quotes a number that
depends on it: pre-flight's key set (P5 rule 2) is *exact* only because of this build, and the pre-flight
guard is the structural mitigation for a defect the CEL language specification manufactures.

Secondarily: **what the harvest actually yields across all nine workbooks**, which is the cheapest evidence
in the plan on the question *product or paper about one workbook*.

## P4.1 Entry criteria

| # | Condition | Why it is a real constraint |
|---|---|---|
| E1 | **P3 complete; G-EVAL passed or its ≤ 25-cell failure branch recorded** | The harvest emits CEL over fact-model paths; the paths must exist and be stable first |
| E2 | The FME key set is **frozen** for `template_sha256 = 7d9a1960…`, with every key in `RESOLVED` state or explicitly `UNRESOLVED` | A key that re-resolves mid-phase silently invalidates every digest computed before it |
| E3 | `facts/units.py` ships `MILLI_USD_MILLION` as `int64` with `τ(n) = 5n`, and `ci/no-float-money.sh` is green | Tolerances appear inside envelopes at P4-B1; a float tolerance would be baked into a content address |
| E4 | P3's `FactTable` / `FactView` interface is published in `docs/interfaces/P3-facts.md` | P4-B2 walks CEL against it and P4-B3 binds exactly two names to it. **If `02-phases-foundation.md` names these differently, that document wins**; the divergence is absorbed in one adapter, `src/cdfc/facts/view.py`, and nowhere else |
| E5 | `tests/negative/catalogue.yaml` exists with its meta-tests green (P0-B3) | Five new entries are appended in this phase and the sweep must already be running |

---

## P4-B1 — THE PREDICATE ENVELOPE · 3 days

### Files created

```
src/cdfc/predicates/__init__.py
src/cdfc/predicates/envelope.py            the record, as two types
src/cdfc/predicates/canonical.py           RFC 8785 JCS + digest
src/cdfc/predicates/loader.py              YAML -> Candidate | Predicate, with the loader invariant
src/cdfc/predicates/schema/predicate.schema.json    additionalProperties:false at every depth
fixtures/predicates/good/P-0041__scheme-type-membership.yaml
fixtures/predicates/good/P-0007__intro-D17-integer-bound.yaml
fixtures/predicates/broken/P-NC02__no-qualification.yaml
fixtures/predicates/broken/P-NC04a__reads-undeclared.yaml
fixtures/predicates/broken/P-NC04b__declares-unread.yaml
docs/decisions/D-P4-01-no-rejected-state.md
docs/decisions/D-P4-02-key-grammar.md
```

### Public interface

```python
# src/cdfc/predicates/envelope.py
Kind            = Literal["harvested", "proposed", "hand_authored", "relation"]
PredicateState  = Literal["ACTIVE", "PROVISIONAL", "QUARANTINED", "WITHDRAWN"]   # D-P4-01: four, no REJECTED
Severity        = Literal["BLOCKING", "ADVISORY"]
Disposal        = Literal["IMPLEMENTED", "DECLARED"]

@dataclass(frozen=True, slots=True)
class Proviso:      text: str; disposal: Disposal; emits: str | None; span: tuple[int, int]
@dataclass(frozen=True, slots=True)
class Clause:       instrument: str; eId: str; span: tuple[int, int]; quote: str; provisos: tuple[Proviso, ...]
@dataclass(frozen=True, slots=True)
class Tolerance:    tau_units_per_summand: int          # int only; None for non-arithmetic
@dataclass(frozen=True, slots=True)
class ExternalDep:  endpoint: str; field: str; snapshot: str; on_missing: str

ClauseAbsentReason = Literal["derived_from_template_formula",      # a <f> element in the pinned blank
                             "derived_from_data_validation",       # a dataValidation in the pinned blank
                             "derived_from_template_constant"]     # a vocabulary or constant

@dataclass(frozen=True, slots=True)
class Candidate:
    """A predicate that has NOT been through the gates. It cannot be evaluated against a filing:
    no function in cdfc.evaluate accepts this type. Barrier 3, expressed as a type."""
    id: str; version: int; kind: Kind; template: str
    schema_keys: tuple[str, ...]; host_fns: tuple[str, ...]
    obligation_id: str; clause: Clause | None; rationale: str
    # ^ C2: obligation_id is NO LONGER OPTIONAL. Every candidate carries one. A harvested candidate
    #   carries OBL-TEMPLATE-<sheet>-<ref> whose Obligation has source == TEMPLATE (plan/04 P7-B1).
    clause_absent_reason: ClauseAbsentReason | None
    # ^ D-P4-07, re-keyed by C2: REQUIRED AND NON-EMPTY IFF the referenced obligation has
    #   source == TEMPLATE  (equivalently, iff `clause is None`, since only a STATUTE obligation
    #   carries a Clause).  It explains why NO STATUTORY CLAUSE IS CITED -- which is a live question
    #   for all 280 harvested candidates, so the field has 280 instances, not zero.
    claims_fault_classes: tuple[str, ...]              # D-P4-06. REQUIRED, NON-EMPTY, every kind.
    applicable: str; expr: str; witness: str
    reason_if_inapplicable: str; tolerance: Tolerance | None
    external_deps: tuple[ExternalDep, ...]

@dataclass(frozen=True, slots=True)
class Predicate(Candidate):
    qualification: Qualification          # REQUIRED. No default. Written by L4, never hand-edited
    qualified_against: QualifiedAgainst   # every element is part of the predicate's IDENTITY
    severity_tier: Severity               # set by the measured FFR, never by hand
    state: PredicateState
    withdrawn_reason: Literal["rule_amended","ffr_exceeded_threshold","superseded_by","source_schema_changed"] | None

# src/cdfc/predicates/canonical.py
def jcs(obj: Mapping[str, Any]) -> bytes                 # RFC 8785, no exceptions, no options
def envelope_projection(c: Candidate | Predicate) -> dict[str, Any]   # THE serialisation the digest covers
def code_sha256(c: Candidate | Predicate) -> str         # sha256(jcs(envelope_projection(c))), lowercase hex

# src/cdfc/predicates/loader.py
class UnqualifiedPredicateError(Exception): ...
class EnvelopeSchemaError(Exception): ...
def load_candidate(src: Path | Mapping) -> Candidate      # used ONLY by cdfc.qualify (P7)
def load_predicate(src: Path | Mapping) -> Predicate       # raises UnqualifiedPredicateError; the run path
def dump(c: Candidate | Predicate) -> Mapping[str, Any]
```

**The loader invariant, stated as the spec states it:** *a predicate row with no qualification row does not
load.* It is enforced twice on purpose — once by the type (`evaluate_one(p: Predicate, …)` will not accept
a `Candidate`) and once at runtime by `load_predicate`. The post-hoc check is kept though redundant, for
the same reason the L2b post-hoc key guard is kept: **it is the one you can prove to a reviewer.**

#### **`claims_fault_classes` — the field that stops a predicate choosing its own denominator** (D-P4-06)

Every binding document repeats that G2's registry bar is *"`K/O ≥ 0.80` on the fault classes the predicate
**claims** to cover"*. **Before this repair, no field of the envelope held such a claim.** The only place a
fault class appeared was `FaultWitness.fault_class` — *"the class the predicate CLAIMS to cover"* — and the
witness set is **selected by `qualify/g2_kill.py` at admission, from mutants that already killed.** The
numerator was choosing its denominator, at the gate that exists to catch exactly that.

**The failure this permitted, concretely.** A `sum_identity` predicate over `'3. Portfolio'!O7` runs against
a 14-class campaign. It kills F01 (sign flip) and F03 (off-by-one) on its own read set; it is structurally
blind to F10 (legal enum substitution), F12 (homoglyph), F13 (carry desync, pair form) and F14
(vocabulary-gap). Overall `K/O = 0.21`. G2 selects three witnesses from the mutants that died — all F01/F03
— stamps `fault_class: F01` on them, and evaluates the bar over `{F01, F03}`, where `K/O = 0.97`. **The
predicate is admitted `BLOCKING`, the library prints `0.97`, the attestation signs it, and nothing in the
plan is red.** NC-Q05 checks the arithmetic (`K ≤ O ≤ G`) and NC-Q06 the site universe; both are satisfied.
The defect is in the *class partition*, and no control reached it.

**The four properties of the repair, each with the artifact that enforces it:**

1. **Required and non-empty, on `Candidate` — not on `Predicate`.** The claim must exist *before*
   qualification, because a field only `Predicate` carries is a field written after the campaign.
   `test_envelope__claims_fault_classes_is_required_and_non_empty` — an empty tuple raises
   `EnvelopeSchemaError` naming the file.
2. **Inside `envelope_projection()`, therefore inside `code_sha256`.** Narrowing the claim after a campaign
   produces a **new digest, i.e. a different predicate**, which the registry treats as a new admission with
   a new qualification record. `test_prop__every_envelope_field_is_covered_by_the_digest` already reads the
   field list from `dataclasses.fields()` at runtime, so it covers the new field the moment it is added —
   this is the property paying for itself. Plus the explicit case:
   `test_envelope__narrowing_a_claim_changes_the_digest`.
3. **Every claimed class must be exercised on the campaign.** `g2_kill.check()` **raises** if any claimed
   class has `O == 0` on this campaign — *an unexercised claim is not a claim* — which also makes
   over-claiming self-punishing in the honest direction: a wider claim is a **harder** bar, never a softer
   one. (P7-B3's half; obligation **X1** below.)
4. **The claim must predate the campaign, and git is the evidence.**
   `test_g2_denominator_is_declared_before_the_campaign` asserts the commit introducing a predicate's
   `claims_fault_classes` is a **git-ancestor** of the campaign id it is scored against — exactly as
   `test_corpus__brief_predates_first_workbook` does for the fill brief. Injector
   `injectors/claims_from_kill_vector.py` derives the claim from the classes that killed; guard
   `test_nc__Q57_claims_precede_the_campaign`. **Admission-side twin:** an honestly-declared predicate
   whose claimed classes all have `O > 0` is admitted.

**And the number a reviewer actually wants:** the predicate library renders `K/O` over the **claimed** set
**and** `K/O` over **all fourteen classes**, side by side. The gap between them is the measurement.
(`07`'s render; obligation **X4**.)

#### **`clause_absent_reason` — a candidate with no *statutory* clause declares why** (D-P4-07, re-keyed by **C2**)

`clause: Clause | None` is typed optional, and **the harvest makes it `None` 280 times out of 280** — its
classes are derived from the workbook's own formulas and validations and cite no regulation. G0's six
rejection reasons (`g0.quote_not_located`, `g0.quote_ambiguous`, `g0.span_mismatch`,
`g0.proviso_undisposed`, `g0.proviso_arithmetic`, `g0.declared_proviso_missing_emission`) **all presuppose
an instrument to locate a quote in**, and nothing in any document originally said what G0 does with a
candidate that cites no regulation. Both of the branches then available were broken: reject, and ALR's five
`≥ −1e17` bounds never reach G3 so **D-REJECT — the flagship demonstration that the gate is not decorative —
is unreachable**; skip, and the funnel's first stage reads `280 → 280`, which is a gate reporting a pass it
did not compute.

> **ARBITRATION C2 — the third thing, and it is strictly better than either branch.** Obligations gain a
> **`source: STATUTE | TEMPLATE`** discriminator (`plan/04` P7-B1). A harvested predicate implements a
> relation the **regulator's template** encodes; a hand-authored one implements a clause the **statute**
> states. **Both are real obligations; they are not the same kind of thing, and collapsing them is what made
> this irreconcilable.**
>
> - **`04` wins on mechanism.** Harvested candidates are minted `OBL-TEMPLATE-<sheet>-<ref>` with
>   `source: TEMPLATE`, and **G0 runs for real** against the template relation. This document's previous
>   ruling — `obligation_id` stays `None`, candidates take `SKIPPED_NOT_APPLICABLE` at G0 — **is deleted.**
>   It made G0 decorative for all 280 candidates, and *a gate stage that cannot fail is this product's own
>   failure mode wearing a gate's clothes.*
> - **This document wins on disclosure.** The published figure is **two** numbers, never one:
>   `predicates_with_a_STATUTE_obligation / 280` — **`0 / 280` today** — and
>   `predicates_with_a_TEMPLATE_obligation / 280` — **`280 / 280` today**. The honest statement this
>   document was defending survives verbatim: ***no harvested predicate yet implements a statutory clause.***

**This document owns the envelope, so it owns the field that makes the disclosure checkable.**
`clause_absent_reason` is required and non-empty **iff the candidate's obligation has `source == TEMPLATE`**
— equivalently, iff `clause is None`, since only a `STATUTE` obligation carries a `Clause` — from the
three-member closed vocabulary above, and it is inside `envelope_projection()` so it cannot be added or
changed without a new identity. **Note what C2 does to this field: it gives it 280 instances instead of
zero.** Under `04`'s branch alone, every candidate would have had an obligation, `clause is None` would have
been read as "nothing to explain", and `test_envelope__clauseless_candidate_declares_why` would have been a
required field with no instances — *the plan's own definition of a green test with no information in it.*
Re-keyed on `source`, it fires 280 times and asks the question that is actually live: **why does this
predicate cite no statute?**

- `test_envelope__clauseless_candidate_declares_why` — an obligation with `source == TEMPLATE` and
  `clause_absent_reason is None` raises; `clause` present with `clause_absent_reason` set also raises
  (the field is an *explanation of an absence*, not an annotation); and
  `test_envelope__every_harvested_candidate_declares_why` asserts the count is **280 of 280**, so the guard
  can never quietly become instance-free again.
- **`obligation_id` is required and non-`None` for every candidate, harvested included** (C2). The
  objection this document raised against minting one — that the quote would be the reader's own parse and
  `find(quote)` would succeed by construction on 280 of 280 — is answered rather than dismissed: the quote
  is the **verbatim formula or data-validation text**, located in a content-addressed rendering of the
  pinned blank, so the check **catches a harvest run against a different template version**, which is a real
  failure mode with a real reject path (`g0.quote_not_located`, and `plan/04`'s
  `test_ti__a_stale_construct_is_not_located`).
- The G0 disposition is **not** a skip. `plan/04` P7-B2 runs G0 for real over every `source: TEMPLATE`
  obligation. Stage one still renders three integers `entered / skipped / survived`, `skipped` is never
  counted as a survivor, and under C2 `skipped == 0`; the column exists so a future obligation source
  cannot enter the funnel silently. Obligation **X2**, rewritten.

### Data produced

`fixtures/predicates/good/*.yaml` (two committed, digest-pinned), `predicate.schema.json`, and
`docs/measurements/P4-envelope-digests.md` — a table of `{fixture, code_sha256}` that later phases cite.

### Functionality validation

**Unit** — `tests/unit/test_envelope.py`
- `test_load_predicate__missing_qualification_raises` — `UnqualifiedPredicateError`, and the message names
  the file and the missing key.
- `test_load_candidate__missing_qualification_is_fine` — the positive control; without it the loader is a
  reject-everything baseline.
- `test_load_predicate__unknown_field_rejected` — `additionalProperties: false`, at every depth including
  inside `clause.provisos[]`.
- `test_load_predicate__severity_tier_cannot_be_hand_set_on_a_candidate` — a `Candidate` has no
  `severity_tier` attribute at all; setting it is an attribute error, not a validation error.
- `test_envelope__claims_fault_classes_is_required_and_non_empty` · `::narrowing_a_claim_changes_the_digest`
  · `::claims_are_drawn_from_the_pinned_fault_model` (every member resolves to a class of
  `docs/FAULT-MODEL-v3.md`; `"F99"` raises).
- `test_envelope__clauseless_candidate_declares_why` — both directions.
- `test_code_sha256__is_key_order_invariant` — the same envelope with shuffled YAML mapping order yields
  one digest.
- `test_dump__roundtrips_byte_identical` — `dump(load(x))` re-serialises to the same JCS bytes.
- `test_predicate_state__has_exactly_four_members` — D-P4-01, mechanised.

**Property** — `tests/property/test_prop_envelope.py`
- `test_prop__jcs_is_order_invariant` — *property:* shuffling any dict's insertion order anywhere in the
  tree does not change `jcs()`'s output. *Generator:* random JSON trees (depth ≤ 5, keys drawn from an
  alphabet including non-ASCII and `U+0000`-adjacent escapes), then a shuffled twin. This is `01` §1.2's
  mandated RFC 8785 property, realised here rather than at P11.
- **`test_prop__every_envelope_field_is_covered_by_the_digest`** — *property:* for a valid envelope `p` and
  any single-field perturbation `p'`, `code_sha256(p) != code_sha256(p')`. *Generator:* the field list is
  taken from `dataclasses.fields(Predicate)` **at runtime**, so adding a field to the record without adding
  it to `envelope_projection` fails this test rather than silently leaving it out of the identity. This is
  the property that catches the digest blind spot, it is the reason NC-Q70 exists, and it is what made
  `claims_fault_classes` and `clause_absent_reason` part of the identity for free the moment they were
  added to the record.

**Golden** — `tests/golden/test_predicate_envelope.py`
- `test_golden__envelope__P0041_digest` on **FME `7d9a1960`**, because it is the only workbook whose
  vocabularies live on a hidden, unprotected `Dropdown` sheet — the case D-P4-02's root-qualified key
  grammar exists to express. Per **R-GOLD-2** the digest (a value) is paired with a value assertion on the
  parsed content: `p.schema_keys == ("filing.intro.tbl15.rows[*].scheme_type", "template.vocab.scheme_type")`.

**Contract** — `tests/contract/test_contract__predicate_schema.py`
- `test_contract__predicate_schema_forbids_result_status_pass` — the same recursive walker
  (`tests/contract/schema_walk.py`) used for the attestation, applied to the predicate schema. The
  prohibition is not attestation-specific; a predicate that could carry `status` would leak it upward.
- `test_contract__rejection_has_no_predicate_id` — D-P4-01's confirmation: the `rejection` row's schema has
  `predicate_id: null` as its only admissible value at this phase.

**Negative controls** — catalogue: **NC-Q02** (a predicate with no qualification record loads), the new
**NC-Q70** (a field is dropped from the canonical serialisation), **NC-Q57** (the fault-class claim is
derived from the kill vector after the campaign) and **NC-Q75** (a clause-less candidate carries no
declared reason). Positive-control twin required by `01` §2.0 rule C5:
`test_load_candidate__missing_qualification_is_fine` and `test_golden__envelope__P0041_digest`.
*Ids follow `02` §1 R5a's band table: this document defines `Q40–Q49` and `E20–E29` and nothing else.*

**Determinism** — `tests/determinism/test_det__envelope_digest_stable` — the same fixture digests
identically under `PYTHONHASHSEED=0` and `=1`, `LC_ALL=C` and `en_IN.UTF-8`, and two working directories.
A digest that moves with the hash seed is a registry root that moves with the hash seed.

**Performance** — none. This build is not on the hot path; `PERF-CORE` is unaffected and must not move.

---

## P4-B2 — THE ADMITTED CEL SUBSET AND THE AST WALKER · 4 days

**This build is what makes the settled fraction exact rather than an estimate.** It is the phase's reason
for existing.

### Files created

```
src/cdfc/predicates/cel_profile.py         the ~20-production admitted grammar and the ban list
src/cdfc/predicates/ast_walker.py          parse -> read_keys / called_host_fns / bound_cells
src/cdfc/predicates/errors.py              UndeclaredKeyRead, DeclaredKeyUnread, SubsetViolation, ...
docs/decisions/D-P4-03-no-regex-in-cel.md
tests/negative/injectors/cel_profile_permissive.py
tests/negative/injectors/schema_keys_from_regex.py
```

### Public interface

```python
# src/cdfc/predicates/cel_profile.py
Slot = Literal["applicable", "expr", "witness"]
SLOT_RETURN: Final[Mapping[Slot, type]] = {"applicable": bool, "expr": bool, "witness": list}

ADMITTED_OPERATORS: Final[frozenset[str]]   # == != < <= > >= && || ! + - * / % in ?:
ADMITTED_MACROS:    Final[frozenset[str]]   # all exists exists_one map filter size has
BANNED: Final[Mapping[str, str]]            # construct -> the SENTENCE printed on rejection

class SubsetViolation(Exception):
    construct: str; slot: Slot; reason: str; offset: int

def check_subset(source: str, *, slot: Slot) -> None      # raises SubsetViolation
```

`BANNED` and its sentences — each is a rejection message a predicate author reads, so it says *why*:

| Construct | Ban reason (the sentence) |
|---|---|
| nested comprehension | *the only route to exponential blow-up the CEL specification itself names* |
| `filter()` outside `witness` | *a filter in `expr` computes a set and then discards it; the set is what a reader needs, so it belongs in `witness`* |
| `map()` outside `sum()` | *a mapped list that is not summed has no bearing on a boolean verdict* |
| `matches()` | **D-P4-03** — *`celpy` uses Python `re`; a step budget does not bound backtracking. Format checks are host functions* |
| `timestamp`, `duration`, `now` | *CEL binds no clock; every timestamp is an input recorded in the manifest* |
| `type()`, `dyn()` | *both defeat static key extraction, which is what makes the settled fraction derivable* |
| `bytes`, `uint`, protobuf messages | *no fact in the model has these types; admitting them admits an unreachable branch* |
| `double` literals | *there is no floating point below the money line* (`ci/no-float-money.sh`'s analogue inside CEL) |

```python
# src/cdfc/predicates/ast_walker.py
@dataclass(frozen=True, slots=True)
class KeyRef: root: Literal["filing", "template"]; path: tuple[str, ...]; repeated_at: tuple[int, ...]; offset: int
    def dotted(self) -> str            # D-P4-02 grammar, e.g. "filing.intro.tbl15.rows[*].scheme_type"

def parse(source: str, *, slot: Slot) -> CelAst              # celpy's parser only; nothing is evaluated
def read_keys(ast: CelAst) -> frozenset[str]                 # comprehension-bound names RESOLVED, not reported
def called_host_fns(ast: CelAst) -> frozenset[str]
def check_declared_keys(c: Candidate) -> None                # raises UndeclaredKeyRead | DeclaredKeyUnread
def bound_cells(c: Candidate, schema: TemplateSchema) -> frozenset[str]   # static upper bound on cells_bound
def inferred_types(ast: CelAst) -> Mapping[str, TypeHint | None]          # D-P5-03; None == ambiguous
```

**The both-ways check, exactly.** `check_declared_keys` compares `read_keys(parse(applicable)) ∪
read_keys(parse(expr)) ∪ read_keys(parse(witness))` against `set(c.schema_keys)`. A key read but not
declared raises `UndeclaredKeyRead`; a key declared but not read raises `DeclaredKeyUnread`. **They are
different exception types because they have different remedies** — the first means the pre-flight set is
too small and rule 2 is guarding the wrong keys; the second means the predicate's declared footprint
overstates what it settles, which inflates the settled numerator. NC-Q04 requires the two rejections to be
distinguishable, and a single `KeysMismatch` reason would fail that test.

**Comprehension binding, which is where a lexical implementation dies.** In

```
filing.intro.tbl15.rows.all(r, r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)
```

the roots read are `filing.intro.tbl15.rows[*].scheme_type` and `template.vocab.scheme_type`. **`r` is not
a key.** A regex over the source reports `r.scheme_type` as a root and misses the `[*]`, and this is the
same defect class as `<f[ >][^>]*>` over OOXML one level up — which in this project returned a *correct
count* with *wrong bodies* (`01` §0.2). Hence NC-Q72 and hence `ci/no-regex-over-xml.sh` gets a sibling,
`ci/no-regex-over-cel.sh`, scanning `src/cdfc/predicates/` for `findall(r?["']filing` and friends.

### Data produced

`docs/measurements/P4-both-ways.md` — for the 280 FME candidates: `declared == read` count, and for every
shortfall the predicate id, the two key sets and the diff. **This is the phase's headline number.**

### Functionality validation

**Unit** — `tests/unit/test_ast_walker.py`, table-driven over a fixed corpus of CEL forms:

| Form | `read_keys` must return |
|---|---|
| `filing.a.b == 1` | `{filing.a.b}` |
| `filing["a"]["b"] == 1` | `{filing.a.b}` — index syntax normalises to the dotted grammar |
| `filing.rows.all(r, r.x > 0)` | `{filing.rows[*].x}` and **not** `{r.x}` |
| `filing.rows.all(r, r.x in template.v.k)` | `{filing.rows[*].x, template.v.k}` |
| `size(filing.rows) > 0` | `{filing.rows}` |
| `has(filing.a.b)` | `{filing.a.b}` |
| `filing.rows.filter(r, r.x == 0).map(r, r.__cell__)` (witness slot) | `{filing.rows[*].x, filing.rows[*].__cell__}` |

plus `test_check_declared_keys__undeclared_read_raises_UndeclaredKeyRead`,
`test_check_declared_keys__declared_unread_raises_DeclaredKeyUnread`,
`test_check_subset__nested_comprehension_raises_with_offset`,
`test_check_subset__filter_in_expr_slot_raises_but_in_witness_slot_passes`,
`test_bound_cells__resolves_a_membership_predicate_to_its_sqref_cells` (the FME `'3. Portfolio'`
instrument-type predicate binds **210** cells over `I116:I126` and `M116:M126` with a two-value vocabulary
— a value assertion, per R-GOLD-2).

**Property** — `tests/property/test_prop_ast_walker.py`
- `test_prop__read_keys_never_reports_a_comprehension_variable` — *property:* for any admitted expression,
  `read_keys` ∩ {comprehension binding names in the source} == ∅. *Generator:* a small CEL expression
  generator over the admitted grammar with binding names drawn from a pool that deliberately collides with
  fact-model segment names (`rows`, `filing`, `template`, `x`).
- `test_prop__declared_key_grammar_roundtrips` — *property:* `KeyRef.dotted()` parsed back yields the same
  `KeyRef`. *Generator:* random paths with 0–3 `[*]` positions.
- `test_prop__bound_cells_is_monotone_in_the_key_set` — *property:* adding a key never shrinks
  `bound_cells`. Catches an intersection written where a union was meant, which would make `cells_bound`
  under-report and turn real predicates into `ERROR(cells_bound_zero)`.

**Golden** — `tests/golden/test_both_ways.py::test_golden__both_ways__fme` — over the 280 harvested FME
candidates, assert `declared == read` on **280 of 280** and pin the number. FME is the workbook because it
is the only one carrying all nine harvest classes and 181 cross-sheet carries, the class most likely to
read a key it did not declare. **This test is authored in B2 and first runs in B4**, because B4 is what
produces 280 envelopes; until then it is `status: PENDING` in the catalogue (the status `01` §2 reserves
for a phase not yet reached) and B2's own evidence is the seven-form unit table plus the two committed
`fixtures/predicates/good/` envelopes. A `PENDING` entry that is still pending at the phase exit gate is a
failed exit gate, not a deferral.

**Negative controls** — **NC-Q04** (declared keys diverge from the AST, both directions, distinct
reasons), and new **NC-Q71** (permissive subset walker) and **NC-Q72** (lexical key extraction). Each new
entry ships with its admission-side twin: `test_nc__Q71d_flat_comprehension_admitted` and
`test_nc__Q72c_both_roots_are_reported`.

**Mutation** — Tier V, threshold `K/V ≥ 0.90`, blocking from this phase (D-P4-05). Reported in the exact
form `01` §3.5 mandates, with `I`, `T` (ids listed) and every `E` argument published. **The
`and ↔ or` mutant inside `check_declared_keys` is the analogue of `01` §3.3's "single most important
mutant in the repository" and must be killed.**

---

## P4-B3 — THE RUNTIME, THE CONFORMANCE RUN, AND THE HOST-FUNCTION REGISTRY · 4 days

### Files created

```
src/cdfc/evaluate/__init__.py
src/cdfc/evaluate/celrt.py                 CelRuntime: compile + evaluate, budgeted
src/cdfc/predicates/host_fns/__init__.py   HostFnRegistry
src/cdfc/predicates/host_fns/reg_resolves.py     tri-state, snapshot-bound, never live
src/cdfc/predicates/host_fns/gstin_valid.py
src/cdfc/predicates/host_fns/template_current.py
src/cdfc/predicates/host_fns/nav_interval.py     MUST be able to return UNDERSPECIFIED
tools/cel_conformance.py
fixtures/host_fns/<name>.vectors.json      published test vectors, hashed
docs/measurements/P4-cel-conformance.md
docs/decisions/D-P4-04-conformance-fallback.md
```

### Public interface

```python
# src/cdfc/evaluate/celrt.py
@dataclass(frozen=True, slots=True)
class Budget: steps: int = 100_000; wall_ms: int = 50

class Outcome(StrEnum): OK = "OK"; ERROR = "ERROR"; BUDGET_EXCEEDED = "BUDGET_EXCEEDED"

@dataclass(frozen=True, slots=True)
class CelResult:
    outcome: Outcome
    value: bool | tuple[str, ...] | None
    error: str | None            # the CEL error text, never an exception object
    steps: int
    elapsed_us: int

class CelRuntime:
    def __init__(self, *, profile_version: str, host_fns: HostFnRegistry, budget: Budget) -> None: ...
    def compile(self, source: str, *, slot: Slot) -> CompiledProgram      # subset-checked; cached by sha256(source)
    def evaluate(self, prog: CompiledProgram, *, filing: FactView, template: FactView) -> CelResult
```

**`evaluate` never raises for a program-level failure.** It returns `Outcome.ERROR` or
`Outcome.BUDGET_EXCEEDED`. The reason is `ci/no-bare-except.sh`: if the runtime raised, every call site
would need a handler, and a handler is where `except Exception: state = NOT_RUN` is written — *a crash that
looks like a limit* (NC-E01). Making the three outcomes a **value** removes the temptation instead of
policing it. `CelRuntime.evaluate` binds **exactly two names**, `filing` and `template`; no clock, no
network, no filesystem.

```python
# src/cdfc/predicates/host_fns/__init__.py
@dataclass(frozen=True, slots=True)
class HostFn:
    name: str; version: str; signature: str; returns_tristate: bool
    fn: Callable[..., Any]; test_vector_sha256: str; mutation_score_json: str; authored_by: str

class UnregisteredHostFn(Exception): ...
class RegistryNotFrozen(Exception): ...

class HostFnRegistry:
    def register(self, hf: HostFn) -> None            # refuses duplicates and post-freeze registration
    def bind_snapshot(self, snapshot_sha256: str, records: Mapping[str, Any]) -> None
    def freeze(self) -> None                          # the set is CLOSED at evaluation time
    def get(self, name: str) -> HostFn                # raises UnregisteredHostFn
```

**`reg_resolves` cannot resolve live, by construction rather than by discipline.** It reads only from the
records handed to `bind_snapshot`; there is no HTTP client in its import closure. A registry with no bound
snapshot makes the call raise, which the evaluator maps to
`NOT_RUN(not_run.input_unavailable.register)` — never a silent live fetch. NC-X01.

**`nav_interval(scheme_type, open_closed, tenure) -> "P6M" | "P1Y" | ... | UNDERSPECIFIED`.** It returns
`UNDERSPECIFIED` wherever reg 51(1)'s *"in such manner as specified by the Authority"* is the operative
text, **and for close-ended Restricted Schemes**, because the 29th IFSCA Authority Meeting of 24 July 2026
made the owed frequency depend on 75%-by-value investor approval — **a fact the workbook does not
collect**. The item then becomes `NO_PREDICATE(no_predicate.no_obligation_specified)` and never
`.not_yet_synthesised`; conflating *the regulator did not legislate this* with *we have not got round to
it* is the most misleading thing the report could do. NC-X04a.

### The conformance run, and its fallback

`make cel-conformance` runs `tools/cel_conformance.py` against **both** `celpy` and `cel-expr-python` and
writes `docs/measurements/P4-cel-conformance.md`: passed / total on the admitted-subset slice per runtime,
and **a separately reported error-semantics slice** — because the CEL specification says an operand error
in `&&`/`||` *"will be ignored"*, and if the two runtimes differ *there specifically*, the pre-flight
guard's necessity argument behaves differently between them. The registry root records which runtime it
was qualified against, in `qualified_against.evaluator_version`.

**D-P4-04, restated where the engineer will hit it:** the official suite is textproto driven through a
conformance server. If it cannot be driven against `celpy` in ≤ 2 days, build the two-runtime differential
harness instead — every expression in the admitted grammar's coverage set through both runtimes, diffed —
and label the number `DIFFERENTIAL, not CONFORMANCE` in the measurement file, in G-CELPY's record and on
any surface that quotes it. It is weaker for the reason `01` §7.5 names: **two implementations wrong the
same way are invisible to a differential**, and that is not hypothetical in this project.

### Functionality validation

**Unit** — `tests/unit/test_celrt.py`
- `test_evaluate__error_returns_ERROR_outcome_not_an_exception`.
- `test_evaluate__step_budget_returns_BUDGET_EXCEEDED` — with a program that is legal in the subset and
  expensive (a flat comprehension over a 5,000-row synthetic fact view).
- `test_evaluate__wall_clock_kill_fires_independently_of_the_step_budget`.
- `test_compile__is_cached_by_source_digest_and_the_cache_is_not_keyed_on_object_identity`.
- `test_evaluate__binds_exactly_two_names` — `filing`, `template`; a reference to any third name is a
  compile-time `SubsetViolation`.
- `tests/unit/test_host_fns.py`: one test per published vector file, plus
  `test_registry__unregistered_call_raises_UnregisteredHostFn`,
  `test_registry__register_after_freeze_raises`,
  `test_reg_resolves__has_no_http_client_in_its_import_closure` (AST import walk),
  `test_nav_interval__close_ended_restricted_returns_UNDERSPECIFIED`.

**Property** — `tests/property/test_prop_celrt.py`
- `test_prop__evaluate_is_pure` — *property:* two evaluations of the same compiled program over the same
  fact view return equal `CelResult.value` and `.outcome`. *Generator:* random admitted expressions ×
  random fact views. Catches a host function that memoises across runs or reads a clock.
- `test_prop__no_admitted_program_exceeds_the_step_budget_on_a_bounded_fact_view` — *property:* for fact
  views of ≤ 200 rows, every generated admitted expression terminates inside the budget. A falsifying
  example is a **grammar finding**, not a budget finding, and the response is to narrow the subset.

**Differential** — `tests/differential/test_diff__celpy_vs_celexpr.py`, exercising the admitted grammar's
coverage set. **It is explicitly not one of `01` §1.4's four required differentials D1–D4** and does not
claim their status; it is the evidence behind G-CELPY.

**Negative controls** — **NC-E02c** (conformance on error semantics; the entry already exists in the
catalogue and this build is where it becomes runnable), **NC-X01** (host function resolves live),
**NC-X04** (host function cannot return its third value). No new entries.

**Determinism** — `tests/determinism/test_det__celrt_no_clock` — a program referencing a time construct
fails to compile; a full evaluation under `TZ=Pacific/Kiritimati` and `TZ=UTC` returns identical results.

**Performance** — a **new** budget, `PERF-CEL-COMPILE`: compile all 280 FME envelopes cold. There is no
measured baseline for it and this document does not invent one. **The rule:** the first CI run on the
runner image records the baseline into `perf/baseline.ci.json`; the budget is then set at **3× the recorded
baseline** (warn at 2×) and the recording is committed in the same PR. Registering a new budget is not a
budget change and does not need a `perf/BUDGET-CHANGES.md` entry; **moving it later does.**

---

## P4-B4 — THE HARVEST INTO ENVELOPES, ACROSS ALL NINE WORKBOOKS · 3 days

**This build also carries the mechanical arm of the transfer measurement (decomposition conflict 3, E4 arm
1).** The threshold and the cost arm belong to `07`; the number belongs here.

### Files created

```
src/cdfc/predicates/harvest.py
src/cdfc/predicates/harvest_classes/{cross_sheet_equality,sum_identity,membership,numeric_bound,
                                     integer_bound,same_sheet_equality,date_bound,tally_identity,
                                     conditional_required}.py
fixtures/baselines/harvest-v0.json         the frozen research output + a README naming its two defects
docs/measurements/P4-harvest-distribution.md
docs/HARVEST-DELTA.md                      append-only; first entry written by this build
predicates/harvested/<template8>/P-*.yaml  the emitted envelopes
```

### Public interface

```python
# src/cdfc/predicates/harvest.py
@dataclass(frozen=True, slots=True)
class SkipRecord:
    kind: Literal["iferror_wrapper","if_conditional_carry","other_formula","list_unresolved",
                  "dv_no_type","function_outside_vocabulary","key_unresolved"]
    sheet: str; ref: str; detail: str          # every field required; no anonymous skips

@dataclass(frozen=True, slots=True)
class HarvestResult:
    template_sha256: str
    candidates: tuple[Candidate, ...]
    by_class: Mapping[str, int]
    skipped: tuple[SkipRecord, ...]            # THE WEAK PILE, typed and counted
    cells_reachable: frozenset[str]            # union of bound_cells; the STATIC settled set

def harvest(schema: TemplateSchema) -> HarvestResult
def emit_envelopes(res: HarvestResult, out_dir: Path) -> list[Path]
def distribution(results: Sequence[HarvestResult]) -> DistributionTable   # renders all nine rows, zeroes included
```

### CLI

```
cdfc harvest --template corpus/templates/<file>.xlsx --out predicates/harvested/
cdfc harvest --all --report docs/measurements/P4-harvest-distribution.md
make harvest            # == cdfc harvest --all, then re-renders the measurement file
```

**Two rules the harvest obeys and one it must not break.** Vocabularies resolve from the **pinned blank**,
never from a filed artifact — `Dropdown` is hidden *and* the only unprotected sheet (NC-D01c). Every
formula the class set cannot express becomes a typed `SkipRecord`, never a silent omission. And **this step
cannot fail, only under-produce** — a harvest that raises has hidden something; a harvest that skips has
declared it.

### The fault-class claims, declared here, before any campaign exists (D-P4-06)

Every emitted candidate carries `claims_fault_classes`. The harvest cannot invent it per predicate, so
**each harvest class declares it once**, as a module-level constant, and the table below is
`docs/FAULT-CLAIMS.md`, **committed in this build — which is four phases before the first campaign runs, so
the git-ancestor test in `test_g2_denominator_is_declared_before_the_campaign` is satisfied by
construction rather than by discipline.**

| harvest class | `claims_fault_classes` | Why exactly these |
|---|---|---|
| `cross_sheet_equality` | `F01 F02 F03 F04 F05 F13` | 181 of these on FME; F13 (carry desync) is the class they exist for, and any single-sided perturbation of either end breaks the equality |
| `sum_identity` | `F01 F02 F03 F04 F05 F07 F08` | A row omission or duplication moves the sum; a transposition or scale slip in a summand does too |
| `tally_identity` | `F05 F07 F08` | Counts against a table body. It sees rows appearing and disappearing and **nothing about value magnitude** |
| `same_sheet_equality` | `F01 F02 F03 F04 F05` | as `cross_sheet_equality` minus the cross-sheet carry |
| `membership` | `F12` | Vocabulary drift, including the homoglyph and whitespace forms. **NOT `F10`** — a *legal* enum substituted for another legal enum is invisible to a membership test **by construction**; claiming it would be the exact lie this field exists to prevent |
| `numeric_bound` | `F01 F03` | A sign flip crosses `≥ 0`; an off-by-one crosses a boundary. **Not `F02`** — a `×10` on a positive value stays above a `≥ 0` bound |
| `integer_bound` | `F01 F03 F06` | as `numeric_bound`, plus the rounding class, because an integrality bound is exactly what F06 perturbs |
| `date_bound` | `F09` | FME's six date bounds; nothing else in the taxonomy moves a date |
| `conditional_required` | `F05` | It detects the blank-and-zero pair and nothing else |

**Two consequences, and both are numbers this phase must publish.**

1. **`F10`, `F11` and `F14` are claimed by no harvested class.** F10 (legal enum substitution) and F14
   (vocabulary-gap exploitation) are *designed misses* — they are P10's residue feedstock and the spec
   already says so. **F11 (formula override) is claimed by `TEMPLATE_DIFF`, which is a relation and is
   built at P9-B1** (obligation **X3**). So `docs/measurements/P4-harvest-distribution.md` publishes
   **`fault_classes_claimed_by_no_harvested_candidate = {F10, F11, F14}`** as a named integer-and-set, and
   `test_harvest__unclaimed_classes_are_published` asserts it renders. *A fault class nobody claims is the
   most useful thing on the page, and today no document contains the list.*
2. **Over-claiming is self-punishing and under-claiming is caught.** A wider claim is a **harder** G2 bar
   (more classes in the denominator) and any claimed class with `O == 0` **raises** at G2, so the incentive
   runs the right way in both directions. `test_harvest__claims_are_a_pure_function_of_the_class` asserts
   two harvests of the same template emit identical claims, so a claim cannot be tuned per predicate after
   a campaign without changing `code_sha256`.

### Data produced

`docs/measurements/P4-harvest-distribution.md` with all nine rows **including the two zeroes**, the class
breakdown, the skip counts by kind, and the reconciliation note that the 2 `list_unresolved` skips on FME
are exactly the pinned `22 list-type − 20 resolving` gap. Plus `docs/HARVEST-DELTA.md` entry #1 recording
any divergence from the v0 baseline in §0.4, with a reason and a date.

**Three further numbers this file must carry, none of which exists in any document today.**

**(i) `static_settled_cells`, computed — and reconciled against 2,373 in writing.**
`len(HarvestResult.cells_reachable)` for `7d9a1960` **is** the static settled set, and until this build
runs, **`2,373` is a spec figure that reconciles with nothing this project will ship.** `02` §0.2 N3a sets
this out: spec §III.4.3 attributes *"2,329 of 2,373 settled cells (98.1%)"* to **53 validation
predicates**, and the frozen v0 harvest emits **20** membership predicates from 22 list-type validations of
which 20 resolve. Either 2,373 was computed from an enumeration this build will not produce, or the 53 is
wrong. **Ruling: the file states the computed number, states 2,373 beside it, and states the delta in a
sentence. A divergence is a finding, published; it is not a number to be corrected quietly**, and
`docs/HARVEST-DELTA.md` entry #1 carries it.
`tests/golden/test_harvest_count.py::test_golden__static_settled_cells_reconcile` asserts the file contains
both integers and the delta. **Until this build runs, `2,373` may not be pinned as a literal in any golden
test** — enforced by `ci/golden-literals-are-traceable.sh`, `02` R5 registry row 17. (`07` P14-B1 pins
`S = 2,373` and `U = 1,374` as MEASURED literals in `test_golden__report_hero__fme`; those are properties
of *our code*, they will move the first time G3 rejects a predicate, and they belong in
`docs/HARVEST-DELTA.md`'s regime. Obligation **X5**.)

**(ii) THE OBLIGATION COVERAGE PAIR — two numbers, never one** (D-P4-07, arbitration **C2**):

| Published number | Today | What it means |
|---|---|---|
| **`predicates_with_a_STATUTE_obligation / 280`** | **`0 / 280`** | *No harvested predicate yet implements a statutory clause.* |
| **`predicates_with_a_TEMPLATE_obligation / 280`** | **`280 / 280`** | Every harvested predicate implements a relation the regulator's own pinned blank encodes. |

**No document in the corpus contained either number before D-P4-07, and publishing only the first was wrong
by 280 while publishing only the second concealed the thing that matters.** Every harvested candidate
carries an `obligation_id` (`OBL-TEMPLATE-<sheet>-<ref>`, `source: TEMPLATE`) **and** a declared
`clause_absent_reason`; the pair is published as a named subordinate measurement with the distribution of
`clause_absent_reason` beside it
(`derived_from_template_formula` / `derived_from_data_validation` / `derived_from_template_constant`).
`test_harvest__obligation_coverage_is_published` asserts **both** ratios render, and
`test_p7__both_obligation_counts_render_or_neither_does` (`plan/04`) raises `UnpairedObligationCount` if one
appears without the other. **The two counts are never added together.** *This is the pair that tells a
reviewer, in two lines, both that these predicates are grounded in a real regulator artifact and that not
one of them is grounded in the statute.*

**(iii) `fault_classes_claimed_by_no_harvested_candidate`** — the `{F10, F11, F14}` set above, with the
reason for each.

### Functionality validation

**Unit** — `tests/unit/test_harvest_classes.py`, one test per class asserting the emitted envelope's
`expr` in CEL and its `schema_keys`; e.g.
`test_sum_identity__emits_a_tolerance_bearing_equality` asserts
`tolerance == Tolerance(tau_units_per_summand=5)` for a money row and `tolerance is None` for a `COUNT`
row — **counts get zero tolerance; a person is not a rounded quantity** (NC-E08).

**Golden** — `tests/golden/test_harvest_count.py`
- `test_golden__harvest_count__fme` pins **280** with the class vector.
- `test_golden__cross_workbook_harvest_distribution` pins **515 with the per-workbook table attached**, all
  nine rows. Which workbooks and why: *all nine*, because 515 is a sum over a concentrated distribution
  (443 of 515 from two workbooks) and publishing it alone is banned.
- `test_golden__zero_formula_template__edr1` — `EDR_1` yields 1 membership predicate and a mechanically
  derivable settled fraction of 0%; **publish it anyway.**
- Per `01` §1.3 these are **properties of our code, allowed to move with a recorded reason**: the expected
  values are read from `docs/HARVEST-DELTA.md`'s last entry, and moving a number without appending an entry
  fails the build. The first thing P7's G3 will do is reject predicates, and this number will fall — which
  is correct behaviour, and a regression test that fails on correct behaviour gets deleted.

**Negative controls** — new **NC-Q73** (the total renders without its distribution) and **NC-Q74** (the
weak pile is dropped instead of counted), plus existing **NC-D01c** (vocabulary resolved from the filing)
and **NC-P01/NC-P02** as upstream positive controls — a harvest that yields 20 membership predicates on FME
is evidence that the `x14` validations survived ingest, and it will silently fall to 15 if they did not.

**Determinism** — `tests/determinism/test_det__harvest_is_ordered` — envelope emission order and generated
`id` assignment are a pure function of `(template_sha256, sheet index, cell ref)`, so two harvests produce
byte-identical files. A harvest keyed on set iteration order produces a different registry root every run.

### The transfer note this build owes `07`

`docs/measurements/P4-harvest-distribution.md` states, in one sentence and with the number: *the harvest
produces a non-empty predicate set on **7 of 9** prescribed workbooks (v0 baseline, MEASURED), against
G-TRANSFER (mech)'s pre-registered threshold of ≥ 5 of 9.* It does **not** state a per-predicate human cost
— that is P15's arm and this document does not touch it.

**And the filename is fixed here, once.** `07` P15-B1's entry criterion requires
`docs/measurements/P4-transfer-mechanical.md`; this build produces
`docs/measurements/P4-harvest-distribution.md`. **There is one file and it is
`docs/measurements/P4-harvest-distribution.md`** — the transfer note is a section of it, because splitting
one measurement across two files is how the two names came to exist. It is exposed as the module constant
`cdfc.measure.paths.P4_HARVEST_DISTRIBUTION` (created at `02` P0-B1), and **`07` imports the constant
rather than re-typing a filename**, per `06` §0.9's rule. Obligation **X6**.

---

## P4.2 The measurement this phase produces

Six numbers, none of which exists today. **(d), (e) and (f) are new in the adversary repair and three of
the five gates downstream are unreadable without them.**

| # | Number | Denominator | Warrant | Where |
|---|---|---|---|---|
| **a** | **`schema_keys` both-ways agreement** — candidates whose declared key set equals their AST-read key set | **280** FME candidates | MEASURED | `docs/measurements/P4-both-ways.md` |
| **b** | **The per-workbook distribution of the 515 figure**, with the skip counts beside it | **9** workbooks | MEASURED (v0 baseline in §0.4; this build reproduces or explains it) | `docs/measurements/P4-harvest-distribution.md` |
| **c** | CEL agreement on the admitted subset, and **separately** on the error-semantics slice, per runtime | expressions in the suite (or in the differential harness) | MEASURED, labelled `CONFORMANCE` or `DIFFERENTIAL` per D-P4-04 | `docs/measurements/P4-cel-conformance.md` |
| **d** | **`static_settled_cells` computed from the emitted envelopes, and its delta from the spec's 2,373** | **3,747** (the FME field surface) | MEASURED, **with 2,373 labelled `DERIVED-FROM-SPEC`** | `docs/measurements/P4-harvest-distribution.md` |
| **e** | **`predicates_with_a_STATUTE_obligation / 280`** — expected `0 / 280` — **and `predicates_with_a_TEMPLATE_obligation / 280`** — expected `280 / 280` — **rendered together or not at all** (C2), with the `clause_absent_reason` distribution | **280** | MEASURED | same file |
| **f** | **`fault_classes_claimed_by_no_harvested_candidate`** — expected `{F10, F11, F14}` — with the reason each is unclaimed | **14** fault classes | MEASURED | same file |

**What (a) means and what it does not.** A shortfall is *the measured size of the gap between "derivable"
and "estimated"* — nothing more. It does not establish that any predicate means what its clause means; that
is **NC-N01**, where a negative control is impossible, and the cost is stated there: a predicate can clear
all five gates and enforce a rule that does not exist.

Ledger rows (append to `reports/validation-ledger.jsonl`, one per number):

```json
{"phase":"P4","build":"P4.2","metric":"schema_keys.both_ways_agreement.fme","numerator":280,
 "denominator":280,"denominator_source":"harvested candidates for template 7d9a1960",
 "warrant":"MEASURED","produced_by":"src/cdfc/predicates/ast_walker.py",
 "command":"cdfc predicate lint predicates/harvested/7d9a1960/ --both-ways",
 "caveat":"licenses one sentence: the declared key set equals the AST-read key set for N of 280 candidates. It says nothing about whether a predicate encodes its clause.","date":"____-__-__"}
```

## P4.3 Exit gate — evaluable by someone who did not do the work

All **eleven** must be true. Each is a command whose output is read from `reports/` or `docs/measurements/`.

1. `make golden` green, with `test_golden__harvest_count__fme` pinning **280** and
   `test_golden__cross_workbook_harvest_distribution` pinning **515 with all nine rows attached**, and
   `docs/HARVEST-DELTA.md` carrying entry #1. **`ci/golden-literals-are-traceable.sh` green** — every
   integer literal these goldens compare resolves to `01` §0.3's table or a ledger row. `2,373` resolves to
   neither and therefore appears in **no** golden at this phase.
1a. **`claims_fault_classes` is required, non-empty and inside `code_sha256` on every emitted envelope**;
   `docs/FAULT-CLAIMS.md` is committed **in this phase**, i.e. its commit is a git-ancestor of every future
   campaign id; `test_envelope__narrowing_a_claim_changes_the_digest` and
   `test_harvest__claims_are_a_pure_function_of_the_class` green; **NC-Q57 caught.** *Without this, G2's
   registry bar is computed over a set the predicate picks after the campaign, and a predicate that kills
   one class of one operator scores `1.00` and is admitted `BLOCKING`.*
1b. **`clause_absent_reason` is required exactly when the candidate's obligation has `source == TEMPLATE`**
   (C2), `test_envelope__clauseless_candidate_declares_why` and
   `test_envelope__every_harvested_candidate_declares_why` green (**280 instances, not zero**),
   **NC-Q75 caught**, and **both** obligation-coverage numbers published together —
   `predicates_with_a_STATUTE_obligation / 280 = 0 / 280` **and**
   `predicates_with_a_TEMPLATE_obligation / 280 = 280 / 280` — with the `clause_absent_reason`
   distribution. Publishing either alone fails this criterion. *Without this, P7's funnel has an undefined
   first stage over 100% of its input population, or a defined one whose headline number is wrong by 280.*
1c. **`docs/measurements/P4-harvest-distribution.md` carries `len(cells_reachable)` for `7d9a1960`, the
   spec's 2,373 beside it, and the delta in a sentence**, plus
   `fault_classes_claimed_by_no_harvested_candidate`. A divergence from 2,373 is written up as a finding in
   `docs/HARVEST-DELTA.md`, **not reconciled by adjusting the harvest.**
2. **Both-ways AST check green on 280 of 280**, or the shortfall published in
   `docs/measurements/P4-both-ways.md` with every diff listed and the failure branch in §P4.4 invoked in
   writing.
3. `docs/measurements/P4-cel-conformance.md` exists, records both runtimes, reports the error-semantics
   slice separately, and states which runtime the registry root is qualified against. **Gate G-CELPY
   decided and recorded in `ci/GATES.md`.**
4. `make nc-sweep` reports the **seven** new entries (**NC-Q70, Q41, Q42, Q43, Q44, Q45, Q46**) as
   `caught`, **and `guards_flipped == guards_expected_to_flip`** — every guard declared `flips: true` was
   observed red and every `flips: false` positive control stayed green (`02` P0-B3's exact-set sweep).
   DoD line C4 cites the sweep report's row and node id, not a pasted assertion. Every entry carries an
   admission-side positive control. **`ci/catalogue-ids.sh` green** — this document's ids are inside its
   `Q40–Q49` / `E20–E29` band (`02` R5a) and are defined nowhere else.
5. `make mutation-pr` reports Tier V `K/V ≥ 0.90` for `predicates/{envelope,cel_profile,ast_walker}.py` and
   `evaluate/celrt.py`, **in the two-integer form with `E`, `I` and `T` listed** — a bare percentage fails
   the review.
6. `make determinism` green including `test_det__envelope_digest_stable` and `test_det__harvest_is_ordered`.
7. Every host function has published test vectors and a mutation score; `test_nc__X04c` refuses to load one
   that does not.
8. Three ledger rows appended; `tests/test_validation_ledger.py` green (the ledger grew since the P3 tag).

## P4.4 What it kills if it fails

- **If the both-ways check cannot be made exact** — some CEL construct in the admitted subset defeats static
  key extraction — then **the settled fraction becomes an estimate and must be relabelled as one
  everywhere**: on the report, in the API, in the attestation, in the README. The product still ships and is
  strictly weaker. The spec's headline argument for CEL over Python is gone with it, and the language
  decision re-opens **with the measurement attached** rather than on preference. The narrower repair, to be
  tried first: delete the offending construct from the admitted subset and re-measure. A smaller grammar
  with an exact guarantee beats a larger one with an estimate.
- **If neither CEL runtime is sound on error semantics**, narrow the admitted subset to ban `&&` and `||`
  **at the top level of `expr`** entirely. Conjunction then lives in the harvest (two predicates instead of
  one), the settled numerator is unaffected, and the pre-flight guard's argument no longer depends on a
  runtime behaviour we could not verify.
- **If the harvest under-produces on the other eight workbooks** — non-empty on fewer than 5 of 9 —
  G-TRANSFER (mech) fails and **the claim narrows to the workbooks where it works**, with the per-workbook
  distribution published including the zeroes. The v0 baseline says this is unlikely (7 of 9), which is
  precisely why a *drop* to fewer than 5 would be a finding about the new code rather than about the
  workbooks.
- **Nothing here can kill P5.** P5 needs the envelope format, the runtime and *some* predicates; it does
  not need 280 of them.

## P4.5 Effort

**14 engineer-days** — B1 3 · B2 4 · B3 4 · B4 3. Assumption: one competent engineer, fluent in Python,
comfortable with raw OOXML and with an AST, ~6 productive hours a day, working from this document and the
spec, no context switching. **Two risks to the estimate, both in B3:** driving the official CEL conformance
suite is the single most likely overrun (D-P4-04 caps it at 2 days by construction), and `celpy`'s AST
shape may not expose comprehension bindings cleanly, in which case B2 grows by ~1 day building a small
normalising visitor. Neither risk touches B1 or B4.

---

# P5 — L5: RUN ASSEMBLY, THE VERDICT MODEL, CLOSURE, THE SETTLED FRACTION

**13 engineer-days.** Critical path. Depends on P4; gates P6, and unlocks P9-B1 and P14-B1–B3 in parallel.

## P5.0 What it settles

The product's core object — and specifically **whether the runtime settled count falls below the static
harvest figure when a predicate does not run.** That is not a detail. Audit §V.7.1 withdrew the
`PASS ≻ NOT_RUN` ordering for exactly one reason: both parts of the spec state that on reader disagreement
every predicate reading the field returns `NOT_RUN(extractor_disagreement)` and *"the settled fraction
falls, it does not silently succeed"* — and under the withdrawn order that sentence is false in precisely
the case it was written for. **A check that did not run must never be absorbed by one that did.** P5 is
where that becomes a measured behaviour rather than a stated intention, and the phase does not exit until
`test_settled_fraction_falls_on_not_run` is green and the delta is published.

## P5.1 Entry criteria

| # | Condition | Why |
|---|---|---|
| E1 | P4 complete: envelopes load, `Predicate` is distinct from `Candidate`, `CelRuntime` compiles the admitted subset | An evaluator cannot evaluate a format that is not fixed |
| E2 | `check_declared_keys` green on the predicate set being run | Rule 2 is *exact rather than an estimate* only because of this; without it pre-flight guards the wrong keys |
| E3 | P2's field surface published per workbook, `computedTwiceAgreed` recorded | Closure's right-hand side is `fieldSurface`. Two of nine ship no mask and their runs take the `null` branch |
| E4 | A **TEMPLATE-COMPUTED clean filing** exists at `fixtures/synthetic/clean__template-computed__fme-q1__<sha8>.xlsx` — fill the input cells, let the workbook's own 505 formula cells compute the rest **via `src/cdfc/calc/`** | **No real filed FME return is public.** This is the only clean input available without the corpus lane, it needs no corpus, and it is labelled synthetic in three places per `01` §6.4. **Read E6 before using it for anything but plumbing** |
| E5 | A single-fault variant `mutant__f11-formula-override__portfolio-O7__seed<...>.xlsx` built by **raw-zip surgery**, never an openpyxl round-trip | The exit gate requires "one seeded fault ⇒ exactly the predicates reading that cell FAIL" |
| **E6** | A **HAND-COMPUTED clean filing** exists at `fixtures/synthetic/clean__hand-computed__fme-q1__<sha8>.xlsx`, built at `02` P3-B4 by `tools/fixtures/materialise_expected.py` from the G-EVAL **arm-2 human expectation file** — **its derived cells were typed by a person from the formula text and `src/cdfc/calc/` never touched them** | **This is the entry criterion the phase's headline gate depends on, and it is new.** The TEMPLATE-COMPUTED filing is produced by the very evaluator the arithmetic predicates re-check: `synthesise` fills the inputs and lets `calc/` compute the rest, and `sum_identity` / `cross_sheet_equality` / `tally_identity` then assert **exactly the identities `calc/` enforced when it wrote the file.** The oracle and the system under test are the same function. On that filing it is *arithmetically impossible* for the 227 arithmetic predicates to fire, so *"clean filing ⇒ 0 FAIL"* is `x == x` — green on a correct implementation, green on one whose tolerance is 1,000× wide, green on one that always returns `[]`. **One filing the product did not compute is enough to make the gate non-vacuous; zero is what this plan had.** It is a *fixture*, not a corpus: `CorpusProvenance` stays at six members and `qualify/corpus.py` refuses to load it as one, so no FFR can ever be computed from a single filing |

---

## P5-B1 — RUN ASSEMBLY: BINDING, SELECTION, PRE-FLIGHT · 3 days

### Files created

```
src/cdfc/evaluate/binding.py       F3 template binding by structural fingerprint
src/cdfc/evaluate/selection.py     F6 predicate selection against the pinned registry root
src/cdfc/evaluate/preflight.py     F7 the key check, before expr is evaluated at all
src/cdfc/evaluate/runner.py        F8 the loop; emits RunCheck rows
src/cdfc/store/schema.sql          run, run_check, run_cell, override, extraction_manifest
src/cdfc/store/db.py               open/create; the file IS the artifact, so it hashes
docs/decisions/D-P5-01-binding-precedes-evaluation.md
docs/decisions/D-P5-03-preflight-type-inference.md
```

### Public interface

```python
# src/cdfc/evaluate/binding.py
@dataclass(frozen=True, slots=True) class Bound:   template_sha256: str; schema: TemplateSchema
@dataclass(frozen=True, slots=True) class Unbound: fingerprint: str; nearest: tuple[tuple[str, int], ...]
def bind_template(raw: RawWorkbook, catalogue: TemplateCatalogue) -> Bound | Unbound
# Unbound ESCALATES: run_state = INVALID(invalid.template_unbound) AND every cell carries
# NOT_RUN(not_run.template_unbound). Both vocabularies, not one -- audit V.7.3.
# Formula content is NOT in the fingerprint: a filer who overwrote a formula with a literal must fail a
# PREDICATE, not the BINDING.

# src/cdfc/evaluate/selection.py
@dataclass(frozen=True, slots=True)
class Selection:
    active: tuple[Predicate, ...]
    provisional: tuple[Predicate, ...]      # STILL RUN. Numbers hidden. NOT in the settled numerator
    not_requalified: tuple[str, ...]        # cells -> NO_PREDICATE(no_predicate.not_yet_requalified)
    deactivated: tuple[tuple[str, str], ...]   # (predicate_id, decision_record_uri)
    registry_root: str
def select(registry_root: str, template_sha256: str, profile: RunProfile) -> Selection

@dataclass(frozen=True, slots=True)
class RunProfile:
    name: str; digest: str
    exclude: tuple[str, ...] = ()
    spike: bool = False        # P9-B1's non-admitted TEMPLATE_DIFF demonstration runs under this flag;
                               # a spike run may not write `settled` for any cell (05 owns the test)

# src/cdfc/evaluate/preflight.py
@dataclass(frozen=True, slots=True)
class PreflightResult:
    proceed: bool
    missing: tuple[str, ...]; mistyped: tuple[tuple[str, str, str], ...]   # (key, expected, actual)
    keys_checked: int; keys_type_checked: int                              # D-P5-03
def preflight(p: Predicate, facts: FactTable) -> PreflightResult

# src/cdfc/evaluate/runner.py
def bind_count(p: Predicate, facts: FactTable, schema: TemplateSchema) -> int   # D-P5-01: BEFORE expr
def evaluate_one(p: Predicate, facts: FactTable, rt: CelRuntime) -> RunCheck
def evaluate_all(sel: Selection, facts: FactTable, rt: CelRuntime) -> tuple[RunCheck, ...]
```

**`evaluate_one` accepts `Predicate` and nothing else.** A `Candidate` is a type error at the call site.
That is barrier 3 in the type system; `test_unmeasured_predicate_rejected` is barrier 3 at runtime; both
are kept.

**Why pre-flight is structural and not defensive**, restated because it is the one paragraph an engineer
must not simplify away: the CEL specification states that for `||` and `&&`, if one operand determines the
result, a runtime error in the other *"will be ignored."* So `true || <error>` is `true`, and an unguarded
predicate returns `PASS` while silently swallowing an operand that could not be evaluated at all — **the
exact defect this product exists to prevent, manufactured by the language.** Pre-flighting every declared
key *before* `expr` is evaluated makes the guard independent of how the predicate was written. It is exact
rather than an estimate because P4-B2 machine-checked `schema_keys` against the AST both ways.

### Functionality validation

**Unit** — `tests/unit/test_preflight.py`, `tests/unit/test_selection.py`, `tests/unit/test_binding.py`
- `test_preflight__missing_key_blocks_expr` — asserts, with a spy on `CelRuntime.evaluate`, that the
  program was **never evaluated**.
- `test_preflight__ambiguous_type_is_presence_checked_and_recorded` — D-P5-03; the result carries
  `keys_type_checked < keys_checked` and the run reports both.
- `test_selection__provisional_runs_but_does_not_settle` — a `PROVISIONAL` predicate appears in
  `run_check` with its state, and its cells do **not** enter `settled`.
- `test_selection__foreign_template_predicate_is_not_evaluated` — its cells land in
  `NO_PREDICATE(no_predicate.not_yet_requalified)`.
- `test_selection__empty_active_set_is_not_an_error` — an honest report with `settled.total == 0`, run
  state `VALID`. The positive control that stops the selector being a reject-everything baseline.
- `test_binding__formula_content_is_not_in_the_fingerprint` — overwrite a formula cell with its own cached
  value; the workbook still **binds**, and the defect surfaces later as a predicate failure.
- `test_binding__unbound_sets_both_vocabularies` — `invalid.template_unbound` at the run level **and**
  `not_run.template_unbound` at the item level. Audit §V.7.3: they are not alternatives.

**Property** — `tests/property/test_prop_preflight.py`
- `test_prop__preflight_set_equals_declared_keys` — *property:* the set of keys pre-flighted equals
  `p.schema_keys` exactly, for any predicate that passes `check_declared_keys`. *Generator:* random
  admitted expressions with their derived declarations. This is the statement "exact, not an estimate", as
  a test.

**Negative controls** — **NC-E02** (a and b; b is `01`'s named exemplar: under `preflight_disabled` the same
predicate returns `PASS`), **NC-Q01** (zero bind), and new **NC-E20** (`cells_bound` computed after `expr`,
so the vacuous pass is produced and then corrected).

**Performance** — `PERF-EV` (evaluation of 280 predicates; baseline sub-ms for the 227 arithmetic ones;
fail above 10 ms, warn above 5 ms). Pre-flight and binding are inside this budget.

---

## P5-B2 — THE EVALUATION CONTRACT, GENERATED · 2 days

### Files created

```
src/cdfc/evaluate/contract.py                 THE single source of truth: TRANSITIONS + COMPOSITION
tools/gen_contract.py                         renders contract.py -> EVALUATION-CONTRACT.md
EVALUATION-CONTRACT.md                        GENERATED. Never hand-edited
tests/contract/expected/spec_II_3_4_transitions.json    the spec's table, extracted once, pinned
```

### The single-source-of-truth decision

The decomposition says `EVALUATION-CONTRACT.md` is *generated from the five rules of spec §II.3.4* and a CI
test asserts the evaluator's transition table equals the file. **Taken literally that means parsing prose in
CI, and a gate that goes red because a paragraph reflowed is a gate that gets disabled.** The decided
arrangement is three-way and each edge is checked in a different way:

```
src/cdfc/evaluate/contract.py::TRANSITIONS      <- the source of truth; the evaluator imports it
        |  tools/gen_contract.py (byte-identity)          |  one-time extraction, pinned
        v                                                  v
EVALUATION-CONTRACT.md                          tests/contract/expected/spec_II_3_4_transitions.json
```

- code → doc: `test_nc__E03b_contract_is_generated_not_edited` regenerates and asserts byte-identity, so a
  hand edit to the markdown fails the build.
- code → spec: `test_contract__evaluation_contract_matches_evaluator` compares `TRANSITIONS` **set-equal**
  to the pinned extraction. The extraction moves only with a decision record — which is exactly how the
  spec's own five rules should move, since three different versions of them were live at once and *a build
  cannot satisfy two fives.*

### Public interface

```python
# src/cdfc/evaluate/contract.py
class RunStateEffect(StrEnum): UNCHANGED = "UNCHANGED"; INVALID = "INVALID"

@dataclass(frozen=True, slots=True)
class Transition:
    order: int            # EVALUATION ORDER -- D-P5-01; distinct from `rule`
    rule: int             # the spec's conceptual rule number, 1..5
    trigger: str
    state: ItemState | None          # None == "continue"
    reason: ReasonCode | None
    run_state_effect: RunStateEffect
    never: tuple[ItemState, ...]     # the spec's "[never FAIL]" annotations, as assertions

TRANSITIONS: Final[tuple[Transition, ...]]      # exactly 9 rows
def compose_warrant(facts: Iterable[Fact]) -> Warrant       # min under DETERMINISTIC > MODEL_EXTRACTED > DERIVED
def compose_retrieved_at(facts: Iterable[Fact]) -> datetime # max
```

The nine rows, in **evaluation order**:

| order | rule | trigger | state | reason | run | never |
|---:|---:|---|---|---|---|---|
| 1 | 1 | `applicable` errors | `NOT_RUN` | `not_run.source_unreadable` | unchanged | FAIL |
| 2 | 1 | `applicable` false | `OUT_OF_SCOPE` | `p.reason_if_inapplicable ∈ out_of_scope.*` | unchanged | PASS, FAIL |
| 3 | 1 | `applicable` true | — (continue) | — | unchanged | — |
| 4 | 5 | `cells_bound == 0` | `ERROR` | `error.cells_bound_zero` | **INVALID** | PASS, NOT_RUN |
| 5 | 2 | declared key absent or mistyped | `NOT_RUN` | `not_run.source_unreadable: <k>` | unchanged | PASS, FAIL |
| 6 | 3 | `expr` budget exceeded | `NOT_RUN` | `not_run.budget_exhausted` | unchanged | FAIL |
| 7 | 3 | `expr` runtime error | `ERROR` | `error.predicate_raised` | **INVALID** | NOT_RUN, PASS, FAIL |
| 8 | 3 | `expr` false | `FAIL` (then evaluate `witness`) | — | unchanged | — |
| 9 | 3 | `expr` true | `PASS` | — | unchanged | — |

Rule 4 is not a transition; it is `compose_warrant` / `compose_retrieved_at`, and the CI equality test
covers both sections. **A verdict is never fresher than its stalest input and never stronger than its
weakest.**

**Note rows 4 and 7 against each other.** A predicate that *raised* is an apparatus failure — fix the code.
A source that could not be read is `not_run.source_unreadable` — retry. **They have opposite remedies**, and
collapsing them is NC-E01. Row 4 sits at order 4, before pre-flight and before `expr`, per D-P5-01.

### Functionality validation

**Contract** — `test_contract__evaluation_contract_matches_evaluator`,
`test_contract__transitions_has_exactly_nine_rows`,
`test_contract__every_transition_declares_its_never_set`, and
`test_contract__never_sets_are_enforced_at_runtime` — a fuzz over triggers asserting the realised state is
never in the row's `never` tuple. That last one turns the spec's bracketed comments into an executable
guarantee.

**Property** — `tests/property/test_prop_contract.py::test_prop__warrant_composes_by_weakest_input` —
*property:* `compose_warrant` is the minimum under the stated lattice and is associative and commutative.
*Generator:* random multisets of the three warrant values, including the empty set (which must **raise**,
not return `DETERMINISTIC` — an empty read set means `cells_bound == 0`, and row 4 already owns it).

**Negative controls** — **NC-E03** (the evaluator drifts from the contract), including
`injectors/contract_table_edit.py` changing one cell of the generated table.

---

## P5-B3 — THE STATE AND REASON VOCABULARY, AND THE RUN-LEVEL VOCABULARY THAT IS SEPARATE FROM IT · 2 days

### Files created

```
src/cdfc/verdict/__init__.py
src/cdfc/verdict/states.py       8 item states, the 7-member precedence tuple, and REMOVAL_BASIS --
                                 the (state, reason) -> basis table that IS the denominator policy
src/cdfc/verdict/reasons.py      30 codes, five families, the discipline rule  (C3: NO 31st code;
                                 the degenerate-precondition case is scope_kind, not a code)
src/cdfc/verdict/invalid.py      the 8 run-level causes -- a SEPARATE closed vocabulary
docs/decisions/D-P5-02-informational-carries-no-reason.md
```

### Public interface

```python
# src/cdfc/verdict/states.py
class ItemState(StrEnum):
    PASS = "PASS"; FAIL = "FAIL"; INDETERMINATE = "INDETERMINATE"; NOT_RUN = "NOT_RUN"
    NO_PREDICATE = "NO_PREDICATE"; ERROR = "ERROR"; OUT_OF_SCOPE = "OUT_OF_SCOPE"
    INFORMATIONAL = "INFORMATIONAL"

PRECEDENCE: Final[tuple[ItemState, ...]] = (
    ItemState.ERROR, ItemState.FAIL, ItemState.INDETERMINATE, ItemState.NOT_RUN,
    ItemState.PASS, ItemState.INFORMATIONAL, ItemState.OUT_OF_SCOPE)     # audit V.7.1, binding
# NO_PREDICATE is deliberately NOT in PRECEDENCE: it is the state of a cell whose evaluation set is empty.

SETTLED:        Final[frozenset[ItemState]] = {PASS, FAIL}
ERROR_STATES:   Final[frozenset[ItemState]] = {ERROR}      # any ERROR sets run_state = INVALID

# DENOMINATOR MEMBERSHIP IS A FUNCTION OF (state, reason, scope_kind), NOT OF state ALONE.  D-P5-05.
# ARBITRATION C3: scope_kind is plan/05's field, WRITTEN by applicable() in probes/relations and READ here.
# NO 31st REASON CODE.  The vocabulary stays at 30.

# scope_kind, imported -- NOT redefined here.  Its home is plan/05 P9-B1 (src/cdfc/probes/relations.py).
ScopeKind = Literal["IN_SCOPE", "DECLARED_CHARACTERISTIC", "PREDICATE_PRECONDITION"]
#   DECLARED_CHARACTERISTIC -> out of scope because of a declared filer/period attribute or a fact about
#                              the pinned template.  A statement about the INSTRUMENT or the FILER.
#   PREDICATE_PRECONDITION  -> out of scope because THIS PREDICATE's own `applicable` precondition was
#                              degenerate on THIS FILING.  A statement about the PREDICATE.
# REQUIRED whenever state == OUT_OF_SCOPE and reason == OOS_NOT_APPLICABLE.  Absent => raises.

class RemovalBasis(StrEnum):
    TEMPLATE = "TEMPLATE"                              # a fact about the pinned blank
    SELECTION = "SELECTION"                            # a fact about which predicates were selected
    DECLARED_CHARACTERISTIC = "DECLARED_CHARACTERISTIC" # a declared filer/period attribute

REMOVAL_BASIS: Final[Mapping[tuple[ItemState, ReasonCode], RemovalBasis]] = {
    (OUT_OF_SCOPE, OOS_NOT_APPLICABLE): DECLARED_CHARACTERISTIC,   # <- CONDITIONAL on scope_kind, below
    (OUT_OF_SCOPE, OOS_NOT_SELECTED):   SELECTION,
    (OUT_OF_SCOPE, OOS_WITHHELD):       SELECTION,
    (INFORMATIONAL, None):              TEMPLATE,
}
# ANY (state, reason) PAIR ABSENT FROM THIS TABLE STAYS IN inScope. The default is to count, never to
# remove.

# THE RETENTION RULE (arbitration C3), and it is the whole of the F13 repair:
#   ONLY scope_kind == DECLARED_CHARACTERISTIC LEAVES THE IN-SCOPE DENOMINATOR.
#   scope_kind == PREDICATE_PRECONDITION STAYS IN THE DENOMINATOR and is additionally flagged for G3
#   re-qualification (see requalification_flag(), below).

def in_scope(state: ItemState, reason: ReasonCode | None,
             scope_kind: ScopeKind | None = None) -> bool:
    if (state, reason) not in REMOVAL_BASIS:
        return True
    if (state, reason) == (OUT_OF_SCOPE, OOS_NOT_APPLICABLE):
        if scope_kind is None:
            raise MissingScopeKindError(state, reason)   # fail closed; never guess the denominator
        return scope_kind != "DECLARED_CHARACTERISTIC"   # PREDICATE_PRECONDITION is RETAINED
    return False

def requalification_flag(scope_kind: ScopeKind | None) -> bool:
    # A degenerate `applicable` is exactly what G3 exists to reject, so a cell retained for
    # PREDICATE_PRECONDITION does not merely stay counted -- it accuses its own predicate.
    return scope_kind == "PREDICATE_PRECONDITION"

# src/cdfc/verdict/reasons.py
class ReasonCode(StrEnum):     # exactly 30, namespaced, five families.  C3: NO 31st CODE.
    NP_UNDECIDABLE_BY_CONSTRUCTION = "no_predicate.undecidable_by_construction"
    NP_REQUIRES_JUDGMENT           = "no_predicate.requires_judgment"
    NP_NOT_YET_SYNTHESISED         = "no_predicate.not_yet_synthesised"
    NP_FAILED_QUALIFICATION        = "no_predicate.failed_qualification"
    NP_RULE_AMBIGUOUS              = "no_predicate.rule_ambiguous"
    NP_NO_OBLIGATION_SPECIFIED     = "no_predicate.no_obligation_specified"
    NP_RULE_WITHDRAWN              = "no_predicate.rule_withdrawn"
    NP_NOT_YET_REQUALIFIED         = "no_predicate.not_yet_requalified"          # 8
    NR_INPUT_UNAVAILABLE_COUNTERPARTY = "not_run.input_unavailable.counterparty"
    NR_INPUT_UNAVAILABLE_REGISTER     = "not_run.input_unavailable.register"
    NR_INPUT_UNAVAILABLE_PRIOR_PERIOD = "not_run.input_unavailable.prior_period"
    NR_SOURCE_UNREADABLE           = "not_run.source_unreadable"
    NR_TEMPLATE_UNBOUND            = "not_run.template_unbound"
    NR_DEACTIVATED                 = "not_run.deactivated"
    NR_BUDGET_EXHAUSTED            = "not_run.budget_exhausted"
    NR_EXTERNAL_SOURCE_LACKS_FIELD = "not_run.external_source_lacks_field"
    NR_EXTERNAL_SOURCE_UNAVAILABLE = "not_run.external_source_unavailable"
    NR_EXTRACTOR_DISAGREEMENT      = "not_run.extractor_disagreement"            # 10
    IND_EXTRACTION_ABSTAINED = "indeterminate.extraction_abstained"
    IND_TOLERANCE_STRADDLE   = "indeterminate.tolerance_straddle"
    IND_CONFLICTING_SOURCES  = "indeterminate.conflicting_sources"
    IND_ENGINE_DISAGREEMENT  = "indeterminate.engine_disagreement"               # 4
    OOS_NOT_APPLICABLE = "out_of_scope.not_applicable"                           # carries scope_kind
    OOS_NOT_SELECTED   = "out_of_scope.not_selected"
    OOS_WITHHELD       = "out_of_scope.withheld"                                 # 3
    # C3: there is NO out_of_scope.precondition_degenerate. The distinction it carried -- "the check could
    # not be ATTEMPTED because the filing carries too few values", as against "the obligation does not
    # apply to you" -- is carried by scope_kind == PREDICATE_PRECONDITION on OOS_NOT_APPLICABLE instead.
    ERR_PREDICATE_RAISED = "error.predicate_raised"
    ERR_CELLS_BOUND_ZERO = "error.cells_bound_zero"
    ERR_CANARY_SILENT    = "error.canary_silent"
    ERR_CLOSURE_VIOLATED = "error.closure_violated"
    ERR_PARSER_DISAGREEMENT_STRUCTURAL = "error.parser_disagreement_structural"  # 5   == 30

FAMILY: Final[Mapping[ReasonCode, ItemState]]
NO_REASON_STATES: Final[frozenset[ItemState]] = {PASS, FAIL, INFORMATIONAL}      # D-P5-02
def reason_required(state: ItemState) -> bool
def validate_pair(state: ItemState, reason: ReasonCode | None, note: str | None) -> None  # raises ReasonDisciplineError

# src/cdfc/verdict/invalid.py
class InvalidCause(StrEnum):      # exactly 8. A SEPARATE vocabulary. Audit V.7.3
    CONTAINER_GUARD_TRIPPED       = "invalid.container_guard_tripped"
    READER_STRUCTURAL_DISAGREEMENT= "invalid.reader_structural_disagreement"
    TEMPLATE_UNBOUND              = "invalid.template_unbound"
    CELLS_BOUND_ZERO              = "invalid.cells_bound_zero"
    PREDICATE_RAISED              = "invalid.predicate_raised"
    CANARY_SILENT                 = "invalid.canary_silent"
    CLOSURE_VIOLATED              = "invalid.closure_violated"
    DENOMINATOR_DISAGREEMENT      = "invalid.denominator_disagreement"

ITEM_ANALOGUE: Final[Mapping[InvalidCause, ReasonCode | None]]   # both are carried; they are not alternatives
```

**There is no 31st code. `scope_kind` is read instead — arbitration C3.** This build previously proposed
`out_of_scope.precondition_degenerate` as a 31st reason code, on the argument that *two reasons are distinct
iff they imply different remedies*, and the two remedies are genuinely different:
`out_of_scope.not_applicable` with `scope_kind = DECLARED_CHARACTERISTIC` implies **no remedy, this
obligation does not apply to you**; the degenerate case implies **fill in the filing; the check could not be
attempted because the values it partitions are absent.** The distinction is real and it survives — **but it
is carried by a field, not by a code.**

**Why the field and not the code.** A 31st reason code **breaks a count pinned in four places**
(`00` §5 P5, `07` P14 entry, `06` §5, `09` §10) — the same category error already ruled on for the container
guard, where run-level causes became **their own vocabulary** rather than a 31st item-level code. `plan/05`
owns the relation that emits the determination and already writes `scope_kind`; **this document's job is to
READ it.** A field one document writes and another ignores is not a repair, and that is precisely why F13's
mechanism survived its own first fix: `03` keyed retention on a new code, `05` keyed it on a new field
attached to the old code, and composing the two as written sent a degenerate-input cell straight out of the
denominator — F13's exact mechanism, restored by the two repairs that were supposed to close it.

**The pinned item-level count therefore stays at `8 × 30`, unchanged, in all four places**, with
`docs/decisions/D-P5-05-inscope-removals-are-value-independent.md` carrying the argument, the date, and the
record that the 31st-code option was raised and **rejected under C3**.

**Why two vocabularies.** A container guard trip, a reader disagreement on sheet structure, an unbound
template and a denominator disagreement **are not properties of any cell.** Forcing them into a per-cell
reason code was the error, not the missing code — that is the audit's category correction, and it is why
the item-level count stays pinned at **8 × 30** in all four places while a ninth run-level object exists
beside it. Where a cause has an item-level analogue (`cells_bound_zero`, `predicate_raised`), **both are
written**; a report that carries one and not the other has lost either the location or the run-level
consequence.

### Functionality validation

**Contract** — the vocabulary tests `01` §1.9 requires, realised here:
`test_contract__eight_item_states`, `test_contract__thirty_reason_codes` (**30**, namespaced, five
families, and `FAMILY` total over the five states — **C3: the count does not move**),
`test_contract__eight_invalid_causes`,
`test_contract__invalid_causes_and_reason_codes_are_disjoint` (no shared member, no shared string),
`test_contract__reason_code_required_iff_state_not_pass_fail_or_informational` — **exhaustive over the
8 × 31 product** (30 codes plus `None`), with the `INFORMATIONAL` row asserting
`reason is None and informational_note is not None` per D-P5-02.
**`test_contract__removal_basis_is_total_and_closed`** (D-P5-05, restated under **C3**) — every key of
`REMOVAL_BASIS` is a legal `(state, reason)` pair; `in_scope()` is total over the
**8 × 31 × |ScopeKind ∪ {None}|** product; and the retention rule is asserted directly:
**`(OUT_OF_SCOPE, OOS_NOT_APPLICABLE)` removes a cell iff `scope_kind == DECLARED_CHARACTERISTIC`**, while
`scope_kind == PREDICATE_PRECONDITION` is **retained**, and a missing `scope_kind` on that pair
**raises `MissingScopeKindError` rather than defaulting either way**. *The table plus the retention rule is
the whole of the removal policy; a second place that removes a cell from the denominator is a defect this
test cannot see, which is why `partition()` consults `in_scope()` and nothing else.*
**`test_contract__scope_kind_is_read_not_ignored`** (new, **C3**) — an AST scan asserting
`settled_fraction.py` and `closure.py` reach `scope_kind` on every `OOS_NOT_APPLICABLE` path. *A field one
document writes and another ignores is the defect C3 exists to close, and it is invisible to every
behavioural test that never builds a `PREDICATE_PRECONDITION` record.*

**Property** — `tests/property/test_prop_reasons.py::test_prop__reason_discipline_is_total` — *property:*
`validate_pair` either accepts or raises for every one of the 8 × 31 pairs; there is no third outcome and
no pair it silently tolerates. *Generator:* the full product, enumerated.

**Negative controls** — **NC-E06** (reason-code discipline inverts) and new **NC-E23** (a run-level
`invalid.*` cause written into an item's reason field). NC-E23's positive control: a guard trip produces
exactly one run-level cause and **zero** per-cell reasons.

---

## P5-B4 — ROLL-UP, CLOSURE, AND THE SETTLED-FRACTION OBJECT · 5 days

**The phase's centre of gravity.**

### Files created

```
src/cdfc/evaluate/rollup.py            precedence max; NO_PREDICATE for an empty evaluation set
src/cdfc/verdict/closure.py            the seven-term invariant; ABORTS the report on a hole
src/cdfc/verdict/settled_fraction.py   the object of spec §III.4.3, never a bare fraction
src/cdfc/verdict/aggregate.py          the 2x2, withheld while K and T are PLACEHOLDER
src/cdfc/cli.py                        `cdfc run`, `cdfc closure explain`
tools/fixtures/value_deletion.py       the value-deletion transform generator. BUILT HERE, imported by
                                       P9-B2's precondition-monotonicity property (D-P5-05)
tests/property/test_prop_settled_fraction.py
docs/decisions/D-P5-04-two-nulls.md
docs/decisions/D-P5-05-inscope-removals-are-value-independent.md
docs/decisions/D-P5-06-invalid-carries-a-null.md
```

### Public interface

```python
# src/cdfc/evaluate/rollup.py
@dataclass(frozen=True, slots=True)
class Evaluation: predicate_id: str; version: int; state: ItemState; reason: ReasonCode | None; witness: tuple[str, ...]
@dataclass(frozen=True, slots=True)
class RunCell: stable_key: str; state: ItemState; reason: ReasonCode | None; settled_by: str | None; evaluations: tuple[Evaluation, ...]

def roll_up(evals: Sequence[Evaluation]) -> tuple[ItemState, ReasonCode | None, str | None]
    # empty -> (NO_PREDICATE, no_predicate.not_yet_synthesised, None)
    # else  -> max over PRECEDENCE.  A CELL IS CLEAN ONLY IF EVERY PREDICATE BINDING IT PASSED.
    # EXCEPT, D-P5-05/F14: if EVERY evaluation in the set is INFORMATIONAL, the cell rolls up to
    #   (NO_PREDICATE, no_predicate.rule_ambiguous, None) -- which STAYS in inScope -- and never to
    #   INFORMATIONAL, which would leave it. A cell we have no verdict on is a gap in US.

def materialise(schema: TemplateSchema) -> dict[str, RunCell]
    # EVERY field-surface cell, BEFORE evaluation, defaulting to NO_PREDICATE(not_yet_synthesised).
    # This is the structural reason closure cannot have a hole: the table is built from the denominator,
    # never accumulated from the evaluations.

def roll_up_run(cells: dict[str, RunCell], checks: Sequence[RunCheck]) -> tuple[RunCell, ...]

# src/cdfc/verdict/closure.py
@dataclass(frozen=True, slots=True)
class ClosurePartition:
    outOfScope: int; informational: int; settled: int; indeterminate: int
    notRun: int; noPredicate: int; error: int; cellsTotal: int
    outOfScopeRetained: int          # D-P5-05: OUT_OF_SCOPE cells that STAY in inScope
    informationalRetained: int       # D-P5-05: INFORMATIONAL cells that STAY in inScope
    @property
    def total(self) -> int           # the SEVEN terms, still summing to cellsTotal. Unchanged.
    @property
    def inScope(self) -> int:
        return (self.cellsTotal
                - (self.outOfScope - self.outOfScopeRetained)
                - (self.informational - self.informationalRetained))
class ClosureViolation(Exception): missing: tuple[str, ...]; sums: Mapping[str, int]

CLOSURE_SQL: Final[str]                       # the one GROUP BY over run_cell
def partition(cells: Sequence[RunCell], field_surface: int) -> ClosurePartition
def assert_closed(p: ClosurePartition) -> None    # raises ClosureViolation -> invalid.closure_violated
                                                  # -> REPORT GENERATION ABORTS. There is no degraded report.

# src/cdfc/verdict/settled_fraction.py
@dataclass(frozen=True, slots=True)
class SettledFraction:
    denominator: Denominator                  # source, generatorRule, fieldSurface, computedTwiceAgreed,
                                              # validationState (plan/02 P2-B2: PROVISIONAL-UNVALIDATED
                                              # until P8-B1's filler check). All FIVE render together.
    cellsTotal: int                           # ALWAYS rendered beside inScope (D-P5-05)
    outOfScope: int; outOfScopeRetained: int   # retained := stayed in inScope (basis would be filing values)
    informational: int; informationalRetained: int
    inScope: int                              # cellsTotal - (outOfScope - retained) - (informational - retained)
    settled: SettledCounts                    # pass, fail, total
    unsettled: UnsettledCounts                # indeterminate, notRun, noPredicate, error
    fraction: Decimal                         # quantize("0.0001"), ROUND_HALF_UP. No float, ever
    admissionState: Literal["PRE-GATE", "POST-GATE"]      # computed from the selection, never hand-set
    admissibilityCaveat: str                  # required and non-empty while admissionState == PRE-GATE
    denominatorWarning: str                   # required
    declaredGaps: tuple[DeclaredGap, ...]
    residue: Residue | None                   # populated by P10; null here

def compute(part: ClosurePartition, sel: Selection, den: Denominator, run_state: RunState) -> SettledFraction | None
    # returns None -- i.e. `settledFraction: null` -- and NEVER a zero, when:
    #   run_state == INVALID  |  den.field_surface is None (template ships no mask)  |  a canary was silent (P10)
    # D-P5-06: `None` here means the SERIALISER EMITS THE KEY WITH A JSON null. It never omits it.

def static_settled_cells(schema, candidates) -> frozenset[str]   # cells reachable by >=1 harvested predicate
def runtime_settled_cells(cells: Sequence[RunCell]) -> frozenset[str]   # rolled-up state in {PASS, FAIL}

def fraction_of(part: ClosurePartition) -> Decimal               # settled.total / part.inScope
def assert_fraction_did_not_rise(before: SettledFraction, after: SettledFraction) -> None
    """Raises FractionRoseError. The one function that expresses D-P5-05's claim as an assertion,
       so the property test, the defect-table guard (P9) and the empty-filing control all call it
       rather than each re-deriving the comparison."""
```

#### **D-P5-05 — the settled fraction may not rise as the filing carries less information**

**The hole, stated as arithmetic.** `inScope = cellsTotal − outOfScope − informational`, and **both
subtrahends are reachable by making the filing worse.** NC-R01 correctly requires a partition relation to
return `OUT_OF_SCOPE`, never `PASS`, on an all-zero filing — so the plan's defence against the empty-filing
attack is *a mechanism that shrinks the denominator*. Take any filing and delete values from it: cells whose
only binding evaluation was such a relation move `NO_PREDICATE → OUT_OF_SCOPE` and **leave `inScope`**,
while cells still settled by membership or bound predicates stay. `settled / inScope` **rises.** There is a
filing shape — sparse but lawful, exactly the shape `05` §0.3 built `CANARY_INAPPLICABLE_CEILING` for — **on
which a filer who fills in less gets a better settled fraction.** The same arithmetic runs through
`INFORMATIONAL`: `05` writes that a template defect *"can neither fail a filer nor inflate our coverage"*,
and the first clause is right while the second is **wrong for the case that matters** — for a cell whose
only binding evaluation is a declared-defective `TEMPLATE_DIFF`, the cell moves `NO_PREDICATE`
(in `inScope`, unsettled) → `INFORMATIONAL` (out of `inScope`), so `s/(i−1) > s/i` and **adding a row to
`template_defects.yaml` raises the headline.** The table is append-only with an evidence command, which
stops fabricated defects and not *convenient true* ones.

The plan has `test_prop__settled_is_monotone_non_increasing_in_not_run` — the same statement for **one**
state transition. Every property in `01` §1.2 is about closure **balancing**; **none is about the
fraction's direction**, and the direction is the product's headline claim.

> **The ruling (DECIDED).** **A cell may leave `inScope` only for a reason that is a function of the
> template, the selection, or a declared filer/period characteristic — never a function of the filing's
> cell values.** Four mechanisms, all in `states.py` and `closure.py` and nowhere else:
>
> 1. **`REMOVAL_BASIS`** (P5-B3) plus **the `scope_kind` retention rule** is the *whole* removal policy.
>    The table is keyed by `(state, reason)` with `RemovalBasis ∈ {TEMPLATE, SELECTION,
>    DECLARED_CHARACTERISTIC}`; **a pair absent from the table stays in `inScope`; the default is to count.**
> 2. **`scope_kind`, `plan/05`'s field on the existing `out_of_scope.not_applicable` code — READ HERE**
>    (arbitration **C3**; there is **no 31st reason code**, and the vocabulary stays at 30). The rule:
>
>    > **Only `scope_kind == DECLARED_CHARACTERISTIC` leaves the in-scope denominator.**
>    > **`scope_kind == PREDICATE_PRECONDITION` stays in the denominator** and is **additionally flagged for
>    > G3 re-qualification**.
>
>    *Why.* A predicate whose `applicable` is degenerate is not telling you something about the filing. It is
>    telling you something about **the predicate** — and a degenerate precondition is exactly what G3 exists
>    to reject. Letting it remove a cell from the denominator lets a bad predicate shrink the thing it is
>    measured against. Under this rule the empty-filing attack closes: **nothing a predicate does to itself
>    can make the settled fraction rise.**
> 3. **`outOfScopeRetained` / `informationalRetained`** as sub-counts, so **the seven-term closure over
>    `cellsTotal` is untouched** — `test_prop__closure_seven_terms` still holds verbatim — while `inScope`
>    stops being `cellsTotal − outOfScope − informational`. *This is a change to spec §3.3's formula and it
>    is stated as one, in `docs/decisions/D-P5-05-…`, with the arithmetic that forced it.*
> 4. **An `INFORMATIONAL`-only cell rolls up to `NO_PREDICATE(no_predicate.rule_ambiguous)`**, so a
>    `template_defects.yaml` row can never move a cell out of the denominator (F14's repair, applied at the
>    roll-up rather than at the defect table, because the defect table is `05`'s and the roll-up is ours).
>
> **The property, formally, and it is the enforcer:**
>
> > **`tests/property/test_prop_settled_fraction.py::test_prop__fraction_does_not_rise_as_the_filing_empties`**
> > — for every filing `F` over a template with a derivable mask, and every **value-deletion transform**
> > `d` — a transform that replaces the value of one or more field-surface cells with an empty cell and
> > changes nothing else — **`fraction(run(d(F))) ≤ fraction(run(F))`**, where
> > `fraction = settled.total / inScope`.
> > **Generator: `tools/fixtures/value_deletion.py::deletions(reference_fill, seed)`** — single-cell
> > deletions over every field-surface cell of the FME reference fill that carries a value; random
> > `k`-subsets for `k ∈ [1, 200]`; and both extremes (delete nothing; delete everything, which is NC-R01's
> > all-zero filing). Hypothesis-driven, seeded, shrinking on the deleted-cell set so a counterexample
> > reports the **smallest** set of deletions that raised the fraction.
>
> **The generator is built here, at P5-B4, not at P9-B2** — `05` specifies the same value-deletion
> transforms for its precondition-monotonicity property, and P9-B2 imports
> `tools/fixtures/value_deletion.py` rather than writing a second one. *A property about the fraction
> cannot wait for the phase after the fraction ships.* Obligation **X7**.
>
> **The pre-committed fallback, because the adversary's prediction is that the property will fail on first
> run.** If it still fails after 1–4, **`inScope` is frozen to `cellsTotal`** — no removals at all — and
> every surface prints `outOfScope` and `informational` beside the fraction. That penalises a filer for
> genuinely inapplicable obligations, which is the **safe** direction, and it is stated on the surface.
> The decision rule is written down now so that the branch is not taken under deadline pressure by whoever
> is looking at a red test.
>
> **And regardless of the outcome, `inScope` and `cellsTotal` render side by side, always.**
> `test_contract__fraction_renders_inscope_and_cellstotal_together` — a shrinking denominator must be
> visible on the page, not merely correct in the object. *This is adopted **in addition** to the ruling,
> not as an alternative to it: the alternative — leave the removals alone and just show both numbers — was
> rejected because a visible non-monotonicity is still a non-monotonicity, and the headline fraction would
> remain gameable by emptying a filing.*
>
> **Companion guard, for `05`'s table:** `test_defect_table_cannot_raise_the_settled_fraction` — for every
> entry added to `template_defects.yaml`, recompute the reference run and call
> `assert_fraction_did_not_rise`. It lives in `05` and calls **our** function; obligation **X8** also
> requires `05` to correct the sentence *"…nor inflate our coverage"*, which is false as written.

**Four rules the object enforces that a reader should be able to check by eye.**

1. **`fraction` may never be serialised without its counts.** It is a field of the object and the object
   is the only serialisation; `test_contract__fraction_never_serialised_alone` asserts that no encoder
   emits it standalone, and the API contract (P14) repeats the prohibition. **The count set now includes
   `cellsTotal` and `inScope` together, plus `outOfScopeRetained` and `informationalRetained`**
   (D-P5-05), and `denominator.generatorRule` and `denominator.validationState` beside them
   (`02` P2-B2), so that a reader can see *which rule produced the denominator, whether anything outside
   this repository has ever checked it, and whether it shrank.*
2. **`admissionState` is computed**, from whether every predicate in `Selection.active` carries a `g4`
   record. Today that is `PRE-GATE` for all 280, and the caveat text is the spec's, verbatim. A1's
   mechanised form (NC-A05) then requires `PRE-GATE` to share an ancestor element with the count, which is
   P14's test — but the field it reads is created here.
3. **`null` is not zero and not omitted.** Three distinct outcomes, three distinct meanings, enforced by
   schema. NC-E22. **And on an `INVALID` run the field is PRESENT and `null` — never absent** (D-P5-06).
   Three documents asserted three different things about the same field in the same state: this build
   returned `SettledFraction | None`, `05` P11-B1's `test_contract__invalid_run_carries_no_fraction`
   asserted the schema **forbids** the property, and `01` §1.9 rules that **an omitted field is a schema
   violation**. `null`, `forbidden` and `omitted` are three different things; P5 and P11 each pass their
   own contract test and the integration produces an attestation that either fails validation or drops the
   `null` that `E2E-INVALID` exists to assert. **One rule, stated once: present and `null`.** The `if/then`
   becomes `{"if": {"runState": "INVALID"}, "then": {"required": ["settledFraction"], "properties":
   {"settledFraction": {"const": null}}}}`, and this build's serialiser may not omit the key.
   `tests/contract/test_contract__invalid_carries_a_null_not_an_absence` — assert the key is in the emitted
   JSON object, that its value is `null`, and that `json.loads(...)` round-trips with the key present.
   `05`'s wording must change from *forbids* to *requires-null*: obligation **X9**.
4. **`noPredicate` stays in the denominator.** XCCDF removes `notchecked` because its denominator is a
   human-authored benchmark; ours is induced from the regulator's own published template, so *no predicate
   exists* is a gap in **us**. Removing it would let the fraction rise by doing nothing. The justification
   ships attached to the number.

`aggregate.py` is deliberately thin at this phase: `residueIsConfined` requires `K` and `T`, which **have
no argued basis anywhere in the corpus** and render the literal string `PLACEHOLDER`. So
`aggregate(sf, policy)` returns `Verdict(state=None, stateWithheldBecause="policy_placeholder", policy=…)`
while the placeholder stands, and `Verdict(state=None, stateWithheldBecause="run_invalid", …)` on an
`INVALID` run — **two different nulls, distinguished** (D-P5-04). The 2×2 fills in when the policy does; it
is an open item and it does not block the phase.

### CLI and outputs

```
cdfc run fixtures/synthetic/clean__template-computed__fme-q1__<sha8>.xlsx \
         --template 7d9a1960 --registry-root <root> --profile default --out runs/
        -> runs/<run_id>/{run.jsonl, run.db, manifest.json}
cdfc closure explain <run_id>        # prints the seven terms and, on violation, the unbucketed keys
make run-fme                          # the clean filing and the seeded-fault variant, both
```

`run.jsonl` is NDJSON, **one line per evaluation** (not per cell), ordered by
`(predicate_id, version, stable_key)` with an explicit sort key so it is byte-stable. `run.db` is a SQLite
file created from `store/schema.sql` — a file, therefore hashable, therefore nameable in the manifest.

### Functionality validation

**Unit** — `tests/unit/test_rollup.py`, `tests/unit/test_closure.py`, `tests/unit/test_settled_fraction.py`
- `test_roll_up__empty_evaluation_set_is_NO_PREDICATE` — and asserts `NO_PREDICATE` is **not** in
  `PRECEDENCE`.
- **`test_roll_up__one_pass_and_one_not_run_is_unsettled`** — the audit's resolution, as one line.
- `test_roll_up__error_beats_everything` and `test_roll_up__out_of_scope_loses_to_everything`.
- **`test_roll_up__informational_only_cell_is_no_predicate`** (D-P5-05/F14) — a cell whose entire
  evaluation set is `INFORMATIONAL` rolls up to `NO_PREDICATE(no_predicate.rule_ambiguous)` and **stays in
  `inScope`**; a cell with one `PASS` and one `INFORMATIONAL` still rolls up to `PASS`.
- **`test_roll_up__degenerate_precondition_stays_in_scope`** (C3) — an
  `OUT_OF_SCOPE(out_of_scope.not_applicable)` cell carrying **`scope_kind = PREDICATE_PRECONDITION`** is
  `OUT_OF_SCOPE` for precedence and **counted in `inScope`**, i.e. it appears in `outOfScopeRetained`; the
  same cell carrying `scope_kind = DECLARED_CHARACTERISTIC` **leaves**; and the same cell carrying **no**
  `scope_kind` **raises `MissingScopeKindError`**. Three rows, one test, no default.
- **`test_roll_up__degenerate_precondition_flags_requalification`** (C3) — the retained cell sets
  `requalification_flag`, so the predicate that produced it is queued for **G3 re-qualification**. *Being
  counted is not the punishment; being re-qualified is.*
- `test_materialise__count_equals_field_surface` — `3,747` for FME, **before** any evaluation.
- `test_partition__seven_terms_sum_to_field_surface`, and
  **`test_partition__inscope_uses_removal_basis_only`** — `inScope` is computed from `in_scope()` and from
  nothing else; a second removal path anywhere in `closure.py` fails the test.
- `test_compute__invalid_run_returns_None_not_zero`, and
  **`test_contract__invalid_carries_a_null_not_an_absence`** (D-P5-06).
- `test_compute__no_mask_template_returns_None_and_the_source_string` — over
  `IFSCA_Annual_Reporting_Format` and `Draft_ACAC_Format`; the former is the dangerous one because a naive
  unlocked count returns **8**, which looks like a small answer rather than like no answer (NC-D03).
- `test_compute__fraction_is_decimal_not_float`.

**Property** — `tests/property/test_prop_closure.py`, `tests/property/test_prop_rollup.py`
- `test_prop__closure_seven_terms` — *property:*
  `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface`.
  *Generator:* random assignment of the 8 states over `N ∈ [1, 5000]` cells. (`01` §1.2, mandatory.)
- `test_prop__rollup_precedence_is_a_total_order` — *property:* `max` under `PRECEDENCE` is associative and
  commutative and the order is total. *Generator:* random multisets of the 8 states. A partial order here
  would make the rolled-up state depend on evaluation order, and evaluation order is not part of the
  verdict.
- `test_prop__settled_is_monotone_non_increasing_in_not_run` — *property:* turning any single evaluation
  from `PASS` into `NOT_RUN` never increases `settled`. *Generator:* random evaluation vectors over
  `M ∈ [1, 50]` predicates × `N ∈ [1, 500]` cells. **This is the audit resolution as an invariant rather
  than as a single case**, and it is the property NC-E04's injector must falsify.
- **`tests/property/test_prop_settled_fraction.py::test_prop__fraction_does_not_rise_as_the_filing_empties`**
  — *property:* for every filing `F` and every value-deletion transform `d`,
  **`fraction(run(d(F))) ≤ fraction(run(F))`**. *Generator:*
  `tools/fixtures/value_deletion.py::deletions(reference_fill, seed)` — every single-cell deletion over the
  FME reference fill's populated field-surface cells, random `k`-subsets for `k ∈ [1, 200]`, and both
  extremes. Shrinks on the deleted-cell set. **This is the general form of the property above, and it is
  the one the product's headline claim actually needs**, because `OUT_OF_SCOPE` and `INFORMATIONAL` both
  leave `inScope` and are both reachable by making the filing worse. See D-P5-05 for the design decision
  it enforces and for the pre-committed fallback if it fails.
- **`test_prop__deleting_a_value_never_moves_a_cell_out_of_inScope`** — the narrower invariant that
  localises a failure of the above: for every `d`, `inScope(d(F)) ≥ inScope(F)` is **not** required, but
  every cell that leaves `inScope` under `d` must carry a `(state, reason)` pair in `REMOVAL_BASIS`. A
  counterexample names the pair, which is the line of `states.py` to change.

**Golden** — `tests/golden/test_closure_partition.py`
- **`test_golden__closure__fme_clean_hand_computed`** on the **HAND-COMPUTED clean filing** (E6) — the
  seven terms pinned, and per R-GOLD-2 paired with value assertions: `settled.fail == 0`, and a named cell
  (`'3. Portfolio'!O7`) carrying state `PASS` with its `settled_by` predicate id. **This is the golden that
  carries information about the arithmetic predicates**, because its derived cells were typed by a person
  and not computed by `calc/`.
- `test_golden__closure__fme_clean` on the **TEMPLATE-COMPUTED clean filing** — the same seven terms, and
  **its docstring states, and a second assertion records, that this filing cannot falsify an arithmetic
  predicate**: `read_keys(p) ∩ generator.computed_cells ≠ ∅` for all 227 of them, so a zero here is
  `x == x`. Same discipline as `02`'s `test_golden__aggregate_block__fme`, which records its own limit
  rather than hiding it. Labelled `NON-DISCRIMINATING (arithmetic)` wherever it renders.
- `test_golden__closure__fme_seeded` on the single-fault variant — `settled.fail` equals the number of
  predicates reading the mutated cell, **and those predicate ids are asserted by name**, not merely
  counted.
- `test_golden__closure__nine_workbooks` — closure holds on the **7 of 9** workbooks that have a mask; the
  other two return `settledFraction: null` with the exact source string and closure is recorded as
  `NOT_EVALUABLE(no_mask)` rather than as `0 == 0`.
  Why these workbooks: FME because it is the only one with all five structural features live at once; the
  two mask-less ones because they are the only ones that can produce a plausible-looking wrong denominator;
  `EDR_1` because it has a mask and zero formulas, so its mechanically derivable settled fraction is 0% and
  that must publish rather than abort.

**Differential (internal, not one of D1–D4)** — `tests/unit/test_closure.py::test_closure_sql_matches_python`
compares `CLOSURE_SQL`'s `GROUP BY` against the Python partition. **It is stated in the test's own docstring
that this is *not* an independent implementation** — both read the same `run_cell` rows, so it catches a
transcription error and nothing more. That is exactly the distinction `NC-D02d` draws between two
implementations and one implementation called twice, applied honestly to our own cheap check.

**Negative controls** — **NC-E04** (roll-up precedence inverted; all three tests, including
`test_nc__E04c_extractor_disagreement_lowers_the_fraction`), **NC-E05** (closure has a hole, plus the
positive control that an `INFORMATIONAL` run does **not** abort under the seven-term form),
**NC-E07** (floating-point money), **NC-E08** (tolerance applied to counts), **NC-D02a** (denominator
provenance: the import closure of `field_surface` does not reach `cdfc.predicates`), **NC-D03** (no mask ⇒
`null`), and new **NC-E21** (`run_cell` materialised from the evaluations instead of from the field
surface), **NC-E22** (`INVALID` emits `0`, or **omits the key**, instead of a present `null`),
**NC-E24** (a cell leaves `inScope` for a reason derived from the filing's own values) and
**NC-E25** (an `INFORMATIONAL`-only cell leaves the denominator).

Plus the six failure modes of spec §II.1.8 as fixtures under
`fixtures/predicates/broken/mode{1..6}__*.yaml`, each of which must be caught:
(1) `check_all_percentages_sum_to_100` whose selector misses a renamed sheet — `group()` returns `[]`,
`all([])` is `True` — must yield `ERROR(error.cells_bound_zero)` and `run_state = INVALID`, never `PASS`;
(2) empty-set arithmetic `sum([]) == 0` passing `len(rows) == declared` as `0 == 0`; (3) selector drift;
(4) scope truncation by hidden sheet; (5) shared numerator/denominator; (6) a swallowed exception.

**Determinism** — `tests/determinism/test_det__run_jsonl_byte_identical` — two runs of the same filing under
different `TZ`, `PYTHONHASHSEED`, locale and working directory produce byte-identical `run.jsonl`. This is
the first phase at which `make determinism` has something to compare, and it is the down payment on
G-REPRO at P11.

**Performance** — a new budget `PERF-ROLLUP` (roll-up + closure over 3,747 cells; spec's DERIVED figure for
F11 is < 5 ms). Same rule as `PERF-CEL-COMPILE`: the first CI run records the baseline, the budget is set
at 3× (warn 2×), the recording is committed in the same PR. `PERF-CORE` (~30 ms, fail 60 ms) must not
regress.

**Mutation** — Tier V, `K/V ≥ 0.90`, blocking from this phase, for `evaluate/` and `verdict/`. Per
`01` §3.3 three operator families are specifically load-bearing here and must be killed rather than
excluded: string-literal mutation on reason codes; comparison-boundary mutation on `τ` (which exercises
`indeterminate.tolerance_straddle`); and `and ↔ or` in `preflight.py`.

---

## P5.2 The measurement this phase produces

**The runtime seven-term closure partition on a real filing, and specifically the runtime settled count and
its delta from the static 2,373.** Denominator: the **3,747**-cell FME field surface. Warrant **MEASURED**.
**Nobody has this number.**

The static figure counts cells reachable by at least one harvested predicate, computed before any
evaluation; it is unaffected by roll-up precedence and is not withdrawn by the audit. The runtime figure is
what a filing actually produces, and **under the binding precedence order it can be lower** — a cell read by
one passing and one not-run predicate is unsettled. Publish both, as a pair, with the delta and the reason
for each cell that moved:

```
docs/measurements/P5-runtime-closure.md
  filing (primary):  clean__hand-computed__fme-q1__<sha8>.xlsx  (SYNTHETIC; derived cells typed by a
                     PERSON from the formula text -- calc/ never touched them.  This is the filing the
                     0-FAIL claim is made on.)
  filing (plumbing): clean__template-computed__fme-q1__<sha8>.xlsx
                     -> labelled NON-DISCRIMINATING (arithmetic): calc/ wrote its derived cells, so no
                        arithmetic predicate can fire on it and a 0 here is x == x
  fieldSurface:      3747          computedTwiceAgreed: true
                     generatorRule: v3      validationState: PROVISIONAL-UNVALIDATED   (plan/02 P2-B2)
  static settled:    <computed by P4-B4>    spec figure 2373 (DERIVED-FROM-SPEC)  delta: <..>
  runtime settled:   <n>           delta from static: <..>
  seven terms:       outOfScope <> + informational <> + settled <> + indeterminate <>
                     + notRun <> + noPredicate <> + error <>  ==  3747        (cellsTotal)
  of which retained: outOfScopeRetained <>  informationalRetained <>          (D-P5-05)
  inScope:           3747 - (outOfScope - retained) - (informational - retained)  =  <..>
  fraction:          settled.total / inScope                                  (rendered WITH cellsTotal)
  admissionState:    PRE-GATE      admissibilityCaveat: <the spec's sentence, verbatim>
```

Two secondary numbers this phase also emits, both new and both cheap:
`keys_type_checked / keys_preflighted` per run (D-P5-03 — a type check that did not happen is never
reported as one), and the **count of cells whose state was lowered by roll-up**, i.e. cells with at least
one `PASS` and at least one non-`PASS` evaluation. The second is the audit resolution's effect size, and it
is the number a reviewer will ask for.

Ledger row:

```json
{"phase":"P5","build":"P5.4","metric":"settled.runtime.fme_clean","numerator":0,"denominator":3747,
 "denominator_source":"field surface from styles.xml unlocked mask, computed twice (P2)",
 "warrant":"MEASURED","produced_by":"src/cdfc/verdict/settled_fraction.py",
 "command":"make run-fme && cdfc closure explain <run_id>",
 "caveat":"PRE-GATE. None of the predicates producing this number is admitted under G4; the corpus is TEMPLATE-COMPUTED and synthetic. Not comparable across filings: out-of-scope determinations are filing-specific.",
 "date":"____-__-__"}
```

## P5.3 Exit gate

**Twelve** booleans, each readable from `reports/` or `docs/measurements/` after a green CI run.

> **One item below is deliberately NOT one of the twelve.** Item **1a** is a **SMOKE CHECK, NON-GATING** —
> it is listed here because it runs here, and it is numbered `1a` rather than `2` precisely so that nobody
> can recount the list and promote it. See the box under it (arbitration **C5**).

1. **Clean filing ⇒ 0 `FAIL`, on a filing this product did not compute.** On the **HAND-COMPUTED** clean
   filing (E6), `settled.fail == 0`. A predicate firing on a cell a *person* derived from IFSCA's own
   formula text is a genuine false failure and must be investigated before this gate can pass.
   **The criterion moved here from the TEMPLATE-COMPUTED filing, and the reason is the whole of finding
   F2:** that filing's derived cells are written by `src/cdfc/calc/`, and `sum_identity`,
   `cross_sheet_equality` and `tally_identity` — **277 of the 515 harvested predicates** — assert exactly
   the identities `calc/` enforced when it produced the file. The oracle and the system under test are the
   same function, so the gate could not detect a *wrong* arithmetic predicate; it could only detect a
   predicate that disagreed with itself. It was green on a correct implementation, on one with a
   1,000×-wide tolerance, and on one that returned `[]`.
1a. **SMOKE CHECK — NON-GATING. NOT AN EXIT CRITERION. `TEMPLATE-COMPUTED` MAY NOT BE CITED IN A GATE.**
   The TEMPLATE-COMPUTED filing still runs, and still reports `settled.fail == 0` — as **plumbing**,
   labelled `SMOKE ONLY — NON-GATING — NON-DISCRIMINATING (arithmetic)` in
   `docs/measurements/P5-runtime-closure.md` and in the golden's docstring, with the second assertion
   recording that `read_keys(p) ∩ generator.computed_cells ≠ ∅` for every arithmetic predicate.
   **Its result does not enter P5's exit gate: P5.3 is TRUE or FALSE without consulting it, and a red 1a
   is a defect report, never a gate failure.** *A check we keep for its plumbing value must say that is why
   we keep it — and must not be allowed to sit in a numbered list of gate conditions where the next reader
   counts it.*
   **No FFR, no false-failure rate, no severity tier and no published rate may ever be derived from this
   filing** — the mechanised form of that prohibition is P8-B3's (obligation **X10**).

   > **Arbitration C5, applied.** This item was previously written as **exit criterion 1a**, i.e. as a gate.
   > `plan/05` ruled that `TEMPLATE-COMPUTED` is *a named smoke test that may not be cited in a gate*, and
   > that ruling wins: a `TEMPLATE-COMPUTED` corpus is generated by `src/cdfc/calc/`, **the same function
   > the arithmetic predicates and the template differential re-check**, so citing it in a gate is buying a
   > gate pass from yourself — which is **F2 exactly**. It may not be cited in a gate, in a severity tier,
   > or in any published rate. It is **relabelled `SMOKE ONLY — NON-GATING` so nobody re-promotes it**, and
   > this is consistent with the corpus-provenance-to-severity table in `plan/04`, with which it must not be
   > allowed to disagree.
2. **One seeded fault ⇒ exactly the predicates reading that cell `FAIL`**, asserted **by predicate id**,
   not by count.
3. **`cells_bound == 0 ⇒ ERROR(error.cells_bound_zero) ⇒ run_state = INVALID`** demonstrated on a fixture,
   with the run-level `invalid.cells_bound_zero` cause carried **as well as** the item-level code.
4. **Closure holds on the 7 of 9 workbooks that have a mask**, or report generation aborts; the two
   mask-less workbooks return `settledFraction: null` with the exact source string.
5. **`test_settled_fraction_falls_on_not_run` green**, and `test_prop__settled_is_monotone_non_increasing_in_not_run`
   green — the single case and the invariant.
5a. **`test_prop__fraction_does_not_rise_as_the_filing_empties` green**, over
   `tools/fixtures/value_deletion.py`'s generator, **or** D-P5-05's pre-committed fallback invoked in
   writing (`inScope` frozen to `cellsTotal`, both counts rendered) with the counterexample published in
   `docs/measurements/P5-runtime-closure.md`. Plus
   `test_roll_up__informational_only_cell_is_no_predicate`,
   `test_roll_up__degenerate_precondition_stays_in_scope`,
   `test_contract__removal_basis_is_total_and_closed`,
   `test_partition__inscope_uses_removal_basis_only`, and
   `test_contract__fraction_renders_inscope_and_cellstotal_together`.
   **This is the phase's second no-fallback criterion after criterion 5. A settled fraction that rises when
   a filer fills in less is not a smaller product; it is a product whose headline number rewards the
   behaviour it exists to detect.**
5b. **`test_contract__invalid_carries_a_null_not_an_absence` green** (D-P5-06), and
   `test_contract__thirty_reason_codes` green with the `8 × 31` exhaustive product — **the pinned counts do
   not move** (C3), and `docs/decisions/D-P5-05-…` records that they were proposed to move and did not.
5c. **`test_contract__scope_kind_is_read_not_ignored` green** (C3) — `settled_fraction.py` reaches
   `scope_kind` on every `out_of_scope.not_applicable` path, and a build that subtracts all `OUT_OF_SCOPE`
   fails it **and** `test_prop__fraction_does_not_rise_as_the_filing_empties`.
6. `EVALUATION-CONTRACT.md` is generated, byte-identical to `tools/gen_contract.py`'s output, and
   set-equal to the pinned spec extraction. **One file. Three drafts gave three different fives.**
7. `make nc-sweep` reports **NC-E20, E21, E22, E23, E24, E25** caught, **with
   `guards_flipped == guards_expected_to_flip`** (`02` P0-B3's exact-set sweep), each entry's DoD line C4
   citing the sweep report's row and node id rather than a pasted assertion, and each with an
   admission-side positive control.
8. `make mutation-pr` reports Tier V `K/V ≥ 0.90` for `evaluate/` and `verdict/` in the two-integer form
   with `E` arguments published and `T` ids listed.
9. `docs/measurements/P5-runtime-closure.md` published with both counts and the delta; ledger grew.

## P5.4 What it kills if it fails

- **If closure cannot be made to hold, the report cannot be generated at all.** That is the design's
  terminal `DISALLOW *` and it is not negotiable — the in-toto specification names the hazard in its own
  text: an implicit open world *"could allow artifacts to sneak into the step or inspection undetected."*
  **There is no degraded report.** The failure branch is to narrow the field surface to the sheets where
  closure does hold, publish the excluded sheets **by name** on the report surface, and carry the exclusion
  in the attestation. A smaller denominator honestly stated beats a full one that does not balance.
- **If the runtime settled count cannot be made to fall when a predicate does not run**, the audit's
  resolution is unimplemented and the product's central sentence — *the settled fraction falls, it does not
  silently succeed* — is false. This does not shrink the system; it **stops** it. There is no smaller
  honest product on the other side of this failure, because every downstream number is a fraction of a
  denominator whose roll-up would then be lying. It is the one branch in these two phases with no
  ship-smaller fallback, and it is stated here so that nobody discovers it under pressure.
- **If the two-vocabulary split cannot be maintained** — if run-level causes keep leaking into per-cell
  reasons — the item-level count is no longer 8 × 30 (the baseline C3 preserves) and four pinned places move
  at once. The fallback is the audit's rejected option, a 31st code, taken **only** with a written argument
  that the category correction was wrong; and the pinned counts are updated everywhere in one commit with a
  decision record. **C3 already refused this once**, for `out_of_scope.precondition_degenerate` — a field on
  the existing code carried the distinction without moving the count, and that is the pattern to reach for
  first.
- **`aggregate.py` failing is not a phase failure.** `K` and `T` are an open item with no argued basis, the
  verdict state is withheld with a typed reason, and P14 renders the withholding. It does not block.

## P5.5 Effort

**13 engineer-days** — B1 3 · B2 2 · B3 2 · **B4 6** (was 5; +1 for D-P5-05: `REMOVAL_BASIS`, the two
closure sub-counts, `tools/fixtures/value_deletion.py` and the fraction property, which P9-B2 then imports
rather than rebuilding). Same assumption as P4. The estimate's two soft spots are both in B4: building the
TEMPLATE-COMPUTED clean filing is *not* free if P3's evaluator needed its ≤ 25-cell exclusion branch (add
~1 day to reconcile the excluded cells against the fact table), and the six §II.1.8 failure-mode fixtures
are six small artifacts, not one. **B3 is two days only because the vocabularies are already decided**; it
would be a week if the 30 codes were being designed here rather than transcribed.
*(The HAND-COMPUTED filing of E6 is built at `02` P3-B4 from the arm-2 expectation file and costs this
phase nothing; the person-days for that expectation file are budgeted in `02` R11.)*

---

# 6. THE NEW NEGATIVE-CONTROL CATALOGUE ENTRIES

**Thirteen** entries are appended to `tests/negative/catalogue.yaml` by these two phases. Every one has an
injector; **none carries `injector: NONE`**. Each is listed with its admission-side positive control, per
`01` §2.0 rule C5 — a rejection-side control alone would score perfectly for a reject-everything guard —
and, per the sweep's changed contract (`02` P0-B3), **every guard carries `flips: true|false`** so the
sweep asserts the exact set rather than "at least one".

> **Id allocation — CORRECTED.** This document previously stated *"`NC-Q11` and `NC-E08` are the current
> maxima"* and numbered from there. **That was false when it was written:** `02` had already allocated
> `NC-E10`–`E13`, and `04` §0.8(e) had allocated the ids then called `NC-Q12`–`Q16` while stating (also
> falsely) that *"the Q family is free from `NC-Q12`"*. *(All five are **RETIRED** under arbitration C9 and
> are quoted here as history only; this document's entries are `NC-Q70`–`NC-Q75`.)* Three of this document's `E` ids and all five of its `Q` ids collided
> with entries in other documents — **and the catalogue is keyed by `id`, so the later document's entry
> would have silently replaced the earlier one**, taking with it `02`'s `NC-E11`, the row that encodes the
> discovery that G-EVAL arm 1 is inert. The sweep would still have reported `caught == active` and
> `test_nc_meta__no_orphan_guard` would still have passed, because *an* entry named the guard.
>
> **This document now takes the bands `Q40–Q49` and `E20–E29` from `02` §1 R5a's normative table**, and its
> entries are renumbered accordingly: `Q12→Q40 · Q13→Q41 · Q14→Q42 · Q15→Q43 · Q16→Q44` and
> `E09→E20 · E10→E21 · E11→E22 · E12→E23`. Enforced by `ci/catalogue-ids.sh` (`02` R5 registry row 18) and
> `test_nc_meta__ids_are_unique`, both live from P0.

| id | The break, in one sentence | Injector | Guard | Positive control |
|---|---|---|---|---|
| **NC-Q70** | A field is dropped from the canonical serialisation, so two different predicates share a digest and one silently overwrites the other in the registry | `injectors/jcs_omits_qualified_against.py` | `test_prop__every_envelope_field_is_covered_by_the_digest`; `test_nc__Q70_digest_covers_qualified_against` | `test_golden__envelope__P0041_digest` |
| **NC-Q71** | The admitted-subset walker is permissive and lets a nested comprehension, a `filter()` in `expr`, or `matches()` through | `injectors/cel_profile_permissive.py` | `test_nc__Q71a_nested_comprehension_refused`, `Q41b_filter_outside_witness_refused`, `Q41c_matches_refused` | `test_nc__Q71d_flat_comprehension_admitted` |
| **NC-Q72** | `schema_keys` is extracted lexically from the CEL source instead of from the parsed AST, so a comprehension variable is reported as a root key and `[*]` is lost | `injectors/schema_keys_from_regex.py` | `test_nc__Q72a_key_extraction_is_ast_based` (7-form table); `Q42b_comprehension_variable_is_not_a_root_key` | `test_nc__Q72c_both_roots_are_reported` |
| **NC-Q73** | The cross-workbook total renders without its per-workbook distribution | `injectors/harvest_total_alone.py` | `test_nc__Q73_total_never_renders_alone` | the distribution renders with all nine rows including the two zeroes |
| **NC-Q74** | The harvest drops what it cannot express instead of recording a typed `SkipRecord`; the 389 weak records vanish and 515 looks like the whole story | `injectors/harvest_drops_weak.py` | `test_nc__Q74_weak_pile_is_counted_not_dropped` (asserts FME's 68, of which 2 `list_unresolved` reconcile the pinned 22−20 gap) | `test_golden__harvest_count__fme` still pins 280 |
| **NC-E20** | `cells_bound` is computed after `expr`, so the vacuous pass is produced and then corrected rather than being unreachable | `injectors/cells_bound_after_expr.py` | `test_nc__E20_binding_precedes_evaluation` (spy asserts `CelRuntime.evaluate` was never called) | a bound predicate does reach evaluation |
| **NC-E21** | `run_cell` is materialised from the evaluations instead of from the field surface, so cells no predicate touches vanish and the `noPredicate` bucket silently empties | `injectors/run_cell_from_evaluations.py` | `test_nc__E21_run_cell_materialised_from_field_surface` (`len(run_cell) == 3747` before evaluation); `E21b_no_predicate_count_is_not_zero` | closure still balances on the clean filing |
| **NC-E22** | An `INVALID` run emits `settledFraction: 0` or omits the field, instead of `null` | `injectors/invalid_emits_zero.py` | `test_nc__E22_invalid_emits_null_not_zero`; ties to `E2E-INVALID` | a `VALID` run emits a number |
| **NC-E23** | A run-level `invalid.*` cause is written into an item's reason field — the category error audit §V.7.3 corrected | `injectors/invalid_cause_as_item_reason.py` | `test_nc__E23_run_level_causes_are_a_separate_vocabulary` (the two enums share no member and no string) | `cells_bound_zero` writes **both** the item code and the run cause |
| **NC-Q57** — **REFERENCE, not a definition** (F1; registered in `01` §2, detail in `04` §4.4) | `claims_fault_classes` is derived from the classes that actually killed, **after** the campaign, so the predicate chooses the denominator of its own quality score. **One break, one entry:** this document and `04` had independently catalogued the *same* injector under two ids (`03`'s former `NC-Q45`, `04`'s former `NC-Q42`), which arbitration **C9** merges into `NC-Q57` | `injectors/claims_from_kill_vector.py` (the same file `04` names) | the `03`-side guards of the one entry: `test_envelope__narrowing_a_claim_changes_the_digest` · `test_g2_denominator_is_declared_before_the_campaign`. The gate-side guards `test_nc__Q57_claims_precede_the_campaign` and `test_nc__Q57b_an_honest_claim_is_admitted` are `04`'s | an honestly-declared predicate whose claimed classes all have `O > 0` **is admitted** |
| **NC-Q75** (new, F9/C2) | A candidate whose obligation has `source == TEMPLATE` carries no declared reason, so the plan cannot say why 280 of 280 harvested predicates cite no statute | `injectors/clause_absent_reason_dropped.py` | `test_nc__Q75_clauseless_candidate_declares_why` · `test_envelope__every_harvested_candidate_declares_why` (asserts **280 instances**, so the guard cannot go instance-free) · `test_harvest__obligation_coverage_is_published` (asserts **both** ratios render) | a clause-**bearing** hand-authored candidate (`source == STATUTE`) loads with `clause_absent_reason is None` |
| **NC-E24** (new, F13) | A cell leaves `inScope` for a reason derived from the filing's own values, so **deleting values raises the settled fraction** | `injectors/degenerate_precondition_removed.py` — makes `in_scope()` remove `(OUT_OF_SCOPE, OOS_NOT_APPLICABLE)` **regardless of `scope_kind`**, i.e. deletes the C3 retention rule for `PREDICATE_PRECONDITION` | `test_prop__fraction_does_not_rise_as_the_filing_empties` *(flips: true)* · `test_contract__removal_basis_is_total_and_closed` *(flips: true)* · `test_prop__closure_seven_terms` **(flips: false — closure must stay GREEN, which is what proves the injector broke the *denominator* and not the *partition*)** | `test_roll_up__degenerate_precondition_stays_in_scope` on the reference fill |
| **NC-E25** (new, F14) | A cell whose only binding evaluation is a declared-defective relation leaves the denominator, so **adding a row to `template_defects.yaml` raises the headline** | `injectors/informational_only_leaves_scope.py` | `test_roll_up__informational_only_cell_is_no_predicate` *(flips: true)* · `test_defect_table_cannot_raise_the_settled_fraction` *(flips: true; lives in `05`, calls our `assert_fraction_did_not_rise`)* | a cell with one `PASS` and one `INFORMATIONAL` still rolls up to `PASS` and stays settled |

**Where a negative control is impossible in these phases, and what it costs.** **NC-N01** applies in full to
P4: G0 will prove the quote locates and the provisos are declared, but *nothing in this document proves the
CEL means what the clause means* — the only published study of statute→executable-model generation tops out
at 51–53% outcome equivalence. A predicate can clear all five gates and enforce a rule that does not exist,
and the only mitigations are the kill vector by fault class and human review. **NC-N06** applies to P4-B3's
differential fallback: two runtimes wrong the same way are invisible to a differential, and this project has
already watched a hand-written regex and openpyxl reach the identical wrong number by the identical
mechanism on the same day. Both are carried in the DoD's §C6 and neither is repaired by anything in P4 or
P5.

---

# 7. WHAT AN ENGINEER SHOULD BUILD FIRST, AND WHY

The dependency order inside these two phases is not the order of maximum evidence. If a day has to be spent
before the rest of the phase is funded, spend it here:

1. **P4-B2's `read_keys` over the seven-form table** (half a day). It answers the phase's question before
   the phase is built: if comprehension binding cannot be resolved statically on `celpy`'s AST, the
   both-ways check is not exact, the settled fraction is an estimate, and §P4.4's failure branch fires —
   and it fires *twelve days earlier* than it would if this were built last.
2. **P5-B4's `roll_up` and the monotonicity property** (half a day, and it needs no filing). The audit's
   binding resolution is eleven lines of code and one property test. If it cannot be made to hold, the one
   branch with no ship-smaller fallback is open, and it should be open on day one rather than on day
   twenty-six.
3. **`test_prop__fraction_does_not_rise_as_the_filing_empties` against a stubbed roll-up** (half a day, and
   it needs no predicates — only the state machine, `REMOVAL_BASIS` and the value-deletion generator).
   **The adversary's prediction is that it fails**, and if it does, D-P5-05's design decision — and
   possibly its pre-committed fallback of freezing `inScope` to `cellsTotal` — is on the table on day two
   rather than after the surfaces have been built against the other shape. It is the cheapest way in this
   phase to find out that the product's headline number rewards emptying a filing.
4. Everything else in dependency order.

All three are cheap, all three are decisive, and all three are the shape this plan's evidence ordering
prefers: **a negative result higher in the list deletes more of the plan for less money.**

---

## REPAIRS APPLIED (adversary pass)

Against `plan/08-adversary.md`. One row per finding that touches P4–P5.

### FATAL

| id | The finding, in one line | What changed | Where |
|---|---|---|---|
| **F1** | G2's registry bar is computed over *"the fault classes the predicate claims to cover"* and **no field of the envelope holds such a claim** — the claim exists only in the `FaultWitness` G2 itself selects after the campaign | **`claims_fault_classes: tuple[str, ...]` added to `Candidate`, required, non-empty, inside `envelope_projection()` and therefore inside `code_sha256`.** Declared per harvest class in `docs/FAULT-CLAIMS.md`, **committed at P4-B4, four phases before the first campaign**. Tests: `…is_required_and_non_empty`, `…narrowing_a_claim_changes_the_digest`, `…claims_are_drawn_from_the_pinned_fault_model`, `test_harvest__claims_are_a_pure_function_of_the_class`, `test_g2_denominator_is_declared_before_the_campaign`. **NC-Q57** with `injectors/claims_from_kill_vector.py` and an admission-side twin. New published number: `fault_classes_claimed_by_no_harvested_candidate = {F10, F11, F14}` | D-P4-06; P4-B1 envelope + `claims_fault_classes` block; P4-B4 claims table; P4.2 (f); P4.3 1a; §6 NC-Q57; X1, X3, X4 |
| **F2** | The `TEMPLATE-COMPUTED` clean corpus is produced by the code the arithmetic predicates re-check, so P5's *"clean ⇒ 0 FAIL"* is true by construction for 277 of 515 predicates | **New entry criterion E6: a HAND-COMPUTED clean filing** whose derived cells were typed by a person from the formula text (built at `02` P3-B4 from the arm-2 expectation file; `calc/` never touches it). **P5.3 criterion 1 moved onto it.** The TEMPLATE-COMPUTED filing is retained as **1a, a NON-GATING SMOKE CHECK** (arbitration **C5** — it was briefly written as an exit criterion; `TEMPLATE-COMPUTED` may not be cited in a gate, in a severity tier or in any published rate), labelled `SMOKE ONLY — NON-GATING — NON-DISCRIMINATING (arithmetic)` with a second assertion recording that `read_keys(p) ∩ computed_cells ≠ ∅` for every arithmetic predicate. `HAND-COMPUTED` is a **fixture** token, not a seventh `CorpusProvenance` | P5.1 E4/E6; P5-B4 goldens; P5.2 measurement block; P5.3 1 and 1a; X10 |
| **F9** | G0's six rejection reasons all presuppose a clause; 280 of 280 harvested candidates carry `clause: None`, and no document says what G0 does with them — reject kills D-REJECT, skip makes the funnel's first stage `280 → 280` | **ARBITRATED (C2).** Obligations gain **`source: STATUTE \| TEMPLATE`**; harvested candidates are minted `OBL-TEMPLATE-<sheet>-<ref>` with `source: TEMPLATE` and **G0 runs for real** (`plan/04` P7-B1/B2) — the `SKIPPED_NOT_APPLICABLE` branch this row first took is **deleted**, because a gate stage that cannot fail is the product's own failure mode wearing a gate's clothes. **`clause_absent_reason` stays**, re-keyed: required and non-empty **iff the obligation has `source == TEMPLATE`**, from a closed three-member vocabulary, inside the digest — **280 instances, not zero**. **The published figure is two numbers, never one:** `predicates_with_a_STATUTE_obligation / 280 = 0 / 280` **and** `predicates_with_a_TEMPLATE_obligation / 280 = 280 / 280`. Tests: `test_envelope__clauseless_candidate_declares_why`, `test_envelope__every_harvested_candidate_declares_why`, `test_harvest__obligation_coverage_is_published`. **NC-Q75.** *The objection this document raised — that `find(quote)` succeeds by construction — is answered rather than dismissed: the quote is verbatim template text located in a content-addressed rendering of the pinned blank, so the check catches a harvest run against a different template version* | D-P4-07; P4-B1 `clause_absent_reason` block; P4-B4 data (ii); P4.2 (e); P4.3 1b; §6 NC-Q75; X2 |
| **F13** | `OUT_OF_SCOPE` and `INFORMATIONAL` leave `inScope`, and both are reachable by making the filing worse — **so emptying a filing can make the settled fraction rise** | **D-P5-05**: (1) `REMOVAL_BASIS`, keyed by `(state, reason)` with `RemovalBasis ∈ {TEMPLATE, SELECTION, DECLARED_CHARACTERISTIC}` — **a pair absent from the table stays in `inScope`**; (2) **`plan/05`'s `scope_kind` field, read here** (arbitration **C3**, superseding the 31st reason code this row originally proposed — a 31st code breaks a count pinned in four places, and `05` already writes the field): **only `scope_kind == DECLARED_CHARACTERISTIC` leaves the denominator; `PREDICATE_PRECONDITION` stays and is flagged for G3 re-qualification**, with `MissingScopeKindError` on absence and `test_contract__scope_kind_is_read_not_ignored` proving this document consumes what `05` produces; (3) `outOfScopeRetained` / `informationalRetained` sub-counts so the **seven-term closure is untouched** while `inScope` stops being `cellsTotal − outOfScope − informational`; (4) the property **`test_prop__fraction_does_not_rise_as_the_filing_empties`**, generator `tools/fixtures/value_deletion.py::deletions(reference_fill, seed)`, **built here and imported by P9-B2**; (5) `inScope` and `cellsTotal` render side by side, always; (6) a **pre-committed fallback** if the property still fails. **NC-E24**, whose `flips: false` guard is `test_prop__closure_seven_terms` | D-P5-05; P5-B3 `states.py` + `in_scope(…, scope_kind)`; P5-B4 `ClosurePartition`, `roll_up`, the boxed ruling, the two properties; P5.3 5a/5b/5c; §6 NC-E24; X7 |

### SERIOUS

| id | The finding, in one line | What changed | Where |
|---|---|---|---|
| **F14** | `05` says a template defect *"can neither fail a filer nor inflate our coverage"*; for a cell whose only binding evaluation is the defective relation, **it does inflate it** | **An `INFORMATIONAL`-only cell rolls up to `NO_PREDICATE(no_predicate.rule_ambiguous)`** and stays in the denominator — the repair applied at the roll-up, which is ours, rather than at the defect table, which is `05`'s. `test_roll_up__informational_only_cell_is_no_predicate`; `assert_fraction_did_not_rise()` published for `05`'s `test_defect_table_cannot_raise_the_settled_fraction`. **NC-E25** | P5-B4 `roll_up` contract + unit tests; §6 NC-E25; X8 |
| **F22** | The headline `2,373` does not reconcile with the harvest (53 validation predicates vs 20 membership predicates), and `07` pins it as a MEASURED literal | P4-B4 publishes **`len(cells_reachable)` computed from the emitted envelopes**, states 2,373 beside it as `DERIVED-FROM-SPEC`, and states the delta in a sentence; **a divergence is a finding in `docs/HARVEST-DELTA.md`, not a quiet correction**. `test_golden__static_settled_cells_reconcile`. `2,373` may be pinned in no golden until then — enforced by `ci/golden-literals-are-traceable.sh` (`02` registry row 17) | P4-B4 data (i); P4.2 (d); P4.3 1 and 1c; X5 |
| **F24** | Three contracts for `settledFraction` on `INVALID`: `null`, `forbidden`, and `omitted-is-a-violation` | **One rule: present and `null`.** `compute()` still returns `None`; **the serialiser may not omit the key**. `test_contract__invalid_carries_a_null_not_an_absence`. The JSON Schema `if/then` becomes `required + const: null` | D-P5-06; P5-B4 rule 3; P5.3 5b; X9 |
| **F27** | Colliding `NC-` ids: this document's `E09–E12` collide with `02`'s `E10–E13`, its `Q12–Q16` with `04`'s, and its own text asserted the collision away | **All ids renumbered into `02` R5a's bands for this document, `Q40–Q49` and `E20–E29`** (`Q12→Q40 … Q16→Q44`, `E09→E20 … E12→E23`), every reference and test name updated; the false *"`NC-Q11` and `NC-E08` are the current maxima"* sentence **replaced with the corrected record and the band statement**. Enforced by `ci/catalogue-ids.sh` and `test_nc_meta__ids_are_unique`, both live from P0 | §6 opening box; every `NC-` reference in the document; P4.3 4 |
| **F29** | `07` P15-B1 requires `docs/measurements/P4-transfer-mechanical.md`; P4-B4 produces `P4-harvest-distribution.md` | **One file, chosen here: `docs/measurements/P4-harvest-distribution.md`**, with the transfer note as a section of it, exposed as `cdfc.measure.paths.P4_HARVEST_DISTRIBUTION` so `07` imports the constant instead of re-typing a filename | P4-B4 transfer note; X6 |

### Cross-document obligations this document's repairs create

Named `X1`–`X10` so the receiving owner can check their change against this document rather than
re-deriving it.

| # | Obligation | Owner |
|---|---|---|
| **X1** | `g2_kill.check()` computes the registry bar **only** over `cand.claims_fault_classes` and **raises** when any claimed class has `O == 0` on this campaign. An unexercised claim is not a claim | `04`, P7-B3 |
| **X2** *(rewritten by C2 — it previously instructed `04` to build the branch C2 deleted)* | **G0 RUNS FOR REAL** over every candidate whose obligation has `source == TEMPLATE`, asking whether the predicate faithfully implements the relation it claims to implement; there is **no `SKIPPED_NOT_APPLICABLE(g0.no_clause_declared)` disposition and no skip branch**. Stage one of `docs/measurements/P7-attrition.md` still renders three integers, `entered / skipped / survived`, `skipped` is **never** counted as a survivor, and under C2 `skipped == 0` — the column exists so a future obligation source cannot enter the funnel silently. **Both** obligation-coverage numbers are published together. `test_g0__disposition_of_a_clauseless_candidate_is_specified_and_counted` · `test_p7__both_obligation_counts_render_or_neither_does` | `04`, P7-B2 |
| **X3** | `TEMPLATE_DIFF` declares `claims_fault_classes = ("F11",)` in its `RelationSpec`, and every relation in the registry declares one. F11 is claimed by nothing in the harvest | `05`, P9-B1/B2 |
| **X4** | The predicate library renders `K/O` over the **claimed** set **and** `K/O` over **all fourteen** classes, side by side. The gap is the number a reviewer wants | `07`, P14 |
| **X5** | `test_golden__report_hero__fme` asserts `S == len(static_settled_cells(schema, registry))` and `S + U == inScope`; the literals `2,373` and `1,374` move into `docs/HARVEST-DELTA.md`'s regime. `ci/golden-literals-are-traceable.sh` fails the build otherwise | `07`, P14-B1 |
| **X6** | `07` P15-B1's entry criterion cites `cdfc.measure.paths.P4_HARVEST_DISTRIBUTION`, not the string `docs/measurements/P4-transfer-mechanical.md`, which no build creates | `07`, P15-B1 |
| **X7** | P9-B2's precondition-monotonicity property **imports `tools/fixtures/value_deletion.py`** (built at P5-B4) rather than specifying a second generator. One generator, two properties | `05`, P9-B2 |
| **X8** | `05` P9-B1's sentence *"`INFORMATIONAL` is removed from the settled denominator … so a template defect can neither fail a filer nor inflate our coverage"* is **arithmetically wrong in its second clause** and must be corrected; `test_defect_table_cannot_raise_the_settled_fraction` calls `verdict.settled_fraction.assert_fraction_did_not_rise` | `05`, P9-B1 |
| **X9** | `05` P11-B1's `test_contract__invalid_run_carries_no_fraction` must change from *the schema **forbids** a `settledFraction`* to **requires it, `const: null`** (D-P5-06), and `01` §1.10 / `00` P10's `E2E-INVALID` text must say *present and null* | `05`, P11-B1; `01` §1.10; `00` P10 |
| **X10** | `g4_ffr.check()` **raises `UninformativeCorpusError`** when `read_keys(cand) ∩ corpus.computed_cells ≠ ∅` — the same fail-closed shape as `SELF-AUTHORED`, in the same function. `ValueGrid.computed_cells` exists from `02` P3-B4 and `import_closure()` from `02` P0-B3, so both operands are available. `TEMPLATE-COMPUTED` remains admissible for membership, bounds, dates and `conditional_required` — a real residual licence, stated narrowly | `04`, P8-B3 |

### Findings recorded but NOT repaired here, and why

- **F2's gate half (X10), F12, F16, F17, F37** are P8's; **F1's gate half (X1)** and **F9's gate half (X2)**
  are P7's; **F18/F19's consumer halves** are P6's and are carried as `02` §Y Y9. `02` repairs the P0–P3
  sides of F3, F4, F5, F7, F8, F10, F15, F18, F19, F20, F22, F23, F27, F28, F31, F36, F38, F39, F40, F43.
- **F21, F30, F32, F34, F35, F41, F42, F44** touch no build in P4 or P5.

### One thing this pass could not repair

**NC-N01 is untouched and it is the largest residue in these two phases.** `claims_fault_classes` makes a
predicate's *quality score* honest about its own denominator; `clause_absent_reason` makes a candidate
honest about having no clause. **Neither establishes that a predicate means what its clause means** — the
only published study of statute→executable-model generation tops out at 51–53% outcome equivalence, and a
predicate can still clear all five gates and enforce a rule that does not exist. The repairs above narrow
what a green build can claim; they do not touch that.

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C2** — F9's disposition | **this document's `SKIPPED_NOT_APPLICABLE` branch is deleted** — it made G0 decorative for all 280. `obligation_id` becomes required; `clause_absent_reason` is **re-keyed to `source == TEMPLATE`**, which gives it **280 instances instead of zero**; the published figure becomes **two numbers**. Obligation **X2** rewritten — it previously instructed `04` to build the branch C2 deleted | D-P4-07 row · P4-B1 envelope + the `clause_absent_reason` block · P4-B4 data (ii) · P4.2 (e) · P4.3 1b · §6 NC-Q75 · F9 row · X2 |
| **C3** — F13's retention | **the 31st reason code `out_of_scope.precondition_degenerate` is deleted**; the vocabulary stays at **30** and this document now **reads `plan/05`'s `scope_kind`**: only `DECLARED_CHARACTERISTIC` leaves the denominator, `PREDICATE_PRECONDITION` stays **and is flagged for G3 re-qualification**; `MissingScopeKindError` on absence; new `test_contract__scope_kind_is_read_not_ignored` (AST scan) | D-P5-05 row · P5-B3 `states.py`/`reasons.py` · the 31st-code section · contract tests · P5-B4 boxed ruling · roll-up tests · P5.3 5b/5c · §6 NC-E24 · F13 row |
| **C5** — `TEMPLATE-COMPUTED` in a gate | P5.3's **exit criterion 1a is downgraded to a NON-GATING SMOKE CHECK** and relabelled `SMOKE ONLY — NON-GATING`; its result does not enter the exit gate | P5.3 header note · P5.3 1a · F2 row |
| **C9** — the catalogue | `NC-Q40`–`Q46` → **`NC-Q70`–`Q75`**, with `NC-Q45` **merged into `NC-Q57`** (one break, one injector, one entry — it was `04`'s former `NC-Q42`). All seven old ids **RETIRED**; guard slugs moved with their entries; this document allocates nothing | §6 catalogue · P4-B1 · P4.3 · §6 id-allocation note |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
