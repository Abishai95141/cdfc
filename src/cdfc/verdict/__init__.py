"""cdfc.verdict — the verdict model. CI scan root (R5).

The public names the plan specifies, re-exported from one place. `reasons.py` is the enum,
`states.py` carries everything that joins a reason to a state, and `invalid.py` is the SEPARATE
run-level vocabulary — no string is shared between the two, and both are written when a cause has
an item-level analogue.
"""

from cdfc.verdict.invalid import InvalidCause
from cdfc.verdict.reasons import (
    FAMILIES,
    REASON_COUNT,
    ReasonCode,
    ReasonDisciplineError,
    by_family,
    family_of,
)
from cdfc.verdict.states import (
    ERROR_STATES,
    FAMILY,
    ITEM_STATE_COUNT,
    NO_REASON_STATES,
    PRECEDENCE,
    REMOVAL_BASIS,
    SETTLED,
    ItemState,
    MissingScopeKindError,
    RemovalBasis,
    in_scope,
    rank,
    reason_required,
    requalification_flag,
    validate_pair,
    worst,
)

__all__ = [
    "ERROR_STATES", "FAMILIES", "FAMILY", "ITEM_STATE_COUNT", "InvalidCause", "ItemState",
    "MissingScopeKindError", "NO_REASON_STATES", "PRECEDENCE", "REASON_COUNT", "REMOVAL_BASIS",
    "ReasonCode", "ReasonDisciplineError", "RemovalBasis", "SETTLED", "by_family", "family_of",
    "in_scope", "rank", "reason_required", "requalification_flag", "validate_pair", "worst",
]
