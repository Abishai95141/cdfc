# The adversarial audit of the A1 diff

*Run 20 Aug 2026 against `ff5ed62`. The A1 diff is `014cb72..276e1af` — five commits, 41 files,
876 insertions. **A2 entry criterion.***

**Method: attack, with the default position that every claim in the diff is wrong.** A1 was
verified by seven probes and had never been attacked. Every claim below was tested by RUNNING
something; nothing is adjudicated from a docstring.

---

## Result: six of seven claims survive; one real defect

| claim | attack | verdict |
|---|---|---|
| `A1-1` the Anchor carries table/rows/cols | construct one and read the fields | **SURVIVES** |
| `A1-2` imported by 22 modules | an import is not a migration — AST-count the modules that CONSTRUCT one | **SURVIVES** — 22 import, **22 construct**, 0 import-only |
| `A1-3` `run_filing` takes a template | is `template=None` a real default or a skipped check? | **SURVIVES** — default and explicit-FME return an **identical run id** and the same 3,747 surface |
| `A1-4` a foreign workbook is not VALID | is the INVALID for the right reason, or something else wearing it? | **SURVIVES** — ALR/FME is `INVALID` with `invalid.denominator_disagreement` and **partition `None`**, so nothing is scored |
| `A1-5` `denominator_disagreement` is reachable | raised in a real run, or only referenced? | **SURVIVES** — observed firing above |
| the run-id widening | does the id actually move? | **SURVIVES** — ALR/ALR, ALR/FME and FME/FME are three distinct ids |
| the graded-binding revert | dead code left behind? | **SURVIVES** — no residue |
| **`render()` is byte-identical to the old cell string** | **eleven adversarial sheet names** | **DEFECT — see below** |

The render itself is byte-identical on ten of eleven, including spaces, an apostrophe, non-ASCII,
an 80-character name, an embedded quote, a tab and a newline. The eleventh — an empty sheet name —
**raises deliberately**, carrying E2's finding that the literal `NULL` is absence and must not
become the name of a table nobody has. That is correct behaviour, not a failure.

---

## THE DEFECT: only the LAST `!` delimits a cell string, and eighteen call sites used the first

A cell string is `<sheet>!<ref>`. **A reference can never contain `!`. A sheet name can** — Excel
permits it and `openpyxl` accepts it, both verified rather than assumed.

`Anchor.parse` **right-splits and is correct**. Eighteen call sites across `src/` and `tools/`
left-split, so:

    rendered            'Bad!Name!A1'
    Anchor.parse   ->   'Bad!Name'                 correct
    partition('!') ->   sheet='Bad'  ref='Name!A1' what eighteen sites saw

**The anchor and the rest of the codebase disagreed about which character was the delimiter** — on
exactly the path A1 exists to serve: *a buyer's own workbook is checkable without a code change.*

### Demonstrated end to end, not argued from a string

A workbook with the sheet `Bad!Name` was built, saved, and run through the **shipped**
`surface_for`:

    field surface        9 cells
    a ref                'Bad!Name!A1'
    Anchor.parse         'Bad!Name'
    partition('!')       'Bad'          <- disagreement, on real bytes

And the consequence is not cosmetic. `probes/qualify._reads` turns a cell string into a CEL path:

    right-split   cel_path('Bad!Name', 'A1')   ->  'bad_name.r1.ca'
    left-split    cel_path('Bad', 'Name!A1')   ->  ValueError: not a cell reference

`_reads` catches that `ValueError` and returns **False** — a relation silently reported as not
reading a cell that it does read. A wrong answer wearing the shape of a right one.

### Severity

**Latent, and latent is not fixed.** None of the nine pinned blanks carries `!` in a sheet name, so
nothing in the current corpus triggers it. The whole point of A1 is that the corpus is no longer
the limit.

---

## The fix, and what keeps it fixed

**22 sites now right-split** (18 found by the audit plus 4 more the same sweep turned up).
`rsplit("!", 1)` and `rpartition("!")` are drop-in: a ref never contains `!`, so the last one is
always the delimiter.

Three things hold it:

1. **`ci/no-left-split-on-cell.sh`** — gate **126**, registered in `ci/GATES.md` with its dated
   argument in `docs/GATE-CHANGES.md`. Observed RED under a planted `partition("!")`.
2. **`NC-A37`** with the `LeftSplitOnCell` injector, whose flipping guard exercises `_reads`
   against a bang sheet — **verified to flip red under the injector**, because a control whose
   guards all stay green proves nothing.
3. **Two behavioural tests**: the render stays byte-identical, and a bang-named workbook survives
   the real field surface with both parsers agreeing.

### A change the fix forced, recorded rather than slipped in

`PHASE_RE` in `src/cdfc/gates.py` accepted only `P0`–`P15`. Gate 126's subject first exists in the
**A-sequence**, which the registry's grammar predated, and writing the nearest P-number would have
put a false statement in the column that decides whether a gate can ever be observed red. The
regex is widened to admit `A0`–`A5` and `A1c`. **A widened check that admits anything is not a
check**, so `test_contract__registry_rejects_a_phase_outside_both_sequences` pins the sixteen
strings it still accepts and refuses.

---

## What this audit did NOT cover

* **The 64-site Anchor migration was not re-verified site by site.** `make determinism` and the
  `A1-7` hazard instrument cover byte-stability; this audit attacked the render CONTRACT rather
  than each call site's use of it.
* **No adversarial test of the upload path's failure modes** beyond the 201 and 422 branches
  already probed — the 413, 415 and 503 branches were read, not attacked.
* **Recall is untouched.** This audit found what it thought to look for. Six claims survived
  attack; that is evidence about those six, not about the diff as a whole.
