"""DPM-XL -> CEL. **Refuses with a NAMED reason rather than guessing.**

The translation is small because the vocabulary is: fourteen function-like tokens across 12,925
published rules, and zero unknown constructs (`E1`). The work is the `with {…}` context header,
which CEL has no binding form for and which must be compiled AWAY into explicit data-point paths.

**Every refusal carries a `NotExecuted` member**, because the product claim is *"here is the typed
reason for each of the other N−M"* and an untyped reason cannot be counted or acted on.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cdfc.pathm.dpmxl import BRACE, Parsed, parse
from cdfc.pathm.statement import NotExecuted, PublishedRule
from cdfc.schema.anchor import Anchor

# The four host functions `E1` identified as unlocking 964 of 12,925 rules WITHOUT weakening a ban.
# They are bounded, total, and free of the clock and of regex — which is why they are admissible
# where `time_shift` and `match` are not.
PATH_M_HOST_FNS: frozenset[str] = frozenset({"isnull", "abs", "max", "min"})

# Deliberate bans. Each maps to its OWN reason: "we chose not to" and "we cannot" are different
# statements to a supervisor, and a coverage table that merged them would be hiding a choice.
BANNED: dict[str, NotExecuted] = {
    "time_shift": NotExecuted.BANNED_CONSTRUCT_CLOCK,
    "match": NotExecuted.BANNED_CONSTRUCT_REGEX,
}

# Structural keywords the compiler handles directly; they are not host functions.
STRUCTURAL: frozenset[str] = frozenset({"if", "then", "else", "and", "or", "not", "sum", "filter"})

# `{r0850-0860}` / `{c0010-0040}` -- a hyphenated axis RANGE. Parseable, not bindable: see
# `NotExecuted.NEEDS_RANGE_BINDING`.
RANGE = re.compile(r"\{[^{}]*\b[rc]\d{3,4}\s*-\s*\d{3,4}")


@dataclass(frozen=True, slots=True)
class Compiled:
    rule: PublishedRule
    cel: str
    anchors: tuple[Anchor, ...]


@dataclass(frozen=True, slots=True)
class Refused:
    rule: PublishedRule
    reason: NotExecuted
    detail: str


def _path(a: Anchor) -> str:
    """A data point as a bound CEL path under the `filing` root."""
    def clean(s: str) -> str:
        return re.sub(r"[^A-Za-z0-9]", "_", s).strip("_").lower()
    parts = [clean(a.table)]
    parts += [f"r{r}" for r in a.rows]
    parts += [f"c{c}" for c in a.cols]
    return "filing." + ".".join(p for p in parts if p) + ".v"


def _translate(parsed: Parsed) -> str:
    """The body, with data points bound and DPM-XL operators mapped to CEL."""
    out = parsed.body
    # Data points first, so a later token replacement cannot walk into a brace group.
    def sub_point(m: re.Match[str]) -> str:
        from cdfc.pathm.dpmxl import parse_point
        a = parse_point(m.group(1), parsed.context.table)
        return _path(a) if a is not None else m.group(0)
    out = BRACE.sub(sub_point, out)
    # DPM-XL `=` is equality, not assignment. Do it before `<=`/`>=`/`!=` are disturbed.
    out = re.sub(r"(?<![<>!=])=(?!=)", "==", out)
    out = re.sub(r"\bnot\b", "!", out)
    out = re.sub(r"\band\b", "&&", out)
    out = re.sub(r"\bor\b", "||", out)
    # `isnull(x)` is `!has(x)` -- an absence test, which CEL expresses natively.
    out = re.sub(r"\bisnull\s*\(", "!has(", out)
    return " ".join(out.split())


def compile_rule(rule: PublishedRule) -> Compiled | Refused:
    """One published rule -> executable CEL, or a typed refusal. **No model is consulted.**"""
    if not rule.active:
        return Refused(rule, NotExecuted.DEACTIVATED_BY_PUBLISHER,
                       "the regulator switched this rule off")
    if rule.scope_is_null:
        return Refused(rule, NotExecuted.NO_TABLE_SCOPE,
                       f"the Tables column is {rule.tables!r}; NULL is absence, not a table name")
    if not rule.expression.strip():
        return Refused(rule, NotExecuted.UNPARSEABLE_EXPRESSION, "the expression is empty")

    parsed = parse(rule.expression, scope=rule.tables)
    for call in parsed.calls:
        if call in BANNED:
            return Refused(rule, BANNED[call], f"{call} is banned by cel_profile")
    unknown = [c for c in parsed.calls if c not in STRUCTURAL and c not in PATH_M_HOST_FNS]
    if unknown:
        return Refused(rule, NotExecuted.NEEDS_HOST_FUNCTION,
                       f"outside the admitted set: {unknown}")
    if not parsed.anchors:
        if RANGE.search(rule.expression):
            return Refused(rule, NotExecuted.NEEDS_RANGE_BINDING,
                           "addresses a row or column range; expanding it would invent axis "
                           "members the table may not have")
        return Refused(rule, NotExecuted.UNPARSEABLE_EXPRESSION,
                       "the expression addresses no data point, so there is nothing to bind")
    return Compiled(rule=rule, cel=_translate(parsed), anchors=parsed.anchors)
