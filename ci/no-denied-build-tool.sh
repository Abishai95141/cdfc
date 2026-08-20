#!/usr/bin/env bash
# An instrument may not be built by a tool whose licence this repository denies.
#
# WHY THIS GATE EXISTS, dated 16 Aug 2026, and the reason is a hole in the gate beside it.
# `ci/licence-denylist.sh` resolves the RUNTIME set and denies AGPL-3.0 among others. S1 pinned the
# first STATUTE instrument using PDF extractors, which are BUILD-TIME tools — outside that gate's
# RUNTIME set entirely. `pymupdf` is `Dual Licensed - GNU AFFERO GPL 3.0 or Artifex commercial`,
# it was the arm that agreed best, and it passed the existing gate by not being looked at.
#
# **A denylisted licence entering through a door the gate does not watch** is this project's own
# subject matter happening to this project. The exception was not taken: the arm was dropped and
# this gate was written.
#
# The check is on the DECLARED PARTIES in tools/pin_statute.py, not on what happens to be
# installed. A gate that only fires when the tool is present is a gate that passes on every clean
# CI image — which is exactly where a pinned instrument gets rebuilt.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -n "${CDFC_PY:-}" ]; then PY="$CDFC_PY"
elif [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"
else PY="$(command -v python3 || true)"; fi
[ -x "$PY" ] || { echo "GATE FAIL: no interpreter found; set CDFC_PY" >&2; exit 1; }
"$PY" - <<'PYEOF'
import pathlib, re, sys

DENY = {"GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0", "AGPL-3.0-only", "SSPL-1.0",
        "GNU AFFERO", "AFFERO GPL"}

# The licence of every tool that may be an extraction party, RECORDED HERE rather than read from
# the environment. A build tool absent from a clean image must still be checkable, and a table the
# environment cannot silently change is the only way that works.
#
# Adding an arm means adding a row here. That is the point: the diff is visible and the licence is
# stated by the person adding it, not inferred later by whoever is debugging CI.
BUILD_TOOL_LICENCES = {
    "pdfplumber": "MIT",
    "pypdfium2":  "BSD-3-Clause, Apache-2.0, dependency licenses",
    "pymupdf":    "Dual Licensed - GNU AFFERO GPL 3.0 or Artifex commercial",
    "pypdf":      "BSD-3-Clause",   # from the wheel LICENSE file; its metadata declares none
    # B3, 20 Aug 2026. docling reads a SOURCE pack at build time. It declares MIT in PEP 639
    # `License-Expression` and leaves the legacy `License` field EMPTY -- see the reader below,
    # which had to learn that field or it would have called a clearly-licensed package unreadable.
    "docling":    "MIT",
}

# EVERY file under tools/ that declares parties, not one file by name.
#
# WIDENED AT B3, 20 Aug 2026, and the reason is this gate's own reason one level up. The gate was
# written because a denylisted licence entered through a door the RUNTIME gate does not watch.
# B3 adds `tools/pdf_ingest.py`, a SECOND file declaring its own extraction parties -- and a gate
# hard-coded to one filename would have watched the first door while the second stood open.
#
# A file that declares no PARTIES is not an error; a tree where NOTHING declares any is, because
# that is what a renamed constant or a moved file looks like from here.
declared: dict[str, tuple[str, ...]] = {}
for src_path in sorted(pathlib.Path("tools").rglob("*.py")):
    # `[^=\n]*` and not `[^=]*`: a negated character class MATCHES NEWLINES, so the loose form
    # ran past the real PARTIES line and captured a LATER tuple in the same file -- it read
    # pin_statute.py's parties as ("pymupdf", "pypdf") and this gate went red on an AGPL arm that
    # the file explicitly excludes. The annotation of an assignment does not span lines.
    m = re.search(r"^PARTIES\s*(?::[^=\n]*)?=\s*\(([^)]*)\)",
                  src_path.read_text(encoding="utf-8"), re.M)
    if m:
        got = tuple(re.findall(r'"([^"]+)"', m.group(1)))
        if not got:
            print(f"GATE FAIL: {src_path} declares an EMPTY PARTIES tuple", file=sys.stderr)
            raise SystemExit(1)
        declared[str(src_path)] = got

if not declared:
    print("GATE FAIL: no file under tools/ declares a PARTIES tuple. Either the constant was "
          "renamed or the declaring file moved; either way this gate is now checking nothing.",
          file=sys.stderr)
    raise SystemExit(1)

parties = tuple(sorted({p for ps in declared.values() for p in ps}))

fail = []
for p in parties:
    lic = BUILD_TOOL_LICENCES.get(p)
    if lic is None:
        fail.append(f"{p} is a declared extraction party with no row in BUILD_TOOL_LICENCES. "
                    f"A tool whose licence nobody wrote down is not a permissively licensed tool.")
        continue
    for token in DENY:
        if token.lower() in lic.lower():
            fail.append(f"{p} is a declared extraction party and its licence matches the denied "
                        f"token {token!r}: {lic!r}")

# WHERE THE TABLE COULD DRIFT: a recorded licence whose DENIAL VERDICT no longer matches the
# installed distribution's. Checked only when the distribution is present.
#
# The comparison is on the verdict, not on the string. The first version compared strings and went
# red on `MIT` against `MIT License` and on `Artifex commercial` against `Artifex Commercial
# License` -- formatting, not drift. A gate that fires on cosmetics is a gate somebody switches
# off, and then the real drift goes with it. What must not change is whether the tool is DENIED.
def denied(blob: str) -> set[str]:
    return {t for t in DENY if t.lower() in blob.lower()}

# ORDERED. First match wins, so the copyleft markers lead and the 3-clause BSD test precedes the
# 2-clause one -- 3-clause text contains everything 2-clause text does, plus the non-endorsement
# clause, so testing 2-clause first would label every BSD-3 file BSD-2.
#
# The last two entries match the licence BODY rather than its NAME, and they are why this list is
# not a copy of the sibling gate's. `pypdf` declares nothing in metadata and ships the raw BSD
# text, which contains no literal "BSD 3-Clause" anywhere -- so a marker list keyed on licence
# names reads a perfectly clear licence file and concludes it cannot be read. The sibling gate has
# the same blind spot latent; it does not fire today only because the one package that reaches its
# file path happens to spell "Apache License" in its body.
FILE_MARKERS = [
    ("GNU AFFERO", "AGPL"), ("GNU GENERAL PUBLIC LICENSE", "GPL"),
    ("Apache License", "Apache-2.0"), ("MIT License", "MIT"),
    ("Mozilla Public License", "MPL-2.0"),
    ("BSD 3-Clause", "BSD-3-Clause"), ("BSD 2-Clause", "BSD-2-Clause"),
    ("Neither the name of", "BSD-3-Clause"),
    ("Redistribution and use in source and binary forms", "BSD-2-Clause"),
]


def _from_files(dist) -> str | None:
    """The licence out of the wheel's own LICENSE file. PRIMARY evidence, same as the sibling."""
    for f in dist.files or ():
        if pathlib.PurePath(str(f)).name.upper().startswith(("LICENSE", "LICENCE", "COPYING")):
            try:
                head = pathlib.Path(str(f.locate())).read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            for marker, spdx in FILE_MARKERS:
                if marker.lower() in head[:4000].lower():
                    return spdx
    return None


from importlib import metadata  # noqa: E402
for name, recorded in sorted(BUILD_TOOL_LICENCES.items()):
    try:
        d = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        continue
    # PEP 639. Modern wheels leave the legacy `License` field empty and declare
    # `License-Expression` instead -- docling is the live instance. Reading only the legacy field
    # would report "declares no licence" about a package that declares MIT unambiguously, and a
    # gate that fails for the wrong reason gets switched off.
    live = ((d.metadata.get("License-Expression") or "").strip()
            or (d.metadata.get("License") or "").strip())
    classifiers = [c.split("::")[-1].strip()
                   for c in d.metadata.get_all("Classifier") or [] if c.startswith("License ::")]
    shown = live or "; ".join(classifiers)
    if not shown:
        # An empty declared licence is NOT a pass -- the rule ci/licence-denylist.sh learned at P4,
        # where cel-python passed by having nothing to check. So open the wheel's own LICENSE file,
        # which is PRIMARY evidence, before concluding anything. `pypdf` is the live instance: it
        # declares no License field and no classifier, and ships a BSD-3-Clause LICENSE file.
        shown = _from_files(d) or ""
    if not shown:
        fail.append(f"{name}: declares no licence in metadata and ships no readable LICENSE file. "
                    f"A tool whose licence cannot be read is not a permissively licensed tool.")
        continue
    if denied(shown) != denied(recorded):
        fail.append(f"{name}: BUILD_TOOL_LICENCES records {recorded!r} (denied tokens "
                    f"{sorted(denied(recorded))}) but the installed distribution declares "
                    f"{shown!r} (denied tokens {sorted(denied(shown))}). The verdict has drifted.")

if fail:
    print("GATE FAIL: no-denied-build-tool", file=sys.stderr)
    for f in fail:
        print(f"  - {f}", file=sys.stderr)
    raise SystemExit(1)

print(f"ok: {len(parties)} extraction part(y/ies) — {', '.join(parties)} — carry no denied "
      f"licence, declared across {len(declared)} file(s): {', '.join(sorted(declared))}")
PYEOF
