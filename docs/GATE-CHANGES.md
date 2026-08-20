# docs/GATE-CHANGES.md

## 20 Aug 2026 — row 127 added: a live document may not carry a falsified claim

Four claims Phase 1 falsified were still being asserted days later, and **two were RENDERED INTO
THE PRODUCT**: `cdfc.surface.openitems` reads `docs/OPEN-ITEMS.md` and shows every `- [OPEN]` line
to a user, so the report was telling readers the upload endpoint refuses every filing while probe
`A1-6` observed it returning 201. They were fixed by hand, and nothing prevented their return — a
second README passage saying the same thing was found later the same session, and three documents
were still quoting a superseded attestation ratio.

Every pattern in the gate was TRUE of this repository once. The rule is not that the words are
banned: a line carrying one must also carry a closure marker, and a document that declares itself
a dated record in its own header is exempt whole, so a pre-registration whose criteria may never be
edited is not asked to annotate them.

**Its first run flagged six lines, and all six were its own author's correction notices** — the
marker set was too narrow. That is recorded rather than quietly widened: the cost of a missed
marker is a false red on a correction someone already wrote, so the markers are broad on purpose.
Observed red under an unmarked planted claim, and observed GREEN under the same claim marked as
history — a gate that only ever goes red cannot tell a claim from a record of one.

## 20 Aug 2026 — row 126 added: only the LAST `!` delimits a cell string

Found by the adversarial audit of the A1 diff. A cell string is `<sheet>!<ref>`. A reference can
never contain `!`; **a sheet name can** — Excel permits it and openpyxl accepts it, both verified.

`Anchor.parse` right-splits and was correct. **Eighteen call sites across `src/` and `tools/`
left-split and were not**, so `Bad!Name!A1` gave sheet `Bad` and a reference addressing nothing.
The anchor and the rest of the codebase disagreed about which character was the delimiter, on
exactly the path A1 exists to serve: a buyer's own workbook, checkable without a code change.

Demonstrated end to end rather than argued: a workbook with the sheet `Bad!Name` was built, run
through the shipped `surface_for`, and produced refs whose two parsers disagree. 22 sites now
right-split. `ci/no-left-split-on-cell.sh` keeps them that way and was observed red under a
planted `partition("!")`.

## 19 Aug 2026 — row 118's evidence binding is wrong, and the gate is fine

`ci/GATES.md` row 118 (`test_contract__fraction_never_travels_alone`) names `ApiBareFraction` as
its `broken_build`. Under the registry's own column definition — *"the named injector or condition
that makes it red"* — that is false: the injector leaves 118 green while turning row 117 red. Both
rows were bound to the same break because they live in the same file.

**The gate itself works.** Neutralising `SettledFractionOut.__post_init__` turns it red. So this is
a wrong binding, not a dead control, and it is one of the reasons `tools/gate_liveness.py` stopped
consulting a hand-maintained map for pytest rows and now derives the binding from the sweep's own
per-guard record. Row 118 has no control that declares it a flipping guard, and it is counted among
the 21 named in `docs/OPEN-ITEMS.md`. The registry is append-only, so the row is not edited.

**Not yet written.** Its subject does not exist at P0; it is created by the phase that first needs it.
This file exists so a reference to it is never dangling, and its emptiness is visible rather than silent.

---

## 12 Aug 2026 — P4 adds rows 21–27, all LIVE, all observed red in the same session

| row | gate | why it is LIVE rather than PENDING |
|---|---|---|
| 21 | `ci/no-regex-over-cel.sh` | its subject exists from P4-B2 and `injectors` makes it red by adding a second `re.` use to `ast_walker.py` |
| 22 | the envelope digest covers every field of the record | `ProjectionDropsAField` |
| 23 | the two key mismatches stay distinguishable | `KeysMismatchCollapsed` |
| 24 | the weak pile is counted, not dropped | `WeakPileDropped` |
| 25 | the G2 denominator is declared per class | `ClaimsFromKillVector` |
| 26 | a host function never resolves live | `HostFnResolvesLive` |
| 27 | the predicate schema is generated from the record | editing the schema without touching the record |

**The pre-registered LIVE set is not edited.** `LIVE_AT_P0` stays exactly as it was and
`ADDED_LIVE_AT_P4` is a separate frozen literal, so a row that was LIVE at P0 cannot leave the set
by being edited out of a growing list. `test_contract__live_set_is_pre_registered` asserts the
containment as well as the equality.

