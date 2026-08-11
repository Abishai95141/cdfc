**Warrant key, governing every number below.** `MEASURED` — run against the primary artifact.
`VERIFIED-AT-SOURCE` — the primary document was opened and the value read off it. `SECONDARY` — a
credible source states it; the primary was not opened. `DERIVED` — arithmetic from stated inputs, and **it
never claims a stronger warrant than its weakest input**. `UNVERIFIED` — could not check. Every fraction
carries its denominator inline.

**Four renames are decided here and bind every JSON key, API path and screen label in the programme.**

| Old | **New** | Why |
|---|---|---|
| `coverage`, `coverageFraction` | **`settledFraction`** | "Coverage" is reserved for the conformal guarantee, which appears three pages away. One word, one meaning |
| money in "micro-units" | **`MILLI_USD_MILLION`** — `int64` count of 10⁻³ USD Million; **1 unit = USD 1,000**; `12.34 → 12340`; half-ulp 5 units; `τ(n) = 5n` | The drafts differed by 10³ and every tolerance is in units |
| the `(field × obligation)` pair | **the cell** | The unit of the denominator, of closure and of the settled fraction is the filer-editable cell. `obligation` becomes a predicate attribute (§4.2) |
| `COVERAGE_INSUFFICIENT`, `…WITHIN_STATED_COVERAGE` | **`SETTLEMENT_INSUFFICIENT`**, **`EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`** | Same rename on the verdict enum. The property that matters — a verdict name unquotable without its own qualifier — survives |

---

## 1. THE DECISION TABLE

Every row is a decision: the component, the decision, the runner-up it beat, the evidence, the **licence
with its warrant** — a licence read at source and a licence merely reported are different facts and the
table shows the difference — and the testable trigger under which we switch.

