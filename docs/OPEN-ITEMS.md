# docs/OPEN-ITEMS.md — standing unanswered questions, rendered with their age

`cdfc.surface.openitems` reads this file and `docs/FIELD-OBSERVATIONS.md`. An item with a sent date
and no reply renders as *"asked <date>, no reply after <n> days"* — **never as absence**. A question
nobody answered gets louder as it ages.

- [OPEN] The clean corpus is not funded, so no predicate is admitted under G4 and every severity is capped at ADVISORY. n >= 189 would be needed for BLOCKING.
- [OPEN] A statutory instrument IS pinned since 16 Aug 2026 — the IFSCA (Fund Management) Regulations 2025, 1,218 units, two external extraction arms. No harvested predicate implements a clause from it, so predicates_with_a_STATUTE_obligation still reads 0 of N. The blocker moved from the corpus to the authoring.
- [OPEN] Cohen's kappa for the stratum assignment is unmeasured; it needs a second named adjudicator and has no mechanical substitute.
- [OPEN] 319 of 348 harvested predicates produce no record in the reference run, so cells like `1. Introduction!D3` — which `P-0002` binds — still sit in the NO_PREDICATE state and under-report coverage. That is the honest direction, and it is what remains open. **The reason code is no longer wrong:** the 1,849 bucket splits 422 `no_predicate.failed_qualification` / 1,427 `no_predicate.not_yet_synthesised`, `1. Introduction!D3` carries `failed_qualification`, and `tests/golden/test_golden__unchecked__fme.py` pins the split. Repaired at `29b40b5`; this entry claimed otherwise until an audit re-ran it.
- [OPEN] Every candidate is refused at G2 — 315 for no kill, 33 for no margin over the free baselines — so the predicate library is empty and every settled count in this product rests on predicates that were never gate-admitted. The two populations are disjoint and the surface says so.
- [OPEN] The churn sweep's precise signal moved nobody in the reference run: `P-0002` carries the year vocabulary and does not appear in that run, so the measured step-down comes from the conservative sheet-level signal instead.
- [OPEN] There is no staleness policy for a running deployment. Nothing expires: a pinned instrument, a qualification artifact and a published run are all served the same way at one day old and at one year old, and no surface states an age past which a coverage declaration should stop being relied on. The README names this as absent and this is the list it names.
- [OPEN] There is no deployment packaging. `make serve` binds loopback on a developer machine and that is the only way this runs; there is no image, no service unit, no configuration surface for a bind address or a data root, and no documented upgrade path for a deployment that already holds runs. Nothing has been operated by anyone who did not build it.
- [OPEN] The instrument-stream watcher (P13-B4) is not built. A pinned instrument that is amended upstream stays pinned silently — nothing watches the source, nothing raises the amendment, and the staleness that results would be invisible for exactly as long as nobody looked.
- [OPEN] 21 of 125 live gates have no negative control that makes them red. The liveness figure used to read 115 of 125 because `EVIDENCE` in `tools/gate_liveness.py` was a HAND-MAINTAINED gate-to-control map that ASSERTED bindings; pytest bindings are now DERIVED from the sweep's own per-guard record and the honest figure is 104 of 125. Two of the assertions were provably wrong rather than merely stale — gate 4 was bound to `NC-CI02`, whose catalogue entry declares that very test `flips: false`, i.e. it must stay GREEN under that injector. The three shell gates among the ten were each tested against their nearest candidate injector and none made its script exit non-zero. So these gates run and can fail; nothing has ever been observed making them fail. Closing it means writing 21 negative controls, not editing a map.

## Closed, with the probe that observed the closure

An item leaves the list above only when a probe in `tools/progress.py` OBSERVES the new behaviour —
never because somebody believed it was done. `make progress` re-runs all of them; a regression puts
the checkpoint back to TODO whether or not anybody expected it to. `cdfc.surface.openitems` matches
only `- [ASKED` and `- [OPEN`, so nothing below renders into the report.

- [CLOSED 2026-08-19] `POST /v1/filings` no longer refuses a filing it can bind. It runs the
  check and returns **201** with the coverage declaration, the counts travelling with the fraction.
  Observed by probe `A1-6`. Two limits stay, and they are stated on the endpoint itself: the run is
  **not persisted** (`"persisted": false` — the run id is a digest of the inputs, so the declaration
  is reproducible with `cdfc run` and needs no server-side record), and `POST /v1/verify` is still
  501 because re-derivation is a command-line tool.
- [CLOSED 2026-08-19] The runner takes the form it is checking.
  `run_filing(filing, *, template=None, ...)` threads a template through what used to be four
  parameterless `lru_cache`d FME globals. Observed by probe `A1-3`; probe `A1-4` runs both arms —
  the ALR return against its own blank is VALID over its own **1,599** cells, and against the wrong
  blank it is INVALID with `invalid.denominator_disagreement`, which probe `A1-5` confirms is
  reachable from outside the module that declares it.

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

## Binding is all-or-nothing, and that — not the closed vocabulary — is where flexibility dies

Asked directly whether a deterministic, closed-vocabulary engine would reject valid-but-unseen
constructs, the answer measured out the opposite way from the intuition.

