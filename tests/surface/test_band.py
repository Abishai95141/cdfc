"""The band, and the invariant that it **cannot fill** — for every input, not for this one."""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.band import (  # noqa: E402
    ALWAYS_LAST, MIN_WIDTH_PERMILLE, BandInvariantViolated, Segment,
    assert_never_fills, band_segments, settled_fraction_text,
)


@dataclass
class _Counts:
    passed: int = 0
    failed: int = 0

    @property
    def total(self) -> int:
        return self.passed + self.failed


@dataclass
class _Un:
    indeterminate: int = 0
    notRun: int = 0
    noPredicate: int = 0
    error: int = 0


@dataclass
class _SF:
    settled: _Counts
    unsettled: _Un
    cellsTotal: int
    inScope: int
    declaredGaps: tuple = ()
    fraction: str = "0"


def _sf(passed=0, failed=0, ind=0, notrun=0, nopred=0, err=0) -> _SF:
    total = passed + failed + ind + notrun + nopred + err
    return _SF(_Counts(passed, failed), _Un(ind, notrun, nopred, err),
               cellsTotal=max(total, 1), inScope=max(total, 1))


def test_band__ends_with_the_two_that_make_it_undrawable() -> None:
    segs = band_segments(_sf(passed=10))
    assert tuple(s.kind for s in segs[-2:]) == ALWAYS_LAST
    assert all(s.pattern == "HATCH" for s in segs[-2:])


def test_band__a_perfect_run_still_does_not_fill() -> None:
    """The strongest possible input: everything settled and passing. It must STILL not fill —
    a full bar would claim nothing is undecidable from the filing and no constructed falsehood
    survives the check set, and neither can be true."""
    segs = band_segments(_sf(passed=3747))
    solid = sum(s.width_permille for s in segs if s.pattern == "SOLID")
    assert solid < sum(s.width_permille for s in segs)


def test_band__an_unknown_count_renders_as_not_yet_measured_never_as_zero() -> None:
    """Zero is a finding about the check set; None is a finding about us."""
    segs = {s.kind: s for s in band_segments(_sf(passed=10))}
    residue = segs["RESIDUE"]
    assert residue.count is None
    assert "not yet measured" in residue.label
    assert "0" not in residue.label.split("—")[0]


def test_band__labels_are_absolute_counts_never_percentages() -> None:
    for s in band_segments(_sf(passed=1898, nopred=1849)):
        assert "%" not in s.label


def test_band__a_segment_with_no_width_cannot_be_constructed() -> None:
    """A segment too narrow to see is a segment that is not there."""
    with pytest.raises(BandInvariantViolated):
        Segment(kind="RESIDUE", count=None, pattern="HATCH", label="x", width_permille=0)


def test_band__a_percentage_label_cannot_be_constructed() -> None:
    with pytest.raises(BandInvariantViolated):
        Segment(kind="SETTLED_PASS", count=1, pattern="SOLID", label="50% settled",
                width_permille=10)


def test_band__a_band_that_would_fill_is_refused() -> None:
    """THE GUARD ITSELF, exercised. Without this the invariant is only ever checked on inputs the
    builder produced, which is checking the builder rather than the property."""
    fake = (
        Segment("SETTLED_PASS", 1, "SOLID", "1 x", 1000),
        Segment("NOT_SETTLEABLE_FROM_ARTIFACT", None, "HATCH", "x", MIN_WIDTH_PERMILLE),
        Segment("RESIDUE", None, "HATCH", "x", MIN_WIDTH_PERMILLE),
    )
    assert_never_fills(fake)          # this one is fine: solid 1000 < total 1024
    bad = (Segment("SETTLED_PASS", 1, "SOLID", "1 x", 1000),
           Segment("SETTLED_FAIL", 1, "SOLID", "1 x", 24))
    with pytest.raises(BandInvariantViolated):
        assert_never_fills(bad)


def test_band__settled_text_carries_both_integers() -> None:
    """`ci/no-bare-rate.sh`'s rule at the surface: a rate never renders without its fraction."""
    assert settled_fraction_text(_sf(passed=1898, nopred=1849)) == "1,898 of 3,747"


@given(
    passed=st.integers(0, 5000), failed=st.integers(0, 5000),
    ind=st.integers(0, 500), notrun=st.integers(0, 500),
    nopred=st.integers(0, 5000), err=st.integers(0, 500),
)
@settings(max_examples=50, derandomize=True)
def test_prop_band__never_fills_for_any_input(passed, failed, ind, notrun, nopred, err) -> None:
    """THE PROPERTY, over the whole count space including all-zero and all-settled.

    The invariant is structural, so it is asserted structurally: there must be no assignment of
    counts that produces a full bar.
    """
    segs = band_segments(_sf(passed, failed, ind, notrun, nopred, err))
    solid = sum(s.width_permille for s in segs if s.pattern == "SOLID")
    total = sum(s.width_permille for s in segs)
    assert solid < total
    assert tuple(s.kind for s in segs[-2:]) == ALWAYS_LAST
