"""P9-B4 — a relation is a predicate, and the closure fix that reaching G4 exposed."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.importgraph import import_closure  # noqa: E402
from cdfc.predicates.envelope import Candidate  # noqa: E402
from cdfc.predicates.errors import DeclaredKeyUnread, UndeclaredKeyRead  # noqa: E402
from cdfc.probes.qualify import (  # noqa: E402
    RelationEnvelopeError,
    check_keys_both_ways,
    evaluation_import_closure,
    targeted_mutants,
    to_envelope,
)
from cdfc.probes.relations.registry import load  # noqa: E402

FME_SHA = "7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39"
GENERATOR = "cdfc.qualify.corpus._derive_foreign"


@pytest.fixture(scope="module")
def by_id():
    return {s.id: s for s in load()}


def test_pq__relation_is_a_predicate(by_id) -> None:
    """`to_envelope`'s output is a `Candidate` and loads through the SAME loader. A divergent
    code path is a second admission standard, and the second one is always the lenient one."""
    c = to_envelope(by_id["R-02"], FME_SHA)
    assert isinstance(c, Candidate)
    assert c.kind == "relation"
    assert c.template == FME_SHA
    assert c.obligation_source == "TEMPLATE"


def test_pq__schema_keys_checked_both_ways(by_id) -> None:
    """Reads-undeclared and declares-unread have DIFFERENT remedies, so they raise different
    types. Collapsing them is NC-Q42."""
    for rid in ("R-02", "R-03", "R-07"):
        check_keys_both_ways(to_envelope(by_id[rid], FME_SHA))

    import dataclasses

    c = to_envelope(by_id["R-03"], FME_SHA)
    with pytest.raises(UndeclaredKeyRead):
        check_keys_both_ways(dataclasses.replace(c, schema_keys=c.schema_keys[:2]))
    with pytest.raises(DeclaredKeyUnread):
        check_keys_both_ways(
            dataclasses.replace(c, schema_keys=(*c.schema_keys, "filing.nowhere.v"))
        )


def test_pq__claims_fault_classes_is_carried_through_to_envelope(by_id) -> None:
    c = to_envelope(by_id["R-02"], FME_SHA)
    assert c.claims_fault_classes == by_id["R-02"].claims_fault_classes
    assert c.claims_fault_classes


def test_pq__a_relation_with_an_empty_claim_set_fails_to_convert(by_id) -> None:
    """F1's consumer side. G2 scores `K/O` over the DECLARED set only, so a relation with no
    claim has no denominator."""
    import dataclasses

    with pytest.raises(RelationEnvelopeError, match="no denominator"):
        to_envelope(dataclasses.replace(by_id["R-02"], claims_fault_classes=()), FME_SHA)


def test_pq__the_flagship_is_refused_because_its_oracle_is_not_expressible(by_id) -> None:
    """**P9 does not widen a decided vocabulary to admit its own flagship.**"""
    assert by_id["R-01"].expr_language == "PYTHON"
    with pytest.raises(RelationEnvelopeError, match="ADMITTED_HOST_FNS"):
        to_envelope(by_id["R-01"], FME_SHA)


def test_pq__a_self_test_is_not_a_predicate(by_id) -> None:
    for rid in ("R-05", "R-06"):
        with pytest.raises(RelationEnvelopeError, match="not a predicate"):
            to_envelope(by_id[rid], FME_SHA)


def test_pq__the_evaluation_closure_is_now_a_function_of_the_candidate(by_id) -> None:
    """**The defect reaching G4 exposed.** `g4_ffr.evaluation_import_closure` ignores its
    argument and returns the runner's closure for everything. For a harvested predicate that is
    right; for a relation that reads the workbook it reports independence by looking at a module
    the relation does not use."""
    runner = frozenset(set(import_closure("cdfc.evaluate.runner")) | {"cdfc.evaluate.runner"})

    class _Harvested:
        id = "P-0001"
        kind = "harvested"

    assert evaluation_import_closure(_Harvested()) == runner, (
        "a harvested predicate must keep exactly the closure it had, so no P8 number moves"
    )

    class _Relation:
        id = "R-01"
        kind = "relation"

    rel = evaluation_import_closure(_Relation())
    assert rel > runner
    assert "cdfc.probes.template_diff" in rel
    assert "cdfc.ingest.reader_lxml" in rel


def test_pq__the_flagships_closure_shares_only_readers_with_the_corpus_driver() -> None:
    """Published rather than argued away: three READERS, no computing module. Under `g4_ffr`'s
    strict disjointness that is `independent=False, why="closure"`, and **the rule is not
    weakened to admit the flagship**."""
    gen = frozenset(set(import_closure(GENERATOR)) | {GENERATOR})

    class _Relation:
        id = "R-01"
        kind = "relation"

    shared = gen & evaluation_import_closure(_Relation())
    assert shared == frozenset({
        "cdfc.ingest.reader_lxml", "cdfc.ingest.xmlsafe", "cdfc.schema.stable_keys",
    })
    assert not any(m.startswith("cdfc.calc") for m in shared), (
        "a shared COMPUTING module would make the oracle and the checker the same function"
    )


def test_pq__a_cel_relations_closure_stays_disjoint_from_the_generator(by_id) -> None:
    """The admission-side control: the fix must not make everything non-independent."""
    gen = frozenset(set(import_closure(GENERATOR)) | {GENERATOR})
    for rid in ("R-02", "R-03"):
        c = to_envelope(by_id[rid], FME_SHA)
        assert gen & evaluation_import_closure(c) == frozenset()


def test_pq__targeted_mutants_carry_a_control_arm(by_id) -> None:
    """**Without the control arm a flag-everything relation scores perfectly.**"""
    sites = [f"4. Investors!AA{r}" for r in range(21, 31)] + [
        f"3. Portfolio!C{r}" for r in range(3, 43)
    ]
    out = targeted_mutants(by_id["R-02"], sites)
    assert out["targeted_n"] == 10
    assert out["control_n"] >= 1
    assert set(out["targeted"]).isdisjoint(out["control"])
    assert all(c.startswith("3. Portfolio") for c in out["control"])