## 12 Aug 2026 — NC-Q02 leaves PROVISIONAL

Its admission-side twin — a QUALIFIED predicate that DOES load — could not be written before the
predicate schema existed, so from P0 to P3 the entry was reported in its own column and excluded
from `entries_caught`: a green entry with no information in it is not evidence. P4-B1 gives the
schema. `fixtures/predicates/good/P-0007` carries a qualification record and loads;
`fixtures/predicates/broken/P-NC02` does not; and `LoaderSkipsQualificationCheck` makes the refusal
green. The entry is now `caught` under the exact-set contract and gate 27 counts it as evidence.

## 12 Aug 2026 — a defect found in row 3's injector, recorded because no gate caught it

`RemoveScanRoot` deleted `src/cdfc/evaluate/__init__.py` and then `rmdir`-ed the directory with the
failure suppressed. That worked while `evaluate/` held one file. P4-B3 added `celrt.py`, the
`rmdir` began failing silently, the directory went on existing, and **the flagship P0 negative
control proved nothing while still reporting itself as caught.** The sweep could not see it — the
injector applied cleanly and the tree restored exactly, and the digest check is blind to a no-op by
construction. It was found because the guard test went red for the right reason. The injector now
removes every file under the root.

---

## 12 Aug 2026 — P5 adds rows 28–36, all LIVE, all observed red in the same session

Row 28 (`ci/no-regex-over-xml.sh`) is the notable one: it was **named as a sibling by a gate
written at P4 and did not exist**. It found a live defect in the P5 filing generator and a
pre-existing one in `tools/fixtures/make_synthetic.py` on its first run. A gate named in a comment
is not a gate.

Row 33 carries the product's headline claim: **nothing derived from the filing's own values may
remove a cell from the in-scope denominator.** `LIVE_AT_P0` and `ADDED_LIVE_AT_P4` are unchanged
and `ADDED_LIVE_AT_P5` is a third frozen literal, so no row that was ever LIVE can leave the set by
being edited out of a growing list.

---

## 13 Aug 2026 — P6 adds rows 37–47, all LIVE

Row 37 (`ci/no-bare-rate.sh`) found **fourteen** bare rates on its first run, including one in a
published measurement file. `docs/measurements/P3-evaluator.md` now renders `n/d` in place of a
percentage column, and two prose sites carry a declared `rate-ok:` marker with a reason — a
regulatory threshold quoted from a rule, and a historical figure named as the defect it was.
Both are quotations, not measurements.

`ADDED_LIVE_AT_P6` is a fourth frozen literal, so no row that was ever LIVE can leave the set by
being edited out of a growing list.

---

## 13 Aug 2026 — P7-B0 narrows row 38 (`ci/no-openpyxl-writer.sh`), and finds a silent Makefile pass

**Row 38's scope is narrowed, not weakened.** The gate banned every openpyxl construct under
`src/cdfc/qualify/`, `load_workbook` included. P7-B0 needs a READ-ONLY openpyxl handle in exactly
one file: `template_instrument.py`, where openpyxl is the EXTERNAL party of the dual-extraction
harness and the whole value of the party is that nobody here wrote it.

So `load_workbook` is admitted **in that one file, by name**, and the three write routes —
`.save(`, `Workbook()`, `ZipFile(..., "w")` — stay banned there and everywhere. The exempt file is
checked SEPARATELY rather than exempted wholesale, because a blanket exemption would have re-opened
the round-trip this gate exists to prevent, in the file the exemption was granted to. Both halves
were observed red in this session against planted controls: a `wb.save(...)` inside the exempt
file, and a `load_workbook` in `sites.py`.

**And a defect the gates could not see, found while running them.** `Makefile` defined the target
`contract:` **twice** — P0's `pytest tests/contract` at line 32 and P5's `python tools/gen_contract.py`
at line 117. `make` keeps the last definition and prints a warning nobody reads, so **since P5
`make contract` regenerated `EVALUATION-CONTRACT.md` and `make all` never ran the contract suite at
all**, while printing a target name that said it had. `make verify` was unaffected — it runs
`pytest tests` — which is exactly why nothing went red. The generator is now `gen-contract`, both
targets are in `.PHONY`, and `make contract` runs 68 contract tests again.

