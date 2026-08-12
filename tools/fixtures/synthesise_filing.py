#!/usr/bin/env python
"""P5-B0 — the clean filings, and the difference between them is the whole of finding F2.

**TEMPLATE-COMPUTED** — inputs filled, derived cells written by `src/cdfc/calc/`.
`sum_identity`, `cross_sheet_equality` and `tally_identity` then assert exactly the identities
`calc/` enforced when it wrote the file. **The oracle and the system under test are the same
function**, so on this filing it is arithmetically impossible for an arithmetic predicate to fire.
*"Clean filing ⇒ 0 FAIL"* is `x == x`: green on a correct implementation, green on one whose
tolerance is a thousand times too wide, green on one that always returns `[]`.
**SMOKE ONLY — NON-GATING — NON-DISCRIMINATING (arithmetic).**

**INDEPENDENTLY-COMPUTED** — the same inputs, and the derived cells computed by **LibreOffice**,
which nobody on this project wrote. This is the filing a `0 FAIL` claim means something on.

> **What this is NOT, stated plainly and carried on every surface that quotes it.**
> The plan's entry criterion E6 asks for a **HAND-COMPUTED** filing whose derived cells were typed
> by a *person* from IFSCA's formula text. There is no such file: it depends on the G-EVAL arm-2
> human expectation file, which does not exist. LibreOffice is the strongest substitute available
> — an independent implementation of spreadsheet arithmetic that this project did not write — and
> it is **weaker than a person in two specific ways**:
>   1. **It is not Excel.** Where the two differ, a disagreement is a THIRD ANSWER, not a verdict
>      against us.
>   2. **It is a spreadsheet engine, not a reader of the regulation.** A person typing a value
>      from the formula text can notice that the formula is wrong. LibreOffice cannot.
> It is labelled `INDEPENDENTLY-COMPUTED (LibreOffice)` and never `HAND-COMPUTED`.

The mechanism: fill the inputs, **strip every cached `<v>` from every formula cell**, and hand the
file to LibreOffice. A formula cell with no cached value must be computed, so the derived values
in the output are LibreOffice's and not ours.

    python tools/fixtures/synthesise_filing.py
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.reader_lxml import _sheet_parts  # noqa: E402
from cdfc.ingest.xmlsafe import fromstring  # noqa: E402
from cdfc.predicates.harvest import M, _load_context, expand  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
OUT = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
SOFFICE = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")

# A lawful default for a cell under no validation. **1, and the value matters.**
#
# A filing must be JOINTLY lawful, not merely cell-wise lawful. With 100 in every input, a ten-row
# SUM produced 1,000 in a total cell the template bounds to [0, 100] — and the bound predicate
# FAILED on the "clean" filing. It was right: the filing was unlawful, in a way no single cell
# showed. 1 keeps every derived total inside the bounds this workbook declares while still
# satisfying every `>= 0`, and it cannot straddle a tolerance.
DEFAULT_NUMBER = 1


def plan_inputs(ctx) -> dict[tuple[str, str], object]:
    """A lawful value for every field-surface cell that is not a formula.

    Lawful means: inside the pinned blank's own data validation where there is one. A filing that
    violates the template's declared bounds would make `0 FAIL` uninteresting for the opposite
    reason.
    """
    from cdfc.predicates.harvest import resolve_vocabulary

    formula_refs = {(s, f.ref) for s, fs in ctx.formulas_by_sheet.items() for f in fs}
    values: dict[tuple[str, str], object] = {}

    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if not dv.sqref.split():
                continue
            refs = [c for part in dv.sqref.split() for c in expand(part.replace("$", ""))]
            if dv.type == "list":
                vocab, _ = resolve_vocabulary(ctx, sheet, dv.formula1)
                chosen: object | None = vocab[0] if vocab else None
            elif dv.type in ("whole", "decimal", "date"):
                chosen = _inside(dv.formula1, dv.formula2, dv.operator)
            else:
                chosen = None
            if chosen is None:
                continue
            for ref in refs:
                if (sheet, ref) in formula_refs or (sheet, ref) not in ctx.key_of:
                    continue
                values[(sheet, ref)] = chosen

    # Every remaining unlocked non-formula cell gets the default, so the filing is FULL — a
    # partially-filled filing would make `notRun` the interesting number rather than `settled`.
    for sheet, ref in ctx.wb.unlocked_cells:
        if (sheet, ref) in formula_refs or (sheet, ref) in values:
            continue
        if (sheet, ref) in ctx.key_of:
            values[(sheet, ref)] = DEFAULT_NUMBER
    return values


def _inside(f1: str | None, f2: str | None, operator: str) -> object | None:
    def num(x: str | None) -> float | None:
        try:
            return float(str(x).strip().lstrip("="))
        except (TypeError, ValueError):
            return None

    lo, hi = num(f1), num(f2)
    if lo is None:
        return None
    # A SMALL lawful value, never the bound itself. One `decimal` validation on this workbook has
    # an upper bound of 9.99999999999999E+26; picking `bound - 1` produced a value that overflows
    # int64 and the fact view refused it — correctly, and for a reason that had nothing to do with
    # the filing being unlawful. A filing should sit comfortably inside its bounds, not on them.
    # INSIDE the declared range, and the clamping order matters. The first version took
    # `min(lo+1, hi-1, DEFAULT_NUMBER)` unconditionally, which wrote 100 into the six DATE cells
    # bounded to [32874, 73415] — Excel serial days. Five date-bound predicates then FAILED on the
    # "clean" filing, and they were RIGHT: the value was outside the template's own bound. The
    # defect was in the filing generator, and the predicates found it.
    if hi is not None and hi > lo:
        candidate = DEFAULT_NUMBER if lo <= DEFAULT_NUMBER <= hi else (lo + 1 if hi - lo > 2 else lo)
        inside = min(max(candidate, lo), hi)
        return int(inside) if _fits(inside) else None
    if operator in ("greaterThanOrEqual", "greaterThan"):
        value = max(lo + 1, DEFAULT_NUMBER) if lo < DEFAULT_NUMBER else lo + 1
        return int(value) if _fits(value) else None
    if operator in ("lessThanOrEqual", "lessThan"):
        value = DEFAULT_NUMBER if lo >= DEFAULT_NUMBER else lo - 1
        return int(value) if _fits(value) else None
    return int(lo) if _fits(lo) else None


def _fits(x: float) -> bool:
    """A value outside int64 cannot enter the fact model, so it must not enter the filing."""
    return -(2**63) <= int(x) < 2**63


# NO REGEX OVER OOXML. The first version of this file rewrote `<c>` elements with a pattern and
# produced malformed XML — `Opening and ending tag mismatch: row ... and c` — which LibreOffice
# then "repaired" by dropping 424 of the workbook's 505 formulas. **That is this project's own
# documented lesson, walked into by the person who wrote the gate against it.** The sibling gate
# `ci/no-regex-over-xml.sh` was named in `ci/no-regex-over-cel.sh`'s own docstring and did not
# exist; it does now.


def write_filing(
    source: Path, target: Path, values: dict[tuple[str, str], object], *, strip_cached: bool
) -> Path:
    """Raw-zip surgery, with the worksheet XML PARSED rather than pattern-matched.

    Every part is copied byte-for-byte except the worksheets that change. Never an openpyxl
    round-trip: openpyxl discards the 19 `x14` validations and the data model, and a fixture that
    differs from the pinned blank in ways nobody intended is not a control.
    """
    with zipfile.ZipFile(source) as z:
        sheets = {name: part for name, _state, part in _sheet_parts(z)}
        parts = {n: z.read(n) for n in z.namelist()}
        infos = {i.filename: i for i in z.infolist()}

    for sheet, part in sheets.items():
        if part not in parts:
            continue
        per_sheet = {ref: v for (s, ref), v in values.items() if s == sheet}
        if not per_sheet and not strip_cached:
            continue
        parts[part] = _rewrite_sheet(parts[part], per_sheet, strip_cached=strip_cached)

    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in parts.items():
            info = zipfile.ZipInfo(name, date_time=infos[name].date_time)
            info.compress_type = infos[name].compress_type
            info.external_attr = infos[name].external_attr
            out.writestr(info, data)
    return target


def _rewrite_sheet(xml: bytes, values: dict[str, object], *, strip_cached: bool) -> bytes:
    from lxml import etree

    root = fromstring(xml)
    ns = f"{{{M}}}"
    seen: set[str] = set()
    for c in root.iter(f"{ns}c"):
        ref = c.get("r") or ""
        seen.add(ref)
        formula = c.find(f"{ns}f")
        if formula is not None:
            if strip_cached:
                for v in c.findall(f"{ns}v"):
                    c.remove(v)
            elif ref in values:
                # A CACHED VALUE for a formula cell. The formula stays: a filing whose derived
                # cells carry values but no formulas is a different artifact, and the template
                # differential reads the formulas.
                for v in c.findall(f"{ns}v"):
                    c.remove(v)
                c.attrib.pop("t", None)
                _sub(c, f"{ns}v").text = str(values[ref])
            continue
        if ref not in values:
            continue
        _set_value(c, ns, values[ref])

    # A cell the template does not carry at all: the filing writes one. `<row>` order and `<c>`
    # order within a row are both significant, so the cell is inserted in column order.
    missing = {r: v for r, v in values.items() if r not in seen}
    if missing:
        _insert_cells(root, ns, missing, etree)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _set_value(c, ns: str, value: object) -> None:
    for child in list(c):
        c.remove(child)
    if isinstance(value, str):
        c.set("t", "inlineStr")
        is_el = _sub(c, f"{ns}is")
        _sub(is_el, f"{ns}t").text = value
    else:
        c.attrib.pop("t", None)
        _sub(c, f"{ns}v").text = str(value)


def _sub(parent, tag: str):
    from lxml import etree

    el = etree.SubElement(parent, tag)
    return el


def _insert_cells(root, ns: str, values: dict[str, object], etree) -> None:
    from cdfc.schema.stable_keys import col_to_index, split_ref

    sheet_data = root.find(f"{ns}sheetData")
    if sheet_data is None:
        return
    rows = {int(r.get("r") or 0): r for r in sheet_data.findall(f"{ns}row")}
    by_row: dict[int, list[tuple[int, str, object]]] = {}
    for ref, value in values.items():
        try:
            col, rownum = split_ref(ref)
        except ValueError:
            continue
        by_row.setdefault(rownum, []).append((col_to_index(col), ref, value))

    for rownum in sorted(by_row):
        row = rows.get(rownum)
        if row is None:
            row = etree.SubElement(sheet_data, f"{ns}row")
            row.set("r", str(rownum))
            rows[rownum] = row
            sheet_data[:] = sorted(sheet_data, key=lambda e: int(e.get("r") or 0))
        for _idx, ref, value in sorted(by_row[rownum]):
            c = etree.SubElement(row, f"{ns}c")
            c.set("r", ref)
            _set_value(c, ns, value)
        row[:] = sorted(row, key=lambda e: col_to_index(split_ref(e.get("r") or "A1")[0]))


def libreoffice_recalculate(path: Path) -> Path:
    """Hand the file to LibreOffice and take back what IT computed. Not us, and not Excel."""
    if not SOFFICE.is_file():
        raise RuntimeError(
            f"LibreOffice is not installed at {SOFFICE}. The independently-computed filing is the "
            "one the 0-FAIL claim is made on; without it there is only the TEMPLATE-COMPUTED "
            "filing, which is SMOKE ONLY and may not be cited in a gate."
        )
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [str(SOFFICE), "--headless", "--norestore", "--convert-to", "xlsx:Calc MS Excel 2007 XML",
             "--outdir", tmp, str(path)],
            capture_output=True, text=True, timeout=600,
        )
        produced = Path(tmp) / (path.stem + ".xlsx")
        if not produced.is_file():
            raise RuntimeError(f"LibreOffice produced nothing: {proc.stdout}\n{proc.stderr}")
        out = path.with_name(path.name)
        shutil.copy2(produced, out)
    return out


def _formula_values(blob: Path) -> dict[tuple[str, str], object]:
    """Every formula cell's CACHED VALUE from a recalculated workbook. The numbers, not the shape."""
    out: dict[tuple[str, str], object] = {}
    with zipfile.ZipFile(blob) as z:
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            for c in root.iter(f"{{{M}}}c"):
                if c.find(f"{{{M}}}f") is None:
                    continue
                v = c.find(f"{{{M}}}v")
                if v is None or v.text is None:
                    continue
                out[(name, c.get("r") or "")] = v.text
    return out


