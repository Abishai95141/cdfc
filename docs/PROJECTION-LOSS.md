# `docs/PROJECTION-LOSS.md` — what each projection cannot say, as a count

**Any party reading only a projection sees a smaller, cleaner report than the truth.** That is not
a defect to be minimised; it is a property of projecting an eight-state coverage declaration into a
form that was designed for something else. What matters is that the loss is **declared inside the
file**, so a reader who never saw the attestation still knows they are holding a projection of one.

## The measured loss

| | OSCAL Assessment Results | RO-Crate |
|---|---:|---:|
| item states representable **as findings** | **2 of 8** | — |
| item states representable **at all** | **8 of 8** (2 findings, 5 observations, 1 exclusion-only) | 8 of 8 |
| run states representable | **1 of 2** — `VALID` only | **2 of 2** |
| carries the normative artifact's URI | yes, `metadata.props` | yes, `isBasedOn` |
| self-contained | n/a | **required** — a missing blob raises |

**Two of eight.** `PASS → satisfied` and `FAIL → not-satisfied` are the only states that become
findings, because OSCAL's `finding-target.status.state` is a **closed two-value enum** and has no
member meaning *we did not look*. Everything else becomes an observation carrying our reason as a
prop, plus an `exclude-controls[]` entry — never a finding, because mapping `NOT_RUN` onto either
member would be inventing a verdict.

## The `INVALID` asymmetry, and why the two projections differ

**`project_oscal` RAISES `NotRepresentable` on an `INVALID` run. `project_rocrate` does not.**

That is deliberate and it is not an inconsistency:

- An **OSCAL Assessment Result** is an assurance document. One with zero findings is schema-valid
  and means nothing in particular — so emitting one for a run in which we could not demonstrate our
  instrument was working publishes a document that reads, to anyone who does not know the mapping,
  as *checked and nothing found*. **That is the most dangerous possible direction to be wrong in**,
  and the refusal has no flag: a flag is what somebody sets when a pipeline is failing and the
  deadline is Friday.
- An **RO-Crate** is a container for evidence. Evidence that the instrument could not be
  demonstrated is still evidence, and a crate carrying an `INVALID` run says so in its `runState`.

The OSCAL refusal is about a form whose vocabulary cannot express *we did not look*. It is not
about `INVALID` being unmentionable.

## What a reader of a projection alone is missing

Everything in this list is in the attestation and in neither projection's *findings*:

- **the liveness proof** — whether every check demonstrated itself on this filing;
- **the residue**, and the rejector set it was computed against;
- **the four required statements** — bounded silence, purpose, the summary caveat, the detection
  boundary;
- **the open items with their ages**;
- **the settled fraction's two denominator terms**, without which the fraction is a number with no
  scale.

The OSCAL document carries the first four as `props` and `description` text, which a consumer's
tooling is free to ignore; the findings are what such tooling reads. That is the loss, stated as
the thing it is.

## Determinism

Both projections join `report.html`, `attestation.json` and `run.jsonl` in `make determinism`'s
comparison set. **A lossy projection that is also non-deterministic is a second artifact a consumer
could diff and mis-read**, so every identifier in them is derived from content — a UUIDv5-shaped
digest over the parts — and nothing is generated. `test_oscal__identifiers_are_derived_and_not_generated`
walks both modules' ASTs and asserts no generator and no clock is called.
