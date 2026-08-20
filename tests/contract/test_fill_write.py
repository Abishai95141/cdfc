"""B1 — the fill writer's contract, over the REAL vendored IFSCA blank.

The subject is not that a value lands in a cell. It is that **nothing else changes**: the part list,
the `x14` validations a filer's dropdowns depend on, and every cell the declaration did not name.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import pytest

from cdfc.fill.propose import Derived, FillDeclaration, FillProposal, FillRefusal, Refusal
from cdfc.fill.write import (
    FillWriteError,
    _count_x14,
    _split,
    verify_written,
    write,
    written_values,
)
from cdfc.qualify.surgery import PartsChangedError

BLANK = Path(
    "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)

# Pinned against the vendored blank, 20 Aug 2026. `ci/no-openpyxl-writer.sh` and NC-Q30 cite the
# 19; a round-trip through openpyxl loses every one of them.
FME_PARTS = 42
FME_X14 = 19
FME_CELLS = 6757
FME_XML_PARTS = 22


def _cond(name: str):
    from cdfc.fill.propose import Condition

    return Condition(name, True, "")


def _proposal(ref: str, value: str) -> FillProposal:
    from cdfc.fill.propose import CONDITIONS

    return FillProposal(ref=ref, label="l", value=value, document="src.csv", span=(0, len(value)),
                        page=1, context="ctx", conditions=tuple(_cond(c) for c in CONDITIONS))


@pytest.fixture(scope="module")
def blank():
    if not BLANK.is_file():
        pytest.skip("the vendored FME blank is not in this checkout")
    return BLANK


def _decl(proposed=(), derived=(), attestations=(), surface=None):
    n = len(proposed) + len(derived) + len(attestations)
    return FillDeclaration(template_sha256="t" * 64, surface_total=surface or n,
                           proposed=tuple(proposed), refused=(), attestations=tuple(attestations),
                           derived=tuple(derived))


# --- the pins, which are the denominators every assertion below rests on ---------------------


def test_write__the_blank_carries_the_parts_and_validations_we_pin(blank):
    with zipfile.ZipFile(blank) as z:
        assert len(z.namelist()) == FME_PARTS
        assert _count_x14(z) == FME_X14


def test_write__x14_is_COUNTED_BY_PARSING_not_by_matching_the_tag_name(blank):
    """A byte count of `x14:dataValidation` reports **48** on this blank, because the string occurs
    in the opening tag, the closing tag and the `<x14:dataValidations>` container. The first
    version of the writer's check was that byte count. It never failed, because the invariant it
    guarded — before equals after — held under a wrong number just as well as a right one."""
    with zipfile.ZipFile(blank) as z:
        naive = sum(z.read(n).count(b"x14:dataValidation")
                    for n in z.namelist() if n.endswith(".xml"))
    assert naive == 48
    with zipfile.ZipFile(blank) as z:
        assert _count_x14(z) == FME_X14 == 19


# --- the write ------------------------------------------------------------------------------


def test_write__lands_the_value_and_changes_NOTHING_else(blank, tmp_path):
    out = tmp_path / "filled.xlsx"
    d = _decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),))
    rec = write(d, blank, out)

    v = verify_written(blank, out, rec, expect_validations=FME_X14)
    assert v["parts_before"] == v["parts_after"] == FME_PARTS
    assert v["x14_validations_before"] == v["x14_validations_after"] == FME_X14
    assert v["cells_before"] == v["cells_after"] == FME_CELLS
    assert v["cells_changed"] == v["cells_named"] == 1
    # and the value is READ BACK OUT OF THE FILE, not out of the record
    assert written_values(out, ["1. Introduction!D10"]) == {
        "1. Introduction!D10": "Authorised FME"}


def test_write__opens_clean_and_every_part_reparses(blank, tmp_path):
    """`testzip()` for CRC integrity, then every XML part re-parsed through `xmlsafe`.

    **Deliberately NOT via openpyxl.** `pyproject.toml`'s non-negotiable block sets
    `filterwarnings = ["error"]` precisely so that openpyxl's *"Data Validation extension is not
    supported and will be removed"* cannot be discarded — and reading this workbook raises it,
    because the 19 validations ARE there. The warning firing is evidence the write preserved them;
    using the reader that raises it to prove they survived would be circular and would also fail.
    """
    from cdfc.ingest.xmlsafe import fromstring

    out = tmp_path / "filled.xlsx"
    rec = write(_decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),)), blank, out)
    assert rec.output_sha256 != rec.template_sha256
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None                     # no corrupt entry
        xml = [n for n in z.namelist() if n.endswith(".xml")]
        # MEASURED, not guessed. The first version asserted `>= 30` — a number nobody had counted,
        # in a file whose 42 entries include .rels, .bin and .vml alongside 22 .xml parts.
        assert len(xml) == FME_XML_PARTS
        for n in xml:
            fromstring(z.read(n))                      # every part is well-formed
    assert written_values(out, ["1. Introduction!D10"]) == {
        "1. Introduction!D10": "Authorised FME"}


def test_write__both_lanes_are_written_and_told_apart(blank, tmp_path):
    out = tmp_path / "filled.xlsx"
    d = _decl(
        proposed=(_proposal("1. Introduction!D10", "Authorised FME"),),
        derived=(Derived(ref="1. Introduction!D8", label="Registration Number",
                         value="IFSCA/FME/2026/001", basis="restated from the cover page",
                         supported_by=("r0002",), model="m"),),
    )
    rec = write(d, blank, out)
    c = rec.counts()
    assert c["written_total"] == 2 and c["evidenced"] == 1 and c["derived"] == 1
    lanes = {x.ref: x.lane for x in rec.cells}
    assert lanes["1. Introduction!D10"] == "evidenced"
    assert lanes["1. Introduction!D8"] == "derived"
    # the DERIVED cell carries no span, and that IS the distinction
    assert {x.span for x in rec.cells if x.lane == "derived"} == {None}
    assert verify_written(blank, out, rec)["cells_changed"] == 2
    got = written_values(out, ["1. Introduction!D10", "1. Introduction!D8"])
    assert got["1. Introduction!D8"] == "IFSCA/FME/2026/001"


def test_write__an_attestation_is_NEVER_written(blank, tmp_path):
    """A certification is a natural person accepting liability, and evidence does not change that."""
    from cdfc.fill.propose import Attestation

    out = tmp_path / "filled.xlsx"
    a = Attestation(ref="8. Compliance Status!C6", label="Net worth complied with",
                    supporting=(), certifies="…")
    d = _decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),), attestations=(a,))
    rec = write(d, blank, out)
    assert rec.attestations_left_blank == ("8. Compliance Status!C6",)
    assert "8. Compliance Status!C6" not in {c.ref for c in rec.cells}
    assert verify_written(blank, out, rec)["cells_changed"] == 1


# --- the refusals ---------------------------------------------------------------------------


def test_write__refuses_a_declaration_with_nothing_to_write(blank, tmp_path):
    d = _decl(refused_only=None) if False else FillDeclaration(
        template_sha256="t" * 64, surface_total=1, proposed=(),
        refused=(Refusal("S!A1", "l", FillRefusal.NO_OBSERVATION, "d"),),
        attestations=(), derived=())
    with pytest.raises(FillWriteError, match="nothing to write"):
        write(d, blank, tmp_path / "x.xlsx")


def test_write__refuses_a_cell_the_template_does_not_carry(blank, tmp_path):
    d = _decl(proposed=(_proposal("1. Introduction!ZZ9999", "x"),))
    with pytest.raises(FillWriteError, match="no such cell"):
        write(d, blank, tmp_path / "x.xlsx")


def test_write__refuses_an_unqualified_cell_reference():
    with pytest.raises(FillWriteError, match="not a sheet-qualified"):
        _split("D10")


def test_write__splits_a_sheet_name_on_the_LAST_bang(blank):
    """Gate 126 exists because a left-split silently addressed the wrong sheet at 18 sites."""
    assert _split("Sheet!With!Bang!D10") == ("Sheet!With!Bang", "D10")


# --- THE NEGATIVE CONTROLS: each constructs the failure and asserts it is CAUGHT --------------


def test_nc__write__a_lost_part_is_REFUSED(blank, tmp_path):
    """A writer that drops a part must go RED. Constructed by writing a workbook with one entry
    removed and asking `verify_written` to accept it."""
    out = tmp_path / "lossy.xlsx"
    rec = write(_decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),)),
                blank, tmp_path / "ok.xlsx")
    with zipfile.ZipFile(tmp_path / "ok.xlsx") as src, zipfile.ZipFile(out, "w") as dst:
        names = [n for n in src.namelist() if not n.endswith("sharedStrings.xml")]
        assert len(names) < len(src.namelist()), "the fixture must actually lose a part"
        for n in names:
            dst.writestr(src.getinfo(n), src.read(n))
    with pytest.raises(FillWriteError, match="part list changed"):
        verify_written(blank, out, rec)


def test_nc__write__a_lost_x14_validation_is_REFUSED(blank, tmp_path):
    """The dropdowns are part of the return. Constructed by stripping the x14 block."""
    import re

    out = tmp_path / "novalid.xlsx"
    rec = write(_decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),)),
                blank, tmp_path / "ok.xlsx")
    stripped = 0
    with zipfile.ZipFile(tmp_path / "ok.xlsx") as src, zipfile.ZipFile(out, "w") as dst:
        for n in src.namelist():
            data = src.read(n)
            if n.endswith(".xml") and b"<x14:dataValidations" in data:
                data = re.sub(rb"<x14:dataValidations.*?</x14:dataValidations>", b"", data,
                              flags=re.S)
                stripped += 1
            dst.writestr(src.getinfo(n), data)
    assert stripped, "the fixture must actually strip a validation block"
    with pytest.raises(FillWriteError, match="data validations went from"):
        verify_written(blank, out, rec)


def test_nc__write__a_cell_changed_that_the_record_did_not_name_is_REFUSED(blank, tmp_path):
    """THE ONE A PART-LEVEL CHECK WOULD MISS. The right part is rewritten and the wrong cell in
    it changes; `write_cells`'s guarantee still holds and this must still go red."""
    out = tmp_path / "extra.xlsx"
    rec = write(_decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),)),
                blank, tmp_path / "ok.xlsx")
    # write TWO cells, then verify against a record that names only one
    two = write(_decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),
                                _proposal("1. Introduction!D12", "Trust"))), blank, out)
    assert len(two.cells) == 2
    with pytest.raises(FillWriteError, match="changed but unnamed"):
        verify_written(blank, out, rec)


