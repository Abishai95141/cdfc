"""P5-B3 — the two vocabularies, their counts, and the whole of the removal policy.

The counts are pinned in four other documents. They do not move here, and D-P5-05 records that
moving one was proposed (a 31st reason code for the degenerate-precondition case) and refused
under arbitration C3 — a field on the existing code carried the distinction.
"""

from __future__ import annotations

import ast
import itertools
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.relations import SCOPE_KINDS  # noqa: E402
from cdfc.verdict import (  # noqa: E402
    FAMILIES,
    FAMILY,
    ITEM_STATE_COUNT,
    NO_REASON_STATES,
    PRECEDENCE,
    REASON_COUNT,
    REMOVAL_BASIS,
    InvalidCause,
    ItemState,
    MissingScopeKindError,
    ReasonCode,
    ReasonDisciplineError,
    RemovalBasis,
    by_family,
    in_scope,
    rank,
    reason_required,
    requalification_flag,
    validate_pair,
)

STATES = tuple(ItemState)
REASONS_AND_NONE: tuple[ReasonCode | None, ...] = (*tuple(ReasonCode), None)
SCOPES: tuple[str | None, ...] = (*sorted(SCOPE_KINDS), None)


# --- the counts ---------------------------------------------------------------------------


def test_contract__eight_item_states() -> None:
    assert len(STATES) == ITEM_STATE_COUNT == 8


def test_contract__thirty_reason_codes() -> None:
    codes = tuple(ReasonCode)
    assert len(codes) == REASON_COUNT == 30
    assert len({c.value for c in codes}) == 30, "two codes share a string"
    for c in codes:
        assert "." in c.value, f"{c.value!r} is not namespaced"
    counts = {f: len(v) for f, v in by_family().items()}
    assert counts == {
        "no_predicate": 8, "not_run": 10, "indeterminate": 4, "out_of_scope": 3, "error": 5
    }
    assert sum(counts.values()) == 30
    assert len(FAMILIES) == 5


def test_contract__there_is_no_thirty_first_code_for_the_degenerate_precondition() -> None:
    """C3. The distinction survives — carried by `scope_kind`, not by a code."""
    assert not any("precondition" in c.value for c in ReasonCode)
    assert "PREDICATE_PRECONDITION" in SCOPE_KINDS


def test_contract__eight_invalid_causes() -> None:
    assert len(tuple(InvalidCause)) == 8


def test_contract__invalid_causes_and_reason_codes_are_disjoint() -> None:
    """No shared member and no shared STRING. A run-level cause in an item's reason field would
    lose either the location or the run-level consequence."""
    item = {c.value for c in ReasonCode}
    run = {c.value for c in InvalidCause}
    assert item & run == set()
    assert all(v.startswith("invalid.") for v in run)
    assert not any(v.startswith("invalid.") for v in item)


# --- precedence ---------------------------------------------------------------------------


def test_contract__precedence_has_seven_members_and_excludes_no_predicate() -> None:
    assert len(PRECEDENCE) == 7
    assert ItemState.NO_PREDICATE not in PRECEDENCE
    assert len(set(PRECEDENCE)) == 7
    assert set(PRECEDENCE) | {ItemState.NO_PREDICATE} == set(STATES)
    with pytest.raises(KeyError, match="EMPTY"):
        rank(ItemState.NO_PREDICATE)


def test_contract__a_check_that_did_not_run_is_never_absorbed_by_one_that_did() -> None:
    """The audit's resolution, as one line. `PASS ≻ NOT_RUN` was withdrawn for this case."""
    assert rank(ItemState.NOT_RUN) < rank(ItemState.PASS)
    assert rank(ItemState.ERROR) < rank(ItemState.FAIL) < rank(ItemState.NOT_RUN)
    assert rank(ItemState.OUT_OF_SCOPE) == len(PRECEDENCE) - 1


# --- the discipline rule, exhaustively ------------------------------------------------------


def test_contract__reason_code_required_iff_state_not_pass_fail_or_informational() -> None:
    """Exhaustive over the 8 x 31 product. Every pair either validates or raises; no third outcome.

    The `INFORMATIONAL` row asserts `reason is None and informational_note is not None` (D-P5-02).
    """
    accepted, refused = 0, 0
    for state, reason in itertools.product(STATES, REASONS_AND_NONE):
        note = "a template defect" if state is ItemState.INFORMATIONAL else None
        try:
            validate_pair(state, reason, note)
            accepted += 1
            if reason_required(state):
                assert reason is not None and FAMILY[reason] is state
            else:
                assert reason is None
                assert (note is not None) is (state is ItemState.INFORMATIONAL)
        except ReasonDisciplineError:
            refused += 1
    assert accepted + refused == len(STATES) * len(REASONS_AND_NONE) == 8 * 31
    # One accepted pair per state: its own reasons, or `None` for the three that carry none.
    assert accepted == REASON_COUNT + len(NO_REASON_STATES)
    assert refused == 8 * 31 - accepted


def test_contract__informational_without_a_note_is_refused() -> None:
    with pytest.raises(ReasonDisciplineError, match="informational_note"):
        validate_pair(ItemState.INFORMATIONAL, None, None)


# --- the removal policy ----------------------------------------------------------------------


