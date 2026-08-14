#!/usr/bin/env bash
# An absence claim must cite a ledger row whose positive control is POSITIVE.
#
# The obvious implementation — grep for absence phrasing "on a line that does not also
# name a positive control" — is defeated in four words by any author who has read it.
# So the gate requires a RESOLVABLE REFERENCE: `ledger:<row_id>`. It resolves the id,
# reads the row, and fails unless positive_control_count > 0. It reads numbers, not prose.
set -euo pipefail
cd "$(dirname "$0")/.."
# `$PY` is DISCOVERED by ci/_roots.sh and the source refuses when no interpreter can import cdfc.
# It used to be defaulted to a machine-local absolute path here, so on any other machine this gate
# printed nothing and exited 0.
source ci/_roots.sh
"$PY" - <<'PYEOF'
import json, pathlib, re, sys
LEDGER = pathlib.Path("reports/validation-ledger.jsonl")
# The ledger carries two ROW SHAPES: absence rows (`row_id` + `positive_control_count`) and
# measurement rows (`metric` + `numerator`/`denominator`). This gate resolves the first kind.
#
# It refuses to guess about the third. A line it can classify as neither is a GATE FAILURE, not a
# line to skip: a ledger the gate cannot read is a ledger whose citations it cannot check, and
# skipping quietly is how a citation comes to resolve to nothing.
rows = {}
unclassifiable = []
if LEDGER.exists():
    for n, line in enumerate(LEDGER.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        if "row_id" in r:
            rows[r["row_id"]] = r
        elif "metric" not in r:
            unclassifiable.append(f"reports/validation-ledger.jsonl:{n}: neither an absence row "
                                  f"(no row_id) nor a measurement row (no metric)")
if unclassifiable:
    print("GATE FAIL:", *unclassifiable, sep="\n  ", file=sys.stderr)
    sys.exit(1)

ABSENCE = re.compile(r"(does not occur|zero hits|not present in|no occurrences)", re.I)
CITE = re.compile(r"ledger:([0-9a-f]{8,})")
ROOTS = ["src", "tests", "docs"]

# --- ONE EXEMPTION, AND IT IS A DIFFERENT REQUIREMENT RATHER THAN A HOLE -------------------
#
# `docs/audit/` is a VERBATIM RECORD of a third-party audit's findings, not this build making a
# claim about itself. The ledger exists so that OUR absence claims cannot ship without a positive
# control; an auditor's absence claim ships with something stronger — the command that produced
# it, inline, in the finding.
#
# So the exemption is conditional and the condition is CHECKED below: every finding in the record
# must carry a `**reproduce**` line. An audit record whose findings lost their commands stops
# being evidence and goes back to needing a ledger row like anything else.
AUDIT_RECORD = "docs/audit"
audit_bad = []
for p in sorted(pathlib.Path(AUDIT_RECORD).rglob("*.md")) if pathlib.Path(AUDIT_RECORD).is_dir() else []:
    text = p.read_text(encoding="utf-8", errors="replace")
    # Only the STRUCTURED findings record is held to this. It is identified by the `**claim**`
    # marker, which is what makes a section an assertion about this build rather than narrative.
    # The narrative assessments beside it are a dated third-party reading; they assert nothing
    # the ledger is for, and holding them to a per-heading command count would fail on any
    # heading that happens to start with a bracket.
    if "**claim**" not in text:
        continue
    findings = text.count("\n### [")
    commands = text.count("**reproduce**")
    if findings and commands < findings:
        audit_bad.append(
            f"{p}: {findings} findings but only {commands} carry a `**reproduce**` command. The "
            "audit record is exempt from the ledger BECAUSE each finding carries its own "
            "reproduction; without that it is prose."
        )
if audit_bad:
    print("GATE FAIL: the audit record lost its reproductions:", *audit_bad, sep="\n  ", file=sys.stderr)
    sys.exit(1)

bad = []
for root in ROOTS:
    for p in pathlib.Path(root).rglob("*"):
        if not p.is_file() or p.suffix not in {".py", ".md", ".sh", ".yaml", ".yml"}:
            continue
        if p.as_posix() == "ci/no-bare-absence.sh":
            continue
        if p.as_posix().startswith(AUDIT_RECORD + "/"):
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
