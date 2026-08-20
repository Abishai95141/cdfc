# D-A3-01a — AMENDMENT: re-derivation at scale, and the registry nobody built

*Decided 20 Aug 2026. Amends `D-A3-01`, which is NOT edited — it is a dated record and rewriting a
decision to match a later measurement is the failure `CLAUDE.md §1` names.*

---

## Why it was reopened

`D-A3-01` decided **persist the artefact set, re-derive the graph**, on a measured premise: the
whole fold costs `0.41 s`. It also named its own limit, in its own words:

> **It does not establish that re-derivation stays cheap at every scale.** … **The re-measurement
> is a named `A3` entry criterion rather than an assumption**: if a fold exceeds a few seconds, the
> rebuilt read index above is the prepared answer.

The product's user flow — *upload rules today, financial exports next week, ask for a filing the
week after* — is an accumulating corpus. This runs that re-measurement.

## The fold is not the scaling term. The PARSE is.

Graph assembly and the RDF projection are linear and negligible:

| artefact sets | nodes | build | triples | RDF projection |
|---:|---:|---:|---:|---:|
| 1 | 1,060 | 0.000 s | 3,220 | 0.000 s |
| 25 | 26,500 | 0.007 s | 80,500 | 0.008 s |
| 100 | 106,000 | 0.034 s | 322,000 | 0.034 s |
| 400 | 424,000 | 0.136 s | 1,288,000 | 0.137 s |

**No cliff.** 400× the original scale costs 0.136 s to assemble. Adjacency lookups run at 0.2 ms
each over 424,000 nodes.

**But re-derivation is `parse + fold`, and the original 0.41 s included the parse.** Measured:

    parse one pinned instrument (digest re-derivation + division recovery)   0.151 s
    parse one workbook into a field surface                                  0.155 s
    all TEN pinned instruments, cold                                         0.20  s

> **A CAVEAT ON MY OWN ARITHMETIC, and it cuts against the alarming reading.** Multiplying 0.15 s
> by an artefact count OVERSTATES the cost: nine of the ten pinned instruments are small workbooks
> and the tenth is a 1,218-unit statute, so ten of them cost **0.20 s**, not the 1.5 s a
> per-artefact average predicts. The projections below use the pessimistic per-artefact figure
> deliberately; the true curve for a mixed corpus sits under them.

| artefacts | upper-bound parse | verdict |
|---:|---:|---|
| 10 | 1.5 s | free |
| 100 | 15 s | **needs the rebuilt read index** |
| 1,000 | 153 s | re-derivation alone is not viable |

## The decision, amended

**`D-A3-01` STANDS. Persist the artefact set; re-derive the graph.** Nothing in this measurement
touches the reason it was decided, and that reason was never performance:

* a graph that ACCUMULATES is state outside `run_id_for`'s digest, so two runs over identical
  inputs would share an id and return different coverage, while `store.write()` overwrites in
  place;
* `cdfc verify` re-derives a payload from the manifest's pins and compares byte for byte, and it
  cannot re-derive a graph whose contents depend on what else had been uploaded by then.

Those hazards are properties of mutability, not of scale, and a faster machine does not retire one.

**What the measurement DOES change is the trigger for the read index.** `D-A3-01` left it as
*"nothing in this decision requires one — 0.63 s does not need an index"*. It now has a number:

> **Build the rebuilt read index when a single entity's artefact set passes ~50 documents**, which
> on the pessimistic curve is where re-derivation crosses a few seconds. It carries the Merkle root
> in a `meta` table so a stale one is detectable, and it is never an input to a verdict.

And the scale that matters is **per entity, not per deployment**. A filing run names one entity's
artefacts; 217 FMEs filing quarterly with five source documents each is ~20 artefacts per entity
per year, so the index becomes necessary in year two or three of a single entity's history, not on
day one.

## THE ACTUAL BLOCKER IS NOT THE GRAPH. IT IS THE REGISTRY NOBODY BUILT.

`D-A3-01` closed with a build task:

> **The build task this creates is an ARTEFACT REGISTRY**, not a graph database: content-addressed
> storage for uploads, with a run naming the artefact digests it used.

**It does not exist.** Measured against the tree:

* `src/cdfc/store/` is the **run** store — `run.jsonl`, `run.db` per run. It records what a run
  produced, not what a user uploaded.
* `POST /v1/filings` runs a filing and returns `"persisted": false`.
* No content-addressed upload store exists anywhere, and no run names an uploaded artefact digest.

So *"upload rules today, financials next week, ask for a filing the week after"* is unbuildable
today — and the reason is that **there is nowhere to put the first two uploads**, not that the
graph is a projection. The graph question was answered a month before the thing it depended on was
started, and re-opening it found the dependency missing rather than the answer wrong.

## What this makes next

1. **The artefact registry.** Content-addressed upload storage; a run names the digests it used;
   the manifest carries them so `cdfc verify` still re-derives. This is the same shape as the
   existing pinned corpus, extended to user uploads — and it is what unblocks the user flow.
2. **The read index, WHEN a per-entity set passes ~50 documents.** Not before: an index built
   ahead of need is a cache nobody can prove correct.

## What this does NOT establish

* **No accumulating corpus has been run.** The scale figures above are a synthetic replication of
  one artefact set, not 400 real documents; the parse curve is a per-artefact average projected
  forward, and the caveat above says which direction it errs in.
* **`Observation` folding is still unmeasured at scale**, which is the population `D-A3-01`
  singled out as the unknown. `A5` now produces observations, but no corpus large enough to
  stress the fold exists.
* **Cognee and the document-graph builders stay rejected**, for the structural reasons in
  `D-A3-01` §Cognee — none of which is a performance argument, so none is disturbed by this.
