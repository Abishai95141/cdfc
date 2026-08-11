# PART V — AUDIT

**An adversarial check of whether the reconciliation ruling `research/synthesis/D-reconciliation.md`
landed in Parts 0–IV, run 10 August 2026 after the merge. Nothing here is new research. Every grade is
against D's ruled `Replacement:` sentence, not against my own preference.**

**Line numbers in this audit are POST-EDIT.** Seventeen edits were made during the audit; they are
listed with before/after in §V.7. Six of them changed line counts in `02-architecture.md` (+2),
`03-stack.md` (+1) and `04-path.md` (+1); every reference below has been re-resolved against the
current files.

**Scope note.** The brief named Parts I–IV. `00-executive.md` was audited as well, because it ships in
front of them and a divergence there is the most visible kind. Two defects were found in it and fixed.

**Headline counts.**

| Class | Total | LANDED | NOT-LANDED | NEW-DIVERGENCE |
|---|---:|---:|---:|---:|
| Contradictions C1–C31 | 31 | **29** | 0 | **2** (C11, C12) |
| Surviving falsehoods F1–F9 | 9 | **8** | **1** (F8) | 0 |
| Unwarranted confidence U1–U11 | 11 | **11** | 0 | 0 |
| Innovation restorations I1–I3 | 3 | **3** | 0 | 0 |

**All four defects above are now fixed.** What remains open is a separate and more serious class: **six
cross-part semantic divergences that D never ruled on**, three of which cannot be closed without the
owner. They are §V.5. One of them — the cell-state precedence order — changes the value of the
product's headline number.

---

## V.1 — THE 31 CONTRADICTIONS

Grading rule: **LANDED** = D's ruled Replacement is what the spec says. **NOT-LANDED** = the spec says
one of the two losing versions. **NEW-DIVERGENCE** = the spec says a third thing.

