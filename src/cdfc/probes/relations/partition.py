"""P9-B2 — the partition family: two independent breakups of the same money must agree.

**The artifact fact, measured first-hand and it is the whole reason this relation exists.**
`'4. Investors'` carries the same per-scheme funds-raised figure three times, under three
different breakups:

| table | heading row | per-scheme rows | totals | breakup |
|---|---:|---|---|---|
| 4.1 (second of that number) | 18 | 21–30 | `AA` amount, `AB` investors | by investor category, 12 columns |
| 4.2 (second of that number) | 39 | 42–51 | `G` amount, `H` investors | by accreditation status, 2 columns |
| 4.3 | 57 | 60–69 are COUNTRIES | **none** | by country, schemes across the columns |

**No formula in the workbook reads `AA21`, `G42` or any country cell** (MEASURED, 14 Aug 2026 —
`build_precedent_map(...).by_formula_cell` returns an empty reader set for all three). The two
totals are computed by the workbook's own `SUM`s from **disjoint filer inputs**, and nothing
relates them. A filer can report USD 100m by category and USD 90m by accreditation status and the
workbook is silent.

**The country arm is REFUSED, and the refusal is recorded rather than quietly dropped.** Table 4.3
has no total row and no total column, so the sum would have to be taken over ten country cells per
scheme — and a blank numeric cell is *absent* from the fact model, not zero, so a `has()`-guarded
sum over them would be un-runnable on every filing that leaves one country blank, which is every
filing. Expressing it needs a range host function that does not exist. `docs/RELATION-REVIEW.md`
carries the row.

**τ = 0, and the argument is not "counts get no tolerance" — it is stronger.** `facts/build.py`'s
`_coerce` returns a NON-INTEGRAL value as TEXT, which is type-mismatched at pre-flight and becomes
`NOT_RUN(source_unreadable)`. So every numeric value this relation can ever see is a whole USD
Million, and two exact partitions of one whole number agree exactly or disagree by at least one.
**This also keeps the relation clear of the unit defect measured in the harvest** — see
`docs/measurements/P9-template-diff-ceiling.md`, open item (b): the harvested `τ` literals are
expressed in `MILLI_USD_MILLION` and compared against an unscaled tree, so they are 1,000× too
wide. A relation with no tolerance literal cannot inherit that.
"""

from __future__ import annotations

from typing import Final

from cdfc.predicates.harvest import cel_path

SHEET: Final[str] = "4. Investors"

# Read off the blank's own table headings and formula rows BY A HUMAN, once. `SCHEMES` is the
# number of per-scheme rows the two tables share.
#
# **NOTHING IN THIS MODULE CHECKS THAT AGAINST A WORKBOOK, and this comment used to claim
# `build()` did.** `build()` takes no arguments, opens no file and reads no template — it returns
# the three CEL strings composed from the constants above, the same strings on every call. It
# cannot refuse a template it never sees. What this module honestly is: a HAND-SPECIFIED relation
# whose cell addresses were typed in from one reading of one blank, valid only for the FME
# template named in `EVIDENCE`. Against a template whose two tables disagreed in length it would
# emit a well-formed expression addressing the wrong rows, silently. The thing in this build that
# does notice a different template is the `template_sha256` pin recorded in the run manifest and
# re-checked by `cdfc verify`, which is outside this module entirely.
CATEGORY_FIRST_ROW: Final[int] = 21
ACCREDITATION_FIRST_ROW: Final[int] = 42
SCHEMES: Final[int] = 10

CATEGORY_AMOUNT_COL: Final[str] = "AA"
CATEGORY_COUNT_COL: Final[str] = "AB"
ACCREDITATION_AMOUNT_COL: Final[str] = "G"
ACCREDITATION_COUNT_COL: Final[str] = "H"

EVIDENCE: Final[str] = (
    "'4. Investors' Tables 4.1 (rows 21-30, by investor category, totals AA/AB) and 4.2 "
    "(rows 42-51, by accreditation status, totals G/H) are two breakups of the same per-scheme "
    "funds-raised figure, computed by the workbook's own SUMs from DISJOINT filer inputs. No "
    "formula in the workbook reads AA21, G42 or any cell of the country table — MEASURED 14 Aug "
    "2026 via build_precedent_map(...).by_formula_cell, which returns an empty reader set for all "
    "three. The workbook enforces agreement between none of them."
)


def cells(scheme: int) -> dict[str, str]:
    """The four `Sheet!Ref` cells of one scheme's row pair. 1-based scheme index."""
    if not 1 <= scheme <= SCHEMES:
        raise ValueError(f"scheme {scheme} is outside 1..{SCHEMES}")
    cat = CATEGORY_FIRST_ROW + scheme - 1
    acc = ACCREDITATION_FIRST_ROW + scheme - 1
    return {
        "category_amount": f"{SHEET}!{CATEGORY_AMOUNT_COL}{cat}",
        "category_count": f"{SHEET}!{CATEGORY_COUNT_COL}{cat}",
        "accreditation_amount": f"{SHEET}!{ACCREDITATION_AMOUNT_COL}{acc}",
        "accreditation_count": f"{SHEET}!{ACCREDITATION_COUNT_COL}{acc}",
    }


def all_cells() -> list[str]:
    out: list[str] = []
    for j in range(1, SCHEMES + 1):
        out.extend(cells(j).values())
    return out


def _p(cell: str) -> str:
    sheet, ref = cell.rsplit("!", 1)
    return f"filing.{cel_path(sheet, ref)}"


def precondition() -> str:
    """**Written FIRST, before `expr`.** Written second, a precondition is written to make the
    relation pass.

    Non-degeneracy has two clauses and both are needed. `has()` on every side, because a
    comparison against an absent value is not false, it is meaningless. And **at least one
    non-zero**, because an all-zero filing satisfies every partition identity by construction —
    which is NC-R01, and it is the same defect as the all-zero grid the blank itself ships.
    """
    present = " && ".join(
        f"has({_p(c)}.v)" for j in range(1, SCHEMES + 1) for c in cells(j).values()
    )
    nonzero = " || ".join(
        f"{_p(cells(j)['category_amount'])}.v != 0 || {_p(cells(j)['category_count'])}.v != 0"
        for j in range(1, SCHEMES + 1)
    )
    return f"({present}) && ({nonzero})"


def expr() -> str:
    """Per scheme, the amount totals agree and the investor-count totals agree. EXACTLY."""
    parts = []
    for j in range(1, SCHEMES + 1):
        c = cells(j)
        parts.append(f"{_p(c['category_amount'])}.v == {_p(c['accreditation_amount'])}.v")
        parts.append(f"{_p(c['category_count'])}.v == {_p(c['accreditation_count'])}.v")
    return " && ".join(parts)


def witness() -> str:
    """The cells a reader opens: both totals of every scheme, in row order."""
    return "[" + ", ".join(f"{_p(c)}.__cell__" for c in all_cells()) + "]"


def schema_keys() -> tuple[str, ...]:
    keys: set[str] = set()
    for c in all_cells():
        keys.add(f"{_p(c)}.v")
        keys.add(f"{_p(c)}.__cell__")
    return tuple(sorted(keys))


def build() -> dict[str, str]:
    """`{precondition, expr, witness}` for the catalogue loader."""
    return {"precondition": precondition(), "expr": expr(), "witness": witness()}
