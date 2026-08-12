"""P4-B2 — the admitted CEL subset: what a predicate may say, and the sentence it gets if it can't.

**Why a subset at all.** The settled fraction is *derivable* rather than *estimated* only because
the key set a predicate reads can be determined **statically**. Every construct banned below is
banned because it defeats that, because it defeats termination, or because it moves a check
somewhere nobody qualified it. Each ban carries the sentence a predicate author reads, so the
rejection says *why* rather than *no*.

**Two names, and only two.** `filing` and `template`. A third free identifier is a way for a
predicate to read something nobody declared, and it is refused at compile time rather than
discovered at evaluation time.

The parser is `celpy`'s. Nothing here evaluates anything.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from functools import lru_cache
from typing import Final, Literal

import lark

from cdfc.predicates.errors import SubsetViolation

Slot = Literal["applicable", "expr", "witness"]
SLOTS: Final[tuple[Slot, ...]] = ("applicable", "expr", "witness")

# What each slot must return. `witness` returns the list a reader opens; the other two return the
# boolean a verdict is read off. A witness expression in an `expr` slot would make every item
# truthy-by-non-emptiness, which is a PASS produced by the shape of the answer.
SLOT_RETURN: Final[Mapping[Slot, type]] = {"applicable": bool, "expr": bool, "witness": list}

BOUND_ROOTS: Final[frozenset[str]] = frozenset({"filing", "template"})

ADMITTED_OPERATORS: Final[frozenset[str]] = frozenset(
    {"==", "!=", "<", "<=", ">", ">=", "&&", "||", "!", "+", "-", "*", "/", "%", "in", "?:"}
)

ADMITTED_MACROS: Final[frozenset[str]] = frozenset(
    {"all", "exists", "exists_one", "map", "filter", "size", "has"}
)

# Global functions the GRAMMAR admits. Whether each has an implementation with published test
# vectors and a mutation score is the registry's question, asked separately at
# `HostFnRegistry.freeze()`. Two checks, because a name the grammar admits and the registry does
# not is a compile that fails at evaluation time.
ADMITTED_HOST_FNS: Final[frozenset[str]] = frozenset(
    {"sum", "reg_resolves", "gstin_valid", "template_current", "nav_interval"}
)

# Built-in global calls, as distinct from methods.
ADMITTED_GLOBALS: Final[frozenset[str]] = frozenset({"size", "has"})

# Host functions whose declared return is a boolean, so `expr` may end in one.
BOOLEAN_HOST_FNS: Final[frozenset[str]] = frozenset(
    {"reg_resolves", "gstin_valid", "template_current"}
)

BANNED: Final[Mapping[str, str]] = {
    "nested comprehension": (
        "the only route to exponential blow-up the CEL specification itself names. Flatten it, "
        "or split it into two predicates"
    ),
    "filter() outside witness": (
        "a filter in `expr` computes a set and then discards it; the set is what a reader needs, "
        "so it belongs in `witness`"
    ),
    "map() outside sum()": (
        "a mapped list that is not summed has no bearing on a boolean verdict"
    ),
    "matches()": (
        "a format check inside an envelope has no test vectors, no mutation score and no author. "
        "MEASURED: the obvious registration-number regex fires on 87 of 228 live FMEs. Format "
        "checks are host functions, which cannot be registered without published vectors. See "
        "docs/decisions/D-P4-03-no-regex-in-cel.md"
    ),
    "timestamp/duration/now": (
        "CEL binds no clock; every timestamp is an input recorded in the manifest, so that a run "
        "can be re-derived from its own bytes"
    ),
    "type()/dyn()": (
        "both defeat static key extraction, which is what makes the settled fraction derivable "
        "rather than estimated"
    ),
    "bytes/uint/protobuf": (
        "no fact in the model has these types; admitting them admits an unreachable branch"
    ),
    "double literal": (
        "there is no floating point below the money line — money is an int64 count of 10^-3 USD "
        "Million, and a float in a predicate is a tolerance nobody declared"
    ),
    "unbound name": (
        "a predicate binds exactly two names, `filing` and `template`. A third is a way to read "
        "something nobody declared"
    ),
    "unknown method": (
        "not in the admitted macro set {all, exists, exists_one, map, filter}"
    ),
    "unknown function": (
        "not an admitted built-in and not a registered host function"
    ),
    "int64 overflow": (
        "an integer literal outside the int64 range. Money is an int64 count of 10^-3 USD "
        "Million and every quantity in this system is an integer, so a literal this large is "
        "outside the model — and the runtime does not merely reject it, it exhausts memory "
        "trying to represent it"
    ),
    "map literal": (
        "no fact in the model is a map; a constant map inside a predicate is a lookup table "
        "nobody qualified, and it belongs in the template side of the fact model where its "
        "provenance is recorded"
    ),
    "wrong return shape": (
        "the slot's return type is fixed: `applicable` and `expr` return a boolean, `witness` "
        "returns a list. A witness expression in an `expr` slot passes by being non-empty"
    ),
}

_BANNED_CALLS: Final[Mapping[str, str]] = {
    "matches": "matches()",
    "timestamp": "timestamp/duration/now",
    "duration": "timestamp/duration/now",
    "now": "timestamp/duration/now",
    "getDate": "timestamp/duration/now",
    "getFullYear": "timestamp/duration/now",
    "type": "type()/dyn()",
    "dyn": "type()/dyn()",
    "bytes": "bytes/uint/protobuf",
    "uint": "bytes/uint/protobuf",
    "double": "double literal",
}

_BANNED_LITERAL_TOKENS: Final[Mapping[str, str]] = {
    "FLOAT_LIT": "double literal",
    "BYTES_LIT": "bytes/uint/protobuf",
    "UINT_LIT": "bytes/uint/protobuf",
}

_MACRO_NODES: Final[frozenset[str]] = frozenset({"member_dot_arg"})
_COMPREHENSION_MACROS: Final[frozenset[str]] = frozenset({"all", "exists", "exists_one", "map", "filter"})


def _pos(node: object) -> int:
    if isinstance(node, lark.Token):
        return int(node.start_pos or 0)
    meta = getattr(node, "meta", None)
    return int(getattr(meta, "start_pos", 0) or 0)


# The rules lark emits purely to encode operator precedence. A one-child instance of any of
# these carries no meaning and is descended through; anything else is stopped at.
#
# The list is EXPLICIT rather than "any node with one child", and that distinction is not
# cosmetic: `list` and `map_lit` also have exactly one child, so the permissive form walked
# straight through a list literal and reported the shape of its first element. A witness slot
# holding `[filing.a.__cell__]` was then refused for returning a scalar.
_TRANSPARENT: Final[frozenset[str]] = frozenset(
    {"expr", "conditionalor", "conditionaland", "relation", "addition", "multiplication",
     "unary", "member", "primary"}
)


def _unwrap(node: lark.Tree | lark.Token) -> lark.Tree | lark.Token:
    """Descend lark's precedence cascade to the first node that actually says something."""
    while (
        isinstance(node, lark.Tree)
        and str(node.data) in _TRANSPARENT
        and len(node.children) == 1
        and isinstance(node.children[0], lark.Tree)
    ):
        node = node.children[0]
    return node


