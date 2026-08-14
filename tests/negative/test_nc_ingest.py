"""P1 negative controls — NC-P01..P08.

The matrix reports 72/72 AGREE. That number is worth nothing unless the instrument that
produced it has been observed reporting something else, so the first test here perturbs a
reader and asserts the cell escalates. A 100% agreement from a comparator that cannot
disagree is the vacuous pass, in a measurement.
"""

from __future__ import annotations

import ast
import sys
import zipfile
from contextlib import closing
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest import reader_lxml as A  # noqa: E402
from cdfc.ingest import reader_lxml_b as AP  # noqa: E402
from cdfc.ingest import reader_openpyxl as B  # noqa: E402
from cdfc.ingest.agreement import Label, compare  # noqa: E402
from cdfc.ingest.competence import Instrument  # noqa: E402
from cdfc.verdict.invalid import InvalidCause  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


# --------------------------------------------------------------------------- NC-P01
def test_nc__P01_the_matrix_can_report_a_structural_disagreement() -> None:
    """THE control on the measurement itself.

    72/72 AGREE is only evidence if the comparator has been seen to disagree. Perturb one
    reader's structural view and assert the cell escalates AND the run becomes INVALID.
    """
    a = A.agreement_view(A.read(FME))
    ap = dict(AP.agreement_view(AP.read_b(FME)))
    ap["n_sheets"] = a["n_sheets"] + 1  # a reader that miscounts sheets

    ag = compare("7d9a1960", {Instrument.A: a, Instrument.A_PRIME: ap})
    cell = ag.by_field("n_sheets")[0]
    assert cell.label is Label.DISAGREE_ESCALATED, f"got {cell.label}"
    assert ag.invalid_cause is InvalidCause.READER_STRUCTURAL_DISAGREEMENT
    assert cell.second_party, "a non-AGREE cell must name its second party"


def test_nc__P01b_the_unperturbed_matrix_agrees() -> None:
    """Admission-side twin: without the perturbation the same cell is AGREE."""
    a = A.agreement_view(A.read(FME))
    ap = AP.agreement_view(AP.read_b(FME))
    ag = compare("7d9a1960", {Instrument.A: a, Instrument.A_PRIME: ap})
    assert ag.by_field("n_sheets")[0].label is Label.AGREE
    assert ag.invalid_cause is None


# --------------------------------------------------------------------------- NC-P02
def test_nc__P02_an_unmeasured_competence_is_never_AGREE() -> None:
    """A field whose exclusion was measured elsewhere may not be compared here.

    Without this rule the matrix classifies unmeasured cells from a judgment taken on one
    workbook and reports them as agreement.
    """
    from cdfc.ingest import competence as C

    saved = C.COMPETENCE["n_validations"]
    C.COMPETENCE["n_validations"] = C.Competence(saved.parties, frozenset({"deadbeef"}))
    try:
        a = A.agreement_view(A.read(FME))
        ap = AP.agreement_view(AP.read_b(FME))
        ag = compare("7d9a1960", {Instrument.A: a, Instrument.A_PRIME: ap})
        cell = ag.by_field("n_validations")[0]
        assert cell.label is Label.NOT_COMPARABLE
        assert cell.mechanism == "competence_unmeasured"
    finally:
        C.COMPETENCE["n_validations"] = saved


# --------------------------------------------------------------------------- NC-P03
def test_nc__P03_readers_A_and_A_prime_are_not_the_same_traversal() -> None:
    """A' must not be a refactor of A: a shared traversal bug is the only way two
    readings can be wrong together."""
    a_src = (REPO / "src/cdfc/ingest/reader_lxml.py").read_text()
    ap_src = (REPO / "src/cdfc/ingest/reader_lxml_b.py").read_text()
    assert "_sheet_parts" in a_src and "workbook.xml.rels" in a_src, "A walks the rel graph"
    assert "[Content_Types].xml" in ap_src, "A' must enumerate parts from [Content_Types].xml"
    assert 'z.read("xl/_rels/workbook.xml.rels")' not in ap_src, (
        "A' reads the relationship graph — it has become a refactor of A and the two "
        "readings no longer fail independently"
    )


