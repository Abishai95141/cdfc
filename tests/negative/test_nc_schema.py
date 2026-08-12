"""P2 negative controls — the denominator is the number everything else is a fraction of.

The failure this phase exists to prevent was committed twice in one afternoon by the
person who knew about it: once by sampling mutation sites only from cells the predicates
already read, and once by computing a settled fraction from a denominator built out of the
numerator.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema import styles_mask_b as B  # noqa: E402
from cdfc.schema.styles_mask import Rule, build  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
ALL_NINE = sorted(FIX.glob("*.xlsx"))


# --------------------------------------------------------------------------- NC-D02
def test_nc__D02_the_two_paths_agree_on_every_workbook() -> None:
    """D2 differential. Proves the paths are two implementations, and NOTHING MORE —
    they would agree just as well on the rejected reading."""
    for wb in ALL_NINE:
        a = build(wb, Rule.V3).n_cells
        b = B.count_field_surface(wb)
        assert a == b, f"{wb.name}: path A {a} vs path B {b}"


def test_nc__D02b_the_paths_do_not_share_a_module() -> None:
    """A differential between two modules that share a resolver is one function called
    twice.

    Checked by AST IMPORT CLOSURE, not by grepping the source. The first version of this
    test grepped for the string `styles_mask` and failed on path B's own docstring, which
    names path A in prose to explain why it must not import it. A grep over prose is a
    shallow proxy for an import.
    """
    sys.path.insert(0, str(REPO / "tests" / "negative"))
    from importgraph import import_closure

    closure_b = import_closure("cdfc.schema.styles_mask_b")
    assert "cdfc.schema.styles_mask" not in closure_b, (
        f"path B reaches path A ({sorted(closure_b)}); the differential is worthless"
    )
    closure_a = import_closure("cdfc.schema.styles_mask")
    assert "cdfc.schema.styles_mask_b" not in closure_a, "path A reaches path B"


def test_nc__D02c_the_differential_can_actually_fail() -> None:
    """If the two paths cannot disagree, their agreement is not evidence.

    Compare path A under the ADOPTED rule against path B under the REJECTED one: a real
    divergence must appear, or the comparator is blind.
    """
    a = build(FME, Rule.V3).n_cells
    b_wrong = B.count_field_surface(FME, absence_means_unlocked=True)
    assert a != b_wrong, "the two paths cannot be made to disagree; the differential is blind"
    assert b_wrong == 6249, b_wrong


# --------------------------------------------------------------------------- NC-D03
def test_nc__D03_hidden_sheets_are_in_scope() -> None:
    """THE DEFECT THIS PHASE'S OWN HEADLINE NUMBER CANNOT SEE.

    The `Dropdown` sheet is hidden and contributes no unlocked non-formula cells, so an
    implementation that skipped hidden sheets returns 3,747 anyway — right by accident
    while the code is wrong. So assert the SHEET SET, never the total.
    """
    fs = build(FME, Rule.V3)
    assert "Dropdown" in fs.sheets_in_scope, (
        f"the hidden sheet is out of scope; scope is {fs.sheets_in_scope}"
    )
    assert len(fs.sheets_in_scope) == 10
    assert fs.n_cells == 3747, "and the total is unchanged by its presence — which is the point"


# --------------------------------------------------------------------------- NC-D05
def test_nc__D05_absence_of_protection_is_not_unlocked() -> None:
    """Reading absence as unlocked inverts the OOXML default and adds 2,502 cells."""
    adopted = build(FME, Rule.V3).n_cells
    rejected = build(FME, Rule.V3_ABS).n_cells
    assert adopted == 3747 and rejected == 6249
    assert rejected - adopted == 2502


def test_nc__D05b_the_three_lawful_readings_are_all_computed() -> None:
    """All three are computed, not just the adopted one.

    Computing the rejected reading is what exposed rule 2a: `<protection hidden="1"/>` is
    an element PRESENT without `@locked`, which is an explicit lock by attribute default
    and not an inheritance case. Under `v3` both readings give 3,747 and the ambiguity is
    invisible; it only appears under `v3-abs`, as three cells.
    """
    assert build(FME, Rule.V3).n_cells == 3747
    assert build(FME, Rule.V3_UW).n_cells == 3755
    assert build(FME, Rule.V3_ABS).n_cells == 6249
    c = build(FME, Rule.V3).census
    assert (c.n_cell_xfs, c.explicit_unlocked, c.explicit_locked, c.inheriting) == (434, 105, 7, 322)


# --------------------------------------------------------------------------- NC-D06
def test_nc__D06_rule_6_fires_before_rule_5() -> None:
    """A workbook shipping no protection mask has NO derivable denominator.

    Two of the nine are in this state. Returning a number for them would be a
    denominator manufactured from a stray unlocked style id.
    """
    not_derivable = [w.name for w in ALL_NINE if build(w, Rule.V3).n_cells is None]
    assert len(not_derivable) == 2, not_derivable
    for name in not_derivable:
        fs = build(FIX / name, Rule.V3)
        assert fs.n_cells is None
        assert "not derivable" in fs.source
        assert B.count_field_surface(FIX / name) is None, "path B disagrees on derivability"


# --------------------------------------------------------------------------- NC-D07
def test_nc__D07_the_denominator_declares_its_validation_state() -> None:
    """Nothing in P2 can falsify the mask. It ships PROVISIONAL-UNVALIDATED and says so
    on every surface until P8-B1 supplies an external falsifier."""
    fs = build(FME, Rule.V3)
    assert fs.validation_state == "PROVISIONAL-UNVALIDATED"
    obj = fs.as_canonical_obj()
    assert obj["validation_state"] == "PROVISIONAL-UNVALIDATED"
    assert obj["generator_rule"] == "v3", "a fraction must name the rule that produced its denominator"


def test_nc__D07b_the_canonical_projection_carries_the_rule_and_the_state() -> None:
    from cdfc.canon import canonical_json

    blob = canonical_json(build(FME, Rule.V3).as_canonical_obj())
    assert b"generator_rule" in blob and b"validation_state" in blob


# --------------------------------------------------------------------------- NC-D08
def test_nc__D08_the_denominator_is_not_derived_from_any_predicate() -> None:
    """The defect committed twice in one afternoon: a denominator built out of the
    numerator. Assert structurally that the mask's import closure never reaches the
    predicate package."""
    sys.path.insert(0, str(REPO / "tests" / "negative"))
    from importgraph import import_closure

    for mod in ("cdfc.schema.styles_mask", "cdfc.schema.styles_mask_b"):
        closure = import_closure(mod)
        offenders = [m for m in closure if "predicate" in m or "qualify" in m or "evaluate" in m]
        assert not offenders, f"{mod} reaches {offenders}: the denominator would come from the numerator"


@pytest.mark.parametrize("wb", ALL_NINE, ids=lambda p: p.name[:26])
def test_nc__D09_every_workbook_states_a_rule_and_a_state(wb: Path) -> None:
    fs = build(wb, Rule.V3)
    assert fs.generator_rule == "v3"
    assert fs.validation_state == "PROVISIONAL-UNVALIDATED"
    assert fs.source
