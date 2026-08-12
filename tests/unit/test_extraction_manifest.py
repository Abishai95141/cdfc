"""The extraction manifest is an output, not a log."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import canonical_json  # noqa: E402
from cdfc.ingest.manifest import (  # noqa: E402
    Construct,
    ExtractionManifest,
    SkipWithoutReason,
    build,
    scan_constructs,
)
from cdfc.ingest.xmlsafe import fromstring  # noqa: E402

FME = REPO / "fixtures" / "prescribed" / (
    "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)
M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
X14 = "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main"


def test_manifest__every_skipped_part_has_a_reason() -> None:
    """A skip with no reason is indistinguishable from a part nobody looked at."""
    with pytest.raises(SkipWithoutReason, match="no reason"):
        build(reader="A", parts_read=(), parts_skipped=[("xl/media/image1.png", "")])


def test_manifest__a_skip_with_a_reason_is_accepted() -> None:
    m = build(reader="A", parts_read=("xl/workbook.xml",),
              parts_skipped=[("xl/media/image1.png", "binary media, no cells")])
    assert m.parts_skipped[0][1]


def test_manifest__unknown_qname_is_recorded() -> None:
    """Raw-zip surgery: inject a synthetic element and assert it surfaces with its count
    and first reference."""
    xml = (
        f'<worksheet xmlns="{M}" xmlns:foo="urn:example:foo">'
        f'<sheetData><row r="1"><c r="A1"><v>1</v></c></row></sheetData>'
        f'<foo:bar ref="A1"/><foo:bar ref="B2"/></worksheet>'
    ).encode()
    constructs, ns = scan_constructs("xl/worksheets/sheet1.xml", fromstring(xml))
    q = [c for c in constructs if c.qname.endswith("}bar")]
    assert q, f"the synthetic construct was not recorded: {constructs}"
    assert q[0].count == 2
    assert q[0].first_ref == "A1"
    assert "urn:example:foo" in ns


def test_manifest__the_real_workbook_declares_its_namespaces() -> None:
    with zipfile.ZipFile(FME) as z:
        root = fromstring(z.read("xl/worksheets/sheet1.xml"))
    _, ns = scan_constructs("xl/worksheets/sheet1.xml", root)
    assert M in ns


def test_manifest__x14_namespace_is_seen_on_the_sheet_that_carries_it() -> None:
    """FME is the only workbook with an x14 extension block, and it is the namespace
    openpyxl discards."""
    with zipfile.ZipFile(FME) as z:
        found = False
        for n in z.namelist():
            if not n.startswith("xl/worksheets/sheet"):
                continue
            _, ns = scan_constructs(n, fromstring(z.read(n)))
            if X14 in ns:
                found = True
                break
    assert found, "the x14 namespace was not seen anywhere in the FME workbook"


def test_contract__manifest_is_not_a_log() -> None:
    """Frozen, canonically serialisable, and no free text outside a skip reason."""
    m = build(
        reader="reader_lxml",
        parts_read=("xl/workbook.xml",),
        parts_skipped=[("xl/media/i.png", "binary media")],
        namespaces_seen=(M,),
        constructs_not_understood=(Construct("xl/worksheets/sheet1.xml", "{urn:x}y", 1, "A1"),),
    )
    with pytest.raises((AttributeError, TypeError)):
        m.reader = "someone else"  # type: ignore[misc]
    blob = canonical_json(m.as_canonical_obj())
    assert blob.startswith(b"{")
    # the only free-text field is the per-skip reason
    fields = set(ExtractionManifest.__dataclass_fields__)
    assert fields == {"reader", "parts_read", "parts_skipped", "namespaces_seen",
                      "constructs_not_understood", "guard"}


def test_contract__two_manifests_are_distinct() -> None:
    a = build(reader="reader_lxml", parts_read=("x",))
    b = build(reader="reader_lxml_b", parts_read=("x",))
    assert canonical_json(a.as_canonical_obj()) != canonical_json(b.as_canonical_obj())


def test_nc__P10_unknown_construct_must_surface() -> None:
    """NC-P10: the residue field must be non-empty when a construct really is unmodelled.

    ITS DECLARED LIMIT, stated here rather than assumed away: this list contains only
    what we knew to look for. A construct in a namespace we never enumerate is invisible
    to it. P1 makes the residue visible; it does not close it.
    """
    xml = f'<worksheet xmlns="{M}" xmlns:zz="urn:zz"><zz:mystery/></worksheet>'.encode()
    constructs, _ = scan_constructs("p", fromstring(xml))
    assert any(c.qname == "{urn:zz}mystery" for c in constructs)
