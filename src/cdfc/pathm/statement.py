"""The published rule, and the CLOSED vocabulary of reasons one may not execute.

**Every rule we do not execute gets a typed reason.** That is the product claim — *"of N published
at date D we executed M, and here is the typed reason for each of the other N−M"* — and a reason
outside a closed set is a reason nobody can act on or count.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NotExecuted(StrEnum):
    """Why a published rule was not executed. CLOSED, and every member is a DIFFERENT remedy."""

    DEACTIVATED_BY_PUBLISHER = "deactivated_by_publisher"
    """The regulator switched it off. We report it because a coverage table that hides the
    publisher's own deactivations overstates what there was to execute."""

    BANNED_CONSTRUCT_CLOCK = "banned_construct_clock"
    """`time_shift`. `cel_profile` bans the clock so a verdict cannot depend on when it ran."""

    BANNED_CONSTRUCT_REGEX = "banned_construct_regex"
    """`match`. Banned so a predicate cannot carry an unbounded backtracking cost."""

    NEEDS_HOST_FUNCTION = "needs_host_function"
    """A function outside the admitted set. Named, so the remedy is 'register it', not 'rewrite'."""

    NO_TABLE_SCOPE = "no_table_scope"
    """The rule's `Tables` cell is empty or the literal four-character string `NULL`. `E2` found
    exactly one such rule and it is a defect in the publication, not in the parser."""

    NEEDS_RANGE_BINDING = "needs_range_binding"
    """The rule addresses a row or column RANGE — `{r0850-0860}`, `{c0010-0040}`. It parses; what
    is missing is the binding. Expanding the range here would INVENT rows that may not exist in
    the table, which is how a read set comes to contain data points the rule never addressed. A
    range binds against the published table's own axis definitions, and those are a different
    artefact we have not pinned."""

    UNPARSEABLE_EXPRESSION = "unparseable_expression"
    """The expression did not parse. Distinct from an unknown construct: this is a shape we could
    not read at all."""

    UNKNOWN_CONSTRUCT = "unknown_construct"
    """Parsed, but carries a token outside the admitted vocabulary. `E1` measured 0 of 12,925."""


@dataclass(frozen=True, slots=True)
class PublishedRule:
    """One row of a regulator's published validation-rule set, as published."""

    code: str
    framework: str
    module: str
    tables: str
    expression: str
    precondition: str
    description: str
    active: bool
    severity: str

    @property
    def scope_is_null(self) -> bool:
        """`E2`: the literal `NULL` means ABSENT and must never be read as a table name."""
        return not self.tables.strip() or self.tables.strip().upper() == "NULL"


@dataclass(frozen=True, slots=True)
class RuleSet:
    """The published set, with the provenance that makes `N` an EXTERNAL fact rather than ours."""

    source_name: str
    source_sha256: str
    published_at: str          # the date IN THE FILE'S OWN NAME, never a clock read
    rules: tuple[PublishedRule, ...]

    def __len__(self) -> int:
        return len(self.rules)

    @property
    def active(self) -> tuple[PublishedRule, ...]:
        return tuple(r for r in self.rules if r.active)