@lru_cache(maxsize=1)
def _environment() -> object:
    """ONE `celpy.Environment`, built once.

    Not an optimisation, or not only one. `celpy.Environment.__init__` calls
    `sys.setrecursionlimit(2500)` — a process-global mutated on every construction. Building one
    per parse re-set the limit thousands of times per test session and broke Hypothesis, which
    saves and restores it around each example. A library that mutates a global at construction
    time is contained by constructing it once, at import, before anything else has an opinion.
    """
    import celpy

    return celpy.Environment()


# Constructed EAGERLY, at import. Deferring it to the first `parse()` call meant celpy's
# `sys.setrecursionlimit(2500)` fired in the middle of a Hypothesis example, and Hypothesis —
# which saves and restores that limit around each example — failed the test that happened to be
# running. Doing it at import makes the mutation happen once, at a time nothing else owns.
_environment()


def parse(source: str, *, slot: Slot) -> lark.Tree:
    """celpy's parser only. Nothing is evaluated, and no activation is built."""
    if slot not in SLOT_RETURN:
        raise SubsetViolation("unknown slot", slot=str(slot), reason=f"slots are {SLOTS}", offset=0)
    try:
        return _environment().compile(source)  # type: ignore[attr-defined]
    except Exception as e:  # celpy raises CELParseError, but its type is not part of our contract
        raise SubsetViolation(
            "unparseable", slot=slot, reason=f"celpy could not parse it: {e}", offset=0
        ) from e


