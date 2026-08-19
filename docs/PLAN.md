# docs/PLAN.md — the plan of record

**The one document that describes the CURRENT plan.** Everything else is a dated record and is
deliberately not edited to match later results.

| document | what it is | edited to match a result? |
|---|---|---|
| `docs/ARCHITECTURE-rules-and-evidence.md` | the ANCHOR architecture decision, 18 Aug 2026 | no — dated decision record |
| `docs/EXPERIMENT-PROGRAMME.md` | pre-registered waves, criteria, kill rules | **never** — editing a criterion after seeing its result is the sin it exists to prevent |
| `docs/measurements/*.md`, `docs/spike/README.md` | what running them produced | no — corrections are appended in place, never overwritten |
| **this file** | what we now intend to build, and why | yes, and it names the evidence for every change |

Every checkpoint marked observed was OBSERVED by a probe in `tools/progress.py`. `make progress`
re-runs all eleven; a regression flips a checkpoint back to TODO whether or not anybody expected it.

---

## 1. Where we stand

    A0   truth, and the Path M spike                COMPLETE
    A1   the Anchor seam, second template           COMPLETE — 7 of 7 probes observed
    A1c  correspondence and entity resolution       NEW, NOT STARTED — §9
    A2   Path M and rule coverage                   NOT STARTED — 2 entry criteria unmet
    A3   the evidence side, CONTRADICT              NOT STARTED — narrowed by W0-C
    A4   Path Q, prose to admitted check            NOT STARTED — 0 of 1 probe
    A5   fill, and the attestation lane             NOT STARTED — gated on a negotiation

**TRUE today, each line traceable to a probe:** a buyer's own workbook is checked over *its own*
denominator and the wrong blank is `INVALID` with `invalid.denominator_disagreement` (`A1-3`,
`A1-4`, `A1-5`); `POST /v1/filings` binds, checks and returns **201** with the declaration, not
persisted (`A1-6`); the `Anchor` carries `(table, rows, cols)` with list-valued axes, imported by
22 modules (`A1-1`, `A1-2`); artefacts are stable across `PYTHONHASHSEED` 0/1/2 under an instrument
proven able to see a seeded perturbation (`A1-7`).

**FALSE today, and it stays visible:** the predicate library holds **0** admitted rows against
**348** rejected (`A2-2`); **0 of 4** Path M host functions registered (`A2-1`); **0** statutory
obligations (`A4-1`); no run store, no staleness policy, no deployment packaging.

---

## 2. The user flow, end to end

What a user actually does, and what the system is allowed to say back. **Two words are removed from
the original vision on purpose — *autonomously* and *zero* — and §8 F10 says why.**

1. **Upload whatever you have.** The filing template, a corpus of rules in whatever shape they
   arrive, and the operational exports — custodian feeds, trial balances, cap tables, PDF valuation
   packs. No template mapping to configure. *Not* a promise that nothing will ever need a human eye:
   real custodian feeds have merged headers, footnotes and multi-row keys.
2. **The system builds the graph.** Provisions with stable eIds and exact spans; template fields
   with types read from the workbook's own number formats and validation lists; records linked
   across documents with a **published match score**; rules bound to the fields they govern.
3. **You say which filing you want** — or you hand over the template and the question is already
   answered. There is no classifier and none is needed: it is resolution against declared inputs.
4. **The system proposes.** For every field it can evidence, a value **with the document and page it
   came from**. For every field it cannot, a named reason from a closed vocabulary.
5. **The system asks rather than guesses.** Where no grounded observation exists, it raises a
   question. Where the field asks you to *certify* rather than *report*, it assembles the evidence,
   states what is being certified and what your corpus says, and **you sign** — recorded with who,
   when, and against which evidence digest.
6. **You get the declaration.** What was checked, what nothing supports, what two of your own
   documents disagree about, and what needs your judgement — each as a counted state, not a silence.

**The sentence that survives a regulator asking "how do you know?"**