def test_nc__surgery__write_cells_refuses_a_no_op(blank, tmp_path):
    """A write whose value equals what the cell already holds changes no part, and the writer
    refuses rather than reporting a filled return. Found by running the first fill against an
    already-filled fixture."""
    from cdfc.qualify.surgery import plan_edit, write_cells

    # The BLANK's D10 is empty — it is a blank — so there is no value in it to re-write. Build
    # the no-op the way it actually arose: fill a cell, then write the SAME value into the result.
    filled = tmp_path / "filled.xlsx"
    write(_decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),)), blank, filled)
    assert written_values(filled, ["1. Introduction!D10"]) == {
        "1. Introduction!D10": "Authorised FME"}
    edit = plan_edit(filled, "1. Introduction", "D10", "Authorised FME", operator_id="NOOP")
    with pytest.raises(PartsChangedError, match="parts changed"):
        write_cells(filled, (edit,), tmp_path / "noop.xlsx")


def test_write__is_deterministic(blank, tmp_path):
    """Two writes of the same declaration produce the same bytes. A filled return that differed
    run to run could not be content-addressed, and the registry addresses by digest."""
    d = _decl(proposed=(_proposal("1. Introduction!D10", "Authorised FME"),))
    a = write(d, blank, tmp_path / "a.xlsx")
    b = write(d, blank, tmp_path / "b.xlsx")
    assert a.output_sha256 == b.output_sha256


def test_write__does_not_use_openpyxl_to_WRITE(blank):
    """`ci/no-openpyxl-writer.sh` scopes to `src/cdfc/qualify/`; this module is under `fill/`, so
    the gate does not see it and this control is what stands in for it here."""
    import inspect

    import cdfc.fill.write as m

    src = inspect.getsource(m)
    for banned in (".save(", "Workbook(", "load_workbook"):
        assert banned not in src.replace("`load_workbook`", ""), (
            f"{banned!r} appears in the fill writer; an openpyxl round-trip of this workbook drops "
            "24 parts and all 19 x14 validations"
        )
