# docs/GATE-CHANGES.md

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
