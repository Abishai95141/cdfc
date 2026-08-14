"""P9-B4 — **a relation is a predicate.** The adapter, and the one thing it must not be.

A relation passes G0 → G1 → G3ᵖ → G2 → G3ᵉ → G4 in that order, is stored in the same registry,
carries the same `qualification` block, and **may not settle a single cell until it does**. The
whole value of this build is that `to_envelope`'s output goes through **the same loader** as a
harvested predicate: a divergent code path is a second admission standard, and the second one is
always the lenient one because it was written by whoever wanted the relation admitted.

**`schema_keys` is machine-checked against the CEL AST BOTH WAYS**, by P4-B2's own walker and with
its own two distinct exceptions — reads-undeclared and declares-unread have different remedies and
collapsing them is NC-Q42.

**`claims_fault_classes` is carried through, and an empty claim set fails to convert** (F1). The
claim is the denominator of the relation's own quality score, and a denominator chosen after the
campaign is not a denominator.

---

**A DEFECT THIS BUILD FIXES IN `g4_ffr`, and it is the reason relations had to reach G4 to find
it.** `g4_ffr.evaluation_import_closure(cand)` ignores `cand` entirely and returns the closure of
`cdfc.evaluate.runner` for every candidate. For a harvested predicate that is right — the runner
evaluates CEL over an already-built fact table and never touches the XML reader, so its closure is
genuinely disjoint from a corpus generator's. **For a relation whose evaluation reads the workbook
it is wrong in the direction that flatters us**: it would report independence by looking at a
module the relation does not use. `RELATION_EVALUATOR_MODULES` below declares what a relation's
evaluation actually reaches, and the fix is strictly stricter — harvested predicates keep exactly
the closure they had, so no published P8 number moves.

**What the honest closure then says about `TEMPLATE_DIFF`, published rather than argued away:**
its evaluation shares `cdfc.ingest.reader_lxml`, `cdfc.ingest.xmlsafe` and
`cdfc.schema.stable_keys` with the FOREIGN_ENGINE corpus driver — three READERS, no computing
module. Under `g4_ffr`'s strict disjointness that is `independent=False, why="closure"`, and **the
rule is not weakened to admit the flagship.** A shared reader is a real correlated-failure path,
even if a weaker one than a shared evaluator, and P1's two-reader differential (1,691 of 1,729
units corroborated externally) is the compensating control that exists for it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

from cdfc.predicates.envelope import Candidate
from cdfc.probes.relations.registry import RelationSpec

# What a relation's evaluation ACTUALLY reaches. Declared per relation-id prefix rather than
# globally: R-01 reads the workbook, R-02 and R-03 are CEL over the fact tree like any harvested
# predicate, and R-05/R-06 are Python over our own record.
RELATION_EVALUATOR_MODULES: Final[Mapping[str, str]] = {
    "R-01": "cdfc.probes.template_diff",
    "R-05": "cdfc.probes.relations.selftest",
    "R-06": "cdfc.probes.relations.selftest",
}

# A relation's obligation is the template construct that licenses it, in the same id space the
# harvest uses so the foreign key stays injective across both sources.
OBLIGATION_PREFIX: Final[str] = "OBL-TEMPLATE-R-"


class RelationEnvelopeError(TypeError):
    """A relation that cannot become a predicate. Never silently skipped."""


def _keys_of(spec: RelationSpec) -> tuple[str, ...]:
    """The declared key set, from the relation's own builder where it has one."""
    if spec.builder:
        module, _, _fn = spec.builder.partition(":")
        import importlib

        mod = importlib.import_module(module)
        if hasattr(mod, "schema_keys"):
            return tuple(mod.schema_keys())
    from cdfc.predicates.ast_walker import all_read_keys

    class _Shim:
        applicable = spec.precondition
        expr = spec.expr
        witness = spec.witness

    return tuple(sorted(all_read_keys(_Shim())))


