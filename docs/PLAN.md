# docs/PLAN.md — the plan of record

**This is the one document that describes the CURRENT plan.** Two documents describe how we got
here and are deliberately not edited to match results:

| document | what it is | may it be edited to match a result? |
|---|---|---|
| `docs/ARCHITECTURE-rules-and-evidence.md` | the ANCHOR architecture decision, 18 Aug 2026 | no — dated decision record |
| `docs/EXPERIMENT-PROGRAMME.md` | pre-registered waves, criteria and kill rules | **never** — editing a criterion after seeing its result is the sin it exists to prevent |
| `docs/measurements/W0-results.md`, `docs/spike/README.md` | what running them produced | no — dated measurements |
| **this file** | what we now intend to build, and why it changed | yes, and it names the evidence for every change |

Every checkpoint marked observed below was OBSERVED by a probe in `tools/progress.py`, not asserted
here. `make progress` re-runs all eleven and rewrites `PROGRESS.md`; a regression flips a checkpoint
back to TODO whether or not anybody expected it to.

---

## 1. Where we stand

    ANCHOR PHASE A0   truth, and the Path M spike            COMPLETE
    ANCHOR PHASE A1   the Anchor seam, second template       COMPLETE — 7 of 7 probes observed
    ANCHOR PHASE A1c  field correspondence                   NEW, NOT STARTED — see §5
    ANCHOR PHASE A2   Path M and rule coverage               NOT STARTED — 2 entry criteria unmet
    ANCHOR PHASE A3   the evidence side, CONTRADICT          NOT STARTED — narrowed by W0-C
    ANCHOR PHASE A4   Path Q, prose to admitted check        NOT STARTED — 0 of 1 probe
    ANCHOR PHASE A5   fill                                   NOT STARTED — gated on a negotiation

What is TRUE of the tree today, each line traceable to a probe:

* a buyer's own workbook is checked over **its own** denominator, and handing the runner the wrong
  blank is `INVALID` with `invalid.denominator_disagreement` rather than a flattering VALID (`A1-3`,
  `A1-4`, `A1-5`);
* `POST /v1/filings` binds, checks and returns **201** with the coverage declaration — the run is
  computed and **not stored** (`A1-6`);
* the `Anchor` carries `(table, rows, cols)` with list-valued axes and a non-identifying dialect,
  imported by 22 modules in `src/` (`A1-1`, `A1-2`);
* published artefacts are stable across `PYTHONHASHSEED` 0/1/2 under an instrument that was proven
  able to see a seeded ordering perturbation (`A1-7`).

What is still FALSE, and stays visible while it is:

* the predicate library holds **0** admitted rows against **348** rejected candidates (`A2-2`);
* **0 of 4** Path M host functions are registered (`A2-1`);
* **0** statutory obligations exist (`A4-1`);
* the run store, the staleness policy and deployment packaging are absent — `docs/OPEN-ITEMS.md`
  carries the standing list and the report renders it with its age.

---

## 2. The flow, end to end — and where each guardrail sits

The spike ran this whole path on the real IFSCA instrument and the real FME template
(`docs/spike/README.md`). It is the target architecture, stated once:

    ┌─ LAYER 1 · DETERMINISTIC ─────────────────────────────────────────────────────┐
    │  regulation corpus ──► Provision nodes: stable eId, exact char span            │
    │  filing template   ──► Field nodes: type read from the workbook's OWN number    │
    │                        formats and validation lists, never guessed             │
    └───────────────────────────────────────────────────────────────────────────────┘
                                        │
    ┌─ LAYER 2 · THE MODEL, AND ONLY HERE ──────────────────────────────────────────┐
    │  proposes  rule ──► field  bindings, AS DATA. It decides nothing.              │
    └───────────────────────────────────────────────────────────────────────────────┘
                                        │
    ┌─ LAYER 3 · DETERMINISTIC — THE GUARDRAILS ────────────────────────────────────┐
    │  G-QUOTE  the cited text is byte-exact at the cited span, or refuse            │
    │  G-FIELD  the cited cell EXISTS in the template's field surface, or refuse     │
    │  G-TYPE   the predicate's type matches the field's derived type, or refuse     │
    │  G-VOCAB  every term is in the closed vocabulary, or refuse                    │
    │  G-XREF   every cross-reference resolves to a provision that EXISTS, or refuse │
    │  ONLY ADMITTED PROPOSALS BECOME NODES — a query cannot return a refused claim   │
    └───────────────────────────────────────────────────────────────────────────────┘
                                        │
    ┌─ LAYER 4 · DETERMINISTIC ─────────────────────────────────────────────────────┐
    │  graph + RDF projection + queries; coverage answers over its own denominator   │
    └───────────────────────────────────────────────────────────────────────────────┘
                                        │
    ┌─ LAYER 5 · MIXED ─────────────────────────────────────────────────────────────┐
    │  precedence resolved in PYTHON, before any engine (see §4 F5)                  │
    │  chaining: applicability ──► obligation ──► breach                             │
    └───────────────────────────────────────────────────────────────────────────────┘

