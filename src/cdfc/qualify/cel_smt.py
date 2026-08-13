"""P7-B3 — the CEL → SMT-LIB translator, over the ADMITTED SUBSET ONLY.

**Why it is tractable.** The construct that looks hard is the comprehension, and it is not: the row
count of every table is a property of the pinned blank, so `t.rows.all(r, φ(r))` compiles to a
finite unrolling `⋀_{i<N} φ(r_i)` — a conjunction, not a quantifier. That is why Z3 decides these.

**The single-row abstraction, and exactly how far it is sound.** If `¬φ(r)` is UNSAT for a
*symbolic* row `r`, it is UNSAT for every unrolling. So the shortcut is sound for `trivially_true`
and for `always_flag`. **It is NOT sound for `redundant`**, because subsumption can couple rows
across predicates, and `g3_degeneracy` does not use it there — asserted on the call path by
`test_smt__abstraction_is_not_used_for_subsumption`.

**A construct outside the admitted subset returns `None`, and `None` becomes `UNKNOWN`, and
`UNKNOWN` is UNPROVEN — never `non_degenerate`.** The switch trigger the plan states in advance
applies: *narrow the admitted subset rather than widening the translator.* This translator covers
integer arithmetic, comparison, boolean structure, `has()`, and `.all()` with a symbolic row. It
does NOT cover strings, `in`, or host functions, and every one of those routes to the empirical
arm rather than to a proof nobody can check.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

import lark

# **THE GRAMMAR'S SHAPE, WRITTEN DOWN BECAUSE IT IS NOT THE OBVIOUS ONE.** `celpy`'s lark grammar
# encodes a binary operator by giving the PARENT two children, where the FIRST is the operator node
# WRAPPING THE LEFT OPERAND and the second is the right operand:
#
#     relation(2)   -> [ relation_ge(1) -> [lhs] , rhs ]
#     addition(2)   -> [ addition_sub(1) -> [lhs] , rhs ]
#     conditionaland(2) -> [ conditionaland(1) -> [lhs] , rhs ]      -- `&&` is the only operator here
#
# A translator written against the shape the pretty-printer SUGGESTS — operator node holding both
# operands — silently returns `None` for every expression, which reads as "outside the admitted
# subset" and routes 349 predicates to the empirical arm. That is a proof arm that cannot fail,
# and it is why the first version of this module was wrong in the direction that hides itself.

_TRANSPARENT: Final[frozenset[str]] = frozenset(
    {"expr", "conditionalor", "conditionaland", "relation", "addition", "multiplication",
     "unary", "member", "primary",
     # `paren_expr` is grouping and nothing else: `(a + b)` must translate as `a + b`. It is
     # listed EXPLICITLY rather than by "any node with one child" for the reason
     # `cel_profile._TRANSPARENT` records — `list` and `map_lit` also have one child, and the
     # permissive form walked straight through a list literal.
     "paren_expr"}
)

_REL: Final[Mapping[str, str]] = {
    "relation_le": "<=", "relation_lt": "<", "relation_ge": ">=", "relation_gt": ">",
    "relation_eq": "==", "relation_ne": "!=",
}


class Untranslatable(Exception):
    """A construct outside the admitted subset. Caught by `translate`, which returns None."""


def _unwrap(node: Any) -> Any:
    while isinstance(node, lark.Tree) and str(node.data) in _TRANSPARENT and len(node.children) == 1:
        node = node.children[0]
    return node


def _op_and_operands(node: lark.Tree) -> tuple[str, Any, Any]:
    """`(operator node name, lhs, rhs)` for a two-child binary node."""
    head, rhs = node.children[0], node.children[1]
    if not isinstance(head, lark.Tree) or not head.children:
        raise Untranslatable(f"{node.data}: malformed binary node")
    return str(head.data), head.children[0], rhs


def _path_of(node: Any) -> str | None:
    """`filing.a.b.v` from a chain of `member_dot`s, or None."""
    node = _unwrap(node)
    parts: list[str] = []
    while isinstance(node, lark.Tree) and str(node.data) == "member_dot":
        kids = list(node.children)
        parts.append(str(kids[-1]))
        node = _unwrap(kids[0])
    if isinstance(node, lark.Tree) and str(node.data) == "ident":
        parts.append(str(node.children[0]))
    elif isinstance(node, lark.Token):
        parts.append(str(node))
    else:
        return None
    return ".".join(reversed(parts))


class Translator:
    """CEL -> z3 over linear integer arithmetic. One instance per expression."""

    def __init__(self) -> None:
        import z3

        self._z3 = z3
        self.ints: dict[str, Any] = {}
        self.bools: dict[str, Any] = {}

    def var(self, path: str) -> Any:
        if path not in self.ints:
            self.ints[path] = self._z3.Int(path)
        return self.ints[path]

    def presence(self, path: str) -> Any:
        if path not in self.bools:
            self.bools[path] = self._z3.Bool(f"has({path})")
        return self.bools[path]

    # -- boolean ---------------------------------------------------------------------------

    def boolean(self, node: Any) -> Any:
        z3 = self._z3
        node = _unwrap(node)
        if isinstance(node, lark.Token):
            t = str(node)
            if t in ("true", "false"):
                return z3.BoolVal(t == "true")
            raise Untranslatable(f"token {t!r}")
        if not isinstance(node, lark.Tree):
            raise Untranslatable(repr(node))
        data = str(node.data)

        if data == "conditionalor" and len(node.children) == 2:
            _op, lhs, rhs = _op_and_operands(node)
            return z3.Or(self.boolean(lhs), self.boolean(rhs))
        if data == "conditionaland" and len(node.children) == 2:
            _op, lhs, rhs = _op_and_operands(node)
            return z3.And(self.boolean(lhs), self.boolean(rhs))
        if data == "relation" and len(node.children) == 2:
            op, lhs, rhs = _op_and_operands(node)
            if op not in _REL:
                raise Untranslatable(f"relation {op}")
            a, b = self.arith(lhs), self.arith(rhs)
            return {
                "relation_le": lambda: a <= b, "relation_lt": lambda: a < b,
                "relation_ge": lambda: a >= b, "relation_gt": lambda: a > b,
                "relation_eq": lambda: a == b, "relation_ne": lambda: a != b,
            }[op]()
        if data == "unary_not":
            return z3.Not(self.boolean(node.children[-1]))
        if data == "literal":
            t = str(node.children[0])
            if t in ("true", "false"):
                return z3.BoolVal(t == "true")
            raise Untranslatable(f"literal {t!r} in a boolean position")
        if data == "ident_arg":
            return self._ident_call(node)
        if data == "member_dot_arg":
            return self._macro(node)
        raise Untranslatable(data)

    def _ident_call(self, node: lark.Tree) -> Any:
        """`has(x)`. Nothing else is a translatable free function."""
        name = str(node.children[0])
        if name != "has":
            raise Untranslatable(f"call {name!r}")
        p = _path_of(_first_expr(node.children[-1]))
        if p is None:
            raise Untranslatable("has() over a non-path")
        return self.presence(p)

    def _macro(self, node: lark.Tree) -> Any:
        """`xs.all(v, phi)` under THE SINGLE-ROW ABSTRACTION.

        `xs.all(v, phi(v))` becomes `phi(row)` for one symbolic row. Sound for `trivially_true` and
        `always_flag` — if `not phi(r)` is UNSAT for a symbolic `r` it is UNSAT for every unrolling
        — and NOT used for `redundant`, because subsumption can couple rows across predicates.
        """
        name = str(node.children[1])
        if name != "all":
            raise Untranslatable(f"macro {name!r}")
        args = node.children[-1]
        exprs = [c for c in getattr(args, "children", []) if isinstance(c, lark.Tree)]
        if len(exprs) < 2:
            raise Untranslatable("all() with no body")
        return self.boolean(exprs[-1])

    # -- arithmetic ------------------------------------------------------------------------

    def arith(self, node: Any) -> Any:
        node = _unwrap(node)
        if isinstance(node, lark.Token):
            return self._literal(str(node))
        if not isinstance(node, lark.Tree):
            raise Untranslatable(repr(node))
        data = str(node.data)
        if data == "literal":
            return self._literal(str(node.children[0]))
        if data == "addition" and len(node.children) == 2:
            op, lhs, rhs = _op_and_operands(node)
            if op == "addition_add":
                return self.arith(lhs) + self.arith(rhs)
            if op == "addition_sub":
                return self.arith(lhs) - self.arith(rhs)
            raise Untranslatable(op)
        if data == "multiplication" and len(node.children) == 2:
            op, lhs, rhs = _op_and_operands(node)
            if op == "multiplication_mul":
                return self.arith(lhs) * self.arith(rhs)
            raise Untranslatable(op)  # division is not in the LIA fragment
        if data == "unary_neg":
            return -self.arith(node.children[-1])
        if data == "ident":
            return self.var(str(node.children[0]))
        p = _path_of(node)
        if p is not None:
            return self.var(p)
        raise Untranslatable(f"arith {data}")

    def _literal(self, text: str) -> Any:
        t = text.strip()
        if t.startswith('"') or t.startswith("'"):
            raise Untranslatable("string literal - strings are outside the LIA fragment")
        try:
            if "." in t or "e" in t.lower():
                # A decimal literal in a money predicate is an INTEGER count of 10^-3 USD Million
                # by R4; a fractional part here means the expression left the integer core, and
                # guessing a rounding would be inventing the predicate.
                as_float = float(t)
                if as_float != int(as_float):
                    raise Untranslatable(f"non-integral literal {t!r}")
                return self._z3.IntVal(int(as_float))
            return self._z3.IntVal(int(t))
        except (ValueError, OverflowError) as e:
            raise Untranslatable(f"literal {t!r}") from e


def _first_expr(args: Any) -> Any:
    for c in getattr(args, "children", []):
        if isinstance(c, lark.Tree):
            return c
    return args


def translate(source: str, *, slot: str = "expr") -> tuple[Any, Translator] | None:
    """`(z3 formula, translator)` or **None** when the expression leaves the admitted subset.

    None is not a failure to be repaired: it is the honest report that this expression cannot be
    decided by proof, and `g3_degeneracy` turns it into `UNKNOWN`, which is UNPROVEN.
    """
    from cdfc.predicates.cel_profile import parse

    try:
        tree = parse(source, slot=slot)  # type: ignore[arg-type]
        t = Translator()
        return t.boolean(tree), t
    except Untranslatable:
        return None
    except Exception:  # noqa: BLE001 - a parser or z3 error is also "cannot decide by proof"
        return None
