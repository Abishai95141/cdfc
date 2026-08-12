# docs/READER-COMPETENCE.md

**Append-only.** One row per field: the written definition, and why each instrument is or is not a party.

**Why this file decides whether the agreement check survives.** Comparing reader A against a reader known
to be blind to a field fires on every filing — and a check that always fires is a check somebody switches
off. So a field names its parties, and every exclusion carries the set of workbooks on which the
incompetence was **measured**. A field may only be compared on a workbook inside that set; anywhere else
the cell reads `NOT_COMPARABLE(competence_unmeasured)`, **never `AGREE`**. Widening the set requires the
measurement, not an edit.

## The instruments

| id | what it is | traversal |
|---|---|---|
| **A** `reader_lxml` | authoritative: raw zipfile + lxml, namespace-aware | walks `xl/workbook.xml`'s relationship graph |
| **A′** `reader_lxml_b` | a second implementation of the same eight fields, by a different route | enumerates `[Content_Types].xml` overrides; counts structurally; matches qualified names anywhere in the tree |
| **B** `reader_openpyxl` | the ecosystem's standard library | its own |

**A′ is deliberately not a refactor of A.** A shared traversal bug is the only way two readings can be
wrong together, and `test_nc__P03_readers_A_and_A_prime_are_not_the_same_traversal` fails the build if A′
starts reading the relationship graph. **They share an author, though** — which is why the four fields
only they can compare are published as a separate vector labelled SAME-AUTHOR.

## The eight fields

| field | definition | parties | measured_on |
|---|---|---|---|
| `n_sheets` | count of `<sheet>` elements in `xl/workbook.xml`, ANY state | A, A′, B | all nine |
| `sheet_names` | the `@name` of each `<sheet>`, in document order | A, A′, B | all nine |
| `hidden_sheets` | the `@name` of each `<sheet>` whose `@state` is not `visible` | A, A′, B | all nine |
| `merged_ranges` | the `@ref` of every `<mergeCell>`, across every worksheet part | A, A′, B | all nine |
| `n_cells` | count of `<c>` elements — **not** non-empty values | A, A′ | all nine |
| `n_formula_cells` | count of `<c>` containing an `<f>` child, **any** encoding | A, A′ | all nine |
| `n_validations` | `dataValidation` in the main namespace **plus** the `x14` extension | A, A′ | all nine |
| `n_defined_names` | `definedName` in `workbook.xml`, **any** scope | A, A′ | all nine |

The definition is the contract. Two readers agreeing on a number they define differently is a
coincidence, not a check — `n_cells` is the clearest case: A counts elements, B counts values, and on the
FME workbook that is 6,757 against 3,740.

## Why B is excluded from four fields, and the measurement behind each

Re-measured on every run by `tools/measure/agreement_matrix.py`. A pinned control that is never re-taken
is a claim about the past.

| field | mechanism | measured |
|---|---|---|
| `n_validations` | namespace-blind: reads the main namespace and discards `x14`, with a warning it expects the caller to ignore | **misses 37 of 234 across the nine — 15.8%** |
| `n_cells` | counts non-`None` values, not `<c>` elements; an empty styled cell is still a cell | FME 3,740 against 6,757 |
| `n_formula_cells` | returns `ArrayFormula` objects and does not expose shared dependents | FME 504 against 505 |
| `n_defined_names` | workbook scope only; sheet-local names absent | FME 4 against 12 |

### The validation blind spot, per workbook

The flagship instance is not the worst one.

| workbook | A | B | missed |
|---|---:|---:|---:|
| AL monthly | 10 | 1 | **9 — B sees one validation in ten** |
| FME quarterly | 54 | 35 | 19 |
| ITFS monthly | 16 | 7 | 9 |
| CMI quarterly | 142 | 142 | 0 |
| ALR · EDR · IBU · Annual · Draft ACAC | 7 · 1 · 4 · 0 · 0 | same | 0 |

**AL-monthly is a 90% under-count** and it appears in no research document, because the corpus was only
ever examined through the FME workbook. It was found by re-measuring rather than remembering.

## What this file does not establish

- **B's exclusions are measured; A′'s competence is asserted.** A′ is a party to all eight fields because
  it was written to be, not because anything measured it. The four A/A′-only cells are a self-check and
  are labelled SAME-AUTHOR wherever they are rendered.
- **The residue of `constructs_not_understood` contains only what we knew to look for.** A construct in a
  namespace we never enumerate is invisible to A and A′ together. P1 makes that residue visible; it does
  not close it.
