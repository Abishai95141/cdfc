"""P10-B1 — wiring the canary loop to the REAL evaluator.

`selfcheck/canary.py` takes its evaluator as three injected callables and imports none of the
evaluation stack. That is not tidiness: `g4_ffr.independent()` decides whether a corpus is an
admissible oracle for a predicate by intersecting import closures, so a module that drags in what
it never executes reports itself less independent than it is, and a closure used as evidence has to
be the truth. This module is the one place the two sides meet, and it lives in `evaluate/`, which
already owns the runner.

**The self-test goes through the same `CelRuntime` as every other check**, and that is the half
that makes death **D4** catchable. A stubbed loop, a stubbed runtime or a short-circuited evaluator
all report `P-SELFTEST-0001` as having fired, `selftest_silent` goes false, and the disposition
withholds the verdict.

**It does NOT go through `evaluate_one`.** `evaluate_one` computes `cells_bound` at order 4 and
raises `invalid.cells_bound_zero` when the set is empty — which a self-test's is, by construction,
since it declares no footprint. Routing it through would put a second `invalid` cause on **every**
run and make §P10·L.2.1's cause-isolation assertion (*the cause set is exactly `{canary_silent}`*)
unsatisfiable. So it takes the runtime directly, on the same activation, and
`test_st__the_selftest_runs_on_the_same_runtime_as_every_other_check` asserts the object identity.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cdfc.evaluate.celrt import CelRuntime, Outcome
from cdfc.evaluate.runner import bind_count, evaluate_one
from cdfc.selfcheck.canary import CanaryReport, RunDisposition, disposition, run_canaries
from cdfc.selfcheck.selftest import P_SELFTEST_DEAD, SelfTestPredicate
from cdfc.selfcheck.thresholds import MAX_WITNESSES
from cdfc.selfcheck.witness import FaultWitness, FilingImage, image_of, witnesses_from_campaign
from cdfc.verdict import ItemState


@dataclass(frozen=True, slots=True)
class LivenessInputs:
    """Everything the loop needs, assembled once per run before it starts."""

    image: FilingImage
    predicates: Sequence[Any]
    witnesses: Mapping[str, Sequence[FaultWitness]]
    passcase_facts: Any
    schema: Any
    rt: CelRuntime
    max_witnesses: int = MAX_WITNESSES


def state_on(p: Any, facts: Any, *, schema: Any, rt: CelRuntime) -> str:
    """The P5 item state this predicate returns on these facts. **Not a bool.**

    `FAIL` is the verdict model's own word for a kill — not "did it raise", not "did it print"; P5
    exists because the v0 harness approximated it with a print statement.

    But returning `state is FAIL` as a bool is what merged `PASS` with `NOT_RUN`, and those are
    opposite findings: `PASS` means the check ran and missed its own fault (death D1), `NOT_RUN`
    means it could not be asked at all. The loop needs all three, so it gets the state.
    """
    return str(evaluate_one(p, facts=facts, schema=schema, rt=rt).state)


def selftest_fired(st: SelfTestPredicate, facts: Any, *, rt: CelRuntime) -> bool:
    """`true` evaluated on this filing's activation. **Anything but `True` is a fire.**

    A runtime that errors, budgets out, or returns a non-boolean has not shown the self-test
    staying silent — it has shown the runtime failing, and reading that as health is the failure
    this layer exists to catch, one level up.
    """
    try:
        prog = rt.compile(st.expr, slot="expr")  # type: ignore[arg-type]
    except Exception:  # noqa: BLE001 — a compile failure IS the loop failing, and it is recorded
        return True
    res = rt.evaluate(prog, filing=facts.view("filing"), template=facts.view("template"))
    return not (res.outcome is Outcome.OK and res.value is True)


def read_set_of(p: Any, *, schema: Any) -> frozenset[str]:
    """The cells the predicate binds, as `Sheet!Ref`. Computed by the SAME function the run uses.

    A second implementation of "what does this predicate read" is a second answer, and
    `WITNESS_MISSES_READ_SET` would then be a statement about which copy was consulted.
    """
    return frozenset(bind_count(p, schema))


def run(inputs: LivenessInputs) -> tuple[CanaryReport, RunDisposition]:
    report = run_canaries(
        inputs.image,
        inputs.predicates,
        inputs.witnesses,
        evaluate=lambda p, facts: state_on(p, facts, schema=inputs.schema, rt=inputs.rt),
        read_set_of=lambda p: read_set_of(p, schema=inputs.schema),
        evaluate_selftest=lambda st, facts: selftest_fired(st, facts, rt=inputs.rt),
        passcase_facts=inputs.passcase_facts,
        selftest=P_SELFTEST_DEAD,
    )
    return report, disposition(report)


def inputs_for(
    filing: Path,
    template: Path,
    *,
    predicates: Sequence[Any],
    schema: Any,
    rt: CelRuntime,
    passcase: Path,
    killed_rows: Sequence[Mapping[str, Any]],
    facts: Any = None,
    passcase_facts: Any = None,
    max_witnesses: int = MAX_WITNESSES,
) -> LivenessInputs:
    """Assemble the loop's inputs. **The two file opens both happen here, before the loop.**"""
    from cdfc.facts.build import fact_set_for

    image = image_of(filing, template, facts=facts)
    harvest = witnesses_from_campaign(
        killed_rows,
        key_of=image.key_of,
        claims={p.id: p.claims_fault_classes for p in predicates},
        max_witnesses=max_witnesses,
    )
    return LivenessInputs(
        image=image,
        predicates=list(predicates),
        witnesses=harvest.by_predicate,
        passcase_facts=passcase_facts if passcase_facts is not None else fact_set_for(passcase, template),
        schema=schema,
        rt=rt,
        max_witnesses=max_witnesses,
    )
