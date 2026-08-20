# D3 — GraphRAG and `cdfc.model.extract`, run head to head. **They do different jobs; take both.**

*Run 20 Aug 2026 on the same 6,000 characters of the pinned IFSCA instrument. GraphRAG 2.x via
`deepseek-v4-flash` (chat) + `gemini-embedding-001` (embeddings). Supersedes `D-A3-02`'s
"proposer at most" ruling, which was made on a reading rather than a run.*

---

## What each produced

| | GraphRAG (Option A) | `cdfc.model.extract` (Option B) |
|---|---|---|
| output | **29 entities · 45 relationships · 4 communities** | **3 claims** |
| shape | an ONTOLOGY — `ORGANIZATION`, `PERSON`, `GEO`, with generated descriptions | VALUES with the sentence each was read from |
| provenance | `text_unit_ids` — a chunk reference | `span=(127,135)`, and `reverify()` returns True |
| **span columns** | **NONE**, in entities or relationships | every observation |
| dependencies | 132 packages, 3 providers, 1 shim | zero new, 1 provider |
| wall clock | ~4 min for 6,000 chars | 2.8 s |

GraphRAG's entities are real and good: `FME → AUTHORITY` *"is regulated by"*, `APPLICANT → FME`
*"is the entity seeking registration"*. That is a map of **who is who and how they relate**, which
this system has never had.

`extract` produced `7,50,000`, `12,40,00,000`, `1,284` — each located, each re-reading byte-exact.
That is **what a filing needs to put in a cell**.

**Neither is a better version of the other.** One answers *what is this document about*; the other
answers *what number goes in this box, and where did it come from*.

## THE RULING IN `D-A3-02` IS AMENDED

That decision said GraphRAG was "a proposer at most, and only after E6", on the reasoning that
LLM-extracted edges cannot enter the graph unadjudicated and that community summaries cannot
re-verify. **The second half held and the first half was too narrow.**

* **Community reports never arrived.** The pipeline ran `create_community_reports` and then failed
  with `Pipeline error: 'community'`. The single output I had argued our gates would have to refuse
  is the one output GraphRAG did not manage to produce.
* **What it DID produce has a home**, and it did not before this week. `docs/AUDIT-TRAIL.md`
  20 Aug: the `Derived` lane admits a value no span supports, carrying `supported_by` unit keys
  instead. **GraphRAG's `text_unit_ids` are exactly that** — weaker than a span, and not nothing.

So the relaxation asked for on other grounds turns out to be the thing that makes GraphRAG usable
here. That was not foreseen and is recorded as luck rather than design.

## The decision: BOTH, into DIFFERENT LANES

    cdfc.model.extract  ->  Observation with a span  ->  A5 EVIDENCED lane  ->  counted as checked
    GraphRAG            ->  entity / relationship    ->  A5 DERIVED  lane   ->  placed, NOT checked

The coverage line already publishes both integers — `N evidenced + M derived` — so a reader can
tell a located figure from a synthesised one without reading the code.

## What Option A actually costs, measured rather than argued

Three providers and a workaround, and the workaround is the interesting part:

1. **DeepSeek serves no embedding model.** `graphrag index` validates the embedding model *before
   doing any work*, sent the DeepSeek key to OpenAI and got a 401. Anthropic has no embeddings
   endpoint either, so routing through a Claude subscription would not have helped.
2. **Gemini has embeddings** (`gemini-embedding-001`, 3,072 dims) and an OpenAI-compatible endpoint,
   **but omits `index` from the response envelope**, which GraphRAG's `LLMEmbeddingResponse`
   declares as `int` and refuses as `None`.
3. **A 25-line local shim** that copies the response through and adds `index` closed it. That is the
   whole fix, and the embeddings themselves were never the problem.

Plus: `graphrag init` is an **interactive wizard** that hangs indefinitely in automation and aborts
with stdin closed; it must be driven with piped answers.

**None of that is a reason not to use it.** It is a reason to keep it at arm's length — a
build-time producer of proposals, never a runtime dependency of a verdict.

## What this does NOT establish

* **No extraction QUALITY was measured.** 29 entities were produced; nobody checked whether they are
  right, and no planted-error campaign was run against them. `D-A3-02`'s point that every
  LLM-extracted edge needs adjudication is untouched.
* **One document, 6,000 characters.** Not a corpus.
* **The community-report failure is undiagnosed.** `Pipeline error: 'community'` may be a config
  problem on my side rather than a defect in GraphRAG, and it was not investigated.
* **Cost was not measured.** DeepSeek Flash is $0.14/M in, and no token count was recorded for
  this run.
