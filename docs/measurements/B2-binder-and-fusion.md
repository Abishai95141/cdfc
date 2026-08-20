# B2 — the binder, and two documents in one run

*Built and measured 20 Aug 2026. `make demo-fuse` reproduces it. Controls in
`tests/contract/test_fill_pipeline.py` (15) and `test_a5_fill.py` (15).*

---

## The result

    2 documents · 10 columns offered · MATCHED 10 of 10 · refused 0
    evidenced 4 · derived 6 · FILLED 10        (B1 achieved 1)
    4 proposed + 3729 refused + 8 attestations + 6 derived = 3747 over 3747
    parts 42 -> 42 · x14 19 -> 19 · cells changed 10 named 10 · 0.35 s

**1 → 10.** Every value re-verifies byte-exact **in its own document**, and both sources
contribute.

## FIRST, A DIAGNOSIS THAT SAVED A FAKE NUMBER

B1 filled one cell against a source pack of `Net worth`, `Number of investors`, `AUM`. Before
touching the binder, the question was *why*. Two causes, and only one is a defect:

**1. Stopword pollution — a real defect that generalises.** The tokeniser was `[a-z0-9]+` with no
stopword handling, and over the FME return's 132 labelled fields **`of` occurs in 73 and `the` in
45**. `header_token_overlap` is a BINARY evidence bit, so a match on `of` was indistinguishable
from a match on `investors`, and it fired on more than half the surface. Fixed by a short, closed
`STOPWORDS` set — short on purpose, because a longer list starts removing words that ARE evidence
in a regulatory label (`fee`, `date`, `name`).

**2. THE TARGET FIELDS DO NOT EXIST, and this is not a binder problem at all.** Across all 132
labelled fields: `net worth` → **1** hit, an attestation. `investor` → **2**, both attestations.
`aum` → **0**. `asset` → **0**. The FME return asks *whether the net worth requirement has been
complied with*, not what the net worth is — the `F6` finding, met head-on.

**So a better binder could not have raised B1's number on that source pack**, and reporting a lift
from it would have been a lift from changing the input. The demo source is now two documents whose
columns the return actually asks for, and `tools/demo_fuse.py` says so in a comment rather than
quietly.

## THE MULTI-SOURCE DEFECT, WHICH IS THE REAL FINDING

`A5` took **one** `InstrumentText` and re-read every span in it. With a custodian feed and an
officers register bound in one run, **every observation from the second document failed
`REVERIFIES`** — not because the span was wrong, but because it was re-read in the wrong file.
Five correctly-bound fields were refused as unverifiable evidence.

**And the failure mode is worse than losing them.** A span from document A re-read in document B
could match *by coincidence*, and would then PASS. **Re-verifying against the wrong document is not
a weaker check; it is a check of something else.** Fixed: `propose` takes a document→text mapping,
each observation re-verifies against its own, and one naming a document the run never read is
refused with that reason rather than re-verified somewhere else.

**The controls did not catch it, and could not have.** `test_a5_fill.py` built sources called `"t"`
and observations labelled `"src.pdf"` — a mismatch that never mattered because the document was
ignored. Four tests broke the moment identity was checked, which is the fixtures being wrong rather
than the code.

## THE UNDECLARED CEILING, AND WHY IT MOVED

`TYPE_ADMITS` refuses a field whose type the template never declared — and that is **92 of 124**
FACT-shaped labelled fields on this return. Refusing them capped the entire product at **32**
fillable cells **because the workbook is sloppy**, a cost borne by the filer for somebody else's
omission.

Those now land in `Derived`: placed in the return, and **never counted as checked**. Every other
condition still had to hold — grounded, re-verified byte-exact, sources agreeing, not an
attestation. What is missing is the template's own type declaration, and the lane says so.

Two bugs in that branch, both found by running it:

* `_evaluate` returned `chosen=None` on a `TYPE_ADMITS` failure, discarding a perfectly good
  observation because of a fact about the workbook — and making the derived route unreachable,
  since it needs a chosen observation.
* the guard required `all(c.holds for c in conds if c.name != "TYPE_ADMITS")`, which is **never
  true**: conditions after the failure are recorded as `not reached` with `holds=False`. The guard
  excluded every case it existed to admit. `first` being `TYPE_ADMITS` already proves everything
  before it held.

## What B2 does NOT deliver, against its own plan

`docs/BUILD-B.md` scoped B2 as *"the binder, AND the graph gets entities"*. **The binder half is
done; the Entity half is not.**

* **No `Entity` node kind exists**, and no entity appearing in both sources resolves to one node.
  What this fuses is **FIELDS from two documents into one return** — real, and not the same thing
  as entity resolution. `cdfc.correspond.link` (Fellegi-Sunter, measured in `N4`) is the component
  that would feed it and is not wired to the graph.
* **GraphRAG's 29 entities are not ingested** into the `Derived` lane either.
* `make demo-fuse` states both absences in its own output rather than passing quietly.

## And what nothing here establishes

**No filled value is claimed correct.** 10 cells hold what two documents said and what a span
re-reads; whether `AABCF1234K` is the right PAN is unmeasured and needs the 30 source-pack pairs.
6 of the 10 are `derived` — placed, not checked — and the return says which.