def computed_cells(blob: Path) -> set[tuple[str, str]]:
    """Every formula cell — i.e. every cell whose value a computation wrote, not a filer."""
    ctx = _load_context(blob)
    return {(s, f.ref) for s, fs in ctx.formulas_by_sheet.items() for f in fs}


def seed_f11(source: Path, target: Path, sheet: str, ref: str, literal: object) -> Path:
    """E5 — a single-fault variant by RAW-ZIP SURGERY. One worksheet part differs; nothing else."""
    return write_filing(source, target, {(sheet, ref): literal}, strip_cached=False)


def sha8(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def main() -> int:
    ctx = _load_context(FME)
    values = plan_inputs(ctx)
    print(f"planned {len(values)} input cells over {len({s for s, _ in values})} sheets")

    OUT.mkdir(parents=True, exist_ok=True)
    staged = OUT / "_staged__fme-q1.xlsx"
    write_filing(FME, staged, values, strip_cached=True)
    print(f"staged (inputs filled, every cached formula value stripped): {staged.name}")

    # LibreOffice is used as a CALCULATOR, and its output STRUCTURE is discarded. Only the numbers
    # cross over, written back into a copy of the pinned blank by the same raw-zip surgery.
    #
    # Why: a LibreOffice round-trip rewrites merged ranges, defined names and the protection mask,
    # so the file it emits does not BIND to the pinned template — correctly, because it is
    # structurally a different workbook. Taking its values and discarding its structure gives the
    # thing that is actually wanted: **the pinned blank, filled, with derived cells this project
    # did not compute.** It also makes the two filings structurally identical, so they differ in
    # exactly one respect: who calculated.
    recalced = OUT / "_recalced__fme-q1.xlsx"
    shutil.copy2(staged, recalced)
    libreoffice_recalculate(recalced)
    derived = _formula_values(recalced)
    recalced.unlink()

    independent = OUT / "clean__independently-computed__fme-q1.xlsx"
    write_filing(FME, independent, {**values, **derived}, strip_cached=False)
    print(f"INDEPENDENTLY-COMPUTED (LibreOffice): {independent.name}  sha8 {sha8(independent)}  "
          f"derived cells LibreOffice computed: {len(derived)} of {len(computed_cells(FME))}")

    template_computed = OUT / "clean__template-computed__fme-q1.xlsx"
    _write_template_computed(FME, FME, template_computed, values)
    print(f"TEMPLATE-COMPUTED (calc/ wrote the derived cells; SMOKE ONLY): "
          f"{template_computed.name}  sha8 {sha8(template_computed)}")

    # E5 — the single-fault variant, by RAW-ZIP SURGERY on the independently-computed filing.
    # One worksheet part differs and nothing else; never an openpyxl round-trip.
    #
    # F11, the FORMULA OVERRIDE: a cell the pinned blank declares a formula for carries a literal
    # instead. The flagship class, and the one no relation the template encodes can detect —
    # which is why the seeded value is chosen to break the identity the carry asserts.
    seeded = OUT / "mutant__f11-formula-override__portfolio-O7.xlsx"
    target = _pick_seed_cell(independent)
    if target is None:
        print("no seedable carry target found; the variant is NOT written and this says so")
    else:
        sheet, ref, was = target
        seed_f11(independent, seeded, sheet, ref, int(was) + 7)
        print(f"SEEDED F11 at {sheet}!{ref}: {was} -> {int(was) + 7}   {seeded.name}  "
              f"sha8 {sha8(seeded)}")

    staged.unlink()
    return 0


def _pick_seed_cell(filing: Path) -> tuple[str, str, int] | None:
    """A cross-sheet carry TARGET with an integer value. Deterministic: the first in cell order."""
    import sys as _sys

    _sys.path.insert(0, str(REPO / "src"))
    from cdfc.predicates.ast_walker import bound_cells

    from cdfc.measure.p5_run import fme_harvest

    res = fme_harvest()
    ctx = _load_context(filing)
    for c in res.candidates:
        if "carried across sheets" not in c.rationale:
            continue
        for cell in sorted(bound_cells(c, res.schema)):
            sheet, ref = cell.split("!")
            raw = ctx.cell_values.get(sheet, {}).get(ref)
            if raw is None:
                continue
            try:
                return sheet, ref, int(float(str(raw)))
            except (TypeError, ValueError):
                continue
    return None


def _write_template_computed(blank: Path, staged: Path, target: Path, values: dict) -> None:
    """Fill the inputs, then let `src/cdfc/calc/` compute the derived cells and write them in."""
    from cdfc.calc.evaluate import recalculate
    from cdfc.calc.shift import materialise as shift_materialise

    ctx = _load_context(blank)
    formulas: dict[tuple[str, str], str] = {}
    deferred: dict[tuple[str, str], str] = {}
    for sheet, records in ctx.formulas_by_sheet.items():
        masters = {f.si: f for f in records if f.encoding == "SHARED_MASTER"}
        for f in records:
            if f.text:
                formulas[(sheet, f.ref)] = f.text
            elif f.encoding == "SHARED_DEPENDENT":
                m = masters.get(f.si)
                if m is None or not m.text:
                    deferred[(sheet, f.ref)] = f"shared dependent si={f.si}, master not visible"
                else:
                    formulas[(sheet, f.ref)] = shift_materialise(m.ref, m.text, f.ref)

    literals = {k: v for k, v in values.items()}
    grid = recalculate(
        formulas=formulas, literals=literals, formula_source="TEMPLATE", deferred=deferred
    )
    computed = {
        k: v for k, v in grid.values.items()
        if k in formulas and isinstance(v, (int, float)) and not isinstance(v, bool)
    }
    write_filing(staged, target, {**values, **{k: _int(v) for k, v in computed.items()}},
                 strip_cached=False)


def _int(v: object) -> object:
    try:
        f = float(str(v))
    except (TypeError, ValueError):
        return v
    return int(f) if f == int(f) else v


if __name__ == "__main__":
    raise SystemExit(main())
