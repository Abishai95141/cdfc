# docs/OPEN-ITEMS.md — standing unanswered questions, rendered with their age

`cdfc.surface.openitems` reads this file and `docs/FIELD-OBSERVATIONS.md`. An item with a sent date
and no reply renders as *"asked <date>, no reply after <n> days"* — **never as absence**. A question
nobody answered gets louder as it ages.

- [OPEN] The clean corpus is not funded, so no predicate is admitted under G4 and every severity is capped at ADVISORY. n >= 189 would be needed for BLOCKING.
- [OPEN] A statutory instrument IS pinned since 16 Aug 2026 — the IFSCA (Fund Management) Regulations 2025, 1,218 units, two external extraction arms. No harvested predicate implements a clause from it, so predicates_with_a_STATUTE_obligation still reads 0 of N. The blocker moved from the corpus to the authoring.
- [OPEN] Cohen's kappa for the stratum assignment is unmeasured; it needs a second named adjudicator and has no mechanical substitute.
- [OPEN] 319 of 348 harvested predicates produce no record in the reference run. `1. Introduction!D3` is in the field-surface mask and `P-0002` binds it, yet the cell falls into the 1,849 no-predicate bucket — so that bucket is counted under a reason code that says no predicate exists when one does. It under-reports coverage, which is the honest direction, but the reason is wrong.
- [OPEN] Every candidate is refused at G2 — 315 for no kill, 33 for no margin over the free baselines — so the predicate library is empty and every settled count in this product rests on predicates that were never gate-admitted. The two populations are disjoint and the surface says so.
- [OPEN] The churn sweep's precise signal moved nobody in the reference run: `P-0002` carries the year vocabulary and does not appear in that run, so the measured step-down comes from the conservative sheet-level signal instead.
- [OPEN] There is no staleness policy for a running deployment. Nothing expires: a pinned instrument, a qualification artifact and a published run are all served the same way at one day old and at one year old, and no surface states an age past which a coverage declaration should stop being relied on. The README names this as absent and this is the list it names.
- [OPEN] There is no deployment packaging. `make serve` binds loopback on a developer machine and that is the only way this runs; there is no image, no service unit, no configuration surface for a bind address or a data root, and no documented upgrade path for a deployment that already holds runs. Nothing has been operated by anyone who did not build it.
- [OPEN] The instrument-stream watcher (P13-B4) is not built. A pinned instrument that is amended upstream stays pinned silently — nothing watches the source, nothing raises the amendment, and the staleness that results would be invisible for exactly as long as nobody looked.
- [OPEN] `POST /v1/filings` refuses every filing — 422 when the workbook binds no pinned blank, 501 when it does, because there is no queue, no worker and no run store behind that endpoint. So the browser cannot check anything and only `cdfc run` on the command line produces a run. The refusals are honest, but the intake a viewer of the walkthrough would reach for does not work.
- [OPEN] The runner checks one form. `run_filing()` takes no template parameter and resolves the pinned FME blank through parameterless `lru_cache`d globals, so the ALR return (own field surface 1,599 cells) is scored over FME's 3,747 and reported VALID. `DENOMINATOR_DISAGREEMENT` exists in the invalid-cause vocabulary and is raised by no code.

## The negative-control sweep report is an INPUT, and nothing forces it to be current

`tests/negative/test_nc_sweep.py` reads `reports/negative-control-sweep.json` rather than running
the sweep. Immediately after the Anchor migration those tests failed against a report produced
BEFORE it — a red that was true of the old measurement and meaningless for the tree under test.

The red is the harmless direction. **The dangerous one is green:** a change that breaks a control
leaves the committed report untouched, so the tests keep passing on a measurement that no longer
describes the code. That is the same defect shape as an injector whose text anchor has drifted,
one level up — and this build has now hit the injector version twice.

What would close it: pin the report to the tree it measured (a digest of `src/` and `injectors/`
recorded inside it, checked on load) so a stale report is a REFUSAL rather than a pass.
