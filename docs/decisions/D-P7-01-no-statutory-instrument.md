# D-P7-01 — the statutory corpus is empty, and that is a published number

**Decided 13 Aug 2026, at P7-B0.**

## The finding

`plan/04-phases-qualification.md` E7.6 states as an ENTRY CRITERION:

> The regulation PDF and the 399-circular corpus are on disk and content-addressed, with the 10
> scanned images declared.

**Neither is on disk.** There is no `corpus/` directory in this repository before this build, no
PDF of any kind, and no instrument of `kind: STATUTE`. E7.7 then requires
`corpus/instruments/fm-regulations-2025.text.json` and names P7-B0 as the build that produces it —
but a dual-extraction harness cannot extract a document that is absent.

This was found by reading the entry criteria against the tree, which is the same way F35 found
that B0 sat five phases downstream of its only consumer.

## The decision

**Build the harness; do not build the document.** `corpus/instruments/MANIFEST.json` carries

```json
"statute_instruments": [],
"statute_absent_reason": "No statutory instrument is pinned in this repository. …"
```

and `obligations.load` refuses a row whose `instrument_id` is not in the store, so a
`source: STATUTE` obligation cannot enter the funnel by resolving against nothing.

## What it costs, stated as the number it changes

P7's obligation-coverage pair is unchanged in VALUE and changed in MEANING:

| Published number | Value | Reason |
|---|---|---|
| `predicates_with_a_STATUTE_obligation / N` | `0 / N` | **not** "no harvested predicate cites a statute yet" — *no statute is pinned in this repository at all* |
| `predicates_with_a_TEMPLATE_obligation / N` | `N / N` | every candidate traces to the regulator's own pinned blank |

The plan expected the first number to be `0` because the harvest cannot invent a citation. It is
`0` for a stricter reason, and the stricter reason is the one that ships: **P13's clause layer has
no input.**

## The alternative it beat

*Synthesise a plausible instrument text so the pipeline has something to point at.* Rejected
outright. Every G0 figure is `source_text.find(quote)` at a character span; against an invented
text, `quote_not_located` becomes a statement about our own fabrication and the attrition funnel's
first stage measures nothing. **A span into an invented instrument is not evidence, and it would
look exactly like progress.**

*Download one during the build.* Not this agent's call to make, and not a build step: a corpus
member has to be pinned, licence-checked and content-addressed before anything resolves against it.

## The drop-in point, so this stays cheap to close

`textsource.build(instrument_id, extractions)` takes `Extraction` objects and does not know what
produced them. Closing this needs exactly three things:

1. a pinned PDF under `corpus/instruments/`, with its sha256 in `MANIFEST.json` and its licence or
   reproduction terms recorded in `docs/LICENCES.md`;
2. **two independent extractors** — not one library in two modes. The template arm's external party
   is `openpyxl`; the statutory arm needs the same kind of independence, and a single extractor run
   twice is NC-Q50's mechanism with extra steps;
3. a `kind: STATUTE` row from `tools/build_instruments.py`.

Nothing in `g0_scope.py` changes: it already resolves each obligation against **its own**
`instrument_id`, and the template arm exercises that path on 1,729 units today.

## What is NOT claimed

That the harness is proven on prose. It is proven on a line-structured instrument where the unit
key is `(sheet, row, column, kind)`. A PDF's unit key is a sentence index, sentence segmentation is
its own source of disagreement, and **the first statutory instrument pinned here will need its
segmentation measured before its agreement rate means anything.** That is a real gap and it is not
softened: the harness is general, the *evidence* is over templates.

Related: `docs/measurements/P7-textsource.md` · `src/cdfc/qualify/instruments.py` ·
`docs/decisions/D-P7-02-three-corroboration-states.md`