> Upload your exports in whatever shape they arrive. We read them, link the records with a published
> match score, propose a value for every field we can evidence, show the document and page each one
> came from, and tell you exactly what nothing supports, what two of your documents disagree about,
> and what needs your judgement.

The claim is **provenance, not correctness**. Ambiguity becomes a declared state with a number
rather than a silent join — the same differentiator the coverage declaration already is, extended
to identity.

---

## 3. The pipeline, sixteen steps, with what builds each

| # | step | mechanism | where |
|---:|---|---|---|
| 1 | template in → `Field` nodes with declared type, unit, vocabulary | our lxml reader (protection mask, formulas, validations) | **BUILT** — `evidence/fields.py` |
| 2 | rules in, **published as data** → `Rule` nodes carrying their own field address | DPM-XL parser + CEL compiler | **A2** |
| 3 | rules in, **as prose** → text with page/bbox provenance | Docling | A3 ingest |
| 4 | prose → `Provision` nodes with stable eIds and spans | **Docling `ListItem.marker`** + segmenter | **BUILT, coordinate-addressed** — `evidence/provisions.py`; durable eIds need the re-pin (`N1`) |
| 5 | `Provision` → `Rule` proposals | LangExtract strict, gated | **SEAM BUILT** — proposals load as DATA; LangExtract not wired |
| 6 | `Rule --governed_by--> Field` | **free on Path M**; type-gated on Path Q | **BUILT for Path Q** — the five gates, `evidence/gates.py` |
| 7 | `Rule --applies_when--> Rule`, conditional obligations | **Datalog chaining, ours** (§8 F5) | **A2** |
| 8 | financial records in → `Document`, `Span`, `Observation` | Docling + CSV/xlsx readers | A3 |
| 9 | source column → template `Field` | composed template-anchored schema matcher | **A1c** |
| 10 | record ↔ record across sources | **Splink** | **A1c** |
| 11 | *"which filing do I want"* | resolution against declared inputs — **collapses into step 6** | not a component |
| 12 | for each `Field`: which rules govern it, which observations could fill it | graph traversal | **BUILT for rules** — `evidence/graph.py`, `query.py`; observations are A3 |
| 13 | is 250,000 below 500,000 | **CEL** | **EXISTS** |
| 14 | does the obligation apply, is it breached | **Datalog** | A2 |
| 15 | value = sum of these three observations | derivation | A3, partially designed |
| 16 | write it into the return | fill / writeback | A5, gated commercially |

**Step 11 used to be listed as an unplanned classifier.** It is not one. If the user uploads the
template, *"which filing"* is answered by the artifact; if they name it, that is resolution against
a declared input; and a bare filing already binds by structural fingerprint against the pinned
catalogue. The real question was always *"which of the uploaded rules govern this template's
fields"* — which is step 6.

**Five of the sixteen now run in `src/`** via `cdfc evidence`, on the real instrument and the real
return, with every gate observed refusing its own planted error. `docs/EVIDENCE-LAYER.md` records
what it measured and the three defects it had first. What it does NOT cover is listed there and in
the rows above.

---

## 4. Three machines get called "reasoning", and conflating them is how systems guess confidently

| | question | machine | state |
|---|---|---|---|
| **Deduction** | registered non-retail ⟹ regulation 8(1) applies ⟹ breached | **Datalog** | verified working in the spike |
| **Computation** | is this value below that threshold | **CEL** | exists, 12,850 of 12,925 EBA rules compile |
| **Association** | which record belongs in this field | **Splink + schema matching** | **this is not reasoning** — it is matching with a score |

**They must stay separate, and that is forced by measurement rather than taste.** The Datalog
engine we tried **accepted an inline comparison and derived nothing** — CEL does comparisons
natively and is already gated. So: **CEL computes the atoms; Datalog chains them.**

Treating association as reasoning is precisely how a system talks itself into confidence.

---

## 5. Meaning enters through three doors, and only one needs inference

**Door 1 — the regulator addresses its own rule.** `with {tC_25.01.a, r0010, c0060}: {r0040} =
{r0050} + {r0060}`. There is nothing to infer; the data point is in the expression. **18,826 of
18,827** addresses resolve against the rule's own declared scope. This is why Path M is first: it is
the semantic problem already solved by the publisher.

