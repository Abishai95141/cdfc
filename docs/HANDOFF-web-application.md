# Build the cdfc web application

## Read these first, in this order

1. **`CLAUDE.md`** — how to work here. The rules in §3 are not style; each one cost a real number.
2. **`docs/ARCHITECTURE-measured.md`** — the architecture from the IMPORT GRAPH, not from prose.
   Regenerate with `make graph`. Where it disagrees with any document, it wins.
3. **`web/README.md`** — the current surface and why it renders a snapshot.
4. `git log --oneline -14` — the `B3` and `C0`–`C5` commits. Each message says what it found, not
   just what it did.

## What you are building

**A working web application, not a presentation.** The current `web/` renders a static snapshot
somebody else computed; you cannot do anything in it. Replace that with an application where a user:

1. **uploads a rules corpus** (PDF or text) → it is pinned, segmented, and addressable
2. **uploads a filing template** (xlsx / XSD) → its field surface is induced, or refused with a reason
3. **sees the graph built** — provisions, fields, and the rules binding them — and can explore it
4. **uploads sample exports** (CSV / Excel / PDF) as the evidence for a filing
5. **asks it to fill** the template, and watches values land with their provenance
6. **answers the system's questions**, and those answers become values
7. **reviews and attests**, ending in a signed coverage certificate

## The architecture you must build WITH, not around

**`src/cdfc/evidence/run.py` is THE DRIVER** — one function, one place where layer order is decided.

**THE SEAM.** `run()` takes `proposals: Path` — a FILE. The model writes proposals as data; the
driver reads them; five gates adjudicate. The model is never called from the verdict path because
it is not called at all. `model.propose()`/`.extract()` take a `transport` so any provider can be
substituted; `cdfc.model.transport.deepseek()` exists.

**`cdfc.fill`, `cdfc.evidence`, `cdfc.qualify` and `cdfc.pathm` are VERDICT ROOTS.** They may never
import `cdfc.model`. Anything a model produces reaches them as DATA. `tests/negative/importgraph.py`
enforces this positively: third-party imports in the verdict closure must be a SUBSET of
`RUNTIME_THIRD_PARTY`, so anything undeclared is refused by default.

**FOUR POPULATIONS, never merged.** corpus/statute · template · source document · entity. A
statute's `FME` is a CONCEPT; a custodian row's `FME` is an IDENTITY. A graph that cannot tell them
apart is a graph nobody can audit.

## What is already built and working

* end-to-end on real IFSCA data — `python tools/user_flow.py`, five of five stages
* `tools/build_frontend_data.py` runs the real flow and emits `web/data/state.json`
* `tools/gen_proposals.py` generates proposals via DeepSeek and pins them content-addressed
* `cdfc evidence --durable` maps a statute onto a template through the five gates
* PDF ingress (`make pin-pdf`, `make demo-pdf`), fill and write (`make demo-fill`), entity fusion
  (`make demo-fuse`)
* the API already serves `/v1/templates`, `/v1/filings`, `/v1/runs/{id}`, `/v1/verify` and more —
  see `src/cdfc/api/routes.py`

## What is NOT built — this is your work

* **upload**: no endpoint accepts a corpus or a source export. `POST /v1/templates` exists.
* **live map / live fill**: both are CLI only. The application needs them as requests.
* **a real graph endpoint**: the current graph screen draws three circles from counts.
* **THE QUESTIONING FLOW — and this is the one that matters most.**

## The questioning flow, and the shallow proxy to remove

The product's sentence is *"tell you exactly what nothing supports, what two of your documents
disagree about, and what needs your judgement."* That is a system that **ASKS**.

**Today it counts and does not ask.** Eight attestation fields are listed as "a human signs; the
system never fills one" and no question is ever put, no answer can be given, and no answer can
become a value. That is a lane in name only — remove it by building the real thing.

`cdfc.fill.propose.FillRefusal` is a CLOSED vocabulary of 8 reasons. Six of them ARE questions:

| reason | the question to ask | how an answer resolves it |
|---|---|---|
| `no_observation` | nothing you gave us contains a value for this field | upload a document, or assert the value |
| `support_contradicted` | two of your documents disagree — which is right? | choose a source |
| `not_locatable_in_source` | a column offered this but the document does not contain it | name the document |
| `vocabulary_not_admitted` | your value is not in the form's list — which of these? | choose a term |
| `type_not_admitted` | this cell needs a date / a number | supply one |
| `attestation_requires_signatory` | sign this | a named signatory |