def _macro_of(node: lark.Tree) -> tuple[str, lark.Tree | None, lark.Tree | None] | None:
    """`(method_name, binding_ident_tree, body_tree)` for a comprehension macro, else name-only."""
    if node.data not in _MACRO_NODES or len(node.children) < 2:
        return None
    name_tok = node.children[1]
    if not isinstance(name_tok, lark.Token):
        return None
    name = str(name_tok)
    args = node.children[2] if len(node.children) > 2 else None
    if name in _COMPREHENSION_MACROS and isinstance(args, lark.Tree) and args.data == "exprlist":
        if len(args.children) == 2:
            return name, args.children[0], args.children[1]  # type: ignore[return-value]
    return name, None, None


def _iter_children(node: lark.Tree) -> Iterator[lark.Tree | lark.Token]:
    yield from node.children


def check_subset(
    source: str,
    *,
    slot: Slot,
    host_fns: frozenset[str] = ADMITTED_HOST_FNS,
) -> None:
    """Raise `SubsetViolation` unless every construct in `source` is admitted for `slot`.

    `host_fns` is the set of NAMES the grammar may call. It defaults to the profile's own closed
    list; the runtime passes the frozen registry's names so that a call to a function with no
    registered implementation is refused before anything runs.
    """
    tree = parse(source, slot=slot)
    _walk(tree, slot=slot, scope=frozenset(), host_fns=host_fns, in_comprehension=False, in_sum=False)
    _check_return_shape(tree, slot=slot, host_fns=host_fns)


def _ban(key: str, *, slot: Slot, offset: int) -> SubsetViolation:
    return SubsetViolation(key, slot=slot, reason=BANNED[key], offset=offset)


def _walk(
    node: lark.Tree | lark.Token,
    *,
    slot: Slot,
    scope: frozenset[str],
    host_fns: frozenset[str],
    in_comprehension: bool,
    in_sum: bool,
) -> None:
    if isinstance(node, lark.Token):
        return

    if node.data == "literal":
        for tok in node.children:
            if isinstance(tok, lark.Token) and tok.type in _BANNED_LITERAL_TOKENS:
                raise _ban(_BANNED_LITERAL_TOKENS[tok.type], slot=slot, offset=_pos(tok))
            if isinstance(tok, lark.Token) and tok.type == "INT_LIT":
                try:
                    value = int(str(tok), 0)
                except ValueError:
                    value = 0
                if not (-(2**63) <= value < 2**63):
                    raise _ban("int64 overflow", slot=slot, offset=_pos(tok))
        return

    if node.data == "member_object":
        raise _ban("bytes/uint/protobuf", slot=slot, offset=_pos(node))

    if str(node.data) in ("map_lit", "mapinits"):
        raise _ban("map literal", slot=slot, offset=_pos(node))

    if node.data == "ident":
        name = str(node.children[0])
        if name not in BOUND_ROOTS and name not in scope:
            raise SubsetViolation(
                f"unbound name {name!r}", slot=slot, reason=BANNED["unbound name"], offset=_pos(node.children[0])
            )
        return

    if node.data == "ident_arg":
        fname = str(node.children[0])
        offset = _pos(node.children[0])
        if fname in _BANNED_CALLS:
            raise _ban(_BANNED_CALLS[fname], slot=slot, offset=offset)
        if fname not in ADMITTED_GLOBALS and fname not in host_fns:
            raise SubsetViolation(
                f"unknown function {fname!r}", slot=slot, reason=BANNED["unknown function"], offset=offset
            )
        entering_sum = fname == "sum"
        for child in node.children[1:]:
            _walk(child, slot=slot, scope=scope, host_fns=host_fns,
                  in_comprehension=in_comprehension, in_sum=in_sum or entering_sum)
        return

    macro = _macro_of(node)
    if macro is not None:
        name, binding, body = macro
        offset = _pos(node.children[1])
        if name in _BANNED_CALLS:
            raise _ban(_BANNED_CALLS[name], slot=slot, offset=offset)
        if name not in ADMITTED_MACROS:
            raise SubsetViolation(
                f"unknown method {name!r}", slot=slot, reason=BANNED["unknown method"], offset=offset
            )
        if name in _COMPREHENSION_MACROS:
            if in_comprehension:
                raise _ban("nested comprehension", slot=slot, offset=offset)
            if name == "filter" and slot != "witness":
                raise _ban("filter() outside witness", slot=slot, offset=offset)
            if name == "map" and slot != "witness" and not in_sum:
                raise _ban("map() outside sum()", slot=slot, offset=offset)
            if binding is None or body is None:
                raise SubsetViolation(
                    f"{name}() takes a binding and a body", slot=slot,
                    reason="a comprehension without both is not statically analysable", offset=offset,
                )
            bound = str(_unwrap(binding).children[0]) if isinstance(_unwrap(binding), lark.Tree) else str(binding)
            # The target is evaluated in the OUTER scope; only the body sees the binding.
            _walk(node.children[0], slot=slot, scope=scope, host_fns=host_fns,
                  in_comprehension=in_comprehension, in_sum=in_sum)
            _walk(body, slot=slot, scope=scope | {bound}, host_fns=host_fns,
                  in_comprehension=True, in_sum=False)
            return
        # `size`/`has` written in method position; walk the receiver and any args.
        for child in _iter_children(node):
            _walk(child, slot=slot, scope=scope, host_fns=host_fns,
                  in_comprehension=in_comprehension, in_sum=in_sum)
        return

    for child in _iter_children(node):
        _walk(child, slot=slot, scope=scope, host_fns=host_fns,
              in_comprehension=in_comprehension, in_sum=in_sum)


