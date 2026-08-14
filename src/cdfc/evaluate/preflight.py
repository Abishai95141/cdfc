"""P5-B1 — F7: the declared-key check, BEFORE `expr` is evaluated at all.

**Why this is structural and not defensive**, and it is the paragraph not to simplify away.

The CEL specification states that for `||` and `&&`, if one operand determines the result, a
runtime error in the other *"will be ignored."* So `true || <error>` is `true` — and an unguarded
predicate returns `PASS` while silently swallowing an operand that could not be evaluated at all.
**That is the exact defect this product exists to prevent, manufactured by the language.**

Pre-flighting every declared key *before* `expr` runs makes the guard independent of how the
predicate was written. It is **exact rather than an estimate** because P4-B2 machine-checked
`schema_keys` against the AST in both directions: the declared set IS the read set.

**D-P5-03: a type check that did not happen is never reported as one.** Type is inferred locally
from the AST; where inference is ambiguous the key is presence-checked only, and the result
carries `keys_type_checked < keys_checked` so the run can publish both.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cdfc.predicates.ast_walker import inferred_types, slots_of


@dataclass(frozen=True, slots=True)
class PreflightResult:
    proceed: bool
    missing: tuple[str, ...]
    mistyped: tuple[tuple[str, str, str], ...]   # (key, expected, actual)
    keys_checked: int
    keys_type_checked: int

    @property
    def blocking_key(self) -> str | None:
        if self.missing:
            return self.missing[0]
        return self.mistyped[0][0] if self.mistyped else None


def expected_types(p: Any) -> dict[str, str | None]:
    """The type each declared key is compared against, from the AST. `None` == undecidable."""
    out: dict[str, str | None] = {}
    for slot, src in slots_of(p):
        for key, hint in inferred_types(src, slot=slot).items():
            if key in out and out[key] != hint:
                out[key] = None      # two slots disagree: undecidable, presence-checked only
            else:
                out.setdefault(key, hint)
    return out


def preflight(p: Any, facts: Any) -> PreflightResult:
    """Every DECLARED key, checked for presence and — where the AST decides it — for type."""
    declared = tuple(p.schema_keys)
    hints = expected_types(p)
    missing: list[str] = []
    mistyped: list[tuple[str, str, str]] = []
    type_checked = 0

    for key in declared:
        if not facts.has(key):
            missing.append(key)
            continue
        expected = hints.get(key)
        if expected is None:
            continue                      # D-P5-03: presence only, and the count says so
        actual = facts.type_of(key)
        if actual is None:
            continue                      # the fact side cannot decide either; still presence only
        if actual == "MIXED":
            # A repeated node whose elements disagree in type. NOT undecidable — decidably
            # unsatisfiable: no single comparison holds over a column that is part number and part
            # text. Letting it through hung the evaluator at 6 GB on one predicate.
            type_checked += 1
            mistyped.append((key, expected, "MIXED"))
            continue
        type_checked += 1
        if not _compatible(expected, actual):
            mistyped.append((key, expected, actual))

    return PreflightResult(
        proceed=not missing and not mistyped,
        missing=tuple(missing),
        mistyped=tuple(mistyped),
        keys_checked=len(declared),
        keys_type_checked=type_checked,
    )


def _compatible(expected: str, actual: str) -> bool:
    """`STRING` admits the empty string a blank cell carries; `INT` does not admit a bool.

    Deliberately narrow. A permissive compatibility table is a pre-flight that passes everything,
    which is the same as no pre-flight with a count beside it.
    """
    if actual == "MIXED":
        return False        # a heterogeneous column satisfies no single comparison
    if expected == actual:
        return True
    # A blank ENUM/TEXT cell is the empty string, and a bound written against a number may read it.
    # That is a MISTYPE and the predicate must not run: `"" >= 0` is not false, it is meaningless.
    return False
