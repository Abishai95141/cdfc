"""P6-B3 — the campaign's arithmetic, and the renderer that cannot print a bare rate."""

from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.campaign import (  # noqa: E402
    V0_BASELINE,
    Campaign,
    CampaignArithmeticError,
    ClassTally,
    restate_v0,
    tally,
)


def _campaign(**tallies) -> Campaign:
    return Campaign("test", {k: v for k, v in tallies.items()}, fault_model_digest="d" * 64)


def test_campaign__kill_rate_is_over_observable() -> None:
    c = _campaign(F01=tally(G=100, U=40, I=0, K=30))
    assert c.kill_rate() == Fraction(1, 2), "30/60, not 30/100"
    assert c.unobservable_rate() == Fraction(2, 5)


def test_campaign__zero_observable_raises() -> None:
    """A campaign in which nothing was observable has told us nothing. It does not print 0.0."""
    with pytest.raises(CampaignArithmeticError, match="told us nothing"):
        _campaign(F01=tally(G=10, U=10, I=0)).kill_rate()


def test_campaign__o_is_defined_not_carried() -> None:
    with pytest.raises(CampaignArithmeticError, match="O is DEFINED as"):
        ClassTally(G=10, U=2, I=1, O=9, R=0, K=0)


def test_campaign__more_killed_than_observable_raises() -> None:
    """The harness v1 printed 100.1% this way."""
    with pytest.raises(CampaignArithmeticError, match="harness v1"):
        tally(G=10, U=0, I=0, K=11)


def test_campaign__render_never_bare() -> None:
    out = _campaign(F01=tally(G=100, U=40, I=10, R=5, K=20)).render()
    for token in ("G", "U", "I", "O", "R", "K", "U/G", "I/G", "K/O"):
        assert token in out
    assert not re.search(r"(?<![/\d])\d+(\.\d+)?%", out), "a lone percentage escaped the renderer"
    assert "F14" in out, "the per-class vector renders every class, zeroes included"


def test_campaign__render_never_shows_UG_without_I() -> None:
    """F18. Table-driven over every rendering path that emits U/G."""
    c = _campaign(F01=tally(G=100, U=40, I=10, K=20))
    # UNCONDITIONAL. An earlier version guarded on `if "U/G" in text`, so a renderer that dropped
    # U/G entirely satisfied it — the test passed by the rate disappearing, which is the one
    # outcome it must not accept.
    rendered = c.render()
    assert "U/G = 40/100" in rendered, "U/G must render, with both integers"
    assert "I/G = 10/100" in rendered, (
        "U/G rendered without I beside it: it would describe our apparatus while claiming to "
        "describe the fault model"
    )
    manifest = c.as_manifest()
    assert manifest["unobservable_rate"] == "40/100"
    assert manifest["indeterminate_rate"] == "10/100"


def test_campaign__the_caveat_ships_with_the_number() -> None:
    out = _campaign(F01=tally(G=10, U=2, I=1, K=3)).render()
    assert "coupling effect" in out and "does NOT say what fraction" in out


def test_campaign__totals_sum_the_classes() -> None:
    c = _campaign(F01=tally(G=10, U=1, I=1, K=2), F02=tally(G=20, U=2, I=0, K=5))
    t = c.totals
    assert (t.G, t.U, t.I, t.O, t.K) == (30, 3, 1, 26, 7)


def test_campaign__v0_is_restated_and_the_form_is_refused() -> None:
    text = restate_v0()
    assert "does not compute that form" in text
    assert "theorem" in text and "diff" in text
    assert "REACH, not QUALITY" in text
    assert str(V0_BASELINE["generated"]) in text


def test_prop__kill_rate_arithmetic() -> None:
    """`K <= O <= G`, `U + I == G - O`, `R <= O`, `KR in [0,1]` — never > 1."""
    import itertools

    checked = 0
    for g, u, i in itertools.product(range(0, 12, 3), repeat=3):
        if u + i > g:
            continue
        o = g - u - i
        for k in range(0, o + 1, max(1, o or 1)):
            for r in range(0, o + 1, max(1, o or 1)):
                t = tally(G=g, U=u, I=i, R=r, K=k)
                assert t.K <= t.O <= t.G
                assert t.U + t.I == t.G - t.O
                assert t.R <= t.O
                if t.O:
                    assert 0 <= Fraction(t.K, t.O) <= 1
                checked += 1
    assert checked > 40, "the enumeration is too small to be a property"
