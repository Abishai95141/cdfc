"""The predicate registry refuses unconditionally at P0."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from cdfc.predicates.registry import UnqualifiedPredicate, load_or_refuse  # noqa: E402


def test_nc__Q02_unqualified_predicate_does_not_load() -> None:
    """PROVISIONAL until P4: its admission-side twin (a QUALIFIED predicate that loads)
    cannot exist until the predicate schema does. The sweep reports it in its own column
    and excludes it from entries_caught, because a green entry with no information in it
    must not be counted as evidence."""
    with pytest.raises(UnqualifiedPredicate, match="not admitted|no qualification record"):
        load_or_refuse({"id": "P-0001", "expr": "true"})


def test_registry__refusal_names_the_predicate() -> None:
    with pytest.raises(UnqualifiedPredicate, match="P-0042"):
        load_or_refuse({"id": "P-0042"})
