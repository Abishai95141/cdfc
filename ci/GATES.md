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
| 14 | ast | `test_no_model_in_verdict_path` — no model client reachable from L5/L6/L7 | P5 | P5 | import a model client in `verdict/` | PENDING |
| 15 | schema | attestation schema has no `result`/`status`/`pass` at any depth | P11 | P11 | add the field to the schema | PENDING |
| 16 | pytest | `test_closure` — the seven-term closure invariant holds | P5 | P5 | drop a bucket from the sum | PENDING |
| 17 | shell | `ci/no-timing-in-hashed-payload.sh` — no duration field inside a hashed object | P0 | P0 | `injectors/elapsed_us_in_canary_row.py` | LIVE |
| 18 | pytest | `test_plan__critical_path_total_equals_sum_of_rows` — a total equals its parts | P0 | P0 | change a per-phase figure without the total | LIVE |
| 19 | shell | `ci/no-external-paths.sh` — no machine-local absolute path in the build | P0 | P1 | `injectors/external_fixture_path.py` | LIVE |
| 20 | shell | `ci/no-float-money.sh` — no float in the deterministic numeric core | P3 | P3 | `injectors/float_in_calc.py` | LIVE |

**Rows 17 and 18 exist as gates from the first commit, dated 11 Aug 2026, and their reason is recorded
rather than assumed.** Row 17: a `CanaryRow.elapsed_us` inside a canonicalised payload was found in the
plan and would have made byte-identical re-derivation impossible; the gate exists before the payload does.
Row 18: a displayed critical-path total that did not equal the sum of its own rows was found in the plan,
which is the shared-denominator error in a schedule; the gate exists before any other total does.

**LIVE = {1,…,13,17,18,19,20} (17 rows). PENDING = {14,15,16} (3 rows). Total 20.**

**Row 20 was added at P3, dated 11 Aug 2026.** R4 requires the evaluator to be `Decimal` from its first line rather than converted later; the gate exists so that cannot drift in unnoticed.

**Row 19 was added at P1, dated 11 Aug 2026, with its reason recorded rather than assumed.** A negative
control was found still pointing at the external directory the corpus was vendored FROM, so it was
validated against bytes that could drift — and the repository was not portable. Adding a row is an
append-only change and the pre-registered LIVE set moves with it, in one commit, with this paragraph as
the dated argument `test_contract__live_set_is_pre_registered` requires.
