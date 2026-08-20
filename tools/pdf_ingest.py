#!/usr/bin/env python
"""B3 — a PDF becomes an ADDRESSABLE TEXT. **Build-time only, and that is architectural.**

    python tools/pdf_ingest.py <in.pdf> <out.text.json> [--id NAME]

## Why this is in `tools/` and not in `src/`

`cdfc.fill` is in `VERDICT_ROOTS` and imports `cdfc.ingest.tabular` and `cdfc.ingest.xmlsafe`, so
**`cdfc.ingest` is inside the verdict closure**. A PDF reader placed there would pull docling —
and torch, and a model zoo — into the closure of code that answers a coverage question, which is
exactly what `tests/negative/importgraph.py` exists to prevent.

So the split is the one `tools/pdf_arms.py` already uses for the statute: **the PDF is read at
BUILD time into a pinned `InstrumentText`, and the runtime reads the text.** The registry stores
that text as an artefact like any other, `cdfc.model.extract` runs over it unchanged because it
takes an `InstrumentText`, and nothing on the verdict path has ever seen a PDF.

That is not a workaround. A span into a PDF is a span into *somebody's rendering* of a PDF; pinning
the text is what makes the span re-derivable at all.

## Two parties, because one reading is that reading's opinion

`textsource.build` refuses a single extraction, and the rule is not weaker here than for the
Gazette. Two independent readers:

  * **docling** — layout-aware, and the one that recovers list markers `pdfplumber` drops
    (`docs/spike/README.md`: 294 regulation-number markers where a flat extraction found 3).
  * **pdfplumber** — `pdfminer.six`, pure Python, a different content model entirely.

A page they agree on is `AGREED`. One they disagree on is `DISPUTED`, excluded from the addressable
text, and published with its location — which is the correct outcome for a page whose reading
depends on which library you believed.

**Both are EXTERNAL** (neither written here), so `agreement()` reports this under `EXTERNAL`, which
is stronger evidence than the `SAME_AUTHOR` pair a CSV gets.

## What this does NOT do

It does not OCR. A scanned page with no text layer yields no units from either party and is
reported as such rather than silently contributing nothing — `absent != empty`.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from collections.abc import Sequence
from difflib import SequenceMatcher
from typing import Final

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.enumerate_shall import sentences  # noqa: E402
from cdfc.qualify.instruments import serialise  # noqa: E402
from cdfc.qualify.textsource import Extraction, Unit, build  # noqa: E402


ALIGN_FLOOR: Final[float] = 0.60
"""Ratcliff-Obershelp ratio below which two sentences are NOT the same sentence.

**A threshold is a parameter, so it is published rather than tuned.** `tools/pdf_align_sweep.py`
reports the corroboration counts at 0.40 / 0.50 / 0.60 / 0.70 / 0.80 so a reader can see whether
the number moves on a knife edge. It does not: see `docs/measurements/B3-pdf-ingress.md`.
"""

ALIGN_MARGIN: Final[float] = 0.05
"""A candidate must beat the runner-up by this much. A TIE IS REFUSED, not broken.

