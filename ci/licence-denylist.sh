#!/usr/bin/env bash
# Registry row 11. No copyleft-incompatible licence in the resolved runtime set.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${CDFC_PY:-/Users/abishaikc/Gift/.venv/bin/python}"
"$PY" - <<'PYEOF'
import sys, json, pathlib
from importlib import metadata
DENY = {"GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later", "AGPL-3.0", "AGPL-3.0-only", "SSPL-1.0"}
RUNTIME = {"lxml", "openpyxl", "et-xmlfile", "et_xmlfile"}
rows, bad = [], []
for name in sorted(RUNTIME):
    try:
        d = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        continue
    lic = (d.metadata.get("License") or "").strip()
    classifiers = [c for c in d.metadata.get_all("Classifier") or [] if c.startswith("License ::")]
    warrant = "METADATA (SECONDARY — the LICENSE file was not opened)"
    rows.append({"name": d.metadata["Name"], "version": d.version, "licence": lic or classifiers,
                 "warrant": warrant, "opened_by": None, "opened_at": None})
    blob = f"{lic} {' '.join(classifiers)}"
    for d_ in DENY:
        if d_.lower() in blob.lower():
            bad.append((d.metadata["Name"], d_))
out = pathlib.Path("docs/LICENCES.md")
lines = ["# docs/LICENCES.md — resolved runtime dependency licences", "",
         "**Every row here is SECONDARY.** The licence was read from package metadata, not from the",
         "LICENSE file. A licence nobody opened is not a licence: spec §III lists this as a hard block",
         "from P2, and the `opened_by` / `opened_at` columns stay empty until someone opens them.", "",
         "| name | version | licence | warrant | opened_by | opened_at |", "|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['name']} | {r['version']} | {r['licence']} | {r['warrant']} | — | — |")
out.write_text("\n".join(lines) + "\n")
if bad:
    print(f"GATE FAIL: denylisted licence: {bad}", file=sys.stderr); sys.exit(1)
print(f"licence-denylist: OK ({len(rows)} runtime deps, all SECONDARY)")
PYEOF
