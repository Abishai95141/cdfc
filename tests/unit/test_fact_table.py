"""P3-B1/B2/B3 — the fact model, units, and the provenance anchor."""

from __future__ import annotations

import datetime as _dt
import sys
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import canonical_json  # noqa: E402
from cdfc.facts.anchor import Anchor, Warrant, compose  # noqa: E402
from cdfc.facts.fact_table import FactError, FactTable, Leaf, build  # noqa: E402
from cdfc.facts.units import (  # noqa: E402
    UNITS_PER_USD_MILLION,
    Unit,
    UnitError,
    from_units,
    tau,
    to_units,
    within_tolerance,
)


# ------------------------------------------------------------------ B2: units
def test_units__one_unit_is_one_thousand_usd() -> None:
    """The specification carried two definitions differing by 1000x. This pins the one
    every tolerance in the design is expressed in."""
    assert UNITS_PER_USD_MILLION == 1_000
    assert to_units(Decimal("12.34")) == 12_340
    assert from_units(12_340) == Decimal("12.34")


def test_units__refuses_precision_the_unit_cannot_hold() -> None:
    """Rounding here would be a silent loss at the boundary where money enters."""
    with pytest.raises(UnitError, match="more precision"):
        to_units(Decimal("12.3456"))


def test_units__blank_is_none_not_zero() -> None:
    assert to_units(None) is None and to_units("") is None


def test_units__rejects_non_numeric_rather_than_zeroing_it() -> None:
    with pytest.raises(UnitError):
        to_units("not a number")


def test_units__tau_is_an_integer_count_not_a_percentage() -> None:
    """A relative tolerance on a total of zero admits everything, and totals of zero are
    the modal case in this corpus."""
    assert tau(0) == 0 and tau(1) == 5 and tau(14) == 70
    assert isinstance(tau(3), int)
    assert within_tolerance(1_000, 1_005, 1)
    assert not within_tolerance(1_000, 1_006, 1)


def test_units__zero_total_still_has_a_finite_tolerance() -> None:
    assert within_tolerance(0, 5, 1) and not within_tolerance(0, 6, 1)


# ------------------------------------------------------------------ B3: anchors
def test_anchor__composes_by_weakest_input() -> None:
    """A sum of three deterministic reads and one model-extracted value is
    MODEL_EXTRACTED. Otherwise one extracted number launders itself into a deterministic
    total and the report claims the total was read off the page."""
    det = Anchor(Warrant.DETERMINISTIC, "sha", cell="S!A1")
    mod = Anchor(Warrant.MODEL_EXTRACTED, "sha", cell="S!A2")
    assert compose(det, det, det).warrant is Warrant.DETERMINISTIC
    assert compose(det, det, mod).warrant is Warrant.MODEL_EXTRACTED
    assert compose(det, mod, Anchor(Warrant.DERIVED, "sha")).warrant is Warrant.DERIVED


def test_anchor__composing_nothing_is_not_deterministic() -> None:
    """A value that came from nothing is not read off the page."""
    a = compose()
    assert a.warrant is Warrant.DERIVED and "no inputs" in (a.note or "")


def test_anchor__the_lattice_is_totally_ordered() -> None:
    assert Warrant.DERIVED < Warrant.MODEL_EXTRACTED < Warrant.DETERMINISTIC


# ------------------------------------------------------------------ B1: fact model
def _tiny(**kw) -> FactTable:
    return build(
        filing_cells={("S", "A1"): Decimal("12.34"), ("S", "A2"): "text", ("S", "A3"): None},
        template_cells={("S", "Z1"): "Yes"},
        key_of=lambda sr: f"s.{sr[1].lower()}",
        filing_sha256="f" * 8,
        template_sha256="t" * 8,
        **kw,
    )


def test_fact_table__two_names_only() -> None:
    fields = set(FactTable.__dataclass_fields__)
    assert {"filing", "template"} <= fields
    assert fields - {"filing", "template", "filing_sha256", "template_sha256"} == set(), (
        "a third bound name is a way for a predicate to read something nobody declared"
    )


def test_fact_table__every_leaf_carries_a_cell() -> None:
    ft = _tiny()
    assert ft.filing and ft.template
    for leaf in list(ft.filing.values()) + list(ft.template.values()):
        assert leaf.cell and "!" in leaf.cell


def test_fact_table__a_leaf_without_a_cell_is_refused_at_construction() -> None:
    with pytest.raises(FactError, match="not evidence"):
        Leaf(value=1, unit=Unit.COUNT, cell="", anchor=Anchor(Warrant.DETERMINISTIC, "x"))


def test_fact_table__money_is_scaled_exactly_once() -> None:
    ft = _tiny(money_keys=frozenset({"s.a1"}))
    leaf = ft.filing["s.a1"]
    assert leaf.value == 12_340 and leaf.unit is Unit.MILLI_USD_MILLION
    # and a non-money key of the same value is NOT scaled
    assert _tiny().filing["s.a1"].value == Decimal("12.34")


def test_fact_table__template_is_anchored_to_the_pinned_blank() -> None:
    """The defect it prevents: a filer edits a vocabulary, then satisfies a membership
    check against their own edited vocabulary."""
    ft = _tiny()
    assert ft.template["s.z1"].anchor.source == "t" * 8
    assert ft.filing["s.a1"].anchor.source == "f" * 8
    assert ft.template_sha256 != ft.filing_sha256


def test_fact_table__a_cell_with_no_stable_key_is_dropped() -> None:
    ft = build(
        filing_cells={("S", "A1"): 1, ("S", "B9"): 2},
        template_cells={},
        key_of=lambda sr: None if sr[1] == "B9" else "s.a1",
    )
    assert set(ft.keys()) == {"s.a1"}, "a key nobody induced is a key no predicate can name"


def test_fact_table__derive_uses_the_weakest_input() -> None:
    ft = _tiny()
    assert ft.derive("s.a1", "s.a2").warrant is Warrant.DETERMINISTIC


def test_fact_table__reading_an_unknown_key_raises() -> None:
    with pytest.raises(FactError, match="not in the induced key set"):
        _tiny().leaf("s.nope")


def test_fact_table__serialises_canonically_with_no_float() -> None:
    obj = _tiny(money_keys=frozenset({"s.a1"})).as_canonical_obj()
    blob = canonical_json(obj)
    assert b"__cell__" in blob and b"MILLI_USD_MILLION" in blob


def test_fact_table__has_no_clock_network_or_filesystem_below_build() -> None:
    import ast

    src = (REPO / "src/cdfc/facts/fact_table.py").read_text()
    tree = ast.parse(src)
    banned = {"open", "now", "utcnow", "today", "urlopen", "get", "post", "perf_counter"}
    found = [
        n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
    ]
    assert not (banned & set(found)), f"fact_table reaches {banned & set(found)}"


def test_fact_table__dates_survive_canonicalisation() -> None:
    leaf = Leaf(_dt.date(2026, 8, 12), Unit.DATE, "S!A1", Anchor(Warrant.DETERMINISTIC, "x"))
    assert leaf.as_canonical_obj()["value"] == "2026-08-12"
    canonical_json(leaf.as_canonical_obj())