| # | Component / layer | **DECISION** | Beat | Evidence | Licence + warrant | Switch when |
|---|---|---|---|---|---|---|
| 1 | Workbook parsing — authoritative reader | **`zipfile` + `lxml` 6.1.1, namespace-aware, over sheet XML, `styles.xml`, `sharedStrings.xml`, `workbook.xml`, `extLst`** | openpyxl 3.1.5 as schema source | openpyxl sees **35 of 54** validations and reports the AML-CFT sheet as **0 when it is 5**; a hand regex reaches the identical wrong 35 by the identical mechanism. Full parse **28 ms** (MEASURED, L14) | BSD — **SECONDARY** | Never for schema induction. Hard rule, with a constants test |
| 2 | Second reader | **openpyxl 3.1.5: formula text with shared-formula row-shifting; `data_only=True` cached values** | Hand-rolling `si`→master translation | openpyxl returns the *translated* dependent (`O4 → =SUM(C4:N4)`), which a hand-rolled reader gets wrong. 202 ms (MEASURED) | MIT — **SECONDARY** | We write and mutation-test our own translator. Until then: never for validations, **never to re-serialise** (round-trip loses 98.2% of bytes and all 19 `x14` validations, MEASURED) |
| 3 | Third reader / normaliser | **LibreOffice headless, pinned by container digest, offline only — not on the verdict path (§7 G12)** | LibreOffice as primary analysis path | It expands all 505 formulas and migrates `x14` into the main namespace in 3.9 s — **but writes 53 where 35 + 19 = 54: one validation lost, unexplained, in the step being recommended** (MEASURED, L05) | MPL-2.0 — **SECONDARY**; file-level copyleft, subprocess use imposes nothing | The 53-vs-54 loss is characterised as a duplicate-`sqref` merge |
| 4 | Schema induction | **Ours, ~200 lines over the OOXML cell graph** | QuantMind (2.3k★) | BUILT, 28–44 ms: 505 formula cells, 54 validations, 3,747-cell field surface, 280 predicates (MEASURED, L14) | MIT — SECONDARY (not adopted) | Never. **Do not take a 2.3k-star dependency to save 200 lines** |
| 5 | Regulation-text parsing | **Docling → `DoclingDocument`; `ProvenanceItem{page_no,bbox,charspan}` adopted verbatim as our `pdf_span`** | MinerU | Docling publishes the only typed, versioned, per-cell provenance schema with an explicit `coord_origin` enum (VERIFIED-AT-SOURCE, L08) | Docling MIT — SECONDARY. **MinerU is Apache-2.0 *plus riders* — VERIFIED-AT-SOURCE**: its §2 requires prominent attribution for any online service. "Apache-2.0" on a slide would be false | Docling's table fidelity blocks a clause. Then PaddleOCR-VL primary |
| 6 | Scanned circulars | **PaddleOCR-VL, run once offline, output frozen and content-addressed** | olmOCR, Marker, Nougat | 10 of 399 circulars are images (2.5%). Marker is worst on OmniDocBench v1.6_full tables (TEDS 65.77); Markdown linearisation destroys the anchor | Apache-2.0 — SECONDARY | Never re-enters a verdict path |
| 7 | Clause identity | **Akoma Ntoso: `eId` per clause, FRBR URI per instrument, via a deterministic promoter** | Inventing a clause-key scheme | OASIS standard designed for amendment commands. **866 dated cross-references in 58.6% of circulars; 76 of 82 amending circulars cite a resolvable target (92.7%)** (MEASURED, L08) | OASIS spec — no obstacle | Never |
| 8 | FRBR URI handling | **Implement the URI grammar ourselves, ~100 lines** | `laws-africa/cobalt` | GitHub reports **NOASSERTION** for `cobalt` and `indigo`; no lane opened either LICENSE | **NOT-FOUND**. `bluebell` is **GPL-3.0 — VERIFIED** and must never be linked | Someone opens `cobalt`'s LICENSE and it is permissive. We adopt Indigo's amendment/point-in-time *data model* either way, never the platform |
| 9 | Citation anaphora | **Ours, modelled on `eyecite`'s antecedent architecture** | Adopting `eyecite` | Its power is `reporters-db`/`courts-db` — US case reporters, zero knowledge of `IFSCA/GN/2025/…`. **The algorithm transfers; the data does not** | BSD-2 — SECONDARY (not adopted) | An Indian statutory-citation library is found. **L08 states it did not search that ecosystem at all** — that search must run before any novelty claim here |
| 10 | Predicate language | **CEL, admitted subset, in a three-slot envelope `applicable`/`expr`/`witness`** | Python + pandera | **The settled fraction is statically computable only because the language has no variables**; model-written Python needs a sandbox and the sandbox layer is where the 2026 CVEs are; an auditor must read a rule, not a function body; a ~20-production grammar has enumerable mutation operators. Precedent: **Kubernetes ValidatingAdmissionPolicy, GA in v1.30** | Apache-2.0 spec — SECONDARY | A predicate class the grammar cannot express **and** cannot be quarantined into a host function. Rego only if the stack moves to Go |
| 11 | CEL runtime | **`celpy` (`cloud-custodian/cel-python`), pinned by PyPI name *and* wheel hash** | `cel-expr-python` | Pure Python, no C++ build, auditable. **Naming trap: two different projects live at a path called `cel-python`** | Apache-2.0 — SECONDARY | `celpy` fails the conformance suite **on error semantics**, where the `&&`/`\|\|` guard lives. `cel-expr-python` wraps the official C++ and inherits conformance |
| 12 | Arithmetic representation | **`MILLI_USD_MILLION` (see rename table)** | `double`; or `Decimal` outside CEL | CEL has **no decimal type**. Guidance C111 fixes 2 dp on USD Million, so the quantum is USD 10,000 and lawful per-cell slack USD 5,000. As `double`, every arithmetic predicate acquires an FFR we did not choose and cannot attribute | — | Never |
| 13 | Tolerance model | **`τ(n) = 5n` units, declared in each predicate and versioned with it; `ROUND_HALF_UP`; counts get zero tolerance** | A constant epsilon | A constant epsilon is the likeliest source of spurious failures. Two predicates differing only in tolerance are two rows with two measured FFRs — **which makes tolerance a measured parameter, not a hidden constant** | — | Never |
| 14 | Formula evaluation | **Ours: topological evaluator over the induced cell graph in `Decimal`; eight functions — `SUM`, `COUNTIF`, `IF`, `IFERROR`, `INDEX`, `ROW`, `ROWS`, `AGGREGATE(15,6,…)`** | `formulas` 1.3.4 | Licence: `formulas` **EUPL 1.1+**, `pycel` **GPL-3.0** (SECONDARY) — copyleft with a live network-deployment question. Method: an imported evaluator imports an unmeasured error rate our own gate would reject. **And building it is the differential arm** — the only check that detects a formula cell overwritten with a literal | Ours (Apache-2.0) | A template's function vocabulary exceeds what we implement exactly |
| 15 | Cross-check recalculation | **The template's own cached values (present on 505 of 505 formula cells, MEASURED) are the primary cross-check; LibreOffice is the *offline* second engine** | Trusting one engine online | The 91.9% LibreOffice recalc-exact figure comes from a **three-hour, unreplicated, self-graded vendor repo** whose top entrant is the owner's product — ruled **evidentially void**. So we quote no floor and **measure disagreement per cell, per template version, offline** | MPL-2.0 — SECONDARY | The engines agree across the full 505-cell graph with a positive control on `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101` |
| 16 | Degeneracy prover | **Z3 for the proof arm of gate G3: `¬P` SAT, `P` SAT, subsumption `P₁ ∧ ¬P₂` UNSAT** | Empirical degeneracy alone | It is a satisfiability question; CEL's comparison fragment maps to SMT-LIB nearly 1:1; Z3 returns a **model** — a counterexample workbook that enters the library as evidence | **MIT (SECONDARY — the LICENSE was not opened by any lane; open it before shipping)** | Never removed, never trusted alone. Host functions are uninterpreted; `unknown` is treated as **unproven, never as non-degenerate** |
| 17 | Fault-seeding harness | **Ours, ~200 lines. Abraham & Erwig's 17 spreadsheet mutation operators (IEEE TSE 35(1):94–108, 2009) + F12 vocabulary drift, F13 carry desync, F14 vocabulary-gap exploitation** | mutmut / PIT / Stryker | **Category error**: those mutate source code; our mutants are *data* and the subject under evaluation is the *predicate set*. BUILT: **19,782 mutants in 2.5 s = 7,946/second** (MEASURED, L14) | Ours (Apache-2.0); mutmut BSD-3 — SECONDARY, retained for mutating **our own** code | Never |
| 18 | Scoring | **`KR = K/O` with both integers, plus `UR = U/G`, plus the per-fault-class vector. Never a bare percentage** | `killed/(mutants − equivalent)` | **3,512 of 7,500 (46.8%)** comparable spreadsheet mutants are irreversible. A rate over *generated* mutants understates every predicate by roughly half, variably by operator mix. **Observability is a diff; equivalence is a theorem** | — | Never |
| 19 | Registry minimisation | **Reimplement SPADE's ILP in PuLP/CBC, ~40 lines, with the interaction bound `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`** | `shreyashankar/spade-experiments` | 17★, 1 fork, **no LICENSE file present**, last push 2024-04-07. Unlicensed is unusable in a commercial product regardless of quality | PuLP MIT / CBC EPL-2.0 — SECONDARY | Never |
| 20 | Interval statistics | **Wilson interval on every rate, ~8 lines. A point estimate is forbidden by schema** | A bare percentage | `0 fires / 4 real → [0.000, 0.490]`. **A real FFR from 4 real filings with an interval of [0, 0.49] is more honest and more useful than 0.0% from 340 workbooks we wrote ourselves** | — | Never |
| 21 | Differential / relation execution | **`Hypothesis` `RuleBasedStateMachine`: `@invariant` for *necessary* relations (⇒ FAIL), in-rule assertions for *expected* (⇒ `INFORMATIONAL`). `max_examples = 50`** | Hand-rolled loops | The necessary/expected split is enforced by the library, not by our convention. **55% of mutations found at n = 1, 76% within 20 inputs** — the input space is small and fixed | **Reported MPL-2.0 — SECONDARY, LICENSE not re-read.** This ledger does not assert a licence nobody opened | Cross-table set relations outgrow a CEL one-liner. Then Soufflé (UPL-1.0), at the cost of a second toolchain |
| 22 | Relation authorship | **Human, read off the formula graph and guidance notes. No model** | Asking a model for relations | MEASURED: model-generated relations score *"markedly low"* on novelty — which is how the brief got five relations of which **four false-alarm on a correct filing and the fifth is vacuous** | — | Never. **The one layer where the model is measurably worse than a person with the file open** |
| 23 | Conformal / abstention | **`crepes` (`MondrianCategorizer`) + `MAPIE` (`OnlineMartingaleTest`), RAPS over the induced key set — BUILD GATED** | `TorchCP` | TorchCP is **LGPL-3.0 (SECONDARY)**; `nonconformist` dead since 2021-03-20; `Fortuna` archived; `puncc` ships no root LICENSE | crepes / MAPIE BSD-3 — SECONDARY | **Pre-registered gate:** measure key-binding accuracy `μ`. Forced abstention `r ≥ (μ−α)/(1−α)`. **`μ > 0.30` ⇒ do not build it** (α = 0.05 forces ≥ 26.3% abstention from base error alone); `μ ≤ 0.10` ⇒ build; between ⇒ build and ship the **abstention rate** as the headline |
| 24 | Structured output (attachments) | **Provider-native structured output, `key` typed `Literal[*L1_KEYS]`, retry disabled, plus the post-hoc deterministic key check** | `outlines` / `XGrammar` | The key is an enum over exactly the induced keys, so an off-schema key is **ungeneratable**. `outlines`/`XGrammar` mask logits and are strictly better **but require a local model, and no local model is in this stack**. **Whether provider-native constraint is guaranteed or best-effort is UNVERIFIED — which is exactly why the post-hoc guard is not optional** | Apache-2.0 — SECONDARY (not adopted) | **An open-weight model enters this path. Then `outlines` becomes primary.** Retry-until-valid is banned outright: it manufactures the clean verdict this product exists to refuse |
| 25 | Model provider | **Anthropic** | Open-weight local | The comparison is **UNVERIFIED**; a guessed URL is the fabrication this programme forbids. **The architecture converts it into a measurement:** the gate adjudicates deterministically, so *model choice affects yield, not correctness*. Measure admitted predicates per unit cost | — | The measurement says otherwise |
| 26 | Model — candidate proposal | **`claude-opus-5`, Batch API (50% off), prompt caching on the schema prefix. Offline, once per template version** | `claude-sonnet-5` | A bad candidate costs a rejection, not an error — the right place to spend on capability. Offline ⇒ Batch applies; stable prefix ⇒ caching applies. **The failure mode being bought down is a plausible-but-wrong check** | — | Yield-per-rupee says Sonnet 5 wins. Under ten dollars either way (§5) |
| 27 | Model — attachment extraction | **`claude-haiku-4-5` bulk, escalating to `claude-sonnet-5` when the conformal set is not a singleton** | Opus 5 for everything | The hard key guard makes failures cheap: a wrong key is caught, a non-singleton set abstains. **A filing with no attachments has a marginal model cost of exactly $0.00** | — | Escalation exceeds ~30%; promote the bulk model |
| 28 | Model — evaluation, relations, verdict, attestation | **No model. Anywhere. Ever.** | LLM-as-judge | LLM judges detect false success at **AUROC ≤ 0.65, 13% recall at a 10% flag rate**; TF-IDF + logistic regression over the same trajectories reaches 0.825–0.953 at **3,364× lower latency** — and even that runs at **50% precision at a 10% flag rate** | — | Never. Enforced at schema level: `MODEL_EXTRACT` may never be the sole `method` on a `PASS` |
| 29 | Data-validation substrate | **Ours. There is no substrate to adopt.** `pandera` 0.32.1 adopted **only** as a host-function implementation for bulk column checks | Great Expectations / Soda Core / dbt / Deequ | **GX is disqualified on semantics:** with `catch_exceptions=True`, *"execution will not fail… it will return `success = False`"* — the same value it returns when the data was wrong. **A framework that folds *could-not-check* into *failed* destroys the denominator**, which is the product. No field for not-applicable, out-of-scope or no-oracle at any verbosity | pandera MIT — SECONDARY (version VERIFIED-AT-SOURCE via PyPI JSON; its release date **UNVERIFIED**). **Soda Core is Elastic 2.0 — VERIFIED-AT-SOURCE**: *"You may not provide the software to third parties as a hosted or managed service"*. Our product **is** that | Never. Read *"do not rebuild Great Expectations"* as: **do not rebuild the check library; you must build the verdict model, because it exists nowhere in the ecosystem** |
| 30 | Model-free baselines, run **before** the model | **B0 the template's own 138 checkable relations · B1 Daikon over the clean corpus · B2 the degenerate arm** | Proposing without baselines | The free baseline beats the neural method more often than not here: SPADE's select-all is 100% settled at 100% FFR; TOGA's `NoException` baseline gets **68.9% of TOGA's bugs at 2× the precision**. **If proposal does not beat B0 ∪ B1 ∪ B2 on marginal kill at equal FFR it has produced nothing** | Daikon MIT-equivalent — SECONDARY (licence text not opened) | Never. Daikon's trivia output doubles as the degeneracy list |
| 31 | Sandboxing — parser tier | **gVisor (`runsc`) + `seccomp` + `--network=none` + read-only rootfs + capped tmpfs + non-root uid + `no-new-privileges` + RLIMITs + wall-clock kill; zip guards *before* parse; `lxml` with `resolve_entities=False`, no DTD, no network** | Firecracker | The threat model is a confused model and a malformed file — but the **filer** is hostile-capable and an `.xlsx` is a zip of XML. **The parser, not the predicate, is the exposed surface.** Firecracker buys hypervisor isolation against an adversary we do not have, at a VM per filing | **NOT-FOUND** — no lane opened gVisor's LICENSE. Widely reported Apache-2.0; not asserted here. **Open it before the code ships** | Multi-tenant SaaS with untrusted tenants. **E2B rejected permanently**: the filing would leave our boundary — a data-residency conversation about regulated filings we should not have to have |
| 32 | Sandboxing — evaluator tier | **An ordinary process. CEL is terminating, side-effect-free, has no I/O and binds two names: the language *is* the sandbox.** Plus a step-count budget and a wall-clock kill | Pyodide / WASM; RestrictedPython | **WASM-of-CPython is a resource boundary, not a security boundary.** In the Grist "Cellbreak" escape (`GHSA-7xvx-8pf2-pv5g`, CVSS 9.1) a spreadsheet formula escaped Pyodide by **three independent routes**, fixed by putting Deno's permission system underneath. RestrictedPython's own docs: *"not a sandbox system or a secured environment"*. **Correction that travels with this: CVE-2026-5752 is against Cohere Terrarium, not Pyodide** | Pyodide MPL-2.0 — SECONDARY (not a boundary) | Client-side predicates: Pyodide returns as *portability* only |
| 33 | Storage and content addressing | **SQLite + `blobs/sha256/<aa>/<rest>`; sha256 over exact received bytes, lowercase hex, plus a per-sheet hash of every `xl/worksheets/sheetN.xml`** | PostgreSQL | **SQLite is a file, so it can be hashed and named in the run manifest** — exactly what the attestation needs. A Postgres cluster cannot be content-addressed. Per-sheet hashes let a re-derivation say *which* sheet changed | Public domain — SECONDARY | **A second concurrent writer exists.** That is the trigger — not row count, not volume (§5.3) |
| 34 | Attestation and signing | **DSSE + in-toto Statement v1; `subject[]` carrying the filing digest **and** the template digest; `predicateType: …/filing-settlement-attestation/v1`; local Ed25519 key, `--tlog-upload=false`** | JWS/JSF; Sigstore keyless + Rekor | `subject[]` carries the two hashes that must be bound — **a verdict against template v3 is meaningless if the entity filed on v4**. **Rekor is a public log**: a named FME's pre-submission check must never be published to it | **in-toto/attestation: Apache-2.0 — VERIFIED-AT-SOURCE** (L10 opened the LICENSE and quotes it). **cosign: Apache-2.0 — SECONDARY**, LICENSE not opened | Sigstore's public-instance logging/retention policy is opened and read. Until then keyed mode with the log off, **asserted in a test** |
| 35 | Result vocabulary | **8 states × 30 namespaced reason codes (§4.4); `override` orthogonal; `severity_tier` set by measured FFR** | `PASS/FAIL/UNCHECKED` × 6 flat reasons | Without `OUT_OF_SCOPE` the fraction is computed against the wrong denominator on every real filing (217 heterogeneous FMEs will not populate all 10 sheets). Without `ERROR`, a crashing predicate is indistinguishable from an uncheckable property. Without `no_predicate.failed_qualification` the gate's rejections are discarded | — | A code is admitted **iff it implies a different remedy** from every existing code. That test is why 30 beats 6 and why it is not 60 |
| 36 | API framework | **FastAPI 0.141.1** | Litestar 2.24.0 | **Not a performance argument.** ~18 paths over a sub-second computation; throughput is irrelevant by three orders of magnitude and the binding constraint is how fast a mentor or judge reads the code. Django-ninja rejected: it puts a migration between us and a reproducible report | MIT — SECONDARY | The team already knows Litestar |
| 37 | Job execution | **Synchronous request/response. No queue, no broker, no workers.** Offline sweeps from a `Makefile` + the Batch API | Celery / Redis / RQ | MEASURED: the deterministic core is ~30 ms; the 19,782-mutant campaign 2.5 s. **The question "do we need a queue for a sub-60-second job" does not arise for a sub-second job** | — | If in-process queuing is needed, a SQLite/Postgres job table **before** any broker |
| 38 | Frontend — the report | **One self-contained HTML file: inline CSS and JS, no external requests, server-generated** | Next.js + shadcn/ui | It opens from `file://` with the wifi down; it is phone-safe with no build target; it is **emailable**, which is how a compliance officer shares a report; and decisively **it is the attested artifact — a file has a hash, a single-page app does not** | — | Never for the report. **SvelteKit is the post-residency answer for the shell.** Streamlit/Reflex/NiceGUI rejected permanently: all bind the UI to a live session |
| 39 | Frontend — shell | **Jinja2 from FastAPI + Tailwind compiled to a static stylesheet + ~50 lines of vanilla JS** | Any SPA framework | Five screens, ≤ 515 rows in the largest table; a plain `<table>` with a filter renders 280 rows in under 200 ms | — | The registry passes ~5,000 rows |
| 40 | Deployment | **One Docker container on Fly.io (`shared-cpu-1x`, 512 MB). The laptop is the demo path and is mandatory as the fallback** | Vercel + Railway | Two targets, two failure modes; Vercel's serverless model fights a long-lived registry file and a content-addressed blob directory. **New Fly.io accounts get no free allowance** (legacy tier closed to organisations created after 7 Oct 2024, VERIFIED-AT-SOURCE) | — | A second concurrent writer or a real availability obligation |
| 41 | Observability | **The run manifest, content addressing end to end, a JSONL log (`{predicate_id, state, reason, cells_bound, elapsed_us}`), and `verify`** | OpenTelemetry / Sentry | Sub-second, single-node; tracing would be theatre. **The question a downstream reviewer asks is not "what was the p99" but "can I get this same answer again", and `verify` answers it** | — | A real user is on the system |

**Rows 10, 17 and 28 are one decision seen from three sides**, and it is the programme's thesis executed
as engineering: *where a programmatic oracle exists we do not need a model; where it does not, we
manufacture labels by seeding faults rather than by asking one.*

---

## 2. THE ADOPTED OPEN-SOURCE LEDGER

