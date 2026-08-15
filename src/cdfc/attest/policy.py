"""P11-B1 — the policy constants, and the one that is a byte-identity hazard.

**`expires` is easy to under-rate and it is a real reproducibility hazard.** `timeVerified` is an
*input recorded in the manifest*; `expires` must be **derived from it**, never from
`datetime.now()`. A single `now()` in this derivation makes every attestation differ from its own
re-derivation on the following day, and `E2E-VERIFY` — the programme's acceptance test — fails
permanently for a reason that reads like a clock skew rather than like a bug.

The spec's own example (`2026-08-14 → 2026-11-14`) implies a 92-day constant. It lives here rather
than inline so it is pinned through `code_git_sha` in the manifest, and so a reader can find the
one place it is decided.
"""

from __future__ import annotations

import datetime as _dt
from typing import Final

# 92 days. Derived from the specification's own worked example rather than chosen: 14 August to
# 14 November 2026 is 92 days, and a constant reverse-engineered from a published example is a
# constant somebody can check.
POLICY_VALIDITY_DAYS: Final[int] = 92

# The reason the field exists at all, carried beside it so a reader of the envelope does not have
# to find this module.
POLICY_VALIDITY_BASIS: Final[str] = (
    "92 days from timeVerified. A settlement statement is about a filing checked against a pinned "
    "template by a pinned predicate set; when any of those move, the statement is about a system "
    "that no longer exists. The window is a policy choice and not a measurement, and it is stated "
    "as one."
)


class TimeNotAnInput(ValueError):
    """A timestamp was needed and none was supplied. **Never defaulted to the clock.**"""


def expires_for(time_verified: str) -> str:
    """`timeVerified + POLICY_VALIDITY_DAYS`, as an ISO-8601 instant. **Reads no clock.**

    A pure function of its argument, which is what
    `test_prop__expires_is_a_function_of_time_verified` asserts over generated instants: the same
    input yields the same output on every machine, on every day, for ever.
    """
    if not time_verified:
        raise TimeNotAnInput(
            "timeVerified is empty. It is an INPUT recorded in the manifest, not a value read at "
            "run time — defaulting it to the clock would make every attestation differ from its "
            "own re-derivation and would fail E2E-VERIFY for a reason that reads like clock skew."
        )
    try:
        stamp = _dt.datetime.fromisoformat(time_verified.replace("Z", "+00:00"))
    except ValueError as e:
        raise TimeNotAnInput(f"timeVerified {time_verified!r} is not an ISO-8601 instant: {e}") from e
    out = stamp + _dt.timedelta(days=POLICY_VALIDITY_DAYS)
    return out.isoformat().replace("+00:00", "Z")