*A duplicate target is a silent pass with a warning attached, and this is the sixth instance in
this repository of a name agreeing with itself while the contents did something else.*

---

## 13 Aug 2026 — P7 adds rows 48–56, all LIVE, all observed red in the same session

Row 48 (`ci/no-wallclock-z3.sh`) is the determinism one: `set("timeout", ms)` makes a proof verdict
a function of what else the machine was doing, so the same candidate is `unknown` on a loaded
runner and `trivially_true` on an idle one — and a predicate's ADMISSION becomes a property of the
CI queue. On its first run the gate matched the sentence in `g3_degeneracy.py` that EXPLAINS why a
timeout is banned. **A gate that fires on its own rationale gets "fixed" by deleting the
rationale**, which is the worst available outcome for a rule whose whole value is that the next
reader knows why it exists, so it now strips comments and scans code.

Row 51 is arbitration C2 and it fires in BOTH directions: `0/572` alone is wrong by 572 under F9's
ruling, and `572/572` alone conceals that nothing here is grounded in a statute.

Row 55's reason is the one worth reading. `unknown` from the proof arm means *nobody could decide
this*. Reading it as `non_degenerate` admits 47 of 349 FME candidates on a proof nobody has;
reading it as a REJECTION refuses those same 47 for a limitation of our own translator. Three
outcomes, and collapsing any pair of them is a defect.

`ADDED_LIVE_AT_P7` is a fifth frozen literal.

**A defect this phase found in an EXISTING gate, recorded because it is the third occurrence of
one shape.** `ci/no-regex-over-xml.sh` caught P7-B3's own baselines matching `<v>([^<]*)</v>` over
a mutant's recorded cell edit — the same pattern-over-OOXML technique that returned a correct count
with wrong contents at P1, dropped 424 of 505 formulas at P5, and has now been attempted a third
time by the author of the gate that bans it. Both baselines now parse the fragment.

---

## 13 Aug 2026 — P8 adds rows 57–62, and widens row 38 by one named file

Rows 57 and 58 are **F2 and F5**, the two the plan calls the adversary's. Before this phase
`clean_corpus_independent_of_predicate` was a field in a YAML file that **no build computed, no
test asserted, no negative control broke and no gate read**, and the corpus generator let
`src/cdfc/calc/` compute the very cells the arithmetic predicates re-check. An arithmetic
predicate's expected false-failure rate was therefore zero *regardless of its quality*, and
`n = 189` — one command, one afternoon — bought a `BLOCKING` tier from a corpus the product
generated about itself.

Row 62 is F2's second half, and it is the one that survives even a foreign oracle: the interval is
a statement about a SAMPLE, and a sample the product generates is unbounded in `n`. `BLOCKING`
needs thirty filings a person or the world produced, whatever the interval says.

**Row 38 (`ci/no-openpyxl-writer.sh`) is widened by exactly one file.** `corpus/_writer.py` joins
`surgery.py` as a declared raw-zip writer: it writes the clean corpus by the same technique and for
the same measured reason — an openpyxl round-trip drops 24 parts and all 19 `x14` validations — and
it imports no openpyxl at all, which the gate's `hits` scan still enforces over every file
including that one. Observed red in this session against a planted `openpyxl.load_workbook` inside
the newly exempt file.

**A defect this phase found in the ROLE of an existing gate, worth recording.** `ci/no-bare-rate.sh`
fired on the string `Wilson 95%` in a column header. It was right: a confidence LEVEL rendered as a
percentage on a surface is indistinguishable from a measured rate to a reader. The level now
renders once, in prose, above the table.

`ADDED_LIVE_AT_P8` is a sixth frozen literal.

## 14 Aug 2026 — P9 adds rows 64–75, and two of them guard a subject that shipped at P3

`ADDED_LIVE_AT_P9 = set(range(64, 76))` — a sixth frozen literal.

**Rows 64 and 65 are the unusual pair.** Their subjects — `recalculate`'s explicit
`formula_source` and G-EVAL's arm-2 independence — shipped at P3. They are recorded
`subject_exists_at P3` and `demonstrable_red_at P9` because **that is when a guard was written for
them**, not when the code arrived. A row whose two phases differ is the honest shape for a gate
that was owed earlier; collapsing them to `P9 | P9` would hide that the subject went unguarded for
six phases, and collapsing them to `P3 | P3` would claim a demonstration nobody performed.