| Project | Used for | Explicitly **not** used for | Licence + commercial implication | Maintenance risk | Fallback if abandoned |
|---|---|---|---|---|---|
| **`lxml` 6.1.1** | Every authoritative OOXML read, incl. `styles.xml` (the unlocked mask that fixes the denominator) and the `extLst` block where the 19 `x14` validations live; XML hardening | Spreadsheet semantics — formulas, style resolution, shared-formula groups are all our code | BSD (SECONDARY). No obligation for a hosted commercial product | Minimal | stdlib `xml.etree` with manual namespaces; a 5× slowdown on a 28 ms parse is survivable |
| **`openpyxl` 3.1.5** | Two things: formula text with correct shared-formula row-shifting, and cached values (present on 505 of 505 formula cells). Offline: writing mutant workbooks | **Hard rule with a test:** schema derivation, validations, defined names as authority, and **re-serialising the artifact anywhere**. Round-trip destroys **98.2% of bytes (3,663,391 → 65,877)** and every `x14` validation — **if the pipeline ever re-serialises, the hash we attest is a hash of something that is not the filing** | MIT (SECONDARY). Clean | Low — it is the ecosystem default, which is why its blind spot is our best demo material: the failure is not ours and needs no defence | ~80 lines of `si`→master translation over lxml. **Mutation-test it first; the row-shift is the part that silently goes wrong** |
| **`celpy`** | Evaluating the admitted CEL subset under a step-count budget | Anything outside the admitted grammar: nested comprehensions, `filter()` outside `witness`, `map()` outside `sum()`, protobuf, `bytes`, `uint`, `type()`, `dyn()`, excluded by an AST walker at admission. **Nested comprehensions are the only route to exponential blow-up the CEL spec names** | Apache-2.0 (SECONDARY). Clean, patent grant included | Moderate and named. **Publishes no CEL conformance claim (NOT-FOUND on its repo page)**, and our absorption guard depends on error semantics | `cel-expr-python`, which wraps the official CEL C++ and inherits conformance, at the cost of a C++ build. **Run the conformance suite against both and record which one the registry root was qualified against** |
| **`SQLite`** | Registry, run manifests, run rows, template records, snapshot index, watch log — one hashable file | Blob storage: blobs are files, so anyone can diff, rsync and hash them without our code | Public domain (SECONDARY). No obligation of any kind | None worth modelling | Postgres on the named trigger; §4.2 is portable SQL for exactly that — no SQLite-only types, no `WITHOUT ROWID`, no JSON1 dependency |
| **`FastAPI`** | ~18 paths, one SSE surface, generated OpenAPI | Background work, scheduling, orchestration | MIT (SECONDARY) | Low | Litestar — a mechanical port; nothing in the domain layer touches the framework |
| **`Z3`** | **The proof arm of gate G3 only**; its model is the non-degeneracy witness and enters the library as evidence | Evaluating predicates against filings — that would put a potentially non-terminating tool into a terminating pipeline | **MIT (SECONDARY — the LICENSE was not opened by any lane). Open it before shipping** | Low | The empirical control arm, which runs regardless. **Losing Z3 costs the proof and the witness, not the gate** |
| **`Hypothesis`** | Driving the relation set; every real defect pinned as an `@example` | **Generating relations.** It generates *inputs*, never *properties* | **Reported MPL-2.0 — SECONDARY, LICENSE not re-read. Read it before adoption**; file-level copyleft would be acceptable unmodified | Low | ~150 lines of hand-rolled transformation loops; the necessary/expected split then becomes our convention rather than the library's enforcement — a real loss, so put it in a test |
| **`pandera`** | Host functions for bulk column checks (`failure_cases` gives row-level provenance free) | The predicate language, the verdict model, anything needing a third value | MIT (SECONDARY; version VERIFIED-AT-SOURCE via PyPI JSON, release date **UNVERIFIED**) | Low | Trivial — a few dozen lines per host function |
| **in-toto Statement / DSSE** | The attestation envelope and the `DISALLOW *` closed-world principle | Build-pipeline semantics. **Its standard `test-result` predicate has `passedTests[]`, `warnedTests[]`, `failedTests[]` and no `skippedTests[]` — it cannot express a test that did not run**, which is why we define our own `predicateType` | **Apache-2.0 — VERIFIED-AT-SOURCE** (L10 opened the LICENSE and quotes it verbatim) | Low | **DSSE is a 40-line spec** (PAE + a signature); sign with `cryptography`'s Ed25519. **The envelope format is the asset; the tool is not** |
| **`Docling`** (offline) | The 102-page FM Regulations and 389 native-text circulars, with typed per-element provenance | **The filing.** All nine workbooks contain **zero embedded images** (`xl/media/` empty, 9 of 9, MEASURED) — no model touches the primary artifact. Also not clause identity | MIT (SECONDARY) | Low; IBM-backed | PaddleOCR-VL or Marker, at a documented cost; neither publishes an equivalent typed cell-level provenance contract. The corpus is static — a one-time re-parse is affordable |
| **`PaddleOCR-VL`** (offline) | The 10 of 399 scanned circulars | The 389 native-text ones | Apache-2.0 (SECONDARY) | Low | Any OCR, or carry `declared_gap: 10/399 sources unread` on every predicate resting on the full-text negative result |
| **`mutmut` 3.7.0** (offline) | Mutating **our own code**: host functions, schema inducer, CEL profile checker — where the silent failures live | Gate G2. **Our mutants are filings, not programs** | BSD-3 (SECONDARY); a dev tool, not a runtime dependency | Low, irrelevant | `cosmic-ray` (MIT). The comparative study favouring it was **not opened — UNVERIFIED** |
| **`crepes` / `MAPIE`** (gated) | Mondrian bookkeeping and the **`OnlineMartingaleTest`** — the instrument that makes the system **refuse to certify** when the population has drifted from the calibration set | **Anything on the workbook path.** MEASURED: **0 of 3,755 unlocked cells are ambiguous under the address key**; 154 (4.10%) under a header-anchored key. **There is no learning problem in the workbook** | BSD-3 both (SECONDARY). TorchCP (LGPL-3.0) rejected on that basis | Low | Split conformal is ~15 lines. **Non-negotiable rule that travels with them: the exchangeable unit is the FILING, not the cell** — report `n = F` beside every number |
| **`PuLP` + CBC** (offline) | Registry-minimisation ILP and the subsumption DAG, at admission | Anything at run time | PuLP MIT / CBC EPL-2.0 (SECONDARY); invoking the solver binary imposes nothing | Low | Greedy set cover with the same constraints, **reported as greedy** |
| **LibreOffice** (offline) | Third reader at template admission; second engine in the observability filter. **Pinned by container digest** | **The verdict path; the artifact we attest over; the normalising authority** | MPL-2.0 (SECONDARY); subprocess use imposes nothing | None | Our evaluator alone, with the observability filter reported as single-engine — a strictly weaker instrument, and the experiment report must say so |
| **`Daikon`** (offline) | Baseline B1; one row per filing, one column per stable key, `--conf_limit 0.99` | Production synthesis — its output goes through the identical gate as a model's | MIT-equivalent (SECONDARY — licence text not opened) | Low | None needed. **It earns its place because it emits trivia — in one published study 27 of 40 correct invariants were "pointer not null" — and the trivia *is* the degeneracy list** |
| **`cosign`** | DSSE construction and Ed25519 signing in **keyed mode** | Keyless signing; **never** the transparency log (`--tlog-upload=false` asserted in a test) | Apache-2.0 — **SECONDARY**; its LICENSE was not opened (the in-toto LICENSE that *was* opened is a different repository) | Low | `cryptography` Ed25519 + 40 lines of DSSE |

**The projects whose licence is not established, named plainly.** **gVisor — NOT-FOUND**, and it is the
parser sandbox; the fallback is plain `seccomp` + namespaces, a weaker boundary that would have to be
disclosed. **Hypothesis — reported MPL-2.0, not re-read.** **`cobalt`/`indigo` — NOASSERTION**, so we
implement the URI grammar and adopt only Indigo's data model; **`bluebell` is GPL-3.0, VERIFIED, and must
never be linked.** Two more must be opened before the code ships: **Z3's**, and **`xbrl.us/dqc-license`** —
if the latter is permissive, the XBRL US DQC rule corpus is the only ready-made financial-filing
evaluation set found anywhere in this research.

---

## 3. THE BACKEND FLOW

Two clocks. The **online** path runs per filing and makes **no model call**. The **offline** paths run per
template version, per regulation version, or on a change signal. The relation layer is **a loop over the
online path on transformed inputs, not a stage after it**, and relations route **through** the
qualification gate like any other predicate.

### 3.1 ONLINE — fifteen steps, F0 to F14

| Step | In → Out | Det. | Failure handling | Human | ⏱ | Status |
|---|---|---|---|---|---|---|
| **F0 RECEIPT** | bytes → `filing_sha256` over the **exact received bytes**, blob, `run` row | total | over the cap or non-zip → `413`/`415`, **no run row**. There is no partial run | no | ~10 ms D | BUILT |
| **F1 CONTAINER GUARD** | digest → pass or `INVALID` | total | zip entry count, per-entry uncompressed size, total ratio, media types, required parts — **all before any XML is parsed**. Any trip → `INVALID` with the **run-level** cause `invalid.container_guard_tripped` (see §III.4.4.1 — run-level causes are a separate closed vocabulary from the item-level 8 × 30, because a guard trip is not a property of any cell). **Not a FAIL: a filing we could not safely open is not a filing that failed a check** | triage | <5 ms D | SPECIFIED |
| **F2 DUAL-READER INGEST** | digest → `RawWorkbook` + extraction manifest | given pinned versions | A (lxml, structure) and B (openpyxl, formula text and cached values) are compared on `n_sheets`, `sheet_names`, `hidden_sheets`, `n_cells`, `n_formula_cells`, `n_validations`, `n_defined_names`, `merged_ranges`. **Disagreement on sheets, names or hidden state → `INVALID`** — the scope is not established. Elsewhere → those fields are marked and every predicate reading them returns `NOT_RUN(extractor_disagreement)`. **No third reader is called online** (§7 G12) | triage | ~230 ms M | PARTIALLY BUILT |
| **F3 TEMPLATE BINDING** | `RawWorkbook` → `template_sha256` + `TemplateSchema` | total | Binding is by **structural fingerprint** over `(sheet names + states, dimensions, merged-range set, defined-name list, unlocked mask)`. **Formula content is deliberately excluded** — otherwise a filer who overwrote a formula with a literal would fail to *bind*, and formula-override must surface as a **predicate failure**, not a binding error. No match → `INVALID` with `NOT_RUN(template_unbound)`, **which escalates**: it is also the signal that a new template version was published | **yes** — new version, superseded, or corrupt? | <1 ms D | SPECIFIED |
| **F4 FACT TABLE** | `RawWorkbook` + `TemplateSchema` → the two-document fact model | total | Two top-level names bound: `filing` and `template`. No clock, no network, no filesystem. **Vocabularies always resolve against `template`, never `filing`** — the `Dropdown` sheet is hidden **and the only unprotected sheet**, and sheet protection is an application flag anyway (**assume the filed artifact is fully mutable**). Every leaf carries `__cell__`. Money is scaled to `MILLI_USD_MILLION` here, once | no | 1 ms M | BUILT |
| **F5 ATTACHMENT EXTRACTION** | attachments + `stable_keys()` → `Fact{…, warrant = MODEL_EXTRACTED}` | **no — model-bearing** | **Skipped entirely when there are no attachments, which is normal; marginal model cost then exactly $0.00.** Three guards: (1) `key` typed `Literal[*L1_KEYS]`, so off-schema keys are *ungeneratable*; (2) post-hoc deterministic rejection — kept though redundant, **because this is the one you can prove to an auditor**; (3) conformal abstention (gated) — abstain unless the set is a singleton; an empty set maps to `INDETERMINATE(extraction_abstained)`. **Retry banned.** Model or network error → `NOT_RUN(source_unreadable)` | no at run time | seconds | SPECIFIED/GATED |
| **F6 PREDICATE SELECTION** | template digest + pinned registry root → `ACTIVE` / `PROVISIONAL` | total | A predicate qualified against a different template **is not evaluated**; its cells land in `NO_PREDICATE(not_yet_requalified)`. A `PROVISIONAL` predicate **still runs**, so detection is not lost, but its numbers are hidden and its cells are **not counted as settled**. An empty active set is not an error — it is an honest report with `settled.total = 0` | no | <1 ms D | SPECIFIED |
| **F7 PRE-FLIGHT** | declared `schema_keys` (machine-checked against the AST at admission, so exact and not an estimate) + fact table → `PROCEED` or `NOT_RUN(source_unreadable: <key>)` | total | **The structural mitigation for CEL's documented error absorption.** The spec says that for `&&`/`\|\|`, if one operand determines the result, an error in the other *"will be ignored"* — so `true \|\| <error>` yields `true`. Pre-flighting every declared key **before evaluation begins** makes the guard independent of how the predicate was written | no | sub-ms D | SPECIFIED |
| **F8 EVALUATION** | active set + fact table → one `run_check` row per predicate | total | The five-rule contract below, which lives in exactly one file, `EVALUATION-CONTRACT.md` (§7 G5) | no | sub-ms for 227 arithmetic predicates M | BUILT |
| **F9 RELATION PROBES** | fact table + admitted relations + pinned template → per relation `PASS`/`FAIL`/`INFORMATIONAL`/`OUT_OF_SCOPE` | total | **A loop over F4–F8 on transformed fact tables.** 25 relations, all oracle-free: 15 need the filing alone, 4 the versioned blank, 3 two consecutive filings, 1 multiple instances, 2 are checker self-tests never shown to the filer. Each carries a **degree map** (money = 1; counts, dates, ratios, categoricals = 0), a **necessary/expected flag**, and a **non-degeneracy precondition** — because an all-zero filing satisfies partition relations trivially. Violated *necessary* → FAIL with both value sets as witness; violated *expected* → `INFORMATIONAL` carrying the guidance note that makes the exception lawful | no at run time | ~160 ms D | SPECIFIED |
| **F10 SEEDED CANARIES** | each admitted predicate's stored `kill_case` + this filing's fact table → `canaries_passed`, or dead predicates and `INVALID` | total | Instantiate the fault each predicate is *known to detect* against **this filing's cells**, re-evaluate, confirm it fires. Catches parser drift, selector misses, renamed sheets, hidden-sheet truncation, encoding changes, empty-set vacuity — **for this file** | **yes on failure.** A silent canary is an engineering incident, not a filing outcome | ~35 ms D, from 7,946 mutants/s M | SPECIFIED |
| **F11 SETTLED FRACTION + CLOSURE** | every field-surface cell + every state → the settled-fraction object (§4.3) | total | The denominator is the **field surface** from `styles.xml` (`cellXfs → <protection locked="0"/>`) — **3,747 for the FME workbook (MEASURED, L14 §1.12)**. It is **computed twice by two independent readers and the run is `INVALID` if they disagree**, because when numerator and denominator come from one wrong parser the ratio is still plausible and the error is invisible by construction. A test asserts the denominator comes from the unlocked mask and **never from the predicate set** — that mistake was made twice in one afternoon by the person who knew about it. **A cell landing in no bucket aborts report generation** | no | <5 ms D | BUILT (denominator) / SPECIFIED (closure) |
| **F12 AGGREGATE VERDICT** | settled-fraction object + `pervasiveness-policy-v1.json` → one verdict state | total | `residueIsConfined := (unsettled cells touch ≤ K sheets) AND (no unsettled cell is material-by-policy) AND (unsettled/inScope ≤ T)`. **`K` and `T` render `PLACEHOLDER` until the argument that sets them exists** (§7). 2×2: failures × confined → `EXCEPTIONS_NOTED`; failures × pervasive → `ADVERSE`; none × confined → `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE`; none × pervasive → `SETTLEMENT_INSUFFICIENT`. **No state's name means "clean"** | no | <1 ms D | SPECIFIED |
| **F13 REPORT + ATTESTATION + LOG** | → `report.html` (self-contained, opens from `file://`, no green tick), `attestation.json`, `run.jsonl`, plus **declared-lossy** OSCAL AR / POA&M / RO-Crate projections | total | The manifest is embedded in the report footer where a human can read it. **A closure violation or a no-green-tick gate failure aborts report generation. There is no degraded report** | no | ~20 ms D | PARTIALLY BUILT |
| **F14 `verify`** | report or attestation + the blobs it names → `REPRODUCED` + byte comparison, or a diff | total | Re-runs the pipeline from the embedded manifest at the pinned registry root, template, register snapshot and tool versions. **The programme's acceptance test: a third party clones the repo, runs `verify` on another machine, and gets a byte-identical re-derivation. If it does not reproduce, it does not ship** | no | = full pipeline | SPECIFIED |