The same rule `cdfc.correspond.link` applies to record pairs, for the same reason: two candidates
of comparable weight is not a match with a tiebreak, it is an absence of evidence about which. An
alignment that guesses puts one sentence's dispute on another sentence's span.
"""


def _page_sentences(pages: Sequence[str]) -> list[list[str]]:
    """Per page, the sentence units. The segmenter is IMPORTED, so a unit boundary cannot disagree
    with an obligation boundary — there is one sentence rule in this system."""
    out: list[list[str]] = []
    for text in pages:
        body = " ".join((text or "").split())
        out.append([body[lo:hi].strip() for lo, hi in sentences(body) if body[lo:hi].strip()]
                   if body else [])
    return out


def _pair_page(a: Sequence[str], b: Sequence[str]) -> tuple[list[tuple[int, int]], list[int],
                                                            list[int]]:
    """Align two readings of ONE page BY CONTENT. Returns (pairs, a_only, b_only).

    ## Why this is not keyed by ordinal, which is what it did first

    The first version keyed a unit `p{page}.s{ordinal}` in each party independently and let
    `textsource.build` align on that key. On the FinCEN instructions that reported **129 of 375
    disputed** — and 21 of those were the two parties' sentence *number three* on a page, which
    were not the same sentence at all. docling leads page 2 with the disclaimer and pdfplumber
    leads it with the contents list; every ordinal after the first divergence faced an unrelated
    sentence.

    **That is not a disagreement, it is a misalignment, and reporting it as DISPUTED overstates
    the disagreement and understates the addressable text.** A count is not a reading.

    So alignment is order-preserving and content-based, which is what a diff is:

      1. **Anchor on exact matches.** `SequenceMatcher.get_matching_blocks` over the sentence
         lists; equal runs are certain and cost nothing to establish.
      2. **Inside each gap between anchors, pair by similarity** — Ratcliff-Obershelp, the ratio
         `difflib` already computes — subject to `ALIGN_FLOOR` and `ALIGN_MARGIN`.
      3. **Anything unpaired is one party's alone**, which is `SINGLE_PARTY`: *exactly one
         competent party produced it*. That is the honest label and it is already in the
         vocabulary.

    Pairing is deliberately similarity-based rather than exact: aligning only identical sentences
    would send every GENUINE disagreement to `SINGLE_PARTY`, which would hide the disputes this
    module exists to surface. The floor separates *the same sentence, read differently* from
    *a sentence only one party saw*.
    """
    pairs: list[tuple[int, int]] = []
    ai, bi = 0, 0
    for blk in SequenceMatcher(a=list(a), b=list(b), autojunk=False).get_matching_blocks():
        # The gap BEFORE this anchor: a[ai:blk.a] against b[bi:blk.b].
        pairs.extend(_pair_gap(a, b, ai, blk.a, bi, blk.b))
        pairs.extend((blk.a + k, blk.b + k) for k in range(blk.size))
        ai, bi = blk.a + blk.size, blk.b + blk.size
    used_a = {i for i, _ in pairs}
    used_b = {j for _, j in pairs}
    return (sorted(pairs),
            [i for i in range(len(a)) if i not in used_a],
            [j for j in range(len(b)) if j not in used_b])


def _pair_gap(a: Sequence[str], b: Sequence[str], a0: int, a1: int, b0: int, b1: int,
              ) -> list[tuple[int, int]]:
    """Similarity pairs inside one gap, ORDER-PRESERVING and tie-refusing."""
    out: list[tuple[int, int]] = []
    taken: set[int] = set()
    for i in range(a0, a1):
        scored = sorted(
            ((SequenceMatcher(a=a[i], b=b[j], autojunk=False).ratio(), j)
             for j in range(b0, b1) if j not in taken),
            reverse=True,
        )
        if not scored or scored[0][0] < ALIGN_FLOOR:
            continue
        if len(scored) > 1 and scored[0][0] - scored[1][0] < ALIGN_MARGIN:
            continue      # a tie is refused; both sentences stay one party's own
        best_j = scored[0][1]
        if out and best_j <= out[-1][1]:
            continue      # order-preserving: an alignment may not cross itself
        out.append((i, best_j))
        taken.add(best_j)
    return out


def _aligned_units(a_pages: Sequence[str], b_pages: Sequence[str], a_name: str, b_name: str,
                   ) -> tuple[tuple[Unit, ...], tuple[Unit, ...], dict[str, int]]:
    """Both parties' units, keyed so that ALIGNED sentences share a key and unaligned ones do not.

    The key is the alignment's identity, not a position: `p0007.a0003` is *the fourth thing the two
    parties agreed was the same sentence on page 7*, and `p0007.docling0012` is one docling saw
    alone. `textsource.build` then does what it always does — same key, compare; one party, label
    `SINGLE_PARTY` — and it needs no knowledge that a PDF was involved.
    """
    sa, sb = _page_sentences(a_pages), _page_sentences(b_pages)
    ua: list[Unit] = []
    ub: list[Unit] = []
    tally = {"aligned": 0, f"{a_name}_only": 0, f"{b_name}_only": 0}
    for page in range(1, max(len(sa), len(sb)) + 1):
        a = sa[page - 1] if page <= len(sa) else []
        b = sb[page - 1] if page <= len(sb) else []
        pairs, a_only, b_only = _pair_page(a, b)
        for n, (i, j) in enumerate(pairs):
            key = f"p{page:04d}.a{n:04d}"
            ua.append(Unit(key=key, text=a[i], page=page))
            ub.append(Unit(key=key, text=b[j], page=page))
        for i in a_only:
            ua.append(Unit(key=f"p{page:04d}.{a_name}{i:04d}", text=a[i], page=page))
        for j in b_only:
            ub.append(Unit(key=f"p{page:04d}.{b_name}{j:04d}", text=b[j], page=page))
        tally["aligned"] += len(pairs)
        tally[f"{a_name}_only"] += len(a_only)
        tally[f"{b_name}_only"] += len(b_only)
    return tuple(ua), tuple(ub), tally


def read_docling(path: pathlib.Path) -> tuple[list[str], str]:
    """Layout-aware. Its `ListItem.marker` is what recovers numbering a flat read drops."""
    from docling.document_converter import DocumentConverter  # build-time only
    from importlib.metadata import version

    doc = DocumentConverter().convert(str(path)).document
    pages: dict[int, list[str]] = {}
    for item, _level in doc.iterate_items():
        prov = getattr(item, "prov", None) or []
        page = prov[0].page_no if prov else None
        text = (getattr(item, "text", "") or "").strip()
        if page is None or not text:
            continue
        marker = (getattr(item, "marker", "") or "").strip()
        pages.setdefault(page, []).append(f"{marker} {text}".strip() if marker else text)
    n = max(pages) if pages else 0
    return [" ".join(pages.get(i, [])) for i in range(1, n + 1)], version("docling")


def read_pdfplumber(path: pathlib.Path) -> tuple[list[str], str]:
    """`pdfminer.six`, pure Python. A different content model from docling's, not a second mode."""
    from importlib.metadata import version

    import pdfplumber

    with pdfplumber.open(path) as doc:
        return [p.extract_text() or "" for p in doc.pages], version("pdfplumber")


