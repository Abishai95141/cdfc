"""P4-B2 — static key extraction over the admitted CEL subset.

**This module is what makes the settled fraction derivable rather than estimated.** You cannot
statically determine which fields a Python function reads, so a coverage claim over Python
predicates is an inference. Over CEL it is a computation — but only if the extraction is *sound*,
and soundness is the whole content of this file.

**Comprehension binding is where a lexical implementation dies.** In

    filing.intro.tbl15.rows.all(r, r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)

the keys read are `filing.intro.tbl15.rows[*].scheme_type` and `template.vocab.scheme_type`.
**`r` is not a key.** A regex over the source reports `r.scheme_type` as a root and misses the
`[*]` — the same defect class as `<f[ >][^>]*>` over OOXML one level up, which in this project
returned a *correct count* with *wrong bodies*. Hence `ci/no-regex-over-cel.sh`.

**The both-ways check.** `check_declared_keys` compares the union of the three slots' read sets
against `schema_keys`, in both directions, and the two failures are **different exception types
because they have different remedies** — see `errors.py`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Literal

import lark

from cdfc.predicates.cel_profile import (
    ADMITTED_HOST_FNS,
    BOUND_ROOTS,
    Slot,
    _macro_of,
    _unwrap,
    parse,
)
from cdfc.predicates.errors import (
    DeclaredKeyUnread,
    KeyGrammarError,
    UndeclaredKeyRead,
    UnresolvableMemberBase,
)

def _is_path_shaped(node: object) -> bool:
    """Is this expression a dotted path — a name, or a chain of `.field` / `[i]` from one?

    The distinction decides WHICH refusal a member access gets, and both must stay available.

    - `prior.x.y` IS path-shaped. It fails because `prior` is a third free root, and
      `check_subset` reports exactly that — P9's un-runnable R-07 depends on the accurate message.
    - `(filing.a).b` and `(c ? p : q).z` are NOT. Their base is an expression the walker cannot
      resolve, and recording only the inner path made the static read set smaller than the
      runtime's — the truncation that let a predicate PASS over an unchecked key.

    Collapsing the two would replace an accurate diagnosis with a vaguer one.
    """
    n = _unwrap(node)  # type: ignore[arg-type]
    if not isinstance(n, lark.Tree):
        return False
    data = str(n.data)
    if data == "ident":
        return True
    if data in ("member_dot", "member_index"):
        return _is_path_shaped(n.children[0])
    return False


Root = Literal["filing", "template"]
TypeHint = Literal["STRING", "INT", "LIST", "BOOL", "DATE"]

REPEATED: Final[str] = "[*]"
_SEGMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class KeyRef:
    """One key, in D-P4-02's grammar: root included, `[*]` for a repeated node."""

    root: Root
    path: tuple[str, ...]
    repeated_at: tuple[int, ...] = ()
    offset: int = 0

    def dotted(self) -> str:
        out: list[str] = [self.root]
        for i, seg in enumerate(self.path):
            out.append(seg + (REPEATED if i in self.repeated_at else ""))
        return ".".join(out)

    @staticmethod
    def parse(dotted: str) -> KeyRef:
        parts = dotted.split(".")
        if len(parts) < 2 or parts[0] not in BOUND_ROOTS:
            raise KeyGrammarError(
                f"{dotted!r} does not name a document. D-P4-02: a key that cannot say WHICH "
                "document it read cannot express a vocabulary resolved from the filing."
            )
        path: list[str] = []
        repeated: list[int] = []
        for i, raw in enumerate(parts[1:]):
            seg = raw
            if seg.endswith(REPEATED):
                seg = seg[: -len(REPEATED)]
                repeated.append(i)
            if not _SEGMENT.match(seg):
                raise KeyGrammarError(f"{dotted!r}: segment {raw!r} is not a lawful identifier")
            path.append(seg)
        return KeyRef(root=parts[0], path=tuple(path), repeated_at=tuple(repeated))  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class _Path:
    """A resolved path under construction, or a comprehension binding's expansion."""

    root: Root
    segs: tuple[str, ...]
    repeated: tuple[int, ...]

    def extend(self, seg: str) -> _Path:
        return _Path(self.root, (*self.segs, seg), self.repeated)

    def repeat(self) -> _Path:
        """Mark the LAST segment as repeated: the binding ranges over its elements."""
        if not self.segs:
            raise KeyGrammarError("a comprehension over a document root has no repeated node")
        return _Path(self.root, self.segs, (*self.repeated, len(self.segs) - 1))

    def to_ref(self, offset: int) -> KeyRef:
        return KeyRef(self.root, self.segs, self.repeated, offset)


