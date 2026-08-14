"""P10-B3 — the adjudication record, its refusals, and Cohen's κ."""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.selfcheck.adjudication import (  # noqa: E402
    RECONCILIATION_TRIGGER,
    RULE_BASED,
    AdjudicationError,
    AdjudicationRecord,
    AdjudicationRow,
    cohens_kappa,
    render_kappa,
)


def _row(mid: str = "a" * 64, **kw) -> AdjudicationRow:
    base = dict(
        mutant_id=mid, verdict="WRONG", argument="[R-QUANTITY] it changes a number.",
        adjudicated_by=RULE_BASED, adjudicated_at="2026-08-14", round=1,
    )
    return AdjudicationRow(**{**base, **kw})


def _record(rows, **kw) -> AdjudicationRecord:
    base = dict(
        rows=tuple(rows), fault_model_version="v3", filing_sha256="f" * 64,
        sample_seed=20261014, sample_fraction="20/100", seed_committed_at="2026-08-01",
    )
    return AdjudicationRecord(**{**base, **kw})


# --- the loader's refusals -------------------------------------------------------------------


def test_adj__verdict_without_argument_is_refused() -> None:
    """An adjudication without an argument is an opinion wearing a schema."""
    with pytest.raises(AdjudicationError) as e:
        _row(argument="")
    assert "re-derive" in str(e.value)
    with pytest.raises(AdjudicationError):
        _row(argument="   ")


def test_adj__an_unknown_verdict_is_refused() -> None:
    with pytest.raises(AdjudicationError):
        _row(verdict="PROBABLY")


def test_adj__an_unadjudicated_mutant_raises_and_is_never_defaulted() -> None:
    """Defaulting to INNOCUOUS shrinks the denominator; to WRONG grows the residue. Both
    directions are a judgement nobody made, and one of them flatters us."""
    rec = _record([_row()])
    with pytest.raises(AdjudicationError) as e:
        rec.verdict_of("b" * 64)
    assert "INNOCUOUS" in str(e.value) and "WRONG" in str(e.value)


def test_adj__record_is_content_addressed_over_sorted_lines() -> None:
    """Shuffling the line order does not change the digest — RFC 8785 plus an EXPLICIT sort."""
    a, b, c = _row("a" * 64), _row("b" * 64), _row("c" * 64)
    assert _record([a, b, c]).digest() == _record([c, a, b]).digest()
    assert _record([a, b, c]).serialise() == _record([c, b, a]).serialise()
    assert _record([a, b]).digest() != _record([a, b, c]).digest()


def test_adj__the_seed_is_inside_the_digest() -> None:
    """A record whose sample was drawn under a different seed is a different record."""
    rows = [_row("a" * 64)]
    assert _record(rows).digest() != _record(rows, sample_seed=1).digest()


def test_adj__sample_seed_precedes_round_one() -> None:
    """From the record's own dates, exactly as `test_corpus__brief_predates_first_workbook` does
    for the fill brief. **A commitment made after seeing the result is not a commitment.**"""
    _record([_row(adjudicated_at="2026-08-14")], seed_committed_at="2026-08-01")
    with pytest.raises(AdjudicationError) as e:
        _record([_row(adjudicated_at="2026-08-01")], seed_committed_at="2026-08-14")
    assert "is not a commitment" in str(e.value)


def test_adj__a_mutant_cannot_be_adjudicated_twice_in_round_one() -> None:
    with pytest.raises(AdjudicationError):
        _record([_row("a" * 64), _row("a" * 64, verdict="INNOCUOUS")])


def test_adj__the_sample_is_deterministic_and_seeded() -> None:
    """`random.Random.sample` is deliberately NOT used: its algorithm is not a documented stable
    interface across CPython versions, and the seed is inside the digest."""
    rows = [_row(f"{i:064x}") for i in range(100)]
    rec = _record(rows)
    assert len(rec.sample()) == 20
    assert rec.sample() == rec.sample()
    assert rec.sample() != _record(rows, sample_seed=99).sample()
    assert set(rec.sample()) <= {r.mutant_id for r in rows}