Writing row 65 is what found the stale measurement: `tools/measure/evaluator_arm1.py` had been
raising `KeyError: 'cells'` since a rename, no make target ran it, and
`docs/measurements/P3-evaluator.md` was therefore an artifact of a version that no longer executed
— publishing FME as 495 agree / 10 not-run when the truth after P6's `AGGREGATE` repair was
475 / 30. **A measurement with no way to re-run it is a memory.** Both measurement tools now have
make targets.

Rows 66–75 are the NC-R family: the relation layer's ten controls, one injector each.

**Row 75 guards an OPEN defect rather than a closed one**, and that is deliberate. `HALF_ULP = 5`
is half a unit of `MILLI_USD_MILLION`, but the fact tree the runner evaluates carries the
workbook's own numbers unscaled — so every harvested tolerance literal is 1,000× the tolerance it
was written to express, and `P-0114` admits a 60 USD Million discrepancy on a row whose true total
is 12. Repairing it moves every envelope digest, the registry root, P7's funnel and P8's FFR, so it
is a phase of its own. What row 75 prevents is a **partial** repair landing quietly: scaling the
tree without moving the literals, or the reverse, is the same defect with the sign flipped and
would be much harder to see than the one we have now.

## 14 Aug 2026 — row 12 restated, and rows 3 / 28 / 48 rebound to injectors that break them

**Row 12 claimed four subjects and enforced one.** `ci/catalogue-ids.sh` ran
`plan/scripts/nc_audit.py` and DISCARDED its exit status behind `|| { echo "advisory at P0"; }`,
so only the UTF-8/NUL half could fail the gate — and the swallowed half had been red the whole
time: 17 orphan ids, 56 dangling ids, `VERDICT: NOT CLEAN`. A gate that prints its own subject's
failure and exits 0 is worse than one that never looked.

The two halves are now separated rather than conflated. **Enforced:** the CATALOGUE's own ids —
unique, every injector defined in `injectors/`, every guard path a real file, and `injector: NONE`
admissible only with a `why_impossible`. That is the registry this build actually runs against and
it is checkable. **Advisory, with its numbers printed on every run:** the plan documents'
cross-references. `plan/*.md` is the design record and names controls that were specified and never
built; making that fatal would demand the plan be edited to match what shipped, which is backwards —
the plan is the input. The count is on screen so it cannot be forgotten, and it is labelled
advisory rather than presented as a pass.

**Rows 3, 28 and 48 were published OBSERVED RED on injectors that break something else.** Row 3
(`scan-roots-exist`) was bound to `DefeatBareExceptGate`, which replaces a different script; rows
28 (`no-regex-over-xml`) and 48 (`no-wallclock-z3`) to injectors that edit a markdown table and a
Z3 verdict reading respectively. Under all three the gate exits 0. The gates were functional the
whole time — this was a wrong evidence binding, not a dead gate, and `tools/gate_liveness.py`'s
own docstring argues that a hand-maintained list drifts, which is what its `EVIDENCE` map did.

Two repairs. `gate_liveness` now RUNS a shell gate under its bound injector and requires a
non-zero exit, reporting `BINDING NOT VERIFIED` instead of counting a red observation nobody can
reproduce; it distinguishes the two injector shapes, because the `_DefeatGate` family replaces the
gate script itself and exits 0 BY DESIGN. And NC-CI18 / NC-CI19 / NC-CI20 plant each gate's own
subject — a missing scan root, a pattern over a cell element, a wall clock on the solver.

## 14 Aug 2026 — rows 76 and 77: two gates that had run since P0 with no row at all

`ci/no-clock-in-core.sh` and `ci/no-bare-absence.sh` are both invoked by `make greps` and neither
had a row in this registry. They were therefore outside `tools/gate_liveness.py`'s denominator
entirely — not counted as LIVE, not counted as PENDING, and never observed red. A gate CI executes
and the registry does not know about is the inverse of the failure row 8 guards: not a gate that
resists demonstration, but one nobody thought to demand it from.

