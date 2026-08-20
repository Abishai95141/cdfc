# D2 — a second ingress: a field surface read from an XML schema

*Run 20 Aug 2026. `make e2e` reproduces it. Reader: `src/cdfc/schema/xsd.py`.
Controls: `tests/contract/test_xsd_surface.py`, 10 tests including 2 positive controls.*

---

## Why this was the gap that mattered

The product claim is *"upload your exports in whatever shape they arrive"*. The ingress was `.xlsx`
and nothing else, so "whatever shape" meant "whatever **workbook**", and the schema-free result —
nine workbooks, 1,729 units, zero per-workbook configuration — was really a *spreadsheet*-free
result. A regulator that declares its return as an XML schema was unreadable.

FinCEN publishes `BSA_XML_2.0.xsd`. ESMA, EIOPA and every XBRL-lineage regulator do the same.

## The result

    schema        fincen-bsa-xml-2.0        namespace www.fincen.gov/base
    declared      3,881 elements  ->  3,837 fields + 44 refused
    typed         3,837 of 3,837            TEXT 2,466 · COUNT 1,086 · DATE 285
    labelled      3,293 of 3,837            the regulator's own <xsd:documentation>
    containers      366
    refused          44 of 3,881            all `type_declares_no_unit`
    wall clock     0.04s

**Nothing is inferred.** This is the same architectural move as reading a workbook's number formats
and data-validation lists: the regulator declared the type, the label and the cardinality, and the
reader reads them. Zero configuration for this schema exists anywhere in the tree.

### The XSD is BETTER evidence than the workbook, by a wide margin

| | IFSCA workbook (`.xlsx`) | FinCEN schema (`.xsd`) |
|---|---:|---:|
| field-surface members | 3,747 | 3,837 |
| carrying a **usable label** | **132** | **3,293** |
| carrying a **declared type** | from number formats, partial | **3,837 of 3,837** |

`N2` measured the workbook side: of 498 label candidates, **351 were the literal string `NA`** and
the real labelled population is 132. The schema hands over 3,293 labels because a schema author is
obliged to say what a field is and a spreadsheet author is not.

**This matters beyond ingestion.** `docs/OPEN-ITEMS.md` carries "50 labelled proviso spans" as a
human blocker gating the semantic half. Labels are the scarce input, and an XSD ingress supplies
them by the thousand from the regulator's own words.

## THE COUNT THAT WAS ABOUT TO BE PUBLISHED WRONG

The first version of this reader flattened the tree, and 3,837 was reported as a field surface
directly comparable to the workbook's 3,747 cells.

**It is not comparable, and the correct figure is:**

    single-valued fields    0 of 3,837
    multivalued fields  3,837 of 3,837

`BSABase.Activity` is `maxOccurs="unbounded"`. So is `Party`, and `Account`, and 50 others. **Every
field in this schema sits under a repeatable ancestor**, which means `Activity.Party.PartyName` is
not one address — it is one value *per party per activity*, and how many of those exist is a
property of the filer's data, not of the schema. A workbook cell is an address; an XSD leaf is a
path into a list.

The tell was a suspicious pair — `required 0 of 3,837` and `repeatable 0 of 3,837` — and opening it
found the flattening. `FieldDecl.repeating_ancestors` now travels with every field and
`test_xsd__multivalued_fields_declare_their_repeating_ancestors` pins it. Ninth instance of *a
count is not a reading* in this repository.

## Two further facts the schema states and we must not soften

* **`required` is 0 of 3,837, and that is correct.** 1,527 of 1,528 elements declare
  `minOccurs="0"`; only the root does not. **FinCEN mandates nothing in the schema** — requiredness
  lives in its business rules, which are a separate artefact. A consumer must not read "0 required"
  as "nothing is mandatory".
* **`vocabularies` is 0 of 3,837.** This schema declares no `<enumeration>` anywhere; its code
  lists live in a separate `www.fincen.gov/codes` namespace this checkout does not have. The ENUM
  branch is therefore exercised by a **positive control** rather than by the corpus — a vocabulary
  path nothing exercises is a path nobody has seen work.

## `xsd:decimal` is refused, and that is the whole design in one decision

All 44 refusals are `type_declares_no_unit`, and 44 of 44 are `xsd:decimal`. The repository's money
type is `MILLI_USD_MILLION` — an int64 count of 10⁻³ USD million. A schema saying `decimal` has
declared **a number, not a currency, a scale or a unit**. Mapping it to money would make every
later comparison arithmetic on an assumption nobody recorded, and the coverage number would look
*better* for it. The refusal is named, counted, and carried into the declaration.

## The end-to-end run, and what it does NOT show

`make e2e` runs three regulators through three ingresses. All three arms pass:

| arm | ingress | result | wall clock |
|---|---|---|---:|
| IFSCA | `.xlsx` filing + pinned blank | `VALID`, settled **1,898 of 3,747** | 6.24s |
| EBA | `.xlsx` rule workbook | executed **10,453 of 12,925**, 31,904 data points | 1.38s |
| FinCEN | `.xsd` | **3,837** fields, 44 refused | 0.04s |

**No number above is comparable to another.** Three regulators declare different things.

Stated in the run's own output, because a demonstration that hides its edges is a demonstration
nobody can act on:

* **No filing was FILLED.** The fill lane (`A5`) is not built, so *"autonomously populates the
  regulator's prescribed filing template"* is demonstrated by **no arm here**.
* **Only IFSCA is checked end to end.** EBA executes against the publisher's declared scope, not a
  filed instance. FinCEN produces a surface and stops — there is no FinCEN filing to bind.
* **No arm crosses regulators.** Nothing fuses a custodian feed with a trial balance.
* **A harness defect, found and fixed here:** the IFSCA summary printed *"filing is correct."* — a
  fragment of the CLI's own disclaimer, *"It does not state that the filing is correct"*, caught by
  a prefix filter and wrapped onto its own line. The summary asserted the exact opposite of the one
  thing this product is careful never to say. Matched on whole lines now.

## What was NOT acquired, and why the dataset list is short of four

`D1` targeted four regulators. Two are absent and it is a fetch problem, not a design one:

* **SEC Form ADV** — `sec.gov` served an HTML shell to every request; the IAPD compilation feed
  returned `AccessDenied`. The blank form and the live filings both need a session this run did
  not have.
* **ESMA AIFMD Annex IV** — the technical reporting package URL 404s; the XSDs have moved.

`17 CFR § 275` **was** acquired, as part of `N6`'s eleven corpora, and is in
`research/corpus-independence/`. So the SEC's *rules* are pinned and its *template* is not.
