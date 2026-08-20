# The architecture, MEASURED — from the import graph, not from prose

*Built 20 Aug 2026 by `graphify` over `src/` — 4,414 nodes, 8,622 edges, directed, AST only (no
LLM). Regenerate with `make graph`. This file records what the graph SAYS; where it disagreed with
`CLAUDE.md`, `CLAUDE.md` was corrected.*

## The five layers, and the file that decides the order

**`src/cdfc/evidence/run.py` is THE DRIVER.** Its own docstring: *"instrument + template +
proposals -> adjudication -> graph -> declaration. One function, so the flow is readable in one
screen and so there is exactly one place where the order of the layers is decided."*

```
LAYER 1a  cdfc.evidence.provisions     rules corpus  -> Provision (eId + exact span)
          cdfc.qualify.provisions      DURABLE division addressing (N1); the eId itself
LAYER 1b  cdfc.evidence.fields         template      -> Field (declared type)
          cdfc.qualify.template_instrument   the pinned blank AS an addressable instrument
          cdfc.schema.xsd              an XSD        -> Field surface
LAYER 2   cdfc.model.propose           rule -> field bindings, AS DATA
          cdfc.model.extract           CLAIMS from prose (GraphRAG's stage, without GraphRAG)
LAYER 3   cdfc.evidence.gates          G-QUOTE - G-FIELD - G-TYPE - G-VOCAB - G-XREF
LAYER 4   cdfc.evidence.graph          the graph, built ONLY from admitted proposals
          cdfc.evidence.query          coverage over a denominator that is not arguable
LAYER 5   cdfc.pathm - cdfc.predicates - cdfc.evaluate
```

## THE SEAM: how a model reaches the system without entering it

`evidence.run()` takes **`proposals: Path`** — a FILE. The model writes proposals as data; the
driver reads the file and the five gates adjudicate it. **The model is never called from the
verdict path because it is not called at all — it is read.** That is the firewall, and it is
structural rather than a promise.

`cdfc.model.propose()` and `.extract()` take a **`transport`** argument, documented *"so the tests
exercise the parsing and the refusals without a network, and so a caller may substitute any
client."* That is the supported way to use a provider other than Anthropic: supply a transport.
`_call` promises one thing and it is the whole point of the function — **a failed call NEVER looks
like a clean empty result.**

## What the graph found that the prose did not say

**`cdfc.model` IS ORPHANED.** Nothing under `src/` imports it; only `tests/contract/` does. LAYER 2
is built, tested, and wired to nothing. Any claim that the system "uses a model" is currently false
of the running product.

**`predicates` is the core, not `qualify`.** Fan-in over package-to-package edges:

| package | fan-in | package | fan-out |
|---|---|---|---|
| `predicates` | **329** | `qualify` | **180** |
| `schema` | 111 | `measure` | 149 |
| `ingest` | 104 | `evaluate` | 146 |
| `qualify` | 100 | `probes` | 133 |
| `verdict` | 100 | `predicates` | 85 |

**`qualify` and `predicates` are mutually dependent** — `qualify -> predicates` 65 edges,
`predicates -> qualify` 23. A cycle at the centre of the system; recorded, not yet resolved.

**Two `provisions` modules exist and they are different things.** `evidence/provisions.py` turns a
corpus into `Provision` nodes; `qualify/provisions.py` is N1's durable division addressing that
supplies the eId. The names collide and the roles do not.

**Hubs, by degree:** `_Path` (180, the CEL AST walker), `fromstring()` (54, `ingest.xmlsafe` — every
XML read in the system funnels through one guarded parser), `esc()` (46), `InstrumentText` (40),
`Anchor` (40, and it exists TWICE — `cdfc.facts.anchor` and `cdfc.schema.anchor`).

## The four concerns, and where each one lives

| concern | modules | resolver |
|---|---|---|
| **corpus / statute** | `evidence.provisions`, `qualify.provisions`, `qualify.textsource` | deterministic; division axis by purity x coverage |
| **template** | `evidence.fields`, `qualify.template_instrument`, `schema.xsd`, `schema.anchor` | deterministic; field surface induced |
| **source document** | `ingest.*`, `fill.pipeline`, `correspond.schema` | two-parser corroboration; A1c column->field |
| **entity** | `correspond.link`, `evidence.entities` | Fellegi-Sunter, EM-fitted, NO labelled pairs |

**These are four different populations and they must not be merged.** GraphRAG's corpus entities
(`FME`, `AUTHORITY`, `APPLICANT`) are concepts IN THE STATUTE. `Record`/`Entity` are identities in
the USER'S FILES. A graph that cannot tell them apart is a graph nobody can audit.

## The verdict closure

Ten roots: `evaluate` `verdict` `probes` `selfcheck` `attest` `qualify` `surface` `pathm`
`evidence` `fill`. 753 modules. Third-party imports must be a SUBSET of `RUNTIME_THIRD_PARTY` —
`celpy` `lark` `lxml` `openpyxl` `yaml` `z3` — enforced positively, so anything undeclared is
refused by default.

**`cdfc.ingest` is INSIDE the closure** (via `fill` and `qualify`), which is why no PDF reader may
live there. Build-time readers go in `tools/`.
