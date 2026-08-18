<!-- Produced 18 Aug 2026. A gap analysis of this repository against the stated product vision:
     "A unified regulatory intelligence and filing platform that unites large-scale statutory
     semantic inference with a deterministic, gate-qualified graph engine to generate, verify and
     mathematically attest regulatory filings end-to-end."

     METHOD. Six dimensions, each read by one agent that was required to RUN the code rather than
     quote a docstring, then a second agent whose default position was that every claim was wrong
     and who re-ran the evidence itself. Claims that survived are marked; corrections from the
     refutation pass win. Six findings were additionally re-verified by hand -- they are the ones
     with run transcripts in the body.

     THIS DOCUMENT IS AN ASSESSMENT, NOT A RECORD OF WORK DONE. Nothing here has been fixed. -->

# cdfc — Vision Gap Analysis

## 1. THE ONE-PARAGRAPH ANSWER

Roughly one quarter of the vision exists, and it is not the quarter the vision leads with. What is real is the *deterministic, gate-qualified engine* half applied to **one** artifact class: an induction engine that derives checks from a spreadsheet's own formulas, dropdowns and protection mask (genuinely schema-free — it induced 10 predicates and caught 3 of 3 seeded defects on a synthetic UK-FCA workbook it had never seen, and 4 of 4 on a second unseen EIOPA workbook), an evaluator that lands every one of 3,747 fields in exactly one state with a closed reason vocabulary, five real gates, and a byte-identical attestation. What does not exist is everything the vision's first clause promises: **0 of 348** live predicates and **0 of 571** committed envelopes carry a statutory obligation; there is no endpoint, CLI command or code path that accepts a corpus of rules; the "graph" is one workbook's formula dependency graph (1,462 nodes / 4,115 edges) that is absent from the import closure of every production entry point; and the three verbs fare badly — GENERATE has no implementation at any surface, VERIFY works only on the CLI, and ATTEST signs a 4,020-byte summary of the *result* with a demo key published in the repo, verified against a public key carried inside the envelope under test. Worse than absence: the two controls a user would reach are inert. `POST /v1/filings` returns a hardcoded 422 for every file including the one the CLI checks successfully (`src/cdfc/api/handlers.py:91`), and `cdfc run --template X` parses the flag, *prints it back as the template used*, and discards it (`src/cdfc/cli.py:191-192`) — two different templates produce the identical run id `9e6c7cc491f4e0a8` and the identical `1557 / 3747`.

**The sentence a sceptical buyer would accept:** *cdfc is a command-line coverage declarer for one pinned Excel return — it induces 348 checks from that workbook's own structure, runs them over a filed copy, and publishes exactly which of 3,747 fields it did not check and why, with none of those checks yet admitted by its own quality gates.*

---

## 2. THE CAPABILITY MAP

