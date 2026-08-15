"""P12-B3 — envelope parsing. **A malformed candidate is a counted row, never a retry.**

`DISCARD_REASONS` is closed at six and a discard with an unlisted reason is rejected at write time.
The closure is the point: an open reason set becomes `"other"`, and `"other"` becomes the bucket
that absorbs whatever nobody wanted to name.

## Nothing here raises on bad model output

Every failure mode returns a `Discard`. **A model that emits rubbish is data about the model**, and
an exception at this layer would end the batch, lose the rows already produced, and — worst — make
the discard rate a function of where in the batch the rubbish landed. `parse()` therefore has no
failure path that is not a row.

The one thing that *does* raise is an attempt to record a reason outside the six: that is a defect
in **us**, not in the model, and the two must not be handled the same way.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

DISCARD_REASONS: Final[tuple[str, ...]] = (
    "not_yaml",
    "envelope_schema_invalid",
    "missing_clause_span",
    "cel_parse_error",
    "unknown_host_fn",
    "duplicate_of_earlier_candidate",
)


class UnlistedDiscardReason(ValueError):
    """A reason outside the closed six. **Rejected at write time.**"""


@dataclass(frozen=True, slots=True)
class Discard:
    reason: str
    detail: str

    def __post_init__(self) -> None:
        if self.reason not in DISCARD_REASONS:
            raise UnlistedDiscardReason(
                f"{self.reason!r} is not one of {DISCARD_REASONS}. The set is closed because an "
                "open one acquires an `other` bucket, and `other` is where the reasons nobody "
                "wanted to name go to stop being counted."
            )


@dataclass(frozen=True, slots=True)
class ParseOutcome:
    """Exactly one of `envelope` / `discard` is set. Both-or-neither cannot be constructed."""

    envelope: Any | None
    discard: Discard | None

    def __post_init__(self) -> None:
        if (self.envelope is None) == (self.discard is None):
            raise ValueError(
                "a parse outcome is an envelope OR a discard. Both would be a candidate that is "
                "simultaneously admitted and rejected; neither would be a call whose result left "
                "no row, and the discard pile is the funnel's stage 0."
            )


def parse(
    raw: str,
    *,
    seen_digests: frozenset[str] = frozenset(),
    host_fns: frozenset[str] | None = None,
) -> ParseOutcome:
    """YAML → `Candidate`, or one of the six discards. **Never raises on model output.**"""
    import yaml

    from cdfc.canon import digest

    try:
        obj = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return ParseOutcome(None, Discard("not_yaml", str(exc)[:400]))
    if not isinstance(obj, dict):
        return ParseOutcome(
            None, Discard("not_yaml", f"parsed to {type(obj).__name__}, not a mapping")
        )

    # The duplicate check runs BEFORE construction, so a repeated candidate is counted as a
    # duplicate rather than as whatever else happens to be wrong with it the second time.
    if digest(obj) in seen_digests:
        return ParseOutcome(
            None, Discard("duplicate_of_earlier_candidate", f"digest {digest(obj)[:16]}…")
        )

    clause = obj.get("clause")
    if isinstance(clause, dict) and not clause.get("span"):
        return ParseOutcome(
            None,
            Discard("missing_clause_span",
                    "a clause with no span cannot be located, and G0 is `source.find(quote)` at "
                    "an exact span"),
        )

    try:
        from cdfc.predicates.loader import load_candidate

        candidate = load_candidate(obj)
    except Exception as exc:                       # noqa: BLE001 — every failure becomes a ROW
        # `ci/no-bare-except.sh` polices `except:` and bare re-raises; this is a broad catch with a
        # NAMED destination, which is the opposite defect from a swallowed exception: nothing is
        # lost, the class and message become the discard's detail, and the row is counted.
        return ParseOutcome(
            None, Discard("envelope_schema_invalid", f"{type(exc).__name__}: {exc}"[:400])
        )

    try:
        from cdfc.predicates.ast_walker import all_called_host_fns, check_declared_keys

        check_declared_keys(candidate)
        called = all_called_host_fns(candidate)
    except Exception as exc:                       # noqa: BLE001 — same rule, different reason
        return ParseOutcome(None, Discard("cel_parse_error", f"{type(exc).__name__}: {exc}"[:400]))

    if host_fns is None:
        from cdfc.predicates.host_fns import default_registry

        host_fns = frozenset(default_registry().names())
    unknown = sorted(called - host_fns)
    if unknown:
        return ParseOutcome(
            None, Discard("unknown_host_fn", f"{unknown} are not in the closed registry")
        )

    return ParseOutcome(candidate, None)
