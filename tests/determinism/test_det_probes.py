"""P9-B3 — the probe seed is an INPUT, and `verify` replays it.

**The positive control is the interesting half.** A seed that changes nothing is not doing
anything, and `test_det__probe_results_are_seed_stable` would then be vacuously green — the exact
shape of a test that has never been observed to fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.driver import Budget, manifest_entry, run_probes, shrink  # noqa: E402
from cdfc.probes.precedents import build_precedent_map  # noqa: E402
from cdfc.probes.relations.registry import load  # noqa: E402

FME = (
    REPO / "fixtures" / "prescribed"
    / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)


def _search(seed: int):
    """A deterministic search whose EXPLORATION ORDER depends on the seed. `shrink` walks the
    candidate list, so a seed-dependent ordering changes which minimal witness it lands on when
    more than one is minimal — which is what a seed is for."""
    import random

    cells = [f"S!A{i}" for i in range(1, 21)]
    rnd = random.Random(seed)
    rnd.shuffle(cells)
    return shrink(cells, lambda t: "S!A3" in t or "S!A17" in t, Budget(500))


def test_det__probe_results_are_seed_stable() -> None:
    """Two runs at one seed produce the same result. Without this, `verify` cannot re-derive a
    probe result at all."""
    assert _search(7) == _search(7)
    a = run_probes(load(), state=None, evaluate=lambda _r, _s: (True, ("S!A1",), ""), seed=7)
    b = run_probes(load(), state=None, evaluate=lambda _r, _s: (True, ("S!A1",), ""), seed=7)
    assert a == b


def test_det__probe_results_differ_under_a_different_seed() -> None:
    """THE POSITIVE CONTROL. A seed that cannot change the search is not a seed."""
    seen = {_search(s) for s in range(12)}
    assert len(seen) > 1, (
        "every seed produced the same witness, so the seed is not reaching the search and the "
        "stability test above is vacuously green"
    )


def test_det__the_seed_is_recorded_in_the_manifest() -> None:
    out = run_probes(load(), state=None, evaluate=lambda _r, _s: (True, ("S!A1",), ""), seed=99)
    entry = manifest_entry(out)
    assert entry["probe_seed"] == 99
    assert [r["id"] for r in entry["relations"]] == [s.id for s in load()]


def test_det__the_precedent_map_is_byte_stable_across_builds() -> None:
    a, b = build_precedent_map(FME), build_precedent_map(FME)
    assert a.in_field_surface == b.in_field_surface
    assert a.formula_text == b.formula_text
    assert a.template_sha256 == b.template_sha256


def test_det__template_diff_findings_are_ordered() -> None:
    """Findings sort by `(sheet, row, column)`, never by dict or set iteration."""
    from cdfc.probes.degree import degree_map
    from cdfc.probes.template_diff import _cell_order, load_defects, template_diff
    from cdfc.probes.workbook import filed_values

    pm = build_precedent_map(FME)
    out = template_diff(
        filed_values(REPO / "fixtures/synthetic/formula-overwritten__portfolio-O7.xlsx"),
        pm, load_defects(), degrees=degree_map(FME),
    )
    keys = [f.formula_cell for f in out]
    assert keys == sorted(keys, key=_cell_order)


def test_det__the_relation_catalogue_is_in_file_order_not_glob_order() -> None:
    """A relation set enumerated by `Path.glob` is ordered by the filesystem, which differs
    between the two CI runner images and would break `verify` for a reason nobody would look
    for."""
    assert [s.id for s in load()] == ["R-01", "R-02", "R-03", "R-05", "R-06", "R-07"]
