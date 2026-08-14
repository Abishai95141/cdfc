"""G-EVAL's independence label, and the rule that it travels with the numbers.

`plan/02` §Y: *"there is no third option and no silent one."* Either arm 2's oracle was authored
by someone who did not write the evaluator, or every surface quoting a number derived from
`cdfc.calc` carries the literal `SAME-AUTHOR — a weaker instrument`. The third option is the one
where nobody remembers, and these tests are what makes it unreachable.

**The positive control is the important half here.** Four tests asserting *the label is absent
because we are independent* are all satisfied by a `label()` that returns `""` unconditionally.
`test_geval__the_label_appears_when_the_author_is_ours` flips the declaration and asserts the
label comes back — so the mechanism is observed working in the direction that costs something.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.measure.geval import (  # noqa: E402
    ARM1,
    ARM2,
    ARMS,
    THIS_PROJECT,
    WEAKER_INSTRUMENT,
    gate_status,
    label,
)

MEASUREMENTS = REPO / "docs" / "measurements"


def test_arm_two_author_is_not_the_evaluator_author() -> None:
    """The rule, in the only form that has no third branch.

    The plan's mechanism reads `expected.json`'s `authored_by` and compares it to `calc/`'s
    dominant `git blame` author. This build has no `expected.json`: arm 2's oracle is a foreign
    engine, so the author is an organisation rather than a file header. The comparison is the
    same one — is the oracle's author us? — against a field that has to be filled in with a name.
    """
    if ARM2.oracle_author == THIS_PROJECT:
        assert label() == WEAKER_INSTRUMENT
        assert gate_status() == "PASSED — NOT INDEPENDENT"
        for page in ("P3-evaluator.md", "P3-cached-value-reproduction.md"):
            text = (MEASUREMENTS / page).read_text(encoding="utf-8")
            assert WEAKER_INSTRUMENT in text, (
                f"{page} quotes numbers derived from cdfc.calc and does not carry the label"
            )
    else:
        assert label() == ""
        assert gate_status() == "PASSED"


def test_geval__the_label_appears_when_the_author_is_ours() -> None:
    """THE POSITIVE CONTROL. Without it every assertion above is green on a function that
    always returns the empty string, and the rule would be enforced by nothing."""
    ours = dataclasses.replace(ARM2, oracle_author=THIS_PROJECT)
    assert ours.independence == "SAME-AUTHOR"
    assert ARM2.independence == "INDEPENDENT", "the real arm must not have been mutated"


def test_geval__independence_is_computed_and_has_no_setter() -> None:
    """A declared independence is a claim. `independence` is a property over `oracle_author`,
    so the only way to assert independence is to write down whose oracle it is."""
    assert isinstance(type(ARM2).independence, property)
    assert not hasattr(ARM2, "__dict__"), "the record is slotted; no attribute can be added"


def test_geval__both_arms_declare_what_they_are_blind_to() -> None:
    """An arm with no declared blind spot is an arm nobody examined. This is the field that
    makes the two arms non-redundant: arm 1 is blind to a constant workbook, arm 2 to a
    defective formula, and neither absence is inferrable from the other's presence."""
    for a in ARMS:
        assert a.blind_to.strip(), f"arm {a.n} declares no blind spot"
        assert a.finds.strip(), f"arm {a.n} does not say what a disagreement would mean"
    assert ARM1.blind_to != ARM2.blind_to, (
        "two arms blind to the same thing are one arm counted twice"
    )


def test_contract__geval_label_travels_with_the_numbers() -> None:
    """Every page publishing a number derived from `cdfc.calc` states G-EVAL's status on its
    face — not in a residue section, and not by omission."""
    for page in ("P3-evaluator.md", "P3-cached-value-reproduction.md"):
        text = (MEASUREMENTS / page).read_text(encoding="utf-8")
        assert f"G-EVAL: {gate_status()}" in text, (
            f"{page} does not carry G-EVAL's status. A gate green on an oracle we wrote "
            "ourselves must say so where the number is, or the reader cannot discount it."
        )
