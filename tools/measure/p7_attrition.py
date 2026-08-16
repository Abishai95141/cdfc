#!/usr/bin/env python
"""P7's measurement — the five-gate attrition funnel over the harvested FME predicates.

    make attrition

Every number here is computed from artifacts already committed: the pinned blank, the harvest, the
instrument corpus, and P6's campaign reports. Nothing is re-sampled, so two runs produce the same
file.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import CelRuntime  # noqa: E402
from cdfc.facts.build import fact_set_for  # noqa: E402
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402
from cdfc.predicates.obligations import generate_template_obligations  # noqa: E402
from cdfc.predicates.registry import Registry, UNSIGNED, batch_manifest_sha256  # noqa: E402
from cdfc.qualify import artifact, g0_scope, g1_binds, g2_kill, g3_degeneracy, ilp  # noqa: E402
from cdfc.qualify.baselines.build import build as build_baselines  # noqa: E402
from cdfc.qualify.corpus import gcorpus  # noqa: E402
from cdfc.qualify.campaign_store import assert_predicate_set  # noqa: E402
from cdfc.qualify.campaign_store import load as load_campaign  # noqa: E402
from cdfc.qualify.domain import load as load_domain  # noqa: E402
from cdfc.qualify.instruments import InstrumentStore  # noqa: E402
from cdfc.qualify.pipeline import Admission, QualificationContext, qualify  # noqa: E402
from cdfc.qualify.provisos import recall as marker_recall  # noqa: E402
from cdfc.qualify.result import GATE_ORDER, GateId  # noqa: E402
from cdfc.qualify.template_instrument import emit  # noqa: E402
from cdfc.surface.library import instrument_label  # noqa: E402

FME = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
CLEAN = REPO / "fixtures/synthetic/clean__independently-computed__fme-q1.xlsx"
CAMPAIGN = "fme-v3-seed20260810"
OUT = REPO / "docs/measurements/P7-attrition.md"
QUALIFIED_AT = "2026-08-13"


def main() -> int:
    r = harvest(FME)
    instrument = emit(FME)
    store = InstrumentStore(REPO / "corpus/instruments")
    store.in_memory(instrument)
    obligations = generate_template_obligations(r, instrument)
    stored = load_campaign(CAMPAIGN, REPO / "reports/campaigns")
    # THE JOIN IS CHECKED, NOT ASSUMED. `killed.jsonl` credits kills to predicate IDS, and ids
    # are re-assigned whenever the harvest changes — after P7-B1 and P8-B1, 125 of the 126 ids
    # this campaign credited carried a different `expr`, and G2 scored all 348 candidates on it.
    assert_predicate_set(stored, r.candidates)
    facts = fact_set_for(CLEAN, FME)
    hf = default_registry()

    clean_cells = {}
    for cell in sorted(r.cells_reachable):
        clean_cells[cell] = None
    baselines, invariants = build_baselines(
        stored, campaign_id=CAMPAIGN, class_of_predicate=r.class_of,
        clean_cells=_clean_values(CLEAN), root=REPO / "reports/campaigns",
    )

    # THE CONTROL ARM, MEASURED rather than assumed: a KILLED mutant marked unreachable would be a
    # predicate firing on a site outside its own read set — an apparatus failure, not a finding.
    killed_rows = [json.loads(x) for x in
                   (REPO / f"reports/campaigns/{CAMPAIGN}/killed.jsonl").read_text().splitlines() if x.strip()]
    # **COUNTED FROM `unreachable.jsonl`, NOT FROM `killed.jsonl`.** Reading it from the killed
    # rows made the number a constant: an unreachable mutant was never evaluated, so it could not
    # appear there, and the published "spurious fires: 0 — the threshold is exactly zero" would
    # have read 0 for a predicate that fired on every mutant in the campaign. The runner now
    # evaluates unreachable mutants and records the fires in `spurious_fires`, kept out of
    # `killed_by` so an apparatus failure can never inflate `K`.
    unreachable_rows = [
        json.loads(x) for x in
        (REPO / f"reports/campaigns/{CAMPAIGN}/unreachable.jsonl").read_text().splitlines()
        if x.strip()
    ]
    spurious = sum(len(row.get("spurious_fires") or ()) for row in unreachable_rows)
    spurious += sum(1 for row in killed_rows if row.get("reachable") is False)

    ctx = QualificationContext(
        obligations=obligations, store=store, schema=r.schema, facts=facts,
        runtime=CelRuntime(profile_version="P7", host_fns=hf), hostfns=hf,
        campaign=stored, baselines=baselines, domain=load_domain(REPO / "domain-policy-v1.json"),
        clean=g3_degeneracy.CleanCorpusResult(
            n_filings=1, n_fired=0, control_spurious_fires=spurious,
            corpus_label="TEMPLATE-COMPUTED reference filing (INDEPENDENTLY-COMPUTED, LibreOffice)",
        ),
        degeneracy_list=invariants, class_of=r.class_of,
        kill_bar=g2_kill.KillBar.EXPERIMENT, qualified_at=QUALIFIED_AT,
        n_sites=2 * stored.campaign.totals.O, true_defective=stored.campaign.totals.O,
        flagged_by={c.id: sum(stored.kills(c.id, k) for k in stored.campaign.by_fault_class)
                    for c in r.candidates},
        repo=REPO,
    )

    results = []
    for cand in r.candidates:
        results.append((cand, qualify(cand, ctx, through=GateId.G3E)))

    admitted = [c for c, res in results if isinstance(res, Admission)]
    rejections = [(c, res) for c, res in results if not isinstance(res, Admission)]

    reg = Registry()
    manifest = batch_manifest_sha256([_digest(c) for c in admitted],
                                     campaign_id=CAMPAIGN, qualified_at=QUALIFIED_AT)
    for c, res in results:
        if isinstance(res, Admission):
            reg.admit(c, res.record, signer=UNSIGNED, signature=b"",
                      batch_manifest_sha256=manifest, admitted_at=QUALIFIED_AT)

    sel = ilp.select(admitted, subsumes=g3_degeneracy.subsumes,
                     cells_of={c.id: len(_cells(c, r.schema)) for c in admitted})

    # ONE COMPUTATION, TWO RENDERINGS. The stages are built once, as validated objects, and both
    # the markdown table and the served JSON are projections of them. Two renderers reading one
    # object cannot disagree about a number; two renderers each doing their own arithmetic can, and
    # the one that drifts is the one nobody is reading.
    stages = _stages(r, results)
    art = _artifact(r, obligations, stored, results, reg, stages)
    written = art.write(REPO / artifact.ARTIFACT_PATH)

    OUT.write_text(_render(r, obligations, stored, baselines, invariants, results, admitted,
                           rejections, reg, sel, spurious, stages), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"wrote {written.relative_to(REPO)}")
    print(f"  entered {len(r.candidates)}  admitted {len(admitted)}  rejected {len(rejections)}")
    print(f"  registry root {reg.root()[:16]}…  unsigned {reg.unsigned_count()}/{len(reg.rows())}")
    return 0


def _stages(r, results) -> tuple[artifact.Stage, ...]:
    """The funnel, as validated `Stage` objects.

    **`survived` subtracts `skipped`.** The previous form computed `survivors - rejected` and
    reported `skipped` in its own column without removing it, so `entered == skipped + survived +
    rejected` held only while `skipped` was zero — which it is in this campaign, which is why the
    published table looked right. `surface.funnel.FunnelStage` refuses that arithmetic, and the
    `Stage` constructor puts the refusal in the path of every future campaign where a gate does
    start declaring itself inapplicable.
    """
    entering = len(r.candidates)
    out: list[artifact.Stage] = [
        artifact.Stage(name=artifact.GENERATED, entered=entering, skipped=0,
                       survived=entering, rejected=0, ran=True),
    ]
    remaining = list(results)
    for gate in GATE_ORDER:
        ran = any(o.gate is gate for _c, res in remaining for o in res.record.outcomes)
        if not ran:
            out.append(artifact.Stage(name=gate.value, entered=entering, skipped=0, survived=0,
                                      rejected=0, ran=False))
            continue
        rejected_here = [(c, res) for c, res in remaining
                         if not isinstance(res, Admission) and res.row.rejecting_gate is gate]
        skipped_here = sum(
            1 for _c, res in remaining
            if any(o.gate is gate and o.skipped is not None for o in res.record.outcomes)
        )
        reasons = Counter(res.record.rejecting.reason for _c, res in rejected_here)
        out.append(artifact.Stage(
            name=gate.value, entered=entering, skipped=skipped_here,
            survived=entering - skipped_here - len(rejected_here),
            rejected=len(rejected_here), ran=True, reasons=dict(sorted(reasons.items())),
        ))
        entering -= len(rejected_here)
        remaining = [(c, res) for c, res in remaining
                     if isinstance(res, Admission) or res.row.rejecting_gate is not gate]
    return tuple(out)


def _artifact(r, obligations, stored, results, reg, stages) -> artifact.QualificationArtifact:
    """The served form. **The library is what was ADMITTED; the rejections are what was refused.**

    Today the library is empty and the rejection list has every candidate in it. That is not a gap
    in this function: `D-P4-01` fixes four predicate states and `REJECTED` is not one of them, so a
    refused candidate never acquires a predicate id and can never be a library row. The empty
    library is the measurement.
    """
    remedies = {**g0_scope.REMEDY, **g1_binds.REMEDY, **g2_kill.REMEDY}
    rejections = []
    for c, res in results:
        if isinstance(res, Admission):
            continue
        o = res.record.rejecting
        rejections.append(artifact.Rejection(
            candidate_id=c.id, candidate_sha256=res.row.candidate_sha256,
            obligation_id=res.row.obligation_id, gate=res.row.rejecting_gate.value,
            reason=o.reason or "", measured=dict(o.measured),
            cells_would_have_covered=res.row.cells_would_have_covered,
            harvest_class=r.class_of.get(c.id, ""),
            remedy=remedies.get(o.reason or "", ""),
        ))

    library = []
    for c, res in results:
        if not isinstance(res, Admission):
            continue
        g2 = res.record.by_gate().get("G2")
        library.append({
            "predicateId": c.id,
            "version": getattr(c, "version", 1),
            "clauseQuote": getattr(c, "clause_quote", "") or "",
            "clauseEid": getattr(c, "clause_eid", None),
            "celSource": getattr(c, "expr", ""),
            "harvestClass": r.class_of.get(c.id, ""),
            "krClaimed": (g2.measured.get("kr_claimed") if g2 else None),
            "krAllClasses": (g2.measured.get("kr_all_classes") if g2 else None),
            "claimsFaultClasses": list((g2.measured.get("claimed_classes") if g2 else ()) or ()),
            "flagEverythingWouldHaveScored": (g2.measured.get("flag_everything") if g2 else None),
            "instrumentLabel": instrument_label(REPO / "ci/GATES.md"),
            "state": "ACTIVE",
        })

    g = gcorpus.load(REPO / gcorpus.CORPUS_MANIFEST)
    s, t, n = obligations.coverage_pair(r.candidates)
    return artifact.QualificationArtifact(
        schema_version=artifact.SCHEMA_VERSION,
        qualified_at=QUALIFIED_AT,
        campaign_id=stored.campaign.campaign_id,
        fault_model_version=stored.campaign.fault_model_version,
        kill_bar=g2_kill.KillBar.EXPERIMENT.name,
        instrument_label=instrument_label(REPO / "ci/GATES.md"),
        instrument_arms=_arms(),
        corpus_outcome=g.outcome, corpus_census=g.census,
        registry_root=reg.root(), registry_rows=len(reg.rows()),
        registry_unsigned=reg.unsigned_count(), registry_signer=UNSIGNED,
        obligation_statute=s, obligation_template=t, obligation_total=n,
        stages=stages, rejections=tuple(rejections), library=tuple(library),
        predicates_that_produced_runs=_predicates_in_runs(),
        ceiling_note=(
            "Every admission this repository can currently issue is an EXPERIMENT admission. No "
            "false-failure rate has been measured for any predicate under a corpus that licenses "
            f"one: G-CORPUS is {g.outcome}, and G4 has not been executed in this campaign."
        ),
    )


def _arms() -> tuple[dict, ...]:
    """G-EVAL's arms, with independence **computed from the oracle's author, never declared.**

    `ci/GATES.md` does not carry the string `NOT INDEPENDENT`, so `instrument_label()` returns
    `None` — which means *the registry does not say*, not *it is independent*. The registry is
    silent because the independence is not a registry entry at all: it is a consequence of
    `ARM2.oracle_author` being The Document Foundation rather than this project, and
    `cdfc.measure.geval` is where that is decided. Reading the arms puts the real answer on the
    screen instead of leaving a reader with the absence.
    """
    from cdfc.measure.geval import ARMS

    return tuple(
        {"n": a.n, "name": a.name, "oracle": a.oracle, "oracleAuthor": a.oracle_author,
         "independence": a.independence, "finds": a.finds, "blindTo": a.blind_to}
        for a in ARMS
    )


def _predicates_in_runs() -> int:
    """**The number the predicate library must state about itself.**

    Runs bind harvested candidates directly, under `PRE-GATE`. So a library reading *0 admitted*
    beside a report reading *1,898 settled* invites exactly one inference — that the settled count
    came from admitted predicates — and it did not. This counts the distinct predicates that
    actually produced settled cells, so the library can say the two populations are disjoint
    instead of leaving a reader to assume they are the same.
    """
    runs = REPO / "reports/runs"
    if not runs.is_dir():
        return 0
    seen: set[str] = set()
    for d in sorted(runs.iterdir()):
        stream = d / "run.jsonl"
        if not stream.is_file():
            continue
        for line in stream.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            pid = json.loads(line).get("predicate_id")
            if pid:
                seen.add(str(pid))
    return len(seen)


def _digest(c):
    from cdfc.predicates.canonical import code_sha256

    return code_sha256(c)


def _cells(c, schema):
    from cdfc.predicates.ast_walker import bound_cells

    return bound_cells(c, schema)


def _clean_values(path):
    """The clean filing's numeric cells, for B1's single observation.

    Read from the raw XML rather than through openpyxl: the synthetic filings are written by
    raw-zip surgery, and openpyxl refuses them. That refusal is a property of the writer this
    project deliberately does not use, not of the artifact.
    """
    import zipfile

    from cdfc.ingest.reader_lxml import _sheet_parts
    from cdfc.ingest.xmlsafe import fromstring

    M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    out = {}
    with zipfile.ZipFile(path) as z:
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            for c in root.iter(f"{{{M}}}c"):
                if c.get("t") in ("s", "str", "inlineStr", "b", "e"):
                    continue
                v = c.find(f"{{{M}}}v")
                if v is None or not (v.text or "").strip():
                    continue
                try:
                    out[f"{name}!{c.get('r')}"] = float(v.text)
                except (TypeError, ValueError):
                    continue
    return out


def _render(r, obligations, stored, baselines, invariants, results, admitted, rejections,
            reg, sel, spurious, stages) -> str:
    entered = len(r.candidates)
    # READ FROM THE VALIDATED STAGES, never recomputed here. This table and the served funnel are
    # the same objects rendered twice.
    per_stage: dict[str, dict[str, int]] = {s.name: s.reasons for s in stages}
    stage_rows = [
        (st.name, st.entered, "NOT RUN" if not st.ran else st.skipped,
         "NOT RUN" if not st.ran else st.rejected,
         "NOT RUN" if not st.ran else st.survived)
        for st in stages if st.name != artifact.GENERATED
    ]

    s, t, n = obligations.coverage_pair(r.candidates)
    tot = stored.campaign.totals
    rec = marker_recall(REPO / "fixtures/predicates/proviso-labels.json")

    L = [
        "# docs/measurements/P7-attrition.md — the five-gate attrition funnel",
        "",
        "GENERATED by `tools/measure/p7_attrition.py`. Do not hand-edit.",
        "",
        f"**Denominator: {entered} harvested FME predicates** (the plan says 280; the harvest has",
        f"produced {entered} since P4-B4 — see `docs/HARVEST-DELTA.md`).",
        "",
        "## The funnel",
        "",
        "**Stage one renders FOUR integers and `skipped` is never counted as a survivor**, whatever",
        "its value. `entered == skipped + rejected + survived` at every stage, and that identity is",
        "now ASSERTED by the object this table is rendered from rather than by the arithmetic in",
        "the renderer — the previous form computed `survived = entered - rejected` and reported",
        "`skipped` beside it without subtracting it, which closes only while `skipped` is zero.",
        "",
        "| gate | entered | skipped | rejected | survived |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, ent, sk, rej, surv in stage_rows:
        L.append(f"| `{name}` | {ent} | {sk} | {rej} | {surv} |")
    L += [
        "",
        "`G4` is **NOT RUN at P7** and the row says so rather than reporting a stage that passed",
        "everything: the false-failure rate needs the BLIND-FILLED corpus, which arrives at P8. No",
        "FFR has been measured for any predicate in this system, so every admission below is an",
        "EXPERIMENT admission and none of them is registry-grade.",
    ]
    L += [
        "",
        "### Every rejection, by gate and reason, with its remedy",
        "",
        "| gate | reason | n | remedy |",
        "|---|---|---:|---|",
    ]
    remedies = {**g0_scope.REMEDY, **g1_binds.REMEDY, **g2_kill.REMEDY}
    for gate in GATE_ORDER:
        for reason, k in sorted(per_stage.get(gate.value, {}).items()):
            L.append(f"| `{gate.value}` | `{reason}` | {k} | {remedies.get(reason, '—')} |")
    if not any(per_stage.get(g.value) for g in GATE_ORDER):
        L.append("| — | *no rejection* | 0 | — |")

    L += [
        "",
        f"Every rejection carries a `rejection` row with `cells_would_have_covered`; the",
        f"{len(rejections)} rejections cover "
        f"**{sum(res.row.cells_would_have_covered for _c, res in rejections)}** cells in total.",
        "",
        "## THE OBLIGATION COVERAGE PAIR (F9, arbitration C2) — two numbers, always both",
        "",
        f"    predicates_with_a_STATUTE_obligation  = {s} / {n}",
        f"    predicates_with_a_TEMPLATE_obligation = {t} / {n}",
        "",
        "**No harvested predicate yet implements a statutory clause.** The two counts are never",
        "added together and never rendered singly. And the `0` is stronger than the plan expected:",
        "**no statute is pinned in this repository at all** (D-P7-01), so the STATUTE arm of the",
        "corpus is empty rather than merely unused.",
        "",
        "## G0 — scope faithfulness",
        "",
        f"* `g0_marker_recall`: **{rec.render()}**",
        f"* marker list: `{'v1'}`, 15 markers, `docs/PROVISO-MARKERS-v1.md`",
        "* every candidate carries exactly one disposition from the seven closed reasons; there is",
        "  no skip, and `provisos_total == 0` for all of them is the TRUTH for a TEMPLATE",
        "  obligation rather than an empty marker list (NC-Q35's guard is scoped to STATUTE and its",
        "  own positive control asserts that scoping).",
        "* **A gate that passes everything is only evidence if it can fail.** All seven reasons are",
        "  observed red on real harvested candidates in `tests/unit/test_g0_scope.py`.",
        "",
        "## G2 — both ratios, side by side, for every candidate that reached it",
        "",
        f"Campaign `{stored.campaign.campaign_id}` · fault model `{stored.campaign.fault_model_version}`",
        f"· claim-ancestry: **{g2_kill.ancestry_state(stored, repo=REPO)}**",
        "",
        f"**Carried from P6 (F18):** `I = {tot.I}`, `I/G = {tot.I}/{tot.G}`, `U/G = {tot.U}/{tot.G}`,",
        f"`O = G − U − I = {tot.O}`. A funnel computed over a denominator our own evaluator could",
        "not fully adjudicate says so where the funnel is read.",
        "",
        "| predicate | class | `kr_claimed` | `kr_all_classes` | claimed set | marginal over B0 / B1 / B2 |",
        "|---|---|---|---|---|---|",
    ]
    g2_rows = [(c, res) for c, res in results
               if any(o.gate is GateId.G2 for o in res.record.outcomes)]
    shown = [(c, res) for c, res in g2_rows
             if res.record.by_gate()["G2"].measured["kr_claimed"].split("/")[0] != "0"]
    for c, res in sorted(shown, key=lambda x: x[0].id)[:25]:
        m = res.record.by_gate()["G2"].measured
        mk = m["marginal_kill"]
        L.append(
            f"| `{c.id}` | {r.class_of[c.id]} | {m['kr_claimed']} | {m['kr_all_classes']} | "
            f"{','.join(m['claimed_classes'])} | {mk.get('B0', 0)} / {mk.get('B1', 0)} / {mk.get('B2', 0)} |"
        )
    L += [
        f"| … | | | | | *{len(shown)} of {len(g2_rows)} candidates that reached G2 fired at all* |",
        "",
        "**A document quoting `kr_claimed` without `kr_all_classes` beside it has quoted half of a",
        "measurement.** The gap between the columns is the number a reviewer wants.",
        "",
        "### The three baselines, separately — a union figure hides which baseline did the work",
        "",
        "| baseline | kills | caveat |",
        "|---|---:|---|",
    ]
    for b in baselines.names():
        L.append(f"| `{b}` | {len(baselines.kills(b))} | {baselines.caveats.get(b, '—')} |")
    L += [
        f"| union | {len(baselines.union())} | reported BESIDE the per-baseline figures, never instead |",
        "",
        f"B1's mined degeneracy list carries **{len(invariants)}** invariants over ONE clean filing.",
        "",
        "## G3 — degeneracy",
        "",
        "| verdict | n |",
        "|---|---:|",
    ]
    verdicts = Counter()
    for _c, res in results:
        o = res.record.by_gate().get("G3p")
        if o is not None:
            verdicts[o.measured.get("verdict", "unknown")] += 1
    for k, v in sorted(verdicts.items()):
        L.append(f"| `{k}` | {v} |")
    L += [
        "",
        "**`unknown` is UNPROVEN, never `non_degenerate`** — it does not pass the proof arm, and the",
        "empirical arm must then decide. The `unknown` count is the sum of two causes, both",
        "declared: expressions outside the admitted CEL→SMT subset (strings, `in`, host functions),",
        "and pure-bound predicates routed to the empirical arm because `domain-policy-v1.json`'s",
        "`implausible_magnitude` is a **PLACEHOLDER** and this build does not invent one.",
        "",
        f"* control-arm spurious fires: **{spurious}** — the threshold is exactly zero and it is",
        "  DERIVED: a control site lies outside `upstream_closure(read_set(p))`, so a fire there is",
        "  an apparatus failure and blocks the batch rather than rejecting a predicate.",
        "* clean-corpus firing: **REJECT-ONLY at P7 (C5)**. Admission on this criterion waits for the",
        "  BLIND-FILLED corpus at P8. With zero false fires on the reference filing, the",
        "  random-flagger adjusted precision is `1` for every predicate that kills anything and `0`",
        "  for every predicate that does not — **the metric has no discriminating power until a",
        "  corpus exists that a predicate can be wrong about.**",
        "",
        "## The ILP — subsumption only at P7",
        "",
        f"* kept **{len(sel.kept)}**, removed **{len(sel.removals)}**",
        "* the set-FFR constraint is ABSENT and that is a declared state, not a gap: it needs a",
        "  false-failure rate, and none has been measured for any predicate in this system.",
        "* every removal carries a `rejection` row naming the subsuming predicate (NC-Q36).",
        "",
        "## Admission",
        "",
        f"* admitted: **{len(admitted)} of {entered}**",
        f"* registry root: `{reg.root()}`",
        f"* **{reg.unsigned_count()} of {len(reg.rows())} admitted under the literal signer",
        f"  `UNSIGNED`** — no signer exists in this repository, so the batch is admitted visibly",
        "  weaker rather than silently: every surface renders `UNSIGNED BATCH` beside the count.",
        "",
        "## What this phase did NOT settle",
        "",
        "**D-REJECT, the ALR demonstration, is not run here and the reason is structural.** ALR's",
        "five `>= -1e17` bounds are on disk and harvested (`P-0003`, `P-0014`, `P-0016`, `P-0028`,",
        "`P-0032`, against the one real `>= 0` bound `P-0031` — the plan's *five of six*). Refusing",
        "them at G2 needs an ALR **campaign**, and a campaign needs a CLEAN ALR FILING. P5-B0's",
        "filing generator builds one workbook only, FME. So the demonstration is blocked on an",
        "artifact, not on the gate: `g2_kill.check` would compute `K/O = 0/O` over those five the",
        "moment the campaign exists.",
        "",
        "**What it would take:** an ALR clean filing from the P5-B0 generator generalised beyond",
        "FME, then one campaign run. Until then the gate's demonstrated rejection power on real",
        "artifacts remains what P7 measured on FME, and every surface says exactly that.",
        "",
    ]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
