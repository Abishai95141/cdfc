"""P14-B4 — the predicate library. **Three of its fields are repairs, not columns.**

Each closes a way this surface could have printed a confident wrong number.

## (a) Two kill rates, side by side, and the GAP is the number a reviewer wants

G2's registry bar is `K/O >= 0.80` *on the fault classes the predicate claims to cover* — and the
claim is selected **after the campaign has run**, from the witnesses of mutants that already died.
A `sum_identity` predicate structurally blind to enum substitution, homoglyphs, carry desync and
vocabulary gaps scores `K/O = 0.21` overall, has three F01/F03 witnesses stamped on it, and is
admitted `BLOCKING` at `0.97`.

So `kr_claimed` and `kr_all_classes` render **in the same row, always both**, and a row that
carries one without the other does not render at all. A wide gap is not a failure — it is a
predicate honestly declaring a narrow scope — but it must be legible, because the alternative is a
`0.97` whose denominator the predicate chose for itself. That is M1, the founding defect.

## (b) SIX integers, not two, and `I` is the new one

`classify(clean, mutant)` marks a mutant `UNOBSERVABLE` when the two recalculated grids are
identical — and **a cell the evaluator could not compute is identical in both grids by
construction**. So every mutant whose only propagation path runs through an unimplemented
function, a cycle, or an excluded engine-disagreement cell is silently removed from `O`. Because
`O = G - U`, each exclusion **raises `K/O`**: the measurement error is correlated with the
quantity being measured, in the direction that flatters us.

`I` is published beside `U/G` every time either renders, **with the offending cells named**. An
integer without the cells behind it is an apology, not a measurement.

## (c) `instrument_label`, and it is not cosmetic

Every kill rate here rests on *"our evaluator reproduces the regulator's own values"*, which G-EVAL
certifies. If G-EVAL's arm-2 expectation file was written by the evaluator's own author, that
sentence is a self-check. The label is **read from `ci/GATES.md`, never from a constant** — the
same rule as `admission_state`. A constant is a claim about a gate; reading the gate is a
measurement of it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

GATES_MD: Final[Path] = Path("ci/GATES.md")

SAME_AUTHOR_LABEL: Final[str] = "SAME-AUTHOR — a weaker instrument"

# The three G-CORPUS outcomes. RESTRICTED is a VISIBLE STATE, never an undetected pass: the gate
# as originally stated was satisfiable by `synthesise(..., n=30)` from a corpus the product
# generated about itself, and its PASS branch said the FFR-bearing surfaces ship.
CorpusOutcome = Literal["PASS", "RESTRICTED", "FAIL"]

RESTRICTED_HEADER: Final[str] = "G-CORPUS: RESTRICTED"


class UnpairedKillRate(ValueError):
    """One kill rate rendered without the other. The gap between them is the finding."""


class IndeterminateNotNamed(ValueError):
    """`I > 0` with no cells named. An integer without its cells is an apology."""


class InstrumentLabelUnread(ValueError):
    """A kill rate was rendered without reading G-EVAL's independence label from `ci/GATES.md`."""


@dataclass(frozen=True, slots=True)
class KillRateCell:
    """SIX integers. `O == G - U - I`, and the identity is asserted rather than assumed."""

    G: int   # generated
    U: int   # unobservable
    I: int   # noqa: E741 — INDETERMINATE observability. The whole point of this field is its name.
    O: int   # observable
    R: int   # run
    K: int   # killed
    per_fault_class: dict[str, tuple[int, int]]
    indeterminate_cells: tuple[str, ...]
    instrument_label: str | None

    def __post_init__(self) -> None:
        if self.O != self.G - self.U - self.I:
            raise ValueError(
                f"O={self.O} but G-U-I={self.G - self.U - self.I}. A census whose parts do not "
                "close is the defect this project is named for."
            )
        if self.I > 0 and not self.indeterminate_cells:
            raise IndeterminateNotNamed(
                f"I={self.I} and no cells are named. `I` counts mutants whose observability could "
                "not be decided because recalculation touched a cell the evaluator could not "
                "compute; without the cells nobody can check whether the exclusion was fair, and "
                "every exclusion RAISES K/O in the direction that flatters us."
            )
        if self.K > self.O:
            raise ValueError(f"K={self.K} exceeds O={self.O}: more killed than were observable")

    @property
    def rate(self) -> tuple[int, int]:
        """`(K, O)` — the two integers, never a float. A float here would be a bare rate."""
        return (self.K, self.O)

    @property
    def unobservable_fraction(self) -> tuple[int, int]:
        """`(U, G)` — a property of OUR APPARATUS, and it renders with `I` beside it."""
        return (self.U, self.G)


