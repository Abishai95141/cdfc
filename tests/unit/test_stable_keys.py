"""Stable keys and the structural fingerprint — P2-B3 and P2-B4."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.reader_lxml import _sheet_parts, read  # noqa: E402
from cdfc.ingest.xmlsafe import fromstring  # noqa: E402
from cdfc.schema.fingerprint import structural_fingerprint, structural_projection  # noqa: E402
from cdfc.schema.stable_keys import (  # noqa: E402
    Field,
    StableKey,
    UnresolvedKey,
    bind,
    build_keys,
    collision_census,
)

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
FIX = REPO / "fixtures" / "prescribed"
SYN = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


def _portfolio_text() -> tuple[dict[str, str], set[str], tuple[str, ...]]:
    """Cell text, formula refs and merged ranges for '3. Portfolio'."""
    with zipfile.ZipFile(FME) as z:
        part = next(p for n, _s, p in _sheet_parts(z) if n.strip().startswith("3."))
        root = fromstring(z.read(part))
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(f"{{{M}}}t"))
                      for si in ss.iter(f"{{{M}}}si")]
    text: dict[str, str] = {}
    formulas: set[str] = set()
    for c in root.iter(f"{{{M}}}c"):
        ref = c.get("r", "")
        if c.find(f"{{{M}}}f") is not None:
            formulas.add(ref)
        v = c.findtext(f"{{{M}}}v")
        if c.get("t") == "s" and v is not None and v.isdigit() and int(v) < len(shared):
            text[ref] = shared[int(v)]
        elif v is not None:
            text[ref] = v
        else:
            text[ref] = ""
    merged = tuple(mc.get("ref", "") for mc in root.iter(f"{{{M}}}mergeCell"))
    return text, formulas, merged


# --------------------------------------------------------------------------- B3
def test_stable_keys__row_ordinal_disambiguates() -> None:
    """The measured justification, re-taken rather than remembered.

    Under a naive (sheet, label-above, label-left) key the 100-row tables repeat the same
    label pair on every row and most cells collide. The ordinal is arithmetic over the
    table's own rows, and it disambiguates completely.
    """
    text, _f, _m = _portfolio_text()
    naive_collisions, total = collision_census(cell_text=text, with_ordinal=False)
    ordinal_collisions, total2 = collision_census(cell_text=text, with_ordinal=True)
    assert total == total2 and total > 1000
    assert naive_collisions > total * 0.5, (
        f"only {naive_collisions} of {total} collide without the ordinal; the ordinal's "
        "justification does not hold on this sheet"
    )
    assert ordinal_collisions == 0, f"{ordinal_collisions} collisions survive the ordinal"


def test_stable_keys__a_key_is_not_a_coordinate() -> None:
    """The coordinate is a RESOLVED ATTRIBUTE, never the identity."""
    text, formulas, merged = _portfolio_text()
    fields = build_keys(sheet="3. Portfolio", cell_text=text, unlocked=set(),
                        formula_refs=formulas, merged_ranges=merged)
    assert fields
    for key in fields:
        assert not key.replace(".", "").replace("_", "").isalnum() or "row[" in key
        assert "!" not in key, "a key must not embed a sheet-qualified coordinate"


def test_stable_keys__unresolved_blocks_its_predicates() -> None:
    """UNRESOLVED never degrades to a guess — a guess is how a predicate comes to pass
    against the wrong cell."""
    f = Field("portfolio.x.row[7].total", None, "UNRESOLVED", "TEXT", True, False, True)
    with pytest.raises(UnresolvedKey, match="does not run"):
        bind(f)
    ok = Field("portfolio.x.row[7].total", "O7", "RESOLVED", "TEXT", True, False, True)
    assert bind(ok) == "O7"


def test_stable_keys__key_renders_the_documented_shape() -> None:
    k = StableKey("3. Portfolio", ("Table 3.1",), "Total value", 7)
    assert str(k) == "3_portfolio.table_3_1.row[7].total_value"


def test_stable_keys__a_row_insertion_does_not_silently_rebind() -> None:
    """THE PROPERTY. Under a row insertion every key must resolve to the CORRECT new
    reference or refuse — never to a different label pair.

    A coordinate-shaped key rebinds silently here, and the predicate goes on passing
    against a different cell with nothing in the output to say so.
    """
    shifted = SYN / "row-inserted__portfolio-r7.xlsx"
    assert shifted.exists(), "run tools/fixtures/make_synthetic.py"
    text, formulas, merged = _portfolio_text()
    before = build_keys(sheet="3. Portfolio", cell_text=text, unlocked=set(),
                        formula_refs=formulas, merged_ranges=merged)

    with zipfile.ZipFile(shifted) as z:
        part = next(p for n, _s, p in _sheet_parts(z) if n.strip().startswith("3."))
        root = fromstring(z.read(part))
    after_text = {c.get("r", ""): (c.findtext(f"{{{M}}}v") or "") for c in root.iter(f"{{{M}}}c")}

    # Every key that still resolves must point at a reference that EXISTS in the shifted
    # document. A key resolving to a coordinate that no longer exists is the silent
    # rebind this design refuses.
    dangling = [
        k for k, f in before.items()
        if f.resolution_state == "RESOLVED" and f.resolved_ref not in after_text
    ]
    assert dangling, (
        "no key was affected by the row insertion — the fixture did not shift anything, "
        "so this property is untested"
    )
    for k in dangling[:20]:
        assert "row[" in k, f"{k} carries no ordinal and would rebind silently"


# --------------------------------------------------------------------------- B4
def test_fingerprint__is_stable_under_value_edits() -> None:
    """A filer writing values must not change the template binding."""
    assert structural_fingerprint(FME) == structural_fingerprint(SYN / "values-written__50-cells.xlsx")


def test_fingerprint__is_stable_under_a_formula_overwrite() -> None:
    """THE LOAD-BEARING EXCLUSION.

    A filer who overwrote a formula cell with a literal must fail a PREDICATE
    (TEMPLATE_DIFF, the flagship check), not the BINDING. If formula content entered the
    fingerprint, that filing would be reported `invalid.template_unbound` — an apparatus
    failure about us instead of a finding about the filing.
    """
    ov = SYN / "formula-overwritten__portfolio-O7.xlsx"
    assert structural_fingerprint(FME) == structural_fingerprint(ov)
    assert len(read(FME).formulas) - len(read(ov).formulas) == 1, (
        "the fixture must overwrite exactly one formula cell"
    )


def test_fingerprint__moves_on_a_row_insertion() -> None:
    assert structural_fingerprint(FME) != structural_fingerprint(SYN / "row-inserted__portfolio-r7.xlsx")


def test_fingerprint__excludes_formula_content_structurally() -> None:
    """Asserted on the projection, not inferred from a hash collision."""
    proj = structural_projection(FME)
    assert set(proj) == {"sheets", "merged_ranges", "defined_names", "unlocked_mask"}
    blob = repr(proj)
    assert "SUM(" not in blob and "COUNTIF(" not in blob, "formula text reached the fingerprint"


def test_fingerprint__is_deterministic() -> None:
    assert structural_fingerprint(FME) == structural_fingerprint(FME)
