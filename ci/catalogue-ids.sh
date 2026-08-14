#!/usr/bin/env bash
# Registry row 12. NC- ids unique, defined, non-dangling; every plan document UTF-8.
# The UTF-8 assertion is not decoration: a raw NUL made grep skip an entire document,
# and this gate would have run green over the largest instance of the problem.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh

# --- WHAT THIS GATE ENFORCES, AND WHAT IT DOES NOT --------------------------------------------
#
# Registry row 12 read *"`NC-` ids unique, defined, non-dangling, UTF-8"*, and three of those four
# ran through `plan/scripts/nc_audit.py` whose exit status was DISCARDED by an `|| { echo
# "advisory at P0"; }`. So only the encoding half could fail the gate — and the swallowed half was
# red the whole time (17 orphans, 56 dangling, VERDICT NOT CLEAN). A gate that prints its own
# subject's failure and exits 0 is worse than one that never looked.
#
# The two halves are now separated honestly:
#
#   ENFORCED — the CATALOGUE's ids. `tests/negative/catalogue.yaml` is the live registry this
#   build runs against: ids unique, every guard resolvable, every injector defined. This is
#   checkable and it is checked below, hard.
#
#   ADVISORY, WITH ITS NUMBERS ON SCREEN — the PLAN documents' cross-references. `plan/*.md` is
#   the design record, and its `NC-` mentions include ids for controls that were specified and
#   never built. Making that fatal would make the gate a demand that the plan be edited to match
#   what shipped, which is backwards: the plan is the input. The count is PRINTED on every run so
#   it cannot be forgotten, and it is named as advisory rather than presented as a pass.
if [ -d plan ]; then
  if ! out="$(python3 plan/scripts/nc_audit.py plan 2>&1)"; then
    orph=$(printf '%s' "$out" | sed -n 's/.*ORPHANS (def, never ref) *: *\([0-9]*\).*/\1/p' | head -1)
    dang=$(printf '%s' "$out" | sed -n 's/.*DANGLING (ref, never def) *: *\([0-9]*\).*/\1/p' | head -1)
    echo "catalogue-ids: plan-document cross-references ADVISORY — orphans ${orph:-?}, dangling ${dang:-?}"
    echo "               (the plan is the design record and names controls that were never built;"
    echo "                the CATALOGUE's own ids are enforced below and are not advisory)"
  fi
fi

# THE ENFORCED HALF: the catalogue this build actually runs.
"$PY" - <<'PYEOF'
import pathlib, sys
sys.path.insert(0, ".")
import yaml
from injectors import BY_NAME

raw = yaml.safe_load(pathlib.Path("tests/negative/catalogue.yaml").read_text(encoding="utf-8"))
rows = list(raw.get("entries") or []) if isinstance(raw, dict) else list(raw or [])
bad = []
seen = {}
for e in rows:
    rid = e.get("id")
    if not rid:
        bad.append("an entry carries no id")
        continue
    if rid in seen:
        bad.append(f"{rid}: duplicate id")
    seen[rid] = e
    inj = e.get("injector")
    # `NONE` is a DECLARED absence, and it is admissible only with a reason. Two entries carry it
    # honestly — a bound over a population that is not public, and a person's reading history —
    # and both name what cannot be planted in a file. An entry that claimed `NONE` without saying
    # why would be an uninjectable control counted as evidence.
    if inj == "NONE":
        if not str(e.get("why_impossible") or "").strip():
            bad.append(f"{rid}: injector NONE with no `why_impossible`")
    elif inj and inj not in BY_NAME:
        bad.append(f"{rid}: injector {inj!r} is not defined in injectors/")
    for g in e.get("guard_tests") or ():
        path = g["path"] if isinstance(g, dict) else g
        f = path.split("::")[0]
        if not pathlib.Path(f).is_file():
            bad.append(f"{rid}: guard names {f}, which does not exist")
if not rows:
    print("GATE FAIL: the catalogue is empty; a check over no entries reports success", file=sys.stderr)
    sys.exit(1)
if bad:
    print("GATE FAIL: the catalogue's own ids do not resolve:", *bad, sep="\n  ", file=sys.stderr)
    sys.exit(1)
print(f"catalogue-ids: {len(rows)} entries, ids unique, every injector and guard resolves")
PYEOF
python3 - <<'PYEOF'
import pathlib, sys
bad = []
for p in list(pathlib.Path("plan").glob("*.md")) + list(pathlib.Path("spec").glob("*.md")):
    raw = p.read_bytes()
    if b"\x00" in raw:
        bad.append(f"{p}: NUL byte — grep would skip this file entirely")
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as e:
        bad.append(f"{p}: not UTF-8 ({e})")
if bad:
    print("GATE FAIL:", *bad, sep="\n  ", file=sys.stderr); sys.exit(1)
print("catalogue-ids: OK (encoding clean)")
PYEOF
