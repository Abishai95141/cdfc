"""B1 — write a `FillDeclaration` into the regulator's own template. Raw-zip surgery, never a rewrite.

## Why this is not a convenience

`A5` proposes a value for a field and nothing put it in a cell, so the most visible clause of the
product's claim — *populates the regulator's prescribed filing template* — was demonstrated by a
JSON file.

**And the obvious way to do it destroys the template.** `ci/no-openpyxl-writer.sh` exists because an
openpyxl round-trip of the FME workbook **drops 24 parts and all 19 `x14` data validations, and
shrinks 3.66 MB to 66 kB**. A "filled return" written that way is a different document that happens
to share a name — the dropdowns a filer relies on are gone, the data model is gone, and a regulator
receiving it receives something nobody produced on purpose.

So this goes through `cdfc.qualify.surgery.write_cells`, which copies every zip entry byte-for-byte
with its original compression parameters, parses the worksheet XML rather than pattern-matching it,
and **refuses if any part changed that no edit named**. That writer was extracted from the mutant
seeder for this: the two paths need identical guarantees for opposite reasons, and one writer with
two callers cannot drift.

## What gets written, and what is refused

**Both lanes are written.** An `admitted` fill is evidenced — a span re-reads it byte-exact. A
`derived` fill is a value a model produced that no span supports. `docs/AUDIT-TRAIL.md` 20 Aug
records the decision to admit those, and the separation that replaces the property it relaxes:
they are written into the return **and never counted as checked**.

`FillWriteRecord` carries both counts separately and a per-cell provenance row, so the artefact
beside the workbook says which cells are which. A filled workbook with no such record would be a
return whose provenance lives only in whoever ran it.

**An ATTESTATION is never written**, whatever evidence supports it, because a certification is a
natural person accepting liability. Those cells are left exactly as the template had them.

## The invariant this module adds on top of the writer's

`write_cells` guarantees no unnamed PART changes. That is not enough here: a bug in edit planning
could rewrite the correct part and the wrong CELL inside it. So `verify_written` re-opens both
workbooks and compares **every cell of every sheet**, asserting that the set of cells that differ
is exactly the set the declaration named. A part-level check would have passed a cell-level defect.
"""

from __future__ import annotations

import zipfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from cdfc.fill.propose import Derived, FillDeclaration, FillProposal
from cdfc.qualify.surgery import CellEdit, plan_edit, write_cells

NS: Final[str] = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


class FillWriteError(RuntimeError):
    """The return cannot be written. Never partially written, never repaired."""


@dataclass(frozen=True, slots=True)
class WrittenCell:
    ref: str
    value: str
    lane: str            # "evidenced" | "derived"
    document: str        # the artefact the value came from
    span: tuple[int, int] | None    # None for derived: that IS the distinction


@dataclass(frozen=True, slots=True)
class FillWriteRecord:
    """What was written, by lane, with per-cell provenance. Ships beside the workbook."""

    template_sha256: str
    output_sha256: str
    parts_changed: tuple[str, ...]
    cells: tuple[WrittenCell, ...]
    attestations_left_blank: tuple[str, ...]

    def counts(self) -> dict[str, int]:
        return {
            "written_total": len(self.cells),
            "evidenced": sum(1 for c in self.cells if c.lane == "evidenced"),
            "derived": sum(1 for c in self.cells if c.lane == "derived"),
            "attestations_left_blank": len(self.attestations_left_blank),
            "parts_changed": len(self.parts_changed),
        }

    def lines(self) -> tuple[str, ...]:
        c = self.counts()
        return (
            f"template   {self.template_sha256[:16]}…",
            f"output     {self.output_sha256[:16]}…",
            f"parts rewritten  {c['parts_changed']}  {list(self.parts_changed)}",
            "",
            f"cells written    {c['written_total']}"
            f"  =  {c['evidenced']} evidenced + {c['derived']} derived",
            f"attestations left blank  {c['attestations_left_blank']}"
            "   (a named human signs; the system never writes one)",
            "",
            "An EVIDENCED cell cites a document and a span that re-reads byte-exact. A DERIVED "
            "cell holds a value a model produced that no span supports. Both are in the return; "
            "only the first is counted as checked.",
        )


