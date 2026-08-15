"""P12-B1 — the draw: the stopping rule, the cap that is not a stopping rule, and three integers.

The draw is the object the experiment's credibility rests on. Two of the defects it can carry are
invisible in the published number: a Stratum-B cap that truncates the denominator of the very
fraction being measured (NC-M03), and a `|A| < 20` shortfall reported as a draw. Both make the
result look better and neither leaves a trace, so both are asserted here from the admission side —
a draw that *should* overshoot the cap, and a pool that *cannot* reach 20.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.draw import (  # noqa: E402
    Draw,
    ExcludedObligation,
    ExtensionAlreadyTaken,
    Obligation,
    Pool,
    PoolExhausted,
    TableOracle,
    draw,
    extend,
    permutation,
)
from cdfc.experiment.enumerate_shall import _sub_clause_key  # noqa: E402

# --- fixtures: a pool is cheap to build, and every test below wants a different SHAPE of one ------


def _ob(n: int, reg: int = 1, sub: tuple[str, ...] = ("1",)) -> Obligation:
    return Obligation(
        ordinal=n, reg_no=reg, sub_clause=sub,
        quote=f"{reg}. ({sub[0]}) The FME shall do the thing at ordinal {n}.",
        char_span=(10 * n + 1, 10 * n + 9), source_sha256="a" * 64,
    )


def _pool(n: int, excluded: int = 0) -> Pool:
    return Pool(
        obligations=tuple(_ob(i) for i in range(n)),
        excluded=tuple(
            ExcludedObligation(
                quote=f"The FME shall, in the disputed region {i}, do a thing.",
                char_span=(9000 + i, 9020 + i), page=41 + i,
                reason="the extractions disagree here, so no party's reading is authoritative",
            )
            for i in range(excluded)
        ),
        source_sha256="a" * 64,
        chapters=("Chapter III",),
    )


def _oracle(assignment: dict[int, str]) -> TableOracle:
    return TableOracle(
        assignment=assignment,                                    # type: ignore[arg-type]
        assigner=dict.fromkeys(assignment, "R. Nair (assigner of record)"),
    )


def _every_nth_is_a(n: int, stride: int) -> dict[int, str]:
    """Stratum A on one index in `stride`. `stride=6` makes B outnumber A five to one."""
    return {i: ("A" if i % stride == 0 else "B") for i in range(n)}


# --- the stopping rule ---------------------------------------------------------------------------


def test_draw__stops_at_twenty_stratum_a() -> None:
    """The draw is defined by `|A| = 20`, and nothing else may end it.

    The stopping rule is what makes `k of 20` a threshold applied to the denominator it was chosen
    for. A draw that stopped on any other condition — a total count, a cap, an index — would put a
    different denominator under a rule written for this one.
    """
    pool = _pool(200)
    strata = _every_nth_is_a(200, 2)
    d = draw(pool, seed=7, strata=_oracle(strata))

    assert len(d.stratum_a) == 20
    assert d.stage == 1
    # It stops ON the twentieth A, never one obligation later: the last index consumed is an A.
    assert d.drawn[-1] == d.stratum_a[-1]
    assert all(strata[pool.obligations[i].ordinal] == "A" for i in d.stratum_a)
    assert all(strata[pool.obligations[i].ordinal] == "B" for i in d.stratum_b_all)


def test_draw__b_cap_does_not_stop_the_draw() -> None:
    """**The admission-side positive control for NC-M03.**

    NC-M03 says the Stratum-B cap is a cap on GENERATION and never on the denominator. A control
    that only showed the cap being obeyed would pass just as happily against an implementation that
    stopped the draw at ten Bs — which is the defect, because it truncates `|drawn|`, the
    denominator of the decidable fraction, in the flattering direction.

    So this is the positive half: a pool where B outnumbers A five to one, which FORCES the draw
    well past ten Bs before it has twenty As. `|A| == 20` still, `stratum_b_all` is much larger
    than the cap, and `stratum_b_generated` is exactly the cap. A cap that stopped the draw could
    not produce this state at all.
    """
    pool = _pool(300)
    d = draw(pool, seed=11, strata=_oracle(_every_nth_is_a(300, 6)))

    assert len(d.stratum_a) == 20, "the cap ended the draw before the stopping rule did"
    assert len(d.stratum_b_all) > 10, (
        "this pool cannot yield 20 As inside 10 Bs; a stratum_b_all of 10 means the cap truncated "
        "the denominator, which is NC-M03 exactly"
    )
    assert len(d.stratum_b_generated) == 10
    assert len(d.drawn) == len(d.stratum_a) + len(d.stratum_b_all)
    # The generated set is the FIRST ten in draw order — not a re-pick, not a sample of a sample.
    assert d.stratum_b_generated == d.stratum_b_all[:10]


def test_draw__pool_exhausted_raises_never_returns_short() -> None:
    """A 19-obligation draw is not a smaller draw; it is a measurement of the instrument.

    `k of 19` evaluated against a rule written for 20 is a threshold applied to a denominator it
    was not chosen for, and the shortfall is invisible in the published fraction. The only safe
    shape is an exception, so the assertion is that **nothing was bound** — a returned `Draw` of
    any size would have been assigned here.
    """
    pool = _pool(30, excluded=3)
    strata = {i: ("A" if i < 19 else "B") for i in range(30)}

    result: Draw | None = None
    with pytest.raises(PoolExhausted) as e:
        result = draw(pool, seed=3, strata=_oracle(strata))

    assert result is None, "a short draw was returned instead of raising"
    assert "19 Stratum-A of the 20" in str(e.value)
    assert "after excluding 3 in extractor-disputed regions" in str(e.value), (
        "the shortfall must carry the exclusion count: |A| < 20 is a fact about our curation of "
        "the instrument, and a reader cannot size it without that integer"
    )


def test_draw__ordering_is_arithmetic_not_lexical() -> None:
    """Regulation 9 before regulation 51, and sub-clause `(10)` after `(9)`.

    The permutation is keyed on the pool hash, and the pool hash is over the obligations **in
    canonical order** — so a lexical ordering is not a cosmetic defect. It is a different draw
    wearing the same seed, and `draw.json` would record the seed that supposedly produced it.

    The test asserts both halves: that the arithmetic order is right, and that the lexical order is
    DIFFERENT. Without the second half this passes against a sort that happens to agree on the
    fixture, which is how an ordering bug survives its own test.
    """
    obs = (
        _ob(0, 51, ("1",)), _ob(1, 9, ("1",)), _ob(2, 9, ("10",)), _ob(3, 9, ("9",)),
    )

    def arithmetic(o: Obligation) -> tuple:
        return (o.reg_no, _sub_clause_key(o.sub_clause), o.char_span[0])

    def lexical(o: Obligation) -> tuple:
        return (str(o.reg_no), tuple(str(s) for s in o.sub_clause), o.char_span[0])

    got = [(o.reg_no, o.sub_clause) for o in sorted(obs, key=arithmetic)]
    lex = [(o.reg_no, o.sub_clause) for o in sorted(obs, key=lexical)]

    assert got == [(9, ("1",)), (9, ("9",)), (9, ("10",)), (51, ("1",))]
    assert lex == [(51, ("1",)), (9, ("1",)), (9, ("10",)), (9, ("9",))]
    assert got != lex, "the fixture does not distinguish arithmetic from lexical ordering"
    # The component key itself, so the property survives a change of sort call site.
    assert _sub_clause_key(("9",)) < _sub_clause_key(("10",))
    assert _sub_clause_key(("9",)) < _sub_clause_key(("a",)), "a letter sorts after any number"

    # AND IT REACHES THE DRAW: the two orders are two pools, two hashes, two permutations.
    arith_pool = Pool(
        obligations=tuple(
            Obligation(ordinal=n, reg_no=o.reg_no, sub_clause=o.sub_clause, quote=o.quote,
                       char_span=o.char_span, source_sha256=o.source_sha256)
            for n, o in enumerate(sorted(obs, key=arithmetic))
        ),
        excluded=(), source_sha256="a" * 64, chapters=("Chapter III",),
    )
    lex_pool = Pool(
        obligations=tuple(
            Obligation(ordinal=n, reg_no=o.reg_no, sub_clause=o.sub_clause, quote=o.quote,
                       char_span=o.char_span, source_sha256=o.source_sha256)
            for n, o in enumerate(sorted(obs, key=lexical))
        ),
        excluded=(), source_sha256="a" * 64, chapters=("Chapter III",),
    )
    assert arith_pool.sha256 != lex_pool.sha256
    assert (permutation(arith_pool.sha256, 4, seed=7)
            != permutation(lex_pool.sha256, 4, seed=7)), (
        "a wrong canonical order would be a different draw carrying the same seed"
    )


# --- the one extension ----------------------------------------------------------------------------


def test_extend__continues_the_same_permutation() -> None:
    """Stage 2 is the NEXT PREFIX of one total order, not a second experiment.

    §0.3 interpretation A: one draw with a stopping rule. Because the order is a keyed sort rather
    than PRNG state somebody has to have kept, "the same permutation without replacement" is
    checkable rather than promised — stage 2's fresh indices must be the continuation of stage 1's
    order and must not repeat anything stage 1 already consumed.
    """
    pool = _pool(200)
    strata = _every_nth_is_a(200, 2)
    one = draw(pool, seed=7, strata=_oracle(strata))
    two = extend(one, pool, strata=_oracle(strata))

    assert two.stage == 2
    assert two.order == one.order, "the extension re-rolled the permutation"
    assert two.drawn[:len(one.drawn)] == one.drawn, "stage 1's prefix was not preserved"

    fresh = two.drawn[len(one.drawn):]
    assert fresh == one.order[len(one.drawn):len(two.drawn)], "stage 2 left the shared order"
    assert set(fresh).isdisjoint(set(one.drawn)), "an obligation was drawn twice"

    # The pooled result — the thing the `>= 12 of 40` threshold is evaluated over.
    assert len(two.stratum_a) == 40
    assert two.stratum_a[:20] == one.stratum_a
    assert len(two.drawn) == len(two.stratum_a) + len(two.stratum_b_all)


def test_extend__second_extension_raises() -> None:
    """There is no third stage, ever (§0.5, NC-M14).

    A second extension is re-rolling a criterion that has already been evaluated twice — the
    stopping rule turned into a sampling budget, which is the shape of every optional-stopping
    defect. The refusal is on the stage of the draw handed in, so it holds however the caller got
    there.
    """
    pool = _pool(200)
    strata = _every_nth_is_a(200, 2)
    one = draw(pool, seed=7, strata=_oracle(strata))
    two = extend(one, pool, strata=_oracle(strata))

    with pytest.raises(ExtensionAlreadyTaken) as e:
        extend(two, pool, strata=_oracle(strata))
    assert "there is no third stage" in str(e.value)


def test_extend__refuses_a_different_pool() -> None:
    """Continuing "the same permutation" over a RE-CURATED pool is NC-M34.

    The refusal is on `pool.sha256`, which covers the exclusions as well as the obligations — so a
    pool whose obligations are identical but whose disputed-region set was edited after stage 1 is
    still refused. That is the case worth having: it is the one that looks like the same pool.
    """
    pool = _pool(200)
    strata = _every_nth_is_a(200, 2)
    one = draw(pool, seed=7, strata=_oracle(strata))

    recurated = _pool(200, excluded=1)
    assert tuple(o.as_obj() for o in recurated.obligations) == tuple(
        o.as_obj() for o in pool.obligations
    ), "the fixture must differ ONLY in the exclusion set"
    assert recurated.sha256 != pool.sha256

    with pytest.raises(ValueError) as e:
        extend(one, recurated, strata=_oracle(strata))
    assert "a different pool than stage 1" in str(e.value)


# --- reproducibility, and the three integers -----------------------------------------------------


def test_draw__is_reproducible_from_the_seed_alone() -> None:
    """A reader who doubts us must be able to RECOMPUTE the draw, not just re-read it.

    This is why the permutation is a sha256-keyed sort rather than `random.Random(seed).shuffle`:
    the guarantee has to survive a different interpreter, a different language and a decade. Byte
    identity of `as_json()` is the form of that claim `draw.json` is published under.
    """
    pool = _pool(200)
    strata = _every_nth_is_a(200, 2)

    first = draw(pool, seed=7, strata=_oracle(strata))
    again = draw(pool, seed=7, strata=_oracle(strata))
    assert first.as_json() == again.as_json()
    assert first.sha256 == again.sha256

    other = draw(pool, seed=8, strata=_oracle(strata))
    assert other.order != first.order, "the seed does not reach the permutation"
    assert other.as_json() != first.as_json()

    # And the pool hash is inside the key, so the same seed over a different pool is a different
    # order — otherwise a pool edited after the draw keeps its ordering and the edit is invisible.
    assert permutation(pool.sha256, 200, seed=7) != permutation("b" * 64, 200, seed=7)


def test_draw__decidable_fraction_is_three_integers() -> None:
    """`(|A|, |drawn|, excluded)` — and the third is NEVER folded into the first two (NC-M34).

    The excluded count is the size of our curation of the instrument. Added into `|drawn|` it
    inflates the denominator with obligations nobody was asked about; dropped, the reader sizes the
    fraction without knowing how much of the instrument we set aside. It is a third integer for
    exactly that reason, and no single ratio is returned here at all.
    """
    pool = _pool(200, excluded=4)
    d = draw(pool, seed=7, strata=_oracle(_every_nth_is_a(200, 2)))
    a, drawn, excluded = d.decidable_fraction()

    assert [type(x) for x in (a, drawn, excluded)] == [int, int, int]
    assert (a, excluded) == (20, 4)
    assert drawn == len(d.stratum_a) + len(d.stratum_b_all), "excluded was folded into |drawn|"
    assert a == len(d.stratum_a), "excluded was folded into |A|"
    # No excluded obligation is reachable from the draw: they are not in the pool to be drawn.
    quotes = {pool.obligations[i].quote for i in d.drawn}
    assert quotes.isdisjoint({e.quote for e in pool.excluded})
    assert pool.excluded_pages() == (41, 42, 43, 44), "the locations travel with the count"


def test_draw__a_draw_whose_strata_do_not_sum_cannot_be_constructed() -> None:
    """The §0.4 invariant is STRUCTURAL — enforced at construction, not only asserted in a test.

    A test can be deleted or skipped; a `__post_init__` cannot be bypassed by any caller in the
    package. A `Draw` whose `drawn` is not exactly its two strata would publish a decidable
    fraction over a truncated denominator, so it must not be a representable object.
    """
    with pytest.raises(ValueError) as e:
        Draw(pool_sha256="p", seed=1, order=(0, 1, 2), drawn=(0, 1, 2),
             stratum_a=(0,), stratum_b_all=(1,), stratum_b_generated=(1,),
             excluded_count=0, stage=1)
    assert "NC-M03" in str(e.value)
    assert "cap on what is PROCESSED and never on what is COUNTED" in str(e.value)

    # The counts can agree while the SETS do not — caught separately, because a draw whose members
    # are not its strata's members is the same lie with matching arithmetic.
    with pytest.raises(ValueError) as e:
        Draw(pool_sha256="p", seed=1, order=(0, 1), drawn=(0, 1),
             stratum_a=(0,), stratum_b_all=(9,), stratum_b_generated=(9,),
             excluded_count=0, stage=1)
    assert "not the union of its strata" in str(e.value)

    # The generated set must be a PREFIX of the drawn one, never a re-pick.
    with pytest.raises(ValueError) as e:
        Draw(pool_sha256="p", seed=1, order=(0, 1, 2), drawn=(0, 1, 2),
             stratum_a=(0,), stratum_b_all=(1, 2), stratum_b_generated=(2,),
             excluded_count=0, stage=1)
    assert "not a prefix" in str(e.value)


def test_draw__unassigned_obligation_cannot_be_drawn() -> None:
    """An unassigned obligation raises rather than defaulting to a stratum.

    The stratum assignment is the one human judgment the whole `n = 20` rests on. A default turns
    that judgment into a fallback, and — because Stratum B is the larger, cheaper class — the
    fallback would silently be "not decidable" for every row the assigner never reached.
    """
    oracle = _oracle({0: "A", 1: "B"})
    assert oracle.stratum_of(0) == "A"
    assert oracle.assigned_by(0) == "R. Nair (assigner of record)"

    with pytest.raises(LookupError) as e:
        oracle.stratum_of(2)
    assert "has no stratum" in str(e.value)
    assert "would make a human judgment into a fallback" in str(e.value)

    # And it propagates out of `draw` rather than being swallowed into a smaller pool.
    with pytest.raises(LookupError):
        draw(_pool(5), seed=1, strata=oracle)
