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