| # | Vision capability | Status | What exists (measured) | What is missing | Effort |
|---|---|---|---|---|---|
| 1 | Check a filing and declare coverage | **BUILT** (CLI only) | `cdfc run` → VALID, settled **1,898 of 3,747**, notRun 0 · noPredicate 1,849; closure sums; 30-code reason vocabulary; report.html renders | No HTTP path; one template | — |
| 2 | Schema-free induction on an unseen form | **BUILT** (engine) / **UNREACHABLE** (product) | 6 channels induce on 2 foreign synthetic workbooks with zero code change; byte-identical envelopes on artifacts never seen | `run_filing` has no `template` parameter (`p10_run.py:175`) | M |
| 3 | Upload a filing through the product | **SCAFFOLD** | `post_filings` = 3 statements: empty→415, non-`PK`→415, unconditional 422 | Everything behind the endpoint; the drop screen's 201 branch (`screens.py:150`) is already written and unreachable | M |
| 4 | Identify filing type / format | **PARTIAL** | Exactly one format (OOXML .xlsx); exact structural-hash match against **9** vendored blanks; all 9 bind to themselves correctly | CSV/PDF/.xls/XBRL/iXBRL readers; regulator / return / period / version fields (zero such identifiers exist in `src/cdfc/`) | XL |
| 5 | Supply your own template at runtime | **MISLEADING** | `--template` parsed, printed, discarded; `POST /v1/templates` returns identical 202 "T1-T6 ran" for an .xlsx, an **empty body**, garbage and a PDF | Template-parameterised runner; a real admission store; T1–T7 (no implementation exists anywhere) | L |
| 6 | Statutory semantic inference (text → rule) | **ABSENT** | Statute pinned: 1,218 units, 1,189 AGREED of 1,218, two external parsers; 15 regexes find 367 markers | Every link after the text: pool tool crashes, prereg frame matches nothing in the PDF, G0 hard-raises, obligations table is `[]` | XL |
| 7 | Corpus of rules/regulations as an input | **ABSENT** | Nothing. 23 routes, 4 POSTs, none accepts a legal instrument; `ingest`/`induce` exit 2 | An ingress of any kind | XL |
| 8 | Graph built and checked against the filing | **BUILT** / **OFF-PATH** | Precedent map: 1,462 nodes, 4,115 transitive edges vs 2,153 lexical, unreachable formula cells 115→0; TEMPLATE_DIFF fires 1 exact on the seeded O7 overwrite, 0 on the clean filing | Zero production callers; one node type ("Sheet!Ref") and one edge type | M to wire / XL to generalise |
| 9 | Semantic + hidden relationships | **SCAFFOLD** | 6 hand-authored relations; 3 of 6 convert to envelopes; **0 of 6** pass any gate; bind 10/11/10 cells on FME and **0 on 8 of 8** other templates | Any relation derived from data; a cross-reference has no target field so it cannot be an edge | XL |
| 10 | "Gate-qualified" | **BUILT machinery / EMPTY output** | 348 entered, 348 survived G0+G1+G3p, **348 of 348 rejected at G2** (315 no_kill, 33 no_margin); library **0 rows**; G3e and G4 never ran | An admitted library — blocked on an unfunded clean corpus | L |
| 11 | GENERATE a filing / a correction | **ABSENT** | No `fill`/`propose`/`correct` command, no route, no `Proposal` type. `recomputed` is computed by TEMPLATE_DIFF and never reaches a user | A writer that can emit `<f>` (no code path anywhere creates one) plus a proposer | L |
| 12 | VERIFY | **BUILT** (CLI) / **SCAFFOLD** (API + UI) | `cdfc verify` round-trips, names a tampered filing correctly | `POST /v1/verify` is a 2-line constant; S-11 screen discards the runId; one corrupted byte of the attestation = unhandled traceback | M |
| 13 | Mathematically attest | **PARTIAL** | DSSE over PAE, RFC 8032 Ed25519, byte identity **0 of 1,569,451** across 4 environments, `assert_not_production_key` enforced | No trust root; attests the *result* not the computation; `registry_root` is a literal | M |
| 14 | "Platform" | **ABSENT** | Single-threaded `wsgiref`; one shared token guarding **2 of 23** routes; state is CWD-relative paths | Tenancy, isolation, concurrency, TLS, deployment, rate limiting | XL |

---

## 3. THE THREE STRUCTURAL GAPS

### Gap 1 — The product is single-template *by construction*, not by configuration

**Why it is structural.** `run_filing(filing, *, predicates, max_witnesses)` (`src/cdfc/measure/p10_run.py:175`) has no template parameter, and its body calls four parameterless `@lru_cache`d globals pinned to `FME` in `src/cdfc/measure/p5_run.py:33`: `fme_harvest()`, `fme_surface()`, `denominator()`, `fact_set_for(filing, FME)`. The binding layer already computes the right answer and throws it away — an ALR filing binds to ALR's real sha `a414d8d3…`, and is then scored over FME's 3,747-cell mask when its own surface is 1,599 cells, and reported **VALID**. An ITFS filing (own surface 481) gets the same treatment. This is not a missing feature behind a flag; it is a missing parameter threaded through a caching layer that has no keys for it, plus a deliberate refusal that was declared and never wired: `DENOMINATOR_DISAGREEMENT = "invalid.denominator_disagreement"` exists at `src/cdfc/verdict/invalid.py:26` and is raised by no code and asserted by no test.

**What would have to change.** Thread `template` through `run_filing` → `execute`; key the three caches on the template digest; make the bound sha choose the surface and denominator; fire `invalid.denominator_disagreement` when they disagree.

**What would break.** Every currently-VALID cross-template run turns INVALID (correctly). If `template_sha256` enters `run_id_for` (`src/cdfc/evaluate/run.py:127-140`, currently digesting filing/registry_root/profile only), every published run id moves, and with it the byte-identity artifact set. The measurement tools in `tools/measure/` assume the warm FME caches.

