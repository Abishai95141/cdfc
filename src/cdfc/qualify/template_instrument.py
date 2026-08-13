"""P7-B0/B1 — the PINNED BLANK, rendered as an addressable instrument (F9).

**Why a template is an instrument.** Under F9 every harvested candidate carries a `TEMPLATE`
obligation whose `quote` is the construct the harvester read and whose `span` is that construct's
offset into this text. That is what makes `instrument_text.find(quote)` a real, failable question
for a candidate that cites no statute: *is the relation this predicate claims to implement present
in the pinned blank, at the offset recorded?* A candidate harvested from a different template
version is then rejected `g0.quote_not_located`, mechanically.

**Two parties, one of them external, and the external one is load-bearing.** Party A is this
repository's raw reader plus its own shared-formula shift; party B is `openpyxl`, which nobody here
wrote and which implements shared-formula translation independently. **211 of FME's 505 formula
cells are shared dependents whose text exists nowhere in the file** — `<f t="shared" si="0"/>`
carries no expression — so their text is something `calc/shift.materialise` COMPUTES. Before this
build nothing checked that computation against another implementation. Now every one of them is
either corroborated by an outside party or excluded.

**Party B's two blindnesses are named, and each is checkable rather than believed.** It returns an
`ArrayFormula` object instead of a string for an array formula (checkable: B itself reports the
object), and it is namespace-blind to the `x14` data-validation extension (checkable: A's record
carries `namespace == "x14"`). Both were measured across all nine workbooks at P1 and live in
`ingest/competence.py`; nothing here widens them by judgment.

**A deviation from the plan's signature, recorded rather than absorbed.** The plan wrote
`emit(schema: TemplateSchema) -> InstrumentText`. `TemplateSchema` is `{key: {cells}}` and carries
no construct text at all, so that signature cannot produce an instrument; `emit` takes the pinned
blank itself. Deriving the text from the schema would also have meant deriving it from ONE reading,
which is the thing this build exists to stop.
"""

from __future__ import annotations

import hashlib
import warnings
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from cdfc.ingest.reader_lxml import RawWorkbook, read
from cdfc.qualify.textsource import Extraction, InstrumentText, TextSourceError, Unit, build, normalise
from cdfc.schema.stable_keys import col_to_index, split_ref

# The visible separator between a construct's address and the construct itself. Any whitespace
# would be collapsed by `normalise`, so the separator has to survive it.
SEP: Final[str] = " :: "

ARRAY_FORMULA_MECHANISM: Final[str] = (
    "openpyxl returns an ArrayFormula object rather than the formula text for an array formula "
    "(ingest/competence.py, measured on all nine workbooks at P1)"
)
X14_MECHANISM: Final[str] = (
    "openpyxl is namespace-blind: it reads the main data-validation namespace and discards the "
    "x14 extension (ingest/competence.py, measured on all nine workbooks at P1)"
)
A_SEES_EVERYTHING: Final[str] = (
    "reader_lxml enumerates every <c> with an <f> child and every dataValidation in both "
    "namespaces; an absence here is a MISS and build() refuses it"
)


class TemplateInstrumentError(TextSourceError):
    """The pinned blank cannot be rendered as an instrument."""


def _corner(token: str) -> tuple[int, int]:
    try:
        col, row = split_ref(token.split(":")[0])
        return row, col_to_index(col)
    except ValueError:
        return 10**6, 10**6


def _norm_ref(ref: str) -> str:
    """A `sqref` canonicalised so that its RANGE ORDER cannot be a disagreement.

    **The reason is a defect this build found on its first run.** A `sqref` is a SET of ranges
    written as a space-separated string, and the two parties serialise that set differently:
    `reader_lxml` reports the bytes in file order, `openpyxl` reports its `MultiCellRange` in its
    own. Eleven of FME's validations differ only in that order. Comparing the raw strings would
    have reported eleven disagreements about the artifact where the artifact says one thing — and
    worse, the ANCHOR derived from "the first range" differed, so the two parties landed on
    different keys and the units never met to be compared at all. A set is sorted before it is
    compared; a genuine difference in the set still shows up, because the sorted forms differ.
    """
    tokens = [t for t in ref.replace("$", "").upper().split() if t]
    return " ".join(sorted(tokens, key=lambda t: (*_corner(t), t)))