**The guardrails already in the shipped tree** are a different, older set and they are not replaced
by the five above — they compose. `G0`–`G4` qualify a predicate; `BANNED_IN_VERDICT` plus
`ci/barrier5.sh` enforce by import closure that no model reaches a verdict; `ci/GATES.md` is an
append-only registry where every row names the injector that makes it red.

**How well the Layer-3 guardrails work is MEASURED, not claimed.** On the real instrument, of 15
proposals the gates admitted 10 and refused 5: all **3 of 3** planted errors, **and 2 of my own 12
genuine proposals** — cells cited without checking they exist. The architecture never claimed the
model is accurate. It claims the model's errors are catchable without a human reading every one,
and that is now a number rather than an argument.

**The one thing this flow does not do, and cannot:** it does not bound RECALL. Nothing measures the
rules nobody proposed. `ARCHITECTURE §5.5(c)` says so and the spike changes nothing about it.

### The ATTESTATION lane — a second output the flow must have

Of 724 labelled field-surface cells, **702 are FACT-shaped and 22 are ATTESTATION-shaped** (14 on
Compliance Status, 4 on AML-CFT, 3 Introduction, 1 Complaints). The classifier is crude — one cell
that reads as an attestation was labelled FACT — so **22 is a floor**.

The consequence is a product decision, not a detail. A FACT field is fillable from evidence. An
ATTESTATION field is a yes/no a human signs, and no system should forge one. The correct behaviour
where the model lacks the information is to **raise a question to a named human and carry their
signature**, never to fill. That lane is designed here and built in A5.

---

## 3. The tech-stack register

Every library evaluated so far, its verdict, and the measurement behind it. **A verdict of REJECTED
is as load-bearing as an adoption and is recorded with its evidence.**

