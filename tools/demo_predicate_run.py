#!/usr/bin/env python
"""P4's value demonstration: harvested predicates catching a seeded fault on the real workbook.

**The claim being tested.** P4 says the regulator's own blank encodes relations that can be
extracted mechanically and run against a filing. This runs that end to end on FME `7d9a1960`:
harvest the blank, build a fact view from a filing, evaluate every cross-sheet-equality predicate,
and report what fired.

**The seeded fault is F13 — carry desync**, the class those 181 predicates exist for: a cross-sheet
carry TARGET is changed while its source is untouched. In a filing that is a coordinated
misstatement's simplest form.

**The admission-side control runs first and matters more than the finding.** An untouched filing
must produce ZERO findings. Without it, a predicate set that fires on everything would look like
detection.

    python tools/demo_predicate_run.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema.anchor import Anchor
from cdfc.evaluate.celrt import CelRuntime, Outcome  # noqa: E402
from cdfc.facts.view import FactView  # noqa: E402
from cdfc.predicates.harvest import _load_context, cel_path, harvest  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402

FME = REPO / "fixtures" / "prescribed" / (
    "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)


def fact_tree(blob: Path, *, perturb: dict[tuple[str, str], object] | None = None) -> dict:
    """The filing side of the fact model, in the convention the harvest emits against.

    A cell becomes `{v, __cell__}`. A blank NUMERIC cell is ABSENT rather than zero — that is
    F05's blank-and-zero distinction, which the taxonomy carries as two operators.
    """
    ctx = _load_context(blob)
    tree: dict = {}
    for sheet, values in ctx.cell_values.items():
        for ref, raw in values.items():
            if (sheet, ref) not in ctx.key_of:
                continue
            value: object = raw
            if perturb and (sheet, ref) in perturb:
                value = perturb[(sheet, ref)]
            try:
                value = int(float(str(value)))
            except (TypeError, ValueError):
                value = str(value)
            node = tree
            for seg in cel_path(sheet, ref).split("."):
                node = node.setdefault(seg, {})
            node["v"] = value
            node["__cell__"] = Anchor.cell(sheet, ref).render()
    return tree


def run(label: str, tree: dict, candidates, rt: CelRuntime) -> tuple[list[tuple[str, tuple[str, ...]]], list]:
    filing = FactView(tree, root="filing")
    template = FactView({}, root="template")
    findings: list[tuple[str, tuple[str, ...]]] = []
    passed: list = []
    counts = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0, "ERROR": 0}
    for c in candidates:
        applicable = rt.evaluate(rt.compile(c.applicable, slot="applicable"), filing=filing, template=template)
        if applicable.outcome is not Outcome.OK or applicable.value is not True:
            counts["NOT_RUN"] += 1
            continue
        result = rt.evaluate(rt.compile(c.expr, slot="expr"), filing=filing, template=template)
        if result.outcome is not Outcome.OK:
            counts["ERROR"] += 1
            continue
        if result.value is True:
            counts["PASS"] += 1
            passed.append(c)
            continue
        counts["FAIL"] += 1
        witness = rt.evaluate(rt.compile(c.witness, slot="witness"), filing=filing, template=template)
        findings.append((c.id, tuple(witness.value or ())))
    print(f"\n{label}")
    print(f"  ran {counts['PASS'] + counts['FAIL']}   "
          f"passed {counts['PASS']}   findings {counts['FAIL']}   "
          f"did not run {counts['NOT_RUN']}   errored {counts['ERROR']}")
    for pid, cells in findings[:6]:
        print(f"    {pid}  {' '.join(cells)}")
    if len(findings) > 6:
        print(f"    ... and {len(findings) - 6} more")
    return findings, passed


def main() -> int:
    res = harvest(FME)
    carries = [c for c in res.candidates if "carried across sheets" in c.rationale]
    rt = CelRuntime(profile_version="P4", host_fns=default_registry())

    print(f"harvested {len(res.candidates)} candidates from {FME.name}")
    print(f"  running the {len(carries)} cross-sheet carries — the class F13 exists for")

    clean = fact_tree(FME)
    baseline, passed = run("CONTROL — the filing untouched", clean, carries, rt)

    # Seed F13 on a carry the control ACTUALLY RAN. The first version picked the first carry with
    # an integer target and hit one whose source cell is blank in the blank — so `applicable` was
    # false, the predicate was NOT_RUN, and the seed landed where nothing was watching. The demo
    # reported "not detected", which was true of the seed and said nothing about the predicates.
    target = None
    for c in passed:
        cell = c.witness.split("[")[1].split(",")[0].strip()
        key = ".".join(cell.split(".")[:-1])
        node: object = clean
        for seg in key.split(".")[1:]:
            node = node.get(seg, {}) if isinstance(node, dict) else {}
        if isinstance(node, dict) and isinstance(node.get("v"), int):
            sheet, ref = str(node["__cell__"]).split("!")
            target = (sheet, ref, int(node["v"]))
            break
    if target is None:
        print("\nno carry that RAN on this workbook has an integer target; the seed cannot be "
              "placed where a predicate is watching, and the demonstration says so rather than "
              "seeding somewhere nothing runs and calling the miss a result")
        return 1

    sheet, ref, value = target
    print(f"\nseeding F13 at {sheet}!{ref}: {value} -> {value + 1} "
          "(the TARGET moves, the source does not)")
    seeded = fact_tree(FME, perturb={(sheet, ref): value + 1})
    found, _ = run("SEEDED — one carry target changed by one unit", seeded, carries, rt)

    print("\n---")
    print(f"control findings {len(baseline)}   seeded findings {len(found)}")
    if baseline:
        print("THE CONTROL FIRED. A predicate set that fires on an untouched filing is not "
              "detecting anything, and the seeded number below carries no information.")
        return 1
    if not found:
        print("The seeded fault was NOT detected. That is the finding, and it is reported "
              "rather than retried with an easier seed.")
        return 1
    print(f"The control produced zero findings and the seeded carry produced "
          f"{len(found)}, naming both ends. Every one of these predicates was derived from the "
          "regulator's own blank; not one of them cites a statute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