| # | Ruled replacement | Grade | Evidence |
|---|---|---|---|
| **C1** | Eight closed item states, first six in the settled denominator, any `ERROR` ⇒ `INVALID` | **LANDED** | `01:376` "Eight closed item states — `PASS`, `FAIL`, `INDETERMINATE`, `NOT_RUN`, `NO_PREDICATE`, `ERROR`, `OUT_OF_SCOPE`, `INFORMATIONAL` — of which the first six are in the settled denominator"; `02:482` the eight-row table; `03:555` verbatim; `04:543` G4 verbatim. Four independent statements, one wording. |
| **C2** | 30 codes, five families, admitted only if a different remedy | **LANDED** | `02:582–635` enumerates 8 + 10 + 4 + 3 + 5 = 30; `03:568` "closed, namespaced and has 30 codes across five state families; a code is admitted only if it implies a different remedy". Family counts reconcile in both parts. |
| **C3** | B's seven-term closure | **LANDED** | `02:516`; `03:562`; `04:463` A12. `02` uses `== cellsTotal`, `03`/`04` use `== fieldSurface`; `02:1008` defines `cellsTotal` as `== fieldSurface`, so this is one equation. |
| **C4** | `applicable == false ⇒ OUT_OF_SCOPE`; `UNCHECKED` nowhere in the contract | **LANDED** | `02:536`, `02:566`, `03:139`, `04:545`. **One leak found and fixed:** `02:866` used `UNCHECKED` as the G3 proof-arm outcome where Part III (`03:41`, `03:261`) says `unproven`. Edit 1. |
| **C5** | `expr` raises ⇒ `ERROR(predicate_raised)`, run `INVALID` | **LANDED** | `02:550`, `02:567`, `03:145–148` with the remedy argument, `04:282` T4, `04:545`. |
| **C6** | `cells_bound == 0 ⇒ ERROR(cells_bound_zero)`, run `INVALID` | **LANDED** | `01:379`; `02:558`; `03:155`; `04:91` and `04:456` A5, both with "never `NOT_RUN`". C's demotion is dead everywhere. |
| **C7** | Declared proviso ⇒ `NO_PREDICATE(no_predicate.not_yet_synthesised)` + verbatim text + span + `provisos_declared` | **LANDED** | `02:570`, `02:572–580` (the cell-denominator interaction), `02:859` G0, `03:253`, `04:90`. |
| **C8** | Nine methods incl. `TEMPLATE_DIFF` + `DIFFERENTIAL`; warrant lattice; `provenance ∈ {COMPUTED, DECLARED}` | **LANDED** | `02:646–651` all three enums; `02:658` deletes the four-value `MEASURED\|MODELED\|ASSERTED\|UNCHECKED` column explicitly; `03:483–486` the SQL matches value-for-value. `METAMORPHIC` survives only in the rename table (`02:16`). |
| **C9** | Six values, spelled `REGISTER-DERIVED` | **LANDED** | `02:650`, `02:668`; `03:463`; `04:103` "The register value is spelled `REGISTER-DERIVED` everywhere". `REAL-REGISTER` appears once, at `02:670`, as the withdrawn third spelling. |
| **C10** | Denominator is the 3,747-cell field surface; pair model unbuilt | **LANDED** | `01:192`; `02:453–464`; `03:410`; `04:540`. `pairsTotal`/`obligationsTotal` appear only in deletion statements. |
| **C11** | Hero is `<F> failures across <S> checks` / `<U> fields were not checked`, from 2,373 / 1,374 / 3,747 | **NEW-DIVERGENCE → fixed** | Correct in `01:201`, `02:1090`, `03:750`. **`04:421` rendered a third form** — `1 failure · 2,373 fields settled across 280 checks` — which puts the predicate count in the hero, the one thing `03:753` forbids ("The predicate count (280) belongs to the strap line and never to the hero"). Edit 13. |
| **C12** | Quantity is the settled fraction; "coverage" reserved for the conformal guarantee; rename key, path and label in one commit | **NEW-DIVERGENCE → fixed** | Landed for the quantity and the API path (`02:14`, `03:11`, `03:731` `/v1/settled-fraction/history`). **Three identifiers were not renamed in Part II** while Part III had renamed them: the verdict enum (`COVERAGE_INSUFFICIENT` / `…WITHIN_STATED_COVERAGE` at `02:511,703,707,710,725` vs `SETTLEMENT_INSUFFICIENT` / `…WITHIN_STATED_SCOPE` at `03:14,129,170,477`), the `predicateType` (`filing-coverage-attestation/v1` vs `filing-settlement-attestation/v1` at `03:59`), and the JSON key `coverageGaps` vs `declaredGaps` (`03:523`). Edits 2, 3, 4. |
| **C13** | 1,692 of 20,562 (8.23%); separately 12,925 → 8,052; do not divide | **LANDED** | `01:697–700`; `01:829` ban row; `04:255`. The 8.23%-of-12,925 pairing occurs nowhere. |
| **C14** | No opened-vendor integer until an inclusion rule exists | **LANDED** | `01:607` "**Neither number is quotable** … the absence claim ships with the list above and no integer"; `01:596` carries the list; `04:208` Fri 11 Aug requires `docs/ABSENCE-SCOPE.md`; `04:523` R13. No `16` or `21` survives. |
| **C15** | Stratum A = 20, ≥ 6 of 20 retain, ≤ 2 delete, one extension to n = 40 at ≥ 12 | **LANDED** | `04:44–47` verbatim as DECISION E6.1; `04:60` "Draw until \|A\| = 20; cap Stratum B at 10; ≈30 drawn in total"; `04:64–72` the power table is stated as exact binomial for n = 20 and labelled "belong to no other n". *A downstream arithmetic divergence in the experiment's size and cost is reported at §V.5.4.* |
| **C16** | Five gates: G0 · G1 · G2 · G3 · G4 | **LANDED** | `01:371`; `02:856–877`; `02:879` "Why five and not four"; `03:246`; `04:85`. The four-gate numbering survives only in the mapping table at `02:920`. |
| **C17** | Two different tests: E6 at `K/O > 0` + marginal kill; registry at `K/O ≥ 0.80` | **LANDED** | `02:890–899` states both in a two-row table and "a document that quotes one attrition figure has quoted the wrong one"; `03:279`; `04:96` DECISION E6.2. |
| **C18** | Provider-native structured output + post-hoc key check; `outlines` when an open-weight model enters | **LANDED** | `02:205–209`; `03:49` row 24. Both carry "whether provider-native constraint is guaranteed or best-effort is UNVERIFIED — which is exactly why the post-hoc guard is not optional". |
| **C19** | Implement the FRBR URI grammar (~100 lines); `cobalt` only if its LICENSE is opened; `bluebell` GPL-3.0 never linked | **LANDED** | `02:167–171`; `03:33` row 8; `03:98`; `04:400`. |
| **C20** | Z3 MIT SECONDARY · Hypothesis reported MPL-2.0 SECONDARY · in-toto Apache-2.0 VERIFIED-AT-SOURCE, deleted from the unread table | **LANDED** | Z3: `03:41`, `03:83`, `04:527`. Hypothesis: `02:338`, `03:46`, `03:84`. in-toto: `01:762`, `02:1131`, `03:59`, `03:86`, `04:355`. `03:96–102` lists the unestablished licences and in-toto is correctly absent. |
| **C21** | Filer signs, detached key; vendor only as `assessor.id`, `thirdParty:false`; residual is legal review | **LANDED** | `02:1141`; `03:623`; `03:825`; `04:530` R20 "**DECIDED, pending legal review**"; `04:567` Q7. "Nobody has raised it yet" is gone. |
| **C22** | One `pervasiveness-policy-v1.json`; both numbers `PLACEHOLDER` until argued | **LANDED** | `02:719–725`; `02:1060` renders `"K": "PLACEHOLDER", "T": "PLACEHOLDER"`; `03:129` F12; `03:827`; `04:337` M3. |
| **C23** | Supervisor is not a user; say "a downstream reviewer"; delete "the two surfaces" | **LANDED** | `01:104`; `01:109` "the phrase 'the two surfaces' does not appear in this specification" — and it does not; `03:707`; `03:723` "what a downstream reviewer's triage tool consumes"; `04:393`. |
| **C24** | "Data model, stack and flow in B; experiment queue, dated plan and deliverable in C" | **LANDED** | `04:571–573` "the data model, the stack and the flow are in the part preceding this one; this part carries the experiment queue, the dated plan, the deliverable and everything still open". The inversion is gone. |
| **C25** | "…any of the fourteen complete outputs" | **LANDED** | `01:59`; `04:263`; `04:521` R11. No "fifteen outputs" anywhere. |
| **C26** | State the plan as `1 list + N detail`, report the run's actual count | **LANDED (with residue)** | `01:236`; `02:94`; `03:691`; `04:483`. *Residue at §V.6.1: 2,235 is reported as MEASURED in two parts and reconciles with no N stated anywhere in the document.* |
| **C27** | One date with one verb, or neither | **LANDED** | `02:101` and `03:57` quote the advisory ID and CVSS only; `04:406` states the rule explicitly. No date survives. |
| **C28** | Quote only what one instrument returned; no scheme count from the register | **LANDED** | `01:115`, `01:120`; `04:484`. The 390 is deleted and its deletion is recorded at `01:122`. |
| **C29** | Induction, harvest, arithmetic evaluation and the denominator are built; the rest is specified | **LANDED** | `02:24` quotes the ruling verbatim and forbids the "L1→L5" form; `01:391`; `03:647`; `04:177`. Layer-by-layer statuses reconcile across `02:39–51`, `03:117–131` and `04:181–188`. |
| **C30** | `.external_source_lacks_field` — our near-miss is the illustration, not an instance | **LANDED** | `01:227`; `02:614`; `03:582`; `04:491`. All four carry "illustration and not an instance" with both endpoints. |
| **C31** | Add the administrator call to M0 as E1b, or record its retirement — not both states | **LANDED (label mismatch, §V.5.6)** | `04:28` E1b; `04:154` "**DECIDED: it stays, scheduled in M0, demoted from killer to pitch-shaping**" with the exact question text at `04:163`; `04:565` Q5. |

