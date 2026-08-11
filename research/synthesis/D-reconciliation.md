# D — RECONCILIATION

**The adversarial pass over sections A, B and C, run 10 Aug 2026 against all fifteen lanes and
`RND-BRIEF.md`. Nothing here is new research. Everything here is a place where the specification
disagrees with itself, with a lane, or with its own warrant rules.**

Counts: **31 contradictions · 9 surviving falsehoods to delete · 11 unwarranted-confidence
restatements · 12 blocking gaps · 3 sanded-off innovations to restore.**

Reading rule used throughout: where a lane opened a primary source and the adversarial pass did not
refute it, the lane wins. Where two synthesis sections disagree and neither cites a lane, the one
whose number is arithmetically checkable wins. Where neither is checkable, the item is a gap, not a
resolution.

---

# 1. CONTRADICTIONS

## Group I — The verdict model does not agree with itself (the product's core object)

### C1 — How many item states are there?

> **A §4.6.1:** "The state axis — **seven** closed values… `PASS · FAIL · INDETERMINATE · NOT_RUN ·
> NO_PREDICATE · OUT_OF_SCOPE · INFORMATIONAL`" — with `ERROR` described separately as "an item state
> distinct from every reason code above."

> **B §4.5:** "**8 states, closed.**" — the same seven **plus `ERROR`** as a first-class row.

> **C §3.2 T4:** "L5 execution with the **7-state axis**"; C §3.1 (Wed 13 Aug) lists the seven.

**B is right.** A itself says `ERROR` is "an item state", then omits it from its own enumeration, and
A's closure invariant (C3) then fails to account for it. C is copying A's error.

**Replacement:** *There are eight closed item states — `PASS`, `FAIL`, `INDETERMINATE`, `NOT_RUN`,
`NO_PREDICATE`, `ERROR`, `OUT_OF_SCOPE`, `INFORMATIONAL` — of which the first six are in the settled
denominator and any `ERROR` sets the run state to `INVALID`.*

### C2 — How many reason codes?

> **A §4.6.2:** "The reason vocabulary — closed, namespaced, **nineteen** codes."
> **B §4.5:** "**30 reason codes**, closed and namespaced."
> **C §3.2 T4 / §5.1 step 4 / §5.5 N3:** "the **19-code** namespaced reason vocabulary."

**B is right, and A's own text proves it:** A enumerates 7 `NO_PREDICATE` + 11 `NOT_RUN` + 4
`INDETERMINATE` + 3 `OUT_OF_SCOPE` = **25** codes under a heading that says nineteen. B's 30 = 8 + 10
+ 4 + 3 + 5 `ERROR` codes, and its list is internally consistent.

**Replacement:** *The reason vocabulary is closed, namespaced and has 30 codes across five state
families; a code is admitted only if it implies a different remedy from every existing code.*

### C3 — The closure invariant is arithmetically wrong in A

> **A §5.1.5 and §L7:** `outOfScope + settled.total + indeterminate + notRun + noPredicate ==
> pairsTotal`
> **B §3.1/F11:** `outOfScope + informational + settled + indeterminate + notRun + noPredicate +
> error == pairsTotal`

**B is right.** A's equation has no bucket for `INFORMATIONAL` or `ERROR`, both of which A's own state
table defines. Under A's formula every informational item aborts the report.

**Replacement:** *Use B's seven-term closure; it is the only form under which every one of the eight
states lands in exactly one bucket.*

### C4 — What happens when `applicable` evaluates false

> **A §L5 rule 1:** "`false → UNCHECKED(P.reason_if_inapplicable)` [NOT PASS]"
> **B §3.1/F8 rule 1:** "`false → OUT_OF_SCOPE(P.reason_if_inapplicable)` [never PASS]"

**B is right, and A is quoting a token it deleted.** `UNCHECKED` is the *brief's* single non-settled
state; A §4.6.1 replaced it with seven states and A §4.6.2 publishes the six→nineteen mapping. A's
entire L5 evaluation contract (rules 1, 2, 3, 5) is still written in the retired vocabulary.

**Replacement:** *`applicable == false` yields `OUT_OF_SCOPE` with a reason from the
`out_of_scope.*` family, and the word `UNCHECKED` appears nowhere in the evaluation contract.*

### C5 — What happens when `expr` raises

> **A §L5 rule 3:** "runtime error → `ERROR(predicate, exception)` **[NEVER FAIL, NEVER UNCHECKED]**"
> **B §3.1/F8 rule 3:** "runtime error → `NOT_RUN("source_unreadable")` [never FAIL]"
> **B §4.5** simultaneously defines `ERROR.predicate_raised`.

**A is right and B contradicts itself.** A predicate that raised is an apparatus failure, not an
unreadable source; B's own `ERROR` family says so one page later.

**Replacement:** *A runtime error inside `expr` is `ERROR(predicate_raised)` and sets the run state to
`INVALID`; `NOT_RUN(source_unreadable)` is reserved for inputs that could not be read.*

### C6 — What `cells_bound == 0` produces

> **A §L5 self-check:** "binding to zero is an automatic `ERROR`, never a `PASS`."
> **B §3.1/F8 rule 5:** "`cells_bound == 0 → ERROR(cells_bound_zero)`, and the run becomes `INVALID`."
> **C §3.2 T4 and §5.2 A5:** "`cells_bound == 0` ⇒ `NOT_RUN(predicate_error)`, never `PASS`."

**A and B are right; C is wrong.** Binding to nothing is the vacuous-pass failure mode the whole
design exists to catch — demoting it to `NOT_RUN` puts it in the same bucket as a rate-limited
register.

**Replacement:** *`cells_bound == 0` is `ERROR(cells_bound_zero)` and makes the run `INVALID`.*

### C7 — What a declared (unimplemented) proviso emits

> **A §L4 T0:** "an emitted `UNCHECKED(scope: <proviso text>)`"; A §4.1 example emits
> `UNCHECKED(not_run.input_unavailable.counterparty)`
> **B §3.5 GATE 0:** "an emitted `NO_PREDICATE(rule_ambiguous)` declaring it"
> **C §1.4 G0:** "`UNCHECKED(scope: <proviso text>)`"

Three different emissions, one of which (`UNCHECKED`) is not a state, and B's choice is wrong on the
merits: an unimplemented proviso is not an ambiguous rule.

**Replacement:** *A declared-but-unimplemented proviso emits
`NO_PREDICATE(no_predicate.not_yet_synthesised)` carrying the proviso's verbatim text and character
span, and the predicate's scope record records `provisos_declared`.*

### C8 — `method`, `warrant` and `provenance` enums differ between the two schemas

> **A §5.1.3:** nine methods, including **`TEMPLATE_DIFF`** ("the formula-override detector") and
> **`DIFFERENTIAL`**.
> **B §4.2 `run_item`:** eight methods — **no `TEMPLATE_DIFF`**, and `DIFFERENTIAL` is spelled
> **`METAMORPHIC`**, a name A §L6 explicitly retires ("A correct small claim beats a large unbuildable
> one") and B §1.1 row 21 also retires.

> **A §3.4 / §5.1.4:** `warrant ∈ {DETERMINISTIC, MODEL_EXTRACTED, DERIVED}` (a provenance lattice).
> **B §4.2:** `warrant -- MEASURED | MODELED | ASSERTED | UNCHECKED` (the *documentation* warrant key).

> **A §5.1.2:** `"provenance": "COMPUTED"` — "COMPUTED (by us) vs **DECLARED** (by the filer)."
> **B §4.2:** `provenance, -- COMPUTED | GATHERED`.

**A is right on all three.** `TEMPLATE_DIFF` is the method of the check both documents call
"predicate #1"; dropping it from the schema makes the design's own flagship undescribable. B's
`warrant` column confuses the corpus's documentation-warrant labels with the runtime provenance
lattice, and no rule composes `MEASURED` with `ASSERTED`. `GATHERED` is C2PA's word for a different
distinction.

**Replacement:** *`method` has nine values including `TEMPLATE_DIFF` and `DIFFERENTIAL`; `warrant ∈
{DETERMINISTIC, MODEL_EXTRACTED, DERIVED}` composing by weakest input; `provenance ∈ {COMPUTED,
DECLARED}`.*

### C9 — Two different `corpus_provenance` enums, and one is missing its most valuable member

> **A §L4 T3:** `corpus_provenance ∈ { SELF-AUTHORED, BLIND-FILLED, TEMPLATE-COMPUTED, REAL-PARTNER,
> PUBLIC }` — **five values, no register value** — while A's *own* rank-2b row calls the register "the
> only non-synthetic FFR in the design."
> **B §3.5:** `{SELF-AUTHORED, BLIND-FILLED, TEMPLATE-COMPUTED, REGISTER-DERIVED, REAL-PARTNER, PUBLIC}`
> **C §1.4:** "`REAL-REGISTER`".

**B is right on content; the spelling must be fixed once.** A's enum cannot express the one FFR the
project can measure today.

**Replacement:** *Six values, and the register value is spelled `REGISTER-DERIVED`.*

## Group II — The headline number does not agree with itself

### C10 — What is the denominator: cells or (field × obligation) pairs?

> **L14 §1.12 (MEASURED):** "THE FIELD SURFACE (unlocked, non-formula): **3747 cells** ← the
> denominator … UNION (280 predicates): 2373 (**63.3%**) … UNCHECKED residue: 1374."
> **A §5.1.2:** `"fieldSurface": 3747, "obligationsTotal": 41, "pairsTotal": 1187, "inScope": 973,
> "fraction": 0.6402`
> **B §4.4:** `"fieldSurface": 3747, "obligationsTotal": 41, "pairsTotal": 4021, "inScope": 3769,
> "coverageFraction": 0.6296`

Three denominators, three fractions, one measurement. **L14's is the only measured one.** A's
`1187` and B's `4021` are both incompatible with `3747 × 41`, with each other, and with 63.3%. A's
numbers are lifted verbatim from an **illustrative JSON block** in L10 (§1021–1022), which never
claimed to be a measurement.

**Replacement:** *The measured denominator is the 3,747-cell field surface; 2,373 cells are settled by
280 harvested predicates and 1,374 are declared unchecked. Any (field × obligation) pair model is
unbuilt: `obligationsTotal` and `pairsTotal` have no derivation anywhere in the corpus and must not
appear in a schema example until one exists (see G1).*

### C11 — Three different hero headlines, and A's is the number A condemns

> **A §4.6.4:** "` 0 failures across 555 checks. 7 properties were not checked.`" — and
> `"checksRun": 555`, `"predicatesReplayed": 555`, "*a coordinated 0.05% misstatement survives all 555
> checks*."
> **B §6.3 Screen 2:** "`12 failures across 2,373 checks. 1,374 fields were not checked.`"
> **C §5.1 step 2:** "`2,373 fields settled across 280 checks · 1,374 fields were not checked`."

**B is right on the form; C is right on the counts; A is self-refuting.** A's own §4.6.4 argues the
fraction must go *because* the 555-predicate enumeration is Goodhart-broken — and then renders 555 as
the shipping headline. Separately, C's step-2 hero shows no failure count for a filing C says has one
deliberately corrupted cell.

**Replacement:** *The hero is `<F> failures across <S> checks` and `<U> fields were not checked`, in
equal type, populated from the measured triple 2,373 / 1,374 / 3,747 — never from the 555 enumeration,
which exists only to demonstrate that the fraction is manipulable.*

### C12 — "coverage" vs "settled fraction"

> **A §3.1 (L7 row):** "**[!]** 'coverage' renamed **settled fraction**" — "'coverage' collides with
> conformal coverage three pages away"; A §5.1.2 emits `"settledFraction"`.
> **B** uses `"coverage"`, `"coverageFraction"`, "the coverage object", `GET /v1/coverage/history`,
> "coverage falls", throughout. **C** uses both interchangeably.

**A is right and its rename was not propagated.** B's own §2.1 conformal entry and §3.1 F5 use
"coverage" in the conformal sense on the same page.

**Replacement:** *The quantity is the **settled fraction**; the word "coverage" is reserved for the
conformal guarantee. Rename the JSON key, the API path and every screen label in one commit.*

### C13 — The 8.23% is attached to the wrong denominator

> **A §1.3:** "**1,692 of 20,562** EBA validation rules in release 3.5 deactivated at least once =
> **8.23%**"
> **B §0.3:** "EBA publishes ~**12,925** validation rules and has **deactivated 8.23% of them**"
> **C §3.1:** "EBA publishes **12,925** rule-instances (**8,052 distinct**)"

**A is right.** 8.23% of 12,925 is 1,064, not 1,692. B has performed exactly the denominator swap the
project sells against.

**Replacement:** *1,692 of the 20,562 validation rules in EBA release 3.5 have been deactivated at
least once (8.23%); 1,008 are still off, 343 of those at `error` severity. Separately, the EBA
publishes 12,925 rule-instances resolving to 8,052 distinct rules — do not divide one figure by the
other.*

### C14 — The absence claim's own denominator is disputed

> **A §1.8 and C §5.5:** "**21** vendor/product pages opened at primary URLs"
> **B §7.2 N1:** "Nothing in the **sixteen** commercial products opened…"
> **L12 adversarial #15 (QUALIFIED):** "'16 opened pages' does not reconcile with the lane's own Part 2
> tables… **That is 21 products, not 16**, and no stated rule."

**Neither is quotable.** The lane that produced the claim flagged its own denominator as
unreconciled. This is the corpus's rule-2 violation occurring inside the corpus's central novelty
claim.

**Replacement:** *Recompute the opened-vendor denominator under a written inclusion rule before any
absence claim ships; until then state "every vendor page opened in this research" and attach the list,
not a count.*

## Group III — The settling experiment is specified three different ways

### C15 — The pre-registered design, and the power table only supports one of them

> **A §L3 and B §3.4:** "n = 20, stratified … Stratum A (arithmetically closed, expected ≈12) …
> **retain L3 for Stratum A iff ≥ 6 of 12** survive … **delete for Stratum A at ≤ 3 of 12** … Power at
> n = 20, threshold ≥6: P(delete | p=0.15) = **0.933**; P(delete | p=0.35) = **0.245**."
> **C §1.1:** "**20 obligations in the arithmetically-closed stratum**, retain … iff **≥ 6** survive …
> **Delete L3 … if ≤ 2 survive**. 3–5 triggers exactly one pre-committed extension to **n = 40** with a
> threshold of ≥ 12."

**C is right and A and B are arithmetically impossible.** The quoted power figures are the binomial
tail for **n = 20**: P(X ≤ 5 | n=20, p=0.15) = 0.933 and P(X ≤ 5 | n=20, p=0.35) = 0.245. For n = 12
the same rule gives 0.995 and 0.739. A and B have kept C's power table while halving C's sample.

**Replacement:** *Stratum A contains 20 obligations (drawn until |A| = 20, Stratum B capped at 10, so
≈30 are drawn in total). Retain L3 for Stratum A iff ≥ 6 of 20 survive all five gates and the
surviving set beats B0 ∪ B1 ∪ B2 on marginal kill at equal FFR; delete at ≤ 2 of 20; 3–5 triggers one
pre-committed extension to n = 40 at a threshold of ≥ 12 and no further extension ever.*

### C16 — Four gates or five?

> **A §4.3:** "How a predicate is qualified — **the four gates**, in order" (T0–T3).
> **B §3.5:** "OFFLINE D — QUALIFICATION (L4). **Four gates.**" (GATE 0–3) — but **B §6.3 Screen 4**
> renders "the attrition funnel … generated → executed → fired → non-degenerate → FFR-admitted", which
> is five stages.
> **C §1.4:** "**The five gates.** An obligation survives iff at least one of its 20 candidates passes
> all five" (G0–G4), and C §3.2 T12 / §5.1 step 5 both show a "five-gate attrition funnel".

**C is right.** G1 (*executes without error, every key exists in the induced schema, `cells_bound >
0`*) is a separately-testable admission condition that A and B fold silently into T1 — and it is
precisely the condition whose absence produces the vacuous pass.

**Replacement:** *Qualification has five gates: G0 scope faithfulness · G1 executes and binds · G2
seeded-defect kill with marginal kill over the baselines · G3 non-degeneracy · G4 false-failure rate.*

### C17 — Two different admission thresholds for the same gate

> **A §L4 and B §3.5:** "admit iff `K/O ≥ 0.80` on the fault classes the predicate *claims* to cover"
> **C §1.4 G2:** "`K/O > 0` on **observable** seeded defects, **and** marginal kill strictly greater
> than `B0 ∪ B1 ∪ B2`"

These are not the same test and the documents do not say they are different tests. A predicate at
`K/O = 0.05` survives C's experiment and fails A's registry.

**Replacement:** *Experiment E6 asks "can this candidate fire at all and does it beat the free
baselines" (`K/O > 0` plus marginal kill); the registry admits at `K/O ≥ 0.80` on the claimed fault
classes. State both, and report the two attrition numbers separately.*

## Group IV — Component decisions taken in opposite directions

### C18 — Structured output: outlines/XGrammar or provider-native?

> **A §L2b component table:** "**Decision: outlines / XGrammar** (both Apache-2.0…). *Alternative it
> beat:* **Provider-native JSON mode** — **UNVERIFIED** what is *guaranteed* versus *best-effort*, and
> that difference is exactly the hard guard."
> **B §1.1 row 24:** "**Decision: Provider-native structured outputs** (`output_config.format`) on
> Anthropic models… Runner-up: `outlines` / `XGrammar` … they **require a local model**."

Directly opposite decisions on the same component, each rejecting the other for a reason the other
does not answer.

**Replacement:** *L2b uses provider-native structured output with `key` typed as
`Literal[*L1_KEYS]`, plus the post-hoc deterministic key check, because no local model is in the
stack; `outlines`/`XGrammar` becomes primary the day an open-weight model enters the L2b path. Record
that whether provider-native constraint is guaranteed or best-effort is UNVERIFIED, which is why the
post-hoc guard is not optional.*

### C19 — `cobalt`: adopt or reimplement?

> **A §L1b component table:** "**Decision: Docling → Akoma Ntoso**, `eId` per clause, FRBR URI per
> instrument…, **`cobalt` for URI handling**."
> **B §1.1 row 8:** "**Implement `cobalt`'s URI grammar ourselves (~100 lines) unless its licence
> clears** … GitHub reports **NOASSERTION**… the lane did not open the LICENSE files."

**B is right** (L08 §1050: "Indigo / cobalt licences. GitHub reports `NOASSERTION`. I did not open the
LICENSE files").

**Replacement:** *Implement the FRBR URI grammar in ~100 lines; adopt `cobalt` only if someone opens
its LICENSE and it is permissive. `bluebell` is GPL-3.0 (verified) and must never be linked.*

### C20 — Licence warrants asserted at three different strengths

| Component | A says | B says | Lane says | Who is right |
|---|---|---|---|---|
| **Z3** | "**Z3 (MIT)**" flatly (§L4 T2, §4.2) | "MIT (SECONDARY; the LICENSE file was not opened by any lane)" | L09 §406: "Licence: MIT (**SECONDARY**)" | **B** |
| **Hypothesis** | "**Hypothesis (MPL-2.0)**" flatly (§L6) | "licence **NOT VERIFIED** by any lane… this ledger does not assert a licence nobody opened" | L06 §426: "MPL-2.0, mature \| **SECONDARY (licence not re-read)**" | **B on the caution; the lane's label is SECONDARY, not NOT-FOUND** |
| **in-toto / DSSE** | "it is **Apache-2.0**" (§5.1.1, §L7) | "**UNVERIFIED** — not re-checked live" (§2.2, §8.1) | L10 §699: "`in-toto/attestation`: 361★, **Apache-2.0** (`LICENSE`: 'Copyright 2021 in-toto Developers… Apache License, Version 2.0')" | **A** — the LICENSE *was* opened |

**Replacement:** *Z3 — MIT (SECONDARY, LICENSE unopened). Hypothesis — reported MPL-2.0 (SECONDARY,
LICENSE not re-read). in-toto/DSSE — Apache-2.0 (VERIFIED-AT-SOURCE, LICENSE read verbatim by L10);
delete it from the "licences not read" table in B §8.1.*

### C21 — Who signs the attestation: decided or open?

> **A §5.2:** "**Decision: the filer signs, with a detached key, over the report JSON.** The vendor
> signs nothing about the filing."
> **B §8.3:** "Things this section deliberately does not specify: **Who signs the attestation** … the
> signer question needs an explicit decision before L7 ships, and it is a legal decision."
> **C R18:** "**Who signs the attestation** is undecided … Early-warning signal: **Nobody has raised
> it yet.** Status: **OPEN — M5 gate**."

**A is right that a decision is needed and its decision is the right one; C is factually wrong that
nobody has raised it** — A raised it and answered it two documents earlier.

**Replacement:** *Decided (A §5.2): the filer signs with a detached key; the vendor appears only as
`assessor.id` with `thirdParty: false`. The residual open item is legal review of that decision, not
the decision itself. Close R18 to "decided, pending legal review" and delete the line from B §8.3.*

### C22 — The pervasiveness policy ships two different parameter sets

> **A §5.1.2:** `"pervasivenessPolicy": { "version": "v2", "K": 3, "T": 0.35, … }`
> **B §4.6:** `"verdict": { …, "policy": { "K": 3, "T": 0.45, "version": "1.1" } }`

Different `T`, different policy version, both presented as the published parameter. Neither has a
basis anywhere in the corpus.

**Replacement:** *Ship one policy file, `pervasiveness-policy-v1.json`, with `K` and `T` set by a
stated argument and versioned in the attestation; until that argument exists, both numbers are
placeholders and must be labelled `PLACEHOLDER` in every example.*

## Group V — Smaller but load-bearing

### C23 — The supervisor is deleted as a user, then keeps appearing

> **A §1.2:** "**Decision: the buyer is the filer's compliance officer. The supervisor is deleted as a
> user.**"
> **B §6.1:** "`GET /v1/runs/{run_id}/items` … **This is what a supervisor's triage tool consumes**";
> B §6.3 heading: "**Who the two surfaces are for**"; A §4.6.1 itself: "the override count is reported
> separately — **a supervisor will want it**."

**Replacement:** *The supervisor is not a user and not a buyer; the supervisor is why the filer cares.
Where a surface happens to be useful to a supervisor, say "a downstream reviewer", and delete "the two
surfaces" framing from B §6.3.*

### C24 — Section A's own closing cross-reference is inverted

> **A, final line:** "The predicate registry schema, the qualification harness and the report renderer
> are specified for build in **Section C**; the experiment queue and its pre-registered thresholds are
> in **Section B**."

The experiment queue is **Section C §2**; the registry schema and data model are **Section B §4**.

**Replacement:** *"The data model, the stack and the flow are in Section B; the experiment queue,
the dated plan and the deliverable are in Section C."*

### C25 — "Fifteen outputs" vs fourteen runs

> **A §1.1:** "nothing in any of the **fifteen** outputs distinguished the calibrated run from the
> uncalibrated ones" — in the same paragraph as "**nine of fourteen complete** frontier-model runs".

L02 §B.1 lists exactly **14 complete runs**, with one incomplete Gemini 2.5 Pro run excluded for
40/108 gateway failures.

**Replacement:** *"…nothing in any of the fourteen complete outputs distinguished the calibrated run
from the uncalibrated ones."*

### C26 — Register enumeration cost

> **A §L0:** "one `GET DirectoryGetList` with `PageSize=2100` (**2,005 records**, ~3.4 MB, one
> request) **+ `GET DirectoryDetailGet?EncryptedId=…` per entity**"
> **B §5.4 / §8.1:** "A full refresh is ~**2,235 polite GETs**."

2,005 + 1 = 2,006. Either the detail sweep is not per-entity or 2,235 counts something else; neither
document says which.

**Replacement:** *State the fetch plan as `1 list request + N detail requests where N = |records|`, and
report the actual request count of the run that produced the snapshot hash.*

### C27 — Cellbreak date

> **A §L0:** "the Grist 'Cellbreak' escape (`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, **disclosed 21 Jan
> 2026**)"
> **B §1.1 row 32:** "(`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1, **patched 20 Jan 2026**)"

