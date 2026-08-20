# B1 — the return gets filled, and nothing else changes

*Built and measured 20 Aug 2026. `make demo-fill` reproduces it. Writer: `src/cdfc/fill/write.py`.
Controls: `tests/contract/test_fill_write.py`, 16 tests including **four negative controls**.*

---

## The result, on the REAL vendored IFSCA blank

    template   7d9a1960085785ee…   (fixtures/prescribed/Reporting_Format_for_Fund_Management…)
    output     b29295d96a3be6e5…
    parts rewritten   1   ['xl/worksheets/sheet1.xml']

    parts             42 -> 42
    x14 validations   19 -> 19        parsed, not byte-counted
    cells           6757 -> 6757
    cells changed      1   named 1
    crc               OK · 22 xml parts re-parsed
    wall clock      0.35 s

    1. Introduction!D10 = 'Registered FME (Retail)'   [evidenced]
    attestations left blank  8

**Read back out of the file, not out of the record.** An assertion against the in-memory record
would prove the record is self-consistent and nothing about the artefact.

## Why raw-zip surgery and not the obvious thing

`ci/no-openpyxl-writer.sh` exists because an openpyxl round-trip of this workbook **drops 24 parts
and all 19 `x14` data validations and shrinks 3.66 MB to 66 kB**. A "filled return" written that
way is a different document that shares a name: the filer's dropdowns are gone and the data model
is gone.

So the write goes through `cdfc.qualify.surgery.write_cells` — every zip entry copied byte-for-byte
with its original compression parameters, worksheet XML parsed rather than pattern-matched, and a
refusal if any part changed that no edit named.

**That writer was EXTRACTED from the mutant seeder for this build.** The fill path and the mutant
path need identical guarantees for opposite reasons — a mutant that lost a part would make the
observability diff a diff of the writer, and a filled return that lost one would be a different
document handed to a regulator. One writer, two callers, and they cannot drift.

## The invariant this adds ON TOP of the writer's

`write_cells` guarantees no unnamed **part** changes. That is not enough: a bug in edit planning
could rewrite the right part and the wrong **cell** inside it, and a part-level check passes that.

`verify_written` re-opens both workbooks and compares **every cell of every sheet** — 6,757 of
them — asserting the differing set is exactly the set the declaration named.
`test_nc__write__a_cell_changed_that_the_record_did_not_name_is_REFUSED` constructs precisely that
case and requires it red.

## Both lanes are written; only one is counted

An `admitted` fill is evidenced — a span re-reads it byte-exact. A `derived` fill is a value a
model produced that no span supports. **Both go into the return**; `FillWriteRecord` carries them
as separate counts with a per-cell provenance row, and a `derived` cell carries `span: null`, which
is the distinction rather than a missing field.

**An ATTESTATION is never written**, whatever evidence supports it. 8 of them on this return.

## THREE DEFECTS OF MINE, ALL FOUND BY RUNNING IT

**1. The validation count was a byte count, and it was wrong by 29.** `b"x14:dataValidation"`
occurs in the opening tag, the closing tag AND the `<x14:dataValidations>` container, so it reported
**48** where this blank carries **19** — the figure `NC-Q30` and the writer gate both cite. The
invariant being guarded, *before equals after*, **held under the wrong number just as well as the
right one**, which is exactly how a bad count survives: it was never the thing failing. Now counted
by parsing, and `test_write__x14_is_COUNTED_BY_PARSING_not_by_matching_the_tag_name` pins both
numbers so the naive one cannot come back unnoticed.

**2. I asserted `>= 30` XML parts, a number nobody had counted.** There are **22**; the other 20 of
the 42 entries are `.rels`, `.bin` and `.vml`. Pinned at the measured figure.

**3. The first run wrote into an already-filled fixture** — `clean__template-computed__fme-q1.xlsx`
— so the value was already there, the part came out byte-identical, and `write_cells` refused with
*"parts changed [] but the edits name…"*. The guard was right and the input was wrong. That refusal
is now a negative control.

## The four negative controls, each constructing the failure

| control | constructs | asserts |
|---|---|---|
| `a_lost_part_is_REFUSED` | a workbook with `sharedStrings.xml` removed | `part list changed` |
| `a_lost_x14_validation_is_REFUSED` | the `<x14:dataValidations>` block stripped | `data validations went from` |
| `a_cell_changed_that_the_record_did_not_name_is_REFUSED` | two cells written, one named | `changed but unnamed` |
| `write_cells_refuses_a_no_op` | the same value written twice | `parts changed` |

Each asserts its own fixture is real before asserting the refusal — a control whose fixture failed
to break anything would pass by accident.

## A finding about the test harness itself

`test_write__opens_clean_and_every_part_reparses` **deliberately does not use openpyxl**.
`pyproject.toml`'s non-negotiable block sets `filterwarnings = ["error"]` so that openpyxl's
*"Data Validation extension is not supported and will be removed"* cannot be discarded — and
reading this workbook raises it, **because the 19 validations are there**. The warning firing is
evidence the write preserved them; using the reader that raises it as proof would be circular and
would also fail the suite. Every part is re-parsed through `xmlsafe` instead.

## What this does NOT establish

* **Nothing here says a filled value is CORRECT.** It says the return was written faithfully: the
  value the declaration named is the value in the cell, and nothing else moved. Accuracy needs the
  30 filing-plus-source-pack pairs and is unmeasured.
* **One cell was filled**, because the binder is weak — that is `B2`, not a limit of this writer.
  `test_write__both_lanes_are_written_and_told_apart` writes two, so the multi-cell path is
  exercised.
* **No formula cell was overwritten**, and the behaviour if one were is inherited from
  `_mutate_element`: the `<f>` is dropped, which is `F11`'s fault shape. Whether a fill SHOULD ever
  overwrite a formula is undecided and is not decided here.