---

## V.2 — THE NINE SURVIVING FALSEHOODS

| # | Grade | Evidence |
|---|---|---|
| **F1** `555` / `562` | **LANDED** | Zero occurrences outside the ban row at `01:822`. The enumeration is `505 + 54 + 15 = 574` and `574 / 581 = 98.8%` at `01:325`, `02:1092`, `04:487`, each labelled DERIVED. |
| **F2** "+37–54 pp of functional equivalence" | **LANDED** | The phrase occurs only in the ban row (`01:825`). The corrected sentence — structural similarity, and outcome equivalence 51–53% — is at `01:261`, `02:255`, `03:231`, `04:266`. |
| **F3** "Hypothesis (MPL-2.0)" as bare fact | **LANDED** | `02:338`, `03:46`, `03:84` all read "reported MPL-2.0 … LICENSE not (re-)read". |
| **F4** "Z3 (MIT)" as bare fact | **LANDED** | `03:41`, `03:83` "MIT (SECONDARY — the LICENSE was not opened by any lane); open it before shipping". |
| **F5** "in-toto — UNVERIFIED" | **LANDED** | Inverted correctly; see C20. |
| **F6** "sixteen commercial products" | **LANDED** | See C14. |
| **F7** "8.23% of ~12,925" | **LANDED** | See C13. |
| **F8** bare "the 17 decidable predicates" | **NOT-LANDED → fixed** | `04:190` carried `*"17 of 24 → 574/581 = 98.8% in an afternoon"*` as a live claim needing a warrant label — the banned figure, presented as a claim rather than quoted as dead. Every other part uses the ruled replacement (`01:299`, `01:823`, `02:843`). Edit 11. |
| **F9** PROVE rows marked VERIFIED-AT-SOURCE | **LANDED** | `01:256` is labelled **ABSTRACT-ONLY** and states "Every negative claim about PROVE … is downgraded to 'not visible in the abstract; the full text is unread'"; `01:733`; `04:39` E13; `04:524` R14. |

---

## V.3 — THE ELEVEN UNWARRANTED-CONFIDENCE RESTATEMENTS

**U1 — the one that matters. PRESENT, PROMINENT, AND USED AS AN ASSET.** This is the strongest thing
the merge did. The corrected paragraph appears verbatim in four places, never in a footnote:

- `01:313` — inside §I.2.5, introduced as "**the one that matters most, because it is about us**", with
  the reasoning spelled out first at `01:305`: "under this specification's own admission rule, **the
  currently admissible predicate set is empty and the currently defensible settled fraction is 0%.**"
- `02:1098` — as the corrected sentence attached to the report's headline, plus a **schema field**
  carrying it: `02:1023` `"admissibilityCaveat": "None of the 280 predicates producing this number is
  admitted under gate G4 … the currently defensible settled fraction is 0%."` Putting it in the payload
  is stronger than D asked for.
- `03:542` — attached to the settled-fraction object.
- `04:420` — as the operator's spoken line at demo step 2, with `04:428` "**Why step 2 is the strongest
  moment and not the fatal objection**", `04:512` R2 ("Mitigated by disclosure — and it becomes the
  strongest moment in the demo"), and `04:462` **A11**, a CI test: "No settled count renders without the
  admission state of the predicate set that produced it … assert `PRE-GATE` appears in the same block".

The composition caveat travels with it in all four (`01:319`, `02:1104`, `03:549`, `04:430`): 2,329 of
2,373 (98.1%) from 53 validation predicates, 271 cells from 227 arithmetic ones. **Those class counts
reconcile against the harvest breakdown at `03:189`** — 181 + 35 + 11 = 227 arithmetic, 20 + 13 + 11 + 6
+ 3 = 53 validation-derived — which is a check D did not ask for and which passes.

