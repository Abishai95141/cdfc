"""The DPM-XL parser: a context header, an expression, and the data points it addresses.

**One structural construct is the whole job.** `E1` measured 12,448 of 12,925 expressions opening
with a `with {…}` context header, and CEL has no equivalent binding form. It must be compiled AWAY
into an explicit binding — once, for all of them — rather than translated token by token. The
vocabulary is small: fourteen distinct function-like tokens across the entire corpus, and zero
unknown constructs.

    with {tC_25.01.a, default: 0, interval: true}: {r0010, c0060} * 12.5 = {tC_02.00.a, r0675, c0010}
    └─────────────── context ───────────────────┘  └──────────────── body ────────────────────────┘

A data point is `{table, row, column}` with the table inheritable from the context — which is why
`Anchor` had to be a dialect-agnostic triple rather than a spreadsheet cell (`E2`, both dialects).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from cdfc.schema.anchor import Anchor

# A braced group: either the context header's `{…}` or a data point in the body.
BRACE = re.compile(r"\{([^{}]*)\}")
# `with {…}:` at the head of an expression. `re.DOTALL` because published expressions wrap.
WITH = re.compile(r"^\s*with\s*\{([^{}]*)\}\s*:\s*(.*)$", re.S | re.I)
# A function-like token: a name immediately followed by `(`.
CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# Axis atoms inside a braced group.
TABLE = re.compile(r"^t([A-Za-z0-9_.]+)$")
ROW = re.compile(r"^r([0-9]{3,4}|\*)$", re.I)
COL = re.compile(r"^c([0-9]{3,4}|\*)$", re.I)
# Any other single-letter axis with a value or a wildcard: `s*`, `z0001`, `f*`.
EXTRA_AXIS = re.compile(r"^([a-z])([0-9]{1,4}|\*)$", re.I)


@dataclass(frozen=True, slots=True)
class Context:
    """The `with {…}` header: a default table plus modifiers that bind the whole body."""

    table: str = ""
    modifiers: tuple[tuple[str, str], ...] = ()

    @property
    def interval(self) -> bool:
        return dict(self.modifiers).get("interval", "").lower() == "true"


@dataclass(frozen=True, slots=True)
class Parsed:
    context: Context
    body: str
    anchors: tuple[Anchor, ...] = field(default_factory=tuple)
    calls: tuple[str, ...] = field(default_factory=tuple)


def _atoms(group: str) -> list[str]:
    """Split on commas, EXCEPT inside a parenthesised list.

    A data point may address a SET of rows or columns in one point:

        {(r0100, r0110, r0200, r0210), c0010}

    `E2` established this — *"row and column may be a LIST … or a wildcard"* — and `Anchor` was
    given tuple-valued `rows`/`cols` for it. A naive comma split turns `(r0100` and `r0210)` into
    atoms that match no axis, and the point silently becomes unaddressable: **1,323 published
    rules were reported UNPARSEABLE by exactly that bug**, which is 10% of the corpus described by
    a reason that was not true of it.
    """
    out: list[str] = []
    depth = 0
    cur: list[str] = []
    for ch in group:
        if ch == "(":
            depth += 1
            continue
        if ch == ")":
            depth -= 1
            continue
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
            continue
        if ch == "," and depth > 0:
            # A comma INSIDE a list still separates axis atoms; the parens only stop the
            # group from being split into a different data point.
            out.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    out.append("".join(cur).strip())
    return [a for a in out if a]


def _first_table(scope: str) -> str:
    """The first table a rule declares. `NULL` and empty are ABSENCE, never a name."""
    t = (scope or "").strip()
    if not t or t.upper() == "NULL":
        return ""
    return re.split(r"[,;\s]+", t)[0].strip()


def parse_context(group: str) -> Context:
    table, mods = "", []
    for atom in _atoms(group):
        if ":" in atom:
            k, _, v = atom.partition(":")
            mods.append((k.strip(), v.strip()))
            continue
        m = TABLE.match(atom)
        if m:
            table = m.group(1)
    return Context(table=table, modifiers=tuple(mods))


def parse_point(group: str, default_table: str) -> Anchor | None:
    """`{tX, r0010, c0060}` -> an Anchor. The table falls back to the context's.

    Returns `None` for a braced group that is not a data point — a `{v_Z_08.02}` precondition
    reference, or a modifier-only group. Guessing an anchor for one would put a data point in the
    read set that the rule never addressed.
    """
    rows: list[str] = []
    cols: list[str] = []
    table = ""
    axes: list[tuple[str, str]] = []
    for atom in _atoms(group):
        if (m := TABLE.match(atom)):
            table = m.group(1)
        elif (m := ROW.match(atom)):
            rows.append(m.group(1))
        elif (m := COL.match(atom)):
            cols.append(m.group(1))
        elif ":" in atom:
            k, _, v = atom.partition(":")
            axes.append((k.strip(), v.strip()))
        elif (m := EXTRA_AXIS.match(atom)):
            # AN AXIS WE DO NOT UNDERSTAND IS CARRIED, NOT REFUSED. `E2` requirement 3: the anchor
            # "must tolerate EXTRA AXES it does not understand -- EIOPA adds z:, f:, fv:, seq:,
            # id:". EBA adds a bare `s*` sheet axis. Refusing the whole data point over one
            # unrecognised axis reported 114 published rules as UNPARSEABLE when every one of them
            # parses; carrying it keeps the address complete and honest about what it holds.
            axes.append((m.group(1).lower(), m.group(2)))
        else:
            return None
    if not (rows or cols):
        return None
    if not (table or default_table):
        # No table anywhere: not in the point, not in the context, not in the rule's own scope.
        # Returning None keeps it OUT of the read set rather than inventing a table for it.
        return None
    return Anchor(
        table=(table or default_table),
        rows=tuple(rows), cols=tuple(cols),
        axes=tuple(sorted(axes)), dialect="dpm-xl",
    )


def parse(expression: str, *, scope: str = "") -> Parsed:
    """Split the context from the body, then read every data point and function call in it.

    `scope` is the rule's OWN declared `Tables` column, and it is the last fallback for a data
    point that names no table and sits under a context header that names none either. `E2`
    measured 18,826 of 18,827 addresses resolving *against each rule's own declared scope* — that
    column IS the scope, so a parser that ignored it would report unresolvable addresses that the
    publisher resolved perfectly well.

    A scope of `NULL` is ABSENCE and never becomes a table name: `Anchor` refuses it, `E2` found
    exactly one such rule, and it is a defect in the publication.
    """
    m = WITH.match(expression)
    ctx = parse_context(m.group(1)) if m else Context()
    body = m.group(2) if m else expression
    fallback = ctx.table or _first_table(scope)

    anchors: list[Anchor] = []
    for g in BRACE.findall(body):
        a = parse_point(g, fallback)
        if a is not None:
            anchors.append(a)
    calls = tuple(sorted({c for c in CALL.findall(body)}))
    return Parsed(context=ctx, body=body.strip(), anchors=tuple(anchors), calls=calls)