PARTIES: Final[tuple[str, ...]] = ("docling", "pdfplumber")
"""The declared extraction parties. `ci/no-denied-build-tool.sh` reads this tuple.

Adding an arm means adding a row to that gate's licence table. The gate was written because a
denylisted licence entered through a door the runtime gate does not watch; a SECOND tool declaring
parties in a second file is that same door one level up, so the gate now scans every file under
`tools/` that declares a `PARTIES` tuple rather than one file by name.
"""

READERS = {"docling": None, "pdfplumber": None}      # bound below; keeps PARTIES the single list


def ingest(path: pathlib.Path, instrument_id: str):
    """`(InstrumentText, tally)`. Raises if either party reads nothing.

    ## The two parties are NOT peers, and that is declared rather than averaged

    `pdfplumber` reports what the content stream says. `docling` runs a document-understanding
    pipeline and returns a *normalised* document — measured here, it folds `U+2019` to `U+0027` and,
    on this instrument, `“…”` to `'…'`. So on a punctuation axis docling is a reading PLUS an
    undeclared transformation, and `docs/measurements/B3-pdf-ingress.md` publishes how many units
    that accounts for.

    **It is not folded away.** `textsource.REFUSED_TRANSFORMATIONS` already names `unify_quotes`
    and gives the reason: folding quote characters would make a homoglyph substitution unlocatable
    by the gate that exists to catch it. Rescuing a dispute count by disabling a gate is the trade
    this repository refused for dashes, and it is refused again here. The units stay DISPUTED, the
    cause is attributed, and the reader can see which is which.
    """
    reads = {}
    for name in PARTIES:
        pages, ver = READERS[name](path)
        reads[name] = (pages, ver)

    a_name, b_name = PARTIES
    ua, ub, tally = _aligned_units(reads[a_name][0], reads[b_name][0], a_name, b_name)
    for name, units in ((a_name, ua), (b_name, ub)):
        if not units:
            raise RuntimeError(
                f"{name} read {len(reads[name][0])} page(s) and produced NO units from "
                f"{path.name}. A scanned page with no text layer is not an empty document; this "
                "refuses rather than contributing nothing silently. OCR is out of scope."
            )

    # Declare each party's absences against the union, exactly as `pin_statute` does: an
    # unexplained absence is a MISS and `build` refuses it, because a reader that silently dropped
    # a construct must not look merely uncorroborated.
    tables = {a_name: {u.key for u in ua}, b_name: {u.key for u in ub}}
    universe = tables[a_name] | tables[b_name]
    arms = [
        Extraction(
            extractor=name, version=reads[name][1], external=True, units=units,
            blind_to={
                k: (f"{name} produced no sentence that aligned with this one at or above "
                    f"ratio {ALIGN_FLOOR} on page {int(k[1:5])}; the other party read it alone")
                for k in sorted(universe - tables[name])
            },
        )
        for name, units in ((a_name, ua), (b_name, ub))
    ]
    return build(instrument_id, arms), tally