| library | version probed | verdict | the measurement |
|---|---|---|---|
| `lxml` | 6.1.1 | **ADOPTED, runtime** | raw-zip + lxml is the only workbook reader; `ci/no-regex-over-xml.sh` guards it |
| `cel-python` | 0.5.0 | **ADOPTED, runtime** | the predicate runtime. E1: 14 distinct function-like tokens across 12,925 foreign rules, **0 unknown constructs** |
| `openpyxl` | 3.1.5 | **ADOPTED as a READER ONLY** | banned as a writer by `ci/no-openpyxl-writer.sh` (NC-P04): a round-trip rewrites bytes the fingerprint depends on |
| `pypdfium2` / `pdfplumber` | 5.13.0 / 0.11.10 | **ADOPTED, build-time only** | nothing in `src/` imports them; the pinned `*.text.json` is what the system reads |
| `pymupdf` | — | **REJECTED on licence** | AGPL-3.0, denied by `ci/licence-denylist.sh`. **It was the arm that scored best**, and it is still refused |
| **Docling** | 2.120.3 | **ADOPT — decided by the spike** | `ListItem.marker` recovers **294** regulation-number markers → **634** provisions (274 EN / 360 HI), **147** distinct EN numbers over range 1–148. This is the segmenter (§4 F4) |
| **LangExtract** | 1.6.0 | **ADOPT for A4, strict mode** | `alignment_status` + `char_interval` give the byte-exact span G-QUOTE needs. Not yet exercised at scale |
| **docling-graph** | 1.9.1 | **DEFERRED** | it does carry semantic models and VLM/LLM paths. What it does not carry is our decide layer; adopting its graph would mean adopting its admissions |
| **networkx + rdflib** | 3.6.1 / 7.6.0 | **ADOPT for the graph projection** | the spike built 1,005 nodes / 20 edges / 2,483 RDF triples over the real artefacts and queried them |
| **semantica (Datalog)** | 0.6.5 | **REJECTED as an adjudicator** | it accepts an inline comparison and derives nothing, **and accepts `not` / `!` / `NOT` and ignores them** — deriving a breach the exception displaces. See §4 F5 |
| **Splink** | not yet run | **PLANNED for A1c** | Fellegi-Sunter with unsupervised EM: the weights are DERIVED, not a knob somebody tunes until the demo passes. The reason it is preferred over a similarity threshold |
| Zingg · dedupe | not yet run | **ALTERNATES to Splink** | evaluated on paper only; named so the choice is a choice |
| Valentine (COMA, Cupid, Similarity Flooding, EmbDI) | not yet run | **BENCHMARK, not a dependency** | the schema-matching benchmark A1c's correspondence must be scored against, so the number is not self-graded |
| Arelle | not yet run | **PLANNED as the external ORACLE** | the only third-party executor of a publisher's own formula linkbase in reach. `W2-5` |
| Slaw (laws.africa) | not yet run | **NOT NEEDED for IFSCA** | an Akoma Ntoso grammar parser. The Docling-marker finding makes it unnecessary for the pinned instrument; revisit per-instrument |
| an LLM API | — | **NOT IN THE RUNTIME, BY CONSTRUCTION** | `BANNED_IN_VERDICT` import closure + `ci/barrier5.sh`. The model proposes; it never appears in a verdict path |

**The runtime closure is deliberately tiny and must stay so.** Docling, LangExtract, networkx and
rdflib all enter as **build-time or proposal-time** dependencies producing pinned artefacts — they
do not join the closure of the code that issues a verdict. Any change to that is an architecture
decision, not a `pip install`.

---

## 4. The findings that changed the plan

Each row: what the plan assumed, what running it measured, and what changes. Nothing here is an
opinion about a result — the results are in the dated documents.

### F1 · Path M is real, and bigger than the plan sized it
`W0-B`, `E1`, `E2`, `E3`. 12,925 EBA rules, **every one** carrying a machine-parseable expression;
**12,850 of 12,925** compilable with four bounded host functions and **not one ban weakened**;
**18,826 of 18,827** addresses resolve against each rule's own declared scope; EIOPA publishes
**6,767** more in a different notation over the same `{table, row, column}` shape.
**CHANGES A2.** The compiler risk is not vocabulary — it is **one structural construct**: 12,448 of
12,925 expressions open with a `with {…}` context header that CEL has no equivalent for. A2 is
scoped as a context-binding compiler, written once, rather than a token-by-token translator.

### F2 · The denominator survives off Excel
`W0-A`: **13 of 16** blanks DERIVED, including all four AcroForm PDFs (389 / 200 / 199 / 23
fillable fields after removing containers and read-only entries).
**CHANGES the strategy that was on the table.** The "structured formats only" fallback is NOT
triggered; PDF AcroForm stays in scope for the denominator. Two cautions travel with it: the DOCX
family is **n = 1** and is the negative case, and the two XBRL counts are extension-taxonomy
concepts that **must never be read as denominators**.

### F3 · Similarity matching manufactures support
`W0-C`: under exact matching, **0 of 20** blanked values were reported SUPPORTED across all three
deletion strata. Under similarity matching, **20 of 20** — on evidence that had been deleted.
**CHANGES A3.** The evidence half ships **exact matching only**. This is the sharpest kill in Wave 0
and it narrows a ten-week phase before it starts.