# --- return shape -----------------------------------------------------------------------

_BOOLEAN_NODES: Final[frozenset[str]] = frozenset(
    {"relation", "conditionaland", "conditionalor"}
)
_BOOLEAN_MACROS: Final[frozenset[str]] = frozenset({"all", "exists", "exists_one"})
_LIST_MACROS: Final[frozenset[str]] = frozenset({"map", "filter"})


def _shape(node: lark.Tree | lark.Token, host_fns: frozenset[str]) -> type | None:
    """`bool`, `list`, or None when the shape cannot be determined from the AST alone."""
    node = _unwrap(node)
    if isinstance(node, lark.Token):
        return None
    if node.data == "literal":
        tok = node.children[0]
        if isinstance(tok, lark.Token) and str(tok) in ("true", "false"):
            return bool
        return None
    if node.data in _BOOLEAN_NODES:
        return bool
    if node.data == "unary":
        first = node.children[0]
        if isinstance(first, lark.Tree) and first.data == "unary_not":
            return bool
        return None
    if str(node.data) in ("list", "list_lit", "exprlist"):
        return list
    if node.data == "expr" and len(node.children) == 3:  # ternary: both branches must agree
        a = _shape(node.children[1], host_fns)
        b = _shape(node.children[2], host_fns)
        return a if a is not None and a is b else None
    if node.data == "ident_arg":
        fname = str(node.children[0])
        if fname == "has":
            return bool
        if fname in BOOLEAN_HOST_FNS:
            return bool
        return None
    macro = _macro_of(node)
    if macro is not None:
        name = macro[0]
        if name in _BOOLEAN_MACROS:
            return bool
        if name in _LIST_MACROS:
            return list
    return None


def _check_return_shape(tree: lark.Tree, *, slot: Slot, host_fns: frozenset[str]) -> None:
    want = SLOT_RETURN[slot]
    got = _shape(tree, host_fns)
    if got is None:
        # Undeterminable is not admitted: a slot whose return shape cannot be read off the AST is
        # a slot whose verdict shape is discovered at evaluation time, on live data.
        raise SubsetViolation(
            "wrong return shape", slot=slot,
            reason=BANNED["wrong return shape"] + " — this expression's shape cannot be "
            "determined from the AST at all",
            offset=_pos(tree),
        )
    if got is not want:
        raise SubsetViolation(
            "wrong return shape", slot=slot,
            reason=BANNED["wrong return shape"] + f" — this one returns {got.__name__}",
            offset=_pos(tree),
        )