**Replacement:** *Quote one date with one verb, or quote neither — the advisory ID carries the fact.*

### C28 — Population figures that do not add up

> **B §0.2:** "**229 live FMEs / 390 schemes / 650 Fund-Management register rows** (L08 §C.2)"
> **A §1.2:** 650 register rows; 229 live FMEs by sub-category (22 + 194 + 13); no 390.
> **L15 §5:** of the same 650, "**365 scheme-like, 285 entity-like**" (INDICATIVE, regex split).

229 + 390 = 619, not 650, and A never carries the 390.

**Replacement:** *Quote only what a single instrument returned: "650 Fund Management register rows as
at 10 Aug 2026, of which 229 resolve as live FME registrations." Do not publish a scheme count from
the register until the split rule is written down.*

### C29 — "The two-day build is already built" vs the status labels

> **C §0 finding 1:** "**The two-day build is already built.** L1→L5 runs end-to-end… **M**"
> **B §3.1 status labels:** F1 SPECIFIED · F2 **PARTIALLY BUILT** · F3 SPECIFIED · F5 SPECIFIED/GATED ·
> F6 SPECIFIED · F7 SPECIFIED · F9 SPECIFIED · F10 SPECIFIED · F11 **BUILT (denominator) / SPECIFIED
> (closure)** · F12 SPECIFIED · F13 PARTIALLY BUILT · F14 SPECIFIED.