### F4 · The segmenter is a RE-EXTRACTION problem, not a parsing problem
The plan carried the provision segmenter as a hard prerequisite at **6–10 weeks**, on the assumption
that recovering `reg_8__subreg_1` from a Gazette PDF is parsing. The spike measured the premise: a
line-anchored pattern finds **3 regulation numbers in 197,767 characters**, because the pinned
corpus was extracted as FLAT TEXT and the list markers were dropped. **No parser recovers them** —
Akoma Ntoso tooling included. Docling's `ListItem.marker` carries them, and yields 634 provisions.
**CHANGES A4, in both directions.** Most of that 6–10 weeks disappears. But re-extracting the
instrument **changes its bytes**, and every offset, span and `text_hash` anchored to it moves with
them. That is a **re-pinning event with a blast radius**, and it must be sequenced and measured like
the vocabulary migration in `ARCHITECTURE` Risk 3 — not slipped in as an extraction improvement.

### F5 · Do not adjudicate with a Datalog engine — resolve precedence first
semantica chains correctly, and it also **accepts `not` / `!` / `NOT` and silently ignores them**,
deriving a breach that the exception displaces; and accepts an inline comparison while deriving
nothing. Both are wrong answers wearing the shape of right ones. Provisos are not a corner case:
**106 of 531** clauses in the pinned instrument carry one.
**CHANGES A4's Layer 5.** The repair is not a better rule. **Resolve precedence in Python BEFORE the
engine, so the engine never needs negation** — an exception is a precedence question and precedence
is computable. Demonstrated in the spike on two entities with identical category and net worth, one
compliant under the proviso's lower threshold and one in breach.

### F6 · What Path Q can promise is narrower than the flagship example implies
`ARCHITECTURE §4.3` builds its worked example on regulation 8(1) and a net-worth threshold. The real
provision requires net worth *"as specified in Second Schedule … or such other amount as may be
specified by the Authority"* — a Schedule plus an **open delegation** — and the only net-worth field
in the entire return is `8. Compliance Status!C6`, a yes/no **attestation**. The return never asks
for the figure.
**CHANGES what A4 may demo.** That obligation is checkable against the **source corpus**
(CONTRADICT), never against the filing. The demo sentence must be drawn from the FACT-shaped 702,
and the flagship example needs a different obligation or an honest re-framing.

### F7 · The propose/decide loop works, with a measured and fully-caught error rate
Toy corpus: 13 proposals, 9 admitted, 4 refused — 3 planted and **one that was not planted**, where
a rule cited *"regulation 19"* that the corpus lacks, so the gate found a hole in the DOCUMENTS.
Real artefacts: 15 proposals, 10 admitted, 5 refused — 3 of 3 planted, plus **2 of 12 genuine**.
**CHANGES the confidence in A4, not its scope.** `ARCHITECTURE §5.5(b)` proposed an adjudicator kill
campaign as the substitute for the kill gate; this is the first real data for it and it partially
pre-pays `W3-3`'s live arm. Recall (§5.5(c)) is untouched and still unbounded.

### F8 · Graded binding is unsafe, and a correspondence component is now a phase
Built, measured, reverted. A row insertion renumbers every cell below it: of 3,747 addresses,
**3,544 are common to both files while holding different fields**. Scoring those against each other
is precisely the wrong-form failure that strict binding exists to prevent.
**ADDS A1c.** Coverage over a real **correspondence** — an alignment that survives insertion,
deletion and reordering — is a distinct component that no phase contained. It is the piece that
makes "schema-free" true for how filers actually behave, and it is a prerequisite for A5: you
cannot fill a form you cannot align.

### F9 · G2 is a statistic, not a veto
Already taken as a decision in the programme, restated because it sizes A2: the four-way
classification is **222 unverifiable / 93 no-kill / 33 no-margin / 0 admit**, summing to 348.
Repairing `observable()` produces **zero** admissions. Path M rules are `ADMITTED_BY_PUBLISHER` and
always executed; the kill campaign publishes a statistic about discriminating power.

---

## 5. The phases, revised

### A1c — FIELD CORRESPONDENCE · **new, and it is the shortest path to the schema-free claim**

**Delivers.** An alignment between the filing's fields and the blank's fields that survives row
insertion, deletion and reordering; coverage scored over that correspondence with unaligned fields
declared on **both** sides; and a refusal when the correspondence is ambiguous — two candidate
alignments of similar quality is the same hazard as two pinned blanks sharing a sheet set.

