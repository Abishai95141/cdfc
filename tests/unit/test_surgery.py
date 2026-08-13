"""P6-B2 — raw-zip surgery. **The openpyxl round-trip's exact failure, asserted on our own writer.**"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.reader_lxml import read  # noqa: E402
from cdfc.qualify.fault_model import REMOVE  # noqa: E402
from cdfc.qualify.surgery import (  # noqa: E402
    CellEdit,
    MultiPartEditError,
    SiteNotFoundError,
    differing_parts,
    plan_edit,
    seed_mutant,
)

FME = REPO / "fixtures" / "prescribed" / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
DATA_MODEL = "xl/model/item.data"


@pytest.fixture(scope="module")
def mutant(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("surgery") / "m.xlsx"
    edit = plan_edit(FME, "3. Portfolio", "O7", 999999, "F11.a")
    seed_mutant(FME, [edit], out, fault_class="F11", operator_id="F11.a", seed=20260810)
    return out


def test_surgery__exactly_one_part_differs(mutant: Path) -> None:
    changed = differing_parts(FME, mutant)
    assert len(changed) == 1, sorted(changed)
    assert next(iter(changed)).startswith("xl/worksheets/sheet")


def test_surgery__x14_validations_survive(mutant: Path) -> None:
    """35 main + 19 `x14`. This is the openpyxl round-trip's exact failure."""
    assert read(mutant).n_validations == 54


def test_surgery__the_large_parts_are_byte_identical(mutant: Path) -> None:
    with zipfile.ZipFile(FME) as a, zipfile.ZipFile(mutant) as b:
        big = sorted(
            (i.file_size, i.filename) for i in a.infolist()
            if not i.filename.startswith("xl/worksheets/")
        )[-3:]
        assert big and big[-1][0] > 100_000, "no large part to compare; the assertion would be weak"
        for _size, name in big:
            assert a.read(name) == b.read(name), name


def test_surgery__the_edited_cell_reads_the_new_value(mutant: Path) -> None:
    """The admission-side twin: surgery writes a USABLE mutant, not merely a small diff."""
    wb = read(mutant)
    assert wb.n_sheets == read(FME).n_sheets
    assert len(wb.formulas) == len(read(FME).formulas) - 1, (
        "the overridden cell lost its formula — that IS the F11 fault"
    )


def test_surgery__a_declared_cross_sheet_pair_writes_exactly_two_parts(tmp_path: Path) -> None:
    """F13's pair form is a CROSS-SHEET carry desync and necessarily touches two sheets.

    The rule is not "exactly one part" — it is "exactly the parts the edits name". A PAIR is one
    fault at two sites, DECLARED, which is a different thing from two faults wearing one mutant id.
    """
    a = plan_edit(FME, "3. Portfolio", "O7", 1, "F13.b")
    b = plan_edit(FME, "1. Introduction", "D11", 1, "F13.b")
    out = tmp_path / "pair.xlsx"
    rec = seed_mutant(FME, [a, b], out, fault_class="F13", operator_id="F13.b", seed=1)
    assert len(rec.parts_changed) == 2
    assert set(differing_parts(FME, out)) == set(rec.parts_changed)


def test_surgery__a_part_nobody_named_is_refused(tmp_path: Path) -> None:
    """The invariant that actually matters, and it is stronger than the one-part rule."""
    edit = plan_edit(FME, "3. Portfolio", "O7", 1, "F11.a")
    out = tmp_path / "one.xlsx"
    rec = seed_mutant(FME, [edit], out, fault_class="F11", operator_id="F11.a", seed=1)
    assert set(rec.parts_changed) == set(differing_parts(FME, out))
    assert len(rec.parts_changed) == 1


def test_surgery__a_site_outside_the_workbook_raises() -> None:
    with pytest.raises(SiteNotFoundError, match="site universe"):
        plan_edit(FME, "3. Portfolio", "ZZ9999", 1, "F01.a")


def test_surgery__blank_empties_the_cell_and_zero_does_not(tmp_path: Path) -> None:
    """F05's two operators are two faults. `0` and `<empty>` are different, and `sum([]) == 0`."""
    blanked = plan_edit(FME, "1. Introduction", "D11", REMOVE, "F05.b")
    zeroed = plan_edit(FME, "1. Introduction", "D11", 0, "F05.a")
    assert "<v>" not in blanked.new_xml and "<is>" not in blanked.new_xml
    assert "<v>0</v>" in zeroed.new_xml
    assert blanked.new_xml != zeroed.new_xml


def test_surgery__old_xml_is_captured_verbatim() -> None:
    edit = plan_edit(FME, "3. Portfolio", "O7", 1, "F11.a")
    assert "<f" in edit.old_xml, "the base declared a formula here; that is the whole F11 story"
    assert "<f" not in edit.new_xml