**B is right.** What is built is L1 induction, predicate harvest, arithmetic evaluation and the
denominator. Template binding, pre-flight, closure, canaries, relations and `verify` are not.

**Replacement:** *"Schema induction, predicate harvest, arithmetic evaluation and the coverage
denominator are built and reproduce in ~30 ms. Template binding, pre-flight, closure, canaries,
attestation and `verify` are specified and not built."*

### C30 — The `.external_source_lacks_field` example is the refuted lane finding

> **B §4.5:** "`.external_source_lacks_field` … **measured live: the register LIST endpoint returns
> RegistrationNumber = null on 650 of 650 fund rows**"
> **A §1.7 and §1.5 instance 4:** the claim "the IFSCA register does not resolve registration numbers"
> is **REFUTED** — "228 of 228 live FMEs resolve via `DirectoryDetailGet?EncryptedId=…`".

B's reason-code example is true of the list endpoint and reads as though the register lacks the field.
It is the sentence that produced the corpus's fourth silent false negative.

**Replacement:** *"`.external_source_lacks_field` — the external source structurally does not carry
the field. Our own near-miss is the canonical illustration and not an instance: the register's **list**
endpoint returns `RegistrationNumber = null` on 650 of 650 rows while its **detail** endpoint returns
it on 228 of 228."*

