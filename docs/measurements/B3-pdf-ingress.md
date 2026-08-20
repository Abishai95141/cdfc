# B3 — a PDF becomes an addressable text

**Dated 20 Aug 2026.** Reproduce with `make pin-pdf` (build-time venv) then `make demo-pdf`.

| | |
|---|---|
| instrument | `source-fincen-boir-instructions`, kind `SOURCE` |
| source | `corpus/regulators/fincen_boir_instructions.pdf`, 457,622 bytes, 21 pages |
| source sha256 | `006027a3a00038ad979c4ed89f6224a7…` |
| parties | **docling 2.120.3** and **pdfplumber 0.11.10** — both EXTERNAL, neither written here |
| segmenter | `cdfc.experiment.enumerate_shall.sentences`, imported, not reimplemented |

## What was produced

| | count |
|---|---|
| units | **401** |
| AGREED | **257** |
| SINGLE_PARTY | **29** |
| DISPUTED | **115** — not addressable, and counted |
| **addressable** | **286 / 401** |
| agreement, EXTERNAL | 257 / 372 |
| agreement, SAME_AUTHOR | 0 / 0 |

Both parties are external, so every corroborated unit rests on two readings neither of which this
repository wrote. That is stronger evidence than the nine TEMPLATE instruments have, where one
party is `openpyxl` and the other is ours.

## The first number was 129, and it was wrong

The first implementation keyed each party's units `p{page}.s{ordinal}` independently and let
`textsource.build` align on that key. It reported **129 of 375 disputed**.

Opening the bucket: **21 of those were not the same sentence.** docling leads page 2 with the
disclaimer; pdfplumber leads it with the contents list. Once the readings diverge, every ordinal
after the divergence faces an unrelated sentence, and the comparison measures **alignment, not
agreement**.

Alignment is now order-preserving and content-based — anchor on exact matches with
`difflib.SequenceMatcher`, pair the gaps by Ratcliff-Obershelp ratio subject to a floor and a
tie-refusing margin, and anything unpaired is `SINGLE_PARTY`, which is the honest label.

| | ordinal keying | content alignment |
|---|---|---|
| AGREED | 246 | **257** |
| SINGLE_PARTY | 23 | **29** |
| DISPUTED | 129 | **115** |

Pairing is deliberately *similarity*-based rather than exact. Aligning only identical sentences
would send every genuine disagreement to `SINGLE_PARTY` and hide the disputes this module exists
to surface.

## The threshold is a parameter, so here is its shape

`ALIGN_FLOOR` is 0.60. `python tools/pdf_align_sweep.py <pdf>`:

| floor | AGREED | SINGLE_PARTY | DISPUTED | total |
|---|---|---|---|---|
| 0.40 | 257 | 29 | 115 | 401 |
| 0.50 | 257 | 29 | 115 | 401 |
| **0.60** | **257** | **29** | **115** | **401** |
| 0.70 | 257 | 31 | 114 | 402 |
| 0.80 | 257 | 33 | 113 | 403 |

**Flat.** Doubling the floor moves DISPUTED by two. The number is not a knife edge and was not
tuned to look good.

## What the 115 disputes are ABOUT

A count is not a reading. Each aligned-but-differing pair is classified by the *smallest* edit
that would reconcile it, after the system's own `normalise` has run:

| cause | count |
|---|---|
| `punctuation_only` | **102 of 115** |
| `spacing_only` | 5 of 115 |
| `content` | 8 of 115 |

**So 8 of 401 units are a genuine disagreement about what the document says.**

`punctuation_only` is **docling normalising, not the parties disagreeing**. docling emits
`FinCEN's` where the content stream carries `FinCEN’s` (U+2019), and on this instrument it also
renders `“reporting company”` as `'reporting company'` — a curly *double* quote arriving as a
straight *single* one. On a punctuation axis docling is a reading **plus an undeclared
transformation**, and it is therefore not a peer of pdfplumber there.

`spacing_only` is word-boundary reconstruction from glyph advance widths — `http s:` against
`https :`. It is the same mechanism `docs/measurements/S1-instrument-agreement.md` records costing
`pypdf` its place as a party, appearing here at 5 units rather than ~1,060.

### They stay DISPUTED, and that is a deliberate refusal

Folding typographic punctuation would move the addressable fraction from **286/401 to roughly
388/401**. It is not done. `cdfc.qualify.textsource.REFUSED_TRANSFORMATIONS` names `unify_quotes`
and gives the reason: folding quote characters makes a homoglyph substitution unlocatable **by the
gate that exists to catch it**. Buying 102 units of coverage by disabling
`test_g0__verbatim_quote_required` is the trade this repository refused for dashes at P7, and
refuses again here.

**The open architectural question this raises** is recorded in `docs/OPEN-ITEMS.md`: the right
answer is probably a *declared transformation* on `Extraction`, dual to the existing `blind_to` —
a party stating what it normalises, so a difference attributable to a declared transform is not
counted as a disagreement about the document. That changes `textsource.build`, which the pinned
statute and nine template instruments depend on, so it is an architecture decision and not a B3
edit.

## The four checks

`make demo-pdf`, run in the **runtime venv, which has no PDF library installed**:

1. **addressable, with the dispute published** — 401 units, 115 disputed, counted, both parties EXTERNAL.
2. **byte-exact re-verification** — 25 values drawn from AGREED units, each located from scratch
   by `find_all`, each re-read at the computed span by `Observation.reverify`. 25 of 25 byte-exact.
3. **no PDF library on the verdict path** — 753 modules across 10 verdict roots; undeclared
   third-party **0**, denylisted **0**, PDF libraries **0**. The demo runs in a venv where docling
   is not installed, so this is demonstrated rather than asserted.
4. **disputed regions refuse** — `slice()` raised `DisputedRegionError` on **115 of 115**, each
   naming the intersecting region; **0** disputed spans leaked into an addressable span.

## What this does NOT establish

* **This is a regulator INSTRUCTIONS pdf, not a valuation pack.** It is a real PDF with a real
  text layer and it exercises the ingress honestly, but the pitch sentence says *"PDF valuation
  packs"*, and no valuation pack has been measured. The mechanism is corpus-independent by
  construction; the *claim* about valuation packs is not yet supported by a measurement.
* **No OCR.** A scanned page with no text layer yields no units and the ingest raises rather than
  contributing nothing silently. `absent != empty`.
* **No fill was run from this PDF.** B3 delivers the addressable text and its refusals. Binding a
  PDF-derived source through `cdfc.fill.pipeline` needs the pipeline to accept a pre-built
  `InstrumentText` instead of delimited bytes, which is B4.
* **Two parties, not three.** `textsource.build` implements unanimity and B3 did not weaken it.
