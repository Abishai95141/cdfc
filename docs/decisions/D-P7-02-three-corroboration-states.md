# D-P7-02 — three corroboration states, not two

**Decided 13 Aug 2026, at P7-B0.**

## The plan's rule, and where it breaks on a real artifact

`plan/04-phases-qualification.md` P7-B0:

> compare sentence-wise. **A region on which the two extractions disagree is EXCLUDED from the
> addressable text and listed with its page number**

Two states are implied: *agreed* and *disputed*. On the pinned blanks there is a third, and it is
not rare — **38 of 1,729 units** across the nine workbooks.

`openpyxl` — the external party — has two blindnesses, both measured across all nine workbooks at
P1 and recorded in `src/cdfc/ingest/competence.py`:

* it is **namespace-blind to the `x14` data-validation extension** (19 units on FME alone);
* it returns an **`ArrayFormula` object rather than the formula text** for an array formula.

Neither is a disagreement. Nobody read those constructs twice.

## Why collapsing the third state is lossy in BOTH directions

**Into `AGREED`:** an uncorroborated reading becomes indistinguishable from a corroborated one.
The instrument would then report `1,729 / 1,729` agreement while 38 units had exactly one reader,
which is a denominator quietly absorbing its own exceptions — this project's subject matter,
committed inside the instrument that measures it.

**Into `DISPUTED`:** 38 constructs leave the addressable text **for a disagreement nobody
observed**, and every predicate harvested from them becomes unlocatable. On FME that is 19 data
validations. A gate would then reject them `g0.quote_in_disputed_region`, which is a false
statement about the artifact: the parties did not disagree, one of them never looked.

## The decision

Every unit carries one of `AGREED | SINGLE_PARTY | DISPUTED`.

* `SINGLE_PARTY` **is addressable** — one competent reading is a reading.
* `SINGLE_PARTY` is **never counted in an agreement rate**: `InstrumentText.agreement()` includes
  only units where more than one party was competent.
* A G0 outcome records the corroboration of the unit it located in, so a pass over an
  uncorroborated construct says so in `measured` rather than looking like a pass over a
  corroborated one.
* `counts()` publishes all four integers and the three states partition the total, asserted.

## The rule that keeps `SINGLE_PARTY` honest

The state is only safe if *"nobody looked"* cannot be confused with *"somebody looked and lost
it"*. So:

**Every absence must be covered by a named mechanism, or the build fails.** `textsource.build()`
refuses an extraction that produced nothing at a key another party read and declared no mechanism
for it (`Extraction.blind_to`), and `template_instrument.emit()` checks each declared blindness
against evidence on the artifact — an `x14` namespace on this repository's own record, or an
`ArrayFormula` object `openpyxl` itself returned. A party may not claim blindness at a key it did
read, and a blindness with an empty mechanism is refused at construction.

Without that rule a reader that silently dropped a construct would be labelled merely
uncorroborated, and the label would be doing the concealing.

## What this is modelled on

`src/cdfc/ingest/agreement.py`, which already refuses a single agreement figure because it would
average an external check with a same-author one, and `Competence.measured_on`, which already
refuses to widen an exclusion by judgement rather than by measurement. This decision is those two
rules applied to a new kind of artifact, not a new idea.

Related: `docs/measurements/P7-textsource.md` · `src/cdfc/qualify/textsource.py` ·
`docs/decisions/D-P7-01-no-statutory-instrument.md`
