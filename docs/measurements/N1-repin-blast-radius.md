# N1 — the re-pinning blast radius

*Run 20 Aug 2026 at `0732fdc` by `tools/measure/repin.py`. Gates `A4`.*

`docs/PLAN.md §8 F4`: re-extracting the pinned instrument with layout preservation recovers durable
`reg_8__subreg_1` eIds and removes most of the segmenter's cost — **but it changes the instrument's
bytes, and every offset, span and `text_hash` anchored to them moves.** This measures how much,
by perturbing a copy and running the shipped readers against it, not by reasoning about it.

---

## The result, and it separates two things that looked like one

| perturbation | units | characters | eIds resolve | quotes exact | admitted |
|---|---:|---:|---:|---:|---:|
| **BASELINE** (pinned) | 1,218 | 197,767 | 11 of 11 | 10 of 11 | 6 of 11 |
| **SHIFT** (+17 characters) | 1,218 | 197,784 | **11 of 11** | 10 of 11 | **6 of 11** |
| **RESEGMENT** (coarser units) | 174 | 197,767 | **0 of 11** | 0 of 11 | **0 of 11** |

*Negative control — a perturbation actually changed the corpus: **PASS**. Without it the table
would be three identical rows proving nothing.*

**Moving the bytes costs nothing. Moving the SEGMENTATION costs everything.**

The reason is in the addressing. An eId here is `p0143.s0008` — a page/sentence **key**, not an
offset. Shift the whole text and every span moves while every key survives, so all 11 proposals
still resolve and all 6 admissions stand. Change where the unit boundaries fall and the keys
themselves are different objects: **11 of 11 citations resolve to nothing, and every admission is
lost.**

**A layout-preserving re-extraction changes segmentation by construction** — producing
provision-level units in place of page-sentence ones is the entire point of it. So the honest
statement is: **a re-pin invalidates 100% of citations made against the current corpus.**

## What that costs TODAY, and it is the whole finding

Measured against the tree:

    unit offset pairs that would move        1,218  (all of them)
    disputed regions that would move            28  (all of them)
    proviso label spans that would move          0   labeller: null
    predicates citing a provision                0   probe A4-1 observes 0 statutory obligations
    published run ids digesting the instrument   0
    JSON artefacts naming the instrument         3   the text, its MANIFEST, and the empty labels

**The blast radius is near-zero because nothing has been built on the instrument yet.** The only
citations that break are the 11 proposals in `fixtures/evidence/fme-proposals.json`, authored two
days ago as a fixture.

### The recommendation, and it is time-sensitive

**RE-PIN BEFORE `A4`, NOT AFTER.** Every provision-citing artefact built between now and the
re-extraction is an artefact that must be re-authored afterwards. The three long poles all cite
provisions: the 50 labelled proviso spans, the first STATUTE obligations, and every rule Path Q
admits. Re-pinning after any of them lands converts a zero-cost migration into the two-digest
transition `ARCHITECTURE` Risk 3 describes — *"a window in which nothing reproduces against
anything published."*

**Today that window is zero-width. It widens with every citation.**

## A finding the first run produced by failing

The perturbed corpus was **refused by the loader** before it could be measured:

> *the stored digest is `7e4321e8bb9e750a…` but the stored fields hash to `203c41a3159238ba…`.
> Either the file was hand-edited or it was written by a different build. **Every span recorded
> against this instrument points somewhere else.***

`deserialise` recomputes a digest over the units, text and manifests and refuses a mismatch. **A
re-pin therefore cannot happen by accident** — it is only possible as a deliberate act that
recomputes the digest, which is what `_repin()` in the measurement now does. That refusal is part
of the answer rather than an obstacle to it: the failure mode of a silent, partial re-pin does not
exist.

## What this does NOT establish

* **It does not perform the re-extraction.** Docling is a build-time dependency and is not
  installed in the repo environment. The `RESEGMENT` arm is a *coarser* segmentation, chosen
  because it is measurable today; a real layout-preserving pass would produce a *finer, differently
  bounded* one. Both change the keys, which is the property that matters, but the number of
  resulting provisions is not predicted here.
* **It does not measure quote survival across a real re-extraction.** Under `RESEGMENT` the quotes
  fail because their provisions are gone, not because the text changed. Whether a verbatim quote
  survives a layout-preserving pass is a separate question and needs the pass.
* **11 proposals is a small population.** They are the only provision citations that exist, so the
  count is complete rather than sampled — but a complete count over 11 is still 11.
