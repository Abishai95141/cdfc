"""ONE patcher for the fact tree, shared by the campaign and the canary loop.

**Why it is one module and not two functions that look alike.** P6's campaign patches a clean fact
tree per mutant to decide what each predicate killed; P10's canary loop patches the same tree per
witness to decide whether each predicate *still* kills it. If the two patchers differ, "the
predicate caught the fault it was admitted for" is not what the canary tests — it tests whether two
implementations of the same idea agree, and they will not.

---

## `None` IS NOT A VALUE, AND THE STRING `"None"` IS A FALSE KILL

**Found by the canary loop replaying the committed campaign, 14 August 2026.** `facts/build._coerce`
begins `text = str(raw)`. Called with `None` it returns the four-character string `"None"`, and
`p6_kill._patch` called it with exactly that: `recalculate` returns `None` for a formula cell whose
input has been blanked, and every such cell entered the mutant's fact tree as `"None"`.

The consequence, measured on mutant `edfc99e6` (`F05.b`, blank `'1. Introduction'!D11`):

    filing.n_1_introduction.r11.cd.v  ->  ''        (the blanked cell, patched with "")
    filing.n_1_introduction.r40.cd.v  ->  'None'    (D40 = D11, uncomputable, coerced)

`P-0012` is `r40.cd.v == r11.cd.v`. Its recorded kill is `'' == 'None'` returning false. **The
predicate did not catch the fault; it compared two coercion artifacts.** Neither key could be
type-inferred from the AST, so pre-flight was presence-only by D-P5-03 and let it through — working
exactly as designed, on a fact tree that should never have existed.

> **RULING.** A cell with no value is **ABSENT**, exactly as `filing_tree` leaves it — that module's
> own rule is *"A blank NUMERIC cell is ABSENT, not zero … there is no integer that means empty"*,
> and there is no string that means it either. `_coerce(None)` now **raises**, so the defect is
> unrepresentable rather than discouraged, and the two callers that could produce it route through
> `ABSENT` here.
>
> What this costs is real and it is the honest direction: an equality predicate over a blanked cell
> now reports `NOT_RUN(source_unreadable)` instead of `FAIL`, so **`K` falls**. A kill that rests on
> `'' == 'None'` was never evidence that the check works.
"""

from __future__ import annotations

from cdfc.schema.anchor import Anchor

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final