**The vocabulary is not the constraint.** E1 put 12,925 published EBA expressions through a CEL
subset designed for spreadsheets and never for DPM-XL: **11,886 compile today**, **12,850** with four
bounded host functions, **75** refused by deliberate bans (62 clock, 13 regex), and **zero** unknown
constructs. A closed vocabulary met a foreign rule language and covered nearly all of it.

**Binding is the constraint, and it is a cliff rather than a slope.** MEASURED over
`fixtures/synthetic/`:

    REFUSED   row-inserted__portfolio-r7.xlsx
    REFUSED   formula-overwritten__investors-N5.xlsx

A filer who INSERTS A ROW — an ordinary act — has the whole filing refused as
`invalid.template_unbound`. Not partially checked, not scored over the cells that still match:
nothing. And the second file is a defect this product exists to CATCH, which instead returns as an
apparatus failure about us.

The distinction that matters: an unseen CONSTRUCT costs coverage and says so
(`no_predicate.not_yet_synthesised`); an unseen STRUCTURE rejects the filing entirely. Only the
second is rigidity, and it is fixable without weakening determinism.

WHAT WOULD CLOSE IT — AND A FIRST ATTEMPT THAT WAS BUILT, MEASURED UNSAFE, AND REVERTED.

The obvious design is: treat `sheets` as the identity facet, admit a `PartiallyBound` when the sheet
set matches exactly, and score coverage over the template's field surface with the differing facets
named. It was implemented and it worked in the sense that both previously-refused fixtures came
back checked — `formula-overwritten__investors-N5` went from a refusal to VALID with 1,557 settled.

**It is wrong, and the measurement that shows it is short.** A ROW INSERTION RENUMBERS EVERY CELL
BELOW IT:

    pinned blank unlocked cells   3,747
    row-inserted filing           3,747
      addresses common to both    3,544
      in blank only                 203
      in filing only                203

`3. Portfolio!A104` is present in BOTH — and in the filing it holds what `A103` held in the blank.
Scoring those against each other compares two different fields that happen to share a name. The
`952 settled` such a run reported is not partial coverage; it is data matched to the wrong labels,
which is the exact wrong-form failure strict binding exists to prevent. Reverted rather than shipped.

WHAT THE CORRECT DESIGN NEEDS, and it is more than a looser facet rule:

1. **A correspondence, not an intersection of names.** Partial binding must establish which field in
   the filing IS which field in the blank — an alignment that survives insertion, deletion and
   reordering — not merely which addresses appear in both.
2. **Coverage scored over the CORRESPONDENCE**, with unaligned fields on both sides declared: cells
   the blank has that the filing lost, and cells the filing has that the blank never declared.
3. **A refusal when the correspondence is ambiguous.** Two candidate alignments of similar quality
   is the same hazard as two pinned blanks sharing a sheet set, and must stay `Unbound`.

Until (1) exists, an exact match is the only safe bind, and `row-inserted__portfolio-r7.xlsx`
staying `Unbound` is CORRECT rather than rigid.

## The sweep report is BOTH an input to the tests and an output of the target they gate

Recorded above as a staleness risk; observed here as something worse. A contaminated run writes a bad
report, `test_nc_sweep.py` reads it and fails, and `make` halts BEFORE `nc_sweep.py` can refresh it.
The build cannot then recover without running the sweep by hand — a deadlock, not merely a stale
number. Pin the report to a digest of `src/` and `injectors/` so a report that does not describe the
tree is a NAMED REFUSAL rather than a pass or an unrecoverable red.
- [OPEN] The division recovery is NOT corpus-independent, and this is measured rather than feared. `docs/measurements/N6-corpus-independence.md` ran it against eleven corpora across five jurisdictions and four document types: the correct top-level division axis is ranked **first on 3 of 11**, is in the top five on 5 of 11, and is induced at all for 9 of 11. The shipped `src/cdfc/qualify/provisions.py` — whose six marker shapes were fitted to the IFSCA Gazette — ranks first on **1 of 11**. Two corpora (`us_bill_hr3684`, `india_const`) induce no candidate matching their true axis at any rank and the reason is unmeasured. **A page-number sequence is a perfect division numbering** — chain 176 of 176, purity, coverage and density all 1.00 in `rfc2616` — and no property intrinsic to numbering separates it from logical structure; nesting was tried and fails, because physical pages genuinely contain sections. Closing this needs the axis to become a DECLARED property of each pinned instrument with the recovery proposing ranked candidates, which is an `A4` change, not a repair.
- [OPEN] `A5`'s `TYPE_ADMITS` refuses a field the template leaves `UNDECLARED`, and on the FME return that is **355 of 443 labelled fields** — the workbook declares a type for 88 and carries no money field at all. The alternative design, filling it and marking the type unchecked, is defensible and was NOT taken: a value in a field whose type nobody declared cannot be validated by anything downstream, and the conservative branch is the one that matches a mechanical trigger. This is recorded as a decision rather than left as an accident, and it is the strongest argument for the XSD ingress, where 3,837 of 3,837 fields carry a declared type. See `docs/measurements/A5-fill-lane.md` and `docs/measurements/D2-xsd-ingress.md`.
- [OPEN] No fill ACCURACY is measured and none can be until the 30 filing-plus-source-pack pairs exist. `A5` is built, its six conditions each have a positive control, and it refused **13 of 13** fields a deliberately crude binder bound — but nothing here says how often a proposed value is RIGHT. The binder itself is not part of `A5` and its quality is separately unmeasured.
