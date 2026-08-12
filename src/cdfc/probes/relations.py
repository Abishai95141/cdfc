"""`scope_kind` — the field that says WHY a cell is out of scope, and it lives here on purpose.

**This module's home is P9-B1.** At P5 it carries exactly one thing: the `ScopeKind` vocabulary,
which `applicable()` in a relation WRITES and `cdfc.verdict` READS. Defining it in `verdict/`
instead would be the defect arbitration C3 exists to close — *a field one document writes and
another ignores is not a repair* — so it is declared at its eventual home from the moment the
reader needs it, and P9 extends this module rather than moving the type.

**The distinction it carries, and why it is a field rather than a 31st reason code.**

    DECLARED_CHARACTERISTIC   out of scope because of a declared filer or period attribute, or a
                              fact about the pinned template. A statement about the INSTRUMENT or
                              the FILER. Remedy: none — this obligation does not apply to you.

    PREDICATE_PRECONDITION    out of scope because THIS PREDICATE's own `applicable` precondition
                              was degenerate on THIS FILING. A statement about the PREDICATE.
                              Remedy: fill in the filing — the check could not be attempted —
                              and re-qualify the predicate, because a degenerate precondition is
                              what G3 exists to reject.

The two remedies are genuinely different, which is the spec's own admission test for a new reason
code. A 31st code would have moved a count pinned in four places; a field on the existing code
carries the distinction and moves nothing. **The count stays at 30.**

**And the retention rule this field exists for:** only `DECLARED_CHARACTERISTIC` leaves the
in-scope denominator. `PREDICATE_PRECONDITION` stays counted — letting a bad predicate shrink the
thing it is measured against is how the empty-filing attack works.
"""

from __future__ import annotations

from typing import Final, Literal, get_args

ScopeKind = Literal["IN_SCOPE", "DECLARED_CHARACTERISTIC", "PREDICATE_PRECONDITION"]

SCOPE_KINDS: Final[frozenset[str]] = frozenset(get_args(ScopeKind))

# The one member that removes a cell from the in-scope denominator. Named as a constant so that
# `states.in_scope()` reads it rather than repeating the string, and a second removal rule would
# have to be written somewhere this constant is not.
LEAVES_IN_SCOPE: Final[str] = "DECLARED_CHARACTERISTIC"