**F8 — the evaluation contract, corrected. The word `UNCHECKED` appears nowhere in it**; it was a state
the vocabulary retired and the drafts kept quoting.

```
1.  Evaluate P.applicable
      error -> NOT_RUN(not_run.source_unreadable)        [never FAIL, never PASS]
      false -> OUT_OF_SCOPE(P.reason_if_inapplicable)    [never PASS]
      true  -> continue
2.  Pre-flight (F7) already ran; any missing/mistyped declared key ->
      NOT_RUN(not_run.source_unreadable: <key>) and expr is never evaluated.
3.  Evaluate P.expr under a step budget and a wall-clock kill
      budget exceeded -> NOT_RUN(not_run.budget_exhausted)         [never FAIL]
      runtime error   -> ERROR(error.predicate_raised), run := INVALID
                         -- a predicate that RAISED is an apparatus failure, not an
                            unreadable source; NOT_RUN(source_unreadable) is reserved
                            for inputs we could not read
      false -> FAIL, then evaluate P.witness for the cell list
      true  -> PASS
4.  Provenance composes by WEAKEST INPUT:
      warrant := min over every fact the AST read, DETERMINISTIC > MODEL_EXTRACTED > DERIVED
      retrieved_at := max over inputs
      -- never fresher than its stalest input, never stronger than its weakest.
5.  cells_bound == 0 -> ERROR(error.cells_bound_zero), run := INVALID
      -- binding to nothing is never a PASS.  Demoting this to NOT_RUN would put the
         vacuous-pass failure mode in the same bucket as a rate-limited register.
```

**Rule 3 is the whole product in four lines**: everywhere a conventional framework turns doubt into a
failure (`success = False`) or into silence, this turns it into a counted, reasoned, reported
non-settlement. **Rule 5 kills the four likeliest silent failures at once** — vacuous pass (`all([])` is
`True`), empty-set arithmetic, selector drift, scope truncation.

**Three run states.** `VALID`: the pipeline ran, the checker demonstrated liveness on this artifact, and
closure holds. `INVALID`: **the system could not demonstrate it was working here** — set by an F1 guard
trip, F2 structural disagreement, F3 unbound template, F8 `cells_bound == 0`, F8 predicate raised, F10
silent canary, F11 closure violation or denominator disagreement. `REJECTED`: the submission never became
a run. **An `INVALID` run renders a report that states why and carries no settled fraction at all**; the
verdict is `null`, not `SETTLEMENT_INSUFFICIENT`, because the latter is a finding about the filing and
this is a finding about us.

**What F10 claims, at full strength.** *No assurance artifact in existence carries evidence that the
instrument that produced it was working on the specific document it examined. A clean audit opinion does
not. An SBOM does not. A validation report does not. Ours refuses to issue a verdict unless every check
has just demonstrated, on your file, that it can still catch the fault it was admitted for.* That is
falsifiable, claims no novelty for the mechanism (two extra executions per predicate), and needs no
citation.

### 3.2 OFFLINE A — template admission and predicate harvest

**T1 Fetch** the published URL → bytes + `template_sha256` + timestamp and origin URI; **a changed hash at
an unchanged URL is a version event, not an error**. **T2 Triple-read** — as F2 *plus* the digest-pinned
LibreOffice reader, available here because this path is offline; **any structural disagreement blocks
admission**. **T3 Induce schema** (deterministic, **28–44 ms MEASURED**) → `TemplateSchema{formulas 505,
validations 54, vocabularies 15, unlocked_mask, field_surface 3747, stable_keys, carry_table 195 edges}`;
a construct not understood is recorded in the manifest and its fields are excluded from `in_scope` **with
a stated reason**, never silently dropped. **T4 Harvest** → **280 executable predicates for the FME
workbook, zero model involvement (MEASURED, L14 §1.9)**: `cross_sheet_equality` 181, `sum_identity` 35,
`membership` 20, `numeric_bound` 13, `integer_bound` 11, `same_sheet_equality` 11, `date_bound` 6,
`tally_identity` 3, `conditional_required` 0. This step cannot fail, only under-produce. **T5
Function-vocabulary check** — an unimplemented function makes those cells `NOT_RUN(source_unreadable)`, or
the pinned second engine is promoted for this template and its disagreement rate published; **a human
decides**. **T6 Stable keys** `= (sheet_name, merged_header_path, row_label)`, coordinates a *resolved
attribute*; an unresolvable key enters `UNRESOLVED` and **blocks** its predicates rather than silently
binding to the wrong cell. **T7 Register** — **a human signs the admission, because this fixes the
denominator every subsequent number is a fraction of.**

**Why T4's 20 membership predicates matter more than their count:** they take the workbook from **3
enforced controlled vocabularies to 20** with no model at all, and one of them — `'3. Portfolio'`
instrument-type over `I116:I126` and `M116:M126` — covers **210 cells with a two-value vocabulary**. *The
check was already latent in the artifact; nobody had extracted it.*

### 3.3 OFFLINE B — clause-graph induction (L1b)

389 native-text circulars → Docling; 10 scanned → PaddleOCR-VL, frozen once and content-addressed; both
into a **deterministic promoter** (numbered headings → `<section>`; `(1)/(a)/(i)` → nested `<paragraph>`;
"Provided that" → `<proviso>`) → Akoma Ntoso with `eId` per clause and an FRBR URI per instrument, plus a
dated cross-reference extractor and an amendment graph. Recall is checked against a declared denominator —
the measured **8,866 `shall` occurrences across 361 circulars**; a promoter that loses `shall` clauses is
losing obligations and the count is the regression test. **90 of 389 circulars amend an earlier
instrument; 76 of 82 amending circulars cite a resolvable target (92.7%, MEASURED).** An unpromotable
region is recorded with its page span and every obligation inside it is `NO_PREDICATE(rule_ambiguous)`
until a human promotes it. **Status: SPECIFIED. Nothing of L1b is built** — which is why the obligation
table is hand-maintained on day one (§4.2).

### 3.4 OFFLINE C — candidate proposal

**The rename is substantive:** this is candidate *proposal*; the gate is *admission*. Every measured system
in this literature that works, works because a rejector exists; every one that fails, fails because the
rejector was absent or fake. **The gate is the rejector and it is the actual product.** In: the
`TemplateSchema` as an explicit I/O constraint, the clause unit with its `eId` and FRBR URI, and the
template's own 505 formulas as an **available** criterion source. Out: candidates in the envelope format,
each carrying its clause locator, exact character span, an enumeration of every proviso in that span, and
a rationale. Model: `claude-opus-5`, Batch, cached prefix, offline, once per template version, never in a
request path. **Determinism: none, and it does not need any** — a weaker model proposes more rejects; it
cannot smuggle an unqualified predicate past a gate that requires a measured kill rate and a measured FFR.
A malformed candidate is discarded and counted: **the discard pile is data** and appears in the attrition
funnel.

**The I/O-constraint intervention, corrected.** Feeding an induced schema in as an explicit I/O constraint
is the dominant lever on **structural similarity (+37–54 percentage points)** in the only published study
of statute→executable-model generation (arXiv:2604.17153, VERIFIED-AT-SOURCE via L04 §2.13); **that
study's *outcome* equivalence tops out at 51–53%**, and its own caveat is that structural similarity does
not guarantee outcome equivalence, or the reverse.

**And the criterion-source claim, restored.** SPADE infers what correctness meant from the traces of a
developer changing their mind, because in a software pipeline nothing else records it. **We do not have to
infer it: the criterion is a published instrument with a version, an amendment chain machine-followable in
76 of 82 cases, and a blank template with a content hash.** It is not more *authoritative* than SPADE's —
the regulator's own template computes a scheme total that misses two of its own nine legal values — it is
**citable, versionable and watchable**, which is precisely what lets a predicate be tied to a clause,
re-qualified when the clause moves, and quarantined the day a circular changes the rule. §3.6 implements
it, and no draft stated it as a contribution.

### 3.5 OFFLINE D — qualification. **Five gates, in this order**

`G0 (free) → G1 (free) → G3 proof arm (cheap) → G2 (expensive) → G3 empirical arm → G4.` Nothing expensive
runs behind something free, and a predicate Z3 proves unfalsifiable never consumes a mutation budget.

- **G0 scope faithfulness.** The candidate carries the exact character span of the clause it implements,
  `source.find(quote)` succeeds deterministically, and every proviso, exception and cross-reference in that
  span is **either implemented by a branch or emitted as `NO_PREDICATE(no_predicate.not_yet_synthesised)`
  carrying the proviso's verbatim text and character span**, with `provisos_declared` recorded. Neither ⇒
  reject. Models ground spans well (SpanFaith 0.77–0.79) and wire exception structure badly (Edge-F1 ≈
  0.22), and our instrument is full of provisos — **reg 51(1) ends "in such manner as specified by the
  Authority"**, a live delegation hook.
- **G1 executes and binds.** Runs without error, every key exists in the induced schema, **`cells_bound >
  0`**. Nearly free and proves nothing alone — which is exactly why it is separate. **It is the condition
  whose absence produces the vacuous pass.**
