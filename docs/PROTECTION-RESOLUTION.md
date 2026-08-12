# docs/PROTECTION-RESOLUTION.md

**Written before either mask path was coded.** Two implementations of an unwritten rule are two guesses;
two implementations of *this* rule are a differential check. `styles_mask.py` (path A) and
`styles_mask_b.py` (path B) both implement what is below, and neither may be derived from the other.

**Why this document is load-bearing.** The field surface is the denominator every number this product will
ever print is a fraction of. It is not read off the file — it is *resolved* from a rule, and the rule has
lawful alternatives that return different answers on the same bytes.

---

## The rule

```
1. A cell's style id  s = <c @s>,  defaulting to 0.

2. cellXfs[s] is the cell format. If it carries a <protection @locked> attribute,
   that value wins outright.

2a. If cellXfs[s] carries a <protection> ELEMENT that does not declare @locked — e.g.
   <protection hidden="1"/> — the element is PRESENT and @locked takes its ECMA-376
   attribute default of TRUE. This is an explicit lock, NOT an inheritance case.
   Rule 3 applies only when there is no <protection> child at all.

3. If cellXfs[s] carries NO <protection> child, the locked bit is INHERITED from
   cellStyleXfs[ cellXfs[s].@xfId ]. If that also declares nothing, the OOXML
   default applies: locked = "1".

4. @applyProtection is a RENDERING HINT. It is not a precondition for honouring an
   explicit locked="0".

5. A cell is IN THE FIELD SURFACE iff (locked resolves to false) AND (the cell has
   no <f> child). A formula cell is not a field a filer fills.

6. If NO sheet in the workbook carries <sheetProtection>, the mask is NOT DERIVABLE:
   field_surface = None, and denominator.source states why. THIS IS CHECKED BEFORE
   STEP 5, so a stray unlocked style id cannot manufacture a small answer from a
   workbook that ships no protection mask at all.
```

## The census this rule was written against

MEASURED on the FME workbook, 434 `cellXfs` entries:

| class | count |
|---|---:|
| explicit `locked="0"` | 105 |
| `<protection hidden="1"/>` — element present, no `@locked`, so locked by attribute default (rule 2a) | 7 |
| no `<protection>` child — inherits (rule 3) | 322 |

**Rule 2a was added after the first implementation disagreed with this census.** Path A initially treated
a `<protection>` element without `@locked` as an inheritance case, giving 105 / 0 / 329. Under `v3` both
readings resolve to locked and the field surface is 3,747 either way — the divergence only appears under
`v3-abs`, where it returned 6,252 against the expected 6,249. **Three cells, in a reading we reject
anyway, exposed an ambiguity the rule did not cover.** That is the argument for computing the rejected
readings at all rather than only the adopted one.

**Rule 4 is not a detail.** 112 `cellXfs` carry `applyProtection="1"` and 105 carry `locked="0"`, and the
two sets are not the same. An implementation that required `applyProtection` before honouring `locked="0"`
would return a different denominator, lawfully.

## The three lawful readings

All three are readings a competent engineer produces from ECMA-376. Every surface that prints a settled
fraction prints `denominator.generator_rule` beside it, resolving to a row of this table.

| rule id | reading | FME field surface | status |
|---|---|---:|---|
| `v3` | rules 1–6 above — inheritance resolves to locked; formula cells excluded | **3,747** | **ADOPTED** |
| `v3-uw` | as `v3` but without excluding unlocked formula cells | 3,755 | lawful, not adopted |
| `v3-abs` | absence of `<protection>` read as UNLOCKED | 6,249 | lawful reading of the same XML, **REJECTED** by NC-D05 |

`v3-abs` adds 2,502 cells. It is rejected because OOXML's default is `locked="1"` and reading absence as
unlocked inverts the default — but it is rejected by *argument*, not by measurement.

---

## NOTHING IN P2 CAN FALSIFY THE CHOICE

This is the honest limit and it is stated where the number is defined rather than discovered later.

The rule is written by us. Both paths implement it. The differential check proves only that they are **two
implementations rather than one function called twice** — it cannot tell us the rule is right, because both
paths would agree just as well on `v3-abs`.

**The external falsifier arrives at P8-B1**: at least thirty workbooks filled by a competent person who has
never seen the predicate set, whose manifest records the cells actually written into. *The set of cells a
real filler used is a direct, independent measurement of "the cells a filer may fill" — which is exactly
what the mask is a proxy for.* The plan already buys that data.

Until then `FieldSurface.validation_state` is **`PROVISIONAL-UNVALIDATED`**, it is carried into every
`SettledFraction.denominator`, and it is rendered on every surface that prints the fraction.
`test_contract__denominator_declares_its_validation_state` asserts no render path drops it.

## The defect this phase's own headline number cannot see

From the plan's §0.2 N2, and it is the reason the mask is computed twice rather than checked once:
**scope truncation by hidden sheet leaves the FME field surface at exactly 3,747.** The `Dropdown` sheet is
`state="hidden"` and contributes no unlocked non-formula cells, so an implementation that skipped hidden
sheets entirely would return the same number — and the number would be right by accident while the code was
wrong. `test_nc__D03_hidden_sheets_are_in_scope` catches it by asserting the *sheet set*, not the total.