def _anchor(ref: str) -> tuple[int, int]:
    """`(row, column)` of the top-left cell of a ref or sqref, over ALL its ranges.

    Invariant under regrouping of the same cell set, which is what makes it a key two independent
    serialisations agree on.
    """
    corners = [_corner(t) for t in _norm_ref(ref).split()]
    return min(corners) if corners else (10**6, 10**6)


def unit_key(sheet_index: int, sheet: str, kind: str, ref: str) -> str:
    """`(sheet ordinal, row, column, kind, address)`, laid out so that LEXICOGRAPHIC order is
    document order. `build()` sorts on this and on nothing else, so the instrument's byte layout
    does not depend on which party is passed first."""
    row, col = _anchor(ref)
    return f"{sheet_index:04d}|{row:06d}|{col:05d}|{kind}|{sheet}!{_norm_ref(ref)}"


def formula_unit_text(sheet: str, ref: str, body: str) -> str:
    return normalise(f"{sheet}!{_norm_ref(ref)}{SEP}{body}")


def validation_unit_text(
    sheet: str, sqref: str, type_: str | None, operator: str | None, formula1: str | None
) -> str:
    """One line per validation. Absent and empty are rendered identically as `-`, deliberately:
    the two parties encode "no operator" as `''` and as `None`, and a difference that exists only
    in a library's choice of sentinel is not a disagreement about the artifact."""
    def show(v: object) -> str:
        s = "" if v is None else str(v).strip()
        return s or "-"

    return normalise(
        f"{sheet}!{_norm_ref(sqref)}{SEP}{show(type_)} {show(operator)}{SEP}{show(formula1)}"
    )


# --- party A: this repository's reader, plus its own shared-formula shift ------------------


def _party_a(wb: RawWorkbook) -> tuple[dict[str, Unit], dict[str, str], dict[str, str]]:
    """Returns (units, x14 keys -> ref, array keys -> ref). The last two are the CHECKABLE
    evidence for party B's two declared blindnesses; nothing else may excuse an absence."""
    from cdfc.calc.shift import materialise

    order = {s.name: i for i, s in enumerate(wb.sheets)}
    by_sheet: dict[str, list[Any]] = {}
    for f in wb.formulas:
        by_sheet.setdefault(f.sheet, []).append(f)

    units: dict[str, Unit] = {}
    array_keys: dict[str, str] = {}
    for sheet, records in sorted(by_sheet.items()):
        masters = {f.si: f for f in records if f.encoding == "SHARED_MASTER"}
        for f in records:
            if f.text:
                body = f.text.strip()
            elif f.encoding == "SHARED_DEPENDENT":
                m = masters.get(f.si)
                if m is None or not m.text:
                    # The harvest declares this a typed skip; an instrument cannot carry a
                    # construct whose expression nobody can produce.
                    continue
                body = materialise(m.ref, m.text, f.ref).strip()
            else:
                body = (f.materialised or "").strip()
            if not body:
                continue
            k = unit_key(order.get(sheet, 10**6), sheet, "F", f.ref)
            units[k] = Unit(key=k, text=formula_unit_text(sheet, f.ref, body),
                            page=order.get(sheet, 10**6) + 1)
            if f.encoding == "ARRAY":
                array_keys[k] = f"{sheet}!{f.ref}"

    x14_keys: dict[str, str] = {}
    for d in wb.validations:
        k = unit_key(order.get(d.sheet, 10**6), d.sheet, "V", d.sqref)
        units[k] = Unit(
            key=k,
            text=validation_unit_text(d.sheet, d.sqref, d.type, d.operator, d.formula1),
            page=order.get(d.sheet, 10**6) + 1,
        )
        if d.namespace == "x14":
            x14_keys[k] = f"{d.sheet}!{d.sqref}"
    return units, x14_keys, array_keys


# --- party B: openpyxl, which nobody here wrote --------------------------------------------


