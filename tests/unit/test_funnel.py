"""P12-B4 — the attrition funnel. **Nothing is filtered before stage 0, and every death has a row.**

A 20:1 attrition displayed honestly is a stronger demonstration than a settled-fraction bar, and a
600:0 attrition displayed honestly is stronger still — the funnel is *more* informative when nothing
survives, because it says **where** the candidates died. That only holds if the denominator is the
planned count and the discard pile is inside it: a funnel starting at `planned − discards` reports a
curated denominator and makes the parse stage invisible, which is NC-M11 wearing the clothes of a
data-cleaning step.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.funnel import (  # noqa: E402
    STAGE_ORDER,
    Funnel,
    FunnelInvariantViolated,
    FunnelStage,
    RejectionRow,
    funnel,
    planned_count,
)

OBLIGATIONS, REGIMES, K = 3, 2, 10
PLANNED = OBLIGATIONS * REGIMES * K


def _records(n: int = PLANNED) -> list[str]:
    return [f"cand-{i:04d}" for i in range(n)]


def _rejections(gate: str, n: int, *, measured: str = "K/O = 0.00 against a bar of > 0",
                start: int = 0) -> list[RejectionRow]:
    return [
        RejectionRow(
            candidate_sha256=f"{i:064x}", gate=gate,  # type: ignore[arg-type]
            reason=f"died at {gate}", measured=measured, cells_it_would_have_covered=4,
        )
        for i in range(start, start + n)
    ]


def _built(deaths: dict[str, int], **kw) -> Funnel:
    rows: list[RejectionRow] = []
    for gate, n in deaths.items():
        rows.extend(_rejections(gate, n, start=len(rows)))
    return funnel(
        _records(), rows, obligations=OBLIGATIONS, regimes=REGIMES, k=K, **kw,
    )


# --- the denominator ------------------------------------------------------------------------------


def test_funnel__stage_zero_is_the_planned_count() -> None:
    """`|obligations| × |regimes| × k`, **DISCARDS INCLUDED**.

    A malformed candidate is a row, not an absence: it enters at `generated` and dies at `parsed`.
    Starting at `600 − discards` would make the parse stage invisible and report an attrition over
    a population somebody had already cleaned — the same truncated denominator as every other one
    in this project, and the funnel is the artefact where it would be least visible because the
    first bar would still be the tallest.
    """
    out = _built({"parsed": 7, "G0": 5, "G2": 11})
    assert out.planned == PLANNED == planned_count(obligations=OBLIGATIONS, regimes=REGIMES, k=K)
    assert out.stages[0].name == "generated"
    assert out.stages[0].entered == PLANNED, "stage 0 was not the planned count"
    assert tuple(s.name for s in out.stages) == STAGE_ORDER

    parsed = next(s for s in out.stages if s.name == "parsed")
    assert parsed.entered == PLANNED and parsed.survived == PLANNED - 7, (
        "the 7 discards must be visible as a death AT parsed, not as 7 rows that never existed"
    )
    assert out.survived == PLANNED - 23
    assert out.as_obj()["planned"] == PLANNED


def test_funnel__records_already_filtered_are_refused() -> None:
    """Handing in the survivors of a filter nobody counted builds a funnel about another experiment.

    This is the same defect as the previous test seen from the caller's side: the discard pile is
    data, so `len(records)` must equal the planned count. Accepting a short sequence would let the
    cleaning happen upstream, where no invariant can see it.
    """
    with pytest.raises(FunnelInvariantViolated) as e:
        funnel(_records(PLANNED - 5), [], obligations=OBLIGATIONS, regimes=REGIMES, k=K)
    assert "discard pile is data" in str(e.value)

    with pytest.raises(FunnelInvariantViolated):
        funnel(_records(PLANNED + 1), [], obligations=OBLIGATIONS, regimes=REGIMES, k=K)

    assert funnel(_records(), [], obligations=OBLIGATIONS, regimes=REGIMES, k=K).survived == PLANNED


# --- every death is accounted for ----------------------------------------------------------------


def test_funnel__every_rejection_carries_its_measured_number() -> None:
    """*"Rejected at G2"* is not a finding; *"rejected at G2 with K/O = 0.05 against 0.80"* is.

    A rejection table with no numbers is a log, and a log is unreadable by the one audience that
    matters — someone who did not run the experiment. The number is refused at construction rather
    than defaulted to `"n/a"`, because a defaulted string renders identically to a measured one.
    """
    with pytest.raises(FunnelInvariantViolated) as e:
        RejectionRow(candidate_sha256="a" * 64, gate="G2", reason="kill rate too low",
                     measured="", cells_it_would_have_covered=3)
    assert "is a log" in str(e.value)

    with pytest.raises(FunnelInvariantViolated):
        RejectionRow(candidate_sha256="a" * 64, gate="G2", reason="", measured="K/O = 0.05",
                     cells_it_would_have_covered=3)

    ok = RejectionRow(candidate_sha256="a" * 64, gate="G2", reason="kill rate too low",
                      measured="K/O = 0.05 against a bar of 0.80", cells_it_would_have_covered=3)
    assert ok.as_obj()["measured"] == "K/O = 0.05 against a bar of 0.80"


def test_funnel__a_death_with_no_row_cannot_be_constructed() -> None:
    """`entered − survived == len(rejections)`, exactly — a gap is a candidate that left silently.

    An unexplained drop between two numbers is the absence this whole project refuses to render as
    silence: the reader sees attrition and supplies their own reason for it, and the supplied
    reason is always the one that flatters whoever drew the chart.
    """
    with pytest.raises(FunnelInvariantViolated) as e:
        FunnelStage(name="G2", entered=10, survived=7, rejections=())
    assert "death with no row" in str(e.value)

    with pytest.raises(FunnelInvariantViolated):
        FunnelStage(name="G2", entered=10, survived=9, rejections=tuple(_rejections("G2", 3)))

    with pytest.raises(FunnelInvariantViolated) as e:
        FunnelStage(name="G2", entered=10, survived=11, rejections=())
    assert "11 survived of 10 entered" in str(e.value)

    assert FunnelStage(name="G2", entered=10, survived=7,
                       rejections=tuple(_rejections("G2", 3))).survived == 7


def test_funnel__registry_bar_survivors_cannot_exceed_the_experiment_bar() -> None:
    """The registry's survivors are a SUBSET, and a count that inverts them has confused two tests.

    The experiment asks `K/O > 0` plus a marginal kill over the free baselines; the registry asks
    `K/O ≥ 0.80` on the classes the predicate claims. A predicate at `K/O = 0.05` survives the
    experiment and fails the registry, so both counts are printed — and quoting the wrong one is
    exactly the mistake this invariant catches before `DECISION.md` is written.
    """
    out = _built({"parsed": 4, "G2": 6})
    assert out.survived == PLANNED - 10

    with pytest.raises(FunnelInvariantViolated) as e:
        _built({"parsed": 4, "G2": 6}, registry_bar_survivors=out.survived + 1)
    assert "SUBSET" in str(e.value)

    strict = _built({"parsed": 4, "G2": 6}, registry_bar_survivors=out.survived)
    assert strict.as_obj()["survived_registry_bar"] == out.survived
    assert strict.as_obj()["registry_bar"] != strict.as_obj()["experiment_bar"], (
        "the two bars must render as different strings or a reader will quote one for the other"
    )
