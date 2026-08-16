# ci/GATES.md — THE GATE REGISTRY

**Append-only.** A row is never edited in place and never deleted. A row that changes its `liveness`
carries an appended, dated argument naming the row, in `docs/GATE-CHANGES.md`.

**Why this file is a registry and not a list.** P0's exit gate was originally `gates_live ==
gates_written`, where `gates_written` meant "the gates whose subject exists" — decided by the same person
deciding whether a gate can be demonstrated. Any gate that resisted demonstration could be moved to
`PENDING` and the ratio would become `n/n`. **The gate could not fail.** So the `LIVE` set is
*pre-registered as a literal set* in `tests/contract/test_contract__live_set_is_pre_registered`, and moving
a row between sets fails the build.

## Columns

| Column | Meaning |
|---|---|
| `id` | stable integer, never reused |
| `kind` | `grep` · `ast` · `pytest` · `schema` · `shell` |
| `subject_exists_at` | the phase at which the thing this gate guards first exists |
| `demonstrable_red_at` | the phase at which this gate can first be *observed failing*. **Never empty.** |
| `broken_build` | the named injector or condition that makes it red |
| `liveness` | `LIVE` (runs and can fail today) · `PENDING` (subject does not exist yet) |

## The rows

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 1 | shell | `ci/no-green-tick.sh` — no all-clear glyph or phrase on a user surface | P0 | P0 | `injectors/green_tick.py` writes a check mark into `report.html.j2` | LIVE |
| 2 | shell | `ci/no-bare-except.sh` — no bare `except:` in any scan root | P0 | P0 | `injectors/bare_except.py` | LIVE |
| 3 | shell | `ci/scan-roots-exist.sh` — every root in `labels.SCAN_ROOTS` exists | P0 | P0 | `injectors/remove_scan_root.py` | LIVE |
| 4 | pytest | `test_nc__CI02_openpyxl_warning_is_an_error` — warnings are errors | P0 | P0 | `injectors/warnings_tolerated.py` | LIVE |
| 5 | pytest | `test_det__lockfile_is_hash_pinned` — every dep carries a wheel hash | P0 | P0 | remove a `--hash=` line | LIVE |
| 6 | contract | `test_contract__gates_registry_schema` — every row well-formed, ids unique | P0 | P0 | duplicate an id in this file | LIVE |
| 7 | contract | `test_contract__pending_rows_name_a_phase` — no permanently-pending gate | P0 | P0 | blank a `demonstrable_red_at` | LIVE |
| 8 | contract | `test_contract__live_set_is_pre_registered` — the LIVE set is a literal | P0 | P0 | move any row between LIVE and PENDING | LIVE |
| 9 | pytest | `test_cli__unimplemented_subcommand_exits_nonzero` — a stub exits 2, not 0 | P0 | P0 | `injectors/stub_exits_zero.py` | LIVE |
| 10 | pytest | `test_cli__version_reports_gate_count` — printed count equals parsed rows | P0 | P0 | add a row without touching `cli.py` | LIVE |
| 11 | shell | `ci/licence-denylist.sh` — no denylisted licence in the resolved set | P0 | P0 | two denylisted packages are installed right now | LIVE |
| 12 | shell | `ci/catalogue-ids.sh` — the CATALOGUE's ids unique, every injector and guard resolvable, plan docs UTF-8 (plan cross-references ADVISORY, counts printed) | P0 | P0 | duplicate an id, or a guard naming a file that does not exist | LIVE |
| 13 | pytest | `test_nc__CI01_missing_scan_root_fails` — a grep over a missing root is red | P0 | P0 | `injectors/remove_scan_root.py` | LIVE |
| 14 | ast | `test_no_model_in_verdict_path` — no model client reachable from L5/L6/L7 | P5 | P5 | import a model client in `verdict/` | LIVE |
| 15 | schema | attestation schema has no `result`/`status`/`pass` at any depth | P11 | P11 | `injectors/banned_names_substring_only.py` — and NC-A01's `schema_status_deep` shape, a `status` inside a `$defs` entry referenced from an `allOf` two levels down | LIVE |
| 16 | pytest | `test_prop__closure_seven_terms` — the seven-term closure invariant holds | P5 | P5 | `injectors/closure_drops_a_bucket.py` | LIVE |
| 17 | shell | `ci/no-timing-in-hashed-payload.sh` — no duration field inside a hashed object | P0 | P0 | `injectors/elapsed_us_in_canary_row.py` | LIVE |
| 18 | pytest | `test_plan__critical_path_total_equals_sum_of_rows` — a total equals its parts | P0 | P0 | change a per-phase figure without the total | LIVE |
| 19 | shell | `ci/no-external-paths.sh` — no machine-local absolute path in the build | P0 | P1 | `injectors/external_fixture_path.py` | LIVE |
| 20 | shell | `ci/no-float-money.sh` — no float in the deterministic numeric core | P3 | P3 | `injectors/float_in_calc.py` | LIVE |
| 21 | shell | `ci/no-regex-over-cel.sh` — key extraction never uses a regex over CEL | P4 | P4 | add a second `re.` use to `ast_walker.py` | LIVE |
| 22 | pytest | `test_nc__Q41_every_record_field_is_inside_the_digest` — the envelope digest covers every field of the record | P4 | P4 | `injectors/projection_drops_a_field.py` | LIVE |
| 23 | pytest | `test_nc__Q42_the_two_key_mismatches_raise_different_types` — the both-ways check keeps its two remedies apart | P4 | P4 | `injectors/keys_mismatch_collapsed.py` | LIVE |
| 24 | pytest | `test_nc__Q46_a_construct_outside_the_class_set_is_recorded` — the weak pile is counted, not dropped | P4 | P4 | `injectors/weak_pile_dropped.py` | LIVE |
| 25 | pytest | `test_nc__Q48_claims_precede_the_campaign_and_do_not_vary_per_predicate` — the G2 denominator is declared per class | P4 | P4 | `injectors/claims_from_kill_vector.py` | LIVE |
| 26 | pytest | `test_nc__Q49_reg_resolves_never_answers_without_a_snapshot` — a host function never resolves live | P4 | P4 | `injectors/host_fn_resolves_live.py` | LIVE |
| 27 | contract | `test_contract__committed_schema_matches_the_generated_one` — the predicate schema is generated from the record | P4 | P4 | edit the schema without touching `envelope.py` | LIVE |
| 28 | shell | `ci/no-regex-over-xml.sh` — no regular expression reads or rewrites OOXML | P1 | P5 | add a pattern over `<c r=...>` to any scanned module | LIVE |
| 29 | pytest | `test_nc__E20_cells_bound_zero_is_error_before_expr_runs` — the vacuous pass is unreachable, not repaired | P5 | P5 | `injectors/cells_bound_after_expr.py` | LIVE |
| 30 | pytest | `test_nc__E21_run_cell_is_materialised_from_the_field_surface` — the cell table IS the denominator | P5 | P5 | `injectors/cells_from_evaluations.py` | LIVE |
| 31 | pytest | `test_nc__E22_invalid_carries_a_present_null` — null is not zero and not omitted | P5 | P5 | `injectors/invalid_emits_zero.py` | LIVE |
| 32 | pytest | `test_nc__E23_no_run_level_cause_appears_in_the_item_vocabulary` — two vocabularies, disjoint | P5 | P5 | `injectors/run_cause_in_item_reason.py` | LIVE |
| 33 | pytest | `test_nc__E24_a_degenerate_precondition_does_not_leave_the_denominator` — nothing derived from the filing's values removes a cell | P5 | P5 | `injectors/value_derived_removal.py` | LIVE |
| 34 | pytest | `test_nc__E25_an_informational_only_cell_is_no_predicate` — a template defect cannot raise the headline | P5 | P5 | `injectors/informational_only_leaves.py` | LIVE |
| 35 | pytest | `test_nc__E03b_contract_is_generated_not_edited` — EVALUATION-CONTRACT.md is generated | P5 | P5 | `injectors/contract_table_edit.py` | LIVE |
| 36 | pytest | `test_nc__E02b_preflight_blocks_expr_when_a_declared_key_is_absent` — a disjunction never returns PASS over an unchecked key | P5 | P5 | `injectors/preflight_disabled.py` | LIVE |
| 37 | shell | `ci/no-bare-rate.sh` — a rate never renders without both integers of its fraction | P6 | P6 | remove the fraction beside any published rate | LIVE |
| 38 | shell | `ci/no-openpyxl-writer.sh` — nothing under `qualify/` writes a workbook except `surgery.py` | P6 | P6 | `injectors/mutant_via_openpyxl.py` | LIVE |
| 39 | pytest | `test_nc__Q33_operator_edit_moves_the_digest` — `v3` is a checkable claim, not a label | P6 | P6 | `injectors/fault_digest_constant.py` | LIVE |
| 40 | pytest | `test_nc__Q31_filter_recalculates` — the observability filter recalculates, never reads cached values | P6 | P6 | `injectors/observability_cached_grid.py` | LIVE |
| 41 | pytest | `test_nc__Q60_unevaluable_cells_do_not_become_unobservable` — F18: our apparatus is not the fault model | P6 | P6 | `injectors/notrun_counts_as_identical.py` | LIVE |
| 42 | pytest | `test_nc__Q61_observability_uses_filing_formulas` — F19: the flagship class reaches the denominator | P6 | P6 | `injectors/observability_uses_template_formulas.py` | LIVE |
| 43 | pytest | `test_nc__Q37_unobservable_are_retained` — an unobservable mutant keeps its reason on disk | P6 | P6 | `injectors/discard_unobservable.py` | LIVE |
| 44 | pytest | `test_nc__Q32_control_excludes_the_cone` — the spurious-fire threshold is exactly zero | P6 | P6 | `injectors/control_from_read_set_complement.py` | LIVE |
| 45 | pytest | `test_nc__Q06a_site_set_is_the_field_surface` — the universe cannot see the predicates | P6 | P6 | `injectors/sites_from_read_set.py` | LIVE |
| 46 | pytest | `test_nc__E08_counts_get_zero_tolerance` — a person is not a rounded quantity | P6 | P6 | `injectors/tolerance_on_counts.py` | LIVE |
| 47 | contract | `test_contract__fault_model_doc_is_generated` — the taxonomy document is generated from the code | P6 | P6 | hand-edit `docs/FAULT-MODEL-v3.md` | LIVE |
| 48 | shell | `ci/no-wallclock-z3.sh` — Z3 is bounded by `rlimit`, never a wall clock | P7 | P7 | plant `set("timeout", …)`, or a `z3.Solver()` with no rlimit | LIVE |
| 49 | pytest | `test_nc__Q50_disputed_regions_are_excluded` — a span into text one extractor never saw is not a span | P7 | P7 | `injectors/TextsourceSingleExtraction` | LIVE |
| 50 | pytest | `test_nc__Q51_disposition_of_a_clauseless_candidate_is_specified_and_counted` — G0 computes a disposition, never a skip | P7 | P7 | `injectors/G0SkipsClauseless` | LIVE |
| 51 | pytest | `test_p7__both_obligation_counts_render_or_neither_does` — C2's two numbers, never one | P7 | P7 | render one obligation-coverage count alone | LIVE |
| 52 | pytest | `test_nc__Q34_order_is_enforced_by_shape` — the free gate runs before the expensive one | P7 | P7 | `injectors/GateOrderShuffled` | LIVE |
| 53 | pytest | `test_nc__Q38_domain_separation_is_load_bearing` — the registry root identifies what ran | P7 | P7 | `injectors/MerkleNoDomainSep` | LIVE |
| 54 | pytest | `test_nc__Q55_admission_requires_a_human` — R7, and `UNSIGNED` is published beside the count | P7 | P7 | `injectors/AdmitAutosign` | LIVE |
| 55 | pytest | `test_nc__Q07_unknown_is_unproven` — UNPROVEN is never PROVED | P7 | P7 | `injectors/Z3UnknownIsOk` | LIVE |
| 56 | pytest | `test_nc__Q36_removal_is_recorded` — a predicate never vanishes from the registry silently | P7 | P7 | `injectors/IlpSilentRemoval` | LIVE |
| 57 | pytest | `test_nc__Q58_template_computed_cannot_license_an_arithmetic_ffr` — F2: a corpus we generated cannot license an arithmetic FFR | P8 | P8 | `injectors/TcLicensesArithmetic` | LIVE |
| 58 | pytest | `test_nc__Q59_independence_is_computed_not_declared` — F5: the field is a RESULT, not a string | P8 | P8 | `injectors/IndependenceHardcoded` | LIVE |
| 59 | pytest | `test_nc__Q56_wilson_is_decimal` — the interval re-derives on another machine | P8 | P8 | `injectors/WilsonFloat` | LIVE |
| 60 | pytest | `test_nc__Q10_set_ffr_is_at_least_one_not_a_mean` — the registry cannot drift to flag-everything | P8 | P8 | `injectors/SetFfrIsMean` | LIVE |
| 61 | pytest | `test_nc__Q09_severity_uses_wilson_upper` — a sample of four cannot buy BLOCKING | P8 | P8 | `injectors/SeverityPointEstimate` | LIVE |
| 62 | pytest | `test_severity__synthetic_corpus_cannot_buy_blocking` — F2's second half: the non-synthetic floor | P8 | P8 | `injectors/SyntheticBuysBlocking` | LIVE |
| 63 | pytest | `test_nc__Q65_a_mixed_column_blocks_expr` — a heterogeneous column is decidable, and never reaches the runtime | P8 | P8 | `injectors/MixedColumnProceeds` | LIVE |
| 64 | pytest | `test_contract__formula_source_is_explicit` — every `recalculate` call site passes a LITERAL source | P3 | P9 | edit any call site to pass a variable | LIVE |
| 65 | pytest | `test_arm_two_author_is_not_the_evaluator_author` — G-EVAL's independence label is computed, not declared | P3 | P9 | set `ARM2.oracle_author` to `cdfc` | LIVE |
| 66 | pytest | `test_nc__R01a_all_zero_filing_is_OUT_OF_SCOPE` — a relation never PASSes an empty filing | P9 | P9 | `injectors/RelationNoPrecondition` | LIVE |
| 67 | pytest | `test_nc__R02a_binding_outside_the_denominator_aborts_closure` — a finding binds inside the field surface | P9 | P9 | `injectors/TdBindsTheFormulaCell` | LIVE |
| 68 | pytest | `test_unqualified_relation_cannot_settle_a_cell` — the B1 spike is a demonstration, not an admission | P9 | P9 | `injectors/RelationWithoutQualification` | LIVE |
| 69 | pytest | `test_nc__R04a_declared_defect_is_INFORMATIONAL_not_FAIL` — a defective oracle never fails a filer | P9 | P9 | `injectors/DefectTableIgnored` | LIVE |
| 70 | pytest | `test_nc__R05a_a_cross_basis_relation_does_not_load` — no relation spans two accounting bases | P9 | P9 | `injectors/BasisGuardDisabled` | LIVE |
| 71 | pytest | `test_nc__R06a_the_probe_seed_is_a_pinned_constant` — the probe seed is an input, not entropy | P9 | P9 | `injectors/ProbeSeedFromEntropy` | LIVE |
| 72 | pytest | `test_nc__R07a_redundant_relation_is_removed_and_the_removal_is_recorded` — a rename does not inflate the delta | P9 | P9 | `injectors/SubsumptionCheckDisabled` | LIVE |
| 73 | pytest | `test_nc__R09a_a_degenerate_precondition_stays_in_the_denominator` — filling in less never scores better | P9 | P9 | `injectors/DegenerateScopeLeavesTheDenominator` | LIVE |
| 74 | pytest | `test_defect_table_cannot_raise_the_settled_fraction` — declaring a defect never raises the headline | P9 | P9 | `injectors/DefectMovesASoleEvaluationOutOfScope` | LIVE |
| 75 | pytest | `test_nc__R12a_the_tolerance_unit_mismatch_is_still_open` — a half repair of the unit defect cannot land quietly | P9 | P9 | `injectors/ToleranceUnitsSilentlyReconciled` | LIVE |
| 76 | shell | `ci/no-clock-in-core.sh` — no clock, wall or monotonic, in the deterministic core | P0 | P9 | `injectors/WallClockInCore` | LIVE |
| 77 | shell | `ci/no-bare-absence.sh` — every absence claim cites a ledger row whose positive control is positive | P0 | P9 | `injectors/BareAbsenceOnASurface` | LIVE |

**Rows 17 and 18 exist as gates from the first commit, dated 11 Aug 2026, and their reason is recorded
rather than assumed.** Row 17: a `CanaryRow.elapsed_us` inside a canonicalised payload was found in the
plan and would have made byte-identical re-derivation impossible; the gate exists before the payload does.
Row 18: a displayed critical-path total that did not equal the sum of its own rows was found in the plan,
which is the shared-denominator error in a schedule; the gate exists before any other total does.

**The LIVE/PENDING split is NOT restated here as a literal.** This line used to read
*"LIVE = {1,…,14,16,…,63} (62 rows). PENDING = {15} (1 row). Total 63."* while the file carried 75
rows with 74 LIVE — it had drifted twelve rows and nothing noticed, because no test read it. That
is the shared-denominator shape row 18 exists to catch, occurring in the registry itself.

The authoritative split is the frozen literal set in
`tests/contract/test_contract_gates.py` (`LIVE_AT_P0` plus one `ADDED_LIVE_AT_Pn` per phase, never
an edit to an earlier one), and the current counts are PRINTED by `tools/gate_liveness.py` on every
run. A count in prose beside a table is a second answer to a question the table already answers.

**Row 20 was added at P3, dated 11 Aug 2026.** R4 requires the evaluator to be `Decimal` from its first line rather than converted later; the gate exists so that cannot drift in unnoticed.

**Row 19 was added at P1, dated 11 Aug 2026, with its reason recorded rather than assumed.** A negative
control was found still pointing at the external directory the corpus was vendored FROM, so it was
validated against bytes that could drift — and the repository was not portable. Adding a row is an
append-only change and the pre-registered LIVE set moves with it, in one commit, with this paragraph as
the dated argument `test_contract__live_set_is_pre_registered` requires.

**Rows 21–27 were added at P4, dated 12 Aug 2026.** Each guards something P4 built and each names
an injector that was observed making it red in the same session.

Row 21's reason is recorded rather than assumed: one level up, `<f[ >][^>]*>` over OOXML returned a
CORRECT COUNT with WRONG BODIES, and the same defect over CEL would be worse — the thing extracted
is the key set, and the key set is the settled fraction's denominator.

Row 22's reason: the envelope digest is the registry's admission key. A field outside the digest can
be changed after admission without producing a new predicate, and `claims_fault_classes` is exactly
such a field — narrowing it after a campaign would otherwise leave the qualification record intact.

Row 24's reason: an undeclared suppression is a coverage lie. The harvest may under-produce; it may
not omit silently.

**A defect this phase found in an EXISTING row, recorded because the gate did not catch it.** Row 3's
injector (`RemoveScanRoot`) deleted `src/cdfc/evaluate/__init__.py` and then `rmdir`-ed the
directory with the failure suppressed. That worked while `evaluate/` held one file. P4-B3 added
`celrt.py`, the `rmdir` began failing silently, the directory went on existing, and **the flagship
P0 negative control proved nothing while still reporting itself as caught.** The sweep could not see
it: the injector applied cleanly and the tree restored exactly. It was found because the guard test
went red for the right reason. The injector now removes every file under the root.

**Rows 28–36 were added at P5, dated 12 Aug 2026.**

Row 28's reason is the one worth reading: `ci/no-regex-over-cel.sh` named this gate as *"the
sibling"* at P4 and **the sibling did not exist**. At P5 the filing generator rewrote `<c>`
elements with a pattern, produced malformed XML, and LibreOffice "repaired" the result by dropping
424 of the workbook's 505 formulas — the formula count then read 81. On its first run the new gate
also found a PRE-EXISTING instance in `tools/fixtures/make_synthetic.py`, which had been building
the adversarial fixtures with the technique this project bans. Same defect shape as
`<f[ >][^>]*>` over the same format: **a correct count with wrong contents, three times now.**

Row 33 is the one the product's headline number depends on. A cell may leave the in-scope
denominator only for a reason that is a function of the template, the selection, or a declared
filer characteristic — **never a function of the filing's own cell values.** Without it a filer who
fills in less gets a better settled fraction.

**Rows 37–47 were added at P6, dated 13 Aug 2026.**

Row 37's reason is arithmetic history. The v0 harness printed `MS = 18.09%` over a denominator
nobody could reconstruct — `|mutants| − |equivalent|`, where `equivalent` is a THEOREM that was
asserted rather than proved — and a later harness printed **100.1%**, which is impossible and went
unnoticed because *a percentage carries no evidence of its own arithmetic*. On its first run this
gate found fourteen bare rates in this repository, including one in a published measurement file.

Rows 41 and 42 are F18 and F19, and both are failures of the *measurement* rather than of the
product. F18: a cell our evaluator cannot compute is identical in both grids by construction, so a
two-way classification banks its mutants as unobservable, removes them from `O`, and — because
`O = G − U − I` — **raises** our own kill rate. F19: recalculating an F11 override through the
TEMPLATE's formula graph overwrites the literal with the formula's value, so the flagship class
classifies unobservable with `O = 0` and `TEMPLATE_DIFF` could never clear G2.

**Rows 14 and 16 moved PENDING to LIVE at P6, dated 13 Aug 2026, and the audit is why.**

Both were registered `PENDING` at P0 because their subjects did not exist. **Both subjects shipped
at P5** — `src/cdfc/verdict/` and the seven-term closure — and the P6 audit found the rows still
`PENDING`. That matters: `PENDING` is the state that lets a gate avoid demonstration, and the whole
reason this file is a registry rather than a list is that a gate which resists demonstration must
not be able to sit in a set nobody has to keep green. **A gate whose subject has shipped and which
is still PENDING is a gate nobody has to keep green.**

Row 15 (the attestation schema) stays `PENDING` honestly: its subject is P11's and does not exist.

**Rows 48–56 were added at P7, dated 13 Aug 2026, and each names an injector observed making it
red in the same session.**

Row 48's reason is determinism: `set("timeout", ms)` makes a proof verdict a function of what else
the machine was doing, so the same candidate is `unknown` on a loaded runner and `trivially_true`
on an idle one and a predicate's ADMISSION becomes a property of the CI queue. On its first run the
gate matched the sentence in `g3_degeneracy.py` that EXPLAINS why a timeout is banned — a gate that
fires on its own rationale gets "fixed" by deleting the rationale, so it now strips comments and
scans code.

Row 51 is arbitration C2 and it fires in BOTH directions: `0/572` alone is wrong by 572 under F9's
ruling, and `572/572` alone conceals that nothing here is grounded in a statute.

Row 55's reason is the one worth reading. `unknown` from the proof arm means *nobody could decide
this*, and reading it as `non_degenerate` would admit 47 of 349 FME candidates on a proof nobody
has. It is also NOT a rejection: rejecting it would refuse those 47 for a limitation of our own
translator. Three outcomes, and collapsing any pair of them is a defect.

`ADDED_LIVE_AT_P7` is a fifth frozen literal, so no row that was ever LIVE can leave the set by
being edited out of a growing list.

**Rows 57–62 were added at P8, dated 13 Aug 2026, all LIVE, all observed red in the same session.**

Rows 57 and 58 are **F2 and F5**, and they are the two the plan calls the adversary's. Before this
phase `clean_corpus_independent_of_predicate` was a field in a YAML file that **no build computed,
no test asserted, no negative control broke and no gate read** — and the corpus generator let
`src/cdfc/calc/` compute the very cells the arithmetic predicates re-check. An arithmetic
predicate's expected false-failure rate was therefore zero *regardless of its quality*, and
`n = 189` bought a `BLOCKING` tier in an afternoon.

Row 62 is F2's second half and it is the one that survives a foreign oracle: the interval is a
statement about a SAMPLE, and a sample the product generates is unbounded in `n` at a cost of one
command. `BLOCKING` needs thirty filings a person or the world produced, whatever the interval says.

`ADDED_LIVE_AT_P8` is a sixth frozen literal.

**Row 63 was added 14 Aug 2026, and it is the only gate in this registry whose subject was found by
an input nobody in this project produced.** The blind-fill probe handed the evaluator a column of
45 numbers and 125 numeric strings; `c.v >= 0` over it took the process from 85 MB to **6 GB
without returning**, and `Budget(steps=2000)` could not stop it because the step meter ticks only
on fact-tree access and the blow-up is inside the runtime. `celrt.Budget`'s own docstring names
that state: *a declared budget nobody enforces is worse than no budget.* Pre-flight now refuses a
heterogeneous column — decidably unsatisfiable, not undecidable — and the predicate reports
`NOT_RUN` in 0.0 s at 90 MB.

**Rows 78–90 were added at P10, dated 14 August 2026, all LIVE, all observed red in the same
session.** They are L6.5's gates and they divide into three kinds.

Rows 78–79 are **adversary F23**, and they are the phase's cheapest structural gates: no duration
field inside any dataclass that reaches a hash, and no clock reachable from `src/cdfc/selfcheck/`
at all. The second is stronger than the plan asked for. `plan/05` puts `timings.py` inside the
selfcheck package, which would have required widening `ci/no-clock-in-core.sh` — the gate the F23
ruling extends in the same breath — so the timing lives in `src/cdfc/measure/perf/` and the loop
**cannot** read a clock rather than being trusted not to.

Rows 80–83 are §P10·L's own gates. Row 80 is the one a reviewer should look for first: under every
apparatus break the `invalid` cause set is **exactly** `{canary_silent}`, which is what makes the
control a statement about the canary layer rather than about whichever layer happened to fire.
Row 81 is its indispensable twin — without an admission-side positive control, all six deaths are
satisfied by a layer that returns `INVALID` unconditionally. Row 82 proves liveness is demonstrated
on the in-memory fact table, with a `sys.addaudithook` over the real `open` event rather than an
import scan, and arms the hook over a deliberate open so its silence means something. Row 83 is
§P10·L.4's single line: the expected-silent set is a module constant, never derived from the loaded
registry.

Rows 84–87 are B2/B3/B4's refusals — a threshold that moved without its dated row, a `|RESIDUE|`
printed without the rejector set it was computed against, an adjudication with no argument, and the
2,790-cell recompute-blind measurement with its paired value assertion.

Rows 88–89 are the two defects P10 found in earlier phases by running against them: the counts are
`len()` of a row set rather than a variable (death D5), and a cell with no value is `ABSENT` and
never the four-character string `"None"` (D-P10-01, which cost 68 of 257 recorded kills).

Row 90 is **adversary F6 in its general form**: every `injector: NONE` catalogue row whose claim is
that some layer did *not* fire must carry a `layer_exists_assertion`, because *"the renamed sheet
produced `template_unbound` and not `canary_silent`"* is trivially true of a system with no canary
layer at all.

`ADDED_LIVE_AT_P10` is a seventh frozen literal.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 78 | contract | `test_contract__no_duration_field_in_a_hashed_object` — no duration inside any hashed dataclass | P10 | P10 | `injectors/elapsed_us_in_canary_row.py` | LIVE |
| 79 | contract | `test_contract__no_clock_is_reachable_from_the_selfcheck_package` — the loop cannot read a clock | P10 | P10 | import `time` into `src/cdfc/selfcheck/` | LIVE |
| 80 | pytest | `test_liveness__only_cause_is_canary_silent` — under an apparatus break the cause set is exactly `{canary_silent}` | P10 | P10 | `injectors/canaries_noop.py` · `keys_resolver_offbyone` · `celrt_short_circuits` · `apply_returns_clean_facts` | LIVE |
| 81 | pytest | `test_canary__healthy_run_is_VALID` — a healthy run is VALID with digits | P10 | P10 | `injectors/keys_resolver_offbyone.py` | LIVE |
| 82 | pytest | `test_nc__C05c_no_artifact_is_opened_during_the_canary_loop` — liveness is proved in memory | P10 | P10 | `injectors/canary_reopens_file.py` | LIVE |
| 83 | pytest | `test_st__expected_set_is_a_constant` — the expected-silent set is never derived from the registry | P10 | P10 | `injectors/selftest_behind_a_flag.py` | LIVE |
| 84 | pytest | `test_th__ceiling_is_pre_registered` — a threshold moves only with its dated row | P10 | P10 | change `CANARY_INAPPLICABLE_CEILING` without touching `docs/SELFCHECK-THRESHOLDS.md` | LIVE |
| 85 | pytest | `test_res__renderer_refuses_without_all_five_fields` — the residue count never prints without its rejector set | P10 | P10 | blank any of the five fields | LIVE |
| 86 | pytest | `test_adj__verdict_without_argument_is_refused` — an adjudication with no argument is an opinion wearing a schema | P10 | P10 | remove the `argument` check from the loader | LIVE |
| 87 | pytest | `test_golden__2790_cells_feed_no_formula` — the recompute-blind set, with a paired value assertion | P10 | P10 | change the pinned count without the per-sheet split | LIVE |
| 88 | pytest | `test_c__counts_are_row_counts_not_variables` — every published liveness count is `len()` of a row set | P10 | P10 | `injectors/canary_count_asserted.py` | LIVE |
| 89 | pytest | `test_patch__none_is_absent_never_the_string` — a cell with no value is ABSENT | P6 | P10 | `injectors/coerce_none_to_string.py` | LIVE |
| 90 | pytest | `test_nc_meta__none_injector_entries_carry_a_layer_exists_assertion` — an absence claim proves the layer exists | P10 | P10 | delete `layer_exists_assertion` from NC-C03 | LIVE |

**Rows 91–98 were added at P11, dated 15 August 2026, all LIVE, all observed red in the same
session.** They are L7's gates, and row 15 — which has been `PENDING` since P0 — goes **LIVE** here
because its subject now exists.

Row 91 is the one P0 wrote and could not run: *the attestation schema has no `result`/`status`/`pass`
at any depth*. It has waited eleven phases for something to walk, and the walk is a total descent
through `properties`, `$defs`, `definitions`, `allOf`, `anyOf`, `oneOf`, `not`, `items`,
`prefixItems`, `patternProperties`, `additionalProperties` and `propertyNames` — because NC-A01's
injector plants `status` inside a `$defs` entry referenced from an `allOf` two levels down, and a
walker that reads only top-level `properties` finds nothing and reports success.

Row 92 is the other half of the same rule and it is the half that needs an argument: the blocking
scan is EXACT because a substring scan rejects the specification's own `canariesPassed`, and the
advisory scan is a substring scan because an exact one admits `overallStatus`. Every advisory hit
carries a written argument in `NAME-ALLOWLIST.md`, checked equal in **both** directions.

Row 94 is worth reading twice. `expires_from_now` turns `E2E-VERIFY` red — the byte-identity
acceptance test catching a single clock read three layers away, without being told where to look.
That is what the whole phase is for.

Row 97 is the projection refusal, and its substance is the absence of a flag: `project_oscal`
raises on an `INVALID` run and there is no parameter that makes it emit one anyway, because a flag
is what somebody sets when a pipeline is failing and the deadline is Friday.

`ADDED_LIVE_AT_P11` is an eighth frozen literal, and row 15 moves from `PENDING` to `LIVE` with its
argument recorded in `docs/GATE-CHANGES.md`.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 91 | contract | `test_contract__attestation_cannot_express_a_pass` — no banned property name at any depth | P11 | P11 | `injectors/banned_names_substring_only.py` | LIVE |
| 92 | contract | `test_contract__banned_names_are_exact_not_substrings` — the three-part name rule, both halves | P11 | P11 | `injectors/banned_names_substring_only.py` | LIVE |
| 93 | contract | `test_contract__no_json_float_in_the_payload` — no JSON float token in the canonicalised bytes | P11 | P11 | `injectors/float_rate_in_payload.py` | LIVE |
| 94 | pytest | `test_prop__expires_is_a_function_of_time_verified` — no clock in the attestation | P11 | P11 | `injectors/expires_from_now.py` | LIVE |
| 95 | pytest | `test_v__verify_never_calls_sign` — verify checks the stored signature, never a fresh one | P11 | P11 | `injectors/verify_resigns.py` | LIVE |
| 96 | pytest | `test_e2e__VERIFY_byte_identical` — the payload re-derives and the signature is valid | P11 | P11 | `injectors/expires_from_now.py` | LIVE |
| 97 | pytest | `test_oscal__invalid_raises_not_representable` — an INVALID run projects to nothing | P11 | P11 | `injectors/oscal_projects_invalid.py` | LIVE |
| 98 | pytest | `test_v__the_non_determinism_document_lists_six_and_six` — the enumeration is complete and says what it has not verified | P11 | P11 | delete a row from `docs/NON-DETERMINISM.md` | LIVE |

---

## P12 — the settling experiment (rows 99–107)

Nine rows, and they guard a property no earlier phase has: **not that a filing was judged
correctly, but that the criterion which decides what the result MEANS was fixed before the result
existed.** Rows 99–101 are the pool and the estimator; 102–104 the run's refusals; 105–107 the
decision's purity and the pool's ordering.

Row 105 is the one to read twice. `decide()` acquiring a keyword-only `override=None` changes no
behaviour and passes every behavioural test — so the gate is a **signature** check, and its
positive control staying green under the injection is the demonstration that nothing behavioural
could have caught it.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 99 | pytest | `test_nc__M02a_h0_mismatch_fails_the_build` — the pre-registration's h0 cannot move | P12 | P12 | `PreregEditThreshold` | LIVE |
| 100 | pytest | `test_nc__M03_decidable_fraction_uses_all_drawn` — the Stratum-B cap never truncates the denominator | P12 | P12 | `TruncateBDenominator` | LIVE |
| 101 | pytest | `test_nc__M04a_both_estimators_are_reported_and_labelled` — inverse sampling is corrected, not assumed away | P12 | P12 | `NaiveRatioEstimator` | LIVE |
| 102 | pytest | `test_nc__M10a_retry_is_impossible_not_merely_banned` — no attempt parameter, and max_retries is a rule | P12 | P12 | `ProposeRetry` | LIVE |
| 103 | pytest | `test_nc__M11_funnel_stage_zero_equals_the_planned_count` — the discard pile is stage 0 | P12 | P12 | `FunnelDropsDiscards` | LIVE |
| 104 | pytest | `test_nc__M13a_qualify_import_closure_has_no_model_client` — no model on the qualification or verdict path | P12 | P12 | `ModelClientInQualify` | LIVE |
| 105 | pytest | `test_nc__M16b_inadmissible_arguments_cannot_enter_decide` — decide() takes a result and a lock, and nothing else | P12 | P12 | `DecideTakesAnOverride` | LIVE |
| 106 | pytest | `test_nc__M14_a_third_stage_raises` — one extension, and there is no third stage | P12 | P12 | `ThirdStage` | LIVE |
| 107 | pytest | `test_nc__M34a_textsource_and_exclusion_hashes_precede_the_draw` — the pool is fixed before the draw | P12 | P12 | `ExclusionsEditedAfterTheDraw` | LIVE |

---

## P14-B1 — the surfaces (rows 108–112)

Five rows. Four are the surface gates SG1–SG4; the fifth is the registry they divide by.

**Row 112 is the one to read twice.** The exit gate reads
`surfaces_passing_all_four_gates == len(SURFACES)` and **P14 writes `SURFACES`** — so a surface
that cannot be made to pass could be deleted and the gate would go green. That is **M1**, this
plan's founding defect, inside the gate meant to prevent it. `NC-A10` does not catch it: NC-A10
catches a surface that renders through a known path, and this one is *removed from the register*.

**Rows 108 and 111 are STRUCTURAL, not computed.** `plan/07` specifies SG1's DOM arm and all of
SG4 against a headless browser (`page.inner_text`, `getComputedStyle`), and there is no headless
browser in the lockfile and no `pip`. The browser arms are recorded **NOT RUN** in
`docs/measurements/P14-surface-audit.md`, with the gap named — a `::before` injecting a glyph
through `content:` is the largest one, and it was measured empty **by hand, once, on one artifact**.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 108 | pytest | `test_render__no_banned_token_reaches_the_rendered_report` — SG1's rendered arm, which catches what no source grep can | P14 | P14 | `AffirmativeThroughData` | LIVE |
| 109 | pytest | `test_render__ffr_refuses_a_digit_in_all_three_uninformative_cases` — SG2, and the third case is the one that matters | P14 | P14 | `DeleteFailingSurface` | LIVE |
| 110 | pytest | `test_render__hero_without_an_admission_state_is_unconstructible` — SG3 as a type, not a convention | P14 | P14 | `DeleteFailingSurface` | LIVE |
| 111 | pytest | `test_style__no_colour_falls_in_the_green_hue_band` — SG4's ink rule over the generated bytes | P14 | P14 | `GreenInThePalette` | LIVE |
| 112 | pytest | `test_surface__registry_is_append_only` — the gate's denominator cannot shrink to meet its numerator | P14 | P14 | `DeleteFailingSurface` | LIVE |

---

## P14-B2 — the Unchecked panel (rows 113–115)

The panel is the product. Row 114 is the one that matters most: **`None` and `()` must not look
alike.** `None` is a statement about us; `()` is a statement about the check set, and per NC-C02 a
residue of exactly zero is a finding rather than good news.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 113 | shell | `ci/no-imported-prior.sh` — an imported prior may not become our threshold (NC-A33, not NC-CI11: that id was taken) | P14 | P14 | `PlantLuxembourgThreshold` | LIVE |
| 114 | pytest | `test_unchecked__none_and_empty_exhibits_render_differently` — unmeasured is not measured-empty | P14 | P14 | `HideUnmeasuredResidue` | LIVE |
| 115 | pytest | `test_unchecked__missing_remedy_raises` — no fallback remedy string, ever | P14 | P14 | `GenericRemedyFallback` | LIVE |

## S1 — the first statutory instrument (row 116)

*Phase column reads `P13`, not `S1`: the registry's grammar is `P0`–`P15` and this instrument is
the input P13's clause layer did not have. The narrower label would have needed a grammar change
to a registry whose whole point is that its shape does not move.*

`ci/licence-denylist.sh` (row 11) resolves the **runtime** set. S1 pinned an instrument using
PDF extractors, which are **build-time** tools and outside that set entirely — and `pymupdf`,
the arm that agreed best, is `AGPL-3.0`, which row 11 denies. It passed row 11 by not being
looked at. **A denylisted licence entering through a door the gate does not watch** is this
project's own subject matter happening to this project; the arm was dropped and this row exists.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 116 | shell | `ci/no-denied-build-tool.sh` — no extraction party carries a denied licence | P13 | P13 | `PARTIES` naming `pymupdf`, observed red 16 Aug 2026 | LIVE |

## P14-B3 — the drop screen and the API (rows 117–119)

A JSON surface is still a surface. Scoping the copy gates to the pages we happen to render would
be the same defect as scoping the licence gate to the runtime set: a rule that only watches the
door it was written for. Row 119 is the one the buyer decision made load-bearing.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 117 | pytest | `test_contract__no_banned_property_at_any_depth` — no property meaning `pass` in the GENERATED OpenAPI | P14 | P14 | `ApiBareFraction` | LIVE |
| 118 | pytest | `test_contract__fraction_never_travels_alone` — a settled fraction cannot be constructed without its six counts | P14 | P14 | `ApiBareFraction` | LIVE |
| 119 | pytest | `test_api__portfolio_has_no_total_row` — no cross-template average at any depth | P14 | P14 | `PortfolioTotalRow` | LIVE |

## P14-B4 — the library, the funnel, the history chart (rows 120–122)

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 120 | pytest | `test_library__both_kill_rates_render_or_neither_does` — the gap between claimed and all-classes is the number a reviewer wants | P14 | P14 | `KrRendersClaimedOnly` | LIVE |
| 121 | pytest | `test_funnel__stage_arithmetic_closes` — a skip cannot be laundered into a survival | P14 | P14 | `FunnelSkippedCountsAsSurvived` | LIVE |
| 122 | pytest | `test_history__can_step_down` — the settled-fraction chart is never clamped or smoothed | P14 | P14 | `HistoryMonotone` | LIVE |

## P13-B0 — the model-free claim, made mechanical (rows 123–125)

Criterion A6. The spec listed `test_no_model_in_verdict_path` as a build gate and recorded it
**not yet written**; these rows close it. `ci/barrier5.sh` is named as an entry criterion by both
P12 and P13 and **no build had created it** — the same class as an entry criterion naming a
measurement file nobody writes.

Row 123 is the guard; row 125 is a cheap companion that proves nothing on its own and exists
because a thirty-second failure gets fixed and a twenty-minute one gets skipped.

| id | kind | gate | subject_exists_at | demonstrable_red_at | broken_build | liveness |
|---:|---|---|---|---|---|---|
| 123 | pytest | `test_nc__A04a_no_model_import_reachable` — the AST import closure of every verdict root reaches nothing banned | P13 | P13 | a planted `import httpx`, observed red 16 Aug 2026 | LIVE |
| 124 | shell | `ci/barrier5.sh` — `propose.py` may not exist without a RETAIN decision record | P13 | P13 | `propose.py` planted against the PENDING record, observed red 16 Aug 2026 | LIVE |
| 125 | shell | `ci/no-model-in-verdict.sh` — the stage-2 grep arm | P13 | P13 | a planted `import httpx`, observed red 16 Aug 2026 | LIVE |
