"""The formula evaluator — tokenizer, recursive-descent parser, topological evaluation.

Three contracts this module holds, each of which exists because breaking it produces a
clean confident wrong answer:

1. **`formula_source` has NO DEFAULT.** Every call states whether it means the TEMPLATE's
   formulas or the FILING's. The defect it prevents is checking a filing against formulas
   the filing itself supplied — under which a filer who rewrote a formula passes their own
   rewritten check.
2. **A cycle is `NOT_RUN`, never a value.** An evaluator that iterates to a fixed point
   returns a number for a circular reference, and nothing in the output says it guessed.
3. **An unimplemented function is `NOT_RUN(unimplemented: NAME)`, never zero and never
   swallowed by `IFERROR`.** `IFERROR` catches Excel errors; "we did not implement this"
   is not one.

Everything numeric is `Decimal` under a pinned context. There is no float in this package.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, localcontext
from typing import Any, Literal

from cdfc.calc.errors import DIV0, NA, NAME, VALUE, ExcelError, first_error, is_error
from cdfc.calc.functions import PRECISION, VOCABULARY, Unimplemented

FormulaSource = Literal["TEMPLATE", "FILING"]

Value = Decimal | str | bool | ExcelError | None


@dataclass(frozen=True, slots=True)
class SourceRule:
    """One row of the `formula_source` contract. It is DATA so that the published rule and the
    argument the code actually passes cannot drift apart: `gen_contract.py` renders this table
    into `EVALUATION-CONTRACT.md`, and `test_contract__formula_source_is_explicit` reads the
    same table when it checks the call sites by AST."""

    caller: str          # a dotted module path under `src/cdfc/`
    source: str          # "TEMPLATE" or "FILING"
    because: str


# --------------------------------------------------------------------------------
# THE `formula_source` CONTRACT (P9-B1, entry criterion 2b; adversary F19)
#
# Two phases meant different things by "recalculate" and both passed in isolation.
#
#   The observability filter classifies a mutant by comparing two RECALCULATED grids.
#   An F11 mutant is *a cell the pinned blank declares a formula, carrying a literal* — so
#   recalculating it through the TEMPLATE's formula graph overwrites the literal with the
#   formula's value, the two grids come out identical, and the design's flagship fault class
#   is classified UNOBSERVABLE **by construction**. `O` for F11 is then 0, `Campaign.kill_rate()`
#   raises on `O == 0`, and TEMPLATE_DIFF — predicate #1 — dies at the third gate with an
#   exception, twelve weeks after the disagreement was introduced.
#
# The repair is not a default. It is the ABSENCE of one: `recalculate` has no default
# `formula_source`, so a call site that omits it is a TypeError, and the two meanings can
# never again be reconciled by whichever phase was written second.
# --------------------------------------------------------------------------------
FORMULA_SOURCE_CONTRACT: tuple[SourceRule, ...] = (
    SourceRule(
        caller="cdfc.qualify.observability",
        source="FILING",
        because=(
            "observability is a question about THE ARTIFACT UNDER TEST. Recalculating a filing "
            "through the blank's formulas asks whether the fault survives a repair we performed "
            "on it, which is not the question. A cell the filing carries as a literal STAYS a "
            "literal."
        ),
    ),
    SourceRule(
        caller="cdfc.probes.template_diff",
        source="TEMPLATE",
        because=(
            "the relation IS the comparison of the two sources: the pinned blank's formula graph "
            "over the filed inputs, against what the filing actually holds. This is the only "
            "caller for which TEMPLATE is correct."
        ),
    ),
)

TOKEN = re.compile(
    r"""
    (?P<ws>\s+)
  | (?P<str>"(?:[^"]|"")*")
  | (?P<sheetref>(?:'[^']+'|[A-Za-z_][\w.]*)![$]?[A-Z]{1,3}[$]?\d+(?::[$]?[A-Z]{1,3}[$]?\d+)?)
  | (?P<range>[$]?[A-Z]{1,3}[$]?\d+:[$]?[A-Z]{1,3}[$]?\d+)
  | (?P<ref>[$]?[A-Z]{1,3}[$]?\d+)
  | (?P<num>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)
  | (?P<func>_?[A-Za-z][\w.]*(?=\s*\())
  | (?P<name>_?[A-Za-z][\w.]*)
  | (?P<op><=|>=|<>|[-+*/^&<>=%])
  | (?P<punc>[(),{};:@])
    """,
    re.X,
)


class ParseError(Exception):
    pass


@dataclass(frozen=True)
class ValueGrid:
    values: Mapping[tuple[str, str], Value]
    not_run: Mapping[tuple[str, str], str]
    computed_cells: frozenset[tuple[str, str]]
    formula_source: FormulaSource


# --------------------------------------------------------------------------------
# tokenizer + parser
# --------------------------------------------------------------------------------


def tokenize(src: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(src):
        m = TOKEN.match(src, i)
        if not m:
            raise ParseError(f"cannot tokenize at {i}: {src[i:i + 20]!r}")
        i = m.end()
        kind = m.lastgroup or ""
        if kind == "ws":
            continue
        out.append((kind, m.group()))
    return out


class Parser:
    def __init__(self, tokens: list[tuple[str, str]]) -> None:
        self.t = tokens
        self.i = 0

    def peek(self) -> tuple[str, str] | None:
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self) -> tuple[str, str]:
        tok = self.t[self.i]
        self.i += 1
        return tok

    def expect(self, text: str) -> None:
        tok = self.peek()
        if tok is None or tok[1] != text:
            raise ParseError(f"expected {text!r}, got {tok!r}")
        self.take()

    # precedence climbing
    def parse(self) -> Any:
        node = self.comparison()
        if self.peek() is not None:
            raise ParseError(f"trailing tokens: {self.t[self.i:]}")
        return node

    def comparison(self) -> Any:
        node = self.concat()
        while (tok := self.peek()) and tok[0] == "op" and tok[1] in ("<", ">", "<=", ">=", "=", "<>"):
            op = self.take()[1]
            node = ("cmp", op, node, self.concat())
        return node

    def concat(self) -> Any:
        node = self.additive()
        while (tok := self.peek()) and tok[1] == "&":
            self.take()
            node = ("concat", node, self.additive())
        return node

    def additive(self) -> Any:
        node = self.multiplicative()
        while (tok := self.peek()) and tok[1] in ("+", "-"):
            op = self.take()[1]
            node = ("bin", op, node, self.multiplicative())
        return node

    def multiplicative(self) -> Any:
        node = self.unary()
        while (tok := self.peek()) and tok[1] in ("*", "/"):
            op = self.take()[1]
            node = ("bin", op, node, self.unary())
        return node

    def unary(self) -> Any:
        return self.power()

    def power(self) -> Any:
        """Exponentiation, right-associative, over a SIGNED atom.

        Excel's unary minus binds TIGHTER than `^`: `-2^2` is 4, not -4. Most languages
        do the opposite, and a parser written from habit rather than from the spreadsheet
        gets the sign of every squared negative wrong — silently, with a well-formed
        number. Caught by a test asserting the Excel value.
        """
        base = self.signed_atom()
        if (tok := self.peek()) and tok[1] == "^":
            self.take()
            return ("bin", "^", base, self.power())  # right-associative: 2^3^2 = 2^(3^2)
        if (tok := self.peek()) and tok[1] == "%":
            self.take()
            return ("pct", base)
        return base

    def signed_atom(self) -> Any:
        tok = self.peek()
        if tok and tok[1] == "-":
            self.take()
            return ("neg", self.signed_atom())
        if tok and tok[1] == "+":
            self.take()
            return self.signed_atom()
        if tok and tok[1] == "@":
            self.take()
            return ("single", self.signed_atom())
        return self.atom()

    def atom(self) -> Any:
        tok = self.peek()
        if tok is None:
            raise ParseError("unexpected end of formula")
        kind, text = self.take()
        if kind == "num":
            return ("num", Decimal(text))
        if kind == "str":
            return ("str", text[1:-1].replace('""', '"'))
        if kind == "func":
            self.expect("(")
            args: list[Any] = []
            if (nxt := self.peek()) and nxt[1] != ")":
                args.append(self.comparison())
                while (nxt := self.peek()) and nxt[1] in (",", ";"):
                    self.take()
                    args.append(self.comparison())
            self.expect(")")
            return ("call", text.upper().lstrip("_").replace("XLFN.", ""), args)
        if kind in ("sheetref", "range", "ref"):
            return ("ref", text)
        if kind == "name":
            return ("name", text)
        if text == "(":
            node = self.comparison()
            self.expect(")")
            return node
        if text == "{":  # an array literal
            items: list[Any] = [self.comparison()]
            while (nxt := self.peek()) and nxt[1] in (",", ";"):
                self.take()
                items.append(self.comparison())
            self.expect("}")
            return ("array", items)
        raise ParseError(f"unexpected token {text!r}")


def parse_formula(src: str) -> Any:
    return Parser(tokenize(src.lstrip("="))).parse()


# --------------------------------------------------------------------------------
# reference resolution
# --------------------------------------------------------------------------------

CELL = re.compile(r"^[$]?([A-Z]{1,3})[$]?(\d+)$")


def _col(c: str) -> int:
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def _colname(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def expand(ref: str, default_sheet: str) -> list[tuple[str, str]]:
    """A reference to the list of (sheet, cell) it covers."""
    sheet = default_sheet
    body = ref
    if "!" in ref:
        sheet, body = ref.rsplit("!", 1)
        sheet = sheet.strip("'")
    if ":" not in body:
        m = CELL.match(body)
        return [(sheet, f"{m.group(1)}{m.group(2)}")] if m else []
    a, b = body.split(":", 1)
    ma, mb = CELL.match(a), CELL.match(b)
    if not (ma and mb):
        return []
    c1, r1 = _col(ma.group(1)), int(ma.group(2))
    c2, r2 = _col(mb.group(1)), int(mb.group(2))
    return [
        (sheet, f"{_colname(c)}{r}")
        for r in range(min(r1, r2), max(r1, r2) + 1)
        for c in range(min(c1, c2), max(c1, c2) + 1)
    ]


# ROW/ROWS/COLUMN/COLUMNS read a range's SHAPE, not its VALUES. `ROWS($C$92:C92)` in cell
# C92 is the standard "which output row am I" counter, and it is not a circular reference:
# Excel resolves it from the range's geometry without reading a cell.
#
# Treating a shape reference as a value dependency invented THIRTY circular references in
# the FME workbook that do not exist, and reported them as NOT_RUN — a defect in our
# dependency analyser, published as a finding about the regulator's template. Caught by
# checking whether the cells really were self-referential before believing the number.
SHAPE_ONLY_FUNCTIONS = frozenset({"ROW", "ROWS", "COLUMN", "COLUMNS"})


def refs_of(node: Any, *, values_only: bool = False) -> list[str]:
    """Every reference in the tree. With `values_only`, shape-only arguments are skipped."""
    if not isinstance(node, tuple):
        return []
    if node[0] == "ref":
        return [node[1]]
    if values_only and node[0] == "call" and node[1] in SHAPE_ONLY_FUNCTIONS:
        return []
    out: list[str] = []
    for part in node[1:]:
        if isinstance(part, list):
            for p in part:
                out.extend(refs_of(p, values_only=values_only))
        elif isinstance(part, tuple):
            out.extend(refs_of(part, values_only=values_only))
    return out


# --------------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------------


def _num(v: Any) -> Decimal | None:
    if isinstance(v, Decimal):
        return v
    if isinstance(v, bool):
        return Decimal(1 if v else 0)
    if isinstance(v, int):
        return Decimal(v)
    if v is None:
        return Decimal(0)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return Decimal(0)
        try:
            return Decimal(s)
        except Exception:
            return None
    return None


def _eval(node: Any, sheet: str, get: Any) -> Any:
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "str":
        return node[1]
    if kind == "array":
        return [_eval(x, sheet, get) for x in node[1]]
    if kind == "name":
        up = node[1].upper()
        if up in ("TRUE", "FALSE"):
            return up == "TRUE"
        return NAME
    if kind == "ref":
        cells = expand(node[1], sheet)
        if not cells:
            return NA
        if len(cells) == 1:
            return get(*cells[0])
        return [get(s, r) for s, r in cells]
    if kind == "neg":
        v = _eval(node[1], sheet, get)
        if is_error(v):
            return v
        n = _num(v)
        return VALUE if n is None else -n
    if kind == "pct":
        v = _eval(node[1], sheet, get)
        n = _num(v)
        return VALUE if n is None else n / Decimal(100)
    if kind == "single":
        v = _eval(node[1], sheet, get)
        return v[0] if isinstance(v, list) and len(v) == 1 else v
    if kind == "concat":
        a, b = _eval(node[1], sheet, get), _eval(node[2], sheet, get)
        if (e := first_error(a, b)) is not None:
            return e
        return f"{'' if a is None else a}{'' if b is None else b}"
    if kind == "cmp":
        op, a, b = node[1], _eval(node[2], sheet, get), _eval(node[3], sheet, get)
        if (e := first_error(a, b)) is not None:
            return e
        na, nb = _num(a), _num(b)
        if na is not None and nb is not None:
            a, b = na, nb
        else:
            a, b = str(a or ""), str(b or "")
        return {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b,
                "=": a == b, "<>": a != b}[op]
    if kind == "bin":
        op = node[1]
        a, b = _eval(node[2], sheet, get), _eval(node[3], sheet, get)
        if (e := first_error(a, b)) is not None:
            return e
        na, nb = _num(a), _num(b)
        if na is None or nb is None:
            return VALUE
        with localcontext() as ctx:
            ctx.prec = PRECISION
            if op == "+":
                return na + nb
            if op == "-":
                return na - nb
            if op == "*":
                return na * nb
            if op == "/":
                return DIV0 if nb == 0 else na / nb
            if op == "^":
                return na ** nb
        return VALUE
    if kind == "call":
        name, args = node[1], node[2]
        fn = VOCABULARY.get(name)
        if fn is None:
            raise Unimplemented(name)
        vals = [_eval(a, sheet, get) for a in args]
        return fn(*vals)
    raise ParseError(f"cannot evaluate node {node!r}")


def recalculate(
    formulas: Mapping[tuple[str, str], str],
    literals: Mapping[tuple[str, str], Value],
    *,
    formula_source: FormulaSource,
    deferred: Mapping[tuple[str, str], str] | None = None,
) -> ValueGrid:
    """Evaluate every formula cell. `formula_source` is REQUIRED — see the module docstring.

    `deferred` is formula cells the CALLER could not materialise (a shared dependent whose
    row shift is not implemented yet, say). They must be declared here rather than simply
    omitted: a cell the caller drops silently is invisible to the cascade rule, so anything
    reading it computes with a zero and returns a clean wrong number. That is exactly the
    defect the cascade rule exists to stop, committed one level up by the caller, and it
    was found in this evaluator's own arm-1 run — `A13 = A11+1` returned 1 where the answer
    was 9, because A11 had been quietly deferred.
    """
    parsed: dict[tuple[str, str], Any] = {}
    not_run: dict[tuple[str, str], str] = dict(deferred or {})
    for key, src in formulas.items():
        try:
            parsed[key] = parse_formula(src)
        except (ParseError, Exception) as e:  # noqa: BLE001 - recorded, never swallowed
            not_run[key] = f"parse: {type(e).__name__}: {e}"

    # dependency edges, then a topological order. A cycle is NOT_RUN, never a value.
    known = set(parsed) | set(not_run)
    deps: dict[tuple[str, str], set[tuple[str, str]]] = {}
    for key, ast in parsed.items():
        sheet = key[0]
        d: set[tuple[str, str]] = set()
        for r in refs_of(ast, values_only=True):
            # deferred cells are IN the dependency set, so the cascade rule sees them
            d.update(c for c in expand(r, sheet) if c in known)
        deps[key] = d

    order: list[tuple[str, str]] = []
    state: dict[tuple[str, str], int] = {}

    def visit(k: tuple[str, str], stack: set[tuple[str, str]]) -> bool:
        if state.get(k) == 2:
            return True
        if k in stack:
            return False
        stack.add(k)
        ok = True
        for d in deps.get(k, ()):
            if d in not_run and d not in parsed:
                continue  # a declared deferral: handled by the cascade rule below
            if not visit(d, stack):
                not_run.setdefault(d, "cycle: circular reference")
                ok = False
        stack.discard(k)
        if ok:
            state[k] = 2
            order.append(k)
        else:
            not_run.setdefault(k, "cycle: circular reference")
        return ok

    for k in parsed:
        visit(k, set())

    values: dict[tuple[str, str], Value] = dict(literals)
    computed: set[tuple[str, str]] = set()

    def get(sheet: str, ref: str) -> Any:
        return values.get((sheet, ref))

    for key in order:
        if key in not_run:
            continue
        # THE CASCADE RULE, and it is the defect this evaluator was caught committing.
        # `A13 = A12+1` where A12 is NOT_RUN read the missing precursor as 0 and returned
        # a clean 1 where the answer was 9. A number computed from an input that did not
        # run is a clean confident wrong answer — the exact thing this system exists to
        # refuse — so it does not run either, and it names the input.
        blocked = sorted(d for d in deps.get(key, ()) if d in not_run)
        if blocked:
            first = blocked[0]
            not_run[key] = f"depends on a NOT_RUN cell: {first[0]}!{first[1]}"
            continue
        try:
            values[key] = _eval(parsed[key], key[0], get)
            computed.add(key)
        except Unimplemented as u:
            not_run[key] = str(u)
        except RecursionError:
            not_run[key] = "cycle: recursion limit"
        except (ParseError, ArithmeticError, TypeError, ValueError, KeyError, IndexError) as e:
            not_run[key] = f"eval: {type(e).__name__}: {e}"

    for key in not_run:
        values.pop(key, None)

    return ValueGrid(
        values=values,
        not_run=not_run,
        computed_cells=frozenset(computed),
        formula_source=formula_source,
    )
