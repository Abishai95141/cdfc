#!/usr/bin/env python
"""S1 — pin the IFSCA (Fund Management) Regulations, 2025 as the first `kind: STATUTE` instrument.

    make statute

Closes `docs/decisions/D-P7-01-no-statutory-instrument.md`, whose three requirements were: a
pinned PDF with its sha256 in the manifest and its terms in `docs/LICENCES.md`; **two independent
extractors, not one library in two modes**; and a `kind: STATUTE` row. All three are met here.

Writes `corpus/instruments/fm-regulations-2025.text.json`, refreshes `MANIFEST.json`, and publishes
`docs/measurements/S1-instrument-agreement.md`. Pure in its inputs: the same PDF and the same
library versions produce byte-identical output.

**pypdf is read and measured, and is not a party.** The argument is in `tools/pdf_arms.py` and its
numbers are in the measurement. Running it here rather than describing it keeps the exclusion
falsifiable by anyone who re-runs this script.
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from cdfc.qualify.instruments import (  # noqa: E402
    InstrumentRow,
    manifest_bytes,
    row_of,
    serialise,
)
from cdfc.qualify.textsource import Corroboration, build  # noqa: E402
from pdf_arms import (  # noqa: E402
    S1_EXCLUSION,
    classify_page,
    declare_asymmetry,
    extraction_of,
    is_devanagari,
    sha256_of,
    units_of,
)

SOURCE = REPO / "corpus/instruments/fm-regulations-2025.pdf"
OUT = REPO / "corpus/instruments"
DOC = REPO / "docs/measurements/S1-instrument-agreement.md"

INSTRUMENT_ID = "statute-fm-regulations-2025"

# THE SHIPPED PAIR. Two conditions, both stated before any agreement number was known:
#   (1) genuinely independent codebases -- `pdfminer.six` is pure Python; PDFium is Google's C++
#       engine, the one in Chrome. Not one library in two modes, which D-P7-01 rejected by name.
#   (2) a licence this repository's own denylist permits.
PARTIES = ("pdfplumber", "pypdfium2")

# MEASURED, NOT PARTIES, each for its own reason -- and both published.
#   `pymupdf`  -- AGPL-3.0, which `ci/licence-denylist.sh` DENIES. Excluded on LICENCE, not score,
#                 and it is the arm that scored best. Recording that is the point.
#   `pypdf`    -- BSD, permitted, but its width-heuristic word boundaries emit spurious intra-word
#                 spaces on this artifact's fonts, which carry no /ToUnicode map.
MEASURED_NOT_PARTY = ("pymupdf", "pypdf")

# The citation, verbatim from the artifact's own first page. It is data, not decoration: the
# watcher resolves amendments against it, and a report that quotes a clause quotes this beside it.
CITATION = (
    "The Gazette of India, EXTRAORDINARY, PART III--Section 4, No. 116, "
    "New Delhi, Thursday, February 13, 2025 / Magha 24, 1946; "
    "e-publication id CG-GJ-E-19022025-261146; "
    "F. No. IFSCA/2025/002, Gandhinagar, 10 February 2025"
)


def main() -> int:
    if not SOURCE.is_file():
        print(f"FAIL: {SOURCE.relative_to(REPO)} is absent. The instrument is not pinned.")
        return 1

    reads = {}
    for name in (*PARTIES, *MEASURED_NOT_PARTY):
        extraction, english, pages = extraction_of(name, SOURCE)
        reads[name] = (extraction, english, pages)
        print(f"  {name:11} {len(pages):3} pages, {len(english):3} English, "
              f"{len(extraction.units):5} units  (v{extraction.version})")

    # The English range is COMPUTED by each party and must agree, or the parties disagree about
    # what the instrument IS rather than about what it says -- a different and worse finding.
    ranges = {n: reads[n][1] for n in PARTIES}
    if len({r for r in ranges.values()}) != 1:
        print(f"FAIL: the parties disagree on the English page range: "
              f"{ {n: (r[0], r[-1]) for n, r in ranges.items()} }")
        return 1
    english = ranges[PARTIES[0]]

    parties = declare_asymmetry([reads[n][0] for n in PARTIES])
    it = build(INSTRUMENT_ID, parties)

    (OUT / f"{INSTRUMENT_ID}.text.json").write_bytes(
        serialise(it, kind="STATUTE", source_name=SOURCE.name, source_sha256=sha256_of(SOURCE))
    )

    rows: list[InstrumentRow] = []
    for blob in sorted(OUT.glob("*.text.json")):
        from cdfc.qualify.instruments import deserialise

        inst, kind, source_name, source_sha = deserialise(blob.read_bytes())
        rows.append(row_of(inst, kind=kind, source_name=source_name, source_sha256=source_sha))
    (OUT / "MANIFEST.json").write_bytes(manifest_bytes(rows))

    DOC.write_text(_render(it, reads, english), encoding="utf-8")
    c = it.counts()
    print(f"\n  {INSTRUMENT_ID}: {c['units_total']} units  "
          f"AGREED {c['AGREED']}  SINGLE_PARTY {c['SINGLE_PARTY']}  DISPUTED {c['DISPUTED']}")
    print(f"  wrote {DOC.relative_to(REPO)} and MANIFEST.json ({len(rows)} instruments)")
    return 0


def _pairwise(a_units, b_units) -> tuple[int, int]:
    ta = {u.key: u.text for u in a_units}
    tb = {u.key: u.text for u in b_units}
    keys = set(ta) | set(tb)
    return sum(1 for k in keys if ta.get(k) is not None and ta.get(k) == tb.get(k)), len(keys)


def _render(it, reads, english) -> str:
    c = it.counts()
    ag = it.agreement()
    addr_n, addr_d = it.addressable_fraction()
    pages = reads[PARTIES[0]][2]
    hindi = [i + 1 for i, t in enumerate(pages) if classify_page(t, i + 1) == "DEVANAGARI"]
    dev_chars = sum(sum(1 for ch in t if is_devanagari(ch)) for t in pages)

    pw = []
    names = (*PARTIES, *MEASURED_NOT_PARTY)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            k, n = _pairwise(reads[x][0].units, reads[y][0].units)
            pw.append((x, y, k, n))

    lines = [
        "# docs/measurements/S1-instrument-agreement.md — the first statutory instrument",
        "",
        "GENERATED by `tools/pin_statute.py`. Do not hand-edit.",
        "",
        f"**`{INSTRUMENT_ID}`** — the first `kind: STATUTE` instrument in this repository.",
        "`docs/decisions/D-P7-01-no-statutory-instrument.md` is closed by this build.",
        "",
        "## The artifact",
        "",
        "| field | value |",
        "|---|---|",
        f"| source | `{SOURCE.name}` |",
        f"| source sha256 | `{sha256_of(SOURCE)}` |",
        f"| citation | {CITATION} |",
        f"| pages | {len(pages)} |",
        f"| text sha256 | `{it.sha256}` |",
        "",
        "## The unit set",
        "",
        "| state | count |",
        "|---|---|",
        f"| AGREED | **{c['AGREED']}** |",
        f"| SINGLE_PARTY | {c['SINGLE_PARTY']} |",
        f"| DISPUTED | {c['DISPUTED']} |",
        f"| **units_total** | **{c['units_total']}** |",
        "",
        f"**Addressable: {addr_n} of {addr_d} units.** A DISPUTED unit is not addressable and "
        "`slice()` raises on any span touching one; `find_all` still returns disputed occurrences, "
        "so G0 can tell *the quote is nowhere* from *the quote is in a region we excluded*.",
        "",
        "### Agreement, as two vectors and never one",
        "",
        f"* `EXTERNAL`: **{ag['EXTERNAL'][0]} / {ag['EXTERNAL'][1]}**",
        f"* `SAME_AUTHOR`: {ag['SAME_AUTHOR'][0]} / {ag['SAME_AUTHOR'][1]}",
        "",
        "**Every unit is corroborated by two readers neither of which was written here.** For the "
        "nine TEMPLATE instruments one party was `openpyxl` and the other was ours; this is the "
        "one respect in which the statutory instrument rests on better evidence than the "
        "templates do.",
        "",
        "## The three arms, and why one of them is not a party",
        "",
        "| pair | units agreeing |",
        "|---|---|",
    ]
    for x, y, k, n in pw:
        both = x in PARTIES and y in PARTIES
        star = " **(shipped pair)**" if both else ""
        # The EMITTED line carries both integers; k and n are variables here, so the gate cannot
        # see digits on this SOURCE line. The rendered output is scanned by the same gate.
        row = f"| `{x}` vs `{y}`{star} | {k} / {n} = {k / n:.2%} |"  # rate-ok: k/n is emitted
        lines.append(row)
    lines += [
        "",
        "`pymupdf` and `pypdf` were read, measured, and **excluded as parties**, each for its "
        "own reason. `pymupdf` is `AGPL-3.0`, which this repository's own "
        "`ci/licence-denylist.sh` DENIES -- and it is the arm that scored best, which is exactly "
        "why the exclusion is recorded rather than quietly taken. That gate scopes to the RUNTIME "
        "set and would not have fired on a build-time tool: **a denylisted licence entering "
        "through a door the gate does not watch.** The gate is extended; the exception is not. "
        "For `pypdf` the ground is "
        "taken from the artifact, not from the score: the instrument's fonts carry **zero "
        "`/ToUnicode` CMaps**, so `pypdf`'s width-heuristic word-boundary reconstruction has no "
        "text-level check, and it emits spurious **intra-word** spaces that whitespace collapsing "
        "cannot repair. The corroborating evidence is the shape of the disagreement: `pdfplumber` "
        "and `pymupdf` share no code and agree with each other, while `pypdf` disagrees with "
        "*both*. Three independent readings of an ambiguous text scatter three ways; these went "
        "two against one.",
        "",
        "**A `>=2 of 3` majority rule was committed to in advance and then NOT used.** "
        "`textsource.build()` implements unanimity, and weakening *every competent party agrees* "
        "to *most agree* across the whole system — including nine TEMPLATE instruments whose "
        "numbers are already published — to rescue one instrument is the wrong trade. The "
        "majority figure is recorded here and shipped nowhere.",
        "",
        "## What is excluded, and counted",
        "",
        f"* **Hindi pages: {len(hindi)}** of {len(pages)} "
        f"(pages {hindi[0]}–{hindi[-1]} where contiguous), carrying {dev_chars:,} Devanagari "
        "characters across the whole document.",
        f"* **English pages: {len(english)}** — {english[0]}–{english[-1]}.",
        "",
        S1_EXCLUSION,
        "",
        "## What is NOT claimed",
        "",
        "The extraction harness is **proven on line-structured workbooks, not on prose** — "
        "`D-P7-01` said so and this build does not retire the caveat, it measures against it. A "
        "PDF's unit key is a sentence ordinal and sentence segmentation is its own source of "
        "disagreement; the segmenter here is "
        "`cdfc.experiment.enumerate_shall.sentences`, **imported rather than reimplemented**, so "
        "there is exactly one sentence rule in the system and a unit boundary cannot disagree "
        "with an obligation boundary.",
        "",
        "The instrument is the **base gazette notification of 19 February 2025**. Amendment "
        "notifications — `IFSCA/GN/2025/007` in force from 30 July 2025, and `IFSCA/GN/2026/006` "
        "— are **known and not pinned**. This instrument is therefore stale by two amendments on "
        "the day it lands, which is a fact about the corpus and is published rather than "
        "discovered later.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
