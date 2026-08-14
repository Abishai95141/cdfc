"""P10-B1 — the stored kill case, replayed on this filing's facts, in memory."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.runner import evaluate_one  # noqa: E402
from cdfc.qualify.observability import Observability  # noqa: E402
from cdfc.selfcheck.witness import (  # noqa: E402
    CoordinateWitnessError,
    FaultWitness,
    UndeclaredFaultClass,
    WitnessKeyUnresolved,
    apply,
    assert_claimed,
    image_of,
    observability,
    witnesses_from_campaign,
)
from cdfc.verdict import ItemState  # noqa: E402
from tests.selfcheck_fixtures import (  # noqa: E402
    FME,
    ROW_INSERTED,
    a_witness,
    image,
    killed_rows,
    population,
    witnesses,
)


def _w(**kw) -> FaultWitness:
    base = dict(
        predicate_id="P-TEST", target="1. Introduction!D11", new_value=1,
        fault_class="F01", mutant_sha256="0" * 64, operator_id="F01.a",
        recorded_at_cell="1. Introduction!D11", removes_formula=False,
    )
    return FaultWitness(**{**base, **kw})


# --- the target is a stable key, never a coordinate (NC-C05) ------------------------------


@pytest.mark.parametrize("bad", ["O7", "$O$7", "a1", "AAA1234"])
def test_w__target_is_a_stable_key_not_a_coordinate(bad: str) -> None:
    """A coordinate names no sheet, so it resolves against whichever sheet is asked."""
    with pytest.raises(CoordinateWitnessError):
        _w(target=bad)


def test_w__C05_a_coordinate_target_is_refused() -> None:
    """NC-C05's guard, un-parametrised so the sweep can name one node id and match it.

    The parametrised twin above covers four shapes; the sweep asserts an EXACT SET of node ids and
    a parametrised id carries its `[param]` suffix, so a guard named without one never matches and
    the entry would be recorded as caught on evidence nobody collected.
    """
    with pytest.raises(CoordinateWitnessError) as e:
        _w(target="O7")
    assert "rebinds" in str(e.value), "the refusal says what a coordinate does, not just that it is one"


def test_w__a_qualified_key_is_accepted() -> None:
    """The admission-side twin. Without it the refusal above is satisfied by refusing everything."""
    assert _w(target="3. Portfolio!O7").target == "3. Portfolio!O7"
    assert _w(target="3_portfolio.root.row[7].na").target.startswith("3_portfolio")


def test_w__an_unresolvable_key_refuses_rather_than_landing_somewhere_else() -> None:
    """NC-C05's mechanism, demonstrated on a filing whose rows have moved.

    `row-inserted__portfolio-r7.xlsx` is the same template with a row inserted. A witness whose
    stable key is not in that filing's induced key set is REFUSED — it is not applied at its
    recorded coordinate instead, because a coordinate that has moved names a different cell and a
    fault applied to a different cell proves nothing about the predicate.
    """
    img = image_of(ROW_INSERTED, FME)
    w = _w(target="a-key-this-filing-does-not-carry")
    with pytest.raises(WitnessKeyUnresolved) as e:
        observability(w, img)
    assert "recorded coordinate" in str(e.value)


# --- the fault class is a declared claim, not a post-hoc label (adversary F1) ---------------


def test_w__fault_class_is_a_declared_claim_not_a_post_hoc_label() -> None:
    assert_claimed(_w(fault_class="F01"), ("F01", "F05"))
    with pytest.raises(UndeclaredFaultClass) as e:
        assert_claimed(_w(fault_class="F13"), ("F01", "F05"))
    assert "code_sha256" in str(e.value), "the refusal says why the claim is dated, not just that"


def test_w__the_projection_refuses_a_class_the_predicate_never_claimed() -> None:
    """And COUNTS the refusals, because a silent skip is the coverage lie one level down."""
    img = image()
    h = witnesses_from_campaign(
        list(killed_rows()),
        key_of=img.key_of,
        claims={p.id: p.claims_fault_classes for p in population()},
        max_witnesses=3,
    )
    assert h.skipped_unclaimed, "no kill was credited outside a declared claim — verify that"
    for entry in h.skipped_unclaimed:
        pid, cls = entry.split(":")
        declared = {p.id: p.claims_fault_classes for p in population()}.get(pid)
        assert declared is None or cls not in declared


def test_w__a_pair_mutant_is_refused_not_half_applied() -> None:
    """One fault at two sites. Applying half of a coordinated pair is a different fault."""
    img = image()
    h = witnesses_from_campaign(
        [r for r in killed_rows() if len(r.get("edits") or ()) > 1],
        key_of=img.key_of,
        claims={p.id: p.claims_fault_classes for p in population()},
        max_witnesses=3,
    )
    assert h.by_predicate == {} or all(not v for v in h.by_predicate.values())
    assert h.skipped_multi_site, "the pair mutants were dropped without being counted"


# --- observability is decided by recalculation, three-valued -------------------------------


def test_w__observability_is_decided_by_recalculation() -> None:
    """A real stored kill case on the filing the campaign was run against IS observable."""
    obs, cells = observability(a_witness(), image())
    assert obs is Observability.OBSERVABLE
    assert cells, "an observable witness names the cells that distinguish it"


def test_w__a_witness_the_filing_already_satisfies_is_unobservable() -> None:
    """The honest inapplicability mechanism: applying the fault changes the artifact not at all.

    Constructed by writing back the value the filing already carries at that cell — so the mutant
    and the clean filing are the same document, and no predicate can be asked to tell them apart.
    """
    img = image()
    cell = ("1. Introduction", "D11")
    current = img.literals.get(cell)
    assert current is not None, "fixture drift: D11 no longer carries a literal"
    obs, cells = observability(_w(target=img.key_of[cell], new_value=current), img)
    assert obs is Observability.UNOBSERVABLE
    assert cells == ()


def test_w__notrun_cell_yields_INDETERMINATE_not_UNOBSERVABLE() -> None:
    """F18, and it is the difference between a fact about the filing and a fact about us.

    A witness whose recalculation traverses a cell this evaluator cannot compute, and which moves
    nothing visible, is INDETERMINATE. Folding it into UNOBSERVABLE would report our evaluator's
    coverage as the fault's invisibility — and because `O = G − U − I`, it RAISES `K/O`.
    """
    img = image()
    blocked = sorted(img.baseline.not_run)
    assert blocked, "fixture drift: this filing has no uncomputable cell, so F18 is untestable here"
    # A cell that FEEDS a not_run cell, set to the value it already holds: nothing moves, and the
    # cone traverses the blocked cell.
    target = None
    for cell, dependents in img.downstream.items():
        if any(d in img.baseline.not_run for d in dependents) and cell in img.literals:
            target = cell
            break
    assert target is not None, "fixture drift: no field cell feeds an uncomputable formula"
    w = _w(target=img.key_of[target], new_value=img.literals[target])
    obs, cells = observability(w, img)
    assert obs is Observability.INDETERMINATE_OBSERVABILITY
    assert cells, "the offending cells are NAMED, not merely counted"


# --- apply returns a copy ------------------------------------------------------------------


def test_w__apply_returns_a_copy() -> None:
    """By identity of the nested nodes, not by equality of the trees."""
    img = image()
    before = img.facts._trees["filing"]
    node = before["n_1_introduction"]
    mutant = apply(a_witness(), img)
    assert mutant is not img.facts
    assert before["n_1_introduction"] is node, "the received fact table was mutated in place"
    assert mutant._trees["filing"]["n_1_introduction"] is not node


def test_w__apply_reproduces_the_recorded_kill() -> None:
    """**The claim the whole layer rests on**, on one predicate, end to end.

    The witness was projected from a row of `killed.jsonl` whose `killed_by` names this predicate.
    Applying it to this filing's facts must make that predicate return `FAIL` — the P5 verdict
    model's own word for a kill, not a print statement.
    """
    from cdfc.measure.p5_run import fme_harvest
    from tests.selfcheck_fixtures import runtime

    img, schema, rt = image(), fme_harvest().schema, runtime()
    by_id = {p.id: p for p in population()}
    reproduced = 0
    for pid, ws in sorted(witnesses().items()):
        p = by_id.get(pid)
        if p is None or not ws:
            continue
        for w in ws:
            if observability(w, img)[0] is not Observability.OBSERVABLE:
                continue
            if evaluate_one(p, facts=apply(w, img), schema=schema, rt=rt).state is ItemState.FAIL:
                reproduced += 1
                break
        if reproduced >= 1:
            break
    assert reproduced >= 1, (
        "not one stored kill case reproduces on the filing the campaign was run against. Either "
        "the replay is wrong or the campaign's evidence is — and both are findings."
    )


# --- F19: the FILING's formulas, never the template's --------------------------------------


def test_w__observability_uses_filing_formulas() -> None:
    """F19, by AST over this package rather than by reading the docstring.

    `TEMPLATE` recomputes the blank's formula graph, which is what `TEMPLATE_DIFF` wants and what
    observability must never use: an F11 mutant — a formula replaced by a literal — recomputes
    IDENTICALLY under `TEMPLATE` and is therefore unobservable by construction, so the flagship
    fault class would leave `O` entirely.
    """
    pkg = REPO / "src" / "cdfc" / "selfcheck"
    sources = sorted(pkg.glob("*.py"))
    assert sources, "the selfcheck package is empty"
    seen = 0
    for path in sources:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "recalculate"):
                continue
            kw = {k.arg: k.value for k in node.keywords}
            assert "formula_source" in kw, f"{path.name}: recalculate() with no formula_source"
            value = kw["formula_source"]
            assert isinstance(value, ast.Constant) and value.value == "FILING", (
                f"{path.name}: observability must recalculate the FILING's own formulas. Under "
                "TEMPLATE an F11 mutant is unobservable by construction and the flagship class "
                "leaves O entirely."
            )
            seen += 1
    assert seen >= 2, "the AST scan found no recalculate() call to check — it is scanning nothing"


def test_w__the_digest_is_a_function_of_the_witness_and_nothing_else() -> None:
    """A cached replay can carry a duration; it cannot carry a digest it did not compute."""
    a, b = _w(), _w()
    assert a.digest() == b.digest()
    assert _w(new_value=2).digest() != a.digest()
    assert len(a.digest()) == 64
