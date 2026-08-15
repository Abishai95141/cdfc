"""P12-B1 — **`lock()` refuses to write a criterion `decide()` cannot consume.** Adversary F30.

## The finding this module is the repair for

`beats_baselines` was written early, hashed early, and committed inside the one artifact whose
entire epistemic value is that it was fixed before the model ran — **and it was prose.**
*"Marginal kill strictly greater than B0"* compares a count **to what?** To zero? To
`killed_by_baseline(B0)`? To the baseline's own marginal over the candidate? Three readings, three
different gates, and **the weakest is trivially satisfiable**: `|K_c \\ K_B2| > 0` is true of any
predicate that kills anything the two degenerate envelopes do not, which is most of them.

So the lock protected a *sentence* rather than a *criterion*. It is not enough that a threshold be
early. It must be **arithmetic** — a number a program reads — and this module is what makes the
prose form unreachable: a criterion that does not parse does not lock, and an experiment whose
criterion does not lock **does not run**.

## What "machine-evaluable" means here, exactly

The pre-registration carries one fenced block, tagged `cdfc-criterion`, of `NAME = <integer>`
lines. This module asserts:

1. **Every threshold `decide()` and `beats_baselines()` read is present.** A missing one is a
   threshold that lives only in code, where it can be edited without touching the hashed document.
2. **Every value is an integer literal.** `"at least six"`, `">= 6"` and `"6 (see §0.5)"` all fail.
   The parse is the point: if a human has to interpret it, it is not a criterion.
3. **Every value equals the module constant it names.** A document and a program that disagree
   about a threshold are two gates with nobody having chosen which is real — and the document is
   the one a reader checks, so the disagreement would resolve silently in favour of the code.
4. **No threshold exists in code that the document does not carry.** The check runs in **both**
   directions for the same reason the AST walker does: a constant the criterion reads and the
   pre-registration never mentions is a threshold outside the lock.

The fourth is the one that would have caught F30's own shape, because `MARGINAL_FLOOR_NUM` and
`MARGINAL_FLOOR_DEN` are exactly the constants that did not exist when the prose was written.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Final

FENCE: Final[str] = "```cdfc-criterion"

# EVERY threshold the two pure functions read, and the module that owns each. The mapping is the
# contract: `assert_machine_evaluable` checks the document against it in both directions.
THRESHOLDS: Final[Mapping[str, tuple[str, str]]] = {
    "N1": ("cdfc.experiment.power", "N1"),
    "RETAIN1": ("cdfc.experiment.power", "RETAIN1"),
    "DELETE1": ("cdfc.experiment.power", "DELETE1"),
    "N2": ("cdfc.experiment.power", "N2"),
    "RETAIN2": ("cdfc.experiment.power", "RETAIN2"),
    "MARGINAL_FLOOR_NUM": ("cdfc.experiment.marginal", "MARGINAL_FLOOR_NUM"),
    "MARGINAL_FLOOR_DEN": ("cdfc.experiment.marginal", "MARGINAL_FLOOR_DEN"),
    "TARGET_A": ("cdfc.experiment.marginal", "TARGET_A"),
    "GENERATE_CAP_B": ("cdfc.experiment.marginal", "GENERATE_CAP_B"),
    "CANDIDATES_PER_OBLIGATION_PER_REGIME": (
        "cdfc.experiment.marginal", "CANDIDATES_PER_OBLIGATION_PER_REGIME"
    ),
}


class CriterionIsProse(ValueError):
    """A threshold in the pre-registration is not a number a program can read.

    **This is raised by `lock()`, before anything is written.** The experiment does not run.
    """


class CriterionDisagreesWithCode(ValueError):
    """The document and the module state different thresholds."""


def parse_criterion(path: Path) -> Mapping[str, int]:
    """The `cdfc-criterion` block, as integers. Raises on anything that is not one."""
    text = path.read_text(encoding="utf-8")
    start = text.find(FENCE)
    if start == -1:
        raise CriterionIsProse(
            f"{path} carries no `{FENCE}` block. The criterion must be stated as arithmetic that "
            "a program reads, not as a sentence a reader interprets: a criterion that has to be "
            "interpreted after the result is not a criterion."
        )
    body_start = start + len(FENCE)
    end = text.find("```", body_start)
    if end == -1:
        raise CriterionIsProse(f"{path}'s `{FENCE}` block is not closed")

    out: dict[str, int] = {}
    for lineno, raw in enumerate(text[body_start:end].splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise CriterionIsProse(
                f"{path}, criterion line {lineno}: {raw.strip()!r} is not `NAME = <integer>`."
            )
        name, _, value = line.partition("=")
        name, value = name.strip(), value.strip()
        try:
            out[name] = int(value)
        except ValueError:
            raise CriterionIsProse(
                f"{path}, criterion line {lineno}: {name} = {value!r} is not an integer literal. "
                "`>= 6`, `at least six` and `6 (see §0.5)` all read well and none of them "
                "evaluates. This is the F30 shape: a threshold that was hashed early and still had "
                "three readings, of which the weakest was trivially satisfiable."
            ) from None
    return out


def assert_machine_evaluable(path: Path) -> Mapping[str, int]:
    """The whole check, in both directions. Called by `prereg.lock()` before it writes."""
    declared = parse_criterion(path)

    missing = sorted(set(THRESHOLDS) - set(declared))
    if missing:
        raise CriterionIsProse(
            f"{path} does not carry {missing}. A threshold that lives only in code is a threshold "
            "outside the lock, editable without touching the hashed document — which is the whole "
            "thing the hash exists to prevent."
        )
    extra = sorted(set(declared) - set(THRESHOLDS))
    if extra:
        raise CriterionIsProse(
            f"{path} declares {extra}, which no pure function reads. A threshold nothing consumes "
            "is a number in a document: it will be quoted as a criterion and enforce nothing."
        )

    import importlib

    disagreements: list[str] = []
    for name, (module_name, attr) in sorted(THRESHOLDS.items()):
        module = importlib.import_module(module_name)
        actual = getattr(module, attr)
        if declared[name] != actual:
            disagreements.append(
                f"{name}: pre-registration says {declared[name]}, {module_name}.{attr} is {actual}"
            )
    if disagreements:
        raise CriterionDisagreesWithCode(
            "the pre-registration and the code state different thresholds:\n  "
            + "\n  ".join(disagreements)
            + "\nTwo gates, and nobody has chosen which is real. The document is the one a reader "
            "checks and the code is the one that runs, so the disagreement resolves silently in "
            "favour of the code and the reader never learns."
        )
    return declared
