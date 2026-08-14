"""P10-B2/B4 — `|RESIDUE|`, its five mandatory fields, and the two demonstrated survivors."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.selfcheck.adjudication import RULE_BASED, AdjudicationRecord, AdjudicationRow  # noqa: E402
from cdfc.selfcheck.exhibit import Exhibit, ExhibitError, recompute_blind  # noqa: E402
from cdfc.selfcheck.exhibit import render as render_exhibits  # noqa: E402
from cdfc.selfcheck.residue import (  # noqa: E402
    REQUIRED,
    ResidueError,
    compute_residue,
    not_inflatable,
    render,
)


def _mutant(mid: str, cls: str = "F10") -> dict:
    return {"mutant_sha256": mid, "fault_class": cls, "operator_id": f"{cls}.a",
            "sites": ["3. Portfolio!O7"]}


def _record(verdicts: dict[str, str]) -> AdjudicationRecord:
    return AdjudicationRecord(
        rows=tuple(
            AdjudicationRow(mutant_id=m, verdict=v, argument=f"[R-TEST] {v} at a cell.",
                            adjudicated_by=RULE_BASED, adjudicated_at="2026-08-14")
            for m, v in verdicts.items()
        ),
        fault_model_version="v3", filing_sha256="f" * 64, sample_seed=1,
        sample_fraction="20/100", seed_committed_at="2026-08-01",
    )


def _compute(verdicts, rejected, **kw):
    return compute_residue(
        [_mutant(m) for m in verdicts], _record(verdicts), rejected,
        **{"registry_root": "root-test", "n_admitted_predicates": 0,
           "n_admitted_relations": 0, "rejector_set": "PRE-GATE", **kw},
    )


def test_res__innocuous_leaves_the_denominator() -> None:
    """**They cannot be killed and must not be counted**, exactly as equivalent mutants must leave
    the code-mutation denominator."""
    r = _compute({"a": "WRONG", "b": "INNOCUOUS", "c": "WRONG"}, {})
    assert r.wrong_total == 2 and r.innocuous_total == 1
    assert set(r.survivors) == {"a", "c"}
    assert "b" not in r.survivors


def test_res__a_rejected_mutant_is_not_a_survivor() -> None:
    r = _compute({"a": "WRONG", "b": "WRONG"}, {"a": ["P-0001"]})
    assert r.survivors == ("b",) and r.wrong_total == 2


def test_res__an_empty_rejection_list_is_a_survivor() -> None:
    """Present-with-nothing and absent are the same fact here, and both must survive."""
    assert _compute({"a": "WRONG"}, {"a": []}).survivors == ("a",)
    assert _compute({"a": "WRONG"}, {}).survivors == ("a",)


def test_res__unadjudicated_mutant_raises() -> None:
    """Never defaulted to either value."""
    from cdfc.selfcheck.adjudication import AdjudicationError

    with pytest.raises(AdjudicationError):
        compute_residue(
            [_mutant("a"), _mutant("z")], _record({"a": "WRONG"}), {},
            registry_root="r", n_admitted_predicates=0, n_admitted_relations=0,
            rejector_set="PRE-GATE",
        )


def test_res__indeterminate_leaves_both_totals_and_is_counted_apart() -> None:
    """F18 again, one layer up: a mutant our evaluator could not adjudicate is neither WRONG nor
    INNOCUOUS, and folding it into either moves the number."""
    r = _compute({"a": "WRONG", "b": "WRONG"}, {}, unadjudicable=["b"])
    assert r.wrong_total == 1 and r.unadjudicable_total == 1 and r.survivors == ("a",)


@pytest.mark.parametrize("field", REQUIRED)
def test_res__renderer_refuses_without_all_five_fields(field: str) -> None:
    """NC-C07. `|RESIDUE| = 12` against an empty admitted set and against 280 predicates are
    utterly different claims, and a reader given only the number supplies the difference from
    their own optimism."""
    import dataclasses

    good = _compute({"a": "WRONG"}, {})
    assert "|RESIDUE| = 1" in render(good)
    blank = None if not isinstance(getattr(good, field), str) else ""
    with pytest.raises(ResidueError) as e:
        render(dataclasses.replace(good, **{field: blank}))
    assert field in str(e.value)


def test_res__C07_the_renderer_refuses_a_nameless_rejector_set() -> None:
    """NC-C07's guard, un-parametrised so the sweep can name one node id and match it.

    The parametrised twin above covers all five fields; the sweep asserts an EXACT SET of node ids
    and a parametrised id carries its `[param]` suffix, so a guard named without one never matches
    and the entry would be recorded as caught on evidence nobody collected.
    """
    import dataclasses

    good = _compute({"a": "WRONG"}, {}, rejector_set="ADMITTED")
    assert "|RESIDUE| = 1" in render(good)
    with pytest.raises(ResidueError) as e:
        render(dataclasses.replace(good, registry_root=""))
    assert "own optimism" in str(e.value), (
        "the refusal must say WHY a bare number is worse than no number: the reader supplies the "
        "missing rejector set themselves"
    )


def test_res__the_ceiling_label_travels_with_an_empty_rejector_set() -> None:
    """NC-C07's measured instance: on G-CORPUS's FAIL branch every WRONG mutant survives by
    construction, and that is a CEILING rather than a strong result."""
    r = _compute({"a": "WRONG", "b": "WRONG"}, {}, rejector_set="ADMITTED")
    text = render(r)
    assert "CEILING" in text and "by construction" in text
    assert "upper bound" in text
    pre = render(_compute({"a": "WRONG"}, {}, rejector_set="PRE-GATE"))
    assert "PRE-GATE" in pre and "may not be cited in a gate" in pre


def test_res__adding_predicates_cannot_grow_the_residue() -> None:
    """For any `S ⊆ S'`, `RESIDUE(S') ⊆ RESIDUE(S)`. Monotone by construction, asserted anyway."""
    verdicts = {chr(97 + i): "WRONG" for i in range(8)}
    small = _compute(verdicts, {"a": ["P-1"]})
    large = _compute(verdicts, {"a": ["P-1"], "b": ["P-2"], "c": ["P-1", "P-3"]})
    assert not_inflatable(small, large)
    assert not not_inflatable(large, small), "the property must be directional, not symmetric"


def test_res__the_survivors_are_reported_by_class_of_falsehood() -> None:
    """Step 6 of the procedure: `|RESIDUE|` AND, per survivor, the class it represents."""
    r = compute_residue(
        [_mutant("a", "F10"), _mutant("b", "F14"), _mutant("c", "F10")],
        _record({"a": "WRONG", "b": "WRONG", "c": "WRONG"}), {},
        registry_root="r", n_admitted_predicates=0, n_admitted_relations=0,
        rejector_set="PRE-GATE",
    )
    assert r.by_class == {"F10": 2, "F14": 1}
    assert "F10  2" in render(r)


# --- the exhibits -----------------------------------------------------------------------------


def _exhibit(**kw) -> Exhibit:
    base = dict(
        family="E2", title="categorical swap", construction="F10.a at Dropdown!I3",
        content_sha256="9" * 64, cells=("Dropdown!I3",),
        survives_against="the PRE-GATE harvested set (348 candidates)",
        why_unkillable="legal by the regulator's own validation; feeds no template formula",
    )
    return Exhibit(**{**base, **kw})


def test_ex__exhibits_render_as_exhibits_not_reasons() -> None:
    """A content hash and a construction, and **no reason code**.

    A reason code would put an exhibit in the same vocabulary as a finding about the filer's
    document, and it is not one: it is a statement about the limits of the instrument.
    """
    text = render_exhibits([_exhibit()])
    assert "sha256:" + "9" * 64 in text
    assert "CDFC_SYNTHETIC = true" in text
    assert "built by" in text and "F10.a at Dropdown!I3" in text
    for family in ("not_run.", "out_of_scope.", "indeterminate.", "no_predicate.", "error."):
        assert family not in text, f"a reason code ({family}) reached the exhibit block"


def test_ex__an_exhibit_without_a_content_hash_is_refused() -> None:
    with pytest.raises(ExhibitError) as e:
        _exhibit(content_sha256="")
    assert "cannot be opened" in str(e.value)


def test_ex__survives_is_meaningless_without_the_set_it_survived() -> None:
    """An exhibit that survives an EMPTY admitted set survives nothing."""
    with pytest.raises(ExhibitError) as e:
        _exhibit(survives_against="")
    assert "survives nothing" in str(e.value)


def test_ex__an_empty_exhibit_block_is_refused() -> None:
    with pytest.raises(ExhibitError) as e:
        render_exhibits([])
    assert "nobody can open" in str(e.value)


def test_ex__the_recompute_blind_set_is_the_complement_of_the_ceiling() -> None:
    """E2's landing ground, computed from the regulator's own formula graph rather than asserted."""

    class _PM:
        reachable = frozenset({"S!A1", "S!A2"})

    surface = frozenset({"S!A1", "S!A2", "S!A3", "S!A4"})
    blind = recompute_blind(_PM(), surface)
    assert blind == {"S!A3", "S!A4"}
    assert blind & _PM.reachable == frozenset(), "a cell cannot be both reachable and blind"
    assert blind | _PM.reachable == surface, "the two sets must partition the field surface"