READERS["docling"] = read_docling
READERS["pdfplumber"] = read_pdfplumber


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=pathlib.Path)
    ap.add_argument("out", type=pathlib.Path)
    ap.add_argument("--id", default="")
    ap.add_argument("--kind", default="SOURCE")
    ap.add_argument("--pin", action="store_true",
                    help="also rebuild corpus/instruments/MANIFEST.json from every pinned text")
    a = ap.parse_args()
    if not a.pdf.is_file():
        print(f"FAIL: {a.pdf} is absent.")
        return 1
    import hashlib

    it, tally = ingest(a.pdf, a.id or a.pdf.stem)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(serialise(it, kind=a.kind, source_name=a.pdf.name,
                                source_sha256=hashlib.sha256(a.pdf.read_bytes()).hexdigest()))
    c = it.counts()
    ag = it.agreement()
    print(f"  {it.instrument_id}")
    for name, n in sorted(tally.items()):
        print(f"    {name:18} {n}")
    print(f"    AGREED {c['AGREED']} · SINGLE_PARTY {c['SINGLE_PARTY']} · DISPUTED {c['DISPUTED']}"
          f" · total {c['units_total']}")
    print(f"    agreement EXTERNAL {ag['EXTERNAL'][0]}/{ag['EXTERNAL'][1]}"
          f" · SAME_AUTHOR {ag['SAME_AUTHOR'][0]}/{ag['SAME_AUTHOR'][1]}")
    print(f"    wrote {a.out}  ({a.out.stat().st_size:,} bytes)")

    if a.pin:
        # Rebuild from EVERY pinned text, not by appending a row. A manifest assembled by appending
        # records what the last run believed; one assembled by reading records what is on disk.
        from cdfc.qualify.instruments import InstrumentRow, deserialise, manifest_bytes, row_of
        out = REPO / "corpus/instruments"
        rows: list[InstrumentRow] = []
        for blob in sorted(out.glob("*.text.json")):
            inst, kind, name, sha = deserialise(blob.read_bytes())
            rows.append(row_of(inst, kind=kind, source_name=name, source_sha256=sha))
        (out / "MANIFEST.json").write_bytes(manifest_bytes(rows))
        print(f"    MANIFEST.json rebuilt from {len(rows)} pinned instrument(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
