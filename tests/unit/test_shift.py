"""Shared-formula materialisation — 211 of 505 FME formula cells depend on it."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.calc.shift import materialise, shift_formula  # noqa: E402


@pytest.mark.parametrize(("src", "dr", "dc", "want"), [
    ("SUM(C3:N3)", 4, 0, "SUM(C7:N7)"),
    ("A1+B1", 0, 1, "B1+C1"),
    ("$C$3", 5, 5, "$C$3"),                       # fully absolute never shifts
    ("C$3", 5, 0, "C$3"),                         # absolute row holds
    ("$C3", 0, 5, "$C3"),                         # absolute column holds
    ("C$3", 0, 2, "E$3"),                         # relative column shifts
    ("'3. Portfolio'!C3", 2, 0, "'3. Portfolio'!C5"),  # sheet name is not a reference
    ("A1", -5, 0, "#REF!"),                       # off the sheet is #REF!, never a clamp
])
def test_shift__rules(src: str, dr: int, dc: int, want: str) -> None:
    assert shift_formula(src, dr, dc) == want


def test_shift__string_literals_are_never_touched() -> None:
    """A shift that rewrote a message a filer reads would corrupt the artifact."""
    out = shift_formula('IF(A1>0,"A1 is required",B1)', 3, 0)
    assert '"A1 is required"' in out, out
    assert "A4" in out and "B4" in out


def test_shift__materialise_uses_the_master_offset() -> None:
    assert materialise("O3", "SUM(C3:N3)", "O7") == "SUM(C7:N7)"


def test_shift__an_unshifted_dependent_would_be_wrong_and_well_formed() -> None:
    """Why this module exists: evaluating a dependent with the MASTER's references
    returns a well-formed number for the wrong row."""
    assert materialise("O3", "SUM(C3:N3)", "O7") != "SUM(C3:N3)"
