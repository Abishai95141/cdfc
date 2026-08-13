"""B0 — the template's own checkable relations.

The regulator's blank already encodes arithmetic identities: `=SUM(range)`, `=COUNTIF(...)`, and
plain carries `=OtherSheet!C25`. **A filing checker that catches only what those already catch has
added nothing**, so B0's kill set is exactly the set of mutants killed by predicates drawn from
those classes — the work the artifact does for free.

It is a subset of our own harvest by construction, and that is the point rather than a flaw: B0
answers *"what would you have caught by just recomputing the template's formulas"*, and any
candidate whose marginal kill over B0 is zero is doing exactly that and nothing more.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

# The four formula-derived harvest classes. A data validation is NOT here: a dropdown is a
# constraint the regulator wrote, not a relation the template can recompute for itself.
B0_CLASSES: Final[frozenset[str]] = frozenset(
    {"sum_identity", "tally_identity", "cross_sheet_equality", "same_sheet_equality"}
)


def members(class_of_predicate: Mapping[str, str]) -> frozenset[str]:
    """The predicate ids whose harvest class is one of B0's."""
    return frozenset(pid for pid, cls in class_of_predicate.items() if cls in B0_CLASSES)


def kill_set(stored, class_of_predicate: Mapping[str, str], *,
             exclude: Sequence[str] = ()) -> frozenset[str]:
    """The mutants B0 kills.

    `exclude` removes the candidate under test, because a baseline that contains the predicate it
    is being compared against always scores a marginal kill of zero — the comparison would be with
    itself.
    """
    out: set[str] = set()
    for pid in members(class_of_predicate) - set(exclude):
        out |= stored.mutants(pid)
    return frozenset(out)
