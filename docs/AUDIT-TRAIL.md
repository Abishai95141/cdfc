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
| 2026-08-20 | DEFECT | a cell string was split on its FIRST `!` at eighteen sites while `Anchor.parse` right-split; a sheet name may contain one and a reference may not | `docs/audit/AUDIT-A1-diff.md` |
| 2026-08-20 | DECISION | `PHASE_RE` widened to admit the A-sequence, with a test pinning what it still refuses — a widened check that admits anything is not a check | `src/cdfc/gates.py` |
| 2026-08-20 | MEASUREMENT | the A1 adversarial audit: six of seven claims survive attack, one real defect | `docs/audit/AUDIT-A1-diff.md` |
| 2026-08-20 | DEFECT | an edit to the gate evidence map silently did nothing because its anchor was absent and unasserted — the drift shape the audit was hunting | `tools/gate_liveness.py` |
| 2026-08-20 | MEASUREMENT | N1: a byte shift costs 0 of 11 citations; a resegmentation costs 11 of 11. A re-pin invalidates every citation against the current corpus | `docs/measurements/N1-repin-blast-radius.md` |
| 2026-08-20 | DECISION | re-pin BEFORE A4: the blast radius is near-zero today and widens with every provision-citing artefact | `docs/measurements/N1-repin-blast-radius.md` |
| 2026-08-20 | MEASUREMENT | N2: the labelling rule pinned by fields-per-label (1.2 vs 4.8); reading all 125 labels found 351 placeholders, 12 instruction texts and a wrong attestation rubric | `docs/measurements/N2-labelling-rule.md` |
| 2026-08-20 | CORRECTION | the labelled population is 132, not 498 or 724; the split is 124 FACT / 8 ATTESTATION, not 481/17 or 702/22 | `docs/measurements/N2-labelling-rule.md` |
| 2026-08-20 | DECISION | an ATTESTATION is a claim NO OBSERVATION CAN SETTLE — a principle, replacing a word list that called evidenceable questions attestations | `src/cdfc/evidence/fields.py` |
| 2026-08-20 | MEASUREMENT | A2: of 12,925 rules published 2026-06-23 we execute 10,453, with a typed reason for each of the other 2,472; zero model calls proven by import closure | `docs/measurements/A2-rule-coverage.md` |
| 2026-08-20 | DEFECT | the Path M parser reported 810 published rules as UNPARSEABLE that parse — a parenthesised row list (696) and a third axis (114), both of which E2 had already specified | `docs/measurements/A2-rule-coverage.md` |
| 2026-08-20 | DECISION | an axis RANGE gets its own typed reason rather than being expanded: expanding would invent axis members the table may not have | `src/cdfc/pathm/statement.py` |
| 2026-08-20 | DECISION | cdfc.pathm and cdfc.evidence added to VERDICT_ROOTS, so 'zero model calls' is a property of the import graph | `tests/negative/importgraph.py` |
| 2026-08-20 | MEASUREMENT | A3: three states over 3,747 filed values against 98 re-verifying observations; exact matching only, per W0-C | `src/cdfc/evidence/contradict.py` |
| 2026-08-20 | DEFECT | A3's first run produced a headline CONTRADICTION out of a category error — a money threshold bound to an attestation cell holding 'Yes' | `src/cdfc/evidence/contradict.py` |
| 2026-08-20 | DECISION | a contradiction REQUIRES a rule: two different numbers in two documents are two different numbers until something says they are about the same quantity | `src/cdfc/evidence/contradict.py` |
| 2026-08-20 | DEFECT | the labelling rule was pinned globally and was NOT schema-free: it named rows on AL_monthly and was chosen on one blank | `src/cdfc/evidence/fields.py` |
| 2026-08-20 | DECISION | the labelling rule is selected PER DOCUMENT by a threshold-free signature — does the rule give one label to two cells on the same line — and the choice is declared on every FieldSet | `src/cdfc/evidence/fields.py` |
| 2026-08-20 | CORRECTION | AL_monthly was called row-labelling on a fields-per-label ratio of 21.6; the within-line signature is 0.00 — 30 questions asked of ~21 rows each, which is a field population | `src/cdfc/evidence/fields.py` |
| 2026-08-20 | DECISION | gate 127: a live document may not carry a claim the tree falsified; a dated record declares itself and is exempt whole | `ci/no-stale-claim.sh` |
| 2026-08-20 | DEFECT | the stale-claim gate's first run flagged six lines that were all its own author's correction notices — the marker set was too narrow | `docs/GATE-CHANGES.md` |
| 2026-08-20 | MEASUREMENT | A1c: structural correspondence aligns 3,747 of 3,747 CORRECTLY across a row insertion, where a name-based align is wrong on 1,451 of 3,544 | `src/cdfc/correspond/align.py` |
| 2026-08-20 | DEFECT | the aligner failed to align the blank to ITSELF — rows carrying no text had no signature and never entered the alignment; caught by the positive control | `src/cdfc/correspond/align.py` |
| 2026-08-20 | DECISION | correspondence is STRUCTURAL, not name-based: rows align as sequences by content signature and cells follow, because only 132 of 3,747 fields carry a label | `src/cdfc/correspond/align.py` |
| 2026-08-20 | CORRECTION | I reported A1c complete; it was scoped as THREE uses and one is built. Uses 2-3 are where Splink and Valentine belong, and N4 has not been run | `docs/PLAN.md` |
| 2026-08-20 | MEASUREMENT | N4: ours F1 0.964 vs Splink 0.915 on a degraded population — NOT a ranking, they are single points on different operating curves | `docs/measurements/N4-correspondence.md` |
| 2026-08-20 | DEFECT | three successive harness bugs each flattered our implementation; one had Splink scoring 0.000 and could have been published as a rout | `docs/measurements/N4-correspondence.md` |
| 2026-08-20 | DEFECT | our EM reported converged:False on a sound fit — an absolute parameter delta cannot serve values spanning six orders of magnitude; now converges on the log-likelihood in 54 iterations | `src/cdfc/correspond/link.py` |
| 2026-08-20 | DEFECT | a linkage could return neither a pair nor a refusal when all comparisons were worthless — records dropped silently; the dataclass now refuses to be constructed unless its states partition the input | `src/cdfc/correspond/link.py` |
| 2026-08-20 | CORRECTION | `PLAN.md §8 F4` and `docs/spike/README.md` said the regulation numbers are ABSENT from the pinned corpus, on a count of 3 in 197,767 characters. They are present — at the END of the heading unit, in the Gazette's margin column. The 3 is a true count of one construct read as a total over two | `docs/measurements/N1b-repin-execution.md` |
| 2026-08-20 | DECISION | the re-pin adds a DURABLE division layer over the existing units rather than re-extracting; coordinate keys keep working and citations made from here on survive a resegmentation | `src/cdfc/qualify/provisions.py` |
| 2026-08-20 | MEASUREMENT | N1b: the re-pin moved 0 bytes of addressable text across all ten instruments and invalidated 0 of 11 provision citations, against N1's predicted 11 of 11 — that prediction is true of a RESEGMENTATION and this is not one | `docs/measurements/N1b-repin-execution.md` |
| 2026-08-20 | DEFECT | `THIRD SCHEDULE` was published as "not recovered" while sitting mid-unit, 175 characters inside the second — a scan anchored at unit starts, publishing its own blind spot as a fact about the document | `docs/measurements/N1b-repin-execution.md` |
| 2026-08-20 | DEFECT | `div1_0148` carried 181 units — every schedule — because no second run bounded it, so a citation to "Repeal and Savings" returned the net-worth table | `src/cdfc/qualify/provisions.py` |
| 2026-08-20 | DEFECT | `(aa)(bb)(cc)` decoded base-26 as 27/54/81, so regulation 2 published 336 rows claiming ordinals were skipped that the document never numbered | `src/cdfc/qualify/provisions.py` |
| 2026-08-20 | DEFECT | `tests/golden/test_textsource_pins.py` pinned ONE digest and read a derived-layer addition as "every span is stale"; text and units are now pinned separately as `ADDRESSABLE_SHA256` | `tests/golden/test_textsource_pins.py` |
| 2026-08-20 | DEFECT | gate 128's control flipped NO guard on its first run: the comparison it breaks was written twice and `_select` consulted the other copy. Twelfth time in this repository a check has been defeated by something other than the thing it was checking | `docs/GATE-CHANGES.md` |
| 2026-08-20 | DEFECT | `tools/nc_sweep.py` selected its denominator with a CASE-SENSITIVE `status == "active"`, silently excluding five entries — `NC-A37` and the four `NC-DIV` controls. The headline read 141/141 over a set that omitted them; a failure in any would have been invisible. True figure 146/146 | `tools/nc_sweep.py` |
| 2026-08-20 | DECISION | the gate registry's phase vocabulary admits `N1`-`N9`: there are THREE numbering sequences, not the two CLAUDE.md §7 names, and a gate born from an experiment cannot be dated to a phase truthfully | `src/cdfc/gates.py` |
| 2026-08-20 | MEASUREMENT | N6: the division recovery is NOT corpus-independent. Over ELEVEN corpora the correct axis ranks first on 3 of 11 (shipped version 1 of 11), top-five on 5, and is induced at all for 9 | `docs/measurements/N6-corpus-independence.md` |
| 2026-08-20 | CORRECTION | `N1b §4` argued corpus-independence from the design rather than evidence, and the module's own docstring repeated it. Both now carry the measured figure | `docs/measurements/N6-corpus-independence.md` |
| 2026-08-20 | DECISION | the N6 prototype is NOT shipped into `src/`: it scores better and is unmeasured, ungated and outside the instrument digest. Replacing a measured component with a better-scoring unmeasured one is the trade this repository refuses | `docs/measurements/N6-corpus-independence.md` |
| 2026-08-20 | DECISION | a SECOND ingress: a field surface read from an XML SCHEMA's own declarations, so "whatever shape they arrive" stops meaning "whatever workbook" | `src/cdfc/schema/xsd.py` |
| 2026-08-20 | MEASUREMENT | D2: FinCEN BSA XML 2.0 -> 3,837 fields, 3,293 carrying the regulator's own label, 44 refused, 0.04s, zero configuration. The workbook ingress yields 132 usable labels of 3,747 | `docs/measurements/D2-xsd-ingress.md` |
| 2026-08-20 | DEFECT | the XSD reader flattened repeatable containers, so 3,837 was about to be published as a field surface comparable to the workbook's 3,747 cells. Every field sits under a `maxOccurs="unbounded"` ancestor: 0 of 3,837 are single-valued, and these are LIST PATHS not addresses | `docs/measurements/D2-xsd-ingress.md` |
| 2026-08-20 | DECISION | `xsd:decimal` is REFUSED as `type_declares_no_unit` rather than mapped to money: a schema declaring `decimal` has declared a number, not a currency, a scale or a unit, and all 44 refusals in this schema are exactly that | `src/cdfc/schema/xsd.py` |
| 2026-08-20 | DEFECT | the e2e harness printed "filing is correct." — a fragment of the CLI's own disclaimer *"It does not state that the filing is correct"*, caught by a prefix filter. The summary asserted the opposite of the one thing this product never says | `tools/e2e_multiformat.py` |
| 2026-08-20 | MEASUREMENT | E2E across three regulators and three ingress formats: IFSCA .xlsx VALID with 1,898 of 3,747 settled in 6.24s; EBA rule workbook 10,453 of 12,925 executed in 1.38s; FinCEN .xsd 3,837 fields in 0.04s. No filing was FILLED by any arm | `reports/e2e-multiformat.json` |
| 2026-08-20 | CORRECTION | D1 targeted four regulators and acquired two: sec.gov served HTML shells and returned AccessDenied on the IAPD feed, and the ESMA AIFMD technical package URL 404s. The SEC's RULES are pinned via 17 CFR 275 in the N6 corpora; its TEMPLATE is not | `docs/measurements/D2-xsd-ingress.md` |
| 2026-08-20 | DEFECT | the XSD reader called `etree.parse` directly — a SECOND door to lxml, bypassing `xmlsafe`'s XXE hardening, on schemas fetched from a regulator's public website. Caught by `test_nc__P08_only_one_parser_factory`, which walks the AST for exactly this | `src/cdfc/schema/xsd.py` |
| 2026-08-20 | DECISION | `corpus/regulators` is declared a PUBLIC corpus in the firewall whitelist rather than exempted silently: artefacts a regulator publishes carry no blind-fill answer and are meant to be read directly | `tests/test_corpus_firewall.py` |
| 2026-08-20 | DECISION | A5 ships as TWO LANES with SIX mechanical conditions; the trigger is byte-exact re-verification of a cited span, never a model's confidence — W0-C had a similarity locator return SUPPORTED 20 of 20 on DELETED evidence | `src/cdfc/fill/propose.py` |
| 2026-08-20 | DECISION | `cdfc.fill` joins `VERDICT_ROOTS`: a lane that decides which fields get a proposed value must not be able to consult the model whose proposals it adjudicates | `tests/negative/importgraph.py` |
| 2026-08-20 | DECISION | the binding is an INPUT to A5 with a required `binding_provenance`, not something A5 produces — a refusal that cannot say whose proposal it refused is not an audit record | `src/cdfc/fill/propose.py` |
| 2026-08-20 | MEASUREMENT | A5 against a deliberately crude binder admitted 0 of 13 bound fields, every refusal correct: 6 support_contradicted, 3 type_not_admitted, 1 vocabulary_not_admitted, 3 routed to the attestation lane. The guardrail held without being told the binding was bad | `docs/measurements/A5-fill-lane.md` |
| 2026-08-20 | MEASUREMENT | the FME return declares a type for 88 of 443 labelled fields and carries NO money field; 355 are UNDECLARED and therefore permanently unfillable. A property of the workbook, not of the fill lane | `docs/measurements/A5-fill-lane.md` |
| 2026-08-20 | CORRECTION | the first A5 run used the pinned STATUTE as its source and proposed 0 of 3,747 — correctly. A statute carries thresholds, not the entity's figures; a filing cannot be filled from the rulebook | `docs/measurements/A5-fill-lane.md` |
| 2026-08-20 | MEASUREMENT | N5-R: graph assembly and RDF projection are linear with no cliff — 424,000 nodes assemble in 0.136s and project 1,288,000 triples in 0.137s; adjacency runs at 0.2 ms. The scaling term is the PARSE, not the fold | `docs/decisions/D-A3-01a-amendment-re-derivation-at-scale.md` |
| 2026-08-20 | DECISION | D-A3-01 STANDS on re-opening — persist artefacts, re-derive the graph. Its reason was never performance: an accumulating graph is state outside `run_id_for`'s digest and `cdfc verify` cannot re-derive it. What the measurement changes is the read index's TRIGGER, now ~50 documents per ENTITY | `docs/decisions/D-A3-01a-amendment-re-derivation-at-scale.md` |
| 2026-08-20 | DEFECT | the ARTEFACT REGISTRY that `D-A3-01` closed by mandating DOES NOT EXIST: `cdfc.store` is a run store, `POST /v1/filings` returns `"persisted": false`, and no run names an uploaded artefact digest. The cross-upload user flow is blocked by that, not by the graph being a projection | `docs/decisions/D-A3-01a-amendment-re-derivation-at-scale.md` |
| 2026-08-20 | CORRECTION | my own per-artefact parse figure OVERSTATES the cost: ten pinned instruments cost 0.20s cold, not the 1.5s a 0.15s-per-artefact average predicts, because nine are small workbooks and one is a 1,218-unit statute | `docs/decisions/D-A3-01a-amendment-re-derivation-at-scale.md` |
| 2026-08-20 | DECISION | the ARTEFACT REGISTRY is content-addressed, immutable and has no update or delete: the Git object model applied to regulatory uploads, so `D-A3-01`'s hazard cannot arise — nothing an artefact digest names can change under it | `src/cdfc/registry/store.py` |
| 2026-08-20 | DECISION | a run's Merkle root is over THAT RUN'S inputs, never over the whole registry: a root over everything present would move under every unrelated upload and the run id would stop being a function of its own inputs | `src/cdfc/registry/store.py` |
| 2026-08-20 | DECISION | `ArtefactKind` is DECLARED by the uploader, never sniffed: an upload whose kind is wrong is a user error with a name, one whose kind was inferred wrongly is a silent one | `src/cdfc/registry/store.py` |
| 2026-08-20 | DECISION | W3C PROV-O and SHACL are adopted as EXPORT projections, not as dependencies. SHACL because the research is unambiguous that a CLOSED-WORLD constraint language is what regulation needs — the same rule as `absent != empty != zero`, already standardised — and because shapes stay a separate artefact whose execution model is decided independently | `src/cdfc/registry/shapes.py` |
| 2026-08-20 | DECISION | nothing in cdfc validates against the SHACL it emits, and `pyshacl`/`rdflib` stay absent: a shapes file we also validate with is a claim we grade ourselves, which is what `N4` made this project stop doing | `src/cdfc/registry/shapes.py` |
| 2026-08-20 | DEFECT | the shapes projection had no `enum` datatype mapping, so a shape emitted `cdfc:undeclared "the source declares no type"` in the same property block as an `sh:in` reciting that field's permitted values. 425 of 443 workbook shapes were marked undeclared; the true figure is 356 | `src/cdfc/registry/shapes.py` |
| 2026-08-20 | MEASUREMENT | E2E arm 4: three uploads across three days stored in 0.01s, one run naming 3 of 3, merkle root UNCHANGED under a later unrelated upload, 22 PROV triples and 4,280 SHACL shapes projected | `reports/e2e-multiformat.json` |
| 2026-08-20 | CORRECTION | the e2e run's own caveat said "the fill lane (A5) is not built" after A5 shipped. It is built and measured; it is not WIRED into this pipeline, which is a different statement | `tools/e2e_multiformat.py` |
| 2026-08-20 | DECISION | a delimited export is read by TWO independent parsers — `csv.reader` and a naive splitter — so a row whose field boundaries depend on which you believed becomes DISPUTED rather than resolved silently. Both are ours, so the corroboration is SAME_AUTHOR and never EXTERNAL | `src/cdfc/ingest/tabular.py` |
| 2026-08-20 | DECISION | the fill pipeline LOCATES every bound value in the source text and produces no observation for one it cannot find: a binder that handed A5 a value and a field would make `REVERIFIES` unfalsifiable, which is exactly the W0-C failure | `src/cdfc/fill/pipeline.py` |
| 2026-08-20 | MEASUREMENT | the full chain runs: two registry artefacts -> two-parser addressable text -> A1c matched 1 of 3 source columns with EM-derived weights -> span-located observations -> A5 admitted `1. Introduction!D10 = 'Registered FME (Retail)'` with all six conditions holding, in 0.35s | `src/cdfc/fill/pipeline.py` |
| 2026-08-20 | DEFECT | I wrote a test assertion ending in `or True`, which cannot fail — the same defect shape as a gate whose control flips no guard. Replaced with an assertion where the provenance actually lives | `tests/contract/test_fill_pipeline.py` |
| 2026-08-20 | DECISION | `POST /v1/filings` now stores the UPLOAD content-addressed and returns its digest and merkle root. What is persisted is the ARTEFACT, never the run: the run id is a digest of its inputs so the declaration re-derives, and a stored run would be state outside that digest | `src/cdfc/api/handlers.py` |
| 2026-08-20 | DEFECT | the endpoint's note promised the declaration was "reproducible with `cdfc run`" while THROWING THE UPLOAD AWAY when the request returned — the file it pointed at no longer existed on the server. The claim was true of the run id and false of the artefact | `src/cdfc/api/handlers.py` |
| 2026-08-20 | DECISION | GraphRAG REJECTED as a graph builder, admissible only as a LAYER 2 proposer — the same ruling Cognee got, for the same reason: every edge is LLM-extracted and would need re-adjudication. A community report cannot re-verify byte-exact because it is generated rather than quoted | `docs/decisions/D-A3-02-graphrag-is-a-proposer-not-a-graph.md` |
| 2026-08-20 | CORRECTION | E6's blocker — "there is no statutory instrument in this repository, there never has been one in its git history" — went STALE on 16 Aug when S1 pinned the IFSCA Regulations, and stood uncorrected for four days | `experiments/E6/DECISION.md` |
| 2026-08-20 | DECISION | E6 set to RETAIN-PROVISIONAL by the product owner on NO measurement, with the revocation condition recorded; `LAYER 2` is finally occupied and the model proposes bindings AS DATA | `experiments/E6/DECISION.md` |
| 2026-08-20 | DECISION | barrier 5 widened to admit RETAIN-PROVISIONAL, and ONLY when the record names who decided, states that no measurement supports it, and says what revokes it | `docs/GATE-CHANGES.md` |
| 2026-08-20 | DEFECT | barrier 5's new check used `^\>` in grep -E, where `\>` is a WORD BOUNDARY and not an escaped `>`, so the pattern could never match a line and the gate refused this repository's own correct record | `ci/barrier5.sh` |
| 2026-08-20 | DEFECT | the proposer wrapped only its built-in transport, so a caller-supplied client raising propagated raw — breaking the module's own promise that a transport failure never looks like a clean empty result | `src/cdfc/model/propose.py` |
| 2026-08-20 | DECISION | the proposer targets any Anthropic-compatible `base_url`, so subscription-proxy routing is a deployment choice; no credential is read from a file, logged, or placed in a proposal | `src/cdfc/model/propose.py` |
| 2026-08-20 | DECISION | GraphRAG's claim-extraction STAGE lifted into `cdfc.model.extract` rather than the package adopted — Option B. Measured cost of Option A: 132 packages incl. the Azure SDK trio, an INTERACTIVE `init` that hung 10+ minutes in automation, and a required embedding model DeepSeek does not serve | `src/cdfc/model/extract.py` |
| 2026-08-20 | DECISION | the model returns a VALUE and the EVIDENCE SENTENCE; it never returns a span. The span is computed by `str.find` in the source, so a fabricated evidence sentence yields NO observation and is counted `evidence_not_located` | `src/cdfc/model/extract.py` |
| 2026-08-20 | MEASUREMENT | deepseek-v4-flash extracted 3 of 3 claims from a source pack in 2.8s; all 3 located, all 3 re-verify byte-exact at spans this system computed | `src/cdfc/model/extract.py` |
| 2026-08-20 | DEFECT | factoring the shared transport out of `src/cdfc/model/propose.py` used a greedy regex that also consumed `parse()` and its docstring; the module imported and its tests collected as an ImportError | `src/cdfc/model/propose.py` |
| 2026-08-20 | MEASUREMENT | Option A closed on evidence: `graphrag index` validates the embedding model BEFORE any work, sends the DeepSeek key to OpenAI and 401s. DeepSeek serves no embedding model and neither does Anthropic, so dario would not fix it — GraphRAG needs a third provider | `src/cdfc/model/extract.py` |
| 2026-08-20 | DECISION | THE GATE IS RELAXED, on the product owner's direction: a model-synthesised value that NO SPAN supports is now ADMITTED, into a fourth lane `Derived`. Requiring a byte-exact span refused everything summed, restated or read off a chart, and that was holding back the semantic half for a property that only ever applied to QUOTED evidence | `src/cdfc/fill/propose.py` |
| 2026-08-20 | DECISION | the separation REPLACES the property it relaxes: `Derived` is never in `admitted()`, so no coverage figure counts it; it carries `supported_by` unit keys rather than spans; and `filled()` publishes both numbers as `N evidenced + M derived`. A reader gets both and can tell them apart | `src/cdfc/fill/propose.py` |
| 2026-08-20 | MEASUREMENT | D3: GraphRAG indexed 6,000 chars of the pinned instrument via deepseek-v4-flash + gemini-embedding-001, producing 29 entities, 45 relationships and 4 communities — and NO span column anywhere, only `text_unit_ids`. `cdfc.model.extract` produced 3 claims, all with spans that re-verify | `docs/measurements/D3-graphrag-vs-extract.md` |
| 2026-08-20 | DECISION | take BOTH, into different lanes: `extract` feeds the EVIDENCED lane with located spans, GraphRAG feeds the DERIVED lane with its text-unit references. They answer different questions and neither is a better version of the other | `docs/measurements/D3-graphrag-vs-extract.md` |
| 2026-08-20 | CORRECTION | `D-A3-02` ruled GraphRAG "a proposer at most" on a READING rather than a run. Running it: the community reports that ruling was built around never arrived — `Pipeline error: 'community'` — and the output it does produce fits the `Derived` lane, which did not exist when the ruling was written | `docs/decisions/D-A3-02-graphrag-is-a-proposer-not-a-graph.md` |
| 2026-08-20 | DEFECT | Gemini's OpenAI-compatible embeddings omit `index`, which GraphRAG's `LLMEmbeddingResponse` declares as `int` and refuses as `None`. A 25-line pass-through shim adding the field closed it; the embeddings themselves were never the problem | `docs/measurements/D3-graphrag-vs-extract.md` |
