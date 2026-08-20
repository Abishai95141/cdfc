# C1 — any template intake, measured over nine real regulator blanks

*Run 20 Aug 2026 over `fixtures/prescribed/*.xlsx`. Reproduce with the loop in
`tests/unit/test_evidence_layer.py::test_schemafree__an_UNREADABLE_template_is_DISTINGUISHABLE_from_an_empty_one`.*

| blank | surface | labelled | state |
|---|---|---|---|
| `ALR_V2_3` | 1,599 | 124 | derived |
| `AL_monthly_report` | 3,537 | 648 | derived |
| `Draft_ACAC_Format` | 0 | 0 | **REFUSED** `no_protection_mask` |
| `EDR_1_Exposure_Data_Report` | 162 | 139 | derived |
| `IBU_Operations_Report` | 459 | 87 | derived |
| `IFSCA_Annual_Reporting_Format` | 0 | 0 | **REFUSED** `no_protection_mask` |
| `ITFS_Monthly_report` | 481 | 63 | derived |
| `Reporting_Format_for_FMEs` | 3,747 | 132 | derived |
| `Quarterly_Reporting_CMI` | 2,255 | 785 | derived |

**7 derived · 2 refused with a reason · 0 silently empty · 0 crashes.**

## What was wrong, and what was NOT wrong

`cdfc.schema.styles_mask` RULE 6 returns `n_cells=None` when a workbook ships no
`sheetProtection`. **That is correct and it was not changed.** The field surface is read from the
unlocked-cell mask; with no mask there is nothing to read, and `None` is the honest answer.

The defect was one layer up. `from_template` carried that `None` into `FieldSet.surface_total`,
which is **declared `int`**, and produced a field set with zero fields. Every downstream count then
read *"this template has no fields"* where the truth was *"we could not read this template"*.

## A decision that was already right, and the gap it left

`test_schemafree__runs_on_every_pinned_blank_without_a_code_change` records:

> *"they must return an EMPTY field set rather than raise — 'we cannot read this' is a state, not
> a crash."*

That is right, and a first attempt to raise `TemplateNotInducible` was **reverted** because of it —
a caller iterating nine blanks should not have to catch. What the decision left open is that the
state was **indistinguishable**: the test asserted `isinstance(len(fs), int)`, which an empty
FieldSet satisfies either way.

So the refusal is **carried**: `FieldSet.refusal` is `None` when the surface was derived, and a
`SurfaceRefusal` when the zero is not a measurement.

## The limit this measures, and it is a real one

Both refused workbooks ship **zero `dataValidation` elements** as well as no protection mask —
`Draft_ACAC_Format` has 13 sheets and 3,793 cells, `IFSCA_Annual_Reporting_Format` has 9 sheets and
1,708 cells. **Neither explicit induction signal is present in either.**

So "any template" is currently **7 of 9 on this corpus**, and the two failures are not a parsing
bug to fix: they are workbooks that declare nothing about which cells a filer may write. Inducing a
surface for them means inferring it structurally — empty cells adjacent to labels — which is a
weaker kind of evidence than a declared mask and must be labelled as such if it is ever added, in
the same way `Derived` fills and `ResolvedBy.MODEL` entities are.

## What this does NOT establish

* **One regulator.** Nine blanks, nine layouts, but all IFSCA. `D2` measured the XSD ingress on
  FinCEN separately; these nine are not a cross-jurisdiction claim.
* **No structural induction exists yet.** The 2 refusals stay refusals.
