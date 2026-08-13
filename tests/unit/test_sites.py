"""P6-B4 — the site universe, and the two arms that are three different sets."""

from __future__ import annotations

import ast
import inspect
import sys
from fractions import Fraction
from math import ceil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.sites import partition, site_universe, stratified, upstream_index  # noqa: E402


def test_sites__universe_equals_field_surface() -> None:
    from cdfc.measure.p5_run import fme_surface

    n, surface, _ = fme_surface()
    assert len(site_universe(surface)) == n == 3747


def test_sites__universe_takes_no_predicate() -> None:
    """v0 sampled sites from the predicates' read set and scored 100.0% on 3,574 mutants."""
    params = list(inspect.signature(site_universe).parameters)
    assert params == ["field_surface", "excluded"]
    assert not any("predicate" in p for p in params)


def test_sites__import_closure_does_not_reach_cdfc_predicates() -> None:
    """Asserted on the imports, not on a convention."""
    tree = ast.parse((REPO / "src" / "cdfc" / "qualify" / "sites.py").read_text(encoding="utf-8"))
    mods: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            mods.add(n.module or "")
    assert not any(m.startswith("cdfc.predicates") for m in mods), sorted(mods)


def test_sites__control_excludes_the_upstream_cone() -> None:
    universe = frozenset(f"S!A{i}" for i in range(1, 51)) | {"T!B1", "T!B2"}
    upstream = {"S!A1": frozenset({"T!B1"})}     # T!B1 FEEDS the read set
    s = partition(universe, ["S!A1"], upstream, rng_seed=7)
    assert "T!B1" in s.excluded_cone, (
        "a cell that feeds the read set will legitimately change what the predicate sees; "
        "counting it as a spurious fire forces the threshold to a fudge factor"
    )
    assert "T!B1" not in s.control
    assert s.primary == {"S!A1"}
    assert s.primary & s.control == frozenset()


def test_sites__a_genuine_outside_site_is_in_control() -> None:
    """The admission-side twin: the control arm is not simply empty."""
    universe = frozenset(f"S!A{i}" for i in range(1, 51)) | {"T!B1"}
    s = partition(universe, ["S!A1"], {"S!A1": frozenset({"T!B1"})}, rng_seed=7)
    assert s.control and s.control <= universe - {"S!A1", "T!B1"}


def test_sites__control_is_at_least_ten_percent() -> None:
    universe = frozenset(f"S!A{i}" for i in range(1, 201))
    reads = [f"S!A{i}" for i in range(1, 51)]
    s = partition(universe, reads, {r: frozenset() for r in reads}, rng_seed=3)
    assert len(s.control) >= ceil(0.10 * len(s.primary)) > 0


def test_sites__a_missing_upstream_map_raises_rather_than_defaulting() -> None:
    with pytest.raises(ValueError, match="NC-Q32"):
        partition(frozenset({"S!A1"}), ["S!A1"], None, rng_seed=1)


def test_sites__the_digest_reproduces_from_the_seed() -> None:
    universe = frozenset(f"S!A{i}" for i in range(1, 101))
    reads = ["S!A1", "S!A2"]
    up = {r: frozenset() for r in reads}
    assert partition(universe, reads, up, rng_seed=11).digest == \
           partition(universe, reads, up, rng_seed=11).digest
    assert partition(universe, reads, up, rng_seed=11).digest != \
           partition(universe, reads, up, rng_seed=12).digest


def test_sites__stratified_returns_its_rule() -> None:
    """Reducing the sample and SAYING SO is arithmetic; reducing the operator set is manipulation."""
    universe = frozenset(f"S!A{i}" for i in range(1, 101))
    strata = {c: ("even" if int(c[3:]) % 2 == 0 else "odd") for c in universe}
    chosen, rule = stratified(universe, per_stratum=5, strata=strata, rng_seed=2)
    assert len(chosen) == 10
    assert "per stratum" in rule and "seed 2" in rule and "of 100" in rule


def test_sites__upstream_index_inverts_the_downstream_map() -> None:
    down = {("S", "A1"): frozenset({("S", "B1"), ("S", "C1")})}
    up = upstream_index(down)
    assert up["S!B1"] == frozenset({"S!A1"}) and up["S!C1"] == frozenset({"S!A1"})
