#!/usr/bin/env bash
# Registry row 113. AN IMPORTED PRIOR MAY NOT BECOME OUR THRESHOLD.
#
# Do-not-build row 9: Luxembourg's 1.72% is a COMPARATOR FOR THE PITCH and an input to nothing.
# The moment it reaches a remedy string a reader takes it as the number this system checks against,
# and it is a figure from another regulator, another fund population and another year.
#
# THIS GATE WALKS THE STRUCTURE, NOT THE TEXT — and it was rewritten to do so after its first
# version went red on `remedies.yaml`'s own COMMENT explaining the ban. That is the eleventh time in
# this build a check has been defeated by prose describing the thing it checks for, and the cure is
# the same one every time: a YAML comment is stripped by the loader and reaches no reader, so the
# subject is the LOADED VALUES and the RENDERED REPORT, never the file's bytes.
#
# THE LAWFUL CASE MUST STAY LAWFUL. `remedies.yaml` cites CSSF Circular 24/856's Tables 1-5 as the
# KIND OF INSTRUMENT that would make a valuation judgment checkable, quoting its own published
# bands. Citing an instrument is not importing a threshold, and a copy gate that blocked the lawful
# case would be a gate people disable.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_surface_roots || { echo "GATE FAIL: refusing to report success over a missing surface root" >&2; exit 1; }

"$PY" - <<'PYEOF'
import pathlib, re, sys
sys.path.insert(0, "src")
from cdfc.surface.unchecked import REMEDIES_PATH, load_remedies

FIGURE = re.compile(r"\b1[.,]72\s*%?")
# "NAV tolerance" as an ASSERTION, not as a question. `tolerance of 5`, `tolerance = 5` assert;
# `what tolerance`, `tolerance?` ask, and asking is the whole point of the panel.
AS_THRESHOLD = re.compile(r"nav\s+tolerance\s*(?:of|is|=|:)\s*[\d.]", re.IGNORECASE)

scanned, bad = 0, []

def check(where: str, text: str) -> None:
    global scanned
    scanned += 1
    if FIGURE.search(text):
        bad.append(f"{where}: the Luxembourg 1.72% prior: {text.strip()[:100]}")
    if AS_THRESHOLD.search(text):
        bad.append(f"{where}: 'NAV tolerance' as a threshold, not a question: {text.strip()[:100]}")

# 1. THE LOADED VALUES — what a reader actually sees.
remedies, unremediable = load_remedies()
for code, r in remedies.items():
    check(f"remedies[{code}].text", r.text)
    check(f"remedies[{code}].applies_to", r.applies_to)
    if r.source:
        check(f"remedies[{code}].source", r.source)
for code, argument in unremediable.items():
    check(f"deliberately_unremediable[{code}]", argument)

# 2. THE RENDERED REPORT — the artifact, if one has been produced. A value can reach a reader
#    through a template as well as through this file.
for report in pathlib.Path("reports").rglob("report.html"):
    html = report.read_text(encoding="utf-8", errors="replace")
    body = html.split("</style>", 1)[-1]
    check(f"{report}", body)

if scanned == 0:
    print("GATE FAIL: nothing was scanned; a check over no values reports success", file=sys.stderr)
    sys.exit(1)
if bad:
    print("GATE FAIL: an imported prior reached a surface:", file=sys.stderr)
    print("\n".join("  " + b for b in bad), file=sys.stderr)
    print("  1.72% is a comparator for the pitch and an input to nothing. Citing the KIND of", file=sys.stderr)
    print("  instrument that would settle a question is lawful; adopting somebody else's number", file=sys.stderr)
    print("  as our threshold is not.", file=sys.stderr)
    sys.exit(1)
print(f"no-imported-prior: OK ({scanned} rendered values and artifacts scanned)")
PYEOF
