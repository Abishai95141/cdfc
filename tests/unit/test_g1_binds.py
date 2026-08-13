"""P7-B2 — G1, executes and binds. All six closed reasons observed on a real candidate."""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import Budget, CelRuntime  # noqa: E402
from cdfc.facts.build import fact_set_for  # noqa: E402
from cdfc.predicates.harvest import harvest  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402
from cdfc.qualify.g1_binds import CLOSED_REASONS, REMEDY, Reason, check  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
FILING = REPO / "fixtures" / "synthetic" / "clean__independently-computed__fme-q1.xlsx"


@pytest.fixture(scope="module")
def world():
    r = harvest(FME)
    facts = fact_set_for(FILING, FME)
    hf = default_registry()
    return r, facts, hf, CelRuntime(profile_version="P7", host_fns=hf)


def _cand(r, pid: str):
    return next(c for c in r.candidates if c.id == pid)


def test_g1__the_reason_set_is_closed_and_each_reason_has_its_own_remedy():
    assert len(CLOSED_REASONS) == 6
    assert set(REMEDY) == set(CLOSED_REASONS)
    assert len(set(REMEDY.values())) == 6


def test_g1__all_348_bind_nonzero(world):
    """ADMISSION SIDE, over the whole FME harvest."""
    r, facts, hf, rt = world
    bound = {}
    for c in r.candidates:
        out = check(c, r.schema, facts, rt, hf)
        assert out.passed, f"{c.id}: {out.reason} {dict(out.measured)}"
        assert out.measured["cells_bound"] > 0
        bound[c.id] = out.measured["cells_bound"]
    assert len(bound) == 348
    # R-GOLD-2: a value assertion, not merely `> 0`. A count that agrees with a pinned count is
    # evidence about the count; this pins WHICH cells a named predicate reaches.
    assert bound["P-0041"] == 2, "P-0041's bind count moved"
    assert bound["P-0001"] == 1, "P-0001's bind count moved"
    assert sum(bound.values()) == 3530


def test_g1__zero_bind_rejected(world):
    """`g1.cells_bound_zero` — the condition whose absence produces the vacuous pass. `all([])` is
    True, so a predicate binding nothing returns a clean pass over nothing at all."""
    r, facts, hf, rt = world
    c = _cand(r, "P-0001")  # a membership predicate: it carries a template vocabulary key
    # A key that exists in the schema and binds no filing cell: a template vocabulary alone.
    vocab = next(k for k in c.schema_keys if k.startswith("template."))
    zero = dataclasses.replace(c, schema_keys=(vocab,), expr="true", witness="[]",
                               applicable="true")
    out = check(zero, r.schema, facts, rt, hf)
    assert not out.passed and out.reason == Reason.CELLS_BOUND_ZERO
    assert out.measured["cells_bound"] == 0


def test_g1__zero_bind_is_decided_before_expr_runs(world):
    """D-P5-01's ordering, at the gate. A zero-binding candidate must never reach an expression
    that would return a clean pass — so `expr_outcome` is absent from the record."""
    r, facts, hf, rt = world
    c = _cand(r, "P-0001")
    vocab = next(k for k in c.schema_keys if k.startswith("template."))
    zero = dataclasses.replace(c, schema_keys=(vocab,), expr="true", applicable="true",
                               witness="[]")
    out = check(zero, r.schema, facts, rt, hf)
    assert "expr_outcome" not in out.measured
    assert "applicable_outcome" not in out.measured


def test_g1__a_key_outside_the_schema_is_rejected(world):
    r, facts, hf, rt = world
    c = _cand(r, "P-0041")
    bad = dataclasses.replace(c, schema_keys=(*c.schema_keys, "filing.not.a.real.key"))
    out = check(bad, r.schema, facts, rt, hf)
    assert not out.passed and out.reason == Reason.KEY_NOT_IN_SCHEMA
    assert out.measured["missing_keys"] == ["filing.not.a.real.key"]


def test_g1__unresolved_key_blocks(world):
    """`g1.key_unresolved` — it BLOCKS; it never degrades to a guess.

    Paired with `NC-D04a`'s row-insertion control so the same defect is caught at induction AND at
    admission: a key that resolved to no cell would let a version bump silently rebind the
    predicate to a different row of the same table.
    """
    from cdfc.predicates.ast_walker import TemplateSchema

    r, facts, hf, rt = world
    c = _cand(r, "P-0041")
    victim = sorted(k for k in c.schema_keys if k.startswith("filing."))[0]
    holed = TemplateSchema(
        {k: (frozenset() if k == victim else r.schema.cells_for(k)) for k in r.schema.keys()},
        r.schema.template_sha256,
    )
    out = check(c, holed, facts, rt, hf)
    assert not out.passed and out.reason == Reason.KEY_UNRESOLVED
    assert out.measured["n_unresolved"] >= 1


def test_g1__a_template_vocabulary_key_is_not_unresolved(world):
    """The admission-side twin of the rule above. A `template.vocab.*` key legitimately binds no
    FILING cell — it names a vocabulary in the pinned blank — and treating it as unresolved would
    reject every membership predicate."""
    r, facts, hf, rt = world
    c = _cand(r, "P-0001")
    assert any(k.startswith("template.") for k in c.schema_keys)
    assert check(c, r.schema, facts, rt, hf).passed


def test_g1__unregistered_host_fn_rejected(world):
    """Admission rule R2: the host-function registry is CLOSED."""
    r, facts, hf, rt = world
    c = _cand(r, "P-0041")
    bad = dataclasses.replace(c, host_fns=("reg_resolves", "not_a_registered_fn"))
    out = check(bad, r.schema, facts, rt, hf)
    assert not out.passed and out.reason == Reason.HOST_FN_UNREGISTERED
    assert out.measured["unregistered"] == ["not_a_registered_fn"]


def test_g1__raise_is_a_gate_failure_not_an_item_state(world):
    """`g1.raised` is DISTINCT from the run-time `ERROR(error.predicate_raised)`.

    A candidate that raises is never admitted. A predicate that raises at run time is an apparatus
    failure on an admitted check. Same symptom; two findings; two remedies.
    """
    from cdfc.verdict.reasons import ReasonCode

    r, facts, hf, rt = world
    c = _cand(r, "P-0041")
    # A type error in CEL: comparing a string-valued cell against an integer.
    broken = dataclasses.replace(c, expr='filing.n_1_introduction.r60.cf.v == 1/0')
    out = check(broken, r.schema, facts, rt, hf)
    assert not out.passed and out.reason == Reason.RAISED
    assert out.measured["slot"] == "expr"
    assert Reason.RAISED != ReasonCode.ERR_PREDICATE_RAISED.value


def test_g1__budget_exhausted_is_its_own_reason(world):
    """A step budget that fires at admission is not a broken predicate and not a passing one."""
    r, facts, hf, _rt = world
    tiny = CelRuntime(profile_version="P7", host_fns=hf, budget=Budget(steps=1))
    out = check(_cand(r, "P-0041"), r.schema, facts, tiny, hf)
    assert not out.passed and out.reason == Reason.BUDGET_EXHAUSTED
    assert out.measured["budget"] == "steps"


def test_g1__a_passing_record_carries_both_slots_outcomes(world):
    r, facts, hf, rt = world
    out = check(_cand(r, "P-0041"), r.schema, facts, rt, hf)
    assert out.passed
    assert out.measured["applicable_outcome"] == "OK"
    assert out.measured["expr_outcome"] == "OK"
    assert out.measured["applicable_steps"] >= 0 and out.measured["expr_steps"] >= 0
