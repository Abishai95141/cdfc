"""assert_absent — an absence is refused unless a positive control saw a presence."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cdfc.measure.absence import AbsenceWithoutControl, assert_absent, read_ledger  # noqa: E402

CORPUS = ["alpha", "beta", "gamma"]


def test_assert_absent__raises_when_control_returns_zero(tmp_path: Path) -> None:
    """A broken interface must not be reported as an empty world."""
    with pytest.raises(AbsenceWithoutControl, match="cannot see a presence"):
        assert_absent(
            lambda c: 0,
            positive_control=lambda c: 0,   # the interface sees nothing at all
            corpus=CORPUS,
            corpus_id="unit",
            query_name="broken_interface",
            ledger=tmp_path / "l.jsonl",
        )


def test_assert_absent__admits_when_control_is_live(tmp_path: Path) -> None:
    """Admission-side twin: a live control lets a genuine zero through."""
    claim = assert_absent(
        lambda c: sum(1 for x in c if x == "delta"),
        positive_control=lambda c: sum(1 for x in c if x == "alpha"),
        corpus=CORPUS,
        corpus_id="unit",
        query_name="delta_absent",
        ledger=tmp_path / "l.jsonl",
    )
    assert claim.count == 0
    assert claim.positive_control_count == 1
    assert claim.citation.startswith("ledger:")


def test_assert_absent__writes_both_counts(tmp_path: Path) -> None:
    led = tmp_path / "l.jsonl"
    claim = assert_absent(
        lambda c: 0,
        positive_control=lambda c: 3,
        corpus=CORPUS,
        corpus_id="unit",
        query_name="both_counts",
        ledger=led,
    )
    row = read_ledger(led)[claim.row_id]
    assert row["count"] == 0 and row["positive_control_count"] == 3 and row["admissible"] is True


def test_assert_absent__records_the_refusal_too(tmp_path: Path) -> None:
    """A refused claim is still written. A refusal nobody can audit is a silent drop."""
    led = tmp_path / "l.jsonl"
    with pytest.raises(AbsenceWithoutControl):
        assert_absent(lambda c: 0, positive_control=lambda c: 0, corpus=CORPUS,
                      corpus_id="unit", query_name="refused", ledger=led)
    rows = read_ledger(led)
    assert any(r["query_name"] == "refused" and r["admissible"] is False for r in rows.values())
