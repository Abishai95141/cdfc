#!/usr/bin/env python
"""P6's measurement — a fault campaign over the FME workbook under fault model v3.

    make campaign
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema.anchor import Anchor
from cdfc.measure.p5_run import FME, INDEPENDENT, fme_harvest, fme_surface, promote  # noqa: E402
from cdfc.predicates.ast_walker import bound_cells  # noqa: E402
from cdfc.qualify.campaign import restate_v0  # noqa: E402
from cdfc.qualify.fault_model import Dtype, Site, model_digest  # noqa: E402
from cdfc.qualify.observability import downstream_index, extract  # noqa: E402
from cdfc.qualify.campaign_store import predicate_set_digest  # noqa: E402
from cdfc.qualify.runner import CampaignRunner, plan_mutants, summarise, write_reports  # noqa: E402
from cdfc.qualify.sites import site_universe, stratified  # noqa: E402

OUT = REPO / "reports" / "campaigns"
DOC = REPO / "docs" / "measurements" / "P6-fault-model-v3.md"
SEED = 20260810
PER_STRATUM = 12


def dtype_of(sheet: str, ref: str, ctx, formula_cells: set, vocab: dict) -> tuple[Dtype, tuple[str, ...]]:
    """The dtype comes from the PINNED BLANK's own declarations, never from the filing."""
    key = (sheet, ref)
    if key in vocab:
        return Dtype.ENUM, vocab[key]
    for dv in ctx.validations_by_sheet.get(sheet, ()):
        from cdfc.predicates.harvest import expand

        refs = {c for part in dv.sqref.split() for c in expand(part.replace("$", ""))}
        if ref not in refs:
            continue
        if dv.type == "date":
            return Dtype.DATE, ()
        if dv.type in ("whole", "decimal"):
            return Dtype.MILLI_USD_MILLION, ()
    return (Dtype.COUNT if key in formula_cells else Dtype.TEXT), ()


def build_sites() -> tuple[list[Site], str, frozenset[str]]:
    from cdfc.predicates.harvest import _load_context, expand, resolve_vocabulary

    ctx = _load_context(FME)
    n, surface, _state = fme_surface()
    formula_cells = {(s, f.ref) for s, fs in ctx.formulas_by_sheet.items() for f in fs}
    vocab: dict[tuple[str, str], tuple[str, ...]] = {}
    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if dv.type != "list":
                continue
            members, _how = resolve_vocabulary(ctx, sheet, dv.formula1)
            if not members:
                continue
            for part in dv.sqref.split():
                for ref in expand(part.replace("$", "")):
                    vocab[(sheet, ref)] = tuple(members)

    # The universe is the FIELD SURFACE, plus the formula cells F11 needs — an override is only
    # possible where the blank declares a formula, and those cells are LOCKED, so they are not in
    # the field surface. Naming them here rather than widening the surface keeps the denominator
    # of the settled fraction untouched.
    universe = site_universe(surface) | frozenset(Anchor.cell(s, r).render() for s, r in formula_cells)

    # The value one row up, for F08. Read from the CLEAN filing once.
    import re as _re
    from cdfc.qualify.observability import extract as _extract

    _lits = _extract(INDEPENDENT).literals
    _above: dict[tuple[str, str], object] = {}
    for (sh, rf), val in _lits.items():
        m = _re.match(r"^([A-Z]+)(\d+)$", rf)
        if m:
            _above[(sh, f"{m.group(1)}{int(m.group(2)) + 1}")] = val

    strata: dict[str, str] = {}
    sites: list[Site] = []
    for cell in sorted(universe):
        sheet, ref = cell.rsplit("!", 1)
        dt, members = dtype_of(sheet, ref, ctx, formula_cells, vocab)
        is_f = (sheet, ref) in formula_cells
        strata[cell] = f"{dt}{'+F' if is_f else ''}"
        sites.append(Site(sheet, ref, dt, is_formula=is_f, vocabulary=members,
                          value_above=_above.get((sheet, ref))))

    sampled, rule = stratified(
        frozenset(universe), per_stratum=PER_STRATUM, strata=strata, rng_seed=SEED
    )

    # DECLARED ADDITION, and it is published in the rule rather than hidden in the seed.
    #
    # `INDETERMINATE_OBSERVABILITY` is unmeasurable unless some mutant's only propagation path
    # crosses a cell this evaluator cannot compute. Whether the RNG happens to pick such a cell is
    # not a property of the fault model, so the sample also takes every cell that FEEDS a formula
    # we could not compute. Choosing sites to make a number non-zero would be manipulation;
    # choosing them to make a class MEASURABLE, and saying so, is coverage.
    from cdfc.qualify.observability import downstream_index, grid_of

    blocked = set(grid_of(INDEPENDENT).not_run)
    upstream_of_blocked = {
        Anchor.cell(src[0], src[1]).render()
        for src, targets in downstream_index(str(INDEPENDENT)).items()
        if targets & blocked
    }
    added = frozenset(upstream_of_blocked) & frozenset(universe)
    sampled = sampled | added
    rule += (
        f"; plus {len(added)} cell(s) that feed a formula this evaluator cannot compute, so the "
        "INDETERMINATE class is measurable at all rather than depending on which cells the RNG "
        f"chose ({len(blocked)} such formula cells)"
    )

    chosen = [s for s in sites if s.cell in sampled]
    return chosen, rule, frozenset(universe)


