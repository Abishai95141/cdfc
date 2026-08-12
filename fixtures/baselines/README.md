# fixtures/baselines — frozen prior measurements, kept as EVIDENCE and not as truth

## `harvest-v0.json`

The output of `research/scripts/predicate_harvest.py`, the research-phase harvest, byte-frozen on
12 Aug 2026. **515 predicates and 389 weak records across the nine prescribed workbooks.**

It is frozen so that P4-B4's harvest can be compared against something that was written before it,
by a different person's reasoning, rather than against nothing. **It is not an authority.** It came
from the same script family that produced two of this project's documented silent false negatives,
and it has two defects of its own, both found by P4-B4 and both named here rather than left for a
reader to discover.

### Defect 1 — it is blind to shared formulas

v0 reads `<f>` element text directly. A shared dependent is written `<f t="shared" si="0"/>` and
carries **no text**, so v0 saw nothing for any of them. On the FME workbook that is **211 of 505
formula cells — 42%**, and every relation they encode was invisible to it.

P4-B4 materialises a dependent by shifting its master's expression to the dependent's cell
(`cdfc.calc.shift.materialise`, built at P3 for exactly this). That alone accounts for most of the
increase: FME's `sum_identity` count goes from 19 comparable to **79**, and `same_sheet_equality`
from 11 to **42**.

*Why nothing caught it in the research phase:* the formula-cell COUNT was right. 505 was reported
and 505 is correct. Only the bodies were missing. This is the same defect shape as `<f[ >][^>]*>`
over OOXML one level up — a correct count with wrong contents — which is why the project now has
`ci/no-regex-over-xml.sh` and its P4 sibling `ci/no-regex-over-cel.sh`.

### Defect 2 — it counts calls it cannot express

v0 matches `^SUM\((.+)\)$` and `^COUNTIFS?\((.+)\)$` greedily, so `SUM(A1:A5)+SUM(B1:B5)` and
`COUNTIF(a,"x") + COUNTIF(b,"y")` were **counted as predicates** while no expressible relation was
ever derived from them. On FME that is 58 formulas counted and not expressed.

P4-B4 counts parentheses instead of matching a pattern, and a body that is not exactly one call
becomes a typed `function_outside_vocabulary` skip. **The harvest under-produces and declares it,
rather than over-claiming.**

### What P4-B4 measures instead

**592 candidates, non-empty on 7 of 9 workbooks**, with every difference from v0 attributable to
one of the two defects above or to a typed skip. `docs/HARVEST-DELTA.md` entry #1 carries the
per-workbook reconciliation, and `docs/measurements/P4-harvest-distribution.md` carries the
distribution.

**The frozen file is never edited.** If v0 is ever re-run, the new output goes in a new file with a
new name and both stay.
