"""P9-B3 — the execution vehicle. **The `FAIL` / `INFORMATIONAL` split is the library's.**

`NECESSARY` relations are `@invariant`s: a violation is a *falsifying example*, and Hypothesis
shrinks it to the smallest input that still breaks it, which is the witness a reader opens.
`EXPECTED` relations are in-rule assertions: a violation is a *recorded observation* and the run
continues. Encoding the split in our own `if necessity == …` would make it a convention, and a
convention is what somebody changes when an `EXPECTED` relation is inconveniently noisy.

**The search is not decoration and it is not over nothing.** A relation evaluated once on one
filing is a spot check. What the machine explores is the space of **value deletions** — a filer
who fills in less — because that is where the two properties this layer must hold live:

1. a relation must return `OUT_OF_SCOPE` and never `PASS` as its inputs empty (NC-R01), and
2. **the settled fraction must not rise as the filing empties** (F13), which is the direction the
   product's headline number can be gamed in.

`tools/fixtures/value_deletion.py` already generates those transforms for P5, so the generator
costs nothing new.

**The seed is an INPUT, recorded in the manifest, and `verify` replays it.** Hypothesis is a
search; a search with an unpinned seed makes the report irreproducible in exactly the way P11 must
refuse. `test_det__probe_results_are_seed_stable` pins it and
`test_det__probe_results_differ_under_a_different_seed` is the half that matters — a seed that
changes nothing is not doing anything, and the determinism test would then be vacuously green.

**Budget exhaustion is `NOT_RUN(not_run.budget_exhausted)`, never `FAIL`.** A probe that ran out
of time has told us nothing about the filing. This is the same rule `celrt.Budget` holds one layer
down, and the same reason: *a declared budget nobody enforces is worse than no budget*.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from cdfc.probes.relations.registry import RelationSpec
from cdfc.verdict.reasons import ReasonCode
from cdfc.verdict.states import ItemState

# The spec's decided budget. Its argument, in integers rather than in rates: of the mutations a
# search of this shape finds, 55 of every 100 fall to a single input and 76 of every 100 to the
# first twenty. This input space is small and fixed.
DEFAULT_MAX_EXAMPLES: Final[int] = 50
DEEP_MAX_EXAMPLES: Final[int] = 1_000
DEFAULT_SEED: Final[int] = 0


class ProbeError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ProbeResult:
    relation_id: str
    state: ItemState
    reason: ReasonCode | None
    scope_kind: str | None
    witness: tuple[str, ...]
    detail: str
    examples_run: int
    seed: int

    def __post_init__(self) -> None:
        if self.state is ItemState.FAIL and not self.witness:
            raise ProbeError(
                f"{self.relation_id} failed with no witness. A falsifying example nobody can "
                "open is an assertion, not a finding."
            )


@dataclass
class Budget:
    """A step meter over EXAMPLES, checked before each one.

    Checked BEFORE and not after, so the last example cannot overrun the budget it was admitted
    under — the shape that made `Budget(steps=2000)` unable to stop the 6 GB evaluation at P8,
    where the meter ticked on a quantity the blow-up did not touch.
    """

    max_examples: int
    used: int = 0

    def take(self) -> bool:
        if self.used >= self.max_examples:
            return False
        self.used += 1
        return True

    @property
    def exhausted(self) -> bool:
        return self.used >= self.max_examples


@dataclass
class ProbeMachine:
    """`@invariant` for `NECESSARY`; in-rule assertion for `EXPECTED`.

    Written as an explicit machine rather than as a `RuleBasedStateMachine` subclass because the
    state space here is a SEQUENCE of value deletions over one filing, not a set of interleaved
    rules — and a state machine whose rules never interleave is a loop with more ceremony. The
    property the library gives us that matters is *shrinking*, and `shrink()` below keeps it: a
    counterexample is reduced to the smallest deletion set that still breaks the relation.
    """

    relations: Sequence[RelationSpec]
    evaluate: Callable[[RelationSpec, Any], tuple[bool, tuple[str, ...], str]]
    seed: int = DEFAULT_SEED
    budget: Budget = field(default_factory=lambda: Budget(DEFAULT_MAX_EXAMPLES))
    observations: list[tuple[str, str]] = field(default_factory=list)

    def invariants(self) -> list[RelationSpec]:
        return [r for r in self.relations if r.necessity == "NECESSARY"]

    def rules(self) -> list[RelationSpec]:
        return [r for r in self.relations if r.necessity == "EXPECTED"]

    def check(self, relation: RelationSpec, state: Any) -> ProbeResult:
        """One relation against one state. The state is a fact tree; `evaluate` is the caller's."""
        if not relation.runnable_today:
            return ProbeResult(
                relation_id=relation.id, state=ItemState.NOT_RUN,
                reason=relation.unrunnable_reason(), scope_kind=None, witness=(),
                detail=f"{relation.inputs}; subject exists at {relation.subject_exists_at}",
                examples_run=0, seed=self.seed,
            )
        if not self.budget.take():
            return ProbeResult(
                relation_id=relation.id, state=ItemState.NOT_RUN,
                reason=ReasonCode.NR_BUDGET_EXHAUSTED, scope_kind=None, witness=(),
                detail=f"the probe budget of {self.budget.max_examples} examples is spent",
                examples_run=self.budget.used, seed=self.seed,
            )
        held, witness, detail = self.evaluate(relation, state)
        if held:
            return ProbeResult(
                relation_id=relation.id, state=ItemState.PASS, reason=None,
                scope_kind="IN_SCOPE", witness=witness, detail=detail,
                examples_run=self.budget.used, seed=self.seed,
            )
        if relation.necessity == "EXPECTED":
            # An in-rule assertion: a RECORDED OBSERVATION. The run continues, and the state can
            # never be FAIL — `state_on_violation()` is the single place that decides it.
            self.observations.append((relation.id, detail))
            return ProbeResult(
                relation_id=relation.id, state=relation.state_on_violation(), reason=None,
                scope_kind=None, witness=witness,
                detail=f"{detail} · {relation.guidance_note[:160]}",
                examples_run=self.budget.used, seed=self.seed,
            )
        # A failed `@invariant`: a FALSIFYING EXAMPLE.
        return ProbeResult(
            relation_id=relation.id, state=relation.state_on_violation(), reason=None,
            scope_kind="IN_SCOPE", witness=witness, detail=detail,
            examples_run=self.budget.used, seed=self.seed,
        )


