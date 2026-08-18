#!/usr/bin/env python
"""P12-B1 — enumerate the pool over the pinned statutory instrument, and report when there is none.

    make pool

**THIS DOCSTRING USED TO SAY THE INSTRUMENT WAS ABSENT, AND IT IS NOT.** It read *"`corpus/
instruments/` carries nine instruments, all `kind: TEMPLATE`, and `statute_instruments` is `[]`"*.
There are TEN instruments today and one of them is a STATUTE: S1 pinned
`statute-fm-regulations-2025` (1,218 units, two independent external extractors), so
`statute_instruments` is `["statute-fm-regulations-2025"]` and the absence branch below no longer
fires on this tree.

The absence branch is KEPT rather than deleted, because it is the honest behaviour for any tree
whose corpus holds no statute: this tool exits **2** with the reason rather than 0 with an empty
pool. An empty pool and an absent instrument are different facts — the first is a measurement of
the regulation, the second is a measurement of the repository — and reporting the second as the
first is the collapse this project is named for.

**With the instrument pinned, this tool reads it through `qualify.instruments.InstrumentStore`,
enumerates the `shall` sentences of the pre-registered chapters, writes `experiments/E6/pool.json`,
and the operator appends `textsource_sha256` and `exclusion_rule_sha256` to the lock — in that
order, before any draw hash, which `prereg.append()` enforces.**

**On this tree it exits 3, and that is the current finding.** The pinned instrument's extracted
headings are not the pre-registered chapter titles — the text reads `CHAPTER II REGISTRATION OF
FUND MANAGEMENT ENTITY (FME) …` where `PREREGISTRATION.md` names `Chapter III — Registration and
Obligations of Fund Management Entities` — so `UndeclaredHeading` fires over 25 unmatched heading
units. The chapter list is part of the HASHED pool construction and may not be relaxed to fit, so
the tool reports the mismatch and builds nothing: either the list or the extraction is wrong, and
which of the two is itself a finding.

**Two bugs made the pinned-instrument path unreachable and are fixed here.** It imported a
`load_instrument` that does not exist in `cdfc.qualify.instruments` — an ImportError the moment a
statute WAS pinned — and it then indexed `statutes[0]["instrument_id"]` although `MANIFEST.json`
carries `statute_instruments` as a list of plain id STRINGS, which is a TypeError one line later.
Neither could fire while the absence branch always returned first, which is how they survived
unnoticed: the absence was masking the breakage.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import canonical_json, digest  # noqa: E402
from cdfc.experiment.draw import ChapterNotFound  # noqa: E402
from cdfc.experiment.enumerate_shall import (  # noqa: E402
    NotAStatute,
    UndeclaredHeading,
    enumerate_shall,
)

MANIFEST = REPO / "corpus" / "instruments" / "MANIFEST.json"
OUT = REPO / "experiments" / "E6" / "pool.json"

EXIT_NO_STATUTE = 2
EXIT_POOL_NOT_BUILT = 3   # a statute is pinned but the pool could not be enumerated over it


def statute_instruments() -> list[str]:
    """The pinned STATUTE ids. `MANIFEST.json` carries them as plain strings, not as row objects."""
    if not MANIFEST.is_file():
        return []
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return [str(i) for i in (raw.get("statute_instruments") or [])]


def main() -> int:
    from tools.e6.preregister import CHAPTERS  # the chapter list is part of the hashed criterion

    statutes = statute_instruments()
    if not statutes:
        raw = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
        kinds = sorted({i.get("kind", "?") for i in raw.get("instruments", [])})
        print("POOL NOT BUILT — no statutory instrument is pinned in this repository.", file=sys.stderr)
        print(f"  instruments on disk : {len(raw.get('instruments', []))}, kinds {kinds}", file=sys.stderr)
        print("  statute_instruments : []", file=sys.stderr)
        print(f"  chapters the pre-registration would sample : {len(CHAPTERS)}", file=sys.stderr)
        print("", file=sys.stderr)
        print(str(raw.get("statute_absent_reason", "")).strip(), file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  This exits non-zero rather than writing an empty pool. An empty pool is a "
            "measurement of the\n  regulation; an absent instrument is a measurement of this "
            "repository. See docs/decisions/\n  D-P7-01-no-statutory-instrument.md and "
            "docs/measurements/P12-entry.md.",
            file=sys.stderr,
        )
        return EXIT_NO_STATUTE

    # `InstrumentStore.get` is the reader; there is no `load_instrument` in that module and there
    # never was one. Imported here rather than at module scope so the absence branch above needs
    # nothing from the qualification package.
    from cdfc.qualify.instruments import InstrumentStore  # noqa: PLC0415 — only reachable here

    instrument_id = statutes[0]
    # stderr, so this line stays adjacent to whichever refusal follows it rather than being
    # reordered behind it by stdout buffering.
    print(f"  instrument  : {instrument_id}", file=sys.stderr)
    it = InstrumentStore(REPO / "corpus" / "instruments").get(instrument_id)
    try:
        pool = enumerate_shall(it, chapters=frozenset(CHAPTERS))
    except NotAStatute as e:
        print(f"POOL NOT BUILT — {instrument_id} is not usable as a pool source: {e}", file=sys.stderr)
        return EXIT_NO_STATUTE
    except (UndeclaredHeading, ChapterNotFound) as e:
        # The pre-registered chapter list is part of the HASHED criterion, so it may not be relaxed
        # to make a run happen. A chapter that does not match the pinned text is a fact about the
        # pair (list, instrument) and it is reported as one.
        print("POOL NOT BUILT — the pre-registered chapters do not match the pinned instrument.",
              file=sys.stderr)
        print(f"  {type(e).__name__}: {e}", file=sys.stderr)
        print("  The chapter list is hashed into experiments/E6/PREREGISTRATION.md and cannot be "
              "loosened\n  to fit; either the list or the extraction is wrong, and which one is a "
              "finding.", file=sys.stderr)
        return EXIT_POOL_NOT_BUILT
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(canonical_json({
        "pool_sha256": pool.sha256,
        "source_sha256": pool.source_sha256,
        "chapters": list(pool.chapters),
        "obligations": [o.as_obj() for o in pool.obligations],
        "excluded": [e.as_obj() for e in pool.excluded],
    }) + b"\n")
    print(f"  obligations : {len(pool.obligations)}")
    print(f"  excluded    : {len(pool.excluded)} on pages {list(pool.excluded_pages())}")
    print(f"  pool_sha256 : {pool.sha256}")
    print(f"  exclusion rule sha256 : {digest([e.as_obj() for e in pool.excluded])}")
    print(f"  wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