**Door 2 — the template encodes its own meaning.** `=SUM(D18:D20)` *means* "the total of those". A
validation list *means* a closed vocabulary. A protection mask *means* "a filer writes here". We
already induce **571** checks from nine workbooks with zero NLP.

**Door 3 — prose, and it is the weak one.** The ceiling is low and now measured: of **532**
shall-bearing units, at most **155** carry both a comparator and its value (`M-CEIL`). LangExtract
grounds the *quote*, never the *rule* — its `attributes` dict carries no offsets, so `USD 75,000`
can be located while the claim *"this threshold governs field X"* stays ungrounded.

### The mechanism that makes door 3 safe comes from door 2

**A rule→field binding is a claim, and claims can be gated mechanically.** The template's own
declarations become the type system that adjudicates semantic bindings:

| the rule says | the field must declare |
|---|---|
| "not less than USD 75,000" | numeric, money-formatted, unit USD |
| "within thirty days" | a date, or a date-validated cell |
| "as a Company, LLP or Trust" | a list validation whose vocabulary covers those |
| "shall not exceed 49 per cent" | a percentage-formatted numeric |

A model proposes *"regulation 8(1) governs `1. Introduction!D40`"*; the induction layer refuses it
because D40 is date-validated and the rule needs money. **Deterministic, no labels, and it uses
evidence we already extract.** This is `G-TYPE`.

**The gap worth naming: there is no published benchmark for rule→field binding.** Entity matching
has one — roughly 87.5 F1 is quotable. Rule→field binding returns vendor claims and patents, not
evaluated methods. We would be building the measurement ourselves, which lands back on the 50
labelled spans. That is the argument for shipping doors 1 and 2 first, where meaning is *given*
rather than inferred.

