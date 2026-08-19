"""The audit trail, CHECKED rather than trusted.

`docs/AUDIT-TRAIL.md` is an append-only record of every decision, correction, measurement and
defect. A log nobody checks is a log that goes stale silently, and this repository has already
caught that shape in a gate registry, an evidence map and a sweep report. So the log is machine
checked in BOTH directions:

    every ARTEFACT is in the log     a decision record or measurement nobody logged is invisible
    every LOG ROW resolves           a row citing a file that does not exist is a dead citation

The second direction is the one that matters and it is the one usually missing. It exists because
this build published, on 19 Aug 2026, a measurement whose stated source contained neither the
number nor the quotation attributed to it -- a citation to the author's own prose. Nothing in the
build could catch it: `ci/no-bare-absence.sh` checks that ABSENCE claims cite a resolvable ledger
row, and there was no check that a POSITIVE citation resolves at all.

`--selftest` proves this can go red. A checker that has never been observed failing is not
evidence that it would.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRAIL = REPO / "docs" / "AUDIT-TRAIL.md"

# Artefacts that MUST appear in the trail. A new one is a change somebody made.
TRACKED: tuple[tuple[str, str], ...] = (
    ("docs/decisions", "D-*.md"),
    ("docs/measurements", "*.md"),
)
# A dated correction inside a document is a change to a published claim and is tracked too.
CORRECTION = re.compile(r"CORRECTED\s+(\d{1,2}\s+\w+\s+\d{4})")
# A row's evidence is any backticked path. `docs/x.md` and `src/y.py:12` both resolve.
CITE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|py|sh|json|jsonl|yaml|xlsx))(?::\d+)?`")


def _rows(text: str) -> list[tuple[int, str]]:
    return [(n, ln) for n, ln in enumerate(text.splitlines(), 1) if ln.strip().startswith("| 20")]


def check() -> list[str]:
    if not TRAIL.is_file():
        return [f"{TRAIL.relative_to(REPO)} does not exist; there is no trail to check"]
    text = TRAIL.read_text(encoding="utf-8")
    rows = _rows(text)
    problems: list[str] = []

    # --- DIRECTION 1: every tracked artefact is logged -------------------------------------
    for d, pat in TRACKED:
        for f in sorted((REPO / d).glob(pat)):
            rel = str(f.relative_to(REPO))
            if rel not in text:
                problems.append(f"{rel} exists and is in no AUDIT-TRAIL row")

    # --- Dated corrections inside documents are changes to published claims ----------------
    for f in sorted(REPO.glob("docs/**/*.md")):
        if f == TRAIL:
            continue
        body = f.read_text(encoding="utf-8")
        if CORRECTION.search(body) and str(f.relative_to(REPO)) not in text:
            problems.append(
                f"{f.relative_to(REPO)} carries a dated CORRECTED marker and is in no trail row"
            )

    # --- DIRECTION 2: every citation in the trail resolves ---------------------------------
    #
    # THE DIRECTION THAT WOULD HAVE CAUGHT THE FABRICATED CITATION. A row may name a file that
    # was renamed, moved or never existed, and a reader has no way to tell without opening it.
    for n, ln in rows:
        for m in CITE.finditer(ln):
            if not (REPO / m.group(1)).exists():
                problems.append(f"AUDIT-TRAIL.md:{n} cites `{m.group(1)}`, which does not exist")

    if not rows:
        problems.append("AUDIT-TRAIL.md has no dated rows; an empty trail passes every other check")
    return problems


def selftest() -> int:
    """Plant each failure and require a refusal. Restores the file exactly."""
    original = TRAIL.read_text(encoding="utf-8") if TRAIL.is_file() else None
    if original is None:
        print("selftest needs the trail to exist", file=sys.stderr)
        return 1
    ok = True
    try:
        # (a) a dead citation must be caught
        TRAIL.write_text(original + "\n| 2026-01-01 | DECISION | planted | `docs/NOT-A-FILE.md` |\n",
                         encoding="utf-8")
        if not any("NOT-A-FILE" in p for p in check()):
            print("SELFTEST FAIL: a dead citation was not caught", file=sys.stderr)
            ok = False
        # (b) an unlogged artefact must be caught
        TRAIL.write_text(re.sub(r"^\| 20.*decisions/D-A3-01.*$", "", original, flags=re.M),
                         encoding="utf-8")
        if not any("D-A3-01" in p for p in check()):
            print("SELFTEST FAIL: an unlogged decision record was not caught", file=sys.stderr)
            ok = False
        # (c) an empty trail must be caught
        TRAIL.write_text("# empty\n", encoding="utf-8")
        if not any("no dated rows" in p for p in check()):
            print("SELFTEST FAIL: an empty trail was not caught", file=sys.stderr)
            ok = False
    finally:
        TRAIL.write_text(original, encoding="utf-8")
    if ok:
        print("audit-trail selftest: all three failure modes observed RED, file restored")
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    problems = check()
    if problems:
        print("AUDIT-TRAIL FAIL:", *problems, sep="\n  ", file=sys.stderr)
        return 1
    n = len(_rows(TRAIL.read_text(encoding="utf-8")))
    print(f"audit-trail: {n} rows, every artefact logged and every citation resolves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
