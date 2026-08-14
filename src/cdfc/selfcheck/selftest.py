"""P10-B1 — `P-SELFTEST-DEAD`: the canary for the canary loop.

A predicate whose `expr` is the literal `true` **cannot be made to FAIL by any fault**. So the loop
running it and reporting that it stayed silent is the only evidence, from inside the loop, that the
loop is running at all: a stub that reports every canary as passing reports this one as passing
too, and *that* is the alarm.

Its expected outcome is **inverted**. `silent == {P-SELFTEST-0001}` is health;
`silent ⊋ {P-SELFTEST-0001}` means a real predicate died; `silent ⊉ {P-SELFTEST-0001}` means the
loop is lying, because a predicate that cannot fire and is reported as having fired did not run.

---

**TWO DEVIATIONS FROM `plan/05`, both recorded here rather than in a commit message.**

**(1) It is not a registry member, and that is strictly stronger than the plan.** `plan/05` writes
*"Registry member. kind='selftest' => excluded from the settled numerator AND from every
filer-facing surface"*, and then §P10·L.4 has to close the hole that creates: *"if the registry
loader silently drops `kind='selftest'` members … the expected set becomes empty, the observed set
is empty, and the run goes green."* The plan closes it with a module-level constant,
`EXPECTED_SILENT`.

Seeding it as a **constant of this module** rather than as a registry row closes the same hole one
step earlier — the loader cannot drop what it never loads — and keeps `EXPECTED_SILENT` as the
second lock rather than the only one. Both are here. The cost is that "excluded from every surface"
stops being a property of a `kind` field and becomes a property of the type, which is why
`test_st__selftest_settles_no_cell` asserts its id appears in no `RunCheck`, no `run_cell`, no term
of the settled fraction and no rendered surface — absence, checked, rather than exclusion, declared.

**(2) It is not a `Predicate`, because a `Predicate` with no `schema_keys` cannot exist and one
with `schema_keys` would break cause isolation.** `envelope._validate_common` refuses an empty
`schema_keys` — correctly: *"a predicate that declares no footprint settles no cells, and the
settled fraction would count it for free."* And a self-test that declared a footprint would reach
`evaluate_one`'s order-4 check, bind zero cells of the template, and raise
`invalid.cells_bound_zero` on **every run** — which would make §P10·L.2.1's cause-isolation
assertion (*the `invalid` cause set is exactly `{canary_silent}`*) unsatisfiable by construction.

So it carries its own two-field type and is evaluated through **the same `CelRuntime`, on the same
fact activation, as every other check**. That is the half that matters: a stubbed loop, a stubbed
runtime or a short-circuited evaluator all report this one as having fired, and the disposition
turns the run `INVALID`.

**The flag is removed, and `plan/05` rules it out explicitly.**
`plan/01-validation-methodology.md` §2.5 NC-C01b seeds this predicate *"under
`CDFC_CANARY_SELFTEST=1`"*. A self-test that runs only when a flag is set is a self-test that is
off in production, which is the failure this whole layer exists to catch, one level up.
`test_nc__C09a_selftest_runs_with_no_environment_set` runs the loop with the environment stripped.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

SELFTEST_ID: Final[str] = "P-SELFTEST-0001"

# §P10·L.4, and it is one line and no more. The expected-silent set is a MODULE-LEVEL CONSTANT and
# is never derived from the loaded registry. Derived from the registry, a loader that drops the
# self-test makes the expected set empty, the observed set is empty, they agree, and the run goes
# green — the recursion closing on itself in the flattering direction.
EXPECTED_SILENT: Final[frozenset[str]] = frozenset({SELFTEST_ID})


@dataclass(frozen=True, slots=True)
class SelfTestPredicate:
    """Two fields and no qualification, because there is nothing to qualify.

    It claims no fault class — it catches nothing, by construction — and declares no schema key,
    because a declared key is a footprint and a footprint is what puts a check on a filer-facing
    surface.
    """

    id: str = SELFTEST_ID
    kind: str = "selftest"
    expr: str = "true"
    # A statement of what it is for, carried in the object so a reader of `run.jsonl` does not
    # have to find this module to know why an always-true check is in the population.
    rationale: str = (
        "expr is the literal `true`, so no fault can make it FAIL. The loop asserts it is SILENT; "
        "a report that it fired is proof the loop is not running."
    )

    def __post_init__(self) -> None:
        if self.expr != "true":
            raise ValueError(
                f"{self.id}: expr is {self.expr!r}. The self-test's entire evidential value is "
                "that NO fault can make it FAIL. An expr that could fail makes a silent result "
                "ambiguous between `the loop ran` and `the fault was absent`."
            )
        if self.id not in EXPECTED_SILENT:
            raise ValueError(
                f"{self.id} is not in EXPECTED_SILENT. The expected set is a constant; a "
                "self-test whose id is outside it is a self-test nothing is watching."
            )


P_SELFTEST_DEAD: Final[SelfTestPredicate] = SelfTestPredicate()