### C31 — The second settling experiment has fallen out of the plan

> **A §1.9 and §6.6:** "**the two calls that would settle that are one email and one phone call, both
> unrun, both ranked joint-first**" — the IFSCA email, and the question to KFin/CAMS/Basiz about a
> written house NAV tolerance.
> **C §2 E1 and §3.3 M0:** only the IFSCA email appears. The administrator call is nowhere in the
> queue, the milestones or the risk register.

**A is right that both are live.** A §1.6.6 demoted the NAV wedge but A §1.9 still lists the
administrator call as one of the two observations that would change the pitch.

**Replacement:** *Either add the administrator call to M0 as E1b with its exact question text, or
record in A §1.9 that the NAV-tolerance question was retired with the NAV wedge and is no longer a
killer. Do not leave it ranked joint-first in one document and absent from the other.*

---

# 2. SURVIVING FALSEHOODS — delete these

**This section is exhaustive against the withdrawal registers in `RND-BRIEF` Part 8, A §1.7, B §0.3
and C's `REF` marks. Every banned string was grepped across all three sections.**

**Clean — verified absent outside the withdrawal registers themselves:** *"46% staffing"* · *"84
numeric / 15 date fields"* · *"35 data validations, only 3 list-type"* · *"Fifth Schedule Part A(g)"*
(zero occurrences anywhere) · *"the registry grows monotonically"* · *"two model calls, both short"* ·
*"zero financial regulations encoded anywhere"* · *"no analogue exists for a financial assertion"* ·
*"no measured system can say clean"* · *"a 90%-per-step agent is 57% reliable"* · *"PASC names
financial documents as a target"* · *"the sandbox is a nearly empty room"* · *"95%+ of AML alerts are
false positives"*. **These are correctly dead.** The nine below are not.

