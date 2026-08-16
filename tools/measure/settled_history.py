#!/usr/bin/env python
"""P15-B2's demonstration — the settled fraction over time, **including the step DOWN.**

    make history

Criterion A8 is *the number falls when the template changes*, and this is the artifact that shows
it. Two points, both computed rather than typed:

1. the reference run against the pinned blank — 1,898 of 3,747;
2. the same filing after the FY2029-30 template bump, with the churn sweep applied.

**The dates are ARGUMENTS.** `surface/history.py` reads no clock and neither does this: a chart
whose points move because the file was regenerated on a different day is a chart nobody can diff.
The two dates are the dates of the events, pinned below.

`history_points()` refuses a decrease with no cause, so the second point cannot be written without
the churn report that produced it. That is the constraint doing the work: the step-down is the most
credible point on this chart, and an unexplained one is indistinguishable from a bug in the
pipeline that produced it.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.churn import on_template_change  # noqa: E402
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.surface.history import HistoryPoint, history_points  # noqa: E402

BASE = REPO / ("fixtures/prescribed/"
               "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
BUMPED = REPO / "fixtures/synthetic/template-bumped__fy2029-30.xlsx"
RUNS = REPO / "reports/runs"
OUT = REPO / "reports/settled-history.jsonl"
CHURN_OUT = REPO / "reports/churn/fy2029-30.json"

# The dates of the EVENTS, pinned. Not `date.today()`.
RUN_AT = "2026-08-13"
BUMP_AT = "2026-08-16"


def main() -> int:
    run_dirs = sorted(d for d in RUNS.iterdir() if (d / "manifest.json").is_file()) \
        if RUNS.is_dir() else []
    if not run_dirs:
        print("no run on disk; `cdfc run <filing> --out reports/runs` first", file=sys.stderr)
        return 1
    run_dir = run_dirs[0]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    closure = manifest["closure"]
    admission = manifest["settledFraction"]["admissionState"]

    report = on_template_change(
        BASE, BUMPED, run_dir=run_dir, candidates=harvest(BASE).candidates,
    )

    points = history_points((
        HistoryPoint(at=RUN_AT, settled=closure["settled"], field_surface=closure["cellsTotal"],
                     admission=admission),
        HistoryPoint(at=BUMP_AT, settled=report.new_settled,
                     field_surface=report.field_surface, admission=admission,
                     cause=report.cause),
    ))

    # The sweep is PERSISTED, not recomputed per request. `GET /v1/churn` reads this file for the
    # same reason `GET /v1/rejections` reads the qualification artifact: an API that recomputes a
    # verdict is an API that can disagree with the artifact the attestation covers.
    CHURN_OUT.parent.mkdir(parents=True, exist_ok=True)
    CHURN_OUT.write_text(json.dumps({
        "sweptAt": BUMP_AT,
        "runId": manifest["run_id"],
        "oldTemplateSha256": report.old_template_sha256,
        "newTemplateSha256": report.new_template_sha256,
        "newTemplateName": BUMPED.name,
        "changedSheets": list(report.changed_sheets),
        "changedVocabularies": list(report.changed_vocabularies),
        "movedToProvisional": list(report.moved_to_provisional),
        "movedReason": report.moved_reason,
        "stillRunning": list(report.still_running),
        "numbersHidden": list(report.numbers_hidden),
        "numeratorDelta": report.numerator_delta,
        "oldSettled": report.old_settled,
        "newSettled": report.new_settled,
        "fieldSurface": report.field_surface,
        "granularity": report.granularity,
        "cause": report.cause,
    }, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(
            json.dumps({"at": p.at, "settled": p.settled, "fieldSurface": p.field_surface,
                        "admission": p.admission, "cause": p.cause,
                        "runId": manifest["run_id"] if p.at == RUN_AT else None},
                       sort_keys=True) + "\n"
            for p in points
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(REPO)} and {CHURN_OUT.relative_to(REPO)}")
    for p in points:
        arrow = " ▼" if p.cause else ""
        print(f"  {p.at}  {p.settled} / {p.field_surface}  {p.admission}{arrow}")
    print(f"  moved to PROVISIONAL: {len(report.moved_to_provisional)} "
          f"({', '.join(report.moved_to_provisional)})")
    print(f"  numerator delta: {report.numerator_delta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