# --------------------------------------------------------------------------- NC-P04
CORE_MODULES = (
    "cdfc.ingest.reader_lxml",
    "cdfc.ingest.reader_lxml_b",
    "cdfc.ingest.container_guard",
    "cdfc.canon",
)


def test_nc__P04_no_reader_re_serialises_the_artifact() -> None:
    """The static tooth. openpyxl's round-trip is destructive on these workbooks, so a
    write-mode ZipFile and any save/write call must be unreachable from the readers."""
    offenders = []
    for mod in CORE_MODULES:
        path = REPO / "src" / (mod.replace(".", "/") + ".py")
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if name == "ZipFile":
                for kw in list(node.args[1:]) + [k.value for k in node.keywords]:
                    if isinstance(kw, ast.Constant) and kw.value in ("w", "a", "x"):
                        offenders.append(f"{mod}: ZipFile opened for writing")
            if name in {"save", "writestr", "write_bytes", "write_text"}:
                offenders.append(f"{mod}: calls {name}()")
    assert not offenders, f"a reader can modify the artifact: {offenders}"


def test_nc__P04_runtime_the_blob_is_unchanged_after_every_reader(tmp_path: Path) -> None:
    """The runtime tooth: the blob digest is identical after all three readers have run."""
    import hashlib
    import shutil

    blob = tmp_path / "f.xlsx"
    shutil.copy(FME, blob)
    before = hashlib.sha256(blob.read_bytes()).hexdigest()
    A.read(blob)
    AP.read_b(blob)
    B.read_formula_text_and_cached(blob)
    assert hashlib.sha256(blob.read_bytes()).hexdigest() == before, (
        "a reader modified the received artifact"
    )


def test_nc__P04_golden_the_round_trip_really_is_destructive(tmp_path: Path) -> None:
    """The pinned twin: the README's number gets a script behind it rather than a memory."""
    import warnings

    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with closing(openpyxl.load_workbook(FME)) as wb:
            out = tmp_path / "roundtripped.xlsx"
            wb.save(out)

    before_bytes = FME.stat().st_size
    after_bytes = out.stat().st_size
    before_x14 = sum(1 for v in A.read(FME).validations if v.namespace == "x14")
    after_x14 = sum(1 for v in A.read(out).validations if v.namespace == "x14")

    assert before_bytes == 3_663_391, before_bytes
    assert after_bytes < before_bytes // 10, f"expected a catastrophic shrink, got {after_bytes}"
    assert before_x14 == 19, before_x14
    assert after_x14 == 0, f"expected all 19 x14 validations destroyed, {after_x14} survived"