### F1 — `505 + 35 + 15 = 555` uses the refuted validation count · **A §3.0 F9, §4.6.4, §L6.5, §5.1.2**

> **A §4.6.4:** "one predicate per formula cell, per validation, per vocabulary — **505 + 35 + 15 =
> 555**"; **A §3.0 F9:** "per validation (**35**) … takes 17/24 = 71% to **555/562 = 98.8%**".

**35 is the namespace-blind validation count.** A §1.7 itself, B §0.2 and B §0.3 all record the
correction: **54 validations (35 main + 19 `x14`), 22 list-type, 20 resolving**. The design's single
most-repeated pitch asset is that a parser reporting 35 is the failure the product exists to prevent —
and the Goodhart arithmetic is built on 35.

**Delete every occurrence of `555` and `562`.** The correct enumeration is **505 + 54 + 15 = 574**, and
the illustration becomes **574 / 581 = 98.8%** (the point is unchanged; the number was wrong). This
also deletes `"checksRun": 555`, `"predicatesReplayed": 555` and "*survives all 555 checks*".

### F2 — "+37–54 percentage points of **functional equivalence**" · **A §L3, B §3.4, C §1.4**

> **C §1.4:** "the single measured intervention that most improves this exact task … **+37 to +54
> percentage points** of **functional equivalence**"

**L04 §2.13 (VERIFIED-AT-SOURCE):** "**I/O constraints give the dominant gain: +37–54% structural
similarity over baseline**" and, separately, "**Outcome evaluation: generated models match the gold
standard on 51–53% of test scenarios**" — and the paper's own caveat, quoted in the lane: *"structural
similarity does not guarantee outcome equivalence, and vice versa."*

**Delete "functional equivalence" from the +37–54 sentence.** Replacement: *"Feeding an induced
schema in as an explicit I/O constraint is the dominant lever on **structural similarity** (+37–54%)
in the only published study of statute→executable-model generation (arXiv:2604.17153); that study's
**outcome** equivalence tops out at 51–53%."*

### F3 — "Hypothesis (MPL-2.0)" asserted as fact · **A §L6 component table**

L06 §426 marks the licence **SECONDARY, "licence not re-read"**; B §8.1 lists it as unread. Delete the
bare parenthetical; write "reported MPL-2.0, LICENSE not opened".

### F4 — "Z3 (MIT)" asserted as fact · **A §L4 T2, A §4.2, B §1.1 row 16**

L09 §406 marks it **SECONDARY**. B's own ledger refuses to assert it. Delete the bare "(MIT)" from
the decision tables and carry "(MIT, SECONDARY — open the LICENSE before shipping)".

### F5 — "in-toto / Sigstore — UNVERIFIED" · **B §2.2, B §8.1**

The inverse error. L10 §699 **opened the LICENSE and quotes it verbatim**. Delete the row from B's
"licences not read" table; the correct label is VERIFIED-AT-SOURCE, Apache-2.0.

### F6 — "sixteen commercial products opened" · **B §7.2 N1**

L12's own adversarial pass #15 marks the "16 opened pages" denominator **QUALIFIED — does not
reconcile with the lane's own Part 2**, and counts 21 with no stated inclusion rule. Delete both `16`
and `21` from every absence claim until the rule is written and the count recomputed. (See C14.)

### F7 — "EBA … deactivated **8.23% of ~12,925**" · **B §0.3**

Arithmetically false: 8.23% belongs to 20,562. Delete the pairing. (See C13.)

### F8 — The bare phrase "the 17 decidable predicates" · **A §4.2 (×2), A §4.2.3, B §1.2(a), C §1.4**

> **B §0.3, its own ban list:** "*'17 of 24 predicates are script-settleable'* → **15 exact + 2
> approximate.**"
> **B §1.2(a):** "13 of **the 17 decidable predicates** are pure expression evaluation."
> **C §1.4:** "Four of **the seventeen decidable predicates** need capabilities CEL lacks."

The banned figure survives in all three sections, including in the document that bans it. **And its
stated justification is dead:** A §3.0 F9 explains the "2 approximate" as "register resolution is a
**fuzzy name/number match**" — which is L15's finding, and L15's premise ("the register does not
resolve registration numbers") is listed as **REFUTED** in A §1.7.

**Delete the bare "17 decidable" everywhere.** Replacement: *"the 24 candidate correctness predicates,
of which 15 are exactly settleable, 2 are settleable only after a declared normalisation (NFKC,
`U+2011 → U+002D`, strip, case-fold) that carries its own measured false-failure rate, and 7 are not
settleable from the artifact at all."*

### F9 — PROVE rows marked VERIFIED-AT-SOURCE when only the abstract was read · **A §6.1 (two rows)**

> **A §6.1:** "Deterministic adjudication of LLM output for a regulatory submission | **PROVE**,
> arXiv:2607.28218 | **VERIFIED-AT-SOURCE**" and "Fault-injection evaluation with paired clean/dirty
> packages | PROVE: 10 replicates × 15 injected discrepancies | **VERIFIED-AT-SOURCE**"
> **A §6.4 3c, same document:** "*(Its full text was **not read** — only the abstract.)*"