def _party_b(blob: Path, sheet_order: Mapping[str, int]) -> tuple[dict[str, Unit], set[str]]:
    """Returns (units, keys where B itself reported an ArrayFormula object)."""
    import openpyxl

    with warnings.catch_warnings():
        # P0 makes openpyxl warnings errors on the ingest path. Here the warning IS the measured
        # exclusion mechanism — B warns that it is discarding the x14 extension and expects the
        # caller to ignore it — so it is caught rather than raised, and the exclusion it announces
        # is checked against A's record below.
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(blob, data_only=False)

    units: dict[str, Unit] = {}
    array_keys: set[str] = set()
    for ws in wb.worksheets:
        idx = sheet_order.get(ws.title, 10**6)
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                k = unit_key(idx, ws.title, "F", cell.coordinate)
                if isinstance(v, str) and v.startswith("="):
                    units[k] = Unit(
                        key=k,
                        text=formula_unit_text(ws.title, cell.coordinate, v[1:].strip()),
                        page=idx + 1,
                    )
                elif type(v).__name__ == "ArrayFormula":
                    array_keys.add(k)
        for dv in ws.data_validations.dataValidation:
            k = unit_key(idx, ws.title, "V", str(dv.sqref))
            units[k] = Unit(
                key=k,
                text=validation_unit_text(ws.title, str(dv.sqref), dv.type, dv.operator, dv.formula1),
                page=idx + 1,
            )
    return units, array_keys


# --- the instrument -------------------------------------------------------------------------


def instrument_id(template_sha256: str) -> str:
    return f"template-{template_sha256[:8]}"


def emit(blob: Path) -> InstrumentText:
    """The pinned blank as an addressable instrument. Deterministic in the file's bytes alone."""
    wb = read(blob)
    template_sha256 = hashlib.sha256(blob.read_bytes()).hexdigest()
    order = {s.name: i for i, s in enumerate(wb.sheets)}

    a_units, x14_keys, a_array_keys = _party_a(wb)
    b_units, b_array_keys = _party_b(blob, order)

    universe = set(a_units) | set(b_units)

    # B's blindness is declared as two named mechanisms, and each excluded key must SATISFY its
    # mechanism on this artifact. A blindness asserted without evidence would let a reader that
    # dropped a construct hide behind a rule, which is the same defect as an absence read as
    # agreement, one level up.
    b_blind: dict[str, str] = {}
    for k in sorted(universe - set(b_units)):
        if k in x14_keys:
            b_blind[k] = X14_MECHANISM
        elif k in b_array_keys or k in a_array_keys:
            b_blind[k] = ARRAY_FORMULA_MECHANISM
    unexplained = sorted(universe - set(b_units) - set(b_blind))
    if unexplained:
        raise TemplateInstrumentError(
            f"{blob.name}: openpyxl produced no reading at {len(unexplained)} key(s) that neither "
            f"declared mechanism explains, e.g. {unexplained[:3]}. That is a MISS by an external "
            "party over a construct this repository's reader claims to have read, and it is a "
            "finding about one of the two readers rather than a fact about the artifact."
        )
    a_blind = {k: A_SEES_EVERYTHING for k in sorted(universe - set(a_units))}
    if a_blind:
        raise TemplateInstrumentError(
            f"{blob.name}: reader_lxml produced no reading at {sorted(a_blind)[:3]} — keys "
            "openpyxl did read. reader_lxml enumerates the raw XML and has no declared blindness, "
            "so this is a defect in this repository's reader, not an exclusion."
        )

    return build(
        instrument_id(template_sha256),
        [
            Extraction(
                extractor="reader_lxml+calc.shift",
                version="P7",
                external=False,
                units=tuple(a_units[k] for k in sorted(a_units)),
                blind_to={},
            ),
            Extraction(
                extractor="openpyxl",
                version=_openpyxl_version(),
                external=True,
                units=tuple(b_units[k] for k in sorted(b_units)),
                blind_to=b_blind,
            ),
        ],
    )


def _openpyxl_version() -> str:
    import openpyxl

    return str(openpyxl.__version__)
