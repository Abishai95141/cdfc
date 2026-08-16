"""P14-B4 — the library, the funnel and the history chart.

Every test here has an admission-side twin. Without them, a library that renders nothing and a
funnel that survives nothing would both score perfectly on the negative controls alone.
"""

from __future__ import annotations

import pytest

from cdfc.surface.funnel import (
    FUNNEL_STAGES,
    NOT_APPLICABLE,
    FunnelStage,
    ObligationCoverage,
    RejectionRow,
    StageArithmeticDoesNotClose,
    UnpairedObligationCount,
    attrition_funnel,
)
from cdfc.surface.history import HistoryPoint, UnlabelledStepDown, history_points, render_series
from cdfc.surface.library import (
    SAME_AUTHOR_LABEL,
    FfrCell,
    IndeterminateNotNamed,
    KillRateCell,
    LibraryRow,
    UnpairedKillRate,
    instrument_label,
    render_corpus_header,
)


def _kr(K=80, O=100, U=10, I=0, cells=(), label=SAME_AUTHOR_LABEL) -> KillRateCell:
    return KillRateCell(G=O + U + I, U=U, I=I, O=O, R=O, K=K,
                        per_fault_class={"F01": (K, O)}, indeterminate_cells=cells,
                        instrument_label=label)


# --- (a) two kill rates ------------------------------------------------------------------


def test_library__both_kill_rates_render_or_neither_does() -> None:
    with pytest.raises(UnpairedKillRate):
        LibraryRow("P1", 1, "q", None, "x > 0", ("F01",), _kr(), None, FfrCell("uninformative",
                   False), None, _kr(), "ACTIVE")


def test_library__a_row_with_both_kill_rates_renders() -> None:
    """The admission-side twin: the lawful row still builds."""
    row = LibraryRow("P1", 1, "q", None, "x > 0", ("F01",), _kr(K=97, O=100),
                     _kr(K=21, O=100), FfrCell("uninformative", False), "ADVISORY", _kr(),
                     "ACTIVE")
    assert row.kr_claimed.rate == (97, 100)
    assert row.kr_all_classes.rate == (21, 100)
    # The gap is the number a reviewer wants, and both are readable from the row.
    assert row.kr_claimed.rate[0] - row.kr_all_classes.rate[0] == 76


# --- (b) six integers, and I is named ----------------------------------------------------


def test_library__kr_renders_six_integers_and_the_vector() -> None:
    k = _kr(I=5, cells=("Sheet1!B12", "Sheet1!B13"))
    assert (k.G, k.U, k.I, k.O, k.R, k.K) == (115, 10, 5, 100, 100, 80)
    assert k.per_fault_class
    assert k.unobservable_fraction == (10, 115)


def test_library__indeterminate_cells_are_named() -> None:
    """An integer without the cells behind it is an apology, not a measurement."""
    with pytest.raises(IndeterminateNotNamed):
        _kr(I=5, cells=())


def test_library__the_census_must_close() -> None:
    with pytest.raises(ValueError, match="G-U-I"):
        KillRateCell(G=100, U=10, I=0, O=95, R=90, K=80, per_fault_class={},
                     indeterminate_cells=(), instrument_label=None)


# --- (c) the instrument label -------------------------------------------------------------


def test_library__instrument_label_is_read_from_gates_md_not_a_constant(tmp_path) -> None:
    p = tmp_path / "GATES.md"
    p.write_text("| 1 | shell | G-EVAL — PASSED — NOT INDEPENDENT | P3 | P3 | x | LIVE |")
    assert instrument_label(p) == SAME_AUTHOR_LABEL
    p.write_text("| 1 | shell | G-EVAL — PASSED | P3 | P3 | x | LIVE |")
    # `None` is "the registry does not say", NOT "independent".
    assert instrument_label(p) is None


def test_library__flag_everything_column_is_present_on_every_row() -> None:
    """Without it a kill rate is REACH, not quality."""
    with pytest.raises(ValueError, match="flag-everything"):
        LibraryRow("P1", 1, "q", None, "x > 0", ("F01",), _kr(), _kr(),
                   FfrCell("uninformative", False), None, None, "ACTIVE")


# --- the three G-CORPUS outcomes ----------------------------------------------------------