### Every rule carries where it came from

    PUBLISHER   the regulator published it as data           (Path M)
    TEMPLATE    the blank encodes it                         (formula / validation / mask)
    STATUTE     derived from pinned text, quote byte-exact   (Path Q, gated)
    ASSERTED    the user typed it in a prompt                (runs, labelled, never attested as the regulator's)

An `ASSERTED` rule — *"treat side letters as binding, use Q3 NAV"* — still executes and still
contributes to coverage. It simply cannot claim a regulator said so, and it cannot carry the same
severity. That is how a typed user instruction enters the system without contaminating the
attestation.

---

## 6. The guardrails, and the one rule about when they fire

**Layer 3 of the spike — the gates that adjudicate a proposal:**

    G-QUOTE   the cited text is byte-exact at the cited span
    G-FIELD   the cited cell EXISTS in the template's field surface
    G-TYPE    the predicate's type matches the field's DECLARED type (§5)
    G-VOCAB   every term is in the closed vocabulary
    G-XREF    every cross-reference resolves to a provision that EXISTS

**Only admitted proposals become nodes**, so a query over the graph cannot return a refused claim.
Composed with the older set: `G0`–`G4` qualify a predicate; `BANNED_IN_VERDICT` plus
`ci/barrier5.sh` enforce by import closure that no model reaches a verdict; `ci/GATES.md` is an
append-only registry where every row names the injector that makes it red.

**Measured, on real artefacts:** of 15 proposals, 10 admitted, 5 refused — all **3 of 3** planted
errors. The architecture never claimed the model is accurate; it claims the model's errors are
catchable without a human reading every one.

**The other 2 refusals were the GATE's defect, not the model's**, and an adversarial audit of this
plan found it. Those two cells exist and are in the field surface; `G-FIELD` was testing the
LABELLED subset while its reason said *"field surface"*. **So there is no measured genuine error
rate for the proposer** — the number that was quoted as one measured our reader. The rebuilt gate
in `src/cdfc/evidence/gates.py` separates the two reasons.

### THE TRIGGER MUST BE MECHANICAL, NEVER THE MODEL'S OWN CONFIDENCE

"If the model doesn't know, ask rather than hallucinate" is right, and the trigger must not be the
model's sense of uncertainty — that is the exact quantity measured unreliable. LLM confidence in
entity matching is poorly calibrated and systematically overconfident; fine-tuned matchers lose
36–56 F1 transferred to an unseen dataset; and `W0-C` measured similarity locate returning
SUPPORTED **20 of 20** for values deleted from the corpus, at every threshold tried.

    is there a grounded observation for this field — a source span that re-verifies byte-exact?
        YES -> propose      NO -> ask

That is a lookup, not a judgement, and it cannot talk itself into confidence. **The states already
exist:** `no_predicate.*` and `not_run.*` are closed "I don't know" vocabularies. What is missing is
wiring them to a *question* instead of a silent gap. That is a build item, not a research one.

### The attestation flow

The value is not the prompt, it is what is attached to it.

> *"Tick yes for net worth compliance?"* → the user rubber-stamps.
>
> *"Regulation 8(1) requires compliance with the Second Schedule net-worth requirement. Your Q3
> balance sheet (page 4) shows USD 380,000. This attestation asks you to certify compliance."*
> → that is a decision.

The system assembles the evidence, states what is being certified and what the corpus says, and a
**named human signs**. Who signed, when, and against which evidence digest is the four-eyes audit
trail. Our attestation layer already signs statements, so it can sign a `Disposition` too.

---

## 7. The tech-stack register

**A REJECTED verdict is as load-bearing as an adoption and is recorded with its evidence.**

| library | version | verdict | measurement |
|---|---|---|---|
| `lxml` | 6.1.1 | **ADOPTED, runtime** | the only workbook reader; `ci/no-regex-over-xml.sh` guards it |
| `cel-python` | 0.5.0 | **ADOPTED, runtime** | 14 distinct function-like tokens across 12,925 foreign rules, **0 unknown constructs** |
| `openpyxl` | 3.1.5 | **ADOPTED as a READER ONLY** | banned as a writer (NC-P04): a round-trip rewrites fingerprint bytes |
| `pypdfium2` / `pdfplumber` | 5.13.0 / 0.11.10 | **ADOPTED, build-time only** | nothing in `src/` imports them |
| `pymupdf` | — | **REJECTED on licence** | AGPL-3.0. **It was the arm that scored best**, and it is still refused |
| **Docling** | 2.120.3 | **ADOPT** | `ListItem.marker` → 294 markers → 634 provisions, 147 distinct regulation numbers. **Trap: it drops formulas from spreadsheets** — fine for source documents where you want values, fatal for templates where you want rules |
| **LangExtract** | 1.6.0 | **ADOPT for A4, `MATCH_EXACT` + byte equality only** | grounds the quote, not the rule (§5) |
| **networkx + rdflib** | 3.6.1 / 7.6.0 | **ADOPT for the graph projection** | 1,005 nodes / 2,483 triples over real artefacts, queried |
| **Datalog, the FORMALISM** | — | **ADOPT — implement it ourselves** | Horn clauses with semi-naive fixpoint express the conditional obligation our `Obligation` type cannot (audit Gap 2). A few hundred lines against our own gates |
| **semantica, the LIBRARY** | 0.6.5 | **REJECTED** | accepts an inline comparison and derives nothing; **accepts `not` / `!` / `NOT` and ignores them**. Its `reasoning_provenance` design is worth borrowing; its `strategy="fuzzy", similarity_threshold=0.7` resolver is a knob and must not be. Also writes `\r` progress bars to stdout from a library call |
| **Splink** | — | **PLANNED, A1c** | Fellegi-Sunter under unsupervised EM: a **derived** match weight, not a threshold somebody tunes until the demo passes |
| Zingg · dedupe | — | **ALTERNATES to Splink** | evaluated on paper; named so the choice is a choice |
| Valentine (COMA, Cupid, Similarity Flooding, EmbDI) | — | **BENCHMARK, not a dependency** | what A1c must be scored against so the number is not self-graded |
| Arelle | — | **PLANNED as the external ORACLE** | the only third-party executor of a publisher's own formula linkbase in reach |
| Akoma Ntoso + Slaw | — | **NOT NEEDED for IFSCA** | AKN's `eId` scheme is the right *idea* and Slaw is a real parser. Docling's markers made it unnecessary here; revisit per instrument |
| **Cognee** | — | **EVALUATE, for §10** | the most complete document-centric graph builder: automated ontology, incremental updates, cross-document entity resolution |
| LlamaIndex `PropertyGraphIndex` | — | **REJECTED for §10** | the schema must be defined manually upfront — the opposite of schema-free |
| Graphiti | — | **NOT APPLICABLE** | temporal, built for episodic streams, not static corpora |
| GraphRAG | — | **REJECTED** | reported prohibitively expensive for practical deployment; frequent LLM calls |
| an LLM API | — | **NOT IN THE RUNTIME, BY CONSTRUCTION** | `BANNED_IN_VERDICT` + `ci/barrier5.sh` |

**The runtime closure is deliberately tiny and must stay so.** Docling, LangExtract, networkx and
rdflib enter as **build-time or proposal-time** dependencies producing pinned artefacts; they do not
join the closure of the code that issues a verdict. Changing that is an architecture decision, not
a `pip install`.

**The rule that governs every graph builder above: no LLM-extracted edge enters the graph
unadjudicated.** Propose freely, decide deterministically — the same seam as everywhere else.

---

## 8. The findings that changed the plan

### F1 · Path M is real, and bigger than the plan sized it
12,925 EBA rules, **every one** carrying a machine-parseable expression; **12,850 of 12,925**
compilable with four bounded host functions and **not one ban weakened**; **18,826 of 18,827**
addresses resolve; EIOPA publishes **6,767** more in a different notation over the same
`{table, row, column}` shape. **CHANGES A2:** the risk is not vocabulary but **one structural
construct** — 12,448 of 12,925 expressions open with a `with {…}` context header CEL has no
equivalent for. A2 is a context-binding compiler, not a token translator.

### F2 · The denominator survives off Excel
**13 of 16** blanks DERIVED, including all four AcroForm PDFs. The "structured formats only"
fallback is NOT triggered. Two cautions travel with it: the DOCX family is **n = 1** and negative,
and the two XBRL counts are extension-taxonomy concepts that **must never be read as denominators**.

### F3 · Similarity matching manufactures support
**0 of 20** blanked values reported SUPPORTED under exact matching; **20 of 20** under similarity,
on evidence that had been deleted. **CHANGES A3:** the evidence half ships **exact matching only**.

### F4 · The segmenter is a RE-EXTRACTION problem
A line-anchored pattern finds **3 regulation numbers in 197,767 characters** — reproduced
first-hand by `M-CEIL` — because the pinned corpus is FLAT TEXT and the list markers were dropped.
No parser recovers them, Akoma Ntoso tooling included. Docling's `ListItem.marker` carries them.
**CHANGES A4 in both directions:** most of the 6–10 weeks disappears, **but re-extraction changes
the instrument's bytes** and every offset, span and `text_hash` anchored to them moves. That is a
re-pinning event with a blast radius, sequenced and measured as `N1`.

### F5 · Adopt Datalog the formalism; reject the library we tried
Two silent acceptances, either of which produces a wrong answer wearing the shape of a right one.
**CHANGES A4's Layer 5 and A2's step 7:** implement semi-naive fixpoint ourselves against our own
gates, **and resolve precedence in Python BEFORE the engine so it never needs negation** — an
exception is a precedence question and precedence is computable. Demonstrated on two entities with
identical category and net worth, one compliant under the proviso's lower threshold, one in breach.

### F6 · What Path Q can promise is narrower than the flagship implies
Regulation 8(1) requires net worth *"as specified in Second Schedule … or such other amount as may
be specified by the Authority"* — a Schedule plus an **open delegation** — and the only net-worth
field in the return is a yes/no attestation. **CHANGES what A4 may demo:** that obligation is
checkable against the **source corpus** (CONTRADICT), never against the filing.

### F7 · The propose/decide loop works, with a measured error rate
Toy: 13 proposals, 9 admitted, 4 refused — 3 planted and **one that was not**, where a rule cited a
regulation the corpus lacks, so the gate found a hole in the DOCUMENTS. Real: 15 proposals, 10
admitted, 5 refused — 3 of 3 planted plus **2 of 12 genuine**. Recall stays unbounded.

### F8 · Graded binding is unsafe, and correspondence is one component with entity resolution
A row insertion renumbers every cell below it: of 3,747 addresses 3,544 are common to both
files, and **1,451 of those hold a DIFFERENT field** — the `3. Portfolio` cells at or below the
inserted row. The other 2,093 hold the same field (44 above the insertion, 2,049 on the seven
sheets whose worksheet XML is byte-identical). *This document first said all 3,544 held different
fields, a 2.4x overstatement corrected by audit; 1,451 silently mislabelled cells is still the
wrong-form failure strict binding exists to prevent.* **ADDS A1c** — and the component is bigger than form-alignment.
*Aligning two versions of a form* and *aligning a cap-table row to a custodian record* are the same
operation: establish which thing here **is** which thing there, refuse when ambiguous, declare what
did not align. **Build it once, and build it before the evidence graph** — a graph is worth little
if its nodes cannot be identified across sources.

### F9 · G2 is a statistic, not a veto
**222** unverifiable / **93** no-kill / **33** no-margin / **0** admit, summing to 348. Repairing
`observable()` produces zero admissions. Path M rules are `ADMITTED_BY_PUBLISHER`.

### F10 · The filing-checkable ceiling is lower than the pattern count, and two published numbers do not reproduce
`M-CEIL`, run first-hand against the pinned artefacts:

* at most **155 of 532** shall-bearing units carry both a comparator and its value, against an
  earlier pattern-only estimate of roughly 176 of 531 — the subtraction is delegation and
  definitions, the two ways a clause can look testable and not be;
* provisos: published **106 of 531**, re-run **83 of 532** over **94** `Provided that` occurrences.
  The argument survives — roughly one shall-clause in six — the number does not;
* the labelled field population **moves sixfold with an unwritten convention**: 3,104 fields (154
  distinct labels — it labels *rows*), or 498 (127 distinct), or the spike's unreproducible 724.
  The FACT/ATTESTATION *shape* holds under every rule; **the ratio 702 of 724 must not be quoted.**

**CHANGES A5's scoping and adds `N2` with a prerequisite:** pin the labelling rule before measuring
anything over it. This is the count-vs-contents defect again, on the denominator of the semantic
half.

---

## 9. The phases, revised

### A1c — CORRESPONDENCE AND ENTITY RESOLUTION · new, and it moved EARLIER
**One component, three uses:** align a filing to its blank; align a source column to a template
field; align a record to a record across documents. **Delivers** an alignment that survives
insertion, deletion and reordering; coverage scored over the correspondence with unaligned fields
declared on **both** sides; and a **refusal when ambiguous** — two candidate alignments of similar
quality is the same hazard as two pinned blanks sharing a sheet set.

**Splink rather than a threshold**, because `W0-C` measured what happens when a similarity judgement
is trusted. **Scored against Valentine** so the number is not self-graded. **Exit:**
`row-inserted__portfolio-r7.xlsx` is checked rather than refused, and a negative control proves a
mis-aligned pair is REFUSED rather than scored.

### A2 — PATH M AND RULE COVERAGE
The `with {…}` context compiler, four host functions, rules `ADMITTED_BY_PUBLISHER`, our own
Datalog chaining for conditional obligations, and a rule-coverage declaration.
**Entry criteria, BOTH UNMET:** one filed COREP/FINREP/Solvency II instance (`E2` proved addresses
resolve against the *publisher's declared scope*, not against a filed artifact); and an adversarial
audit of the A1 diff (verified by probes, never attacked). **Positioning:** land Path M as an
overlay on the incumbent, never a replacement.

### A3 — THE EVIDENCE SIDE: CONTRADICT
Docling ingress; the tabular `(value, row-label, column-header)` triple with its geometric
constraint; `Observation` / `Derivation` / `SUPPORTS` / `CONTRADICTS`; the three-tier surface with
`Denominator.provenance` and the render refusal. **Exact matching only** (F3). `UNDERIVABLE` renders
**no fraction at all**.

### A4 — PATH Q: PROSE TO ADMITTED CHECK
**Re-pin first** (`N1`), then LangExtract strict per provision, the five gates, precedence before
the engine, adjudicator kill campaigns with published false-admit rates, planted-obligation recall.
**Hard human blocker:** 50 labelled proviso spans; `g0_scope.py` raises on any STATUTE obligation
until they exist. Demo drawn from the FACT-shaped fields (F6).

### A5 — FILL, AND THE ATTESTATION LANE
Two lanes. **FACT** fills from evidence under the six machine-checked conditions. **ATTESTATION**
assembles evidence, states what is certified, and a named human signs — it never fills. Gated on 30
filing-plus-source-pack pairs **and on A1c**: you cannot fill a form you cannot align.

---

## 10. The architectural question that WAS open — decided 20 Aug 2026

**The architecture made the evidence graph a PROJECTION of a run — emitted, never stored** — because
a critique showed a graph-native rewrite bought nothing a buyer could see.

**The user flow in §2 needs the opposite:** a graph that persists across uploads and is queried by a
later prompt. Upload rules today, upload financials next week, ask for a filing the week after.

**RESOLVED by `N5`. See `docs/decisions/D-A3-01-the-graph-is-re-derived-not-stored.md`.**

**What persists is the ARTEFACT SET; the graph is re-derived, never stored.** The measurement
dissolves the dilemma: re-deriving the whole graph from pinned artefacts takes **0.41 s** (1,722
nodes), and nine pinned blanks plus the 1,218-unit instrument take **0.63 s** (3,550 nodes). The
projection is a deterministic fold — the sorted triple set digests identically under
`PYTHONHASHSEED` 0/1/2 — and the control holds, because the digest moves when the template changes
or a proposal is added.

So every upload pins an artefact and a run names which artefacts it used. Rules uploaded today and
financials uploaded next week are two pinned artefacts; the filing run names both. **The evidence
survives across uploads; a derived index of it does not need to.**

A mutable store is not merely unnecessary but unsafe: `run_id_for` is a digest of the inputs, so
accumulated state would give two runs over identical inputs one id with different answers, and
`store.write()` overwrites in place. **Cognee is REJECTED for this path** — its value is
LLM-extracted edges, which cannot enter unadjudicated, and the problem it solves is measured at
0.63 s. The build task this creates is an **artefact registry**, not a graph database.

**What it does NOT establish:** that re-derivation stays cheap at every scale. A corpus of thousands
of source PDFs is a different population, and re-measuring the fold is now a named `A3` entry
criterion rather than an assumption.

**Also unresolved, and smaller:** the coverage vocabulary needs more than governed/ungoverned. In
the spike, two fields were *read as conditions* without being *governed*, and the query reported
them as untouched. That is a third state and it is missing.

---

## 11. The experiment programme, amended

Pre-registered criteria stand as written; what changed is which experiments are worth running.

| experiment | status | why |
|---|---|---|
| `W0-A`…`W0-E`, `E1`, `E2`, `E3` | **RUN** | `docs/measurements/W0-results.md` |
| `M-CEIL` | **RUN** | `docs/measurements/M-CEIL-results.md` — the ceiling, and three re-runs |
| `W1-3` Anchor substitution | **RECLASSIFIED as build work** | `W0-E` qualified the instrument; measured as it was made |
| `W3-1` segmenter cross-layout | **SUPERSEDED by F4** | it would tune a baseline that recovers 3 numbers from 197,767 characters |
| `W3-3` adjudicator campaign | **PARTIALLY PRE-PAID by F7** | the live arm has real data; the synthetic arm still needs drawing |
| `W2-*` evidence half | **NARROWED by F3** | similarity arms dead, exact-match arms stand |
| `C5-X1`, `C5-X2` | **DELETED** | the G2 repair produces 0 admissions |

**Two figures `W1-4` pre-registered have moved, and the pre-registration is NOT edited.**
`EXPERIMENT-PROGRAMME` requires `make verify` to return *"the same integers, not merely green"* —
`(1,600, 1,600)` tests and `(115, 125)` gates observed red. Neither holds now. The test count has
drifted twice with nothing asserting it, so the README no longer quotes one. The gate figure is
**104 of 125**, and it moved because the evidence stopped being asserted by a hand-maintained map
and started being derived from the sweep's own per-guard record — the criterion did not fail, the
number it was written against was wrong. `(141, 141)` entries and `(230, 230)` guards still hold.

**Five experiments the spike and M-CEIL created:**

| new | question | cost |
|---|---|---|
| **N1 · re-pinning blast radius** | when the instrument is re-extracted with layout, how many offsets, spans, `text_hash`es and committed envelopes move, and is there a window where nothing reproduces? | 2 d, **gates A4** |
| **N2 · the labelling rule, then the split** | pin what "this field has a label" means BEFORE measuring FACT vs ATTESTATION over it — the denominator moved sixfold | 2 d |
| **N3 · the negation negative control** | every engine we adopt must PROVE it honours negation and comparison before it adjudicates | 0.5 d, reusable |
| **N4 · correspondence vs Valentine** | does A1c beat the published baselines, judged by somebody who did not write it? | 3 d, inside A1c |
| **N5 · the persistent-graph decision** | **RUN 20 Aug 2026 — `D-A3-01`.** Re-derivation measured at 0.41 s / 0.63 s and proven a deterministic fold; artefacts persist, the graph does not; Cognee rejected | ~0.5 d |

---

## 12. The blockers that are people, not code

| blocker | gates | state |
|---|---|---|
| **50 labelled proviso spans**, one named labeller | all of A4 | 0 spans, `labeller: null` |
| **30 filing + source-pack pairs**, real | all of A5 (G4 `BLOCKING`) | n = 40, non-synthetic 0 |
| **Cohen's κ for the stratum assignment** | the adjudication statistic | needs a second named adjudicator |
| **One filed COREP / FINREP / SII instance** | A2 entry | none held |
| **Reproduction terms for the pinned instrument** | A3 shipping to anyone | recorded NOT ESTABLISHED |

---

## 13. What is next

1. ~~The persistent-graph decision (`N5`)~~ — **DONE 20 Aug 2026**, `D-A3-01`. Artefacts persist,
   the graph is re-derived. A1c and A3 are both unblocked, and A3's shape is settled: a projection
   layer over pinned source artefacts, plus an artefact registry.
2. **The adversarial audit of the A1 diff — 1–2 days.** Already a declared A2 entry criterion, needs
   nothing we lack, and A1 has been verified by probes but never attacked.
3. **`N1`, the re-pinning blast radius — 2 days.** Gates the single largest saving in the plan.
4. **A1c.** The longest, and the one that makes schema-free true for real filer behaviour.

**A2 stays blocked** on a filed instance — a sourcing problem to start in parallel, not to discover
later. **A4 should not start:** its human blocker has not moved and `g0_scope.py` will raise on the
first STATUTE obligation regardless of how much segmenter exists.

---

## 14. Two numbering sequences

| prefix | sequence | where |
|---|---|---|
| `P0`…`P15`, `P4-B1` | the **build** phases shipped | `docs/measurements/P*.md`, `plan/`, the task list |
| `A0`…`A5`, `A1-4` | the **ANCHOR architecture** phases | `ARCHITECTURE §9`, `PROGRESS.md`, this file |
| `W0-*`, `E1`… | pre-registered experiments | `EXPERIMENT-PROGRAMME.md` |
| `M-CEIL`, `N1`…`N5` | experiments this work created | §11 |

Both sequences reached 4 independently, which is why the architecture phases were renamed to `A`.