def to_envelope(spec: RelationSpec, template_sha256: str) -> Candidate:
    """`RelationSpec` → the P4 envelope, `kind="relation"`.

    Raises rather than returning `None`: a relation that cannot be converted must not be counted
    as one that was, and the funnel's `generated` figure is read from this call's success.
    """
    if not spec.claims_fault_classes:
        raise RelationEnvelopeError(
            f"{spec.id}: an empty `claims_fault_classes` cannot convert. G2 scores `K/O` over the "
            "DECLARED set only, so a relation with no claim has no denominator (F1)."
        )
    if spec.inputs == "SELF_TEST":
        raise RelationEnvelopeError(
            f"{spec.id}: a SELF_TEST relation is not a predicate. Its subject is the run's own "
            "record, not a cell of the filing, so it settles nothing and there is nothing for the "
            "five gates to qualify. It runs, and it is reported to us."
        )
    if spec.expr_language != "CEL":
        # **THE FLAGSHIP IS HERE, AND THE REFUSAL IS THE FINDING.** `TEMPLATE_DIFF`'s oracle is
        # the pinned blank's FORMULA GRAPH, recomputed by `cdfc.calc` over the filed inputs. The
        # admitted CEL subset cannot express that and was designed not to: every construct it
        # bans is banned because it defeats static key recovery, defeats termination, or moves a
        # check somewhere nobody qualified it, and a formula-graph recomputation is the first of
        # those. The envelope's `schema_keys` are recovered from the expression's AST, so an
        # expression the walker cannot parse has no declarable read set.
        #
        # The route the design provides is a HOST FUNCTION — that is what `gstin_valid` and
        # `nav_interval` are. Taking it means adding a member to `ADMITTED_HOST_FNS`, which is a
        # decided vocabulary, in order to admit the relation whose author wants it admitted.
        # **P9 does not widen a vocabulary to fit its own flagship**; it records that the flagship
        # cannot be routed through the CEL envelope and publishes the consequence in
        # `docs/measurements/P9-relation-attrition.md`.
        raise RelationEnvelopeError(
            f"{spec.id}: its expression is {spec.expr_language}, not CEL. The admitted subset "
            "cannot express a recomputation of the template's formula graph, and the envelope's "
            "schema_keys are recovered from the expression's AST — so there is no read set to "
            "declare. Admitting it needs a new member of ADMITTED_HOST_FNS, which is a decided "
            "vocabulary; widening it here would widen it for every predicate."
        )

    keys = _keys_of(spec)
    if not keys:
        raise RelationEnvelopeError(
            f"{spec.id}: no schema keys could be derived from its expression. A predicate that "
            "declares no key binds no cell, which is `error.cells_bound_zero` one step earlier."
        )

    return Candidate(
        id=spec.id,
        version=1,
        kind="relation",
        template=template_sha256,
        schema_keys=keys,
        host_fns=(),
        obligation_id=f"{OBLIGATION_PREFIX}{spec.id}",
        obligation_source="TEMPLATE",
        clause=None,
        rationale=spec.evidence,
        clause_absent_reason="derived_from_template_formula",
        claims_fault_classes=spec.claims_fault_classes,
        applicable=spec.precondition,
        expr=spec.expr,
        witness=spec.witness,
        reason_if_inapplicable=(
            f"{spec.id}'s non-degeneracy precondition is not met on this filing"
        ),
        tolerance=None,
    )


def check_keys_both_ways(cand: Candidate) -> None:
    """P4-B2's check, on the same code path and with the same two distinct exceptions.

    Reads-undeclared and declares-unread have DIFFERENT remedies — widen the declaration, or
    delete a key nobody reads — so they raise different types. Collapsing them into one is NC-Q42.
    """
    from cdfc.predicates.ast_walker import check_declared_keys

    check_declared_keys(cand)


def evaluation_import_closure(cand: Any) -> frozenset[str]:
    """The modules a candidate's evaluation reaches — **now a function of the candidate.**

    A harvested predicate is evaluated by `cdfc.evaluate.runner` and gets exactly the closure it
    had before this build. A relation that reads the workbook gets the closure of the module that
    actually reads it, so `g4_ffr.independent()` compares the truth rather than a stand-in.
    """
    from cdfc.importgraph import import_closure
    from cdfc.qualify.g4_ffr import EVALUATOR_MODULE

    modules = {EVALUATOR_MODULE}
    extra = RELATION_EVALUATOR_MODULES.get(getattr(cand, "id", ""))
    if getattr(cand, "kind", None) == "relation" and extra:
        modules.add(extra)
    out: set[str] = set()
    for m in modules:
        out |= set(import_closure(m)) | {m}
    return frozenset(out)


def targeted_mutants(spec: RelationSpec, sites: Sequence[str], *, control_share: int = 10) -> dict:
    """G2 for a relation: mutants aimed at its read set, PLUS a control sample it does NOT read.

    **Without the control arm a flag-everything relation scores perfectly.** The share is a
    fraction of the targeted count and it is an integer ratio rather than a percentage, so the
    two populations are always reported as two integers.
    """
    read = sorted({s for s in sites if _reads(spec, s)})
    unread = sorted(set(sites) - set(read))
    n_control = max(1, len(read) // control_share) if unread else 0
    return {
        "relation_id": spec.id,
        "targeted": read,
        "control": unread[:n_control],
        "targeted_n": len(read),
        "control_n": min(n_control, len(unread)),
    }


def _reads(spec: RelationSpec, cell: str) -> bool:
    from cdfc.predicates.harvest import cel_path

    sheet, _, ref = cell.partition("!")
    if not ref:
        return False
    try:
        return f"filing.{cel_path(sheet, ref)}." in spec.expr
    except ValueError:
        return False
