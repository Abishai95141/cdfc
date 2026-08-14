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
| 12 | shell | `ci/catalogue-ids.sh` — `NC-` ids unique, defined, non-dangling, UTF-8 | P0 | P0 | duplicate an id in the registry | LIVE |
| 13 | pytest | `test_nc__CI01_missing_scan_root_fails` — a grep over a missing root is red | P0 | P0 | `injectors/remove_scan_root.py` | LIVE |
| 14 | ast | `test_no_model_in_verdict_path` — no model client reachable from L5/L6/L7 | P5 | P5 | import a model client in `verdict/` | LIVE |
| 15 | schema | attestation schema has no `result`/`status`/`pass` at any depth | P11 | P11 | add the field to the schema | PENDING |
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

**Rows 17 and 18 exist as gates from the first commit, dated 11 Aug 2026, and their reason is recorded
rather than assumed.** Row 17: a `CanaryRow.elapsed_us` inside a canonicalised payload was found in the
plan and would have made byte-identical re-derivation impossible; the gate exists before the payload does.
Row 18: a displayed critical-path total that did not equal the sum of its own rows was found in the plan,
which is the shared-denominator error in a schedule; the gate exists before any other total does.

**LIVE = {1,…,14,16,…,63} (62 rows). PENDING = {15} (1 row). Total 63.**

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