def test_library__three_corpus_outcomes_render_distinctly() -> None:
    """Only the first two contain a digit. A RESTRICTED pass rendered as a PASS is the failure."""
    census = {"n": 40, "n_non_synthetic": 0, "n_blind_or_real": 0, "SELF-AUTHORED": 0}
    outs = {o: render_corpus_header(o, census) for o in ("PASS", "RESTRICTED", "FAIL")}
    assert len(set(outs.values())) == 3
    assert "G-CORPUS: RESTRICTED" in outs["RESTRICTED"]
    assert not any(ch.isdigit() for ch in outs["FAIL"].split("census —")[0])
    assert "RESTRICTED" not in outs["PASS"]


# --- the funnel ---------------------------------------------------------------------------


def test_funnel__stages_are_the_gate_order() -> None:
    assert FUNNEL_STAGES[0] == "generated"
    assert FUNNEL_STAGES.index("G0.scope") < FUNNEL_STAGES.index("G1.binds")
    assert FUNNEL_STAGES.index("G2.kill") < FUNNEL_STAGES.index("G4.ffr")


def test_funnel__stage_arithmetic_closes() -> None:
    with pytest.raises(StageArithmeticDoesNotClose):
        FunnelStage("G0.scope", entered=280, skipped=0, survived=280,
                    rejections=(RejectionRow("c1", "G0", "quote_not_located", 3),))


def test_funnel__a_wholly_skipped_stage_does_not_render_as_a_pass() -> None:
    """G0 over the 280 clause-less harvested candidates is the live instance."""
    s = FunnelStage("G0.scope", entered=280, skipped=280, survived=0, rejections=())
    assert s.wholly_skipped
    assert NOT_APPLICABLE in s.render()
    assert "survived 280" not in s.render()


def test_funnel__a_real_stage_renders_its_three_integers() -> None:
    """Admission-side twin: a stage that DID evaluate renders as one."""
    s = FunnelStage("G3.proof", entered=280, skipped=0, survived=275,
                    rejections=tuple(RejectionRow(f"ALR_{i}", "G3", ">= -1e17 over 1,428 cells",
                                                  1428) for i in range(5)))
    assert "skipped 0" in s.render() and "survived 275" in s.render()
    assert NOT_APPLICABLE not in s.render()


def test_funnel__every_rejection_carries_its_measured_number() -> None:
    with pytest.raises(ValueError, match="no measured number"):
        RejectionRow("c1", "G3", "   ", 10)


def test_funnel__both_obligation_counts_render_or_neither_does() -> None:
    with pytest.raises(UnpairedObligationCount):
        ObligationCoverage(with_statute_obligation=0, with_template_obligation=None, total=280)


def test_funnel__publishing_a_zero_is_the_honest_case() -> None:
    """`0 / 280` renders as one, BESIDE the template count, never instead of it."""
    c = ObligationCoverage(0, 280, 280)
    r = c.render()
    assert "0 / 280" in r and "280 / 280" in r
    assert "no harvested predicate yet implements a statutory clause" in r


def test_funnel__attrition_funnel_rejects_out_of_order_stages() -> None:
    a = FunnelStage("G1.binds", 10, 0, 10, ())
    b = FunnelStage("G0.scope", 10, 0, 10, ())
    with pytest.raises(ValueError, match="gate order"):
        attrition_funnel((a, b))
    assert attrition_funnel((b, a)) == (b, a)


# --- the history chart ---------------------------------------------------------------------


def test_history__can_step_down() -> None:
    """**The step-downs are the most credible thing on the chart.**"""
    pts = (
        HistoryPoint("2026-01-01", 1898, 3747, "PRE-GATE"),
        HistoryPoint("2026-02-01", 1600, 3747, "PRE-GATE",
                     cause="template hash bumped; 298 predicates moved to PROVISIONAL"),
    )
    assert history_points(pts) == pts
    assert "▼" in render_series(pts)


def test_history__step_down_without_a_cause_raises() -> None:
    with pytest.raises(UnlabelledStepDown):
        history_points((
            HistoryPoint("2026-01-01", 1898, 3747, "PRE-GATE"),
            HistoryPoint("2026-02-01", 1600, 3747, "PRE-GATE"),
        ))


def test_history__monotone_series_renders_unchanged() -> None:
    """The positive control: a rising series needs no cause and is not altered."""
    pts = (
        HistoryPoint("2026-01-01", 1000, 3747, "PRE-GATE"),
        HistoryPoint("2026-02-01", 1898, 3747, "PRE-GATE"),
    )
    assert history_points(pts) == pts
    assert "▼" not in render_series(pts)


def test_history__a_numerator_cannot_exceed_its_denominator() -> None:
    with pytest.raises(ValueError, match="exceeds the field surface"):
        HistoryPoint("2026-01-01", 4000, 3747, "PRE-GATE")
