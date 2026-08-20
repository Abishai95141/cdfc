"""P6-B2 — raw-zip surgery. **The only sanctioned mutant writer.**

Every zip entry is copied byte-for-byte with its original compression parameters, and exactly one
`xl/worksheets/sheetN.xml` is rewritten. **This is the method and not a convenience**, and the
property it preserves is MEASURED: the 3.55 MB data-model part and all 19 `x14` data validations
survive byte-identical. An openpyxl round-trip loses 24 parts and every `x14` validation, so a
campaign whose mutants went through one would be measuring **the writer** rather than the fault —
`U/G` would collapse to zero and every `K/O` would be wrong in the direction that flatters us.
That is NC-Q30, and `ci/no-openpyxl-writer.sh` is the gate.

**The worksheet XML is PARSED, never pattern-matched.** `ci/no-regex-over-xml.sh` exists because a
pattern over this format returned a correct count with wrong contents three times in this project,
most recently by producing malformed XML that LibreOffice "repaired" by dropping 424 of 505
formulas.

**The rule is not "exactly one part". It is "exactly the parts the edits name."**

The first version required one worksheet, and it was wrong for the class the whole design is built
around: **F13's pair form is a CROSS-SHEET carry desync** — both ends of a carry moved by the same
amount so every cross-sheet equality still holds — and it necessarily touches two sheets. The
campaign surfaced it as a `MultiPartEditError` 200 mutants in.

The invariant that actually matters is **no part changes that no edit named**. That is strictly
stronger than the one-part rule for the single-cell case, and correct for the pair case: a PAIR is
*one fault at two sites, declared*, which is a different thing from two faults wearing one mutant
id. `parts_changed` is compared against the parts the edits name, not against the number 1.
"""

from __future__ import annotations

import copy
import hashlib
import zipfile
from functools import lru_cache
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from lxml import etree

from cdfc.schema.anchor import Anchor
from cdfc.ingest.reader_lxml import _sheet_parts
from cdfc.ingest.xmlsafe import fromstring
from cdfc.qualify.fault_model import FAULT_MODEL_VERSION, HARNESS_VERSION, REMOVE

M: Final[str] = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS: Final[str] = f"{{{M}}}"


class SurgeryError(Exception):
    """A mutant that must not be written."""


class MultiPartEditError(SurgeryError):
    """A part changed that no edit named — or an edit named a part that did not change."""


class SiteNotFoundError(SurgeryError):
    """The cell the edit names does not exist in the base workbook.

    Never created silently: a mutant seeded at a cell the template does not carry is a mutant whose
    site is outside the universe, and the site universe is what `K/O`'s denominator rests on.
    """


@dataclass(frozen=True, slots=True)
class CellEdit:
    sheet_name: str
    ref: str
    old_xml: str
    new_xml: str
    operator_id: str

    def as_row(self) -> dict[str, Any]:
        return {
            "sheet_name": self.sheet_name, "ref": self.ref,
            "old_xml": self.old_xml, "new_xml": self.new_xml, "operator_id": self.operator_id,
        }


@dataclass(frozen=True, slots=True)
class MutantRecord:
    mutant_sha256: str
    base_sha256: str
    fault_class: str
    operator_id: str
    edits: tuple[CellEdit, ...]
    seed: int
    harness_version: str
    fault_model_version: str
    parts_changed: tuple[str, ...]
    path: Path | None = field(default=None, compare=False)

    @property
    def sites(self) -> tuple[str, ...]:
        return tuple(Anchor.cell(e.sheet_name, e.ref).render() for e in self.edits)

    def as_row(self) -> dict[str, Any]:
        return {
            "mutant_sha256": self.mutant_sha256,
            "base_sha256": self.base_sha256,
            "fault_class": self.fault_class,
            "operator_id": self.operator_id,
            "seed": self.seed,
            "harness_version": self.harness_version,
            "fault_model_version": self.fault_model_version,
            "parts_changed": list(self.parts_changed),
            "sites": list(self.sites),
            "edits": [e.as_row() for e in self.edits],
        }


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@lru_cache(maxsize=4)
def _sheet_root(blob_str: str, sheet: str, _stamp: tuple[int, int]) -> Any:
    with zipfile.ZipFile(blob_str) as z:
        return fromstring(z.read(_part_for(z, sheet)))


def plan_edit(base: Path, sheet: str, ref: str, new_value: Any, operator_id: str) -> CellEdit:
    """Build one `CellEdit`, capturing the `<c>` element AS FOUND.

    `old_xml` is verbatim so a reviewer can see exactly what the base carried — including whether
    the cell held a formula, which is the whole content of an F11 override.
    """
    st = base.stat()
    root = _sheet_root(str(base), sheet, (st.st_size, st.st_mtime_ns))
    for c in root.iter(f"{NS}c"):
        if c.get("r") != ref:
            continue
        old = etree.tostring(c, encoding="unicode")
        new_el = _mutate_element(c, new_value)
        return CellEdit(sheet, ref, old, etree.tostring(new_el, encoding="unicode"), operator_id)
    raise SiteNotFoundError(
        f"{sheet}!{ref} does not exist in {base.name}. A mutant seeded outside the workbook is a "
        "mutant outside the site universe, and the universe is what K/O's denominator rests on."
    )


def _part_for(z: zipfile.ZipFile, sheet: str) -> str:
    for name, _state, part in _sheet_parts(z):
        if name == sheet:
            return part
    raise SiteNotFoundError(f"no worksheet named {sheet!r}")


