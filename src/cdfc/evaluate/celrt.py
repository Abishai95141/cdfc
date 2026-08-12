"""P4-B3 — the CEL runtime: compile once, evaluate under a budget, and never raise for a
program-level failure.

**`evaluate` returns an outcome as a VALUE.** If it raised, every call site would need a handler,
and a handler is where `except Exception: state = NOT_RUN` gets written — *a crash that looks like
a limit*, which is NC-E01. Making the three outcomes a value removes the temptation rather than
policing it.

**The two budgets are not interchangeable, and the result says which one fired.**

- The **step** budget is deterministic. The same program over the same facts consumes the same
  steps on every machine, so a `BUDGET_EXCEEDED(steps)` item can be re-derived from its own bytes.
- The **wall** budget is not. It depends on machine load, so an item killed by it is *not*
  reproducible — `CelResult.deterministic` is `False` and every surface that quotes it must say so.

A runtime that reported one `BUDGET_EXCEEDED` for both would make a non-reproducible verdict
indistinguishable from a reproducible one. The clock itself lives in `cdfc.measure.perf.deadline`,
outside the deterministic core, and this module never imports it: it takes a factory.

**Exactly two names are bound**, `filing` and `template`. A reference to a third is a compile-time
`SubsetViolation`, not an evaluation-time surprise.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from cdfc.facts.view import BudgetExceeded, FactView, Meter
from cdfc.predicates.cel_profile import Slot, check_subset, parse
from cdfc.predicates.errors import SubsetViolation
from cdfc.predicates.host_fns import HostFnRegistry, SnapshotMissing

DEFAULT_STEPS = 100_000


class Outcome(StrEnum):
    OK = "OK"
    ERROR = "ERROR"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    INPUT_UNAVAILABLE = "INPUT_UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class Budget:
    """`wall_ms` may only be set when a deadline factory is supplied.

    A declared budget nobody enforces is worse than no budget: it appears in the run record, a
    reviewer reads it as a bound, and nothing was bounded.
    """

    steps: int = DEFAULT_STEPS
    wall_ms: int | None = None

    def __post_init__(self) -> None:
        if self.steps <= 0:
            raise ValueError("a step budget of zero kills every evaluation before it starts")


@dataclass(frozen=True, slots=True)
class CelResult:
    outcome: Outcome
    value: bool | tuple[str, ...] | None
    error: str | None  # the CEL error TEXT, never an exception object
    steps: int
    budget: str | None = None  # "steps" | "wall" | None
    deterministic: bool = True

    @property
    def reproducible(self) -> bool:
        return self.deterministic


@dataclass(frozen=True, slots=True)
class CompiledProgram:
    source: str
    slot: Slot
    source_sha256: str
    runner: Any = field(repr=False, default=None)


class CelRuntime:
    def __init__(
        self,
        *,
        profile_version: str,
        host_fns: HostFnRegistry,
        budget: Budget = Budget(),
        deadline_factory: Callable[[], Callable[[], bool]] | None = None,
    ) -> None:
        if budget.wall_ms is not None and deadline_factory is None:
            raise ValueError(
                "a wall budget was declared with no deadline factory to enforce it. A budget "
                "that appears in the run record and bounds nothing is worse than none."
            )
        self.profile_version = profile_version
        self.host_fns = host_fns
        self.budget = budget
        self._deadline_factory = deadline_factory
        self._cache: dict[str, CompiledProgram] = {}

    # -- compile ------------------------------------------------------------------
    def compile(self, source: str, *, slot: Slot) -> CompiledProgram:
        """Subset-checked, then compiled. Cached by `sha256(source)` and the slot.

        Keyed on the source DIGEST rather than on object identity: two envelopes that carry the
        same expression are the same program, and a cache keyed on identity would compile it twice
        and could hold two different compilations of one string.
        """
        digest = hashlib.sha256(f"{slot}\n{source}".encode()).hexdigest()
        hit = self._cache.get(digest)
        if hit is not None:
            return hit
        check_subset(source, slot=slot, host_fns=self.host_fns.names())
        import celpy

        env = celpy.Environment()
        runner = env.program(parse(source, slot=slot), functions=self.host_fns.bindings())
        prog = CompiledProgram(source=source, slot=slot, source_sha256=digest, runner=runner)
        self._cache[digest] = prog
        return prog

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    # -- evaluate -----------------------------------------------------------------
    def evaluate(self, prog: CompiledProgram, *, filing: FactView, template: FactView) -> CelResult:
        meter = Meter(
            limit=self.budget.steps,
            deadline=self._deadline_factory() if self._deadline_factory is not None else None,
        )
        activation = {"filing": filing.bind(meter), "template": template.bind(meter)}
        try:
            raw = prog.runner.evaluate(activation)
        except BudgetExceeded as e:
            return CelResult(
                outcome=Outcome.BUDGET_EXCEEDED,
                value=None,
                error=str(e),
                steps=meter.steps,
                budget=e.kind,
                # A wall kill depends on machine load. Saying so is the difference between an
                # item a reviewer can re-open and one they cannot.
                deterministic=e.kind != "wall",
            )
        except SnapshotMissing as e:
            return CelResult(
                outcome=Outcome.INPUT_UNAVAILABLE, value=None, error=str(e), steps=meter.steps
            )
        except Exception as e:  # celpy raises CELEvalError for a program-level failure
            if _is_budget(e):
                inner = _budget_of(e)
                return CelResult(
                    outcome=Outcome.BUDGET_EXCEEDED, value=None, error=str(inner),
                    steps=meter.steps, budget=inner.kind, deterministic=inner.kind != "wall",
                )
            if _is_snapshot_missing(e):
                return CelResult(
                    outcome=Outcome.INPUT_UNAVAILABLE, value=None, error=str(e), steps=meter.steps
                )
            return CelResult(
                outcome=Outcome.ERROR, value=None, error=f"{type(e).__name__}: {e}", steps=meter.steps
            )
        return CelResult(
            outcome=Outcome.OK, value=_to_python(raw, prog.slot), error=None, steps=meter.steps
        )

    def observed_keys(self, prog: CompiledProgram, *, filing: FactView, template: FactView) -> frozenset[str]:
        """The keys actually read on this evaluation. The dynamic arm of the both-ways check."""
        meter = Meter(limit=self.budget.steps)
        activation = {"filing": filing.bind(meter), "template": template.bind(meter)}
        try:
            prog.runner.evaluate(activation)
        except Exception:  # noqa: BLE001 — the reads up to the failure are still what was read
            pass
        return frozenset(meter.reads)


def _is_budget(e: BaseException) -> bool:
    return _budget_of(e) is not None


def _budget_of(e: BaseException) -> BudgetExceeded | None:
    """celpy wraps an exception raised inside evaluation; the cause chain still carries ours."""
    seen: set[int] = set()
    cur: BaseException | None = e
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, BudgetExceeded):
            return cur
        for attr in ("__cause__", "__context__"):
            nxt = getattr(cur, attr, None)
            if isinstance(nxt, BudgetExceeded):
                return nxt
        args = getattr(cur, "args", ())
        for a in args:
            if isinstance(a, BudgetExceeded):
                return a
            if isinstance(a, type) and issubclass(a, BudgetExceeded):
                return BudgetExceeded("steps", -1, -1)
        cur = cur.__cause__ or cur.__context__
    return None


def _is_snapshot_missing(e: BaseException) -> bool:
    cur: BaseException | None = e
    seen: set[int] = set()
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, SnapshotMissing):
            return True
        for a in getattr(cur, "args", ()):
            if isinstance(a, type) and issubclass(a, SnapshotMissing):
                return True
            if isinstance(a, SnapshotMissing):
                return True
        cur = cur.__cause__ or cur.__context__
    return False


def _to_python(raw: Any, slot: Slot) -> bool | tuple[str, ...] | None:
    if slot == "witness":
        return tuple(str(x) for x in raw)
    if isinstance(raw, bool):
        return raw
    # celpy returns BoolType, an int subclass. Anything that is not a boolean in a boolean slot is
    # a shape error the subset checker should already have refused; returning None rather than
    # coercing keeps a non-boolean from being read as True.
    return bool(raw) if isinstance(raw, int) else None


__all__ = ["Budget", "CelResult", "CelRuntime", "CompiledProgram", "Outcome", "DEFAULT_STEPS"]