def _split(ref: str) -> tuple[str, str]:
    """`'1. Introduction!D10'` -> `('1. Introduction', 'D10')`.

    **Split on the LAST `!`**, because a sheet name may contain one. `docs/AUDIT-TRAIL.md` records
    an adversarial audit finding this exact defect at 18 sites, where a left-split silently
    addressed the wrong sheet; gate 126 exists for it.
    """
    if "!" not in ref:
        raise FillWriteError(
            f"{ref!r} is not a sheet-qualified cell reference; a bare cell address does not say "
            "which sheet it is on and this writer will not guess."
        )
    sheet, cell = ref.rsplit("!", 1)
    return sheet, cell


def plan(declaration: FillDeclaration, template: Path) -> tuple[CellEdit, ...]:
    """One `CellEdit` per cell to write. Raises rather than skipping a cell it cannot place."""
    edits: list[CellEdit] = []
    for item in (*declaration.admitted(), *declaration.derived):
        sheet, cell = _split(item.ref)
        try:
            edits.append(plan_edit(template, sheet, cell, item.value, operator_id="A5-FILL"))
        except Exception as exc:                                   # noqa: BLE001
            raise FillWriteError(
                f"{item.ref}: the template carries no such cell ({type(exc).__name__}). A fill "
                "that silently skipped it would report a value as written that is not in the "
                "return."
            ) from exc
    return tuple(edits)


def write(declaration: FillDeclaration, template: Path, out: Path) -> FillWriteRecord:
    """Write the declaration's evidenced and derived fills into a copy of `template`."""
    import hashlib

    edits = plan(declaration, template)
    if not edits:
        raise FillWriteError(
            "the declaration proposes no value for any field, so there is nothing to write. An "
            "empty write would produce a copy of the blank under a filled return's name."
        )
    changed = write_cells(template, edits, out)

    by_ref: dict[str, WrittenCell] = {}
    for p in declaration.admitted():
        assert isinstance(p, FillProposal)
        by_ref[p.ref] = WrittenCell(ref=p.ref, value=p.value, lane="evidenced",
                                    document=p.document, span=p.span)
    for d in declaration.derived:
        assert isinstance(d, Derived)
        by_ref[d.ref] = WrittenCell(ref=d.ref, value=d.value, lane="derived",
                                    document=d.basis, span=None)

    return FillWriteRecord(
        template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),
        output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
        parts_changed=tuple(sorted(changed)),
        cells=tuple(by_ref[r] for r in sorted(by_ref)),
        attestations_left_blank=tuple(sorted(a.ref for a in declaration.attestations)),
    )


# --- verification, and it is CELL-level on purpose ------------------------------------------


def _cells_of(path: Path) -> dict[str, str]:
    """Every cell of every sheet, as `'Sheet!Ref' -> serialised <c> element`.

    Read through the ONE parser factory, as `xmlsafe` requires, and by parsing rather than by
    pattern: `ci/no-regex-over-xml.sh` exists because a pattern over this format returned a correct
    count with wrong contents three times in this project.
    """
    from lxml import etree

    from cdfc.ingest.xmlsafe import fromstring

    out: dict[str, str] = {}
    with zipfile.ZipFile(path) as z:
        wb = fromstring(z.read("xl/workbook.xml"))
        rel = fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rel}
        RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
        for sh in wb.iter(f"{NS}sheet"):
            name = sh.get("name") or ""
            t = target.get(sh.get(f"{RNS}id") or "")
            if not t:
                continue
            part = t if t.startswith("xl/") else f"xl/{t.lstrip('/')}"
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            for c in root.iter(f"{NS}c"):
                ref = c.get("r")
                if ref:
                    out[f"{name}!{ref}"] = etree.tostring(c, encoding="unicode")
    return out


X14: Final[str] = "{http://schemas.microsoft.com/office/spreadsheetml/2009/9/main}"


