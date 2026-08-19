#!/usr/bin/env python
"""P5-B4 — the value-deletion transform generator. **Built here, imported by P9-B2.**

A *value-deletion transform* replaces the value of one or more field-surface cells with an empty
cell and changes nothing else. It is the adversary in D-P5-05's property: **a filer who fills in
less must never get a better settled fraction.**

`05` specifies the same transforms for its precondition-monotonicity property, and P9-B2 imports
this module rather than writing a second one — a property about the fraction cannot wait for the
phase after the fraction ships, and two generators of one transform drift.

**Both extremes are in the generator on purpose.** Delete nothing (the identity, which must not
change the fraction at all) and delete everything (NC-R01's all-zero filing, which is the shape
the whole ruling was written for).
"""

from __future__ import annotations

import random
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.schema.anchor import Anchor
from cdfc.predicates.harvest import _load_context  # noqa: E402


def populated_cells(filing: Path) -> tuple[str, ...]:
    """Every field-surface cell of this filing that CARRIES a value. Deleting an empty cell is
    the identity, so it is not a transform — including it would pad the generator with no-ops."""
    from cdfc.measure.p5_run import fme_surface

    _n, surface, _state = fme_surface()
    ctx = _load_context(filing)
    present = {
        Anchor.cell(sheet, ref).render()
        for sheet, values in ctx.cell_values.items()
        for ref in values
    }
    return tuple(sorted(set(surface) & present))


def deletions(filing: Path, seed: int, *, k_max: int = 200) -> Iterator[tuple[str, ...]]:
    """Deletion sets: the two extremes first, then single cells, then random `k`-subsets.

    Ordered so that a failure reports the SMALLEST interesting case first.
    """
    cells = populated_cells(filing)
    yield ()                                   # delete nothing — the identity
    for c in cells[:64]:                       # single-cell deletions
        yield (c,)
    rnd = random.Random(seed)
    for k in (2, 8, 32, min(k_max, len(cells))):
        if k <= len(cells):
            yield tuple(sorted(rnd.sample(cells, k)))
    yield cells                                # delete everything — NC-R01's all-zero filing


def apply(filing: Path, target: Path, cells: Sequence[str]) -> Path:
    """Write a copy with those cells EMPTIED. Raw-zip surgery, worksheet XML parsed not matched."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_synth", Path(__file__).resolve().parent / "synthesise_filing.py"
    )
    mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
    spec.loader.exec_module(mod)                          # type: ignore[union-attr]
    return mod.write_filing(filing, target, {_split(c): "" for c in cells}, strip_cached=False)


def _split(cell: str) -> tuple[str, str]:
    sheet, ref = cell.rsplit("!", 1)
    return sheet, ref


def main() -> int:
    from cdfc.measure.p5_run import INDEPENDENT

    cells = populated_cells(INDEPENDENT)
    sets = list(deletions(INDEPENDENT, seed=0))
    print(f"{len(cells)} populated field-surface cells; {len(sets)} deletion sets")
    print(f"  smallest {min(len(s) for s in sets)}  largest {max(len(s) for s in sets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
