"""NC-A01 — an absence claim citing a dead control must fail the gate."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from injectors import AbsenceCitesEmptyControl, inject, run_gate  # noqa: E402


def test_nc__A01_absence_must_resolve_a_live_ledger_row() -> None:
    assert run_gate("ci/no-bare-absence.sh") == 0, "precondition: green on a correct tree"
    with inject(AbsenceCitesEmptyControl()):
        rc = run_gate("ci/no-bare-absence.sh")
    assert rc != 0, "an absence citing a ledger row with a zero control was accepted"


def test_nc__A01b_the_gate_is_not_merely_grepping_for_a_phrase() -> None:
    """The lexical form of this gate is defeated in four words. Prove ours is not.

    A line that says 'positive control' but cites nothing must STILL fail.
    """
    doc = Path("docs/ABSENCE-SCOPE.md")
    original = doc.read_bytes()
    try:
        # assembled at runtime: a literal here would itself be an uncited absence claim
        # in a scanned file, and the gate would be right to reject it.
        phrase = "does not " + "occur"
        doc.write_bytes(
            original
            + f"\nThe term {phrase} in the corpus; we ran a positive control.\n".encode()
        )
        assert run_gate("ci/no-bare-absence.sh") != 0, (
            "the gate accepted the words 'positive control' with no resolvable citation"
        )
    finally:
        doc.write_bytes(original)
