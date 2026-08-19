"""P9-B1 — the template formula → field-surface precedent map, and `TEMPLATE_DIFF`'s ceiling.

**What this module decides, and it is decided here rather than at run time.** `TEMPLATE_DIFF`
fires on a cell the pinned blank declares to be a **formula**. The field surface is
*unlocked ∧ non-formula*, so the cell the finding is *about* has no `run_cell` row. Two naive
outcomes, both wrong: drop the item, and the flagship settles nothing ever; or widen the
denominator when the relation is admitted, and the numerator has chosen its own denominator —
NC-D02 arriving through a new door.

**The ruling: a `TEMPLATE_DIFF` evaluation binds the FIELD-SURFACE PRECEDENTS of the formula
cell**, and its witness names the overwritten cell. Overwriting `'3. Portfolio'!O7` with a literal
is a statement about the inputs `C7:N7` — it asserts that their sum is something other than their
sum. Attributing the finding to the inputs is not a workaround; it is what the finding *means*.
It also keeps the denominator a pure function of `styles.xml`.

---

**THREE READINGS OF "PRECEDENT", AND THIS MODULE PUBLISHES ALL THREE.** The plan's measurement
script intersected the references it found by pattern with the field surface and reported 957.
Two of its choices are not obviously right, and neither was argued:

| reading | what it counts | on FME |
|---|---|---|
| `lexical` | every reference appearing in the formula text | the plan's 957 |
| `value` | `lexical` minus arguments read for their SHAPE only — `ROW(D54)` reads a row number, never D54's value | measured |
| `transitive` | `value`, followed through intermediate FORMULA cells to the field-surface inputs that actually determine the answer | measured — **the one that binds** |

`transitive` is the answer, and the argument is the recomputation itself. `recalculate(...,
formula_source="TEMPLATE")` recomputes the *whole* formula graph over the filed inputs, so a
finding at `'2. Summary'!X = '1. Introduction'!D17` depends on `D17`'s own inputs — `G54:G63` —
and not on `D17`, which is not a cell the filer may write. Binding only the direct references
would attribute the finding to a cell that carries no filer decision and would under-report
`cells_bound`; binding the lexical set would attribute it to cells whose *value* the formula never
reads, which is worse, because overwriting one of them cannot move the finding at all.

**A precedent set that passes through a formula we could not materialise is INCOMPLETE and says
so.** It is not silently truncated: a truncated precedent set is a `cells_bound` that is too small
for a reason nobody can see, and `cells_bound == 0` is a G1 refusal. `pm.incomplete` names those
cells and `assert_complete()` raises on demand.

**DEVIATION FROM THE PLAN'S SIGNATURE, recorded.** `plan/05` writes
`build_precedent_map(schema: TemplateSchema)`. `TemplateSchema` in this build carries only
`key → cells`; it has no formulas, so it cannot answer the question. The map is built from the
pinned blank itself, which is the artifact the plan's own measurement script reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from cdfc.schema.anchor import Anchor
from cdfc.calc.evaluate import ParseError, expand, parse_formula, refs_of
from cdfc.calc.shift import materialise
from cdfc.ingest.reader_lxml import read
from cdfc.schema.styles_mask import Rule, build as build_field_surface

# `"Sheet!Ref"` — the representation `run_cell.stable_key`, `TemplateSchema.cells_for` and
# `settled_fraction.static_settled_cells` all already use. The plan types these `StableKey`;
# using the dotted header key here would make `bound_cells` incomparable with the cell table.
CellKey = str

Reading = Literal["lexical", "value", "transitive"]
READINGS: Final[tuple[Reading, ...]] = ("lexical", "value", "transitive")

# The iteration bound, and it is NOT the cycle detector it was written as. Each round composes
# the reachability relation with itself, so reach DOUBLES per round: a graph of depth d converges
# in about log2(d) rounds, and a cycle saturates and converges rather than running out of rounds.
# Sixty-four rounds is therefore not reachable by any graph that fits in memory. The bound stays
# as a liveness stop against a future non-monotonic edit to `_close`, which is a smaller claim
# than the one this comment used to make. See `_close`.
MAX_ROUNDS: Final[int] = 64


class PrecedentError(RuntimeError):
    """The precedent map cannot be built, or is being used past what it can support."""


class IncompletePrecedents(PrecedentError):
    """A precedent set passes through a formula that could not be materialised."""


@dataclass(frozen=True, slots=True)
class PrecedentMap:
    template_sha256: str
    reading: Reading
    by_formula_cell: Mapping[CellKey, frozenset[CellKey]]      # ALL precedents, any kind of cell
    in_field_surface: Mapping[CellKey, frozenset[CellKey]]     # ∩ field surface — what binds
    unreachable: frozenset[CellKey]      # formula cells whose precedents miss the field surface
    field_surface: frozenset[CellKey]
    formula_text: Mapping[CellKey, str]  # materialised, shared dependents already row-shifted
    deferred: Mapping[CellKey, str]      # a formula we could not materialise, with its reason
    incomplete: frozenset[CellKey]       # formula cells whose closure passes through `deferred`

    def assert_complete(self, cell: CellKey) -> None:
        if cell in self.incomplete:
            raise IncompletePrecedents(
                f"{cell}'s precedent set passes through a formula this build could not "
                f"materialise, so its bound set is a LOWER BOUND. A relation that binds a "
                f"lower bound reports a `cells_bound` nobody can check."
            )

    @property
    def reachable(self) -> frozenset[CellKey]:
        """The union — `TEMPLATE_DIFF`'s ceiling as a SET, so a caller can ask which cells."""
        out: set[CellKey] = set()
        for cells in self.in_field_surface.values():
            out |= cells
        return frozenset(out)

    def as_pairs(self, mapping: Mapping[CellKey, str]) -> dict[tuple[str, str], str]:
        """`{"Sheet!Ref": text}` → `{(sheet, ref): text}`, which is what `recalculate` takes.

        **The one-line conversion that has to exist somewhere.** Passing the string-keyed map
        straight into `recalculate` does not raise: it reads `key[0]` as the sheet name and gets
        the first CHARACTER, every reference resolves against a sheet that does not exist, every
        cell comes back absent, and the relation FAILS on all 456 evaluable cells of a clean
        filing. Confident, uniform and completely wrong.
        """
        return {tuple(k.split("!", 1)): v for k, v in mapping.items()}  # type: ignore[misc]

    def per_sheet(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for key in self.reachable:
            counts[key.split("!", 1)[0]] = counts.get(key.split("!", 1)[0], 0) + 1
        return dict(sorted(counts.items()))


def ceiling(pm: PrecedentMap) -> tuple[int, int]:
    """`(|⋃ in_field_surface|, |field_surface|)`.

    Published BEFORE the delta, always. A ceiling stated afterwards reads as an excuse; stated
    first it makes a small delta a measurement rather than a disappointment.
    """
    return len(pm.reachable), len(pm.field_surface)


# --------------------------------------------------------------------------------
# construction
# --------------------------------------------------------------------------------


def materialised_formulas(blob: Path) -> tuple[dict[CellKey, str], dict[CellKey, str]]:
    """`(formula text by cell, deferred by cell)` with every shared dependent ROW-SHIFTED.

    NC-P02 is the hazard this function exists inside: a dependent resolved from its master's
    UNSHIFTED text yields a well-formed formula for the wrong row, so the precedent map would be
    confidently wrong about 211 of FME's 505 cells and nothing would look broken.
    """
    wb = read(blob)
    masters = {(f.sheet, f.si): f for f in wb.formulas if f.encoding == "SHARED_MASTER"}
    out: dict[CellKey, str] = {}
    deferred: dict[CellKey, str] = {}
    for f in wb.formulas:
        key = f"{f.sheet}!{f.ref}"
        if f.text:
            out[key] = f.text
        elif f.encoding == "SHARED_DEPENDENT":
            m = masters.get((f.sheet, f.si))
            if m is None or not m.text:
                deferred[key] = f"shared dependent si={f.si}: master not visible"
            else:
                out[key] = materialise(m.ref, m.text, f.ref)
        else:
            deferred[key] = f"formula cell carrying no text, encoding={f.encoding}"
    return out, deferred


def _direct(text: str, sheet: str, *, values_only: bool) -> frozenset[CellKey]:
    ast = parse_formula(text)
    out: set[CellKey] = set()
    for ref in refs_of(ast, values_only=values_only):
        for s, r in expand(ref, sheet):
            out.add(f"{s}!{r}")
    return frozenset(out)


def build_precedent_map(
    blob: Path, *, reading: Reading = "transitive", rule: Rule = Rule.V3
) -> PrecedentMap:
    """The map, at one of the three readings. `transitive` is the one `TEMPLATE_DIFF` binds."""
    if reading not in READINGS:
        raise PrecedentError(f"unknown reading {reading!r}; the three are {READINGS}")

    import hashlib

    template_sha256 = hashlib.sha256(blob.read_bytes()).hexdigest()
    fs = build_field_surface(blob, rule)
    field_surface = frozenset(Anchor.cell(s, r).render() for s, r in fs.cells)

    text, deferred = materialised_formulas(blob)
    values_only = reading != "lexical"

    direct: dict[CellKey, frozenset[CellKey]] = {}
    for key, src in text.items():
        sheet = key.split("!", 1)[0]
        try:
            direct[key] = _direct(src, sheet, values_only=values_only)
        except (ParseError, RecursionError) as e:
            # DECLARED, never dropped. A formula we cannot parse contributes no precedents, and
            # every reader of it is `incomplete` — which is a different claim from "it has none".
            deferred[key] = f"parse: {type(e).__name__}: {e}"
    for key in deferred:
        direct.pop(key, None)

    if reading == "transitive":
        by_cell, incomplete = _close(direct, formula_cells=frozenset(text) | frozenset(deferred),
                                     deferred=frozenset(deferred))
    else:
        by_cell = direct
        incomplete = frozenset(
            k for k, refs in direct.items() if refs & frozenset(deferred)
        )

    in_fs = {k: refs & field_surface for k, refs in by_cell.items()}
    unreachable = frozenset(k for k, refs in in_fs.items() if not refs)

    return PrecedentMap(
        template_sha256=template_sha256,
        reading=reading,
        by_formula_cell=by_cell,
        in_field_surface=in_fs,
        unreachable=unreachable,
        field_surface=field_surface,
        formula_text=text,
        deferred=deferred,
        incomplete=incomplete,
    )


def _close(
    direct: Mapping[CellKey, frozenset[CellKey]],
    *,
    formula_cells: frozenset[CellKey],
    deferred: frozenset[CellKey],
) -> tuple[dict[CellKey, frozenset[CellKey]], frozenset[CellKey]]:
    """Follow references THROUGH formula cells to the inputs that determine the answer.

    A reference to a formula cell is replaced by that cell's own precedents. A reference to a
    non-formula cell is a leaf and stays. The formula cell itself is retained in the set as well
    — `by_formula_cell` is *all* precedents, and the intersection with the field surface drops it
    a moment later, because a formula cell is never in the field surface.

    Iterated to a fixpoint rather than recursed, so a cyclic template produces a bounded loop
    instead of a stack overflow.

    **A CYCLE DOES NOT RAISE HERE, and this docstring used to say it did.** MEASURED: `_close`
    over the genuine two-cycle `{'S!A1': {'S!B1'}, 'S!B1': {'S!A1'}}` converges in two rounds and
    returns the saturated closure — `S!A1 → {S!A1, S!B1}` and `S!B1 → {S!A1, S!B1}` — with no
    exception and an empty `incomplete`. The `MAX_ROUNDS` refusal at the bottom of this function
    cannot be the cycle detector it reads as, for the reason given at `MAX_ROUNDS`: reach doubles
    each round, so a cycle SATURATES long before the rounds run out.

    **The guarantee was borrowed from a different module.** `calc/evaluate.py` does genuinely
    detect cycles: its topological visit (the `visit()` walk, around lines 480-516) carries a stack
    and marks every cell it re-enters `NOT_RUN("cycle: circular reference")`, so a circular
    reference there yields a named refusal and never a value. The two modules differ, and only
    that one holds the claim.

    Why the saturated closure is acceptable in THIS module. A precedent set answers a reachability
    question, and reachability through a cycle is well defined — every member of a cycle reaches
    every other, which is exactly what the saturated set says. It is a VALUE that cannot be
    computed through a cycle, and this module computes no values; `evaluate.py`, which does, is
    the module that has to refuse. So the closure returned for a cyclic template is a correct
    answer to the question asked, not a partial one, and `cells_bound` derived from it is still
    re-derivable by anyone who runs the same fixpoint.
    """
    closed = {k: set(v) for k, v in direct.items()}
    incomplete = {k for k, v in direct.items() if v & deferred}
    for _round in range(MAX_ROUNDS):
        changed = False
        for key, refs in closed.items():
            addition: set[CellKey] = set()
            for r in refs:
                if r in formula_cells and r != key:
                    addition |= closed.get(r, frozenset())
                    if r in deferred or r in incomplete:
                        if key not in incomplete:
                            incomplete.add(key)
                            changed = True
            if not addition <= refs:
                refs |= addition
                changed = True
        if not changed:
            return {k: frozenset(v) for k, v in closed.items()}, frozenset(incomplete)
    raise PrecedentError(
        f"the precedent closure did not converge in {MAX_ROUNDS} rounds. This is NOT the signature "
        "of a cycle — a cycle saturates and converges, because reach doubles each round — so "
        "reaching this line means the iteration stopped being monotonic, and a partial closure "
        "would be a `cells_bound` nobody can re-derive."
    )
