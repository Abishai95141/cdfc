"""READER B — openpyxl. Formula TEXT and cached values. NEVER validations. NEVER a save.

B is a party to four of the eight agreement fields and is declared INCOMPETENT for the
other four, with the incompetence MEASURED rather than assumed:

  n_validations    namespace-blind — sees the main namespace only, discarding x14
  n_cells          counts non-empty VALUES, not <c> elements
  n_formula_cells  returns ArrayFormula objects and does not expose shared dependents
  n_defined_names  workbook scope only

Those measurements are the blind-control vector, and they are re-measured on every run
rather than remembered — a pinned control that is never re-taken is a claim about the
past.

**NEVER a save.** openpyxl's round-trip is destructive on these workbooks: 3,663,391
bytes in, 65,877 out, and 19 of 19 x14 validations gone. NC-P04 asserts statically that
`Workbook.save` is unreachable from every core package.
"""

from __future__ import annotations

import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReaderBView:
    n_sheets: int
    sheet_names: tuple[str, ...]
    hidden_sheets: tuple[str, ...]
    merged_ranges: tuple[str, ...]
    # the four it is not a party to, measured anyway so the blindness is a number
    blind_n_validations: int
    blind_n_cells: int
    blind_n_formula_cells: int
    blind_n_defined_names: int
    formula_text: Mapping[tuple[str, str], str]
    cached_values: Mapping[tuple[str, str], object]


def read_formula_text_and_cached(blob_path: Path) -> ReaderBView:
    # The warning openpyxl emits here IS the signal — it is telling us it is about to
    # discard the x14 validations. We capture it deliberately rather than let the global
    # `filterwarnings = ["error"]` turn reading B into a crash; the point of B is to
    # measure what it cannot see.
    import openpyxl

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(blob_path)
        wbv = openpyxl.load_workbook(blob_path, data_only=True)

        names, hidden, merged = [], [], []
        dv = n_cells = n_formula = 0
        ftext: dict[tuple[str, str], str] = {}
        cached: dict[tuple[str, str], object] = {}

        for ws in wb.worksheets:
            names.append(ws.title)
            if ws.sheet_state != "visible":
                hidden.append(ws.title)
            merged.extend(str(r) for r in ws.merged_cells.ranges)
            dv += len(ws.data_validations.dataValidation)
            for row in ws.iter_rows():
                for c in row:
                    if c.value is not None:
                        n_cells += 1
                        if isinstance(c.value, str) and c.value.startswith("="):
                            n_formula += 1
                            ftext[(ws.title, c.coordinate)] = c.value
        for ws in wbv.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if c.value is not None:
                        cached[(ws.title, c.coordinate)] = c.value

        n_defined = len(list(wb.defined_names))

    return ReaderBView(
        n_sheets=len(names),
        sheet_names=tuple(names),
        hidden_sheets=tuple(hidden),
        merged_ranges=tuple(merged),
        blind_n_validations=dv,
        blind_n_cells=n_cells,
        blind_n_formula_cells=n_formula,
        blind_n_defined_names=n_defined,
        formula_text=ftext,
        cached_values=cached,
    )


def agreement_view(v: ReaderBView) -> Mapping[str, object]:
    """Only the four fields B is a party to. The other four are deliberately absent —
    supplying them would invite a comparison the competence matrix forbids."""
    return {
        "n_sheets": v.n_sheets,
        "sheet_names": list(v.sheet_names),
        "hidden_sheets": list(v.hidden_sheets),
        "merged_ranges": sorted(v.merged_ranges),
    }


def blind_controls(v: ReaderBView) -> Mapping[str, int]:
    return {
        "n_validations": v.blind_n_validations,
        "n_cells": v.blind_n_cells,
        "n_formula_cells": v.blind_n_formula_cells,
        "n_defined_names": v.blind_n_defined_names,
    }
