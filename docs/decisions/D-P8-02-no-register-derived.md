# D-P8-02 — `REGISTER-DERIVED` is not built, and the 87-of-228 exhibit is unmeasured

**Decided 13 Aug 2026, at P8-B2.**

## What it would have been

`REGISTER-DERIVED` is the oracle whose warrant is stated narrowly and is therefore strong:
**every entity in the IFSCA register is validly registered, so a predicate asserting *membership*
cannot have a true positive there.** Its worked counter-example is the best artifact this project
has for showing a reviewer why the FFR column exists: the obvious format regex
`^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$` **fires on 87 of 228** live registration numbers, and the
admitted predicate is set membership under a declared normalisation instead.

## Why it is not built

The register is a live API. Two things stop it here, and neither is a preference:

1. **Its terms of use have not been read.** That is recorded as a standing constraint on this
   project: nothing polls that endpoint until somebody has read what the endpoint permits.
2. **A host function never resolves live** (NC-X01). What the product would use is a SNAPSHOT,
   content-addressed and pinned — and taking a snapshot is the same network call.

## What that costs, stated as the thing it removes

* The **`87 / 228`** exhibit is not a measurement in this repository. It is quoted from the
  specification, and `fixtures/baselines/register-regex-ffr.json` does not exist.
* **The membership/identity classes have no corpus-free oracle other than
  `TEMPLATE-COMPUTED`.** They are covered, because `derived_by=FOREIGN_ENGINE` licenses every
  class — but they are covered by ONE oracle rather than two, and a second independent oracle is
  exactly the thing that would make a membership FFR believable.
* **The positive control that stops the F2 repair from being reject-everything is weaker.**
  `plan/04` names `REGISTER-DERIVED` as that control; here it is carried by
  `test_template_computed_licenses_a_membership_ffr` instead, which is a check against our own
  generator rather than against the world.

## What it does not cost

Nothing in `g4_ffr`, `severity` or `provenance` is conditional on it. `CorpusProvenance` carries
`REGISTER-DERIVED` as one of its six values with `ADMISSIBLE` membership unchanged, so the day a
snapshot is pinned the oracle is a data file and a loader, not a redesign.

Related: `docs/decisions/D-P8-01-no-blind-fill-corpus.md` · `docs/measurements/P8-ffr.md`
