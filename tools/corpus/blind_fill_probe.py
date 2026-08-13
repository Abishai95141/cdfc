#!/usr/bin/env python
"""P8-B1 — the BLIND-FILL PROBE. Five fills by fresh instances, honestly labelled.

    make blind-probe

**This is a PROBE, not a corpus.** Its purpose is to FIND DEFECTS the seeded generator cannot —
`P-0009` was caught only because inputs varied — and it is not enough for `n_non_synthetic >= 30`,
so it licenses no tier. Every filing carries `person_a_kind: "model-instance"`, and
`severity.BLOCKING_REQUIRES_PERSON_A` refuses `BLOCKING` on that value however large `n` grows.

**What the fillers received:** the workbook's own field labels, the regulator's own data
validations and permitted vocabularies, and an instruction to fill correctly and plausibly.
**What they never received:** any predicate, any expression, any report, any gate output.

**Three weaknesses, stated where the number is produced.**
1. A sibling instance SHARES OUR WEIGHTS. It is nearer to *"we generated it"* than to *"the world
   produced it"*, which is why it cannot buy a tier.
2. **The regulation is not on disk** (D-P7-01), so a filler had the blank alone. "Filled correctly
   per the regulation" is therefore unverifiable; the fills are PLAUSIBLE, not certified correct.
3. Only the regulator-validated fields were offered — the rest take the same declared default the
   seeded generator uses. It is a PARTIAL blind fill and the manifest says so.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

S = pathlib.Path("/private/tmp/claude-501/-Users-abishaikc-Gift/"
                 "894fad3b-2031-4e06-855a-b18de2cd4288/scratchpad")
FME = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
OUT = REPO / "docs/measurements/P8-blind-probe.md"


def _row(ref: str) -> int:
    return int(re.search(r"(\d+)$", ref).group(1))


def expand(fill: dict, groups: list) -> dict[tuple[str, str], object]:
    """Cycle each filler's values across that column's rows. The expansion is MECHANICAL and
    declared; what the filler contributed is the value SET per field."""
    out: dict[tuple[str, str], object] = {}
    for g in groups:
        # **`uid`, NOT `sheet|column`.** The first version keyed on `sheet|column`, and the FIRST
        # FILLER FLAGGED IT: 454 distinct stacked fields collapse onto 103 such keys, so a JSON
        # object could carry only 103 of the 454 decisions and every stacked field sharing a
        # column would have been given the same values. A probe run that way would have produced
        # fires that look like predicate defects and are artefacts of this key.
        vals = fill.get(g.get("uid", ""))
        if not vals:
            continue
        for i, ref in enumerate(sorted(g["refs"], key=_row)):
            out[(g["sheet"], ref)] = vals[i % len(vals)]
    return out


def main() -> int:
    from cdfc.evaluate.celrt import CelRuntime
    from cdfc.facts.build import fact_set_for
    from cdfc.measure.p5_run import promote
    from cdfc.evaluate.runner import evaluate_one
    from cdfc.predicates.harvest import harvest
    from cdfc.predicates.host_fns import default_registry
    from cdfc.qualify.corpus._derive_foreign import value_table
    from cdfc.qualify.corpus._writer import strip_and_write, write_values
    from cdfc.qualify.corpus.template_computed import SOFFICE
    from cdfc.verdict import ItemState

    groups = [g for g in json.loads((S / "fill_groups.json").read_text()) if g.get("uid")]
    fills = sorted(S.glob("fill_0*.json"))
    if not fills:
        print("no fills present; run the blind-fill agents first", file=sys.stderr)
        return 2

    r = harvest(FME)
    hf = default_registry()
    rt = CelRuntime(profile_version="P8", host_fns=hf)
    predicates = [promote(c) for c in r.candidates]

    rows, fires = [], Counter()
    detail: dict[str, list[str]] = {}
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        for f in fills:
            inputs = expand(json.loads(f.read_text(encoding="utf-8")), groups)
            target = work / f"{f.stem}.xlsx"
            strip_and_write(FME, target, inputs)
            write_values(FME, target, value_table(SOFFICE, target))
            facts = fact_set_for(target, FME)
            fired = []
            for p in predicates:
                if evaluate_one(p, facts=facts, schema=r.schema, rt=rt).state is ItemState.FAIL:
                    fired.append(p.id)
                    fires[p.id] += 1
            rows.append((f.stem, len(inputs), len(fired)))
            detail[f.stem] = fired
            print(f"  {f.stem}: {len(inputs)} cells filled, {len(fired)} predicate(s) fired")
            target.unlink()

    OUT.write_text(_render(r, rows, fires, detail), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(REPO)}")
    return 0


def _render(r, rows, fires, detail) -> str:
    n = len(rows)
    L = [
        "# docs/measurements/P8-blind-probe.md — the blind-fill probe",
        "",
        "GENERATED by `tools/corpus/blind_fill_probe.py`. Do not hand-edit.",
        "",
        "**A PROBE, NOT A CORPUS.** Its purpose is to find defects the seeded generator cannot —",
        "`P-0009` was caught only because inputs varied. It licenses no tier: every filing carries",
        "`person_a_kind: \"model-instance\"`, and `severity.BLOCKING_REQUIRES_PERSON_A` refuses",
        "`BLOCKING` on that value however large `n` grows.",
        "",
        "**What the fillers received:** the workbook's own field labels, the regulator's own data",
        "validations and permitted vocabularies, and an instruction to fill correctly and plausibly.",
        "**What they never received:** any predicate, any expression, any report, any gate output.",
        "",
        "| filing | cells filled | predicates fired |",
        "|---|---:|---:|",
    ]
    for stem, cells, fired in rows:
        L.append(f"| `{stem}` | {cells} | {fired} |")
    L += ["", f"**{len(fires)} distinct predicate(s) fired across {n} filings.**", ""]
    if fires:
        L += ["| predicate | class | filings fired on |", "|---|---|---:|"]
        for pid, k in sorted(fires.items(), key=lambda x: -x[1]):
            L.append(f"| `{pid}` | {r.class_of.get(pid, '?')} | {k} / {n} |")
        L += ["", "**Each is a candidate defect and is triaged in `docs/HARVEST-DELTA.md` before",
              "any of them is dismissed.** A predicate firing on a plausibly-filled return is",
              "either wrong or is reading a rule the filler broke — and only reading it settles",
              "which.", ""]
    else:
        L += ["No predicate fired. That is corroboration and it is WEAK corroboration: five filings",
              f"is `n = {n}`, the fillers share our weights, and the regulation was not available to",
              "them (D-P7-01), so 'filled correctly' is unverified.", ""]
    L += [
        "## The three weaknesses, stated where the number is",
        "",
        "1. **A sibling instance shares our weights.** If our harvest misreads a construct, a",
        "   sibling reading the same blank can make the same misreading. That is why it cannot buy",
        "   a tier — F2 at the level of the mind rather than of the code.",
        "2. **The regulation is not on disk** (D-P7-01), so a filler had the blank alone. The fills",
        "   are PLAUSIBLE, not certified correct.",
        "3. **Only the regulator-validated fields were offered**; the rest take the same declared",
        "   default the seeded generator uses. A PARTIAL blind fill.",
        "",
    ]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