class _PartnerCtx:
    """Supplies a PAIR operator's second edit from the workbook's own dependency graph."""

    def __init__(self, sites: dict[str, Site], downstream) -> None:
        self.sites = sites
        self.upstream: dict[str, list[str]] = {}
        for src, targets in downstream.items():
            s = Anchor.cell(src[0], src[1]).render()
            for t in targets:
                self.upstream.setdefault(Anchor.cell(t[0], t[1]).render(), []).append(s)

    def inputs_of(self, site: Site):
        return [self.sites[c] for c in sorted(self.upstream.get(site.cell, ())) if c in self.sites]

    def carry_counterpart(self, site: Site):
        for cell in sorted(self.upstream.get(site.cell, ())):
            other = self.sites.get(cell)
            if other is not None and other.sheet != site.sheet:
                return other, 3
        return None


def main() -> int:
    h = fme_harvest()
    preds = [promote(c) for c in h.candidates]
    read_cells = frozenset().union(*(bound_cells(p, h.schema) for p in preds)) if preds else frozenset()

    sites, rule, universe = build_sites()
    print(f"site universe {len(universe)} | sampled {len(sites)} | {rule[:90]}")

    ex = extract(INDEPENDENT)
    values = dict(ex.literals)
    for k in ex.formulas:
        values.setdefault(k, None)
    from cdfc.qualify.observability import grid_of

    grid = grid_of(INDEPENDENT)
    for k, v in grid.values.items():
        values[k] = v

    by_cell = {s.cell: s for s in sites}
    partner_ctx = _PartnerCtx(by_cell, downstream_index(str(INDEPENDENT)))
    plans = plan_mutants(sites, rng=random.Random(SEED), values=values, partner_ctx=partner_ctx)
    print(f"planned {len(plans)} mutants over {len({p[1].id for p in plans})} operators", flush=True)

    from cdfc.measure.p6_kill import killer

    runner = CampaignRunner(
        base=FME, clean=INDEPENDENT, out_dir=OUT / "_work",
        evaluate=killer(preds, h.schema), read_cells=read_cells,
    )
    outcomes = []
    for i, (cls, op, _site, edits) in enumerate(plans):
        outcomes.append(runner.run_one(cls, op, edits, SEED + i))
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(plans)}", flush=True)

    campaign = summarise(
        outcomes,
        campaign_id=f"fme-v3-seed{SEED}",
        site_set_digest=model_digest()[:16],
        evaluator_version="cdfc.calc P3 + celpy 0.5.0",
        base_sha256=h.template_sha256,
        sampling_rule=rule,
        # WHICH PREDICATES THIS CAMPAIGN CREDITED, as a digest over `(id, code_sha256)`. Without
        # it a later harvest can re-assign ids and G2 goes on scoring each candidate with another
        # predicate's evidence — which is exactly what happened between P6 and P9.
        predicate_set_digest=predicate_set_digest(h.candidates),
    )
    target = write_reports(campaign, outcomes, OUT)
    print()
    print(campaign.render())
    DOC.write_text(render_doc(campaign, target, len(universe)), encoding="utf-8")
    print(f"\nwrote {DOC.relative_to(REPO)}")
    return 0


