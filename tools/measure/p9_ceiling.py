#!/usr/bin/env python
"""`docs/measurements/P9-template-diff-ceiling.md` — the ceiling, published BEFORE any delta.

    make ceiling

**Why the order matters.** `TEMPLATE_DIFF`'s settled-count delta on FME is near zero by
construction: its reachable cells are largely already bound by the 181 harvested cross-sheet
equalities and 35 sum identities, which read the same precedent ranges. A delta published without
its ceiling reads as a disappointment; published under the ceiling it reads as what it is — a
measurement of overlap, with the flagship's actual power (it is the only check in the design that
sees a formula replaced by a literal) sitting in a different column.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema.anchor import Anchor
from cdfc.ingest.reader_lxml import read  # noqa: E402
from cdfc.measure.geval import ARM2, gate_status, label  # noqa: E402
from cdfc.probes.degree import degree_map  # noqa: E402
from cdfc.probes.precedents import READINGS, build_precedent_map, ceiling  # noqa: E402
from cdfc.schema.styles_mask import Rule, build as build_mask  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
OUT_MD = REPO / "docs" / "measurements" / "P9-template-diff-ceiling.md"
OUT_JSON = REPO / "docs" / "measurements" / "p9-template-diff-ceiling.json"


def style_only_unlocked(blob: Path) -> set[tuple[str, str]]:
    """The unlocked set as `styles.xml` alone declares it — formula cells INCLUDED.

    `reader_lxml.unlocked_cells` and `styles_mask.build()` both drop formula cells, which is
    right for the DENOMINATOR (the field surface is what a filer may fill) and is what makes the
    difference below measurable at all.
    """
    import zipfile

    from cdfc.ingest.reader_lxml import _sheet_parts
    from cdfc.ingest.xmlsafe import fromstring

    m = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    ids = set(read(blob).styles.unlocked_style_ids)
    out: set[tuple[str, str]] = set()
    with zipfile.ZipFile(blob) as z:
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            for c in fromstring(z.read(part)).iter(f"{m}c"):
                s = c.get("s")
                if s is not None and s.isdigit() and int(s) in ids:
                    out.add((name, c.get("r") or ""))
    return out


def harvested_tolerance_audit() -> dict[str, object]:
    """The two open items the degree map surfaced in the HARVEST, both measured.

    (a) `harvest_classes/sum_identity.py` gives every `=SUM(range)` a `τ(n) = 5n` allowance
        without asking what the cells hold, so a count acquires a tolerance (NC-E08's defect).
    (b) `τ` is defined in `MILLI_USD_MILLION` — `HALF_ULP = 5` is half a unit of 10⁻³ USD
        Million — but the fact tree the runner evaluates (`facts.build.fact_set_for`) carries
        the workbook's own numbers UNSCALED. Only `facts.fact_table.build(..., money_keys=...)`
        scales, and the runner does not use it. So every emitted literal is 1,000× the
        tolerance it was written to express.
    """
    from cdfc.predicates.harvest import harvest

    res = harvest(FME)
    dm = degree_map(FME)
    with_tol = [c for c in res.candidates if getattr(c, "tolerance", None) is not None]
    on_counts: list[str] = []
    taus: list[int] = []
    for c in with_tol:
        cell = res.constructs.get(c.obligation_id)
        if cell is None:
            continue
        _kind, _parts, sheet, ref = cell
        a = dm.get(Anchor.cell(sheet, ref).render())
        if a is not None and a.degree == 0:
            on_counts.append(f"{c.id} at '{sheet}'!{ref} ({a.basis})")
        for token in c.expr.replace("(", " ").replace(")", " ").split():
            if token.isdigit():
                taus.append(int(token))
    return {
        "with_tolerance": len(with_tol),
        "on_degree_zero_cells": len(on_counts),
        "examples": sorted(on_counts),
        "max_tau_literal": max(taus) if taus else 0,
        "distinct_tau_literals": sorted(set(taus)),
    }


def main() -> int:
    maps = {r: build_precedent_map(FME, reading=r) for r in READINGS}
    pm = maps["transitive"]
    n, d = ceiling(pm)

    style_unlocked = style_only_unlocked(FME)
    formula_cells = {(f.sheet, f.ref) for f in read(FME).formulas}
    unbinding = sorted(Anchor.cell(s, r).render() for s, r in (style_unlocked & formula_cells))

    reach_binding: set[str] = set()
    for cell, cells in pm.in_field_surface.items():
        if cell not in set(unbinding):
            reach_binding |= cells

    dm = degree_map(FME)
    bases = Counter(a.basis for a in dm.values())
    tol = harvested_tolerance_audit()
    n_bad_tol, n_tol = tol["on_degree_zero_cells"], tol["with_tolerance"]
    bad_examples = tol["examples"]

    fs = build_mask(FME, Rule.V3)
    lab = label()

    L = [
        "# P9-B1 — `TEMPLATE_DIFF`'s ceiling, published before its delta",
        "",
        "**GENERATED by `tools/measure/p9_ceiling.py`. Run `make ceiling`.**",
        "",
        f"**G-EVAL: {gate_status()}.** Every number on this page is derived from `cdfc.calc`; "
        f"arm 2's oracle is {ARM2.oracle}, {ARM2.independence}."
        + (f" **{lab}**" if lab else ""),
        "",
        "## The headline",
        "",
        f"> **{n} of the {d} field-surface cells feed at least one formula the template declares.**",
        "",
        "Per sheet: "
        + " · ".join(f"{k} {v}" for k, v in sorted(pm.per_sheet().items(), key=lambda kv: -kv[1]))
        + ".",
        "",
        f"This is the **ceiling**, not the yield. Any claim that predicate #1 covers more than {n} "
        "cells is arithmetically impossible.",
        "",
        f"And the other half of the same measurement: **{d - n} field-surface cells feed no "
        "template formula at all.** They participate in no arithmetic relation the regulator "
        "encoded, so every recompute, carry and sum-identity check in the design is structurally "
        "blind to them, and only bound, membership and date predicates can reach them. That is a "
        "second, independent, measured argument that the residue set is non-empty — one that does "
        "not depend on the coordinated-misstatement construction at all.",
        "",
        "## What a precedent is — three readings, and the count does not distinguish them",
        "",
        "| reading | precedents | ceiling | formula cells binding ZERO field-surface cells |",
        "|---|---|---:|---:|",
    ]
    for r in READINGS:
        m = maps[r]
        cn, _cd = ceiling(m)
        gloss = {
            "lexical": "every reference in the formula text",
            "value": "minus arguments read for their SHAPE only (`ROW`, `ROWS`, …)",
            "transitive": "followed THROUGH intermediate formula cells to the filer's inputs",
        }[r]
        L.append(f"| `{r}` | {gloss} | {cn} | {len(m.unreachable)} |")

    L += [
        "",
        "**All three agree on the ceiling and disagree about everything else.** The ceiling is a "
        "union, so it saturates; the per-cell binding is where the reading is decided. Under a "
        f"direct reading **{len(maps['value'].unreachable)} of the {len(pm.formula_text)} formula "
        "cells bind nothing** and would be refused at G1 with `cells_bound = 0` — including "
        "`'1. Introduction'!D17`, the flagship's own worked example, whose direct precedents "
        "`D18:D20` are themselves formulas. Following through to `G54:G63` is not a widening: it "
        "is what `recalculate(..., formula_source=\"TEMPLATE\")` actually does, since it recomputes "
        "the whole graph over the filed inputs.",
        "",
        "**A count that agrees with a pin is evidence about the count.** Three readings returning "
        f"{n} is the reason to trust {n}; it is not a reason to think the reading did not matter.",
        "",
        "## The eight cells the relation can never reach — MEASURED, and it corrects the plan",
        "",
        f"`plan/05` §0.1 records **{len(unbinding)}** cells that are unlocked *and* formula-bearing "
        "and calls a fixture overwriting one of them *\"a strictly stronger demonstration and the "
        "one to show a reviewer\"*, on the grounds that a filer needs no zip edit and no "
        "adversarial intent — **Excel alone will do it**. The first half is right. The conclusion "
        "is not, and the fixture is what showed it:",
        "",
        "| overwritten cell | field surface | filing binds? | who catches it |",
        "|---|---:|---|---|",
        f"| `'3. Portfolio'!O7` (locked) | {fs.n_cells} → {fs.n_cells} | yes | **`TEMPLATE_DIFF`** |",
        f"| `'4. Investors'!N5` (unlocked) | {fs.n_cells} → {fs.n_cells + 1} | **no** | the template binder |",
        "",
        "The field surface is *unlocked ∧ non-formula*, so deleting a formula from an **unlocked** "
        "cell moves that cell **into** the field surface. The structural fingerprint carries the "
        "unlocked mask, so the fingerprint moves, and the run terminates at F3 with "
        "`invalid.template_unbound` — five steps before the relation executes.",
        "",
        "> **The claim that the fingerprint \"excludes formula content\" is false for exactly these "
        f"{len(unbinding)} cells.** It excludes formula *text*; it does not exclude formula "
        "*presence*. This is §0.5's own mechanism — a catch credited to the wrong layer — "
        "reappearing inside P9's headline fixture, and it points the other way: the eight cells a "
        "filer can overwrite **without stripping protection** are the eight the flagship can never "
        "see.",
        "",
        f"The cells: {', '.join('`' + c + '`' for c in unbinding)}.",
        "",
        f"**So the ceiling has two numbers and both are published.** {n} of {d} is the ceiling if "
        f"every formula cell could be checked. **{len(reach_binding)} of {d}** is the ceiling over "
        f"the {len(pm.formula_text) - len(unbinding)} formula cells whose overwrite still binds — "
        f"the flagship's real domain. The {n - len(reach_binding)} cells in the difference are "
        "reachable only through a formula cell whose overwrite ends the run before the relation "
        "runs.",
        "",
        "The remedy is named and is **not** taken here: making the fingerprint's mask "
        "style-only would restore all "
        f"{len(pm.formula_text)} cells to the relation, and it would move every template binding "
        "digest in the system. That is P5's binder, not P9's relation, and a phase that repairs "
        "another phase's load-bearing artifact as a side effect is how a build stops being "
        "re-derivable. Registered as NC-R11 with a guard, so it cannot be forgotten.",
        "",
        "## Degree — who gets a tolerance, and on whose authority",
        "",
        f"`τ(n) = 5n` units of `MILLI_USD_MILLION` for degree 1; **0** for everything else. Of the "
        f"{len(dm)} formula cells:",
        "",
        "| basis | cells | degree |",
        "|---|---:|---:|",
    ]
    for basis, count in sorted(bases.items(), key=lambda kv: -kv[1]):
        L.append(f"| `{basis}` | {count} | {1 if basis == 'MONEY_MARKER' else 0} |")

    L += [
        "",
        "Every assignment names the regulator's own words and the cell they are in — "
        "`'1. Introduction'!D17` is degree 0 on the authority of `'1. Introduction'!C17`, *\"Total "
        "No. of Schemes of the FME authorised by IFSCA\"*. **A person, and a scheme, is not a "
        "rounded quantity**: under a blanket `τ(n) = 5n` that cell could be wrong by fifteen "
        "schemes and pass.",
        "",
        "### TWO OPEN ITEMS IN THE HARVEST, dated 14 Aug 2026, found by building the degree map",
        "",
        "Neither is repaired here, and the reason is the same for both: changing a harvested "
        "predicate's tolerance changes its envelope, therefore its `code_sha256`, therefore the "
        "registry root, therefore P7's funnel and P8's FFR. A phase that silently moves another "
        "phase's published numbers is how a build stops being re-derivable. Both are published, "
        "dated, and guarded so they cannot be forgotten.",
        "",
        "**(a) `τ` is applied to counts.** "
        f"**{n_bad_tol} of the {n_tol}** harvested predicates that carry a tolerance carry it on a "
        "cell this degree map assigns degree 0. `harvest_classes/sum_identity.py` gives every "
        "`=SUM(range)` a `τ(n) = 5n` allowance without asking what the cells hold. That is NC-E08's "
        "defect standing in the harvest rather than in the probe layer.",
        "",
        "Examples: " + (", ".join(f"`{e}`" for e in bad_examples[:6]) or "none") + ".",
        "",
        "**(b) Every emitted tolerance is 1,000× the one it was written to express, and this is "
        "the larger of the two.** `HALF_ULP = 5` is half a unit of `MILLI_USD_MILLION`, i.e. "
        "**0.005 USD Million**. `facts/fact_table.py` scales money to that unit — but only when "
        "given `money_keys`, and the runner does not use it. The tree the runner evaluates is "
        "`facts/build.py::fact_set_for`, whose `_coerce` returns the workbook's own number "
        "unscaled and says so in its own docstring: *\"this builder does not know a cell's unit\"*. "
        "So the literal in every emitted expression is a tolerance in **whole USD Million**.",
        "",
        f"Measured: the largest tolerance literal in the harvested set is **{tol['max_tau_literal']}**, "
        f"and the distinct literals are {tol['distinct_tau_literals']}. Worked instance — `P-0114` "
        "over `'3. Portfolio'!O7`:",
        "",
        "```",
        "filing.n_3_portfolio.r7.co.v - (…twelve summands…) <= 60",
        "```",
        "",
        "On the reference clean filing that row's twelve summands are `1` each and the total is "
        "`12`. **The check passes for any total between −48 and 72.** The tolerance it was written "
        "to express is 0.06 USD Million.",
        "",
        "This is a measurement error correlated with the quantity being measured, in the direction "
        "that flatters us: an arithmetic mutant smaller than the over-wide tolerance is `WRONG`, "
        "observable, and **not killed** — so it depresses `K/O` rather than inflating it. The sign "
        "matters and it is the reason this is an open item rather than an emergency: the published "
        "kill rate is a LOWER bound on what these predicates can do, not an upper one.",
        "",
        "Guarded by `tests/negative/test_nc_probes.py::test_nc__R12a_the_tolerance_unit_mismatch_is_still_open`, "
        "which fails the day either side is repaired without the other — because a scaled fact "
        "tree with unscaled literals, or the reverse, is the same defect with the sign flipped.",
        "",
    ]
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps({
            "warrant": "MEASURED",
            "template_sha256": pm.template_sha256,
            "field_surface": d,
            "formula_cells": len(pm.formula_text),
            "ceiling_all_formula_cells": n,
            "ceiling_binding_formula_cells": len(reach_binding),
            "reachable_only_via_unbinding_cells": n - len(reach_binding),
            "per_sheet": pm.per_sheet(),
            "readings": {r: ceiling(maps[r])[0] for r in READINGS},
            "unreachable_by_reading": {r: len(maps[r].unreachable) for r in READINGS},
            "unlocked_formula_cells": unbinding,
            "degree_bases": dict(sorted(bases.items())),
            "harvested_tolerance": tol,
            "geval": {"status": gate_status(), "label": lab},
        }, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"ceiling {n} of {d} (all) · {len(reach_binding)} of {d} (binding only)")
    print(f"unlocked formula cells: {len(unbinding)} · harvested tolerance on counts: {n_bad_tol}/{n_tol}")
    print(f"wrote {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