The two quantitative facts *are* in the abstract (L12 quotes it), so they survive — but the **negative**
claims A and B make about PROVE ("**no admission gate**", "**no relation layer**", "nothing prevents a
validator with a terrible FFR from being in the set") are absence claims about a paper nobody opened,
made without a positive control. Under this corpus's own rule 2 they are inadmissible.

**Replacement:** *Relabel both rows **ABSTRACT-ONLY**. Downgrade every PROVE absence claim to
"**not visible in the abstract; the full text is unread**" until E13 opens it — and open it before the
pitch, because a coverage table in PROVE's implementation section would narrow N3.*

---

# 3. UNWARRANTED CONFIDENCE

### U1 — 63.3% is a **pre-gate** number, and the product's own rule says none of those predicates is admissible

All three sections lead with "63.3% of 3,747 fields settled by 280 predicates". All three also state
that **"a predicate whose `qualification` block is absent does not load"** and that **an FFR whose
corpus provenance is `SELF-AUTHORED` is "not a number"**. No blind-fill corpus exists. No FFR has been
measured for any of the 280. Therefore, under the specification's own admission rule, **the currently
admissible predicate set is empty and the currently defensible settled fraction is 0%.**

Worse, L14 §1.12 records the composition: **2,329 of the 2,373 settled cells (98.1%) come from the 53
validation predicates, not the 227 arithmetic ones** — and L14 adds the caveat that "the 62.2% carried
by validation predicates is *weaker per cell*… some are near-vacuous." G3 exists to reject exactly
those. A judge who connects the gate to the headline gets to say the product failed its own test on
stage.

**Corrected phrasing, and it is stronger than the current one:** *"280 predicates are mechanically
derivable from the regulator's blank template with no model, and they touch 2,373 of 3,747 filer-
editable cells. **None of them is admitted yet**, because no one has measured a false-failure rate for
them on a corpus we did not write. That is the point: the number you are looking at is what every
compliance product ships, and it is the number our own gate is designed to refuse. Watch what happens
to it after qualification — that delta is the product."*

### U2 — "L1→L5 runs end-to-end" overstates what is built

See C29. **Corrected:** *"schema induction, predicate harvest and arithmetic evaluation run end-to-end
in ~30 ms; the verdict model, closure, canaries and attestation are specified and unbuilt."*

### U3 — "Zero model calls in the verdict path" is a design property, not yet an enforced one

A calls it "enforceable as a CI assertion"; B lists `test_no_model_in_verdict_path` as a build gate; C
lists it as acceptance criterion A6. All three then state it in the present tense as a property of the
system. **Corrected:** *"The verdict path is specified to make zero model calls, and the assertion is
listed as a build gate; the gate is not yet written."*

### U4 — The FinVerBench evidence is one 37-page single-author unreviewed preprint with unreleased code

C's R12 says exactly this and marks it **"RETIRED by L02, action pending"** — the action being "add a
Warrant column naming the paper so a reader can see rows 1–5 are one instrument". **A §1.1's headline
table does not do it.** F1, F3, the 65.4/66.2 comparison's neighbour rows and the rounding-artifact
finding all trace to `arXiv:2605.29586` (Silu Panda, single author, no institutional affiliation,
n = 43 clean, code not released in v1). **Corrected:** attach "(FinVerBench, arXiv:2605.29586 —
single-author preprint, not peer-reviewed, artifacts not released in v1, n = 43 clean)" to the first
occurrence, and never let two rows sourced from it read as two independent measurements.

### U5 — "0% FPR" from FinVerBench is true by construction and the design knows it

A §3.0 F3 records that the rule verifier's 15 relations are *"guaranteed consistent in our clean data
by construction"*. The same construction applies to Claude Sonnet 4's 0.0% FPR on the 43 clean
instances that A §1.1 uses to refute the brief's headline. The refutation still stands — a run *was*
calibrated — but **"calibration is achievable" is measured on a clean set built to satisfy the
checks.** Say so in the same sentence.

### U6 — "The residue set … a third party can re-run it and get the same answer"

