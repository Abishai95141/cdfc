# The graph spike — evidence that the propose/decide architecture works, and where it costs

Run 19 Aug 2026. **A throwaway on a deliberately different stack** — networkx + rdflib + semantica's
Datalog + Docling, with a reasoning LLM in the loop — so that nothing here inherits cdfc's habits or
its blind spots. Kept in the repository because it is the only end-to-end evidence we have for the
layer the plan calls Phase 4/5, and because two of its findings resize phases.

The scripts live in **`tools/spike/`**, not beside this file: `ci/no-bare-absence.sh` scans
`src`, `tests` and `docs`, and it correctly refused `layer3_gates.py` for claiming *"quote does not
occur in the cited provision"* without citing a validation-ledger row. (The refusal was first
attributed here to a different line reading *"provision does not exist"*; that string does not match
the gate's pattern and was not what fired.) That gate is right — an absence claim in this
repository owes a positive control — and throwaway spike code should not be the thing that earns an
exemption. The measurement record stays here; the code moved to where it belongs.

Reproduce with the probe venv at `/tmp/arch-scratch/.venv-probe` (langextract, docling,
docling-graph, semantica). `docling_markers.json` is omitted — 3,328 items, regenerable in 93 s.

---

## What was tested

    LAYER 1  deterministic   regulation text -> provisions with AKN-style eIds and exact spans
                             template        -> fields with types read from the workbook's own
                                                number formats and validation lists
    LAYER 2  the LLM         proposes rule -> field bindings, as data
    LAYER 3  deterministic   four gates decide: G-QUOTE, G-TYPE/G-FIELD, G-VOCAB, G-XREF
    LAYER 4  deterministic   graph (networkx) + RDF projection (rdflib) + queries
    LAYER 5  mixed           precedence resolved in Python, chaining in Datalog

**Only admitted proposals become nodes.** A query over the graph therefore cannot return an
ungrounded claim — the refusals are not in it.

## Result on an authored corpus

    proposals 13   ADMITTED 9   REFUSED 4        graph 29 nodes / 24 edges / 111 triples

Three refusals were planted errors and all three were caught. **The fourth was not planted:**
`reg_2` cites *"regulation 19"*, which the corpus does not contain — the gate found a hole in the
DOCUMENTS rather than in the reasoning. Zero false refusals.

## Result on the REAL IFSCA instrument and the REAL FME template

    provisions available 271 (English)      labelled template fields 724 of 3,747
    proposals 15   ADMITTED 10   REFUSED 5
    graph 1,005 nodes / 20 edges / 2,483 RDF triples
    fields governed 9 of 724        provisions cited 9 of 271

All 3 planted errors caught. **And 2 of my 12 GENUINE proposals were refused** — `G-FIELD`
refused `4. Investors!C6` and `3. Portfolio!C6`.

> **CORRECTED 19 Aug 2026, and the correction matters more than the original.** This document said
> those cells do not exist. **They do.** Both are present in the sheet XML and both are in the
> 3,747-cell field surface. `G-FIELD` was testing membership of the 724-cell LABELLED subset while
> its refusal string said *"field surface"* — so **a defect in OUR reader was published as the
> proposer's error rate.** The 2-of-12 is not a measurement of the model. The gate now separates
> `field_not_in_surface` (a bad citation) from `field_not_labelled` (a gap in what we can read),
> because the two have different remedies. Found by an adversarial audit of this file.

**That 2-of-12 was called the most useful number in this document, and it measured the wrong
thing** — see the correction above. Both cells exist and are in the field surface, so the refusals
were our reader's, not the model's. **This document therefore reports NO genuine error rate for an
LLM binding rules to fields**, and the honest statement of what it does show is narrower: 3 of 3
planted errors were caught, by gates that decide without consulting the model.

The architecture's claim is unchanged and was never a claim about accuracy: the model's errors are
meant to be CATCHABLE without a human reading every one. What this correction costs is the
evidence that they *were* caught on real artifacts — that evidence has to be re-earned, and
`docs/EVIDENCE-LAYER.md` is where the rebuilt gate is measured.

---

## THE FINDING THAT RESIZES A PHASE: the segmenter is a re-extraction problem

`docs/ARCHITECTURE-rules-and-evidence.md` §9 Phase 4 carries the provision segmenter as a hard
prerequisite costed at **6–10 weeks including the labelling to measure it**, on
the assumption that recovering `reg_8__subreg_1` from a Gazette PDF is a parsing problem.

