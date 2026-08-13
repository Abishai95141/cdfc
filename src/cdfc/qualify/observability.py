"""P6-B3 — the observability filter, THREE-WAY, and it recalculates with the FILING's formulas.

**The single most important implementation note in P6.** The grid compared is the **recalculated**
grid, not the mutant file's cached values. A raw-zip edit does not update Excel's cached values, so
a filter reading cached values reports a difference at exactly the edited cell and nowhere else —
it would measure *the edit*, not *its propagation*, and return `U = 0` on every campaign. `U/G`
would then be a plausible, confident, wrong number, and every `K/O` computed through it would be
wrong in the direction that flatters us. NC-Q31.

**F18 — why there are three values and not two.** `ValueGrid` carries a `not_run` map for cells the
evaluator could not compute. **A cell in `not_run` is identical in both grids by construction**, so
under a two-way classification every mutant whose only propagation path runs through such a cell is
marked `UNOBSERVABLE`, leaves `O`, and — because `O = G − U` — **raises** `K/O`. The measurement
error is correlated with the quantity being measured, in the direction that flatters us. `U/G` would
be published as *the fraction of our mutants whose effect is invisible* (a property of the FAULT
MODEL) while measuring *the fraction our evaluator cannot see* (a property of OUR APPARATUS).

**F19 — `formula_source=FILING`, and it is required.** An F11 mutant is a cell the pinned blank
declares a formula for, carrying a literal. Recalculating it through the TEMPLATE's formula graph
**overwrites the literal with the formula's value**, so the two grids are identical and the
flagship class classifies `UNOBSERVABLE` with `O = 0` — at which point `TEMPLATE_DIFF` can never
clear G2, and nothing goes red for twelve weeks. Observability recalculates with the filing's own
`<f>` elements, materialised, so a cell carrying a literal stays a literal and its wrongness
propagates. NC-Q61.
"""

from __future__ import annotations

import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

from cdfc.calc.evaluate import ValueGrid, recalculate, refs_of, expand as _expand_ref, parse_formula
from cdfc.calc.shift import materialise as shift_materialise
from cdfc.ingest.reader_lxml import _sheet_parts
from cdfc.ingest.xmlsafe import fromstring

M: Final[str] = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS: Final[str] = f"{{{M}}}"

CellRef = tuple[str, str]


class Observability(StrEnum):
    OBSERVABLE = "OBSERVABLE"
    UNOBSERVABLE = "UNOBSERVABLE"
    INDETERMINATE_OBSERVABILITY = "INDETERMINATE_OBSERVABILITY"


@dataclass(frozen=True, slots=True)
class Extraction:
    """A workbook's own formulas and literals — the FILING's, not the template's."""

    formulas: Mapping[CellRef, str]
    literals: Mapping[CellRef, Any]
    deferred: Mapping[CellRef, str]


@lru_cache(maxsize=8)
def _extract_cached(blob_str: str, _stamp: tuple[int, int]) -> Extraction:
    return _extract_uncached(Path(blob_str))


def extract(blob: Path) -> Extraction:
    """Memoised on `(path, size, mtime_ns)`.

    The clean workbook was re-parsed once per mutant, which dominated the campaign's wall clock.
    The key includes size and mtime so a REWRITTEN file at the same path is a different entry —
    every mutant is written to the same name in turn, and a path-only cache would have served one
    mutant's formulas for another's. That would have been a silent, uniform wrong answer.
    """
    st = blob.stat()
    return _extract_cached(str(blob), (st.st_size, st.st_mtime_ns))


def _extract_uncached(blob: Path) -> Extraction:
    """Read the workbook's `<f>` elements and its literal cells.

    A shared dependent whose master is visible is MATERIALISED; one whose master is not is
    DECLARED as deferred rather than dropped. A dropped cell is invisible to the cascade rule, so
    anything reading it computes with a zero and returns a clean wrong number — which is the
    defect the cascade rule exists to stop, committed one level up by the caller.
    """
    formulas: dict[CellRef, str] = {}
    literals: dict[CellRef, Any] = {}
    deferred: dict[CellRef, str] = {}

    with zipfile.ZipFile(blob) as z:
        shared_strings = _shared_strings(z)
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            masters: dict[str, tuple[str, str]] = {}
            pending: list[tuple[str, str]] = []
            for c in root.iter(f"{NS}c"):
                ref = c.get("r") or ""
                f = c.find(f"{NS}f")
                if f is not None:
                    si = f.get("si") or ""
                    if f.get("t") == "shared" and (f.text or "").strip():
                        masters[si] = (ref, f.text or "")
                    if (f.text or "").strip():
                        formulas[(name, ref)] = f.text or ""
                    elif f.get("t") == "shared":
                        pending.append((ref, si))
                    else:
                        deferred[(name, ref)] = "formula element carries no text"
                    continue
                value = _cell_value(c, shared_strings)
                if value is not None:
                    literals[(name, ref)] = value
            for ref, si in pending:
                master = masters.get(si)
                if master is None:
                    deferred[(name, ref)] = f"shared dependent si={si}, master not visible"
                else:
                    formulas[(name, ref)] = shift_materialise(master[0], master[1], ref)
    return Extraction(formulas, literals, deferred)


def _shared_strings(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    ss = fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(f"{NS}t")) for si in ss.iter(f"{NS}si")]


def _cell_value(c: Any, shared: Sequence[str]) -> Any:
    v = c.find(f"{NS}v")
    raw = v.text if v is not None else None
    if raw is None:
        inline = c.find(f"{NS}is")
        raw = "".join(x.text or "" for x in inline.iter(f"{NS}t")) if inline is not None else None
    if raw is None:
        return None
    if c.get("t") == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return ""
    from decimal import Decimal, InvalidOperation

    try:
        d = Decimal(raw)
    except (InvalidOperation, ValueError):
        return raw
    return int(d) if d == d.to_integral_value() else d