def instrument_label(gates_md: Path = GATES_MD) -> str | None:
    """Read G-EVAL's independence from `ci/GATES.md`. **Never a constant.**

    Returns the literal `SAME-AUTHOR — a weaker instrument` when the registry records G-EVAL as
    `PASSED — NOT INDEPENDENT`, and `None` when it does not. `None` is not "independent": it is
    "the registry does not say", and the caller renders that as its own state.
    """
    if not gates_md.is_file():
        return None
    text = gates_md.read_text(encoding="utf-8")
    if re.search(r"G-EVAL.*NOT INDEPENDENT", text) or "PASSED — NOT INDEPENDENT" in text:
        return SAME_AUTHOR_LABEL
    return None


@dataclass(frozen=True, slots=True)
class FfrCell:
    text: str
    has_digit: bool


@dataclass(frozen=True, slots=True)
class LibraryRow:
    predicate_id: str
    version: int
    clause_quote: str
    clause_eid: str | None
    cel_source: str
    claims_fault_classes: tuple[str, ...]
    kr_claimed: KillRateCell | None
    kr_all_classes: KillRateCell | None
    ffr: FfrCell
    severity_tier: Literal["BLOCKING", "ADVISORY"] | None
    flag_everything_would_have_scored: KillRateCell | None
    state: Literal["ACTIVE", "PROVISIONAL", "QUARANTINED", "WITHDRAWN"]

    def __post_init__(self) -> None:
        if (self.kr_claimed is None) != (self.kr_all_classes is None):
            raise UnpairedKillRate(
                f"{self.predicate_id}: one kill rate is present and the other is not. G2's bar is "
                "measured over the classes the predicate CLAIMS, and the claim is selected after "
                "the campaign has run -- so a claimed rate alone is a number whose denominator the "
                "predicate chose for itself. They render together or not at all."
            )
        if self.kr_claimed is not None and not self.claims_fault_classes:
            raise ValueError(
                f"{self.predicate_id}: claims_fault_classes is empty and a claimed kill rate is "
                "rendered. An empty claim set makes `kr_claimed` a rate over nothing."
            )
        if self.kr_claimed is not None and self.kr_claimed.instrument_label is None:
            # None is admissible ONLY when the registry genuinely does not record NOT INDEPENDENT.
            if instrument_label() is not None:
                raise InstrumentLabelUnread(
                    f"{self.predicate_id}: ci/GATES.md records G-EVAL as NOT INDEPENDENT and this "
                    "row rendered a kill rate without the label. Every kill rate in this "
                    "programme rests on 'our evaluator reproduces the regulator's own values'."
                )
        if self.kr_claimed is not None and self.flag_everything_would_have_scored is None:
            raise ValueError(
                f"{self.predicate_id}: no flag-everything column. Without it a kill rate is REACH, "
                "not quality: a predicate that fires on everything kills everything."
            )


def render_corpus_header(outcome: CorpusOutcome, census: dict[str, int]) -> str:
    """The three outcomes render DISTINCTLY, and only two of them contain a digit.

    A restricted pass rendered as a pass is the whole failure G-CORPUS exists to prevent, one
    level up.
    """
    if outcome == "PASS":
        return f"G-CORPUS: PASS — n = {census.get('n_blind_or_real', 0)} filings"
    if outcome == "RESTRICTED":
        return (
            f"{RESTRICTED_HEADER} — digits are licensed only for the predicate classes this "
            f"corpus covers; every other row renders uninformative. n = {census.get('n', 0)} "
            f"filings, of which n_non_synthetic = {census.get('n_non_synthetic', 0)}"
        )
    parts = " · ".join(f"{k}: {v}" for k, v in sorted(census.items()))
    return (
        "G-CORPUS: FAIL — no false-failure rate is licensed and no digit appears. "
        f"corpus provenance census — {parts}"
    )