The residue depends on a **human INNOCUOUS/WRONG adjudication** (B §3.9 step 3, "the only human
step"). B §7.2 N4 concedes this; A §6.2 N4 and C §5.5 N3 do not. **Corrected:** *"reproducible given
the published fault model **and the published adjudication record**, both content-addressed."*

### U7 — "17 of 24 → 555/562 = 98.8% in an afternoon" is asserted as measured

Marked **M** in C §0 finding 4 and stated flatly in A. It is an *enumeration argument*, not a run: no
one generated 555 predicates and measured 98.8%. **Corrected:** label it **DERIVED (an enumeration
argument, not a run)** — and fix the arithmetic per F1.

### U8 — "The gate demonstrably does real work" rests on one worked example

Both A §L4 T2 and B §3.5 GATE 2 cite the ALR `−1e17` bounds. That is one workbook, one predicate class,
five predicates. **Corrected:** *"the gate has one demonstrated rejection: five of ALR's six bound
predicates assert only `≥ −1e17` over 1,428 cells and are refused. Whether it rejects anything on the
FME workbook is unmeasured — 19 of 24 FME bounds are a real `≥ 0`."*

### U9 — "the register is clean by definition"

A §L4 rank-2b: "the live register is public… and it is **clean by definition** — every entity in it is
validly registered." That licenses an FFR for the *membership* predicate only. It says nothing about
whether the register's **strings** are correctly formatted, which is the thing the 38.2% measures.
**Corrected:** *"every entity in the register is validly registered, so a predicate asserting
membership cannot have a true positive there; a predicate asserting *format* can, and 87 of 228
registration numbers fail the obvious regex."*

### U10 — τ-bench `pass^k` is quoted with a denominator in A/C and without one elsewhere

A §3.0 F7 carries "**τ-retail only, n = 115**; τ-airline never reaches 60% at k=1"; C §4 row 1 carries
"τ-retail (n=115)". B §7.3 and B's summary drop it. **Corrected:** the denominator travels or the
figure does not.

### U11 — "Coverage is a per-template property and must never be averaged" — then it is averaged

B §0.1 and C §5.3 both publish "**515 executable predicates across nine workbooks**" as a headline,
next to the rule that per-template coverage must never be averaged. 515 is a sum, not an average, so it
is legitimate — but it sits beside "two of the nine have zero formulas and one has zero validations
too", which means the 515 is concentrated. **Corrected:** always publish 515 with its per-workbook
distribution attached, never alone.

---

# 4. GAPS — what blocks an engineer on day one, and what only the user can answer

## 4.1 Blocking on day one

| # | Gap | Why it blocks | Smallest thing that unblocks it |
|---|---|---|---|
| **G1** | **What is a `pair`, and how is `pairsTotal` computed?** The closure invariant, the settled fraction, `DISALLOW *` and the attestation's `scope` object are all defined over `(field × obligation)` pairs. `obligationsTotal: 41` and `pairsTotal: 1187` are copied from an **illustrative JSON block in L10**; B invents 4021; the only measured quantity is a **cell** count (2,373 / 3,747). | You cannot write `test_closure` without knowing what it closes over. | Decide: either the unit is the **cell** (matches every measurement, and the "obligation" becomes a predicate attribute) or the unit is the **pair** and someone must publish the rule that enumerates obligations. Write it before T4. |
| **G2** | **What FFR threshold makes a predicate `ADVISORY` rather than `BLOCKING`?** All three sections say severity is "set by the measured FFR, not by taste". No number is given anywhere. | `severity_tier` is a required column. | Pre-register one number with the admission thresholds: e.g. `FFR ≤ 0.02 ⇒ BLOCKING; 0.02 < FFR ≤ 0.10 ⇒ ADVISORY; FFR > 0.10 ⇒ not admitted`. Any defensible number beats none. |
| **G3** | **Money scale.** A says "**integer micro-units**" in five places (§2.2, §L1 `scale: micro_units`, §3.1, §4.2.2, §4.2.4). B row 12 defines "**`int64` count of 10⁻³ USD Million (1 unit = USD 1,000)**, `12.34 → 12340`, half-ulp = 5 units, `τ(n) = 5n`". Those differ by 10³, and every tolerance in the design is expressed in units. | Pick wrong and every arithmetic predicate's tolerance is off by a thousand. | **B's definition is the operative one.** Delete the word "micro-units" from A and call it `MILLI_USD_MILLION` (= USD 1,000) everywhere, including the `Field.scale` enum. |
| **G4** | **The state/reason vocabulary is not one vocabulary** (C1, C2, C4–C7). The build plan (C §3.2 T4) targets 7 states / 19 codes; the data model (B §4.2) requires 8 / 30. | `run_item.state` and `reason_code` are database columns. | Freeze B's 8 × 30 as normative, regenerate A §4.6 and C T4 from it, and add the six-code→thirty-code mapping table to the frozen version. |
| **G5** | **Where does the `applicable`-false / raise / budget-exceeded mapping live?** Three sections give three answers (C4, C5). | It is the five-line evaluation contract at the centre of L5. | Publish one `EVALUATION-CONTRACT.md` with the five rules and their state+reason pairs, and make it the only place the contract appears. |
| **G6** | **Nothing specifies how an "obligation" is bound to a field.** Predicates carry `clause{eId, span}` and `schema_keys`, but the report keys items as `"intro.tbl15.row[3].scheme_type × reg27(1)"` — a join nothing constructs. | The report's primary key. | Define `pair_id = (stable_key, obligation_id)` and state where `obligation_id` comes from — L1b clause `eId`, or a hand-maintained obligation table. L1b is **entirely unbuilt** (B §3.3: "Status: SPECIFIED. Nothing of L1b is built"), so the honest day-one answer is a hand-maintained table. |
| **G7** | **The five gates' order and ownership vs the four gates' order.** C runs G1 (executes and binds) before G2; A runs T2's proof arm before T1's empirical arm. Both cannot be "the order". | The harness is a pipeline. | One ordering: **G0 (free) → G1 (free) → G3 proof arm (cheap) → G2 (expensive) → G3 empirical arm → G4**. Write it once. |
| **G8** | **`test_constants` asserts numbers two documents disagree about.** C §3.1 (Tue 12 Aug) and B §6.4 both list the pinned constants, and both include **`280` predicates** — a number that will change the first time G3 rejects one. | A regression test that fails on correct behaviour gets deleted. | Split it: `test_schema_constants` (505/294/211/54/22/20/252/3747 — properties of the file) and `test_harvest_count` (280/515 — a property of our code, allowed to move with a recorded reason). |
| **G9** | **No repo licence decision.** C §3.1: "a public repo, **MIT or Apache-2.0**". | It is the first file created. | Apache-2.0 — it carries a patent grant, and every core dependency chosen (celpy, in-toto, PaddleOCR, crepes/MAPIE via BSD) is compatible. Decide on 11 Aug. |
| **G10** | **Who is Person A?** The blind-fill firewall (E8, M2) requires ≥30 clean workbooks filled by someone who has never seen the predicate set, and the team is ≤4 people, all of whom have. | M2's acceptance test, and every FFR in the product. | Name Person A on 11 Aug, or commit to the audited second-model-instance route with the fill prompt hashed and published before the first workbook is filled. |
| **G11** | **The residency plan has no owner map.** M1–M5 span 8.5 weeks with 12 human-required decision points (B §3.10) and no allocation. | Two of the milestones (M2 corpus, M4 residue adjudication) are human-time-bound, not compute-bound. | One table: milestone × person × hours. |
| **G12** | **`verify` byte-identity is asserted against an unpinned toolchain.** B §4.7 pins eight things including `tool_versions: {python, lxml, openpyxl, celpy, libreoffice, z3}` — but LibreOffice is invoked as a subprocess and its output is the thing B §1.1 row 3 says has an **uncharacterised one-validation loss**. | A7 ("re-derives byte-identically on another machine") is the programme's acceptance test. | Either exclude LibreOffice from the verdict path entirely (it is currently a *cross-check*, so this is free) or pin it by container digest. State which. |

## 4.2 Questions only the user can answer

1. **Is the application portal live, and does the form match the recorded spec?** C R1: WebFetch to
   `giftifih.getkruu.com/apply` returned **HTTP 404** and the root served only an SPA shell. Nobody in
   this corpus has seen the live form. Applications close **16 Aug**. C schedules the check for 11 Aug
   and the submission for the morning of the 16th — a zero-slack plan against an unverified portal.
   **This is the only item that can end the programme, and it costs ten minutes.**
2. **Does IFSCA already run these checks on receipt, and how often is an FME filing returned for
   correction?** (E1 — one email. Both A and C rank it joint-first; it is unrun.)
3. **Does a fund administrator serving GIFT IFSC (KFin / CAMS / Basiz) have a written house NAV
   tolerance?** (A §1.9's second killer; missing from C's queue entirely — see C31. Decide whether it
   is still live.)
4. **Who is on the team, and is anyone eligible to be Person A?** (G10; also the ≤4-member cap and the
   under-29 / Indian-institution eligibility test.)
5. **Are you willing to submit on 15 Aug rather than 16 Aug?** The plan has no slack against a portal
   that returned 404.
6. **If E6 returns k = 0, do you still want to run the residency as specified?** The plan says yes and
   funds it; that is a commitment only the user can make, and it should be made before M1, not during.
7. **Is anyone prepared to sign the attestation?** A decides "the filer signs" — which means a real
   FME must exist and consent. Until then the demo signs nothing real, and the demo script should say
   so.

---

# 5. THE INNOVATION CHECK — what got sanded off

Three genuinely novel things were narrowed past the point of accuracy in the name of defensibility.
Each should be restored, in a form that is both bolder and *more* true than the hedged version.

### I1 — RESTORE: the **undetectable-in-principle** mutant class

**What was sanded.** The residue set is now presented (A §6.2 N4, C §5.5 N3) as "which falsehoods
survive every check we have" — a statement about *our* check set, and therefore a statement about our
incompleteness. But the corpus contains a strictly stronger claim, stated once in A §L6.5 and once in
B §3.9 and then dropped from every novelty ledger:

> "In code mutation testing, a mutant that changes behaviour is in principle killable by *some* test.
> Here, a mutant can change the *truth* of the artifact and be **provably unkillable by any predicate
> over the artifact alone**."

That is not a coverage gap. It is a **theorem about the artifact class**, and it is the only thing in
the corpus that answers the brief's §2.4 structural finding with a construction rather than a
classification.

**Restore it as, and this is both bold and true:** *"A prescribed return is a closed arithmetic system.
We can construct, and exhibit, a family of filings that are internally perfect under every relation the
regulator's own template encodes and every relation we have added — and materially false. That family
is non-empty by construction, its size is measurable, and measuring it is the first quantitative
statement anyone has made about the limit of document-level verification for a regulated filing."*
The risk register's R9 ("the residue set is empty") is then correctly graded **Low → structurally
impossible**, which C already argues and then does not use.

### I2 — RESTORE: `INVALID` as a **liveness proof**, not a self-check

**What was sanded.** N5 is written defensively — "the nearest named prior art is SRE synthetic
monitoring and hardware built-in self-test", and A adds "*a formal-methods citation for vacuity
detection is UNVERIFIED and must not be asserted*". Both true. But the hedging buried the actual claim,
which is not "we self-test" — every system self-tests — it is **the verdict is conditioned on a proof
obtained from the artifact under test, in the same execution, and is withheld when that proof fails.**

**Restore it as:** *"No assurance artifact in existence carries evidence that the instrument that
produced it was working on the specific document it examined. A clean audit opinion does not. An SBOM
does not. A validation report does not. Ours refuses to issue a verdict unless every check has just
demonstrated, on your file, that it can still catch the fault it was admitted for."* That sentence is
falsifiable, is not a novelty claim about a mechanism (two extra executions per predicate), and needs
no citation.

### I3 — RESTORE: the criterion-source substitution, honestly downgraded but not deleted

**What was sanded.** The brief claimed "statutory text + the template's own formulas — an
**authoritative** criterion source rather than an inferred one". A and B correctly downgrade
"authoritative" to "**available**" (D17's COUNTIF gap proves it). But the downgrade swallowed the
actual novelty, which survives intact: **SPADE mines prompt-version history because in a software
pipeline nothing else records what "correct" meant. A regulation has no prompt history — and it does
not need one, because the criterion is published, dated, versioned, and amendable by an authority that
publishes its amendments.**

**Restore it as:** *"SPADE infers what correctness meant from the traces of a developer changing their
mind. We do not have to infer it: the criterion is a published instrument with a version, an amendment
chain that is machine-followable in 76 of 82 cases, and a blank template with a content hash. The
criterion source is not more *authoritative* than SPADE's — the regulator's own template computes a
scheme total that misses two of its own nine legal values — it is **citable, versionable and
watchable**, which is what lets a predicate be tied to a clause, re-qualified when the clause moves,
and quarantined the day a circular changes the rule."* That is the claim the instrument-stream watcher
implements, and no section currently states it as a novelty.

### Checked and correctly *not* restored

- **"We remove the green tick."** Correctly kept, correctly mechanised (schema prohibition + CI grep +
  a verdict state literally named `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE`). Nothing sanded.
- **"Measurement is the admission condition."** Correctly narrowed to "the quantified, per-rule,
  published version of a discipline the XBRL DQC already practises qualitatively". That narrowing is
  right and must not be un-narrowed.
- **The NAV-error regime.** Correctly deleted (five independent measured reasons). Do not restore.
- **L6's five metamorphic relations.** Correctly deleted. Do not restore.
- **"The verification problem and the capability problem are the same problem."** The brief's sharpest
  sentence, and it survives nowhere in A, B or C. It is not restorable as written — L4's seeded-defect
  labels are precisely the counter-example — but its corrected form is worth one line: *"where a
  programmatic oracle exists we do not need a model; where it does not, we manufacture labels by
  seeding faults rather than by asking one."*

---

# 6. EXECUTIVE VERDICT

**The problem.** Every quarter, 217 fund managers licensed at GIFT City return a spreadsheet the
regulator publishes. The only thing in it resembling a verdict is a Yes/No box in which the manager
attests that its own valuations comply; nothing in the other 6,756 cells can contradict it. That is a
green tick with no denominator. It is also the general case: an audit opinion, a filing sign-off and a
sanctions disposition all end in *nothing wrong here*, and none of them says what was looked at. The
scarce quantity is not error detection. It is an attributable, per-check, measured statement of how
often that check is wrong, carried next to the finding it produced, together with a computed
declaration of what was not touched. No product opened in this research prints either.

**What we are building.** A checker for a prescribed regulatory workbook that reports what it did not
check. It induces the field graph from the regulator's *blank* template — 505 formula cells, 54 data
validations, a 3,747-cell filer-editable surface — harvests 280 executable predicates from what the
template already encodes with no model, and admits a predicate to the active set only after measuring
its kill rate against seeded defects, proving it is not the flag-everything baseline, and measuring its
false-failure rate on a corpus its authors did not write. Every filing gets a signed report with two
counts of equal weight, a typed reason for every unsettled property, each firing check's own error
rate, and a replay proving the checks were alive on that document. There is no field in the schema
where a downstream consumer could write "pass".

**Why it works.** Each part alone is defeated by a measured fact, and each part's failure mode is
another part's input. SPADE's own paper says its false-failure rate cannot be computed because the
example universe is unknown; seeded defects manufacture that universe with certain ground truth. Seeded
defects say nothing about properties with no oracle; differential relations over the workbook-as-program
settle some without one. Relations can be trivially true; the degeneracy gate rejects them — it already
rejected five real bound predicates that assert only "this is a number" over 1,428 cells. And the whole
thing runs in 30 milliseconds with zero model calls on the verdict path, so reliability does not decay
over steps.

**What could kill it.** Four things, in order. **One:** the application portal returned HTTP 404 and
nobody has seen the live form; applications close on 16 August. **Two:** IFSCA may already run these
checks on receipt, which makes the filer-side product a convenience — one email settles it and it is
unsent. **Three:** the headline 63.3% is computed from 280 predicates of which **none is admissible
under our own gate**, because no false-failure rate has been measured for any of them; a judge who
connects those two facts wins. **Four:** the method may not transfer past one workbook, and nine are
already on disk to find out.

**What to do first.** Open the portal in a browser and screenshot every field. Send the IFSCA email.
Then run the transfer measurement, which needs no model and no corpus. The settling experiment costs
nine dollars and belongs after all three, because it can only tell us how big the model's role is — not
whether anyone wants the thing.