**It is not. The numbers are absent from our pinned corpus entirely.** A line-anchored pattern finds
**3 regulation numbers in 197,767 characters** — because the corpus was extracted as FLAT TEXT and
list markers were dropped. No parser recovers them, Akoma Ntoso tooling included.

Docling's `ListItem.marker` field carries them:

    regulation-number markers recovered   294
    provisions segmented                  634
      English                             274
      Hindi (the Gazette is bilingual)    360
    distinct regulation numbers, EN       147   range 1–148

Real eIds on the real instrument. **Re-extract with layout preservation and most of that phase
disappears.**

## THE FINDING THAT CHANGES WHAT PATH Q CAN PROMISE

The toy regulation said *"maintain a net worth of not less than USD 500,000"* — bind to a money
field, compare, done. The real regulation 8(1) says:

> *"shall at all times comply with the net worth requirements **as specified in Second Schedule** of
> these regulations **or such other amount as may be specified by the Authority**."*

The threshold is in a Schedule plus an open delegation, and the only net-worth field in the whole
return is `8. Compliance Status!C6` — *"The Net worth requirement has been complied with…"*, a yes/no
**attestation**. The return never asks for the figure, so no extractor can make it checkable against
the filing. It is checkable only against the SOURCE CORPUS, which is CONTRADICT.

**The split, measured, corrects an over-generalisation made from that one sheet:**

    labelled field-surface cells   724
      FACT-shaped                  702
      ATTESTATION-shaped            22     (14 on Compliance Status, 4 on AML-CFT, 3 Introduction, 1 Complaints)

> **CORRECTED 19 Aug 2026 by `M-CEIL`.** These three numbers depend on a labelling rule this
> document did not record, and **724 is not reproducible**. Over the same 3,747-cell surface,
> "nearest text anywhere to the left" gives 3,104 fields sharing only 154 distinct labels — it
> labels ROWS — and "immediately adjacent cell is text" gives 498 fields with 481 FACT and 17
> ATTESTATION. The SHAPE holds under every rule tried: the return is overwhelmingly factual and the
> attestations are a small minority on four sheets. The RATIO must not be quoted as 702 of 724.

So the return is overwhelmingly DATA and the attestations are a small, localised minority. Both
halves matter: most fields are fillable-with-evidence, and a few require a signature no system
should forge. Note the classifier is crude — `8. Compliance Status!C7` reads as an attestation and
was labelled FACT — so treat 22 as a floor.

## SEMANTICA'S DATALOG: TWO SILENT ACCEPTANCES. Do not adjudicate with it.

It chains correctly — applicability → obligation → breach was verified. But it

* **accepts an inline comparison** (`N < T`) **and silently DROPS it**, deriving the head as though
  the comparison had never been written — a false BREACH against a filing that meets the threshold,
  which is worse than the vacuous non-derivation this document first reported; and
* **accepts `not` / `!` / `NOT` and ignores them**, deriving a breach the exception displaces.

Both are wrong answers wearing the shape of right ones, and provisos are not a corner case.

> **CORRECTED 19 Aug 2026 by `M-CEIL`.** This paragraph published **106 of 531**. Re-run against the
> pinned text it is **83 of 532** shall-bearing units, over **94** `Provided that` occurrences in the
> instrument. The argument is unchanged — roughly one shall-clause in six carries a proviso — but
> 106 is not reproducible and should not be quoted. See `docs/measurements/M-CEIL-results.md`. It also writes `\r` progress bars to **stdout** and
deleted a row of results from a three-row table.

**The repair is not a better rule.** Resolve precedence BEFORE the engine so it never needs
negation — an exception is a precedence question and precedence is computable. Verified in
`layer5b_precedence.py`: two entities with identical category and net worth, one compliant under the
proviso's lower threshold and one in breach.

---

## What this evidence supports, and what it does not

**Supports:** the propose/decide loop, on real artifacts, with a measured and fully-caught error
rate; the segmenter at a fraction of its estimated cost; the graph as a queryable object whose
coverage question answers honestly (*9 of 724* is not flattering, and that is the point).

**Does not support:** any claim about recall. Nothing here measures the rules I FAILED to propose,
and that needs labelled ground truth — the same blocker that gates the rest of the semantic half.
