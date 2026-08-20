# N1b — the re-pin, executed. And the finding that made it free

*Run 20 Aug 2026 at `c2e2151` by `tools/repin_divisions.py` and `src/cdfc/qualify/provisions.py`.
Supersedes nothing in `N1`; it corrects one of its conclusions and one of `PLAN.md §8 F4`.*

---

## 1. `F4` IS FALSE, and the count that established it was never opened

`docs/PLAN.md §8 F4` and `docs/spike/README.md` both carry this, as the finding that resizes a phase:

> **It is not. The numbers are absent from our pinned corpus entirely.** A line-anchored pattern
> finds **3 regulation numbers in 197,767 characters** — because the corpus was extracted as FLAT
> TEXT and list markers were dropped. No parser recovers them, Akoma Ntoso tooling included.

**The 3 is a true count of one construct, published as a total over two.** Measured on the pinned
text, the regulation numbers are present, at the END of the heading unit, where the Gazette's
margin column puts them:

    p0148.s0007   'Net worth requirements 8'
    p0158.s0000   'Minimum number of Investors 44'
    p0170.s0007   'Trust 85'
    p0161.s0009   'Nature and Structure of Scheme 56'

A pattern anchored on `^\d{1,3}\.` cannot see one of those. The 3 it found are exactly the three
provisions the Gazette sets inline instead — `'75. (1) A FME shall enter into…'`, `'128. (1) All
fees…'`, `'142. The Authority may…'` — which is why the number looked like a floor rather than an
artefact of the pattern.

| where the numbers were looked for | found |
|---|---:|
| `^(\d{1,3})\.\s` at line start — **the F4 pattern** | 3 |
| a bare number at a heading unit's END | 147 |
| **both, reconciled on one ascending chain** | **147** |

Docling — a third, independent reading with layout preservation — recovers **147** English
regulation markers over the same instrument. **146 of the two sets agree.** The one on each side:

* **138 party-only.** `'CHAPTER IX INSPECTION AND AUDIT Inspection 138'`, AGREED by both PDF
  parties, and docling emits no marker for it.
* **100 docling-only.** Its heading is inside the 28-unit disputed region on page 177. Our two
  parties disagree there, so it is correctly *not addressable* — `anchor_disputed`, and the remedy
  is a third competent party rather than a better parser.

**The consequence is that the re-pin needed no re-extraction.** The boundaries come out of text the
two parties had already corroborated, which is better evidence than a third reader's opinion, and
docling's role drops from *the only way to get eIds* to *an independent check on a set we already
had*. It is not a dependency of anything.

## 2. What the re-pin actually cost, against what `N1` predicted

`N1` concluded: *"a re-pin invalidates 100% of citations made against the current corpus."* That was
measured on a `RESEGMENT` arm and **is true of a resegmentation**. This is not one.

| | before | after |
|---|---|---|
| text | 197,767 chars | **identical** |
| units | 1,218 | **identical**, every key, page, span, corroboration |
| disputed regions | 28 | **identical** |
| digest over text + units | `6c0b2b8df8baeb4a…` | **`6c0b2b8df8baeb4a…`** |
| instrument digest | `7e4321e8bb9e750a…` | `5e4a4310c2a18f0a…` |
| provision citations invalidated | *predicted 11 of 11* | **0 of 11** |

`tools/repin_divisions.py` REFUSES to write if the text or any unit moved, for all ten instruments;
the table above was then re-derived independently against a copy taken before anything was written.
The instrument digest moved because the division map joined the payload it covers — which is the
deliberate act `N1` said a re-pin has to be.

**`tests/golden/test_textsource_pins.py` could not tell those two apart and reported the wrong one.**
It pinned one digest and its docstring read *"moving any number here means the addressable text
moved, and every span recorded against this instrument now points at different characters."*
Nothing pointed anywhere new. `ADDRESSABLE_SHA256` — text and units and nothing derived — is now
pinned separately, and it is the one that must never move.

## 3. What was recovered

    regulations (run 1)         147     ordinals 1..148, gap at 100
    schedules   (run 2)           6     ordinals 1..6
    subdivisions (depth 1)      464
    ------------------------------------------------------------------
    divisions total             617     over 1,218 units
    refused                      58     every one with a reason from a closed vocabulary
    units in no division          3     the two-unit preamble and the notification line
    wall clock                0.13s

Refusals, by reason:

| reason | n | what it means |
|---|---:|---|
| `unstable_position` | 24 | two equally good readings place it differently; refused, not picked |
| `not_on_ascending_chain` | 20 | a number in running text — `'…as such by the FME 7'` |
| `not_a_new_sequence` | 6 | a later run opening at ordinal 2; these are subdivisions, already addressed |
| `anchor_disputed` | 5 | the parties disagree where the heading is |
| `ordinal_skipped` | 3 | no admitted marker carries it, and the region is not disputed |

**All nine pinned workbooks recover 0 divisions.** That is the honest degrade, not a bug: a
spreadsheet's text has no numbered prose, no shape matches, and the map says so rather than
inventing a structure.

## 4. The machine is corpus-free; the shapes are a declared vocabulary

