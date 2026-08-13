"""AST import-closure walker.

**MOVED TO `src/` AT P8, dated 13 Aug 2026.** It lived under `tests/negative/` while only tests
read it. P8-B3's `g4_ffr.independent()` computes it AT RUNTIME — the corpus generator's import
closure against the predicate evaluator's is one of the two conjuncts that decides whether an FFR
is informative at all — and a runtime module importing from `tests/` is a product that does not
ship. `tests/negative/importgraph.py` re-exports from here, so every existing import still
resolves and there is still exactly one implementation.

PUBLIC, because three later phases and two gates read it: denominator provenance
(NC-D02a/c), the round-trip control (NC-P04), registry row 14 (no model client reachable
from the verdict path), and from P8 the corpus-independence property that G4's FFR rests
on. **It is one function, so there is no second implementation to forget.**

It walks the AST and never imports the module. Importing to discover imports runs module
level code, which for a verdict-path module could be the very thing under test — and a
side effect during a purity check is a measurement of the instrument.
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]


def _module_path(module: str) -> Path | None:
    rel = module.replace(".", "/")
    for cand in (SRC / f"{rel}.py", SRC / rel / "__init__.py"):
        if cand.is_file():
            return cand
    return None


def _direct_imports(module: str, root: str) -> set[str]:
    path = _module_path(module)
    if path is None:
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == root or a.name.startswith(root + "."):
                    out.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import
                base = module.rsplit(".", 1)[0] if "." in module else module
                mod = f"{base}.{node.module}" if node.module else base
            else:
                mod = node.module or ""
            if mod == root or mod.startswith(root + "."):
                out.add(mod)
                for a in node.names:
                    if _module_path(f"{mod}.{a.name}") is not None:
                        out.add(f"{mod}.{a.name}")
    return out


@lru_cache(maxsize=None)
def import_closure(module: str, *, root: str = "cdfc") -> frozenset[str]:
    """The transitive first-party import set of `module`, by AST, without importing it."""
    seen: set[str] = set()
    stack = [module]
    while stack:
        cur = stack.pop()
        for dep in _direct_imports(cur, root):
            if dep not in seen:
                seen.add(dep)
                stack.append(dep)
    return frozenset(seen)


def reaches(module: str, target: str, *, root: str = "cdfc") -> bool:
    return target in import_closure(module, root=root)