### Gap 2 — The obligation vocabulary can express a *citation*, never a *rule*

**Why it is structural.** `Obligation` (`src/cdfc/predicates/obligations.py:57`) is eight citation fields — id, source, instrument, FRBR URI, eId, quote, span, ingest_source. `Clause` adds instrument/eId/span/quote/provisos. `Proviso` (`envelope.py:64`) is text, disposal, emits, span — **no target, no antecedent, no consequent**. `Tolerance` is one dimensionless int in a hard-coded `MILLI_USD_MILLION`. `cel_profile.py:120` bans `timestamp`, `duration`, `now`, `getDate`, `getFullYear` — CEL binds no clock. `ObligationSource` is a closed two-member StrEnum. The 79 `cross_reference` markers the proviso detector finds carry text and span and *no target field*, so "regulation 51 refers to regulation 9" cannot become an edge.

Consequence: the semantic arm cannot be delivered by better extraction. A perfect extractor has nowhere to put a conditional obligation, a definition, a deadline ("within 30 days"), a threshold with units ("USD 150,000 net worth"), a deontic force (shall / may / shall not), or an applicability scope. This is why the arm is at zero and why hiring an extraction team would not move it.

**What would have to change.** Extend the vocabulary *before* extracting: a DEFINITION source, antecedent/consequent on Proviso, a target eId on cross-references, a unit field on Tolerance, a temporal representation that does not require a clock inside CEL.

**What would break.** A third `ObligationSource` member re-opens the deferred arbitration C2. New required fields change the envelope's JCS digest, invalidating all **571** committed envelope files and their golden tests. Admitting a clock into CEL undermines the determinism argument the byte-identity number rests on.

### Gap 3 — No format-neutral seam, and no node type that is not a cell

**Why it is structural.** 15 modules under `src/cdfc` import `zipfile` directly; 14 hardcode the SpreadsheetML namespace. `src/cdfc` contains exactly one `typing.Protocol` and it is `StratumOracle` in `experiment/draw.py`, unrelated to ingest. `Receipt.media_type` is recorded into a hashed projection and never branched on. The three seams a second format would need — `facts.build.fact_set_for(filing: Path, template: Path)`, `schema.fingerprint.structural_projection(blob_path: Path)`, `schema.styles_mask.build(blob_path: Path, rule)` — all take a filesystem Path and each calls `zipfile.ZipFile` on it. And the FactSet key vocabulary is itself spreadsheet-shaped: `cel_path(sheet, ref)` → `f"{sheet}!{ref}"` (`src/cdfc/facts/build.py:98`). XBRL and PDF have no sheets and no refs; the key language does not survive contact with them.

The same shape defeats the graph. There is one node type (a cell inside one workbook) and one edge type (this formula reads that cell). No `Graph`/`Node`/`Edge`/adjacency class exists in `src/`, and no networkx/rdflib/neo4j dependency exists in `requirements.lock`. Two filings, or a filing and a statute, cannot share a node — so the vision's "graph built and then checked against the filing" has no representable form.

**What would have to change.** Invent the reader interface at those three seams; invent a key vocabulary that is not `Sheet!Ref`; invent a node/edge type vocabulary and a store for it.

**What would break.** All 571 envelopes are written in the old key language. `stable_keys`, the CEL path vocabulary and every golden test over them are downstream.

---

## 4. WHAT IS STRONGER THAN THE VISION ADMITS

These are real assets. A bigger product keeps every one of them, and none is cheap to rebuild because each is a *discipline encoded in tests*, not a module.

1. **The coverage declaration itself, with a declared denominator.** 1,849 unchecked of 3,747, split 422 gate-refused / 1,427 no-candidate, each with a remedy; and the denominator declares its own exclusions (6,757 cells recorded → 505 formula + 2,505 locked excluded → 3,747). No competing tool ships the second table. This is the actual differentiator and it is *finished*.

2. **The negative-control discipline.** 141 negative-control entries against 230 guards under exact-set semantics — every guard expected red must go red, every guard expected green must stay green, not *at least one*. 1,600 tests, green. This is a decade-of-habit asset and it is the reason this audit could measure anything at all.