| # | Grade | Evidence |
|---|---|---|
| **U2** "L1→L5 runs end-to-end" | **LANDED** | `02:29` bans the form by name; `02:24`, `01:391`, `03:647`, `04:177` carry the ruled sentence. |
| **U3** "zero model calls" stated as a property | **LANDED** | `02:34`, `01:394`, `03:649`, `04:192`, `04:457` A6 "**Not yet written — this is the gate that turns a design property into a system property**"; `03:805` lists `test_no_model_in_verdict_path` as "(**not yet written**)". *Minor residue at §V.6.6.* |
| **U4** FinVerBench concentration | **LANDED** | `01:243` is a bold single-instrument warning governing the first four rows, each tagged `[FVB]`; `04:259` makes the annotation non-negotiable before submission; `04:522` R12. |
| **U5** "0% FPR" true by construction | **LANDED** | `01:253` "**Calibration is achievable, and it was measured on a clean set built to satisfy the checks. Say both in one sentence.**"; `04:266`. |
| **U6** residue reproducibility | **LANDED** | `01:801`, `02:1241`, `03:367`, `04:35` — all four carry "and the published adjudication record", content-addressed. |
| **U7** 98.8% asserted as measured | **LANDED** | `01:328`, `02:1093`, `04:190` (as corrected), `04:487` — all labelled "DERIVED — an enumeration argument, not a run". |
| **U8** "the gate demonstrably does real work" | **LANDED** | `01:795`, `02:268`, `03:785`, `04:423` — all four state one rejection, five predicates, 1,428 cells, and "whether it rejects anything on the FME workbook is unmeasured — 19 of 24 FME bounds are a real `≥ 0`". |
| **U9** "the register is clean by definition" | **LANDED** | `01:231`, `03:294`, `04:111` — membership vs format split, with 87 of 228. |
| **U10** τ-bench denominator | **LANDED** | `01:258` "τ-retail, n = 115 tasks; τ-airline (n = 50) … **The denominator travels or the figure does not**"; `01:404`; `04:383`. |
| **U11** 515 never alone | **LANDED** | `01:188`, `02:1106`, `03:793`, `04:244`, `04:477` — every occurrence carries the per-workbook distribution requirement, and `03:796` makes publishing it a build gate. |

---

## V.4 — THE THREE INNOVATION RESTORATIONS

All three are restored in D's bolder-and-truer form, not sanded off. Each is carried as a block quote in
at least three parts, which is what makes it survivable.

**I1 — the undetectable-in-principle mutant class. RESTORED.**
> `01:533` / `02:1253` / `03:370` / `04:426`: *"A prescribed return is a closed arithmetic system. We can
> construct, and exhibit, a family of filings that are internally perfect under every relation the
> regulator's own template encodes and every relation we have added — and materially false. That family
> is non-empty by construction, its size is measurable, and measuring it is the first quantitative
> statement anyone has made about the limit of document-level verification for a regulated filing."*

The consequence D asked for is drawn: `04:520` grades R9 **"Low → structurally impossible"** and marks
it "Structurally retired; the measurement is the deliverable". `02:1259` and `03:377` state the same.

**I2 — `INVALID` as a liveness proof. RESTORED.**
> `01:551` / `02:1178` / `03:173` / `04:425`: *"No assurance artifact in existence carries evidence that
> the instrument that produced it was working on the specific document it examined. A clean audit
> opinion does not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict
> unless every check has just demonstrated, on your file, that it can still catch the fault it was
> admitted for."*

The hedges D said to keep are kept and subordinated: `02:1184` "The nearest named prior art is SRE
synthetic monitoring and hardware built-in self-test" and "*A formal-methods citation for vacuity
detection is **UNVERIFIED** and must not be asserted.*"

**I3 — the criterion-source substitution. RESTORED.**
> `01:564` / `02:232` / `03:237` / `04:438`: *"SPADE infers what correctness meant from the traces of a
> developer changing their mind. We do not have to infer it: the criterion is a published instrument
> with a version, an amendment chain that is machine-followable in 76 of 82 cases, and a blank template
> with a content hash. The criterion source is not more* authoritative *than SPADE's — the regulator's
> own template computes a scheme total that misses two of its own nine legal values — it is* **citable,
> versionable and watchable***…"*

`02:239` and `03:244` both add the sentence D wanted: this is what the instrument-stream watcher
implements, and no draft stated it as a novelty. The brief's sharpest sentence is carried in its only
defensible form at `01:578`, `02:930`, `03:69` and `04:389`.

---

## V.5 — CROSS-PART SEMANTIC DIVERGENCE

**This is the section that matters. D ruled on none of these, so none of them is a failure of the
merge — they are places where two parts, each internally coherent, assign two different values or two
different meanings to one thing. Ranked by consequence.**

### V.5.1 — THE CELL-STATE PRECEDENCE ORDER IS TWO DIFFERENT ORDERS, AND THEY DISAGREE ON THE HEADLINE NUMBER — **UNRESOLVED, OWNER DECISION REQUIRED**

> `02:477`: `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`
> and `02:478`: "A cell is clean only if **every** predicate binding it passed."

> `03:506`: `ERROR ≻ FAIL ≻ PASS ≻ INDETERMINATE ≻ NOT_RUN ≻ NO_PREDICATE`
> and `03:507`: "A cell read by one passing and one not-run predicate is **settled**."

These are opposite rules for the same case. Under Part II a cell read by one passing and one `NOT_RUN`
predicate is **unsettled**; under Part III it is **settled**. The settled fraction — 2,373 / 3,747, the
number the whole document is built around — is not well defined until one of them wins. The two orders
also differ in membership: Part II includes `INFORMATIONAL` and `OUT_OF_SCOPE` and excludes
`NO_PREDICATE` (`02:478–480`); Part III includes `NO_PREDICATE` and excludes the other two, having
determined scope first (`03:503`).

