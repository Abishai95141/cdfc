# The evidence layer — `src/cdfc/evidence/`

Built 19 Aug 2026. **The first part of the semantic half that is in the product rather than in a
spike.** It takes a pinned rules corpus, a filing template and a model's proposed `rule -> field`
bindings, adjudicates the bindings deterministically, builds a graph from the survivors, and
declares coverage over a denominator that is not arguable.

    cdfc evidence --template <blank.xlsx> --proposals <proposals.json> [--only-with shall]

Exits non-zero when any proposal was refused, because a run whose refusals nobody read is a run
whose refusals nobody read.

---

## What it does, layer by layer

| module | decides | what it may NOT do |
|---|---|---|
| `provisions.py` | corpus → `Provision` with an eId and an exact span | invent an address |
| `fields.py` | template → `Field` with a type the WORKBOOK declares | guess a type or a label |
| `workbook.py` | cell text and number formats, off the raw zip | use openpyxl (see below) |
| `proposal.py` | loads a model's bindings as untrusted DATA | decide anything |
| `gates.py` | five gates admit or refuse, with a closed reason | be persuaded |
| `graph.py` | nodes and edges, from admitted proposals ONLY | contain a refused claim |
| `query.py` | coverage, every count with its denominator | render a bare fraction |

**The model is not in this package and there is no client to import.** A model writes a JSON file;
`proposal.load` reads it. That is the whole seam, and it is what lets the import-closure test
prove no model reaches a verdict.

## Measured, on the real IFSCA instrument and the real FME return

    provisions 1218   labelled fields 132 of 3747   (rule: adjacent_left, placeholders excluded)
    proposals 11   ADMITTED 6   REFUSED 5
    planted errors caught      5 of 5
    genuine proposals refused  0 of 6
    graph 1722 nodes {Field 498, Provision 1218, Rule 6} · 11 edges · 5669 RDF triples
    fields governed 5 of 498      provisions cited 6 of 1218
    durably addressable          0 of 1218

Five proposals are wrong ON PURPOSE, one per gate, and each is refused **by its own gate** — the
test asserts the named gate fired, not merely that something did. Two gates are additionally
DEFEATED in the tests and their plant required to sail through, because a test that only ever
sees red cannot tell a working gate from a broken one.

**`0 of 6` genuine refusals is not a boast about the model.** Every quote and every field
reference was verified against the pinned artefacts *before* the fixture was written. The
previous run of this exercise, without that step, had 2 of 12 genuine proposals refused for citing
cells that do not exist.

## Three things this build got wrong first, and each is worth keeping

**1. openpyxl is lossy on this workbook, and a gate said so.** `pytest.ini` turns openpyxl
warnings into errors (NC-CI02). The warning here is *"Data Validation extension is not supported
and will be removed"* — and **19 of this workbook's 54 validations live in that `x14`
namespace**. Reading it with openpyxl finds zero inline vocabularies: a clean, empty, wrong
answer. The gate was telling the truth about the reader, so `workbook.py` reads the raw zip with
lxml and openpyxl is absent from the package. That recovered **219 ENUM fields** carrying the
workbook's own permitted values, which is what `G-VOCAB` adjudicates against.

**2. A numeric cell is not a label.** The first raw reader returned `<v>` text for every cell, so
every number to the left of a field looked like that field's label — and the labelled population
went from 498 to **2,169**. That is the same denominator-by-unwritten-convention defect `M-CEIL`
measured, reintroduced by a reader instead of by a rule. `Cell.is_text` now separates a string
from the decimal rendering of a number.

**3. The labelled population is a property of the RULE.** `LabelRule.ADJACENT_LEFT` is pinned and
named on every `FieldSet`. The looser `NEAREST_LEFT` yields 3,104 fields sharing **154 distinct
labels** — it labels rows, not fields, and must never be a denominator. Both are available; the
count says which produced it.

**Cross-validation worth stating:** these numbers were produced by a reader that shares no code
with `tools/measure/ceiling.py`, and they agreed with `M-CEIL` exactly — 498 labelled, 481 FACT,
17 ATTESTATION, and 3,104 / 154 under the loose rule.

> **AND AGREEING WAS NOT THE SAME AS BEING RIGHT.** `N2` then read the labels rather than counting
> them: **351 of the 498 are the literal `NA`**, this form's filler. Two independent readers agreed
> because they implemented the same rule, and the rule admitted placeholders. The population is
> **132**, the split **124 / 8**, and `docs/measurements/N2-labelling-rule.md` carries the
> derivation. Cross-validation checks that two readers agree; it does not check that what they
> agree on is a label.

## What is honest about the eId, and it limits everything above

`Provision.eid_kind` is `COORDINATE` for every node this build produces: `p0143.s0008` means page
143, sentence 8. **A rule stored against one moves if the instrument is re-extracted, if the
layout shifts, or if an amendment adds a page**, and the declaration says `durably addressable
0 of 1218` on its face rather than in a footnote.

`PROVISION` eIds (`reg_8__subreg_1`) need Docling's `ListItem.marker`, which needs a re-extraction
of the pinned instrument — a re-pinning event whose blast radius is experiment `N1`.
`provisions.from_markers` is the seam they land in, and it validates every span against the
instrument it claims to address.

## What is NOT built

Of the sixteen-step pipeline in `docs/PLAN.md §3`, this covers steps 1, 4, 5's seam, 6 and 12.
Still absent, and none of it is implied by the above:

* **step 2 · Path M** — published rules compiled from DPM-XL. `A2`, blocked on a filed instance.
* **step 3 · Docling ingress** for source documents.
* **step 7 / 14 · Datalog chaining** — conditional obligations. The formalism is adopted and
  written ourselves; nothing is built.
* **steps 9, 10 · correspondence and linkage** — `A1c`, and it gates fill.
* **steps 8, 15 · observations and derivation** — `A3`.
* **step 16 · writeback** — `A5`, gated commercially.

And the standing limit that no amount of building removes: **nothing here bounds RECALL.** It
measures the rules that were proposed, never the ones nobody proposed.
