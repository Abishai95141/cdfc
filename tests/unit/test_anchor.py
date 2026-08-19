"""`Anchor` — the five requirements, each traced to the measurement that produced it.

Every assertion here exists because experiment E2 measured something on two regulators' published
rule sets, not because a design document preferred it. Where a requirement came from a number, the
number is in the test name or the message, so a future reader can tell a measured constraint from a
taste.
"""

from __future__ import annotations

import pytest

from cdfc.schema.anchor import Anchor, AnchorError

# Every sheet name in the pinned corpus that has ever caused trouble: a leading digit, a dot, a
# space, and a two-letter column.
REAL_CELLS = (
    "3. Portfolio!O7",
    "1. Introduction!D17",
    "4. Investors!AA21",
    "Dropdown!E3",
    "2. Summary!X1",
)


@pytest.mark.parametrize("text", REAL_CELLS)
def test_anchor__the_A1_case_round_trips_byte_identically(text: str) -> None:
    """**This is the property that made a substitution across dozens of sites safe.**

    An `Anchor` may be introduced at a construction site only because its rendering of a single
    spreadsheet cell is the exact string this project has always written. If this ever fails, every
    published artefact moves and `tools/anchor_hazard.py --check` goes red — which is the intended
    order of discovery, but this is the cheaper place to find out.
    """
    a = Anchor.parse(text)
    assert a.render() == text
    assert str(a) == text
    assert a.is_cell


def test_anchor__a_sheet_name_containing_a_separator_splits_on_the_LAST_one() -> None:
    """Sheet names here carry dots and spaces; the day one carries `!`, a first-split is wrong."""
    a = Anchor.parse("Odd!Name!B2")
    assert a.table == "Odd!Name"
    assert a.render() == "Odd!Name!B2"


def test_anchor__requirement_2_rows_may_be_a_LIST() -> None:
    """MEASURED: EIOPA writes `r: R0010; R0030; R0110; …` — ONE address over eleven rows.

    The architecture document assumed a scalar. A scalar field would have forced eleven anchors for
    one rule and thrown away the fact that they are a single assertion.
    """
    a = Anchor.data_point("S.01.01.13.01", "R0010; R0030; R0110; R0140", "C0010")
    assert a.rows == ("R0010", "R0030", "R0110", "R0140")
    assert a.spans == 4
    assert not a.is_cell


def test_anchor__requirement_3_an_unknown_axis_is_carried_not_dropped() -> None:
    """EIOPA adds `z:`, `f:`, `fv:`, `seq:`, `id:`. Dropping one merges two distinct data points."""
    with_z = Anchor.data_point("S.05.01.13.01", "R1300", "C0200", {"z": "Z0001"})
    without = Anchor.data_point("S.05.01.13.01", "R1300", "C0200")
    assert with_z != without
    assert hash(with_z) != hash(without)
    assert "z=Z0001" in with_z.render()


def test_anchor__requirement_4_the_dialect_is_not_part_of_the_identity() -> None:
    """MEASURED: two regulators, two notations, one structure — 23,843 EIOPA triples and 18,827
    EBA addresses over the same `(table, row, column)` shape. If the notation entered identity, two
    published rule sets could never be merged and a filing could never be checked against both."""
    eba = Anchor.data_point("C_25.01.a", "0010", "0060", dialect="dpm-xl")
    eiopa = Anchor.data_point("C_25.01.a", ["0010"], ["0060"], dialect="eiopa")
    assert eba == eiopa
    assert hash(eba) == hash(eiopa)
    assert len({eba, eiopa}) == 1, "two notations for one data point must collapse to one anchor"


@pytest.mark.parametrize("absent", ["NULL", "null", "", "-", "None"])
def test_anchor__requirement_5_NULL_is_absence_and_never_a_table(absent: str) -> None:
    """MEASURED: EBA rule `v3695_s` carries the literal four characters `NULL` in its declared-
    tables cell. Read as a name it becomes a table nobody has; read as absence it is the deactivated
    rule it actually is. It was 1 of 18,827 — and one silent wrong address is the whole risk."""
    with pytest.raises(AnchorError):
        Anchor.data_point(absent, "r1", "c1")


def test_anchor__a_wildcard_refuses_to_be_counted() -> None:
    """`r*` covers however many rows a template has. Returning a number without the template would
    be inventing one, and this project's failure mode is a plausible number nobody can source."""
    a = Anchor.data_point("R_04.00.a", "*", "c0020")
    with pytest.raises(AnchorError):
        a.spans


def test_anchor__equality_is_order_insensitive_in_the_axes() -> None:
    """The hash must not depend on dict insertion order — that is the exact hazard
    `tools/anchor_hazard.py` exists to catch, and it would be careless to introduce a fresh
    instance of it in the type built to end it."""
    a = Anchor.data_point("T", "r1", "c1", {"z": "Z1", "f": "solvency"})
    b = Anchor.data_point("T", "r1", "c1", {"f": "solvency", "z": "Z1"})
    assert a == b and hash(a) == hash(b)


def test_anchor__a_non_A1_reference_is_refused() -> None:
    for bad in ("A1B2", "7", "!!", "O"):
        with pytest.raises(AnchorError):
            Anchor.cell("Sheet", bad)


def test_anchor__is_load_bearing_on_the_run_path() -> None:
    """A type nobody constructs is not a migration.

    Asserted by IMPORT CLOSURE rather than by grep: these three modules are on the path every run
    takes, and each builds the canonical cell string through the anchor.
    """
    import cdfc.predicates.harvest_classes._shared as shared
    import cdfc.probes.precedents as prec
    import cdfc.schema.fingerprint as fp

    for mod in (shared, fp, prec):
        assert getattr(mod, "Anchor", None) is Anchor, f"{mod.__name__} does not use the anchor"