3. **The willingness to publish an empty library.** G2 rejected **348 of 348**. The CLI prints `PRE-GATE: none of the predicates producing this number is admitted under G4` on its own face, and `manifest.json` carries `admissionState: PRE-GATE`. A product that ships an empty qualified set rather than an inflated one has credibility that cannot be retrofitted after the fact.

4. **The typed-skip contract.** **0 of 1,495** formula cells corpus-wide are silently dropped; 325 skips on FME are typed by kind (`iferror_wrapper` 130, `key_unresolved` 118, `function_outside_vocabulary` 59, …). A coverage tool that drops constructs silently is lying about its denominator; this one structurally cannot.

5. **Determinism, measured.** 0 bytes differing of 1,569,451 across four environment variations. The harvest emits byte-identical envelopes on workbooks the system has never seen — I confirmed the property holds on an unseen EIOPA workbook, not only on the pinned corpus with a golden test. The YAML emitter is hand-rolled (`harvest.py:479`) precisely so this survives library churn.

6. **`assert_not_production_key`** (`src/cdfc/attest/ed25519.py`). `sign()` raises `KeyRefused` on any secret but the published demo key. The demo cannot become the product by accident. That is a correct, deliberate refusal and most teams would have shipped a config flag instead.

7. **The dual-extraction statute pin.** 1,218 units from a 2,909,841-byte PDF via two external parsers, 1,189 AGREED / 28 DISPUTED / 1 SINGLE_PARTY, `SAME_AUTHOR = (0,0)`, with `docs/CORPUS-PROVENANCE.md` honestly recording that reproduction terms were **not** established and that two amendment notifications are not pinned. Nothing consumes it yet — but the corpus engineering is real work already done.