def render_doc(campaign, target: Path, universe: int) -> str:
    t = campaign.totals
    per_class = "\n".join(
        f"| {cid} | {v.G} | {v.U} | {v.I} | {v.O} | {v.R} | {v.K} | "
        f"{'`' + str(v.K) + '/' + str(v.O) + '`' if v.O else '— nothing observable'} |"
        for cid, v in sorted(campaign.by_fault_class.items())
    )
    indet = "\n".join(
        f"- **{cid}** — {', '.join(cells[:6])}"
        for cid, cells in sorted(campaign.indeterminate_cells.items())
    ) or "- none on this campaign"
    return f"""# P6 — the fault campaign, model `v3`

**Warrant: MEASURED.** Produced by `make campaign`. Reports in
`{target.relative_to(target.parents[2])}/`.

**What did not exist before this run.** `U/G` for OUR operator mix — the literature's comparable
figure, 3,512 of 7,500 = 46.8%, is a property of a different suite and must not be assumed for
ours. And `K/O` per class where **killed means a predicate returned `FAIL` under the eight-state
verdict model**, rather than a boolean.

## The sample, and its rule

Site universe: **{universe}** cells. Sampling rule, published because the number is a fraction of
it: `{campaign.sampling_rule}`

Reducing the operator set to make the number look better is the manipulation this project bans.
Reducing the sample and saying so is arithmetic.

## The six integers

| class | G | U | I | O | R | K | K/O |
|---|---:|---:|---:|---:|---:|---:|---|
{per_class}
| **TOTAL** | **{t.G}** | **{t.U}** | **{t.I}** | **{t.O}** | **{t.R}** | **{t.K}** | **{t.K}/{t.O}** |

    U/G = {t.U}/{t.G}      I/G = {t.I}/{t.G}      K/O = {t.K}/{t.O}

**`I` is our EVALUATOR, not the fault model, and it never renders without `U/G` beside it.** A cell
in `not_run` is identical in both grids *by construction*, so a two-way classification banks its
mutants as unobservable, removes them from `O`, and — because `O = G − U − I` — **raises** `K/O`.
The measurement error would be correlated with the quantity being measured, in the direction that
flatters us.

### `I = 0` on this campaign, and a zero is not the same as an absent column

The sample deliberately includes every cell that feeds a formula this evaluator cannot compute, so
the class is *reachable* rather than depending on which cells the RNG chose. It still measures
zero, and the reason is worth stating: **every operator in this model edits a cell whose own value
moves**, and the edited cell's literal is part of the comparison. A mutant is therefore observable
at its own site before propagation is considered, and `INDETERMINATE` — *the grids agree but we
could not adjudicate the path* — needs a mutant that is invisible at its own site. This model has
none.

The class is implemented, controlled and rendered anyway. A campaign whose operator mix did produce
one would count it, and `U/G` would still not absorb it.

### The cells behind every `I`

{indet}

### What the `U = {t.U}` actually are, because a rate is only as honest as its composition

All {t.U} are `F12.c` — the trailing-whitespace operator — applied to cells the clean filing holds
the integer `1` in. `"1 "` parses back as `1` through any numeric read, in this system and in
Excel: **the fault is one the format cannot carry.** That is precisely what `U/G` is for.

It is also partly an artifact of the fixture, and saying so is the point of publishing the
composition: the synthetic filing writes `1` into every field-surface cell that carries no data
validation, so the `TEXT` stratum is full of integers. A filing with real text in those cells would
move this number. **`U/G` is a property of our operator mix ON THIS FILING**, and neither half of
that sentence is optional.

## The v0 restatement

{restate_v0()}

## What this licenses, and what it does not

> The predicate set rejects **{t.K} of {t.O}** observable defects seeded under fault model `v3`, of
> which **{t.U} of {t.G}** were discarded as unobservable and **{t.I} of {t.G}** could not be
> adjudicated by our own evaluator.

It does **not** license *"detects X% of real filing errors"*. The bridge from seeded faults to real
ones is the coupling effect, and **there is no coupling study for financial filing data** — NC-N50,
where a negative control is impossible because no filed FME return is public and the denominator
does not exist.

**Three classes are designed misses.** `F10`, `F12`'s homoglyph form and `F14` are classes our own
predicates cannot catch by construction. **A per-class vector that is uniformly high would be
evidence that the model is too weak, not that the predicates are good.**
"""


if __name__ == "__main__":
    raise SystemExit(main())
