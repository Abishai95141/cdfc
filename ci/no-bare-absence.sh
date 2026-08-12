#!/usr/bin/env bash
# An absence claim must cite a ledger row whose positive control is POSITIVE.
#
# The obvious implementation — grep for absence phrasing "on a line that does not also
# name a positive control" — is defeated in four words by any author who has read it.
# So the gate requires a RESOLVABLE REFERENCE: `ledger:<row_id>`. It resolves the id,
# reads the row, and fails unless positive_control_count > 0. It reads numbers, not prose.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
"$PY" - <<'PYEOF'
import json, pathlib, re, sys
LEDGER = pathlib.Path("reports/validation-ledger.jsonl")
rows = {}
if LEDGER.exists():
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line); rows[r["row_id"]] = r

ABSENCE = re.compile(r"(does not occur|zero hits|not present in|no occurrences)", re.I)
CITE = re.compile(r"ledger:([0-9a-f]{8,})")
ROOTS = ["src", "tests", "docs"]
bad = []
for root in ROOTS:
    for p in pathlib.Path(root).rglob("*"):
        if not p.is_file() or p.suffix not in {".py", ".md", ".sh", ".yaml", ".yml"}:
            continue
        if p.as_posix() == "ci/no-bare-absence.sh":
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not ABSENCE.search(line):
                continue
            m = CITE.search(line)
            if not m:
                bad.append(f"{p}:{n}: absence claim with no `ledger:<row_id>` citation")
                continue
            row = rows.get(m.group(1))
            if row is None:
                bad.append(f"{p}:{n}: cites ledger:{m.group(1)} which does not resolve")
            elif int(row.get("positive_control_count", 0)) <= 0:
                bad.append(
                    f"{p}:{n}: cites ledger:{m.group(1)} whose positive control returned "
                    f"{row.get('positive_control_count')} — the query cannot see a presence"
                )
if bad:
    print("GATE FAIL: absence claims without a live positive control:", *bad, sep="\n  ", file=sys.stderr)
    sys.exit(1)
print("no-bare-absence: OK")
PYEOF
