"""G-EVAL's two arms, and the independence label that must travel with every number they found.

**Why this is code and not a sentence in a measurement file.** `plan/02` §Y's rule is *"there is
no third option and no silent one"*: either arm 2's oracle was authored by someone who did not
write the evaluator, or every surface quoting a number derived from `cdfc.calc` carries the
literal `SAME-AUTHOR — a weaker instrument`. A rule of that shape enforced by a human writing a
label is a rule with a third option — the one where nobody remembers. So the arms are declared
here, `label()` COMPUTES the string, and `test_contract__geval_label_travels_with_the_numbers`
asserts it is on the page.

**What arm 2 actually is in this build, stated plainly because it is not what the plan assumed.**
`plan/02` specifies arm 2 as a human-authored `expected.json`, and budgets 1.5 person-days of
someone who has not read `calc/`. No such person exists on this project. What was built instead
is a **foreign-engine differential**: the same workbook recalculated by LibreOffice, cell for
cell. That substitution is neither silently better nor silently worse, and both directions are
recorded on the record itself rather than argued in prose:

- **Stronger** on the axis the plan was worried about. The failure it names is *the engineer
  implements `AGGREGATE(15,6,…)` with a subtly wrong tie-break and writes the expectation file
  from the same mental model an hour later.* A foreign engine cannot share a mental model. It
  found exactly that defect: 29 cells where we returned `#NUM!`, `IFERROR` wrote `"NA"`, and
  nothing was red. See `docs/AUDIT-P0-P6.md` §6.1.
- **Weaker** on an axis the plan did not have to consider, because its oracle was a person.
  LibreOffice reads the same formula text we do. It can say *your value differs from mine*; it
  can never say *the regulator's formula is wrong*. `'1. Introduction'!D17`'s under-count is
  invisible to it and visible to a reader — which is why P9-B1 needs `template_defects.yaml` and
  cannot get it from this arm.

So arm 2 is `INDEPENDENT`, and the sentence naming what it still cannot see is carried beside the
label rather than left to be inferred from its absence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Independence = Literal["INDEPENDENT", "SAME-AUTHOR"]

# The literal the plan requires on every surface if the oracle and the evaluator share an author.
# It is a constant so that the test asserting its presence and the renderer emitting it cannot
# spell it differently — a label enforced by two spellings is enforced by neither.
WEAKER_INSTRUMENT: Final[str] = "SAME-AUTHOR — a weaker instrument"

THIS_PROJECT: Final[str] = "cdfc"


@dataclass(frozen=True, slots=True)
class Arm:
    n: int
    name: str
    oracle: str
    oracle_author: str          # who wrote the ORACLE, not who ran the comparison
    finds: str                  # what a disagreement on this arm would mean
    blind_to: str               # what this arm cannot see even when it is green

    @property
    def independence(self) -> Independence:
        """COMPUTED from the author, never declared. A declared independence is a claim; a
        computed one is a consequence of a field somebody had to fill in with a name."""
        return "SAME-AUTHOR" if self.oracle_author == THIS_PROJECT else "INDEPENDENT"


ARM1: Final[Arm] = Arm(
    n=1,
    name="the regulator's own cached values",
    oracle="the `<v>` elements the regulator shipped inside the blank",
    oracle_author="IFSCA (the regulator, via whichever engine wrote the workbook)",
    finds="our evaluator disagreeing with the engine that produced the published file",
    blind_to=(
        "a workbook whose cached values are constant. FME caches 301 zeros and 204 copies of "
        "'NA', so a null evaluator scores 505 of 505 here — which is why arm 2 exists"
    ),
)

ARM2: Final[Arm] = Arm(
    n=2,
    name="a foreign engine, cell for cell",
    oracle="LibreOffice Calc, recalculating the same workbook",
    oracle_author="The Document Foundation",
    finds=(
        "our evaluator computing a different value from an implementation that shares no code "
        "and no author with it"
    ),
    blind_to=(
        "a defect in the regulator's own formula. A foreign engine reads the same formula text "
        "we do, so it agrees with us about a formula that is wrong. Arm 2 green says nothing "
        "about '1. Introduction'!D17 under-counting two of the nine scheme types"
    ),
)

ARMS: Final[tuple[Arm, ...]] = (ARM1, ARM2)


def label() -> str:
    """The literal that must render beside every number derived from `cdfc.calc`.

    Empty when arm 2 is independent — and empty is the ONLY case in which nothing renders. A
    build that returned `""` for the same-author case would satisfy every caller silently, so
    the branch is written the other way round: the label is the non-empty answer.
    """
    return "" if ARM2.independence == "INDEPENDENT" else WEAKER_INSTRUMENT


def gate_status() -> str:
    """What `ci/GATES.md` and every measurement header record for G-EVAL."""
    return "PASSED" if ARM2.independence == "INDEPENDENT" else "PASSED — NOT INDEPENDENT"
