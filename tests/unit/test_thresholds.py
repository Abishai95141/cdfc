"""P10-B1 — the pre-registered thresholds, and the numerator that F18 decides."""

from __future__ import annotations

import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.selfcheck.thresholds import (  # noqa: E402
    CALIBRATION_SETTINGS,
    CANARY_INAPPLICABLE_CEILING,
    MAX_WITNESSES,
    MAX_WITNESSES_STATUS,
    PRE_REGISTERED,
    ceiling_exceeded,
)

DOC = REPO / "docs" / "SELFCHECK-THRESHOLDS.md"


def test_th__ceiling_is_pre_registered() -> None:
    """A ceiling chosen after seeing the rate is not a ceiling, it is a description of the rate.

    Every constant in `PRE_REGISTERED` must appear in `docs/SELFCHECK-THRESHOLDS.md` with its
    value, so moving the constant without moving its dated row fails the build. The test reads the
    module's own map rather than a second list here — a second list is the one that drifts.
    """
    assert DOC.is_file(), "the thresholds document does not exist, so nothing is pre-registered"
    text = DOC.read_text(encoding="utf-8")
    for name, value in PRE_REGISTERED.items():
        assert name in text, f"{name} is not pre-registered in {DOC.name}"
        assert str(value) in text, (
            f"{DOC.name} names {name} but not its current value {value}. A document that names a "
            "constant without its value cannot be checked against the code."
        )


def test_th__the_ceiling_is_exact_arithmetic() -> None:
    """R4. A threshold that can turn on the last binary place is one nobody can re-derive."""
    assert isinstance(CANARY_INAPPLICABLE_CEILING, Decimal)
    assert CANARY_INAPPLICABLE_CEILING == Decimal("0.25")


def test_th__indeterminate_counts_toward_the_ceiling() -> None:
    """F18. The numerator is `inapplicable + indeterminate`, and pooling only the first fails.

    An INDETERMINATE canary is one where we cannot say whether the predicate would have caught the
    fault. A run in which we cannot say that for a third of the checks has not demonstrated
    liveness either — so it counts HERE, and is reported apart everywhere else.
    """
    assert ceiling_exceeded(0, 0, 100) is False
    assert ceiling_exceeded(25, 0, 100) is False, "exactly at the ceiling is not over it"
    assert ceiling_exceeded(26, 0, 100) is True
    assert ceiling_exceeded(0, 26, 100) is True, "indeterminate alone can exceed the ceiling"
    assert ceiling_exceeded(13, 13, 100) is True, "the numerator is BOTH, not the larger of them"
    assert ceiling_exceeded(20, 0, 100) is False and ceiling_exceeded(20, 6, 100) is True


def test_th__an_empty_loop_exceeds_the_ceiling() -> None:
    """`rows == 0` is not a pass. A loop that attempted nothing has an undefined rate, and
    returning False would let a build with no canary layer sail through the disposition."""
    assert ceiling_exceeded(0, 0, 0) is True
    assert ceiling_exceeded(0, 0, -1) is True


def test_th__max_witnesses_renders_its_provisional_status() -> None:
    """§5.1, adversary F44. *Nothing in the corpus argues for 3.*

    A constant nobody can defend is allowed to ship — labelled — and is not allowed to ship
    quietly. The label points at the document that will close it.
    """
    assert MAX_WITNESSES == 3
    assert "PROVISIONAL" in MAX_WITNESSES_STATUS
    assert "P10-canary-cost" in MAX_WITNESSES_STATUS
    assert MAX_WITNESSES in CALIBRATION_SETTINGS, (
        "the calibration curve must be measured AT the value the code ships, or it cannot close it"
    )


def test_th__the_document_carries_a_dated_row_per_constant() -> None:
    text = DOC.read_text(encoding="utf-8")
    dates = re.findall(r"\d{1,2} August 2026|\d{4}-\d{2}-\d{2}", text)
    assert len(dates) >= len(PRE_REGISTERED), (
        "a threshold with no date beside it cannot be shown to predate the number it judges"
    )
