# docs/BUILD-B.md — the build plan to a demonstrable product. Four phases.

*Written 20 Aug 2026 at `266c855`. Supersedes nothing; `docs/PLAN.md` stays the plan of record and
this is the near-term build sequence inside it.*

Four phases, deliberately few. **Every phase ends with a command anybody can run and a result they
can check** — not a status update. A phase is not done because the code exists; it is done because
its check passes and its number is in `docs/AUDIT-TRAIL.md`.

The target is one sentence, and the plan is organised so each phase makes one more clause of it
true:

> Upload raw, scattered operational exports with zero manual formatting. The platform ingests,
> resolves and fuses them into a unified knowledge graph, maps them against statutory rules,
> populates the regulator's prescribed template, runs deterministic checks over the completed
> return, and delivers an audit-ready filing with a cryptographically signed coverage certificate
> in seconds.

---

## Where the sentence stands entering B1

| clause | state at `266c855` |
|---|---|
| upload multi-format, zero formatting | xlsx · XSD · CSV **built**; PDF **absent** |
| fuse into a unified knowledge graph | graph builds 1,667 nodes; **no Entity/Record node kind** |
| map against statutory rules | Path M **10,453 of 12,925**; Path Q blocked on 50 labelled spans |
| populate the template | values proposed with spans; **nothing writes the workbook** |
| deterministic **gate-qualified** checks | checks run; **0 predicates admitted under G4** |
| signed certificate, in seconds | **built** — Ed25519, 0.35 s fill, 6.24 s check |

---

## B1 — THE RETURN GETS FILLED, AND YOU CAN OPEN IT

**Why first.** `A5` proposes values and nothing puts them in a cell, so the most visible clause —
*populates the regulator's prescribed template* — is demonstrated by a JSON file. This is the
smallest change with the largest visible effect.

**Build**

* A cell writer over **raw-zip surgery**, reusing the mechanism `injectors/surgery.py` already uses.
  `ci/no-openpyxl-writer.sh` exists because an openpyxl round-trip of the FME workbook **drops 24
  parts and all 19 `x14` validations and shrinks 3.66 MB to 66 kB** — a "filled" template written
  that way is a different document that shares a name. The writer edits cell values inside the
  existing zip and touches nothing else.
* `cdfc fill <template> --source <artefact> --out <path>` writing evidenced and derived fills.
* The gate registry row and a negative control that flips: a writer that loses a part must go RED.

**FUNCTIONALITY CHECK**

```bash
make demo-fill
```

Passes when, over the FME return:

1. the output opens in Excel and in `openpyxl` without a repair prompt;
2. `zipfile.namelist()` of input and output are **identical sets** — no part gained or lost;
3. all **19 `x14` data validations** survive, counted before and after;
4. every cell the declaration marked `admitted` holds exactly that value, and every `derived` cell
   holds its value and is listed as derived in the accompanying declaration;
5. **no cell the declaration did not name has changed**, asserted by diffing every cell.

**Then demonstrable:** upload → a filled return you can open, with a coverage declaration beside it.

---

## B2 — THE BINDER, AND THE GRAPH GETS ENTITIES

**Why second.** B1 makes filling visible and then shows one field filled, which looks worse than
the system is. The bottleneck is the **binder**, not the fill lane: `A1c` use 2 is measured and is
not the one wired into the prose path.

**Build**

* Wire `cdfc.correspond.schema.match` into `cdfc.fill.pipeline` as the primary binder, with the
  label-overlap binder demoted to a declared fallback.
* An `Entity` node kind in `cdfc.evidence.graph`, fed from `cdfc.correspond.link` (deterministic,
  Fellegi-Sunter) **and** from GraphRAG entities into the `Derived` lane — `D3` measured 29
  entities and 45 relationships from 6,000 characters, carrying `text_unit_ids` rather than spans,
  which is exactly what `Derived.supported_by` holds.
* Cross-document fusion: two source artefacts in one run, entities resolved across both.

**FUNCTIONALITY CHECK**

```bash
make demo-fuse
```

Passes when:

1. two source artefacts (custodian feed + trial balance) are bound in **one** run;
2. `cdfc evidence` reports a non-zero `Entity` count, and each entity names the artefact digests it
   was resolved from;
3. an entity appearing in **both** sources resolves to **one** node, asserted by name;
4. fills rise from **1** to a recorded number, and the declaration still closes across four lanes;
5. every evidenced fill still re-verifies byte-exact — the binder got better and the trigger did
   not move.