Registering `no-clock-in-core` found a second defect in it. Its pattern listed
`perf_counter|monotonic|process_time` — the clocks a person reaches for when TIMING something —
and missed `time.time()`, `datetime.now()`, `datetime.utcnow()` and `date.today()`, which are what
a person reaches for when STAMPING something. A timestamp inside a hashed payload is precisely
what makes byte-identical re-derivation impossible, so the gate was blind to its own headline case:
a `time.time()` planted in `src/cdfc/verdict/closure.py`, the deterministic core, left it green.
Nothing in `src/cdfc` uses a wall clock today, so the widening cost nothing.

NC-CI21 and NC-CI22 plant each gate's own subject.

---

## 15 August 2026 — P11. Rows 91–98 added LIVE, and **row 15 promoted PENDING → LIVE**

**Row 15 is the first row in this registry ever to change its liveness**, and the registry is built
so that doing so fails the build until somebody writes down why. This is why.

It was written at P0: *the attestation schema has no `result`/`status`/`pass` property at any
depth*. It sat `PENDING` for eleven phases for the only admissible reason — **its subject did not
exist**. There was no attestation schema to walk, so the gate could not be observed red, and a gate
that cannot be observed red is not evidence whatever colour it reports.

P11-B1 wrote `src/cdfc/attest/schema/attestation.schema.json`. The gate now walks it: 95 property
names at every depth, through every combinator, with **zero blocking hits**. It is demonstrated red
by `injectors/banned_names_substring_only.py`, and the shape it has to catch is NC-A01's own — a
`status` planted inside a `$defs` entry referenced from an `allOf` two levels down, which a walker
reading only top-level `properties` would miss while reporting success.

**The PENDING set is now empty.** Every gate in this registry is LIVE, and every LIVE gate has been
observed red.

### Rows 91–98

L7's gates: the name prohibition in both its halves, the float refusal over the canonicalised
bytes, `expires` as a function of `timeVerified`, `verify` never re-signing, `E2E-VERIFY`'s byte
identity, the OSCAL refusal on an `INVALID` run, and the completeness of
`docs/NON-DETERMINISM.md`'s enumeration.

Row 94's injector, `expires_from_now`, turns **row 96** red as well — the byte-identity acceptance
test catching a single clock read three layers away, without being told where to look. That
coupling is the phase's strongest single piece of evidence and it was measured, not arranged.

## 15 Aug 2026 — P12 adds rows 99–107, all LIVE on the day they land

Nine rows for the settling experiment. **None was PENDING for a moment**, because each subject was
written before its gate: the injectors exist, and every one was observed to turn its guard red with
its positive control holding, before the rows were appended.

| row | what it guards | injector |
|---:|---|---|
| 99 | the pre-registration's `h0` cannot move | `PreregEditThreshold` |
| 100 | the Stratum-B cap never truncates the denominator | `TruncateBDenominator` |
| 101 | inverse sampling is corrected and labelled, not assumed away | `NaiveRatioEstimator` |
| 102 | retry is impossible, not merely banned | `ProposeRetry` |
| 103 | the discard pile is stage 0 of the funnel | `FunnelDropsDiscards` |
| 104 | no model client on the qualification or verdict path | `ModelClientInQualify` |
| 105 | `decide()` takes a result and a lock, and nothing else | `DecideTakesAnOverride` |
| 106 | one extension; there is no third stage | `ThirdStage` |
| 107 | the pool is fixed before the draw | `ExclusionsEditedAfterTheDraw` |

**Two of the nine had to be rebuilt after their first observation, and both corrections are the
kind this register exists to record.**

**Row 104's guard was checking nothing.** The import closure was seeded with the package name, and
`cdfc/qualify/__init__.py` imports almost nothing — so the walk never reached `g2_kill`, the
injected model client sat there undetected, and the control reported itself caught. The fix seeds
the walk with **every module file under each root**, which is also the stronger rule: *no module in
this package may import a model client*, undefeatable by a module simply not being re-exported.
This is the project's own recurring defect — a gate that reports OK having looked at nothing —
occurring inside the gate written to catch it.

**Row 100's injector broke the harness rather than the measurement.** Truncating `stratum_b_all`
at construction is refused by `Draw.__post_init__`, so `draw()` raised and *every* guard went red
including the positive control. That the invariant catches the constructional form is a real
property; the injector now attacks the **reporting** path instead, which is the version that would
survive review.

## Row 116 added LIVE — 16 August 2026, at S1

