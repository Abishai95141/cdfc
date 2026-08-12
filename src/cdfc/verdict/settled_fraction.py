"""P5-B4 — the settled fraction, as an OBJECT. There is no bare fraction anywhere in this system.

Four rules a reader should be able to check by eye:

1. **`fraction` is never serialised without its counts.** It is a field of this object and this
   object is the only serialisation. `cellsTotal` and `inScope` render together, always — a
   shrinking denominator must be visible on the page, not merely correct in the object.
2. **`admissionState` is computed**, from whether every active predicate carries a G4 record.
   It is `PRE-GATE` today, and the caveat beside it is required and non-empty while it is.
3. **`null` is not zero and not omitted.** Three outcomes, three meanings. On an `INVALID` run the
   field is PRESENT and `null` (D-P5-06) — `null`, `forbidden` and `omitted` are three different
   things and three documents asserted three different ones about the same field.
4. **`noPredicate` stays in the denominator.** XCCDF removes `notchecked` because its denominator
   is a human-authored benchmark; ours is induced from the regulator's own published template, so
   *no predicate exists* is a gap in **us**. Removing it would let the fraction rise by doing
   nothing, and the justification ships attached to the number.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Literal

from cdfc.verdict.closure import ClosurePartition
from cdfc.verdict.states import ItemState, in_scope

QUANTUM = Decimal("0.0001")

ADMISSIBILITY_CAVEAT = (
    "PRE-GATE: none of the predicates producing this number is admitted under G4. The number "
    "says how much of the denominator a check ran over, not that any check is right."
)

DENOMINATOR_WARNING = (
    "The denominator is the template's unlocked-cell mask under generator rule v3, computed twice "
    "and agreed. It has never been checked against a person filling the form in, so it is "
    "PROVISIONAL-UNVALIDATED: it may be larger or smaller than the set a filer actually completes."
)

NO_MASK_SOURCE = (
    "this template ships no cell-protection mask, so its field surface is not derivable. A naive "
    "unlocked count returns a small number, which looks like a small answer rather than like no "
    "answer — so the fraction is null and this sentence is published in its place."
)


@dataclass(frozen=True, slots=True)
class Denominator:
    source: str
    generatorRule: str
    fieldSurface: int | None
    computedTwiceAgreed: bool
    validationState: str


@dataclass(frozen=True, slots=True)
class SettledCounts:
    passed: int
    failed: int

    @property
    def total(self) -> int:
        return self.passed + self.failed


@dataclass(frozen=True, slots=True)
class UnsettledCounts:
    indeterminate: int
    notRun: int
    noPredicate: int
    error: int


@dataclass(frozen=True, slots=True)
class DeclaredGap:
    what: str
    why: str


@dataclass(frozen=True, slots=True)
class SettledFraction:
    denominator: Denominator
    cellsTotal: int
    outOfScope: int
    outOfScopeRetained: int
    informational: int
    informationalRetained: int
    inScope: int
    settled: SettledCounts
    unsettled: UnsettledCounts
    fraction: Decimal
    admissionState: Literal["PRE-GATE", "POST-GATE"]
    admissibilityCaveat: str
    denominatorWarning: str
    declaredGaps: tuple[DeclaredGap, ...] = ()
    residue: None = None                 # populated by P10; null here
    requalificationFlagged: int = 0
    loweredByRollup: int = 0

    def __post_init__(self) -> None:
        if self.admissionState == "PRE-GATE" and not self.admissibilityCaveat:
            raise ValueError(
                "a PRE-GATE fraction with no caveat is a coverage number presented as a verdict"
            )
        if not self.denominatorWarning:
            raise ValueError("the denominator's warning is required; it is what it is a fraction OF")
        if isinstance(self.fraction, float):
            raise TypeError("the fraction is a Decimal. A float headline is not re-derivable.")

    def as_row(self) -> dict[str, Any]:
        """The ONLY serialisation. `fraction` never leaves this object on its own."""
        d = asdict(self)
        d["fraction"] = str(self.fraction)
        d["settled"]["total"] = self.settled.total
        return d


def fraction_of(part: ClosurePartition) -> Decimal:
    """`settled.total / inScope`, quantised. Decimal throughout — no float, ever."""
    if part.inScope <= 0:
        return Decimal("0").quantize(QUANTUM)
    return (Decimal(part.settled) / Decimal(part.inScope)).quantize(QUANTUM, rounding=ROUND_HALF_UP)


def compute(
    part: ClosurePartition,
    sel: Any,
    den: Denominator,
    run_state: str,
    *,
    canary_silent: bool = False,
    declared_gaps: Sequence[DeclaredGap] = (),
) -> SettledFraction | None:
    """`None` — i.e. `settledFraction: null` — and NEVER a zero, when the run is INVALID, the
    template ships no mask, or a canary was silent.

    D-P5-06: `None` here means the SERIALISER EMITS THE KEY WITH A JSON null. It never omits it.
    """
    if run_state == "INVALID" or den.fieldSurface is None or canary_silent:
        return None

    from cdfc.evaluate.selection import admission_state

    state = admission_state(sel)
    return SettledFraction(
        denominator=den,
        cellsTotal=part.cellsTotal,
        outOfScope=part.outOfScope,
        outOfScopeRetained=part.outOfScopeRetained,
        informational=part.informational,
        informationalRetained=part.informationalRetained,
        inScope=part.inScope,
        settled=SettledCounts(passed=part.settledPass, failed=part.settledFail),
        unsettled=UnsettledCounts(
            indeterminate=part.indeterminate, notRun=part.notRun,
            noPredicate=part.noPredicate, error=part.error,
        ),
        fraction=fraction_of(part),
        admissionState=state,  # type: ignore[arg-type]
        admissibilityCaveat=ADMISSIBILITY_CAVEAT if state == "PRE-GATE" else "",
        denominatorWarning=DENOMINATOR_WARNING,
        declaredGaps=tuple(declared_gaps),
        requalificationFlagged=part.requalify,
        loweredByRollup=part.loweredByRollup,
    )


def serialise(sf: SettledFraction | None) -> dict[str, Any]:
    """D-P5-06: the key is PRESENT and `null`. It is never omitted and never zero."""
    return {"settledFraction": None if sf is None else sf.as_row()}


class FractionRoseError(AssertionError):
    """The settled fraction rose. The one function that expresses D-P5-05's claim as an assertion.

    The property test, P9's defect-table guard and the empty-filing control all call this rather
    than each re-deriving the comparison — three derivations are three chances to derive it
    differently.
    """

    def __init__(self, before: Decimal, after: Decimal, note: str = "") -> None:
        self.before = before
        self.after = after
        super().__init__(
            f"the settled fraction rose from {before} to {after}{': ' + note if note else ''}. "
            "A headline number that rewards filling in less is a number that rewards the "
            "behaviour the product exists to detect."
        )


def assert_fraction_did_not_rise(
    before: SettledFraction | None, after: SettledFraction | None, note: str = ""
) -> None:
    if before is None or after is None:
        return
    if after.fraction > before.fraction:
        raise FractionRoseError(before.fraction, after.fraction, note)


def static_settled_cells(candidates: Sequence[Any], schema: Any) -> frozenset[str]:
    """Cells reachable by at least one harvested predicate. Computed before any evaluation."""
    from cdfc.predicates.ast_walker import bound_cells

    out: set[str] = set()
    for c in candidates:
        out |= bound_cells(c, schema)
    return frozenset(out)


def runtime_settled_cells(cells: Sequence[Any]) -> frozenset[str]:
    """Cells whose ROLLED-UP state is PASS or FAIL. Under the binding precedence this can be
    lower than the static figure — a cell read by one passing and one not-run predicate is
    unsettled, and that is the audit's resolution having an effect."""
    return frozenset(
        c.stable_key for c in cells if c.state in (ItemState.PASS, ItemState.FAIL)
    )


def cells_removed_from_scope(cells: Sequence[Any]) -> tuple[tuple[str, str, str], ...]:
    """`(stable_key, state, reason)` for every cell that LEFT the denominator, with its pair.

    A counterexample to the fraction property names the pair, which is the line of `states.py` to
    change. `in_scope` is consulted here too — this function reports the same decision, it does
    not make a second one.
    """
    out = []
    for c in cells:
        if not in_scope(c.state, c.reason, getattr(c, "scope_kind", None)):
            out.append((c.stable_key, str(c.state), str(c.reason)))
    return tuple(sorted(out))