**Why Splink rather than a threshold.** Fellegi-Sunter under unsupervised EM derives its weights
from the data. A similarity cut-off is a number somebody chooses, and `W0-C` measured what happens
when a similarity judgement is trusted: 20 of 20 manufactured supports on deleted evidence.

**Entry criteria.** None outstanding. **Scored against** the Valentine benchmark so the number is
not self-graded.
**Exit.** `row-inserted__portfolio-r7.xlsx` is checked rather than refused, and every cell it scores
is demonstrably the field the blank declared — a negative control that a mis-aligned pair is REFUSED
rather than scored is required before any of it ships.

### A2 — PATH M AND RULE COVERAGE

**Delivers.** The `with {…}` context compiler, the four host functions (`isnull`, `abs`, `max`,
`min`), rules `ADMITTED_BY_PUBLISHER`, and a rule-coverage declaration over an externally
enumerable rule set.

**Entry criteria, BOTH UNMET.**
1. **One filed COREP / FINREP / Solvency II instance.** `E2` proved addresses resolve against the
   publisher's declared scope; it did **not** prove a filed artifact carries a fact at that address,
   and supervisory filings are largely non-public.
2. **An adversarial audit of the A1 diff.** A1 was verified by probes; it has not been audited by
   anything whose default position is that every claim in it is wrong. The last such audit raised
   70 findings and 35 survived refutation.

**Positioning, unchanged and still decisive.** Where the denominator is externally fixed, a coverage
table measures **our** incompleteness. Land Path M as an overlay on the incumbent, never as a
replacement.

### A3 — THE EVIDENCE SIDE: CONTRADICT

**Delivers.** Docling ingress for the source corpus; the tabular `(value, row-label, column-header)`
triple with its geometric constraint; `Observation` / `Derivation` / `SUPPORTS` / `CONTRADICTS`; the
three-tier field surface with `Denominator.provenance` and the render refusal.

**Narrowed by F3:** exact matching only. **Narrowed by F2:** the three-tier surface must publish
`UNDERIVABLE` as a tier that renders **no fraction at all**, and the XBRL trap is explicit — an
extension taxonomy is not a field surface.

### A4 — PATH Q: PROSE TO ADMITTED CHECK

**The prerequisite changed shape.** Re-extract the pinned instrument with layout preservation, then
segment off `ListItem.marker` (F4). Cheaper than the plan assumed — and it carries a **re-pinning
event**: every offset and `text_hash` anchored to the current bytes moves. Sequence and measure that
first, as its own step, with the old and new pinnings both resolvable.

**Then.** LangExtract in strict mode per provision; the five Layer-3 gates; **precedence resolved in
Python before any engine** (F5); adjudicator kill campaigns with published false-admit rates;
`ci/barrier6.sh`; planted-obligation recall.

**Hard human blocker, unchanged.** 50 labelled proviso spans, one named labeller.
`g0_scope.py` raises `ProvisoRecallUnmeasured` on **any** STATUTE obligation until they exist, and
there is no mechanical substitute. Smallest useful version: 50 spans, `labeller` set, no κ.

**What A4 may claim** is bounded by F6: draw the demo from the FACT-shaped 702.

### A5 — FILL, AND THE ATTESTATION LANE

**Now two lanes, not one.** The FACT lane fills from evidence under the six machine-checked
admission conditions. The **ATTESTATION lane** (22 fields, a floor) raises a question to a named
human and carries their signature — it never fills. Where the model lacks the information, the
guardrail is to **ask**, not to guess.

**Gated on a negotiation, not a sprint** — 30 filing-plus-source-pack pairs — **and now also on
A1c**: a fill needs a correspondence.

---

## 6. The experiment programme, amended

The pre-registered criteria in `docs/EXPERIMENT-PROGRAMME.md` stand as written. What changed is
which experiments are still worth running.

