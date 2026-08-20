#!/usr/bin/env python
"""B3 measurement — is the DISPUTED count a reading, or an artifact of a threshold?

    python tools/pdf_align_sweep.py <in.pdf>

Two questions, because a published count answers neither on its own.

**1. Does the number move on a knife edge?** `ALIGN_FLOOR` is a parameter. A parameter that was
tuned until the number looked good is not a measurement, so the counts are reported across the
range and the reader can see the shape rather than trust the pick.

**2. What are the disputes ABOUT?** A dispute between two PDF readers is not one thing. Each
aligned-but-differing pair is classified by the *smallest* edit that would reconcile it, which
attributes the disagreement to a mechanism instead of leaving 115 as a number nobody has opened:

  * `punctuation_only`  — reconciled by folding typographic punctuation. This is **docling
    normalising**, not the parties disagreeing about the document. It stays DISPUTED because
    `textsource.REFUSED_TRANSFORMATIONS` names `unify_quotes` and folding it would disable the
    homoglyph gate — but it is attributed, not buried.
  * `spacing_only`      — reconciled by deleting all whitespace. Word boundaries reconstructed
    from glyph advance widths; `docs/measurements/S1-instrument-agreement.md` records the same
    mechanism costing `pypdf` its place as a party.
  * `content`           — neither. The parties read different text, which is a real dispute.
"""

from __future__ import annotations

import pathlib
import sys
import unicodedata

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

import pdf_ingest as PI  # noqa: E402
from cdfc.qualify.textsource import Corroboration, normalise  # noqa: E402


def _fold_punct(s: str) -> str:
    """Every Unicode PUNCTUATION character to a single sentinel. General, not a quote list.

    Enumerating the pairs a corpus happens to contain is the shallow proxy; `unicodedata.category`
    starting with `P` is the property itself, and it covers quotes, dashes, brackets and every
    typographic variant of them in one rule.
    """
    return "".join("\x00" if unicodedata.category(c).startswith("P") else c for c in s)


def classify(a: str, b: str) -> str:
    if _fold_punct(a) == _fold_punct(b):
        return "punctuation_only"
    if "".join(a.split()) == "".join(b.split()):
        return "spacing_only"
    return "content"


def main() -> int:
    pdf = pathlib.Path(sys.argv[1])
    reads = {n: PI.READERS[n](pdf) for n in PI.PARTIES}
    a_name, b_name = PI.PARTIES
    ap, bp = reads[a_name][0], reads[b_name][0]

    print(f"{pdf.name}  {a_name} {len(ap)} pages · {b_name} {len(bp)} pages\n")
    print(f"{'floor':>6}  {'AGREED':>7} {'SINGLE':>7} {'DISPUTED':>9} {'total':>7}")
    original = PI.ALIGN_FLOOR
    for floor in (0.40, 0.50, 0.60, 0.70, 0.80):
        PI.ALIGN_FLOOR = floor
        ua, ub, _ = PI._aligned_units(ap, bp, a_name, b_name)
        tables = {a_name: {u.key for u in ua}, b_name: {u.key for u in ub}}
        universe = tables[a_name] | tables[b_name]
        from cdfc.qualify.textsource import Extraction, build
        arms = [Extraction(extractor=n, version=reads[n][1], external=True, units=u,
                           blind_to={k: "unaligned" for k in sorted(universe - tables[n])})
                for n, u in ((a_name, ua), (b_name, ub))]
        c = build(f"sweep-{floor}", arms).counts()
        mark = "  <- shipped" if abs(floor - original) < 1e-9 else ""
        print(f"{floor:>6.2f}  {c['AGREED']:>7} {c['SINGLE_PARTY']:>7} {c['DISPUTED']:>9} "
              f"{c['units_total']:>7}{mark}")
    PI.ALIGN_FLOOR = original

    ua, ub, _ = PI._aligned_units(ap, bp, a_name, b_name)
    ta = {u.key: u.text for u in ua}
    tb = {u.key: u.text for u in ub}
    buckets: dict[str, list[tuple[str, str, str]]] = {}
    for k in sorted(set(ta) & set(tb)):
        # Compare on NORMALISED text, which is what `build` compares. Classifying the raw strings
        # would count differences the system's own normaliser already reconciles.
        na, nb = normalise(ta[k]), normalise(tb[k])
        if na != nb:
            buckets.setdefault(classify(na, nb), []).append((k, na, nb))
    total = sum(len(v) for v in buckets.values())
    print(f"\nDISPUTED at floor {original}: {total}, by the smallest edit that reconciles them")
    for name in ("punctuation_only", "spacing_only", "content"):
        v = buckets.get(name, [])
        print(f"  {name:18} {len(v):>4} of {total}")
        for k, x, y in v[:2]:
            print(f"      {k}  {a_name[:4]}: {x[:88]}")
            print(f"      {'':<{len(k)}}  {b_name[:4]}: {y[:88]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
