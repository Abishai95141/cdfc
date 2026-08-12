#!/usr/bin/env python
"""P4-B3 — a measured mutation score for every host function, from its published vectors.

**Why this exists rather than a placeholder.** `HostFnRegistry.register` refuses a function with no
`mutation_score_json`. If that file said `PENDING: P6`, the check would be satisfied by a string
and the registry's bar would be decoration — the exact shape of defect this project is about,
inside the gate written to prevent it.

P6 builds the full campaign against the *workbooks*. This is much smaller and entirely local: it
mutates each host function's own AST with a fixed operator set and asks whether the **published
vectors** kill the mutant. It is a real number, available now, over the artifact the registry
actually gates on.

**Equivalent mutants are reported, not silently dropped.** A mutant no vector distinguishes is
either a hole in the vectors or a genuinely equivalent program, and the two are told apart by
reading the mutant — so this tool lists them by line and operator instead of quietly raising the
denominator's floor.

    python tools/host_fn_mutation.py            # writes reports/host_fns/<name>.mutation.json
"""

from __future__ import annotations

import ast
import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

OUT_DIR = REPO / "reports" / "host_fns"
HOST_FNS = ("sum", "gstin_valid", "template_current", "nav_interval", "reg_resolves")
MODULES = {
    "sum": ("cdfc.predicates.host_fns.sum_units", "sum_units"),
    "gstin_valid": ("cdfc.predicates.host_fns.gstin_valid", "gstin_valid"),
    "template_current": ("cdfc.predicates.host_fns.template_current", "template_current"),
    "nav_interval": ("cdfc.predicates.host_fns.nav_interval", "nav_interval"),
    "reg_resolves": ("cdfc.predicates.host_fns.reg_resolves", "reg_resolves"),
}

_CMP_FLIP = {
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.Lt: ast.GtE, ast.GtE: ast.Lt,
    ast.Gt: ast.LtE, ast.LtE: ast.Gt,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
}
_BIN_SWAP = {
    ast.Add: ast.Sub, ast.Sub: ast.Add,
    ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult,
    ast.Mod: ast.FloorDiv,
}
_BOOL_FLIP = {ast.And: ast.Or, ast.Or: ast.And}


@dataclass
class Mutant:
    operator: str
    line: int
    detail: str


class _Mutator(ast.NodeTransformer):
    """Applies exactly one mutation, identified by index, and records what it did."""

    def __init__(self, target: int) -> None:
        self.target = target
        self.seen = 0
        self.applied: Mutant | None = None

    def _hit(self, operator: str, node: ast.AST, detail: str) -> bool:
        fired = self.seen == self.target
        if fired:
            self.applied = Mutant(operator, getattr(node, "lineno", 0), detail)
        self.seen += 1
        return fired

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            flip = _CMP_FLIP.get(type(op))
            if flip and self._hit("comparison-flip", node, f"{type(op).__name__} -> {flip.__name__}"):
                node.ops[i] = flip()
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        swap = _BIN_SWAP.get(type(node.op))
        if swap and self._hit("arithmetic-swap", node, f"{type(node.op).__name__} -> {swap.__name__}"):
            node.op = swap()
        return node

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        self.generic_visit(node)
        flip = _BOOL_FLIP.get(type(node.op))
        if flip and self._hit("boolean-flip", node, f"{type(node.op).__name__} -> {flip.__name__}"):
            node.op = flip()
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.op, ast.Not) and self._hit("negation-drop", node, "drop `not`"):
            return node.operand
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, bool):
            if self._hit("constant-flip", node, f"{node.value} -> {not node.value}"):
                return ast.copy_location(ast.Constant(value=not node.value), node)
        elif isinstance(node.value, int):
            if self._hit("boundary-shift", node, f"{node.value} -> {node.value + 1}"):
                return ast.copy_location(ast.Constant(value=node.value + 1), node)
        return node


# Only the module's own function definitions are mutated. `register_into` is registration
# METADATA, not the check under test: the published vectors call the function and cannot see a
# flipped `returns_tristate`, so every mutation there survives and drags the score down for a
# reason that has nothing to do with how well the function is tested.
_NOT_UNDER_TEST = frozenset({"register_into", "bind_registry"})


def _mutable_tree(source: str) -> ast.Module:
    tree = ast.parse(source)
    tree.body = [
        n for n in tree.body
        if not (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in _NOT_UNDER_TEST)
    ]
    return tree


def _count_sites(source: str) -> int:
    m = _Mutator(-1)
    m.visit(_mutable_tree(source))
    return m.seen


def _mutate(source: str, index: int) -> tuple[str, Mutant | None]:
    m = _Mutator(index)
    tree = m.visit(_mutable_tree(source))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree), m.applied


