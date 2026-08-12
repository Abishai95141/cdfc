"""The predicate registry.

At P0 through P4 `load_or_refuse` refuses UNCONDITIONALLY (R5). That is not a stub: the
predicate schema does not exist yet, so there is no qualification block to check, and a
loader that accepted anything would be the vacuous pass at the registry boundary.

**This entry is PROVISIONAL in the negative-control catalogue**, and the sweep reports it
in its own column rather than counting it as caught. Its guard
(`test_nc__Q02_unqualified_predicate_does_not_load`) is green for four phases while
proving nothing, because its admission-side twin — a *qualified* predicate that DOES
load — is impossible until P4 gives the schema. A green entry with no information in it
must not be counted as evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import NoReturn

PHASE = "P0"


class UnqualifiedPredicate(Exception):
    """A predicate without a qualification record. It does not load. Ever."""


def load_or_refuse(envelope: Mapping[str, object]) -> NoReturn:
    """P0: always raises. P4 gives it the other branch."""
    pid = envelope.get("id", "<no id>")
    raise UnqualifiedPredicate(
        f"predicate {pid!r} not loaded: no qualification record exists at phase {PHASE}. "
        "A predicate whose error rate is unknown is not admitted — which is what makes "
        "the settled-fraction claim true by construction rather than by discipline."
    )
