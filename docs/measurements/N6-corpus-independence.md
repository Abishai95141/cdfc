# N6 — is the division recovery corpus-independent? Measured on eleven corpora. **NO.**

*Run 20 Aug 2026. Harness, provenance and full results in `research/corpus-independence/`.
Re-acquire with `fetch.sh`; the corpora are public and are NOT vendored.*

---

## The claim under test, and the verdict

`N1b §4` said the division recovery in `src/cdfc/qualify/provisions.py` is corpus-free because its
machine — the ascending-chain filter — knows nothing about statutes, and only its six MARKER SHAPES
were fitted to one Gazette. **That claim was not supported by evidence and it is now measured.**

| | |
|---|---:|
| corpora | **11**, five jurisdictions, four document types, ten independently sourced |
| correct division axis ranked **first** | **3 of 11** |
| correct axis in the **top five** | **5 of 11** |
| correct axis **induced at all** | **9 of 11** |

**Three of eleven is not corpus independence, and the claim is withdrawn rather than qualified.**
What it does support is narrower and still worth having: the induction proposes the right axis
somewhere in its candidate set for **9 of 11**, which is a recall figure for a proposer — and this
architecture already knows what to do with a proposer.

## The corpora

Chosen to be structurally unlike each other, not merely numerous. Ground truth — what the top-level
division axis IS for each — was **authored by me from reading the documents**; it is a label, not a
tuning knob, and it is published in `final.py` so it can be disputed.

| corpus | source | kind | division axis | rank found |
|---|---|---|---|---:|
| `ifsca_gazette` | this repo's pinned instrument | Indian statute, PDF | regulations 1–148, margin-numbered | **1** |
| `gdpr` | EUR-Lex CELEX 32016R0679 | EU regulation, HTML | recitals (1)–(173), Articles 1–99 | **1** |
| `gutenberg_prideprejudice` | Project Gutenberg 1342 | Victorian novel, plain text | CHAPTER I–LXI | **1** |
| `rfc2616` | RFC Editor | IETF standard, plain text | sections 1–19 | 2 |
| `rbi_circular` | rbi.org.in | Indian circular, HTML | numbered paragraphs | 3 |
| `rfc8259` | RFC Editor | IETF standard, plain text | sections 1–15 | 36 |
| `ecfr_17_275` | eCFR API | US CFR part, XML | §§ 275.0-2 … | 248 |
| `rfc5321` | RFC Editor | IETF standard, plain text | sections 1–8 | 276 |
| `w3c_html52` | W3C REC | web standard, HTML | sections 1–14 | 321 |
| `us_bill_hr3684` | GovInfo | US bill, HTML | SEC. n | **not found** |
| `india_const` | Constitute Project | constitution, PDF | Articles / Parts | **not found** |

## What the architecture became, and it IS better

The version measured here replaced the six enumerated regexes with a three-layer decomposition. It
is in `research/corpus-independence/induct.py`, and it is **not** in `src/` — see §5.

    LAYER 1  NUMERAL SYSTEMS      DECLARED and universal: arabic, dotted multi-index, roman,
                                  alphabetic (BOTH continuation conventions), English ordinal
                                  words. Properties of notation, not of any document.
    LAYER 2  TEMPLATE INDUCTION   OBSERVED: the punctuation touching a numeral, the word before,
                                  the word after, line start, line end. Five candidate groupings
                                  are generated per occurrence and the machine picks.
    LAYER 3  THE CHAIN MACHINE    Corpus-free. Longest stable ascending chain, scored on four
                                  measured properties: chain, purity, coverage, density.

The gain is real and is visible in the table: **`CHAPTER I–LXI` in a Victorian novel is recovered
at rank 1 by the same code that recovers a Gazette's margin numbers**, and the word `chapter` is
nowhere in it — the template was induced. The enumerated version scores that corpus, and eight
others, at zero.

### Four defects the multi-corpus run exposed, each fixed at its layer

1. **Dotted outline numbering was not a numeral system.** `1.1`, `2.10.3`, `275.206` tokenised as
   two separate numerals, so the section structure of every RFC, the CFR and the W3C spec was
   invisible. Added as `MULTI_INDEX` — a notation, not a convention.
