"""Which instrument is a party to which field, and on which workbooks that was MEASURED.

The competence matrix is what stops the agreement check being switched off. Comparing
reader A against a reader known to be blind to a field fires every time, and a check that
always fires is a check somebody disables. So each field names its parties, and every
exclusion carries `measured_on` — the set of workbooks on which the incompetence was
actually observed.

**`measured_on` is not decoration.** A field whose parties exclude an instrument may only
be compared on a workbook inside `measured_on`; anywhere else the cell reads
`NOT_COMPARABLE(competence_unmeasured)`, **never `AGREE`**. Widening the set requires the
measurement, not an edit. Without that rule this matrix would classify 64 unmeasured cells
from a judgment taken on one workbook.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

AGREEMENT_FIELDS: tuple[str, ...] = (
    "n_sheets",
    "sheet_names",
    "hidden_sheets",
    "n_cells",
    "n_formula_cells",
    "n_validations",
    "n_defined_names",
    "merged_ranges",
)

STRUCTURAL_FIELDS: tuple[str, ...] = ("n_sheets", "sheet_names", "hidden_sheets")

# The written definition is the contract. Two readers agreeing on a number they define
# differently is a coincidence, not a check.
FIELD_DEFINITIONS: dict[str, str] = {
    "n_sheets": "count of <sheet> elements in xl/workbook.xml, ANY state",
    "sheet_names": "the @name of each <sheet>, in workbook.xml document order",
    "hidden_sheets": "the @name of each <sheet> whose @state is not 'visible'",
    "n_cells": "count of <c> elements across every worksheet part — NOT non-empty values",
    "n_formula_cells": "count of <c> elements containing an <f> child, ANY encoding "
                       "(TEXT, SHARED_MASTER, SHARED_DEPENDENT, ARRAY)",
    "n_validations": "count of dataValidation elements in the main namespace PLUS the "
                     "x14 extension namespace",
    "n_defined_names": "count of definedName elements in workbook.xml, ANY scope, "
                       "including _xlnm.* and sheet-local names",
    "merged_ranges": "the @ref of every <mergeCell>, across every worksheet part",
}


class Instrument(StrEnum):
    A = "reader_lxml"
    A_PRIME = "reader_lxml_b"
    B = "reader_openpyxl"


ALL_NINE: frozenset[str] = frozenset(
    {
        "a414d8d3",  # ALR
        "79e43a7f",  # AL monthly
        "74ba7b89",  # Draft ACAC
        "230a6f0c",  # EDR 1
        "bf6bbf6b",  # IBU Operations
        "4b2d4a2b",  # Annual Reporting
        "446b811a",  # ITFS monthly
        "7d9a1960",  # FME quarterly
        "82dd291f",  # CMI quarterly
    }
)


@dataclass(frozen=True)
class Competence:
    parties: frozenset[Instrument]
    measured_on: frozenset[str]


A, AP, B = Instrument.A, Instrument.A_PRIME, Instrument.B

# The four exclusions below were widened from n=1 (FME alone) to all nine by
# `tools/measure/agreement_matrix.py`, which re-measures B's blind counts on every
# workbook rather than remembering them. See docs/READER-COMPETENCE.md.
COMPETENCE: dict[str, Competence] = {
    "n_sheets": Competence(frozenset({A, AP, B}), ALL_NINE),
    "sheet_names": Competence(frozenset({A, AP, B}), ALL_NINE),
    "hidden_sheets": Competence(frozenset({A, AP, B}), ALL_NINE),
    "merged_ranges": Competence(frozenset({A, AP, B}), ALL_NINE),
    "n_cells": Competence(frozenset({A, AP}), ALL_NINE),
    "n_formula_cells": Competence(frozenset({A, AP}), ALL_NINE),
    "n_validations": Competence(frozenset({A, AP}), ALL_NINE),
    "n_defined_names": Competence(frozenset({A, AP}), ALL_NINE),
}

# Why each exclusion holds. Prose, because the mechanism is what a reader needs; the
# numbers are re-measured every run and live in the matrix.
EXCLUSION_MECHANISM: dict[str, str] = {
    "n_cells": "B counts non-None VALUES, not <c> elements; an empty styled cell is a cell",
    "n_formula_cells": "B returns ArrayFormula objects for array formulas and does not "
                       "expose shared dependents as formula cells",
    "n_validations": "B is namespace-blind: it reads the main namespace and discards the "
                     "x14 extension, with a warning it expects the caller to ignore",
    "n_defined_names": "B exposes workbook-scoped names only; sheet-local names are absent",
}

THREE_PARTY_FIELDS: tuple[str, ...] = tuple(
    f for f in AGREEMENT_FIELDS if B in COMPETENCE[f].parties
)
TWO_PARTY_FIELDS: tuple[str, ...] = tuple(
    f for f in AGREEMENT_FIELDS if B not in COMPETENCE[f].parties
)