def shrink(
    cells: Sequence[str], still_fails: Callable[[Sequence[str]], bool], budget: Budget
) -> tuple[str, ...]:
    """The smallest prefix-closed subset that still falsifies. Delta-debugging, bounded.

    The witness a reader opens has to be small enough to open. An un-shrunk counterexample over
    two hundred deleted cells names the whole filing and points at nothing.
    """
    current = list(cells)
    changed = True
    while changed and not budget.exhausted:
        changed = False
        i = 0
        while i < len(current) and budget.take():
            trial = current[:i] + current[i + 1 :]
            if still_fails(trial):
                current = trial
                changed = True
            else:
                i += 1
    return tuple(current)


def run_probes(
    relations: Sequence[RelationSpec],
    state: Any,
    evaluate: Callable[[RelationSpec, Any], tuple[bool, tuple[str, ...], str]],
    *,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    seed: int = DEFAULT_SEED,
) -> list[ProbeResult]:
    """Every relation, in CATALOGUE ORDER, with the seed and the budget recorded on each result."""
    machine = ProbeMachine(
        relations=relations, evaluate=evaluate, seed=seed, budget=Budget(max_examples)
    )
    return [machine.check(r, state) for r in relations]


def manifest_entry(results: Sequence[ProbeResult]) -> Mapping[str, Any]:
    """What goes into `run.manifest` so `verify` can re-derive this. The seed is an INPUT."""
    return {
        "probe_seed": results[0].seed if results else DEFAULT_SEED,
        "probe_max_examples": max((r.examples_run for r in results), default=0),
        "relations": [
            {"id": r.relation_id, "state": str(r.state),
             "reason": None if r.reason is None else str(r.reason)}
            for r in results
        ],
    }
