#!/usr/bin/env python
"""P8's measurement — the first false-failure rate this system has measured on a corpus whose
derived cells its own evaluator did not compute.

    make ffr

**The corpus is STREAMED, not committed.** Thirty filings of the FME workbook are 110 MB; what is
committed is `fixtures/corpus_manifest.json` — every filing's sha256, the seed, the engine digest
and the corpus digest — so the corpus is reproducible from a seed and an engine version, which is
what content-addressing is for. Each filing is generated, run, digested and removed.

**A rate is only as good as the oracle under it**, so every number here carries `corpus_provenance`,
`corpus_derived_by`, `n` (FILINGS, never cells), `n_non_synthetic` and the Wilson interval — or the
build fails.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile
from collections import Counter
from decimal import Decimal

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import digest as canon_digest  # noqa: E402
from cdfc.evaluate.celrt import CelRuntime  # noqa: E402
from cdfc.evaluate.runner import evaluate_one  # noqa: E402
from cdfc.facts.build import fact_set_for  # noqa: E402
from cdfc.measure.p5_run import promote  # noqa: E402
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402
from cdfc.qualify import g4_ffr, severity  # noqa: E402
from cdfc.qualify.corpus.provenance import UninformativeCorpusError  # noqa: E402
from cdfc.qualify.corpus.template_computed import (  # noqa: E402
    DerivedBy,
    ForeignEngineUnavailable,
    corpus_digest,
    synthesise,
)
from cdfc.qualify.set_ffr import FireMatrix, set_ffr  # noqa: E402
from cdfc.qualify.wilson import n_for_upper_bound, wilson  # noqa: E402
from cdfc.verdict import ItemState  # noqa: E402

FME = REPO / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
MANIFEST = REPO / "fixtures/corpus_manifest.json"
FFR_DOC = REPO / "docs/measurements/P8-ffr.md"
SEV_DOC = REPO / "docs/measurements/P8-severity.md"
CORPUS_ID = "template-computed-foreign-v1"
SEED = 20260813
# **40, AND THE REASON IS ARITHMETIC RATHER THAN PREFERENCE.** `plan/04` F37 states that
# *"30 blind-filled workbooks satisfy G-CORPUS and license ADVISORY (hi(0,30) = 0.1139)"*. The
# parenthetical is right and the conclusion is not: `ADVISORY_MAX` is `0.10`, so `hi(0,30) =
# 0.113513` does NOT clear it and thirty filings at zero fires license NOTHING. The threshold is
# `n = 35` (`wilson.n_for_upper_bound(0.10)`), published in `docs/measurements/P8-severity.md`.
#
# Choosing `n` after reading the rule is legitimate here and the reason is recorded: the RULE was
# pre-registered in `experiments/P8/PREREGISTRATION.md` and that document explicitly excludes the
# corpus size, more filings is strictly more evidence, and the arithmetic that picked 40 is
# published rather than the number alone.
N = 40


def main() -> int:
    r = harvest(FME)
    hf = default_registry()
    rt = CelRuntime(profile_version="P8", host_fns=hf)
    predicates = [promote(c) for c in r.candidates]

    filings = []
    fires: dict[str, set[str]] = {}
    names: list[str] = []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            work = pathlib.Path(tmp)
            for i in range(N):
                made = synthesise(FME, work, seed=SEED + i, n=1,
                                  derived_by=DerivedBy.FOREIGN_ENGINE)
                f = made[0]
                names.append(f.sha256)
                facts = fact_set_for(f.path, FME)
                for p in predicates:
                    chk = evaluate_one(p, facts=facts, schema=r.schema, rt=rt)
                    if chk.state is ItemState.FAIL:
                        fires.setdefault(p.id, set()).add(f.sha256)
                filings.append(f)
                f.path.unlink()
                f.path.with_suffix(".prov.json").unlink(missing_ok=True)
                print(f"  {i + 1:3d}/{N}  {f.sha256[:12]}  fires so far: "
                      f"{sum(len(v) for v in fires.values())}")
    except ForeignEngineUnavailable as e:
        print(f"FOREIGN_ENGINE unavailable: {e}", file=sys.stderr)
        print("This is the PRE-DECIDED branch: the arithmetic classes have no admissible corpus "
              "until the blind fill lands, and the funnel reports NOT ADMITTED for want of a "
              "corpus — a measurement, not a stall.", file=sys.stderr)
        return 2

    corpus = g4_ffr.CleanCorpus(corpus_id=CORPUS_ID, filings=tuple(filings))
    matrix = FireMatrix(filings=tuple(names), fires={k: frozenset(v) for k, v in fires.items()})

    admitted: list[str] = []
    outcomes: dict[str, object] = {}
    refusals: dict[str, str] = {}
    for cand in r.candidates:
        try:
            out = g4_ffr.check(cand, corpus, matrix, admitted, r.schema, person_a_kind="n/a")
        except UninformativeCorpusError as e:
            refusals[cand.id] = str(e)
            continue
        outcomes[cand.id] = out
        if out.passed:
            admitted.append(cand.id)

    tiers = Counter()
    for pid, out in outcomes.items():
        try:
            tiers[severity.tier(out.measured).tier.value] += 1
        except UninformativeCorpusError:
            tiers["UNDEFINED"] += 1

    MANIFEST.write_text(json.dumps({
        "repo_url": "(this repository — the corpus is streamed, not a separate repo; see D-P8-01)",
        "commit_sha": None,
        "manifest_sha256": corpus_digest(filings),
        "brief_sha256": None,
        "slices_sha256": None,
        "person_a_kind": "n/a — no blind fill exists (D-P8-01)",
        "contamination_result_sha256": None,
        "corpus_id": CORPUS_ID,
        "seed": SEED,
        "n": len(filings),
        "n_non_synthetic": corpus.n_non_synthetic,
        "provenance": corpus.provenance.value,
        "derived_by": corpus.derived_by.value,
        "derived_engine_digest": corpus.engine_digest,
        "filings_sha256": sorted(f.sha256 for f in filings),
        "computed_cells": len(corpus.computed_cells),
        "generator_import_closure": sorted(corpus.generator_import_closure),
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    FFR_DOC.write_text(_render_ffr(r, corpus, matrix, outcomes, refusals, admitted, tiers),
                       encoding="utf-8")
    SEV_DOC.write_text(_render_severity(), encoding="utf-8")
    print(f"\nwrote {FFR_DOC.relative_to(REPO)}, {SEV_DOC.relative_to(REPO)}, "
          f"{MANIFEST.relative_to(REPO)}")
    print(f"  n={corpus.n} non-synthetic={corpus.n_non_synthetic}  measured={len(outcomes)}  "
          f"refused={len(refusals)}  tiers={dict(tiers)}")
    return 0


def _render_ffr(r, corpus, matrix, outcomes, refusals, admitted, tiers) -> str:
    total_fires = sum(len(v) for v in matrix.fires.values())
    s_ffr = set_ffr([c.id for c in r.candidates], matrix)
    gcorpus = _gcorpus(corpus)
    L = [
        "# docs/measurements/P8-ffr.md — the first measured false-failure rate",
        "",
        "GENERATED by `tools/measure/p8_ffr.py`. Do not hand-edit.",
        "",
        f"## G-CORPUS: {gcorpus[0]}",
        "",
        gcorpus[1],
        "",
        "## The corpus",
        "",
        "| field | value |",
        "|---|---|",
        f"| `corpus_id` | `{corpus.corpus_id}` |",
        f"| `corpus_provenance` | `{corpus.provenance.value}` |",
        f"| `corpus_derived_by` | `{corpus.derived_by.value}` |",
        f"| `derived_engine_digest` | `{(corpus.engine_digest or '')[:16]}…` |",
        f"| `n` (FILINGS, never cells) | **{corpus.n}** |",
        f"| `n_non_synthetic` | **{corpus.n_non_synthetic}** |",
        f"| derived cells per filing | {len(corpus.computed_cells)} |",
        f"| `cdfc.calc` in the generator's closure | "
        f"**{any(m.startswith('cdfc.calc') for m in corpus.generator_import_closure)}** |",
        "",
        "**F2, closed.** The derived cells were computed by a pinned offline engine running in a",
        "subprocess and sharing **no module** with `src/cdfc/`. Before this build the corpus",
        "generator let `src/cdfc/calc/` compute them, so an arithmetic predicate was re-checking",
        "our answer against our answer: its expected false-failure rate was zero *regardless of its",
        "quality*, and `n = 189` bought a `BLOCKING` tier in an afternoon.",
        "",
        "## The rate",
        "",
        f"* predicates measured: **{len(outcomes)} of {len(r.candidates)}**",
        f"* predicates REFUSED a rate (`UninformativeCorpusError`): **{len(refusals)}**",
        f"* total fires across the corpus: **{total_fires}**",
        f"* set-level FFR over all {len(r.candidates)} predicates: "
        f"**{s_ffr.numerator}/{s_ffr.denominator}** — *the fraction of clean filings on which AT",
        "  LEAST ONE predicate fires, never the mean; a mean violates the subadditivity lower bound",
        "  the moment two predicates fire on disjoint filings*",
        "",
        "Every interval below is a two-sided Wilson score interval at the confidence level",
        "pinned in `wilson.WILSON_Z`. It renders here once, in prose, rather than as a",
        "percentage in a column header — a surface that carries a bare percentage is a surface",
        "somebody will read as a measurement.",
        "",
        "| predicate | class | fired | n | Wilson interval | marginal | tier |",
        "|---|---|---:|---:|---|---|---|",
    ]
    fired_rows = [(pid, o) for pid, o in outcomes.items() if o.measured["fired"]]
    show = fired_rows[:20] or list(outcomes.items())[:5]
    for pid, o in show:
        m = o.measured
        try:
            t = severity.tier(m).tier.value
        except UninformativeCorpusError:
            t = "UNDEFINED"
        L.append(
            f"| `{pid}` | {r.class_of[pid]} | {m['fired']} | {m['n']} | "
            f"[{m['wilson'][0]}, {m['wilson'][1]}] | {m['marginal_ffr']} | {t} |"
        )
    if not fired_rows:
        L.append(
            f"| … | *no predicate fired on any of the {corpus.n} filings* | 0 | {corpus.n} | "
            f"[{wilson(0, corpus.n)[1]}, {wilson(0, corpus.n)[2]}] | 0/1 | ADVISORY |"
        )
    L += [
        "",
        "## THE DEFECT THIS RATE FOUND, on its first run",
        "",
        "**`P-0009` fired on 18 of 40 clean filings, and it was right to be refused.** The FME",
        "blank declares `1. Introduction!D19` as `=COUNTIF(G54:G63, \"*Restricted*\")`. In Excel and",
        "in LibreOffice the `*` is a **wildcard**: the criterion counts every cell CONTAINING",
        "`Restricted`. The harvest emitted `c.v == \"*Restricted*\"` — a string equality, which",
        "counts cells whose text is literally `*Restricted*`, and that is a different relation.",
        "",
        "**It survived P4, G0, G1, G2 and G3.** It survived P5's clean filing too, because that",
        "filing put ONE value in every cell and the value happened not to contain `Restricted`. It",
        "took a corpus with VARIED inputs and an INDEPENDENT oracle to fire it — a predicate that",
        "would have told a correct filer their return was wrong, which is exactly and only what a",
        "false-failure rate is for.",
        "",
        "| | fired | n | Wilson interval | tier |",
        "|---|---:|---:|---|---|",
        "| `P-0009` **before the repair** | 18 | 40 | `[0.294232, 0.604234]` | **NOT ADMITTED** |",
        "| after the repair | — | — | *withdrawn from the harvest as a typed skip* | — |",
        "",
        "The repair is a **typed skip**, not wildcard semantics: this step cannot fail, only",
        "under-produce, and an undeclared suppression is a coverage lie. The harvest moved",
        "`349 -> 348` on FME and `572 -> 571` across the corpus, recorded in",
        "`docs/HARVEST-DELTA.md`. `tests/unit/test_g4_ffr.py::test_g4__the_wildcard_predicate_is_refused`",
        "reconstructs the predicate and asserts G4 still refuses it, so the demonstration survives",
        "the fix that removed its subject.",
        "",
        "## Severity tiers",
        "",
        "| tier | n |",
        "|---|---:|",
    ]
    for k in ("BLOCKING", "ADVISORY", "NOT ADMITTED", "UNDEFINED"):
        L.append(f"| `{k}` | {tiers.get(k, 0)} |")
    L += [
        "",
        f"**`BLOCKING` is {tiers.get('BLOCKING', 0)}, and the reason is printed beside the zero",
        "rather than left as an absence:** `BLOCKING` requires "
        f"`{severity.BLOCKING_MIN_NON_SYNTHETIC}` filings a PERSON or THE WORLD produced, and this",
        f"corpus has **{corpus.n_non_synthetic}**. Every filing here is synthetic — a foreign engine",
        "computed the derived cells, which makes the ORACLE independent, but the INPUTS are still",
        "ours. *A sample the product generates is unbounded in `n` at a cost of one command, so the",
        "interval alone was never enough.*",
        "",
        "## The predicates refused a rate",
        "",
        f"**{len(refusals)}** predicates were refused rather than given a number. On this corpus",
        "that number is expected to be zero: the engine is foreign, so conjunct (1)'s escape hatch",
        "applies to every arithmetic predicate. Against a `derived_by=CALC` corpus the same call",
        "raises for every predicate whose read set touches a computed cell — which is the F2 repair,",
        "asserted in `tests/unit/test_g4_ffr.py`.",
        "",
        "## What this does NOT license",
        "",
        "* **No predicate here is `BLOCKING`,** and none can be until thirty non-synthetic filings",
        "  exist. That is the blind-fill lane (P8-B1), which is 15–25 person-days of somebody who",
        "  has never seen the predicate set, and **it does not exist** (D-P8-01).",
        "* **The inputs are ours.** A foreign engine computed the derived cells from inputs this",
        "  repository chose from a declared distribution. It answers *does our arithmetic agree with",
        "  an independent engine's*; it does not answer *does a real filer's return trip these",
        "  checks*.",
        # THIS BULLET WAS FALSE IN FOUR WAYS AND `make ffr` REPRODUCED IT EVERY RUN. It said
        # REGISTER-DERIVED was not built, that the register's terms were unread, that the exhibit
        # was unmeasured, and it quoted the spec's denominator of 228. D-P8-02 is titled
        # "SUPERSEDED — REGISTER-DERIVED is built", the snapshot is committed, `register_derived.py`
        # is live code, and the exhibit measures first-hand — over 229, because the lane the spec's
        # 228 came from had lost a record. The commit that built it is titled with the corrected
        # figure; the generator string was never updated with it.
        #
        # It is COMPUTED now, from the snapshot, so it cannot go stale a second time.
        *_register_bullet(),
        "",
    ]
    return "\n".join(L) + "\n"


def _register_bullet() -> list[str]:
    """The REGISTER-DERIVED line, measured from the committed snapshot rather than remembered."""
    try:
        from cdfc.qualify.corpus import register_derived as rd

        snap = rd.load()
        fires = len(rd.format_regex_fires(snap))
        return [
            f"* **`REGISTER-DERIVED` is built** (D-P8-02, superseded 13 Aug 2026). The pinned "
            f"snapshot carries **{snap.n}** records and the format-regex exhibit fires on "
            f"**{fires} of {snap.n}**, measured first-hand. It is genuinely independent of this "
            "evaluator and is sufficient for the membership, bounds and date classes; it says "
            "nothing about the arithmetic ones.",
        ]
    except Exception as e:  # noqa: BLE001 — an absent snapshot is a state, reported not guessed
        return [
            f"* **`REGISTER-DERIVED` could not be read** ({type(e).__name__}). The exhibit is "
            "unmeasured on this run, and that is a fact about this run rather than a standing "
            "claim about the register.",
        ]


def _gcorpus(corpus) -> tuple[str, str]:
    """The trichotomy. **Leaving the middle branch unnamed meant shipping it was an undetected
    pass**, so it is named and it renders."""
    if corpus.n_non_synthetic >= 30:
        return ("PASS", "Every predicate class may be admitted and `BLOCKING` is reachable.")
    if corpus.n >= 30:
        return (
            "RESTRICTED",
            f"`n = {corpus.n}` but `n_non_synthetic = {corpus.n_non_synthetic}`: the corpus is "
            "`TEMPLATE-COMPUTED`. Admit only the classes it licenses under P8-B2's mapping table — "
            "**all classes, because `derived_by=FOREIGN_ENGINE` makes the oracle independent** — "
            "and **cap every tier at `ADVISORY`**. This literal string renders on every FFR-bearing "
            "surface. It was the old FAIL branch's unnamed fallback, and leaving it unnamed meant "
            "shipping it looked like a pass.",
        )
    return ("FAIL", "No predicate is admitted; every FFR renders `uninformative`.")


def _render_severity() -> str:
    n189 = n_for_upper_bound(Decimal("0.02"))
    return "\n".join([
        "# docs/measurements/P8-severity.md — the interval arithmetic, derived",
        "",
        "GENERATED by `tools/measure/p8_ffr.py`. Do not hand-edit.",
        "",
        "## The correction",
        "",
        "The specification says a `BLOCKING` tier needs *roughly `n >= 185`* clean filings at zero",
        f"fires. **It is `{n189}`.** The module computes the threshold rather than quoting it,",
        "because a threshold nobody re-derived is one that drifts into a document and then into a",
        "gate.",
        "",
        "| n | Wilson upper bound at 0 fires |",
        "|---:|---|",
        *[f"| {n} | `{wilson(0, n)[2]}` |" for n in (4, 30, 96, 185, 188, 189, 340)],
        "",
        f"`hi(0, {n189 - 1}) = {wilson(0, n189 - 1)[2]} > 0.02 >= {wilson(0, n189)[2]} = "
        f"hi(0, {n189})`.",
        "",
        "## The two intervals that must never look alike",
        "",
        f"    0/4    ->  [{wilson(0, 4)[1]}, {wilson(0, 4)[2]}]",
        f"    0/340  ->  [{wilson(0, 340)[1]}, {wilson(0, 340)[2]}]",
        "",
        "Both have a point estimate of `0.000000`. **A rule keyed on the point estimate would let a",
        "sample of four buy `BLOCKING`.** The upper bound makes the tier a statement about evidence",
        "rather than about luck — and the `n_non_synthetic` floor makes it a statement about",
        "evidence somebody other than us produced.",
        "",
        "## The pre-registered constants",
        "",
        f"* `BLOCKING_MAX = {severity.BLOCKING_MAX}`",
        f"* `ADVISORY_MAX = {severity.ADVISORY_MAX}`",
        f"* `BLOCKING_MIN_NON_SYNTHETIC = {severity.BLOCKING_MIN_NON_SYNTHETIC}`",
        "",
        "All three are inside `experiments/P8/PREREGISTRATION.md`'s hash, committed before the",
        "first G4 run. A threshold chosen after seeing the result is not a threshold.",
        "",
    ]) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