@dataclass(frozen=True, slots=True)
class WalkResult:
    keys: frozenset[str]
    host_fns: frozenset[str]
    refs: tuple[KeyRef, ...]
    types: Mapping[str, TypeHint | None]


class _Walker:
    def __init__(self) -> None:
        self.reads: dict[str, KeyRef] = {}
        self.host_fns: set[str] = set()
        self.types: dict[str, TypeHint | None] = {}

    # -- reading ---------------------------------------------------------------------
    def _record(self, path: _Path, offset: int) -> None:
        ref = path.to_ref(offset)
        self.reads.setdefault(ref.dotted(), ref)

    def _hint(self, path: _Path | None, hint: TypeHint) -> None:
        if path is None:
            return
        key = path.to_ref(0).dotted()
        # Two incompatible hints for one key means the AST cannot decide, and D-P5-03 says a key
        # whose type cannot be inferred is PRESENCE-CHECKED ONLY. `None` is that state, and it is
        # recorded rather than defaulted, so the run can publish keys_type_checked/keys_preflighted.
        if key in self.types and self.types[key] != hint:
            self.types[key] = None
        else:
            self.types.setdefault(key, hint)

    # -- resolution ------------------------------------------------------------------
    def resolve(self, node: lark.Tree | lark.Token, env: Mapping[str, _Path]) -> _Path | None:
        """The path this expression names, or None if it is not a path expression."""
        node = _unwrap(node)
        if isinstance(node, lark.Token):
            return None
        data = str(node.data)

        if data == "ident":
            name = str(node.children[0])
            if name in env:
                return env[name]
            if name in BOUND_ROOTS:
                return _Path(name, (), ())  # type: ignore[arg-type]
            return None

        if data == "member_dot":
            base = self.resolve(node.children[0], env)
            if base is None and not _is_path_shaped(node.children[0]):
                # **AN UNRESOLVABLE BASE IS A REFUSAL, NEVER A SILENT TRUNCATION.**
                #
                # `(filing.a).b` parses as `member_dot(paren_expr(...), 'b')`. Returning `None`
                # here made `walk` fall through and record only the INNER path `filing.a`, so the
                # static read set was strictly SMALLER than the runtime's. `check_declared_keys`
                # then agreed both ways — the declaration matched the (truncated) static set —
                # pre-flight guarded a key that was never read, `filing.a.b` was never checked for
                # presence, and the predicate reached `PASS`. One pair of parentheses was the
                # whole difference between `UndeclaredKeyRead` and a clean pass.
                #
                # It is the exact defect `preflight.py`'s claim — *"the declared set IS the read
                # set"* — exists to make impossible, and both existing controls were blind: the
                # differential's CASES list and the property test's generator contain no
                # parentheses.
                #
                # Recovering the path where it is recoverable would fix `(filing.a).b` and leave
                # `(cond ? p : q).z`, which is not statically resolvable at all. So the rule is
                # the subset's rule: a construct that defeats static key recovery is not admitted.
                raise UnresolvableMemberBase(
                    "a member access whose base is not a statically resolvable path — e.g. "
                    "`(filing.a).b` or `(cond ? p : q).z`. The admitted subset exists so that the "
                    "key set a predicate reads can be determined STATICALLY; a base the walker "
                    "cannot resolve makes the read set larger than anything it can declare, and "
                    "pre-flight would guard a key the runtime does not read. Write the path "
                    "without parentheses."
                )
            # An unresolved plain IDENTIFIER is a different refusal and keeps its own message: it
            # is a third free root, which `check_subset` already reports as such — `prior.x` in
            # P9's un-runnable R-07, for instance. Collapsing the two would replace an accurate
            # diagnosis with a vaguer one.
            return None if base is None else base.extend(str(node.children[1]))

        if data == "member_index":
            base = self.resolve(node.children[0], env)
            if base is None:
                return None
            idx = _unwrap(node.children[1])
            if isinstance(idx, lark.Tree) and str(idx.data) == "literal":
                tok = idx.children[0]
                if isinstance(tok, lark.Token) and tok.type == "STRING_LIT":
                    # `a["b"]` normalises to `a.b`: one grammar, so two spellings of one key
                    # cannot both be declared and both be counted.
                    return base.extend(str(tok)[1:-1])
            raise KeyGrammarError(
                "an index that is not a string literal defeats static key extraction; "
                "write the segment out"
            )

        macro = _macro_of(node)
        if macro is not None and macro[1] is not None:
            # A comprehension RETURNS its collection, so `filter(...).map(...)` chains resolve.
            return self.resolve(node.children[0], env)
        return None

    # -- the walk --------------------------------------------------------------------
    def walk(self, node: lark.Tree | lark.Token, env: Mapping[str, _Path]) -> None:
        if isinstance(node, lark.Token):
            return
        data = str(node.data)

        macro = _macro_of(node)
        if macro is not None and macro[1] is not None:
            name, binding, body = macro
            target = self.resolve(node.children[0], env)
            if target is None:
                raise KeyGrammarError(
                    f"{name}() is applied to something that is not a declared path; a "
                    "comprehension over an anonymous value cannot be attributed to a key"
                )
            bound_name = str(_unwrap(binding).children[0])  # type: ignore[union-attr]
            inner = dict(env)
            inner[bound_name] = target.repeat()
            before = len(self.reads)
            self.walk(body, inner)  # type: ignore[arg-type]
            if len(self.reads) == before:
                # The body read nothing through the binding, but the collection was still read.
                # Reporting nothing here would understate the footprint.
                self._record(target, _pos(node))
            # The TARGET is deliberately not recorded as a key of its own when the body read
            # through it: `filing.rows[*].x` already says the collection was traversed, and
            # reporting `filing.rows` beside it would double-count the footprint and put a
            # container into the pre-flight set that no predicate reads as a value.
            #
            # It IS walked when it is itself a comprehension, because a `filter(...).map(...)`
            # chain reads keys in the filter's body that appear nowhere else.
            inner_target = _unwrap(node.children[0])
            if isinstance(inner_target, lark.Tree) and _macro_of(inner_target) is not None:
                self.walk(node.children[0], env)
            return

        if data in ("ident", "member_dot", "member_index"):
            path = self.resolve(node, env)
            if path is not None:
                if path.segs:
                    self._record(path, _pos(node))
                return
            # not a path: fall through and walk the children
        if data == "ident_arg":
            fname = str(node.children[0])
            if fname in ADMITTED_HOST_FNS:
                self.host_fns.add(fname)
            for child in node.children[1:]:
                self.walk(child, env)
            return

        if data == "relation" and len(node.children) == 2:
            self._infer_relation(node, env)

        for child in node.children:
            self.walk(child, env)

    # -- D-P5-03 type inference ------------------------------------------------------
    def _infer_relation(self, node: lark.Tree, env: Mapping[str, _Path]) -> None:
        op_node = node.children[0]
        rhs = node.children[1]
        if not isinstance(op_node, lark.Tree):
            return
        op = str(op_node.data)
        lhs = op_node.children[0] if op_node.children else None
        lpath = self.resolve(lhs, env) if lhs is not None else None
        rpath = self.resolve(rhs, env)

        if op == "relation_in":
            self._hint(lpath, "STRING")
            self._hint(rpath, "LIST")
            return
        rhs_u = _unwrap(rhs)
        lhs_u = _unwrap(lhs) if lhs is not None else None
        for path, other in ((lpath, rhs_u), (rpath, lhs_u)):
            if path is None or other is None or isinstance(other, lark.Token):
                continue
            if str(other.data) == "literal":
                tok = other.children[0]
                if isinstance(tok, lark.Token):
                    if tok.type == "STRING_LIT":
                        self._hint(path, "STRING")
                    elif tok.type == "INT_LIT":
                        self._hint(path, "INT")
            elif str(other.data) in ("addition", "multiplication"):
                self._hint(path, "INT")
        if op in ("relation_lt", "relation_le", "relation_gt", "relation_ge"):
            self._hint(lpath, "INT")
            self._hint(rpath, "INT")