**Recommendation, not applied because D does not rule it.** Part II's order is the one consistent with
both parts' prose. `02:83` and `03:119` both say that when the readers disagree on a field, every
predicate reading it returns `NOT_RUN(extractor_disagreement)` and **"the settled fraction falls, it
does not silently succeed"** — which is only true if `NOT_RUN ≻ PASS`. Part III's order makes that
sentence false in exactly the case it was written for. Adopting Part II's order requires flipping the
claim at `03:507` and re-deriving nothing else.

### V.5.2 — THE "FIVE RULES" OF THE EVALUATION CONTRACT ARE TWO DIFFERENT FIVES — **UNRESOLVED**

`02:534–560` and `03:137–157` are identical, rule for rule: (1) `applicable` · (2) pre-flight ·
(3) `expr` · (4) warrant composition · (5) `cells_bound`. `04:545` G5 enumerates a **different** five:
(1) `applicable == false` · (2) `expr` true/false · (3) runtime error · (4) budget · (5) `cells_bound`.

Nothing in Part IV's five is *wrong*; it drops pre-flight and warrant composition and splits rule 3.
But `03:819` G5 says the contract "**contain[s] the five rules and nothing else; every other document
links to it**", and `02:529` says a CI test asserts the evaluator's transition table equals that table.
A build that generates `EVALUATION-CONTRACT.md` from Part II and tests it against Part IV's G5 fails.

**Recommended replacement for `04:545`**, not applied because it rewrites rather than corrects:
*"DECIDED: one file, `EVALUATION-CONTRACT.md`, generated from §II.3.4 and the only place the contract
appears. Its five rules are `applicable`, pre-flight, `expr`, warrant composition and `cells_bound`; the
three rulings the drafts disagreed about are rules 1, 3 and 5, resolved as `OUT_OF_SCOPE`,
`ERROR(predicate_raised)` and `ERROR(cells_bound_zero)`."*

### V.5.3 — THE CONTAINER GUARD EMITS A REASON CODE THAT IS NOT IN THE CLOSED VOCABULARY — **UNRESOLVED**

> `03:118` F1: "Any trip → `INVALID` with `ERROR(source_unreadable)`."

`source_unreadable` is a `not_run.*` code (`02:607`, `03:573`). The `error.*` family has exactly five
members and none of them fits a container-guard trip (`02:633`, `03:578`). This is the closed-world
promise failing inside the document that makes it: a state/reason pair is emitted that the frozen 8 × 30
vocabulary cannot represent. `02:1221` lists "a container guard trip" among the `INVALID` causes and
assigns it no code at all, so there is no second opinion to copy.