class _Absent:
    """The cell has no value. Distinct from `""`, from `0`, and from the string `"None"`."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return "ABSENT"

    def __bool__(self) -> bool:
        return False


ABSENT: Final[_Absent] = _Absent()

# The key a leaf carries. Patching walks on THIS rather than on a dotted path, and that is what
# makes it exact for both node shapes: a scalar cell node and an element of a data-validation range
# node carry the same `__cell__`, and a patch that reached only the first would leave a membership
# predicate reading the pre-fault value out of the range it binds.
CELL: Final[str] = "__cell__"


def value_for(raw: Any) -> Any:
    """A recalculated or extracted value, as the fact model's own value — or `ABSENT`.

    `None` and `""` both mean *this cell carries nothing*, which is what a blanked cell and an
    uncomputable cell both are. `filing_tree` expresses that by never inserting the key.
    """
    from cdfc.facts.build import _coerce

    if raw is None or raw is ABSENT or raw == "":
        return ABSENT
    return _coerce(raw)


@dataclass(frozen=True, slots=True)
class CellIndex:
    """Where a cell's node BELONGS, for the cells the filing does not carry.

    Built once from the pinned template's context, never from the filing — a filer who leaves a
    cell blank must not thereby remove it from the model, which is the whole reason a fault that
    WRITES into a blank cell has to be expressible.
    """

    scalar: Mapping[str, str]                  # "Sheet!Ref" -> dotted path of the cell node
    ranges: Mapping[str, tuple[str, ...]]      # "Sheet!Ref" -> dotted paths of the range nodes

    @staticmethod
    def of(ctx: Any) -> "CellIndex":
        from cdfc.predicates.harvest import cel_path, expand, range_path

        scalar = {Anchor.cell(s, r).render(): cel_path(s, r) for (s, r) in ctx.key_of}
        ranges: dict[str, list[str]] = {}
        for sheet, dvs in ctx.validations_by_sheet.items():
            for dv in dvs:
                if not dv.sqref.split():
                    continue
                path = range_path(sheet, dv.sqref)
                for part in dv.sqref.split():
                    for ref in expand(part.replace("$", "")):
                        ranges.setdefault(Anchor.cell(sheet, ref).render(), []).append(path)
        return CellIndex(scalar=scalar, ranges={k: tuple(v) for k, v in ranges.items()})


def patch(
    tree: Mapping[str, Any], patches: Mapping[str, Any], *, index: CellIndex | None = None
) -> dict[str, Any]:
    """A deep copy of `tree` with every `__cell__`-named leaf rewritten.

    `patches` maps `"Sheet!Ref"` to a fact-model value or to `ABSENT`. An `ABSENT` patch **deletes
    the leaf's `v`**, leaving the node with its `__cell__` and nothing else — which is what
    `filing_tree` produces for a cell the workbook does not carry, so `FactSet.has()` reports the
    key missing and pre-flight refuses to run the predicate over it.

    **With an `index`, a patch may also CREATE a node the filing does not carry**, and without that
    a whole class of fault is silently unappliable. `filing_tree` inserts a cell only when the
    workbook carries a value for it, so on a sparsely-filled filing the node for a blank cell does
    not exist — and a fault whose whole content is *the filer wrote the wrong number into this
    empty cell* had nothing to rewrite. Measured: on `formula-overwritten__portfolio-O7.xlsx`, 20
    of 33 canaries went silent because their witness landed on a cell whose node was absent, and
    the loop read that as *the check is dead*. It is not: the fault had not been applied.

    The input is not mutated. `test_patch__the_input_tree_is_unchanged` asserts it by identity.
    """
    seen: set[str] = set()
    out = _walk(tree, patches, seen)
    if index is None:
        return out
    for cell in sorted(set(patches) - seen):
        value = patches[cell]
        if value is ABSENT:
            continue            # a cell that is absent and stays absent needs no node
        dotted = index.scalar.get(cell)
        if dotted is not None:
            _insert(out, dotted, value, cell)
        for path in index.ranges.get(cell, ()):
            node = _node_at(out, path)
            cells = node.setdefault("cells", [])
            if not any(c.get(CELL) == cell for c in cells):
                cells.append({"v": value, CELL: cell})
                # Sorted so the tree is a function of the patch set and not of iteration order:
                # a fact tree whose element order depends on `dict` ordering is a run whose
                # bytes cannot be re-derived.
                cells.sort(key=lambda c: str(c.get(CELL)))
    return out


def _node_at(tree: dict[str, Any], dotted: str) -> dict[str, Any]:
    node: Any = tree
    for seg in dotted.split("."):
        nxt = node.get(seg)
        if not isinstance(nxt, dict):
            nxt = {}
            node[seg] = nxt
        node = nxt
    return node


def _insert(tree: dict[str, Any], dotted: str, value: Any, cell: str) -> None:
    node = _node_at(tree, dotted)
    node["v"] = value
    node[CELL] = cell


def _walk(node: Any, patches: Mapping[str, Any], seen: set[str]) -> Any:
    if isinstance(node, Mapping):
        out: dict[str, Any] = {k: _walk(v, patches, seen) for k, v in node.items()}
        cell = node.get(CELL)
        if isinstance(cell, str) and cell in patches:
            seen.add(cell)
            new = patches[cell]
            if new is ABSENT:
                out.pop("v", None)
            else:
                out["v"] = new
        return out
    if isinstance(node, (list, tuple)):
        return [_walk(v, patches, seen) for v in node]
    return node
