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
