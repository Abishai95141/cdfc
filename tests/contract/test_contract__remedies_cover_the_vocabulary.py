"""Every reason code that can reach a cell has a remedy, or a written argument for having none."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.surface.unchecked import MIN_REMEDY_CHARS, load_remedies  # noqa: E402
from cdfc.verdict.reasons import ReasonCode  # noqa: E402

# `out_of_scope.*` codes never reach the Unchecked panel: an out-of-scope cell is not unchecked,
# it is outside the denominator, and it is accounted for in the closure's own term.
NOT_RENDERABLE = {c.value for c in ReasonCode if c.value.startswith("out_of_scope.")}


def test_contract__every_renderable_reason_has_a_remedy_or_an_argument() -> None:
    remedies, unremediable = load_remedies()
    renderable = {c.value for c in ReasonCode} - NOT_RENDERABLE
    covered = set(remedies) | set(unremediable)
    missing = sorted(renderable - covered)
    assert missing == [], (
        f"{len(missing)} reason codes can reach a cell with no remedy and no argument: {missing}. "
        "Each one is a group that would render, and there is no fallback string — so a run that "
        "produced one of these would abort the report rather than print a placeholder. Write a "
        "remedy, or list it under `deliberately_unremediable` with an argument."
    )


def test_contract__declining_a_remedy_requires_an_argument_at_length() -> None:
    """Declining without saying why is a way of moving a reason code out of the panel."""
    _, unremediable = load_remedies()
    assert unremediable, "nothing is declared unremediable; this assertion would be vacuous"
    for code, argument in unremediable.items():
        assert len(argument) >= MIN_REMEDY_CHARS, f"{code}: {len(argument)} characters"


def test_contract__the_vocabulary_is_still_thirty() -> None:
    """The closed set. A reason outside it is a reason nobody wrote a remedy for."""
    assert len(list(ReasonCode)) == 30