**`ci/no-denied-build-tool.sh` — no extraction party carries a denied licence.**

S1 pinned the first `kind: STATUTE` instrument, which required PDF extractors. Those are
**build-time** tools: nothing in `src/` imports them, and the pinned `*.text.json` is what the
system reads. `ci/licence-denylist.sh` (row 11) resolves the **runtime** set, so it never looked at
them.

`pymupdf` is `Dual Licensed - GNU AFFERO GPL 3.0 or Artifex commercial`. `AGPL-3.0` is on row 11's
own `DENY` list. **It passed row 11 by not being looked at**, and it was the arm that agreed best —
1,217 of 1,219 units against the shipped pair's 1,189 of 1,218.

The exception was not taken. The arm was dropped, at a measured cost of 27 units of accuracy, and
this row was written so the next one cannot enter the same way.

**Observed red 16 August 2026** by setting `PARTIES = ("pdfplumber", "pymupdf")` in
`tools/pin_statute.py`; the gate named `pymupdf` and both denied tokens. Restored, green.

The row is checked against the DECLARED `PARTIES`, not against what happens to be installed — a
gate that only fires when the tool is present passes on every clean CI image, which is exactly
where a pinned instrument gets rebuilt.

## Rows 117–122 added LIVE — 16 August 2026, at P14-B3 and P14-B4

**117 · 118 · 119 — the API.** The two prohibitions are enforced over the GENERATED OpenAPI
document, not over a hand-written list of models, so a model added without touching the gate is
still scanned. Row 119 is the buyer decision made mechanical: an administrator's portfolio view is
exactly where somebody averages the settled fraction across templates, and the denominators are
different workbooks' unlocked-cell masks. Observed red under `ApiBareFraction` and
`PortfolioTotalRow`; 2 entries caught, 3 guards flipped, contaminated 0.

**120 · 121 · 122 — the library, the funnel, the chart.** Observed red under
`KrRendersClaimedOnly`, `FunnelSkippedCountsAsSurvived` and `HistoryMonotone`; 3 entries caught,
6 guards flipped, contaminated 0.

Three ids in `plan/07` could not be used as written. `NC-A31` and `NC-A32` were allocated at B1
(a banned phrase arriving through data, and a green entering the palette), so the B4 controls take
`NC-A35` and `NC-A36`. That is F27's shape for the third time in this build, and
`ci/catalogue-ids.sh` caught it each time.

## Rows 123–125 added LIVE — 16 August 2026, at P13-B0

**Criterion A6.** Until today *"no model is in the verdict path"* was a design intention that
happened to be true. It is now a property CI re-establishes on every commit.

`ci/barrier5.sh` did not exist. `plan/06` names it as an entry criterion for **both** P12 and P13,
and no build created it — an entry criterion naming a file nobody writes is a phase that cannot
start and nobody finds out until it does. P13-B0 creates it, and it enforces both directions: a
proposer that ships before its experiment, and — the one that gets forgotten — a proposer that
ships **against** its experiment's answer, which is worse, because a record exists and says no.

**Two findings while building the guard, both in the guard.**

1. **The first closure walk was a silent pass.** It seeded with the root module alone, and six of
   the seven verdict roots are packages whose `__init__.py` imports nothing — so it returned a
   clean closure of **size 1** for each and passed. R3's finding, occurring inside the check
   written to make the central claim mechanical. `_seed` now expands a package to its members, and
   `test_nc__A04a_the_closure_is_not_empty` asserts a floor so it cannot regress silently.
2. **A bound enforced in one module and relied on in another.** `probes/qualify.py` imported a
   relation builder by dotted name without re-checking the `cdfc.probes.relations` prefix that
   `relations/registry.py` enforces — so a `RelationSpec` built by any other path could have named
   any importable module. The repair is two lines in `qualify.py` rather than an exemption in the
   walker: **a bound the walker cannot see is a bound a reader cannot check.**

Closures after the repairs: `evaluate` 366 · `verdict` 251 · `probes` 293 · `selfcheck` 253 ·
`attest` 422 · `qualify` 330 · `surface` 53. **None reaches a banned module.**

`cdfc.api` is deliberately outside `VERDICT_ROOTS`: an API binds a socket by definition, and the
honest response to *"the rule cannot hold here"* is to say where the rule applies rather than to
weaken it everywhere. `tests/unit/test_api.py::test_api__no_socket_in_the_import_closure` carries
the API's own narrower rule — no socket in the dispatcher, only in the server.