# --- Cohen's κ --------------------------------------------------------------------------------


def test_kappa__perfect_agreement_is_one() -> None:
    r1 = {"a": "WRONG", "b": "INNOCUOUS", "c": "WRONG", "d": "INNOCUOUS"}
    k, n = cohens_kappa(r1, dict(r1))
    assert n == 4 and k == Decimal(1)


def test_kappa__chance_agreement_is_zero() -> None:
    """Hand-computed. 2×2 with p_o = 0.5 and p_e = 0.5, so κ = 0 exactly.

        rater 1: W W I I     rater 2: W I W I
        agree on a and d  ->  p_o = 2/4 = 0.5
        each rater says WRONG twice of four  ->  p_e = .5*.5 + .5*.5 = 0.5
    """
    r1 = {"a": "WRONG", "b": "WRONG", "c": "INNOCUOUS", "d": "INNOCUOUS"}
    r2 = {"a": "WRONG", "b": "INNOCUOUS", "c": "WRONG", "d": "INNOCUOUS"}
    k, n = cohens_kappa(r1, r2)
    assert n == 4 and k == Decimal(0)


def test_kappa__total_disagreement_is_negative_one() -> None:
    r1 = {"a": "WRONG", "b": "INNOCUOUS"}
    r2 = {"a": "INNOCUOUS", "b": "WRONG"}
    k, n = cohens_kappa(r1, r2)
    assert n == 2 and k == Decimal(-1)


def test_kappa__is_decimal_never_float() -> None:
    """R4. κ is published beside `|RESIDUE|`; a number nobody can re-derive to the last place is
    one two readers can disagree about for no reason."""
    k, _n = cohens_kappa({"a": "WRONG"}, {"a": "WRONG"})
    assert k is None or isinstance(k, Decimal)


def test_kappa__one_label_returns_none_not_zero() -> None:
    """`p_e == 1`: both raters used exactly one label, so κ is undefined.

    **`None` is not zero.** Zero means *no better than chance*; `None` means *the statistic does
    not apply here*, and reporting the first for the second is the substitution this whole system
    exists to refuse.
    """
    k, n = cohens_kappa({"a": "WRONG", "b": "WRONG"}, {"a": "WRONG", "b": "WRONG"})
    assert k is None and n == 2


def test_kappa__no_second_rater_is_none_with_n_zero() -> None:
    k, n = cohens_kappa({"a": "WRONG"}, {})
    assert k is None and n == 0


def test_kappa__renders_with_its_n_and_never_alone() -> None:
    assert "n = 4" in render_kappa(Decimal("0.83"), 4)
    assert "UNMEASURED" in render_kappa(None, 0, reason="no second adjudicator")
    assert "no second adjudicator" in render_kappa(None, 0, reason="no second adjudicator")


def test_kappa__below_the_trigger_the_reconciliation_rule_renders() -> None:
    """There is no THRESHOLD on κ — inventing one would be the invention this document refuses.
    There is a decision rule, and it renders with the number."""
    low = render_kappa(RECONCILIATION_TRIGGER - Decimal("0.1"), 40)
    assert "reconcile IN WRITING" in low and "round 3" in low and "BOTH κ values" in low
    assert "reconcile" not in render_kappa(RECONCILIATION_TRIGGER, 40)


def test_adj__the_committed_record_loads_and_carries_its_rater_label() -> None:
    """The record on disk, not a fixture. Its label must travel with every number it produces."""
    from cdfc.selfcheck.adjudication import load

    paths = sorted((REPO / "adjudication" / "v3").glob("*.jsonl"))
    assert paths, "no adjudication record is committed, so |RESIDUE| cites a hash of nothing"
    rec = load(
        paths[0], fault_model_version="v3", filing_sha256="", sample_seed=20261014,
        sample_fraction="20/100", seed_committed_at="2026-08-14",
    )
    assert rec.rows and rec.rater_label == RULE_BASED
    assert "not a human judgement" in rec.rater_label
    for row in rec.rows[:20]:
        assert row.argument.startswith("[R-"), "every row names the rule that decided it"
        assert " at " in row.argument, "and instantiates it on its own cell"
