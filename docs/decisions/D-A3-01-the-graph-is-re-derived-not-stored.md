# D-A3-01 — what persists is the ARTIFACT SET; the graph is re-derived, never stored

*Decided 20 Aug 2026. Experiment `N5` in `docs/PLAN.md §11`. Gates `A1c` and `A3`.*

## The question, and why it looked like a hard one

`ARCHITECTURE §4` chose the evidence graph as **a projection of the run, not the substrate of it**
— emitted, Merkle-rooted, never stored — on a critique's argument that a graph-native rewrite is
*"the most expensive way to change nothing a buyer can see."*

The user flow in `PLAN.md §2` appears to need the opposite: upload a rules corpus today, upload
financial exports next week, ask for a filing the week after. That is a graph surviving across
uploads and answering a later question, and it was recorded as *"the biggest open architectural
question on the table."*

## The measurement that dissolves it

**Re-deriving the whole graph from the pinned artefacts is free at the scale this product operates
at.** MEASURED on this machine, over the real IFSCA instrument (1,218 units) and the real FME
return:

    cold re-derivation, whole graph        0.41 s      1,722 nodes · 11 edges
    RDF projection over it                 0.00 s      5,669 triples
      provisions layer                     0.03 s
      fields layer (raw zip + validations)  0.07 s

    nine pinned blanks + the instrument    0.63 s      3,550 nodes

**And the projection is a deterministic fold, not merely a fast one.** The sorted triple set
digests identically under `PYTHONHASHSEED` 0, 1 and 2:

    seed 0 / 1 / 2   bdcb23f16a2dcd360f0c   1,722 nodes · 11 edges   (identical)

**With the control that makes that mean something** — a digest that cannot move proves nothing:

    FME  + 11 proposals   bdcb23f16a2dcd360f0c
    ALR  + 11 proposals   f2f15633452dbda6e291   DIFFERS
    FME  + 12 proposals   000f7d2f106b9e0a75d0   DIFFERS

So `project(artefacts) -> Graph` is a **total, deterministic function of its inputs**, and computing
it costs under a second.

## The decision

**PERSIST THE ARTEFACT SET. RE-DERIVE THE GRAPH.** Every upload pins an artefact — a rules corpus,
a template, a source document — and a run names which artefacts it used. The graph is rebuilt from
that set on every query.

The user flow is satisfied in full: rules uploaded today and financials uploaded next week are two
pinned artefacts, and the filing run the week after names both. **What survives across uploads is
the evidence, not a derived index of it.**

## Why a mutable store is not merely unnecessary but unsafe here

`run_id_for` is *"a digest of the inputs, not a timestamp. Two identical runs share an id, which is
the point."* A graph that ACCUMULATES is state that is not in that digest. The consequences are not
stylistic:

* two runs over an identical filing, template and registry would return different coverage while
  sharing one run id, and `store.write()` overwrites in place — the second silently replaces the
  first, and an attestation over either verifies;
* `cdfc verify` re-derives the payload from the manifest's pins and compares byte for byte. It
  cannot re-derive a graph whose contents depend on what else had been uploaded by then;
* the same defect shape has already been caught in this repository when `run_filing` learned to
  take a template, and the fix was to widen the digest — which is possible for a template sha and
  impossible for accumulated state.

**A read index remains permitted and is unchanged from `ARCHITECTURE §4`:** SQLite may be a REBUILT
index carrying the Merkle root in a `meta` table so a stale one is detectable, and it is never an
input to a verdict. Nothing in this decision requires one — 0.63 s does not need an index — and one
built before it is needed would be a cache nobody can prove correct.

## Cognee, and every other document-graph builder — REJECTED for this path

`PLAN.md §7` lists Cognee as the candidate worth a real evaluation. It is not evaluated further,
and the reason is structural rather than a benchmark:

1. **Its value is automated ontology generation and LLM-extracted edges.** The rule over every
   graph builder in this design is that **no LLM-extracted edge enters the graph unadjudicated**.
   An adopted builder would have to have its every edge re-adjudicated by our gates, at which point
   it has contributed the one thing we cannot use and none of the thing we need.
2. **It would put a model in the closure of code that answers a coverage question.**
   `BANNED_IN_VERDICT` plus `ci/barrier5.sh` exist to make that impossible.
3. **The problem it solves — building a graph cheaply — is measured at 0.63 s.**

It may still earn a place on the **propose** side, where `networkx` is already permitted. That is a
different question and it is not this one.

## What this decides for the phases

* **`A3` is a projection layer, not a store.** Its shape is settled: `Observation` and `Derivation`
  nodes are folded from pinned source artefacts exactly as `Provision` and `Field` nodes already
  are, and the ingress pins documents rather than mutating a graph.
* **`A1c` is unblocked.** Correspondence operates over a re-derived graph and needs no persistence
  layer beneath it.
* **The build task this creates is an ARTEFACT REGISTRY**, not a graph database: content-addressed
  storage for uploads, with a run naming the artefact digests it used. That is the same shape as
  the existing pinned corpus, extended to user uploads.

## What this decision does NOT establish

**It does not establish that re-derivation stays cheap at every scale.** The measurement covers
1,218 provisions, nine blanks and 3,550 nodes. A corpus of thousands of source PDFs is a different
population, and the number that would decide it — the cost of folding a large `Observation` set —
cannot be measured before `A3` exists. **The re-measurement is a named `A3` entry criterion rather
than an assumption**: if a fold exceeds a few seconds, the rebuilt read index above is the
prepared answer, and it changes performance without changing the reproducibility model.
