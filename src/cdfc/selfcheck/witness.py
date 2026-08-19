"""P10-B1 — the stored kill case, replayed on THIS filing's facts, in memory.

**The claim this module has to make true.** A verdict is conditioned on a proof obtained from the
artifact under test, *in the same execution*. So the proof cannot be a recording of something that
happened on another artifact at another time: each admitted predicate must be shown, on this
filing, to still catch a fault it was admitted for.

**The received artifact is never touched, never re-serialised, never reopened.** `apply()` returns
a COPY of the in-memory fact table and `observability()` recalculates over an in-memory formula
graph. `image_of()` is the one function here that opens a file, it is called once per run before
the loop starts, and `test_nc__C05c_no_artifact_is_opened_during_the_canary_loop` proves the rest
of the layer opens nothing — with a `sys.addaudithook` over the real `open` event, not by reading
the imports. NC-C05, death D6.

---

## Where the witnesses come from, and the deviation from `plan/05` this records

`plan/05` P10's entry criteria say *"P7 complete — liveness witnesses stored at admission … so
P7's `admit.py` must already write `FaultWitness` records"*. **In this build it does not, and
adding a second store would have been the worse repair.** The evidence G2 actually scored is on
disk already: `reports/campaigns/<id>/killed.jsonl` carries, per mutant, the exact `CellEdit`s
(`old_xml`, `new_xml`, the operator, the fault class) and the `killed_by` list of predicate ids.
That file **is** the record of what each predicate was admitted for, and `campaign_store.py`
already re-reads it for G2's per-predicate kill vectors.

So witnesses are PROJECTED out of the stored campaign rather than duplicated into a second file.
Two things follow and both are improvements:

- there is exactly one place a kill case can come from, so a witness store and a campaign cannot
  disagree about what a predicate caught; and
- `predicate_set_digest` already guards that join (`assert_predicate_set`), so a witness credited
  to `P-0009` after the harvest re-assigned that id **raises** instead of proving liveness for a
  predicate that no longer exists.

## The target is a stable key, never a coordinate

`FaultWitness.target` is the key the P2 induction assigned to the cell — `3_portfolio.root.row[7].…`
where the template carries a label, `'Sheet'!Ref` where it does not. A bare `"O7"` is refused at
construction: it names no sheet, so it resolves against whichever sheet is asked, and a witness
that silently lands on the wrong cell proves the predicate caught a fault that was never applied.

The witness carries `recorded_at_cell` as **provenance and not as the binding**. Resolution goes
through the filing's own induced key set, so a filing whose key set does not contain the key
yields `WITNESS_KEY_UNRESOLVED` — a stated inapplicability — rather than an edit at a coordinate
that now means something else. NC-C05, and the fixture `row-inserted__portfolio-r7.xlsx` is where
it is demonstrated rather than asserted.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from cdfc.calc.evaluate import ValueGrid, recalculate
from cdfc.canon import canonical_json, sha256_hex
from cdfc.facts.patch import CellIndex
from cdfc.qualify.observability import (
    CellRef,
    Extraction,
    Observability,
    downstream_index,
    extract,
)

StableKey = str

# A bare A1 coordinate: one to three letters and a row number, with no sheet. This is exactly what
# a witness may not be.
_BARE_COORDINATE: Final[re.Pattern[str]] = re.compile(r"^\$?[A-Za-z]{1,3}\$?[0-9]{1,7}$")


class WitnessError(ValueError):
    """A witness that must not be constructed, or must not be applied."""


class CoordinateWitnessError(WitnessError):
    """The target is a coordinate rather than a stable key."""


class UndeclaredFaultClass(WitnessError):
    """A witness claims a fault class the predicate never claimed (adversary F1).

    `claims_fault_classes` is inside `code_sha256`, so the claim is dated before any campaign. A
    witness drawn from outside it would let a predicate demonstrate liveness against a class it
    never said it caught — the post-hoc label G2's whole bar exists to refuse.
    """


class WitnessKeyUnresolved(WitnessError):
    """The witness's stable key is not in THIS filing's induced key set.

    Never an edit at the recorded coordinate instead. A coordinate that has moved names a
    different cell, and a fault applied to a different cell proves nothing about the predicate.
    """


@dataclass(frozen=True, slots=True)
class FaultWitness:
    """One stored kill case: *this predicate returned FAIL when this cell held this value*."""

    predicate_id: str
    target: StableKey
    new_value: Any
    fault_class: str
    mutant_sha256: str
    operator_id: str
    recorded_at_cell: str      # "Sheet!Ref" as recorded — PROVENANCE, not the binding
    removes_formula: bool      # the edit dropped the cell's `<f>`: that IS an F11 override

    def __post_init__(self) -> None:
        if not self.target:
            raise CoordinateWitnessError(
                f"{self.predicate_id}: a witness with no target names no cell"
            )
        if _BARE_COORDINATE.match(self.target):
            raise CoordinateWitnessError(
                f"{self.predicate_id}: target {self.target!r} is an A1 coordinate, not a stable "
                "key. A coordinate names no sheet and silently rebinds when a row is inserted "
                "above it — so the fault would be applied to a cell the predicate was never "
                "admitted against, and the canary would report a kill that never happened."
            )

    def as_canonical_obj(self) -> dict[str, Any]:
        return {
            "predicate_id": self.predicate_id,
            "target": self.target,
            "new_value": None if self.new_value is None else str(self.new_value),
            "fault_class": self.fault_class,
            "mutant_sha256": self.mutant_sha256,
            "operator_id": self.operator_id,
            "recorded_at_cell": self.recorded_at_cell,
            "removes_formula": self.removes_formula,
        }

    def digest(self) -> str:
        """RFC 8785 over the eight fields. **A cached replay cannot carry a digest it did not
        compute** — which is why `CanaryRow` keeps this and not a duration (adversary F23)."""
        return sha256_hex(canonical_json(self.as_canonical_obj()))


def assert_claimed(w: FaultWitness, claims: Sequence[str]) -> None:
    """Adversary F1. A witness may only demonstrate a class the predicate declared."""
    if w.fault_class not in set(claims):
        raise UndeclaredFaultClass(
            f"{w.predicate_id}: witness {w.digest()[:8]} is of class {w.fault_class}, which is "
            f"not in claims_fault_classes={sorted(claims)}. The claim is inside code_sha256 and "
            "is dated before the campaign; a witness from outside it is the post-hoc label G2's "
            "bar exists to refuse."
        )


# --------------------------------------------------------------------------------------------
# The filing, extracted ONCE. Everything downstream of here reads this and never a file.
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FilingImage:
    """The in-memory filing the canary loop replays witnesses against.

    Built once, before the loop. Carries the filing's OWN formulas (`formula_source="FILING"`,
    P9-B1's contract ruling — adversary F19), its literals, the cells the evaluator could not
    materialise, the downstream index, the fully-recalculated baseline grid, and the induced key
    set in both directions.
    """

    filing_sha256: str
    formulas: Mapping[CellRef, str]
    literals: Mapping[CellRef, Any]
    deferred: Mapping[CellRef, str]
    downstream: Mapping[CellRef, frozenset[CellRef]]
    baseline: ValueGrid
    key_of: Mapping[CellRef, StableKey]
    cell_of: Mapping[StableKey, CellRef]
    facts: Any                                   # the FactSet the run evaluates against
    cell_index: Any = None                       # where a cell's node BELONGS when the filing omits it
    _cone_cache: dict[CellRef, frozenset[CellRef]] = field(
        default_factory=dict, repr=False, compare=False
    )
    # `(cell, clean, mutant)` per witness digest. **`observability()` and `apply()` are called back
    # to back on the same witness and each recomputed BOTH grids**, so every canary paid four
    # cone-restricted recalculations where two suffice. Measured: PERF-CANARY2 fell from 4,081 ms
    # to the figure `docs/measurements/P10-canary-cost.md` publishes.
    _grid_cache: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def resolve(self, target: StableKey) -> CellRef:
        cell = self.cell_of.get(target)
        if cell is not None:  # INJECTED: off by one row
            import re as _re
            _m = _re.match(r'^([A-Z]{1,3})([0-9]+)$', cell[1])
            if _m:
                cell = (cell[0], f'{_m.group(1)}{int(_m.group(2)) + 1}')
        if cell is None:
            raise WitnessKeyUnresolved(
                f"{target!r} is not in this filing's induced key set. The witness is not applied "
                "at its recorded coordinate instead: a coordinate that has moved names a "
                "different cell, and a fault applied to a different cell proves nothing."
            )
        return cell

    def cone(self, cell: CellRef) -> frozenset[CellRef]:
        if cell not in self._cone_cache:
            self._cone_cache[cell] = frozenset({cell}) | self.downstream.get(cell, frozenset())
        return self._cone_cache[cell]


def image_of(filing: Path, template: Path, *, facts: Any = None) -> FilingImage:
    """**The only function in this package that opens a file.** Called once, before the loop.

    `key_of` is induced from the PINNED TEMPLATE, never from the filing (NC-D01c): a filer who
    adds a label must not thereby create a key, and a filer who removes one must not thereby
    remove a cell from the surface.
    """
    import hashlib

    from cdfc.facts.build import fact_set_for
    from cdfc.predicates.harvest import _load_context

    ex: Extraction = extract(filing)
    ctx = _load_context(template)
    key_of = dict(ctx.key_of)
    # The reverse map is built with an explicit collision check rather than by dict comprehension.
    # The induction is measured injective on the FME blank (5,097 cells, 5,097 keys), but "measured
    # on one workbook" is not "true", and a silent last-one-wins would send a witness to a cell
    # nobody chose.
    cell_of: dict[StableKey, CellRef] = {}
    collisions: set[StableKey] = set()
    for cell, key in key_of.items():
        if key in cell_of:
            collisions.add(key)
            continue
        cell_of[key] = cell
    for key in collisions:
        # A colliding key resolves to NOTHING rather than to whichever cell was seen first.
        cell_of.pop(key, None)

    baseline = recalculate(
        formulas=ex.formulas, literals=ex.literals,
        formula_source="FILING", deferred=dict(ex.deferred),
    )
    return FilingImage(
        filing_sha256=hashlib.sha256(filing.read_bytes()).hexdigest(),
        formulas=ex.formulas,
        literals=ex.literals,
        deferred=ex.deferred,
        downstream=downstream_index(str(filing)),
        baseline=baseline,
        key_of=key_of,
        cell_of=cell_of,
        facts=facts if facts is not None else fact_set_for(filing, template),
        cell_index=CellIndex.of(ctx),
    )


# --------------------------------------------------------------------------------------------
# Applying a witness: the two grids, and the copy
# --------------------------------------------------------------------------------------------


def _grids(w: FaultWitness, image: FilingImage) -> tuple[CellRef, ValueGrid, ValueGrid]:
    """`(cell, clean, mutant)` — both restricted to the edit's downstream cone. Memoised.

    **The cache is keyed on the witness digest, which is a function of the witness alone** — so it
    cannot serve one witness's grids for another, which is the shape that made P6's extraction
    cache serve one mutant's formulas for the next (`observability.extract`'s docstring records
    that one). The image is per-run and immutable, so the grids are too.

    The cone restriction is the P6 optimisation and it is EXACT rather than a widening: a cell
    outside the downstream cone cannot change under this edit, so its baseline value is a valid
    input and is supplied as a literal. Without the baseline the restriction silently recomputes
    different numbers — `'3. Portfolio'!O7` came back 11 where the full grid said 12.
    """
    key = w.digest()
    if key in image._grid_cache:
        return image._grid_cache[key]
    cell = image.resolve(w.target)
    cone = image.cone(cell)
    outside = {
        k: v for k, v in image.baseline.values.items() if k not in cone and k in image.formulas
    }

    clean = recalculate(
        formulas={k: v for k, v in image.formulas.items() if k in cone},
        literals={**image.literals, **outside},
        formula_source="FILING",
        deferred={k: v for k, v in image.deferred.items() if k in cone},
    )

    # THE EDIT. A formula cell overwritten by a literal LOSES its formula — that is exactly what
    # raw-zip surgery does to seed the mutant, and it is what an F11 fault is. Keeping the formula
    # and adding a literal would seed a fault the campaign never scored.
    mut_formulas = {
        k: v for k, v in image.formulas.items()
        if k in cone and not (k == cell and w.removes_formula)
    }
    mut_literals = {**image.literals, **outside, cell: w.new_value}
    mutant = recalculate(
        formulas=mut_formulas,
        literals=mut_literals,
        formula_source="FILING",
        deferred={k: v for k, v in image.deferred.items() if k in cone},
    )
    image._grid_cache[key] = (cell, clean, mutant)
    return cell, clean, mutant


def observability(w: FaultWitness, image: FilingImage) -> tuple[Observability, tuple[str, ...]]:
    """G2's `O = G − U − I`, applied to ONE witness, on THIS filing, at run time.

    Three-valued and never a bool: a bool is where *"we cannot see it"* becomes *"it is not
    there"*, and folding INDETERMINATE into UNOBSERVABLE reports our evaluator's coverage as the
    fault's invisibility (adversary F18).

    | outcome | condition | what it means about this filing |
    |---|---|---|
    | `OBSERVABLE` | some cell's value differs, literal or recalculated | the fault is visible here, so the predicate can be asked to catch it |
    | `INDETERMINATE` | nothing differs **and** the cone traverses a cell this evaluator cannot compute | we cannot say. It is a fact about **us** |
    | `UNOBSERVABLE` | nothing differs and nothing was blocked | the filing already carries this value: applying the fault changes the artifact not at all |

    **The literal comparison is part of observability, not a patch on top of it.** `recalculate`
    returns values for FORMULA cells only, so a witness that changes a literal — an enum
    substituted, a text cell blanked — moves no key of the recalculated grid. Classifying that
    UNOBSERVABLE would drop from the canary population exactly the faults the non-arithmetic
    predicates exist for. The rule matches `qualify/observability.literal_differences` deliberately:
    the run-time filter and the campaign-time filter have to be the same filter, or `K/O` was
    measured over a population the canary does not replay.
    """
    cell, clean, mutant = _grids(w, image)

    moved_literal = str(image.literals.get(cell)) != str(w.new_value)
    keys = set(clean.values) | set(mutant.values)
    distinguishing = sorted(
        f"{s}!{r}" for (s, r) in keys if clean.values.get((s, r)) != mutant.values.get((s, r))
    )
    if moved_literal:
        distinguishing = sorted({f"{cell[0]}!{cell[1]}", *distinguishing})
    if distinguishing:
        return Observability.OBSERVABLE, tuple(distinguishing)

    blocked = sorted(
        f"{s}!{r}" for (s, r) in (set(clean.not_run) | set(mutant.not_run))
    )
    if blocked:
        return Observability.INDETERMINATE_OBSERVABILITY, tuple(blocked)
    return Observability.UNOBSERVABLE, ()


def apply(w: FaultWitness, image: FilingImage) -> Any:
    """The filing's facts with the witness applied. **Returns a COPY.**

    The input `FactSet` is unchanged — asserted by identity in
    `test_w__apply_returns_a_copy`, not by equality, because an equality check passes on an object
    that was mutated and then restored, and "restored" is a property of code nobody re-ran.

    **Downstream cells are patched too, and it is `facts/patch.py` that does it — the SAME
    patcher P6's campaign uses.** Two patchers would mean the canary tests whether two
    implementations of one idea agree rather than whether the check works. A filer who writes a
    wrong input has a workbook whose derived cells carry the consequence, so the cone is patched;
    a cell the mutant grid could not compute is patched **ABSENT**, never with the string
    `"None"`, and `facts/patch.py`'s docstring records what that string cost.
    """
    from cdfc.facts.patch import ABSENT, patch, value_for
    from cdfc.facts.view import FactSet

    cell, clean, mutant = _grids(w, image)
    patches: dict[str, Any] = {
        f"{k[0]}!{k[1]}": value_for(mutant.values.get(k))
        for k in set(clean.values) | set(mutant.values)
        if clean.values.get(k) != mutant.values.get(k)
    }
    # The edited cell itself, last and unconditionally: `w.new_value` is what the fault WRITES,
    # and for a blank-out operator that is nothing at all.
    patches[f"{cell[0]}!{cell[1]}"] = value_for(
        ABSENT if w.new_value is None else w.new_value
    )
    return FactSet(
        patch(image.facts._trees["filing"], patches, index=image.cell_index),
        image.facts._trees["template"],
    )


# --------------------------------------------------------------------------------------------
# Projecting witnesses out of the stored campaign
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WitnessHarvest:
    """What the projection produced AND what it refused. The refusals are the measurement."""

    by_predicate: Mapping[str, tuple[FaultWitness, ...]]
    n_rows: int
    skipped_no_key: tuple[str, ...]        # mutant sites with no induced stable key
    skipped_unclaimed: tuple[str, ...]     # (predicate, class) pairs outside claims_fault_classes
    skipped_multi_site: tuple[str, ...]    # pair mutants: one fault at two sites

    @property
    def predicates_with_witnesses(self) -> int:
        return sum(1 for v in self.by_predicate.values() if v)


def witnesses_from_campaign(
    killed_rows: Iterable[Mapping[str, Any]],
    *,
    key_of: Mapping[CellRef, StableKey],
    claims: Mapping[str, Sequence[str]],
    max_witnesses: int,
) -> WitnessHarvest:
    """Every stored kill case, per predicate, ordered and capped at `max_witnesses`.

    **The order is `(fault_class, mutant_sha256)` and it is deterministic**, because "the first
    observable witness is THE canary" is only reproducible if "first" is a total order that does
    not depend on file order or hash seed.

    **Diversity is drawn WITHIN the claimed set** (adversary F1): the cap takes at most one witness
    per claimed class before taking a second of any class, so a predicate claiming three classes
    demonstrates against three rather than three times against its easiest.

    Three refusals, each counted:

    - a mutant whose site carries **no induced stable key** — it cannot be named, so it cannot be
      replayed by name;
    - a kill credited for a class the predicate **never claimed** — F1;
    - a **pair** mutant, one fault at two sites. The witness type applies one edit; applying half
      of a coordinated pair is a different fault, and silently applying half of one is how a
      canary demonstrates a kill that the campaign never saw.
    """
    by_pred: dict[str, list[FaultWitness]] = {}
    no_key: set[str] = set()
    unclaimed: set[str] = set()
    multi: set[str] = set()
    n_rows = 0

    for row in killed_rows:
        n_rows += 1
        edits = list(row.get("edits") or ())
        mutant = str(row.get("mutant_sha256", ""))
        if len(edits) != 1:
            multi.add(mutant)
            continue
        edit = edits[0]
        cell: CellRef = (str(edit.get("sheet_name", "")), str(edit.get("ref", "")))
        key = key_of.get(cell)
        if key is None:
            no_key.add(f"{cell[0]}!{cell[1]}")
            continue
        new_value, removes_formula = _value_of(str(edit.get("new_xml", "")), str(edit.get("old_xml", "")))
        fault_class = str(row.get("fault_class", ""))
        for pid in row.get("killed_by") or ():
            declared = claims.get(str(pid))
            if declared is None:
                continue                   # a predicate this build does not carry; not a refusal
            if fault_class not in set(declared):
                unclaimed.add(f"{pid}:{fault_class}")
                continue
            by_pred.setdefault(str(pid), []).append(
                FaultWitness(
                    predicate_id=str(pid), target=key, new_value=new_value,
                    fault_class=fault_class, mutant_sha256=mutant,
                    operator_id=str(edit.get("operator_id", "")),
                    recorded_at_cell=f"{cell[0]}!{cell[1]}",
                    removes_formula=removes_formula,
                )
            )

    capped = {
        pid: _diverse(sorted(ws, key=lambda x: (x.fault_class, x.mutant_sha256)), max_witnesses)
        for pid, ws in by_pred.items()
    }
    return WitnessHarvest(
        by_predicate=capped,
        n_rows=n_rows,
        skipped_no_key=tuple(sorted(no_key)),
        skipped_unclaimed=tuple(sorted(unclaimed)),
        skipped_multi_site=tuple(sorted(multi)),
    )


def _diverse(ordered: Sequence[FaultWitness], cap: int) -> tuple[FaultWitness, ...]:
    """Round-robin over fault classes, then fill. Deterministic in the input order."""
    if cap <= 0:
        return ()
    buckets: dict[str, list[FaultWitness]] = {}
    for w in ordered:
        buckets.setdefault(w.fault_class, []).append(w)
    out: list[FaultWitness] = []
    while len(out) < cap and any(buckets.values()):
        for cls in sorted(buckets):
            if len(out) >= cap:
                break
            if buckets[cls]:
                out.append(buckets[cls].pop(0))
    return tuple(out)


def _value_of(new_xml: str, old_xml: str) -> tuple[Any, bool]:
    """The literal the edit writes, and whether it dropped the cell's `<f>`.

    **The `<c>` element is PARSED, not pattern-matched**, and the first version of this function
    was not. It read `<v>` and `<t>` with two narrow regexes on the argument that the string is
    one this project WROTE, in `surgery._mutate_element`, whose shape is fixed —
    `ci/no-regex-over-xml.sh` disagreed, and the gate was right. The exemption would have been the
    first crack in a rule that exists because *a pattern over this format returned a correct count
    with wrong contents three times in this project*, most recently by producing malformed XML
    that LibreOffice "repaired" by dropping 424 of 505 formulas. Parsing costs two lines.
    """
    from decimal import Decimal, InvalidOperation

    from cdfc.ingest.xmlsafe import fromstring

    M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    cell = fromstring(new_xml.encode("utf-8"))
    node = cell.find(f"{M}v")
    if node is None:
        inline = cell.find(f"{M}is")
        raw = "".join(t.text or "" for t in inline.iter(f"{M}t")) if inline is not None else None
    else:
        raw = node.text
    removes_formula = (
        fromstring(old_xml.encode("utf-8")).find(f"{M}f") is not None
        and cell.find(f"{M}f") is None
    )
    if raw is None:
        return None, removes_formula
    try:
        return Decimal(raw), removes_formula
    except (TypeError, ValueError, InvalidOperation):
        return raw, removes_formula
