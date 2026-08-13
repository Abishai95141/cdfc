# D-P8-01 — there is no blind-fill corpus, and `BLOCKING` is `0` by construction

**Decided 13 Aug 2026, at P8-B1.**

## The finding

P8-B1 is **15–25 person-days of a different person** — somebody who has never seen the predicate
set, filling ≥ 30 copies of the FME blank correctly from the regulation alone. `plan/04` E8.1 says
it plainly: *"the longest pole in this plan is not the code. It is the corpus."*

**No such person exists on this project, and no such corpus exists.** This is the blocker already
recorded in memory as the human dependency, and P8 does not resolve it.

## What was built instead, and what it is worth

A **`TEMPLATE-COMPUTED` corpus with `derived_by = FOREIGN_ENGINE`**: 40 filings whose INPUT cells
this repository chose from a declared distribution and whose DERIVED cells were computed by a
pinned offline engine running in a subprocess and sharing **no module** with `src/cdfc/`.

That is genuinely informative and it closed F2: an arithmetic predicate checked against it is not
re-checking our answer against our answer, and `g4_ffr.independent()` proves that by AST rather
than by assertion. **It produced the first false-failure rate this system has measured, and that
rate immediately found a real defect** (`P-0009`, the wildcard `COUNTIF`).

**What it is NOT.** The inputs are ours. It answers *does our arithmetic agree with an independent
engine's*; it does not answer *does a real filer's return trip these checks*. Only a person can
answer the second.

## The consequence, enforced rather than noted

`BLOCKING` requires `n_non_synthetic >= 30` — thirty filings a PERSON or THE WORLD produced. This
corpus has **`0`**. So:

* **the `BLOCKING` count is `0` by construction**, and `docs/measurements/P8-ffr.md` prints the
  reason beside the zero rather than leaving it as an absence;
* **G-CORPUS resolves to `RESTRICTED`**, the middle branch — `n >= 30` but `n_non_synthetic < 30` —
  and that literal string renders on every FFR-bearing surface. *Leaving that branch unnamed is
  what made shipping it look like a pass.*

## What is committed against the day a Person A exists

`corpus/blind-fill/FILL-BRIEF.md` and `corpus/blind-fill/SLICES.md` are **written and hashed NOW**,
before any workbook is filled, because rule 3 of the firewall is that the brief's commit must be an
**ancestor** of the first workbook's. A commitment made after seeing the result is not a
commitment, and here the git history is the evidence. `fixtures/corpus_manifest.json` carries the
seven keys with the blind-fill ones `null` and the reason in `person_a_kind`.

## The alternative it beat

*Filling thirty workbooks ourselves and labelling the corpus `BLIND-FILLED`.* Rejected outright —
that is `SELF-AUTHORED` with a different word on it, its expected FFR is zero regardless of
predicate quality, and the whole of P8 exists to refuse exactly that number.

*Using the model-instance fallback (firewall rule 5).* Available and pre-decided, and it would
carry `person_a_kind: "model-instance"` wherever the rate renders. **It needs a second instance
that has provably never seen the predicate set, and this repository has no way to establish that** —
the same problem NC-N03 records: blindness is a property of a history, not of an artifact.

Related: `docs/measurements/P8-ffr.md` · `corpus/blind-fill/FILL-BRIEF.md` ·
`docs/decisions/D-P8-02-no-register-derived.md`