def _mutate_element(c: Any, new_value: Any) -> Any:
    """Return a COPY of `<c>` carrying the new value. The original tree is never modified.

    `deepcopy`, not a re-parse. P1's rule is that there is exactly ONE parser factory — a second
    `etree.fromstring` can carry different entity and DTD settings, and the test that enforces it
    caught this module on its first run.
    """
    el = copy.deepcopy(c)
    if new_value is REMOVE or new_value == REMOVE:
        # F05.b — the cell is EMPTIED, which is a different fault from writing 0. The `<c>` element
        # stays so the row's shape is unchanged; only its value goes.
        for child in list(el):
            el.remove(child)
        el.attrib.pop("t", None)
        return el
    for child in list(el):
        # A formula cell being overridden loses its `<f>`: that IS the F11 fault, and leaving the
        # formula in place would make the mutant a cached-value edit rather than an override.
        el.remove(child)
    if isinstance(new_value, str):
        el.set("t", "inlineStr")
        is_el = etree.SubElement(el, f"{NS}is")
        t_el = etree.SubElement(is_el, f"{NS}t")
        t_el.text = new_value
        if new_value != new_value.strip():
            # `xml:space="preserve"`, and without it F12.c was not the fault it claimed to be.
            # The trailing-whitespace operator writes `"X "`; the serialiser dropped the space,
            # the mutant read back as `"X"`, and 12 mutants classified UNOBSERVABLE because they
            # were identical to the clean filing — a fault that did not survive being written.
            t_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    else:
        el.attrib.pop("t", None)
        etree.SubElement(el, f"{NS}v").text = str(new_value)
    return el


class PartsChangedError(SurgeryError):
    """A part changed that no edit named. Shared by every caller of `write_cells`."""


def write_cells(base: Path, edits: Sequence[CellEdit], out: Path) -> frozenset[str]:
    """THE ONE WORKBOOK WRITER. Byte-for-byte copy; exactly the parts the edits name are rewritten.

    **Extracted from `seed_mutant` on 20 Aug 2026 so the FILL path and the MUTANT path cannot
    drift.** They need identical guarantees for opposite reasons — a mutant that lost a part would
    make the observability diff a diff of the writer, and a FILLED RETURN that lost a part would be
    a different document handed to a regulator under the original's name. One writer, two callers,
    one set of invariants.

    Everything the module docstring says about the method applies here and is where it is enforced:
    every entry copied with its original compression parameters, the worksheet XML PARSED rather
    than pattern-matched, and `parts_changed` compared against the parts the edits name rather than
    against the number 1.
    """
    if not edits:
        raise SurgeryError(
            "a write with no edits is the base workbook under another name; callers that mean "
            "'copy' should copy."
        )

    with zipfile.ZipFile(base) as z:
        named_parts = {e.sheet_name: _part_for(z, e.sheet_name) for e in edits}
        parts = {n: z.read(n) for n in z.namelist()}
        infos = {i.filename: i for i in z.infolist()}

    for sheet, target in named_parts.items():
        by_ref = {e.ref: e for e in edits if e.sheet_name == sheet}
        root = fromstring(parts[target])
        applied = set()
        for c in root.iter(f"{NS}c"):
            edit = by_ref.get(c.get("r") or "")
            if edit is None:
                continue
            c.getparent().replace(c, fromstring(edit.new_xml.encode()))
            applied.add(edit.ref)
        if applied != set(by_ref):
            raise SiteNotFoundError(
                f"edit(s) found no cell on {sheet}: {sorted(set(by_ref) - applied)[:5]}"
            )
        parts[target] = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone=True
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as w:
        for name, data in parts.items():
            src = infos[name]
            info = zipfile.ZipInfo(name, date_time=src.date_time)
            info.compress_type = src.compress_type
            info.external_attr = src.external_attr
            info.create_system = src.create_system
            w.writestr(info, data)

    changed = differing_parts(base, out)
    expected = set(named_parts.values())
    if changed != expected:
        raise PartsChangedError(
            f"parts changed {sorted(changed)} but the edits name {sorted(expected)}. Raw-zip "
            "surgery rewrites exactly the parts the edits name; anything else means a part was "
            "re-serialised."
        )
    return changed


def seed_mutant(
    base: Path,
    edits: Sequence[CellEdit],
    out: Path,
    *,
    fault_class: str,
    operator_id: str,
    seed: int,
) -> MutantRecord:
    """Write the mutant, through `write_cells`. The invariants live there and are shared."""
    if not edits:
        raise SurgeryError("a mutant with no edits is the base workbook under another name")
    try:
        changed = write_cells(base, edits, out)
    except PartsChangedError as exc:
        # The mutant path has always raised MultiPartEditError here and the campaign catches it
        # by name; re-raised so extracting the writer changes no caller's contract.
        raise MultiPartEditError(str(exc)) from exc
    return MutantRecord(
        mutant_sha256=_sha(out.read_bytes()),
        base_sha256=_sha(base.read_bytes()),
        fault_class=fault_class,
        operator_id=operator_id,
        edits=tuple(edits),
        seed=seed,
        harness_version=HARNESS_VERSION,
        fault_model_version=FAULT_MODEL_VERSION,
        parts_changed=tuple(sorted(changed)),
        path=out,
    )


def differing_parts(a: Path, b: Path) -> frozenset[str]:
    """Zip-entry-wise diff. The test that matters is that this returns exactly one name."""
    with zipfile.ZipFile(a) as za, zipfile.ZipFile(b) as zb:
        names = set(za.namelist()) | set(zb.namelist())
        out = set()
        for n in names:
            try:
                same = za.read(n) == zb.read(n)
            except KeyError:
                same = False
            if not same:
                out.add(n)
    return frozenset(out)
