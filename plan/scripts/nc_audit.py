#!/usr/bin/env python3
"""
nc_audit.py — independent enumeration of the negative-control catalogue.

Written by the session owner as a SECOND instrument, deliberately not the one the
arbitration agent writes. The catalogue has now failed twice; a check authored by
the same pass that did the repair is a self-check, and this corpus has five
documented instances of exactly that failure.

A "definition" is an id introduced by a catalogue row or a heading.
A "reference" is any other occurrence.

Run:  python3 nc_audit.py [plan_dir]
Exit: 0 if the catalogue is clean, 1 otherwise.
"""
import re, sys, glob, os, json, hashlib
from collections import defaultdict

ID_RE = re.compile(r'\bNC-([A-Z]{1,2})(\d{2,3})\b')
# A definition looks like a catalogue row or a heading that introduces the id.
DEF_HINTS = (
    re.compile(r'^\s*-\s*id:\s*`?NC-[A-Z]+\d{2,3}`?'),                 # YAML catalogue entry — the real form
    re.compile(r'^\s*\|\s*\*{0,2}`?NC-[A-Z]\d{2,3}`?\*{0,2}\s*\|'),   # table row starting with the id
    re.compile(r'^#{2,6}\s+\*{0,2}`?NC-[A-Z]\d{2,3}`?'),               # heading
    re.compile(r'^\s*[-*]\s+\*{0,2}`?NC-[A-Z]\d{2,3}`?\*{0,2}\s*[—:-]'),  # bullet definition
)

# A retirement or old->new mapping row leads with the OLD id and names a target.
# Structurally identical to a definition row; semantically its opposite. Failing to
# exclude these was this instrument's second false-positive generator.
MAPPING_ROW = re.compile(r'^\s*\|[^|]*NC-[A-Z]+\d{2,3}[^|]*\|.*(?:→|->|NC-[A-Z]+\d{2,3})')


def is_definition_line(line: str) -> bool:
    return any(h.search(line) for h in DEF_HINTS)


def defined_id(line: str):
    """The id a definition line DEFINES — the leading one only.

    A catalogue row defines the id in its FIRST cell; ids appearing later in the
    same row are prose references (a retirement record, for example, reads
    '| NC-E09 | ... vacated to NC-E20 | -> NC-E20 |' and defines only NC-E09).
    Crediting every id on the line was this instrument's own false-positive
    generator: it reported 24 duplicates where 0 existed.
    """
    if not is_definition_line(line):
        return None
    # a mapping / retirement row records an id, it does not define one
    if line.lstrip().startswith("|") and MAPPING_ROW.search(line):
        return None
    if line.lstrip().startswith("- id:"):
        m = ID_RE.search(line)
        return f"NC-{m.group(1)}{m.group(2)}" if m else None
    if line.lstrip().startswith("|"):
        cells = line.split("|")
        head = cells[1] if len(cells) > 1 else ""
    else:
        head = line
    m = ID_RE.search(head)
    return f"NC-{m.group(1)}{m.group(2)}" if m else None


# Documents that DEFINE the catalogue. The others (08 adversary, 10 verification,
# 11 arbitration, 12 confirmation) are reports ABOUT it: their table rows quote ids
# and would otherwise be miscounted as definitions. Scoping this wrongly inflates
# the duplicate count — the denominator discipline applies to the instrument too.
NORMATIVE = ("00-", "01-", "02-", "03-", "04-", "05-", "06-", "07-", "09-")


def is_normative(path: str) -> bool:
    return os.path.basename(path).startswith(NORMATIVE)


def scan(plan_dir: str):
    defs = defaultdict(list)     # id -> [(file, lineno, text)]
    refs = defaultdict(list)
    files = sorted(f for f in glob.glob(os.path.join(plan_dir, "*.md")))
    nul_report = []
    for path in files:
        raw = open(path, "rb").read()
        nul_report.append((os.path.basename(path), raw.count(b"\x00"), len(raw)))
        text = raw.decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            ids = set(f"NC-{a}{b}" for a, b in ID_RE.findall(line))
            if not ids:
                continue
            head = defined_id(line) if is_normative(path) else None
            for nc in ids:
                target = defs if nc == head else refs
                target[nc].append((os.path.basename(path), i, line.strip()[:110]))
    return files, defs, refs, nul_report


def main():
    plan_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)) + "/.."
    files, defs, refs, nul_report = scan(plan_dir)

    print(f"=== NC CATALOGUE AUDIT — {len(files)} documents ===\n")

    # --- positive control: the instrument can see an id when one exists -------
    probe = "NC-Z99"
    seen_probe = probe in defs or probe in refs
    synthetic = "| **NC-Z99** | synthetic control row |"
    detects = bool(ID_RE.search(synthetic)) and is_definition_line(synthetic)
    print("POSITIVE CONTROL")
    print(f"  parser detects a synthetic definition row : {detects}   (expect True)")
    print(f"  {probe} absent from the real corpus        : {not seen_probe}   (expect True)")
    print(f"  ids matched in corpus                      : {len(set(defs) | set(refs))}\n")
    if not detects:
        print("  INSTRUMENT BROKEN — aborting rather than reporting a clean result.")
        return 1

    # --- NUL scan -------------------------------------------------------------
    bad_nul = [(n, c) for n, c, _ in nul_report if c]
    print("NUL-BYTE SCAN (binary read)")
    print(f"  files containing NUL: {len(bad_nul)} of {len(nul_report)}"
          + ("" if not bad_nul else f"  -> {bad_nul}"))
    print("  note: a shell cannot pass NUL as an argv pattern; the obvious grep test")
    print("        matches everything and reports a false positive on every file.\n")

    dup = {k: v for k, v in defs.items() if len({f for f, _, _ in v}) > 1}
    orphan = sorted(set(defs) - set(refs))
    dangling = sorted(set(refs) - set(defs))

    print("COUNTS")
    print(f"  distinct ids defined      : {len(defs)}")
    print(f"  distinct ids referenced   : {len(refs)}")
    print(f"  DUPLICATE definitions     : {len(dup)}        (must be 0)")
    print(f"  ORPHANS (def, never ref)  : {len(orphan)}        (must be 0)")
    print(f"  DANGLING (ref, never def) : {len(dangling)}        (must be 0)")

    if dup:
        print("\nDUPLICATE DEFINITIONS")
        for k in sorted(dup):
            print(f"  {k}")
            for f, ln, t in dup[k]:
                print(f"      {f}:{ln}  {t}")
    if orphan:
        print(f"\nORPHANS: {', '.join(orphan[:40])}{' …' if len(orphan) > 40 else ''}")
    if dangling:
        print(f"\nDANGLING: {', '.join(dangling[:40])}{' …' if len(dangling) > 40 else ''}")

    # --- band table count -----------------------------------------------------
    band_tables = 0
    for path in files:
        t = open(path, encoding="utf-8", errors="replace").read()
        band_tables += len(re.findall(r'(?im)^.{0,80}\bband\b.{0,80}$\n\|', t))
    print(f"\n  candidate band-table headings across corpus: {band_tables}   (target: 1 normative)")

    clean = not dup and not orphan and not dangling and not bad_nul
    print(f"\nVERDICT: {'CLEAN' if clean else 'NOT CLEAN'}")

    out = os.path.join(plan_dir, "scripts", "nc_audit_result.json")
    json.dump({
        "defined": len(defs), "referenced": len(refs),
        "duplicates": sorted(dup), "orphans": orphan, "dangling": dangling,
        "nul_files": bad_nul, "clean": clean,
    }, open(out, "w"), indent=1)
    print(f"wrote {out}")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
