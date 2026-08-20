# A5 — the fill lane, built and measured

*Built 20 Aug 2026. `src/cdfc/fill/propose.py`, 12 controls in `tests/contract/test_a5_fill.py`,
one positive control per condition. `cdfc.fill` is inside `VERDICT_ROOTS`.*

---

## What it is

Two lanes and six mechanical conditions. **FACT** proposes a value from evidence; **ATTESTATION**
assembles the evidence, records what is being certified, and stops — a certification is a natural
person accepting liability, and no system may forge one.

    1  GROUNDED            at least one observation is bound to this field
    2  REVERIFIES          the observation re-reads BYTE-EXACT at the span it cites   <- the trigger
    3  UNIQUE              the verified observations agree on one value
    4  TYPE_ADMITS         the value parses under the type the TEMPLATE declares
    5  VOCABULARY_ADMITS   for an ENUM, the value is in the template's own list
    6  LANE_IS_FACT        the field asks for a value, not a signature

**The trigger is mechanical, never a model's confidence.** `W0-C` had a similarity locator return
`SUPPORTED` **20 of 20** times on evidence that had been DELETED. So the question is not *how sure
are we* — it is *does the cited span reproduce the exact bytes*. There is no score anywhere in this
module and no threshold.

Every proposal carries **all six outcomes**, held or not, so a reader can see which condition was
load-bearing. Conditions after a failure are reported as `not reached` rather than omitted — a
report that silently dropped the checks it skipped would imply they passed.

`FillDeclaration.__post_init__` refuses construction unless the three lanes **partition** the field
surface, the same discipline `RuleCoverage` applies to rules and `Linkage` to records.

## It works

A precise binding onto a field the template types, against a two-reader source pack:

    field    1. Introduction!D10    type=enum
    vocabulary  ['Registered FME (Retail)', 'Registered FME (Non-Retail)', 'Authorised FME']
    ADMITTED FILL = 'Registered FME (Retail)'
      evidence source-pack.pdf span (47, 70), re-verified byte-exact
      GROUNDED HOLDS · REVERIFIES HOLDS · UNIQUE HOLDS
      TYPE_ADMITS HOLDS · VOCABULARY_ADMITS HOLDS · LANE_IS_FACT HOLDS

## THE GUARDRAIL HELD UNDER A DELIBERATELY BAD BINDER

A crude binder — label-token overlap, declared as crude — bound 13 fields against a source pack.
**A5 admitted zero of them**, and every refusal reads correctly:

| refusal | n | what the binder had done |
|---|---:|---|
| `support_contradicted` | 6 | attached 2–4 unrelated numbers to one field; A5 refused rather than picking |
| `type_not_admitted` | 3 | the template declares no type for those cells |
| `vocabulary_not_admitted` | 1 | offered `'12,40,00,000'` to a 2-value ENUM |
| routed to ATTESTATION | 3 | correctly not a fill at all |

**That is the result that matters.** The lane refused 100% of a bad binding without being told the
binding was bad. Producing the binding is `cdfc.correspond`'s job or, once `E6` licenses one, a
model's; `propose()` takes it as an argument and requires `binding_provenance`, because a refusal
that cannot say *whose* proposal it refused is not an audit record.

## TWO FINDINGS ABOUT THE TEMPLATE, NOT ABOUT THE FILL LANE

**1. You cannot fill a filing from the statute, and the first run tried.** Against the pinned IFSCA
instrument as the source, A5 proposed **0 of 3,747** — correctly. The statute says *"net worth
shall not be less than USD 500,000"*: that is a **threshold**, not the entity's net worth. Filling
needs the entity's own documents. This is exactly what the "30 filing-plus-source-pack pairs"
blocker is for, and the first run made the reason concrete rather than theoretical.

**2. The FME return declares a type for 88 of its 443 labelled fields, and has NO money field.**

    undeclared   355 of 443
    enum          69
    percent       11
    text           5
    date           3
    money          0

`TYPE_ADMITS` therefore refuses **355 labelled fields permanently**, because a value placed in a
field whose type nobody declared cannot be checked by anything downstream. That is a property of
the workbook, not of this module — and it is the strongest argument yet for the XSD ingress (`D2`),
where **3,837 of 3,837** fields carry a declared type.

## The full declaration, over the real return

    of 3747 fields in the surface, we propose a value for 0.
    the typed reason for each of the others:
      field_not_labelled     3304 of 3747
      no_observation          415 of 3747
      support_contradicted     10 of 3747
      vocabulary_not_admitted  10 of 3747
    awaiting a named signatory  8 of 3747

`field_not_labelled` at 3,304 is the largest lane and it is the same population `N2` measured: we
cannot bind evidence to a cell we cannot name.

## What this does NOT establish

* **No fill accuracy is measured.** That needs the 30 filing-plus-source-pack pairs. Nothing here
  is a claim about how often a proposed value is right.
* **The binder is not part of A5 and the one used here is crude.** Its own quality is unmeasured.
* **Nothing writes a workbook.** `ci/no-openpyxl-writer.sh` exists because an openpyxl round-trip
  of the FME workbook drops 24 parts and all 19 `x14` validations and shrinks 3.66 MB to 66 kB. A
  "filled" template written that way is a different document that shares a name. Fills are DATA;
  writing one needs raw-zip surgery and is a separate gated decision.
* **`UNDECLARED` is refused rather than filled-and-flagged.** The alternative — fill it and mark
  the type unchecked — is defensible and is NOT taken here. Recorded in `docs/OPEN-ITEMS.md` as a
  decision rather than left as an accident.