# --------------------------------------------------------------------------- NC-P08
def test_nc__P08_only_one_parser_factory() -> None:
    """lxml is reached through ONE door: `xmlsafe.fromstring`.

    NC-P05a spies on `xmlsafe.fromstring` to prove the guard ran before any parse, and a spy can
    only watch one door.

    **THIS WAS A TWO-STRING SUBSTRING CHECK AND IT IS NOW AN AST WALK, which is what the module
    docstring always said it was.** The check looked for the literals `etree.XMLParser(` and
    `etree.fromstring(`, so a second door opened under any other name went straight past it:

        from lxml import etree as ET
        ET.fromstring(b, parser=ET.XMLParser(resolve_entities=True, recover=True))

    — including `recover=True`, which `xmlsafe`'s own docstring calls the setting that matters
    most. The committed injector plants the exact literal spelling the substring matched, so the
    control was observed red only on the shape of its own check.

    The walk resolves lxml under ANY alias: it tracks what `lxml`, `lxml.etree` and their members
    were bound to in each module, then flags a call whose receiver resolves to lxml's `etree`.
    """
    import ast

    # THE PARSING SURFACE, and only it. `tostring`, `SubElement` and `Element` BUILD XML; they
    # cannot expand an entity or recover from malformed input, which is what the hardened factory
    # exists to control. `surgery.py` and `corpus/_writer.py` legitimately serialise, and they are
    # governed by `ci/no-openpyxl-writer.sh` and `ci/no-regex-over-xml.sh` instead. A control that
    # flagged them would be red for a reason unrelated to its own subject.
    PARSERS = frozenset({"fromstring", "fromstringlist", "XML", "parse", "XMLParser", "iterparse"})

    offenders: list[str] = []
    for path in sorted((REPO / "src" / "cdfc").rglob("*.py")):
        if path.name == "xmlsafe.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))

        # A local name bound to lxml's `etree` module, under any alias.
        module_alias: set[str] = set()
        # A local name bound to a MEMBER of it, mapped to the member's ORIGINAL name — so
        # `from lxml.etree import fromstring as _fs` is `_fs -> fromstring`.
        member_alias: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name in ("lxml.etree", "lxml"):
                        module_alias.add(a.asname or a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith("lxml"):
                for a in node.names:
                    if a.name == "etree":
                        module_alias.add(a.asname or a.name)
                    else:
                        member_alias[a.asname or a.name] = a.name

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr in PARSERS:
                # `X.fromstring(...)` / `X.etree.fromstring(...)` where X resolves to lxml
                root = fn.value
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name) and root.id in module_alias:
                    offenders.append(f"{path.relative_to(REPO)}:{node.lineno}: {fn.attr}(...)")
            elif isinstance(fn, ast.Name) and member_alias.get(fn.id) in PARSERS:
                # `from lxml.etree import fromstring [as _fs]` then a bare call
                offenders.append(f"{path.relative_to(REPO)}:{node.lineno}: {fn.id}(...)")

    assert not offenders, (
        f"lxml is reached outside the single hardened factory: {offenders}. "
        "Every parse goes through `xmlsafe.fromstring` or the spy in NC-P05a watches a door "
        "nobody uses."
    )


# --------------------------------------------------------------------------- NC-P05
def test_nc__P05b_the_hardened_parser_neutralises_an_external_entity() -> None:
    """And the UNHARDENED parser leaks — otherwise the control discriminates nothing.

    The first version of this fixture put the entity in an ATTRIBUTE, where lxml refuses
    it regardless of configuration; hardened and unhardened behaved identically and the
    control proved nothing. The entity is in element text for that reason.
    """
    from lxml import etree

    from cdfc.ingest import xmlsafe

    adv = REPO / "fixtures" / "adversarial" / "xxe-entity__passwd.xlsx"
    with zipfile.ZipFile(adv) as _z:
        raw = _z.read("xl/workbook.xml")
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

    el = xmlsafe.fromstring(raw)
    hardened = (el.find(f".//{ns}sheet").text or "")
    assert "root:" not in hardened and "/bin/" not in hardened, (
        "the hardened parser expanded an external entity"
    )

    unhardened_el = etree.fromstring(
        raw, parser=etree.XMLParser(resolve_entities=True, load_dtd=True, no_network=False)
    )
    leaked = unhardened_el.find(f".//{ns}sheet").text or ""
    if not leaked.strip():
        pytest.skip("no readable /etc/passwd here; the control cannot discriminate on this platform")
    assert leaked != hardened, (
        "hardened and unhardened parsers behaved identically — the control discriminates nothing"
    )


def test_nc__P05c_a_guard_trip_is_a_run_level_cause_not_a_cell_reason() -> None:
    from cdfc.ingest.container_guard import GuardTrip, guard

    adv = REPO / "fixtures" / "adversarial" / "zipbomb-ratio__x1000.xlsx"
    with pytest.raises(GuardTrip) as ei:
        guard(adv)
    assert ei.value.cause is InvalidCause.CONTAINER_GUARD_TRIPPED
    assert str(ei.value.cause).startswith("invalid."), "a guard trip must be a run-level cause"