| experiment | status now | why |
|---|---|---|
| `W0-A` · `W0-B` · `W0-C` · `W0-D` · `W0-E` | **RUN** | results in `docs/measurements/W0-results.md` |
| `E1` · `E2` · `E3` | **RUN** | selected from Wave 1 and run before development |
| `W1-3` Anchor substitution | **RECLASSIFIED as build work** | `W0-E` qualified the instrument, so the substitution was measured AS it was made |
| `W3-1` segmenter cross-layout spike | **SUPERSEDED by F4** | it would tune a regex baseline that recovers 3 numbers from 197,767 characters on the CURRENT edition. The question is no longer "is the eId a property of the law or of the PDF" but "does layout-preserving re-extraction carry the markers", and that is answered |
| `W3-3` adjudicator kill campaign | **PARTIALLY PRE-PAID by F7** | the live arm has real data: 5 of 15 refused, all 3 planted plus 2 genuine. The synthetic arm still needs drawing |
| `W2-*` evidence half | **NARROWED by F3** | the similarity arms are dead; the exact-match arms stand |
| `C5-X1` · `C5-X2` | **DELETED** | the G2 repair produces 0 admissions; measured before scheduling |

**Four experiments the spike CREATED, none of which was in the programme:**

| new | question | cost |
|---|---|---|
| **N1 · the re-pinning blast radius** | when the instrument is re-extracted with layout, how many offsets, spans, `text_hash`es and committed envelopes move — and is there a window where nothing reproduces? | 2 d, and it gates A4 |
| **N2 · the FACT/ATTESTATION classifier** | the 702/22 split was produced by a crude classifier that mislabelled at least one cell. What is the real split, on more than one return? | 2 d |
| **N3 · the negation negative control** | semantica silently ignored `not`. **Every** engine we adopt now needs a control that PROVES it honours negation and comparison before it adjudicates anything | 0.5 d, and it is reusable |
| **N4 · correspondence scored against Valentine** | does the A1c alignment beat the published schema-matching baselines, judged by somebody who did not write it? | 3 d, inside A1c |

---

## 7. The blockers that are people, not code

Neither has a mechanical substitute and both gate a phase. `PROGRESS.md` renders their state.

| blocker | gates | state today |
|---|---|---|
| **50 labelled proviso spans**, one named labeller | all of A4 | 0 spans, `labeller: null` |
| **30 filing + source-pack pairs**, real | all of A5 (G4 `BLOCKING`) | n = 40, non-synthetic 0 |
| **Cohen's κ for the stratum assignment** | the adjudication statistic | needs a second named adjudicator |
| **One filed COREP / FINREP / SII instance** | A2 entry | none held |
| **Reproduction terms for the pinned instrument** | A3 shipping to anyone | recorded NOT ESTABLISHED |

---

## 8. What is next

**Recommended order, and the reasoning is cost against what it unblocks.**

1. **The adversarial audit of the A1 diff — 1–2 days.** It is already a declared A2 entry criterion,
   it needs nothing we do not have, and A1 has been verified by probes but never attacked. Every
   previous audit of this repository found real defects; the last one raised 70 and 35 survived.
   Doing it now is cheaper than doing it after A2 builds on top.
2. **N1, the re-pinning blast radius — 2 days.** It gates the single largest saving in the plan
   (F4), and it is the kind of migration this repository has already identified as dangerous when
   landed mid-flight.
3. **A1c, field correspondence.** The longest of the three and the one that makes the schema-free
   claim true for real filer behaviour. It also unblocks A5.

**A2 stays blocked** until a filed instance exists. That is a sourcing problem, not an engineering
one, and it should be started in parallel with all three items above rather than discovered later.

**Not recommended: starting A4.** Its human blocker has not moved, and `g0_scope.py` will raise on
the first STATUTE obligation regardless of how much of the segmenter exists.

---

## 9. Two numbering sequences, and how to tell them apart

| prefix | sequence | where |
|---|---|---|
| `P0`…`P15`, `P4-B1` | the **build** phases actually shipped | `docs/measurements/P*.md`, `plan/`, the task list |
| `A0`…`A5`, `A1-4` | the **ANCHOR architecture** phases | `ARCHITECTURE-rules-and-evidence.md §9`, `PROGRESS.md`, this file |
| `W0-*`, `W1-*`, `E1`… | pre-registered experiments | `EXPERIMENT-PROGRAMME.md`, `measurements/W0-results.md` |
| `N1`…`N4` | experiments the spike created | §6 of this file |

Both sequences reached 4 independently, which is why the architecture phases were renamed to `A`:
`P4-1` and `P4-B1` used to be a decade of work apart while sharing a prefix.
