#!/usr/bin/env python
"""E2E — the whole product path, across THREE ingress formats and THREE regulators, in one run.

    make e2e

The claim under test is the product's own: *upload your exports in whatever shape they arrive.* Up
to today the ingress was `.xlsx` and nothing else, so "whatever shape" meant "whatever workbook".
This runs every ingress the system has against a real artefact from a different regulator and
prints one coherent result, so that a gap is visible as a gap rather than as an absence.

    IFSCA   .xlsx    a blank return -> field surface -> bind a filing -> check -> coverage
    EBA     .xlsx    12,925 PUBLISHED validation rules -> execute -> coverage over the rules
    FinCEN  .xsd     an XML schema  -> field surface from the regulator's own declarations

**Nothing here is a benchmark and no arm is scored against another.** The three regulators declare
different things in different formats; the point is that each is READ, and that what is not read is
named. Every figure printed carries both of its integers.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

FINCEN_XSD = REPO / "corpus/regulators/fincen_bsa_xml_2.0.xsd"
EBA_RULES = REPO / "corpus/rules/eba_validation_rules_4.3_2026_06_23.xlsx"
FME_FILING = REPO / "fixtures/synthetic/clean__template-computed__fme-q1.xlsx"


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def arm_ifsca() -> dict[str, object]:
    """IFSCA, `.xlsx`: a filing checked against its pinned blank, with a coverage declaration."""
    import subprocess

    # Driven through the CLI ON PURPOSE. `execute()` takes eleven wired arguments and the CLI is
    # what wires them, so calling it directly here would exercise a path no user takes and could
    # pass while the product was broken.
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "cdfc.cli", "run", str(FME_FILING)],
        capture_output=True, text=True, cwd=REPO,
        env={**__import__("os").environ, "PYTHONPATH": str(REPO / "src")},
    )
    dt = time.time() - t0
    if proc.returncode != 0:
        print(f"  ARM FAILED (exit {proc.returncode})\n{proc.stderr[-600:]}")
        return {"regulator": "IFSCA", "ingress": "xlsx", "failed": f"exit {proc.returncode}"}
    # MATCHED ON THE WHOLE LINE, not on a prefix. A prefix filter here printed "filing is
    # correct." — a fragment of the CLI's own disclaimer, *"It does not state that the filing is
    # correct."*, wrapped onto its own line. The summary asserted the exact opposite of the thing
    # the product is careful to never say.
    keep = ("filing ", "run ", "state ", "cellsTotal", "settled ", "NOT settled",
            "settled fraction", "liveness ")
    for line in proc.stdout.splitlines():
        t = line.strip()
        if any(t.startswith(k) for k in keep) and "is correct" not in t:
            print(f"  {t}")
    print(f"  wall clock    {dt:.2f}s")
    return {"regulator": "IFSCA", "ingress": "xlsx", "seconds": round(dt, 2), "exit": 0}


def arm_eba() -> dict[str, object]:
    """EBA, `.xlsx`: rules the REGULATOR wrote, executed, with a typed reason for each that is not."""
    from cdfc.pathm.coverage import declare

    if not EBA_RULES.is_file():
        print("  REFUSED: the pinned rule workbook is absent from this checkout.")
        return {"regulator": "EBA", "ingress": "xlsx-rules", "refused": "corpus_absent"}
    t0 = time.time()
    cov = declare(EBA_RULES)
    dt = time.time() - t0
    print(f"  published     {cov.published} rules at {cov.published_at}")
    print(f"  executed      {cov.executed} of {cov.published}")
    for reason, n in cov.not_executed:
        print(f"     {reason.value:32} {n:6} of {cov.published}")
    print(f"  data points   {cov.data_points} addressed by executed rules")
    print(f"  wall clock    {dt:.2f}s")
    return {"regulator": "EBA", "ingress": "xlsx-rules", "published": cov.published,
            "executed": cov.executed, "seconds": round(dt, 2)}


def arm_fincen() -> dict[str, object]:
    """FinCEN, `.xsd`: a field surface read from the regulator's own schema declarations."""
    from cdfc.schema.xsd import read

    if not FINCEN_XSD.is_file():
        print("  REFUSED: the pinned schema is absent from this checkout.")
        return {"regulator": "FinCEN", "ingress": "xsd", "refused": "corpus_absent"}
    t0 = time.time()
    s = read(FINCEN_XSD, schema_id="fincen-bsa-xml-2.0")
    dt = time.time() - t0
    c = s.counts()
    labelled = sum(1 for f in s.fields if f.label)
    print(f"  schema        {s.schema_id}   namespace {s.target_namespace}")
    print(f"  declared      {c['declared_total']} elements -> "
          f"{c['fields_total']} fields + {c['refused_total']} refused")
    print(f"  typed         {c['fields_total']} of {c['fields_total']}  "
          f"(TEXT {c.get('dtype_TEXT', 0)} · COUNT {c.get('dtype_COUNT', 0)} · "
          f"DATE {c.get('dtype_DATE', 0)})")
    print(f"  labelled      {labelled} of {c['fields_total']}   "
          f"(the regulator's own <xsd:documentation>)")
    print(f"  single-valued {c['fields_singleton']} of {c['fields_total']} — every field sits "
          "under a repeatable ancestor,")
    print("                so these are LIST PATHS, not addressable cells. Not comparable to a "
          "workbook's cells.")
    print(f"  refused       {c['refused_total']} of {c['declared_total']}, all "
          "`type_declares_no_unit` (xsd:decimal is a number, not a currency)")
    print(f"  vocabularies  {len(s.with_vocabulary())} of {c['fields_total']} — this schema "
          "declares NO enumerations;")
    print("                its code lists live in a separate namespace this checkout does not have.")
    print(f"  wall clock    {dt:.2f}s")
    return {"regulator": "FinCEN", "ingress": "xsd", "fields": c["fields_total"],
            "labelled": labelled, "refused": c["refused_total"], "seconds": round(dt, 2)}