## 2026-08-20 — gates 128–131, the N1 division map

Four gates, all `pytest`, all in `tests/negative/test_nc_div.py`. **Every one of them was observed
red for a defect this build actually shipped**, not for a hypothesis — the injectors reproduce
breaks that were in the tree during the session that wrote the module, and the guard for each was
written after reading what the broken map contained.

**Why the guards do not go through `deserialise`.** Any edit to `qualify/provisions.py` changes the
division map the instrument digest covers, so a pinned instrument refuses to load with a
`TextSourceError`. That refusal is a real property and a useless guard: all four injectors would
flip every corpus-reading test with one identical error, and the sweep would record four controls as
caught while distinguishing nothing between them. Each guard therefore reads the raw text and calls
`recover()` directly, and asserts the specific thing that specific break destroys.

**`NC-DIV01` FAILED TO FLIP ON ITS FIRST RUN, AND THAT IS THE MOST USEFUL THING HERE.**
`LevelByChainLength` replaces `_better` — the purity x coverage comparison — with raw chain length,
and all five guards stayed GREEN. The reason was a second copy: `_select` ordered its candidate
shapes with an inline sort key that recomputed the same comparison, so the choice was never made by
`_better` at all and breaking `_better` broke nothing observable.

That is `ci/GATES.md`'s own rule biting the gate being registered under it. **A control that breaks
a rule the system does not consult proves nothing**, and it would have registered as LIVE on a
guard that could never go red. The repair is one comparison: `_select` now orders through
`_better` via `cmp_to_key`, the second copy is gone, and the control flips.

Counted honestly, this is the twelfth time in this repository a check has been defeated by
something other than the thing it was checking.

| gate | injector | what goes red | positive control |
|---|---|---|---|
| 128 | `LevelByChainLength` | six schedules lost; `div1_0148` back to 181 units | `DIV05` holds |
| 129 | `AnchorAtMarkerNotLine` | `div1_0008` heading reads `'8'`; the COUNT is unchanged at 153 | `DIV05` holds |
| 130 | `AcceptUnstableChain` | both maximum chains admitted at a tied position | `DIV05` holds |
| 131 | `DoubledLetterAsBase26` | 336 false `ordinal_skipped` rows inside regulation 2 | `DIV05` holds |

`DIV05` is the positive control and it stayed green under all four. Without it a recovery that
returned NOTHING would score perfectly on the other four, each of which is an assertion about what a
wrong map contains.

### The registry's phase vocabulary now admits `N1`–`N9`

`PHASE_RE` accepted `P0`–`P15` and `A0`–`A5`, which is the two sequences `CLAUDE.md §7` names.
**There are three.** `docs/EXPERIMENT-PROGRAMME.md` numbers the experiments `N1`…, and gates
128–131 were born from one: `N1` measured that a coordinate eId dies on a resegmentation, and the
division map is what that measurement produced.

Neither existing label is true of them. `A4` dates them to a phase that has not started and that
`g0_scope.py` still refuses to enter; `A3` backdates them to one that closed before the module
existed. A gate row is a dated claim about when a guard could first be observed red, and both
alternatives make that claim false. The vocabulary was the thing that was wrong.

## 2026-08-20 — barrier 5 WIDENED to admit `RETAIN-PROVISIONAL`

`ci/barrier5.sh` admitted `src/cdfc/model/propose.py` only on `**status: RETAIN`. It now also
admits `**status: RETAIN-PROVISIONAL`, and **only when the decision record carries three fields**:
`Decided by:`, the literal phrase `Supported by no measurement`, and `Revoked by:`.

**Why widen it at all.** The barrier's purpose is that *"a proposer shipping against its own
experiment's answer is worse than one shipping before the experiment: a record exists, and it says
no."* That purpose is untouched — `DELETE` still refuses. What the old shape could not express is
the case that actually arose: an owner deciding to ship a proposer while the experiment remains
un-run, with the un-run-ness recorded rather than dressed as evidence.

**The three required fields ARE the widening.** A provisional admission that did not say it was
provisional would be a `RETAIN` in a longer word, and the gate refuses that shape explicitly.