- **G3 proof arm.** Z3 as above; `unknown` is **unproven, never "non-degenerate"**.
- **G2 seeded-defect kill.** `KR = K/O` over mutants **verified observable by recalculation**, plus the
  per-fault-class vector and `UR = U/G`. Seeding targets the fields `schema_keys` reads **plus a 10%
  control sample of fields it does not** — without the control arm a flag-everything predicate scores
  perfectly. Mutants are made by **raw-zip surgery** (copy every part byte-for-byte, rewrite one worksheet
  XML; MEASURED: one part differs, the 3.55 MB data model and all 19 `x14` validations survive
  byte-identical). The **observability filter** decides whether a kill rate means anything: recalculate,
  diff the value grid, **discard mutants no cell value distinguishes**. Expected discard is high —
  **3,512 of 7,500 (46.8%)** on a comparable operator suite — **and we report our own figure every run,
  because it is a property of our operator mix and must not be assumed.**
- **G3 empirical arm.** Spurious firing on the control sample below threshold; flags ≤ 50% of the clean
  corpus; not equivalent to a published degeneracy-list member. SPADE's own paper: taking every candidate
  yields 100% settled at 100% FFR.
- **G4 false-failure rate.** `FFR ≤ 0.10` with `n`, a Wilson interval, `corpus_provenance ≠
  SELF-AUTHORED`, a structurally distinct held-out slice reported separately, and the **marginal** FFR
  under `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)`. In two of SPADE's nine pipelines, assertions
  that each individually met the budget composed to **88%** and **53%**.

**Two thresholds, and they are different tests — the drafts stated them as one.** The settling experiment
asks *"can this candidate fire at all, and does it beat the free baselines"* — `K/O > 0` plus marginal
kill strictly greater than `B0 ∪ B1 ∪ B2`. **The registry admits at `K/O ≥ 0.80` on the fault classes the
predicate claims to cover.** Both are stated; the two attrition numbers are reported separately.