def grid_of(
    blob: Path,
    *,
    cone: frozenset[CellRef] | None = None,
    baseline: ValueGrid | None = None,
) -> ValueGrid:
    """The RECALCULATED grid. `formula_source="FILING"` — required, and F19 is why.

    `cone` restricts the recalculation to the edit's transitive DOWNSTREAM set. **`baseline` is
    then required**, and the reason is a defect the differential test caught on its first run:
    restricting the formula set also removes formula cells that a cone member READS, and those
    cells then fell back to their cached literals — `'3. Portfolio'!O7` computed 11 where the full
    grid computed 12. A silent one-off in the cone optimisation would have moved every kill rate.

    The repair is exact rather than a widening: a cell outside the downstream cone **cannot change
    under this edit**, so its value in the clean grid is a valid input, and it is supplied as a
    literal. The optimisation stays exact and the differential test proves it on every mutant.
    """
    ex = extract(blob)
    if cone is None:
        return recalculate(
            formulas=ex.formulas, literals=ex.literals,
            formula_source="FILING", deferred=dict(ex.deferred),
        )
    if baseline is None:
        raise ValueError(
            "a cone-restricted recalculation needs the baseline grid: the cells it excludes are "
            "inputs to the cells it keeps, and without their computed values the restriction "
            "silently computes different numbers"
        )
    outside = {
        k: v for k, v in baseline.values.items() if k not in cone and k in ex.formulas
    }
    return recalculate(
        formulas={k: v for k, v in ex.formulas.items() if k in cone},
        literals={**ex.literals, **outside},
        formula_source="FILING",
        deferred={k: v for k, v in ex.deferred.items() if k in cone},
    )


@lru_cache(maxsize=4)
def downstream_index(blob_str: str) -> Mapping[CellRef, frozenset[CellRef]]:
    """`cell -> every formula cell transitively reading it`. Built once per base workbook."""
    ex = extract(Path(blob_str))
    direct: dict[CellRef, set[CellRef]] = {}
    for key, src in ex.formulas.items():
        try:
            ast = parse_formula(src)
        except Exception:  # noqa: BLE001 - an unparseable formula has no edges, and it is deferred
            continue
        for r in refs_of(ast, values_only=True):
            for dep in _expand_ref(r, key[0]):
                direct.setdefault(dep, set()).add(key)

    memo: dict[CellRef, frozenset[CellRef]] = {}

    def closure(cell: CellRef, seen: frozenset[CellRef]) -> frozenset[CellRef]:
        if cell in memo:
            return memo[cell]
        out: set[CellRef] = set()
        for nxt in direct.get(cell, ()):
            if nxt in seen:
                continue                      # a cycle is NOT_RUN downstream; it is not an edge here
            out.add(nxt)
            out |= closure(nxt, seen | {nxt})
        result = frozenset(out)
        if not seen:
            memo[cell] = result
        return result

    return {cell: closure(cell, frozenset({cell})) for cell in direct}


def cone_for(blob: Path, edited: Sequence[CellRef]) -> frozenset[CellRef]:
    """The transitive downstream cone of the edited cells, plus the cells themselves."""
    index = downstream_index(str(blob))
    out: set[CellRef] = set(edited)
    for cell in edited:
        out |= index.get(cell, frozenset())
    return frozenset(out)


def classify(
    clean: ValueGrid, mutant: ValueGrid
) -> tuple[Observability, frozenset[CellRef]]:
    """Three-way. `UNOBSERVABLE` requires that NO not_run cell was traversed.

    A grid pair that is equal *and* traversed a cell we could not compute is
    `INDETERMINATE_OBSERVABILITY`: we do not know whether the fault is invisible or whether we
    are. Folding it into `UNOBSERVABLE` is NC-Q60, and it raises `K/O`.
    """
    keys = set(clean.values) | set(mutant.values)
    distinguishing = frozenset(
        k for k in keys if clean.values.get(k) != mutant.values.get(k)
    )
    if distinguishing:
        return Observability.OBSERVABLE, distinguishing
    blocked = frozenset(set(clean.not_run) | set(mutant.not_run))
    if blocked:
        return Observability.INDETERMINATE_OBSERVABILITY, blocked
    return Observability.UNOBSERVABLE, frozenset()


def literal_differences(clean: Path, mutant: Path) -> frozenset[CellRef]:
    """Cells whose LITERAL value differs. Part of observability, not a patch on top of it.

    `recalculate` returns values for FORMULA cells only, so a mutant that changes a literal — an
    enum substituted, a homoglyph, a blanked text cell — moves no key of the recalculated grid.
    Classifying that UNOBSERVABLE would remove it from `O` even though a membership predicate
    kills it, and `K/O` would be computed over a denominator missing exactly the mutants our
    non-arithmetic predicates exist for.
    """
    a, b = extract(clean).literals, extract(mutant).literals
    keys = set(a) | set(b)
    return frozenset(k for k in keys if str(a.get(k)) != str(b.get(k)))


def classify_files(
    clean: Path, mutant: Path, *, edited: Sequence[CellRef] | None = None
) -> tuple[Observability, frozenset[CellRef]]:
    """Recalculate both and classify. Restricted to the edit's cone when `edited` is given."""
    if not edited:
        return classify(grid_of(clean), grid_of(mutant))
    full = grid_of(clean)
    cone = cone_for(clean, edited)
    return classify(
        grid_of(clean, cone=cone, baseline=full), grid_of(mutant, cone=cone, baseline=full)
    )