def _pos(node: object) -> int:
    if isinstance(node, lark.Token):
        return int(node.start_pos or 0)
    meta = getattr(node, "meta", None)
    return int(getattr(meta, "start_pos", 0) or 0)


def walk_source(source: str, *, slot: Slot) -> WalkResult:
    w = _Walker()
    w.walk(parse(source, slot=slot), {})
    return WalkResult(
        keys=frozenset(w.reads),
        host_fns=frozenset(w.host_fns),
        refs=tuple(w.reads.values()),
        types=dict(w.types),
    )


def read_keys(source_or_ast: str | lark.Tree, *, slot: Slot = "expr") -> frozenset[str]:
    """The keys this expression reads. Comprehension-bound names are RESOLVED, never reported."""
    if isinstance(source_or_ast, str):
        return walk_source(source_or_ast, slot=slot).keys
    w = _Walker()
    w.walk(source_or_ast, {})
    return frozenset(w.reads)


def called_host_fns(source_or_ast: str | lark.Tree, *, slot: Slot = "expr") -> frozenset[str]:
    if isinstance(source_or_ast, str):
        return walk_source(source_or_ast, slot=slot).host_fns
    w = _Walker()
    w.walk(source_or_ast, {})
    return frozenset(w.host_fns)


def inferred_types(source: str, *, slot: Slot = "expr") -> Mapping[str, TypeHint | None]:
    """D-P5-03. `None` means ambiguous, and a key with an ambiguous type is presence-checked only."""
    return walk_source(source, slot=slot).types