**Two admissible fixes, both needing the owner:** map it to `error.parser_disagreement_structural`
(stretching that code's meaning), or admit a 31st code `error.container_guard_tripped` under the
stated admission test — it plainly implies a different remedy from every existing code, which is the
test at `02:584`. **The count 8 × 30 is pinned in four places, so this is not a free change.**

### V.5.4 — THE SETTLING EXPERIMENT SHIPPED THREE SIZES AND THREE COSTS — **FIXED**

`04:118` derives 600 candidates ≈ $13 from ≈30 obligations drawn, consistent with `02:373` ("~600 calls
per template version … ~30 obligations × 10 candidates × 2 prompt regimes"). `03:665` carried "20
obligations × 10 candidates × 2 prompt regimes = 400 candidates … ≈ $9.10" — a fourth arithmetic that
does not even multiply out (400 × $0.0218 = $8.72) — and `00:64` carried "about nine dollars". Both
aligned to Part IV's shown arithmetic, which is the only one that reconciles with C15's ≈30 drawn.
Edits 8 and 9.

### V.5.5 — SMALLER DIVERGENCES, ALL FIXED

| Thing | Part II said | Part III / IV said | Resolution |
|---|---|---|---|
| Verdict enum | `COVERAGE_INSUFFICIENT`, `…_WITHIN_STATED_COVERAGE` | `SETTLEMENT_INSUFFICIENT`, `…_WITHIN_STATED_SCOPE` (`03:14` decides it, with a reason) | Part II aligned to Part III (edit 4) |
| `predicateType` | `filing-coverage-attestation/v1` | `filing-settlement-attestation/v1` (`03:59`) | Part II aligned (edit 2) |
| Declared-gaps key | `coverageGaps` | `declaredGaps` (`03:523`) | Part II aligned (edit 3) |
| Predicate `state` enum | `ACTIVE \| PROVISIONAL \| QUARANTINED \| WITHDRAWN` (`02:802`) | `ACTIVE \| PROVISIONAL \| WITHDRAWN \| REJECTED` (`03:451`) — **no `QUARANTINED`, though `02:972` V5 and `03:345` both mandate automatic quarantine** | Part III aligned to Part II (edit 7). *Residual: `REJECTED` is now absent from both; rejected candidates live in the `rejection` table with `predicate_id NULL` (`03:468`), so this is believed correct — confirm.* |
| Report item key | `cell_id = stable_key` (`02:455`) | `item_id = (stable_key, predicate_id)` (`04:546`) | Part IV aligned to Part II (edit 15) |
| Obligation table file | `obligations.yaml` (`02:470`) | `obligations.csv` (`04:546`) | Part IV aligned (edit 15) |
| Money-scale enum | `field(… unit …)` (`03:428`), `Field.unit` (`03:818`) | `Field.scale` (`04:543`) — names a field that exists nowhere | Part IV aligned (edit 14) |
| Fact-table build time | — | 1 ms MEASURED (`03:636`) vs ~10 ms (`04:183`, the receipt figure) | Part IV aligned (edit 12) |
| Residue exhibit | "all 223 carries and all 135 SUM identities" — 135 is sourced nowhere in the corpus | "all 181 cross-sheet carries and all 35 SUM identities" (`04:426`, `04:520`), matching the harvest breakdown at `03:189` | Part II aligned (edit 6) |
| G3 proof-arm outcome | `unknown ⇒ UNCHECKED` (`02:866`) — a retired token | `unknown` is `unproven` (`03:41`, `03:261`) | Part II aligned (edit 1) |

### V.5.6 — DIVERGENCES LEFT DELIBERATELY UNTOUCHED

- **E1b status label.** `01:507` opens the administrator call as "**OPEN — USER DECISION** … is the
  fund-administrator call still live?" with a default of retirement-as-killer; `04:154` says
  "**DECIDED: it stays**, scheduled in M0, demoted from killer to pitch-shaping". The *substance* is
  identical (not a killer; still worth one call) and `04:565` Q5 preserves the user's decision, so this
  is a label mismatch, not a contradiction. Worth one word if the owner wants it tidy.
- **`K`/`T` absolutism.** `03:827` says "**no number for either appears anywhere**", while `02:719`
  quotes the two withdrawn parameter sets (`K = 3, T = 0.35, v2` and `K = 3, T = 0.45, v1.1`) in a
  withdrawal note. Part II's usage matches the convention every ban table in the document uses; Part
  III's absolute is what is overstated. Left alone.
- **Severity threshold precision.** `02:678` and `04:542` both key the tier on the **Wilson upper
  bound** and argue it; `03:817` G2 states the same thresholds without saying which statistic. Silence,
  not contradiction — but in a document whose §V.6 exists, the words "Wilson upper bound" are worth
  three characters of ink at `03:817`.
- **SPADE's own metric.** `02:220` and `04:93` render it "100% coverage and 100% FFR"; `03:273` renders
  it "100% settled at 100% FFR". Quoting another system's metric name is defensible, so C12 is not
  violated; but two renderings of one quoted fact is a smell.

---

## V.6 — WARRANT DISCIPLINE: NUMBERS WITHOUT A DENOMINATOR OR A WARRANT

Judged against the document's own rule (`01:3`: "Every quantity below carries a warrant label and a
denominator"). Worst first.

1. **`02:96` and `03:693` — "2,235 requests / 2,235 GETs (MEASURED)".** The plan is stated as
   `1 list + N detail where N = |records|`. The document publishes two candidate values of `|records|`:
   650 fund rows and 2,005 register records (`01:209–210`), giving 651 or 2,006. **2,235 reconciles with
   neither, and neither part says what it counts.** D's C26 asked for the plan *and* the run's count;
   the merge delivered both and reconciled neither, so the arithmetic an adversary checks first is still
   unaccounted for. This is the single worst offender because it is the same species of defect — a
   number whose denominator is not stated — that the document exists to attack.
2. **`02:220`, `03:55`, `04:93` — "44.4% of raw candidates individually blow a 25% FFR budget".** No
   denominator (44.4% of how many candidates?), no warrant label, in all three parts.
3. **`02:247`, `03:55` — "68.9% of a published neural oracle's bugs at twice its precision".** No
   denominator, no warrant label.
4. **`02:342`, `03:46` — "55% of mutations are found with a single input and 76% within the first 20".**
   No denominator, no warrant label; it is load-bearing, because it sets `max_examples = 50`.
5. **`03:636` — "fact table over 511 cells 1 ms (MEASURED)".** 511 appears exactly once in the corpus
   and is never defined. The field surface is 3,747; the formula-cell count is 505. A reader cannot tell
   whether 511 is a typo, a subset, or a different filing.
6. **`00:47` — "The whole thing runs in ~30 ms with zero model calls on the verdict path."** Stated as a
   present-tense property of a running system, which is exactly what U3 forbids. The four numbered parts
   all carry the "specified, gate not yet written" caveat; the executive summary does not. *Not edited —
   the same sentence appears in D's own executive verdict, so the owner may have wanted it. It is
   nonetheless the one sentence in the front matter a judge can falsify.*
7. **`02:687` — "roughly `n ≥ 185` clean, non-self-authored filings".** DERIVED and correct, but
   unlabelled and with no shown arithmetic, sitting one line from a paragraph about labelling.
8. **`01:144` — "20% of *inspected* Big Four US audits".** The qualifier "inspected" is carried
   correctly and never drops off, but the inspected population is never given a number, so the
   percentage has a named denominator and no size.

**Also fixed under this heading:** `02:1019` rendered `"settled": { "pass": 2361, "fail": 12, "total":
2373 }` under the comment `// MEASURED (harvest)`. The total is measured; the 2,361/12 split is
invented. Part III's twin block carries the disclaimer (`03:529`: "*A schema example on a hypothetical
filing, not a measurement*"); Part II asserted MEASURED over a fabricated failure count. Edit 5.

---

## V.7 — EDITS MADE

Seventeen edits. Every one is a token or single-clause replacement; no section was rewritten, no claim
was added, no structure changed.

| # | File:line | Before | After | Authority |
|---|---|---|---|---|
| 1 | `02:866` | ``` `unknown` ⇒ UNCHECKED, never "non-degenerate"``` | ``` `unknown` ⇒ unproven, never "non-degenerate"``` | C4 (retired token); `03:41`, `03:261` |
| 2 | `02:993` | `"predicateType": "https://<ns>/filing-coverage-attestation/v1"` | `…/filing-settlement-attestation/v1` | C12; `03:59` |
| 3 | `02:1068` | `"coverageGaps": [ … ]` | `"declaredGaps": [ … ]` | C12; `03:523` |
| 4 | `02:511`, `02:703` (×2), `02:707`, `02:710`, `02:725` (×2) | `COVERAGE_INSUFFICIENT` · `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE` | `SETTLEMENT_INSUFFICIENT` · `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` | C12; `03:14` is the only place the question is decided. **Reversible in one commit if the owner prefers the old spelling — but one of the two must go.** |
| 5 | `02:1019` | `// MEASURED (harvest), see caveat` | `// total MEASURED (harvest), see caveat; the pass/fail split is illustrative, not a measurement` | Warrant rule `01:3`; `03:529` |
| 6 | `02:1264–1265` | "all 223 carries and all 135 SUM identities" | "all 181 cross-sheet carries and all 35 SUM identities" | `03:189` harvest breakdown; `04:425`, `04:519`. 135 is sourced nowhere. |
| 7 | `03:451` | `-- ACTIVE \| PROVISIONAL \| WITHDRAWN \| REJECTED` | `-- ACTIVE \| PROVISIONAL \| QUARANTINED \| WITHDRAWN` | `02:802`; V5 at `02:972` and `03:345` both mandate automatic quarantine |
| 8 | `03:665–667` | "(20 obligations × 10 × 2 = 400 candidates) is ≈ $9.10 … costs under ten dollars" | "(≈30 obligations drawn × 10 × 2 = 600 candidates) is ≈ $13, budgeted at $25 with re-runs … costs under thirty dollars" | C15 (≈30 drawn); `04:118` shows the arithmetic |
| 9 | `00:64` | "costs about nine dollars" | "costs about thirteen dollars" | same |
| 10 | `00:76` | "This is what makes the coverage claim true by construction rather than by discipline." | "The settled-fraction claim is then true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement." | `03:305–308` explicitly withdraws the sentence the executive summary was still using |
| 11 | `04:190` | *"17 of 24 → 574/581 = 98.8% in an afternoon"* | *"15 exact + 2 normalisation-dependent of 24 → 574/581 = 98.8% in an afternoon"* | F8; `01:299`, `01:823` |
| 12 | `04:183` | "fact-table construction (~10 ms)" | "fact-table construction (~1 ms)" | `03:636` MEASURED |
| 13 | `04:421` | `` `1 failure · 2,373 fields settled across 280 checks` `` … "in the same block." | `` `1 failure across 2,373 checks` `` … "with `predicate set: PRE-GATE` and the 280-predicate strap line in the same block, never in the hero." | C11; `03:750–753` |
| 14 | `04:543` | "including from the `Field.scale` enum" | "including from the `Field.unit` enum" | `03:428` SQL, `03:818`; no `scale` field exists |
| 15 | `04:546` | "report items are keyed `item_id = (stable_key, predicate_id)` … `obligations.csv`" | "report items are keyed by the cell — `cell_id = stable_key` (§II.3.1), with each item carrying its per-predicate `evaluations[]` … `obligations.yaml`" | `02:455`, `02:468`, `02:470` |
| 16 | `01:146` | "the warrant is qualified in §I.2.3" | "…in §I.5.3" | §I.2.3 contains no PCAOB row; the qualification is at `01:664` |
| 17 | `01:64` | "§I.5.3 states the search that failed to find one" | "§I.5.2 states…" | The search scope and the list are at `01:596`, inside §I.5.2 |

---

## V.8 — WHAT WAS NOT FIXED, AND WHY

| # | Problem | Why I did not fix it | What closing it costs |
|---|---|---|---|
| 1 | **Cell-state precedence (§V.5.1)** | D issues no ruling, and both orders are argued in place. Choosing changes the value of the settled fraction — the product's headline — so it is not an auditor's call. | One sentence at `03:506–507`, plus a line in the closure test. Ten minutes, and it must happen before `test_closure` is written. |
| 2 | **Two "five rules" (§V.5.2)** | Correcting `04:545` means rewriting the cell, not correcting a token. | Replace `04:545` with the text drafted in §V.5.2. |
| 3 | **`ERROR(source_unreadable)` outside the vocabulary (§V.5.3)** | Needs either a 31st reason code or a stretched meaning; both change a count pinned in four places. | One decision, then a one-word edit at `03:118` or a 31st row at `02:633` and `03:578` — and the "30 codes" count updated everywhere if the latter. |
| 4 | **The unreconciled 2,235 (§V.6.1)** | The reconciliation is a fact about a run I cannot re-execute. | Re-read the snapshot manifest and state what the 2,235 counts, or drop the figure and cite the manifest. |
| 5 | **`00:47` present-tense "runs with zero model calls" (§V.6.6)** | The identical sentence is in D's own executive verdict, so this may be intentional. | Add the six-word caveat the other four parts carry. |
| 6 | **Undefined `511 cells` (§V.6.5)** | I cannot invent the denominator. | Define it or delete it. |
| 7 | **`REJECTED` now absent from the predicate `state` enum (§V.5.5)** | Edit 7 aligned Part III to Part II's four values; if a *predicate row* (not a candidate) can be rejected, the enum needs five. | Confirm that rejected candidates only ever exist in the `rejection` table. |
| 8 | **Document title, `00:1` — "THE COVERAGE-DECLARING FILING CHECKER"** | Renaming the document's title is not a surgical edit. | Under C12 the word "coverage" is reserved for the conformal guarantee; the title uses it as the product's defining property. Either accept "coverage declaration" as a distinct concept phrase (it is used that way at `01:495` and `04:391`) or retitle. |

---

## V.9 — VERDICT

**The ruling landed.** Twenty-nine of thirty-one contradictions state D's replacement in the exact terms
D wrote, most of them in three or four parts independently; eight of nine falsehoods are dead and quoted
only in ban tables; all eleven unwarranted-confidence corrections are present; and all three sanded-off
innovations are restored in the bolder form, block-quoted, with the consequences D asked for actually
drawn (R9 regraded to structurally impossible; the admissibility caveat promoted into the attestation
schema and into a CI test). **U1 in particular is not merely present — it is the spine of the demo, a
required schema field, and a build gate.** That is more than the ruling asked for.

**The residual risk is not in the ruling; it is in the seams.** Three unruled cross-part divergences
survive, and one of them — whether a cell read by one passing and one not-run predicate is settled —
changes the number on the front page. A specification whose thesis is that a denominator must be
derived rather than asserted cannot ship with two derivations of its own denominator.

**Fit to hand to its owner: yes, with one blocking item.** Resolve §V.5.1 before anyone writes
`test_closure`; §V.5.2 and §V.5.3 before the evaluation contract is generated. Everything else in §V.8
is an afternoon.

---

## V.7 — POST-AUDIT RESOLUTIONS (owner, 10 Aug 2026)

The three items the audit correctly declined to fix on its own authority have been decided. Each was a
determined answer under the design's own thesis, not a preference; each is recorded here and applied in
place in the parts named.

### V.7.1 resolves V.5.1 — cell-state precedence · **APPLIED to §III.4.2**

**Decision: §II's order is normative** — `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻
OUT_OF_SCOPE`, and **a cell is clean only if every predicate binding it passed.** §III's
`PASS ≻ INDETERMINATE ≻ NOT_RUN` and its claim that a cell read by one passing and one not-run predicate
is *settled* are withdrawn.

*Why it is determined rather than chosen:* both parts state that on reader disagreement every predicate
reading the field returns `NOT_RUN(extractor_disagreement)` and **"the settled fraction falls, it does not
silently succeed."** Under `PASS ≻ NOT_RUN` that sentence is false in exactly the case it was written for —
a passing predicate absorbs the un-run one and the fraction holds. A check that did not run must never be
absorbed by one that did; that is the product, not a tie-break.

*Blast radius:* the **runtime** settled count can now fall below the static figure, which is the intended
behaviour. The harvest figure **2,373 of 3,747** is unaffected — it counts cells reachable by at least one
harvested predicate, computed before any evaluation.

### V.7.2 resolves V.5.2 — the two different "five rules" · **APPLIED to §IV.6 G5**

**Decision: the five rules are §II.3.4's** — `applicable` · pre-flight · `expr` · warrant composition ·
`cells_bound` — because `EVALUATION-CONTRACT.md` is *generated* from §II.3.4 and a CI test asserts the
evaluator's transition table equals it. §IV's alternative five (which dropped pre-flight and warrant
composition and split rule 3) was not wrong, but a build cannot satisfy two fives. The three rulings the
drafts disagreed about now sit **inside** rules 1, 3 and 5, and budget exhaustion is a sub-case of rule 2.

### V.7.3 resolves V.5.3 — the container guard's reason code · **APPLIED to §III.4.4.1**

**Decision: neither of the audit's two options. A category correction instead.** The 8 × 30 vocabulary is
**per item**, and an item is a cell. A container guard trip is not a property of any cell — nor are an
unbound template or a denominator disagreement, both of which fall through the same hole. Forcing them into
a per-cell reason code was the error, not the missing code.

Run-level `INVALID` causes therefore become their own closed vocabulary, `invalid.*`, with exactly the
eight causes §II.6.2 already enumerates. **The item-level count stays pinned at 8 × 30 in all four
places**, so nothing pinned moves. Where a run-level cause has an item-level analogue
(`.cells_bound_zero`, `.predicate_raised`) both are carried; they are not alternatives.

### V.7.4 resolves the worst of V.6 — warrant discipline · **APPLIED to §II.1.2, §III.5, §0**

- **"2,235 register GETs (MEASURED)" is withdrawn to UNRECONCILED** in both places it appeared. It matches
  neither `1 + 650 = 651` nor `1 + 2,005 = 2,006`, no document states its `N`, and the run cannot be
  re-executed from the artifacts on disk. The fetch plan is now quoted in its **form** — `1 list request +
  N detail requests` — and never as an integer until a re-fetch records one in the manifest. This is the
  same rule the system applies to a filer, applied to the system.
- **Zero model calls in the verdict path** is stated in the executive summary as *specified, with the CI
  gate listed and not yet written* — never in the present tense as a property of a running system.

### V.7.5 — What remains genuinely open after this pass

Not defects, and not fixable by decision: the undefined "511 cells" reference in §III.5; the "44.4% of raw
candidates" and "68.9% of TOGA's bugs" figures carried without their denominators; and the `REJECTED`
predicate state, now absent from both enums on the belief that rejected candidates live in the `rejection`
table with `predicate_id NULL` — **confirm before the schema is written.** These are listed so the next
pass starts from them rather than rediscovering them.