2. **The chain machine was O(n²).** Affordable on 150 candidates, impossible on the 250,000 a
   2.7-million-character bill produces. **The algorithm that could only run on the small corpus was
   itself a way of only ever seeing the small corpus.** Now O(n log n) via Fenwick trees over
   coordinate-compressed ordinals.
3. **`purity × coverage` rewarded three-element chains.** A 3-chain spanning a document scored 0.91
   and beat a 176-chain. Two properties were missing and both are properties of what a division
   numbering IS: **chain** (how much structure it explains) and **density** (a numbering runs
   1..N; noise skips).
4. **The alphabetic continuation convention was hand-picked.** `(aa)` was decoded as 27 by fiat.
   Both conventions are now separate numeral systems and the chain machine sees which one forms a
   sequence in the document at hand.

## THE FAILURE MODE THAT DOES NOT HAVE A CORPUS-FREE FIX

**Page numbers are a perfect division numbering.** In `rfc2616` the footer sequence scores chain
176 of 176, purity 1.00, coverage 1.00, density 1.00 — better on every intrinsic property than the
section structure it beats. It is not noise. It is a real, dense, ascending numbering that really
does partition the document, into pages.

Three discriminators were tried:

* **Nesting** — does the candidate have children that restart per block? Measured, and it **fails**:
  physical pages genuinely contain sections, so the page sequence scores 0.74 on it.
* **Position** — require a line start? The IFSCA margin number is at a line END, so this would
  destroy the one corpus that already worked.
* **Boilerplate variety** — mask the numeral and ask how varied the remainder is. **This one works**,
  and it took three corrections to make it mean what it says:
  - mask the TOKEN, not `str(ordinal)`, or `CHAPTER II` is mis-measured and every non-arabic system
    with it;
  - extend to the next line when the marker sits alone on its own, or GDPR's 173 recitals — the
    correct answer — are condemned as boilerplate by the filter built to protect them;
  - **subtract the template's own words first**, or `CHAPTER #.` reads as identical across all 61
    chapters and the correct answer is destroyed a second time, in the other direction.

  With all three, RFC page footers drop from 175.31 to 1.00 and the novel's chapters stay at 38.42.

**But it is not enough.** After demoting the footers the RFC section structure still does not rise
to the top, because the sections were never induced as a strong candidate in the first place — a
separate failure, in Layer 2.

**The honest conclusion is that "which numbering is the LOGICAL structure" is not answerable from
numbering properties alone.** Page numbers and section numbers are both real divisions; separating
them needs layout or typography, which a text-only pipeline has already discarded. This is what
Docling's `ListItem.marker` has and our extraction does not, and it is why the spike found docling
useful — a fact that survives even though `F4`'s reason for it was wrong.

## What the architecture should therefore be

**Induce and RANK; do not choose.** The recovery emits every candidate axis with its measured
evidence — chain, purity, coverage, density, variety, worked examples — and the axis is a
**DECLARED** property of the pinned instrument, recorded as data.

That is this repository's own propose/decide split applied one layer down, and it has the property
the current code does not: **the corpus knowledge becomes one auditable declaration per instrument
instead of six regexes nobody can see the fit of.** It also makes the claim measurable in the form
it is actually true — *the correct axis is among the induced candidates for 9 of 11 corpora* — a
recall figure for a proposer, which is a claim this project already knows how to carry.

## What this does NOT establish, and what was NOT done

* **It is not in `src/`.** The prototype scores rank-1 on 3 of 11 and the shipped enumerated version
  scores rank-1 on 1 of 11 — but the shipped one is measured, gated by four negative controls, and
  inside a digest. Replacing a measured component with a better-scoring unmeasured one is the trade
  this repository exists to refuse. `A4` is where the replacement belongs, with its own controls.
* **The two `not found` corpora are not diagnosed.** `us_bill_hr3684` and `india_const` induce no
  candidate matching their true axis at any rank, and why is unmeasured.
* **Ground truth is single-author.** I wrote the labels. Cohen's κ has no mechanical substitute here
  either, and this is a fourth place it is missing.
* **Text extraction is uniform and dumb by design** — strip markup, split lines, drop empties. A
  better per-corpus extractor would change these numbers and would be the corpus-specific tuning
  the whole exercise exists to avoid.
