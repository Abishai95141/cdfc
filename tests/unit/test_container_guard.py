"""The container guard — one test per limit, and the admission-side control.

Every trip must name the LIMIT and the OBSERVED VALUE. A guard that says only "rejected"
cannot be triaged, and an operator who cannot triage a rejection switches the guard off.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.container_guard import GuardLimits, GuardTrip, guard  # noqa: E402
from cdfc.verdict.invalid import InvalidCause  # noqa: E402

ADV = REPO / "fixtures" / "adversarial"
FIX = REPO / "fixtures" / "prescribed"

# fixture -> (substring naming the limit, substring naming the observed value)
TRIPS = [
    ("zipbomb-entrycount__x1200.xlsx", "entry count", "1024"),
    ("zipbomb-ratio__x1000.xlsx", "compression ratio", "100.0"),
    ("zipbomb-entrysize__17mb.xlsx", "uncompressed size", "16777216"),
    ("not-a-zip__renamed.xlsx", "not a readable zip", ""),
    ("missing-part__no-workbook.xlsx", "missing required part", "xl/workbook.xml"),
    ("disallowed-suffix__shell.xlsx", "disallowed entry suffix", ".sh"),
]


@pytest.mark.parametrize(("name", "limit_phrase", "value_phrase"), TRIPS)
def test_guard__trips_and_names_the_limit(name: str, limit_phrase: str, value_phrase: str) -> None:
    with pytest.raises(GuardTrip) as ei:
        guard(ADV / name)
    detail = ei.value.detail
    assert limit_phrase in detail, f"the trip does not name the limit: {detail}"
    if value_phrase:
        assert value_phrase in detail, f"the trip does not name the observed value: {detail}"
    assert ei.value.cause is InvalidCause.CONTAINER_GUARD_TRIPPED


def test_guard__xxe_fixture_is_admitted_by_the_container_guard() -> None:
    """Deliberate division of responsibility, asserted so nobody 'fixes' it.

    An XXE payload is a well-formed container. The container guard is about container
    limits; the entity is the PARSER's problem and `xmlsafe` handles it (NC-P05b). A
    guard that also tried to catch XXE would be parsing XML before the guard ran, which
    is the exact ordering defect NC-P05a exists to prevent.
    """
    report = guard(ADV / "xxe-entity__passwd.xlsx")
    assert report.entries >= 3


# --------------------------------------------------------------------------------
# THE ADMISSION-SIDE CONTROL. Without it the guard is a reject-everything baseline
# that would score perfectly on the negative controls alone.
# --------------------------------------------------------------------------------
ALL_NINE = sorted(FIX.glob("*.xlsx"))


def test_guard__the_corpus_is_not_empty() -> None:
    assert len(ALL_NINE) == 9, "the admission control would be vacuous without the corpus"


@pytest.mark.parametrize("wb", ALL_NINE, ids=lambda p: p.name[:28])
def test_guard__all_nine_pass_the_guard(wb: Path) -> None:
    report = guard(wb)
    assert report.entries > 0 and report.total_uncompressed > 0


def test_guard__headroom_is_real_not_tuned_to_the_largest_workbook() -> None:
    """The limits must leave room. A limit tuned to the observed maximum rejects the
    tenth workbook, and this corpus is nine."""
    limits = GuardLimits()
    obs_entries = max(guard(w).entries for w in ALL_NINE)
    obs_entry = max(guard(w).max_entry for w in ALL_NINE)
    obs_total = max(guard(w).total_uncompressed for w in ALL_NINE)
    assert limits.max_entries >= obs_entries * 4, (obs_entries, limits.max_entries)
    assert limits.max_entry_uncompressed_bytes >= obs_entry * 4, obs_entry
    assert limits.max_total_uncompressed_bytes >= obs_total * 4, obs_total


def test_guard__report_projection_carries_no_float() -> None:
    """`ratio` is a float and must not enter a hashed projection; its integer inputs do."""
    r = guard(FIX / "ITFS_Monthly_report201220241626.xlsx")
    obj = r.as_canonical_obj()
    assert "ratio" not in obj
    assert {"total_uncompressed", "total_compressed"} <= set(obj)
    from cdfc.canon import canonical_json

    canonical_json(obj)  # raises if a float slipped in
