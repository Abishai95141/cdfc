# M-CEIL — the filing-checkable ceiling, and three published numbers re-run

Run 19 Aug 2026 at `6d3582e` by `tools/measure/ceiling.py`, against the pinned instrument
(`corpus/instruments/statute-fm-regulations-2025.text.json`, 197,767 characters, 1,218 units) and
the pinned FME return over **the repository's own field surface**, not a second reader.

**Why it was run.** `docs/spike/README.md` records that regulation 8(1) is inside the ~176-of-531
"testable content" estimate by pattern and is still not checkable against this filing, and says the
true ceiling *"is lower than the text-level count suggests, and I'd want that measured properly
before Phase 5 is scoped."* This is that measurement. Two other published numbers were re-run at the
same time because they were cheap, and **two of the three do not reproduce.**

---

## Stage 0 — reproducing what has been published

| published | where | re-run | verdict |
|---|---|---:|---|
| naive line-anchored regulation numbers: **3** | `docs/spike/README.md` | **3** (3 distinct) | **REPRODUCES** |
| `Provided that` occurrences: **93** | `docs/EXPERIMENT-PROGRAMME.md §5` | **94** | **CORRECTED** |
| clauses carrying a proviso: **106 of 531** | `docs/spike/README.md` | **83 of 532** | **CORRECTED** |

The proviso figure is the one that matters, because it is the argument for handling provisos as a
first-class case rather than a corner case. **That argument survives the correction** — 83 of 532 is
still roughly one shall-clause in six — but the published number was not reproducible from the
pinned text under any reading of *clause* this script can construct, and it should not be quoted
again.

## Stage 1 — every `shall` clause, classified

**1,218 pinned units; 532 contain `shall`.** One class per clause, first match wins, ordered
most-disqualifying first.

| class | count | what it means for a filing check |
|---|---:|---|
| `QUANTIFIED_IN_CLAUSE` | **128 of 532** | a comparator AND its value are both present |
| `TEMPORAL_ONLY` | **27 of 532** | a deadline, checkable if a date field exists |
| `DELEGATED_ELSEWHERE` | **8 of 532** | comparator present, value in a Schedule or delegated to the Authority |
| `DEFINITION` | **4 of 532** | *"'control' shall include…"* — carries quantities, defines a term, tests nothing |
| `PROVISO_ONLY` | **34 of 532** | an exception with no testable content of its own |
| `NO_TESTABLE_CONTENT` | **331 of 532** | no quantity, no comparator, no temporal marker |

**Negative control: every class is reachable on this corpus — PASS.** A classifier that puts
everything in one bucket produces a clean number and has measured nothing, so this is checked
rather than assumed, and one real clause per class is printed with the totals.

**The ceiling from the instrument side: 155 of 532**, against the earlier pattern-only estimate of
roughly 176 of 531. The subtraction is small in absolute terms and it is the *right* subtraction:
delegation and definitions are exactly the two ways a clause can look testable and not be.

### Two classifier defects, found by reading the examples rather than the totals

1. **`Rs\.?` under `re.I` matched the "rs" inside `forms`, `advertisers`, `matters`.** The first run
   put **228 of 532** in the quantified bucket, headed by a pure definition of *"advertisement"*.
   Every alternative is now word-bounded. A currency abbreviation that matches inside ordinary
   words is a classifier that has measured nothing.
2. **Definitions carry quantities.** *"'control' shall include the right to appoint a majority …
   a parenthesised voting-rights threshold"* trips every quantity pattern, and no filing tests
   it against. `DEFINITION` was added and ordered ahead of the quantity test.

Both were caught only because the script prints a verbatim example per class. Totals alone would
have shipped 228.

## Stage 2 — the return's fields, and a denominator that moves sixfold

Over the repository's own **3,747-cell** field surface — the same denominator every run is scored
over, not a private re-derivation.

| labelling rule | fields | distinct labels |
|---|---:|---:|
| **A** — nearest text anywhere to the left on the row | **3,104 of 3,747** | **154** |
| **B** — the immediately adjacent cell is text | **498 of 3,747** | **127** |
| **C** — the rule `docs/spike/README.md` used | **724 of 3,747** | unrecorded |

**Rule C is not reproducible.** The spike published 724 labelled fields and a 702 / 22 FACT vs
ATTESTATION split over them, and did not record which rule produced 724.

**The distinct-label count is what gives Rule A away.** 3,104 fields sharing 154 labels means the
rule is labelling *rows* — one row header reused across every column in the row. It must never be
used as a denominator. Reported over Rule B:

    FACT-shaped          481 of 498
    ATTESTATION-shaped    17 of 498      <- a FLOOR
      1. Introduction  3    6. Complaints  1    7. AML-CFT  5    8. Compliance Status  8

**The shape of the finding survives; the numbers do not.** The return is overwhelmingly factual and
the attestations are a small, localised minority on four sheets — that was the product-relevant
conclusion and it holds under every rule tried. What does not hold is quoting *702 of 724*: the
labelled population is a property of an unwritten convention, and it moves by a factor of six
across three defensible readings of the same 3,747 cells.

**This is the count-vs-contents defect again, on the denominator of the semantic half.** A count
that agrees with nothing about its own contents is evidence about the count.

---

## What this bounds, and what it does not

**Bounds, from the instrument side:** at most **155 of 532** shall-clauses have both a comparator
and its value in the clause. Every count here is over a **fragment** population — the pinned units
are page-sentences, and `p0143.s0018` opens mid-clause on a bare threshold fragment. The provision
segmenter is what fixes that, and until it lands this number is over the wrong unit.

**Does not bound:** the intersection. The real ceiling is *clauses that survive **and** bind to a
FACT-shaped field*, and performing that binding is the rule→field problem this measurement
deliberately does not attempt. The two sides are reported separately so neither is multiplied into
a number nobody measured.

## Miss modes, published with the number

1. The pinned units are **page-sentences, not provisions**; a clause split across two units is
   classified twice, on fragments.
2. `DELEGATED_ELSEWHERE` is detected by phrase — a clause pointing at a Schedule without one of
   those phrases scores as quantified.
3. Stage 2 reads the label to the **left**; a field labelled above its column is skipped rather
   than guessed, so every labelled population here is a floor.