def test_contract__removal_basis_is_total_and_closed() -> None:
    """Every key is a legal pair; `in_scope` is total over 8 x 31 x |ScopeKind ∪ {None}|."""
    for (state, reason), basis in REMOVAL_BASIS.items():
        assert state in STATES
        assert reason is None or FAMILY[reason] is state
        assert isinstance(basis, RemovalBasis)

    seen_true = seen_false = raised = 0
    for state, reason, scope in itertools.product(STATES, REASONS_AND_NONE, SCOPES):
        try:
            (seen_true := seen_true + 1) if in_scope(state, reason, scope) else (
                seen_false := seen_false + 1
            )
        except MissingScopeKindError:
            raised += 1
            assert (state, reason) == (ItemState.OUT_OF_SCOPE, ReasonCode.OOS_NOT_APPLICABLE)
            assert scope is None
    assert seen_true + seen_false + raised == 8 * 31 * 4
    assert raised == 1, "exactly one (state, reason, scope) triple may fail closed"
    assert seen_false > 0 and seen_true > 0, "a total function that never removes, or always does"


def test_contract__the_retention_rule_is_asserted_directly() -> None:
    pair = (ItemState.OUT_OF_SCOPE, ReasonCode.OOS_NOT_APPLICABLE)
    assert in_scope(*pair, "PREDICATE_PRECONDITION") is True, "a degenerate precondition is RETAINED"
    assert in_scope(*pair, "DECLARED_CHARACTERISTIC") is False, "and only this one leaves"
    assert in_scope(*pair, "IN_SCOPE") is True
    with pytest.raises(MissingScopeKindError):
        in_scope(*pair, None)


def test_contract__a_pair_absent_from_the_table_stays_in_scope() -> None:
    """The default is to COUNT. `noPredicate` staying in the denominator is the load-bearing case:
    ours is induced from the regulator's own template, so *no predicate exists* is a gap in US."""
    for state, reason in itertools.product(STATES, REASONS_AND_NONE):
        if (state, reason) in REMOVAL_BASIS:
            continue
        scope = "IN_SCOPE" if state is ItemState.OUT_OF_SCOPE else None
        assert in_scope(state, reason, scope) is True
    assert in_scope(ItemState.NO_PREDICATE, ReasonCode.NP_NOT_YET_SYNTHESISED) is True
    assert in_scope(ItemState.NOT_RUN, ReasonCode.NR_EXTRACTOR_DISAGREEMENT) is True


def test_contract__requalification_flag_fires_only_on_the_retained_kind() -> None:
    """Being counted is not the punishment; being re-qualified is."""
    assert requalification_flag("PREDICATE_PRECONDITION") is True
    assert requalification_flag("DECLARED_CHARACTERISTIC") is False
    assert requalification_flag("IN_SCOPE") is False
    assert requalification_flag(None) is False


def test_contract__scope_kind_is_read_not_ignored() -> None:
    """An AST scan. A field one document writes and another ignores is the defect C3 exists to
    close, and it is invisible to every behavioural test that never builds such a record.

    The rule enforced: any module that decides denominator membership must reach `scope_kind` —
    which in practice means calling `in_scope`, the only function that takes it.
    """
    targets = [
        REPO / "src" / "cdfc" / "verdict" / "closure.py",
        REPO / "src" / "cdfc" / "verdict" / "settled_fraction.py",
    ]
    for path in targets:
        assert path.is_file(), f"{path.name} does not exist; the scan would pass vacuously"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = {
            n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "")
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
        }
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
            n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
        }
        assert "in_scope" in calls or "scope_kind" in names, (
            f"{path.name} decides denominator membership without reaching scope_kind. A build "
            "that subtracts all OUT_OF_SCOPE fails this and the fraction-does-not-rise property."
        )


def test_contract__only_in_scope_removes_a_cell_from_the_denominator() -> None:
    """A second removal path is a defect no test of the table can see. This looks for one.

    The rule: in `closure.py`, any subtraction touching a BUCKET COUNT must be one of the two
    published `- *Retained` terms. A subtraction that reduces a bucket by anything else is a
    removal decision made outside `in_scope()`.
    """
    from cdfc.verdict.closure import TERMS

    source = (REPO / "src" / "cdfc" / "verdict" / "closure.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    offenders = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub)):
            continue
        seg = ast.get_source_segment(source, node) or ""
        if not any(term in seg for term in (*TERMS, "cellsTotal", "in_scope")):
            continue                       # not about the denominator at all
        if "Retained" not in seg:
            offenders.append(seg)
    assert offenders == [], (
        f"a subtraction over a bucket count that is not a published *Retained term: {offenders}"
    )


def test_contract__the_scan_above_can_see_an_extra_removal_when_there_is_one() -> None:
    """The admission-side control: a scan that matches nothing is not a guard."""
    from cdfc.verdict.closure import TERMS

    injected = "return self.cellsTotal - self.outOfScope - self.notRun"
    tree = ast.parse(injected.replace("return ", "x = "))
    found = [
        ast.get_source_segment(injected.replace("return ", "x = "), n)
        for n in ast.walk(tree)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub)
    ]
    hits = [s for s in found if s and any(t in s for t in TERMS) and "Retained" not in s]
    assert hits, "the scan would not have caught a hand-written second removal"