**Then demonstrable:** *fuses these multi-format files into a unified knowledge graph* — with the
word "unified" meaning something checkable.

---

## B3 — PDF IN

**Why third.** *"PDF valuation packs"* is named in the claim and nothing reads one. It is last of
the ingest work because it is the only piece needing a new build-time dependency.

**Build**

* A docling ingress: PDF → `InstrumentText` with spans, corroborated by a second reader on the same
  discipline as `tools/pdf_arms.py`. Docling stays **build-time**; the runtime closure is unchanged
  and `tests/negative/importgraph.py` still proves it.
* `cdfc.model.extract` over the resulting text, which needs no change — it takes an
  `InstrumentText`.

**FUNCTIONALITY CHECK**

```bash
make demo-pdf
```

Passes when:

1. a real PDF valuation pack becomes an addressable text with two-party corroboration and a
   published DISPUTED count;
2. at least one value extracted from it **re-verifies byte-exact** at a span computed by us;
3. the runtime closure test still passes — docling appears in **no** verdict path;
4. a value in a disputed region is **refused**, with its reason, and the refusal is counted.

**Then demonstrable:** all four named source types — custodian feeds, trial balances, cap tables,
PDF valuation packs.

---

## B4 — THE WHOLE THING OVER HTTP, AND IT VERIFIES

**Why last.** It is the least uncertain and the most mechanical, and it is what turns a demo into a
product somebody else can run.

**Build**

* A run **manifest** naming the artefact digests it used, so `cdfc verify` re-derives from stored
  artefacts rather than from files on the operator's disk. The registry exists and
  `POST /v1/filings` stores uploads; **no run yet records its digests**, which is the open item.
* The drop screen wired to the registry, showing prior uploads and letting a run name them.
* PROV-O and SHACL exported beside every run, as the audit bundle.

**FUNCTIONALITY CHECK**

```bash
make demo-e2e
```

Passes when, in one scripted session:

1. three files are uploaded on three separate calls, days apart in the story, and stored once each
   — a re-upload of identical bytes creates **no** second artefact;
2. a run names all three, and its Merkle root is **unchanged** by an unrelated later upload;
3. `cdfc verify` re-derives the declaration **byte-for-byte** from the stored artefacts alone;
4. the signed certificate verifies, and its signature covers the artefact digests;
5. wall clock from last upload to signed certificate is **reported**, whatever it is.

**Then demonstrable:** the whole sentence, end to end, over HTTP, reproducible by a third party.

---

## THE CLAUSE NO PHASE ABOVE FIXES

**"gate-qualified" will still be false, and building faster will not change it.**

`G4` admits no predicate. Every candidate is refused at `G2` — **315 for producing no kill, 33 for
no margin over the free baselines** — and `G4` needs `n >= 189` from a clean corpus that is not
funded. That is not a gate being strict: **no predicate has ever beaten a coin-flip, a constant or
a copy of last quarter.**

Two honest options, and they are the only two:

* **Change the word.** *Deterministic* is true, provable today, and is most of what a buyer hears
  in *gate-qualified*.
* **Fund the corpus**, run `G4`, and earn it. `docs/OPEN-ITEMS.md` carries the requirement.

Anything else is publishing a quality claim over predicates that never passed a quality gate, which
is the one failure this whole system is built to make impossible.

## AND THE WORD ABOVE IT

**"Autonomously"** is also not earned and is not on the roadmap to be. **8 of 443** labelled FME
fields are `ATTESTATION` — *"The Net worth requirement has been complied with…"* — and a
certification is a natural person accepting liability. `A5` assembles the evidence for those and
stops. `CLAUDE.md §5` records that the product claim deliberately omits *autonomously* and *zero*;
the pitch put one back.

*proposes and populates, with a named human signing the attestations* is true, and is a better
sentence than the one it replaces.

## What this plan does NOT contain

* **No fill-accuracy number**, in any phase. That needs the 30 filing-plus-source-pack pairs, which
  is a data blocker rather than a build one. Every phase above reports what was filled and what was
  refused; **none reports how often a filled value is right.**
* **No Path Q.** Prose-to-check needs 50 labelled proviso spans and `g0_scope.py` raises without
  them. `N6` also measured the division recovery at rank-1 on **3 of 11** corpora, so the
  segmentation under it is not ready either.
* **No GraphRAG extraction-quality measurement.** `D3` produced 29 entities and nobody checked
  whether they are right.