> **MEASURED AND LARGELY WITHDRAWN, 20 Aug 2026 — see `docs/measurements/N6-corpus-independence.md`.**
> This section argued corpus-independence from the design rather than from evidence. Measured
> across ELEVEN corpora the shipped recovery ranks the correct division axis first on **1 of 11**,
> because the six shapes below match almost nothing outside this Gazette. The *machine* below —
> the ascending chain, the stability rule, the integer scoring — survives the test and is reused
> unchanged in `N6`'s prototype. **The claim that the recovery as a whole is corpus-free does not.**
> The numbers in this section are correct for THIS instrument and were never evidence about any
> other.

The version this nearly shipped as had an `ORDINALS = {FIRST…TENTH}` map and a scan anchored at
unit starts, and it had already published *"no unit carries a THIRD SCHEDULE heading"* about a
heading sitting **mid-unit, 175 characters inside the second schedule**. Same defect shape as `F4`,
one level down: a pattern's blind spot published as a fact about the document.

What separates a top-level numbering from a subdivision's is that **the first ascends across the
whole region and the second restarts at every parent.** That is measurable, and it is measured:

| shape | candidates | ascending chain | purity | coverage | score |
|---|---:|---:|---:|---:|---:|
| `DECIMAL_TRAILING` | 147 | 144 | 0.98 | 0.83 | **0.809** |
| `DECIMAL_LEADING` | 3 | 3 | 1.00 | 0.37 | 0.365 |
| `ORDINAL_WORD` | 6 | 6 | 1.00 | 0.15 | 0.146 |
| `PAREN_LETTER` | 365 | 40 | 0.11 | 0.05 | 0.005 |
| `PAREN_DECIMAL` | 335 | 9 | 0.03 | 0.02 | 0.000 |

**Nothing declares that the margin number is the top level.** Over the schedule tail the same
criterion picks `ORDINAL_WORD` at **0.911** against `PAREN_ROMAN` at 0.030. Chain length alone gets
that one WRONG — the lettered lists inside the schedules score 19 against the six schedule headings'
6 — which is `NC-DIV01`.

Both ratios ship with both integers and the comparison is exact integer cross-multiplication:
`cdfc.canon` refuses a float outright, and caught this on the first write.

## 5. The holdout, and exactly what it does and does not establish

The Hindi half of the same Gazette — 142 pages, excluded from the unit set by `S1_EXCLUSION`, never
read while these shapes were written. **It is not a segmentation target and the re-pin does not
address it.** It was run to ask one question: is the machine tuned to the English typesetting?

    DECIMAL_TRAILING   cand  56  chain 50  score 0.745      <- wins, unchanged
    PAREN_ROMAN        cand  23  chain  5  score 0.091
    ORDINAL_WORD       cand   0  chain  0  score 0.000      <- no English ordinals; contributes nothing
    recovered: 48 divisions, ordinals 5..147

**ESTABLISHES: script independence.** Devanagari, zero code changes, the same shape wins, and the
one language-bound shape correctly scores zero instead of misfiring.

**DOES NOT ESTABLISH: convention independence.** Same Gazette, same typesetter, same margin column.
An instrument numbering its schedules `SCHEDULE 3`, or using a marker shape not among the six, is
untested — and **this repository holds exactly one prose instrument**, so it cannot be tested here
today. Recall on the Hindi arm is also low for a reason that is nothing to do with the divider: the
two PDF parties produce **413 DISPUTED units of 691** on Devanagari against 28 of 1,218 on the
English, so most anchors are unreadable. That is a corroboration failure in the corpus.

## 6. The controls, and the one that did not flip

Four negative controls, gates **128–131**, each reproducing a defect that was in this tree during
the session that wrote the module. Every one observed red; the positive control held under all four.

**`NC-DIV01` FAILED TO FLIP ON ITS FIRST RUN.** `LevelByChainLength` replaces the purity x coverage
comparison with raw chain length, and all five guards stayed GREEN — because the comparison was
written **twice**, once in `_better` and once as an inline sort key in `_select`, and the choice was
being made by the copy the injector did not touch.

A control that breaks a rule the system does not consult proves nothing, and it would have
registered LIVE on a guard that could never go red. `_select` now orders through `_better` and the
second copy is gone. **This is the twelfth time in this repository a check has been defeated by
something other than the thing it was checking.**

## 7. What this does NOT establish

* **No cross-reference is resolved by the map itself.** `div1_0008__sub_0001` says *"as specified in
  Second Schedule"* and `div2_0002` holds the table it points at; that both are now addressable is a
  precondition for resolving the reference, not the resolution.
* **Nothing bounds recall over marker shapes.** Six are declared. How many a wider corpus would need
  is unmeasured, and there is no second prose instrument here to measure it on.
* **Depth stops at 2.** Lettered and roman sub-lists are candidates and are not addressed;
  `DEFAULT_DEPTH` says so and running deeper was measured at 1,176 further divisions whose level
  selection is choosing between shapes on chains of length 1.
* **The `A4` blocker has not moved.** `g0_scope.py` still raises on any STATUTE obligation until 50
  labelled proviso spans exist. The re-pin was the prerequisite `N1` named; it is not the phase.