8. **Real cycle detection where it matters.** `calc/evaluate.py:480-516` genuinely marks circular references NOT_RUN — I verified with a hand-built 2-cycle. (The precedent map's docstring claims the same and is wrong; see §5.)

---

## 5. MISLEADING SURFACES

### A. False statements emitted to a user or a client

| Location | The claim | The measured truth |
|---|---|---|
| `src/cdfc/api/handlers.py:221-224` | `"T1-T6 ran. T7 is a human signature…"` | Byte-identical 202 for an .xlsx, an **empty body**, 18 bytes of garbage, and a PDF. Nothing ran. `grep -rn 'def t1\|template_admission\|admit_template' src/ tools/` returns nothing; T1–T7 exist only in `spec/03-stack.md:182-196`. |
| `src/cdfc/api/handlers.py:94` | `structuralFingerprint="sheet-shape:unknown"` | A literal returned for every filing on earth. The real function is `src/cdfc/schema/fingerprint.py:69` with **zero** callers in `src/`. Rendered to the user with a copy button. |
| `src/cdfc/api/handlers.py:82-84` (docstring) | "The fingerprint is what they paste into `POST /v1/templates`… so the refusal carries its own remedy" | The fingerprint is a constant and the endpoint it names is a constant. The remedy loop is closed and empty. |
| `src/cdfc/api/handlers.py:67-69` | `templateSha256` | Fabricated: `f"sha-{name}"` → `"sha-FME_Quarterly"`. Ceiling `0.63` is a literal. 3 rows against a catalogue of 9 with real sha256s. Byte-identical payload from an empty directory. |
| `src/cdfc/api/routes.py:44` | GET `/v1/templates/{sha}/schema` — "the induced schema" | Ignores `{sha}`; returns the API's own response-DTO JSON Schema (`DenominatorOut`, `ErrorOut`, `RunOut`, …). Identical body for a real sha and for `"deadbeef"`. |
| `src/cdfc/api/routes.py:40` + `openapi.json` | POST `/v1/verify` — `{reproduced, diff[]}` | `handlers.py:227-228` is a 2-line constant that never reads the body. Identical response for a genuine attestation, for garbage and for an empty body. Also **unauthenticated**. |
| `src/cdfc/cli.py:78-79` | `--template` help: "the pinned blank; defaults to the FME reference template" | Discarded at `cli.py:192`; `cli.py:197` prints the discarded name as the template used. Two templates → identical run id `9e6c7cc491f4e0a8`, identical `1557 / 3747`, manifest naming the FME sha. |
| `src/cdfc/surface/web/screens.py:1053` and `:216` | remedy `cdfc verify <run-id> --against <published.html>` | `cdfc verify` takes one positional attestation path plus `--blobs`. `--against` does not exist: `error: unrecognized arguments`. |
| `src/cdfc/surface/web/screens.py:200-202` / `:180` | The Verify and Admit screens | Both post the literal `b"{}"`. The runId the user typed and the fingerprint the user typed are discarded. The `/templates` form (`screens.py:1009-1018`) has **no file input at all**. |
| `src/cdfc/attest/dsse.py:103-124` | `signature VALID` | Verifies against `entry["publicKey"]` — the key inside the envelope under test. No allowlist, no pinned key. I re-signed a payload with an attacker key and `cdfc verify` printed `reproduced YES / signature VALID` — immediately above its own line that "a changed report and a changed key are different events". It cannot detect a changed key at all. |

### B. Docstrings describing code that does not exist

| Location | The claim | The measured truth |
|---|---|---|
| `src/cdfc/probes/precedents.py:243` | "**A cycle raises**" | It does not. `_close()` on a genuine 2-cycle converges silently and returns a saturated closure. The 64-round bound is unreachable — the fixpoint doubles reach each round. |
| `src/cdfc/probes/relations/partition.py:44-46` | "a template whose two tables disagreed in length would be a different template and `build()` refuses it below" | `build()` takes **no arguments**, reads no workbook, and returns a constant string (`partition.py:134`). It cannot refuse anything. |
| `src/cdfc/probes/relations/registry.py:150-153` | "Long CEL is GENERATED from the pinned blank… The builder is deterministic in the template" | All three builders are nullary: `build() -> dict[str, str]`. |
| `src/cdfc/evaluate/binding.py` | a binding failure exists so a filing is never "checked against the wrong form" | Binding succeeds and the *checking* is against the wrong form anyway, silently, with a VALID verdict. |
| `src/cdfc/attest/verify.py:218-222` | "A MISSING BLOB IS A NAMED ANSWER, NOT A CRASH… a reader would learn that the tool broke rather than that the artifact did" | Applied to the blob lookup only. One corrupted byte of `attestation.json` → unhandled `KeyError: 'counterEvidence'` or `JSONDecodeError`, discarding a `signature_valid=False` already computed at `verify.py:246`. |
| `src/cdfc/ingest/container_guard.py` | "a guard that runs after the parser is not a guard" | It has **no caller at all**. I appended a 20 MiB entry to the FME filing: `guard()` raises `invalid.container_guard_tripped`; `cdfc run` on the same file returns VALID with a full coverage declaration. |
| `tools/e6/enumerate_shall.py:6-7` | "carries nine instruments, all `kind: TEMPLATE`… `statute_instruments` is `[]`" | Ten instruments, one STATUTE. The tool then dies at line 72: `ImportError: cannot import name 'load_instrument'`, and line 74 would raise `TypeError` after that is fixed. |

### C. Stale docs, and one test that makes a falsehood a build requirement

- `tests/unit/test_obligations.py:112` — `assert "D-P7-01" in text and "statute_instruments: []" in text`. **A false sentence is now required for the suite to be green.**
- `obligations.yaml:16` and `src/cdfc/qualify/instruments.py:17` — both still say `statute_instruments: []`; MANIFEST says `['statute-fm-regulations-2025']`.
- `fixtures/predicates/proviso-labels.json` `reason_if_absent` — "no statutory instrument is pinned in this repository" is quoted **verbatim into a live runtime exception**; I saw it in the `ProvisoRecallUnmeasured` raised by my own G0 test.
- `experiments/E6/DECISION.md:27` — "There is no statutory instrument in this repository, there never has been one in its git history."
- `experiments/E6/PREREGISTRATION.md` — the three pre-registered chapter titles appear **nowhere** in the pinned PDF (the real headings are CHAPTER I–XII; registration is II not III, schemes is III not IV, and there is no "Valuation, Reporting and Disclosure" chapter). The file is hash-locked at `h0 = e7e1099209a5…`, so the sampling frame of the whole E6 experiment is frozen against an instrument it does not describe.
- `docs/measurements/P11-byte-identity.md:7` and `docs/measurements/P11-exit-gate.md:20` publish **1,568,185**; the tool now produces **1,569,451**. Nothing pins it — `make verify` does not run `byte-identity`.
- `README.md:95` — "1,573 tests"; the collection is **1,600**.
- `README.md:73` — "`docs/OPEN-ITEMS.md` carries the standing list" for staleness and deployment. It does not: `grep -niE 'deploy|stale|packag' docs/OPEN-ITEMS.md` returns nothing.

### D. The suite is green *over the stubs*

`tests/unit/test_api.py:41-47` POSTs the 14-byte string `b"PK\x03\x04rest-of-a-zip"` and asserts the 422 with `assert body["structuralFingerprint"]` — a truthiness check a constant satisfies. That test **pins the hardcoded refusal as correct behaviour**. The only three references to `/v1/filings` in `tests/` are in that one file, and none uploads a real workbook or asserts a run is created.

---

## 6. THE SHORTEST HONEST PATH

### Phase 0 — Stop the false statements (days)
Everything downstream is credibility-dependent, and this phase costs almost nothing.
- Delete `"T1-T6 ran"`; call `structural_fingerprint()` at `handlers.py:94`; make `--template` work or refuse; fix the two `--against` remedy strings; fix `1,573`→`1,600` and `1,568,185`→`1,569,451`; unpin the false sentence at `tests/unit/test_obligations.py:112` and correct `obligations.yaml:16`, `instruments.py:17`, `enumerate_shall.py:6-7`, `DECISION.md:27`, `proviso-labels.json`.
- **Becomes TRUE:** no surface emits a statement the code cannot support.
- **Demo:** nothing new. That is the point — a buyer who catches one of these loses all the others.

### Phase 1 — Make the engine reachable (weeks) — *highest leverage in the whole plan*
The engine is already general; only the wiring is missing. I proved this with a 30-line script and no change to `src/`.
- `run_filing(filing, *, template)`; key the three `lru_cache`s on the template digest; let the bound sha select the surface and denominator; fire `invalid.denominator_disagreement`.
- Wire `post_filings`: `receipt.receive` → `container_guard.guard` → `structural_fingerprint` → `bind_template` → `execute` → **201 + runId**. The drop screen's success branch at `screens.py:150` is already written and currently unreachable.
- Serve `attestation.json` and `log.jsonl` — two one-line 404s at `handlers.py:202-207` sitting directly beneath a `get_report` that reads its file correctly.
- **Becomes TRUE:** a filing uploaded in a browser produces a coverage declaration, scored against the template it actually bound to.
- **Demo:** upload the ALR workbook; get **1,599** cells and ALR's own denominator instead of today's VALID-over-FME's-3,747.

### Phase 2 — The second template, end to end (weeks) — *this is the schema-free claim, delivered*
- Real template admission: `POST /v1/templates` writes a catalogue entry keyed by the real fingerprint; the `/templates` screen gets a file input; `GET /v1/templates` enumerates the real 9 with real digests and real per-template ceilings (the field-surface tool already computes them).
- Fix `date_bound`'s ISO-8601 literal (`harvest_classes/_bounds.py:57-62` — I proved the sole cause is the literal by re-writing the same validation as an Excel serial, which fires) and correct its skip detail, which currently blames the filer.
- Read `numFmt` for currency instead of `probes/degree.py`'s English `MONEY_MARKERS` — 255 `cfRule` elements and 21 `numFmt` definitions in the corpus are read by nothing, and a GBP/EUR/INR form currently gets **0** money cells and therefore tolerance 0.
- **Becomes TRUE:** a buyer's own workbook is checkable without a code change.
- **Demo:** hand the system a form nobody in the room has seen; admit it; upload a filled copy with three seeded defects; all three surface with exact witness cells. *(I ran exactly this on two synthetic foreign workbooks — FCA: 19/31 settled, 3 of 3 caught; EIOPA: 17/17 clean, 4 of 4 caught. Only the entry point is missing.)*

### Phase 3 — The graph arm (weeks → months)
**3a (cheap, real).** Put the precedent map and TEMPLATE_DIFF on the production path. Both work — 1,462 nodes / 4,115 transitive edges; 1 exact fire on the seeded O7 overwrite, 0 on the independently-computed clean filing — and both are absent from the import closure of `cdfc.cli`, `cdfc.api.serve`, `cdfc.measure.p10_run`. Admission needs one new member of `ADMITTED_HOST_FNS` plus a mutation-harness row. Note the honest caveat found in audit: the *sibling* seeded defect (`formula-overwritten__investors-N5`) fires zero because every precedent is empty — the ceiling is real and documented at `tools/measure/p9_ceiling.py:190`.
**3b (the first honest, data-derived graph).** The harvest already emits **181** cross-sheet equality edges as 181 independent predicates. I parsed them back into an adjacency map: they contain **90** genuine two-hop A→B→C chains, and **0** composed A→C predicates exist. Build the adjacency, close it transitively, and you have a graph *derived from the artifact* rather than typed by a human — which is more than the six hand-authored relations will ever be.
**3c (the real work).** A node type that is not a cell. Today: one node type, one edge type. A clause node, an entity node, a period node and a typed edge vocabulary are what let two filings — or a filing and a statute — share a node. Until 3c ships, "graph engine" honestly means "one workbook's formula dependency graph".
- **Becomes TRUE after 3a/3b:** a failure is attributed to the cells that actually determine it, and the system surfaces a relationship no human typed.
- **Demo after 3a:** the O7 overwrite is named as a *finding*. Today `cdfc run` on that fixture reports PASS 1,557 / FAIL 0.

### Phase 4 — The semantic arm (months, and it has a human blocker)
The chain: PDF → dual extraction (**works**, 1,218 units) → shall pool (**crashes**) → draw → model proposal (**never run**) → STATUTE obligation (**table empty**) → G0 (**hard-raises**) → predicate with a Clause (**0 of 571**). The last real link is the addressable text.
- **4a (days).** Fix `tools/e6/enumerate_shall.py:72` (`load_instrument` does not exist) and `:74` (indexes a list of strings). Re-lock `PREREGISTRATION.md` against the chapters that are actually in the PDF. Re-locking breaks `h0` deliberately, in the open, with the reason recorded — leaving it is strictly worse, because a frozen frame that samples a non-existent instrument is not a pre-registration, it is a bug wearing one.
- **4b (the human blocker — one named person, weeks).** Label 50 proviso spans with a recorded seed and date. `fixtures/predicates/proviso-labels.json` has `labeller: null` and 0 spans, so `g0_scope.py:131` raises `ProvisoRecallUnmeasured` on any STATUTE obligation — I authored a genuine one from the pinned text (verbatim AGREED unit, exact span) and it raised. **There is no mechanical substitute.** This one task gates the entire semantic half of the vision, and it costs a person, not an engineering quarter.
- **4c.** Extend the obligation vocabulary (Gap 2) *before* building any extractor.
- **4d.** Take the E6 run (money + two humans + Cohen's κ) and record RETAIN or DROP. Until `DECISION.md` says RETAIN, `ci/barrier5.sh` forbids `src/cdfc/model/propose.py` from existing. **Do not weaken that barrier to make a demo** — it is the most defensible thing in the repo.
- **Becomes TRUE after 4a+4b:** `predicates_with_a_STATUTE_obligation` can be non-zero for the first time. That single number is the vision's second half coming off the floor.
- **Demo:** point at a numbered regulation in the pinned FM Regulations; show the clause text, the span, the two-parser agreement, and a predicate that cites it and fires on a filing.

### Phase 5 — Attest the computation, not the report of it
- `registry_root` is the literal `"root-p5-pre-gate-fixture"` (`p5_run.py:39`); the real Merkle root sits unused at `predicates/registry.py:164`. I produced a semantically-changed predicate that yields a **byte-identical, validly-signed** attestation — a recipient cannot detect a different predicate set behind the same numbers.
- Stop feeding `residue` and `counterEvidence` back from the document under test (`verify.py:274-275`). They re-derive to themselves and *cannot fail*. `residue` is precisely the field a filer would want to zero.
- Give the verifier an expected keyid / key directory instead of trusting the envelope's own `publicKey`.
- Add `run_jsonl_sha256` and `report_sha256` to the manifest pins — today the signature reaches 4,020 bytes of a roughly 1 MB record.
- **Becomes TRUE:** "mathematically attest" describes the computation.

### Phase 6 — Platform
Not a wrapper. `run_id_for` digests `{filing, registry_root, profile}` with no tenant term, and `write()` overwrites in place — two parties uploading the same workbook collide on one directory. One stalled client with no body takes the whole service down (measured: second request `TimeoutError` after 4.00s). No Dockerfile, no TLS, no rate limit, no configurable data root — `cdfc serve` from the wrong directory silently serves 503s and 404s with no startup error.

---

## 7. WHAT TO STOP CLAIMING NOW

### README.md

| Line | Stop saying | Say instead |
|---|---|---|
| 95 | "`make verify` runs 1,573 tests" | "runs 1,600 tests" — and add a test that pins the number, or drop the number |
| 73 | "…`docs/OPEN-ITEMS.md` carries the standing list" | Add deployment packaging and staleness to `docs/OPEN-ITEMS.md`, or write "Also absent, and **not yet** in `docs/OPEN-ITEMS.md`: …" |
| 28-32 | "This one derives its rules from the filing template rather than from a maintained schema" (true of the engine, read as true of the product) | Append: "The induction is template-agnostic and has been run on workbooks outside this corpus. The shipped runner is not: `cdfc run` substitutes the FME blank whatever `--template` is given, and `POST /v1/filings` refuses every filing. Only the command line checks anything." |
| 8-18 (video) | An unqualified walkthrough of a running server | State in the caption which steps are CLI. The server's upload endpoint refuses every filing; a viewer will assume otherwise. |

Add a fourth bullet to **THE SCOPE OF THIS PROTOTYPE** (currently three):

> **It checks one form.** Nine blanks are pinned and a filing is bound by exact structural hash. Whatever template you name, the checks, the field surface and the denominator come from the FME blank — an ALR filing (own surface **1,599** cells) is scored over FME's **3,747** and still reported VALID.

### docs/PITCH.md

| Line | Stop saying | Say instead |
|---|---|---|
| 22-24 | "This system induces a form's rules from the form itself… No rules project to commission, no schema to maintain, no lag when a version changes." | "The induction engine derives a form's rules from the form itself — formulas, dropdowns, protection masks, cross-sheet references — and has been run on forms outside its corpus. In the prototype the shipped runner is wired to one workbook family; making a second form checkable is a wiring change, not an authoring project." |
| 76-77 | "Static analysis of the artifact — formula graph, data validations, protection mask, cross-sheet references" | "…formula graph (built, and not yet on the path that checks a filing), data validations, protection mask, cross-sheet references" |
| 78-80 | "Each is put through seeded-fault testing before it may count: a check that cannot be shown to catch anything contributes nothing to coverage." | Keep — but add the sentence the README already carries and PITCH does not: "In this prototype **348 of 348** candidates were refused at that gate, and the published coverage number comes from a disjoint pre-gate population. The admitted library has 0 rows." |
| 80-81 | "Reports are deterministic and re-derivable byte for byte, so a published claim can be verified by whoever receives it." | "The attestation payload is deterministic and re-derivable byte for byte — 0 bytes differing of 1,569,451 across four environments. In the prototype it covers a 4,020-byte summary statement, not the per-cell record or the rendered report, and it is signed with a demo key published in this repository." |

### The UI

- `screens.py:1053` and `:216` — delete `cdfc verify <run-id> --against <published.html>`; replace with `cdfc verify <path>/attestation.json`.
- `screens.py:1009-1018` — the "Admit a template" form collects a fingerprint it discards. Until Phase 2, replace it with an empty state: *"Template admission is not implemented in this build. The nine pinned templates are the only ones it can bind."*
- `handlers.py:91-94` — the 422 tells the user to paste a fingerprint (a constant, identical for every file) into an endpoint that does nothing. Until Phase 1, replace the detail with: *"This build checks filings from the command line only. `POST /v1/filings` does not yet run a check."*
- Anywhere `GET /v1/templates` is rendered — it publishes 3 of 9 templates with invented shas. Either enumerate the real corpus or drop the sha column.

### Two phrases to retire from every surface until they are earned

- **"gate-qualified"** — always followed by "the qualified set is currently empty: 348 of 348 rejected at G2".
- **"mathematically attest"** — say "deterministically re-derive and sign". The current scheme signs a summary of the result with a repo-published demo key and validates against whatever key the envelope carries.

**The line to use with a buyer today:** *A deterministic coverage declarer for structured spreadsheet filings — it induces checks from the form's own structure, runs them, and publishes exactly what it did not check and why.* Statutory semantic inference and the graph engine belong in the roadmap column until Phase 4b and Phase 3b respectively.