def _run_vectors(name: str, fn: Any, registry: Any) -> list[Any]:
    """Every vector's observed outcome, as a comparable token. An exception is an outcome."""
    from cdfc.predicates.host_fns import load_vectors

    out: list[Any] = []
    for v in load_vectors(name):
        if "snapshot" in v and registry is not None:
            if v["snapshot"] is None:
                registry._snapshot_sha256 = None
                registry._records = {}
            else:
                registry.bind_snapshot("vectors", v["snapshot"])
        try:
            got = fn(*v["args"])
            out.append(("value", str(got), type(got).__name__))
        except Exception as e:  # noqa: BLE001 — the exception type IS the observation
            out.append(("raised", type(e).__name__))
    return out


def score(name: str) -> dict[str, Any]:
    mod_name, attr = MODULES[name]
    module = importlib.import_module(mod_name)
    source = Path(module.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]

    from cdfc.predicates.host_fns import HostFnRegistry

    registry = HostFnRegistry() if name == "reg_resolves" else None
    if registry is not None:
        module.bind_registry(registry)

    baseline = _run_vectors(name, getattr(module, attr), registry)
    total = _count_sites(source)
    killed, survived = 0, []

    for i in range(total):
        mutated_src, applied = _mutate(source, i)
        if applied is None:
            continue
        ns: dict[str, Any] = {"__name__": f"{mod_name}__mutant{i}", "__file__": module.__file__}
        try:
            exec(compile(mutated_src, f"<mutant {name} {i}>", "exec"), ns)  # noqa: S102
        except Exception:  # noqa: BLE001 — a mutant that will not even import is killed
            killed += 1
            continue
        if registry is not None and "bind_registry" in ns:
            ns["bind_registry"](registry)
        mutant_fn = ns.get(attr)
        if mutant_fn is None:
            killed += 1
            continue
        try:
            observed = _run_vectors(name, mutant_fn, registry)
        except Exception:  # noqa: BLE001
            killed += 1
            continue
        if observed != baseline:
            killed += 1
        else:
            survived.append({"index": i, "operator": applied.operator,
                             "line": applied.line, "detail": applied.detail})
        if registry is not None:
            module.bind_registry(registry)

    declared = _declared_equivalent(name, survived)
    unexplained = [s for s in survived if s not in declared]
    return {
        "host_fn": name,
        "mutants_generated": total,
        "killed": killed,
        "survived": len(survived),
        "declared_equivalent": len(declared),
        "unexplained_survivors": len(unexplained),
        # TWO denominators, always both. The second may only move because a row was argued in
        # docs/EQUIVALENT-MUTANTS.md; a tool that silently excluded survivors would raise every
        # score by exactly the amount nobody was allowed to see.
        "score": f"{killed}/{total}",
        "score_excluding_declared_equivalent": f"{killed}/{total - len(declared)}",
        "survivors": survived,
        "note": (
            "Mutants are generated from this host function's own AST and killed by its PUBLISHED "
            "vectors. Survivors are listed by line and operator rather than absorbed into the "
            "denominator: a survivor is either a hole in the vectors or a genuinely equivalent "
            "program, and only reading it tells you which. This is a LOCAL score over the "
            "function, not P6's campaign over the workbooks."
        ),
    }


# Declared equivalent in docs/EQUIVALENT-MUTANTS.md, by (host function, operator, detail). The
# argument lives in that file; this is only the machine-readable pointer to it, so a score cannot
# be raised by editing a tool.
DECLARED_EQUIVALENT: dict[str, set[tuple[str, str]]] = {
    "template_current": {("boundary-shift", "1 -> 2")},   # EQ-001: lru_cache(maxsize=)
}


def _declared_equivalent(name: str, survivors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = DECLARED_EQUIVALENT.get(name, set())
    return [s for s in survivors if (s["operator"], s["detail"]) in allowed]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    worst = 1.0
    for name in HOST_FNS:
        result = score(name)
        (OUT_DIR / f"{name}.mutation.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        k, t = result["killed"], result["mutants_generated"]
        eq, unexp = result["declared_equivalent"], result["unexplained_survivors"]
        denom = t - eq
        worst = min(worst, k / denom if denom else 1.0)
        note = f"   equivalent: {eq}" if eq else ""
        note += f"   UNEXPLAINED: {unexp}" if unexp else ""
        print(f"{name:18s} {k:3d}/{t:<3d} killed  ({k}/{denom} excl. declared equivalent){note}")
    print(f"weakest host function: {worst:.2f} (excluding mutants declared equivalent in "
          f"docs/EQUIVALENT-MUTANTS.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
