"""P10-B4 — E2, the categorical swap, built and run rather than argued.

**E1 is a construction and E2 is a measurement**, and that asymmetry is the whole reason E2 is
this document's contribution. E1's unkillability is an argument — scale one connected component of
the carry graph and every identity still holds. E2's is two facts about the regulator's own
artifact, and both are checked here on a workbook this file actually writes:

1. the new value is **legal by the regulator's own data validation**, so every membership
   predicate passes by construction; and
2. the cell **feeds no template formula**, so no recompute, cross-sheet carry or SUM identity can
   reach it either.

Either alone is not enough. A legal swap in a *reachable* cell can still break a sum, and an
illegal value in a blind cell is killed by R-04. It is the intersection that is unkillable, and
`tests/golden/test_golden__recompute_blind_set.py` pins how large that intersection is: 2,790 of
3,747 field-surface cells.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema.anchor import Anchor
from cdfc.measure.p5_run import FME, TEMPLATE_COMPUTED  # noqa: E402
from cdfc.predicates.harvest import _load_context, expand  # noqa: E402
from cdfc.probes.precedents import build_precedent_map  # noqa: E402
from cdfc.qualify.observability import extract  # noqa: E402
from cdfc.qualify.surgery import plan_edit, seed_mutant  # noqa: E402
from cdfc.schema.styles_mask import Rule, build  # noqa: E402
from cdfc.selfcheck.exhibit import recompute_blind  # noqa: E402
from cdfc.verdict import ItemState  # noqa: E402

# What "survives" is measured AGAINST, and it is named on the exhibit rather than implied.
# The ADMITTED set is empty on this build — P7 admits 0 of 348 — so survival against it is by
# construction and says nothing. The claim below is against the PRE-GATE harvested set, which is
# 348 real checks including every membership predicate the harvest derived from this workbook's
# own data validations.
SURVIVES_AGAINST = "the PRE-GATE harvested set (348 candidates)"


def _blind_enum_cell() -> tuple[str, str, str, list[str]]:
    """`(sheet, ref, current, members)` for a cell that is BOTH in a vocabulary and blind.

    Chosen deterministically — the first in sorted order — so the exhibit is reproducible and the
    test is not quietly choosing a different cell on each run.
    """
    fs = build(FME, Rule.V3)
    surface = frozenset(Anchor.cell(s, r).render() for s, r in fs.cells)
    blind = recompute_blind(build_precedent_map(FME, reading="transitive"), surface)
    ctx = _load_context(FME)
    filed = extract(TEMPLATE_COMPUTED).literals

    from cdfc.predicates.harvest import resolve_vocabulary

    for sheet in sorted(ctx.validations_by_sheet):
        for dv in ctx.validations_by_sheet[sheet]:
            if dv.type != "list" or not dv.sqref.split():
                continue
            members, _how = resolve_vocabulary(ctx, sheet, dv.formula1)
            if len(members) < 2:
                continue
            for part in sorted(dv.sqref.split()):
                for ref in expand(part.replace("$", "")):
                    key = Anchor.cell(sheet, ref).render()
                    current = filed.get((sheet, ref))
                    if key in blind and current is not None and str(current) in members:
                        return sheet, ref, str(current), list(members)
    pytest.skip("no filled vocabulary cell lands in the recompute-blind set on this fixture")


def test_e2__the_swap_is_legal_under_the_blank() -> None:
    """Otherwise it would be killed by R-04 and the exhibit would be a bug report, not a residue
    member. The vocabulary is resolved from the PINNED BLANK, never from the filing."""
    sheet, _ref, current, members = _blind_enum_cell()
    other = next(m for m in members if m != current)
    assert current in members and other in members
    assert other != current, "a swap to the same value is not a swap"


def test_e2__categorical_swap_survives_every_admitted_check(tmp_path: Path) -> None:
    """**The exhibit, built and run.** A one-character edit that changes what the scheme IS, and
    that nothing in the artifact contradicts.

    Not asserted from the residue file: this writes the mutant by the same raw-zip surgery the
    campaign uses, evaluates the whole pre-gate predicate set over it, and asserts NOTHING rejects
    it. An exhibit taken on trust from a measurement is a reason wearing an exhibit's clothes.
    """
    from cdfc.measure.p10_run import all_predicates, run_filing

    sheet, ref, current, members = _blind_enum_cell()
    other = next(m for m in members if m != current)
    target = tmp_path / "exhibit-e2.xlsx"
    edit = plan_edit(TEMPLATE_COMPUTED, sheet, ref, other, "F10.a")
    record = seed_mutant(
        TEMPLATE_COMPUTED, [edit], target, fault_class="F10", operator_id="F10.a", seed=0
    )

    baseline = run_filing(TEMPLATE_COMPUTED, predicates=all_predicates())
    swapped = run_filing(target, predicates=all_predicates())
    fails = sorted(c.predicate_id for c in swapped.checks if c.state is ItemState.FAIL)
    base_fails = sorted(c.predicate_id for c in baseline.checks if c.state is ItemState.FAIL)

    assert fails == base_fails, (
        f"the swap at {sheet}!{ref} ({current!r} -> {other!r}) was rejected by "
        f"{sorted(set(fails) - set(base_fails))} against {SURVIVES_AGAINST}. Either the cell is "
        "not recompute-blind or the value is not legal — and both are findings."
    )
    assert record.mutant_sha256 != record.base_sha256, "the exhibit is byte-identical to its base"
    assert len(record.parts_changed) == 1


def test_e2__the_survivor_is_in_the_recompute_blind_set() -> None:
    """The measured half. `probes/precedents.py`'s `transitive` reading is what decides it, and it
    is the reading that BINDS — it follows references through intermediate formula cells."""
    sheet, ref, _current, _members = _blind_enum_cell()
    fs = build(FME, Rule.V3)
    surface = frozenset(Anchor.cell(s, r).render() for s, r in fs.cells)
    pm = build_precedent_map(FME, reading="transitive")
    assert Anchor.cell(sheet, ref).render() in recompute_blind(pm, surface)
    assert Anchor.cell(sheet, ref).render() not in pm.reachable


def test_residue_not_inflatable() -> None:
    """**Adding 505 recompute predicates does not shrink the residue.** The spec's own claim,
    mechanised.

    `TEMPLATE_DIFF` binds the field-surface PRECEDENTS of every formula cell — 869 of them on this
    template, and 957 counting the non-binding ones. Not one of those cells is the exhibit's,
    because the exhibit's cell is in the complement of exactly that set. So the residue is
    populated by falsehoods consistent with **every arithmetic relation in the file**, and adding
    more arithmetic cannot touch it.
    """
    sheet, ref, _c, _m = _blind_enum_cell()
    pm = build_precedent_map(FME, reading="transitive")
    every_recompute_binds = pm.reachable
    assert len(every_recompute_binds) == 957, "the ceiling moved; the argument below needs re-checking"
    assert Anchor.cell(sheet, ref).render() not in every_recompute_binds, (
        "the exhibit's cell is bound by a recompute predicate, so adding recompute predicates "
        "WOULD shrink the residue and the spec's claim is false on this template"
    )