Two are NOT questions and must never be presented as ones:

* `field_not_labelled` — the regulator's cell has no label; we cannot formulate a question. On the
  FME blank this is **3,615 of 3,735** refusals. Headlining that total as "needs your judgement"
  is misleading and the current screen does exactly that. **Only ~120 are answerable.**
* `reverification_failed` — our defect, not the user's.

**An answered question must become a value with its own provenance** — `resolved_by: human`, the
answering user, the instant, and the question it answered — and it must NEVER be counted as
evidenced. An asserted value and a byte-exact located value are different evidence, and the whole
product rests on not confusing them. `cdfc.evidence.entities.ResolvedBy` and the `Derived` fill lane
are the existing precedents for a labelled weaker tier; follow them.

## Defect shapes that recurred in the last session — do not repeat them

* **`getattr(obj, "name", default)` in a serialiser or a measurement harness NEVER FAILS; it
  publishes a falsehood.** It emptied a `governed` column across nine templates, and rendered every
  provenance field as an em-dash — the whole product shown as absent. Read the real attribute.
* **`str.replace` that matches nothing is a silent no-op.** Assert the anchor is present first.
* **A partial view is not a reading.** `tail -4 | head -3` of a registry showed rows to 130; the
  next id was taken as 131 and 131 already existed.
* **`make x | tail` returns TAIL's exit code.** Capture to a file, or `set -o pipefail`.
* **`document.createElement("svg")` returns an HTMLUnknownElement** — `cx`/`cy`/`r` are inert. SVG
  must be parsed into its namespace.
* **`hashchange` is async.** A probe that sets `location.hash` and reads the DOM in the same tick
  measures the same screen every time and returns identical numbers that look like measurements.
* **A count is not a reading.** Open the bucket before publishing the total.
* **`absent != empty != zero`.** A template we cannot read must not be reported as a template with
  no fields in it.

## Known limits — state them, do not paper over them

* **`deepseek-v4-flash` is NOT reproducible at `temperature=0`.** Two runs over identical inputs
  gave 9 proposals then 2, 11 then 0, 0 then 10, 19 then 42. Generation is a BUILD step and its
  output is pinned; a run names the digest. Never claim the generation is reproducible.
* **"any template" is 7 of 9** on the pinned corpus. Two IFSCA workbooks ship no protection mask
  AND no data validation, so neither induction signal exists; they are refused with a reason.
* **`gate-qualified` and `autonomously` are NOT claimed.** G4 admits 0; 8 of 443 labelled fields are
  attestations. No fill-accuracy number exists and none can until 30 filing-plus-source-pack pairs
  arrive.
* **Filing coverage on the demo is 2 of 3,747 cells** — the mechanism is proven, the coverage is
  unmeasured on realistic inputs. Do not present the demo figure as a product figure.
* **LangExtract is ADOPTED in `docs/PLAN.md` line 247 and NOT wired.** The grounding it would give
  is enforced later by G-QUOTE. Wire it or record why not; do not leave the divergence silent.

## The bar for "it works"

Not a passing fixture. Drive YOUR OWN frontend and prove the flow:

1. `make greps` — **exit 0, checked** (not through a pipe)
2. `CDFC_REQUIRE_RUN=1 pytest tests -q` — exit code **captured to a file**, nothing else touching
   the tree
3. `python tools/nc_sweep.py` then `python tools/gate_liveness.py` — every new gate needs a row in
   `ci/GATES.md` **naming its TEST**, a dated argument in `docs/GATE-CHANGES.md`, an entry in
   `tests/negative/catalogue.yaml` with a guard that **actually flips**, and each half of a check
   needs its own injector
4. **Through the browser**: upload a corpus, upload a template, upload a CSV, press fill, answer a
   question, see the answer become a value, and read the certificate — with screenshots
5. Rows in `docs/AUDIT-TRAIL.md` for every decision, measurement, correction and defect
6. **Never add a `Co-Authored-By: Claude` trailer**

## Credentials

`DEEPSEEK_API_KEY` and a Gemini key are used **via environment variable only** — never written to
disk, never committed. Both appear in the previous session transcript and should be rotated.