**Observed RED before it was relied on.** The first version of the check used `^\>` in `grep -E`,
where `\>` is a WORD-BOUNDARY operator rather than an escaped `>`, so the pattern could never match
any line — and the gate refused this repository's own correctly-formatted record. That refusal was
the check working on a broken pattern rather than on a broken record, and both were fixed.

**What does NOT change:** `cdfc.model` stays in `BANNED_IN_VERDICT`; `test_nc__A04a` still walks
the closure; a proposal is data and the five gates still decide.

---

## B3, 20 Aug 2026 — the import rule gets its POSITIVE form, and the licence gate gets a second door

**What changed.** Two gates, for one reason: B3 introduces `docling`, and both existing gates
would have watched the wrong door.

### 1. `RUNTIME_THIRD_PARTY` — an allowlist, beside the denylist

`BANNED_IN_VERDICT` refuses `anthropic`, `openai`, `httpx`, `cdfc.model` and eleven others. Its own
comment says why that shape is weak: *an enumeration is a list somebody has to remember to extend,
and this project has been bitten by exactly that four times.*

**B3 walked into the fifth.** It adds a PDF reader. The obvious home for a PDF reader is
`src/cdfc/qualify/textsource.py` — that is where the two-party corroboration lives, it is the file
that already knows what an extraction is, and it is a **VERDICT ROOT**. Nothing on the denylist
says `docling`, so the import would have been admitted and the "tiny runtime closure" claim would
have become false silently, in the same commit that published a measurement resting on it.

So the rule is inverted: the verdict closure's third-party imports must be a **subset** of a
declared set. `docling`, `torch`, `pdfplumber` and every package nobody has thought of yet are
refused **by default**.

**The list was MEASURED, and the measurement corrected the alignment file.** `CLAUDE.md` named
three packages — `lxml`, `cel-python`, `openpyxl`. Walking the graph found **six**: `celpy`,
`lark`, `lxml`, `openpyxl`, `yaml`, `z3`. `z3` is an SMT solver reached through
`cdfc.qualify.g3_degeneracy`, which decides degeneracy by proof rather than by sampling, and
`yaml` is the predicate authoring format. Both were load-bearing and undescribed. **`CLAUDE.md`
was corrected to match the tree; the allowlist was not trimmed to match `CLAUDE.md`.**

The second gate exists because an allowlist of ghosts refuses nothing: every allowed package must
be **actually reachable** from a verdict root, or the row comes out.

### 2. `ci/no-denied-build-tool.sh` — every declaring file, not one filename

The gate read `tools/pin_statute.py` **by name**. B3 adds `tools/pdf_ingest.py`, which declares its
own `PARTIES`. A gate hard-coded to one filename would have watched the first door with the second
standing open — which is, exactly, the failure this gate was written for: *a denylisted licence
entering through a door the gate does not watch.* It now scans every `PARTIES` tuple under
`tools/`, and a tree where **nothing** declares any is itself a failure, because that is what a
renamed constant looks like from here.

It also learned **PEP 639**: modern wheels leave the legacy `License` field empty and declare
`License-Expression`. `docling` is the live instance — it declares `MIT` there and nothing in the
old field. Reading only the legacy field would have reported *"declares no licence"* about an
unambiguously MIT package, and a gate that fails for the wrong reason is a gate somebody switches
off.

**The widened gate went red on its first run, and the defect was mine.** Supporting
`PARTIES: Final[...] = (...)` needed a regex over the annotation, and `[^=]*` **matches newlines**
— so it ran past the real declaration and captured a later tuple in the same file, reading
`pin_statute.py`'s parties as `("pymupdf", "pypdf")` and refusing an AGPL arm that file explicitly
excludes. Constrained to `[^=\n]*`.

**What does NOT change.** `unify_quotes` stays in `REFUSED_TRANSFORMATIONS`. B3 measured that
**102 of 115** disputed units on the FinCEN instrument are docling folding `'` to `'`, and folding
them back would raise the addressable fraction from 286/401 to roughly 388/401 — at the cost of
making a homoglyph substitution unlocatable by `test_g0__verbatim_quote_required`, the gate that
exists to catch it. That is the trade this repository refused for dashes at P7. It is refused
again, the cause is attributed in `docs/measurements/B3-pdf-ingress.md`, and the units stay
DISPUTED.
