#!/usr/bin/env python3
"""
catalogue_check.py — reproducible enumeration of the NC- catalogue, written for the
arbitration-confirmation pass (plan/12).

WHY A SECOND INSTRUMENT EXISTS.  scripts/nc_audit.py was written by the session owner
as an independent check.  It is deliberately coarse: it treats any table row whose
first cell is an id as a *definition*, so `01` §2.2's retired list and `01` §2.3's
old->new mapping — both of which are REQUIRED by ruling C9.2/C9.4 to name the ids they
retire — are miscounted as live definitions, and every renumbered id is reported as a
duplicate.  Running it against a corpus that HAS been repaired reports 24 duplicates
that do not exist.  An instrument that cannot tell a retirement record from a
definition cannot certify a repair whose whole content is retirement records.

WHAT THIS ONE DOES DIFFERENTLY — three region kinds, decided structurally, never by
line number:

  ENTRY table     header does not look like a mapping or an allocation -> a row whose
                  first cell is an id DEFINES that id.
  MAPPING table   header mentions "old id" / "new id" / "retired id" / "held by" ->
                  ids here are RETIREMENT RECORDS.  Exempt, per C9 rule 4 exemption (a).
  BAND table      first header cell is "band" -> an allocation of ranges.  Exempt.

  history note    a blockquote or emphasised line carrying RETIRED / DELETED /
                  renumber* / "was the id" -> exempt, per C9 rule 4 exemption (b),
                  which names exactly these blocks in `02` R5a, `03` §6, `04` §0.8,
                  `05` §4 and `07` §3.

SPEC docs (00-07, 09) are the plan.  HISTORY docs (08 adversary, 10 verification,
11 arbitration, 12 confirmation) are reports ABOUT the plan: they must be free to
quote a retired id, so their occurrences are recorded and exempted, never counted as
definitions or as live references.

A NUL-byte scan runs first, with a positive control, because one raw NUL in `03`
previously made grep skip an entire document and would have made the id-collision CI
gate run green over the largest instance of the problem.  The read is binary.  A shell
cannot pass a NUL as an argv pattern, so the obvious `grep -P '\\x00'` test either
matches everything or nothing depending on the tool, and reports a false result on
every file; the control below proves this instrument fires on a file that really has
one and stays silent on one that does not.

Run:  python3 catalogue_check.py [plan_dir]
Exit: 0 clean, 1 otherwise.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import tempfile
from collections import defaultdict

ID_RE = re.compile(r"\bNC-([A-Z]{1,2})(\d{2,3})([a-z]?)\b")

SPEC = ("00-", "01-", "02-", "03-", "04-", "05-", "06-", "07-", "09-")
HISTORY = ("08-", "10-", "11-", "12-")

MAPPING_HDR = ("old id", "retired id", "new id", "held by", "where its content went")
# An id-RETIREMENT signal, not merely the word "retired".  `07`'s NC-A30 entry is
# *about* retiring a surface row and says so in prose; a bare substring test on
# "retired" swallows the entry and then reports NC-A30 as dangling at six sites.  An
# over-broad exemption is the same failure as no exemption, pointed the other way:
# it hides the thing the check exists to find.
HISTORY_MARKS = tuple(re.compile(p) for p in (
    r"NC-[A-Z]{1,2}\d{2,3}`?\*{0,2}[^.\n]{0,90}\b(?:is|are|was|were|now)\b[^.\n]{0,40}RETIRED",
    r"RETIRED PERMANENTLY",
    r"\bRETIRED\b[^.\n]{0,40}(?:id|ids)\b",
    r"`?NC-[A-Z]{1,2}\d{2,3}`?\*{0,2}\s*(?:→|->|becomes|became)\s*\*{0,2}`?NC-",
    r"\brenumber(?:ed|ing|s)?\b",
    r"\bRenumber(?:ed|ing|s)?\b",
    r"the ids? then called",
    r"\bId note\b",
    r"STOOD HERE IS DELETED",
    r"historical id",
    r"\bvacated\b",
    r"this entry was\b",
    r"it was `NC-",
    r"no longer allocated",
    r"TABLE THAT STOOD HERE",
    r"PARTITION THAT STOOD HERE",
    r"reservation paragraph that stood here",
    r"\bre-keyed\b",
    r"\bformer\b[^.\n]{0,12}`?NC-",
    r"under two different ids",
    r"REFERENCE, not a definition",
    r"\bold ids?\b[^.\n]{0,40}RETIRED",
    r"RETIRED\b[^.\n]{0,60}never reassigned",
    r"\ballocated\b[^.\n]{0,20}`NC-",
    r"NC-[A-Z]{1,2}\d{2,3}[^.\n]{0,60}\bcollide(?:d|s)?\b",
    r"\bcollide(?:d|s)?\b[^.\n]{0,60}NC-[A-Z]{1,2}\d{2,3}",
    r"was defined [\*\"']{0,3}under",
    r"\bcollisions?\b[^.\n]{0,60}`NC-",
    r"`NC-[A-Z]{1,2}\d{2,3}`[^.\n]{0,60}\bcollisions?\b",
))

# Inside a DEFINITION row, ids that sit in an italic parenthetical or an italic quote
# are the entry's own provenance note — "*(was NC-N11 — re-keyed)*", "defined *\"under
# NC-Q22's entry\"*" — not live references.  Harvesting them as references turns every
# correctly-annotated renumbering into a dangling reference, which is the failure mode
# that makes a verifier demand edits that would REMOVE the audit trail.
ASIDE = re.compile(r"\*\([^)]*\)\*|\*\"[^\"]*\"\*|\*\u201c[^\u201d]*\u201d\*")

# 01 §2.2 / §2.3 are the registry's own bookkeeping.  Named, not guessed.
REGISTRY_META_HEADINGS = (
    "THE RETIRED LIST",
    "THE OLD → NEW MAPPING",
    "THE BAND TABLE",
)


def doc_class(path: str) -> str:
    b = os.path.basename(path)
    if b.startswith(SPEC):
        return "SPEC"
    if b.startswith(HISTORY):
        return "HISTORY"
    return "OTHER"


def ids_in(line: str) -> set[str]:
    """Bare ids, letter suffixes folded onto their parent entry (C9 rule 3:
    'a letter suffix names a guard test inside an entry, never a second break')."""
    return {f"NC-{a}{n}" for a, n, _sfx in ID_RE.findall(line)}


def first_cell(line: str) -> str:
    parts = line.split("|")
    return parts[1] if len(parts) > 2 else ""


YAML_DEF = re.compile(r"^\s*-\s*id:\s*`?(NC-[A-Z]{1,2}\d{2,3})`?\s*$")


def cell_is_bare_id(cell: str) -> tuple[str | None, bool]:
    """A definition row's first cell is the id and (optionally) an annotation such as
    '(new, F13)', '(new, `injector: NONE`)', '*(the former NC-Q22b)*'.

    Returns (id, is_amendment).  '*(amended)*' marks a document editing an entry whose
    home is elsewhere; that is not a second definition and must not be counted as a
    collision, but it IS a cross-document write and is reported separately."""
    c = cell.strip()
    amended = "amended" in c.lower()
    c = re.sub(r"\*\(.*?\)\*", " ", c)          # *(italic aside)*
    c = re.sub(r"\((?:new|NEW)[^)]*\)", " ", c)  # (new, ...)
    c = c.replace("**", "").replace("`", "").strip()
    m = re.fullmatch(r"NC-([A-Z]{1,2})(\d{2,3})([a-z]?)", c)
    return (f"NC-{m.group(1)}{m.group(2)}" if m else None), amended


def scan_file(path: str):
    """Yield (lineno, line, region) where region in {ENTRY, MAPPING, BAND, HIST, PROSE}."""
    raw = open(path, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    table_kind = None          # active table's kind
    meta_section = False       # inside a §2.1/§2.2/§2.3 registry-meta heading
    out = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("#"):
            table_kind = None
            meta_section = any(h in stripped for h in REGISTRY_META_HEADINGS)

        # table header detection: a '|' row immediately followed by a '|---' separator
        if stripped.startswith("|") and i < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
            cells = [c.strip().lower().replace("*", "").replace("`", "")
                     for c in stripped.strip("|").split("|")]
            if cells and cells[0] == "band":
                table_kind = "BAND"
            elif any(any(h in c for h in MAPPING_HDR) for c in cells):
                table_kind = "MAPPING"
            else:
                table_kind = "ENTRY"
        elif not stripped.startswith("|"):
            table_kind = None

        if meta_section:
            region = "HIST"
        elif table_kind == "BAND":
            region = "BAND"
        elif table_kind == "MAPPING":
            region = "HIST"
        elif table_kind == "ENTRY":
            region = "ENTRY"
            if any(m.search(line) for m in HISTORY_MARKS) and not cell_is_bare_id(first_cell(line))[0]:
                region = "HIST"
        else:
            region = "PROSE"

        out.append((i, line, region))

    # --- BLOCK-LEVEL history marking.  C9 rule 4 exemption (b) exempts "a block a
    # document marks as a retirement or history note", not a line.  A per-line test
    # under-exempts: `02` R5a's blockquote carries "RETIRED permanently" two lines
    # below the id it retires, and a line-scoped instrument then reports the
    # retirement record itself as a live dangling reference.  Blocks are blockquote
    # runs and prose paragraphs, delimited by blank lines and headings.
    blocks: list[list[int]] = []
    cur: list[int] = []
    for idx, (_i, line, region) in enumerate(out):
        s = line.strip()
        if not s or s.startswith("#") or region in ("ENTRY", "BAND"):
            if cur:
                blocks.append(cur)
                cur = []
            continue
        cur.append(idx)
    if cur:
        blocks.append(cur)

    for blk in blocks:
        # A block that CONTAINS a catalogue entry is a definition, never a history
        # note, whatever words appear inside it.
        if any(YAML_DEF.match(out[j][1]) for j in blk):
            continue
        if any(any(m.search(out[j][1]) for m in HISTORY_MARKS) for j in blk):
            for j in blk:
                i, line, _r = out[j]
                out[j] = (i, line, "HIST")

    return raw, out


def parse_registered_in_retired_table(plan_dir: str) -> dict:
    """`01` §2.2's last row is not a retirement — it REGISTERS `NC-L01`, an id C9 found
    orphaned in `07`.  A row that registers inside the retired table is a placement
    wart, reported as such, but it is a real registry row and must resolve."""
    path = os.path.join(plan_dir, "01-validation-methodology.md")
    reg = {}
    inside = False
    for n, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        s_ = line.strip()
        if s_.startswith("#"):
            inside = "THE RETIRED LIST" in s_
            continue
        if not inside or not s_.startswith("|"):
            continue
        cell = first_cell(line)
        if "not** retired" in cell or "not retired" in cell.lower():
            for nc in ids_in(cell):
                reg[nc] = n
    return reg


def parse_retired(plan_dir: str) -> set[str]:
    """Read the RETIRED list out of `01` §2.2 rather than hardcoding it."""
    path = os.path.join(plan_dir, "01-validation-methodology.md")
    retired: set[str] = set()
    inside = False
    for line in open(path, encoding="utf-8", errors="replace"):
        s = line.strip()
        if s.startswith("#"):
            inside = "THE RETIRED LIST" in s
            continue
        if not inside or not s.startswith("|"):
            continue
        cell = first_cell(line)
        if "not** retired" in cell or "not retired" in cell.lower():
            continue  # the `NC-L01` row: a REGISTRATION living inside the retired table
        # ranges: `NC-Q23`–`NC-Q29`
        m = re.search(r"NC-([A-Z]{1,2})(\d{2,3})\S*\s*[–-]\s*`?NC-([A-Z]{1,2})(\d{2,3})", cell)
        if m and m.group(1) == m.group(3):
            for n in range(int(m.group(2)), int(m.group(4)) + 1):
                retired.add(f"NC-{m.group(1)}{n:02d}")
            continue
        # EXACT tokens.  `NC-Q22b` retires the SUFFIXED id only: folding the suffix
        # onto its parent would retire `NC-Q22`, which `01` §2.1 still allocates to
        # `04` — an instrument that invents a retirement then reports every live use
        # of a live id as a dangling reference.
        for a, n, sfx in ID_RE.findall(cell):
            retired.add(f"NC-{a}{n}{sfx}")
    return {r for r in retired if not r[-1].isalpha() or not r[-2].isdigit()} | \
           {r for r in retired if r[-1].isalpha() and r[-2].isdigit()}


def nul_scan(plan_dir: str):
    files = sorted(glob.glob(os.path.join(plan_dir, "*.md")))
    rows = []
    for p in files:
        raw = open(p, "rb").read()
        nul = raw.count(b"\x00")
        try:
            raw.decode("utf-8")
            enc = "utf-8"
        except UnicodeDecodeError as e:
            enc = f"NOT-utf-8 ({e.reason} at byte {e.start})"
        rows.append((os.path.basename(p), len(raw), nul, enc))
    return rows


def positive_control():
    """Prove the NUL detector fires.  Two synthetic files, one with a real NUL."""
    d = tempfile.mkdtemp(prefix="nulctl_")
    good = os.path.join(d, "control_clean.md")
    bad = os.path.join(d, "control_with_nul.md")
    open(good, "wb").write(b"# clean\n| **NC-Z99** | synthetic control row |\n")
    open(bad, "wb").write(b"# dirty\n| **NC-Z98** | synthetic\x00control row |\n")
    res = {}
    for label, p in (("clean", good), ("with_nul", bad)):
        raw = open(p, "rb").read()
        res[label] = raw.count(b"\x00")
    # parser control: can the definition detector see a synthetic row at all?
    detects = (cell_is_bare_id(" **NC-Z99** ")[0] == "NC-Z99"
               and YAML_DEF.match("- id: NC-Z97") is not None
               and cell_is_bare_id(" **NC-Z96** *(amended)* ")[1] is True)
    return res, detects, bad


def main() -> int:
    plan_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..")
    plan_dir = os.path.abspath(plan_dir)
    files = sorted(glob.glob(os.path.join(plan_dir, "*.md")))

    print(f"=== NC CATALOGUE CHECK (arbitration C9) — {len(files)} documents in {plan_dir} ===\n")

    # ---------------------------------------------------------------- controls
    ctl, detects, bad_path = positive_control()
    print("POSITIVE CONTROLS")
    print(f"  definition parser sees a synthetic entry row  : {detects}   (expect True)")
    print(f"  NUL detector on a file WITHOUT a NUL          : {ctl['clean']}      (expect 0)")
    print(f"  NUL detector on a file WITH one real NUL      : {ctl['with_nul']}      (expect 1)")
    ok_ctl = detects and ctl["clean"] == 0 and ctl["with_nul"] == 1
    print(f"  instrument trustworthy                        : {ok_ctl}")
    if not ok_ctl:
        print("  INSTRUMENT BROKEN — refusing to report a clean result.")
        return 1
    print()

    # ---------------------------------------------------------------- NUL scan
    print("NUL-BYTE AND ENCODING SCAN (binary read; a shell cannot pass NUL as argv)")
    rows = nul_scan(plan_dir)
    dirty = [r for r in rows if r[2]]
    for name, size, nul, enc in rows:
        flag = "  <-- NUL" if nul else ""
        print(f"  {name:34s} {size:>8d} B  NUL={nul}  enc={enc}{flag}")
    print(f"  files containing NUL: {len(dirty)} of {len(rows)}   (must be 0)\n")

    # ---------------------------------------------------------------- retired
    retired = parse_retired(plan_dir)
    registered_in_2_2 = parse_registered_in_retired_table(plan_dir)
    print(f"RETIRED IDS read from `01` §2.2: {len(retired)}")
    print(f"  {', '.join(sorted(retired))}\n")

    # ---------------------------------------------------------------- scan
    defs = defaultdict(list)
    refs = defaultdict(list)
    hist = defaultdict(list)
    amendments = defaultdict(list)
    index_rows = defaultdict(list)

    for path in files:
        cls = doc_class(path)
        base = os.path.basename(path)
        _raw, scanned = scan_file(path)
        for lineno, line, region in scanned:
            found = ids_in(line)
            if not found:
                continue
            if cls == "HISTORY" or region in ("HIST", "BAND"):
                for nc in found:
                    hist[nc].append((base, lineno))
                continue

            # --- definition form 1: a YAML catalogue entry (`02`, `05`, `06`, `07`)
            m = YAML_DEF.match(line)
            if m:
                defs[m.group(1)].append((base, lineno, line.strip()[:100]))
                continue

            # --- definition form 2: a heading (`01`, the registry itself)
            if re.match(r"^#{2,6}\s+\*{0,2}`?NC-", line.strip()):
                dd = sorted(found)[0]
                defs[dd].append((base, lineno, line.strip()[:100]))
                for nc in found - {dd}:
                    refs[nc].append((base, lineno))
                continue

            # --- definition form 3: an entry-table row keyed on the id
            if region == "ENTRY":
                d, amended = cell_is_bare_id(first_cell(line))
                if d and amended:
                    amendments[d].append((base, lineno, line.strip()[:100]))
                    refs[d].append((base, lineno))
                    continue
                if d:
                    # FIRST site in a document defines; a later same-document listing
                    # is that document's own index (e.g. `04` §4.4, `06` §3) and is a
                    # REFERENCE.  Counting it as a definition manufactures both a
                    # duplicate and an orphan out of one healthy entry.
                    if any(f == base for f, _l, _t in defs[d]):
                        index_rows[d].append((base, lineno))
                        refs[d].append((base, lineno))
                    else:
                        defs[d].append((base, lineno, line.strip()[:100]))
                    body = ASIDE.sub(" ", line)
                    for nc in ids_in(body) - {d}:
                        refs[nc].append((base, lineno))
                    continue

            for nc in found:
                refs[nc].append((base, lineno))

    # count band tables corpus-wide, by header signature
    band_hdr = []
    for path in files:
        for i, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
            if re.match(r"^\s*\|\s*\*{0,2}`?Band`?\*{0,2}\s*\|", line):
                low = line.lower()
                if any(h in low for h in MAPPING_HDR):
                    continue   # `01` §2.3's mapping table also opens with a Band column
                band_hdr.append((os.path.basename(path), i))

    # A C9 DUPLICATE is an id defined as a catalogue entry in TWO DOCUMENTS — that is
    # the collision the ruling is about.  An id listed twice inside ONE document (an
    # entry plus that document's own index row, e.g. `04` §4.4) is a summary, not a
    # collision, and is reported separately so it is visible without being counted.
    for nc, ln in registered_in_2_2.items():
        if nc not in defs:
            defs[nc].append(("01-validation-methodology.md", ln,
                             "registered in the RETIRED table (placement wart)"))

    dup = {k: v for k, v in defs.items() if len({f for f, _l, _t in v}) > 1}
    intra = {k: v for k, v in index_rows.items()}
    orphan = sorted(set(defs) - set(refs))
    dangling = sorted(set(refs) - set(defs))
    retired_redefined = sorted(set(defs) & retired)
    retired_live_ref = sorted(set(refs) & retired)

    print("COUNTS")
    print(f"  distinct ids DEFINED            : {len(defs)}")
    print(f"  total definition sites          : {sum(len(v) for v in defs.values())}")
    print(f"  distinct ids REFERENCED (live)  : {len(refs)}")
    print(f"  total live reference sites      : {sum(len(v) for v in refs.values())}")
    print(f"  distinct ids in history/exempt  : {len(hist)}")
    print(f"  DUPLICATE definitions (2+ docs) : {len(dup)}     (must be 0)")
    print(f"  same-doc index restatements     : {len(intra)}    (informational)")
    print(f"  cross-doc amendments (*amended*): {len(amendments)}    (informational)")
    print(f"  DANGLING (ref'd, never defined) : {len(dangling)}     (must be 0)  <- C9.5")
    print(f"  entries with no prose cross-ref : {len(orphan)}    (informational, NOT an error)")
    print("      `10` §4.3 and C9.5 define an ORPHAN as *referenced, defined nowhere* —")
    print("      the DANGLING line above.  `01` §2.4 rule 3 defines the orphan GUARD test")
    print("      over `tests/negative/` functions, which do not exist yet.  A catalogue")
    print("      entry that no prose sentence happens to cite is the normal, healthy state")
    print("      of a catalogue and is reported here only so the number is not hidden.")
    print(f"  RETIRED ids REDEFINED           : {len(retired_redefined)}     (must be 0)")
    print(f"  RETIRED ids in a LIVE reference : {len(retired_live_ref)}     (must be 0)")
    print(f"  BAND TABLES in the corpus       : {len(band_hdr)}     (must be 1)")
    for b, l in band_hdr:
        print(f"      {b}:{l}")

    if dup:
        print("\nDUPLICATE DEFINITIONS")
        for k in sorted(dup):
            print(f"  {k}")
            for f, ln, t in dup[k]:
                print(f"      {f}:{ln}  {t}")
    if orphan:
        print("\nENTRIES WITH NO PROSE CROSS-REFERENCE (informational)")
        for k in orphan:
            f, ln, _t = defs[k][0]
            print(f"  {k}  defined at {f}:{ln}")
    if dangling:
        print("\nDANGLING (referenced, defined nowhere)")
        for k in dangling:
            where = ", ".join(f"{f}:{l}" for f, l in refs[k][:6])
            note = "  [RETIRED]" if k in retired else ""
            print(f"  {k}{note}  referenced at {where}")
    if retired_redefined:
        print("\nRETIRED IDS REDEFINED")
        for k in retired_redefined:
            for f, ln, t in defs[k]:
                print(f"  {k}  {f}:{ln}  {t}")
    if retired_live_ref:
        print("\nRETIRED IDS IN A LIVE (non-history) REFERENCE")
        for k in retired_live_ref:
            where = ", ".join(f"{f}:{l}" for f, l in refs[k][:6])
            print(f"  {k}  {where}")

    clean = not (dup or dangling or retired_redefined
                 or retired_live_ref or dirty) and len(band_hdr) == 1
    print(f"\nVERDICT: {'CLEAN' if clean else 'NOT CLEAN'}")

    out = os.path.join(plan_dir, "scripts", "catalogue_check_result.json")
    json.dump({
        "documents": len(files),
        "defined": len(defs),
        "definition_sites": sum(len(v) for v in defs.values()),
        "referenced": len(refs),
        "reference_sites": sum(len(v) for v in refs.values()),
        "duplicates": sorted(dup),
        "same_doc_index_restatements": sorted(intra),
        "cross_doc_amendments": sorted(amendments),
        "no_prose_cross_reference": orphan,
        "dangling": dangling,
        "retired_count": len(retired),
        "retired_redefined": retired_redefined,
        "retired_live_reference": retired_live_ref,
        "band_tables": band_hdr,
        "nul_files": [r[0] for r in dirty],
        "clean": clean,
    }, open(out, "w"), indent=1)
    print(f"wrote {out}")
    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
