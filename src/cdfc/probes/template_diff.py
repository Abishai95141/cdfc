"""P9-B1 — `TEMPLATE_DIFF`, predicate #1: the filed value against the template's own formula.

**The check nothing else in the design can perform.** A filer who overwrites a formula cell with
a literal deletes the inconsistency along with the formula. Every harvested predicate reads the
*filed* values, so the carry and sum identities are satisfied by construction — the filer's
literal is what the carry now carries. Only a comparison against the pinned blank sees it.

**Two comparisons, and conflating them is the defect this module is written around.**

| | what it absorbs | why it exists |
|---|---|---|
| `REPRESENTATION_EPS` | a relative `1e-15` | LibreOffice writes IEEE-754 doubles at ~16 significant digits; we compute in `Decimal` at 34. A difference at the 16th digit is a statement about **float serialisation**, not about the filer. Arm 1 learned this the expensive way: 100 of its first 129 "disagreements" were this and nothing else. |
| `τ(n) = 5n` units | half a unit per summand, **on money only** | a rounding allowance for the **filer**, in integer `MILLI_USD_MILLION`. `probes/degree.py` decides who gets it, from the regulator's own printed units. |

They are applied in that order and reported separately. A single merged epsilon would let a
missing investor hide behind a float, and would let a float artefact be reported as a filing
error — the two mistakes point in opposite directions and both are invisible once merged.

**Applicability is a `ScopeKind`, not a bool** (arbitration C3). The blank's own cached grid is
essentially zeros and `"NA"` strings, so without a precondition an unfilled filing sweeps the
flagship's door — NC-R01. But `OUT_OF_SCOPE` leaves the denominator, so the precondition is also
the mechanism by which a filer who fills in **less** could score **better**. The split is what
closes it: `DECLARED_CHARACTERISTIC` (no field-surface precedent could ever exist — a fact about
the INSTRUMENT) leaves; `PREDICATE_PRECONDITION` (precedents exist and this filing left them
empty — a fact about the PREDICATE) **stays counted and accuses its own predicate**.

**The oracle is authoritative and not correct.** `template_defects.yaml` names the cells where the
regulator's own formula is wrong for this `template_sha256`. A declared defect is `INFORMATIONAL`,
never `FAIL` — except where `INFORMATIONAL` would *raise the settled fraction*, because
`INFORMATIONAL` leaves the denominator too. For a bound cell whose only evaluation is the
defective relation, `fraction = s/(i−1) > s/i`: **declaring a defect would raise the headline.**
Those cells take `NO_PREDICATE(no_predicate.rule_ambiguous)` instead, which stays in the
denominator. Both dispositions are true of a defective oracle; only one of them is honest about
the arithmetic (F14).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Final, Literal

from cdfc.schema.anchor import Anchor
from cdfc.calc.evaluate import Value, recalculate
from cdfc.calc.errors import is_error
from cdfc.facts.units import UNITS_PER_USD_MILLION
from cdfc.probes.degree import Assignment, degree_map, tau_for
from cdfc.probes.precedents import CellKey, PrecedentMap
from cdfc.probes.relations import ScopeKind
from cdfc.verdict.reasons import ReasonCode
from cdfc.verdict.states import ItemState

METHOD: Final[str] = "TEMPLATE_DIFF"
WARRANT: Final[str] = "DETERMINISTIC"
PROVENANCE: Final[str] = "COMPUTED"

# A relative difference below this is float serialisation, not a finding. It is NOT a tolerance:
# it never grows with the number of summands and it never applies to an integer difference.
REPRESENTATION_EPS: Final[Decimal] = Decimal("1e-15")


class TemplateDiffError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DiffFinding:
    formula_cell: CellKey
    state: ItemState
    reason: ReasonCode | None
    scope_kind: ScopeKind | None
    filed_value: str | None
    recomputed: str | None
    tau: int                          # MILLI_USD_MILLION units. 0 for every degree-0 cell.
    degree: int
    bound_cells: frozenset[CellKey]
    witness: tuple[CellKey, ...]
    detail: str = ""
    defect_id: str | None = None
    method: str = METHOD
    warrant: str = WARRANT
    provenance: str = PROVENANCE

    def __post_init__(self) -> None:
        if self.state is ItemState.FAIL and not self.bound_cells:
            raise TemplateDiffError(
                f"{self.formula_cell} produced a FAIL bound to no cell. A finding that settles "
                "nothing is a finding nobody can act on, and `cells_bound == 0` is a G1 refusal "
                "— it must never be reachable at run time."
            )
        if (
            self.state is ItemState.OUT_OF_SCOPE
            and self.reason is ReasonCode.OOS_NOT_APPLICABLE
            and self.scope_kind is None
        ):
            raise TemplateDiffError(
                f"{self.formula_cell}: OUT_OF_SCOPE(not_applicable) with no scope_kind. Whether "
                "this cell leaves the in-scope denominator is then undecided, and `in_scope()` "
                "fails closed rather than guessing."
            )


@dataclass(frozen=True, slots=True)
class TemplateDefect:
    cell: CellKey
    template_sha256: str
    description: str
    evidence_command: str
    declared_by: str
    declared_at: str
    id: str = ""


@dataclass(frozen=True, slots=True)
class TemplateDefectTable:
    by_cell: Mapping[CellKey, TemplateDefect] = field(default_factory=dict)

    def for_template(self, template_sha256: str) -> TemplateDefectTable:
        """A defect is declared AGAINST A TEMPLATE DIGEST. A defect table applied to a template
        it was not declared for is an opinion about a different artifact."""
        return TemplateDefectTable(
            {k: v for k, v in self.by_cell.items() if v.template_sha256 == template_sha256}
        )


def load_defects(path: Path | None = None) -> TemplateDefectTable:
    import yaml

    p = path or Path(__file__).with_name("template_defects.yaml")
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    out: dict[CellKey, TemplateDefect] = {}
    for i, row in enumerate(raw.get("defects", []) or [], start=1):
        missing = [
            k for k in ("cell", "template_sha256", "description", "evidence_command",
                        "declared_by", "declared_at")
            if not row.get(k)
        ]
        if missing:
            raise TemplateDiffError(
                f"template_defects.yaml row {i} is missing {missing}. **A defect table without "
                "re-runnable evidence is a list of opinions**, and the list would grow to cover "
                "every relation someone found inconvenient."
            )
        d = TemplateDefect(
            cell=row["cell"], template_sha256=row["template_sha256"],
            description=row["description"].strip(), evidence_command=row["evidence_command"],
            declared_by=row["declared_by"], declared_at=str(row["declared_at"]),
            id=row.get("id", f"TD-{i:02d}"),
        )
        out[d.cell] = d
    return TemplateDefectTable(out)


# --------------------------------------------------------------------------------
# applicability
# --------------------------------------------------------------------------------


def applicable(
    filed: Mapping[tuple[str, str], Value], formula_cell: CellKey, pm: PrecedentMap
) -> ScopeKind:
    """`IN_SCOPE` · `DECLARED_CHARACTERISTIC` · `PREDICATE_PRECONDITION`. **Never a bool.**

    - no field-surface precedent EXISTS ⇒ `DECLARED_CHARACTERISTIC`. No relation over this
      template could ever reach the cell: a fact about the INSTRUMENT, and it leaves the
      denominator legitimately.
    - precedents exist and THIS FILING left every one of them empty ⇒ `PREDICATE_PRECONDITION`.
      A fact about the PREDICATE. It stays in the denominator and is flagged for G3
      re-qualification, because a degenerate precondition is what G3 exists to reject.
    """
    bound = pm.in_field_surface.get(formula_cell, frozenset())
    if not bound:
        return "DECLARED_CHARACTERISTIC"
    for cell in bound:
        sheet, ref = cell.rsplit("!", 1)
        v = filed.get((sheet, ref))
        if v is not None and v != "":
            return "IN_SCOPE"
    return "PREDICATE_PRECONDITION"


# --------------------------------------------------------------------------------
# comparison
# --------------------------------------------------------------------------------


def _as_decimal(v: Any) -> Decimal | None:
    if v is None or isinstance(v, bool) or is_error(v):
        return None
    if isinstance(v, Decimal):
        return v
    try:
        return Decimal(str(v).strip())
    except (InvalidOperation, ValueError):
        return None


def agree(filed: Any, recomputed: Any, tau_units: int) -> bool:
    """`True` when the two values are the same answer.

    Numeric: equal, or within `REPRESENTATION_EPS` relatively, or within `τ` absolutely.
    Non-numeric: compared as trimmed, case-folded strings — `"NA"` and `"na"` are one answer,
    and `"NA"` against `12` is not.
    """
    a, b = _as_decimal(filed), _as_decimal(recomputed)
    if a is None or b is None:
        fa = "" if filed is None else str(filed).strip().casefold()
        fb = "" if recomputed is None else str(recomputed).strip().casefold()
        return fa == fb
    if a == b:
        return True
    delta = abs(a - b)
    if a != 0 and delta / abs(a) < REPRESENTATION_EPS:
        return True
    # τ is an integer count of MILLI_USD_MILLION; workbook values are in USD Million. Comparing
    # `delta * 1000 <= tau` keeps the tolerance an INTEGER and avoids `to_units`, which REFUSES
    # a value carrying more precision than the unit can hold — correct at the boundary where
    # money enters the system, and wrong here, where the value came out of a foreign engine.
    return delta * UNITS_PER_USD_MILLION <= Decimal(tau_units)


def _render(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return str(v.normalize())
    return str(v)


def _n_summands(pm: PrecedentMap, cell: CellKey) -> int:
    """`n` for `τ(n) = 5n`: the number of field-surface cells the answer is summed over.

    Using the BOUND set and not the formula's textual argument count is deliberate — a
    `SUM(C7:N7)` whose range is half locked is a sum over the unlocked half, and a tolerance
    scaled by the textual width would be larger than the arithmetic warrants.
    """
    return len(pm.in_field_surface.get(cell, frozenset()))


# --------------------------------------------------------------------------------
# the relation
# --------------------------------------------------------------------------------


def template_diff(
    filed: Mapping[tuple[str, str], Value],
    pm: PrecedentMap,
    defects: TemplateDefectTable,
    *,
    degrees: Mapping[CellKey, Assignment] | None = None,
    otherwise_bound: frozenset[CellKey] = frozenset(),
    blob: Path | None = None,
) -> list[DiffFinding]:
    """One finding per formula cell of the pinned blank, in `(sheet, row, column)` order.

    `otherwise_bound` is the set of field-surface cells some OTHER evaluation reaches. It is
    read only by the F14 fallback, and it is passed in rather than computed here because this
    module must not reach into `cdfc.predicates` — that is NC-D02's rule, and a probe that
    imported the predicate registry to decide a denominator question would be the numerator
    choosing its own denominator with an extra step.
    """
    if degrees is None:
        if blob is None:
            raise TemplateDiffError(
                "template_diff needs either a degree map or the blank it should build one from. "
                "Defaulting every cell to degree 0 would silently withhold τ from money, and "
                "defaulting to 1 would silently grant it to counts."
            )
        degrees = degree_map(blob)

    declared = defects.for_template(pm.template_sha256).by_cell

    grid = recalculate(
        pm.as_pairs(pm.formula_text),
        {k: v for k, v in filed.items() if Anchor.cell(k[0], k[1]).render() not in pm.formula_text},
        formula_source="TEMPLATE",
        deferred=pm.as_pairs(pm.deferred),
    )

    out: list[DiffFinding] = []
    for cell in sorted(set(pm.formula_text) | set(pm.deferred), key=_cell_order):
        sheet, ref = cell.rsplit("!", 1)
        bound = pm.in_field_surface.get(cell, frozenset())
        assignment = degrees.get(cell)
        degree = assignment.degree if assignment else 0
        tau = tau_for(assignment, _n_summands(pm, cell)) if assignment else 0

        scope = applicable(filed, cell, pm)
        if scope != "IN_SCOPE":
            out.append(DiffFinding(
                formula_cell=cell, state=ItemState.OUT_OF_SCOPE,
                reason=ReasonCode.OOS_NOT_APPLICABLE, scope_kind=scope,
                filed_value=None, recomputed=None, tau=tau, degree=degree,
                bound_cells=bound, witness=(cell,),
                detail=(
                    "no field-surface precedent exists for this cell on this template"
                    if scope == "DECLARED_CHARACTERISTIC"
                    else "this filing left every field-surface precedent of this cell empty"
                ),
            ))
            continue

        # ABSENT FROM THE GRID IS `NOT_RUN`, NEVER A MISMATCH. A cell the evaluator did not
        # produce a value for is one we could not check; comparing `None` against the filed value
        # would turn "our apparatus said nothing" into "your filing is wrong", which is the exact
        # inversion `error.predicate_raised` and `not_run.source_unreadable` exist to keep apart.
        if cell in pm.deferred or (sheet, ref) in grid.not_run or (sheet, ref) not in grid.values:
            why = (
                pm.deferred.get(cell)
                or grid.not_run.get((sheet, ref))
                or "the evaluator produced no value for this cell"
            )
            out.append(DiffFinding(
                formula_cell=cell, state=ItemState.NOT_RUN,
                reason=ReasonCode.NR_SOURCE_UNREADABLE, scope_kind=None,
                filed_value=_render(filed.get((sheet, ref))), recomputed=None,
                tau=tau, degree=degree, bound_cells=bound, witness=(cell,),
                detail=f"the template's formula could not be evaluated: {why}",
            ))
            continue

        recomputed = grid.values.get((sheet, ref))
        actual = filed.get((sheet, ref))
        if agree(actual, recomputed, tau):
            out.append(DiffFinding(
                formula_cell=cell, state=ItemState.PASS, reason=None, scope_kind="IN_SCOPE",
                filed_value=_render(actual), recomputed=_render(recomputed),
                tau=tau, degree=degree, bound_cells=bound, witness=(cell,),
            ))
            continue

        defect = declared.get(cell)
        if defect is not None:
            # F14, IN CODE and not in the declarer's judgement. `INFORMATIONAL` leaves the
            # denominator; for a cell nothing else reaches, that RAISES the settled fraction, so
            # adding a row to the defect table would improve the headline. Where it would, the
            # honest disposition is the one that stays counted.
            sole = frozenset(bound) - otherwise_bound
            if sole:
                out.append(DiffFinding(
                    formula_cell=cell, state=ItemState.NO_PREDICATE,
                    reason=ReasonCode.NP_RULE_AMBIGUOUS, scope_kind=None,
                    filed_value=_render(actual), recomputed=_render(recomputed),
                    tau=tau, degree=degree, bound_cells=bound, witness=(cell,),
                    defect_id=defect.id,
                    detail=(
                        f"the template's own formula is defective here ({defect.id}); "
                        f"{len(sole)} bound cell(s) have no other evaluation, so INFORMATIONAL "
                        "would remove them from the denominator and raise the fraction"
                    ),
                ))
            else:
                out.append(DiffFinding(
                    formula_cell=cell, state=ItemState.INFORMATIONAL, reason=None,
                    scope_kind=None,
                    filed_value=_render(actual), recomputed=_render(recomputed),
                    tau=tau, degree=degree, bound_cells=bound, witness=(cell,),
                    defect_id=defect.id, detail=defect.description,
                ))
            continue

        out.append(DiffFinding(
            formula_cell=cell, state=ItemState.FAIL, reason=None, scope_kind="IN_SCOPE",
            filed_value=_render(actual), recomputed=_render(recomputed),
            tau=tau, degree=degree, bound_cells=bound, witness=(cell,),
            detail=(
                f"the template computes {pm.formula_text.get(cell, '(deferred)')[:60]} , which "
                f"over this filing's inputs yields {_render(recomputed)}; the filing holds "
                f"{_render(actual)}"
            ),
        ))
    return out


def _cell_order(cell: CellKey) -> tuple[str, int, int]:
    from cdfc.schema.stable_keys import col_to_index, split_ref

    sheet, ref = cell.rsplit("!", 1)
    col, row = split_ref(ref)
    return sheet, row, col_to_index(col)


def fired(findings: Sequence[DiffFinding]) -> list[DiffFinding]:
    return [f for f in findings if f.state is ItemState.FAIL]
