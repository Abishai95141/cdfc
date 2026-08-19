"""A3 — CONTRADICTED / SUPPORTED / NOT_ASSESSED, exact matching only."""

from __future__ import annotations

from pathlib import Path

import pytest

from cdfc.evidence.contradict import NotAssessed, Standing, assess
from cdfc.evidence.observe import canonical, index, observe
from cdfc.qualify.instruments import InstrumentStore


@pytest.fixture(scope="module")
def source():
    return InstrumentStore().get("statute-fm-regulations-2025")


@pytest.fixture(scope="module")
def observed(source):
    return index(observe(source))


def test_a3__every_observation_reverifies(source) -> None:
    """A locator that cannot reproduce what it found is not evidence."""
    obs = observe(source)
    assert obs, "no observations would make every other assertion vacuous"
    assert all(o.reverify(source) for o in obs)


def test_a3__a_deleted_value_is_never_supported(source, observed) -> None:
    """W0-C in miniature: similarity reported 20 of 20 SUPPORTED on DELETED evidence. Exact
    matching must report a value the corpus does not contain as NOT_ASSESSED, never supported."""
    d = assess({"X!A1": "999999999999"}, observed, source_document=source.instrument_id)
    assert not d.supported
    assert d.not_assessed[0].reason is NotAssessed.NO_OBSERVATION


def test_a3__a_contradiction_requires_a_rule(source, observed) -> None:
    """Two different numbers in two documents are two different numbers until something says
    they are about the same quantity."""
    filed = {"X!A1": "380000"}
    assert not assess(filed, observed, source_document="s").contradicted
    d = assess(filed, observed, bindings={"X!A1": "500000"}, source_document="s")
    assert len(d.contradicted) == 1
    assert d.contradicted[0].standing is Standing.CONTRADICTED
    assert "500000" in d.contradicted[0].line()


def test_a3__an_attestation_is_never_contradicted(source, observed) -> None:
    """A3's first run produced a headline contradiction out of a category error: it compared the
    Second Schedule's money threshold against a cell holding `Yes`."""
    d = assess({"8. Compliance Status!C6": "Yes"}, observed,
               bindings={"8. Compliance Status!C6": "500000"},
               attestations=frozenset({"8. Compliance Status!C6"}), source_document="s")
    assert not d.contradicted, "no observation settles a certification"
    assert d.not_assessed[0].reason is NotAssessed.ATTESTATION_NOT_A_MEASUREMENT


def test_a3__the_three_states_partition_every_filed_value(source, observed) -> None:
    filed = {f"X!A{i}": str(i) for i in range(1, 40)}
    filed["X!B1"] = ""
    d = assess(filed, observed, source_document="s")
    assert d.total == len(filed)
    assert len(d.contradicted) + len(d.supported) + len(d.not_assessed) == len(filed)


def test_a3__empty_is_not_absent_is_not_zero(source, observed) -> None:
    d = assess({"X!A1": "", "X!A2": "0"}, observed, source_document="s")
    reasons = {a.field: a.reason for a in d.not_assessed}
    assert reasons["X!A1"] is NotAssessed.FIELD_EMPTY
    assert reasons["X!A2"] is not NotAssessed.FIELD_EMPTY


def test_a3__canonical_normalises_grouping_and_nothing_else() -> None:
    """`5,00,000` and `500000` are one number in two conventions. Rounding and unit conversion
    are excluded: each is a judgement, and a judgement here is similarity under another name."""
    assert canonical("5,00,000") == canonical("500000") == "500000"
    assert canonical("500000.00") == "500000"
    assert canonical("500001") != canonical("500000")
    assert canonical("5000") != canonical("500000"), "no scale inference"
