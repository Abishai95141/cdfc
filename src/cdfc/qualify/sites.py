"""P6-B4 — the site universe, the primary arm and the control arm. **Three different sets.**

**`site_universe` takes NO predicate parameter, and its import closure does not reach
`cdfc.predicates`.** That is not style. v0 sampled mutation sites *from the predicates' read set*
and scored **100.0% on 3,574 mutants** — the degenerate-baseline failure, committed by the harness  # rate-ok: v0's historical figure, named as the defect
built to detect it. A universe that cannot see the predicates cannot be drawn from them, and the
absence is asserted by an import walk rather than by a convention.

**The control arm excludes the UPSTREAM CLOSURE, not merely the read set**, and that is what makes
the correct spurious-fire threshold **exactly zero** rather than a fudge factor. A mutant seeded at
a cell that FEEDS the predicate's read set will legitimately change what the predicate sees; count
it as a spurious fire and the threshold has to be softened — and a softened threshold then hides a
real flag-everything predicate. NC-Q32.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from math import ceil
from typing import Any

from cdfc.schema.anchor import Anchor
from cdfc.canon import canonical_json

CellKey = str  # "Sheet!REF"


@dataclass(frozen=True, slots=True)
class SiteSet:
    universe: frozenset[CellKey]
    primary: frozenset[CellKey]
    control: frozenset[CellKey]
    control_fraction: Fraction
    rng_seed: int
    digest: str
    # The cells the control arm was NOT allowed to draw from: the read set plus everything
    # upstream of it. Exposed because it is the DECISION — which cells are eligible — and the
    # sample drawn from it is a separate step. A guard that asserted on the sample would pass or
    # fail on the sampler's luck, which is not a control.
    excluded_cone: frozenset[CellKey] = frozenset()

    def as_row(self) -> dict[str, Any]:
        return {
            "universe": len(self.universe),
            "primary": len(self.primary),
            "control": len(self.control),
            "control_fraction": str(self.control_fraction),
            "rng_seed": self.rng_seed,
            "digest": self.digest,
        }


def site_universe(
    field_surface: Iterable[tuple[str, str]] | Iterable[CellKey],
    *,
    excluded: Iterable[CellKey] = (),
) -> frozenset[CellKey]:
    """The mask's field surface, minus the pinned engine-disagreement exclusions.

    **One parameter, and it is the surface.** `test_sites__universe_takes_no_predicate` asserts the
    signature, because the defect this guards is a universe drawn from the thing it is meant to
    measure.
    """
    cells = {c if isinstance(c, str) else Anchor.cell(c[0], c[1]).render() for c in field_surface}
    return frozenset(cells - set(excluded))


def _digest(universe: Iterable[str], primary: Iterable[str], control: Iterable[str]) -> str:
    payload = {
        "universe": sorted(universe), "primary": sorted(primary), "control": sorted(control),
    }
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def partition(
    universe: frozenset[CellKey],
    read_set: Iterable[CellKey],
    upstream: Mapping[CellKey, frozenset[CellKey]] | None = None,
    *,
    control_fraction: Fraction = Fraction(1, 10),
    rng_seed: int,
) -> SiteSet:
    """`primary = universe ∩ read_set`; `control` is drawn from `universe \\ upstream_closure(read_set)`.

    `upstream[cell]` is every cell that feeds `cell`. A missing map is treated as *no upstream
    information*, which makes the control arm the read-set complement — **the NC-Q32 break** — so
    it raises rather than defaulting.
    """
    reads = frozenset(read_set) & universe
    if upstream is None:
        raise ValueError(
            "partition() needs the upstream map. Excluding only the read set is NC-Q32: legitimate "
            "propagation is then counted as a spurious fire, the threshold has to be softened to a "
            "fudge factor, and the fudge factor hides a real flag-everything predicate."
        )
    cone: set[CellKey] = set(reads)
    for cell in reads:
        cone |= upstream.get(cell, frozenset())
    candidates = sorted(universe - cone)
    want = max(1, ceil(float(control_fraction) * len(reads))) if reads else 0
    rng = random.Random(rng_seed)
    control = frozenset(rng.sample(candidates, min(want, len(candidates))))
    return SiteSet(
        universe=universe,
        primary=reads,
        control=control,
        excluded_cone=frozenset(cone),
        control_fraction=control_fraction,
        rng_seed=rng_seed,
        digest=_digest(universe, reads, control),
    )


def upstream_index(downstream: Mapping[Any, frozenset[Any]]) -> dict[CellKey, frozenset[CellKey]]:
    """Invert the observability module's downstream index into `cell -> everything feeding it`."""
    out: dict[CellKey, set[CellKey]] = {}
    for source, targets in downstream.items():
        s = source if isinstance(source, str) else Anchor.cell(source[0], source[1]).render()
        for t in targets:
            key = t if isinstance(t, str) else Anchor.cell(t[0], t[1]).render()
            out.setdefault(key, set()).add(s)
    return {k: frozenset(v) for k, v in out.items()}


def stratified(
    universe: frozenset[CellKey],
    *,
    per_stratum: int,
    strata: Mapping[CellKey, str],
    rng_seed: int,
) -> tuple[frozenset[CellKey], str]:
    """A published sample of the universe, and the RULE is returned with it.

    The plan sanctions sampling when a full campaign is impractical — **with the sampling rule
    published and the sample size in every quoted denominator.** Reducing the operator set to make
    the number look better is the manipulation this project bans; reducing the sample and saying so
    is arithmetic.
    """
    buckets: dict[str, list[CellKey]] = {}
    for cell in sorted(universe):
        buckets.setdefault(strata.get(cell, "UNTYPED"), []).append(cell)
    rng = random.Random(rng_seed)
    chosen: set[CellKey] = set()
    for name in sorted(buckets):
        pool = buckets[name]
        chosen |= set(rng.sample(pool, min(per_stratum, len(pool))))
    rule = (
        f"stratified by dtype, at most {per_stratum} sites per stratum, seed {rng_seed}; "
        f"{len(chosen)} of {len(universe)} field-surface cells "
        f"({', '.join(f'{k}:{min(per_stratum, len(v))}/{len(v)}' for k, v in sorted(buckets.items()))})"
    )
    return frozenset(chosen), rule
