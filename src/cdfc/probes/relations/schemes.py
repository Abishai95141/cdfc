"""P9-B2 — R-03, the scheme total against the FULL nine-member vocabulary.

`'1. Introduction'!D17` is *"Total No. of Schemes of the FME authorised by IFSCA"*, computed as
`SUM(D18:D20)` over three `COUNTIF` rows whose five wildcard patterns match **seven of the nine**
scheme types the workbook's own validation offers at `Dropdown!F3:F11`. *Special Situation Fund*
and *Family Investment Fund* match none of them (MEASURED — `tools/probes/p9_scheme_vocabulary.py`
re-derives it and exits non-zero if it stops reproducing).

**This relation is `EXPECTED`, therefore `INFORMATIONAL`, and the classification is the whole
point.** A violation is not the filer's error: it is the template's. A `NECESSARY` version of this
relation would fail the filer who filled the form **correctly** and pass the one who reproduced
the regulator's omission — the check inverted, on the cells where being right is hardest.

Step 2 of the authoring protocol requires naming the note that makes the exception lawful, and
*"if you cannot name the note, it is not EXPECTED; it is unfinished."* The note here is
`TD-01` in `probes/template_defects.yaml`, which carries a re-runnable evidence command; that is a
stronger authority than a guidance paragraph, because it can fail.
"""

from __future__ import annotations

from typing import Final

from cdfc.predicates.harvest import cel_path, cel_segment

SHEET: Final[str] = "1. Introduction"
TOTAL_CELL: Final[str] = "D17"
TYPE_COL: Final[str] = "G"
FIRST_ROW: Final[int] = 54
LAST_ROW: Final[int] = 63

# The vocabulary the harvest already resolves from the pinned blank for this column. Naming the
# same key rather than minting a second one is deliberate: two vocabularies for one column is two
# lists, and the one that drifts is the one nobody is reading.
VOCAB: Final[str] = f"template.vocab.{cel_segment(SHEET)}_{TYPE_COL.lower()}{FIRST_ROW}"

EVIDENCE: Final[str] = (
    "'1. Introduction'!D17 = SUM(D18:D20) over COUNTIF patterns *Angel*, *Venture*, *Restricted*, "
    "*Retail* and *Exchange Traded Fund*, against the nine-member scheme-type vocabulary at "
    "Dropdown!F3:F11. Seven of nine match. MEASURED 14 Aug 2026; re-derive with "
    "`tools/probes/p9_scheme_vocabulary.py`, which exits non-zero if the claim stops holding."
)

GUIDANCE_NOTE: Final[str] = (
    "Template defect TD-01 in src/cdfc/probes/template_defects.yaml, with its evidence command. "
    "The disagreement is a property of the regulator's formula, not of the filer, so a violation "
    "is INFORMATIONAL and can never fail a filing."
)


def _p(ref: str) -> str:
    return f"filing.{cel_path(SHEET, ref)}"


def type_cells() -> list[str]:
    return [f"{TYPE_COL}{r}" for r in range(FIRST_ROW, LAST_ROW + 1)]


def precondition() -> str:
    """The total is present AND at least one scheme type is declared. Without the second clause
    an empty filing satisfies `0 == 0` and scores a clean sweep — NC-R01."""
    declared = " || ".join(f'{_p(c)}.v != ""' for c in type_cells())
    return f"has({_p(TOTAL_CELL)}.v) && ({declared})"


def expr() -> str:
    """`D17` equals the number of `G54:G63` cells holding a member of the FULL vocabulary."""
    terms = " + ".join(f"({_p(c)}.v in {VOCAB} ? 1 : 0)" for c in type_cells())
    return f"{_p(TOTAL_CELL)}.v == {terms}"


def witness() -> str:
    return (
        "["
        + ", ".join([f"{_p(TOTAL_CELL)}.__cell__"] + [f"{_p(c)}.__cell__" for c in type_cells()])
        + "]"
    )


def build() -> dict[str, str]:
    return {"precondition": precondition(), "expr": expr(), "witness": witness()}