**FFR corpora, ranked; every FFR carries which one produced it.** `BLIND-FILLED` (Person A fills from
template and regulation only, never having seen the predicate set; Person B authors predicates never
having seen A's workbooks) — **an FFR that *can* be non-zero, therefore one that carries information, and
the minimum bar below which no FFR may be printed anywhere in the product**. `TEMPLATE-COMPUTED` — fill
the inputs and let the workbook's own 505 formula cells compute the rest; **a predicate that fires on a
cell IFSCA's own artifact computed is a genuine false failure, because the regulator authored the ground
truth**; ready today. `REGISTER-DERIVED` — **MEASURED**. `REAL-PARTNER` — needs a partner we do not have;
`n` will be tiny and that is fine if reported as an interval. `SELF-AUTHORED` — **renders as `—` and the
word `uninformative`. Not a number. The schema forbids it.**

**What `REGISTER-DERIVED` licenses, precisely.** Every entity in the register is validly registered, **so a
predicate asserting *membership* cannot have a true positive there** — the register licenses an FFR for
the membership predicate only. A predicate asserting *format* can: the regex any competent engineer would
write after five examples, `^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$`, **fires on 87 of 228 live FMEs — a
38.2% false-failure rate, MEASURED, denominator 228 live FMEs resolved via the detail endpoint, 10 Aug
2026 (L08 §C.3)**. Two incompatible identifier schemes are live in the same register on the same day (141
legacy, 84 new, 3 neither), and one of the three carries a `U+2011 NON-BREAKING HYPHEN` homoglyph —
visually identical, byte-wise different, invisible in any screenshot. **The admitted predicate is
therefore set membership against a snapshotted register under a declared normalisation (NFKC, `U+2011 →
U+002D`, strip, case-fold), never a format grammar.**

**And the design's own sentence must be corrected.** *"A check whose error rate is unknown is not admitted
— which makes the coverage claim true by construction"* becomes: **the settled-fraction claim is true to
the extent the admission measurements are valid, and each predicate carries the provenance of its own
measurement.** Longer, weaker, defensible.

### 3.6 OFFLINE E, F, G — admission, re-qualification, and the watcher that quarantines a moved clause

**Admission (R1–R7).** R1: the AST walker enforces the grammar and **verifies `schema_keys` against the
AST both ways** — a predicate reading an undeclared key, or declaring one it does not read, is rejected;
**this is what makes the settled fraction computable rather than estimated**. R2: host-function references
checked against the closed registry. R3: the ILP selects a minimal set; the Z3 subsumption DAG removes
implied predicates. R4: **liveness witnesses stored with the predicate** — a `kill_case` (a mutant it is
known to reject) and a `pass_case`; F10 replays the `kill_case` on every filing. R5: append-only;
supersession is a new row. R6: the **registry root** — a Merkle tree over sorted `code_sha256`, leaf
`sha256(0x00 ‖ h)`, internal `sha256(0x01 ‖ l ‖ r)`, odd node promoted; **domain separation is not
decoration**. R7: **a human signs the batch** — the gate is mechanical, shipping a check that will be
applied to a regulated filing is not. **A predicate whose `qualification` block is absent does not load**,
and a test attempts the admission and asserts the rejection. Every rejection records the gate, the measured
number, the cells it would have covered and the obligation it claimed — that record *is*
`no_predicate.failed_qualification` and the `counterEvidence` array. **We were going to discard exactly
the information an audit-documentation standard makes mandatory.**

**Re-qualification is live, not hypothetical.** The FME workbook is dated 02 Jan 2026; the FM Regulations
are consolidated as amended to 30 Jan 2026; and the **29th IFSCA Authority Meeting of 24 Jul 2026**
decided that NAV periodicity for close-ended Restricted Schemes *"may be enhanced by the FME from
semi-annual to annual, subject to prior approval of at least 75% of the investors in the scheme by value
of their investments"* (VERIFIED-AT-SOURCE). The owed frequency now depends on **a fact the workbook does
not collect**. The predicate neither errors nor abstains — it keeps computing a date difference against a
rule that no longer exists: **a filer who lawfully moved to annual gets a false failure; a filer who moved
without approval gets a silent pass. Both outputs are clean, confident and well-formed.**

Seven rules. (1) **Keys are label-anchored, never coordinate-anchored**; a version bump is a
re-resolution, not a rewrite. (2) Every predicate carries a `qualified_against` record **as part of its
identity** — template digest and label, regulation version, circular snapshot, count of unreadable
circulars, corpus id and provenance, `n`, harness and evaluator versions, and for proposed predicates the
model id, date and prompt hash, **so a re-synthesis under a drifted model is a diff and not a mystery**.
(3) Any change to any element moves the predicate to `PROVISIONAL`: it still runs, its numbers are hidden,
and it does not count in the settled numerator. (4) **Therefore the settled fraction falls when the world
moves**, and the chart must be able to step down — **the step-downs are the most credible thing on it,
because they are the only evidence the system notices when the world moves**. (5) Liveness witnesses are
re-run on every version change and every filing; a predicate whose `kill_case` no longer dies is
quarantined automatically — **but this alone cannot catch a rule change**, because the mutant and the
predicate move together, which is why rule 6 exists. (6) **Watch the instrument stream, not just the
instrument**: a daily content-hash of the circular list, Authority-meeting page and download page, diffed
against the last snapshot; any new instrument citing a regulation a predicate claims to implement puts
that predicate into `PROVISIONAL` **automatically and pessimistically**, only a human clears it, and **the
watcher never re-admits**. A fetch failure is recorded as **a gap in the watch log with its duration**,
never as "no change" — an unobserved day is not a quiet day. This is diff-and-flag, not NLP, and **it is
the only mechanism that would have caught 24 Jul 2026**. (7) Carry the 10 unreadable circulars as a
permanent declared gap — or OCR them, which is an afternoon.

**One version event is already on the calendar:** `Dropdown!$E$3:$E$6 = {2025-26, 2026-27, 2027-28,
2028-29}`. **The workbook cannot express FY2029-30.**

### 3.7 OFFLINE H — the residue set

Take the filing `F`; generate mutants under a declared, versioned fault model; adjudicate each INNOCUOUS
or WRONG (**the only human step**); run the full admitted predicate set and all admitted relations over
every WRONG mutant; `RESIDUE := {WRONG mutants nothing rejects}`; report `|RESIDUE|` and each survivor's
class of falsehood. **It cannot be inflated by boring checks** — adding 505 recompute predicates does not
shrink it, because the residue is populated by falsehoods consistent with every arithmetic relation in the
file. It **makes 100% structurally unreachable**, because the count is never zero and it is a permanent
row in the denominator. It is **reproducible given the published fault model *and the published
adjudication record*, both content-addressed.**

**The class it names, at full strength.** A prescribed return is a closed arithmetic system. **We can
construct, and exhibit, a family of filings that are internally perfect under every relation the
regulator's own template encodes and every relation we have added — and materially false.** In code
mutation testing a mutant that changes behaviour is in principle killable by *some* test; here a mutant
can change the **truth** of the artifact and be **provably unkillable by any predicate over the artifact
alone**. That family is non-empty by construction, its size is measurable, and measuring it is the first
quantitative statement anyone has made about the limit of document-level verification for a regulated
filing. It follows that *"the residue set comes back empty"* is not a Low risk; **it is structurally
impossible.**

### 3.8 Where a human is required

Template admission sign-off (fixes the denominator); the function-vocabulary decision; promoter failures
and the 6 of 82 unresolved amendment chains; **host-function authoring — added only by a human, never
generated by a model**; relation authoring; **blind-fill corpus construction, which is both the
measurement and the expensive input**; the admission batch signature; clearing a `PROVISIONAL` flag;
INNOCUOUS/WRONG adjudication; `INVALID` triage; override entry (both states retained, inside the signed
payload; the override count is reported separately — a downstream reviewer will want it); and the
pre-registered go/no-go on candidate proposal, **recorded on the date it was taken, whichever way it
goes**. **Nowhere here does a human adjudicate a PASS. The verdict itself is never negotiated.**

---

## 4. THE DATA MODEL

### 4.1 Content addressing

`sha256` over exact bytes, lowercase hex, at `blobs/sha256/<aa>/<remaining-62>`. No compression, no
re-encoding, no normalisation: **the bytes we hash are the bytes we received.** Canonical serialisation
for every hashed JSON object is **RFC 8785**, stated explicitly because *"the sha256 of the JSON"* is not
a definition and two implementations that disagree on key order produce two roots for one registry.
Content-addressed and named in the run manifest: the filing; **each worksheet inside it**, so a
re-derivation can say *which sheet* changed; the blank template; the `TemplateSchema`; each predicate,
host function (source + test-vector result) and relation; the registry root; each regulation PDF; the
**register snapshot** (the register is mutable and undated — a verdict citing "the register" without a
snapshot hash is not reproducible and cannot be signed); each mutant; the per-template engine-disagreement
set; and the report.

### 4.2 Tables — and the decision that the unit is the cell

**DECIDED.** The unit of the denominator, of closure and of the settled fraction is the **filer-editable
cell**; `obligation` becomes a **predicate attribute**, not a denominator axis. It beat the
`(field × obligation)` pair on one fact: every measurement in this corpus is a cell count (**2,373 settled
of a 3,747-cell field surface, MEASURED, L14 §1.12**), while the pair model has no published enumeration
rule anywhere — the drafts' figures came from an illustrative JSON block that never claimed to be a
measurement. **Consequently no total over obligations and no total over pairs appears in this
specification, in any schema or in any example.** Obligation identity comes from a hand-maintained
`obligation` table (`source='hand'`) because nothing of L1b is built; it flips to `source='l1b'` the day
the clause graph produces `eId`s. Two run tables follow, and the split is what makes closure one SQL
statement.

```sql
blob(sha256 PK, n_bytes, media_type, first_seen_at, origin_uri, retrieved_at)
template(template_sha256 PK, label, published_at, fetched_at, origin_uri,
         structural_fingerprint, admitted_at, admitted_by, superseded_by NULL)
template_sheet(template_sha256 FK, sheet_index, sheet_name, sheet_state, sheet_sha256,
               protected, dimension, PRIMARY KEY(template_sha256, sheet_index))
field(template_sha256 FK, stable_key, sheet_name, merged_header_path, row_label, resolved_ref,
      dtype, unit,                 -- MILLI_USD_MILLION | COUNT | DATE | TEXT | ENUM
      is_unlocked, is_formula, in_field_surface,
      resolution_state,            -- RESOLVED | UNRESOLVED
      PRIMARY KEY(template_sha256, stable_key))
vocabulary(template_sha256 FK, vocab_key, source_ref, terms_json, term_count, wired_by_validation)
validation(template_sha256 FK, seq, namespace,      -- 'main' | 'x14'
           type, sqref, formula1, resolved_vocab_key NULL, cell_count)
carry_edge(template_sha256 FK, src_ref, dst_ref, formula_text, encoding)
           -- TEXT | SHARED_MASTER | SHARED_DEPENDENT | ARRAY
engine_disagreement(template_sha256 FK, cell_ref, our_value, lo_value, lo_container_digest,
                    measured_at, PRIMARY KEY(template_sha256, cell_ref))
           -- computed OFFLINE; the online path reads this table, never LibreOffice

instrument(frbr_uri PK, title, as_at, pdf_sha256, page_count, promoter_version)
clause(frbr_uri FK, eId, text, page_no, bbox_json, charspan_json, provisos_json, xrefs_json,
       PRIMARY KEY(frbr_uri, eId))
amendment(source_frbr_uri, target_frbr_uri, target_eId, effective_date, resolved BOOLEAN)
obligation(obligation_id PK, frbr_uri NULL, eId NULL, quote, span_json, source)  -- 'hand' | 'l1b'

predicate(predicate_id, version, PRIMARY KEY(predicate_id, version),
          kind,                    -- harvested | proposed | hand_authored | relation
          template_sha256, obligation_id NULL, clause_span_json NULL,
          envelope_json, code_sha256, schema_keys_json, host_fns_json,
          state,                   -- ACTIVE | PROVISIONAL | QUARANTINED | WITHDRAWN
          severity_tier,           -- BLOCKING | ADVISORY, set by measured FFR (§7 G2)
          admitted_at, admitted_by, superseded_by NULL)
qualification(predicate_id, version, PRIMARY KEY(predicate_id, version),
  g0_scope_faithful, g0_provisos_declared, g0_provisos_implemented,
  g1_executes, g1_cells_bound,
  g2_killed, g2_observable, g2_generated, g2_unobservable, g2_unreachable,
  g2_by_fault_class_json, fault_model_version, harness_version,
  g3_method,          -- z3 | empirical | both
  g3_verdict,         -- non_degenerate | trivially_true | always_flag | unknown
  g3_witness_sha256 NULL, g3_control_arm_spurious,
  g4_fired, g4_n, g4_wilson_lo, g4_wilson_hi, g4_corpus_id,
  g4_corpus_provenance,  -- SELF-AUTHORED | BLIND-FILLED | TEMPLATE-COMPUTED
                         -- | REGISTER-DERIVED | REAL-PARTNER | PUBLIC
  g4_heldout_fired NULL, g4_heldout_n NULL, g4_marginal_ffr NULL, g4_conditioned_on_json NULL,
  kill_case_sha256, pass_case_sha256, qualified_against_json, qualified_at)
-- INVARIANT enforced by the loader: a predicate row with no qualification row DOES NOT LOAD.
rejection(candidate_sha256 PK, predicate_id NULL, obligation_id, rejecting_gate,
          measured_json, cells_would_have_covered, rejected_at)
host_function(name, version, PRIMARY KEY(name, version), source_sha256, signature,
              returns_tristate, test_vector_sha256, mutation_score_json, authored_by)
registry_root(root PK, computed_at, n_predicates, predicate_ids_json)

run(run_id PK, filing_sha256, template_sha256, registry_root, register_snapshot_sha256 NULL,
    run_state,               -- VALID | INVALID | REJECTED
    aggregate_verdict NULL,  -- EXCEPTIONS_NOTED | ADVERSE
                             -- | EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE | SETTLEMENT_INSUFFICIENT
    invalid_reason NULL, canaries_run, canaries_passed,
    started_at, finished_at, manifest_json, report_sha256, attestation_sha256)
run_check(run_id FK, predicate_id, predicate_version,
          state,        -- 8 values, §4.4
          reason_code,  -- 30 values; REQUIRED iff state not in (PASS, FAIL)
          method,       -- RECOMPUTE | TIE_OUT | SCHEMA_BIND | TEMPLATE_DIFF | REGISTER_LOOKUP
                        -- | CLAUSE_TEST | DIFFERENTIAL | MODEL_EXTRACT | UNKNOWN     (nine)
          warrant,      -- DETERMINISTIC | MODEL_EXTRACTED | DERIVED  (composes by weakest input)
          provenance,   -- COMPUTED | DECLARED
          cells_bound, witness_json NULL, elapsed_us,
          PRIMARY KEY(run_id, predicate_id))
-- CONSTRAINT: method='MODEL_EXTRACT' AND state='PASS' is rejected at write time.
run_cell(run_id FK, stable_key, state, reason_code NULL, settled_by_predicate_id NULL,
         PRIMARY KEY(run_id, stable_key))
-- materialised for EVERY field-surface cell before evaluation, defaulting to
-- NO_PREDICATE(not_yet_synthesised).  Closure is one GROUP BY over this table.
override(run_id FK, stable_key, old_state, new_state, remark, actor_id, decided_at, evidence_sha256)
extraction_manifest(run_id FK, reader, parts_read_json, parts_skipped_json, namespaces_json,
                    constructs_not_understood_json, agreement_json)
register_snapshot(snapshot_sha256 PK, endpoint, fetched_at, n_records, n_requests,
                  list_response_sha256, detail_response_shas_json)
instrument_watch(observed_at PK, endpoint, content_sha256, changed, gap_since NULL,
                 predicates_flagged_json)
```

**The cell roll-up rule, stated once so ambiguity cannot re-enter.** Scope is determined first: a cell is
`OUT_OF_SCOPE` only if a scope rule with a **machine-checkable pointer to the schema condition** makes it
inapplicable, or a named run profile excludes it (and the profile digest is recorded). For every in-scope
cell the state is the maximum over the predicates that read it under
`ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`, with
`settled_by_predicate_id` naming the producer. `NO_PREDICATE` is not in the order: it is the state of a
cell whose evaluation set is empty.

> **RESOLVED (owner decision, 10 Aug 2026 — this was the audit's one blocking contradiction).** An
> earlier draft of this section ordered `PASS ≻ INDETERMINATE ≻ NOT_RUN` and concluded that *"a cell read
> by one passing and one not-run predicate is settled."* **That is withdrawn.** The order above is
> normative, it is §II.3.1's, and under it **a cell is clean only if every predicate binding it passed** —
> one `NOT_RUN` makes the cell unsettled no matter how many other predicates passed.
>
> *Why the other order could not stand:* both §II and §3.1 F2 state that when the two readers disagree on
> a field, every predicate reading it returns `NOT_RUN(extractor_disagreement)` and **"the settled fraction
> falls, it does not silently succeed."** Under `PASS ≻ NOT_RUN` that sentence is false in exactly the case
> it was written for — a passing predicate would absorb the un-run one and the fraction would hold. A check
> that did not run must never be absorbed by one that did. That is the product.
>
> *What it changes, and what it does not.* It changes the **runtime** settled count, which can now be lower
> than the static figure — which is the intended behaviour, not a defect. It does **not** change the
> harvest figure **2,373 of 3,747**: that is a static count of cells reachable by at least one harvested
> predicate, computed before any evaluation, and it is unaffected by roll-up precedence.

The not-run predicate remains visible in `run_check`: the two tables answer two different questions and
neither is derivable from the other alone.

### 4.3 The settled-fraction object — never a bare fraction

```jsonc
"settledFraction": {
  "denominator": { "source": "induced-from-template-unlocked-mask",   // NOT negotiated
                   "generatorRule": "v3", "fieldSurface": 3747, "computedTwiceAgreed": true },
  "outOfScope": 214, "informational": 38,     // both removed from the denominator
  "inScope": 3495,                            // <- THE denominator
  "settled":   { "pass": 2361, "fail": 12, "total": 2373 },
  "unsettled": { "indeterminate": 41, "notRun": 88, "noPredicate": 993, "error": 0 },
  "fraction": 0.6789,                         // meaningless without the six counts above
  "residue": { "survivors": 12, "faultModel": "v3", "adjudicationRecord": "sha256:…" },
  "declaredGaps": [ { "kind": "unread-sources", "detail": "10 of 399 circulars are scanned images" } ],
  "denominatorWarning": "Out-of-scope determinations are filing-specific, so the denominator varies
     between filings. Settled fractions are not directly comparable across filings."
}
```

*(A schema example on a hypothetical filing, not a measurement. The measured triple for the published FME
blank filled clean is **2,373 settled / 1,374 unchecked / 3,747 field surface**, MEASURED, L14 §1.12.)*

**The most important scoring decision in the design.** XCCDF removes `notchecked` from its denominator; **we
keep `noPredicate` in.** XCCDF's denominator is a benchmark a human authored, so "no check exists" means
the author chose not to have one. **Ours is induced from the regulator's own template, so "no predicate
exists" is a gap in *us*, not in the specification** — and removing it would let the fraction rise by doing
nothing. **Absent ≠ empty ≠ zero:** `[]` = *we determined there are none*; `null` = *we make no claim*; an
omitted field is a schema violation. **For an unprotected template there is no unlocked mask**, so
`settledFraction: null` and `denominator.source: "not derivable — template ships no protection mask"`;
**two of the nine prescribed workbooks are in this state.** The settled fraction is a **per-template
property and must never be averaged across templates.**

**And the number ships with the sentence that makes it honest.** 280 predicates are mechanically derivable
from the regulator's blank template with no model, and they touch 2,373 of 3,747 filer-editable cells
(MEASURED). **None of them is admitted yet**, because no false-failure rate has been measured for any of
them on a corpus we did not write — so under this specification's own admission rule the currently
admissible set is empty and the currently defensible settled fraction is 0%. **That is the point: the
number you are looking at is what every compliance product ships, and it is the number our own gate is
designed to refuse. Watch what happens to it after qualification — that delta is the product.** The
composition matters too: **2,329 of the 2,373 settled cells (98.1%) come from the 53 validation
predicates, not the 227 arithmetic ones** (MEASURED, L14 §1.12), and the validation-carried share is
weaker per cell — some of those bounds are near-vacuous, which is exactly what gate G3 exists to reject.

### 4.4 The state and reason vocabulary — frozen at 8 × 30

#### 4.4.1 Two vocabularies, not one — RESOLVED (owner decision, 10 Aug 2026)

The audit found the container guard emitting `ERROR(source_unreadable)`, a pair the frozen 8 × 30 cannot
represent: `source_unreadable` is a `not_run.*` code, and none of the five `error.*` codes fits a guard
trip. The same hole swallows two more of the eight documented `INVALID` causes — an unbound template, and
the two denominator computations disagreeing.

**The fix is not a 31st code. It is a category correction.** The 8 × 30 vocabulary is **per item**, and an
item is a cell. A container guard trip, a reader disagreement on sheet structure, an unbound template and a
closure violation are not properties of any cell — forcing them into a per-cell reason code was the error.

> **Run-level `INVALID` causes are their own closed vocabulary, `invalid.*`, with exactly the eight causes
> already enumerated in §II.6.2:** `.container_guard_tripped` · `.reader_structural_disagreement` ·
> `.template_unbound` · `.cells_bound_zero` · `.predicate_raised` · `.canary_silent` ·
> `.closure_violated` · `.denominator_disagreement`.
>
> The item-level count **stays pinned at 8 × 30** in all four places. An `INVALID` run renders a report
> naming which `invalid.*` cause fired, carries **no settled fraction of any kind**, and sets the aggregate
> verdict to `null`. Where a run-level cause has an item-level analogue — `.cells_bound_zero` and
> `.predicate_raised` — the item still carries its `error.*` code and the run additionally carries the
> `invalid.*` cause; the two are not alternatives.

**There are eight closed item states — `PASS`, `FAIL`, `INDETERMINATE`, `NOT_RUN`, `NO_PREDICATE`,
`ERROR`, `OUT_OF_SCOPE`, `INFORMATIONAL` — of which the first six are in the settled denominator and any
`ERROR` sets the run state to `INVALID`.** `PASS` and `FAIL` form the settled bucket; the other four
in-denominator states are unsettled; `OUT_OF_SCOPE` and `INFORMATIONAL` are removed from the denominator.
**Closure, seven terms, enforced not documented:**

```
outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface
```

It is the only form under which all eight states land in exactly one bucket, it is one `GROUP BY` over
`run_cell`, and **a cell that lands in no bucket aborts report generation.**

**The reason vocabulary is closed, namespaced and has 30 codes across five state families; a code is
admitted only if it implies a different remedy from every existing code.** `NO_PREDICATE` (8):
`.undecidable_by_construction`, `.requires_judgment`, `.not_yet_synthesised`, `.failed_qualification`,
`.rule_ambiguous`, `.no_obligation_specified` (**never conflate "the regulator did not legislate this"
with "we haven't got round to it"**), `.rule_withdrawn`, `.not_yet_requalified`. `NOT_RUN` (10):
`.input_unavailable.{counterparty,register,prior_period}`, `.source_unreadable`, `.template_unbound`,
`.deactivated`, `.budget_exhausted`, `.external_source_lacks_field`, `.external_source_unavailable`,
`.extractor_disagreement`. `INDETERMINATE` (4): `.extraction_abstained`, `.tolerance_straddle`,
`.conflicting_sources`, `.engine_disagreement`. `OUT_OF_SCOPE` (3): `.not_applicable` (requires a
machine-checkable pointer), `.not_selected` (requires the profile and its digest), `.withheld` (requires
an actor and rationale; **counted and displayed separately, never folded in**). `ERROR` (5):
`.predicate_raised`, `.cells_bound_zero`, `.canary_silent`, `.closure_violated`,
`.parser_disagreement_structural` — **any one sets `run_state = INVALID`.**

**Two codes carry corrections that travel with them.** `.external_source_lacks_field` means *the external
source structurally does not carry the field*; **our own near-miss is the canonical illustration and not
an instance** — the register's **list** endpoint returns `RegistrationNumber = null` on 650 of 650 fund
rows while its **detail** endpoint returns it on 228 of 228 (MEASURED, L08 §C.1, §C.3).
`.engine_disagreement` is emitted only when the cell appears in the **offline, digest-pinned
`engine_disagreement` table** for this template version — never from a live LibreOffice call.

**Severity is orthogonal to state**, not a ninth value: `BLOCKING | ADVISORY`, set by measured FFR (§7 G2),
with the number printed beside it. **`override` is likewise orthogonal**: it changes the result, retains
both states, and sits inside the signed payload.

### 4.5 How a report is proven to re-derive

The manifest embedded in every report footer pins eight things:
`{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha,
evaluator_version, fault_model_version, tool_versions:{python, lxml, openpyxl, celpy, z3}}`.
**`libreoffice` is deliberately absent, because LibreOffice is not on the verdict path** (§7 G12); the
offline artifacts it produced carry `lo_container_digest` and are content-addressed, so a quoted kill rate
stays reproducible even though the binary is not in the online pin.

| Non-determinism | Removal |
|---|---|
| The mutable register | `register_snapshot_sha256`. **The host function never resolves live at verdict time** — it resolves against a content-addressed snapshot, or the report is not reproducible |
| Wall-clock time | Every timestamp is an input recorded in the manifest, never read at evaluation. **CEL binds no clock** |
| Iteration order | RFC 8785 wherever a hash is taken; all report ordering by an explicit sort key |
| Floating point | There is none. Money is `int64 MILLI_USD_MILLION`; tolerances are integers |

**A model call is never on the re-derivation path.** If a filing had attachments, the *facts* the model
produced are content-addressed and pinned; `verify` replays those facts, it does not re-call the model.
**A model output is an input to the verdict, not a step of it.**

**The attestation** is a DSSE envelope over an in-toto Statement v1 whose `subject[]` carries the filing
digest **and** the template digest. Its top-level object is `scope`; it carries `assessor{id,
thirdParty:false, components}`, `timeVerified`, `expires`, `runState`, `livenessProof{canariesRun,
canariesPassed}`, the settled-fraction object, the per-check items, `counterEvidence[]`, the verdict with
its policy version, and four required sentences — bounded silence, purpose, `summaryIsNotSubstitute: true`,
and the detection boundary: *"This system detects error, not deception. Every check here is a consistency
check over a self-reported document. A coherent liar passes all of them."* **There is no `result`,
`status` or `pass` field anywhere in the schema and there never will be** — schema-level prohibition
survives the screenshot, the API integration and the intern.

**Who signs: DECIDED.** The **filer** signs with a detached key; the vendor signs nothing about the filing
and appears only as `assessor.id` with `thirdParty: false`. Vendor signing was rejected because it would
have the vendor attesting to a regulated filing it did not prepare — **if an FME shows an inspector a
signed attestation over a filing that was wrong, the signature is the first exhibit.** Sigstore keyless was
rejected because a public transparency log makes *the fact and timing of a named FME running a
pre-submission check* world-readable and correlatable. **The residual open item is legal review of that
decision, not the decision itself.**

---

## 5. PERFORMANCE AND COST

**Runtime per filing.** Reader A full structural parse **28–44 ms (MEASURED)**; reader B openpyxl load
**202 ms (MEASURED)**; fact table over 511 cells **1 ms (MEASURED)**; evaluation of 227 arithmetic
predicates **sub-millisecond (MEASURED)** and ~2 ms for all 280 (DERIVED); relation probes ~160 ms and
canaries ~35 ms (both DERIVED from the measured 7,946 fact-table mutations/s); receipt ~10 ms, guard <5 ms,
binding <1 ms, settled fraction + closure <5 ms, render + sign ~20 ms (all DERIVED).

**Three totals, and the middle one is the number to quote.** The **deterministic core as built today is
~30 ms (MEASURED)** — which is what makes "no queue" a measurement rather than a preference. A **complete
online run** with readers agreeing and no attachments is **≈ 450 ms (DERIVED)**, dominated by openpyxl and
the probes. **There is no third, worse figure any more:** removing LibreOffice from the online path removes
the 3.9 s tail. The 19,782-mutant campaign is **2.5 s (MEASURED)** and is offline, per template version.

**What is actually built.** *Schema induction, predicate harvest, arithmetic evaluation and the
settled-fraction denominator are built and reproduce in ~30 ms. Template binding, pre-flight, closure,
canaries, attestation and `verify` are specified and not built.* Relatedly: **the verdict path is specified
to make zero model calls, and the assertion is listed as a build gate; the gate is not yet written.**

**Model cost.** Prices VERIFIED-AT-SOURCE at `platform.claude.com/docs/en/about-claude/pricing`, 10 Aug
2026, USD/MTok: Opus 5 $5 in / $25 out (5-min cache write $6.25, cache hit $0.50); Sonnet 5 $2/$10 through
31 Aug 2026 and **$3/$15 from 1 Sep 2026**; Haiku 4.5 $1/$5. **Batch is 50% off both directions and the
cache multipliers stack with it.** Two dated facts that must not survive onto a slide: **Sonnet 5's
introductory pricing expires the day before the residency starts**, and **Opus 5 uses the newer tokenizer,
which produces approximately 30% more tokens for the same text** — so every estimate below is **MODELED**,
not measured with `count_tokens`, and **must be re-baselined before it is quoted**, not multiplied by a
guess.

Candidate proposal, per template version, one-time, on the model actually chosen (Opus 5, cached prefix
~6,000 tokens, ~600 fresh tokens of clause text, ~1,500 output tokens per candidate, Batch): **$0.0218 per
candidate, $0.52 for 24 obligations**, plus a one-time cache write of $0.0375. **About $0.55 per template
version; under $6 for the entire nine-workbook corpus, paid once per revision (MODELED).** The settling
experiment at its pre-registered size (≈30 obligations drawn × 10 candidates × 2 prompt regimes = 600
candidates) is **≈ $13 (MODELED)**, budgeted at $25 with re-runs — *the settling experiment for the entire
AI half of the architecture costs under thirty dollars, which is the correct reason to run it before
elaborating anything on top of it.* Attachment
extraction, per filing and only when attachments exist (20-page PDF ≈ 25,000 in / ~3,000 out): Haiku 4.5
**$0.040**, Sonnet 5 from 1 Sep **$0.120**, Opus 5 **$0.200** (all MODELED).

**The three headline numbers. Marginal model cost per filing on the workbook path: $0.00** — the 280
predicates, the settled fraction, the canaries, the probes and the verdict involve no model at all.
**Annual model spend across the whole modelled population: under $200**, even routing every attachment
through Opus 5. **And the cost that matters is not inference: it is the blind-filled qualification
corpus** — human time, for which no amount of model spend substitutes. **Do not pitch inference savings;
pitch the boundary.** Infrastructure is Fly.io `shared-cpu-1x`/512 MB at **$3.32/month ≈ ₹290/month
(VERIFIED-AT-SOURCE)** and ~3.4 GB/yr of storage: **≈ $240 ≈ ₹21,000 a year all in.**

**At 868 filings a year, and at 100×.** **868/yr is MODELED** — 217 FMEs × 4 quarters, assuming every FME
files every quarter including those registered mid-year. That is ~3.4 filings per working day, or **1.5
seconds of compute per day**. **This must be said out loud rather than hidden:** as a *deployment* this
architecture is absurdly over-engineered for 3.4 documents a day. **As a research instrument it is not** —
the layers are how the measurement is made legible. *The IFSCA workbook is the testbed, not the market: it
is public, machine-readable, small enough to characterise exhaustively, and has a real regulator behind
it. The asset is the method.* At 86,800/yr — 340 per working day, ≈ 11 minutes of compute per day —
**nothing about the request path breaks.** What breaks first, in order: (1) **blob storage**, 3.66 MB ×
86,800 ≈ **320 GB/yr**, triggered by disk not throughput → object storage on the identical `sha256` path,
**the content-addressing scheme unchanged, which is the point of choosing it**; (2) **SQLite's single
writer**, triggered by **concurrent uploads, not row count** → Postgres, **losing content-addressability,
so the manifest must then name a logical snapshot id instead of a file hash**; (3) **the register
snapshot** — the fetch plan is **1 list request + N detail requests where N = |records|**, and the run
that produced the 10 Aug 2026 snapshot made **`1 + N` GETs where `N = |records|`** (the drafts carried
**2,235**; that figure is **withdrawn to UNRECONCILED** — see §II.1.2 — because it matches neither 651 nor
2,006 and no document states its `N`) at 0.06–0.25 s spacing → snapshot
daily, cite the snapshot hash **and its age**, degrade past a staleness bound to
`NOT_RUN(input_unavailable.register)`, and **read IFSCA's terms of use before any scheduled polling**,
which has not been done; (4) **the qualification corpus, which is the real one — it does not scale with
filings at all, it scales with *templates***. That last is the transfer question, **and it is the
experiment that decides whether this is a product or a paper**: what fraction of the FME predicate set
transfers to a second prescribed format, at what human cost per transferred predicate, against a
pre-registered threshold. Nine workbooks are already on disk. **What never becomes the constraint at
either scale is inference:** at 100× with every attachment through Opus 5 the annual bill is **$17,400
(MODELED)** — the cheapest line in the table and the one everybody expects to be expensive.

---

## 6. THE INTERFACES

**Who these surfaces are for.** The buyer is **the filer's compliance officer**, who runs this before
submitting; the unit of value is the avoided deficiency — the inspection observation, the rework, the
Principal Officer's personal exposure — **and that value is UNMEASURED**. The supervisor is **not** a user
and not a buyer: the supervisory system is procured. **The supervisor is why the filer cares.** Where a
surface is useful to a supervisor it is described as useful to *a downstream reviewer*. The single question
that decides whether the entity-facing product is worth anything is **how often IFSCA returns an FME filing
for correction**, and it is answerable by one email.

**API.** FastAPI, `/v1`, JSON except where noted, OpenAPI generated, **no authentication before 30 October**
except on the mutating endpoints, which take an operator token.

| Method | Path | Request | Response |
|---|---|---|---|
| `POST` | `/v1/filings` | multipart: `filing` (.xlsx, required), `attachments[]`, `template_sha256`, `profile` | `201 {run_id, filing_sha256, template_sha256, run_state, report_url, attestation_url}`. Synchronous, median ~450 ms. `413` over cap, `415` non-zip, **`422` on `template_unbound` with the structural fingerprint in the body so an operator can admit the new template** |
| `GET` | `/v1/runs/{id}` | — | the full `run` record incl. `settledFraction`, `verdict`, `livenessProof`, `manifest` |
| `GET` | `/v1/runs/{id}/checks` | `?state=&reason=&predicate_id=` | paginated `run_check[]`, one row per predicate evaluation |
| `GET` | `/v1/runs/{id}/cells` | `?state=&reason=&sheet=` | paginated `run_cell[]` — **the closure table, and what a downstream reviewer's triage tool consumes** |
| `GET` | `/v1/runs/{id}/report.html` · `/attestation.json` · `/log.jsonl` | — | the self-contained HTML (byte-identical to disk, sha256 in the manifest); the DSSE envelope; NDJSON, one line per evaluation |
| `POST` | `/v1/runs/{id}/overrides` | `{stable_key, new_state, remark, evidence_sha256}` + token | the updated cell. **Both states retained**, inside the signed payload, counted separately |
| `POST` | `/v1/verify` | multipart: `report` or `attestation` | `{reproduced, diff[]}` |
| `GET` | `/v1/templates` · `/v1/templates/{sha}/schema` | `?state=` | `template[]` with `field_surface`, `n_predicates`, **`settled_fraction_ceiling` (`null` for unprotected templates — the absent-vs-empty rule applied to our own headline)**; and the full `TemplateSchema` + extraction manifest |
| `POST` | `/v1/templates` | `{origin_uri}` + token | `201`; runs T1–T6 and **stops at T7 awaiting a human signature** |
| `GET` | `/v1/predicates` · `/v1/predicates/{id}/versions/{v}` | `?template=&state=&kind=&obligation=&min_kr=&max_ffr=` | `predicate[]` with the **full qualification block** incl. `g4_corpus_provenance`; and per version the envelope, liveness witnesses and the mutants it kills by fault class. **This endpoint is the product's honesty, exposed — public and unauthenticated by design** |
| `GET` | `/v1/rejections` | `?template=&gate=` | every candidate the gate refused, with the gate, the measured number and the cells it would have covered |
| `GET` | `/v1/registry/roots` · `/v1/settled-fraction/history` | `?template=` | roots with timestamps and counts; the admission timeline annotated with measured rates. **Must be able to step down** |
| `GET` | `/v1/healthz` · `/v1/openapi.json` | — | — |

**Two prohibitions, enforced by schema and by test.** (1) **No endpoint returns a boolean pass/fail, a
`status: "clean"`, or a bare settled fraction** — every figure comes inside the object of §4.3 with all six
counts, so a consumer who wants one number must compute it and will have the denominators in hand when
they do. (2) **`ffr` renders as `null` with `g4_corpus_provenance: "SELF-AUTHORED"`** when that is the
provenance, so a client cannot display an uninformative rate as a measurement.

**CLI** (the primary interface during the residency; the API is the demo surface): `ingest` · `induce` ·
`harvest` · `propose` · `seed` · `qualify` · `admit` · `run` · `verify` · `watch` · `residue` ·
`transfer`. `make demo` runs `ingest → induce → harvest → run` against the workbook as published, on a
judge's laptop, offline after the fetch.

**Screens. One commitment governs all of them: there is no green tick anywhere in the product.**

**1 — Drop.** One control, no settings, no account. On submit: the run state and the two hero counts.

**2 — Report.** The hero is two counts of equal weight, same type size, same ink, no colour on either:
`12 failures across 2,373 checks.` and `1,374 fields were not checked.` The binding is fixed in the label
registry so it cannot drift: `<F>` = failing cells; **`<S>` = settled cells (2,373 on the reference
filing) — in this one label a "check" is a settled field, one per cell**; `<U>` = unsettled cells (1,374).
**The predicate count (280) belongs to the strap line and never to the hero.** The right-hand number is
never smaller, never grey, never below the fold, never collapsed. No progress bar, no ring, no percentage
in the hero: a fixed-height **stacked band** labelled by absolute count, with **the unchecked segment
hatched, not muted** — muted reads as "resolved, minor"; hatched reads as "not filled in", which is the
truth. **The band never fills**, because two permanent rows sit inside the denominator — *properties no
predicate can settle from this artifact alone*, and *demonstrated survivors from the residue set*. **100%
is structurally unreachable, and that is architectural rather than cosmetic.** Nothing renders green;
passing checks take body-text ink; only failures take colour — *the absence of colour is not the presence
of green.* One expandable strap line under the band: `denominator from styles.xml unlocked mask v3 ·
predicate set v11 · registry root 9f3c… · qualified against template sha256:7d9a… · 4 predicates
provisional · 280/280 canaries passed`. **Each failure expands to four things:** both cells, the clause
with its `eId` and a link to the exact page and bounding box, the CEL source, and — the unusual part —
**that check's own measured false-failure rate inline**: `fired on 2 of 96 clean filings [0.6%–7.4%] ·
corpus: BLIND-FILLED, n=96`. A permanent, non-dismissible sentence carries the detection boundary. **When
the run is `INVALID` the whole screen is replaced by the reason, the dead predicates, and no settled
fraction of any kind.**

**3 — The Unchecked panel.** Not an appendix: it sits on Screen 2, above the fold, and it is the
differentiator. Grouped by reason code with counts, and per entry **"what would make this checkable"**,
specific rather than generic. The canonical entry is writable today: *Third Schedule Part A(g) — whether
the valuation is appropriate*, `no_predicate.requires_judgment`, and what would fix it: *a materiality
threshold by scheme class of the kind CSSF Circular 24/856 Tables 1–3 specify (0.20% money-market / 0.50%
bond and mixed / 1.00% equity and other), plus a compensation-direction rule of the kind its Tables 4–5
specify.* Beneath the reasons: **demonstrated survivors** — not reasons but exhibits.

**4 — The predicate library.** Every admitted check, filterable, ≤ 515 rows, a plain `<table>`. Per row:
clause (`eId` + quote), CEL source, `KR = K/O` with both integers **and** the per-fault-class vector, the
degeneracy verdict with its Z3 witness, FFR with corpus provenance, `n` and Wilson interval, severity tier,
admission date, liveness witnesses — **and, beside each rule, what a flag-everything rule would have
scored.** Two tabs the category does not have: **Rejected**, and **the five-gate attrition funnel** per
obligation (generated → executed and bound → non-degenerate → killed → FFR-admitted). **A 20:1 attrition
ratio displayed honestly is a stronger demo than a settled-fraction bar, because no competitor will show
it.** One caution the screen must obey: **the gate has exactly one demonstrated rejection** — five of ALR's
six bound predicates assert only `≥ −1e17` over 1,428 cells and are refused (MEASURED, L14 §1.12) — and
**whether it rejects anything on the FME workbook is unmeasured**, since 19 of that workbook's 24 bounds
are a real `≥ 0`.

**5 — Settled fraction over time.** Renders from a static JSON log, no live backend. Each increment
annotated with the predicate's measured rates; **the chart must be able to step down** and every step-down
is labelled with its cause. Beside it, on the same axis, `R/O` — the fraction of observable defects no
admitted predicate can reach — the inverse curve. **When the 515-predicate figure appears it appears with
its per-workbook distribution attached, never alone:** it is a sum over nine workbooks and it is
concentrated, since `EDR_1` has zero formulas and `IFSCA_Annual_Reporting_Format` has zero formulas and
zero validations. **Publishing that distribution is a build gate, because no lane published it.**

**Build gates — commitments that are tested rather than believed.** `ci/no-green-tick.sh` (grep for
`✓ ✔ ✅ 🟢 / all clear / no issues / looks good / verified clean / compliant / passed all / fully checked`
over `src/ templates/ locales/`); `test_schema_constants` (**505 / 294 / 211 / 54 / 22 / 20 / 252 /
3,747** — properties of the file); `test_harvest_count` (**280** and **515** with the per-workbook
distribution — **a property of our code, allowed to move with a recorded reason**, split from the constants
test so a correct rejection by gate G3 does not fail the build); `test_denominator_provenance`;
`test_ffr_provenance`; `test_unmeasured_predicate_rejected`; `test_closure`; `test_error_absorption`;
`test_vacuity`; `test_predicate_raise_is_error`; `test_dual_reader`; `test_no_model_in_verdict_path`
(**not yet written**); `test_no_libreoffice_online`; `test_no_tlog`;
`test_attestation_has_no_status_field`; `test_openpyxl_never_writes_the_artifact`.

---

## 7. DECIDED HERE, AND WHAT REMAINS OPEN

| Ref | Item | Status |
|---|---|---|
| **G1** | Unit of the denominator and of closure | **DECIDED: the cell.** Beat the pair model because every measurement is a cell count and the pair model has no published enumeration rule (§4.2) |
| **G2** | FFR threshold setting `severity_tier` | **DECIDED, pre-registered: `FFR ≤ 0.02 ⇒ BLOCKING`; `0.02 < FFR ≤ 0.10 ⇒ ADVISORY`; `FFR > 0.10 ⇒ not admitted`.** Any defensible number beats none; changeable only by an argument that the old one was wrong, recorded with its date |
| **G3** | Money scale | **DECIDED: `MILLI_USD_MILLION`, `int64`, 1 unit = USD 1,000, `τ(n) = 5n`**, everywhere including the `Field.unit` enum |
| **G4** | State/reason vocabulary | **DECIDED: 8 × 30, frozen and normative** (§4.4). Any plan targeting 7 states or 19 codes is regenerated from this |
| **G5** | Where the evaluation contract lives | **DECIDED: one file, `EVALUATION-CONTRACT.md`**, containing the five rules and nothing else; every other document links to it |
| **G6** | How an obligation binds to a field | **DECIDED: a hand-maintained `obligation` table (`source='hand'`)**, because nothing of L1b is built; it flips to `'l1b'` when the clause graph produces `eId`s |
| **G7** | Gate order | **DECIDED: G0 → G1 → G3 proof → G2 → G3 empirical → G4** |
| **G8** | Regression constants | **DECIDED: split** into `test_schema_constants` and `test_harvest_count` |
| **G9** | Repo licence | **DECIDED: Apache-2.0** — it carries a patent grant and every core dependency chosen is compatible. First file created |
| **G12** | LibreOffice and the toolchain pin | **DECIDED: excluded from the online verdict path entirely** — it was a cross-check, so this is free, and it removes an unpinnable subprocess from under a byte-identity acceptance test. **Pinned by container digest wherever it runs offline**, with its outputs content-addressed so quoted kill rates stay reproducible. Consequence: `INDETERMINATE(engine_disagreement)` comes from the pinned per-template table, never a live call |
| **C21** | Who signs | **DECIDED: the filer, detached key**; vendor only as `assessor.id`, `thirdParty: false`. Residual: legal review of the decision, not the decision |
| **C22** | Pervasiveness `K`, `T` | **OPEN, non-blocking.** One file, `pervasiveness-policy-v1.json`, versioned inside the attestation. **Until the argument that sets them exists both render `PLACEHOLDER`, and no number for either appears anywhere** |
| **G10** | Person A | **OPEN — USER DECISION.** *Name one person, not on the team and having never seen the predicate set, who will fill ≥ 30 clean workbooks from the template and regulation only — or authorise the audited second-model-instance route, with the fill prompt hashed and published before the first workbook is filled.* **Every FFR in the product depends on this, and no FFR may be printed until it exists** |
| — | Licences not opened | **OPEN, engineering, before the code ships:** gVisor, Z3, `xbrl.us/dqc-license`, `cobalt`/`indigo` — **and IFSCA's terms of use for the register API**, a gap in conduct rather than code |
| — | Measurements before any number is quoted | **OPEN, ordered:** does our evaluator reproduce the template's cached values exactly, incl. `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101` — **a positive control is required before any kill rate is quoted**; our own `U/G`; does `celpy` pass the conformance suite **on error semantics**; key-binding accuracy `μ`; **the vocabulary→validation mapping — two lanes imply different counts and neither figure may be quoted until the build computes it**; whether a filer's Excel round-trip rewrites the 211 shared-formula followers; the field surface for an unprotected template; whether the `D17` COUNTIF defect recurs in the other prescribed workbooks (20 minutes, and it turns one finding into a pattern); **the transfer measurement** |

**One last thing this part must not sand off.** The gate, the seeded defects, the relations and the typed
non-settlement vocabulary are not four features. Remove seeded defects and the FFR is uncomputable and the
gate is decorative. Remove the gate and the settled fraction is an assertion. Remove relations and it is a
ceiling rather than a growth curve. Remove typed non-settlement and the whole thing is a linter. **No part
is removable — which is the test of whether an assembly is a design rather than a stack.**