def _count_x14(z: zipfile.ZipFile) -> int:
    """`<x14:dataValidation>` ELEMENTS, by parsing.

    **A BYTE COUNT OF THE TAG NAME IS NOT A COUNT OF THE VALIDATIONS**, and the first version of
    this was one: `b"x14:dataValidation"` occurs in the opening tag, the closing tag AND the
    `<x14:dataValidations>` container, so it reported **48** where the FME blank carries **19**.
    The invariant being checked — before equals after — held either way, which is exactly how a
    wrong number survives: it was never the thing failing.

    19 is the figure `ci/no-openpyxl-writer.sh` and `NC-Q30` cite, and parsing reproduces it.
    """
    from cdfc.ingest.xmlsafe import fromstring

    n = 0
    for name in z.namelist():
        if not name.endswith(".xml"):
            continue
        try:
            root = fromstring(z.read(name))
        except Exception:                                          # noqa: BLE001
            continue        # a part that is not parseable XML carries no validations to count
        n += sum(1 for _ in root.iter(f"{X14}dataValidation"))
    return n


def verify_written(
    template: Path, out: Path, record: FillWriteRecord, *, expect_validations: int | None = None
) -> dict[str, Any]:
    """Re-open BOTH workbooks and prove the write did exactly what the record says.

    **Cell-level, not part-level.** `write_cells` already guarantees no unnamed PART changed; a
    bug in edit planning could still rewrite the right part and the wrong cell inside it, and a
    part-level check would pass that. So every cell of every sheet is compared and the differing
    set must equal the set the record names.

    Returns the observed figures rather than a bare pass, so a caller reports numbers.
    """
    before, after = _cells_of(template), _cells_of(out)

    with zipfile.ZipFile(template) as a, zipfile.ZipFile(out) as b:
        parts_before, parts_after = set(a.namelist()), set(b.namelist())
        v_before, v_after = _count_x14(a), _count_x14(b)

    if parts_before != parts_after:
        raise FillWriteError(
            f"the part list changed: {len(parts_before ^ parts_after)} part(s) differ, e.g. "
            f"{sorted(parts_before ^ parts_after)[:3]}. A return missing a part is a different "
            "document under the original's name."
        )
    if v_after != v_before:
        raise FillWriteError(
            f"x14 data validations went from {v_before} to {v_after}. The dropdowns a filer "
            "relies on are part of the return."
        )

    named = {c.ref for c in record.cells}
    differing = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
    if differing != named:
        unexpected = sorted(differing - named)
        missing = sorted(named - differing)
        raise FillWriteError(
            f"the cells that changed are not the cells the record names. "
            f"{len(unexpected)} changed but unnamed (e.g. {unexpected[:3]}); "
            f"{len(missing)} named but unchanged (e.g. {missing[:3]})."
        )
    if expect_validations is not None and v_after != expect_validations:
        raise FillWriteError(
            f"expected {expect_validations} x14 validations, the template carries {v_after}. The "
            "pin and the artefact disagree."
        )
    return {
        "parts_before": len(parts_before), "parts_after": len(parts_after),
        "x14_validations_before": v_before, "x14_validations_after": v_after,
        "cells_before": len(before), "cells_after": len(after),
        "cells_changed": len(differing), "cells_named": len(named),
    }


def written_values(out: Path, refs: Sequence[str]) -> dict[str, str]:
    """The VALUE now at each ref, read back out of the written workbook.

    Reading the file we just wrote is the point: an assertion against the in-memory record would
    prove the record is self-consistent and nothing about the artefact.
    """
    from cdfc.ingest.xmlsafe import fromstring

    want = set(refs)
    got: dict[str, str] = {}
    cells = _cells_of(out)
    for ref in want:
        raw = cells.get(ref)
        if raw is None:
            continue
        c = fromstring(raw.encode())
        t = c.find(f"{NS}is/{NS}t")
        if t is not None:
            got[ref] = t.text or ""
            continue
        v = c.find(f"{NS}v")
        if v is not None:
            got[ref] = v.text or ""
    return got
