"""P12-B1 — the three properties of the draw that no fixture can establish.

A fixture shows the draw behaving on one pool. These are the statements that have to hold on
*every* pool the experiment could have been run over, because each one is a claim `draw.json` makes
to a reader who was not there: that the seed alone regenerates it, that the Stratum-B cap never
reached the denominator, and that the order is a permutation rather than a selection.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.draw import (  # noqa: E402
    Obligation,
    Pool,
    Stratum,
    TableOracle,
    draw,
    permutation,
)

PROFILE = settings(
    max_examples=50, deadline=None, derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


@st.composite
def pool_and_strata(draw_) -> tuple[Pool, dict[int, Stratum], int]:
    """A pool of 40–400, a stratum map with AT LEAST 20 As, and a seed.

    The A count is bounded below at 20 on purpose: `PoolExhausted` is a real and correct outcome,
    but it is a different property with its own unit test, and letting it dominate the generated
    examples would leave these three properties asserted over pools that never got drawn.
    """
    n = draw_(st.integers(min_value=40, max_value=400))
    n_a = draw_(st.integers(min_value=20, max_value=n))
    tag = draw_(st.integers(min_value=0, max_value=2**31))
    seed = draw_(st.integers(min_value=-(2**40), max_value=2**40))

    # Which indices are A: scattered through the pool rather than clumped at the front, so the
    # draw has to walk past Bs to reach its twenty.
    scattered = sorted(range(n), key=lambda i: hashlib.sha256(f"{tag}:{i}".encode()).digest())
    a_set = set(scattered[:n_a])
    strata: dict[int, Stratum] = {i: ("A" if i in a_set else "B") for i in range(n)}

    pool = Pool(
        obligations=tuple(
            Obligation(
                ordinal=i, reg_no=1 + i // 4, sub_clause=(str(1 + i % 4),),
                quote=f"{1 + i // 4}. ({1 + i % 4}) The FME shall do thing {i}.",
                char_span=(10 * i + 1, 10 * i + 9), source_sha256="a" * 64,
            )
            for i in range(n)
        ),
        excluded=(), source_sha256="a" * 64, chapters=("Chapter III",),
    )
    return pool, strata, seed


def _oracle(strata: dict[int, Stratum]) -> TableOracle:
    return TableOracle(assignment=strata, assigner=dict.fromkeys(strata, "R. Nair"))


@PROFILE
@given(pool_and_strata())
def test_prop__the_draw_is_reproducible_from_the_seed_alone(case) -> None:
    """Same pool, same seed, same strata — byte-identical `draw.json`, on every pool shape.

    This is the whole reason the permutation is a sha256-keyed sort and not
    `random.Random(seed).shuffle`: the reproducibility claim has to be checkable by someone with a
    hash function and the seed, not by someone with our interpreter. Determinism that held only on
    the pool we happened to test would be an accident of that pool's size.
    """
    pool, strata, seed = case
    first = draw(pool, seed=seed, strata=_oracle(strata))
    again = draw(pool, seed=seed, strata=_oracle(strata))

    assert first.as_json() == again.as_json()
    assert first.sha256 == again.sha256
    assert first.order == permutation(pool.sha256, len(pool.obligations), seed=seed), (
        "the recorded order is not the one the published algorithm regenerates"
    )
    # The order is recorded WHOLE, not just the prefix consumed — a reader can replay past the stop.
    assert len(first.order) == len(pool.obligations)
    assert first.drawn == first.order[:len(first.drawn)]


@PROFILE
@given(pool_and_strata())
def test_prop__b_cap_never_touches_the_denominator(case) -> None:
    """**NC-M03's guard: `|drawn| == |A| + |B_all|`, for every pool and every stratum map.**

    `|A| / |drawn|` is the published decidable fraction. If the Stratum-B cap ever ends the draw,
    the Bs it declined to record vanish from `|drawn|` — the denominator shrinks, the fraction
    rises, and nothing in the artifact says a number was withheld. That is scope truncation,
    NC-D01's mechanism, turned on our own headline.

    The cap is allowed to bind only `stratum_b_generated`, which is what is carried into candidate
    generation and appears in no fraction at all.
    """
    pool, strata, seed = case
    d = draw(pool, seed=seed, strata=_oracle(strata))

    assert len(d.drawn) == len(d.stratum_a) + len(d.stratum_b_all)
    assert set(d.drawn) == set(d.stratum_a) | set(d.stratum_b_all)
    assert len(d.stratum_a) == 20, "the draw ended on something other than the stopping rule"

    # The cap binds generation and nothing else, and the generated set is a true prefix of the
    # drawn one — the first ten in draw order, never a re-pick.
    assert len(d.stratum_b_generated) == min(10, len(d.stratum_b_all))
    assert d.stratum_b_generated == d.stratum_b_all[:len(d.stratum_b_generated)]

    a, drawn, excluded = d.decidable_fraction()
    assert (a, drawn) == (len(d.stratum_a), len(d.drawn))
    assert excluded == len(pool.excluded), "the third integer is not the exclusion count"


@PROFILE
@given(
    st.integers(min_value=0, max_value=500),
    st.integers(min_value=-(2**40), max_value=2**40),
    st.text(min_size=1, max_size=64),
)
def test_prop__permutation_is_a_true_permutation_of_range_n(
    n: int, seed: int, pool_hash: str
) -> None:
    """Every index exactly once — a reordering, never a selection.

    A keyed sort whose key collided, or whose tie-break was not total, would silently drop or
    duplicate an index. A dropped index is an obligation that could never be drawn no matter how
    long the draw ran; a duplicated one is an obligation the model is asked about twice and counted
    twice. Both are invisible in a draw that stops after twenty As, because the defect lives in the
    tail nobody consumed.
    """
    order = permutation(pool_hash, n, seed=seed)

    assert len(order) == n
    assert sorted(order) == list(range(n)), "not a permutation: an index is missing or repeated"
    assert order == permutation(pool_hash, n, seed=seed), "not a pure function of its arguments"
    # The order must depend on the pool hash, or a pool edited after the draw keeps its ordering
    # and the edit is invisible in `draw.json`. Asserted only from n = 8, where two independent
    # keyed sorts agreeing by chance is one outcome in 8! rather than the coin flip it is at n = 2.
    if n >= 8:
        assert order != permutation(pool_hash + "!", n, seed=seed)
        assert order != permutation(pool_hash, n, seed=seed + 1)
