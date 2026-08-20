# D-A3-02 — GraphRAG: rejected as a graph builder, admissible ONLY as a proposer

*Assessed 20 Aug 2026 against `github.com/microsoft/graphrag` and its indexing documentation.
Extends `D-A3-01`'s ruling on document-graph builders to a named, specific candidate.*

---

## What it is

An LLM-driven pipeline that extracts **entities, relationships and claims** from unstructured text,
runs **Leiden community detection**, generates **community summaries and reports at multiple
levels**, embeds into a vector store, and writes Parquet. MIT licensed.

Two facts read directly off the repository and the docs, both load-bearing here:

* the README carries a note that the project is **"largely in maintenance mode"**;
* indexing is prompt-driven — *"extract meaningful, structured data from unstructured text using
  the power of LLMs"* — so a corpus costs many thousands of model calls to index.

## The ruling, and it is the same one Cognee got, for the same reason

**REJECTED as a graph builder. It is a `LAYER 2` candidate — a PROPOSER — and nothing else.**

`D-A3-01` set the rule before this candidate existed: *"no LLM-extracted edge enters the graph
unadjudicated."* Every GraphRAG edge is LLM-extracted, so every edge would have to be re-adjudicated
by `G-QUOTE`, `G-FIELD`, `G-TYPE`, `G-VOCAB` and `G-XREF` — at which point, in that decision's
words, *"it has contributed the one thing we cannot use and none of the thing we need."*

## The mismatch that is specific to this product, and it is not about performance

**A community report cannot re-verify byte-exact, because it is generated rather than quoted.**

That is the whole of it. This system's admission trigger is mechanical: *is there a grounded
observation that re-reads the exact bytes at the span it cites?* `W0-C` is why — a similarity
locator returned `SUPPORTED` **20 of 20** on evidence that had been DELETED. GraphRAG's most
valuable output, the multi-level community summary, is by construction a synthesis over many text
units; it has no span, and there is no span it could have. `A5` would refuse every one of them at
`REVERIFIES`, correctly, and the refusal would be the system working.

Its **claims/covariates** extraction, which carries text-unit references, is the part closest to our
`Observation`. That is the part worth looking at, and it is not the part GraphRAG is famous for.

## What it would genuinely buy, and it is a real gap

**Cross-document entity resolution.** Our graph has three node kinds — `Provision`, `Field`, `Rule`
— and no `Entity` or `Record`. Nothing fuses a custodian feed with a cap table, and *"fuses these
multi-format files into a unified knowledge graph"* is unsupported today. GraphRAG does that stage.

But we already have a **measured, deterministic, model-free** answer to the same question:
`cdfc.correspond.link` — Fellegi-Sunter with `m`/`u`/prevalence fitted by EM on no labelled pairs,
scored against Splink 4.0.16 in `N4`. Replacing a measured deterministic component with an
unmeasured LLM one, to do a job the deterministic one already does, is the trade this repository
refuses in both directions.

## The narrow door that stays open

`D-A3-01` left it explicitly: *"It may still earn a place on the propose side, where `networkx` is
already permitted."* Concretely, GraphRAG could sit behind `src/cdfc/model/propose.py`, emitting
candidate rule-to-field bindings **as data**, for our gates to admit or refuse.

**That is `E6`'s question and it is not answerable yet.** `experiments/E6/DECISION.md` reads
`status: PENDING — the run has not been taken`; `propose.py` does not exist and `ci/barrier5.sh`
enforces its absence; `cdfc.model` is in `BANNED_IN_VERDICT` as a package. Any adoption discussion
that skips E6 is a discussion about putting a model in the closure of code that answers a coverage
question.

**And maintenance mode is a real input to that.** A proposer is a dependency of the one layer we
plan to let make mistakes; depending on a project whose own README says development has moved on,
for a component that costs thousands of model calls per corpus, is a poor trade against writing the
proposer against a model API directly — which is what `E6` was scoped to test anyway.

## What this does NOT establish

* **Nothing here was measured.** This is an architectural reading of the repository and its
  documentation, not a benchmark. No GraphRAG index was built and no extraction quality was
  observed — if it were adopted on the propose side, `E6`'s protocol is what would have to run.
* **The "maintenance mode" note is read from the README**, not from commit activity.
* **It says nothing about GraphRAG's quality at its own job**, which is global sensemaking over a
  prose corpus — a different job from admitting a value into a regulatory return with a span behind
  it.
