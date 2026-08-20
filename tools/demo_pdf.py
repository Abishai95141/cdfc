#!/usr/bin/env python
"""B3 — a PDF is ingested, addressed, and its unreadable regions REFUSE. Four checks.

    make demo-pdf

**This script runs in the runtime venv, which has no docling and no pdfplumber, and that is
check 3 demonstrated rather than asserted.** The PDF was read at build time by
`tools/pdf_ingest.py`; what ships is the pinned `InstrumentText`, and every span below is computed
against those pinned bytes. If a PDF library were anywhere on the verdict path this file could not
import.

  1  the pinned text is addressable, with two-party corroboration and a PUBLISHED disputed count
  2  a value re-verifies BYTE-EXACT at a span this system computed
  3  no verdict-path module imports a PDF library — checked over the real import graph
  4  a value inside a DISPUTED region is REFUSED, with a reason from the closed vocabulary
"""

from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evidence.observe import Observation  # noqa: E402
from cdfc.qualify.instruments import deserialise  # noqa: E402
from cdfc.qualify.textsource import Corroboration  # noqa: E402

PINNED = REPO / "corpus/instruments/source-fincen-boir-instructions.text.json"
PDF_LIBS = ("docling", "pdfplumber", "pypdfium2", "pypdf", "fitz", "pymupdf")


def check1(it) -> bool:
    c = it.counts()
    addressable, total = it.addressable_fraction()
    ag = it.agreement()
    print("  1  ADDRESSABLE, WITH THE DISPUTE PUBLISHED")
    print(f"       units          {c['units_total']}")
    print(f"       AGREED         {c['AGREED']}")
    print(f"       SINGLE_PARTY   {c['SINGLE_PARTY']}")
    print(f"       DISPUTED       {c['DISPUTED']}   (NOT addressable, and counted)")
    print(f"       addressable    {addressable}/{total}")
    print(f"       agreement      EXTERNAL {ag['EXTERNAL'][0]}/{ag['EXTERNAL'][1]}"
          f" · SAME_AUTHOR {ag['SAME_AUTHOR'][0]}/{ag['SAME_AUTHOR'][1]}")
    ok = c["units_total"] > 0 and c["DISPUTED"] > 0 and ag["EXTERNAL"][1] > 0
    print(f"       both parties EXTERNAL, neither written here: {ag['SAME_AUTHOR'][1] == 0}")
    return ok


def check2(it) -> bool:
    """A value re-verifies byte-exact at a span WE computed. The span is the point."""
    print("\n  2  A VALUE RE-VERIFIES BYTE-EXACT AT A COMPUTED SPAN")
    agreed = [u for u in it.units if u.corroboration is Corroboration.AGREED]
    picked = 0
    for unit in agreed:
        body = it.slice(unit.span)
        # Take a real multi-word phrase out of an AGREED unit and go find it again from scratch.
        words = body.split()
        if len(words) < 6:
            continue
        value = " ".join(words[2:6])
        spans = [s for s in it.find_all(value) if not it.is_disputed(s)]
        if not spans:
            continue
        span = spans[0]
        obs = Observation(value=value, document=it.instrument_id, span=span,
                          page=(it.unit_at(span).page if it.unit_at(span) else None),
                          context=it.text[max(0, span[0] - 30):span[1] + 30])
        if not obs.reverify(it):
            print(f"       FAIL re-verify at {span}")
            return False
        assert it.text[span[0]:span[1]] == value
        if picked == 0:
            print(f"       value    {value!r}")
            print(f"       span     {span}   page {obs.page}")
            print(f"       re-read  {it.text[span[0]:span[1]]!r}")
            print(f"       byte-exact: True")
        picked += 1
        if picked >= 25:
            break
    print(f"       {picked} value(s) drawn from AGREED units, all re-verified byte-exact")
    return picked >= 25


def check3() -> bool:
    """No verdict-path module imports a PDF library. Over the REAL import graph, not a grep.

    The check is the POSITIVE one: the verdict closure's third-party imports must be a subset of
    the declared runtime set. A denylist would only refuse the PDF libraries somebody remembered
    to name; this refuses everything nobody declared, which is the only form that survives the
    next library.
    """
    print("\n  3  NO PDF LIBRARY ON THE VERDICT PATH")
    sys.path.insert(0, str(REPO / "tests"))
    from negative.importgraph import (  # noqa: E402
        RUNTIME_THIRD_PARTY, VERDICT_ROOTS, banned_in, import_closure, third_party_in,
    )
    closure: set[str] = set()
    for root in VERDICT_ROOTS:
        closure |= set(import_closure(root, src=REPO / "src"))
    frozen = frozenset(closure)
    offenders = third_party_in(frozen)
    banned = banned_in(frozen)
    pdf_in_closure = sorted({m.split(".")[0] for m in closure} & set(PDF_LIBS))
    print(f"       verdict roots       {len(VERDICT_ROOTS)}")
    print(f"       modules in closure  {len(closure)}")
    print(f"       allowed third-party {sorted(RUNTIME_THIRD_PARTY)}")
    print(f"       UNDECLARED          {list(offenders) or 'none'}")
    print(f"       banned (denylist)   {list(banned) or 'none'}")
    print(f"       PDF libraries       {pdf_in_closure or 'none'}")
    print(f"       installed HERE      "
          f"{[m for m in PDF_LIBS if _importable(m)] or 'none'}  <- and the demo ran anyway")
    return not offenders and not banned and not pdf_in_closure


def _importable(name: str) -> bool:
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def check4(it) -> bool:
    """A value inside a disputed region is REFUSED, with a reason, and counted."""
    print("\n  4  A VALUE IN A DISPUTED REGION IS REFUSED")
    from cdfc.qualify.textsource import DisputedRegionError
    disputed = [u for u in it.units if u.corroboration is Corroboration.DISPUTED]
    if not disputed:
        print("       no disputed unit in this instrument; nothing to refuse")
        return False
    region = disputed[0]
    print(f"       disputed regions   {len(disputed)}")
    print(f"       first at           {region.span}  page {region.page}")
    refused = 0
    for u in disputed:
        try:
            it.slice(u.span)
        except DisputedRegionError as e:
            refused += 1
            if refused == 1:
                print(f"       slice() raised     {type(e).__name__}")
                print(f"       reason             {str(e).splitlines()[0][:110]}")
    print(f"       refused            {refused}/{len(disputed)} disputed regions")
    # And the refusal is not merely a raise: the region is unaddressable to `find_all` too.
    leaked = sum(1 for u in disputed for s in it.find_all(it.text[u.span[0]:u.span[1]])
                 if not it.is_disputed(s))
    print(f"       leaked into an addressable span: {leaked}")
    return refused == len(disputed) and leaked == 0


def main() -> int:
    if not PINNED.is_file():
        print(f"FAIL: {PINNED.relative_to(REPO)} is absent. Build it with:")
        print("  python tools/pdf_ingest.py corpus/regulators/fincen_boir_instructions.pdf \\")
        print(f"      {PINNED.relative_to(REPO)} --id source-fincen-boir-instructions --pin")
        return 1
    it, kind, name, sha = deserialise(PINNED.read_bytes())
    print(f"B3  {name}  kind={kind}")
    print(f"    source sha256 {sha[:32]}…")
    print(f"    text   sha256 {it.sha256[:32]}…\n")
    results = [check1(it), check2(it), check3(), check4(it)]
    print()
    for i, ok in enumerate(results, start=1):
        print(f"  check {i}  {'PASS' if ok else 'FAIL'}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