def slots_of(c: object) -> tuple[tuple[Slot, str], ...]:
    return (
        ("applicable", getattr(c, "applicable")),
        ("expr", getattr(c, "expr")),
        ("witness", getattr(c, "witness")),
    )


def all_read_keys(c: object) -> frozenset[str]:
    """The union over the three slots. This is the set `schema_keys` is compared against."""
    out: set[str] = set()
    for slot, src in slots_of(c):
        out |= walk_source(src, slot=slot).keys
    return frozenset(out)


def check_declared_keys(c: object) -> None:
    """The both-ways check. Raises `UndeclaredKeyRead` or `DeclaredKeyUnread`, never one type."""
    declared = frozenset(getattr(c, "schema_keys"))
    for k in declared:
        KeyRef.parse(k)  # a declared key must be writable in the grammar
    read = all_read_keys(c)
    pid = str(getattr(c, "id", "<no id>"))
    undeclared = tuple(sorted(read - declared))
    if undeclared:
        raise UndeclaredKeyRead(pid, undeclared)
    unread = tuple(sorted(declared - read))
    if unread:
        raise DeclaredKeyUnread(pid, unread)


def all_called_host_fns(c: object) -> frozenset[str]:
    out: set[str] = set()
    for slot, src in slots_of(c):
        out |= walk_source(src, slot=slot).host_fns
    return frozenset(out)


# --- cells_bound --------------------------------------------------------------------


class TemplateSchema:
    """The pinned blank's key → cell mapping. Built by the harvest from the template, never
    from a filing: a vocabulary or a cell set resolved from the filed artifact is NC-D01c."""

    def __init__(self, key_to_cells: Mapping[str, frozenset[str]], template_sha256: str) -> None:
        self._cells = dict(key_to_cells)
        self.template_sha256 = template_sha256

    def cells_for(self, key: str) -> frozenset[str]:
        return self._cells.get(key, frozenset())

    def keys(self) -> frozenset[str]:
        return frozenset(self._cells)


def bound_cells(c: object, schema: TemplateSchema) -> frozenset[str]:
    """A static UPPER BOUND on the cells this predicate settles.

    Only `filing`-rooted keys contribute: a template vocabulary is not a cell of the artifact
    under check, and counting it would inflate `cells_bound` with cells no filer wrote.

    The union — not the intersection. An intersection written here would make `cells_bound`
    under-report and turn real predicates into `ERROR(cells_bound_zero)`, which is why
    `test_prop__bound_cells_is_monotone_in_the_key_set` exists.
    """
    out: set[str] = set()
    for key in getattr(c, "schema_keys"):
        if KeyRef.parse(key).root != "filing":
            continue
        out |= schema.cells_for(key)
    return frozenset(out)


def declared_vs_read(c: object) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """`(read_but_not_declared, declared_but_not_read)` — for the measurement file's diff column."""
    declared = frozenset(getattr(c, "schema_keys"))
    read = all_read_keys(c)
    return tuple(sorted(read - declared)), tuple(sorted(declared - read))


def observed_key_grammar(keys: Sequence[str]) -> tuple[str, ...]:
    """Round-trip every key through the grammar. A key that does not round-trip is not a key."""
    return tuple(KeyRef.parse(k).dotted() for k in keys)