def main() -> int:
    rows: list[dict[str, object]] = []
    rule("ARM 1 · IFSCA (GIFT City) — ingress .xlsx — check a filing, declare coverage")
    try:
        rows.append(arm_ifsca())
    except Exception as exc:  # a broken arm is reported, never swallowed
        print(f"  ARM FAILED: {type(exc).__name__}: {exc}")
        rows.append({"regulator": "IFSCA", "failed": f"{type(exc).__name__}: {exc}"})

    rule("ARM 2 · EBA — ingress .xlsx rule workbook — execute the regulator's published rules")
    try:
        rows.append(arm_eba())
    except Exception as exc:
        print(f"  ARM FAILED: {type(exc).__name__}: {exc}")
        rows.append({"regulator": "EBA", "failed": f"{type(exc).__name__}: {exc}"})

    rule("ARM 3 · FinCEN — ingress .xsd — field surface from the regulator's declarations")
    try:
        rows.append(arm_fincen())
    except Exception as exc:
        print(f"  ARM FAILED: {type(exc).__name__}: {exc}")
        rows.append({"regulator": "FinCEN", "failed": f"{type(exc).__name__}: {exc}"})

    rule("WHAT THIS RUN DOES NOT SHOW")
    print("""  * No filing was FILLED. The fill lane (A5) is not built, so 'autonomously populates
    the template' is not demonstrated by any arm here.
  * Only IFSCA is checked end to end. EBA executes rules against the publisher's declared
    scope, not against a filed instance; FinCEN produces a surface and stops.
  * No arm crosses regulators. Nothing here fuses a custodian feed with a trial balance.
  * No coverage number below is comparable to another: three regulators declare different
    things in different formats.""")
    failed = [r for r in rows if "failed" in r]
    print(f"\n  arms run {len(rows)} · arms failed {len(failed)}")
    (REPO / "reports").mkdir(exist_ok=True)
    (REPO / "reports/e2e-multiformat.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print("  wrote reports/e2e-multiformat.json")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
