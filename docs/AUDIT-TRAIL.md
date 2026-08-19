# docs/AUDIT-TRAIL.md — every decision, measurement, correction and defect, with its evidence

**Append-only, and CHECKED.** `tools/audit_trail.py` verifies it in both directions: every decision
record and measurement in the repository appears here, AND every file this file cites exists.

The second direction is the one that is usually missing, and it is here for a reason. On 19 Aug
2026 this build published a measurement whose stated source contained neither the number nor the
quotation attributed to it — a citation to the author's own prose, presented as external. Nothing
could catch it: `ci/no-bare-absence.sh` requires an ABSENCE claim to cite a resolvable ledger row,
and no check existed that a POSITIVE citation resolves at all.

`make audit` runs it. `python tools/audit_trail.py --selftest` proves it can go red — a dead
citation, an unlogged artefact, and an empty trail are each planted and observed refused.

| kind | meaning |
|---|---|
| `DECISION` | a choice that closes an option, with the evidence that closed it |
| `MEASUREMENT` | a number produced by running something |
| `CORRECTION` | a published claim that was wrong, and what replaced it |
| `DEFECT` | something the build found in itself |

| date | kind | what | evidence |
|---|---|---|---|
| 2026-08-20 | DECISION | D-A3-01 — what persists is the ARTIFACT SET; the graph is re-derived, never stored | `docs/decisions/D-A3-01-the-graph-is-re-derived-not-stored.md` |
| 2026-08-20 | DECISION | D-P10-01 — a cell with no value is `ABSENT`, and `_coerce(None)` raises | `docs/decisions/D-P10-01-none-is-not-a-value.md` |
| 2026-08-20 | DECISION | D-P4-01 — there is no `REJECTED` predicate state | `docs/decisions/D-P4-01-no-rejected-state.md` |
| 2026-08-20 | DECISION | D-P4-02 — the `schema_keys` grammar | `docs/decisions/D-P4-02-key-grammar.md` |
| 2026-08-20 | DECISION | D-P4-03 — `matches()` is not in the admitted subset | `docs/decisions/D-P4-03-no-regex-in-cel.md` |
| 2026-08-20 | DECISION | D-P4-04 — the CEL agreement claim is a DIFFERENTIAL, not a CONFORMANCE run | `docs/decisions/D-P4-04-conformance-fallback.md` |
| 2026-08-20 | DECISION | D-P4-06 — `claims_fault_classes`, the field that stops a predicate choosing its own denominator | `docs/decisions/D-P4-06-fault-class-claims.md` |
| 2026-08-20 | DECISION | D-P4-07 — a candidate with no statutory clause declares why (re-keyed by arbitration C2) | `docs/decisions/D-P4-07-clauseless-candidates.md` |
| 2026-08-20 | DECISION | D-P7-01 — the statutory corpus is empty, and that is a published number | `docs/decisions/D-P7-01-no-statutory-instrument.md` |
| 2026-08-20 | DECISION | D-P7-02 — three corroboration states, not two | `docs/decisions/D-P7-02-three-corroboration-states.md` |
| 2026-08-20 | DECISION | D-P8-01 — there is no blind-fill corpus, and `BLOCKING` is `0` by construction | `docs/decisions/D-P8-01-no-blind-fill-corpus.md` |
| 2026-08-20 | DECISION | D-P8-02 — SUPERSEDED 13 Aug 2026: `REGISTER-DERIVED` is built | `docs/decisions/D-P8-02-no-register-derived.md` |
| 2026-08-20 | MEASUREMENT | M-CEIL — the filing-checkable ceiling, and three published numbers re-run | `docs/measurements/M-CEIL-results.md` |
| 2026-08-20 | MEASUREMENT | P1 — container guard headroom | `docs/measurements/P1-guard-headroom.md` |
| 2026-08-20 | MEASUREMENT | P1 — the reader-agreement matrix | `docs/measurements/P1-agreement.md` |
| 2026-08-20 | MEASUREMENT | P10 exit gate — **G-LIVENESS**, evaluated point by point | `docs/measurements/P10-exit-gate.md` |
| 2026-08-20 | MEASUREMENT | P10 — `|RESIDUE|`, the adjudication record, and the demonstrated survivors | `docs/measurements/P10-residue.md` |
| 2026-08-20 | MEASUREMENT | P10 — the canary cost, and the `MAX_WITNESSES` calibration curve | `docs/measurements/P10-canary-cost.md` |
| 2026-08-20 | MEASUREMENT | P11 exit gate — **G-REPRO**, evaluated point by point | `docs/measurements/P11-exit-gate.md` |
| 2026-08-20 | MEASUREMENT | P11 — byte identity | `docs/measurements/P11-byte-identity.md` |
| 2026-08-20 | MEASUREMENT | P12 entry — what can be built, what cannot, and which of the plan's own failure branches each fa | `docs/measurements/P12-entry.md` |
| 2026-08-20 | MEASUREMENT | P12 exit gate — **G-SETTLE**, evaluated point by point | `docs/measurements/P12-exit-gate.md` |
| 2026-08-20 | MEASUREMENT | P14 entry — the surfaces, and the two decisions taken before the first template | `docs/measurements/P14-entry.md` |
| 2026-08-20 | MEASUREMENT | P14 — the surface audit | `docs/measurements/P14-surface-audit.md` |
| 2026-08-20 | MEASUREMENT | P2 — the field surface | `docs/measurements/P2-field-surface.md` |
| 2026-08-20 | MEASUREMENT | P3 — G-EVAL arm 1: evaluator against the regulator's cached values | `docs/measurements/P3-evaluator.md` |
| 2026-08-20 | MEASUREMENT | P3 — cached-value reproduction, and the function census that bounds it | `docs/measurements/P3-cached-value-reproduction.md` |
| 2026-08-20 | MEASUREMENT | P4-B1 — envelope digests | `docs/measurements/P4-envelope-digests.md` |
| 2026-08-20 | MEASUREMENT | P4-B2/B4 — `schema_keys` both ways | `docs/measurements/P4-both-ways.md` |
| 2026-08-20 | MEASUREMENT | P4-B3 — CEL runtime agreement | `docs/measurements/P4-cel-conformance.md` |
| 2026-08-20 | MEASUREMENT | P4-B4 — the harvest distribution, across all nine prescribed workbooks | `docs/measurements/P4-harvest-distribution.md` |
| 2026-08-20 | MEASUREMENT | P5 — the runtime closure partition, on a real filing | `docs/measurements/P5-runtime-closure.md` |
| 2026-08-20 | MEASUREMENT | P6 — the fault campaign, model `v3` | `docs/measurements/P6-fault-model-v3.md` |
| 2026-08-20 | MEASUREMENT | P9 · Exit gate — evaluated point by point, by someone who did not do the work | `docs/measurements/P9-exit-gate.md` |
| 2026-08-20 | MEASUREMENT | P9-B1 — `TEMPLATE_DIFF`'s ceiling, published before its delta | `docs/measurements/P9-template-diff-ceiling.md` |
| 2026-08-20 | MEASUREMENT | P9-B2 — relation runnability, and the two counts that are the deliverable | `docs/measurements/P9-relation-runnability.md` |
| 2026-08-20 | MEASUREMENT | P9-B4 — routing every relation through the five gates | `docs/measurements/P9-relation-attrition.md` |
| 2026-08-20 | MEASUREMENT | P9-delta — before/after settled count AND marginal kill, per relation | `docs/measurements/P9-delta.md` |
| 2026-08-20 | MEASUREMENT | Wave 0 — results | `docs/measurements/W0-results.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/P7-attrition.md — the five-gate attrition funnel | `docs/measurements/P7-attrition.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/P7-textsource.md — the instrument text source (P7-B0) | `docs/measurements/P7-textsource.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/P8-blind-probe.md — the blind-fill probe | `docs/measurements/P8-blind-probe.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/P8-ffr.md — the first measured false-failure rate | `docs/measurements/P8-ffr.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/P8-mask-external-check.md — F36 | `docs/measurements/P8-mask-external-check.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/P8-severity.md — the interval arithmetic, derived | `docs/measurements/P8-severity.md` |
| 2026-08-20 | MEASUREMENT | docs/measurements/S1-instrument-agreement.md — the first statutory instrument | `docs/measurements/S1-instrument-agreement.md` |
| 2026-08-19 | CORRECTION | M-CEIL attributed a ~176-of-531 estimate AND a verbatim quotation to a file containing neither; the source was this build's own docstring | `docs/measurements/M-CEIL-results.md` |
| 2026-08-19 | CORRECTION | "2 of 12 genuine proposals refused" was never a model error rate — both cells exist and are in the field surface; G-FIELD tested the LABELLED subset while its reason said "field surface" | `docs/spike/README.md` |
| 2026-08-19 | CORRECTION | provisos 106 of 531 does not reproduce; re-run gives 83 of 532 over 94 `Provided that` occurrences | `docs/measurements/M-CEIL-results.md` |
| 2026-08-19 | CORRECTION | the labelled-field denominator is a property of an unwritten RULE, not of the return — 3,104 / 498 / 724 across three readings of the same 3,747 cells | `docs/measurements/M-CEIL-results.md` |
| 2026-08-19 | CORRECTION | the 3,544 common-address claim overstated the hazard 2.4x; measured 1,451 hold a different field, 2,093 the same | `docs/PLAN.md` |
| 2026-08-19 | CORRECTION | README claimed every figure in the published walkthrough is read live from the API; three detection-card values are asserted by nothing and served by no route | `README.md` |
| 2026-08-19 | CORRECTION | a second README passage still said POST /v1/filings refuses every filing, after the first was fixed | `README.md` |
| 2026-08-19 | CORRECTION | two claims Phase 1 falsified were RENDERED INTO THE PRODUCT via the standing open-items panel | `docs/OPEN-ITEMS.md` |
| 2026-08-19 | DEFECT | the gate-to-control map ASSERTED bindings; deriving them from the sweep's own per-guard record gives 104 of 125, not 115, and exposes 21 gates with no control at all | `tools/gate_liveness.py` |
| 2026-08-19 | DEFECT | the evidence layer reached lxml directly, bypassing the one hardened parser factory; NC-P08 failed the build because the XXE spy can only watch one door | `src/cdfc/evidence/workbook.py` |
| 2026-08-19 | DEFECT | openpyxl silently drops the x14 namespace where 19 of 54 validations live; reading with it finds zero vocabularies — clean, empty and wrong | `docs/EVIDENCE-LAYER.md` |
| 2026-08-19 | DEFECT | the raw reader returned `<v>` text for numeric cells, so numbers read as labels and the labelled count went 498 to 2,169 | `src/cdfc/evidence/workbook.py` |
| 2026-08-19 | DEFECT | the ceiling classifier's `Rs\.?` matched inside ordinary words, putting 174 of 532 clauses in the quantified bucket on a substring | `tools/measure/ceiling.py` |
| 2026-08-19 | DECISION | pytest gate evidence is DERIVED from the sweep, never hand-maintained; a pytest row left in the map is a hard refusal | `tools/gate_liveness.py` |
| 2026-08-19 | DECISION | the ANCHOR architecture phases are renamed P->A; both sequences had reached 4 while sharing a prefix | `docs/PLAN.md` |
| 2026-08-20 | DECISION | the audit trail is checked in BOTH directions — every artefact logged, and every citation resolves | `tools/audit_trail.py` |
| 2026-08-19 | MEASUREMENT | the evidence layer end to end on the real instrument and return: 5 of 5 planted errors caught, each by its own named gate | `docs/EVIDENCE-LAYER.md` |
