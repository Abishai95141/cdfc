"""P12-B2 — the four marginal-kill rows, and the two §0.6 preconditions that fail closed.

Two of the three demolitions in this literature are demolitions by baseline. The rows exist so the
comparison against free work is *printed*, not asserted; and the preconditions exist so a row that
cannot support a comparison renders a sentence where a number would otherwise go. A number under an
inadmissible comparison is read as a result, which is why `render()` returns a string long enough
not to fit in a column somebody skims.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.marginal import (  # noqa: E402
    BASELINE_IDS,
    CORPUS_UNINFORMATIVE,
    FFR_UPPER_BOUND_EXCEEDED,
    UNION_ID,
    MarginalKill,
    beats_baselines,
    corpus_is_uninformative,
    marginal_kill,
)
from cdfc.qualify.corpus.provenance import CorpusProvenance  # noqa: E402


@dataclass(frozen=True)
class _StubCorpus:
    """The two fields `corpus_is_uninformative` reads, and nothing else.

    `computed_cells` is read off the corpus rather than recomputed, so a stub carrying the two
    attributes is the whole interface — and a stub is right here because the alternative is
    building a real filing corpus to test a two-line predicate about labels and set intersection.
    """

    provenance: CorpusProvenance
    computed_cells: frozenset[str]


def _sets(observable: set[str], candidate: set[str], b0: set[str], b1: set[str], b2: set[str]):
    return dict(
        observable=frozenset(observable),
        candidate_kills=frozenset(candidate),
        baseline_kills={"B0": frozenset(b0), "B1": frozenset(b1), "B2": frozenset(b2)},
    )


# --- the four rows -------------------------------------------------------------------------------


def test_marginal__returns_four_rows() -> None:
    """**Three baselines and the union, always** — including when a baseline killed nothing.

    NC-M07. Reporting only the union hides that one baseline already killed everything, which is
    the exact shape of the demolitions this build exists to pre-empt; and dropping a row for a
    baseline that did not run silently strengthens the candidate by removing a comparison it never
    beat. B1 not running contributes a row with `killed_by_baseline = 0`, which is the honest
    reading of "declared not-run".
    """
    for kwargs in (
        _sets({"m1", "m2", "m3"}, {"m1", "m2"}, {"m3"}, set(), {"m2"}),
        _sets({"m1", "m2", "m3"}, set(), set(), set(), set()),          # candidate killed nothing
        _sets({"m1", "m2", "m3"}, {"m1"}, {"m1", "m2", "m3"}, set(), set()),  # B0 killed all
        _sets(set(), set(), set(), set(), set()),                        # nothing observable
    ):
        rows = marginal_kill(**kwargs)
        assert len(rows) == 4
        assert tuple(r.baseline_id for r in rows) == BASELINE_IDS
        assert sum(1 for r in rows if r.baseline_id == UNION_ID) == 1


def test_marginal__a_missing_baseline_row_is_refused_not_dropped() -> None:
    """A baseline that did not run is a row of zeroes, never an absent row.

    The two are indistinguishable in a rendered table and they mean opposite things: one says the
    candidate beat a baseline that killed nothing, the other says the comparison was not made.
    """
    with pytest.raises(ValueError) as e:
        marginal_kill(
            observable=frozenset({"m1"}),
            candidate_kills=frozenset({"m1"}),
            baseline_kills={"B0": frozenset(), "B2": frozenset()},
        )
    assert "B1" in str(e.value)


def test_marginal__union_dominates_members() -> None:
    """`K_union ⊇ K_b` for every member, so the union's marginal is the SMALLEST of the four.

    This is what makes the union the honest headline: a candidate can look strong against any one
    free baseline and add nothing over all three at once. A union row whose marginal exceeded a
    member's would mean the union had been computed as something other than `B0 ∪ B1 ∪ B2` — the
    error that turns the hardest comparison into the easiest one.
    """
    for kwargs in (
        _sets({"a", "b", "c", "d"}, {"a", "b", "c"}, {"a"}, {"b"}, {"c"}),
        _sets({"a", "b", "c", "d"}, {"a", "b", "c", "d"}, set(), set(), set()),
        _sets({"a", "b", "c", "d"}, {"a"}, {"a", "b"}, {"a", "c"}, {"d"}),
        _sets({"a", "b"}, {"a", "b"}, {"a", "b"}, {"a", "b"}, {"a", "b"}),
    ):
        rows = marginal_kill(**kwargs)
        by_id = {r.baseline_id: r for r in rows}
        union = by_id[UNION_ID]
        for b in ("B0", "B1", "B2"):
            assert union.killed_by_baseline >= by_id[b].killed_by_baseline
            assert union.killed_by_candidate_only <= by_id[b].killed_by_candidate_only, (
                f"the union's marginal exceeded {b}'s; the union is not the union of the members"
            )
        assert union.killed_by_candidate == by_id["B0"].killed_by_candidate


# --- §0.6, both preconditions fail closed --------------------------------------------------------


def test_marginal__incomparable_renders_a_string_not_a_number() -> None:
    """**A sentence where the number would go, and `None` in the JSON.**

    A number printed under an inadmissible comparison is read as a result by everyone who did not
    read the footnote. `as_obj()["killed_by_candidate_only"]` is `None` rather than the computed
    integer for the same reason: a downstream consumer summing that column must fail, not quietly
    total an inadmissible figure into a headline.
    """
    rows = marginal_kill(
        **_sets({"m1", "m2", "m3"}, {"m1", "m2"}, {"m3"}, set(), {"m2"}),
        incomparable_reason=FFR_UPPER_BOUND_EXCEEDED,
    )
    for row in rows:
        assert row.comparable is False
        assert row.render() == f"NOT COMPARABLE — {FFR_UPPER_BOUND_EXCEEDED}"
        assert "/" not in row.render(), "a k/n fragment here would still read as a measurement"
        assert row.as_obj()["killed_by_candidate_only"] is None
        assert row.as_obj()["rendered"].startswith("NOT COMPARABLE — ")
    assert beats_baselines(rows) is False, "an inadmissible comparison cannot satisfy criterion 4"

    comparable = marginal_kill(**_sets({"m1", "m2", "m3"}, {"m1", "m2"}, {"m3"}, set(), {"m2"}))
    assert comparable[0].render() == "2/3"
    assert comparable[0].as_obj()["killed_by_candidate_only"] == 2


def test_marginal__uninformative_corpus_is_incomparable() -> None:
    """F2 — on a corpus our own `calc/` computed, both arms fire zero times whatever their quality.

    The comparability precondition would then *pass* and tell you nothing: an arithmetic candidate
    and an arithmetic baseline agree with a workbook whose values were produced by the same
    arithmetic. The detector is the intersection `read_keys & computed_cells` under a
    `TEMPLATE-COMPUTED` label — both conditions, so this is a precondition and not a knob.
    """
    read_keys = frozenset({"3. Portfolio!O7", "3. Portfolio!O8"})
    computed = _StubCorpus(CorpusProvenance.TEMPLATE_COMPUTED, frozenset({"3. Portfolio!O7"}))
    assert corpus_is_uninformative(computed, read_keys) is True

    disjoint = _StubCorpus(CorpusProvenance.TEMPLATE_COMPUTED, frozenset({"1. Cover!B2"}))
    assert corpus_is_uninformative(disjoint, read_keys) is False, (
        "a TEMPLATE-COMPUTED corpus the candidate does not read is still informative about it"
    )

    rows = marginal_kill(
        **_sets({"m1", "m2", "m3"}, {"m1", "m2", "m3"}, set(), set(), set()),
        incomparable_reason=CORPUS_UNINFORMATIVE,
    )
    assert beats_baselines(rows) is False, (
        "a clean sweep of every observable mutant must still not beat the baselines when the FFR "
        "corpus could not have distinguished the two arms"
    )
    assert all(r.render().endswith(CORPUS_UNINFORMATIVE) for r in rows)


def test_marginal__register_derived_corpus_is_comparable_for_membership_candidates() -> None:
    """The ADMISSION side of the same rule — without it, §0.6 rejects everything and measures none.

    A precondition that never admits a comparison is not fail-closed, it is closed: the experiment
    would report NOT COMPARABLE for every candidate and the four rows would carry no information
    about any model. A `REGISTER-DERIVED` corpus is not template-computed, so a membership
    candidate reading register cells is comparable against it and criterion 4 can actually be met.
    """
    read_keys = frozenset({"2. Register!C4", "2. Register!C5"})
    register = _StubCorpus(CorpusProvenance.REGISTER_DERIVED, frozenset({"3. Portfolio!O7"}))
    assert corpus_is_uninformative(register, read_keys) is False

    overlapping = _StubCorpus(CorpusProvenance.REGISTER_DERIVED, read_keys)
    assert corpus_is_uninformative(overlapping, read_keys) is False, (
        "the rule is keyed on the TEMPLATE-COMPUTED label AND the intersection; an overlap alone "
        "would make every corpus uninformative for every candidate that reads a computed cell"
    )

    rows = marginal_kill(**_sets(
        {f"m{i}" for i in range(10)}, {"m0", "m1", "m2"}, {"m3"}, {"m4"}, {"m5"},
    ))
    assert all(r.comparable for r in rows)
    assert beats_baselines(rows) is True, (
        "3 marginal kills of 10 observable, positive against each baseline, clears the 10% floor"
    )


def test_marginal__a_row_with_no_reason_cannot_be_incomparable() -> None:
    """An incomparable row with no reason renders as a blank, and a reader fills a blank in.

    They fill it in with the flattering value. The reason is the payload of the whole precondition:
    "NOT COMPARABLE" alone is indistinguishable from a missing measurement.
    """
    with pytest.raises(ValueError) as e:
        MarginalKill(
            baseline_id="B0", observable=10, killed_by_baseline=1, killed_by_candidate=3,
            killed_by_candidate_only=2, comparable=False, incomparable_reason=None,
        )
    assert "blank" in str(e.value)

    with pytest.raises(ValueError):
        MarginalKill(
            baseline_id="B0", observable=10, killed_by_baseline=1, killed_by_candidate=3,
            killed_by_candidate_only=2, comparable=False, incomparable_reason="",
        )

    with pytest.raises(ValueError) as e:
        MarginalKill(
            baseline_id="B0", observable=10, killed_by_baseline=1, killed_by_candidate=3,
            killed_by_candidate_only=2, comparable=True,
            incomparable_reason=FFR_UPPER_BOUND_EXCEEDED,
        )
    assert "comparable row carries no incomparable_reason" in str(e.value)
