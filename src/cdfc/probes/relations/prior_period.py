"""P9-B2 — R-07, opening/closing continuity, and the honest report that it cannot run.

**This build's most useful output may be this file.** We hold **zero** real filed FME returns, so
a relation needing two consecutive filings of one entity is structurally un-runnable today. The
temptation is to omit it; omitting it is the coverage lie in miniature — a layer that ships `n − k`
relations while claiming `n`.

So R-07 is authored, reviewed, loaded, and reports
`NOT_RUN(not_run.input_unavailable.prior_period)` on every run. **Absence and
`NOT_RUN` are different claims**, and only the second one is a coverage declaration.

The relation itself is written out rather than left as a gesture, because a placeholder that says
*"prior-period continuity"* and nothing more cannot be reviewed, cannot be qualified, and cannot
be checked the day a second filing arrives.
"""

from __future__ import annotations

from typing import Final

from cdfc.predicates.harvest import cel_path

SHEET: Final[str] = "3. Portfolio"

# Table 3.1's per-scheme Total Portfolio Value, which is the quantity a closing balance carries
# into the next period's opening balance. Rows 3-12 are the ten scheme rows (MEASURED: the
# heading is at row 1, the column header at row 2, and `O3:O12` are the SUM(C:N) totals).
TOTAL_COL: Final[str] = "O"
FIRST_ROW: Final[int] = 3
SCHEMES: Final[int] = 10

EVIDENCE: Final[str] = (
    "'3. Portfolio'!A129, note 2: \"'Total Portfolio Value' of the scheme is same as Column 'O' "
    "of Table 3.1.\" The closing Total Portfolio Value of one quarter is the opening value of the "
    "next, so two consecutive filings of one entity must agree at that boundary. MEASURED from "
    "the pinned blank, 14 Aug 2026."
)

WHY_UNRUNNABLE: Final[str] = (
    "We hold ZERO real filed FME returns, so no two consecutive filings of one entity exist. "
    "This is a fact about the corpus, not about the relation, and it is reported as "
    "NOT_RUN(not_run.input_unavailable.prior_period) rather than by omission."
)


def _p(sheet: str, ref: str) -> str:
    return f"filing.{cel_path(sheet, ref)}"


def cells() -> list[str]:
    return [f"{SHEET}!{TOTAL_COL}{FIRST_ROW + i}" for i in range(SCHEMES)]


def precondition() -> str:
    """Both periods present AND at least one non-zero. The second clause is what stops an
    all-zero pair of filings scoring a clean sweep through continuity."""
    present = " && ".join(
        f"has({_p(SHEET, r.split('!')[1])}.v) && has(prior.{cel_path(SHEET, r.split('!')[1])}.v)"
        for r in cells()
    )
    nonzero = " || ".join(f"{_p(SHEET, r.split('!')[1])}.v != 0" for r in cells())
    return f"({present}) && ({nonzero})"


def expr() -> str:
    return " && ".join(
        f"{_p(SHEET, r.split('!')[1])}.v == prior.{cel_path(SHEET, r.split('!')[1])}.v"
        for r in cells()
    )


def witness() -> str:
    return "[" + ", ".join(f"{_p(SHEET, r.split('!')[1])}.__cell__" for r in cells()) + "]"


def build() -> dict[str, str]:
    """**The `prior.` root is NOT in `BOUND_ROOTS`.**

    `cel_profile.BOUND_ROOTS` is `{filing, template}`, and a third free identifier is refused at
    compile time — deliberately, because it is how a predicate reads something nobody declared.
    So this relation does not merely lack an input: **it is not expressible in the admitted subset
    at all**, and adding a root to make it expressible would widen the subset for a relation that
    cannot be run or qualified against anything.

    That is the honest finding, and it is stronger than *"we have no second filing"*. It is
    published in `docs/measurements/P9-relation-runnability.md` and in `docs/RELATION-REVIEW.md`.
    """
    return {"precondition": precondition(), "expr": expr(), "witness": witness()}
