#!/usr/bin/env python
"""P12-B1 — enumerate the pool over the pinned statutory instrument, and report when there is none.

    make pool

**On this tree it reports an absence, and the absence is the finding.** `corpus/instruments/`
carries nine instruments, all `kind: TEMPLATE`, and `statute_instruments` is `[]`. That is not an
oversight: `docs/decisions/D-P7-01-no-statutory-instrument.md` records that P7's entry criterion
asserted a regulation PDF that was never on disk, and that **synthesising one was rejected** —
a span into an invented instrument is not evidence, and it would make every G0 number meaningless
while looking exactly like progress.

So this tool exits **2** with the reason, rather than 0 with an empty pool. An empty pool and an
absent instrument are different facts: the first is a measurement of the regulation, the second is
a measurement of this repository, and reporting the second as the first is the collapse this
project is named for.

**What it does the day an instrument is pinned:** reads it through `qualify.textsource`, enumerates
the `shall` sentences of the pre-registered chapters, writes `experiments/E6/pool.json`, and
appends `textsource_sha256` and `exclusion_rule_sha256` to the lock — in that order, before any
draw hash, which `prereg.append()` enforces.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import canonical_json, digest  # noqa: E402
from cdfc.experiment.enumerate_shall import enumerate_shall  # noqa: E402

MANIFEST = REPO / "corpus" / "instruments" / "MANIFEST.json"
OUT = REPO / "experiments" / "E6" / "pool.json"

EXIT_NO_STATUTE = 2


def statute_instruments() -> list[dict]:
    if not MANIFEST.is_file():
        return []
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return list(raw.get("statute_instruments") or [])


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

    from cdfc.qualify.instruments import load_instrument  # noqa: PLC0415 — only reachable here

    text = load_instrument(statutes[0]["instrument_id"])
    pool = enumerate_shall(text, chapters=frozenset(CHAPTERS))
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
