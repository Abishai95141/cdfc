"""The validation ledger: every published number resolves to a row, and every row carries a caveat.

**Why the caveat field is required rather than encouraged.** A number without a stated licence gets
read as licensing whatever the reader hoped. Every measurement row names, in one sentence, the
sentence it licenses — and, where it matters more, the sentence it does not.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

LEDGER = REPO / "reports" / "validation-ledger.jsonl"

REQUIRED = (
    "phase", "build", "metric", "numerator", "denominator", "denominator_source",
    "warrant", "produced_by", "command", "caveat", "date",
)
ADMISSIBLE_WARRANTS = {"MEASURED", "DERIVED", "DERIVED-FROM-SPEC", "MODEL-EXTRACTED", "ASSUMED"}


def _rows() -> list[dict]:
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def _metrics() -> list[dict]:
    return [r for r in _rows() if "metric" in r]


def test_ledger__every_measurement_row_is_complete() -> None:
    metrics = _metrics()
    assert metrics, "the ledger carries no measurement row at all"
    for r in metrics:
        missing = [k for k in REQUIRED if k not in r]
        assert missing == [], f"{r.get('metric')} is missing {missing}"
        assert r["warrant"] in ADMISSIBLE_WARRANTS, f"{r['metric']}: warrant {r['warrant']!r}"
        assert len(r["caveat"]) > 60, (
            f"{r['metric']}: a caveat shorter than a sentence is not a licence. A number with no "
            "stated licence gets read as licensing whatever the reader hoped."
        )
        assert r["denominator_source"], f"{r['metric']}: a denominator nobody can name"
        assert (REPO / r["produced_by"]).exists() or r["produced_by"].startswith("tools/"), (
            f"{r['metric']}: produced_by {r['produced_by']!r} does not resolve"
        )


def test_ledger__no_ratio_exceeds_its_denominator() -> None:
    for r in _metrics():
        assert 0 <= r["numerator"] <= r["denominator"], (
            f"{r['metric']}: {r['numerator']}/{r['denominator']} is not a ratio"
        )


def test_ledger__the_p4_rows_are_present() -> None:
    """The ledger grew since the P3 tag. A phase that publishes numbers appends rows."""
    metrics = {r["metric"] for r in _metrics() if r["phase"] == "P4"}
    assert {
        "schema_keys.both_ways_agreement.all_nine",
        "harvest.candidates.all_nine",
        "harvest.non_empty_workbooks",
        "cel.runtime_agreement.admitted_subset",
        "cel.runtime_agreement.error_semantics",
        "harvest.static_settled_cells.fme",
    } <= metrics


@pytest.mark.parametrize(
    "metric,phrase",
    [
        ("cel.runtime_agreement.admitted_subset", "DIFFERENTIAL, not CONFORMANCE"),
        ("cel.runtime_agreement.error_semantics", "pre-flight guard"),
        ("harvest.non_empty_workbooks", "P15"),
        ("schema_keys.both_ways_agreement.all_nine", "NC-N01"),
        ("harvest.static_settled_cells.fme", "2,373"),
    ],
)
def test_ledger__the_caveat_carries_the_label_that_must_travel(metric: str, phrase: str) -> None:
    row = next(r for r in _metrics() if r["metric"] == metric)
    assert phrase in row["caveat"], (
        f"{metric}'s caveat must carry {phrase!r}: the label travels with the number or the "
        "number is quoted without it"
    )


def test_ledger__the_p4_numbers_agree_with_what_the_code_produces_today() -> None:
    """A ledger row nobody can re-derive is a screenshot."""
    from cdfc.predicates.harvest import harvest_all

    res = harvest_all(REPO / "fixtures" / "prescribed")
    total = sum(len(r.candidates) for r in res)
    non_empty = sum(1 for r in res if r.candidates)
    by_metric = {r["metric"]: r for r in _metrics()}
    assert by_metric["harvest.candidates.all_nine"]["numerator"] == total
    assert by_metric["harvest.non_empty_workbooks"]["numerator"] == non_empty
    assert by_metric["harvest.non_empty_workbooks"]["denominator"] == len(res)


def test_ledger__absence_rows_still_parse_beside_the_measurement_rows() -> None:
    """Two row shapes in one file. `ci/no-bare-absence.sh` resolves the first kind and must not
    crash on the second — it did, the first time a measurement row was appended."""
    absence = [r for r in _rows() if "row_id" in r]
    assert absence, "the absence rows have gone; ledger:<row_id> citations would stop resolving"
    for r in absence:
        assert "positive_control_count" in r
