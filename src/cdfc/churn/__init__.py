"""P15-B2 — version churn. **The package whose job is to make the number go DOWN.**

Every other package in this repository exists to establish that something was checked. This one
exists to take checks away: when the template a predicate was qualified against changes, the
predicate's qualification is about a workbook that no longer exists, and the honest response is to
stop counting it — not to keep the number and hope.

The seven rules the plan fixes, and where each lives:

| rule | statement | here |
|---|---|---|
| V1 | a predicate names what it was qualified against | `predicates/envelope.py` (`QualifiedAgainst`) |
| V2 | `qualified_against` is part of the predicate's IDENTITY | `churn/identity.py` |
| V3 | a `PROVISIONAL` predicate **still runs** and does not settle | `evaluate/selection.py`, asserted here |
| V4 | a template bump moves affected predicates to `PROVISIONAL`, and the numerator FALLS | `churn/requalify.py` |
| V5 | a stored kill case that stops dying QUARANTINES the predicate | `churn/quarantine.py` |
| V6 | the instrument stream is watched; an unobserved day is not a quiet day | `ops/watcher.py` (P13-B4) |
| V7 | withdrawal is dated and reasoned; nothing re-admits automatically | `churn/withdraw.py` |

**V3 is the one that is easy to get backwards.** The tempting implementation of "this predicate is
no longer qualified" is to stop running it. That loses detection *and* lowers the number, and the
two failures look identical on a chart: the fraction falls either way. What must happen is that the
predicate keeps running and keeps reporting, and only its claim to *settle* a cell is withdrawn —
so a filer still sees the finding, and the coverage number stops asserting the cell was decided.
`NC-X06` injects the wrong version and both guards go red.
"""

from __future__ import annotations

from cdfc.churn.identity import IdentityInputsMissing, predicate_identity
from cdfc.churn.quarantine import QuarantineReport, replay_liveness
from cdfc.churn.requalify import (
    ChurnArithmeticError,
    ChurnReport,
    changed_sheets,
    on_template_change,
)
from cdfc.churn.withdraw import Withdrawal

# `withdraw()` the FUNCTION is deliberately NOT re-exported here. Binding it at package level
# shadows `cdfc.churn.withdraw` the MODULE, so `from cdfc.churn import withdraw` hands a caller a
# function where they asked for a namespace and every `withdraw.WithdrawalUndated` raises
# `AttributeError` on an object that looks right. Callers use `cdfc.churn.withdraw.withdraw(...)`.
__all__ = [
    "ChurnArithmeticError", "ChurnReport", "IdentityInputsMissing", "QuarantineReport",
    "Withdrawal", "changed_sheets", "on_template_change", "predicate_identity",
    "replay_liveness",
]
